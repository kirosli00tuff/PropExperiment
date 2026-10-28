# SearchCoder readings (Stage E.33 B1, pipeline A search engine)

Worker SearchCoder-OpusXHigh, 2026-10-27 (14:47-15:25 PDT). Code:
reports/stage_e33_briefs/work/pipeline/search33.py, run_search33.py, tests/test_search33.py,
tests/synth_search33.py (synthetic tables for tests and timing only). Protocol sha256 c4ffb9d7... verified
at start. Every reading below is marked `# READING S<n>` in the code where it acts. The lead decides each
before the freeze; none changes a declared choice as I read the protocol.

## Readings

S1. Class with no training row. P3.5: "mu_long_k = the weighted mean of N_long over training rows with
y = k". P5: "A configuration with any fold whose fit raises an error, or yields probabilities that are not
finite, is failed". Considered: (a) the fit raises, so the configuration fails; (b) mu_k = 0 for the
empty class; (c) drop the class. Chosen: (a). A fold whose training rows lack a class, or (LGBM) whose
inner validation block lacks a class for the calibrator, raises FitError. That fold is written as
fold<k>.FAILED and the configuration is failed. Why conservative: no invented magnitude enters EV, and the
configuration cannot reach Tier A. On the real search (about 170,000 rows) this should never fire.

S2. "SD 0". P4 G5: "a training SD of 0 makes the feature 0 in that fold". Floating evaluation of a
constant column's weighted SD gives about 1e-17, not 0, which would blow the column up to +-1 noise.
Chosen: SD is 0 when the training column is exactly constant (max == min) or its computed SD is 0. The
feature is then 0 in training and evaluation rows. Conservative: it never amplifies a constant column.

S3. Entry not made. P3.2: "an entry with no such update before its planned exit time is not made
(counted)". P3.8: "When flat at t ..., and fewer than 20 entries have been made on D, apply P3.5."
Considered: (a) the account stays flat, the next grid minute decides, and the attempt does not count
toward the cap; (b) the next decision waits for the planned exit time; (c) the attempt counts toward the
cap. Chosen: (a), the literal reading ("entries made"). Not-made attempts go to not_made.parquet and the
stats counts. In practice (a) and (b) coincide: an empty side through the planned exit makes entry_ok
false at the minutes in between (the entry rules need both sides at t).

S4. Exit fill time = the label table's s_exit_ns. The next decision is the first grid minute whose t_ns
is >= s_exit_ns (an exit exactly on a grid minute lets that minute decide). This is not ambiguous; it
is listed so the lead sees which field drives P3.8.

S5. sigma_ZM(D) missing. P8 G5 (d): "the 796 OOF dates sorted by sigma_ZM(D) ascending (ties by date),
ranks 1-265, 266-530 and 531-796". Chosen: an OOF date whose _day json has no finite, positive sigma_zm
stops the load (ValueError) rather than defining terciles some other way. Conservative: it is a data
fault for the lead, not a silent gate failure.

S6. Quarters. P6.2: "per-fold, per-quarter and per-month sums". G5 (a): "(Dec-Feb, Mar-May, Jun-Aug,
Sep-Nov; the first without the burn-in dates)". Chosen: P6.2's quarters are G5 (a)'s seasonal quarters,
keyed by the start month ("2020-12" = Dec 2020-Feb 2021). stats.json carries sum, mean and n_dates for
each quarter and each month.

S7. Reported-only rho and top decile. P6.2: "the Pearson correlation rho over all OOF rows between the
chosen side's EV and the realised net of that side; ... the mean realised net in the top decile of
max(EV_long, EV_short)". Chosen:
- rows = the row_ok rows of the 796 dates, each with its fold's prediction;
- chosen side = the side with the larger EV, ignoring the zero threshold (exact ties dropped);
- realised net = the label's n_long or n_short;
- top decile = the first ceil(n/10) rows by max EV descending, ties by (date, i).
Also reported: the same rho over the trades actually taken ("rho_chosen_ev_net_trades"). These are never
used by P8.

S8. Mid-sign hit rate. P6.2: "the hit rate of the realised sign of the mid move over [t + L, t + L + h]
given the chosen side". Lead follow-up (15:2x PDT): the label table gains `mid_move` (float64 ZM ticks,
M_ZM(t + L + h) - M_ZM(t + L), NaN when undefined; TB uses the vertical h). Rule implemented
(search33.mid_sign_hit, MID_SIGN_RULE, written into stats.json):
- the population is the trades taken (P3.8), each with the side it took;
- hit rate = the share of those trades whose mid_move has the sign of the side;
- trades whose mid_move is NaN or exactly 0 are left out of the share and reported as n_nan and n_zero
  (n_used + n_nan + n_zero = trade count);
- hit_rate is None when no trade is usable;
- "not available" only when the column is absent from every date. A column present on some dates only
  stops the load.
stats.json: reported_only.mid_sign = {hit_rate, n_used, n_nan, n_zero, rule}, plus
reported_only.mid_sign_hit_rate = that hit_rate.

S9. Code-version folders. INTERFACE 4.1 keys tables by <code_sha12>. Chosen: the engine uses the only
12-hex folder under features/ and labels/, or the one given by --feat-sha / --label-sha. With two or more
folders it refuses. Fold DONE metadata records both shas, and finalisation refuses folds fitted on other
tables.

S10. Real root and the probe. INTERFACE 2.1: "No outcomes before registration." P5: "before the first
real-outcome fit, E.33 times ... fold 6 (the largest training set, 664 dates) of the two slowest grid
points". Chosen:
- run_search33 refuses the real DERIVED root (derived/e33 itself) unless --registered is given.
- It then runs `screening.trial_registry.require_registered(ids, test=<prefix>)` (read-only) per id
  prefix, E33 or E33A.
- On the real root, --expected-n must be 796.
- --probe writes timing only (no probabilities, mu_k or losses) to <root>/probes/search/<id>/. A probe on
  the real root still fits on real outcomes. I read P5's probe as needing a production-size synthetic
  table such as the one built for the timings below. The lead decides.

S11. Early-stopping metric. P5: "up to 500 iterations with early stopping after 50 rounds without
improvement in the weighted multi_logloss of the inner validation block". Found in testing: LightGBM's
built-in multi_logloss stores weights as float32 (it differs from the float64 weighted log loss by about
1.5e-8 relative). It also sums with an OpenMP reduction whose order varies between runs. When the trees
stop splitting, the jitter moved "best_iteration" past the iterations actually built, and one test fold
failed nondeterministically. Chosen: the same metric, sum w (-log max(p_y, 1e-15)) / sum w, as a numpy
feval with float64 P3.7 weights and a fixed summation order (metric "None" for the built-in one). The
stopping rule is LightGBM's own early_stopping callback (strict improvement, 50 rounds). Kept iteration =
min(LightGBM best, iterations built); both are logged. Evidence: the stopping points at production size
were identical before and after the change (best 29/46/27/29, 153/147/149/147 and 16/16/10/11 in the
three regimes). Tests show the feval equals LightGBM's metric to 1e-6 relative, my independent
recomputation to 1e-12, and repeated fits at 1, 3 and 4 threads give identical trees.

S12. Guard. INTERFACE 2.2: "Every real-data read goes through guard33 (P1.2)." Chosen: for roots inside
derived/e33 (real and proof trees), check_path on the features, labels and _day folders once per load,
check_date on every date, and check_path on any file that is a symlink. Per-file check_path costs 15 ms,
which made a 796-date load take 53 s against 6.3 s now. A folder check refuses a folder holding an
unsealed file, and the symlink check catches links out of the folder. Synthetic roots outside derived/e33
(pytest, scratch) skip the guard; its allowlist refuses them by design. The engine itself also refuses
dates outside 2020-12-01..2024-02-29.

S13. Interruptions and failed fits (revised 2026-10-28 02:2x PDT for review SF2, SF3, SF4). P5: "A
configuration with any fold whose fit raises an error, or yields probabilities that are not finite, is
failed"; "A fold interrupted before it writes its result ... is rerun once from the DONE markers with
identical settings ...; a second interruption of the same fold fails the configuration. Every
out-of-memory kill counts toward P10's two-failure stop". Chosen:
- Attempts (SF4). Each attempt appends a start record (time, pid, pipeline_sha) to fold<k>.attempts
  before the tables load, so a fold killed while loading is charged like any other.
- Twice interrupted. At planning, a fold with 2 attempts and no DONE or FAILED is marked FAILED
  ("interrupted twice"), and its configuration is failed.
- What fails a fit (SF2). Only the fit itself fails a configuration (fold<k>.FAILED):
  - FitError raised by the engine's own fit checks (a class without a training row, an empty inner block,
    an inner block without a class, wrong classes, no kept iteration);
  - ValueError, ArithmeticError or LinAlgError raised inside sklearn's est.fit (LOGIT, calibrator);
  - LightGBMError raised inside lgb.train, Booster or predict, except "bad_alloc";
  - non-finite probabilities.
- What is an interruption (SF2). Every other error propagates out of run_fold: loading, validation,
  writing (OSError), bookkeeping, and code bugs (TypeError, KeyError, ImportError, AssertionError, ...).
  The fold stays pending with its attempt charged, and the runner stops with rc 5 and the traceback in the
  log. A MemoryError, including LightGBM's "std::bad_alloc" (converted to MemoryError), is an
  out-of-memory interruption: rc 4, logged as counting toward P10.
- Dead workers (SF3). The runner no longer uses ProcessPoolExecutor, which terminates every worker when
  one dies. It runs long-lived worker processes, one pipe each; the parent assigns one fold at a time and
  watches each worker's pipe and process sentinel. A worker that dies (exit code logged; -9 = killed, for
  example by the OOM killer) loses only its own fold, which keeps its one charged attempt. The folds
  running beside it finish normally and write DONE, without a charge. The runner then submits nothing more
  and stops with rc 4 once those folds finish. The lead's relaunch is the one rerun; the log says the
  death counts toward P10 if it was an OOM kill.
- Logging. Failed folds and failed configurations are logged at WARNING, and the run summary prints the
  count and ids of failed configurations.

S14. Collector window. CLAUDE.md: heavy runs stay out of 15:30-16:00 PT on weekdays. Chosen: the runner
submits no new fold in that window (running fits finish; a single fit takes seconds to about 2 minutes).
--no-window-pause disables this.

S15. Label validation (the engine stops, never repairs):
- on row_ok rows: y outside {-1, 0, 1}, non-finite n_long/n_short/w, or w <= 0;
- off rows: y != 0;
- FH labels only: class and net disagree (P3.3; TB classes follow the mid barrier, so not for TB);
- a made trade with a non-finite net, entry_ns < t, or exit_ns <= entry_ns;
- feature and label t_ns differ, feature minutes are not 0..272, label rows are not exactly G_h(D), or
  features are non-finite.

S16. Model-file sha and threads. P8 records "the 6 fold models of each with sha256". The LightGBM model
string ends with a parameters block that records num_threads, so the file sha of an LGBM fold model
depends on --lgbm-threads; the trees do not (with deterministic=true). Each LGBM fold's metadata also
carries trees_sha256 (the model string before "parameters:"), which does not depend on the thread count.
LOGIT model files are byte-identical across reruns.

S17. Bit-for-bit predictions (lead addendum). The OOF probabilities are computed by predict_proba(model,
X) on the model reloaded from fold<k>.model.json (canonical JSON; floats round-trip exactly). Logits use
a fixed-order sum (no BLAS), then softmax. This is not sklearn's predict_proba, which differs at about
1e-16 and depends on BLAS. A test shows a fresh process with another thread count reproduces the stored
probabilities byte for byte (LOGIT and LGBM).

S18. Inner split counts training dates, excluded dates included. P5: "the latest 15% of the fold's
training dates by date (rounded up to whole dates)". ceil(15 n / 100) in integer arithmetic: 97, 97, 97,
97, 97, 100 dates for folds 1-6 (642, 642, 642, 642, 643, 664).

S19. LightGBM parameters P5 does not list stay at LightGBM 4.7.0 defaults:
- min_sum_hessian_in_leaf 1e-3, min_data_in_bin 3, feature_pre_filter true;
- bin_construct_sample_cnt 200000 (inner-training rows are about 141,000, so every inner-training row
  enters the bins);
- verbosity -1.
The calibrator input is the booster's three raw scores, unscaled (P5: "of y on the booster's three raw
scores"); sklearn 1.9.1 fits it multinomial (3 classes, lbfgs, l1_ratio 0 = L2, C = 1e4).

S20. Trade nets. X_D sums the label table's s_net of the trades entered (fallback fills included, P3.2).
The S7 rho over rows uses n_long/n_short; the trade-level rho uses s_net.

S21. Code and table versions in markers (review SF1). P4.2: "each run exactly once per pipeline hash ...
after a logged code fix (0.2) all 40 are rerun"; P4.1 LT7: "any fit the fix touches, is re-run".
- pipeline_sha is the sha256 over search33.py, run_search33.py and every pipeline/ module they import,
  found transitively from their import statements (today guard33.py). Each process computes it at import,
  so it is the code that process runs.
- It is written into every marker: fold<k>.attempts records, fold<k>.DONE, fold<k>.FAILED (fit failures
  and "interrupted twice"), the fold npz metadata, the config DONE and stats.json.
- tables_fingerprint is the sha256 over the bytes of every table file the load reads: features, labels
  and _day json, each tagged and named. Each file is read once, hashed and parsed from memory; a
  production-size guarded load took 3.6 s. It is written into the fold DONE, the npz metadata, FAILED,
  the config DONE and stats.json.
- Resume rule: refusal, not silent redo. Before anything runs, run_search33.plan() checks every marker of
  every requested configuration. Any marker without the running pipeline_sha (older markers have none)
  makes the whole run refuse with rc 6 and a "REFUSED" log line. The line names the configurations and
  says to move the config folder aside (or delete it) to rerun under the running code.
- finalize_config and load_fold_payload refuse the same way (StaleMarkerError). finalize_config also
  refuses folds whose tables_fingerprint differs from the tables now on disk: a store rebuilt under the
  same sha12 name is caught by content, not by folder name.
- Nothing is deleted or redone automatically. The lead decides what to move aside, so every run before
  and after a fix stays on disk to be reported (P4.2).

## sklearn 1.9.1 spelling (brief item)
- `penalty` is deprecated since 1.8 (removed in 1.10). The engine leaves it at its default and sets
  `l1_ratio` (0 -> L2, 0.5 -> elastic net). There is no `multi_class` parameter.
- saga minimises the multinomial loss for 3 classes; the code path is `_logistic_regression_path`,
  `loss = "multinomial"`, `alpha = (1/C)(1 - l1_ratio)`, `beta = (1/C) l1_ratio`.
- That is C sum_i s_i l_i + (1 - rho)/2 ||b||^2 + rho ||b||_1, with an unpenalised intercept, which is
  P5's objective.
- test_logit_minimises_p5_objective (3 grid points):
  - fits with warnings as errors;
  - evaluates P5's formula at sklearn's coefficients and matches an independent L-BFGS-B minimum on the
    split L1 form to 1e-7 relative;
  - checks the softmax link;
  - shows sklearn's solution is not the minimiser of two nearby wrong objectives (penalised intercepts,
    mean instead of sum loss).

## Additions to INTERFACE 4.3 (for the lead)
- fold<k>.model.json (lead addendum; sha256 in the fold metadata and in fold<k>.DONE).
- fold<k>.attempts (S13) and fold<k>.FAILED (P5 failed fits).
- not_made.parquet (date, i, side, flags, ev_long, ev_short).
- probes/search/<id>/fold6.timing.json.
- Logs in search/_logs/: run log plus a JSON manifest with argv, versions, uv.lock sha256, seed, thread
  environment, nice level, and start and end times.
- Exposed for LT7 and P8: load_fold_model(path), predict_proba(model, X), expected_values(p, mu_long,
  mu_short), decide(ev_long, ev_short); simulate_date also uses decide.

## Timings (synthetic production-size tables, fold 6, S5 x F15, 166,158 training rows x 59 features, 3 classes)
Tables: DERIVED/probes/searchcoder_synth/{balanced,imbal,stress}/ (synthetic). Measured 15:00-15:18
PDT at nice 10, with other E.33 workers loading the machine (load average about 6), so times vary up to
3x between runs.

| regime | LOGIT s per fit (L001A..L100E) | saga epochs | LGBM s per fit, 4 threads (G2050..G3200) | best iteration |
|---|---|---|---|---|
| balanced (independent features; synthetic class shares -1/0/+1 = 0.444/0.113/0.443) | 2.7-3.6 | 15-19 | 2.4-3.1 (first run), 5.9-9.2 (rerun under load) | 27-46 |
| imbal (independent; 0.071/0.858/0.071) | 2.0-2.9 | 12-14 | 4.2-5.2, 5.0-7.9 under load | 147-153 |
| stress (one factor per family at r = 0.9; 0.002/0.996/0.002) | 3.0 (L001E), 13.3 (L001A), 37.1 (L010A), 54.6 (L010E), 48.6 (L100A), 126.5 (L100E) | 5-419 | 6.8-8.3 (old metric), 2.1-2.7 (final code) | 10-16 |

- In the 6-process pool (balanced tables, other workers running), LOGIT folds took 9-19 s against 2.7-3.6
  s alone. Finalisation took 8.7 s, including the parent's table load (6.3 s with the guard).
- Peak RSS of one fold process: 0.67 GB (LOGIT L100E) and 0.74 GB (LGBM G3050). Eight LOGIT processes at
  once peak at about 6 GB; the runner refuses to submit when MemAvailable < 2 GB.
- Real features are correlated, so the stress row is the more realistic LOGIT bound. L100E is the slowest
  grid point, consistent with P5's probe choice.
