# Stage E.25 shared brief (R0): every reader starts here

Written by the E.25 lead, 2026-10-18 01:45 PDT. Stage prompt: docs/prompts/STAGE_E.25.md (research only).
Your spawn message names your reader id (R1..R20 or RD1..RD10), your one objective and any shared
assignment. Everything else is in this file. Read it whole once; read every other file by section.

## 1. Why this stage exists (one paragraph)

The user wants a strategy that can pass a futures prop-firm evaluation and be paid. 538 registered or
screened trials found none. The program's literature passes (E.13 and E.20: SSRN, arXiv, Quantpedia,
157 sized evidence rows) covered published intraday effects on 1-minute bars; none cleared the cost
hurdle below. This stage reads what those passes did not (0DTE and dealer hedging, order flow, news,
live audited records, prop firms' own outcome data, practitioner work, communities as pointers), and
re-digs the sources they did read, deeper. Output is a ranked shortlist of hypotheses for the user to
decide on. Nothing is tested here.

## 2. The cost hurdle (V31 gate, V38 hurdle: published gross per trade > 1.5 x the D8 round trip)

D8 round trip (RT) = commission + entry and exit slippage, day session, 1 lot, frozen in
reports/stage_e2a_costs.md (per-bucket detail there; grep it). Hurdle = 1.5 x RT.

| Vehicle | Tick | Tick $ | RT ticks | RT $ | Hurdle ticks | Hurdle $ | Hurdle in underlying units |
|---|---|---|---|---|---|---|---|
| MNQ (NQ x 0.1) | 0.25 pt | 0.50 | 4.119 | 2.06 | 6.18 | 3.09 | 1.54 NQ index points |
| MES (ES x 0.1) | 0.25 pt | 1.25 | about 2.0 (Stage D model: $1.22 commission + 2 x about 0.53 tick half-spread; not in the D8 table) | about 2.53 | about 3.0 | about 3.80 | about 0.76 ES points |
| M2K (RTY x 0.1) | 0.10 pt | 0.50 | 3.954 | 1.98 | 5.93 | 2.97 | 0.59 RTY points |
| MYM (YM x 0.1) | 1.0 pt | 0.50 | 3.983 | 1.99 | 5.97 | 2.99 | 5.97 YM points |
| MCL | 0.01 | 1.00 | 3.167 | 3.17 | 4.75 | 4.75 | $0.0475/bbl |
| MGC | 0.10 | 1.00 | 4.086 | 4.09 | 6.13 | 6.13 | $0.61/oz |
| MHG | 0.0005 | 1.25 | 3.701 | 4.63 | 5.55 | 6.94 | $0.0028/lb |
| MNG | 0.001 | 1.00 | 5.350 | 5.35 | 8.03 | 8.03 | $0.008/MMBtu |
| M6E | 0.0001 | 1.25 | 1.922 | 2.40 | 2.88 | 3.60 | 0.00029 EURUSD |
| NQ | 0.25 | 5.00 | 3.110 | 15.55 | 4.67 | 23.33 | 1.17 NQ points |
| ZN | 1/64 | 15.625 | 1.168 | 18.25 | 1.75 | 27.38 | 1.75/64 of a point |
| CL | 0.01 | 10.00 | 1.728 | 17.28 | 2.59 | 25.92 | $0.026/bbl |
| GC | 0.10 | 10.00 | 4.351 | 43.51 | 6.53 | 65.27 | $0.65/oz |

In basis points at recent prices (state the price level you use; e.g. NQ about 21,000 to 25,000, ES
about 5,500 to 6,700 in 2025-2026): MNQ RT is about 0.4 bp of notional, the MNQ hurdle about 0.6 bp;
the MES hurdle about 1.2 to 1.4 bp. Convert every published effect: (effect in bp) x (price) / 10,000 =
index points; points / tick size = ticks. Show the conversion. Effects published in percent of
the underlying (SPY, SPX, QQQ) convert the same way. A net-of-cost figure published at a different cost
assumption: report the gross and the paper's cost assumption. You give the inputs; the lead computes
the ratios.

## 3. Prop constraints (what "prop-compatible" means here)

Topstep (venue of record; reports/E.19_RETURN.md and reports/stage_e19_rules.md, 214 sourced rules):
- Flat before 15:10 CT (auto-flatten about 10 s before); trading day 17:00-15:10 CT; no overnight.
- Optional daily loss limit (DLL) $1,000 / $2,000 / $3,000 (50K/100K/150K), chosen at purchase;
  end-of-day trailing max loss $2,000 / $3,000 / $4,500.
- Combine consistency: best day below 55% of total profit; payout paths: Standard (5 winning days of
  at least $150) or Consistency (3 days, best day at most 40%); 90% split.
- Automation allowed via the TopstepX/ProjectX API ($14.50/month), no HFT, no VPS; no scalping that
  exploits SIM fills; news trading allowed but NOT at full maximum position size into a scheduled major
  release (P06). Cross-account hedging banned.
- E.19: at zero edge the funnel loses money at every size; break-even net Sharpe about 0 (50K) to 0.86
  (150K). V33: no Combine is bought before a strategy passes a registered test with net Sharpe about 0.5.
Other firms (E.13, E.21; for R9 to update): The Trading Pit Classic permitted multi-day automation
(possibly no longer sold); Phidias Premium human-in-the-loop only; PropEd allows overnight holds but
grants no automation publicly; Elite Trader Funding unclear; NinjaTrader and Tradovate exclude BC
(the user is in British Columbia, Canada). V39: manual or semi-automated execution is acceptable.

## 4. Data the program owns (no data is read in this stage)

- 1-minute OHLCV bars only (Databento GLBX.MDP3 ohlcv-1m). No order book, no trades, no options.
  Exceptions: D8's mbp-1 on five trade dates (cost calibration) and two MES mbp-10 days.
- 17 roots with 2010-07..2024-02 (NG NQ ZN 6E GC ZC ZT ZF ZB UB TN CL ZL ZS RTY HE LE); 27 price
  paths 2019-05..2024-02; MES 2019-05..2025-03 (holdout-2 sealed).
- Research window: trade dates 2025-04-01..2026-06-19, 45 CME contracts (equity, rates, FX, energy,
  metals, grains, livestock micros and full-size). The Stage E cluster screens (E.3-E.9) and D.1 read it
  for their own members; a NEW hypothesis's outcome on it has never been computed. It lies inside the
  0DTE era (daily SPX expiries since 2022-05; Mon-Fri). Holdout-1 (from 2026-06-22) is not owned.
- Owned side data: SqueezeMetrics DIX/GEX daily CSV (E.14 copy, terms cleared in E.20), Cboe VXN and
  VIX daily history (free), release calendars (FOMC, CPI, NFP, PPI, GDP, ISM; 2010-2026), EIA/WASDE
  calendars. No news feed, no options data, no order-book data.
- Databento spend: none in this stage. You may read Databento's public pricing pages and quote
  published prices; never request a quote, never call the API.

## 5. What was already tested (do not re-propose without saying so)

Full index (one row per member, ids to cite): reports/stage_e25_briefs/r0_mechanism_index.md
(written by about 02:15; grep it; if it is not there yet when you write your overlap column, write
"overlap unchecked" and the lead checks). Sized evidence already in E.20 (157 rows):
reports/stage_e25_briefs/r0_e20_evidence_index.md; sources already read by E.10/E.13/E.20 (253
groups): reports/stage_e25_briefs/r0_prior_sources.md. Raw inventory tables:
reports/stage_e23_briefs/inventory/{K1..K8,CDE,H6}.md. Family-level summary:
- D.1-D.1f (MES): 23 hypotheses in 5 families, C-H4 reversal with passive fills, Family F data-native,
  coarser-bar sweep 5/15/30/60 min, 58 Tier A confirmations (incl. Family H) on MES: no pass.
- K1 equity index (E.7, MNQ/M2K/MYM): cp1 morning-sign to last-half-hour, cp3, VXN band, VWAP member
  (K1-vwap), opening and closing windows. K2 rates (44 trials: auctions, releases, settlement). K3 FX
  (London fix reversal K3-ldnrev-01, hedging flows). K4 energy (NG storage pre-release K4-ngpre-01,
  WPSR). K5 metals (FOMC gold K5-fomc-01, PM fix). K6 ags/livestock (limit continuation, WASDE).
  K7 bitcoin. K8 cross-market (flight to quality MGC with MES, oil to CAD 6C with MCL, weekend BTC to MNQ).
- E.12 Gate 0 ML route (273 trials) and E.20 ML search (45 configurations, 17 roots, 4 decision
  times, r_ROD features): FAIL.
- E.13/E.14 C2 GEX-conditioned S&P late-session momentum: stopped at its power rule (not a trial).
- E16 H1-H5: settlement-window momentum, month-end NQ/ZN pair, Treasury auction cycle, next-day
  reversal, combination: all FAIL. C1/C1b NG replication: FAIL.
- E20H6 T1-T3: rest-of-day to last-half-hour momentum on NQ at MNQ cost (Baltussen et al. 2021),
  T2 large-move filter, T3 previous-day GEX < 0: all FAIL (T1 gross 1.25 ticks vs 4.08 cost).
- E.21 multi-day trend (TSMOM-12, blends, turn-of-month): FAIL on Holm; E22-F1 trend book (forward);
  E.23 intraday triggers at 5/20-day holds: no survivor.
- Closed directions (V39-V41): prediction markets, crypto, commodity event drift as a standalone stage,
  ML overlays on trend, the program's own intraday triggers at multi-day holds.

## 6. Source rules and evidence grades

- Evidence: peer-reviewed papers, working papers (SSRN, NBER, arXiv, university repositories), theses,
  official exchange, regulator, prop-firm and vendor pages, audited or broker-verified live records.
  Pointers only (never evidence): blogs, forums, videos, social posts, marketing copy.
- Grade every claim: `peer-reviewed` | `working-paper` | `thesis` | `exchange-regulator` | `firm-page`
  | `vendor` | `live-record-audited` | `live-record-unaudited` | `practitioner-book` | `pointer`.
  Add `[secondary-only]` when you could read only an abstract, snippet or a citing source, and
  `[unverified]` when you could not fetch the text at all.
- Every number you report carries a verbatim quote from the fetched full text with its location
  (page, table, section). Never present a search summary or a snippet as retrieved text.
- Report failures, nulls, decay, after-cost failures and replications that did not hold, not only wins.
- Selection bias: for live records, vendor claims and prop outcome data, state the bias explicitly
  (survivorship, self-selection, marketing, backfill).

## 7. Tools (user addendum 2026-10-18 01:33: use every research tool at full depth)

- Search: WebSearch; Firecrawl `firecrawl_search` (web, `categories` research/pdf/developer/gov);
  Firecrawl paper tools `firecrawl_research_search_papers`, `firecrawl_research_read_paper` (full text),
  `firecrawl_research_related_papers` (citation graph), `firecrawl_research_inspect_paper` (arXiv and
  biomedical indexes); load their schemas with ToolSearch, e.g.
  "select:mcp__claude_ai_Firecrawl__firecrawl_research_search_papers,mcp__claude_ai_Firecrawl__firecrawl_research_read_paper".
- Scholarly APIs: OpenAlex (https://api.openalex.org, polite pool: add `mailto=$OPENALEX_EMAIL`; read
  the value into an environment variable with `export OPENALEX_EMAIL="$(grep '^OPENALEX_EMAIL=' .env |
  cut -d= -f2- | tr -d '\"')"` and never echo or log it; never `source .env`, it holds other keys).
  Use OpenAlex `filter=cites:W...` for forward citations and author ids for authors' later work.
  Semantic Scholar Graph API (https://api.semanticscholar.org/graph/v1): the key in .env is unusable
  (1 character), so call it WITHOUT a key, at most one call every 10 seconds per reader; on a 429
  wait 60 s, retry at most twice, then log "throttled" and use OpenAlex.
- **Update 01:57 PDT (lead):** OpenAlex's free daily budget for this machine's IP ran out at
  01:46-01:47 PDT ("Rate limit exceeded ... Insufficient budget ... resets at midnight UTC", i.e. 17:00
  PDT). Do not call OpenAlex in this stage. Forward citations: OpenCitations
  (`https://api.opencitations.net/index/v2/citations/doi:<DOI>`, free, no key; at most one call per 5 s),
  Crossref metadata (`https://api.crossref.org/works/<DOI>?mailto=$OPENALEX_EMAIL`, polite, one call per
  2 s), Semantic Scholar keyless (as above), Firecrawl `firecrawl_research_related_papers`, and
  "cited by" pages reached through search results. Log which you used.
- Fetch: WebFetch first; on failure `scrapling extract get <url> <file>`, then `scrapling extract fetch
  <url> <file>`; `stealthy-fetch` only where the site's terms allow automated access; Firecrawl
  `firecrawl_scrape` when Scrapling fails. Playwright MCP is ONE shared browser for all readers: use it
  only as a last resort for a JavaScript-rendered page, check that the snapshot's URL is the URL you
  asked for before you save anything, and never close tabs you did not open. R8 and R9 have priority.
- Scripts and scratch files: your own private folder
  /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/37fc9660-82d1-49fd-be83-50b822ab0a5b/scratchpad/<your id>/
  (E.20 lesson: shared script names collided across readers). Run python on downloaded files with
  `python3 -I`.
- Context hygiene: save every page or PDF to disk first, then grep it; only quoted lines enter your
  context. Convert PDFs with `pdftotext -layout` if available, else read the PDF by page ranges.

## 8. Web rules (terms, pacing, budgets)

- Read each site's terms of use (and robots.txt) before any automated fetch from it. Check
  reports/stage_e25_briefs/terms/terms_log.md first: if another E.25 reader already logged that site,
  cite its line; otherwise save the terms page to reports/stage_e25_briefs/terms/<host>_terms.html and
  APPEND one line to terms_log.md: `host | terms URL | UTC | sha256 | ruling (allowed / allowed for
  named pages one at a time / forbidden) | reader id`. If the terms forbid automated access, do not
  fetch content pages from that site; cite it only through search results, and add the host to
  reports/stage_e25_briefs/DO_NOT_COMMIT.txt if you already saved anything from it.
- Never fetch cmegroup.com or any archived copy of it (Wayback included) by automation. SSRN blocks
  automation: use the author's page, NBER, arXiv, RePEc, OpenAlex's open-access URL or a university
  repository. Reddit, X and YouTube: only through search-engine results and pages whose terms allow it;
  no scraping, no transcript download unless the terms allow it.
- Pacing: at most about 2 readers on one domain at once (section 10 keeps the heavy domains apart);
  leave at least 5 seconds between requests to one domain; on a 429 or 403 back off, retry at most
  twice, then log "throttled" or "blocked". A blocked or throttled fetch is a gap in the record, never
  evidence that something does not exist.
- WebSearch budget: 1,500 per session, shared by every worker. At most 45 WebSearch calls per reader
  (Firecrawl search and the scholarly APIs do not count against it). If a WebSearch returns an
  over-budget notice, stop WebSearch at once, write the notice and its time into your log, continue
  with Firecrawl/OpenAlex if they work, and never continue from memory. If Firecrawl reports no
  credits, log it the same way and fall back. Cost or usage notices are informational, not a reason
  to stop early.

## 9. Output (two files, fixed names given in your spawn message)

`reports/stage_e25_briefs/<ID>_<topic>.md` with sections:
1. Answer to your objective in at most 250 words.
2. Candidate hypotheses (zero is a valid answer; say why): one table row each, the JSON fields below.
3. Evidence table: claim | number | verbatim quote | location | source (authors, year, venue, URL) |
   grade | saved path.
4. Negative evidence: nulls, decay, failed replications, after-cost failures, with quotes.
5. Data and cost: what each candidate needs, whether the program owns it (section 4), the published
   price (quoted, with URL and date) and any terms on use.
6. Prop compatibility: flat by 15:10 CT, DLL, P06 news rule, HFT ban, automation; per firm if known.
7. Overlap with tested mechanisms: ids from the index (section 5), with one line on how they differ.
8. Re-dig readers only: earlier verdicts or closures the deeper reading SUPPORTS, WEAKENS or
   OVERTURNS (cite the verdict: stage, trial id or V-decision), each with a quote.
9. Fetch log (url | UTC | sha256 | saved path | status ok/blocked/throttled/terms-forbid | tool),
   terms read, budget notices with times.
10. Unfinished and unverified items.

`reports/stage_e25_briefs/<ID>_<topic>.json`:
```json
{"schema": "stage_e25_reader/1", "reader": "<ID>-<Topic>-OpusHigh", "finished_utc": "",
 "candidates": [{"id": "<ID>-C1", "hypothesis": "", "mechanism": "", "instruments": [],
   "entry_window_ct": "", "hold": "", "trades_per_year": null,
   "best_source": "", "source_url": "", "grade": "", "sample": "", "post_2015_or_oos": "",
   "published_effect": "<as published, with units>", "price_level_used": "",
   "gross_per_trade_points": null, "gross_per_trade_micro_ticks": null, "micro": "",
   "gross_or_net": "gross|net|unknown", "dispersion": "<per-trade sd, t-stat, Sharpe or n as published>",
   "quote": "<verbatim>", "quote_location": "", "decay_evidence": "",
   "data_needed": "", "owned": "yes|no|partial", "data_cost": "<published price, quoted>",
   "research_window_testable": "yes|no|partial", "why": "",
   "prop_notes": "", "overlap_ids": [], "overlap_note": ""}],
 "evidence": [{"claim": "", "number": "", "quote": "", "location": "", "source": "", "url": "",
   "grade": "", "saved_path": "", "sha256": ""}],
 "verdict_checks": [{"verdict": "<stage/trial/V-id>", "effect": "supports|weakens|overturns",
   "quote": "", "source": ""}],
 "fetch_log": [{"url": "", "utc": "", "sha256": "", "path": "", "status": "", "tool": ""}],
 "budget_notices": [], "unfinished": []}
```
Raw pages: `reports/stage_e25_briefs/pages/<ID>/`. Final reply to the lead: the two paths, a summary
of at most 200 words, and anything you could not finish. Aim to return within about 75 minutes;
write your md and json incrementally so nothing is lost if you are stopped.

## 10. Readers, objectives and shared-source owners (one owner per shared source; others cite)

| ID | Objective (one) | Owns / heavy domains |
|---|---|---|
| R1 | 0DTE and dealer gamma, ACADEMIC 2022-2026: same-day SPX options, dealer hedging, gamma and charm flows, their intraday effect on ES/NQ (direction, horizon, size, decay); data each needs | arXiv, NBER, journals, OpenAlex; owns Dim-Eraker-Vilkov, Brogaard-Han-Won, Beckmeyer et al., Adams et al. (2026) |
| R2 | 0DTE second reader: EXCHANGE, VENDOR and PRACTITIONER work (Cboe research, SpotGamma, SqueezeMetrics, MenthorQ, bank notes via press, Cboe/OPRA data prices) with different query families from R1 | cboe.com, vendor sites, databento.com pricing (OPRA) |
| R3 | Order-book and order-flow imbalance on CME futures: horizons and sizes published (Cont-Kukanov-Stoikov 2014 and later), what survives at retail latency (100 ms to seconds) and at 1-30 min, data needed (Databento MBP-1/MBP-10/MBO, published prices) | arXiv q-fin, journals |
| R4 | Volume and trade-side features computable from cheap data (trades, TBBO, volume profile, VWAP families, delta); overlap with K1-vwap and ZA23 stated | databento.com docs (with R2: space requests) |
| R5 | News and headline-driven intraday futures moves: macro headlines, geopolitical and oil, LLM-scored news, Fed speakers; horizons, sizes, decay; timestamped news sources with terms and cost (GDELT, agency press feeds) | gdeltproject.org, agency sites |
| R6 | Scheduled-event microstructure NOT already tested: CPI, NFP, retail sales, PCE, GDP release minutes on NQ, ES, ZN, CL, GC (check the index first; report only untested) | journals; FRB/NY Fed working papers |
| R7 | Live audited track records: Collective2, Darwinex-like, World Cup Trading Championship, broker-audited vendors, CTA short-term programs (BarclayHedge, IASG): any multi-year live intraday futures record net of costs, and its style; record the bias | collective2.com, worldcupchampionships.com, iasg.com, barclayhedge.com |
| R8 | Prop firms' own outcome data: pass rates, payout counts and amounts, payout-to-fee ratios, statements on what styles get paid (Topstep, Apex, Tradeify, Take Profit Trader, MFFU, others); terms first | prop firm stats/blog pages; press |
| R9 | Prop-rules landscape since E.21: firms now allowing automated or semi-automated strategies, overnight holds, news trading; plan-level rules quoted; BC eligibility | prop firm help centres and terms |
| R10 | Practitioner books and authors (Crabel, Raschke, Davey, Williams, Chan, Zarattini and Concretum 2023-2026): which rules were published with OOS or live evidence; which the program tested | owns all Zarattini/Concretum papers; concretumgroup.com |
| R11 | Communities as pointers only (NexusFi, Elite Trader, r/FuturesTrading, r/algotrading, prop-trader interviews on YouTube via search results): recurring ideas, never evidence | search results only |
| R12 | Volatility and regime timing for intraday books (VIX term structure, overnight range, event-day exclusion): does any published filter lift a weak intraday effect above costs | journals, cboe.com (cite R2's terms line) |
| R13 | Cross-market intraday lead-lag not yet tested (check K8 and the index): rates to equity index, dollar to gold, crude to energy equities, with horizons | journals, arXiv |
| RD1-RD10 | Re-dig readers (user addendum): go back to sources E.13/E.20 already cited and read deeper (full text, appendices, forward citations and replications since publication, authors' later work, data/code releases); report which earlier verdicts the deeper reading supports, weakens or overturns. Your spawn message lists your sources. | OpenAlex, S2 (keyless, slow), Firecrawl paper tools |
| R14-R20 | Deep follow-ups the lead assigns after the first wave | as assigned |

Shared sources already on disk (grep, do not refetch): Baltussen, Da, Lammers, Martens (JFE 2021),
reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md; E.20 shared notes
reports/stage_e20_briefs/shared/ (if present) and reports/stage_e20_briefs/pages/; E.13 pages
reports/stage_e13_briefs/pages/; E.13 information-source notes reports/stage_e13_info_sources.md.

## 11. Boundaries

- No market data: do not open anything under data/processed*, data/sealed, data/raw, data/vendor, or
  any .parquet/.dbn/.zst file. Do not open the SqueezeMetrics CSV's values. No outcome is computed.
- No purchase, subscription, quote request, sign-up, login or account creation anywhere. No Databento
  or TopstepX/ProjectX calls, no credentials printed, copied or logged.
- Write only your own outputs (md, json, pages/<ID>/, your scratch folder, and appends to
  terms/terms_log.md and DO_NOT_COMMIT.txt). Stage E.24 runs in parallel: never touch forward/,
  base_rules/, multiday/, tests/, the harness, ledger/, live/, ops/; never run pytest. No commits.
  Do not spawn agents.
- You give facts, conversions and proposals. Ranking, hurdle ratios, power, acceptance and every
  design choice belong to the lead. Do not choose test parameters by looking at any data.
- Times you write: UTC in the fetch log (ISO 8601); PDT elsewhere (`TZ=America/Vancouver date`).
