"""E.29 basket tests (not part of the repo suite).

Run (repo root): OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 nice -n 10 \
    uv run pytest -q -p no:cacheprovider reports/stage_e29_briefs/work/basket/test_e29_basket.py

(a) B0 reproduces E.28's QM pair at all five firms: mu*_lim, mu*_mkt, mu10K, cost per attempt, and every stored
    on-lattice evaluation of pairs/<firm>__QM.json that the B0 search also visits, bit for bit.
(c) one member at zero trades (any rho) reduces to the other member alone (law identity, bit for bit).
(d) the trade split and the lot arithmetic.
"""

from __future__ import annotations

import json
import math
import multiprocessing as mp
import os
import sys
from pathlib import Path
from typing import Any

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import e29_basket as B  # noqa: E402

PAIRS = B.E28_WORK / "pairs"


def _b0(firm: str) -> dict[str, Any]:
    import A3_run as R

    os.nice(10)
    inputs = B.load_inputs()
    rg = int(round(float(B.e28_pair(firm, "QM")["mu_star_lim"]) * 100))
    out = {}
    for case in ("limit", "market"):
        spec = {"kind": "cell", "case": case, "form": "primary", "firm": firm, "basket": "B0", "rho": None,
                "setting": "ii", "mode": "bisection", "mu_star": None, "report_g_b0": rg}
        out[case] = B.run_cell(spec, R._STATE, inputs)
    return out


@pytest.fixture(scope="module")
def b0_cells() -> dict[str, dict[str, Any]]:
    import A3_run as R

    R.build_state(list(B.FIRMS))
    with mp.get_context("fork").Pool(len(B.FIRMS)) as pool:
        res = pool.map(_b0, B.FIRMS)
    return dict(zip(B.FIRMS, res, strict=True))


@pytest.mark.parametrize("firm", B.FIRMS)
def test_a_b0_reproduces_e28_qm(b0_cells: dict[str, dict[str, Any]], firm: str) -> None:
    e28 = B.e28_pair(firm, "QM")
    lim, mkt = b0_cells[firm]["limit"], b0_cells[firm]["market"]
    assert lim["threshold"]["value"] == e28["mu_star_lim"]
    assert lim["x10K"]["value"] == e28["mu10K"]
    assert mkt["threshold"]["value"] == e28["mu_star_mkt"]
    assert lim["cost_per_attempt_usd"] == e28["cost_per_attempt_usd"]
    stored = json.loads((PAIRS / f"{firm}__QM.json").read_text())["evaluations"]
    mine = {e["g"]: e for e in lim["evaluations"]}
    n_cmp = 0
    for s in stored:
        j = int(round(s["mu_lim"] * 100))
        if abs(s["mu_lim"] * 100 - j) > 1e-4 or j not in mine or mine[j]["p10k"] is None:
            continue
        for k in ("ev", "se", "ev_ex_api", "p10k"):
            assert mine[j][k] == s[k], (firm, j, k, mine[j][k], s[k])
        n_cmp += 1
    assert n_cmp >= 1
    k_lim = int(round(float(e28["mu_star_lim"]) * 100))
    assert k_lim in mine  # the threshold point itself is among the compared evaluations


def test_a_b0_law_equals_e28_daylaw() -> None:
    import A3_funnel as F

    inputs = B.load_inputs()
    for firm in B.FIRMS:
        mem = B.members_for(firm, ("QM",), inputs)
        for g in (0, 1, 32, 57, 133, 400):
            for market in (False, True):
                c = mem[0].cost(market)
                d = g * B.STEP - c
                ref = F.DayLaw(m=F.T_RT * d * mem[0].v, s=math.sqrt(F.T_RT) * mem[0].sigma * mem[0].v)
                got = B.combined_law(mem, [g * B.STEP], 0.0, market)
                assert (got.m, got.s) == (ref.m, ref.s)


def test_c_zero_trade_member_reduces_to_other_alone() -> None:
    inputs = B.load_inputs()
    for firm in B.FIRMS:
        alone = B.members_for(firm, ("QM",), inputs)
        for other in ("ZM", "MGC", "MNQ"):
            pair = B.members_for(firm, ("QM", other), inputs, (20, 0))
            for rho in B.RHOS:
                for mus in ([0.3, 0.0], [1.25, 2.0]):
                    for market in (False, True):
                        a = B.combined_law(alone, mus[:1], rho, market)
                        b = B.combined_law(pair, mus, rho, market)
                        assert (a.m, a.s) == (b.m, b.s)


def test_c_rho_limits_of_sd() -> None:
    inputs = B.load_inputs()
    mem = B.members_for("lucid", B.BASKETS["B3"], inputs)
    s = [m.s_usd for m in mem]
    assert B.combined_sd(mem, 0.0) == pytest.approx(math.sqrt(sum(x * x for x in s)), rel=1e-15)
    assert B.combined_sd(mem, 1.0) == pytest.approx(sum(s), rel=1e-12)


def test_d_trade_split_and_lots() -> None:
    assert B.trade_split(1) == (20,)
    assert B.trade_split(2) == (10, 10)
    assert B.trade_split(3) == (7, 7, 6)
    lots = {b: B.basket_lots(c) for b, c in B.BASKETS.items()}
    assert lots == {"B0": 1.0, "B1": 2.0, "B2": 1.1, "B3": 2.1, "B4": 1.1}
    mem = B.members_for("topstep", B.BASKETS["B3"], B.load_inputs())
    assert [(m.code, m.T) for m in mem] == [("QM", 7), ("ZM", 7), ("MGC", 6)]
    assert all(lots[b] <= min(B.FIRM_CAP_LOTS.values()) for b in lots)
    assert [b for b in lots if lots[b] > 2] == ["B3"]  # only B3 exceeds Topstep's 2-lot XFA tier


# ---------------------------------------------------------------- (b) and (e), written at 22:02 ----
XFA_FIELDS = ("payout_days", "payout_gross", "n_payouts", "total_gross", "first_payout_day", "end_day",
              "end_reason", "end_balance", "overflow")


def test_b_combined_law_against_correlated_member_days() -> None:
    """B3 at rho 0.5: members' cumulative P&L are Brownian motions with instantaneous correlation rho over the day
    (42 slots = lcm of the trade counts); each trade is the increment over its sub-interval, so trades are
    independent within a member with SD sigma_i; the day's sum of all trades has mean M and SD S."""
    import numpy as np

    inputs = B.load_inputs()
    mem = B.members_for("topstep", B.BASKETS["B3"], inputs)
    rho, mus = 0.5, [0.6, 1.1, 9.0]
    law = B.combined_law(mem, mus, rho, False)
    rng = np.random.default_rng(20261021)
    n, slots = 100_000, 42
    common = rng.standard_normal((n, slots)) / math.sqrt(slots)
    total = np.zeros(n)
    days = []
    for m, mu in zip(mem, mus, strict=True):
        inc = math.sqrt(rho) * common + math.sqrt(1 - rho) * rng.standard_normal((n, slots)) / math.sqrt(slots)
        trades = inc.reshape(n, m.T, slots // m.T).sum(axis=2) * math.sqrt(m.T) * m.sigma + (mu - m.c_lim)
        assert abs(trades.std() / m.sigma - 1) < 0.01  # each trade SD sigma_i
        day = trades.sum(axis=1) * m.v
        days.append(day)
        total += day
    assert abs(total.mean() - law.m) < 4 * law.s / math.sqrt(n)
    assert abs(total.std(ddof=1) - law.s) < 4 * law.s / math.sqrt(2 * n)
    assert abs(np.corrcoef(days[0], days[2])[0, 1] - rho) < 0.02


def test_e_b3_wrapper_reduces_to_primary_when_tier_not_reached() -> None:
    from dataclasses import replace

    import A3_funnel as F
    import A3_models as M
    import numpy as np
    from prop_econ.vec import simulate_xfas

    model = M.firm_models()["topstep"]
    rules, pol = model.xfa_rules, F.size1_policy(model.attempt_max_days)
    dr = F.make_draws("xfa", n=1000)
    pt = B.cell_point_fn("topstep", "B3", "i", 0.5, False, "b3_sens", {"QM": 0.32, "ZM": 0.59, "MGC": 9.0},
                         B.load_inputs())
    law_a, law_b = pt(150)
    sh_a, _ = F.shock_set(dr, law_a)
    sh_b, _ = F.shock_set(dr, law_b)
    ref = simulate_xfas(sh_a, rules, pol)

    def same(p: Any) -> bool:
        return all(np.array_equal(getattr(p, f), getattr(ref, f)) for f in XFA_FIELDS)

    got, low, alld = B.simulate_xfas_b3(sh_a, sh_b, rules, pol, 1.1)  # 1.1 lots fit every tier
    assert low == 0 and alld > 0 and same(got)
    no2 = replace(rules, xfa=replace(rules.xfa, scaling=((1500.0, 3), (2000.0, 3), (None, 5))))
    got, low, _ = B.simulate_xfas_b3(sh_a, sh_b, no2, pol, 2.1)  # the 2-lot tier removed
    assert low == 0 and same(got)
    got, low, _ = B.simulate_xfas_b3(sh_a, sh_a, rules, pol, 2.1)  # law B = law A: the primary form
    assert low > 0 and same(got)
    got, low, _ = B.simulate_xfas_b3(sh_a, sh_b, rules, pol, 2.1)  # the sensitivity proper changes the pool
    assert low > 0 and not same(got)
