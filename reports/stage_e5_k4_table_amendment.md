# Stage E.5 Task C3: K4-ngpre-01 NGS table amendment

Worker: MemberCoder-OpusXHigh. Brief: reports/stage_e5_briefs/C3_member_coder.md. Written 2026-09-27 19:06 PDT.
Ruling applied: R-C3-1 (C9's first drop rule, confirmation window S_NG = 2019-05-06..2024-02-29).
Source: reports/stage_e5_ngs_check.json, sha256 ddfecb3e1575dc817aaeebc0f8795ebcbbbd10e78b4a936ec8b454d277706b44
(verified by sha256sum before use). No web access, no Stage E entry point, no commits.

## Files touched

| File | Change |
|---|---|
| strategy/members/k4/_releases.py | 5 NGS rows removed in place, drop record and 2 constants added, docstring sources and counts, `__all__` |
| tests/test_e4_k4_members_b.py | E.5 pins, NGS recomputation with the E.5 drops, 4 new tests, generator test extended |
| reports/stage_e5_briefs/gen_k4_releases_e5.py (new, untracked) | one-off generator: renders the E.4 module through the unchanged E.4 generator, then applies the E.5 drops |

`git diff --numstat`: _releases.py +47/-11, test file +103/-9 (150 insertions, 20 deletions in total).
Not touched: ngpre.py and every other member, the WPSR, API, NYSE, holiday and unverified tables, the release
calendar, the E.4 generator, the harness, screening/, rules/, data/, docs/, the cluster freeze file.

File sha256:
- strategy/members/k4/_releases.py: before 35bd4730d12386f4e31f7f045d95afe9a9f7843c686899557a944bcfa68dd1f0
  (the value recorded in reports/stage_e_k4_member_freeze.json), after aa8764b375283e812315b90ca699a9671e2c96e7793a02bbeb56b7a94ea4d388.
  **The K4 freeze now records a stale hash for this file; the lead's freeze rewrite must pick up aa8764b3....**
- tests/test_e4_k4_members_b.py after: d9d4ec9d9e1a74f7fe005968c17ed6066aa69d15b10a0903db56f5fa0a2b26b2
- reports/stage_e5_briefs/gen_k4_releases_e5.py: b5d799d3d08db56c9aa8cb816d92417e29cf28da5fb0213529e308c07c8853ed

## Rows removed from NGS (all 09:30 CT in the table)

Each reason is stored as `drop_actual_differs: ` followed by the check's `reason` field, verbatim
(so the stored text keeps the check's closing "(lead decides drop vs correction)"; the lead's decision is
drop, R-C3-1, recorded in the module docstring).

| Date (table row) | Actual per the E.5 check | Reason (check, verbatim) |
|---|---|---|
| 2019-12-26 | 2019-12-27 10:30 ET | table/calendar row 2019-12-26 10:30 ET; actual release 2019-12-27 10:30 ET; the last schedule capture before the release (20191129075548) lists 2019-12-27 10:30 ET, so EIA published on its schedule and the table's standing-Thursday date is wrong (lead decides drop vs correction) |
| 2020-01-02 | 2020-01-03 10:30 ET | same form; last schedule capture before the release 20191229152905 lists 2020-01-03 10:30 ET |
| 2020-11-12 | 2020-11-13 10:30 ET | same form; last schedule capture before the release 20201031145739 lists 2020-11-13 10:30 ET |
| 2021-01-21 | 2021-01-22 10:30 ET | same form; last schedule capture before the release 20210118172825 lists 2021-01-22 10:30 ET |
| 2023-11-09 | no release that week | schedule entry: standard Thursday 2023-11-09 10:30 ET; actual: no WNGSR published that week (EIA notice in NGWU); next release 2023-11-16 |

The four Friday releases (2019-12-27, 2020-01-03, 2020-11-13, 2021-01-22) were not added as rows. A test asserts
that none of them is in NGS and that `ngpre.schedule(NGS)` has no entry on any of the five dropped dates.

Layout: the rows are removed in place. Four source lines of the NGS literal changed (2019-12-26 and 2020-01-02
share a line). No line lost all of its rows, so the table keeps its 124 lines. Every other line of the module
body is byte-identical to the E.4 generator's rendering; the test checks this block by block.

## Constants added (strategy/members/k4/_releases.py)

- `E5_NGS_CHECK_SHA256 = "ddfecb3e1575dc817aaeebc0f8795ebcbbbd10e78b4a936ec8b454d277706b44"`
- `CONFIRMATION_CHECK_WINDOW = ("2019-05-06", "2024-02-29")` (equals the check's `window`; parallel to
  `RESEARCH_CHECK_WINDOW`)
- `DROPPED_NGS_CONFIRMATION`: the 5 (date, reason) rows above, rendered with the E.4 generator's `render_drops`.
  `DROPPED_NGS` (the E.4 section-11 drop 2025-12-29) is unchanged, so the E.4 assertion on it stays as written.
- `__all__` gains these three names (sorted, re-wrapped).

Docstring edits: the GENERATED line now names the E.5 generator and the third source. The NGS bullet says
"less DROPPED_NGS and DROPPED_NGS_CONFIRMATION". The research-window bullet loses "only", because C9's drop rule is
now also applied in S_NG. A confirmation-window bullet was added. The counts line now reads 367 NGS rows.

## Counts before and after

| Table | Before | After |
|---|---|---|
| NGS rows | 372 | 367 |
| NGS rows in the research window 2025-04-01..2026-06-19 | 63 | 63 |
| DROPPED_NGS (research window) | 1 | 1 |
| DROPPED_NGS_CONFIRMATION | (absent) | 5 |
| WPSR rows (standard) | 369 (317) | 369 (317) |
| DROPPED_WPSR | 2 | 2 |
| API_DROPPED_WEEKS | 0 | 0 |
| NGS_UNVERIFIED_IN_WINDOW | 3 | 3 |
| FEDERAL_MONDAY_HOLIDAYS | 46 | 46 |
| NYSE_NOT_FULL | 84 | 84 |

E.5 check cross-check: its 252 rows equal the calendar's NGS rows in S_NG one for one (date and ET time).
Its verdicts are {keep: 247, drop_actual_differs: 5} and nothing else. Its `time_ct_table` equals the
pre-amendment table value on all 252 rows.

## Research-window rows unchanged

63 rows (2025-04-03..2026-06-18), on 21 whole source lines of the NGS literal.

| Measure | Before | After |
|---|---|---|
| Row count | 63 | 63 |
| sha256 of the 21 source lines joined by "\n" | d1a4ccf4cb541d25bd0a446e408323fa0daa23c63e066ad9ad616d557fcc3746 | d1a4ccf4cb541d25bd0a446e408323fa0daa23c63e066ad9ad616d557fcc3746 |
| sha256 of the 63 row literals `("date", "HH:MM"),` joined by "\n" | b19e7f1bf07c577acdfc1463b20aee2269cbbdb493902ba52442dde3d0104127 | b19e7f1bf07c577acdfc1463b20aee2269cbbdb493902ba52442dde3d0104127 |

The line hash is pinned in the test as `RESEARCH_WINDOW_NGS_LINES_SHA256`.

## Test changes (tests/test_e4_k4_members_b.py)

- New constants: `E5_CHECK_JSON`, `E5_GENERATOR`, `E5_CHECK_SHA256` (pinned), `S_NG`, `E5_NGS_DROPS`,
  `RESEARCH_WINDOW_NGS_LINES_SHA256`; `import re`; module docstring mentions the E.5 check.
- `test_ngs_table_is_every_calendar_row_less_the_drop_with_t_n_in_ct`: the recomputation drops
  `DROPPED_NGS | DROPPED_NGS_CONFIRMATION`; the total count is 373 - 1 - 5; the research-window count stays 63.
- New `test_the_e5_check_has_the_pinned_sha256_and_window`: pins the sha256 and the window, and checks that S_NG
  ends before the research window starts.
- New `test_the_e5_drops_are_the_e5_checks_drop_verdicts_on_or_after_s_ng`: the verdict set is exactly
  {keep, drop_actual_differs}. The check rows equal the calendar's 252 S_NG rows. The drop dates equal the check's
  drop_actual_differs dates on or after S_NG, which equal E5_NGS_DROPS. Each reason equals
  "drop_actual_differs: " + the check's reason. Also asserted: no dropped date is left in NGS or appears in
  DROPPED_NGS, no Friday row was added, and ngpre.schedule(NGS) has no dropped date.
- New `test_research_window_ngs_rows_are_unchanged_by_the_e5_drops`: the window rows equal the calendar
  recomputation with only the E.4 drop; the test also checks the counts (63 rows, 21 lines) and the pinned line sha256.
- New `test_the_e5_amendment_removes_the_five_ngs_rows_and_nothing_else`: DROPPED_WPSR, DROPPED_NGS,
  API_DROPPED_WEEKS, NGS_UNVERIFIED_IN_WINDOW, WPSR, FEDERAL_MONDAY_HOLIDAYS and NYSE_NOT_FULL are byte-identical
  to the E.4 rendering. The NGS literal differs only on 4 lines, each being the E.4 line minus the dropped literals.
- `test_the_module_is_exactly_the_generators_output`: keeps its E.4 rendering and asserts that the E.5
  generator renders the identical E.4 text. It then asserts that the module equals `amend(...)`, which is that text
  plus the E.5 drops. Every other assertion in the file is unchanged.

Mutation checks, run by swapping the module and then restoring it (sha256 re-verified as aa8764b3... afterwards):
- With the pre-amendment module in place, 5 of the 6 selected NGS/E.5/generator tests fail. The research-window
  test passes, as expected.
- With one extra kept row (2020-01-09) removed, 3 tests fail.

## Test results (2026-09-27, about 19:05 PDT)

- Baseline before any edit, the four tests/test_e4_k4_* files: `236 passed in 5.91s`
- After: `240 passed in 5.89s` (236 plus the 4 new tests)
  - tests/test_e4_k4_members_b.py: `63 passed in 1.96s`
  - tests/test_e4_k4_members_b_eia.py: `43 passed in 1.57s`
  - tests/test_e4_k4_members_a.py: `95 passed in 2.29s`
  - tests/test_e4_k4_members_a_ovr.py: `39 passed in 1.73s`
- `ruff check` on the three touched files: all checks passed.
The full suite was not run (per the brief).

## Open items for the lead

1. tests/test_e4_k4_members_b.py now loads reports/stage_e5_briefs/gen_k4_releases_e5.py, in the same way it
   already loads the tracked E.4 generator. That file is untracked. It must be committed with the amendment, or
   `test_the_module_is_exactly_the_generators_output` and `test_the_e5_amendment_removes_the_five_ngs_rows_and_nothing_else`
   fail with a missing file.
2. reports/stage_e_k4_member_freeze.json still records _releases.py at 35bd4730...; the new file is aa8764b3....
   The freeze rewrite is the lead's.
3. The stored reasons keep the check's "(lead decides drop vs correction)" verbatim so that they match the check
   exactly. If the lead wants that clause stripped, the generator's `e5_drops` and the test's reason assertion both
   need a one-line change.
