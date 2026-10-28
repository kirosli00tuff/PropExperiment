# Brief: SearchCoder-OpusXHigh (Stage E.33 B1, pipeline A search engine)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue. The user asked for extreme care with the ML implementation: a leak in the folds
or the simulator makes every number worthless.

## Objective
Write the search engine: given one configuration (feature set, label, grid point) and the feature and label tables
(INTERFACE.md 4.1 and 4.2), run P6.1's six folds with P5's models exactly, P3.5's EV rule, P3.8's simulation and
P6.2's metrics, and write INTERFACE.md 4.3's outputs with DONE markers; resumable and deterministic. The same engine
runs the synthetic proofs (P4.2) on tables in the same schemas under DERIVED/proofs/seed<s>/, so it must take a root
directory.

## Read first (by section)
- reports/stage_e33_briefs/INTERFACE.md (all; section 2 rules bind you)
- Protocol reports/stage_e32_discovery_protocol.md: 0.3 (statistics conventions), P3.5, P3.7 (the weights you use),
  P3.8, P4 G5, P4.1 LT3 and LT7, P5 (all), P6.1, P6.2, P7.1, P8 G5 (d) (the volatility terciles use sigma_ZM(D)),
  P10 (failed and interrupted fits, DONE markers, run order)
- screening/stage_e_verdict.py moments() and t_stat(); screening/stage_e_runner.py lines 25-45 (the entry cap)
- reports/stage_e32_briefs/protocol/p7_final.py (thresholds; you only need to know it exists)

## Deliverables (reports/stage_e33_briefs/work/pipeline/)
1. search33.py:
   - Folds: the 796 OOF dates in order cut into blocks of 133, 133, 133, 133, 132, 132; embargo = the 21 trade dates
     after block k's last date; assert training dates per fold 642, 642, 642, 642, 643, 664. Training rows = row_ok
     rows on training dates.
   - LOGIT exactly per P5: scikit-learn 1.9.1 LogisticRegression, solver saga, max_iter 2000, tol 1e-4, multinomial
     loss, sample_weight = w, random_state 20261027, the C x rho grid, intercepts unpenalised, G5 standardisation by
     the training fold's weighted mean and population-weighted SD (SD 0 -> feature 0); non-convergence logged and the
     fit used. Check how 1.9.1 spells elastic net and multinomial (penalty, l1_ratio, multi_class deprecations) and
     prove in a test that the objective you call is P5's (e.g. compare the attained objective with a direct
     evaluation of P5's formula at the returned coefficients on a small problem).
   - LGBM exactly per P5 (4.7.0 parameters as listed; inner validation block = the latest 15% of the fold's training
     dates, rounded up to whole dates; early stopping after 50 rounds on the weighted multi_logloss of the inner
     block; the validation Dataset built with reference= the inner-training Dataset; kept at its best iteration, not
     refit; calibration = multinomial LogisticRegression C = 1e4, lbfgs, max_iter 1000, tol 1e-6 on the booster's 3
     raw scores fitted on the inner block with weights w). Threads per P5 (processes x threads <= 8).
   - mu_long_k and mu_short_k: weighted means of n_long and n_short over the fold's training rows with y = k (P3.5;
     LGBM: all training rows, inner-train and inner-validation). Define what happens if a class has no training row
     (a READING; most conservative).
   - Predictions at every grid minute of every evaluation date (features exist at every minute); EV rule; the
     simulation per evaluation date with that date's fold model: flat, entry_ok, fewer than 20 entries, enter long if
     EV_long > max(EV_short, 0), short if EV_short > max(EV_long, 0), exact tie -> no trade; outcome from the label
     table's per-side fields; s_made false -> the entry is not made and counted; next decision = the first grid
     minute at or after the exit fill time; X_D = sum of nets of trades entered on D; X_D = 0 on dates without a trade
     (excluded dates included).
   - P6.2 statistics with moments() and t_stat() of the program, trade counts, trades per date, mean net per trade,
     hit rate, share of dates with a trade, per-fold, per-quarter and per-month sums, volatility-tercile means (P8 G5
     (d) ranks by sigma_ZM(D) from the features _day json; ties by date), and the reported-only items (rho of chosen
     EV and realised net; the mid-sign hit rate if the label table supplies a mid move, else "not available"; the
     top-decile EV mean). Failed-fit rule of P5.
2. run_search33.py: run a list of P7.1 IDs; process pools under the thread cap (LOGIT up to 8 single-thread
   processes; LGBM 2 x 4 threads or 1 x 8; never more than 8 threads in all); DONE markers per (config, fold) and per
   config; resume; seeds and library versions logged; nice 10; --root (the real DERIVED tree or a proof tree);
   --probe CONFIG_IDS to time fold 6 alone; --max-procs.
3. tests/test_search33.py on small synthetic tables generated in the test: fold arithmetic and embargo; LT3 (no
   training row from the evaluation fold or its embargo; scaler, calibrator and mu_k from training rows only; early
   stopping on the inner block only; LightGBM bins from inner-training rows only via reference=; weights per date);
   the EV rule incl. exact ties; the simulator (one position, the cap of 20, next decision after the exit, entries not
   made); determinism (identical outputs on a rerun); resume after a killed fold.

## Boundaries
P8 selection, the synthetic proof generator and the registry belong to other workers. Real label tables do not
exist before the registration: test only on synthetic tables. Never read reports/stage_e33_briefs/work/implB/.

## Return
Paths, a summary of at most 200 words (include measured seconds per LOGIT and LGBM fit on a production-size synthetic
table: 170,000 rows x 59 features, 3 classes), what is unfinished, and
reports/stage_e33_briefs/work/SearchCoder_readings.md.
