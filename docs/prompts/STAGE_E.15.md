STAGE E.15 "C1, THE BACKWARD NG REPLICATION: VERIFY THE FREEZE, RAISE THE ACCT-2 CAP, REGISTER, BUY, EVALUATE ONCE"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.14 froze C1 (the backward replication of E.12's NG
near-miss on 2010-2019 data no part of the program has read), reproduced
E.12's NG rows exactly, fixed q and fitted M1, quoted C1's data at
$57.742330 and stopped, awaiting funds. The user has now topped up acct-2
(V27). This session completes C1 exactly as reports/stage_e14_c1_model.md
section "later session" and the freeze reports/stage_e14_prereg_C1.md
section 11 prescribe: verify every frozen input, raise ACCOUNT_2_CAP_USD
in harness v11, quote fresh, register (N 471 -> 473), buy, build the six
stores, evaluate once, and have Fable recompute the verdict. Nothing in
the freeze changes.

Decisions in force: docs/DECISIONS.md V24 to V27. The freeze
reports/stage_e14_prereg_C1.md (sha256
afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b, commit
1680982) rules over everything else, including this prompt.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: one registered evaluation with a purchase.
The silent failures to guard against: a frozen input that changed, a
test-window byte read before registration, spend above the approval, a
second evaluation, and a wrong verdict number. Fable recomputes the
verdict independently.

Usage: follows CLAUDE.md's context-hygiene rules. The user may be away.
reports/stage_e15_STATE.md names, after every step, the step finished,
the hashes in force, the ledger total per account and the next step.
Expect 2 to 3 hours.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue. The only
stops are the ones this prompt and the freeze name, a decision that
cannot be undone and could reasonably go either way, or a guardrail
conflict.

============================================================
SCOPE
============================================================

This stage does exactly the six steps of reports/stage_e14_c1_model.md's
"later session" list, plus harness v11 and the Fable check.

This stage does NOT:
- change the freeze, its inputs, q, M1, the calendars or any rule
- read any 2010-2019 byte before C1's registration is written
- spend beyond the fresh quote x 1.03, or beyond $60.00 in any case, or
  buy anything but the ext2010 plan's six roots (NG, NQ, ZN, 6E, GC, ZC,
  2010-06..2019-04 with the June-2010 chunks)
- evaluate more than once, rerun Gate 0, or test anything else
- touch C2 (stopped in E.14; it stays stopped), MES's sealed holdouts,
  holdout-1, holdout-2 or the research window
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V24 to V27.
3. reports/stage_e14_prereg_C1.md in full (the freeze).
4. reports/stage_e14_c1_model.md in full, above all its "later session"
   list, and c1_replication/README.md.
5. reports/E.14_RETURN.md sections 1, 3 and 6.
6. The code the steps name: data/config.py, data/pull_step2.py,
   data/hist_store.py, screening/trial_registry.py,
   c1_replication/evaluate.py, screening/harness_freeze.py.

============================================================
GUARDRAILS
============================================================

- Harness: every command takes `--harness-sha256
  fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b` (v10)
  until Step 2 commits v11, then the v11 sha256. Fresh
  PYTHONPYCACHEPREFIX outside the repository.
- Harness v11 differs from v10 only in what the freeze allows (the model
  file's step 1, last bullet): data/config.py's ACCOUNT_2_CAP_USD and
  E14_EXT2010_SESSION_CAP_USD, their comments, and the test assertions
  that pin those two values. Any other diff is a stop.
- Spend (V27). Pre-approved, no further approval needed, if every
  condition holds: only through the frozen purchase path and its gate,
  after a fresh quote-only run in this session ledgered at $0.00; only
  the ext2010 plan on acct-2; ACCOUNT_2_CAP_USD = 291.08;
  E14_EXT2010_SESSION_CAP_USD = the fresh quote x 1.03 in whole cents,
  never above acct-2's headroom under 291.08 and never above $60.00. A
  fresh quote whose x 1.03 exceeds that headroom stops the session before
  registration, with the figures. Databento refusing a purchase for
  balance stops the buy and is reported (the user tops up again). A
  billed amount above its quote by more than 3% stops further buys.
- Order of events, enforced and shown with timestamps in the return:
  verification, v11 commit, fresh quote, registration (N written), buy,
  store builds (counts only), one evaluation, Fable check.
- Holdout status all_ok, 0 unlocks, at start, after the purchase and at
  end.
- Start and end checks, quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the manifest checks, the cluster freezes, the v2
  freeze verify, the ledger line count, sha256 and total per account,
  and `uv run pytest -q -p no:cacheprovider` (without
  PYTHONPYCACHEPREFIX, as E.12 ruled).

============================================================
STEPS
============================================================

STEP 0: STARTUP (lead). Start checks; reports/stage_e15_STATE.md; the
ETA table. HEAD is the commit holding this prompt or a descendant, with a
clean tree apart from the expected DO_NOT_COMMIT page folders and
.claude/worktrees/.

STEP 1: VERIFY THE FREEZE (lead, by script). Every check in the model
file's step 1: the 43 freeze inputs, the freeze file's sha256 and its git
history, the E.12 state copy against its manifest, the model JSON and
both M1 payloads. Any mismatch is a stop: C1 is not registered, and the
return explains.

STEP 2: HARNESS V11 (lead). Set ACCOUNT_2_CAP_USD = 291.08 (V27) and,
after Step 3's quote, E14_EXT2010_SESSION_CAP_USD; update only the pinned
test assertions; write and verify the v11 manifest; show the diff
against v10; one commit "harness v11, acct-2 cap for C1". If the session
cap needs the fresh quote first, run Step 3 under v10 (a quote needs no
spend), then commit v11 before Step 4.

STEP 3: FRESH QUOTE (lead). The model file's step 2 command, ledgered at
$0.00. Show the arithmetic against the headroom.

STEP 4: REGISTER (lead). The model file's step 3 command. N 471 -> 473.
Record the registry lines and N in STATE before any purchase.

STEP 5: BUY AND BUILD (lead). The model file's steps 4 and 5. Counts
only. Holdout status after the purchase.

STEP 6: EVALUATE ONCE (lead). The model file's step 6, behind the
run-once marker. Verdict per the freeze's section 5 (PASS iff at least
one of T1 = NG h60 and T2 = NG hF passes: mean gross >= 1.5c, one-sided
p <= 0.025, at least 30 trades), then the descriptive outputs. The
ruling C10 guard applies: a feature live in E.12 with 0 applicable rows
stops C1 and closes this registered attempt.

STEP 7: VERIFY (Fable). VerdictVerifier-FableXHigh (worker-xhigh on
fable) recomputes the verdict from the stores and the frozen rules
without reading the lead's statistics first: per test the trade count,
mean gross, c, t and p, the C10 counts, and the order of events in git
and the ledgers. Findings graded BLOCKING, SHOULD FIX or NOTE in
reports/stage_e15_review.md; the lead's rulings in
reports/stage_e15_rulings.md. A BLOCKING finding on a verdict number is
resolved by finding the code error, never by a second evaluation; if
unresolved, the verdict is reported as unverified.

STEP 8: RETURN AND COMMIT (lead). One final commit "Stage E.15 C1
evaluated" holding the reports, the result JSON, the registry lines, the
STATE file and the briefs. Raw data stays in the stores. No push.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 to 6 | lead | opus | xhigh | serial | frozen steps, spend and verdict reserved to the lead |
| 7 Verify | VerdictVerifier-FableXHigh | fable | xhigh | after 6 | verdict numbers recomputed independently |
| 8 Return, commit | lead | opus | xhigh | last | reserved to the lead |

Usage pools: Fable runs only the one check. No other worker is needed;
if the lead spawns one for a mechanical step, it states model and effort
first, per CLAUDE.md.

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

Compute: heavy steps at nice 10 under the overnight profile, resumable.
Before ending, confirm no worker or background shell is still running.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.15_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 250 words: C1's verdict (PASS, FAIL or
   STOPPED with the rule), T1's and T2's decisive numbers, the cost and
   funds left, the v11 sha256, the new N, and what the outcome means per
   the freeze's section 8.
2. Guardrail evidence: the start, post-purchase and end checks verbatim,
   and the order of events with timestamps.
3. Results per step.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
