# Brief: HarnessReviewer-FableXHigh (Stage E.4, Task H3)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. You wrote none of the change under review.
Read CLAUDE.md's "Context hygiene" section first. Times in PDT (America/Vancouver).

## Objective (one)
An independent, adversarial review of the Stage E harness change for bug C-1 and the added trip list
(docs/DECISIONS.md V13 (a), lines 229-243: "Nothing else in the harness changes").

## Inputs
- The diff: `git diff HEAD -- screening/ tests/` and the new untracked test files (`git status --short`).
  The committed tree (HEAD) is the frozen harness cf939270...; the working tree holds the change and a
  manifest rebuilt in place by the lead (reports/stage_e2b_harness_freeze.json, uncommitted).
- The fixer's report: reports/stage_e4_harness_fix.md.
- The regression: reports/stage_e4_k2_regression.md and the replay records in
  reports/stage_e4_k2_regression/ (44 member records, their *_trips.json files, the cluster record),
  against E.3's records in reports/stage_e3_k2_screen/ (never edit either directory).
- Background: reports/E.3_RETURN.md lines 200-223 (C-1) and screening/stage_e_start_dates.py (its
  `_runner()` and the eight raises).

## What to check (each is required)
1. Scope: the diff touches only refusal routing and the added trip file. List every changed hunk and
   classify it. Any change to fills, costs, the account model, the screen, tiers, coverage, labels or the
   record files' format or content is BLOCKING. Only screening/stage_e_runner.py,
   screening/stage_e_start_dates.py and test files may change; anything else is BLOCKING.
2. C-1: every one of the eight raises in stage_e_start_dates.py and every runner refusal
   (RunnerRefusal and subclasses, StageEBarRefusal where the runner catches it) is caught by name under
   both launches: `python -m screening.stage_e_runner` and an import of screening.stage_e_runner. Show it
   by reasoning over module identity AND by running tests (or your own subprocess probe under tmp paths,
   never writing under reports/ or data/). Consider every other way the runner could be loaded twice
   (runpy, `python screening/stage_e_runner.py`, imports from stage_e_start_dates, the test suite).
3. The trip list: every TripRecord is written with the fields the brief names, exact cents, the record's
   sha256 (of the exact bytes written), write-once; its per-date net sums equal the record's
   daily_net_usd and its count equals n_trips; it reveals nothing outside the window being run (no trips,
   dates or bar data from outside the window; no paths or data beyond the record's own).
4. The regression proves numerical identity: 44/44 records match E.3 field by field with only
   harness_sha256 and created_utc differing, the cluster record (tiers) matches, and every trip list sums
   to its series. Re-check a sample yourself (at least 5 records, chosen by you, plus the cluster record)
   with your own code.
5. The tests: the subprocess test really launches `python -m` and would fail on the frozen runner (check
   the RED evidence or reproduce it, for example by running the test body against a copy of HEAD's
   runner in a tmp directory; never stash or check out in the repository); no test is vacuous.
6. The manifest (uncommitted): `git diff HEAD -- reports/stage_e2b_harness_freeze.json` changes only the
   entries of the changed or added files. Do NOT run `python -m screening.harness_freeze build`.

## Output
reports/stage_e4_harness_review.md: each finding graded BLOCKING, SHOULD FIX or NOTE, with file and
line, the evidence and a suggested fix; then a verdict line per check 1-6.

## Boundaries
Read-only on the repository except your report and scratch files under /tmp/claude-1000/e4_h3/
(create it). Do not edit code, tests, manifests, records, briefs or docs. No commits, no git stash, no
checkout. Do not run the runner on real data; do not read bar files. Stage E entry points take a fresh
PYTHONPYCACHEPREFIX outside the repository; pytest runs without it. Other workers are coding K4 members
under strategy/members/k4/ and tests/test_e4_k4_members*.py at the same time: ignore those files. No web.

## Return
The report path, a summary of at most 200 words with the counts per grade, and anything unfinished.
