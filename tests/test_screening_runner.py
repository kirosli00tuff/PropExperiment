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
