STAGE E.35 "PASSIVE ORDERS OUTSIDE PROP FIRMS: FIND A MARKET THAT BEATS ZM'S ADVERSE SELECTION"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: E.31 found two separate reasons passive one-lot orders lose in ZM.
- Problem 1 is the prop-firm simulators' trade-through fill rule. It costs
  about 1 tick per fill, and no product choice avoids it inside a prop
  firm.
- Problem 2 is real adverse selection. Even under CBOT's real queue rules
  (K algorithm) and under a FIFO back-of-queue model, fills lost 0.25 to
  0.29 tick each before fees.

The user wants to know whether any market beats Problem 2. If one does,
passive orders could work in a venue without Problem 1: the user's own
account at a futures broker, or an exchange that pays maker rebates. This
stage finds the best candidates by reading, then measures passive markouts
on at most 6 of them with cheap data.

Lead: Opus 5.5, effort xhigh, Ultracode on (Max).
- Readers are Opus high.
- Reviews are Fable xhigh, each model confirmed from its transcript.
  Never Sonnet.
- At most 6 workers at once. One CLI session at a time (user rule): this
  stage runs only when no other stage is running.

Decisions in force: docs/DECISIONS.md V20 to V51 plus any later entries.
Binding: this prompt, V43 (each measured product counts into N), V50.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue. Checkpoint
reports/stage_e35_STATE.md after every step.

============================================================
PART A: READING (NO SPEND)
============================================================

A1 What drives adverse selection for a slow passive order. A short brief,
reusing E.28's methods brief and E.31's results. Cover:
- tick size relative to volatility (tick-constrained books have long
  queues);
- the matching algorithm (FIFO, pro-rata, mixed);
- the HFT and market-maker share;
- the mix of informed, commercial and retail flow;
- maker rebates and fee tiers;
- quote lifetimes;
- how fast a retail cancel can be.
Derive a scoring rule from these drivers, and hash it before scoring any
venue.

A2 Candidates. Score at least 25, across:
- CME Group futures with a different trader mix from ZM:
  - livestock (LE, HE, GF);
  - minor grains (ZO, ZR, KE, MWE);
  - dairy and lumber;
  - smaller FX (6N, 6S, 6M);
  - Treasury futures with large ticks (ZT, ZF);
  - micro contracts;
- ICE US softs (sugar SB, coffee KC, cocoa CC, cotton CT) and ICE
  Europe, reachable through a futures broker;
- Eurex;
- crypto venues with maker rebates at reachable tiers (spot and perpetual
  futures on the large exchanges), with their fee schedules, rebates,
  API rate limits and the published evidence on maker adverse selection.

For each candidate, collect sourced facts:
- the spread distribution;
- displayed size at the touch;
- the matching algorithm;
- maker and taker fees, and rebates;
- the evidence on passive profitability;
- the minimum capital and broker or exchange access for a Canadian
  resident;
- the data source and its price.
Follow E.28's reader rules. Never fetch CME's site by automation. Label
pointers.

A3 Score the candidates blind, from a masked fact table, and rank them.
Pick at most 6 for Part B: at most 4 CME Group products (Databento data)
and at most 2 others, if their data is affordable. Prefer products whose
historical data the program can buy for under USD 10 a month.

============================================================
PART B: MEASUREMENT (SPEND ONLY WITH APPROVAL)
============================================================

B1 Spend preconditions:
- a funded Databento account, added as acct-4 under DATABENTO_API_KEY4
  in data/config.py, reviewed, with tests and a harness bump if needed;
- the presence of the key checked by NAME only, never read, printed or
  logged;
- a logged fresh quote for the exact files;
- the user's explicit approval of that quote, given in the planning
  chat and recorded as a V-entry.
If any precondition fails, stop after Part A and write the purchase plan
with the quotes.

B2 Data window per product: 1 to 2 whole months, dated before
2024-03-01. Never inside a sealed or spent window:
- holdout-2 roots, 2024-04 to 2025-03;
- the March 2024 embargo;
- the research window for the 12 micros;
- ZM, ZS and ZL from 2017-05 to 2020-11 (the E.32 test seal).
Schema:
- MBO where the matching algorithm needs queue position (FIFO products);
- MBP-1 plus trades otherwise.
Non-Databento data is bought only under the same approval rule.

B3 Freeze reports/stage_e35_measure_spec.md and hash it before the
purchase. Reuse E.31's frozen measurement code wherever it fits. Fix:
- fill models: FIFO back of visible queue, the venue's real algorithm
  where it differs, and trade-through only for reference;
- markouts at 1, 10 and 60 seconds, against the mid, plus half the
  spread captured;
- fees: the cheapest realistic retail broker or venue tier for a
  one-lot, sourced; maker rebates where they apply;
- the pass bar: mean (markout + half-spread + rebate - fee) per fill
  above zero, with a day-block 95% bound and at least 400 fills, in the
  main session;
- Holm across the measured products;
- each measured product registered into N before its data is read.

B4 Purchase, verify against a manifest, measure, report. The
measurement code and the verdict numbers are checked by an independent
recomputation (Opus xhigh, fresh context) and a Fable review.

============================================================
SCOPE AND DELIVERABLE
============================================================

This stage does NOT:
- trade, open any account, or connect to any broker or exchange
- read any sealed or spent window
- touch live/, ops/, TopstepX credentials or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

The usual start and end checks, quoted verbatim.

Write reports/E.35_RETURN.md (the usual eight sections), one progress.md
entry, one docs/STAGES.md line, and one final commit "Stage E.35 passive
venue screen". Do not push.

Section 1 states:
- the ranked candidates;
- which were measured;
- each one's net passive edge per fill with its interval;
- whether any market beats ZM's Problem 2, and by how much;
- what trading it outside a prop firm would require (capital, broker or
  venue, fees).

END PROMPT
