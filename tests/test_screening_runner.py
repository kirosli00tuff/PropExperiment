"""The shared screening runner's contract (Stage D.1a, Task 3).

What these pin: one canonical EngineConfig (roll blackout included) that matches the
configuration Stage D.1's lead accounting used, train-date-only windows, and a report
that carries the passive-fill caveats whenever a passive fill happened.
Real-data tests read only the research parquet's metadata and trade dates.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

import pytest

from data.research_bars import RESEARCH_SERIES_PATH
from screening import ScreeningWindow, fold_train_window, screen_candidate, train_union_window
from screening.runner import CANONICAL_ROLL_BLACKOUT_SESSIONS, canonical_engine_config, screen_frame
from sim.engine import EngineConfig, roll_blackout_dates, splice_trade_dates_from_parquet
from sim.fill_model import PASSIVE_FILL_CAVEATS
from strategy.interface import AccountView, Bar, limit_intent, market_intent
from tests.test_drift_benchmark import ct_hm, path_ticks, session_frame


def test_canonical_config_is_the_one_stage_d1_lead_accounting_used() -> None:
    splices = splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH)
    lead = EngineConfig(restart_on_terminal=True, roll_blackout=roll_blackout_dates(splices, 2))
    assert canonical_engine_config(splices) == lead
    assert CANONICAL_ROLL_BLACKOUT_SESSIONS == 2
    assert canonical_engine_config(splices).mask_hindsight_fields is True


def test_canonical_blackout_covers_six_fold0_train_dates() -> None:
    # Stage D.1, Task 3: "Fold 0's train window contains exactly 6 blackout dates".
    config = canonical_engine_config(splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH))
    assert len(config.roll_blackout & set(fold_train_window(0).trade_dates)) == 6


def test_windows_are_train_dates_and_match_stage_d1() -> None:
    assert len(fold_train_window(0).trade_dates) == 142
    union = train_union_window()
    assert (len(union.trade_dates), union.trade_dates[0], union.trade_dates[-1]) == (
        289, date(2025, 4, 1), date(2026, 5, 13))


def test_window_with_a_test_only_date_is_refused() -> None:
    # 2026-06-12 is the last research date: fold 7's TEST window, in no train window.
    bad = ScreeningWindow("leaky", (*fold_train_window(7).trade_dates, date(2026, 6, 12)))
    with pytest.raises(ValueError, match="train dates only"):
        screen_candidate("x", lambda: None, bad)
    with pytest.raises(ValueError, match="empty"):
        screen_candidate("x", lambda: None, replace(bad, trade_dates=()))


@dataclass(frozen=True)
class PassiveDipBuyer:
    """Rests a buy limit 4 ticks under the 09:00 close; exits at 15:00 with a market order."""

    name: str = "passive_dip_buyer"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if ct_hm(bar) == (9, 0) and account.position_micros == 0:
            return (limit_intent(bar, "buy", 1, bar.close - 1.00, 60),)
        if ct_hm(bar) == (15, 0) and account.position_micros:
            return (market_intent(bar, "sell", account.position_micros),)
        return ()


def test_passive_fills_flow_through_the_runner_with_their_caveats() -> None:
    # Sessions fall 40 ticks, linearly, from 08:31. The 09:00 close is 3 ticks down, so the
    # limit sits 7 ticks down; by 09:10 price is more than 8 ticks down: traded through.
    frame = session_frame([path_ticks(-40)] * 5)
    report = screen_frame(frame, "passive", PassiveDipBuyer, "synthetic", splice_trade_dates=())
    assert report.passive_orders_placed == 5
    assert report.passive_fills == 5 and report.market_fills == 5
    assert set(PASSIVE_FILL_CAVEATS) <= set(report.caveats)


def test_market_only_report_does_not_carry_passive_caveats() -> None:
    @dataclass(frozen=True)
    class Flat:
        name: str = "flat"

        def on_bar(self, bar: Bar, account: AccountView) -> tuple:
            return ()

    report = screen_frame(session_frame([path_ticks(0)] * 3), "flat", Flat, "synthetic",
                          splice_trade_dates=())
    assert report.passive_fills == 0 and not set(PASSIVE_FILL_CAVEATS) & set(report.caveats)
    assert report.exposure == "none" and report.verdict == "fail"


def test_daily_net_series_covers_every_window_date_and_sums_to_net() -> None:
    # Stage D.1b: the accounting consumes this series, so it must align to the window's
    # dates (a $0 day included) and add up to the report's net to the cent.
    frame = session_frame([path_ticks(-40)] * 5)
    report = screen_frame(frame, "passive", PassiveDipBuyer, "synthetic", splice_trade_dates=())
    assert len(report.daily_net_usd) == report.n_dates == 5
    assert round(sum(report.daily_net_usd), 2) == report.net_pnl_usd
    assert all(day < 0 for day in report.daily_net_usd)  # bought a falling session every day

    flat = screen_frame(frame, "flat", lambda: _Flat(), "synthetic", splice_trade_dates=())
    assert flat.daily_net_usd == (0.0,) * 5


@dataclass(frozen=True)
class _Flat:
    name: str = "flat"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        return ()


# ---------------------------------------------------------- per-trade series ----
@dataclass(frozen=True)
class _ScheduledTrader:
    """Buys 1 micro at each scheduled (trade date, CT hour:minute) and sells it at the next
    bar's decision: exactly one closed round trip per schedule entry, on a date we choose."""

    schedule: tuple[tuple[date, tuple[tuple[int, int], ...]], ...] = ()
    name: str = "scheduled_trader"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if account.position_micros:
            return (market_intent(bar, "sell", account.position_micros),)
        if ct_hm(bar) in dict(self.schedule).get(bar.trade_date, ()):
            return (market_intent(bar, "buy", 1),)
        return ()


def test_trip_series_matches_the_trip_count_and_the_net() -> None:
    # Stage D.1e: the power calculation consumes the per-trade series, so it must hold exactly
    # the trips the report counted and add up to the same net as the daily series.
    report = screen_frame(session_frame([path_ticks(-40)] * 5), "passive", PassiveDipBuyer,
                          "synthetic", splice_trade_dates=())
    assert len(report.trip_pnls_usd) == report.n_trips == 5
    assert round(sum(report.trip_pnls_usd), 2) == report.net_pnl_usd
    assert sum(report.daily_n_trips) == report.n_trips
    assert len(report.daily_n_trips) == report.n_dates == 5
    assert report.daily_n_trips == (1,) * 5  # one trip a day, the day it was bought and sold


def test_daily_trip_counts_land_on_the_dates_the_trips_closed() -> None:
    # Two trips on day 1, none on day 2, one on day 3: the counts follow the closing fills.
    days = sorted({date.fromisoformat(d) for d in session_frame([path_ticks(0)] * 5)
                   ["trade_date"]})
    schedule = ((days[0], ((9, 0), (10, 0))), (days[2], ((11, 0),)))
    report = screen_frame(session_frame([path_ticks(0)] * 5), "scheduled",
                          lambda: _ScheduledTrader(schedule), "synthetic", splice_trade_dates=())
    assert report.n_trips == 3
    assert report.daily_n_trips == (2, 0, 1, 0, 0)
    assert len(report.trip_pnls_usd) == 3
    assert round(sum(report.trip_pnls_usd), 2) == report.net_pnl_usd


def test_a_report_with_no_trades_has_no_trips_at_all() -> None:
    flat = screen_frame(session_frame([path_ticks(0)] * 5), "flat", lambda: _Flat(),
                        "synthetic", splice_trade_dates=())
    assert flat.n_trips == 0
    assert flat.trip_pnls_usd == ()
    assert flat.daily_n_trips == (0,) * 5
    assert flat.to_dict()["daily_n_trips"] == (0,) * 5


# ------------------------------------------------------------ per-trip micros ----
@dataclass(frozen=True)
class _FixedSizeTrader:
    """Buys ``micros`` at 09:00 CT and sells the whole lot at the next bar's decision."""

    micros: int = 2
    name: str = "fixed_size_trader"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if account.position_micros:
            return (market_intent(bar, "sell", account.position_micros),)
        if ct_hm(bar) == (9, 0) and account.pending_signed_micros == 0:
            return (market_intent(bar, "buy", self.micros),)
        return ()


@dataclass(frozen=True)
class _ScaleInTrader:
    """One trip a day, built in two lots: buy 1 at 09:00 CT, 1 more at 10:00, sell both at
    11:00. The position never returns to flat in between, so it is ONE round trip of 2 micros,
    not two trips of 1."""

    name: str = "scale_in_trader"

    def on_bar(self, bar: Bar, account: AccountView) -> tuple:
        if account.pending_signed_micros:
            return ()
        hm = ct_hm(bar)
        if hm in ((9, 0), (10, 0)) and account.position_micros < 2:
            return (market_intent(bar, "buy", 1),)
        if hm == (11, 0) and account.position_micros:
            return (market_intent(bar, "sell", account.position_micros),)
        return ()


def test_trip_micros_is_one_for_every_trip_of_a_one_micro_strategy() -> None:
    # Stage D.1e: the per-micro series divides each trip by its OWN size, so the field has to
    # carry one size per trip, in the same order and of the same length as trip_pnls_usd.
    passive = screen_frame(session_frame([path_ticks(-40)] * 5), "passive", PassiveDipBuyer,
                           "synthetic", splice_trade_dates=())
    assert passive.trip_micros == (1,) * 5
    assert len(passive.trip_micros) == len(passive.trip_pnls_usd) == passive.n_trips

    days = sorted({date.fromisoformat(d) for d in session_frame([path_ticks(0)] * 5)
                   ["trade_date"]})
    schedule = ((days[0], ((9, 0), (10, 0))), (days[2], ((11, 0),)))
    scheduled = screen_frame(session_frame([path_ticks(0)] * 5), "scheduled",
                             lambda: _ScheduledTrader(schedule), "synthetic",
                             splice_trade_dates=())
    assert scheduled.n_trips == 3
    assert scheduled.trip_micros == (1, 1, 1)


def test_trip_micros_follows_the_size_the_strategy_actually_traded() -> None:
    # The unit error Stage D.1e's adversarial review found: a two-micro trip is worth $2.50 a
    # tick, a one-micro trip $1.25. The report says which, per trip, instead of assuming.
    report = screen_frame(session_frame([path_ticks(0)] * 5), "two_micro",
                          lambda: _FixedSizeTrader(2), "synthetic", splice_trade_dates=())
    assert report.n_trips == 5
    assert report.trip_micros == (2,) * 5
    assert len(report.trip_micros) == len(report.trip_pnls_usd)


def test_trip_micros_of_a_scale_in_is_the_largest_position_that_trip_held() -> None:
    # Buy 1, buy 1 more, sell 2: never flat in between, so ONE trip carrying 2 micros.
    report = screen_frame(session_frame([path_ticks(0)] * 5), "scale_in", _ScaleInTrader,
                          "synthetic", splice_trade_dates=())
    assert report.n_trips == 5
    assert report.market_fills == 15  # three fills a day: two in, one out
    assert report.trip_micros == (2,) * 5


def test_a_report_with_no_trades_has_no_trip_sizes() -> None:
    flat = screen_frame(session_frame([path_ticks(0)] * 5), "flat", lambda: _Flat(),
                        "synthetic", splice_trade_dates=())
    assert flat.trip_micros == ()
    assert flat.to_dict()["trip_micros"] == ()
