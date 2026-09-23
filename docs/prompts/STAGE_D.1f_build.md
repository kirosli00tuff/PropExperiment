STAGE D.1f "HARNESS BUILD AND FREEZE (NO PURCHASE)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage D.1e froze the MES null criteria (docs/NULL_CRITERIA.md) and
the confirmation list (reports/stage_d1f_confirmation_list.md). That list's
order of operations requires every piece of harness work to be built, tested
and hash-frozen BEFORE any data is quoted or bought, so the new history
cannot shape the code that will judge it. This session does exactly steps 1
and 1b of that order and stops. It builds the confirmation-window loader, the
holdout-2 sealing support, the 2019-2024 CME calendar, the statistics
wrapper, the six Family H modules, the 2019-2024 macro release table, the
list runner, and every test named in section 5 of the list; then it writes
the harness-freeze manifest and hands it to the user to commit. It buys
nothing, quotes nothing, downloads nothing, and runs no confirmation test.
The purchase and the run are the next session.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: this stage is implementation, not judgment. The
criteria and the list are already frozen, so there is no new pre-registration
to write and no verdict to reach. CLAUDE.md's routing puts code touching
screening/, data/holdout and the fill path at opus xhigh, and docs/
ORCHESTRATION.md says implementation-heavy stages run an Opus lead so Fable's
weekly slice is kept for verdict-bearing work. The parallel parts are real
but modest (six H modules, the calendar, the release table), so ultracode's
fan-out is not justified.

Usage: Fable is used twice, both narrow: one worker-xhigh verification of the
holdout-2 sealing tests and the look-ahead tests, and one worker-max
adversarial review of those same two areas before the freeze. Everything
else is opus, sonnet or haiku. Stage D.1e spent 169M Fable tokens; this
stage should spend a small fraction of that.

============================================================
SCOPE
============================================================

This stage does:
- build and test every item in section 5 of reports/stage_d1f_confirmation_list.md
- write reports/stage_d1f_harness_freeze.json, the sha256 of every file the
  run session must not change, print it into the STATE file, and ask the user
  to commit it
- record the declared amendment to the two E-H modules (section 5.7) in the
  STATE file, with its re-hash and its train-union reproduction test

This stage does NOT:
- quote, buy or download any data. Zero Databento calls of any kind,
  including metadata. The quote-and-purchase step belongs to the run session.
- seal anything for real. Holdout-2 sealing is built and tested on synthetic
  chunks; the real sealing happens on arrival in the run session.
- run any H module, statistic or trial on the research parquet, the train
  union, any fold, or any real bars beyond what an existing test already
  covers. Per the list (R-7), an H module run on real bars before the
  confirmation counts as a screen against N for that member. Synthetic bars
  only.
- change any file the list's section 0 hashed, except the two E-H modules
  through the declared amendment in section 5.7
- touch REGISTRATION.md, holdout-1's manifest, rules/, live/, ops/ or any
  TopstepX credential
- add to N. N stays 31.

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md: roles, routing, worker files,
   concurrency, artifacts, checkpoints, the ETA table and the Session cost
   section. This prompt does not repeat them; on any conflict CLAUDE.md wins
   and the conflict is logged.
2. reports/stage_d1f_confirmation_list.md in full, especially section 0
   (what "frozen" refers to), 1.2 (holdout-2), 1.3 (confirmation window),
   1.5 (order of operations), 2.1 A3 (the look-ahead test design), 3.1 to
   3.6 (the decision rules this session implements), and section 5 (the work
   itself). This file is read-only and FROZEN: read it, never edit it.
3. docs/NULL_CRITERIA.md in full, especially 2.2 (ε), 4.1 (the start rule)
   and 4.2 to 4.5 (roll, degraded days, calendar, cost model).
4. progress.md's Stage D.1e entry, then D.1a (the runner contract), B-C (the
   harness), and docs/SCREENING.md.
5. The code the work extends: screening/runner.py, screening/drift.py,
   funnel/null_generator.py, data/research_bars.py, data/holdout.py,
   data/cme_calendar.py, data/pull_mes.py, data/build_mes_bars.py,
   data/bars.py, data/validate.py, strategy/interface.py,
   strategy/research/_d1e_event_series.py (the wrapper pattern section 5.4
   tells you to copy), and the two E-H modules.

============================================================
GUARDRAILS (short recap; CLAUDE.md has the full list)
============================================================

- `uv run python -m data.holdout status` at start and end; report
  unlocks_logged (must be 0).
- Databento spend $0.00 and zero calls. Nothing may import the vendor client
  outside a test that stubs it.
- N stays 31.
- No commits. The user commits after review; the freeze manifest needs their
  commit before the run session can start.
- Checkpoint to reports/stage_d1f_build_STATE.md after every task, with the
  ETA table updated.

============================================================
TASK 0 — STARTUP
============================================================

Holdout status. Confirm the working tree is clean at 9cbd815 or later and
that docs/NULL_CRITERIA.md and reports/stage_d1f_confirmation_list.md match
the sha256 values in reports/stage_d1e_declaration_hashes.json; if either
differs, stop and report. Confirm the four worker files load. Plan the stage,
write the estimate ETA table to the STATE file and print it in chat.

Work autonomously from here to the end. Do not pause, do not ask, and do not
stop to confirm anything: the user is not watching and will review the
finished entry. Where a choice is genuinely open, take the most conservative
reading, write the choice and its reason in the STATE file, and carry on.
"Conservative" means the reading that makes a later null claim harder, a
leak less likely, and a look-ahead easier to catch.

Set data/config.py yourself rather than waiting for the user: session id
`stage-D.1f-2026-09`, a per-session Databento cap of $10.00 and a
per-request cap of $10.00, which covers the $7.59 history and nothing more.
The order-book purchase is a separate decision and must not fit under these
caps. Print the chosen values in the deliverable under a heading the user
cannot miss, and note that changing them means re-running the manifest
script before committing, since data/config.py is inside the freeze.

Write the manifest as a small re-runnable script
(strategy/research/_d1f_freeze.py) rather than a one-off command, so the
user can regenerate it after any edit without a new session.

============================================================
TASK 1 — CONFIRMATION WINDOW IN THE SCREENING PATH (list 5.1)
============================================================

Add a ConfirmationWindow that `screen_candidate` accepts, loading the
confirmation parquet through a loader with the same refusal semantics as
data.research_bars: holdout-1 and holdout-2 dates refused always, mined dates
refused on a confirmation run. Recompute the splice dates, the drift path and
the session benchmark on the confirmation bars rather than reusing the mined
window's. Replace funnel.null_generator's research-slice refusal with the
same refusal (R-3). The train-union path stays exactly as it is, so the
continuity check still runs. Re-run the leakage canaries and the full test
suite.

Tests: the refusals (each of the three date classes, both directions), the
recomputed benchmark on synthetic bars, and a continuity test showing an
existing trial's train-union figures are unchanged to the cent.

============================================================
TASK 2 — HOLDOUT-2 SEALING SUPPORT (list 5.2)
============================================================

Extend data/holdout.py with a second HoldoutPaths (store
data/sealed/MES_holdout_v2/, manifest docs/HOLDOUT2_MANIFEST.json, the same
append-only unlock log and the same REGISTRATION.md requirement) and the new
logic wherever the current functions assume holdout-1. Sealing is per chunk,
oldest first, at download time.

Build and test on synthetic chunks only. The five assertions the list names
are mandatory: (i) after sealing, no plaintext of any of the 13 chunks exists
under the repo, in /tmp or in the vendor client's cache; (ii) the manifest
lists 13 raw records with the sha256 of the plaintext and of the sealed blob;
(iii) verify_seal on the holdout-2 paths reports all_ok with plaintext absent
for all 13; (iv) the confirmation loader asserts max(trade_date) <=
2024-02-29 and refuses 2024-03-01..2025-03-31 and >= 2025-04-01 on the
confirmation path; (v) `python -m data.holdout status` reports both holdouts.
Holdout-1's manifest is untouched.

This is the one irreversible part of the whole stage: if sealing is wrong,
the second holdout is spent before it is used. It gets the Fable review in
Task 8.

============================================================
TASK 3 — CME CALENDAR 2019-2024 (list 5.3)
============================================================

Extend data/cme_calendar.py with every holiday and early close from 2019
through 2024, each entry citing its source verbatim from CME's published
schedules. The 2025-2026 entries stay byte-identical to the hashed file.
Extend CALENDAR_COVERAGE to 2019-01-01 and assert it in the bar builder for
every built date. Implement the step 4b validation (data.validate.
observe_holidays over the confirmation bars) as a callable the run session
invokes; it is not run on real bars here. The flatten-time logic is unchanged.

Delegable: the entry collection is extraction with citations; the coverage
assertion and the validator are code.

============================================================
TASK 4 — STATISTICS WRAPPER (list 5.4)
============================================================

New module strategy/research/_d1f_statistics.py that calls the two hashed
statistics builders with the confirmation date set, exactly as
strategy/research/_d1e_event_series.py calls them with the EDA dates. The
hashed modules are NOT edited. Test: the wrapper on the 139 EDA dates
reproduces every recorded estimate, n and implied edge to 1e-9, and every
per-event value of _d1e_event_series.py.

============================================================
TASK 5 — THE SIX FAMILY H MODULES (list 5.5, spec in 2.1)
============================================================

strategy/research/h_daily_bar/: H1 NR4 breakout, H2 NR7 breakout, H3
inside-day breakout, H4 bottom-tercile-range breakout, H5 top-tercile-range
fade, H6 prior-close-location follow-through. Implement exactly the frozen
specification: the daily bar built inside the strategy from bars already
seen, the complete-day rule, the instrument guard on every daily bar entering
the condition (H1 and H2's earlier ranges exempt as the amendment states),
the 30-minute opening range needing 25 of 30 bars, entry on the first close
beyond the range between 09:00 and 14:29 CT with one entry per day and fill
at the next open, the exit emitted at or after 14:58 CT with the engine's
forced flatten as the logged fallback, the lookbacks 4, 7, 2, 61, 61 and 1
complete bars, tercile cuts at exactly 33.33 and 66.67 linear over the 60
complete ranges before d-1, CLV cuts at 0.2 and 0.8 with the tabulated
inequalities, 2 micros at the size-5 slippage bucket, and factories taking no
arguments.

Per-module tests, on synthetic bars only: the look-ahead pair (perturb day
d's bars and assert the condition is unchanged; perturb day d-1's and assert
it changes as computed by hand), the fill-timing canaries, and hand-built
known-answer days. Do not run these modules on the research parquet, the
train union or any fold. If one is run on real bars by accident, log it in
the STATE file as a look and report it; per R-7 it counts as a screen.

Parallelizable: one worker per pair of modules, each with its own tests.

============================================================
TASK 6 — RELEASE TABLE 2019-2024 AND THE E-H AMENDMENT (list 5.7)
============================================================

New hashed module strategy/research/e_calendar_event/_release_table_2019_2024.py
covering 2019-05-01..2024-02-29: scheduled FOMC statement dates with their
2:00pm ET times from the Federal Reserve's historical FOMC calendars, and CPI
and Employment Situation release dates with their 8:30am ET times from the
BLS schedule archives. Use the published date where a release moved. Exclude
unscheduled FOMC actions, following the hashed module's own "regularly
scheduled" convention. Every entry cites its source.

Then the declared amendment: E-H1 and E-H2 currently read a module-level
table with no hook, so each is amended to accept a table argument whose
default is the existing table, and nothing else in either module changes.
Re-hash both, record the amendment in the STATE file with the old and new
hashes and the reason, and add a test that the amended modules reproduce
their train-union figures to the cent. The D.1f factories pass the combined
table.

Citation discipline: each date carries a verbatim quote from the fetched
source page or an [unverified] mark. A Fable-free task, but the verification
pass in Task 8 spot-checks a sample against the sources.

============================================================
TASK 7 — THE LIST RUNNER (list 5.6)
============================================================

strategy/research/_d1f_confirmation.py: runs the whole frozen list, writes
one JSON per tier, and computes the decision rules of sections 3.1 to 3.4
(the per-member edge statistic and its bootstrap uncertainty; Holm over the
58 Tier A p-values; the composite screening verdict; the cumulative
accounting at N = 58 pinned to the program's own DSR, t and CSCV PBO
functions; the class null rule at ε with its achieved-power condition; the
inconclusive and null-by-inactivity labels). It refuses to run if any hash in
section 0, in the harness-freeze manifest, or of itself or of
docs/NULL_CRITERIA.md differs, re-checks at completion, and records the
manifest's own sha256 in every output JSON.

Tested end to end on synthetic members with known answers: a member with a
planted edge above ε must pass, one at zero must be null, one with too few
events must be inconclusive, one with zero events must be inconclusive rather
than null, and a tampered hash must refuse.

============================================================
TASK 8 — VERIFICATION AND ADVERSARIAL REVIEW (narrow, Fable)
============================================================

8a. worker-xhigh on fable: verify the Task 2 sealing tests and the Task 5
    look-ahead tests. Do they actually prove what they claim? Re-derive at
    least one look-ahead case by hand and check the sealing assertions
    against data/holdout.py's real code paths rather than its docstrings.
8b. worker-max on fable: adversarial review of those same two areas only, and
    of the freeze manifest's coverage. The brief: find every way holdout-2
    could leak, every way an H module could see day d before deciding, and
    every file whose change could alter a confirmation result while staying
    outside the manifest. The lead adjudicates every finding in writing and
    applies the fixes before Task 9.

============================================================
TASK 9 — THE FREEZE MANIFEST (list step 1b)
============================================================

Write reports/stage_d1f_harness_freeze.json: the sha256 of every file under
screening/, sim/ (including sim/slippage_calibration.json), funnel/
(including reports/power_gate.json), rules/, data/*.py,
strategy/interface.py, strategy/research/h_daily_bar/*,
strategy/research/_d1f_*.py, the release-table module, and every file hashed
in section 0. Print it into the STATE file. State plainly in the deliverable
that the run session cannot start until the user commits this manifest, and
that any change to a listed file after the commit voids the run.

============================================================
WHAT NOT TO DO
============================================================

- No Databento call, quote, download or purchase.
- No real sealing, no real confirmation run, no H module on real bars.
- No edit to any file hashed in section 0 except the two E-H modules through
  the declared amendment, and no edit to any file outside section 5.8's
  allowed list.
- No change to holdout-1, REGISTRATION.md, rules/, live/, ops/.
- No new hypothesis, no new statistic, no addition to N.
- No commits.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry for Stage D.1f (build): guardrail evidence; the
delegation record with deviations; what each of Tasks 1 to 7 built, with test
counts and what the tests prove; the E-H amendment with old and new hashes;
Task 8's findings and rulings; the freeze manifest's path, its own sha256 and
the file count; anything the run session must do first (the user's commit,
the data/config.py session id and spend caps); and the closing Session cost
section with the final ETA table, per CLAUDE.md. Also one line in
docs/STAGES.md recording this build session under Stage D.1f.

Artifacts: reports/stage_d1f_harness_freeze.json,
strategy/research/_d1f_freeze.py, reports/stage_d1f_build_STATE.md, the new
modules and tests named above.

A closing section listing every open choice the lead made on its own, with
the reason, so the user can overturn any of them before committing the
freeze.

END PROMPT
