STAGE E.0 "CME UNIVERSE: RESEARCH, HYPOTHESIS CATALOG AND PROGRAM DESIGN"

BEGIN PROMPT - SUMMARY OF PROMPT

Summary: Stage D closed intraday MES for the XFA. The D.1f run found every
class C1 to C5 and C7 null at epsilon = 34 net ticks per micro per day
(commit ca8befb), and C6 (passive execution) is closed here as
non-deployable on the XFA without running D.1g (Task 7). Stage E widens
the program to every CME Group product TopstepX lists, run as one
program over one universe with clusters, instead of 45 separate
projects. This session, E.0, is the research and design session only.
It does four things: (1) collects the facts the design depends on
(Topstep's per-product rules and fees, public liquidity figures, free
Databento quotes for every product); (2) runs a literature and
practitioner research pass per cluster, the way Stage D.1 did for MES,
with the same pre-filter and citation discipline; (3) turns what the
research supports into a written hypothesis catalog, every member fully
specified before any price data for the new products exists on this
machine; (4) drafts the Stage E program design (universe, liquidity
floor, sizing, epsilon per product, windows, holdouts, multiple-testing
plan, cost model plan, session plan, spend plan). An independent Fable
review audits the catalog and the design. Nothing is frozen, bought or
registered here. The user reviews the catalog and the design, and Stage
E.1 freezes them and buys the data.

Lead: Opus 5.5, effort max. Ultracode: off.

Why this lead and effort: the research reading is delegated, but the
session's real output is a set of design choices that every later Stage
E session inherits: which products are in, how epsilon converts per
product, how the multiple-testing budget splits across clusters, what
counts as a Topstep-rule conflict. A weak choice here silently weakens
every null or finding that follows. CLAUDE.md reserves opus max for
judgment of that kind. Ultracode stays off because the fan-out is
explicit in the delegation plan below and must go through the worker
files, so each worker's model and effort follow the routing table;
ultracode's own fan-out would bypass it.

Usage: Fable's shared allowance hit its limit once last week. Fable is
used once here, for the independent review in Task 6, at xhigh. If
Fable is unavailable when Task 6 starts, finish everything else, mark
the review pending in the STATE file and the entry, and label the
catalog and design "pending independent review". Never substitute opus
for the Fable review. The research tasks are web-heavy and token-heavy:
keep sources to the pre-filter, and do not re-read a source another
worker already logged.

============================================================
SCOPE
============================================================

This session does:
- collect Topstep's per-product facts, public liquidity figures and free
  Databento quotes for the universe (Tasks 1 and 2)
- research each cluster and log every source considered (Task 3)
- write the hypothesis catalog (Task 4)
- write the Stage E program design draft (Task 5)
- record the C6 closure decision (Task 7)
- run the independent review and rule on its findings (Tasks 6 and 8)

This session does NOT:
- buy anything. Quotes only, $0.00. Add a Stage E.0 session id to
  data/config.py with a $0.00 session cap and a $0.00 request cap, so the
  gate refuses any billable request by construction. Do not change
  SHARED_ACCOUNT_CAP_USD.
- download, open, chart or summarize price, volume-by-minute or order
  book data for any product. The catalog must be written before any such
  data exists on this machine. Public aggregate figures (average daily
  volume, open interest, contract specifications, published tick sizes)
  are allowed for the liquidity floor; bar-level data is not. The
  Databento billable-size figure from a quote is allowed as a coverage
  proxy, since it carries no prices.
- read MES bars. MES is closed. It appears in Stage E only as one leg of
  a cross-product member, and only on non-holdout dates.
- freeze, hash or register anything. REGISTRATION.md stays 0 bytes. The
  catalog and design are drafts for the user's review.
- touch holdout-1 or holdout-2, rules/, live/, ops/, sim/, screening/,
  funnel/, strategy/, or any TopstepX credential or API
- edit docs/NULL_CRITERIA.md or reports/stage_d1f_confirmation_list.md.
  Both stay frozen as the MES record. Stage E gets its own criteria draft
  (Task 5).
- build or test any social-media or sentiment signal (shelved in an
  earlier session; unchanged)
- commit. The planning chat commits after the user's review.

============================================================
CONTEXT TO READ FIRST
============================================================

1. CLAUDE.md, in full: roles, routing, worker naming, compute limits,
   ETA tables, Session cost, unattended runs. This prompt restates only
   what is specific to this stage.
2. progress.md: the Stage D.1f (run) entry in full, and the Stage D.1e
   entry's sections on epsilon, the power table and the funnel model.
   These define the bar a Stage E member must clear and how it was
   derived.
3. docs/NULL_CRITERIA.md and reports/stage_d1f_confirmation_list.md, read
   only, as the template Stage E's criteria draft generalizes.
4. docs/prompts/STAGE_D.1.md, Task 1, for the research pre-filter and
   citation rules this session reuses per cluster.
5. docs/DECISIONS.md, docs/STAGES.md, docs/ORCHESTRATION.md.
6. data/spend_gate.py and data/pull_mes.py (quote path only), for Task 2.
7. rules/xfa_rules.py, read only: it encodes the 50K XFA for MES alone.
   Task 5 lists what Stage E.2 must add.

============================================================
THE UNIVERSE AND ITS CLUSTERS
============================================================

The universe is every product on Topstep's permitted products page
(help.topstep.com/en/articles/8284206, last updated 2026-07-13, fetched
by the planning chat on 2026-09-23). Task 1 re-fetches it and records any
change. Clusters are labelled K1 to K8 so they never collide with the
MES class labels C1 to C7.

- K1 equity index: MNQ, M2K, MYM, NKD; full-size ES, NQ, RTY, YM as
  alternate vehicles of the same exposures. MES only as a cross-product
  leg.
- K2 rates: ZT, ZF, ZN, TN, ZB, UB.
- K3 FX: 6A, 6B, 6C, 6E, 6J, 6S, 6M, 6N, E7, M6E, M6A, M6B.
- K4 energy: CL, QM, MCL, NG, QG, MNG, RB, HO.
- K5 metals: GC, MGC, SI, SIL, HG, MHG, PL.
- K6 agriculture and livestock: ZC, ZW, ZS, ZM, ZL, HE, LE.
- K7 crypto: MBT, MET.
- K8 cross-cluster relationships only: lead-lag and relative value where
  the legs sit in different clusters (for example rates leading equity
  index, the dollar and gold, crude and CAD). Relationships inside one
  cluster (gold and silver, the crack spread, the soybean crush, MNQ and
  M2K, the Treasury curve) belong to that cluster, not K8.

Where a product has a micro and a full-size contract, the design picks
one trading vehicle per exposure (Task 5, D2). Where only a full-size
contract exists (rates, most FX, grains, livestock, PL, NG), the vehicle
is the full-size contract, subject to the 50K limit of 5 minis.

============================================================
TOPSTEP CONSTRAINTS EVERY MEMBER MUST RESPECT
============================================================

These are the constraints as the planning chat read them on 2026-09-23.
Task 1 confirms each one verbatim from Topstep's own pages and records
any difference, and Task 5 encodes the confirmed versions.

- Flat by the XFA cutoff: TopstepX closes at 15:10 CT for every product;
  the program flattens by 15:08 CT. Grains trade 19:00 to 07:45 CT and
  08:30 to 13:20 CT; livestock 08:30 to 13:05 CT.
- Limit orders on TopstepX fill only when the market trades through the
  price (help.topstep.com/en/articles/8765442). Any member using limit
  orders is modelled at trade-through fills, the pessimistic model D.1f
  used for C-H4.
- Prohibited on Topstep (help.topstep.com/en/articles/10305426, updated
  2026-06-10; help.topstep.com/en/articles/10431370): "Running scalping
  algorithms designed to exploit unrealistic SIM fills"; "Making
  hundreds of rapid trades to take advantage of preferential queue
  position in SIM"; patterns of "hundreds or thousands of trades per day,
  with average durations measured in seconds, not minutes"; trading
  gapped markets for stray fills; exploiting the lack of SIM slippage on
  stops; tight brackets or auto-breakeven for favourable SIM fills. A
  member whose edge depends on any of these is excluded at design, with a
  logged reason. Task 5 sets a program-wide trade-rate and holding-time
  floor that keeps every member clear of the "seconds, not minutes"
  pattern.
- Products marked * on the permitted list carry product-specific
  restrictions under Topstep's Prohibited Conduct policy. Task 1 finds
  and quotes each restriction.
- News and scheduled-event trading: Task 1 establishes, verbatim, what
  Topstep allows around scheduled releases (EIA, USDA, FOMC, CPI, NFP)
  for XFAs. Event classes depend on the answer; if a restriction applies,
  Task 4 writes it into every affected member.
- Position limits on a 50K account: 5 minis or 50 micros, with special
  weightings for Micro Silver, Micro Bitcoin and Micro Ether
  (help.topstep.com/en/articles/8284223). XFA scaling applies.
- The eventual bot must run on a personal device (no VPS, VPN or remote
  server) and uses the ProjectX API; there is no sandbox. This does not
  affect E.0's work but belongs in the design's deployment notes.

============================================================
TASK 0: STARTUP
============================================================

- `uv run python -m data.holdout status`: both holdouts all_ok, 0
  unlocks. Repeat at the end.
- Confirm HEAD is ca8befb or a descendant, and the working tree is clean
  apart from files this session creates.
- Confirm REGISTRATION.md is 0 bytes.
- Write the estimate ETA table (CLAUDE.md) and print it in chat. Base the
  research rows on a probe: time one worker's pre-filter pass over one
  source container before sizing the rest.
- Start reports/stage_e0_STATE.md and keep it current, so the session
  can resume after an interruption without redoing finished tasks.

============================================================
TASK 1: TOPSTEP FACTS AND PUBLIC LIQUIDITY
============================================================

Two workers, in parallel.

TopstepFacts-SonnetMed (worker-medium, sonnet) reads Topstep's help
center and rules pages and writes reports/stage_e0_topstep_facts.md and
.json. For every fact: the verbatim quote, the URL, the fetch date and
the page's own "last updated" date. Facts required:
- the permitted product list, per exchange, with every * mark
- each * product's restriction, quoted from the Prohibited Conduct policy
- TopstepX commissions and fees per product (round turn), and the page
  they come from
- trading hours per product group, and the daily and weekly close
- position limits for 50K, 100K and 150K, special weightings, and the
  XFA scaling plan tiers where published
- rules on trading around scheduled news and economic releases, for the
  Combine and for the XFA separately
- the prohibited-strategy and SIM-fill pages, quoted in full
- the XFA payout rules per tier, including the Daily Loss Limit option
  that doubles the payout caps when added at Combine checkout
- the API access page: personal device rule, no sandbox, HFT rule
Where a fact is not published, write "not published" with the pages
checked. Do not infer a number.

LiquidityCensus-SonnetMed (worker-medium, sonnet) writes
reports/stage_e0_liquidity.md and .json: for each product, the
contract specifications (tick size, tick value, contract unit, listing
date of the micro where one exists) and public average daily volume and
open interest, from CME Group pages or other published sources, each
with URL and date. cmegroup.com often refuses automated fetches; D.1f's
CalendarChecker read CME pages through Wayback Machine copies, and that
is the accepted route here, with the archive URL logged. No bar data, no
Databento data. Where a figure cannot be found, write "not found".

============================================================
TASK 2: FREE QUOTES FOR THE UNIVERSE
============================================================

QuoteCoder-OpusHigh (worker-high, opus) writes a quote-only module,
data/quote_universe.py, reusing data/spend_gate.py's quote path and
ledger, under the new Stage E.0 session id with $0.00 caps. It must be
unable to request data: no timeseries call exists in the module, and a
test proves the gate refuses a billable request under the E.0 caps.

The lead runs it. For each product: quote GLBX.MDP3 ohlcv-1m for the
continuous front-month series from 2019-05-01 (or the product's listing
date if later) to 2026-06-21, split by month as pull_mes does, and log
every quote at $0.00. Also quote, per product, the cost of a small
spread-calibration sample (5 full trade dates of mbp-1 or tbbo, dates
chosen by a stated rule that avoids both holdout windows), because
Stage E.2's cost model needs one. Write reports/stage_e0_quotes.md and
.json: per product, total ohlcv-1m cost, billable bytes, the
calibration-sample cost, and the minute-coverage proxy from billable
size. Then the totals per cluster and for the whole universe.

If the Databento key or ledger is unreadable (the ledger lives at the
archived MLCryptoEngine path on the large drive), stop Task 2, record
it, and continue the other tasks.

============================================================
TASK 3: RESEARCH PER CLUSTER
============================================================

Eight workers, one per cluster K1 to K8, at most 4 running at once.
ClusterReader-K#-SonnetMed (worker-medium, sonnet) for each cluster.
Each writes reports/stage_e0_research_K#.md.

The rules are Stage D.1's Task 1, applied per cluster:

1. Pre-filter every item on title, abstract and lede only: does it
   concern this cluster's products, or a market close enough in
   microstructure that the mechanism plausibly transfers, at an intraday
   horizon that can be flat by 15:08 CT? If not, log one line (source,
   item, one-phrase reason) and move on. No full-text fetch for rejected
   items.
2. For items that pass: retrieve the full text, and log the mechanism in
   one or two sentences, the product and horizon, the source's own cost
   assumptions, the data window, and any source-quality tells
   (speculative language presented as findings, vague sourcing,
   cherry-picked windows, vendor marketing, aggregation instead of
   primary research).
3. Citation verification is mandatory: a claim is logged as sourced only
   with the specific passage from retrieved text quoted beside it. Any
   numeric result (a return, a Sharpe, a hit rate, a cost) is re-checked
   against the text before it is logged. Anything that cannot be pinned
   to retrieved text is marked [unverified]. Say plainly when a full text
   could not be retrieved (paywall, blocked fetch) and what was read
   instead.
4. Every mechanism is tagged as either new to the program or a port of an
   MES family (name the D.1 family), and as intraday-feasible under the
   Topstep constraints above or not, with the reason.

Starting source directory. These are discovery seeds the planning chat
named from memory; verify each before relying on it, and log any seed
that turns out wrong or unreachable.

All clusters: SSRN (Market Microstructure eJournal, Derivatives
eJournal, Commodities eJournal); arXiv q-fin.TR and q-fin.ST; the
Journal of Futures Markets (abstracts are open); CFTC Office of the Chief
Economist papers; CME Group research and education articles (via Wayback
when blocked); Databento's blog; Quantpedia filtered to the cluster's
instruments; practitioner blogs as a discovery layer only (Jonathan
Kinlay, Quantitative Brokers, Robert Carver, Robot Wealth, Quantocracy
as an aggregator). Named author seed for scheduled-announcement effects
in futures: Alexander Kurov (West Virginia University).

- K1 equity index: the MES D.1 sources apply; add lead-lag between ES,
  NQ, RTY and YM, the Nikkei contract's overlap with Tokyo hours, and
  index-rebalance days.
- K2 rates: Treasury auction cycles (seed: Lou, Yan and Zhang,
  "Anticipated and Repeated Shocks in Liquid Markets", Review of
  Financial Studies, 2013); FOMC, CPI and NFP responses in Treasury
  futures; Federal Reserve and New York Fed staff reports; month-end
  index extension flows.
- K3 FX: the WM/Reuters 4 p.m. London fix (seed: Melvin and Prins,
  "Equity Hedging and Exchange Rates at the London 4 p.m. Fix", Journal
  of Financial Markets, 2015); the Tokyo fix; FX futures against spot
  around the CME and London sessions.
- K4 energy: the EIA Weekly Petroleum Status Report and the weekly
  natural gas storage report (seed: Halova, Kurov and Kucher, "Noisy
  Inventory Announcements and Energy Prices", Journal of Futures
  Markets, 2014); API inventory data the evening before; crack spread
  relationships; roll and expiry behaviour.
- K5 metals: the LBMA gold price auctions and their effect on COMEX
  (seed: Caminschi and Heaney, "Fixing a Leaky Fixing: Short-Term Market
  Reactions to the London PM Gold Price Fixing", Journal of Futures
  Markets, 2014); the gold-silver relationship; copper and the Asian
  session.
- K6 agriculture and livestock: USDA reports (WASDE, Crop Progress,
  Grain Stocks, Acreage, Hogs and Pigs, Cattle on Feed) and market
  reactions (seed: Scott Irwin and colleagues, farmdoc at the University
  of Illinois, farmdocdaily.illinois.edu); the soybean crush; the
  overnight-to-day-session gap.
- K7 crypto: CME bitcoin and ether futures against spot, the weekend gap
  between the CME close and the Sunday open, and the CME settlement
  window.
- K8 cross-cluster: lead-lag between rates and equity index, the dollar
  and gold, crude and CAD, and any cross-asset intraday relationship the
  other seven workers flag as outside their cluster (the lead routes
  those flags to K8, so no two workers read the same mechanism).

Partition rule: before dispatch, the lead writes each worker's region in
reports/stage_e0_partition.md, stated so that two workers cannot end up
reading the same mechanism from different angles. Any overlap found
afterwards is reported as a partitioning failure, not as convergence.

Cap: each worker stops after its cluster's containers are exhausted or
after 60 full-text reads, whichever comes first, and logs where it
stopped. The lead may raise one worker's cap with a logged reason.

============================================================
TASK 4: THE HYPOTHESIS CATALOG
============================================================

For each cluster, CatalogWriter-K#-OpusXHigh (worker-xhigh, opus) turns
that cluster's research log into catalog entries, in
reports/stage_e0_catalog_K#.md. It may use only sourced or clearly
reasoned mechanisms from the log, never a mechanism from memory. At most
4 run at once; each starts when its cluster's research is finished.

Every entry is complete before any data exists:
- ID (K#-short-name-##), cluster, product or products, trading vehicle
- mechanism, and the verified passages it rests on (log references)
- new, or a port of an MES family (which one)
- entry rule, exit rule, holding horizon, session window, flat by 15:08
  CT (or the product's earlier close), and the exact data fields the
  rule reads with their availability timestamp (for example, a report's
  release time, never a settlement published after the close)
- order type: market orders; any limit order is modelled at
  trade-through fills
- sizing under the rule Task 5 sets
- every parameter value fixed. If a member needs a grid, list every
  point; each point counts as a trial.
- expected trades per day and holding time, with the source or
  reasoning, and the check against the program's trade-rate floor
- falsification condition: what result on the confirmation window
  counts against the member
- the Topstep check: flatten, order type, prohibited-pattern check, *
  restriction, news rule, position limit. A member that fails any of
  these is excluded, with the reason logged, not quietly dropped.
- data needed (products, schema, window)

The core port set: in addition to its new members, each cluster
carries a small fixed set of MES families as a baseline, the same set
for every product, chosen by the lead in Task 5 (D6) and counted in N.
Do not port all 58 D.1f members to every product.

Budget per cluster: at most 15 members including the core port set,
unless the lead logs why the research supports more. A catalog is not
better for being longer; every member costs power at confirmation.

The lead then has CatalogAssembler-SonnetMed (worker-medium, sonnet)
merge the eight files into reports/stage_e0_catalog.md and .json, with a
count per cluster, per product and in total, and a projected cumulative
N for the program. The assembler does not edit any entry.

============================================================
TASK 5: THE STAGE E PROGRAM DESIGN DRAFT (LEAD)
============================================================

The lead writes docs/STAGE_E_DESIGN.md, marked DRAFT at the top. It
answers each design question below with a proposed rule, the reasoning,
the alternatives considered, and what the user must decide. It does not
freeze anything.

- D1 Universe and liquidity floor: a rule, stated before looking at
  which products it drops, using Task 1's public volume and open
  interest and Task 2's coverage proxy. The list of products kept and
  dropped follows from the rule.
- D2 Trading vehicle per exposure, and the sizing rule. Default to
  evaluate: size each member so its expected daily P&L risk matches MES
  at 2 micros, with the sizing inputs measured on the research window
  only, within Topstep's position limits.
- D3 Epsilon per product: the dollar bar ($85 per day at 50K, from
  D.1e) converted to each product's ticks at its vehicle and size, and
  how Stage E.2 re-derives the funding bar through the funnel simulator
  with each product's measured research-window P&L distribution.
- D4 Windows and holdouts, per product: the default to evaluate is MES's
  calendar structure (screening on the research window 2025-04-01 to
  2026-06-21; confirmation from a start date S set by a start rule
  through 2024-02-29; embargo March 2024; holdout-2 2024-04-01 to
  2025-03-31 sealed on arrival; holdout-1 from 2026-06-22), so that
  cross-product members see aligned windows. Handle products with short
  histories (micros listed after 2019) with a per-product start rule and
  a power check.
- D5 Multiple testing: Holm within each cluster's confirmation list;
  whether the program splits alpha across clusters, and how; the
  program-level accounting (cumulative N, DSR at N, PBO) reported beside
  every result.
- D6 The core port set of MES families, and why those.
- D7 Stage E null criteria: a draft docs/NULL_CRITERIA_E.md generalizing
  docs/NULL_CRITERIA.md to clusters and products, including the
  statement wording and the claims the program may not make.
- D8 Cost model per product: Topstep commissions from Task 1, and a
  slippage model calibrated on the Task 2 sample, with the calibration
  rule stated before any sample is bought.
- D9 The Topstep constraint set, confirmed from Task 1, as it will be
  encoded in the harness: flatten times per product, trade-through limit
  fills, the program-wide trade-rate and holding-time floor, *
  restrictions, the news rule, position limits and weightings.
- D10 The calendar: every product needs a CME calendar for 2019 to 2026.
  Record the carried item from D.1f: data/cme_calendar.py lists
  2024-07-04 as a full closure where CME gives a 12:00 CT halt, and no
  2024 entry after 2024-02-29 has been checked against bars. Grains and
  livestock need their own session tables.
- D11 What Stage E.2 must build: per-product rules in the rules engine
  (the 50K XFA with per-product limits; 100K, 150K and the Daily Loss
  Limit option stay out of scope until an edge exists), per-product
  cost models and calendars, multi-product bar builds, cross-product
  alignment, and the sealing path for every product.
- D12 Session plan: the sequence E.1 (freeze and purchase), E.2 (build),
  then one screening and one confirmation session per cluster, ordered
  by distance from MES's drivers (energy and metals first, then rates,
  FX and agriculture, then crypto, equity-index siblings last), with an
  ETA and a rough usage estimate per session.
- D13 Spend plan: the quoted total from Task 2, the proposed caps per
  session, and the note that data/config.py's SHARED_ACCOUNT_CAP_USD
  ($120.00, with $91.59 spent) must be raised by the user before E.1 can
  buy. Databento credit left is about $33.
- D14 Carried items from D.1f: the two failing calendar-build tests
  (tests/test_d1f_calendar_build.py) and the 2024-07-04 entry, with the
  stage that fixes each.

============================================================
TASK 6: INDEPENDENT REVIEW (FABLE XHIGH)
============================================================

CatalogAuditor-FableXHigh (worker-xhigh, fable) did not write any of the
work it reviews. It reads the catalog, the design draft, the research
logs and the Topstep facts, and writes reports/stage_e0_review.md with a
finding per item graded BLOCKING, SHOULD FIX, or NOTE:
- look-ahead in any rule: a field read before it is published, a
  settlement or report used before its timestamp
- Topstep conflicts: a member that depends on a prohibited pattern, a
  news restriction, a * restriction, or a fill better than trade-through
- misread sources: re-read at least 15 logged passages chosen across all
  clusters, including every numeric claim a member rests on
- duplicate mechanisms across clusters, and ports that are not what the
  MES family was
- design choices D2, D3, D4 and D5, argued adversarially
- anything in the catalog that could not have been written without
  having seen price data

============================================================
TASK 7: THE C6 CLOSURE DECISION (LEAD)
============================================================

Add an entry to docs/DECISIONS.md, dated 2026-09-23 (the user's decision
in the planning chat): C6, passive execution, is closed as non-deployable
on the XFA, and Stage D.1g will not run. Reasons, each with its Topstep
source: TopstepX fills limit orders only on trade-through, which is the
fill model D.1f already applied to C-H4 (UCB95 -177.18 net ticks per
micro per day, 90,418 trips); and any edge from better-than-trade-through
fills would depend on behaviour Topstep prohibits ("Making hundreds of
rapid trades to take advantage of preferential queue position in SIM").
State plainly that this is a scope decision, not a null under
docs/NULL_CRITERIA.md: C6 was not tested at queue-position fills, and no
C6 null statement exists. Update docs/STAGES.md: D.1g not run, with a
pointer to the decision, and a Stage E outline (E.0 to E.2, then the
cluster sessions) marked planned.

============================================================
TASK 8: RULING ON THE REVIEW (LEAD)
============================================================

For every BLOCKING and SHOULD FIX finding: fix the catalog entry or the
design, or keep it with a written reason. Record each ruling in
reports/stage_e0_review_rulings.md. A member with an unresolved BLOCKING
finding is marked excluded in the catalog, with the finding's number.
Do not re-run the review.

============================================================
DELEGATION PLAN (the lead executes this; it does not do worker tasks)
============================================================

| Task | Owner | Model / effort | Parallel? | Why this tier |
|---|---|---|---|---|
| 0 Startup, ETA, STATE | lead | opus max | - | gates the session |
| 1 Topstep facts | TopstepFacts-SonnetMed | sonnet medium | parallel with 1b, 2 | complex extraction, verbatim, no conclusions |
| 1b Liquidity census | LiquidityCensus-SonnetMed | sonnet medium | parallel with 1, 2 | complex extraction from public pages |
| 2 Quote module | QuoteCoder-OpusHigh | opus high | parallel with 1, 1b | coding against the spend gate |
| 2 Quote run | lead runs the module | - | after the module's test passes | spend-adjacent, the lead watches it |
| 3 Partition | lead | opus max | before dispatch | judgment: non-overlapping regions |
| 3 Research K1-K8 | ClusterReader-K#-SonnetMed x8 | sonnet medium | at most 4 at once | pre-filter and verbatim extraction |
| 4 Catalog K1-K8 | CatalogWriter-K#-OpusXHigh x8 | opus xhigh | at most 4 at once, each after its cluster's research | turning mechanisms into testable rules; look-ahead and Topstep checks |
| 4 Assembly | CatalogAssembler-SonnetMed | sonnet medium | after all 8 | merging and counting, no edits |
| 5 Design draft | lead | opus max | alongside Task 4 where inputs allow | the judgment this session exists for |
| 6 Independent review | CatalogAuditor-FableXHigh | fable xhigh | after 4 and 5 | a second model on a declaration |
| 7 C6 decision, STAGES.md | lead | opus max | any time | wording must stay within what was tested |
| 8 Rulings | lead | opus max | after 6 | - |
| Entry, Session cost | lead | opus max | last | - |

At most 4 workers at once across all tasks. Workers write files and
return paths, never large pastes. Name workers exactly as above.

============================================================
COMPUTE AND UNATTENDED RUNNING
============================================================

This session is web-bound and light on CPU. CLAUDE.md's limits still
apply: at most 4 concurrent workers, resumable through the STATE file,
nothing heavy in the AiTrader collector window. If the session is
interrupted, resume from the STATE file; do not redo a finished task or
re-read a logged source.

============================================================
WHAT NOT TO DO
============================================================

- No purchase, no data download for any product, no bar-level data of
  any kind, no chart or summary of prices. Quotes only, at $0.00.
- No change to SHARED_ACCOUNT_CAP_USD or any existing cap.
- No read of MES bars, holdout-1 or holdout-2.
- No edit to docs/NULL_CRITERIA.md or the D.1f confirmation list.
- No freeze, hash, registration or commit. REGISTRATION.md stays 0 bytes.
- No catalog member written from memory instead of a logged source or a
  stated line of reasoning.
- No member that relies on fills better than trade-through, queue
  position, or any pattern Topstep prohibits.
- No social-media or sentiment signal.
- No unlogged rejection: every source considered gets its line.

============================================================
DELIVERABLE
============================================================

A dated progress.md entry for Stage E.0, containing:
- guardrail evidence (both holdouts at start and end, REGISTRATION.md,
  the $0.00 session caps, no data files for new products on disk)
- the Topstep facts that changed or could not be confirmed, against the
  constraints listed in this prompt
- the quotes table per cluster and the universe total, with the
  calibration-sample costs
- the research summary per cluster: sources considered, passed,
  full-text read, [unverified] count, and the strongest mechanisms found
- the catalog summary: members per cluster, new against ported, members
  excluded and why, and the projected program N
- the design draft's proposed answers to D1 to D14, and the list of
  decisions the user must make before Stage E.1
- the review findings and the rulings
- the C6 decision and the STAGES.md update
- the delegation record, and any deviation from the plan with its reason
- the open choices the lead made on its own, with reasons
- the Session cost section and the final ETA table, per CLAUDE.md

Also one line in docs/STAGES.md recording the session and its headline.

END PROMPT
