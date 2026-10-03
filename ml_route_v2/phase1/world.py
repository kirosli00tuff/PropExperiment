"""Phase 1 of ML route v2 on real data: the world (Stage E.12 Task 1b).

docs/STAGE_E_ML_V2_DESIGN.md V2.1 (phase 1), V2.2 (decision clock, excluded dates), V2.9 (training
calendar) and "The phase-1 test list"; Stage E.12 lead rules P-1 and P-3 (cited "E.12 lead rule
P-n"). ``Phase1World`` carries the fields of ml_route_v2.synthetic.SyntheticWorld that
pipeline.build_world_panel and the Gate 0 stage read (vehicles, first, last, bars_first, calendar,
bars, frames, releases, costs, blackout, legs). No engine runs in this stage: ``frames`` is empty.

Sources, all frozen:
- Vehicles (freeze review F-3): never a free input. ``phase1_subset`` starts from the "subset" list
  of the lead's ranking, reports/stage_e12_ranking.json ({"subset": [{"vehicle", "path",
  "account", "quote_usd"}], ...}; Task 5), and keeps each vehicle whose price-path step 2 store
  (data.step2_store.step2_parquet_path) and summary reports/step2/bars_<PATH>.json exist (NG's
  owned store counts); a subset vehicle without them is dropped by name, "no step 2 store
  (purchase incomplete or failed)". A missing or malformed ranking file refuses. The file's sha256
  is recorded in the bars report and the input fingerprint (build.py).
- Roots (P-1): the price path of every vehicle (constants.UNIVERSE[v][1]) plus MES. The owned
  micro step 2 stores MCL, MGC and MHG are not price paths and are never read. A signal
  (signals.REGISTRY) is covered iff ``spec.own_path_only`` or every root of ``spec.roots_read`` is
  available (``signal_coverage``); an uncovered signal is left out of the panel and listed by name
  with its missing roots.
- MES contingency (E.12 lead rule P-1a): when loading MES's frozen confirmation store raises a
  data.stage_e_bars.StageEBarRefusal (any subclass), or D.1f's record check fails
  (StartDatesRefusal), MES is UNAVAILABLE: every signal reading MES is a coverage exclusion with
  the reason "MES store refused: <exception class>: <message>" (``Coverage.reasons``), and the
  world records mes_status "refused" and the text. A price-path root's refusal still stops.
- S_X (P-3): D4's frozen start rule per price path, screening.stage_e_start_dates.
  product_start_rule (it reads ts_event, volume and trade_date of the root's research store, whose
  sha256 must equal E.2a's record in screening.stage_e_frozen, and of its step 2 store; never a
  price). The set-file machinery takes whole sets only (a cluster, or "ML" = all 31 price-path
  contracts), so the per-root function is called and nothing is written to
  reports/stage_e_start_rule_*.json. MES: D4's fixed 2020-02-03 from D.1f's pinned record
  (stage_e_start_dates.mes_from_d1f), whose confirmation-parquet sha256 pins MES's store. A root
  whose window is empty (no qualifying month) is dropped by name, and so is its vehicle.
- Bars (P-3): data.stage_e_bars.load_confirmation_leg per price path (the step 2 store, its sha256
  the one the start rule read, review F-3), cut to trade dates [S_X, 2024-02-29]; it books every row
  to its CME trade date by the group calendar (L-3), refuses holdout, embargo and out-of-store rows
  and gives the roll blackout (L-8). MES: its frozen confirmation parquet
  (data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet) through the same
  loader's ``read_leg`` with the step 2 store's checks (the step 2 layout has no MES file;
  E.2b review F3-1 left the MES store to the lead), cut at S_X exactly as load_confirmation_leg
  cuts. The loaded frame is compacted to the eight columns the signals and targets read (ts_event,
  OHLC, volume, instrument_id, trade_date as a category), as the synthetic world's compact bars.
- Window guard: any bar dated (trade date) on or after constants.FORBIDDEN_FROM (2024-03-01), or
  opening at or after 00:00 CT of that date, raises Phase1WindowError (``refuse_late``); the panel
  then runs panel.assert_window(train).
- Training calendar (V2.9): every CME trade date from the earliest S_X of the phase-1 price paths to
  2024-02-29 of at least one phase-1 group calendar (synthetic.training_calendar, the same rule;
  MES is a signal-only root and does not set the start).
- Decision rows (V2.2): pipeline.build_world_panel's own call: each vehicle's own roll-blackout
  dates (its price path's; the vehicle's own store is not read, P-1) and the group calendar's
  early-halt and early-close dates (ml_route_v2/clock.py reads the real group calendar through
  ml_route.inputs.day_times and rules.sessions.flatten_time_ct); the CPI window is the engine's.
- Releases: screening.stage_e_rules.load_release_calendar (reports/stage_e2b_release_calendar.json).
- Costs: the frozen D8 leg inputs of the vehicles (targets.frozen_costs), as the synthetic world.
- Vendor-degraded dates (V2.2, NULL_CRITERIA_E 4): reported and kept. Step 2 roots: the store
  summary reports/step2/bars_<ROOT>.json (its parquet sha256 must be the store's); MES: the
  parquet's own metadata (degraded_vendor_days). Beside them, the trade dates whose bars carry the
  store's vendor_degraded_day flag.
"""

from __future__ import annotations

import gc
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, datetime, time
from pathlib import Path
from types import MappingProxyType
from typing import Any
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

from ml_route_v2.constants import FORBIDDEN_FROM, TRAIN_LAST, UNIVERSE

MES = "MES"  # E.12 lead rule P-1: the phase-1 price paths plus MES
EXTRA_ROOTS = (MES,)
CT = ZoneInfo("America/Chicago")
# 00:00 CT of FORBIDDEN_FROM in UTC ns: no CME session of trade date <= 2024-02-29 reaches it
FORBIDDEN_FROM_NS = int(datetime.combine(FORBIDDEN_FROM, time(0, 0), tzinfo=CT).timestamp()
                        ) * 1_000_000_000
COMPACT_COLUMNS = ("ts_event", "open", "high", "low", "close", "volume", "instrument_id",
                   "trade_date")
MES_STORE = "mes_confirmation"
STEP2_STORE = "step2"
_U32_MAX = int(np.iinfo(np.uint32).max)


class Phase1Error(RuntimeError):
    """A phase-1 input is unusable; nothing is built."""


class Phase1WindowError(Phase1Error):
    """A bar or row is dated on or after constants.FORBIDDEN_FROM (2024-03-01)."""


# ------------------------------------------------------------------ P-1 coverage ----
@dataclass(frozen=True)
class Coverage:
    available: tuple[str, ...]  # roots the features may read (P-1)
    covered: tuple[str, ...]  # REGISTRY order
    uncovered: Mapping[str, tuple[str, ...]]  # signal -> its roots outside ``available``
    # E.12 lead rule P-1a: a signal-only root whose frozen store was refused -> the reason
    unavailable: Mapping[str, str] = field(default_factory=dict)

    def reasons(self) -> dict[str, str]:
        """Per uncovered signal: why (an unavailable root's refusal, or roots not in phase 1)."""
        out = {}
        for name, missing in self.uncovered.items():
            refused = [self.unavailable[r] for r in missing if r in self.unavailable]
            other = [r for r in missing if r not in self.unavailable]
            parts = refused + ([f"reads roots outside phase 1: {', '.join(other)}"]
                               if other else [])
            out[name] = "; ".join(parts)
        return out


def price_path(vehicle: str) -> str:
    return UNIVERSE[vehicle][1]


def check_vehicles(vehicles: Sequence[str]) -> tuple[str, ...]:
    vs = tuple(str(v) for v in vehicles)
    if not vs:
        raise Phase1Error("no vehicles")
    dup = sorted({v for v in vs if vs.count(v) > 1})
    if dup:
        raise Phase1Error(f"vehicles listed twice: {dup}")
    unknown = [v for v in vs if v not in UNIVERSE]
    if unknown:
        raise Phase1Error(f"not vehicles of constants.UNIVERSE: {unknown}")
    return vs


def available_roots(vehicles: Sequence[str], unavailable: Sequence[str] = ()
                    ) -> tuple[str, ...]:
    """E.12 lead rule P-1: the vehicles' price paths plus MES (less a signal-only root whose
    store was refused, P-1a)."""
    bad = set(unavailable) - set(EXTRA_ROOTS)
    if bad:
        raise Phase1Error(f"only a signal-only root can be unavailable (P-1a), not {sorted(bad)}")
    roots = {price_path(v) for v in check_vehicles(vehicles)} | set(EXTRA_ROOTS)
    return tuple(sorted(roots - set(unavailable)))


def signal_coverage(vehicles: Sequence[str], registry: Mapping[str, Any] | None = None,
                    unavailable: Mapping[str, str] | None = None) -> Coverage:
    """E.12 lead rule P-1: a signal is covered iff own_path_only or every root it reads is
    available; the uncovered ones with their missing roots. ``unavailable``: signal-only roots
    whose frozen store was refused (P-1a) -> the refusal text."""
    if registry is None:
        from ml_route_v2.signals import REGISTRY as registry  # noqa: N811
    unavailable = dict(unavailable or {})
    avail = available_roots(vehicles, tuple(unavailable))
    have = set(avail)
    covered: list[str] = []
    uncovered: dict[str, tuple[str, ...]] = {}
    for name, spec in registry.items():
        missing = () if spec.own_path_only else tuple(r for r in spec.roots_read if r not in have)
        if missing:
            uncovered[name] = missing
        else:
            covered.append(name)
    return Coverage(avail, tuple(covered), MappingProxyType(uncovered),
                    MappingProxyType(unavailable))


# ------------------------------------------------------------------ F-3 vehicles ----
RANKING_FILE = "stage_e12_ranking.json"  # written by the lead at Task 5
NO_STORE = "no step 2 store (purchase incomplete or failed)"


@dataclass(frozen=True)
class Phase1Subset:
    """The phase-1 vehicles derived from the ranking (freeze review F-3)."""

    vehicles: tuple[str, ...]  # kept, in the ranking's order
    subset: tuple[str, ...]  # every subset vehicle, in the ranking's order
    dropped: Mapping[str, str]  # vehicle -> reason (NO_STORE)
    ranking_path: str
    ranking_sha256: str


def _subset_entries(doc: Any, name: str) -> list[tuple[str, str]]:
    subset = doc.get("subset") if isinstance(doc, dict) else None
    if not isinstance(subset, list) or not subset:
        raise Phase1Error(f"{name}: no \"subset\" list")
    out = []
    for entry in subset:
        if not isinstance(entry, dict) or not {"vehicle", "path"} <= set(entry):
            raise Phase1Error(f"{name}: malformed subset entry {entry!r}"[:200])
        v, path = str(entry["vehicle"]), str(entry["path"])
        if v not in UNIVERSE or UNIVERSE[v][1] != path:
            raise Phase1Error(f"{name}: {v} with path {path} is not a vehicle and its price path "
                              "of constants.UNIVERSE")
        out.append((v, path))
    vs = [v for v, _ in out]
    if len(set(vs)) != len(vs):
        raise Phase1Error(f"{name}: a vehicle is listed twice")
    return out


def phase1_subset(ranking_path: Path, *, step2_root: Path | None = None,
                  summaries_root: Path | None = None) -> Phase1Subset:
    """The phase-1 vehicles (module docstring, F-3)."""
    import hashlib

    from data.config import STEP2_ROOT
    from data.step2_store import STEP2_REPORTS, step2_parquet_path

    path = Path(ranking_path)
    if not path.is_file():
        raise Phase1Error(f"{path} does not exist: the phase-1 vehicles come from the ranking's "
                          "subset (Task 5), never from an operator list")
    raw = path.read_bytes()
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Phase1Error(f"{path.name}: not valid JSON ({exc})") from exc
    entries = _subset_entries(doc, path.name)
    s2, summaries = Path(step2_root or STEP2_ROOT), Path(summaries_root or STEP2_REPORTS)
    dropped = {v: NO_STORE for v, p in entries
               if not (step2_parquet_path(p, s2).is_file()
                       and (summaries / f"bars_{p}.json").is_file())}
    kept = tuple(v for v, _ in entries if v not in dropped)
    if not kept:
        raise Phase1Error(f"{path.name}: no subset vehicle has a step 2 store ({sorted(dropped)})")
    return Phase1Subset(kept, tuple(v for v, _ in entries), MappingProxyType(dropped), str(path),
                        hashlib.sha256(raw).hexdigest())


# ------------------------------------------------------------------ P-3 start dates ----
def _day(value: object) -> date | None:
    return None if value is None else date.fromisoformat(str(value))


@dataclass(frozen=True)
class RootStart:
    """D4's start rule of one root (P-3) and the files it read."""

    root: str
    s_x: date | None  # None: an empty window
    v_ref: float | None
    store: str  # STEP2_STORE | MES_STORE
    store_path: str
    store_sha256: str  # the store S_X came from (review F-3); the bars must hash to it
    research_path: str | None
    research_sha256: str | None
    entry: Mapping[str, Any]  # stage_e_start_dates' JSON entry (medians, M*, source)
    inputs: tuple[tuple[str, str], ...]  # (path, sha256) of every file the rule read


def root_start(root: str, *, step2_root: Path, research_root: Path,
               research_sha256: str | None, tables: Any = None) -> RootStart:
    """E.12 lead rule P-3: D4's start rule of one price path from its research and step 2
    stores (screening.stage_e_start_dates.product_start_rule; volume only, never a price)."""
    from data.build_bars import research_parquet_path
    from data.step2_store import step2_parquet_path
    from screening import stage_e_start_dates as sd

    if root == MES:
        raise Phase1Error("MES's S_X is D4's fixed date (mes_root_start)")
    if research_sha256 is None:
        raise Phase1Error(f"{root}: no recorded research parquet sha256 (E.2a)")
    window = sd.day_session_window(root, tables)
    research = research_parquet_path(root, Path(research_root))
    step2 = step2_parquet_path(root, Path(step2_root))
    got = sd.product_start_rule(root, research_path=research, step2_path=step2,
                                research_sha256=research_sha256, window=window)
    entry = dict(got.entry)
    return RootStart(root, _day(entry["s_x"]), entry["v_ref"], STEP2_STORE, str(step2),
                     str(entry["step2_sha256"]), str(research), research_sha256,
                     MappingProxyType(entry), tuple(got.inputs))


def mes_root_start(mes_path: Path, *, record_root: Path) -> RootStart:
    """E.12 lead rule P-3: MES at D4's fixed 2020-02-03 (D.1f's pinned record; it also pins the
    confirmation parquet's sha256)."""
    from screening.stage_e_start_dates import mes_from_d1f

    got = mes_from_d1f(Path(record_root))
    entry = dict(got.entry)
    return RootStart(MES, _day(entry["s_x"]), entry["v_ref"], MES_STORE, str(mes_path),
                     str(entry["step2_sha256"]), None, None, MappingProxyType(entry),
                     tuple(got.inputs))


def frozen_start_agreement(root: str, start: RootStart, *, repo_root: Path) -> dict[str, Any]:
    """Whether an existing reports/stage_e_start_rule_*.json lists the root, and with the same
    S_X and store sha256 (recorded only; P-3 writes no start-rule file)."""
    from screening.stage_e_start_dates import load_start_entries

    try:
        entry = load_start_entries(Path(repo_root)).get(root)
    except Exception as exc:  # noqa: BLE001 - recorded, never fatal: the per-root rule governs
        return {"listed": None, "error": f"{type(exc).__name__}: {exc}"}
    if entry is None:
        return {"listed": False}
    return {"listed": True, "files": [p for p, _ in entry.sources],
            "s_x": None if entry.s_x is None else entry.s_x.isoformat(),
            "s_x_agrees": entry.s_x == start.s_x,
            "store_sha256_agrees": entry.step2_sha256 == start.store_sha256}


# ------------------------------------------------------------------ bars ----
def refuse_late(root: str, frame: pd.DataFrame) -> None:
    """The window guard: no bar dated on or after FORBIDDEN_FROM (trade date, or the bar's
    open at or after 00:00 CT of that date)."""
    if len(frame) == 0:
        return
    days = frame["trade_date"].astype(str).str.slice(0, 10).to_numpy(dtype=object)
    late_day = days >= FORBIDDEN_FROM.isoformat()
    late_ts = frame["ts_event"].to_numpy(np.int64) >= FORBIDDEN_FROM_NS
    if bool(late_day.any()) or bool(late_ts.any()):
        first = sorted(days[late_day | late_ts])[0]
        raise Phase1WindowError(f"{root}: {int((late_day | late_ts).sum())} bars dated on or after "
                                f"{FORBIDDEN_FROM} (first trade date {first})")


def _narrow(values: np.ndarray) -> np.ndarray:
    """uint32 when every value fits (as the synthetic bars), else int64 unchanged."""
    if values.size and (int(values.min()) < 0 or int(values.max()) > _U32_MAX):
        return values.astype(np.int64)
    return values.astype(np.uint32)


def compact_bars(frame: pd.DataFrame) -> pd.DataFrame:
    """The eight columns the signals and targets read (module docstring)."""
    return pd.DataFrame({
        "ts_event": frame["ts_event"].to_numpy(np.int64),
        "open": frame["open"].to_numpy(np.float64), "high": frame["high"].to_numpy(np.float64),
        "low": frame["low"].to_numpy(np.float64), "close": frame["close"].to_numpy(np.float64),
        "volume": _narrow(frame["volume"].to_numpy()),
        "instrument_id": _narrow(frame["instrument_id"].to_numpy()),
        "trade_date": pd.Categorical(frame["trade_date"].astype(str).to_numpy(dtype=object)),
    })


def _cut_at(leg: Any, start: date) -> Any:
    """load_confirmation_leg's cut: the frame and trade dates from ``start`` (ISO order equals
    date order)."""
    from data.stage_e_bars import LegFrame

    keep = leg.frame["trade_date"].astype(str).to_numpy(dtype=object) >= start.isoformat()
    frame = leg.frame[keep].reset_index(drop=True)
    days = tuple(d for d in leg.trade_dates if d >= start)
    return LegFrame(leg.root, leg.store, leg.path, leg.sha256, frame, days,
                    leg.splice_trade_dates, leg.roll_blackout)


def load_root_leg(start: RootStart, *, step2_root: Path) -> Any:
    """The root's checked LegFrame from S_X (module docstring, P-3)."""
    from data import stage_e_bars as seb

    if start.s_x is None:
        raise Phase1Error(f"{start.root}: empty start window, no bars are read")
    if start.store == MES_STORE:
        if not seb.STEP2_FIRST_TRADE_DATE <= start.s_x <= seb.CONFIRMATION_LAST_TRADE_DATE:
            raise ValueError(f"MES S_X {start.s_x} is outside the step 2 window")
        leg = seb.read_leg(MES, Path(start.store_path), seb.STEP2,
                           expected_sha256=start.store_sha256)
        return _cut_at(leg, start.s_x)
    return seb.load_confirmation_leg(start.root, Path(step2_root), start.s_x,
                                     expected_sha256=start.store_sha256)


def _summary_degraded(start: RootStart, summaries_root: Path) -> dict[str, Any]:
    path = Path(summaries_root) / f"bars_{start.root}.json"
    if not path.is_file():
        raise Phase1Error(f"{start.root}: the store summary {path} does not exist")
    doc = json.loads(path.read_text(encoding="utf-8"))
    sha = (doc.get("parquet") or {}).get("sha256")
    if sha != start.store_sha256:
        raise Phase1Error(f"{start.root}: {path.name} records parquet sha256 {str(sha)[:12]}..., "
                          f"not the store's {start.store_sha256[:12]}...")
    deg = doc["degraded"]
    return {"source": path.name, "vendor_degraded_utc_dates": sorted(deg["degraded_utc_dates"]),
            "on_store_trade_dates": sorted(deg["on_store_trade_dates"])}


def _mes_degraded(start: RootStart) -> dict[str, Any]:
    import pyarrow.parquet as pq

    raw = (pq.read_schema(start.store_path).metadata or {}).get(b"propexperiment")
    meta = json.loads(raw) if raw else {}
    days = sorted({str(d["date"]) if isinstance(d, Mapping) else str(d)
                   for d in meta.get("degraded_vendor_days", [])})
    return {"source": f"{Path(start.store_path).name} metadata degraded_vendor_days",
            "vendor_degraded_utc_dates": days, "on_store_trade_dates": None}


def closure_counts(root: str, frame: pd.DataFrame) -> dict[str, int]:
    """Bars outside the group calendar's open intervals, and of those the close-minute prints
    (lead ruling L-3: booked to the session they close). Counted, not refused: the loader has
    already booked every bar under L-3 to its own trade-date label."""
    from data.group_session import assign_trade_dates, load_group_calendar, open_intervals
    from rules.products import product

    ts = frame["ts_event"].to_numpy(np.int64)
    if len(ts) == 0:
        return {"outside_open_intervals": 0, "close_minute": 0}
    days = frame["trade_date"].astype(str)
    lo, hi = date.fromisoformat(days.iloc[0][:10]), date.fromisoformat(days.iloc[-1][:10])
    opened = open_intervals(load_group_calendar(product(root).group), lo, hi)
    got = assign_trade_dates(opened, ts, close_minute_to_previous=True)
    boundary = got.boundary if got.boundary is not None else np.zeros(len(ts), dtype=bool)
    return {"outside_open_intervals": int(got.in_closure.sum()),
            "close_minute": int(boundary.sum())}


def _root_record(start: RootStart, leg: Any, frame: pd.DataFrame, degraded: dict[str, Any],
                 agreement: dict[str, Any]) -> dict[str, Any]:
    iso = {d.isoformat() for d in leg.trade_dates}
    listed = degraded["on_store_trade_dates"]
    in_window = sorted(d for d in (listed if listed is not None
                                   else degraded["vendor_degraded_utc_dates"]) if d in iso)
    flagged = frame["vendor_degraded_day"].to_numpy(dtype=bool)
    flagged_days = sorted(set(frame.loc[flagged, "trade_date"].astype(str)))
    lo, hi = start.s_x, TRAIN_LAST
    entry = dict(start.entry)
    return {
        "root": start.root, "store": start.store, "store_path": start.store_path,
        "store_sha256": start.store_sha256, "s_x": start.s_x.isoformat(),
        "bars": int(len(frame)), "trade_dates": len(leg.trade_dates),
        "first_trade_date": leg.trade_dates[0].isoformat() if leg.trade_dates else None,
        "last_trade_date": leg.trade_dates[-1].isoformat() if leg.trade_dates else None,
        "splice_trade_dates_in_window": sum(lo <= d <= hi for d in leg.splice_trade_dates),
        "roll_blackout_dates_in_window": sum(lo <= d <= hi for d in leg.roll_blackout),
        "bars_in_scheduled_closure": int(frame["in_scheduled_closure"].to_numpy(bool).sum()),
        "bars_closure": closure_counts(start.root, frame),
        "degraded": {**degraded, "in_window_trade_dates": in_window,
                     "flagged_bar_trade_dates": flagged_days},
        "start_rule": {"s_x": entry.get("s_x"), "s_x_015": entry.get("s_x_015"),
                       "s_x_040": entry.get("s_x_040"), "v_ref": entry.get("v_ref"),
                       "m_star": entry.get("m_star"), "source": entry.get("source"),
                       "monthly_medians": entry.get("monthly_medians"),
                       "day_session_ct": entry.get("day_session_ct"),
                       "research_path": start.research_path,
                       "research_sha256": start.research_sha256,
                       "step2_or_store_sha256": start.store_sha256,
                       "inputs": [{"path": p, "sha256": s} for p, s in start.inputs],
                       "frozen_start_rule_file": agreement},
    }


def load_root(start: RootStart, *, step2_root: Path, summaries_root: Path, repo_root: Path
              ) -> tuple[pd.DataFrame, frozenset[date], dict[str, Any]]:
    """(compact bars from S_X, the roll blackout, the report record) of one root."""
    leg = load_root_leg(start, step2_root=step2_root)
    refuse_late(start.root, leg.frame)
    degraded = (_mes_degraded(start) if start.store == MES_STORE
                else _summary_degraded(start, summaries_root))
    agreement = frozen_start_agreement(start.root, start, repo_root=repo_root)
    record = _root_record(start, leg, leg.frame, degraded, agreement)
    bars = compact_bars(leg.frame)
    blackout = frozenset(leg.roll_blackout)
    del leg
    gc.collect()
    return bars, blackout, record


# ------------------------------------------------------------------ the world ----
@dataclass(frozen=True)
class Phase1World:
    vehicles: tuple[str, ...]  # traded vehicles kept (decision rows)
    first: date  # the earliest S_X of the vehicles' price paths
    last: date  # TRAIN_LAST
    bars_first: date  # first bar trade date over every root
    calendar: tuple[date, ...]  # V2.9 training calendar
    bars: Mapping[str, pd.DataFrame]  # by root (price paths + MES), compact
    frames: Mapping[str, pd.DataFrame]  # empty: no engine in this stage
    releases: Any  # screening.stage_e_rules.ReleaseCalendar
    costs: Mapping[str, Any]  # vehicle -> frozen D8 LegInputs
    blackout: Mapping[str, frozenset[date]]  # root -> roll-blackout dates (L-8)
    legs: Mapping[str, tuple[str, ...]]  # vehicle -> loaded roots its features may read
    requested: tuple[str, ...] = ()
    starts: Mapping[str, RootStart] = field(default_factory=dict)
    dropped: Mapping[str, str] = field(default_factory=dict)  # root -> reason (P-3)
    coverage: Coverage | None = None
    roots: Mapping[str, Mapping[str, Any]] = field(default_factory=dict)  # root -> record
    mes_status: str = "loaded"  # E.12 lead rule P-1a: "loaded" | "refused"
    mes_refusal: str | None = None  # "MES store refused: <exception class>: <message>"


def _starts(requested: Sequence[str], *, step2_root: Path, research_root: Path,
            mes_path: Path, research_sha256: Mapping[str, str] | None,
            mes_start: RootStart | None, repo_root: Path
            ) -> tuple[dict[str, RootStart], str | None]:
    """(S_X per root, MES's refusal text or None). P-1a: a failing D.1f record check
    (StartDatesRefusal: its pinned sha256, its presence or its re-run) makes MES unavailable."""
    from screening.stage_e_frozen import load_frozen_tables
    from screening.stage_e_start_dates import StartDatesRefusal

    tables = load_frozen_tables()
    shas = tables.research_parquet_sha256 if research_sha256 is None else research_sha256
    out = {p: root_start(p, step2_root=step2_root, research_root=research_root,
                         research_sha256=shas.get(p), tables=tables)
           for p in sorted({price_path(v) for v in requested})}
    if mes_start is None:
        try:
            mes_start = mes_root_start(mes_path, record_root=repo_root)
        except StartDatesRefusal as exc:
            return out, mes_refused(exc)
    if mes_start.s_x is None:
        raise Phase1Error("MES has no S_X (D4 fixes it at 2020-02-03)")
    out[MES] = mes_start
    return out, None


def mes_refused(exc: BaseException) -> str:
    """E.12 lead rule P-1a: the reason every signal reading MES is excluded."""
    return f"MES store refused: {type(exc).__name__}: {exc}"


def phase1_world(vehicles: Sequence[str], *, step2_root: Path | None = None,
                 research_root: Path | None = None, mes_path: Path | None = None,
                 summaries_root: Path | None = None,
                 research_sha256: Mapping[str, str] | None = None,
                 mes_start: RootStart | None = None,
                 repo_root: Path | None = None) -> Phase1World:
    """The phase-1 world of ``vehicles`` from the frozen stores (module docstring). Defaults: the
    repository's stores (data.config STEP2_ROOT, PROCESSED_ROOT, MES's confirmation parquet,
    reports/step2). ``research_sha256`` (default E.2a's record) and ``mes_start`` (default D.1f's
    record) exist for the fixture stores of the tests."""
    from data.config import PROCESSED_ROOT, REPO_ROOT, STEP2_ROOT
    from data.research_bars import CONFIRMATION_SERIES_PATH
    from data.step2_store import STEP2_REPORTS
    from ml_route_v2.synthetic import legs_by_vehicle, training_calendar
    from ml_route_v2.targets import frozen_costs
    from screening.stage_e_rules import load_release_calendar

    repo = Path(repo_root or REPO_ROOT)
    step2 = Path(step2_root or STEP2_ROOT)
    requested = check_vehicles(vehicles)
    starts, mes_refusal = _starts(requested, step2_root=step2, research_root=Path(research_root or
                                                                     PROCESSED_ROOT),
                     mes_path=Path(mes_path or CONFIRMATION_SERIES_PATH),
                     research_sha256=research_sha256, mes_start=mes_start, repo_root=repo)
    dropped = {r: "empty start window: D4's rule found no qualifying month (P-3)"
               for r, s in starts.items() if s.s_x is None}
    kept = tuple(v for v in requested if price_path(v) not in dropped)
    if not kept:
        raise Phase1Error(f"every vehicle's price path has an empty window: {sorted(dropped)}")
    bars: dict[str, pd.DataFrame] = {}
    blackout: dict[str, frozenset[date]] = {}
    records: dict[str, Mapping[str, Any]] = {}
    from data.stage_e_bars import StageEBarRefusal

    for root in sorted(r for r in starts if r not in dropped):
        try:
            bars[root], blackout[root], records[root] = load_root(
                starts[root], step2_root=step2,
                summaries_root=Path(summaries_root or STEP2_REPORTS), repo_root=repo)
        except StageEBarRefusal as exc:
            if root != MES:
                raise  # a price-path refusal stops the build (P-1a: MES only)
            mes_refusal = mes_refused(exc)
            gc.collect()
    first = min(starts[price_path(v)].s_x for v in kept)
    calendar = training_calendar(kept, first, TRAIN_LAST)
    if not calendar or calendar[-1] >= FORBIDDEN_FROM:
        raise Phase1WindowError(f"training calendar {first}..{TRAIN_LAST} is empty or late")
    coverage = signal_coverage(kept, unavailable={MES: mes_refusal} if mes_refusal else None)
    legs = {v: tuple(r for r in legs_by_vehicle((v,))[v] if r in bars) for v in kept}
    bars_first = min(date.fromisoformat(str(f["trade_date"].iloc[0])[:10])
                     for f in bars.values() if len(f))
    return Phase1World(
        vehicles=kept, first=first, last=TRAIN_LAST, bars_first=bars_first, calendar=calendar,
        bars=MappingProxyType(bars), frames=MappingProxyType({}),
        releases=load_release_calendar(repo), costs=MappingProxyType(frozen_costs(kept)),
        blackout=MappingProxyType(blackout), legs=MappingProxyType(legs), requested=requested,
        starts=MappingProxyType(starts), dropped=MappingProxyType(dropped), coverage=coverage,
        roots=MappingProxyType(records), mes_status="refused" if mes_refusal else "loaded",
        mes_refusal=mes_refusal)


__all__ = [
    "COMPACT_COLUMNS", "EXTRA_ROOTS", "FORBIDDEN_FROM_NS", "MES", "NO_STORE", "RANKING_FILE",
    "Coverage", "Phase1Error", "Phase1Subset", "phase1_subset",
    "Phase1World", "Phase1WindowError", "RootStart", "available_roots", "check_vehicles",
    "compact_bars", "frozen_start_agreement", "load_root", "load_root_leg", "mes_refused",
    "mes_root_start", "phase1_world", "price_path", "refuse_late", "root_start", "signal_coverage",
]
