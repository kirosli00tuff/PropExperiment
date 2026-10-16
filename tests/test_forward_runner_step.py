"""forward.runner (E.22, ForwardRunnerCoder): fills, costs, rolls, missing data, ordering,
idempotent re-runs and restarts. Synthetic instruments and prices only; a stub target function."""

from __future__ import annotations

import sys
import types
from datetime import date

import numpy as np
import pytest

from forward import rolls as R
from forward.history import back_adjusted_series, instrument_frame, reference_series
from forward.runner import LedgerConflictError, PaperRunner, RunnerConfig, RunnerError
from forward.sources import InMemorySettlementSource, Missing

ROLLS = R.parse_rolls(
    {
        "status": R.CHECK_FLAG,
        "instruments": {
            "AAA": {
                "root": "AAA",
                "cycle": "HMUZ",
                "cycle_source": "test",
                "anchor": {"kind": "nth_weekday", "weekday": 4, "nth": 3, "month_offset": 0},
                "n_bdays": 6,
            },  # Z26 rolls 2026-12-10, anchor 2026-12-18
            "BBB": {
                "root": "BBB",
                "cycle": "FGHJKMNQUVXZ",
                "cycle_source": "test",
                "anchor": {"kind": "calendar_day", "day": 25, "month_offset": -1},
                "n_bdays": 10,
            },  # F27 rolls 2026-12-11
        },
    }
)
MULT = {"AAA": 2.0, "BBB": 100.0}
CPS = {"AAA": 1.25, "BBB": 2.5}
CONFIG = RunnerConfig(MULT, CPS, ROLLS, {"name": "stub"})
D = {k: date(2026, 11, k) for k in range(2, 7)}  # Mon 2 .. Fri 6 November 2026


class Script:
    """Stub target: keep positions unless the plan sets a target for the decision date."""

    def __init__(self, plan=None):
        self.plan = plan or {}
        self.calls = []

    def __call__(self, history, prev, config):
        assert config == {"name": "stub"}
        self.calls.append(
            {
                "date": history[-1].date,
                "dates": [r.date for r in history],
                "prev": dict(prev),
                "history": history,
            }
        )
        return {**prev, **self.plan.get(history[-1].date, {})}


def nov(aaa=None, bbb=None):
    day = {}
    if aaa is not None:
        day["AAA"] = {"AAAZ26": aaa}
    if bbb is not None:
        day["BBB"] = {"BBBZ26": bbb}
    return day


def make(tmp_path, data, plan=None, name="l.jsonl", config=CONFIG):
    script = Script(plan)
    runner = PaperRunner(tmp_path / name, InMemorySettlementSource(data), config, target_fn=script)
    return runner, script


def run_all(runner, days):
    return [runner.run_date(d) for d in days]


def test_order_made_at_t_fills_at_next_settlement_never_at_t(tmp_path):
    data = {D[2]: nov(100.0, 50.0), D[3]: nov(101.0, 50.5), D[4]: nov(103.0, 50.5)}
    runner, _ = make(tmp_path, data, {D[2]: {"AAA": 2}})
    r2, r3, r4 = run_all(runner, [D[2], D[3], D[4]])
    assert r2["fills"] == [] and r2["orders"] == {"AAA": 2} and r2["net_pnl"] == 0.0
    assert r3["fills"] == [
        {"instrument": "AAA", "contract": "AAAZ26", "qty": 2, "price": 101.0, "cost": 2.5}
    ]
    assert r3["gross_pnl"] == 0.0 and r3["net_pnl"] == -2.5
    assert r3["positions"]["AAA"] == {
        "contract": "AAAZ26",
        "qty": 2,
        "mark": 101.0,
        "mark_date": "2026-11-03",
    }
    assert r4["gross_pnl"] == 2 * (103.0 - 101.0) * 2.0 and r4["net_pnl"] == 8.0
    assert r4["fills"] == [] and r4["orders"] == {}


def test_target_function_sees_history_through_t_only_and_post_fill_positions(tmp_path):
    data = {D[2]: nov(100.0, 50.0), D[3]: nov(101.0, 50.5), D[4]: nov(103.0, 50.5)}
    runner, script = make(tmp_path, data, {D[2]: {"AAA": 2}})
    run_all(runner, [D[2], D[3], D[4]])
    for call in script.calls:
        assert call["dates"][-1] == call["date"] and max(call["dates"]) == call["date"]
    assert [c["prev"] for c in script.calls] == [
        {"AAA": 0, "BBB": 0},
        {"AAA": 2, "BBB": 0},
        {"AAA": 2, "BBB": 0},
    ]
    with pytest.raises(TypeError):
        script.calls[-1]["history"][-1].prices["AAA"]["AAAZ26"] = 0.0


def test_cost_arithmetic_on_flips_and_two_instruments(tmp_path):
    data = {
        D[2]: nov(100.0, 50.0),
        D[3]: nov(100.0, 50.0),
        D[4]: nov(100.0, 51.0),
        D[5]: nov(100.0, 51.0),
    }
    plan = {D[2]: {"AAA": 2, "BBB": 1}, D[4]: {"AAA": -1, "BBB": -2}}
    runner, _ = make(tmp_path, data, plan)
    r = run_all(runner, [D[2], D[3], D[4], D[5]])
    assert r[1]["costs"] == {"fills": 2 * 1.25 + 1 * 2.5, "rolls": 0.0, "total": 5.0}
    assert r[2]["gross_pnl"] == 1 * (51.0 - 50.0) * 100.0  # BBB long 1 marked up
    assert r[3]["costs"]["fills"] == 3 * 1.25 + 3 * 2.5  # AAA 2 -> -1, BBB 1 -> -2
    assert r[3]["net_pnl"] == r[3]["gross_pnl"] - r[3]["costs"]["total"]
    for rec in r:
        assert rec["net_pnl"] == rec["gross_pnl"] - rec["costs"]["total"]
        for inst, v in rec["pnl_by_instrument"].items():
            assert v["cost"] == sum(f["cost"] for f in rec["fills"] if f["instrument"] == inst)


def dec(day, aaa=None, bbb=None):
    return date(2026, 12, day), {k: v for k, v in (("AAA", aaa), ("BBB", bbb)) if v}


def test_roll_fills_two_legs_with_costs_and_switches_the_mark(tmp_path):
    days = [
        dec(8, {"AAAZ26": 108.0}, {"BBBF27": 60.0}),
        dec(9, {"AAAZ26": 109.0}, {"BBBF27": 60.0}),
        dec(10, {"AAAZ26": 110.0, "AAAH27": 111.0}, {"BBBF27": 60.0}),
        dec(11, {"AAAH27": 112.0}, {"BBBF27": 60.0, "BBBG27": 61.0}),
    ]
    runner, script = make(tmp_path, dict(days), {date(2026, 12, 8): {"AAA": 2}})
    r8, r9, r10, r11 = run_all(runner, [d for d, _ in days])
    assert r9["fills"][0]["price"] == 109.0 and r9["rolls"] == []
    assert r10["rolls"] == [
        {
            "instrument": "AAA",
            "from_contract": "AAAZ26",
            "to_contract": "AAAH27",
            "qty": 2,
            "close_price": 110.0,
            "open_price": 111.0,
            "cost": 5.0,
        }
    ]
    assert r10["gross_pnl"] == 2 * (110.0 - 109.0) * 2.0 and r10["net_pnl"] == 4.0 - 5.0
    assert (
        r10["positions"]["AAA"]["contract"] == "AAAH27" and r10["positions"]["AAA"]["mark"] == 111.0
    )
    assert r11["gross_pnl"] == 2 * (112.0 - 111.0) * 2.0
    # flat BBB: the reference switches on its roll date without fills or costs
    assert r11["rolls"] == [
        {
            "instrument": "BBB",
            "from_contract": "BBBF27",
            "to_contract": "BBBG27",
            "qty": 0,
            "close_price": 60.0,
            "open_price": 61.0,
            "cost": 0.0,
        }
    ]
    history = script.calls[-1]["history"]
    assert [c for _, c, _ in reference_series(history, "AAA")] == [
        "AAAZ26",
        "AAAZ26",
        "AAAH27",
        "AAAH27",
    ]
    assert back_adjusted_series(history, "AAA") == [
        (date(2026, 12, 8), 109.0),
        (date(2026, 12, 9), 110.0),
        (date(2026, 12, 10), 111.0),
        (date(2026, 12, 11), 112.0),
    ]


def test_instrument_frame_gives_price_and_adjusted_columns(tmp_path):
    days = [
        dec(9, {"AAAZ26": 109.0}, {"BBBF27": 60.0}),
        dec(10, {"AAAZ26": 110.0, "AAAH27": 111.0}, {"BBBF27": 60.0}),
        dec(11, {"AAAH27": 112.0}, {"BBBF27": 60.0, "BBBG27": 61.0}),
    ]
    runner, script = make(tmp_path, dict(days), {date(2026, 12, 9): {"AAA": 1}})
    run_all(runner, [d for d, _ in days])
    frame = instrument_frame(script.calls[-1]["history"], "AAA")
    assert list(frame["contract"]) == ["AAAZ26", "AAAH27", "AAAH27"]
    assert list(frame["price"]) == [109.0, 111.0, 112.0]
    assert list(frame["adjusted"]) == [110.0, 111.0, 112.0]
    assert str(frame.index[0].date()) == "2026-12-09"


def test_roll_deferred_without_the_new_contract_then_overdue(tmp_path):
    z = {k: {"AAAZ26": 100.0 + k} for k in (8, 9, 10, 11, 14, 15, 16, 17, 18)}
    data = {
        date(2026, 12, k): {"AAA": q, "BBB": {"BBBF27": 60.0, "BBBG27": 61.0}} for k, q in z.items()
    }
    data[date(2026, 12, 21)] = {"AAA": {"AAAZ26": 120.0, "AAAH27": 121.0}, "BBB": {"BBBG27": 61.0}}
    runner, _ = make(tmp_path, data, {date(2026, 12, 8): {"AAA": 1}})
    recs = run_all(runner, sorted(data))
    by = {r["date"]: r for r in recs}
    assert "roll_deferred:AAA" in by["2026-12-10"]["flags"]
    assert "roll_overdue:AAA" not in by["2026-12-17"]["flags"]
    assert "roll_overdue:AAA" in by["2026-12-18"]["flags"]
    assert by["2026-12-18"]["positions"]["AAA"]["contract"] == "AAAZ26"
    assert by["2026-12-21"]["rolls"][0]["to_contract"] == "AAAH27"
    assert by["2026-12-21"]["rolls"][0]["cost"] == 2 * 1 * 1.25


def test_missing_instrument_carries_position_at_last_mark_and_expires_its_order(tmp_path):
    data = {
        D[2]: nov(100.0, 50.0),
        D[3]: nov(101.0, 50.0),
        D[4]: nov(None, 50.0),
        D[5]: nov(104.0, 50.0),
    }
    plan = {D[2]: {"AAA": 2}, D[3]: {"AAA": 3}, D[4]: {"AAA": 5}}
    runner, script = make(tmp_path, data, plan)
    r = run_all(runner, [D[2], D[3], D[4], D[5]])
    r4 = r[2]
    assert {"missing:AAA", "order_expired:AAA"} <= set(r4["flags"])
    assert r4["fills"] == [] and r4["expired_orders"] == {"AAA": 3}
    assert "AAA" not in r4["orders"]  # no new order for a missing instrument
    assert r4["positions"]["AAA"] == {
        "contract": "AAAZ26",
        "qty": 2,
        "mark": 101.0,
        "mark_date": "2026-11-03",
    }
    assert r4["pnl_by_instrument"]["AAA"]["gross"] == 0.0
    assert D[4] in [c["date"] for c in script.calls]  # BBB had data, so the strategy ran
    assert r[3]["gross_pnl"] == 2 * (104.0 - 101.0) * 2.0 and r[3]["fills"] == []


def test_missing_whole_day_is_a_no_trade_day(tmp_path):
    data = {D[2]: nov(100.0, 50.0), D[3]: Missing("vendor outage"), D[4]: nov(103.0, 50.0)}
    runner, script = make(tmp_path, data, {D[2]: {"AAA": 2}})
    r2, r3, r4 = run_all(runner, [D[2], D[3], D[4]])
    assert r3["missing_day"] and set(r3["flags"]) == {"missing_day", "order_expired:AAA"}
    assert r3["fills"] == [] and r3["orders"] == {} and r3["net_pnl"] == 0.0
    assert r3["expired_orders"] == {"AAA": 2}
    assert [c["date"] for c in script.calls] == [D[2], D[4]]
    assert r4["fills"] == [] and r4["positions"]["AAA"]["qty"] == 0
    assert D[3] in script.calls[-1]["dates"]


def test_rerun_of_a_recorded_date_is_a_no_op(tmp_path):
    data = {D[2]: nov(100.0, 50.0), D[3]: nov(101.0, 50.5), D[4]: nov(103.0, 50.5)}
    runner, _ = make(tmp_path, data, {D[2]: {"AAA": 2}})
    recs = run_all(runner, [D[2], D[3], D[4]])
    before = runner.ledger.path.read_bytes()
    assert runner.run_date(D[3]) == recs[1]
    assert runner.run_date(D[2]) == recs[0]
    assert runner.ledger.path.read_bytes() == before


def test_rerun_with_changed_data_conflicts_and_writes_nothing(tmp_path):
    data = {D[2]: nov(100.0, 50.0), D[3]: nov(101.0, 50.5)}
    runner, _ = make(tmp_path, data, {D[2]: {"AAA": 2}})
    run_all(runner, [D[2], D[3]])
    before = runner.ledger.path.read_bytes()
    changed, _ = make(tmp_path, {**data, D[3]: nov(101.25, 50.5)}, {D[2]: {"AAA": 2}})
    with pytest.raises(LedgerConflictError, match="prices"):
        changed.run_date(D[3])
    assert runner.ledger.path.read_bytes() == before


def test_restart_rebuilds_state_from_the_ledger(tmp_path):
    data = {D[k]: nov(100.0 + k, 50.0 - k) for k in range(2, 7)}
    plan = {D[2]: {"AAA": 2}, D[3]: {"BBB": -1}, D[4]: {"AAA": -1}}
    straight, _ = make(tmp_path, data, plan, "a.jsonl")
    run_all(straight, sorted(data))
    first, _ = make(tmp_path, data, plan, "b.jsonl")
    run_all(first, [D[2], D[3]])
    second, _ = make(tmp_path, data, plan, "b.jsonl")  # a fresh process
    run_all(second, [D[4], D[5], D[6]])
    assert (tmp_path / "a.jsonl").read_bytes() == (tmp_path / "b.jsonl").read_bytes()


def test_dates_must_come_in_order_without_undeclared_gaps(tmp_path):
    data = {D[k]: nov(100.0, 50.0) for k in range(2, 7)}
    runner, _ = make(tmp_path, data)
    run_all(runner, [D[3], D[4]])
    with pytest.raises(RunnerError, match="out-of-order|before the last"):
        runner.run_date(D[2])
    with pytest.raises(RunnerError, match="weekend"):
        runner.run_date(date(2026, 11, 7))
    with pytest.raises(RunnerError, match="2026-11-05"):
        runner.run_date(D[6])
    with pytest.raises(RunnerError, match="weekdays strictly inside"):
        runner.run_date(D[6], declared_closed=[date(2026, 11, 8)])
    rec = runner.run_date(D[6], declared_closed=[D[5]])
    assert rec["declared_closed"] == ["2026-11-05"]
    assert runner.run_date(D[6]) == rec  # re-run reuses the stored declaration


@pytest.mark.parametrize(
    "bad", [{"AAA": 1.5}, {"AAA": True}, {"AAA": "2"}, {"CCC": 1}, "not a mapping"]
)
def test_non_integer_or_unknown_targets_are_refused_and_nothing_is_written(tmp_path, bad):
    def target(history, prev, config):
        return {**prev, **bad} if isinstance(bad, dict) else bad

    runner = PaperRunner(
        tmp_path / "l.jsonl",
        InMemorySettlementSource({D[2]: nov(1.0, 1.0)}),
        CONFIG,
        target_fn=target,
    )
    with pytest.raises(RunnerError):
        runner.run_date(D[2])
    assert not (tmp_path / "l.jsonl").exists() or runner.ledger.records() == []


def test_omitting_an_instrument_with_data_is_refused(tmp_path):
    runner = PaperRunner(
        tmp_path / "l.jsonl",
        InMemorySettlementSource({D[2]: nov(1.0, 1.0)}),
        CONFIG,
        target_fn=lambda h, p, c: {"AAA": 0},
    )
    with pytest.raises(RunnerError, match="omitted"):
        runner.run_date(D[2])


def test_numpy_integers_are_accepted(tmp_path):
    runner = PaperRunner(
        tmp_path / "l.jsonl",
        InMemorySettlementSource({D[2]: nov(1.0, 1.0)}),
        CONFIG,
        target_fn=lambda h, p, c: {"AAA": np.int64(3), "BBB": np.int32(0)},
    )
    assert runner.run_date(D[2])["orders"] == {"AAA": 3}


def test_unknown_instrument_in_settlements_is_refused(tmp_path):
    src = InMemorySettlementSource({D[2]: {**nov(1.0, 1.0), "CCC": {"CCCZ26": 1.0}}})
    runner = PaperRunner(tmp_path / "l.jsonl", src, CONFIG, target_fn=Script())
    with pytest.raises(RunnerError, match="outside the universe"):
        runner.run_date(D[2])


def test_restart_under_another_configuration_is_refused(tmp_path):
    data = {D[2]: nov(1.0, 1.0), D[3]: nov(1.0, 1.0)}
    runner, _ = make(tmp_path, data)
    runner.run_date(D[2])
    other = RunnerConfig(MULT, {"AAA": 1.25, "BBB": 3.0}, ROLLS, {"name": "stub"})
    changed, _ = make(tmp_path, data, config=other)
    with pytest.raises(RunnerError, match="another configuration"):
        changed.run_date(D[3])


def test_default_target_is_resolved_lazily_at_call_time(tmp_path, monkeypatch):
    src = InMemorySettlementSource({D[2]: nov(1.0, 1.0)})
    monkeypatch.setitem(sys.modules, "forward.strategy", None)
    runner = PaperRunner(tmp_path / "l.jsonl", src, CONFIG)  # construction needs no strategy
    with pytest.raises(ImportError):
        runner.run_date(D[2])
    fake = types.ModuleType("forward.strategy")
    fake.target_positions = lambda history, prev, config: {"AAA": 1, "BBB": 0}
    monkeypatch.setitem(sys.modules, "forward.strategy", fake)
    assert runner.run_date(D[2])["orders"] == {"AAA": 1}


def test_config_validation():
    with pytest.raises(RunnerError):
        RunnerConfig({"AAA": 2.0}, {"AAA": 1.0, "BBB": 1.0}, ROLLS)
    with pytest.raises(RunnerError):
        RunnerConfig({"AAA": 0.0}, {"AAA": 1.0}, ROLLS)
    with pytest.raises(RunnerError):
        RunnerConfig({"ZZZ": 1.0}, {"ZZZ": 1.0}, ROLLS)
