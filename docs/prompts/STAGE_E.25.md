STAGE E.25 "UNTAPPED SOURCES: A DEEP RESEARCH PASS FOR A PROP-COMPATIBLE INTRADAY EDGE"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: A research-only stage (V42). No outcome read, no market data
read, no purchase, nothing added to N. The user still wants a strategy
that can pass and be paid at a futures prop firm. 538 trials so far found
none; the program's literature passes (E.13, E.20: SSRN, arXiv,
Quantpedia, 157 evidence rows) covered published intraday effects on 1-
minute bars. This stage reads what those passes did not: newer market
structure (0DTE options and dealer hedging), order-book and order-flow
evidence, news- and headline-driven futures moves, live audited track
records, prop firms' own published outcome data, practitioner work, and
trader communities as pointers. It returns a ranked shortlist of
candidate hypotheses, each with its mechanism, its expected gross move
per trade against the D8 cost hurdle, the data it needs and whether the
program owns it, prop-rule compatibility, and overlap with the 538
trials. The user decides afterwards whether any candidate earns a
registered test (most likely on the owned, unread research window
2025-04..2026-06, which lies inside the 0DTE era).

Decisions in force: docs/DECISIONS.md V20 to V42. Binding: this prompt
and V37 (maximum parallelism, shared briefs, about 2 workers per web
domain, throttled fetches logged and never presented as findings).

Lead: Opus 5.5, effort xhigh. Ultracode: on (launched interactively).

Why this lead and effort: the work is wide (up to 20 readers) and the
value is in honest triage: separating evidence from marketing, matching
each idea against 538 prior trials, and doing the cost arithmetic. Fable
reviews the ranked shortlist and recomputes every hurdle figure.

Usage and time: launched about 01:50 PDT on 2026-10-18, in parallel with
Stage E.24 (a build stage). Work to finish by 07:00 PDT; by 07:30 the
return is written, finished or not. Checkpoint
reports/stage_e25_STATE.md after every step.

Do not stop to ask, and do not use AskUserQuestion. Decide, log the choice
under Open choices in the return document, and continue.

============================================================
THE READING PLAN (FIXED HERE)
============================================================

R0. Shared brief (lead, before any reader): the program's state in one
page: D8 costs per micro (MNQ about $2.06 round trip), the V38 hurdle (a
published effect must exceed 1.5 x the D8 round trip), the prop
constraints (Topstep: flat by the session close, daily loss limits,
consistency and payout rules from reports/E.19_RETURN.md; which firms
allow automation and overnight holds, from E.13, E.21 and the planning
research), the owned data (1-minute bars only, 2010-2024 for 17 roots,
2019-2024 for 27 paths, the research window 2025-04..2026-06 unread),
and a compact index of every tested mechanism (from the E.23 inventory,
reports/stage_e23_briefs/inventory/, and the E.20 evidence table) so
readers can flag overlap without opening old reports.

Readers, all at once (opus high unless stated), each with one objective,
an output file under reports/stage_e25_briefs/, and the shared brief:
- R1 0DTE and dealer gamma: academic and practitioner work 2022-2026 on
  same-day options, dealer hedging, gamma and charm flows, and their
  intraday effect on ES and NQ (direction, horizon, size, decay); the
  data each needs (CBOE, OPRA, vendor gamma estimates) and its cost.
- R2 0DTE second reader (different query families, no overlap with R1).
- R3 Order-book and order-flow imbalance on CME futures: the horizons
  and sizes published (Cont-Kukanov-Stoikov and later), what survives at
  retail latency (100 ms to seconds) and at 1- to 30-minute horizons, and
  the data needed (Databento MBP-1, MBP-10, MBO; quote the published
  prices, do not request a quote).
- R4 Volume and trade-side features computable from data the program
  could own cheaply (trade prints, TBBO, volume profile, VWAP families);
  overlap with K1-vwap and ZA23 stated.
- R5 News and headline-driven intraday futures moves: macro headlines,
  geopolitical and oil headlines, LLM-scored news, Fed speakers; event
  horizons, sizes and decay; timestamped news sources with terms and
  cost (including free sources such as GDELT and agency press feeds).
- R6 Scheduled-event microstructure the program did not test: CPI, NFP,
  retail sales, PCE, GDP release minutes on NQ, ES, ZN, CL, GC (check
  the inventory first; report only what is not already a trial).
- R7 Live audited track records: Collective2, Darwinex-like platforms,
  World Cup Trading Championship, broker-audited system vendors: does
  any intraday futures system show a multi-year live record net of
  costs, and what style is it. Treat as selection-biased; record the
  bias.
- R8 Prop firms' own outcome data: published pass rates, payout counts
  and amounts, payout-to-fee ratios, and any firm statements on what
  styles get paid (Topstep, Apex, Tradeify, Take Profit Trader, MFFU,
  others with public data); terms read first.
- R9 Prop-firm rules landscape since E.21: firms that now allow
  automated or semi-automated strategies, overnight holds or news
  trading, with plan-level rules quoted (this updates V38 and V39).
- R10 Practitioner books and authors on short-term futures patterns
  (Crabel, Raschke, Davey, Williams, Chan, Zarattini and Concretum's
  2023-2026 papers): which specific rules have been published with
  out-of-sample or live evidence, and which the program already tested.
- R11 Communities as pointers only: NexusFi, Elite Trader,
  r/FuturesTrading, r/algotrading, prop-trader interviews on YouTube
  (titles and descriptions through search results; no scraping where the
  terms forbid it, no transcript download unless the terms allow it).
  Output: recurring ideas, never evidence.
- R12 Volatility and regime timing for intraday books (VIX term
  structure, overnight-range filters, event-day exclusion): does any
  published filter lift a weak intraday effect above costs.
- R13 Cross-market intraday lead-lag not yet tested (check K8 and the
  inventory first): rates to equity index, dollar to gold, crude to
  energy equities, with horizons.
- R14 to R20: spare readers the lead assigns after R1-R13 report, to
  chase the strongest leads in depth (a second reader on any candidate
  ranked in the top five).

Source rules for every reader: academic papers, official exchange,
regulator, firm and vendor pages are evidence; blogs, forums, videos and
social posts are pointers only. Read each site's terms before any
automated fetch; never fetch CME's site or archived copies by
automation; X, Reddit and YouTube content only through search-engine
results and pages whose terms allow access, no scraping. A throttled or
blocked fetch is logged, never reported as missing evidence.

============================================================
SYNTHESIS (FIXED HERE)
============================================================

S1. Candidate table: one row per distinct hypothesis, with: mechanism;
best evidence and its quality (peer-reviewed, working paper, vendor,
live record, pointer); instrument and horizon; published gross effect per
trade in ticks and dollars on the micro; the D8 round trip and the ratio
(hurdle 1.5); data needed, owned or not, and the cost to get it; whether
the owned research window can test it; prop compatibility (flat by
close, daily loss limit, automation and news rules, per firm); overlap
with any of the 538 trials (named); and a lead rank.
S2. A short list of at most 5 candidates that clear the hurdle on
published numbers and do not duplicate a prior trial, each with a draft
test design (one paragraph, no parameters chosen from data) and its
power on the research window at the published effect size.
S3. An honest closing paragraph: what the evidence says about the odds
that any intraday futures edge is reachable at retail costs and prop
rules, with the reasons.
S4. ShortlistReviewer-FableXHigh: checks every row's evidence quality
label, recomputes every hurdle ratio and power figure, and checks the
overlap claims against the inventory; BLOCKING and SHOULD FIX fixed
before the return.

============================================================
SCOPE
============================================================

This stage does NOT:
- read any market data (owned or not), any holdout, the embargo or the
  research window; no outcome is computed
- register, freeze or test anything; N stays 538 (E.24 may raise it to
  539 in parallel; report whichever N the ledger shows at the end)
- buy, subscribe, request a quote, or call Databento
- create accounts, sign up, or log in anywhere
- touch the files Stage E.24 is changing (forward/, base_rules/,
  multiday/, the harness); this stage writes only under
  reports/stage_e25_briefs/, reports/stage_e25_STATE.md and its return
- touch live/, ops/, any TopstepX credential or the ProjectX API
- print, copy or log any key. REGISTRATION.md stays 0 bytes.
- push

============================================================
GUARDRAILS
============================================================

- Start and end checks quoted verbatim in the return: `git status
  --short`, `git log --oneline -3`, the holdout status, `wc -c
  REGISTRATION.md`, the ledger line count and sha256, N. No pytest run
  (E.24 owns the test suite tonight).
- Commits touch only this stage's files; before committing, `git status`
  shows no file of E.24 staged.
- Before ending, confirm no worker or background shell is still running.

============================================================
DELEGATION PLAN
============================================================

| Step | Owner | Model | Effort | Parallel or serial | Why this tier |
|---|---|---|---|---|---|
| 0 Startup, R0 brief | lead | opus | xhigh | first | one shared brief |
| R1-R13 readers | SourceReader-OpusHigh x 13 | opus | high | all at once, about 2 per web domain | independent topics |
| R14-R20 deep follow-ups | SourceReader-OpusHigh x up to 7 | opus | high | after R1-R13 | chase top leads |
| S1-S3 synthesis | lead | opus | xhigh | after the readers | triage and arithmetic reserved |
| S4 review | ShortlistReviewer-FableXHigh | fable | xhigh | after S3 | independent recomputation |
| Return | lead | opus | xhigh | last | reserved |

    DELEGATION PLAN (the lead executes this; it does not do worker tasks)
    1. Decompose each task into subtasks with one objective, inputs, output
       path and format, allowed tools, and boundaries.
    2. Route per CLAUDE.md. State model and effort for each subtask before
       spawning.
    3. Run independent workers at once (V37).
    4. Collect results as files plus short summaries.
    5. Verify every number entering the shortlist with an independent
       fable xhigh worker.
    6. Synthesize in the lead against this prompt, and write the synthesis
       to disk before ending.
    7. Unattended run: no pauses to ask. Checkpoint to
       reports/stage_e25_STATE.md after each task.

============================================================
DELIVERABLE: ONE RETURN DOCUMENT
============================================================

Write reports/E.25_RETURN.md, one progress.md entry, one docs/STAGES.md
line, and one final commit "Stage E.25 untapped sources research". No
push. Fixed sections:

1. Summary, at most 300 words: the shortlist (or that none cleared the
   hurdle), the strongest single lead, and what the user must decide.
2. Guardrail evidence: start and end checks verbatim; order of events.
3. Results: the candidate table (S1), the shortlist with draft designs
   (S2), the closing assessment (S3), and per-reader source lists.
4. Delegation record.
5. Verification: each Fable finding, the ruling and the fix.
6. Open choices: every decision the lead made on its own, with the reason.
7. Decisions for the user, each with a recommendation.
8. Session cost: the final ETA table and the per-model token table, per
   CLAUDE.md. Never estimated.

The last thing before ending: list every open choice in section 6 of the
return document.

END PROMPT
