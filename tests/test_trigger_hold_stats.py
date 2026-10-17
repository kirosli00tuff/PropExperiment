"""trigger_hold.stats, trigger_hold.power and trigger_hold.types: the HAC alpha against hand
computations, p_alpha, Holm, the survivor rule and the cap, the confirmation composite and
hurdle, the power numbers, the non-overlapping count, the events schema."""

from __future__ import annotations

import math
from datetime import date

import numpy as np
import pytest

from base_rules.stats import newey_west_se, one_sided_p_normal, one_sided_p_t
from trigger_hold import constants as K
from trigger_hold.power import (
    expected_t,
    inconclusive,
    nonoverlapping,
    power_at,
    power_gate,
    power_holm1,
)
from trigger_hold.stats import (
    alpha_ols,
    confirmation_hurdle,
    confirmation_verdicts,
    discovery_survivors,
    dsr_with_variance,
    holm05,
    pbo_cscv,
    raw_stats,
)
from trigger_hold.types import (
    EventsError,
    TriggerEvent,
    events_record,
    parse_events,
)
from trigger_hold.units import Unit


# ------------------------------------------------------------------ HAC alpha ----
def test_intercept_only_hac_is_newey_west_by_hand() -> None:
    y = [1.0, -1.0, 2.0, 0.0]
    # e = [.5, -1.5, 1.5, -.5]; sum e^2 = 5; lag-1 sum = -3.75; w = 1/2;
    # S = 5 + 2 x .5 x -3.75 = 1.25; V = S / n^2 = 0.078125
    res = alpha_ols(y, [], 1)
    assert res["se_hac"] == pytest.approx(math.sqrt(0.078125), abs=1e-15)
    assert res["se_hac"] == pytest.approx(newey_west_se(np.array(y), 1), abs=1e-15)
    assert res["t_nw"] == pytest.approx(raw_stats(y, 1)["t_nw"])
    assert res["alpha"] == pytest.approx(0.5)


def _hac_by_loops(y, xs, lags):  # noqa: ANN001, ANN202
    """An independent pure-Python OLS + Bartlett sandwich (3 columns, Gauss-Jordan inverse)."""
    n = len(y)
    X = [[1.0, *[x[t] for x in xs]] for t in range(n)]
    k = len(X[0])
    xtx = [[sum(X[t][i] * X[t][j] for t in range(n)) for j in range(k)] for i in range(k)]
    inv = _inv(xtx)
    xty = [sum(X[t][i] * y[t] for t in range(n)) for i in range(k)]
    b = [sum(inv[i][j] * xty[j] for j in range(k)) for i in range(k)]
    e = [y[t] - sum(X[t][i] * b[i] for i in range(k)) for t in range(n)]
    S = [[sum(e[t] ** 2 * X[t][i] * X[t][j] for t in range(n)) for j in range(k)]
         for i in range(k)]
    for lag in range(1, min(lags, n - 1) + 1):
        w = 1 - lag / (lags + 1)
        for i in range(k):
            for j in range(k):
                S[i][j] += w * sum(e[t] * e[t - lag] * (X[t][i] * X[t - lag][j]
                                                        + X[t - lag][i] * X[t][j])
                                   for t in range(lag, n))
    V = [[sum(inv[i][a] * S[a][c] * inv[c][j] for a in range(k) for c in range(k))
          for j in range(k)] for i in range(k)]
    s2 = sum(v * v for v in e) / (n - k)
    return b, math.sqrt(V[0][0]), math.sqrt(s2 * inv[0][0])


def _inv(m):  # noqa: ANN001, ANN202
    k = len(m)
    a = [row[:] + [1.0 if i == j else 0.0 for j in range(k)] for i, row in enumerate(m)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(a[r][c]))
        a[c], a[p] = a[p], a[c]
        piv = a[c][c]
        a[c] = [v / piv for v in a[c]]
        for r in range(k):
            if r != c:
                f = a[r][c]
                a[r] = [v - f * w for v, w in zip(a[r], a[c], strict=True)]
    return [row[k:] for row in a]


@pytest.mark.parametrize("lags", [1, 5, 20])
def test_alpha_hac_matches_an_independent_loop_implementation(lags: int) -> None:
    rng = np.random.default_rng(11)
    n = 60
    x1, x2 = rng.normal(size=n), rng.normal(size=n)
    y = 0.1 + 0.5 * x1 - 0.3 * x2 + rng.normal(size=n)
    res = alpha_ols(y, [x1, x2], lags)
    b, se_hac, se_plain = _hac_by_loops(list(y), [list(x1), list(x2)], lags)
    assert res["alpha"] == pytest.approx(b[0], rel=1e-10)
    assert res["betas"] == pytest.approx(b[1:], rel=1e-10)
    assert res["se_hac"] == pytest.approx(se_hac, rel=1e-10)
    assert res["se_plain"] == pytest.approx(se_plain, rel=1e-10)
    t_plain, t_nw = b[0] / se_plain, b[0] / se_hac
    assert res["p_alpha"] == pytest.approx(max(one_sided_p_t(t_plain, n - 3),
                                               one_sided_p_normal(t_nw)))
    assert 0 <= res["r2"] <= 1 and len(res["corr"]) == 2


def test_a_rank_deficient_design_leaves_alpha_undefined() -> None:
    y = [1.0, 2.0, 0.5, 1.5, 0.0]
    res = alpha_ols(y, [[0.0] * 5, [1.0, 2.0, 3.0, 4.0, 5.0]], 5)
    assert res["p_alpha"] is None and res["undefined"]


def test_raw_stats_sharpe_and_t() -> None:
    y = [0.01, -0.02, 0.03, 0.0, 0.015]
    r = raw_stats(y, 5)
    x = np.array(y)
    assert r["sharpe"] == pytest.approx(x.mean() / x.std(ddof=1) * math.sqrt(252))
    assert r["t"] == pytest.approx(x.mean() / (x.std(ddof=1) / math.sqrt(5)))


# ------------------------------------------------------------------ Holm and survivors ----
def test_holm_step_down_at_one_sided_005() -> None:
    p = {"a": 0.01, "b": 0.02, "c": 0.04, "d": None}
    assert holm05(p) == {"a": True, "b": False, "c": False, "d": False}
    assert holm05({"a": 0.01, "b": 0.02}) == {"a": True, "b": True}


def _row(p, t, s):  # noqa: ANN001, ANN202
    return {"p_alpha": p, "t_nw": t, "sharpe": s}


def test_the_survivor_rule_needs_all_three_checks_and_caps_at_four() -> None:
    rows = {"A": _row(1e-6, 4.0, 0.5), "B": _row(1e-6, 3.0, 0.6), "C": _row(1e-6, 3.0, 0.7),
            "D": _row(1e-6, 2.5, 0.31), "E": _row(1e-6, 2.2, 0.4), "F": _row(1e-6, 1.9, 0.9),
            "G": _row(1e-6, 2.6, 0.29), "H": _row(None, None, None), "I": _row(0.2, 5.0, 1.0)}
    out = discovery_survivors(rows)
    assert out["k"] == 9
    assert set(out["eligible"]) == {"A", "B", "C", "D", "E"}
    assert out["ranked"] == ["A", "C", "B", "D", "E"]  # t tie B/C broken by the larger Sharpe
    assert out["survivors"] == ["A", "C", "B", "D"] and out["cut_by_cap"] == ["E"]
    assert not out["checks"]["I"]["holm_rejects"]


def test_survivor_ties_in_t_and_sharpe_fall_to_the_id() -> None:
    rows = {"Z": _row(1e-6, 3.0, 0.5), "Y": _row(1e-6, 3.0, 0.5)}
    assert discovery_survivors(rows)["ranked"] == ["Y", "Z"]


# ------------------------------------------------------------------ confirmation ----
def test_the_confirmation_hurdle() -> None:
    assert confirmation_hurdle(1) == 2.0
    assert confirmation_hurdle(4) == pytest.approx(2.241402727604947)


def test_confirmation_verdicts_need_every_check_and_count_gated_survivors() -> None:
    good = {"status": "read", "p_alpha": 1e-4, "t_nw": 3.0, "sharpe_base": 0.5,
            "sharpe_stress": 0.2, "dsr": 0.97, "pbo_discovery": 0.3}
    rows = {"A": good, "B": {**good, "sharpe_stress": -0.1}, "C": {"status": K.INCONCLUSIVE},
            "D": {**good, "p_alpha": 0.03}}
    out = confirmation_verdicts(rows)["rows"]
    assert out["A"]["verdict"] == K.PASS
    assert out["B"]["verdict"] == K.NULL and not out["B"]["checks"]["stress_sharpe_positive"]
    assert out["C"]["verdict"] == K.INCONCLUSIVE
    # m = 4: A, B rejected at 0.05/4 and 0.05/3; D's 0.03 > 0.05/2; C (gated) still counts
    assert out["D"]["verdict"] == K.NULL and not out["D"]["checks"]["holm_rejects"]


def test_dsr_with_variance_over_the_discovery_series_and_pbo() -> None:
    rng = np.random.default_rng(5)
    series = {f"s{i}": list(rng.normal(0.0005 * i, 0.01, 400)) for i in range(4)}
    res = dsr_with_variance(series["s3"], series, 537)
    assert res["dsr"] is not None and 0 <= res["dsr"] <= 1 and res["n_trials"] == 537
    days = [date(2015, 1, 1).fromordinal(date(2015, 1, 1).toordinal() + i) for i in range(400)]
    pb = pbo_cscv({k: list(zip(days, v, strict=True)) for k, v in series.items()})
    assert 0 <= pb["pbo"] <= 1 and pb["n_strategies"] == 4 and pb["aligned_dates"] == 400


# ------------------------------------------------------------------ power ----
@pytest.mark.parametrize("n_dates,et,gate", [(1953, 1.392, 0.272), (1215, 1.098, 0.183)])
def test_power_numbers(n_dates: int, et: float, gate: float) -> None:
    assert expected_t(n_dates) == pytest.approx(et, abs=5e-4)
    assert power_gate(n_dates) == pytest.approx(gate, abs=5e-4)
    assert power_at(2.0, n_dates) == power_gate(n_dates)


def test_power_holm1_uses_the_larger_hurdle() -> None:
    assert power_holm1(1953, 1) == pytest.approx(power_gate(1953))
    from scipy.stats import norm

    z = float(norm.ppf(1 - 0.05 / 40))
    assert z == pytest.approx(3.0233, abs=1e-4)
    assert power_holm1(1953, 40) == pytest.approx(1 - 0.5 * math.erfc(-(z - expected_t(1953))
                                                                       / math.sqrt(2)))


def test_inconclusive_by_design() -> None:
    assert inconclusive(29, 0.9) and inconclusive(100, 0.19) and not inconclusive(30, 0.2)


def _unit(a: int, b: int) -> Unit:
    d0 = date(2015, 1, 1).toordinal()
    return Unit(date.fromordinal(d0 + a), date.fromordinal(d0 + b), 1, "X", "NQ",
                date.fromordinal(d0 + a), b - a)


def test_nonoverlapping_is_greedy_in_entry_order() -> None:
    units = [_unit(0, 5), _unit(3, 8), _unit(5, 10), _unit(9, 14), _unit(10, 15), _unit(10, 15)]
    # counted: (0,5), (5,10) [entry on the exit date counts], (10,15)
    assert nonoverlapping(units) == 3
    assert nonoverlapping([]) == 0


# ------------------------------------------------------------------ events schema ----
def test_an_event_row_with_a_price_or_pnl_key_is_refused() -> None:
    body = events_record("X1", "NQ", K.W_EXT, [TriggerEvent(date(2015, 3, 2), 10, 1, "X1")],
                         {"no signal": 3}, {})
    assert parse_events(body).events[0].side == 1
    body["events"][0]["pnl"] = 1.0
    with pytest.raises(EventsError):
        parse_events(body)


@pytest.mark.parametrize("side", [0, 2, True])
def test_side_must_be_plus_or_minus_one(side) -> None:
    with pytest.raises(EventsError):
        TriggerEvent(date(2015, 3, 2), 10, side, "X1")


def test_events_round_trip_sorted_and_duplicates_refused() -> None:
    evs = [TriggerEvent(date(2015, 3, 3), 20, -1, "X1"),
           TriggerEvent(date(2015, 3, 2), 10, 1, "X1")]
    body = events_record("X1", "NQ", K.W_CF, evs, {}, {"a": {"path": "p", "sha256": "0"}})
    got = parse_events(body)
    assert [e.d0 for e in got.events] == [date(2015, 3, 2), date(2015, 3, 3)]
    body["events"].append(dict(body["events"][0]))
    with pytest.raises(EventsError):
        parse_events(body)
