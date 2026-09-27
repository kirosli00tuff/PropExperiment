"""The generalized Stage E engine under MesRules equals the unchanged MES engine (sim/engine.py)
fill for fill and day for day, on synthetic MES bars and random strategies (market and limit
orders, scale-ins, flips, construction refusals, MLL breaches with restarts, forced flattens,
sessions that end with no flatten-window bar, roll-blackout dates). No real data is read."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from screening.stage_e_engine import DayClose, Fill, run_engine
from screening.stage_e_mes_rules import MesRules
from sim.costs import load_slippage_table
from sim.engine import (
    DayCloseEvent,
    EngineConfig,
    FillEvent,
    IntentEvent,
    iter_bars,
    run_backtest,
)
from strategy.stage_e.interface import LegSpec
from tests._stage_e_synthetic import RandomMesStrategy, mes_frame

DAYS = tuple(date(2025, 6, 2) + timedelta(days=i) for i in range(21) if
             (date(2025, 6, 2) + timedelta(days=i)).weekday() < 5)
MES = (LegSpec("MES", True),)


def _both(frame, strategy_factory, blackout=frozenset()):
    table = load_slippage_table()
    config = EngineConfig(restart_on_terminal=True, roll_blackout=frozenset(blackout),
                          slippage_statistic="mean", mask_hindsight_fields=True)
    old = run_backtest(iter_bars(frame), strategy_factory(), config, table)
    new = run_engine({"MES": frame}, strategy_factory(), MES,
                     MesRules(table=table, roll_blackout=frozenset(blackout)))
    return old, new


def _fill_key(f) -> tuple:
    return (f.fill_ts_ns, f.decision_ts_ns, f.account_index, f.reason, f.side, f.qty, f.price,
            f.commission_cents, f.slippage_cents, f.gross_realized_cents, f.position_after,
            f.balance_after_cents, f.minutes_after_decision, f.order_type)


def _new_fill_key(f: Fill) -> tuple:
    return (f.fill_ts_ns, f.decision_ts_ns, f.account_index, f.reason, f.side, f.qty, f.price,
            f.commission_cents, f.slippage_cents, f.gross_realized_cents, f.position_after,
            f.balance_after_cents, f.minutes_after_decision, f.order_type)


def _day_key(d) -> tuple:
    return (d.trade_date, d.account_index, d.status_before, d.status_after, d.balance_cents,
            d.day_net_cents, d.floor_after_cents, d.strategy_fills)


def _assert_same(old, new) -> None:
    old_fills = [_fill_key(f) for f in old.events(FillEvent)]
    new_fills = [_new_fill_key(f) for f in new.events(Fill)]
    assert new_fills == old_fills
    assert [_day_key(d) for d in new.events(DayClose)] == [
        _day_key(d) for d in old.events(DayCloseEvent)]
    old_intents = [(e.decision_ts_ns, e.accepted, e.refusal.reason if e.refusal else None)
                   for e in old.events(IntentEvent)]
    from screening.stage_e_engine import IntentRecord

    new_intents = [(e.decision_ts_ns, e.accepted, e.refusal.reason if e.refusal else None)
                   for e in new.events(IntentRecord)]
    assert new_intents == old_intents
    assert new.final_state == old.final_state
    assert new.accounts_started == old.accounts_started


@pytest.mark.parametrize("seed", range(6))
def test_random_market_and_limit_orders_match_the_mes_engine(seed: int) -> None:
    frame = mes_frame(DAYS, seed)
    old, new = _both(frame, lambda: RandomMesStrategy(seed + 100))
    assert len(old.events(FillEvent)) > 20
    _assert_same(old, new)


def test_mll_breaches_and_restarts_match_the_mes_engine() -> None:
    frame = mes_frame(DAYS, 7, drift_ticks=-1.5, vol_ticks=6.0)
    old, new = _both(frame, lambda: RandomMesStrategy(7, max_qty=20, p_order=0.08, p_limit=0.0))
    assert old.accounts_started > 1  # at least one breach and restart happened
    _assert_same(old, new)


def test_sessions_without_a_flatten_bar_and_gaps_match_the_mes_engine() -> None:
    frame = mes_frame(DAYS, 11, end=(15, 5), gap_prob=0.05)  # no bar inside 15:10..
    old, new = _both(frame, lambda: RandomMesStrategy(11, p_order=0.1))
    assert any(f.reason == "forced_flatten_session_end" for f in old.events(FillEvent))
    _assert_same(old, new)


def test_roll_blackout_refusals_match_the_mes_engine() -> None:
    frame = mes_frame(DAYS, 13)
    blackout = frozenset(DAYS[3:6])
    old, new = _both(frame, lambda: RandomMesStrategy(13, p_order=0.1), blackout)
    assert any(e.refusal is not None and e.refusal.reason == "engine_roll_blackout"
               for e in old.events(IntentEvent))
    _assert_same(old, new)
