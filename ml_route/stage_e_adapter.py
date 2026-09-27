"""A distilled route rule on the Stage E engine, one exposure per run (M5, M6 ML-A15, M7.7;
lead rulings OC-L item 1 and OC-P).

INTERFACE (for CanaryCoder and the E.ML-test entry; stable):

    plans = exposure_plans(rule_json, products)     # one ExposurePlan per exposure, primary first
    for plan in plans:
        member = build_exposure_member(rule_json, plan, products, costs, events, trade_dates,
                                       blackout)
        result = screening.stage_e_engine.run_engine(frames, member, plan.legs,
                                                     StageERules(...))
        member.decisions                             # [Decision(t_ns, complete, fired, acted)]

- ``rule_json``: a rule file's JSON (rules/<rule_sha256>.json); its hash is checked by
  ``ml_route.rule_wrapper.rule_spec_from_json`` (RuleIntegrityError on any change).
- ``products`` / ``costs``: ``ml_route.inputs.load_products()`` / ``load_vehicle_costs()``;
  ``events``: ``ml_route.inputs.load_event_calendar()`` (a price path reads its vehicle's list,
  the list the engine applies to the vehicle's fills).
- ``trade_dates[root]`` / ``blackout[root]``: for each price-path root the plan reads (its own
  and its F16 lead), every trade date with bars and the roll-blackout dates
  (``LegFrame.trade_dates`` / ``LegFrame.roll_blackout`` in a real run).
- ``frames``: one frame per leg of the plan, in the Stage E store schema.

ONE EXPOSURE PER RUN (lead ruling OC-P, from frozen M5 step 1 and ML-A10: "M4's one-open-position
rule applies in time order per product ... A product's daily P&L is the sum of its trades' P&L
on that date, and zero on a date with rows and no trade; the portfolio's daily P&L is the mean
over the products with rows on that date"). A route rule trades every traded exposure of its
cluster (ML-A15), each as its OWN engine run with ONE traded leg: the exposure's D2 vehicle at its
q_c, plus the signal legs that exposure's features read, namely its price-path contract (when the
vehicle is another contract, MNQ for NQ: the model learned on the price path, M1) and its cluster's
F16 lead price path (when the exposure is not the lead). So D11.5's missing-bar rule applies to
that run's own legs, no second traded leg exists to refuse, and exposures on different group
calendars (K6's grains and livestock) never meet in one run. The rule's daily series is combined
across the runs by ``ml_route.test`` (M5's mean over the exposures with rows on each date).

PER MINUTE (``on_minute``): the lead's price-path bar, when present, is handed to the wrapper
through ``observe_lead`` (the wrapper filters the lead history to bars closed by its decision time);
when the exposure's price-path bar is present, the wrapper's ``on_bar`` runs on it with the
vehicle's position and pending contracts, exactly as in training (one open position per
product, M4); each OrderIntent it returns becomes a LegIntent on the vehicle with the same side,
quantity and timestamp (a construction Refusal passes through). Everything else is the engine's:
fills at the vehicle's next bar open, D8 costs with the event-window rule, the D9.5a fill guard
(ml_route.rows applies the same deferral to the training targets, lead ruling OC-M), forced
flattens at F and the D9 constraint set.

TRADING WINDOWS (D9's member-level coverage): every leg is declared on its product's D6 day
session [O_X, C_X) from the frozen tables, the session M4's decision times run in.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from types import MappingProxyType
from typing import Any

from ml_route.constants import CLUSTER_OF, LEAD_OF_CLUSTER
from ml_route.inputs import DayTimes, EventCalendar, ProductSpec, VehicleCost, day_times
from ml_route.rule_wrapper import DistilledRuleStrategy, LeadSpec, RuleSpec, rule_spec_from_json
from rules.xfa_rules import OrderIntent, Refusal
from strategy.stage_e.interface import (
    LegIntent,
    LegSpec,
    MemberAccountView,
    MinuteView,
    TradingInterval,
)


class RouteMemberError(ValueError):
    """The rule cannot be run on the Stage E engine as frozen; the case is named."""


@dataclass(frozen=True)
class RouteExposure:
    """One traded exposure of a rule: the price-path contract and its D2 vehicle."""

    path_root: str
    vehicle: str
    q_c: int


@dataclass(frozen=True)
class ExposurePlan:
    """One engine run of a rule: one traded leg (the vehicle) and the price paths it reads."""

    exposure: RouteExposure
    lead_root: str
    legs: tuple[LegSpec, ...]  # the vehicle (traded) first, then the signal legs

    @property
    def path_root(self) -> str:
        return self.exposure.path_root

    @property
    def vehicle(self) -> str:
        return self.exposure.vehicle

    @property
    def paths_read(self) -> tuple[str, ...]:
        """The price-path roots whose bars the wrapper reads (its own, then the lead)."""
        return tuple(dict.fromkeys((self.exposure.path_root, self.lead_root)))


@dataclass(frozen=True)
class _LegAccount:
    """The wrapper's view of its own vehicle (it reads only these two fields)."""

    position_micros: int
    pending_signed_micros: int


def rule_exposures(rule: Mapping, products: Mapping[str, ProductSpec]) -> tuple[RouteExposure, ...]:
    """The rule's exposures, primary first, each mapped back to its price path."""
    cluster = rule["cluster"]
    lead_root = LEAD_OF_CLUSTER.get(cluster)
    if lead_root is None:
        raise RouteMemberError(f"cluster {cluster!r} has no F16 lead; no route rule can read it")
    vehicles = list(rule["exposures"])
    if len(set(vehicles)) != len(vehicles) or not vehicles:
        raise RouteMemberError(f"rule exposures {vehicles} are empty or repeat a vehicle")
    lead_vehicle = products[lead_root].vehicle
    if lead_vehicle is None or rule["primary_leg"] != lead_vehicle:
        raise RouteMemberError(
            f"primary leg {rule['primary_leg']!r} is not the vehicle {lead_vehicle!r} of the "
            f"{cluster} lead {lead_root} (ML-A15; its ADV fallback is not wired)")
    if lead_vehicle not in vehicles:
        raise RouteMemberError(f"the primary leg {lead_vehicle} is not among the exposures")
    out = []
    for v in [lead_vehicle] + [x for x in vehicles if x != lead_vehicle]:
        paths = [p for p, s in products.items() if s.vehicle == v and CLUSTER_OF[p] == cluster]
        if len(paths) != 1:
            raise RouteMemberError(f"vehicle {v} maps to price-path contracts {paths} in "
                                   f"{cluster}, not exactly one")
        spec = products[paths[0]]
        if spec.q_c is None or spec.q_c <= 0:
            raise RouteMemberError(f"{v}: no positive q_c in the frozen vehicle table")
        out.append(RouteExposure(paths[0], v, int(spec.q_c)))
    return tuple(out)


def exposure_plans(rule: Mapping, products: Mapping[str, ProductSpec]) -> tuple[ExposurePlan, ...]:
    """One plan per exposure (OC-P): the vehicle traded, its price path and lead as signals."""
    lead_root = LEAD_OF_CLUSTER[rule["cluster"]]
    plans = []
    for e in rule_exposures(rule, products):
        roots = list(dict.fromkeys((e.vehicle, e.path_root, lead_root)))
        legs = (LegSpec(e.vehicle, True),) + tuple(LegSpec(r, False) for r in roots[1:])
        plans.append(ExposurePlan(e, lead_root, legs))
    return tuple(plans)


def session_times(root: str, group: str, dates: Iterable[date]) -> dict[date, DayTimes]:
    """D6's O_X/C_X and D9.1's F_X for every trade date given (None days are left out)."""
    out = {}
    for d in sorted(set(dates)):
        dt = day_times(root, group, d)
        if dt is not None:
            out[d] = dt
    return out


def _day_session_windows(roots: Iterable[str]) -> dict[str, tuple[TradingInterval, ...]]:
    from screening.stage_e_frozen import load_frozen_tables

    table = load_frozen_tables().day_session_ct
    roots = list(roots)
    missing = [r for r in roots if r not in table]
    if missing:
        raise RouteMemberError(f"no frozen D6 day session for {missing}")
    return {r: (TradingInterval(*table[r]),) for r in roots}


class RouteExposureMember:
    """One exposure of one distilled rule as a Stage E member (see the module docstring)."""

    def __init__(self, spec: RuleSpec, plan: ExposurePlan, strategy: DistilledRuleStrategy,
                 trading_windows: Mapping[str, tuple[TradingInterval, ...]]) -> None:
        self.spec = spec
        self.plan = plan
        self.name = f"route_rule_{spec.rule_sha256[:12]}_{plan.path_root}"
        self.legs = plan.legs
        self.trading_windows = MappingProxyType(dict(trading_windows))
        self.strategy = strategy
        self._follows_lead = strategy.lead is not None

    @property
    def decisions(self) -> list:
        return self.strategy.decisions

    def on_minute(self, view: MinuteView, account: MemberAccountView
                  ) -> Sequence[LegIntent | Refusal]:
        plan = self.plan
        if self._follows_lead:
            lead_bar = view.bars.get(plan.lead_root)
            if lead_bar is not None:
                self.strategy.observe_lead(lead_bar)
        bar = view.bars.get(plan.path_root)
        if bar is None:  # no price-path bar: no decision and no history (never forward fill)
            return ()
        leg_account = _LegAccount(account.position(plan.vehicle),
                                  int(account.pending.get(plan.vehicle, 0)))
        return tuple(_as_leg_intent(item, plan.vehicle)
                     for item in self.strategy.on_bar(bar, leg_account))


def _as_leg_intent(item: Any, vehicle: str) -> LegIntent | Refusal:
    if isinstance(item, Refusal):
        return item
    if not isinstance(item, OrderIntent):
        raise RouteMemberError(f"the wrapper returned {type(item).__name__}, not an OrderIntent")
    return LegIntent(vehicle, item.side, int(item.quantity_micros), item.ts_utc)


def build_exposure_member(rule: Mapping, plan: ExposurePlan,
                          products: Mapping[str, ProductSpec],
                          costs: Mapping[str, VehicleCost], events: EventCalendar,
                          trade_dates: Mapping[str, Iterable[date]],
                          blackout: Mapping[str, Iterable[date]]) -> RouteExposureMember:
    """The member for one exposure of one rule (hash-checked); see the module docstring."""
    spec = rule_spec_from_json(rule)
    if plan not in exposure_plans(rule, products):
        raise RouteMemberError(f"the plan for {plan.path_root} is not one of the rule's")
    missing = sorted(r for r in plan.paths_read if r not in trade_dates)
    if missing:
        raise RouteMemberError(f"no trade dates given for the price-path legs {missing}")
    times = {r: session_times(r, products[r].group, trade_dates[r]) for r in plan.paths_read}
    lead = None
    if plan.path_root != plan.lead_root:
        lead_spec = products[plan.lead_root]
        lead = LeadSpec(plan.lead_root, float(lead_spec.vehicle_ticks_per_vendor_unit),
                        lead_spec, times[plan.lead_root])
    strategy = DistilledRuleStrategy(
        spec, products[plan.path_root], costs[plan.vehicle], times[plan.path_root],
        frozenset(blackout.get(plan.path_root, ())), events.of(plan.path_root), events.cpi,
        lead=lead, quantity_micros=plan.exposure.q_c)
    return RouteExposureMember(spec, plan, strategy,
                               _day_session_windows(leg.root for leg in plan.legs))


__all__ = ["ExposurePlan", "RouteExposure", "RouteExposureMember", "RouteMemberError",
           "build_exposure_member", "exposure_plans", "rule_exposures", "session_times"]
