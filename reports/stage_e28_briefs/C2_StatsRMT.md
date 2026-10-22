# E.28 methods brief, Part C2: random-matrix covariance cleaning, Bayesian shrinkage, information theory

Worker: C2_StatsRMT (MethodReader, opus). Written 2026-10-21 PDT, starting 02:44. Pages:
`reports/stage_e28_briefs/pages/C2_StatsRMT/` (log: `log.tsv`, one row per fetch, including failed fetches).
Scripts and outputs: `reports/stage_e28_briefs/work/C2_StatsRMT/` (`C2_StatsRMT_examples.py`, its output
`C2_StatsRMT_examples.json` (sha256 7eaf690d...6a), run log `C2_StatsRMT_examples.log`, and the fetch helper
`C2_StatsRMT_fetch.sh`). Every number marked "measured" comes from that JSON. The script uses synthetic data only,
with a fixed seed (20261021). No market data was read, nothing was registered, and N stays 538.

How to read this section. Section 0 ties these methods to the statistics the program already uses (DSR, PBO,
Holm, N). Part I (sections 1 to 4) covers random-matrix theory (RMT) and covariance shrinkage. Part II (sections 5
to 8) covers James-Stein, empirical Bayes, hierarchical models and Bayesian model averaging. Part III (sections 9
to 13) covers entropy, Lempel-Ziv, approximate entropy, mutual information and transfer entropy. Each method has
the eight items the brief asks for: (1) idea, (2) equations, (3) data, (4) what it estimates, (5) worked example,
(6) pilot hypothesis, (7) compute, (8) evidence. Section 14 summarizes compute and price, section 15 collects the
candidate hypotheses, section 16 gives verdicts, then come references, the evidence table and the gaps log.

Quotes are verbatim from saved text files (pdftotext output of the saved PDFs, or de-tagged HTML/XML). pdftotext
mangles some symbols (Greek letters, fraction bars, sums). Where a quoted line is mangled I say so and restate the
equation in clean notation beside it. Candidate hypotheses in this file are inputs for the lead. They are not
declarations, and the trial-count figures are what each would add if the lead chose to register it.

The short version. For a one-contract order-book program, RMT covariance cleaning has almost nothing to clean: with
40 book fields and about 2 million one-second snapshots, q = N/T is 2e-5 and the Marchenko-Pastur noise band
collapses to [0.991, 1.009] (measured, section 1). RMT and shrinkage matter on the multiple-testing side: the
matrix of the program's trial returns (538 trials by about 1,250 days) has q = 0.43, and empirical-Bayes shrinkage
is a direct alternative or complement to the DSR. The information-theory tools are usable as features and
lead-lag screens on one contract. The published evidence says predictability measured this way does not by itself
pay the spread.

---

## 0. Where these methods meet the program's existing statistics

The verdict code computes the DSR from each trial's Sharpe ratio, its sample length, skew and kurtosis, the trial
count N and the cross-sectional variance of the trials' Sharpe ratios (`screening/stage_e_verdict.py`, `dsr_table`:
"the Sharpe variance over ``variance_over`` (population variance)"). The deflation benchmark is the expected
maximum Sharpe ratio of N independent null trials (Bailey and López de Prado 2014, eq. 1 (restated under eq. 2) and Appendix 1, file
`bailey_lopezdeprado_2014_dsr.txt`):

    E[max SR] ~ sqrt(V) * [ (1 - g) * PhiInv(1 - 1/N) + g * PhiInv(1 - 1/(N e)) ]

where V is the variance of the estimated Sharpe ratios across trials, g = 0.5772 is the Euler-Mascheroni constant,
PhiInv is the standard normal quantile function and e = 2.718. The DSR is then the probabilistic Sharpe ratio
evaluated against that benchmark:

    DSR = Phi( (SR_hat - SR0) * sqrt(T - 1) / sqrt(1 - skew * SR_hat + (kurt - 1)/4 * SR_hat^2) ),  SR0 = E[max SR]

with SR_hat the selected trial's per-period Sharpe ratio, T its number of returns, skew and kurt its sample
skewness and (non-excess) kurtosis, and Phi the standard normal distribution function. The paper's text is mangled
in extraction at the equation itself; the surrounding sentence reads "we propose a Deflated Sharpe Ratio (DSR)
statistic that corrects for both sources of ̂ inflation" and it names the inputs: "the number of independent trials
carried out (N); ii) the variance of the backtest results".

Three places where Part I to III methods touch this machinery:

1. **N is "independent" trials.** The paper says so explicitly: "It is critical to understand that the N used to
   compute [...] corresponds to the number of independent trials. Suppose that we run M trials, where only N trials
   are independent, N<M." Random-matrix tools (section 1, item 6) and entropy of the eigenvalue spectrum (section 9)
   give estimates of an effective N from the correlation matrix of trial returns. The program's rule counts every
   configuration into N. Section 1 measures how much that rule overstates the benchmark (about 8% in one design).
2. **Shrinkage is the Bayesian answer to the winner's curse that DSR answers by deflation.** The DSR paper itself
   frames it that way: "Performance out of sample is likely to disappoint, a phenomenon called 'regression to the
   mean' in the shrinkage estimation literature, see Efron [2011]." Sections 5 to 7 give the shrinkage versions.
3. **PBO/CSCV and Holm are model-free.** Bayesian model averaging (section 8) and hierarchical models (section 7)
   replace "pick the best and correct" with "average or pool and report the posterior". They change what is
   selected, so under V43 the pooling rule itself must be frozen before data and every configuration it pools still
   counts into N.

---

# Part I. Random-matrix theory and covariance shrinkage

## 1. Marchenko-Pastur law and eigenvalue clipping (Laloux, Cizeau, Bouchaud and Potters 1999)

**(1) Idea.** Estimate a correlation matrix from T observations of N series. Even if the true correlation is the
identity (no correlation at all), the sample eigenvalues spread out over a band whose width depends only on
q = N/T. The Marchenko-Pastur (MP) law gives that band. Sample eigenvalues inside the band cannot be told apart from
noise; eigenvalues above it carry information (market factor, sectors). "Clipping" keeps the eigenvalues above the
band and replaces those inside it by their average.

**(2) Equations.** Let X be a T x N matrix of returns, each column demeaned and scaled to unit variance, and
E = X'X / T the sample correlation matrix with eigenvalues lambda_1 >= ... >= lambda_N. If the entries of X are
i.i.d. with variance sigma^2 and N, T -> infinity with q = N/T fixed in (0, 1], the empirical density of the
eigenvalues converges to

    rho(lambda) = sqrt( (lambda_+ - lambda)(lambda - lambda_-) ) / (2 pi q sigma^2 lambda),  lambda in [lambda_-, lambda_+]
    lambda_+-  = sigma^2 (1 +- sqrt(q))^2

Laloux et al. write it with Q = T/N (file `laloux_1999_noise_dressing.txt`, eq. 3; the line reads, mangled,
"λmax min = σ 2 (1 + 1/Q ± 2 1/Q)", which is sigma^2 (1 + 1/Q +- 2 sqrt(1/Q)), the same expression since
(1 +- sqrt(q))^2 = 1 + q +- 2 sqrt(q)). Assumptions: independent, identically distributed entries with finite
variance; no autocorrelation; stationarity. Derivation summary: the Stieltjes transform g(z) = (1/N) tr (zI - E)^-1
of a Wishart matrix satisfies a quadratic equation in the large-N limit (the "fundamental equation" of RMT);
solving it and taking the imaginary part of g just below the real axis gives rho. Bun et al. (2017) derive it in
their chapter 3.

Clipping (Bun et al. 2017, eq. 7.55, file `bun_bouchaud_potters_2017_cleaning.txt`):

    Xi_clip = sum_i xi_i u_i u_i',   xi_i = lambda_i if lambda_i >= (1 + sqrt(q))^2, else lambda_bar

where u_i are the sample eigenvectors (kept unchanged) and lambda_bar is chosen so that the trace is preserved
(Tr Xi_clip = Tr E = N). Bun et al.: "all the eigenvalues that are beyond the largest expected eigenvalue of the
empirical matrix λ+ = (1 + q)2 (within a null hypothesis) are interpreted as signal while the others are pure
noise" (the sqrt is lost in extraction: lambda_+ = (1 + sqrt(q))^2).

Why it matters for portfolios. For a minimum-variance portfolio built from E, the realized out-of-sample risk
exceeds the true optimal risk by about 1/(1 - q): Bun et al. state "TrE−1 = TrC−1 /(1 − q) for a wide class of
processes. In other words, the out-of-sample risk TrE−1 can excess by far the true optimal risk TrC−1 when q > 0,
and even diverge when q → 1."

**(3) Data.** Many series observed over the same times: N assets (or N strategies, or N features) by T periods.
One CME contract's mbp-10/mbo/tbbo data gives one price series. The method applies only if N is formed some other
way: (a) N order-book fields (10 bid and 10 ask prices and sizes = 40) at T snapshots, or (b) N candidate
strategy configurations at T days. For (a) four months are far more than enough, so cleaning has nothing to do.
For (b) the data is the program's own trial-return matrix, not Databento data.

**(4) Estimates / decides.** A cleaned correlation (or covariance) matrix; the number of eigenvalues above the
noise band (the number of "factors"); a null test of "no correlation structure".

**(5) Worked examples (measured, part A of the script; arithmetic shown).**

| Setting | N | T | q = N/T | lambda_- = (1 - sqrt q)^2 | lambda_+ = (1 + sqrt q)^2 |
|---|---|---|---|---|---|
| Laloux et al. S&P 500 (check) | 406 | 1309 | 0.310 | (1 - 0.557)^2 = 0.196 | (1 + 0.557)^2 = 2.424 |
| 45 CME roots, 4 years daily | 45 | 1000 | 0.045 | (1 - 0.212)^2 = 0.621 | (1 + 0.212)^2 = 1.469 |
| 538 trials, 5 years daily | 538 | 1250 | 0.430 | (1 - 0.656)^2 = 0.118 | (1 + 0.656)^2 = 2.742 |
| one contract, 40 book fields, 1 s, 84 days x 6.5 h | 40 | 1,965,600 | 2.0e-5 | 0.991 | 1.009 |

Laloux et al. found the largest S&P eigenvalue "25 times larger than the predicted λmax" and that the MP fit
"accounts quite satisfactorily for 94% of the spectrum, while the 6% highest eigenvalues still exceed the
theoretical upper edge". For the one-contract case the band is 1 +- 0.009: any book-field correlation that matters
is far outside it, so the MP law has nothing to say. That is the honest core of this section.

**Item 6 below uses the trial matrix, where q is large.** Measured, part B: 200 null trials (true Sharpe 0) in 5
clusters of 40, correlation 0.6 inside a cluster and 0.1 across, T = 750 days, 400 Monte Carlo repetitions.

| Quantity | Value |
|---|---|
| Monte Carlo mean of the maximum daily Sharpe among 200 trials | 0.0849 |
| DSR formula with N = M = 200 (all trials counted) | 0.0913 (+7.6%) |
| N that makes the DSR formula match the Monte Carlo | 112 |
| Bailey-López de Prado N_hat = rho_bar + (1 - rho_bar) M, rho_bar = 0.198 | 160.7, giving 0.0890 |
| Exponential of the Shannon entropy of normalized eigenvalues ("effective rank") | 37.4, giving 0.0714 |
| Participation ratio (sum lambda)^2 / sum lambda^2 | 11.9, giving 0.0549 |
| Number of eigenvalues above the MP edge (2.30) | 5, giving 0.0394 |

Reading: the MP count finds the 5 clusters (the true top eigenvalues are 40.4, 20.4 x 4), but the number of
factors is not the number of independent trials. Trials correlated at 0.6 are far from duplicates, and using N = 5
would understate the selection benchmark by more than half: an anti-conservative error. Counting every trial
(N = M) overstates the benchmark by about 7% here (0.7 points of it is the formula's asymptotic approximation and the rest is the correlation), a conservative error. The Bailey-López de Prado interpolation (their
eq. 9, mangled in extraction; restated here) came closest without going below the Monte Carlo value. This is one
synthetic design; the ordering may change with other correlation structures.

**(6) Pilot hypothesis.** The pilot (fill rates, queue times, 1/10/60 s markouts of a 1-lot passive order on one
contract) has no cross-section for RMT to clean. Two uses remain, both on the multiple-testing side:
- *Candidate R1 (reporting, not a trading hypothesis):* "The effective number of independent configurations in the
  pilot grid, estimated three ways (Bailey-López de Prado N_hat, MP count, entropy rank), is below the raw count."
  Statistic: the three estimates from the daily markout-P&L matrix of the K configurations. Sample: needs T well
  above K (q < 0.5); with 84 trading days, K <= 40. Adds 0 to N: it is a diagnostic. It must never lower the N used
  in a verdict unless the lead registers that change in advance.
- If a later purchase covers several contracts (for example the 45-root universe at 1-minute bars, already owned),
  clipping becomes usable for a multi-contract passive-order book allocation. That is outside the pilot.

**(7) Compute.** Measured: eigendecomposition of a 538 x 538 correlation matrix 0.025 s, of 2000 x 2000 0.62 s;
covariance of a 1,000,000 x 40 array 0.25 s (part H). Clipping on p = 100 took 1.16 ms per estimate (part C). Laptop
is ample; no cloud needed.

**(8) Evidence.** Laloux et al. (1999) and Plerou et al. (2002; file `plerou_2002_rmt.txt`: "a majority of the
eigenvalues of C fall within the RMT bounds [λ− , λ+ ] for the eigenvalues of random correlation matrices") are
in-sample spectral facts, not trading results. Out-of-sample evidence is about risk, not returns: Bun et al. (2017,
Tables 4 and 5) report that "it is always better to use a cleaned correlation matrix: the out-ofsample risk
without cleaning is, as expected, always higher than with any of the cleaning schemes", on US, Japanese and
European stock panels. Bun et al. list clipping's weakness: "one often observes empirically, especially with
financial data, that the value of q = N/T [...] is significantly different from the 'effective' value qeff",
because of autocorrelation and fat tails. Negative/mixed: Pantaleo et al. (2011; `pantaleo_2011_covariance.txt`):
"when short selling is not allowed and T > N , the considered methods are unable to outperform the sample
covariance in terms of realized risk". No retail-scale, one-contract or latency-related evidence exists for this
method because it is not a single-instrument method.

---

## 2. Rotationally invariant estimators, RIE (Bun, Bouchaud and Potters 2017)

**(1) Idea.** Keep the sample eigenvectors (we cannot do better without a prior on directions) and choose new
eigenvalues to minimize the distance to the true matrix. The best such eigenvalues ("oracle") involve the unknown
truth, but in the large-N limit they converge to a formula that uses only the sample eigenvalues. Clipping is a
crude special case; RIE shrinks each eigenvalue by its own amount.

**(2) Equations.** The oracle within the class of estimators that share E's eigenvectors u_i is
xi_i^ora = u_i' C u_i (the true variance along the sample direction). Bun et al. derive (eq. 6.5, the
Ledoit-Péché formula; file `bun_bouchaud_potters_2017_cleaning.txt`):

    xi_hat(lambda) = lambda / | 1 - q + q lambda lim_{eta -> 0+} g_E(lambda - i eta) |^2,
    g_E(z) = (1/N) sum_j 1/(z - lambda_j)

where g_E is the sample Stieltjes transform, i is the imaginary unit, |.| the complex modulus. Quote: "We notice that
the RHS of this last equation does not involve the matrix C anymore and depends only on deterministic quantities.
This is the 'miracle' of the large N limit". Practical version: evaluate at finite eta and rescale to preserve the trace. I used eta = N^-1/2, as in
Bun et al.'s own numerical check of g_E (their Figure caption: "The empirical estimate of GE (z) (blue line) is
computed for any z = λi − iN −1/2"). Assumptions: N and T large
with q fixed; returns i.i.d. over time (the same as MP); rotational invariance (no preferred eigenvector basis).
Bun et al. note that for small N the raw formula is biased for small eigenvalues and propose a regularized "hRie"
(their section 8.1); I implemented the plain form only.

**(3) Data.** As in section 1: a cross-section. Not applicable to a single price series.

**(4) Estimates.** A cleaned covariance matrix; it is optimal for the out-of-sample risk of Markowitz portfolios
under the stated assumptions (Bun et al.: "the optimal RIE (6.5) actually minimizes the out-of-sample risk").

**(5) Worked example (measured, part C).** p = 100 assets, n = 200 observations (q = 0.5), population eigenvalues
80 x 1, 15 x 3, 5 x 10 in a random basis, 60 repetitions. Out-of-sample variance of the global minimum-variance
portfolio divided by the oracle variance:

| Estimator | OOS variance / oracle | s.e. | ms per estimate |
|---|---|---|---|
| sample covariance | 1.967 | 0.025 | 0.08 |
| MP clipping | 1.283 | 0.004 | 1.16 |
| Ledoit-Wolf linear (sklearn) | 1.228 | 0.005 | 3.01 |
| RIE, plain eq. 6.5 form | 1.181 | 0.005 | 1.18 |
| Ledoit-Wolf analytical nonlinear | 1.127 | 0.003 | 1.41 |

The sample-covariance figure matches the theory: 1/(1 - q) = 1/(1 - 0.5) = 2.0. RIE and nonlinear shrinkage target the same
oracle: Bun et al. call eq. 6.5 "the final Ledoit-Péché formula", and Ledoit and Wolf (2020) say their oracle
"was first discovered by Ledoit and Péché (2011, Theorem 3)". The gap here comes from how each estimates the
spectral density (my unregularized complex-shift RIE versus their kernel), not from different targets.

**(6) Pilot hypothesis.** None on one contract. Same reporting use as R1 if the lead wants a cleaned
correlation of configurations; RIE adds nothing to N.

**(7) Compute.** O(N^3) for the eigendecomposition plus O(N^2) for the transform; 1.18 ms at N = 100. Laptop.

**(8) Evidence.** Bun et al. (2017, Table 4): the regularized RIE gave the lowest out-of-sample volatility "in all
cases but one (Minimum risk portfolio in Japan, where the LW linear shrinkage outperforms)". That is a risk result
on stock panels with N >= 100, not a return or one-contract result. No negative-result paper was found in this
search budget for RIE specifically; Pantaleo et al. (section 1) is the general caution.

---

## 3. Ledoit-Wolf linear shrinkage (2004)

**(1) Idea.** Replace the sample covariance S by a weighted average of S and a simple target (a multiple of the
identity). Choose the weight that minimizes expected squared error; it has a closed form, estimated from the data.

**(2) Equations** (Ledoit and Wolf 2004, JMVA; file `ledoit_wolf_2004_jmva.txt`). The norm is the scaled
Frobenius norm ||A||^2 = tr(A A')/p. Define mu = tr(Sigma)/p (average true variance), alpha^2 = ||Sigma - mu I||^2
(how far the truth is from the target), beta^2 = E||S - Sigma||^2 (estimation error of S), delta^2 = E||S - mu I||^2.
Lemma 2.1: alpha^2 + beta^2 = delta^2. Among Sigma* = rho nu I + (1 - rho) S the optimum is nu = mu and

    rho* = beta^2 / delta^2,   Sigma* = (beta^2/delta^2) mu I + (alpha^2/delta^2) S

Derivation (quoted, from the paper's proof): "E[kΣ∗ − Σk2 ] = ρ2 α2 + (1 − ρ)2 β 2 . The first order condition is:
2ρα2 − 2(1 − ρ)β 2 = 0. The solution is: ρ = β 2 /(α2 + β 2 ) = β 2 /δ 2 ." The bona fide estimator replaces the
four scalars by sample versions (Lemmas 3.2 to 3.5, eq. 14):

    m = tr(S)/p,   d^2 = ||S - m I||^2,   b_bar^2 = (1/n^2) sum_k ||x_k x_k' - S||^2,
    b^2 = min(b_bar^2, d^2),   a^2 = d^2 - b^2,   S* = (b^2/d^2) m I + (a^2/d^2) S

where x_k is the k-th (demeaned) observation vector and n the sample size. Assumptions: i.i.d. observations with
finite fourth moments; p and n may both grow. Note b_bar^2 measures how much the individual outer products scatter
around their average: the noisier, the more shrinkage.

**(3) Data.** A cross-section again. On one contract, the natural use is regularizing a feature covariance (for
example the 40 book fields or a 64-feature library) inside a linear model. Ridge regression is the same idea
applied to the regression coefficients; the program already uses ridge.

**(4) Estimates.** A well-conditioned covariance matrix and the shrinkage intensity rho*.

**(5) Worked example (measured, part C).** On p = 100, n = 200 the sklearn estimator chose rho* = 0.287 on the last
repetition and cut the GMV out-of-sample variance from 1.97x to 1.23x the oracle (table in section 2). Hand
illustration of the formula: if b^2 = 0.30 and d^2 = 1.05 (scaled units), then rho* = 0.30/1.05 = 0.286, so
S* = 0.286 m I + 0.714 S.

**(6) Pilot hypothesis.** No standalone hypothesis. If the lead's frozen pipeline fits a linear markout model on
many book features, linear shrinkage of the feature covariance is a pipeline choice to freeze, not a trial.

**(7) Compute.** O(n p^2); 3.01 ms at p = 100, n = 200 (measured). Laptop.

**(8) Evidence.** Ledoit and Wolf (2004, "Honey"; file `ledoit_wolf_2004_honey.txt`): "nobody should be using the
sample covariance matrix for the purpose of portfolio optimization" and "shrinkage reduces tracking error relative
to a benchmark index, and substantially increases the realized information ratio of the active portfolio manager".
These are equity-portfolio results with N in the hundreds. Pantaleo et al. (2011) is the mixed result (long-only,
T > N: no gain in realized risk).

---

## 4. Ledoit-Wolf nonlinear shrinkage (2017 RFS; analytical version 2020)

**(1) Idea.** Linear shrinkage pulls every eigenvalue toward the grand mean by the same fraction. Nonlinear
shrinkage moves each eigenvalue toward its own neighbours, by an amount read off the density of the other
eigenvalues. It is the RIE of section 2, estimated with a kernel.

**(2) Equations** (Ledoit and Wolf, UZH WP 264, "Analytical nonlinear shrinkage"; file
`ledoit_wolf_analytical_nls.txt`). With c = p/n, f the limiting density of sample eigenvalues and Hf its Hilbert
transform (Hf(x) = (1/pi) p.v. integral f(t)/(t - x) dt), the oracle shrunk eigenvalue is (their eq. 3.6 with
estimates plugged in):

    d_i = lambda_i / ( [pi c lambda_i f(lambda_i)]^2 + [1 - c - pi c lambda_i Hf(lambda_i)]^2 )

Feasible version: estimate f and Hf with an Epanechnikov kernel of bandwidth h_i = lambda_i n^(-1/3) (eq. 4.9: "hn
..= n−1/3 =⇒ ∀i = 1, . . . , p hn,i ..= λn,i hn = λn,i n−1/3"). The paper's interpretation of eq. 3.5: "if there is
a heavy mass of other eigenvalues hovering slightly above, 2cHϕ (λn,i ) will be strongly positive, which will push
λn,i higher in the direction of its closest and most numerous neighbors." Assumptions: as in section 2, plus
regularity of the limiting spectrum; the p > n case is covered separately in the paper (I implemented p <= n).

**(3) Data.** Cross-section; same remarks as sections 1 to 3.

**(4) Estimates.** A covariance matrix with p free parameters (one per eigenvalue): the "Goldilocks" number in the
RFS paper's title.

**(5) Worked example (measured, part C).** Best of the five in the race: 1.127x the oracle variance, 1.41 ms per
estimate at p = 100 (implementation in `C2_StatsRMT_examples.py`, function `analytic_nls`, written from the
paper's equations 3.6, 4.5 to 4.9).

**(6) Pilot hypothesis.** None on one contract.

**(7) Compute.** O(p^2) after the eigendecomposition; the paper: "typically 1,000 times faster with the same
accuracy, and accommodates covariance matrices of dimension up to 10, 000". Laptop.

**(8) Evidence.** RFS 2017 (file `ledoit_wolf_2017_goldilocks.txt`): "In backtests with historical stock return data,
it performs better than previous proposals and, in particular, it dominates linear shrinkage." These are
portfolio-variance results on stocks, not returns and not single-instrument trading.

**Part I bottom line for this program.** One contract has no cross-section; RMT cleaning does not apply to the
pilot. The only live use is the trial matrix (effective N, section 1 item 6), where the measured design says
counting every configuration is mildly conservative and the MP factor count is badly anti-conservative.

---
# Part II. James-Stein, empirical Bayes, hierarchical models, model averaging

Common setting for sections 5 to 7. K strategies or configurations; for each an estimate z_i (a Sharpe ratio, a
mean markout, an alpha) with sampling standard error s_i, and an unknown true value mu_i:

    z_i | mu_i ~ N(mu_i, s_i^2),   i = 1..K

The winner's curse: the largest z_i are, on average, too large, because they were selected for being large.
Efron (2011; file `efron_2011_tweedie.txt`): "The largest few of the zi ’s are likely to substantially overestimate
their corresponding µi ’s, this being an example of selection bias, or regression to the mean."

## 5. James-Stein estimation

**(1) Idea.** With three or more means to estimate at once, the obvious estimate (each z_i on its own) is beaten,
in total squared error, by pulling every z_i toward a common point by a data-chosen fraction. The fraction is large
when the z_i are no more spread out than noise alone would make them, and small when they are much more spread
out.

**(2) Equations.** Equal known variance s^2 (set s = 1 by rescaling). Shrinking toward 0 (Efron 2011, eq. 3.9,
derived from Tweedie's formula under a normal prior mu ~ N(0, A)):

    mu_hat_i = (1 - (K - 2) / sum_j z_j^2) z_i

Derivation summary (Efron 2011, eqs. 3.7 to 3.9, quoted): "Suppose the prior density g(µ) in (1.2) is normal, say
µ ∼ N (0, A) and z|µ ∼ N (µ, 1). [...] The marginal distribution of z is then N (0, V ), with V = A + 1, so l0 (z)
= −z/V and Tweedie’s formula becomes E{µ|z} = (1 − 1/V )z." and "The James–Stein rule substitutes the unbiased
estimator (N − 2)/ [sum] zj^2 for 1/V" (sum sign mangled in extraction). So James-Stein is the empirical-Bayes
posterior mean with the prior variance estimated from the data. Shrinking toward the grand mean z_bar instead of
0 costs one more degree of freedom:

    mu_hat_i = z_bar + (1 - B)(z_i - z_bar),   B = min(1, (K - 3) s^2 / sum_j (z_j - z_bar)^2)

(the positive-part, grand-mean version used by Efron and Morris; [unverified] in fetched text: the Efron-Morris
1977 Scientific American file `efron_morris_1977_sciam.pdf` is a scanned image with no text layer, and the James
and Stein 1961 paper was blocked by Project Euclid's bot wall). Assumptions: independent normal z_i, known common
s^2, K >= 3 (K >= 4 for the grand-mean version), squared-error loss summed over all K.

**(3) Data.** One estimate and its standard error per configuration. On one contract: per-configuration mean
markouts or daily P&L Sharpe ratios from the pilot. Four months is enough to compute it; whether it is enough to
learn anything is the worked example's point.

**(4) Estimates.** Shrunk estimates of every configuration's true performance; B is the fraction of the observed
spread that is noise.

**(5) Worked example (measured, part D; arithmetic shown).** Twelve configurations with observed annualized Sharpe
ratios z = (1.9, 1.2, 0.8, 0.5, 0.3, 0.1, -0.2, -0.4, -0.6, -0.9, -1.1, -1.5) (illustrative numbers, not data).
z_bar = 0.0083; sum (z - z_bar)^2 = 10.869. Under i.i.d. normal daily returns the standard error of an annualized
Sharpe ratio from T daily returns is about sqrt(252/T) (the SE of a daily Sharpe is about 1/sqrt(T) when the
Sharpe is small; annualizing multiplies by sqrt(252)).

- T = 84 days (four months): s = sqrt(252/84) = sqrt(3) = 1.732, s^2 = 3. B = 9 x 3 / 10.869 = 2.48, capped at 1.
  Every configuration is shrunk all the way to 0.008: the observed spread is smaller than noise alone would give
  (the expected sum of squares under pure noise is (K - 1) s^2 = 33). The 1.9 "winner" carries no information.
- T = 1000 days: s^2 = 0.252. B = 9 x 0.252 / 10.869 = 0.209. The winner becomes 0.0083 + 0.791 x 1.892 = 1.505.
- For comparison, the DSR benchmark for K = 12 null trials with V = s^2 = 3 (annualized units):
  sqrt(3) x [0.4228 x PhiInv(1 - 1/12) + 0.5772 x PhiInv(1 - 1/(12e))] = 1.732 x [0.4228 x 1.383 + 0.5772 x 1.871]
  = 1.732 x 1.665 = 2.88. With four months of data, the best of twelve null configurations is expected to show an
  annualized Sharpe ratio near 2.9. With T = 1000 the benchmark is 0.84.

**(6) Pilot hypothesis.** James-Stein is the simplest form of the empirical-Bayes candidate in section 6 (E1); it
adds no configurations of its own.

**(7) Compute.** Closed form; microseconds.

**(8) Evidence.** Efron (2011) shows the empirical-Bayes correction working on simulated and genomics data ("the
empirical Bayes bias correction lˆi0 was quite effective in both groups"). In finance, the closest out-of-sample
test is the empirical-Bayes work in section 6. James-Stein's dominance is a theorem about total squared error over
all K; it does not promise that the selected best is estimated well, which is the question the program cares about
(see Andrews, Kitagawa and McCloskey in section 6).

---

## 6. Empirical-Bayes shrinkage of many strategies' Sharpe ratios, and how it relates to DSR, Holm and FDR

**(1) Idea.** Treat the K true performances mu_i as draws from a common distribution g. Estimate g from all K
estimates at once (that is the "empirical" part), then report each strategy's posterior mean E[mu_i | z_i]. The
posterior is immune to selection: picking the largest posterior mean does not bias it, because the posterior
already accounts for luck. This replaces "select the best, then deflate" (DSR) with "shrink all, then select".

**(2) Equations.**

*Normal prior (Jensen, Kelly and Pedersen 2021; file `jensen_kelly_pedersen_2021_replication.txt`, eqs. 4 to 6).*
With prior alpha ~ N(0, tau^2) and OLS estimate alpha_hat with sampling variance sigma^2/T:

    E(alpha | alpha_hat) = kappa alpha_hat,   kappa = tau^2 / (tau^2 + sigma^2/T) = 1 / (1 + sigma^2/(tau^2 T))
    Var(alpha | alpha_hat) = kappa sigma^2 / T

Quote: "The more data we have (higher T ), the less shrinkage there is (i.e., κ closer to 1). Likewise, the
stronger is the prior of zero alpha (i.e., lower τ ), the heavier is the shrinkage." The empirical-Bayes step
estimates tau^2 from the cross-section, for example by the method of moments:
tau_hat^2 = max(0, sample variance of z - mean of s_i^2).

*General prior: Tweedie's formula (Efron 2011, eqs. 1.4 and 1.5).* For z | mu ~ N(mu, s^2) and any prior g,

    E[mu | z] = z + s^2 l'(z),   l(z) = log f(z),   f(z) = integral phi_s(z - mu) g(mu) dmu

where f is the marginal density of the z's and phi_s the N(0, s^2) density. Quote: "The crucial advantage of
Tweedie’s formula is that it works directly with the marginal density f (z), avoiding the difficulties of
deconvolution involved in the estimation of g(µ)." In practice l is fitted to the histogram of the K estimates
(Efron uses Poisson regression on binned counts). It needs K in the hundreds or more; with K = 12 only the normal
prior is estimable.

*Relation to the program's controls.*
- DSR deflates only the selected strategy, by the expected maximum of N null trials. Empirical Bayes shrinks every
  strategy by an amount learned from the cross-section; if the cross-section looks like pure noise (tau_hat = 0),
  everything is shrunk to the prior mean, which is the Bayesian version of "nothing passed".
- Holm controls the family-wise error rate (any false rejection). Benjamini-Hochberg controls the false discovery
  rate. Efron (2011) relates Tweedie's formula to Benjamini-Hochberg in his section 6 (abstract keyword list:
  "false discovery rates"). Jensen et al.: "Reduction of false discoveries is achieved first by shrinking estimates
  toward the prior. When there is no information in the data, the alpha point estimate is the prior mean and there
  are no false discoveries."
- Selective inference is the frequentist answer to the same question. Andrews, Kitagawa and McCloskey (file
  `andrews_kitagawa_mccloskey_2018_winners.txt`) give confidence sets valid "conditional on the parameter selected",
  naming "the best-performing investment strategy based on historical data" as a case where "conventional estimates
  are biased and conventional confidence intervals are unreliable".

**(3) Data.** One estimate z_i and standard error s_i per configuration; the more configurations, the better g is
estimated. Correlated estimates (overlapping configurations on the same days) break the independence that the
simple formulas assume; Jensen et al.'s hierarchical model handles correlation explicitly (section 7). One
contract's four months give K configurations with large s_i (worked example in section 5).

**(4) Estimates.** Posterior means and intervals for every configuration; tau^2 (the true dispersion of
performance across configurations); a Bayesian false discovery rate.

**(5) Worked example (measured, part D).** Same twelve Sharpe ratios as section 5.
- T = 84: tau_hat^2 = max(0, 10.869/11 - 3) = max(0, 0.988 - 3) = 0, kappa = 0. All posteriors equal z_bar = 0.008.
- T = 1000: tau_hat^2 = 0.988 - 0.252 = 0.736; kappa = 0.736 / (0.736 + 0.252) = 0.745. The 1.9 winner becomes
  0.0083 + 0.745 x 1.892 = 1.418 (slightly more shrinkage than James-Stein's 1.505 because the moment estimator uses
  K - 1 rather than K - 3).

**(6) Pilot hypothesis (candidate E1).**
- Name: "Empirical-Bayes posterior of the 60-s markout, net of fees, for the K passive-order configurations of the
  pilot grid." The configurations would be the grid the lead defines (for example order side x time-of-day bucket x
  queue position at entry).
- Statistic: (a) tau_hat^2 with a parametric-bootstrap p-value against tau^2 = 0 (is there any real dispersion in
  configuration quality?); (b) for the configuration with the highest posterior mean, the posterior probability
  that its net markout is above zero; (c) a calibration check on held-out months, in the style of Chen and Dim
  (2025): the out-of-sample mean of the top configuration lies within 2 standard errors of its EB prediction.
- Sample: per-configuration standard error s = sd/sqrt(fills). With a 60-s markout sd of 1.5 ticks (an assumption,
  not a measurement) and 500 fills per configuration, s = 0.067 tick; detecting tau = 0.1 tick of true dispersion
  needs s comparable to tau or smaller, so several hundred fills per configuration. Part H of the script: detecting
  a 0.1-tick mean at 80% power needs 1,766 fills for one test, 3,092 under a Bonferroni split over K = 12, 3,842
  over K = 50.
- Trial count: the K configurations count into N whether or not shrinkage is used (V43: every configuration
  counted). EB is a selection and reporting rule; it must be declared with the grid. The lead decides whether a
  DSR gate still applies on top (my reading: keep both; they answer different questions).

**(7) Compute.** Normal-prior EB is closed form. Tweedie with a spline or Poisson fit: milliseconds for K in the
thousands. Chen and Dim ran 136,000 strategies; that is still a laptop-sized job.

**(8) Evidence (all cross-sectional equities; none at retail order-book scale).**
- Chen and Zimmermann (file `chen_zimmermann_pubbias_eb.txt`): "Estimates from three meta-studies find that the
  average correction (shrinkage) accounts for only 10 to 15 percent of in-sample mean returns and that the risk of
  inference going in the wrong direction (the false discovery rate) is less than 10%." This is for published
  predictors with t-statistics well above 2, the opposite of a pilot with four months of data.
- Chen and Dim (file `chen_dim_high_throughput.txt`): EB-selected top 1% of 136,000 data-mined strategies "earns
  out-of-sample returns of 5.7% per year over the 1983-2020 sample". The negative part: "Post-2004, EB has more
  difficulty with accuracy [...] out-of-sample returns are even closer to zero than predicted." A text search (grep -a) of the full
  text for "cost" finds no transaction-cost adjustment (only accounting variable names and one reference title), so these are gross
  long-short portfolio returns. They also report: "Multiple testing methods popular in finance fail to identify
  most out-of-sample performers."
- Jensen, Kelly and Pedersen: factors "work out-of-sample in a new large data set covering 93 countries".
- Chen (2024, file `chen_tstat_hurdles.txt`): raised t-hurdles are weakly identified from published data, whereas
  "statistics that can target only published findings (e.g. empirical Bayes shrinkage and the FDR) can be strongly
  identified".
- Harvey and Liu (2015, file `harvey_liu_2015_backtesting.txt`), the frequentist haircut the program's t > 3.0 rule
  comes from: "the multiple testing haircut is nonlinear. The highest Sharpe ratios are only moderately penalized,
  while the marginal Sharpe ratios are heavily penalized."

---

## 7. Hierarchical (multilevel) models for many configurations

**(1) Idea.** Configurations come in families: the same rule with different parameters, the same signal on
different sessions. A hierarchical model shrinks each configuration toward its family mean, and each family mean
toward an overall prior. A family where most members do badly drags down its one lucky member.

**(2) Equations.** Two levels, normal throughout:

    z_ij | mu_ij ~ N(mu_ij, s^2)          configuration j in family i
    mu_ij | theta_i ~ N(theta_i, tau_w^2)  within-family dispersion
    theta_i ~ N(0, tau_b^2)                between-family dispersion, prior mean 0

Posterior means (known variances): theta_i shrinks the family average z_i. toward 0 with
kappa_b = tau_b^2 / (tau_b^2 + s^2/J) (J members per family), and each mu_ij shrinks toward the posterior family
mean with kappa_w = tau_w^2 / (tau_w^2 + s^2). (This is the conditional-on-variances version; full Bayes puts
priors on tau_w and tau_b and integrates them out by MCMC.) Jensen et al. (Proposition 4) give the multi-level
posterior with correlated factors and clusters; quote on the mechanism: "each alpha is shrunk toward its cluster
mean (i.e., toward related factors), in addition to being shrunk toward the prior of zero. So, if we observe a
cluster of factors in which most perform poorly, then this evidence reduces the posterior alpha even for the few
factors with strong performance—another form of Bayesian MT correction." Assumptions: exchangeability within each
family (no configuration known in advance to be better), normal errors, independence or a modelled correlation.

**(3) Data.** As section 6, plus a family label for every configuration, fixed before data.

**(4) Estimates.** Posterior configuration and family means; the share of variance between versus within families.

**(5) Worked example (measured, part D two-level; method of moments).** Three families of four markout means
(ticks): A = (0.30, 0.22, 0.18, 0.10), B = (0.05, 0.02, -0.04, -0.08), C = (-0.10, -0.12, -0.20, -0.25), common
s = 0.08. Within-family sum of squares = 0.0458 over 9 degrees of freedom = 0.0051 < s^2 = 0.0064, so
tau_w^2 = 0 and kappa_w = 0: within a family the differences are noise, and every member gets the family mean.
Family means 0.200, -0.013, -0.168 with standard error s/2 = 0.04; the mean of their squares (0.0227, prior mean 0) minus 0.0016 gives
tau_b^2 = 0.0211, kappa_b = 0.0211/(0.0211 + 0.0016) = 0.930. Posteriors: 0.186 for all of A, -0.012 for B, -0.156
for C. The "best" configuration (0.30) is reported as 0.19, and the choice among A's four members is declared
uninformative.

**(6) Pilot hypothesis (candidate E2).** "Partial pooling across the pilot grid's families gives a positive
posterior net markout for at least one family." Statistic: posterior probability P(theta_i > 0 | data) for each
family, with the family structure and priors frozen in advance; out-of-sample check as in E1. Sample: as E1, and
at least 3 families for tau_b to be estimable. Trial count: every configuration in every family counts into N.
The lead decides whether family-level selection reduces the count used in a DSR gate (it should not, under the
current rule).

**(7) Compute.** Closed form for the normal model; MCMC (PyMC or Stan) for full Bayes with unknown variances and
fat-tailed errors: seconds to minutes for K in the hundreds on the laptop CPU. No GPU needed.

**(8) Evidence.** Jensen et al. is the main finance test (cross-sectional factors, 93 countries, out-of-sample).
Their result runs against a "replication crisis" reading, and their hierarchical shrinkage produces more
discoveries, not fewer: "the increased precision from joint estimation has the opposite effect of enhancing
statistical power and thus increases discoveries." That cuts both ways for this program: a hierarchical model is
less conservative than Holm when families are strong, so it must be frozen before data.

---

## 8. Bayesian model averaging (BMA)

**(1) Idea.** Instead of choosing one model (one feature set, one specification), weight every candidate model by
its posterior probability and average their predictions. The uncertainty about which model is right then shows up
in the forecast's spread instead of being thrown away at the selection step.

**(2) Equations** (Hoeting, Madigan, Raftery and Volinsky 1999; file `hoeting_1999_bma.txt`, eqs. 1 to 3 and 13;
the equation glyphs are partly lost in extraction and restated here). For a quantity of interest Delta, data D and
models M_1..M_K:

    pr(Delta | D) = sum_k pr(Delta | M_k, D) pr(M_k | D)
    pr(M_k | D) = pr(D | M_k) pr(M_k) / sum_l pr(D | M_l) pr(M_l),   pr(D | M_k) = integral pr(D | theta_k, M_k) pr(theta_k | M_k) dtheta_k
    E[Delta | D] = sum_k Delta_hat_k pr(M_k | D)
    Var[Delta | D] = sum_k (Var[Delta | D, M_k] + Delta_hat_k^2) pr(M_k | D) - E[Delta | D]^2

where pr(D | M_k) is the integrated (marginal) likelihood, theta_k model k's parameters. BIC approximation (their
eq. 13: "log prD  Mk  ≈ log prD  β̂k  Mk  − dk log n", the factor 1/2 lost in extraction): log pr(D | M_k) is
about log-likelihood minus (d_k/2) log n, so with equal model priors w_k is proportional to exp(-BIC_k/2), with
BIC_k = n log(RSS_k/n) + d_k log n for Gaussian regression. The variance formula is the law of total variance: the
second term adds between-model disagreement. Assumptions: the true model is in the set ("All probabilities are
implicitly conditional on [the set of models]"), sensible priors, and for BIC large n.

**(3) Data.** Whatever the candidate models need. On one contract: for example K regressions of the 10-s or 60-s
markout of filled passive orders on different subsets of book features at entry.

**(4) Estimates.** Model-averaged predictions and coefficients, posterior model probabilities, posterior inclusion
probability of each feature.

**(5) Worked example (measured, part E).** n = 2000 synthetic fills; 60-s markout y = -0.15 x imbalance + noise
(sd 1.5 ticks). Models: M0 constant, M1 constant + imbalance, M2 constant + imbalance + spread. BIC = 1667.64,
1664.57, 1672.17. Differences from the best: 3.07 and 7.60; exp(-3.07/2) = 0.2155, exp(-7.60/2) = 0.0224; weights
= 1, 0.2155, 0.0224 divided by 1.2379 = 0.808 (M1), 0.174 (M0), 0.018 (M2). The averaged imbalance coefficient is
0.808 x (-0.1945) + 0.018 x (-0.1945) + 0.174 x 0 = -0.161, closer to the true -0.15 than M1 alone (-0.194),
because it keeps 17% weight on "no effect". One draw; not a general result.

**(6) Pilot hypothesis (candidate E3).** "The BMA forecast of the 60-s markout from features at order entry has
positive out-of-sample rank correlation with realized markouts." Statistic: Spearman correlation on held-out days,
day-block bootstrap p-value. Sample: thousands of fills (as E1); the out-of-sample segment must be one test on
data that never selected anything (V43). Trial count: the whole model space is one frozen pipeline; whether it
counts as 1 or as K configurations is the lead's call. A conservative reading counts every model in the space.

**(7) Compute.** Enumerating 2^p subsets is feasible to p of about 20 (one million least-squares fits: minutes on
the laptop); beyond that, MCMC model composition or Occam's window (Hoeting et al. section 3). CPU only.

**(8) Evidence.** Hoeting et al.: "In these examples, BMA provides improved out-ofsample predictive performance."
(non-finance examples). Avramov (2002 JFE; file `avramov_2002_bma_draft.txt`, a 2001 draft hosted on a forum site,
so the wording may differ from the published version): "the out-of-sample performance of the Bayesian approach is
superior to that of model selection criteria" for monthly stock-return predictability. These are monthly
macro-predictor results, not order-book, not cost-inclusive. No order-book BMA study was found in this search
budget.

---
# Part III. Information theory: entropy, Lempel-Ziv, approximate entropy, mutual information, transfer entropy

Common setting for sections 9 to 13. Discretize the price path of one contract into symbols. The natural choice for
MES at a fixed clock (say 1 s) is the sign of the mid-price change: s_t in {down, flat, up} = {0, 1, 2}. Most
seconds are flat. Other choices: tick-time symbols (each mid change, up or down only), quantile bins of returns
(Fiedor 2014 uses quartiles, so the maximum entropy is log2 4 = 2 bits), trade-sign sequences (buyer- or
seller-initiated, from tbbo or mbo), or the sign of top-of-book imbalance. Every discretization choice is a
configuration if it is tried against the data.

## 9. Shannon entropy of discretized price changes (and the entropy rate)

**(1) Idea.** Entropy measures how unpredictable the next symbol is. If price changes were a fair coin, nothing
about the past would help; low entropy means the symbols are concentrated (mostly flat) or patterned. The quantity
that matters for prediction is the entropy rate: the uncertainty of the next symbol given the whole past. The gap
between the marginal entropy and the entropy rate is the information the past carries about the next step.

**(2) Equations.** Shannon (1948; file `shannon_1948.txt`, Theorem 2): "The only H satisfying the three above
assumptions is of the form: H = −K ∑ pi log pi" (the minus sign extracts as a comma). With K = 1 and log base 2 the
unit is bits. For a stationary process define block entropies over words of length k,

    H_k = - sum_{w in A^k} p(w) log2 p(w),   h = lim_{k -> inf} (H_{k+1} - H_k) = lim H_k / k

where A is the alphabet (size m) and p(w) the probability of word w. Schreiber (2000, eq. 3) writes the order-k
conditional form, "the average number of bits needed to encode one additional state of the system if all previous
states are known is given by the entropy rate hI = − sum p(in+1, in(k)) log p(in+1 | in(k))" (indices mangled in
extraction). For a first-order Markov chain with transition matrix P and stationary distribution pi,
h = - sum_i pi_i sum_j P_ij log2 P_ij exactly. Estimation: plug-in frequencies. The plug-in estimator is biased low;
the standard first-order (Miller-Madow) correction adds (number of occupied cells - 1)/(2n) nats ([unverified]:
Miller 1955 not fetched; the formula is in the script for orientation only). The bias explodes when m^(k+1) is not
small compared with n.

**(3) Data.** One symbol sequence. One contract's mbp-10, mbo or tbbo data for 4 months is plenty for small k: about
84 days x 23,400 regular-hours seconds = 1.97 million one-second symbols, or several million tick-time events.
Trailing-window features (entropy over the last 5 minutes = 300 one-second symbols) are a different matter: k must
be 1 or 2 there.

**(4) Estimates.** Marginal entropy, entropy rate, and their gap (the predictable part, in bits per step).

**(5) Worked examples (measured, part F).**
- i.i.d. symbols with p = (0.1, 0.8, 0.1): H = -(2 x 0.1 x log2 0.1 + 0.8 x log2 0.8) = 2 x 0.1 x 3.3219 + 0.8 x
  0.3219 = 0.6644 + 0.2575 = 0.922 bits (maximum for three symbols: log2 3 = 1.585).
- A "bid-ask bounce" Markov chain: after a down move, P(up) = 0.20, P(down) = 0.05; after an up move the mirror;
  after flat (0.1, 0.8, 0.1). Stationary distribution (0.105, 0.789, 0.105). Marginal entropy 0.953 bits; true
  entropy rate 0.937 bits. The past is worth 0.016 bits per second: real but tiny.
- Estimates of that 0.937 by sample size n: block rate with k = 4: 0.917 (n = 2,000), 0.932 (20,000), 0.937
  (200,000). With k = 8 the plug-in collapses: 0.683 (2,000), 0.841 (20,000), 0.917 (200,000), because 3^9 = 19,683
  cells cannot be filled. The plug-in rate at k = 4 is biased low by 0.020 bits at n = 2,000 in this run (0.005 at
  20,000), the same size as the 0.016-bit effect; the first-order bias scale for the rate is
  (3^5 - 3^4)/(2n ln 2) = 0.058 bits at n = 2,000.

**(6) Pilot hypothesis (candidate I1).**
- Name: "Fills during low-entropy (patterned) seconds are more toxic." The 60-s markout of filled 1-lot passive
  orders is more adverse when the trailing 5-minute entropy rate (k = 1) of 1-s mid-change signs, measured at the
  fill time, is in its bottom tercile than when it is in its top tercile.
- Statistic: difference of mean 60-s markouts (ticks) between the two terciles, with a day-clustered (or day-block
  bootstrap) standard error. Terciles defined on a training month, applied unchanged to the rest.
- Sample: two-sample comparison of 0.1 tick with markout sd 1.5 ticks (assumed) at 80% power and 5% two-sided
  needs 2 x (2.80 x 1.5/0.1)^2 = about 3,530 fills per tercile, so about 10,600 fills in all. Whether a 1-lot
  passive order on one contract gets that many fills in four months is exactly what the pilot measures.
- Trial count: 1 if one window, one discretization and one horizon are fixed in advance; 3 if all three markout
  horizons are tested; multiply by every window length or symbol scheme tried.

**(7) Compute.** Counting words is O(n). Measured: block entropies on 200,000 symbols in well under a second; the
whole part F (dominated by the Lempel-Ziv runs) took 164 s. Two million symbols: seconds. Laptop.

**(8) Evidence.** Fiedor (2014; file `fiedor_2014_frequency_predictability.txt`), NYSE 100 stocks, quartile
symbols: "the average estimated entropy rate of daily price changes is equal to 2.04 (CTW) or 1.92 (Lempel-Ziv) out
of the theoretical maximum of 2 [...] Surprisingly the average estimated entropy for intraday price changes is
equal to 2 (CTW) or 1.90 (Lempel-Ziv), which means that high frequency price changes are more predictable than
daily price changes." The measured gaps are 0 to 0.10 bits out of 2, and one estimate exceeds the maximum (2.04 against 2), which shows the size of estimation error at that scale. Fiedor is explicit that predictability is not
profitability: "We propose that predictability is a prerequisite for profitability" and "It is conceivable that
certain trading strategies will not be able to find the patterns even" if they exist. No cost-inclusive trading
result built on entropy features was found in this search budget.

---

## 10. Lempel-Ziv complexity and entropy-rate estimation

**(1) Idea.** Read the sequence left to right and count how often you meet a pattern you have not seen before. A
random sequence keeps producing new patterns; a regular one keeps repeating old ones. Turned into a rate, this gives
an entropy-rate estimate that adapts to any memory length without choosing k.

**(2) Equations.** Fiedor (2014, eq. 5), following Kontoyiannis (1998):

    H_lz = n log2 n / sum_{i=1}^{n} Lambda_i

where n is the sequence length and, quoting, "Λi denotes the length of the shortest substring starting from time i
that has not yet been observed prior to time i, i.e. from time 1 to i − 1. It is known that for stationary ergodic
processes, Ĥ(X) converges to the entropy rate H(X) almost surely as n approaches infinity". Intuition: if the
process has entropy rate h, the longest match back into a past of length i grows like log2(i)/h, so the average
Lambda is about log2(n)/h and the ratio recovers h. Fiedor's example of the parsing: "the complexity the below
series: s = 101001010010111110 is equal to 8, since scanning it from left to right one finds 8 distinct patterns
[...] 1|0|10|01|010|0101|11|110|". The Lempel-Ziv 1976/1977 originals were not fetched ([unverified] beyond
Fiedor's description). Assumptions: stationarity and ergodicity; convergence is slow (logarithmic).

**(3) Data.** As section 9. Needs long sequences: the estimator's bias decays slowly in n.

**(4) Estimates.** The entropy rate, with no block length to choose.

**(5) Worked example (measured, part F).** Bounce chain, true rate 0.937 bits: H_lz = 0.929 (n = 2,000), 0.893
(20,000), 0.906 (200,000). i.i.d. check, true 0.922: H_lz = 0.890 (n = 200,000) against block k = 4 at 0.921. So
on these processes Lempel-Ziv is 3% low at n = 200,000, larger than the 0.016-bit effect it would be asked to
detect, and the block estimator with short k is more accurate when the memory really is short.

**(6) Pilot hypothesis.** Same as I1 with a different estimator. Using both estimators is 2 configurations. My
reading: for windows of a few hundred symbols, Lempel-Ziv is too biased to be useful; for whole-day entropy rates
(a daily regime variable) it is usable.

**(7) Compute.** My implementation (Python with `bytes.find`, O(n^2) worst case) took 0.02 s at 2,000, 1.37 s at
20,000 and 81 s at 200,000 symbols (measured). Two million symbols would take hours this way; a suffix-tree or
suffix-array implementation is O(n) or O(n log n) and would take seconds. Laptop either way, after a rewrite.

**(8) Evidence.** Fiedor (2014), above: Lempel-Ziv and CTW agree ("both used algorithms are indeed highly
correlated"), and both say stock price changes are close to maximal entropy. No profitability evidence.

---

## 11. Approximate entropy (ApEn) and sample entropy (SampEn)

**(1) Idea.** For real-valued series: take every run of m consecutive values, count how many other runs are within
a tolerance r of it, then see how many of those matches still match when extended to m + 1 values. If close
patterns stay close, the series is regular (low ApEn); if they diverge, it is irregular (high ApEn).

**(2) Equations** (Delgado-Bonal and Marshak 2019 tutorial, file `delgado_bonal_2019_apen_sampen.txt`, eqs. 25 to
29; spaces inside symbols are from the XML extraction). With template vectors x_m(i) = (x_i, ..., x_{i+m-1}),
distance d = max absolute difference, and C_i^m(r) the fraction of templates within r of x_m(i) (self-match
included):

    Phi^m(r) = (1/(N - m + 1)) sum_i log C_i^m(r),   ApEn(m, r, N) = Phi^m(r) - Phi^{m+1}(r)
    SampEn(m, r, N) = - log [ (number of pairs i != j matching for m + 1 points) / (number of pairs matching for m points) ]

Quote of eq. 27's structure: "S a m p E n ( m , r , N ) = − log ∑ i = 1 N − m ∑ j = 1 , j ≠ i N − m [ number of
times that d [ | x m + 1 ( j ) − x m + 1 ( i ) | ] < r ] ∑ [...] [ number of times that d [ | x m ( j ) − x m ( i ) |
] < r ]". The differences: "SampEn does not allow self-counting while ApEn does". Parameters: m = 2 and
r = 0.2 standard deviations are the usual defaults; the tutorial warns the ranking of series can flip with r
("If we chose r = 0.08 σ , then the order of the randomness would be 1888 > 1878 > 1938. A value of r = 0.10 σ
would give us 1878 > 1888 > 1938"). Pincus (1991, abstract only, file `pincus_1991_apen_pmc.html.txt`): ApEn "can
classify complex systems, given at least 1000 data values". Assumptions: stationarity within the window; r
relative to the window's own standard deviation.

**(3) Data.** A real-valued series, for example 1-s returns or order-flow imbalance. Windows need about 1,000 points
or more, so a trailing ApEn of 1-s data covers at least 17 minutes.

**(4) Estimates.** A regularity index; it is not a calibrated entropy rate in bits.

**(5) Worked example (measured, part F, m = 2, r = 0.2 sd).** i.i.d. normal: ApEn 1.897 (n = 2,000) but 2.256
(n = 20,000); SampEn 2.171 and 2.189. AR(1) with coefficient 0.5: ApEn 1.862 and 2.132; SampEn 2.087 and 2.053.
ApEn moved by 0.36 with sample size alone, ten times the iid-versus-AR(1) difference at n = 2,000 (0.035). SampEn
is stable in n and separates the two processes by 0.08 to 0.14. The tutorial's "Due to its theoretical definition,
ApEn is a biased statistic" is visible here.

**(6) Pilot hypothesis.** A variant of I1 with SampEn of 1-s returns over a trailing 20-minute window. It adds one
configuration per (m, r, window) tried. Prefer SampEn to ApEn.

**(7) Compute.** O(n^2) naive, O(n log n) with a k-d tree; measured 1.2 to 1.3 s per window of 20,000 points with
scipy's cKDTree. A rolling window recomputed every second over four months is millions of windows; recompute every
minute instead (about 33,000 windows of 1,200 points, minutes of CPU). Laptop.

**(8) Evidence.** The tutorial is methodological (physiology and climate examples). No finance out-of-sample or
cost-inclusive result was found in this search budget.

---

## 12. Mutual information (MI)

**(1) Idea.** MI measures how much knowing X reduces uncertainty about Y, in any form, linear or not. It is zero
exactly when X and Y are independent. As a feature screen it asks: does this book variable at order entry carry any
information about the later markout?

**(2) Equations.** Schreiber (2000): "MIJ = HI + HJ − HIJ ≥ 0. Note that MIJ is symmetric under the exchange of I
and J and therefore does not contain any directional sense." For continuous variables the Kraskov, Stögbauer and
Grassberger (2004; file `kraskov_2004_mi.txt`) estimator 1 is (their eq. 8):

    I(X, Y) = psi(k) - < psi(n_x + 1) + psi(n_y + 1) > + psi(N)

where psi is the digamma function, N the sample size, eps_i the max-norm distance from point i to its k-th nearest
neighbour in the joint (x, y) space, n_x(i) and n_y(i) the numbers of points strictly within eps_i of point i in the
x and y marginals, and <.> the average over i. Quote: "they are data efficient [...] adaptive (the resolution is
higher where data are more numerous), and have minimal bias". For jointly Gaussian X, Y with correlation rho,
I = -(1/2) ln(1 - rho^2) nats.

**(3) Data.** Pairs (feature at entry, outcome) for every fill or every second. One contract, four months: enough
for single features; MI between high-dimensional feature sets needs far more.

**(4) Estimates.** Dependence strength in nats or bits, including nonlinear dependence that a correlation misses.

**(5) Worked example (measured, part G).** Gaussian rho = 0.3: true MI = -0.5 ln(1 - 0.09) = 0.0472 nats. KSG
(k = 3): 0.076 (n = 2,000), 0.0472 (20,000), 0.0500 (100,000). One draw each; the n = 2,000 value shows how noisy a
small sample is.

**(6) Pilot hypothesis.** MI is a screening tool, not a hypothesis. If the frozen pipeline uses an MI screen to pick
features, every feature screened is a configuration that selection touched, and counts into N. A cleaner design:
fix the features in advance and use MI only as a reported diagnostic.

**(7) Compute.** k-d tree, roughly O(N log N): measured 1.1 s at 20,000 and 12.3 s at 100,000 (single thread). Two
million points per feature: minutes. Laptop.

**(8) Evidence.** Kraskov et al. test on synthetic data and ICA. No finance trading result with MI features was
found in this search budget.

---

## 13. Transfer entropy (Schreiber 2000) and lead-lag tests

**(1) Idea.** Transfer entropy from J to I asks: once I know I's own past, does J's past still help predict I's next
step? It is a directional, nonlinear version of Granger causality. For lead-lag (does ES lead MES; does order flow
lead price), it measures the information that flows from the leader to the follower.

**(2) Equations.** Schreiber (2000; file `schreiber_2000_transfer_entropy.txt`, eq. 4):

    T_{J->I} = sum p(i_{n+1}, i_n^(k), j_n^(l)) log [ p(i_{n+1} | i_n^(k), j_n^(l)) / p(i_{n+1} | i_n^(k)) ]

where i_n^(k) = (i_n, ..., i_{n-k+1}) is I's last k states and j_n^(l) J's last l states. Quote: "In the absence of
information flow from J to I, the state of J has no influence on the transition probabilities on system I. The
incorrectness of this assumption can again be quantified by a Kullback entropy (1) by which we define the transfer
entropy" and "TJ→I is now explicitly non-symmetric since it measures the degree of dependence of I on J and not
vice versa." Equivalently T = H(I_{n+1} | I past) - H(I_{n+1} | I past, J past) (Bongiorno and Challet 2022, eq. 1;
file `te_leadlag_pvalues_2022.txt`).

Inference, three routes:
- *Asymptotic chi-square* (Bongiorno and Challet 2022, eq. 6): 2 T TE -> chi^2(nu) under the null (T here is the
  sample length and TE in nats), with nu = (n_A - 1) n_A (n_B - 1) for k = l = 1 and alphabet sizes n_A, n_B
  (the extracted line reads "ν = nA nA − 1 nB − 1"; I read it as (n_A - 1) n_A^k (n_B^l - 1), which reduces to the
  same at k = l = 1). Quote: "Refs. [3, 8] show that the TEB→A converges to a chi-square distribution for binary
  states and Markovian systems with constant numbers of symbols per time step."
- *Gaussian case*: Barnett, Barrett and Seth (2009; file `barnett_2009_granger_te.txt`, eq. 13): "if all processes
  are jointly Gaussian, then F Y →X |Z = 2 T Y →X |Z so that Granger causality and transfer entropy are equivalent
  up to a factor of 2." So a linear Granger test is TE's baseline; TE adds only nonlinearity.
- *Bootstrap*: Dimpfl and Peter (2012 working paper of their 2013 SNDE article; file `dimpfl_peter_2012_te.txt`)
  criticize shuffling ("shuffling the data destroys the dependencies within the univariate time series as well")
  and "bootstrap the underlying Markov process [...] whereby the dependencies between J and I are destroyed, but
  the dynamics of the series J is retained."

Assumptions: stationarity, a finite Markov order, and for chi-square a large sample relative to the number of
cells.

**(3) Data.** Two aligned symbol sequences. On one contract: trade-sign sequence (tbbo or mbo) or top-of-book
imbalance sign as J, mid-change sign as I. Lead-lag across instruments (ES to MES, or MES to MNQ) needs a second
contract in the same schema and time window: Part B buys one, so that test needs a later purchase. Asynchronous
event times need care (Bongiorno and Challet section on asynchronous series; Huth and Abergel use Hayashi-Yoshida
style cross-correlations).

**(4) Estimates.** Directional information flow in bits or nats per step; the lag at which it peaks (Bongiorno and
Challet's time-shifted TE "allows to measure the timescale at which information transfer is maximal and vanishes").

**(5) Worked example (measured, part G).** Three-symbol leader with p = (0.1, 0.8, 0.1); the follower copies the
leader's previous symbol with probability c, else draws fresh noise.
- n = 20,000, c = 0.05: TE(leader -> follower) = 0.00259 nats; 2(n - 1) TE = 103.7 against chi^2(12), p < 1e-15.
  Reverse direction: 0.00047 nats, p = 0.09. Shuffle null mean 0.00030 = nu/(2n) = 12/40,000, as the chi-square
  theory predicts for the plug-in bias.
- n = 200,000, c = 0.02: TE = 0.00044 nats, statistic 176, p < 1e-15; reverse p = 0.15.
- Sample size for 80% power at 5% (noncentral chi-square, noncentrality 2 n TE): binary symbols (nu = 2) need 4,818
  steps for TE = 0.001 nats and 48,174 for 0.0001; three symbols (nu = 12) need 8,668 and 86,680. One regular
  trading session has 23,400 one-second steps: statistical detection of a weak lead is cheap. Economic value is the
  binding constraint.

**(6) Pilot hypothesis (candidate I2).**
- Name: "Order flow leads the mid beyond our latency." TE from the 1-s sign of top-of-book imbalance (or net
  aggressor volume) over [t - 1 s, t) to the sign of the mid change over [t + 0.1 s, t + 1.1 s), the 0.1 s gap
  covering the tens of milliseconds of order latency from Vancouver to Aurora with margin, is above a
  Markov-bootstrap null; and conditioning the passive order's placement on that sign improves the 10-s markout.
- Statistic: TE with the Dimpfl-Peter Markov bootstrap p-value, then the difference in mean 10-s markout of fills
  when the signal agrees versus disagrees with the order's side (day-clustered t).
- Sample: detection needs thousands of seconds (above); the markout comparison needs the fill counts of I1.
- Trial count: each (source variable, k, l, lag gap, symbol scheme) combination tried is a configuration. A single
  pre-declared combination adds 1; a lag scan over 5 gaps adds 5.
- With a later two-contract purchase: TE from ES to MES mid changes at gaps beyond latency, same statistic.

**(7) Compute.** Plug-in TE is counting: measured 15 s for part G including 200 shuffle surrogates of 20,000 and
200,000 steps. A Markov bootstrap with 1,000 replicates on 2 million steps: minutes. Laptop.

**(8) Evidence.**
- Huth and Abergel (2014; file `huth_abergel_2014_leadlag.txt`), equities and equity index futures, tick data:
  "We reach 60% of accuracy when forecasting the next midquote variation of the lagger using only the past
  information of the leader [...] However, a naive strategy based on market orders cannot make any profit of this
  effect because of the bid/ask spread." Their conclusion keeps a door open that matters for a passive program:
  "it does not allow making money by sending market orders only but it could be used for other trading purposes
  such as market-making or best execution." They also find "the average response time of a stock after a move of
  the index future is of the order of one second", which is above this program's latency but not by much.
- Bongiorno and Challet (2022): statistically validated lead-lag networks on "tick-by-tick price changes of several
  hundreds of stocks"; no trading results.
- Dimpfl and Peter: CDS versus bond markets and VIX versus iTraxx, a price-discovery study; no trading results.
- No cost-inclusive, out-of-sample trading result using TE was found in this search budget.

---

## 14. Compute and price summary

Every method in this brief runs on the ThinkPad (20 logical CPUs, 14 GB RAM, RTX 3050 4 GB). None needs a GPU.
Measured costs come from `C2_StatsRMT_examples.json`. The rest are order-of-magnitude estimates.

| Method | Pilot-scale job | Measured or estimated cost | Machine |
|---|---|---|---|
| MP clipping, effective N | 538 x 1,250 trial matrix; 40-field book covariance | 0.025 s eigendecomposition (538); 0.25 s covariance of 1,000,000 x 40 (measured) | laptop |
| RIE, LW linear, LW nonlinear | p = 100 race | 1.16 to 3.01 ms per estimate (measured) | laptop |
| James-Stein, normal EB | K up to thousands | closed form, microseconds to milliseconds | laptop |
| Tweedie EB (Efron) | K in the thousands | milliseconds | laptop |
| Hierarchical model, MCMC | K in the hundreds | seconds to minutes (estimate) | laptop CPU |
| BMA, full enumeration | p up to about 20 | minutes (estimate) | laptop CPU |
| Block entropy, entropy rate | 2 million 1-s symbols | seconds (measured scale: under 1 s at 200,000) | laptop |
| Lempel-Ziv (my Python) | 200,000 symbols | 81 s (measured); hours at 2 million unless rewritten with a suffix array | laptop after rewrite |
| ApEn/SampEn | 33,000 windows of 1,200 points | 1.2 to 1.3 s per 20,000-point window (measured); minutes in all | laptop |
| MI (KSG) | 2 million points per feature | 12.3 s at 100,000 (measured); minutes | laptop |
| TE plus Markov bootstrap | 2 million steps, 1,000 replicates | 15 s for part G (measured); minutes | laptop |

**Cloud price check (pages fetched 2026-10-21 02:50 PDT; files `runpod_pricing.html`, `lambda_pricing.html`).**
RunPod on-demand: "RTX 4090 24 GB VRAM 41 GB RAM 6 vCPUs $ 0.89 /hr", "A100 PCIe 80 GB VRAM 117 GB RAM 8 vCPUs $ 1.79
/hr", "H100 PCIe 80 GB VRAM 188 GB RAM 16 vCPUs $ 2.89 /hr". Lambda (table headed "PRICE/GPU/HR*", with "* plus
applicable sales tax/VAT/GST"): "NVIDIA A100 PCIe 40 GB 120 900 GiB 1 TiB SSD $1.99" per GPU-hour.

What it would cost if the lead moved any of this off the laptop anyway. The largest job above is a hierarchical
MCMC fit or a TE bootstrap sweep, under an hour of CPU. A 4-hour RunPod RTX 4090 session is 4 x 0.89 = $3.56; a
4-hour A100 PCIe 80 GB session is 4 x 1.79 = $7.16; on Lambda, 4 x 1.99 = $7.96 per A100 40 GB GPU before tax.
None of these methods uses a GPU, so the real speed-up from a cloud box would come from more CPU cores, not from the
card. The cheaper fix in every case is better code on the laptop (a suffix-array Lempel-Ziv; vectorized counting
for TE). My recommendation: no cloud spend for anything in this brief.

---

## 15. Candidate hypotheses for the lead (inputs, not declarations)

All markout figures are in ticks, net of fees, for a 1-lot passive order on one contract. The sample sizes assume
a 60-s markout standard deviation of 1.5 ticks. That is an assumption, not a measurement; the pilot measures it.
The "Adds to N" column gives what each would add to the trial count if registered as written. Where a range is
given, the lead picks the grid.

| ID | Hypothesis | Test statistic | Sample needed | Adds to N |
|---|---|---|---|---|
| R1 | Effective number of independent configurations in the pilot grid is below the raw count (Bailey-López de Prado N_hat, MP count, entropy rank) | the three estimates from the daily markout-P&L matrix | T well above K (q < 0.5): K <= 40 with 84 days | 0 (diagnostic; never lowers the N used in a verdict unless pre-registered) |
| E1 | Empirical-Bayes posterior of the 60-s net markout across the K grid configurations; the top configuration's posterior P(theta > 0) | tau_hat^2 with parametric-bootstrap p; posterior P(theta_top > 0); held-out calibration within 2 SE | several hundred fills per configuration; 1,766 fills for one 0.1-tick test at 80% power, 3,092 at K = 12 (Bonferroni), 3,842 at K = 50 (measured) | K (every configuration counts) |
| E2 | Partial pooling across families gives a positive posterior net markout for at least one family | posterior P(theta_family > 0), out-of-sample check as E1 | as E1, and >= 3 families | every configuration in every family |
| E3 | BMA forecast of the 60-s markout from entry features ranks realized markouts out of sample | Spearman correlation on held-out days, day-block bootstrap p | thousands of fills | 1 (frozen pipeline) to every model in the space (conservative); lead's call |
| I1 | Fills in low-entropy (bottom tercile, 5-min entropy rate of 1-s mid-change signs) seconds have worse 60-s markouts than top-tercile fills | difference in mean markouts, day-clustered SE; terciles fixed on a training month | about 3,530 fills per tercile, about 10,600 in all, for a 0.1-tick gap | 1 (one window, one horizon); 3 for three horizons; times each window or symbol scheme |
| I1-LZ | As I1 with the Lempel-Ziv entropy estimator | as I1 | as I1 | +1 per estimator |
| I1-SE | As I1 with SampEn of 1-s returns over a 20-min window | as I1 | as I1 | +1 per (m, r, window) |
| I2 | Order-flow sign leads the mid beyond latency (gap 0.1 s); conditioning placement on it improves the 10-s markout | TE with Dimpfl-Peter Markov-bootstrap p; then the 10-s markout difference agree versus disagree, day-clustered t | thousands of seconds for TE detection; fill counts as I1 for the markout step | 1 if one (source, k, l, gap, symbols) is fixed; 5 for a five-gap scan |
| (MI) | No hypothesis: MI only as a reported diagnostic on pre-fixed features | - | - | 0 if diagnostic; every screened feature if MI selects features |

The two that most directly use the pilot's own outputs are E1 (a selection rule for the pilot grid) and I2 (a
placement signal tied to latency). I1 is cheap but the published effect sizes for entropy are tiny (section 9).

---

## 16. Verdicts per method (for this program)

| Method | Verdict | Reason |
|---|---|---|
| Marchenko-Pastur law, eigenvalue clipping | skip for the pilot; maybe as a diagnostic on the trial matrix | One contract has no cross-section: with 40 book fields and about 2 million 1-s snapshots the noise band is 1 +- 0.009 (section 1). On the trial matrix it gives an effective-N diagnostic (R1), but the MP factor count is badly anti-conservative as N (5 against a Monte Carlo-matched 112 in the measured design) and must never stand in for N. |
| Rotationally invariant estimator (Bun, Bouchaud and Potters 2017) | skip | Same reason: needs many assets. Evidence is out-of-sample portfolio risk on stock panels with N >= 100, not returns. Revisit only if a multi-contract passive-order allocation is ever built. |
| Ledoit-Wolf linear shrinkage | maybe (as a default regularizer, not a hypothesis) | Useful only if the frozen pipeline fits a linear markout model on many features with a few thousand fills; there q = p/n is small (for example 64/5,000 = 0.013) and the gain is modest. Cheap and standard. Adds no hypothesis and no trials if fixed in advance. |
| Ledoit-Wolf nonlinear shrinkage | skip | Built for large p/n; no cross-section here. Evidence is stock-portfolio variance. |
| James-Stein | use (as the simplest form of E1) | Closed form; directly shrinks the grid's per-configuration markouts toward the grand mean. It is a theorem about total squared error, not about the selected best (Andrews et al.), so it complements the DSR rather than replacing it. |
| Empirical-Bayes shrinkage of many strategies' Sharpe ratios or markouts | use | The Bayesian answer to the winner's curse that the DSR answers by deflation. The finance evidence is cross-sectional equities: shrinkage of published anomalies is small (Chen and Zimmermann), EB-selected data-mined strategies held up out of sample before 2004 and weakened after (Chen and Dim, gross of costs). Must be declared with the grid; every configuration still counts into N; the lead decides whether a DSR gate stays on top (my reading: keep both). |
| Hierarchical (multilevel) models | maybe | Needs at least 3 families and several hundred fills per configuration. Jensen, Kelly and Pedersen show joint estimation increases discoveries, so it is less conservative than Holm when families are strong. Use only with the family structure and priors frozen before data. |
| Bayesian model averaging | maybe, leaning skip | Relevant only if the traded model is a linear markout regression with model uncertainty. Evidence is non-finance examples and monthly stock-return predictability (Avramov), not order-book data and not cost-inclusive. Under V43 the whole averaged model space is one frozen pipeline, and counting it as 1 trial is the lead's call. |
| Shannon entropy and entropy rate of discretized price changes | maybe (one pre-declared feature, I1) | Cheap and well defined. Published estimates put stock price changes within 0 to 0.10 bits of maximal entropy (Fiedor), close to estimation error. Fiedor states that predictability is not profitability. No cost-inclusive trading result was found. |
| Lempel-Ziv complexity | skip | Biased in short windows; highly correlated with CTW (Fiedor); in the worked example it is biased low where the block estimator is not, so it adds nothing over I1 but a trial. Usable only as a whole-day regime variable. |
| Approximate entropy (ApEn) | skip | Biased by self-matches (Delgado-Bonal and Marshak); rankings flip with the tolerance r. |
| Sample entropy (SampEn) | maybe, as a variant only | Better than ApEn, but it adds a configuration per (m, r, window) and has no finance evidence. Prefer one entropy feature (I1) to several. |
| Mutual information (KSG estimator) | use as a diagnostic only | Good nonlinear dependence measure, low bias (Kraskov et al.). Used to select features, every screened feature counts into N; used as a report on pre-fixed features, it adds nothing. No finance trading evidence. |
| Transfer entropy (Schreiber 2000) and lead-lag tests | maybe, leaning use (I2) | The only information-theory tool tied to the latency question. Huth and Abergel find 60% accuracy for lead-lag on tick data but no profit with market orders, and leave market making open; the response time (about 1 s) is above this program's tens of milliseconds, but not by much. For Gaussian data TE equals Granger causality up to a factor of 2 (Barnett et al.), so a linear Granger test is the baseline. No cost-inclusive out-of-sample TE trading result was found. |

**Overall.** For a one-contract order-book program, RMT does not apply to the trading side. Its live uses are a
diagnostic effective N for the trial matrix and Ledoit-Wolf as a routine regularizer. The Bayesian part (James-Stein,
empirical Bayes, hierarchical pooling) matters most, and it matters on the multiple-testing side: it estimates how
good the selected pilot configuration really is, which the DSR and Holm only gate. The information-theory part
offers one cheap feature test (I1) and one latency-linked lead-lag test (I2). The published evidence says
predictability measured this way does not by itself pay the spread.

---

## 17. References

Bibliographic details (journal, volume, pages) are given from the saved files' title pages where those show them.
Where a saved file is a preprint or working paper, I name both. Volume and page numbers marked (vp) come from my
own knowledge and were not checked against a publisher page in this session.

1. Andrews, I., Kitagawa, T. and McCloskey, A. (2018). Inference on winners. CeMMAP working paper CWP73/18
   (published version: Quarterly Journal of Economics 139(1), 2024 (vp)). File `andrews_kitagawa_mccloskey_2018_winners.pdf`.
2. Avramov, D. (2002). Stock return predictability and model uncertainty. Journal of Financial Economics 64(3),
   423-458 (vp). File `avramov_2002_bma_draft.pdf` (a 2001 draft on a forum host; weak provenance).
3. Bailey, D. H. and López de Prado, M. (2014). The deflated Sharpe ratio: correcting for selection bias, backtest
   overfitting and non-normality. Journal of Portfolio Management 40(5), 94-107 (vp). File
   `bailey_lopezdeprado_2014_dsr.pdf`.
4. Bailey, D. H., Borwein, J. M., López de Prado, M. and Zhu, Q. J. (2017). The probability of backtest overfitting.
   Journal of Computational Finance 20(4), 39-69 (vp). File `bailey_etal_pbo.pdf`.
5. Barnett, L., Barrett, A. B. and Seth, A. K. (2009). Granger causality and transfer entropy are equivalent for
   Gaussian variables. Physical Review Letters 103, 238701 (vp). arXiv 0910.4514. File `barnett_2009_granger_te.pdf`.
6. Bongiorno, C. and Challet, D. (2022). Statistical inference of lead-lag at various timescales between
   asynchronous time series from p-values of transfer entropy. arXiv 2206.10173. File `te_leadlag_pvalues_2022.pdf`.
7. Bun, J., Bouchaud, J.-P. and Potters, M. (2017). Cleaning large correlation matrices: tools from random matrix
   theory. Physics Reports 666, 1-109 (vp). arXiv 1610.08104. File `bun_bouchaud_potters_2017_cleaning.pdf`.
8. Chen, A. Y. (2024). Do t-stat hurdles need to be raised? Identification of publication bias in the cross-section
   of stock returns. arXiv 2204.10275. File `chen_tstat_hurdles.pdf`.
9. Chen, A. Y. and Dim, C. High-throughput asset pricing. arXiv 2311.10685v3. File `chen_dim_high_throughput.pdf`.
10. Chen, A. Y. and Zimmermann, T. Publication bias in asset pricing research. arXiv 2209.13623. File
    `chen_zimmermann_pubbias_eb.pdf`.
11. Delgado-Bonal, A. and Marshak, A. (2019). Approximate entropy and sample entropy: a comprehensive tutorial.
    Entropy 21(6), 541. File `delgado_bonal_2019_apen_sampen.xml` (Europe PMC full text, PMC7515030).
12. Dimpfl, T. and Peter, F. J. (2012). Using transfer entropy to measure information flows between financial
    markets. SFB 649 discussion paper 2012-051, Humboldt University Berlin (published in Studies in Nonlinear
    Dynamics and Econometrics 17(1), 2013 (vp)). File `dimpfl_peter_2012_te.pdf`.
13. Efron, B. (2011). Tweedie's formula and selection bias. Journal of the American Statistical Association
    106(496), 1602-1614 (vp). File `efron_2011_tweedie.pdf`.
14. Efron, B. and Morris, C. (1977). Stein's paradox in statistics. Scientific American 236(5), 119-127 (vp). File
    `efron_morris_1977_sciam.pdf` (scanned image, no text layer; not quoted).
15. Fiedor, P. (2014). Frequency effects on predictability of stock returns. arXiv 1310.5540. File
    `fiedor_2014_frequency_predictability.pdf`.
16. Harvey, C. R. and Liu, Y. (2015). Backtesting. Journal of Portfolio Management 42(1), 13-28 (vp). File
    `harvey_liu_2015_backtesting.pdf`.
17. Hoeting, J. A., Madigan, D., Raftery, A. E. and Volinsky, C. T. (1999). Bayesian model averaging: a tutorial.
    Statistical Science 14(4), 382-417 (vp). File `hoeting_1999_bma.pdf`.
18. Huth, N. and Abergel, F. (2014). High frequency lead/lag relationships: empirical facts. Journal of Empirical
    Finance 26, 41-58 (vp). arXiv 1111.7103. File `huth_abergel_2014_leadlag.pdf`.
19. James, W. and Stein, C. (1961). Estimation with quadratic loss. Proceedings of the Fourth Berkeley Symposium on
    Mathematical Statistics and Probability, vol. 1, 361-379 (vp). [Not fetched: Project Euclid returned a bot
    page.]
20. Jensen, T. I., Kelly, B. and Pedersen, L. H. (2021 working paper, 2021-01-28 version). Is there a replication
    crisis in finance? (published in Journal of Finance 78(5), 2023 (vp)). File
    `jensen_kelly_pedersen_2021_replication.pdf`.
21. Kontoyiannis, I. (1998), cited through Fiedor (2014) for the Lempel-Ziv entropy-rate estimator. [unverified: not
    fetched.]
22. Kraskov, A., Stögbauer, H. and Grassberger, P. (2004). Estimating mutual information. Physical Review E 69,
    066138 (vp). arXiv cond-mat/0305641. File `kraskov_2004_mi.pdf`.
23. Laloux, L., Cizeau, P., Bouchaud, J.-P. and Potters, M. (1999). Noise dressing of financial correlation
    matrices. Physical Review Letters 83(7), 1467-1470 (vp). arXiv cond-mat/9810255. File
    `laloux_1999_noise_dressing.pdf`.
24. Ledoit, O. and Péché, S. (2011), cited through Ledoit and Wolf (2020) for the oracle nonlinear shrinkage formula.
    [unverified: not fetched.]
25. Ledoit, O. and Wolf, M. (2004a). Honey, I shrunk the sample covariance matrix. Journal of Portfolio Management
    30(4), 110-119 (vp). File `ledoit_wolf_2004_honey.pdf`.
26. Ledoit, O. and Wolf, M. (2004b). A well-conditioned estimator for large-dimensional covariance matrices. Journal
    of Multivariate Analysis 88(2), 365-411 (vp). File `ledoit_wolf_2004_jmva.pdf`.
27. Ledoit, O. and Wolf, M. (2017). Nonlinear shrinkage of the covariance matrix for portfolio selection: Markowitz
    meets Goldilocks. Review of Financial Studies 30(12), 4349-4388 (vp). File `ledoit_wolf_2017_goldilocks.pdf`.
28. Ledoit, O. and Wolf, M. (2020). Analytical nonlinear shrinkage of large-dimensional covariance matrices. Annals
    of Statistics 48(5) (vp). University of Zurich working paper 264. File `ledoit_wolf_analytical_nls.pdf`.
29. Lempel, A. and Ziv, J. (1976). On the complexity of finite sequences. IEEE Transactions on Information Theory 22(1)
    (vp). [unverified: not fetched; used only through Fiedor (2014).]
30. Miller, G. A. (1955), the Miller-Madow bias correction. [unverified: not fetched.]
31. Pantaleo, E., Tumminello, M., Lillo, F. and Mantegna, R. N. (2011). When do improved covariance matrix
    estimators enhance portfolio optimization? An empirical comparative study of nine estimators. Quantitative
    Finance 11(7), 1067-1080 (vp). arXiv 1004.4272. File `pantaleo_2011_covariance.pdf`.
32. Pincus, S. M. (1991). Approximate entropy as a measure of system complexity. Proceedings of the National Academy
    of Sciences 88(6), 2297-2301 (vp). File `pincus_1991_apen_pmc.html` (abstract page only; the PDF fetches
    returned bot pages).
33. Plerou, V., Gopikrishnan, P., Rosenow, B., Amaral, L. A. N., Guhr, T. and Stanley, H. E. (2002). Random matrix
    approach to cross correlations in financial data. Physical Review E 65, 066126 (vp). arXiv cond-mat/0108023.
    File `plerou_2002_rmt.pdf`.
34. Schreiber, T. (2000). Measuring information transfer. Physical Review Letters 85(2), 461-464 (vp). arXiv
    nlin/0001042. File `schreiber_2000_transfer_entropy.pdf`.
35. Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal 27, 379-423 and
    623-656 (vp). File `shannon_1948.pdf`.
36. RunPod. GPU cloud pricing page, https://www.runpod.io/pricing, fetched 2026-10-21 09:50:34 UTC. File
    `runpod_pricing.html`.
37. Lambda. GPU cloud pricing page, https://lambda.ai/pricing, fetched 2026-10-21 09:50:36 UTC. File
    `lambda_pricing.html`.
38. Program code: `screening/stage_e_verdict.py` (`dsr_table`), read for how the program computes the DSR.

---

## 18. Evidence table

Every quote below was machine-checked against the saved file named in its row (letters and digits only, case
folded, so pdftotext line breaks and hyphenation do not block a match). Script:
`work/C2_StatsRMT/C2_StatsRMT_evidence.py`; result: 58 rows, 0 failures (run 2026-10-21 05:15 PDT, from the output file's mtime). Files are
under `reports/stage_e28_briefs/pages/C2_StatsRMT/` except the program code row. Where a `.txt` file is named, the
`.raw.txt` reading-order version beside it was also searched, because the layout `.txt` splits two-column pages.

| # | Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|---|
| 1 | DSR deflates by the number of independent trials and the variance of trial results | Bailey and López de Prado 2014 | "the number of independent trials carried out (N); ii) the variance of the backtest results" | `bailey_lopezdeprado_2014_dsr.txt` |
| 2 | DSR's N means independent trials, not raw trials | Bailey and López de Prado 2014 | "It is critical to understand that the N used to compute" | `bailey_lopezdeprado_2014_dsr.txt` |
| 3 | DSR paper links its correction to shrinkage and regression to the mean | Bailey and López de Prado 2014 | "regression to the mean" | `bailey_lopezdeprado_2014_dsr.txt` |
| 4 | Program's DSR uses the population variance of trial Sharpe ratios | repo code | "the Sharpe variance over ``variance_over`` (population variance)" | `screening/stage_e_verdict.py` |
| 5 | Top S&P eigenvalue far above the MP edge | Laloux et al. 1999 | "25 times larger than the predicted" | `laloux_1999_noise_dressing.txt` |
| 6 | MP fits most of the S&P spectrum; top 6% exceed the edge | Laloux et al. 1999 | "accounts quite satisfactorily for 94% of the spectrum, while the 6% highest eigenvalues still exceed the theoretical upper edge" | `laloux_1999_noise_dressing.txt` |
| 7 | Most US stock correlation eigenvalues lie in the RMT band | Plerou et al. 2002 | "a majority of the eigenvalues of C fall within the RMT bounds" | `plerou_2002_rmt.txt` |
| 8 | Cleaning lowers out-of-sample risk on stock panels | Bun, Bouchaud and Potters 2017 | "it is always better to use a cleaned correlation matrix" | `bun_bouchaud_potters_2017_cleaning.txt` |
| 9 | Effective q differs from N/T in financial data | Bun, Bouchaud and Potters 2017 | "one often observes empirically, especially with financial data, that the value of q = N/T" | `bun_bouchaud_potters_2017_cleaning.txt` |
| 10 | RIE best in all but one case; LW linear wins once | Bun, Bouchaud and Potters 2017 | "in all cases but one (Minimum risk portfolio in Japan, where the LW linear shrinkage outperforms)" | `bun_bouchaud_potters_2017_cleaning.txt` |
| 11 | Negative: no estimator beats sample covariance long-only with T > N | Pantaleo et al. 2011 | "when short selling is not allowed and T > N , the considered methods are unable to outperform the sample covariance in terms of realized risk" | `pantaleo_2011_covariance.txt` |
| 12 | Sample covariance should not be used for optimization | Ledoit and Wolf 2004 (JPM) | "nobody should be using the sample covariance matrix for the purpose of portfolio optimization" | `ledoit_wolf_2004_honey.txt` |
| 13 | Shrinkage cuts tracking error, raises information ratio | Ledoit and Wolf 2004 (JPM) | "shrinkage reduces tracking error relative to a benchmark index, and substantially increases the realized information ratio of the active portfolio manager" | `ledoit_wolf_2004_honey.txt` |
| 14 | Optimal shrinkage intensity derivation (first-order condition) | Ledoit and Wolf 2004 (JMVA) | "The first order condition is" | `ledoit_wolf_2004_jmva.txt` |
| 15 | Nonlinear shrinkage dominates linear in stock backtests | Ledoit and Wolf 2017 | "In backtests with historical stock return data, it performs better than previous proposals and, in particular, it dominates linear shrinkage." | `ledoit_wolf_2017_goldilocks.txt` |
| 16 | Analytical NLS is fast and scales to p = 10,000 | Ledoit and Wolf 2020 | "typically 1,000 times faster with the same accuracy, and accommodates covariance matrices of dimension up to 10, 000" | `ledoit_wolf_analytical_nls.txt` |
| 17 | Oracle nonlinear formula is due to Ledoit and Péché | Ledoit and Wolf 2020 | "was first discovered by Ledoit and Péché (2011, Theorem 3)" | `ledoit_wolf_analytical_nls.txt` |
| 18 | Largest estimates overstate their means (selection bias) | Efron 2011 | "The largest few of the zi ’s are likely to substantially overestimate their corresponding µi ’s, this being an example of selection bias, or regression to the mean." | `efron_2011_tweedie.txt` |
| 19 | Normal prior gives Tweedie posterior mean (1 - 1/V) z | Efron 2011 | "Tweedie’s formula becomes E{µ/z} = (1 − 1/V )z." | `efron_2011_tweedie.txt` |
| 20 | James-Stein replaces 1/V by an unbiased estimate | Efron 2011 | "substitutes the unbiased estimator" | `efron_2011_tweedie.txt` |
| 21 | EB bias correction worked in Efron's examples | Efron 2011 | "the empirical Bayes bias correction lˆi0 was quite effective in both groups" | `efron_2011_tweedie.txt` |
| 22 | Shrinkage toward the prior is what removes false discoveries | Jensen, Kelly and Pedersen 2021 (WP) | "Reduction of false discoveries is achieved first by shrinking estimates toward the prior." | `jensen_kelly_pedersen_2021_replication.txt` |
| 23 | Hierarchical model shrinks toward cluster means | Jensen, Kelly and Pedersen 2021 (WP) | "each alpha is shrunk toward its cluster mean (i.e., toward related factors), in addition to being shrunk toward the prior of zero." | `jensen_kelly_pedersen_2021_replication.txt` |
| 24 | Joint estimation increases discoveries | Jensen, Kelly and Pedersen 2021 (WP) | "the increased precision from joint estimation has the opposite effect of enhancing statistical power and thus increases discoveries." | `jensen_kelly_pedersen_2021_replication.txt` |
| 25 | Factors replicate out-of-sample internationally | Jensen, Kelly and Pedersen 2021 (WP) | "covering 93 countries" | `jensen_kelly_pedersen_2021_replication.txt` |
| 26 | Naive inference on the selected best is biased | Andrews, Kitagawa and McCloskey 2018 (WP) | "conventional estimates are biased and conventional confidence intervals are unreliable" | `andrews_kitagawa_mccloskey_2018_winners.txt` |
| 27 | Winners problem covers the best backtested strategy | Andrews, Kitagawa and McCloskey 2018 (WP) | "the best-performing investment strategy based on historical data" | `andrews_kitagawa_mccloskey_2018_winners.txt` |
| 28 | EB shrinkage of published anomalies is only 10-15% | Chen and Zimmermann (arXiv 2209.13623) | "the average correction (shrinkage) accounts for only 10 to 15 percent of in-sample mean returns" | `chen_zimmermann_pubbias_eb.txt` |
| 29 | EB-selected data-mined strategies earn out of sample (gross) | Chen and Dim (arXiv 2311.10685v3) | "earns out-of-sample returns of 5.7% per year over the 1983-2020 sample" | `chen_dim_high_throughput.txt` |
| 30 | Negative: EB accuracy worse post-2004 | Chen and Dim (arXiv 2311.10685v3) | "Post-2004, EB has more difficulty with accuracy" | `chen_dim_high_throughput.txt` |
| 31 | Popular multiple-testing methods miss OOS performers | Chen and Dim (arXiv 2311.10685v3) | "Multiple testing methods popular in finance fail to identify most out-of-sample performers" | `chen_dim_high_throughput.txt` |
| 32 | EB and FDR are strongly identified from published data | Chen (arXiv 2204.10275) | "empirical Bayes shrinkage and the FDR) can be strongly identified" | `chen_tstat_hurdles.txt` |
| 33 | Multiple-testing haircut is nonlinear | Harvey and Liu 2015 | "the multiple testing haircut is nonlinear. The highest Sharpe ratios are only moderately penalized, while the marginal Sharpe ratios are heavily penalized." | `harvey_liu_2015_backtesting.txt` |
| 34 | BMA improves out-of-sample prediction (non-finance) | Hoeting et al. 1999 | "In these examples, BMA provides improved out-ofsample predictive performance." | `hoeting_1999_bma.txt` |
| 35 | BMA beats model selection for stock-return predictability | Avramov 2002 (2001 draft) | "the out-of-sample performance of the Bayesian approach is superior to that of model selection criteria" | `avramov_2002_bma_draft.txt` |
| 36 | Shannon's uniqueness theorem for H | Shannon 1948 | "three above assumptions is of the form" | `shannon_1948.txt` |
| 37 | Stock price changes near maximal entropy | Fiedor 2014 | "the average estimated entropy rate of daily price changes is equal to 2.04 (CTW) or 1.92 (Lempel-Ziv) out of the theoretical maximum of 2" | `fiedor_2014_frequency_predictability.txt` |
| 38 | Predictability is not profitability | Fiedor 2014 | "We propose that predictability is a prerequisite for profitability" | `fiedor_2014_frequency_predictability.txt` |
| 39 | LZ and CTW estimates agree | Fiedor 2014 | "both used algorithms are indeed highly correlated" | `fiedor_2014_frequency_predictability.txt` |
| 40 | LZ estimator definition | Fiedor 2014 | "denotes the length of the shortest substring starting from time i that has not yet been observed prior to time i" | `fiedor_2014_frequency_predictability.txt` |
| 41 | ApEn needs about 1000 points | Pincus 1991 (abstract only) | "can classify complex systems, given at least 1000 data values" | `pincus_1991_apen_pmc.html.txt` |
| 42 | ApEn is biased | Delgado-Bonal and Marshak 2019 | "Due to its theoretical definition, ApEn is a biased statistic" | `delgado_bonal_2019_apen_sampen.txt` |
| 43 | SampEn excludes self-matches | Delgado-Bonal and Marshak 2019 | "SampEn does not allow self-counting while ApEn does" | `delgado_bonal_2019_apen_sampen.txt` |
| 44 | ApEn/SampEn rankings flip with tolerance r | Delgado-Bonal and Marshak 2019 | "If we chose r = 0.08 σ , then the order of the randomness would be 1888 > 1878 > 1938" | `delgado_bonal_2019_apen_sampen.txt` |
| 45 | KSG MI estimator is data efficient and low bias | Kraskov, Stögbauer and Grassberger 2004 | "adaptive (the resolution is higher where data are more numerous), and have minimal bias" | `kraskov_2004_mi.txt` |
| 46 | MI has no direction | Schreiber 2000 | "symmetric under the exchange of I and J and therefore does not contain any directional sense" | `schreiber_2000_transfer_entropy.txt` |
| 47 | TE is directional | Schreiber 2000 | "is now explicitly non-symmetric since it measures the degree of dependence of I on J and not vice versa" | `schreiber_2000_transfer_entropy.txt` |
| 48 | Gaussian TE equals Granger causality up to factor 2 | Barnett, Barrett and Seth 2009 | "Granger causality and transfer entropy are equivalent up to a factor of 2" | `barnett_2009_granger_te.txt` |
| 49 | Markov bootstrap null for TE | Dimpfl and Peter 2012 (WP) | "whereby the dependencies between J and I are destroyed, but the dynamics of the series J is retained" | `dimpfl_peter_2012_te.txt` |
| 50 | TE p-values give the lead-lag timescale | Bongiorno and Challet 2022 (arXiv 2206.10173) | "allows to measure the timescale at which information transfer is maximal and vanishes" | `te_leadlag_pvalues_2022.txt` |
| 51 | Lead-lag predicts 60% of lagger moves | Huth and Abergel 2014 | "We reach 60% of accuracy when forecasting the next midquote variation of the lagger using only the past information of the leader" | `huth_abergel_2014_leadlag.txt` |
| 52 | Negative: lead-lag does not pay the spread with market orders | Huth and Abergel 2014 | "a naive strategy based on market orders cannot make any profit of this effect because of the bid/ask spread" | `huth_abergel_2014_leadlag.txt` |
| 53 | Lead-lag may still help market making | Huth and Abergel 2014 | "it could be used for other trading purposes such as market-making or best execution" | `huth_abergel_2014_leadlag.txt` |
| 54 | Stock response to index-future move about 1 s | Huth and Abergel 2014 | "the average response time of a stock after a move of the index future is of the order of one second" | `huth_abergel_2014_leadlag.txt` |
| 55 | Cloud GPU price: RTX 4090 | RunPod pricing page (fetched 2026-10-21) | "RTX 4090 24 GB VRAM 41 GB RAM 6 vCPUs $ 0.89 /hr" | `runpod_pricing.html.txt` |
| 56 | Cloud GPU price: A100 PCIe 80 GB | RunPod pricing page (fetched 2026-10-21) | "A100 PCIe 80 GB VRAM 117 GB RAM 8 vCPUs $ 1.79 /hr" | `runpod_pricing.html.txt` |
| 57 | Cloud GPU price: H100 PCIe | RunPod pricing page (fetched 2026-10-21) | "H100 PCIe 80 GB VRAM 188 GB RAM 16 vCPUs $ 2.89 /hr" | `runpod_pricing.html.txt` |
| 58 | Cloud GPU price: A100 PCIe 40 GB per GPU-hour | Lambda pricing page (fetched 2026-10-21) | "NVIDIA A100 PCIe 40 GB 120 900 GiB 1 TiB SSD $1.99" | `lambda_pricing.html.txt` |

---

## 19. Gaps, failures and open items

- **Not fetched or blocked:** James and Stein (1961; Project Euclid bot page), Efron and Hastie CASI and Efron LSI
  (404 at every author URL tried), the Pincus (1991) PDF (bot pages from PMC and Europe PMC; only the abstract page
  is used), the Lempel-Ziv (1976/1977) originals, Kontoyiannis (1998), Ledoit and Péché (2011), Miller (1955). Each
  claim resting on these is marked [unverified] or cited through a fetched paper that quotes it.
- **Scanned, not quoted:** Efron and Morris (1977) has no text layer and no OCR tool is installed.
- **Weak provenance:** the Avramov (2002) text is a 2001 draft hosted on a forum site; wording may differ from the
  published version.
- **Gross, not net:** the Chen and Dim EB out-of-sample returns carry no transaction-cost adjustment (a text search (grep -a) for "cost" finds only accounting variable names and one reference title).
- **No evidence at this program's scale.** In this search budget I found no out-of-sample, cost-inclusive result at
  retail latency for any method here on a single futures contract. The finance evidence is equity cross-sections
  (RMT, shrinkage, EB, hierarchical), monthly predictability (BMA), and tick-data lead-lag without profit from
  market orders (Huth and Abergel). Treat this as an absence of evidence within the budget, not as proof that the
  methods fail.
- **Assumed, not measured:** the 1.5-tick standard deviation of the 60-s markout behind every sample-size figure.
  The pilot measures it.
- **Synthetic design:** the effective-N comparison (section 1) is one synthetic correlation structure (5 clusters,
  0.6 within, 0.1 across). The ordering of the estimators may change with other structures.
- **Code:** my Lempel-Ziv implementation is O(n^2) and too slow for 2 million symbols without a rewrite.
- **Searches:** 15 of 60 WebSearch calls used; no budget notice was seen. This resumption (05:16 PDT) made no new
  web calls. It wrote sections 14 to 19 from pages already saved.
- **Decisions left to the lead:** whether a frozen BMA or hierarchical pipeline counts as 1 trial or as every model
  it contains; whether a DSR gate stays on top of an EB selection rule; whether R1 is reported at all; which of
  E1, E2, E3, I1 and I2 (if any) enter a registration.

## Corrections after review (Stage E.28, MathReviewer G4)

- MG4-10: two-level example kept at prior mean 0: tau_b^2 = 0.0211 (mean of squared family means 0.0227 minus 0.0016), kappa_b = 0.930, posteriors 0.186 / -0.012 / -0.156. The script's part D still computes the grand-mean version; see R_fix_G4.md.
- MG4-11: the k = 4 entropy-rate bias claim replaced by the measured 0.020 bits at n = 2,000 (0.005 at 20,000), the same size as the 0.016-bit effect, with the first-order scale 0.058 bits.
- MG4-12: printed timings changed to the saved JSON values (clip 1.16, LW 3.01, RIE 1.18, NLS 1.41 ms) in the compute lines, the race table and the cost table.
- MG4-14: Fiedor gaps restated as 0 to 0.10 bits, with one estimate above the maximum (section 10).
- MG4-15: citation changed to "eq. 1 (restated under eq. 2) and Appendix 1".
- MG4-16: the Chen-Dim cost search now says "grep -a" and names the one reference title (both places).
- MG4-17: the Lempel-Ziv verdict row now cites correlation with CTW only and the worked-example bias.
- MG4-18: the +7.6% overstatement is described as about 7%, of which 0.7 points is the formula's approximation.
- Not applied (style NOTE): MG4-13.

Lead note (Stage E.28, after MathReviewer G4): the examples script part_d and its JSON still hold the grand-mean values;
the text above uses the review's prior-mean-0 option (MG4-10), and the script output is superseded for that example.
