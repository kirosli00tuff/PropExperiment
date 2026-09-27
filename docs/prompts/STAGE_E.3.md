STAGE E.3 "K2 RATES: CODE, AUDIT AND FREEZE THE EIGHT MEMBERS, THEN SCREEN THEM ON THE RESEARCH WINDOW (NO PURCHASE, NO CONFIRMATION DATA)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.2b froze the Stage E harness (commit 273c27b, manifest
reports/stage_e2b_harness_freeze.json, sha256
cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45). This
session is the first cluster session of Stage E, cluster K2, the Treasury
futures (ZT, ZF, ZN, TN, ZB, UB). It codes K2's eight active catalog
members from their frozen entries (reports/stage_e0_catalog_K2.md, as
amended by E.1 and E.2a), has an independent Fable worker check that each
module implements its entry and nothing else, freezes the member code by
hash, and runs every member once through the frozen Stage E runner on the
research window (trade dates 2025-04-01..2026-06-19). The runner computes
the D5 screen and assigns each member to Tier A, Tier B or excluded. A
second Fable check recomputes the screen figures. It stops there. The D4
power check needs each product's start date S_X, which needs the step 2
history, so it runs in K2's confirmation session after the user funds
acct-2. That session also hashes the confirmation list and runs it once.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: the work is translating eight frozen,
fully-specified entries into code and running a frozen runner. The silent
failure to guard against is a module that runs cleanly but implements
something other than its entry. CLAUDE.md routes strategy code to opus at
xhigh, and the fidelity check to an independent Fable worker. The lead's
judgment is reserved for rulings and for reading the result. Ultracode
stays off: eight small modules, routed through the worker files.

Usage: follows CLAUDE.md's context-hygiene rules. Read the catalog by
member section, never whole. Fable is used by one worker,
MemberAuditor-FableXHigh: first the fidelity audit of the coded members
before the cluster freeze (Task 3), then, resumed with a small brief, the
recomputation of the screen figures (Task 6). If Fable is unavailable when
Task 3 starts, do not freeze or run: finish Task 2, and mark the rest
pending. Never substitute opus for a Fable check. Compute: the ThinkPad
under the overnight profile (the Windows PC is not set up yet, E.2c).
This session's runs are small: eight members on six products over about
300 research dates.

Do not stop to ask. Decide, log the choice under Open choices in the
return document, and continue. The only stops are the ones this prompt
names, a decision that cannot be undone and could reasonably go either
way, or a guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- code K2's eight active members under strategy/members/k2/ from the
  member template (Task 2)
- audit each module against its frozen entry (Task 3)
- freeze the member code with the harness's cluster-freeze helper (Task 4)
- run the eight members once through the frozen runner on the research
  window, and record the D5 screen and tiers (Task 5)
- recompute the screen figures independently (Task 6)

This stage does NOT:
- buy anything, or read any bar outside the research window. The step 2
  history is bought in K2's confirmation session.
- run the D4 power check, build start dates, hash the confirmation list, or
  touch the confirmation window. All of that belongs to K2's confirmation
  session.
- change any member's rule, parameter, threshold, window or trade count
  from its frozen entry. A member the lead finds unimplementable as
  written is labelled and reported, never rewritten.
- re-run a member after seeing its result, with any change. Each member
  runs once. A run that crashes is fixed only in code the audit covered,
  re-audited, and re-run from scratch, and the crash is reported.
- touch the ML route, any other cluster, holdout-1 or holdout-2, live/,
  ops/, or any TopstepX credential or API
- edit any frozen file or manifest, docs/NULL_CRITERIA.md, or
  reports/stage_d1f_confirmation_list.md
- write to REGISTRATION.md (it stays 0 bytes)
- push. The session makes exactly the one commit Task 4 names.

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md and docs/ORCHESTRATION.md. This prompt does not repeat them.
   On any conflict CLAUDE.md wins, and the conflict is logged.
2. reports/E.2b_RETURN.md, section 7, "What K2's screening session needs
   from this harness", items 1 to 5, and the decisions list.
3. reports/stage_e0_catalog_K2.md: the header (section 0) and the eight
   member sections K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-aucpre-01,
   K2-aucpost-01, K2-fomcpost-01, K2-predrift-01 and K2-monthend-01, with
   every bracketed E.0, E.1 and E.2a note. K2-ml-01 is excluded (U6).
   reports/stage_e1_changes.md for any K2 edit. The source-window
   amendment (reports/stage_e2a_source_window_amendment.md) for K2's
   labels.
4. docs/STAGE_E_DESIGN.md (FROZEN): D2 (vehicles and q_c), D5 (the screen
   and tiers), D6 (the core ports CP1 to CP3 and the session table), D8
   (costs and the event window), D9 (the constraint set, the coverage
   check, the trade-rate floor).
5. reports/stage_e2a_vehicles.md, K2 rows: ZT and ZF undersized at 1
   contract, ZN, TN, ZB and UB chosen at 1 contract. reports/stage_e2a_epsilon.md,
   K2 rows.
6. strategy/stage_e/_template.py and strategy/stage_e/interface.py (the
   member contract and its import allowlist), screening/stage_e_freeze.py
   (write_cluster_freeze), screening/stage_e_runner.py (the command in the
   E.2b return, section 7, item 3), and the release calendar the runner
   loads (auction results, FOMC, ISM Services instants).

============================================================
GUARDRAILS
============================================================

CLAUDE.md invariants apply in full. This stage adds:

- Every Stage E command takes `--harness-sha256
  cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45`, and runs
  with a fresh `PYTHONPYCACHEPREFIX` outside the repository (E.2b review
  F-2). A preflight refusal stops the session with a named refusal.
- The E.1 and E.2a freeze manifests and the E.2b harness manifest verify at
  start and at end.
- Research window only: 2025-04-01..2026-06-19, read by the runner. No
  script of this session opens a bar file directly.
- One run per member. The member code is frozen by Task 4 before Task 5
  runs anything on data.
- No spend. The ledger is unchanged at the end.
- Holdout status at start and end: both all_ok, 0 unlocks.
- REGISTRATION.md stays 0 bytes. No TopstepX reference of any kind.

Start and end checks, quoted verbatim in the return document: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the three manifest checks, `uv run pytest -q` (expected at
start: the E.2b end result).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Inputs: the context files.
- Output: reports/stage_e3_STATE.md and the estimate ETA table.
- Done when: the start checks pass, HEAD is 9ae322a or a descendant with a
  clean tree, and the runner's preflight accepts the harness sha256.
- Failure path: any mismatch or refusal stops the session with a named
  refusal.

============================================================
TASK 1: MEMBER SPECIFICATIONS (LEAD)
============================================================

- Owner: lead.
- Inputs: the eight catalog sections and their notes.
- Output: reports/stage_e3_member_specs.md: for each member, the exact
  rule as the frozen entry states it after every amendment, with line
  references: products and vehicle, decision and entry times, exit, hold,
  flatten, order type, sizing at q_c, every parameter as a literal, the
  release instants it reads, the trade count in N, and the Topstep checks.
  Where the entry leaves a detail open, the lead writes the narrowest
  reading and logs it as an open choice. It never widens a rule.
- Done when: every field of every member has a line reference or a logged
  reading.
- Failure path: a member whose entry cannot be implemented without a
  choice that could change its result materially is labelled
  "unimplementable as frozen", reported for the user, and not coded.

============================================================
TASK 2: CODE THE MEMBERS
============================================================

- Owner: two workers, MemberCoder-A-OpusXHigh (the three core ports and
  K2-monthend-01) and MemberCoder-B-OpusXHigh (the four event members:
  K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01, K2-predrift-01), each
  worker-xhigh on opus, in parallel.
- Inputs: reports/stage_e3_member_specs.md, the template and interface,
  the D6 port definitions, the release calendar's interface.
- Output: one module per member under strategy/members/k2/, from the
  template, using only the template's import allowlist, with unit tests on
  synthetic bars (tests/test_e3_k2_members.py) that pin each rule's
  decisions on hand-built cases: entry and exit times, the event-window
  behaviour, the flatten, a missing bar at a decision time, and a release
  that moved.
- Done when: every module passes its tests and the full suite passes.
- Failure path: a coder that finds its spec ambiguous stops and reports
  to the lead, who rules in writing. The coder does not choose.

============================================================
TASK 3: FIDELITY AUDIT (FABLE XHIGH)
============================================================

- Owner: MemberAuditor-FableXHigh, worker-xhigh on fable. It wrote none of
  the code.
- Inputs: the eight catalog sections (by section), the specs file, the
  modules, their tests.
- Output: reports/stage_e3_member_audit.md, each finding graded BLOCKING,
  SHOULD FIX or NOTE, with file and line.
- Done when: for every member, the auditor has checked that the module
  implements the frozen entry and nothing more: every literal, every time,
  the direction, the exit, the sizing, the event instants and their
  availability times, the flatten, and that no input is read before its
  availability time. It also checks that each lead reading in Task 1 is
  the narrowest one.
- Failure path: if Fable is unavailable, stop before Task 4.

============================================================
TASK 4: RULINGS AND THE CLUSTER FREEZE (LEAD)
============================================================

- Owner: lead.
- Inputs: the audit.
- Output: reports/stage_e3_member_rulings.md, the fixes, the cluster
  freeze file from screening.stage_e_freeze.write_cluster_freeze, and one
  commit on main holding exactly the member modules, their tests, the
  specs, the audit, the rulings and the cluster freeze file, with a message
  naming the cluster freeze sha256 and "K2 member freeze", ending with this
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
- Inputs: the cluster freeze, the harness.
- Output: the runner's output directory reports/stage_e3_k2_screen/ with
  every member's research-window daily series, trade list, coverage and
  trade-rate labels, the D5 screen figures (mean net P&L per contract per
  day with zeros on no-trade days, daily t) and the tier assignment, all
  written by the runner.
- The command, as the E.2b return gives it:
  `PYTHONPYCACHEPREFIX=<fresh dir> uv run python -m screening.stage_e_runner
  --harness-sha256 cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45
  --cluster K2 --all --window research --research-root data/processed
  --step2-root data/processed_step2 --out-dir reports/stage_e3_k2_screen`
- Done when: every coded member has a result or a named refusal, and the
  runner has written the tiers.
- Failure path: a crash stops that member. The fix goes through Tasks 2 to
  4 again (audit and freeze), and the member runs from scratch. Report the
  crash and the fix.

============================================================
TASK 6: RECOMPUTATION (FABLE RESUMED)
============================================================

- Owner: MemberAuditor-FableXHigh, resumed with SendMessage (a small
  brief).
- Inputs: the runner's outputs, the frozen D5.
- Output: a second section in reports/stage_e3_member_audit.md: every
  member's screen mean and daily t recomputed from its daily series in
  the auditor's own code, each tier assignment checked against D5, and for
  two members (one port, one event member) the daily series rebuilt from
  the trade list and the cost table. Each item VERIFIED, VERIFIED WITH
  NOTES or DISCREPANCY.
- Done when: every item has a verdict.
- Failure path: a DISCREPANCY is ruled on by the lead in writing. A tier
  with an unresolved discrepancy is marked "unverified" and the
  confirmation session may not use it.

============================================================
TASK 7: READ THE RESULT (LEAD)
============================================================

- Owner: lead.
- Inputs: the verified outputs.
- Output: the results in the return document: per member and exposure, the
  trades, the screen figures, the labels and the tier. The cumulative
  program N after this session, as the runner counts it. What the
  confirmation session will need: the Tier A members, the Tier B members,
  and the step 2 purchase for K2's vehicles ($40.50 quoted in E.2b).
- Done when: the tables are written from the runner's files, not from
  memory of the logs.
- Failure path: none expected. A result that surprises the lead is still
  reported as computed.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, ETA | lead | opus | xhigh | first | gates the session |
| 1 Member specs | lead | opus | xhigh | after 0 | readings of frozen text, reserved to the lead |
| 2 Code the ports and month-end | MemberCoder-A-OpusXHigh | opus | xhigh | parallel with B | strategy code |
| 2 Code the event members | MemberCoder-B-OpusXHigh | opus | xhigh | parallel with A | strategy code with release instants |
| 3 Fidelity audit | MemberAuditor-FableXHigh | fable | xhigh | after 2 | an independent model checks code against the declaration |
| 4 Rulings, cluster freeze, commit | lead | opus | xhigh | after 3 | reserved to the lead |
| 5 Screening run | lead runs the frozen command | opus | xhigh | after 4 | a frozen command, the lead watches it |
| 6 Recomputation | MemberAuditor-FableXHigh, resumed | fable | xhigh | after 5 | every tier-deciding number gets an independent check |
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
  (Task 6), both by MemberAuditor-FableXHigh, which wrote none of it.
- The lead rules on every finding in writing. It never re-runs a check or
  a member to get a different answer.
- If Fable runs out, the checks stay pending and no tier is final.

============================================================
WHAT NOT TO DO
============================================================

- No member rule changed from its frozen entry.
- No run before the cluster freeze commit, and one run per member.
- No bar outside the research window, and no direct bar reads.
- No purchase, no power check, no confirmation list.
- No edit to any frozen file or manifest.
- No push, and no commit beyond the cluster freeze commit.
- No write to REGISTRATION.md. No edit to docs/NULL_CRITERIA.md.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.3_RETURN.md. The planning chat reads this one file to
review the session. Fixed sections, in order:

1. Verdict summary, at most 200 words: members coded, frozen and run, the
   cluster freeze sha256 and commit, the Tier A and Tier B members with
   their screen figures in one short table, any member unimplementable or
   refused, the program N after this session, and what K2's confirmation
   session needs (purchase amount, power check, list hash).
2. Guardrail evidence: the start and end checks verbatim, the manifest
   checks, the ledger diff, `git status --short` and `git diff --stat` at
   the end.
3. Results per task: the specs and every lead reading, the modules and
   their tests, the audit findings, the screen per member and exposure,
   the labels, the tiers.
4. Delegation record: one row per spawn with agent name, worker file,
   model, effort, objective, status and deviations.
5. Verification: each Fable finding in both parts, the lead's ruling and
   the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. What the next session must do first: the push the planning chat owes,
   the frozen hashes, the funding the user owes for K2's confirmation, and
   any blocker.
8. Session cost: the final ETA table (one row per task and per spawn,
   actual start and end, time taken, tokens from the transcripts, status)
   and the per-model token table, per CLAUDE.md. Never estimated.

Also write one short dated progress.md entry that points to the return
document, and one line in docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
