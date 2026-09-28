"""HarnessReviewer (E.5 A3): independent re-derivation of verdict known answers."""
import math, statistics, sys
from statistics import NormalDist
from itertools import combinations
import numpy as np
sys.path.insert(0, "/home/kiros-li/Documents/GitHub/PropExperiment")
from screening import stage_e_verdict as V
from screening.stage_e_stats_units import frozen_epsilon
from funnel.multiple_comparisons import probability_of_backtest_overfitting, deflated_sharpe_ratio, expected_max_sharpe
nd = NormalDist()
means = np.arange(1.0, 101.0); b = V.summarize_means(np.array([40.0, 60.0]), means)
print("1 summary: ucb", b.ucb95, "hand", 1 + 0.95 * 99, "| se", b.se_boot, "hand", math.sqrt(sum((m - 50.5) ** 2 for m in means) / 100), "| p", b.p_upper, "hand", 2 / 101)
print("2 power:", V.null_power(10.0, 16.45), nd.cdf(16.45 / 10 - 1.645), "|", V.null_power(10.0, 10 * (1.645 + nd.inv_cdf(0.8))), 0.8)
print("3 holm thresholds K=9 m=3:", [0.05 / 9 / (3 - i) for i in range(3)], "| 0.002<=0.05/18:", 0.002 <= 0.05 / 18, "| 0.003<=0.05/18:", 0.003 <= 0.05 / 18)
for v in ("NG", "MCL", "MGC", "MHG"):
    e = frozen_epsilon(v); print("4 eps", v, e.eps_ticks, e.q_c, e.eps_usd_per_day_at_q)
vals = np.array([(-1.0) ** i for i in range(200)])
m = V.resampled_means(vals, 400, 20260923)
srt = np.sort(m); pos = 0.95 * 399; lo = int(math.floor(pos)); ucb = srt[lo] + (pos - lo) * (srt[lo + 1] - srt[lo])
se = math.sqrt(float(((m - m.mean()) ** 2).mean()))
p = (1 + int(((m - 0.0) >= 0.0).sum())) / 401
f = V.trial_figures(V.Series(tuple(range(200)), vals, 40), 8.0, 20260923, 400)
print("5 alt: ucb", f["ucb95"], ucb, "| se", f["se_boot"], se, "| p", f["p_upper"], p, "| power", f["null_power"], nd.cdf(8.0 / se - 1.645), "| status", f["status"], "| theta", f["theta_hat"])
m2 = V.resampled_means(vals, 400, 20260924)
print("6 seed sensitivity: arrays equal?", np.array_equal(m, m2), "| ucb", ucb, float(np.quantile(m2, 0.95)))
rng = np.random.default_rng(11); M = rng.normal(0, 1, (3, 8)).tolist()
cnt = 0; n = 0
for train in combinations(range(8), 4):
    test = [x for x in range(8) if x not in train]
    ins = [sum(r[x] for x in train) for r in M]; oos = [sum(r[x] for x in test) for r in M]
    best = max(range(3), key=lambda s: ins[s]); worse = sum(1 for s in range(3) if oos[s] < oos[best])
    cnt += ((worse + 0.5) / 3) <= 0.5; n += 1
print("7 pbo mine", cnt / n, "funnel", probability_of_backtest_overfitting(M, 8).pbo, "splits", n)
sh, nobs, N, var, sk, ku = 0.12, 200, 150, 0.02, -0.3, 4.5
g = 0.5772156649015329
emax = math.sqrt(var) * ((1 - g) * nd.inv_cdf(1 - 1 / N) + g * nd.inv_cdf(1 - 1 / (N * math.e)))
z = (sh - emax) * math.sqrt(nobs - 1) / math.sqrt(1 - sk * sh + (ku - 1) / 4 * sh ** 2)
print("8 dsr mine", nd.cdf(z), "funnel", deflated_sharpe_ratio(sh, nobs, N, var, sk, ku)["deflated_sharpe_ratio"], "| emax mine", emax, "funnel", expected_max_sharpe(N, var))
print("9 pvariance([0.3]) =", statistics.pvariance([0.3]), "| DSR with variance 0:", deflated_sharpe_ratio(0.12, 200, 150, 0.0)["deflated_sharpe_ratio"])
