STAGE E.18 "C1B: THE BACKWARD NG REPLICATION RE-REGISTERED WITH THE C10 CONTRADICTION FIXED, EVALUATED ONCE ON DATA ALREADY OWNED"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: C1's single evaluation in Stage E.17 stopped at its own guard
C10: the feature g17_mbt reads bitcoin futures (MBT), which did not trade
in 2010-2019, so it applied on 0 NG rows, and the freeze had no exemption
for a leg that is not applicable by design. Fable verified that the stop
was the freeze's rule applied as written, and that the contradiction
(C10 against the freeze's section 2, which already says unlisted legs
get "not applicable") was decidable before any data. No statistic was
computed. The user chose (V31) to re-register the same test as C1b, with
the one contradiction fixed. Everything else is C1 unchanged: model M1,
the threshold q, the calendars, the data (bought in E.17), the trade
rule, the costs, the pass bar. This session writes C1b, has Fable check
it, runs a dry check on synthetic sentinel frames, freezes, registers
(N 478 -> 480), evaluates once, and has Fable recompute the verdict. No
purchase, no Databento call.

Decisions in force: docs/DECISIONS.md V24 to V31. Binding: C1's freeze
reports/stage_e14_prereg_C1.md (sha256
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b) as the
base text; reports/E.17_RETURN.md sections 3 (C1) and 7 item 1; Fable's
C1 finding F-1 in reports/stage_e17_review.md.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: one registered evaluation of a frozen design
with one textual fix. The silent failures to guard against: a change in
C1b beyond the stated fix, a second contradiction of the same kind
missed again, and a wrong verdict number. Fable reviews the C1b diff
before the freeze and recomputes the verdict.

Usage: follows CLAUDE.md's context-hygiene rules. The user may be away.
reports/stage_e18_STATE.md is updated after every step. Expect 2 to 3
hours.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue.

============================================================
THE ONE FIX (FIXED HERE)
============================================================

C1b's text is C1's freeze with exactly these changes and no others:
1. The test ids become C1b-T1 (NG h60) and C1b-T2 (NG hF); the
   registration is new (N 478 -> 480); C1's closed attempt stays closed
   and is cited.
2. Guard C10 gains one clause: a feature whose leg had no listed
   contract on any date of the test window (MBT, listed only from
   December 2017 for BTC and 2021 for MBT; and CL, already 0 in E.12 on
   NG rows) is exempt, because section 2 already makes it "not
   applicable" on every such date, as in training. The exempt list is
   decided from listing dates alone, written in the freeze, and checked
   by the dry run below; it is not decided from any count of the test
   window.
3. Every other feature keeps C10 exactly as C1 had it: 0 applicable rows
   stops the attempt and closes it.
The code change is the smallest one that implements clause 2 in
c1_replication/guards.py (or wherever c10_check lives), with a test.

Before the freeze, a dry check (Fable F-1): run the amended c10_check on
the frozen E.12 reference counts against synthetic sentinel frames that
mimic the 2010-2019 listing state of every leg (MBT and CL absent, all
other legs present), and show it passes; then remove one non-exempt leg
from the sentinel and show it stops. No test-window bar is read by the
dry check.

The applicable-row counts that E.17's stopped run printed (counts only,
no values) are known; the return must state that C1b's design change
depends only on listing dates and section 2, not on those counts.

============================================================
SCOPE
============================================================

This stage does:
- write reports/stage_e18_prereg_C1b.md and the code change (Step 1)
- Fable review of the diff against C1's freeze (Step 2)
- the dry check (Step 3)
- freeze manifest and commit (Step 4)
- register C1b-T1 and C1b-T2, evaluate once (Step 5)
- Fable recomputation of the verdict (Step 6)

This stage does NOT:
- buy anything or call Databento
- change M1, q, the calendars, the windows, the trade rule, the costs,
  the pass bar, or anything else of C1 beyond THE ONE FIX
- run the evaluation more than once, or rerun H1 to H5 or Gate 0
- read holdout-2, the research window, MES's sealed stores, or anything
  from 2026-06-21
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V24 to V31.
3. reports/stage_e14_prereg_C1.md in full; reports/stage_e14_c1_model.md;
   c1_replication/README.md and guards.py.
4. reports/E.17_RETURN.md sections 1, 3 (C1) and 7; reports/stage_e17_review.md
   (C1 findings) and reports/stage_e17_rulings.md.

============================================================
GUARDRAILS
============================================================

- Harness: v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32,
  verified at start, unchanged. Fresh PYTHONPYCACHEPREFIX outside the
  repository for harness commands.
- The six ext2010 stores bought in E.17 verify against their recorded
  sha256 before the evaluation.
- Order of events, shown with timestamps: Fable review, dry check,
  freeze commit, registration, evaluation, Fable recomputation.
- Holdout status all_ok, 0 unlocks, at start and end. The spend ledger
  is unchanged.
- Start and end checks, quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the manifest checks, the cluster freezes, the v2,
  E.14 and E.16 freeze verifications, the ledger line count and sha256,
  N, and `uv run pytest -q -p no:cacheprovider`.
- Before ending, confirm no worker or background shell is still running.

============================================================
STEPS
============================================================

STEP 0: STARTUP (lead). Start checks; STATE; ETA table.

STEP 1: C1B TEXT AND CODE (lead). The freeze text with THE ONE FIX, a
line-by-line diff against C1's freeze in reports/stage_e18_c1b_diff.md,
and the guard change with its test.

STEP 2: REVIEW (DiffReviewer-FableXHigh, worker-xhigh on fable). Checks:
the diff holds only THE ONE FIX; the exempt list follows from listing
dates and section 2 alone; no other leg can hit the same contradiction
(every leg's listing state in 2010-2019 checked); the code change does
exactly clause 2. BLOCKING and SHOULD FIX findings are fixed before the
freeze.

STEP 3: DRY CHECK (lead). As above. Output reports/stage_e18_dry_check.md.

STEP 4: FREEZE (lead). A manifest reports/stage_e18_freeze.json hashing
the C1b text, the guard code and its test, and citing every C1 input
unchanged (the E.12 state copy, the model JSON, M1 payloads, q, the
calendars, the six store hashes). One commit "C1b freeze".

STEP 5: REGISTER AND EVALUATE ONCE (lead). Register C1b-T1 and C1b-T2
(N 478 -> 480), then run the evaluation once behind a new run-once
marker (reports/stage_e18_c1b_RUN_ONCE.json). Verdict per C1's section 5
(PASS iff at least one of T1 and T2 passes: mean gross >= 1.5c, one-sided
p <= 0.025, at least 30 trades), then the descriptive outputs.

STEP 6: VERIFY (VerdictVerifier-FableXHigh, worker-xhigh on fable).
Recompute the verdict numbers independently, without reading the lead's
statistics first, and check the order of events. Findings in
reports/stage_e18_review.md, rulings in reports/stage_e18_rulings.md. A
BLOCKING finding is resolved by finding the code error, never by a
second evaluation.

STEP 7: RETURN AND COMMIT (lead). reports/E.18_RETURN.md, one dated
progress.md entry, one docs/STAGES.md line, one final commit "Stage E.18
C1b evaluated". No push.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0, 1, 3, 4, 5, 7 | lead | opus | xhigh | serial | frozen design, registration and verdict reserved to the lead |
| 2 Review | DiffReviewer-FableXHigh | fable | xhigh | after 1 | independent check of the only change |
| 6 Verify | VerdictVerifier-FableXHigh | fable | xhigh | after 5 | verdict numbers recomputed |

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
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.18_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 250 words: C1b's verdict (PASS, FAIL or
   STOPPED with the rule), T1's and T2's decisive numbers, the new N, and
   what the outcome means per C1's section 8.
2. Guardrail evidence: the start and end checks verbatim, and the order
   of events with timestamps.
3. Results per step, including the diff, the review, the dry check.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
