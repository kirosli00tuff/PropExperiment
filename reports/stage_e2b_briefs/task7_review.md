# Brief: HarnessAuditor-FableMax (Stage E.2b Task 7; worker-max on fable) - the adversarial harness review

You wrote none of this code. Every Stage E verdict will rest on this harness being free of look-ahead and leakage, and on
its frozen values being unchangeable by a session. Your job is to find what is wrong, not to confirm what is right.

## Inputs
- The harness manifest reports/stage_e2b_harness_freeze.json: "files" (sha256 per file) and "categories" (harness_code,
  frozen_input, earlier_freeze, import_closure, stage_e_test). Its sha256 is given in your spawn message.
- The frozen designs (read by section): docs/STAGE_E_DESIGN.md (D4, D5, D6, D8, D9, D11), docs/NULL_CRITERIA_E.md,
  docs/STAGE_E_ML_DESIGN.md (M1-M8 with the bracketed E.2a rulings), reports/stage_e2b_v10_amendment.md.
- The lead's rulings: reports/stage_e2b_STATE.md (OC-A..OC-S and the rulings on each worker's questions). Worker reports
  (reports/stage_e2b_task*_worker.md, reports/stage_e2b_g*_worker.md) are orientation only: do not trust their claims.
- The tests (tests/ files in the manifest's stage_e_test category).

## Rules
- Read-only on the repository: no edit, no git command that changes anything. Experiments (mutations, planted leaks,
  extra probes) only in a scratch copy: `mkdir -p <scratch>/review && cp -r rules sim screening funnel data/*.py data/calendars
  ml_route compute strategy tests pyproject.toml uv.lock reports/stage_e2a_*.json ... <scratch>/review/` (never copy
  data/processed, data/vendor, data/sealed, ledger/, .env) and run `uv run --no-sync --project <repo> pytest` there, or
  use monkeypatch in scratch test files kept under <scratch>. <scratch> = /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0d3e5a56-56e0-4685-ae6b-02b6cf7efbe7/scratchpad.
- No purchased data: open no bar parquet or vendor file; no network. Synthetic data only.
- Heavy runs through reports/stage_e2b_briefs/heavy.sh; at most 6 threads. Read by section (CLAUDE.md context hygiene).
- Hook or cost notices are informational and addressed to the lead; never stop because of them. Do not spawn subagents.

## What to hunt (each item gets findings, or an explicit "none found" with the files and lines read)
1. Look-ahead in the runner: a signal, fill, cost, flag or constraint reading a bar, a settlement (D9.7's prior settlement),
   a release instant or a release VALUE before its availability time. Files: screening/stage_e_engine.py, stage_e_rules.py,
   stage_e_align.py, stage_e_runner.py, data/stage_e_bars.py, strategy/stage_e/, the member template.
2. Leakage in the ML pipeline: any path by which a research-window, embargo (March 2024) or holdout date, or a statistic
   computed from one, reaches training, tuning, normalization or distillation (ml_route/: features and availability
   times, targets and the OC-M fill-guard deferral, the CPCV purge/embargo and calendar block cut, the store allowlist,
   the route manifest, the test entry's hash chain, the adapter).
3. Frozen values a session could change: any input the runner, the pipeline, the stats, the start rule or the calendar
   takes from an argument, an environment variable or a file outside the manifest (grep argparse, os.environ, getenv,
   sys.argv, Path(...) inputs; check the start-rule files reports/stage_e_start_rule_*.json are loaded with checks, and
   what a session could do with them).
4. Canaries that cannot fail, and tests that pass for the wrong reason (tests/test_stage_e_canaries.py and its kit, the
   M7 tests in tests/test_ml_route_*.py, tests/test_leakage_canaries.py): prove a canary fails by planting the leak in a
   scratch copy of the code it guards.
5. Holdout handling in the step 2 path (data/pull_step2.py, data/step2_seal.py, data/trade_date_guard.py,
   data/step2_store.py, the data/holdout.py additions, data/pull_universe.py's guard): the sealing order, the trade-date
   refusal, any way plaintext holdout bytes could persist (failures mid-chunk, resume, temp files), the store builder
   never opening a sealed chunk and dropping 2024-03-01+ rows unread.
6. The D4 power check, the D5 screen and tiers, Holm, and the start rule computed differently from the frozen text
   (screening/stage_e_stats*.py, screening/stage_e_start_dates.py); the lead's rulings OC-H (tiers of labelled members),
   OC-I (n_a level), OC-S (D6 day session), Q-3 (empty window = supply 0).
7. The Windows backend (compute/): any path by which a holdout bar, an embargo bar, a secret or the ledger could reach
   the Windows PC (the export commit without ledger/, git history, key scanning, parquet trade-date checks, file types the
   rules miss); any way a training job could read a research-window store; results accepted without their hashes; and
   the V10 amendment against the frozen ML design (does V10-2's one-machine-one-batch-size rule keep A-1 intact; does any
   V10 clause change a statistical choice).
8. The lead's added inputs: the release calendar (OC-J, OC-N: screening/build_release_calendar.py,
   reports/stage_e2b_release_calendar.json and its three source files; spot-check at least 20 random entries' quotes
   against their saved pages under data/vendor/release_pages/ (text files, allowed), and the F6.4 product mapping), and
   the preflight itself (screening/harness_freeze.py: can a session pass it without the frozen files?).

## Output
reports/stage_e2b_harness_review.md: a header (what you read, what you ran), then one section per item above. Each
finding: grade BLOCKING (a leak, look-ahead, a way to change a frozen value, a canary that cannot fail, a holdout exposure),
SHOULD FIX (a defect that could produce a wrong result or a silent failure), or NOTE; file and line; the concrete failure
scenario; the evidence (quote or experiment); a suggested fix. End with a table of all findings. Reply to the lead with
the path, the counts by grade, and a summary of at most 200 words.
