# Brief: SearchReviewer-OpusXHigh (Stage E.33, pre-proof review of the search engine)

You are an independent reviewer (Opus 5.5, xhigh, fresh context) for the E.33 lead. You did not write this code. Do
not spawn workers; do not ask questions. This review comes before the 40 synthetic proof searches (4,800 fits),
which by protocol P4.2 run once per pipeline hash: a bug found after them forces a full rerun. The formal B7 review
(Fable) comes later; your job is to catch what would invalidate the proofs or the search.

## Object
reports/stage_e33_briefs/work/pipeline/search33.py, run_search33.py, tests/test_search33.py,
tests/synth_search33.py, and the author's readings reports/stage_e33_briefs/work/SearchCoder_readings.md (S1-S20).
The author is making one small change in parallel (a P6.2 reported-only hit rate from a new label column
`mid_move`); ignore that part.

## Standard
The frozen protocol reports/stage_e32_discovery_protocol.md (read 0.3 statistics conventions, P3.5, P3.7, P3.8, P4
G5, P4.1 LT3 and LT7, P5, P6.1, P6.2, P7.1, P8 G5 (d), P10) and reports/stage_e33_briefs/INTERFACE.md (sections 3,
4.2, 4.3). screening/stage_e_verdict.py moments() and t_stat(); screening/stage_e_runner.py lines 25-45.

## Check at least
1. Folds and embargo exactly as P6.1 (block sizes, the 21 dates after each block, training-date counts, no date
   before block k removed); no evaluation-fold or embargo row in any training set.
2. LOGIT exactly as P5 (objective, grid, saga settings, weights, random_state, standardisation by the training fold's
   weighted mean and population SD, SD 0 -> 0, evaluation fold uses training statistics); non-convergence logged.
3. LGBM exactly as P5 (every parameter; the inner validation block = latest 15% of training dates rounded up; bins
   from inner-training rows only via reference=; early stopping after 50 rounds on the weighted multi_logloss of the
   inner block, reading S11 (a numpy float64 metric replacing LightGBM's float32 one): is it the same declared
   quantity, and is the stopping logic identical to LightGBM's early-stopping semantics (best iteration, ties,
   first_metric_only, min rounds)?; booster kept at its best iteration; calibration exactly as P5, fitted on the inner
   block with weights; no refit).
4. mu_k (P3.5) from the right rows (LGBM: all training rows), weights w, and the empty-class reading.
5. The EV rule and the simulation (P3.5, P3.8): flat, entry_ok, cap 20 entries, exact tie -> no trade, entries not
   made, next decision = first grid minute at or after the exit fill time, X_D, excluded dates, the fold model used per
   evaluation date. Any way a future value could enter a decision.
6. P6.2 statistics computed with the program's moments() and t_stat(); per-quarter and per-month sums; vol terciles.
7. Failed and interrupted fits (P5 "Failed fits"), DONE markers and resume: can a partial or stale result be taken as
   done? Determinism across processes and thread counts.
8. The runner's thread cap (processes x threads <= 8), nice 10, and its refusal of the real root before registration.
9. Whether the tests actually test what they claim (look for tests that would pass on wrong code).

You may run the tests (`uv run pytest -q -p no:cacheprovider <file>`) and write small probe scripts under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/86e80bc3-d62a-42e1-b5fd-5c881ccf8b54/scratchpad/searchreview/
(synthetic data only). Do not edit any pipeline file. INTERFACE.md section 2 rules apply (no real outcomes).

## Output
reports/stage_e33_briefs/review/SearchReview.md: each finding as BLOCKING (would invalidate the proofs or the search,
or departs from a declared choice), SHOULD FIX (a real defect of smaller consequence) or NOTE, with file:line, the
protocol line, a concrete failure scenario, and a suggested fix. Also list what you checked and found correct.
Return: the path, the counts by severity, and a summary of at most 200 words.
