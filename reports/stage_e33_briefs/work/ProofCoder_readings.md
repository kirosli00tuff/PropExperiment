# ProofCoder readings (Stage E.33 B5: select33, synth33, run_proofs33)

Protocol: reports/stage_e32_discovery_protocol.md (cited P<n>). Code: reports/stage_e33_briefs/work/pipeline/
select33.py (`# READING Q<n>`), synth33.py (READING P-*), run_proofs33.py. Each entry: protocol line, readings
considered, choice, why conservative. The lead decides each before the freeze. Generator entries (P-*) are design
choices of the synthetic world, logged for review; they touch no real outcome.

## Selection rule (select33.py, P8)

### Q3 Tier B start point (outcome-relevant when Tier A is non-empty)
- P8: "Tier B ...: continue the Tier A walk over all 300 configurations ordered by the same key, gates ignored,
  taking the next two whose OOF daily series has correlation <= 0.70 with every configuration already taken".
- Readings: (continue) walk the all-configuration order from the position after the last configuration the Tier A
  walk examined (the third member taken, or the last passing configuration when fewer than 3 were taken);
  (restart) walk the all-configuration order from the top, skipping the taken ones.
- Choice: continue (default; `--tier-b-reading restart` available). Both are computed and written to
  selection output (`tier_b_detail`), so the lead sees both outcomes.
- Why conservative: "continue" is the literal sense of continuing a walk, and it picks companions ranked below the
  Tier A members, whose Sharpes are lower; under V14 (c) as coded the program verdict's SR0 = 3.2045 x the population
  SD of the tested Sharpes (P7.2), so lower-ranked companions widen that SD and make the DSR check harder to pass.
  "Restart" can pull in a configuration that ranks above the Tier A member but failed a gate (for example G1),
  a closer companion and an easier verdict. (The PBO check with 2-3 strategies moves the other way, but it is the
  coarser of the two.) A test (test_tier_b_readings_differ_on_a_high_ranked_gate_failure) shows a case where they
  differ.

### Q2 Mean net per trade (G2)
- P8 G2: "mean net per trade >= 0.50 tick"; P6.2 "mean net per trade".
- Readings: sum of the trades' nets / trade count; sum of the daily values X_D / trade count.
- Choice: math.fsum(X_D) / trade count (X_D is the sum of the nets of the trades entered on D, P3.8). The two
  differ only by float rounding (1e-15); load_root cross-checks daily.parquet against stats.json.
- Why conservative: no outcome difference except at an exact tie at 1e-15; fsum makes the sum correctly rounded.

### Q1 G1 comparisons
- P8 G1: "at least 1.0 trade per OOF date on average (at least 796 trades) and a trade on at least 50% of the OOF
  dates". Choice: integer comparisons count >= 1.0 x T and dates_with_trade >= 0.5 x T (398 of 796 passes).
  Not ambiguous; logged because 50% of 796 is a whole number (398 passes, 397 fails; tested).

### Q4 G4 with an undefined standard error
- P8 G4: se(SR_d) = sqrt((1 - g3 SR_d + (g4 - 1)/4 SR_d^2)/(T_disc - 1)).
- Readings: a non-positive radicand (a) fails G4; (b) is clamped as p7_final.se_sharpe does (max(1e-12, .)),
  which makes se about 3.5e-8 and can pass G4.
- Choice: (a) fails G4. Why conservative: an undefined se cannot show power. Such a configuration also fails G3
  (deflated_sharpe_ratio raises on the same radicand), so the pass set does not depend on this reading.

### Q5 G5 (c) undefined t
- P8 G5 (c): the daily t of the series without each month >= 2.5 (t_stat() population SD).
- Choice: a month whose removal leaves SD 0 (t_stat returns None) fails (c). Why conservative: an undefined t is
  not >= 2.5. Only constant series reach it, and they fail G1-G4 anyway.

### Q6 Undefined correlation in a walk
- P8 Tier A / Tier B: "correlation <= 0.70 with every configuration already taken".
- Choice: an undefined Pearson correlation (a constant series) never qualifies in the walk. In Tier A it cannot
  arise (G3 needs SD > 0); in Tier B constant series are skipped by P8's own text; the fill reports None.

### Q7 One-sided p-values for the BH and Holm reports (never gates)
- Brief / prompt D1: "BH FDR and Holm on one-sided p-values from the daily t (state the reading)".
- Choice: p = 1 - Phi(t) with t from t_stat() (normal reference; with 795 degrees of freedom Student t differs in the
  4th decimal); a configuration with no t (failed, constant) enters with p = 1 and counts in m. BH at q = 0.05
  (largest k with p_(k) <= k q / m), Holm step-down at 0.05. Reports only.

### Q8 Discovery PBO set (report)
- P6.3: CSCV PBO over the 300 OOF series with screening.stage_e_verdict.pbo.
- Choice: every configuration with a series (constant series included); failed configurations have no series and
  are left out (the count is reported).

### Q9 "Best configuration" in the proof summary
- P4.2: "the realised OOF Sharpe of the best planted configuration per seed beside the oracle"; brief: "the best
  configuration's SR_d".
- Choice: the first configuration in P8's total order over the configurations with a non-constant series, gates
  ignored (the highest SR_d rounded to 4 decimals, then the tie-breaks); None if every series is constant or failed.
  A no-trade series (SR_d 0 by the moments() convention) is never the best: it would hide the null's maximum.
  Report only; the gates, ranking and walks do not use it. (Changed 02:37 after a reduced null run showed a
  no-trade configuration as "best".)

### Q10 SD of the 400 null daily Sharpes
- P4.2: "the SD of the 400 null daily Sharpes (20 configurations x 20 seeds, each centred on its configuration's
  mean)".
- Choice: population SD of the 400 centred values, a constant (no-trade) series counting as Sharpe 0 (moments()
  convention); reported a second time over non-constant series only, centred on their own configuration means.

### Q11 Funnel of failed configurations
- P8: "A failed configuration (P5) fails G1"; "the count passing each gate alone".
- Choice: a failed configuration has no series, so it fails every gate alone as well (no gate can be evaluated).

## Generator (synth33.py, P4.2 "Search proofs")

### P-L Latency at minute resolution
- P4.2 asks for minute rows; P3.2-P3.4 use u + L. Choice: the synthetic latent price is sampled at three points per
  minute: A_j = t_j (features, sigma_ZM, entry rules), B_j = t_j + L (entry fills at t + L, FH exits at t + h + L,
  TB barrier checks), C_j = t_j + 2L (TB exits at tau + L). Increments A->B and B->C carry 1/60 of a minute's
  variance and drift, C->A(next) the other 58/60. Next decision after an exit = the first grid minute at or after the
  exit fill (FH: t_{i+h+1}; TB: t_{j+1}).

### P-TB Barrier monitoring
- P3.4 steps through every book update in (t + L, t + L + h]. Choice: the synthetic book's updates for barrier
  purposes are B_j, j = i+1..i+h (discrete monitoring once a minute), comparison 2(M - m0) vs 2b exactly as lab33
  (integer mid sums against a float). Consequence: fewer barrier hits than continuous monitoring (T30 class shares
  about 0.29 / 0.42 / 0.29). b = sigma_ZM(D) sqrt(h) with the synthetic sigma_ZM(D) of the _day json.

### P-SPREAD Touch and spread
- Brief: "a 1-tick spread most of the time". Choice: 2-tick touches with probability 0.10, i.i.d. per sample point;
  1 tick: bid = floor(X); 2 ticks: bid = round(X) - 1. Independence keeps C_3 (the spread at t) free of
  information about the entry cost at t + L, so the null carries no cost signal either.

### P-VOL Volatility
- Brief: "sigma_1m about 3.15 ticks with day-to-day variation". Choice: log sigma_D AR(1) across dates (persistence
  0.90, stationary SD 0.20), mean set so that E[sigma_D^2] + 1/6 (two uniform rounding errors) = 3.15^2. Realised
  mean sigma_ZM(D) over OOF dates 3.10-3.14 across draws (Jensen; tested within 2.9-3.3). Constant within a date.
  sigma_ZM(D) = population SD of the pooled 1-minute mid changes 08:35-13:13 of the 20 previous dates; null
  (undefined) on the 20 burn-in dates.

### P-PLANT The plant
- Brief: "one F3 feature (name it) shifts the drift of the next minutes". Choice: F3_4 (IOFI5), a unit-variance
  Gaussian AR(1) over minutes with phi = exp(-1/5) in every seed (null too); the latent drift over minute
  (t_j, t_j+1] is beta x F3_4(t_j). Null beta = 0; planted beta = 0.367 ticks per minute per unit. Markov plant:
  given F3_4(t), the rest of the information set adds nothing about the future drift, so the oracle depends on
  F3_4(t) and sigma_D only. In planted seeds the past path drifts, so the F4 path features (and F2_7, which
  contains rZ_5) carry derived momentum information; the only source is the plant.

### P-ORACLE Oracle and calibration
- P4.2: "the oracle strategy (the P3.5 rule applied with the generator's true class probabilities, with the P3.8
  costs and the dead zone) has a daily Sharpe of 0.35 net ... at FH15"; brief: "expected over draws".
- Choice: true p_+1, p_-1 of the FH15 label given F3_4(t_i) and the true sigma_D in closed form: the move
  X(B_{i+h}) - X(B_i) is N(beta g z, sigma_D^2 h + beta^2 v_z) (g, v_z from the AR(1)), the fractional part of
  X(B_i) uniform, entry and exit spreads independent; the integral over the fractional part uses the antiderivative
  of Phi (exact). Verified by Monte Carlo (tests) and by binned empirical class shares. Class-conditional means:
  P3.7-weighted means of N_long, N_short by class over all rows of the seed's 796-date series. P3.8 simulation
  (cap 20, one position, exits as labelled) on the seed's own series; X_D = 0 on excluded dates.
- Calibration (synth33.calibrate, 2026-10-27 15:24-15:28 PDT, 262 s): bisection on beta over 60 draws (seeds
  70001-70060, common random numbers across beta), tolerance 5e-4 in beta, then beta rounded to 0.367: mean oracle
  SR 0.3498 (se 0.0048, SD across draws 0.037); independent check on 60 fresh draws (80001-80060): 0.3486 (se
  0.0045). dSR/dbeta about 1.0, so the bisection tolerance moves SR by about 5e-4. Output:
  reports/stage_e33_briefs/work/ProofCoder_calibration.json. No T30 oracle is computed (the protocol defines the
  oracle at FH15; the same plant serves T30).

### P-NULL Exactness of the null
- With beta = 0 every non-F4 feature is independent of the path; F4 features use only the past mids of a
  driftless walk. The only residual is discretisation: given the past mids, the fractional part of X(t + L) is not
  exactly uniform (deviation of order 1/sigma^2), worth well under 0.01 tick against a round-trip cost of about
  1.6 ticks. Logged, not removed.

### P-RULES Exclusions on the synthetic book
- Rules 1-4 come from the real calendar (grid G_h(D), cal33.excluded, cal33.releases, closed-interval test as
  lab33). Rule 5 (locked book, price limits) and rule 6 (ZS/ZL invalid) cannot arise: the synthetic book always has
  both sides, no limits and no ZS/ZL book. Hence row_ok = entry_ok, P3.2 fallbacks never fire, flags are 0.
  mid_move = M(t + L + h) - M(t + L) (TB: vertical h), NaN on excluded dates (production builds no book there).

### P-FEATURES Non-plant features
- C_1, C_2, C_8, C_9, C_10, C_15 from the clock and the real calendar; C_3 = synthetic spread at t; C_6 = log
  sigma_ZM(D); C_7 a proxy (trade dates to the next ZM roll + 10, capped at 60, / 60; READING P-C7: definitions are
  not read); C_11-C_14 validity flags all 1 (READING P-FLAGS; constant columns, zeroed by the engine for LOGIT).
  F1, F2 (except F2_7) and F3 (except F3_4) are noise with feature-like persistence: AR(1) or overlapping window
  sums of i.i.d. innovations, tanh-bounded where the protocol's feature is bounded, Poisson counts for sweeps and
  refills. F4 per the P4 definitions on the synthetic minute mids. P4 G4 clipping applied to the 38 listed columns.

### P-SEED9000 Probe table
- Brief deliverable 4. Choice: seed 9000 written as a null seed (closest to what real data are expected to look
  like for fit time), full size, under DERIVED/proofs/seed9000/.

## Runner (run_proofs33.py)

- Order: seeds 1-20 then 101-120, one search at a time (run_search33 holds the P5 thread cap: processes x threads
  <= 8). Thresholds at N = 838 (P4.2). Every fold model is kept (seed 1's are required by LT7).
- Exactly once per pipeline hash: <proofs-dir>/run_manifest.json pins the sha256 of synth33, select33,
  run_proofs33, search33, run_search33, cal33, data33, guard33, p7_final and p7_thresholds; a restart with other
  code stops. A rerun after a logged fix goes to a new --proofs-dir. Production seeds run only as the full set of 40
  (unless --allow-partial), never mixed with test seeds, at full size and N 838.
- The summary states the P4.2 criteria next to the counts; it draws no verdict.

## Test runs (non-production seeds only; times PDT from the logs)

- Unit tests: tests/test_select33.py 27 passed, tests/test_synth33.py 15 passed, tests/test_run_proofs33.py 8 passed
  (2026-10-28 02:05-02:15).
- Reduced end-to-end (seed 9002, planted, 120 OOF dates, --max-procs 4; DERIVED/proofs_test/e2e/): generation,
  20 configurations / 120 fits through run_search33, select33 (not strict) and the summary, 02:03:54-02:06:24.
  Tier A empty (G3 and G5 cannot pass on 120 dates); best E33-S5F15L010E SR_d 0.248; oracle 0.395.
- Full size (seed 9101, planted; DERIVED/proofs_test/full/): run with 8 processes 02:07:31, stopped by me at about
  02:09:50 on the lead's instruction (feature builds were running; available memory 4.3 GB). Finished configurations:
  E33-S5F15L001A SR_d 0.336 (10.1 trades a date, 1.31 ticks a trade, t 9.48), E33-S5F15L001E SR_d 0.417 (8.8, 1.72,
  t 11.77); this seed's oracle 0.369 (10.7 trades a date, 1.31 a trade). A fitted model can exceed the P3.5 oracle:
  P3.5 is not Bayes-optimal (within-class means do not depend on x), so the oracle is a calibration anchor, not a
  ceiling. LOGIT fold times under that load: C 0.01 about 14 s, C 0.1 30-50 s.
- Fold-6 probe, one process (02:10-02:12, seed 9101): E33-S5F15L100E 23.4 s (46 iterations), E33-S5F15G3050 12.0 s
  (4 threads, best iteration 76), E33-S5T30L100E 41.2 s (96 iterations), E33-S5T30G3050 15.9 s (best 168).
- Projection for the 40 searches (a guess, not a measured run): per seed 72 LOGIT fits (about 15-45 s each
  uncontended, 1.5-2x slower with 8 concurrent processes) / 8 processes plus 48 LGBM fits (12-16 s) / 2 processes:
  about 13-20 minutes a seed, so about 9-13 hours for the 40 at --max-procs 8 (longer while other jobs share the
  machine).

## Changes after ProofReview (2026-10-28 02:32-02:40 PDT)

- SF1: the summary shows per seed "failed fits: k" and, per section, the failed configurations with their failed
  folds (stats.json errors). Counting rule, stated in the summary: a seed with any failed configuration is never a
  clean empty Tier A; null: it counts against the proof together with the seeds whose Tier A is non-empty
  (criterion at 2 or more on the union); planted: it does not count toward the pass count even with Tier A
  non-empty. Both raw counts are printed. Why conservative: a failed fit can only make the null look cleaner and the
  planted pass count is never raised by an incomplete search.
- SF2: the run manifest pins run_search33.versions() (python, numpy, scikit-learn, lightgbm, pandas, pyarrow,
  scipy, uv.lock sha256) and search33.PIPELINE_SHA; a resume with any of them different refuses.
- Code hashes now cover every pipeline/ module the proof entry points import, transitively (the AST walk of
  search33.pipeline_files from run_proofs33, synth33, select33, search33, run_search33), plus p7_final.py and
  p7_thresholds.py.
- Notes applied: N1 and N3 (summary sentences on derived F4 signal and on the oracle as an anchor), N2 (df-corrected
  SD printed beside the raw one; reference 0.0345 for the centred SD), N6 (the summary prints the sha256 of the
  run_proofs33.py that wrote it and flags a difference from the manifest), N8 (look-ahead test also perturbs the B
  and C points of minute i0, the plant latent and the spreads after i0), N9 (short-side nets and exits checked
  against independent arithmetic, FH and TB), N11 (the summary prints the manifest's starts).
- Notes not applied (no code change): N4 (minute barrier monitoring; logged as P-TB), N5 (Tier B fill accepts a
  constant series, the literal "defined series"; one `or r["constant"]` if the lead reads it otherwise), N7
  (evidence only), N10 (feasibility, the lead's call).
- Reduced end-to-end run after the 02:24 engine change: seed 9003 (null, 60 dates, 4 processes), 02:34:30-02:35:13,
  rc 0, 20/20 configurations DONE, 0 failed, summary rendered.
