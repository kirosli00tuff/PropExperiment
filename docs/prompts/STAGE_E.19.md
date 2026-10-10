STAGE E.19 "PROP ECONOMICS: WHAT THE TOPSTEP COMBINE-TO-XFA FUNNEL IS WORTH TO THE USER IN CASH, AT ZERO EDGE AND AT SMALL EDGES, BEFORE ANY COMBINE IS BOUGHT"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: After 480 registered trials nothing has passed, and C1b closed
the NG near-miss (E.18). The user cannot fund a personal IBKR account
yet and wants to build that capital from Topstep XFA payouts (V32). The
question this stage answers is purely economic, not an edge claim: what
is the user's expected net cash, and its distribution, from buying
Topstep Combines and trading the funded accounts that follow, for a
trader with zero edge and with small edges, under Topstep's real current
rules and fees, with realistic trading costs and fat-tailed daily
returns? The user's money at risk is only fees; the drawdown is
Topstep's. Whether that structure gives a positive or negative expected
value depends on the exact rules, which this stage sources and models.
No market-data purchase, no edge test, no change to N.

Decisions in force: docs/DECISIONS.md V22, V31, V32. The Live Funded
API prohibition (F12) and the five-XFA cap apply.

Lead: Opus 5.5, effort xhigh. Ultracode: off.

Why this lead and effort: the answer depends on many small rules (fees,
targets, consistency, payout caps, splits, scaling, resets, the trailing
drawdown's lock), each easy to get wrong, and on modelling choices that
can flatter the result. The silent failures to guard against: a rule
taken from a marketing page instead of the help centre or terms, a rule
missed, thin-tailed returns, a sizing policy tuned to the simulation's
own noise, and a strategy that would break Topstep's terms. Fable
reviews the rule table and the model, and recomputes the headline
numbers.

Usage: follows CLAUDE.md's context-hygiene rules. The user may be away.
reports/stage_e19_STATE.md is updated after every task. Expect 4 to 6
hours.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the
choice under Open choices in the return document, and continue.

============================================================
SCOPE
============================================================

This stage does:
- source Topstep's current rules and fees for the 50K, 100K and 150K
  Combine and XFA, and its terms on prohibited trading practices
  (Task 1)
- build a funnel simulator: Combine attempts (fees, resets, pass or
  fail), activation, the XFA (trailing drawdown and its lock, the daily
  loss limit if any, scaling plan, winning-day rules, payout paths,
  caps, split, payout effect on the balance and drawdown), Live Funded
  call-up treated as the end of automated trading, the five-account cap
  (Task 2)
- feed it daily P&L from: (a) zero edge, (b) annual net Sharpe 0.3, 0.5,
  1.0, each with realistic fat tails and costs (Task 3)
- report expected net cash per attempt and per funded account, the
  distribution, the chance of losing all fees, the break-even edge, the
  sizing that maximizes expected cash per rule set (with its
  sensitivity), and how many attempts reach $5K and $10K of withdrawn
  cash (Task 4)
- Fable review and recomputation (Task 5)

This stage does NOT:
- buy any data, call Databento, or read holdout-2, the research window
  or MES's sealed stores
- test any edge, register anything, or change N
- recommend any practice Topstep's terms prohibit (hedging across
  accounts, copying trades between accounts where banned, exploiting
  simulator fills, news or HFT rules, any "gaming the evaluation"
  clause); every modelled strategy is checked against the terms
- contact Topstep, open any account, or touch any TopstepX credential,
  the ProjectX API, live/ or ops/
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md (the page-fetch order and terms rule) and docs/ORCHESTRATION.md.
2. docs/DECISIONS.md V20 to V32.
3. reports/stage_e0_topstep_facts.json and .md, reports/stage_e12_topstep_150k.md,
   rules/xfa_rules.py.
4. ml_route_v2/payout_sim.py and its tests (the keep-D policy, the
   Standard and Consistency paths), ml_route_v2/sizing.py.
5. docs/STAGE_E_ML_V2_DESIGN.md V2.0 and V2.8-V2.9 (the economics and
   ruin arithmetic).
6. reports/stage_e2a_costs.md (D8 costs) and the cost wall from E.10.

============================================================
TASKS
============================================================

TASK 0: STARTUP (lead). Start checks (git state, holdout status,
REGISTRATION.md, harness v12 verify
ece91ae8e6993ad3c64412d30cc0b6ff6a4af07a15a6956ce9f2927f7ea70d32, N =
480, ledger unchanged); STATE; ETA table.

TASK 1: RULES AND TERMS (TopstepRules-OpusHigh, worker-high on opus).
From Topstep's help centre and terms pages (public; read the site's
terms before any automated fetch; quote each rule with URL and fetch
date): for 50K, 100K and 150K, the Combine price and billing (monthly?),
reset price, profit target, maximum loss limit and its trailing rule,
daily loss limit (if any), consistency rule in the Combine, minimum
days, activation fee and options, the XFA's trailing drawdown and when it
locks, scaling plan, winning-day definition, Standard and Consistency
payout paths, payout caps, profit split, any payout count limits, what
a payout does to the balance and the drawdown, inactivity rules,
Back2Funded or reset options, the Live Funded call-up rule, and the
maximum number of XFAs. Separately, quote every prohibited or
restricted trading practice in the terms. Output
reports/stage_e19_rules.md and .json; a rule with no source is marked
UNSOURCED and the simulator runs both plausible readings.

TASK 2: SIMULATOR (FunnelCoder-OpusXHigh, worker-xhigh on opus). Extend
or wrap ml_route_v2/payout_sim.py into prop_econ/: the full funnel from
the user's wallet's point of view (cash out = fees; cash in = payouts
after the split). Deterministic by seed. Tests that pin hand-computed
paths (a pass then a payout; a fail and reset; a drawdown lock; a
payout under each path; the five-account cap). Rules come only from
Task 1's JSON.

TASK 3: RETURN MODELS (lead, with the coder). Daily P&L per contract
unit:
- Fat tails: bootstrap demeaned daily returns (blocks of 5 days) from
  the owned E.12 training stores (2019-05..2024-02) of the price paths
  NQ, CL, GC, ZN and 6E, scaled to the vehicle actually traded (micro
  where the risk budget needs it), demeaned so the zero-edge case has
  exactly zero drift before costs. This reads return magnitudes only,
  never a signal, and is not an edge test. No research-window,
  holdout or 2010-2019 bar is read.
- Costs: D8 round trip per trade for the vehicle, at an explicit trades
  per day (1 and 3).
- Edges: add a constant drift giving annual net Sharpe 0.3, 0.5 and 1.0
  after costs.
- Sizing: a grid of daily risk as a fraction of the drawdown distance
  (for example 0.05, 0.10, 0.15, 0.25 x D), within lot limits and the
  scaling plan. Report every grid point, not only the best; the best is
  labelled "in-simulation optimum" with its standard error.

TASK 4: RESULTS (lead). For each account size, payout path, return model
and sizing: expected net cash per Combine purchase and per funded XFA,
the 5th / 50th / 95th percentiles, the probability of losing all fees
paid, the break-even annual Sharpe, expected time to the first payout,
and the number of Combine purchases (and total fees) to reach $5K and
$10K of withdrawn cash with 50% and 80% probability, with five XFAs at
most. Include a sensitivity table for the UNSOURCED rules and for the
tail model (bootstrap versus normal). Write reports/stage_e19_results.md
and .json.

TASK 5: REVIEW (EconReviewer-FableXHigh, worker-xhigh on fable). Checks
the rule table against its quotes, the simulator against hand paths and
the rules, the zero-drift demeaning, the costs, and recomputes the
headline numbers (zero edge and Sharpe 0.5, each account size, the
best sizing) independently. Findings graded BLOCKING, SHOULD FIX or NOTE
in reports/stage_e19_review.md; rulings in reports/stage_e19_rulings.md.

TASK 6: RETURN AND COMMIT (lead). reports/E.19_RETURN.md, one dated
progress.md entry, one docs/STAGES.md line, one commit "Stage E.19 prop
economics". No push.

============================================================
DELEGATION PLAN
============================================================

| Task | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup | lead | opus | xhigh | first | gates the session |
| 1 Rules and terms | TopstepRules-OpusHigh | opus | high | parallel with 2 | sourced facts with terms check |
| 2 Simulator | FunnelCoder-OpusXHigh | opus | xhigh | parallel with 1 | rules engine with hand-pinned tests |
| 3, 4 Models, results | lead | opus | xhigh | after 1 and 2 | modelling judgment reserved to the lead |
| 5 Review | EconReviewer-FableXHigh | fable | xhigh | after 4 | independent recomputation |
| 6 Return | lead | opus | xhigh | last | reserved to the lead |

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

Before ending, confirm no worker or background shell is still running.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.19_RETURN.md. Fixed sections, in order:

1. Verdict summary, at most 300 words: is the funnel positive expected
   value for the user at zero edge (yes, no, or depends, with the rules
   it depends on); the break-even edge; the best account size and payout
   path; the expected fees and attempts to reach $5K and $10K; the risk
   of losing all fees; and the terms constraints.
2. Guardrail evidence: start and end checks verbatim; no purchase, N
   unchanged.
3. Results per task, with the rule table and the main results tables.
4. Delegation record: one row per spawn.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation: whether to buy a
   Combine at all, which size, which payout path, how many attempts to
   budget, the stop rule, and what a bot must and must not do under the
   terms.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
