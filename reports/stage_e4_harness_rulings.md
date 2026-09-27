# Stage E.4 Task H4: the lead's rulings on the harness review, and harness manifest v4

Lead: Opus 5.5 (xhigh), 2026-09-27, about 03:05 PDT. Review: reports/stage_e4_harness_review.md
(HarnessReviewer-FableXHigh, fable xhigh, which wrote none of the change): BLOCKING 0, SHOULD FIX 0, NOTE 9;
checks 1-6 all PASS (scope; C-1 caught by name under both launches for all 21 `_runner()` raise sites;
the trip list; the regression's numerical identity, re-checked independently on all 44 records; the
tests, RED reproduced against HEAD's runner; the manifest diff).

## Rulings

| Note | Finding | Ruling | Change |
|---|---|---|---|
| N-1 | `trip_gross_cents` raises AssertionError outside the runner's handler | Unreachable from any ledger `extract_trips` accepts (both walk the same Fill tuple the same way, and `extract_trips` raises first); consistent with `extract_trips`' own AssertionError for engine invariants | none |
| N-2 | the fix report's RED ran against an intermediate state (trip list added, C-1 not yet) | Accepted. The reviewer reproduced RED against HEAD's runner itself (3 failed, 4 passed; the two `python -m` items fail with the escaped StartRuleMissing through HEAD line 442). A lead note is added to reports/stage_e4_harness_fix.md section 5 | report note only |
| N-3 | the confirmation-window launch test does not discriminate C-1 | It pins that the fix does not start swallowing refusals that propagate by design; kept | none |
| N-4 | one launch case has an empty fragment | Not vacuous (the `startswith("ConfirmationStoreMissing: ")` check holds). Editing tests/_stage_e_launch.py, a manifest-hashed file, would change the manifest after the regression ran under it | none |
| N-5 | stage_e_start_dates lines 584 and 589 run under neither launch | Reached only through `start_date()`, which no harness entry point calls; same `_runner()` classes as the other 19 sites; unit-tested against the imported classes | none |
| N-6 | the trip file has no created_utc or harness id of its own | As specified: it is bound to its record by `record_sha256`, and the record carries both | none |
| N-7 | `_exact_cents` on a float would write its binary fraction | Defensive only: cents are `int | Fraction` by type, and the replay shows only ints and small-denominator fractions | none |
| N-8 | compute/agent.py:312 launches the runner with `-m` | The same mechanism the launch tests exercise; fixed by the same change | none |
| N-9 | the replay's harness id names an uncommitted manifest | Decided: harness manifest v4 IS that manifest, sha256 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009, built in place at 02:30 PDT and not rebuilt since, so the K2 regression ran under exactly the committed v4 | none |

No BLOCKING or SHOULD FIX finding, so no code or test changed after the review, and the regression
(reports/stage_e4_k2_regression.md: 44/44 records field-identical, 44/44 trip lists sum, cluster record
identical) stands for v4 as committed.

## Harness manifest v4

- `python -m screening.harness_freeze build` at 02:30 PDT (the lead): 1,034 files; sha256
  82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009.
  `verify --expected 82ae8536...` printed `preflight OK`, again at commit time.
- Diff against the committed manifest cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45:
  changed screening/stage_e_runner.py and tests/test_stage_e_runner.py; added tests/_stage_e_launch.py and
  tests/test_stage_e_runner_launch.py (category stage_e_test); removed none; the header fields created_pdt and
  head_at_creation differ; nothing else.
- Naming: DECISIONS V13 (a) calls this manifest v4 ("Later purchase sessions that edit data/config.py write the
  version after v4"). From its commit on, every Stage E command takes `--harness-sha256 82ae8536...`, and the
  old sha256 cf939270 is refused by the preflight.
