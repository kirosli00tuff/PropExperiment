# Brief: HarnessReviewer-FableXHigh (Stage E.5 Task A3, independent review of the harness v5 change)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" paragraph first (read
files by section; short command output). Times PDT. You are a worker: you do not spawn workers. You wrote none of this
change; your job is to find what is wrong with it.

## Objective (one)
Review the uncommitted harness v5 change set (`git diff` against HEAD plus the new untracked files named below) against
its specification and the frozen texts, and classify every finding BLOCKING, SHOULD FIX or NOTE with file and line.

## What changed (read the diff, not the whole files)
- rules/sessions.py: 2019-2023 Topstep holiday rows derived by Rule H-1 (plan 3a), the 2019-2023 lead, the unsettled list.
- screening/stage_e_verdict.py (new): the confirmation verdicts (plan 3b).
- data/config.py and data/pull_step2.py: the E.5 spend block and the gate's reading of it (plan 3c, lead ruling L-E5-1).
- tests/ (new and changed test files; `git status --short tests/`).
- The builder's report: reports/stage_e5_harness_change.md. The spec: reports/stage_e5_harness_plan.md (sections 3, 4).
- The replay: reports/stage_e5_replay_k4.md and reports/stage_e5_replay_k5.md (K4's and K5's research runs under the
  working tree vs E.4's records; the lead ran them).

## Check, at least
1. The holiday rule: that Rule H-1 applied to 2024-2026 reproduces the published rows except the four named exceptions
   (recompute it yourself from data/cme_calendar.py HOLIDAYS and rules/sessions.py's published rows); that the
   2019-2023 rows equal the rule's output minus the unsettled dates; that the unsettled list is complete (every July 3,
   every non-ordinary equity entry); that nothing changes day_rule for any group on any date from 2024-01-01 on; the
   effect on the 15 FX dates of audit E.4c N-1 and on energy and metals early-halt dates 2019-2023.
2. Every verdict function against docs/NULL_CRITERIA_E.md section 3 (lines 59-92), sections 1, 6, 7, the D.1f text
   reports/stage_d1f_confirmation_list.md 3.1-3.4 (lines 424-497) and the pinned program functions
   (strategy/research/_d1f_decisions.py 155-280, strategy/research/_d1b_accounting.py 73-110,
   funnel/multiple_comparisons.py, funnel/null_generator.py 176 on): the unit; the bootstrap (seed = 20260923 + list
   ordinal, a fresh generator per trial, B = 10,000, mean block 5, np.quantile 0.95, SE ddof 0, the p formula); null
   power at eps_X; the inactivity (< 30 trips), zero-trip and SE_boot = 0 branches; Holm at K = 9 (V14 b) through
   screening/stage_e_stats.holm_tier_a; DSR at the list's program N with moments on the trial's own series and the V14 (c)
   variance switch (docs/DECISIONS.md V14); daily t > 3.0; PBO on 8 contiguous blocks with ruling L-E5-3's switch and the
   union-date alignment; the source-overlap gate; the inconclusive-by-design and OC-H exclusions in the null statement;
   V14 (a)'s "edge candidate, composite pending" (never "edge" alone); the refusals. Independently re-derive at least two
   figures of the known-answer tests.
3. That the restated functions equal D.1f's (the equality tests exist and are real, not tautological).
4. data/config.py: the E.5 block (session id "stage-E.5-2026-09-27", both caps 0.00), the E.2b block and every other
   value byte-identical; data/pull_step2.py: only the gate and its messages changed; with the caps at 0.00 `--buy`
   refuses before any vendor call; no chunk, seal, byte-check, quote-writer or path change.
5. The replay reports: every file matches E.4's apart from harness_sha256, created_utc and the trip files'
   record_sha256.
6. Anything the change set touches outside the five allowed paths, any new import of unfrozen code from a harness
   module, any TopstepX reference, any Databento key handling.

## Output
reports/stage_e5_harness_review.md: a table of findings (id, class, file:line, what is wrong, why it matters, suggested
fix), then a short section per check above saying what you verified and how (commands or recomputations, with their
results). You may write scratch scripts under /tmp/claude-1000/ or reports/stage_e5_briefs/review_scratch/. Run targeted
tests if useful (`uv run pytest -q tests/<file>`), not the full suite.

## Boundaries
Read-only on every repository file except your report and your scratch directory. No commits, no manifest build, no
Stage E entry point on real data, no vendor call, no web.

## Return
The report path, a summary of at most 200 words (counts per class and each BLOCKING and SHOULD FIX in one line), and
anything you could not check.
