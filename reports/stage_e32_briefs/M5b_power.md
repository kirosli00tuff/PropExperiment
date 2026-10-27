# Stage E.32 Part M5 (second half): safe feature importance, stability requirements, and power for E.33

Worker PowerStability-OpusHigh (Opus 5.5, high), ROOT M5b_power, started 2026-10-27 00:29 PDT.
Inputs read by line range: READER_BRIEF.md, E.28 READER_RULES.md, reports/stage_e28_methods_brief.md 2.7 (sections 4,
5, 12) and 2.11 (sections 3-4), M5a_validation.md section 0 (shared quantities), R4_events.md lines 230-240 (event
count). M5a owns CV schemes, DSR, PBO and FDR; this file cites "M5a" for them and does not repeat them.

No market data was read. Every number below is arithmetic or a synthetic Monte Carlo on the standard ZM numbers.
Scripts (written by me, run at nice 10): work/M5b_power/M5b_days.py (trade-date count), M5b_calc.py
(-> M5b_calc_out.txt), M5b_calc2.py (-> M5b_calc2_out.txt). Pages and log.tsv: pages/M5b_power/.

## 0. Shared quantities (assumptions marked)

| Quantity | Value | How |
|---|---|---|
| ZM sigma_1m | 3.15 ticks | brief, E.28 A0 Table 1 (2022-11..2023-10) |
| sigma_h under a random walk (ASSUMPTION: increments uncorrelated, constant variance, so sigma_h = sigma_1m sqrt(h)) | 5 min: 3.15 x 2.2361 = 7.044; 15 min: 3.15 x 3.8730 = 12.200; 60 min: 3.15 x 7.7460 = 24.400; 75 min: 3.15 x 8.6603 = 27.280 ticks | M5b_calc_out.txt "constants". Check: 12.200 x 2 = 24.400 = sigma_60, since sqrt(60/15) = 2 |
| Market-order round-trip break-even at Topstep | 1.59 ticks | stage_e28_ranking.md line 130 (as quoted by M5a 0.1; the brief's "about 1.6") |
| Test window trade dates, 2017-05-01..2020-11-30 | **904** (range 903-905) | 936 weekdays (counted by script) minus 32 typed CBOT-grain full closures (New Year, MLK, Presidents, Good Friday, Memorial, July 4, Labor, Thanksgiving, Christmas, observed dates; plus 2018-12-05, the national day of mourning, [unverified] whether grains closed). Typed from memory, not from a CME page (the E.32 CME rule forbids fetching one); DataFacts owns the real calendar. **M5a 0.1 has 899 (it assumed 37 closures). The two differ by 5 dates; neither is read from data. The difference moves every per-day rate below by 0.6%.** |
| Discovery trade dates, 2020-12-01..2024-02-29 | 816 | 848 weekdays minus 32 typed closures (adds Juneteenth 2022-06-20 and 2023-06-19). Agrees with M5a's 816 |
| Session minutes per trade date | 765 overnight + 290 day = 1,055 | brief's session times; [unverified here, DataFacts owns] |
| Calendar months | test 43, discovery 39 | May 2017..Nov 2020 = 8+12+12+11; Dec 2020..Feb 2024 = 1+12+12+12+2 |
| 3-month blocks | test 14 full + 1 month; discovery 13 | 43 = 14 x 3 + 1; 39 = 13 x 3 |
| Critical values | one-sided alpha 0.05/3: z = 2.1280; t > 3.0 (one-sided alpha 0.00135); power 0.8: z_b = 0.8416; one-sided 0.05: 1.6449 | Python statistics.NormalDist |

[MathReview C-7 (lead: accepted): row "Test window trade dates": 2018-12-05 is not a grain full closure in the program's calendars (31 closures), which are the source of record for E.33, so the count is 905, not 904. Every "/test day" figure moves by 0.1% (e.g. 8,786/905 = 9.71, not 9.72; 1,313/905 = 1.45 unchanged) and the gate formula "k_test x 904" should read 905 (also at original lines 361-390, 466-469, 529, 583-587 and 610-611); no verdict moves.]

Why "net mu in {0.25, 0.5, 1.0} ticks" is the right scale: at h = 15 minutes and a market-order round trip of 1.59
ticks, net mu = 0.5 tick needs a gross 2.09 ticks, and under the assumption that the sign of the move is
independent of its size and moves are normal, gross = (2p - 1) E|r| with E|r| = sigma_h sqrt(2/pi) =
12.200 x 0.7979 = 9.734 ticks, so the hit rate must be p = 0.5 + 2.09 / (2 x 9.734) = 0.6074 (M5b_calc2_out.txt).
At 5 minutes the same net edge needs p = 0.6859, and at 60 minutes p = 0.5537. These are large hit rates for a
minutes-scale futures signal; they are the scale against which every importance number in (a) should be read.

## (a) Feature importance on purged folds: MDI, MDA, SFI, clustered MDA, and why importance must not steer choices

### a.1 Core idea
Feature importance asks which inputs a fitted model relies on. MDI (mean decrease impurity) is computed in-sample
from the tree splits. MDA (mean decrease accuracy, Breiman's permutation importance) is the drop in an
out-of-sample score when one feature's values are shuffled in the test fold. SFI (single feature importance) is the
out-of-sample score of a model fitted on that feature alone. Correlated features share credit (the "substitution
effect"), so MDA can call two near-copies of a real signal both unimportant; clustered MDA permutes a whole cluster
of related features at once. Under V43 importance is a diagnostic that is reported, never a lever that changes the
frozen pipeline after its folds have been scored.

### a.2 Equations
Notation: K purged and embargoed folds (scheme: M5a (a)); for fold k, model f_k is fitted on the training part and
scored on the test part T_k with n_k rows; S(f, X, y) is a score where higher is better (accuracy, minus log loss,
or the net P&L of the traded rule in ticks); X^{(j,pi)} is X with column j permuted by a random permutation pi
inside T_k only; C is a cluster (a set of columns); R is the number of permutation repeats.

- MDI (Breiman 2001 Gini importance, the "Mean decrease impurity" of AFML ch. 8):
  MDI_j = (1/B) sum_{b=1..B} sum_{s in tree b, split on j} w(s) [i(s) - (n_L/n_s) i(L) - (n_R/n_s) i(R)],
  with B trees, w(s) the share of training rows reaching node s, i(.) the impurity (Gini or entropy) and L, R the
  children. It is computed on training rows only, is never negative, and needs no test data. (Standard definition;
  wording as in Falces Marin et al. 2022: "a feature-specific measure of the mean reduction of weighted impurity over
  all the nodes in the tree ensemble".)
- MDA (Breiman 2001 section 10 used out-of-bag rows; López de Prado's version uses purged CV test folds):
  MDA_j = (1/K) sum_k (1/R) sum_{r=1..R} [ S(f_k, X_{T_k}, y_{T_k}) - S(f_k, X_{T_k}^{(j,pi_r)}, y_{T_k}) ].
  A relative form divides each term by |S(f_k, X_{T_k}, y_{T_k}) - S_0|, with S_0 the score of a no-skill predictor.
- Clustered MDA: replace column j by cluster C and permute all columns of C with the SAME row permutation
  (so their mutual dependence is kept and their link to y is broken):
  MDA_C = (1/K) sum_k (1/R) sum_r [ S(f_k, X_{T_k}, y) - S(f_k, X_{T_k}^{(C,pi_r)}, y) ].
  Clusters come from a dependence matrix computed on feature values only (for example the distance
  d_ij = sqrt((1 - rho_ij)/2) and the ONC algorithm of López de Prado and Lewis, used in M5a for trial clustering).
  Clustered MDI = sum_{j in C} MDI_j. [The book's own equations were not read: MLAM section 6.5 is not available as
  free full text; the mechanism is quoted from library documentation and the published table of contents, see a.9.]
- SFI: SFI_j = (1/K) sum_k S(g_{k,j}, x_{j,T_k}, y_{T_k}) - S_0, where g_{k,j} is fitted on column j alone on fold
  k's training rows. No substitution effect (each model sees one feature), but no interactions either.
- Retrain-based importance (Hooker, Mentch and Zhou 2021: "re-learning"; also called leave-one-covariate-out):
  LOCO_j = (1/K) sum_k [ S(f_k) - S(f_k^{(-j)}) ], with f_k^{(-j)} refitted without column j. Avoids the
  extrapolation that permutation forces, at K extra fits per feature.
- Noise canary: add Q columns of pure noise (for example a block-permuted copy of a real feature); the importance
  floor is max_q MDA_{noise q}. A feature is "distinguished" only above that floor.
- Sampling noise of accuracy-based MDA: if the permutation changes the predicted class on a share f of n test rows,
  each change moves accuracy by +-1/n, so SE(MDA_j) <= sqrt(f / n) (a bound I derived; it ignores that changes
  are not independent across overlapping labels, so the effective n is smaller: see (c)).

### a.3 Worked example (standard ZM numbers; M5b_calc2_out.txt)
1. Units. At h = 15 minutes, E|r| = 12.200 x sqrt(2/pi) = 12.200 x 0.79788 = 9.734 ticks. One percentage point of
   hit rate is worth (2 x 0.01) x 9.734 = 0.195 ticks gross a trade (sign independent of size: assumption). At 60
   minutes it is 0.389 ticks; at 5 minutes 0.112 ticks.
2. Sample. Non-overlapping 15-minute labels over discovery: 1,055 min x 816 days / 15 = 57,392 rows (all sessions;
   about 15,776 for the day session only: 290 x 816 / 15 = 15,776). With 10 folds every row is tested once.
3. Noise. If shuffling a feature flips 20% of predictions, SE(MDA) <= sqrt(0.2 / 57,392) = sqrt(3.485e-6) =
   0.00187, i.e. 0.19 percentage points; a 2-SE detection floor is 0.37 points = 0.37 x 0.195 = 0.073 ticks gross.
   Check: with n = 100,000 and f = 0.2 the bound is 0.00141 (script), and 0.00187 x sqrt(57,392/100,000) =
   0.00187 x 0.7576 = 0.00142. Consistent.
4. Size of what must be found. Net 0.5 tick at h = 15 needs p = 0.6074 (section 0), i.e. 10.7 percentage points of
   hit rate over 0.5 in total, or a log-loss gain of ln 2 - H(0.6074) = 0.693147 - 0.669897 = 0.02325 nats
   (script). A feature with MDA of 1 point carries 0.195 ticks; so a tradeable model needs either a few strong
   features or many weak ones whose importance is split by substitution, which is exactly where single-column MDA
   misleads.
5. Substitution, toy arithmetic. Two features x1 and x2 with correlation 0.99 carry the same signal and the model
   splits on either. Permuting x1 alone leaves x2 intact, so MDA_x1 and MDA_x2 are both near 0 (Hooker et al.:
   permutation also makes the model extrapolate to (x1, x2) pairs that never occur, which can instead inflate both);
   permuting the cluster {x1, x2} together removes the whole signal, so MDA_C equals the full 10.7-point drop in the
   step-4 example. SFI_x1 = SFI_x2 = the full single-feature score. Reading: with correlated order-flow features
   (OFI at several lags, queue imbalance at several depths) use clustered MDA and SFI, never raw MDA alone.

### a.4 Data it needs
The frozen E.33 feature matrix (from ZM MBO; ZS and ZL MBP-1 for cross-asset features; definitions for roll and tick
size) at the label horizon, the purged fold assignment from M5a (a), and each fold's fitted model. Clustering uses
feature values only, from the training folds. Nothing from the sealed 2017-05..2020-11 window.

### a.5 Leakage and look-ahead traps, each with a test
1. MDI is in-sample: it rewards features the trees used, including overfit ones, and favours continuous and
   high-cardinality features (Strobl et al. 2007). Test: add noise canaries; MDI gives them positive importance, a
   purged-fold MDA should give them about 0. Rule: MDI is never evidence.
2. Out-of-bag importance on overlapping labels: bagged trees put the row adjacent in time (sharing most of its
   label window) in-bag, so the "out-of-bag" score is contaminated. Test: compute importance both out-of-bag and on
   purged folds for one model; any gap means leakage; ban OOB scoring (for example sklearn `oob_score`) in E.33.
3. Permuting across folds or across the embargo: the permutation must stay inside T_k. Test: assert that the set of
   row indices before and after permutation is identical within each fold.
4. Selection bias: features chosen by importance on all folds and the chosen model then cross-validated on the same
   folds. Ambroise and McLachlan (2002) show the CV error is then biased (it can reach zero on noise). Tests: (i)
   nested CV, selection inside each outer training fold, and compare with the non-nested number; (ii) a null-label
   run: permute labels in whole-day blocks, run the full pipeline including any selection step; the CV score must
   sit at chance, and a non-nested pipeline that scores above chance on shuffled labels has leaked.
5. Scalers, winsorization limits or cluster definitions fitted on all discovery rows before the split. Test: refit
   them per training fold and confirm identical test-fold predictions to 1e-9; any difference shows that test rows
   informed the transform.
6. Importance on the test window: forbidden (V43, one read). Test: the E.33 run log has no importance call after the
   seal is opened.

### a.6 Why importance must never steer a later choice inside the same data
- It is a selection step that saw the test folds. Any choice made with it (drop features, re-weight, pick a
  cluster, pick a model rung) makes the CV estimate of the result optimistic, as in a.5 item 4 above: "the
  cross-validation of the rule is not external to the selection process" (Ambroise and McLachlan 2002).
- It is an uncounted search. Under V43 every configuration enters N. A feature subset picked after reading
  importance is one draw from up to 2^F subsets (F = 64 gives 1.8e19) that N does not count, so M5a's DSR and PBO
  numbers would be computed at the wrong N.
- The Rashomon effect (Fisher, Rudin and Dominici 2019): many near-equal models rely on different features, so the
  importance ranking of one fitted model is itself unstable (Man and Chan 2020 find MDA "the least stable" of the
  three methods they test, and that no method "converges to a single feature set").
- What is allowed: (i) importance reported after the frozen grid has run, as a diagnostic and a sanity check
  (López de Prado 2018: "feature importance is a research tool, and backtesting is not"); (ii) a feature-selection
  step that is declared in the protocol, runs inside each training fold, and is counted into N as part of the
  pipeline; (iii) using importance to design the NEXT stage's grid, on new data, with the trial count carried.

### a.7 Compute (ThinkPad, 39 months; estimates, not measured)
Matrix: 860,880 one-minute rows x 64 float32 features = 220 MB (M5a 0.1 gives the row count). MDA: K = 10 fits
already exist; 64 features x 10 folds x R = 5 repeats = 3,200 predictions of about 86,000 rows each; seconds to
minutes on CPU. Clustered MDA: fewer (one per cluster). SFI: 64 x 10 = 640 single-feature fits; for a depth-3
gradient-boosted model on about 775,000 rows a fit takes seconds, so tens of minutes in total at 14 threads [guess,
no probe run]. LOCO: 640 full refits, about 64 times the cost of the base CV: run on finalists only. Memory is not
binding.

### a.8 Verdict
USE clustered MDA on purged folds with noise canaries, and SFI as the cross-check, as REPORTED diagnostics after the
frozen run. SKIP MDI as evidence (debugging aid only). LOCO: MAYBE, finalists only. Importance-driven feature
selection: SKIP unless the lead pre-declares it as a nested, N-counted step. For a minutes-scale directional ZM
search the realistic signal is a few percentage points of hit rate spread over correlated order-flow features, which
is the regime where single-column MDA understates and MDI overstates.

### a.9 Evidence
| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Permutation importance origin: out-of-bag values of one variable permuted, percent increase in error | Breiman 2001, Machine Learning 45 (academic) | "After each tree is constructed, the values of the mth variable in the out-of-bag examples are randomly permuted and the out-of-bag data is run down the corresponding tree." ... "The output is the percent increase in misclassification rate as compared to the out-of-bag rate (with all variables intact)." | breiman_2001_random_forests.pdf/.txt |
| MDI, MDA, SFI definitions; SFI avoids the substitution effect | Falces Marin et al. 2022, PLOS ONE (academic, applying AFML/MLfinlab) | "Mean decrease impurity (MDI), a feature-specific measure of the mean reduction of weighted impurity over all the nodes in the tree ensemble"; "Single feature importance (SFI), an out-of-sample estimator of the individual importance of each feature, that avoids the substitution effect found with MDI and MDA (important features are ignored when highly correlated with other important features)." | falces_marin_2022_plosone.pdf/.txt (lines 729-739) |
| Clustered feature importance comes from MLAM (2020) section 6.5.2 and is used with MDI and MDA | MLfinlab-fork documentation (practitioner software docs) | "described in the book Machine Learning for Asset Manager (snippet 6.5.2.1 page-85). This subsets can be further utilised for getting Clustered Feature Importance using the clustered_subsets argument in the Mean Decreased Impurity (MDI) and Mean Decreased Accuracy (MDA) algorithm." | mlfinlab_fork_feature_clusters.html/.txt |
| MLAM chapter 6 is "Feature Importance Analysis" | Cambridge University Press table of contents (publisher) | "6 Feature Importance Analysis 74" | lopezdeprado_2020_mlam_toc.pdf/.txt |
| Clustered MDA permutes the whole cluster jointly; ONC clustering on a dependence metric | López de Prado 2020, MLAM 6.5 | not read in full text | [unverified: book not available as free full text; mechanism as described in the docs row above] |
| AFML ch. 8 sections "Feature importance with substitution effects" (8.3) and "without substitution effects" (8.4) | AFML 2018 table of contents | search-result snippet only | [unverified: library catalogue page returned an anti-bot stub, see log] |
| Importance is a research tool, backtesting is not | López de Prado 2018, "The 10 reasons most ML funds fail", JPM (practitioner-academic) | "Remember, feature importance is a research tool, and backtesting is not." | lopezdeprado_2018_10reasons_jpm.pdf/.txt (line 183) |
| Gini (MDI) importance unreliable when predictors differ in scale or number of categories | Strobl, Boulesteix, Zeileis, Hothorn 2007, BMC Bioinformatics (academic) | "random forest variable importance measures are a sensible means for variable selection in many applications, but are not reliable in situations where potential predictor variables vary in their scale of measurement or their number of categories"; "the Gini importance is most strongly biased" | strobl_etal_2007_pmc.html/.txt |
| Permutation importance overestimates correlated predictors; conditional permutation proposed | Strobl et al. 2008, BMC Bioinformatics (academic) | "We know that the original permutation importance overestimates the importance of correlated predictor variables."; "we develop a new, conditional permutation scheme for the computation of the variable importance measure" | strobl_etal_2008_conditional_pmc.html/.txt |
| Permutation forces extrapolation; re-learning is the alternative | Hooker, Mentch, Zhou 2021, arXiv 1905.03151v2 (academic) | "breaking dependencies between features in hold-out data places undue emphasis on sparse regions of the feature space by forcing the original model to extrapolate to regions where there is little to no data"; "A more general approach is re-learning, which generally involves measuring the drop in model performance when the effects of the features in question are muted." | hooker_mentch_zhou_arxiv_1905_03151.pdf/.txt |
| Rashomon effect: different good models rely on different covariates | Fisher, Rudin, Dominici 2019, JMLR 20 (academic) | "the model used by one analyst may rely on entirely different covariate information than the model used by another analyst. This common scenario has been called the "Rashomon" effect of statistics" | fisher_rudin_dominici_2019_jmlr.pdf/.txt |
| MDA least stable; no method converges to one feature set; not only substitution | Man and Chan 2020, arXiv 2005.12483 (ICAIF'20, academic) | "the instability index of MDA computed on the validation set is consistently higher than that of LIME and SHAP, which means MDA is the least stable method"; "none of the algorithms converges to a single feature set even if the number of random iterations is large, and this isn't solely due to the substitution effect" | man_chan_2020_arxiv_2005_12483.pdf/.txt |
| Selection bias when CV is not external to selection | Ambroise and McLachlan 2002, PNAS 99(10) (academic) | "the cross-validation of the rule is not external to the selection process; that is, gene selection is not performed in training the rule at each stage of the cross-validation process"; "when correction is made for the selection bias, the cross-validated error is no longer zero for a subset of only a few genes" | ambroise_mclachlan_2002_pnas_pmc.html/.txt |

Stopping rule (a): 8 full-text sources read on this topic; my last 3 discovery searches (clustered feature
importance PDF, MLAM PDF, smallake mirror) surfaced no new primary text, only blogs (MQL5, IBKR Campus, Numerai
forum), which are pointers only and are not cited.

## (b) Stability across months and regimes

All P&L below is the net per-trade outcome x_i in ticks of the one frozen candidate on the window being judged
(discovery folds' out-of-sample P&L in E.33; the test window once, in the later test stage). Monte Carlo results are
synthetic (M5b_calc_out.txt sections b1-b5), not data.

### b.1 Core idea
A real minutes-scale edge should show up in most months and quarters, in every volatility regime, and should not
rest on one month. These checks are stability REQUIREMENTS, not significance tests: under the null they are weak
filters (a share-of-quarters rule passes a no-edge candidate 9-13% of the time), but they catch the failure the
t-statistic cannot see, a total built from one episode. Significance comes from the HAC t (M5a, and c.2 here) and a
stationary bootstrap that resamples whole trade dates.

### b.2 Equations
Notation: trade dates t = 1..T; D_t = sum of x_i over trades whose ENTRY falls on date t (zero if none); months
m = 1..M with P_m = sum_{t in m} D_t; blocks of 3 months q = 1..Q with P_q; total P = sum_m P_m; overall
noncentrality delta = E[t-stat] = mu sqrt(n_eff) / sigma (c.2).

1. Share of months positive: S_M = #{m : P_m > 0}. Null (mu = 0, months independent, P(P_m > 0) = 1/2):
   S_M ~ Binomial(M, 1/2), P0(S_M >= k) = sum_{j=k..M} C(M, j) 2^{-M}.
   Alternative, equal trades per month: P(P_m > 0) = Phi(delta / sqrt(M)), because each month carries 1/M of the
   total and its own z-score has mean delta / sqrt(M).
2. Two-thirds-of-quarters rule (planner pointer): pass if S_Q >= ceil(2Q/3).
3. Dominance: share_max = max_m P_m / P (defined when P > 0); leave-one-month-out t:
   t_{-m} = (P - P_m) / (s_LR sqrt((T - T_m))) computed with the same HAC estimator on the dates outside month m.
   In the Monte Carlo, months are iid N(delta/sqrt(M), 1) units, so t_{-m} = (sum - x_m)/sqrt(M - 1).
4. Stationary bootstrap by day (Politis and Romano 1994): build D*_1..D*_T by taking D*_1 = D_{I_1} with I_1
   uniform on 1..T, and, given D*_i = D_J, set D*_{i+1} = D_{J+1} with probability 1 - p and a fresh uniform draw
   with probability p (indices past T wrap to the start). Block lengths are then geometric with mean 1/p, and the
   resampled series is stationary conditional on the data. One-sided bootstrap p-value for H0: mu <= 0:
   p_boot = (1 + #{b : mean(D*_b) - mean(D) >= mean(D)}) / (B + 1), B >= 10,000.
   Mean block length 1/p by Politis and White (2004) with the Patton, Politis and White (2009) correction, as
   implemented in the `arch` package's `optimal_block_length`:
   b_SB = (2 g^2 / D_SB)^{1/3} T^{1/3}, D_SB = 2 sigma_LR^4 (corrected), so b_SB = (g^2 / sigma_LR^4)^{1/3} T^{1/3},
   g = sum_{k=-m..m} lambda(k/m) |k| gamma_k, sigma_LR^2 = sum_{k=-m..m} lambda(k/m) gamma_k,
   lambda(x) = min(1, 2(1 - |x|)) (flat-top), gamma_k the sample autocovariance of D_t at lag k, m chosen from the
   autocorrelations (arch docs: the first m where k_n consecutive autocorrelations are inside
   +-2 sqrt(log10(T)/T), k_n = max(5, log10 T)).
   For an AR(1) day series with coefficient phi (my closed form, flat-top window ignored):
   gamma_k = gamma_0 phi^|k|, g = 2 gamma_0 phi/(1 - phi)^2, sigma_LR^2 = gamma_0 (1 + phi)/(1 - phi), so
   b_SB = T^{1/3} (2 phi / (1 - phi^2))^{2/3}.
5. Regime splits. Volatility terciles: v_t = a causal volatility measure known before the session that contains the
   trade (for example the realized volatility of ZM 1-minute returns over the previous 20 trade dates); cut points
   c_1 < c_2 are the 1/3 and 2/3 quantiles of v_t over DISCOVERY dates and are frozen in the protocol; the test
   window uses the same cut points (its terciles may be unequal in size). Oil-share regime: OS_t = 0.11 O / (0.022 M +
   0.11 O) with O the ZL price in cents/lb and M the ZM price in USD per short ton, from the previous settlement
   (R3a_crush.md lines 51-60, 44 lb board crush), split at a frozen discovery median or at fixed values. Per-regime
   statistics: mean, HAC t and trade count in each cell; with a share 1/3 of the trades, z_r has mean delta/sqrt(3).

### b.3 Worked examples (M5b_calc_out.txt)
1. Binomial null, months (b1). Test window M = 43: share >= 2/3 means k = ceil(28.67) = 29, P0 = 0.0158; share
   >= 0.6 (k = 26): P0 = 0.1110; share >= 0.75 (k = 33): 0.0003. Discovery M = 39: k = 26, P0 = 0.0266.
   Check: the normal approximation for M = 43 gives z = (28.5 - 21.5)/sqrt(43 x 0.25) = 7/3.279 = 2.135, upper
   tail 0.0164, close to 0.0158.
2. Two-thirds of quarters (b1, b2). Discovery Q = 13: k = 9, P0 = 0.1334 (so 13% of no-edge candidates pass the
   rule by itself). Test Q = 14: k = 10, P0 = 0.0898. Under an edge sized for 80% power at t > 3 (delta = 3.84, c.3),
   each quarter is positive with probability Phi(3.84/sqrt(13)) = Phi(1.065) = 0.857; Monte Carlo: P(rule passes)
   = 0.971 (discovery), 0.949 (test); P(t > 3 AND rule) = 0.797 (discovery) and 0.791 (test) against P(t > 3) =
   0.800. **Reading: the two-thirds-of-quarters rule costs about 1 point of power at delta = 3.84 and 1-2 points at
   delta = 3.0; it is cheap insurance, not a filter that adds significance.** A two-thirds rule on MONTHS costs more:
   at delta = 3.84 over 43 test months, P(t > 3 AND >= 29 positive months) = 0.726 vs 0.800, a 7-point power loss;
   at delta = 3.0, 0.429 vs 0.501.
3. Dominance (b3), given t > 3, delta = 3.84: the largest month carries a median 10.3% (43 months) or 10.8% (39) of
   the total, 99th percentile 16.9% / 17.7%; a rule "no month above 25% of total P&L" rejects essentially no real
   edge (P(share <= 0.25 | t > 3) = 1.000 in 200,000 draws). The leave-one-month-out minimum t has 1st percentile
   2.63 (43 months); a rule "every LOMO t > 2.5" keeps 99.9% of real-edge passes. Counter-case: 42 noise months and
   one month at +6 SD gives t > 3 in 1.7% of draws (b3 "spike example"). Check by hand: with 42 null months the
   total is N(6, 42), and t > 3 needs total > 3 sqrt(43) = 19.67, i.e. z > (19.67 - 6)/6.481 = 2.11, tail 0.0174.
   Matches 0.0173. Among those false passes (M5b_calc3_out.txt, 2,000,000 draws, spike month = 6 + its own N(0,1)
   noise): the 25% rule catches 78.5%, the LOMO t > 2.5 rule 66.3%, either rule 82.4%; with a +10 SD spike month
   (t > 3 in 7.0% of draws) the 25% rule catches 100%. So the dominance rules remove most, not all, one-episode
   passes, at almost no cost to real edges.
4. Volatility terciles (b4). With 1/3 of the trades in each tercile, z_r has mean delta/sqrt(3). At delta = 3.84:
   2.217, P(all three positive) = Phi(2.217)^3 = 0.9867^3 = 0.961; P(all three z > 1.645) = Phi(0.572)^3 = 0.716^3
   = 0.368. **Same sign in every tercile is a cheap requirement (4% power loss); significance in every tercile is not
   (it keeps 37% of real edges).** Requiring z > 1.0 in each keeps 70%.
5. Stationary-bootstrap block length (b5). Test window T = 904 trade dates, phi = 0.1: T^{1/3} = 9.670,
   2 phi/(1 - phi^2) = 0.2/0.99 = 0.20202, ^(2/3) = 0.34427, b_SB = 9.670 x 0.34427 = 3.33 days (p = 0.300).
   Numeric sums agree to 3 decimals (script). phi = 0.05: 2.09 days; phi = 0.2: 5.39; phi = 0.3: 7.33.
   Discovery T = 816, phi = 0.1: 3.22 days. Sanity bound: b_SB -> 0 as phi -> 0 (iid days, no blocks needed); the
   arch implementation floors it at 1.
6. Month-sign test under skew (a trap, see b.5 item 1): with mean zero, P(P_m > 0) = 1/2 only if the monthly P&L is
   symmetric. A strategy with many small wins and rare large losses (negative skew, typical of fading moves with a
   wide stop) has P(P_m > 0) > 1/2 at zero mean, so the binomial null overstates significance. The day-block
   bootstrap null, which resamples the de-meaned D_t, handles this.

### b.4 Data it needs
D_t from the candidate's frozen trade list (entries, exits, net P&L in ticks, entry timestamps), the trade-date
calendar (DataFacts), causal ZM realized volatility (from ZM MBO trades or 1-minute bars built from it), ZM and ZL
previous settlements for the oil share (ZL from MBP-1; settlements: if no statistics schema is owned, use the last
trade before the 13:15 CT close, as DataFacts specifies). All on discovery; the test window only at the one test.

### b.5 Leakage and look-ahead traps, each with a test
1. Binomial null under skew (b.3 item 6). Test: compute the null share-of-months distribution by stationary
   bootstrap of D_t - mean(D) and compare with the binomial; report the bootstrap one.
2. Tercile cut points computed on the whole sample including the test window. Test: cut points are written into
   the frozen protocol with its hash before the seal is opened; the test-stage script reads them, never recomputes.
3. Same-day volatility that includes the trade's own path. Test: assert v_t's latest input timestamp < the entry
   timestamp for every trade; a shift test (v lagged one more day) must leave tercile labels unchanged on days where
   the lag already applies.
4. Bootstrap over trades instead of days: trades on the same day share shocks (c.2 design effect). Test: compare
   the bootstrap SE over trades with the one over days; a smaller trade-level SE is the symptom.
5. Choosing the block length or the month/quarter partition after seeing results. Test: the rule (arch
   `optimal_block_length`, column b_sb, on the discovery D_t) and the partition (calendar months; 3-month blocks
   from the window start) are in the protocol; the test stage recomputes b_sb on test D_t by the same rule.
6. Months with few trades: a month with 3 trades is "positive" by noise. Test: report trades per month; count a month
   in S_M only if it has at least a declared minimum, or use 3-month blocks (the planner's quarters).
7. Oil-share split chosen after looking: the planner expects a regime break between discovery (renewable-diesel era)
   and test (2017-20); the split value must be frozen before the test, and any OS-conditioned rule counts into N.

### b.6 Compute
Trivial: D_t has under 1,000 entries; 10,000 stationary-bootstrap resamples of 904 values take well under a second
in NumPy; the Monte Carlo above (200,000 draws per cell) ran in seconds.

### b.7 Verdict
USE: (i) the day-block stationary bootstrap p-value next to the HAC t; (ii) the two-thirds-of-3-month-blocks rule
as a stability requirement (about 1 point of power at delta 3.84); (iii) a dominance requirement "no single month
above 25% of total net P&L" plus "every leave-one-month-out t above a declared floor" (2.5 costs about 0.1 point of
power at delta 3.84); (iv) same sign of mean net P&L in each frozen volatility tercile. MAYBE: oil-share regime
split, reported descriptively (the regime differs between windows by the planner's own account, so a hard
requirement could fail a real edge for a known reason). SKIP: requiring significance inside every regime cell
(keeps only 37% of real edges at delta 3.84). The thresholds are the lead's decision (P8); these numbers are their
cost.

### b.8 Evidence
| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Stationary bootstrap algorithm: continue the block with probability 1 - p, jump with p; resampled series stationary | Politis and Romano 1994b, Statistica Sinica 4, 461-476, p. 468 (academic; same authors, describes the JASA 1994 scheme) | "let X*_{i+1} be equal to X_{J+1} with probability 1 - p and picked at random from the original n observations with probability p. This description makes it clear that, conditional on X_1, ..., X_n, the new process X*_1, ..., X*_n is indeed stationary." (read from the scanned page image; subscripts typed) | politis_romano_1994_stat_sinica.pdf (scanned, no text layer; read as images, pp. 1-2, 8-11) |
| Wrap-around past n | same, p. 470 | "with n fixed, let X_j for j > n be defined to be X_{j-n}." | same |
| The stationary bootstrap was introduced by Politis and Romano (1991; published JASA 89(428), 1994) for weakly dependent stationary data | same, abstract p. 461 | "In Politis and Romano (1991), a resampling procedure, called the stationary bootstrap, is introduced as a means of calculating standard errors of estimators and constructing confidence regions for parameters based on weakly dependent stationary observations." | same |
| JASA 1994 paper itself (geometric block lengths in the abstract) | Politis and Romano 1994, JASA 89, 1303-1313 | not read in full text | [unverified: JSTOR only; repository record page returned a Cloudflare 403] |
| Optimal block length corrected: D_SB = 2 g^2(0) | Patton, Politis, White 2009, Econometric Reviews 28(4) (academic) | "The correct value for the variance constant DSB defined in Theorem 3.1 of Politis and White (2004) is DSB = 2g 2 (0);" (pdftotext layout) | patton_politis_white_2009_correction.pdf/.txt |
| Implementation: b_opt = (2 g^2 / d_i n)^{1/3}, flat-top lambda, m rule | arch documentation, optimal_block_length (software docs) | "The block length is then computed as b^{OPT}_i = \left(\frac{2g^2}{d_{i}} n\right)^{\frac{1}{3}}"; "h(x) & = \min(1, 2(1-|x|))"; "d_{i} & = c_{i} \left(\hat{\sigma}^2\right)^2"; "the two remaining constants c_i are 2 for the Stationary" | arch_docs_optimal_block_length.html; arch_bootstrap_base_py.txt (source read, not run) |
| Stability by month and by volatility regime is step 6 of the E.28 minimum research process | E.28 2.11 section 4 (program) | "stability by month and by volatility regime; if every configuration breaks at the same date, record a regime change, not a model failure (E9)." | reports/stage_e28_methods_brief.md line 11968 |
| Board crush 44 lb meal, 11 lb oil; oil share formula | R3a_crush.md lines 27-60 (E.32 sibling worker, sources there) | "OS = 0.11 * O / (0.022 * M + 0.11 * O) under 44 lb" | reports/stage_e32_briefs/R3a_crush.md |

Stopping rule (b): the binomial, Monte Carlo and AR(1) block-length results are my own derivations and need no
source beyond those above; 3 discovery searches for the JASA full text found none.

## (c) Power: trades needed to detect a minimum net edge, with overlap and autocorrelation

### c.1 Core idea
The one-shot test on 2017-05..2020-11 can only confirm an edge it has the sample to see. The number of trades
needed grows with the square of (per-trade noise / edge); overlapping or same-day trades add less information than
their count suggests; and testing up to 3 candidates raises the bar. The result is a gate for E.33's selection rule
(P8): a candidate whose expected test-window trade count cannot give about 80% power at the test bar should not use
one of the 3 test slots, however good its discovery numbers look.

### c.2 Equations
Notation: x_i net P&L of trade i (ticks), mean mu, SD sigma; n trades; rho_k the lag-k autocorrelation of the
trade series (in time order); c the one-sided critical value; z_{1-beta} the power quantile.

1. iid, one-sided test of H0: mu <= 0 (normal approximation; with n in the hundreds or more the t and normal
   critical values agree to 2 decimals):
   delta = mu sqrt(n) / sigma (noncentrality); power = 1 - Phi(c - delta);
   n_iid = ((c + z_{1-beta}) sigma / mu)^2; minimum detectable edge mu_min = (c + z_{1-beta}) sigma / sqrt(n).
   This is E.28 2.7 section 12's rule, made one-sided and with the stage's critical values.
2. Critical values. Up to 3 candidates tested once: Bonferroni (and Holm for the first rejection) uses
   alpha = 0.05/3 one-sided, c = z(0.98333) = 2.1280. The program bar t > 3.0 is one-sided alpha 0.00135 and is
   stricter, so when both apply c = 3.0 binds. z_{0.8} = 0.8416. delta at 80% power: 2.128 + 0.842 = 2.970 or
   3.0 + 0.842 = 3.842.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
3. Dependence (Lo 2002 eq. 19 gives the variance of a q-period sum; dividing by q^2 gives the mean):
   Var(xbar) = (sigma^2 / n) [1 + 2 sum_{k=1..n-1} (1 - k/n) rho_k] ~= (sigma^2 / n) D, D = 1 + 2 sum_k rho_k;
   n_eff = n / D; raw trades needed n = D n_iid. Lo's eq. 20 is the same factor applied to Sharpe ratios:
   SR(q) = eta(q) SR, eta(q) = q / sqrt(q + 2 sum_{k=1..q-1} (q - k) rho_k).
4. Overlapping holds. Entries every Delta minutes, each held h = m Delta minutes, price a random walk: consecutive
   trades share m - k of their m increments, so rho_k = 1 - k/m (k < m) and 0 beyond;
   D = 1 + 2 sum_{k=1..m-1} (1 - k/m) = 1 + (m - 1) = m. So n_eff = n/m: overlapping entries carry no more
   information than non-overlapping ones. (My derivation; simulated check below.)
5. Same-day clustering. k trades a day with a common within-day correlation rho_w (shared regime, news, liquidity):
   D_day = 1 + (k - 1) rho_w (variance of a sum of k equicorrelated terms divided by k sigma^2).
6. HAC estimator (Newey and West 1987, eq. (5) of the 1986 working paper):
   S_hat = Omega_0 + sum_{j=1..m} w(j, m) [Omega_j + Omega_j'], w(j, m) = 1 - j/(m + 1), Omega_j = sum_{t=j+1..T}
   h_t h_{t-j}' / T. For a mean, h_t = D_t - Dbar, and t_NW = Dbar / sqrt(S_hat / T). Run it on the DAILY series D_t
   (b.2), which absorbs all within-day overlap and clustering, so the lag m only has to cover day-to-day dependence.
   A common automatic lag is floor(4 (T/100)^{2/9}) = 6 for T = 816 and for T = 904 [rule attributed to Newey and
   West 1994; not read here].
7. Daily units: with k trades a day, E[D_t] = k mu and Var(D_t) = k sigma^2 D_day; the daily t over T days equals the
   trade-level t with n = kT and D = D_day, so both routes give the same power.
8. Gate for P8 (a formula, the thresholds are the lead's): a candidate with expected test trades a day k_test,
   haircut net edge mu_h (ticks), per-trade SD sigma_h and dependence factor D needs
   k_test x 904 >= D ((c + 0.8416) sigma_h / mu_h)^2, with c = 3.0 if the program bar applies.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]

### c.3 Worked examples (M5b_calc_out.txt c1-c3; sigma from section 0; random-walk scaling ASSUMED; non-overlapping
trades, D = 1)
Arithmetic of one cell by hand: h = 15, mu = 0.5, c = 3.0: (3.0 + 0.8416) x 12.200 / 0.5 = 3.8416 x 24.400 = 93.735;
93.735^2 = 8,786 trades; over 904 test dates 8,786/904 = 9.72 a day; over 816 discovery dates 10.77 a day.
Check: delta = 0.5 sqrt(8,786)/12.2 = 0.5 x 93.73/12.2 = 3.842 = 3.0 + 0.842.

Trades needed for 80% power (n), and per trade date over the test (904) and discovery (816) windows. Last two
columns: the most non-overlapping holds a single position can make per date, all sessions (1,055/h) and day session
only (290/h).

| h (min) | sigma_h | mu net | n, alpha 0.05/3 | /test day | /disc day | n, t > 3.0 | /test day | /disc day | cap all | cap day |
|---|---|---|---|---|---|---|---|---|---|---|
| 5 | 7.044 | 0.25 | 7,000 | 7.74 | 8.58 | 11,715 | 12.96 | 14.36 | 211.0 | 58.0 |
| 5 | 7.044 | 0.50 | 1,750 | 1.94 | 2.14 | 2,929 | 3.24 | 3.59 | 211.0 | 58.0 |
| 5 | 7.044 | 1.00 | 438 | 0.48 | 0.54 | 732 | 0.81 | 0.90 | 211.0 | 58.0 |
| 15 | 12.200 | 0.25 | 21,001 | 23.23 | 25.74 | 35,145 | 38.88 | 43.07 | 70.3 | 19.3 |
| 15 | 12.200 | 0.50 | 5,250 | 5.81 | 6.43 | 8,786 | 9.72 | 10.77 | 70.3 | 19.3 |
| 15 | 12.200 | 1.00 | 1,313 | 1.45 | 1.61 | 2,197 | 2.43 | 2.69 | 70.3 | 19.3 |
| 60 | 24.400 | 0.25 | 84,005 | 92.93 | 102.95 | 140,579 | 155.51 | 172.28 | 17.6 | 4.8 |
| 60 | 24.400 | 0.50 | 21,001 | 23.23 | 25.74 | 35,145 | 38.88 | 43.07 | 17.6 | 4.8 |
| 60 | 24.400 | 1.00 | 5,250 | 5.81 | 6.43 | 8,786 | 9.72 | 10.77 | 17.6 | 4.8 |

Minimum detectable net edge at 80% power over the 904 test dates, by trades a day (non-overlapping, D = 1):

| h | bar | 1/day | 2/day | 5/day | 10/day | 20/day |
|---|---|---|---|---|---|---|
| 5 | 0.05/3 | 0.696 | 0.492 | 0.311 | 0.220 | 0.156 |
| 15 | 0.05/3 | 1.205 | 0.852 | 0.539 | 0.381 | 0.269 |
| 60 | 0.05/3 | 2.410 | 1.704 | 1.078 | 0.762 | 0.539 |
| 5 | t > 3.0 | 0.900 | 0.636 | 0.402 | 0.285 | 0.201 |
| 15 | t > 3.0 | 1.559 | 1.102 | 0.697 | 0.493 | 0.349 |
| 60 | t > 3.0 | 3.118 | 2.204 | 1.394 | 0.986 | 0.697 |

Readings:
- Because sigma_h grows as sqrt(h), n scales with h at fixed mu: 60-minute trades need 4 times the trades of
  15-minute ones (5,250 vs 1,313 at mu = 1, alpha 0.05/3) and 12 times those of 5-minute ones.
- At 60 minutes, mu = 0.5 is not testable: it needs 23.2 (alpha 0.05/3) or 38.9 (t > 3) non-overlapping trades a
  date against a ceiling of 17.6 (all sessions) or 4.8 (day session). Only mu >= 1 tick is testable at 60 minutes,
  and at t > 3 even that needs 9.7 a date, i.e. trading most overnight hours. mu = 0.25 is testable only at 5
  minutes (7.7 to 13.0 a date).
- At 15 minutes: mu = 0.5 needs 5.8 to 9.7 trades a date (feasible in the day session, cap 19.3); mu = 1 needs
  1.5 to 2.4.
- Overlap check (c2-c3): m = 3 (15-minute holds entered every 5 minutes): theory D = 3; simulation (2,000 paths of
  600 five-minute steps) gives 3.04. So entering a 15-minute trade every 5 minutes triples the count but not the
  information.
- Same-day clustering: 10 trades a day with rho_w = 0.05 gives D = 1 + 9 x 0.05 = 1.45, i.e. 45% more trades for the
  same power; with rho_w = 0.1, 1.90. rho_w is unknown until discovery; E.33 should estimate it on discovery D_t
  (ratio of the daily-sum variance to k sigma^2) and carry it into the gate.
- HAC shortfall (c4): Bartlett weights shrink the long-run variance in finite lags. Daily AR(1) phi = 0.2: true
  ratio (1 + 0.2)/(1 - 0.2) = 1.5; Newey-West with 5 lags gives 1 + 2 sum_{j=1..5} (1 - j/6) 0.2^j = 1.3958, so
  the NW t is too large by sqrt(1.5/1.3958) = 1.037. Small, but in the anti-conservative direction; the day-block
  bootstrap is the cross-check.
- Winner's curse: the candidate's discovery edge is the maximum over many configurations and is biased upward; E.28
  2.11 records Harvey and Liu's worked example in which multiple testing cuts a Sharpe ratio by 52.0% (E.28 2.11,
  line 11626). Plan the gate with a haircut mu_h (for example half the discovery net edge) rather than the point
  estimate. The haircut value is the lead's decision.

### c.4 Planner pointer: "about 40 major events in the discovery window": power of an event-family test
Setup: one trade per event, entered 5-15 minutes after an 11:00 CT USDA release and held to 90 minutes after it, so
at most 75 minutes; sigma_75 = 3.15 x sqrt(75) = 3.15 x 8.660 = 27.28 ticks under the random walk; event days are
noisier, so k_ev in {1.0, 1.5, 2.0} scales sigma. Event counts: 40 (planner), 49 (R4_events.md line 235: 15 major
USDA days a year x 39/12), 24 (R4's median split into "big" events), 54 (the test window: 15 x 43/12 = 53.75).

Minimum detectable net edge at 80% power (ticks) and power at a net edge of 2 ticks (M5b_calc_out.txt c5):

| n events | k_ev | sigma | MDE, one-sided 0.05 | MDE, 0.05/3 | MDE, t > 3 | power at 2 ticks (0.05 / 0.05/3 / t > 3) |
|---|---|---|---|---|---|---|
| 24 | 1.0 | 27.28 | 13.85 | 16.54 | 21.39 | 0.099 / 0.038 / 0.004 |
| 40 | 1.0 | 27.28 | 10.72 | 12.81 | 16.57 | 0.119 / 0.048 / 0.006 |
| 40 | 1.5 | 40.92 | 16.09 | 19.21 | 24.86 | 0.091 / 0.034 / 0.004 |
| 40 | 2.0 | 54.56 | 21.45 | 25.62 | 33.14 | 0.079 / 0.029 / 0.003 |
| 49 | 1.0 | 27.28 | 9.69 | 11.57 | 14.97 | 0.129 / 0.053 / 0.006 |
| 54 | 1.0 | 27.28 | 9.23 | 11.02 | 14.26 | 0.134 / 0.056 / 0.007 |

By hand, n = 40, k_ev = 1, one-sided 0.05: (1.6449 + 0.8416) x 27.28 / sqrt(40) = 2.4865 x 27.28 / 6.3246 =
67.83 / 6.3246 = 10.72 ticks. Power at 2 ticks: 1 - Phi(1.6449 - 2 x 6.3246/27.28) = 1 - Phi(1.6449 - 0.4637) =
1 - Phi(1.1812) = 0.119. (With n = 40 the t critical value with 39 df is 1.685 rather than 1.645, so these normal
numbers are slightly optimistic.)

Reading: with about 40 events, an event-direction family can only detect net edges of 10 to 33 ticks per event,
i.e. 1/3 to more than 1 full 75-minute SD. A plausible edge of 1-2 ticks has 5-12% power at a lenient 5% level and
under 1% at t > 3. More trades per event do not help (c.2 item 4: overlapping holds inside one event window share
the same path, D ~ m). The family is untestable as a stand-alone one-shot candidate; it can enter only as a
conditioning flag on a high-frequency family, or be dropped. This is a power statement, not a statement that the
effect is absent.

### c.5 Data it needs
Discovery-window estimates of sigma_h (per-trade net P&L SD, not the random-walk proxy), the candidate's trade rate
by session, the lag autocorrelations of the trade series and of D_t, rho_w, and the frozen trade-date calendars of
both windows (DataFacts). The sealed window supplies nothing until the test.

### c.6 Leakage and look-ahead traps, each with a test
1. Raw counts of overlapping trades used as n (overstates power and the t). Test: compute D on discovery as
   Var(sum over a day)/ (k sigma^2) and from the lag autocorrelations; the gate uses n / D.
2. Power planned on the discovery point estimate (winner's curse). Test: simulate the selection (the max of N
   null-plus-signal configurations) and compare the selected configuration's discovery edge with its true edge;
   the gap is the haircut.
3. sigma or trade rate measured on the test window to "check feasibility" before the test: that is a peek at sealed
   data. Test: the gate's inputs are written into the protocol, hashed, before the seal is opened.
4. A regime with lower volatility in the test window raises power, a higher one lowers it; the gate uses discovery
   sigma and should state the test window's volatility as unknown.
5. Event families: counting events after seeing which releases moved the market (for example dropping "quiet"
   reports) inflates the edge. Test: the event list is the frozen USDA calendar (R4), all events kept.

### c.7 Compute
Closed-form; the Monte Carlo checks ran in seconds.

### c.8 Verdict
USE as a P8 gate: a candidate takes a test slot only if D-adjusted, haircut power at the binding bar (t > 3.0, which
is stricter than 0.05/3) is at least the lead's threshold over 904 test dates. On the standard numbers this rules out
60-minute holds below 1 tick net, any 15-minute rule trading under about 2.4 non-overlapping trades a date at
mu = 1 (9.7 at mu = 0.5), and a stand-alone USDA event family.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]

### c.9 Evidence
| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Variance of a q-period sum with autocorrelation | Lo 2002, FAJ 58(4), eq. 19 (academic) | "= qσ 2 + 2σ 2 ∑ ( q – k )ρk , where ρk ≡ Cov(Rt , Rt–k)/Var(Rt) is the kth-order autocorrelation of Rt." (pdftotext layout) | lo_2002_faj_statistics_sharpe.pdf/.txt, lines 305-311 |
| Time-aggregation factor eta(q) | Lo 2002 eq. 20 | "SR ( q ) = η ( q ) SR, η ( q ) ≡ ... q + 2 ∑ q –1 ( q – k )ρk" and "Note that Equation 20 reduces to Equation 17 if all autocorrelations ρk are zero" | same, lines 313-320 |
| Bartlett-weighted HAC estimator | Newey and West, NBER Technical Working Paper 55 (April 1986; published Econometrica 55, 1987), eq. (5) (academic) | "S_T = Ω_0 + Σ_{j=1}^m w(j,m)[Ω_j + Ω_j'], w(j,m) = 1 - [j/(m+1)]." and "This estimator is numerically equal to 2π times an estimator of the spectral density of h_t(θ*) at frequency zero, where the modified Bartlett weights are used" (scanned page 3 read as an image; hats and tildes typed) | newey_west_1986_nber_t0055.pdf (scanned, no text layer) |
| Program power rule (two-sided form) | E.28 2.7 section 12 (program) | "n = ((1.96 + 0.8416) sigma / delta)^2 *effective* observations" | reports/stage_e28_methods_brief.md line 8054 |
| Event count about 49 in discovery | R4_events.md (E.32 sibling) | "Over the 39-month discovery window: 15 x 39 / 12 = 48.75, about 49" | reports/stage_e32_briefs/R4_events.md line 235 |
| Harvey-Liu haircut example 52.0% | E.28 2.11 (program, sources there) | "autocorrelation-corrected SR is 0.912 and the BHY-adjusted SR is 0.438, a 52.0% haircut (E16)" | reports/stage_e28_methods_brief.md line 11626 |
| Newey-West 1994 automatic lag rule floor(4(T/100)^{2/9}) | Newey and West 1994 | not read | [unverified] |

## (d) The Sharpe-ratio standard error with non-normal returns, and the minimum track record length

### d.1 Core idea
The Sharpe ratio is an estimate with a standard error. Lo (2002) gives it under iid returns and under serial
dependence; Mertens (2002) adds skewness and kurtosis for iid non-normal returns, and Opdyke (2007) showed the same
expression holds for stationary and ergodic returns. Bailey and López de Prado (2012) turn it into the probabilistic
Sharpe ratio (PSR) and the minimum track record length (MinTRL): the number of observations needed before an
observed SR is significantly above a benchmark. For this program the per-trade SR is tiny (0.04-0.08), so higher
moments barely move the SE; dependence does. MinTRL is a 50%-power sample size, not an 80% one.

### d.2 Equations
Notation: SR = mu/sigma per observation (per trade here), SR_hat its estimate from T observations, gamma_3 the
skewness, gamma_4 the kurtosis (3 for the normal; not excess), SR* a benchmark, Z the standard normal CDF.
1. iid normal (Lo 2002 eqs. 8-9): sqrt(T) (SR_hat - SR) ~a N(0, V_IID), V_IID = 1 + SR^2 / 2;
   SE(SR_hat) ~= sqrt((1 + SR^2/2) / T).
2. Dependent returns (Lo 2002 eqs. 14-15): V_GMM from a GMM/HAC estimate of the joint variance of (mu_hat,
   sigma_hat^2) and the delta method; SE(SR_hat) = sqrt(V_GMM_hat / T). For a mean-dominated SR (SR small), V_GMM ~=
   D, the long-run variance ratio of c.2, so SE ~= sqrt(D / T): the same factor as in the power calculation.
3. iid non-normal (Mertens 2002, as given by Bailey and López de Prado 2012 eq. 8; valid for stationary ergodic
   returns per Opdyke 2007):
   SR_hat ~a N( SR, (1 + SR^2/2 - gamma_3 SR + ((gamma_4 - 3)/4) SR^2) / T ).
   Equivalently V = 1 - gamma_3 SR + ((gamma_4 - 1)/4) SR^2, since (gamma_4 - 1)/4 = (gamma_4 - 3)/4 + 1/2; this
   second form is the one in BLdP's code.
4. PSR (BLdP 2012 eq. 11; their code `set_PSR`):
   PSR(SR*) = Z[ (SR_hat - SR*) sqrt(T - 1) / sqrt(1 - gamma_3 SR_hat + ((gamma_4 - 1)/4) SR_hat^2) ].
5. MinTRL (BLdP 2012 eq. 13; their code `set_TRL`), in observations, at confidence 1 - alpha:
   MinTRL = 1 + [1 - gamma_3 SR_hat + ((gamma_4 - 1)/4) SR_hat^2] (Z^{-1}(1 - alpha) / (SR_hat - SR*))^2.
6. Link to power: with SR* = 0 and moments normal, MinTRL ~= (c / SR)^2 = the n at which the expected t equals the
   critical value c, i.e. 50% power. The 80%-power sample is ((c + 0.8416)/SR)^2, larger by ((c + 0.8416)/c)^2:
   1.639 at c = 3.0, 1.776 at c = 2.128.
[MathReview C-8 (lead: accepted): the second number is wrong: ((2.1280 + 0.8416)/2.1280)^2 = (1.3955)^2 = 1.947, matching this file's own worked example 1,313/677 = 1.94 (d.3 item 2); 1.639 at c = 3.0 is right, and the verdict line "1.64 times MinTRL at t > 3" is unaffected.]
7. The DSR (M5a (d)) is the PSR with SR* set to the expected maximum SR of N null trials; it is not repeated here.

### d.3 Worked examples (M5b_calc_out.txt d1-d2)
1. SE at h = 15, mu = 1 tick net: SR = 1/12.200 = 0.08197 a trade; SR^2 = 0.006719. T = 5,000 trades:
   naive 1/sqrt(5,000) = 0.014142; Lo iid sqrt(1.003359/5,000) = 0.014166 (+0.17%); Mertens with gamma_3 = -0.5,
   gamma_4 = 8: V = 1.003359 + 0.5 x 0.08197 + (5/4) x 0.006719 = 1.003359 + 0.040984 + 0.008399 = 1.052742;
   sqrt(1.052742/5,000) = 0.014510 (+2.6%); gamma_3 = -1, gamma_4 = 20: 0.014926 (+5.5%). Check: the ratio
   0.014510/0.014142 = 1.026 = sqrt(1.052742). Compare dependence: D = 1.45 (10 trades a day, rho_w = 0.05, c.3)
   inflates the SE by sqrt(1.45) = 1.204, i.e. +20%. **Non-normality is second order at these per-trade SRs;
   dependence is first order.**
2. MinTRL vs 80%-power n, SR* = 0 (normal moments; gamma_3 = -0.5, gamma_4 = 8 in brackets):
   - h = 15, mu = 1 (SR 0.08197), c = 3.0: MinTRL = 1 + 1.003359 x (3/0.08197)^2 = 1 + 1.003359 x 1,339.4 =
     1,345 (1,411); 80%-power n = 2,197. With c = 2.128: 677 (711) vs 1,313.
   - h = 5, mu = 0.5 (SR 0.07099), c = 3.0: 1,792 (1,866) vs 2,929.
   - h = 60, mu = 1, or h = 15, mu = 0.5 (both SR 0.04098), c = 3.0: 5,364 (5,485) vs 8,786.
   Check: 2,197 / 1,345 = 1.633, against the theoretical 1.639 (the small gap is the "1 +" and the SR^2 term).
3. In calendar terms: one 15-minute trade a date at mu = 1 is an annualised SR of 0.08197 x sqrt(251) = 1.30. Its
   MinTRL at t > 3 is 1,345 trades = 5.4 years at one a date, longer than the 3.6-year test window (904/251). Its
   power over 904 test dates: delta = 0.08197 x sqrt(904) = 0.08197 x 30.07 = 2.465; power = 1 - Phi(3 - 2.465) =
   1 - Phi(0.535) = 1 - 0.704 = 0.30. An annualised SR of 1.3 is not enough at one trade a day.

### d.4 Data it needs
The candidate's net per-trade (or daily) P&L series from discovery out-of-sample folds: mean, SD, gamma_3, gamma_4,
autocorrelations. Moments above the second need long series (BLdP 2012 note that the fourth moment needs much longer
samples), so estimate gamma_3 and gamma_4 on all discovery trades, not per fold.

### d.5 Leakage and look-ahead traps, each with a test
1. Annualising by sqrt(q) with autocorrelated daily P&L (Lo: up to 65% overstatement in his hedge-fund example).
   Test: report eta(q) from Lo eq. 20 with the estimated autocorrelations next to sqrt(q).
2. PSR or MinTRL with SR* = 0 after a search over N configurations: it ignores selection. Test: the program's bar is
   DSR at N (M5a), which uses SR* = the expected maximum of N null SRs.
3. Moments from too few trades: gamma_4 from a few hundred trades is unstable. Test: bootstrap (by day) the
   gamma_4 estimate and show its interval; if it is wide, report the normal-moment version beside it.
4. Mixing units: SR per trade with T in days, or daily SR with trade counts. Test: one unit per calculation, stated
   (M5a (d) checks the per-trade versus daily-with-zeros equivalence).

### d.6 Compute
Closed form.

### d.7 Verdict
USE the Lo/Mertens SE (with V_GMM or HAC for dependence) for confidence bands and the PSR as a reported statistic;
the program bar remains the DSR at N (M5a). Use MinTRL only with the warning that it is a 50%-power length; the P8
gate should use the 80%-power n of c.2, which is 1.64 times MinTRL at t > 3.

### d.8 Evidence
| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| iid asymptotic variance V_IID = 1 + SR^2/2 | Lo 2002, FAJ 58(4) (academic) | "Note: Returns are assumed to be IID, which implies VIID = 1 + 1/2SR ." (pdftotext drops the superscript 2) | lo_2002_faj_statistics_sharpe.pdf/.txt line 223 |
| Non-iid SE from GMM | Lo 2002 eqs. 14-15 | "for non-IID returns, the standard error of the Sharpe ratio can be estimated by SE[SR] = V̂ GMM /T (15)" (square root lost in extraction) | same, lines 276-281 |
| Serial correlation can overstate annual SR by 65% | Lo 2002 abstract | "the annual Sharpe ratio for a hedge fund can be overstated by as much as 65 percent because of the presence of serial correlation in monthly returns" | same, lines 14-16 |
| Mertens: SR normal even if returns are not; skewness and kurtosis widen the band | Bailey and López de Prado 2012, J. Risk 15(2), "The Sharpe ratio efficient frontier", section 2.4 (academic) | "Mertens (2002) concludes that the Normality assumption on returns could be dropped, and still the estimated Sharpe ratio would follow a Normal distribution"; "although skewness and kurtosis does not affect the point estimate of SR, it greatly impacts its confidence bands" | bailey_ldp_2012_sharpe_frontier.pdf/.txt lines 308-318 |
| Opdyke: Mertens = Christie; valid for stationary ergodic returns | same, sections 2.1 and 2.4 | "Opdyke (2007) has shown that Mertens' equation has a limiting distribution that is valid under the more general assumption of stationary and ergodic returns, and not only IID." | same, lines 132-134 |
| PSR and MinTRL formulas | same, appendix code (eqs. 11 and 13 garbled by extraction) | "self.PSR=norm.cdf((sr-self.sr_ref)*(self.obs-1)**0.5/ (1-sr*stats[2]+sr**2*(stats[3]-1)/4.)**0.5)" and "self.minTRL=1+(1-stats[2]*sr+(stats[3]-1)/4.*sr**2)* (norm.ppf(self.prob)/(sr-self.sr_ref))**2" | same, lines 894-902 |
| MinTRL is in observations; moments need long series | same, section 4 | "It is important to note that MinTRL is expressed in terms of number of observations, not annual or calendar terms."; "the moments inputted in Eq. (13) must be computed on longer series for CLT to hold" | same, lines 486-491 |
| Fourth moment needs longer samples | same, section 2.3 | "estimating moments beyond the third, and particularly the fourth moment, requires longer sample lengths than estimating only the first two moments" | same, lines 303-305 |
| Opdyke's formula valid for stationary ergodic returns | Opdyke 2007, J. Asset Management 8(5) (academic), abstract only | "This paper presents an easily implemented formula for the asymptotic distribution that is valid under very general conditions — stationary and ergodic returns — thus permitting time-varying conditional volatilities, serial correlation, and other non-iid returns behaviour." | opdyke_2007_repec_abstract.html [abstract only; full text not obtained: SSRN blocked, journal paywalled] |
| Lo, Mertens, Christie; Opdyke showed equivalence | Benhamou 2018, arXiv 1808.04233 (academic) | "Opdyke (2007) interestingly showed that the derivation provided by Christie (2005) under the non-IID returns condition was in fact identical to the one provided by Mertens (2002)." | benhamou_arxiv_1808_04233.pdf/.txt lines 466-469 |
| PSR uses sample length and four moments | Bailey and López de Prado 2014, JPM, DSR paper (academic) | "PSR takes into account the sample length and the first four moments of the returns' distribution." | bailey_ldp_2014_dsr.pdf/.txt lines 352-353 |
| Mertens 2002 working paper itself | Mertens, "Comments on variance of the IID estimator in Lo (2002)" | not read | [unverified: unpublished note, not found online; formula taken from BLdP 2012 eq. 8 and code] |

Stopping rule (d): 5 full-text sources read (Lo, BLdP 2012, BLdP 2014, Benhamou, plus the Opdyke abstract); two
searches for Opdyke's full text and none for Mertens found anything new.

## Planner pointers owned by M5b

| Pointer (reports/stage_e32_inputs/planner_research_soy_complex.md) | Status | Evidence and what differs |
|---|---|---|
| "block bootstrap by day, and positive results in at least two-thirds of quarters" (line 121-122) | PARTLY VERIFIED | A protocol suggestion, not an empirical claim. The day-block stationary bootstrap is sound (Politis and Romano 1994; block length by Politis-White with the 2009 correction; quotes in b.8). The two-thirds-of-quarters rule is a weak null filter (passes a no-edge candidate with probability 0.133 over 13 discovery quarters, 0.090 over 14 test quarters) and costs about 1 point of power at delta = 3.84 (b.3 item 2). It is a stability requirement, not significance. Applied to MONTHS instead of quarters it costs about 7 points of power. Under negative skew the binomial null is wrong (b.3 item 6). |
| "There are only about 40 major events in the discovery window" (line 92) | PARTLY VERIFIED (count); power COMPUTED | R4_events.md line 235 counts 15 major 11:00 CT USDA days a year, so about 49 in 39 months ("the planner's 'about 40' is the same order"); from a typed calendar, not a data read. Power: with 40 events, one trade each and a 75-minute hold, the minimum detectable net edge at 80% power is 10.7 ticks (one-sided 0.05, event-day noise as on normal days) up to 33.1 ticks (t > 3, noise doubled); a 2-tick edge has 3-12% power at the lenient bars and under 1% at t > 3 (c.4). A stand-alone event family cannot pass the one-shot test. |

## What this means for E.33 (inputs for the lead's P8; the thresholds are the lead's)
1. Power gate: a candidate takes one of the 3 test slots only if D x ((3.0 + 0.8416) sigma_h / mu_h)^2 <= expected
   test trades (904 dates x trades a date), with mu_h a haircut discovery net edge and D from discovery
   autocorrelations and same-day clustering. On the standard numbers: 5-minute holds can test mu = 0.25-0.5 at
   3-13 trades a date; 15-minute holds need 2.4 (mu = 1) or 9.7 (mu = 0.5) a date; 60-minute holds can test only
   mu >= 1 and need about 9.7 a date across sessions; the USDA event family is untestable alone.
[MathReview C-6/C-9 (lead: ruled): the frozen test bar is the program verdict plus a protocol-added DSR >= 0.95 at N with V = 1/(T_test - 1) (t about 4.86 at N 838, T 870); see reports/stage_e32_discovery_protocol.md P7.2 and P9.]
2. Stability requirements with their measured cost at delta = 3.84 (80% power at t > 3): two-thirds of 3-month blocks
   positive (about 1 point of power); no month above 25% of net P&L (about 0 points; removes 78-100% of one-spike
   false passes); every leave-one-month-out t above 2.5 (about 0.1 point); same sign in each frozen volatility
   tercile (about 4 points). Significance inside every tercile would cost 63 points: do not require it.
3. Inference: HAC t on the daily P&L series (Newey-West, Bartlett weights, lag by a frozen rule) plus a day-block
   stationary-bootstrap p-value (b_SB from arch's automatic rule on discovery; about 2-5 days for daily AR(1)
   coefficients 0.05-0.2).
4. Feature importance: clustered MDA and SFI on purged folds, with noise canaries, reported after the frozen grid
   runs; no importance-driven selection unless nested and counted into N.
5. MinTRL is a 50%-power length; the gate should use the 80%-power n (1.64 times MinTRL at t > 3).

## Failures, gaps and negative evidence
- Full text NOT obtained (marked [unverified] where used): Politis and Romano 1994 JASA (JSTOR only; the UCY record
  page returned a Cloudflare 403); López de Prado 2020 MLAM section 6.5 (clustered importance) and AFML ch. 8 (no
  free copy; the SCU library catalogue returned an anti-bot stub); Opdyke 2007 (SSRN blocked, journal paywalled; abstract
  from RePEc only); Mertens 2002 (unpublished note, not found); Newey and West 1994 lag rule (not searched). The
  BMC copy of Strobl et al. 2007 returned a cookie redirect twice; the PMC copy was used instead.
- Two sources are scanned PDFs without a text layer (Newey-West NBER TWP 55; Politis-Romano Statistica Sinica
  1994). I read the relevant pages as images; their quotes were typed from the page images and need a visual check
  by the reviewer (pages named in the evidence rows).
- Lo 2002 was fetched from a copy on a UC Berkeley student-organisation host (traders.studentorg.berkeley.edu);
  authorisation of that copy is unknown; the text matches the FAJ article's first page.
- Test-window trade dates: my typed calendar gives 904; M5a's gives 899. Neither is read from data; DataFacts owns the
  real number. Every per-day rate in (c) moves by 0.6% between the two.
- All sigma values are random-walk scalings of a 2022-23 one-minute SD (an assumption); real minute returns in ZM may
  mean-revert or trend at 5-60 minutes, and 2017-2020 volatility is unknown without opening the seal. The Monte Carlo
  stability results assume equal trades per month and iid months.
- SFI and LOCO compute times in a.7 are guesses; no probe was run (no data may be read in E.32).
- WebSearch calls used: 13 of 80. No budget notice was received.

Finished 2026-10-27 (time in log). Reviewer notes: every number above is reproducible from
work/M5b_power/M5b_calc.py, M5b_calc2.py, M5b_calc3.py and M5b_days.py.
