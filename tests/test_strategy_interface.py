"""Interface conformance tests for strategy/interface.py and its two reference
strategies (Stage C, Task 1). Every expected value is hand-computed in a
comment beside the assert that uses it; none is read back from the code
under test.
"""

from __future__ import annotations

import dataclasses
from dataclasses import FrozenInstanceError
from datetime import UTC, date, datetime, time

import pytest

from rules.xfa_rules import MES_SYMBOL, OrderIntent, Phase, Refusal, Status
from strategy.interface import (
    BAR_FIELD_AVAILABILITY,
    HINDSIGHT_FIELDS,
    NS_PER_BAR,
    NS_PER_S,
    AccountView,
    Bar,
    Strategy,
    construct_bar,
    market_intent,
)
from strategy.null_strategy import NullStrategy
from strategy.random_baseline import RandomBaseline, coin_uniforms

D0 = date(2026, 1, 5)
_UTC_EPOCH = datetime(1970, 1, 1, tzinfo=UTC)


def ts_ns(dt: datetime) -> int:
    """UTC datetime -> ns since epoch. Exact for whole-minute timestamps: the
    fractional part of total_seconds() is always 0, and the integer part is
    far below 2**53, so the float -> int conversion loses nothing."""
    seconds = int((dt - _UTC_EPOCH).total_seconds())
    return seconds * NS_PER_S


T0 = ts_ns(datetime(2026, 1, 5, 14, 30, tzinfo=UTC))


def _valid_kwargs(ts_event_ns: int = T0, **overrides: object) -> dict[str, object]:
    """A construct_bar kwargs dict known to be valid; overrides layer on top."""
    base: dict[str, object] = dict(
        ts_event_ns=ts_event_ns,
        open=6000.00,
        high=6000.50,
        low=5999.75,
        close=6000.25,
        volume=10,
        instrument_id=12345,
        raw_symbol="MESH6",
        trade_date=D0,
        in_flatten_window=False,
        in_no_new_positions_window=False,
        early_halt_ct=None,
        in_scheduled_closure=False,
        is_roll_session=False,
        gap_before_minutes=0,
        vendor_degraded_day=False,
    )
    base.update(overrides)
    return base


def build_bar(ts_event_ns: int = T0, **overrides: object) -> Bar:
    result = construct_bar(**_valid_kwargs(ts_event_ns, **overrides))
    assert isinstance(result, Bar), f"expected a Bar, got a refusal: {result!r}"
    return result


def bar_sequence(n: int, start_ts_ns: int = T0) -> list[Bar]:
    return [build_bar(start_ts_ns + i * NS_PER_BAR) for i in range(n)]


def account_view(**overrides: object) -> AccountView:
    base: dict[str, object] = dict(
        phase=Phase.XFA,
        status=Status.ACTIVE,
        trade_date=D0,
        balance_cents=0,
        mll_floor_cents=-200_000,
        prior_session_balance_cents=0,
        max_position_micros=20,
        position_micros=0,
        pending_signed_micros=0,
        avg_entry_price=None,
        unrealized_at_close_cents=0,
    )
    base.update(overrides)
    return AccountView(**base)


# ================================================================ construct_bar
def test_construct_bar_returns_bar_for_valid_input() -> None:
    result = construct_bar(**_valid_kwargs())
    assert isinstance(result, Bar)
    assert result.ts_event_ns == T0
    assert result.close == 6000.25


BAR_REFUSAL_CASES: list[tuple[str, dict[str, object], str]] = [
    ("timestamp_non_int", {"ts_event_ns": "not-an-int"}, "bar_bad_timestamp"),
    ("timestamp_bool", {"ts_event_ns": True}, "bar_bad_timestamp"),
    ("timestamp_non_positive", {"ts_event_ns": 0}, "bar_bad_timestamp"),
    ("timestamp_off_minute", {"ts_event_ns": T0 + 1}, "bar_bad_timestamp"),
    ("bad_price_not_a_number", {"open": "6000.00"}, "bar_bad_price"),
    ("off_tick_price", {"close": 6000.10}, "bar_off_tick"),
    ("ohlc_inconsistent_high_below_close", {"high": 6000.00}, "bar_ohlc_inconsistent"),
    ("negative_volume", {"volume": -1}, "bar_bad_volume"),
    ("bool_volume", {"volume": True}, "bar_bad_volume"),
    ("trade_date_is_datetime", {"trade_date": datetime(2026, 1, 5, tzinfo=UTC)},
     "bar_bad_trade_date"),
    ("trade_date_is_str", {"trade_date": "2026-01-05"}, "bar_bad_trade_date"),
    ("early_halt_not_a_time", {"early_halt_ct": "15:00"}, "bar_bad_early_halt"),
    ("flag_not_bool", {"is_roll_session": 1}, "bar_bad_flag"),
    ("flatten_without_no_new_positions",
     {"in_flatten_window": True, "in_no_new_positions_window": False}, "bar_bad_flag"),
    ("negative_gap", {"gap_before_minutes": -1}, "bar_bad_gap"),
]


@pytest.mark.parametrize(
    ("overrides", "expected_reason"),
    [(case[1], case[2]) for case in BAR_REFUSAL_CASES],
    ids=[case[0] for case in BAR_REFUSAL_CASES],
)
def test_construct_bar_refuses_malformed_input(
    overrides: dict[str, object], expected_reason: str
) -> None:
    result = construct_bar(**_valid_kwargs(**overrides))
    assert isinstance(result, Refusal)
    assert result.reason == expected_reason


def test_bar_is_frozen() -> None:
    bar = build_bar()
    with pytest.raises(FrozenInstanceError):
        bar.close = 9999.0  # type: ignore[misc]


def test_bar_uses_slots() -> None:
    bar = build_bar()
    assert not hasattr(bar, "__dict__")


def test_decision_ts_ns_is_ts_event_ns_plus_60_seconds() -> None:
    bar = build_bar(T0)
    expected = T0 + 60_000_000_000  # 60 s * 1_000_000_000 ns/s, hand-computed
    assert bar.decision_ts_ns == expected


def test_decision_ts_utc_is_one_minute_after_bar_open() -> None:
    open_ts = ts_ns(datetime(2026, 7, 15, 14, 30, 0, tzinfo=UTC))
    bar = build_bar(open_ts)
    assert bar.decision_ts_utc == datetime(2026, 7, 15, 14, 31, 0, tzinfo=UTC)


def test_bar_field_availability_covers_every_field_with_a_known_class() -> None:
    field_names = {f.name for f in dataclasses.fields(Bar)}
    assert set(BAR_FIELD_AVAILABILITY) == field_names
    assert set(BAR_FIELD_AVAILABILITY.values()) <= {"bar_close", "calendar", "hindsight"}
    assert HINDSIGHT_FIELDS == ("vendor_degraded_day",)


# ================================================================ market_intent
def test_market_intent_stamps_decision_time_and_mes_symbol() -> None:
    bar = build_bar()
    intent = market_intent(bar, "buy", 5)
    assert isinstance(intent, OrderIntent)
    assert intent.ts_utc == bar.decision_ts_utc
    assert intent.symbol == MES_SYMBOL  # "MES"
    assert intent.quantity_micros == 5


def test_market_intent_bad_side_is_refused() -> None:
    bar = build_bar()
    result = market_intent(bar, "hold", 5)
    assert isinstance(result, Refusal)
    assert result.reason == "intent_bad_side"


# ================================================================ AccountView
def test_account_view_is_frozen() -> None:
    view = account_view()
    with pytest.raises(FrozenInstanceError):
        view.balance_cents = 1  # type: ignore[misc]


# ================================================================ Strategy protocol
def test_null_strategy_satisfies_the_strategy_protocol() -> None:
    assert isinstance(NullStrategy(), Strategy)


def test_random_baseline_satisfies_the_strategy_protocol() -> None:
    assert isinstance(RandomBaseline(seed=1), Strategy)


# ================================================================ NullStrategy
def test_null_strategy_emits_nothing_across_bars_and_account_states() -> None:
    strat = NullStrategy()
    bars = bar_sequence(500)
    accounts = [
        account_view(),  # flat
        account_view(position_micros=20, avg_entry_price=6000.0),  # long
        account_view(position_micros=-20, avg_entry_price=6000.0),  # short
        account_view(pending_signed_micros=10),  # pending
    ]
    for bar in bars:
        for account in accounts:
            assert strat.on_bar(bar, account) == ()


# ================================================================ RandomBaseline
def _mutated_overrides(i: int) -> dict[str, object]:
    """A different, but still valid, value for every field RandomBaseline must
    never read: every price, volume, flag, early_halt_ct, gap_before_minutes,
    raw_symbol and instrument_id."""
    open_p = 6000.00 + 0.25 * (i % 40)
    close_p = open_p + 0.25 * ((i % 3) - 1)  # open-0.25, open, or open+0.25
    high_p = max(open_p, close_p) + 0.25 * (i % 5)
    low_p = min(open_p, close_p) - 0.25 * (i % 5)
    is_flatten = i % 7 == 0
    return dict(
        open=open_p,
        high=high_p,
        low=low_p,
        close=close_p,
        volume=(i % 500) + 1,
        instrument_id=99_999 - i,
        raw_symbol=f"MESZ{i % 9}",
        in_flatten_window=is_flatten,
        in_no_new_positions_window=is_flatten or (i % 3 == 0),
        early_halt_ct=time(9, 30) if i % 11 == 0 else None,
        in_scheduled_closure=i % 13 == 0,
        is_roll_session=i % 17 == 0,
        gap_before_minutes=i % 4,
        vendor_degraded_day=i % 19 == 0,
    )


def simulate_positions(
    strategy: RandomBaseline, bars: list[Bar]
) -> list[tuple[OrderIntent | Refusal, ...]]:
    """A minimal test-only harness (NOT sim/engine.py): each emitted intent is
    reflected into the NEXT bar's position immediately, so the strategy's own
    flat -> entry -> exit -> flat state machine is exercised across many bars
    without depending on the real fill model or engine."""
    position = 0
    outputs: list[tuple[OrderIntent | Refusal, ...]] = []
    for bar in bars:
        account = account_view(position_micros=position, pending_signed_micros=0)
        result = tuple(strategy.on_bar(bar, account))
        outputs.append(result)
        for item in result:
            assert isinstance(item, OrderIntent)
            position += item.signed_quantity
    return outputs


def test_coin_uniforms_returns_values_in_the_unit_interval() -> None:
    for seed in range(5):
        for i in range(1000):
            u1, u2 = coin_uniforms(seed, T0 + i * NS_PER_BAR)
            assert 0.0 <= u1 < 1.0
            assert 0.0 <= u2 < 1.0


def test_random_baseline_is_deterministic_for_the_same_seed() -> None:
    bars = bar_sequence(2000)
    outputs_a = simulate_positions(RandomBaseline(seed=42), bars)
    outputs_b = simulate_positions(RandomBaseline(seed=42), bars)
    assert outputs_a == outputs_b


def test_random_baseline_differs_across_seeds() -> None:
    bars = bar_sequence(2000)
    outputs_a = simulate_positions(RandomBaseline(seed=1), bars)
    outputs_b = simulate_positions(RandomBaseline(seed=2), bars)
    assert outputs_a != outputs_b


def test_random_baseline_is_blind_to_price_volume_and_every_flag() -> None:
    """PRICE/FLAG BLINDNESS: this is the exact property the leakage-canary suite
    (tests/test_leakage_canaries.py) relies on. A strategy that structurally
    cannot see a field cannot leak information through it, so proving
    RandomBaseline is unmoved by every price, volume, and calendar/hindsight
    flag column certifies the harness's field-isolation mechanism itself,
    independent of any one strategy's trading logic.
    """
    n = 2000
    timestamps = [T0 + i * NS_PER_BAR for i in range(n)]
    baseline_bars = [build_bar(ts) for ts in timestamps]
    mutated_bars = [build_bar(ts, **_mutated_overrides(i)) for i, ts in enumerate(timestamps)]
    outputs_baseline = simulate_positions(RandomBaseline(seed=99), baseline_bars)
    outputs_mutated = simulate_positions(RandomBaseline(seed=99), mutated_bars)
    assert outputs_baseline == outputs_mutated


def test_random_baseline_intents_carry_the_bars_decision_time() -> None:
    bars = bar_sequence(2000)
    outputs = simulate_positions(RandomBaseline(seed=3), bars)
    for bar, result in zip(bars, outputs, strict=True):
        for item in result:
            assert isinstance(item, OrderIntent)
            assert item.ts_utc == bar.decision_ts_utc


def test_random_baseline_emits_nothing_while_an_order_is_pending() -> None:
    # Arrange: probabilities pinned to 1.0 so, absent the pending check, a
    # coin flip in [0, 1) would ALWAYS clear the entry/exit threshold.
    bar = build_bar()
    strat = RandomBaseline(seed=1, entry_probability=1.0, exit_probability=1.0)
    flat_pending = account_view(position_micros=0, pending_signed_micros=5)
    long_pending = account_view(position_micros=20, pending_signed_micros=-5)
    # Act / Assert
    assert strat.on_bar(bar, flat_pending) == ()
    assert strat.on_bar(bar, long_pending) == ()


def test_random_baseline_exit_closes_the_whole_exposure_on_the_opposite_side() -> None:
    bar = build_bar()
    strat = RandomBaseline(seed=5, exit_probability=1.0)  # always exits when exposed
    long_result = strat.on_bar(bar, account_view(position_micros=30))
    assert len(long_result) == 1
    assert long_result[0].side == "sell"
    assert long_result[0].quantity_micros == 30  # abs(30), hand-computed

    short_result = strat.on_bar(bar, account_view(position_micros=-30))
    assert len(short_result) == 1
    assert short_result[0].side == "buy"
    assert short_result[0].quantity_micros == 30  # abs(-30), hand-computed


def test_random_baseline_entry_frequency_and_side_split_match_probability() -> None:
    # Arrange: N bars, held flat throughout, default entry_probability = 1/30.
    n = 20_000
    p = 1 / 30
    bars = bar_sequence(n)
    strat = RandomBaseline(seed=123)
    flat = account_view()

    # Act
    entries = 0
    buy_entries = 0
    for bar in bars:
        result = strat.on_bar(bar, flat)
        if result:
            entries += 1
            if result[0].side == "buy":
                buy_entries += 1

    # Assert: entry count within 4 binomial standard errors of n*p.
    # expected = 20000 * 1/30 = 666.666...
    # se = sqrt(n*p*(1-p)) = sqrt(20000 * 1/30 * 29/30) = sqrt(644.444...) = 25.386
    # 4*se = 101.54
    expected_entries = n * p
    se_entries = (n * p * (1 - p)) ** 0.5
    assert abs(entries - expected_entries) <= 4 * se_entries

    # Assert: buy share of entries within 4 SE of 0.5.
    # se = sqrt(0.5*0.5/entries); entries ~= 666.67 -> se ~= sqrt(0.000375) = 0.01936
    se_buy_share = (0.25 / entries) ** 0.5
    assert abs(buy_entries / entries - 0.5) <= 4 * se_buy_share


def test_random_baseline_exit_frequency_matches_probability() -> None:
    # Arrange: N bars, held with a fixed long exposure throughout, default
    # exit_probability = 1/15.
    n = 20_000
    p = 1 / 15
    bars = bar_sequence(n)
    strat = RandomBaseline(seed=321)
    long_exposed = account_view(position_micros=30)

    # Act
    exits = sum(1 for bar in bars if strat.on_bar(bar, long_exposed))

    # Assert: exit count within 4 binomial standard errors of n*p.
    # expected = 20000 * 1/15 = 1333.333...
    # se = sqrt(n*p*(1-p)) = sqrt(20000 * 1/15 * 14/15) = sqrt(1244.444...) = 35.278
    # 4*se = 141.11
    expected_exits = n * p
    se_exits = (n * p * (1 - p)) ** 0.5
    assert abs(exits - expected_exits) <= 4 * se_exits


RANDOM_BASELINE_REFUSAL_CASES: list[tuple[str, dict[str, object]]] = [
    ("seed_not_int", {"seed": 1.5}),
    ("seed_is_bool", {"seed": True}),
    ("entry_probability_zero", {"entry_probability": 0.0}),
    ("entry_probability_above_one", {"entry_probability": 1.5}),
    ("entry_probability_negative", {"entry_probability": -0.1}),
    ("exit_probability_zero", {"exit_probability": 0.0}),
    ("exit_probability_above_one", {"exit_probability": 1.1}),
    ("quantity_zero", {"quantity_micros": 0}),
    ("quantity_negative", {"quantity_micros": -1}),
    ("quantity_is_bool", {"quantity_micros": True}),
    ("quantity_not_int", {"quantity_micros": 1.5}),
]


@pytest.mark.parametrize(
    "overrides",
    [case[1] for case in RANDOM_BASELINE_REFUSAL_CASES],
    ids=[case[0] for case in RANDOM_BASELINE_REFUSAL_CASES],
)
def test_random_baseline_constructor_refuses_bad_input(overrides: dict[str, object]) -> None:
    kwargs: dict[str, object] = {"seed": 1, **overrides}
    with pytest.raises(ValueError):
        RandomBaseline(**kwargs)
