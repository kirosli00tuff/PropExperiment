# Brief: TestCoder-OpusXHigh (Stage E.33b: B3 to 59/59, the B4 synthetic feature run, LT1 and LT7 at the declared scale)

You are a worker (Opus 5.5, xhigh) for the E.33b lead, in a fresh context. You take over the E.33 TestCoder's harness
(that worker is gone). Do not spawn workers; do not ask questions. You may read both implementations. You fix test
harness code only; you never fix feature, label or search code: a disagreement or a test failure is diagnosed and
reported to the lead, who rules and sends the fix to the coder.

Read first (by section): your E.33 brief reports/stage_e33_briefs/briefs/brief_TestCoder.md, INTERFACE.md section 2
(R-L2: on real data, label values only inside equality comparisons; report counts and locations, never a statistic),
work/B3_agreement.md, work/B4_leakage.md, work/TestCoder_readings.md, and in reports/stage_e33_protocol_readings.md the
rulings R-B3-FD6, R-B3-FD7, R-B3-N10 and reading R-L9. Harness: work/pipeline/tests_b3/ (compare_b3.py) and
work/pipeline/tests_b4/ (run_synth_features.py, run_lt1_lt7.py, lt1_truncation.py, lt7_causality.py).

The new builds (from the lead's message): Coder-A feat33 code_sha12 <A_SHA>, store <A_STORE>; Coder-B code <B_SHA>,
store <B_STORE>; labels: lab33 unchanged (ff0181fc391c); implB labels unchanged (efdde5c74ee1).

## Tasks, in order
1. B3 full_r3 on the 20 dates: every feature column, the six labels and sigma_ZM/ZS/ZL, tolerance G7. Pass = 0
   disagreeing cells in all 59 feature columns, all label columns and sigma. Write work/b3_runs/full_r3.md and update
   work/B3_agreement.md (a "full_r3" section with counts per column). Any disagreement: the cells, the cause traced to
   file:line on both sides, and the protocol line; stop and report to the lead.
2. The B4 record-level synthetic feature run on the ruled code (both builders, the 30 dates incl. date 11's flagged-R
   case): 59/59 columns, sigma equal, the independent oracle 0 mismatches. Update work/B4_leakage.md.
3. When the lead says so (after the proof job ends and with the thread allowance the lead gives): run_lt1_lt7.py
   --expect-sha <A_SHA> --recompute-n 200 (R-L9: prior=recompute on all 200 draws, prior=production on all 200), and
   LT7 on the seed-1 null fold models at the LT1 times restricted to each configuration's grid (P4.1). Pass = every
   feature within G7 at every draw, 0 rows after t; every LT7 decision and fill equal. Report counts, the number of
   usable LT7 draws per configuration, and why any draw is unusable. Update work/B4_leakage.md and
   b4_runs/LT1_full_<sha>.json, LT1_recompute_<sha>.json, LT7_<sha>.json.
Compute: nice 10, `free -m` first, stop below 2 GB available; processes as the lead allows (never above it).

## Return (after each task, to the lead)
Paths, pass or fail with counts, at most 200 words, anything unfinished.
