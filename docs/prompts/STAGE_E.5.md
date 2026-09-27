STAGE E.5 "K4 AND K5 CONFIRMATION: HARNESS V5 (PRE-2024 HOLIDAYS, CONFIRMATION VERDICTS), STEP 2 PURCHASE WITH HOLDOUT-2 SEALED ON ARRIVAL, START RULES, POWER CHECKS, HASHED LISTS, ONE CONFIRMATION RUN PER CLUSTER"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.4 screened K4, K5 and K3 on the research window (commit
7c2cec3). Tier A holds one trial in each: K4-ngpre-01 on NG (t 1.814),
K5-fomc-01 on MGC (t 1.846) and K3-ldnrev-01 on 6E (t 1.422). The user
approved the step 2 purchases for K4 (MCL and NG, $11.46 quoted) and K5
(MGC and MHG, $9.74 quoted), both on acct-2 ($21.52 of its cap left). K3's
confirmation is deferred. This session confirms K4 and K5. It first
extends the harness (v5): the pre-2024 Topstep holiday schedule the engine
lacks (E.4c audit N-1), the confirmation-window verdict computations
NULL_CRITERIA_E section 3 requires if any are not yet built, and the E.5
spend block in data/config.py. A Fable worker reviews the change. It then
buys the step 2 history through the frozen gate, with every holdout-2
chunk sealed on arrival, builds the step 2 bars, and per cluster builds
the start rule, runs D4's power check, applies catalog C9 to
K4-ngpre-01's confirmation-window storage dates, hashes and commits the
confirmation list, runs the confirmation window once, and has Fable
recompute every verdict figure. It reports per trial: the null test at
eps, and for Tier A the edge chain as far as the frozen rules allow.

Decisions in force (docs/DECISIONS.md V14, frozen before any confirmation
read):
- (a) OC-Q. The composite verdict for an exposure X is D.1f's procedure
  (the robust zero-edge gate plus both drift sub-checks) run with X's own
  research-window bars, X's frozen D8 cost table, X's vehicle at q_c and
  eps_X in place of MES's. It is built, reviewed and frozen only if a trial
  passes Holm, DSR, daily t > 3.0 and PBO. Until then such a trial's
  verdict reads "edge candidate, composite pending", never "edge".
- (b) Holm K = 9 (the maximum) for every Holm run until every cluster and
  the ML route have been screened.
- (c) Where a cluster's Tier A has one member, DSR's Sharpe variance is
  taken over all of that cluster's confirmation-window daily Sharpes (Tier
  A and Tier B), since a one-member variance is undefined.
- (d) The purchases above are approved by the user.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: this is the first Stage E session that spends
money, seals holdout data and reads a confirmation window. Each of those
is irreversible. The work is mostly running frozen commands in the right
order with checks between them, plus one small harness change set.
CLAUDE.md routes code to opus at xhigh and independent checks to Fable.
Ultracode stays off: the steps are serial.

Usage: follows CLAUDE.md's context-hygiene rules. Fable is used by
HarnessReviewer-FableXHigh (Task A3), and by one auditor per cluster
(ConfirmAuditor-K4-FableXHigh, ConfirmAuditor-K5-FableXHigh) for the date
table audit where one is needed and the recomputation. If Fable is
unavailable at a Fable task, stop at that point: no manifest without the
review, no list hash without the audits, no verdict without the
recomputation. Compute: the ThinkPad under the overnight profile. The
session may run across usage pauses. The auto-retry launcher resumes it
with "read the STATE file first", so reports/stage_e5_STATE.md names,
after every task, the task finished, the hashes in force, the ledger total
and the next task.

Do not stop to ask. Decide, log the choice under Open choices in the return
document, and continue. The only stops are the ones this prompt names, a
decision that cannot be undone and could reasonably go either way, or a
guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- harness v5: the pre-2024 holiday schedule, any missing confirmation
  verdict code, the E.5 spend block, tests, a replay proof, a Fable review,
  the manifest and one commit (Part A)
- buy the step 2 history for MCL, NG, MGC and MHG on acct-2, sealing every
  holdout-2 chunk on arrival, and build the step 2 bars (Part B)
- for K4, then K5: the start rule, D4's power check, C9 on
  K4-ngpre-01's confirmation-window storage dates, the hashed confirmation
  list and its commit, one confirmation run, the recomputation, the
  verdicts (Parts C and D)

This stage does NOT:
- buy anything for K2, K3, the ML route or any leg outside the four roots,
  or buy full-size bars for a short-history micro (U8: only if a power
  check fails and the user agrees, which is a later decision)
- read any holdout-2 or embargo bar, unseal anything, or touch holdout-1
- change any member rule, parameter or research result. The only member
  code that may change is K4-ngpre-01's literal storage-date table, and
  only by C9's frozen drop rule (Task C3).
- run a confirmation more than once per cluster, or change anything after
  seeing a confirmation result
- build the composite verdict unless V14 (a)'s condition is met
- register anything or write to REGISTRATION.md (it stays 0 bytes)
- touch live/, ops/, or any TopstepX credential or API
- print, copy or log the Databento key
- push. The session makes exactly the commits this prompt names.

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md and docs/ORCHESTRATION.md. On any conflict CLAUDE.md wins,
   and the conflict is logged.
2. docs/DECISIONS.md V13 and V14.
3. reports/E.4_RETURN.md sections 1, 6, 7 and the final table.
   reports/E.4b_RETURN.md sections 1, 6, 7. reports/E.4c_RETURN.md section
   5 (audit N-1) and section 7.
4. reports/E.2b_RETURN.md: section 3's step 2 path, the preflight design
   paragraph on manifest rebuilds, section 6 (OC-H to OC-T) and section 7
   (the decisions owed, items 1 to 3 and 9).
5. docs/STAGE_E_DESIGN.md (FROZEN): D4 (windows, holdouts, start rule,
   power check, short histories), D5 (Holm, edge chain), D13 (purchases).
   docs/NULL_CRITERIA_E.md sections 1 to 7.
6. docs/NULL_CRITERIA.md sections 2 and 3 and
   reports/stage_d1f_confirmation_list.md: the MES record of how a list is
   hashed and a confirmation is read. Read only, never edited.
7. reports/stage_e0_catalog_K4.md C9 (EC-NGS and its drop rules) and the
   K4-ngpre-01 section. reports/stage_e4_release_check.md.
8. The code: data/pull_step2.py, data/config.py, the step 2 store,
   screening/stage_e_start_dates.py, screening/stage_e_stats.py and
   stage_e_stats_power.py, screening/stage_e_runner.py (the confirmation
   window path), rules/sessions.py, screening/harness_freeze.py, and the
   program functions for DSR, daily t and CSCV PBO that D.1f pinned.

============================================================
GUARDRAILS
============================================================

CLAUDE.md invariants apply in full. This stage adds:

- Until Task A4's commit, every Stage E command takes `--harness-sha256
  82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009` (v4).
  After it, the v5 sha256. Every Stage E command runs with a fresh
  `PYTHONPYCACHEPREFIX` outside the repository.
- The E.1, E.2a ML and harness manifests, and the K2, K4, K5 and K3
  cluster freezes, verify at start and at end (K4's against its new hash
  if Task C3 changed its table).
- Spend: acct-2 only, only through `python -m data.pull_step2 --buy` and
  its gate, only for MCL, NG, MGC and MHG, only after a fresh
  `--quote-only` run in this session. The session cap is the fresh quote
  total plus 10%, but never above acct-2's remaining headroom. K4 is
  bought first. K5 is bought only if the headroom left after K4 covers
  K5's fresh quote. Otherwise K5's purchase stops, and the return states
  the top-up needed. ACCOUNT_2_CAP_USD is never raised.
- Holdout-2: every chunk from range=2024-03-01_2024-04-01 through
  range=2025-03-01_2025-04-01 is sealed in the download call after its
  byte check, oldest first, for each root, exactly as the frozen step 2
  path does. `--status` shows every seal before any step 2 bar is built.
  Holdout status at start and end: all_ok, 0 unlocks.
- The confirmation window is S_X..2024-02-29. No script opens a bar file
  directly. The runner reads the bars.
- One confirmation run per cluster, after its list is hashed and
  committed.
- REGISTRATION.md stays 0 bytes. No TopstepX reference of any kind.
- Web access (Task C3 only): read-only fetches of EIA pages and Wayback
  captures. No login, no paid source.

Start and end checks, quoted verbatim in the return document: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the manifest checks, the ledger total for acct-2, `uv
run pytest -q` (expected at start: E.4's end result).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Inputs: the context files.
- Output: reports/stage_e5_STATE.md and the estimate ETA table.
- Done when: the start checks pass, HEAD is the commit holding this prompt
  or a descendant with a clean tree, the runner's preflight accepts v4,
  and `python -m data.pull_step2 --status` shows no step 2 chunk for the
  four roots yet.
- Failure path: any mismatch or refusal stops the session with a named
  refusal.

============================================================
PART A: HARNESS V5
============================================================

TASK A1: INVENTORY (LEAD)
- Owner: lead.
- Output: a section of reports/stage_e5_harness_plan.md listing, for each
  item of NULL_CRITERIA_E section 3 (the unit, theta_hat, UCB95 and SE_boot
  from the stationary block bootstrap with its seeds, null power, Holm at
  K = 9, DSR at cumulative N with V14 (c), daily t > 3.0, CSCV PBO on 8
  contiguous blocks, the source-overlap gate, the inconclusive-by-design
  exception, the V14 (a) "composite pending" state), whether code already
  computes it and where, pinned to the program's functions. And the exact
  shape of the holiday gap in rules/sessions.py.
- Done when: every item is "exists at file:line" or "missing".

TASK A2: THE CHANGE SET (WORKER)
- Owner: HarnessBuilder-OpusXHigh, worker-xhigh on opus.
- Output:
  (a) rules/sessions.py gains the Topstep holiday schedule for trade dates
  2019-05-01..2023-12-31, derived by the same rule that produced the
  existing 2024-onward entries, applied to the frozen E.2a exchange
  calendars (data/calendars). Validation: the same rule applied to
  2024-2026 reproduces the existing entries exactly. Any date the rule
  cannot settle is listed, not guessed.
  (b) The missing verdict items from Task A1, as one module
  (screening/stage_e_verdict.py or the name the harness pattern suggests),
  pure functions on the runner's confirmation records and the hashed list,
  pinned to the program's existing functions, with a known-answer test for
  each item.
  (c) data/config.py: an E.5 block (session id "stage-E.5-2026-09-27",
  request and session caps at $0.00 until Task B1 sets them from the fresh
  quote).
  (d) Tests. The full suite passes.
- Failure path: anything that needs a change outside these files stops
  the worker, which reports to the lead. The lead stops the session before
  any purchase.

TASK A3: PROOF AND REVIEW
- Owner: lead runs the replay, HarnessReviewer-FableXHigh (worker-xhigh on
  fable, it wrote none of the change) reviews.
- The replay: K4's and K5's research runs through `python -m` into scratch
  directories (reports/stage_e5_replay_k4/, _k5/), compared field by field
  with reports/stage_e4_k4_screen/ and reports/stage_e4b_k5_screen/. Only
  harness hashes and timestamps may differ. The holiday change touches only
  2019-2023, so any other difference is BLOCKING.
- The review: reports/stage_e5_harness_review.md, BLOCKING, SHOULD FIX or
  NOTE with file and line. It checks the holiday rule and its validation,
  every verdict function against NULL_CRITERIA_E and the pinned program
  functions, the seeds, V14 (b) and (c) as coded, and that the E.5 caps
  start at $0.00.
- Done when: the replay matches and every finding has a verdict.

TASK A4: RULINGS, MANIFEST V5, COMMIT (LEAD)
- Output: reports/stage_e5_harness_rulings.md, the fixes, `python -m
  screening.harness_freeze build`, `verify --expected <v5>`, the manifest
  diff showing only the changed files, and one commit holding exactly the
  change set, its tests, the plan, the review, the rulings, the replay
  report and the manifest. Message: "harness v5", the new sha256, this
  repository's attribution lines.
- Failure path: an unfixable BLOCKING finding stops the session before any
  purchase.

============================================================
PART B: THE PURCHASE
============================================================

TASK B1: FRESH QUOTE AND CAPS (LEAD)
- `python -m data.pull_step2 --quote-only --set <the set that prices
  MCL, NG, MGC, MHG>` under the v5 sha256 (a quote is free and ledgered at
  $0.00). Then set the E.5 caps in data/config.py per the spend guardrail
  and show the arithmetic. This config edit changes a frozen file: write
  the manifest after v5 (v6), whose only difference is data/config.py's
  entry, verify it, show the diff, commit it alone ("harness v6, E.5 spend
  caps"), and use v6 from here on.
- Failure path: a fresh quote above the headroom for K4 alone stops the
  session with the figure for the user.

TASK B2: BUY, SEAL, BUILD (LEAD RUNS THE FROZEN COMMANDS)
- `python -m data.pull_step2 --buy --cluster K4 ...` then, if the
  guardrail allows, `--cluster K5`, each with `--harness-sha256 <v6>`.
  Then `--status`: every holdout-2 chunk of the four roots sealed. Then
  build the step 2 bars with the frozen store path.
- Output: reports/stage_e5_purchase.md: the quote, the caps, the ledger
  lines, spend against quote, the seal status per root and chunk, the bar
  build counts, and any failed chunk with its cause.
- Failure path: a failed chunk is retried once with `--retry-failed`. A
  chunk still failing leaves that root's confirmation for the user. An
  unsealed holdout-2 chunk is a stop.

============================================================
PART C: K4 CONFIRMATION
============================================================

TASK C1: START RULE (LEAD)
- `python -m screening.stage_e_start_dates --harness-sha256 <v6> --set K4`.
  Output: S_X for MCL and NG, the monthly medians, the 0.15 and 0.40
  descriptive dates, and any refusal by name.

TASK C2: POWER CHECK (LEAD)
- D4's power check for each of the 12 K4 trials at eps_X, from its
  recorded research-window series in reports/stage_e4_k4_screen/ and the
  supply its confirmation window gives, seeded from the frozen ordinals.
  Use the frozen stage_e_stats.power_check directly on the recorded
  series, or a research re-run under v6 into a scratch directory that
  first matches the E.4 records, whichever the harness supports. Log which.
- Output: per trial n_b, the supply, and the label ("sufficient" or
  "inconclusive by design"). The five coverage-excluded K5 and K3 trials
  are not in scope. K4 has none.

TASK C3: NGS CONFIRMATION-WINDOW DATES (WORKER, THEN FABLE)
- Owner: ReleaseChecker-OpusMed (worker-medium on opus) checks every
  storage release in K4-ngpre-01's confirmation window (S_NG..2024-02-29)
  against EIA's record of actual publication and the schedule captures,
  with C9's two drop rules, as E.4's Task 1b did for the research window.
  Output: reports/stage_e5_ngs_check.md and .json, each release keep,
  drop or unverifiable with a source URL.
- If any release drops, MemberCoder-OpusXHigh removes exactly those rows
  from K4-ngpre-01's literal table, and nothing else. The research-window
  rows must stay identical. ConfirmAuditor-K4-FableXHigh checks the table
  against the check and the source, and confirms the research series is
  unchanged by a research re-run into a scratch directory. The lead writes
  a new K4 cluster freeze and commits it with the check and the audit
  ("K4 C9 table amendment").
- Unverifiable releases are kept and counted. K4-ngpre-01 carries the
  count in the list.
- Done when: every confirmation-window release has a verdict, and the K4
  freeze in force is named.

TASK C4: THE HASHED LIST (LEAD)
- Output: reports/stage_e5_k4_confirmation_list.md and .json, in the
  shape of reports/stage_d1f_confirmation_list.md: per trial its ordinal,
  member, vehicle, q_c, eps_X, tier, labels (source-overlap, calendar
  partly unverified, inconclusive by design), S_X, the bootstrap seed, the
  cluster freeze hash, the harness hash, K = 9, and the program N the DSR
  uses (150). Its sha256, and one commit holding exactly the list files,
  the start-rule output and the power-check output, message "K4
  confirmation list" with the sha256.
- Done when: the commit exists. Nothing reads the confirmation window
  before it.

TASK C5: THE CONFIRMATION RUN (LEAD RUNS THE FROZEN COMMAND)
- `PYTHONPYCACHEPREFIX=<fresh> nice -n 10 uv run python -m
  screening.stage_e_runner --harness-sha256 <v6> --cluster K4 --all
  --window confirmation --research-root data/processed --step2-root
  data/processed_step2 --out-dir reports/stage_e5_k4_confirmation`, then
  the verdict module on its records and the hashed list.
- Output: the runner's records and trip lists, and
  reports/stage_e5_k4_verdicts.md and .json: per trial theta_hat, UCB95,
  SE_boot, null power and the null verdict at eps, and for the Tier A
  trial the Holm result at K = 9, DSR, daily t, PBO and the V14 (a) state.
  The cluster's null statement per NULL_CRITERIA_E section 1, with the
  per-exposure resolution table.
- Failure path: a crash stops the cluster. A fix goes through a harness
  review and the next manifest, and the run is repeated from scratch
  because nothing was read. A run that completed is never repeated.

TASK C6: RECOMPUTATION (FABLE)
- Owner: ConfirmAuditor-K4-FableXHigh (resumed, or fresh if Task C3
  needed none).
- Output: reports/stage_e5_k4_audit.md: every figure in the verdict file
  recomputed in the auditor's own code from the records, the list and the
  trip lists: the bootstrap bounds with the list's seeds, null power, the
  Holm result, DSR with V14 (c), daily t, PBO, and one trial's daily series
  rebuilt from its trip list and the cost table. It also checks that the
  run's inputs equal the hashed list. Each item VERIFIED, VERIFIED WITH
  NOTES or DISCREPANCY.
- Failure path: a DISCREPANCY is ruled on by the lead in writing. An
  unresolved one marks that verdict "unverified".

============================================================
PART D: K5 CONFIRMATION
============================================================

Only if Task B2 bought K5. Repeat Tasks C1, C2, C4, C5 and C6 for K5 with
these substitutions:
- Roots MGC and MHG.
- Trials: the 8 tiered K5 trials (1 Tier A, 7 Tier B) are run. K5-pmfix-01
  MGC (screened, then excluded before confirmation) and the two
  coverage-excluded MHG trials are listed with their labels and not run
  (OC-H).
- No Task C3. K5-fomc-01's dates are the frozen FOMC rows E.3 verified.
- Files named stage_e5_k5_..., the list commit "K5 confirmation list", and
  the auditor ConfirmAuditor-K5-FableXHigh.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, ETA | lead | opus | xhigh | first | gates the session |
| A1 Inventory | lead | opus | xhigh | after 0 | a reading of frozen text and code, reserved to the lead |
| A2 Change set | HarnessBuilder-OpusXHigh | opus | xhigh | after A1 | frozen code every confirmation depends on |
| A3 Replay | lead | opus | xhigh | after A2 | proves the research records did not move |
| A3 Review | HarnessReviewer-FableXHigh | fable | xhigh | after the replay | an independent model checks a frozen-code change |
| A4 Rulings, v5, commit | lead | opus | xhigh | after A3 | reserved to the lead |
| B1 Quote, caps, v6 | lead | opus | xhigh | after A4 | spend, reserved to the lead |
| B2 Buy, seal, build | lead runs frozen commands | opus | xhigh | after B1 | irreversible, the lead watches it |
| C1, C2 Start rule, power | lead | opus | xhigh | after B2 | frozen commands |
| C3 NGS check | ReleaseChecker-OpusMed | opus | medium | after B2, parallel with C1 and C2 | web lookups against fixed drop rules |
| C3 Table fix, if needed | MemberCoder-OpusXHigh | opus | xhigh | after the check | a literal-table edit |
| C3 Table audit, if needed | ConfirmAuditor-K4-FableXHigh | fable | xhigh | after the fix | member code change before a hash |
| C4 List, commit | lead | opus | xhigh | after C1 to C3 | reserved to the lead |
| C5 Run, verdicts | lead runs frozen commands | opus | xhigh | after C4 | a frozen command |
| C6 Recomputation | ConfirmAuditor-K4-FableXHigh | fable | xhigh | after C5 | every verdict number gets an independent check |
| Part D (K5) | as C1, C2, C4 to C6 | as Part C | as Part C | after Part C | same pattern, fresh auditor |
| Return | lead | opus | xhigh | last | reserved to the lead |

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

- The harness change is proven inert on the research window by the replay
  and reviewed by Fable before any money is spent.
- The seals are shown by `--status` before any step 2 bar is built.
- Each list is hashed and committed before its confirmation run.
- Every verdict figure is recomputed by a Fable auditor that wrote none of
  it. The lead rules on every finding in writing and never re-runs a check
  or a confirmation to get a different answer.

============================================================
WHAT NOT TO DO
============================================================

- No purchase outside MCL, NG, MGC and MHG, and no raised account cap.
- No holdout-2 or embargo bar read, no unseal.
- No member rule change. No change after seeing a confirmation result.
- No second confirmation run of a cluster.
- No composite build unless V14 (a)'s condition is met. No "edge" word
  for a trial whose composite is pending.
- No push. No write to REGISTRATION.md. No edit to docs/NULL_CRITERIA.md,
  docs/NULL_CRITERIA_E.md or any E.3/E.4 record.
- No key printed, copied or logged.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.5_RETURN.md. The planning chat reads this one file to
review the session. Fixed sections, in order:

1. Verdict summary, at most 250 words: harness v5 and v6 hashes and
   commits, spend against quote, seals, S_X per root, power labels, the
   NGS check result, the list hashes, and per cluster the null statement
   and each Tier A trial's edge chain in one short table.
2. Guardrail evidence: the start and end checks verbatim, the manifest
   checks, the ledger diff, the seal status, `git status --short` and `git
   diff --stat` at the end.
3. Results per task, with every trial's confirmation figures in one table
   (theta_hat, UCB95, SE_boot, null power, null verdict, labels).
4. Delegation record: one row per spawn with agent name, worker file,
   model, effort, objective, status and deviations.
5. Verification: each Fable finding, the lead's ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. What the next session must do first: the push the planning chat owes,
   the hashes in force, the acct-2 balance left, any blocker, and the
   questions for the user.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
