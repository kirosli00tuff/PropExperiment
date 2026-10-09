"""CALENDAR-ONLY count mode: the candidate units per test, key and year that the calendars, the
windows, the settlement table and an ESTIMATED roll blackout allow, with no bar (for the power
table). Stated assumptions (power_table.md repeats them):
- roll blackout: 3 trade dates per roll (the splice and the two before), splices ESTIMATED from
  each product's listed contract cycle (``CYCLES``; the full listed cycle, an upper bound on the
  volume roll's count): equity and FX on the contract month's third Friday minus 8 days, every
  other product on the 5th-last trade date of the month before each listed month;
- early halts, unsourced dates and the day-session open intervals from the frozen calendars; a
  required minute outside its trade date's open intervals is "missing bar (calendar)";
- missing bars inside the session: 0; zero signals: 0 (neither is knowable without bars).
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from datetime import date, timedelta

from base_rules import constants as K
from base_rules.common import RunContext, action_exclusion, reference_exclusion
from base_rules.h2 import months
from base_rules.h3 import windows

NS_MIN = 60_000_000_000
QUARTERLY = (3, 6, 9, 12)
CYCLES: Mapping[str, tuple[int, ...]] = {
    **{p: QUARTERLY for p in ("NQ", "RTY", "YM", "ZT", "ZF", "ZN", "TN", "ZB", "UB", "6E", "6A",
                              "6B", "6C", "6J", "6S", "6N")},
    "CL": tuple(range(1, 13)), "NG": tuple(range(1, 13)), "GC": (2, 4, 6, 8, 10, 12),
    "HG": (3, 5, 7, 9, 12), "ZC": (3, 5, 7, 9, 12), "ZW": (3, 5, 7, 9, 12),
    "ZS": (1, 3, 5, 7, 8, 9, 11), "ZM": (1, 3, 5, 7, 8, 9, 10, 12),
    "ZL": (1, 3, 5, 7, 8, 9, 10, 12), "HE": (2, 4, 5, 6, 7, 8, 10, 12), "LE": (2, 4, 6, 8, 10, 12)}


def estimated_splices(ctx: RunContext, p: str) -> list[date]:
    cal = ctx.cal(p)
    by_month: dict[tuple[int, int], list[date]] = {}
    for x in cal.trade_dates():
        by_month.setdefault((x.year, x.month), []).append(x)
    out = []
    for year in range(2010, 2025):
        for month in CYCLES[p]:
            if K.GROUP_OF[p] in ("equity", "fx"):
                first = date(year, month, 1)
                fri = first + timedelta(days=(4 - first.weekday()) % 7 + 14)
                d = cal.previous(fri - timedelta(days=7))
            else:
                prev = date(year, month, 1) - timedelta(days=1)
                in_month = by_month.get((prev.year, prev.month), [])
                d = in_month[-5] if len(in_month) >= 5 else None
            if d is not None:
                out.append(d)
    return out


def estimated_blackout(ctx: RunContext, p: str) -> frozenset[date]:
    cal = ctx.cal(p)
    out = set()
    for s in estimated_splices(ctx, p):
        out.add(s)
        for k in (1, 2):
            prev = cal.offset(s, -k)
            if prev is not None:
                out.add(prev)
    return frozenset(out)


class _CalendarBars:
    """Stands in for ProductBars in action_exclusion: only the estimated blackout."""

    def __init__(self, blackout: frozenset[date]) -> None:
        self.blackout = blackout


def in_session(ctx: RunContext, p: str, day: date, minute: int) -> bool:
    return ctx.in_session(p, day, minute)


def settle_ok(ctx: RunContext, p: str, day: date) -> bool:
    """R-B1 (a): the settlement point's bar can exist (bar S, or bar S-1 at a closure)."""
    s = int(ctx.settlement.settle_minute(p, day))
    return ctx.in_session(p, day, s - 1 if ctx.closure_at(p, day, s) else s)


def entry_why(ctx: RunContext, p: str, day: date, minute: int) -> str | None:
    """R-B1 (b): None when an entry bar can exist at ``minute`` (or after the closure there)."""
    if ctx.closure_at(p, day, minute):
        return None if ctx.reopen_ns(p, day, minute) is not None else "no entry bar"
    return None if ctx.in_session(p, day, minute) else "missing bar (calendar)"


def _intraday(test: str, ctx: RunContext, p: str, bars: _CalendarBars, c: Counter
              ) -> list[date]:
    st, w, out = ctx.settlement, K.H1_WINDOW_MIN, []
    for d in ctx.window_dates(p):
        why = action_exclusion(ctx, bars, p, d)  # type: ignore[arg-type]
        if not why and not ctx.listed(p, d):
            why = "not listed"
        if not why and not st.sourced(p, d):
            why = "settlement unsourced"
        s, o = (st.settle_minute(p, d) or 0), (ctx.open_minute(p, d) or 0)
        if not why and ((test == "H1" and not s - w > o)
                        or (test == "H4" and not o + 1 < s - w - 1)):
            why = "window before open"
        ref = ctx.cal(p).previous(d)
        if not why:
            why = reference_exclusion(ctx, p, ref)
        if not why and ref is not None and not ctx.listed(p, ref):
            why = "no reference"
        if not why and ref is not None:
            sr = int(st.settle_minute(p, ref))
            ref_ok = in_session(ctx, p, ref, sr - 1) if test == "H1" else (
                in_session(ctx, p, ref, sr - w) and settle_ok(ctx, p, ref))
            if not st.sourced(p, ref) or not ref_ok:
                why = "no reference"
        if not why:
            need = [s - w - 1, s - w] if test == "H1" else [o + 1, s - w - 1]
            if not all(in_session(ctx, p, d, m) for m in need) or (
                    test == "H1" and not settle_ok(ctx, p, d)):
                why = "missing bar (calendar)"
        c[(why or "eligible").split(" (")[0] if why != "missing bar (calendar)" else why] += 1
        if not why:
            out.append(d)
    return out


def _per_year(dates: list[date]) -> dict[str, int]:
    out: dict[str, int] = {}
    for d in dates:
        out[str(d.year)] = out.get(str(d.year), 0) + 1
    return dict(sorted(out.items()))


def calendar_counts(ctx: RunContext) -> dict:
    """Per test: per-key exclusions, eligible units per year, and the unit dates per year after
    warm-up (the power table's input)."""
    blackout = {p: _CalendarBars(estimated_blackout(ctx, p)) for p in K.PRODUCTS}
    res: dict = {}
    eligible_dates: dict[str, set[date]] = {}
    for test in K.INTRADAY_TESTS:
        per_key, pooled = {}, set()
        for p in K.PRODUCTS:
            c: Counter = Counter()
            dates = _intraday(test, ctx, p, blackout[p], c)
            eligible_dates.setdefault(test, set()).update(dates)
            traded = dates[K.WARMUP_UNITS:]
            pooled.update(traded)
            per_key[p] = {"exclusions": dict(c), "eligible_per_year": _per_year(dates),
                          "traded_per_year": _per_year(traded)}
        res[test] = {"per_key": per_key, "units_per_year": _per_year(sorted(pooled))}
    res["H2"], open2 = _h2(ctx, blackout)
    res["H3"], open3 = _h3(ctx, blackout)
    grid = sorted(eligible_dates.get("H1", set()) | eligible_dates.get("H4", set()) | open2
                  | open3)
    res["H5"] = {"grid_dates": len(grid), "units_per_year": _per_year(grid[K.H5_WARMUP:])}
    return res


def _h2(ctx: RunContext, blackout: Mapping) -> tuple[dict, set[date]]:
    st, c, units, open_dates = ctx.settlement, Counter(), [], set()
    for ref, d5, d_last in months(ctx):
        if d_last > ctx.last or d5 < min(ctx.starts[x] for x in K.H2_LEGS):
            continue
        if not all(ctx.listed(x, d) for x in K.H2_LEGS
                   for d in (d5, d_last) + ((ref,) if ref is not None else ())):
            c["not listed"] += 1
            continue
        dec = max(st.settle_minute(x, d5) for x in K.H2_LEGS)
        why = None
        for x in K.H2_LEGS:
            why = why or next((w for w in (action_exclusion(ctx, blackout[x], x, d)
                                           for d in (d5, d_last)) if w), None)
            why = why or reference_exclusion(ctx, x, ref)
            if not why and ref is not None and not (
                    in_session(ctx, x, ref, st.settle_minute(x, ref) - 1)
                    and in_session(ctx, x, d5, st.settle_minute(x, d5) - 1)
                    and settle_ok(ctx, x, d_last)):
                why = "missing bar (calendar)"
            if not why:
                why = entry_why(ctx, x, d5, dec)
        if not why and ((d5 <= K.HIST_LAST < d_last)
                        or any(K.HIST_LAST < d < K.STEP2_FIRST for d in (d5, d_last))):
            why = "store boundary"
        c[(why or "eligible").split(" (")[0]] += 1
        if not why:
            c["entry after closure"] += int(any(ctx.closure_at(x, d5, dec) for x in K.H2_LEGS))
            units.append((d5, d_last))
    traded = units[K.WARMUP_UNITS:]
    for d5, d_last in traded:
        cal, d = ctx.cal(K.H2_EQUITY), d5
        while d is not None and d <= d_last:
            open_dates.add(d)
            d = cal.offset(d, 1)
    return ({"exclusions": dict(c), "eligible_per_year": _per_year([u[1] for u in units]),
             "units_per_year": _per_year([u[1] for u in traded])}, open_dates)


def _h3(ctx: RunContext, blackout: Mapping) -> tuple[dict, set[date]]:
    st, c = ctx.settlement, Counter()
    kept = windows(ctx, ctx.auctions, c)
    by_tenor: dict[str, list] = {}
    for a, before, t, after in kept:
        why = next((w for w in (action_exclusion(ctx, blackout[a.root], a.root, d)
                                for d in (before, t, after)) if w), None)
        if not why and not all(ctx.listed(a.root, d) for d in (before, t, after)):
            why = "not listed"
        if not why and not (settle_ok(ctx, a.root, t) and settle_ok(ctx, a.root, after)):
            why = "missing bar (calendar)"
        if not why:
            why = (entry_why(ctx, a.root, before, int(st.settle_minute(a.root, before)))
                   or entry_why(ctx, a.root, t, int(st.settle_minute(a.root, t))))
        if not why and ((before <= K.HIST_LAST < after)
                        or any(K.HIST_LAST < d < K.STEP2_FIRST for d in (before, after))):
            why = "store boundary"
        c[(why or "eligible").split(" (")[0]] += 1
        if not why:
            c["entry after closure"] += int(any(
                ctx.closure_at(a.root, d, int(st.settle_minute(a.root, d))) for d in (before, t)))
            by_tenor.setdefault(a.tenor, []).append((t, before, after, a.root))
    traded = [u for us in by_tenor.values() for u in us[K.WARMUP_UNITS:]]
    open_dates: set[date] = set()
    for _t, before, after, root in traded:
        d = before
        while d is not None and d <= after:
            open_dates.add(d)
            d = ctx.cal(root).offset(d, 1)
    return ({"exclusions": dict(c),
             "eligible_per_tenor": {k: len(v) for k, v in sorted(by_tenor.items())},
             "units_per_year": _per_year(sorted(u[0] for u in traded))}, open_dates)


__all__ = ["CYCLES", "calendar_counts", "entry_why", "estimated_blackout", "estimated_splices",
           "in_session", "settle_ok"]
