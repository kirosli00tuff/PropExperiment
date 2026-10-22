"""A3 tests: the extensions equal E.19's simulator where they overlap, the per-trade layer matches the spec, and
the wallet / cycle / campaign wrappers equal E.19's conventions. No market data: E.19's normal source with the
published sigma_full values.

Run: PYTHONPATH=.:reports/stage_e28_briefs/work/A3_econ uv run pytest -q -p no:cacheprovider \
     reports/stage_e28_briefs/work/A3_econ/test_A3_econ.py
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

import prop_econ.grid as grid
from prop_econ.assemble import assemble_cycle, fee_terms
from prop_econ.funnel import Policy
from prop_econ.returns import ROOTS, bridge_min, draw_layout, normal_shocks, product_specs
from prop_econ.rules import size_rules
from prop_econ.types import ProductSpec, ShockSet
from prop_econ.vec import simulate_attempts, simulate_xfas

import A3_funnel as F
import A3_models as M

REPO = Path(__file__).resolve().parents[4]
SUMMARY = REPO / "reports" / "stage_e19_returns_summary.json"
RULES_E19 = REPO / "reports" / "stage_e26_briefs" / "stage_e19_rules.before_e26.json"
XFA_FIELDS = ("payout_days", "payout_gross", "n_payouts", "total_gross", "first_payout_day", "end_day",
              "end_reason", "end_balance", "overflow")


def _sigma() -> dict[str, float]:
    return {p["root"]: float(p["sigma_full_usd"]) for p in json.loads(SUMMARY.read_text())["paths"]}


def e19_normal(n: int, seed: int, days: int = F.HORIZON) -> ShockSet:
    specs = product_specs(_sigma(), "d8")
    return normal_shocks(specs, draw_layout(n, days, seed), seed)


def e19_policy(path: str = "standard", dll: bool = False, f: float = 0.25) -> Policy:
    return Policy(f=f, mode="continuous", edge="zero", k=1, dll_chosen=dll, payout_path=path,
                  attempt_max_days=F.HORIZON, xfa_max_days=F.HORIZON, max_payouts=F.MAX_PAYOUTS)


@pytest.fixture(scope="module")
def ts_rules():
    return M.topstep_rules()[0]


@pytest.mark.parametrize("path,dll", [("standard", False), ("consistency", False), ("standard", True)])
def test_funded_extension_equals_prop_econ_xfa(ts_rules, path, dll):
    shocks = e19_normal(3000, 7)
    pol = e19_policy(path, dll)
    ref = simulate_xfas(shocks, ts_rules, pol)
    got = F.simulate_funded(shocks, None, F.funded_from_topstep(ts_rules, path, dll), pol)
    for name in XFA_FIELDS:
        assert np.array_equal(getattr(ref, name), getattr(got, name)), name
    assert ref.n_payouts.sum() > 0


def test_intraday_code_paths_reduce_to_eod(ts_rules):
    """With the bridge maximum pushed to -inf the intraday floor never trails a high: both intraday code paths
    must then equal E.19's EOD simulators path for path."""
    shocks = e19_normal(3000, 11)
    low = np.full(shocks.z.shape, -1e12)
    lucid = M.firm_models()["lucid"]
    pol = e19_policy()
    ref_a = simulate_attempts(shocks, lucid.eval_rules, pol)
    got_a = F.simulate_attempts_intraday(shocks, low, lucid.eval_rules, pol, lucid.eval_dll_usd)
    for name in ("passed", "length", "reason"):
        assert np.array_equal(getattr(ref_a, name), getattr(got_a, name)), name
    fr = F.funded_from_topstep(ts_rules)
    ref_x = F.simulate_funded(shocks, None, fr, pol)
    got_x = F.simulate_funded(shocks, low, replace(fr, trail="intraday"), pol)
    for name in XFA_FIELDS:
        assert np.array_equal(getattr(ref_x, name), getattr(got_x, name)), name


def _one_path(closes: list[float], lows: list[float], highs: list[float], s: float = 100.0):
    z = np.array([closes]) / s
    w = np.array([lows]) / s
    h = np.array([highs]) / s
    spec = ProductSpec("x", s, 0.0, None, None, None)
    return ShockSet(z, w, np.zeros(z.shape, dtype=np.int16), (spec,)), h


def test_intraday_trailing_hand_case():
    """Bulenox-style evaluation: MLL 2,500 trailing the intraday high, lock +100, target 3,000.
    Day 1: high +1,500, close +1,000 -> floor -1,000 (EOD trailing would give -1,500).
    Day 2: high 0 above the open, low -1,900 (equity -900): floor -1,000 holds, no breach; close at 0.
    Day 3: low -1,000 reaches the floor -1,000 -> breach on day 3. The same path under EOD trailing survives
    day 3 (floor -1,500) and passes on day 4."""
    model = M.firm_models()["bulenox"]
    pol = F.size1_policy(21)
    sh, h = _one_path([1000.0, -1000.0, 500.0, 0.0] + [0.0] * 17,
                      [-100.0, -1900.0, -1000.0, 0.0] + [0.0] * 17,
                      [1500.0, 0.0, 600.0, 0.0] + [0.0] * 17)
    pool = F.simulate_attempts_intraday(sh, h, model.eval_rules, pol, None)
    assert not pool.passed[0] and pool.length[0] == 3 and pool.reason[0] == F.ATTEMPT_BREACH
    sh2, _ = _one_path([1000.0, -1000.0, 500.0, 2500.0] + [0.0] * 17,
                       [-100.0, -1900.0, -1000.0, 0.0] + [0.0] * 17,
                       [1500.0, 0.0, 600.0, 2500.0] + [0.0] * 17)
    eod = simulate_attempts(sh2, model.eval_rules, pol)
    assert eod.passed[0] and eod.length[0] == 4


def test_bridge_formulas_match_e19():
    g = np.random.default_rng(3)
    x = g.standard_normal(10000) * 2
    u = 1.0 - g.random(10000)
    e = -np.log(u)
    assert np.allclose(F.bridge_min_e(x, e), bridge_min(x, u), atol=1e-12)
    hmax = F.bridge_max_e(x, e)
    assert np.allclose(hmax, -bridge_min(-x, u), atol=1e-12)
    assert np.all(hmax >= np.maximum(x, 0)) and np.all(F.bridge_min_e(x, e) <= np.minimum(x, 0))


@pytest.mark.parametrize("mu,c,sig,v", [(0.0, 2.44, 27.83, 0.5), (1.3, 0.756, 27.83, 5.0),
                                        (2.0, 0.402, 6.30, 10.0)])
def test_per_trade_layer_daily_moments(mu, c, sig, v):
    """Daily P&L of the model = T (mu - c) v mean, sqrt(T) sigma_T v SD (spec), and equals in law the sum of
    T = 20 independent normal trades."""
    law = F.DayLaw.from_trades(mu, c, sig, v)
    assert math.isclose(law.m, 20 * (mu - c) * v) and math.isclose(law.s, math.sqrt(20) * sig * v)
    dr = F.make_draws("test", n=4000, days=50, with_max=True)
    sh, h = F.shock_set(dr, law)
    pnl = sh.products[0].sigma_full_usd * sh.z
    n = pnl.size
    assert abs(pnl.mean() - law.m) < 4 * law.s / math.sqrt(n)
    assert abs(pnl.std() / law.s - 1) < 4 / math.sqrt(2 * n)
    assert np.all(sh.w <= np.minimum(sh.z, 0)) and np.all(h >= np.maximum(sh.z, 0))
    trades = np.random.default_rng(5).normal(mu - c, sig, size=(n, 20)).sum(axis=1) * v
    assert abs(trades.mean() - law.m) < 4 * law.s / math.sqrt(n)
    assert abs(trades.std() / law.s - 1) < 4 / math.sqrt(2 * n)


def test_size_one_through_e19_day_step(ts_rules):
    """f = 1e-12 makes E.19's sizing trade exactly one contract: the pool equals a hand evaluation."""
    law = F.DayLaw(m=-50.0, s=300.0)
    dr = F.make_draws("test1", n=200, days=F.HORIZON)
    sh, _ = F.shock_set(dr, law)
    pool = simulate_attempts(sh, ts_rules, F.size1_policy())
    # scalar replay with P&L = s z (no sizing): breach when cumulative worst crosses the trailing floor
    for i in range(50):
        bal, flo, best = 0.0, -2000.0, -math.inf
        for d in range(F.HORIZON):
            close, worst = 300.0 * sh.z[i, d], 300.0 * sh.w[i, d]
            if worst <= -(bal - flo):
                assert pool.length[i] == d + 1 and not pool.passed[i]
                break
            bal += close
            best = max(best, close)
            flo = max(flo, min(bal - 2000.0, 0.0))
            if d + 1 >= 2 and bal >= 3000.0 and best < 0.55 * bal:
                assert pool.length[i] == d + 1 and pool.passed[i]
                break
        else:
            assert pool.length[i] == F.HORIZON and not pool.passed[i]


def test_cycle_wrapper_reproduces_e19_normal_twin(ts_rules):
    """E.19's normal-tail twin of the -250 headline job: E.19 shock seeds and index draws, prop_econ pools at
    f = 0.25, then this module's cycle_stats (assembly + API wallet) must give E.19's stored net exactly."""
    book = grid.headline_book(RULES_E19)
    rules = size_rules(book, "50K")
    settings, sc = grid.Settings(), grid.ShockConfig(tail="normal")
    sig = _sigma()
    specs = product_specs(sig, "d8")
    sh_a = normal_shocks(specs, draw_layout(20000, 756, grid.shock_seed(settings, "attempt", "50K", sc)),
                         grid.shock_seed(settings, "attempt", "50K", sc))
    sh_x = normal_shocks(specs, draw_layout(20000, 756, grid.shock_seed(settings, "xfa", "50K", sc)),
                         grid.shock_seed(settings, "xfa", "50K", sc))
    pol = e19_policy()
    pools = F.Pools(simulate_attempts(sh_a, rules, pol), simulate_xfas(sh_x, rules, pol))
    terms = fee_terms(rules, pricing_path="standard", dll_chosen=False, b2f_on=False, attempt_cap=60)
    rng = np.random.Generator(np.random.PCG64(grid.draw_seed(settings, "cycle", "50K", sc)))
    att, xfa = grid.draw_indices(rng, settings.n_cycles, grid._N(20000), grid._N(20000), terms)
    model = replace(M.firm_models()["topstep"], terms=terms)
    st = F.cycle_stats(model, pools, att, xfa)
    stored = json.loads((REPO / "reports" / "stage_e19_runs" /
                         "normal-random-all-d8-continuous__50K__zero_k1__f0.25__dll0__base.json").read_text())
    rec = next(r for r in stored["records"] if r["path"] == "standard" and r["pricing"] == "standard")
    assert st.ev == pytest.approx(rec["net"]["mean"], abs=1e-9)
    assert st.ev_ex_api == pytest.approx(rec["net_ex_api"]["mean"], abs=1e-9)


def test_campaign_matches_scalar_reference():
    """The vectorized 250-day campaign equals a plain loop over the same cycles (E.19's scalar assembly)."""
    model = M.firm_models()["bulenox"]
    law = F.DayLaw.from_trades(3.0, 1.22 / 5.0, 27.83, 5.0)
    da = F.make_draws("tca", n=2000, days=F.HORIZON, with_max=True)
    dx = F.make_draws("tcx", n=2000, days=F.HORIZON, with_max=True)
    pools = F.simulate_pools(model, law, da, dx)
    n_reps = F.CAMPAIGN_CHUNK + 200  # two replication blocks
    p = F.campaign_p_reach(model, pools, n_reps=n_reps)
    hits = 0
    t = model.terms
    for r in range(n_reps):
        block, local = divmod(r, F.CAMPAIGN_CHUNK)
        n_block = min(F.CAMPAIGN_CHUNK, n_reps - block * F.CAMPAIGN_CHUNK)
        clock, events, rnd = 0, [], 0
        while clock <= F.CAMPAIGN_DAYS:
            att, xfa = F.campaign_indices(block, rnd, n_block, pools.attempts.n, pools.xfas.n)
            for k in range(F.CAMPAIGN_ROUND):
                cyc = assemble_cycle(att[local, k], xfa[local, k, :1], pools.attempts, pools.xfas, t)
                events += [(clock + tt, 0, -usd) for tt, usd, _ in cyc.fees]
                events += [(clock + tt, 1, usd) for tt, usd in cyc.cash]
                clock += cyc.end
            rnd += 1
        events.sort(key=lambda e: (e[0], e[1]))
        run = 0.0
        for tt, is_cash, amt in events:
            if tt > F.CAMPAIGN_DAYS:
                break
            run += amt
            if is_cash and run - model.api_monthly_usd * (tt // model.api_period_days + 1) >= 10000:
                hits += 1
                break
    assert p == pytest.approx(hits / n_reps, abs=1e-12)
    assert 0 < hits < n_reps


def test_chunked_pools_equal_one_call():
    model = M.firm_models()["bulenox"]
    law = F.DayLaw.from_trades(2.0, 0.84, 27.83, 5.0)
    da = F.make_draws("tch_a", n=1500, days=F.HORIZON, with_max=True)
    dx = F.make_draws("tch_x", n=1500, days=F.HORIZON, with_max=True)
    p1 = F.simulate_pools(model, law, da, dx, chunk=1500)
    p2 = F.simulate_pools(model, law, da, dx, chunk=400)
    for name in ("passed", "length", "reason"):
        assert np.array_equal(getattr(p1.attempts, name), getattr(p2.attempts, name))
    for name in XFA_FIELDS:
        assert np.array_equal(getattr(p1.xfas, name), getattr(p2.xfas, name))
    assert np.array_equal(F.make_draws("tch_a", n=50, days=20, with_max=True).e2, F.make_e2("tch_a", 50, 20))


def test_mapping_covers_every_firm():
    assert set(M.MAPPING) == set(M.firm_models())
    for rows in M.MAPPING.values():
        assert all(kind in ("exact", "conservative", "ignored", "policy") for *_, kind in rows)
    assert ROOTS  # E.19 roots importable
