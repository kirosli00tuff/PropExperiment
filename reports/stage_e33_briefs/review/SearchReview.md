# SearchReview (Stage E.33, pre-proof review of the search engine)

Reviewer: SearchReviewer-OpusXHigh (fresh context; did not write the code). 2026-10-28, started 02:03 PDT.
Status: COMPLETE (02:17 PDT by `date`; line numbers re-checked against the files as of that time, mtimes 2026-10-27 15:13-15:24).

Object: reports/stage_e33_briefs/work/pipeline/search33.py (886 lines), run_search33.py (299),
tests/test_search33.py (644), tests/synth_search33.py (132), work/SearchCoder_readings.md (S1-S20).
Standard: reports/stage_e32_discovery_protocol.md (0.3, P3.5, P3.7, P3.8, P4 G5, P4.1 LT3/LT7, P4.2, P5,
P6.1, P6.2, P7.1, P8 G5 (d), P10) and reports/stage_e33_briefs/INTERFACE.md (3, 4.2, 4.3).
The parallel P6.2 mid_move change (mid_sign_hit, MID_SIGN_RULE, OPTIONAL_LABEL_COLUMNS) is out of scope.

Evidence run (synthetic data only). Probe scripts (session scratchpad, may not persist):
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/86e80bc3-d62a-42e1-b5fd-5c881ccf8b54/scratchpad/searchreview/
(probe_lgb.py = probe 1, probe_pp.py = probe 2, probe_fail.py = probe 3 (in SF2), probe_thr.py = probe 4).
- `uv run pytest -q -p no:cacheprovider .../tests/test_search33.py`: 35 passed in 149.9 s (02:07-02:10 PDT).
  Side effect to note: test_runner_refuses_real_root_without_registration launches the runner on the real
  root, and the runner writes its log into derived/e33/search/_logs/ before it refuses (see N1); my run
  added run_20261028_021007_1947078.log there. No outcome is read or written by it.
- Probe 1 (scratchpad/searchreview/probe_lgb.py, synthetic 20,000 x 10, 3 classes, LightGBM 4.7.0): the
  engine's feval receives predictions already shaped (n, 3) (so the reshape is a no-op, not a reorder);
  per-iteration feval values equal LightGBM's built-in weighted multi_logloss to 1.6e-10 relative; both
  runs stop at the same best iteration (88) after the same 138 rounds; the feval equals a manual
  recomputation at the best iteration exactly.
- Probe 4 (scratchpad/searchreview/probe_thr.py, synth_search33 T30 tables, 120 dates, correlated
  features, fold 1): G3050 and G2200 fitted and predicted at 1 and at 8 threads give identical trees,
  best iterations (29, 65), calibrator coefficients and probability bytes (P5's 1 x 8 option included).
- Probe 2 (scratchpad/searchreview/probe_pp.py, synth_search33 tables, fold 3): the engine's
  predict_proba equals sklearn's est.predict_proba (LOGIT L100E) to 2.2e-16 and the booster + sklearn
  calibrator predict_proba (LGBM G2050) to 2.8e-16; LGBM mu_long equals an independent weighted mean over
  all training rows (inner-train and inner-validation) exactly.

Severity counts: BLOCKING 0, SHOULD FIX 4, NOTE 10.

## Findings

### SHOULD FIX

SF1. Finished folds and configurations are reused across pipeline versions (no code hash in any DONE).
- Where: search33.py:830-836 (fold_state), 839-861 (finalize_config checks only feat_sha/label_sha folder
  names, 858-861); run_search33.py:118-131 (plan() skips any config with DONE and any fold with DONE or
  FAILED); run_fold's meta (search33.py:804-806) records versions and table folder names but no sha256 of
  search33.py / run_search33.py.
- Protocol: P4.2 "each run exactly once per pipeline hash ... after a logged code fix (0.2) all 40 are
  rerun with the same seeds, every run before and after the fix is reported"; P4.1 LT7 second run "the P3.8
  simulation, and any fit the fix touches, is re-run for all 300 configurations".
- Failure scenario: a proof exposes a bug in fit_lgbm; the lead fixes search33.py and relaunches the 40
  searches on the same proofs/seed<s>/ roots. plan() finds every config DONE, logs "0 fold tasks to run",
  and the pre-fix results are reported as the post-fix rerun. The same happens to FAILED folds (a failure
  caused by the fixed bug stays failed). Tables: synth33._sha12 names proof folders by the generator's
  sha256 and the seed, so a generator fix gives new folder names and finalize_config refuses folds fitted
  on the old ones, but only for configurations not yet DONE: plan() skips a config-level DONE without any
  check, and a fix to search33.py or run_search33.py changes no folder name at all. A rebuilt real store
  with unchanged code keeps its <sha12> name, and finalize compares names, not contents.
- Fix: compute pipeline_sha = sha256 over search33.py + run_search33.py (+ the guard/data modules the
  engine imports) once per process; write it into fold meta, fold<k>.DONE, fold<k>.FAILED and the config
  DONE; in plan() and finalize_config treat any marker whose pipeline_sha differs as stale (refuse with a
  clear message, or key outputs as search/<pipeline_sha12>/<cid>/). Also record a content fingerprint of
  the tables actually loaded (e.g. sha256 of each label folder's file list with sizes and mtimes, or of
  the manifest.json) and compare it in finalize.

SF2. Any exception in the fold path, including infrastructure errors and code bugs, is recorded as a failed
fit and permanently fails the configuration.
- Where: search33.py:791-803 (`except Exception` around fit, model write, model reload, predict).
- Protocol: P5 "Failed fits": a fold "whose fit raises an error, or yields probabilities that are not
  finite, is failed"; "A fold interrupted before it writes its result ... is not failed: it is rerun once".
- Failure scenarios (probe 3, scratchpad/searchreview/probe_fail.py, synthetic): (a) an OSError while
  writing the fold model (EIO injected on fold1.model.json only) wrote fold1.FAILED: the configuration
  fails G1 forever instead of being an interruption that is rerun (a completely full disk is different:
  the FAILED write then fails too and the run stops, rc 5). (b) A code bug in this path (probe 3: a TypeError injected into fit_lgbm wrote
  fold1.FAILED; likewise KeyError, ImportError of lightgbm in a worker, AssertionError) fails every
  configuration it touches; in a null proof that makes Tier A
  empty for the wrong reason (failed configurations fail G1), and the runner logs it only at INFO
  ("fold k failed ..."), so 20 null "passes" can hide a broken LGBM path. (c) LightGBM reports a C++
  allocation failure as lightgbm.basic.LightGBMError ("std::bad_alloc"), not MemoryError, so an in-fit
  out-of-memory error inside LightGBM becomes a failed fit rather than the interruption P5/P10 require.
- Fix: catch only fit-time numerical failures (FitError, LightGBMError other than bad_alloc, sklearn's
  ValueError/FloatingPointError raised inside est.fit/booster training/predict) as failed; let OSError,
  ImportError, TypeError, NameError, KeyError, AssertionError and any bad_alloc propagate (rc 5 stop, or
  treat bad_alloc as an OOM interruption). Log every failed fold at WARNING and print the count of failed
  configurations in the run summary.

SF3. One dead worker counts as an interruption of every fold running beside it, so one deterministic OOM can
fail up to seven innocent configurations.
- Where: run_search33.py:192-198 (BrokenProcessPool handling), with search33.py:789-790 (an attempt line is
  appended by every fold at start); CPython 3.12 concurrent.futures.process._terminate_broken terminates
  all remaining workers when one dies (checked in the installed interpreter).
- Protocol: P5 "a second interruption of the same fold fails the configuration"; P10 counts OOM kills.
- Failure scenario: 8 LOGIT folds run; one is OOM-killed. The pool terminates the other 7, each with one
  attempt line. The lead relaunches; the same heavy fold is OOM-killed again (deterministic), the pool
  again kills the 7 bystanders, now at 2 attempts each; the next plan() marks all 8 folds FAILED
  ("interrupted twice") and fails 8 configurations, 7 of which were never interrupted by anything of
  their own. (P10 stops E.33 at the second OOM anyway, but the failed markers stay on disk and any
  resume after the stop inherits them.)
- Fix: when a BrokenProcessPool arrives, write a "collateral" record into the bystanders' attempts files
  (or remove their last attempt line) so only the fold whose process died first is charged; or run each
  fold in its own subprocess (subprocess.run per task) so a kill is local, and read the exit status
  (-9 = killed) to classify the interruption.

SF4. The attempt record is written after the tables load, so a fold killed during loading is never charged.
- Where: search33.py:786-790 (load_tables, then the attempts append).
- Protocol: P5 "A fold interrupted before it writes its result (a killed process, an out-of-memory kill
  ...) ... a second interruption of the same fold fails the configuration".
- Failure scenario: a fold whose worker is OOM-killed during load_tables (the largest allocation of a
  worker: about 0.13 GB of features plus labels, more in the concatenation) is rerun indefinitely and never
  reaches the "interrupted twice" rule; the attempts count under-reports interruptions to the lead.
- Fix: append the start record before load_tables (it costs nothing), with a field saying which phase
  was reached, or append a second record "fit_start" after loading.

### NOTE

N1. The real-root refusal is by exact path and happens after the runner has written into the real root.
- run_search33.py:69-81 refuses only when root.resolve() == derived/e33. Any other root holding real
  labels (derived/e33/implB, a copy, a tree of symlinks into derived/e33/labels) is not refused; the
  guard is applied (guard_for returns guard33 for roots inside derived/e33) but the guard allows the whole
  derived/e33 tree. Today implB/labels has no <sha12> level (implB/labels/F05/...), so load_tables fails
  on it with "0 code_sha12 folders"; the hole is closed by layout, not by the check. Also main() calls
  setup_logging(root) before check_root (run_search33.py:281-282), so every refused attempt (and every run
  of test_runner_refuses_real_root_without_registration) writes derived/e33/search/_logs/run_*.log (8 such
  logs exist there now). Suggest: call check_root before setup_logging, and require --registered for every
  root inside derived/e33 except proofs*/ and probes/, or require a SYNTHETIC marker file written by the
  synthetic generators in every unregistered root.

N2. The thread cap is per runner invocation. Two runners (for example two proof seeds launched side by side)
make up to 16 fitting threads; nothing (a lock file) prevents it (P5 "processes x threads <= 8 at any
time", CLAUDE.md). The parent also runs finalize (simulation, table load) as a ninth busy thread while 8
worker threads fit. Suggest an flock on derived/e33/search.lock (or one proof driver that runs seeds
serially) and counting the parent's finalize as one thread.

N3. meta["iterations_built"] is not the number of iterations built. lgb.train(keep_training_booster=False)
returns the booster reloaded at its best iteration, so booster.current_iteration() equals best_iteration
(probe 2: best 22, "iterations_built" 22, rounds_run 72). best = min(best_reported, built) is therefore a
no-op except when splits run out, and the test assertion `best_iteration <= iterations_built`
(test_search33.py:342) is vacuous. The kept model is correct (best iteration, no refit); only the label is
wrong. Suggest recording the pre-reload count from a callback (env.model.current_iteration()) or renaming.

N4. A finalize error crashes the runner without a log line. run_search33.py:205-207 calls finalize() outside
any try; an exception propagates through the ProcessPoolExecutor context (running folds finish), and main()
never writes the manifest JSON; the traceback goes to stderr only. Suggest try/except around finalize with
log.error and stop/rc as for rc 5.

N5. A MemoryError re-raised by run_fold (search33.py:798-799) reaches the runner as an ordinary exception and
is logged as "raised" with rc 5, not as an out-of-memory interruption; P10 counts OOM failures. Suggest a
distinct rc and message for MemoryError.

N6. S3 (entry not made -> the next minute is decided, not counted toward the cap) is the literal reading of
P3.8 ("fewer than 20 entries have been made"; "When flat") and I find it causal: for flag 16 (no valid
update before the planned exit) the ZM book lacks the needed side or is marked bad at every grid minute
before the planned exit, so entry_ok is false there and the reading cannot differ from "wait for the
planned exit"; for flag 32 (TB, mid undefined at the fill update) the fill update is at or before the next
entry_ok minute, so the not-made status is known before the next decision. No future value enters.

N7. Tests that would pass on some wrong code (the code itself is right; see probes): (a) the bit-for-bit
round-trip test compares predict_proba with itself (stored vs recomputed by the same function), never with
sklearn's predict_proba or the calibrator's; probe 2 fills that gap (2e-16), and a test should keep it;
(b) no test pins that LGBM mu_k use all training rows (inner-train and inner-validation) and that the
calibrator uses inner-validation rows only (test_lt3 perturbs only evaluation/embargo rows and non-rows);
(c) test_lgbm_bins_from_inner_train_only cannot fail on reference= misuse because lgb.train itself sets
the validation set's reference to the training set; it proves the property, not the code line;
(d) the real-root refusal test covers only the exact root (N1).

N8. S18 (inner validation counts training dates including excluded dates) and the absence of an embargo
between inner-train and inner-validation are literal readings of P5; flagged only so the lead rules on S18
explicitly.

N9. LightGBM's metric "None" plus the float64 feval (S11): same declared quantity (probe 1: 1.6e-10
relative, same stopping point); the stopping logic is LightGBM's own early_stopping callback, so best
iteration (first strict minimum), ties (no improvement on equality), first_metric_only (one metric) and
minimum rounds (none in LightGBM; the earliest stop is round 51) are identical to the built-in path. The
change removes a nondeterminism; I accept S11.

N10. The memory guard checks MemAvailable only at submit time (run_search33.py:175-178). Up to 8 workers
are submitted within a second, before any has loaded its tables (0.67-0.74 GB peak each, readings
"Timings"), so the check cannot see the growth of workers just started; with 8 LOGIT processes plus the
parent's finalize the peak is about 6-6.5 GB. With about 9 GB available now this fits, but the guard is
not what keeps it safe. Suggest reserving the measured per-process peak for every started-but-not-loaded
worker (or a fixed budget: refuse a submission if avail - 750 MB x (workers started in the last 30 s)
< 2048 MB).

## Checked and found correct
1. Folds and embargo (P6.1), search33.py:117-143: blocks 133, 133, 133, 133, 132, 132 in date order; the
   embargo is the next 21 OOF dates after block k (none after block 6); training = all other dates minus
   block k and its embargo; counts 642, 642, 642, 642, 643, 664 asserted for N = 796; no date before block
   k removed. training_mask = training dates AND row_ok. No evaluation or embargo row reaches the scaler,
   the LOGIT fit, mu_k, the LGBM inner blocks, early stopping or the calibrator (code path read; LT3 test
   perturbing evaluation, embargo and non-row data leaves the model bytes identical, folds 1, 3, 6, LOGIT
   and LGBM).
2. LOGIT (P5, G5): LogisticRegression(C, l1_ratio = rho, solver saga, max_iter 2000, tol 1e-4,
   random_state 20261027), sample_weight = w, multinomial (softmax link and P5's objective with
   unpenalised intercepts confirmed by the author's test against an independent L-BFGS-B minimum, with
   warnings as errors under sklearn 1.9.1); standardisation by the training rows' w-weighted mean and
   population SD, SD 0 (exact constant or computed 0) -> feature 0 in training and evaluation, evaluation
   uses training statistics; non-convergence recorded (n_iter, converged, warnings) and the fit used as
   is. Engine probabilities equal sklearn's predict_proba to 2.2e-16 (probe 2).
3. LGBM (P5): every listed parameter present and equal (multiclass/3, gbdt, 0.05, 500 rounds, stop 50,
   feature_fraction 0.8, bagging 0.8/1, lambda_l2 1.0, min_gain_to_split 0, max_bin 255, seed 20261027,
   deterministic, force_row_wise, num_leaves 2^d, max_depth d, min_data_in_leaf 50h/200h with the
   vertical h for TB, weights w, num_threads per the runner); inner validation = the latest
   ceil(15% x training dates) dates (97, 97, 97, 97, 97, 100); validation Dataset built with reference=
   the inner-training Dataset; early stopping on the w-weighted multi_logloss of the inner block only
   (S11, N9); booster kept at its best iteration via model_to_string(num_iteration=best), never refit;
   calibrator LogisticRegression(C 1e4, lbfgs, max_iter 1000, tol 1e-6) of y on the kept booster's three
   raw scores, fitted on the inner-validation rows with w; non-convergence recorded. Engine probabilities
   equal booster + sklearn calibrator predict_proba to 2.8e-16 (probe 2).
4. mu_k (P3.5): w-weighted means of n_long/n_short by class over all training rows (LGBM: inner-train
   and inner-validation; probe 2 exact); the empty-class reading S1 (FitError -> failed configuration) is
   consistent with the classes_ check, which would fail such a fit anyway.
5. EV rule and simulation (P3.5, P3.8): EV summed in class order; long iff EV_long > max(EV_short, 0),
   short iff EV_short > max(EV_long, 0), exact tie or both <= 0 -> no trade; decisions only at entry_ok
   minutes of G_h(D) while flat; at most 20 entries made per date (not-made attempts do not count, S3);
   the realised net, fill times and flags come from the chosen side's label fields; next decision = the
   first grid minute with t_ns >= exit fill (searchsorted left); X_D = sum of nets of trades entered on D,
   0 on dates without a trade and on excluded dates; each evaluation date uses its own fold's model
   (overlap and gap checks in run_simulation). The only label fields read before a decision are entry_ok
   (by contract known at t); made/net/exit are read only after the decision; row_ok, y, n_* never touch
   the simulation. No future value enters a decision (see N6 for the not-made case).
6. P6.2 statistics: moments(x) and t_stat(moments) from screening/stage_e_verdict.py on the 796-value
   series; trade count, trades per date (/796), mean net per trade, hit rate (net > 0), share of dates
   with a trade; per-fold, per-quarter (Dec-Feb, Mar-May, Jun-Aug, Sep-Nov keyed by the start month; 13
   on the OOF dates) and per-month (39) sums and means; vol terciles by (sigma_ZM(D), date) with ranks
   1-265, 266-530, 531-796 (n // 3 = 265). Counts of fallback fills, entries not made, limit and
   last-touch marks per configuration (P3.2).
7. Persistence: model JSON is canonical and reloaded before predicting (the OOF probabilities are those of
   the stored model, bit-for-bit across processes and thread counts per the author's test); fold DONE is
   written last with the sha256 of the npz and the model, and finalize re-verifies both before use; config
   DONE is written after daily/trades/not_made/stats with their sha256; all writes are tmp + os.replace.
   A partial fold (killed before DONE) is pending and refitted on resume (resume test: identical output).
   Exceptions: SF1 (stale across versions), SF2-SF4.
8. Runner: OMP/OpenBLAS/MKL = 1 set before numpy loads and inherited by spawned workers; LOGIT 1 thread,
   LGBM 4 or 8; submissions keep the sum of running threads <= 8 and processes <= --max-procs <= 8;
   os.nice to 10 before the pool starts (children inherit); collector-window pause; the real root needs
   --registered, --expected-n 796 and trial_registry.require_registered per prefix (exceptions: N1, N2).
9. Tests: 35 pass. The strong ones are the fold/embargo counts, the LOGIT objective with discrimination
   against wrong objectives, the LT3 perturbation tests, the independent early-stopping recomputation from
   a full 500-round booster, the simulator cases (cap, ties, not-made, exit exactly on a minute), the
   end-to-end determinism at two thread counts, and the kill-and-resume test. Gaps: N7.

## Not checked
- The parallel mid_move / P6.2 mid-sign change (out of scope by the brief).
- Behaviour on the real store or a production-size proof tree (synthetic small tables and probes only).
- select33.py, synth33.py and the proof driver (other workers); whether the proof driver uses fresh roots
  per pipeline hash (SF1 matters only if it does not).
