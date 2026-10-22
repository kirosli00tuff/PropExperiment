# C4 (lead draft): the recommended method set and a draft design for the order-book ML search under V43

Draft by the lead, 2026-10-21 05:13 PDT, from the C2 verdict tables (C2_SDE section 9, C2_Hawkes 12, C2_LOB 13,
C2_Control 11, C2_DeepLOB 12, C2_OFI 13, C2_Pooled 9, C2_Filter 9, C2_Firms 3-4, C2_AFML 13, C2_StatsRMT 16). This is a design draft, not a pre-registration: no grid, threshold or selection rule here is frozen,
and nothing here changes N. The stage that runs the search writes its own declaration, hashes it before any
outcome read, and has it adversarially reviewed.

## C4.1 What the deep dives agree on

Eleven readers worked independently, and their verdicts converge on five points.

1. **No method in the brief is a source of edge on its own at retail latency.** No reader found an out-of-sample,
   cost-inclusive result for a slow 1-lot passive or taker strategy on a large-tick futures book. The order-book
   ML literature reports accuracy, not net profit, and accuracy overstates value (C2_DeepLOB section 12: "the
   deep-model literature gives no evidence that any of these models earns money after costs at retail latency on
   any market"). Avellaneda-Stoikov has a negative cost-inclusive test (C2_Control section 11). Plain Hawkes
   direction forecasts lose to "same as last" out of sample (C2_Hawkes section 12).
2. **The first question is the economics of a passive fill, and it is a measurement.** The queue-position value
   identity is the decision framework: the value of a resting 1-lot = P(fill) x (half-spread - expected adverse
   move after a fill) - fee (C2_LOB section 13, after Moallemi-Yuan, Dahlstrom et al. and the Bouchaud et al.
   markout identity). Every model agrees that a slow order at the back of a FIFO queue on a large-tick contract is
   filled disproportionately on adverse paths. The pilot's markouts measure that term directly.
3. **The useful methods are measurement and conditioning tools.** Survival analysis with censoring for fill rates;
   markouts at fixed horizons; realized variance for the volatility state; seasonal Poisson and low-dimensional
   Hawkes intensities; queue imbalance and depth-normalized order-flow imbalance (OFI) as the conditioning
   variables; a hidden-Markov "do not post" gate. Their job is to tell a passive order when not to rest, not to
   predict direction.
4. **Simple first, and every rung counts.** Queue imbalance and level-1 OFI are the most robust features in the
   literature and the cheapest. Trees add little over linear models at high frequency (C2_OFI section 13). Deep
   models must beat simple baselines in independent replications before they earn a test (C2_DeepLOB section 12:
   "MLPLOB / MLP baseline ... Matches or beats deep models in three independent studies").
5. **Latency decides the horizon.** Much published predictability lives below 100 ms (C2_OFI: deep OFI's effective
   horizon is "milliseconds to half a second"; C2_Hawkes: excitation at about 0.3 ms). The only feature with
   published evidence of keeping most of its value at 100 ms in an execution use is queue imbalance (C2_OFI
   section 13, Stoikov-Waeber). Every feature in the search is lagged by a declared latency of at least 100 ms.

## C4.2 The recommended method set

| Role | Methods (source section) | Why |
|---|---|---|
| Fill measurement | Kaplan-Meier fill curves with censoring, and a generalized-gamma accelerated-failure-time model for covariates (C2_LOB, Lo-MacKinlay-Zhang); diffusion touch probability set against measured fills (C2_SDE) | Correct treatment of orders cancelled or still resting at the horizon; the touch-versus-fill gap measures the queue effect with no fitted model |
| Adverse selection | Markouts at 1, 10 and 60 s against the mid, with the microprice as a second reference (C2_LOB, C2_OFI); toxic-fill share (C2_OFI H-SNIPE-1); latency decay of the conditioning signal at 100 ms (C2_OFI H-LAT-1) | These are the terms of the queue-value identity |
| Arrival intensities | Seasonal (inhomogeneous) Poisson baseline, then univariate and low-dimensional multivariate Hawkes with exponential kernels, fitted by the O(N) likelihood, checked by time rescaling (C2_Hawkes) | Without the seasonal baseline, Hawkes fits read seasonality as self-excitation (C2_Hawkes measured a regime-switching Poisson process, true branching ratio n = 0, fitted as n = 0.956) |
| Conditioning features | Queue imbalance (Gould-Bonart), level-1 OFI (Cont-Kukanov-Stoikov), integrated OFI (Cont-Cucuringu-Zhang, one frozen weight vector), the Cont-de Larrard direction probability, spread and volatility state (C2_LOB, C2_OFI) | Few, robust, depth-normalized; integrated OFI replaces a choice among ten levels and saves trials |
| Policy | The bounded-inventory quoting rule of Gueant-Lehalle-Fernandez-Tapia, which on a one-tick book reduces to "touch, cap at Q": resting at the touch with the inventory capped at Q (C2_Control section 4.5c), with imbalance gating in the style of Cartea, Donnelly and Jaimungal; at most one hidden-Markov "do not post" gate, rated maybe after review (C2_Filter, MG1-18) | The control papers give inventory discipline and a gating structure, not an edge |
| Models (ladder) | (a) no-model passive baseline; (b) single-feature gates; (c) logistic or linear markout model; (d) one frozen LightGBM configuration; (e) a small MLP or DeepLOB-sized network only if (c) or (d) show structure net of costs in cross-validation (C2_Firms section 4 step 4; C2_DeepLOB) | Each rung counts into N; a rung advances only by a margin declared in advance |
| Baselines and labels | A time-of-day baseline (the Andersen-Bollerslev flexible Fourier form, harmonics fixed by the periodogram) that every model must beat, and which stratifies the fill model; triple-barrier labels with barriers declared in advance for a post-then-exit passive order; meta-labeling only as an architecture (a fixed simple primary rule plus a learned filter), never as a search over primaries (C2_AFML section 13) | C2_AFML: the periodicity form is a "mandatory baseline"; meta-labeling's published support is thin and comes from its promoters |
| Validation | Purged k-fold by trade date with session-aligned folds and gaps of H + c tau (H the label horizon, tau the longest feature memory, c a declared constant; C2_AFML), combinatorial purged CV as a diagnostic for PBO and DSR only (its paths are correlated), DSR at N, Holm; the Harvey-Liu haircut Sharpe at N and an empirical-Bayes (James-Stein) shrunken estimate of the selected configuration's net markout as reported extras, and the Marchenko-Pastur effective N of the trial matrix as a diagnostic (C2_AFML section 13; C2_StatsRMT section 16; C2_Firms section 3.1) | V43's binding conditions; one forward hold-out decides. Shrinkage estimates how good the selected configuration really is, which the DSR and Holm only gate |
| Skipped | Wavelet denoising (two-sided, no forecasting gain) and fractional differencing beyond at most one counted feature variant (C2_AFML), Avellaneda-Stoikov as a strategy, Almgren-Chriss (nothing to schedule at 1 lot), random-matrix cleaning and nonlinear shrinkage of covariances (need many assets), Lempel-Ziv and approximate entropy (biased; at most one pre-declared entropy feature), Kalman hedge ratios and particle filters, deep OFI, TransLOB and TLOB, full-scale Sirignano-Cont, neural point processes, the branching ratio as a signal | Each has a reason in its section: no edge mechanism, failed replication, sub-millisecond horizon, or scale beyond this program |

## C4.3 A phased contract plan

**Phase 0, the pilot (this stage).** One contract, one schema, measurement only, under the spec frozen in Part B
(B2). It estimates P(fill), queue times and markouts for passive orders at the touch and one tick inside. It adds
nothing to N, because no rule is selected and nothing is tested. Its months may be reused as discovery data in
Phase 1, because they selected no model. They can never be test data.

**Decision after Phase 0 (the user's, informed by the lead).** If the measured unconditional net markout of a
passive fill (half-spread captured minus the adverse move minus fees) is far below zero in every session, and the
conditional markouts by book state show no state whose upper confidence bound reaches zero, the honest
recommendation is to stop the order-book direction before buying more data. The pilot is designed to answer
exactly that. Using it to decide whether to continue is a decision about the research programme, not a trial, but
it is recorded.

**Phase 1, one contract.** The top pair's contract only.
- Discovery data: the pilot months plus the backward extension bought today, plus, if needed, earlier months bought
  in the Phase 1 stage, all before 2024-03-01.
- A written protocol, hashed before the first fit (C2_Firms section 4 steps 1 and 2): discovery months; folds,
  purge and embargo lengths; the untouched test period; labels (the net markout of a simulated passive 1-lot fill
  under the frozen fill rule, at horizons declared in advance); the feature list with every transform; the model
  ladder and its full grid; the N rule; and a commitment to run the whole grid.
- Trial counting into N: every hypothesis-configuration pair counts, including every rung of the ladder and every
  markout horizon that is tested rather than fixed. The OFI reader's first five hypotheses add 5 to 11 trials
  (C2_OFI section 13.1); the Hawkes reader's add 8 to 13 if all six run, 7 to 12 without the skipped H-C2-4 (C2_Hawkes section 11, as corrected by MathReviewer MG2-04); with a ladder of five rungs over two
  horizons, a disciplined Phase 1 lands near N = 538 + 20 to 40. The DSR is computed at the new N with the
  variance of the trial Sharpe ratios.
- Validation: purged k-fold with folds of whole trade dates. The purge removes training observations whose label
  window (at most 60 s) overlaps a test fold, and an embargo of at least one full trade date follows each test
  fold (day-level dependence, not only label overlap). Combinatorial purged CV (for example 6 groups, 2 held out:
  15 splits, 5 backtest paths) gives PBO. The selection rule is declared in advance (for example the highest mean cross-validated
  net markout per resting order, ties to the simpler model).
- Freeze: the model, features, labels, training window, hyperparameters and code are hashed before any test
  read, as E.20's pipeline was.
- One test: the frozen model is run once on data that never selected it. The candidate period is the contract's
  research window (2024-03-01 onward) under a registered read, bought in that stage. Holm across the declared
  family, net Sharpe above the bar, DSR at N, PBO. A failure ends that model, with no retune.
- Costs: the measured fill and adverse-selection model from Phase 0, never touched-means-filled (V43), applied
  both in the real-market version and under the chosen firm's simulated fill rule, which decides what the prop
  account would actually book.

**Phase 2, pooled, only after a Phase 1 pass.** Two or three contracts that match the Phase 1 contract on tick
regime (the share of time at a one-tick spread) and on sigma in ticks, with features in unit-free form (ticks,
spreads, depth-normalized OFI). Partial pooling with a contract indicator or random-effects shrinkage is
preferred over full pooling (C2_Pooled section 9). The test is out of time and on one contract named in advance
that the pooled model never saw (the zero-shot design of C2_Pooled). Pooling very different contracts is skipped:
"Sigma in ticks differs by 4.2x (MES vs NQ)" (C2_Pooled section 9). Every pooled configuration adds to N.

## C4.4 Hardware and data

- Phase 0 and Phase 1 rungs (a) to (d) run on the laptop. The Hawkes likelihood costs about 0.71 s per million
  events in one dimension and 2.95 s in four (C2_Hawkes, measured on synthetic data). LightGBM on event-sampled
  rows from a year of one contract fits in memory if features are built by trade date in shards and written to
  disk (the CLAUDE.md compute rules).
- Rung (e): a DeepLOB-sized network has about 60k parameters and takes 8 to 34 hours per configuration on the RTX
  3050 (C2_DeepLOB section 12). More than a few configurations go to a rented GPU (USD 0.69 to 1.29 per hour on the
  Lambda price page the Hawkes reader fetched), or to the "more powerful machine" the 2026-10-18 record
  anticipates.
- Data: Phase 1 needs at least about 12 months of one schema on one contract for discovery, and a separate
  research-window purchase for the test. Level-1 features (queue imbalance, level-1 OFI, the Cont-de Larrard
  probability, microprice) need only top-of-book data. Integrated OFI and depth features need mbp-10. Exact queue
  position needs mbo. Part B's schema decision (B1) sets what Phase 1 can use without a second purchase.

## C4.5 What the user should take from C4

The methods that matter next are the plain ones: fill survival curves, markouts, queue imbalance, depth-normalized
OFI, and a small, disciplined model ladder. The sophisticated mathematics (HJB, Hawkes, queue-reactive models)
earns its place as measurement and as a policy language, not as alpha. The design's real risk is not a missing
method. It is that a slow back-of-queue order on a large-tick CME book loses its half-spread to adverse selection,
and the pilot is the cheapest way to find that out.
