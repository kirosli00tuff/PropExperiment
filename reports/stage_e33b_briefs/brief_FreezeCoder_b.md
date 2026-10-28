# Brief: FreezeCoder-OpusXHigh (Stage E.33b, PipelineReview SF2: the pipeline freeze list)

You are a worker (Opus 5.5, xhigh) for the E.33b lead, in a fresh context. Do not spawn workers; do not ask questions.
Do not edit any pipeline code. You write the tool that freezes the pipeline; the lead runs the real freeze later.

## Standard
Prompt docs/prompts/STAGE_E.33.md B7: "freeze the pipeline: a sha256 list of every code file, config and environment
lock (uv.lock). From here on the pipeline does not change." Protocol P0.2 (the readings file's sha256 is a line of the
freeze list), P5 ("No package is added after the pipeline freeze (uv.lock is hashed)"), P7.1 (the pipeline sha256 in
every C1 row: reports/stage_e33_briefs/work/lead/c1_freeze.py takes the sha256 of the freeze list file).
PipelineReview SF2 (reports/stage_e33_briefs/review/PipelineReview.md lines 76-91): the list must also cover code the
pipeline executes outside pipeline/ (screening/stage_e_verdict.py, funnel/multiple_comparisons.py,
reports/stage_e32_briefs/protocol/p7_final.py and p7_thresholds.py, the E.31 modules under
reports/stage_e31_briefs/work/pilot/ that cal33/data33/feat33/lab33/cost33 import, the program calendars under data/
and any other data or config file the pipeline reads: release CSVs, the E.28 fee file, etc.). R-L3 in
reports/stage_e33_protocol_readings.md: at the freeze, every file of the proof run manifest
(/mnt/large-storage/market_data/PropExperiment/derived/e33/proofs/run_manifest.json) must have the same sha256 in the list.

## Objective
Write reports/stage_e33_briefs/work/lead/freeze33.py with tests (reports/stage_e33_briefs/work/lead/test_freeze33.py):
- `build --out <file>`: find the files by MEASURING, not only by listing: import every pipeline entry point
  (pipeline/*.py modules incl. build_features33, build_labels33, run_search33, search33, select33, synth33,
  run_proofs33, cost33, split33, check33, g6_33, guard33, data33, cal33) in a subprocess without running main and
  record every loaded module file inside the repo; add data and config files the code opens (find them by reading
  the path constants; list how each was found); add uv.lock, pyproject.toml, .python-version if present, the
  protocol, the readings file. implB/ and tests are listed in a separate "verification evidence" section of the
  same file (hashed, not executed by the search). Output in `sha256sum` format, sorted by path, repo-relative, plus a
  header of comment lines (python and library versions: numpy, pandas, pyarrow, scikit-learn, lightgbm, scipy).
  The pipeline sha256 is the sha256 of that file.
- `verify --freeze <file>`: recompute every line; print the differing paths; exit non-zero on any difference.
- `check-proofs --freeze <file>`: the R-L3 check against the proof run manifest.
- Dry run now to reports/stage_e33b_briefs/freeze_dryrun.sha256 (NOT the final path reports/stage_e33_pipeline_freeze.sha256)
  and report the file count by section and any file you were unsure about.
Light work only (no heavy compute; a proof job uses 8 processes until about 10:00 PDT).

## Return
Paths, the dry-run counts, test counts, open questions for the lead, a summary of at most 200 words.
