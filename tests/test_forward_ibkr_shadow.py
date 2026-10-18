"""Shadow order route (Stage E.24): the E22-F1 ledger is byte-identical with the route on and off;
path, paper-account and idempotency guards. Mock gateway, synthetic prices, no network."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest

from forward.ibkr_gateway import ConnectionParams, GatewaySession, RetryPolicy
from forward.orders_ibkr import (
    DEFAULT_SHADOW_CONFIG,
    PlannedOrder,
    ShadowConfig,
    ShadowRoute,
    ShadowRouteError,
    load_shadow_config,
    plan_orders,
)
from forward.runner import PaperRunner, RunnerConfig, load_tables
from forward.sources_ibkr import ContractResolver, IBKRSettlementSource
from tests._forward_ibkr_mock import (
    ENV,
    FAKE_VENDOR,
    PAPER,
    ROLLS,
    MockGateway,
    build_bars,
    build_listings,
    ct,
)

FIRST, LAST = date(2026, 11, 2), date(2026, 12, 31)
DAYS = [date(2026, 12, d) for d in (7, 8, 9, 10, 11, 14)]  # MNQ/M2K/M6E roll on 12-10
PLAN = {
    date(2026, 12, 7): {"MNQ": 2, "MCL": -1},
    date(2026, 12, 9): {"MNQ": 3, "MCL": -1, "MZC": 1},
    date(2026, 12, 11): {"MNQ": 1, "MZC": 0},
}
TICKS = {
    k: float(v["tick"])
    for k, v in json.loads(Path("forward/config_f1.json").read_text())["instruments"].items()
}


def target(history, prev, config):
    day = history[-1].date
    plan = {}
    for d in sorted(PLAN):
        if d <= day:
            plan = PLAN[d]
    return {i: plan.get(i, 0) for i in prev if history[-1].price(i) is not None}


def build(tmp_path, name, env=ENV, accounts=(PAPER,)):
    listings = build_listings(FIRST, LAST)
    gw = MockGateway(
        listings, build_bars(listings, FIRST, LAST), now=ct(2026, 12, 15, 19), accounts=accounts
    )
    session = GatewaySession(
        gw,
        ConnectionParams.from_env(env, need_account=True),
        readonly=False,
        policy=RetryPolicy(backoff_base_s=0),
        sleep=lambda s: None,
    )
    multipliers, costs = load_tables("forward/tables_f1.json")
    resolver = ContractResolver(session, FAKE_VENDOR, ROLLS, config_multipliers=multipliers)
    src = IBKRSettlementSource(session, resolver, ROLLS, now=lambda: gw.now)
    ledger = tmp_path / f"{name}_e22.jsonl"
    runner = PaperRunner(ledger, src, RunnerConfig(multipliers, costs, ROLLS, {}), target_fn=target)
    return gw, session, resolver, runner, ledger


def route(tmp_path, session, resolver, ledger, **kw):
    cfg = ShadowConfig(
        enabled=True, shadow_ledger=str(tmp_path / "shadow.jsonl"), fill_wait_s=0, **kw
    )
    return ShadowRoute(
        cfg, session, resolver, FAKE_VENDOR, e22_ledger_path=ledger, ticks=TICKS, clock=lambda: 0.0
    )


def test_e22_ledger_is_byte_identical_with_the_shadow_route_on_and_off(tmp_path):
    _, _, _, runner_off, ledger_off = build(tmp_path, "off")
    for d in DAYS:
        runner_off.run_date(d)
    gw, session, resolver, runner_on, ledger_on = build(tmp_path, "on")
    shadow = route(tmp_path, session, resolver, ledger_on)
    for d in DAYS:
        runner_on.run_date(d)
        before = ledger_on.read_bytes()
        shadow.run(d)
        assert ledger_on.read_bytes() == before  # the route never writes the E22-F1 ledger
    a, b = ledger_off.read_bytes(), ledger_on.read_bytes()
    assert a == b and hashlib.sha256(a).hexdigest() == hashlib.sha256(b).hexdigest()
    recs = shadow.shadow.records()
    assert [r["date"] for r in recs] == [d.isoformat() for d in DAYS]
    assert all(
        r["schema"] == "E22-F1-shadow/1" and r["account_env"] == "IBKR_ACCOUNT_ID" for r in recs
    )
    assert sum(len(r["orders"]) for r in recs) >= 5 and all(
        r["fills"] or not r["orders"] for r in recs
    )
    assert PAPER not in (tmp_path / "shadow.jsonl").read_text()
    # after the MNQ roll on 12-10 the shadow book closes Z26 and opens H27
    roll_day = next(r for r in recs if r["date"] == "2026-12-10")
    legs = {(o["contract_id"], o["action"]) for o in roll_day["orders"] if o["instrument"] == "MNQ"}
    assert ("MNQZ26", "SELL") in legs and ("MNQH27", "BUY") in legs
    n = gw.count("placeOrder")
    shadow.run(DAYS[-1])  # a re-run of a recorded date places nothing
    assert gw.count("placeOrder") == n


def test_the_shadow_ledger_can_never_be_the_e22_ledger(tmp_path):
    _, session, resolver, runner, ledger = build(tmp_path, "x")
    runner.run_date(DAYS[0])
    for path in (ledger, tmp_path / "link.jsonl", tmp_path / "hard.jsonl"):
        if path.name == "link.jsonl":
            os.symlink(ledger, path)
        if path.name == "hard.jsonl":
            os.link(ledger, path)
        cfg = ShadowConfig(enabled=True, shadow_ledger=str(path))
        with pytest.raises(ShadowRouteError, match="E22-F1 ledger"):
            ShadowRoute(cfg, session, resolver, FAKE_VENDOR, e22_ledger_path=ledger, ticks=TICKS)


def test_default_config_is_off_and_a_disabled_route_refuses(tmp_path):
    cfg = load_shadow_config(DEFAULT_SHADOW_CONFIG)
    assert cfg.enabled is False
    _, session, resolver, _, ledger = build(tmp_path, "x")
    with pytest.raises(ShadowRouteError, match="disabled"):
        ShadowRoute(cfg, session, resolver, FAKE_VENDOR, e22_ledger_path=ledger, ticks=TICKS)


@pytest.mark.parametrize(
    "env_over,accounts,match",
    [
        ({"IBKR_ACCOUNT_ID": "U1234567"}, ("U1234567",), "not a paper account"),
        ({"IBKR_GATEWAY_PORT": "4001"}, (PAPER,), "LIVE port"),
        ({}, ("DU0000001",), "managed accounts"),
    ],
)
def test_paper_guards_refuse_without_showing_values(tmp_path, env_over, accounts, match):
    gw, session, resolver, runner, ledger = build(
        tmp_path, "x", env={**ENV, **env_over}, accounts=accounts
    )
    runner.run_date(DAYS[0])
    with pytest.raises(ShadowRouteError, match=match) as info:
        route(tmp_path, session, resolver, ledger).run(DAYS[0])
    assert "U1234567" not in str(info.value) and PAPER not in str(info.value)
    assert gw.count("placeOrder") == 0


def test_open_shadow_orders_block_and_late_fills_are_recorded_next_day(tmp_path):
    gw, session, resolver, runner, ledger = build(tmp_path, "x")
    gw.fill_mode = "none"
    shadow = route(tmp_path, session, resolver, ledger)
    runner.run_date(DAYS[0])
    runner.run_date(DAYS[1])
    first = shadow.run(DAYS[1])
    assert first["orders"] and not first["fills"]
    runner.run_date(DAYS[2])
    with pytest.raises(ShadowRouteError, match="open shadow orders"):
        shadow.run(DAYS[2])
    gw.fill_open_orders()
    gw.fill_mode = "immediate"
    second = shadow.run(DAYS[2])
    assert {f["exec_id"] for f in second["late_fills"]} == {
        f.execution.execId for f in gw.executions[: len(first["orders"])]
    }


def test_limit_orders_price_off_the_settlement_in_ib_units(tmp_path):
    gw, session, resolver, runner, ledger = build(tmp_path, "x")
    runner.run_date(DAYS[0])
    runner.run_date(DAYS[1])
    route(tmp_path, session, resolver, ledger, order_type="LMT", limit_offset_ticks=2).run(DAYS[1])
    orders = {o["conId"]: o["order"] for name, o in gw.calls if name == "placeOrder"}
    assert orders and all(o.orderType == "LMT" for o in orders.values())
    mnq = next(o for o in orders.values() if o.action == "BUY" and o.totalQuantity == 2)
    settle = json.loads(ledger.read_text().splitlines()[1])["prices"]["MNQ"]["MNQZ26"]
    assert mnq.lmtPrice == settle + 2 * 0.25


def test_plan_closes_legs_outside_the_target_first():
    plan = plan_orders(
        {"MNQ": ("MNQH27", 2), "MCL": ("MCLF27", 0)},
        {"MNQ": {"MNQZ26": 2}, "MCL": {"MCLF27": -1}, "MZC": {"MZCH27": 1}},
    )
    assert plan == [
        PlannedOrder("MCL", "MCLF27", 1),
        PlannedOrder("MNQ", "MNQZ26", -2),
        PlannedOrder("MNQ", "MNQH27", 2),
        PlannedOrder("MZC", "MZCH27", -1),
    ]
    assert replace(plan[0], delta=1) == plan[0]


# --- wave 3 (IBKRFixer): S5 late fills past the executions' retention, N4 guard order ---------
def _late_setup(tmp_path):
    gw, session, resolver, runner, ledger = build(tmp_path, "x")
    gw.fill_mode = "none"
    shadow = route(tmp_path, session, resolver, ledger)
    runner.run_date(DAYS[0])
    runner.run_date(DAYS[1])
    gw.now = ct(2026, 12, 8, 18, 5)
    first = shadow.run(DAYS[1])  # placed at 18:05 CT; nothing fills within the wait
    assert first["orders"] and not first["fills"]
    gw.now = ct(2026, 12, 8, 19, 0)  # e.g. the grains open at 19:00 CT: fills after the record
    gw.fill_open_orders()
    gw.fill_mode = "immediate"
    gw.now = ct(2026, 12, 9, 18, 5)  # the next run: IB returns the current day's executions
    assert gw.reqExecutions() == []
    runner.run_date(DAYS[2])
    return gw, runner, shadow, first


def test_a_late_fill_past_the_executions_retention_is_recovered_from_completed_orders(tmp_path):
    gw, runner, shadow, first = _late_setup(tmp_path)
    second = shadow.run(DAYS[2])
    assert second["late_fills"] == [] and second["unresolved_orders"] == []
    got = {(x["instrument"], x["contract_id"]): x for x in second["late_fills_unretained"]}
    want = {(o["instrument"], o["contract_id"]): o for o in first["orders"]}
    assert set(got) == set(want)
    for key, x in got.items():
        assert x["shares"] == want[key]["qty"] and x["source"] == "completed_order"
        assert x["order_ref"] == "E22F1-shadow:2026-12-08" and x["perm_id"] > 0
    gw.now = ct(2026, 12, 10, 18, 5)
    runner.run_date(DAYS[3])
    third = shadow.run(DAYS[3])  # accounted once: never listed again
    assert third["late_fills_unretained"] == [] and third["unresolved_orders"] == []


def test_an_unfilled_order_that_left_no_trace_is_listed_once_as_unresolved(tmp_path):
    gw, runner, shadow, first = _late_setup(tmp_path)
    gw.completed_visible = False  # neither executions nor completed orders still show it
    second = shadow.run(DAYS[2])
    assert second["late_fills_unretained"] == []
    assert {(x["instrument"], x["contract_id"]) for x in second["unresolved_orders"]} == {
        (o["instrument"], o["contract_id"]) for o in first["orders"]
    }
    assert all(x["accounted_shares"] == 0 for x in second["unresolved_orders"])
    gw.now = ct(2026, 12, 10, 18, 5)
    runner.run_date(DAYS[3])
    assert shadow.run(DAYS[3])["unresolved_orders"] == []


def test_late_fills_within_the_retention_carry_their_order_ref(tmp_path):
    gw, session, resolver, runner, ledger = build(tmp_path, "x")
    gw.fill_mode = "none"
    shadow = route(tmp_path, session, resolver, ledger)
    runner.run_date(DAYS[0])
    first = shadow.run(DAYS[0])
    gw.fill_open_orders()
    gw.fill_mode = "immediate"
    runner.run_date(DAYS[1])
    second = shadow.run(DAYS[1])
    assert {f["order_ref"] for f in second["late_fills"]} == {"E22F1-shadow:2026-12-07"}
    assert len(second["late_fills"]) == len(first["orders"])
    assert second["late_fills_unretained"] == [] and second["unresolved_orders"] == []


def test_port_and_account_prefix_are_checked_before_connecting(tmp_path):
    gw, session, resolver, runner, ledger = build(
        tmp_path, "x", env={**ENV, "IBKR_GATEWAY_PORT": "4001"}
    )
    runner.run_date(DAYS[0])
    session.close()
    n = gw.count("connect")
    with pytest.raises(ShadowRouteError, match="LIVE port"):
        route(tmp_path, session, resolver, ledger).run(DAYS[0])
    assert gw.count("connect") == n and not gw.connected
