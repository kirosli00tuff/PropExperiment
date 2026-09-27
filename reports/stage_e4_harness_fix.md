# Stage E.4 Task H1: harness fix C-1 and the per-trial trip list

HarnessFixer-OpusXHigh, 2026-09-27, 02:08 to 02:37 PDT. Brief: reports/stage_e4_briefs/H1_harness_fixer.md.
Scope held: only screening/stage_e_runner.py and test files changed. screening/stage_e_start_dates.py
is untouched. No manifest rebuild, no frozen file, no bar data, nothing under data/, live/, ops/ or
strategy/members/, no commit.

## 1. Shape chosen (C-1)

The preferred shape, unchanged. The runner's `if __name__ == "__main__":` block now imports
`screening.stage_e_runner` and calls that module's `main()`:

```python
if __name__ == "__main__":
    # C-1 (E.3 return, section 7; E.4 H1): ... (4 comment lines)
    from screening import stage_e_runner

    sys.exit(stage_e_runner.main())
```

Under `python -m`, the file still executes once as `__main__`, but that copy only defines names;
all work runs in `sys.modules["screening.stage_e_runner"]`, which is the module `_runner()` in
stage_e_start_dates returns. So every refusal class raised through `_runner()` is the class the
running code's `except (RunnerRefusal, StageEBarRefusal)` names. The `__main__` copy's classes still
exist but nothing raises or catches them. No smaller shape exists: any change inside
stage_e_start_dates (for example, making `_runner()` look at `sys.modules["__main__"]`) is longer
and more fragile. runpy prints no warning (the child's stderr was empty in a probe run), because
the runner is imported after `__main__` has run, not before.

## 2. Diff summary per file

```
$ git diff --stat
 screening/stage_e_runner.py  |  90 +++++++++++++++++++++++++++++--
 tests/test_stage_e_runner.py | 123 ++++++++++++++++++++++++++++++++++++++++++-
 2 files changed, 207 insertions(+), 6 deletions(-)
new (untracked): tests/_stage_e_launch.py (330 lines), tests/test_stage_e_runner_launch.py (122 lines)
```

- **screening/stage_e_runner.py**
  - The C-1 block above.
  - `import hashlib`, plus the constants `TRIPS_SCHEMA = "stage_e_member_trips/1"`,
    `TRIPS_SUFFIX = "_trips"` and `CENTS_NOTE`.
  - `trip_gross_cents(result, trips)`: per trip, the sum of its fills' `gross_realized_cents`. It
    replays extract_trips' flat-to-flat grouping over the same `Fill` events and returns the sums
    in the same order. If the replay's (root, open_ts_ns, close_ts_ns) sequence differs from the
    trips it was given, it raises `AssertionError`. It reads nothing else and changes nothing:
    TripRecord and extract_trips are untouched.
  - `trip_rows(trips, gross)`, `_exact_cents` and `_utc_iso` build the rows.
  - `write_member_record(record, trips, out_dir)`: refuses (RunnerRefusal) if the trip file
    already exists, then calls `write_record(record, ...)` exactly as before. It hashes the
    written file's bytes (read back from disk, so the hash is of the bytes actually written), then
    writes the trip document through `write_record` itself (mode "x", RunnerRefusal "already
    exists; records are written once").
  - `screen_member`: its three `write_record(record, out_dir, f"{cluster}_{label}_{window}")`
    calls became `write_member_record(record, rows_or_(), out_dir)`. The name comes from
    `record["cluster"]`, `record["member"]` and `record["window"]`, which equal those arguments.
    One line computes the rows right after `extract_trips`, before anything is written.
  - Module docstring: one paragraph on the trip file. The first line, which argparse uses, is
    unchanged.
- **screening/stage_e_start_dates.py**: no change.
- **tests/test_stage_e_runner.py**: 5 tests appended (section 4), plus imports.
- **tests/_stage_e_launch.py** (new; the harness manifest hashes it through `_stage_e_*.py`): the
  synthetic world, the patches both launches use, the case table, the child launcher and the
  record checks.
- **tests/test_stage_e_runner_launch.py** (new; hashed through `test_stage_e_*.py`): 7 test
  items (section 4).

Record format is unchanged: HEAD's runner (`git show HEAD:screening/stage_e_runner.py`, loaded as
a separate module) and the new runner ran on one synthetic 22-member world (the launch case
table). All 23 HEAD files (22 member records and the cluster record) are byte-identical in the
new output once the `"created_utc"` value is masked. The new output adds exactly 22 files, all
`*_trips.json`. This one-off script sat in the scratchpad and is not a test. The records it
covers have statuses `run` (with power `not_run`) and `refused_case`. Nothing in the record-
building code changed; only the write call did.

## 3. Trip-file schema

Name: `_safe(f"{cluster}_{label}_{window}_trips") + ".json"` in the record's directory, for example
`K2_K2-cp1-01_ZT_research_trips.json` beside `K2_K2-cp1-01_ZT_research.json`. It is written with
the same `json.dumps(..., indent=2, sort_keys=True) + "\n"` as the record. Top-level keys:

| key | value |
|---|---|
| schema | "stage_e_member_trips/1" |
| record_file | the record file's name |
| record_sha256 | sha256 of the record file's bytes as written |
| cluster, member, window, status | as in the record (status: run, excluded_before_screening, refused_case) |
| cents | the encoding note (below) |
| n_trips | len(trips) |
| trips | one row per TripRecord, in extract_trips' (closing) order; `[]` without an engine run |

Row keys: root, open_ts_ns, open_utc, close_ts_ns, close_utc, trade_date (ISO date of the closing
fill), contracts, net_cents, net_cents_float, gross_cents, gross_cents_float, close_reason, locked,
hold_minutes. The `*_utc` values are ISO UTC strings added beside the ns integers: `...Z`, with
`.nnnnnnnnn` only when the timestamp has a sub-second part.

**Cents encoding (the choice made):** `net_cents` and `gross_cents` are written exactly. The value
is a JSON int when it is a whole number of cents, and the string `"p/q"` (lowest terms, sign on p)
otherwise. `net_cents_float` and `gross_cents_float` always carry `float(value)`, correctly
rounded. `Fraction(str(v))` recovers the exact value in both cases. A consumer that sums the raw
field fails loudly on a fractional value (TypeError), never silently.

Synthetic example, from a real `python -m` run of the launch world (member `K1-c01-missing ZN`,
first of its 10 trips shown):

```json
{
  "cents": "net_cents and gross_cents are exact: an int, or 'p/q' when the value is not a whole number of cents; *_float beside each is float(value)",
  "cluster": "K1",
  "member": "K1-c01-missing ZN",
  "n_trips": 10,
  "record_file": "K1_K1-c01-missing_ZN_research.json",
  "record_sha256": "0ef6bd94c3d6eb409c38d02ecf27750411645c9cab2efebc25203c4a74f062a6",
  "schema": "stage_e_member_trips/1",
  "status": "run",
  "trips": [
    {
      "close_reason": "strategy",
      "close_ts_ns": 1748875260000000000,
      "close_utc": "2025-06-02T14:41:00Z",
      "contracts": 1,
      "gross_cents": -15625,
      "gross_cents_float": -15625.0,
      "hold_minutes": 30.0,
      "locked": false,
      "net_cents": -17451,
      "net_cents_float": -17451.0,
      "open_ts_ns": 1748873460000000000,
      "open_utc": "2025-06-02T14:11:00Z",
      "root": "ZN",
      "trade_date": "2025-06-02"
    }
  ]
}
```

A fractional row, from the unit test (hand-built fills, gross 0 + 250 - 125/3):
`"net_cents": "-1475/3", "net_cents_float": -491.6666666666667, "gross_cents": "625/3",
"gross_cents_float": 208.33333333333334`.

## 4. Tests and what each proves

tests/test_stage_e_runner_launch.py (the C-1 tests; the child is a real
`sys.executable -m screening.stage_e_runner` process run from the repo root):

1. `test_c1_a_start_date_refusal_under_python_m_is_recorded_by_name_and_exits_0` reproduces E.3's
   attempt 1. A one-member cluster has no start-rule file, so the power check's
   `start_dates_for` raises `StartRuleMissing` through `_runner()` (stage_e_start_dates.py line
   609). The test asserts:
   - exit code 0, and the child's synthetic world was installed (marker file);
   - stdout `K1 ... research: run []`;
   - the record on disk carries `power.status == "not_run"`, and the reason starts
     `StartRuleMissing: no frozen S_X for ['ZN']`;
   - the trip file carries the record's name and sha256;
   - the engine was called from module `screening.stage_e_runner` (one module object);
   - exactly two files were written.

   A second launch into the same directory exits 1 with
   `screening.stage_e_runner.RunnerRefusal: ... already exists; records are written once`. So the
   runner's own refusals now also carry the imported module's class (before the fix they would
   print as `__main__.RunnerRefusal`).
2. `test_c1_every_start_date_refusal_is_caught_by_name_under_both_launches[python -m | import]`: a
   22-member cluster, one member per case, run with `--all` under each launch. Each member's
   record names its refusal by class and message fragment. The cases are:
   - 19 members covering every start-date raise a research run's power check can meet, all
     through `_runner()`. The table is in `start_cases()`; each row names its raise site.
   - a `ConfirmationStoreMissing` control (data.stage_e_bars, the other class in the `except`);
   - `EngineRefusedCase` and `FrozenInputError` controls (the OC-T `except`), recorded as
     `refused_case`.

   The test also asserts:
   - exit code 0 (python -m), or `main()` returns 0 (import);
   - the summary line `K1 research: 22 members, 2 refused`;
   - each trip file matches its record's sha256;
   - all 22 engine calls came from `screening.stage_e_runner`;
   - exactly 45 files were written;
   - the cluster record's refused_members.
3. `test_c1_a_confirmation_run_without_s_x_is_refused_by_name_under_both_launches` (2 cases x 2
   launches) covers `StartRuleMissing` (line 609) and `StartWindowEmpty` (line 614, reachable only
   with `allow_empty=False`, that is the confirmation window). The runner lets these propagate by
   design (existing test `test_the_confirmation_window_needs_a_frozen_start_rule`). Under
   `python -m` the process exits 1 and names `screening.stage_e_runner.<class>` with its message.
   Under import, `pytest.raises` gets that exact class (`type(...) is`). In both, nothing is
   written and the engine never runs.

tests/test_stage_e_runner.py (the trip list, on the existing `world` fixture):

4. `test_e4_the_trip_list_sums_per_trade_date_to_the_records_daily_series`: from the trip file on
   disk alone:
   - `n_trips` equals the series' `n_trips`;
   - per trade date, the exact sum of `net_cents` / 100 gives the record's `daily_net_usd`
     exactly (float equality);
   - per trade date, the sum of `(net_cents / 100) / (contracts x 15.625)` gives
     `series.values` exactly, in net ticks per contract per day with the ZN tick value;
   - `float(exact) == *_float`, and gross minus net is greater than 0 (the costs).
5. `test_e4_the_trip_file_is_written_once_and_carries_the_records_sha256`: `record_file` and
   `record_sha256` match the record's bytes; cluster, member, window and status match. A second
   run is refused ("written once") and leaves the trip file byte-identical. With the record
   deleted and the trip file left in place, a run is refused naming the trip file, before the
   record is written.
6. `test_e4_a_member_excluded_before_screening_gets_an_empty_trip_list`: coverage 0.9 gives
   `trips: []`, `n_trips` 0 and a matching sha.
7. `test_e4_a_refused_case_gets_an_empty_trip_list`: EngineRefusedCase gives `trips: []` and a
   matching sha.
8. `test_e4_trip_rows_carry_every_field_and_exact_gross_and_net_cents`: hand-built Fill events on
   two roots, interleaved, with a partial exit, a locked exit, Fraction and int cents, and a
   forced_flatten close. It checks every row field exactly (one full-dict equality), gross sums
   (625/3, 3125/2, 1000), nets equal to TripRecord.net_cents, and that gross replayed against a
   different trip set raises.

**Why this covers "every raise in stage_e_start_dates and every runner refusal, by name, under
both launches".** stage_e_start_dates has 21 raise statements that use a `_runner()` class. The
E.3 return's "eight" counts only the lines spelled `raise _runner().X`; 13 more raise through
aliases bound from `_runner()` (`invalid = _runner().StartRuleInvalid`, `rt = _runner()`).
- 18 of the 21 are reachable in a research run's power check. Each is a member of test 2 under
  both launches. Line 419 is met twice there, once through `_s_x` and once through `_first_dates`.
- Line 614 is reachable only in a confirmation run and is covered by test 3.
- Lines 584 and 589 (`_date_of`) are reached only through `start_date()`. No Stage E entry point
  calls it; only tests do. The existing tests
  `test_no_file_means_every_root_is_missing_by_the_runners_class` and
  `test_an_empty_window_is_named_and_is_still_a_start_rule_missing` check them against the
  runner's classes, imported from `screening.stage_e_runner`.

The runner catches refusals in exactly two places:
- `_research_statistics`, which catches (RunnerRefusal, StageEBarRefusal): tested under both
  launches, with all start-date classes and a bar control.
- `screen_member`, which catches (EngineRefusedCase, FrozenInputError): classes of modules that
  never run as `__main__`, controls included under both launches.

The runner's own refusals (window, legs, empty window, release calendar, write-once, parquet sha,
calendars) are never caught. They propagate by design. After the fix they carry the one module's
class under `python -m`, and test 1's second launch shows this.

## 5. RED and GREEN evidence

> Lead note (H4 ruling on review N-2, 03:05 PDT): the RED below ran against an intermediate state (trip list added,
> C-1 edit not yet made). HarnessReviewer-FableXHigh reproduced RED against HEAD's runner itself: 3 failed, 4 passed;
> the two `python -m` items fail with the escaped StartRuleMissing through HEAD line 442, and the import item fails
> only for the missing trip file (reports/stage_e4_harness_review.md, N-2 and check 5).

**RED** (02:13:33 PDT). The launch tests ran against the runner with the trip list already in
place but before the C-1 edit: `2 failed, 5 passed in 8.07s`. Both failures are the `python -m`
launches, and both show the escaped refusal (child stderr tail, verbatim from the assertion
message):

```
E       AssertionError:   File ".../screening/stage_e_runner.py", line 516, in _research_statistics
E             supply, meta = confirmation_supply_days(legs, Path(step2_root))
E           File ".../screening/stage_e_runner.py", line 319, in confirmation_supply_days
E             starts, provenance = _start_dates([leg.root for leg in legs], allow_empty=True)
E           File ".../screening/stage_e_runner.py", line 284, in _start_dates
E             return start_dates.start_dates_for(tuple(roots), allow_empty=allow_empty)
E           File ".../screening/stage_e_start_dates.py", line 609, in start_dates_for
E             raise _runner().StartRuleMissing(f"no frozen S_X for {missing}: no reports/"
E         screening.stage_e_runner.StartRuleMissing: no frozen S_X for ['ZN']: no reports/stage_e_start_rule_<SET>.json lists them
E       assert 1 == 0
FAILED tests/test_stage_e_runner_launch.py::test_c1_a_start_date_refusal_under_python_m_is_recorded_by_name_and_exits_0
FAILED tests/test_stage_e_runner_launch.py::test_c1_every_start_date_refusal_is_caught_by_name_under_both_launches[python -m]
```

The 5 that passed before the fix: test 2's import launch (all 22 caught, the path R-T5-1 used) and
the 4 confirmation items (propagation is the same before and after).

The trip tests were RED first as well: `5 failed, 25 deselected` (AttributeError:
`trip_gross_cents`; no `_trips.json`).

**GREEN** (02:13:54 PDT, after the C-1 edit): tests/test_stage_e_runner_launch.py and
tests/test_stage_e_runner.py together gave `37 passed, 1 warning in 12.30s` (7 launch items, 25
existing runner tests, 5 new trip tests).

The focused set gave `290 passed, 1 warning in 63.04s`. It covers test_stage_e_runner,
test_stage_e_runner_launch, test_stage_e_start_dates, test_cross_platform_static (it scans the
runner), test_compute_units, test_ml_route_test_entry, test_ml_route_stage_e_adapter,
test_ml_route_stage_e_inputs and test_stage_e_freeze. ruff: "All checks passed!" on the four
changed files.

## 6. Full suite

Command (PYTHONPYCACHEPREFIX unset):
`env -u PYTHONPYCACHEPREFIX nice -n 10 uv run pytest -q -p no:cacheprovider --deselect
tests/test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_exists`,
02:16:52 to 02:35:06 PDT. The process survived the Claude Code restart at about 02:25 and ran to
the end. Tail, verbatim:

```
-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
3019 passed, 2 skipped, 1 deselected, 1 xfailed, 54 warnings in 1090.78s (0:18:10)
exit 0
end 02:35:06 PDT
```

No failures and no errors. The lead's start-of-stage baseline was 3008 passed. 3008 - 1
deselected + 12 new (5 trip tests, 7 launch items) = 3019. The other workers' K4 files
(tests/test_e4_k4_members*.py, strategy/members/k4/) do not appear in the output; they were
probably created after collection began, so this run neither passed nor failed them.

**The manifest test alone.**
`uv run pytest -q tests/test_harness_freeze.py::test_the_real_tree_matches_the_committed_manifest_when_it_exists`
gave `1 passed in 1.12s`. It did not fail as the brief expected, because the manifest on disk is
no longer the committed one. `reports/stage_e2b_harness_freeze.json` was rewritten at 02:30 PDT
(git status `M`; sha256 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009, against
the committed cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45). I did not run the
build or touch that file; I assume the lead rebuilt it. The rebuilt manifest lists my four files
at their current bytes:

| file | sha256 |
|---|---|
| screening/stage_e_runner.py | 6283d679... |
| tests/test_stage_e_runner.py | 7eb61e83... |
| tests/_stage_e_launch.py | 28f2e987... |
| tests/test_stage_e_runner_launch.py | 843856db... |

`hf.check` on the tree now reports 0 problems.

To show what the brief asked for, the same `hf.check` ran in a throwaway process against the
committed manifest (`git show HEAD:reports/stage_e2b_harness_freeze.json` loaded in memory; no
file written). Its only problems are my two modified files:

```
committed manifest cf939270f0a0 problems 2
  screening/stage_e_runner.py: sha256 6283d6795f86... differs from the frozen 998c8db93d91...
  tests/test_stage_e_runner.py: sha256 7eb61e834137... differs from the frozen 6dd1ac8dbaf7...
```

The committed manifest's `check` does not flag the two new test files, because its
unlisted-file scan covers harness code, not tests. The rebuild's `manifest_categories` picks them
up through TEST_PATTERNS, and the rebuilt manifest lists them.

## 7. Not finished or not verified

- Nothing in the brief is left undone.
- The manifest test did not fail as the brief expected. Someone else rebuilt the manifest at
  02:30 PDT, during my suite run; I did not build it. Section 6 gives the evidence against the
  committed manifest instead. The lead should confirm that the 02:30 rebuild was theirs and was
  intended. It hashes my files at their current bytes, but I have not checked what else it lists
  (for example strategy/members/k4/).
- The full suite ran from 02:16:52. The manifest rebuild at 02:30 happened mid-run. The
  deselected manifest test was the only test that reads it, so the result should not depend on
  it. By grep, only tests/test_harness_freeze.py:92 calls `hf.check` on the real tree; the other
  tests that name a manifest path build their own under tmp_path.
- The record parity check (HEAD's runner against the new one, 23 of 23 byte-identical once
  created_utc is masked) is a one-off scratchpad script, not a test. It covers statuses run (power
  not_run) and refused_case, not excluded_before_screening or power run. The lead's replay of
  K2's 44 frozen trials is the numerical check on real records.
- The multi-leg series path (`daily_series_from_leg_dollars`) has no trip-sum test. The trip
  file's per-day net sums are the same for any leg count; only the ticks conversion differs.
- The unit test of `_utc_iso` covers whole-second timestamps only. The sub-second branch
  (`.nnnnnnnnn`) is untested; engine fills are on minute bars.
