# Brief: MemberCoder-OpusXHigh (Stage E.5 Task C3, K4-ngpre-01 NGS table amendment)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" paragraph first. Times PDT.
You are a worker: you do not spawn workers.

## Objective (one)
Remove exactly the NGS rows the lead lists below from K4-ngpre-01's literal storage-date table and nothing else, keep the
table's generated-and-tested discipline, and leave every other table, every rule and every research-window row
byte-identical.

## The rows to remove (lead ruling R-C3-1, C9's first drop rule; confirmation window S_NG = 2019-05-06..2024-02-29)
- 2019-12-26 (table 09:30 CT): table/calendar row 2019-12-26 10:30 ET; actual release 2019-12-27 10:30 ET; the last schedule capture before the release (20191129075548) lists 2019-12-27 10:30 ET, so EIA published on its schedule and the table's standing-Thursda
- 2020-01-02 (table 09:30 CT): table/calendar row 2020-01-02 10:30 ET; actual release 2020-01-03 10:30 ET; the last schedule capture before the release (20191229152905) lists 2020-01-03 10:30 ET, so EIA published on its schedule and the table's standing-Thursda
- 2020-11-12 (table 09:30 CT): table/calendar row 2020-11-12 10:30 ET; actual release 2020-11-13 10:30 ET; the last schedule capture before the release (20201031145739) lists 2020-11-13 10:30 ET, so EIA published on its schedule and the table's standing-Thursda
- 2021-01-21 (table 09:30 CT): table/calendar row 2021-01-21 10:30 ET; actual release 2021-01-22 10:30 ET; the last schedule capture before the release (20210118172825) lists 2021-01-22 10:30 ET, so EIA published on its schedule and the table's standing-Thursda
- 2023-11-09 (table 09:30 CT): schedule entry: standard Thursday 2023-11-09 10:30 ET; actual: no WNGSR published that week (EIA notice in NGWU); next release 2023-11-16
Source of each verdict: reports/stage_e5_ngs_check.json (key `ngs`, rows with `verdict == "drop_actual_differs"`;
sha256 ddfecb3e1575dc817aaeebc0f8795ebcbbbd10e78b4a936ec8b454d277706b44) and reports/stage_e5_ngs_check.md ("Every non-keep row"). The four Friday releases are NOT added as
rows: the frozen rule allows only a drop (the prompt: "only by C9's frozen drop rule").

## Inputs (read by section)
- strategy/members/k4/_releases.py: the docstring (lines 1-25), RELEASE_CHECK_SHA256 and the DROPPED_NGS block (27-52), the
  NGS tuple (242 on). The table is GENERATED and a test recomputes it: tests/test_e4_k4_members_b.py lines 60-70 and
  230-300 (CHECK_JSON, the section 11 drop constants, the NGS recomputation and its counts).
- strategy/members/k4/ngpre.py lines 1-70 (how NGS is read; you do not change this file).

## What to change
1. strategy/members/k4/_releases.py: add the listed rows to the drop record in the file's style. Either extend DROPPED_NGS,
   with the confirmation-window reasons taken from the E.5 check, or add a separate literal (e.g. DROPPED_NGS_CONFIRMATION,
   with an E5_NGS_CHECK_SHA256 constant and the check's path in the docstring). Remove exactly those rows from NGS. Update
   the docstring's source lines and counts (372 NGS rows becomes 372 minus the rows dropped). Nothing else in the file changes.
2. tests/test_e4_k4_members_b.py: the recomputation must now apply the E.5 drops too. Pin the E.5 check's sha256. Assert
   the E.5 drop dates equal the check's drop_actual_differs verdicts on or after S_NG. Assert the research-window row count
   (63) and every research-window row are unchanged. Update the total count. Keep every other assertion.
3. Optionally, a one-off generator under reports/stage_e5_briefs/ (not committed by you) that reproduces the new table
   from the calendar and the two checks.
Run tests/test_e4_k4_members_b.py and every tests/test_e4_k4_* file, and report the result lines.

## Boundaries
Touch only strategy/members/k4/_releases.py, tests/test_e4_k4_members_b.py and, optionally, a script under
reports/stage_e5_briefs/. No change to ngpre.py or any other member, to the WPSR, API, NYSE or holiday tables, or to the
release calendar. No edit to any report, the harness, screening/, rules/, data/, docs/ or the cluster freeze file: the
lead writes the new freeze. No Stage E entry point, no web, no commits.

## Output and return
reports/stage_e5_k4_table_amendment.md: the diff summary (rows removed, with reasons; constants added; counts before and
after), the unchanged research-window rows (count and sha256 of their literal text before and after), the test results.
Return the path, a summary of at most 150 words, and anything unfinished.
