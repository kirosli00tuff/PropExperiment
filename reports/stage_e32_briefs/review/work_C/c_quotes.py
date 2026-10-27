"""MathReviewer C: whitespace- and ligature-tolerant quote check against saved evidence pages.
Usage: uv run python c_quotes.py  (pairs are listed below). Prints FOUND line / NOT FOUND only."""
from __future__ import annotations

import re
import sys
from pathlib import Path

PAGES = Path("/home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e32_briefs/pages")
NORM = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "ﬁ": "fi",
                      "ﬂ": "fl", "–": "-", "—": "-", "­": ""})


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.translate(NORM)).strip().lower()


def check(root: str, fname: str, quote: str) -> str:
    path = PAGES / root / fname
    if not path.exists():
        return f"NO FILE {root}/{fname}"
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    joined = norm(text)
    q = norm(quote)
    if q in joined:
        # locate the line of the first 40 chars
        head = norm(quote[:40])
        for i, ln in enumerate(lines, 1):
            if head[:25] in norm(ln):
                return f"FOUND l.{i} {root}/{fname} :: {quote[:60]}"
        return f"FOUND (multi-line) {root}/{fname} :: {quote[:60]}"
    return f"NOT FOUND {root}/{fname} :: {quote[:70]}"


PAIRS = [
    ("M5a_validation", "lopezdeprado_2018_10reasons_jpm.pdf.txt", "The embargo does not need to affect training observations prior to a test"),
    ("M5a_validation", "lopezdeprado_2018_10reasons_jpm.pdf.txt", "where T is the number of bars, often suffices to prevent all leakage"),
    ("M5a_validation", "lopezdeprado_2018_10reasons_jpm.pdf.txt", "it is as easy to overfit a walk-forward backtest as to overfit a walk-backward backtest"),
    ("M5a_validation", "lopezdeprado_2018_10reasons_jpm.pdf.txt", "History is a filtration; hence, using trailing data guarantees that the testing set is out-of-sample"),
    ("M5a_validation", "lopezdeprado_2018_10reasons_jpm.pdf.txt", "we can backtest a total number of paths"),
    ("M5a_validation", "li_2026_arxiv_2609_29530.pdf.txt", "no statistical technique conjures information out of unobserved intervals"),
    ("M5a_validation", "li_2026_arxiv_2609_29530.pdf.txt", "report the per-fold-versus-training-size curve rather than a single average"),
    ("M5a_validation", "cerqueira_torgo_mozetic_2020_arxiv_1905_11744.pdf.txt", "cross-validation approaches can be applied to stationary time series"),
    ("M5a_validation", "harvey_liu_zhu_2016_rfs.pdf.txt", "with a t-statistic greater than 3.0"),
    ("M5a_validation", "harvey_liu_zhu_2016_rfs.pdf.txt", "Both Bonferroni and Holm control FWER, and BHY controls FDR"),
    ("M5a_validation", "bailey_borwein_ldp_zhu_2017_pbo.pdf.txt", "even number S of disjoint submatrices of equal dimensions"),
    ("M5a_validation", "bailey_borwein_ldp_zhu_2017_pbo.pdf.txt", "High logit values imply a consistency between IS and OOS performances"),
    ("M5a_validation", "bailey_borwein_ldp_zhu_2014_pseudomath.pdf.txt", "no more than 45 independent model configurations should be tried"),
    ("M5a_validation", "lopezdeprado_lewis_2019_onc_ssrn3167017.pdf.txt", "the discovered strategy is likely to be a false positive"),
    ("M5a_validation", "lopezdeprado_lewis_2019_onc_ssrn3167017.pdf.txt", "using those clusters as a proxy"),
    ("M5a_validation", "lopezdeprado_lewis_2019_onc_ssrn3167017.pdf.txt", "in order to match the frequency"),
    ("M5a_validation", "storey_tibshirani_2003_pnas.pdf.txt", "expected proportion of false positives among all features as or more extreme than the observed one"),
    ("M5a_validation", "white_2000_reality_check.pdf.txt", "data snooping to be undertaken with some degree of confidence"),
    ("M5a_validation", "benjamini_hochberg_1995.pdf.txt", "For independent test statistics and for any configuration of false null hypotheses"),
    ("M5a_validation", "arxiv_2604_15531_spurious_predictability.pdf.txt", "the nominal K overstates the effective dimensionality of the search"),
    ("M5a_validation", "bailey_lopezdeprado_2014_dsr.pdf.txt", "expected maximum of"),
    ("M5b_power", "breiman_2001_random_forests.txt", "the values of the mth variable in the out-of-bag examples are randomly permuted"),
    ("M5b_power", "falces_marin_2022_plosone.txt", "mean reduction of weighted impurity over all the nodes"),
    ("M5b_power", "lopezdeprado_2018_10reasons_jpm.txt", "feature importance is a research tool, and backtesting is not"),
    ("M5b_power", "hooker_mentch_zhou_arxiv_1905_03151.txt", "forcing the original model to extrapolate to regions where there is little to no data"),
    ("M5b_power", "hooker_mentch_zhou_arxiv_1905_03151.txt", "A more general approach is re-learning"),
    ("M5b_power", "man_chan_2020_arxiv_2005_12483.txt", "MDA is the least stable method"),
    ("M5b_power", "lo_2002_faj_statistics_sharpe.txt", "reduces to Equation 17 if all autocorrelations"),
    ("M5b_power", "bailey_ldp_2012_sharpe_frontier.txt", "requires longer sample lengths than estimating only the first two moments"),
    ("M5b_power", "fisher_rudin_dominici_2019_jmlr.txt", "may rely on entirely different covariate information than the model used by another analyst"),
    ("M5b_power", "mlfinlab_fork_feature_clusters.txt", "snippet 6.5.2.1 page-85"),
    ("M5b_power", "lopezdeprado_2020_mlam_toc.txt", "Feature Importance Analysis"),
    ("M5b_power", "opdyke_2007_repec_abstract.html", "stationary and ergodic returns"),
]

if __name__ == "__main__":
    for root, f, q in PAIRS:
        print(check(root, f, q))
