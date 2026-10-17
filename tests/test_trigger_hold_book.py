"""trigger_hold.units and trigger_hold.book on synthetic bars (no market data): entry timing (tau
before / at / after the settlement bar), the h-th mark exit with a missing mark carried, window
and boundary exclusions, overlapping units and the clip, flips, a hold spanning a roll paying the
roll legs, base vs stress costs, sigma warm-up, the series."""

from __future__ import annotations

from collections import Counter
from datetime import date, time

import pytest

from base_rules.costs import vehicle_cost
from data.session import ct_ns
from multiday import constants as MK
from multiday.book import simulate_book
from tests.test_multiday_world import all_cals, ctx_for, walk_prices, window, world_bars
from trigger_hold import constants as K
from trigger_hold.book import (
    daily_series,
    e23_vehicle_cost,
    net_path,
    prepare_root,
    unit_book,
    unit_orders,
)
from trigger_hold.types import TriggerEvent
from trigger_hold.units import BarMarks, Unit, Window, build_units, entry_mark_date, series_days

S = 15 * 60
ROOT = "NQ"


@pytest.fixture(scope="module")
def cals():  # noqa: ANN201
    return all_cals()


def _world(cals, *, drop=(), splices=(), symbol=None, blackout=()):  # noqa: ANN001, ANN202
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 7, 29))
    price = walk_prices(days, drift=0.0002, vol=0.01, seed=7)
    with_bars = [d for d in days if d not in set(drop)]
    bars = world_bars(ROOT, with_bars, lambda d: price[d], symbol=symbol or (lambda d: "C1"),
                      splices=splices, blackout=blackout)
    ctx = ctx_for(cals, {ROOT: bars}, starts={ROOT: days[0]})
    rd = prepare_root(ctx, bars, ROOT)
    src = BarMarks(ctx, bars, ROOT, rd.path.marks)
    return days, rd, src, price


def _ev(d0: date, minute: int, side: int = 1, second: int = 0) -> TriggerEvent:
    return TriggerEvent(d0, ct_ns(d0, time(minute // 60, minute % 60, second)), side, "X")


def _win(days) -> Window:  # noqa: ANN001
    return Window(K.W_EXT, days[0], days[-1])


# ------------------------------------------------------------------ entry timing ----
def test_tau_strictly_before_the_settlement_bar_enters_at_mk_of_d0(cals) -> None:
    days, rd, src, _ = _world(cals)
    d0 = days[80]
    assert src.settle_open_ns(d0) == rd.path.marks[rd.path.index[d0]].ts  # bar S's open
    assert entry_mark_date(src, _ev(d0, S - 1, second=59)) == d0
    assert entry_mark_date(src, TriggerEvent(d0, src.settle_open_ns(d0) - 1, 1, "X")) == d0


@pytest.mark.parametrize("minute", [S, S + 1, 16 * 60])
def test_tau_at_or_after_the_settlement_bar_enters_at_the_next_mark_date(cals, minute) -> None:
    days, _, src, _ = _world(cals)
    d0 = days[80]
    assert entry_mark_date(src, _ev(d0, minute)) == days[81]


def test_entry_skips_a_date_without_a_mark_when_tau_is_after_s(cals) -> None:
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 7, 29))
    _, _, src, _ = _world(cals, drop=[days[81]])
    assert entry_mark_date(src, _ev(days[80], S + 5)) == days[82]


def test_a_missing_mark_on_d_e_excludes_the_unit(cals) -> None:
    days, _, src, _ = _world(cals, drop=[date(2016, 5, 2)])
    d0 = date(2016, 5, 2)
    units, c = build_units(src, [_ev(d0, 9 * 60)], _win(days), m=1, h=5)
    assert units == [] and c["excluded: entry: missing bar (mark)"] == 1


def test_a_roll_blackout_entry_or_exit_excludes_the_unit(cals) -> None:
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 7, 29))
    _, _, src, _ = _world(cals, blackout=[days[80], days[95]])
    win = _win(days)
    u1, c1 = build_units(src, [_ev(days[80], 9 * 60)], win, m=1, h=5)
    u2, c2 = build_units(src, [_ev(days[90], 9 * 60)], win, m=1, h=5)  # exit days[95]
    assert u1 == [] and c1["excluded: entry: roll blackout"] == 1
    assert u2 == [] and c2["excluded: exit: roll blackout"] == 1


# ------------------------------------------------------------------ exit and carried P&L ----
def test_exit_is_the_hth_mark_date_and_a_missing_mark_carries_the_pnl(cals) -> None:
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 7, 29))
    gap = days[83]
    _, rd, src, price = _world(cals, drop=[gap])
    marks = list(src.mark_days())
    d0 = days[80]
    units, _ = build_units(src, [_ev(d0, 9 * 60)], _win(days), m=1, h=5)
    assert len(units) == 1
    k = marks.index(d0)
    assert units[0].d_e == d0 and units[0].d_x == marks[k + 5] == days[86]
    book = unit_book(rd, units)
    n = book.fills[0]["trade"]
    tv = float(rd.tick_value_cents)
    assert sum(book.gross.values()) == pytest.approx(n * (price[days[86]] - price[d0]) * tv / 100)
    assert gap not in book.gross


@pytest.mark.parametrize("m,side,expect", [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)])
def test_direction_is_side_times_m(cals, m: int, side: int, expect: int) -> None:
    days, rd, src, _ = _world(cals)
    units, _ = build_units(src, [_ev(days[80], 9 * 60, side)], _win(days), m=m, h=5)
    assert units[0].u == expect
    assert (unit_book(rd, units).fills[0]["trade"] > 0) == (expect > 0)


# ------------------------------------------------------------------ window edges ----
def test_window_edges_exclude_units_by_reason(cals) -> None:
    days, _, src, _ = _world(cals)
    win = Window(K.W_EXT, days[70], days[100])
    evs = [_ev(days[60], 9 * 60), _ev(days[97], 9 * 60), _ev(days[100], S + 1),
           _ev(days[80], 9 * 60)]
    units, c = build_units(src, evs, win, m=1, h=5)
    assert [u.d_e for u in units] == [days[80]]
    assert c["excluded: event outside the window"] == 1
    assert c["excluded: exit outside the window (window edge)"] == 1
    assert c["excluded: entry outside the window (window edge)"] == 1
    assert series_days(src, win) == days[70:101]


def test_a_unit_across_the_store_boundary_is_excluded(cals) -> None:
    days = window(cals["equity"], date(2019, 1, 2), date(2019, 6, 28))
    price = walk_prices(days, drift=0.0, vol=0.01, seed=3)
    bars = world_bars(ROOT, days, lambda d: price[d])
    ctx = ctx_for(cals, {ROOT: bars}, starts={ROOT: days[0]})
    rd = prepare_root(ctx, bars, ROOT)
    src = BarMarks(ctx, bars, ROOT, rd.path.marks)
    whole = Window("both", days[0], days[-1])
    d0 = max(d for d in days if d <= date(2019, 4, 26))
    units, c = build_units(src, [_ev(d0, 9 * 60)], whole, m=1, h=5)
    assert units == [] and c["excluded: exit across the store boundary"] == 1


# ------------------------------------------------------------------ net position ----
def _u(days, a: int, b: int, u: int) -> Unit:  # noqa: ANN001
    return Unit(days[a], days[b], u, "X", ROOT, days[a], b - a)


def test_overlapping_same_side_units_trade_once_and_extend_the_holding(cals) -> None:
    days, rd, _, _ = _world(cals)
    units = [_u(days, 80, 85, 1), _u(days, 83, 88, 1)]
    assert net_path(units) == [(days[80], 1, 1), (days[88], 0, 0)]
    c: Counter = Counter()
    orders = unit_orders(rd, units, c)
    assert [(o.day, o.kind) for o in orders] == [(days[80], "open"), (days[88], "close")]
    book = unit_book(rd, units)
    assert len(book.fills) == 2 and book.fills[0]["trade"] == -book.fills[1]["trade"]
    sigma = rd.sigma[days[80]]
    v = float(rd.path.marks[rd.path.index[days[80]]].price) * float(rd.tick_value_cents) / 100
    assert book.fills[0]["trade"] == pytest.approx(0.40 / (sigma * v))


def test_opposite_units_net_to_zero_and_the_clip_caps_at_one(cals) -> None:
    days, _, _, _ = _world(cals)
    units = [_u(days, 80, 86, 1), _u(days, 82, 90, -1), _u(days, 81, 84, 1)]
    # sums: d80 +1, d81 +2 (clip 1), d82 +1, d84 0, d86 -1, d90 0
    assert net_path(units) == [(days[80], 1, 1), (days[84], 0, 2), (days[86], -1, 1),
                               (days[90], 0, 0)]


def test_a_flip_is_one_fill_of_the_difference_sized_at_the_flip_date(cals) -> None:
    days, rd, _, _ = _world(cals)
    units = [_u(days, 80, 84, 1), _u(days, 84, 90, -1)]
    book = unit_book(rd, units)
    kinds = [(f["date"], f["kind"]) for f in book.fills]
    assert kinds == [(str(days[80]), "open"), (str(days[84]), "flip"), (str(days[90]), "close")]
    n0 = book.fills[0]["trade"]
    sigma = rd.sigma[days[84]]
    v = float(rd.path.marks[rd.path.index[days[84]]].price) * float(rd.tick_value_cents) / 100
    n1 = -0.40 / sigma / v
    assert book.fills[1]["trade"] == pytest.approx(n1 - n0)
    assert book.fills[1]["held_after"] == pytest.approx(n1)


def test_an_opening_inside_the_sigma_warm_up_is_skipped_and_counted(cals) -> None:
    days, rd, _, _ = _world(cals)
    book = unit_book(rd, [_u(days, 20, 25, 1)])
    assert book.fills == [] and book.gross == {}
    assert book.counters["opening skipped: sigma undefined (warm-up or zero)"] == 1


def test_orders_equal_the_frozen_engine_input(cals) -> None:
    days, rd, _, _ = _world(cals)
    units = [_u(days, 80, 85, 1)]
    c: Counter = Counter()
    a = simulate_book(rd, unit_orders(rd, units, c))
    b = unit_book(rd, units)
    assert a.net(K.BASE) == b.net(K.BASE)


# ------------------------------------------------------------------ rolls and costs ----
def test_a_hold_spanning_a_roll_pays_both_roll_legs(cals) -> None:
    days = window(cals["equity"], date(2016, 1, 4), date(2016, 7, 29))
    roll = days[83]
    _, rd, src, _ = _world(cals, splices=[roll], symbol=lambda d: "H6" if d < roll else "M6")
    units, _ = build_units(src, [_ev(days[80], 9 * 60, -1)], _win(days), m=1, h=5)
    book = unit_book(rd, units)
    kinds = [f["kind"] for f in book.fills]
    assert kinds == ["open", "roll_out", "roll_in", "close"]
    n = book.fills[0]["trade"]
    legs = [leg for iv in rd.path.intervals if iv is not None for leg in iv.rolls]
    assert len(legs) == 2
    for c in K.CASES:
        assert book.fills[1]["cost"][c] == pytest.approx(abs(n) * float(
            legs[0].fill.cost["buy"][c]) / 100)  # a short rolls out by buying
        assert book.fills[2]["cost"][c] == pytest.approx(abs(n) * float(
            legs[1].fill.cost["sell"][c]) / 100)


def test_stress_is_commission_plus_twice_the_one_side_slippage(cals) -> None:
    days, rd, _, _ = _world(cals)
    vc0, vc = vehicle_cost(ROOT), e23_vehicle_cost(ROOT)
    comm = vc.costs.commission_side_cents
    for k in range(60, 120, 7):
        ts = rd.path.marks[k].ts
        for side in ("buy", "sell"):
            for event in (False, True):
                base0, u0 = vc0.fill_costs(ts, side, event)
                got, u1 = vc.fill_costs(ts, side, event)
                assert got[K.BASE] == base0[K.BASE] and u0 == u1
                assert got[K.STRESS] == comm + 2 * (base0[K.BASE] - comm)
                assert got[K.STRESS] > got[K.BASE]
    book = unit_book(rd, [_u(days, 80, 85, 1)])
    for f in book.fills:
        per = rd.fills[date.fromisoformat(f["date"])].cost[f["side"]]
        assert f["cost"][K.STRESS] == pytest.approx(abs(f["trade"]) * float(
            2 * per[K.BASE] - comm) / 100)
    assert sum(book.cost[K.STRESS].values()) > sum(book.cost[K.BASE].values()) > 0


def test_the_base_case_equals_the_frozen_d8_cost(cals) -> None:
    from multiday.book import process_root

    days = window(cals["equity"], date(2016, 1, 4), date(2016, 7, 29))
    price = walk_prices(days, drift=0.0002, vol=0.01, seed=7)
    bars = world_bars(ROOT, days, lambda d: price[d])
    ctx = ctx_for(cals, {ROOT: bars}, starts={ROOT: days[0]})
    frozen = process_root(ctx, bars, ROOT)  # the default VehicleCost
    mine = prepare_root(ctx, bars, ROOT)
    assert frozen.fills and set(frozen.fills) <= set(mine.fills)
    assert len(mine.fills) == len(mine.path.marks)
    for d, f in frozen.fills.items():
        for side in ("buy", "sell"):
            assert mine.fills[d].cost[side][K.BASE] == f.cost[side][K.BASE]
    assert mine.path.intervals == frozen.path.intervals or all(
        a is None and b is None
        or [x.fill.cost[s][K.BASE] for x in a.rolls for s in ("buy", "sell")]
        == [x.fill.cost[s][K.BASE] for x in b.rolls for s in ("buy", "sell")]
        for a, b in zip(mine.path.intervals, frozen.path.intervals, strict=True))


# ------------------------------------------------------------------ series ----
def test_the_series_is_zero_when_flat_and_sums_the_book(cals) -> None:
    days, rd, src, _ = _world(cals)
    win = Window(K.W_EXT, days[70], days[110])
    book = unit_book(rd, [_u(days, 80, 85, 1), _u(days, 95, 100, -1)])
    c: Counter = Counter()
    ser = daily_series(book, series_days(src, win), c)
    for case in K.CASES:
        vals = dict(ser[case])
        assert list(vals) == days[70:111]
        assert vals[days[75]] == 0.0 and vals[days[90]] == 0.0
        assert sum(vals.values()) == pytest.approx(sum(book.net(case).values()))
    assert MK.SLIP150 not in ser
