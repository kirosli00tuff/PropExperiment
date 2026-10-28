# ProofReview (Stage E.33, pre-proof review of P8 selection, the synthetic generator and the proof runner)

Reviewer: ProofReviewer-FableXHigh (fresh context; wrote none of this code). 2026-10-28, started 02:18 PDT.
Status: COMPLETE (closing time in the last section). Line numbers are against the files as of 02:18 PDT.

Object: reports/stage_e33_briefs/work/pipeline/select33.py (467 lines), synth33.py (757), run_proofs33.py (299),
tests/test_select33.py (457), tests/test_synth33.py (232), tests/test_run_proofs33.py (60),
work/ProofCoder_readings.md, work/ProofCoder_calibration.json.
Standard: reports/stage_e32_discovery_protocol.md (0.3, P3.3-P3.5, P3.6-P3.8, P4.2, P6.1-P6.3, P7.2, P8, P10),
reports/stage_e32_briefs/protocol/p7_final.py (+ p7_thresholds.required_sharpe), screening/stage_e_verdict.py
(moments, t_stat, pbo), funnel/multiple_comparisons.py (deflated_sharpe_ratio, harvey_liu_zhu_verdict),
reports/stage_e33_protocol_readings.md (R-L3, R-L4), reports/stage_e33_briefs/INTERFACE.md. SearchReview.md
(search33, run_search33; 0 BLOCKING, 4 SHOULD FIX, 10 NOTE) is not repeated.

Evidence (synthetic, non-production seeds only; scratchpad scripts may not persist):
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/86e80bc3-d62a-42e1-b5fd-5c881ccf8b54/scratchpad/proofreview/
- `uv run pytest -q -p no:cacheprovider tests/test_select33.py tests/test_synth33.py tests/test_run_proofs33.py`
  at nice 10: 50 passed in 6.1 s (02:24 PDT; pytest.log).
- probe_null.py (seeds 9201 null, 9202 planted, 200 OOF dates): (1) features at minutes <= i0 are unchanged when the
  B and C sample points of minute i0 itself (t + L, t + 2L), every later point, the plant latent z after t and the
  later spreads are all perturbed: True (stronger than test_no_look_ahead_in_features, see N8). (2) Pooled Pearson
  correlation of each of the 59 features with n_long, n_short, mid_move and y on about 45,800 overlapping rows:
  null max |rho| 0.037 (F15) and 0.058 (T30), the maxima on per-date or slow features (F4_9, F1_8, F4_7, F4_6,
  C_10) whose effective sample is the 180 non-excluded dates; planted: F3_4 +0.146 (F15 n_long), +0.123 (T30),
  the next largest 0.043-0.061 on pure-noise features (F1_2, F1_7), i.e. the same noise level as the null maxima.
- A second null probe (seeds 9203-9205, inline): the pooled correlations of F4_9, F1_8, F4_7, F4_6, F3_4, F4_1
  with the F15 mid_move change sign across seeds (F4_9 +0.037, -0.011, -0.011; F1_8 -0.037, +0.012, +0.020). The
  within-date correlations of F4_9 (-0.30) and F4_6 (-0.20) are the mechanical negative bias of a within-sample
  demeaned cumulative-return regressor on a driftless walk, not information about the future path; the models
  are fitted on pooled rows, where the relation is zero.
- Real-calendar check (inline): cal33.oof_dates() gives 796 dates, 13 quarter keys (2020-12 with 40 dates, ...,
  2023-12 with 61), 39 months (2020-12 has 2 OOF dates: 12-30, 12-31; the last burn-in date is 2020-12-29);
  b_test_at(838) = 0.16488165417252623 (displayed 0.164882); p7_final.g4_threshold(b_test, 796) = 0.200703.

Severity counts: BLOCKING 0, SHOULD FIX 2, NOTE 11.

## Findings

### SHOULD FIX

SF1. A failed configuration (P5) is invisible in the proof summary B5_proofs.md.
- Where: run_proofs33.py:159-179 (_seed_rows prints Tier A, best, best SR_d, the funnel in order and alone, search
  minutes) and 213-246 (the null and planted sections). selection.json carries `funnel.failed_configs` and each
  configuration's `failed` flag (select33.py:133-137, 216-217), but neither reaches the summary.
- Protocol: P4.2 (the proof's per-seed event is "Tier A non-empty"; every run is reported); P8 ("A failed
  configuration (P5) fails G1"); brief item 3 ("a failed configuration is visible in the summary; it must not pass
  as an empty Tier A").
- Failure scenario: in a null seed k of the 20 configurations fail to fit (a LightGBM error, a class without a
  training row, two interruptions of one fold: search33 FitError / run_search33 "interrupted twice"). The row
  shows "Tier A -" and a funnel starting at 20 - k, the seed counts as a null success, and a reader of the summary
  sees a clean null proof. In a planted seed the same silently lowers the pass count. In the extreme, an engine
  defect that fails every fit passes the null proof 20 of 20.
- Fix (before launch, see N6): add a `failed` column per seed row (sel["funnel"]["failed_configs"]) and, in each
  section, a line "seeds with at least one failed configuration: n (seed: ids)" taken from the per-config `failed`
  flags; state next to the null count that a seed with a failed configuration is reported as such. Optionally make
  the null criterion line read "Tier A non-empty: n; seeds with any failed configuration: m".

SF2. The run manifest pins the pipeline files and p7_*.py but no library version or uv.lock.
- Where: run_proofs33.py:49-52 (HASHED, P7_FILES), 64-66 (code_hashes), 77-96 (check_manifest). run_search33.py:58-66
  versions() already computes the lightgbm/sklearn/numpy/pandas/pyarrow/scipy versions and the uv.lock sha256, but
  run_proofs33's manifest does not include them.
- Protocol: P4.2 "each run exactly once per pipeline hash"; R-L3 (b) lists uv.lock among the files whose change
  forces a rerun of all 40.
- Failure scenario: a `uv sync` or package upgrade between two starts of the same --proofs-dir changes LightGBM or
  scikit-learn; the resume passes check_manifest and seeds run before and after the change are reported as one
  run under one hash.
- Fix: add `run_search33.versions()` (or at least its uv_lock_sha256) to `cur` in check_manifest. One line; low
  likelihood, but it is the mechanism the protocol relies on.

### NOTE

N1. Under the plant, features derived from the past path carry a weak derived signal (synth33.py:296-323, F4 and
F2_7; readings P-PLANT). Probe: F4_11 +0.031 and F4_12 +0.030 against F3_4 +0.146 at F15. The only source is
F3_4 (the latent is Markov, so given F3_4(t) nothing else predicts the drift), which satisfies P4.2's "one F3
feature carries a signal"; the pass rule is about Tier A, not feature attribution. Say so in the B5 summary's
plant line so a reader of the fold models' coefficients does not take F4 weight for a leak.

N2. The 400-null-Sharpe SD (run_proofs33.py:182-199) centres each configuration on its mean over the 20 seeds,
which removes one degree of freedom per configuration: under independence the expected population SD of the
centred values is sqrt(19/20) x 0.0354 = 0.0345, not 0.0354. Report only (P4.2); print the df-corrected value
sqrt(20/19) x pstdev beside the raw one, or state 0.0345 as the reference for the centred SD.

N3. A fitted configuration can exceed the oracle (readings: seed 9101 L001E 0.417 against the seed's oracle
0.369). P3.5 with class-level means is not Bayes-optimal, and the oracle conditions on (z, sigma_D) but trades
whenever EV > 0; a more selective fitted rule can earn more per trade. The oracle is a calibration anchor, as the
readings say; the summary should carry one sentence to that effect so "fitted > oracle" is not read as a leak.
Also: at an oracle SR of 0.35 every gate passes with probability near 1 (G4 needs 0.2007 at se 0.035; G5 (a)
P(quarter mean > 0) = Phi(0.35 sqrt(61)) = 0.997; G5 (b) cannot fail at this Sharpe; G5 (c) t about 9.9), so the
planted proof will not separate a weak pipeline from a strong one. This is the protocol's declared scale (P4.2:
oracle 0.35; the 0.91 arithmetic was for a realised 0.25), not a defect; the per-seed realised Sharpes beside the
oracle are the informative output.

N4. TB barriers are monitored once a minute at the B points (synth33.py:413-431; readings P-TB), so the synthetic
T30 reaches a barrier less often than the production label would on a real book (class shares about
0.29/0.42/0.29). The proof exercises the TB code path (first hit, direction, exit at tau + L, vertical exit at
t + L + h with the fill at C_{i+h}) rather than its rates; fine for a proof, and consistent with P3.4 at minute
resolution.

N5. Tier B fill accepts a constant (no-trade) series (select33.py:277-286; test_failed_and_constant asserts it).
P8's fill text says "with a defined series", so this is literal; the correlation is reported as None. If the lead
reads "defined" as "non-constant" the fill condition is one `or r["constant"]`. No outcome effect in the proofs.

N6. run_proofs33.py is itself in HASHED (run_proofs33.py:49). Any edit after launch, including SF1's summary text,
makes check_manifest refuse the resume; the only ways on are a new --proofs-dir (all 40 seeds again) or
`--summary-only`, which skips check_manifest (main: 279-281) and runs whatever run_proofs33.py is on disk. So:
land SF1/SF2 before the first production start; and have the summary print the sha256 of the run_proofs33.py that
wrote it (code_hashes()["run_proofs33.py"] at write time) beside the manifest's, so a summary-only rewrite after an
edit is visible. Under R-L3 (b) an edit of run_proofs33.py is an executed-file change; the lead decides whether a
summary-printer edit triggers the rerun rule or is logged as a report-only change.

N7. Null probe (evidence above): no feature carries information about the future path under beta = 0 as far as
pooled correlations on 46k rows show; the maxima sit on per-date features with an effective sample of about 180
dates, and their signs vary across seeds. Streams are separate per component (synth33.py:163-170): the features'
draws (ctx, f1-f4, the plant latent at A_j) and the future increments (diffusion at later j, the spreads at the B
and C points) never share a cell. C_3 is the spread at A_j; the entry and exit spreads are other i.i.d. cells.

N8. test_no_look_ahead_in_features (test_synth33.py:149-159) perturbs from minute i0 + 1 on, all three sample
points. A feature that read the B or C point of minute i0 itself (t + L or t + 2L, the entry fill) would pass that
test. The code reads only `[:, :, 0]` (A points) for mids and spreads (synth33.py:257, 297), and my probe with the
B/C points of minute i0 perturbed passes; tighten the test by also perturbing `bid[:, PRE + i0, 1:]`,
`ask[:, PRE + i0, 1:]`, `z[:, PRE + i0 + 1:]` and `spread_a[:, PRE + i0 + 1:]`.

N9. The label tests check the long side's net and exit against independent arithmetic (test_fh_label_invariants,
test_tb_label_against_a_row_loop) and the short side only through y consistency; n_short = bid_e - ask_x - f
(synth33.py:408, 433) is visibly right, but a sign slip there would not fail a test (the oracle MC test checks the
same formula in fh_class_probs, not in make_labels). Add `short_net == bid[dd, jb, 1] - ask[dd, jx, 2] - FEE` to
the TB loop and the FH gross-integer check for the short side.

N10. Feasibility, outside my object but visible from the readings: 13-20 minutes a seed (9-13 h for 40) against
the 09:00 PDT hard deadline, with a start after about 02:40. The runner reports seeds not run as "not run" and the
counts over the seeds run; P4.2's "all 40, each once" and P10's feasibility rules are the lead's call. Memory: the
readings' full-size trial at 8 processes was stopped with 4.3 GB available; check `free -m` and the P5 thread cap
(processes x threads <= 8) before launch.

N11. `--allow-partial` lets a subset of the 40 run under one --proofs-dir (run_proofs33.py:271-272). Each start's
seeds are appended to the manifest's `starts` and a finished seed is skipped by selection.DONE, so no seed reruns on
its own unless its folder is deleted. Have the summary print `starts` (times and seeds) so a partial or resumed
run is visible in the deliverable.

## Readings (my view on each; the lead decides)

Q3 Tier B start point ("continue" chosen; both computed and written to selection.json tier_b_detail). My view:
"continue" is the literal reading of "continue the Tier A walk ... taking the next two", and the implementation
matches the readings' description (select33.py:355-358: from the position in the all-configuration order after
the last configuration the Tier A walk examined; the third taken, or the last passer when fewer than 3). The two
readings differ only when a gate-failed configuration ranks above the last examined passer (the test
test_tier_b_readings_differ_on_a_high_ranked_gate_failure shows one). On conservativeness: the coder's argument
("lower-ranked companions widen the verdict's Sharpe SD") is about discovery ranks while V14 (c)'s variance is
over test-window Sharpes; it holds only to the degree that discovery rank predicts the test Sharpe, which it does
weakly (a gate-failed high-SR_d configuration is likelier than a low-ranked one to have a high test Sharpe, hence
a closer companion and an easier DSR under "restart"). So "continue" is the conservative choice for the binding
check (the DSR) and the coarser PBO check moves the other way, as the coder says. I agree with "continue"; the lead
should carry it into reports/stage_e33_protocol_readings.md before the freeze, since it is outcome-relevant when
Tier A has one member. Two details worth stating in the reading: (i) under "continue" with Tier A full, gate-failed
configurations ranked between the first and third member are never examined for Tier B while those just below
the third are; (ii) under "continue" with one Tier A member, every passer rejected for rho > 0.70 lies above the
start, so Tier B comes from below the lowest-ranked passer.

Q1 (G1 integer comparisons): agree; 398 of 796 passes, tested. Q2 (fsum(X_D)/count): agree; identical to the
trades' nets up to rounding. Q4 (undefined se fails G4): agree; the same radicand makes deflated_sharpe_ratio
raise, so G3 fails too and the pass set is unaffected. Q5 (undefined LOMO t fails): agree; constant series only.
Q6 (undefined correlation never qualifies): agree. Q7 (one-sided normal p for BH/Holm): reports only; fine.
Q8 (PBO over configurations with a series): agree with P6.3. Q9 (best = first in the total order over defined
series): agree with P4.2's "best planted configuration per seed". Q10 (SD of 400 centred Sharpes, constants as
0): agree, with N2's df remark. Q11 (failed configurations fail every gate alone): agree.
Generator readings P-L, P-TB (N4), P-SPREAD, P-VOL, P-PLANT (N1), P-ORACLE, P-NULL, P-RULES, P-FEATURES,
P-SEED9000: design choices of the synthetic world, none departs from P4.2; the oracle definition (true class
probabilities given z and sigma_D, class means over all rows, P3.8 with f and the dead zone) matches P4.2's text.
P-FLAGS (C_11-C_14 constant 1) is harmless: the engine zeroes constant columns for LOGIT (SearchReview).

## Checked and found correct

P8 in select33.py (evaluate 129-175, g5_stability 178-206, funnel 210-217, rank_key 220-228, walks 245-288,
select 337-371):
- G1: count >= 1.0 x 796 and dates with a trade >= 0.5 x 796 (154); test_g1_boundaries at 795/796 trades and
  397/398 dates.
- G2: fsum(X_D) / count >= 0.50 (146-155); undefined (no trade) fails; boundary tested to 1e-6.
- G3: deflated_sharpe_ratio(observed_sharpe = mom["sharpe"], n_observations = T = len(dates) = 796 (strict asserts
  796), n_trials = N (838 in the proofs), sharpe_variance = 1/(T - 1), skewness and raw kurtosis from moments()
  of the configuration's own series) and `> 0.95` strict (160-165); sd = 0 and a ValueError (degenerate radicand)
  give None and fail. The argument order matches the function's signature (funnel/multiple_comparisons.py:81-88).
- G4: se = sqrt((1 - g3 SR + (g4 - 1)/4 SR^2)/(T - 1)) with the configuration's g3, g4 (91-96), SR - se >= b_test
  (170); b_test_at(N) reproduces p7_final.report() unrounded (max of 3/sqrt(870) and required_sharpe(N, 870,
  1/869, 0, 3)) and asserts round(., 6) == 0.164882 at N 838 (74-88); the G4 threshold at normal moments is
  0.2007 (test and my inline check). Reading Q4 for a non-positive radicand.
- G5 (a): quarters Dec-Feb, Mar-May, Jun-Aug, Sep-Nov named by their first month (quarter_key 100-107; Dec -> y-12,
  Jan/Feb -> (y-1)-12, else 3 (m // 3)); 13 quarters on the real OOF dates, the first (2020-12) holding the 40
  dates 2020-12-30..2021-02 and no burn-in date; mean daily net > 0 in >= 9 (184-186).
- G5 (b): total > 0 and max month sum <= 0.25 x total (187-190); the exact-25% boundary tested with integers.
- G5 (c): for each of the 39 months, t_stat(moments(series without the month)) >= 2.5 (191-196); t_stat is
  harvey_liu_zhu_verdict's mean / (pstdev / sqrt(n)); min LOMO t equals an independent recomputation in the test.
- G5 (d): dates sorted by (sigma_ZM(D), date) ascending, slices [0:265], [265:530], [530:796] (117-121); the tie
  rule tested with a flat sigma; sigma read from the features' _day json per OOF date (load_root 418-424).
- Failed configuration (x None): every gate False, no series, never ranked or walked (133-137, 225-226).
- Funnel: each gate alone and in order G1, G1..G2, ..., G1..G5 (210-217), failed count carried.
- Ranking: (-round(SR_d, 4), trade_count, LOGIT 0 / LGBM 1, set index, h, FH 0 / TB 1, grid position) (220-228):
  the P8 order including "FH before TB at equal h" and Python's half-to-even round; test_ranking_tie_breaks covers
  every tie-break.
- Tier A walk: rank order over passers, take if rho <= 0.70 with every taken (np.corrcoef on the raw daily
  series), stop at 3 (245-257); the cap and a rho 0.95 near-duplicate tested.
- Tier B walk: gates ignored, failed and constant skipped, rho <= 0.70 against Tier A and Tier B taken, fill by
  the highest-ranked remaining defined series with correlations reported (260-288); both readings computed.
- Empty Tier A: ranking_pass [], tier_a [], best_config still reported (P10).
- Reports (never gates): PBO via screening.stage_e_verdict.pbo over the series present; BH largest k with
  p_(k) <= k q / m and Holm step-down (298-314); the P7.2 reference z values reproduced (3.588, 4.042, 6.283,
  3.847, 2.539/2.773/2.902).
- load_root (385-425): requires DONE per configuration, treats stats.failed as a failed configuration, checks
  daily.parquet against stats.json (trade_count exactly, Sharpe to 1e-12), requires one code_sha12 features folder
  or an explicit sha, and a finite positive sigma_zm on every OOF date.

synth33.py (the generator):
- Real OOF dates, grid G_h(D) = i in 0..277-h on the open-time axis from 08:35:00 CT (make_labels 394-400,
  t0_ns from cal33.ct_ns), real P1.4 exclusions (rule 4: entry_ok and row_ok all False, mid_move NaN) and the real
  rule-3 release instants with the closed-interval test on the possible span [t, t + L + h] (353-358, 434-438);
  rules 1-2 hold by the grid; rules 5-6 cannot arise on the synthetic book (readings P-RULES).
- FH (403-411): N_long = bid(B_{i+h}) - ask(B_i) - f, N_short = bid(B_i) - ask(B_{i+h}) - f, y by sign with the
  P3.3 impossibility asserted; exit fill time t + h + L, entry t + L.
- TB (412-433): m0 = M(B_i); barrier test 2(M - m0) >= 2b, <= -2b with b = sigma_ZM(D) sqrt(h) at the B points
  k = 1..h (the interval (t + L, t + L + h]); both-barriers asserted impossible; tau = first hit else t + L + h;
  exit at tau + L = C point; nets as P3.4; direction from the hit side. Checked by a row loop in the test.
- Weights: P3.7 average uniqueness at 1-minute resolution over intervals met by more than one second (the FH
  span of h min + 1 s covers h intervals; TB's realised span), per date; equal to lab33.uniqueness_weights to 1e-12
  in the test.
- Null (beta = 0): the drift term vanishes in d_ab, d_bc, d_ca (223-225); F4 features use mids at A points at or
  before t (297-321: look-backs j_i - k, hi/lo accumulated through t, dm and b2 windows ending at t); F2_7 is a
  combination of noise and F4_2; every other feature is clock, calendar, sigma_ZM(D) of the 20 previous dates, the
  spread at t, or an independent stream. Probe results in N7/N8.
- Plant: drift over (t_j, t_{j+1}] = beta z_j with z_j = F3_4(t_j) (223-225, 330); beta = 0.367 (PLANT_BETA, equal
  to ProofCoder_calibration.json's beta, tested).
- Oracle (464-565): drift_moments gives E and Var of the B_i -> B_{i+h} drift for the AR(1) plant (checked
  against a simulation in the test); fh_class_probs is the exact P(y = +1), P(y = -1) given Delta ~ N(m, v), a
  uniform fractional part and independent 1/2-tick spreads at entry and exit. I re-derived the eight thresholds:
  1-tick exit y = +1 iff Delta >= a_e + 1 - u, 2-tick exit iff Delta >= a_e + 1.5 - u, with a_e = 1 (+1 at a 2-tick
  entry when u >= 1/2); y = -1 iff Delta < b_e - 1 - u (1-tick) or b_e - 1.5 - u (2-tick), b_e = 0 or -1; the
  average over u uses s (G(x0) - G(x1))/(u1 - u0) with G(x) = x Phi(x) + phi(x). The MC test agrees to 0.002. Class
  means are P3.7-weighted over all rows; EV = sum_k p_k mu_k; the P3.8 simulation (one position, cap 20, entry_ok,
  exact tie = no trade, next decision at the first grid minute >= the exit fill) equals search33.simulate_date
  trade by trade in the test.
- Calibration record: bisection over 60 draws (seeds 70001-70060, common random numbers), beta 0.367 gives mean
  oracle SR 0.3498 (se 0.0048, SD 0.037 across draws), the independent 60-draw check 0.3486 (se 0.0045);
  dSR/dbeta about 1.0. Target 0.35 met within one se.
- Determinism: SeedSequence([20261027, seed]) spawned into 10 named PCG64 streams, draws of fixed size 816 so a
  reduced calendar is a prefix; tested (same seed equal, other seed different, prefix property).
- Layout: features/<sha12>/<date>.parquet (date, i, t_ns, 59 columns), _day/<date>.json for all 816 dates with
  sigma_zm None on burn-in dates, labels/<sha12>/<LABEL>/<date>.parquet in the INTERFACE 4.2 columns plus mid_move,
  _excl json, synth/oracle.json, manifest.json, DONE last (resumable); search33.load_tables reads it (test).

run_proofs33.py (the runner and summary):
- Seeds 1-20 null, 101-120 planted (synth33.kind_of_seed; PRODUCTION_SEEDS), refusals for a mixed run, a subset
  without --allow-partial, reduced size, another kind or N != 838 on production seeds, and a test run writing the
  production summary (266-274; tested).
- 20 configurations E33-S5{F15,T30}{10 grid points} through run_search33 with the P5 thread cap and
  --expected-n 796 at full size (45, 119-121); selection with strict = True at full size, N = 838, b_test from
  p7_final (128-129); selection.json and selection.DONE with select33's sha (131-138).
- Exactly once per code hash: run_manifest.json pins synth33, select33, run_proofs33, search33, run_search33,
  cal33, data33, guard33, p7_final, p7_thresholds, N, n_oof, the ids, PLANT_BETA and the plant feature; a resume
  with any difference refuses (77-96; tested). Finished seeds are skipped by selection.DONE; synth/DONE and the
  engine's markers make a cut run resumable.
- Fold models: nothing in run_search33/search33 deletes fold<k>.npz; every seed's models stay (seed 1 for LT7).
- Summary: null section counts seeds with Tier A non-empty against the P4.2 rule (fails at >= 2 of 20), the
  best-SR_d distribution, the 400-Sharpe SD against 1/sqrt(796) = 0.0354 (all series, constants as 0; and
  non-constant only); planted section counts seeds with at least one configuration in Tier A against >= 14 of 20
  (R-L4 (a)) with the per-configuration counts (R-L4 (b)) and the oracle SR beside each seed's best; the manifest's
  code hashes are printed; "not run" rows for unfinished seeds. The summary draws no verdict.
- Collector window wait, nice 10, OMP/OPENBLAS/MKL threads 1.

Tests: the 50 tests pass; they would fail on wrong code at every gate boundary (bisection to 1e-6 on G3, G4 and
G5 (c)), on a wrong quarter grouping (13 keys asserted on the real dates), a wrong tercile size or tie rule, a
wrong tie-break order, a wrong Tier A cap or rho rule, a wrong Tier B start under either reading, a wrong b_test,
a wrong TB first-hit or exit time (row loop), wrong weights (lab33 comparison), a non-deterministic seed, a
drifting null or a plant elsewhere than F3_4 (correlation of z with mid_move), a wrong oracle probability (MC) or
a simulation differing from search33's. Gaps: N8 (look-ahead cut one minute late), N9 (short-side nets), and
no test of the summary's content (SF1).

## Not checked

- The engine's folds, embargo, fits, calibration and P3.8 simulation (SearchReview.md).
- cal33's calendar (DataCoder); lab33 beyond the uniqueness comparison; the real feature and label builders.
- A full-size proof seed end to end (the readings' seed 9002 reduced run and 9101 partial full run stand; I ran
  no search).
- Memory and wall time of the 40-seed run (N10).

Closing: 02:32 PDT by `date`. No pipeline file was edited (mtimes 02:02-02:03 and 2026-10-27 15:26, all before
this review started); no production seed was run; holdout `sealed_ok` true at the end.
