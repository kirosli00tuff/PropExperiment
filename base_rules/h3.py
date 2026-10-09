"""H3, the Treasury auction cycle (lead_spec section 4; multi-day, IBKR).

EC-AUC auctions (base_rules.auctions.load_auctions, E.0's rule), tenor map 2Y ZT, 5Y ZF, 10Y ZN,
30Y ZB. An auction counts only if announced on or before t-3 (F-04, lead ruling). t = the
auction date (a rates trade date, else skipped and counted). Short at the open of
bar(T, t-3, S_T); at the open of bar(T, t, S_T) cover and go long (one fill of two contracts:
two sides); exit at the open of bar(T, t+5, S_T); t-3 and t+5 counted in rates trade dates.
Ruling R-B1 applies at a closure beginning at S_T (none in the rates calendars).
Same-tenor windows [t-3, t+5] that overlap: the earlier is kept, the later dropped (on the
calendar, before any bar). t-3, t and t+5 are action dates (t is an exit and an entry). A unit
whose t+5 is after 2024-02-29 is excluded ("window end"). A fill the engine's limit-lock test
refuses excludes the unit ("limit locked", F-07; rates have no hard limit). "entry after closure"
counts R-B1 (b) entries (F-09). Unit: the auction, dated t; one sigma per tenor from the combined
two-leg g.
"""

from __future__ import annotations

from collections import Counter
from datetime import date

from base_rules import constants as K
from base_rules.auctions import Auction
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
    scale_units,
    settle_point,
    unit_row,
)
from base_rules.scaling import TRADED
from base_rules.sim import simulate


def windows(ctx: RunContext, auctions: tuple[Auction, ...] | list[Auction], counters: Counter
            ) -> list[tuple[Auction, date, date, date]]:
    """(auction, t-3, t, t+5) kept, in date order, on the calendar only: t a rates trade date;
    t on or before the window's end; t-3 exists; the announcement rule (F-04, lead ruling: the
    auction counts only if announcemt_date is on or before t-3; "announced after entry", "no
    announcement date"); t+5 on or before the window's end ("window end"); then the same-tenor
    overlap rule among the auctions that count."""
    kept: list[tuple[Auction, date, date, date]] = []
    last_end: dict[str, date] = {}
    for a in sorted(auctions, key=lambda x: (x.day, x.tenor)):
        cal = ctx.cal(a.root)
        if not cal.is_trade_date(a.day):
            counters["auction not a trade date"] += 1
            continue
        if a.day > ctx.last:
            counters["window end"] += 1
            continue
        before, after = cal.offset(a.day, -K.H3_BEFORE), cal.offset(a.day, K.H3_AFTER)
        if before is None:
            counters["outside window"] += 1
            continue
        if a.announced is None:
            counters["no announcement date"] += 1
            continue
        if a.announced > before:
            counters["announced after entry"] += 1
            continue
        if after is None or after > ctx.last:
            counters["window end"] += 1
            continue
        if a.tenor in last_end and before <= last_end[a.tenor]:
            counters["same-tenor overlap"] += 1
            continue
        last_end[a.tenor] = after
        kept.append((a, before, a.day, after))
    return kept


def _boundary(lo: date, hi: date) -> bool:
    return (lo <= K.HIST_LAST < hi) or any(K.HIST_LAST < d < K.STEP2_FIRST for d in (lo, hi))


def _changes(ctx: RunContext, bars, root: str, before: date, t: date, after: date  # noqa: ANN001
             ) -> tuple[list, str | None]:
    """The fill points (R-B1): short at the entry point of t-3; at t, cover at t's settlement
    point and go long at t's entry point (one fill of two contracts when they are the same bar
    open); exit at t+5's settlement point."""
    st = ctx.settlement
    p1, why = entry_point(ctx, bars, root, before, int(st.settle_minute(root, before)))
    if p1 is None:
        return [], why
    cover = settle_point(ctx, bars, root, t)
    p2, why = entry_point(ctx, bars, root, t, int(st.settle_minute(root, t)))
    p3 = settle_point(ctx, bars, root, after)
    if cover is None or p3 is None:
        return [], "missing bar"
    if p2 is None:
        return [], why
    middle = [(p2, 1)] if cover == p2 else [(cover, 0), (p2, 1)]
    return [(p1, -1), *middle, (p3, 0)], None


def run_h3(ctx: RunContext) -> RunOutput:
    counters: Counter = Counter()
    kept = windows(ctx, ctx.auctions, counters)
    units: list[Unit] = []
    notes: dict = {}
    for root in sorted({a.root for a, *_ in kept}):
        bars = load_or_exclude(ctx, root, counters, notes)
        if bars is None:
            continue
        cal = ctx.cal(root)
        locks = lock_rule(ctx, bars)
        for a, before, t, after in (w for w in kept if w[0].root == root):
            why = next((w for w in (action_exclusion(ctx, bars, root, d)
                                    for d in (before, t, after)) if w), None)
            if why:
                counters[why] += 1
                continue
            if _boundary(before, after):
                counters["store boundary"] += 1
                continue
            if not all(ctx.listed(root, d) for d in (before, t, after)):
                counters["not listed"] += 1
                continue
            changes, why = _changes(ctx, bars, root, before, t, after)
            if why:
                counters[why] += 1
                continue
            dates, d = [], before
            while d is not None and d <= after:
                dates.append(d)
                d = cal.offset(d, 1)
            marks = [settle_point(ctx, bars, root, x) if ctx.listed(root, x) else None
                     for x in dates]
            sim = simulate(bars, ctx.vc(root), ctx.releases, changes, marks, locks=locks)
            if not sim.ok:
                counters[sim.reason or "excluded"] += 1
                continue
            counters["uncalibrated bucket"] += int(sim.uncalibrated)
            st = ctx.settlement
            counters["entry after closure"] += int(any(
                ctx.closure_at(root, d, int(st.settle_minute(root, d))) for d in (before, t)))
            counters[FLAT_DIAG] += flat_fill_bars(bars, sim)
            counters["eligible"] += 1
            units.append(Unit(root, t, 1, sim, {"auction": a.id, "tenor": a.tenor,
                                                 "t_minus": str(before), "t_plus": str(after),
                                                 "open_dates": [str(x) for x in dates]}))
        del bars
    scale_units(units, counters)
    series = {c: [] for c in K.COST_CASES}
    daily: dict[str, dict[date, float]] = {c: {} for c in K.COST_CASES}
    grid: set[date] = set()
    for u in sorted(units, key=lambda u: (u.unit_date, u.key)):
        if u.status != TRADED:
            continue
        for c in K.COST_CASES:
            series[c].append((u.unit_date, u.net_ru(c)))
            for d, v in u.sim.daily[c].items():
                daily[c][d] = daily[c].get(d, 0.0) + float(v) / 100.0 / float(u.sigma)
        grid.update(date.fromisoformat(x) for x in u.info["open_dates"])
    per_product = {r: Counter(u.status for u in units if u.key == r)
                   for r in sorted(set(K.H3_TENOR_ROOT.values()))}
    return RunOutput("H3", series, daily, grid, counters, per_product,
                     [unit_row(u) for u in units], notes)


__all__ = ["run_h3", "windows"]
