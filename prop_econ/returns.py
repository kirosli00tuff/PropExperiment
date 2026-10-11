"""Stage E.19 shocks: daily day-session returns of NQ, CL, GC, ZN, 6E and the two shock sources.

Implements reports/stage_e19_briefs/sim_spec.md section 1 (lead, binding). Reads return magnitudes
only from the owned E.12 training stores (trade dates 2019-05-06..2024-02-29); computes no signal.

- Window per root: design D6's day session [O_X, C_X) in CT on the trade date's own calendar day
  (screening.vehicles.D6_SESSIONS via session_of, the frozen table D8's day buckets cover).
- Kept date: the bar at exactly O_X and the bar at exactly C_X - 1 min both exist and one
  instrument covers the whole window. Entry = open of the O_X bar, exit = close of the last bar
  before C_X, H / L = max high / min low over the window. Every skip is counted by reason.
- r, up, dn in USD per full-size contract (price ticks x tick value, exact on the tick grid).
- Demeaned per path; sigma_full = sd (ddof 1); long and short z, w columns (w <= min(0, z)).
- Shock sources: 5-day block bootstrap (fat tails) and the normal / Brownian-bridge comparison,
  sharing the product sequence and direction signs for a given seed.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import os
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, time
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

from prop_econ.types import MICROS_PER_FULL, ProductSpec, ShockSet

REPO_ROOT = Path(__file__).resolve().parents[1]
ROOTS: tuple[str, ...] = ("NQ", "CL", "GC", "ZN", "6E")
MICRO_OF: dict[str, str | None] = {"NQ": "MNQ", "CL": "MCL", "GC": "MGC", "ZN": None, "6E": "M6E"}
TRAIN_FIRST = date(2019, 5, 6)
TRAIN_LAST = date(2024, 2, 29)
BLOCK_DAYS = 5
COST_TABLE = REPO_ROOT / "reports" / "stage_e2a_costs.json"
COST_WALL = REPO_ROOT / "reports" / "stage_e10_research" / "cost_wall.json"
SUMMARY_JSON = REPO_ROOT / "reports" / "stage_e19_returns_summary.json"
SUMMARY_MD = REPO_ROOT / "reports" / "stage_e19_returns_summary.md"
STORE_COLUMNS = ("ts_event", "open", "high", "low", "close", "instrument_id", "trade_date")
SKIP_REASONS = ("no_bars_in_window", "instrument_change", "missing_open_bar", "missing_close_bar")
CT = ZoneInfo("America/Chicago")
PT = ZoneInfo("America/Vancouver")
NS_PER_MIN = 60 * 1_000_000_000
GRID_TOL = 1e-6  # prices must sit on the tick grid to this fraction of a tick
TAIL_Z = 4.0
TAILS = ("bootstrap", "normal")
DIRECTIONS = ("random", "long")
COST_MODELS = ("d8", "wall")


class ReturnsError(ValueError):
    """An input breaks section 1 of the spec; nothing is guessed."""


def store_path(root: str) -> Path:
    return (REPO_ROOT / "data" / "processed_step2" / root
            / f"ohlcv-1m_{root}_v_0_2019-05-06_2024-02-29_step2.parquet")


# ------------------------------------------------------------------ contract facts ----
@functools.cache
def _cost_json() -> dict:
    return json.loads(COST_TABLE.read_text())


@dataclass(frozen=True)
class Contract:
    root: str
    group: str
    tick: Decimal  # vendor tick (price units of the store)
    tick_value_usd: Decimal
    open_ct: time
    close_ct: time

    @property
    def multiplier(self) -> Fraction:
        """USD per one price unit of the full-size contract."""
        return Fraction(self.tick_value_usd) / Fraction(self.tick)


def contract(root: str) -> Contract:
    """Tick facts from the frozen D8 table; the window from D6 (screening.vehicles.session_of)."""
    from screening.vehicles import session_of  # frozen D6 table, read-only

    entry = _cost_json()["products"][root]
    if int(entry["vendor_price_factor"]) != 1:
        raise ReturnsError(f"{root}: vendor price factor {entry['vendor_price_factor']} != 1")
    _, open_ct, close_ct = session_of(root, entry["group"])
    d8 = entry["day_session_ct"]
    if (open_ct.strftime("%H:%M"), close_ct.strftime("%H:%M")) != (d8["open"], d8["close"]):
        raise ReturnsError(f"{root}: D6 session {open_ct}-{close_ct} != D8's {d8}")
    return Contract(root, entry["group"], Decimal(entry["vendor_tick"]),
                    Decimal(str(entry["tick_value_usd"])), open_ct, close_ct)


# ------------------------------------------------------------------ daily moves ----
@dataclass(frozen=True)
class SessionMoves:
    """Per kept trade date: USD per full-size contract of the day-session position."""

    root: str
    dates: np.ndarray  # datetime64[D], kept dates in order
    r: np.ndarray  # C - O
    up: np.ndarray  # H - O (>= 0)
    dn: np.ndarray  # L - O (<= 0)
    n_trade_dates: int
    skips: dict[str, int]
    early_halt_in_missing_close: int  # diagnostic: missing-close skips on CME early-halt days


def _ct_day_minute(ts_ns: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    import pandas as pd

    local = pd.DatetimeIndex(pd.to_datetime(ts_ns, utc=True)).tz_convert(CT).tz_localize(None)
    loc = local.values.astype("datetime64[m]")
    day = loc.astype("datetime64[D]")
    minute = (loc - day.astype("datetime64[m]")).astype(np.int64)
    return day, minute


def _ticks_usd(diff: np.ndarray, c: Contract) -> np.ndarray:
    ticks = diff / float(c.tick)
    rounded = np.rint(ticks)
    if ticks.size and np.max(np.abs(ticks - rounded)) > GRID_TOL:
        raise ReturnsError(f"{c.root}: a price move is off the {c.tick} tick grid")
    return rounded * float(c.tick_value_usd)


def session_moves(ts_ns: np.ndarray, trade_date: np.ndarray, open_: np.ndarray,
                  high: np.ndarray, low: np.ndarray, close: np.ndarray,
                  instrument_id: np.ndarray, c: Contract, *, first: date = TRAIN_FIRST,
                  last: date = TRAIN_LAST) -> SessionMoves:
    """Section 1 rows from one root's time-ordered 1-minute bars (ts_ns = bar open, UTC ns)."""
    from data.session import early_halt_ct

    ts = np.asarray(ts_ns, dtype=np.int64)
    if ts.size > 1 and not (np.diff(ts) > 0).all():
        raise ReturnsError(f"{c.root}: bars are not strictly increasing in time")
    tdate = np.asarray(trade_date).astype("datetime64[D]")
    all_dates = np.unique(tdate)
    lo_d, hi_d = np.datetime64(first), np.datetime64(last)
    if all_dates.size and (all_dates[0] < lo_d or all_dates[-1] > hi_d):
        raise ReturnsError(f"{c.root}: trade dates {all_dates[0]}..{all_dates[-1]} leave "
                           f"{first}..{last}")
    o_min = c.open_ct.hour * 60 + c.open_ct.minute
    c_min = c.close_ct.hour * 60 + c.close_ct.minute
    ct_day, minute = _ct_day_minute(ts)
    mask = (ct_day == tdate) & (minute >= o_min) & (minute < c_min)
    idx = np.flatnonzero(mask)
    wdates = tdate[idx]
    if wdates.size > 1 and (np.diff(wdates.astype(np.int64)) < 0).any():
        raise ReturnsError(f"{c.root}: trade dates are not ordered inside the windows")
    days, starts = np.unique(wdates, return_index=True)
    if days.size == 0:
        empty = np.array([], dtype=np.float64)
        return SessionMoves(c.root, np.array([], dtype="datetime64[D]"), empty, empty, empty,
                            int(all_dates.size), {**dict.fromkeys(SKIP_REASONS, 0),
                                                  "no_bars_in_window": int(all_dates.size)}, 0)
    ends = np.append(starts[1:], wdates.size) - 1
    i0, i1 = idx[starts], idx[ends]
    inst = np.asarray(instrument_id)[idx]
    changed = np.minimum.reduceat(inst, starts) != np.maximum.reduceat(inst, starts)
    open_ok = minute[i0] == o_min
    close_ok = minute[i1] == c_min - 1
    keep = ~changed & open_ok & close_ok
    skips = {"no_bars_in_window": int(all_dates.size - days.size),
             "instrument_change": int(changed.sum()),
             "missing_open_bar": int((~changed & ~open_ok).sum()),
             "missing_close_bar": int((~changed & open_ok & ~close_ok).sum())}
    miss_close = days[~changed & open_ok & ~close_ok]
    halts = sum(early_halt_ct(d.astype(object)) is not None for d in miss_close)
    o = np.asarray(open_, dtype=np.float64)[i0]
    h = np.maximum.reduceat(np.asarray(high, dtype=np.float64)[idx], starts)
    lo = np.minimum.reduceat(np.asarray(low, dtype=np.float64)[idx], starts)
    cl = np.asarray(close, dtype=np.float64)[i1]
    return SessionMoves(c.root, days[keep], _ticks_usd(cl - o, c)[keep],
                        _ticks_usd(h - o, c)[keep], _ticks_usd(lo - o, c)[keep],
                        int(all_dates.size), skips, int(halts))


def read_store(path: Path, c: Contract) -> SessionMoves:
    """Read only the needed columns of one store and reduce it to daily moves."""
    import pyarrow.parquet as pq

    table = pq.read_table(path, columns=list(STORE_COLUMNS))
    enc = table.column("trade_date").combine_chunks().dictionary_encode()
    labels = np.array(enc.dictionary.to_pylist(), dtype="datetime64[D]")
    tdate = labels[enc.indices.to_numpy()]
    cols = {k: table.column(k).to_numpy() for k in STORE_COLUMNS if k != "trade_date"}
    del table, enc
    return session_moves(cols["ts_event"], tdate, cols["open"], cols["high"], cols["low"],
                         cols["close"], cols["instrument_id"], c)


# ------------------------------------------------------------------ standardized path ----
@dataclass(frozen=True)
class PathShocks:
    moves: SessionMoves
    mean_r_usd: float  # removed by demeaning
    sigma_full_usd: float
    z_long: np.ndarray
    w_long: np.ndarray
    z_short: np.ndarray
    w_short: np.ndarray

    @property
    def root(self) -> str:
        return self.moves.root

    @property
    def n_kept(self) -> int:
        return int(self.z_long.size)


def standardize(m: SessionMoves) -> PathShocks:
    if m.r.size < BLOCK_DAYS + 1:
        raise ReturnsError(f"{m.root}: {m.r.size} kept dates, too few")
    mean_r = float(np.mean(m.r))
    rp = m.r - mean_r
    sigma = float(np.std(rp, ddof=1))
    zero = np.zeros_like(rp)
    return PathShocks(m, mean_r, sigma, rp / sigma, np.minimum(np.minimum(m.dn, rp), zero) / sigma,
                      -rp / sigma, np.minimum(np.minimum(-m.up, -rp), zero) / sigma)


@functools.cache
def load_paths() -> tuple[PathShocks, ...]:
    """The five paths in ROOTS order, one store in memory at a time (cached per process)."""
    return tuple(standardize(read_store(store_path(r), contract(r))) for r in ROOTS)


# ------------------------------------------------------------------ costs and specs ----
def d8_round_trips() -> dict[str, float]:
    """D8 day-session mean RT USD per contract (sim.product_costs), checked against the table."""
    from sim.product_costs import load_cost_table

    models = load_cost_table()
    out: dict[str, float] = {}
    for root in ROOTS:
        for v in (root, MICRO_OF[root]):
            if v is None:
                continue
            m = models[v]
            day = [b for b in m.buckets if b.day_session]
            rt = [(m.commission_rt_ticks + b.side_ticks["buy"] + b.side_ticks["sell"])
                  * m.tick_value_usd for b in day]
            out[v] = float(sum(rt) / len(rt))
            ref = _cost_json()["products"][v]["headline_day_session"]["round_turn_usd"]["mean"]
            if not math.isclose(out[v], ref, rel_tol=1e-9):
                raise ReturnsError(f"{v}: D8 day mean {out[v]} != table headline {ref}")
    return out


def _wall_rule_ticks(entry: dict) -> float:
    """E.10 rule (reports/stage_e10_briefs/cost_wall.py): commission + 2 x worst bucket side."""
    side = max(max(b["side_ticks"]["buy"], b["side_ticks"]["sell"]) for b in entry["buckets"])
    return float(entry["commission_rt_ticks"]) + 2.0 * side


def wall_round_trips() -> tuple[dict[str, float], dict[str, str]]:
    """E.10 cost wall RT_X USD per contract and its source per vehicle. Vehicles without a
    cost_wall.json row (NQ, CL, GC, M6E) get the same rule applied to the D8 table."""
    rows = {r["vehicle"]: r for r in json.loads(COST_WALL.read_text())["rows"]}
    prods = _cost_json()["products"]
    out: dict[str, float] = {}
    src: dict[str, str] = {}
    for root in ROOTS:
        for v in (root, MICRO_OF[root]):
            if v is None:
                continue
            tv = float(prods[v]["tick_value_usd"])
            rule = _wall_rule_ticks(prods[v])
            if v in rows:
                if abs(round(rule, 3) - rows[v]["rt_wall_ticks"]) > 1e-9:
                    raise ReturnsError(f"{v}: E.10 rule {rule} != cost_wall row")
                out[v], src[v] = rows[v]["rt_wall_ticks"] * tv, "cost_wall.json row"
            else:
                out[v], src[v] = rule * tv, "E.10 rule applied to the D8 table (no row)"
    return out, src


def product_specs(sigma_full: dict[str, float], cost_model: str = "d8"
                  ) -> tuple[ProductSpec, ...]:
    if cost_model not in COST_MODELS:
        raise ValueError(f"cost_model must be one of {COST_MODELS}")
    rt = d8_round_trips() if cost_model == "d8" else wall_round_trips()[0]
    specs = []
    for root in ROOTS:
        micro = MICRO_OF[root]
        s = float(sigma_full[root])
        specs.append(ProductSpec(root, s, rt[root], micro,
                                 None if micro is None else s / MICROS_PER_FULL,
                                 None if micro is None else rt[micro]))
    return tuple(specs)


# ------------------------------------------------------------------ shock sources ----
def _streams(seed: int) -> dict[str, np.random.Generator]:
    kids = np.random.SeedSequence(seed).spawn(4)
    return {k: np.random.Generator(np.random.PCG64(s))
            for k, s in zip(("product", "start", "sign", "normal"), kids, strict=True)}


def _allowed(products: str | Sequence[str]) -> np.ndarray:
    names = ROOTS if products == "all" else ((products,) if isinstance(products, str)
                                              else tuple(products))
    bad = [p for p in names if p not in ROOTS]
    if bad or not names:
        raise ValueError(f"products must be 'all' or roots of {ROOTS}, not {products!r}")
    return np.array([ROOTS.index(p) for p in names], dtype=np.int16)


@dataclass(frozen=True)
class Layout:
    """Draws shared by both sources for one seed: block products and direction signs."""

    prod_block: np.ndarray  # (n_paths, n_blocks) int16
    start_u: np.ndarray  # (n_paths, n_blocks) uniform [0, 1) block-start fractions
    sign: np.ndarray  # (n_paths, n_days) int8, +1 long / -1 short
    n_days: int

    @property
    def prod(self) -> np.ndarray:
        return np.repeat(self.prod_block, BLOCK_DAYS, axis=1)[:, : self.n_days]


def draw_layout(n_paths: int, n_days: int, seed: int, direction: str = "random",
                products: str | Sequence[str] = "all") -> Layout:
    if direction not in DIRECTIONS:
        raise ValueError(f"direction must be one of {DIRECTIONS}")
    if n_paths < 1 or n_days < 1:
        raise ValueError("n_paths and n_days must be >= 1")
    allowed = _allowed(products)
    g = _streams(seed)
    n_blocks = -(-n_days // BLOCK_DAYS)
    prod_block = allowed[g["product"].integers(0, allowed.size, size=(n_paths, n_blocks))]
    start_u = g["start"].random((n_paths, n_blocks))
    if direction == "random":
        sign = (g["sign"].integers(0, 2, size=(n_paths, n_days), dtype=np.int8) * 2 - 1)
    else:
        sign = np.ones((n_paths, n_days), dtype=np.int8)
    return Layout(prod_block.astype(np.int16), start_u, sign.astype(np.int8), n_days)


def bootstrap_shocks(paths: Sequence[PathShocks], specs: tuple[ProductSpec, ...], lay: Layout
                     ) -> ShockSet:
    """5-day blocks from one path each; block start uniform over that path's kept dates."""
    n_kept = np.array([p.n_kept for p in paths], dtype=np.int64)
    base = np.concatenate([[0], np.cumsum(n_kept)[:-1]])
    pb = lay.prod_block.astype(np.int64)
    start = np.floor(lay.start_u * (n_kept[pb] - BLOCK_DAYS + 1)).astype(np.int64)
    first = (base[pb] + start)
    offs = np.arange(BLOCK_DAYS, dtype=np.int64)
    idx = (first[:, :, None] + offs).reshape(first.shape[0], -1)[:, : lay.n_days]
    long_ = lay.sign > 0
    zl, wl = np.concatenate([p.z_long for p in paths]), np.concatenate([p.w_long for p in paths])
    zs, ws = np.concatenate([p.z_short for p in paths]), np.concatenate([p.w_short for p in paths])
    z = np.where(long_, zl[idx], zs[idx])
    w = np.where(long_, wl[idx], ws[idx])
    return ShockSet(z, w, lay.prod, specs)


def bridge_min(z: np.ndarray, u: np.ndarray) -> np.ndarray:
    """Minimum of a unit-variance Brownian bridge from 0 to z on [0, 1]; u in (0, 1]."""
    w = (z - np.sqrt(z * z - 2.0 * np.log(u))) / 2.0
    return np.minimum(w, np.minimum(z, 0.0))  # guards a 1-ulp sqrt overshoot only


def normal_shocks(specs: tuple[ProductSpec, ...], lay: Layout, seed: int) -> ShockSet:
    g = _streams(seed)["normal"]
    shape = lay.sign.shape
    z = lay.sign * g.standard_normal(shape)
    u = 1.0 - g.random(shape)  # (0, 1]
    return ShockSet(z, bridge_min(z, u), lay.prod, specs)


def build_shocks(n_paths: int, n_days: int, seed: int, tail: str = "bootstrap",
                 direction: str = "random", products: str | Sequence[str] = "all",
                 cost_model: str = "d8", paths: Sequence[PathShocks] | None = None
                 ) -> ShockSet:
    """ShockSet (n_paths, n_days). ``products`` = 'all' or one root (per-product restriction);
    the ShockSet always carries all five ProductSpecs in ROOTS order so prod indices are stable."""
    if tail not in TAILS:
        raise ValueError(f"tail must be one of {TAILS}")
    paths = load_paths() if paths is None else tuple(paths)
    if tuple(p.root for p in paths) != ROOTS:
        raise ReturnsError(f"paths must be in {ROOTS} order")
    specs = product_specs({p.root: p.sigma_full_usd for p in paths}, cost_model)
    lay = draw_layout(n_paths, n_days, seed, direction, products)
    return bootstrap_shocks(paths, specs, lay) if tail == "bootstrap" else normal_shocks(
        specs, lay, seed)


# ------------------------------------------------------------------ summary ----
def _moments(z: np.ndarray) -> tuple[float, float]:
    c = z - z.mean()
    m2 = float(np.mean(c**2))
    return float(np.mean(c**3)) / m2**1.5, float(np.mean(c**4)) / m2**2 - 3.0


def path_summary(p: PathShocks, d8: dict[str, float], wall: dict[str, float]) -> dict:
    c = contract(p.root)
    skew, kurt = _moments(p.z_long)
    micro = MICRO_OF[p.root]
    sig = {p.root: p.sigma_full_usd}
    if micro is not None:
        sig[micro] = p.sigma_full_usd / MICROS_PER_FULL
    vehicles = {v: {"sigma_usd": s, "rt_d8_usd": d8[v], "rt_wall_usd": wall[v],
                    "cost_per_sigma": {f"{m}_k{k}": k * rt[v] / s
                                       for m, rt in (("d8", d8), ("wall", wall))
                                       for k in (1, 3)}}
                for v, s in sig.items()}
    return {
        "root": p.root, "window_ct": f"{c.open_ct:%H:%M}-{c.close_ct:%H:%M}",
        "multiplier_usd_per_point": float(c.multiplier),
        "trade_dates": p.moves.n_trade_dates, "dates_kept": p.n_kept,
        "first_kept": str(p.moves.dates[0]), "last_kept": str(p.moves.dates[-1]),
        "skips": p.moves.skips,
        "early_halt_days_in_missing_close": p.moves.early_halt_in_missing_close,
        "mean_r_removed_usd_full": p.mean_r_usd, "sigma_full_usd": p.sigma_full_usd,
        "sigma_micro_usd": None if micro is None else p.sigma_full_usd / MICROS_PER_FULL,
        "z_skew": skew, "z_excess_kurtosis": kurt,
        "share_abs_z_gt_4": float(np.mean(np.abs(p.z_long) > TAIL_Z)),
        "w_long": {"mean": float(p.w_long.mean()), "p01": float(np.quantile(p.w_long, 0.01))},
        "w_short": {"mean": float(p.w_short.mean()), "p01": float(np.quantile(p.w_short, 0.01))},
        "vehicles": vehicles,
    }


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_summary(paths: Sequence[PathShocks]) -> dict:
    d8 = d8_round_trips()
    wall, wall_src = wall_round_trips()
    now = datetime.now(UTC)
    return {
        "stage": "E.19", "spec": "reports/stage_e19_briefs/sim_spec.md section 1",
        "generated_pdt": now.astimezone(PT).strftime("%Y-%m-%d %H:%M %Z"),
        "definitions": {
            "kept_date": "bars at exactly O_X and C_X-1min exist, one instrument_id in window",
            "skip_precedence": list(SKIP_REASONS),
            "z": "long column, (r - mean r)/sigma_full; short z = -z",
            "skew_kurtosis": "population moments of z (biased), excess = m4/m2^2 - 3",
            "cost_per_sigma": "k x RT / sigma of the same vehicle, k in {1, 3}",
        },
        "inputs_sha256": {**{f"store_{r}": _sha256(store_path(r)) for r in ROOTS},
                          "stage_e2a_costs.json": _sha256(COST_TABLE),
                          "cost_wall.json": _sha256(COST_WALL)},
        "wall_source": wall_src,
        "paths": [path_summary(p, d8, wall) for p in paths],
    }


def _md(s: dict) -> str:
    out = [f"# Stage E.19 returns summary ({s['generated_pdt']})", "",
           f"Spec: {s['spec']}. Generated by prop_econ/returns.py; figures from "
           "reports/stage_e19_returns_summary.json.", "",
           "| Path | Window CT | Dates | Kept | Skips (none/roll/open/close) | Mean r removed $ | "
           "sigma_full $ | sigma_micro $ | skew | ex. kurt | share abs z>4 | w_L mean / p01 | "
           "w_S mean / p01 |", "|" + "---|" * 13]
    for p in s["paths"]:
        k = p["skips"]
        sm = "-" if p["sigma_micro_usd"] is None else f"{p['sigma_micro_usd']:.2f}"
        out.append(
            f"| {p['root']} | {p['window_ct']} | {p['trade_dates']} | {p['dates_kept']} | "
            f"{k['no_bars_in_window']}/{k['instrument_change']}/{k['missing_open_bar']}/"
            f"{k['missing_close_bar']} | {p['mean_r_removed_usd_full']:.2f} | "
            f"{p['sigma_full_usd']:.2f} | {sm} | {p['z_skew']:.3f} | "
            f"{p['z_excess_kurtosis']:.3f} | {p['share_abs_z_gt_4']:.4f} | "
            f"{p['w_long']['mean']:.3f} / {p['w_long']['p01']:.3f} | "
            f"{p['w_short']['mean']:.3f} / {p['w_short']['p01']:.3f} |")
    out += ["", "| Vehicle | sigma $ | RT D8 $ | RT wall $ (source) | D8 k=1 | D8 k=3 | wall k=1 | "
            "wall k=3 |", "|" + "---|" * 8]
    for p in s["paths"]:
        for v, x in p["vehicles"].items():
            c = x["cost_per_sigma"]
            src = "row" if s["wall_source"][v].startswith("cost_wall") else "rule"
            out.append(f"| {v} | {x['sigma_usd']:.2f} | {x['rt_d8_usd']:.2f} | "
                       f"{x['rt_wall_usd']:.2f} ({src}) | {c['d8_k1']:.4f} | {c['d8_k3']:.4f} | "
                       f"{c['wall_k1']:.4f} | {c['wall_k3']:.4f} |")
    out += ["", "Missing-close skips on CME early-halt days: " + ", ".join(
        f"{p['root']} {p['early_halt_days_in_missing_close']}" for p in s["paths"]) + ".",
        "Wall source 'rule': no cost_wall.json row for that vehicle; the E.10 rule "
        "(commission + 2 x worst bucket side, reports/stage_e10_briefs/cost_wall.py) was applied "
        "to the frozen D8 table.", ""]
    return "\n".join(out)


def write_summary(json_path: Path = SUMMARY_JSON, md_path: Path = SUMMARY_MD) -> dict:
    s = build_summary(load_paths())
    json_path.write_text(json.dumps(s, indent=1) + "\n")
    md_path.write_text(_md(s))
    return s


if __name__ == "__main__":
    os.nice(10)
    summary = write_summary()
    for row in summary["paths"]:
        print(row["root"], row["window_ct"], row["dates_kept"], row["skips"],
              round(row["sigma_full_usd"], 2))
