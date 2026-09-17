"""Topstep 50K Combine + Express Funded Account (XFA) rules, as pure functions.

Every function here is pure: no I/O, no network, no clock, no account. State
moves only through explicit transitions that return a NEW frozen
``AccountState``. Money is integer cents throughout, so percentage boundaries
(40.00% vs 40.01%) are compared exactly, never through floats.

Shape borrowed, not copied (docs/DECISIONS.md):

- HFExperiment ``intents.py`` / ``gate.py``: a frozen ``OrderIntent`` built
  only through ``construct_intent``, which refuses a malformed input before
  it can reach the gate; ``check_order`` returns ``None`` (proceed) or the
  FIRST ``Refusal`` in a fixed order, carrying a named reason and the exact
  arithmetic.
- AiTrader ``risk/risk_gate.hpp``: the gate is deny-only and final. Its hard
  limits are module constants bound here, not parameters — nothing upstream
  can pass a looser rule set. The only optional input
  (``cme_early_close_ct``) can move the flatten EARLIER, never later.

Sources and conflicts. Values come from the Stage A.1 prompt (project
research) and were checked against Topstep's help center on 2026-09-16.
Where the two disagree, the STRICTER value is encoded; every conflict is
listed in progress.md for reconfirmation at Stage A.2:

1. Combine consistency: prompt 50% of target; help center (Consistency
   article, updated week of 2026-09-14) now says 55%. 50% is stricter
   (raises the target sooner) -> 50% encoded.
2. Scaling plan at exactly $2,000: prompt says 5 lots; help center text says
   "$1,500 - $2,000: 3 Lots / Above $2,000: 5 Lots" -> 5 lots only ABOVE $2,000.
3. Payout minimum $125, and (after the first payout) Standard requires net
   P&L > $0 since the last payout: help center only -> encoded.
4. The 50%-of-balance payout ceiling applies to both paths (help center XFA
   Parameters, 2026-08-05); the prompt stated it for Standard only.
5. No new positions after 15:08 CT ("Risk Managers begin flattening at that
   time", Hours article 2026-07-13); on CME early-close days the flatten is 15
   minutes before the early close (Holiday Hours article 2026-09-01).
6. Payout-path day counts restart after every payout, and the payout-request
   day does not count toward the next window (Payout Policy 2026-09-03).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta
from enum import Enum
from zoneinfo import ZoneInfo

CT = ZoneInfo("America/Chicago")

# ------------------------------------------------------------ instrument ----
MES_SYMBOL = "MES"
MES_TICK_SIZE = 0.25
MES_TICK_VALUE_CENTS = 125  # $1.25 per tick per micro contract
# Topstep position limits are stated in mini (ES) lots; this project trades
# micros. 1 mini = 10 micros (help center Scaling Plan article, 2026-07-16).
MICROS_PER_MINI = 10
BPS = 10_000  # basis-point denominator for exact integer percentage checks


def _usd(cents: int) -> str:
    return f"${cents / 100:,.2f}"


class Phase(Enum):
    COMBINE = "combine"
    XFA = "xfa"


class Status(Enum):
    ACTIVE = "active"
    PASSED = "passed"  # Combine only
    BREACHED = "breached"


class PayoutPath(Enum):
    STANDARD = "standard"
    CONSISTENCY = "consistency"


@dataclass(frozen=True)
class Refusal:
    """One named refusal with its arithmetic spelled out."""

    reason: str
    arithmetic: str


# ------------------------------------------------------ registered rules ----
@dataclass(frozen=True)
class CombineRules:
    starting_balance_cents: int
    profit_target_cents: int
    mll_cents: int
    best_day_max_bps: int  # best day may be at most this share of the target
    max_position_minis: int


@dataclass(frozen=True)
class ScalingTier:
    threshold_cents: int
    inclusive: bool  # True: balance >= threshold; False: balance > threshold
    max_minis: int


@dataclass(frozen=True)
class PayoutPathRules:
    min_days: int
    winning_day_min_net_cents: int | None  # Standard only
    largest_day_max_bps: int | None  # Consistency only
    per_request_cap_cents: int


@dataclass(frozen=True)
class XfaRules:
    starting_balance_cents: int
    mll_cents: int
    mll_lock_cents: int
    post_payout_mll_floor_cents: int
    payout_balance_ceiling_bps: int
    min_payout_cents: int
    standard: PayoutPathRules
    consistency: PayoutPathRules
    base_max_minis: int
    scaling_tiers: tuple[ScalingTier, ...]


COMBINE_50K = CombineRules(
    starting_balance_cents=5_000_000,
    profit_target_cents=300_000,
    mll_cents=200_000,
    best_day_max_bps=5_000,  # conflict 1: stricter of 50% (prompt) / 55% (help center)
    max_position_minis=5,
)

XFA_50K = XfaRules(
    starting_balance_cents=0,
    mll_cents=200_000,  # floor starts at -$2,000
    mll_lock_cents=0,  # trails up to $0, then locks
    post_payout_mll_floor_cents=0,
    payout_balance_ceiling_bps=5_000,
    min_payout_cents=12_500,
    standard=PayoutPathRules(
        min_days=5,
        winning_day_min_net_cents=15_000,
        largest_day_max_bps=None,
        per_request_cap_cents=200_000,
    ),
    consistency=PayoutPathRules(
        min_days=3,
        winning_day_min_net_cents=None,
        largest_day_max_bps=4_000,
        per_request_cap_cents=300_000,
    ),
    base_max_minis=2,
    scaling_tiers=(
        ScalingTier(threshold_cents=150_000, inclusive=True, max_minis=3),
        ScalingTier(threshold_cents=200_000, inclusive=False, max_minis=5),  # conflict 2
    ),
)


# ----------------------------------------------------------------- state ----
@dataclass(frozen=True)
class DayRecord:
    trade_date: date
    net_pnl_cents: int
    trades: int


@dataclass(frozen=True)
class AccountState:
    phase: Phase
    balance_cents: int  # realized balance, including today's realized P&L
    session_start_balance_cents: int
    mll_floor_cents: int
    status: Status = Status.ACTIVE
    history: tuple[DayRecord, ...] = ()
    payout_window: tuple[DayRecord, ...] = ()  # XFA days since the last payout
    payouts_processed: int = 0
    exclude_next_close_from_window: bool = False
    breach: Refusal | None = None


def new_combine_account() -> AccountState:
    start = COMBINE_50K.starting_balance_cents
    return AccountState(Phase.COMBINE, start, start, start - COMBINE_50K.mll_cents)


def new_xfa_account() -> AccountState:
    start = XFA_50K.starting_balance_cents
    return AccountState(Phase.XFA, start, start, start - XFA_50K.mll_cents)


def _mll_params(phase: Phase) -> tuple[int, int]:
    """(MLL distance, lock level) for a phase."""
    if phase is Phase.COMBINE:
        return COMBINE_50K.mll_cents, COMBINE_50K.starting_balance_cents
    return XFA_50K.mll_cents, XFA_50K.mll_lock_cents


# ======================================================================
# MLL part (a): the end-of-day trailing floor. Moves once per day, up only.
# ======================================================================
def trail_mll_floor(prev_floor_cents: int, eod_balance_cents: int, phase: Phase) -> int:
    """Floor after a day's close: rises toward (EOD balance - MLL), capped at the
    lock level, and never moves down."""
    mll, lock = _mll_params(phase)
    return max(prev_floor_cents, min(eod_balance_cents - mll, lock))


# ======================================================================
# MLL part (b): the real-time breach check on realized + unrealized equity.
# Independent of (a): it reads the floor; it never moves it.
# ======================================================================
def price_to_ticks(price: float) -> int:
    ticks = round(price / MES_TICK_SIZE)
    if abs(ticks * MES_TICK_SIZE - price) > 1e-9:
        raise ValueError(f"price {price} is not on the MES {MES_TICK_SIZE} tick grid")
    return ticks


def unrealized_pnl_cents(position_micros: int, avg_entry_price: float, mark_price: float) -> int:
    """Signed position (long > 0) marked at ``mark_price``."""
    ticks = price_to_ticks(mark_price) - price_to_ticks(avg_entry_price)
    return position_micros * ticks * MES_TICK_VALUE_CENTS


def worst_intrabar_unrealized_cents(
    position_micros: int, avg_entry_price: float, bar_high: float, bar_low: float
) -> int:
    """Adverse extreme of a bar: the low for a long, the high for a short."""
    if position_micros == 0:
        return 0
    mark = bar_low if position_micros > 0 else bar_high
    return unrealized_pnl_cents(position_micros, avg_entry_price, mark)


def check_mll_realtime(
    floor_cents: int, balance_cents: int, unrealized_cents: int
) -> Refusal | None:
    """Breach iff equity touches or falls below the floor ("touches" => <=)."""
    equity = balance_cents + unrealized_cents
    if equity <= floor_cents:
        return Refusal(
            reason="mll_breach",
            arithmetic=f"equity {_usd(balance_cents)} realized + {_usd(unrealized_cents)} "
            f"unrealized = {_usd(equity)} <= MLL floor {_usd(floor_cents)}",
        )
    return None


def apply_realtime_mll(state: AccountState, unrealized_cents: int) -> AccountState:
    """Transition: evaluate (b) now. A breach ends the account."""
    if state.status is not Status.ACTIVE:
        return state
    breach = check_mll_realtime(state.mll_floor_cents, state.balance_cents, unrealized_cents)
    if breach is None:
        return state
    return replace(state, status=Status.BREACHED, breach=breach)


def record_realized_pnl(state: AccountState, realized_cents: int) -> AccountState:
    """Transition: a closed trade's net P&L (after commissions) hits the balance,
    then (b) is re-checked on the now-flat equity."""
    booked = replace(state, balance_cents=state.balance_cents + realized_cents)
    return apply_realtime_mll(booked, 0)


# ======================================================================
# Combine: the best-day rule RAISES the profit target; it never fails the account.
# ======================================================================
@dataclass(frozen=True)
class CombineProgress:
    total_profit_cents: int
    best_day_cents: int
    effective_target_cents: int
    target_raised: bool
    passed: bool


def effective_profit_target_cents(best_day_cents: int) -> int:
    """max(base target, best day / 50%)."""
    base = COMBINE_50K.profit_target_cents
    if best_day_cents <= 0:
        return base
    needed = -(-best_day_cents * BPS // COMBINE_50K.best_day_max_bps)  # ceiling division
    return max(base, needed)


def evaluate_combine(state: AccountState) -> CombineProgress:
    total = state.balance_cents - COMBINE_50K.starting_balance_cents
    best = max((d.net_pnl_cents for d in state.history), default=0)
    target = effective_profit_target_cents(best)
    return CombineProgress(
        total_profit_cents=total,
        best_day_cents=best,
        effective_target_cents=target,
        target_raised=target > COMBINE_50K.profit_target_cents,
        passed=total >= target,
    )


# ======================================================================
# End of day: EOD breach, (a) floor trail, day bookkeeping, Combine pass.
# ======================================================================
def close_trading_day(state: AccountState, trade_date: date, trades: int) -> AccountState:
    """Transition at the daily close.

    Order: EOD breach against the floor in force during the day, then trail
    the floor (part a), then record the day, then evaluate a Combine pass.
    """
    if state.status is not Status.ACTIVE:
        return state
    breach = check_mll_realtime(state.mll_floor_cents, state.balance_cents, 0)
    if breach is not None:
        return replace(state, status=Status.BREACHED, breach=breach)
    day = DayRecord(trade_date, state.balance_cents - state.session_start_balance_cents, trades)
    window = state.payout_window
    if state.phase is Phase.XFA and not state.exclude_next_close_from_window:
        window = (*window, day)
    closed = replace(
        state,
        mll_floor_cents=trail_mll_floor(state.mll_floor_cents, state.balance_cents, state.phase),
        session_start_balance_cents=state.balance_cents,
        history=(*state.history, day),
        payout_window=window,
        exclude_next_close_from_window=False,
    )
    if closed.phase is Phase.COMBINE and evaluate_combine(closed).passed:
        return replace(closed, status=Status.PASSED)
    return closed


# ======================================================================
# XFA payout paths.
# ======================================================================
def standard_path_eligibility(
    window: tuple[DayRecord, ...], payouts_processed: int
) -> Refusal | None:
    rules = XFA_50K.standard
    min_net = rules.winning_day_min_net_cents
    if min_net is None:
        raise ValueError("Standard path requires a winning-day threshold")
    winners = [d for d in window if d.net_pnl_cents >= min_net]
    if len(winners) < rules.min_days:
        return Refusal(
            reason="standard_insufficient_winning_days",
            arithmetic=f"{len(winners)} days with net >= {_usd(min_net)} "
            f"< required {rules.min_days}",
        )
    window_net = sum(d.net_pnl_cents for d in window)
    if payouts_processed > 0 and window_net <= 0:
        return Refusal(
            reason="standard_no_profit_since_last_payout",
            arithmetic=f"net since last payout {_usd(window_net)} <= $0.00",
        )
    return None


def consistency_path_eligibility(window: tuple[DayRecord, ...]) -> Refusal | None:
    rules = XFA_50K.consistency
    max_bps = rules.largest_day_max_bps
    if max_bps is None:
        raise ValueError("Consistency path requires a largest-day limit")
    traded = [d for d in window if d.trades >= 1]
    if len(traded) < rules.min_days:
        return Refusal(
            reason="consistency_insufficient_trading_days",
            arithmetic=f"{len(traded)} trading days < required {rules.min_days}",
        )
    total = sum(d.net_pnl_cents for d in traded)
    if total <= 0:
        return Refusal(
            reason="consistency_no_net_profit",
            arithmetic=f"window net profit {_usd(total)} <= $0.00",
        )
    largest = max(d.net_pnl_cents for d in traded)
    # Inclusive: largest / total <= 40%  <=>  largest * 10_000 <= 4_000 * total
    if largest * BPS > max_bps * total:
        return Refusal(
            reason="consistency_largest_day_exceeds_limit",
            arithmetic=f"largest day {_usd(largest)} / net {_usd(total)} = "
            f"{100 * largest / total:.4f}% > {max_bps / 100:.2f}%",
        )
    return None


def check_payout_request(
    state: AccountState, path: PayoutPath, amount_cents: int
) -> Refusal | None:
    """None to proceed, or the first refusal in fixed order."""
    if state.phase is not Phase.XFA:
        return Refusal("payout_not_xfa", f"phase {state.phase.value} has no payouts")
    if state.status is not Status.ACTIVE:
        return Refusal("account_not_active", f"status {state.status.value}")
    if path is PayoutPath.STANDARD:
        path_rules = XFA_50K.standard
        ineligible = standard_path_eligibility(state.payout_window, state.payouts_processed)
    else:
        path_rules = XFA_50K.consistency
        ineligible = consistency_path_eligibility(state.payout_window)
    if ineligible is not None:
        return ineligible
    if amount_cents < XFA_50K.min_payout_cents:
        return Refusal(
            reason="payout_below_minimum",
            arithmetic=f"{_usd(amount_cents)} < minimum {_usd(XFA_50K.min_payout_cents)}",
        )
    if amount_cents > path_rules.per_request_cap_cents:
        return Refusal(
            reason="payout_exceeds_dollar_cap",
            arithmetic=f"{_usd(amount_cents)} > {path.value} cap "
            f"{_usd(path_rules.per_request_cap_cents)}",
        )
    ceiling_bps = XFA_50K.payout_balance_ceiling_bps
    if amount_cents * BPS > ceiling_bps * state.balance_cents:
        return Refusal(
            reason="payout_exceeds_balance_ceiling",
            arithmetic=f"{_usd(amount_cents)} > {ceiling_bps / 100:.0f}% of balance "
            f"{_usd(state.balance_cents)} = {_usd(ceiling_bps * state.balance_cents // BPS)}",
        )
    return None


def debit_payout(state: AccountState, amount_cents: int) -> AccountState:
    """Transition: money leaves; the payout window restarts, and the request day
    will not count toward the next window. Does NOT touch the MLL."""
    return replace(
        state,
        balance_cents=state.balance_cents - amount_cents,
        session_start_balance_cents=state.session_start_balance_cents - amount_cents,
        payout_window=(),
        payouts_processed=state.payouts_processed + 1,
        exclude_next_close_from_window=True,
    )


def reset_mll_after_payout(state: AccountState) -> AccountState:
    """Transition: the MLL floor is set to a $0 balance "regardless of where it
    was before" (Payout Policy). The remaining balance is now the ENTIRE
    drawdown buffer.

    Its own named transition, not a side effect of the debit, because it is
    the most dangerous state change in the account's life: a floor sitting
    $2,000 under equity can jump to within a few hundred dollars of it.
    """
    return replace(state, mll_floor_cents=XFA_50K.post_payout_mll_floor_cents)


@dataclass(frozen=True)
class PayoutOutcome:
    state: AccountState
    refusal: Refusal | None


def process_payout(state: AccountState, path: PayoutPath, amount_cents: int) -> PayoutOutcome:
    """check -> debit -> reset MLL, each an explicit step. A refusal changes nothing."""
    refusal = check_payout_request(state, path, amount_cents)
    if refusal is not None:
        return PayoutOutcome(state, refusal)
    debited = debit_payout(state, amount_cents)
    return PayoutOutcome(reset_mll_after_payout(debited), None)


# ======================================================================
# Scaling Plan (limits follow the PRIOR session's closing balance).
# ======================================================================
def max_position_micros(phase: Phase, prior_session_balance_cents: int) -> int:
    if phase is Phase.COMBINE:
        return COMBINE_50K.max_position_minis * MICROS_PER_MINI
    minis = XFA_50K.base_max_minis
    for tier in XFA_50K.scaling_tiers:
        above = prior_session_balance_cents > tier.threshold_cents
        at = tier.inclusive and prior_session_balance_cents == tier.threshold_cents
        if above or at:
            minis = tier.max_minis
    return minis * MICROS_PER_MINI


# ======================================================================
# 15:10 CT auto-flatten: hard and non-overridable.
# ======================================================================
FLATTEN_TIME_CT = time(15, 10)
NO_NEW_POSITIONS_LEAD = timedelta(minutes=2)  # 15:08 CT on a normal day
HOLIDAY_FLATTEN_LEAD = timedelta(minutes=15)  # before a CME early close
REOPEN_TIME_CT = time(17, 0)
_FRIDAY, _SATURDAY, _SUNDAY = 4, 5, 6


def _minus(at: time, delta: timedelta) -> time:
    return (datetime.combine(date(2000, 1, 3), at) - delta).time()


def flatten_time_ct(cme_early_close_ct: time | None = None) -> time:
    """15:10 CT, or 15 minutes before a CME early close, whichever is earlier."""
    if cme_early_close_ct is None:
        return FLATTEN_TIME_CT
    return min(FLATTEN_TIME_CT, _minus(cme_early_close_ct, HOLIDAY_FLATTEN_LEAD))


def _to_ct(ts_utc: datetime) -> datetime:
    if ts_utc.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return ts_utc.astimezone(CT)


def _in_window_from(ts_utc: datetime, start_ct: time) -> bool:
    local = _to_ct(ts_utc)
    weekday, t = local.weekday(), local.time()
    if weekday == _FRIDAY:
        return start_ct <= t  # no 17:00 reopen on a Friday: flat through the weekend
    if weekday == _SATURDAY:
        return True
    if weekday == _SUNDAY:
        return t < REOPEN_TIME_CT
    return start_ct <= t < REOPEN_TIME_CT


def is_flatten_window(ts_utc: datetime, cme_early_close_ct: time | None = None) -> bool:
    """True from the flatten time until the 17:00 CT reopen, and all weekend."""
    return _in_window_from(ts_utc, flatten_time_ct(cme_early_close_ct))


def no_new_positions_time_ct(cme_early_close_ct: time | None = None) -> time:
    return _minus(flatten_time_ct(cme_early_close_ct), NO_NEW_POSITIONS_LEAD)


def is_no_new_positions_window(ts_utc: datetime, cme_early_close_ct: time | None = None) -> bool:
    return _in_window_from(ts_utc, no_new_positions_time_ct(cme_early_close_ct))


@dataclass(frozen=True)
class ForcedFlatten:
    side: str
    quantity_micros: int
    arithmetic: str


def required_flatten(
    position_micros: int, ts_utc: datetime, cme_early_close_ct: time | None = None
) -> ForcedFlatten | None:
    """The close the rules force, or None. There is deliberately no override input."""
    if position_micros == 0 or not is_flatten_window(ts_utc, cme_early_close_ct):
        return None
    return ForcedFlatten(
        side="sell" if position_micros > 0 else "buy",
        quantity_micros=abs(position_micros),
        arithmetic=f"position {position_micros} open at {_to_ct(ts_utc):%a %H:%M:%S} CT; "
        f"flatten is {flatten_time_ct(cme_early_close_ct):%H:%M} CT",
    )


# ======================================================================
# Intent + deny-only gate.
# ======================================================================
SIDES = ("buy", "sell")
GATE_REFUSAL_ORDER = (
    "account_not_active",
    "flatten_window_non_reducing_order",
    "no_new_positions_after_cutoff",
    "position_limit_exceeded",
)


@dataclass(frozen=True)
class OrderIntent:
    """One would-be MES order. ``construct_intent`` is the only blessed path."""

    symbol: str
    side: str
    quantity_micros: int
    ts_utc: datetime

    @property
    def signed_quantity(self) -> int:
        return self.quantity_micros if self.side == "buy" else -self.quantity_micros


def construct_intent(
    *,
    symbol: str | None,
    side: str | None,
    quantity_micros: int | None,
    ts_utc: datetime | None,
) -> OrderIntent | Refusal:
    """An intent, or the named construction refusal. Nothing malformed travels."""
    if symbol != MES_SYMBOL:
        return Refusal("intent_bad_symbol", f"symbol {symbol!r} is not {MES_SYMBOL}")
    if side not in SIDES:
        return Refusal("intent_bad_side", f"side {side!r} is not one of {SIDES}")
    if (
        isinstance(quantity_micros, bool)
        or not isinstance(quantity_micros, int)
        or quantity_micros <= 0
    ):
        return Refusal(
            "intent_bad_quantity", f"quantity {quantity_micros!r} is not a positive integer"
        )
    if ts_utc is None or ts_utc.tzinfo is None:
        return Refusal("intent_bad_timestamp", f"timestamp {ts_utc!r} is absent or naive")
    return OrderIntent(symbol, side, quantity_micros, ts_utc)


def is_reducing(position_micros: int, signed_quantity: int) -> bool:
    """Strictly toward flat without flipping through it."""
    after = position_micros + signed_quantity
    same_side_or_flat = after == 0 or (after > 0) == (position_micros > 0)
    return position_micros != 0 and abs(after) < abs(position_micros) and same_side_or_flat


def check_order(
    intent: OrderIntent,
    state: AccountState,
    position_micros: int,
    prior_session_balance_cents: int,
    cme_early_close_ct: time | None = None,
) -> Refusal | None:
    """None to proceed, or the first refusal in ``GATE_REFUSAL_ORDER``.

    Deny-only and final: the limits are the registered 50K constants, and the
    strategy layer has no input through which to request a flatten exception.
    """
    after = position_micros + intent.signed_quantity
    reducing = is_reducing(position_micros, intent.signed_quantity)
    if state.status is not Status.ACTIVE:
        return Refusal("account_not_active", f"status {state.status.value}")
    if not reducing and is_flatten_window(intent.ts_utc, cme_early_close_ct):
        return Refusal(
            "flatten_window_non_reducing_order",
            f"{intent.side} {intent.quantity_micros} takes position {position_micros} -> "
            f"{after} at/after flatten {flatten_time_ct(cme_early_close_ct):%H:%M} CT",
        )
    if not reducing and is_no_new_positions_window(intent.ts_utc, cme_early_close_ct):
        return Refusal(
            "no_new_positions_after_cutoff",
            f"position {position_micros} -> {after} is not reducing at/after "
            f"{no_new_positions_time_ct(cme_early_close_ct):%H:%M} CT",
        )
    limit = max_position_micros(state.phase, prior_session_balance_cents)
    if not reducing and abs(after) > limit:
        return Refusal(
            "position_limit_exceeded",
            f"|{after}| micros > limit {limit} micros "
            f"(prior session balance {_usd(prior_session_balance_cents)}, {state.phase.value})",
        )
    return None
