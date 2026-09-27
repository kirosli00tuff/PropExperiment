"""M7.7: a distilled route rule's strategy wrapper through the engine and the leakage canaries'
machinery (sim/leakage_canaries.py, used as is): timing, train/test feature parity, a planted
future, the cross-product (F16) canary, and the tripwire."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

import numpy as np
import pandas as pd
import pytest

from ml_route.dataset import build_from_bars
from ml_route.inputs import day_times
from ml_route.rows import COL
from ml_route.rule_wrapper import DistilledRuleStrategy, LeadSpec, rule_spec_from_json
from ml_route.surrogate import Leaf, condition_mask, rule_json
from ml_route.synthetic import bars_from_frame, synthetic_events, synthetic_inputs
from sim import leakage_canaries as lc
from sim.costs import load_slippage_table
from sim.engine import NO_ROLL_BLACKOUT, EngineConfig, FillEvent, iter_bars

NS_MIN = 60_000_000_000
CONFIG = EngineConfig(restart_on_terminal=True, roll_blackout=NO_ROLL_BLACKOUT)


def _frame(seed: int) -> tuple[pd.DataFrame, dict]:
    frame = lc.synthetic_rth_bars(160, seed=seed, start=date(2025, 6, 2))
    times = {}
    for d in sorted(frame["trade_date"].unique()):
        dt = day_times("NQ", "equity", date.fromisoformat(d))
        if dt is not None:
            times[date.fromisoformat(d)] = dt
    keep = frame["trade_date"].isin({d.isoformat() for d in times})
    return frame[keep].reset_index(drop=True), times


def _rule(cluster: str, conditions: tuple, horizon: str = "h30"):  # noqa: ANN202
    return rule_spec_from_json(rule_json(cluster, "lgbm", horizon, Leaf(0, 1, conditions, 0.1), 1,
                                         0.05, ["X"], "X", {}, {}))


@dataclass
class _Flat:
    """A flat account view for the direct driver (decisions do not depend on the account)."""

    position_micros: int = 0
    pending_signed_micros: int = 0


def _drive(strat: DistilledRuleStrategy, frame: pd.DataFrame) -> list:
    for bar in iter_bars(frame):
        strat.on_bar(bar, _Flat())
    return strat.decisions


@pytest.fixture(scope="module")
def world() -> dict:
    frame, times = _frame(3)
    first, last = min(times), max(times)
    events = synthetic_events(["NQ", "RTY"], first, last, 5)
    inputs = synthetic_inputs({"NQ": first, "RTY": first}, events)
    spec = _rule("K1", (("F1_ret5", ">", 0.0),))
    strat = DistilledRuleStrategy(spec, inputs.products["NQ"], inputs.costs["MNQ"], times,
                                  frozenset(), events.of("NQ"), events.cpi)
    feed = lc.CountingFeed(iter_bars(frame))
    pulls: list[tuple[int, int]] = []

    class Spy:
        name = strat.name

        def on_bar(self, bar, account):  # noqa: ANN001, ANN202
            pulls.append((bar.ts_event_ns, feed.pulled))
            return strat.on_bar(bar, account)

    from sim.engine import run_backtest

    result = run_backtest(feed, Spy(), CONFIG, load_slippage_table())
    table = build_from_bars({"NQ": bars_from_frame("NQ", frame)}, inputs, last=last)
    return {"frame": frame, "times": times, "inputs": inputs, "events": events, "spec": spec,
            "strat": strat, "result": result, "table": table, "pulls": pulls}


def test_the_engine_never_hands_the_wrapper_a_later_bar(world) -> None:
    pulls = world["pulls"]
    assert len(pulls) == len(world["frame"])
    assert all(pulled == k + 1 for k, (_, pulled) in enumerate(pulls))


def test_features_equal_the_training_rows_at_every_decision(world) -> None:
    tb, dec = world["table"], world["strat"].decisions
    complete_rows = {int(t) for t in tb.t_ns[np.isfinite(tb.X).all(axis=1)]}
    complete_dec = {d.t_ns for d in dec if d.features_complete}
    assert complete_dec == complete_rows and len(complete_rows) > 50
    fired_train = {int(t) for t, f in zip(tb.t_ns, condition_mask(
        np.nan_to_num(tb.X, nan=-1.0), world["spec"].conditions), strict=True)
        if f and int(t) in complete_rows}
    assert {d.t_ns for d in dec if d.fired} == fired_train


def test_entries_fill_at_t_plus_one_minute_and_exits_at_t_plus_h(world) -> None:
    fills = [f for f in world["result"].events(FillEvent) if f.reason == "strategy"]
    acted = [d.t_ns for d in world["strat"].decisions if d.acted]
    entries = [f for f in fills if f.side == "buy"]
    exits = [f for f in fills if f.side == "sell"]
    assert len(entries) == len(acted) > 10
    assert [f.fill_ts_ns for f in entries] == [t + NS_MIN for t in acted]
    assert [f.fill_ts_ns for f in exits] == [t + 30 * NS_MIN for t in acted[:len(exits)]]


def test_a_planted_future_does_not_change_earlier_decisions(world) -> None:
    dec0 = world["strat"].decisions
    complete = [d.t_ns for d in dec0 if d.features_complete]
    cutoff = complete[len(complete) // 2]
    frame = world["frame"].copy()
    late = frame["ts_event"].to_numpy() + NS_MIN > cutoff
    rng = np.random.default_rng(99)
    jump = rng.integers(-40, 41, int(late.sum())) * 0.25
    for col in ("open", "high", "low", "close"):
        frame.loc[late, col] = frame.loc[late, col] + jump
    frame.loc[late, "volume"] = rng.integers(1, 1000, int(late.sum()))
    strat = DistilledRuleStrategy(world["spec"], world["inputs"].products["NQ"],
                                  world["inputs"].costs["MNQ"], world["times"], frozenset(),
                                  world["events"].of("NQ"), world["events"].cpi)
    dec1 = _drive(strat, frame)
    before0 = [(d.t_ns, d.features_complete, d.fired) for d in dec0 if d.t_ns <= cutoff]
    before1 = [(d.t_ns, d.features_complete, d.fired) for d in dec1 if d.t_ns <= cutoff]
    assert before0 == before1
    after0 = [d.fired for d in dec0 if d.t_ns > cutoff and d.features_complete]
    after1 = [d.fired for d in dec1 if d.t_ns > cutoff and d.features_complete]
    assert after0 != after1  # the planted future is visible once it is the past


def test_cross_product_lead_bars_handed_over_early_change_nothing(world) -> None:
    lead_frame = world["frame"]
    rty_frame, _ = _frame(4)
    rty_frame = rty_frame[rty_frame["trade_date"].isin(set(lead_frame["trade_date"]))]
    inputs, times, ev = world["inputs"], world["times"], world["events"]
    spec = _rule("K1", (("F16_lead_ret30", ">", 0.0),))
    lead = LeadSpec("NQ", 4.0, inputs.products["NQ"], times)

    def run(lead_bars: pd.DataFrame) -> list:
        strat = DistilledRuleStrategy(spec, inputs.products["RTY"], inputs.costs["M2K"], times,
                                      frozenset(), ev.of("RTY"), ev.cpi, lead=lead)
        for bar in iter_bars(lead_bars):  # EVERY lead bar, future ones included, up front
            strat.observe_lead(bar)
        return _drive(strat, rty_frame.reset_index(drop=True))

    dec0 = run(lead_frame)
    complete = [d.t_ns for d in dec0 if d.features_complete]
    assert len(complete) > 50
    tb = build_from_bars({"NQ": bars_from_frame("NQ", lead_frame),
                          "RTY": bars_from_frame("RTY", rty_frame)}, inputs, last=max(times))
    rty = tb.product == "RTY"
    fin = np.isfinite(tb.X).all(axis=1) & rty
    assert set(complete) == {int(t) for t in tb.t_ns[fin]}
    fired = {int(t) for t, v in zip(tb.t_ns[fin], tb.X[fin, COL["F16_lead_ret30"]] > 0,
                                    strict=True) if v}
    assert {d.t_ns for d in dec0 if d.fired} == fired
    cutoff = complete[len(complete) // 2]
    perturbed = lead_frame.copy()
    late = perturbed["ts_event"].to_numpy() + NS_MIN > cutoff
    shift = np.random.default_rng(7).integers(-80, 81, int(late.sum())) * 0.25
    for col in ("open", "high", "low", "close"):
        perturbed.loc[late, col] = perturbed.loc[late, col] + shift
    dec1 = run(perturbed)
    key = [(d.t_ns, d.features_complete, d.fired) for d in dec0 if d.t_ns <= cutoff]
    assert key == [(d.t_ns, d.features_complete, d.fired) for d in dec1 if d.t_ns <= cutoff]


def test_a_non_lead_leg_without_its_lead_is_refused(world) -> None:
    inputs, ev = world["inputs"], world["events"]
    with pytest.raises(ValueError, match="F16 reads the cluster lead NQ"):
        DistilledRuleStrategy(world["spec"], inputs.products["RTY"], inputs.costs["M2K"],
                              world["times"], frozenset(), ev.of("RTY"), ev.cpi)
    no_vehicle = replace(inputs.products["NQ"], vehicle=None)
    with pytest.raises(ValueError, match="no vehicle"):
        DistilledRuleStrategy(world["spec"], no_vehicle, inputs.costs["MNQ"], world["times"],
                              frozenset(), ev.of("NQ"), ev.cpi)
