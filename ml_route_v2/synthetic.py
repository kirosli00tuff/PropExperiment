"""The synthetic world of ML route v2: bars, engine frames, releases, D8 costs, roll blackouts and
planted edges for the pipeline, the leakage canaries and the runtime probe. No market data is read.

docs/STAGE_E_ML_V2_DESIGN.md V2.9 (leakage controls, the planted canaries, Gate 0's canary
semantics from V2.2b) and V2.11 (the runtime probe); contract reports/stage_e11_interfaces.md
section 8 (Task 5).

- Bars (``SyntheticWorld.bars``, the signal library's input): one-minute random-walk bars on every
  open interval of each root's real group calendar (data.group_session.session_intervals, as
  ml_route_v2/signals/synthetic_bars.session_bars), on the root's vendor tick grid, for the price
  path of every vehicle, every cluster lead (G17), MES (signal only) and every leg a member signal
  of the vehicles' clusters reads (``legs_by_vehicle``). The per-minute step sd is set in vehicle
  ticks from the vehicle's nominal D8 round trip (``nominal_cost_ticks``) so that the 60-minute sd
  is ``sigma_cost_multiple`` round trips (default 20: c/sigma = 0.05, admissible under V2.2's
  tau, constants.C_SIGMA_TAU); ``vol_ticks`` overrides it per root.
- Bars start ``warmup_dates`` trade dates before ``first`` (history for sigma_X,d, G9's 120-date
  median and the 60-date z-score warm-up, V2.4). ``calendar`` is the training calendar: the union
  of the vehicles' group trade dates in [first, last] (V2.9 "cut from calendars alone"); the
  pipeline keeps panel rows on it.
- Engine frames (``SyntheticWorld.engine_frames``, by vehicle root): the vehicle's price-path bars
  from O_X - 150 min to F_X + 2 min of each trade date with the engine's BAR_COLUMNS flags
  (ml_route.synthetic.synthetic_bars' layout). Built eagerly (``frames``) for a small world or a
  shifted one, else on demand from the bars, cut to the requested dates (the probe's memory).
  The vehicle and its price path quote the same underlying in the same units (interfaces
  section 1), so engine fills see the planted edges.
- Releases: ml_route_v2.signals.synthetic_bars.synthetic_releases (a ReleaseCalendar for the
  signals, the targets and the engine). Costs: the frozen D8 leg inputs (targets.frozen_costs).
  Roll blackouts: a synthetic splice on the first trade date on or after the 10th of March, June,
  September and December, plus the one trade date before it (data.group_session.roll_blackout).

Plants (``plant``: one mapping or a sequence of them, each with a "kind"):
- {"kind": "sign", "edge_ticks" or "edge_cost_multiple", "feature_minutes": 60,
  "horizon_minutes": 60, "vehicles": (...)}: at every decision time t of the vehicle, with x the
  vehicle's trailing ``feature_minutes`` return read from bars closed by t (close of the bar opening
  at t - 1 min minus close of the bar opening at t - 1 - feature_minutes; g02_ret60 for 60), the
  path drifts by edge x sign(x) vehicle ticks, linearly over the bars closing in (t, t + horizon]
  and as a level thereafter. So E[open(t + h) - open(t) | x] = edge x sign(x) for h >= horizon
  (a binary edge E[r | x] = beta x sign(x)); x = 0 or a missing bar plants nothing.
- {"kind": "noise"}: nothing planted (the default world is pure noise).
- {"kind": "shift", "roots": (...), "minutes": -1}: the roots' bar timestamps move by ``minutes``
  (-1: each bar is labelled one minute before it opened, so the bar a feature reads as "closed by
  t" really closes at t + 1 min). Engine frames are not shifted.
- {"kind": "leak", "roots": (...), "minutes": 60}: adds a column ``leak_fwd`` to the roots' bars:
  the close ``minutes`` later minus the bar's close (NaN when absent), a future-leaking column.
"""

from __future__ import annotations

import zlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta
from types import MappingProxyType
from typing import Any

import numpy as np
import pandas as pd

from ml_route_v2.clock import decision_rows, session_group
from ml_route_v2.constants import (
    CLUSTER_LEADS,
    DECISION_TIMES_CT,
    SIGNAL_ONLY_ROOTS,
    UNIVERSE,
)

NS_MIN = 60_000_000_000
WARMUP_DATES = 210  # sigma_X,d 20 + G9 median 120 + z warm-up 60 (V2.4) + margin
SIGMA_COST_MULTIPLE = 20.0  # default 60-minute sd in round trips (c/sigma 0.05 < tau C_SIGMA_TAU)
SIGNAL_ONLY_VOL_TICKS = 4.0  # per-minute sd of a signal-only root (MES), its own ticks
START_TICKS = 100_000  # starting price in vendor ticks
FLOOR_TICKS = 10_000  # reflecting floor of the random walk, vendor ticks
PRE_OPEN_MINUTES = 150  # engine frames start at O_X - 150 min (ml_route.synthetic)
POST_FLATTEN_MINUTES = 3  # engine frames end at F_X + 2 min
ROLL_MONTHS = (3, 6, 9, 12)
ROLL_DAY = 10
ROLL_SESSIONS_BEFORE = 1
PLANT_KINDS = ("sign", "noise", "shift", "leak")
_PATH_TO_VEHICLE = {path: v for v, (_c, path) in UNIVERSE.items()}


class SyntheticError(ValueError):
    """A synthetic-world request is unusable (unknown root, bad plant)."""


@dataclass(frozen=True)
class SyntheticWorld:
    vehicles: tuple[str, ...]  # traded vehicle roots (decision rows)
    first: date  # training calendar bounds: panel rows are kept on [first, last]
    last: date
    bars_first: date  # first bar trade date (warm-up history before ``first``)
    calendar: tuple[date, ...]  # union of the vehicles' group trade dates in [first, last]
    bars: Mapping[str, pd.DataFrame]  # by price-path root (+ MES, + legs): the signal input
    frames: Mapping[str, pd.DataFrame]  # by vehicle root (eager; empty: built on demand)
    releases: Any  # screening.stage_e_rules.ReleaseCalendar
    costs: Mapping[str, Any]  # vehicle -> frozen D8 LegInputs
    blackout: Mapping[str, frozenset[date]]  # bar root -> synthetic roll blackout dates
    legs: Mapping[str, tuple[str, ...]]  # vehicle -> bar roots its features read
    vol_ticks: Mapping[str, float]  # bar root -> per-minute step sd (vehicle ticks of its path)
    seed: int
    plant: tuple[Mapping[str, Any], ...] = field(default_factory=tuple)

    def exclude(self) -> dict[str, frozenset[date]]:
        """D4's union per vehicle (clock.exclude_union): its legs' roll blackouts. D4's rule, kept
        for the frozen K8 members as trials; the v2 pipeline excludes only each product's own
        dates (pipeline.own_blackout) and passes ``blackout`` to the signals (V2.2)."""
        from ml_route_v2.clock import exclude_union

        return exclude_union(self.blackout, self.legs)

    def engine_frames(self, vehicles: Sequence[str] | None = None,
                      dates: Sequence[date] | None = None) -> dict[str, pd.DataFrame]:
        """Engine frames of ``vehicles`` (default all) on ``dates`` (default all)."""
        out = {}
        keep = None if dates is None else {d.isoformat() for d in dates}
        for v in (self.vehicles if vehicles is None else vehicles):
            frame = self.frames[v] if v in self.frames else engine_frame(
                v, self.bars[UNIVERSE[v][1]], keep)
            if keep is not None and v in self.frames:
                frame = frame.loc[frame["trade_date"].astype(str).isin(keep)]
            out[v] = frame.reset_index(drop=True)
        return out

    def engine_blackout(self) -> frozenset[date]:
        """The union of every traded leg's roll blackout (StageERules.blackout, D4)."""
        out: set[date] = set()
        for v in self.vehicles:
            out |= set(self.blackout.get(UNIVERSE[v][1], frozenset()))
        return frozenset(out)


# ------------------------------------------------------------------ roots and costs ----
def legs_by_vehicle(vehicles: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Bar roots a vehicle's features read: its path, the G17 leads, MES, and the legs of the
    member signals of its cluster and of K8 (signals REGISTRY roots_read; pooled ports read the
    row's own path only)."""
    from ml_route_v2.signals import REGISTRY

    n_paths = len(UNIVERSE)
    out = {}
    for v in vehicles:
        if v not in UNIVERSE:
            raise SyntheticError(f"{v} is not a vehicle of constants.UNIVERSE")
        cluster, path = UNIVERSE[v]
        roots = {path, *CLUSTER_LEADS.values(), *SIGNAL_ONLY_ROOTS}
        for spec in REGISTRY.values():
            if spec.kind == "member" and len(spec.roots_read) < n_paths and \
                    spec.cluster in (cluster, "K8"):
                roots |= set(spec.roots_read)
        out[v] = tuple(sorted(roots))
    return out


def nominal_cost_ticks(vehicle: str) -> float:
    """Mean over the vehicle's three decision times of max(long, short) D8 round trip at h60,
    outside event windows, in vehicle ticks (commission / tick value + entry and exit sides)."""
    from datetime import datetime
    from zoneinfo import ZoneInfo

    from ml_route_v2.targets import frozen_costs

    leg = frozen_costs((vehicle,))[vehicle]
    pc = leg.costs
    comm = float(pc.commission_rt_cents) / float(leg.tick_value_cents)
    ct = ZoneInfo("America/Chicago")
    vals = []
    for at in DECISION_TIMES_CT[session_group(vehicle)]:
        entry = datetime(2021, 1, 4, at.hour, at.minute, tzinfo=ct)
        exit_ = entry + timedelta(minutes=60)
        long_ = (pc.side_slippage_ticks(entry, "buy", False)
                 + pc.side_slippage_ticks(exit_, "sell", False))
        short = (pc.side_slippage_ticks(entry, "sell", False)
                 + pc.side_slippage_ticks(exit_, "buy", False))
        vals.append(comm + max(long_, short))
    return float(np.mean(vals))


def _ticks_per_unit(root: str) -> float:
    """Vehicle ticks per vendor unit for a vehicle's path; own ticks for any other root."""
    from ml_route_v2.signals._core import own_per_unit, per_unit

    vehicle = _PATH_TO_VEHICLE.get(root)
    return per_unit(vehicle) if vehicle is not None else own_per_unit(root)


def default_vol_ticks(root: str, sigma_cost_multiple: float = SIGMA_COST_MULTIPLE) -> float:
    """Per-minute step sd (vehicle ticks) giving a 60-minute sd of sigma_cost_multiple x c."""
    vehicle = _PATH_TO_VEHICLE.get(root)
    if vehicle is None:
        return SIGNAL_ONLY_VOL_TICKS
    return sigma_cost_multiple * nominal_cost_ticks(vehicle) / np.sqrt(60.0)


# ------------------------------------------------------------------ calendars ----
def _group_dates(root: str, first: date, last: date) -> list[date]:
    from data.group_session import group_of, trade_dates_between
    from ml_route.inputs import _group_calendar

    return trade_dates_between(_group_calendar(group_of(root)), first, last)


def _back_dates(roots: Sequence[str], first: date, n: int) -> date:
    """The date ``n`` union trade dates before ``first`` (``first`` itself when n = 0)."""
    if n <= 0:
        return first
    lo = first - timedelta(days=int(n * 1.6) + 20)
    days = sorted({d for r in roots for d in _group_dates(r, lo, first - timedelta(days=1))})
    if len(days) < n:
        raise SyntheticError(f"no {n} trade dates before {first}")
    return days[-n]


def training_calendar(vehicles: Sequence[str], first: date, last: date) -> tuple[date, ...]:
    return tuple(sorted({d for v in vehicles for d in _group_dates(v, first, last)}))


def synthetic_blackout(root: str, first: date, last: date) -> frozenset[date]:
    from data.group_session import group_of, roll_blackout
    from ml_route.inputs import _group_calendar

    cal = _group_calendar(group_of(root))
    days = _group_dates(root, first, last)
    splices = []
    for year in range(first.year, last.year + 1):
        for month in ROLL_MONTHS:
            nxt = [d for d in days if d >= date(year, month, ROLL_DAY)][:1]
            if nxt and nxt[0].month == month:
                splices.append(nxt[0])
    return frozenset(d for d in roll_blackout(cal, splices, ROLL_SESSIONS_BEFORE)
                     if first <= d <= last)


# ------------------------------------------------------------------ bars ----
def _seed_of(seed: int, root: str) -> np.random.Generator:
    return np.random.default_rng([int(seed), zlib.crc32(root.encode("utf-8"))])


def _session_grid(root: str, first: date, last: date) -> tuple[np.ndarray, np.ndarray, list[date]]:
    from data.group_session import group_of, session_intervals
    from ml_route.inputs import _group_calendar

    cal = _group_calendar(group_of(root))
    days = _group_dates(root, first, last)
    ts_parts, code_parts = [], []
    for code, day in enumerate(days):
        for lo, hi in session_intervals(cal, day):
            start = -(-lo // NS_MIN) * NS_MIN
            ts = np.arange(start, hi, NS_MIN, dtype=np.int64)
            if len(ts):
                ts_parts.append(ts)
                code_parts.append(np.full(len(ts), code, dtype=np.int32))
    if not ts_parts:
        raise SyntheticError(f"{root}: no session minutes in {first}..{last}")
    return np.concatenate(ts_parts), np.concatenate(code_parts), days


def _closes(n: int, vol_units: float, tick: float, rng: np.random.Generator) -> np.ndarray:
    steps = np.rint(rng.normal(0.0, vol_units / tick, size=n))
    path = START_TICKS + np.cumsum(steps)
    path = np.abs(path - FLOOR_TICKS) + FLOOR_TICKS
    return path * tick


def _plants(plant: Mapping | Sequence[Mapping] | None) -> tuple[Mapping[str, Any], ...]:
    if plant is None:
        return ()
    items = (plant,) if isinstance(plant, Mapping) else tuple(plant)
    for p in items:
        if p.get("kind") not in PLANT_KINDS:
            raise SyntheticError(f"plant kind {p.get('kind')!r} not in {PLANT_KINDS}")
    return tuple(MappingProxyType(dict(p)) for p in items)


def _edge_ticks(p: Mapping[str, Any], vehicle: str) -> float:
    if "edge_ticks" in p:
        return float(p["edge_ticks"])
    if "edge_cost_multiple" in p:
        return float(p["edge_cost_multiple"]) * nominal_cost_ticks(vehicle)
    raise SyntheticError("a sign plant needs edge_ticks or edge_cost_multiple")


def _decision_ts(vehicle: str, days: Sequence[date]) -> np.ndarray:
    rows = decision_rows((vehicle,), {vehicle: days})
    return rows["decision_ts_ns"].to_numpy(np.int64)


def _sign_shift(ts: np.ndarray, closes: np.ndarray, t_dec: np.ndarray, edge_units: float,
                feature_min: int, horizon_min: int) -> np.ndarray:
    """The planted level path S at every bar's close (module docstring, kind "sign")."""
    width = horizon_min * NS_MIN
    t_arr = np.zeros(len(t_dec), dtype=np.int64)
    a_cum = np.zeros(len(t_dec) + 1)
    n = 0

    def shift_at(close_ns: int) -> float:
        k_full = int(np.searchsorted(t_arr[:n] + width, close_ns, side="right"))
        k_on = int(np.searchsorted(t_arr[:n], close_ns, side="left"))
        part = (close_ns - t_arr[k_full:k_on]) / width
        return float(a_cum[k_full] + np.dot(part, np.diff(a_cum[k_full:k_on + 1])))

    for t in np.sort(t_dec):
        i1 = np.searchsorted(ts, t - NS_MIN)
        i0 = np.searchsorted(ts, t - NS_MIN - feature_min * NS_MIN)
        if i1 >= len(ts) or i0 >= len(ts) or ts[i1] != t - NS_MIN or \
                ts[i0] != t - NS_MIN - feature_min * NS_MIN:
            continue
        x = (closes[i1] + shift_at(int(ts[i1]) + NS_MIN)) - \
            (closes[i0] + shift_at(int(ts[i0]) + NS_MIN))
        if x != 0:
            t_arr[n] = int(t)
            a_cum[n + 1] = a_cum[n] + edge_units * float(np.sign(x))
            n += 1
    t_j = t_arr[:n].tolist()
    a_j = np.diff(a_cum[:n + 1]).tolist()
    out = np.zeros(len(ts))
    close_ns = ts + NS_MIN
    tail = np.zeros(len(ts) + 1)
    for t, a in zip(t_j, a_j, strict=True):
        lo = np.searchsorted(close_ns, t, side="right")
        hi = np.searchsorted(close_ns, t + width, side="left")
        out[lo:hi] += a * (close_ns[lo:hi] - t) / width
        tail[hi] += a
    return out + np.cumsum(tail)[:-1]


def leak_column(ts: np.ndarray, closes: np.ndarray, minutes: int) -> np.ndarray:
    j = np.searchsorted(ts, ts + minutes * NS_MIN)
    ok = j < len(ts)
    ok[ok] = ts[j[ok]] == ts[ok] + minutes * NS_MIN
    out = np.full(len(ts), np.nan)
    out[ok] = closes[j[ok]] - closes[ok]
    return out


def _root_bars(root: str, bars_first: date, last: date, *, seed: int, vol_ticks: float,
               plants: Sequence[Mapping[str, Any]], vehicles: Sequence[str],
               compact: bool) -> pd.DataFrame:
    from rules.products import product

    rng = _seed_of(seed, root)
    ts, code, days = _session_grid(root, bars_first, last)
    tick = float(product(root).vendor_tick)
    closes = _closes(len(ts), vol_ticks / _ticks_per_unit(root), tick, rng)
    vehicle = _PATH_TO_VEHICLE.get(root)
    extra: dict[str, np.ndarray] = {}
    for p in plants:
        if p["kind"] == "sign" and vehicle in vehicles and \
                vehicle in tuple(p.get("vehicles", vehicles)):
            edge_units = _edge_ticks(p, vehicle) / _ticks_per_unit(root)
            shift = _sign_shift(ts, closes, _decision_ts(vehicle, days), edge_units,
                                int(p.get("feature_minutes", 60)),
                                int(p.get("horizon_minutes", 60)))
            closes = np.rint((closes + shift) / tick) * tick
        if p["kind"] == "leak" and root in tuple(p.get("roots", ())):
            extra["leak_fwd"] = leak_column(ts, closes, int(p.get("minutes", 60)))
    opens = np.concatenate([[START_TICKS * tick], closes[:-1]])
    wig = rng.integers(0, 3, size=len(ts)) * tick
    iso = np.array([d.isoformat() for d in days], dtype=object)
    trade = pd.Categorical.from_codes(code, categories=iso) if compact else iso[code]
    for p in plants:
        if p["kind"] == "shift" and root in tuple(p.get("roots", ())):
            ts = ts + int(p.get("minutes", -1)) * NS_MIN
    frame = pd.DataFrame({
        "ts_event": ts, "open": opens, "high": np.maximum(opens, closes) + wig,
        "low": np.minimum(opens, closes) - wig, "close": closes,
        "volume": rng.integers(1, 400, size=len(ts)).astype(np.uint32),
        "instrument_id": np.ones(len(ts), dtype=np.uint32), "trade_date": trade})
    for k, v in extra.items():
        frame[k] = v
    return frame


def engine_frame(vehicle: str, path_bars: pd.DataFrame,
                 dates: set[str] | None = None) -> pd.DataFrame:
    """The vehicle's engine frame from its price-path bars (module docstring), optionally on the
    ISO trade dates ``dates`` only."""
    from data.group_session import group_of
    from ml_route.inputs import day_times

    group = group_of(vehicle)
    ts = path_bars["ts_event"].to_numpy(np.int64)
    isos, code = np.unique(path_bars["trade_date"].astype(str).to_numpy(), return_inverse=True)
    lo = np.full(len(isos), np.iinfo(np.int64).max)
    hi = np.full(len(isos), np.iinfo(np.int64).min)
    fl = np.full(len(isos), np.iinfo(np.int64).max)
    for k, iso in enumerate(isos):
        if dates is not None and iso not in dates:
            continue
        dt = day_times(vehicle, group, date.fromisoformat(iso))
        if dt is not None:
            lo[k] = dt.open_ns - PRE_OPEN_MINUTES * NS_MIN
            hi[k] = dt.flatten_ns + POST_FLATTEN_MINUTES * NS_MIN
            fl[k] = dt.flatten_ns
    keep = (ts >= lo[code]) & (ts < hi[code])
    flat = keep & (ts >= fl[code])
    trade = isos[code]
    sub = path_bars.loc[keep]
    n = len(sub)
    return pd.DataFrame({
        "ts_event": sub["ts_event"].to_numpy(np.int64),
        "open": sub["open"].to_numpy(np.float64), "high": sub["high"].to_numpy(np.float64),
        "low": sub["low"].to_numpy(np.float64), "close": sub["close"].to_numpy(np.float64),
        "volume": sub["volume"].to_numpy().astype(np.uint64),
        "instrument_id": np.ones(n, dtype=np.uint32), "raw_symbol": vehicle + "Z9",
        "trade_date": trade[keep], "in_flatten_window": flat[keep],
        "in_no_new_positions_window": flat[keep], "early_halt_ct": "",
        "in_scheduled_closure": False, "is_roll_session": False, "gap_before_minutes": 0,
        "vendor_degraded_day": False})


# ------------------------------------------------------------------ the world ----
def synthetic_universe(roots: Sequence[str], first: date, last: date, *, seed: int,
                       plant: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
                       warmup_dates: int = WARMUP_DATES,
                       vol_ticks: Mapping[str, float] | None = None,
                       sigma_cost_multiple: float = SIGMA_COST_MULTIPLE,
                       compact: bool = False, eager_frames: bool = True) -> SyntheticWorld:
    """Bars by price-path root (plus MES and legs), engine frames by vehicle, releases, the frozen
    D8 costs, roll blackouts and plants (module docstring). ``roots`` are vehicle roots;
    ``eager_frames`` False leaves the engine frames to ``SyntheticWorld.engine_frames`` (a shift
    plant always builds them eagerly from the unshifted series)."""
    from ml_route_v2.signals.synthetic_bars import synthetic_releases
    from ml_route_v2.targets import frozen_costs

    vehicles = tuple(dict.fromkeys(roots))
    if not vehicles:
        raise SyntheticError("no vehicles")
    if first > last:
        raise SyntheticError(f"first {first} after last {last}")
    plants = _plants(plant)
    legs = legs_by_vehicle(vehicles)
    bar_roots = tuple(sorted({r for v in vehicles for r in legs[v]}))
    bars_first = _back_dates(bar_roots, first, warmup_dates)
    vol = {r: float((vol_ticks or {}).get(r, default_vol_ticks(r, sigma_cost_multiple)))
           for r in bar_roots}
    bars = {r: _root_bars(r, bars_first, last, seed=seed, vol_ticks=vol[r], plants=plants,
                          vehicles=vehicles, compact=compact) for r in bar_roots}
    unshifted = {r: bars[r] for r in bar_roots}
    shifted = any(p["kind"] == "shift" for p in plants)
    for p in plants:  # engine frames are not shifted: rebuild the unshifted series
        if p["kind"] == "shift":
            for r in p.get("roots", ()):
                if r in bars:
                    unshifted[r] = _root_bars(r, bars_first, last, seed=seed, vol_ticks=vol[r],
                                              plants=[q for q in plants if q["kind"] != "shift"],
                                              vehicles=vehicles, compact=compact)
    frames = ({v: engine_frame(v, unshifted[UNIVERSE[v][1]]) for v in vehicles}
              if eager_frames or shifted else {})
    releases = synthetic_releases(bars_first, last, seed)
    blackout = {r: synthetic_blackout(r, bars_first, last) for r in bar_roots}
    return SyntheticWorld(
        vehicles=vehicles, first=first, last=last, bars_first=bars_first,
        calendar=training_calendar(vehicles, first, last),
        bars=MappingProxyType(bars), frames=MappingProxyType(frames), releases=releases,
        costs=MappingProxyType(frozen_costs(vehicles)),
        blackout=MappingProxyType(blackout), legs=MappingProxyType(legs),
        vol_ticks=MappingProxyType(vol), seed=int(seed), plant=plants)


__all__ = [
    "PLANT_KINDS", "SIGMA_COST_MULTIPLE", "WARMUP_DATES", "SyntheticError", "SyntheticWorld",
    "default_vol_ticks", "engine_frame", "leak_column", "legs_by_vehicle", "nominal_cost_ticks",
    "synthetic_blackout", "synthetic_universe", "training_calendar",
]
