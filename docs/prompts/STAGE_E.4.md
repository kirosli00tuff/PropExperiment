STAGE E.4 "HARNESS FIX C-1 AND TRIP LISTS, THEN SCREEN K4 ENERGY, K5 METALS AND K3 FX ON THE RESEARCH WINDOW, ONE CLUSTER AFTER ANOTHER (NO PURCHASE)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.3 screened cluster K2 (all 44 trials Tier B, commit
9d36669). It found two harness gaps. Bug C-1: under `python -m
screening.stage_e_runner` the runner module loads twice, so every refusal
that screening/stage_e_start_dates.py raises through `_runner()` escapes the
runner's `except` clauses and crashes the run instead of being recorded by
name (E.3 ruling R-T5-1 worked around it by calling main() from an import).
And the runner writes no trip list (R-T6-1). This session first fixes both
in the harness, has an independent Fable worker review the change, proves
with a regression replay of K2 that no number moved, and rebuilds the
harness manifest (v4). It then does for cluster K4, energy, what E.3 did for
K2: codes K4's eight active members from their frozen entries
(reports/stage_e0_catalog_K4.md, as amended by E.1 and E.2a), checks the
research-window release dates they time on, has an independent Fable
worker check each module against its entry, freezes the member code by
hash, and runs every member once through the frozen runner on the research
window (trade dates 2025-04-01..2026-06-19). A second Fable check
recomputes the screen figures. That is Part 1 (E.4a). Part 2 (E.4b) then
does the same for K5, metals, and Part 3 (E.4c) for K3, FX, in the order the
user froze (U3: K2, K4, K5, K3). Each part has its own specs, audit, cluster
freeze commit, screening run, recomputation and return document. A part
that fails does not stop the next one unless this prompt says so. The
confirmation sessions (step 2 purchase, D4 power check, confirmation list)
come later.

The user runs this session unattended overnight across three usage windows
(until about 04:10, 04:10 to 09:10, and 09:10 to 14:10 Pacific). The
auto-retry launcher resumes it after each usage pause with "read the STATE
file first". So the master checkpoint is reports/stage_e4_STATE.md: after
every task it names the part, the task finished, the hashes in force and
the next task. Each part also keeps its own STATE file.

K4 trades two exposures (E.2a vehicles): WTI crude through MCL at q_c = 4
(eps 21 ticks) and Henry Hub gas through NG at q_c = 1 (eps 8 ticks). RBOB
and ULSD have no vehicle and are not traded. Expected trials: 12 (three
core ports on two exposures, K4-ngpre-01 on gas, K4-apipre-01,
K4-eiafade-01 and K4-eiamom-01 on crude, K4-ovr-01 on crude and gas). The
lead takes the count from the freeze declarations and logs any difference.

K5 trades gold through MGC at q_c = 1 (eps 85 ticks) and copper through MHG
at q_c = 2 (eps 34 ticks). Silver has no vehicle and platinum is out (U2).
Expected trials: 11 (three ports on two exposures, K5-preauc-01 on gold,
K5-pmfix-01 and K5-fomc-01 on gold, K5-ovr-01 on gold and copper).

K3 trades EUR (6E), AUD (6A), GBP (6B), JPY (6J) and CHF (6S) at q_c = 1,
and CAD (6C) and NZD (6N) undersized at 1 contract, screened as E.3 screened
ZT and ZF (E.3 L-20). Expected trials: 31 (three ports on seven exposures,
K3-ldnrev-01 on EUR, JPY and CHF, K3-ldnmom-01 on EUR and JPY,
K3-mehedge-01 on EUR and JPY if its index histories exist, K3-ecbfix-01 on
EUR, K3-tkypre-01 and K3-tkypost-01 on JPY).

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: the harness fix is a small change to frozen code
that every later cluster depends on, and the member work is the E.3 pattern
again: translating frozen, fully specified entries into code and running a
frozen runner. The silent failures to guard against are a harness fix that
changes a number, and a member module that runs cleanly but implements
something other than its entry. CLAUDE.md routes code to opus at xhigh and
independent checks to Fable. Ultracode stays off: at most two coding
workstreams at a time, routed through the worker files.

Usage: follows CLAUDE.md's context-hygiene rules. Read the catalog by member
section, never whole. Keep the lead's context small across three parts:
at the end of each part, write its return document and STATE file, and
carry into the next part only the hashes in force and the next part's
inputs. Do not re-read an earlier part's worker outputs. Fable is used by
four workers, each fresh: HarnessReviewer-FableXHigh (Task H3 only), and
one member auditor per cluster (MemberAuditor-K4-FableXHigh,
MemberAuditor-K5-FableXHigh, MemberAuditor-K3-FableXHigh), each used for
its cluster's Task 3 and resumed with a small brief for its Task 6. If
Fable is unavailable when a Fable task is due, finish the work that needs
no Fable check (specs, release checks, coding and unit tests for the
remaining clusters) and stop before the next freeze. Never substitute opus
for a Fable check. Compute: the ThinkPad under the overnight profile (the
Windows PC is not set up yet, E.2c). E.3 (one cluster, 44 trials) took 101
minutes and 84M tokens. Expect about 6 hours of work in total, plus the
usage pauses.

Do not stop to ask. Decide, log the choice under Open choices in the return
document, and continue. The only stops are the ones this prompt names, a
decision that cannot be undone and could reasonably go either way, or a
guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- fix bug C-1 in the harness and add a per-trial trip list to the runner's
  output (Task H1)
- test the fix, including a subprocess test through `python -m` (Task H1)
- replay K2's 44 frozen trials under the fixed harness into a scratch
  directory and prove every record's numbers equal E.3's (Task H2)
- have the fix reviewed by Fable, rule on the findings, rebuild the harness
  manifest (v4) and commit (Tasks H3 and H4)
- write K4's member specifications and check the research-window release
  dates (Tasks 1 and 1b)
- code K4's eight active members under strategy/members/k4/ (Task 2)
- audit each module against its frozen entry (Task 3)
- freeze the member code with the cluster-freeze helper (Task 4)
- run K4's members once through the frozen runner on the research window
  (Task 5) and recompute the screen figures independently (Task 6)
- repeat Tasks 1 to 7 for K5 (Part 2) and for K3 (Part 3)

This stage does NOT:
- buy anything, or read any bar outside the research window
- run the D4 power check, build start dates, hash a confirmation list, or
  touch any confirmation window. That is K4's confirmation session.
- change any member's rule, parameter, threshold, window or trade count
  from its frozen entry. A member the lead finds unimplementable as written
  is labelled and reported, never rewritten.
- change any harness behaviour other than the refusal routing (C-1) and the
  added trip-list file. No change to fills, costs, the account model, the
  screen, tiers, coverage, labels or record format of existing files.
- re-decide any K2 tier. The K2 regression replay is a determinism check,
  not a new result. Its files stay out of reports/stage_e3_k2_screen/.
- re-run a member after seeing its result, with any change. Each member
  runs once. A crash is fixed only in code the audit covered, re-audited,
  and the member re-run from scratch, and the crash is reported.
- touch the ML route (V11 stays unapplied), any other cluster, holdout-1 or
  holdout-2, live/, ops/, or any TopstepX credential or API
- edit any frozen file other than the harness files Task H1 names, and the
  manifest Task H4 rebuilds. docs/NULL_CRITERIA.md,
  reports/stage_d1f_confirmation_list.md and every E.3 record stay as they
  are.
- write to REGISTRATION.md (it stays 0 bytes)
- buy index histories, or anything else. K3-mehedge-01's free index
  histories are fetched only as Part 3 describes.
- push. The session makes exactly four commits: the harness commit (Task
  H4) and one cluster freeze commit per part (K4, K5, K3).

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md and docs/ORCHESTRATION.md. This prompt does not repeat them.
   On any conflict CLAUDE.md wins, and the conflict is logged.
2. reports/E.3_RETURN.md: section 3 "Task 5" (the C-1 crash and R-T5-1),
   section 5 (the verification and the note on MLL liquidations), section 6
   (the lead readings L-01 to L-23 and rulings R-T2-1, R-T5-1, R-T6-1) and
   section 7. E.3's readings are precedents: where a K4 entry uses the same
   text (the ports, "the bar at hh:mm", named entry bars, instrument guards,
   integer ticks, release tables as literal tables in the cluster package),
   adopt E.3's reading and cite it. Where the K4 text differs, read it
   fresh.
3. docs/DECISIONS.md, entry V13 (this stage's authority for the harness
   change).
4. reports/E.2b_RETURN.md, section 7 items 1 to 5 (the runner command and
   the member contract), and the preflight design paragraph on manifest
   rebuilds.
5. reports/stage_e0_catalog_K4.md: the header (section 0) with its common
   conventions C1 to C13 and every bracketed note, and the eight member
   sections K4-cp1-01, K4-cp2-01, K4-cp3-01, K4-ngpre-01, K4-apipre-01,
   K4-eiafade-01, K4-eiamom-01 and K4-ovr-01. K4-ngrev-01 is excluded (E.0
   review R-06) and K4-ml-01 is excluded (U6). reports/stage_e1_changes.md
   for every K4 edit (K4-00 to K4-03, F-4, F-7). The source-window
   amendment for K4's labels (K4-ngpre-01 lost "source-overlap").
6. The catalog's section 7 questions are settled by the frozen text as
   follows, and are not reopened: item 1 (MCL restriction) is moot, D2
   chose MCL. Item 2 (CP2's tick buffer) is moot, MCL and CL share the
   0.01 tick and NG is the gas vehicle. Item 3 (CP1 on FOMC days) stays as
   D6 is written. Item 4 (event frequency) stays at one trial each. Item 5
   (the Thursday cost sample) is governed by the frozen D8 table: report
   it as a limitation of K4-ngpre-01's cost, no new sample. Items 6 to 9
   stay as frozen. Item 10 (E.2 checks): Task 1b covers (a) to (c) for the
   research window, and (f) is the runner's coverage check.
7. docs/STAGE_E_DESIGN.md (FROZEN): D2, D5, D6 (the energy row O = 08:00,
   C = 13:30, F = 15:08 and CP1 to CP3), D8, D9 (the constraint set, D9.7
   price-limit proximity, the coverage check, the trade-rate floor).
8. reports/stage_e2a_vehicles.md and reports/stage_e2a_epsilon.md, K4 rows.
9. For Part 2: reports/stage_e0_catalog_K5.md, its header and every
   bracketed note, the seven member sections K5-cp1-01, K5-cp2-01,
   K5-cp3-01, K5-preauc-01, K5-pmfix-01, K5-fomc-01 and K5-ovr-01 (K5-ml-01
   excluded, U6), its section 7 as amended, the K5 rows of the E.2a
   vehicles and epsilon files, and the K5 edits in stage_e1_changes.md.
   For Part 3: the same for reports/stage_e0_catalog_K3.md and its nine
   members K3-cp1-01, K3-cp2-01, K3-cp3-01, K3-ldnrev-01, K3-ldnmom-01,
   K3-mehedge-01, K3-ecbfix-01, K3-tkypre-01 and K3-tkypost-01 (K3-ml-01
   excluded, U6). Read each part's files when the part starts, not before.
10. strategy/stage_e/_template.py, strategy/stage_e/interface.py,
   screening/stage_e_freeze.py (write_cluster_freeze),
   screening/stage_e_runner.py, screening/stage_e_start_dates.py
   (`_runner()` and its eight raises), screening/harness_freeze.py (build
   and verify), and the release calendar the runner loads (EIA WPSR, EIA
   gas storage with its 365 [unverified] dates, API bulletin, FOMC, NYSE
   early closes if present).

============================================================
GUARDRAILS
============================================================

CLAUDE.md invariants apply in full. This stage adds:

- Until Task H4's commit, every Stage E command takes `--harness-sha256
  cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45`. After
  it, every Stage E command takes the new v4 sha256, and a run under the
  old sha256 is refused. Every Stage E command runs with a fresh
  `PYTHONPYCACHEPREFIX` outside the repository (E.2b review F-2). A
  preflight refusal stops the session with a named refusal.
- The E.1 and E.2a freeze manifests verify at start and at end. The
  harness manifest verifies at start against cf939270 and at end against
  v4. The K2 cluster freeze (8815a775...) verifies at start and at end.
- Research window only: 2025-04-01..2026-06-19, read by the runner. No
  script of this session opens a bar file directly.
- One run per member. Each cluster's member code is frozen by its Task 4
  before its Task 5 runs anything on data.
- The harness fix may change only screening/stage_e_runner.py,
  screening/stage_e_start_dates.py and tests. Any other harness file the
  fix seems to need is a stop: report it, do not edit.
- No spend. The ledger is unchanged at the end.
- Holdout status at start and end: both all_ok, 0 unlocks.
- REGISTRATION.md stays 0 bytes. No TopstepX reference of any kind.
- Web access (each part's Task 1b only): read-only fetches of public schedule and
  archive pages. No data API, no login, no paid source. Stay within
  CLAUDE.md's WebSearch budget rule.

Start and end checks, quoted verbatim in the return document: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the manifest checks, `uv run pytest -q` (expected at
start: E.3's end result).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Inputs: the context files.
- Output: reports/stage_e4_STATE.md and the estimate ETA table.
- Done when: the start checks pass, HEAD is the commit holding this prompt
  or a descendant with a clean tree, and the runner's preflight accepts
  cf939270.
- Failure path: any mismatch or refusal stops the session with a named
  refusal.

============================================================
TASK H1: THE HARNESS FIX (WORKER)
============================================================

- Owner: HarnessFixer-OpusXHigh, worker-xhigh on opus.
- Inputs: E.3 section 3 (C-1), the runner, stage_e_start_dates.py, the
  runner tests.
- Output:
  (a) The C-1 fix: one class identity for every refusal, whichever way the
  runner is launched. The preferred shape is the smallest one: the
  runner's `if __name__ == "__main__":` block imports
  `screening.stage_e_runner` and calls that module's main(), so `python -m`
  and an import run the same module object. The worker may choose another
  shape if it is smaller and says why.
  (b) A trip list: for every trial the runner records, one file next to
  its record, `<cluster>_<label>_<window>_trips.json` (or the runner's
  existing naming pattern), listing every TripRecord the runner already
  computes (root, entry and exit timestamps, trade date, contracts, gross
  and net in cents, hold minutes, the locked flag) and the sha256 of the
  record it belongs to. The existing record files keep their exact format
  and content.
  (c) Tests: a subprocess test that launches `python -m
  screening.stage_e_runner` on a synthetic case where a start-date refusal
  is raised and asserts it is recorded by name with exit code 0. A test
  that the trip list's net sums per date equal the record's daily series.
  The full suite passes.
- Done when: (a) to (c) exist and the full suite passes.
- Failure path: a fix that needs any other harness file stops the worker,
  which reports to the lead. The lead stops Task H and reports it for the
  user. The K4 work continues under R-T5-1's import launch, and Task 4
  commits the member freeze alone.

============================================================
TASK H2: K2 REGRESSION REPLAY (LEAD RUNS IT)
============================================================

- Owner: lead.
- Inputs: the fixed harness (not yet committed), the K2 cluster freeze.
- Output: reports/stage_e4_k2_regression/ (scratch records and trip
  lists), and reports/stage_e4_k2_regression.md: for each of the 44 K2
  records, the daily series, n_trips, the screen figures, coverage, labels
  and tier compared with the E.3 record in reports/stage_e3_k2_screen/,
  field by field. Only harness hashes and timestamps may differ.
- The command: the E.3 command launched through `python -m` (the path C-1
  broke), with `--out-dir reports/stage_e4_k2_regression`, run under the
  uncommitted fix. The preflight refuses an unlisted change, so the lead
  runs it with the new manifest built to a scratch location or with the
  preflight's documented test mode. If neither exists, the lead runs Task
  H2 immediately after Task H4's commit instead, and any difference then
  reverts that commit.
- Done when: 44 of 44 records match, and every trip list sums to its
  record's series.
- Failure path: any difference is BLOCKING. The fix is wrong. Do not
  commit it. Revert to the frozen harness, report, and continue the K4 work
  under R-T5-1's import launch.

============================================================
TASK H3: HARNESS REVIEW (FABLE XHIGH)
============================================================

- Owner: HarnessReviewer-FableXHigh, worker-xhigh on fable. It wrote none
  of the fix.
- Inputs: the diff, the new tests, reports/stage_e4_k2_regression.md.
- Output: reports/stage_e4_harness_review.md, each finding graded
  BLOCKING, SHOULD FIX or NOTE, with file and line.
- Done when: the reviewer has checked that the diff touches only refusal
  routing and the added trip file, that every one of the eight raises in
  stage_e_start_dates.py and every runner refusal is now caught by name
  under both launches, that the trip list reveals nothing outside the
  window being run, and that the regression proves numerical identity.
- Failure path: if Fable is unavailable, stop Task H before H4 (see
  Usage).

============================================================
TASK H4: RULINGS, MANIFEST V4 AND THE HARNESS COMMIT (LEAD)
============================================================

- Owner: lead.
- Inputs: the review.
- Output: reports/stage_e4_harness_rulings.md, the fixes, the rebuilt
  manifest (`python -m screening.harness_freeze build`, verified with
  `verify --expected <new sha256>`), a diff of the old and new manifests
  showing only the changed files, and one commit on main holding exactly
  the harness diff, its tests, the review, the rulings, the regression
  report and the manifest, with a message naming "harness v4", the C-1 fix
  and the new sha256, ending with this repository's attribution lines.
- Done when: every BLOCKING and SHOULD FIX finding has a ruling and its
  fix, the regression still matches after any fix, the full suite passes,
  and the commit exists.
- Failure path: an unfixable BLOCKING finding: revert, report, and
  continue K4 under R-T5-1.

============================================================
TASK 1: MEMBER SPECIFICATIONS (LEAD)
============================================================

- Owner: lead. Runs in parallel with Task H.
- Inputs: the eight catalog sections, C1 to C13, and their notes.
- Output: reports/stage_e4_member_specs.md: for each member, the exact rule
  as the frozen entry states it after every amendment, with line
  references: exposures traded (crude through MCL, gas through NG, never
  RBOB or ULSD), decision and entry times, exit, hold, flatten, order type,
  sizing at q_c, every parameter as a literal, the release instants it
  reads and their availability times, the C10 non-positive price guard,
  the trade count in N, and the Topstep checks. An ordinal table of the
  trials, catalog order then crude before gas. Where the entry leaves a
  detail open, the lead writes the narrowest reading and logs it as an
  open choice. It never widens a rule.
- Done when: every field of every member has a line reference, an E.3
  precedent or a logged reading.
- Failure path: a member whose entry cannot be implemented without a
  choice that could change its result materially is labelled
  "unimplementable as frozen", reported for the user, and not coded.

============================================================
TASK 1b: RESEARCH-WINDOW RELEASE DATES (WORKER)
============================================================

- Owner: ReleaseChecker-OpusMed, worker-medium on opus. The lead names it
  because E.2 never ran catalog item 10 (a) to (c), and E.2b kept 365 gas
  storage dates [unverified] from EIA's standing rule.
- Inputs: C9 (EC-WPSR, EC-NGS, EC-API and their drop rules), the release
  calendar's rows inside the research window, EC-NYSE rows for
  K4-eiamom-01.
- Output: reports/stage_e4_release_check.md and .json: for every WPSR and
  gas-storage release in the research window, the calendar's date and time
  against EIA's record of actual publication (the petroleum weekly archive,
  the storage report's schedule and history pages, or Wayback captures),
  the "(Updated)" availability test, and C9's verdict: keep or drop. For
  every standard API week in the window, the federal-holiday check. For
  every NYSE early close in the window used by K4-eiamom-01, the source.
- Done when: every in-window release has a verdict with a source URL, or
  the label "unverifiable" with the reason.
- Failure path: a release that cannot be verified is kept as the calendar
  gives it and labelled. A member whose event set holds any unverifiable
  release carries the label "calendar partly unverified" into its record
  in the return. If that member reaches Tier A, its confirmation session
  must verify the dates before it runs.
- The member modules read the checked event tables as literal tables in
  the cluster package (E.3 L-01), with the dropped releases removed and
  the drops listed in the specs.

============================================================
TASK 2: CODE THE MEMBERS
============================================================

- Owner: two workers, MemberCoder-A-OpusXHigh (the three core ports and
  K4-ovr-01) and MemberCoder-B-OpusXHigh (the four event members:
  K4-ngpre-01, K4-apipre-01, K4-eiafade-01, K4-eiamom-01, and the release
  tables), each worker-xhigh on opus, in parallel. They start after Task 1
  and, for coder B's tables, after Task 1b.
- Inputs: reports/stage_e4_member_specs.md, the template and interface,
  the D6 port definitions, the checked release tables, E.3's K2 modules as
  a pattern (not as a source of rules).
- Output: one module per member under strategy/members/k4/, from the
  template, using only the template's import allowlist, with unit tests on
  synthetic bars (tests/test_e4_k4_members*.py) that pin each rule's
  decisions on hand-built cases: entry and exit times, the event window,
  the flatten, a missing bar at a decision time, a moved or dropped
  release, the C10 guard, and D9.7's price-limit exit.
- Done when: every module passes its tests and the full suite passes.
- Failure path: a coder that finds its spec ambiguous stops and reports to
  the lead, who rules in writing. The coder does not choose.

============================================================
TASK 3: FIDELITY AUDIT (FABLE XHIGH)
============================================================

- Owner: MemberAuditor-K4-FableXHigh, worker-xhigh on fable. It wrote none of
  the code and is not the harness reviewer.
- Inputs: the eight catalog sections (by section), C1 to C13, the specs,
  the release check, the modules, their tests.
- Output: reports/stage_e4_member_audit.md, each finding graded BLOCKING,
  SHOULD FIX or NOTE, with file and line.
- Done when: for every member, the auditor has checked that the module
  implements the frozen entry and nothing more: every literal, every time,
  the direction, the exit, the sizing at q_c, the event instants and their
  availability times, the drops, the flatten, and that no input is read
  before its availability time. It also checks that each lead reading in
  Task 1 is the narrowest one, and recomputes every literal event table
  from its source.
- Failure path: if Fable is unavailable, stop before Task 4.

============================================================
TASK 4: RULINGS AND THE CLUSTER FREEZE (LEAD)
============================================================

- Owner: lead.
- Inputs: the audit.
- Output: reports/stage_e4_member_rulings.md, the fixes, the cluster freeze
  file from write_cluster_freeze, and one commit on main holding exactly
  the member modules, their tests, the specs, the release check, the audit,
  the rulings and the cluster freeze file, with a message naming the
  cluster freeze sha256 and "K4 member freeze", ending with this
  repository's attribution lines.
- Done when: every BLOCKING and SHOULD FIX finding has a ruling and its
  fix, the full suite passes, and the commit exists.
- Failure path: a BLOCKING finding that cannot be fixed within the frozen
  entry makes that member "unimplementable as frozen". It is not run, and
  the others proceed.

============================================================
TASK 5: THE SCREENING RUN (LEAD RUNS THE FROZEN COMMAND)
============================================================

- Owner: lead.
- Inputs: the cluster freeze, the harness (v4, or cf939270 if Task H was
  reverted).
- Output: reports/stage_e4_k4_screen/ with every trial's research-window
  daily series, trip list (under v4), coverage and trade-rate labels, the
  D5 screen figures (mean net P&L per contract per day with zeros on
  no-trade days, daily t) and the tier assignment, all written by the
  runner.
- The command under v4:
  `PYTHONPYCACHEPREFIX=<fresh dir> nice -n 10 uv run python -m
  screening.stage_e_runner --harness-sha256 <v4 sha256> --cluster K4 --all
  --window research --research-root data/processed --step2-root
  data/processed_step2 --out-dir reports/stage_e4_k4_screen`.
  If Task H was reverted, the same argv through R-T5-1's import launch.
- Done when: every coded trial has a result or a named refusal, and the
  runner has written the tiers. Power is `not_run` for every trial, by
  design.
- Failure path: a crash stops that member. The fix goes through Tasks 2 to
  4 again, and the member runs from scratch. Report the crash and the fix.

============================================================
TASK 6: RECOMPUTATION (FABLE RESUMED)
============================================================

- Owner: MemberAuditor-K4-FableXHigh, resumed with SendMessage (a small
  brief).
- Inputs: the runner's outputs, the frozen D5, the frozen D8 cost table.
- Output: a second section in reports/stage_e4_member_audit.md: every
  trial's screen mean and daily t recomputed from its daily series in the
  auditor's own code, each tier checked against D5, and for two trials (one
  port, one event member) the daily series rebuilt from the runner's trip
  list and the cost table, with no replay needed under v4. Each event
  member's trade count reconciled with the checked event table. Each item
  VERIFIED, VERIFIED WITH NOTES or DISCREPANCY.
- Done when: every item has a verdict.
- Failure path: a DISCREPANCY is ruled on by the lead in writing. A tier
  with an unresolved discrepancy is marked "unverified" and the
  confirmation session may not use it.

============================================================
TASK 7: READ THE RESULT (LEAD)
============================================================

- Owner: lead.
- Inputs: the verified outputs.
- Output: in the return document, per trial: the trips, the screen
  figures, the labels, the MLL liquidation count and the tier. Program N
  after this session: 102 plus the K4 trials screened. What K4's
  confirmation session will need: the Tier A trials, the Tier B trials,
  and the step 2 purchase for MCL and NG ($11.46 in
  reports/stage_e2b_step2_quotes.md, inside acct-2's remaining $21.52, so
  no top-up).
- Done when: the tables are written from the runner's files, not from
  memory of the logs.
- Failure path: none expected. A result that surprises the lead is still
  reported as computed.

============================================================
PART 2 (E.4b): K5 METALS
============================================================

Start when Part 1 has ended, whatever its outcome. Harness: v4 if Task H4
committed it, otherwise cf939270 with R-T5-1's import launch. Repeat Tasks
1 to 7 exactly as Part 1 sets them, with these substitutions:

- Files: reports/stage_e4b_member_specs.md, reports/stage_e4b_release_check.md
  and .json, strategy/members/k5/, tests/test_e4_k5_members*.py,
  reports/stage_e4b_member_audit.md, reports/stage_e4b_member_rulings.md,
  the K5 cluster freeze file, reports/stage_e4b_k5_screen/,
  reports/stage_e4b_STATE.md.
- Workers: MemberCoder-A-OpusXHigh codes the three ports and K5-ovr-01.
  MemberCoder-B-OpusXHigh codes K5-preauc-01, K5-pmfix-01, K5-fomc-01 and
  the event tables. MemberAuditor-K5-FableXHigh audits and recomputes.
  ReleaseChecker-OpusMed does Task 1b. Spawn each fresh for this part.
- Traded: gold on MGC and copper on MHG only. No silver, no platinum
  trial.
- K5-ovr-01 carries the same rule text as K4-ovr-01 (E.1 F-7) with K5's
  decision clock. Code it as its own module under k5, and have the auditor
  confirm the two differ only in the clock.
- Task 1b checks, for the research window: the LBMA gold AM and PM auction
  dates and start times in CT (UK bank holidays, and the weeks when UK and
  US clocks change on different dates), and that K5-fomc-01's FOMC
  statement instants equal the table E.3 verified for K2.
- Catalog section 7 items are settled by the frozen text (E.1 rulings and
  the frozen D8 and D9). Item 1 (auction starts and the D9.5a fill guard):
  use whatever the frozen D9 and D8 text and the E.2b release calendar
  already do, and log the reading. Items 3 to 6: the members stay as
  frozen, one trial per traded exposure.
- Commit: exactly the K5 member modules, tests, specs, release check,
  audit, rulings and cluster freeze file, message "K5 member freeze" with
  the cluster freeze sha256 and this repository's attribution lines.
- Program N after Part 2: Part 1's figure plus the K5 trials screened.
  K5's confirmation purchase: MGC and MHG, $9.74 in
  reports/stage_e2b_step2_quotes.md.
- Return document: reports/E.4b_RETURN.md, the same eight sections.

============================================================
PART 3 (E.4c): K3 FX
============================================================

Start when Part 2 has ended. Same harness rule as Part 2. Repeat Tasks 1 to
7 with these substitutions:

- Files: the stage_e4c_ names, strategy/members/k3/,
  tests/test_e4_k3_members*.py, reports/stage_e4c_k3_screen/,
  reports/stage_e4c_STATE.md.
- Workers: MemberCoder-A-OpusXHigh codes the three ports.
  MemberCoder-B-OpusXHigh codes K3-ldnrev-01, K3-ldnmom-01, K3-ecbfix-01,
  K3-tkypre-01, K3-tkypost-01 and the event tables. K3-mehedge-01 goes to
  whichever coder finishes first. MemberAuditor-K3-FableXHigh audits and
  recomputes. ReleaseChecker-OpusMed does Task 1b. Spawn each fresh for
  this part.
- Traded: all seven exposures. 6C and 6N are coded and screened although
  undersized (E.3 L-20).
- Task 1b checks, for the research window: the London 4 p.m. fix instant
  T_L in CT on every date (UK and US clocks change on different dates),
  the ECB reference rate instant, the Tokyo 9:55 fix instant in CT, the
  Tokyo business-day calendar and gotobi dates (Japanese holidays), and
  the month-end dates the members use.
- K3-mehedge-01's index histories (E.2b open decision 10: they are not
  GLBX data and step 2 cannot buy them). Its entry trades an exposure only
  if its free daily index history is obtained. Task 1b's worker tries to
  obtain each free history the entry names (the STOXX daily file for the
  EURO STOXX 50, and the Nikkei 225 from Nikkei Inc. or FRED series
  NIKKEI225), covering 2019-04-01..2026-06-19, saves the raw file with its
  source URL and sha256 under data/vendor/, and checks it for gaps. The
  member reads the monthly signal as a literal table in the cluster
  package (E.3 L-01), each value built only from closes available before
  its entry time. An exposure whose history cannot be obtained free is not
  traded, as the entry says: it adds no trial, and the return names it for
  the user. No purchase, no paid source, no login.
- The ports read the frozen D6 FX row. Catalog section 7 items are settled
  by the frozen text and E.1's rulings, and each reading is logged.
- Commit: exactly the K3 member modules, tests, specs, release check, the
  index files if obtained, audit, rulings and cluster freeze file, message
  "K3 member freeze" with the cluster freeze sha256 and this repository's
  attribution lines.
- Program N after Part 3: Part 2's figure plus the K3 trials screened.
  K3's confirmation purchase: 6E, 6A, 6B, 6C, 6J, 6S and 6N, $49.34 in
  reports/stage_e2b_step2_quotes.md (a top-up is needed).
- Return document: reports/E.4c_RETURN.md, the same eight sections.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, ETA | lead | opus | xhigh | first | gates the session |
| H1 Harness fix and tests | HarnessFixer-OpusXHigh | opus | xhigh | parallel with 1 and 1b | frozen code every cluster depends on |
| H2 K2 regression replay | lead runs it | opus | xhigh | after H1 | proves no number moved |
| H3 Harness review | HarnessReviewer-FableXHigh | fable | xhigh | after H2 | an independent model checks a frozen-code change |
| H4 Rulings, manifest v4, commit | lead | opus | xhigh | after H3 | reserved to the lead |
| 1 Member specs | lead | opus | xhigh | after 0, parallel with H | readings of frozen text, reserved to the lead |
| 1b Release-date check | ReleaseChecker-OpusMed | opus | medium | parallel with 1 and H | web lookups against fixed drop rules, no judgment on results |
| 2 Code the ports and ovr | MemberCoder-A-OpusXHigh | opus | xhigh | after 1, parallel with B | strategy code |
| 2 Code the event members | MemberCoder-B-OpusXHigh | opus | xhigh | after 1 and 1b, parallel with A | strategy code with release instants |
| 3 Fidelity audit | MemberAuditor-K4-FableXHigh | fable | xhigh | after 2 | an independent model checks code against the declaration |
| 4 Rulings, cluster freeze, commit | lead | opus | xhigh | after 3 and H4 | reserved to the lead |
| 5 Screening run | lead runs the frozen command | opus | xhigh | after 4 | a frozen command, the lead watches it |
| 6 Recomputation | MemberAuditor-K4-FableXHigh, resumed | fable | xhigh | after 5 | every tier-deciding number gets an independent check |
| 7 Read the result, return | lead | opus | xhigh | after 6 | reserved to the lead |
| Part 2 (K5), Tasks 1 to 7 | as Part 1, auditor MemberAuditor-K5-FableXHigh | as Part 1 | as Part 1 | after Part 1 | same pattern, fresh workers |
| Part 3 (K3), Tasks 1 to 7 | as Part 1, auditor MemberAuditor-K3-FableXHigh | as Part 1 | as Part 1 | after Part 2 | same pattern, fresh workers |

At most 4 workers at once. Workers write files and return paths.

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. At most 4 concurrent. Small tasks needing no isolation go inline.
    4. Collect results as files plus short summaries.
    5. Verify every number entering a verdict with an independent fable
       xhigh worker.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/<stage>_STATE.md after each task.

============================================================
VERIFICATION
============================================================

- The harness change is proven numerically inert by the K2 regression
  (Task H2) and reviewed by HarnessReviewer-FableXHigh (Task H3), which
  wrote none of it.
- The member code is audited against the frozen entries before it runs
  (Task 3), and the screen figures and tiers are recomputed after it runs
  (Task 6), both by MemberAuditor-K4-FableXHigh, which wrote none of it.
- The lead rules on every finding in writing. It never re-runs a check or
  a member to get a different answer.
- If Fable runs out, the checks stay pending and no tier is final.

============================================================
WHAT NOT TO DO
============================================================

- No harness change beyond refusal routing and the trip-list file.
- No K2 tier re-decided, and no E.3 record touched.
- No member rule changed from its frozen entry.
- No RBOB, ULSD, silver or platinum trial.
- No run before the cluster freeze commit, and one run per K4 member.
- No bar outside the research window, and no direct bar reads.
- No purchase, no paid data, no power check, no confirmation list.
- No edit to any other frozen file or manifest.
- No push, and no commit beyond the four named.
- No write to REGISTRATION.md. No edit to docs/NULL_CRITERIA.md.

============================================================
DELIVERABLE: THREE RETURN DOCUMENTS
============================================================

Write reports/E.4_RETURN.md for Part 1 (the harness and K4),
reports/E.4b_RETURN.md for K5 and reports/E.4c_RETURN.md for K3. The
planning chat reads these three files to review the session. Each has
these fixed sections, in order (Parts 2 and 3 leave the harness items
out):

1. Verdict summary, at most 200 words: the harness fix (v4 sha256 and
   commit, or reverted and why), the K2 regression result, K4 trials coded,
   frozen and run, the cluster freeze sha256 and commit, the Tier A and
   Tier B trials with their screen figures in one short table, any member
   unimplementable or refused, releases dropped or unverifiable, the
   program N after this session, and what K4's confirmation session needs.
2. Guardrail evidence: the start and end checks verbatim, the manifest
   checks (old and new harness sha256), the ledger diff, `git status
   --short` and `git diff --stat` at the end.
3. Results per task: the harness diff summary, the regression table, the
   specs and every lead reading, the release check, the modules and their
   tests, the audit findings, the screen per trial, the labels, the MLL
   liquidation counts, the tiers.
4. Delegation record: one row per spawn with agent name, worker file,
   model, effort, objective, status and deviations.
5. Verification: each Fable finding from both workers, the lead's ruling
   and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. What the next session must do first: the push the planning chat owes,
   the frozen hashes (harness v4, K4 cluster freeze), the funding status
   for K4's confirmation, and any blocker.
8. Session cost: the final ETA table (one row per task and per spawn,
   actual start and end, time taken, tokens from the transcripts, status)
   and the per-model token table, per CLAUDE.md. Never estimated.

Also write one short dated progress.md entry per part that points to its
return document, and one line per part in docs/STAGES.md. When all three
parts are done, add a final section to reports/E.4_RETURN.md: one table of
every screened trial across K4, K5 and K3 with its tier, and the program N
after the session.

The last thing before ending each part: list every open choice in section
6 of its return document.

END PROMPT
