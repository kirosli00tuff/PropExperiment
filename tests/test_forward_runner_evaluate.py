"""forward.evaluate (E.22, ForwardRunnerCoder): E22-F1's frozen bar. Synthetic series only."""

from __future__ import annotations

import math
from datetime import date, timedelta

import numpy as np
import pytest

from forward.evaluate import (
    FROZEN_BAR,
    NW_LAG,
    EvaluationRefused,
    add_months,
    annualised_sharpe,
    evaluate,
    evaluate_ledger,
    newey_west,
    one_sided_p,
    passes,
)
from forward.ledger import Ledger, LedgerIntegrityError

START = date(2026, 11, 2)


def weekdays(start: date, end: date) -> list[date]:
    out, d = [], start
    while d <= end:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


def records(values, start=START):
    days = weekdays(start, start + timedelta(days=2 * len(values) + 10))[: len(values)]
    return [
        {"date": d.isoformat(), "net_pnl": float(v), "flags": []}
        for d, v in zip(days, values, strict=True)
    ]


def full_horizon(drift: float, scale: float = 400.0, seed: int = 20261016):
    days = weekdays(START, add_months(START, 36))
    rng = np.random.default_rng(seed)
    vals = drift + scale * rng.standard_normal(len(days))
    return [
        {"date": d.isoformat(), "net_pnl": float(v), "flags": []}
        for d, v in zip(days, vals, strict=True)
    ]


def nw_t_reference(x, lag):
    x = np.asarray(x, dtype=float)
    n, d = len(x), x - x.mean()
    s = d @ d / n
    for k in range(1, lag + 1):
        s += 2.0 * (1.0 - k / (lag + 1.0)) * (d[k:] @ d[:-k]) / n
    return x.mean() / math.sqrt(s / n)


def test_newey_west_matches_a_hand_computed_example():
    # x = [1,-1,2,0,3]: mean 1, deviations [0,-2,1,-1,2]
    # gamma0 = 10/5 = 2.0; gamma1 = (0-2-1-2)/5 = -1.0; gamma2 = (0+2+2)/5 = 0.8
    # lag 2 Bartlett weights 2/3, 1/3: LRV = 2 + 2(-2/3 + 0.8/3) = 1.2; se = sqrt(1.2/5)
    nw = newey_west([1.0, -1.0, 2.0, 0.0, 3.0], lag=2)
    assert nw.mean == 1.0
    assert nw.lrv == pytest.approx(1.2, abs=1e-12)
    assert nw.se == pytest.approx(math.sqrt(0.24), abs=1e-12)
    assert nw.t == pytest.approx(1.0 / math.sqrt(0.24), abs=1e-12)  # 2.0412...
    assert one_sided_p(nw.t) == pytest.approx(0.020613, abs=1e-6)


def test_newey_west_lag_zero_is_the_iid_t_with_divisor_n():
    x = [1.0, -1.0, 2.0, 0.0, 3.0]
    assert newey_west(x, lag=0).t == pytest.approx(1.0 / math.sqrt(2.0 / 5), abs=1e-12)


def test_newey_west_needs_more_observations_than_lags():
    with pytest.raises(ValueError):
        newey_west([1.0] * 10, lag=10)


def test_p_and_sharpe_formulas():
    assert one_sided_p(0.0) == 0.5
    assert one_sided_p(1.6448536269514722) == pytest.approx(0.05, abs=1e-12)
    x = [1.0, -1.0, 2.0, 0.0, 3.0]
    assert annualised_sharpe(x) == pytest.approx(1.0 / math.sqrt(2.5) * math.sqrt(252))
    assert annualised_sharpe([2.0, 2.0, 2.0]) is None


@pytest.mark.parametrize(
    "p,s,ok",
    [
        (0.05, 0.3, True),
        (0.0500001, 1.0, False),
        (0.01, 0.2999, False),
        (None, 1.0, False),
        (0.01, None, False),
    ],
)
def test_pass_rule_boundaries(p, s, ok):
    assert passes(p, s) is ok


def test_frozen_constants():
    assert NW_LAG == 10
    assert FROZEN_BAR["p_max"] == 0.05 and FROZEN_BAR["sharpe_min"] == 0.3
    assert FROZEN_BAR["horizon_months"] == 36 and FROZEN_BAR["kernel"] == "Bartlett"


def test_final_evaluation_is_refused_before_36_months():
    recs = records([10.0, -5.0] * 200)
    with pytest.raises(EvaluationRefused, match="interim=True"):
        evaluate(recs)


def test_interim_returns_descriptive_figures_without_p():
    recs = records([10.0, -5.0] * 200)
    out = evaluate(recs, interim=True)
    assert out["interim"] and not out["horizon_complete"]
    assert not {"p_one_sided", "nw_t", "nw_se", "nw_lrv", "pass"} & set(out)
    assert out["n_days"] == 400 and out["mean_daily_net_usd"] == 2.5


def test_full_horizon_evaluation_uses_lag_10_and_the_window_only():
    recs = full_horizon(drift=60.0)
    assert recs[-1]["date"] == add_months(START, 36).isoformat()  # 2029-11-02, a Friday
    out = evaluate(recs)
    window = [r["net_pnl"] for r in recs[:-1]]
    assert out["n_days"] == len(window)
    assert out["horizon_end_exclusive"] == "2029-11-02"
    assert out["nw_t"] == pytest.approx(nw_t_reference(window, 10), rel=1e-10)
    assert out["p_one_sided"] == pytest.approx(one_sided_p(out["nw_t"]), rel=1e-12)
    assert out["sharpe_annualised_net"] == pytest.approx(
        np.mean(window) / np.std(window, ddof=1) * math.sqrt(252), rel=1e-10
    )
    assert out["pass"] is passes(out["p_one_sided"], out["sharpe_annualised_net"])
    later = recs + [{"date": "2029-11-05", "net_pnl": 1e9, "flags": []}]
    assert evaluate(later)["nw_t"] == out["nw_t"]


def test_pass_and_fail_on_clear_synthetic_series():
    assert evaluate(full_horizon(drift=80.0))["pass"] is True
    assert evaluate(full_horizon(drift=-20.0))["pass"] is False


def test_clock_start_after_the_first_record_is_refused():
    recs = full_horizon(drift=0.0)
    with pytest.raises(ValueError):
        evaluate(recs, clock_start=date(2026, 11, 3))
    with pytest.raises(EvaluationRefused):
        evaluate([])


def test_evaluate_ledger_verifies_the_chain_first(tmp_path):
    led = Ledger(tmp_path / "l.jsonl")
    for r in records([1.0, 2.0, -1.0] * 5):
        led.append(r)
    assert evaluate_ledger(led.path, interim=True)["n_days"] == 15
    text = led.path.read_text(encoding="ascii").replace('"net_pnl":2.0', '"net_pnl":20.0', 1)
    led.path.write_text(text, encoding="ascii")
    with pytest.raises(LedgerIntegrityError):
        evaluate_ledger(led.path, interim=True)


def test_add_months_clamps_to_month_end():
    assert add_months(date(2027, 1, 31), 1) == date(2027, 2, 28)
    assert add_months(date(2026, 11, 2), 36) == date(2029, 11, 2)
