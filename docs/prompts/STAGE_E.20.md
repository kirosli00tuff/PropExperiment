STAGE E.20 "PATTERN SEARCH WITH PER-PRODUCT RESEARCH: A LITERATURE PASS PER ROOT, THE REST-OF-DAY MOMENTUM TEST ON NQ, THEN THE ML ROUTE'S NET PIPELINE ON 17 ROOTS WITH ONE FINAL MODEL TESTED BACKWARD"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Nothing has passed in 480 trials, and E.19 showed that the
Topstep funnel loses money without an edge (a net Sharpe of about 0.5 is
needed at 50K). The user chooses a pattern search (V33 item 5), revised
after the planning chat's literature run (V34;
reports/stage_e20_briefs/literature_planning_2026-10-10.md). Three parts,
in this order:
- Part A: one research agent per root (17) checks that root's published
  intraday evidence since 2015, audits its feature availability over both
  windows, and proposes at most two literature-sourced features.
- Part B: H6, the one published effect whose numbers clear the cost gate,
  tested directly: rest-of-day to last-half-hour momentum (Baltussen, Da,
  Lammers and Martens, JFE 2021) on NQ at MNQ cost, on 2020-06..2024-02,
  after the paper's sample. The program has read these NQ bars before
  (Gate 0), but never for this rule. Registered and evaluated once,
  before the search reads any data.
- Part C: the ML route's frozen net pipeline (docs/STAGE_E_ML_V2_DESIGN.md
  V2.3 to V2.9) on the 17 roots with owned 2010-2019 history, with a
  late-session decision time and Part A's features added. It reads only
  2019-05-06..2024-02-29. If its nested out-of-sample record clears the
  screen, its one final model is frozen, registered and evaluated once,
  backward, on the owned 2010-2019 stores.
Fable reviews each plan and freeze and recomputes each verdict. No
purchase, no Databento call.

Decisions in force: docs/DECISIONS.md V20 to V34. Binding, in this order:
this prompt's FIXED DESIGN, then docs/STAGE_E_ML_V2_DESIGN.md (its v2
freeze, reports/stage_e12_ml_v2_freeze.json), then docs/STAGE_E_DESIGN.md
CP1's bar and close conventions (for H6), then the E.16 rulings on the
2010-2019 windows (reports/stage_e16_rulings.md,
reports/stage_e16_windows.json).

Lead: Opus 5.5, effort xhigh. Ultracode: on (the user's choice, V34). The
session is launched interactively, per docs/ORCHESTRATION.md.

Why this lead and effort: 17 parallel research readers, one direct test
of a published effect, a model search and up to one more registered
evaluation, unattended. The silent failures to guard against: a feature
or calendar that does not exist in 2010-2019 (C1's C10 stop); a 2010-2019
or post-2024-02 byte read before its registration; H6's rule changed
after its data is read; leakage across CPCV folds; a configuration count
that understates the search; a literature claim taken from a secondary
source; and a wrong verdict number.

Usage: follows CLAUDE.md's context-hygiene rules. The user runs this
unattended. reports/stage_e20_STATE.md names, after every step, the step
finished, the hashes in force, N, each guard's state and the next step;
the session resumes from it after a usage pause. Expect 12 to 16 hours.
Part A's 17 readers run at most 4 at a time (.claude/settings.json).

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue. The only
stops are the ones this prompt names, a decision that cannot be undone
and could reasonably go either way, or a guardrail conflict.

============================================================
FIXED DESIGN (DECIDED HERE, BEFORE ANY DATA IS READ)
============================================================

F1. Universe. The 17 roots with owned 2010-2019 stores: ext2010 (NG, NQ,
ZN, 6E, GC, ZC) and ext2010h (ZT, ZF, ZB, UB, TN, CL, ZL, ZS, RTY, HE,
LE). Each root's vehicle, tick value and D8 cost are those E.12 froze for
its exposure (reports/stage_e12_ranking.json, reports/stage_e2a_costs.md).

F2. Windows.
- H6: 2020-06-01..2024-02-29 from the E.12 NQ store
  (data/processed_step2/NQ), with the 60 trade dates before 2020-06-01
  allowed as warm-up for T2's median.
- Search: 2019-05-06..2024-02-29, the E.12 training stores under
  data/processed_step2/.
- Backward test: each root's window in reports/stage_e16_windows.json
  ("products") up to 2019-05-05 (2010-07 for most; TN 2016-01, RTY
  2017-06, HE 2017-07; LE 2010-06-07..2014-12-14 excluded, R-S3), from
  data/processed_hist/ext2010 and ext2010h, with the E.16 rulings'
  conventions for sessions, closures and price limits.
- Never read in this stage: anything dated 2024-03-01 or later (the March
  2024 embargo, holdout-2, the research window), MES's sealed stores.

F3. Read guard. Every Part B and Part C process imports a guard that
raises on any path under data/processed_hist/, data/sealed/, the holdout
stores, or any bar dated 2024-03-01 or later. H6's evaluation is further
limited to the NQ store. A test plants each case and shows that it
raises. Only the Part C backward evaluation passes the 2010-2019 guard,
behind its run-once marker, after its registration line exists.

F4. Part A, one reader per root (ProductReader-<ROOT>-OpusHigh,
worker-high on opus, per CLAUDE.md's literature routing). Each writes
reports/stage_e20_briefs/product_<ROOT>.md and .json with:
1. Published intraday evidence for that root or its asset class since
   2015: effect, rule, hold, gross per trade, gross or net, sample, decay
   evidence, source. Start from the planning brief; verify every claim it
   relies on against the primary source; mark secondary-only claims.
2. Feature availability over both windows: every V2.3 feature that reads
   this root, with its legs and calendars, and whether each exists causally
   in 2010-2019 and 2019-2024, decided from listing dates and calendar
   coverage only, never from a bar value.
3. At most two proposed literature features: a published rule turned into
   a causal value at a decision time, computable from the 17 roots' bars
   and calendars available in both windows; source, formula, and its
   expected gross per trade against the root's D8 cost (V31). No feature
   may come from looking at this program's data.
4. For NQ only: the H6 details below, and whether the SqueezeMetrics daily
   GEX CSV may be fetched and used under its terms (read the terms first;
   CLAUDE.md's page-fetch order). Its answer decides T3 before any NQ bar
   is read.
Web rules: CLAUDE.md's research rules; pages saved to disk before use;
never fetch CME's site or any archived copy of it by automation; read a
site's terms before any automated fetch. Readers do not open any data
store and do not read E.15, E.17 or E.18 results.

F5. Part B, H6 (rest-of-day to last-half-hour momentum on NQ), fixed now.
Vehicle MNQ, one lot, D8 MNQ costs in the entry and exit buckets. C is
the equity group's close as CP1 defines it (docs/STAGE_E_DESIGN.md, CP1
row: 15:00 CT on a normal day, the early close on a shortened day), and
the bar, intent and fill conventions are CP1's, through the frozen engine.
- Signal at C-30: r_ROD = P(C-30) / P(prior C) - 1, where P(C-30) is the
  close of the bar ending at C-30 and P(prior C) is the close of the bar
  ending at the previous trade date's C. Both bars must exist with one
  instrument_id, else no trade. r_ROD = 0: no trade.
- Entry: market intent on the bar ending at C-30, in sign(r_ROD), filling
  at the next open. Exit: CP1's exit (market intent on the first bar at or
  after C-2 min, filling at the next open).
- E20-H6-T1: every eligible date.
- E20-H6-T2: only dates where |r_ROD| exceeds the median of |r_ROD| over
  the previous 60 eligible trade dates (Rosa, J. Futures Markets 2022, the
  threshold form).
- E20-H6-T3, only if the NQ reader clears the GEX source under its terms
  before any NQ bar is read: only dates whose previous trade date's GEX is
  negative (Baltussen et al.: momentum present when NGE is negative). If
  not cleared, T3 is not registered.
- Statistic per test: the per-date net P&L (one trade a day), t_B and the
  one-sided p by gate0._b_test (the frozen code C1 used); annualized net
  Sharpe over all trade dates in the window at one MNQ, zero on no-trade
  dates.
- PASS per test iff all hold: one-sided p within Holm's step-down at family
  alpha 0.025 over the registered H6 tests; mean gross per trade >= 1.5c
  (c = that trade's D8 round trip); at least 100 trades (30 for T3);
  annualized net Sharpe >= 0.5.
- Descriptive only: per-year results, the 1.5 x slippage stress, gross and
  net in bp, and the 2019-05-06..2020-05-29 overlap with the paper's
  sample reported separately and never in the verdict.
- Power, for the record: at the paper's per-day Sharpe of 0.055 to 0.11 on
  about 930 dates, the expected t is about 1.7 to 3.4 before decay.

F6. Part C, the search.
- Pipeline: V2.2 clock, V2.4 normalization, V2.5 targets, V2.6 models
  (ridge lambda in {0.01, 0.1, 1.0}; LightGBM depth 2 and 3 with V2.6's
  fixed settings), V2.7 cost gate (gross reading, k in {1.5, 2, 3}), V2.8
  sizing and caps at 50K, V2.9 nested CPCV (6 blocks, 2 test, 15 splits,
  purge, one-date embargo), selection metric, tie rules and eligibility.
  45 configurations, no others. Market orders only (the planning brief's
  passive-fill evidence).
- Additions, and only these:
  1. A fourth decision time t4 = F_X - 60 min for every group; t4 rows
     enter the h60 and F horizons only (h120 does not fit).
  2. Two features at every decision time: r_ROD(t) = P(t) / P(prior
     close) - 1 with the group's close as V2.2 and D6 define it, and
     |r_ROD(t)| over its median over the previous 60 trade dates.
  3. The Part A features the plan review accepts.
- Feature cut before any fit: a feature enters only if every leg it reads
  is one of the 17 roots and every calendar it needs exists causally over
  both windows (Part A item 2). No feature may be not-applicable by
  design in the backward window; such features are dropped now, not
  exempted later. Every dropped feature is logged with its reason.
- Departures from the v2 design, and only these: Gate 0 is waived (this
  is a search, and the backward test confirms it); the training-window
  verdict becomes the SCREEN; the universe is F1; the clock and features
  are as above.

F7. SCREEN (on the nested out-of-sample record; all must hold):
1. The nested OOS median-path daily t >= 2.0.
2. PBO < 0.5.
3. The nested OOS annualized net Sharpe >= 0.5 at 50K, and <= 4.0 (above
   4.0 is a leakage alarm: hold the result and run an independent Fable
   leakage audit first).
Reported, not gating: the DSR at N_total, the ruin probability (V2.9
criterion 7), products with fewer than 30 OOS round trips (flagged and
kept, V2.9 criterion 6), the per-configuration table, and the share of
the final model's OOS P&L from t4 rows and from the r_ROD features (the
planning brief expects a surviving late-session signal to be H6 found
again).
A failed screen ends Part C: no freeze, no backward read. That is a
complete result.

F8. Freeze and backward test (E20-B1). On a passed screen, the final
configuration is chosen and refit on all six blocks as V2.9 says. The
freeze holds the model payload and its sha256, the feature list, the
normalization state, the risk table from all six blocks, k, the vehicle
and cost table, the backward windows, the statistic, the bar and the code
hashes. Before the freeze commit, a dry check on synthetic sentinel
frames that mimic the 2010-2019 listing and calendar state of every leg
shows every feature computes; removing one leg's frames must stop it.
The backward evaluation runs once at 50K with V2.7 and V2.8 as frozen, at
1.0 x D8. Statistic: the daily net P&L in dollars, zero on no-trade
dates; its daily t computed as V2.9 computes the screen's daily t; the
one-sided p from the t distribution with n_dates - 1 degrees of freedom;
the annualized net Sharpe. PASS iff: one-sided p <= 0.025; annualized
net Sharpe >= 0.5; at least 100 round trips. Descriptive only: per year,
per product, 1.5 x slippage, the DSR at the final N.

F9. Trial accounting, in order of registration: H6 (E20-H6-T1, T2, and
T3 if cleared: N 480 -> 482 or 483); the 45 configurations before any
fit (E20-S01..S45: +45); E20-B1 only after a passed screen (+1). A pass
anywhere is a candidate, not a strategy: it leads to the forward
research-window read and then holdout-2, each in its own stage, and to no
Combine (V33 item 1).

============================================================
SCOPE
============================================================

This stage does:
- Part A: 17 product readers, consolidated by the lead (Step 1)
- Part B: H6 plan, Fable review, freeze, register, evaluate once, Fable
  recomputation (Steps 2 to 4)
- Part C: search plan, Fable review, build, register the 45, search,
  screen; on a pass, freeze, Fable review, register B1, evaluate once,
  Fable recomputation (Steps 5 to 9)

This stage does NOT:
- buy anything, call Databento, or use either account
- read any 2010-2019 bar before E20-B1's registration line exists, read
  any NQ bar before H6's registration, or run any evaluation twice
- read Gate 0's NQ rows (reports/stage_e12_gate0.md and .json) before
  H6's evaluation
- read anything dated 2024-03-01 or later, or MES's sealed stores
- read the results of E.15, E.17 or E.18 on 2010-2019 (verdict tables,
  per-period figures, trade files) while planning, searching or choosing;
  their code may be read
- fit any DNN, sequence model or RL policy (V28, V33)
- add configurations, horizons, features, models or tests beyond F5 and F6
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
2. docs/DECISIONS.md V20 to V34.
3. reports/stage_e20_briefs/literature_planning_2026-10-10.md.
4. docs/STAGE_E_ML_V2_DESIGN.md V2.0 to V2.9 in full; docs/STAGE_E_DESIGN.md
   D6, D8, D9 and the CP1 row.
5. reports/stage_e13_info_sources.md section 2.7 (dealer gamma, GEX
   source and terms notes).
6. reports/E.12_RETURN.md sections 1, 3 and 6; reports/stage_e12_ml_v2_freeze.json;
   reports/stage_e12_gate0.md only after H6's evaluation.
7. reports/E.16_RETURN.md (windows); reports/stage_e16_rulings.md;
   reports/stage_e16_windows.json.
8. reports/stage_e14_prereg_C1.md and c1_replication/ (code and README
   only: how C1 froze a model and guarded a backward read).
9. reports/E.19_RETURN.md sections 1 and 7 (the 50K economics).
10. The code: ml_route_v2/ (pipeline.py, panel.py, signals/, cpcv.py,
    selection_metric.py, sizing.py, gate0.py), base_rules/ (engine use),
    screening/trial_registry.py.

============================================================
GUARDRAILS
============================================================

- Harness v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32,
  verified at start and end, unchanged. Fresh PYTHONPYCACHEPREFIX outside
  the repository for harness commands.
- The search and backward stores verify against their recorded sha256 at
  start; the backward ones by hash only, without decoding a bar.
- Order of events, shown with timestamps: Part A; H6 review, freeze,
  registration, evaluation, verification; search plan review, 45
  registrations, search, screen; (B1 freeze review, dry check, freeze
  commit, registration, evaluation, verification).
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

STEP 1: PART A (17 ProductReader-<ROOT>-OpusHigh, at most 4 at a time;
NQ first). Then the lead consolidates reports/stage_e20_product_summary.md:
per root, the evidence table, the feature availability, the proposed
features, and the NQ reader's GEX ruling.

STEP 2: H6 PLAN AND REVIEW. The lead writes reports/stage_e20_prereg_H6.md
from F5 exactly, with T3's status, and the code in a new package
h6_rod/ (the frozen engine called, never edited) with tests on synthetic
bars (the signal, the C-30 and C-2 bars, early closes, missing bars, the
threshold's warm-up, the guard). H6Reviewer-FableXHigh (worker-xhigh on
fable) checks the text against F5, the rule against the paper's, and the
code against the text. BLOCKING and SHOULD FIX are fixed before the
freeze. Findings in reports/stage_e20_review_h6.md.

STEP 3: H6 FREEZE, REGISTER, EVALUATE ONCE (lead). Manifest
reports/stage_e20_h6_freeze.json; commit "E.20 H6 freeze". Register the
H6 tests; then evaluate once behind reports/stage_e20_H6_RUN_ONCE.json.
Verdict per F5, then the descriptive outputs.

STEP 4: H6 VERIFY (VerdictVerifier-FableXHigh). Independent
recomputation without reading the lead's statistics first; the order of
events in git and the registry. Findings in reports/stage_e20_review.md,
rulings in reports/stage_e20_rulings.md. A BLOCKING finding is resolved
by finding the code error, never by a second evaluation.

STEP 5: SEARCH PLAN AND REVIEW. The lead writes reports/stage_e20_plan.md:
the universe, the kept and dropped features with reasons, Part A's
accepted features, t4, the 45-configuration grid with ids, the guard,
the screen, the freeze contents, the backward test and its bar, and any
v2 amendment with its diff. PlanReviewer-FableXHigh checks it against
this prompt and the v2 design: leakage paths (normalization, the risk
table, purge and embargo, the admissibility filter), the feature cut,
each Part A feature's source and causality, the guard's coverage, and
that the screen and bar are exactly F7 and F8. BLOCKING and SHOULD FIX
are fixed before any fit. Findings in reports/stage_e20_review_plan.md.

STEP 6: BUILD (SearchCoder-OpusXHigh, worker-xhigh on opus). A new
package pattern_search/ that configures and calls ml_route_v2 without
editing it, plus the guard, t4 and the added features. Tests: the
guard's planted cases; V2.9's perturbation, fold and canary tests rerun
on the 17-root universe on synthetic data; the grid count is 45; the
feature list equals the plan's; t4 and r_ROD on synthetic bars.

STEP 7: REGISTER, SEARCH, SCREEN (lead). Register E20-S01..S45 and record
the registry lines in STATE before any fit. Run the nested CPCV and the
final selection. Apply F7. Write reports/stage_e20_search.md and .json.
A failed screen: go to Step 10.

STEP 8: B1 FREEZE (lead). F8's contents in reports/stage_e20_prereg_B1.md,
the dry check in reports/stage_e20_dry_check.md, and
FreezeReviewer-FableXHigh's review (BLOCKING and SHOULD FIX fixed first).
Manifest reports/stage_e20_freeze.json. Commit "E.20 B1 freeze".

STEP 9: B1 REGISTER, EVALUATE ONCE, VERIFY. Register E20-B1, evaluate
once behind reports/stage_e20_B1_RUN_ONCE.json, verdict per F8; then
VerdictVerifier-FableXHigh recomputes as in Step 4.

STEP 10: RETURN AND COMMIT (lead). reports/E.20_RETURN.md, one dated
progress.md entry, one docs/STAGES.md line, one final commit "Stage E.20
pattern search". No push.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Part A | 17 x ProductReader-<ROOT>-OpusHigh | opus | high | 4 at a time | literature reading and availability audit per root (CLAUDE.md routing) |
| 1 Consolidation | lead | opus | xhigh | after the readers | feature acceptance reserved to the lead |
| 2 H6 review | H6Reviewer-FableXHigh | fable | xhigh | after the H6 text and code | independent check before a registration |
| 3 H6 evaluate | lead | opus | xhigh | after 2 | registration and verdict reserved to the lead |
| 4, 9 Verify | VerdictVerifier-FableXHigh | fable | xhigh | after each evaluation | verdict numbers recomputed |
| 5 Plan review | PlanReviewer-FableXHigh | fable | xhigh | after the plan | leakage and scope check |
| 6 Build | SearchCoder-OpusXHigh | opus | xhigh | after 5 | pipeline wiring, guard, additions, tests |
| 7 Search | lead | opus | xhigh | after 6 | registration and screen reserved to the lead |
| 8 Freeze review | FreezeReviewer-FableXHigh | fable | xhigh | after the freeze text | independent check before registration |
| 10 Return | lead | opus | xhigh | last | reserved to the lead |

Usage pools: Fable runs only the reviews and verifications. If Fable
passes about 40% of the weekly bar mid-stage, keep Fable for the verdict
recomputations and move the plan and freeze reviews to opus xhigh
(docs/ORCHESTRATION.md).

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

1. Verdict summary, at most 350 words: H6's verdict per test (PASS, FAIL
   or STOPPED with the rule) with mean gross and net in bp, t_B, p, net
   Sharpe and trades; whether T3 ran; the screen's result with its
   numbers (median-path t, PBO, net Sharpe, DSR); if run, E20-B1's verdict
   with t, p, net Sharpe and trades; the final N; the features dropped
   and added; and what the outcome means.
2. Guardrail evidence: the start and end checks verbatim, and the order
   of events with timestamps.
3. Results per part: Part A's per-root table (evidence, availability,
   proposed and accepted features), H6, the search's per-configuration
   table and the t4 and r_ROD shares, and the dry check.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation: on any pass, the
   forward research-window read and holdout-2 (owned sealed only for MES,
   MCL, MGC, MHG and NG; NQ and the rest need a purchase decision); on a
   fail, what is closed.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
