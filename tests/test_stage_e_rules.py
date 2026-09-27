"""The Stage E rule set of the generalized engine (screening/stage_e_rules.py), known answers on
synthetic bars of several product groups: vendor ticks and exact money, D8 costs and the event
window (T12-4), the D9.5a fill guard, flatten times (rules/sessions.py), the grain pause, the
member cap, the D9.3 floor, D9.7 with its locked-market rule, D9.12 and the window refusals."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime, time
from fractions import Fraction
from types import MappingProxyType
from zoneinfo import ZoneInfo

import pytest

from rules import sessions
from screening.stage_e_engine import (
    DayClose,
    EngineRefusedCase,
    Fill,
    IntentRecord,
    run_engine,
)
from screening.stage_e_frozen import leg_inputs, slippage_cents
from screening.stage_e_rules import ReleaseCalendar, StageERules, release_calendar_from_dict
from strategy.stage_e.interface import LegSpec, leg_limit_intent, leg_market_intent
from tests._stage_e_synthetic import NS, minute_ct, product_frame

CT = ZoneInfo("America/Chicago")
MON, TUE, WED = date(2025, 6, 2), date(2025, 6, 3), date(2025, 6, 4)
NO_RELEASES = ReleaseCalendar(MappingProxyType({}), (), date(2019, 5, 1), date(2026, 6, 19),
                              "0" * 64, "test")


@dataclass
class Script:
    """Emit scripted orders at CT minutes: {(day, hh, mm): [(root, side, qty[, limit, ttl])]}."""

    orders: dict
    name: str = "script"
    trading_windows: dict = field(default_factory=dict)
    seen: list = field(default_factory=list)

    def on_minute(self, view, account):
        self.seen.append((view.ts_event_ns, {r: b is not None for r, b in view.bars.items()}))
        local = datetime.fromtimestamp(view.ts_event_ns / NS, tz=UTC).astimezone(CT)
        out = []
        for spec in self.orders.get((local.date(), local.hour, local.minute), []):
            root, side, qty = spec[:3]
            if side == "flat":
                pos = account.position(root)
                if not pos:
                    continue
                side, qty = ("sell" if pos > 0 else "buy"), abs(pos)
            if len(spec) > 3:
                out.append(leg_limit_intent(view, root, side, qty, spec[3], spec[4]))
            else:
                out.append(leg_market_intent(view, root, side, qty))
        return out


def _with_prior(root, prior, seg, frame, base_ticks):
    """Prepend a prior trade date's segment (holding its settlement window) to ``frame``."""
    import pandas as pd

    head = product_frame(root, [prior], 99, start=seg[0], end=seg[1], base_ticks=base_ticks,
                         vol_ticks=0.0)
    return pd.concat([head, frame], ignore_index=True)


def _rules(roots, traded=None, dates=(MON, TUE, WED), blackout=(), releases=NO_RELEASES):
    traded = set(traded if traded is not None else roots)
    return StageERules({r: leg_inputs(r, traded=r in traded) for r in roots},
                       frozenset(dates), frozenset(blackout), releases)


def _run(frames, orders, traded=None, **kw):
    roots = list(frames)
    traded_set = set(traded if traded is not None else roots)
    legs = tuple(LegSpec(r, r in traded_set) for r in roots)
    member = Script(orders)
    res = run_engine(frames, member, legs, _rules(roots, traded, **kw))
    return res, member


def _fills(res, reason=None):
    return [f for f in res.events(Fill) if reason is None or f.reason == reason]


def _refusals(res):
    return [e.refusal.reason for e in res.events(IntentRecord) if e.refusal is not None]


# ------------------------------------------------------------- money and ticks ----
def test_zn_round_trip_is_exact_in_fractional_cents_with_d8_costs() -> None:
    frame = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30),
                          path_ticks={(MON, 9 * 60 + 11): (10000, 10000, 10000, 10000),
                                      (MON, 9 * 60 + 21): (10013, 10013, 10013, 10013)})
    res, _ = _run({"ZN": frame}, {(MON, 9, 10): [("ZN", "buy", 1)],
                                  (MON, 9, 20): [("ZN", "sell", 1)]})
    buy, sell = _fills(res)
    assert (buy.price, sell.price) == (10000 * 0.015625, 10013 * 0.015625)
    assert sell.gross_realized_cents == Fraction(13 * 3125, 2)  # 13 ticks x $15.625
    costs = leg_inputs("ZN", traded=True).costs
    slip = costs.side_slippage_ticks(datetime.fromtimestamp(buy.fill_ts_ns / NS, tz=UTC), "buy",
                                     False)
    assert buy.slippage_cents == slippage_cents(1, slip, Fraction(3125, 2))
    assert buy.commission_cents == sell.commission_cents == 131
    (day,) = res.events(DayClose)
    assert day.day_net_cents == Fraction(40625, 2) - 262 - buy.slippage_cents - sell.slippage_cents


def test_cent_quoted_grains_trade_on_the_vendor_tick_grid() -> None:
    frame = product_frame("ZC", [TUE], 2, start=(9, 0), end=(9, 30), base_ticks=1800,
                          path_ticks={(TUE, 9 * 60 + 6): (1800, 1800, 1800, 1800),
                                      (TUE, 9 * 60 + 16): (1804, 1804, 1804, 1804)})
    frame = _with_prior("ZC", MON, ((13, 0), (13, 20)), frame, 1800)
    res, _ = _run({"ZC": frame}, {(TUE, 9, 5): [("ZC", "buy", 1)],
                                  (TUE, 9, 15): [("ZC", "sell", 1)]})
    buy, sell = _fills(res)
    assert buy.price == 450.0 and sell.price == 451.0  # cents: 1800 x 0.25
    assert sell.gross_realized_cents == 4 * 1250  # 4 ticks x $12.50


# ---------------------------------------------------------------- flatten ----
def test_energy_position_is_force_closed_at_1508_ct_from_rules_sessions() -> None:
    frame = product_frame("MCL", [MON], 3, start=(14, 0), end=(15, 20))
    res, _ = _run({"MCL": frame}, {(MON, 14, 0): [("MCL", "buy", 4)]})
    (forced,) = _fills(res, "forced_flatten")
    assert minute_ct(forced.fill_ts_ns) == (15, 8)
    assert sessions.flatten_time_ct("MCL", MON) == time(15, 8)


def test_no_new_energy_position_from_f_and_orders_in_the_window_are_refused() -> None:
    frame = product_frame("MCL", [MON], 3, start=(14, 50), end=(15, 20))
    res, _ = _run({"MCL": frame}, {(MON, 15, 7): [("MCL", "buy", 1)],
                                   (MON, 15, 10): [("MCL", "buy", 1)]})
    assert _refusals(res) == ["engine_flatten_window", "engine_flatten_window"]
    assert not _fills(res)


def test_a_topstep_early_close_moves_f_rule_rf1() -> None:
    """2025-11-28: Topstep's close-by 11:45 CT binds (R-F1 era); F from rules/sessions.py.
    The prior equity trade date is Thanksgiving 2025-11-27 (CME halt 12:00 CT), whose settlement
    proxy window is the last half minute before the halt (R-P3)."""
    day = date(2025, 11, 28)
    f = sessions.flatten_time_ct("MNQ", day)
    assert f is not None and f <= time(11, 45)
    frame = product_frame("MNQ", [day], 4, start=(10, 0), end=(12, 0), base_ticks=80000)
    frame = _with_prior("MNQ", date(2025, 11, 27), ((10, 0), (12, 0)), frame, 80000)
    res, _ = _run({"MNQ": frame}, {(day, 10, 0): [("MNQ", "buy", 1)]}, dates=(day,))
    (forced,) = _fills(res, "forced_flatten")
    assert minute_ct(forced.fill_ts_ns) == (f.hour, f.minute)


def test_a_grain_overnight_position_is_closed_before_the_0745_pause() -> None:
    frame = product_frame("ZC", [TUE], 5, start=(6, 0), end=(8, 0), base_ticks=1800)
    frame = _with_prior("ZC", MON, ((13, 0), (13, 20)), frame, 1800)
    res, _ = _run({"ZC": frame}, {(TUE, 7, 0): [("ZC", "buy", 1)]})
    (forced,) = _fills(res, "forced_flatten")
    assert minute_ct(forced.fill_ts_ns) == (7, 43)


def test_an_entry_whose_forced_exit_would_come_within_2_minutes_is_skipped_for_the_day() -> None:
    releases = release_calendar_from_dict(
        {"schema": "stage_e_release_calendar/1",
         "coverage": {"first": "2025-06-01", "last": "2025-06-30"},
         "releases": [{"id": "r1", "instant_utc": "2025-06-02T20:05:00Z", "products": ["MCL"]}]},
        "0" * 64, "test")  # 15:05 CT: the guard pushes a 15:05 fill to 15:07, 1 minute before F
    frame = product_frame("MCL", [MON], 3, start=(14, 50), end=(15, 20))
    res, _ = _run({"MCL": frame}, {(MON, 15, 4): [("MCL", "buy", 1)],
                                   (MON, 15, 7): [("MCL", "buy", 1)]}, releases=releases)
    assert not _fills(res)
    assert res.counters["fill_guard_deferral"] == 2
    assert res.counters["entry_skipped_min_hold_before_flatten"] == 1


# ------------------------------------------------------------- D8 and D9.5a ----
def test_event_window_cost_and_the_two_minute_fill_guard() -> None:
    release = datetime(2025, 6, 2, 9, 30, tzinfo=CT).astimezone(UTC)
    releases = release_calendar_from_dict(
        {"schema": "stage_e_release_calendar/1",
         "coverage": {"first": "2025-06-01", "last": "2025-06-30"},
         "releases": [{"id": "eia", "instant_utc": release.isoformat(), "products": ["MCL"]}]},
        "0" * 64, "test")
    frame = product_frame("MCL", [MON], 6, start=(9, 0), end=(11, 0))
    res, _ = _run({"MCL": frame}, {(MON, 9, 29): [("MCL", "buy", 4)],
                                   (MON, 10, 30): [("MCL", "sell", 4)]}, releases=releases)
    entry, exit_ = _fills(res)
    assert minute_ct(entry.fill_ts_ns) == (9, 32)  # 09:30 fill guarded to release + 2 min
    assert entry.event_window and not exit_.event_window
    costs = leg_inputs("MCL", traded=True).costs
    at = datetime.fromtimestamp(entry.fill_ts_ns / NS, tz=UTC)
    event_slip = costs.max_half_spread_ticks + costs.bucket_at(at).depth_ticks["buy"]
    assert entry.slippage_ticks == event_slip
    assert entry.slippage_cents == slippage_cents(4, event_slip, 100)


# ---------------------------------------------------------------- D9.3, D9.5 ----
def test_member_cap_and_volatility_cap_refuse_oversize_entries() -> None:
    frame = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30))
    res, _ = _run({"ZN": frame}, {(MON, 9, 1): [("ZN", "buy", 2)]})
    assert _refusals(res) == ["member_product_cap_exceeded"]
    frame = product_frame("MCL", [MON], 1, start=(9, 0), end=(9, 30))
    res, _ = _run({"MCL": frame}, {(MON, 9, 1): [("MCL", "buy", 10)],
                                   (MON, 9, 2): [("MCL", "buy", 1)]})
    assert _refusals(res) == ["member_product_cap_exceeded"]  # 10 + 1 > MCL's cap of 10


def test_the_21st_entry_of_a_trade_date_is_refused() -> None:
    frame = product_frame("ZN", [MON], 1, start=(8, 0), end=(10, 0))
    orders = {}
    for i in range(21):
        orders.setdefault((MON, 8, 3 * i), []).append(("ZN", "buy", 1))
        orders.setdefault((MON, 8, 3 * i + 2), []).append(("ZN", "flat", 0))
    res, _ = _run({"ZN": frame}, {(d, h + m // 60, m % 60): v for (d, h, m), v in orders.items()})
    assert sum(f.opening for f in _fills(res)) == 20
    assert _refusals(res).count("engine_entry_cap") == 1


def test_an_exit_less_than_two_minutes_after_the_opening_fill_is_refused() -> None:
    frame = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30))
    res, _ = _run({"ZN": frame}, {(MON, 9, 1): [("ZN", "buy", 1)],
                                  (MON, 9, 2): [("ZN", "flat", 0)],
                                  (MON, 9, 3): [("ZN", "flat", 0)]})
    assert _refusals(res) == ["engine_min_hold"]
    entry, exit_ = _fills(res)
    assert (exit_.fill_ts_ns - entry.fill_ts_ns) == 2 * 60 * NS


def test_window_and_roll_blackout_dates_refuse_new_exposure() -> None:
    frame = product_frame("ZN", [MON, TUE], 1, start=(9, 0), end=(9, 30))
    res, _ = _run({"ZN": frame}, {(MON, 9, 1): [("ZN", "buy", 1)],
                                  (TUE, 9, 1): [("ZN", "buy", 1)]}, dates=(TUE,),
                  blackout=(TUE,))
    assert _refusals(res) == ["engine_not_a_window_date", "engine_roll_blackout"]


def test_a_signal_leg_cannot_be_traded_and_a_second_leg_cannot_open() -> None:
    frames = {"ZN": product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30)),
              "ZB": product_frame("ZB", [MON], 2, start=(9, 0), end=(9, 30)),
              "MES": product_frame("MES", [MON], 3, start=(9, 0), end=(9, 30), base_ticks=24000)}
    res, _ = _run(frames, {(MON, 9, 1): [("MES", "buy", 1), ("ZN", "buy", 1)],
                           (MON, 9, 2): [("ZB", "buy", 1)]}, traded=("ZN", "ZB"))
    assert _refusals(res) == ["engine_not_a_traded_leg", "engine_second_leg_position"]


def test_limit_orders_fill_on_trade_through_at_the_limit_commission_only() -> None:
    frame = product_frame("ZN", [MON], 1, start=(9, 0), end=(9, 30),
                          path_ticks={(MON, 9 * 60 + 1): (10000, 10000, 10000, 10000),
                                      (MON, 9 * 60 + 2): (10000, 10000, 9998, 9999),
                                      (MON, 9 * 60 + 3): (9999, 9999, 9996, 9997)})
    limit = 9998 * 0.015625
    res, _ = _run({"ZN": frame}, {(MON, 9, 1): [("ZN", "buy", 1, limit, 10)]})
    fills = _fills(res)
    assert fills[0].order_type == "passive" and fills[0].price == limit
    assert minute_ct(fills[0].fill_ts_ns) == (9, 3)  # 9:02 only touches; 9:03 trades through
    assert fills[0].slippage_cents == 0 and fills[0].commission_cents == 131


# ----------------------------------------------------------------- D9.7 ----
def _zc_limit_days(lock: bool) -> dict:
    """ZC with a prior-day settlement of 440.00 cents (Monday's 13:14 CT bar, 1760 ticks) and
    the encoded 35-cent limit for 2025-06-03: the lower stop is 440 - 35 + 8.8 = 413.8 cents and
    limit-down 405.00 cents (1620 ticks)."""
    paths = {(MON, 13 * 60 + 14): (1760, 1760, 1760, 1760)}
    for m in range(9 * 60, 13 * 60 + 20):  # Tuesday: flat at 430.00 cents
        paths[(TUE, m)] = (1720, 1720, 1720, 1720)
    paths[(TUE, 9 * 60 + 10)] = (1720, 1720, 1654, 1654)  # close 413.50 <= 413.8: beyond
    if lock:
        for m in range(9 * 60 + 11, 13 * 60 + 20):  # locked at limit-down 405.00 (1620)
            paths[(TUE, m)] = (1620, 1620, 1620, 1620)
    else:
        for m in range(9 * 60 + 11, 9 * 60 + 20):
            paths[(TUE, m)] = (1654, 1660, 1650, 1654)
    return paths


def test_price_limit_zone_refuses_entries_and_forces_the_exit_with_event_cost() -> None:
    from rules import price_limits as pl

    band = pl.limit_band("ZC", TUE, datetime(2025, 6, 3, 15, tzinfo=UTC), 440)
    assert band.down_amount == 35  # the encoded initial limit for this date (cents)
    frame = product_frame("ZC", [MON, TUE], 7, start=(9, 0), end=(13, 20), base_ticks=1760,
                          vol_ticks=0.0, path_ticks=_zc_limit_days(lock=False))
    res, _ = _run({"ZC": frame}, {(TUE, 9, 0): [("ZC", "buy", 1)],
                                  (TUE, 9, 12): [("ZC", "buy", 1)]})
    exit_ = _fills(res, "price_limit_exit")
    assert len(exit_) == 1 and minute_ct(exit_[0].fill_ts_ns) == (9, 11)
    assert exit_[0].event_window  # D9.7's exit pays the event-window cost
    assert "price_limit_zone_no_entry" in _refusals(res)


def test_no_prior_settlement_means_no_entry_on_a_hard_limit_product() -> None:
    frame = product_frame("ZC", [TUE], 7, start=(9, 0), end=(9, 30), base_ticks=1760)
    res, _ = _run({"ZC": frame}, {(TUE, 9, 0): [("ZC", "buy", 1)]})
    assert _refusals(res) == ["engine_price_limit_reference_unavailable"]


def test_an_exit_locked_at_limit_down_waits_and_through_the_session_end_is_refused() -> None:
    frame = product_frame("ZC", [MON, TUE, WED], 7, start=(9, 0), end=(13, 20), base_ticks=1760,
                          vol_ticks=0.0, path_ticks=_zc_limit_days(lock=True))
    with pytest.raises(EngineRefusedCase, match="locked_exit_through_session_end"):
        _run({"ZC": frame}, {(TUE, 9, 0): [("ZC", "buy", 1)]})
    paths = _zc_limit_days(lock=True)
    for m in range(9 * 60 + 30, 13 * 60 + 20):  # the lock breaks at 09:30
        paths[(TUE, m)] = (1625, 1630, 1620, 1625)
    frame = product_frame("ZC", [MON, TUE], 7, start=(9, 0), end=(13, 20), base_ticks=1760,
                          vol_ticks=0.0, path_ticks=paths)
    res, _ = _run({"ZC": frame}, {(TUE, 9, 0): [("ZC", "buy", 1)]})
    (exit_,) = _fills(res, "price_limit_exit")
    assert minute_ct(exit_.fill_ts_ns) == (9, 30) and exit_.locked_bars_waited == 19
    assert exit_.price == 1625 * 0.25


# ------------------------------------------------------------------ D9.12 ----
def test_cpi_window_skips_an_opening_fill_for_the_day_on_a_no_open_product() -> None:
    cpi = datetime(2025, 6, 11, 7, 30, tzinfo=CT).astimezone(UTC)
    releases = release_calendar_from_dict(
        {"schema": "stage_e_release_calendar/1",
         "coverage": {"first": "2025-06-01", "last": "2025-06-30"},
         "releases": [{"id": "cpi", "instant_utc": cpi.isoformat(), "products": [], "cpi": True}]},
        "0" * 64, "test")
    day = date(2025, 6, 11)
    frame = product_frame("NQ", [day], 8, start=(7, 0), end=(8, 30), base_ticks=80000)
    frame = _with_prior("NQ", date(2025, 6, 10), ((14, 0), (15, 5)), frame, 80000)
    rules = StageERules({"NQ": replace(leg_inputs("MNQ", traded=True), root="NQ",
                                       product=leg_inputs("NQ", traded=False).product,
                                       tick_value_cents=500,
                                       costs=replace(leg_inputs("MNQ", traded=True).costs,
                                                     root="NQ"))},
                        frozenset([day]), frozenset(), releases)
    member = Script({(day, 7, 30): [("NQ", "buy", 1)], (day, 8, 0): [("NQ", "buy", 1)]})
    res = run_engine({"NQ": frame}, member, (LegSpec("NQ", True),), rules)
    assert not _fills(res)
    assert res.counters["cpi_skip:cpi_window_no_opening"] == 1
    assert _refusals(res) == ["engine_skipped_for_day"]


def test_rules_read_no_argument_that_could_vary_a_cost_or_tick() -> None:
    import inspect

    params = set(inspect.signature(StageERules).parameters)
    assert params == {"legs", "window_dates", "blackout", "releases", "restart_on_terminal",
                      "mask_hindsight_fields", "phase"}
    assert _rules(["ZN"]).tick_value("ZN") == leg_inputs("ZN", traded=True).tick_value_cents


# ------------------------------------------------------------ OC-T closures ----
def _closure_frame(end: tuple[int, int] = (15, 4)) -> object:
    """ZN on Monday from 14:00 to ``end`` (a vendor gap after it), then a closure print at the
    16:00 CT close minute (lead ruling L-3: booked to Monday, flagged), priced far away."""
    import pandas as pd

    frame = product_frame("ZN", [MON], 1, start=(14, 0), end=end, vol_ticks=0.0)
    row = frame.iloc[[-1]].copy()
    row["ts_event"] = int(datetime(2025, 6, 2, 16, 0, tzinfo=CT).timestamp()) * NS
    row[["open", "high", "low", "close"]] = 9000 * 0.015625
    row["in_scheduled_closure"] = True
    return pd.concat([frame, row], ignore_index=True)


def test_oct_a_pending_exit_at_a_closure_print_fills_at_the_prior_tradable_close() -> None:
    frame = _closure_frame()
    res, _ = _run({"ZN": frame}, {(MON, 14, 30): [("ZN", "buy", 1)],
                                  (MON, 15, 3): [("ZN", "flat", 0)]})
    exit_ = _fills(res)[-1]
    assert exit_.closure_gap and exit_.reason == "strategy"
    assert minute_ct(exit_.fill_ts_ns) == (15, 4)  # the 15:03 bar's close (its decision time)
    assert exit_.price == 10000 * 0.015625  # not the closure print's 140.625
    assert res.counters["fill_at_prior_close_closure_gap"] == 1
    assert res.counters["closure_bars_seen:ZN"] == 1


def test_oct_an_open_position_meeting_a_closure_print_is_closed_at_the_prior_close() -> None:
    """Nothing pending, no bar in the flatten window: the MLL never reads the closure print (it
    lies far beyond the $2,000 floor) and the position closes at the last tradable close."""
    frame = _closure_frame(end=(15, 5))
    res, _ = _run({"ZN": frame}, {(MON, 14, 30): [("ZN", "buy", 1)]})
    fills = _fills(res)
    assert [f.reason for f in fills] == ["strategy", "forced_flatten"]
    assert fills[1].closure_gap and minute_ct(fills[1].fill_ts_ns) == (15, 5)
    assert "mll_liquidation" not in res.counters and res.accounts_started == 1


def test_oct_a_pending_opening_order_at_a_closure_print_is_cancelled_not_filled() -> None:
    frame = _closure_frame(end=(15, 5))
    frame.loc[frame.index[-2], ["in_flatten_window", "in_no_new_positions_window"]] = False
    res, _ = _run({"ZN": frame}, {(MON, 15, 4): [("ZN", "buy", 1)]})
    assert not _fills(res)
    assert res.counters["closure_bar_no_fill"] == 1


def test_oct_the_mes_rules_keep_sim_engine_behaviour_at_closure_prints() -> None:
    from screening.stage_e_mes_rules import MesRules

    assert MesRules.skip_closure_bars is False and StageERules.skip_closure_bars is True
