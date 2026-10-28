"""Stage E.33 B5 (iii): the CV, uniqueness, deflated Sharpe, FDR and PBO code reproduces published worked examples.

Code under test: funnel/multiple_comparisons.py (expected_max_sharpe, deflated_sharpe_ratio,
probability_of_backtest_overfitting), screening/stage_e_verdict.py (moments, t_stat, dsr, dsr_table, pbo),
screening/stage_e_stats.py (holm_tier_a, the test's Holm), strategy/research/_d1f_decisions.py (holm,
benjamini_hochberg), and E.33's pipeline/search33.py (make_folds: folds and embargo) and pipeline/lab33.py
(uniqueness_weights), and pipeline/select33.py (bh_holm, reference_thresholds; added 2026-10-28 02:05 PDT).

Every published number below is quoted with its source file (saved pages; sha256 in
reports/stage_e33_briefs/pages/LOG.md and the E.28/E.32 page logs) and the digits matched. A worked example that
could not be obtained is not reconstructed (see StatsCostCoder_readings.md).

Run: uv run pytest -q reports/stage_e33_briefs/work/pipeline/tests/test_stats_repro33.py
"""
from __future__ import annotations

import math
import statistics
import sys
from datetime import date, timedelta
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np
import pytest

HERE = Path(__file__).resolve().parent
PIPE = HERE.parent
REPO = PIPE.parents[3]
for _p in (str(REPO), str(PIPE)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lab33  # noqa: E402
import search33  # noqa: E402

from funnel.multiple_comparisons import (  # noqa: E402
    deflated_sharpe_ratio,
    expected_max_sharpe,
    probability_of_backtest_overfitting,
)
from screening import stage_e_verdict as sev  # noqa: E402
from screening.stage_e_stats import holm_tier_a  # noqa: E402
from strategy.research import _d1f_decisions as d1f  # noqa: E402

PAGES_M5A = REPO / "reports" / "stage_e32_briefs" / "pages" / "M5a_validation"
PAGES_M3 = REPO / "reports" / "stage_e32_briefs" / "pages" / "M3_labels"
PAGES_AFML = REPO / "reports" / "stage_e28_briefs" / "pages" / "C2_AFML"


def _source_has(path: Path, *needles: str) -> None:
    """The quoted passage is in the saved source (whitespace-normalised)."""
    text = " ".join(path.read_text(encoding="utf-8", errors="replace").split())
    for n in needles:
        assert " ".join(n.split()) in text, (path.name, n)


def _matches(value: float, published: float, decimals: int) -> None:
    assert round(value, decimals) == pytest.approx(published, abs=1e-12), (value, published)
    assert abs(value - published) <= 0.5 * 10 ** -decimals + 1e-15


# ------------------------------------------------------------------------------------ deflated Sharpe --
# Bailey and Lopez de Prado (2014), "The Deflated Sharpe Ratio", JPM 40(5), section "A NUMERICAL EXAMPLE",
# pp. 9-10 of the author copy (PAGES_M5A/bailey_lopezdeprado_2014_dsr.pdf). The inputs are equation glyphs that
# pdftotext drops; they were read from the rendered pages (reports/stage_e33_briefs/pages/StatsCost/
# dsr2014_p9_numerical_example_inputs.png, ..._p10_...outputs.png) and appear as text in the author's slides
# (Lopez de Prado 2017, "The 7 Reasons Most Machine Learning Funds Fail", SSRN 3031282, slides 41-42,
# PAGES_AFML/lopezdeprado_2017_7reasons_slides.txt lines 1311-1355): "An analyst uncovers a daily strategy with
# annualized SR=2.5, after running N=100 independent trials, where V[SR_n] = 1/2, T=1250, gamma3 = -3 and
# gamma4 = 10." Published: SR0 ~ 0.1132 (non-annualized, 250 observations a year), DSR ~ 0.9004; N=46 gives
# 0.9505; normal returns (gamma3 = 0, gamma4 = 3) give 0.9505 after N=88.
SR_DAILY = 2.5 / math.sqrt(250)  # the paper's 2.5 / sqrt(250)
V_DAILY = 0.5 / 250  # V = 1/2 annualised; the paper's sqrt(1 / (2 * 250))
T_OBS = 1250  # the formula uses sqrt(T - 1) = sqrt(1249)


def test_dsr_example_sources_quoted():
    _source_has(PAGES_M5A / "bailey_lopezdeprado_2014_dsr.pdf.txt", "A NUMERICAL EXAMPLE",
                "would have been 0.9505, above the 95% confidence level",
                "there is only a 90% chance that the true SR")
    _source_has(PAGES_AFML / "lopezdeprado_2017_7reasons_slides.txt",
                "annualized SR=2.5, after", "running N=100 independent trials", "T=1250",
                "𝛾3 = −3 and 𝛾4 = 10", "0.1132", "= 0.9004.", "𝐷𝑆𝑅 ≈ 0.9505", "𝐷𝑆𝑅 = 0.9505 after N=88")


def test_dsr_example_threshold_sr0_0_1132():
    _matches(expected_max_sharpe(100, V_DAILY), 0.1132, 4)


def test_dsr_example_0_9004_at_n100():
    out = deflated_sharpe_ratio(SR_DAILY, T_OBS, 100, V_DAILY, skewness=-3.0, kurtosis=10.0)
    _matches(out["deflated_sharpe_ratio"], 0.9004, 4)
    _matches(out["expected_max_sharpe_under_null"], 0.1132, 4)
    assert out["deflated_sharpe_ratio"] < 0.95  # "not a legitimate empirical discovery at a 95% confidence level"


def test_dsr_example_0_9505_at_n46_and_normal_n88():
    _matches(deflated_sharpe_ratio(SR_DAILY, T_OBS, 46, V_DAILY, -3.0, 10.0)["deflated_sharpe_ratio"], 0.9505, 4)
    _matches(deflated_sharpe_ratio(SR_DAILY, T_OBS, 88, V_DAILY, 0.0, 3.0)["deflated_sharpe_ratio"], 0.9505, 4)


def test_stage_e_verdict_dsr_and_dsr_table_reproduce_0_9004():
    mom = {"n": T_OBS, "mean": SR_DAILY, "sd": 1.0, "skew": -3.0, "kurtosis": 10.0, "sharpe": SR_DAILY}
    value, note = sev.dsr(mom, 100, V_DAILY)
    assert note is None
    _matches(value, 0.9004, 4)
    # dsr_table takes V as the population variance of the listed Sharpes: +-sqrt(V) has pvariance V exactly
    sd = math.sqrt(V_DAILY)
    moms = {"x": mom, "a": {**mom, "sharpe": sd}, "b": {**mom, "sharpe": -sd}}
    tab = sev.dsr_table(moms, ["a", "b"], 100, ["x"])
    assert tab["sharpe_variance"] == pytest.approx(V_DAILY, rel=1e-12)
    _matches(tab["dsr"]["x"], 0.9004, 4)
    _matches(tab["expected_max_daily_sharpe_under_null"], 0.1132, 4)


# ---------------------------------------------------------------------------------- moments and t --
# No published worked example covers moments() and t_stat() in the four sources; they are checked against
# Harvey and Liu (2015) eq. (1)-(2) (PAGES_M5A/harvey_liu_2015_backtesting.pdf.txt: t = mu / (sigma / sqrt(T)),
# "SR ... is simply t-ratio / sqrt(T)") on a hand-computed series.
def test_moments_and_t_stat_hand_computed():
    mom = sev.moments([1.0, 2.0, 3.0, 4.0])
    assert mom["mean"] == 2.5 and mom["sd"] == pytest.approx(math.sqrt(1.25))
    assert mom["skew"] == pytest.approx(0.0, abs=1e-15) and mom["kurtosis"] == pytest.approx(1.64)
    assert mom["sharpe"] == pytest.approx(2.5 / math.sqrt(1.25))
    assert sev.t_stat(mom) == pytest.approx(mom["sharpe"] * math.sqrt(4))


# --------------------------------------------------------------------------- Benjamini-Hochberg (1995) --
# Benjamini and Hochberg (1995), JRSS B 57(1), section 3.2, p. 295 (PAGES_M5A/benjamini_hochberg_1995.pdf.txt
# lines 298-317): "The ordered p-values for the 15 comparisons made are 0.0001, 0.0004, 0.0019, 0.0095, 0.0201,
# 0.0278, 0.0298, 0.0344, 0.0459, 0.3240, 0.4262, 0.5719, 0.6528, 0.7590, 1.000. Controlling the FWER at 0.05,
# the Bonferroni approach, using 0.05/15 = 0.0033, rejects the three hypotheses corresponding to the smallest
# p-values ... Using Hochberg's procedure leaves us with the same three hypotheses rejected ... The first p-value
# to satisfy the constraint is p(4) as P(4) = 0.0095 < 4/15 0.05 = 0.013. Thus we reject the four hypotheses".
BH_P = (0.0001, 0.0004, 0.0019, 0.0095, 0.0201, 0.0278, 0.0298, 0.0344, 0.0459, 0.3240, 0.4262, 0.5719, 0.6528,
        0.7590, 1.000)
BH_KEYS = {f"h{i:02d}": p for i, p in enumerate(BH_P, 1)}


def test_bh_example_source_quoted():
    _source_has(PAGES_M5A / "benjamini_hochberg_1995.pdf.txt",
                "0.0001, 0.0004, 0.0019, 0.0095, 0.0201, 0.0278, 0.0298, 0.0344,",
                "0.0459, 0.3240, 0.4262, 0.5719, 0.6528, 0.7590, 1.000.", "using 0.05/15 = 0.0033",
                "Using Hochberg's procedure leaves us with the same three hypotheses rejected",
                "Thus we reject the four hypotheses")


def test_bh_step_up_rejects_four_at_q_0_05():
    out = d1f.benjamini_hochberg(BH_KEYS, q=0.05)
    rejected = sorted(k for k, v in out.items() if v["reject"])
    assert rejected == ["h01", "h02", "h03", "h04"]
    _matches(out["h04"]["threshold"], 0.013, 3)  # "4/15 0.05 = 0.013"
    assert BH_KEYS["h04"] <= out["h04"]["threshold"]


def test_bonferroni_threshold_and_holm_reject_three():
    res = holm_tier_a(BH_KEYS, 1)  # K = 1: family-wise 0.05, the test's Holm (P7.2)
    _matches(res.rows[0].threshold, 0.0033, 4)  # Holm's first step is Bonferroni's 0.05/15
    assert sum(p <= 0.05 / 15 for p in BH_P) == 3  # Bonferroni: three rejections
    # Holm is never weaker than Bonferroni and never stronger than Hochberg; the paper gives 3 for both, so
    # Holm must reject exactly 3 (implied by the published counts, not printed in the paper)
    assert res.rejected == ("h01", "h02", "h03")
    assert sorted(k for k, v in d1f.holm(BH_KEYS, alpha=0.05).items() if v["reject"]) == ["h01", "h02", "h03"]


def test_select33_bh_holm_helpers():
    """select33.bh_holm (ProofCoder's; select33.py sha256 1a7207f8... when written) on the paper's 15 p-values.
    It takes daily t values and uses p = 1 - Phi(t) (READING Q7), so each p enters as t = Phi^-1(1 - p); the
    paper's p = 1.000 enters as t = None (select33 gives such a configuration p = 1)."""
    import select33  # noqa: PLC0415  (imported here so the other reproductions run if select33 breaks)

    norm = statistics.NormalDist()
    results = [{"config": k, "t": (None if p >= 1.0 else norm.inv_cdf(1.0 - p))} for k, p in BH_KEYS.items()]
    out = select33.bh_holm(results, q=0.05)
    assert out["m"] == 15
    for k, p in BH_KEYS.items():
        assert out["p_values"][k] == pytest.approx(p, rel=1e-9, abs=1e-15)
    assert out["bh_rejected"] == ["h01", "h02", "h03", "h04"]  # "we reject the four hypotheses"
    assert out["holm_rejected"] == ["h01", "h02", "h03"]  # implied by Bonferroni = Hochberg = 3 (see above)
    ref = select33.reference_thresholds(15, 838)
    _matches(1.0 - norm.cdf(ref["bonferroni_holm_step1_m"]), 0.0033, 4)  # "0.05/15 = 0.0033"
    assert sum(BH_KEYS[k] <= 1.0 - norm.cdf(ref["bonferroni_holm_step1_m"]) + 1e-15 for k in BH_KEYS) == 3


# ------------------------------------------------------------------------------------------ PBO, CSCV --
# Bailey, Borwein, Lopez de Prado and Zhu (2017), "The Probability of Backtest Overfitting", J. Comp. Finance
# (author copy PAGES_M5A/bailey_borwein_ldp_zhu_2017_pbo.pdf; text in ...pdf.txt). Worked numbers:
# - section 2.1, p. 9: "if N = 3 and the performance measure is the Sharpe ratio, for a particular sample c,
#   R^c = (0.5, 1.1, 0.7) and Rbar^c = (0.6, 0.7, 1.3), then we have r^c = (1, 3, 2) and rbar^c = (1, 2, 3)";
# - Algorithm 2.3 f)-g): omega_bar = rbar_n* / (N + 1), lambda = ln(omega_bar / (1 - omega_bar)); section 3.1:
#   PBO phi = integral of f(lambda) from -infinity to 0;
# - Eq. (2.3) and Figure 1: "S = 4 ... the six combinations"; section 4: "S = 12 partitions, which will give us
#   924 logits", "S = 24 ... 2, 704, 156 logits", and "S = 16 we will obtain 12, 780 logits ... sigma[f(lambda)] <
#   0.0045" (p. 11 and p. 22 print 12,780; Eq. (2.3) gives C(16, 8) = 12,870: a misprint in the paper).
PBO_TXT = PAGES_M5A / "bailey_borwein_ldp_zhu_2017_pbo.pdf.txt"


def test_pbo_sources_quoted():
    _source_has(PBO_TXT, "R = (0.6, 0.7, 1.3), then we have rc = (1, 3, 2) and r̄c = (1, 2, 3)",
                "Rc = (0.5, 1.1, 0.7)", "S = 12 partitions, which will give us", "924 logits",
                "2, 704, 156 logits", "S = 16 we will obtain 12, 780", "It shows the six combi-")


def _ranks_ascending(values) -> tuple[int, ...]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0] * len(values)
    for r, i in enumerate(order, 1):
        ranks[i] = r
    return tuple(ranks)


def test_pbo_n3_rank_example():
    r_is, r_oos = (0.5, 1.1, 0.7), (0.6, 0.7, 1.3)
    assert _ranks_ascending(r_is) == (1, 3, 2) and _ranks_ascending(r_oos) == (1, 2, 3)  # the published ranks
    n_star = max(range(3), key=lambda i: r_is[i])
    omega_paper = _ranks_ascending(r_oos)[n_star] / (3 + 1)
    assert omega_paper == 0.5  # lambda = 0: the IS winner sits at the OOS median
    # program: two blocks, block 0 = this IS sample and block 1 = this OOS sample
    res = probability_of_backtest_overfitting([[a, b] for a, b in zip(r_is, r_oos, strict=True)], n_blocks=2)
    assert res.n_splits == 2 and res.logits[0] == pytest.approx(0.0, abs=1e-12)
    # the program counts lambda <= 0 as overfit; Definition 2.2 (rbar < N/2 = 1.5) would not count rank 2:
    # the program is the conservative side of the paper's own ambiguity at the median (READING R3)
    assert res.pbo == 1.0


@pytest.mark.parametrize(("n_blocks", "published"), [(4, 6), (12, 924)])
def test_pbo_split_counts_match_published(n_blocks, published):
    perf = [[float(b == s) for b in range(n_blocks)] for s in range(2)]
    assert probability_of_backtest_overfitting(perf, n_blocks).n_splits == published


def _eq_2_3(s: int) -> Fraction:
    """Eq. (2.3): prod_{i=0}^{S/2-1} (S - i) / (S/2 - i)."""
    return math.prod((Fraction(s - i, s // 2 - i) for i in range(s // 2)), start=Fraction(1))


def test_pbo_split_count_s16_paper_misprint_and_eq_2_3():
    perf = [[float(b % 3 == s) for b in range(16)] for s in range(2)]
    n = probability_of_backtest_overfitting(perf, 16).n_splits
    assert n == _eq_2_3(16) == math.comb(16, 8) == 12_870
    assert n != 12_780  # the paper's printed figure: not reproduced (misprint)
    assert math.sqrt(1 / (4 * 12_780)) < 0.0045 and math.sqrt(1 / (4 * n)) < 0.0045  # "sigma[f(lambda)] < 0.0045"


def test_pbo_split_count_eq_2_3_reproduces_s12_s24_figures():
    # the program enumerates itertools.combinations(range(S), S/2): C(S, S/2) splits (run above for S = 4, 12,
    # 16); S = 24 (2.7 million splits) is checked on Eq. (2.3) alone, not by running the program
    assert _eq_2_3(4) == 6 and _eq_2_3(12) == 924 and _eq_2_3(24) == 2_704_156


def _pbo_paper(perf, n_blocks):
    """Algorithm 2.3 literally on block sums (the program's performance measure): omega_bar = rbar / (N + 1)."""
    n = len(perf)
    lams = []
    for train in combinations(range(n_blocks), n_blocks // 2):
        test = [b for b in range(n_blocks) if b not in train]
        r_is = [sum(row[b] for b in train) for row in perf]
        r_oos = [sum(row[b] for b in test) for row in perf]
        star = max(range(n), key=lambda i: r_is[i])
        w = _ranks_ascending(r_oos)[star] / (n + 1)
        lams.append(math.log(w / (1 - w)))
    return sum(lam <= 0 for lam in lams) / len(lams), lams


@pytest.mark.parametrize(("n_strat", "seed"), [(3, 1), (4, 2), (10, 3), (25, 4)])
def test_pbo_program_equals_paper_algorithm_without_ties(n_strat, seed):
    rng = np.random.default_rng(seed)
    perf = rng.normal(size=(n_strat, 8)).tolist()
    prog = probability_of_backtest_overfitting(perf, 8)
    paper, lams = _pbo_paper(perf, 8)
    assert prog.pbo == paper
    # the program's omega = (worse + 0.5) / N and the paper's rbar / (N + 1) share the sign of the logit
    assert [np.sign(round(a, 12)) for a in prog.logits] == [np.sign(round(b, 12)) for b in lams]


def test_stage_e_verdict_pbo_uses_8_contiguous_blocks():
    rng = np.random.default_rng(7)
    series = {k: rng.normal(size=796) for k in ("a", "b", "c")}
    out = sev.pbo(series)
    width = 796 // 8
    blocks = [[float(np.sum(series[k][b * width:(b + 1) * width])) for b in range(8)] for k in series]
    assert out["n_splits"] == 70 and out["block_days"] == 99
    assert out["pbo"] == pytest.approx(_pbo_paper(blocks, 8)[0], abs=1e-12)


# ----------------------------------------------------------------------- AFML ch. 4: average uniqueness --
# Lopez de Prado, AFML (2018) ch. 4: the book was not obtained (a paid text). Definition from the author's slides
# (PAGES_AFML/lopezdeprado_2017_7reasons_slides.txt lines 1127-1141: c_t = sum_i 1_{t,i}; u_{t,i} = 1_{t,i} /
# c_t; "The average uniqueness of label i is the average u_{t,i} over the label's lifespan"). The book's toy
# example from a secondary source, the mlfinpy documentation (PAGES_M3/mlfinpy_Sampling.rst.txt lines 97-230,
# "An example of Sequential Bootstrap using a a toy example from the book"): labels y0 on r_{0,2} (rows 0-2),
# y1 on r_{2,3} (rows 2-3), y2 on r_{4,5} (rows 4-5); sequential-bootstrap probabilities after phi = [1]:
# 0.35714285714285715, 0.21428571428571427, 0.42857142857142855; after phi = [1, 2]: 0.45454545454545453,
# 0.2727272727272727, 0.2727272727272727; after phi = [1, 2, 0]: 0.32653061224489793, 0.3061224489795918,
# 0.36734693877551017. Each probability is the appended label's average uniqueness over the sum.
MIN = lab33.MIN_NS
TOY_ROWS = ((0, 3), (2, 4), (4, 6))  # [first row, last row + 1] of each label, one row = one minute
TOY_PUBLISHED = {
    (1,): (0.35714285714285715, 0.21428571428571427, 0.42857142857142855),
    (1, 2): (0.45454545454545453, 0.2727272727272727, 0.2727272727272727),
    (1, 2, 0): (0.32653061224489793, 0.3061224489795918, 0.36734693877551017),
}


def test_afml_toy_sources_quoted():
    _source_has(PAGES_M3 / "mlfinpy_Sampling.rst.txt", "toy example from the book",
                "ind_mat.loc[:, 0] = [1, 1, 1, 0, 0, 0]", "ind_mat.loc[:, 1] = [0, 0, 1, 1, 0, 0]",
                "ind_mat.loc[:, 2] = [0, 0, 0, 0, 1, 1]",
                ">> array([0.35714285714285715, 0.21428571428571427, 0.42857142857142855],",
                ">> array([0.45454545454545453, 0.2727272727272727, 0.2727272727272727],",
                ">> array([0.32653061224489793, 0.3061224489795918, 0.36734693877551017],")
    _source_has(PAGES_AFML / "lopezdeprado_2017_7reasons_slides.txt",
                "The average uniqueness of label i is the average 𝑢𝑡,𝑖 over the label’s")


def _uniq(labels) -> np.ndarray:
    starts = [TOY_ROWS[i][0] * MIN for i in labels]
    ends = [TOY_ROWS[i][1] * MIN for i in labels]
    return lab33.uniqueness_weights(starts, ends)


def test_afml_toy_average_uniqueness_with_lab33_weights():
    assert lab33.interval_set(0, 3 * MIN) == [0, 1, 2]  # a span ending on a minute mark meets 3 intervals
    np.testing.assert_allclose(_uniq((0, 1, 2)), [5 / 6, 3 / 4, 1.0], rtol=0, atol=1e-15)


@pytest.mark.parametrize("phi", sorted(TOY_PUBLISHED))
def test_afml_toy_sequential_bootstrap_probabilities(phi):
    u = np.array([_uniq((*phi, i))[-1] for i in range(3)])
    prob = u / u.sum()
    np.testing.assert_allclose(prob, TOY_PUBLISHED[phi], rtol=0, atol=2e-16)


# -------------------------------------------------------------- AFML ch. 7: purged and embargoed K-fold --
# AFML ch. 7 itself was not obtained. The construction is the author's restatement (Lopez de Prado 2018, "The 10
# Reasons Most Machine Learning Funds Fail", JPM, Solution #8; PAGES_M5A/lopezdeprado_2018_10reasons_jpm.pdf.txt
# lines 505-523; the same text in the 2017 slides 34-35): a training label i overlaps a test label j if
# (1) t_j0 <= t_i0 <= t_j1, (2) t_j0 <= t_i1 <= t_j1 or (3) t_i0 <= t_j0 <= t_j1 <= t_i1; the embargo removes
# training labels with t_j1 <= t_i0 <= t_j1 + h by setting Y_j = f[[t_j0, t_j1 + h]] before purging; "A small
# value h ~ .01T ... often suffices". No numeric worked example exists in these sources: the test reproduces the
# construction on E.33's design (P6.1: K = 6 blocks 133 x 4, 132 x 2; h = 21 trade dates) and checks search33.
def test_purge_embargo_source_quoted():
    _source_has(PAGES_M5A / "lopezdeprado_2018_10reasons_jpm.pdf.txt", "SOLUTION #8: PURGING AND EMBARGOING",
                "suffices to prevent all leakage", "before purging")


def _afml_train(n_dates: int, test: range, h: float) -> list[int]:
    """Date-level labels: date d's labels lie inside [d + 0.35, d + 0.55] (08:35-13:13 of a day; P3.6 rules
    1-2), so a label never crosses its date. Purge with every test label extended by h, three conditions."""
    span = {d: (d + 0.35, d + 0.55) for d in range(n_dates)}
    ext = [(span[j][0], span[j][1] + h) for j in test]
    keep = []
    for i in range(n_dates):
        if i in test:
            continue
        ti0, ti1 = span[i]
        if any(j0 <= ti0 <= j1 or j0 <= ti1 <= j1 or (ti0 <= j0 and j1 <= ti1) for j0, j1 in ext):
            continue
        keep.append(i)
    return keep


def test_search33_folds_equal_afml_purge_and_embargo_construction():
    dates = [(date(2021, 1, 1) + timedelta(days=k)).isoformat() for k in range(796)]
    folds = search33.make_folds(dates)
    assert [len(f.eval_dates) for f in folds] == [133, 133, 133, 133, 132, 132]
    assert [len(f.train_dates) for f in folds] == [642, 642, 642, 642, 643, 664]
    start = 0
    for f in folds:
        test = range(start, start + len(f.eval_dates))
        assert f.eval_dates == tuple(dates[d] for d in test)
        assert list(f.train_dates) == [dates[d] for d in _afml_train(796, test, h=search33.EMBARGO)]
        # no purge is needed (labels end inside their own date) and nothing before the block is removed
        assert _afml_train(796, test, h=0.0) == [d for d in range(796) if d not in test]
        start += len(f.eval_dates)
    assert math.ceil(0.01 * 796) <= search33.EMBARGO  # h = 21 dates >= AFML's h ~ 0.01 T (8 dates)


def test_statistics_module_population_conventions():
    """P0.3: daily statistics use the population SD (moments) and dsr_table the population variance."""
    xs = [0.3, -0.1, 0.4, 0.0]
    assert sev.moments(xs)["sd"] == pytest.approx(statistics.pstdev(xs))
