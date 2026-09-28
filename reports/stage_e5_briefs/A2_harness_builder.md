# Brief: HarnessBuilder-OpusXHigh (Stage E.5 Task A2, harness v5 change set)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" and "Compute limits"
paragraphs first (read files by section: grep, line ranges; keep command output short; pytest -q with output to a file,
read the tail). Times in your report: PDT (America/Vancouver). You are a worker: you do not spawn workers.

## Objective (one)
Implement section 3 of reports/stage_e5_harness_plan.md exactly (3a the 2019-2023 Topstep schedule in rules/sessions.py,
3b the new screening/stage_e_verdict.py, 3c the E.5 spend block and the step 2 gate's reading of it, 3d tests), with the
full test suite passing. Section 4 of the plan holds the lead's rulings you implement; do not re-decide them.

## Inputs (read by section)
- reports/stage_e5_harness_plan.md (all of it: it is your specification).
- docs/NULL_CRITERIA_E.md sections 1, 3, 6, 7 (lines 16-43, 59-92, 124-158).
- reports/stage_d1f_confirmation_list.md 3.1-3.4 (lines 424-497): the D.1f procedure you restate.
- The code named in the plan's inventory table, at the lines it gives: strategy/research/_d1f_decisions.py (lines 106-280),
  strategy/research/_d1b_accounting.py (73-110), funnel/null_generator.py (176 on), funnel/multiple_comparisons.py
  (63-182), screening/stage_e_stats.py (250-334), screening/stage_e_stats_power.py (1-58, 461-561; its restated-core
  pattern and its tests tests/test_stage_e_stats_power.py are your model), screening/stage_e_stats_units.py (32-100),
  screening/stage_e_runner.py (353-485: the record fields you read), rules/sessions.py (all 337 lines),
  data/cme_calendar.py (the Holiday type and the HOLIDAYS entries 2019-2026), data/calendars/*.py (HOLIDAYS only),
  data/config.py (all), data/pull_step2.py (1-125, 365-400, 728-800), tests/test_e2b_pull_step2.py (grep for the E.2b
  names), tests/test_session_calendar.py (grep).
- A runner confirmation record does not exist yet. Build test fixtures in the shape of a research record
  (reports/stage_e4_k4_screen/K4_K4-ngpre-01_NG_research.json: read its keys and the lengths only, with a short script,
  never print it whole) with `"window": "confirmation"`, `"screen": null`, `"power": null` and an `"s_x"` map, which is
  what the runner writes on the confirmation window (screening/stage_e_runner.py:302-313, 482-483).

## Output
- The code and tests of the plan's section 3, in exactly these files: rules/sessions.py, screening/stage_e_verdict.py
  (new), data/config.py, data/pull_step2.py, and files under tests/ (new Stage E tests named to match the harness
  TEST_PATTERNS, e.g. tests/test_stage_e_verdict.py, tests/test_stage_e_sessions_holidays.py).
- reports/stage_e5_harness_change.md: every change with file:line; the holiday validation table (per published row:
  rule value, published value, match, and for each of the four expected exceptions its reason); the derived 2019-2023
  rows as a table (date, equity entry, close-by or closed); the unsettled list with reasons; the day_rule effect on the
  audit's 15 FX dates and on the energy and metals early-halt dates 2019-2023 (before and after); the verdict module's
  public functions and their D.1f counterparts; each known-answer test and what it pins; the E.5 config block as
  written; the full-suite result line (count and time) and the command you ran.
- Deviations: anything the plan does not settle, decided by you only if it cannot change a verdict figure, and listed.

## Allowed tools
Read, Edit, Write, Bash (python via `uv run`), no web access. Run the full suite once at the end:
`nice -n 10 uv run pytest -q > <scratch file> 2>&1` without PYTHONPYCACHEPREFIX (three bytecode tests fail with it set),
and read the tail; run targeted test files as you go. One heavy computation at a time: do not run the full suite more
than twice.

## Boundaries
- Touch no file outside the list above. If the plan cannot be implemented without another change (another harness
  file, the manifest, a frozen table, member code), STOP and report to the lead what and why; do not make it.
- Do not rebuild or edit reports/stage_e2b_harness_freeze.json and do not run screening.harness_freeze build. Do not
  run any Stage E entry point against real data (the runner, the start-rule builder, pull_step2 --quote-only or --buy,
  step2_store): no vendor call, no Databento key, no bar read. The E.5 caps stay 0.00.
- No edit to docs/, reports/ other than your one report, data/calendars, data/cme_calendar.py, strategy/, the member
  freezes, REGISTRATION.md, live/ or ops/. No commits. No TopstepX reference in code or text beyond the existing
  source ids.
- The research window (2025-04-01..2026-06-19) must be numerically untouched: nothing you change may alter day_rule for
  any date from 2024-01-01 on (the plan's 3a test (v)).

## Return
The report path, a summary of at most 200 words (what changed, the validation result, the suite line), and anything
unfinished or needing the lead.
