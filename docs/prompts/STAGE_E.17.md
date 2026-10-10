STAGE E.17 "C1 COMPLETED, THEN THE BASE-RULE BATCH H1 TO H5 RUN ONCE, WITHIN A $97 BUDGET ON ACCT-2"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: C1 (the backward NG replication) is frozen and ready since E.14;
the five base-rule tests H1 to H5 were frozen in E.16 Part A on a
2010-2024 window. Both wait on 2010-2019 history from Databento. The user
has about $100 in Databento acct-2 (V30). This session follows E.16's
hand-off (reports/stage_e16_handoff.md) exactly, with the amendments
below for the smaller budget: it completes C1 first (verify, harness v11,
fresh quote, register, buy, evaluate once), then writes harness v12,
buys as many of the other 21 extension roots as the remaining budget
covers under a priority rule fixed now, registers H1 to H5 with the
per-product fallback list written before any purchase, runs each test
once, and has Fable recompute every verdict number.

Decisions in force: docs/DECISIONS.md V24 to V30. Binding documents, in
this order of authority: C1's freeze (reports/stage_e14_prereg_C1.md,
sha256 afc5c10f628771afa3d1311192316ff3b4b681d7308d2b411fc655c15f821c0b),
E.16's freeze (reports/stage_e16_freeze.json, manifest sha256
5274aa97f3359d7dcfaae15cb0590b6147d1624e6056ea396df08c6215209ad4), E.16's
rulings (reports/stage_e16_rulings.md, U1 to U3b), then the hand-off as
amended here.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: two registered evaluations, two harness
changes and two purchases in one unattended night. The silent failures:
a stale quote taken for a fresh one (E.15), spend above the budget, a
test bar read before registration, a hashed file changed by v12, a test
run twice, and a wrong verdict number. Spend, registrations and verdicts
stay with the lead. Fable reviews both harness diffs and recomputes both
sets of verdict numbers.

Usage: follows CLAUDE.md's context-hygiene rules. The user runs this
unattended. reports/stage_e17_STATE.md names, after every step, the step
finished, the hashes in force, the ledger total per account, the budget
left, each test's status and the next step. If the session pauses at a
usage limit, it resumes from STATE. Expect 6 to 9 hours.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue. The only
stops are the ones this prompt, the freezes and the hand-off name, a
decision that cannot be undone and could reasonably go either way, or a
guardrail conflict.

============================================================
AMENDMENTS TO THE HAND-OFF (V30; FIXED BEFORE ANY QUOTE)
============================================================

A1. Budget. The user reports about $100 in acct-2. Total spend in this
stage is at most $97.00 (C1 plus Part 2 together, at billed prices).
Every cap the hand-off computes is also bounded by this. Databento
refusing a purchase for balance stops further buys and is reported.

A2. Databento access. Step 5's fresh quote is the access check. If the
guard fails because acct-2 is still locked (403 auth_account_locked or
any auth error), the whole stage stops there, before any registration:
both parts need Databento. Report and end.

A3. Part 2 purchase priority, fixed now, reading no market data. After
C1's evaluation, with B = $97.00 minus everything billed in Part 1:
  1. ZT, ZF, ZB, in that order (with C1's ZN they complete H3's tenors).
  2. Then the other roots of the 21 in the order of E.12's frozen
     phase-1 ranking (reports/stage_e12_ranking.json, rank 1 first;
     each vehicle mapped to its price-path root; roots already bought or
     in C1's set skipped).
  Greedy: a root is taken if its fresh quote x 1.03 fits the budget
  left; otherwise it is skipped and the next is tried. The selected list
  and every skip are written to STATE before registration.

A4. Harness v12 holds plan "ext2010h" for all 21 roots exactly as the
hand-off and E.16's freeze require; the purchase is restricted to the A3
selection by a roots option in data/pull_hist.py (a file E.16's freeze
does not hash). If adding that option needs any hashed file changed,
Part 2 stops for a re-freeze (hand-off step 8 rule).

A5. Fallback list. At H1 to H5's registration (hand-off step 10), every
root of the 21 not in the A3 selection is on the fallback list (window
2019-05-06..2024-02-29), with the reason "not funded". The list's sha256
goes into STATE before any Part 2 purchase.

A6. H2. If C1's purchase of NQ and ZN did not complete, H2 is dropped and
four tests are registered (N + 4), per E.16's return, decision 2.

A7. The E.16 lead's other recommendations are accepted (V30): H2's NQ
entry at the 15:30 reopen before 2020-10; HE's window from 2017-07; LE
2010-2014 excluded from H1 and H4; equity H1 trades past 15:08 kept for
2010-2020 with the descriptive table without them.

============================================================
SCOPE
============================================================

This stage does exactly the hand-off's steps 1 to 15 with A1 to A7.

This stage does NOT:
- spend above $97.00 in total, buy anything outside C1's plan and the
  A3 selection, or use acct-1
- change any frozen parameter, any file either freeze hashes, or the
  order of events
- read any test bar before its test's registration
- run any test twice, rerun Gate 0, or test anything else
- read holdout-2, the embargo, MES's sealed stores, the research window,
  or anything from 2026-06-21 in any test
- fit any ML model, network or RL policy (V28)
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V24 to V30.
3. reports/stage_e16_handoff.md in full (the order of events).
4. reports/stage_e14_prereg_C1.md section 11, reports/stage_e14_c1_model.md,
   c1_replication/README.md.
5. reports/E.16_RETURN.md sections 1, 6 and 7; reports/stage_e16_rulings.md;
   base_rules/README.md.
6. reports/E.15_RETURN.md and reports/stage_e15_briefs/fresh_quote_guard.py
   (the guard).
7. reports/stage_e12_ranking.json (A3's order).

============================================================
GUARDRAILS
============================================================

- Harness: v10
  fde3a49c8e15f08b36108e9a32d062f08f342fe2414607d33a7b8981ef00e34b until
  v11 is committed, then v11, then v12 after C1's evaluation. Fresh
  PYTHONPYCACHEPREFIX outside the repository for harness commands.
- Every quote passes the guard: the fresh total is the sum of the run's
  own new ledger lines; the tool's JSON is never trusted; --retry-failed
  is never used.
- Holdout status all_ok, 0 unlocks, at start, after each purchase and at
  end.
- Start and end checks, quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the manifest checks, the cluster freezes, the v2
  freeze verify, both E.14 and E.16 freeze verifications, the ledger line
  count, sha256 and total per account, N, and `uv run pytest -q -p
  no:cacheprovider` (without PYTHONPYCACHEPREFIX).
- Before ending, confirm no worker or background shell is still running.

============================================================
STEPS
============================================================

Follow reports/stage_e16_handoff.md steps 1 to 15 in order, with A1 to A7
applied where they bear. Checkpoint STATE after each step. Fable
(worker-xhigh on fable) reviews the v11 diff (step 6), the v12 diff
(step 8), recomputes C1's verdict numbers (after step 7) and every
number entering H1 to H5's verdicts (step 15), each without reading the
lead's statistics first. Findings graded BLOCKING, SHOULD FIX or NOTE in
reports/stage_e17_review.md; rulings in reports/stage_e17_rulings.md. A
BLOCKING finding on a verdict is resolved by finding the code error,
never by a second run; if unresolved, that verdict is reported as
unverified.

Commits: v11 alone ("harness v11, acct-2 cap for C1"), C1's result
("E.17 C1 evaluated"), v12 alone ("harness v12, ext2010h plan"), and the
final commit ("Stage E.17 C1 and base-rule batch evaluated"). No push.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 1 to 7 (C1) | lead | opus | xhigh | serial | frozen steps, spend and verdict reserved to the lead |
| v11 review | HarnessReviewer-FableXHigh | fable | xhigh | after the v11 diff | independent check of a frozen-file change |
| C1 verify | VerdictVerifier-FableXHigh | fable | xhigh | after C1's evaluation | verdict numbers recomputed |
| v12 build | V12Coder-OpusXHigh | opus | xhigh | after C1 | plan, calendar and store code with tests |
| v12 review | HarnessReviewer-FableXHigh | fable | xhigh | after the v12 diff | independent check |
| 9 to 14 (batch) | lead | opus | xhigh | serial | spend, registration, runs, verdicts |
| 15 verify | VerdictVerifier-FableXHigh | fable | xhigh | after 14 | verdict numbers recomputed |

Usage pools: Fable runs only the four checks at xhigh. No Sonnet or Haiku
worker draws a conclusion.

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

Compute: heavy steps at nice 10, free memory checked before each run
(the H1 probe peaked at 1.2 GB before the review fixes), resumable.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.17_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 300 words: C1's verdict and decisive
   numbers; each of H1 to H5's verdict (PASS, FAIL or STOPPED with the
   rule), its decisive numbers, its window and the fallback roots; what
   was bought and its cost; funds left; the v11 and v12 sha256; the new N;
   and what each outcome means per the freezes.
2. Guardrail evidence: the start, post-purchase and end checks verbatim,
   and the order of events with timestamps.
3. Results per step, including the A3 selection with every skip.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation: on any pass, the
   holdout-2 registered read it leads to (and only after that,
   meta-labeling, V28); on fails, what is closed.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
