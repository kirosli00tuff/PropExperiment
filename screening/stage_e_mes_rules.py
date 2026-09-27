"""sim/engine.py's rules as a rule set of the generalized Stage E engine (Stage E.2b Task 1).

``MesRules`` plugs into screening.stage_e_engine.run_engine for one MES leg: the MES tick grid and
$1.25 tick, sim/costs.py's slippage table, 61 cents a side, rules/xfa_rules.py's 15:10 flatten and
15:08 no-new-positions time, the 20-micro XFA position gate, and no closure check (sim/engine.py
has none; OC-T's closure rule is the Stage E rule set's). It exists so the MES regressions prove
that the generalized loop reproduces D.1 bit for bit (tests/test_stage_e_engine_mes_parity.py,
tests/test_stage_e_mes_regression.py).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date
from typing import Any

from rules import xfa_rules as xr
from rules.xfa_rules import AccountState, OrderIntent, Phase, Refusal
from screening.stage_e_engine import _Normalized, _Order, _Run
from sim.fill_model import FillCost
from strategy.interface import AccountView, Bar, PassiveIntent, passive_refusal


@dataclass(frozen=True)
class MesRules:
    """sim/engine.py's rules for one MES leg (the MES regressions)."""

    table: Any  # sim.costs.SlippageTable
    roll_blackout: frozenset[date]
    slippage_statistic: str = "mean"
    restart_on_terminal: bool = True
    mask_hindsight_fields: bool = True
    phase: Phase = Phase.XFA

    ROOT = "MES"
    skip_closure_bars = False  # sim/engine.py has no closure check; the MES parity keeps it so

    def new_account(self) -> AccountState:
        return xr.new_combine_account() if self.phase is Phase.COMBINE else xr.new_xfa_account()

    def bar_iterator(self, root: str) -> Any:
        from sim.engine import iter_bars

        return iter_bars

    def tick_value(self, root: str) -> int:
        from sim.fill_model import MES_TICK_VALUE_CENTS

        return MES_TICK_VALUE_CENTS

    def price_ticks(self, root: str, price: float) -> int:
        return xr.price_to_ticks(price)

    def ticks_price(self, root: str, ticks: int) -> float:
        return ticks * xr.MES_TICK_SIZE

    def observe(self, run: _Run, ts: int, bars: Mapping[str, Bar]) -> None:
        return None

    def fill_cost(self, run: _Run, order: _Order, bar: Bar, qty: int, side: str, reason: str
                  ) -> tuple[FillCost, bool]:
        from sim.fill_model import passive_side_cost, side_cost

        if order.is_passive:
            return passive_side_cost(qty), False
        return side_cost(self.table, bar.open_ts_utc, qty, self.slippage_statistic), False

    def close_cost(self, run: _Run, root: str, bar: Bar, qty: int, side: str
                   ) -> tuple[FillCost, bool]:
        from sim.fill_model import side_cost

        return side_cost(self.table, bar.open_ts_utc, qty, self.slippage_statistic), False

    def admit_fill(self, run: _Run, order: _Order, bar: Bar) -> str:
        return "fill"

    def before_session_change(self, run: _Run) -> None:
        return None

    def passive_no_new(self, run: _Run, root: str, bar: Bar) -> bool:
        return bar.in_no_new_positions_window or xr.is_no_new_positions_window(
            bar.open_ts_utc, bar.early_halt_ct)

    def forced_reasons(self, run: _Run, root: str, bar: Bar) -> tuple[str, ...]:
        forced = xr.required_flatten(run.exposure(root), bar.decision_ts_utc, bar.early_halt_ct)
        return () if forced is None else ("forced_flatten",)

    def call_member(self, run: _Run, ts: int, bars: Mapping[str, Bar]) -> Sequence[Any]:
        bar = bars.get(self.ROOT)
        if bar is None:
            return ()
        return run.member.on_bar(run.visible(bar), self.view(run, bar))

    def view(self, run: _Run, bar: Bar) -> AccountView:
        pos = run.position[self.ROOT]
        q = pos.qty
        state = run.state
        return AccountView(
            phase=state.phase, status=state.status, trade_date=bar.trade_date,
            balance_cents=state.balance_cents, mll_floor_cents=state.mll_floor_cents,
            prior_session_balance_cents=state.session_start_balance_cents,
            max_position_micros=xr.max_position_micros(state.phase,
                                                       state.session_start_balance_cents),
            position_micros=q, pending_signed_micros=run.pending_signed(self.ROOT),
            avg_entry_price=None if q == 0 else pos.basis_ticks / q * xr.MES_TICK_SIZE,
            unrealized_at_close_cents=(q * xr.price_to_ticks(bar.close) - pos.basis_ticks)
            * self.tick_value(self.ROOT) if q else 0)

    def received_repr(self, item: Any, norm: _Normalized | None) -> str:
        return repr(item)

    def normalize(self, run: _Run, item: Any, ts: int, bars: Mapping[str, Bar]
                  ) -> tuple[_Normalized | None, Refusal | None]:
        """sim.engine._Run.structural_refusal's construction checks, in its order."""
        bar = bars[self.ROOT]
        if isinstance(item, PassiveIntent):
            if not isinstance(item.intent, OrderIntent):
                return None, Refusal("engine_not_an_intent",
                                     f"PassiveIntent wraps {type(item.intent).__name__}")
            norm, refusal = self.normalize(run, item.intent, ts, bars)
            if refusal is not None or norm is None:
                return norm, refusal
            structural = self.structural_refusal(run, norm, ts, bars)
            if structural is not None:
                return norm, structural
            passive = passive_refusal(bar, item)
            if passive is not None:
                return norm, Refusal("engine_malformed_passive",
                                     f"{passive.reason}: {passive.arithmetic}")
            return replace(norm, limit_price=float(item.limit_price),
                           ttl_bars=item.ttl_bars), None
        if isinstance(item, Refusal):
            return None, Refusal("strategy_construction_refusal",
                                 f"{item.reason}: {item.arithmetic}")
        if not isinstance(item, OrderIntent):
            return None, Refusal("engine_not_an_intent", f"strategy returned {type(item).__name__}")
        if item.symbol != xr.MES_SYMBOL or item.side not in xr.SIDES:
            return None, Refusal("engine_malformed_intent",
                                 f"symbol {item.symbol!r} / side {item.side!r} did not come "
                                 "through construct_intent")
        if (isinstance(item.quantity_micros, bool) or not isinstance(item.quantity_micros, int)
                or item.quantity_micros <= 0):
            return None, Refusal("engine_malformed_intent",
                                 f"quantity {item.quantity_micros!r} is not a positive integer")
        norm = _Normalized(self.ROOT, item.signed_quantity, item.ts_utc, None, None, item)
        return norm, None

    def structural_refusal(self, run: _Run, norm: _Normalized, ts: int,
                           bars: Mapping[str, Bar]) -> Refusal | None:
        bar = bars[self.ROOT]
        if norm.ts_utc != bar.decision_ts_utc:
            return Refusal("engine_intent_timestamp_mismatch",
                           f"intent ts {norm.ts_utc.isoformat()} != bar decision time "
                           f"{bar.decision_ts_utc.isoformat()}")
        if bar.in_scheduled_closure:
            return Refusal("engine_scheduled_closure", f"bar {bar.ts_event_ns} is in a closure")
        if bar.in_flatten_window or xr.is_flatten_window(bar.decision_ts_utc, bar.early_halt_ct):
            return Refusal("engine_flatten_window",
                           f"decision {bar.decision_ts_utc.isoformat()} is in the flatten window")
        exposure = run.exposure(self.ROOT)
        if bar.trade_date in self.roll_blackout and not xr.is_reducing(exposure, norm.signed_qty):
            return Refusal("engine_roll_blackout",
                           f"trade date {bar.trade_date} is a roll-blackout session")
        return None

    def gate(self, run: _Run, norm: _Normalized, ts: int, bars: Mapping[str, Bar]
             ) -> Refusal | None:
        assert norm.intent is not None
        bar = bars[self.ROOT]
        return xr.check_order(norm.intent, run.state, run.exposure(self.ROOT),
                              run.state.session_start_balance_cents, bar.early_halt_ct)


__all__ = ["MesRules"]
