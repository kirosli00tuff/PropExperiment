"""Rebalance dates, references, lookbacks, the T1/T2 signals, the divisor S_M and the T3 units
(lead_spec sections 3, 4, 5).

Eligibility is asked of an ``Oracle``: ``BarOracle`` answers from a root's loaded bars (the run),
``CalendarOracle`` from the calendars and the settlement table alone (the calendar-only counts:
a required bar is assumed present when its minute lies inside the trade date's open intervals).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date, timedelta

from base_rules.common import RunContext, action_exclusion, reference_exclusion
from base_rules.counts import in_session, settle_ok
from base_rules.h2 import chained_return
from base_rules.store import ProductBars
from base_rules.touch import settle_ns
from multiday import constants as K
from multiday.daily import Mark, chain_prices, era_of, ps_index

Month = tuple[int, int]


def month_add(m: Month, k: int) -> Month:
    n = m[0] * 12 + (m[1] - 1) + k
    return (n // 12, n % 12 + 1)


def month_of(d: date) -> Month:
    return (d.year, d.month)


def by_month(dates: Sequence[date]) -> dict[Month, list[date]]:
    out: dict[Month, list[date]] = {}
    for d in dates:
        out.setdefault(month_of(d), []).append(d)
    return out


# ------------------------------------------------------------------ oracles ----
class BarOracle:
    """Answers from the loaded bars: MK exists (marks), PS exists, the MK bar's open instant."""

    def __init__(self, ctx: RunContext, bars: ProductBars, root: str, marks: Sequence[Mark]):
        self.ctx, self.bars, self.root = ctx, bars, root
        self.blackout = bars.blackout
        self.marks = {m.day: m for m in marks}

    def has_mark(self, d: date) -> bool:
        return d in self.marks

    def has_ps(self, d: date) -> bool:
        return self.ctx.listed(self.root, d) and ps_index(self.ctx, self.bars, self.root, d) \
            is not None

    def mark_ts(self, d: date) -> int:
        return self.marks[d].ts


class CalendarOracle:
    """Calendar-only: bars assumed present inside the trade date's open intervals; the roll
    blackout from the stores' metadata (no row read)."""

    def __init__(self, ctx: RunContext, root: str, blackout: frozenset[date]):
        self.ctx, self.root, self.blackout = ctx, root, blackout

    def has_mark(self, d: date) -> bool:
        return self.ctx.listed(self.root, d) and settle_ok(self.ctx, self.root, d)

    def has_ps(self, d: date) -> bool:
        if not self.ctx.listed(self.root, d):
            return False
        return in_session(self.ctx, self.root, d,
                          int(self.ctx.settlement.settle_minute(self.root, d)) - 1)

    def mark_ts(self, d: date) -> int:
        return settle_ns(self.ctx, self.root, d)


def action_why(ctx: RunContext, oracle, root: str, d: date) -> str | None:  # noqa: ANN001
    """Why ``d`` is not an eligible action date (spec 3): base_rules' action exclusion, listed,
    MK and PS present, the MK fill point outside every D9.5a guard window."""
    why = action_exclusion(ctx, oracle, root, d)  # type: ignore[arg-type]
    if why:
        return why
    if not ctx.listed(root, d):
        return "not listed"
    if not oracle.has_mark(d):
        return "missing bar (mark)"
    if not oracle.has_ps(d):
        return "missing bar (signal)"
    if ctx.releases.guard(root, oracle.mark_ts(d)):
        return "fill guard"
    return None


def reference_why(ctx: RunContext, oracle, root: str, d: date) -> str | None:  # noqa: ANN001
    why = reference_exclusion(ctx, root, d)
    if why:
        return why
    if not oracle.has_ps(d):
        return "no reference (missing bar)"
    return None


# ------------------------------------------------------------------ rebalance dates ----
@dataclass
class Rebalance:
    month: Month
    e: date  # the month's last trade date on the group calendar
    d_star: date | None
    skipped: list[tuple[date, str]] = field(default_factory=list)  # later dates, why skipped
    refs: dict[int, date | None] = field(default_factory=dict)
    ref_why: dict[int, str] = field(default_factory=dict)


def rebalances(ctx: RunContext, oracle, root: str) -> list[Rebalance]:  # noqa: ANN001
    """Per month M whose last trade date lies in the root's window: d*(i, M), the latest eligible
    date among the month's last 6 trade dates (None: no eligible rebalance date), and the
    references of the k-month lookbacks."""
    months = by_month(ctx.cal(root).trade_dates())
    out = []
    for m in sorted(months):
        ds = months[m]
        e = ds[-1]
        if not ctx.in_window(root, e):
            continue
        rb = Rebalance(m, e, None)
        for d in reversed(ds[-K.REBALANCE_LAST_DATES:]):
            why = action_why(ctx, oracle, root, d)
            if why is None:
                rb.d_star = d
                break
            rb.skipped.append((d, why))
        for k in K.LOOKBACKS:
            prev = months.get(month_add(m, -k), [])
            rb.refs[k] = None
            last_why = "no reference (no trade date)"
            for d in reversed(prev[-K.REFERENCE_LAST_DATES:]):
                why = reference_why(ctx, oracle, root, d)
                if why is None:
                    rb.refs[k] = d
                    break
                last_why = why
            if rb.refs[k] is None:
                rb.ref_why[k] = last_why
        out.append(rb)
    return out


def first_eligible_after(ctx: RunContext, oracle, root: str, after: date  # noqa: ANN001
                         ) -> date | None:
    """The first eligible action date after ``after`` in the same store era and the window."""
    for d in ctx.window_dates(root):
        if d <= after:
            continue
        if era_of(d) != era_of(after):
            return None
        if action_why(ctx, oracle, root, d) is None:
            return d
    return None


# ------------------------------------------------------------------ lookbacks and signals ----
def sign(x: float) -> int:
    return (x > 0) - (x < 0)


def lookback(ctx: RunContext, chain_bars: ProductBars, root: str, ref: date, d: date,
             boundary_ts: int | None, counters: Counter) -> tuple[float | None, str]:
    """R_k: base_rules.h2.chained_return from PS(ref) to PS(d) on the boundary-split bars."""
    i_ref, i_d = ps_index(ctx, chain_bars, root, ref), ps_index(ctx, chain_bars, root, d)
    if i_ref is None or i_d is None:
        return None, "missing bar"
    if min(chain_prices(chain_bars, (i_ref, True), (i_d, True))) <= 0:
        return None, "non-positive price"  # R-B3: undefined and counted, never raised
    if boundary_ts is not None and int(chain_bars.ts[i_ref]) < boundary_ts <= \
            int(chain_bars.ts[i_d]):
        counters["lookbacks split at the store boundary"] += 1
    return chained_return(chain_bars, i_ref, i_d)


def t1_signal(r12: float | None) -> int | None:
    return None if r12 is None else sign(r12)


def t2_signal(r1: float | None, r3: float | None, r12: float | None) -> float | None:
    """The trend blend: the mean of the three signs; any undefined lookback: no signal."""
    if r1 is None or r3 is None or r12 is None:
        return None
    return (sign(r1) + sign(r3) + sign(r12)) / 3.0


# ------------------------------------------------------------------ the divisor S_M ----
def divisor_table(ctx: RunContext, roots: Sequence[str]) -> dict[Month, int]:
    """S_M for every month M (spec 4, calendar-defined, no data): the number of roots i whose
    e(i, M - 12), the last trade date of month M - 12 on i's group calendar, lies inside i's
    window. A root counted here whose signal or sigma is undefined holds zero."""
    out: dict[Month, int] = {}
    for r in roots:
        for m, ds in by_month(ctx.cal(r).trade_dates()).items():
            if ctx.in_window(r, ds[-1]):
                key = month_add(m, K.DIVISOR_LOOKBACK)
                out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


# ------------------------------------------------------------------ T3 units ----
@dataclass
class TomUnit:
    root: str
    month: Month
    entry: date | None  # day -2
    exit: date | None  # day +3
    why: str | None  # None: eligible (counted in S_u)
    days: dict[int, date | None] = field(default_factory=dict)  # -2, -1, +1, +2, +3


def _observed(day: date) -> date:
    """Saturday -> Friday, Sunday -> Monday."""
    if day.weekday() == 5:
        return day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    last = nxt - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def nyse_closures(year: int) -> frozenset[date]:
    """NYSE full-day closures of ``year`` by rule (lead_spec A12): New Year's Day (Sunday ->
    Monday; Saturday -> no closure), MLK Day, Presidents Day, Good Friday, Memorial Day,
    Juneteenth (from 2022), Independence Day, Labor Day, Thanksgiving, Christmas (Saturday ->
    Friday, Sunday -> Monday), and the special closures in constants."""
    from dateutil.easter import easter

    ny = date(year, 1, 1)
    out = set() if ny.weekday() == 5 else {_observed(ny)}
    out |= {_nth_weekday(year, 1, 0, 3), _nth_weekday(year, 2, 0, 3),
            easter(year) - timedelta(days=2), _last_weekday(year, 5, 0),
            _observed(date(year, 7, 4)), _nth_weekday(year, 9, 0, 1),
            _nth_weekday(year, 11, 3, 4), _observed(date(year, 12, 25))}
    if year >= K.NYSE_JUNETEENTH_FIRST_YEAR:
        out.add(_observed(date(year, 6, 19)))
    out |= {d for d in K.NYSE_SPECIAL_CLOSURES if d.year == year}
    return frozenset(out)


def t3_trading_days(ctx: RunContext, root: str) -> list[date]:
    """The group calendar's trade dates that are not NYSE full-day closures (lead_spec A12)."""
    cache: dict[int, frozenset[date]] = {}
    out = []
    for d in ctx.cal(root).trade_dates():
        if d.year not in cache:
            cache[d.year] = nyse_closures(d.year)
        if d not in cache[d.year]:
            out.append(d)
    return out


def tom_units(ctx: RunContext, oracle, root: str) -> list[TomUnit]:  # noqa: ANN001
    """Per month M from the root's window start: days -2, -1 (the month's last two T3 trading
    days) and +1, +2, +3 (month M + 1's first three), numbered on T3 trading days (A12), and the
    unit's eligibility (spec 5): window, window end, store boundary, entry (day -2) and exit
    (day +3) eligible action dates (section 3)."""
    months = by_month(t3_trading_days(ctx, root))
    first = month_of(ctx.starts[root])
    out = []
    for m in sorted(months):
        if m < first or m > month_of(K.WINDOW_LAST):
            continue
        ds, nxt = months[m], months.get(month_add(m, 1), [])
        days = {-2: ds[-2] if len(ds) >= 2 else None, -1: ds[-1] if ds else None,
                **{k: nxt[k - 1] if len(nxt) >= k else None for k in (1, 2, 3)}}
        entry = days[-K.TOM_ENTRY_FROM_END]
        exit_ = days[K.TOM_EXIT_DAY]
        why = _tom_why(ctx, oracle, root, entry, exit_)
        out.append(TomUnit(root, m, entry, exit_, why, days))
    return out


def _tom_why(ctx: RunContext, oracle, root: str, entry: date | None,  # noqa: ANN001
             exit_: date | None) -> str | None:
    if entry is None or not ctx.in_window(root, entry):
        return "outside window"
    if exit_ is None or exit_ > K.WINDOW_LAST:
        return "window end"
    if era_of(entry) != era_of(exit_) or era_of(entry) is None:
        return "store boundary"
    for d, tag in ((entry, "entry"), (exit_, "exit")):
        why = action_why(ctx, oracle, root, d)
        if why:
            return f"{tag}: {why}"
    return None


def divisor_su(units: Mapping[str, Sequence[TomUnit]]) -> dict[Month, int]:
    """S_u per month: the roots with an eligible unit (calendar and bar existence; spec 5)."""
    out: dict[Month, int] = {}
    for us in units.values():
        for u in us:
            if u.why is None:
                out[u.month] = out.get(u.month, 0) + 1
    return out


__all__ = ["BarOracle", "CalendarOracle", "Month", "Rebalance", "TomUnit", "action_why",
           "by_month", "divisor_su", "divisor_table", "first_eligible_after", "lookback",
           "month_add", "month_of", "nyse_closures", "rebalances", "reference_why", "sign",
           "t1_signal", "t2_signal", "t3_trading_days", "tom_units"]
