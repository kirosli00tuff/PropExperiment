"""Multi-day integration tests for rules/xfa_rules.py (Stage B, Task 1).

These tests chain many simulated trading days through the pure state-transition
functions and check state evolution across sequences long enough that a bug in
a "keeps trailing/keeps ratcheting/keeps excluding" loop would show up, but a
single-scenario test would not.

As in tests/test_xfa_rules.py, every expected value is HAND-COMPUTED from the
rules as written in rules/xfa_rules.py's docstrings and constants (never by
calling the code under test and pasting the result). A per-day table sits next
to each sequence as a comment. MES arithmetic (not used directly here except in
TestTrailingMllLongSequences.test_intraday_wick_breaches_mid_sequence) is the
same as in the existing suite: 1 tick = 0.25 pt = $1.25/micro.

Helpers below are local to this file (do not import run_days/xfa_with_window
from tests/test_xfa_rules.py).
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from rules import xfa_rules as xr
from rules.xfa_rules import AccountState, PayoutPath, Phase, Status

D0 = date(2026, 1, 5)


def close_day(state: AccountState, pnl_cents: int, day_index: int, trades: int = 1) -> AccountState:
    """Book one day's realized P&L (record_realized_pnl), then close it
    (close_trading_day). NOTE: record_realized_pnl already re-checks the MLL
    breach against the SAME floor with 0 unrealized (identical to the check
    close_trading_day would do), so a breach through THIS helper is always
    caught at the record_realized_pnl step, not in close_trading_day's own
    EOD breach branch -- that branch is structurally unreachable from this
    helper. ``day_index`` is 0-based and only labels the DayRecord's date."""
    booked = xr.record_realized_pnl(state, pnl_cents)
    return xr.close_trading_day(booked, D0 + timedelta(days=day_index), trades)


def close_many(state: AccountState, pnls_cents: list[int], start_index: int = 0) -> AccountState:
    """Chain close_day over a list of daily P&Ls, starting at day ``start_index``."""
    for offset, pnl in enumerate(pnls_cents):
        state = close_day(state, pnl, start_index + offset)
    return state


def utc(y: int, mo: int, d: int, h: int, mi: int, s: int = 0) -> datetime:
    return datetime(y, mo, d, h, mi, s, tzinfo=UTC)


# =====================================================================
# 1. Long trailing-MLL sequences: ratchet, lock, stay-locked-through-losses, breach.
# =====================================================================
class TestTrailingMllLongSequences:
    def test_xfa_32_day_sequence_ratchets_locks_and_breaches(self) -> None:
        # XFA: mll_cents=200_000, lock=0. floor := max(prev, min(balance-200_000, 0)).
        # Breach check at each close is against the floor IN FORCE DURING THE DAY,
        # i.e. the floor left by the PREVIOUS close (floor0 = -200_000 initially).
        #
        # day |   pnl    | balance  |  floor   | note
        #  1  | +50,000  |   50,000 | -150,000 | max(-200000, min(-150000,0)) = -150000
        #  2  | -20,000  |   30,000 | -150,000 | LOSS: min(-170000,0)=-170000 < -150000 -> unchanged
        #  3  | +70,000  |  100,000 | -100,000 | ratchet: min(-100000,0)=-100000 > -150000
        #  4  | +60,000  |  160,000 |  -40,000 | ratchet: min(-40000,0)=-40000 > -100000
        #  5  | -10,000  |  150,000 |  -40,000 | LOSS: min(-50000,0)=-50000 < -40000 -> unchanged
        #  6  | +60,000  |  210,000 |        0 | LOCK: $2,100 >= $2,000 -> min(10000,0)=0 (lock)
        #  7  | -30,000  |  180,000 |        0 | LOSS after lock: min(-20000,0)=-20000<0 -> stays 0
        #  8  | +90,000  |  270,000 |        0 | new high after lock: min(70000,0)=0 -> capped
        #  9  | -50,000  |  220,000 |        0 |
        # 10  | -80,000  |  140,000 |        0 | LOSS after lock: stays 0 (never moves down)
        # 11  | +40,000  |  180,000 |        0 |
        # 12  | -60,000  |  120,000 |        0 |
        # 13  | +30,000  |  150,000 |        0 |
        # 14  | -40,000  |  110,000 |        0 |
        # 15  | +20,000  |  130,000 |        0 |
        # 16  | -50,000  |   80,000 |        0 |
        # 17  | +10,000  |   90,000 |        0 |
        # 18  | -30,000  |   60,000 |        0 |
        # 19  |  +5,000  |   65,000 |        0 |
        # 20  | -20,000  |   45,000 |        0 |
        # 21  | +15,000  |   60,000 |        0 |
        # 22  | -25,000  |   35,000 |        0 |
        # 23  | +10,000  |   45,000 |        0 |
        # 24  | -15,000  |   30,000 |        0 |
        # 25  |  +5,000  |   35,000 |        0 |
        # 26  | -10,000  |   25,000 |        0 |
        # 27  |  +5,000  |   30,000 |        0 |
        # 28  |  -5,000  |   25,000 |        0 |
        # 29  |  +5,000  |   30,000 |        0 |
        # 30  |  -5,000  |   25,000 |        0 |
        # 31  |  +5,000  |   30,000 |        0 |
        # 32  | -30,000  |        0 |        0 | 0 <= floor(day31)=0 -> BREACHED (touch)
        pnls = [
            50_000, -20_000, 70_000, 60_000, -10_000, 60_000, -30_000, 90_000,
            -50_000, -80_000, 40_000, -60_000, 30_000, -40_000, 20_000, -50_000,
            10_000, -30_000, 5_000, -20_000, 15_000, -25_000, 10_000, -15_000,
            5_000, -10_000, 5_000, -5_000, 5_000, -5_000, 5_000, -30_000,
        ]
        expected_balances = [
            50_000, 30_000, 100_000, 160_000, 150_000, 210_000, 180_000, 270_000,
            220_000, 140_000, 180_000, 120_000, 150_000, 110_000, 130_000, 80_000,
            90_000, 60_000, 65_000, 45_000, 60_000, 35_000, 45_000, 30_000,
            35_000, 25_000, 30_000, 25_000, 30_000, 25_000, 30_000, 0,
        ]
        expected_floors = [
            -150_000, -150_000, -100_000, -40_000, -40_000, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ]
        assert len(pnls) == 32 and len(expected_balances) == 32 and len(expected_floors) == 32

        state = xr.new_xfa_account()
        actual_floors: list[int] = []
        for i, pnl in enumerate(pnls):
            state = close_day(state, pnl, i)
            assert state.balance_cents == expected_balances[i], f"day {i + 1} balance"
            assert state.mll_floor_cents == expected_floors[i], f"day {i + 1} floor"
            actual_floors.append(state.mll_floor_cents)
            if i < 31:
                assert state.status is Status.ACTIVE, f"day {i + 1} should still be active"
            else:
                assert state.status is Status.BREACHED, "day 32 must breach (touch)"

        # Named call-outs against the REAL account's recorded floors (each
        # hand-computed in the day table above), not a self-comparison of the
        # expected_* fixture:
        assert actual_floors[1] == -150_000  # day 2 loss: floor unchanged at -$1,500
        assert actual_floors[5] == 0  # day 6: lock reached at $2,000 -> floor $0
        assert actual_floors[7] == 0  # day 8: new high after lock still capped at $0
        assert actual_floors[9] == 0  # day 10 loss after lock: stays $0, not lower

        # Terminal: a further close changes nothing (close_trading_day is a no-op
        # once status is not ACTIVE).
        after = xr.close_trading_day(state, D0 + timedelta(days=99), 7)
        assert after == state

    def test_combine_25_day_sequence_ratchets_and_locks_without_passing(self) -> None:
        # Combine: mll_cents=200_000, lock=starting_balance=5_000_000.
        # We deliberately keep total profit under the pass target (base $3,000,
        # since best day here is $900 <= $1,500, so the target is never raised)
        # throughout, so the account stays ACTIVE for the whole 25-day loop.
        #
        # day |   pnl    |  balance  |   floor   | note
        #  1  | +80,000  | 5,080,000 | 4,880,000 | max(4800000,min(4880000,5000000))
        #  2  | -30,000  | 5,050,000 | 4,880,000 | LOSS: min(4850000,..)=4850000<4880000 -> same
        #  3  | +90,000  | 5,140,000 | 4,940,000 | ratchet
        #  4  | +70,000  | 5,210,000 | 5,000,000 | LOCK: min(5010000,5000000)=5000000 (lock cap)
        #  5  | -40,000  | 5,170,000 | 5,000,000 | LOSS after lock: min(4970000,..)=4970000<5M
        #  6  | +20,000  | 5,190,000 | 5,000,000 | new high after lock, still capped by 5M
        #  7  | -10,000  | 5,180,000 | 5,000,000 |
        #  8  | +15,000  | 5,195,000 | 5,000,000 |
        #  9  | -25,000  | 5,170,000 | 5,000,000 |
        # 10  | +10,000  | 5,180,000 | 5,000,000 |
        # 11  |  -5,000  | 5,175,000 | 5,000,000 |
        # 12  |  +5,000  | 5,180,000 | 5,000,000 |
        # 13  | -15,000  | 5,165,000 | 5,000,000 |
        # 14  | +10,000  | 5,175,000 | 5,000,000 |
        # 15  |  -5,000  | 5,170,000 | 5,000,000 |
        # 16  |  +5,000  | 5,175,000 | 5,000,000 |
        # 17  | -10,000  | 5,165,000 | 5,000,000 |
        # 18  |  +5,000  | 5,170,000 | 5,000,000 |
        # 19  |  -5,000  | 5,165,000 | 5,000,000 |
        # 20  |  +5,000  | 5,170,000 | 5,000,000 |
        # 21  |  -5,000  | 5,165,000 | 5,000,000 |
        # 22  |  +5,000  | 5,170,000 | 5,000,000 |
        # 23  |  -5,000  | 5,165,000 | 5,000,000 |
        # 24  |  +5,000  | 5,170,000 | 5,000,000 |
        # 25  |  -5,000  | 5,165,000 | 5,000,000 |
        # total profit final = 5,165,000 - 5,000,000 = 165,000 < 300,000 -> ACTIVE, not PASSED
        pnls = [
            80_000, -30_000, 90_000, 70_000, -40_000, 20_000, -10_000, 15_000,
            -25_000, 10_000, -5_000, 5_000, -15_000, 10_000, -5_000, 5_000,
            -10_000, 5_000, -5_000, 5_000, -5_000, 5_000, -5_000, 5_000, -5_000,
        ]
        expected_balances = [
            5_080_000, 5_050_000, 5_140_000, 5_210_000, 5_170_000, 5_190_000,
            5_180_000, 5_195_000, 5_170_000, 5_180_000, 5_175_000, 5_180_000,
            5_165_000, 5_175_000, 5_170_000, 5_175_000, 5_165_000, 5_170_000,
            5_165_000, 5_170_000, 5_165_000, 5_170_000, 5_165_000, 5_170_000, 5_165_000,
        ]
        expected_floors = [
            4_880_000, 4_880_000, 4_940_000, 5_000_000, 5_000_000, 5_000_000,
            5_000_000, 5_000_000, 5_000_000, 5_000_000, 5_000_000, 5_000_000,
            5_000_000, 5_000_000, 5_000_000, 5_000_000, 5_000_000, 5_000_000,
            5_000_000, 5_000_000, 5_000_000, 5_000_000, 5_000_000, 5_000_000, 5_000_000,
        ]
        assert len(pnls) == 25 and len(expected_balances) == 25 and len(expected_floors) == 25

        state = xr.new_combine_account()
        actual_floors: list[int] = []
        for i, pnl in enumerate(pnls):
            state = close_day(state, pnl, i)
            assert state.balance_cents == expected_balances[i], f"day {i + 1} balance"
            assert state.mll_floor_cents == expected_floors[i], f"day {i + 1} floor"
            actual_floors.append(state.mll_floor_cents)
            assert state.status is Status.ACTIVE, (
                f"day {i + 1} should stay active (25 days is not yet a breach)"
            )

        # Named call-outs against the REAL account's recorded floors, not a
        # self-comparison of the expected_* fixture:
        assert actual_floors[1] == 4_880_000  # day 2 loss: floor unchanged at $4,880,000
        assert actual_floors[3] == 5_000_000  # day 4: lock reached at starting balance
        assert actual_floors[5] == 5_000_000  # day 6 new high after lock: still capped

        progress = xr.evaluate_combine(state)
        # best day = day 3's $900; target = max(300_000, ceil(90_000*10_000/5_000)) = 300_000
        assert progress.best_day_cents == 90_000
        assert progress.effective_target_cents == 300_000  # not raised
        assert progress.total_profit_cents == 165_000
        assert not progress.passed

        # Day 26: after 25 days of ratcheting/locking without the balance ever
        # coming near the locked floor, a loss that exactly touches it still
        # breaches ("touch" == "<="):
        # balance 5,165,000 - 165,000 = 5,000,000 <= floor 5,000,000 -> BREACHED.
        breached = close_day(state, -165_000, day_index=25)
        assert breached.balance_cents == 5_000_000
        assert breached.mll_floor_cents == 5_000_000  # unchanged: breach precedes the trail step
        assert breached.status is Status.BREACHED
        assert breached.breach is not None and breached.breach.reason == "mll_breach"

    def test_intraday_wick_breaches_mid_sequence_although_close_would_not(self) -> None:
        # Reuse the first TEN days of the 32-day XFA sequence above -- a long
        # enough run to have already ratcheted through several floors and
        # locked at $0: balance $1,400, floor $0 after day 10 (see the table
        # in test_xfa_32_day_sequence...).
        first_ten = [
            50_000, -20_000, 70_000, 60_000, -10_000, 60_000, -30_000, 90_000, -50_000, -80_000,
        ]
        state = close_many(xr.new_xfa_account(), first_ten)
        assert (state.balance_cents, state.mll_floor_cents) == (140_000, 0)

        # Day 11 (per the same 32-day table) is a +$400 day (balance -> $1,800),
        # which on its own never comes near the locked $0 floor. But intraday,
        # long 10 MES @ 6000.00, the bar wicks to 5970.00:
        # ticks = (5970.00 - 6000.00) / 0.25 = -120; 10 micros x -120 ticks x $1.25 = -$1,500.00
        wick = xr.worst_intrabar_unrealized_cents(10, 6000.00, bar_high=6005.00, bar_low=5970.00)
        assert wick == -150_000
        # Equity $1,400 - $1,500 = -$100 <= floor $0 -> breach.
        breached = xr.apply_realtime_mll(state, wick)
        assert breached.status is Status.BREACHED
        assert breached.breach is not None and breached.breach.reason == "mll_breach"

        # Counterfactual: the close of day 11 alone (balance $1,400 + $400 = $1,800,
        # checked against the SAME floor $0 in force during the day) would NOT
        # breach: $1,800 <= $0 is false.
        assert xr.check_mll_realtime(state.mll_floor_cents, 140_000 + 40_000, 0) is None
        eod_only = close_day(state, 40_000, day_index=10)
        assert eod_only.status is Status.ACTIVE
        # ...but the real account, which saw the wick, is already breached and a
        # subsequent close of the same day changes nothing.
        after = xr.close_trading_day(breached, D0 + timedelta(days=10), 1)
        assert after == breached


# =====================================================================
# 2. Scaling-plan tier transitions across a balance path crossing $0/$1,500/$2,000.
# =====================================================================
class TestScalingPlanTransitions:
    def test_tier_transitions_both_directions_with_exact_boundaries(self) -> None:
        # XFA base = 2 lots (20 micros); >= $1,500 -> 3 lots (30); > $2,000 -> 5 lots (50).
        # The lock at $0 only engages once a CLOSE reaches $2,000 (balance - mll >= 0),
        # so the below-$0 crossings (days 1-3) happen while the floor is still very
        # negative (safe): no breach risk there.
        #
        # day |   pnl    |  balance  |  floor  | breach check (vs prior floor)
        #  1  | -50,000  |  -50,000  | -200,000| -50000 <= -200000(initial)? no
        #  2  | +130,000 |   80,000  | -120,000| 80000 <= -200000? no; crosses $0 upward
        #  3  | -100,000 |  -20,000  | -120,000| -20000 <= -120000? no; crosses $0 downward
        #  4  | +169,999 |  149,999  |  -50,001| BOUNDARY: closes at exactly $1,499.99
        #  5  |       +1 |  150,000  |  -50,000| BOUNDARY: closes at exactly $1,500.00
        #  6  |  +49,999 |  199,999  |      -1 |
        #  7  |       +1 |  200,000  |       0 | BOUNDARY: closes at exactly $2,000.00 (LOCK)
        #  8  |       +1 |  200,001  |       0 | BOUNDARY: closes at exactly $2,000.01
        #  9  |       -1 |  200,000  |       0 | crosses $2,000/$2,000.01 boundary downward
        # 10  | -50,000  |  150,000  |       0 |
        # 11  |       -1 |  149,999  |       0 | crosses $1,500/$1,499.99 boundary downward
        pnls = [-50_000, 130_000, -100_000, 169_999, 1, 49_999, 1, 1, -1, -50_000, -1]
        expected_balances = [
            -50_000, 80_000, -20_000, 149_999, 150_000, 199_999, 200_000, 200_001,
            200_000, 150_000, 149_999,
        ]
        expected_floors = [
            -200_000, -120_000, -120_000, -50_001, -50_000, -1, 0, 0, 0, 0, 0,
        ]
        assert len(pnls) == 11 and len(expected_balances) == 11 and len(expected_floors) == 11

        # prior_session_balance for day i is the close BEFORE day i (day 1's prior is
        # the account's initial balance, $0).
        expected_tier_micros = [20, 20, 20, 20, 20, 30, 30, 30, 50, 30, 30]

        state = xr.new_xfa_account()
        # actual_balances[i] = the REAL prior-session balance in force for day i+1's
        # orders (index 0 is the account's initial balance, $0, before any close).
        actual_balances: list[int] = [0]
        actual_tiers: list[int] = []
        for i, pnl in enumerate(pnls):
            state = close_day(state, pnl, i)
            assert state.status is Status.ACTIVE, f"day {i + 1} should not breach"
            assert state.balance_cents == expected_balances[i], f"day {i + 1} balance"
            assert state.mll_floor_cents == expected_floors[i], f"day {i + 1} floor"
            tier = xr.max_position_micros(Phase.XFA, actual_balances[i])
            assert tier == expected_tier_micros[i], (
                f"day {i + 1} tier (prior balance {actual_balances[i]})"
            )
            actual_tiers.append(tier)
            actual_balances.append(state.balance_cents)

        # Boundary spot-checks against the REAL tiers just computed above (not a
        # self-comparison of the expected_* fixture):
        assert actual_tiers[4] == 20  # prior $1,499.99 (day 4 close) -> base 2 lots
        assert actual_tiers[5] == 30  # prior $1,500.00 (day 5 close) -> 3 lots
        assert actual_tiers[7] == 30  # prior $2,000.00 (day 7 close) -> still 3 lots (not "above")
        assert actual_tiers[8] == 50  # prior $2,000.01 (day 8 close) -> 5 lots

        # A downward tier crossing: an order allowed using yesterday's close as the
        # prior session balance is refused using today's (lower) close as the prior.
        # Day 10's close was $1,500.00 (prior for day 11's orders -> 3 lots -> 30
        # micros: buy 25 from flat is allowed). Day 11's close was $1,499.99 (prior
        # for the NEXT day's orders -> base 2 lots -> 20 micros: the same buy 25 is
        # now refused). Both prior balances are read from the REAL sequence above,
        # not typed in as literals.
        assert actual_balances[10] == 150_000  # day 10's close (from the loop above)
        assert state.balance_cents == 149_999  # day 11's close == the final loop state
        ts = utc(2026, 1, 7, 16, 0)  # Wed 2026-01-07, 10:00 CT (CST, UTC-6): well before cutoff.
        order = xr.construct_intent(symbol="MES", side="buy", quantity_micros=25, ts_utc=ts)
        assert isinstance(order, xr.OrderIntent)
        allowed = xr.check_order(
            order, state, position_micros=0, prior_session_balance_cents=actual_balances[10]
        )
        assert allowed is None  # 25 <= 30 micros (yesterday's tier)
        refused = xr.check_order(
            order, state, position_micros=0, prior_session_balance_cents=state.balance_cents
        )
        assert refused is not None and refused.reason == "position_limit_exceeded"


# =====================================================================
# 3. Sequential payouts: multiple payouts in one account life, on each path.
# =====================================================================
class TestSequentialPayouts:
    def test_standard_path_three_payouts_with_a_no_profit_stretch(self) -> None:
        # --- Payout 1 -----------------------------------------------------
        # Days 1-5: five $200 winning days (each >= the $150 Standard threshold).
        # balance: 20000,40000,60000,80000,100000. floor trails: -180000,-160000,
        # -140000,-120000,-100000 (all ratchets, no lock since balance stays < $2,000).
        state = close_many(xr.new_xfa_account(), [20_000] * 5)
        assert (state.balance_cents, state.mll_floor_cents) == (100_000, -100_000)
        assert len(state.payout_window) == 5  # 5 closes recorded since account open
        # eligibility: 5 winners >= $150 (all 5 qualify), payouts_processed=0 so no
        # window-net-positive requirement applies yet.
        assert xr.standard_path_eligibility(state.payout_window, payouts_processed=0) is None
        # ceiling = 50% of $1,000 = $500; $2,000 Standard cap is not binding here.
        assert xr.check_payout_request(state, PayoutPath.STANDARD, 50_000) is None
        refusal = xr.check_payout_request(state, PayoutPath.STANDARD, 50_001)
        assert refusal is not None and refusal.reason == "payout_exceeds_balance_ceiling"
        outcome1 = xr.process_payout(state, PayoutPath.STANDARD, 50_000)
        assert outcome1.refusal is None  # $500 request <= $500 ceiling -> allowed
        state = outcome1.state
        # balance $1,000 - $500 = $500; floor RESETS from -$1,000 to $0 (a big jump:
        # the whole remaining $500 buffer is now the drawdown distance).
        assert state.balance_cents == 50_000
        assert state.mll_floor_cents == 0
        # debit_payout() empties the window and bumps payouts_processed to 1.
        assert state.payout_window == () and state.payouts_processed == 1

        # The request day's close is excluded from the next window (window len 0);
        # the day after that counts (window len 1).
        state = close_day(state, 5_000, day_index=5)  # balance 55,000; excluded
        assert state.payout_window == ()
        assert state.mll_floor_cents == 0  # 55000-200000=-145000 < 0 lock -> stays 0
        state = close_day(state, 20_000, day_index=6)  # balance 75,000; counted
        assert len(state.payout_window) == 1  # exclude_next_close_from_window fired once

        # --- Payout 2 -------------------------------------------------------
        # Four more $200 days (days 8-11) bring the window to 5 winning days
        # (days 7-11), each $200, window net $1,000 > $0 (payouts_processed=1 now
        # requires window net > 0 as well as the winner count).
        state = close_many(state, [20_000] * 4, start_index=7)
        assert state.balance_cents == 155_000
        assert len(state.payout_window) == 5  # day 7 (already counted) + days 8-11
        assert sum(d.net_pnl_cents for d in state.payout_window) == 100_000
        assert xr.standard_path_eligibility(state.payout_window, payouts_processed=1) is None
        # ceiling = 50% of $1,550 = $775.
        assert xr.check_payout_request(state, PayoutPath.STANDARD, 77_500) is None
        refusal = xr.check_payout_request(state, PayoutPath.STANDARD, 77_501)
        assert refusal is not None and refusal.reason == "payout_exceeds_balance_ceiling"
        outcome2 = xr.process_payout(state, PayoutPath.STANDARD, 77_500)
        assert outcome2.refusal is None  # $775 request <= $775 ceiling -> allowed
        state = outcome2.state
        assert state.balance_cents == 77_500
        assert state.mll_floor_cents == 0  # already 0 (locked); reset is idempotent here
        # second payout resets the window again and bumps the counter to 2.
        assert state.payout_window == () and state.payouts_processed == 2

        state = close_day(state, 5_000, day_index=12)  # excluded
        assert state.payout_window == ()
        state = close_day(state, 20_000, day_index=13)  # counted
        assert len(state.payout_window) == 1

        # --- No-profit stretch, then eligible again --------------------------
        # Four more $200 days give 5 winning days in the window (days 14-18), but
        # then one big loss drags the WINDOW NET to <= $0 while >= 5 winning days
        # still sit in the window: refused for lack of profit, not lack of winners.
        state = close_many(state, [20_000] * 4, start_index=14)
        assert len(state.payout_window) == 5
        assert sum(d.net_pnl_cents for d in state.payout_window) == 100_000
        assert xr.standard_path_eligibility(state.payout_window, payouts_processed=2) is None
        state = close_day(state, -150_000, day_index=18)
        # balance 102,500 + 20,000*4 - 150,000... tracked precisely: 102500->182500
        # (4 wins) -> 32,500 after the loss.
        assert state.balance_cents == 32_500
        window_net = sum(d.net_pnl_cents for d in state.payout_window)
        assert window_net == -50_000  # $1,000 - $1,500
        winners = [d for d in state.payout_window if d.net_pnl_cents >= 15_000]
        assert len(winners) == 5  # still >= 5 winning days
        refusal = xr.standard_path_eligibility(
            state.payout_window, payouts_processed=state.payouts_processed
        )
        assert refusal is not None and refusal.reason == "standard_no_profit_since_last_payout"
        # The same refusal, exercised through the real gate on the real account
        # state (not just the window helper), and proven to change nothing:
        gate_refusal = xr.check_payout_request(state, PayoutPath.STANDARD, 10_000)
        assert gate_refusal is not None
        assert gate_refusal.reason == "standard_no_profit_since_last_payout"
        no_op = xr.process_payout(state, PayoutPath.STANDARD, 10_000)
        assert no_op.refusal is not None
        assert no_op.refusal.reason == "standard_no_profit_since_last_payout"
        assert no_op.state == state  # a refusal changes nothing

        state = close_day(state, 100_000, day_index=19)
        assert state.balance_cents == 132_500
        window_net = sum(d.net_pnl_cents for d in state.payout_window)
        assert window_net == 50_000  # -$500 + $1,000 -> profitable again
        assert xr.standard_path_eligibility(state.payout_window, payouts_processed=2) is None

        # --- Payout 3 --------------------------------------------------------
        # ceiling = 50% of $1,325 = $662.50.
        assert xr.check_payout_request(state, PayoutPath.STANDARD, 66_250) is None
        refusal = xr.check_payout_request(state, PayoutPath.STANDARD, 66_251)
        assert refusal is not None and refusal.reason == "payout_exceeds_balance_ceiling"
        outcome3 = xr.process_payout(state, PayoutPath.STANDARD, 66_250)
        assert outcome3.refusal is None
        state = outcome3.state
        assert state.balance_cents == 66_250
        assert state.mll_floor_cents == 0
        assert state.payouts_processed == 3

        # After payout 3, losing exactly the remaining balance touches the reset
        # floor ($0): $662.50 - $662.50 = $0 <= floor $0 -> breach.
        breached = xr.record_realized_pnl(state, -66_250)
        assert breached.status is Status.BREACHED
        # One cent less loss stays active.
        still_active = xr.record_realized_pnl(state, -66_249)
        assert still_active.status is Status.ACTIVE

    def test_consistency_path_two_payouts_dilution_and_no_trade_day(self) -> None:
        # Day 1: a big $400 day (trades=1). Day 2: NO TRADE (pnl $0, trades=0) --
        # it must not count toward the 3-trading-day minimum, even though it IS
        # recorded in payout_window. Day 3: a $100 day.
        # balance: 40000 (day1), 40000 (day2, unchanged), 50000 (day3).
        # floor: -160000, -160000 (no change: pnl 0 -> min(-160000,0)=-160000, same),
        #        -150000.
        state = close_day(xr.new_xfa_account(), 40_000, day_index=0)
        state = close_day(state, 0, day_index=1, trades=0)
        state = close_day(state, 10_000, day_index=2)
        assert state.balance_cents == 50_000
        assert state.mll_floor_cents == -150_000

        # window has 3 RECORDS (every close is recorded), but only 2 TRADING
        # days (trades >= 1); the required minimum is 3 trading days. If the
        # no-trade day were wrongly counted, len(window)=3 >= 3 would pass this
        # check and eligibility would instead fall through to the profit/
        # largest-day checks below -- so getting THIS specific refusal reason
        # is the signal that the no-trade day was correctly excluded here,
        # not merely that some refusal was returned.
        assert len(state.payout_window) == 3  # every close recorded, no-trade day included
        traded = [d for d in state.payout_window if d.trades >= 1]
        assert len(traded) == 2  # the no-trade day does not count as a trading day
        refusal = xr.consistency_path_eligibility(state.payout_window)
        assert refusal is not None
        assert refusal.reason == "consistency_insufficient_trading_days"

        # Day 4: one more $100 day brings TRADING days to 3 (day 2's no-trade
        # record still sits in the window but still does not count).
        state = close_day(state, 10_000, day_index=3)
        assert state.balance_cents == 60_000
        assert state.mll_floor_cents == -140_000
        assert len(state.payout_window) == 4  # 4 records: 3 traded + 1 no-trade
        traded = [d for d in state.payout_window if d.trades >= 1]
        assert len(traded) == 3  # now meets the 3-trading-day minimum

        # Largest day ($400) / total ($600) = 66.67% > 40% -> refused, and for
        # a DIFFERENT reason than above, now that the day-count check passes.
        refusal = xr.consistency_path_eligibility(state.payout_window)
        assert refusal is not None and refusal.reason == "consistency_largest_day_exceeds_limit"

        # Dilute: two more $400 days. Traded days now: 40000,10000,10000,40000,40000
        # (day 2's no-trade record stays excluded from "traded" but stays in
        # payout_window). total = 140,000; largest = 40,000.
        # 40,000/140,000 = 28.57% <= 40% -> eligible.
        state = close_many(state, [40_000, 40_000], start_index=4)
        assert state.balance_cents == 140_000
        assert state.mll_floor_cents == -60_000  # 140000-200000=-60000 > -140000 -> ratchet
        traded = [d for d in state.payout_window if d.trades >= 1]
        assert len(traded) == 5
        assert sum(d.net_pnl_cents for d in traded) == 140_000
        assert max(d.net_pnl_cents for d in traded) == 40_000
        assert xr.consistency_path_eligibility(state.payout_window) is None

        # --- Payout 1 (Consistency) -------------------------------------------
        # Floor just before the payout is -$600 (-60,000 cents, from the ratchet
        # above), not yet reset -- the reset below is the jump from -$600 to $0.
        assert state.mll_floor_cents == -60_000
        # ceiling = 50% of $1,400 = $700; Consistency cap $3,000 not binding.
        assert xr.check_payout_request(state, PayoutPath.CONSISTENCY, 70_000) is None
        outcome1 = xr.process_payout(state, PayoutPath.CONSISTENCY, 70_000)
        assert outcome1.refusal is None  # $700 request <= $700 ceiling -> allowed
        state = outcome1.state
        # balance $1,400 - $700 = $700; floor RESETS from -$600 to $0.
        assert state.balance_cents == 70_000
        assert state.mll_floor_cents == 0
        assert state.payout_window == () and state.payouts_processed == 1

        # Request day excluded, next day counted (same pattern as the Standard path).
        state = close_day(state, 10_000, day_index=6, trades=1)  # excluded
        assert state.payout_window == ()
        state = close_day(state, 10_000, day_index=7, trades=1)  # counted
        assert len(state.payout_window) == 1  # exclude_next_close_from_window fired once

        # --- Payout 2 (Consistency) --------------------------------------------
        # Two more $100 days: window = 3 x $100, largest/total = 10,000/30,000 = 33.33%
        # <= 40% -> eligible.
        state = close_many(state, [10_000, 10_000], start_index=8)
        assert state.balance_cents == 110_000
        assert len(state.payout_window) == 3  # 3 trading days, none excluded this time
        assert xr.consistency_path_eligibility(state.payout_window) is None
        # ceiling = 50% of $1,100 = $550.
        assert xr.check_payout_request(state, PayoutPath.CONSISTENCY, 55_000) is None
        outcome2 = xr.process_payout(state, PayoutPath.CONSISTENCY, 55_000)
        assert outcome2.refusal is None  # $550 request <= $550 ceiling -> allowed
        state = outcome2.state
        assert state.balance_cents == 55_000
        assert state.mll_floor_cents == 0
        assert state.payouts_processed == 2


# =====================================================================
# 4. Combine: best-day rule raises the target multiple times; delayed pass.
# =====================================================================
class TestCombineRaisedTargetSequences:
    def test_target_raised_twice_then_passes_exactly_at_the_raising_close(self) -> None:
        # target(best) = max(300_000, ceil(best*10_000/5_000)) = max(300_000, best*2).
        #
        # day |   pnl    |  balance  |  total  |  best   | target | passed | note
        #  1  | +200,000 | 5,200,000 | 200,000 | 200,000 | 400,000|  no    | raises target
        #  2  |  +50,000 | 5,250,000 | 250,000 | 200,000 | 400,000|  no    |
        #  3  |  +60,000 | 5,310,000 | 310,000 | 200,000 | 400,000|  no    | clears base, not raised
        #  4  |  -30,000 | 5,280,000 | 280,000 | 200,000 | 400,000|  no    | loss delays the pass
        #  5  | +300,000 | 5,580,000 | 580,000 | 300,000 | 600,000|  no    | raises target again
        #  6  |  +20,000 | 5,600,000 | 600,000 | 300,000 | 600,000|  YES   | total == raised target
        # (floor trails 4,800,000 -> 5,000,000 on day 1 and stays locked at 5,000,000)
        state = xr.new_combine_account()

        # Day 1: best day $2,000; target = max(300000, 2000_00*2) = 400,000.
        state = close_day(state, 200_000, day_index=0)
        assert state.mll_floor_cents == 5_000_000
        progress = xr.evaluate_combine(state)
        assert (progress.total_profit_cents, progress.best_day_cents) == (200_000, 200_000)
        assert progress.effective_target_cents == 400_000
        assert progress.target_raised
        assert not progress.passed
        assert state.status is Status.ACTIVE
        assert state.breach is None  # raising the target never breaches (no Refusal recorded)

        # Day 2.
        state = close_day(state, 50_000, day_index=1)
        progress = xr.evaluate_combine(state)
        assert progress.total_profit_cents == 250_000
        assert progress.effective_target_cents == 400_000
        assert not progress.passed
        assert state.status is Status.ACTIVE

        # Day 3: total $3,100 clears the BASE $3,000 target but not the raised
        # $4,000 (best day is still day 1's $2,000, so the target has not moved:
        # max(300_000, ceil(200_000*10_000/5_000)) = 400_000).
        state = close_day(state, 60_000, day_index=2)
        progress = xr.evaluate_combine(state)
        assert progress.total_profit_cents == 310_000
        assert progress.total_profit_cents >= 300_000  # clears the base target...
        target = progress.effective_target_cents
        assert target == 400_000  # target unchanged: best day is still day 1's $2,000
        assert progress.total_profit_cents < target  # ...but not the raised one
        assert not progress.passed
        assert state.status is Status.ACTIVE

        # Day 4: a loss delays the pass further; best day is still day 1's
        # $2,000 (a loss can never raise the best-day target), so the target
        # is still 400,000.
        state = close_day(state, -30_000, day_index=3)
        progress = xr.evaluate_combine(state)
        assert progress.total_profit_cents == 280_000
        assert progress.effective_target_cents == 400_000
        assert not progress.passed
        assert state.status is Status.ACTIVE

        # Day 5: a bigger best day ($3,000) raises the target again to $6,000.
        state = close_day(state, 300_000, day_index=4)
        progress = xr.evaluate_combine(state)
        assert progress.best_day_cents == 300_000
        assert progress.effective_target_cents == 600_000
        assert progress.total_profit_cents == 580_000
        assert not progress.passed
        assert state.status is Status.ACTIVE  # ACTIVE the close before the pass

        # Day 6: total $6,000 == the (raised) target -> PASSED at this exact close.
        state = close_day(state, 20_000, day_index=5)
        progress = xr.evaluate_combine(state)
        assert progress.total_profit_cents == 600_000
        assert progress.effective_target_cents == 600_000
        assert progress.passed
        assert state.status is Status.PASSED

        # PASSED is terminal for close_trading_day: passing more days/trades
        # through it changes nothing -- the call's arguments are simply ignored
        # once status != ACTIVE (this call books no P&L; it only exercises the
        # close_trading_day no-op path itself).
        after = xr.close_trading_day(state, D0 + timedelta(days=50), 4)
        assert after == state
        assert after.status is Status.PASSED
