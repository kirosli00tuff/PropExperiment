# Stage E.32b brief: family readers (F2), shared by all eight

Written by the lead (session 2, Opus 5.5 max) on 2026-10-28 at about 22:50 PDT. Read
reports/stage_e32b_briefs/READER_RULES.md first (it binds you), then the part "All readers" below and your own family
section, then the frozen spec reports/stage_e32b_ranking_spec.md sections 0, 1 and 3 only (they say what your facts
feed: D1 spread, D2 a and b, D3 s1 s2 s3, D4 L and Sat, D6). You report facts and sources. You never score, rank or say
what a fact would score.

## All readers

Objective: for every code in your family, gather sourced facts on topics T1 to T7 below, reusing E.28's and E.20's
sourced facts first, and write them to F2_<family>.json (schema below) and F2_<family>.md.

Inputs (read by section: grep, jq, line ranges; never load a large file whole):
- reports/stage_e28_briefs/A1_<family>.json and .md: E.28's sourced facts for your codes. Reuse with citation (file and
  JSON field path).
- reports/stage_e20_briefs/product_<ROOT>.json and .md where one exists for your codes (`ls reports/stage_e20_briefs/`).
- reports/stage_e28_briefs/C2_*.md (E.28's method readers' notes): grep for your products or underlyings for directional
  evidence pointers.
- The RETURN files reports/E.29_RETURN.md, reports/E.31_RETURN.md and reports/E.33c_RETURN.md: the program's own earlier
  measurements (for example a measured median spread) count as sources; cite file and line. Read no other E.31 to E.33
  file.
- Your family's pointers below: the lead's memory, unverified. Verify or discard each; never cite a pointer as a source.

Topics, per code. Where a fact concerns the underlying or the leader, record it once and list every code it applies to.
- T1 Spread and touch: the median main-session bid-ask spread in ticks, and the median displayed size at the best bid and
  ask (contracts), each with window and session. Sources: published studies, CME liquidity reports or Market Liquidity
  pages via Wayback (never cmegroup.com live), CFTC or vendor reports, E.20 and E.28 facts, program RETURN files. If
  none is found, say so (the spec then sets S = 1 tick, marked unknown).
- T2 Crowding:
  - T2a a published automated-trading or HFT share of volume for the product, its leader or its CME product group: the
    figure, its window, its scope (most specific and post-2012 first; list older figures too).
  - T2b CME market-maker, lead market-maker or volume-incentive programs for the product's outright futures in force at
    any time 2021 to 2026: program name, products covered, dates. Sources: CFTC self-certification filings (cftc.gov),
    CME notices via Wayback, the Federal Register. Record which searches found nothing; absence is "not found", never
    "none exists" unless a source says so.
  - T2c a published retail share of volume, if any.
- T3 Structural relationships: economic spreads (crush, crack, cross-asset pairs), calendar spreads, mini or micro to
  full-size pairs, implied spread books. For each: the members; the type (economic, mechanical or arbitrage-tight,
  calendar); any documented intraday cointegration, mean reversion or lead-lag with its horizon (minute-level or daily),
  data period and quote.
- T4 Scheduled events: the releases that move the product (name, day and time with zone, frequency), and the evidence on
  absorption speed: does the price effect keep moving the mean for 5 minutes or more after the release (drift, slow
  adjustment), or is it absorbed within seconds to a few minutes? Quote the study's statement with its horizon and data
  period. Record volatility-only effects as volatility-only.
- T5 Satellite status: each code's settlement basis (physical delivery; financial against which price: a sibling's
  settlement price, an index, a fixing), from contract specifications or rulebook chapters (Wayback or CFTC filings);
  and any information-share or price-discovery study on the product or its underlying with the shares (which market
  leads, by how much, period).
- T6 Intraday directional evidence at horizons from 5 minutes to the session: per study, the authors, year, title, venue
  (peer-reviewed journal, working paper, thesis, practitioner), product(s), horizon(s), data period, in or out of
  sample, net of costs or not, the finding (sign, size, significance), a verbatim quote and the verified level
  (full_text, abstract, snippet). Include null and negative results (no predictability, gone after costs, arbitraged
  away) with the same detail. Contemporaneous order flow (same-interval order flow explaining same-interval returns)
  does not count, nor does predictability only under 5 minutes: if you meet such an item, record it with
  "excluded: <reason>", but do not search for them.
- T7 Session structure: Globex session times, daily pauses, the main session, and any documented handoff effect (the day
  session's open after an overnight break or pause, a regional open or close, the settlement window, fixings), with
  quote and horizon.
- F1 changes: if you meet a fact that changes one in A1_<family>.json (listing, fees, limits, sessions, ADV), record the
  new value with its source and the old value with its field path. Do not re-verify unchanged E.28 facts.

Budgets and stopping:
- WebSearch: at most your family's budget below. Per topic and underlying, stop after 2 consecutive queries that add
  nothing new, or after 10 queries. At most 12 full-text reads for T6 per family.
- Shared sources (one owner reads each; the other readers do not fetch it):
  - CFTC automated-trading reports (Haynes and Roberts 2015 "Automated Trading in Futures Markets", its updates, and any
    later CFTC Office of the Chief Economist series on automated trading by product): RatesReader reads them and writes
    one item per product group and per named product to reports/stage_e32b_briefs/F2_shared_cftc_automation.json (same
    file schema, family "shared_cftc"). Other readers record only other sources on automated or HFT shares.
  - Baltussen, van Bekkum and Da (2021, Journal of Financial Economics) "Hedging demand and market intraday momentum",
    saved at reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md: EquityReader reads it and writes one
    item per asset class (equity, bonds, commodities, currencies) plus any product-level rows it gives for the
    underlyings of the eight families, to reports/stage_e32b_briefs/F2_shared_baltussen.json (same schema, family
    "shared_baltussen"). Other readers do not re-read it.
- Soft time limit: aim to finish within about 100 minutes. At 120 minutes, stop searching, write what you have and list
  the gaps.
- A GateGuard hook may deny your first Bash command or your first Write or Edit of a file and ask for facts (the request,
  what the command does, who uses the file). State the facts it asks for in your reply and retry the same call.

Output 1, reports/stage_e32b_briefs/F2_<family>.json, rewritten after each code or underlying is finished:

    {
      "family": "...", "worker": "<Role>-OpusHigh", "codes": [...],
      "started_pdt": "...", "finished_pdt": "... or null while running",
      "websearch_calls": 0, "fulltext_reads_t6": 0,
      "notices": [ {"time_pdt": "...", "text": "..."} ],
      "items": [ {
        "id": "<ROOT>-<n>",
        "codes": ["..."],
        "topic": "T1 | T2a | T2b | T2c | T3 | T4 | T5 | T6 | T7 | F1",
        "field": "median_spread_ticks | touch_size | auto_share_pct | mm_program | retail_share | relationship | event |
                  settlement_basis | info_share | directional_study | session_handoff | changed_fact | ...",
        "value": "number or short string, null if not found",
        "scope": "product | leader | sibling | underlying | product_group | asset_class | futures_broad | other_venue",
        "window": "data period, or dates in force",
        "detail": "what the topic asks for: horizon, type, absorption, in or out of sample, net of costs, finding,
                   members, venue type ...",
        "quote": "verbatim from the saved full text (or abstract or snippet, as 'verified' says)",
        "source": {"file": "saved page path or reused fact file", "field": "JSON path if reused",
                   "url": "...", "fetched_utc": "...", "sha256": "..."},
        "verified": "full_text | abstract | snippet | reused",
        "pointer": false,
        "negative": false
      } ],
      "searched_not_found": [ {"codes": ["..."], "topic": "...", "queries": ["..."], "note": "..."} ],
      "per_code": { "<CODE>": {
        "median_spread_ticks": null, "spread_item": null, "touch_size": null, "touch_item": null,
        "settlement_basis": "...", "settlement_item": "...", "leader": "<CODE>", "notes": "..." } },
      "gaps": ["..."]
    }

Output 2, reports/stage_e32b_briefs/F2_<family>.md: per code (or per underlying for shared facts) the key facts with
their item ids, then searched-not-found and gaps; at most about 300 lines.

Pages: reports/stage_e32b_briefs/pages/<ROOT>/ with log.tsv (READER_RULES). Helpers: reports/stage_e32b_briefs/work/<ROOT>/.

Boundaries: no scoring. No Databento facts (MBO start dates, prices: the DataAccess worker owns them). No firm rules
(the FirmRules worker owns them). Do not read or write other families' folders or outputs, except the shared file you own.
No market data, no E.31 to E.33 file except their RETURN files, no keys, no git writes, no spawning.

Return: the output paths; a summary of at most 200 words (per code: spread found or not, settlement basis, the best
directional-evidence level found, notable negatives); what you could not finish, and why.

## Families

### crude: ROOT CRUDE, codes MCL QM CL, WebSearch budget 60
Pointers (unverified): CL is the leader; MCL and QM are smaller contracts on the same underlying (check whether they are
financially settled off CL's settlement). Events: EIA Weekly Petroleum Status Report (Wednesdays 10:30 ET), API weekly
(Tuesdays 16:30 ET), OPEC+ meetings; studies of the price adjustment to EIA inventory announcements in crude futures.
Relationships: crack spread (RB, HO), Brent-WTI, calendar spreads. NYMEX settlement window around 14:28-14:30 ET.
Intraday momentum or reversal studies on crude oil futures.

### natgas: ROOT NATGAS, codes MNG QG NG, WebSearch budget 60
Pointers (unverified): NG is the leader. EIA Weekly Natural Gas Storage Report (Thursdays 10:30 ET) and studies of its
price adjustment; weather-model updates as a recurring information flow (pointer class unless studied); settlement
window around 14:28-14:30 ET; calendar spreads; intraday momentum on natural gas futures.

### metals: ROOT METALS, codes MGC GC SIL SI MHG HG, WebSearch budget 70
Pointers (unverified): GC, SI and HG lead their underlyings. LBMA gold and silver price auctions (London) and the
COMEX settlement window; US macro releases (employment, CPI, FOMC) and gold's intraday response; the gold-silver
relation; copper price discovery against Shanghai (SHFE) and the LME (information-share studies); intraday momentum on
precious-metals futures.

### grains: ROOT GRAINS, codes MZC MZS MZW MZL MZM XC XK XW ZC ZS ZW ZL ZM, WebSearch budget 80
Pointers (unverified): ZC, ZS, ZW, ZL and ZM lead their underlyings; the micro and mini grains are smaller contracts on
the same underlyings (check their settlement: physical, or financial off the full-size settlement). USDA reports (WASDE,
Crop Production, Grain Stocks, Prospective Plantings, Acreage at 12:00 ET; Crop Progress Mondays 16:00 ET; Export Sales
Thursdays 08:30 ET) and studies of grain futures' intraday response and absorption speed; the soybean crush (ZS against
ZM and ZL); the daily pause and the day-session reopen (CT times). reports/stage_e32_inputs/planner_research_soy_complex.md
and reports/stage_e31_inputs/planner_research_notes.md are planner pointers: verify each item you use against full text
before citing it. ZM's directional route is closed (E.33c); still record ZM's facts.

### rates: ROOT RATES, codes 2YY 5YY 10Y 30Y ZT ZF ZN ZB, WebSearch budget 70 (includes the CFTC shared source)
Pointers (unverified): ZN leads the 10-year; the micro yield futures are yield-quoted and cash-settled (check against
what: a yield fixing or a futures settlement). Macro announcements and Treasury futures (Fleming and Remolona 1999 and
later work on adjustment within minutes; drift after announcements); Treasury auctions; FOMC; information share of
Treasury futures against the cash market (BrokerTec). You own the CFTC automated-trading shared source (above).

### equity: ROOT EQUITY, codes M2K RTY MYM YM MNQ, plus NQ leader facts only, WebSearch budget 60 (includes Baltussen)
NQ is excluded from scoring (V49), but MNQ's leader facts come from NQ: record NQ facts with codes ["MNQ","NQ"].
Pointers (unverified): the cash open 09:30 ET and close 16:00 ET (closing-auction imbalances); market intraday momentum
(Gao, Han, Li and Zhou 2018 on SPY; Baltussen et al. 2021 on futures); macro releases at 08:30 and 10:00 ET; FOMC;
E-mini against ETF price discovery; Russell 2000 and Dow futures specifics. You own the Baltussen shared source (above).

### fx: ROOT FX, codes M6E 6E M6A 6A, WebSearch budget 60
Pointers (unverified): futures against spot (EBS, Reuters) price discovery for EUR/USD and AUD/USD (information-share
studies); the WM/Reuters 16:00 London fix and its documented pre- and post-fix patterns; regional opens (Tokyo, London,
New York); ECB and RBA decisions and US releases; intraday momentum in FX (Elaut, Froemmel and Lampaert 2018).

### crypto: ROOT CRYPTO, codes MET ETH MBT BTC, WebSearch budget 60
Pointers (unverified): CME bitcoin and ether futures settle to CME CF reference rates (check); spot exchanges against
CME futures price discovery (information-share studies with conflicting results: record each with its share and
period); the weekend gap and the Sunday reopen; US macro releases; intraday momentum or reversal in bitcoin; micro
against standard contracts.
