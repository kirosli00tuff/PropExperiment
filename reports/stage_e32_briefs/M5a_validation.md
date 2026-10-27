# Stage E.32 Part M5 (first half): validation and multiple-testing mathematics for the E.33 ZM discovery search

Worker: ValidationMath-OpusHigh (ROOT M5a_validation). Written 2026-10-27 from 00:25 PDT. Evidence pages and
log: reports/stage_e32_briefs/pages/M5a_validation/ (log.tsv). Scratch and calculators:
reports/stage_e32_briefs/work/M5a_validation/ (`M5a_calc.py` -> `M5a_calc_out.txt`, `M5a_calc2.py` ->
`M5a_calc2_out.txt`). No market data was read; every number below is arithmetic on the brief's standard ZM numbers,
on published formulas, or on synthetic random numbers with fixed seeds. Nothing was registered, N stays 538.

This section extends E.28 1b/1h (what the program already uses: Holm, BH, DSR, PBO/CSCV, effective N, nested CPCV)
and E.28 2.7 sections 5-6 (purged k-fold and CPCV basics: the three overlap conditions, the AFML 0.01T embargo, Li's
H + c tau rule, phi[N,k] = C(N-1, k-1), the CPCV table for N = 6..16). It does not repeat them: it adds the
horizon and session scaling, the discovery-length arithmetic (39 months), the DSR at the E.33 search sizes on
per-trade ZM statistics, and the FWER/FDR choice for a design that takes at most 3 candidates to one one-shot test.

## 0. Shared inputs and the program's own code

### 0.1 Standard quantities used in every worked example (assumptions marked)

| Quantity | Value | Where it comes from |
|---|---|---|
| ZM sigma_1m | 3.15 ticks | brief, from E.28 A0 Table 1 (2022-11..2023-10) |
| sigma_h under a random walk (ASSUMPTION: sigma_h = sigma_1m sqrt(h)) | 5 min 7.04, 15 min 12.20, 30 min 17.25, 60 min 24.40, 120 min 34.51, 240 min 48.80 ticks | `M5a_calc_out.txt` section (a); e.g. 3.15 x sqrt(15) = 3.15 x 3.873 = 12.20 |
| Market-order break-even c at Topstep | 1.59 ticks a round trip (mu*_mkt) | reports/stage_e28_ranking.md line 130: "\| 6 \| topstep \| ZM \| ... \| 0.59 \| 1.59 \| 0.86 \| 49.23 \|", columns mu*_lim, mu*_mkt, mu10K, cost/attempt (header line 123). The brief's "about 1.6" is this row. |
| Discovery trade dates T_d (2020-12-01..2024-02-29) | about 816 | 848 weekdays minus 32 assumed CBOT full closures (a holiday list I typed, not read from any data or CME page; error about +-3 dates) |
| Test-window trade dates (2017-05-01..2020-11-30, sealed) | about 899 | 936 weekdays minus an assumed 37 closures. Calendar arithmetic only; no sealed file was opened |
| Minutes per trade date | 765 overnight (19:00-07:45 CT) + 290 day (08:30-13:20 CT) = 1,055 | brief's session times [unverified here: the brief says verify; I did not fetch a CME page, which the E.32 CME rule forbids; DataFacts owns this] |
| 1-minute bar slots over discovery | 816 x 1,055 = 860,880 | arithmetic |
| Discovery length in years | 39 / 12 = 3.25 | arithmetic |

[MathReview C-1 (lead: accepted): row "Test-window trade dates": 37 closures is 6 too many; CBOT grain full closures in the window are 31 (identical date for date to the program's grains/hist2010 calendars), so the count is 936 weekdays - 31 = 905, not about 899. In f.3 (original lines 660-672) SR = z/sqrt(905) gives 0.0547/0.0707/0.0997 for z 1.645/2.128/3.0 (table has 0.0549/0.0710/0.1001), gross ticks unchanged to 2 d.p., power 0.998/0.981, 0.661/0.323, 0.373/0.116 (vs 0.998/0.98, 0.66/0.32, 0.37/0.12), and the summary (original line 758) reads 905 trades; no verdict moves.]

### 0.2 The program's implementations the lead can call (read, not run)

All signatures and docstrings were read from source on 2026-10-27; none was executed by this worker.

| Function | File:line | Signature (abridged) | What the docstring and body say |
|---|---|---|---|
| `expected_max_sharpe` | funnel/multiple_comparisons.py:63 | `(n_trials: int, sharpe_variance: float) -> float` | "E[max SR] under the null that every trial has true SR = 0. Bailey & Lopez de Prado eq. (3). ``sharpe_variance`` is the variance of the Sharpe estimates ACROSS trials; with one trial the expected maximum is 0". Body: sqrt(V) x ((1 - gamma) Z^-1[1 - 1/N] + gamma Z^-1[1 - 1/(N e)]), gamma = 0.5772156649015329. (The paper's main-text number for this is eq. (1); eq. (3) is in Appendix A.1.) |
| `deflated_sharpe_ratio` | funnel/multiple_comparisons.py:81 | `(observed_sharpe, n_observations, n_trials, sharpe_variance, skewness=0.0, kurtosis=3.0) -> dict` | "Probability the true Sharpe exceeds 0, given the trial count and return shape. ``observed_sharpe`` and ``sharpe_variance`` must be on the SAME period basis as ``n_observations`` ... ``kurtosis`` is the raw fourth standardised moment, so a normal distribution is 3.0". Body: z = (SR - SR0) sqrt(n - 1) / sqrt(1 - skew SR + 0.25 (kurt - 1) SR^2); raises on a non-positive variance term. |
| `harvey_liu_zhu_verdict` | funnel/multiple_comparisons.py:116 | `(mean, stdev, n_observations, hurdle=HLZ_HURDLE=3.0) -> dict` | "t-stat of a mean against the HLZ (2016) hurdle: t > 3.0, not the usual 2.0." |
| `probability_of_backtest_overfitting` | funnel/multiple_comparisons.py:143 | `(performance: list[list[float]], n_blocks: int = 8) -> PBOResult` | rows = strategies, columns = blocks; all C(S, S/2) symmetric splits; OOS relative rank of the IS winner = (number strictly worse + 0.5)/n_strategies; PBO = share of logits <= 0. Fewer than 2 strategies returns NaN with degenerate=True. |
| `dsr`, `dsr_table`, `pbo` | screening/stage_e_verdict.py:197, :216, :231 | `dsr(mom, n_trials, variance)`; `dsr_table(moms, variance_over, n_trials, members)`; `pbo(series)` | `dsr_table`: "the Sharpe variance over ``variance_over`` (population variance)"; `pbo`: "CSCV PBO on 8 contiguous blocks of n_days // 8 dates" (N_PBO_BLOCKS = 8, line 92). Moments use the population sd and raw kurtosis. |
| `holm_alpha_k`, `holm_tier_a` | screening/stage_e_stats.py:288, :317 | `holm_alpha_k(k_clusters: int) -> float`; `holm_tier_a(pvalues: Mapping[str, float], k_clusters: int) -> HolmResult` | "alpha_k = 0.05 / K, K the number of families with a non-empty tested set ... K in 1..9"; "Holm step-down over one family's one-sided p-values ... at family-wise 0.05 / K". FAMILY_ALPHA = 0.05 (line 103), MAX_FAMILIES = MAX_CLUSTERS + 1 (line 108). This is exactly the planner's "Holm across families" structure, already coded. |
| `holm`, `benjamini_hochberg` | strategy/research/_d1f_decisions.py:195, :207 | `holm(pvalues, alpha=HOLM_FWE)`; `benjamini_hochberg(pvalues, q=BH_Q)` | "Holm step-down: sort ascending, reject while p_(i) <= alpha / (m - i + 1)."; "BH step-up: reject ranks 1..k, k the largest rank with p_(k) <= k q / m." (outside screening/; listed for completeness) |
| `pbo_cscv`, `sharpe_variance`, `dsr_at_n` | ml_route_v2/cpcv.py:735, :761, :769 | `pbo_cscv(perf, n_blocks=PBO_BLOCKS)`; `sharpe_variance(sharpes)`; `dsr_at_n(daily, n_trials, sharpe_variance)` | perf = dates x configurations, cut into n_blocks contiguous date blocks, then passed to the funnel function; "Population variance of the configurations' daily Sharpes"; "DSR of a daily series at N trials ... daily, unannualized". Constants (ml_route_v2/constants.py:128-132): N_BLOCKS = 6, N_TEST_BLOCKS = 2 ("15 splits, 5 paths"), EMBARGO_DATES = 1, PBO_BLOCKS = 16. |

Not in the code base (0 hits, as E.28 1b found): White's Reality Check, Hansen's SPA, Romano-Wolf stepdown,
Benjamini-Yekutieli, Storey q-values, probabilistic Sharpe ratio and minimum backtest length, ONC clustering.

Consistency check of the program's DSR against the paper (section (d) below): with the paper's own example inputs
the formula above gives DSR 0.9004 at N = 100, 0.9505 at N = 46, and 0.9505 at N = 88 under normal returns,
matching the three outcomes the paper prints in text ("only a 90% chance", "0.9505", "after N=88";
`bailey_lopezdeprado_2014_dsr.pdf.txt` lines 441-446). The example's inputs sit in equation images that pdftotext
lost; the values I used (N = 100, V = 1/2 annualised, T = 1,250, skew -3, kurtosis 10, SR 2.5 annualised) are
from my memory of the paper [unverified as text], and are confirmed only indirectly, by reproducing all three
printed outcomes.

## (a) Purged and embargoed K-fold for overlapping labels of horizon h

### a.1 Core idea
A row decided at time t carries a label that looks h minutes ahead, so its information spans [t, t + h]. A training
row whose span overlaps a test row's span shares realised prices with it (purge it); a training row just after a
test block has features built from the test block's prices (embargo it). E.28 2.7 section 5 gives the three overlap
conditions and the AFML 0.01T rule; this section adds how both cuts scale with h and with ZM's session calendar, and
shows that session-aligned folds make the purge free.

### a.2 Equations
Notation: decision time t_i,0; label end t_i,1 = t_i,0 + h (clock or trading minutes, to be declared) or the trade
date's 13:20 CT close for "to close" labels; a test fold is the set of rows with decision times in [a_j, b_j]; its
label envelope is [a_j, b_j + h_max]; e is the embargo width.

1. Purge (LdP 2018, Solution #8; the three conditions reduce to one interval test for fixed-horizon labels): drop
   training row i if t_i,1 >= a_j and t_i,0 <= b_j + h_max, i.e. t_i,0 in [a_j - h, b_j + h_max].
2. Embargo (same source): "We can implement this embargo period h by setting Y_j = f[[t_j,0, t_j,1 + h]] before
   purging"; so additionally drop t_i,0 in (b_j + h_max, b_j + h_max + e]. Nothing is embargoed before a test block.
3. Rows lost per split (bar-level folds): about h before the block and h_max + e after it. Over k folds, the
   aggregate share of the sample cut is Li's (2026) "sanitization overhead k(2H + h)/T", which should be << 1
   (Li, Practical guidance item 2; there H is the label horizon and h the embargo).
4. Session alignment (worker's derivation, not from a source): if every fold is a union of whole CME trade dates
   (a trade date runs from 19:00 CT the evening before to 13:20 CT) and every label ends by its own trade date's
   13:20 close, then t_i,1 < a_j for every training row before the block and t_i,0 > b_j + h_max for every row
   after it, so the purge set is empty for any h up to "to close". The only cut left is the embargo, measured in
   trade dates. The 13:20 to 19:00 CT gap (340 minutes) is longer than every intraday horizon on the planner's list
   (5 to 240 minutes) [session times from the brief, unverified here].
5. Embargo width candidates, each in trade dates for the 39-month sample:
   - planner and program: 1 trade date (ml_route_v2 EMBARGO_DATES = 1);
   - AFML: h_emb ~ 0.01T with T the number of bars: 0.01 x 860,880 = 8,609 bar slots = 8,609 / 1,055 = 8.16 trade
     dates (and 0.01 x 816 trade dates = 8.16 if T is counted in dates: the rule is scale-free, 1% of the sample);
   - Li: H + c tau with c about 2 to 3, tau the dependence scale of the losses (not of raw returns);
   - feature lookback L (worker's conservative bound): e >= L makes every training row's features free of test-block
     prices; for a 5-20 session rolling crush beta (planner family 1) that is 5-20 trade dates.

### a.3 Worked example (h = 60 minutes, k = 10 folds, 816 trade dates)
- Fold size: 816 / 10 = 81.6 trade dates. Training per split before cuts: 816 - 81.6 = 734.4 dates.
- sigma_60 under the random-walk assumption: 3.15 x sqrt(60) = 3.15 x 7.746 = 24.40 ticks (only to show what a
  60-minute label measures; it does not enter the split).
- Bar-level folds (cut at arbitrary minutes): purge removes 60 bar slots on each side of each test block, so
  2 x 60 = 120 slots per block; over 10 folds k x 2H / T = 10 x 120 / 860,880 = 0.00139 = 0.139% of the sample.
  Negligible.
- Session-aligned folds with labels clipped at 13:20: purge removes 0 rows.
- Embargo 1 trade date after each test block: per split 1 / 734.4 = 0.136% of training rows; aggregated over the
  10 folds k x 1 / 816 = 1.23%. Li's overhead with H = 60 min and h = 1 date: 0.139% + 1.23% = 1.36%
  (`M5a_calc_out.txt` line "k=10 H=60").
- Embargo by AFML 0.01T: 8.16 dates per split = 8.16 / 734.4 = 1.11% of training rows per split.
- Embargo by a 20-session feature lookback: 20 / 734.4 = 2.7% of training rows per split.
- At h = 240 minutes and k = 10 the bar-level purge share rises to 10 x 480 / 860,880 = 0.558%, still small.
- Check (independent bound): even the largest choice (20 dates per split) leaves 714 of 734 training dates (97.3%),
  so the choice of e is a leakage question, not a sample-size question, over 39 months.

How the cuts scale: purge rows grow linearly in h (2h per boundary) and vanish under session alignment; embargo is
set by dependence (tau, feature lookback), not by h. A session boundary is the natural fold edge because labels end
there. Labels that cross the 07:45-08:30 CT pause stay within one trade date, so they do not touch a fold edge, but
their horizon must be declared in clock or trading minutes (a 60-minute label from 07:30 ends at 08:30 in clock time
and at 09:15 in trading minutes). Labels that hold across the daily halt (close-to-next-open) cross trade dates and
need a 1-date purge.

### a.4 Data it needs
Per row: decision timestamp, label end timestamp, trade date, instrument_id of the v.0 contract at t_i,0 and t_i,1
(ZM MBO bars aggregated to the decision grid), and the roll dates from the definitions schema. ZS/ZL MBP-1 features
use the same trade-date key. No outcome is needed to build the splits; they can be frozen and hashed before any
label is computed.

### a.5 Leakage and look-ahead traps, each with a test
| Trap | Test that catches it |
|---|---|
| A label crosses a fold edge (overnight-hold labels, a fold cut mid-session) | Unit test on timestamps only: for every split assert max(t_i,1 over training rows before the block) < a_j and min(t_i,0 over training rows after) > b_j + h_max + e |
| A label straddles a v.0 roll (two contracts in one return) | Assert instrument_id(t_i,0) == instrument_id(t_i,1) for every labelled row; count and drop the rest before freezing |
| Transforms fitted on the full sample (z-scores, winsorization quantiles, the crush hedge ratio, PCA) | Perturbation test: scramble the prices inside one test block, rebuild the training-fold features, require them bit-identical |
| Features use data after t (bar close used at bar open; a USDA number before its release time) | Truncation test: recompute features on data cut at t for 1,000 random t and require equality with the full-data features; the program's planted-future canaries (E.28 1h V9) are the template |
| Embargo too short for slow features | Pre-declared embargo-sensitivity diagnostic: CV score at e = 1, 5 and 20 dates; a material drop as e grows flags leakage (report only; never used to select) |
| Inner tuning on the reporting folds | Nested CV, as ml_route_v2's nested CPCV already asserts (E.28 1h V5) |
| Leak through the protocol as a whole | E.28 2.7 section 5.6 placebo test H-CV0 (labels from another session must give AUC 0.5 +- 2 SE) |

[MathReview C-3 (lead: accepted): the timestamp-only purge test (row "A label crosses a fold edge") is only as good as the clock; add the row "Decision time and label end taken from different clocks" with the test "declare the clock (ts_recv, or ts_event + a fixed latency) in the protocol; assert both t_i,0 and t_i,1 are built from it; assert t_i,0 >= the ts_recv of the last feature input" (also applies to a.4, original line 116).]

### a.6 Compute (ThinkPad, 39 months)
Building splits is negligible (816 dates, integer arithmetic). The cost is k fits per configuration: at E.28's
measured 6 s per LightGBM fit on 10^6 rows, 10 folds cost 60 s per configuration (200 configurations: 3.3 h;
5,000: 83 h). Linear or logistic fits are an order of magnitude cheaper [assumed, not measured here].

### a.7 Verdict: USE (inside discovery, for model selection)
Folds = contiguous blocks of whole trade dates; labels clipped at their trade date's 13:20 close; purge asserted
(it should remove 0 rows); embargo 1 trade date as the frozen default with the 1/5/20-date sensitivity diagnostic.
This costs about 1% of training data and removes the label-overlap leak by construction. It does not address
non-stationarity (section c).

### a.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Purging definition | Lopez de Prado 2018, JPM "10 reasons" (AFML ch. 7 summary) | "eliminate from the training set all observations whose labels overlapped in time with those labels included in the testing set. I call this process purging." | lopezdeprado_2018_10reasons_jpm.pdf.txt l.506-507 |
| Embargo only after the test; why | same | "we should eliminate from the training set observations that immediately follow an observation in the testing set. I call this process embargo. The embargo does not need to affect training observations prior to a test" | same, l.515-518 |
| 0.01T rule | same | "A small value h ≈ .01T, where T is the number of bars, often suffices to prevent all leakage." | same, l.522-523 |
| Gap unit and overhead | Li 2026, arXiv 2609.29530 (single-author preprint, not peer reviewed) | "All gaps/purges/embargoes should be denominated in H + cτ with c ≈ 2–3."; "Check that the sanitization overhead k(2H + h)/T ≪ 1; otherwise reduce k." | li_2026_arxiv_2609_29530.pdf.txt l.742, l.747-748 |
| Blocked CV is fine for stationary series | Cerqueira, Torgo, Mozetic 2020, Machine Learning (arXiv 1905.11744) | "empirical experiments suggest that cross-validation approaches can be applied to stationary time series" | cerqueira_torgo_mozetic_2020_arxiv_1905_11744.pdf.txt l.35-36 |
| AFML ch. 7 book text itself | Lopez de Prado 2018, AFML | not fetched (no open copy); the JPM summary above is the author's own condensed version [book chapter unverified] | none |

Stopping rule: 3 full-text sources read on this topic (LdP 2018, Li 2026, Cerqueira et al. 2020) plus E.28's two;
the Bergmeir-Hyndman-Koo note could not be fetched (403 and a non-PDF page, logged).

## (b) Combinatorial purged cross-validation (CPCV)

### b.1 Core idea
Cut the discovery sample into N_g contiguous groups, test on every set of k groups and train (purged, embargoed) on
the rest, then stitch the test predictions into phi backtest paths that each cover the whole sample once. E.28 2.7
section 6 already gives the counts and the N = 6..16 table; this section adds what the path-Sharpe distribution does
and does not measure, the 39-month numbers, and whether the E.33 search can afford it.

### b.2 Equations
- Splits: C(N_g, k) = N_g! / (k! (N_g - k)!). Paths: phi[N_g, k] = (k / N_g) C(N_g, k) = C(N_g - 1, k - 1)
  (LdP 2018: "phi[N,k] = (k/N) C(N, N-k)", l.583-588; same number).
- Training fraction per split: (N_g - k)/N_g, minus the embargo after each test group that is not the last group.
- Path Sharpe: for path p, r_p,t is the stitched out-of-sample net P&L on date t (t = 1..T_d); SR_p = mean(r_p)/sd(r_p)
  on the daily basis; the CPCV "distribution" is {SR_1, ..., SR_phi}.
- What the dispersion measures (worker's derivation): every path covers the same T_d dates, so the return-sampling
  noise is common to all paths; paths differ only in which training set produced each group's forecasts. The
  spread across paths therefore measures model instability across training sets, not the sampling error of the
  Sharpe ratio. Under a true SR of 0 the sampling error of any one path's daily SR is still about 1/sqrt(T_d), and
  averaging the phi paths does not shrink it.

### b.3 Worked example (816 trade dates)
| N_g | k | splits | paths | group size (dates) | training fraction |
|---|---|---|---|---|---|
| 6 | 2 | 15 | 5 | 136.0 | 0.667 |
| 8 | 2 | 28 | 7 | 102.0 | 0.750 |
| 10 | 2 | 45 | 9 | 81.6 | 0.800 |
| 10 | 3 | 120 | 36 | 81.6 | 0.700 |
| 12 | 2 | 66 | 11 | 68.0 | 0.833 |
| 16 | 2 | 120 | 15 | 51.0 | 0.875 |

Row N_g = 10, k = 2 by hand: C(10,2) = 10 x 9 / 2 = 45 splits; phi = (2/10) x 45 = 9 = C(9,1); groups 816 / 10 =
81.6 dates; training 8 groups = 652.8 dates, minus at most 2 embargo dates (one after each test group) = 650.8.
Check: 45 splits x 2 test groups = 90 group-tests = 10 groups x 9 tests each.

Null spread of one path's Sharpe: 1/sqrt(816) = 1/28.57 = 0.0350 per day, or 0.0350 x sqrt(252) = 0.556 annualised.
So even a perfectly stable model with no edge shows path Sharpes centred anywhere in roughly +-1.1 annualised (2 sd)
from the common sampling draw; a tight CPCV path distribution around 1.0 is not evidence by itself.

Compute (fits = configurations x C(N_g, k); E.28 measured about 6 s per LightGBM fit on 10^6 rows; 0.5 s is an
assumption for a linear or logistic fit):

| Configurations | N_g = 6, k = 2 (15 fits each) | N_g = 10, k = 2 (45 fits each) |
|---|---|---|
| 200 | 3,000 fits: 5.0 h at 6 s; 0.42 h at 0.5 s | 9,000 fits: 15.0 h; 1.25 h |
| 1,000 | 15,000: 25.0 h; 2.08 h | 45,000: 75.0 h; 6.25 h |
| 5,000 | 75,000: 125 h; 10.4 h | 225,000: 375 h; 31.3 h |

Rows: one decision per minute over discovery is about 860,880 rows, close to E.28's 10^6 timing; one decision per
15 minutes in the day session only is 816 x 290 / 15 = 15,776 rows, where fits are much cheaper. Memory: 860,880
rows x 100 float32 features = 344 MB per copy, within 14 GB.

### b.4 Data it needs
The same row table as (a) (decision time, label end, trade date, net label) plus, for the path Sharpe, a daily net
P&L per configuration and path (zeros on no-trade dates, the program's convention).

### b.5 Leakage traps and tests
| Trap | Test |
|---|---|
| Reading the path distribution as phi independent replications (they share data and most of their training sets) | Report the across-path spread next to 1/sqrt(T_d); never compute a t-stat across paths |
| Selecting hyperparameters on the same CPCV used to report | Nested CPCV (ml_route_v2 V5) or select on CPCV and report only on the sealed test |
| Embargo omitted for interior test groups (a test group with training on both sides) | The split unit test of (a), run on every one of the C(N_g, k) splits |
| A configuration with no eligible model in some split silently scored as 0 | Count and report splits with no model per configuration (ml_route_v2 already records `selected = None`) |

### b.6 Compute
See b.3. CPCV on every configuration is affordable for linear models up to about 1,000 configurations and for GBMs
only up to about 200 (N_g = 10) on one machine overnight under the CLAUDE.md limits (half the cores, one heavy job).

### b.7 Verdict: MAYBE (finalists only)
Use plain purged K-fold or walk-forward to score all configurations, and CPCV (or the program's CSCV/PBO on the daily
P&L matrix, which needs no refits) only on the final shortlist, as a model-stability diagnostic declared in advance.
Its Sharpe distribution measures model instability, not sampling error, so it is never the test.

### b.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Path count formula | LdP 2018 JPM | "from k-sized testing sets on N groups we can backtest a total number of paths phi[N, k]" (formula image garbled; restated in E.28 2.7 section 6.2) | lopezdeprado_2018_10reasons_jpm.pdf.txt l.583-588 |
| Paths grow with N and k | same | "The number of paths phi[N, k] increases with N -> T and with k -> N/2." | same, l.604-605 |
| Claimed advantage | same | "A key advantage of CPCV is that it allows us to derive a distribution of Sharpe ratios, as opposed to a single (likely overfit) Sharpe ratio estimate." | same, l.605-606 |
| CPCV does not fix non-stationarity | Li 2026 | "Stationarity credible, goal is model comparison/tuning → purged k-fold + embargo (or CPCV)" | li_2026_arxiv_2609_29530.pdf.txt l.745 |
| CPCV motivated by coverage of regimes | same | "it is the motivation for the multi-path coverage of combinatorial purged cross-validation" | same, l.524-525 |
| CPCV superior on synthetic data | Arian, Norouzi Mobarekeh, Seco 2024 | not retrieved (E.28 2.7 section 6.8: citing-paper quote only) [unverified] | none |

## (c) Walk-forward, anchored and rolling, under a regime break

### c.1 Core idea
Walk-forward trains only on data before each test block, so every decision is causal. Anchored (expanding) folds
keep all history; rolling folds keep a fixed window W and forget older data. Under drift, Li (2026) proves expanding
walk-forward is the causal frontier, and an empirical study of 62 real series finds order-preserving methods more
accurate than CV when the series are non-stationary. Its cost: one historical path, fewer test months, early folds
trained on little data.

### c.2 Equations
Fold i (i = 1..F) tests on [s_i, s_i + Delta) with s_i = s_1 + (i - 1) Delta, and trains on
- anchored: [t_0, s_i - g);  rolling: [s_i - g - W, s_i - g);
- g = purge + embargo gap, in trade dates (section a: 1 date when labels end by the 13:20 close).
- Number of folds: F = floor((L - W_1)/Delta), L the sample length, W_1 the first training length; out-of-sample
  share beta = F Delta / L.
- Li (2026) Proposition 7: (i) the variance of the average test loss is about sigma_inf^2 / (beta T); (ii) under
  non-stationarity, a risk difference Delta_r confined to the uncovered part of the sample gives worst-case error at
  least (1 - beta) Delta_r / 2, which no estimator can remove. Coverage beta is what walk-forward pays with.

### c.3 Worked example (39 months, step 3 months)
| First training length | Step | Test folds F = floor((39 - W_1)/3) | Test months | beta |
|---|---|---|---|---|
| 12 months | 3 | floor(27/3) = 9 | 27 | 27/39 = 0.69 |
| 18 months | 3 | floor(21/3) = 7 | 21 | 0.54 |
| 24 months | 3 | floor(15/3) = 5 | 15 | 0.38 |
| 12 months | 6 | floor(27/6) = 4 | 24 | 0.62 |

With W_1 = 12 months: 9 quarterly folds of about 816 x 3/39 = 62.8 trade dates each; anchored training grows from
about 251 to about 754 dates; a rolling W = 12 months keeps about 251 dates. Check: 9 x 3 + 12 = 39 months.

The planner's "positive results in at least two-thirds of quarters" (not one of my pointers; arithmetic only): with
9 test quarters, at least 6 positive. If quarterly signs were independent fair coins under the null, P(>= 6 of 9) =
(C(9,6) + C(9,7) + C(9,8) + C(9,9)) / 2^9 = (84 + 36 + 9 + 1)/512 = 130/512 = 0.254. A null rule passes that filter
one time in four, so it is a stability description, not a significance test.

Direction of the final test (worker's observation for the lead): the sealed test window 2017-05..2020-11 lies BEFORE
the discovery window 2020-12..2024-02. The one-shot test therefore asks whether a rule fitted on later data works on
earlier data. A forward walk-forward inside discovery estimates the opposite direction. LdP (2018) argues that the
two directions are equally legitimate ("it is as easy to overfit a walk-forward backtest as to overfit a
walk-backward backtest"). A mirror diagnostic is cheap: a reversed anchored walk-forward inside discovery (train on
the last 12 months, test the preceding quarters moving backward), reported next to the forward one. If the planner's
expected regime break (renewable-diesel oil share after 2021 versus trade war and Covid in 2017-20) is real, the
reversed folds are the closer rehearsal of the sealed test. This is a suggestion, not a source claim.

### c.4 Data it needs
The trade-date calendar of discovery, the row table of (a), and roll dates. Rolling windows need W declared in
trade dates.

### c.5 Leakage traps and tests
| Trap | Test |
|---|---|
| Hyperparameters chosen by looking at walk-forward results, then the same results reported | Nested: tune inside each training window only (Li guidance item 3: "rehearse the tuning process inside the rolling procedure"); the frozen pipeline is re-run end to end |
| Gap g omitted at fold starts | Same timestamp unit test as (a) on every fold |
| Fold boundaries chosen after seeing performance (moving the start to dodge a bad quarter) | Fold dates frozen and hashed with the protocol; a shift test (all boundaries moved by 5 dates) reported alongside |
| Learning-curve bias: early folds starved, the average understates the final model | Report per-fold score against training size (Li Proposition 6 / guidance item 3), not only the mean |

### c.6 Compute
F fits per configuration (9 for the table's first row), less than 10-fold CV and 5x less than CPCV with N_g = 10,
k = 2. At 6 s per GBM fit: 200 configurations x 9 = 1,800 fits = 3.0 h; 5,000 x 9 = 45,000 fits = 75 h.

### c.7 Verdict: USE (as the reported discovery estimate); K-fold for tuning only if stationarity is credible
The planner expects a regime break and the final test runs on a different era, which is the case where both Li and
Cerqueira et al. favour order-preserving validation. Recommended for the lead to weigh: expanding walk-forward with
quarterly steps and a 1-date gap as the discovery estimate; the reversed walk-forward as a pre-declared diagnostic;
purged K-fold (a) only inside each training window for tuning.

### c.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Use expanding walk-forward under non-stationarity | Li 2026 (preprint) | "Non-stationarity feared, or “expected live performance” to be quoted → expanding walk-forward (it is the causal frontier, Corollary 3); report the per-fold-versus-training-size curve rather than a single average" | li_2026_arxiv_2609_29530.pdf.txt l.750-752 |
| Uncovered regimes cannot be repaired | same | "a regime you never tested may hide a ∆, and no statistical technique conjures information out of unobserved intervals" | same, l.522-523 |
| Order-preserving methods win on real non-stationary series | Cerqueira, Torgo, Mozetic 2020 | "in real-world scenarios, when different sources of non-stationary variation are at play, the most accurate estimates are produced by out-of-sample methods that preserve the temporal order of observations" | cerqueira_torgo_mozetic_2020_arxiv_1905_11744.pdf.txt l.36-39 |
| Repeated hold-out recommended | same | "out-of-sample applied in multiple testing periods (Rep-Holdout) is recommended" | same, l.1256-1261 |
| WF is one overfit-prone path; walk-backward equally valid | LdP 2018 JPM | "First, a single scenario is tested (the historical path), which can be easily overfit"; "it is as easy to overfit a walk-forward backtest as to overfit a walk-backward backtest" | lopezdeprado_2018_10reasons_jpm.pdf.txt l.538-544 |
| WF's advantage | same | "History is a filtration; hence, using trailing data guarantees that the testing set is out-of-sample (no leakage), as long as purging has been properly implemented." | same, l.535-536 |

Stopping rule: three full-text sources (Li, Cerqueira et al., LdP 2018); no source compared forward and backward
validation on futures data; I found none in two arXiv-style queries and stopped.

## (d) The deflated Sharpe ratio at the search's N

### d.1 Core idea
The best of N trials has a positive expected Sharpe ratio even when every trial is worthless. The DSR (Bailey and
Lopez de Prado 2014) asks how likely the selected strategy's true Sharpe ratio is above zero once the benchmark is
raised from 0 to that expected maximum, and once the standard error is widened for skew, fat tails and a short
sample. The program already computes it (section 0.2). New here: what it implies on ZM per-trade numbers at
N = 538 + 200, 538 + 1,000 and 538 + 5,000 over 39 months, which effective N goes with which variance, and the
per-trade versus annualised bookkeeping.

### d.2 Equations
Symbols: SR_hat the selected strategy's Sharpe ratio on its own sampling basis (per trade, or per trade date with
zeros on no-trade dates); T the number of observations on that basis; gamma3 its skewness; gamma4 its raw kurtosis
(normal = 3); V = V[{SR_hat_n}] the variance of the Sharpe estimates across the trials, same basis; N the number of
(independent) trials; gamma = 0.5772 the Euler-Mascheroni constant; Z the standard normal CDF.

1. Expected maximum (BLdP 2014 eq. (1); the "False Strategy theorem" in LdP and Lewis 2019 section 6):
   E[max_n SR_hat_n] ~ sqrt(V) x e(N),  e(N) = (1 - gamma) Z^-1[1 - 1/N] + gamma Z^-1[1 - 1/(N e)].
2. DSR (BLdP 2014 eq. (2)):
   DSR = Z[ (SR_hat - SR0) sqrt(T - 1) / sqrt(1 - gamma3 SR_hat + ((gamma4 - 1)/4) SR_hat^2) ],  SR0 = sqrt(V) e(N).
   (Symbols lost in pdftotext; the form matches funnel/multiple_comparisons.py:81 and is confirmed by reproducing the
   paper's three printed outcomes, section 0.2.)
3. Null calibration (worker's derivation): for T iid observations with true SR 0, Var(SR_hat) ~ 1/T (to first order,
   normal returns). Setting V = 1/T and sqrt(T - 1) ~ sqrt(T), DSR >= 0.95 becomes
   SR_hat sqrt(T) >= e(N) + 1.645 sqrt(D),  D = 1 - gamma3 SR_hat + ((gamma4 - 1)/4) SR_hat^2 ~ 1 for per-trade SR ~ 0.1-0.3.
   So the DSR bar is a t-statistic bar t* ~ e(N) + 1.645, independent of T and of the horizon.
4. Basis invariance: if SR_hat and sqrt(V) are both multiplied by sqrt(q) (annualising with q observations a year) then
   T must become years, and z is unchanged. In annual units the bar is SR*_ann ~ t* / sqrt(Y), Y the sample in years.
   Mixing bases (an annualised SR_hat with T counted in trades, or a daily V with a per-trade SR_hat) is the error the
   program's docstring warns against and LdP-Lewis 2019 section 8.2 corrects ("in order to match the frequency").
[MathReview C-2 (lead: accepted): the invariance claim is not true beyond first order: sqrt(T/q - 1) is not sqrt(T - 1)/sqrt(q) at Y = 3.25 years (1.50 vs 1.80), and D's SR^2 term scales by q (annual D = 1 + SR_ann^2/2 = 4.6 at SR_ann 2.68); per-trade SR 0.1689, T 816, N 738, V 1/T gives z 1.644, DSR 0.950, while the same inputs annualised (SR 2.676, V x 251, T 3.25) give z 0.644, DSR 0.74 (monthly basis DSR 0.924). Replace the sentence with the rule: compute DSR on the native basis (per trade or daily with zeros) and never rescale inside the formula; SR*_ann ~ t*/sqrt(Y) stays valid as a display conversion of the t-bar only.]
5. Effective number of trials, three published definitions:
   - BLdP 2014 Appendix 3 eq. (9): N_hat = rho_bar + (1 - rho_bar) M, rho_bar the average off-diagonal correlation
     of the M trials' returns (eq. (8)); implemented, never run, in ml_route/accounting.py (E.28 1b M5).
   - ONC (LdP and Lewis 2019 section 8): cluster the trials on the distance D_ij = sqrt((1 - rho_ij)/2) with k-means
     and silhouette scores; E[K] = number of clusters; form each cluster's minimum-variance portfolio
     w_k = Sigma_k^-1 1 / (1' Sigma_k^-1 1); annualise each cluster Sharpe (aSR_k = SR_k sqrt(Frequency_k),
     Frequency_k = T_k / Years_k); E[V[{SR_k}]] = V[{aSR_k}] / Frequency_k*, k* the selected strategy's cluster.
   - Participation ratio (Nikolopoulos 2026, arXiv 2604.15531, preprint, eq. (4)): K_eff = (tr Sigma)^2 / ||Sigma||_F^2
     = K^2 / sum_ij rho_ij^2.
6. Minimum backtest length (Bailey, Borwein, Lopez de Prado, Zhu 2014, Theorem 3.1, eq. (3.2)), years needed for the
   expected maximum annualised Sharpe of N null trials to equal E[max_N]: MinBTL ~ (e(N) / E[max_N])^2 < 2 ln(N) / E[max_N]^2.

### d.3 Worked examples

**(i) e(N) at the three search sizes** (`M5a_calc_out.txt`, section "(d) e(N)"):

| N | 1 - 1/N | Z^-1 | N e | Z^-1[1 - 1/(N e)] | e(N) = 0.4228 x col3 + 0.5772 x col5 | Monte Carlo mean max (4,000 draws) | sqrt(2 ln N) |
|---|---|---|---|---|---|---|---|
| 538 + 200 = 738 | 0.998645 | 2.9988 | 2,006.1 | 3.2914 | 3.1677 | 3.1543 | 3.6343 |
| 538 + 1,000 = 1,538 | 0.999350 | 3.2159 | 4,180.7 | 3.4926 | 3.3756 | 3.3596 | 3.8310 |
| 538 + 5,000 = 5,538 | 0.999819 | 3.5670 | 15,053.8 | 3.8211 | 3.7137 | (not run) | 4.1520 |

Check: 0.4228 x 2.9988 + 0.5772 x 3.2914 = 1.2679 + 1.8998 = 3.1677. The approximation sits 0.4-0.5% above the
simulated mean (MC standard error about 0.006), so it is slightly conservative. Seven and a half times more trials
(738 to 5,538) raise the bar by only 3.7137 / 3.1677 = 1.17 times.

**(ii) The DSR bar on ZM per-trade statistics, null-calibrated V = 1/T.** Assumptions: market-order round trip
c = 1.59 ticks; sigma_15 = 12.20 and sigma_60 = 24.40 ticks (random walk); trades do not overlap; gamma3 and
gamma4 are illustrative, not measured. One cell by hand, h = 15 min, one trade per trade date (T = 816), N = 738,
gamma3 = 0, gamma4 = 3:
- sqrt(V) = sqrt(1/816) = 0.035007; SR0 = 0.035007 x 3.1677 = 0.1109 per trade.
- Solve (SR - 0.1109) x sqrt(815) / sqrt(1 + 0.5 SR^2) = 1.645: SR* = 0.1689. Check: (0.1689 - 0.1109) x 28.548 /
  sqrt(1 + 0.5 x 0.1689^2) = 0.0580 x 28.548 / 1.0071 = 1.644.
- t* = 0.1689 x sqrt(816) = 0.1689 x 28.566 = 4.83 (versus e(N) + 1.645 = 4.81).
- Net edge needed = SR* x sigma_15 = 0.1689 x 12.20 = 2.06 ticks a trade; gross = 1.59 + 2.06 = 3.65 ticks.
- Annualised: q = 816 / 3.25 = 251 trades a year; SR*_ann = 0.1689 x sqrt(251.1) = 0.1689 x 15.85 = 2.68 = 4.83 / sqrt(3.25).

| h | trades T (per year) | N | SR0 per trade | SR* per trade (gamma4 3 / 8 / skew -0.5 & 8) | t* | gross edge needed, ticks (gamma4 3) | SR*_ann |
|---|---|---|---|---|---|---|---|
| 15 | 408 (126) | 738 | 0.1568 | 0.2395 / 0.2424 / 0.2473 | 4.84 | 4.51 | 2.68 |
| 15 | 408 (126) | 1,538 | 0.1671 | 0.2499 / 0.2531 / 0.2581 | 5.05 | 4.64 | 2.80 |
| 15 | 408 (126) | 5,538 | 0.1839 | 0.2668 / 0.2704 / 0.2758 | 5.39 | 4.85 | 2.99 |
| 15 | 816 (251) | 738 | 0.1109 | 0.1689 / 0.1699 / 0.1724 | 4.83 | 3.65 | 2.68 |
| 15 | 816 (251) | 1,538 | 0.1182 | 0.1762 / 0.1774 / 0.1799 | 5.03 | 3.74 | 2.79 |
| 15 | 816 (251) | 5,538 | 0.1300 | 0.1881 / 0.1894 / 0.1921 | 5.37 | 3.89 | 2.98 |
| 15 | 3,264 (1,004) | 738 | 0.0554 | 0.0843 / 0.0844 / 0.0850 | 4.82 | 2.62 | 2.67 |
| 15 | 3,264 (1,004) | 5,538 | 0.0650 | 0.0939 / 0.0940 / 0.0947 | 5.36 | 2.74 | 2.97 |
| 60 | 816 (251) | 738 | 0.1109 | 0.1689 / 0.1699 / 0.1724 | 4.83 | 5.71 | 2.68 |
| 60 | 816 (251) | 5,538 | 0.1300 | 0.1881 / 0.1894 / 0.1921 | 5.37 | 6.18 | 2.98 |
| 60 | 3,264 (1,004) | 5,538 | 0.0650 | 0.0939 / 0.0940 / 0.0947 | 5.36 | 3.88 | 2.97 |

Reading: (1) the bar is t ~ 4.8 to 5.4 whatever the horizon or frequency; (2) skew and kurtosis barely move it at
per-trade SR of 0.1-0.3 (at most +2%), unlike the BLdP example where daily skew -3 and kurtosis 10 mattered;
(3) the only lever is the number of independent trades: four non-overlapping 15-minute trades a day bring the gross
edge needed down to 2.6-2.7 ticks, one a day needs 3.6-3.9 ticks, one every other day 4.5-4.9 ticks; (4) the
annualised bar of about 2.7-3.0 equals the expected best null Sharpe plus a margin: with 3.25 years the best of N
null trials shows e(N)/sqrt(3.25) = 1.76 (N = 738), 1.87 (1,538), 2.06 (5,538) annualised.

**(iii) A fixed candidate at the three N** (h = 15, T = 816, gamma4 = 8, V = 1/T): gross 3.0 ticks gives net SR
(3.0 - 1.59)/12.20 = 0.1156 a trade and t = 0.1156 x 28.566 = 3.30 (it passes HLZ t > 3.0), but DSR = 0.589 (N = 538),
0.553 (738), 0.471 (1,538), 0.342 (5,538). Gross 3.5 ticks (t = 4.47): DSR 0.914, 0.899, 0.858, 0.771. None reaches 0.95.

**(iv) Per-trade versus daily-with-zeros** (synthetic, 2,000 samples of 816 days, a trade on half the days, per-trade
SR 0.08, t5 noise): mean z on the per-trade series 1.640, on the daily series with zeros 1.635, correlation 1.0000. The
daily Sharpe is about sqrt(p) times the per-trade Sharpe (sqrt(0.5) x 0.08 = 0.0566) and T is about 1/p times larger,
so z = SR sqrt(T) is unchanged to first order; the zero-inflated series has kurtosis about gamma4 / p (9 / 0.5 = 18
for t5), which enters D only through ((gamma4 - 1)/4) SR^2 and stays small. The program's daily convention is
therefore safe, provided V is also computed on daily Sharpes (it is: `dsr_table`, `sharpe_variance`).

**(v) Which effective N goes with which V** (synthetic, M = 1,000 trials, T = 816, 400 repetitions; `M5a_calc3_out.txt`):

| Correlation structure | Mean max SR (simulated) | sqrt(V_emp) e(M) | sqrt(V_emp) e(K) | sqrt(1/T) e(M) | K_eff (participation) |
|---|---|---|---|---|---|
| one factor, rho 0.5 | 0.0803 | 0.0803 | n/a | 0.1140 | 4.0 |
| one factor, rho 0.8 | 0.0521 | 0.0509 | n/a | 0.1140 | 1.6 |
| 50 clusters of 20, within 0.95 | 0.0927 | 0.1131 | 0.0791 | 0.1140 | 55.1 |
| 200 clusters of 5, within 0.9 | 0.1066 | 0.1138 | 0.0967 | 0.1140 | 235.8 |

Reading (worker's derivation, checked by this simulation): the cross-trial variance V_emp already shrinks by (1 - rho)
under a common factor (simulated V 0.000619 versus (1 - 0.5)/816 = 0.000613, `M5a_calc2_out.txt`), so the
empirical-V benchmark with the literal count M is exact there; combining V_emp with a reduced N (eq. (9) gives
N_hat = 500.5 at rho 0.5, the participation ratio 4.0) double-discounts and is anti-conservative. Under cluster
structure the truth lies between sqrt(V_emp) e(M) (conservative) and sqrt(V_emp) e(K) (slightly anti-conservative).
Rule for the lead to weigh: either the empirical V with the literal N (the program's current pairing, conservative
in both structures) or the null V = 1/T with an effective N, never the empirical V with an effective N.

Effective N by eq. (9), with the 538 earlier trials added literally:

| M (E.33 configurations) | rho_bar 0.3 | 0.5 | 0.7 | 0.9 |
|---|---|---|---|---|
| 200 | 140.3 (N 678, e 3.143) | 100.5 (639, 3.125) | 60.7 (599, 3.106) | 20.9 (559, 3.086) |
| 1,000 | 700.3 (1,238, 3.315) | 500.5 (1,039, 3.266) | 300.7 (839, 3.205) | 100.9 (639, 3.126) |
| 5,000 | 3,500.3 (4,038, 3.633) | 2,500.5 (3,039, 3.559) | 1,500.7 (2,039, 3.453) | 500.9 (1,039, 3.266) |

Even the most generous discount moves e(N) by at most 12% (3.7137 to 3.266 at M = 5,000); the cumulative 538 keeps
the floor near e(538) = 3.07.

**(vi) MinBTL**: at E[max] = 1 annualised, N = 45 needs (e(45))^2 = 5.00 years (the paper's own "if only 5 years of
data are available, no more than 45 independent model configurations should be tried"); N = 738 needs 10.0 years,
1,538 needs 11.4, 5,538 needs 13.8. With 3.25 years, the null maximum is 1.76-2.06 annualised (iii above).

### d.4 Data it needs
Per configuration: the daily net P&L over discovery (zeros on no-trade dates), from which SR_hat, skew, raw kurtosis
and T; the cross-configuration population variance of the daily Sharpes (V); the full daily matrix (dates x
configurations) for rho_bar, ONC or K_eff. Per-trade P&L only for the overlap diagnostic below.

### d.5 Leakage traps and tests
| Trap | Test |
|---|---|
| Basis mismatch (annualised SR with T in trades; daily V with a per-trade SR) | Assert one basis in the call (the program's docstring requires it); unit test: DSR unchanged when every input is rescaled consistently |
| Overlapping trades (decisions every 15 minutes, 60-minute holds) inflate T | Compute z on daily-aggregated P&L and on per-trade P&L; a per-trade z more than about 1.2 times the daily z flags overlap; the daily series is the one reported |
| N undercounted (exploratory runs, discarded configurations, re-runs with a bug fix) | Count from the append-only trial registry (E.28 1b M6) and require it to equal the number of distinct configuration hashes in the run logs |
| V computed over survivors only, or over a hand-picked subset | `dsr_table(variance_over=...)` must receive every configuration in the search; assert len(variance_over) == M |
| Empirical V paired with an effective N (double discount, (v) above) | Declare one pairing in the protocol |
| Long and short mirrors of one signal counted as two trials (V and N both inflated, and the sign chosen after the fact) | Fix each signal's sign economically before the run, or count the pair as one trial and report the sign rule |
| Excess kurtosis passed where raw is expected | Unit test: a normal sample must give kurtosis near 3 into `deflated_sharpe_ratio` |
| V, moments or N touched by the sealed window | All inputs from discovery only; the sealed seal check (reports/stage_e32_briefs/seal/) before any DSR run |

### d.6 Compute
Negligible: moments and a variance over M daily series (816 x 5,000 floats = 33 MB); ONC's k-means over a 5,000 x 5,000
correlation matrix (200 MB in float64) with repeated restarts is minutes on the ThinkPad [estimate].

### d.7 Verdict: USE (it is the program's bar; the lead sets the threshold)
On ZM it means t ~ 4.8-5.4 on the discovery sample, i.e. an annualised Sharpe of about 2.7-3.0 over 39 months, or a
gross edge of 2.6-3.9 ticks a 15-minute trade at one to four trades a day. Report DSR at the literal cumulative N with
the empirical V (current pairing) and, beside it, the eq. (9) and ONC variants, as E.2b's RA-3 already specified for
the ML route (ml_route/accounting.py:25-31).

### d.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Expected maximum after N independent trials | Bailey and Lopez de Prado 2014, JPM | "Appendix 1 proves that, under these assumptions, the expected maximum of { ̂ } after independent trials can be approximated as:" (eq. (1), symbols lost) | bailey_lopezdeprado_2014_dsr.pdf.txt l.312-316 |
| Definition of the DSR inputs | same | "[{ ̂ }] is the variance across the trials’ estimated SR and N is the number of independent trials. We also use information concerning the selected strategy: ̂ is its estimated SR, T is the sample length, ̂ is the skewness ... and ̂ is the kurtosis" | same, l.373-379 |
| What DSR deflates | same | "DSR deflates SR by taking into consideration five additional variables: The non-Normality of the returns ( ̂ ̂ ), the length of the returns series ( ), the variance of the SRs tested ( [{ ̂ }]), as well as the number of independent trials" | same, l.389-392 |
| Paper's example outcomes | same | "there is only a 90% chance that the true SR associated with this strategy is greater than zero"; "after running only N=46 independent trials ... would have been 0.9505"; "If the strategy had exhibited Normal returns ( ̂ ̂ ), ̂ after N=88 independent trials" | same, l.440-446 |
| Effective N interpolation | same, Appendix 3 | "Suppose that we run M trials, where only N trials are independent, N<M."; eq. (9) image lost; restated in ml_route/accounting.py:33-43 | same, l.625, l.655-658 |
| False Strategy theorem | Lopez de Prado and Lewis 2019, QF (SSRN 3167017 working-paper copy) | "unless max_k{SR_k} ≫ E[max_k{SR_k}], the discovered strategy is likely to be a false positive" | lopezdeprado_lewis_2019_onc_ssrn3167017.pdf.txt l.344-345 |
| ONC clusters as the trial count | same | "we consider clustering the strategies and using those clusters as a proxy" | same, l.411-412 |
| Frequency matching of V | same | "We need to express the estimated variance of clustered trials in terms of the frequency of the selected strategy, in order to match the frequency of the ̂ SR estimate used by the DSR equation" | same, l.573-575 |
| Participation-ratio K_eff | Nikolopoulos 2026, arXiv 2604.15531 (preprint) | "When candidates are correlated, the nominal K overstates the effective dimensionality of the search." (eq. (4)) | arxiv_2604_15531_spurious_predictability.pdf.txt l.259-264 |
| MinBTL | Bailey, Borwein, Lopez de Prado, Zhu 2014, Notices AMS | "if only 5 years of data are available, no more than 45 independent model configurations should be tried, or we are almost guaranteed to produce strategies with an annualized Sharpe ratio IS of 1, but an expected Sharpe ratio OOS of zero" | bailey_borwein_ldp_zhu_2014_pseudomath.pdf.txt l.426-429 |
| MLAM 2020 ch. 8 (ONC, false strategy) | Lopez de Prado 2020, Cambridge Elements | book not fetched; the 2019 paper above is the same authors' source text [book unverified] | none |
| Var(SR_hat) ~ 1/T under the null | Lo 2002 / Mertens 2002 (cited in BLdP l.357-358) | not fetched; standard result used as an assumption [unverified] | none |

## (e) PBO by combinatorially symmetric cross-validation (CSCV)

### e.1 Core idea
Cut the dates x configurations performance matrix into S equal row blocks, form every split of the blocks into two
halves, pick the in-sample best configuration on one half, and record where it ranks on the other. PBO is the share
of splits where the in-sample winner lands at or below the out-of-sample median. The program runs it (funnel, 8
blocks; ml_route_v2, 16 blocks) with a bar of 0.5 (E.20: "0.596 (bar < 0.5)", E.28 1b M4). New here: the paper's own
definitions, a hand-worked split, the sampling noise of the PBO estimate itself on 39 months, and a typo in the paper.

### e.2 Equations (Bailey, Borwein, Lopez de Prado, Zhu 2017, section 2.2)
- M: the T x N matrix of performance (T dates, N configurations). Partition rows into S (even) blocks M_s of T/S rows.
- C_S: all combinations of the S blocks taken S/2 at a time; #C_S = C(S, S/2) (eq. (2.3)).
- For c in C_S: J = the S/2 training blocks in order, J_bar = the complement (test). R_c and R_bar_c the vectors of
  the N configurations' performance on J and J_bar; n* = argmax R_c (the in-sample best).
- omega_bar_c = r_bar_{n*,c} / (N + 1), with r_bar the out-of-sample rank (1 = worst, N = best).
- lambda_c = ln( omega_bar_c / (1 - omega_bar_c) ) (the paper prints the fraction inverted in the pdftotext line
  "λc = ln (1−ω̄ c) / ω̄c"; its next sentence, "High logit values imply a consistency between IS and OOS performances",
  fixes the orientation as ln(omega / (1 - omega))).
- PBO = phi = integral_{-inf}^{0} f(lambda) d lambda = share of splits with lambda_c <= 0.
- Program convention (funnel/multiple_comparisons.py:143): omega = (number strictly worse + 0.5)/N instead of r/(N+1);
  both give lambda <= 0 exactly when the winner is at or below the median, so PBO agrees; individual logits differ.

### e.3 Worked example
**Counts.** S = 8: C(8,4) = 70 splits; S = 16: C(16,8) = 12,870 splits. The paper writes "if S = 16, we will form
12, 780 combinations" (`bailey_borwein_ldp_zhu_2017_pbo.pdf.txt` l.453): a typo, C(16,8) = 16!/(8! 8!) = 12,870 (the
program computes 12,870 combinations, which is correct). With 816 discovery dates: S = 8 gives blocks of 102 dates,
S = 16 blocks of 51 dates.

**One split by hand** (4 made-up configurations x 8 blocks, net ticks per block):

| Config | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 |
|---|---|---|---|---|---|---|---|---|
| A | 5 | -3 | 4 | -2 | 6 | -4 | 3 | -1 |
| B | 2 | 2 | -1 | 1 | 0 | 1 | -2 | 2 |
| C | -4 | 6 | -3 | 5 | -2 | 4 | -1 | 3 |
| D | 1 | -1 | 1 | -1 | 1 | -1 | 1 | -1 |

Training blocks {b1, b3, b5, b7}: A 5 + 4 + 6 + 3 = 18; B 2 - 1 + 0 - 2 = -1; C -4 - 3 - 2 - 1 = -10; D 1 + 1 + 1 + 1 = 4.
In-sample best n* = A. Test blocks {b2, b4, b6, b8}: A -3 - 2 - 4 - 1 = -10; B 2 + 1 + 1 + 2 = 6; C 6 + 5 + 4 + 3 = 18;
D -1 - 1 - 1 - 1 = -4. A ranks last: r_bar = 1, omega = 1/5 = 0.2, lambda = ln(0.2/0.8) = -1.386 <= 0: overfit on this
split. Over all 70 splits the PBO is 0.800 (56 of 70), and the in-sample winner loses money out of sample in 45.7% of
splits (`M5a_calc_out.txt`, section "(e)"; both conventions give 0.800). Tie rule: on split {b1, b2, b3, b4} A, B and C
tie at 4 in sample; the program's Python `max` takes the first index. Ties must be broken by a declared rule.

**Sampling noise of the PBO estimate** (synthetic iid N(0,1) daily P&L, 816 days; `M5a_calc2_out.txt`):

| Configurations | S | Repetitions | Mean PBO | sd | 5%-95% |
|---|---|---|---|---|---|
| 10 | 8 | 200 | 0.485 | 0.223 | 0.128-0.829 |
| 50 | 8 | 200 | 0.504 | 0.180 | 0.228-0.814 |
| 200 | 16 | 12 | 0.504 | 0.114 | 0.341-0.671 |
| 50, one with a true daily SR 0.10 (about 1.6 annualised) | 8 | 200 | 0.299 | n/a | 0.029-0.657 |

Reading: under pure noise the PBO estimate is centred at 0.5 as it should be, but a single 39-month estimate wanders
from about 0.13 to 0.83 with 8 blocks; with a normal approximation (mean 0.5, sd 0.18-0.22) roughly one null search in three reports PBO below 0.4. A real edge of
annualised Sharpe 1.6 hidden among 49 null configurations gives PBO 0.30 on average, with a 95th percentile of
0.657, so it too can read above 0.5. The program's bar PBO < 0.5 is therefore a weak screen in both directions on this sample; the paper's own
suggested Neyman-Pearson cut is 0.05, which the one-true-edge case meets only in its lowest tail (5th percentile 0.029).
Check: the mean null PBO (0.485-0.504) is within 2 sd/sqrt(reps) of 0.5 in every row.

### e.4 Data it needs
The daily net P&L matrix over discovery (816 dates x M configurations), from the frozen pipeline's out-of-sample
predictions (walk-forward or CV), not in-sample fits. Configurations that trade at different frequencies are aligned
on the common trade-date index (the paper: "observations should be aggregated to match a common index").

### e.5 Leakage traps and tests
| Trap | Test |
|---|---|
| PBO computed on in-sample (fitted) P&L instead of out-of-sample predictions | Assert every P&L entry comes from a model that did not train on that date (fold id per date) |
| Blocks not contiguous, or not equal (the last block taking a large remainder) | Assert block sizes differ by at most the remainder (ml_route_v2 `pbo_cscv` reports `block_dates`) |
| Ties in the in-sample argmax resolved by column order | Declare a tie rule; test with a duplicated column |
| A handful of configurations (N < 10) makes ranks coarse | Report N with the PBO; with N = 4 the rank takes only four values |
| Reading PBO as a significance test | Report the null band above next to the estimate |

### e.6 Compute
C(16,8) = 12,870 splits x M configurations of sums: for M = 5,000 about 64 million additions, seconds in NumPy; the
synthetic run of 200 configurations x 12,870 splits x 12 repetitions took well under a minute.

### e.7 Verdict: USE (as a reported diagnostic, not as a gate)
Keep it (it is the program's practice and cheap), report it with its null band, and do not let PBO < 0.5 carry weight
in selection on a 39-month sample.

### e.8 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Partition into S blocks | Bailey, Borwein, Lopez de Prado, Zhu 2017, J. Computational Finance (author copy) | "we partition M across rows, into an even number S of disjoint submatrices of equal dimensions" | bailey_borwein_ldp_zhu_2017_pbo.pdf.txt l.442-443 |
| Combination count and the typo | same | "For instance, if S = 16, we will form 12, 780 combinations." | same, l.453 |
| Relative rank | same | "Define the relative rank of r̄nc ∗ by ω̄c := r̄nc ∗ /(N + 1) ∈ (0, 1)." | same, l.481 |
| Logit orientation | same | "High logit values imply a consistency between IS and OOS performances, which indicates a low level of backtest overfitting." | same, l.488-490 |
| PBO definition | same | "This represents the rate at which optimal IS strategies underperform the median of the OOS trials." | same, l.540-542 |
| Suggested cut 0.05 | same | "a customary approach would be to reject models for which PBO is estimated to be greater than 0.05" | same, l.553-554 |
| PBO can be low while losses are likely | same | "Note that, even if φ ≈ 0, P rob[Rn∗ < 0] could be high" | same, l.582 |

## (f) FWER versus FDR for a large search that sends at most 3 candidates to one one-shot test

### f.1 Core idea
FWER procedures (Bonferroni, Holm, Romano-Wolf, White's Reality Check, Hansen's SPA) bound the chance of even one false
claim; FDR procedures (Benjamini-Hochberg, Benjamini-Yekutieli, Storey's q-values) bound the expected share of false
claims among many. A design that spends one sealed test on at most 3 candidates makes few claims and pays heavily for
a single false one, so it is an FWER problem at both stages. The search's size N matters at the selection stage
(discovery); the one-shot test, on data that played no part in selection, needs a correction over its own 3
hypotheses only. Whether to add more (HLZ t > 3.0, a family layer) is the lead's conservatism choice.

### f.2 Equations (one-sided p-values p_(1) <= ... <= p_(m); alpha = 0.05)
- Bonferroni (FWER, any dependence): reject H_i if p_i <= alpha / m (HLZ 2016 section 3.4.1).
- Holm 1979 (FWER, any dependence, step-down): with b the rank, reject H_(1)..H_(k-1), k the first index with
  p_(b) > alpha / (M + 1 - b) (HLZ 2016 section 3.4.2; Holm's paper not fetched).
- Benjamini-Hochberg 1995 (FDR at q*, independence; also PRDS): k = largest i with p_(i) <= (i/m) q*; reject H_(1)..H_(k).
  Under PRDS it controls FDR at q* m0/m (BY 2001 as stated by Fithian and Lei 2020).
- Benjamini-Yekutieli 2001 (FDR, arbitrary dependence): BH at q*/L_m, L_m = sum_{i=1}^{m} 1/i = ln m + O(1)
  (HLZ's c(M), their eq. (1); Fithian-Lei restatement).
- Storey's q-value (FDR, needs pi0): pi0_hat(lambda) = #{p_i > lambda} / (m (1 - lambda)); q-value = the smallest FDR
  at which a feature is called significant (Storey and Tibshirani 2003). The pi0 estimate "can fail badly under
  dependence" (Fithian-Lei).
- White 2000 Reality Check (FWER for "the best beats the benchmark"): f_k,t = performance of rule k relative to the
  benchmark at t; H0: max_k E(f_k) <= 0; statistic V_bar = max_k n^{1/2} f_bar_k; p-value from the stationary
  (Politis-Romano) bootstrap distribution of max_k n^{1/2} (f_bar*_k - f_bar_k).
- Hansen 2005 SPA: studentise each n^{1/2} d_bar_k by omega_hat_k, and recentre the bootstrap only for rules that are
  not clearly bad: mu_hat_k = d_bar_k 1{ n^{1/2} d_bar_k / omega_hat_k <= -sqrt(2 log log n) }; "more powerful and less
  sensitive to poor and irrelevant alternatives" than the RC.
- Romano-Wolf 2005 stepdown (FWER, asymptotic, any dependence): at each step compare every remaining studentised
  statistic with the bootstrap 1 - alpha quantile of the max over the remaining set, reject those above, drop them,
  repeat until none is rejected.
- HLZ 2016 hurdle: t > 3.0 (two-sided p 0.0027).

### f.3 Worked arithmetic
**Thresholds (one-sided alpha 0.05; `M5a_calc_out.txt` section "(f)")**

| m | Bonferroni p | z | BY first rejection p = alpha/(m L_m) | z | L_m | BH at the 3rd rejection p = 3 alpha/m | z |
|---|---|---|---|---|---|---|---|
| 3 | 0.01667 | 2.128 | 0.00909 | 2.362 | 1.833 | 0.05 | 1.645 |
| 200 | 2.50e-4 | 3.481 | 4.25e-5 | 3.930 | 5.878 | 7.50e-4 | 3.175 |
| 738 | 6.78e-5 | 3.816 | 9.43e-6 | 4.278 | 7.182 | 2.03e-4 | 3.536 |
| 1,000 | 5.00e-5 | 3.891 | 6.68e-6 | 4.354 | 7.485 | 1.50e-4 | 3.615 |
| 1,538 | 3.25e-5 | 3.994 | 4.11e-6 | 4.460 | 7.916 | 9.75e-5 | 3.725 |
| 5,000 | 1.00e-5 | 4.265 | 1.10e-6 | 4.734 | 9.095 | 3.00e-5 | 4.013 |
| 5,538 | 9.03e-6 | 4.288 | 9.82e-7 | 4.757 | 9.197 | 2.71e-5 | 4.037 |

By hand for m = 738: 0.05 / 738 = 6.775e-5, z = Z^-1(1 - 6.775e-5) = 3.816; L_738 = ln 738 + 0.5772 + 1/(2 x 738) =
6.604 + 0.577 + 0.0007 = 7.182; 0.05 / (738 x 7.182) = 9.43e-6, z = 4.278. The first BH rejection always equals
Bonferroni (i = 1); BH is only less strict for the 2nd, 3rd, ... rejection, which a design taking at most 3 to the test
barely uses.

HLZ t > 3.0 in these units: one-sided p = 1 - Z(3.0) = 0.00135, two-sided 0.0027; it equals Bonferroni at 5% over
0.05 / 0.00135 = 37 one-sided tests (18.5 two-sided). It is far below the Bonferroni z for the E.33 search sizes (3.8
to 4.3) and far above what 3 sealed-test hypotheses need (2.128).

**Dependence: what a max-statistic method (RC, SPA, Romano-Wolf) saves over Bonferroni.** 95% quantile of the
maximum of m equicorrelated standard normals (one factor; max of m iid normals drawn exactly by the inverse CDF of
U^(1/m); 200,000 draws):

| m | rho = 0 | rho = 0.5 | rho = 0.8 | Bonferroni |
|---|---|---|---|---|
| 738 | 3.812 | 3.472 | 2.903 | 3.816 |
| 1,538 | 3.987 | 3.607 | 2.995 | 3.994 |
| 5,538 | 4.283 | 3.844 | 3.152 | 4.288 |

Check: at rho = 0 the simulated quantile matches Bonferroni to 0.005, as it should for independent tests. Correlated
configurations (shared features, neighbouring parameters) lower the max-statistic bar by 0.3 to 1.1 in z; Bonferroni,
Holm and BY cannot use that.

**DSR as a test.** With V = 1/T, DSR >= 0.95 means t >= e(N) + 1.645 (section d.2), and the chance that any of N
independent null trials passes is 1 - Z(t*)^N = 5.5e-4 (N = 738, t* 4.813), 4.0e-4 (1,538, t* 5.020), 2.3e-4 (5,538,
t* 5.359) (`M5a_calc2_out.txt`). So "DSR >= 0.95" is about 100 times stricter than an FWER 5% test at the same N
(compare Bonferroni z 3.8-4.3 above); it is not an alpha-level procedure, and 1 - DSR is not a p-value with nominal
size.

**The one-shot test with at most 3 candidates (Holm over 3, one-sided 0.05):** first p <= 0.0167 (z >= 2.128), second
p <= 0.025 (z >= 1.960), third p <= 0.05 (z >= 1.645). If the lead adds a family layer by Bonferroni over 3 x K:
K = 4 gives z >= 2.638, K = 5 gives z >= 2.713. What this means in ZM units (test window about 899 trade dates; h = 15
min, sigma 12.20 ticks, c = 1.59; one non-overlapping trade a date):

| Bar | Per-trade SR = z / sqrt(899) | Net ticks a trade | Gross ticks a trade |
|---|---|---|---|
| z 1.645 | 0.0549 | 0.67 | 2.26 |
| z 2.128 (Holm first, Bonferroni over 3) | 0.0710 | 0.87 | 2.46 |
| z 3.0 (HLZ) | 0.1001 | 1.22 | 2.81 |
| the same at 449 trades (every other date), z 2.128 | 0.1004 | 1.23 | 2.82 |

Power of the first Holm step (z 2.128) and of HLZ (3.0) at 899 trades, for a true net per-trade SR: 0.1689 (the
discovery DSR bar of d.3, gross 3.65): expected z = 0.1689 x sqrt(899) = 5.06, power 0.998 and 0.98; 0.0845 (half that
bar, gross 2.62): z 2.53, power 0.66 and 0.32; 0.060 (gross 2.32): z 1.80, power 0.37 and 0.12. Because the discovery
estimate of the winner is inflated by selection, the true SR is likely well below its discovery value, so an extra
HLZ hurdle at the test costs most of the power exactly where the candidate is real but modest.

### f.4 Which fits the design (for the lead to decide)
1. Discovery (M configurations, choose at most 3): the question is "does the best of this search beat zero after
   selection?", an FWER-of-the-max question. Fits: the program's DSR at the cumulative N (its bar; strictest, d.7) and,
   as a calibrated companion, a Romano-Wolf stepdown or Hansen SPA on the discovery daily net P&L matrix with a
   stationary bootstrap, which uses the configurations' correlation and gives a p-value with nominal size. FDR
   methods (BH, BY, Storey) answer a question this design does not ask (what share of many discoveries is false), and
   Storey's pi0 is unreliable under the strong dependence of a parameter grid.
2. One-shot test (at most 3 hypotheses, sealed 2017-05..2020-11 data): Holm over the tested candidates at one-sided 0.05
   (the program's `holm_tier_a` with K counting only families that send a candidate) controls FWER without any
   dependence assumption. No N-deflation is needed for validity, because the test data played no role in selection;
   HLZ t > 3.0 or a family layer are extra conservatism with the power cost shown above.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
3. Benchmark: for a directional ZM rule the RC/SPA benchmark should be the rule's unconditional counterpart (the
   program's drift benchmark, E.28 1h V10), not zero, so that drift in 2020-24 does not pass as skill.

### f.5 Data it needs
Discovery: the dates x configurations daily net P&L matrix (816 x M) for RC/SPA/Romano-Wolf and DSR; a block length
for the stationary bootstrap, declared in advance (for example the mean of 5 trade dates). Test: per-candidate daily
net P&L over the sealed window, and HAC or block-bootstrap p-values (the program's Newey-West t, E.28 1a S2).

### f.6 Leakage traps and tests
| Trap | Test |
|---|---|
| The test statistic, sidedness or alpha chosen after seeing results | Frozen and hashed in the protocol before the run; the runner refuses other values |
| K (families) or m counted after results (dropping a family that failed) | K and m fixed by the registered candidate list; `holm_alpha_k` takes K from it |
| Per-trade p-values from overlapping trades | Use daily P&L with Newey-West or block bootstrap; compare with per-trade p (overlap diagnostic of d.5) |
| Bootstrap block length tuned to the result | Declared in the protocol; a sensitivity row at half and double length, reported only |
| Benchmark = zero for a directional rule in a trending window | RC/SPA run against the unconditional counterpart; report both |
| Sealed data touched by threshold setting (variance, moments, block length) | Everything set from discovery; seal check before the test run |

### f.7 Compute
RC, SPA and Romano-Wolf on an 816 x 5,000 daily matrix (33 MB): B = 2,000 stationary-bootstrap resamples, each a row
gather and 5,000 column means (about 4 million operations), about 8 x 10^9 operations in all, seconds to a minute in
NumPy [estimate]; Romano-Wolf repeats the max per step on shrinking sets. BH, BY, Holm and Bonferroni are instant.

### f.8 Verdict
- Holm over the at most 3 tested candidates: USE at the test (already coded).
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
- DSR at cumulative N: USE at discovery (program bar), knowing it is about 100 times stricter than a 5% FWER test.
- Romano-Wolf stepdown or Hansen SPA (studentised, stationary bootstrap, drift benchmark): MAYBE, as the calibrated
  discovery p-value beside DSR; the lead decides whether it gates or is reported.
- White's RC: SKIP in favour of SPA or Romano-Wolf (Hansen: RC is less powerful and sensitive to poor alternatives,
  which a parameter grid has many of).
- BH, BY, Storey: SKIP (they control a quantity the design does not use).
- HLZ t > 3.0: MAYBE, lead's conservatism call; it is redundant at discovery (weaker than DSR and Bonferroni at N) and
  costly at the test.

### f.9 Evidence
| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| t > 3.0 hurdle | Harvey, Liu, Zhu 2016, RFS (Duke author copy) | "A new factor needs to clear a much higher hurdle, with a t-statistic greater than 3.0." | harvey_liu_zhu_2016_rfs.pdf.txt l.16-17 |
| t of 3.0 and its p | same | "While a t-statistic of 3.0 (which corresponds to a p-value of 0.27%) seems like a very high hurdle, we also argue that there are good reasons to expect that 3.0 is too low." | same, l.1752-1754 |
| FWER versus FDR levels | same | "a t-statistic of 3.9 and 3.0 is needed to control FWER at 5% and FDR at 1%, respectively" | same, l.1641-1642 |
| Bonferroni rule | same | "Reject any hypothesis with p-value ≤ αw/M" (layout garbled: "≤ αMw") | same, l.685-686 |
| Holm rule | same | "Let k be the minimum index such that p(b) > αw/(M+1−b)" (layout garbled) and "Holm’s adjustment is a step-down procedure" | same, l.788-800 |
| BY constant | same | "Benjamini and Yekutieli (2001) show that setting c(M) at ... [sum 1/j] allows the procedure to work under arbitrary dependency among the test statistics" | same, l.880-886 |
| BH procedure | Benjamini and Hochberg 1995, JRSS B (third-party copy) | "let k be the largest i for which P(i) ≤ (i/m) q*; then reject all H(i) i = 1, 2, . . . k." (OCR-garbled in the file); "Theorem 1. For independent test statistics and for any configuration of false null hypotheses, the above procedure controls the FDR at q*." | benjamini_hochberg_1995.pdf.txt l.215-220 |
| BH under PRDS; BY | Fithian and Lei 2020, arXiv 2007.10438 (secondary statement of BY 2001; BY's own paper failed to download) | "Benjamini and Yekutieli (2001) show that the BH(α) procedure controls FDR conservatively at αm0/m, provided that p−i is PRD on pi"; "the much more conservative BH(α/Lm) procedure controls FDR at level α under arbitrary dependence" | fithian_lei_2020_arxiv_2007_10438.pdf.txt l.118-120, l.132-134 |
| Storey pi0 fails under dependence | same | "the Storey-BH method (Storey et al., 2004), whose estimate of m0/m can fail badly under dependence" | same, l.122-124 |
| q-value definition | Storey and Tibshirani 2003, PNAS (course copy) | "The q value of a particular feature can be described as the expected proportion of false positives among all features as or more extreme than the observed one." (left column) | storey_tibshirani_2003_pnas.pdf.txt l.227-230 |
| Romano-Wolf stepdown | Romano and Wolf 2005, Econometrica (UZH copy) | "asymptotically controls the familywise error rate. Compared to related single-step methods, the procedure is more powerful and often will reject more false hypotheses. In addition, we advocate the use of studentization when feasible." | romano_wolf_2005_econometrica.pdf.txt l.9-11 |
| RC null and statistic | White 2000, Econometrica (course copy) | "Ho : max k=1,...,l E(f*_k) ≤ 0" and "V_l ≡ max k=1,...,l n^1/2 f_bar_k" (OCR-garbled) | white_2000_reality_check.pdf.txt l.208, l.283 |
| What RC does | same | "This permits data snooping to be undertaken with some degree of confidence that one will not mistake results that could have been generated by chance for genuinely good results." (abstract) | same, l.19-22 |
| SPA versus RC | Hansen 2005, JBES (UNC repository copy) | "The new test compares favorably to the reality check (RC) for data snooping, because it is more powerful and less sensitive to poor and irrelevant alternatives." | hansen_2005_spa_unc.pdf.txt l.5-6 |
| SPA recentring threshold | same | "µ̂k = d̄k 1{n1/2 d̄k /ω̂k ≤− 2 log log n}" (square root lost in extraction) | same, l.227 |
| Holm 1979 original | Holm 1979, Scand. J. Statist. | download timed out twice (logged); procedure taken from HLZ 2016 [original unverified] | none |
| Benjamini-Yekutieli 2001 original | Annals of Statistics | Project Euclid returned a 1 KB HTML page, the TAU author copy failed twice (logged); taken from Fithian-Lei 2020 and HLZ 2016 [original unverified] | none |

## Planner pointers owned by this section

| Pointer (reports/stage_e32_inputs/planner_research_soy_complex.md) | Status | Evidence and what differs |
|---|---|---|
| "At most 4-5 families, with Holm or Bonferroni across families and a deflated Sharpe or White's reality check within each." (l.108-109) | PARTLY VERIFIED | Holm and Bonferroni control FWER (HLZ 2016 l.667-668: "Both Bonferroni and Holm control FWER, and BHY controls FDR"), and the program already codes the across-family layer (`holm_alpha_k` = 0.05/K, screening/stage_e_stats.py:288). What differs: (1) Bonferroni across K families with Bonferroni inside each is identical to a global Bonferroni (0.05/4/50 = 0.05/200: z 3.481 both ways; same at m = 1,000 and 5,000), so the family layer gains power only when the within-family method uses the configurations' correlation (RC, SPA, Romano-Wolf: 0.3-1.1 z lower at rho 0.5-0.8, f.3). (2) "DSR within" does not combine with Holm: DSR >= 0.95 is not an alpha-level test (size 2-6 x 10^-4 under V = 1/T, f.3) and 1 - DSR is not a p-value, so Holm over DSRs is not a defined FWER procedure. RC or SPA within plus Holm across is coherent; Hansen 2005 shows SPA dominates RC. (3) "4-5 families" has no source; it is a design choice. (4) For the one-shot test, Holm over the at most 3 candidates already covers families if K counts only families that send one. |
| "Walk-forward validation with purge and embargo of at least the label horizon plus one session" (l.120-121) | PARTLY VERIFIED | Purge of at least the label horizon is LdP's rule (purging, LdP 2018 l.506-507), and walk-forward under expected non-stationarity is supported by Li 2026 (l.750-752) and Cerqueira et al. 2020 (l.36-39). What differs: (1) no source gives "one session" as the embargo; AFML's rule is 0.01T, which is 8.16 trade dates on 39 months (a.2), and Li's is H + c tau with c 2-3; one session is a defensible, shorter engineering default that should come with the 1/5/20-date sensitivity diagnostic (a.5). (2) With session-aligned folds and labels clipped at the 13:20 close, the "label horizon" part costs nothing (the purge set is empty), so the rule reduces to a 1-date embargo. (3) LdP 2018 (l.538-544) warns that walk-forward tests one path that can be overfit and that walk-backward is equally legitimate; the sealed test is backward in time (2017-20 before 2020-24), so a reversed walk-forward diagnostic is the closer rehearsal (c.3). |

## Summary of findings for the lead
1. DSR at the E.33 search sizes is a t-bar of about e(N) + 1.645: 4.81 (N = 738), 5.02 (1,538), 5.36 (5,538) under the
   null-calibrated V = 1/T, independent of horizon and frequency; on ZM that is an annualised Sharpe of 2.7-3.0 over
   39 months, or gross 2.6-2.7 ticks a 15-minute trade at four non-overlapping trades a day, 3.6-3.9 at one a day.
   Skew and kurtosis move it by at most 2% at per-trade Sharpe 0.1-0.3.
2. Pair the empirical cross-trial V with the literal N (the program's current pairing; conservative), or V = 1/T with
   an effective N, never the empirical V with an effective N (double discount; shown by simulation in d.3 (v)).
3. The one-shot test of at most 3 candidates needs Holm over 3 (z 2.128 / 1.960 / 1.645 one-sided); N-deflation at the
   test is not needed for validity. HLZ t > 3.0 there costs half the power for a modest true edge (0.66 to 0.32 at a
   true net Sharpe of 0.0845 a trade, 899 trades).
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
4. PBO on 39 months is noisy: a null search's PBO ranges about 0.13-0.83 (8 blocks); report it with that band, do not
   gate on PBO < 0.5. The PBO paper's "12, 780" is a typo for C(16,8) = 12,870.
5. Session-aligned folds (whole trade dates, labels clipped at 13:20 CT) make purging free; the embargo is a dependence
   choice (1 date default, AFML 0.01T = 8.2 dates, feature lookback up to 20 dates) costing at most about 3% of
   training data per split.
6. CPCV path Sharpes measure model instability, not sampling error (all paths share the same test dates); CPCV on
   every configuration is affordable only for linear models or small grids (225,000 GBM fits at N = 5,000).
7. The sealed test runs backward in time from discovery; a reversed walk-forward inside discovery rehearses it.

## Gaps, failures and negative evidence
- Not fetched (no open copy): AFML 2018 chapters 7, 11, 12, 14 and MLAM 2020; covered by the author's own JPM summary
  (lopezdeprado_2018_10reasons_jpm) and the Lopez de Prado-Lewis ONC paper; book text [unverified].
- Download failures (logged in log.tsv): Holm 1979 (timed out twice), Benjamini-Yekutieli 2001 (Project Euclid
  returned a 1 KB HTML page; the TAU author copy failed twice), Bergmeir-Hyndman-Koo 2018 (403 and a non-PDF page).
  Their procedures are quoted from HLZ 2016 and Fithian-Lei 2020 as secondary statements.
- The BLdP 2014 example inputs were lost in pdftotext (equation images); confirmed only by reproducing the three
  printed outcomes. Lo 2002 / Mertens 2002 (Var(SR_hat) ~ 1/T) not fetched; used as a stated assumption.
- Session times (19:00-07:45 and 08:30-13:20 CT) and the CBOT holiday list are assumptions from the brief and my own
  list, not verified (the E.32 CME rule forbids fetching cmegroup.com); trade-date counts carry about +-3 dates of
  error. Kurtosis and skew values in d.3 are illustrative, not measured. The 0.5 s linear-model fit time is assumed;
  only the 6 s GBM figure is measured (E.28).
- Negative evidence: no source found that compares forward and backward validation on futures data (arXiv API
  queries on 2026-10-27 surfaced none; the closest, Nikolopoulos 2026, is a placebo-audit framework); no source
  supports "one session" as an embargo width; no source supports a PBO bar of 0.5.
- WebSearch: 0 calls in this spawn (discovery by the arXiv API and direct author-copy URLs).
