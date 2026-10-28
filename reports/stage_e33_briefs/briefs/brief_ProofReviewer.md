# Brief: ProofReviewer (Stage E.33, pre-proof review of P8 and the synthetic proofs; Fable 5.1 xhigh)

You are an independent reviewer for the E.33 lead, in a fresh context. You wrote none of this code. Do not spawn
workers; do not ask questions. The 40 production proof searches (P4.2; 4,800 fits, about 9-13 hours) start once the
search engine's last fixes land; a defect in the code below found after they start forces a rerun, so find it now.
The search engine itself (search33.py, run_search33.py) was reviewed separately (review/SearchReview.md); read that
review's summary and do not repeat it.

## Object (reports/stage_e33_briefs/work/pipeline/)
select33.py (P8), synth33.py (the P4.2 synthetic generator, null and planted), run_proofs33.py (the proof runner and
its summary), their tests (tests/test_select33.py, test_synth33.py, test_run_proofs33.py), the author's readings
reports/stage_e33_briefs/work/ProofCoder_readings.md (decide nothing; give your view on each, especially Q3, the Tier
B start point) and the calibration record reports/stage_e33_briefs/work/ProofCoder_calibration.json.

## Standard
The frozen protocol reports/stage_e32_discovery_protocol.md: 0.3 (statistics conventions), P3.3-P3.5, P3.8, P4.2,
P6.1-P6.3, P7, P8, P10; reports/stage_e32_briefs/protocol/p7_final.py; screening/stage_e_verdict.py (moments, t_stat,
pbo); funnel/multiple_comparisons.py (deflated_sharpe_ratio); reports/stage_e33_protocol_readings.md (DRAFT; R-L3 and
R-L4 concern the proofs); reports/stage_e33_briefs/INTERFACE.md.

## Check at least
1. P8 exactly: G1-G5 (the DSR call's arguments: N, V = 1/(T_disc - 1), T, the configuration's own skewness and raw
   kurtosis, "> 0.95"; G4's se formula and the unrounded b_test at N; G5 (a) the 13 quarters with the first without
   burn-in dates, (b), (c) leave-one-month-out t with the population SD, (d) terciles 1-265, 266-530, 531-796 by
   sigma_ZM(D) with ties by date); failed configurations fail G1; the funnel; the total-order ranking and its
   tie-breaks; the Tier A walk; the Tier B walk and Q3; constant series.
2. The generator: real OOF dates, real grid G_h(D) and real calendar exclusions; F15 and T30 labels and per-side
   outcomes built as P3.3, P3.4 and P3.8 say on the synthetic touch path; under the null no feature carries any
   information about the future path (look for any feature computed from a window that reaches past t, or any
   shared random draw between features and future increments); under the plant only F3_4 carries signal; the oracle
   (P3.5 with true class probabilities and class means, f, the dead zone, the P3.8 simulation) and the calibration to
   a daily Sharpe of 0.35 at F15; determinism per seed.
3. The runner: seeds 1-20 null and 101-120 planted, each once per code hash (its run manifest), 20 configurations
   S5 x {F15, T30} x 10 grid points through the engine, selection at N = 838 with the production thresholds, the seed-1
   fold models kept for LT7; the summary's pass and fail rules (null fails at >= 2 seeds with Tier A non-empty;
   planted per R-L4), the 400-Sharpe SD against 1/sqrt(796), and that a failed configuration is visible in the
   summary (it must not pass as an empty Tier A).
4. Whether the tests would fail on wrong code.

You may run the tests and small synthetic probes (non-production seeds only, e.g. 9201-9210, reduced sizes, at most 2
processes, nice 10) under /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/86e80bc3-d62a-42e1-b5fd-5c881ccf8b54/scratchpad/proofreview/.
Never run a production seed. Do not edit any pipeline file.

## Output
reports/stage_e33_briefs/review/ProofReview.md, written as you go: findings graded BLOCKING (would invalidate the
proofs or departs from a declared choice), SHOULD FIX, NOTE, each with file:line, the protocol line, a failure
scenario and a fix; plus what you checked and found correct. Finish within about 40 minutes. Return: the path, counts
by grade, and a summary of at most 200 words.
