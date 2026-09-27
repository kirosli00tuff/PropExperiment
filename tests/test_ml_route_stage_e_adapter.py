"""Stage E.2b G4 (MLTestCoder): a distilled route rule on the Stage E engine
(screening.stage_e_engine with StageERules) via ml_route.stage_e_adapter, one exposure per run
(lead ruling OC-P), on synthetic bars.

A K1 rule on two exposures: NQ -> MNQ (the primary; legs MNQ traded, NQ signal) and RTY -> M2K
(legs M2K traded, RTY and the NQ lead signal). Proves: each run has one traded leg and reads only
its own price path and lead; train/test parity of every exposure's complete and fired decisions
(F16 read from the NQ lead through observe_lead); entries fill at t + 1 minute on the vehicle;
exits fill at the training rows' exit time, including exits deferred by the D9.5a guard (lead
ruling OC-M); each trip's net dollars equal the training target in vehicle ticks x tick value x
q_c (the D8 cost surfaces agree); the exposures trade independently (positions overlap in time,
no second-leg refusal exists); and the adapter's refusals."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from fractions import Fraction
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import pytest

from ml_route.dataset import build_from_bars
from ml_route.inputs import RouteInputs, event_calendar_from_release, load_products
from ml_route.rule_wrapper import RuleIntegrityError
from ml_route.stage_e_adapter import (
    RouteMemberError,
    build_exposure_member,
    exposure_plans,
    rule_exposures,
)
from ml_route.surrogate import Leaf, condition_mask, rule_json
from ml_route.synthetic import bars_from_frame, synthetic_bars, synthetic_inputs
from screening.stage_e_engine import IntentRecord, run_engine
from screening.stage_e_frozen import leg_inputs
from screening.stage_e_rules import StageERules, release_calendar_from_dict
from screening.stage_e_runner import extract_trips
from strategy.stage_e.interface import LegSpec, StageEMember, TradingInterval

NS_MIN = 60_000_000_000
CT = ZoneInfo("America/Chicago")
FIRST, LAST = date(2019, 5, 6), date(2019, 12, 31)
CONDITIONS = (("F1_ret5", ">", 0.0), ("F16_lead_ret30", "<=", 5.0))
PATH = {"MNQ": "NQ", "M2K": "RTY"}
Q_C = {"MNQ": 1, "M2K": 3}


def k1_rule(exposures=("MNQ", "M2K"), primary="MNQ", cluster="K1", conditions=CONDITIONS,
            horizon="h30") -> dict:
    return rule_json(cluster, "lgbm", horizon, Leaf(0, 1, conditions, 0.1), 1, 0.05,
                     list(exposures), primary, {"model_sha256": "m" * 64}, {})


def _calendar(days: list[date]) -> object:
    """A release at 10:29 CT on every given date: the h30 exit at 10:30 is deferred to 10:31."""
    entries = []
    for i, d in enumerate(days):
        at = datetime.combine(d, time(10, 29), tzinfo=CT).astimezone(UTC)
        entries.append({"id": f"r{i}", "instant_utc": at.isoformat().replace("+00:00", "Z"),
                        "products": ["NQ", "MNQ", "RTY", "M2K"], "cpi": False, "source": "t"})
    raw = {"schema": "stage_e_release_calendar/1",
           "coverage": {"first": "2019-05-01", "last": "2020-01-31"}, "releases": entries}
    return release_calendar_from_dict(raw, "c" * 64, "synthetic calendar")


@pytest.fixture(scope="module")
def world() -> dict:
    nq = synthetic_bars("NQ", "equity", FIRST, LAST, 21, 0.25, 8000.0)
    rty = synthetic_bars("RTY", "equity", FIRST, LAST, 22, 0.1, 1500.0)
    frames = {"NQ": nq, "RTY": rty,
              "MNQ": nq.assign(raw_symbol="MNQZ9", instrument_id=np.uint32(2)),
              "M2K": rty.assign(raw_symbol="M2KZ9", instrument_id=np.uint32(3))}
    days = sorted(date.fromisoformat(d) for d in nq["trade_date"].unique())
    cal = _calendar(days[130:])
    products = load_products()
    events = event_calendar_from_release(cal, {r: products[r] for r in ("NQ", "RTY")})
    base = synthetic_inputs({"NQ": FIRST, "RTY": FIRST}, events)
    inputs = RouteInputs(base.products, base.costs, events, base.s_x)
    rule = k1_rule()
    plans = exposure_plans(rule, inputs.products)
    runs = {}
    for plan in plans:
        member = build_exposure_member(rule, plan, inputs.products, inputs.costs, events,
                                       {"NQ": days, "RTY": days}, {})
        rules = StageERules({leg.root: leg_inputs(leg.root, traded=leg.traded)
                             for leg in plan.legs}, frozenset(days), frozenset(), cal)
        result = run_engine({leg.root: frames[leg.root] for leg in plan.legs}, member, plan.legs,
                            rules)
        runs[plan.vehicle] = {"plan": plan, "member": member, "result": result,
                              "trips": list(extract_trips(result))}
    table = build_from_bars({"NQ": bars_from_frame("NQ", nq), "RTY": bars_from_frame("RTY", rty)},
                            inputs, last=LAST)
    return {"frames": frames, "days": days, "inputs": inputs, "rule": rule, "plans": plans,
            "runs": runs, "table": table}


def test_one_plan_per_exposure_with_one_traded_leg_and_only_its_own_reads(world) -> None:
    plans = world["plans"]
    assert [p.vehicle for p in plans] == ["MNQ", "M2K"]
    assert plans[0].legs == (LegSpec("MNQ", True), LegSpec("NQ", False))
    assert plans[1].legs == (LegSpec("M2K", True), LegSpec("RTY", False), LegSpec("NQ", False))
    assert plans[0].paths_read == ("NQ",) and plans[1].paths_read == ("RTY", "NQ")
    for run in world["runs"].values():
        member = run["member"]
        assert isinstance(member, StageEMember)
        assert set(member.trading_windows) == {leg.root for leg in run["plan"].legs}
        assert member.trading_windows["NQ"] == (TradingInterval(time(8, 30), time(15, 0)),)
    assert world["runs"]["M2K"]["member"].name.endswith("_RTY")


@pytest.mark.parametrize("vehicle", ["MNQ", "M2K"])
def test_every_exposures_decisions_equal_the_training_rows(world, vehicle: str) -> None:
    tb = world["table"]
    complete = np.isfinite(tb.X).all(axis=1) & (tb.product == PATH[vehicle])
    dec = world["runs"][vehicle]["member"].decisions
    assert {d.t_ns for d in dec if d.features_complete} == {int(t) for t in tb.t_ns[complete]}
    assert int(complete.sum()) > 100
    fired = condition_mask(np.nan_to_num(tb.X, nan=-1e9), CONDITIONS) & complete
    assert {d.t_ns for d in dec if d.fired} == {int(t) for t in tb.t_ns[fired]}
    assert all(d.trade_date is not None for d in dec)


@pytest.mark.parametrize("vehicle", ["MNQ", "M2K"])
def test_entries_at_t_plus_one_and_exits_at_the_training_exit_including_deferrals(
        world, vehicle: str) -> None:
    tb, run = world["table"], world["runs"][vehicle]
    trips = run["trips"]
    assert len(trips) > 10 and {t.root for t in trips} == {vehicle}
    deferred = 0
    for trip in trips:
        t = trip.open_ts_ns - NS_MIN  # the decision time: the entry fills at the open of t + 1
        row = np.flatnonzero((tb.product == PATH[vehicle]) & (tb.t_ns == t))
        assert row.size == 1, "every entry comes from a decision row"
        assert trip.close_ts_ns == int(tb.exit_ns["h30"][row[0]])
        assert trip.close_reason == "strategy"
        deferred += trip.close_ts_ns - trip.open_ts_ns == 30 * NS_MIN  # t + 31 - (t + 1)
    assert deferred >= 1  # 10:30 exits wait for 10:31 in the engine and in the training rows
    assert run["result"].counters.get("fill_guard_deferral", 0) == deferred


@pytest.mark.parametrize("vehicle", ["MNQ", "M2K"])
def test_each_trips_net_equals_the_training_target_in_dollars(world, vehicle: str) -> None:
    tb = world["table"]
    for trip in world["runs"][vehicle]["trips"]:
        r = int(np.flatnonzero((tb.product == PATH[vehicle])
                               & (tb.t_ns == trip.open_ts_ns - NS_MIN))[0])
        want = tb.y["h30"][r] * tb.sigma[r] * 50 * Q_C[vehicle]  # $0.50 a tick for both
        assert trip.contracts == Q_C[vehicle]
        got = float(Fraction(trip.net_cents))
        assert got == pytest.approx(want, abs=2.0), (trip, want)  # slippage is ceiled per side


def test_the_exposures_trade_independently(world) -> None:
    runs = world["runs"]
    for run in runs.values():
        assert "engine_second_leg_position" not in run["result"].counters
    spans = {v: [(t.open_ts_ns, t.close_ts_ns) for t in run["trips"]] for v, run in runs.items()}
    overlap = sum(1 for a0, a1 in spans["MNQ"] for b0, b1 in spans["M2K"] if a0 < b1 and b0 < a1)
    assert overlap > 0  # both exposures hold positions at once, as in M5's per-product P&L


@pytest.mark.parametrize("vehicle", ["MNQ", "M2K"])
def test_acted_decisions_are_the_intents_from_flat(world, vehicle: str) -> None:
    run = world["runs"][vehicle]
    acted = {d.t_ns + NS_MIN for d in run["member"].decisions if d.acted}
    entries = {e.decision_ts_ns for e in run["result"].events(IntentRecord)
               if e.root == vehicle and e.position_before == 0 and e.pending_before == 0}
    assert acted == entries
    refused = [e for e in run["result"].events(IntentRecord) if not e.accepted]
    assert not refused, refused[:3]


# ------------------------------------------------------------------ refusals ----
class TestAdapterRefusals:
    def test_a_primary_that_is_not_the_leads_vehicle_is_refused(self) -> None:
        with pytest.raises(RouteMemberError, match="ML-A15"):
            rule_exposures(k1_rule(primary="M2K"), load_products())

    def test_a_vehicle_outside_the_cluster_is_refused(self) -> None:
        with pytest.raises(RouteMemberError, match="maps to price-path contracts"):
            rule_exposures(k1_rule(exposures=("MNQ", "ZN")), load_products())

    def test_repeated_or_missing_primary_exposures_are_refused(self) -> None:
        with pytest.raises(RouteMemberError, match="repeat"):
            rule_exposures(k1_rule(exposures=("MNQ", "MNQ")), load_products())
        with pytest.raises(RouteMemberError, match="not among the exposures"):
            rule_exposures(k1_rule(exposures=("M2K",)), load_products())

    def test_a_cluster_without_a_lead_is_refused(self) -> None:
        with pytest.raises(RouteMemberError, match="no F16 lead"):
            rule_exposures(k1_rule(cluster="K8"), load_products())

    def test_a_changed_rule_is_refused_by_its_hash(self, world) -> None:
        rule = dict(world["rule"])
        rule["conditions"] = [{"feature": "F1_ret5", "op": ">", "cut": 0.5}]
        inputs = world["inputs"]
        with pytest.raises(RuleIntegrityError):
            build_exposure_member(rule, world["plans"][0], inputs.products, inputs.costs,
                                  inputs.events, {"NQ": world["days"]}, {})

    def test_missing_trade_dates_or_a_foreign_plan_are_refused(self, world) -> None:
        inputs = world["inputs"]
        with pytest.raises(RouteMemberError, match="NQ"):
            build_exposure_member(world["rule"], world["plans"][1], inputs.products,
                                  inputs.costs, inputs.events, {"RTY": world["days"]}, {})
        other = exposure_plans(k1_rule(exposures=("MNQ", "MYM")), inputs.products)[1]
        with pytest.raises(RouteMemberError, match="not one of the rule's"):
            build_exposure_member(world["rule"], other, inputs.products, inputs.costs,
                                  inputs.events, {"NQ": world["days"], "YM": world["days"]}, {})

    def test_a_construction_refusal_passes_through(self) -> None:
        from ml_route.stage_e_adapter import _as_leg_intent
        from rules.xfa_rules import Refusal

        ref = Refusal("intent_bad_quantity", "x")
        assert _as_leg_intent(ref, "MNQ") is ref
        with pytest.raises(RouteMemberError, match="not an OrderIntent"):
            _as_leg_intent(object(), "MNQ")


class TestPlansOfOtherClusters:
    def test_rates_read_their_own_path_and_the_zn_lead(self) -> None:
        rule = rule_json("K2", "lgbm", "h30", Leaf(0, 1, CONDITIONS, 0.1), 1, 0.05,
                         ["ZN", "ZF"], "ZN", {}, {})
        zn, zf = exposure_plans(rule, load_products())
        assert zn.legs == (LegSpec("ZN", True),) and zn.paths_read == ("ZN",)
        assert zf.legs == (LegSpec("ZF", True), LegSpec("ZN", False))

    def test_k6_grains_and_livestock_are_separate_runs(self) -> None:
        from rules.products import product

        rule = rule_json("K6", "lgbm", "h30", Leaf(0, 1, CONDITIONS, 0.1), 1, 0.05,
                         ["ZC", "HE", "LE"], "ZC", {}, {})
        plans = exposure_plans(rule, load_products())
        for plan in plans:
            traded = [leg.root for leg in plan.legs if leg.traded]
            assert traded == [plan.vehicle]
        assert {product(p.vehicle).group for p in plans} == {"grains", "livestock"}
        assert plans[1].legs == (LegSpec("HE", True), LegSpec("ZC", False))

    def test_energy_reads_the_micro_vehicle_path_and_lead(self) -> None:
        rule = rule_json("K4", "lgbm", "h30", Leaf(0, 1, CONDITIONS, 0.1), 1, 0.05,
                         ["MCL", "NG"], "MCL", {}, {})
        mcl, ng = exposure_plans(rule, load_products())
        assert mcl.legs == (LegSpec("MCL", True), LegSpec("CL", False))
        assert ng.legs == (LegSpec("NG", True), LegSpec("CL", False))


def test_the_frames_are_the_store_schema(world) -> None:
    from data.stage_e_bars import BAR_COLUMNS

    frame = world["frames"]["MNQ"]
    assert set(BAR_COLUMNS) <= set(frame.columns)
    assert isinstance(frame, pd.DataFrame)
