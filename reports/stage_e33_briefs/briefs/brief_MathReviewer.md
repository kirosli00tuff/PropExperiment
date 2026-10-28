# Brief: MathReviewer (Stage E.33 B7; Fable 5.1 xhigh, model confirmed from the transcript)

You are an independent reviewer for the E.33 lead, in a fresh context. You wrote none of this code. Do not spawn
workers; do not ask questions; decide conservatively and say so.

## Objective (prompt B7, second bullet)
1. Recompute by hand, from raw records, 10 feature values and 10 labels on trade dates of your own choice, and compare
   them with both implementations: Coder-A (production) and Coder-B (independent).
2. Recompute the B5 threshold arithmetic.

## 1. Hand recomputation
- Choose your dates among the 20 B3 dates, where both implementations' tables exist or are being built (the rule is
  in reports/stage_e33_STATE.md, "B3 dates rule"; cal33.oof_dates() gives the OOF list). Choose the decision times
  yourself and record why.
- "By hand" means a short, explicit script of your own that reads raw records through the loader
  reports/stage_e33_briefs/work/pipeline/data33.py (load_zm, load_mbp1, definitions; every read goes through
  guard33) and computes each value step by step from the protocol text. You may use mbo_book31.Book
  (reports/stage_e31_briefs/work/pilot/) for the ZM book, since the protocol names it. Do not import or copy any
  feature or label code from pipeline/ (feat33, lab33, build_*) or implB/. Print the intermediate quantities (mids,
  window sums, the OLS fit, the touch prices at t + L and t + h + L, the barrier crossing) to your work file, not to
  your context.
- Cover: at least one feature from each block C, F1, F2, F3, F4, including the hard ones (seasoned depth F3.7 or
  F3.8, an OFI with its trailing 20-date reference F3.1 or F2.8, the F1.3 residual with its 10-date OLS, F4.11/F4.12
  burst, the open-time-axis window across 08:30); and labels of both types (FH and TB), at least one TB with a barrier
  hit, the exclusion flags (entry_ok, row_ok) of at least two minutes near a release window or a limit or roll
  condition, and the P3.7 weight of at least two rows.
- Compare with Coder-A's tables (features: /mnt/large-storage/market_data/PropExperiment/derived/e33/features/<sha>/,
  labels: .../derived/e33/labels/<sha>/<LABEL>/; the newest sha folder whose manifest lists the current code) and
  Coder-B's (.../derived/e33/implB/features/<sha>/, .../implB/labels/<LABEL>/). If A's labels for your dates are not
  built yet, wait (poll every few minutes up to 40 minutes), then report what was available.
- Protocol tolerance G7: features within 1e-9 relative (1e-12 absolute near 0); labels and classes exactly.
- No outcomes before registration (reports/stage_e33_protocol_readings.md R-L2): label VALUES appear only inside these
  equality checks. Never compute or report a class share, mean net or any other statistic of labels.

## 2. B5 threshold arithmetic
Recompute independently: p7_final.py's thresholds at N = 838 (SR0 0.1137, G3 0.1724, b_test 0.164882, G4 0.2007,
T_disc 796, T_test 870; reports/stage_e32_briefs/protocol/p7_final.py and p7_final_budget300.md); P4.2's binomial
figures (P(at least 2 of 20) = 0.26 at a rate of 0.05; P(at least 14 of 20) = 0.91 at a per-seed power of 0.8); the
analytic rates 300 x P(Z > 5.66) and 300 x P(Z > 4.86); 1/sqrt(796) = 0.0354; and the plant calibration of
reports/stage_e33_briefs/work/ProofCoder_calibration.json against reports/stage_e33_briefs/work/pipeline/synth33.py
(the oracle's class probabilities and class means, the beta found, its precision).

## Standard
The frozen protocol reports/stage_e32_discovery_protocol.md (0.3, P1.4, P3, P4, P4.2, P7.2) and
reports/stage_e33_briefs/INTERFACE.md. reports/stage_e33_protocol_readings.md (DRAFT) and the coders' readings files
show the readings each side took; judge each against the protocol text.

## Output
reports/stage_e33_briefs/review/MathReview.md, written as you go: a table of the 10 features and 10 labels (date,
time, ID, your value, A's value, B's value, agree or not, and for each disagreement which side matches the protocol
and why), the arithmetic checks, and findings graded BLOCKING, SHOULD FIX or NOTE with file:line where code is at
fault. Work files under reports/stage_e33_briefs/review/math_work/. Compute: nice 10, one process, `free -m` first.
Return: the path, the counts (features agreeing with A, with B; labels likewise; findings by grade) and a summary of
at most 200 words.
