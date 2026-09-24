# Stage E.0 Task 3 — K5 metals literature log

**This log supersedes the partial run's copy (reports/stage_e0_research_K5_sonnet_partial.md, the
first reader's log, preserved unchanged).**

## 0. Header

- Cluster: K5 metals. Products: GC, MGC, SI, SIL, HG, MHG, PL (gold {GC, MGC}; silver {SI, SIL};
  copper {HG, MHG}; platinum {PL}).
- Run 1 (ClusterReader-K5, sonnet medium): 2026-09-23 20:15 to 20:40 PDT. Stopped early (misread a
  cost notice); containers 5, 6, 9, 10, 11 were under the 4-query floor.
- Run 2 (ClusterReader-K5b-OpusHigh, promoted continuation): 2026-09-23 20:50 to 21:26 PDT.
- Stop reason, by branch of rule (c): **branch 2**. Every container has at least 4 distinct logged
  queries and its last 2 queries produced no new passing item (per-container detail in section 1).
  Branch 1 (60 full-text reads) was not reached: 17 research full texts across both runs (5 in
  run 1, 12 in run 2), plus 2 re-fetches in run 2 to re-check run-1 numbers (K5-006, K5-009) and
  9 official documentation pages for timing facts.
- Retrieval constraints met in run 2 (they limited routes, not the stopping rule): Firecrawl
  credits ran out at about 20:54 PDT (only 2 firecrawl reads in run 2: K5-011, K5-001);
  the session-wide WebSearch budget (200 calls) was exhausted at about 21:05 PDT; the OpenAlex
  free daily budget for this IP ran out at about 21:13 PDT. After that, discovery used the
  Crossref API, the arXiv API, Wayback CDX URL listings and direct site fetches; retrieval used curl
  (PDF + pdftotext; HTML tag-stripped) and Wayback `id_` captures. HTML read by curl is labelled
  "curl" and counts as fetched text; no passage below comes from a WebSearch summary or a WebFetch
  rendering.
- Counts (both runs):
  - Items screened: run 1 about 28; run 2 about 170 titles or abstracts (bulk title lists from
    Crossref JFM and SSRN queries, OpenAlex citing-paper lists, arXiv, CFTC, Wayback URL lists).
    Approximate; bulk title-level rejects are listed in section 2.
  - Passed pre-filter and logged: 31 unique sources (K5-001, K5-002, K5-004 to K5-032; K5-003 is a
    duplicate of K5-006). 9 from run 1, 22 new in run 2.
  - Full text read: 17 (K5-001, 004, 006, 007, 009, 010, 011, 012, 014, 016, 019, 020, 024, 028,
    029, 032, plus K5-008 as abstract + section snippets).
  - Abstract only: 8 (K5-002, 005, 013, 015, 017, 021, 025, 031).
  - Retrieval failed, title-level only: 6 (K5-018, 022, 023, 026, 027, 030).
  - Panel sources claimed (rule 3): K5-028 ([K5] gold, [K4] oil); K5-029 ([K5] GC, SI, PL, HG;
    [K4] CL, HO, NG; [K6] W, C, S, BO). Panel source met and not re-read: K3-007 (Baum, Kurov,
    Wolfe; its [K5] passage P-K3-007-h gives copper 0.18 and silver 0.06 per one-SD Chinese PMI
    surprise).
  - [unverified] numeric claims: none asserted without a passage; every [unverified] field is
    labelled in place.
- Registry corrections found (registry not rewritten, per rule 1): K5-004's registry DOI
  10.1016/j.irfa.2015.01.019 is wrong (correct .017); K5-005's DOI in the log and registry
  (10.1016/j.intfin.2018.12.012) resolves to another paper, and OpenAlex gives
  10.1016/j.intfin.2018.12.003; K5-003 duplicates K5-006.
- Corrections to run-1 content: K5-006 now carries the authors' trend-controlled finding that the
  fix change INCREASED volatility (run 1 reported only the raw reduction); K5-010's London-to-CT
  conversion is corrected; the four [unverified] timing facts are now verified (section 3.0).

## 1. Container log

Times are PDT on 2026-09-23. Run-2 times are from checkpoints written during the run and are
accurate to about ±2 minutes. "New pass" means a new item passing pre-filter.

| # | Container | Run-1 queries | Run-2 queries (in order; result) | Run-2 start / pre-filter done / full text done | Passed (both runs) | Last 2 queries dry? |
|---|---|---|---|---|---|---|
| 1 | Journal of Futures Markets | 5 | Q6 WebSearch Hauptfleisch/Putnins/Lucey (new pass K5-011); Q7 Crossref JFM "gold intraday" (new K5-021, K5-022, K5-023); Q8 "silver futures" (none); Q9 "copper futures" (none); Q10 "precious metals" (new K5-020); Q11 "gold futures announcement" (none); Q12 "platinum" (none); Q13 "gold fixing benchmark" (none); Q14 "metals settlement expiration" (none relevant) | 20:51 / 21:09 / 21:07 | K5-001, 011, 015, 020, 021, 022, 023 | yes (Q13, Q14) |
| 2 | Caminschi and Heaney 2014 and the London-fix literature (citation chain) | 3 | Q4 Semantic Scholar record of Caminschi (refs and citations; leads K5-012/013/015/018); Q5 WebSearch Caminschi PDF (UWA manuscript; EFMA lead); Q6 WebSearch "Transparency in Commodities Markets" (new K5-012); Q7 OpenAlex papers citing Caminschi (new K5-024, 026, 027); Q8 OpenAlex citing Hauptfleisch (new K5-025); Q9 OpenAlex citing Batten et al. 2017 (new K5-028, K5-029); Q10 citing Aspris et al. 2020 (none: FX-fix papers); Q11 citing Elder et al. 2012 (none) | 20:51 / 21:15 / 21:12 | K5-002, 006, 012, 013, 016, 018, 024, 025, 026, 027, 028, 029 | yes (Q10, Q11) |
| 3 | Alexander Kurov (panel sources: rule 3) | 3 | Q4 Crossref author list for Kurov (title-level pass K5-030; K3-007 panel: see K3-007; Drift Begone: see K3-034); Q5 Crossref abstracts of Kurov commodity papers (none new); Q6 Crossref Kurov + gold (none); Q7 Crossref Kurov + metal/copper/silver (none). A RePEc htsearch attempt returned an empty results page (failed, not counted). | 21:12 / 21:14 / n/a (no full text reachable) | K5-030 (title-level) | yes (Q6, Q7) |
| 4 | SSRN (via Crossref prefix 10.2139; SSRN itself returns 403 to curl and WebFetch) | 2 | Q3 "gold futures intraday" (none new); Q4 "silver futures intraday" (none); Q5 "copper futures intraday Shanghai COMEX" (none); Q6 "precious metals fix auction" (new K5-031); Q7 "gold silver ratio" (none: 1 shelved, 3 rejected); Q8 "platinum futures" (none) | 21:14 / 21:16 / n/a (SSRN blocked) | K5-031 | yes (Q7, Q8) |
| 5 | arXiv q-fin.TR / q-fin.ST (arXiv API) | 1 | Q2 gold AND intraday/high-frequency (none); Q3 silver/platinum AND futures (none); Q4 copper AND futures (none; one K8 flag); Q5 "precious metals" (new K5-032); Q6 COMEX (none); Q7 gold AND announcement/FOMC/macroeconomic (none) | 21:15 / 21:17 / 21:16 | K5-009, 032 | yes (Q6, Q7) |
| 6 | CFTC Office of the Chief Economist | 1 | Q2 OCE research-papers index and keyword list (no metals keyword); Q3 OCE research papers pages 1-6, 57 titles (4 candidates, all rejected); Q4 OCE reports pages (5 titles, none relevant) | 21:18 / 21:20 / n/a | none | yes (Q3, Q4) |
| 7 | LBMA, ICE Benchmark Administration; LME and SHFE hours | 3 | Q4 LBMA Gold Price page (no times stated); Q5 ICE IBA LBMA gold/silver page (times verified); Q6 LBMA Platinum and Palladium page (times verified); Q7 LME trading venues via Wayback 2025-12-05 (hours verified); Q8 SHFE English trading-hours page (hours verified). Documentation only; no new research items. | 20:54 / 20:57 / 20:57 | K5-010 (documentation) | yes |
| 8 | CME Group metals research and education (cmegroup.com refuses this IP; Wayback and CME's client wiki used) | 3 (2 timed out) | Q4 CME Client Systems Wiki: Gold settlement (verified); Q5 Wiki: Copper settlement (verified); Q6 CFTC-hosted COMEX 4GC settlement filing (context); Q7 Wayback copies of GC and HG contract-spec pages (nav links only; hours load by script); Q8 Wayback CME weekly metals options fact card PDF (Globex hours); Q9 "Metal options liquidity during London market hours" (rejected); Q10 "Will coronavirus impact industrial metals markets?" (rejected) | 20:55 / 21:21 / 20:57 | none | yes (Q9, Q10) |
| 9 | Databento blog | 1 | Q2 blog index (25 posts, none metals); Q3 "learning" category (none); Q4 pagination (client-side, same content); Q5 Wayback CDX of databento.com/blog/* (205 URLs, none on metals) | 21:21 / 21:22 / n/a | none | yes |
| 10 | Quantpedia | 2 | Q3 site search (script-rendered, no results in HTML); Q4 WordPress REST API (HTTP 466 "Access Forbidden", failed); Q5 Wayback CDX of /strategies/* (138 URLs: "gold-market-timing" only); Q6 Wayback CDX of all quantpedia.com URLs (12,064; 14 gold posts, all rejected or flagged) | 21:22 / 21:23 / n/a | none | yes (Q5, Q6) |
| 11 | Practitioner blogs (discovery only) | 1 | Q2 Kinlay: Wayback CDX (6,226 URLs) and metals category (2 posts, rejected); Q3 Quantitative Brokers CDX (1 gated note, rejected); Q4 Robot Wealth CDX (GLD posts, rejected); Q5 Carver (qoppac) CDX (1 opinion post, rejected); Q6 Quantocracy CDX (1,942 URLs, no metals) | 21:23 / 21:24 / n/a | none | yes |

## 2. Rejected items (pre-filter, one line each; no full text fetched unless stated)

Run 1 (kept as logged):
- R-K5-001 | JFM | Bracker (1999), "Detecting and modeling changing volatility in the copper futures market" | daily volatility model, title-level
- R-K5-002 | arXiv/MDPI | "Construction of an SDE Model from Intraday Copper Futures Prices" | stochastic-model construction, no trading mechanism
- R-K5-003 | Kurov, Sancetta, Strasser, Wolfe (JFQA 2019) | E-mini S&P 500 and 10-year note only (claimed as K2-007) | not K5
- R-K5-004 | CFTC OCE | "Convective Risk Flows in Commodity Futures Markets" | weekly COT frequency
- R-K5-005 | Quantpedia | "A New Return Asymmetry Investment Factor in Commodity Futures" | monthly cross-sectional factor
- R-K5-006 | Quantpedia | "Commodity Portfolio Strategy for a Potential 2026 Inflationary and Supply Shock Regime" | monthly ETF momentum
- R-K5-007 | discoveryalert.com.au | "silver declines before COMEX options expiration due to delta hedging" | content-marketing site, no data
- R-K5-008 | JFM | Hauptfleisch, Putnins, Lucey (2016) | run 1 listed it as unread; run 2 read it in full as K5-011 (not a rejection)

Run 2:
- R-K5-009 | J. Financial Markets 2022 | Aquilina, Ibikunle, Mollica, Steffen, "The visible hand: benchmarks, regulation, and liquidity" | interest-rate swaps benchmark, not K5 (OpenAlex abstract)
- R-K5-010 | JBF 2017 | Frino, Ibikunle, Mollica, Steffen, "The impact of commodity benchmarks on derivatives markets: Dated Brent" | Brent, K4 region (title)
- R-K5-011 | JFM 2018 | Xu, "Market openness and market quality in gold markets" | SGE international-board event study; COMEX only a benchmark; no intraday mechanism for a K5 product (abstract)
- R-K5-012 | J. Commodity Markets 2017 | Smales, "Commodity market volatility in the presence of U.S. and Chinese macroeconomic news" | sector-level volatility, energy-driven; no intraday horizon in the abstract (RePEc abstract, curl)
- R-K5-013 | Economic Modelling 2021 | "Media effects matter: Macroeconomic announcements in the gold futures market" | sentiment (media coverage), shelved
- R-K5-014 | JFM 2013 | Yin and Han, "Exogenous Shocks and Information Transmission in Global Copper Futures Markets" | bivariate EGARCH spillovers at daily frequency (abstract)
- R-K5-015 | JFM 2010 | Fung, Liu, Tse, "The information flow and market efficiency between the U.S. and Chinese aluminum and copper futures markets" | "comparably efficient on a daily basis"; daily (abstract)
- R-K5-016 | JFM 2016 | Pradkhan, "Information Content of Trading Activity in Precious Metals Futures Markets" | Markov-switching Granger tests; no intraday horizon in the abstract
- R-K5-017 | JFM 1994 | Wahab, Cohn, Lashgari, "The gold-silver spread: Integration, cointegration, predictability, and ex-ante arbitrage" | no abstract available; title and era indicate a daily cointegration and arbitrage study (title-level judgment, flagged as such)
- R-K5-018 | JFM 2022 | Rosa, "Understanding intraday momentum strategies" | generic overnight-predicts-last-half-hour momentum; abstract names no metals product (D.1 territory, rule 6)
- R-K5-019 | JFM, titles only | daily, hedging or non-mechanism studies: "Return distributions and volatility forecasting in metal futures markets" (2010); "Structural breaks and volatility forecasting in the copper futures market" (2017); "Jumping hedges ... copper spot and futures" (2005); "A semi-strong test of the efficiency of the aluminum and copper markets at the LME" (1988); "Commonality in the LME aluminum and copper volatility processes through a FIGARCH lens" (2008); "Risk and return in copper, platinum, and silver futures" (1990); "Conditional dynamics and optimal spreading in the precious metals futures markets" (1995); "Analyzing the frequency dynamics of volatility spillovers across precious and industrial metal markets" (2021); "Regional premiums in nonferrous metals markets" (2021); "Cointegration tests of the unbiased expectations hypothesis in metals markets" (1993); "Commodity futures market conditions and climate policy risk" (2024); "Cold fusion—hot metal" (1991, one-off event); "Hedging industrial metals with stochastic volatility models" (2014); "The distribution of gold futures spreads" (1990); "Put-call-futures parity ... options on gold futures" (1990); "Forecasting S&P and gold futures prices: neural networks" (1993); "The relative efficiency of the gold and treasury bill futures markets" (1986); "Role of economic policy uncertainty in forecasting gold futures volatility: India" (2025); "South African political unrest, oil prices, and the time varying risk premium in the gold futures market" (1990); "Spreading between the gold and silver markets: is there a parity?" (1985); "Silver price volatility: July 1979-April 1980" (1981); "Golden turtle tracks: gold spreads" (1987); "Gold and the weekend effect" (1982, close-to-close); "A further investigation of the day-of-the-week effect in the gold market" (1986, close-to-close); "Rational speculative bubbles in the gold futures market" (2000); "A tale of two contracts: SHFE copper vs INE bonded copper" (2023, China-internal)
- R-K5-020 | JFM 1981 | "Newspaper articles and their impact on commodity price formation: copper" | sentiment, shelved
- R-K5-021 | Brandeis WP 2017 / JBF 2026 | Osler and Turnbull, "Dealer Trading at the Fix" / "Dealer misconduct and price dynamics at the fix" | the WM/R London 4 pm FX fix (first page of the Wayback-archived WP read for pre-filter), K3 region
- R-K5-022 | SSRN 2017/2018 | Boot, Klein, Schinkel, "Collusive Benchmark Rates Fixing" | collusion theory, no product data (title)
- R-K5-023 | Int. J. Finance & Economics 2020 | Rzayev and Ibikunle, "Order aggressiveness and flash crashes" | S&P 500 stocks (abstract)
- R-K5-024 | Physica A 2017 | Lin, Wang, Xie, Stanley, "Cross-correlations and influence in world gold markets" | network cross-correlation study; no abstract obtained; title-level
- R-K5-025 | IRFA 2015 | "The financial economics of gold — A survey" | survey, no single mechanism
- R-K5-026 | Quantitative Finance 2020 | "The impact of US macroeconomic news announcements on Chinese commodity futures" | target is SHFE/DCE, not CME products
- R-K5-027 | Resources Policy / other citing-list titles | daily hedge, safe-haven, forecasting and ETF-volatility studies (e.g. "Volatility forecasting of strategically linked commodity ETFs: gold-silver" 2016; "Forecasting gold futures market volatility using macroeconomic variables" 2018; "Extreme risk spillover effects in world gold markets" 2016) | daily horizon
- R-K5-028 | SSRN 2023 | "Forecasting Intraday Volatility: Evidence from China Gold Futures Market" | SHFE gold target; forecasting only
- R-K5-029 | SSRN 2026 | Shrestha, "Relative-Value Reversal in Precious Metals and Mining ETFs" | ETFs and mining equities; multi-day lookbacks (Crossref abstract)
- R-K5-030 | SSRN 2016 | Klein, "Conditional Variance Dynamics of Gold and Other Precious Metals" | 1, 5 and 20 day-ahead GARCH forecasts (Crossref abstract)
- R-K5-031 | SSRN 2007 | Batten, Ciner, Lucey, "Structure in Gold and Silver Spread Fluctuations" | COMEX spread long-memory; no intraday horizon. NEGATIVE result in the abstract: "This last finding suggests limited opportunity to profit from strategies based on mean reversion of the spread." (Crossref abstract)
- R-K5-032 | SSRN 2016 | Lucey and O'Connor, "Mind the Gap: Psychological Barriers in Gold and Silver Prices" | daily fix-price digit distribution (Crossref abstract)
- R-K5-033 | SSRN 2025 | Kelly, "Gold and Silver Shine During the Day" | sentiment (weather-mood effect on GLD/SLV day returns), shelved (Wayback SSRN abstract page)
- R-K5-034 | SSRN 2025 | Mittal and Mittal, "Gold Silver Pair Trading - Mean Reversion Strategy Using Machine Learning" | GC-SI spread z-score with Kalman hedge and ML regime filters incl. sentiment features, 2015-2025; no intraday horizon stated (Wayback SSRN abstract page)
- R-K5-035 | SSRN 2010 | "The Asymmetric Volatility of Platinum and Palladium Futures" | daily volatility (title)
- R-K5-036 | arXiv 1402.6583 | "Finding informed traders in futures and their underlying assets in intraday trading" | ultra-high-frequency, a few days in 2013 (Topstep bars high-rate trading)
- R-K5-037 | arXiv 2203.12457 | "Neural Network and Order Flow, Technical Analysis: Predicting short-term direction of futures contract" | SHFE silver, order-book features
- R-K5-038 | arXiv 2006.15214 and 1210.7215 | MF-DFA of precious metals; LOB volume profiles | no trade mechanism
- R-K5-039 | CFTC OCE (Jain, Kayhan, Onur) | "Determinants of Commodity Market Liquidity" | positions-data liquidity determinants, not intraday (abstract read from the PDF's first pages)
- R-K5-040 | CFTC OCE (Haynes, Roberts 2015) | "Macro News Announcements and Automated Trading" | E-mini S&P 500 and 10-year note only (first page read)
- R-K5-041 | CFTC OCE (Onur, Reiffen) | "The Effect of Settlement Rules on the Incentive to Bang the Close" | CBOT corn, K6 region
- R-K5-042 | CFTC OCE (Raman, Robe, Yadav) | "The Third Dimension of Financialization" | crude oil, K4 region
- R-K5-043 | CME Group (Wayback 2026-01-19) | "Metal options liquidity during London market hours" | options ADV note (2019 data), not a futures mechanism
- R-K5-044 | CME Group (Wayback 2026-01-14) | "Will coronavirus impact industrial metals markets?" | macro commentary
- R-K5-045 | Kinlay blog | "Metal Logic" (2016) | daily spot VAR forecasts, 2012-2016
- R-K5-046 | Kinlay blog | "A Study in Gold" (2014) | GDX gold-miners equity ETF day/overnight rule; not a K5 product. NEGATIVE: the post says the rule "has recently begun to fail, producing (substantial) negative returns since June 2013"
- R-K5-047 | Quantitative Brokers | "Reddit Frenzy and Microstructure Changes in Silver and Gold Futures" (2021) | gated (form), one two-week episode
- R-K5-048 | Robot Wealth | "Gold's weekend effect: GLD Thursday-Friday trade"; "Weekly seasonality in gold" | ETF, overnight holds
- R-K5-049 | Carver (qoppac) | "Bitcoin, money, gold and my great ..." (2014) | opinion
- R-K5-050 | Quantpedia | "Cultural calendars and the gold drift: are holidays moving GLD ETF"; "An extensive test of market timing strategies in the gold market"; strategy "gold-market-timing"; allocation and safe-haven posts | daily close-to-close ETF or allocation (titles; Wayback CDX list)
- R-K5-051 | Kurov et al. (Financial Review 2023) | "A shot in the arm: COVID-19 vaccine news" | one-off 2020 event set
- R-K5-052 | Kurov, Sancetta, Wolfe (JIMF 2022) | "Drift Begone!" | see K3-034 (claimed by K3)
- R-K5-053 | Baum, Kurov, Wolfe (JIMF 2015) | "What do Chinese macro announcements tell us about the world economy?" | see K3-007 (panel; [K5] passage P-K3-007-h)

## 3. Passed items

### 3.0 Timing facts (re-scraped; replaces run 1's four [unverified] background facts)

- LBMA auction times. Source: ICE Benchmark Administration, https://www.ice.com/iba/lbma-gold-silver-price (curl, tags stripped): "The auctions are run at 10:30 and 15:00 London time for gold, 12:00 London time for silver, and 09:45 and 14:00 London time for platinum and palladium." LBMA page https://www.lbma.org.uk/prices-and-data/lbma-platinum-and-palladium-price (curl): "Since the benchmarks are derived from the price of the final round of the auctions, they do not have set publication times. The expected auction start times, in London time, are: ... LBMA Platinum Price 09:45 and 14:00 ... LBMA Gold Price 10:30 and 15:00 LBMA Silver Price 12:00". VERIFIED.
- LME hours. Source: Wayback capture 2025-12-05 of https://www.lme.com/en/Trading/Trading-venues (curl; lme.com returns 403 to curl directly): "The Ring 11:40 - 17:00 ... LMEselect 01:00 - 19:00 ... The Exchange also supports an inter-office telephone market between LME members, which operates 24 hours a day." (London time per run 1's context; the page lists the times without a zone label.) VERIFIED, with that caveat.
- SHFE copper hours. Source: https://www.shfe.com.cn/eng/reports/CalendarHolidays/TradingHours/ (curl, 2026-09-23; checked that the table is not inside an HTML comment): "Futures: CU,BC,AL,AO,ZN,PB,NI,SN,SS,AD ... Night trading session ... Auction trading period 21:00-01:00 Day trading session ... Auction trading period 09:00-10:15 Auction trading period 10:30-11:30 Auction trading period 13:30-15:00" and for "Futures: AU,AG,SC": night "Auction trading period 21:00-02:30". "Notice:The night trading session for a given trading day begins at 21:00 of the previous trading day." Beijing time, UTC+8. VERIFIED. (Run 1's "9 AM-11:30 AM and 1:30 PM-3:00 PM" omitted the 10:15-10:30 break and the night session.)
- CME settlement windows. Source: CME Group Client Systems Wiki (CME's own Confluence, curl), https://cmegroupclientsite.atlassian.net/wiki/display/EPICSANDBOX/Gold: "Gold futures (GC) are settled by CME Group staff based on trading activity on CME Globex during the settlement period. The settlement period is defined as: 13:29:00 to 13:30:00 ET for the active month and 13:15:00 to 13:30:00 ET for calendar spreads." and .../pages/457415464/Copper: "Copper futures (HG) are settled by CME Group staff based on trading activity on CME Globex during the settlement period. The settlement period is defined as: 12:59:00 to 13:00:00 ET for the active month and 12:30:00 to 13:00:00 ET for calendar spreads." Consistent with the CFTC-hosted COMEX filing https://www.cftc.gov/sites/default/files/filings/orgrules/23/08/rules0815235374.pdf (4GC: "The settlement period is defined as: 13:29:00 to 13:30:00 ET."). VERIFIED (GC 12:29-12:30 CT; HG 11:59-12:00 CT).
- CME Globex metals hours. Source: Wayback capture 2024-12-07 of CME's "METALS COMEX Weekly Options Gold – Silver - Copper" fact card PDF (https://www.cmegroup.com/trading/metals/files/weekly-options-fact-card.pdf; curl, pdftotext): "CME Globex Open: Sunday 5:00 p.m. - Friday 4:00 p.m. CT with a daily maintenance period from 4:00 p.m. - 5:00 p.m. CT". VERIFIED for the metals weekly options on Globex. The futures contract-spec pages load hours by script and did not show them in the Wayback copy, so the futures hours are not separately quoted from a CME page. Run 1's "Sunday 6:00 PM ET ... break 5:00-6:00 PM ET" matches this in Central time.


### 3.1 Passed items (registry id order)

### K5-001
- **Citation:** Caminschi, A. & Heaney, R. (2014). "Fixing a Leaky Fixing: Short-Term Market Reactions to the London PM Gold Price Fixing." Journal of Futures Markets, 34(11), 1003–1039. DOI 10.1002/fut.21636.
- **Retrieval (first run):** Abstract only. Full text is paywalled at Wiley (direct fetch returned HTTP 403). Routes tried and failed: (1) publisher (onlinelibrary.wiley.com) — 403; (2) RePEc/IDEAS mirror — abstract only, `File URL: http://hdl.handle.net/` with no usable full text; (3) Wayback Machine capture of the Wiley page — redirected to a cookie-set page, no article body. Abstract obtained via `firecrawl_scrape` of the RePEc/IDEAS page (genuine markdown fetch, not a search summary).
- **Mechanism:** Studies the London PM gold price fixing's effect on the GC futures contract and the GLD ETF; finds elevated volume/volatility and informed-trader returns in the minutes after the fixing opens, before the fixing result is published.
- **Products/horizon:** GC gold futures (and GLD, non-CME, K5-relevant as background); horizon is minutes (intraday, within the PM fixing window, 15:00 London / 09:00–10:00 CT depending on DST — well before the 15:08 CT flatten).
- **Quality tells (first run, abstract only; see the continuation-run quality tells below):** none observable from the abstract; the paper is widely cited and is credited (per secondary UWA press material, not independently verified here) with contributing to the 2015 replacement of the London Fix — this attribution itself is [unverified], not drawn from the paper's own text.
- **Verified passages:**
  - P-K5-001-a (abstract, RePEc mirror of Wiley abstract): "We find significantly elevated levels of trade volume and price volatility immediately following the fixing's start, well before the conclusion of the fixing and the publication of its results... we find statistically significant return advantages in the 4 minutes following the start of the fixing for informed traders... Trades in the opening minutes of the fixing are significantly predictive of the price direction of the fixings, in some cases exceeding 90%."
- **Numeric claims:** "4 minutes" and "exceeding 90%" — P-K5-001-a; >50% volume and >40% volatility increase — P-K5-001-b; ~10 bps and ~4 bps, 80-95% — P-K5-001-c; windows — P-K5-001-d; costs — P-K5-001-e.
- **Tags:** new to the program. Intraday-feasible: yes — mechanism is a same-session reaction to a scheduled twice-daily auction, flat well before 15:08 CT, uses market-order-compatible directional signals (not queue-position or SIM-fill dependent as described).
- **Clusters tagged:** [K5] only.
- **CONTINUATION RUN: full text read.**
- Retrieval: firecrawl_scrape (pdf parser) of https://research-repository.uwa.edu.au/files/4725264/A0205_use_this.pdf (UWA "Accepted author manuscript", linked from the UWA repository record found via Semantic Scholar), 20:53 PDT, before Firecrawl credits ran out. curl of the same URL returned a Cloudflare challenge page.
  - P-K5-001-b (mechanism, Introduction): "This study finds that both the GC and GLD markets are sensitive to the fixing, with large, statistically significant spikes in trade volume and price volatility following the start of the price fixing period. Trade volumes increase over 50% and price volatility increases over 40% following the fixing start."
  - P-K5-001-c (returns, Introduction): "The difference in returns deliver the informed trader an advantage of around 10bps in the four minutes following the start of the fixing, and a possible further 4bps in the two minutes before the end of the fixing. These returns far exceed trading costs, and can be deemed economic. However, we find no significant returns following the end of the fixing. Further, trades in GC and GLD following the start of the fixing are found to be predictive of the fixing price direction, with higher prediction rates (80-95%) for fixings resulting in larger price movements."
  - P-K5-001-d (data window, Introduction): "This study analyses two time periods: the six years from 1 January 2007 to 31 December 2012, and the one and a half years from 18 August 2011 to 31 December 2012." Table note: "The sample period, January 1, 2007 to December 31, 2012, covers 1504 trade days."
  - P-K5-001-e (costs, section 3): "Even for the worst case of $2.32/contract for retail traders, the transaction costs represent less than 0.0015% or 0.15 basis points (bps) of notional value." and "each tick in either GC or GLD represents about 0.00625% (0.63 bps) of notional value using a price of $1,600 per ounce. Allowing for four ticks of slippage and spread, and two sets of transaction costs, suggests a threshold of 3 bps for a trade to be deemed economic in this study."
  - P-K5-001-f (definition of the informed trader, results): "In summary, the empirical analysis suggests that an informed trader, with directional foresight of the fixing price, can earn returns in excess of those available to an uninformed trader. These returns are realizable largely in the four minutes following the start of the fixing."
  - P-K5-001-g (end-of-fix reversal, results): "the two minutes leading to the end of the fixing do show statistically significant negative returns. One possible explanation for this is the overshoot caused by uniformed traders." [sic]
- Numeric re-checks: tick 0.10/1600 = 0.00625% (matches); "$400 per contract (100 ounces x $4)" and "$208,000 per year ($400 x 2 x 260)" recompute correctly (the x 2 assumes both daily fixings, while the study measures only the PM fixing).
- Cost assumptions: GC fees USD 0.70 to 2.32 per contract; economic threshold 3 bps including four ticks of spread and slippage (P-K5-001-e).
- Data window: 2007-01-01 to 2012-12-31 (GC 1504 trade days); sub-sample 2011-08-18 to 2012-12-31 with fix publication times (P-K5-001-d). GC data from TickData Inc.
- Quality tells: (1) the headline 10 bps and 4 bps are "adjusted returns" signed by the eventual fixing direction, i.e. they assume directional foresight (P-K5-001-f); what a public trader can observe is the opening-minute trade direction, reported as 80-95% predictive only for fixings with larger moves (P-K5-001-c). (2) The sample is the old telephone PM fixing, replaced by the electronic LBMA Gold Price auction in March 2015; K5-012 re-tests the pattern after the change. (3) Manuscript, not the typeset article: page numbers not matched to the published pagination.

### K5-002
- **Citation:** Nilsson, L. (2015, rev. 2018). "Did the New Fix, Fix the Fix? An Intraday Exploration of the Precious Metal Fixing." SSRN 2657767.
- **Retrieval:** Abstract only. Routes tried and failed: SSRN abstract page direct WebFetch — 403; `firecrawl_scrape` of the SSRN abstract page succeeded (genuine fetch) but the page's own "Download This Paper" / "Open PDF in Browser" links both resolve back to the same abstract page when scraped — full text is not served without an SSRN login. No working-paper mirror found elsewhere.
- **Mechanism:** Examines price pressure into the gold/silver/platinum/palladium fixing auctions before and after the 2014–2015 structural change (opaque negotiation → electronic auction), inside vs. outside active US trading hours.
- **Products/horizon:** Gold, silver, platinum (palladium not a Topstep-listed product, ignored); horizon is the pre-auction window (minutes), intraday.
- **Cost assumptions:** [unverified], not in abstract.
- **Data window:** "the precious metal Fixing structure that took place in 2014 and 2015" — the study window itself is not more precisely dated in the abstract; [unverified] beyond that.
- **Quality tells:** author is a practitioner (NilssonHedge.com), not an academic venue; unpublished/self-hosted SSRN working paper never placed in a peer-reviewed journal in the 3 years between initial post and last revision — treat findings as lower-confidence pending full text.
- **Verified passage:**
  - P-K5-002-a (SSRN abstract, firecrawl_scrape): "We find that there is negative price pressure going into the auctions, for all precious metals, outside active US trading hours regardless of Fixing structure. For active US trading hours, there is no obvious, observable persistent price pressures."
- **Numeric claims:** none quantified in the abstract; no numeric claim logged.
- **Tags:** new to the program. Intraday-feasible: yes as described (pre-auction price pressure, same-session), but the "no significant change" finding for US hours weakens the case for a US-session version of this mechanism.
- **Clusters tagged:** [K5] only (palladium excluded, not a traded product).
- **Continuation-run retry (K5-002):** (Nilsson, SSRN 2657767): curl of the SSRN abstract page gave HTTP 403; the NilssonHedge research page (curl) links only to the SSRN page; the Wayback CDX index holds only abstract-page captures (2018-06-05, 2019-08-18, 2025-04-26) and no Delivery.cfm PDF; Firecrawl is out of credits. Status unchanged.

### K5-003
- Duplicate registry id: K5-003 (claimed at the first run for the BearWorks URL of Crain, Hoelscher & Jones 2020) is the same source as K5-006. The registry line is kept (rule 1: never rewrite); treat K5-003 as pointing to K5-006.

### K5-004
- **Citation:** Smales, L.A. & Yang, Y. (2015). "The importance of belief dispersion in the response of gold futures to macroeconomic announcements." International Review of Financial Analysis, 41(C), 292–302. DOI 10.1016/j.irfa.2015.01.017.
- **Retrieval (first run):** Abstract only. Routes tried and failed: (1) ScienceDirect direct — paywalled (confirmed via RePEc download-restriction note: "Full text for ScienceDirect subscribers only"); (2) RePEc/IDEAS abstract mirror — abstract only, `firecrawl_scrape` genuine fetch; (3) Wayback Machine capture of the ScienceDirect abstract page (2020-07-29 snapshot) — abstract + "Highlights" only, "View full text" link leads back to the paywalled live site.
- **Mechanism:** Gold futures' trading volume, returns and volatility response to US macro announcements (esp. unemployment, GDP), with a novel "belief dispersion" measure amplifying the response.
- **Products/horizon:** COMEX gold futures (per keywords: "Gold futures... COMEX... High-frequency"); horizon: seconds to ~90 seconds post-release, intraday.
- **Cost assumptions:** none (not a strategy paper; continuation run).
- **Data window:** 2006-11-24 to 2012-12-31, 1,532 trading days (P-K5-004-d, continuation run).
- **Quality tells:** none apparent from abstract; peer-reviewed Elsevier journal.
- **Verified passages:**
  - P-K5-004-a (RePEc/IDEAS abstract, firecrawl_scrape): "Market activity, in terms of traded volume, returns, and volatility, responds to new information quickly, with the majority of the reaction complete within 90-s."
  - P-K5-004-b (same source): "gold futures exhibit greater reactions to 'good' economic news (which is negative for gold prices) and the magnitude of the response does not appear to increase during recession."
- **Numeric claims:** "90-s" reaction window — P-K5-004-a.
- **Tags:** new to the program (product-specific announcement-response study on gold; distinct from the K4/D.1 generic announcement family since it is gold-specific with a belief-dispersion conditioning variable). Intraday-feasible: yes — reaction window is under 2 minutes, well inside a single session, market-order compatible.
- **Clusters tagged:** [K5] only.
- **CONTINUATION RUN: full text read.**
- Retrieval: Curtin espace AAM found through OpenAlex (oa_url https://espace.curtin.edu.au/bitstream/20.500.11937/40677/4/227313.pdf). A direct curl got HTTP 202 with an empty body. The Wayback capture of 2023-11-18 (curl, `id_` raw mode) returned the PDF, read with pdftotext.
- Registry correction (not rewritten, per rule 1): registry line K5-004 carries DOI 10.1016/j.irfa.2015.01.019. OpenAlex resolves that DOI to a different paper ("Time variation in systematic risk, returns and trading volume ..."). The correct DOI is 10.1016/j.irfa.2015.01.017 (OpenAlex title match; the log's citation line already has .017).
- P-K5-004-c (AAM abstract): "Market activity, in terms of traded volume, returns, and volatility, responds to new information quickly, with the majority of the reaction complete within 90-seconds. Surprises on the unemployment rate have the largest impact, with the market witnessing greater reactions to 'good' news and a weaker response during recession."
- P-K5-004-d (data, section 2): "Transaction level data for gold futures are obtained from Thomson Reuters Tick History (TRTH) provided by SIRCA for the period 24th November 2006 – 31st December 2012, a total of 1,532 trading days; for the data used in this sample the nearest-to-maturity contract is used and switched to the second-nearest contract when open interest becomes greater."
- P-K5-004-e (response size and decay): "As the announcement is made there is a significant spike in volume and volatility (volume increases by 405%, and volatility by 220% for 10-sec intervals). Volume and volatility peak in the first interval (0,10), and then declines to a level that is generally higher but statistically indistinguishable from that on non-announcement days within 90 seconds (60 seconds for volatility)"
- P-K5-004-f (pit open): "there is also a jump in volume and volatility upon the opening of the pit at 08:20AM, however the increase is greater and more persistent following major macroeconomic announcements."
- Numeric claims: 405% and 220% (P-K5-004-e); 90 s and 60 s (P-K5-004-e); 1,532 trading days and the window (P-K5-004-d).
- Cost assumptions: none (not a trading-strategy paper).
- Quality tells: the manuscript abstract says "a weaker response during recession" (P-K5-004-c) while the published abstract read by the first run says "the magnitude of the response does not appear to increase during recession" (P-K5-004-b); the published text may differ from the manuscript. Same author and same TRTH sample as K5-019, so the two are not independent evidence.

### K5-005
- **Citation:** Smales, L.A. & Lucey, B.M. (2019). "The influence of investor sentiment on the monetary policy announcement liquidity response in precious metal markets." Journal of International Financial Markets, Institutions and Money, 60(C), 19–38. DOI 10.1016/j.intfin.2018.12.012.
- **Retrieval:** Abstract only. Same route pattern as K5-004: publisher paywalled, RePEc/IDEAS mirror gives abstract via genuine `firecrawl_scrape`.
- **Mechanism:** Liquidity (bid-ask/depth proxies) in gold and silver — across futures, ETF and physical/bullion instruments — is withdrawn ahead of monetary-policy announcements and recovers afterward; recovery speed depends on prevailing investor sentiment and surprise size.
- **Products/horizon:** Gold and silver, three instrument types including futures; horizon: minutes around the announcement, intraday.
- **Cost assumptions:** [unverified].
- **Data window:** [unverified] (not in abstract).
- **Quality tells:** none apparent; peer-reviewed.
- **Verified passage:**
  - P-K5-005-a (RePEc/IDEAS abstract, firecrawl_scrape): "We show that liquidity is removed from the market around 5-minutes prior to the announcement and reverts to normal within 10-minutes (gold market) and 20-minutes (silver market)."
- **Numeric claims:** "5-minutes prior," "10-minutes" (gold), "20-minutes" (silver) — all P-K5-005-a.
- **Tags:** port of D.1 family E (calendar and events), specifically the announcement-liquidity mechanism, tested product-specifically on gold and silver (satisfies rule 6's product-specific exception). Intraday-feasible: yes — the mechanism is about liquidity timing within minutes of an announcement, no overnight hold, market-order compatible if the strategy trades outside the illiquid 5-minute pre-announcement window (a market order placed inside that window would face wide spreads — a design constraint to flag, not a disqualifier).
- **Clusters tagged:** [K5] only.
- **Continuation-run retry (K5-005):** (Smales and Lucey): curl of SSRN 3011758 gave 403; WebFetch of the SSRN Delivery.cfm URL gave 403; the Wayback CDX holds only abstract pages; the UWA repository record (curl) has no attached file; ScienceDirect is paywalled. Status unchanged. DOI correction: the log and the registry give 10.1016/j.intfin.2018.12.012, which OpenAlex resolves to "Mutual fund ownership and foreign exchange risk in Chinese firms". An OpenAlex title search returns this paper under 10.1016/j.intfin.2018.12.003. Flag for the lead, not decided here: the paper's conditioning variable is investor sentiment, which sits close to rule 7 (sentiment shelved). The liquidity-timing mechanism itself does not depend on it.

### K5-006
- **Citation:** Crain, S.J., Hoelscher, S.A. & Jones, J.S. (2020). "Fixing the Fix for Silver and Gold." ACRN Journal of Finance and Risk Perspectives, 9, 177–197. DOI 10.35944/jofrp.2020.9.1.013.
- **Retrieval:** Full text obtained. University mirror (bearworks.missouristate.edu) PDF was Cloudflare-blocked (`curl` returned a "Just a moment..." challenge page; `firecrawl_scrape` of the article landing page worked and gave the abstract, but the PDF link itself stayed blocked). Full text recovered from the journal's own site: DOAJ's record linked directly to `http://www.acrn-journals.eu/resources/jofrp09m.pdf` (the full Volume 9 issue PDF, 21 pages as fetched, containing this article at its original pagination 177–197), downloaded with `curl` and read with `pdftotext -layout`. CC-BY-SA open access (per the article's own rights statement).
- **Mechanism:** Compares gold and silver futures/spot volatility before vs. after the London gold/silver fix's 2014–2015 change from a small-bank telephone negotiation to an electronic multi-participant auction. Raw volatility is lower after the change, but after controlling for the downward time trend the authors report that the fix change significantly INCREASED volatility in silver and gold (corrected in the continuation run, P-K5-006-f and -g; the first run's text reported only the raw reduction).
- **Products/horizon:** Silver and gold futures on "the Chicago Mercantile Exchange Globex platform" (i.e., SI/GC-equivalent continuous series) plus LBMA spot fix prices; horizon is DAILY — this is a daily-bar structural-break study, not an intraday trading signal.
- **Cost assumptions:** not modeled; the paper studies volatility levels, not a tradeable strategy with costs.
- **Data window:** "January 1, 2008, through June 27, 2018" (silver); the gold fix change date March 20, 2015 is verified (P-K5-006-h); a shortened gold window 8/20/2014 – 10/20/2015 is also used (P-K5-006-g).
- **Quality tells:** none — data source, methodology (GARCH(1,1), Garman-Klass, Kruskol-Wallis) and dates are all explicit and traceable; this is a solid, non-speculative empirical paper.
- **Verified passages:**
  - P-K5-006-a (mechanism, pdftotext p.1): "The purpose of this study is to examine pricing patterns in the spot and futures contracts in the periods prior to and following the London fix changes for silver and gold to detect evidence of manipulation that may have been reduced due to the increased transparency of the fixing process."
  - P-K5-006-b (data window, pdftotext, "Data" section): "Daily prices, open interest, and the trading volume for futures contracts on silver and gold trading on the Chicago Mercantile Exchange Globex platform are obtained from Commodity Systems Incorporated over the sample period of January 1, 2008, through June 27, 2018."
  - P-K5-006-c (numeric/result, pdftotext, "Methodology and Results"): "the high price of the day minus the low price of the day is significantly lower in the post-fix change period indicating a reduction in volatility... In all instances, the standard deviations are significantly lower in the post-fix change period."
  - P-K5-006-d (gold fix mechanics, pdftotext p.2): "The LBMA gold price is set twice daily at 10:30 a.m. and 3:00 p.m. (London BST)."
  - P-K5-006-e (silver fix mechanics, pdftotext p.2): "The daily process consists of a series of electronic auction rounds starting at noon (12:00 London BST), during which each participant is required to input their buy volume and sell volume orders."
- **Numeric claims:** dates in P-K5-006-b; volatility-reduction direction (no specific t-stat or coefficient quoted here — the tables in the PDF contain them but were not individually transcribed given the scope of this pass; any specific coefficient the lead wants pulled should be requested as a follow-up, page ~181–188 tables 1–2).
- **Tags:** port of D.1 family H (daily-bar constructions), tested product-specifically on gold/silver futures. Intraday-feasible: NO — the entire mechanism and evidence base is a daily-closing-price volatility regime comparison across a multi-year pre/post structural break; it identifies a fact about the market (volatility fell after 2014–2015) but is not itself an intraday timing signal. It is background/context for the K5 CatalogWriter, not a candidate mechanism on its own.
- **Clusters tagged:** [K5] only.
  - P-K5-006-f (continuation run, re-fetched http://www.acrn-journals.eu/resources/jofrp09m.pdf by curl, pdftotext, Conclusion): "The results show that returns have been unaffected by the recent changes in the fixing processes, but volatilities in the futures and various spot markets are lower in the post-fix change period that spans approximately 3.5 years. However, after controlling for the time trend of generally decreasing overall futures market volatility throughout the sample period, further examination of the relationship between the futures market and the London spot market suggests that the fix change significantly increased volatility of prices in silver and gold markets, respectively."
  - P-K5-006-g (gold, Panel B discussion): "Thus, the gold fix change led to an increase in volatility in gold futures following the change to the gold fixing process. ... we use a shortened sample period of seven months prior to the gold fix change (March 20, 2015) to seven months after the gold fix change (8/20/2014 – 10/20/2015) to eliminate the potential for the confounding effect."
  - P-K5-006-h (History of the Gold Fix): "The change in the gold fix occurred on March 20, 2015, when the new auction platform replaced the twice-daily telephone conference fixing process by five market participants"
  - Continuation-run note: P-K5-006-c describes the silver raw-volatility result (Panel A, silver); read alone it overstates the paper's conclusion (see -f).

### K5-007
- **Citation:** Batten, J.A., Lucey, B.M., McGroarty, F., Peat, M. & Urquhart, A. (2017). "Stylized facts of intraday precious metals." PLOS ONE, 12(4), e0174232. DOI 10.1371/journal.pone.0174232.
- **Retrieval:** Full text obtained (PLOS ONE is fully open access). `firecrawl_scrape` of `journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0174232` returned the complete article (Introduction through Discussion); PMC mirror (pmc.ncbi.nlm.nih.gov) was blocked by a cookie wall and not used.
- **Mechanism:** Documents intraday stylized facts (periodicity in returns, volatility, volume, bid-ask spread) at 5-minute frequency for spot gold, silver, platinum, palladium (Reuters codes XAU/XAG/XPT/XPD — this is the LOTC spot/OTC market, not COMEX futures directly, though the paper notes COMEX is ~7.7% of gold turnover vs. ~78% for London spot); Granger causality between returns and volatility.
- **Products/horizon:** Spot precious metals as a non-CME leading indicator for K5 futures (gold, silver, platinum are all K5 products; palladium not traded); horizon: 5-minute intraday bars across the full 22:00–21:00 GMT trading day.
- **Cost assumptions:** not modeled — this is a stylized-facts/descriptive paper, not a strategy paper.
- **Data window:** "5-minute frequency for gold, silver, platinum and palladium from May 2000 to April 2015," split into three 5-year subsamples (2000–05, 2005–10, 2010–15).
- **Quality tells:** none — peer-reviewed, data source disclosed (Thomson Reuters Tick History), methodology explicit.
- **Verified passages:**
  - P-K5-007-a (abstract, firecrawl_scrape): "We find strong evidence of periodicity in returns, volatility, volume and bid-ask spread. Returns and volume both experience strong intraday periodicity linked to the opening and closing of major markets around the world while the bid-ask spread is at its lowest when European markets are open."
  - P-K5-007-b (data/methods section, firecrawl_scrape): "The markets of all four precious metals trade from Sunday 22.00 to Friday with a daily break between 21.00 and 22.00 GMT... we also split our sample into three equal-sized subsamples, from 1st May 2000 to 30th April 2005, 1st May 2005 to 30th April 2010 and 1st May 2010 to 30th April 2015."
  - P-K5-007-c (product/venue disclosure, firecrawl_scrape): "the two major centers for gold trading, London (physical, over-the-counter (LOTC) spot trade) and the New York Mercantile Exchange Futures Market (COMEX), totaling 85% (78.0% and 7.7% respectively) of global turnover value."
- **Numeric claims:** 78.0%/7.7% turnover split — P-K5-007-c; sample dates — P-K5-007-b.
- **Tags:** port of D.1 family A (session clock / intraday seasonality), tested product-specifically on precious metals spot (a non-CME leading instrument for K5 per section 1 of the partition). Intraday-feasible: yes as a session-timing background fact — this is descriptive of periodicity, not itself a trading rule, but supports a D.1-family-A candidate (session-open/close volume-and-spread pattern) for gold/silver/platinum futures.
- **Clusters tagged:** [K5] only (palladium not traded, ignored for K5 purposes).

### K5-008
- **Citation:** Cohen, G. (2022). "Intraday Trading of Precious Metals Futures Using Algorithmic Systems." Chaos, Solitons & Fractals, 154, 111676. DOI 10.1016/j.chaos.2021.111676.
- **Retrieval:** Paywalled at ScienceDirect (Purchase PDF required); however `firecrawl_scrape` of the abstract/preview page returned not just the abstract but the "Highlights," full "Introduction" section and "Data and methodologies"/"Results"/"Conclusions" section-snippets (Elsevier's public preview goes beyond a bare abstract for this article) — logged as "abstract + section snippets," not a bare abstract, but still not the complete paper (tables/full results section not retrieved).
- **Mechanism:** Builds and PSO-optimizes two rule-based intraday systems (RSI oscillator; Keltner Channel breakout) on minute and 60-minute bars for five precious-metals futures, comparing system returns to buy-and-hold.
- **Products/horizon:** "Gold, Silver, Copper, Platinum and Palladium" futures (GC/SI/HG/PL all K5 products; palladium not traded); horizon: minute bars up to 60-minute bars, explicitly intraday ("Intraday In the financial world describe securities that trade on the markets during regular business hours").
- **Cost assumptions:** not disclosed in the retrieved text; [unverified] whether commissions/slippage are modeled.
- **Data window:** "from the beginning of 2020 till the end of September 2021," minute-by-minute.
- **Quality tells:** single-author paper testing many parameter combinations (PSO optimization "with multiple objectives and under many constraints' variables") over a ~21-month window with no out-of-sample/holdout split disclosed in the retrieved text — high overfitting risk from parameter search on one window; treat headline return figures as a source-quality-flagged claim, not a validated result.
- **Verified passages:**
  - P-K5-008-a (Highlights, firecrawl_scrape): "We find that the RSI system outperformed the B&H returns for Gold, Silver, platinum and palladium and was beaten by the B&H returns for copper trades. The system has delivered 106.2%, 63.7%, 22.4% and 326.3% excess returns for Gold, Silver, platinum and palladium."
  - P-K5-008-b (Abstract, firecrawl_scrape): "Sixty minutes bars with 1.5 Average True rang Multiplier (MATR) have been found to be a fruitful configuration for the KC system trading Gold, Silver and Palladium providing better trading returns than the B&H strategy, by 64.72%, 58.5% and 310.25%, respectively."
  - P-K5-008-c (Data and methodologies section-snippet, firecrawl_scrape): "Our data is consisted of minute-by-minute price data of five major precious metals futures: Gold, Silver, Copper, Platinum and Palladium from the beginning of 2020 till the end of September 2021."
- **Numeric claims:** 106.2% / 63.7% / 22.4% / 326.3% (RSI excess returns, gold/silver/platinum/palladium) — P-K5-008-a; 64.72% / 58.5% / 310.25% (KC excess returns, gold/silver/palladium) — P-K5-008-b. All excess-return figures are as stated in the retrieved preview text over the single ~21-month sample; not independently re-derived.
- **Tags:** port of D.1 family C (short-horizon reversal/momentum via RSI) and G (coarser-bar timeframes, 60-minute KC), tested product-specifically on metals futures. Intraday-feasible: yes by construction (minute/60-minute bars, flat presumably each day though the retrieved text does not explicitly confirm daily flattening — [unverified] whether positions are held overnight; this must be checked against the full paper before any design borrows from it).
- **Clusters tagged:** [K5] only (palladium excluded from K5 scope; copper result is a negative finding, logged above).

### K5-009
- **Citation:** Wang, Z. & Lu, X. (2024). "COMEX Copper Futures Volatility Forecasting: Econometric Models and Deep Learning." arXiv:2409.08356 [q-fin.MF].
- **Retrieval:** Full text obtained — WebFetch saved the arXiv PDF to disk, read with `pdftotext -layout`.
- **Mechanism:** Forecasts COMEX copper futures realized volatility at daily and hourly horizons using GARCH/HAR econometric models vs. RNN/LSTM/GRU deep-learning models; does not propose a trading rule, only a volatility-forecasting comparison.
- **Products/horizon:** COMEX copper futures (HG); horizon: daily realized volatility (primary) and hourly high-frequency realized volatility (secondary) — this is a forecasting-accuracy paper, not a same-session entry/exit rule.
- **Cost assumptions:** none — no trading strategy or costs modeled.
- **Data window (continuation run, arXiv PDF re-fetched by curl):** daily COMEX copper 2000-01-04 to 2023-03-02 (Wind); minute data 2023-01-02 18:01 to 2023-04-13 03:27 for hourly RV (P-K5-009-b). Quality tell: the daily "realized volatility" is the squared daily return ("assuming M is 1"), and the high-frequency sample is about 3.5 months.
- **Quality tells:** none apparent from the retrieved abstract/introduction; standard econometrics/ML comparison paper, methodologically explicit (GARCH, HAR, RNN, LSTM, GRU named).
- **Verified passage:**
  - P-K5-009-a (Abstract, pdftotext of the arXiv PDF): "In forecasting daily realized volatility for COMEX copper futures with a rolling window approach, the econometric models, particularly HAR, outperform recurrent neural networks overall, with HAR achieving the lowest QLIKE loss function value. However, when the data is replaced with hourly high-frequency realized volatility, the deep learning models outperform the GARCH model."
- **Numeric claims:** none with a specific number quoted (QLIKE values not extracted); no numeric claim logged beyond the qualitative model-ranking above.
- **Tags:** port of D.1 family D (volatility state), tested product-specifically on COMEX copper. Intraday-feasible: this is a forecasting-accuracy study, not itself a trading rule — the volatility-state distinction (HAR wins daily, deep learning wins hourly) could inform a volatility-regime filter for an intraday copper rule, but the paper itself makes no trading claim and no flatten-by-15:08-CT question arises since nothing is held.
- **Clusters tagged:** [K5] only.
  - P-K5-009-b (section 3.1 Data Collection): "This article collects daily COMEX copper futures prices from the Wind database from 2000/1/4 to 2023/3/2. Daily log returns are calculated from the daily copper prices, and then assuming M is 1, a preliminary daily realized volatility is obtained as a volatility measure (which is actually the square of the daily return). And for high frequency data, this paper collects the price changes from 2023-01-02 18:01 to 2023-04-13 03:27, which in turn gives the hourly RV (which is actually the sum of the squares of the returns per minute)."

### K5-010
- **Citation:** LBMA / ICE Benchmark Administration. "LBMA Silver Price FAQs" (public documentation page, undated/current as of 2026-09-23).
- **Retrieval:** Full page obtained via `firecrawl_scrape` (genuine markdown fetch of the live LBMA page).
- **Mechanism:** Documents the LBMA Silver Price auction mechanics: a 30-second-round electronic auction starting at 12:00 London time, algorithmic matching of lakh-denominated buy/sell orders within a tolerance band, restarting rounds until equilibrium.
- **Products/horizon:** Silver (spot fix, a non-CME leading instrument for SI/SIL per partition section 1); horizon: the auction starts at 12:00 London = 06:00 CT when the UK and US are both on standard or both on daylight time, and 07:00 CT in the March and late-October/early-November weeks when only the US is on daylight time (conversion corrected in the continuation run; the first run's "05:00 CT-ish" was wrong) — this is background/reference documentation, not a study with a mechanism-and-effect claim.
- **Cost assumptions:** n/a (not a strategy source).
- **Data window:** n/a (current operational documentation).
- **Quality tells:** primary source (the benchmark administrator itself); fully reliable for mechanics, not for market-impact claims.
- **Verified passage:**
  - P-K5-010-a: "The auction takes place at 12 noon (UK time) each working day... The LBMA Silver Price is set in US dollars per troy ounce in a series of auction rounds, each lasting 30 seconds... In the first round the system algorithm will attempt to match buy and sell orders within the permitted tolerance level (3 lakhs). If the buy and sell orders are out of tolerance, the auction price will change and the auction will restart until the buy and sell volumes are in tolerance and the equilibrium price is set."
- **Numeric claims:** "30 seconds" per round, "3 lakhs" tolerance — both P-K5-010-a.
- **Tags:** background/reference, not a family port (this is documentation, not a research finding) — supports the mechanism claims in K5-001/002/006 above rather than standing alone as a candidate. Intraday-feasible: n/a (reference material).
- **Clusters tagged:** [K5] only.

### K5-011
- Citation: Hauptfleisch, M., Putnins, T.J. & Lucey, B.M. (2016). "Who Sets the Price of Gold? London or New York." Journal of Futures Markets 36(6), 564-586. DOI 10.1002/fut.21775. Working paper dated May 15, 2015 (the version read).
- Retrieval: full text of the working paper through firecrawl_scrape (pdf parser) of https://acfr.aut.ac.nz/__data/assets/pdf_file/0009/29790/T-Putnis-GoldILS-v4.3.pdf, 20:52 PDT. curl of the same URL returned a Cloudflare challenge. The published version was not read: Wiley is paywalled; a UTS OPUS copy ("GoldILS JFutMkt Forthcoming.pdf", found via OpenAlex) was not fetched.
- Mechanism: one-second price discovery (Hasbrouck IS, Gonzalo-Granger CS, information leadership share ILS) between COMEX gold futures and London OTC spot. COMEX leads on average despite less than a tenth of London's volume. Before COMEX's late-2006 electronic upgrade, the futures share rose while the COMEX floor was open; after 2007 the shares are stable through the day. The PM fix raises relative noise in London quotes, and US GDP and PPI releases raise the futures share.
- Products and horizon: GC against London spot (a non-CME signal instrument for GC, K5 under partition section 1); one-second data, measures estimated per day and per hour.
- Cost assumptions: none; a price-discovery measurement, not a strategy.
- Data window: 1997-01-01 to 2014-11-30, Thomson Reuters Tick History, best bid and ask quotes, one-second midquotes.
- Quality tells: working-paper text, whose numbers may differ from the JFM version. One internal inconsistency: the text calls start-of-sample IS and CS "only slightly above 50%" and then gives them as 67% and 61% (P-K5-011-c). Robustness results are "not reported, but are available from the authors upon request".
- P-K5-011-a (abstract): "Using intraday data during a 17-year period we find that although both markets contribute to price discovery, the New York futures play a larger role on average. This is striking given the volume of gold traded in New York is less than a tenth of the London spot volume, and illustrates the importance of market structure on the process of price discovery. We find considerable variation in price discovery shares both intraday and across years. The variation is related to the structure and liquidity of the markets, daylight hours, and macroeconomic announcements that affect the price of gold."
- P-K5-011-b (data): "Our sample period extends from January 1, 1997 to November 30, 2014. In total this includes 3,872 trading days and 51,702,414 one-second observations."
- P-K5-011-c (annual shares): "The IS and CS measures at the start of the sample are only slightly above 50% (67% and 61%, respectively). IS rises steadily until 2006, after which it remains consistently above 90%." and "The futures market in the first year of our sample has an ILS of 66%, which rises above 85% for the years 2003 to 2007, after which it falls slightly and remains stable around 70%."
- P-K5-011-d (intraday pattern): "The opening of floor trading at COMEX around 13:20 GMT (12:20 GMT) is associated with a substantial increase in the price discovery share of the futures market. ... From 2007 onwards, after COMEX introduced the new near 24-hour electronic GLOBEX platform, the intraday patterns are substantially different. There are no longer clear intraday shifts in the price discovery shares and instead, the price discovery shares remain relatively stable throughout the day."
- P-K5-011-e (fix and announcements): "We find weak evidence that the gold fixing increases the UK OTC market's share of price discovery. Also, our results indicate that US GDP and PPI announcements are associated with an increase in the US futures market's share of price discovery, whereas US employment announcements including Non-Farm Payroll are associated with an increase in noise but not price discovery share for either market."
- P-K5-011-f (PM fix noise): "The PMFIX coefficients for the CS and IS regressions are highly significant and positive, indicating that the relative level of noise between our two markets changes around the time of the fixing. We interpret this as an increase in the level of noise in the LOTC as liquidity providers may widen their spreads due to increased information asymmetry, or liquidity in general decreasing around the fixing."
- P-K5-011-g (platform change): "According to the regressions, CS, IS, and ILS increase by 19, 22, and 3 percentage points respectively after the change, holding other variables constant."
- P-K5-011-h (venue shares): "OTC spot market is more than ten times higher than that of the US futures market (78.0% market share compared to 7.7%)". Re-check: 78.0 / 7.7 = 10.1, consistent with "less than a tenth" (P-K5-011-a).
- Numeric claims: sample and counts (b); 67%, 61%, >90%, 66%, >85%, ~70% (c); 19, 22 and 3 pp (g); 78.0% and 7.7% (h).
- Tags: new to the program (cross-venue lead-lag with a non-CME instrument). Intraday-feasible: descriptive; no position is held, so the 15:08 CT limit does not arise. It measures which venue leads, not a trade.
- Clusters tagged: [K5].

### K5-012
- Citation: Aspris, A., Foley, S., Gratton, F. & O'Neill, P. (2017). "Transparency in Commodities Markets." EFMA 2017 Athens conference paper (working paper).
- Retrieval: full text. curl of http://efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2017-Athens/papers/EFMA2017_0580_fullpaper.pdf (the https URL fails SSL chain verification; the plain http URL served the same PDF), 26 pages, pdftotext.
- Mechanism: the 2014-2015 replacement of the London fix (gold, silver, platinum, palladium) by transparent electronic auctions shortened fix duration and lowered adjusted returns, volatility and return predictability in the linked COMEX futures around the fix. Quoted spreads peak just before the fix starts; depth dips before the start and recovers as the auction runs.
- Products and horizon: GC, SI, PL (and PA, not a K5 product) on Globex, plus gold and silver ETFs; one-minute data in a window from 30 minutes before to 60 minutes after the fix start.
- Cost assumptions: cites "approximately 1-2 (3-6) basis points" average execution cost for gold (silver) CME contracts (P-K5-012-c); no strategy is costed.
- Data window: 2012-02-14 to 2015-04-30 (P-K5-012-b); TRTH one-minute data; open-outcry trades excluded.
- Quality tells: conference draft, with tables at "<<Insert Table>>" placeholders in the text (the tables were not transcribed). The post-reform sample for gold is short (the gold auction began March 2015 and the sample ends April 2015); the authors say gold and platinum results are "statistically insignificant" and blame "the small sample of data in the post period". Likely the working-paper ancestor of K5-013 ([unverified]: different author list and emphasis).
- P-K5-012-a (abstract): "In this paper we analyse the duration of the price discovery process across the three introduced regimes and show that it has become more efficient. We observe a decline in the length of time required to reach the final benchmark price, and also show a reduction in the adjusted returns, volatility, and return predictability of the associated futures contract."
- P-K5-012-b (sample): "Our data extends from the 14th February 2012 to the 30th of April, 2015, a sample period that allows us to examine the interactions between the OTC and the financially linked futures and ETF markets."
- P-K5-012-c (costs): "We use data from the electronic GLOBEX platform and exclude quotes and trades from the open-outcry period. The average execution cost for gold (silver) contracts on the CME are approximately 1-2 (3-6) basis points (Marshall et al (2011)."
- P-K5-012-d (old-regime leakage): "We show in the former fix period, significant return advantages accrue to informed participants ahead of the announcement of the benchmark price. This pattern is consistent across all the precious metals, with the average amount of leakage between 4-10 basis points."
- P-K5-012-e (change in returns): "our results show a significant decline in cumulative adjusted returns for silver futures. ... The results for gold and platinum are consistent in terms of their direction, but are statistically insignificant. A possible cause of this is the small sample of data in the post period."
- P-K5-012-f (spreads around the fix): "quoted spreads are typically at their highest point immediately prior to the start of the fix, reflecting the uncertainty in the market about what the fix price will be. This uncertainty is however, typically resolved within a matter of minutes from the start."
- P-K5-012-g (depth): "we observe a noticeable decline in depth prior to the start of the fix, followed by a steady recovery as information is revealed to the market."
- P-K5-012-h (duration): "The LBMA Silver Price, which was the first of the OTC metals to switch to the new and more transparent electronic system, has seen a 60% reduction in the time taken to determine the benchmark price." and "For gold and silver, the fix is almost always complete within ten minutes of the opening submission."
- P-K5-012-i (post-reform return path): "The panels in Figure 4 reveal a similar returns process for the two periods; there is no significant leakage prior to the start of the fix and within minutes of the start, most of the price discovery process is complete."
- Numeric claims: dates (b); 1-2 and 3-6 bps (c); 4-10 bps (d); 60% and "within ten minutes" (h). Nothing recomputed; no table values transcribed.
- Tags: new to the program (London auction window effects on COMEX); extends K5-001 past the 2015 reform. Intraday-feasible: yes. The windows are minutes around 10:30 and 15:00 London (gold), 12:00 (silver) and 09:45 and 14:00 (platinum). In US Central time these are 03:45 to 09:00 CT when the UK and the US are both on standard or both on daylight time, and one hour later (04:45 to 10:00 CT) in the weeks when US daylight time has started and UK summer time has not (March), or UK summer time has ended and US daylight time has not (late October to early November); all well before 15:08 CT.
- Clusters tagged: [K5].

### K5-013
- Citation: Aspris, A., Foley, S. & O'Neill, P. (2020). "Benchmarks in the spotlight: The impact on exchange traded markets." Journal of Futures Markets 40(11), 1691-1710. DOI 10.1002/fut.22120. SSRN 3562073.
- Retrieval: ABSTRACT ONLY. The abstract came from the RePEc page by curl (https://ideas.repec.org/a/wly/jfutmk/v40y2020i11p1691-1710.html). Failed routes: Wiley (curl 403); SSRN (curl 403); OpenAlex lists no open-access location; Firecrawl out of credits.
- P-K5-013-a (abstract): "The Fix for precious metals is a global pricing benchmark that provides pricing and liquidity provision for market participants. We exploit the gradual change in the century old auction process to quantify the efficiencies related to more transparent pricing. Our focus is in the market impact of this change on exchange listed products. We find that reforms to the Fix have reduced quoted and effective bid-ask spreads and improved overall market depth."
- Mechanism, products and horizon: as K5-012, focused on spreads and depth of exchange-listed products around the fix. Costs, data window and quality tells: [unverified].
- Numeric claims: none.
- Tags: new to the program; intraday-feasible as K5-012. Probably the published descendant of K5-012 ([unverified]); if the lead treats them as one source, K5-013 is a duplicate id.
- Clusters tagged: [K5].

### K5-014
- Citation: Elder, J., Miao, H. & Ramchander, S. (2012). "Impact of macroeconomic news on metal futures." Journal of Banking & Finance 36(1), 51-65. DOI 10.1016/j.jbankfin.2011.06.007. Version read: manuscript "This version: June 7, 2011".
- Retrieval: full text. Colorado State University Mountain Scholar repository (https://mountainscholar.org/items/e073c497-6566-4d5b-8e13-b08f1ede2236 -> bitstream https://mountainscholar.org/bitstreams/21623442-a01d-45a6-879d-d645e781e52a/download), curl + pdftotext, 2,308 lines. The scispace.com PDF link returned 403.
- Mechanism: 19 scheduled US macro announcements; the surprise component moves 5-minute returns, realized volatility and volume of COMEX gold, silver and copper futures immediately. Better-than-expected growth news lowers gold and silver and raises copper. Effects dissipate within about 60 minutes. The 08:30 ET releases (nonfarm payrolls, durable goods) matter most for gold and silver; the 09:15 ET releases (industrial production, capacity utilization) matter most for copper.
- Products and horizon: GC, SI, HG; 1-minute sampled prices, 5-minute returns; 50-minute event window (10 minutes before to 40 after).
- Cost assumptions: none; no strategy.
- Data window: January 2002 to December 2008, tick data from the Futures Industry Institute; volume only for 2007-2008 (P-K5-014-b).
- Quality tells: manuscript version; the pit hours quoted describe 2002-2008 open outcry, not today's Globex-only market. Univariate R-squared figures are for single 5-minute windows.
- P-K5-014-a (abstract): "This paper uses intra-day data for the period 2002 through 2008 to examine the intensity, direction, and speed of impact of U.S. macroeconomic news announcements on the return, volatility and trading volume of three important commodities – gold, silver and copper futures. We find that the response of metal futures to economic news surprises is both swift and significant, with the 8:30 am set of announcements – in particular, nonfarm payrolls and durable goods orders – having the largest impact. Furthermore, announcements that reflect an unexpected improvement in the economy tend to have a negative impact on gold and silver prices; however, they tend to have a positive effect on copper prices."
- P-K5-014-b (data, section 4): "Our data on metals prices consists of intra-day, tick-by-tick, futures transaction prices for gold, silver and copper for the period January 2002 through December 2008. The data for trading volume is available only for 2007 and 2008. The futures data is obtained from the Futures Industry Institute." and "The futures prices are then sampled at 1-minute discrete intervals ... The 1-minute observations are then used to construct 5-minute return and volatility measures."
- P-K5-014-c (conclusions, size): "surprises in nonfarm payroll (released at 8:30 am) explain about 35% and 23% of the returns of gold and silver, respectively during the 8:30 to 8:35 time interval. Copper returns, on the hand, are more sensitive to the 9:15 set of announcements which include capacity utilization and industrial production."
- P-K5-014-d (persistence, conclusions): "our evidence indicates that the effect of macroeconomic news dissipates quickly, within about 60 minutes of the news release, and notably, and that several announcements have an asymmetric impact on market activity variables."
- P-K5-014-e (event window, section 4.2): "We examine price and volume in the study over a 50-minute time period: 10 minutes prior to the new release and 40 minutes after the new release."
- P-K5-014-f (literature, used for K5-015 and K5-018): "Christie-David, Chaudhry and Koch (2000) use intra-day 15-minute transaction prices between 1992 and 1995 to show that the impact of economic surprises on the return variance of gold and silver futures prices is less pronounced compared to interest rate futures. Cai, Cheung and Wong (2001) provide a detailed characterization of return volatility in gold futures using 5-minute returns between 1994 and 1997. They find that the impact of macroeconomic announcements is much smaller on gold compared to the impact on Treasury bond or currency markets, and only four announcements – jobs report, inflation, GDP and personal income – carry statistically significant effects on gold volatility."
- Numeric claims: 2002-2008 (a, b); 35% and 23% (c); about 60 minutes (d); 10 and 40 minutes (e).
- Tags: port of D.1 family E (calendar and events), tested product-specifically on GC, SI, HG. Intraday-feasible: yes (08:30 to 09:15 ET releases; response within minutes, gone within about an hour).
- Clusters tagged: [K5].

### K5-015
- Citation: Cai, J., Cheung, Y.-L. & Wong, M.C.S. (2001). "What moves the gold market?" Journal of Futures Markets 21(3), 257-278.
- Retrieval: ABSTRACT ONLY. The abstract came from RePEc by curl (https://ideas.repec.org/a/wly/jfutmk/v21y2001i3p257-278.html). Failed routes: Wiley PDF (curl 403); OpenAlex lists no open-access location; ResearchGate is request-only; Firecrawl out of credits.
- P-K5-015-a (abstract): "In this article, we provide a detailed characterization of the intraday return volatility in gold futures contracts traded on the COMEX division of the New York Mercantile Exchange. The approach allows the study of intraday patterns, interday ARCH effects, and announcement effects in a coherent framework. We show that the intraday patterns exert a profound impact on the dynamics of return volatility. Among the 23 U.S. macroeconomic announcements, we identify employment reports, gross domestic product, consumer price index, and personal income as having the greatest impact."
- Data window: 5-minute returns, 1994-1997, SECONDARY only (P-K5-014-f); not verified in the primary.
- Mechanism: intraday volatility seasonality and announcement effects in COMEX gold. Costs and quality tells: [unverified].
- Numeric claims: "23 U.S. macroeconomic announcements" (a).
- Tags: port of D.1 families A (session clock) and E (events), on GC. Intraday-feasible: yes (descriptive volatility pattern).
- Clusters tagged: [K5].

### K5-016
- Citation: Chai, E.F.L., Lee, A.D. & Wang, J. (2015). "Global information distribution in the gold OTC markets." International Review of Financial Analysis 41, 206-217. DOI 10.1016/j.irfa.2015.05.001. Version read: manuscript dated March 2015.
- Retrieval: full text. OpenAlex gave the UTS OPUS handle http://hdl.handle.net/10453/77450 (curl); its citation_pdf_url is a .docx manuscript (https://opus.lib.uts.edu.au/bitstream/10453/39810/1/Price%20Discovery%20in%20the%20Global%20Gold%20Market_JX%20Lee%20150324%20-%20FINAL%20with%20contact%20details.docx), downloaded with curl and read from word/document.xml. The figshare record has no files.
- Mechanism: the 24-hour OTC spot gold day is split into four sequential sessions. Information share (two-scale realized variance) is highest per hour in the 2-hour London afternoon / New York morning overlap.
- Products and horizon: London OTC spot gold (XAU=), a non-CME signal instrument for GC (K5 under partition section 1); 1-minute data aggregated per session.
- Cost assumptions: none.
- Data window: 1996-01-01 to 2012-12-31, TRTH 1-minute (P-K5-016-b).
- Quality tells: manuscript version; spot quotes from contributors, not transactions on an exchange.
- P-K5-016-a (abstract): "we estimate the information shares of Asia, Europe, London/New York and the United States, with London/New York covering the two-hour overlapping trading in London afternoon and New York morning. We find that over the sample period of 1996 to 2012, the average daily information shares are 17%, 31%, 22%, and 30% for Asia, Europe, London/New York and U.S., respectively. On a per-hour basis, the information share of London/New York is over two and half times of those of the rest of Europe and U.S., and over five times of the information share of Asia."
- P-K5-016-b (data): "We extract data from TRTH at 1-minute intervals from January 1, 1996 to December 31, 2012."
- P-K5-016-c (session definitions): "During non-DST, Asia covers 23 GMT to 6 GMT, Europe covers 7 GMT to 13 GMT, London/NYC covers 14 GMT to 15 GMT, and U.S. covers 16 GMT to 22 GMT." and "The two-hour London/New York market covers 2 to 4 pm London local time and 9 to 11 am New York local time."
- P-K5-016-d (per-hour shares): "On a per-hour basis, the information shares are 2.1%, 4.4%, 11%, and 4.3% respectively. Clearly trading in Asia has the least information content, and trading during the 2-hour London/New York period has the highest information content."
- Numeric re-check: 17/8 h = 2.1; 31/7 h = 4.4; 22/2 h = 11; 30/7 h = 4.3 (hour counts from P-K5-016-c). All match.
- Tags: port of D.1 family A (session clock), measured on the spot gold market that leads or accompanies GC. Intraday-feasible: descriptive; the 08:00-10:00 CT (9-11 am New York) window lies inside the trading day.
- Clusters tagged: [K5].

### K5-017
- Citation: Sobti, N., Sehgal, S. & Ilango, B. (2021). "How do macroeconomic news surprises affect round-the-clock price discovery of gold?" International Review of Financial Analysis 78, 101893.
- Retrieval: ABSTRACT ONLY. The abstract came from RePEc by curl (https://ideas.repec.org/a/eee/finana/v78y2021ics1057521921002209.html). Failed routes: OpenAlex says closed with no repository full text; ScienceDirect paywalled; Firecrawl out of credits.
- P-K5-017-a (abstract): "We examine round-the-clock international price discovery of gold among the major gold markets—New York, London and Shanghai during news-intensive and no-news time zones using one-minute data. Using GMM based parallel price discovery measure, we find global leadership of the US as New York gold futures lead across five time zones with 56% information share. New York/London (Nylon) timezone (51%) is the most informative trading session in sequential price discovery for all markets in 24-h. Our aggregate and disaggregate news analysis reveals that the US news surprises have a substantial and positive impact on its price discovery leadership while Eurozone news surprises have a negative impact and Chinese news have negligible impact."
- Numeric claims: 56% and 51% (a). Data window, costs, quality: [unverified].
- Tags: new to the program (cross-venue lead-lag, London and Shanghai as non-CME signal instruments for GC). Intraday-feasible: descriptive, one-minute.
- Clusters tagged: [K5]. The Eurozone and Chinese news legs concern macro news moving gold, which is K5 under rule 5, not a cross-cluster trade.

### K5-018
- Citation: Christie-David, R., Chaudhry, M. & Koch, T.W. (2000). "Do macroeconomics news releases affect gold and silver prices?" Journal of Economics and Business 52(5), 405-421. DOI 10.1016/S0148-6195(00)00029-1.
- Retrieval: FAILED; neither abstract nor full text. It passed pre-filter on its title (gold and silver futures, macro news). RePEc (curl) says "No abstract is available for this item"; Semantic Scholar API reports the abstract "elided by the publisher" and closed access; OpenAlex has no open-access location; Firecrawl out of credits.
- Only a secondary description exists (P-K5-014-f): 15-minute transaction prices, 1992-1995; the effect on gold and silver variance is smaller than on interest-rate futures. [unverified in the primary.]
- Tags: port of D.1 family E on GC and SI; intraday-feasible as described.
- Clusters tagged: [K5].

### K5-019
- Citation: Smales, L.A. (2015). "Examining the impact of macroeconomic announcements on gold futures in a VAR-GARCH framework." Applied Economics Letters 22(9). DOI 10.1080/13504851.2014.972538.
- Retrieval: full text (manuscript). OpenAlex oa_url https://espace.curtin.edu.au/bitstream/20.500.11937/28039/2/227202.pdf; retrieved from the Wayback capture of 2023-11-19 (curl, `id_` raw), pdftotext.
- Mechanism: COMEX gold 30-second returns, volatility, spreads and volume around 08:30 ET releases in a VAR-GARCH. Activity spikes at the release and is back to normal within about 3 minutes. Higher volatility widens spreads, which lowers volume.
- Products and horizon: GC; 30-second intervals from 15 minutes before to 45 minutes after the release.
- Cost assumptions: bid-ask spread is measured as a variable; no strategy cost.
- Data window: 2006-11-24 to 2012-12-31, 1,532 trading days, TRTH (P-K5-019-b); the same sample and author as K5-004.
- Quality tells: short letter; not independent of K5-004 (same data).
- P-K5-019-a (abstract): "This article considers the impact of major scheduled US macroeconomic announcements on the COMEX gold futures market in a high-frequency setting. A VAR-GARCH framework identifies the significant relationship between the release of macroeconomic news and measures of market activity. There is a well-defined link between (higher) volatility, (higher) trading costs and (lower) transaction volume."
- P-K5-019-b (data): "History (TRTH) provided by SIRCA for the period 24th November 2006 – 31st December 2012, a total of 1,532 trading days" and "All announcements occur at 08:30AM (EST), just 10-minutes after the official market open."
- P-K5-019-c (decay): "There is a clear jump in all measures of market activity as the announcement is released, this subsides to a level statistically indistinguishable from non-announcement days within 3-minutes (6 intervals). A spike in market activity of a lower magnitude is also registered as the trading pit opens in Chicago (10-minutes prior to the release)." and "the impact is short-lived with volatility and returns returning to normal within approximately 2½-min (5 x 30-sec intervals)."
- Numeric claims: 1,532 days and dates (b); 3 minutes and 2.5 minutes (c).
- Tags: port of D.1 family E on GC. Intraday-feasible: yes.
- Clusters tagged: [K5].

### K5-020
- Citation: Jiang, Y., Kellard, N. & Liu, X. (2020). "Night trading and market quality: Evidence from Chinese and US precious metal futures markets." Journal of Futures Markets 40(10). DOI 10.1002/fut.22147. Open access.
- Retrieval: full text. The Wiley pdfdirect URL gave 403 by curl and by WebFetch; the Wayback capture redirected to a cookie page. The copy read is the University of Essex repository record https://repository.essex.ac.uk/27740/ -> https://repository.essex.ac.uk/27740/1/fut.22147.pdf (curl, pdftotext, 1,356 lines), the typeset article (running head "JIANG ET AL.").
- Mechanism: in July 2013 SHFE opened a night session (21:00-02:30 Beijing) that overlaps the COMEX US daytime session. Afterwards SHFE liquidity rose, SHFE's first-hour volatility fell, SHFE gold's price-discovery share fell relative to COMEX, and volatility spillovers rose in both directions, mostly from the US to China.
- Products and horizon: SHFE gold and silver against COMEX gold and silver (SHFE is a non-CME signal instrument for GC and SI, K5 under partition section 1); daily and intraday data.
- Cost assumptions: none; no strategy.
- Data window: January 2008 to April 2016 (P-K5-020-b).
- Quality tells: typeset open-access version. Numeric re-check: the text equates 9:00 p.m. China with "9:00 a.m. Eastern Standard Time". China is UTC+8, so 21:00 Beijing is 13:00 UTC, which is 08:00 EST or 09:00 EDT. The stated equivalence holds only under US daylight time.
- P-K5-020-a (session facts): "From July 2013, an additional session was added which runs from 9:00 p.m. to 2:30 a.m. the following day" and "By opening at 9:00 p.m. in China, which is 9:00 a.m. Eastern Standard Time (EST) in New York, the SHFE trading for gold and silver futures now overlaps with the active trading period in the United States given that the COMEX opens at 8:20 a.m. EST."
- P-K5-020-b (sample): "Employing a sample period from January 2008 to April 2016, our empirical tests validate our hypotheses to a large extent but also reveal some unexpected findings."
- P-K5-020-c (price discovery): "we show that for gold, price discovery share actually falls relative to the United States after the introduction of night trading. However, we posit this is not a sign of weakening market quality but the contrary." and footnote 3: "price discovery measures for Chinese silver futures rise after the introduction of night trading, albeit from a very low base. ... US silver futures still dominate in terms of price discovery in postnight trading."
- P-K5-020-d (spillovers): "directional (and total) spillovers grow following the introduction of night trading but particularly from the United States to China for both commodities."
- P-K5-020-e (opening volatility): "comparing the first daylight trading hour in China pre- and postnight trading, Roll, Amihud and realized volatility measures are lower for the postnight trading subsample."
- Numeric claims: session hours (a); sample (b). No table values transcribed.
- Tags: new to the program (Asian-session interaction for precious metals). Intraday-feasible: descriptive. The SHFE night session (21:00-02:30 Beijing = 13:00-18:30 UTC = 08:00-13:30 CDT in US summer, 07:00-12:30 CST in US winter) overlaps the whole US morning and ends before 15:08 CT. The evidence says COMEX leads, not SHFE.
- Clusters tagged: [K5].

### K5-021
- Citation: Sehgal, S., Sobti, N. & Diesting, F. (2021). "Who leads in intraday gold price discovery and volatility connectedness: Spot, futures, or exchange-traded fund?" Journal of Futures Markets 41. DOI 10.1002/fut.22208.
- Retrieval: ABSTRACT ONLY, from the OpenAlex API (Crossref-deposited abstract reconstructed from OpenAlex's inverted index; fetched by me via curl, not a search summary). Failed routes: OpenAlex has no open-access location; Wiley curl 403; Firecrawl out of credits; WebSearch budget exhausted, so no author-page search was possible.
- P-K5-021-a (abstract): "We examine intraday price discovery and volatility connectedness among three gold instruments—spot, futures, and ETF—across mature and emerging gold markets in domestic and international settings from 2010 to 2018. Using the network approach, we find that gold futures are a global leader in price discovery and volatility spillover. However, during 2016–2018, physical-gold-backed ETF and spot challenge the futures' leadership in New York and Shanghai."
- Data window: 2010-2018 (a). Costs and quality: [unverified]. Same authors (Sehgal, Sobti) as K5-017.
- Tags: new to the program (cross-instrument lead-lag for GC). Intraday-feasible: descriptive.
- Clusters tagged: [K5].

### K5-022
- Citation: Lauterbach, B. & Monroe, M.A. (1989). "Evidence on the effect of information and noise trading on intraday gold futures returns." Journal of Futures Markets 9(4). DOI 10.1002/fut.3990090404.
- Retrieval: FAILED. It passed pre-filter on its title (GC, intraday). OpenAlex has no abstract and no open-access location; Wiley is closed (curl 403 on the Wiley domain for every JFM item tried this run). Everything beyond the title is [unverified]. Data are 1980s pit-era, per the publication year.
- Tags: [unverified]; the title suggests D.1 family C (short-horizon reversal/momentum) on GC.
- Clusters tagged: [K5].

### K5-023
- Citation: Martell, T.F. & Trevino, R.C. (1990). "The intraday behavior of commodity futures prices." Journal of Futures Markets 10(6). DOI 10.1002/fut.3990100608.
- Retrieval: FAILED. Title-level pass only (intraday commodity futures, which may include metals); OpenAlex has no abstract and no open-access location; Wiley closed. Whether it covers any K5 product is [unverified]. If it is a multi-commodity panel, rule 3 applies to whoever reads it.
- Clusters tagged: [K5] (provisional).

### K5-024
- Citation: Awartani, B., Hussain, S.M. & Virk, N.S. (2024). "How do the gold intra-day returns and volatility react to monetary policy shocks?" International Review of Financial Analysis, 103486. DOI 10.1016/j.irfa.2024.103486. Version read: the authors' final review manuscript ("IRFA_review_final.pdf").
- Retrieval: full text. OpenAlex oa_url pointed to figshare article 32489703; its file list (figshare API, curl) gave https://ndownloader.figshare.com/files/65204829, downloaded with curl and read with pdftotext (1,920 lines).
- Mechanism: gold futures 5-minute and 10-minute returns and volatility after FOMC rate surprises. Loosening surprises move gold more than tightening surprises of the same size, and adjustment continues past 5 minutes: the 10-minute adjustment is about three times the 5-minute one.
- Products and horizon: NYMEX/COMEX gold futures (GC); 5-minute bars; windows 5 and 10 minutes after the 14:00 ET FOMC announcement.
- Cost assumptions: none; efficiency test, no strategy.
- Data window: 2007-01-02 to 2020-12-31, Olsen data, continuous front-contract series (P-K5-024-c).
- Quality tells: manuscript, not the typeset version. Numeric re-check: "1,244.448" returns (decimal typo for 1,244,448) divided by 288 bars per day is about 4,321 days. That exceeds the roughly 3,650 weekdays in 2007-2020, so how weekends and holidays enter the series is [unverified]. Conclusions about "inefficiency" are the authors' and are not costed.
- P-K5-024-a (abstract, figshare record and PDF): "The gold returns and volatility 5 min after the shock are found to be more sensitive to looser than tighter FOMC rate announcement changes. ... Moreover, we find that the gold price adjustment and its volatility adjustment continue for longer than five minutes after the FOMC shock. This suggests potential short-term inefficiencies in the gold market concerning the short-term rates."
- P-K5-024-b (results): "Outputs show that positive monetary policy shocks tend to reduce the price of gold and increase its volatility 5 and 10 minutes after the announcement. However, the adjustment 10 minutes after the shock is significantly threefold higher than after 5 minutes."
- P-K5-024-c (data): "The 5-minute intraday price data of gold futures contracts traded at the New York Mercantile Exchange (NYMEX) are obtained from Olsen data. We construct the continuous series from the futures contracts by frontloading and rolling over the future gold contracts. The data covers the period from January 2, 2007, through December 31, 2020. It contains 1,244.448 equally spaced 5-minute gold futures returns."
- Numeric claims: "threefold" (b); dates and count (c).
- Tags: port of D.1 family E (FOMC event) on GC. Intraday-feasible: yes (14:00 ET = 13:00 CT announcement; a 10-minute window ends at 13:10 CT, before 15:08 CT).
- Clusters tagged: [K5]. This is not a K8 item: the rate surprise is the event, and gold is the only traded product (rule 5).

### K5-025
- Citation: Iwatsubo, K., Watkins, C. & Xu, T. (2018). "Intraday seasonality in efficiency, liquidity, volatility and volume: Platinum and gold futures in Tokyo and New York." Journal of Commodity Markets. DOI 10.1016/j.jcomm.2018.05.001 (SSRN 3021533).
- Retrieval: ABSTRACT ONLY, from the OpenAlex API (abstract text fetched by curl). OpenAlex lists it as hybrid open access (cc-by-nc-nd), but the full-text routes failed: ScienceDirect /pdfft (curl 403); the Elsevier API text/plain link requires a key (HTTP 400); the only Wayback capture (2024-08-28) is a 403 page with no article text; SSRN is blocked by curl; no repository copy exists per OpenAlex; Firecrawl out of credits.
- P-K5-025-a (abstract): "Our analysis indicates that both platinum and gold markets in Tokyo are dominated by uninformed trading, while there is evidence supporting both uninformed and informed trading in New York. Separating global trading hours into Tokyo, London and New York day sessions, we also find that uninformed trading is more prevalent during the Tokyo day session while informed trading dominates the New York day session for both metals in both locations."
- Products and horizon: PL and GC (COMEX/NYMEX) and TOCOM platinum and gold; intraday sessions. Data window, costs and quality: [unverified].
- Tags: port of D.1 family A (session clock) on PL and GC. Intraday-feasible: descriptive.
- Clusters tagged: [K5].

### K5-026
- Citation: Batten, J.A., Lucey, B.M. & Peat, M. (2016). "Gold and silver manipulation: What can be empirically verified?" Economic Modelling. DOI 10.1016/j.econmod.2016.03.005 (SSRN 2721250).
- Retrieval: FAILED; no abstract obtained. Title-level pass (gold and silver fix manipulation). OpenAlex says closed with no abstract; SSRN is blocked by curl; Firecrawl out of credits; WebSearch budget exhausted before a repository search could be run. Everything else is [unverified].
- Clusters tagged: [K5].

### K5-027
- Citation: Sobti, N. (2025). "What triggers intraday price jumps and co-jumps in gold?" International Review of Financial Analysis, 104380. DOI 10.1016/j.irfa.2025.104380.
- Retrieval: FAILED; no abstract obtained. Title-level pass (gold intraday jumps). OpenAlex says closed with no abstract; ScienceDirect paywalled; Firecrawl out of credits. Everything else is [unverified]. Same author as K5-017 and K5-021.
- Clusters tagged: [K5].

### K5-028 (PANEL SOURCE, rule 3: gold [K5] and oil [K4])
- Citation: Caporale, G.M. & Plastun, A. (2021). "Gold and oil prices: abnormal returns, momentum and contrarian effects." Financial Markets and Portfolio Management. DOI 10.1007/s11408-021-00380-w. Open access.
- Retrieval: full text, 16 pages. Springer PDF by curl returned an HTML page; the Sumy State University repository copy gave curl 403; the Wayback capture (2024, `id_` raw) of https://link.springer.com/content/pdf/10.1007/s11408-021-00380-w.pdf gave the typeset PDF, read with pdftotext.
- Mechanism: a day with an abnormal daily return (dynamic threshold) can be detected intraday, and the price keeps moving in that direction until the end of that day (momentum). On the next day, oil continues for the first few hours (momentum) while gold reverses (contrarian). Trading simulations use estimated "timing parameters".
- Products and horizon: gold [K5] and oil [K4]; hourly data; intraday, from the detection hour to the end of day, and the first hours of the next day.
- Cost assumptions: none in the simulations (P-K5-028-c).
- Data window: 2009-01-01 to 2020-03-31, hourly and daily, MetaQuotes Software Corp. data, "GMT + 3 time zone" (P-K5-028-b).
- Quality tells: (1) MetaQuotes data are broker (MetaTrader) prices, not CME futures prices; the text does not name the instrument. (2) No transaction costs. (3) "Profit % per year" equals total profit divided by 10 (41.44 -> 4.14; 77.79 -> 7.78), but the sample spans about 11.25 years. (4) Day boundaries are at GMT+3 midnight = 21:00 UTC = 15:00 CST / 16:00 CDT. A "till the end of the day" exit therefore falls after 15:08 CT in US summer; whether the broker clock shifts with daylight time is [unverified]. (5) The gold contrarian strategy is not statistically different from random (Tables 3 and 4, "Not rejected").
- P-K5-028-a (abstract) [K5][K4]: "Prices tend to move in the direction of abnormal returns till the end of the day when these occur. The presence of abnormal returns can usually be detected before the end of the day by estimating specific timing parameters, and a momentum effect can be detected. On the following day two different price patterns are detected: a momentum effect for oil prices and a contrarian effect for gold prices, respectively. These effects are limited in time, and the corresponding timing parameters are estimated."
- P-K5-028-b (data) [K5][K4]: "Daily and hourly data for gold and oil over the period 01.01.2009–31.03.2020 (GMT + 3 time zone) are used. ... The data source is MetaQuotes Software Corp."
- P-K5-028-c (costs) [K5][K4]: "Our analysis does not incorporate transaction costs (spreads, broker or bank fees, swaps etc.), and therefore it is only a proxy for actual trading. ... In the case of gold the spread is only 0.02% per trade, which implies that the error in our profit estimates is around 1%."
- P-K5-028-d (gold timing) [K5]: "Table 4 reports the timing parameters, which imply that anomaly appears are after 5 p.m. in the case of positive abnormal returns and after 7 p.m. in the case of negative ones." (GMT+3 clock: 17:00 = 08:00 CST / 09:00 CDT; 19:00 = 10:00 CST / 11:00 CDT, if the clock is fixed GMT+3.)
- P-K5-028-e (simulation, Table 3, positive abnormal returns) [K5]: "Strategy 1 Gold 59 51 86 41.44 4.14 0.70 5.61 Rejected" and "Golda 59 35 59 4.26 0.43 0.07 1.36 Not rejected" (a = contrarian strategy). [K4]: "Oil 96 54 56 213.60 21.36 2.22 12.23 Rejected".
- P-K5-028-f (simulation, Table 4, negative abnormal returns) [K5]: "Gold 74 53 72 77.79 7.78 1.05 8.17 Rejected" and "Gold* 74 43 58.1 11.3 1.1 0.15 0.73 Not rejected". [K4]: "Oil 89 59 66 369.56 36.96 4.15 8.60 Rejected".
- Numeric re-checks (gold): 51/59 = 86.4% (86 printed); 41.44/59 = 0.70; 53/74 = 71.6% (72); 77.79/74 = 1.05. All consistent. Per-year figures: see quality tell (3).
- Tags: port of D.1 family C (short-horizon momentum and reversal) with a daily-threshold trigger, tested on gold [K5] (and oil [K4]). Intraday-feasible: partly. Entry after intraday detection and an exit before 15:08 CT is feasible. The simulated exit at the GMT+3 day end (15:00 CST / 16:00 CDT) is not reachable in US summer. The next-day gold contrarian leg is intraday.
- Clusters tagged: [K5], [K4]. K4's CatalogWriter reads the [K4] passages here.

### K5-029 (PANEL SOURCE, rule 3: [K5] metals, [K4] energy, [K6] grains)
- Citation: Borgards, O., Czudaj, R.L. & Hoang, T.H.V. (2021). "Price overreactions in the commodity futures market: An intraday analysis of the Covid-19 pandemic impact." Resources Policy 71, 101966. DOI 10.1016/j.resourpol.2020.101966. PMC9759686 (Elsevier COVID-19 collection).
- Retrieval: full text from the Europe PMC REST API (https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9759686/fullTextXML, curl), tags stripped.
- Mechanism: large intraday price changes (beyond a dynamic decile threshold) are followed by proportional reversals in 20 front-month commodity futures at 1-minute to 1-hour frequencies. A contrarian trade after the top or bottom decile move is profitable before costs, more so during Covid-19.
- Products and horizon: [K5] GC, SI, PL, HG (and PA, LME-style AA/LX/LN, not K5); [K4] CL, HO, NG (and Brent); [K6] W, C, S, BO (and softs, not in any cluster); 1 min to 1 h.
- Cost assumptions: none modelled; the authors assert costs are negligible (P-K5-029-d). The holding period of the contrarian trade was not extracted: [unverified].
- Data window: 2019-11-20 to 2020-06-03, split into pre-Covid (to 2020-01-31) and Covid periods (P-K5-029-a).
- Quality tells: about six months of data, dominated by the Covid-19 shock (including negative WTI); decile thresholds; no out-of-sample test was seen in the text read; cost claim unquantified.
- P-K5-029-a (abstract) [K5][K4][K6]: "The objective of this paper is to examine the overreaction behavior of 20 commodity futures based on intraday data from November 20, 2019 to June 3, 2020 with a focus on the impact of the Covid-19 pandemic. ... Our findings also indicate that soft and metal commodities show much less overreactions than precious metals and especially energy commodities."
- P-K5-029-b (products) [K5][K4][K6]: "The commodity futures include WTI crude oil (CL), Brent crude oil (CO), heating oil (HO), natural gas (NG), gold (GC), silver (SI), platinum (PL), palladium (PA), copper (HG), aluminium (AA), zinc (LX), nickel (LN), wheat (W), corn (C), soybeans (S), soybean oil (BO), cocoa (CC), coffee (KC), sugar (SB) and cotton (CT)."
- P-K5-029-c (strategy returns) [K5]: "almost all commodities have higher trading returns with exception of industrial metals which have a 0.98% lower but still positive return in the first decile" and "the metals index would have generated a 4.0% (5.0%) compounded return over the pandemic period after positive (negative) first decile overreactions for the 1-h frequency". [K4]: "An investor who would have traded all crude oil long positions after the 10% highest negative price changes, would have also traded this price reversal and consequently would have realized a trading return of 11.91%".
- P-K5-029-d (costs) [K5][K4][K6]: "As transaction costs in futures trading are negligible, the net-of-fees trading results would be still positive in both periods for positive and negative initial price changes."
- Numeric claims: dates (a); 0.98%, 4.0%, 5.0% (c); 11.91% [K4] (c). Not recomputed (per-commodity tables not transcribed).
- Tags: port of D.1 family C (short-horizon reversal), tested product-specifically per commodity. Intraday-feasible: yes by construction (1 min to 1 h bars); exit timing [unverified].
- Clusters tagged: [K5], [K4], [K6]. The K4 and K6 CatalogWriters read the tagged passages here.

### K5-030
- Citation: Gu, C., Kurov, A. & Stan, R. (2023). "Monetary policy and uncertainty resolution in commodity markets." Finance Research Letters, 103907. DOI 10.1016/j.frl.2023.103907.
- Retrieval: FAILED; title-level pass only (container 3, Kurov; FOMC and commodity futures, possibly including metals). Crossref deposits no abstract; the Semantic Scholar API returns abstract null and status CLOSED; OpenAlex was out of its daily budget; ScienceDirect paywalled; Firecrawl out of credits. Whether it covers any K5 product, and whether it is a panel source under rule 3, is [unverified]. Claimed as [K5] only; the lead may reassign.
- Clusters tagged: [K5] (provisional).

### K5-031
- Citation: Lyocsa, S., Todorova, N. & Zhu, (initial not given) (2026). "Relative Valuation in Precious Metals Markets." SSRN 7170627 (earlier version SSRN 6381672).
- Retrieval: ABSTRACT ONLY, from the Crossref API record for 10.2139/ssrn.7170627 (curl). SSRN full text is blocked (curl 403); Firecrawl out of credits.
- P-K5-031-a (abstract): "We estimate valuation pressure from the magnitude of unexpected deviations in the gold-silver ratio and use it as a measure of relative price misalignment. ... Using intraday data on gold and silver futures from 2009 to 2025, we find that valuation pressure predicts higher variance from one day to three months ahead. Across these horizons, a one-standard-deviation increase is associated with variance increases averaging about 3% for gold and 4% for silver. Rebalancing pressure, which combines valuation pressure with unexpected trading volume, reduces future volatility in the silver market. ... Adding valuation pressure to a HAR model with gold implied volatility improves forecasting accuracy for both metals across the reported horizons."
- Products and horizon: GC and SI futures (inside-metals gold-silver ratio); forecasts next-day to three-month realized variance. Costs and quality: [unverified]. Working paper.
- Numeric claims: 2009-2025; about 3% and 4% (a).
- Tags: port of D.1 family D (volatility state), with a gold-silver ratio conditioning variable (new to the program). Intraday-feasible: as a filter read from prior-day information; it predicts variance, not direction.
- Clusters tagged: [K5].

### K5-032
- Citation: Barzykin, A., Bergault, P. & Gueant, O. (2024, v5 18 Jan 2026). "Market Making in Spot Precious Metals." arXiv:2404.15478 [q-fin.TR].
- Retrieval: full text, arXiv PDF v5 (curl, pdftotext, 14 pages).
- Mechanism: the futures-minus-spot Exchange for Physical (EFP) spread in gold mean-reverts on several time scales, from intraday to weekly (nested Ornstein-Uhlenbeck). A spot market maker hedging in futures skews quotes toward EFP reversion. Direct EFP arbitrage is rare because it requires crossing two spreads.
- Products and horizon: gold spot (XAUUSD) against COMEX gold futures; intraday to days.
- Cost assumptions: hedging costs in spot and futures appear in the control problem; "one would have to cross two spreads" to enter an EFP position (P-K5-032-c).
- Data window: EFP illustration for 2023 (Figure 1); one-day backtest on XAUUSD, 12 January 2024 (Figure 9).
- Quality tells: a stochastic-control model paper by a dealer (HSBC) and academics; the empirical content is illustrative (a single-day backtest). The strategy needs an OTC spot leg, which a TopstepX futures-only account cannot trade (a fact about the instrument set, not a verdict).
- P-K5-032-a (abstract): "The primary challenge of market making in spot precious metals is navigating the liquidity that is mainly provided by futures contracts. The Exchange for Physical (EFP) spread, which is the price difference between futures and spot, plays a pivotal role and exhibits multiple modes of relaxation corresponding to the diverse trading horizons of market participants."
- P-K5-032-b (EFP time scales, Introduction and Figure 1 caption): "as inspired by the observation of multiple relaxation times in the market ranging from hours to days" and "Zoom in on 21 July also shows OTC forward rate – OTC FWD – (red) and demonstrates intraday mean reversion. Daily median difference in basis points between implied EFP and OTC forward rate (blue) illustrates mean reversion on a weekly scale."
- P-K5-032-c (arbitrage rarity): "Figure 5 demonstrates that EFP mean reversion will only lead to rare direct arbitrage opportunities under strong risk aversion. This is related to the cost of opportunistically entering into an EFP position (one would have to cross two spreads)."
- Numeric claims: none beyond dates.
- Tags: new to the program (futures-spot basis dynamics for GC). Intraday-feasible: the futures leg alone is intraday; the mechanism as modelled needs the spot leg.
- Clusters tagged: [K5].
## 4. Flags for K8 (cross-cluster; not read further)

Run 1:
- Multiple sources (not pinned) | gold vs the US dollar and real interest rates | legs: gold (K5), dollar/rates (K3/K2) | dollar-and-gold relationship, K8 per partition section 3
- Wright Blogs, "Metals as Macro Signals: Reading Gold, Silver and Copper in a Fragile World" (not read) | metals as cross-asset macro signal | legs: metals (K5) and macro/cross-asset (K1/K2/K3) | cross-asset framing

Run 2:
- Baur and Kuck (2019), Finance Research Letters, "The timing of the flight to gold: An intra-day analysis of gold and the S&P500" (also SSRN 3243111) | intraday flight-to-safety timing | legs: gold (K5), S&P 500 (K1) | intraday gold-equity interaction
- "Effects of idiosyncratic jumps and co-jumps on oil, gold, and copper markets" (Energy Economics 2021, DOI 10.1016/j.eneco.2021.105660; OA copy listed at pure.hud.ac.uk) | one-minute co-jumps and intraday correlations | legs: oil (K4), gold and copper (K5) | intraday cross-commodity co-jumps
- arXiv 2409.08355, "On the macroeconomic fundamentals of long-term volatilities and dynamic correlations in COMEX copper futures" | copper-S&P 500 dynamic correlation (GARCH-MIDAS/DCC-MIDAS) | legs: copper (K5), S&P 500 (K1) | low-frequency, equities against copper
- Quantpedia, "Cross-asset price-based regimes for gold" (URL from the Wayback list, not read) | gold regimes from other assets' prices | legs: gold (K5), other clusters | cross-asset regime signal
- JFM 2025, "Gold Jump Risk, Rare Macroeconomic Disaster Probability, and Expected Stock Returns" (DOI 10.1002/fut.70074) | gold jumps predicting stock returns | legs: gold (K5), equities (K1) | title-level
- Caporale and Plastun (K5-028) is a panel source (gold and oil tested separately, no cross-product signal), so it is claimed here, not flagged.

## 5. Registry ids owned by K5

K5-001 to K5-032 (32 registry lines). K5-003 duplicates K5-006 (kept, not rewritten). Lines
K5-011 to K5-032 were appended in run 2, each before its full-text read. Registry DOI errors (not
rewritten): K5-004 (should be 10.1016/j.irfa.2015.01.017) and K5-005 (should be
10.1016/j.intfin.2018.12.003 per OpenAlex). K5-028 is tagged ["K5", "K4"] and K5-029
["K5", "K4", "K6"] as panel sources. K5-030 is provisionally [K5] only: it was never read, and the
lead may reassign it.
