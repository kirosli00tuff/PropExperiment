"""H1 (settlement-window momentum) and H4 (next-day reversal), pooled daily (lead_spec section 4).

H1, product p, eligible date d: s = sign(close of bar(p,d,S-31) - PS(p,d-1)), PS = close of
bar(p,d-1,S(d-1)-1); entry at the open of bar(p,d,S-30), exit "at the settlement minute": the
open of bar(p,d,S), or, ruling R-B1, the close of bar(p,d,S-1) when a scheduled closure begins at
S (equity 15:15 before 2020-10-26, grains when the day session closed at S).
H4: m = (H1's exit price on d-1, R-B1) - open bar(p,d-1,S(d-1)-30); direction -sign(m); entry at
the open of bar(p,d,O+1), exit at the open of bar(p,d,S-31).
Every decision is taken from bars that close at or before the fill bar's open (the engine's
clock). Unit: the date d; value: the equal-weight mean over the products traded on d of their
risk-unit net P&L. Products are processed one at a time; the bars are released after each.
A contract change between the reference and the trade on a non-blackout date is excluded and
counted ("contract change", R-B3): no data condition raises during a run. A fill the engine's
limit-lock test refuses excludes the unit ("limit locked", F-07). Descriptive tables beside the
base statistic (never the bar): H1 without product-dates with S_p > 15:08 CT (F-14); H1 and H4
without units entered in a no-new-positions bar ("no new positions (Topstep)", F-07); H4 without
units with an uncalibrated-bucket fill (F-13).
"""

from __future__ import annotations

from collections import Counter
from datetime import date

from base_rules import constants as K
from base_rules.common import (
    FLAT_DIAG,
    RunContext,
    RunOutput,
    Unit,
    action_exclusion,
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
from base_rules.sim import price_at, simulate
from base_rules.stats import stats_for_test
from base_rules.store import ProductBars

W = K.H1_WINDOW_MIN


def _sign(x: int) -> int:
    return (x > 0) - (x < 0)


def candidate(test: str, ctx: RunContext, bars: ProductBars, p: str, d: date
              ) -> tuple[str | None, tuple | None]:
    """(exclusion reason, None) or (None, (direction, entry point, exit point, info));
    direction 0 means an eligible date with a zero signal."""
    st = ctx.settlement
    why = action_exclusion(ctx, bars, p, d)
    if why:
        return why, None
    if not ctx.listed(p, d):
        return "not listed", None
    if not st.sourced(p, d):
        return "settlement unsourced", None
    s_min, o_min = int(st.settle_minute(p, d)), int(ctx.open_minute(p, d))
    if test == "H1" and not s_min - W > o_min:
        return "window before open", None
    if test == "H4" and not o_min + 1 < s_min - W - 1:
        return "window before open", None
    ref = ctx.cal(p).previous(d)
    why = reference_exclusion(ctx, p, ref)
    if why:
        return why, None
    assert ref is not None
    if not ctx.listed(p, ref):
        return "no reference (not listed)", None
    if not st.sourced(p, ref):
        return "no reference (settlement unsourced)", None
    s_ref = int(st.settle_minute(p, ref))
    if not s_ref - W > int(ctx.open_minute(p, ref)):
        return "no reference (window before open)", None
    if test == "H1":
        refs = [bars.bar(ref, s_ref - 1)]
        sig, i_in = bars.bar(d, s_min - W - 1), bars.bar(d, s_min - W)
        out = settle_point(ctx, bars, p, d)
        need = [sig, i_in, None if out is None else out[0]]
    else:
        ref_exit = settle_point(ctx, bars, p, ref)
        refs = [bars.bar(ref, s_ref - W), None if ref_exit is None else ref_exit[0]]
        i_in, i_out = bars.bar(d, o_min + 1), bars.bar(d, s_min - W - 1)
        need = [i_in, i_out]
    if any(i is None for i in refs):
        return "no reference (missing bar)", None
    if any(i is None for i in need):
        return "missing bar", None
    if len({bars.contract(int(i)) for i in refs + need if i is not None}) != 1:
        return "contract change", None
    info = {"settle_ct": s_min, "after_1508": s_min > K.TOPSTEP_FLATTEN_CT.hour * 60
            + K.TOPSTEP_FLATTEN_CT.minute}
    if test == "H1":
        direction = _sign(int(bars.close_t[sig]) - int(bars.close_t[refs[0]]))
        info["exit_at_close"] = bool(out[1])
        info["entry_no_new"] = _no_new(bars, int(i_in))
        return None, (direction, (int(i_in), False), out, info)
    m = price_at(bars, ref_exit) - int(bars.open_t[refs[0]])
    info["ref_exit_at_close"] = bool(ref_exit[1])
    info["entry_no_new"] = _no_new(bars, int(i_in))
    return None, (-_sign(m), (int(i_in), False), (int(i_out), False), info)


def _no_new(bars: ProductBars, i: int) -> bool:
    return bars.no_new is not None and bool(bars.no_new[i])


def product_units(test: str, ctx: RunContext, p: str, bars: ProductBars, counters: Counter,
                  eligible: set[date]) -> list[Unit]:
    units = []
    vc = ctx.vc(p)
    locks = lock_rule(ctx, bars)
    for d in ctx.cal(p).trade_dates():
        if d < K.PROMPT_FIRST or d > ctx.last:
            continue
        why, cand = candidate(test, ctx, bars, p, d)
        if why:
            counters[top(why)] += 1
            counters[why] += 0 if why == top(why) else 1
            continue
        assert cand is not None
        direction, p_in, p_out, info = cand
        eligible.add(d)
        counters["eligible"] += 1
        counters["after 15:08"] += int(info["after_1508"])
        counters["exit at the close of S-1 (R-B1)"] += int(info.get("exit_at_close", False))
        if direction == 0:
            counters["zero signal"] += 1
            continue
        sim = simulate(bars, vc, ctx.releases, [(p_in, direction), (p_out, 0)], locks=locks)
        if not sim.ok:
            counters[sim.reason or "excluded"] += 1
            continue
        counters["uncalibrated bucket"] += int(sim.uncalibrated)
        counters["no new positions (Topstep)"] += int(info["entry_no_new"])
        counters[FLAT_DIAG] += flat_fill_bars(bars, sim)
        units.append(Unit(p, d, direction, sim, info))
    counters["diag: limit period pending or absent (fills)"] += locks.pending
    return units


DESCRIPTIVE = {
    "H1": {"without_S_after_1508 (F-14)": lambda u: not u.info["after_1508"],
           "topstep_without_no_new_positions (F-07)": lambda u: not u.info["entry_no_new"]},
    "H4": {"without_uncalibrated_bucket (F-13)": lambda u: not u.sim.uncalibrated,
           "topstep_without_no_new_positions (F-07)": lambda u: not u.info["entry_no_new"]},
}


def _pool(units: list[Unit], keep) -> dict:  # noqa: ANN001
    pooled: dict[str, dict] = {c: {} for c in K.COST_CASES}
    for u in units:
        if u.status == TRADED and keep(u):
            for c in K.COST_CASES:
                pooled[c].setdefault(u.unit_date, []).append(u.net_ru(c))
    return {c: sorted((d, sum(v) / len(v)) for d, v in pooled[c].items()) for c in K.COST_CASES}


def run_intraday(test: str, ctx: RunContext, products: tuple[str, ...] = K.PRODUCTS
                 ) -> RunOutput:
    if test not in K.INTRADAY_TESTS:
        raise ValueError(f"{test} is not an intraday test")
    counters: Counter = Counter()
    per_product: dict[str, Counter] = {}
    eligible: set[date] = set()
    rows, pooled, notes, kept = [], {c: {} for c in K.COST_CASES}, {}, []
    for p in products:
        c_p: Counter = Counter()
        bars = load_or_exclude(ctx, p, c_p, notes)
        units = [] if bars is None else product_units(test, ctx, p, bars, c_p, eligible)
        del bars
        scale_units(units, c_p)
        for u in units:
            rows.append(unit_row(u))
            if u.status != TRADED:
                continue
            kept.append(u)
            for c in K.COST_CASES:
                pooled[c].setdefault(u.unit_date, []).append(u.net_ru(c))
        per_product[p] = c_p
        counters.update(c_p)
    series = {c: sorted((d, sum(v) / len(v)) for d, v in pooled[c].items())
              for c in K.COST_CASES}
    daily = {c: dict(s) for c, s in series.items()}
    traded_per_date = {d: len(v) for d, v in pooled[K.BASE].items()}
    notes["products_traded_per_date_mean"] = (sum(traded_per_date.values())
                                              / max(len(traded_per_date), 1))
    notes["descriptive"] = {name: {"marked": "DESCRIPTIVE, never part of the pass bar",
                                   "stats": stats_for_test(test, _pool(kept, keep))}
                            for name, keep in DESCRIPTIVE[test].items()}
    return RunOutput(test, series, daily, eligible, counters, per_product, rows, notes)


__all__ = ["candidate", "product_units", "run_intraday"]
