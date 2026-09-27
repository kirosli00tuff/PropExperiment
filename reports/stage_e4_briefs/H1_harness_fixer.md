# Brief: HarnessFixer-OpusXHigh (Stage E.4, Task H1)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" and
"Compute limits" sections first (read files by section; keep command output short; `nice -n 10`).
Times in your report: PDT (America/Vancouver).

## Objective (one)
Fix harness bug C-1 in the Stage E runner and add a per-trial trip list to the runner's output, with
tests. Nothing else in the harness changes (docs/DECISIONS.md V13 (a), lines 229-243).

## Background (C-1)
reports/E.3_RETURN.md lines 200-223. Under `python -m screening.stage_e_runner` the runner module is
`__main__`. screening/stage_e_start_dates.py raises its refusals through `_runner()`
(`from screening import stage_e_runner`), a second copy of the module, so the `except (RunnerRefusal,
StageEBarRefusal)` in `__main__`'s `_research_statistics` (screening/stage_e_runner.py ~line 443) does
not match, and a refusal that tests/test_stage_e_runner.py (~line 94) expects to be recorded as
`power: not_run` escapes and crashes the run. All eight raises in stage_e_start_dates go through
`_runner()`.

## Output
(a) The C-1 fix: one class identity for every refusal, whichever way the runner is launched. Preferred
shape (the smallest): the runner's `if __name__ == "__main__":` block imports `screening.stage_e_runner`
and calls THAT module's `main()`, so `python -m` and an import run the same module object. You may
choose another shape only if it is smaller; say why in your report.

(b) A trip list. For every member record the runner writes (screen_member; not the cluster record),
write one file next to it through the same write-once pattern as write_record (open mode "x", a
RunnerRefusal if it exists), named `<same name as the record>_trips.json`, that is
`f"{cluster}_{label}_{window}_trips"` through `_safe`. Content:
- the record file's name and the sha256 of the exact bytes write_record wrote for it;
- cluster, member, window, status;
- `trips`: every TripRecord the runner already computes (extract_trips), in its order, with every
  field: root, open_ts_ns, close_ts_ns (you may add ISO UTC strings beside them), trade_date,
  contracts, net_cents, close_reason, locked, hold_minutes, AND gross_cents (the sum of the trip's
  fills' gross_realized_cents; TripRecord does not carry it today). Compute gross from the same Fill
  events without changing any existing TripRecord value or any number that enters a record. Cents
  must be exact: if a value can be a Fraction, write it exactly (for example "p/q") with a float
  beside it, and say what you chose.
- For a record with no engine run (status excluded_before_screening or refused_case), write the file
  with `trips: []`.
The existing record files keep their exact format and content, byte for byte (created_utc apart).
Do not change write_record's output, the record schema, fills, costs, the account model, the screen,
tiers, coverage or labels.

(c) Tests, in files the harness manifest hashes (tests/test_stage_e_runner.py or a new
tests/test_stage_e_runner_*.py; see TEST_PATTERNS in screening/harness_freeze.py):
- A subprocess test that launches a real `python -m screening.stage_e_runner ...` process (not runpy
  inside pytest) on a synthetic case in which a start-date refusal is raised through
  stage_e_start_dates' `_runner()`, and asserts the refusal is recorded by name (power not_run with
  the class name in the reason) and the exit code is 0. Nothing may be written under reports/ or
  data/; use tmp_path. Show RED first: run it against the unfixed runner and record that it fails
  with the escaped refusal, then fix and show GREEN.
- A test that the trip list's net sums per trade date equal the record's daily series
  (daily_net_usd exactly, and the series values in net ticks per contract per day).
- A test that the trip file is write-once and carries the record's sha256.
- Every one of the eight raises in stage_e_start_dates and every runner refusal must be caught by
  name under both launches: add what is needed to show it, or explain in the report why the
  existing tests plus yours cover it.

## Full suite
`nice -n 10 uv run pytest -q` WITHOUT PYTHONPYCACHEPREFIX (three bytecode tests fail with it set).
One test must fail until the lead rebuilds the manifest, because you changed frozen files:
tests/test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_exists.
Run the suite with that one test deselected (`--deselect ...`) and report the result, then run that
one test alone and report that its only problems are the files you changed (and your new test file).
Pipe output to a file and read the tail only. The suite takes about 11 minutes.

## Boundaries
- You may change only screening/stage_e_runner.py, screening/stage_e_start_dates.py and test files.
  If the fix seems to need any other harness file, STOP and report to the lead; do not edit it.
- Do NOT run `python -m screening.harness_freeze build` (lead only). Do not edit
  reports/stage_e2b_harness_freeze.json or any other frozen file or manifest.
- Do not run the runner on real data. Do not read bar files. Nothing under data/, live/, ops/.
- Do not touch strategy/members/ (other workers are coding K4 members there) or reports/ other than
  your report. No commits. No web access needed.
- Stage E entry points launched outside pytest take a fresh PYTHONPYCACHEPREFIX outside the repo.

## Return
Write reports/stage_e4_harness_fix.md: the shape chosen and why; the diff summary per file (and
`git diff --stat`); the trip-file schema with one synthetic example; each test and what it proves;
the RED and GREEN evidence; the suite result verbatim (tail); anything you could not finish.
Reply with the path, a summary of at most 200 words, and anything unfinished.
