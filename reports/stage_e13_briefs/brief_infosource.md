# Brief: InfoSource-OpusHigh (Stage E.13 Task 3: new information sources for intraday signals)

Read reports/stage_e13_briefs/research_rules.md first and follow it. Your pages folder:
reports/stage_e13_briefs/pages/InfoSource/.

## Objective (one)
Scope information sources the program has never used for intraday signals, and find the two or three with
the best published evidence of intraday or one-day predictability in the program's products AND the best fit
to the program's trading constraints.

## The program's constraints (fixed)
- Venue: Topstep XFA via its API; every position flat by 15:08 CT (flatten time F_X; grains 13:18, livestock
  13:03); one-minute bars; holds of 60 minutes or longer at 1 to 3 decision times per product per session in
  ML route v2 (docs/STAGE_E_ML_V2_DESIGN.md lines 263-300). Single-rule K-clusters used holds of minutes to a
  session. A source whose information arrives after the last decision time of the day can only be used the
  next day.
- The 28 products and their cost wall: docs/STAGE_E_ML_V2_DESIGN.md lines 143-172 (RT_X in ticks and $).
- Data: free or cheap sources only; Databento GLBX.MDP3 one-minute bars for prices. No tick data.

## What the program has already used (check before calling anything new)
- docs/STAGE_E_ML_V2_DESIGN.md lines 435-550 (V2.3: the signal library: K1-K9 member families and G1-G19).
- The cluster catalogs docs/stage_e0_catalog_K1.md ... K8.md (grep for the source names: COT, EIA, storage,
  WPSR, API, WASDE, USDA, crop, weather, degree day, VIX, VXN, OVX, GVZ, surprise, consensus, options, skew,
  put/call, gamma) and reports/stage_e10_catalog_K9.md (sections 2 Excluded, 3 Beyond budget, 4 Routed, and
  the two withdrawn VIX drafts in Appendices A-B). Record for each candidate: never used / used as a calendar
  flag only (release time, no content) / used with content (which member).
- Stage results to respect (do not re-test anything): reports/E.12_RETURN.md lines 7-32 (Gate 0 failed:
  price-based signals on 28 futures show no edge after costs; V24 in docs/DECISIONS.md lines 446-467).

## Candidates (add others you find with evidence)
1. CFTC Commitments of Traders positioning (legacy, disaggregated, TFF).
2. EIA weekly natural gas storage surprise against consensus; EIA WPSR crude/product inventory surprise
   against consensus (and the API Tuesday report).
3. Weather forecast revisions: heating/cooling degree days (GFS/ECMWF/NOAA CPC 6-10 and 8-14 day outlooks)
   for NG; precipitation/temperature for grains.
4. USDA report surprises: WASDE, Crop Progress, Grain Stocks, Prospective Plantings, Acreage, Hogs and Pigs,
   Cattle on Feed, against analyst consensus.
5. Implied-volatility indices: CBOE VIX, VIX term structure (VIX/VIX3M, VIX futures curve), VXN, OVX, GVZ,
   and their changes; CME CVOL if reachable.
6. Economic-surprise indices (Citi, Bloomberg ECO, or a free reconstruction from consensus vs actual).
7. Options-market positioning: put/call ratios, dealer gamma exposure, skew (CBOE SKEW).
8. Others with evidence, for example: Treasury auction results (tails), Fed communications text, news
   sentiment (note only: the sibling AiTrader project tests news judgment; do not research it), order-flow
   data that one-minute OHLCV can carry (volume imbalance; note only).

## Per candidate (one block each, every field sourced)
- What it measures; release day and time (CT); when it is AVAILABLE to a retail system (and its lag).
- Source(s): free or paid, cost, terms of use (automated access, redistribution), API or file format.
- History length available (start year), and whether a consensus/expectation series exists with history.
- Published evidence for intraday or one-day predictability in the program's products: the paper or record,
  its sample, the effect size (in ticks, bp or Sharpe), whether it survives costs, and the record AFTER its
  publication (later papers, replications, out-of-sample tests). Say plainly when evidence is only daily or
  weekly, or only for other assets.
- Already used by the program? (never / calendar flag only / with content: which member).
- Fit with flat-by-15:08 trading at holds of 60 minutes or more: which products, which decision times, how
  many events a year (and so, at a plausible per-event Sharpe, the years needed for t = 3: t ~ Sharpe x
  sqrt(years); per-event figures convert by the event count).
- A one-line verdict: strong / moderate / weak / none, for evidence and for fit, separately.

## Output
reports/stage_e13_info_sources.md: a summary table (candidate | measures | available at (CT) | source and
cost | history | evidence (post-publication) | used by program | fit | verdict), the per-candidate blocks, a
source list (key I-01... | URL | fetched | page date | verbatim quote), gaps, and a closing section naming the
two or three sources with the best evidence and fit, each with a sketch of the hypothesis the next stage
could pre-register (product, event, signal, decision time, hold, expected events a year), in at most 300
words. Ranking criterion: post-publication evidence first, fit second, cost third. Never rank by ease.

## Stopping rule
Done when every listed candidate has a block (fields marked UNSOURCED where they cannot be sourced), after at
least 3 logged queries per candidate on the evidence field with the last 2 adding nothing new. Budget: at
most 150 WebSearch calls.

## Boundaries
No market data, no Databento call, no account sign-ups or API keys requested. Do not research AiTrader, prop
firms, brokers or trend/carry (other workers own those).
