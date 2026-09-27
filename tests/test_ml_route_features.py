"""M4 features and targets with known answers; M7.1 validator and canaries; M7.2 perturbation."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import date

import numpy as np
import pandas as pd
import pytest

from ml_route.constants import FEATURES_DISTILLABLE
from ml_route.dataset import build_from_bars
from ml_route.features import Bars, FeatureLeak
from ml_route.inputs import CostBucket, VehicleCost, day_times
from ml_route.rows import COL, validate_availability
from ml_route.synthetic import bars_from_frame, synthetic_bars, synthetic_events, synthetic_inputs

NS_MIN = 60_000_000_000
FIRST, LAST = date(2019, 5, 6), date(2020, 1, 31)
SPEC = {"NQ": ("equity", 0.25, 8000.0), "RTY": ("equity", 0.1, 1500.0),
        "ZN": ("rates", 0.015625, 125.0)}


@pytest.fixture(scope="module")
def world() -> dict:
    frames = {r: synthetic_bars(r, g, FIRST, LAST, i + 1, tick, p0)
              for i, (r, (g, tick, p0)) in enumerate(SPEC.items())}
    bars = {r: bars_from_frame(r, f) for r, f in frames.items()}
    events = synthetic_events(list(SPEC), FIRST, LAST, seed=5)
    inputs = synthetic_inputs({r: FIRST for r in SPEC}, events)
    table = build_from_bars(bars, inputs)
    return {"frames": frames, "bars": bars, "inputs": inputs, "table": table}


def _row(world: dict, root: str, horizon: str = "h30") -> int:
    tb = world["table"]
    ok = np.flatnonzero((tb.product == root) & tb.complete_mask(horizon))
    assert ok.size > 20
    return int(ok[len(ok) // 2])


def _close_at(frame: pd.DataFrame, ts: int) -> float:
    return float(frame.loc[frame["ts_event"] == ts, "close"].iloc[0])


def _open_at(frame: pd.DataFrame, ts: int) -> float:
    return float(frame.loc[frame["ts_event"] == ts, "open"].iloc[0])


def _sigma_by_hand(world: dict, root: str, day: np.datetime64) -> float:
    frame = world["frames"][root]
    group = SPEC[root][0]
    moves = []
    for d in sorted(frame["trade_date"].unique()):
        if np.datetime64(d) >= day:
            break
        dt = day_times(root, group, date.fromisoformat(d))
        if dt.early_halt:
            continue
        moves.append(abs(_close_at(frame, dt.close_ns - NS_MIN) - _open_at(frame, dt.open_ns)))
    per_unit = world["inputs"].products[root].vehicle_ticks_per_vendor_unit
    return float(np.mean(moves[-20:])) * per_unit


class TestKnownAnswers:
    def test_sigma_is_the_mean_day_move_of_the_20_prior_complete_dates(self, world) -> None:
        tb = world["table"]
        r = _row(world, "NQ")
        assert tb.sigma[r] == pytest.approx(_sigma_by_hand(world, "NQ", tb.day[r]), rel=1e-12)

    def test_returns_and_target_by_hand(self, world) -> None:
        tb, frame = world["table"], world["frames"]["NQ"]
        r = _row(world, "NQ")
        t, sig = int(tb.t_ns[r]), tb.sigma[r]
        f1 = (_close_at(frame, t - NS_MIN) - _close_at(frame, t - 6 * NS_MIN)) * 4 / sig
        f5 = (_close_at(frame, t - NS_MIN) - _close_at(frame, t - 121 * NS_MIN)) * 4 / sig
        assert tb.X[r, COL["F1_ret5"]] == pytest.approx(f1, rel=1e-12)
        assert tb.X[r, COL["F5_ret120"]] == pytest.approx(f5, rel=1e-12)
        from ml_route.inputs import COSTS_PATH

        raw = json.loads(COSTS_PATH.read_text(encoding="utf-8"))
        mnq = raw["products"]["MNQ"]

        def side(ts: int, s: str) -> float:
            local = pd.Timestamp(ts, tz="UTC").tz_convert("America/Chicago")
            m = local.hour * 60 + local.minute
            b = [b for b in mnq["buckets"] if b["start_min"] <= m < b["end_min"]][0]
            return b["side_ticks"][s]

        cost = (mnq["commission_rt_usd"] / mnq["tick_value_usd"] + side(t + NS_MIN, "buy")
                + side(t + 30 * NS_MIN, "sell"))
        move = (_open_at(frame, t + 30 * NS_MIN) - _open_at(frame, t + NS_MIN)) * 4
        assert tb.y["h30"][r] == pytest.approx((move - cost) / sig, rel=1e-12)
        assert tb.cost["h30"][r] == pytest.approx(cost / sig, rel=1e-12)

    def test_to_f_horizon_exits_at_the_flatten_bar(self, world) -> None:
        tb = world["table"]
        r = _row(world, "NQ", "hF")
        dt = day_times("NQ", "equity", tb.day[r].astype(object))
        assert tb.exit_ns["hF"][r] == dt.flatten_ns

    def test_lead_feature_reads_the_lead_by_hand(self, world) -> None:
        tb, lead = world["table"], world["frames"]["NQ"]
        r = _row(world, "RTY")
        t = int(tb.t_ns[r])
        lead_rows = np.flatnonzero((tb.product == "NQ") & (tb.t_ns == t))
        sig_nq = tb.sigma[lead_rows[0]]
        want = (_close_at(lead, t - NS_MIN) - _close_at(lead, t - 31 * NS_MIN)) * 4 / sig_nq
        assert tb.X[r, COL["F16_lead_ret30"]] == pytest.approx(want, rel=1e-12)

    def test_decision_grid_counts(self, world) -> None:
        tb = world["table"]
        day = tb.day[_row(world, "NQ")]
        assert int(((tb.product == "NQ") & (tb.day == day)).sum()) == 12  # 09:00..14:30 CT
        zn_days = tb.day[tb.product == "ZN"]
        assert np.unique(zn_days, return_counts=True)[1].max() == 13  # 07:50..13:50 CT
        halt = np.datetime64("2019-07-03")  # equity early halt: the whole date is excluded
        assert not ((tb.product == "NQ") & (tb.day == halt)).any()
        assert tb.counts["dates_early_halt"] > 0

    def test_event_guard_and_cpi_window_exclude_decisions(self, world) -> None:
        from ml_route.dataset import _cut, session_times
        from ml_route.features import build_daily
        from ml_route.rows import build_rows

        inputs = world["inputs"]
        spec = replace(inputs.products["NQ"], cpi_no_open=True)
        bars = _cut(world["bars"]["NQ"], FIRST, LAST)
        daily = build_daily(bars, spec, session_times("NQ", "equity", bars.trade_date))
        pos = daily.pos_of(np.datetime64("2019-12-10"))
        o = daily.times[pos].open_ns
        rel = np.array([o + 60 * NS_MIN], dtype=np.int64)  # release at 09:30 CT
        cpi = np.array([o + 151 * NS_MIN], dtype=np.int64)  # CPI at 11:01 CT
        tb = build_rows(bars, daily, spec, inputs.costs["MNQ"], frozenset(), rel, cpi, None,
                        only_date_pos=pos)
        times = ((tb.t_ns - o) // NS_MIN).tolist()
        assert 60 not in times and 150 not in times and 30 in times and 180 in times
        assert tb.counts["decisions_event_guard"] == 1 and tb.counts["decisions_cpi_window"] == 1

    def test_roll_blackout_dates_are_excluded(self, world) -> None:
        bars = world["bars"]
        tb = build_from_bars({"NQ": bars["NQ"]}, world["inputs"],
                             {"NQ": frozenset({date(2019, 12, 10)})})
        assert not (tb.day == np.datetime64("2019-12-10")).any()
        assert tb.counts["dates_roll_blackout"] == 1


def test_event_window_cost_is_largest_half_spread_plus_own_depth() -> None:
    from types import MappingProxyType

    b1 = CostBucket(0, 60, 0.5, MappingProxyType({"buy": 0.25, "sell": 0.0}))
    b2 = CostBucket(60, 120, 1.5, MappingProxyType({"buy": 0.0, "sell": 0.0}))
    vc = VehicleCost("X", 2.0, (b1, b2), 1.5)
    assert vc.side_ticks(10, "buy", False) == 0.75
    assert vc.side_ticks(10, "buy", True) == 1.75  # T12-4: max s_b + the fill bucket's depth
    assert vc.long_round_turn_ticks(10, 70, True, False) == pytest.approx(2.0 + 1.75 + 1.5)
    assert vc.side_ticks(200, "buy", False) is None


class TestValidatorCanaries:
    def test_honest_table_passes(self, world) -> None:
        validate_availability(world["table"])

    @staticmethod
    def _plant(world: dict, value_idx_of_row) -> None:  # noqa: ANN001
        tb = world["table"]
        bars: Bars = world["bars"]["NQ"]
        rows = np.flatnonzero((tb.product == "NQ") & tb.complete_mask("h30"))
        X, A = tb.X.copy(), tb.avail.copy()
        idx = value_idx_of_row(bars, tb, rows)
        X[rows, 0] = bars.open[idx] if value_idx_of_row.__name__ == "exit_bar" else bars.close[idx]
        A[rows, 0] = bars.ts[idx] + NS_MIN  # availability from the latest bar the value reads
        validate_availability(replace(tb, X=X, avail=A))

    def test_feature_equal_to_the_target_is_rejected(self, world) -> None:
        def exit_bar(bars, tb, rows):  # noqa: ANN001, ANN202
            return bars.idx_at(tb.exit_ns["h30"][rows])

        with pytest.raises(FeatureLeak, match="F1_ret5"):
            self._plant(world, exit_bar)
        tb = world["table"]  # and literally equal to y, with the target's availability
        rows = np.flatnonzero(tb.complete_mask("h30"))
        X, A = tb.X.copy(), tb.avail.copy()
        X[rows, 3], A[rows, 3] = tb.y["h30"][rows], tb.exit_ns["h30"][rows]
        with pytest.raises(FeatureLeak, match="F4_ret60"):
            validate_availability(replace(tb, X=X, avail=A))

    def test_feature_equal_to_the_next_bars_close_is_rejected(self, world) -> None:
        def next_bar(bars, tb, rows):  # noqa: ANN001, ANN202
            return bars.idx_at(tb.t_ns[rows])  # the bar opening at t closes at t + 1 minute

        with pytest.raises(FeatureLeak, match="F1_ret5"):
            self._plant(world, next_bar)


def _perturb_after(bars: Bars, cutoff_ns: int, seed: int) -> Bars:
    """Every bar that closes after ``cutoff_ns`` gets random prices and volume (times kept)."""
    rng = np.random.default_rng(seed)
    late = bars.ts + NS_MIN > cutoff_ns
    n = int(late.sum())

    def rnd(a: np.ndarray, scale: float) -> np.ndarray:
        out = a.copy()
        out[late] = a[late] * (1 + scale * rng.standard_normal(n))
        return out

    hi, lo, op, cl = rnd(bars.high, 0.05), rnd(bars.low, 0.05), rnd(bars.open, 0.05), rnd(
        bars.close, 0.05)
    top = np.maximum.reduce([hi, lo, op, cl])
    bot = np.minimum.reduce([hi, lo, op, cl])
    vol = bars.volume.copy()
    vol[late] = rng.integers(1, 1000, n)
    return replace(bars, open=op, high=top, low=bot, close=cl, volume=vol)


@pytest.fixture(scope="module")
def cutoff(world) -> int:  # noqa: ANN001
    tb = world["table"]
    rows = np.flatnonzero((tb.product == "NQ") & tb.complete_mask("h30"))
    return int(tb.t_ns[rows[len(rows) // 2]])


class TestPerturbation:
    @staticmethod
    def _same_rows(a, b, keep: np.ndarray) -> None:  # noqa: ANN001
        assert np.array_equal(a.t_ns[keep], b.t_ns[keep])
        np.testing.assert_array_equal(a.X[keep], b.X[keep])

    def test_single_product_features_and_prediction_unchanged(self, world, cutoff) -> None:
        from ml_route import lgbm

        bars = dict(world["bars"])
        bars["NQ"] = _perturb_after(bars["NQ"], cutoff, seed=11)
        tb0 = world["table"]
        tb1 = build_from_bars(bars, world["inputs"])
        keep = (tb0.product == "NQ") & (tb0.t_ns <= cutoff)
        self._same_rows(tb0, tb1, keep)
        later = (tb0.product == "NQ") & (tb0.t_ns > cutoff) & tb0.complete_mask("h30")
        assert not np.allclose(np.nan_to_num(tb0.X[later]), np.nan_to_num(tb1.X[later]))
        fit_rows = np.flatnonzero(tb0.complete_mask("h30"))
        products = sorted(set(tb0.product.astype(str)))
        X0, names = lgbm.design_matrix(tb0.X, tb0.product, tb0.cluster, products)
        X1, _ = lgbm.design_matrix(tb1.X, tb1.product, tb1.cluster, products)
        booster, _, _ = lgbm.fit(X0[fit_rows], tb0.y["h30"][fit_rows], names,
                                 {"num_leaves": 7, "min_data_in_leaf": 500, "lambda_l2": 1.0})
        np.testing.assert_array_equal(lgbm.predict(booster, X0[keep]),
                                      lgbm.predict(booster, X1[keep]))

    def test_cross_product_lead_feature_unchanged(self, world, cutoff) -> None:
        bars = dict(world["bars"])
        bars["NQ"] = _perturb_after(bars["NQ"], cutoff, seed=12)  # only the lead's future
        tb0 = world["table"]
        tb1 = build_from_bars(bars, world["inputs"])
        keep = (tb0.product == "RTY") & (tb0.t_ns <= cutoff)
        self._same_rows(tb0, tb1, keep)
        c = COL["F16_lead_ret30"]
        later = (tb0.product == "RTY") & (tb0.t_ns > cutoff) & np.isfinite(tb0.X[:, c])
        assert not np.allclose(tb0.X[later, c], tb1.X[later, c])


def test_feature_names_are_the_frozen_seventeen() -> None:
    assert list(COL) == list(FEATURES_DISTILLABLE) and len(COL) == 17
