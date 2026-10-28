# Brief: PipelineReviewer-FableXHigh (Stage E.33b, B7 first bullet, continued; Fable xhigh, model confirmed from transcript)

You are the independent PipelineReviewer for the E.33b lead, in a fresh context. You wrote none of this code. Do not
spawn workers; do not ask questions; do not edit any code. Your final verdict (GO or NO GO) decides whether the
pipeline may be frozen (prompt B7).

The E.33 PipelineReviewer (also Fable) was cut by usage limits and left a provisional NOT YET:
reports/stage_e33_briefs/review/PipelineReview.md (0 BLOCKING, 3 SHOULD FIX, 10 NOTE). Read it first; take its findings
as your starting point and do not redo what it checked unless the file changed since (it lists sha256 at 07:02).
Its original brief: reports/stage_e33_briefs/briefs/brief_PipelineReviewer.md (object, standard, focus 1-6, the R-L2
rule: on real data only counts, hashes and equality checks).

## Phase 1 (now)
1. "Not reached": read the modules and evidence its last section lists: data33.py, split33.py, check33.py, g6_33.py,
   build_labels33.py, build_features33.py, synth33.py and run_proofs33.py beyond ProofReview's coverage, cost33.py
   (the E.31 per-fill agreement claim in work/StatsCostCoder_readings.md), test_stats_repro33.py's cited digits (spot
   check), implB build_featB.py and labB*.py (B's labels agree exactly; read for silent-failure paths).
2. Rerun the tests nobody reran after the last code change: pipeline/tests/test_search33.py (LT3 evidence; about 150
   s), test_guard33, test_data33, test_synth33, test_run_proofs33, tests_b4 test_lt3/lt5/lt6. One process, nice 10,
   `free -m` first; a proof job (8 processes) is running until about 10:00 PDT.
3. Check R-L3's hash condition again: every file of the proof run manifest
   (/mnt/large-storage/market_data/PropExperiment/derived/e33/proofs/run_manifest.json) is byte-identical to the
   current file.
4. Your view on the lead's new rulings R-B3-FD6, R-B3-FD7, R-B3-N10 in reports/stage_e33_protocol_readings.md.
Write reports/stage_e33_briefs/review/PipelineReview_b.md as you go (same grading: BLOCKING, SHOULD FIX, NOTE, each with
file:line, protocol line, failure scenario, fix). Return the path, counts by grade, an interim verdict and a summary of
at most 200 words.

## Phase 2 (the lead will send it when ready)
The fix diffs (Coder-A FD7, Coder-B FD6 and N10), the B3 rerun to 59/59, the B4 synthetic feature run, LT1 and LT7 at
scale, the final proof summary (40 seeds), the final readings file (SF1) and the freeze list (SF2). Then GO or NO GO.
