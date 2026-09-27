"""M4: one product's decision rows with F1-F17, availability times and the three net targets.

The target (M4 with ruling ML-A08): y = (open of the bar at the exit - open of the bar at
t + 1 minute), in ticks of the exposure's D2 vehicle, minus the vehicle's full D8 round-turn
cost at q_c for a long (entry side "buy" in t + 1 minute's bucket, exit side "sell" in the exit's
bucket; an event-window fill pays the largest half-spread plus its own depth term, T12-4), all
divided by sigma_X,d. The exit is the bar at t + h, or the forced flatten fill at the bar opening
at F_X for the "to F" horizon. ``cost`` is that round turn in sigma units (ML-A01's c).
Exit fills inside the event-minute guard (lead ruling OC-M, Stage E.2b, on the pipeline worker's
Q3): D9.5a governs every simulated fill, exactly as the Stage E engine applies it
(screening.stage_e_rules.StageERules.admit_fill). An exit whose fill would land in
[release, release + 2 min) is deferred to the open of the first bar at or after release + 2 min
(again while that bar is itself in a guard window), and the D8 event-window cost applies to a
fill in [release, release + 30 min). A deferral that reaches F_X is superseded by the forced
flatten at the bar opening at F_X, which the engine exempts from the guard (runner reading RR-3),
so the to-F horizon is never deferred. The target is not set missing for this reason; the exit
time (``exit_ns``) is the deferred fill time, so M4's one-open-position rule sees it. Counted:
``target_<h>_exit_deferred_event_guard`` (deferred to a later bar before F_X) and
``target_<h>_exit_guard_forced_at_flatten`` (a deferral superseded by the flatten at F_X).
An entry fill (t + 1 minute) in a guard window cannot arise: M4 excludes that decision time.
Rows or targets that cannot be formed are counted by named cause:
- ``decisions_event_guard`` / ``decisions_cpi_window``: the entry fill at t + 1 minute lies in a
  D9.5a guard window or D9.12's CPI window of the vehicle (the decision time is excluded);
- ``target_<h>_no_cost_bucket``: a fill minute that no calibrated D8 bucket covers;
- ``target_<h>_too_short``: t + h beyond F_X, or less than 2 minutes between the fills (D9.3);
- ``target_<h>_bar_absent``: no bar at t, at t + 1 minute or at the exit (ML-A05); for a
  deferred exit, no bar before F_X after the guard and no bar at F_X.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date

import numpy as np
import pandas as pd

from ml_route.constants import (
    EVENT_COST_WINDOW_MIN,
    EVENT_GUARD_MIN,
    HORIZON_MINUTES,
    HORIZONS,
    LEAD_RETURN_MIN,
    MIN_HOLD_MIN,
    RETURN_LOOKBACKS_MIN,
    SIGMA_LOOKBACK_DATES,
)
from ml_route.features import (
    BAR_NS,
    N_FEATURES,
    NS_MIN,
    Bars,
    Daily,
    LeadContext,
    RowTable,
    _ct_date,
    _ct_minute,
    _in_windows,
    decision_grid,
)
from ml_route.inputs import ProductSpec, VehicleCost

COL = {name: i for i, name in enumerate((
    "F1_ret5", "F2_ret15", "F3_ret30", "F4_ret60", "F5_ret120", "F6_ret_day", "F7_gap",
    "F8_clv_prev", "F9_range", "F10_logvol", "F11_min_since_open", "F12_dow",
    "F13_min_to_release", "F14_min_since_release", "F15_release_day", "F16_lead_ret30",
    "F17_vol_state"))}


def _same_day(bars: Bars, idx: np.ndarray, days: np.ndarray) -> np.ndarray:
    ok = idx >= 0
    out = np.zeros(len(idx), dtype=bool)
    out[ok] = bars.trade_date[idx[ok]] == days[ok]
    return out


def _grouped_cum(values: np.ndarray, first_idx: np.ndarray, n: int, fn: str) -> np.ndarray:
    group = np.zeros(n, dtype=np.int64)
    group[first_idx[1:]] = 1
    group = np.cumsum(group)
    s = pd.Series(values)
    return getattr(s.groupby(group), fn)().to_numpy()


def _vol30_table(bars: Bars, daily: Daily, slots: np.ndarray) -> dict[int, np.ndarray]:
    """Per CT decision minute: the (t - 30, t] volume on every product date (NaN if the date has
    no session time at that clock), in date order."""
    cum = np.concatenate([[0.0], np.cumsum(bars.volume)])
    opens = np.array([dt.open_ns for dt in daily.times], dtype=np.int64)
    midnight = opens - _ct_minute(opens).astype(np.int64) * NS_MIN  # CT midnight of each date
    ends = np.append(daily.first_idx[1:], len(bars.ts))
    out = {}
    for slot in slots.tolist():
        t = midnight + int(slot) * NS_MIN
        lo = np.maximum(np.searchsorted(bars.ts, t - 30 * NS_MIN), daily.first_idx)
        hi = np.minimum(np.searchsorted(bars.ts, t - BAR_NS, side="right"), ends)
        out[slot] = np.where(hi > lo, cum[np.maximum(hi, lo)] - cum[lo], 0.0)
    return out


def build_rows(bars: Bars, daily: Daily, spec: ProductSpec, cost: VehicleCost,
               blackout: frozenset[date], releases: np.ndarray, cpi: np.ndarray,
               lead: LeadContext | None, only_date_pos: int | None = None) -> RowTable:
    counts: dict[str, int] = {}
    pos, t = decision_grid(bars, daily, spec, blackout, releases, cpi, counts, only_date_pos)
    n = len(t)
    pu = spec.vehicle_ticks_per_vendor_unit
    days = daily.dates[pos]
    sigma = daily.sigma[pos]
    X = np.full((n, N_FEATURES), np.nan)
    A = np.full((n, N_FEATURES), -1, dtype=np.int64)
    i_t = bars.idx_at(t - BAR_NS)  # the bar closing at t
    ok_t = _same_day(bars, i_t, days)
    close_t = np.where(ok_t, bars.close[np.clip(i_t, 0, None)], np.nan)
    avail_t = np.where(ok_t, bars.ts[np.clip(i_t, 0, None)] + BAR_NS, -1)
    for c, k in enumerate(RETURN_LOOKBACKS_MIN):  # F1-F5
        i_k = bars.idx_at(t - (k * NS_MIN) - BAR_NS)
        ok = ok_t & _same_day(bars, i_k, days)
        X[ok, c] = (close_t[ok] - bars.close[i_k[ok]]) * pu / sigma[ok]
        A[ok, c] = avail_t[ok]
    first = daily.first_idx[pos]
    X[ok_t, COL["F6_ret_day"]] = (close_t[ok_t] - bars.open[first[ok_t]]) * pu / sigma[ok_t]
    A[ok_t, COL["F6_ret_day"]] = avail_t[ok_t]
    X[:, COL["F7_gap"]] = daily.f7[pos] / sigma  # f7 is already in vehicle ticks
    A[:, COL["F7_gap"]] = daily.f7_avail[pos]
    X[:, COL["F8_clv_prev"]] = daily.f8[pos]
    A[:, COL["F8_clv_prev"]] = daily.f8_avail[pos]
    hi_cum = _grouped_cum(bars.high, daily.first_idx, len(bars.ts), "cummax")
    lo_cum = _grouped_cum(bars.low, daily.first_idx, len(bars.ts), "cummin")
    it = np.clip(i_t, 0, None)
    X[ok_t, COL["F9_range"]] = (hi_cum[it[ok_t]] - lo_cum[it[ok_t]]) * pu / sigma[ok_t]
    A[ok_t, COL["F9_range"]] = avail_t[ok_t]
    _fill_f10(bars, daily, pos, t, ok_t, X, A)
    X[:, COL["F11_min_since_open"]] = (t - np.array([daily.times[p].open_ns for p in pos],
                                                    dtype=np.int64)) / NS_MIN
    X[:, COL["F12_dow"]] = (days.astype("datetime64[D]").view("int64") - 4) % 7  # Monday = 0
    A[:, COL["F11_min_since_open"]] = t
    A[:, COL["F12_dow"]] = t
    _fill_events(t, releases, X, A)
    if lead is not None:
        _fill_f16(lead, days, t, X, A)
    X[:, COL["F17_vol_state"]] = daily.f17[pos]
    A[:, COL["F17_vol_state"]] = daily.sigma_avail[pos]
    X[~np.isfinite(sigma)] = np.nan
    y, cst, exits = _targets(bars, daily, pos, t, days, sigma, cost, pu, releases, counts)
    prod = np.full(n, spec.root, dtype=object)
    clus = np.full(n, spec.cluster, dtype=object)
    counts["decision_rows"] = n
    counts["rows_sigma_missing"] = int((~np.isfinite(sigma)).sum())
    return RowTable(prod, clus, days, t, X, A, sigma, y, cst, exits, counts)


def _fill_f10(bars: Bars, daily: Daily, pos: np.ndarray, t: np.ndarray, ok_t: np.ndarray,
              X: np.ndarray, A: np.ndarray) -> None:
    c = COL["F10_logvol"]
    slots = np.unique(_ct_minute(t)) if len(t) else np.array([], dtype=np.int64)
    table = _vol30_table(bars, daily, slots)
    row_slot = _ct_minute(t) if len(t) else np.array([], dtype=np.int64)
    for slot, vals in table.items():
        med = (pd.Series(vals).rolling(SIGMA_LOOKBACK_DATES, min_periods=SIGMA_LOOKBACK_DATES)
               .median().shift(1).to_numpy())
        rows = np.flatnonzero((row_slot == slot) & ok_t)
        cur, base = vals[pos[rows]], med[pos[rows]]
        good = np.isfinite(base) & (base > 0) & (cur > 0)
        X[rows[good], c] = np.log(cur[good] / base[good])
        A[rows[good], c] = t[rows[good]]


def _fill_events(t: np.ndarray, releases: np.ndarray, X: np.ndarray, A: np.ndarray) -> None:
    if len(t) == 0:
        return
    nxt = np.searchsorted(releases, t, side="left")
    has_next = nxt < len(releases)
    has_last = nxt > 0
    X[has_next, COL["F13_min_to_release"]] = (releases[nxt[has_next]] - t[has_next]) / NS_MIN
    X[has_last, COL["F14_min_since_release"]] = (t[has_last] - releases[nxt[has_last] - 1]) / NS_MIN
    rel_days = np.unique(_ct_date(releases)) if len(releases) else np.array([], "datetime64[D]")
    X[:, COL["F15_release_day"]] = np.isin(_ct_date(t), rel_days).astype(float)
    for name in ("F13_min_to_release", "F14_min_since_release", "F15_release_day"):
        A[:, COL[name]] = t  # calendar values, known in advance


def _fill_f16(lead: LeadContext, days: np.ndarray, t: np.ndarray, X: np.ndarray,
              A: np.ndarray) -> None:
    lb = lead.bars
    j = np.searchsorted(lb.ts, t - BAR_NS, side="right") - 1  # latest lead bar closing <= t
    ok = j >= 0
    jj = np.clip(j, 0, None)
    ok &= lb.trade_date[jj] == days
    j30 = lb.idx_at(lb.ts[jj] - LEAD_RETURN_MIN * NS_MIN)
    ok &= j30 >= 0
    ok[ok] &= lb.trade_date[j30[ok]] == days[ok]
    lpos = np.searchsorted(lead.daily.dates, days)
    lpos_ok = (lpos < len(lead.daily.dates))
    lpos_ok[lpos_ok] &= lead.daily.dates[lpos[lpos_ok]] == days[lpos_ok]
    ok &= lpos_ok
    lsig = np.full(len(t), np.nan)
    lsig[ok] = lead.daily.sigma[lpos[ok]]
    ok &= np.isfinite(lsig)
    X[ok, COL["F16_lead_ret30"]] = (lb.close[jj[ok]] - lb.close[j30[ok]]) * lead.per_unit / lsig[ok]
    A[ok, COL["F16_lead_ret30"]] = lb.ts[jj[ok]] + BAR_NS


def deferred_exit(bars: Bars, releases: np.ndarray, x_ns: int, flatten_ns: int
                  ) -> tuple[int, int, str]:
    """(fill time, bar index or -1, kind) of an exit whose nominal fill is at ``x_ns``, as the
    engine fills it (OC-M): kind "none" (not in a guard window), "deferred" (the open of the
    first bar at or after release + 2 min, repeated while that bar is guarded) or "flatten"
    (the deferral reaches F_X: the forced flatten at the bar opening at F_X, exempt, RR-3)."""
    guard_ns = EVENT_GUARD_MIN * NS_MIN
    when, kind = int(x_ns), "none"
    while True:
        k = int(np.searchsorted(releases, when, side="right")) - 1
        if k < 0 or when >= int(releases[k]) + guard_ns:
            break
        kind = "deferred"
        j = int(np.searchsorted(bars.ts, int(releases[k]) + guard_ns, side="left"))
        if when >= flatten_ns or j >= len(bars.ts) or int(bars.ts[j]) >= flatten_ns:
            return int(flatten_ns), int(bars.idx_at(np.array([flatten_ns]))[0]), "flatten"
        when = int(bars.ts[j])
    return when, int(bars.idx_at(np.array([when]))[0]), kind


def _targets(bars: Bars, daily: Daily, pos: np.ndarray, t: np.ndarray, days: np.ndarray,
             sigma: np.ndarray, cost: VehicleCost, pu: float, releases: np.ndarray,
             counts: dict[str, int]) -> tuple[dict, dict, dict]:
    n = len(t)
    entry_ns = t + BAR_NS
    i_bar_t = bars.idx_at(t)
    i_entry = bars.idx_at(entry_ns)
    flat = np.array([daily.times[p].flatten_ns for p in pos], dtype=np.int64)
    entry_min = _ct_minute(entry_ns) if n else np.array([], dtype=np.int64)
    entry_event = _in_windows(entry_ns, releases, EVENT_COST_WINDOW_MIN * NS_MIN)
    y, cst, exits = {}, {}, {}
    for h in HORIZONS:
        mins = HORIZON_MINUTES[h]
        x_ns = flat.copy() if mins is None else t + mins * NS_MIN
        yv = np.full(n, np.nan)
        cv = np.full(n, np.nan)
        xv = np.full(n, -1, dtype=np.int64)
        short = (x_ns > flat) | (x_ns - entry_ns < MIN_HOLD_MIN * NS_MIN)
        i_exit = bars.idx_at(x_ns)
        guard = _in_windows(x_ns, releases, EVENT_GUARD_MIN * NS_MIN)
        n_deferred = n_flatten = 0
        for r in np.flatnonzero(guard & ~short).tolist():  # OC-M: the engine's D9.5a deferral
            when, j, kind = deferred_exit(bars, releases, int(x_ns[r]), int(flat[r]))
            x_ns[r], i_exit[r] = when, j
            n_deferred += kind == "deferred"
            n_flatten += kind == "flatten"
        absent = (i_bar_t < 0) | (i_entry < 0) | (i_exit < 0)
        exit_event = _in_windows(x_ns, releases, EVENT_COST_WINDOW_MIN * NS_MIN)
        exit_min = _ct_minute(x_ns) if n else np.array([], dtype=np.int64)
        ok = ~short & ~absent & np.isfinite(sigma)
        no_bucket = 0
        for r in np.flatnonzero(ok):
            rt = cost.long_round_turn_ticks(int(entry_min[r]), int(exit_min[r]),
                                            bool(entry_event[r]), bool(exit_event[r]))
            if rt is None:
                ok[r] = False
                no_bucket += 1
                continue
            move = (bars.open[i_exit[r]] - bars.open[i_entry[r]]) * pu
            yv[r] = (move - rt) / sigma[r]
            cv[r] = rt / sigma[r]
            xv[r] = x_ns[r]
        counts[f"target_{h}_too_short"] = int(short.sum())
        counts[f"target_{h}_bar_absent"] = int((absent & ~short).sum())
        counts[f"target_{h}_exit_deferred_event_guard"] = n_deferred
        counts[f"target_{h}_exit_guard_forced_at_flatten"] = n_flatten
        counts[f"target_{h}_no_cost_bucket"] = no_bucket
        y[h], cst[h], exits[h] = yv, cv, xv
    return y, cst, exits


def concat_tables(tables: list[RowTable]) -> RowTable:
    """Rows of several products, ordered by (t, product) so a date's rows sit together."""
    if not tables:
        raise ValueError("no row tables to join")
    cat = {name: np.concatenate([getattr(tb, name) for tb in tables])
           for name in ("product", "cluster", "day", "t_ns", "X", "avail", "sigma")}
    ys = {h: np.concatenate([tb.y[h] for tb in tables]) for h in HORIZONS}
    cs = {h: np.concatenate([tb.cost[h] for tb in tables]) for h in HORIZONS}
    xs = {h: np.concatenate([tb.exit_ns[h] for tb in tables]) for h in HORIZONS}
    order = np.lexsort((cat["product"].astype(str), cat["t_ns"]))
    counts: dict[str, int] = {}
    for tb in tables:
        for k, v in tb.counts.items():
            counts[k] = counts.get(k, 0) + v
    return RowTable(cat["product"][order], cat["cluster"][order], cat["day"][order],
                    cat["t_ns"][order], cat["X"][order], cat["avail"][order],
                    cat["sigma"][order], {h: v[order] for h, v in ys.items()},
                    {h: v[order] for h, v in cs.items()}, {h: v[order] for h, v in xs.items()},
                    counts)


def validate_availability(table: RowTable, names: Mapping[int, str] | None = None) -> None:
    """M7.1: every present feature value must be available at or before its row's t."""
    present = np.isfinite(table.X)
    late = present & ((table.avail > table.t_ns[:, None]) | (table.avail < 0))
    if late.any():
        cols = np.flatnonzero(late.any(axis=0))
        label = {v: k for k, v in COL.items()} if names is None else names
        from ml_route.features import FeatureLeak

        raise FeatureLeak("feature values available after t: " + ", ".join(
            f"{label.get(int(c), c)} ({int(late[:, c].sum())} rows)" for c in cols))
