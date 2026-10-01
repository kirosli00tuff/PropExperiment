STAGE E.9 "K8 CROSS-MARKET: CODE, AUDIT AND FREEZE THE THREE MEMBERS, AND SCREEN THEM ON THE RESEARCH WINDOW (NO PURCHASE)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stages E.3 to E.8 screened K2, K4, K5, K3, K7, K1 and K6 (program
N = 194 after E.8, reports/E.8_RETURN.md). This session screens K8, the
cross-market cluster, whose members read one market to trade another, on
its own. K8 runs alone, as the user asked (V15, V17), because its members
differ in kind: every trial has a signal leg on one product and a traded
leg on another. It is the last cluster. The ML route follows. This session
writes the member specs from the frozen catalog entries, checks the
research-window event dates and any free external series the members read,
codes the members, has a fresh Fable worker audit each module against its
entry, freezes the member code by hash, runs every trial once through the
frozen runner on the research window (trade dates 2025-04-01..2026-06-19),
and has the same Fable worker recompute every screen figure. It stops
there. The confirmation comes later.

Trials (catalog section 5 as amended, E.2a vehicles): K8-flight-01 in
two variants, H30 and HEOD (signal leg the S&P 500 on MES, traded leg gold
on MGC at q_c = 1), K8-oilcad-01 (signal leg crude on MCL, traded leg CAD
on 6C, undersized at 1 contract, screened as E.3 screened ZT and ZF, E.3
L-20), and K8-wkndbtc-01 (signal leg bitcoin on MBT, traded leg the
Nasdaq-100 on MNQ at q_c = 1, labelled source-overlap). Expected trials: 4.
K8-ml-01 is excluded (U6). Every leg's research-window bars are owned
from step 1, so nothing is bought.

Decisions in force for the legs (docs/DECISIONS.md V16, the user,
2026-09-28, which settle the catalog's section 6 items 1 to 4):
- A trade date is dropped if it is a roll-blackout date of ANY leg the
  member reads, signal legs included (D4's union). The catalog's C5
  wording that keeps signal-leg rolls yields to D4. The harness already
  does this.
- Every leg, signal legs included, starts at its own S from the start
  rule (D4), and every leg passes the D9 coverage check (D4, the catalog's
  C13).
- A signal leg on a root with no D6 session record reads its micro twin
  (ES as MES, BTC as MBT). The K8 members already read MES and MBT, so
  this changes no text. A leg on NKD, MET or 6M is refused by name.
- Crude legs read MCL. Full-size CL is a later question for the
  confirmation session, only if its power check fails and the user agrees
  (U8).
The catalog's other section 6 items are settled by the frozen text and
E.1's rulings, and each reading is logged. Item 11 (bitcoin's 24/7
regime from 2026-05-29) is recorded in the return for the user, with the
count of research-window dates on each side of the change.

The lead takes the count from the freeze declarations and logs any
difference.

The user may run this session unattended, across usage windows. The
auto-retry launcher resumes it with "read the STATE file first", so
reports/stage_e9_STATE.md names, after every task, the task finished, the
hashes in force and the next task.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: this is E.3's and E.4's pattern again,
translating frozen, fully specified entries into code and running a frozen
runner. The silent failure to guard against is a module that runs cleanly
but implements something other than its entry. CLAUDE.md routes strategy
code to opus at xhigh and independent checks to Fable. Ultracode stays
off: at most two coding workstreams at a time.

Usage: follows CLAUDE.md's context-hygiene rules. Read the catalog by
member section, never whole. Fable is used by one worker,
MemberAuditor-K8-FableXHigh: the fidelity audit (Task 3), then, resumed
with a small brief, the recomputation (Task 6). If Fable is unavailable
when Task 3 starts, finish Task 2 and stop before Task 4. Never substitute
opus for a Fable check. Compute: the ThinkPad under the overnight profile.
E.3 (one cluster, 44 trials) took 101 minutes and 84M tokens. Expect about
1.5 hours here: few trials, but every module joins two products.

Do not stop to ask. Decide, log the choice under Open choices in the return
document, and continue. The only stops are the ones this prompt names, a
decision that cannot be undone and could reasonably go either way, or a
guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- write the member specs (Task 1)
- check the research-window event dates and fetch any free external series
  a member reads (Task 1b)
- code the members under strategy/members/k8/ (Task 2)
- audit each module against its frozen entry (Task 3)
- freeze the member code with the cluster-freeze helper, and commit (Task 4)
- run each trial once through the frozen runner on the research window
  (Task 5)
- recompute the screen figures independently (Task 6)
- read the result (Task 7)

This stage does NOT:
- buy anything, or read any bar outside the research window
- change the harness. A member that the frozen harness cannot run is
  labelled and reported, never worked around with a harness edit.
- run a power check, build start dates, hash a confirmation list, or touch
  any confirmation window
- change any member's rule, parameter, threshold, window or trade count from
  its frozen entry. A member the lead finds unimplementable as written is
  labelled and reported, never rewritten.
- re-run a member after seeing its result, with any change. Each member runs
  once. A crash is fixed only in code the audit covered, re-audited, and the
  member re-run from scratch, and the crash is reported.
- touch any other cluster, K8, the ML route, holdout-1 or holdout-2, live/,
  ops/, or any TopstepX credential or API
- use a paid data source or a login for any external series
- edit any frozen file or manifest, docs/NULL_CRITERIA.md,
  docs/NULL_CRITERIA_E.md or any earlier stage's records
- write to REGISTRATION.md (it stays 0 bytes)
- push. The session makes exactly the one commit Task 4 names.

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md (including the page-fetch fallback) and
   docs/ORCHESTRATION.md. On any conflict CLAUDE.md wins, and the conflict
   is logged.
2. docs/DECISIONS.md V13 to V15.
3. reports/E.4_RETURN.md sections 5 and 6, reports/E.4b_RETURN.md
   section 6, reports/E.4c_RETURN.md section 6, and reports/E.6_RETURN.md,
   E.7_RETURN.md and E.8_RETURN.md section 6 (E.6's MBT readings and
   E.7's MNQ readings bear directly on K8's legs): the lead readings are precedents. Where an entry uses the
   same text (the ports, "the bar at hh:mm", named entry bars, instrument
   guards, integer ticks, event tables as literal tables in the cluster
   package, free external series as hashed files under data/vendor/ read
   as literal tables), adopt the earlier reading and cite it. Where the
   text differs, read it fresh.
4. reports/E.5_RETURN.md section 1 (harness v6 is in force) and the holiday
   rows harness v5 added.
5. reports/stage_e0_catalog_K8.md: its header (conventions C1 to C15,
   including C4's cross-leg synchronization, C6's guarded-entry skip rule
   and C13's coverage, with every bracketed note), the three member
   sections K8-flight-01, K8-oilcad-01 and K8-wkndbtc-01, the trial count
   table (section 5) and the questions (section 6) as amended.
   reports/E.2b_RETURN.md, the multi-leg engine and alignment notes
   (screening/stage_e_engine.py, screening/stage_e_align.py,
   tests/test_stage_e_alignment.py).
6. reports/stage_e1_changes.md for K8's edits, the source-window
   amendment for its labels, K8's rows in reports/stage_e2a_vehicles.md
   and stage_e2a_epsilon.md, and docs/STAGE_E_DESIGN.md (FROZEN) D2, D5, D6
   (the session rows), D8 and D9.
7. strategy/stage_e/_template.py and interface.py (the member contract and
   import allowlist), screening/stage_e_freeze.py (write_cluster_freeze),
   screening/stage_e_runner.py, and the release calendar the runner loads.

============================================================
GUARDRAILS
============================================================

CLAUDE.md invariants apply in full. This stage adds:

- Every Stage E command takes `--harness-sha256
  9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87` (v6),
  and runs with a fresh `PYTHONPYCACHEPREFIX` outside the repository. A
  preflight refusal stops the session with a named refusal.
- The E.1, E.2a ML and harness manifests, and the K2, K4, K5, K3, K7, K1 and K6 cluster
  freezes, verify at start and at end.
- Research window only: 2025-04-01..2026-06-19, read by the runner. No
  script of this session opens a bar file directly.
- One run per member. The member code is frozen by Task 4 before Task 5
  runs anything on data.
- No spend. The ledger is unchanged at the end.
- Holdout status at start and end: all_ok, 0 unlocks.
- REGISTRATION.md stays 0 bytes. No TopstepX reference of any kind.
- Web access (Task 1b only): read-only fetches of public schedule, archive
  and data pages, with CLAUDE.md's page-fetch fallback. No data API needing
  a key, no login, no paid source. Stay within CLAUDE.md's WebSearch budget
  rule.

Start and end checks, quoted verbatim in the return document: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the manifest and freeze checks, the ledger total, `uv run
pytest -q` (expected at start: E.8's end result).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Inputs: the context files.
- Output: reports/stage_e9_STATE.md and the estimate ETA table.
- Done when: the start checks pass, HEAD is the commit holding this prompt
  or a descendant with a clean tree, and the runner's preflight accepts v6.
- Failure path: any mismatch or refusal stops the session with a named
  refusal.

============================================================
TASK 1: MEMBER SPECIFICATIONS (LEAD)
============================================================

- Owner: lead.
- Output: reports/stage_e9_member_specs.md: for each member, the exact rule as
  the frozen entry states it after every amendment, with line references:
  exposures traded, the signal leg and the traded leg, with the exact bars each reads, decision and entry times, exit, hold, flatten,
  order type, sizing at q_c, every parameter as a literal, the event
  instants and values it reads with their availability times, the trade
  count in N, and the Topstep checks. An ordinal table of the trials,
  catalog order (flight-01 H30, flight-01 HEOD, oilcad-01, wkndbtc-01). Where the entry leaves a detail open, the narrowest reading,
  logged. Never a widened rule.
- Done when: every field of every member has a line reference, a precedent
  or a logged reading.
- Failure path: a member that cannot be implemented without a choice that
  could change its result materially is labelled "unimplementable as
  frozen", reported for the user, and not coded.

============================================================
TASK 1b: RESEARCH-WINDOW EVENTS AND FREE SERIES (WORKER)
============================================================

- Owner: ReleaseChecker-OpusMed, worker-medium on opus.
- Output: reports/stage_e9_release_check.md and .json, checking any dated input a K8 member reads in the research window: the
  D9.5a release instants that C6's skip rule applies to each traded leg,
  the Friday 14:59 and Sunday 17:59 CT clock points K8-wkndbtc-01 reads
  (with the MBT session record and E.6's trade-date readings), the date
  bitcoin futures moved to continuous trading (catalog item 11) and the
  research-window dates on each side of it, and, for every member, the
  research-window dates the union of its legs' roll blackouts removes.
  Each item keep, drop or unverifiable, with a source URL.
- Failure path: an item that cannot be verified is kept as the frozen input
  gives it and labelled. A member whose event set holds an unverifiable
  item carries "calendar partly unverified" into the return.

============================================================
TASK 2: CODE THE MEMBERS
============================================================

- Owners, in parallel, each worker-xhigh on opus: MemberCoder-A-OpusXHigh
  (K8-flight-01, both variants) and MemberCoder-B-OpusXHigh (K8-oilcad-01 and K8-wkndbtc-01).
- Output: one module per member under strategy/members/k8/, from the
  template, using only its import allowlist, with unit tests on synthetic
  bars (tests/test_k8_members*.py) pinning each rule's decisions: entry and
  exit times, the event window, the flatten, a missing bar at a decision
  time, a signal bar from the other leg arriving late or missing (no trade, no forward fill), a roll date on the signal leg only, a guarded entry skipped under C6, and the Friday and Sunday clock points.
- Done when: every module passes its tests and the full suite passes.
- Failure path: a coder that finds its spec ambiguous stops and reports to
  the lead, who rules in writing. The coder does not choose.

============================================================
TASK 3: FIDELITY AUDIT (FABLE XHIGH)
============================================================

- Owner: MemberAuditor-K8-FableXHigh, worker-xhigh on fable. It wrote none
  of the code.
- Output: reports/stage_e9_member_audit.md, each finding BLOCKING, SHOULD FIX or
  NOTE, with file and line.
- Done when: for every member, the auditor has checked that the module
  implements the frozen entry and nothing more (every literal, time,
  direction, exit, size, event instant and its availability, drop and
  flatten, and no input read before its availability time), that each lead
  reading is the narrowest one, and that every literal table equals its
  source. For K8 especially: that no signal-leg bar is read before it has
  closed on the UTC minute grid, that a missing or late signal bar blocks
  the trade instead of being forward-filled, that the traded leg's fill
  comes strictly after the signal is known, and that the union of the
  legs' roll blackouts is applied. The tests must fail on a mutant for every rule they pin (the E.4
  K5 and K3 lessons).
- Failure path: if Fable is unavailable, stop before Task 4.

============================================================
TASK 4: RULINGS AND THE CLUSTER FREEZE (LEAD)
============================================================

- Owner: lead.
- Output: reports/stage_e9_member_rulings.md, the fixes, the cluster freeze
  file, and one commit holding exactly the member modules, their tests, the
  specs, the release check, any free series file, the audit, the rulings
  and the cluster freeze file. Message "K8 member freeze" with the cluster
  freeze sha256 and this repository's attribution lines.
- Done when: every BLOCKING and SHOULD FIX finding has a ruling and its fix,
  the full suite passes, and the commit exists.
- Failure path: a BLOCKING finding that cannot be fixed within the frozen
  entry makes that member "unimplementable as frozen". It is not run, and
  the others proceed.

============================================================
TASK 5: THE SCREENING RUN (LEAD RUNS THE FROZEN COMMAND)
============================================================

- Owner: lead.
- `PYTHONPYCACHEPREFIX=<fresh dir> nice -n 10 uv run python -m
  screening.stage_e_runner --harness-sha256 <v6> --cluster K8 --all
  --window research --research-root data/processed --step2-root
  data/processed_step2 --out-dir reports/stage_e9_k8_screen`
- Output: the runner's records and trip lists, coverage and trade-rate
  labels, the D5 screen figures and the tiers. Power is `not_run`.
- Done when: every coded trial has a result or a named refusal, and the
  runner has written the tiers.
- Failure path: a crash stops that member. The fix goes through Tasks 2 to 4
  again, and the member runs from scratch. Report the crash and the fix.

============================================================
TASK 6: RECOMPUTATION (FABLE RESUMED)
============================================================

- Owner: MemberAuditor-K8-FableXHigh, resumed with a small brief.
- Output: a second section in reports/stage_e9_member_audit.md: every trial's
  screen mean and daily t recomputed from its series in the auditor's own
  code, each tier checked against D5 and OC-H, two trials' series (one port,
  one other member) rebuilt from their trip lists and the cost table, each
  event member's trade count reconciled with its checked event table, and
  the MLL liquidation count per trial. Each item VERIFIED, VERIFIED WITH
  NOTES or DISCREPANCY.
- Failure path: a DISCREPANCY is ruled on by the lead in writing. A tier
  with an unresolved discrepancy is marked "unverified".

============================================================
TASK 7: READ THE RESULT (LEAD)
============================================================

- Owner: lead.
- Output: in the return document, per trial: trips, screen figures, labels,
  MLL liquidations and tier. The program N after the session:
  194 plus the K8 trials screened, counted as E.4 counted (N before this stage: 194 (after E.8)).
  What K8's confirmation would need: the step 2 quote for every leg root of the four trials (K8 $29.65 quoted in reports/E.2b_RETURN.md for the cluster set), and the
  top-up, since acct-2 holds $0.33.
- Done when: the tables are written from the runner's files.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, ETA | lead | opus | xhigh | first | gates the session |
| 1 Member specs | lead | opus | xhigh | after 0 | readings of frozen text, reserved to the lead |
| 1b Event checks, free series | ReleaseChecker-OpusMed | opus | medium | parallel with 1 | web lookups against fixed rules, no judgment on results |
| 2 Code, coder A | MemberCoder-A-OpusXHigh | opus | xhigh | after 1, parallel with B | strategy code |
| 2 Code, coder B | MemberCoder-B-OpusXHigh | opus | xhigh | after 1 and 1b, parallel with A | strategy code with event instants |
| 3 Fidelity audit | MemberAuditor-K8-FableXHigh | fable | xhigh | after 2 | an independent model checks code against the declaration |
| 4 Rulings, freeze, commit | lead | opus | xhigh | after 3 | reserved to the lead |
| 5 Screening run | lead runs the frozen command | opus | xhigh | after 4 | a frozen command, the lead watches it |
| 6 Recomputation | MemberAuditor-K8-FableXHigh, resumed | fable | xhigh | after 5 | every tier-deciding number gets an independent check |
| 7 Read the result, return | lead | opus | xhigh | last | reserved to the lead |

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

- The member code is audited against the frozen entries before it runs
  (Task 3), and the screen figures and tiers are recomputed after it runs
  (Task 6), both by MemberAuditor-K8-FableXHigh, which wrote none of it.
- The lead rules on every finding in writing. It never re-runs a check or a
  member to get a different answer.
- If Fable runs out, the checks stay pending and no tier is final.

============================================================
WHAT NOT TO DO
============================================================

- No harness change, and no member rule changed from its frozen entry.
- No run before the cluster freeze commit, and one run per member.
- No bar outside the research window, and no direct bar reads.
- No purchase, no paid data, no login, no power check, no confirmation list.
- No work on any other cluster.
- No edit to any frozen file, manifest or earlier record.
- No push, and no commit beyond the one named.
- No write to REGISTRATION.md.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.9_RETURN.md. The planning chat reads this one file to
review the session. Fixed sections, in order:

1. Verdict summary, at most 200 words: trials coded, frozen and run, the
   cluster freeze sha256 and commit, the Tier A and Tier B trials with
   their screen figures in one short table, any member unimplementable,
   refused or not traded, event items dropped or unverifiable, the program
   N after the session, and what K8's confirmation would need.
2. Guardrail evidence: the start and end checks verbatim, the manifest and
   freeze checks, the ledger diff, `git status --short` and `git diff
   --stat` at the end.
3. Results per task: the specs and every lead reading, the event check, the
   modules and their tests, the audit findings, the screen per trial, the
   labels, the MLL liquidation counts, the tiers.
4. Delegation record: one row per spawn with agent name, worker file, model,
   effort, objective, status and deviations.
5. Verification: each Fable finding in both parts of the audit, the lead's
   ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. What the next session must do first: the push the planning chat owes,
   the frozen hashes, the funding a confirmation would need, and any blocker
   or question for the user.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
