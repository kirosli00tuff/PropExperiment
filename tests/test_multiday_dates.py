"""multiday.signals and the T1/T2/T3 schedules: month-end rebalance dates (a blackout moving the
rebalance earlier, the 6-date limit and its close-out, the February 2024 close-out, the April 2019
flat month), references, the 12-month lookback over several splices, turn-of-month dates across
month and year ends and holidays, and the calendar-defined divisor S_M."""

from __future__ import annotations

from collections import Counter
from datetime import date, timedelta

import pytest

from base_rules.h2 import chained_return
from multiday import constants as K
from multiday.book import process_root, t3_orders, t12_orders
from multiday.signals import (
    CalendarOracle,
    divisor_su,
    divisor_table,
    nyse_closures,
    rebalances,
    t2_signal,
    t3_trading_days,
    tom_units,
)
from tests._base_rules_fixtures import closure, early_halt, group_calendars, hist_payload
from tests.test_multiday_world import (
    all_cals,
    ctx_for,
    walk_prices,
    window,
    world_bars,
)

S = 15 * 60


@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return all_cals()


def _rb(rbs, month):  # noqa: ANN001, ANN202
    return next(rb for rb in rbs if rb.month == month)


def test_the_rebalance_is_the_months_last_trade_date(cals) -> None:
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 4, 29))
    bars = world_bars("NQ", days, lambda d: 1000)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rb = _rb(rebalances(ctx, CalendarOracle(ctx, "NQ", frozenset()), "NQ"), (2016, 3))
    assert rb.e == date(2016, 3, 31) and rb.d_star == rb.e and rb.skipped == []


def test_a_blackout_moves_the_rebalance_earlier_and_six_dates_is_the_limit(cals) -> None:
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 5, 31))
    march = [d for d in days if d.month == 3]
    two = march[-2:]
    ctx = ctx_for(cals, {}, starts={"NQ": days[0]})
    rb = _rb(rebalances(ctx, CalendarOracle(ctx, "NQ", frozenset(two)), "NQ"), (2016, 3))
    assert rb.d_star == march[-3]
    assert rb.skipped == [(march[-1], "roll blackout"), (march[-2], "roll blackout")]
    six = frozenset(march[-6:])
    rb6 = _rb(rebalances(ctx, CalendarOracle(ctx, "NQ", six), "NQ"), (2016, 3))
    assert rb6.d_star is None and len(rb6.skipped) == K.REBALANCE_LAST_DATES
    five = frozenset(march[-5:])
    assert _rb(rebalances(ctx, CalendarOracle(ctx, "NQ", five), "NQ"), (2016, 3)).d_star == \
        march[-6]


def test_no_eligible_date_closes_at_the_first_eligible_date_after_month_end(cals) -> None:
    days = window(cals["equity"], date(2014, 1, 2), date(2016, 6, 30))
    march = [d for d in days if d.month == 3 and d.year == 2016]
    px = walk_prices(days, drift=0.002, vol=0.004, seed=3)
    bars = world_bars("NQ", days, px.__getitem__, blackout=march[-6:])
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = process_root(ctx, bars, "NQ")
    c: Counter = Counter()
    orders = t12_orders(rd, "T1", divisor_table(ctx, ["NQ"]), c)
    close = next(o for o in orders if o.kind.startswith("close"))
    assert close.day == date(2016, 4, 1) and close.target == 0.0
    in_data = [rb for rb in rd.rebalances if rb.e <= days[-1]]
    assert [rb.month for rb in in_data if rb.d_star is None] == [(2016, 3)]
    assert c["no eligible rebalance date"] >= 1
    feb = next(o for o in orders if o.info.get("month") == "2016-02")
    assert feb.target > 0  # an up-trend: long


def test_the_february_2024_rebalance_closes_every_position(cals) -> None:
    days = window(cals["equity"], date(2022, 6, 1), date(2024, 2, 29))
    px = walk_prices(days, drift=0.002, vol=0.004, seed=4)
    bars = world_bars("NQ", days, px.__getitem__)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = process_root(ctx, bars, "NQ")
    orders = t12_orders(rd, "T2", divisor_table(ctx, ["NQ"]), Counter())
    last = orders[-1]
    assert last.info["month"] == "2024-02" and last.target == 0.0
    assert last.day == date(2024, 2, 29)
    assert orders[-2].info["month"] == "2024-01" and orders[-2].target > 0


def test_april_2019_is_flat_and_may_2019_reopens(cals) -> None:
    hist = [d for d in window(cals["equity"], date(2017, 1, 3), date(2019, 4, 30))]
    step = window(cals["equity"], date(2019, 5, 6), date(2019, 7, 31))
    days = hist + step
    px = walk_prices(days, drift=0.002, vol=0.004, seed=5)
    sym = lambda d: "M9" if d <= date(2019, 4, 30) else "U9"  # noqa: E731
    bars = world_bars("NQ", days, px.__getitem__, sym)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = process_root(ctx, bars, "NQ")
    c: Counter = Counter()
    orders = {o.info.get("month"): o for o in t12_orders(rd, "T1", divisor_table(ctx, ["NQ"]),
                                                          c)}
    assert orders["2019-03"].target > 0 and orders["2019-04"].target == 0.0
    assert orders["2019-05"].target > 0  # the 12-month lookback split at the store boundary
    assert rd.counters["lookbacks split at the store boundary"] >= 1
    assert c["flat month 2019-04 (store boundary or window end)"] == 1


def test_a_reference_skips_an_early_halt_and_allows_a_blackout(cals) -> None:
    payload = hist_payload("equity", entries=[early_halt(date(2015, 3, 31))])
    cals2 = {**cals, "equity": group_calendars("equity", payload)}
    ctx = ctx_for(cals2, {}, starts={"NQ": date(2014, 1, 2)})
    oracle = CalendarOracle(ctx, "NQ", frozenset({date(2015, 3, 30)}))
    rb = _rb(rebalances(ctx, oracle, "NQ"), (2016, 3))
    assert rb.refs[12] == date(2015, 3, 30)  # the halt date skipped, the blackout date allowed
    assert rb.refs[1] == date(2016, 2, 29) and rb.refs[3] == date(2015, 12, 31)


def test_a_twelve_month_lookback_over_several_splices_is_the_product_of_segments(cals) -> None:
    days = window(cals["equity"], date(2015, 1, 2), date(2016, 3, 31))
    roll_days = [date(2015, 3, 12), date(2015, 6, 11), date(2015, 9, 17), date(2015, 12, 10)]
    names = ["H5", "M5", "U5", "Z5", "H6"]

    def sym(d: date) -> str:
        return names[sum(1 for r in roll_days if d >= r)]

    px = {d: 1000 + 7 * k + 50 * names.index(sym(d)) for k, d in enumerate(days)}
    bars = world_bars("NQ", days, px.__getitem__, sym, splices=roll_days)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = process_root(ctx, bars, "NQ")
    rb = _rb(rd.rebalances, (2016, 3))
    ref = rb.refs[12]
    assert ref == date(2015, 3, 31)
    i, j = bars.bar(ref, S - 1), bars.bar(rb.d_star, S - 1)
    want, k = 1.0, 0
    start = px[ref]
    for r in roll_days[1:]:  # the splices after the reference (2015-03-12 precedes it)
        prev = max(d for d in days if d < r)
        want *= px[prev] / start  # the old segment ends at the close of the last bar before
        start = px[r]  # the new one starts at the open of the first bar at or after
        k += 1
    want *= px[rb.d_star] / start
    assert k == 3
    assert rd.lookbacks[((2016, 3), 12)] == pytest.approx(want - 1)
    assert chained_return(bars, i, j)[0] == pytest.approx(want - 1)


def test_turn_of_month_dates_across_month_and_year_ends_and_holidays(cals) -> None:
    ctx = ctx_for(cals, {}, starts={"NQ": date(2019, 5, 6)})
    units = {u.month: u for u in tom_units(ctx, CalendarOracle(ctx, "NQ", frozenset()), "NQ")}
    eq = ctx.cal("NQ")
    u = units[(2019, 12)]
    assert (u.entry, u.exit) == (date(2019, 12, 30), date(2020, 1, 6))  # Jan 1 closed
    u = units[(2020, 12)]
    assert (u.entry, u.exit) == (date(2020, 12, 30), date(2021, 1, 6))
    t3_days = t3_trading_days(ctx, "NQ")
    for m, u in units.items():  # day -2: the month's SECOND-to-last T3 trading day (A8, A12)
        ds = [d for d in t3_days if (d.year, d.month) == m]
        assert u.entry == ds[-2] and u.entry != ds[-3] and u.days[-1] == ds[-1]
    assert set(t3_days) <= set(eq.trade_dates())
    assert units[(2024, 2)].why == "window end"  # day +3 in March 2024
    assert (2019, 4) not in units and units[(2019, 5)].why is None  # from the window month


def test_day_minus_two_straddling_a_holiday_is_the_second_to_last_trade_date() -> None:
    """Memorial Day 2016 closed (synthetic calendar): the month's last two trade dates are
    Friday 05-27 and Tuesday 05-31; day -2 is 05-27, not 05-26 (third-to-last, lead_spec A8)."""
    cals = {**all_cals(), "equity": group_calendars(
        "equity", hist_payload("equity", entries=[closure(date(2016, 5, 30))]))}
    ctx = ctx_for(cals, {}, starts={"NQ": date(2016, 1, 4)})
    u = next(u for u in tom_units(ctx, CalendarOracle(ctx, "NQ", frozenset()), "NQ")
             if u.month == (2016, 5))
    ds = [d for d in ctx.cal("NQ").trade_dates() if (d.year, d.month) == (2016, 5)]
    assert ds[-2:] == [date(2016, 5, 27), date(2016, 5, 31)]
    assert u.entry == date(2016, 5, 27) and u.entry != date(2016, 5, 26)
    assert u.exit == date(2016, 6, 3) and u.why is None
    gap = [ds[-2] + timedelta(days=k) for k in range(1, (ds[-1] - ds[-2]).days)]
    assert date(2016, 5, 30) in gap and not ctx.cal("NQ").is_trade_date(date(2016, 5, 30))


def test_the_april_may_2019_t3_unit_is_a_store_boundary_exclusion(cals) -> None:
    ctx = ctx_for(cals, {}, starts={"NQ": date(2018, 1, 2)})
    units = {u.month: u for u in tom_units(ctx, CalendarOracle(ctx, "NQ", frozenset()), "NQ")}
    assert units[(2019, 4)].why == "store boundary"
    assert units[(2019, 3)].why is None


def test_s_m_is_calendar_defined_from_each_roots_window() -> None:
    cals = all_cals()
    ctx = ctx_for(cals, {}, starts={"NQ": date(2010, 7, 1), "ZN": date(2015, 6, 1)})
    sm = divisor_table(ctx, ["NQ", "ZN"])
    assert sm[(2016, 5)] == 1 and sm[(2016, 6)] == 2 and sm[(2011, 7)] == 1
    assert (2011, 6) not in sm  # e(NQ, 2010-06) lies before NQ's window


def test_s_u_counts_date_eligible_units_before_the_sigma_check(cals) -> None:
    ctx = ctx_for(cals, {}, starts={"NQ": date(2019, 5, 6), "RTY": date(2019, 5, 6)})
    units = {r: tom_units(ctx, CalendarOracle(ctx, r, frozenset()), r) for r in ("NQ", "RTY")}
    su = divisor_su(units)
    assert su[(2020, 1)] == 2


def test_a_t3_unit_in_sigma_warm_up_is_excluded_and_not_in_s_u(cals) -> None:
    """Lead ruling Q2: RTY in warm-up while NQ is eligible -> S_u = 1 for NQ's unit."""
    nq_days = window(cals["equity"], date(2019, 5, 6), date(2020, 6, 30))
    rty_days = window(cals["equity"], date(2020, 1, 2), date(2020, 6, 30))
    bars = {"NQ": world_bars("NQ", nq_days, walk_prices(nq_days, drift=0.0, vol=0.01,
                                                         seed=1).__getitem__),
            "RTY": world_bars("RTY", rty_days, walk_prices(rty_days, drift=0.0, vol=0.01,
                                                           seed=2).__getitem__)}
    ctx = ctx_for(cals, bars, starts={"NQ": nq_days[0], "RTY": rty_days[0]})
    rd = {r: process_root(ctx, bars[r], r, with_tom=True) for r in ("NQ", "RTY")}
    rty = {u.month: u for u in rd["RTY"].tom}
    assert rty[(2020, 2)].why == "sigma warm-up"  # dates and bars eligible, sigma undefined
    su = divisor_su({r: rd[r].tom for r in ("NQ", "RTY")})
    assert su[(2020, 2)] == 1
    c: Counter = Counter()
    nq = next(o for o in t3_orders(rd["NQ"], su, c) if o.kind == "entry"
              and o.info["month"] == "2020-02")
    assert nq.info["S_u"] == 1
    assert nq.target == pytest.approx(K.TARGET_VOL / rd["NQ"].sigma[nq.day] / nq.info["V"])
    c_rty: Counter = Counter()
    assert not [o for o in t3_orders(rd["RTY"], su, c_rty) if o.info.get("month") == "2020-02"]
    assert c_rty["T3 unit excluded: sigma warm-up"] >= 1


def test_window_starts_take_the_latest_of_file_listing_and_le_dates(cals) -> None:
    """Lead ruling Q1: every purpose uses the latest of the windows file, R-S4 and R-S3; S_M
    counts RTY (and HE) from 2018-07: 15 in 2018-06, 17 from 2018-07."""
    from base_rules import constants as BK
    from multiday.run import e21_starts

    file_starts = {**{r: date(2010, 7, 1) for r in K.ROOTS}, "RTY": date(2017, 6, 1),
                   "TN": date(2016, 1, 1), "HE": date(2017, 7, 1)}
    starts = e21_starts(file_starts)
    assert starts["RTY"] == date(2017, 7, 10) and starts["TN"] == date(2016, 1, 11)
    assert starts["LE"] == date(2014, 12, 15) and starts["HE"] == date(2017, 7, 1)
    assert starts["NQ"] == date(2010, 7, 1)
    ctx = ctx_for(cals, {}, starts=starts)
    sm = divisor_table(ctx, K.ROOTS)
    assert sm[(2018, 6)] == 15 and sm[(2018, 7)] == 17 and sm[(2024, 2)] == 17
    assert sm[(2015, 12)] == 14 and sm[(2017, 1)] == 15  # LE, then TN
    assert set(BK.WINDOW_START) >= set(K.ROOTS)


def test_t2_is_the_mean_of_three_signs_without_book_scaling() -> None:
    assert t2_signal(0.1, -0.2, 0.3) == pytest.approx(1 / 3)
    assert t2_signal(0.1, 0.0, 0.3) == pytest.approx(2 / 3)
    assert t2_signal(None, 0.1, 0.1) is None


def test_no_sigma_floor_and_no_position_cap(cals) -> None:
    """lead_spec A4: n = s x 0.40 / sigma / (S_M x V), however small sigma is."""
    days = window(cals["equity"], date(2014, 1, 2), date(2016, 3, 31))
    px = {d: 400_000 + k for k, d in enumerate(days)}  # tiny, steady moves: a tiny sigma
    bars = world_bars("NQ", days, px.__getitem__)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = process_root(ctx, bars, "NQ")
    o = next(o for o in t12_orders(rd, "T1", {(2016, 2): 1}, Counter())
             if o.info.get("month") == "2016-02")
    sigma, v = o.info["sigma"], o.info["V"]
    assert sigma < 0.01
    assert o.target == pytest.approx(K.TARGET_VOL / sigma / v)


def test_t3_orders_enter_at_day_minus_two_and_exit_at_day_plus_three(cals) -> None:
    days = window(cals["equity"], date(2019, 5, 6), date(2020, 3, 31))
    px = walk_prices(days, drift=0.0, vol=0.01, seed=8)
    bars = world_bars("NQ", days, px.__getitem__)
    ctx = ctx_for(cals, {"NQ": bars}, starts={"NQ": days[0]})
    rd = process_root(ctx, bars, "NQ", with_tom=True)
    su = divisor_su({"NQ": rd.tom})
    c: Counter = Counter()
    orders = t3_orders(rd, su, c)
    entry = next(o for o in orders if o.kind == "entry" and o.info["month"] == "2019-12")
    assert entry.day == date(2019, 12, 30)
    exit_ = orders[orders.index(entry) + 1]
    assert exit_.day == date(2020, 1, 6) and exit_.target == 0.0
    assert entry.target == pytest.approx(K.TARGET_VOL / rd.sigma[entry.day] / entry.info["V"])
    assert c["T3 unit excluded: sigma warm-up"] >= 1  # the first months



def test_nyse_closures_by_rule() -> None:
    """lead_spec A12: observed-day rules, Good Friday, Juneteenth from 2022, the specials."""
    closed = {d for y in range(2010, 2025) for d in nyse_closures(y)}
    for d in ("2010-12-24", "2011-12-26", "2015-04-03", "2015-07-03", "2017-01-02",
              "2021-07-05", "2022-06-20", "2023-06-19", "2012-10-29", "2012-10-30",
              "2018-12-05", "2016-05-30", "2016-09-05", "2016-01-18", "2016-02-15",
              "2016-11-24", "2016-03-25"):
        assert date.fromisoformat(d) in closed, d
    for d in ("2010-12-31", "2021-12-31", "2015-11-27", "2021-06-18", "2016-12-23"):
        assert date.fromisoformat(d) not in closed, d
    assert date(2021, 6, 18) not in nyse_closures(2021)  # no Juneteenth before 2022


def test_t3_days_are_numbered_on_nyse_trading_days_on_the_real_equity_calendar() -> None:
    """The equity group calendar books Memorial Day and Labor Day as early-halt trade dates; T3
    skips them (A12): 2016-05 day -2 = 05-27, day -1 = 05-31; 2016-09 days +1, +2, +3 = 09-01,
    09-02, 09-06 (the August 2016 unit's exit)."""
    from base_rules.calendars import GroupCalendars, load_hist
    from data.group_session import load_group_calendar

    eq = GroupCalendars("equity", load_hist("equity"), load_group_calendar("equity"))
    assert eq.is_trade_date(date(2016, 5, 30)) and eq.early_halt(date(2016, 5, 30)) is not None
    cals = {**all_cals(), "equity": eq}
    ctx = ctx_for(cals, {}, starts={"NQ": date(2014, 1, 2)})
    units = {u.month: u for u in tom_units(ctx, CalendarOracle(ctx, "NQ", frozenset()), "NQ")}
    may, aug = units[(2016, 5)], units[(2016, 8)]
    assert (may.days[-2], may.days[-1]) == (date(2016, 5, 27), date(2016, 5, 31))
    assert may.entry == date(2016, 5, 27)
    assert [aug.days[k] for k in (1, 2, 3)] == [date(2016, 9, 1), date(2016, 9, 2),
                                                date(2016, 9, 6)]
    assert aug.exit == date(2016, 9, 6)
    nov = units[(2015, 11)]  # the half day after Thanksgiving stays a T3 day, action-excluded
    assert nov.days[-2] == date(2015, 11, 27) and nov.why == "entry: early halt"
