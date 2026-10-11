STAGE E.20 "PATTERN SEARCH: THE ML ROUTE'S FROZEN NET PIPELINE ON 17 ROOTS, SCREENED ON 2019-2024, ONE FINAL MODEL TESTED ONCE BACKWARD ON 2010-2019"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Nothing has passed in 480 trials, and E.19 showed that the
Topstep funnel loses money without an edge (a net Sharpe of about 0.5 is
needed at 50K). The user chooses an ML pattern search (V33 item 5): run
the ML route's frozen net pipeline (docs/STAGE_E_ML_V2_DESIGN.md V2.3 to
V2.9: the signal library, ridge and shallow LightGBM, the cost gate, 50K
sizing, nested CPCV) on the 17 roots whose 2010-2019 history is owned.
v2 never ran this pipeline: Gate 0 stopped it in E.12. The search reads
only the E.12 training stores (2019-05-06..2024-02-29). If its nested
out-of-sample record clears the screen fixed below, its one final model
is frozen, as C1's M1 was, registered, and evaluated once, backward, on
the owned 2010-2019 stores, which no part of this search reads. Fable
reviews the plan before any fit, the freeze before registration, and
recomputes the verdict. No purchase, no Databento call.

Decisions in force: docs/DECISIONS.md V20 to V33. Binding, in this
order: this prompt's FIXED DESIGN, then docs/STAGE_E_ML_V2_DESIGN.md (its
v2 freeze, reports/stage_e12_ml_v2_freeze.json), then the E.16 rulings on
the 2010-2019 windows (reports/stage_e16_rulings.md,
reports/stage_e16_windows.json).

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: a model search followed by one registered
evaluation on data the program has already used for other tests. The
silent failures to guard against: a 2010-2019 byte read before
registration, a feature whose legs or calendars do not exist in
2010-2019 (C1's C10 stop), leakage across CPCV folds, a frozen file
changed without a reviewed amendment, a configuration count that
understates the search, and a wrong verdict number. Fable reviews the
plan, the freeze and the verdict.

Usage: follows CLAUDE.md's context-hygiene rules. The user runs this
unattended. reports/stage_e20_STATE.md names, after every step, the step
finished, the hashes in force, N, each guard's state and the next step.
Expect 7 to 10 hours.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue. The only
stops are the ones this prompt names, a decision that cannot be undone
and could reasonably go either way, or a guardrail conflict.

============================================================
FIXED DESIGN (DECIDED HERE, BEFORE ANY DATA IS READ)
============================================================

F1. Universe. The 17 roots with owned 2010-2019 stores:
ext2010 (NG, NQ, ZN, 6E, GC, ZC) and ext2010h (ZT, ZF, ZB, UB, TN, CL,
ZL, ZS, RTY, HE, LE). Each root's vehicle, tick value and D8 cost are
the ones E.12 froze for its exposure. The admissibility filter (V2.2)
runs as frozen, on the search window only.

F2. Windows.
- Search: 2019-05-06..2024-02-29, the E.12 training stores under
  data/processed_step2/. Nothing on or after 2024-03-01 is read: not the
  March 2024 embargo, not holdout-2, not the research window.
- Backward test: each root's window in reports/stage_e16_windows.json
  ("products") up to 2019-05-05 (2010-07 for most; TN 2016-01, RTY
  2017-06, HE 2017-07; LE 2010-06-07..2014-12-14 excluded, R-S3), from
  data/processed_hist/ext2010 and ext2010h, with the E.16 rulings'
  conventions for sessions, closures and price limits in that period.

F3. Read guard. Every search process imports a guard that raises on any
path under data/processed_hist/, data/sealed/, the holdout stores, or any
bar dated 2024-03-01 or later. A test plants each case and shows that it
raises. The backward evaluation is the only code allowed past the guard,
and only behind its run-once marker after the registration line exists.

F4. Features: V2.3's library as ml_route_v2/signals computes it, cut
BEFORE any fit by one rule: a feature enters only if every leg it reads
is one of the 17 roots and every calendar it needs (releases, auctions,
fixes, holidays, sessions) is available causally over both windows. The
cut is decided from listing dates and calendar coverage alone, never from
any value in either window. Every dropped feature is logged with its
reason. C1's lesson: no feature may be not-applicable by design in the
backward window; such features are dropped now, not exempted later.

F5. Pipeline: V2.2 clock, V2.4 normalization, V2.5 targets (horizons as
frozen), V2.6 models (ridge lambda in {0.01, 0.1, 1.0}; LightGBM depth 2
and 3 with V2.6's fixed settings), V2.7 cost gate (gross reading, k in
{1.5, 2, 3}), V2.8 sizing and caps at 50K, V2.9 nested CPCV (6 blocks, 2
test, 15 splits, purge, one-date embargo), selection metric, tie rules
and eligibility. 45 configurations, no others. Positions are flat by
15:08 CT as V2.2 builds.

F6. Departures from the v2 design, and only these:
- Gate 0 (V2.2b, training-window criterion 1) is waived: this is a
  search, and the backward test is its confirmation.
- The training-window verdict becomes the SCREEN below. v2 set t >= 3.0
  because its only confirmation was the 1.2-year research window; here
  the confirmation is a 9-year backward test.
- The universe is F1, and the features are cut by F4.

F7. Trial accounting. The 45 configurations are registered before any
fit (V2.9: N_total = N_program + 45; N 480 -> 525), with ids E20-S01 to
E20-S45 mapped to the grid. The backward test is registered after the
freeze as E20-B1 (N 526). If the screen fails, nothing more is
registered.

F8. SCREEN (on the nested out-of-sample record; all must hold):
1. The nested OOS median-path daily t >= 2.0.
2. PBO < 0.5.
3. The nested OOS annualized net Sharpe >= 0.5 at 50K (E.19's
   break-even band), and <= 4.0 (above 4.0 is a leakage alarm: hold the
   result and run an independent Fable leakage audit first).
Reported, not gating: the DSR at N_total, the payout-simulation ruin
probability (V2.9 criterion 7), products with fewer than 30 OOS round
trips (flagged and kept, V2.9 criterion 6), the per-configuration CPCV
table.
A failed screen ends the stage: no freeze, no backward read. That is a
complete result.

F9. Freeze. On a passed screen, the final configuration is chosen and
refit on all six blocks exactly as V2.9 says. The freeze holds: the model
payload and its sha256, the feature list after F4, the normalization
state, the risk table from all six blocks, k, the vehicle and cost table,
the backward windows, the statistic, the pass bar and the code hashes.
Before the freeze commit, a dry check on synthetic sentinel frames that
mimic the 2010-2019 listing and calendar state of every leg shows every
feature computes; removing one leg's frames must stop it. No backward
bar is read by the dry check.

F10. Backward test, evaluated once (E20-B1). The frozen model trades the
backward windows at 50K with V2.7 and V2.8 as frozen, at 1.0 x D8.
Statistic: the daily net P&L series in dollars, zero on no-trade dates;
its daily t computed exactly as V2.9 computes the screen's daily t (the
frozen ml_route_v2 code), the one-sided p from the t distribution with
n_dates - 1 degrees of freedom (as gate0._b_test does), and the
annualized net Sharpe (daily mean / sd x sqrt(252)). PASS iff all hold:
- one-sided p <= 0.025;
- annualized net Sharpe >= 0.5;
- at least 100 round trips in total.
Descriptive only: per-year results, per product, 1.5 x slippage stress,
the DSR at N 526. A PASS is a candidate, not a strategy: it leads to the
forward research-window read and then holdout-2, each in its own stage,
and to no Combine (V33 item 1).

============================================================
SCOPE
============================================================

This stage does:
- audit the stores, windows and feature availability (Step 1)
- write the search plan; Fable reviews it before any fit (Step 2)
- build the search on ml_route_v2 with the guard and tests (Step 3)
- register the 45 configurations, run the search, apply the screen (Step 4)
- on a pass: freeze, Fable review, register, evaluate once, Fable
  recomputation (Steps 5 to 7)

This stage does NOT:
- buy anything, call Databento, or use either account
- read any 2010-2019 bar before E20-B1's registration line exists, or
  run the backward evaluation more than once
- read holdout-2, the March 2024 embargo, MES's sealed stores, the
  research window, or anything dated 2024-03-01 or later
- read the results of E.15, E.17 or E.18 on 2010-2019 (their verdict
  tables, per-period figures or trade files) while planning, searching
  or choosing; their code may be read
- fit any DNN, sequence model or RL policy (V28, V33)
- add configurations, horizons, features or models beyond F4 and F5
- change any file the harness v12, the v2 freeze, or the E.14, E.16 or
  E.18 freezes hash, except by a v2 amendment written, Fable-reviewed and
  committed before any fit; any other change is a stop
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V20 to V33.
3. docs/STAGE_E_ML_V2_DESIGN.md V2.0 to V2.9 in full.
4. reports/E.12_RETURN.md sections 1, 3 and 6; reports/stage_e12_gate0.md;
   reports/stage_e12_ml_v2_freeze.json.
5. reports/E.16_RETURN.md sections on windows; reports/stage_e16_rulings.md;
   reports/stage_e16_windows.json.
6. reports/stage_e14_prereg_C1.md and c1_replication/ (code and README
   only: how C1 froze a model and guarded a backward read).
7. reports/E.19_RETURN.md sections 1 and 7 (the 50K economics).
8. The code: ml_route_v2/ (pipeline.py, panel.py, signals/, cpcv.py,
   selection_metric.py, sizing.py, gate0.py), screening/trial_registry.py.

============================================================
GUARDRAILS
============================================================

- Harness v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32,
  verified at start and end, unchanged. Fresh PYTHONPYCACHEPREFIX outside
  the repository for harness commands.
- The 17 search stores and the 17 backward stores verify against their
  recorded sha256 at start; the backward ones by hash only, without
  decoding a bar.
- Order of events, shown with timestamps: audit, plan review, 45-config
  registration, search, screen, (freeze review, dry check, freeze commit,
  E20-B1 registration, evaluation, Fable recomputation).
- Holdout status all_ok, 0 unlocks, at start and end. The spend ledger is
  unchanged.
- Start and end checks, quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the manifest checks, the cluster freezes, the v2,
  E.14, E.16 and E.18 freeze verifications, the ledger line count and
  sha256, N, and `uv run pytest -q -p no:cacheprovider`.
- Compute: nice 10, free memory checked before each heavy run, resumable
  by configuration and split.
- Before ending, confirm no worker or background shell is still running.

============================================================
STEPS
============================================================

STEP 0: STARTUP (lead). Start checks; STATE; ETA table.

STEP 1: AUDIT (DataAudit-OpusHigh, worker-high on opus). For the 17
roots: the search stores' coverage and hashes; the backward stores'
hashes only; each root's vehicle, tick value and D8 cost from E.12's
freeze; the feature cut of F4 from listing dates and calendar coverage,
every dropped feature with its reason. Output
reports/stage_e20_audit.md and .json.

STEP 2: PLAN AND REVIEW. The lead writes reports/stage_e20_plan.md: the
universe, the kept features, the 45-configuration grid with ids, the
guard, the screen, the freeze contents, the backward test and its bar,
and any v2 amendment needed with its diff. PlanReviewer-FableXHigh
(worker-xhigh on fable) checks it against this prompt and the v2 design:
leakage paths (normalization, the risk table, purge and embargo, the
admissibility filter), the F4 cut, the guard's coverage, and that the
screen and bar are exactly F8 and F10. Findings graded BLOCKING, SHOULD
FIX or NOTE in reports/stage_e20_review_plan.md. BLOCKING and SHOULD FIX
are fixed before any fit.

STEP 3: BUILD (SearchCoder-OpusXHigh, worker-xhigh on opus). A new
package pattern_search/ that configures and calls ml_route_v2 without
editing it, plus the guard. Tests: the guard's planted cases; V2.9's
perturbation, fold and canary tests rerun on the 17-root universe on
synthetic data; the grid count is 45; the feature list equals the plan's.

STEP 4: REGISTER, SEARCH, SCREEN (lead). Register E20-S01..S45 (N 480 ->
525) and record the registry lines in STATE before any fit. Run the
nested CPCV and the final selection. Apply F8. Write
reports/stage_e20_search.md and .json: the screen's numbers, the
per-configuration table, PBO, the DSR at 525, the ruin probability.
A failed screen: go to Step 8.

STEP 5: FREEZE (lead). F9's contents in reports/stage_e20_prereg_B1.md,
the dry check in reports/stage_e20_dry_check.md, and
FreezeReviewer-FableXHigh's review (BLOCKING and SHOULD FIX fixed
first). Manifest reports/stage_e20_freeze.json. One commit "E.20 B1
freeze".

STEP 6: REGISTER AND EVALUATE ONCE (lead). Register E20-B1 (N 526), then
run the backward evaluation once behind
reports/stage_e20_B1_RUN_ONCE.json. Verdict per F10, then the
descriptive outputs.

STEP 7: VERIFY (VerdictVerifier-FableXHigh, worker-xhigh on fable).
Recompute the verdict numbers independently, without reading the lead's
statistics first, and check the order of events in git and the registry.
Findings in reports/stage_e20_review.md, rulings in
reports/stage_e20_rulings.md. A BLOCKING finding is resolved by finding
the code error, never by a second evaluation.

STEP 8: RETURN AND COMMIT (lead). reports/E.20_RETURN.md, one dated
progress.md entry, one docs/STAGES.md line, one final commit "Stage E.20
pattern search". No push.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Audit | DataAudit-OpusHigh | opus | high | after 0 | coverage and feature cut, mechanical but exact |
| 2 Plan | lead | opus | xhigh | after 1 | design decisions reserved to the lead |
| 2 Review | PlanReviewer-FableXHigh | fable | xhigh | after the plan | independent leakage and scope check |
| 3 Build | SearchCoder-OpusXHigh | opus | xhigh | after the review | pipeline wiring and guard with tests |
| 4 Search | lead | opus | xhigh | after 3 | registration and screen reserved to the lead |
| 5 Freeze review | FreezeReviewer-FableXHigh | fable | xhigh | after the freeze text | independent check before registration |
| 6 Evaluate | lead | opus | xhigh | after 5 | verdict reserved to the lead |
| 7 Verify | VerdictVerifier-FableXHigh | fable | xhigh | after 6 | verdict numbers recomputed |
| 8 Return | lead | opus | xhigh | last | reserved to the lead |

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

Write reports/E.20_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 300 words: the screen's result with its
   numbers (median-path t, PBO, net Sharpe, DSR at 525); if run, E20-B1's
   verdict (PASS, FAIL or STOPPED with the rule) with t, p, net Sharpe
   and trades; the final N; the features dropped by F4; and what the
   outcome means.
2. Guardrail evidence: the start and end checks verbatim, and the order
   of events with timestamps.
3. Results per step, including the audit, the plan review, the
   per-configuration table and the dry check.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation: on a pass, the
   forward research-window read and holdout-2 (owned sealed only for MES,
   MCL, MGC, MHG and NG; any other product needs a purchase decision); on
   a fail, what is closed.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
