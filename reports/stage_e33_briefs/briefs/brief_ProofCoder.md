# Brief: ProofCoder-OpusXHigh (Stage E.33 B5 code: P8 selection, synthetic proof generator, proof runner)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue. The user asked for extreme care with the mathematics and the ML implementation.

## Objective
Write and test (1) select33.py, the mechanical selection rule P8; (2) synth33.py, the synthetic minute-row generator
of P4.2 (null and planted); (3) run_proofs33.py, the runner of the 40 proof searches. The lead launches the
production proof run; you test on non-production seeds only.

## Read first (by section)
- reports/stage_e33_briefs/INTERFACE.md (all; section 2 rules bind you)
- Protocol reports/stage_e32_discovery_protocol.md: 0.2 (P8 coded and unit-tested before the first real fit), 0.3,
  0.4, P3.3-P3.5, P3.8, P4.2 (all), P5 (compute bullets), P6.1-P6.3, P7 (all), P8 (all), P10
- reports/stage_e32_briefs/protocol/p7_final.py and p7_final_budget300.md (thresholds at N; b_test unrounded)
- screening/stage_e_verdict.py moments(), t_stat(), pbo(), dsr(); funnel/multiple_comparisons.py
  deflated_sharpe_ratio(), expected_max_sharpe(), probability_of_backtest_overfitting()
- reports/stage_e33_briefs/work/pipeline/search33.py and run_search33.py (SearchCoder's engine; read its docstrings
  and CLI; it may still be in progress; poll) and cal33.py (DataCoder's calendar: oof_dates, excluded, releases,
  ct_ns)
- reports/stage_e32_data_facts.md sections 1.3-1.5, 3 (rates for the generator); P0.4's standard numbers

## Deliverables (reports/stage_e33_briefs/work/pipeline/)
1. select33.py (P8 exactly): inputs = the daily series (796 values) and P6.2 statistics of each configuration
   (failed configurations included, failing G1); G1-G5 as written (G3 with funnel.multiple_comparisons.
   deflated_sharpe_ratio at N, V = 1/(T_disc - 1), T = T_disc, the configuration's own skewness and raw kurtosis from
   moments(), "> 0.95"; G4 with the se formula and b_test from p7_final.py at N, unrounded; G5 (a) 13 calendar quarters
   Dec-Feb, Mar-May, Jun-Aug, Sep-Nov, the first without burn-in dates, (b), (c) leave-one-month-out t >= 2.5 with
   t_stat()'s population SD, (d) sigma_ZM(D) terciles ranks 1-265, 266-530, 531-796, ties by date); the funnel (each
   gate alone and in order G1..G5); the total-order ranking (SR_d rounded to 4 decimals with Python round(), then
   fewer trades per date, LOGIT before LGBM, lower set index, shorter horizon with FH before TB at equal h, earlier
   grid point); the Tier A walk (correlation <= 0.70, at most 3) and the Tier B walk (gates ignored, failed or
   constant series skipped, fill rule when fewer than 2 qualify, correlations reported). Reporting helpers that are
   never gates (D1 of the prompt): PBO via screening.stage_e_verdict.pbo; BH FDR and Holm on one-sided p-values from
   the daily t (state the reading); the P7.2 reference z thresholds. Unit tests tests/test_select33.py on synthetic
   series: each gate's boundary (just passing, just failing), the ranking tie-breaks, the walks, the funnel counts,
   failed and constant series, N other than 838 (p7_final.py recomputation path).
2. synth33.py (P4.2 "Search proofs"): per seed, synthetic tables in the INTERFACE.md 4.1 and 4.2 schemas for the 796
   real OOF dates on the real grid G_h(D) and the real P1.4 and P3.6 calendar exclusions (rules 1-4 from cal33; rule 5
   and 6 do not arise on a synthetic book: document), labels F15 and T30 only, the 59 S5 columns, and _day json with a
   synthetic sigma_ZM(D) path (the 20 burn-in dates as history). Mids, touch prices and labels generated to match the
   data facts' rates (ZM tick 0.10, sigma_1m about 3.15 ticks with day-to-day variation, a 1-tick spread most of the
   time; document the choices). Labels and the per-side outcome fields follow P3.3-P3.4 and P3.8 on the synthetic
   touch path (state how L is treated at minute resolution). Null: no feature carries signal (F4-type features may be
   computed from the synthetic past path, which carries no signal in a driftless walk; the others as autocorrelated
   noise). Planted: one F3 feature (name it) shifts the drift of the next minutes; its size is calibrated so that the
   oracle (P3.5 with the generator's true class probabilities and class-conditional means, the P3.8 simulation, f,
   the dead zone) has a daily Sharpe of 0.35 net at F15 (expected over draws; document the calibration and its
   precision); the same plant serves T30. Deterministic per seed.
3. run_proofs33.py: seeds 1-20 (null) and 101-120 (planted), each a search over S5 x {F15, T30} x the 10 grid points
   (20 configurations, 120 fits) through search33's engine (--root DERIVED/proofs/seed<s>/), then select33 with the
   production thresholds at N = 838 and the Tier A walk. Resumable (DONE markers per seed, configuration and fold),
   nice 10, the thread cap of P5 (processes x threads <= 8), a --max-procs option, a summary writer:
   reports/stage_e33_briefs/work/B5_proofs.md with, per seed, Tier A members, the best configuration's SR_d, the
   funnel; null: the count of seeds with Tier A non-empty (the proof fails at 2 or more), the distribution of the best
   SR_d, the SD of the 400 null daily Sharpes (each centred on its configuration's mean) against 1/sqrt(796) =
   0.0354; planted: per seed the realised OOF Sharpe of the best planted configuration beside the oracle's, and the
   pass count (in at least 14 of the 20 planted seeds at least one configuration enters Tier A; also report, per
   configuration, in how many seeds it entered Tier A). The proofs keep the fold models of seed 1 (LT7 needs them).
4. A production-size synthetic table for the P5 probe under DERIVED/proofs/seed9000/ (not a proof seed), so the lead
   can time fold 6 of E33-S5F15L100E and E33-S5F15G3050 without touching real outcomes.

## Rules for seeds
Seeds 1-20 and 101-120 run only in the lead's production run, exactly once per pipeline hash (P4.2). Your tests use
other seeds (e.g. 9001-9010) and reduced sizes. Never run a production seed.

## Boundaries
Do not change search33.py (SearchCoder's; report any problem). No real labels exist; never read real outcomes.
Never read reports/stage_e33_briefs/work/implB/.

## Return
Paths, a summary of at most 200 words (the plant's size and calibration precision, a timing estimate for the 40
searches from a reduced test), what is unfinished, and reports/stage_e33_briefs/work/ProofCoder_readings.md.
