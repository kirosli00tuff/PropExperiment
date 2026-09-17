"""Known-answer tests for rules/xfa_rules.py. Every expected value is hand-computed
in the comment beside it; none is read back from the implementation.

MES arithmetic used throughout: 1 tick = 0.25 pt = $1.25 per micro, so
1 point = 4 ticks = $5.00 per micro.
"""

from __future__ import annotations

import inspect
from dataclasses import FrozenInstanceError, replace
from datetime import UTC, date, datetime, time, timedelta

import pytest

from rules import xfa_rules as xr
from rules.xfa_rules import (
    COMBINE_50K,
    MICROS_PER_MINI,
    XFA_50K,
    AccountState,
    OrderIntent,
    PayoutPath,
    Phase,
    Refusal,
    Status,
)

D0 = date(2026, 1, 5)


def run_days(state: AccountState, pnls_cents: list[int], trades: int = 1) -> AccountState:
    """Book each day's net P&L as one realized trade, then close the day."""
    for i, pnl in enumerate(pnls_cents):
        state = xr.record_realized_pnl(state, pnl)
        state = xr.close_trading_day(state, D0 + timedelta(days=i), trades)
    return state


def xfa_with_window(pnls_cents: list[int], balance_cents: int) -> AccountState:
    """An active XFA whose payout window is exactly ``pnls_cents``."""
    days = tuple(xr.DayRecord(D0 + timedelta(days=i), p, 1) for i, p in enumerate(pnls_cents))
    return AccountState(
        Phase.XFA, balance_cents, balance_cents, 0, history=days, payout_window=days
    )


# ============================================================ MLL (a) EOD floor
class TestEndOfDayTrailingFloor:
    def test_floor_ratchets_up_with_closing_balance(self) -> None:
        # XFA starts at $0 balance, floor -$2,000. Close at +$1,000 -> floor -$1,000.
        state = run_days(xr.new_xfa_account(), [100_000])
        assert state.mll_floor_cents == -100_000

    def test_floor_never_moves_down_on_a_losing_day(self) -> None:
        # +$1,000 (floor -$1,000) then -$500 (balance $500; $500-$2,000=-$1,500 < -$1,000).
        state = run_days(xr.new_xfa_account(), [100_000, -50_000])
        assert state.mll_floor_cents == -100_000

    def test_xfa_floor_locks_at_zero_balance(self) -> None:
        # Close at $2,500: $2,500-$2,000 = $500, but the XFA lock is $0.
        state = run_days(xr.new_xfa_account(), [250_000])
        assert state.mll_floor_cents == 0

    def test_combine_floor_locks_at_starting_balance(self) -> None:
        # $50,000 + $2,900 = $52,900; $52,900-$2,000 = $50,900 -> locked at $50,000.
        state = run_days(xr.new_combine_account(), [100_000, 100_000, 90_000])
        assert state.mll_floor_cents == 5_000_000

    def test_floor_does_not_move_intraday(self) -> None:
        # A realized +$1,000 mid-session leaves the floor at -$2,000 until the close.
        state = xr.record_realized_pnl(xr.new_xfa_account(), 100_000)
        assert state.mll_floor_cents == -200_000


# ======================================================= MLL (b) real-time check
class TestRealTimeBreach:
    def test_intrabar_wick_breach_caught_although_close_never_breaches(self) -> None:
        # Day 1: +$1,000 -> balance $1,000, floor -$1,000.
        state = run_days(xr.new_xfa_account(), [100_000])
        assert (state.balance_cents, state.mll_floor_cents) == (100_000, -100_000)

        # Day 2: long 10 MES @ 6000.00. The bar wicks to 5959.75:
        # (5959.75 - 6000.00) = -40.25 pt = -161 ticks; x 10 micros x $1.25 = -$2,012.50.
        wick = xr.worst_intrabar_unrealized_cents(10, 6000.00, bar_high=6005.00, bar_low=5959.75)
        assert wick == -201_250
        # Equity $1,000 - $2,012.50 = -$1,012.50 <= floor -$1,000 -> breach.
        breached = xr.apply_realtime_mll(state, wick)
        assert breached.status is Status.BREACHED
        assert breached.breach is not None and breached.breach.reason == "mll_breach"

        # The same trade exits at 6004.00: +16 ticks x 10 x $1.25 = +$200 -> close $1,200.
        exit_pnl = xr.unrealized_pnl_cents(10, 6000.00, 6004.00)
        assert exit_pnl == 20_000
        # An end-of-day-only check would see $1,200 > -$1,000 and miss the breach:
        assert xr.check_mll_realtime(state.mll_floor_cents, 100_000 + exit_pnl, 0) is None
        eod_only = xr.close_trading_day(xr.record_realized_pnl(state, exit_pnl), D0, 1)
        assert eod_only.status is Status.ACTIVE
        # ...but the real account, which saw the wick, stays breached through the close.
        after = xr.close_trading_day(xr.record_realized_pnl(breached, exit_pnl), D0, 1)
        assert after.status is Status.BREACHED

    def test_short_position_uses_the_bar_high(self) -> None:
        # Short 20 @ 5000.00, high 5025.00: -25 pt = -100 ticks x 20 x $1.25 = -$2,500.
        assert xr.worst_intrabar_unrealized_cents(-20, 5000.00, 5025.00, 4990.00) == -250_000

    def test_touching_the_floor_is_a_breach(self) -> None:
        # Equity exactly -$2,000 on a fresh XFA: "touches or falls below".
        assert xr.check_mll_realtime(-200_000, 0, -200_000) is not None
        assert xr.check_mll_realtime(-200_000, 0, -199_999) is None

    def test_off_tick_price_is_rejected(self) -> None:
        with pytest.raises(ValueError):
            xr.price_to_ticks(6000.10)


# ================================================================ Combine
class TestCombine:
    def test_big_day_raises_target_and_does_not_fail_account(self) -> None:
        # Day 1: +$1,600 > 50% of $3,000 ($1,500). Target -> $1,600 / 0.50 = $3,200.
        state = run_days(xr.new_combine_account(), [160_000])
        progress = xr.evaluate_combine(state)
        assert state.status is Status.ACTIVE  # NOT failed, NOT breached, NOT passed
        assert state.status is not Status.BREACHED
        assert progress.target_raised
        assert progress.effective_target_cents == 320_000

        # Day 2: +$1,500 -> total $3,100 >= base $3,000 but < raised $3,200: still trading.
        state = run_days(state, [150_000])
        assert xr.evaluate_combine(state).total_profit_cents == 310_000
        assert state.status is Status.ACTIVE

        # Day 3: +$100 -> total $3,200 = raised target -> passed.
        state = run_days(state, [10_000])
        assert state.status is Status.PASSED

    def test_exactly_half_the_target_does_not_raise_it(self) -> None:
        # $1,500 / 0.50 = $3,000 = base target: no raise.
        assert xr.effective_profit_target_cents(150_000) == 300_000
        assert xr.effective_profit_target_cents(150_001) == 300_002

    def test_combine_passes_at_base_target_with_even_days(self) -> None:
        state = run_days(xr.new_combine_account(), [100_000, 100_000, 100_000])
        assert state.status is Status.PASSED

    def test_combine_breach_by_mll(self) -> None:
        # -$2,000 realized from $50,000 -> $48,000 touches floor $48,000.
        state = xr.record_realized_pnl(xr.new_combine_account(), -200_000)
        assert state.status is Status.BREACHED


# ======================================================= XFA Standard payout
class TestStandardPayout:
    def test_five_winning_days_of_150_are_eligible(self) -> None:
        state = xfa_with_window([15_000] * 5, balance_cents=75_000)
        # 50% of $750 = $375 -> request $375 is allowed.
        assert xr.check_payout_request(state, PayoutPath.STANDARD, 37_500) is None

    def test_a_149_99_day_does_not_count(self) -> None:
        state = xfa_with_window([15_000] * 4 + [14_999], balance_cents=74_999)
        refusal = xr.check_payout_request(state, PayoutPath.STANDARD, 12_500)
        assert refusal is not None and refusal.reason == "standard_insufficient_winning_days"

    def test_days_need_not_be_consecutive(self) -> None:
        state = xfa_with_window([20_000, -5_000, 20_000, 20_000, 0, 20_000, 20_000], 95_000)
        assert xr.standard_path_eligibility(state.payout_window, 0) is None

    def test_amount_above_half_balance_refused_even_below_dollar_cap(self) -> None:
        # Balance $1,500; request $1,000 < $2,000 cap, but > 50% x $1,500 = $750.
        state = xfa_with_window([30_000] * 5, balance_cents=150_000)
        refusal = xr.check_payout_request(state, PayoutPath.STANDARD, 100_000)
        assert refusal is not None
        assert refusal.reason == "payout_exceeds_balance_ceiling"
        assert refusal.reason != "payout_exceeds_dollar_cap"
        # Boundary: exactly $750 is allowed.
        assert xr.check_payout_request(state, PayoutPath.STANDARD, 75_000) is None

    def test_amount_above_dollar_cap_has_its_own_reason(self) -> None:
        # Balance $10,000 (50% = $5,000); request $2,500 > Standard cap $2,000.
        state = xfa_with_window([200_000] * 5, balance_cents=1_000_000)
        refusal = xr.check_payout_request(state, PayoutPath.STANDARD, 250_000)
        assert refusal is not None and refusal.reason == "payout_exceeds_dollar_cap"

    def test_below_minimum_payout(self) -> None:
        state = xfa_with_window([30_000] * 5, balance_cents=150_000)
        refusal = xr.check_payout_request(state, PayoutPath.STANDARD, 12_499)
        assert refusal is not None and refusal.reason == "payout_below_minimum"

    def test_combine_account_has_no_payouts(self) -> None:
        refusal = xr.check_payout_request(xr.new_combine_account(), PayoutPath.STANDARD, 12_500)
        assert refusal is not None and refusal.reason == "payout_not_xfa"


# ==================================================== XFA Consistency payout
class TestConsistencyPayout:
    def test_exactly_40_00_percent_passes(self) -> None:
        # $4,000 / ($4,000 + $3,000 + $3,000) = 40.00% -> eligible.
        state = xfa_with_window([400_000, 300_000, 300_000], balance_cents=1_000_000)
        assert xr.consistency_path_eligibility(state.payout_window) is None
        assert xr.check_payout_request(state, PayoutPath.CONSISTENCY, 300_000) is None

    def test_40_01_percent_fails(self) -> None:
        # $4,001 / ($4,001 + $3,000 + $2,999) = $4,001 / $10,000 = 40.01% -> not eligible.
        state = xfa_with_window([400_100, 300_000, 299_900], balance_cents=1_000_000)
        refusal = xr.check_payout_request(state, PayoutPath.CONSISTENCY, 300_000)
        assert refusal is not None
        assert refusal.reason == "consistency_largest_day_exceeds_limit"
        assert "40.0100%" in refusal.arithmetic

    def test_needs_three_days_with_a_trade(self) -> None:
        days = (
            xr.DayRecord(D0, 10_000, 1),
            xr.DayRecord(D0 + timedelta(days=1), 10_000, 1),
            xr.DayRecord(D0 + timedelta(days=2), 0, 0),  # no trade: not a trading day
        )
        refusal = xr.consistency_path_eligibility(days)
        assert refusal is not None and refusal.reason == "consistency_insufficient_trading_days"

    def test_consistency_cap_is_3000(self) -> None:
        state = xfa_with_window([400_000, 300_000, 300_000], balance_cents=1_000_000)
        refusal = xr.check_payout_request(state, PayoutPath.CONSISTENCY, 300_001)
        assert refusal is not None and refusal.reason == "payout_exceeds_dollar_cap"


# ===================================================== post-payout MLL reset
class TestPostPayoutMllReset:
    def test_payout_resets_floor_and_next_loss_breaches_against_it(self) -> None:
        # Five +$300 days: EOD balances 300..1,500 -> floor -1,700,-1,400,-1,100,-800,-500.
        state = run_days(xr.new_xfa_account(), [30_000] * 5)
        assert (state.balance_cents, state.mll_floor_cents) == (150_000, -50_000)

        # Payout $750 (= 50% of $1,500, under the $2,000 cap).
        outcome = xr.process_payout(state, PayoutPath.STANDARD, 75_000)
        assert outcome.refusal is None
        paid = outcome.state
        assert paid.balance_cents == 75_000
        assert paid.mll_floor_cents == 0  # reset to $0: the whole buffer is now $750
        assert paid.payout_window == () and paid.payouts_processed == 1

        # Immediately lose $760: balance -$10 <= $0 floor -> breach.
        after_loss = xr.record_realized_pnl(paid, -76_000)
        assert after_loss.status is Status.BREACHED
        # Counterfactual: under the pre-payout floor (-$500) that loss would NOT breach,
        # so this test fails if the reset is missing.
        assert xr.check_mll_realtime(-50_000, -1_000, 0) is None

    def test_losing_exactly_the_remaining_balance_touches_the_floor(self) -> None:
        paid = xr.process_payout(
            run_days(xr.new_xfa_account(), [30_000] * 5), PayoutPath.STANDARD, 75_000
        ).state
        assert xr.record_realized_pnl(paid, -75_000).status is Status.BREACHED
        assert xr.record_realized_pnl(paid, -74_999).status is Status.ACTIVE

    def test_reset_is_a_separate_transition_from_the_debit(self) -> None:
        state = run_days(xr.new_xfa_account(), [30_000] * 5)
        debited = xr.debit_payout(state, 75_000)
        assert debited.mll_floor_cents == -50_000  # debit alone leaves the floor
        assert xr.reset_mll_after_payout(debited).mll_floor_cents == 0

    def test_refused_payout_changes_nothing(self) -> None:
        state = run_days(xr.new_xfa_account(), [30_000] * 5)
        outcome = xr.process_payout(state, PayoutPath.STANDARD, 100_000)  # > 50% of $1,500
        assert outcome.refusal is not None
        assert outcome.state == state

    def test_window_restarts_and_request_day_is_excluded(self) -> None:
        state = run_days(xr.new_xfa_account(), [30_000] * 5)
        paid = xr.process_payout(state, PayoutPath.STANDARD, 75_000).state
        paid = run_days(paid, [20_000])  # the request day's close: excluded
        assert paid.payout_window == ()
        paid = run_days(paid, [20_000])  # next day: counts
        assert len(paid.payout_window) == 1

    def test_standard_requires_profit_since_last_payout(self) -> None:
        window = tuple(xr.DayRecord(D0 + timedelta(days=i), p, 1)
                       for i, p in enumerate([15_000] * 5 + [-80_000]))
        refusal = xr.standard_path_eligibility(window, payouts_processed=1)
        assert refusal is not None and refusal.reason == "standard_no_profit_since_last_payout"
        assert xr.standard_path_eligibility(window, payouts_processed=0) is None


# ============================================================= scaling plan
class TestScalingPlan:
    def test_micro_per_mini_is_a_named_constant_of_ten(self) -> None:
        assert MICROS_PER_MINI == 10

    @pytest.mark.parametrize(
        ("balance_cents", "expected_micros"),
        [
            (-50_000, 20),  # below $0: 2 lots x 10
            (0, 20),  # $0: 2 lots
            (149_999, 20),  # $1,499.99: 2 lots
            (150_000, 30),  # $1,500: 3 lots
            (200_000, 30),  # exactly $2,000: 3 lots (help center "Above $2,000: 5")
            (200_001, 50),  # $2,000.01: 5 lots
            (10_000_000, 50),
        ],
    )
    def test_xfa_tiers(self, balance_cents: int, expected_micros: int) -> None:
        assert xr.max_position_micros(Phase.XFA, balance_cents) == expected_micros

    def test_combine_cap_is_five_minis(self) -> None:
        assert xr.max_position_micros(Phase.COMBINE, 5_000_000) == 50


# ================================================================== flatten
def utc(y: int, mo: int, d: int, h: int, mi: int, s: int = 0) -> datetime:
    return datetime(y, mo, d, h, mi, s, tzinfo=UTC)


class TestAutoFlatten:
    def test_boundary_in_cdt(self) -> None:
        # Wed 2026-07-15, CDT = UTC-5: 15:10 CT = 20:10 UTC.
        assert not xr.is_flatten_window(utc(2026, 7, 15, 20, 9, 59))
        assert xr.is_flatten_window(utc(2026, 7, 15, 20, 10, 0))
        assert xr.is_flatten_window(utc(2026, 7, 15, 21, 59, 59))  # 16:59:59 CT
        assert not xr.is_flatten_window(utc(2026, 7, 15, 22, 0, 0))  # 17:00 reopen

    def test_boundary_in_cst(self) -> None:
        # Wed 2026-01-14, CST = UTC-6: 15:10 CT = 21:10 UTC.
        assert not xr.is_flatten_window(utc(2026, 1, 14, 21, 9, 59))
        assert xr.is_flatten_window(utc(2026, 1, 14, 21, 10, 0))

    def test_weekend_is_flat(self) -> None:
        assert xr.is_flatten_window(utc(2026, 7, 18, 15, 0))  # Saturday
        assert xr.is_flatten_window(utc(2026, 7, 19, 21, 59))  # Sunday 16:59 CT
        assert not xr.is_flatten_window(utc(2026, 7, 19, 22, 0))  # Sunday 17:00 CT

    def test_friday_after_flatten_stays_flat_into_the_weekend(self) -> None:
        # Fri 2026-07-17 CDT: 15:09 open; 20:00 CT (Sat 01:00 UTC) must still be flat,
        # because there is no 17:00 reopen on a Friday.
        assert not xr.is_flatten_window(utc(2026, 7, 17, 20, 9))
        assert xr.is_flatten_window(utc(2026, 7, 18, 1, 0))
        assert xr.is_no_new_positions_window(utc(2026, 7, 18, 1, 0))
        assert xr.required_flatten(5, utc(2026, 7, 18, 1, 0)) is not None

    def test_forced_close_of_open_position(self) -> None:
        forced = xr.required_flatten(30, utc(2026, 7, 15, 20, 10))
        assert forced is not None
        assert (forced.side, forced.quantity_micros) == ("sell", 30)
        short = xr.required_flatten(-7, utc(2026, 7, 15, 20, 30))
        assert short is not None and (short.side, short.quantity_micros) == ("buy", 7)
        assert xr.required_flatten(30, utc(2026, 7, 15, 20, 9)) is None
        assert xr.required_flatten(0, utc(2026, 7, 15, 20, 30)) is None

    def test_holiday_flatten_is_15_minutes_before_early_close(self) -> None:
        assert xr.flatten_time_ct(time(12, 0)) == time(11, 45)
        assert xr.flatten_time_ct(time(12, 15)) == time(12, 0)
        # 2026-11-26 Thanksgiving (CST, UTC-6): 11:45 CT = 17:45 UTC.
        assert xr.is_flatten_window(utc(2026, 11, 26, 17, 45), time(12, 0))
        assert not xr.is_flatten_window(utc(2026, 11, 26, 17, 44, 59), time(12, 0))

    def test_early_close_input_cannot_make_flatten_later(self) -> None:
        assert xr.flatten_time_ct(time(17, 0)) == time(15, 10)
        assert xr.flatten_time_ct(time(23, 59)) == time(15, 10)

    def test_no_override_inputs_exist(self) -> None:
        for fn in (xr.required_flatten, xr.check_order, xr.is_flatten_window):
            names = set(inspect.signature(fn).parameters)
            assert not any("override" in n or "exception" in n or "force" in n for n in names)


# ===================================================================== gate
def intent(side: str, qty: int, ts: datetime) -> OrderIntent:
    built = xr.construct_intent(symbol="MES", side=side, quantity_micros=qty, ts_utc=ts)
    assert isinstance(built, OrderIntent)
    return built


class TestGate:
    xfa = AccountState(Phase.XFA, 100_000, 100_000, -100_000)

    def test_opening_order_after_flatten_refused(self) -> None:
        refusal = xr.check_order(intent("buy", 1, utc(2026, 7, 15, 20, 10)), self.xfa, 0, 100_000)
        assert refusal is not None and refusal.reason == "flatten_window_non_reducing_order"

    def test_reducing_order_after_flatten_allowed_but_flip_refused(self) -> None:
        ts = utc(2026, 7, 15, 20, 11)
        assert xr.check_order(intent("sell", 10, ts), self.xfa, 10, 100_000) is None
        flip = xr.check_order(intent("sell", 15, ts), self.xfa, 10, 100_000)
        assert flip is not None and flip.reason == "flatten_window_non_reducing_order"

    def test_new_exposure_refused_after_1508(self) -> None:
        ts = utc(2026, 7, 15, 20, 8, 30)  # 15:08:30 CT
        refusal = xr.check_order(intent("buy", 1, ts), self.xfa, 5, 100_000)
        assert refusal is not None and refusal.reason == "no_new_positions_after_cutoff"
        assert xr.check_order(intent("sell", 1, ts), self.xfa, 5, 100_000) is None
        assert xr.check_order(intent("buy", 1, utc(2026, 7, 15, 20, 7, 59)),
                              self.xfa, 5, 100_000) is None

    def test_position_limit_from_scaling_plan(self) -> None:
        ts = utc(2026, 7, 15, 15, 0)  # 10:00 CT
        # Prior balance $1,000 -> 20 micros. 15 + 6 = 21 > 20.
        refusal = xr.check_order(intent("buy", 6, ts), self.xfa, 15, 100_000)
        assert refusal is not None and refusal.reason == "position_limit_exceeded"
        assert xr.check_order(intent("buy", 5, ts), self.xfa, 15, 100_000) is None
        # Prior balance $1,500 -> 30 micros: the same order passes.
        assert xr.check_order(intent("buy", 6, ts), self.xfa, 15, 150_000) is None

    def test_refusals_come_in_fixed_order(self) -> None:
        breached = replace(self.xfa, status=Status.BREACHED)
        refusal = xr.check_order(intent("buy", 99, utc(2026, 7, 15, 20, 30)), breached, 0, 0)
        assert refusal is not None and refusal.reason == xr.GATE_REFUSAL_ORDER[0]

    @pytest.mark.parametrize(
        ("kwargs", "reason"),
        [
            ({"symbol": "ES"}, "intent_bad_symbol"),
            ({"side": "short"}, "intent_bad_side"),
            ({"quantity_micros": 0}, "intent_bad_quantity"),
            ({"quantity_micros": True}, "intent_bad_quantity"),
            ({"quantity_micros": 1.5}, "intent_bad_quantity"),
            ({"ts_utc": datetime(2026, 7, 15, 15, 0)}, "intent_bad_timestamp"),
            ({"ts_utc": None}, "intent_bad_timestamp"),
        ],
    )
    def test_malformed_intent_refused_at_construction(self, kwargs: dict, reason: str) -> None:
        base = {"symbol": "MES", "side": "buy", "quantity_micros": 1,
                "ts_utc": utc(2026, 7, 15, 15, 0)}
        built = xr.construct_intent(**{**base, **kwargs})
        assert isinstance(built, Refusal) and built.reason == reason

    def test_registered_rules_are_immutable(self) -> None:
        with pytest.raises(FrozenInstanceError):
            XFA_50K.mll_cents = 1  # type: ignore[misc]
        with pytest.raises(FrozenInstanceError):
            COMBINE_50K.best_day_max_bps = 9_999  # type: ignore[misc]
