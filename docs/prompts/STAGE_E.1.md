STAGE E.1 "FREEZE THE STAGE E DESIGN AND CATALOG, SWITCH THE DATABENTO ACCOUNT, BUY THE FIRST DATA, DRAFT THE ML ROUTE (NO PRICES READ)"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage E.0 (commit 01b259a) left a draft program design
(docs/STAGE_E_DESIGN.md, D1 to D15), draft null criteria
(docs/NULL_CRITERIA_E.md), a 61-member hypothesis catalog
(reports/stage_e0_catalog.md and .json, with the eight cluster files
reports/stage_e0_catalog_K1.md to K8.md), the research logs behind it, and
5,050 free quotes. The user reviewed it in the planning chat on 2026-09-24
and made the decisions listed in Task 1. This session does five things, in
this order: (1) applies exactly those decisions to the design and the
catalog, (2) has an independent Fable worker audit the result, (3) freezes
the design, the criteria and the catalog with a sha256 manifest and
commits the freeze, (4) switches the program to a second Databento account
and buys step 1 of the staged purchase (the research window of every
admissible contract, and the mbp-1 cost-calibration sample), and (5)
drafts the separate machine-learning route that replaces design section
D15. It stops there. No price is read, no bar is built, no member is run.
Stage E.2 builds the per-product harness (D11) and freezes the ML route
design after the user reviews it.

Lead: Opus 5.5, effort max. Ultracode: off.

Why this lead and effort: the core of this session is a pre-registration
freeze. Every later Stage E null or finding rests on the frozen files
saying exactly what the user decided and nothing more, and the ML route
draft is statistical design (data partition, trial accounting, leakage).
CLAUDE.md reserves opus max for pre-registration drafting and statistical
design. The coding (the account switch in the spend gate and a purchase
path) goes to an opus xhigh worker, because data/ code that spends money
sits in the xhigh row of the routing table. Ultracode stays off: the
session has three independent workstreams at most, and the fan-out must
go through the worker files so each worker's model and effort follow the
routing table.

Usage: the user's weekly allowance stood at 40% (all models) and 24%
(Fable) after E.0, which used 32 points of the week. This session is
lighter: no broad research, one literature reader for the ML route, one
coder, one Fable worker. Fable is used once, by one worker,
FreezeAuditor-FableXHigh: first to audit the freeze before it is committed
(Task 3), then resumed with SendMessage to recompute the spend after the
purchase (Task 8). No fable max hinge review is spawned. The freeze audit
is the hinge, and xhigh is judged enough for a diff-and-count audit, to
save the Fable allowance for the cluster verdicts. If Fable is unavailable
when Task 3 starts, stop before the freeze commit, finish Tasks 5 and 9,
and mark Tasks 3, 4, 6, 7 and 8 pending in the STATE file. The purchase
never runs before a Fable-audited freeze. Never substitute opus for the
Fable audit. Nothing heavy runs in this session, so the AiTrader collector
window does not constrain it.

Do not stop to ask. Decide, log the choice under Open choices in the
return document, and continue. The only stops are the ones this prompt
names, a decision that cannot be undone and could reasonably go either
way, or a guardrail conflict.

============================================================
SCOPE
============================================================

This stage does:
- apply the user's 2026-09-24 decisions (Task 1) to docs/STAGE_E_DESIGN.md,
  docs/NULL_CRITERIA_E.md and the catalog, and record them in
  docs/DECISIONS.md
- run the independent freeze audit and rule on it (Tasks 3 and 4)
- freeze and commit the Stage E pre-registration files (Task 4)
- switch the spend gate to the second Databento account and build a
  purchase path for step 1 (Task 5)
- quote, then buy step 1, then check the files (Tasks 6 and 7)
- recompute the spend independently (Task 8)
- draft the ML route design (Tasks 2 and 9)

This stage does NOT:
- read, chart, summarize or build bars from any purchased price or order
  book data. The files are checked for bytes, counts, dates and hashes
  only. Building bars, the cost calibration, the vehicle choice (D2) and
  every other D11 item belong to Stage E.2.
- buy anything outside step 1: no 2019-05..2025-03 history, no holdout-2
  chunk, no holdout-1 data, no tbbo sample, nothing for PL, MET, NKD or
  6M, nothing for ES or MES. Step 2 (each cluster's history, holdout-2
  sealed on arrival) is bought per cluster in later stages.
- change any member's rule, parameter, threshold or window beyond Task 1's
  list. A problem found in a member is logged for the user, not fixed.
- freeze the ML route design. It is a DRAFT for the user's review. E.2
  freezes it before any ML fit and before any research-window bar is
  read.
- train, fit or tune any model.
- touch holdout-1 or holdout-2, rules/, live/, ops/, sim/, screening/,
  funnel/, strategy/, or any TopstepX credential or API
- edit docs/NULL_CRITERIA.md or reports/stage_d1f_confirmation_list.md
  (the frozen MES record)
- write to REGISTRATION.md (it stays 0 bytes)
- push. The session makes exactly the commits Task 4 and Task 5 name, on
  main, and the planning chat pushes after its review.

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md: roles, routing (note the
   2026-09-24 rows: literature research runs on opus, and the WebSearch
   budget rule), worker files, worker naming, concurrency, artifacts,
   checkpoints, compute limits, the ETA tables and the Session cost
   section. This prompt does not repeat them. On any conflict CLAUDE.md
   wins, and the conflict is logged.
2. The Stage E.0 entry in progress.md, in full, especially "Decisions the
   user must make before Stage E.1".
3. docs/STAGE_E_DESIGN.md, in full. Sections this session edits: D1
   (lines 24 to 127 at 01b259a), D4, D12, D13, D14 and D15. It is a DRAFT
   until Task 4 freezes it.
4. docs/NULL_CRITERIA_E.md, in full (DRAFT until Task 4).
5. reports/stage_e0_catalog.md and .json, and the eight cluster files.
   reports/stage_e0_review.md and reports/stage_e0_review_rulings.md
   (R-01 to R-28).
6. reports/stage_e0_topstep_facts.md (the volatility caps, including PL at
   0 on the 50K), reports/stage_e0_liquidity.md,
   reports/stage_e0_quotes.md and .json (the step 1 request set and its
   quotes).
7. data/config.py, data/spend_gate.py, data/quote_universe.py,
   tests/test_quote_universe.py and data/pull_mes.py (the purchase path
   Task 5 generalizes: monthly chunks, oldest first, quote, gate, commit,
   download, byte check, settle).
8. docs/DECISIONS.md and docs/STAGES.md.

============================================================
GUARDRAILS
============================================================

CLAUDE.md invariants apply in full. This stage adds:

- The order is fixed: decisions applied (Task 1), audit (Task 3),
  rulings and freeze commit (Task 4), and only then the purchase (Task
  6). No billable request is issued before the freeze commit exists and
  its manifest verifies.
- Precondition set by the user before launch: the DATABENTO_API_KEY in
  this repo's .env now holds the second account's key. The user replaced
  it and keeps the old key outside the repo. Never print, log, hash into
  a report, or copy either key. If the key is missing, stop Tasks 6 to 8,
  record a named refusal, and finish the rest.
- Spend: the active account is acct-2 (new, $125.00 credit, nothing else
  draws on it). Caps for this session: the session cap is the fresh step
  1 quote plus 10% and never above $120.00, the request cap is $3.00, and
  the account cap for acct-2 is $125.00. Every request is quoted and
  ledgered first. If the fresh step 1 quote exceeds $104.77 by more than
  5%, stop Task 6 and report. Do not raise any cap.
- Dates: every step 1 request lies inside trade dates 2025-04-01 to
  2026-06-19, with the data end at 2026-06-21 00:00 UTC (holdout-1's first
  bar is 2026-06-21 22:00 UTC, design D4). The purchase path refuses any
  range that touches 2024-03-01 to 2025-03-31 (embargo and holdout-2) or
  any time at or after 2026-06-21 00:00 UTC, and a test proves it.
- Holdout status at start, after the purchase, and at end:
  `uv run python -m data.holdout status`. Holdout-1 and holdout-2 stay
  all_ok with unlocks_logged 0.
- Price blindness: the purchased files are opened only by the purchase
  path's byte check and by Task 7's integrity checks (record counts, first
  and last timestamps, symbols, sha256). No price, size, spread or volume
  value is printed, summarized or written anywhere.
- Every Python command runs with OPENBLAS_NUM_THREADS=1 at nice -n 10.
- REGISTRATION.md stays 0 bytes. No TopstepX reference of any kind.

Start and end checks, with their output quoted verbatim in the return
document: `git status --short`, `git log --oneline -3`, the holdout
status, `wc -c REGISTRATION.md`, `uv run pytest -q` (expected at start:
the E.0 result, 940 passed, 1 xfailed, exactly the 2 known D.1f calendar
test failures).

============================================================
TASK 0: STARTUP
============================================================

- Owner: lead.
- Inputs: the context files above.
- Output: reports/stage_e1_STATE.md, and the estimate ETA table printed in
  chat and written to the STATE file.
- Done when: the start checks are recorded, HEAD is 92f8f88 or a
  descendant with a clean tree, and the ETA table exists.
- Failure path: an unexpected test failure, a dirty tree, or a holdout
  status other than all_ok stops the session with a named refusal in the
  STATE file.

============================================================
TASK 1: APPLY THE USER'S DECISIONS (LEAD)
============================================================

- Owner: lead.
- Inputs: the user's decisions below (planning chat, 2026-09-24), the
  E.0 drafts.
- Output: the edited drafts, a new docs/DECISIONS.md entry dated
  2026-09-24 listing U1 to U9, and reports/stage_e1_changes.md: every
  edit as file, section or entry ID, old text, new text, and the decision
  that requires it.
- Done when: every decision below maps to at least one logged edit or to
  a logged "no edit needed", and no edit exists that maps to no decision.
- Failure path: a decision that conflicts with another frozen rule, or
  that cannot be applied without changing a member beyond this list, is
  logged as a question for the user and left unapplied. It is not
  resolved by judgment.

The user's decisions:

- U1. D1 as the rule gives it: NKD (ADV 7,969, coverage 0.621), 6M
  (coverage 0.903) and MET (coverage 0.947) are OUT. The user confirmed
  this after reading the reasons. They may serve only as signal legs,
  under D9's member-level coverage check, as D1 already says.
- U2. Platinum (PL) is OUT, by the user's decision. Topstep's volatility
  cap for PL on the 50K is 0 contracts (reports/stage_e0_topstep_facts.md),
  PL has no micro, so the bot cannot trade it. Remove PL as a traded
  exposure everywhere: D1's table and result line (30 traded exposures),
  D2 and D13's lists, K5's exposures, and every member's product list. A
  member whose only traded exposure was PL is excluded with this reason.
  The core-port trials on PL are removed. PL may not serve as a signal leg
  either, since nothing in the catalog needs it.
- U3. D12 cluster order: K2 first, then K4, K5, K3, K6, K7, then K1 only
  if the user decides it is needed after K7, and K8 last (its members
  read other clusters' products). K1's members stay in the frozen catalog
  so that a later K1 session is pre-registered.
- U4. D13 and D4, staged purchase: step 1 in E.1 is the research window of
  every admissible contract of the 30 traded exposures plus the mbp-1
  sample on the five fixed dates, with no tbbo. Step 2 is design option
  (b): each cluster's 2019-05..2025-03 history for its chosen vehicles is
  bought just before that cluster's confirmation session, with its
  holdout-2 chunks sealed on arrival. Fix D4's sentence "Holdout-2 ...
  bought in E.1" to match. The ML route's data needs (Task 9) are decided
  separately and may pull some step 2 purchases forward. Say so in D13.
- U5. Databento account: acct-2, $125.00 credit, used only by this repo.
  acct-1 (the old account, shared with the archived MLCryptoEngine, $91.59
  spent) is closed to new spend by this program. D13 records both.
- U6. D15 is superseded by a separate Stage E ML route (Task 9). The eight
  K#-ml-01 entries are marked "excluded: superseded by the Stage E ML
  route (user decision 2026-09-24)". Keep their text visible, as E.0's
  exclusions did. D15's text stays in the file under a SUPERSEDED banner
  with a pointer to docs/STAGE_E_ML_DESIGN.md. The ML route's purpose, set
  by the user: ML is a strategy-discovery tool. Its findings become plain
  rules that are pre-registered and tested like any other member. No
  model is deployed or makes live decisions.
- U7. M6E and M6A stay non-candidates for D2 until Topstep answers the
  user's support email (drafted 2026-09-24, not yet answered). Record in
  D9 and D2 that if Topstep clears them before a cluster's screening
  session, a vehicle amendment may be written before that session reads
  any research-window bar, and the amendment is logged in DECISIONS.md.
- U8. Accepted as drafted: D2 (the risk target, band and 1-lot cap), D3
  (min(translated, funnel-derived), with E.0's no-passing-cell rule), D4
  (holdout-1 not bought for new products, full-size bars as a price path
  only if the power check fails and the user agrees), D5 (the alpha split
  and the t >= 1.0 screen), D6 (the three ports), D7 (the "inconclusive by
  design" and "source-overlap" rules), D8 (mbp-1 only, five dates), D9,
  D10, D11, D14, and every member's parameters as E.0's rulings left them.
- U9. E.0's small text items (review R-28): the K5 header and
  K5-preauc-01 say 3 trials beside the ruling's 2. Fix them. Apply any
  other text item R-28 lists that changes no rule.

After the edits, recompute and write into the catalog summary and D5:
active members per cluster, confirmation trials per cluster, the total,
and the projected cumulative N (58 plus the new total). The E.0 figures
were 61 members, 170 trials, N = 228. The lead expects a lower count
after U2 and U6, and writes the arithmetic out.

Mark docs/STAGE_E_DESIGN.md and docs/NULL_CRITERIA_E.md with a header line
that reads "FROZEN by Stage E.1 on <date>, manifest
reports/stage_e1_freeze.json" only in Task 4, after the audit.

============================================================
TASK 2: ML ROUTE LITERATURE (WORKER)
============================================================

- Owner: MLLitReader-OpusHigh, worker-high on opus. Starts at Task 0,
  parallel with Tasks 1, 3 and 5.
- Inputs: the questions below, the retrieval and citation rules of Stage
  D.1 Task 1 (docs/prompts/STAGE_D.1.md), and CLAUDE.md's web research
  budget rule.
- Output: reports/stage_e1_ml_research.md: every source considered (one
  line for rejects), and for each source read in full, the claim, the
  quoted passage, the market, the horizon, the data size, the cost
  treatment and the source-quality notes. Unverifiable claims are marked
  [unverified].
- Done when: every question below has either sourced answers or a logged
  "no source found", after at least 4 logged queries per question, or 30
  full-text reads in total, whichever comes first.
- Failure path: a WebSearch budget notice or a blocked source is logged
  with the time. The worker stops searching and never continues from
  memory.

Questions:
1. Which model families have shown out-of-sample, net-of-cost
   predictability in liquid futures at horizons from 15 minutes to one
   trading day (gradient-boosted trees, temporal convolutional networks,
   LSTMs, transformers, others), with what data sizes? Where does the
   evidence say deep networks beat trees at these horizons, and where
   not? Known anchor: order-book deep learning (for example DeepLOB, Zhang,
   Zohren and Roberts) finds its predictability at horizons of seconds,
   which Topstep's rules exclude. Log what it says about longer horizons.
2. Pooled cross-asset models: training one model across many futures
   with per-asset normalization (for example the momentum and
   trend-following deep learning work from the Oxford-Man Institute).
   What pooling adds in effective sample size, and how its authors handle
   correlation between assets.
3. Leakage and validation for financial ML: purged and embargoed
   cross-validation, combinatorial purged CV, and how many
   configurations a search can try before a backtest result is
   uninterpretable (deflated Sharpe, PBO under model search).
4. Turning a fitted model into plain rules: rule extraction, surrogate
   trees, SHAP interactions, partial dependence. What survives
   distillation and how authors test the distilled rule out of sample.

============================================================
TASK 3: INDEPENDENT FREEZE AUDIT (FABLE XHIGH)
============================================================

- Owner: FreezeAuditor-FableXHigh, worker-xhigh on fable. It wrote none of
  the work it audits.
- Inputs: the edited drafts, reports/stage_e1_changes.md, the user's
  decisions U1 to U9 as quoted in this prompt, and `git diff 01b259a`
  on the design, the criteria and the catalog files.
- Output: reports/stage_e1_freeze_audit.md, each finding graded BLOCKING,
  SHOULD FIX or NOTE, with file and line.
- Done when: the auditor has checked all of the following:
  - every change in the diff maps to one of U1 to U9 and every decision is
    applied (no silent edit, no missed decision)
  - PL is gone as a traded exposure everywhere, and nothing still depends
    on it
  - the eight ML entries are excluded with the stated reason, and D15
    carries its banner
  - the recount of members, trials and projected N is right, recomputed
    independently from the catalog JSON
  - D4, D12 and D13 now agree with each other on the staged purchase and
    the order
  - no member rule, parameter, threshold or window changed except where a
    decision requires it
- Failure path: if Fable is unavailable, stop before Task 4 as the Usage
  paragraph says.

============================================================
TASK 4: RULINGS, FREEZE AND COMMIT (LEAD)
============================================================

- Owner: lead.
- Inputs: the audit.
- Output: reports/stage_e1_freeze_rulings.md, the FROZEN header lines,
  reports/stage_e1_freeze.json, and one commit.
- Done when:
  - every BLOCKING and SHOULD FIX finding has a written ruling and its fix
    applied. A BLOCKING finding that cannot be fixed within U1 to U9 stops
    the freeze, the purchase does not run, and the finding goes to the
    user.
  - reports/stage_e1_freeze.json lists the sha256 of every frozen file:
    docs/STAGE_E_DESIGN.md, docs/NULL_CRITERIA_E.md,
    reports/stage_e0_catalog.md, reports/stage_e0_catalog.json,
    reports/stage_e0_catalog_K1.md to K8.md, reports/stage_e0_research_K1.md
    to K8.md, reports/stage_e0_source_registry.jsonl,
    reports/stage_e0_partition.md, reports/stage_e0_topstep_facts.md and
    .json, reports/stage_e0_liquidity.md and .json,
    reports/stage_e0_quotes.json, reports/stage_e0_review.md,
    reports/stage_e0_review_rulings.md, reports/stage_e1_changes.md,
    reports/stage_e1_freeze_audit.md and reports/stage_e1_freeze_rulings.md,
    plus the manifest's own creation time and HEAD.
  - a script check (inline) recomputes every sha256 in the manifest and
    matches, and the check confirms no file under data/vendor/ for any
    Stage E product exists at freeze time
  - one commit on main holds exactly the frozen files, the manifest,
    docs/DECISIONS.md and docs/STAGES.md, with a message that names the
    manifest sha256 and says "Stage E pre-registration freeze". It ends
    with this repository's attribution lines.
- Failure path: a sha256 mismatch or a stray product data file stops the
  session before Task 6.

============================================================
TASK 5: ACCOUNT SWITCH AND PURCHASE PATH (WORKER)
============================================================

- Owner: PurchaseCoder-OpusXHigh, worker-xhigh on opus. Starts at Task 0,
  parallel with Tasks 1 to 3. It touches no frozen file.
- Inputs: data/config.py, data/spend_gate.py, data/pull_mes.py,
  data/quote_universe.py and its tests, reports/stage_e0_quotes.json (the
  request set), design D1 (admissible vehicles) as amended by U2.
- Output:
  - Per-account spend in the gate. data/config.py gains the account
    registry: acct-1 with cap $120.00 and the external MLCryptoEngine
    ledger (as today), acct-2 with cap $125.00 and no external ledger, and
    an active account, acct-2. Every new ledger line carries an `account`
    field. Lines without one are acct-1 (legacy). The gate sums spend per
    account, applies the active account's cap, and fails closed on an
    unknown account. The external ledger is required only when acct-1 is
    active. The E.1 session constants: STAGE_E1_SESSION_ID
    "stage-E.1-2026-09-24", the request cap $3.00, and the session cap
    set by the lead in Task 6 from the fresh quote.
  - data/pull_universe.py, the step 1 purchase path, generalized from
    pull_mes.py: ohlcv-1m monthly chunks of the research window for every
    admissible contract, oldest first, and mbp-1 for the five fixed dates
    (2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11, 2026-04-15) for every
    admissible contract. Each request is quoted, authorized, committed,
    downloaded, byte-checked against the quote, and settled, as in
    pull_mes.py. A --quote-only mode issues no billable request. The path
    is resumable: a chunk already on disk with a settled ledger line is
    skipped.
  - tests (tests/test_pull_universe.py and additions to the gate's tests)
    proving each of these:
    - per-account totals are right with legacy lines present
    - the acct-2 cap refuses past $125.00
    - the session and request caps refuse
    - any range touching 2024-03-01..2025-03-31, or at or after
      2026-06-21 00:00 UTC, is refused before any vendor call
    - PL, MET, NKD, 6M, ES and MES are refused as step 1 symbols
    - --quote-only makes no billable call
    - resume skips settled chunks
- Done when: the full suite passes with only the 2 known failures, and
  the new tests' names and what each proves are listed in the return
  document. One commit on main, made after Task 4's freeze commit, holds
  exactly the code and test files, with this repository's attribution
  lines.
- Failure path: if the per-account change cannot keep every existing gate
  test passing unchanged, the worker stops and reports. The lead does not
  weaken a test to pass it.

============================================================
TASK 6: QUOTE AND BUY STEP 1 (LEAD)
============================================================

- Owner: lead, running the Task 5 path.
- Inputs: the freeze commit, the Task 5 commit, the .env key.
- Output: ledger lines under stage-E.1-2026-09-24 with account acct-2,
  and the purchased files under data/vendor/databento/.
- Done when:
  1. `--quote-only` runs, and its total is compared with E.0's step 1
     figures ($58.42 research window, $46.35 mbp-1, before U2 removed PL).
     The lead writes the session cap (quote plus 10%, at most $120.00)
     into data/config.py before any purchase, and records it.
  2. The purchase runs to completion, or to a named stop.
  3. The holdout status after the purchase shows both holdouts all_ok, 0
     unlocks.
- Failure path: a quote above the limit in GUARDRAILS, a gate refusal, an
  authentication error, or a byte-check failure stops the purchase at
  that request. The lead records the state and does not retry with a
  changed cap. A partial purchase is resumable in a later session.

============================================================
TASK 7: INTEGRITY CHECKS (LEAD, INLINE)
============================================================

- Owner: lead (small, inline).
- Inputs: the purchased files and the ledger.
- Output: reports/stage_e1_purchase.md and .json: per file, the product,
  the schema, the date range, the record count, the first and last
  timestamps (UTC), and the sha256. Per product and in total, the quoted
  and settled cost.
- Done when: every request in the step 1 set has a file and a settled
  ledger line, or a named gap, and no file carries a timestamp outside the
  allowed range.
- Failure path: a file outside the allowed dates is quarantined unread in
  data/vendor/quarantine/, logged, and reported as a BLOCKING item for the
  user. It is never deleted without the user's decision.

============================================================
TASK 8: SPEND RECOMPUTATION (FABLE XHIGH, RESUMED)
============================================================

- Owner: FreezeAuditor-FableXHigh, resumed with SendMessage.
- Inputs: ledger/databento_spend.jsonl, reports/stage_e1_purchase.json,
  data/config.py.
- Output: a second section in reports/stage_e1_freeze_audit.md: the
  session total, the acct-2 total, and the acct-1 total recomputed from
  the ledger lines alone, with every cap checked. It also confirms that
  no ledger line was rewritten (append-only) and that every file in the
  purchase report matches a settled line.
- Done when: every figure agrees with the purchase report, or each
  disagreement is listed.
- Failure path: a disagreement goes to the return document as unresolved.
  It is not reconciled by editing the ledger.

============================================================
TASK 9: THE ML ROUTE DESIGN DRAFT (LEAD)
============================================================

- Owner: lead.
- Inputs: reports/stage_e1_ml_research.md, the frozen design (for its
  windows, costs, Topstep constraints and trial accounting), and the
  user's aims: find a viable strategy, with the method open, ML as the
  discovery tool, and plain rules as the deployed output.
- Output: docs/STAGE_E_ML_DESIGN.md, marked DRAFT at the top, answering
  each item below with a proposed rule, the reasoning, the alternatives
  and what the user decides.
- Done when: every item below is answered, and the draft states what E.2
  must build for it and the data it needs, with quoted costs from the
  E.0 quotes where the data is not yet bought.
- Failure path: an item the literature cannot support is answered with
  the plain statement that no source supports it, and a conservative
  default.

Items:
- M1 Data partition. The planning chat's proposal to evaluate: train and
  tune only on the older history (from each product's start date through
  2024-02-29), with March 2024 and holdout-2 never used. Test the frozen
  models and their distilled rules once on the research window
  (2025-04-01..2026-06-19), which the ML route never trains on. Keep
  holdout-2 sealed as the final gate for any strategy from any route.
  The hand-written catalog is frozen in Task 4, before any ML training,
  so ML results cannot leak into it, and ML-derived rules are never
  confirmed on data the models trained on. Also state what this implies:
  the ML route needs the older history of the products it uses, which
  pulls step 2 purchases forward. Give the cost from the E.0 quotes.
- M2 Pooling. One model across the traded exposures with per-product
  normalization, against per-cluster models. Effective sample size, and
  the handling of correlation between products.
- M3 The challenger list, fixed in advance: a gradient-boosted tree
  baseline and at most two small deep networks on normalized bar
  sequences (for example a temporal convolutional network and an LSTM),
  each with a tuning grid listed in full. Justify each by Task 2's
  evidence, or drop it.
- M4 Features and targets: which inputs, their availability timestamps,
  the horizons (15 minutes to the XFA flatten), net of the D8 cost model,
  inside D9's trade-rate floor and the 1-lot cap.
- M5 Distillation: how a fitted model becomes 1 to 3 plain rules per
  cluster or per exposure, written in the catalog's entry format, frozen
  before the research-window test. How many rules the route may produce
  in total.
- M6 Trial accounting: each distilled rule is one trial at its test. The
  full model search is reported beside it and counted in the route's own
  training-window accounting. How the route's trials join the program's
  cumulative N and the per-cluster Holm families.
- M7 Leakage controls: carry over D15.7's validator, perturbation, fold
  and window tests, adapted to the new partition. Add a check that no
  research-window bar enters any training, tuning or normalization step.
- M8 Compute: where training runs (the ThinkPad CPU, or the Windows PC
  with the RTX 2060 Super 8 GB), the time per challenger, and CLAUDE.md's
  limits (half the cores, one heavy job, nice 10, resumable, memory
  checked first).
- M9 The session plan for the route, and where it sits in the cluster
  order.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, ETA, STATE | lead | opus | max | serial, first | gates the session |
| 1 Apply decisions | lead | opus | max | parallel with 2 and 5 | pre-registration content, reserved to the lead |
| 2 ML literature | MLLitReader-OpusHigh | opus | high | parallel with 1, 3 and 5 | literature research runs on opus (CLAUDE.md, 2026-09-24) |
| 3 Freeze audit | FreezeAuditor-FableXHigh | fable | xhigh | after 1 | an independent model on a declaration |
| 4 Rulings, freeze, commit | lead | opus | max | after 3 | reserved to the lead |
| 5 Account switch, purchase path, tests | PurchaseCoder-OpusXHigh | opus | xhigh | parallel with 1 to 3, commit after 4 | data/ code that spends money |
| 6 Quote and buy | lead runs the path | opus | max | after 4 and 5 | irreversible spend, the lead watches it |
| 7 Integrity checks | lead, inline | opus | max | after 6 | small, under 15 minutes |
| 8 Spend recomputation | FreezeAuditor-FableXHigh, resumed | fable | xhigh | after 7 | every spend figure gets an independent check |
| 9 ML route draft | lead | opus | max | after 2, any time after 4 | statistical design |
| Return document | lead | opus | max | last | reserved to the lead |

At most 3 workers exist in this session and at most 3 run at once.

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

- The freeze (Task 3) and the spend (Task 8) are checked by
  FreezeAuditor-FableXHigh, which produced neither.
- The lead rules on every finding in writing, applies the fixes, and
  never re-runs the audit to get a different answer.
- If Fable runs out, the checks stay pending in the STATE file, and the
  purchase does not run without the Task 3 audit.

============================================================
WHAT NOT TO DO
============================================================

- No billable request before the freeze commit.
- No price, size, spread or volume value read, printed or summarized.
- No purchase outside step 1. Nothing for PL, MET, NKD, 6M, ES or MES.
- No cap raised, no key printed.
- No member changed beyond U1 to U9.
- No ML fit, and no freeze of the ML route draft.
- No push, and no commit beyond the two named.
- No write to REGISTRATION.md. No edit to docs/NULL_CRITERIA.md.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.1_RETURN.md. The planning chat reads this one file to
review the session. Fixed sections, in order:

1. Verdict summary, at most 200 words: what was done and what was not,
   the manifest sha256, members, trials and projected N after the
   decisions, the step 1 spend, and whether E.2 is unblocked.
2. Guardrail evidence: the start and end checks verbatim, the holdout
   status after the purchase, the price-blindness attestation (which
   scripts opened purchased files, and what they read), `git status
   --short` and `git diff --stat` at the end, and both commit hashes.
3. Results per task: the decisions applied (with a pointer to
   reports/stage_e1_changes.md), the recount, the freeze, the account
   switch and its tests (each test's name and what it proves), the quote
   and purchase figures per cluster, the integrity checks, the ML
   literature summary, and the ML route draft's proposals M1 to M9 in
   short form.
4. Delegation record: one row per spawn with agent name, worker file,
   model, effort, objective, status, and deviations from the plan.
5. Verification: each finding of the audit and the spend recomputation,
   the lead's ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason,
   so the user can overturn any of them before E.2.
7. What the next session must do first: pushes the planning chat owes, the
   frozen files and the manifest sha256, the decisions the user owes on
   the ML route draft, the Topstep answer on M6E and M6A, and any
   blocker.
8. Session cost: the final ETA table (one row per task and per spawn,
   actual start and end, time taken, tokens from the transcripts, status)
   and the per-model token table, per CLAUDE.md. Never estimated.

Also write one short dated progress.md entry that points to the return
document, and one line in docs/STAGES.md.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
