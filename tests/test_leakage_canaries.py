"""Leakage suite (Stage C, Task 4): planted-future canaries, mutation positive controls,
the latency control, and structural point-in-time checks.

A failure here is a STOP-THE-LINE event: no backtest number is trustworthy until it passes.
Thresholds live in ``sim.leakage_canaries.CRITERIA`` and were fixed before any run.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from datetime import date

import numpy as np
import pytest

from data.research_bars import RESEARCH_SERIES_PATH
from sim import leakage_canaries as lc
from sim.costs import load_slippage_table
from sim.engine import (
    BAR_COLUMNS,
    NO_ROLL_BLACKOUT,
    EngineConfig,
    EngineInvariantError,
    _Order,
    _Run,
    iter_bars,
    roll_blackout_dates,
    splice_trade_dates_from_parquet,
)
from strategy.interface import BAR_FIELD_AVAILABILITY, Bar
from strategy.random_baseline import RandomBaseline

TABLE = load_slippage_table()
CONFIG = EngineConfig(restart_on_terminal=True, roll_blackout=NO_ROLL_BLACKOUT)


@pytest.fixture(scope="module")
def synthetic_report() -> dict:
    return lc.run_suite(lc.synthetic_rth_bars(25, seed=9), TABLE, seed=4)


# ------------------------------------------------------------------ planting itself ----
class TestPlanting:
    def test_input_frame_is_not_mutated_and_prices_stay_valid(self) -> None:
        frame = lc.synthetic_rth_bars(3, seed=1)
        before = frame.copy()
        planted = lc.plant_canaries(frame, seed=2)
        assert frame.equals(before)
        out = planted.frame
        ticks = out[["open", "high", "low", "close"]].to_numpy() / 0.25
        assert np.allclose(ticks, np.round(ticks))  # still on the 0.25 grid
        assert (out["high"] >= out[["open", "close"]].max(axis=1)).all()
        assert (out["low"] <= out[["open", "close"]].min(axis=1)).all()
        list(iter_bars(out))  # every row still passes construct_bar

    def test_jump_is_inside_the_marked_bar_and_carried_forward(self) -> None:
        frame = lc.synthetic_rth_bars(2, seed=1)
        planted = lc.plant_canaries(frame, seed=3)
        ts = frame["ts_event"].to_numpy()
        for marked_ts, direction in list(planted.leak_markers.items())[:5]:
            i = int(np.flatnonzero(ts == marked_ts)[0])
            orig_body = frame["close"].iloc[i] - frame["open"].iloc[i]
            new_body = planted.frame["close"].iloc[i] - planted.frame["open"].iloc[i]
            # The body grows by exactly d * 16 ticks = d * 4.00 points.
            assert new_body - orig_body == pytest.approx(direction * 4.0)
            # Bar i+1 carries the jump forward: its shift exceeds bar i's by d * 4.00 points.
            shift_next = planted.frame["open"].iloc[i + 1] - frame["open"].iloc[i + 1]
            shift_here = planted.frame["open"].iloc[i] - frame["open"].iloc[i]
            assert shift_next - shift_here == pytest.approx(direction * 4.0)
        # Latency markers sit exactly one bar (60 s) before each leak marker.
        assert sorted(k + 60_000_000_000 for k in planted.latency_markers) == sorted(
            planted.leak_markers)

    def test_markers_are_spaced_and_directions_are_balanced(self) -> None:
        planted = lc.plant_canaries(lc.synthetic_rth_bars(40, seed=5), seed=6)
        keys = sorted(planted.leak_markers)
        gaps = np.diff(keys) / 60_000_000_000
        assert gaps.min() >= lc.MARK_EVERY_MINUTES
        directions = np.array(list(planted.leak_markers.values()))
        n = len(directions)
        # Fair-coin directions: long share within 4 binomial SE of 0.5.
        assert abs((directions > 0).mean() - 0.5) < 4 * (0.25 / n) ** 0.5


# ------------------------------------------------------------------ the canaries ----
class TestCanariesSynthetic:
    def test_real_engine_shows_no_edge_from_the_planted_future(self, synthetic_report) -> None:
        check = synthetic_report["checks"]["leak_canary_real_engine"]
        assert check["passed"], check
        assert abs(check["mean_captured_ticks"]) < lc.JUMP_TICKS / 4

    @pytest.mark.parametrize("mutant", ["same_bar_fill", "peek_next_bar"])
    def test_positive_controls_are_detected(self, synthetic_report, mutant: str) -> None:
        check = synthetic_report["checks"][f"positive_control_{mutant}_detected"]
        assert check["passed"], check
        assert check["mean_captured_ticks"] >= lc.JUMP_TICKS / 2 and check["hit_rate"] > 0.9

    def test_latency_control_is_captured_by_the_real_engine(self, synthetic_report) -> None:
        check = synthetic_report["checks"]["latency_control_real_engine"]
        assert check["passed"], check

    def test_mutants_act_too_early_for_the_latency_markers(self, synthetic_report) -> None:
        for diag in synthetic_report["diagnostics"].values():
            assert abs(diag["mean_captured_ticks"]) < lc.JUMP_TICKS / 4

    def test_random_baseline_shows_no_edge_even_on_a_leaky_engine(self, synthetic_report) -> None:
        checks = synthetic_report["checks"]
        for name in ("random_baseline_planted_real_engine", "random_baseline_clean_real_engine",
                     "random_baseline_planted_same_bar_fill_mutant"):
            assert checks[name]["passed"], (name, checks[name])

    def test_structural_checks(self, synthetic_report) -> None:
        for name in ("tripwire_no_peek", "strategy_receives_frozen_primitives_only",
                     "backdated_intents_refused", "hindsight_flag_never_gates_trading",
                     "every_bar_field_has_availability_class"):
            assert synthetic_report["checks"][name]["passed"], name
        assert synthetic_report["all_passed"]


# ------------------------------------------------------------------ the checks have teeth ----
class TestChecksHaveTeeth:
    def test_tripwire_catches_an_engine_that_pulls_one_bar_ahead(self) -> None:
        bars = list(iter_bars(lc.synthetic_rth_bars(1, seed=2)))
        feed = lc.CountingFeed(bars)
        spy = lc.TripwireSpy(feed)
        run = _Run(spy, CONFIG, TABLE)
        previous = next(feed)
        for upcoming in feed:  # a look-ahead buffer: bar N+1 is pulled before N is processed
            run.step(previous)
            previous = upcoming
        violations = [k for k, (_, pulled) in enumerate(spy.calls) if pulled != k + 1]
        assert spy.calls and len(violations) == len(spy.calls)  # every call saw N+2 pulled

    def test_fill_before_decision_raises_on_the_real_engine(self) -> None:
        bars = list(iter_bars(lc.synthetic_rth_bars(1, seed=2)))
        run = _Run(RandomBaseline(seed=1), CONFIG, TABLE)
        run.step(bars[0])
        # An order decided at bar 1's close cannot fill at bar 1's open.
        with pytest.raises(EngineInvariantError, match="before the decision"):
            run.fill(_Order(bars[1].decision_ts_ns, 1, "strategy"), bars[1], 96_000, "strategy")

    def test_frozen_primitive_check_rejects_containers_and_mutables(self) -> None:
        @dataclass(frozen=True)
        class Leaky:
            future: tuple

        @dataclass
        class Mutable:
            x: int

        assert not lc.only_frozen_primitives(Leaky(()))
        assert not lc.only_frozen_primitives(Mutable(1))

    def test_hindsight_class_is_recorded_for_vendor_degraded_day(self) -> None:
        assert set(BAR_FIELD_AVAILABILITY) == {f.name for f in fields(Bar)}
        assert BAR_FIELD_AVAILABILITY["vendor_degraded_day"] == "hindsight"


# ------------------------------------------------------------------ real research bars ----
@pytest.mark.skipif(not RESEARCH_SERIES_PATH.is_file(), reason="research parquet not present")
def test_canaries_on_one_real_research_month() -> None:
    from data.research_bars import load_research_bars

    frame = load_research_bars(BAR_COLUMNS)
    frame = frame[(frame["trade_date"] >= "2025-10-01")
                  & (frame["trade_date"] <= "2025-10-31")].reset_index(drop=True)
    blackout = roll_blackout_dates(splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH), 2)
    report = lc.run_suite(frame, TABLE, roll_blackout=blackout)
    failed = {k: v for k, v in report["checks"].items() if not v["passed"]}
    assert not failed, failed
    assert date.fromisoformat(str(frame["trade_date"].iloc[0])) >= date(2025, 10, 1)
