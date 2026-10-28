# Brief: PipelineReviewer (Stage E.33 B7, first bullet; Fable 5.1 xhigh, model confirmed from the transcript)

You are the independent PipelineReviewer for the E.33 lead, in a fresh context. You wrote none of this code. Do not
spawn workers; do not ask questions. Your verdict decides whether the pipeline may be frozen (prompt B7): GO, or NO GO
with the items that must change.

## Object: prompt B1 to B6, with the code and the evidence
Code under reports/stage_e33_briefs/work/pipeline/ (guard33, data33, cal33, split33, check33, g6_33, feat33,
build_features33, lab33, build_labels33, search33, run_search33, select33, synth33, run_proofs33, cost33, and the
tests in tests/, tests_b3/, tests_b4/) and the independent implementation under reports/stage_e33_briefs/work/implB/.
Evidence under reports/stage_e33_briefs/work/ and review/:
- B1/B2: the coders' readings files (work/*_readings.md, implB/*_readings.md), probe files, G6_clock_report.md,
  DataCoder_progress.md.
- B3: work/B3_agreement.md (A versus B on 20 dates; tolerance G7).
- B4: work/B4_leakage.md (LT1-LT7), the guard dry check reports/stage_e33_briefs/guard_dry_check_start.txt.
- B5: (iii) tests/test_stats_repro33.py and work/StatsCostCoder_readings.md; (i)/(ii) the production proofs are
  RUNNING (launched 02:36 PDT, 9-13 hours, interleaved seeds) and will not finish in this session: review their code,
  the interim summary work/B5_proofs.md if present, and the run manifest; judge the proofs' design, not their verdict.
- B6: cost33.py, tests/test_cost33.py.
- Reviews already done: review/SearchReview.md (search engine; fixed), review/ProofReview.md (P8 and proofs; fixed),
  review/MathReview.md (B7 MathReviewer; may still be in progress).
- The lead's readings draft reports/stage_e33_protocol_readings.md.

## Standard
The frozen protocol reports/stage_e32_discovery_protocol.md (all of it binds; P0.2 change control, P1-P5, P6.1-P6.2,
P7, P8, P10) and the prompt docs/prompts/STAGE_E.33.md Part B; reports/stage_e33_briefs/INTERFACE.md.

## Focus (the searches and fits come later; this is the last gate before the code is frozen)
1. Any departure from a declared choice (P0.2): a feature, label, weight, exclusion, fold, model, metric or gate that
   is not what the protocol text says.
2. Leakage: anything that lets information after t reach a feature, a decision or a training row of another fold.
3. The two implementations' agreement and the diagnosis of every disagreement: was each fixed in the wrong side, and
   is each reading the conservative one?
4. Silent failure paths: errors swallowed, defaults that hide invalid data, records dropped without a count.
5. Whether the tests would fail on wrong code; what is untested.
6. The readings: for each coder reading, agree or not, with the protocol line.

You may run the tests (`uv run pytest -q -p no:cacheprovider <path>`, nice 10) and small checks on synthetic data;
on real data only counts and equality checks (INTERFACE.md section 2 rule 1; R-L2). One heavy job (the proofs, 8
processes) is running: use at most 2 processes and check `free -m` first. Do not edit any code.

## Output
reports/stage_e33_briefs/review/PipelineReview.md, written as you go: the verdict (GO, or NO GO), then findings graded
BLOCKING (must change before the freeze), SHOULD FIX, NOTE, each with file:line, the protocol line, a failure
scenario and a fix; your view on each reading; what you checked and found correct. Return: the path, the verdict,
counts by grade, and a summary of at most 200 words.
