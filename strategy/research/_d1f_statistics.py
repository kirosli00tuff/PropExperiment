"""Stage D.1f Task 4: the Family F and G statistics on a supplied date set, with each event's
forward clock interval (reports/stage_d1f_confirmation_list.md 2.1 A2, 2.2, 3.2(ii), 5.4).

WHAT IT DOES. ``compute_statistics(bars, candidate_dates, splice_trade_dates)`` resolves the
date set as the hashed ``f_data_native._stylized_facts.resolve_eda_dates`` does on the EDA
path, then calls the two hashed modules' builders (``build_f1`` .. ``build_f6``; per timeframe
``build_days``/``build_statistics``) exactly as ``strategy.research._d1e_event_series`` calls
them with the 139 EDA dates. Neither hashed module is edited or monkey-patched. No bars are
loaded here: the caller passes them from a ``data.research_bars`` loader (research or
confirmation; the module has no preference).

DATE SET AND DEGRADED DAYS (list 1.3, N-3), as on the EDA path: a candidate date is dropped if
it is in the roll blackout (``canonical_engine_config(splices).roll_blackout``) or if ANY of
its bars carries ``vendor_degraded_day``, logged as ``roll_blackout``, ``vendor_degraded_day``
or both joined by ``+``. The builders never read the flag; they receive exactly the surviving
dates' bars, sorted by (trade_date, ts_event).

THRESHOLDS (R-6). The F2.4, F5.1, F5.2 tercile edges, F5.3's regression, G1/G4's Q80 and
trailing 20-date baselines are recomputed by the hashed code on the supplied dates, pooled;
nothing is frozen at EDA values. ``StatisticsRun.thresholds`` reports them.

EVENT VALUES. e is exactly ``_d1e_event_series._event_values`` on the hashed ``DayObs``:
sign(sign_pred) x ticks (correlation statistics), the signed forward move (F4.1/F4.2, G),
round_ticks with no control subtraction (F4.4).

FORWARD CLOCK INTERVALS. The hashed objects hold values, not times, so each builder's event
selection is replicated here with bar timestamps attached, and checked against the hashed
arrays on every key (pred, targ, sign_pred, ticks; ticks; round_ticks; x), day by day and in
order, and against the bars' own prices; any mismatch raises. An interval is two points,
each (bar ts_event in ns, "open" | "close"), the prices the forward move runs from and to (a
close is observed at ts_event + 1 minute). Per type (session minute m: 0 = 17:00 CT, 930 =
08:30 CT):
- F1.1 h = 1 (RTH, ETH): the target is the 1-minute step into m+1: close(m) -> close(m+1).
- F1.1 h in {5, 15, 30, 60}, F2.4 (h = 15), F3.2, F5.1, F5.2, F5.3 (30-min buckets): the
  target is the next clock window k+1 = [lo, lo+h), lo = base + (k+1)h, whose ticks are
  close(lo+h-1) - close(lo-1) (``WindowStat.price_change``): close(lo-1) -> close(lo+h-1).
- F3.3 (both): the target is bucket 13, 14:30-15:00 CT: close(14:29) -> close(14:59).
- F6.1: the target is the first 60-min RTH window: close(08:29) -> close(09:29).
- F4.1, F4.2: a crossing at minute m, e = direction x (close(m+15) - close(m)):
  close(m) -> close(m+15).
- F4.4: a crossing of level L inside bar i (any session), e = direction x (close(i+15) - L).
  L is touched inside bar i, so the start is anchored at bar i's open, as screening/drift.py
  anchors an inside-bar fill: open(i) -> close(i+15), bar i+15 being the 15th row after i in
  the hashed code's gap-free test. The first bar of a trade date carries
  gap_before_minutes = 0, so, as the hashed module's own implementation choices say, this
  window can run past the daily halt into the NEXT statistic date: such events have
  ``end_trade_dates`` later than ``trade_dates`` (``crosses_trade_date``), and
  ``forward_mean_moves_ticks`` refuses them (a single-day drift path cannot price them).
- G1, G2, G4, G5 at tf minutes: the next coarse bar's move, close of slot j+1 minus close of
  slot j, a coarse close being the close of the last 1-minute bar opening in the slot:
  close(last bar of slot j) -> close(last bar of slot j+1).
- G3: from the first breakout slot j to P_end, the close of the last 1-minute RTH bar opening
  before the RTH segment end: close(last bar of slot j) -> close(P_end bar).
The drift charge of list 3.2(ii) is s x ``forward_mean_moves_ticks(events, path)``.
"""

from __future__ import annotations

import math
from collections import deque
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType

import numpy as np
import pandas as pd

import strategy.research.f_data_native._stylized_facts as fsf
import strategy.research.g_timeframe._stylized_facts as gsf
import strategy.research.g_timeframe.resample as rsm
from screening.drift import DriftPath
from screening.runner import canonical_engine_config
from strategy.research._d1e_event_series import _event_values

TICK, DAY_SIZE, EMPTY = fsf.TICK, fsf.DAY_SIZE, fsf.EMPTY
BUCKET_H, N_BUCKETS = fsf.BUCKET_H, fsf.N_BUCKETS
RTH_BASE, RTH_LEN, ETH_BASE, ETH_LEN = fsf.RTH_BASE, fsf.RTH_LEN, fsf.ETH_BASE, fsf.ETH_LEN
TOL = 1e-9
NS_PER_MINUTE = 60_000_000_000
OPEN, CLOSE = "open", "close"
N_DIRECTIONAL = 64  # 36 Family F + 28 Family G (list 2.1 A2: 21 Tier A, 2.2: 43 Tier B)
N_DESCRIPTIVE = 21  # the non-directional F facts (F1.2, F2.1, F2.2, F2.3, F4.3)
_SEGMENT_SPECS = (("RTH", RTH_BASE, RTH_LEN), ("ETH", ETH_BASE, ETH_LEN))


def _clock(ts: np.ndarray, prices: tuple[str, ...]) -> np.ndarray:
    return ts + np.where(np.array(prices, dtype=object) == CLOSE, NS_PER_MINUTE, 0)


@dataclass(frozen=True)
class StatisticEvents:
    """One directional statistic on the supplied dates: per-event e, date and interval."""

    stat_id: str
    source: str  # "F" (stage_d1b module) or "G" (stage_d1d module)
    family: str
    description: str
    keys: tuple[str, ...]
    values: np.ndarray  # e per event, ticks
    trade_dates: tuple[date, ...]  # per event: the date the event is counted on
    start_bar_ts_ns: np.ndarray  # int64 per event
    start_price: tuple[str, ...]  # "open" | "close" per event
    end_bar_ts_ns: np.ndarray
    end_price: tuple[str, ...]
    end_trade_dates: tuple[date, ...]  # trade date of the end bar (later only for F4.4)
    estimate: float | None
    n: int
    implied_edge_ticks: float | None
    extra: Mapping[str, float | int | None]  # F4.4: control_mean_ticks, n_control

    @property
    def start_clock_ns(self) -> np.ndarray:
        """The instant the start price is observed (a close is seen one minute after open)."""
        return _clock(self.start_bar_ts_ns, self.start_price)

    @property
    def end_clock_ns(self) -> np.ndarray:
        return _clock(self.end_bar_ts_ns, self.end_price)

    @property
    def crosses_trade_date(self) -> np.ndarray:
        pairs = zip(self.trade_dates, self.end_trade_dates, strict=True)
        return np.array([a != b for a, b in pairs], dtype=bool)

    def daily_sums(self, dates: Sequence[date]) -> np.ndarray:
        """Sum of e per date of ``dates`` (0 where none); raises on an event outside them."""
        index = {d: i for i, d in enumerate(dates)}
        out = np.zeros(len(dates))
        for d, v in zip(self.trade_dates, self.values, strict=True):
            out[index[d]] += v
        return out


@dataclass(frozen=True)
class StatisticsRun:
    dates: tuple[date, ...]  # the post-exclusion statistic date set
    excluded: tuple[Mapping[str, str], ...]  # {"date", "reason"} as resolve_eda_dates logs
    directional: Mapping[str, StatisticEvents]  # the 64
    descriptive: Mapping[str, Mapping[str, object]]  # the 21 non-directional F facts
    g0: tuple[Mapping[str, object], ...]  # G0 per timeframe and segment
    f3_1_table: tuple[Mapping[str, object], ...]
    thresholds: Mapping[str, tuple[float, ...]]


def resolve_statistic_dates(
    bars: pd.DataFrame, candidate_dates: Iterable[date], roll_blackout: frozenset[date]
) -> tuple[tuple[date, ...], tuple[dict[str, str], ...]]:
    """``resolve_eda_dates``'s exclusion rule on any candidate set: drop the roll blackout and
    every date with ANY vendor-degraded bar; log the reasons in the same form."""
    days = pd.to_datetime(bars["trade_date"].astype(str)).dt.date
    candidates = sorted(set(candidate_dates))
    missing = sorted(set(candidates) - set(days))
    if missing:
        raise ValueError(f"no bars for {len(missing)} candidate dates, e.g. {missing[0]}")
    vdd = set(days[bars["vendor_degraded_day"].to_numpy(dtype=bool)])
    reasons = {d: "+".join(r for r, hit in (("roll_blackout", d in roll_blackout),
                                            ("vendor_degraded_day", d in vdd)) if hit)
               for d in candidates}
    return (tuple(d for d in candidates if not reasons[d]),
            tuple({"date": d.isoformat(), "reason": reasons[d]} for d in candidates
                  if reasons[d]))


def select_statistic_bars(bars: pd.DataFrame, dates: Sequence[date]) -> pd.DataFrame:
    """The surviving dates' bars, sorted and indexed as ``resolve_eda_dates`` returns them."""
    wanted = {d.isoformat() for d in dates}
    return (bars[bars["trade_date"].isin(wanted)]
            .sort_values(["trade_date", "ts_event"]).reset_index(drop=True))


@dataclass(frozen=True)
class _Event:
    values: tuple[float, ...]  # the compared keys' values, in _compare_keys order
    start: tuple[int, str]
    end: tuple[int, str]


_Replica = dict[date, list[_Event]]


def _compare_keys(keys: tuple[str, ...]) -> tuple[str, ...]:
    return ("round_ticks",) if keys == ("round_ticks", "control_ticks") else keys


def _pt(ts: np.ndarray, m: int, price: str) -> tuple[int, str]:
    t = int(ts[m])
    if t < 0:
        raise AssertionError(f"no bar at slot/minute {m} for a forward-interval point")
    return t, price


def _window_iv(ts: np.ndarray, base: int, h: int, k: int) -> tuple[tuple[int, str], ...]:
    lo = base + k * h
    return _pt(ts, lo - 1, CLOSE), _pt(ts, lo + h - 1, CLOSE)


def _pair_event(w: fsf.WindowStat, nxt: fsf.WindowStat, ts: np.ndarray, base: int, h: int,
                k_next: int) -> _Event:
    return _Event((w.ret, nxt.ret, w.ret, nxt.price_change / TICK),
                  *_window_iv(ts, base, h, k_next))


def _tercile_split(records: list[tuple[date, _Event, float]], ids: tuple[str, str],
                   name: str, thresholds: dict, dates: Sequence[date]) -> dict[str, _Replica]:
    """The hashed tercile rule: edges at np.percentile(.., [100/3, 200/3]) over all records
    (NaN below 3), bottom = value <= lo, top = value >= hi, each day's order kept."""
    values = np.array([r[2] for r in records])
    lo, hi = (np.percentile(values, [100 / 3, 200 / 3]) if len(values) >= 3
              else (math.nan, math.nan))
    thresholds[name] = (float(lo), float(hi))
    out: dict[str, _Replica] = {ids[0]: {d: [] for d in dates}, ids[1]: {d: [] for d in dates}}
    for d, ev, v in records:
        for sid, keep in ((ids[0], v <= lo), (ids[1], v >= hi)):
            if keep:
                out[sid][d].append(ev)
    return out


@dataclass(frozen=True)
class _FCtx:
    dates: tuple[date, ...]
    bars: pd.DataFrame  # engineered
    day_arrays: dict[date, dict[str, np.ndarray]]
    ts: dict[date, np.ndarray]  # session minute -> bar ts_event (ns), -1 where absent
    wcache: dict

    def window(self, base: int, h: int, length: int) -> dict[date, dict[int, fsf.WindowStat]]:
        return fsf.get_window_table(self.wcache, self.day_arrays, list(self.dates), base, h,
                                    length)


def _day_ts(f_bars: pd.DataFrame) -> dict[date, np.ndarray]:
    out = {}
    for d, g in f_bars.groupby("trade_date_obj", sort=True):
        arr = np.full(DAY_SIZE, -1, dtype=np.int64)
        arr[g["session_minute"].to_numpy()] = g["ts_event"].to_numpy(np.int64)
        out[d] = arr
    return out


def _rep_f1(c: _FCtx) -> dict[str, _Replica]:
    out: dict[str, _Replica] = {}
    for seg, base, length in _SEGMENT_SPECS:
        for h in (1, 5, 15, 30, 60):
            rep: _Replica = {}
            for d in c.dates:
                da, ts = c.day_arrays[d], c.ts[d]
                if h == 1:
                    sl = slice(base, base + length)
                    v, lr, cl = da["valid"][sl], da["logret1"][sl], da["close"][sl]
                    rep[d] = [
                        _Event((lr[i], lr[i + 1], lr[i], (cl[i + 1] - cl[i]) / TICK),
                               _pt(ts, base + i, CLOSE), _pt(ts, base + i + 1, CLOSE))
                        for i in np.flatnonzero(v[:-1] & v[1:])]
                else:
                    win = c.window(base, h, length)[d]
                    rep[d] = [_pair_event(w, win[k + 1], ts, base, h, k + 1)
                              for k, w in win.items() if (k + 1) in win]
            out[f"F1_1_h{h}_{seg}"] = rep
    return out


def _rep_f2_4(c: _FCtx, thresholds: dict) -> dict[str, _Replica]:
    win_by_date = c.window(RTH_BASE, 15, RTH_LEN)
    records: list[tuple[date, _Event, float]] = []
    for d in c.dates:
        da, win = c.day_arrays[d], win_by_date[d]
        for k, w in win.items():
            nxt = win.get(k + 1)
            trail_start = RTH_BASE + k * 15 - 60
            if (nxt is None or trail_start < 0
                    or not da["valid"][trail_start:trail_start + 60].all()):
                continue
            lr = da["logret1"][trail_start:trail_start + 60]
            records.append((d, _pair_event(w, nxt, c.ts[d], RTH_BASE, 15, k + 1),
                            float(np.sqrt(np.sum(lr * lr)))))
    return _tercile_split(records, ("F2_4_15min_vol_tercile_bottom",
                                    "F2_4_15min_vol_tercile_top"),
                          "F2_4_trailvol_tercile_edges", thresholds, c.dates)


def _rep_f3(c: _FCtx) -> dict[str, _Replica]:
    bw = c.window(RTH_BASE, BUCKET_H, RTH_LEN)
    out: dict[str, _Replica] = {}
    for k in range(N_BUCKETS - 1):
        out[f"F3_2_bucket{k + 1:02d}_bucket{k + 2:02d}"] = {
            d: ([] if bw[d].get(k) is None or bw[d].get(k + 1) is None else
                [_pair_event(bw[d][k], bw[d][k + 1], c.ts[d], RTH_BASE, BUCKET_H, k + 1)])
            for d in c.dates}
    last, rep_a, rep_b = N_BUCKETS - 1, {}, {}
    for d in c.dates:
        f9, b1, b13 = fsf._first_bar_to_0900(c.day_arrays[d]), bw[d].get(0), bw[d].get(last)
        rep_a[d] = ([] if f9 is None or b13 is None
                    else [_pair_event(f9, b13, c.ts[d], RTH_BASE, BUCKET_H, last)])
        rep_b[d] = ([] if b1 is None or b13 is None
                    else [_pair_event(b1, b13, c.ts[d], RTH_BASE, BUCKET_H, last)])
    out["F3_3_overnight_to_close_momentum"] = rep_a
    out["F3_3_opening_30min_to_close_momentum"] = rep_b
    return out


def _scan_crossings(da: dict[str, np.ndarray], ts: np.ndarray, minutes: range,
                    reference: float, refractory: int) -> list[_Event]:
    """``scan_reference_crossings`` with the crossing minute kept."""
    valid, close = da["valid"], da["close"]
    events: list[_Event] = []
    next_eligible = -1
    for m in minutes:
        if m < next_eligible or not valid[m]:
            continue
        prev_c, cur_c = close[m - 1], close[m]
        if not (np.isfinite(prev_c) and np.isfinite(cur_c)):
            continue
        if (prev_c - reference) * (cur_c - reference) >= 0:
            continue
        direction = 1.0 if cur_c > reference else -1.0
        next_eligible = m + refractory
        fwd = fsf.forward_clean_close(da, m, 15)
        if fwd is None:
            continue
        events.append(_Event((direction * (fwd - cur_c) / TICK,), _pt(ts, m, CLOSE),
                             _pt(ts, m + 15, CLOSE)))
    return events


def _rep_f4_crossings(c: _FCtx) -> dict[str, _Replica]:
    rep1: _Replica = {}
    for d in c.dates:
        ref = c.day_arrays[d]["open"][RTH_BASE]
        rep1[d] = (_scan_crossings(c.day_arrays[d], c.ts[d], range(960, 1290), float(ref), 15)
                   if np.isfinite(ref) else [])
    rep2: _Replica = {d: [] for d in c.dates}
    for i, d in enumerate(c.dates[1:], start=1):
        da_prior, da = c.day_arrays[c.dates[i - 1]], c.day_arrays[d]
        prior_close = da_prior["close"][RTH_BASE + RTH_LEN - 1]
        prior_instr = da_prior["instr"][RTH_BASE + RTH_LEN - 1]
        cur_instr = da["instr"][RTH_BASE]
        if (np.isfinite(prior_close) and np.isfinite(prior_instr) and np.isfinite(cur_instr)
                and prior_instr == cur_instr):
            rep2[d] = _scan_crossings(da, c.ts[d], range(930, 1290), float(prior_close), 15)
    return {"F4_1_rth_open_crossing": rep1, "F4_2_prior_rth_close_crossing": rep2}


def _rep_f4_4(c: _FCtx) -> dict[str, _Replica]:
    """``build_f4``'s round-level scan (``scan_round_levels``, then ``collect``) with rows."""
    ts, tdo = c.bars["ts_event"].to_numpy(), c.bars["trade_date_obj"].to_numpy()
    close_, high_, low_ = (c.bars[k].to_numpy(dtype=float) for k in ("close", "high", "low"))
    gap0 = (c.bars["gap_before_minutes"] == 0).to_numpy()
    level_lo = math.floor(float(np.nanmin(low_)) / 50.0) * 50.0 - 50.0
    level_hi = math.ceil(float(np.nanmax(high_)) / 50.0) * 50.0 + 50.0
    levels_50 = [level_lo + 50.0 * i for i in range(int(round((level_hi - level_lo) / 50.0)) + 1)]
    levels_100 = [lv for lv in levels_50 if lv % 100.0 == 0.0]
    prev_close = np.full_like(close_, np.nan)
    prev_close[1:] = close_[:-1]
    refractory_ns = 30 * 60 * 1_000_000_000

    def scan(lv: float) -> list[tuple[date, _Event]]:
        cross_up = (prev_close < lv) & (high_ >= lv)
        cross_down = (prev_close > lv) & (low_ <= lv)
        events, next_eligible = [], -1
        for i in np.flatnonzero((cross_up | cross_down) & gap0):
            if int(ts[i]) < next_eligible:
                continue
            next_eligible = int(ts[i]) + refractory_ns
            fwd = fsf.forward_clean_flat(gap0, close_, int(i), 15)
            if fwd is None:
                continue
            direction = 1.0 if cross_up[i] else -1.0
            events.append((tdo[i], _Event((direction * (fwd - lv) / TICK,),
                                          (int(ts[i]), OPEN), (int(ts[i + 15]), CLOSE))))
        return events

    by_level = {lv: scan(lv) for lv in levels_50}
    out: dict[str, _Replica] = {}
    for suffix, levels in (("50", levels_50), ("100", levels_100)):
        rep: _Replica = {d: [] for d in c.dates}
        for lv in levels:
            for d, ev in by_level[lv]:
                if d in rep:
                    rep[d].append(ev)
        out[f"F4_4_round_number_multiples_of_{suffix}"] = rep
    return out


def _rep_f5_1(c: _FCtx, bw: dict, thresholds: dict) -> dict[str, _Replica]:
    history = {k: deque(maxlen=20) for k in range(N_BUCKETS)}
    records: list[tuple[date, _Event, float]] = []
    for d in c.dates:
        win = bw[d]
        for k in range(N_BUCKETS - 1):
            w = win.get(k)
            if w is not None and len(history[k]) == 20:
                relvol = w.volume / (sum(history[k]) / 20.0)
                nxt = win.get(k + 1)
                if nxt is not None:
                    records.append((d, _pair_event(w, nxt, c.ts[d], RTH_BASE, BUCKET_H, k + 1),
                                    relvol))
        for k in range(N_BUCKETS):
            if win.get(k) is not None:
                history[k].append(win[k].volume)
    return _tercile_split(records, ("F5_1_relvol_tercile_bottom", "F5_1_relvol_tercile_top"),
                          "F5_1_relvol_tercile_edges", thresholds, c.dates)


def _rep_f5_2(c: _FCtx, bw: dict, thresholds: dict) -> dict[str, _Replica]:
    records: list[tuple[date, _Event, float]] = []
    for d in c.dates:
        for k in range(N_BUCKETS - 1):
            w, nxt = bw[d].get(k), bw[d].get(k + 1)
            if w is None or nxt is None or w.range_ <= 0:
                continue
            records.append((d, _pair_event(w, nxt, c.ts[d], RTH_BASE, BUCKET_H, k + 1),
                            abs(w.price_change) / w.range_))
    return _tercile_split(records, ("F5_2_efficiency_tercile_bottom",
                                    "F5_2_efficiency_tercile_top"),
                          "F5_2_efficiency_tercile_edges", thresholds, c.dates)


def _rep_f5_3(c: _FCtx, bw: dict, thresholds: dict) -> dict[str, _Replica]:
    all_obs = [(d, k, math.log(w.range_), math.log(w.volume), w.ret)
               for d in c.dates for k, w in bw[d].items() if w.range_ > 0 and w.volume > 0]
    xv, yv = np.array([o[3] for o in all_obs]), np.array([o[2] for o in all_obs])
    if len(xv) >= 2 and np.std(xv) > 0:
        b = float(np.cov(xv, yv, ddof=1)[0, 1] / np.var(xv, ddof=1))
        a = float(yv.mean() - b * xv.mean())
    else:
        a = b = 0.0
    thresholds["F5_3_log_range_on_log_volume_intercept_slope"] = (a, b)
    resid = {(o[0], o[1]): o[2] - (a + b * o[3]) for o in all_obs}
    rep: _Replica = {}
    for d in c.dates:
        win, evs = bw[d], []
        for k in range(N_BUCKETS - 1):
            w, nxt = win.get(k), win.get(k + 1)
            if w is None or nxt is None or (d, k) not in resid:
                continue
            pv = resid[(d, k)] * (1.0 if w.ret >= 0 else -1.0)
            evs.append(_Event((pv, nxt.ret, pv, nxt.price_change / TICK),
                              *_window_iv(c.ts[d], RTH_BASE, BUCKET_H, k + 1)))
        rep[d] = evs
    return {"F5_3_range_volume_residual": rep}


def _rep_f6(c: _FCtx) -> dict[str, _Replica]:
    win60 = c.window(RTH_BASE, 60, RTH_LEN)
    rep: _Replica = {}
    for d in c.dates:
        da, eth = c.day_arrays[d], slice(ETH_BASE, ETH_BASE + ETH_LEN)
        has_eth = bool(np.any(~np.isnan(da["high"][eth])))
        eth_high = float(np.nanmax(da["high"][eth])) if has_eth else math.nan
        eth_low = float(np.nanmin(da["low"][eth])) if has_eth else math.nan
        open_0830, target = da["open"][RTH_BASE], win60[d].get(0)
        if (math.isnan(eth_high) or math.isnan(eth_low) or eth_high <= eth_low
                or not np.isfinite(open_0830) or target is None):
            rep[d] = []
            continue
        position = (open_0830 - eth_low) / (eth_high - eth_low)
        rep[d] = [_Event((position, target.ret, position - 0.5, target.price_change / TICK),
                         *_window_iv(c.ts[d], RTH_BASE, 60, 0))]
    return {"F6_1_overnight_range_position": rep}


def _f_replicas(c: _FCtx, thresholds: dict) -> dict[str, _Replica]:
    bw = c.window(RTH_BASE, BUCKET_H, RTH_LEN)
    out: dict[str, _Replica] = {}
    for part in (_rep_f1(c), _rep_f2_4(c, thresholds), _rep_f3(c), _rep_f4_crossings(c),
                 _rep_f4_4(c), _rep_f5_1(c, bw, thresholds), _rep_f5_2(c, bw, thresholds),
                 _rep_f5_3(c, bw, thresholds), _rep_f6(c)):
        out.update(part)
    return out


def _slot_last_ts(g_bars: pd.DataFrame, days: list[gsf.DayData], tf: int
                  ) -> dict[date, dict[str, np.ndarray]]:
    """Per day and segment: ts_event of the last 1-minute bar of each present coarse slot
    (the bar whose close is the coarse close), -1 elsewhere."""
    slotted = rsm._assign_slots(rsm.annotate_session(g_bars), tf)
    last = slotted.groupby(["trade_date", "segment", "slot"], sort=False)["ts_event"].last()
    lookup = {(date.fromisoformat(str(td)), seg, int(k)): int(t)
              for (td, seg, k), t in last.items()}
    out: dict[date, dict[str, np.ndarray]] = {}
    for d in days:
        out[d.obs_date] = {}
        for seg in rsm.SEGMENTS:
            arr = np.full(gsf._NOMINAL_SLOTS[seg] // tf, -1, dtype=np.int64)
            for j in np.flatnonzero(d.seg[seg]["present"]):
                arr[j] = lookup[(d.obs_date, seg, int(j))]
            out[d.obs_date][seg] = arr
    return out


def _p_end_ts(g_bars: pd.DataFrame, dates: Sequence[date]) -> dict[date, int]:
    """ts_event of the bar whose close is ``build_days``'s P_end (-1 where none)."""
    by_date = {d: g for d, g in g_bars.groupby("trade_date_obj", sort=True)}
    out = {}
    for d in dates:
        g = by_date[d]
        own = g[g["session_minute"] >= rsm.MIDNIGHT_SESSION_MINUTE]
        limit = int(own["limit"].iloc[0]) if len(own) else rsm.DEFAULT_LIMIT
        rth_end = min(rsm.RTH_NOMINAL_END, limit) if len(own) else None
        rth = g[g["session_minute"].between(rsm.RTH_START, (rth_end or 0) - 1)]
        out[d] = int(rth["ts_event"].iloc[-1]) if len(rth) else -1
    return out


def _g_iv(lt: np.ndarray, j: int) -> tuple[tuple[int, str], tuple[int, str]]:
    return _pt(lt, j, CLOSE), _pt(lt, j + 1, CLOSE)


def _rep_relative(days: list[gsf.DayData], lts: dict, segment: str, measure_fn: Callable
                  ) -> tuple[_Replica, float]:
    """``_relative_events`` with the slot kept (G1, G4)."""
    signed = np.array([measure_fn(d) for d in days])
    absolute = np.abs(signed)
    rel = np.full_like(signed, np.nan)
    for i in range(gsf.BASELINE_DAYS, len(days)):
        baseline = gsf._trailing_baseline(absolute, i)
        with np.errstate(invalid="ignore", divide="ignore"):
            rel[i] = np.where(baseline > 0, absolute[i] / baseline, np.nan)
    pooled = rel[np.isfinite(rel)]
    q80 = float(np.percentile(pooled, gsf.TOP_QUANTILE * 100)) if len(pooled) else math.nan
    rep: _Replica = {}
    for i in range(gsf.BASELINE_DAYS, len(days)):
        d = days[i]
        close, present = d.seg[segment]["close"], d.seg[segment]["present"]
        evs = []
        for j in np.flatnonzero(np.isfinite(rel[i])):
            if rel[i, j] < q80 or signed[i, j] == 0:
                continue
            fwd = gsf._forward(close, present, j)
            if fwd is not None:
                evs.append(_Event((np.sign(signed[i, j]) * fwd,),
                                  *_g_iv(lts[d.obs_date][segment], int(j))))
        rep[d.obs_date] = evs
    return rep, q80


def _rep_g2(days: list[gsf.DayData], lts: dict, segment: str) -> _Replica:
    rep: _Replica = {}
    for d in days:
        s, lt = d.seg[segment], lts[d.obs_date][segment]
        evs, run_high, run_low = [], -math.inf, math.inf
        for j in np.flatnonzero(s["present"]):
            if run_high > -math.inf:
                close = s["close"][j]
                direction = 1 if close > run_high else (-1 if close < run_low else 0)
                fwd = gsf._forward(s["close"], s["present"], j) if direction else None
                if fwd is not None:
                    evs.append(_Event((direction * fwd,), *_g_iv(lt, int(j))))
            run_high, run_low = max(run_high, s["high"][j]), min(run_low, s["low"][j])
        rep[d.obs_date] = evs
    return rep


def _rep_g3(days: list[gsf.DayData], lts: dict, p_end_ts: dict[date, int]) -> _Replica:
    rep: _Replica = {}
    for d in days:
        s, lt, evs = d.seg["RTH"], lts[d.obs_date]["RTH"], []
        if s["present"][0] and d.p_end is not None and d.rth_end is not None:
            or_high, or_low = s["high"][0], s["low"][0]
            for j in np.flatnonzero(s["present"])[1:]:
                direction = (1 if s["close"][j] > or_high
                             else (-1 if s["close"][j] < or_low else 0))
                if not direction:
                    continue
                if s["end"][j] < d.rth_end:
                    evs.append(_Event((direction * (d.p_end - s["close"][j]) / TICK,),
                                      _pt(lt, int(j), CLOSE), (p_end_ts[d.obs_date], CLOSE)))
                break
        rep[d.obs_date] = evs
    return rep


def _rep_g5(days: list[gsf.DayData], lts: dict) -> _Replica:
    rep: _Replica = {}
    for d in days:
        s, lt, evs = d.seg["RTH"], lts[d.obs_date]["RTH"], []
        if d.eth_high is not None:
            for direction, hit in ((1, s["close"] > d.eth_high), (-1, s["close"] < d.eth_low)):
                firsts = np.flatnonzero(s["present"] & hit)
                if len(firsts):
                    fwd = gsf._forward(s["close"], s["present"], int(firsts[0]))
                    if fwd is not None:
                        evs.append(_Event((direction * fwd,), *_g_iv(lt, int(firsts[0]))))
        rep[d.obs_date] = evs
    return rep


def _g_replicas(days: list[gsf.DayData], lts: dict, p_end_ts: dict[date, int], tf: int,
                thresholds: dict) -> dict[str, _Replica]:
    out: dict[str, _Replica] = {}
    for seg in rsm.SEGMENTS:
        out[f"G1.{seg}.{tf}"], q80 = _rep_relative(days, lts, seg, gsf.g1_body(seg))
        thresholds[f"G1.{seg}.{tf}_q80"] = (q80,)
        out[f"G2.{seg}.{tf}"] = _rep_g2(days, lts, seg)
    out[f"G3.RTH.{tf}"] = _rep_g3(days, lts, p_end_ts)
    out[f"G4.RTH.{tf}"], q80 = _rep_relative(days, lts, "RTH", gsf.g4_vwap_deviation)
    thresholds[f"G4.RTH.{tf}_q80"] = (q80,)
    out[f"G5.RTH.{tf}"] = _rep_g5(days, lts)
    return out


class _PriceIndex:
    """Bar prices and trade dates by ts_event, for the interval checks."""

    def __init__(self, bars: pd.DataFrame) -> None:
        self.ts = bars["ts_event"].to_numpy(np.int64)
        if len(self.ts) and not np.all(np.diff(self.ts) > 0):
            raise ValueError("statistic bars must be strictly increasing in ts_event")
        self.open, self.close = bars["open"].to_numpy(float), bars["close"].to_numpy(float)
        self.day = pd.to_datetime(bars["trade_date"].astype(str)).dt.date.to_numpy()

    def rows(self, ts: np.ndarray) -> np.ndarray:
        idx = np.searchsorted(self.ts, ts)
        ok = (idx < len(self.ts)) & (self.ts[np.minimum(idx, len(self.ts) - 1)] == ts)
        if not ok.all():
            raise AssertionError("a forward-interval point names a bar that does not exist")
        return idx

    def prices(self, ts: np.ndarray, which: Sequence[str]) -> np.ndarray:
        idx = self.rows(ts)
        return np.where(np.array(which, dtype=object) == OPEN, self.open[idx], self.close[idx])


def _same(got: np.ndarray, want: np.ndarray) -> bool:
    return got.shape == want.shape and bool(
        np.allclose(got, want, rtol=0.0, atol=TOL, equal_nan=True))


def _align(stat: fsf.TestedStat, replica: _Replica) -> list[tuple[date, _Event]]:
    """Check the replica against the hashed DayObs arrays, key by key and day by day; return
    the per-event (date, replica event) in the hashed order."""
    keys = _compare_keys(stat.keys)
    out: list[tuple[date, _Event]] = []
    for day in stat.days:
        evs = replica.get(day.obs_date, [])
        for ki, key in enumerate(keys):
            got = np.asarray(day.data.get(key, EMPTY), dtype=float)
            if not _same(got, np.array([ev.values[ki] for ev in evs], dtype=float)):
                raise AssertionError(f"{stat.id}: interval replica disagrees with the hashed "
                                     f"'{key}' array on {day.obs_date}")
        out += [(day.obs_date, ev) for ev in evs]
    seen = {day.obs_date for day in stat.days}
    if stray := [d for d, evs in replica.items() if evs and d not in seen]:
        raise AssertionError(f"{stat.id}: replica events on dates the hashed stat lacks: {stray}")
    return out


def check_intervals(ev: StatisticEvents, prices: _PriceIndex) -> None:
    """Each interval starts and ends on its event's trade date (F4.4 may end on a later
    one), runs forward, and (not F4.4, which starts at L) moves |e| ticks unless e = 0."""
    if not len(ev.values):
        return
    event_days = np.array(ev.trade_dates, dtype=object)
    end_days = np.array(ev.end_trade_dates, dtype=object)
    if not (np.array_equal(prices.day[prices.rows(ev.start_bar_ts_ns)], event_days)
            and np.array_equal(prices.day[prices.rows(ev.end_bar_ts_ns)], end_days)):
        raise AssertionError(f"{ev.stat_id}: an interval point is off its recorded date")
    if ev.family != "F4.4" and ev.crosses_trade_date.any():
        raise AssertionError(f"{ev.stat_id}: a forward interval leaves its trade date")
    if not (np.all(end_days >= event_days) and np.all(ev.end_clock_ns > ev.start_clock_ns)):
        raise AssertionError(f"{ev.stat_id}: a forward interval does not run forward")
    if ev.family == "F4.4":
        return
    move = (prices.prices(ev.end_bar_ts_ns, ev.end_price)
            - prices.prices(ev.start_bar_ts_ns, ev.start_price)) / TICK
    if not ((np.abs(np.abs(ev.values) - np.abs(move)) <= TOL) | (ev.values == 0)).all():
        raise AssertionError(f"{ev.stat_id}: forward interval price move != |e|")


def _summary(stat: fsf.TestedStat) -> tuple[float | None, int, float | None, dict]:
    """estimate, n, implied edge and extras exactly as ``compute_result`` computes them."""
    pool = fsf.pool_days(stat.days, stat.keys)
    estimate = fsf._safe_float(stat.estimate_fn(pool))
    if stat.edge_equals_estimate:
        edge = estimate
    elif stat.directional and stat.edge_fn is not None:
        edge = fsf._safe_float(stat.edge_fn(pool))
    else:
        edge = None
    return estimate, int(stat.n_fn(pool)), edge, stat.extra_fn(pool) if stat.extra_fn else {}


def _events(stat: fsf.TestedStat, source: str, replica: _Replica, prices: _PriceIndex
            ) -> StatisticEvents:
    aligned = _align(stat, replica)
    chunks = [np.asarray(_event_values(d, stat.keys), dtype=float) for d in stat.days]
    values = np.concatenate(chunks) if chunks else EMPTY
    if len(values) != len(aligned):
        raise AssertionError(f"{stat.id}: {len(values)} values vs {len(aligned)} intervals")
    end_ts = np.array([ev.end[0] for _, ev in aligned], dtype=np.int64)
    estimate, n, edge, extra = _summary(stat)
    out = StatisticEvents(
        stat_id=stat.id, source=source, family=stat.family, description=stat.description,
        keys=stat.keys, values=values, trade_dates=tuple(d for d, _ in aligned),
        start_bar_ts_ns=np.array([ev.start[0] for _, ev in aligned], dtype=np.int64),
        start_price=tuple(ev.start[1] for _, ev in aligned), end_bar_ts_ns=end_ts,
        end_price=tuple(ev.end[1] for _, ev in aligned),
        end_trade_dates=tuple(prices.day[prices.rows(end_ts)]) if len(end_ts) else (),
        estimate=estimate, n=n, implied_edge_ticks=edge, extra=MappingProxyType(dict(extra)))
    check_intervals(out, prices)
    return out


def _family_f(bars: pd.DataFrame, dates: tuple[date, ...], thresholds: dict
              ) -> tuple[list[fsf.TestedStat], dict[str, _Replica], list[dict]]:
    """``_d1e_event_series.collect_f_stats``'s calls, keeping F3.1's table and the cache."""
    f_bars = fsf.engineer_bars(bars)
    day_arrays = fsf.build_all_day_arrays(f_bars)
    wcache: dict = {}
    eda = list(dates)
    stats = fsf.build_f1(day_arrays, eda, wcache) + fsf.build_f2(day_arrays, eda, wcache)
    f3_stats, f3_1_table = fsf.build_f3(day_arrays, eda, wcache)
    stats += f3_stats + fsf.build_f4(f_bars, day_arrays, eda)
    stats += fsf.build_f5(day_arrays, eda, wcache) + fsf.build_f6(day_arrays, eda, wcache)
    ctx = _FCtx(dates, f_bars, day_arrays, _day_ts(f_bars), wcache)
    return stats, _f_replicas(ctx, thresholds), f3_1_table


def _family_g(bars: pd.DataFrame, dates: tuple[date, ...], thresholds: dict
              ) -> tuple[list[fsf.TestedStat], dict[str, _Replica], list[dict]]:
    """``_d1e_event_series.collect_g_stats``'s pipeline per timeframe, plus G0."""
    g_bars = rsm.annotate_session(bars)
    g_bars["trade_date_obj"] = pd.to_datetime(g_bars["trade_date"].astype(str)).dt.date
    p_end_ts = _p_end_ts(g_bars, dates)
    stats, replicas, g0 = [], {}, []
    for tf in rsm.TIMEFRAMES:
        coarse = rsm.coarse_bars(g_bars, tf)
        days = gsf.build_days(g_bars, coarse, tf, list(dates))
        tf_stats, q80s = gsf.build_statistics(days, tf)
        stats += tf_stats
        replicas.update(_g_replicas(days, _slot_last_ts(g_bars, days, tf), p_end_ts, tf,
                                    thresholds))
        for sid, q in q80s.items():
            if not _same(np.array([q]), np.array(thresholds[f"{sid}_q80"])):
                raise AssertionError(f"{sid}: replica Q80 differs from the hashed Q80")
        g0 += [{"tf": tf, **gsf.g0_autocorrelation(days, s)} for s in rsm.SEGMENTS]
    return stats, replicas, g0


def compute_statistics(bars: pd.DataFrame, candidate_dates: Iterable[date],
                       splice_trade_dates: Sequence[date]) -> StatisticsRun:
    """Every F and G statistic on ``candidate_dates`` after the EDA path's exclusions.
    ``bars``: every bar of every candidate date (BAR_COLUMNS, from a data.research_bars
    loader); ``splice_trade_dates``: that parquet's roll splices (for the roll blackout)."""
    roll_blackout = canonical_engine_config(splice_trade_dates).roll_blackout
    dates, excluded = resolve_statistic_dates(bars, candidate_dates, roll_blackout)
    if not dates:
        raise ValueError("no statistic dates survive the exclusions")
    stat_bars = select_statistic_bars(bars, dates)
    prices = _PriceIndex(stat_bars)
    thresholds: dict[str, tuple[float, ...]] = {}
    f_stats, f_rep, f3_1_table = _family_f(stat_bars, dates, thresholds)
    g_stats, g_rep, g0 = _family_g(stat_bars, dates, thresholds)
    directional: dict[str, StatisticEvents] = {}
    descriptive: dict[str, Mapping[str, object]] = {}
    for source, stats, rep in (("F", f_stats, f_rep), ("G", g_stats, g_rep)):
        for stat in stats:
            if stat.directional:
                directional[stat.id] = _events(stat, source, rep[stat.id], prices)
            else:
                estimate, n, _, extra = _summary(stat)
                descriptive[stat.id] = MappingProxyType({
                    "family": stat.family, "description": stat.description,
                    "estimate": estimate, "n": n, **extra})
    if (len(directional), len(descriptive)) != (N_DIRECTIONAL, N_DESCRIPTIVE):
        raise AssertionError(f"got {len(directional)}/{len(descriptive)} statistics")
    return StatisticsRun(
        dates, tuple(MappingProxyType(e) for e in excluded), MappingProxyType(directional),
        MappingProxyType(descriptive), tuple(MappingProxyType(g) for g in g0),
        tuple(MappingProxyType(r) for r in f3_1_table), MappingProxyType(thresholds))


def forward_mean_moves_ticks(events: StatisticEvents, path: DriftPath) -> np.ndarray:
    """Per event: the window-mean price change, in ticks, over the event's own forward
    interval (``DriftPath.mean_move_ticks`` between its two points); the list's drift charge
    (3.2(ii)) is s times this. An interval that crosses a trade date (F4.4 only) raises:
    how to charge drift across the daily halt is not defined here."""
    out = np.empty(len(events.values))
    cache: dict[tuple, float] = {}
    for i in range(len(events.values)):
        start_ts, end_ts = int(events.start_bar_ts_ns[i]), int(events.end_bar_ts_ns[i])
        if start_ts not in path.locator or end_ts not in path.locator:
            raise ValueError(f"{events.stat_id}: event {i} on {events.trade_dates[i]} lies "
                             "outside the drift path's dates")
        (s_row, s_min), (e_row, e_min) = path.locator[start_ts], path.locator[end_ts]
        if s_row != e_row:
            raise ValueError(f"{events.stat_id}: event {i} on {events.trade_dates[i]} crosses "
                             "a trade date; its drift charge is undefined on a one-day path")
        key = (s_min, events.start_price[i], e_min, events.end_price[i])
        if key not in cache:
            cache[key] = path.mean_move_ticks(key[:2], key[2:])
        out[i] = cache[key]
    return out
