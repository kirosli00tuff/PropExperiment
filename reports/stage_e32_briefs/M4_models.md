# E.32 Part M4: model families for a minutes-scale directional ZM search

Worker: ModelsMath-OpusHigh (Opus 5.5, effort high). Started 2026-10-27 00:30 PDT. ROOT M4_models.
Pages and log: `reports/stage_e32_briefs/pages/M4_models/` (log.tsv). Scripts and their outputs:
`reports/stage_e32_briefs/work/M4_models/` (`M4_ess.py/.out`, `M4_examples.py/.out`,
`M4_compute_probe.py/.out`).

Nothing here was computed from market data. The sample-size counts are calendar arithmetic. The compute
numbers come from a timing probe on synthetic random data (seed 20261027) run on this ThinkPad at nice 10
with 8 threads, 00:40:20-00:44:24 PDT. The probe trained nothing on ZM, ZS or ZL. No feature, label or return
was computed.

## 0. Scope, what was read, and the yardsticks used in every section

**E.28 sections read (by line range) and cited, not repeated:**
- E.28 2.8 (deep LOB models): DeepLOB equations, LOBCAST, Briola et al., Lucchese et al., futures results,
  measured GPU throughput (2.8 section 10.1) and verdicts (2.8 section 12).
- E.28 2.9 (OFI and trees): XGBoost/LightGBM objective, eqs. 2, 4, 5 and 6, the leaf-weight worked example
  (2.9 section 6.3), Aït-Sahalia et al. "trees about equal to LASSO" (2.9 section 6.6), latency decay
  (2.9 section 9).
- E.28 2.5 (Kalman, HMM): the Kalman recursion (Welch-Bishop eqs. 1.9-1.13), the Hamilton filter
  (eqs. 5-12), Baum-Welch, the Viterbi look-ahead trap, measured filter costs (2.5 sections 1.7 and 4.7), and
  the verdict "HMM as a return forecaster (directional): skip" (2.5 section 9).
- E.28 C4.4 (hardware): "a DeepLOB-sized network has about 60k parameters and takes 8 to 34 hours per
  configuration on the RTX 3050".

**E.28's data-size verdict for deep LOB models (E.28 2.8 section 1.3), quoted because the brief asks for it:**
"So 4 months is enough to fit the model (it has only 60k parameters and millions of event samples), but not
enough to show the result is stable across regimes: the test window would be one or two months of one
contract. 12 months allows a 6/3/3 split like the paper's. The binding constraint is independence, not sample
count: successive samples share 99 of 100 input rows and overlapping label windows, so the effective sample
size is closer to the number of non-overlapping horizons than to the number of events." That verdict was
written for event-horizon labels (10 to 100 book events). For minutes-scale labels, section (e) shows the
independent-sample count is smaller again, by orders of magnitude.

**Standard ZM yardsticks (from READER_BRIEF; arithmetic in `M4_examples.out`).** Tick 0.10 USD/short ton,
10.00 USD. sigma_1m = 3.15 ticks. Under a random-walk ASSUMPTION, sigma_h = 3.15 x sqrt(h):
5 min 3.15 x 2.2361 = 7.044 ticks; 15 min 3.15 x 3.8730 = 12.200; 30 min 3.15 x 5.4772 = 17.253;
60 min 3.15 x 7.7460 = 24.400. Market-order hurdle at Topstep: E.28 ranking row 6
(`reports/stage_e28_ranking.md` line 130, "| 6 | topstep | ZM | ... | 0.59 | 1.59 | ..."), column
mu*_mkt = **1.59 ticks** per round trip (the brief's "about 1.6").

**The probability a direction call needs (used in (a) and (c)).** ASSUMPTIONS: the h-minute return r is
normal with mean 0 and standard deviation sigma_h; the model's sign call is independent of |r|; one 1-lot
market round trip costs C = 1.59 ticks. Then E|r| = sigma_h sqrt(2/pi), and a call that is right with
probability p earns (2p - 1) E|r| - C ticks gross of slippage beyond C. Break-even: p* = 1/2 + C / (2 E|r|).
[MathReview D-1 (lead: accepted): 1.59 is not the cost of a round trip but E.28's cycle-EV threshold mu*_mkt at T = 20/day (= 1.528 + 0.062, the 0.062 being the per-trade drift that pays the evaluation and API fees over a cycle at 20 trades a day); the per-round-trip cost is c = 1.528 ticks (c_mkt = F_rt/v + S_rt = 0.528 + 1.00, A3_econ 2.1), as M6 uses, so under this model p*(15 min) = 0.5 + 1.528/(2 x 9.734) = 0.5785, not 0.5817 (also applies to the table below and original line 117).]

| h (min) | sigma_h (ticks) | E\|r\| = 0.79788 sigma_h | p* = 0.5 + 1.59 / (2 E\|r\|) | edge at p = 0.55: 0.10 E\|r\| |
|---|---|---|---|---|
| 1 | 3.150 | 2.513 | 0.8163 | 0.251 |
| 5 | 7.044 | 5.620 | 0.6415 | 0.562 |
| 15 | 12.200 | 9.734 | 0.5817 | 0.973 |
| 30 | 17.253 | 13.766 | 0.5578 | 1.377 |
| 60 | 24.400 | 19.468 | 0.5408 | 1.947 |

Check (h = 15): 1.59 / (2 x 9.734) = 1.59 / 19.468 = 0.0817, so p* = 0.5817. A sanity bound: p* falls like
1/sqrt(h), so going from 15 to 60 minutes (4x) halves the excess: 0.0817 / 2 = 0.0408, and the table has
0.5408. The table shows why the stage's labels sit at 15 to 240 minutes. Below about 5 minutes, no realistic
hit rate pays a market round trip.
[MathReview D-2 (lead: accepted): M6 (A2) and R5 (B2) use a Gaussian model under which the edge for a hit rate p is f = sigma Phi^{-1}(p) = sqrt(2 pi) sigma (p - 1/2) + O((p-1/2)^3) = 2.5066 sigma (p - 1/2), whereas this model gives (2p - 1) sigma sqrt(2/pi) = 1.5958 sigma (p - 1/2), a ratio of exactly pi/2 = 1.571, so the same 15-minute Topstep hurdle is p* = 0.5817 here but 0.5498 in M6 (A2) and 0.552 in R5. State both models in section 0 with the pi/2 factor, say which one E.33 will use, and (better) freeze the trade rule in ticks of the calibrated map p -> E[G | p] measured on held-out folds, as M6 (A2) already requires, so no hit-rate threshold enters the protocol (table for both conventions in d_m4.out, section 0; also applies to a.3 item 3, original lines 115-118).]

## (a) Regularised linear and logistic models (L1, L2, elastic net) and probability calibration

### a.1 Core idea
A linear score w'x, or a logistic probability sigma(w'x), is fitted with a penalty that shrinks the weights
toward zero. L2 (ridge) shrinks correlated features together, L1 (lasso) sets some exactly to zero, and the
elastic net mixes the two. With a weak, noisy target and a few thousand independent labels (section (e)),
shrinkage is what keeps the out-of-sample forecast from being mostly noise. A directional rule then trades
only when the predicted probability clears the cost hurdle p* (section 0). That requires the probability to be
calibrated, meaning that among cases forecast at 0.58, about 58% go up. That is the second half of this topic.

### a.2 Equations
Elastic net, linear (Friedman, Hastie and Tibshirani 2010, JSS 33(1), eqs. 1-3; `friedman2010_glmnet_pmc.txt`):

    min_{beta0, beta}  (1/(2N)) sum_{i=1..N} (y_i - beta0 - x_i' beta)^2 + lambda P_alpha(beta)          (1)
    P_alpha(beta) = (1 - alpha) (1/2) ||beta||_2^2 + alpha ||beta||_1
                  = sum_{j=1..p} [ (1/2)(1 - alpha) beta_j^2 + alpha |beta_j| ]                         (2), (3)

- N: number of training rows. x_i: p-vector of features, standardised to mean 0 and mean square 1 (the paper
  assumes "sum_i x_ij = 0, (1/N) sum_i x_ij^2 = 1"). y_i: the label. beta0: intercept. lambda >= 0: overall
  penalty strength. alpha in [0, 1]: the mix, where alpha = 0 is ridge and alpha = 1 is lasso.
- Coordinate update (described in words in the paper: "we compute the simple least-squares coefficient on the
  partial residual, apply soft-thresholding to take care of the lasso contribution to the penalty, and then
  apply a proportional shrinkage for the ridge penalty"; written out here by me, with no equation number):
  beta_j <- S(z_j, lambda alpha) / (1 + lambda (1 - alpha)), where z_j = (1/N) sum_i x_ij r_ij is the
  least-squares coefficient on the partial residual r_ij = y_i - beta0 - sum_{k != j} x_ik beta_k, and
  S(z, g) = sign(z) max(|z| - g, 0) is soft-thresholding.

Penalised logistic (same paper, eqs. 11, 13, 14): Pr(G = 1 | x) = 1 / (1 + exp(-(beta0 + x' beta))), and

    max_{beta0, beta} [ (1/N) sum_i { y_i (beta0 + x_i' beta) - log(1 + exp(beta0 + x_i' beta)) } - lambda P_alpha(beta) ]   (13)-(14)

with y_i = 1 for "up" and 0 otherwise. It is solved by iteratively reweighted least squares around the current
fit (their eqs. 15-16: weights w_i = p_i(1 - p_i), working response z_i = beta0 + x_i'beta + (y_i - p_i)/w_i).
The paper warns about the unpenalised limit: "the saturated logistic regression fit is undefined (parameters
wander off to ±∞ in order to achieve probabilities of 0 or 1)".

Calibration. Platt scaling (Niculescu-Mizil and Caruana 2005, eqs. 1-3;
`niculescu_caruana2005_calibration.pdf`): P(y = 1 | f) = 1 / (1 + exp(A f + B)), with A and B fitted by
maximum likelihood on a separate calibration set (f is the model's raw score). Isotonic regression (their
eq. 6): m_hat = argmin_z sum_i (y_i - z(f_i))^2 over non-decreasing step functions z, solved by
pair-adjacent violators. Temperature scaling for networks (Guo et al. 2017) is Platt scaling with B = 0 on the
logit. Scores used to judge calibration (standard definitions): Brier score BS = (1/n) sum_i (p_i - y_i)^2;
log loss LL = -(1/n) sum_i [y_i log p_i + (1 - y_i) log(1 - p_i)]; expected calibration error
ECE = sum_{m=1..M} (|B_m| / n) |acc(B_m) - conf(B_m)| (Guo et al. 2017, eq. 3), with B_m the m-th bin of
predicted probabilities.

### a.3 Worked example (arithmetic in `M4_examples.out`)
1. *One elastic-net coordinate step.* Standardised feature j with partial-residual coefficient z_j = 0.04 (in
   label units per feature standard deviation), lambda = 0.02, alpha = 0.5. Soft-threshold:
   S(0.04, 0.02 x 0.5) = S(0.04, 0.01) = 0.04 - 0.01 = 0.03. Ridge shrink: 0.03 / (1 + 0.02 x 0.5) =
   0.03 / 1.01 = **0.0297**. Check: with alpha = 1 (lasso) the result would be 0.04 - 0.02 = 0.02. With
   alpha = 0 (ridge) it would be 0.04 / 1.02 = 0.0392. The elastic net lies between the two, as it should.
2. *Platt scaling a raw score.* A model outputs f = 0.8, and the calibration fit gives A = -2.0, B = 0.1.
   A f + B = -1.6 + 0.1 = -1.5, and p = 1 / (1 + e^-1.5) = 1 / (1 + 0.22313) = **0.8176**.
3. *Why calibration decides trades.* At h = 15 minutes the hurdle is p* = 0.5817 (section 0). If the
   uncalibrated model says 0.60 but the true frequency in that bin is 0.56, the rule trades a call worth
   (2 x 0.56 - 1) x 9.734 - 1.59 = 1.168 - 1.59 = **-0.42 ticks** per round trip, when it believes it earns
   (0.20 x 9.734) - 1.59 = +0.36 ticks. A 4-point calibration error flips the sign of the edge.
4. *How much calibration data.* Niculescu-Mizil and Caruana: "When the calibration set is small (less than
   about 200-1000 cases), Platt Scaling outperforms Isotonic Regression with all nine learning methods." A
   6-month calibration block (about 126 day sessions, 816 x 6/39 = 125.5) holds 126 x 19 = 2,394
   non-overlapping 15-minute day-session labels, or 126 x 4 = 504 at 60 minutes. At 60 minutes that is inside
   the "small" range, so use Platt or none, not isotonic.

### a.4 Data it needs
A decision grid (every 1 minute, or every 10 s, inside the day session 08:30-13:20 CT and, if declared, the
overnight 19:00-07:45 CT), with each row's features computed only from events stamped before the decision time
plus the latency. Features come from the ZM MBO book (OFI, queue imbalance, signed trade flow, recent ZM mid
returns), ZS and ZL MBP-1 (their recent returns, a crush residual) and definitions (tick size, expiry and roll
dates for the v.0/v.1 switch). The label is the ZM mid (or the executable price) change over h minutes, as a
sign for logistic or as ticks for linear. One model has p of roughly 10 to 60 coefficients.

### a.5 Leakage and look-ahead traps, each with a test
- *Scaler fitted on all data.* Means and standard deviations for standardisation must come from the training
  block only. **Test (prefix invariance):** rerun the whole pipeline on data truncated at the end of fold k.
  Fold k's predictions must be bit-identical to the full run's.
- *Penalty lambda chosen by random K-fold.* glmnet's default `cv.glmnet` and sklearn's `LogisticRegressionCV`
  shuffle rows into folds. With overlapping h-minute labels on a 1-minute grid, neighbouring rows share up to
  (h-1)/h of their label, so a random fold leaks. The inner folds must be blocked by day, with a purge of h and
  an embargo. Purge mechanics belong to M5a. **Test (day-block null):** permute the labels across whole days,
  which keeps their within-day overlap, and rerun the inner CV. The selected model's inner deviance must not
  beat the intercept-only model by more than its null spread, measured over 20 permutations.
- *Calibrating on training data.* Niculescu-Mizil and Caruana: "If we use the same data set that was used to
  train the model we want to calibrate, we introduce unwanted bias." Fit A and B on a later block that the
  model did not see. **Test:** the ECE on the calibration block must be compared with the ECE on the next
  block, never with itself.
- *Label-threshold or class-weight statistics from the full sample* (for example quantile thresholds as in
  Lucchese et al., E.28 2.8 section 4.4). **Test:** the same prefix-invariance test catches it.
- *Feature timestamp at or after the decision.* **Test:** shift every feature one extra decision step into the
  past. A large drop in validation skill from one step alone flags a feature that peeks at the label window.

### a.6 Compute on the ThinkPad (measured, synthetic data, `M4_compute_probe.out`)
1,000,000 rows x 30 float32 features, 8 threads, nice 10. L2 logistic (lbfgs): **0.16 s** per fit. Elastic-net
logistic (saga, l1_ratio 0.5, 50 iterations at tol 1e-3, converged): **10.6 s** per fit. The 39-month window
at 1-minute rows, both sessions, is 860,880 rows (section (e)), so one fit is under 11 s. A 20-value lambda
path x 3 alphas x 5 outer folds = 300 fits x 10.6 s = 53 minutes at most, and much less with warm-started
paths (glmnet computes a whole path in about the time of a few fits). Memory: 1M x 30 x 4 bytes = 120 MB.
No GPU.

### a.7 Verdict: **use**, as the primary model family
It fits the sample (section (e): tens of parameters against thousands of independent labels). Its
probabilities are well calibrated before any correction: Niculescu-Mizil and Caruana place logistic regression
among the methods "well calibrated initially and post-calibration does not help them on most problems". In
the closest large high-frequency horse race, trees and neural nets beat LASSO by little (Aït-Sahalia et al.,
quoted in E.28 2.9 section 6.6). And one-minute LASSO forecasts on equities did find real, short-lived signal
(Chinco, Clark-Joseph and Ye, below). Each declared (alpha, lambda-rule, feature-set) combination is +1 to N
under V43. The lambda path itself counts as one configuration only if the rule that picks lambda (for example
"1-SE rule on blocked inner CV") is frozen in advance. That is a lead decision.

### a.8 Evidence table
| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| Elastic net is a ridge-lasso mix | Friedman, Hastie, Tibshirani 2010, JSS (academic) | "P α is a compromise between the ridge-regression penalty (α = 0) and the lasso penalty (α = 1). This penalty is particularly useful in the p ≫ N situation, or any situation where there are many correlated predictor variables." | friedman2010_glmnet_pmc.html/.txt |
| Ridge shares weight among correlated features; lasso picks one | same | "Lasso, on the other hand, is somewhat indifferent to very correlated predictors, and will tend to pick one and ignore the rest." | same |
| Logistic is calibrated without correction | Niculescu-Mizil & Caruana 2005, ICML (academic) | "Examining the histograms and reliability diagrams for logistic regression and bagged trees shows that they behave similar to neural nets. Both learning algorithms are well calibrated initially and post-calibration does not help them on most problems." and "While it is not surprising that logistic regression pre-dicts such well-calibrated probabilities" (the PDF splits the sentence across a page; joined from raw-text lines 837-840 and 1194) | niculescu_caruana2005_calibration.pdf/.raw.txt |
| Boosted trees are distorted until calibrated | same | "maximum margin methods such as boosted trees and boosted stumps push probability mass away from 0 and 1 yielding a characteristic sigmoid shaped distortion in the predicted probabilities" | same |
| Isotonic regression overfits on small calibration sets | same | "A learning curve analysis shows that Isotonic Regression is more prone to overfitting, and thus performs worse than Platt Scaling, when data is scarce." | same |
| Platt is better below about 1,000 cases | same | "When the calibration set is small (less than about 200-1000 cases), Platt Scaling outperforms Isotonic Regression with all nine learning methods." | same |
| Calibrate on independent data | same | "So we need to use an independent calibration set in order to get good posterior probabilities." | same |
| Modern networks are miscalibrated; temperature scaling fixes it | Guo et al. 2017, ICML, arXiv 1706.04599 (academic) | "modern neural networks, unlike those from a decade ago, are poorly calibrated" and "temperature scaling – a single-parameter variant of Platt Scaling – is surprisingly effective at calibrating predictions" | guo2017_calibration.pdf |
| LASSO finds short-lived 1-minute predictors | Chinco, Clark-Joseph, Ye, NBER w23933 (2017), published JF 74(1) 2019 (academic) | "The LASSO increases both out-of-sample fit and forecast-implied Sharpe ratios. And, this out-of-sample success comes from identifying predictors that are unexpected, short-lived, and sparse." | chinco2017_nber_w23933.pdf |
| The size of that gain | same | "increases out-of-sample fit by at least ∆R̄n2 = 1.2%pt relative to just using the benchmark model by itself" and "this forecast-implied strategy generates an annualized Sharpe ratio of 1.8 net of trading costs" | same |
| It refits in short rolling windows | same | "we use the LASSO to make 1-minute-ahead return forecasts in rolling 30-minute estimation windows using the entire cross-section of lagged returns as candidate predictors" | same |

Caveat on Chinco et al.: equities, 2005-2012, 2,191 stocks of cross-sectional predictors. ZM has three
instruments, so the "sparse among thousands" mechanism does not carry over. What carries over is the
evidence that minute-scale signals are short-lived and need frequent refits (topic (d)).

## (b) Gradient-boosted trees (LightGBM): depth limits, monotone constraints, early stopping

### b.1 Core idea
A sum of small regression trees, each fitted to the gradient of the loss left by the previous ones (objective,
leaf weights and split gain in E.28 2.9 section 6.2, XGBoost eqs. 2, 4, 5, 6; worked leaf example in E.28 2.9
section 6.3). Three things matter for a weak minutes-scale signal. A depth limit caps how many features can
interact in one tree. A monotone constraint makes the prediction move in a declared direction in a feature
whose sign is economically fixed. Early stopping chooses the number of trees and is the main leakage risk
inside purged folds.

### b.2 Equations (what is new beyond E.28 2.9)
- Leaves per tree: with depth d, a depth-wise tree has at most L = 2^d leaves, so d = 3 gives L = 8.
  LightGBM grows trees leaf-wise, so depth and leaf count are separate settings: "max_depth ... limit the max
  depth for tree model. This is used to deal with over-fitting when #data is small. Tree still grows
  leaf-wise", and "num_leaves, default = 31". The tuning page: "Theoretically, we can set num_leaves =
  2^(max_depth) to obtain the same number of leaves as depth-wise tree"
  (`lightgbm_parameters.html`, `lightgbm_tuning.html`). Setting max_depth = 3 alone already caps a tree at 8
  leaves, because the default 31 cannot be reached. Declare num_leaves <= 8 anyway, so the frozen
  configuration says what it does.
- Model size: K trees x L leaves gives K L leaf values plus K (L - 1) split thresholds. K = 300 and L = 8
  give 2,400 leaf values and 2,100 thresholds. Leaf values are shrunk by the learning rate eta and by lambda
  (w*_j = -G_j / (H_j + lambda), E.28 2.9 eq. 5), so the effective degrees of freedom are far fewer than
  4,500. No closed form is available. Treat the comparison with independent labels (section (e)) as an upper
  bound on risk.
- Monotone constraint, increasing in feature j: f(x) <= f(x') whenever x_j <= x'_j and all other features are
  equal. In LightGBM: "1 means increasing, -1 means decreasing, 0 means non-constraint". There are three
  enforcement methods: "basic ... does not slow down the training speed at all, but over-constrains the
  predictions"; "intermediate ... much less constraining than the basic method"; "advanced ... even less
  constraining" (`lightgbm_parameters.html`). The method is a hyperparameter. Choosing among methods on
  results adds configurations to N.
- Path smoothing (optional regulariser for small leaves, LightGBM docs): w = w (n/s) / (n/s + 1) +
  w_p / (n/s + 1), with n the leaf count, s = path_smooth and w_p the parent's weight.
- Early stopping: "will stop training if one metric of one validation data doesn't improve in last
  early_stopping_round rounds" (`lightgbm_parameters.html`). The selected K* = argmin_k
  Loss_valid(F_k), where F_k is the model after k rounds. K* is a statistic of the validation block, so
  whatever block it comes from is no longer out-of-sample for K*.

### b.3 Worked example
1. *Effective leaf occupancy in independent labels.* Rows on a 1-minute grid with a 15-minute label: one
   independent label spans 15 rows. LightGBM's default min_data_in_leaf = 20 rows is therefore about
   20 / 15 = 1.3 independent labels, so a leaf can be fitted to about one label's worth of noise. To require
   at least m = 30 independent labels per leaf, set min_data_in_leaf >= m x (h / Delta) = 30 x 15 / 1 = 450
   rows. At h = 60 on the same grid it is 30 x 60 = 1,800 rows. Check: the training fold of 60% of 816 days
   x 290 rows = 141,984 day-session rows, divided by 8 leaves, gives about 17,700 rows per leaf on average,
   so 1,800 rows is not binding for the average leaf. It is binding only for leaves cut off in a tail.
2. *Model size against independent labels.* 15-minute day-session labels in a 60% training fold:
   0.6 x 15,504 = 9,302 (section (e)). K = 300 trees of 8 leaves give 2,400 leaf values, or 2,400 / 9,302 =
   0.26 leaf values per independent label. With eta = 0.05, each leaf moves the fit only 5% of its
   Newton step, which is why shrinkage plus early stopping, not leaf count, is the real capacity control.
3. *Leaf-weight shrinkage.* E.28 2.9 section 6.3: residuals -0.5, -0.2, +0.1 tick, lambda = 1 gives
   w* = +0.15 tick instead of the plain mean of 0.2. With lambda = 10, w* = 0.6 / (3 + 10) = 0.046 tick.
   Large lambda matters for leaves holding few independent labels.
4. *Monotone sign, honestly.* For minutes-ahead ZM direction, very few signs are economically fixed. Order-flow
   imbalance is contemporaneously positive (E.28 2.9 section 1). Its predictive sign at 15 minutes can be
   continuation or reversal, and is not fixed. A crush-residual reversion feature has a fixed sign only if the
   declared hypothesis is reversion: then "ZM rich relative to the crush, so lower future ZM return" means
   monotone -1. A constraint is legitimate only when it restates a pre-registered directional hypothesis.
   Otherwise it is a free choice that must be counted.

### b.4 Data it needs
Same rows and features as (a). Trees need no standardisation and handle interactions (session x imbalance,
spread state x flow) without hand-made products. Session indicators (day versus overnight, minutes since
08:30, report-day flags) are natural split variables.

### b.5 Leakage and look-ahead traps, each with a test
- *Early stopping on the test fold.* K* chosen on the block that is then reported as "out-of-sample" makes
  that score optimistic. This is the selection bias of Cawley and Talbot (2010): "over-fitting in model
  selection can result in biased performance evaluation if model selection is not viewed as an integral part
  of the modelling procedure". **Rule:** K* comes from an inner validation block carved from the end of the
  training fold. That block is purged (label horizon h) from the inner training rows and embargoed from the
  outer test fold. **Test:** log, for every outer fold, which row indices the early-stopping set used. Their
  intersection with the outer test fold's indices, widened by h on each side, must be empty (a mechanical
  assertion).
- *Random-row early-stopping split inside the training fold.* With overlapping labels and autocorrelated
  features, a random 10% holdout sits next to its training neighbours. Its loss keeps falling for longer, so
  K* is too large (overfit), and the inflated validation score feeds any later selection. **Test (day-block
  null):** permute labels across whole days and run the full pipeline. The median K* must stay near the
  minimum number of rounds, and validation AUC must be about 0.5 (within its permutation spread). Under a
  random-row split, the null run will typically show more rounds and AUC above 0.5. That is the leak's
  signature.
- *K* re-tuned per outer fold and then a final model refitted on all data with a K chosen by looking at
  outer-fold scores.* That is a selection on the test folds. **Rule and test:** freeze the refit rule, for
  example "K_final = median of the inner K* times n_full / n_inner". The final score is the one-shot test
  under V43.
- *Binning (histogram) bounds computed on the full sample.* LightGBM builds feature bins from the Dataset it
  is given. Build the Dataset from the training fold only and construct validation and test with
  `reference=` to the training Dataset (installed lightgbm 4.7.0 docstring: "If this is Dataset for validation,
  training data should be used as reference"). **Test:** prefix invariance, as in (a).
- *Monotone constraints or features chosen after looking at fold results.* **Test:** the frozen
  configuration's hash is recorded before the first fit. Any change adds configurations to N.

### b.6 Compute on the ThinkPad (measured, synthetic data, `M4_compute_probe.out`)
Depth 3, 8 leaves, eta 0.05, min_data_in_leaf 500, lambda_l2 10, 500 rounds, 30 features, 8 threads, nice 10:

| Rows | Unconstrained | Monotone on 5 features (intermediate) |
|---|---|---|
| 1,000,000 | 26.3 s | 27.2 s |
| 5,000,000 | 91.3 s | 74.8 s |

The two 5M timings are within noise of each other: the monotone run happened to be faster, and one run each
is not enough to tell them apart. The 39-month window has 860,880 one-minute rows over both sessions, or
5,165,280 ten-second rows (section (e)). So one fit takes under 30 s at 1-minute and under 2 minutes at
10-second sampling. Memory: 5M x 30 x 4 bytes = 600 MB for the raw matrix, plus LightGBM's binned copy (1
byte per value per feature at <= 255 bins, about 150 MB). An illustrative fixed grid of 3 eta x 2
min_data_in_leaf x 2 feature sets = 12 configurations x 5 outer folds = 60 fits x 26 s = 26 minutes at
1-minute rows. No GPU (LightGBM's GPU build is not needed at this size).

### b.7 Verdict: **maybe**, as one or two declared secondary configurations next to the linear primary
Shallow (depth <= 3) boosted trees can pick up session-by-state interactions the linear model misses. The
best large comparison found them little better than LASSO at high frequency (E.28 2.9 section 6.6). Their raw
probabilities need Platt calibration (Niculescu-Mizil and Caruana: boosted trees push "probability mass away
from 0 and 1"), which adds a calibration block. Early stopping must sit inside the purged inner split.
Monotone constraints only where the sign restates the declared hypothesis.

### b.8 Evidence table
| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| max_depth controls over-fitting; tree still grows leaf-wise | LightGBM docs (developer documentation), "latest" page, fetched 2026-10-27; project env has lightgbm 4.7.0 | "limit the max depth for tree model. This is used to deal with over-fitting when #data is small. Tree still grows leaf-wise" | lightgbm_parameters.html |
| num_leaves vs depth | LightGBM tuning docs | "Theoretically, we can set num_leaves = 2^(max_depth) to obtain the same number of leaves as depth-wise tree." | lightgbm_tuning.html |
| Monotone constraint encoding | LightGBM docs | "1 means increasing, -1 means decreasing, 0 means non-constraint you need to specify all features in order." | lightgbm_parameters.html |
| Basic method over-constrains | LightGBM docs | "basic, the most basic monotone constraints method. It does not slow down the training speed at all, but over-constrains the predictions" | same |
| Early stopping definition | LightGBM docs | "will stop training if one metric of one validation data doesn’t improve in last early_stopping_round rounds" | same |
| min_data_in_leaf default 20 | LightGBM docs | "min_data_in_leaf ... default = 20 ... minimal number of data in one leaf. Can be used to deal with over-fitting" | same |
| Selection on the evaluation data biases it | Cawley & Talbot 2010, JMLR 11 (academic) | "Section 5 shows that over-fitting in model selection can result in biased performance evaluation if model selection is not viewed as an integral part of the modelling procedure." | cawley_talbot2010.pdf |
| Unbiased evaluation needs nesting | same | "robust unbiased performance evaluation is likely to require more rigorous and computationally intensive protocols, such a nested cross-validation or “double cross” (Stone, 1974)." | same |
| Variance of the selection criterion causes overfitting in selection | same | "a nonnegligible variance introduces the potential for over-fitting in model selection as well as in training the model" | same |
| Trees add little over LASSO at high frequency | Aït-Sahalia et al. 2022 via E.28 2.9 section 6.6 | "The improvements from a nonlinear method like random forest or gradient boosting trees are limited for most cases when compared with LASSO." | reports/stage_e28_briefs/pages/C2_OFI/afxz2022_hf_predictable.pdf/.txt |
| Boosted-tree probabilities are distorted | Niculescu-Mizil & Caruana 2005 | quoted in (a) | niculescu_caruana2005_calibration.pdf |

## (c) Small sequence models (DeepLOB-style CNN-LSTM, TCN, small transformers): the data-size verdict

### c.1 Core idea
Instead of hand-made features, these models read a window of the last T book or bar states and learn their own
features. DeepLOB stacks convolutions over book levels, then an Inception block and an LSTM (equations in E.28
2.8 section 1.2). A temporal convolutional network (TCN) uses causal dilated 1-D convolutions. A small
transformer uses self-attention over the window. The question for this stage is not whether they can be
trained on the laptop (they can). It is whether 39 months of one contract hold enough independent
minutes-scale labels to fit tens of thousands of weights without fitting noise.

### c.2 Equations
- TCN dilated causal convolution (Bai, Kolter and Koltun 2018, eq. 2; `bai2018_tcn.pdf`):
  F(s) = (x *_d f)(s) = sum_{i=0..k-1} f(i) x_{s - d i}, where x is the input sequence, f a filter of size k,
  and d the dilation factor ("Where d is the dilation factor, k is the filter size, and s − d · i accounts for
  the direction of the past"). Only past inputs enter, so the convolution is causal by construction.
- Receptive field of a TCN with L residual blocks, two convolutions per block, filter size k and dilations
  d_l = 2^l (l = 0..L-1): R = 1 + 2 (k - 1) sum_l 2^l = 1 + 2 (k - 1)(2^L - 1). This is my derivation for
  the block layout of their Figure 1; the paper gives the per-layer rule, not this total.
- Self-attention (standard): Attention(Q, K, V) = softmax(Q K' / sqrt(d_k)) V, with Q, K, V linear maps of
  the T x d input. Parameters per encoder layer are about 4 d^2 (attention) + 2 d d_ff (feed-forward).
- DeepLOB: E.28 2.8 section 1.2 (label eqs. and architecture; 60,947 parameters in the paper version, E.28
  2.8 section 10.1).
- Parameter-to-sample ratio: q = (number of trainable weights) / (number of independent labels in the
  training fold). This is a heuristic, not a bound: weight sharing and early stopping lower the effective
  count. A ratio well above 1 means the label set cannot pin the weights down, and the fit is decided by
  regularisation and the seed.

### c.3 Worked example (`M4_examples.out`, `M4_compute_probe.out`)
1. *TCN receptive field.* The probe's TCN has L = 6 blocks, k = 3, dilations 1, 2, 4, 8, 16, 32:
   R = 1 + 2 x 2 x 63 = **253** steps. On a 1-minute grid that is 253 minutes, nearly the whole 290-minute
   day session. On a 10-second grid it is 42 minutes.
2. *Parameters against independent labels (whole 39 months, day session only; section (e) gives the
   counts).* q = params / labels:

   | Model (params) | 1-min labels 236,640 | 5-min 47,328 | 15-min 15,504 | 60-min 3,264 |
   |---|---|---|---|---|
   | TCN probe (38,081) | 0.16 | 0.80 | 2.46 | 11.7 |
   | DeepLOB paper (60,947) | 0.26 | 1.29 | 3.93 | 18.7 |
   | Tiny transformer probe (110,209) | 0.47 | 2.33 | 7.11 | 33.8 |

   Check (DeepLOB, 15 min): 60,947 / 15,504 = 3.93. These counts are for the whole window. A training fold of
   60% raises every q by 1/0.6 = 1.67x. At the horizons where the cost hurdle can be met (15 to 60 minutes,
   section 0), every sequence model has 2 to 34 weights per independent label. A 30-feature logistic model has
   30 / 15,504 = 0.002.
3. *What the labels can detect at all.* With n independent labels, a correlation (information coefficient,
   IC) between forecast and outcome is about 3 standard errors from zero when IC = 3 / sqrt(n). For 15-minute
   day-session labels over 39 months, IC = 3 / sqrt(15,504) = 0.024; over a 60% fold, 3 / sqrt(9,302) =
   0.031. Any signal weaker than that is invisible to any model. A model with 60,000 weights must find that
   signal using no more labels than the 30-weight model has.

### c.4 Data it needs
A T x F tensor per decision row. For DeepLOB proper, the top 10 book levels per event. ZM MBO can rebuild them
(E.28 2.8 section 1.3: "mbo is a superset (mbp-10 can be built from it)"), but ZS and ZL are MBP-1 only, so a
deep book model sees depth for ZM alone. For TCNs and transformers on bars, T bars of F engineered features (as
in (a)). GPU memory is not binding: probe peak 165 MiB (TCN) and 365 MiB (transformer) at batch 256 and
T = 128.

### c.5 Leakage and look-ahead traps, each with a test
- *Overlapping windows across the train/validation boundary.* A window of T steps for the first validation row
  reaches T - 1 steps into the training block, and its label reaches h past the row. Purge T + h rows (T for
  features, h for labels) at every boundary. **Test:** assert that no validation or test row's input window or
  label window intersects a training row's label window.
- *Non-causal layers.* Same-padding convolutions, bidirectional LSTMs and unmasked attention over a window
  that includes post-decision steps all see the future. **Test (future perturbation):** change the input at
  steps after the decision time. The output must not change, to the bit.
- *Normalisation statistics over the whole dataset.* (DeepLOB normalises with prior-day statistics, E.28 2.8.)
  **Test:** prefix invariance, as in (a).
- *Early stopping, seed choice and architecture search on the test block* (the LOBCAST lesson, E.28 2.8
  section 4.1). Each seed kept by result is a configuration. **Test:** record all seeds and report the mean
  over a fixed seed set, never the best.
- *Calibration.* Guo et al.: modern networks "are poorly calibrated". A probability rule needs temperature
  scaling on a separate block (topic (a)).

### c.6 Compute on the ThinkPad (measured, synthetic tensors, RTX 3050 4 GB)
Training throughput, batch 256, T = 128, 30 input channels, AdamW: TCN 32 channels x 6 blocks (38,081
params) **18,018 samples/s**, peak 165 MiB. 2-layer transformer, d = 64, 4 heads (110,209 params)
**4,466 samples/s**, peak 365 MiB. DeepLOB (paper) 5,247 samples/s at batch 256 (E.28 2.8 section 10.1).
One epoch over the 39-month day-session 1-minute rows (236,640) takes 236,640 / 18,018 = 13 s for the TCN and
53 s for the transformer. Over 10-second rows, both sessions (5,165,280), it takes 287 s and 1,157 s, so
40 epochs take 3.2 h and 12.9 h. A grid of 10 configurations x 5 seeds x 5 folds at 40 epochs on 10-second
rows is 250 runs x 3.2 h = 800 GPU-hours for the TCN. Compute is not the barrier at 1-minute sampling. It
becomes the barrier at 10-second sampling with seeds, and then only multiplies a problem the data already has.

### c.7 Verdict: **skip** for the minutes-scale directional search (no pre-registered deep model in E.33)
The data-size verdict: at the horizons where p* is reachable (15 to 60 minutes), every small sequence model
has 2 to 34 weights per independent label over all 39 months (q table above), and the detectable IC floor is
the same for every model. The published evidence for deep LOB models is at 10 to 100 book events, mostly
under 10 seconds (Briola et al. Table 7; E.28 2.8 section 4.3). Even there, the gain over simple models is
disputed (LOBCAST, Briola-Turiel-Aste 2020 "an MLP is as good", E.28 2.8 section 4.2). In long-horizon time
series, a one-layer linear model beat transformers "in all cases", and transformers "are prone to overfit on
noisy financial data" (Zeng et al. 2023). The planner's "No deep LOB models" is supported (planner table). If
the lead wants a non-linear sequence check, a TCN on the same features as the linear model, declared as one
configuration with a fixed seed set, is the cheapest. It is not recommended.

### c.8 Evidence table
| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| Dilated causal convolution definition | Bai, Kolter, Koltun 2018, arXiv 1803.01271 (academic) | "Where d is the dilation factor, k is the filter size, and s − d · i accounts for the direction of the past." | bai2018_tcn.pdf/.raw.txt |
| TCNs beat canonical RNNs on generic benchmarks | same | "Our results indicate that a simple convolutional architecture outperforms canonical recurrent networks such as LSTMs across a diverse range of tasks and datasets, while demonstrating longer effective memory." | same |
| Linear beats transformers for time-series forecasting | Zeng, Chen, Zhang, Xu 2023, AAAI, arXiv 2205.13504 (academic) | "Experimental results on nine real-life datasets show that LTSF-Linear surprisingly outperforms existing sophisticated Transformer-based LTSF models in all cases, and often by a large margin." | zeng2023_ltsf_linear.pdf |
| Transformers overfit noisy financial data | same | "LTSF-Transformers with different positional and temporal embeddings preserve quite limited temporal relations and are prone to overfit on noisy financial data, while the LTSF-Linear can model the order naturally and avoid overfitting with fewer parameters." | same |
| Networks miscalibrated | Guo et al. 2017 | quoted in (a) | guo2017_calibration.pdf |
| Deep LOB data-size verdict | E.28 2.8 section 1.3 | "The binding constraint is independence, not sample count" (full quote in section 0) | reports/stage_e28_methods_brief.md |
| Deep LOB horizons are seconds | Briola, Bartolucci, Aste (arXiv 2403.09267v4; QF 25(7) 2025) | "for all the stocks, except MCD (small-tick stock) and ABBV (medium-tick stock), 10 LOB’s updates are more likely to happen in a physical time < 1 s" | reports/stage_e28_briefs/pages/C2_DeepLOB/briola_microstructural_guide2024.pdf/.raw.txt (sha256 1642bd28...) |

Caveat on Zeng et al.: their datasets are long-horizon (hours to days ahead) and include one exchange-rate
series, not intraday futures. The quote supports "transformers overfit noisy series", not a ZM-specific result.

## (d) Online and regime-switching models: online logistic, RLS with forgetting, Markov-switching regression, Kalman time-varying coefficients

### d.1 Core idea
If the relation between features and future ZM returns drifts (the planner expects a break between discovery,
2020-24, and test, 2017-20), a model fitted once on 39 months predicts with stale weights. Online models update
the weights as each label arrives. Online logistic regression does it by a gradient step. Recursive least
squares (RLS) with a forgetting factor, which is the same thing as a Kalman filter on random-walk
coefficients, does it by an exact weighted least-squares update. A Markov-switching regression lets the
weights jump between K fixed sets. The price is new tuning choices (learning rate, forgetting factor, K), each a
configuration under V43, and a timing trap: an h-minute label is only known h minutes later.

### d.2 Equations
- *Online logistic regression* (McMahan et al. 2013, eq. 1 and the OGD update; `mcmahan2013_ftrl.pdf`):
  p_t = sigma(w_t . x_t), sigma(a) = 1/(1 + exp(-a)); loss l_t(w_t) = -y_t log p_t - (1 - y_t) log(1 - p_t);
  gradient "∇l_t(w) = (σ(w · x_t) − y_t)x_t = (p_t − y_t)x_t"; online gradient descent
  "w_{t+1} = w_t − η_t g_t, where η_t is a non-increasing learning-rate schedule". Their FTRL-Proximal
  variant adds per-coordinate rates eta_{t,i} = alpha / (beta + sqrt(sum_s g_{s,i}^2)) (their eq. 2) and L1
  sparsity. For a drifting target the schedule must NOT decay to zero. A constant eta gives exponential
  forgetting, roughly over 1/(eta x curvature) steps (my statement, standard for SGD on a quadratic).
- *Kalman time-varying-parameter regression with forgetting* (Raftery, Kárný and Ettler 2010, Technometrics,
  eqs. 1-9; `raftery2010_dma.pdf`):
    observation  y_t = x_t' theta_t + eps_t,  eps_t ~ N(0, V)                     (1)
    state        theta_t = theta_{t-1} + delta_t,  delta_t ~ N(0, W_t)           (2)
    prediction   theta_t | Y^{t-1} ~ N(theta_hat_{t-1}, R_t),  R_t = Sigma_{t-1} + W_t   (3), (4)
    forgetting   R_t = lambda^{-1} Sigma_{t-1}                                    (5)
    update       theta_hat_t = theta_hat_{t-1} + R_t x_t (V + x_t' R_t x_t)^{-1} e_t,  e_t = y_t - x_t' theta_hat_{t-1}   (7)
                 Sigma_t = R_t - R_t x_t (V + x_t' R_t x_t)^{-1} x_t' R_t        (8)
    delayed use  y_hat_t = x_t' theta_hat_{t-d-1}                                (9)
  "λ is called the forgetting factor and is typically slightly below 1", with W_t = a Sigma_{t-1},
  a = lambda^{-1} - 1, and "the effective amount of data used for estimation, or the effective window size, is
  h = 1/(1 − λ)". With V = 1 this is exactly RLS with exponential forgetting: P_t = Sigma_t / V,
  k_t = P_{t-1} x_t / (lambda + x_t' P_{t-1} x_t), theta_t = theta_{t-1} + k_t e_t,
  P_t = (P_{t-1} - k_t x_t' P_{t-1}) / lambda (my algebra: substitute R_t = P_{t-1}/lambda into (7)-(8)).
  Equation (9) is the label-delay rule: when the outcome is known only d steps late, predict with the
  estimate from d + 1 steps back.
- *Markov-switching regression* (statsmodels `MarkovRegression` docs, after Kim and Nelson 1999; Hamilton
  filter in E.28 2.5 section 4.2): y_t = a_{S_t} + x_t' beta_{S_t} + eps_t, eps_t ~ N(0, sigma^2_{S_t}),
  S_t in {1..K} a first-order Markov chain with transition matrix P = [p_ij]. Filtering, likelihood and
  EM are those of E.28 2.5 (Hamilton eqs. 5-12). Optional time-varying transition probabilities
  ("exog_tvtp", logit of observable variables).

### d.3 Worked example (`M4_examples.out`)
1. *One RLS-with-forgetting step* (one feature). theta_{t-1} = 0.02 ticks per unit, P_{t-1} = 50,
   lambda = 0.99, x_t = 1.5, y_t = 0.8 ticks. Gain k = 50 x 1.5 / (0.99 + 1.5 x 50 x 1.5) = 75 / 113.49 =
   0.66085. Error e = 0.8 - 1.5 x 0.02 = 0.77. theta_t = 0.02 + 0.66085 x 0.77 = **0.52886**.
   P_t = (50 - 0.66085 x 1.5 x 50) / 0.99 = (50 - 49.5638) / 0.99 = **0.44057**. Check: a diffuse prior
   (P = 50) makes the first update almost an OLS fit of one point (y/x = 0.533). theta moved to 0.529, close to
   that, as it should.
2. *Forgetting factor in session time.* Effective window h = 1/(1 - lambda). On a 1-minute day-session grid
   (290 rows a day): lambda = 0.99 gives 100 rows = 0.34 sessions; 0.999 gives 1,000 rows = 3.4 sessions;
   0.9999 gives 10,000 rows = 34.5 sessions. With a 15-minute label, the rows inside a window are not
   independent: 1,000 rows hold about 1,000/15 = 67 independent labels. A window short enough to track
   intraday drift (lambda = 0.999) estimates each coefficient from about 67 labels, so its standard error is
   about 1/sqrt(67) = 0.12 in correlation units. That is five times the IC floor of 0.024 from (c.3), so the
   tracking weights are mostly noise unless the signal is far stronger than anything published for grains.
   This is the bias-variance trade the forgetting factor sets, and why it cannot be tuned freely.
3. *Label delay.* With h = 15 minutes on a 1-minute grid, d = 15: the forecast at 10:00 may use only
   coefficients updated with labels whose 15-minute window closed by 10:00, that is, outcomes for decision
   times up to 09:45 (Raftery eq. 9 with d = 15).
4. *Markov-switching regime durations.* With p_11 = 0.98 on a 1-minute grid, the expected stay in regime 1 is
   1/(1 - 0.98) = 50 minutes (E.28 2.5 section 4.2 formula). With p_11 = 0.9993 it is about 1,430 minutes,
   or about 5 day sessions. The regime's labels per stay are what the regime's beta is fitted from, so the
   same independent-label arithmetic applies within each regime.

### d.4 Data it needs
Same features and labels as (a), processed strictly in time order, plus a clock of when each label is
realised (decision time + h). For Markov-switching on minute data, the full 39-month series fits in memory.
Session boundaries need a rule: carry the state over the 13:20-19:00 CT break and the weekend, or reset it.
That rule is a frozen choice.

### d.5 Leakage and look-ahead traps, each with a test
- *Updating with labels not yet realised.* The commonest online-model leak: updating at step t with y_t
  whose window ends at t + h. **Test:** each update record carries the label-realisation timestamp, and the
  forecast at time tau may only use updates with realisation time <= tau - latency (a mechanical assertion
  over every row; Raftery eq. 9).
- *Smoothed regime probabilities or a full-sample Viterbi path used as features* (E.28 2.5 section 4.2:
  "run on the whole sample, it looks ahead"). Only filtered probabilities xi_{t|t} may be used, from
  parameters fitted on the training block. **Test:** future perturbation, as in (c): change data after tau,
  and the regime probability at tau must not move.
- *Hyperparameters (eta, lambda, K, starting values) tuned on the test period.* Every value tried is a
  configuration. **Test:** the frozen configuration hash is recorded before the first test-period prediction.
- *"Online" evaluation that reuses the initial batch fit's sample.* Use progressive validation: score each
  prediction before its label updates the model. McMahan et al.: "We generally use progressive validation
  (sometimes called online loss) [5] rather than cross-validation or evaluation on a held out dataset."
  **Test:** prefix invariance holds by construction. Check it anyway.
- *Label switching in Markov-switching EM across folds* (regime 1 in one fold is regime 2 in another).
  **Rule:** order regimes by a declared statistic (for example sigma_{S}), fixed in advance.

### d.6 Compute on the ThinkPad
Measured, synthetic data: RLS with forgetting, p = 30, a plain Python and numpy loop: 200,000 steps in 1.64 s,
so 860,880 one-minute rows take about 7 s per pass. A lambda grid of 3 values x 5 folds is under 2 minutes.
Online logistic regression costs less than one RLS step per row. Markov-switching and HMM costs, measured in
E.28 2.5 section 4.7 (numpy): forward filter 200,000 steps in 0.72 s, ten Baum-Welch iterations 27.3 s, about
4.5 minutes for ten iterations on 1.87M steps. A K = 2 Markov-switching regression adds a weighted least-squares
solve per regime per iteration, which is cheap at p = 30. statsmodels 0.15.0 provides `MarkovRegression` but is
not in the project environment (E.28 2.5 section 1.7). A numpy version is short. A Kalman TVP regression is the
RLS loop above. No GPU for any of these.

### d.7 Verdict
- **Online logistic or RLS/Kalman TVP with a fixed forgetting factor: maybe**, as one declared configuration
  that wraps the primary linear model (same features, lambda fixed in advance from an economic window such
  as "about 20 sessions", lambda = 1 - 1/(20 x 290) = 0.99983 on a 1-minute grid). It is the cheapest
  answer to the expected discovery/test regime break, and Chinco et al.'s 1-minute result came from frequent
  re-estimation. Against: the variance arithmetic in d.3 item 2, and no grain evidence.
- **Markov-switching regression as a directional forecaster: skip.** Same verdict as E.28 2.5 section 9
  ("HMM as a return forecaster (directional): skip") on the same evidence: regime models forecast poorly
  out of sample because misclassification of future regimes dominates (Engel 1994; Bessec and Bouabdallah,
  quoted in E.28 2.5 section 4.8). A 2-state volatility gate (trade or stand aside) remains E.28's "maybe",
  but that is a filter, not a direction model, and belongs to the lead's family design.

### d.8 Evidence table
| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| Online logistic gradient | McMahan et al. 2013, KDD, "Ad Click Prediction: a View from the Trenches" (firm research, Google) | "It is straightforward to show ∇ℓt(w) = (σ(w · xt) − yt)xt = (pt − yt)xt, and this gradient is all we will need for optimization purposes." | mcmahan2013_ftrl.pdf/.raw.txt |
| OGD update with non-increasing rate | same | "OGD performs the update wt+1 = wt − ηt gt , where ηt is a non-increasing learning-rate schedule" | same |
| Progressive validation | same | "We generally use progressive validation (sometimes called online loss) [5] rather than cross-validation or evaluation on a held out dataset." | same |
| Forgetting factor definition | Raftery, Kárný, Ettler 2010, Technometrics 52(1) (academic) | "where λ is called the forgetting factor and is typically slightly below 1." | raftery2010_dma.pdf/.raw.txt |
| Effective window h = 1/(1−λ) | same | "estimation in this model is essentially age-weighted estimation where data i time points old has weight λi , and the effective amount of data used for estimation, or the effective window size, is h = 1/(1 − λ)." | same |
| Delayed outcomes use an older estimate | same | "The information available for predicting yt is d samples old because of the time-delay problem, and so we use ŷt = xtT θ̂t−d−1 ." | same |
| Markov-switching regression form | statsmodels 0.15.0 docs (developer documentation) | "the model is a dynamic linear regression where the coefficients and the variance of the error term may be switching across regimes" | statsmodels_markovregression.html |
| Regime forecasts fail on misclassification | Bessec & Bouabdallah via E.28 2.5 section 4.8 | "We find that the main source of error is due to the misclassification of future regimes" | reports/stage_e28_briefs/pages/C2_Filter/bessec_bouabdallah_2005.txt (E.28 file) |
| Short rolling windows find 1-minute signals | Chinco et al. | quoted in (a) | chinco2017_nber_w23933.pdf |

Not found: an intraday futures study that compares a fixed-weight model with an online or TVP version of the
same model out of sample and net of costs. Dangl and Halling (2012, JFE), the standard reference for
time-varying-coefficient return prediction, is monthly equity-premium work and was not fetched [unverified,
named from memory only, so no claim rests on it].

## (e) Effective sample size per horizon and parameter-to-sample ratios

### e.1 Core idea
The number of rows is not the number of independent pieces of evidence. With an h-minute label sampled every
minute, consecutive labels share h - 1 of their h minutes. The count that limits what any model can learn,
and what any test can show, is close to the number of NON-overlapping label windows. Within-day dependence
(volatility clustering, a day's common news) lowers it further. This section counts the non-overlapping
windows from session lengths and the calendar, without reading data.

### e.2 Equations
- Non-overlapping labels per session: n_s(h) = floor(L_s / h), with L_s the session length in minutes.
- Over D trade dates: N(h) = D x n_s(h), per session type.
- Session lengths (READER_BRIEF, CT): day 08:30-13:20 = **290 minutes**; overnight 19:00-07:45 =
  **765 minutes** (12 h 45 min); sum 1,055 minutes. Day-session volume share 0.83 (READER_BRIEF table), so
  overnight minutes carry about 17% of the volume over 2.6 times the minutes.
[MathReview D-3 (lead: accepted): M3 g.3 allows label spans only from 08:35 to 13:13 (278 minutes) and 19:05 to 07:44 overnight (759 minutes) and excludes roll dates and the next date (E.31: 52 of 816 dates); on the 278 basis 15-min labels per session are 18 not 19 and 5-min 55 not 58 (30, 60, 120, 240 unchanged), so on D = 816 the 15-min day total is 14,688 (not 15,504), the 60% fold 8,813 (not 9,302), IC floor 0.0248 (not 0.0241), GBM-300 q 0.27 (not 0.26), and with E.31's exclusions (D about 764) 13,752 whole-window, 8,251 in a 60% fold, IC floor 0.033 in the fold (recomputed table in d_m4.out, "day278" columns). Verdicts are unchanged (q <= 0.004 for linear, 0.27-0.29 for GBM-300 at 15 min, 4-125 for sequence models); M4 should state the 278/759-minute basis and that D after g.3 rules 5-7 is about 764, so M5b's power arithmetic reads the smaller n_eff (also applies at original lines 585-594, 601-607, 616-627, 121-122, 234-236, 352-356).]
- Overlapping rows on a grid of step Delta: R(h) = D x L_s / Delta rows, with an overlap factor of about
  h / Delta between rows and independent labels.
- Design effect for day clustering (standard survey formula, my addition): n_eff = N / (1 + (m - 1) rho),
  with m labels per day and rho their average intra-day correlation. Unknown until E.33 measures it.
- Detectable effect at t = 3: IC_min = 3 / sqrt(n_eff) for a correlation-type signal, or equivalently the
  number of labels for an IC: n = (3 / IC)^2.
- Parameter-to-sample ratio: q = k / n_eff, with k the model's free parameters (or leaf values).

### e.3 Worked example: counts over the 39-month owned window (2020-12-01 to 2024-02-29)
Calendar (`M4_ess.py`): 848 weekdays minus 32 ASSUMED full-day CBOT grain closures (New Year, MLK, Presidents,
Good Friday, Memorial, Juneteenth from 2022, Independence, Labor, Thanksgiving, Christmas, with the observed
dates listed in the script) = **D = 816 trade dates**. The DataFacts worker owns the true calendar.
Early-close days, roll and notice exclusions, and the 1-2 minutes after releases that the planner would drop
all lower these counts. The memory note on the equity calendar booking US holidays as trade dates applies:
do not take D from that calendar.

| h (min) | per day session (290 min) | per overnight (765 min) | day total (D = 816) | overnight total | both | IC_min (t = 3), day | IC_min, both |
|---|---|---|---|---|---|---|---|
| 1 | 290 | 765 | 236,640 | 624,240 | 860,880 | 0.0062 | 0.0032 |
| 5 | 58 | 153 | 47,328 | 124,848 | 172,176 | 0.0138 | 0.0072 |
| 15 | 19 | 51 | 15,504 | 41,616 | 57,120 | 0.0241 | 0.0126 |
| 30 | 9 | 25 | 7,344 | 20,400 | 27,744 | 0.0350 | 0.0180 |
| 60 | 4 | 12 | 3,264 | 9,792 | 13,056 | 0.0525 | 0.0263 |
| 120 | 2 | 6 | 1,632 | 4,896 | 6,528 | 0.0743 | 0.0371 |
| 240 | 1 | 3 | 816 | 2,448 | 3,264 | 0.1050 | 0.0525 |
| to close (13:15-ish) | 1 per decision time | n/a | 816 | n/a | 816 | 0.1050 | n/a |

Check rows: 290 / 15 = 19.33, floored to 19; 19 x 816 = 15,504; 3 / sqrt(15,504) = 3 / 124.5 = 0.0241.
765 / 60 = 12.75, floored to 12; 12 x 816 = 9,792. Sanity bound: the "to close" label has exactly one
independent outcome per day whatever the decision grid, so 816 is a hard ceiling for any session-close
label over the whole window. In a 60% discovery fold that is about 490.

Per-fold arithmetic (fold shares are M5a's and the lead's choice; 60/20/20 is illustration only):

| h | day labels, 60% train | 20% validation | 20% test-in-discovery |
|---|---|---|---|
| 15 | 9,302 | 3,101 | 3,101 |
| 60 | 1,958 | 653 | 653 |
| 240 | 490 | 163 | 163 |

At h = 60, a 653-label validation block detects only IC >= 3 / sqrt(653) = 0.117. That is a large
correlation for a minutes-scale return forecast (Chinco et al.'s 1.2 percentage-point R² gain corresponds,
roughly and only if the added forecast is orthogonal to the benchmark, to an incremental correlation of about
sqrt(0.012) = 0.11 at 1 minute in equities, the strongest result found).
Validation blocks at long horizons cannot rank models with any precision. That favours few, frozen
configurations over a searched grid.

### e.4 Parameter-to-sample ratios per family (q = k / n, n = 60% training fold of day-session labels)
| Family, illustrative size | k | q at 15 min (n = 9,302) | q at 60 min (n = 1,958) | q at 240 min (n = 490) |
|---|---|---|---|---|
| Logistic / elastic net, 30 features | 31 | 0.0033 | 0.016 | 0.063 |
| Logistic, 60 features | 61 | 0.0066 | 0.031 | 0.12 |
| LightGBM depth 3, 300 trees (leaf values, unshrunk) | 2,400 | 0.26 | 1.23 | 4.9 |
| LightGBM depth 3, 100 trees | 800 | 0.086 | 0.41 | 1.6 |
| RLS, 30 features, lambda = 0.999 (per-window count: about 67 labels at 15 min) | 30 | 0.45 within the window | n/a | n/a |
| Markov-switching regression, K = 2, 30 features (2 x 31 + 2 variances + 2 transitions) | 66 | 0.0071 | 0.034 | 0.13 |
| TCN probe | 38,081 | 4.1 | 19.4 | 77.7 |
| DeepLOB (paper) | 60,947 | 6.6 | 31.1 | 124.4 |
| Tiny transformer probe | 110,209 | 11.8 | 56.3 | 224.9 |

Check one cell: 2,400 / 1,958 = 1.226. A rule of thumb from regression practice (my addition, not sourced:
about 10 or more independent observations per free parameter, so q <= 0.1) admits the linear and
Markov-switching families at every horizon up to 60 minutes, shallow GBM with about 100 or fewer trees at
15 minutes, and no sequence model at any horizon where the cost hurdle can be met. Overnight labels add
2.6 times as many windows but at 17% of the volume, so they are worth fewer than their count. Whether to
pool them is a lead decision.

### e.5 Data it needs
The calendar, the session clock and the exclusion list. No market data. The real D and the real exclusions
come from DataFacts and the frozen protocol.

### e.6 Leakage and look-ahead traps
- *Counting rows as observations in a t-statistic.* Using 236,640 rows for a 15-minute label inflates t by
  about sqrt(15) = 3.9. **Test:** recompute the statistic on non-overlapping labels only (one decision time
  per window), or with Newey-West lags >= h - 1 (M5a). The two must agree to within sampling error.
- *Overlap across fold boundaries.* Handled by purge and embargo (M5a). **Test:** the interval-intersection
  assertion in (b) and (c).

### e.7 Compute
Calendar arithmetic only (`M4_ess.py`, under a second).

### e.8 Verdict: **use** (mandatory)
Every model and test in E.33 should state its n_eff per horizon and its q. Report n_eff from non-overlapping
labels and, once measured, the design effect.

## (f) Compute per family on the ThinkPad for a fixed, finite grid

### f.1 Core idea
Every family fits on the laptop. What scales the cost is configurations x outer folds x seeds, and (for
networks) epochs. V43 counts every configuration into N, so the grid size is fixed by the trial budget long
before it is fixed by compute.

### f.2 Equations
Total time T = (configurations) x (outer folds) x (seeds) x (time per fit). Time per fit is about rows x
(passes or rounds) / throughput, linear in rows for every family here.

### f.3 Worked example: measured per-fit times and an illustrative grid (grid sizes are illustrations for the lead, not proposals)
Assumptions: 30 features, float32; rows = 860,880 one-minute decision points (both sessions, 39 months) or
236,640 (day session only), or 5,165,280 ten-second points (both sessions); 5 outer folds; nice 10; 8 CPU
threads (within the 14-thread overnight cap); one GPU job at a time. Measured on synthetic data
(`M4_compute_probe.out`, 2026-10-27 00:40-00:44 PDT) unless marked E.28.

| Family | Per-fit time, measured | Illustrative grid | Fits | Total | Memory peak | GPU |
|---|---|---|---|---|---|---|
| L2 logistic | 0.16 s at 1M rows | 10 lambdas x 2 feature sets | 100 | < 1 min | ~0.2 GB | no |
| Elastic-net logistic (saga) | 10.6 s at 1M rows | 10 lambdas x 3 alphas x 2 sets | 300 | ~53 min (a warm-started path is much less) | ~0.2 GB | no |
| LightGBM depth 3, 500 rounds | 26 s at 1M; 91 s at 5M | 3 eta x 2 min_leaf x 2 sets | 60 | 26 min (1-min rows); 91 min (10-s rows) | ~0.8 GB at 5M | no |
| RLS / Kalman TVP, p = 30 | 1.64 s per 200k steps, so ~7 s per 860,880 | 3 lambdas x 2 sets | 30 | ~4 min | < 0.1 GB | no |
| Online logistic (OGD/FTRL) | below RLS (O(p) vs O(p^2) per step; not timed) | 3 rates x 2 sets | 30 | < 4 min | < 0.1 GB | no |
| Markov-switching / HMM, K = 2 | E.28: 27.3 s per 10 EM iterations at 200k steps, ~4.5 min at 1.87M | 2 feature sets x 5 fixed starts | 50 | ~2 h at 860,880 rows (50 x ~2.1 min) | few hundred MB | no |
| TCN (38k params), 40 epochs | 18,018 samples/s, so 13 s/epoch (day 1-min) or 287 s/epoch (10-s, both) | 4 configs x 5 seeds | 100 | 15 h (day 1-min rows) or 318 h (10-s rows) | 165 MiB GPU | yes |
| Tiny transformer (110k), 40 epochs | 4,466 samples/s, so 53 s/epoch (day 1-min) | 4 configs x 5 seeds | 100 | 59 h (day 1-min rows) | 365 MiB GPU | yes |
| DeepLOB paper (61k) | E.28: 5,247 samples/s at batch 256 | (not recommended) | | E.28: 8.5-34 h per configuration on event rows | 577 MiB at batch 256 (E.28) | yes |

Arithmetic checks: TCN 100 fits x 40 epochs x 13.13 s = 52,520 s = 14.6 h. With 10-second rows, 100 x 40 x
286.7 s = 1,146,800 s = 318.6 h. Transformer 100 x 40 x 52.99 s = 211,960 s = 58.9 h. LightGBM 60 x 26.3 s =
1,578 s = 26.3 min. Markov switching: 4.5 min for 1.87M steps scales to 4.5 x 0.8609 / 1.87 = 2.07 min at
860,880 steps, and 50 fits x 2.07 = 104 min (about 1.7 h, rounded up to ~2 h for the regression solves).

### f.4 Data it needs
The feature table built once per frozen configuration and stored by trade date in shards (C4.4: "LightGBM on
event-sampled rows from a year of one contract fits in memory if features are built by trade date in shards
and written to disk"). At 860,880 x 30 float32 = 103 MB, the 1-minute table fits in RAM whole. The 10-second
table at 5.17M x 30 x 4 = 620 MB also fits.

### f.5 Leakage traps
None specific to compute. One practical trap: a non-deterministic fit (LightGBM threads, cuDNN) gives
different models on rerun, so a result cannot be re-derived for verification. **Test:** run each frozen
configuration twice. LightGBM: "setting this to true should ensure the stable results when using the same
data and the same parameters (and different num_threads)" (`deterministic`, `lightgbm_parameters.html`).
For torch, set deterministic algorithms and fixed seeds, and compare two runs' predictions.

### f.6 Compute caveats
The probe used random features with a weak planted logit (0.05 x1 - 0.03 x2). Real features with heavy
tails and many ties change LightGBM's binning slightly but not its order of time. Early stopping usually
stops well before 500 rounds on a weak signal, so the LightGBM figures are upper bounds per fit. Saga's
convergence time depends on conditioning and may be longer on correlated real features.

### f.7 Verdict
Compute does not constrain any recommended family (linear, shallow GBM, RLS/TVP): a full illustrative grid of
all three takes under 2 hours of CPU. Sequence models are feasible on the RTX 3050 at 1-minute sampling
(hours to days) but not with seeds at 10-second sampling (hundreds of GPU-hours). They are excluded by (c) and
(e), not by compute.

### f.8 Evidence
Measured: `work/M4_models/M4_compute_probe.out` (raw JSON line), script `M4_compute_probe.py`. E.28 figures:
E.28 2.8 section 10.1, E.28 2.5 sections 1.7 and 4.7, E.28 C4.4.

## Summary of verdicts (recommendations to the lead; the lead decides)

| Family | Verdict | One-line reason |
|---|---|---|
| (a) Regularised logistic / linear (L2, elastic net) + Platt check | **use (primary)** | q <= 0.03 at 15-60 min; calibrated by construction; the strongest minute-scale evidence (Chinco et al.) is LASSO; trees and nets add little over LASSO at high frequency (Aït-Sahalia et al. via E.28) |
| (a) Isotonic calibration | **skip** at h >= 60 min | calibration blocks hold < 1,000 independent labels; Platt is better there (Niculescu-Mizil & Caruana) |
| (b) LightGBM depth <= 3, <= ~100-300 trees, early stopping inside a purged inner block, Platt-calibrated | **maybe (one or two declared secondary configurations)** | captures session x state interactions; q 0.09-1.2 at 15-60 min; needs calibration and early-stopping discipline |
| (b) Monotone constraints | **use only where the sign restates a declared hypothesis**; otherwise skip | few minutes-ahead ZM signs are economically fixed; the method choice (basic/intermediate/advanced) is itself a configuration |
| (c) DeepLOB, TCN, small transformers | **skip** | 2-34 weights per independent label at the horizons that can pay costs; published gains are at seconds-scale event horizons; linear baselines match them |
| (d) Online logistic / RLS / Kalman TVP with a fixed forgetting factor | **maybe (one declared wrapper of the primary model)** | cheap answer to the expected regime break; label-delay rule (Raftery eq. 9) mandatory; short windows mean noisy weights |
| (d) Markov-switching regression as a direction model | **skip** | regime forecasts fail on regime misclassification (E.28 2.5); a volatility gate stays E.28's "maybe" as a filter |
| (e) Non-overlapping-label n_eff and q reporting | **use (mandatory)** | rows overstate evidence by about h/Delta |
| (f) Compute | not binding for any recommended family | all three recommended families: under 2 CPU-hours for an illustrative grid |

## Planner pointers owned by M4 (reports/stage_e32_inputs/planner_research_soy_complex.md)

| # | Planner claim (line) | Status | Evidence and what differs |
|---|---|---|---|
| 1 | "Briola et al. (QF 2025) found deep LOB models help only for very active stocks" (lines 79-80) | **PARTLY VERIFIED** | Publication verified: Crossref gives "Deep limit order book forecasting: a microstructural guide", Quantitative Finance 25(7), 1101-1131, published 2025-07-03 (`crossref_briola_qf2025.json`); full text read from arXiv 2403.09267v4 (E.28 file, sha256 1642bd28...). The finding is about **tick size, not trading activity**: "we find that large-tick stocks are easier to predict, they are overall characterized by a stronger prediction signal, and their forecast performance is robust across prediction horizons", and "the observed behavioural clusters can ultimately be entirely traced back to tick-size-driven effects". All 15 stocks were "liquid" NASDAQ names. Activity enters only through how fast 10-100 updates happen in physical time (their Table 7), and the paper adds that "the utility of this signal is significantly dependent on the presence of low-latency hardware infrastructures" and that "high forecasting power does not necessarily correspond to actionable trading signals". The paper does not say "only for very active stocks". |
| 1b | "ZM is in the sparse regime" (line 80-81, same bullet) | **UNVERIFIED, possibly inverted** | Briola's "sparse LOB structure with empty levels" describes **small-tick** stocks ("This means that the corresponding stocks are characterized by a sparse LOB structure with empty levels"). A contract whose average spread is under about 1.5 ticks is large-tick in their classification ("if (ii) ⟨σ⟩ ≲ 1.5θ, we are dealing with a large-tick stock", E.28 2.8 section 4.3), and large-tick books were the MORE predictable class. ZM's average spread is not measured in anything I may read (no new statistic from data), so its class is open. The planner's conclusion (no deep models for minutes-to-hours labels) still holds, for a different reason: Briola's predictability is at 10-100 book updates (seconds), not minutes, and the sample arithmetic in (c) and (e) rules deep models out. |
| 2 | "no credible grain LOB ML study exists" (line 79) | **NOT REFUTED (absence after search; not proof)** | Searched: arXiv API 2 queries (`arxiv_q1_lob_grain.xml`, `arxiv_q2_commodity_lob_ml.xml`: 7 hits, none on grains); OpenAlex 4 queries (`openalex_oa1-4.json`, top 25 each); WebSearch 3 queries (results in this file's log section). The last three discovery queries surfaced nothing new, which meets the stopping rule. Closest items, none of them a credible grain LOB ML direction study: (i) "Evaluating the Effectiveness of Optimized LSTM and XGBoost Classifiers in High-Frequency Futures Market Prediction" (IGI Global book chapter, 2025, DOI 10.4018/979-8-3693-8186-1.ch014). The abstract (OpenAlex) covers five Chinese futures markets, including soybean, with "backtesting profits", and says XGBoost "demonstrates better stability and efficiency in more stable markets like Soybean and Rebar Futures". Abstract only [unverified]; data granularity and cost model unstated; an edited book chapter, not peer-reviewed journal work. (ii) Jin, Kearney, Li, Yang, "Order book price impact in the Chinese soybean futures market" (IJFE 2020, DOI 10.1002/ijfe.2439): statistical OFI, not ML; known from a search snippet only [unverified]. (iii) "Microstructure and high-frequency price discovery in the soybean complex" (J. Commodity Markets 2023, DOI 10.1016/j.jcomm.2023.100314): cointegration theory and empirics, not ML (abstract from OpenAlex). (iv) Daily or longer grain price forecasting with LSTM and XGBoost (Agricultural Economics 2024; JFM 2023, 22 commodities, monthly LightGBM; SJSU price-level LSTM). Wrong horizon, not LOB. |
| 3 | "Models: regularised linear or logistic, and shallow GBM (depth up to 3, monotone constraints where the sign is economically fixed). No deep LOB models." (lines 126-128) | **VERIFIED, with four qualifications** | Supported by the sample arithmetic (e.4: q <= 0.03 for linear, 0.09-1.2 for depth-3 GBM, 4-225 for sequence models at 15-240 min) and by the evidence in (a)-(c). Qualifications: (1) the probabilities must be calibrated (Platt on a separate block), because the trade rule is a probability threshold (section 0, a.3 item 3); (2) in LightGBM, state num_leaves <= 8 with max_depth 3 explicitly, and set min_data_in_leaf in independent-label units (b.3 item 1); (3) early stopping only on a purged inner block (b.5); (4) for minutes-ahead ZM direction very few signs are economically fixed, so monotone constraints apply only to features whose sign restates a declared hypothesis, and the constraint method is a counted choice. |

## Gaps, failures and limits

- Not fetched: Tibshirani (1996) and Zou and Hastie (2005) originals. statweb.stanford.edu returned nothing to
  curl, and hastie.su.domains returned an anti-robot validation page (HTTP 403). An anti-bot page signals
  that automated access is not wanted, so Scrapling was not used there. The elastic-net and logistic
  equations are quoted from Friedman, Hastie and Tibshirani (2010, PMC copy) instead.
- Not fetched: Dangl and Halling (2012); Kolm and Westray, "Deep learning alpha signals from limit order
  books" (risk.net, paywalled; pointer only); Jin et al. (2020) full text; the IGI chapter full text.
- Not measured: ZM's average spread (it decides Briola's tick-size class, row 1b); the intra-day correlation
  rho of labels (design effect, e.2); online-logistic timing; statsmodels MarkovRegression timing
  (statsmodels is not installed; the E.28 numpy HMM timing is used).
- The trade-date count D = 816 rests on an assumed holiday list. DataFacts owns the real count.
- WebSearch calls used: 6 of 80. No budget notice was seen. Cost-notice hooks appeared; they are informational
  and did not affect the work.
- The compute probe used synthetic random data only. It is a timing measurement, not a result about ZM.

## Fetch log summary
All pages are listed with UTC and PDT times and sha256 in `pages/M4_models/log.tsv`. WebSearch queries (for
the record): (1) '"limit order book" soybean OR corn OR wheat futures deep learning mid-price prediction'; (2)
'Dalian commodity exchange soybean meal high-frequency order book machine learning prediction tick data';
(3) 'CBOT soybean OR corn futures intraday high-frequency direction prediction machine learning LightGBM OR
LSTM order flow'; (4) Raftery DMA PDF lookup; (5) RLS forgetting-factor notes lookup; (6) Chinco et al. PDF
lookup.

Completed 2026-10-27 00:51 PDT (all sections (a)-(f), the verdict summary and the planner table written).
