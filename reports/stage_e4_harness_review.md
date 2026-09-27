# Stage E.4 Task H3: independent review of the harness change (C-1 routing and the trip list)

HarnessReviewer-FableXHigh, 2026-09-27, about 02:38 to 02:50 PDT. Brief: reports/stage_e4_briefs/H3_harness_reviewer.md.
I wrote none of the change. Read-only on the repository; scratch and probe outputs under /tmp/claude-1000/e4_h3/
(compare.py, red.out, green.out, runner.diff, tests.diff, manifest_head.json, headrepo/). No commit, stash, checkout,
manifest build, bar data or web. `git status --short` after every run shows only the three pre-existing `M` lines.

Reviewed at HEAD 0fb61f2e (frozen harness cf939270...) against the working tree (rebuilt manifest 82ae8536...).
Files in the diff: screening/stage_e_runner.py (+90/-6), tests/test_stage_e_runner.py (+123/-1),
reports/stage_e2b_harness_freeze.json (+22/-... header and four entries); new tests/_stage_e_launch.py and
tests/test_stage_e_runner_launch.py. screening/stage_e_start_dates.py is unchanged (sha256 ef5e7a15... equals HEAD
and the manifest entry).

## Counts

BLOCKING 0, SHOULD FIX 0, NOTE 9. All six checks pass.

## Findings

### N-1 NOTE. `trip_gross_cents` raises `AssertionError` outside any handler (screening/stage_e_runner.py:206, called at :465)
The replay's consistency check raises `AssertionError`, not `RunnerRefusal`, and the call at line 465 sits after the
`try/except (EngineRefusedCase, FrozenInputError)` block, so if it ever fired an `--all` run would stop with a traceback
and no record for that member. It cannot fire from a ledger `extract_trips` accepts: both functions iterate the same
`result.events(Fill)` tuple, key on `f.root`, take the first fill's `fill_ts_ns` as the open, and close on
`position_after == 0`; `extract_trips` raises first on any ledger with an open trip or a trip that never held a
position, so the replay's (root, open, close) list is the same by construction. Consistent with `extract_trips`'
own `AssertionError` for engine invariants. No action needed; if the lead wants uniformity, raise `RunnerRefusal`.

### N-2 NOTE. RED evidence in the fix report is from an intermediate state, not HEAD (reports/stage_e4_harness_fix.md, section 5)
The fixer's "2 failed, 5 passed" ran against the runner with the trip list already added but without the C-1 edit.
Against HEAD's runner itself (my reproduction, check 5 below) the result is 3 failed, 4 passed: the same two
`python -m` items fail with the escaped `screening.stage_e_runner.StartRuleMissing` (raised through HEAD's line 442
in `_research_statistics`, the line E.3's return names), and the `import` item fails only with
`FileNotFoundError ... K1_K1-c01-missing_ZN_research_trips.json` because HEAD writes no trip file. The C-1 evidence is
the same; the report should say which state its RED ran against. Suggested fix: one sentence in section 5.

### N-3 NOTE. The confirmation-window launch test does not discriminate C-1 (tests/test_stage_e_runner_launch.py:94-122)
Its four items pass before and after the fix (both RED runs and GREEN), because those refusals propagate by design
and were already raised by the imported module's classes. It is not vacuous: it pins that the fix does not start
swallowing them and that nothing is written. Keep; no action.

### N-4 NOTE. One launch case has an empty fragment (tests/_stage_e_launch.py:145)
`Case("no_step2_store", ..., "ConfirmationStoreMissing", "", ...)`: `check_member`'s `case.fragment in reason` is
trivially true for that row. The `reason.startswith("ConfirmationStoreMissing: ")` check still holds, so the row is
not vacuous. Suggested fix: give it a fragment (for example `no_step2`).

### N-5 NOTE. Lines 584 and 589 of stage_e_start_dates.py are not exercised under either launch
`_date_of` is reached only through `start_date()`, which no harness module calls (grep: only
tests/test_stage_e_start_dates.py). Their classes come from the same `_runner()` as the other 19 sites, so the
module-identity argument (check 2) covers them; the existing unit tests check them against the imported classes.
No action.

### N-6 NOTE. The trip file has no `created_utc` or `harness_sha256` of its own (screening/stage_e_runner.py:378-382)
Top-level keys are exactly schema, record_file, record_sha256, cluster, member, window, status, cents, n_trips,
trips, as the H1 brief lists. The file is bound to its record only through `record_sha256`, and the record carries
the harness id and the time. Acceptable as specified; no action.

### N-7 NOTE. `_exact_cents` on a float would write the float's binary fraction (screening/stage_e_runner.py:211-214)
`Fraction(0.1)` is `3602879701896397/36028797018963968`. `Fill.gross_realized_cents` is typed `int | Fraction`,
`TripRecord.net_cents` too, and the 44 replayed trip lists show only ints and small-denominator fractions (3,614 of
8,914 cents fields are `"p/q"` strings: treasury halves and quarters of a cent), so the case does not arise.
Defensive only.

### N-8 NOTE. The compute backend launches the runner on the C-1 path too (compute/agent.py:312)
`[sys.executable, "-m", spec.kind_spec().module, ...]` with cwd = REPO_ROOT is the same `python -m` mechanism the
launch tests exercise, so it is fixed by the same change. Untested directly; no action.

### N-9 NOTE. The replay's harness id names an uncommitted manifest (reports/stage_e4_k2_regression/*.json)
All 44 replay records and the cluster record carry harness_sha256 82ae8536..., the sha256 of the working-tree
manifest, which is uncommitted (`M`); E.3's carry cf939270..., the committed one. Any further rebuild (for example
after strategy/members/k4/ lands, which MEMBER_CLUSTER_DIRS covers) changes the id again. Lead's decision (the
return calls this the scratch manifest); noted only.

## Check 1: scope. PASS

Every hunk of `git diff HEAD -- screening/ tests/`, classified:

| file:lines (new) | hunk | class |
|---|---|---|
| stage_e_runner.py:50-54, 60 | docstring paragraph on the trip file; `import hashlib` | trip list |
| :111-114 | `TRIPS_SCHEMA`, `TRIPS_SUFFIX`, `CENTS_NOTE` constants | trip list |
| :189-231 | `trip_gross_cents`, `_exact_cents`, `_utc_iso`, `trip_rows` (new functions, nothing existing edited) | trip list |
| :365-382 | `write_member_record`: trips-file existence check, then `write_record` unchanged, then the trip document through `write_record` | trip list (write-once) |
| :452, :462, :484 | the three `write_record(record, out_dir, f"{cluster}_{label}_{window}")` calls become `write_member_record(record, rows or (), out_dir)`; the name is rebuilt from `record["cluster"]`, `record["member"]`, `record["window"]`, which screen_member sets to `cluster`, `label`, `window` (lines 434-436), so the record file name is unchanged | trip list |
| :465 | `rows = trip_rows(...)` computed from `result` and `trips` (both frozen dataclasses; read-only) before anything is written | trip list |
| :592-599 | `if __name__ == "__main__":` imports `screening.stage_e_runner` and calls its `main()` | C-1 routing |

Nothing touches fills, costs, the account model, `_screen`, `assign_tiers`, `member_coverage`, `floor_labels`, the
record dict or `write_record`'s output. `screen_cluster` still writes the cluster record through `write_record`
directly (no trip file). An AST scan of the runner's top level finds only constant assignments, defs, imports and
the `__main__` block, so the `__main__` copy executing under `python -m` has no side effects. Only
screening/stage_e_runner.py, tests and the manifest (check 6) changed; `git diff HEAD --stat` over the whole tree
lists those three files and nothing else.

## Check 2: C-1, every refusal caught by name under both launches. PASS

Raise sites in stage_e_start_dates.py that use a `_runner()` class: 21, at lines 417, 419, 428, 457, 462, 471, 486,
495, 502, 506, 511, 521, 524, 526, 529, 538, 566, 584, 589, 609, 614. Eight are spelled `raise _runner().X` (428,
457, 462, 471, 538, 566, 609, 614); thirteen go through `invalid = _runner().StartRuleInvalid` or `rt = _runner()`.
The fixer's count of 21 is right; E.3's "eight" counted the literal spelling.

Module identity. `_runner()` (stage_e_start_dates.py:121-124) is `from screening import stage_e_runner`, which
returns `sys.modules["screening.stage_e_runner"]` on every call. All 21 sites therefore raise classes of that one
module object. The runner catches runner classes at exactly one place, line 517 `except (RunnerRefusal,
StageEBarRefusal)` in `_research_statistics`; line 456 catches `EngineRefusedCase` and `FrozenInputError`, classes
of modules never run as `__main__`; `StageEBarRefusal` and its six subclasses (data/stage_e_bars.py:75-99, including
`ConfirmationStoreMissing`) live in a module never run as `__main__`, so they were never affected. Outside the runner
the only catch is ml_route/inputs.py:357, through a normal import, unaffected.
- `python -m screening.stage_e_runner`: runpy executes the file as `__main__` without registering it under its
  real name (screening/__init__.py does not import it, so no runpy warning). Line 597 then imports the real module,
  a second copy, and line 599 runs that copy's `main()`. Every frame of the run, including line 517's `except`,
  belongs to `sys.modules["screening.stage_e_runner"]`, the object `_runner()` returns. One class set.
- `python -c "from screening.stage_e_runner import main; ..."`, pytest, ml_route: a normal import; unchanged.
- runpy.run_module in a process that already imported the runner: line 597 returns the existing module (my probe:
  `_runner() is runner` True, `RunnerRefusal` identical; runpy prints its standard sys.modules RuntimeWarning for
  that unusual launch, as before the fix). `python screening/stage_e_runner.py`: `ModuleNotFoundError: No module
  named 'data'` at the first import, before and after (the package is not installed in .venv; `import screening`
  from /tmp fails), so it is not a launch and not a regression. compute/agent.py:312: the `-m` path (N-8).

Tests (GREEN, real repository, `env -u PYTHONPYCACHEPREFIX .venv/bin/python -m pytest -q -p no:cacheprovider
tests/test_stage_e_runner_launch.py tests/test_stage_e_runner.py`): 37 passed in 9.41 s. The 22-member launch case
table reaches 19 of the 21 sites under both launches (417, 419 twice, 428, 457, 462, 471, 486, 495, 502, 506, 511,
521, 524, 526, 529, 538, 566, 609 plus a `ConfirmationStoreMissing` control and two OC-T engine controls); the
confirmation test reaches 609 and 614 as propagating refusals; 584 and 589 are unreachable from the runner (N-5).
The child asserts the engine's caller module is `screening.stage_e_runner` for every member (frame inspection,
tests/_stage_e_launch.py:230), which is direct evidence of which module object ran. Probe: `python -m
screening.stage_e_runner --help` under a fresh PYTHONPYCACHEPREFIX exits 0.

## Check 3: the trip list. PASS

- Fields: every TripRecord field the brief names (root, open_ts_ns, close_ts_ns, trade_date, contracts, net_cents,
  close_reason, locked, hold_minutes) plus gross_cents, with open_utc, close_utc, net_cents_float, gross_cents_float
  beside them (stage_e_runner.py:223-231). `hold_minutes` is TripRecord's own property.
- Exact cents: `_exact_cents` writes the int, or lowest-terms `"p/q"` (`Fraction` normalises), with `float(value)`
  beside it; `_jsonable` never sees a Fraction. Verified on all 4,457 replayed trips: `float(Fraction(str(v))) ==
  *_float` for every net and gross.
- Record sha256: `hashlib.sha256(path.read_bytes())` of the file `write_record` just closed (line 380); 44/44 match
  on disk.
- Write-once: the trips path is checked first (372-374, `RunnerRefusal`), then the record through `write_record`
  (mode "x"), then the trip document through `write_record` (mode "x"). `_safe(name + "_trips") == _safe(name) +
  "_trips"` because `name` always ends in the window word, so the check and the write name the same file.
- Sums and counts: for all 44 records the exact per-trade-date sum of `net_cents` / 100, as floats over
  `series.dates`, equals `daily_net_usd` element for element, and `n_trips == len(trips) == series.n_trips`.
- Nothing outside the window: every `trade_date` is in the record's `series.dates` and in none of its
  `window_dates.excluded` lists; every open and close UTC date lies within [first - 1 day, last + 1 day] of the
  window; `open_utc`/`close_utc` equal `_utc_iso` of the ns values (probe of the sub-second branch:
  `2025-06-02T14:11:00.123456789Z`); `record_file` is a bare file name; no paths, bars or dates beyond the trips.
  Top-level keys are exactly the ten listed (N-6).

## Check 4: the regression proves numerical identity. PASS

My own script (/tmp/claude-1000/e4_h3/compare.py), over all 44 records, not a sample: field-by-field recursive
comparison skipping only `harness_sha256` and `created_utc`: 44/44 identical; the stronger check, the record text
with those two values masked: 44/44 byte-identical (json.dumps with sort_keys and indent=2 is deterministic).
`harness_sha256` is cf939270... in E.3 and 82ae8536... in E.4 everywhere, and `created_utc` differs everywhere,
nothing else. The cluster record K2_research_cluster.json: identical apart from `harness_sha256`; tiers 44 x B,
every member "fails the D5 screen", `refused_members` empty, `not_tiered` empty. Trip lists: 44/44 consistent as in
check 3. Named sample I read individually in the output: K2-cp1-01 ZT (E.3's crash trial), K2-predrift-01 ZN,
K2-fomcpost-01 UB, K2-monthend-01 ZF, K2-aucpre-01 TN, plus the cluster record. Directory contents: E.3 45 files,
E.4 89 = the same 45 names plus 44 `*_trips.json`, nothing missing. All 44 E.3 records have status `run`, so the
replay covers the `run` path only; the `excluded_before_screening` and `refused_case` paths are covered by the
synthetic tests, and their record-building code is untouched.

## Check 5: the tests. PASS

The subprocess test really launches `[sys.executable, "-m", "screening.stage_e_runner", ...]` (tests/_stage_e_launch.py:293)
with cwd the repository, PYTHONPATH = the tmp hooks dir + repository, a fresh PYTHONPYCACHEPREFIX under tmp_path,
and a sitecustomize that asserts the runner was not imported before the launch (lines 264, 269). RED reproduced by
me against HEAD's runner (sha 998c8db9..., the frozen entry) in a tmp tree (/tmp/claude-1000/e4_h3/headrepo:
symlinked packages, copied screening/ and tests/, `git show HEAD:screening/stage_e_runner.py` written over the
copy; no stash or checkout): `3 failed, 4 passed in 5.58s`. The two `python -m` items fail with exit 1 and the
escaped `screening.stage_e_runner.StartRuleMissing: no frozen S_X for ['ZN']` raised through HEAD's line 442; the
`import` item fails only for the missing trip file (N-2). GREEN in the real repository: 37 passed. No test is
vacuous: each asserts a class name in a record or in stderr, exit codes, the caller module, and the exact file set
written; the trip tests assert exact float equality of the sums, sha256 equality, refusal on the second run with the
file byte-identical, and a full-dict row equality on hand-built fills (N-3, N-4 are minor).

## Check 6: the manifest. PASS

JSON-level diff of `git show HEAD:reports/stage_e2b_harness_freeze.json` against the working tree: `files` 1,032 to
1,034, changed exactly screening/stage_e_runner.py and tests/test_stage_e_runner.py, added exactly
tests/_stage_e_launch.py and tests/test_stage_e_runner_launch.py, nothing removed; `categories` adds the same two
(stage_e_test), nothing else; header `created_pdt` and `head_at_creation` (0fb61f2e) changed, as a rebuild must;
every other key identical. The four entries' sha256 and byte counts equal the files on disk (6283d679.../31038,
7eb61e83.../26775, 28f2e987.../17061, 843856db.../6170); the manifest file's sha256 is 82ae8536..., the id in the
replay records; HEAD's is cf939270..., the id in E.3's. The build was not run.

## Not finished or not verified

- Nothing in the brief is left undone.
- compute/agent.py's `-m` launch (N-8) is covered by reasoning and the same mechanism, not by a test of its own.
- The replay covers status `run` only (all of E.3's records); the other two statuses rest on the synthetic tests.
