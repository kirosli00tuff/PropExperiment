STAGE E.28 "THE METHODS BRIEF, THE FIRM-CONTRACT RANKING, AND THE ORDER-BOOK PILOT"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: The main stage of the user's last Max day (2026-10-21), run
beside Stage E.26 (V43, V44). Three parts, in this chronological order:
- Part C, the user's priority: a methods brief. First a gap inventory of
  every method the program has used, then deep dives on what it never
  used (mostly the mathematics of prices, order flow and limit-order
  books, and machine learning on order-book data), then an honest
  section on whether missing methods explain the program's failures,
  then a draft design for the ML and model search under V43.
- Part A: a blind two-layer ranking of firm-contract pairs for
  limit-order strategies at automation-friendly prop firms.
- Part B, LAST: the pilot data purchase for the top pair's one contract
  and one schema, then the pilot measurement (fill rates, queue times,
  markouts) under a spec frozen before the download.
No rule is tested, nothing is registered, N stays 538.

Decisions in force: docs/DECISIONS.md V20 to V44 (V43: the amended V28;
V44: this day's rules). Binding: this prompt and V37.

Lead: Opus 5.5, effort xhigh. Ultracode: on (launched interactively).

Why this lead and effort: the brief's value is in correct mathematics and
honest evidence; the ranking's value is in fixed criteria applied
blindly; the pilot's value is in a fill model that cannot flatter the
result. Fable checks the brief's mathematics, the ranking arithmetic, the
schema decision, the measurement spec and the spend.

Usage and time: launched about 02:15 PDT on 2026-10-21; the laptop is on
until 24:00. Work until 23:00 PDT; the return by 23:30; nothing running
after 23:45. At most 6 workers at once (E.26 runs beside this session).
Each part writes a finished, self-contained section to disk as it
completes, so a usage limit never leaves a part half-done. Checkpoint
reports/stage_e28_STATE.md after every step and resume from it after any
usage limit. If a part finishes early, deepen the weakest section rather
than stopping.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
PART C: THE METHODS BRIEF (THE USER'S PRIORITY)
============================================================

Spend careful time and the largest share of the reading budget here
(readers in waves, at depth; the lead writes the synthesis at xhigh).

C1. Gap inventory first. From the repo (the harness, base_rules, the ML
v2 and E.20 pipelines, and the E.12, E.13, E.20, E.21, E.23 and E.25
returns) list every method the program has used (rule screens on
1-minute bars, Newey-West t, Holm, DSR, PBO and CSCV, ridge and LightGBM
on the 64-feature library, EWMAC trend sizing, and the rest) and then
what it never used.

C2. Deep dives on what was never used:
- stochastic calculus and continuous-time models of prices and order
  flow: Ito processes, jump-diffusions, Ornstein-Uhlenbeck mean reversion
  and its estimation;
- point processes: Poisson and Hawkes order arrivals and their
  maximum-likelihood estimation;
- limit-order-book models: queue-reactive and Cont-Stoikov-Talreja
  models and the mathematics of fill probability;
- stochastic optimal control and the Hamilton-Jacobi-Bellman equation
  behind Avellaneda-Stoikov and Gueant market making with inventory and
  Almgren-Chriss execution;
- filtering: Kalman and particle filters, hidden Markov regimes;
- random-matrix covariance cleaning; information theory and entropy
  features; fractional differencing and meta-labeling; signal processing
  (wavelets, spectral methods); Bayesian methods and shrinkage;
- machine learning on order-book data: DeepLOB and later CNN, RNN and
  transformer models, gradient-boosted trees on order-flow-imbalance
  features, deep OFI, label design at horizons that beat costs,
  post-publication results and decay, what survives retail latency;
- single-contract versus pooled multi-contract models (Sirignano and
  Cont 2019, universal features of price formation, and later work);
- how top firms run the research process (Two Sigma, Man AHL, AQR,
  Citadel Securities, Jane Street, Optiver, Jump and others where
  public).
For each method: the core idea in plain words; the key equations with
every term explained; the data it needs; what it estimates or decides; a
small worked example where it helps; how it would turn the pilot data
into a testable, pre-registerable hypothesis; compute needs (the 14 GB
laptop versus a bigger machine or a cloud GPU, with cost); and honest
evidence on whether it works at retail scale and latency.

C3. An honest section: does the missing mathematics explain the
program's failures so far, or were costs and data granularity the binding
constraint? Cite the earlier returns.

C4. A recommended method set, and a draft design for the ML and model
search stage under V43: a phased contract plan (one contract first, then
a pooled model on 2 to 3 similar contracts tested on an unseen contract),
its trial counting into N, its validation (purged and embargoed CV, a
frozen pipeline, one test on data that never selected it), and the
hardware and data it needs.

Sources: textbooks, papers, public firm research and talks, exchange and
regulator publications; interviews as pointers. MathReviewer-FableXHigh
checks every equation, derivation summary and claim of evidence before
the return; BLOCKING and SHOULD FIX fixed first.

============================================================
PART A: THE FIRM-CONTRACT RANKING (BLIND)
============================================================

Write the criteria, their weights, the Layer 1 gate and the combination
rule to reports/stage_e28_ranking_spec.md and hash it BEFORE any lookup.

Candidates: MNG, QG, MGC, SIL, MHG, MCL, M6E, M6A, MET, MBT, M2K, MYM, the
micro yields and micro grains, and minis or full-size versions where a
firm allows them; MNQ as the baseline. Firms: Topstep, Lucid, Tradeify,
MFFU, Bulenox.

Layer 1, contract feasibility (readers per contract): market structure
and participants (commercial hedgers; the retail share, which is high in
micros and lowers adverse selection; HFT and designated or lead market
makers and their incentive programs; competition intensity),
tick-constrainedness and queue sizes, spread regimes and depth by
session, information events and their timing, volume and volatility per
tick, gap and limit-move risk, and published microstructure research on
the contract or close cousins with any evidence of findable short-horizon
patterns. Contracts below the gate are not ranked further.

Layer 2, firm-contract economics for each surviving contract at each
firm: fees in ticks (that firm's per-contract commission for that product
divided by tick value), the dollar limits in ticks and in typical daily
ranges, position limits and micro-to-mini scaling, product restrictions
(news windows around EIA, inventory and other reports; trading hours),
automation permission and order-rate or scalping rules, and the prop
economics (reuse E.19's simulator with the rules record E.26 refreshes)
under a market-order and a limit-order cost case: per pair, the gross
edge per trade in ticks needed to break even and to reach USD 10K, and
the expected cost per attempt.

Also scored:
- per firm and platform (Tradovate, Rithmic, CQG, TopstepX): how its
  simulated accounts fill resting limit orders (touch, trade-through or
  queue model), supported order types, API rate limits, typical
  round-trip latency from Vancouver to CME Aurora, and whether a VPS near
  Chicago is allowed. The score uses both the pilot's real-market fill
  model and each firm's sim fill rule; exploiting sim fill quirks is
  excluded (Lucid bans it; check each firm's terms);
- firm reliability and eligibility: payout track record and speed,
  regulatory actions against the firm or close peers, history of rule
  changes, acceptance of British Columbia residents and any
  Canada-specific payout terms; one line on Canadian tax treatment of
  prop payouts (not a ranking factor).

Output: reports/stage_e28_ranking.md, one ranked table of firm-contract
pairs with every score shown, the top pair selected and the next 4 named
(none bought). RankingReviewer-FableXHigh recomputes the arithmetic.

============================================================
PART B: PURCHASE AND PILOT (LAST IN ORDER)
============================================================

Part B starts after Parts C and A are finished and E.26's STATE file
marks the data move done. The purchase starts no later than 20:30 PDT,
so the download and its verification finish before 23:00.

B1. The schema decision, written before any quote: the single Databento
schema the pilot needs (mbo if queue position must be reconstructed;
otherwise the cheapest of mbp-1, tbbo or mbp-10 that supports fill
rates, queue times and markouts), with the reason; and the minimum date
span inside 2023-11-01..2024-02-29 that gives stable estimates, with the
arithmetic.

B2. The measurement spec, frozen and hashed before the download, so the
pilot cannot turn into an edge search: the order placements simulated
(at the touch, and one tick inside the spread where the spread allows;
size 1 contract); the conservative fill rule (an order joins at the back
of the visible queue and fills only when the volume traded at its price
after it joined exceeds the queue ahead, or price trades through it;
with mbp-10 the queue ahead is the displayed size at join; never a fill
on a touch alone); cancellations; sessions and their clock boundaries;
markout horizons 1, 10 and 60 s against the mid; the statistics and
their confidence intervals; and what counts as a positive markout. The
analysis runs only this spec. SpecReviewer-FableXHigh checks B1, B2 and
the spend plan before any purchase.

B3. The account and the spend (user, 2026-10-21 01:10 to 01:34):
- The purchase uses ONLY ACCOUNT_3 (DATABENTO_API_KEY3), a temporary
  account the user funds around 10:00 PDT today and will wipe after the
  download. Never spend on acct-1 or acct-2. The key is checked by
  variable NAME only (empty or non-empty); never read, print, copy or log
  its value. If ACCOUNT_3's selection code from E.26 is not committed
  yet, wait for it.
- Check the balance (through the existing quote tool or balance call)
  only when the purchase step is reached.
- Use ALL the funds on that account, on the pilot's ONE contract and ONE
  schema only: first the minimum span of B1, then, with what is left,
  extend the SAME contract and schema backwards in time (earlier dates
  only), keeping a few dollars of margin so the order is not rejected.
  Never 2024-03-01 or later, never the research window, holdout-2 or the
  embargo. No second contract, no second schema.
- Get one fresh quote for exactly that request, log it in the spend
  ledger with the account, then buy. If the key is missing or the balance
  does not cover even the minimum span by 20:30 PDT, buy nothing, and
  leave the quote, the frozen spec and the code ready for a Pro-plan
  session.

B4. Download straight to /mnt/large-storage/market_data/PropExperiment/
(E.26's destination root), verify every file (sizes, record counts,
sha256 in a manifest), log the amount and account in the spend ledger,
and write "ACCOUNT_3 SAFE TO WIPE" with the time, amount and what was
bought to the STATE file. The planner tells the user from that line;
wiping before it would lose the data.

B5. If time remains, run the frozen spec on the purchased data and
re-score the top pair with the measured costs and the firm's sim fill
rule. Otherwise the pilot analysis is the first job for a Pro-plan
session, with the data on disk. No rule is tested and nothing is
registered.

============================================================
SCOPE
============================================================

This stage does NOT:
- read or buy the research window, holdout-2 or the embargo, or any data
  dated 2024-03-01 or later
- test any rule, register anything, or change N
- spend on acct-1 or acct-2, or spend on more than one contract or schema
- connect to any broker; touch live/, ops/, any TopstepX credential or
  the ProjectX API
- touch E.26's files (the data move, data/config.py, DECISIONS.md)
- print, copy or log any key. REGISTRATION.md stays 0 bytes.

============================================================
GUARDRAILS
============================================================

- Start and end checks quoted verbatim: `git status --short`, `git log
  --oneline -3`, the holdout status, `wc -c REGISTRATION.md`, the spend
  ledger line count and sha256, N. No pytest run (E.26 runs the suite).
- Commits touch only this stage's files; before committing, `git status`
  shows no file of E.26 staged. Do not push (the planner pushes).
- Before ending, confirm no worker, download or background shell is
  still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, specs | lead | opus | xhigh | first | ranking spec hashed before lookups |
| C1 gap inventory | MethodsInventory-OpusHigh | opus | high | first wave | repo reading |
| C2 deep dives | MethodReader-OpusHigh x waves | opus | high | waves, with Part A readers, 6 at once in total | depth per method family |
| C3, C4 synthesis | lead | opus | xhigh | after C2 | reserved |
| C review | MathReviewer-FableXHigh | fable | xhigh | after C4 | equations and evidence |
| A Layer 1 | ContractReader-OpusHigh x waves | opus | high | waves | per contract |
| A Layer 2 and extras | FirmReader-OpusHigh, EconCoder-OpusXHigh | opus | high, xhigh | after Layer 1 | rules and simulator |
| A review | RankingReviewer-FableXHigh | fable | xhigh | after the table | arithmetic |
| B1, B2 | lead | opus | xhigh | after A and C | reserved |
| B review | SpecReviewer-FableXHigh | fable | xhigh | before the purchase | spec and spend |
| B3-B5 | lead, PilotCoder-OpusXHigh | opus | xhigh | last | purchase and measurement |
| Return | lead | opus | xhigh | last | reserved |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. Run independent workers at once (V37); at most 6 at once today.
    4. Collect results as files plus short summaries.
    5. Verify every number entering a decision with an independent fable
       xhigh worker.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e28_STATE.md after each task.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.28_RETURN.md, reports/stage_e28_methods_brief.md and
reports/stage_e28_ranking.md, one progress.md entry, one docs/STAGES.md
line, and one final commit "Stage E.28 methods brief, ranking and pilot".
No push. Fixed sections of the return:

1. Summary, at most 300 words: the methods brief's headline and C3's
   answer; the top firm-contract pair and the next 4; the purchase
   (account, amount, contract, schema, span) or why nothing was bought;
   the pilot result or its status; what the user must decide.
2. Guardrail evidence: start and end checks verbatim; order of events.
3. Results: Part C (pointer to the brief, with its contents list), Part
   A (the table), Part B (the schema decision, the frozen spec and its
   hash, the quote, the purchase, the verification manifest, the pilot
   results).
4. Delegation record.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation, marking which next
   steps fit a Pro plan (short, few workers) and which need a Max-sized
   session or a bigger machine.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
