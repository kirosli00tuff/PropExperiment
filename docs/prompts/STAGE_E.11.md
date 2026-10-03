STAGE E.11 "ML ROUTE V2, A QUANT-STYLE PORTFOLIO MODEL: DRAFT THE DESIGN AND BUILD THE PIPELINE ON SYNTHETIC DATA (NO MARKET DATA READ, NO PURCHASE, NO TRAINING)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E screened 198 hand-written trials across all eight clusters,
and Stage E.10 showed that a low-frequency rule cannot reach eps on its
own: at one or two trades a week, each trade would need a move several
times larger than any published effect. Any edge the program finds will be
a component edge, small pieces that only matter in combination. The user
decided (V20) that the frozen ML route is replaced by ML route v2: a
quant-style portfolio model built the way a quant trader builds one,
within the program's technology and Topstep's rules. This session drafts
the v2 design for the user and builds the whole pipeline, tested on
synthetic data only: the signal library (every K1 to K9 family as a
feature, plus generic features), causal normalization, targets, alpha
combination models, a cost-aware decision layer, risk-scaled sizing,
portfolio construction under the XFA constraints, a walk-forward and
nested-selection framework, the portfolio simulator on the frozen Stage E
engine, leakage canaries, and the per-account Databento key fix. Fable
reviews the design and the code. Nothing reads market data, nothing is
bought, nothing is trained on real bars. The user decides the open points,
and a later session freezes the design, buys the training history and
trains.

Decisions in force: docs/DECISIONS.md V20 (ML route v2), V18 (a minimum
trade count stated before any data is read), V19 (account keys and caps),
V21 (K9-anncday-01 is folded into v2 as a candidate signal, with no K9
screen. E.10's design inputs carry forward: the cost wall, K = 10 as the
proposed maximum Holm K, a minimum trade count of 30 per evaluated unit).

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: this is a long design and build session, the
E.2b pattern. The silent failures to guard against are look-ahead (a
feature, normalizer, target or selection step that sees the future), a
design that leaves a free parameter to be chosen after seeing results, and
a simulator that is more generous than the frozen engine. CLAUDE.md routes
code touching screening/ and data/ to opus at xhigh and every independent
check to Fable. Ultracode stays off: at most four workstreams at once.

Usage: follows CLAUDE.md's context-hygiene rules. The user runs this
unattended overnight, across usage windows. The auto-retry launcher
resumes it with "read the STATE file first", so reports/stage_e11_STATE.md
names, after every task, the task finished, the files and hashes in force
and the next task. Compute: the ThinkPad under the overnight profile, with
synthetic data only. Expect 6 to 9 hours.

Do not stop to ask. Decide, log the choice under Open choices in the return
document, and continue. The only stops are the ones this prompt names, a
decision that cannot be undone and could reasonably go either way, or a
guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- draft docs/STAGE_E_ML_V2_DESIGN.md, the pre-registration text for v2,
  with every open point listed for the user (Task 1)
- build the v2 pipeline in a new package ml_route_v2/, reusing ml_route/
  and the frozen Stage E harness where they fit (Tasks 2 to 5)
- teach data/config.py to select the Databento key by account, and write
  the next harness manifest (Task 6)
- test everything on synthetic data, including leakage canaries and a
  runtime probe at full scale (Task 7)
- have Fable review the design and the code (Task 8)

This stage does NOT:
- read any bar, quote, cost sample or market data file, in any window, or
  open any Stage E screen or confirmation record for its numbers. The
  frozen cost tables, rules tables, release calendars and the member
  modules' code may be read.
- choose any model, feature set, threshold or parameter from data. Every
  default in the design is a stated rule or a grid to be searched later
  on the training window only.
- call Databento, buy anything, or raise any account cap (the cap raise
  belongs to the purchasing session)
- train any model on real data, or run anything on the research window
- freeze the v2 design (the user decides first), edit
  docs/STAGE_E_ML_DESIGN.md, docs/STAGE_E_DESIGN.md, docs/NULL_CRITERIA*.md
  or any member module
- touch holdout-1 or holdout-2, live/, ops/, or any TopstepX credential
  or API
- print, copy or log any key
- write to REGISTRATION.md (it stays 0 bytes)
- push. The session makes exactly the commits Tasks 6 and 9 name.

============================================================
CONTEXT TO READ FIRST
============================================================

Read by section, as CLAUDE.md's context-hygiene rules require.

1. CLAUDE.md and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V10 to V21.
3. docs/STAGE_E_ML_DESIGN.md (FROZEN, v1): M1 (the data partition), M2
   (pooling), M3 (the challengers), M4 (features and targets), M6 (trial
   accounting), M7 (leakage controls), M8 (compute). v2 keeps M1, M7 and
   M8's rules unless the draft says why not, and replaces M5's
   distillation with a deployable model or rule set (user decision).
4. reports/E.10_RETURN.md sections 1, 3 (the design target and the cost
   wall) and 7. reports/stage_e10_design_target.md and
   reports/stage_e10_catalog_K9.md (K9-anncday-01's frozen-to-be text).
5. docs/STAGE_E_DESIGN.md (FROZEN): D2 (vehicles, q_c), D3 (eps), D4
   (windows, holdout-2), D5, D6 (session rows), D8 (costs), D9 (the
   constraint set, the flatten, the lot limits).
6. The code: ml_route/ (features, blocks, selection, lgbm, lstm, store,
   ledger, synthetic, stage_e_adapter), screening/stage_e_engine.py (the
   multi-leg engine and the account model), screening/stage_e_align.py,
   strategy/members/k1..k8/ (each member's decision variables),
   data/config.py, screening/harness_freeze.py.
7. reports/stage_e0_topstep_facts.json: the lot limits for 50K and 150K,
   the trailing MLL, the payout rules.

============================================================
GUARDRAILS
============================================================

- No market data, no Stage E result figures, no Databento call. All tests
  run on ml_route/synthetic.py data or new synthetic generators.
- Every v2 component is causal: any value used at decision time t is
  computed only from data available before t (closed bars, published
  events). The leakage canaries prove it.
- The simulator is never more generous than the frozen engine: the same
  fills, costs, flatten, lot limits and trailing MLL.
- Every Stage E harness command takes `--harness-sha256
  9a8ebe7364beb7980eaea923888e06c2da253b7ff8ce2ce771b55045caf22f87` (v6)
  until Task 6 commits the next manifest, then the new sha256. Fresh
  PYTHONPYCACHEPREFIX outside the repository.
- No key printed, copied or logged. REGISTRATION.md stays 0 bytes. No
  TopstepX reference. Holdout status all_ok, 0 unlocks, at start and end.
  The ledger is unchanged.

Start and end checks, quoted verbatim in the return: `git status
--short`, `git log --oneline -3`, the holdout status, `wc -c
REGISTRATION.md`, the manifest checks, the ledger total, `uv run pytest -q`.

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead. Output: reports/stage_e11_STATE.md and the ETA table.
- Done when: the start checks pass, HEAD is the commit holding this prompt
  or a descendant with a clean tree, and the preflight accepts v6.

============================================================
TASK 1: THE V2 DESIGN DRAFT (LEAD)
============================================================

- Owner: lead. Output: docs/STAGE_E_ML_V2_DESIGN.md (DRAFT, not frozen),
  written as a pre-registration a quant would sign before touching data.
  Sections, each with a stated rule or a bounded grid, never "chosen
  later by looking":
  V2.1 Universe and data: the 28 traded exposures and their vehicles, the
  windows (training S_X..2024-02-29, embargo, holdout-2 sealed, research
  window tested once), the purchase plan (acct-1 first, then acct-2, V19).
  V2.2 Decision clock: a fixed small set of decision times per product
  per session (proposed: the session open and two or three fixed times),
  and a frequency cap per product, so turnover stays inside the cost wall.
  V2.3 Signals: the candidate signal library. Every K1 to K9 member's
  decision variable as a feature, all of them (V20: never chosen by
  Stage E results), and generic features (returns over several
  horizons, realized volatility, range, gap, time of day, day of week,
  calendar and release flags, cross-product returns from other clusters).
  Each with its availability time.
  V2.4 Normalization: causal rolling z-scores or ranks, window lengths
  fixed in the draft.
  V2.5 Targets: forward net return per decision time over a fixed set of
  horizons ending at or before the flatten, in vehicle ticks after the
  frozen D8 cost.
  V2.6 Alpha combination: the model families (a regularized linear
  baseline, gradient-boosted trees, and at most one small neural network),
  each with a bounded hyperparameter grid, pooled across products with
  product and cluster identifiers.
  V2.7 Decision layer: trade only when the predicted net edge exceeds a
  cost multiple, the multiple chosen on the training window by nested
  selection.
  V2.8 Sizing and portfolio: volatility-scaled size per position, capped
  at the lot limit, a risk budget derived from the trailing MLL (50K and
  150K stated separately), a cap on simultaneous positions and on any one
  cluster, everything flat by 15:08 CT.
  V2.9 Evaluation: walk-forward blocks on the training window with nested
  selection, the trial count for DSR at program N (every configuration
  counts), the minimum trade count (30 per evaluated unit), and the
  success criteria for the one research-window test, then the holdout-2
  registered read, then paper trading. Portfolio-level economics: daily
  P&L in dollars at the 50K and 150K constraints against eps at portfolio
  level.
  V2.10 Deployment: the user's choice, stated as options with their
  trade-offs: (a) a frozen model, weights fixed and hashed, never
  retrained live, or (b) a distilled rule set as v1's M5. Open.
  V2.11 Compute: the ThinkPad, the Windows PC (V10, E.2c), or another
  host the user names, with the runtime probe's figures (Task 7). Open.
  V2.12 What the user decides, collected.
- Done when: every section has a rule or a bounded grid, and every open
  point is in V2.12.

============================================================
TASKS 2 TO 5: THE BUILD (WORKERS, IN PARALLEL WHERE THE INTERFACES ALLOW)
============================================================

The lead first writes reports/stage_e11_interfaces.md: the module list,
each public function's signature, and the data contracts between them.
Then:

TASK 2: SIGNAL LIBRARY AND TARGETS
- Owner: SignalCoder-OpusXHigh, worker-xhigh on opus.
- Output: ml_route_v2/signals/ (one function per K1 to K9 family decision
  variable, computed causally from bars and the frozen calendars, each
  traced to its member module or catalog entry, plus the generic
  features), ml_route_v2/normalize.py, ml_route_v2/targets.py, and tests.
- Done when: every family in the frozen catalogs has a signal or a logged
  reason it cannot be one (for example a member whose only content is a
  fixed clock trade), and every signal has a causality test.

TASK 3: MODELS, SELECTION AND THE DECISION LAYER
- Owner: ModelCoder-OpusXHigh, worker-xhigh on opus.
- Output: ml_route_v2/models.py (the families in V2.6, reusing
  ml_route/lgbm.py and lstm.py where they fit), ml_route_v2/walkforward.py
  (blocks and nested selection, reusing ml_route/blocks.py and
  selection.py), ml_route_v2/decide.py (the cost-multiple gate), the
  configuration ledger (every configuration counted for DSR), and tests.

TASK 4: SIZING, PORTFOLIO AND THE SIMULATOR
- Owner: PortfolioCoder-OpusXHigh, worker-xhigh on opus.
- Output: ml_route_v2/sizing.py, ml_route_v2/portfolio.py, and
  ml_route_v2/simulate.py, which runs the portfolio's orders through the
  frozen Stage E engine as one multi-leg account (shared trailing MLL,
  lot limits, flatten, D8 costs, D9 constraints), and tests that pin a
  hand-computed portfolio day to the cent.

TASK 5: LEAKAGE CANARIES AND THE END-TO-END DRY RUN
- Owner: CanaryCoder-OpusXHigh, worker-xhigh on opus.
- Output: tests/test_ml_v2_leakage.py: a planted future bar, a planted
  future release, a shuffled-target run that must find no edge, a
  normalizer that would peek, a selection step that would see the test
  block, and a product whose bars are shifted by one minute. Each must be
  caught. And an end-to-end dry run on synthetic data of realistic size
  (28 products, the training window's date count, the full grid), with
  wall time, peak memory and disk per stage written to
  reports/stage_e11_runtime_probe.md.

============================================================
TASK 6: THE ACCOUNT KEY FIX (LEAD, SMALL)
============================================================

- Owner: lead, or KeyFix-OpusXHigh.
- Output: data/config.py reads DATABENTO_API_KEY1 for acct-1 and
  DATABENTO_API_KEY2 for acct-2, by ACTIVE_ACCOUNT (or the account a
  purchase names), refusing by name when the variable is missing or empty.
  No other config change: the caps stay as they are. Tests that never
  print a key. The next harness manifest (only data/config.py and its
  test differ), verified, and one commit "harness v7, per-account
  Databento keys" with the new sha256.

============================================================
TASK 7: SUITE AND RUNTIME PROBE (LEAD)
============================================================

- The full suite passes. The runtime probe gives the full grid's
  estimated time on the ThinkPad (20 threads, 14 GB, RTX 3050 4 GB, the
  overnight profile), and how it splits into 8 to 10 hour windows that
  pause cleanly at checkpoints (V12).

============================================================
TASK 8: REVIEW (FABLE)
============================================================

- Owners: DesignReviewer-FableMax (worker-max on fable) for the design
  draft, and CodeReviewer-FableXHigh (worker-xhigh on fable) for the code.
  Neither wrote what it reviews.
- DesignReviewer checks: every free parameter is either a stated rule or
  a bounded grid searched only on the training window, the trial count is
  complete, the success criteria are fixed, nothing selects on Stage E
  results, the cost and risk constraints match the frozen rules, and the
  open points are complete.
- CodeReviewer checks: causality of every signal, normalizer, target and
  selection step, that the simulator matches the frozen engine, that the
  canaries can fail, the key fix (no key ever printed), and determinism.
- Output: reports/stage_e11_review.md, findings graded BLOCKING, SHOULD
  FIX or NOTE.

============================================================
TASK 9: RULINGS, RETURN AND COMMIT (LEAD)
============================================================

- Output: reports/stage_e11_rulings.md, the fixes, the full suite passing,
  and one commit holding exactly ml_route_v2/, its tests, the design
  draft, the interfaces, the runtime probe, the review and the rulings,
  message "Stage E.11 ML route v2 design draft and build", with this
  repository's attribution lines.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Design draft | lead | opus | xhigh | after 0 | pre-registration judgment, reserved to the lead |
| Interfaces | lead | opus | xhigh | after 1 | contracts between workers |
| 2 Signals, targets | SignalCoder-OpusXHigh | opus | xhigh | parallel | causal feature code |
| 3 Models, selection | ModelCoder-OpusXHigh | opus | xhigh | parallel | selection code |
| 4 Sizing, simulator | PortfolioCoder-OpusXHigh | opus | xhigh | parallel | must match the frozen engine |
| 5 Canaries, dry run | CanaryCoder-OpusXHigh | opus | xhigh | after 2 to 4 | leakage proof |
| 6 Key fix, harness v7 | lead or KeyFix-OpusXHigh | opus | xhigh | any time | small frozen-file change |
| 7 Suite, probe | lead | opus | xhigh | after 5 | gates the review |
| 8 Design review | DesignReviewer-FableMax | fable | max | after 1 and 7 | the hinge of v2's honesty |
| 8 Code review | CodeReviewer-FableXHigh | fable | xhigh | after 7 | independent check of causality |
| 9 Rulings, commit | lead | opus | xhigh | last | reserved to the lead |

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

- The canaries prove causality, and each is shown to fail on a planted
  leak.
- The simulator's hand-computed day matches to the cent.
- Fable reviews the design (max) and the code (xhigh). The lead rules on
  every finding in writing.

============================================================
WHAT NOT TO DO
============================================================

- No market data, no Stage E result figures, no Databento call, no
  purchase, no training on real bars.
- No signal, model or parameter chosen from any result.
- No freeze of the v2 design. No edit to frozen design documents or
  member modules.
- No key printed. No push. No write to REGISTRATION.md.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.11_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 250 words: the design draft in brief, what was
   built, the test and canary results, the runtime estimate in overnight
   windows, the harness v7 sha256, and the user's decisions.
2. Guardrail evidence: the start and end checks verbatim.
3. Results per task: the design sections, the signal library (families
   covered and any excluded with reasons), the models and grids, the
   simulator check, the canaries, the runtime probe.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user (V2.12), each with a recommendation: deployment
   (frozen model or distilled rules), the compute host, the decision
   clock, the grid sizes, the success criteria, the purchase plan and the
   cap raise, and what the freeze session needs.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

Also write one short dated progress.md entry and one line in
docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
