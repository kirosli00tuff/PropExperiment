# Brief: TestCoder-OpusXHigh (Stage E.33 B3 agreement and B4 leakage tests)

You are a worker (Opus 5.5, xhigh) for the E.33 lead. Do not spawn workers. Do not use AskUserQuestion: decide
conservatively, log it, continue. You are the one worker allowed to read both implementations (pipeline/ and implB/),
because you compare them; you never edit either. Disagreements go back to their owners through the lead.

## Objective 1: B3 agreement (prompt B3, protocol G7)
pipeline/tests_b3/compare_b3.py: compare Coder-A (DERIVED/features/<sha>/, DERIVED/labels/<sha>/) with Coder-B
(DERIVED/implB/features/, DERIVED/implB/labels/) on the 20 B3 dates (rule in reports/stage_e33_STATE.md):
features within 1e-9 relative (1e-12 absolute near 0; state the exact formula you use), labels, classes, every flag,
n_long, n_short, weights and per-side outcome fields exactly (weights: within 1e-12 relative, they are float means;
say so). Output: counts of agreeing and disagreeing cells per column and per date to
reports/stage_e33_briefs/work/B3_agreement.md, and the mismatching cells (date, i, column, A value, B value) to
DERIVED/b3/mismatches_<run>.parquet. Rule 1 of INTERFACE.md section 2: print and report counts and locations only;
never a statistic of label values (no class shares, no means of nets). For each disagreement class, trace the cause
by reading both codes against the protocol text and write a diagnosis (which implementation is wrong and the protocol
line), so the lead can send fixes; when the text is ambiguous, say so and give the most conservative reading.

## Objective 2: B4 leakage tests (protocol P4.1)
- LT1: 200 decision times drawn with seed 20261027 across the OOF dates (state the draw); recompute every feature from
  ALL input streams truncated at ts_recv <= t (build_features33 --cutoff-ns); every feature equals production within
  G7. Script + result file reports/stage_e33_briefs/work/LT1.md.
- LT2: for every row (all label types, the 20 B3 dates and any dates built so far) the span lies in [08:35, 13:13] on
  D, on one ZM front, clear of P3.6; no feature window reaches past t. Violations must be 0.
- LT3: run SearchCoder's fold-hygiene tests and add the check that the embargo (21 dates) exceeds every label's span
  and every feature look-back (the longest look-back in trade dates, derived from P4's definitions).
- LT4: unit tests that label starts, label ends and feature cut-offs come from ts_recv only, with ts_recv < ts_event
  records kept in ts_recv order (use hand-built streams).
- LT5: the leak canary: a deliberately leaked feature (the label shifted by one step) is caught by LT1-LT2 and gives
  an absurd CV score through search33 on synthetic data (or as a pure unit test); then removed.
- LT6: run DataCoder's guard tests; confirm one test per refused class of P1.2.
- LT7 (prepare now, run when the seed-1 null proof fold models exist): apply the seed-1 null search's fold models (20
  configurations, S5 x {F15, T30} x 10 grid points) to the REAL feature rows at the 200 LT1 times restricted to each
  configuration's grid; the entry decision recomputed from streams truncated at t equals the production decision, and
  the entry fill recomputed from streams truncated at the production fill time equals the production fill. Uses
  search33's load_fold_model / predict_proba / decide and lab33's entry-fill function. Real label VALUES are not
  needed and must not be computed or printed beyond the fill price equality check (counts only).
- Record-level synthetic streams (P4.2 first bullet): a synthetic MBO (ZM) and MBP-1 (ZS, ZL) stream for 30 trade
  dates with the data facts' tick sizes, spreads, volatility and event rates, fed through BOTH builders (A and B),
  with hand-built known-answer cases checked; report agreement on them too.
Put the tests in pipeline/tests_b4/ and the results in reports/stage_e33_briefs/work/B4_leakage.md (each LT: what
ran, counts, pass or fail).

## Read first
INTERFACE.md (all); protocol 0.3, P3, P4 (incl. P4.1, P4.2 first bullet), P5 (folds and models only as needed),
P6.1; the coders' readings files (reports/stage_e33_briefs/work/*_readings.md and implB/*_readings.md) after reading
the protocol, so you see each side's readings; the code under pipeline/ and implB/ by section.

## Compute
nice 10, at most 3 processes, `free -m` first (stop below 2 GB). LT1's 200 rebuilds can be slow: time 5 first and
report the projection before running all.

## Return
Paths, a summary of at most 200 words (B3 counts by family and the diagnosed causes; each LT's status), what is
unfinished, and reports/stage_e33_briefs/work/TestCoder_readings.md.
