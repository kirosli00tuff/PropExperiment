STAGE E.22 "LOOSE ENDS AND THE MICRO BOOK: CONFIRM THE FIVE UNCONFIRMED TIER A MEMBERS AS FROZEN, AND DESIGN THE SMALL-ACCOUNT MICRO TREND BOOK AND ITS FORWARD RECORD"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Two independent parts, run in parallel, in a session that must
end by 08:00 PDT (V39).
- Part A closes loose ends. Five cluster members passed their screens in
  E.4b to E.9 (Tier A) and were never confirmed, because the program
  moved to the ML route: K5-fomc-01 (MGC), K3-ldnrev-01 (6E),
  K6-limitcont-01 (HE), K8-flight-01 HEOD (MGC with MES) and K8-wkndbtc-01
  (MNQ with MBT). Each is confirmed once, exactly as its cluster freeze
  defines it, on its confirmation window (S_X..2024-02-29) under
  docs/STAGE_E_DESIGN.md D4 and D5, as E.5 did for K4, using owned data
  only. Nothing is changed in any member.
- Part B designs the personal-account engine: the multi-day micro trend
  book (E.21's T1 and T2 were real but underpowered; the planning research
  found integer rounding and breadth are what matter at $10K-$50K). It is
  a design and feasibility study, not an edge test: the rounding loss
  against an unrounded book, the capital each size needs, the expected
  drawdowns, the universe per capital level, and a frozen forward-test
  registration with a paper runner, so that new independent evidence can
  start to accrue. No purchase, no Databento call, no data fetch without
  the user's approval.

Decisions in force: docs/DECISIONS.md V20 to V39. Binding for Part A:
each member's cluster freeze and docs/STAGE_E_DESIGN.md D4, D5, D9, D13,
with E.5's confirmation procedure (reports/E.5_RETURN.md) as the worked
precedent. Binding for Part B: this prompt and V37.

Lead: Opus 5.5, effort xhigh. Ultracode: on (launched interactively).

Why this lead and effort: Part A applies frozen definitions to data with
silent-failure risk in window starts, price-path substitution, cross-
product leg alignment and the composite verdict; Part B builds sizing code
whose integer arithmetic is easy to get subtly wrong. Fable reviews Part
A's confirmation list before any confirmation read and recomputes every
Part A verdict number; Fable reviews Part B's forward registration before
it is frozen.

Usage and time: the user cleared the window from about 00:50 to 08:00
PDT. reports/stage_e22_STATE.md is updated after every step. No
confirmation read starts after 06:30 PDT; by 07:30 PDT the return is
written with each part's status, finished or not. Parts A and B run in
parallel (V37).

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue.

============================================================
PART A: THE FIVE TIER A CONFIRMATIONS (FIXED HERE)
============================================================

A1. Members, unchanged: K5-fomc-01 (MGC; the K5 Tier A list also covers
any other K5 Tier A trial its freeze lists), K3-ldnrev-01 (6E),
K6-limitcont-01 (HE), K8-flight-01 HEOD (MGC with MES), K8-wkndbtc-01
(MNQ with MBT). The lead confirms the list against the cluster freezes and
the E.4b, E.4c, E.8 and E.9 returns before anything else; any member
whose Tier A status differs from this list is logged and handled as the
freeze says.

A2. Windows and price paths. Confirmation window S_X..2024-02-29 with the
start rule of D4; March 2024 embargo and holdout-2 never read. Where a
micro's own history is too short (MGC, MBT), D4 and U8 allow the
full-size bars as the price path (GC for MGC; BTC for MBT) only if the
power check fails and the user agrees: the user delegated tonight's
choices to the planner (V39), and the planner's ruling is that the
substitution is allowed where D4's power check fails, declared per member
in the confirmation list BEFORE any confirmation read, exactly as U8
describes. Owned stores only (data/processed_step2/ for GC, 6E, HE, NQ,
MBT and the others; MES's pre-holdout history from its Stage D store);
a member whose required leg is not owned for its window is labelled
"untestable on owned data" with the missing leg named, not bought.

A3. Power check before any read (D4): a member whose n_b exceeds its
window is labelled "inconclusive by design", never tested for a null it
cannot reach.

A4. Verdicts per D5: Holm within each cluster's Tier A at alpha_k = 0.05
/ K, with K = the number of clusters with a non-empty Tier A in the
program (state the count and its source); then, for any Holm rejection,
the composite verdict (robust zero-edge gate, both drift sub-checks), DSR
> 0.95 at the program N, daily t > 3.0 one-sided, CSCV PBO < 0.5. N is
unchanged by confirmations of already-counted members unless E.5's
precedent says otherwise (follow E.5 and state it).

A5. Order: confirmation list written and hashed, ListReviewer-FableXHigh
review (BLOCKING and SHOULD FIX fixed first), list commit, then each
member confirmed once behind a run-once marker, then
VerdictVerifier-FableXHigh recomputation. A BLOCKING finding on a verdict
is resolved by finding the code error, never by a second run.

============================================================
PART B: THE MICRO TREND BOOK (DESIGN, NOT AN EDGE TEST)
============================================================

B1. The rule, from the planning research (Carver's published method):
EWMAC forecasts at speeds 8/32, 16/64, 32/128, 64/256 on each instrument's
daily settlement series, each scaled to an average absolute value of 10
and capped at +/-20, equally weighted and rescaled with Carver's forecast
diversification multiplier; positions sized for a 20% annual portfolio
volatility target with Carver's instrument diversification multiplier,
from his published formulas (cite the source of each constant).

B2. The universe per capital level ($10K, $25K, $50K): CME micros
(MES or MNQ, M2K, MGC, SIL, MHG, MCL, MNG or QG, M6E, M6A, M6B, MCD, MJY,
micro yields 2YY, 10Y, 30Y, micro grains MZC, MZS, MZW, MZL, MZM), each
mapped to an owned price path; instruments with no owned price path are
listed as "not modelled". Rounding by (a) simple rounding and (b) Carver's
greedy minimum-tracking-error dynamic optimisation (November 2021
version), both implemented from his published description.

B3. Outputs, all descriptive (no p-values, no verdict, nothing added to
N): per capital level and rounding method, the correlation of daily P&L
with the unrounded book, the Sharpe loss against unrounded, turnover and
costs at D8, expected and worst drawdowns, the share of instruments held
at zero, and margin at IBKR's published rates where sourced. Data:
2010-07..2024-02 owned stores; never anything from 2024-03-01 on. The
return states plainly that these figures re-use data E.21 already read
and are not evidence of edge.

B4. Forward registration (E22-F1). A frozen pre-registration of the micro
book at the $25K level: the rule, the universe, the rounding method, the
start date (the first trade date after the user approves a daily data
source), the evaluation horizon (36 months), and the bar (one-sided p <=
0.05 on the forward daily net series, net Sharpe >= 0.3), with an interim
descriptive look every 6 months that changes nothing. Registered now (N
532 -> 533); the clock starts only when data flows.

B5. Paper runner: a small package forward/ that, given each day's
settlement prices from a pluggable source, computes forecasts, target
positions and paper fills at the next settlement with D8 costs, rolls by
the micro's published roll schedule, and appends to a ledger. Tests on
synthetic data. A data-source memo lists the options for daily
settlements (Databento ohlcv-1d with a fresh quote, broker paper
accounts, other licensed sources), each with cost and terms; no source is
fetched by automation tonight, CME's site is never fetched by automation,
and nothing is bought.

============================================================
SCOPE
============================================================

This stage does Part A and Part B, in parallel, and nothing else.

This stage does NOT:
- buy anything, call Databento, or fetch any market data from the web
- change any frozen member, rule, harness file or freeze
- read holdout-2, the March 2024 embargo, MES's sealed stores, the
  research window for Part B, or anything dated 2024-03-01 or later
- run any confirmation twice, or start one after 06:30 PDT
- fit any ML model
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V24 to V39.
3. docs/STAGE_E_DESIGN.md D2, D4, D5, D9, D12, D13 (Part A).
4. reports/E.5_RETURN.md in full (the confirmation precedent); the
   E.4b, E.4c, E.8 and E.9 returns and their cluster freezes (Part A).
5. reports/E.21_RETURN.md and reports/stage_e13_trend_carry.md (Part B).
6. The planning research for Part B, summarized in V39.

============================================================
GUARDRAILS
============================================================

- Harness v12 ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32
  verified at start and end; any harness change needed for Part A is a
  new harness version written, Fable-reviewed and committed before any
  confirmation read, as E.5 did (v5, v6).
- Holdout status all_ok, 0 unlocks, at start and end; spend ledger
  unchanged.
- Start and end checks quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the freeze verifications, the ledger line count and
  sha256, N, and `uv run pytest -q -p no:cacheprovider`.
- Compute at nice 10 after a free-memory check; at most 2 heavy workers.
- Before ending, confirm no worker or background shell is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| A list | lead | opus | xhigh | parallel with B | frozen definitions, windows, power checks |
| A list review | ListReviewer-FableXHigh | fable | xhigh | after the list | independent check before any read |
| A confirm | lead | opus | xhigh | after the review | verdicts reserved to the lead |
| A verify | VerdictVerifier-FableXHigh | fable | xhigh | after the confirmations | verdict numbers recomputed |
| B build | MicroBookCoder-OpusXHigh | opus | xhigh | parallel with A | sizing, rounding, optimiser, runner, tests |
| B registration review | RegReviewer-FableXHigh | fable | xhigh | after the B4 text | independent check before freezing |
| Return | lead | opus | xhigh | last | reserved to the lead |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. Run independent workers at once (V37); heavy compute at most 2.
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

Write reports/E.22_RETURN.md, one progress.md entry, one docs/STAGES.md
line, and one final commit "Stage E.22 Tier A confirmations and micro
book". No push. Fixed sections:

1. Summary, at most 300 words: each Tier A member's verdict (CONFIRMED,
   NULL, INCONCLUSIVE BY DESIGN or UNTESTABLE ON OWNED DATA, with the
   rule) and its decisive numbers; the micro book's headline figures per
   capital level; E22-F1's registration and N; what the user must decide
   (the daily data source).
2. Guardrail evidence: start and end checks verbatim; the order of events.
3. Results: Part A's list, power checks and verdicts; Part B's tables and
   the data-source memo.
4. Delegation record.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
