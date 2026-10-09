"""H2, the month-end NQ/ZN rebalancing pair (lead_spec section 4; multi-day, IBKR).

Trading days: trade dates of both the equity and the rates group calendars. d5 = the month's
fifth-last trading day, dL = its last. Decision at D = max(S_NQ(d5), S_ZN(d5)) CT on d5 (15:00
under equity 15:00 and rates 14:00): MTD_X = the chained same-contract return from PS(X, the prior
month's last trading day) to PS(X, d5) (PS = close of bar(X, d, S_X - 1), section 0; the chain
splits at each splice: the old segment ends at the close of the last bar before it, the new one
starts at the open of the first bar at or after it). MTD_NQ > MTD_ZN: short NQ, long ZN; else
long NQ, short ZN. Both legs enter at the open of bar(X, d5, D) and exit at the open of
bar(X, dL, S_X(dL)), rolled across splices, marked daily at MK(X, d) = open of bar(X, d, S_X);
ruling R-B1: where a scheduled closure begins at that minute, an exit or mark is the close of
bar(S_X - 1) and an entry the open of the first bar of the trade date's session after it.
Unit: the month, dated dL; value: the sum of the two legs' risk-unit net P&L (one sigma per leg).
"""

from __future__ import annotations

from collections import Counter
from datetime import date

from base_rules import constants as K
from base_rules.calendars import both_trade_dates
from base_rules.common import (
    FLAT_DIAG,
    RunContext,
    RunOutput,
    Unit,
    action_exclusion,
    entry_point,
    flat_fill_bars,
    load_or_exclude,
    lock_rule,
    reference_exclusion,
    scale_units,
    settle_point,
    top,
    unit_row,
)
from base_rules.scaling import TRADED
from base_rules.sim import simulate
from base_rules.store import ProductBars


def months(ctx: RunContext) -> list[tuple[date | None, date, date]]:
    """(prior month's last trading day, d5, dL) per month with at least 5 trading days."""
    days = both_trade_dates(ctx.cal(K.H2_EQUITY), ctx.cal(K.H2_BOND))
    by_month: dict[tuple[int, int], list[date]] = {}
    for d in days:
        by_month.setdefault((d.year, d.month), []).append(d)
    out, prev_last = [], None
    for key in sorted(by_month):
        ds = by_month[key]
        if len(ds) >= K.H2_D5_FROM_END:
            out.append((prev_last, ds[-K.H2_D5_FROM_END], ds[-1]))
        prev_last = ds[-1]
    return out


def chained_return(bars: ProductBars, i_start: int, i_end: int) -> tuple[float | None, str]:
    """Product of same-contract segment returns from the close of ``i_start`` to the close of
    ``i_end``, split at the store's splices; (None, reason) when a bar is missing or a segment
    changes contract."""
    lo, hi = int(bars.ts[i_start]), int(bars.ts[i_end])
    start_price, start_i, ratio = int(bars.close_t[i_start]), i_start, 1.0
    for s in bars.splices_between(lo, hi):
        i_out, i_in = bars.last_before(s.ts_ns), bars.first_at_or_after(s.ts_ns)
        if i_out is None or i_in is None or i_out < start_i:
            return None, "missing bar"
        if bars.contract(i_out) != bars.contract(start_i):
            return None, "contract change"
        ratio *= int(bars.close_t[i_out]) / start_price
        start_price, start_i = int(bars.open_t[i_in]), i_in
    if bars.contract(i_end) != bars.contract(start_i):
        return None, "contract change"
    return ratio * int(bars.close_t[i_end]) / start_price - 1.0, ""


def _store_boundary(d5: date, d_last: date) -> bool:
    gap = (K.HIST_LAST, K.STEP2_FIRST)
    return (d5 <= gap[0] < d_last) or any(gap[0] < d < gap[1] for d in (d5, d_last))


def _leg(ctx: RunContext, bars: ProductBars, x: str, ref: date | None, d5: date,
         d_last: date, decision: int) -> tuple[str | None, dict]:
    st = ctx.settlement
    for d in (d5, d_last):
        why = action_exclusion(ctx, bars, x, d)
        if why:
            return why, {}
    why = reference_exclusion(ctx, x, ref)
    if why:
        return why, {}
    assert ref is not None
    if not ctx.listed(x, ref):
        return "no reference (not listed)", {}
    i_ref = bars.bar(ref, st.settle_minute(x, ref) - 1)
    if i_ref is None:
        return "no reference (missing bar)", {}
    i_ps = bars.bar(d5, st.settle_minute(x, d5) - 1)
    if i_ps is None:
        return "missing bar", {}
    p_in, why = entry_point(ctx, bars, x, d5, decision)  # R-B1 (b)
    if p_in is None:
        return why, {}
    p_out = settle_point(ctx, bars, x, d_last)  # R-B1 (a)
    if p_out is None:
        return "missing bar", {}
    mtd, why = chained_return(bars, i_ref, i_ps)
    if mtd is None:
        return why, {}
    cal = ctx.cal(x)
    marks, dates, d = [], [], d5
    while d is not None and d <= d_last:
        marks.append(settle_point(ctx, bars, x, d) if ctx.listed(x, d) else None)
        dates.append(d)
        d = cal.offset(d, 1)
    return None, {"mtd": mtd, "p_in": p_in, "p_out": p_out, "marks": marks, "dates": dates,
                  "after_closure": ctx.closure_at(x, d5, decision)}


def run_h2(ctx: RunContext) -> RunOutput:
    counters: Counter = Counter()
    notes: dict = {}
    legs = {x: load_or_exclude(ctx, x, counters, notes) for x in K.H2_LEGS}
    if any(b is None for b in legs.values()):
        return _combine([], counters, notes)
    st = ctx.settlement
    units: list[Unit] = []
    locks = {x: lock_rule(ctx, legs[x]) for x in K.H2_LEGS}
    for ref, d5, d_last in months(ctx):
        if d_last > ctx.last or d5 < min(ctx.starts[x] for x in K.H2_LEGS):
            counters["outside window"] += 1
            continue
        if _store_boundary(d5, d_last):
            counters["store boundary"] += 1
            continue
        if not all(ctx.listed(x, d) for x in K.H2_LEGS for d in (d5, d_last)):
            counters["not listed"] += 1
            continue
        decision = max(int(st.settle_minute(x, d5)) for x in K.H2_LEGS)
        got = {x: _leg(ctx, legs[x], x, ref, d5, d_last, decision) for x in K.H2_LEGS}
        why = next((w for w, _ in got.values() if w), None)
        if why:
            counters[top(why)] += 1
            counters[why] += 0 if why == top(why) else 1
            continue
        counters["eligible"] += 1
        eq, bd = got[K.H2_EQUITY][1], got[K.H2_BOND][1]
        sign_eq = -1 if eq["mtd"] > bd["mtd"] else 1
        sims = {}
        for x, info, direction in ((K.H2_EQUITY, eq, sign_eq), (K.H2_BOND, bd, -sign_eq)):
            sims[x] = (simulate(legs[x], ctx.vc(x), ctx.releases,
                                [(info["p_in"], direction), (info["p_out"], 0)], info["marks"],
                                locks=locks[x]), direction)
        bad = next((s.reason for s, _ in sims.values() if not s.ok), None)
        if bad:
            counters[bad] += 1
            continue
        counters["uncalibrated bucket"] += int(any(s.uncalibrated for s, _ in sims.values()))
        counters["entry after closure"] += int(eq["after_closure"] or bd["after_closure"])
        counters[FLAT_DIAG] += sum(flat_fill_bars(legs[x], s) for x, (s, _) in sims.items())
        month = f"{d_last.year}-{d_last.month:02d}"
        for x, (sim, direction) in sims.items():
            units.append(Unit(x, d_last, direction, sim, {
                "month": month, "d5": str(d5), "mtd": got[x][1]["mtd"],
                "decision_ct": decision, "entry_after_closure": got[x][1]["after_closure"],
                "exit_at_close": bool(got[x][1]["p_out"][1]),
                "open_dates": [str(d) for d in got[x][1]["dates"]]}))
    del legs
    leg_counts: Counter = Counter()
    scale_units(units, leg_counts)
    counters.update({f"leg {k}": v for k, v in leg_counts.items()})
    return _combine(units, counters, notes)


def _combine(units: list[Unit], counters: Counter, notes: dict) -> RunOutput:
    by_month: dict[date, list[Unit]] = {}
    for u in units:
        by_month.setdefault(u.unit_date, []).append(u)
    series = {c: [] for c in K.COST_CASES}
    daily: dict[str, dict[date, float]] = {c: {} for c in K.COST_CASES}
    grid: set[date] = set()
    for d_last, pair in sorted(by_month.items()):
        if len(pair) != 2 or any(u.status != TRADED for u in pair):
            counters["unit not traded (warm-up or sigma)"] += 1
            continue
        counters["traded"] += 1
        for c in K.COST_CASES:
            series[c].append((d_last, sum(u.net_ru(c) for u in pair)))
            for u in pair:
                for d, v in u.sim.daily[c].items():
                    daily[c][d] = daily[c].get(d, 0.0) + float(v) / 100.0 / float(u.sigma)
        for u in pair:
            grid.update(date.fromisoformat(d) for d in u.info["open_dates"])
    per_product = {x: Counter(u.status for u in units if u.key == x) for x in K.H2_LEGS}
    return RunOutput("H2", series, daily, grid, counters, per_product,
                     [unit_row(u) for u in units], notes)


__all__ = ["chained_return", "months", "run_h2"]
