STAGE E.6 "SCREEN K6 AGS AND LIVESTOCK, K7 CRYPTO AND K1 EQUITY INDEX ON THE RESEARCH WINDOW, ONE CLUSTER AFTER ANOTHER (NO PURCHASE)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.4 screened K4, K5 and K3, and Stage E.5 confirmed K4 null
(commit 4c8010f). This session screens the next three clusters in one
unattended run, as E.4 did: Part 1 (E.6a) K6, grains, oilseeds and
livestock, Part 2 (E.6b) K7, bitcoin, and Part 3 (E.6c) K1, the equity
indexes other than MES. For each cluster it writes the member specs from
the frozen catalog entries, checks the research-window event dates and
free external series the members read, codes the members, has a fresh
Fable worker audit each module against its entry, freezes the member code
by hash, runs every trial once through the frozen runner on the research
window (trade dates 2025-04-01..2026-06-19), and has the same Fable worker
recompute every screen figure. Each part has its own freeze commit and
return document. A part that fails does not stop the next one unless this
prompt says so. K8, the cross-market cluster, is not in this session: the
user runs it on its own later. Confirmations come later too.

Decision in force: docs/DECISIONS.md V15 (the user, 2026-09-27): K1 is
screened now, after K6 and K7, instead of "only if needed" (U3). K8 runs
alone in its own session.

Traded exposures (reports/stage_e2a_vehicles.md), expected trials:
- K6: ZW, ZS, ZM, ZL, HE, LE at q_c = 1, and ZC undersized at 1 contract
  (screened as E.3 screened ZT and ZF, E.3 L-20). 27 trials: three ports
  on seven exposures (21), K6-crushgap-01 on ZS, K6-limitcont-01 on HE and
  LE, K6-wasdepre-01 on ZC and ZS, K6-wasdepost-01 on ZC. K6-ovr-01 is
  excluded (E.0) and K6-ml-01 is excluded (U6).
- K7: bitcoin through MBT, undersized at 1 contract. 6 trials: the three
  ports, K7-expiry-01, K7-rev2h-01, K7-montrend-01. K7-ml-01 is excluded.
- K1: Nasdaq-100 through MNQ at q_c = 1, Russell 2000 through M2K at 3,
  Dow through MYM at 3. 11 trials: three ports on three exposures (9),
  K1-vxnband-01 and K1-vwap-01 on MNQ. K1-predrift-01 is excluded (E.0) and
  K1-ml-01 is excluded (U6).
The lead takes each count from its freeze declarations and logs any
difference. Expected total: 44 trials.

The user runs this session unattended, possibly across several usage
windows. The auto-retry launcher resumes it with "read the STATE file
first". So the master checkpoint is reports/stage_e6_STATE.md: after
every task it names the part, the task finished, the hashes in force and
the next task. Each part also keeps its own STATE file.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: this is E.3's and E.4's pattern a fourth time,
translating frozen, fully specified entries into code and running a
frozen runner. The silent failure to guard against is a module that runs
cleanly but implements something other than its entry. CLAUDE.md routes
strategy code to opus at xhigh and independent checks to Fable. Ultracode
stays off: at most two coding workstreams at a time.

Usage: follows CLAUDE.md's context-hygiene rules. Read each catalog by
member section, never whole, and read each part's files when the part
starts. At the end of each part, write its return document and STATE file,
and carry into the next part only the hashes in force and the next part's
inputs. Do not re-read an earlier part's worker outputs. Fable is used by
three workers, each fresh: MemberAuditor-K6-FableXHigh,
MemberAuditor-K7-FableXHigh and MemberAuditor-K1-FableXHigh, each for its
cluster's Task 3 and resumed with a small brief for its Task 6. If Fable is
unavailable when a Fable task is due, finish the work that needs no Fable
check (specs, event checks, coding and unit tests for the remaining
clusters) and stop before the next freeze. Never substitute opus for a
Fable check. Compute: the ThinkPad under the overnight profile. E.4 (three
clusters, 53 trials) took 4.6 hours of work and 320M tokens. Expect about 4
hours here.

Do not stop to ask. Decide, log the choice under Open choices in the return
document, and continue. The only stops are the ones this prompt names, a
decision that cannot be undone and could reasonably go either way, or a
guardrail conflict.

============================================================
SCOPE
============================================================

This stage does, for K6, then K7, then K1:
- write the member specs (Task 1)
- check the research-window event dates and fetch any free external
  series a member reads (Task 1b)
- code the members under strategy/members/k6/, k7/ and k1/ (Task 2)
- audit each module against its frozen entry (Task 3)
- freeze the member code with the cluster-freeze helper, and commit
  (Task 4)
- run each cluster's trials once through the frozen runner on the research
  window (Task 5)
- recompute the screen figures independently (Task 6)
- read the result (Task 7)

This stage does NOT:
- buy anything, or read any bar outside the research window
- change the harness. A member that the frozen harness cannot run is
  labelled and reported, never worked around with a harness edit.
- run a power check, build start dates, hash a confirmation list, or touch
  any confirmation window
- change any member's rule, parameter, threshold, window or trade count
  from its frozen entry. A member the lead finds unimplementable as written
  is labelled and reported, never rewritten.
- re-run a member after seeing its result, with any change. Each member
  runs once. A crash is fixed only in code the audit covered, re-audited,
  and the member re-run from scratch, and the crash is reported.
- touch K8, the ML route, any other cluster's code or records, holdout-1
  or holdout-2, live/, ops/, or any TopstepX credential or API
- use a paid data source or a login for any external series
- edit any frozen file or manifest, docs/NULL_CRITERIA.md,
  docs/NULL_CRITERIA_E.md or any earlier stage's records
- write to REGISTRATION.md (it stays 0 bytes)
- push. The session makes exactly three commits, one cluster freeze
  commit per part.

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md and docs/ORCHESTRATION.md. On any conflict CLAUDE.md wins,
   and the conflict is logged.
2. docs/DECISIONS.md V13 to V15.
3. reports/E.4_RETURN.md sections 5 and 6, reports/E.4b_RETURN.md
   section 6 and reports/E.4c_RETURN.md section 6: the lead readings
   (E.3 L-01 to L-23 and the E.4 K4-L, K5-L and K3-L readings) are
   precedents. Where an entry uses the same text (the ports, "the bar at
   hh:mm", named entry bars, instrument guards, integer ticks, event
   tables as literal tables in the cluster package, free external series
   as hashed files under data/vendor/ read as literal tables), adopt the
   earlier reading and cite it. Where the text differs, read it fresh.
4. reports/E.5_RETURN.md section 1 (harness v6 is in force) and the
   holiday rows harness v5 added.
5. Part 1: reports/stage_e0_catalog_K6.md, its header (conventions C1 to
   C-last, including C10 EC-LIM) with every bracketed note, and the member
   sections K6-cp1-01, K6-cp2-01, K6-cp3-01, K6-crushgap-01,
   K6-limitcont-01, K6-wasdepre-01 and K6-wasdepost-01. Its section 7 as
   amended. rules/price_limits.py and reports/stage_e2a_price_limits.json
   for the limit tables D9.7 and K6-limitcont-01 read.
6. Part 2: reports/stage_e0_catalog_K7.md, its header and the six member
   sections. The MBT trade-date guard and its E.2b fix (E.2a L-9).
7. Part 3: reports/stage_e0_catalog_K1.md, its header (C9's VXN source)
   and the five member sections K1-cp1-01, K1-cp2-01, K1-cp3-01,
   K1-vxnband-01 and K1-vwap-01. D9's CPI window rule for equity index
   products as the frozen rules code applies it.
8. For every part: reports/stage_e1_changes.md for the cluster's edits,
   the source-window amendment for its labels, the cluster's rows in
   reports/stage_e2a_vehicles.md and stage_e2a_epsilon.md, and
   docs/STAGE_E_DESIGN.md (FROZEN) D2, D5, D6 (the session rows), D8 and
   D9.
9. strategy/stage_e/_template.py and interface.py (the member contract and
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
- The E.1, E.2a ML and harness manifests, and the K2, K4, K5 and K3
  cluster freezes, verify at start and at end.
- Research window only: 2025-04-01..2026-06-19, read by the runner. No
  script of this session opens a bar file directly.
- One run per member. Each cluster's member code is frozen by its Task 4
  before its Task 5 runs anything on data.
- No spend. The ledger is unchanged at the end.
- Holdout status at start and end: all_ok, 0 unlocks.
- REGISTRATION.md stays 0 bytes. No TopstepX reference of any kind.
- Web access (each part's Task 1b only): read-only fetches of public
  schedule, archive and data pages. No data API needing a key, no login, no
  paid source. Stay within CLAUDE.md's WebSearch budget rule.

Start and end checks, quoted verbatim in the return document: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the manifest and freeze checks, the ledger total, `uv run
pytest -q` (expected at start: E.5's end result).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Inputs: the context files.
- Output: reports/stage_e6_STATE.md and the estimate ETA table.
- Done when: the start checks pass, HEAD is the commit holding this prompt
  or a descendant with a clean tree, and the runner's preflight accepts
  v6.
- Failure path: any mismatch or refusal stops the session with a named
  refusal.

============================================================
PART 1 (E.6a): K6 GRAINS, OILSEEDS AND LIVESTOCK
============================================================

TASK 1: MEMBER SPECIFICATIONS (LEAD)
- Output: reports/stage_e6a_member_specs.md: for each member, the exact
  rule as the frozen entry states it after every amendment, with line
  references: exposures traded, every leg it reads (K6-crushgap-01 reads
  ZM and ZL as signal legs), decision and entry times, exit, hold,
  flatten, order type, sizing at q_c, every parameter as a literal, the
  release instants and limit values it reads with their availability
  times, the trade count in N, and the Topstep checks. An ordinal table of
  the trials, catalog order then ZC, ZW, ZS, ZM, ZL, HE, LE. Where the
  entry leaves a detail open, the narrowest reading, logged. Never a
  widened rule.
- Done when: every field of every member has a line reference, a
  precedent or a logged reading.
- Failure path: a member that cannot be implemented without a choice that
  could change its result materially is labelled "unimplementable as
  frozen", reported for the user, and not coded.

TASK 1b: RESEARCH-WINDOW EVENTS (WORKER)
- Owner: ReleaseChecker-OpusMed, worker-medium on opus.
- Output: reports/stage_e6a_release_check.md and .json: every WASDE
  release in the research window (date and 11:00 CT instant, including any
  moved release) against USDA's record of publication, with the catalog's
  drop rules. The limit values K6-limitcont-01 reads on each date, checked
  against rules/price_limits.py and its sources. Any other dated input a
  K6 member reads. Each item keep, drop or unverifiable, with a source URL.
- Failure path: an item that cannot be verified is kept as the frozen
  input gives it and labelled. A member whose event set holds an
  unverifiable item carries "calendar partly unverified" into the return.

TASK 2: CODE THE MEMBERS
- Owners, in parallel, each worker-xhigh on opus: MemberCoder-A-OpusXHigh
  (the three ports and K6-crushgap-01) and MemberCoder-B-OpusXHigh
  (K6-limitcont-01, K6-wasdepre-01, K6-wasdepost-01 and the event and
  limit tables). Spawn each fresh for this part.
- Output: one module per member under strategy/members/k6/, from the
  template, using only its import allowlist, with unit tests on synthetic
  bars (tests/test_e6_k6_members*.py) pinning each rule's decisions: entry
  and exit times, the event window, the flatten, a missing bar at a
  decision time, a moved or dropped release, a limit close, and D9.7's
  limit-proximity exit.
- Done when: every module passes its tests and the full suite passes.
- Failure path: a coder that finds its spec ambiguous stops and reports to
  the lead, who rules in writing.

TASK 3: FIDELITY AUDIT (FABLE XHIGH)
- Owner: MemberAuditor-K6-FableXHigh, worker-xhigh on fable. It wrote none
  of the code.
- Output: reports/stage_e6a_member_audit.md, each finding BLOCKING, SHOULD
  FIX or NOTE, with file and line.
- Done when: for every member, the auditor has checked that the module
  implements the frozen entry and nothing more (every literal, time,
  direction, exit, size, event instant and its availability, limit value,
  drop and flatten, and no input read before its availability time), that
  each lead reading is the narrowest one, and that every literal table
  equals its source. Its tests must fail on a mutant for every rule it
  pins (the E.4 K5 and K3 lessons).
- Failure path: if Fable is unavailable, stop before Task 4.

TASK 4: RULINGS AND THE CLUSTER FREEZE (LEAD)
- Output: reports/stage_e6a_member_rulings.md, the fixes, the cluster
  freeze file, and one commit holding exactly the member modules, their
  tests, the specs, the release check, the audit, the rulings and the
  cluster freeze file. Message "K6 member freeze" with the cluster freeze
  sha256 and this repository's attribution lines.
- Done when: every BLOCKING and SHOULD FIX finding has a ruling and its
  fix, the full suite passes, and the commit exists.
- Failure path: a BLOCKING finding that cannot be fixed within the frozen
  entry makes that member "unimplementable as frozen". It is not run, and
  the others proceed.

TASK 5: THE SCREENING RUN (LEAD RUNS THE FROZEN COMMAND)
- `PYTHONPYCACHEPREFIX=<fresh dir> nice -n 10 uv run python -m
  screening.stage_e_runner --harness-sha256 <v6> --cluster K6 --all
  --window research --research-root data/processed --step2-root
  data/processed_step2 --out-dir reports/stage_e6a_k6_screen`
- Output: the runner's records and trip lists, coverage and trade-rate
  labels, the D5 screen figures and the tiers. Power is `not_run`.
- Done when: every coded trial has a result or a named refusal, and the
  runner has written the tiers.
- Failure path: a crash stops that member. The fix goes through Tasks 2 to
  4 again, and the member runs from scratch. Report the crash and the fix.

TASK 6: RECOMPUTATION (FABLE RESUMED)
- Owner: MemberAuditor-K6-FableXHigh, resumed with a small brief.
- Output: a second section in reports/stage_e6a_member_audit.md: every
  trial's screen mean and daily t recomputed from its series in the
  auditor's own code, each tier checked against D5 and OC-H, two trials'
  series (one port, one event member) rebuilt from their trip lists and the
  cost table, each event member's trade count reconciled with its checked
  event table, and the MLL liquidation count per trial. Each item
  VERIFIED, VERIFIED WITH NOTES or DISCREPANCY.
- Failure path: a DISCREPANCY is ruled on by the lead in writing. A tier
  with an unresolved discrepancy is marked "unverified".

TASK 7: READ THE RESULT (LEAD)
- Output: in reports/E.6a_RETURN.md, per trial: trips, screen figures,
  labels, MLL liquidations and tier, the program N after the part (150
  plus the trials screened, counted as E.4 counted), and what K6's
  confirmation would need (the step 2 quote for its vehicles from
  reports/stage_e2b_step2_quotes.md, and the top-up, since acct-2 holds
  $0.33).
- Done when: the tables are written from the runner's files.

============================================================
PART 2 (E.6b): K7 BITCOIN
============================================================

Start when Part 1 has ended, whatever its outcome. Repeat Tasks 1 to 7 with
these substitutions:
- Files: the stage_e6b_ names, strategy/members/k7/,
  tests/test_e6_k7_members*.py, reports/stage_e6b_k7_screen/,
  reports/stage_e6b_STATE.md, reports/E.6b_RETURN.md.
- Workers: MemberCoder-A-OpusXHigh codes the three ports.
  MemberCoder-B-OpusXHigh codes K7-expiry-01, K7-rev2h-01, K7-montrend-01
  and the event tables. MemberAuditor-K7-FableXHigh audits and
  recomputes. ReleaseChecker-OpusMed does Task 1b. Spawn each fresh.
- Task 1b checks, for the research window: MBT's last trading days and the
  CME CF Bitcoin Reference Rate final-settlement instant in CT on each
  (UK and US clock changes), the Sunday-evening session opens
  K7-montrend-01 reads, and that no MBT bar booked to a trade date on or
  after 2026-06-22 reaches the members (the E.2a L-9 guard).
- Commit message "K7 member freeze". Program N: Part 1's figure plus the
  K7 trials screened.

============================================================
PART 3 (E.6c): K1 EQUITY INDEX
============================================================

Start when Part 2 has ended. Repeat Tasks 1 to 7 with these substitutions:
- Files: the stage_e6c_ names, strategy/members/k1/,
  tests/test_e6_k1_members*.py, reports/stage_e6c_k1_screen/,
  reports/stage_e6c_STATE.md, reports/E.6c_RETURN.md.
- Workers: MemberCoder-A-OpusXHigh codes the three ports.
  MemberCoder-B-OpusXHigh codes K1-vxnband-01 and K1-vwap-01.
  MemberAuditor-K1-FableXHigh audits and recomputes. ReleaseChecker-OpusMed
  does Task 1b. Spawn each fresh.
- Task 1b: fetch Cboe's free VXN daily history (the catalog's C9 source,
  cdn.cboe.com), covering 2019-04-30..2026-06-19, save the raw file with
  its source URL and sha256 under data/vendor/index_history/, check it for
  gaps against the equity trade-date calendar, and record Cboe's
  publication time for the daily close. K1-vxnband-01 reads the previous
  close as a literal table in the cluster package (E.3 L-01), each value
  used only from its availability time (the catalog's KF1 row: from 08:35
  CT on d). If the history cannot be obtained free, K1-vxnband-01 is not
  traded and adds no trial, and the return names it for the user. Also
  check the CPI release instants in the research window that D9's CPI
  window applies to MNQ, M2K and MYM.
- K1-vxnband-01 is labelled source-overlap (E.0 R-04). Record it.
- Commit message "K1 member freeze". Program N: Part 2's figure plus the
  K1 trials screened.
- When all three parts are done, add a final section to
  reports/E.6a_RETURN.md: one table of every trial across K6, K7 and K1
  with its status and tier, the per-cluster counts (declared, screened,
  Tier A, Tier B, excluded), and the program N after the session.

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
| 3 Fidelity audit | MemberAuditor-Kx-FableXHigh | fable | xhigh | after 2 | an independent model checks code against the declaration |
| 4 Rulings, freeze, commit | lead | opus | xhigh | after 3 | reserved to the lead |
| 5 Screening run | lead runs the frozen command | opus | xhigh | after 4 | a frozen command, the lead watches it |
| 6 Recomputation | MemberAuditor-Kx-FableXHigh, resumed | fable | xhigh | after 5 | every tier-deciding number gets an independent check |
| 7 Read the result, return | lead | opus | xhigh | after 6 | reserved to the lead |
| Part 2 (K7), Tasks 1 to 7 | as Part 1, fresh workers | as Part 1 | as Part 1 | after Part 1 | same pattern |
| Part 3 (K1), Tasks 1 to 7 | as Part 1, fresh workers | as Part 1 | as Part 1 | after Part 2 | same pattern |

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

- Each cluster's member code is audited against the frozen entries before
  it runs (Task 3), and its screen figures and tiers are recomputed after
  it runs (Task 6), both by that cluster's Fable auditor, which wrote none
  of it.
- The lead rules on every finding in writing. It never re-runs a check or
  a member to get a different answer.
- If Fable runs out, the checks stay pending and no tier is final.

============================================================
WHAT NOT TO DO
============================================================

- No harness change, and no member rule changed from its frozen entry.
- No run before a cluster's freeze commit, and one run per member.
- No bar outside the research window, and no direct bar reads.
- No purchase, no paid data, no login, no power check, no confirmation
  list.
- No K8 work.
- No edit to any frozen file, manifest or earlier record.
- No push, and no commit beyond the three named.
- No write to REGISTRATION.md.

============================================================
DELIVERABLE: THREE RETURN DOCUMENTS
============================================================

Write reports/E.6a_RETURN.md for K6, reports/E.6b_RETURN.md for K7 and
reports/E.6c_RETURN.md for K1. The planning chat reads these three files
to review the session. Each has these fixed sections, in order:

1. Verdict summary, at most 200 words: trials coded, frozen and run, the
   cluster freeze sha256 and commit, the Tier A and Tier B trials with
   their screen figures in one short table, any member unimplementable,
   refused or not traded, event items dropped or unverifiable, the program
   N after the part, and what the cluster's confirmation would need.
2. Guardrail evidence: the start and end checks verbatim, the manifest and
   freeze checks, the ledger diff, `git status --short` and `git diff
   --stat` at the end.
3. Results per task: the specs and every lead reading, the event check,
   the modules and their tests, the audit findings, the screen per trial,
   the labels, the MLL liquidation counts, the tiers.
4. Delegation record: one row per spawn with agent name, worker file,
   model, effort, objective, status and deviations.
5. Verification: each Fable finding in both parts of the audit, the lead's
   ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. What the next session must do first: the push the planning chat owes,
   the frozen hashes, the funding a confirmation would need, and any
   blocker or question for the user.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated. Part 3's also gives the session total.

Also write one short dated progress.md entry per part and one line per
part in docs/STAGES.md.

The last thing before ending each part: list every open choice in section
6 of its return document.

END PROMPT
