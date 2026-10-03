"""Shared machinery of the V2.3 signal library: types, bar arrays, clock helpers, releases.

docs/STAGE_E_ML_V2_DESIGN.md V2.3; contract reports/stage_e11_interfaces.md sections 1 and 3.

Conventions (interfaces section 1):
- a bar frame per root has the repo's BAR_COLUMNS; ``ts_event`` is the bar OPEN in UTC ns and the
  bar closes 60 s later; a value used at decision time t reads only bars with ts_event <= t - 60 s;
- "the bar at hh:mm of CT date D" is the bar whose open is hh:mm CT on calendar date D (members'
  clock, e.g. k2/_event_common.ct_open_ns); with a trade-date check where the member has one;
- a signal frame is aligned to ctx.rows and has ``value`` (float64; NaN = missing for data
  reasons), ``applicable`` (float64 0/1) and ``avail_ts_ns`` (int64). Not applicable: value 0,
  avail = t (known at t that nothing applies). Applicable and missing: avail -1.

Signal-leg roll blackout (V2.2 "Excluded dates", lead ruling 2026-10-03). A traded product's own
roll-blackout dates drop its decision rows (the caller's ``exclude`` map to clock.decision_rows).
A signal leg's roll-blackout date drops no row: on a row whose trade date is a roll-blackout date
of a root R, every signal that reads R as a root other than the row's own price-path root is not
applicable (value 0, applicable 0, avail = t), the same treatment as a lead not yet listed. It is
applied once, centrally, by ``apply_leg_blackout`` (called from signals.compute_signals) with
SignalContext.blackout (bar root -> its roll-blackout dates). The roots a row reads come from
SignalSpec.roots_read, except that a spec with ``own_path_only`` reads only the row's own price
path on every row (the pooled ports, G1-G10 and the per-vehicle members whose roots_read is the
union of their vehicles' paths, such as K4-ovr: CL on MCL rows, NG on NG rows), so the rule never
blanks it.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from functools import lru_cache
from typing import Any

import numpy as np
import pandas as pd

from ml_route_v2.constants import UNIVERSE

NS_MIN = 60_000_000_000
NS_DAY = 86_400 * 1_000_000_000
NAT = np.iinfo(np.int64).min
CT_ZONE = "America/Chicago"
_EPOCH = date(1970, 1, 1)


class CausalityError(RuntimeError):
    """A signal value is available after its row's decision time, or a frame breaks the contract."""


class SignalInputMissing(RuntimeError):
    """A signal needs an input (a root's bars, a release list) that the context does not hold."""


@dataclass(frozen=True)
class SignalSpec:
    name: str  # feature column stem, e.g. "k4_eiafade_move" or "g01_ret30"
    family: str  # member id ("K4-eiafade-01") or generic id ("G1")
    cluster: str | None
    kind: str  # "member" | "generic" | "flag" | "id"
    source: str  # file:line of the member definition or design section
    roots_read: tuple[str, ...]  # price-path roots (plus MES) whose bars the signal reads
    normalize: bool  # False for flags and identifiers
    fn: Callable[[SignalContext], pd.DataFrame]
    # V2.2 leg blackout (module docstring): True when each row reads only its own price path among
    # roots_read (roots_read is then the union over the vehicles the signal serves).
    own_path_only: bool = False


@dataclass(frozen=True)
class SignalContext:
    rows: pd.DataFrame  # DecisionRows (all products)
    bars: Mapping[str, pd.DataFrame]  # by price-path root (plus signal-only roots such as MES)
    releases: Any  # ReleaseCalendar (screening.stage_e_rules) or EventCalendar (ml_route.inputs)
    sigma_d: pd.Series  # sigma_X,d in vehicle ticks, aligned to rows (targets.sigma_d)
    # V2.2 leg blackout (module docstring): bar root -> its roll-blackout dates. Empty: no rule.
    blackout: Mapping[str, frozenset[date]] = field(default_factory=dict)
    # Addition to the interfaces contract: a per-context memo (bar arrays, daily tables). It never
    # holds anything but deterministic functions of the four fields above (never of blackout,
    # which is applied after a signal's fn).
    cache: dict = field(default_factory=dict, compare=False, repr=False)


# ------------------------------------------------------------------------------ bars ----
@dataclass(frozen=True)
class BarArrays:
    """One root's bars as arrays (prices in vendor units); ``day`` = trade date in epoch days."""

    root: str
    ts: np.ndarray
    open: np.ndarray
    high: np.ndarray
    low: np.ndarray
    close: np.ndarray
    volume: np.ndarray
    iid: np.ndarray
    day: np.ndarray
    udays: np.ndarray  # the distinct trade dates, ascending
    first: np.ndarray  # index of each trade date's first bar
    last: np.ndarray  # index of each trade date's last bar

    def at(self, when: np.ndarray) -> np.ndarray:
        """Index of the bar opening exactly at ``when`` (UTC ns), -1 when absent."""
        when = np.asarray(when, dtype=np.int64)
        if len(self.ts) == 0:
            return np.full(when.shape, -1, dtype=np.int64)
        pos = np.searchsorted(self.ts, when)
        ok = pos < len(self.ts)
        ok[ok] = self.ts[pos[ok]] == when[ok]
        return np.where(ok, pos, -1).astype(np.int64)

    def last_closed(self, t: np.ndarray) -> np.ndarray:
        """Index of the latest bar closed by ``t`` (ts_event <= t - 60 s), -1 when none."""
        t = np.asarray(t, dtype=np.int64)
        return (np.searchsorted(self.ts, t - NS_MIN, side="right") - 1).astype(np.int64)

    def day_pos(self, days: np.ndarray) -> np.ndarray:
        """Position of each epoch day in ``udays``, -1 when the root has no bar that trade date."""
        days = np.asarray(days, dtype=np.int64)
        pos = np.searchsorted(self.udays, days)
        ok = pos < len(self.udays)
        ok[ok] = self.udays[pos[ok]] == days[ok]
        return np.where(ok, pos, -1).astype(np.int64)

    def on_day(self, idx: np.ndarray, days: np.ndarray) -> np.ndarray:
        """True where ``idx`` is a bar (>= 0) of trade date ``days``."""
        idx = np.asarray(idx, dtype=np.int64)
        ok = idx >= 0
        out = np.zeros(len(idx), dtype=bool)
        out[ok] = self.day[idx[ok]] == np.asarray(days, dtype=np.int64)[ok]
        return out


def trade_date_days(col: pd.Series) -> np.ndarray:
    """A trade_date column (ISO strings, dates, categories or datetime64) as int64 epoch days."""
    if pd.api.types.is_datetime64_any_dtype(col.dtype):
        return col.to_numpy().astype("datetime64[D]").astype(np.int64)
    codes, uniques = pd.factorize(col, sort=False)
    if (codes < 0).any():
        raise SignalInputMissing("a bar has no trade_date")
    parsed = pd.to_datetime(pd.Index(uniques).astype(str).str.slice(0, 10), format="%Y-%m-%d")
    return parsed.to_numpy().astype("datetime64[D]").astype(np.int64)[codes]


def segment_index(lo: np.ndarray, hi: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """(gathered indices, segment starts in them) of the index ranges [lo, hi), hi >= lo; an
    empty segment has no element and its start equals the next segment's."""
    lo = np.asarray(lo, dtype=np.int64)
    n = np.maximum(np.asarray(hi, dtype=np.int64) - lo, 0)
    starts = np.concatenate([[0], np.cumsum(n)[:-1]]) if len(n) else np.zeros(0, np.int64)
    idx = np.repeat(lo - starts, n) + np.arange(int(n.sum()), dtype=np.int64)
    return idx, starts


def window_sums(values: np.ndarray, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """sum(values[lo:hi]) per segment (0 for an empty one), without a full-length cumulative
    array (memory: the gathered windows only)."""
    idx, starts = segment_index(lo, hi)
    out = np.zeros(len(starts))
    if len(idx) == 0:
        return out
    nonempty = np.asarray(hi) > np.asarray(lo)
    sums = np.add.reduceat(np.asarray(values, dtype=np.float64)[idx] if not callable(values)
                           else values(idx), starts[nonempty])
    out[nonempty] = sums
    return out


def bar_arrays(root: str, frame: pd.DataFrame) -> BarArrays:
    ts = frame["ts_event"].to_numpy(np.int64)
    if len(ts) > 1 and not bool(np.all(np.diff(ts) > 0)):
        raise SignalInputMissing(f"{root}: bars are not strictly ascending in ts_event")
    day = trade_date_days(frame["trade_date"])
    if len(day) > 1 and not bool(np.all(np.diff(day) >= 0)):
        raise SignalInputMissing(f"{root}: trade dates are not non-decreasing in ts_event order")
    change = np.flatnonzero(np.diff(day)) + 1 if len(day) else np.zeros(0, np.int64)
    first = np.concatenate([[0], change]).astype(np.int64) if len(day) else change
    udays = day[first].astype(np.int64)
    last = np.append(first[1:], len(day)) - 1
    # prices are float64 views of the frame; volume and instrument_id keep their own dtype (no
    # copy); the trade date is held as int32 epoch days (memory, reading PF-1)
    return BarArrays(root, ts, frame["open"].to_numpy(np.float64),
                     frame["high"].to_numpy(np.float64), frame["low"].to_numpy(np.float64),
                     frame["close"].to_numpy(np.float64), frame["volume"].to_numpy(),
                     frame["instrument_id"].to_numpy(), day.astype(np.int32),
                     udays, first, last.astype(np.int64))


def bars_of(ctx: SignalContext, root: str) -> BarArrays:
    key = ("bars", root)
    if key not in ctx.cache:
        if root not in ctx.bars:
            raise SignalInputMissing(f"the context holds no bars for {root}")
        ctx.cache[key] = bar_arrays(root, ctx.bars[root])
    return ctx.cache[key]


# ------------------------------------------------------------------------------ rows ----
@dataclass(frozen=True)
class RowsView:
    index: pd.Index
    root: np.ndarray  # vehicle (object)
    path: np.ndarray  # price-path root (object)
    cluster: np.ndarray
    group: np.ndarray
    day: np.ndarray  # trade date, epoch days
    t: np.ndarray  # decision_ts_ns
    t_index: np.ndarray
    flatten: np.ndarray
    sigma: np.ndarray  # sigma_X,d (vehicle ticks), NaN where missing

    @property
    def n(self) -> int:
        return len(self.t)

    def where_root(self, roots: tuple[str, ...] | frozenset[str]) -> np.ndarray:
        return np.flatnonzero(np.isin(self.root, list(roots)))

    def by_root(self) -> dict[str, np.ndarray]:
        out: dict[str, np.ndarray] = {}
        for r in pd.unique(self.root):
            out[str(r)] = np.flatnonzero(self.root == r)
        return out


def rows_of(ctx: SignalContext) -> RowsView:
    if "rows" not in ctx.cache:
        r = ctx.rows
        sigma = ctx.sigma_d.reindex(r.index).to_numpy(np.float64)
        ctx.cache["rows"] = RowsView(
            r.index, r["root"].to_numpy(object), r["path_root"].to_numpy(object),
            r["cluster"].to_numpy(object), r["group"].to_numpy(object),
            r["trade_date"].to_numpy().astype("datetime64[D]").astype(np.int64),
            r["decision_ts_ns"].to_numpy(np.int64), r["t_index"].to_numpy(np.int64),
            r["flatten_ts_ns"].to_numpy(np.int64), sigma)
    return ctx.cache["rows"]


# ----------------------------------------------------------------------------- clock ----
def ct_ns(days: np.ndarray, minutes: np.ndarray | int, day_offset: int = 0) -> np.ndarray:
    """UTC ns of hh:mm CT (``minutes`` after midnight) on calendar date day + day_offset; NAT on a
    clock time that does not exist or is ambiguous on that date (a DST change)."""
    days = np.asarray(days, dtype=np.int64)
    mins = np.broadcast_to(np.asarray(minutes, dtype=np.int64), days.shape)
    if days.size == 0:
        return np.zeros(0, dtype=np.int64)
    naive = (days + day_offset) * NS_DAY + mins * NS_MIN
    idx = pd.DatetimeIndex(naive.astype("datetime64[ns]"))
    local = idx.tz_localize(CT_ZONE, ambiguous="NaT", nonexistent="NaT")
    return local.asi8.astype(np.int64)


def minute_of(at: str | Any) -> int:
    """CT clock minute of an "HH:MM" text or a datetime.time."""
    if isinstance(at, str):
        hh, mm = at.split(":")[:2]
        return int(hh) * 60 + int(mm)
    return at.hour * 60 + at.minute


def epoch_day(day: date | str) -> int:
    if isinstance(day, str):
        day = date.fromisoformat(day[:10])
    if isinstance(day, datetime):
        day = day.date()
    return (day - _EPOCH).days


def as_date(days: int) -> date:
    return date.fromordinal(_EPOCH.toordinal() + int(days))


def day_set(days: Any) -> np.ndarray:
    """A literal date table (ISO strings or dates) as sorted unique epoch days."""
    return np.unique(np.array([epoch_day(d) for d in days], dtype=np.int64))


def in_days(days: np.ndarray, table: np.ndarray) -> np.ndarray:
    return np.isin(np.asarray(days, dtype=np.int64), table)


def weekday(days: np.ndarray) -> np.ndarray:
    """Monday = 0 of epoch days (1970-01-01 was a Thursday)."""
    return (np.asarray(days, dtype=np.int64) + 3) % 7


# ------------------------------------------------------------------------------ units ----
@lru_cache(maxsize=64)
def per_unit(vehicle: str) -> float:
    """Vehicle ticks per vendor price unit of the vehicle's price path (interfaces section 1)."""
    from rules.products import product

    if vehicle not in UNIVERSE:
        raise SignalInputMissing(f"{vehicle} is not a vehicle of constants.UNIVERSE")
    path = UNIVERSE[vehicle][1]
    p_path, p_veh = product(path), product(vehicle)
    if p_path.exposure != p_veh.exposure:
        raise SignalInputMissing(f"{path} and {vehicle} quote different exposures")
    return 1.0 / (p_path.vendor_price_factor * float(p_veh.tick_size))


@lru_cache(maxsize=64)
def own_per_unit(root: str) -> float:
    """Ticks of ``root`` itself per vendor unit (a signal leg read in its own ticks)."""
    from rules.products import product

    p = product(root)
    return 1.0 / (p.vendor_price_factor * float(p.tick_size))


def row_per_unit(view: RowsView) -> np.ndarray:
    out = np.empty(view.n)
    for r in pd.unique(view.root):
        out[view.root == r] = per_unit(str(r))
    return out


def path_of(vehicle: str) -> str:
    return UNIVERSE[vehicle][1]


# --------------------------------------------------------------------------- releases ----
def release_times(releases: Any, vehicle: str) -> np.ndarray:
    """Sorted release instants (UTC ns) of a vehicle: D8's list as the engine applies it to the
    vehicle's fills (ReleaseCalendar.by_root or EventCalendar.releases; vehicle key first)."""
    table = getattr(releases, "by_root", None)
    if table is None:
        table = getattr(releases, "releases", None)
    if table is None:
        raise SignalInputMissing("the release calendar has neither by_root nor releases")
    for key in (vehicle, path_of(vehicle) if vehicle in UNIVERSE else vehicle):
        if key in table:
            return np.sort(np.asarray(table[key], dtype=np.int64))
    raise SignalInputMissing(f"the release calendar lists no release for {vehicle}")


def cpi_times(releases: Any) -> np.ndarray:
    raw = getattr(releases, "cpi", ())
    if isinstance(raw, np.ndarray):
        return np.sort(raw.astype(np.int64))
    out = [int(pd.Timestamp(x).value) for x in raw]
    return np.sort(np.array(out, dtype=np.int64))


def release_coverage(releases: Any) -> tuple[int, int] | None:
    """(first, last) epoch days the calendar covers, None when it does not say (synthetic)."""
    first, last = getattr(releases, "first", None), getattr(releases, "last", None)
    if first is None or last is None:
        return None
    return epoch_day(first), epoch_day(last)


# ---------------------------------------------------------------------------- results ----
def empty(view: RowsView) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """(value, applicable, avail) to fill: NaN, False, -1."""
    return np.full(view.n, np.nan), np.zeros(view.n, dtype=bool), np.full(view.n, -1, np.int64)


def result(view: RowsView, value: np.ndarray, app: np.ndarray, avail: np.ndarray) -> pd.DataFrame:
    """The signal frame: 0 and avail = t where not applicable; avail -1 where missing."""
    app = np.asarray(app, dtype=bool)
    value = np.asarray(value, dtype=np.float64)
    finite = np.isfinite(value)
    v = np.where(app, value, 0.0)
    av = np.where(app, np.where(finite, avail, -1), view.t).astype(np.int64)
    return pd.DataFrame({"value": v, "applicable": app.astype(np.float64), "avail_ts_ns": av},
                        index=view.index)


def leg_blackout_mask(spec: SignalSpec, ctx: SignalContext) -> np.ndarray:
    """Rows on which the V2.2 leg rule blanks ``spec`` (module docstring): the row's trade date is
    a roll-blackout date of a root the signal reads there other than the row's own price path."""
    view = rows_of(ctx)
    mask = np.zeros(view.n, dtype=bool)
    if spec.own_path_only or not ctx.blackout:
        return mask
    for root in spec.roots_read:
        days = ctx.blackout.get(root)
        if not days:
            continue
        mask |= (view.path != root) & in_days(view.day, day_set(days))
    return mask


def apply_leg_blackout(spec: SignalSpec, frame: pd.DataFrame, ctx: SignalContext
                       ) -> tuple[pd.DataFrame, int]:
    """``frame`` (a signal frame of ``spec``) with the V2.2 leg rule applied: a new frame with
    value 0, applicable 0 and avail = t on the blanked rows; and the number of blanked rows that
    were applicable."""
    mask = leg_blackout_mask(spec, ctx)
    if not mask.any():
        return frame, 0
    app = frame["applicable"].to_numpy(np.float64)
    n_hit = int(np.count_nonzero(mask & (app > 0)))
    t = rows_of(ctx).t
    out = pd.DataFrame({
        "value": np.where(mask, 0.0, frame["value"].to_numpy(np.float64)),
        "applicable": np.where(mask, 0.0, app),
        "avail_ts_ns": np.where(mask, t, frame["avail_ts_ns"].to_numpy(np.int64)).astype(np.int64),
    }, index=frame.index)
    return out, n_hit


def apply_event(view: RowsView, rows: np.ndarray, ev_value: np.ndarray, ev_avail: np.ndarray,
                ev_on: np.ndarray, out: tuple[np.ndarray, np.ndarray, np.ndarray]) -> None:
    """Rows ``rows`` with a same-day event (``ev_on``) whose value is known by t (nominal
    ``ev_avail`` <= t) become applicable with ``ev_value`` (NaN = data missing); an event later
    that day, or no event, stays not applicable (V2.3). Arrays are aligned to ``rows``."""
    value, app, avail = out
    t = view.t[rows]
    known = ev_on & (ev_avail >= 0) & (ev_avail <= t)
    value[rows[known]] = ev_value[known]
    avail[rows[known]] = ev_avail[known]
    app[rows[known]] = True


def lookup_days(keys: np.ndarray, table_days: np.ndarray) -> np.ndarray:
    """Position of each key in a sorted day table, -1 when absent."""
    keys = np.asarray(keys, dtype=np.int64)
    pos = np.searchsorted(table_days, keys)
    ok = pos < len(table_days)
    ok[ok] = table_days[pos[ok]] == keys[ok]
    return np.where(ok, pos, -1)


def sort_unique(days: np.ndarray) -> np.ndarray:
    return np.unique(np.asarray(days, dtype=np.int64))


def pick(arr: np.ndarray, idx: np.ndarray, fill: float = np.nan) -> np.ndarray:
    """arr[idx] with ``fill`` where idx < 0."""
    idx = np.asarray(idx, dtype=np.int64)
    out = np.full(len(idx), fill, dtype=np.float64)
    ok = idx >= 0
    out[ok] = arr[idx[ok]]
    return out


def same_iid(bars: BarArrays, *idxs: np.ndarray) -> np.ndarray:
    """True where every index is present and all carry one instrument_id."""
    ok = np.ones(len(idxs[0]), dtype=bool)
    for i in idxs:
        ok &= i >= 0
    if not ok.any():
        return ok
    ref = bars.iid[np.where(ok, idxs[0], 0)]
    for i in idxs[1:]:
        ok &= bars.iid[np.where(ok, i, 0)] == ref
    return ok


__all__ = [
    "NAT", "NS_DAY", "NS_MIN", "BarArrays", "CausalityError", "RowsView", "SignalContext",
    "SignalInputMissing", "SignalSpec", "apply_event", "as_date", "bar_arrays", "bars_of",
    "cpi_times", "ct_ns", "day_set", "empty", "epoch_day", "in_days", "lookup_days", "minute_of",
    "segment_index", "window_sums",
    "own_per_unit", "path_of", "per_unit", "pick", "release_coverage", "release_times", "result",
    "row_per_unit", "rows_of", "same_iid", "sort_unique", "trade_date_days", "weekday",
]
