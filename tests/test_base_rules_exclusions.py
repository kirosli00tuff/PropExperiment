"""Exclusion counters on small hand-built calendars (lead_spec section 2): roll blackout, early
close, unsourced date, missing bar, no reference, settlement unsourced (lead grade), not listed,
window end, store boundary, same-tenor overlap, auction not a trade date."""

from __future__ import annotations

from collections import Counter
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from base_rules import constants as K
from base_rules.auctions import Auction
from base_rules.h3 import run_h3
from base_rules.intraday import product_units
from tests._base_rules_fixtures import (
    calendars,
    context,
    early_halt,
    hist_payload,
    intraday_world,
    make_bars,
    ns,
    settlement,
    trade_dates,
)

START, END = date(2016, 2, 1), date(2016, 4, 29)
ANN = date(2017, 2, 1)  # an announcement long before t-3
HALT, UNSOURCED = date(2016, 3, 10), date(2016, 3, 15)
BLACKOUT, NO_S30 = date(2016, 3, 22), date(2016, 3, 29)


def _nq_settle() -> list[dict]:
    rows = [("2010-06-07", "2016-04-10", "15:00", "primary"),
            ("2016-04-11", "2016-04-15", "15:00", "weak"),
            ("2016-04-16", "2016-04-19", "15:00", "secondary"),
            ("2016-04-20", "2016-04-22", None, "primary"),
            ("2016-04-23", "2024-02-29", "15:00", "primary")]
    return [{"from": a, "to": b, "minute_ct": m, "grade": "primary", "lead_grade": g}
            for a, b, m, g in rows]


def _ct_minute(ts_ns: int) -> int:
    t = datetime.fromtimestamp(ts_ns / 1e9, tz=UTC).astimezone(ZoneInfo("America/Chicago"))
    return t.hour * 60 + t.minute


def _world():  # noqa: ANN202
    payload = hist_payload("equity", entries=[early_halt(HALT)], unsourced=[UNSOURCED])
    cals = calendars(("equity",), {"equity": payload})
    days = trade_dates(cals["equity"], START, END)
    bars = intraday_world("NQ", days, h1_edge=5.0, h4_edge=0.0, noise=3.0, seed=1)
    s30 = ns(NO_S30, 15 * 60 - 30)
    rows = [(date.fromordinal(int(bars.td[k])), _ct_minute(int(bars.ts[k])),
             int(bars.open_t[k]), int(bars.close_t[k]), "C1")
            for k in range(len(bars.ts)) if int(bars.ts[k]) != s30]  # drop one S-30 bar
    bars = make_bars("NQ", rows, blackout=[BLACKOUT])
    st = settlement(overrides={"NQ": _nq_settle()})
    ctx = context(cals, {"NQ": bars}, st=st, starts={"NQ": START})
    ctx.last = END
    return ctx, bars


def test_h1_exclusions_are_counted_by_reason() -> None:
    ctx, bars = _world()
    c: Counter = Counter()
    eligible: set[date] = set()
    product_units("H1", ctx, "NQ", bars, c, eligible)
    assert c["roll blackout"] == 1
    assert c["early halt"] == 1
    assert c["unsourced calendar date"] == 1
    assert c["missing bar"] == 1
    assert c["settlement unsourced"] == 5  # 04-11..04-15, lead grade weak
    assert c["not listed"] == 3  # 04-20..04-22, minute_ct null
    # references: 02-01 (prior 01-29 outside the window), 03-11 (halt), 03-16 (unsourced),
    # 04-18 (prior 04-15 weak), 04-25 (prior 04-22 not listed)
    assert c["no reference"] == 5
    assert c["no reference (outside window)"] == 1 and c["no reference (early halt)"] == 1
    assert c["no reference (unsourced)"] == 1
    assert c["no reference (settlement unsourced)"] == 1 and c["no reference (not listed)"] == 1
    assert date(2016, 3, 23) in eligible  # a blackout date is a valid reference
    assert date(2016, 3, 30) in eligible
    days = trade_dates(ctx.cal("NQ"), START, END)
    assert c["eligible"] == len(days) - 1 - 1 - 1 - 1 - 5 - 3 - 5
    assert c["outside window"] == len([d for d in ctx.cal("NQ").trade_dates()
                                       if K.PROMPT_FIRST <= d < START])


def test_h3_calendar_exclusions_are_counted() -> None:
    cals = calendars(("rates",))
    auctions = [
        Auction("A", "10Y", "ZN", date(2017, 3, 8), "", ANN),
        Auction("B", "10Y", "ZN", date(2017, 3, 10), "", ANN),  # overlaps A's [t-3, t+5]
        Auction("C", "5Y", "ZF", date(2017, 3, 9), "", date(2017, 3, 6)),  # announced ON t-3
        Auction("D", "30Y", "ZB", date(2017, 3, 11), "", ANN),  # a Saturday
        Auction("E", "2Y", "ZT", date(2024, 2, 27), "", date(2024, 2, 1)),  # t+5 > 2024-02-29
        Auction("F", "30Y", "ZB", date(2019, 5, 1), "", date(2019, 4, 1)),  # spans the boundary
        Auction("G", "2Y", "ZT", date(2017, 4, 24), "", date(2017, 4, 20)),  # after t-3 (04-19)
        Auction("H", "5Y", "ZF", date(2017, 4, 25), ""),  # no announcement date on file
        # I: same tenor as A and overlapping it, but not counted (announced after its t-3), so
        # it neither trades nor blocks; the overlap rule runs among the counted auctions only
        Auction("I", "10Y", "ZN", date(2017, 3, 7), "", date(2017, 3, 6)),
    ]
    bars = {r: make_bars(r, [(date(2017, 3, 1), 840, 1, 1, "C")]) for r in ("ZN", "ZF", "ZB")}
    out = run_h3(context(cals, bars, auctions=auctions))
    c = out.counters
    assert c["same-tenor overlap"] == 1
    assert c["auction not a trade date"] == 1
    assert c["announced after entry"] == 2 and c["no announcement date"] == 1
    assert c["window end"] == 1
    assert c["store boundary"] == 1
    assert c["missing bar"] == 2  # A and C: no bar at their settlement minutes
    assert not out.units[K.BASE]
