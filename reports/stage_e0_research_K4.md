# Stage E.0 research log: cluster K4 energy (promoted rerun)

## 0. Header

- Cluster: K4 energy. Products: CL, QM, MCL (WTI crude); NG, QG, MNG (Henry Hub gas); RB (RBOB); HO (ULSD).
- Worker: ClusterReader-K4b-OpusHigh (promoted rerun of the sonnet medium reader). This log supersedes reports/stage_e0_research_K4_sonnet_shallow.md, which is kept for the record. Its title/abstract rejections stand (R-K4-001 to R-K4-006). Its passed items were re-retrieved to the standard below or re-decided.
- Start: 2026-09-23 20:31 PDT. End: 2026-09-23 21:24 PDT.
- Stop reason: every container met the stopping rule (at least 4 logged queries, and the last 2 produced no new passing item). The 60-read cap was not reached. Discovery tools also ran out during the session: Firecrawl credits at about 20:52 PDT; the WebSearch session cap (200/200, shared) at about 21:03 PDT, which refused 3 planned SSRN queries; the OpenAlex free daily IP budget and Crossref (HTTP 429) at about 21:17 PDT. After that, retrieval continued by curl (publisher mirrors, CFTC, EIA, arXiv, IDEAS, Wayback). The lead's weather-model-update seed could not get a dedicated search (see section 1, row +).
- Counts:
  - Items considered: about 305 titles or abstracts. About 125 of these are title-only screens of the CME OpenMarkets and Databento listings.
  - Passed pre-filter: 43 registry items (section 3), plus K4-013 logged as "see D.1 B4".
  - Full text read: 22. That is 17 papers (K4-001, 002, 003, 004, 020, 021, 022, 023 [2-page poster version only], 024, 025, 026, 028, 034, 035, 036, 042, 043) and 5 documentation pages (K4-017, 018, 045, 046, 047).
  - Abstract only: 18 (K4-005, 006, 007, 009, 010 [plus author slides], 012, 014, 027, 029, 030, 031, 032, 033, 037, 038, 040, 041, 044).
  - Blocked (title only): 3 (K4-048, 049, 050).
  - Rejected: 75 lines (about 250 titles; some lines group titles from one listing).
  - K8 flags: 13.
  - [unverified] markers in section 3: 49.
- Retrieval standard used: passages are verbatim from text I fetched myself. That means curl plus pdftotext for PDFs; firecrawl_scrape markdown (before credits ran out); curl plus BeautifulSoup for HTML (IDEAS abstract pages, EIA, Wayback copies of SSRN and CME pages); and the arXiv API. One abstract (K4-041) comes from the OpenAlex API record and is labelled as such. No passage comes from a WebSearch summary. WebFetch was not used for any passage.
- Registry notes: the lines for K4-042 (author placeholder "Lipton?"; correct: Baviera & Santagostino Baldi) and K4-044 (authors given generically; correct: Fishe, Haynes & Onur) carry imperfect author fields. The registry is append-only, so the corrections are made here. K4-039 was claimed before its lede showed it to be off-mechanism (rejected as R-K4-040). K4-048 to K4-050 were claimed as blocked, title-only items to prevent duplicate attempts.

## 1. Container log

| # | container | queries run | start | pre-filter done | full-text done | considered | passed | full-text read | notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Journal of Futures Markets (with the Energy Journal / Energy Economics hits its queries led to) | WebSearch: (1) "Journal of Futures Markets crude oil inventory announcement intraday EIA futures price response"; (2) "... natural gas storage report intraday futures surprise"; (3) "... crack spread intraday heating oil gasoline crude futures". firecrawl_search: (4) site:onlinelibrary.wiley.com JFM crude oil futures intraday announcement; (5) site:onlinelibrary.wiley.com/doi/10.1002/fut natural gas futures storage announcement. OpenAlex title/abstract search filtered to JFM (source S136612413): (6) inventory announcement; (7) crude oil intraday; (8) natural gas intraday; (9) crack spread; (10) energy futures high-frequency; (11) commodity index; (12) settlement; (13) OPEC; (14) heating oil; (15) natural gas storage; (16) roll; (17) gasoline futures; (18) expiration energy; (19) WTI; (20) energy announcements; (21) gasoline; (22) NYMEX energy. OpenAlex unfiltered: (23) analyst accuracy oil; (24) intraday crude oil futures macroeconomic news. Plus citation chasing from K4-002, K4-022, K4-001 reference lists | 20:32 | 21:04 | 21:04 | ~60 | 22 | 10 (+12 abstract only) | Seed Halova/Wolfe, Kurov & Kucher 2014 JFM confirmed (K4-002). Seeds Linn & Zhu 2004 (K4-004) and Gay, Simkins & Turac 2009 (K4-005) confirmed. Queries 21 and 22 produced no new pass (stopping rule met). Wiley full texts are paywalled; open versions were found for 10. |
| 2 | Named author Alexander Kurov (WVU) | (1) IDEAS/RePEc author page pku378 (curl); (2) OpenAlex works list, author A5060535200 (83 works); (3) WebSearch "Gu Kurov 'What drives informed trading before public releases' natural gas pdf"; (4) WebSearch "Alturki Kurov 'Market inefficiencies surrounding energy announcements' pdf"; (5) firecrawl_search Alturki Kurov sequential announcements pdf; (6) firecrawl_search Basistha Kurov monetary policy energy pdf; (7) OpenAlex works list, co-author M. Halova Wolfe; (8) lede check of "Drift Begone!" (Skidmore PDF) | 20:41 | 21:04 | 20:54 | ~10 | 3 new (K4-010, K4-012, K4-025); K4-002/009/029 counted under #1 | 1 (+2 abstract or slides only) | Kurov's energy papers are all JFM; SSRN PDFs are bot-walled. No Kurov multi-asset panel covering K4 was found (the price-drift paper is K2-007). Queries 7 and 8: no new pass. |
| 3 | SSRN (via WebSearch site:papers.ssrn.com; abstracts via Wayback copies of SSRN pages) | (1) crude oil futures intraday return predictability; (2) natural gas futures intraday storage announcement trading strategy; (3) commodity index roll Goldman roll front-running futures prices; (4) crack spread futures intraday mean reversion gasoline heating oil; (5) EIA petroleum status report crude oil futures pre-announcement drift. Planned but refused by the WebSearch session cap (200/200): TAS/settlement window; OPEC intraday; NG weather-forecast updates | 20:56 | 21:03 | 21:03 | ~35 | 9 (3 of them blocked) | 3 (+4 abstract only, 3 blocked) | SSRN PDFs unobtainable (Delivery links redirect to the abstract page; Wayback holds only the challenge page). Queries 4 and 5: no new pass (rule met). |
| 4 | arXiv q-fin (API via curl) | (1) cat:q-fin.* AND ("crude oil" OR WTI) AND (intraday OR high-frequency); (2) ... AND "natural gas" AND (futures OR storage OR weather); (3) ... ("oil futures" OR "energy futures" OR "crude oil futures") AND (announcement OR inventory OR news OR predictab OR momentum); (4) ... ("crack spread" OR "heating oil" OR "gasoline futures" OR "commodity index" OR "Goldman roll"); (5) ... "commodity futures" AND (intraday OR time-of-day OR "opening range"); (6) ... (EIA OR OPEC OR "settlement price" OR "rig count") AND (oil OR gas) | 21:05 | 21:06 | 21:06 | ~26 | 1 (K4-042; K4-020 already held) | 1 | Queries 5 and 6: zero results or no pass. |
| 5 | CFTC Office of the Chief Economist | (1) OCE White Papers page (curl); (2) OCE Research Papers page; (3) OCE Reports page (no PDFs listed); OpenAlex, CFTC institution I1290158734 x (4) crude oil, (5) natural gas, (6) energy futures, (7) index | 21:06 | 21:08 | 21:09 | ~16 | 3 (K4-003 re-verified, K4-043, K4-044) | 2 (+1 abstract only) | K4-035 and K4-036 are CFTC-hosted PDFs found via #3. Queries 5 to 7: no new pass. |
| 6 | EIA WPSR / storage report docs; API report | (1) eia.gov/petroleum/supply/weekly/; (2) its schedule.php; (3) ir.eia.gov/ngs/schedule.html; (4) ir.eia.gov/ngs/ngs.html; (5) api.org WSB page (live URL is a 404); (6) Wayback copy of the API page | 21:09 | 21:10 | 21:10 | 3 | 3 (documentation) | 3 pages | Facts only. The first reader's K4-018 paraphrase was replaced by fetched text. |
| 7 | CME Group research and education (Wayback; cmegroup.com refuses this IP) | Wayback CDX listings: (1) cmegroup.com/openmarkets/energy/*; (2) cmegroup.com/education/articles-and-reports/*; (3) cmegroup.com/trading/energy/files/*; (4) cmegroup.com/education/files/*; then 10 page/PDF fetches | 21:11 | 21:13 | 21:14 | ~67 (mostly titles) | 2 (K4-046, K4-047) | 2 pages | Exchange commentary and marketing dominate. CDX lists 3 and 4: no new pass. |
| 8 | Databento blog | (1) /blog; (2) /blog/learning; (3) /blog/engineering; (4) /blog/learning?page=2 and 3; plus 3 posts opened | 21:14 | 21:15 | n/a | ~60 titles | 0 | 0 | No energy research posts. Confirms the first reader's result. |
| 9 | Quantpedia (energy) | (1) strategy "trading-wti-brent-spread" (curl, 200); (2) blog "pre-holiday-effect-in-commodities" (HTTP 466); (3) site search "crude oil" (466); (4) site search "natural gas" (466); (5) Wayback CDX quantpedia.com/strategies/*; (6) Wayback CDX quantpedia.com/* energy slugs; (7) Wayback "financialization-of-crude-oil-market" | 21:15 | 21:16 | n/a | ~10 | 0 | 0 | Primaries followed. Both first-reader Quantpedia passes (K4-015, K4-016) fail the intraday pre-filter (multi-day holds). |
| 10 | Practitioner blogs (discovery only) | (1) Kinlay search "crude oil" (406); (2) Kinlay search "natural gas" (406); (3) Quantitative Brokers /blog; (4) Robot Wealth search "crude"; (5) Quantocracy search "crude oil"; (6) Carver (qoppac) search "crude"; (7) Wayback CDX jonathankinlay.com/*; (8) Wayback CDX quantitativebrokers.com/blog/*; (9) Kinlay tag pages via Wayback (4 pages); (10) Quantocracy "natural gas"; (11) Quantocracy "EIA"; (12) Robot Wealth "natural gas" | 21:15 | 21:17 | n/a | ~13 | 0 | 0 | No testable K4 mechanism; one K8 flag (CAD-crude). |
| + | Lead's extra seeds | Checked against the above: Linn & Zhu (K4-004); Gay, Simkins & Turac (K4-005); informed trading and drift before EIA (K4-012, K4-022, K4-026, K4-009, K4-032); commodity-index roll (K4-034, K4-035, K4-036, K4-003); intraday/opening-range crude (D.1 B4 = K4-013; K4-021, K4-037, K4-014); weather-model update times and NG: only K4-038 (abstract); a dedicated search failed (OpenAlex daily IP budget exhausted, Crossref HTTP 429, WebSearch cap) | 21:17 | 21:22 | n/a | - | - | - | Weather-model-update seed: UNFINISHED (see return notes). |

## 2. Rejected items

- R-K4-001 | arXiv (first reader, title/abstract decision stands) | "Testing the weak-form efficiency of the WTI crude oil futures market" (arXiv 1211.4686) | generic random-walk test, no tradeable mechanism
- R-K4-002 | arXiv (first reader, stands) | "Convex Modeling of Price Cross-Impact over Time" (arXiv 2609.04712) | generic cross-impact model, not K4-specific
- R-K4-003 | SSRN (first reader, stands) | "Intraday Microstructure Dynamics of E-mini S&P 500 Futures" (Brown) | equity index, K1/D.1 territory
- R-K4-004 | Quantpedia (first reader, stands) | "Crude Oil Predicts Equity Returns" | cross-cluster (crude to equities), flagged K8
- R-K4-005 | ScienceDirect (first reader, stands) | "Evidence of infinite and finite jump processes in commodity futures prices: crude oil and natural gas" | return-process modelling, no mechanism
- R-K4-006 | Investing.com and calendar sites (first reader, stands) | EIA inventory calendar pages | not research; superseded by EIA's own schedule pages
- R-K4-007 | JFM | Singal & Tayal (2019), "Risky short positions and investor sentiment: Evidence from the weekend effect in futures markets" | daily Friday-minus-Monday effect; needs weekend hold; multi-market generic calendar
- R-K4-008 | JFM | Chen, Hartley & Lan (2023), "Temperature, storage, and natural gas futures prices" | daily contemporaneous explanatory regressions, no intraday or predictive horizon
- R-K4-009 | JFM | Adrangi, Chatrath, Christie-David & Lee (2010), "Dominant markets, staggered openings, and price discovery" (crude and gasoline) | depends on staggered pit openings that no longer exist on Globex
- R-K4-010 | JFM | Fink & Fink (2013), "Do Seasonal Tropical Storm Forecasts Affect Crack Spread Prices?" | a few seasonal forecasts a year, price-level effect, no intraday window in the abstract
- R-K4-011 | JFM | Kalev & Duong (2008), "A test of the Samuelson Hypothesis using realized range" | volatility-to-maturity relation across 14 markets, no trading horizon
- R-K4-012 | JFM | Deaves & Krinsky (1992), "The behavior of oil futures returns around OPEC conferences" | 1980s daily returns, no abstract, pit era
- R-K4-013 | JFM | Yang & Zhou (2020), "Return and volatility transmission between China's and international crude oil futures markets" | INE and Oman adjust to WTI; no signal for CL
- R-K4-014 | JFM | Girma & Paulson (1999), "Risk arbitrage opportunities in petroleum futures spreads" | multi-day cointegration crack-spread holds, not intraday
- R-K4-015 | JFM | "Realized volatility and correlation in energy futures markets" (2008, fut.20347) | descriptive distribution of realized volatility and correlation
- R-K4-016 | JFM | Onur & Reiffen (2018), "The effect of settlement rules on the incentive to Bang the Close" | CBOT corn settlement (K6 region), not read
- R-K4-017 | JFM | O'Neill & Whaley (2022), "Effects of nondiscretionary trading on futures prices" | VIX futures ETP rebalancing, not a K4 product (analogue of USO/GSCI roll noted only)
- R-K4-018 | Review of Financial Economics | Kucher & Kurov (2014), "Business cycle, storage, and energy prices" | monthly basis and return cycles
- R-K4-019 | JFM | Boyd & Kurov (2012), "Trader Survival: Evidence from the Energy Futures Markets" (registry K4-011, claimed by the first reader) | trader-survival study, no price mechanism
- R-K4-020 | Financial Review | Kurov et al. (2023), "A shot in the arm: The effect of COVID-19 vaccine news on financial and commodity markets" | one-off 2020 events
- R-K4-021 | AgEcon Search | Kurov et al. (2015), "Forecasting Commodity Price Volatility with Internet Search Activity" | sentiment, shelved (search-attention proxy; daily volatility)
- R-K4-022 | J. Banking & Finance | Gu & Kurov (2020), "Informational role of social media: Evidence from Twitter sentiment" | sentiment, shelved
- R-K4-023 | IJFE | Chebbi & Hmedat (2022), "Inventory information arrival and the crude oil futures market" | contemporaneous release response; abstract states no intraday or predictive horizon
- R-K4-024 | Energy Economics | Wolfe (Halova) & Rosenman (2014), "Bidirectional causality in oil and gas markets" | daily causality, no intraday mechanism
- R-K4-025 | Energy Economics | "Asymmetric impacts of fundamentals on the natural gas futures volatility: An augmented GARCH approach" (2016) | daily GARCH volatility
- R-K4-026 | Cogent Economics & Finance | "Day-of-the-week effect: Petroleum and petroleum products" (2023) | daily day-of-week returns (D.1 family H generic)
- R-K4-027 | Macroeconomic Dynamics | "Are product spreads useful for forecasting oil prices? An empirical evaluation of the Verleger hypothesis" (2017) | one-to-two-year forecasting horizon
- R-K4-028 | J. Derivatives & Hedge Funds (Springer) | "Modelling and trading the gasoline crack spread: A non-linear..." (title as listed by WebSearch) | daily-close crack-spread model
- R-K4-029 | JFM | "Price discovery in China's crude oil futures markets: An emerging Asian benchmark?" (2023, fut.22384) and "Price Discovery in China's Crude Oil Derivatives Market" (2025, fut.22578) | INE price discovery, no CL signal
- R-K4-030 | JFM | "Functional Volatility Relationship Analysis and Prediction in International Crude Oil Futures Markets" (2024) and "Extreme Comovement and Risk Spillovers in Crude Oil Prices" (2025) | volatility and tail-risk modelling, no trading horizon
- R-K4-031 | JFM | "Systemic Risk Transmission to Energy Futures: Weekend Information..." (2026, fut.70128) | weekend information transmission; needs weekend hold
- R-K4-032 | JFM | "Predictability of commodity futures returns with machine learning models" (fut.22471); "Commodity Strategies Based on Momentum, Term Structure, and Idiosyncratic Volatility" (fut.21656); "A trend factor in commodity futures markets" (fut.22291) | monthly cross-sectional commodity factors (D.1 family H, not energy-specific)
- R-K4-033 | naturalgasintel.com | six news items on storage-report reactions | news, not research
- R-K4-034 | Int. J. Forecasting | "Text-based crude oil price forecasting: A deep learning approach" (2018) | sentiment, shelved (news-text sentiment)
- R-K4-035 | Journal of Forecasting / J. Applied Econometrics | Kilian & Hicks (2012), "Did Unexpectedly Strong Economic Growth Cause the Oil Price Shock of 2003–2008?"; "The role of inventories and speculative trading in the global market for crude oil" (2013) | macro structural oil-price models, monthly
- R-K4-036 | J. International Money and Finance | Kurov, Sancetta & Wolfe (2022), "Drift Begone! Release policies and preannouncement informed trading" | UK releases in FX futures (K3 region), lede read only
- R-K4-037 | Quantpedia strategy page (first reader's K4-015) | "Trading WTI/BRENT Spread"; primary: Evans, Dunis & Laws, "Trading Futures Spread: An Application of Correlation and Threshold Filters" (J. Derivatives & Hedge Funds) | daily-rebalanced WTI-Brent spread with a non-CME leg; multi-day holds (the page lists "Period of Rebalancing Daily" and backtest period 1995-2004)
- R-K4-038 | Quantpedia blog (first reader's K4-016) | "Pre-Holiday Effect in Commodities" (2024) | multi-day hold D-5 to D-1 on USO/UGA ETFs; not intraday. The page returned HTTP 466 to curl this session, so the first reader's passages were not re-verified
- R-K4-039 | Quantitative Finance (first reader's K4-019) | Cummins & Bucca (2012), "Quantitative spread trading on crude oil and refined products markets" | multi-day spreads: IDEAS abstract (curl) states "trade lengths of 9--55 days"
- R-K4-040 | FEDS 2011-57 / J. Financial Markets 2014 (registry K4-039, claimed before the lede was read) | Brunetti & Reiffen, "Commodity Index Trading and Hedging Costs" | CIT positions and hedging costs in wheat, corn, soybeans on non-public CFTC data; not a roll-timing or intraday mechanism ([K6] topic)
- R-K4-041 | SSRN | Li & Liu, "Functional Classification and Dynamic Prediction of Cumulative Intraday Returns of Crude Oil Futures in China" | INE (Shanghai) intraday paths; not CL
- R-K4-042 | SSRN | Chevallier & Sévi, "A Fear Index to Predict Oil Futures Returns" | rejected on title (implied-volatility index as a return predictor, no intraday horizon indicated); not retrieved
- R-K4-043 | SSRN | Bredin, O'Sullivan & Spencer, "Information in the Term Structure of WTI Crude Oil Futures" | term-structure forecasting, daily or lower frequency
- R-K4-044 | SSRN | Kolpakov, "Economic Fundamentals of Gasoline Crack Spreads in the U.S."; Choi, Leatham & Sukcharoen, "Oil Price Forecasting Using Crack Spread Futures and Oil ETFs"; Ahn, "Cracker Barrel"; Mahringer & Prokopczuk, crack-spread option valuation | seasonal, forecasting, macro-identification and option-pricing studies, no intraday mechanism
- R-K4-045 | SSRN | Conlon, Corbet & Muñiz, "Fear Gauges and Oil Futures: Weekday Patterns in Volatility Spillovers" | daily TVP-VAR volatility spillovers
- R-K4-046 | SSRN | Frankfurter & Accomazzo, "Term Structure and Roll Yield"; Gorton & Rouwenhorst, "Facts and Fantasies About Commodity Futures"; Dürr & Voegeli; Horváth et al.; Bhardwaj et al., "The First Commodity Futures Index of 1933" | monthly roll-yield, risk-premium and forward-curve studies
- R-K4-047 | SSRN | Bu, "Effects of Inventory Announcement on Crude Oil Price Volatility" (abstract via Wayback: "negatively affect crude oil returns on the day the EIA releases", GARCH(1,1) daily) | daily
- R-K4-048 | SSRN | Derbali, "OPEC News and Predictability of Energy Futures Returns and Volatility"; Hasanpour et al., "OPEC Announcements and Their Effects on Oil Price..."; Gkillas et al., "International Announcements and WTI Crude Oil Futures: ... 2008" | daily OPEC or announcement event studies (abstracts via Wayback for the first two)
- R-K4-049 | SSRN | Cocoma, "Disagreement and Scheduled Announcements: Explaining the Pre-Announcement Drift"; Garratt, Petrella & Zhang, "How far ahead can the EIA forecast oil market developments?"; Yue, Li & Wu, "Weekday Variations in the Chinese Crude Oil Futures Market" | generic theory, monthly STEO forecasting, INE market
- R-K4-050 | Energy Economics 115 (2022) (Glasgow eprints, first page read) | Ewald, Haugom, Lien, Størdal & Wu, "Trading time seasonality in commodity futures: An opportunity for arbitrage in the natural gas and crude oil markets?" | seasonality by calendar trading time (months), not intraday
- R-K4-051 | SSRN | Song, López de Prado, Simon & Wu, "Exploring Irregular Time Series Through Non-Uniform Fast Fourier Transform" | method paper
- R-K4-052 | NBER (via WebSearch results) | "Limits to Arbitrage and Hedging: Evidence from Commodity Markets"; "Index Investment and Financialization of Commodities" | monthly hedging-pressure and cross-commodity correlation studies
- R-K4-053 | arXiv | 2310.18903 (visibility graph, crude futures), 2011.00552 (mixed-frequency VaR), 1403.0064 (leverage effect in energy futures), 1405.2445 (good/bad volatility spillover in petroleum), 1201.4776 (energy wavelet co-movement), 1610.05697 (chaos in energy futures), 1309.1492 (commodity futures efficiency), 2204.05199 (INE multifractal COVID), 2501.15596 (multi-factor oil pricing), 0806.1170 (oil bubble), 1804.10869 (PGM oil forecasting) | modelling or descriptive, no intraday trading mechanism
- R-K4-054 | arXiv | 1312.3789, 2406.16400, 1803.11309, 2102.01980, 2001.08906, 2605.06570 (gas storage and swing valuation); 2010.06227 (European gas forecasting); 2301.08359, 2309.00630, 2308.01910 (deep RL commodity trading); 1307.7244 (signature methods) | valuation or ML methodology, non-CME gas, or daily RL
- R-K4-055 | arXiv | 2603.11408, "Beyond Polarity: Multi-Dimensional LLM Sentiment Signals for WTI Crude Oil Futures Return Prediction" | sentiment, shelved
- R-K4-056 | CFTC OCE white papers | "Liquidity in Select Futures Markets" (Fett & Haynes 2017; ES, ZN, CL 2013-2016; lede read) | descriptive liquidity trends, no mechanism (useful only for cost context)
- R-K4-057 | CFTC OCE white papers | "Macro News Announcements and Automated Trading" (Haynes & Roberts 2015; lede read) | ES and ZN only (K1/K2 region)
- R-K4-058 | CFTC OCE | "The Effect of Pit Closure on Futures Trading"; "Automated Trading in Futures Markets" (and update); "The Futures Trading Landscape"; "Exploring Commodity Trading Activity: An Integrated Analysis of Swaps and Futures" | descriptive market-structure reports
- R-K4-059 | CFTC OCE research papers page | "Determinants of Commodity Market Liquidity"; "Retail Traders in Futures Markets"; other swaps/FX/Treasury papers listed | liquidity determinants or descriptive; non-K4 topics
- R-K4-060 | Energy Journal (CFTC authors) | Brunetti, Büyükşahin, Robe & Soneson (2013), "OPEC 'Fair Price' Pronouncements and the Market Price of Crude Oil" | daily; the abstract (Wayback SSRN) reports "little influence on the market price of crude oil"
- R-K4-061 | Resources Policy / SSRN (CFTC authors) | "Arbitrage breakdown in WTI crude oil futures: An analysis of the events on April 20, 2020" | single one-off event
- R-K4-062 | JFM (CFTC authors) | "Reversing the lead, or a series of unfortunate events? NYMEX, ICE, and Amaranth" (2009); "Hedge Funds, Volatility, and Liquidity Provision in Energy Futures Markets" (J. Alternative Investments 2007) | historic 2006 episode; descriptive
- R-K4-063 | AEPP (CFTC authors) | "Spreads and Non-Convergence in Chicago Board of Trade Corn, Soybean, and Wheat Futures: Are Index Funds to Blame?" | delivery convergence in grains ([K6] region), not roll timing
- R-K4-064 | CME OpenMarkets (Wayback) | "The Events to Watch in Crude Oil" (2023) | commentary. Quality note: it states the EIA report is "typically ... published on Wednesdays at 10:30 a.m. Central Time", which contradicts EIA's own schedule (10:30 a.m. ET, K4-017)
- R-K4-065 | CME OpenMarkets (Wayback) | "Why Crude Oil Traders are Focusing on the Short-Term" (2023) | exchange marketing for weekly options (descriptive statistics only)
- R-K4-066 | CME OpenMarkets (Wayback) | "What do Diesel and Gasoline Tell us About Oil Prices?" (2024); "Where Oil Prices Meet Central Bank Policy" (2023) | macro commentary
- R-K4-067 | CME OpenMarkets (Wayback CDX list) | 55 further energy-section article titles 2022-2026 (exports, LNG, carbon, ethanol, SPR, outlooks; full list in the CDX output, not reproduced) | market commentary, pre-filtered on title
- R-K4-068 | CME education (Wayback) | "FAQ: Daily Settlement Price Determination Time Change" (equity-index settlement); "FAQ: CME Crude Auction" (physical cargo auction); "Are Crude Oil & Natural Gas Prices Linked?" (commentary on the long-run ratio) | not a K4 intraday mechanism
- R-K4-069 | CME education files (Wayback) | Dow Jones-UBS "Commodity Index Pre-Roll Analysis" (index weights and roll-yield table); "Crack Spread Handbook"; "Deconstructing futures returns: the role of roll yield" | documentation or education, no mechanism beyond K4-034/035/036
- R-K4-070 | Databento blog | about 60 post titles (engineering, data, tutorials; opened: "Build a Pairs Trading Strategy in Python", "What are futures spreads?", "Self-match prevention") | no energy-specific research
- R-K4-071 | Quantpedia (CDX list) | "Momentum Effect in Commodities", "Term Structure Effect in Commodities", "Skewness Effect in Commodities", "Return Asymmetry Effect in Commodity Futures" | monthly cross-sectional commodity factors (D.1 family H)
- R-K4-072 | Quantpedia strategy page, related papers | Lubnau, "Spread trading strategies in the crude oil futures market"; Donninger, "The Poverty of Academic Finance Research..." (critique: the page quotes "He used the wrong data"); Fanelli, Fontana & Rotondi, "A Hidden Markov Model for Statistical Arbitrage in International Crude Oil Futures Markets" | daily WTI-Brent(-INE) spread strategies with non-CME legs
- R-K4-073 | Quantitative Brokers blog | roll tools ("The Roll algorithm", roll timing forecasts, roll tracker) and "Basics of US Treasury Futures Roll Microstructure" | vendor tooling; Treasury roll is K2's (registry K2-005)
- R-K4-074 | Robot Wealth / Quantocracy / Carver | "Commodity Carry"; Harbourfronts, "Option Pricing Models and Strategies for Crude Oil Markets"; Harbourfronts, "Cross-Sectional Momentum: Results from Commodities and Equities"; Factor Research, "Commodities vs Commodity ETFs"; Quant at Risk, Brent 1-minute data tutorial; Carver, "Systems building - futures rolling"; Jay Kaeppel, "Will Natural Gas Break Wind in June?" | monthly carry or seasonal, options pricing, tutorials
- R-K4-075 | Jonathan Kinlay (Wayback tag pages) | "Developing High Performing Trading Strategies with Genetic Programming"; "Futures WealthBuilder"; "Systematic Futures Trading" | vendor marketing and data-mined GP strategies with no disclosed mechanism

## 3. Passed items

Ordered by registry id. For each item, the retrieval line names the URL actually read and the routes that failed. Status of the first reader's other registry lines: K4-008 is flagged for K8 (section 4, not read); K4-011 is rejected (R-K4-019); K4-015, K4-016 and K4-019 are rejected at pre-filter (R-K4-037, R-K4-038, R-K4-039); K4-013 is "see D.1 B4" (block below).

### K4-001
- Citation: Prokopczuk, M., Wese Simen, C., Wichmann, R. (2021). "The Natural Gas Announcement Day Puzzle." The Energy Journal 42(2). DOI 10.5547/01956574.42.2.mpro.
- Retrieval: full text, accepted manuscript (dated 25 Nov 2019) with online appendix, University of Reading CentAUR. URL read: https://centaur.reading.ac.uk/90003/1/NG_paper_final_round.pdf (curl, pdftotext).
- Mechanism: NG futures earn a large negative average return on EIA storage-report days; 99% of it falls in the window from 90 minutes before to 30 minutes after the 10:30 ET release, split about evenly between pre-release and post-release. The pre-release part appears only on days when storage exceeds the analyst consensus. A short from -90 to +30 minutes earned money before 2011 and nothing after.
- Products and horizon: NG (Henry Hub, NYMEX) nearby; 09:00-11:00 ET (08:00-10:00 CT) on report days.
- Cost assumptions: sells at the last bid and buys back at the last ask; also subtracts funding at overnight LIBOR on a fully funded position.
- Data window: daily Bloomberg data March 2003 to December 2018 (3,982 days, 699 report days); 5-minute Thomson Reuters Tick History data for the intraday decomposition.
- Quality tells: (1) Sharpe ratios for a once-a-week trade are annualized with sqrt(252), not sqrt(52) (footnote 24 and the Table 8 caption), which inflates them by about 2.2x. (2) The whole-sample result comes from before 2011; after 2011 the strategy is flat to negative after costs (Table 8, Panel C). The authors report this decay themselves. (3) The 2011 split is not motivated in the text and differs from the 2007/2014 subsample boundaries used in Section IV.
- Verified passages:
  - P-K4-001-a (Abstract): "More than 50% of the annual return is earned on these days. ... At the intraday level, the return splits half into a pre- and post-announcement part. The pre-announcement return is entirely generated on days when storage levels exceed analysts' expectations casting doubt on explanations based on informed trading."
  - P-K4-001-b (Sec. IV.A): "Panel A of Table 5 shows that the entire effect (99%) stems from the two hour window surrounding the announcement."
  - P-K4-001-c (Online Appendix, Table 5, Panel B): "(−90, 30) ... (−90, −5) ... (−5, 30) / Average Return -0.37 -0.18 -0.19 / p-value (0.000) (0.000) (0.010)".
  - P-K4-001-d (Sec. V.C): "the simple strategy of opening a short position 90 minutes before the announcement and closing it 30 minutes afterwards yields a significant annual return of 12% (t-stat = 2.93) translating into a Sharpe ratio of 1.76 after transaction and funding costs."
  - P-K4-001-e (Table 8, Panels B and C): "Panel B: Before 2011 ... Raw + TC + FC 25.02 (0.000) 3.26 ... Panel C: After 2011 ... Raw (-90,30) 2.91 (0.558) 0.50 / Raw + TC -0.90 (0.854) -0.16 / Raw + TC + FC -0.97 (0.843) -0.17".
  - P-K4-001-f (footnote 24): "while returns are annualized using a multiplier of 52 to represent the realisable return within a year, the corresponding Sharpe ratio is annualized with a multiplier of 252, since means and standard deviation are based on daily returns."
  - P-K4-001-g (Sec. IV.A): "On EIA annuoncement days there is a clear spike in volume and volatility at exactly 10:30 AM with volumes sixfold and volatility fivefold compared to non-announcement days."
- Numeric claims: -0.37% mean (-90,+30) return, split -0.18/-0.19 (P-K4-001-c); 12.01% a year with Sharpe 1.76 after costs over the whole sample (P-K4-001-d, Sharpe inflated per P-K4-001-f); 25.02% before 2011, -0.97% (p=0.843) after 2011 (P-K4-001-e); 6x volume and 5x volatility at 10:30 (P-K4-001-g).
- Tags: port of D.1 family E (scheduled event, pre-release window), NG-specific. Intraday-feasible: yes. One trade a week at 08:00-10:00 CT, market orders, flat by 10:00 CT. The after-2011 null is the binding evidence.
- Clusters tagged: K4 only.

### K4-002
- Citation: Halova (Wolfe), M. W., Kurov, A., Kucher, O. (2014). "Noisy Inventory Announcements and Energy Prices." Journal of Futures Markets 34(10), 911-933. DOI 10.1002/fut.21633.
- Retrieval: full text, author working-paper version dated June 2013 marked "Forthcoming, Journal of Futures Markets" (same source). URL read: https://www.skidmore.edu/economics/documents/NoisyInventoryAnnouncementsAndEnergyPrices.pdf (curl, pdftotext).
- Mechanism: WPSR and gas storage report surprises move CL, RB, HO and NG in a 15-minute window; OLS response coefficients are biased toward zero by noise in the Bloomberg consensus surprise, and ITC estimates are 2x (petroleum) to 4x (gas) larger. The gas storage report also moves crude, gasoline and heating oil (cross-product response inside K4).
- Products and horizon: nearby CL, RB (gasoline), HO, NG futures (roll to next contract in last 3 trading days); 10:25-10:40 ET event window.
- Cost assumptions: none (price-impact measurement, no strategy).
- Data window: 16 Jul 2003 to 27 Jun 2012; 435 usable announcements per report (simultaneous Thursday releases excluded). Futures data from Genesis Financial Technologies; expectations from Bloomberg consensus.
- Quality tells: peer-reviewed; no trading claim. Explanatory power of the OLS surprise regression is low (NG R2 0.244), which the paper attributes to survey noise; the ITC "pseudo-R2" is a model quantity, not out-of-sample fit.
- Verified passages:
  - P-K4-002-a (Abstract, p.1): "The ITC coefficient estimates are about twice as large as OLS estimates for petroleum commodities and about four times as large as OLS estimates for natural gas. These results imply that energy prices are more strongly influenced by unexpected changes in inventory than shown in previous research."
  - P-K4-002-b (Sec. 3.4, p.13): "The event window is from five minutes before to ten minutes after the announcement time."
  - P-K4-002-c (Sec. 3.2, p.11): "Our sample period extends from July 16, 2003 through June 27, 2012. This period contains 468 releases of the Petroleum Status Report and 467 releases of the Natural Gas Storage Report."
  - P-K4-002-d (Sec. 4, p.15): "The OLS estimate of the response coefficient for natural gas futures is about –2.4, implying that an unexpected 1% increase in natural gas in storage results in a 2.4% drop in natural gas futures prices."
  - P-K4-002-e (Table III, Panel A, full sample N=435, OLS response coefficients to the gas storage report): "Crude Oil -0.14 (0.08)* ... Gasoline -0.13 (0.07)** ... Heating Oil -0.15 (0.07)**".
- Numeric claims: ITC/OLS ratio ~2 petroleum, ~4 gas (P-K4-002-a); NG OLS coefficient -2.4 per 1% storage surprise (P-K4-002-d); gas-report spillover to CL/RB/HO significant at 10%/5% (P-K4-002-e).
- Tags: port of D.1 family E (scheduled event), energy-specific release. Intraday-feasible: yes (15-minute window at 09:25-09:40 CT), but the paper documents a contemporaneous response, not a predictable return; a rule would need the surprise faster than the price, which market orders on TopstepX cannot achieve. The usable content is the size and noise of the response.
- Clusters tagged: K4 only.

### K4-003
- Citation: Bessembinder, H., Carrion, A., Tuttle, L., Venkataraman, K. (2014 draft). "Predatory or Sunshine Trading? Evidence from Crude Oil ETF Rolls." CFTC Office of the Chief Economist working paper, March 2014 draft. (The published version, Journal of Financial Economics 2016, is [unverified] and was not retrieved.)
- Retrieval: full text, CFTC-hosted draft. URL read: https://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_predatorysunshine0314.pdf (curl, pdftotext). The first reader's passages were re-verified against this text.
- Mechanism: around USO's large, pre-announced monthly roll trades in CL, spreads narrow, depth rises and more accounts supply liquidity (sunshine trading, not predation). Temporary price impact of order imbalances in the expiring contract reverses almost entirely within 10 minutes (95% within 15 minutes for the second contract). USO still pays about 25 bp per roll in adverse settlement-price moves. ETFs roll largely via TAS at the 14:28-14:30 ET settlement.
- Products and horizon: CL nearby and second contract on USO roll dates; order-book and account data; minutes (resiliency) and settlement-to-settlement (roll cost).
- Cost assumptions: this is the roll cost borne by USO ("round-trip trading costs that average 25 basis points"), not a strategy cost.
- Data window: account-level data 1 Mar 2008 to 28 Feb 2009 (12 rolls); daily settlements Jan 1990 to Dec 2013.
- Quality tells: CFTC contractor study using non-public account data, presented at WFA 2013. The account-level evidence covers only 12 rolls in 2008-09, a crisis year with USO assets rising from $0.47 bn to $3.92 bn.
- Verified passages:
  - P-K4-003-a (Abstract): "We find narrower bid-ask spreads, greater order book depth, and more trading accounts providing liquidity on roll dates. We estimate that the largest ETF tracking crude oil prices effectively pays round-trip trading costs that average 25 basis points."
  - P-K4-003-b (Introduction): "The resulting estimates imply that over 99% of the temporary price impact due to an order imbalance in the expiring contract is reversed within ten minutes. For the second nearest-to-expiration contract, over 95% of the temporary price impact is reversed within 15 minutes".
  - P-K4-003-c (Introduction): "our analysis of daily settlement prices indicates that USO does pay to execute its roll trades – about 25 basis points on average per roll, or 3% per year, in the form of adverse changes in settlement prices at the time of the rolls."
  - P-K4-003-d (Sec. 3): "USO's roll volume on average exceeds market volume during the settlement period, indicating that it would be difficult for USO to execute its entire roll by use of regular trades during the settlement interval. Many Crude oil ETFs employ TAS contracts to ensure a price that closely matches the benchmark settlement price."
  - P-K4-003-e (Sec. 3): "Our study of individual orders and trades spans the period March 1, 2008 to February 28, 2009, and therefore includes twelve monthly rolls. We also study daily crude oil settlement price data for the longer time interval January 1990 through December 2013."
- Numeric claims: 25 bp per roll, about 3% a year (P-K4-003-a, c); impact reversal 99% in 10 min, 95% in 15 min (P-K4-003-b).
- Tags: new to the program (ETF/index roll flow in CL; settlement-window TAS). Intraday-feasible: partly. The adverse settlement move on roll days is a settlement-window effect (13:28-13:30 CT, inside the XFA day). A same-day position on the nearby-versus-deferred spread or the nearby leg on published USO roll dates is conceivable, but the paper tests liquidity, not such a rule. The minutes-scale resiliency argues against fading order imbalances.
- Clusters tagged: K4 only.

### K4-004
- Citation: Linn, S. C., Zhu, Z. (2004). "Natural Gas Prices and the Gas Storage Report: Public News and Volatility in Energy Futures Markets." Journal of Futures Markets 24(3), 283-313. DOI 10.1002/fut.10115.
- Retrieval: full text, published version (Wiley typeset PDF) hosted by the University of Oklahoma Price College. URL read: https://www.ou.edu/content/dam/price/Management/Energy%20Institute/docs/Linn%20and%20Zhu%20JFM%202004.pdf (curl, pdftotext).
- Mechanism: the weekly gas storage report sharply raises 5-minute NG volatility at the release interval, and volatility stays elevated for up to 30 minutes. Separately, volatility is high at the open and at the close of the (pit) session. The study measures volatility only and makes no directional claim.
- Products and horizon: NYMEX NG nearby, 5-minute intervals, pit-session hours (10:00 to 14:30 or 15:10 ET depending on subperiod).
- Cost assumptions: none.
- Data window: 1 Jan 1999 to 31 Oct 2002, tick data. The report moved from AGA (Wednesday after the close, then about 14:00 ET) to EIA (Thursday 10:30 ET) in May 2002, so the EIA-era subsample is about 6 months.
- Quality tells: open-outcry era, before Globex side-by-side trading; the open and close effects are tied to pit hours that no longer bound the session. The EIA-era evidence covers only about 6 months.
- Verified passages:
  - P-K4-004-a (Abstract, pp.283-284): "We find that the weekly gas storage report announcement was responsible for considerable volatility at the time of its release and that volatility up to 30 minutes following the announcement was also higher than normal. Aside from these results, we document pronounced price volatility in this market both at the beginning of the day and at the end of the day".
  - P-K4-004-b (Introduction, p.284): "The study spans the period January 1, 1999 through October 31, 2002."
  - P-K4-004-c (Weekday and Thursday Effects section): "the 2:00–2:05 PM Wednesday standard deviation for the second two calendar periods is on the order of six times the standard deviations for the same time periods on the other days of the week during those periods."
  - P-K4-004-d (same section): "volatility during this time interval is larger than normal only on Thursday during the last calendar subperiod, the period during which the EIA has been handling the report."
- Numeric claims: release-interval volatility about 6x the same interval on other weekdays in the AGA era (P-K4-004-c).
- Tags: port of D.1 family D (volatility state) and family E (scheduled event), NG-specific. Intraday-feasible: yes as a timing input (when volatility arrives), no as a directional signal; the source has no return result. Historical interest only for session-open and close effects, which are pit-era.
- Clusters tagged: K4 only.

### K4-005
- Citation: Gay, G. D., Simkins, B. J., Turac, M. (2009). "Analyst forecasts and price discovery in futures markets: The case of natural gas storage." Journal of Futures Markets 29(5), 451-477. DOI 10.1002/fut.20368. SSRN 972381 (2007 WP, same source).
- Retrieval: abstract only, read from IDEAS via curl: https://ideas.repec.org/a/wly/jfutmk/v29y2009i5p451-477.html. Failed routes: SSRN Delivery PDF (bot wall; WebSearch listed the link SSRN_ID1031184; Wayback has no copy), Wiley (paywall), Semantic Scholar/Unpaywall (no OA copy).
- Mechanism: the NG market forms its expectation of the weekly storage number from individual analyst forecasts weighted by each analyst's past (especially long-term) accuracy, not from the published consensus.
- Products and horizon: NG futures around the weekly storage release. The intraday window is [unverified]; K4-002 (P-K4-002-b) states this paper "also use[s] 15-minute intervals containing the announcement".
- Cost assumptions: [unverified]. Data window: [unverified].
- Quality tells: cannot assess beyond the abstract.
- Verified passages:
  - P-K4-005-a (Abstract, IDEAS): "we show that the market appears to condition expectations regarding a weekly storage release on the analyst forecasts and beyond that of various statistical‐based models. Further, we find that the market looks through the reported consensus analyst forecast and places differential emphasis on the individual forecasts of analysts according to their prior accuracy. Also, the market appears to place greater emphasis on analysts' long‐term accuracy than on their recent accuracy."
- Numeric claims: none in the abstract. Halova et al. (K4-002, Introduction) report that this paper finds "a 1% unexpected increase in natural gas inventory results in an approximately 1% drop in the natural gas futures price". That is a secondary citation, [unverified] against this source.
- Tags: new to the program (accuracy-weighted analyst expectation as the market's expectation). It is the design basis for the K4-012 predictor. Intraday-feasible: yes as an input to a pre-release rule; not a rule by itself.
- Clusters tagged: K4 only.

### K4-006
- Citation: Ederington, L. H., Lin, F., Linn, S. C., Yang, L. Z. (2019). "EIA Storage Announcements, Analyst Storage Forecasts, and Energy Prices." The Energy Journal 40(5), 121-142. DOI 10.5547/01956574.40.5.lede.
- Retrieval: abstract only, via IDEAS (curl): https://ideas.repec.org/a/sae/enejou/v40y2019i5p121-142.html. Failed routes: Sage/IAEE (paywall), co-author Lisa Yang's site (lists the paper, no file), Semantic Scholar/Unpaywall (no OA). A Montana State "research brief" page turned up in WebSearch but is secondary and was not read.
- Mechanism: analyst storage forecasts carry information beyond seasonality and past flows, and prices incorporate them before the EIA release. NG price reactions to the release depend on analyst disagreement. Storage surprises partly reverse the following week, and dispersion rises after large errors.
- Products and horizon: CL and NG around EIA releases; the exact window is [unverified].
- Cost assumptions / data window: [unverified].
- Quality tells: cannot assess.
- Verified passages:
  - P-K4-006-a (Abstract, IDEAS): "we find that analyst storage forecasts bring additional information to the market beyond seasonal patterns and past storage flows and that the market promptly incorporates analyst forecasts into oil and gas prices prior to the EIA announcements. ... We further find that the price reaction to subsequent EIA natural gas storage announcements is contingent on the level of analyst forecast uncertainty as proxied by analyst forecast disagreement. Storage flows higher or lower than analysts had expected one week tend to be partially reversed the following week".
- Numeric claims: none.
- Tags: new to the program (pre-release incorporation of the forecast; disagreement-conditioned reaction; week-to-week surprise reversal as a predictor of the next surprise). Intraday-feasible: as a conditioning variable for release-day rules, yes; the paper's own horizon is [unverified].
- Clusters tagged: K4 only.

### K4-007
- Citation: Miao, H., Yang, J. (2026). "Intraday Liquidity in International Crude Oil Futures Markets: News Impacts, Commonality, and Spillovers." Journal of Futures Markets 46(7), 1234-1255 (pages from OpenAlex). DOI 10.1002/fut.70106.
- Retrieval: abstract only, via IDEAS (curl): https://ideas.repec.org/a/wly/jfutmk/v46y2026i7p1234-1255.html. Failed routes: Wiley (paywall), no working paper found (WebSearch, OpenAlex, Semantic Scholar). The first reader's note that the abstract was "not retrievable" is superseded.
- Mechanism: EIA releases move intraday returns (and, less, liquidity) in WTI, Brent and INE. Intraday liquidity co-moves across the three, and WTI is the main source of liquidity spillovers, though not of return spillovers.
- Products and horizon: CL (WTI), ICE Brent, INE crude; tick data, intraday.
- Cost assumptions / data window: [unverified].
- Verified passages:
  - P-K4-007-a (Abstract, IDEAS): "US EIA inventory announcements significantly affect intraday returns and, to a lesser extent, liquidity across all three markets. We document strong commonality in intraday liquidity, largely driven by supply‐side factors, and find that WTI is the dominant source of liquidity spillovers, a pattern not mirrored in return spillovers."
- Numeric claims: none.
- Tags: port of D.1 family E / D (event-time liquidity state). Intraday-feasible: as a liquidity-timing input, yes; there is no directional claim.
- Clusters tagged: K4 only (Brent and INE are non-CME signal instruments for CL, so K4 per partition section 1).

### K4-009
- Citation: Alturki, S., Kurov, A. (2022). "Market inefficiencies surrounding energy announcements." Journal of Futures Markets 42(1), 172-188. DOI 10.1002/fut.22264. SSRN 3747330 (same source).
- Retrieval: abstract only. Read by firecrawl_scrape of the SSRN abstract page (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3747330) and by curl of IDEAS (https://ideas.repec.org/a/wly/jfutmk/v42y2022i1p172-188.html); the two match. Failed routes: SSRN Delivery (redirects to the abstract page for automated clients, tested on K4-012), Wiley full text (redirects to the ePDF reader, no access), Semantic Scholar/Unpaywall (no OA), no author-hosted copy found.
- Mechanism: the API report (Tuesday evening) is informative about the EIA report (Wednesday), yet CL does not fully absorb it. A predictor built from sequential information forecasts the EIA surprise and the pre-EIA return, in-sample and out-of-sample.
- Products and horizon: CL (and stocks, see K8 flag); the window between the API and EIA releases.
- Cost assumptions / data window: [unverified]. The abstract says the inefficiency "can be exploited by sophisticated traders"; the magnitude is [unverified].
- Verified passages:
  - P-K4-009-a (Abstract, SSRN and IDEAS): "Our findings provide clear evidence of inefficiency in crude oil futures and stock markets. This inefficiency can be exploited by sophisticated traders. ... We also construct a predictor that can predict inventory surprises and pre-announcement returns in-sample and out-of-sample. Finally, we develop a combination forecast that can be used as a proxy for market expectations of oil inventory announcements."
- Numeric claims: none verifiable; any return or Sharpe figure is [unverified].
- Tags: new to the program (API-to-EIA sequential information predicting the CL pre-EIA return). Intraday-feasible: likely. The API is read Tuesday after the flat time, and the trade is placed Wednesday before 09:30 CT, flat after the release. The paper's exact entry and exit windows are [unverified].
- Clusters tagged: K4 (the stock-market leg is flagged for K8, section 4).

### K4-010
- Citation: Basistha, A., Kurov, A. (2015). "The Impact of Monetary Policy Surprises on Energy Prices." Journal of Futures Markets 35(1), 87-103. DOI 10.1002/fut.21639. SSRN 2284431 (same source).
- Retrieval: abstract plus the authors' seminar slides (George Washington University, 18 Apr 2013), not the paper. URLs read: SSRN abstract via firecrawl_scrape (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2284431); slides via curl (https://www2.gwu.edu/~forcpgm/Basistha_slides.pdf, pdftotext). Routes that failed for the paper: Wiley PDF (403), SSRN Delivery (redirects to the abstract page for bots, tried on the sister paper K4-012), no repository copy found. The slide estimates may differ from the published tables; they are labelled "slides".
- Mechanism: CL and gasoline fall immediately after surprise fed-funds target increases (30-minute window). The response does not persist over several days, and the monthly VAR finds no effect. Per the slides, the intraday effect is significant for unscheduled (inter-meeting) moves and not for scheduled meetings.
- Products and horizon: CL and gasoline (RB predecessor) futures; 30-minute window for scheduled meetings, 3 hours for unscheduled.
- Cost assumptions: none.
- Data window (slides): Jan 1994 to Dec 2008, 129 events.
- Quality tells: the authors report their own non-persistence and VAR null, which is a positive tell. The headline intraday significance leans on unscheduled meetings, which are rare and unpredictable.
- Verified passages:
  - P-K4-010-a (SSRN abstract): "We find a significant response of energy prices to surprise changes in the federal funds target rate in an intra-day window, immediately following the monetary announcement. However, the accumulated responses of energy prices to monetary shocks over a period of several days after the announcement are statistically insignificant."
  - P-K4-010-b (slides, "Data and models"): "Sample: January 1994 to December 2008, 129 events. Event window: 30 minutes for scheduled meetings and three hours for unscheduled meetings."
  - P-K4-010-c (slides, "Intraday scheduled/unscheduled meetings"): "Target*Scheduled Target*Unscheduled R2 / Crude Oil -0.88 (0.8) -5.61 (0.9)* 0.3 / Gasoline -0.93 (0.9) -5.40 (0.6)* 0.3".
- Numeric claims: scheduled-meeting CL coefficient -0.88 (s.e. 0.8, insignificant); unscheduled -5.61 (significant) (P-K4-010-c, slides only; published-table values [unverified]).
- Tags: port of D.1 family E (FOMC), energy product. Intraday-feasible: a scheduled-FOMC reaction trade is feasible in timing (13:00-13:15 CT), but the scheduled-meeting evidence here is null. Unscheduled moves cannot be pre-planned.
- Clusters tagged: K4 only.

### K4-012
- Citation: Gu, C., Kurov, A. (2018). "What drives informed trading before public releases? Evidence from natural gas inventory announcements." Journal of Futures Markets 38(9), 1079-1096. DOI 10.1002/fut.21926. SSRN 2826684 (43-page WP, revised 29 Mar 2018; same source).
- Retrieval: abstract only. Read by firecrawl_scrape of the SSRN page and by curl of IDEAS (https://ideas.repec.org/a/wly/jfutmk/v38y2018i9p1079-1096.html); they match. Failed routes: SSRN Delivery PDF via firecrawl, both plain and stealth-proxy attempts (each returned the abstract page), and via curl (403); Wayback (no snapshot); Wiley (paywall); Unpaywall (not OA); ResearchGate (not attempted; login-gated).
- Mechanism: NG shows informed trading before the Thursday storage release. The gap between the median forecast of historically accurate analysts and the consensus predicts the storage surprise and part of the pre-release drift. The authors attribute this to superior forecasting rather than leakage.
- Products and horizon: NG futures; the pre-release window before 10:30 ET Thursday. The exact window is [unverified].
- Cost assumptions: [unverified]. Data window: [unverified].
- Verified passages:
  - P-K4-012-a (Abstract): "The results show that the difference between the median forecast of analysts with high historical forecasting accuracy and the consensus forecast can be used to predict inventory surprises. This predictor explains some of the pre-announcement price drift, suggesting that informed trading before the announcement is likely to be driven by superior forecasting rather than by information leakage. A simple trading strategy conditioned on the predictor would have generated an annualized Sharpe ratio of 1.26."
- Numeric claims: Sharpe 1.26 (P-K4-012-a, abstract). The cost treatment, annualization method (compare K4-001's sqrt(252) on weekly trades) and sample are [unverified].
- Tags: new to the program (accuracy-weighted analyst dispersion as a surprise predictor). Intraday-feasible: likely (a pre-release NG position on Thursday morning, flat after 09:30 CT), pending the full text. It needs the analyst-level forecast data (Bloomberg).
- Clusters tagged: K4 only.

### K4-013 (not re-read: see D.1 B4)
- Holmberg, Lönnbark & Lundström (2013), "Assessing the profitability of intraday opening range breakout strategies" (Finance Research Letters; Umeå WP 845), WTI crude oil futures. It appears in Stage D.1's log as row B4 (full text read there), so under partition rule 2 it is not re-read. The first reader's passages for it (full-sample ORB success, sub-period non-robustness, 0.08% round-trip cost) were not re-verified in this pass. The CatalogWriter should use D.1 B4 as the source record. Tag: port of D.1 family B, CL-specific.

### K4-014
- Citation: Ewald, C.-O., Haugom, E., Ouyang, R., Smith-Meyer, E., Størdal, S. (2025). "Intra-day seasonality and abnormal returns in the Brent crude oil futures market." Quantitative Finance 25(11), 1731-1744 (per WebSearch; DOI 10.1080/14697688.2025.2535479 per OpenAlex). SSRN 5037563 (same source).
- Retrieval: abstract only, read from the University of Glasgow eprints record (curl + BeautifulSoup): https://eprints.gla.ac.uk/363707/. The record states the file is "Restricted to Repository staff only until 6 February 2027." Failed routes: SSRN (bot wall; no Wayback snapshot), Taylor & Francis (paywall).
- Mechanism: 1-minute Brent futures returns show statistically significant time-of-day patterns (peaks and troughs at particular clock times, differing by maturity and for spreads). Long-short strategies timed to those clock times earn positive, significant CAPM alphas after costs and margin.
- Products and horizon: ICE Brent futures, several maturities and calendar spreads; intraday clock-time holds.
- Cost assumptions: "realistic transaction costs and margin requirements" (values [unverified]).
- Data window: tick data Jan 2010 to Oct 2021 ("130 Gigabytes").
- Quality tells: many clock-time windows by maturity by spread invite multiple-testing issues; whether the paper adjusts for them is [unverified]. It is an ICE product, not CME.
- Verified passages:
  - P-K4-014-a (Abstract, Glasgow eprints): "We convert these data into one-minute data and observe statistically significant intra-day seasonal patterns with peaks and bottoms at particular times of the day, depending on maturities and whether or not spreads are considered. ... even when accounting for realistic transaction costs and margin requirements, some of the proposed strategies can create consistent positive and significant CAPM alphas."
  - P-K4-014-b (Abstract): "Our data cover tick data for futures of various maturities from January 2010 to October 2021, a database covering 130 Gigabytes of oil transactions."
- Numeric claims: none quantified in the abstract.
- Tags: port of D.1 family A (session clock), crude-specific but on ICE Brent. Transfer to CL is a hypothesis this source does not test. Intraday-feasible: yes by construction (the clock-time windows fall within the day, per the abstract).
- Clusters tagged: K4 only (Brent is a non-CME signal/analogue instrument for CL).

### K4-017 / K4-018 / K4-045 (release-schedule documentation; not findings)
- Citations: U.S. EIA, "Weekly Petroleum Status Report" page (https://www.eia.gov/petroleum/supply/weekly/) and its schedule page (https://www.eia.gov/petroleum/supply/weekly/schedule.php) [K4-017]; U.S. EIA, "Weekly Natural Gas Storage Report Schedule" (https://ir.eia.gov/ngs/schedule.html) and the report page (https://ir.eia.gov/ngs/ngs.html) [K4-018]; American Petroleum Institute, "Weekly Statistical Bulletin" page, Wayback copy of 18 Nov 2025 (http://web.archive.org/web/20251118103548/https://www.api.org/products-and-services/statistics/api-weekly-statistical-bulletin) [K4-045; the live API URL returned a 404 page].
- Retrieval: full pages, curl + BeautifulSoup text extraction, 23 Sep 2026. The first reader's passage for K4-018 was a WebSearch paraphrase; it is replaced here by fetched text.
- Content (facts the event studies assume):
  - P-K4-017-a (WPSR schedule page): "The wpsrsummary.pdf, overview.pdf, and Tables 1-14 in CSV and XLS formats, are released to the web site after 10:30 a.m. eastern time on Wednesday. All other PDF and HTML files are released to the web site after 1:00 p.m. eastern time on Wednesday. For some weeks that include holidays, releases are delayed by one day."
  - P-K4-017-b (WPSR holiday table on the same page, as extracted): "The standard release time and day of the week will be at 10:30 a.m. eastern time on Wednesdays with the following exceptions. ... January 2, 2025 Thursday 11:00 a.m. New Year's Day ... January 23, 2025 Thursday 12:00 p.m. Martin Luther King Jr. Day / Inauguration ... February 20, 2025 Thursday 12:00 p.m. President's Day".
  - P-K4-018-a (NG storage schedule): "The standard release time and day of the week will be at 10:30 a.m. eastern time on Thursdays with the following exceptions. All times are eastern." Listed 2025-2026 exceptions include "November 26, 2025 Wednesday 12:00 p.m. Thanksgiving Day" and "November 13, 2026 Friday 10:30 a.m. Veterans Day".
  - P-K4-045-a (API WSB page, Wayback): "the weekly reports are scheduled for release every Tuesday afternoon at approximately 4:30 pm Eastern. If Monday is a Federal holiday, the reports are scheduled for release on Wednesday afternoon." and "Published every Tuesday afternoon, the WSB brings its subscribers accurate and reliable petroleum data 18 hours before the rest of the world gets the data from EIA."
- Implications for feasibility, stated as facts only: WPSR = Wednesday 09:30 CT; gas storage = Thursday 09:30 CT; holiday weeks shift to other days and to 10:00 or 11:00 CT; API = Tuesday about 15:30 CT, after the 15:08 CT flat time. API content can therefore only be read, not traded, on the release day.
- Tags: documentation (no mechanism). Clusters tagged: K4.

### K4-020
- Citation: Jang, H. J., Lee, K., Lee, K. (2020). "Systemic Risk in Market Microstructure of Crude Oil and Gasoline Futures Prices: A Hawkes Flocking Model Approach." Journal of Futures Markets (online 2019 per OpenAlex; volume and pages not verified; published version DOI 10.1002/fut.22048; the first reader registered only the arXiv id). arXiv:2012.04181 [q-fin.TR].
- Retrieval: full text, arXiv v1 (8 Dec 2020). URL read: https://arxiv.org/pdf/2012.04181 (curl, pdftotext). The published JFM version and the arXiv version are one source.
- Mechanism: a bivariate Hawkes model of CL and RB tick-level price changes estimates self-excitation (endogeneity) and cross-excitation (interactivity). RB price changes excite CL price changes more than CL excites RB, and the asymmetry narrowed over 2007-2016. The paper measures systemic risk; it runs no return-predictability or trading test.
- Products and horizon: CL and RB nearest-delivery futures; transaction level, one-second resolution; excitation decays at microstructure time scales.
- Cost assumptions: none (no strategy).
- Data window: 1 Jan 2007 to 30 Dec 2016, trade prices from Tickdatamarket.
- Quality tells: a risk-measurement paper benchmarked against CoVaR. The "RB affects CL more" result is a branching-ratio statement, not a lead-lag return statement. Irregular preprocessing: prices are rescaled every 10 minutes, and several changes in one second are spread evenly across that second.
- Verified passages:
  - P-K4-020-a (Abstract): "The endogenous systemic risk in WTI was significantly higher than that in gasoline, and the level at which gasoline affects WTI was constantly higher than in the opposite case. Moreover, although the relative influence's degree was asymmetric, its difference has gradually reduced."
  - P-K4-020-b (Sec. 3.2): "We consider the data for 10 years from January 1, 2007 to December 30, 2016, and each year has twelve delivery months."
  - P-K4-020-c (Sec. 3.2 (ii)): "The minimum resolution time of the data is one second, and multiple price changes can be observed in one second."
  - P-K4-020-d (Sec. 5): "the change in gasoline futures price has a significantly greater impact on WTI crude oil futures price than in the opposite case, which implies that the relative contribution of each price is asymmetric at the microscopic level of price structure."
- Numeric claims: none quantitative logged (the branching-ratio estimates are model parameters, not tradeable magnitudes).
- Tags: new to the program (RB-to-CL microstructure lead). Intraday-feasible: no as tested. The effect lives at second-level time scales, which would need high-rate trading (prohibited) and limit-order fills (unavailable). At most it hints that RB may lead CL, which a minute-bar lead-lag test would have to establish on its own.
- Clusters tagged: K4 only.

### K4-021
- Citation: Wen, Z., Indriawan, I., Lien, D., Xu, Y. (2023). "Intraday Return Predictability in the Crude Oil Market: The Role of EIA Inventory Announcements." The Energy Journal 44(5), 149-171 (per the repository cover sheet). DOI 10.5547/01956574.44.4.zwen. SSRN 3822093 is the working-paper version (same source).
- Retrieval: full text, accepted version, University of Adelaide repository. URL read: https://digital.library.adelaide.edu.au/dspace/bitstream/2440/141224/2/hdl_141224.pdf via firecrawl_scrape (PDF parser; curl returned 404). The SSRN download returned 403.
- Mechanism: intraday momentum on EIA days. On Wednesdays with the 10:30 ET WPSR, the return over the third half-hour (10:30-11:00 ET, the release interval) positively predicts the return over the last half-hour of the NYSE session (15:30-16:00 ET). On other days only the first half-hour return (mostly its overnight component) predicts the last half-hour. The authors attribute this to informed trading and reduced liquidity around the release.
- Products and horizon: the USO ETF (NYSE Arca), not CL futures; 1-minute data aggregated to half-hours, 09:30-16:00 ET. Last half-hour = 14:30-15:00 CT, which is inside the XFA window, but it is after the 13:30 CT CL settlement and in thinner CL trading.
- Cost assumptions: none; no transaction costs in the Table 6 strategy returns.
- Data window: 10 Apr 2006 to 31 Jul 2019; 3,240 trading days; 591 Wednesday-10:30 EIA releases.
- Quality tells: (1) the traded instrument is USO, not CL. Transfer to CL is plausible but untested, and the ETF close has no analogue in CL. (2) The Sharpe ratios are not credible as stated: long-only earns an "insignificant" 1.04% a year yet is reported with Sharpe 5.15, and the EIA strategy with 4.14% a year gets Sharpe 19.54. The scaling is evidently not a standard annualized Sharpe, so only the mean returns and t-stats are usable. (3) No costs. (4) The authors report a declining trend and no predictability during 2014-2016. (5) Predictive adjusted R2 is 3.10% on EIA days.
- Verified passages:
  - P-K4-021-a (Abstract): "Our results indicate that returns on the third half-hour on EIA announcement days can significantly and positively predict the returns in the last half-hour, whereas, on non-EIA announcement days, only returns in the first half-hour have significant predictability. The dominant source of prediction in the first half-hour return mainly comes from the overnight component."
  - P-K4-021-b (Sec. 2.1): "We collect USO ETF data at a one-minute frequency from Refinitv Tick History. The sample period is from April 10, 2006, when the ETF started trading, to July 31, 2019."
  - P-K4-021-c (Table 1, Panel A, EIA days, column [1]): "𝑟₃ | 0.038** ... [2.12] ... Obs. | 591 ... Adj. R2(%) | 3.10".
  - P-K4-021-d (Sec. 5): "The long-only strategy generates a statistically insignificant annualized return of 1.04% ... The long-only and buy-and-hold strategies yield a Sharpe ratio of 5.15 and -10.51, respectively." and "using 𝑟₃ as a trading signal on days with EIA announcements, we can generate an even higher average return of 4.14% per annum and a Sharpe ratio of 19.54."
  - P-K4-021-e (Sec. 5, Figure 4 discussion): "the intraday momentum phenomenon is strong and statistically significant over our sample period, albeit with a declining trend. ... during the crude oil price plunge between 2014 and 2016, the intraday return predictability is not observed."
- Numeric claims: r3 slope 0.038 (t=2.12), adj. R2 3.10% on 591 EIA days (P-K4-021-c); 4.14% a year before costs (P-K4-021-d; the Sharpe 19.54 is unusable, see quality tells).
- Tags: port of D.1 family C (intraday momentum, first/third half-hour predicts the last), conditioned on an energy-specific event (family E). Intraday-feasible: yes. Enter at 14:30 CT and exit by 15:00 CT (before 15:08 CT), one trade per Wednesday; on CL the "last half-hour" would have to be redefined, since the CL day session settles at 13:30 CT.
- Clusters tagged: K4 only.

### K4-022
- Citation: Rousse, O., Sévi, B. (2019). "Informed Trading in the WTI Oil Futures Market." The Energy Journal 40(2). DOI 10.5547/01956574.40.2.orou. Working paper: "Informed Trading in Oil-Futures Market," GAEL WP 07/2016 (1 Dec 2016), hal-01410093v2 (same source).
- Retrieval: full text of the working paper. URL read: https://hal.science/hal-01410093/file/Rousse_gael2016-07.pdf (curl, pdftotext). The published version was not retrieved (Sage paywall; HAL record hal-02024317 has no file). The published abstract, seen in the OpenAlex record, differs slightly in wording.
- Mechanism: on WPSR days when the build greatly exceeds the Bloomberg median forecast (3-sigma "positive surprise"), CL shows net seller-initiated order imbalance and a price run-up (decline) of about -0.25% starting around 08:30 ET, two hours before the 10:30 release. The release-time drop of about 0.5% partly reverses over the following four hours (overreaction).
- Products and horizon: CL front contract, tick data; 08:30-14:30 ET (07:30-13:30 CT) on Wednesdays.
- Cost assumptions: none (event study, no strategy).
- Data window: Feb 2007 to Oct 2014; 402 WPSR releases, 90 3-sigma surprises (43 positive, 47 negative). Trade direction is classified by the tick rule.
- Quality tells: (1) the pre-release drift is conditioned on the sign of the surprise, which is known only after the release, so the result is not a tradeable rule without an ex-ante predictor. (2) Only 43 events drive the headline result. (3) Internal inconsistency: the abstract says "significantly more orders initiated by buyers", while the conclusion and the Section 4 results say "selling-initiated" imbalance. The price direction (down) fits selling. (4) The authors say they cannot identify the leakage channel.
- Verified passages:
  - P-K4-022-a (Abstract, WP p.1): "there are significantly more orders initiated by buyers in the two hours preceding the official release of the inventory level. We also show a clear drop in the average price of -0.25% ahead of the news release. This is consistent with informed trading. We also provide evidence of an asymmetric response of the oil price to the news, and highlight an over-reaction that is partly compensated in the hours following the announcement."
  - P-K4-022-b (Sec. 5, Conclusion): "This paper has provided evidence of a clear run-up price effect of about 0.25% and large selling-initiated transactions ahead of the EIA-DOE inventory release each Wednesday, when the level to be released is higher than expected."
  - P-K4-022-c (Sec. 3, surprise definition): "we define a surprise as an actual value that is over three standard deviations from the median forecast in the Bloomberg survey: we call these 3σ surprises." and "In the total sample of 402 announcements over the February 2007 – October 2014 period, there are 90 surprises (22.39%), of which 43 are positive and 47 are negative."
  - P-K4-022-d (Sec. 4): "days with positive surprises are characterized by a large average price drop of about 0.5% – traders take short positions as inventories are larger than expected – which is partly corrected in the hours following the news release. Four hours later, the drop is half as large, i.e. 0.25%."
  - P-K4-022-e (Sec. 4, OID regression): "The results clearly indicate a significant association between the dummy for positive surprises and the average OID over the 8:30 – 9:30 period. The t-statistic is large (3.154)".
- Numeric claims: -0.25% pre-release drift on 3-sigma positive-surprise days (P-K4-022-a, b); about -0.5% release drop, half reversed within 4 hours (P-K4-022-d); OID t = 3.154 (P-K4-022-e); 43 positive events (P-K4-022-c).
- Tags: port of D.1 family E (pre-release drift), CL-specific; the post-release partial reversal is a port of family C (reversal after an event shock). Intraday-feasible: the post-release reversal (fade the release move from 10:30 ET into early afternoon, flat by 13:30 CT) is feasible. The pre-release drift is feasible only with an ex-ante predictor of the surprise sign (see K4-012 for NG).
- Clusters tagged: K4 only.

### K4-023
- Citation: Ye, S., Karali, B. (2016). "The informational content of inventory announcements: Intraday evidence from crude oil futures market." Energy Economics 59, 349-364. DOI 10.1016/j.eneco.2016.08.011. Earlier version: AAEA/WAEA 2015 selected poster (AgEcon Search record 205595), same source.
- Retrieval: the 2-page 2015 poster only. URL read: https://ageconsearch.umn.edu/record/205595/files/AAEA_Ye_Karali-2015.pdf via firecrawl_scrape (PDF parser; curl got an HTTP 202 bot challenge and WebFetch 403). The published full text was not retrieved (Elsevier paywall; no open copy found in OpenAlex or WebSearch). Everything below comes from the poster; any claim about the published paper's longer sample is [unverified].
- Mechanism: API (Tuesday 16:30 ET) and EIA (Wednesday 10:30 ET) surprises in crude, distillate and gasoline inventories (against the Reuters median forecast) move 15-minute CL returns. Expected changes do not move CL. The EIA crude surprise impact is about twice the API impact, and distillate and gasoline surprises also move CL.
- Products and horizon: CL (electronic); 15-minute windows 16:25-16:40 ET (API) and 10:25-10:40 ET (EIA).
- Cost assumptions: none.
- Data window (poster): 24 May 2013 to 9 May 2014, 50 weeks.
- Quality tells: a one-year poster sample; the published version may differ. The jump table counts only 11 of 50 EIA reports producing a significant jump.
- Verified passages:
  - P-K4-023-a (poster, Data): "Sample period: May 24, 2013–May 9, 2014 (50 weeks or 249 trading days)" and "API report: Tuesdays at 4:30pm EST ... EIA report: Wednesdays at 10:30am EST".
  - P-K4-023-b (poster, Table 2): "Crude oil | Positive Inventory Shock | -0.134 (0.000) | -0.231 (0.004) | ... Negative Inventory Shock | -0.126 (0.000) | -0.247 (0.033)" (API return column, then EIA return column).
  - P-K4-023-c (poster, results): "The impact of crude oil inventory surprises in EIA report is almost twice the impact of the surprise in API reports." and "In total, 11 out of 50 EIA reports generated significant return jumps."
  - P-K4-023-d (poster, conclusions): "Crude oil returns are also affected by the unexpected inventory changes in distillate oil and gasoline."
- Numeric claims: API crude-shock coefficients -0.134/-0.126, EIA -0.231/-0.247 (P-K4-023-b); 11 of 50 EIA reports with jumps (P-K4-023-c). Published-sample figures: [unverified].
- Tags: port of D.1 family E (scheduled release). Intraday-feasible: the API release (16:30 ET = 15:30 CT) falls after the 15:08 CT flat time and cannot be traded. The API surprise can only be READ as information for the next day's pre-EIA window (see K4-009). The EIA response is inside the day (09:30 CT) but contemporaneous.
- Clusters tagged: K4 only.

### K4-024
- Citation: Bjursell, J., Wang, G. H. K., Zheng, H. (2017). "VPIN, Jump Dynamics and Inventory Announcements in Energy Futures Markets." Journal of Futures Markets 37(6), 542-577. DOI 10.1002/fut.21839 (volume and pages from the Wiley citation metadata).
- Retrieval: full text, working-paper version dated 1 Aug 2016, hosted by AUT (ACFR conference). URL read: https://acfr.aut.ac.nz/__data/assets/pdf_file/0003/36309/Johan-V2-644434-vpin_bjursell_wang_zheng.pdf via firecrawl_scrape (PDF parser; curl returned 403). The published abstract was also scraped from Wiley (it matches).
- Mechanism: VPIN (order-flow toxicity) rises around inventory announcements that carry price jumps and around unscheduled jumps in CL and NG. It peaks after the event, not before. An exponentially smoothed VPIN is a better early warning of large subsequent absolute returns. This is a volatility and toxicity measure with no directional return claim.
- Products and horizon: CL and NG front futures; 1-minute bars aggregated into volume buckets (daily volume / 50); horizon of minutes to hours.
- Cost assumptions: none.
- Data window: 1 Jan 2009 to 31 May 2015.
- Quality tells: the "early warning" claim is a conditional-probability association between the prior-bucket VPIN percentile and the next bucket's absolute return, not an out-of-sample forecast test. The authors frame the result against an ongoing debate about VPIN's predictive power (Andersen-Bondarenko).
- Verified passages:
  - P-K4-024-a (Abstract, WP): "VPIN increased significantly around the inventory announcements with price jumps (scheduled events) and at jumps not associated with any scheduled announcements (unscheduled events). (2) VPIN did not peak prior to the events but shortly after. (3) A minor variation of VPIN based on exponential smoothing significantly improved the early warning signal property of VPIN."
  - P-K4-024-b (Sec. 5): "Our sample period spans from January 1, 2009 to May 31, 2015."
  - P-K4-024-c (Sec. 4, conditional probabilities): "for absolute value of returns in the bins 2.0% and ≥ 2.00%, the probability associated with VPIN in the 1.00 percentile are 36% and 30.8% while the corresponding probabilities for EXPS_VPIN α=0.1 are 72.% and 69.2% for crude oil futures."
- Numeric claims: for large CL absolute-return buckets, the share preceded by the top-percentile VPIN is 36%/30.8% for VPIN against 72%/69.2% for the smoothed variant (P-K4-024-c).
- Tags: port of D.1 family D (volatility/liquidity state), energy-specific. Intraday-feasible: as a volatility-state filter, yes (bucket-level, minutes); as a directional signal, no (none claimed).
- Clusters tagged: K4 only.

### K4-025
- Citation: Rosa, C. (2013). "The High-Frequency Response of Energy Prices to Monetary Policy: Understanding the Empirical Evidence." Federal Reserve Bank of New York Staff Report No. 598, February 2013. (A later journal version exists per the IDEAS listing fip/fednsr/598; not retrieved, same source.)
- Retrieval: full text. URL read: https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr598.pdf (curl, pdftotext).
- Mechanism: FOMC target surprises (fed funds futures) move CL, HO and NG within a 1-hour window around the statement: a hypothetical +100 bp target surprise means about -2.7% on CL. The effect works mainly through the dollar, since energy prices in other currencies do not respond. Intraday energy prices also respond to macro releases (industrial production, payrolls, consumer confidence) and inventories, but daily responses are insignificant except for inventory news. For the LSAP events, intraday and daily CL returns correlate at -0.24, so the immediate move reversed within the day.
- Products and horizon: CL (front, 2nd, 3rd, 6th), HO, NG; 5-minute mid-quotes; 1-hour window around 14:15 ET (13:15 CT) FOMC statements; macro-release windows.
- Cost assumptions: none.
- Data window: Jan 1999 to Jun 2011.
- Quality tells: FRBNY staff report, "preliminary findings". The LSAP estimates are "surrounded by considerable uncertainty" per the author. The -0.24 reversal correlation covers only a handful of LSAP events.
- Verified passages:
  - P-K4-025-a (Abstract): "I find that, on average, a hypothetical unanticipated 100 basis point hike in the federal funds target rate is associated with roughly a 3 percent decrease in West Texas Intermediate oil prices. ... Monetary policy affects oil prices mostly by affecting the value of the U.S. dollar exchange rate. Intraday energy prices also respond to news announcements about the U.S. macroeconomy and inventories. The daily responses are never significant, except in the case of inventory news."
  - P-K4-025-b (Introduction): "in a 1-h window around the FOMC press release a hypothetical unanticipated 100-basis-point hike in the federal funds target rate is associated with 2.7% decline in crude light oil price and 1.8% decrease in heating oil price."
  - P-K4-025-c (Sec. 2.1): "The high-frequency energy prices consist of 5-min quotes of futures data on light sweet crude oil ... heating oil, and natural gas (Henry Hub), and covers the period January 1999 - June 2011."
  - P-K4-025-d (Sec. 3): "the correlation between intraday and daily crude oil futures returns equals -0.24, suggesting that for this specific time series realization the immediate asset price response was reversed in the course of the trading day."
  - P-K4-025-e (Sec. 4): "A hypothetical unanticipated 100-basis-point hike in the federal funds target rate is associated with 1.8% decline in heating oil futures prices and 2.7% decline in natural gas futures."
- Numeric claims: CL -2.7% per +100 bp target surprise in 1 hour (P-K4-025-b); HO -1.8%, NG -2.7% (P-K4-025-e); intraday-daily correlation -0.24 on LSAP events (P-K4-025-d).
- Tags: port of D.1 family E (FOMC), energy product. Intraday-feasible: the statement falls at 13:15 CT (14:00 ET in later years), inside the XFA window, but the response is contemporaneous and a surprise needs a fed-funds-futures reading. The within-day reversal hint (P-K4-025-d) is feasible (fade into 15:08 CT) but rests on few events.
- Clusters tagged: K4. The dollar-channel finding (energy in other currencies does not move) is a USD/energy relationship: flagged for K8 in section 4, passage not used here.

### K4-026
- Citation: Miao, H., Ramchander, S., Wang, T., Yang, J. (2018). "The impact of crude oil inventory announcements on prices: Evidence from derivatives markets." Journal of Futures Markets 38(1), 38-65. DOI 10.1002/fut.21850.
- Retrieval: full text, author manuscript in the Colorado State University repository (Mountain Scholar). URL read: https://mountainscholar.org/bitstream/10217/206701/1/Wang_TY_FutMar_2018.pdf (curl, pdftotext).
- Mechanism: daily CL futures and options returns respond to the WPSR surprise on the release day. On the day before the release (day -1), returns already move in the direction of the coming surprise: the coefficient on the next day's standardized surprise is significant and negative. There is no persistence after the release.
- Products and horizon: CL futures (six contracts along the curve) and CL options; DAILY returns (settlement to settlement), [-2,+2] day windows.
- Cost assumptions: none for futures (the options section mentions profits from writing OTM calls in-sample, with no costs).
- Data window: 16 Jun 2003 to 30 Dec 2011; 446 EIA releases (223 positive, 223 negative surprises against the Bloomberg median).
- Quality tells: a daily-frequency study. The day -1 "anticipation" is measured against the ex-post surprise, and the paper does not separate the Tuesday 16:30 ET API release from informed trading. API falls inside the day -1 settlement-to-settlement window only partially (after the 14:30 ET settle, so it lands in the day 0 return). The mechanism behind the day -1 effect is left open.
- Verified passages:
  - P-K4-026-a (Abstract): "We document evidence of a strong announcement day effect on both markets, and find prices to move in anticipation of the inventory surprise. Futures returns significantly decrease with positive surprises and increase with negative surprises. There is no evidence of an asymmetric impact on futures prices."
  - P-K4-026-b (Sec. 3): "The sample period of our study is June 16, 2003 to December 30, 2011, which includes 446 EIA inventory news releases."
  - P-K4-026-c (Sec. 4.1.3): "the coefficients for 𝑆𝑈𝑅𝑡−1 and 𝑆𝑈𝑅𝑡−2 are insignificant for all the 6 contracts ... we do not find any persistence of the impact of inventory news announcements on the returns of futures. Third, the coefficients for 𝑆𝑈𝑅𝑡+1 are significant and negative for all the different contracts. ... For instance, 𝛾1 = −0.289 without macroeconomic news and 𝛾1 = −0.236 with macroeconomic announcements. This suggests that the futures market seems to anticipate the surprises correctly one day before the storage announcement." (subscript symbols garbled in the text extraction; rendered here as SUR)
  - P-K4-026-d (Sec. 4.1.3): "in Table 12, 𝛾0 = −0.507 with t-statistics of -3.97."
- Numeric claims: day -1 coefficient on the next day's surprise -0.289 / -0.236 (P-K4-026-c); release-day coefficient -0.507, t=-3.97 (P-K4-026-d).
- Tags: port of D.1 family E (pre-event drift), CL. Intraday-feasible: not as tested (daily settlement returns). An intraday version (a Tuesday-session position closed by 15:08 CT) is a design step the paper does not take. The day -1 effect needs an ex-ante surprise predictor to trade.
- Clusters tagged: K4 only.

### K4-027
- Citation: Pirrong, C. (2023). "Strategic trading and manipulation in trade at settlement contracts." Journal of Futures Markets 43(5), 615-634. DOI 10.1002/fut.22401.
- Retrieval: abstract only. OpenAlex listed a "pdfdirect" OA URL; firecrawl_scrape of it returned the Wiley abstract page, and the ePDF reader failed ("wiley.scienceconnect.io is blocked"). curl of pdfdirect returned 403. The abstract and data-availability statement were read from that scraped page.
- Mechanism: holders of large TAS positions can profit by trading the underlying around the settlement window, which causes excess and partly permanent price moves. Concentration of TAS positions and price moves can identify it.
- Products and horizon: TAS contracts in general. Which futures (CL, where TAS is heavily used, or others) is [unverified]; data "from www.barchart.com". Horizon: the settlement window (CL: 13:28-13:30 CT).
- Cost assumptions / data window: [unverified].
- Verified passages:
  - P-K4-027-a (Abstract): "TAS contracts are susceptible to strategic, and indeed manipulative, trading by large intermediaries. Those with large TAS positions can profit from trading strategically/manipulatively, and this trading tends to cause excessive price movements. Moreover, some of the price impacts of such strategic trading are permanent."
  - P-K4-027-b (Data Availability Statement): "The data that support the findings of this study are available from www.barchart.com."
- Numeric claims: none.
- Tags: new to the program (settlement-window flow). Intraday-feasible: the window is inside the XFA day, but the mechanism is described as large-intermediary strategic trading. A follower rule would need public TAS concentration information, and whether any exists is [unverified].
- Clusters tagged: K4 (product coverage [unverified]).

### K4-028
- Citation: Chiou-Wei, S.-Z., Linn, S. C., Zhu, Z. (2014). "The response of U.S. natural gas futures and spot prices to storage change surprises: Fundamental information and the effect of escalating physical gas production." Journal of International Money and Finance 42, 156-173. DOI 10.1016/j.jimonfin.2013.08.009 (confirmed via OpenAlex after the registry claim).
- Retrieval: full text of the working-paper version dated 16 Mar 2013 (IMF 2012 commodity seminar). URL read: https://www.imf.org/-/media/websites/imf/imported-events/external/np/seminars/eng/2012/commodity/pdf/_linnpdf.pdf (curl, pdftotext). The published abstract was read from IDEAS (curl): https://ideas.repec.org/a/eee/jimfin/v42y2014icp156-173.html.
- Mechanism: NG front-month settlement changes on EIA storage-report days are inversely related to the storage surprise against the Bloomberg consensus. The response is symmetric, is not larger for larger surprises, and grew after 2005 (shale era). There is no economically meaningful response on days other than the release day, so no multi-day drift.
- Products and horizon: NYMEX NG front month, DAILY settlement-to-settlement changes; Henry Hub spot.
- Cost assumptions: none.
- Data window: Aug 2002 to Aug 2011.
- Quality tells: daily resolution only. The informative content for the program is the null on non-release days.
- Verified passages:
  - P-K4-028-a (WP Abstract): "Our study spans August 2002 through August 2011. We identify an inverse empirical relation between changes in futures prices and surprises in the change in natural gas in storage and that this relation is not driven by the absolute size of the surprise."
  - P-K4-028-b (published abstract, IDEAS): "No evidence is found of economically meaningful reactions to the surprise other than on the date the storage news is released."
  - P-K4-028-c (WP Sec. V): "We find an inverse and statistically significant relation between the change in storage surprise and the log futures price change. Further, we find that the size of the reaction has become larger post 2005."
- Numeric claims: none logged beyond the qualitative results (the regression coefficients were not needed; not re-checked).
- Tags: port of D.1 family E; daily. Intraday-feasible: no as tested (daily settlements). It serves as evidence against a multi-day post-release drift in NG.
- Clusters tagged: K4 only.

### K4-029
- Citation: Gu, C., Kurov, A., Stan, R. (2026). "Trader Attention and Market Reaction to Fundamental News: Evidence From Natural Gas Futures." Journal of Futures Markets 46(7), 1171-1181. DOI 10.1002/fut.70104.
- Retrieval: abstract only, via IDEAS (curl): https://ideas.repec.org/a/wly/jfutmk/v46y2026i7p1171-1181.html. Failed routes: Wiley (paywall), no WP found (OpenAlex author list, WebSearch).
- Mechanism: on holiday weeks, when the gas storage report moves to Friday, NG's response to the surprise is much weaker than on Thursdays, which the authors attribute to lower Friday attention.
- Products and horizon: NG; "daily regression estimates".
- Verified passages:
  - P-K4-029-a (Abstract): "Based on our daily regression estimates, the market responds 74% weaker to inventory announcements released on Fridays, compared to those released on Thursdays. We attribute the findings to lower trader attention in the natural gas market on Fridays compared to other weekdays."
- Numeric claims: 74% weaker Friday response (P-K4-029-a). Whether the missing response is recovered later (drift) is [unverified].
- Tags: port of D.1 family E (event, with a day-of-week condition). Intraday-feasible: daily as tested. A follow-up drift after Friday releases would have to be held over the weekend (infeasible) unless it completes intraday [unverified]. There are few events (holiday-shifted weeks only).
- Clusters tagged: K4 only.

### K4-030
- Citation: Liu, W.-M., Schultz, E. L., Swieringa, J. (2015). "Price Dynamics in Global Crude Oil Markets." Journal of Futures Markets 35(2), 148-162. DOI 10.1002/fut.21658.
- Retrieval: abstract only, via IDEAS (curl): https://ideas.repec.org/a/wly/jfutmk/v35y2015i2p148-162.html. Failed routes: the ANU Open Research record (hdl 1885/13630) is metadata only (DSpace API bundles: LICENSE/SWORD, no ORIGINAL file), Wiley (paywall), ResearchGate (not attempted).
- Mechanism: with high-frequency data, CME WTI dominates price discovery over ICE Brent on days when the two are cointegrated. Cushing constraints reduced cointegration.
- Products and horizon: CL against ICE Brent; high-frequency. The window is [unverified].
- Verified passages:
  - P-K4-030-a (Abstract): "we quantify the impact of oil supply constraints at Cushing, showing they are a significant determinant of ever decreasing levels of cointegration between Brent and WTI markets. Finally, against this backdrop we show that, on days where ICE Brent and CME WTI futures remain cointegrated, the latter still dominate price discovery."
- Numeric claims: none.
- Tags: port of D.1 family F (data-native lead-lag). It argues against Brent as a leading signal for CL. Intraday-feasible: n/a (evidence about signal direction).
- Clusters tagged: K4 only (Brent is a non-CME signal instrument for CL).

### K4-031
- Citation: Fernandez-Perez, A., Garel, A., Indriawan, I. (2020). "Natural Gas Storage Forecasts: Is the Crowd Wiser?" The Energy Journal 41(5), 213-238. DOI 10.5547/01956574.41.5.afer. SSRN 3498025.
- Retrieval: abstract only, via IDEAS (curl): https://ideas.repec.org/a/sae/enejou/v41y2020i5p213-238.html. Failed routes: HAL hal-02635639 (record without a file, per the HAL API), SSRN Delivery (bot wall), AUT ACFR page (403), Sage (paywall).
- Mechanism: crowdsourced (Estimize) NG storage forecasts are less accurate than professional ones and add nothing to the market's expectation beyond the professional consensus.
- Products and horizon: NG storage report; the market-expectation test window is [unverified].
- Verified passages:
  - P-K4-031-a (Abstract): "We find that crowdsourced forecasts are less accurate than professional forecasts on average. ... We further show that crowdsourced consensus forecast does not influence the market's expectation of gas storage changes beyond what is already contained in professional consensus forecast".
- Numeric claims: none.
- Tags: new to the program (a null for crowd forecasts as a surprise predictor). Intraday-feasible: n/a (input evaluation).
- Clusters tagged: K4 only.

### K4-032
- Citation: Armstrong, W. J., Cardella, L., Sabah, N. (2021). "Information shocks, disagreement, and drift." Journal of Financial Economics 140(3), 916-940. DOI 10.1016/j.jfineco.2021.02.002. SSRN 3314221.
- Retrieval: abstract only. Read from the Wayback copy of the SSRN abstract page (curl): http://web.archive.org/web/20250512184529/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3314221. Failed routes: SSRN Delivery (Wayback holds only the HTML challenge page, per CDX), ScienceDirect (paywall), the Louisiana Tech research portal (metadata only), OpenAlex (no abstract, no OA).
- Mechanism: after the recurring crude-oil public information event (the WPSR, per the paper's framing [unverified from the abstract, which says only "a recurring public information event"]), CL absorbs good news within half a second but drifts for five minutes after bad news, because of a surge of buying that impedes price discovery.
- Products and horizon: CL; sub-second to 5 minutes after the release.
- Verified passages:
  - P-K4-032-a (Abstract): "We show that prices reflect positive news within one-half second of trading, but continue to drift for five minutes when news is negative. Evidence suggests the drift arises from a systematic surge in buying pressure that impedes the price discovery process when news is negative."
- Numeric claims: 0.5-second absorption against a 5-minute drift (P-K4-032-a).
- Tags: port of D.1 family C (short-horizon post-event momentum), CL-specific. Intraday-feasible: marginal. A 5-minute drift after a bearish release could be followed with a market order within seconds, but the capturable part after TopstepX latency and the release-minute spread is unknown. The trade is once a week, so it is not high-rate.
- Clusters tagged: K4 only.

### K4-033
- Citation: Chang, C., Daouk, H., Wang, A. Z. (2009). "Do investors learn about analyst accuracy? A study of the oil futures market." Journal of Futures Markets 29(5), 414-429. DOI 10.1002/fut.20374. SSRN 1531886 (same source).
- Retrieval: abstract only, via IDEAS (curl): https://ideas.repec.org/a/wly/jfutmk/v29y2009i5p414-429.html. Failed routes: SSRN (bot wall; no Wayback snapshot), Wiley (paywall), Unpaywall (not OA).
- Mechanism: CL moves when analysts publish their inventory forecasts (up on forecast draws, down on forecast builds). In the 15 minutes after the WPSR, CL moves against the analysts' forecast error. Both effects are stronger for historically accurate analysts. This is the crude analogue of K4-005.
- Products and horizon: CL; around forecast publication and the 15 minutes after the WPSR.
- Cost assumptions / data window: [unverified].
- Verified passages:
  - P-K4-033-a (Abstract): "We find that prices rise (fall) when analysts forecast a decrease (increase) in supplies. During the 15 minutes following supply announcements, prices rise (fall) when forecasts have been too high (low). Importantly, both relationships are stronger for more accurate analysts, implying that investors learn about analyst accuracy."
- Numeric claims: none.
- Tags: new to the program (price response to analyst forecast publication, accuracy-weighted). Intraday-feasible: the post-release 15-minute response is contemporaneous. The forecast-publication response is feasible only if the forecast release times are known and fall inside the session [unverified].
- Clusters tagged: K4 only.

### K4-034
- Citation: Dubois, M., Maréchal, L. "The Valuation Effects of Index Investment in Commodity Futures." SSRN 3942440 (SSRN version posted 2023 per WebSearch). Version read: working paper dated 15 Jan 2020, EFMA 2020 (Dublin) full paper; same source, earlier version.
- Retrieval: full text of the 2020 EFMA version. URL read: https://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2020-Dublin/papers/EFMA%202020_stage-1301_question-Full%20Paper_id-418.pdf (curl with TLS verification disabled because the site sends an incomplete certificate chain; WebFetch failed on the same certificate; pdftotext). The AUT copy returned 403; the SSRN PDF was not attempted (bot wall). The WebSearch summary of the later SSRN version reports different magnitudes ("115 bps ... 146 bps" before 2004, "-60 bps (-40 bps)" 2004-2010). Those are [unverified] and conflict with the 2020 version's "17 basis points at most".
- Mechanism: price pressure from the S&P GSCI roll (5th to 9th business day of the month before maturity, 20% a day) on nearby and first-deferred contracts across the 27 GSCI constituents, tested with a difference-in-differences across a dated financialization break. In the 2020 version the abnormal term-structure change is small, explained by arbitrage transaction costs, and not significant once standard errors account for event-induced variance and cross-correlation.
- Products and horizon: 27 GSCI constituents, including CL, HO, RB, NG [K4]; GC, HG and LME metals [K5]; corn, wheat, Kansas wheat, soybeans, live cattle, feeder cattle, lean hogs [K6]. DAILY closing prices over the 5-business-day roll window.
- Cost assumptions: arbitrageur transaction costs are the explanatory variable (they "explain most of the abnormal term-structure change").
- Data window: 2 Jan 1999 to 31 Dec 2010.
- Quality tells: the two versions of the same paper appear to report different magnitudes (see Retrieval). The 2020 version reports its own null after correcting the standard errors, which is a positive tell.
- Verified passages:
  - P-K4-034-a (Abstract, 2020 version): "Finally, in a cruder market efficiency framework, we find that transaction costs incurred by an arbitrager (price taker) explain most of the abnormal term-structure change with a coefficient close to unity. In addition, this abnormal change -which is of 17 basis points at most- is never significant once we adjust the standard errors for event-induced variance and cross-correlation."
  - P-K4-034-b (Introduction): "The SP-GSCI rolls its position from the fifth to the ninth business day of the month preceding maturity (hereafter, the roll). Every day, the index transfers 20% of its positions from one contract to the next."
  - P-K4-034-c (Sec. 4): "We download the daily closing prices of the 27 commodity futures constituents of the SP-GSCI for the first five consecutive maturities m. The sample starts on January 2, 1999 and ends on December 31, 2010."
- Numeric claims: abnormal roll-window term-structure change of at most 17 bp, never significant after SE adjustment (P-K4-034-a). The later version's 115/146 bp and -60/-40 bp figures are [unverified].
- Tags: new to the program (commodity-index roll, owned by K4 for all commodities). Intraday-feasible: no as tested (a daily, 5-day window, and the effect is a nearby-versus-deferred spread). An intraday roll-flow rule would be a new design that this source does not test.
- Clusters tagged: K4, with the same passages applying to [K5] (GC, HG and LME metals among the 27 constituents, P-K4-034-c) and [K6] (grains and livestock among the constituents; the paper's CIT data cover "13 agriculture contracts"). The paper reports pooled results; per-commodity results were not extracted.

### K4-035
- Citation: Mou, Y. (2011 version; SSRN 2010). "Limits to Arbitrage and Commodity Index Investment: Front-Running the Goldman Roll." Columbia University working paper, SSRN 1716841; hosted by the CFTC among the position-limits study documents.
- Retrieval: full text, version dated 15 Jul 2011. URL read: https://www.cftc.gov/sites/default/files/idc/groups/public/@swaps/documents/file/plstudy_33_yu.pdf (curl, pdftotext). SSRN abstract also read via Wayback (curl): http://web.archive.org/web/20260716144352/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1716841. D.1 row E31 rejected this item on its title only, so this is not a re-read.
- Mechanism: the S&P GSCI roll (sell maturing, buy deferred, 5th to 9th business day) pushes down the nearby-minus-deferred calendar spread. Putting the same calendar spread on 10 to 6 days (Strategy 1) or 5 to 1 days (Strategy 2) before the roll, and unwinding during the roll, earned abnormal returns from 2000 to 2010. Energy was the best sector.
- Products and horizon: 19 US-listed GSCI commodities in four sector portfolios, including [K4] energy (CL, HO, RB and NG among the 19; the text names crude oil WTI, heating oil and gasoline RBOB), [K5] metals, [K6] agriculture and livestock. Multi-day calendar-spread holds (about 1 to 3 weeks); daily CRB settlement data.
- Cost assumptions: none in the backtest. The author argues from typical spreads ("For crude oil (WTI), the bid-ask-spread is often just 1 bp") that costs are low; that is an untested claim.
- Data window: Jan 1980 to Mar 2010, split at 2000.
- Quality tells: no transaction costs. The headline Sharpe of 4.39 is the "money manager" variant that counts only trading periods, and the always-invested variant is lower (1.09 to 2.75 for Strategy 1). The sample ends in 2010, and later work (K4-034, K4-036) finds small or no roll impact. It is a single-author PhD working paper.
- Verified passages:
  - P-K4-035-a (Abstract): "Two trading strategies, devised to exploit this anomaly, yielded excess returns with positive skewness and Sharpe ratios as high as 4.39 from 2000 to March 2010. The profitability of the strategies is positively correlated with the net result of two opposite forces: the size of index investment and the amount of arbitrage capital employed."
  - P-K4-035-b (Sec. 4): "calendar spread positions are created on each day in the first group, which runs from 10 to 6 business days before the SP-GSCI's first rolling date. The spread position involves shorting the maturing contracts that the SP-GSCI is currently holding and longing the deferred contracts that it will roll into. ... The calendar spread positions will be unwound in the SP-GSCI's rolling period."
  - P-K4-035-c (Introduction): "the annualized Sharpe ratios ranged from 1.09 to 2.75 with Strategy 1 and from 0.46 to 1.78 with Strategy 2. ... Energy sector is overall the best performing sector. With Strategy 1, the energy portfolio has unleveled annual excess return of 4.43%, with Sharpe ratio 2.2, skewness 0.88 and maximum drawdown only 0.94%."
  - P-K4-035-d (Sec. 4): "The CRB data set does not have data on the bid-ask-spreads, so I can not incorporate transaction costs into the evaluation of the strategies."
- Numeric claims: Sharpe up to 4.39 (trading-period basis) (P-K4-035-a); 1.09 to 2.75 always-invested for Strategy 1, energy 4.43% a year with Sharpe 2.2 (P-K4-035-c); no costs (P-K4-035-d).
- Tags: new to the program (commodity-index roll front-running). Intraday-feasible: no. It is a multi-day calendar-spread hold, and TopstepX would also need spread legs held overnight. The XFA flat rule forbids it as designed.
- Clusters tagged: K4. The same strategy passages apply to [K5] (metals sector portfolio, P-K4-035-c: "agriculture, livestock, energy and metals") and [K6] (agriculture and livestock portfolios, same passage). Sector-level figures for metals and ags were not extracted.

### K4-036
- Citation: Stoll, H. R., Whaley, R. E. (2010). "Commodity Index Investing and Commodity Futures Prices." Journal of Applied Finance 20(1) (per WebSearch; not verified against the journal). Version read: 10 Sep 2009, Vanderbilt WP hosted by the CFTC (SSRN 1478195 / 2693084, same source).
- Retrieval: full text. URL read: https://www.cftc.gov/sites/default/files/idc/groups/public/@swaps/documents/file/plstudy_45_hsrw.pdf (curl, pdftotext). SSRN abstract also read via Wayback (curl): http://web.archive.org/web/20250215211919/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2693084.
- Mechanism: tests whether GSCI and DJ-UBSCI rolls depress the nearby contract against the second nearby during the roll (4th to 9th business day, settlement to settlement). For eight ag and soft contracts, the differentials are a few basis points, "on order of the typical bid/ask spreads". For crude oil the S&P GSCI roll differential is 26 bp and significant, larger than CL's typical spread.
- Products and horizon: CL [K4] (Table II-4); wheat, corn, soybeans, cotton, lean hogs, live cattle, sugar, coffee (Table II-3; the Topstep-listed ones are [K6]). Settlement-to-settlement over the 5-day roll window (multi-day).
- Cost assumptions: magnitudes are compared with typical bid/ask spreads; there is no strategy.
- Data window: Jan 2006 to Jul 2009 (roll tests); daily data from the exchanges.
- Quality tells: funded by "a grant from Gresham Investment Management LLC" (a commodity index manager), which is a potential conflict of interest and is disclosed. The sample is short (3.5 years). The crude result contradicts the paper's general conclusion and the authors report it openly.
- Verified passages:
  - P-K4-036-a (SSRN abstract, Wayback): "We conclude that: a) commodity index investing is not speculation; b) commodity index rolls have little futures price impact, and inflows and outflows from commodity index investment do not cause futures prices to change".
  - P-K4-036-b (Sec. II, roll tests): "Scanning down the column of return differentials for the different commodity futures, we find that all but one (soybeans) is positive, and three are significant in the statistical sense. In a practical sense, however, the roll returns and return differentials are not economically meaningful, on order of the typical bid/ask spreads observed in these markets."
  - P-K4-036-c (Sec. II, crude oil): "The size of the return differential for the S&P-GSCI oil futures is 26 basis points, larger than typical bid/ask spreads in the NYME crude oil futures market. Apparently the crude oil futures market shows the effects of price impact during the index roll period due to the sheer size of the notional value of the futures contracts being rolled."
  - P-K4-036-d (Table II-3, K6 rows): "Wheat W 48 ... 0.0009 / Corn C 48 ... 0.0012* / Soybeans S 48 ... -0.0016 / ... Lean hogs LH 68 ... 0.0037 / Live cattle LC 58 ... 0.0021*" (return differential column; returns over the 4th to 9th business days).
  - P-K4-036-e (funding footnote): "This research was supported by a grant from Gresham Investment Management LLC."
- Numeric claims: CL GSCI roll differential 26 bp, significant (P-K4-036-c); ag differentials 0.09% to 0.37% or negative, 3 of 8 significant (P-K4-036-b, d).
- Tags: new to the program (commodity-index roll). Intraday-feasible: no as tested. It is a multi-day nearby-versus-deferred differential; a single-leg intraday version during roll days is untested.
- Clusters tagged: K4 (crude result), [K6] (P-K4-036-b and P-K4-036-d: wheat, corn, soybeans, lean hogs, live cattle), [K5] none (no metals in the roll tests).

### K4-037
- Citation: Wen, Z., Gong, X., Ma, D., Xu, Y. (2021). "Intraday momentum and return predictability: Evidence from the crude oil market." Economic Modelling (DOI 10.1016/j.econmod.2020.03.004; OpenAlex lists 2020). SSRN 3553682.
- Retrieval: abstract only, via the Wayback copy of the SSRN page (curl): http://web.archive.org/web/20250507014439/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3553682. Failed routes: SSRN PDF (bot wall), Elsevier (paywall), OpenAlex/Unpaywall (no OA copy).
- Mechanism: in USO from 2006 to 2018, the first half-hour return (mainly its overnight component) positively predicts the last half-hour return. The two weekly inventory announcements shape intraday volume but do NOT predict the last half-hour. This conflicts with the same first author's later K4-021 (EIA third half-hour predicts the last half-hour).
- Products and horizon: USO ETF, half-hour returns, 09:30-16:00 ET.
- Verified passages:
  - P-K4-037-a (Abstract): "We find a different intraday prediction pattern in the oil market, where only the first half-hour returns positively predict the last half-hour returns. A market timing strategy based on the findings generates substantial profits. We further decompose the first half-hour return into the overnight and the open half-hour components, and find that the former contains more predictive information."
  - P-K4-037-b (Abstract): "Notably, unlike equity markets, the oil market exhibits a unique intraday trading volume pattern, caused by the release of two routine oil inventory announcements. However, the information contained in the inventory announcements does not offer predictability to the last half-hour returns."
- Numeric claims: none in the abstract ("substantial profits" unquantified; [unverified]).
- Tags: port of D.1 family C (intraday momentum, first half-hour to last half-hour) on a crude vehicle. Intraday-feasible: yes (a last-half-hour hold that ends 15:00 CT for the USO clock; a CL analogue would need a redefined close). Note the direct tension with K4-021.
- Clusters tagged: K4 only.

### K4-038
- Citation: Song, J. H., López de Prado, M., Simon, H., Wu, K. (2015). "Intraday Patterns in Natural Gas Futures: Extracting Signals from High-Frequency Trading Data." SSRN 2657224 (LBNL working paper).
- Retrieval: abstract only, via the Wayback copy of the SSRN page (curl): http://web.archive.org/web/20251107012444/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2657224. Failed routes: SSRN PDF (bot wall; WebSearch listed Delivery link SSRN_ID2742734), OSTI API (non-JSON response), Semantic Scholar API (HTTP 429).
- Mechanism: Fourier analysis of NG trade timing shows rising high-frequency (algorithmic) activity and a spike in trading in the first second of every minute (TWAP execution). Seasonally split temperature forecasts are cointegrated with NG prices, and temperature-forecast variation accounts for a large share of daily price fluctuation.
- Products and horizon: NG futures; trade-level timing; daily temperature-forecast link.
- Verified passages:
  - P-K4-038-a (Abstract): "significant amount of trading activities occur in the first second of every minute, which is a telltale sign of the Time-Weighted Average Price (TWAP) execution algorithms."
  - P-K4-038-b (Abstract): "After separating the data according to seasons, the temperature forecast is strongly cointegrated with natural gas price. ... the variations in temperature forecasts contribute to a significant percentage of the average daily price fluctuations".
- Numeric claims: none quantified in the abstract.
- Tags: new to the program (weather-forecast updates as NG drivers; the TWAP clock is a microstructure fact). Intraday-feasible: the weather-forecast mechanism is feasible only if forecast-model update times fall inside the session and are observable [unverified]. The first-second-of-minute TWAP effect is a seconds-scale feature and not tradeable under the no-HFT rule.
- Clusters tagged: K4 only.

### K4-040
- Citation: Chan, K. F., Gray, P. K. (2017). "Do Scheduled Macroeconomic Announcements Influence Energy Price Jumps?" Journal of Futures Markets 37(1), 71-89. DOI 10.1002/fut.21796.
- Retrieval: abstract only, via IDEAS (curl): https://ideas.repec.org/a/wly/jfutmk/v37y2017i1p71-89.html. Failed routes: Wiley (paywall), Unpaywall (not OA), no WP found in OpenAlex.
- Mechanism (a null): across six energy futures, scheduled US macro releases do not raise jump arrival rates, and surprise size and sign do not affect mean jump size.
- Products and horizon: six energy futures (the list is [unverified]; likely including CL, HO, RB and NG); intraday jump tests.
- Verified passages:
  - P-K4-040-a (Abstract): "We find little evidence of an increase in jump arrival rates coinciding with scheduled releases of economic data. Similarly, there is no compelling evidence that the magnitude and/or sign ("good" vs. "bad") of the inherent announcement surprises influence the mean jump size."
- Numeric claims: none.
- Tags: port of D.1 family E (macro releases), energy products; a null. Intraday-feasible: n/a (evidence against macro-release jump rules on energy).
- Clusters tagged: K4 only.

### K4-041
- Citation: Chatrath, A., Miao, H., Ramchander, S. (2012). "Does the price of crude oil respond to macroeconomic news?" Journal of Futures Markets 32(6), 536-559. DOI 10.1002/fut.20525.
- Retrieval: abstract only. IDEAS has no abstract ("No abstract is available for this item"), so the abstract text comes from the OpenAlex API record (publisher-deposited abstract, reconstructed from OpenAlex's inverted index); it is not a page scrape. Failed routes: Wiley (paywall), Unpaywall (not OA).
- Mechanism (mostly a null): with daily and intraday data and inventory controls, crude's response to US macro news is limited, and inventory levels play little role in it. This supports flow-based pricing.
- Products and horizon: CL; daily and intraday windows ([unverified] detail).
- Verified passages:
  - P-K4-041-a (Abstract, OpenAlex record): "Using daily and intraday price data and proxies for inventory levels, we reexamine the responsiveness of crude prices to macroeconomic news. Our evidence suggests a very limited role for stock levels in the responsiveness of crude oil. The prior conclusion that crude oil is priced primarily in a flow‐environment is supported by our data."
  - P-K4-041-b (Chan & Gray 2017 abstract, K4-040, describing this paper): "Chatrath, Miao, and Ramchander [(2012) ...] find little evidence of an announcement‐price reaction in mean energy returns". This is a secondary characterization.
- Numeric claims: none.
- Tags: port of D.1 family E (macro releases), CL; mostly null. Intraday-feasible: n/a.
- Clusters tagged: K4 only.

### K4-042
- Citation: Baviera, R., Santagostino Baldi, T. (2017). "Stop-loss and Leverage in optimal Statistical Arbitrage with an application to Energy market." arXiv:1706.07021 [q-fin.PM]. (The registry line K4-042 has a wrong placeholder author, "Lipton?"; the correct authors are Baviera and Santagostino Baldi as read from the PDF. The registry is append-only, so it is corrected here.)
- Retrieval: full text. URL read: https://arxiv.org/pdf/1706.07021 (curl, pdftotext).
- Mechanism: an Ornstein-Uhlenbeck mean-reversion band strategy with stop-loss and leverage, applied to the spread between the 2nd HO contract and the 6th ICE Gasoil contract on half-hour prices. Bands are calibrated in-sample (9 months) and tested out-of-sample (3 months).
- Products and horizon: HO (2nd contract) against ICE Gasoil (6th contract); half-hour bars; holding periods follow the first-exit times of the OU band (not stated as intraday-only; positions can span the round-the-clock session).
- Cost assumptions: proportional cost c in spread-sigma units, with a maximum admissible c* = 0.76. The empirical returns are shown for the calibrated bands; the exact cost used in Table 2 is [unverified].
- Data window: 23 Apr 2015 to 22 Apr 2016 (one year), Thomson Reuters.
- Quality tells: one year of data and one pair, and a 3-month OS window. The pair was chosen from Cummins and Bucca (2012) (K4-019). The optimal leverage (28.54) is "too large for practical purposes". This is a methods paper with an illustrative application.
- Verified passages:
  - P-K4-042-a (Sec. 4): "the spread between the second future contract of Heating Oil and the sixth future contract of Gas Oil (generally identified as HOc2-LGOc6)" and "we consider a half-an-hour dataset for one year between the 23.04.2015 and the 22.04.2016."
  - P-K4-042-b (Table 2): "f d CI u CI µ CI µOS / 1 −0.870 ... 0.145 (0.124, 0.151) 0.410 / 10 ... 1.175 (1.049, 1.367) 4.340" (long-run return µ in-sample, µOS out-of-sample, units per the paper's definition).
  - P-K4-042-c (Sec. 5): "Optimal leverage is too large for practical purposes, but Out-the-Sample results show that the proposed trading strategy provides significant long-run returns even considering a suboptimal leverage."
- Numeric claims: in-sample µ 0.145 and OS µ 0.410 at leverage 1 (P-K4-042-b; the units are the paper's long-run return per unit time, not an annual percentage [unverified]).
- Tags: port of D.1 family C (mean reversion) applied to an intra-energy spread. Intraday-feasible: no as designed. The Gasoil leg is ICE (not tradeable on TopstepX), and OU band exits are not bounded by a daily flat time. Only a single-leg HO rule conditioned on the spread would be possible, and that is untested.
- Clusters tagged: K4 only (Gasoil is a non-CME instrument for HO).

### K4-043 (panel source: CL [K4], ZN [K2], ES [K1 leg; D.1 territory])
- Citation: Fett, N., McPhail, L. (2017). "Stop Orders in Select Futures Markets." CFTC OCE Staff Papers and Reports No. 2017-009, August 2017.
- Retrieval: full text. URL read: https://www.cftc.gov/sites/default/files/Stoploss_final_ada.pdf (curl, pdftotext).
- Mechanism: descriptive audit-trail study of stop orders in ES, ZN and CL. Stop-order executions are correlated with intraday volatility. Stop orders are invisible until triggered, and some participants use them for latency reduction rather than hedging. CL has the highest stop-order share of volume. There is no return or predictability claim.
- Products and horizon: CL [K4], ZN [K2], ES (MES exposure, D.1); intraday.
- Cost assumptions: none.
- Data window: full audit trail 2014 to 2016, plus sampled dates (first Tuesday and Thursday of each month).
- Quality tells: regulator descriptive study on non-public data, with no strategy. It is relevant as a microstructure fact behind D.1 family B (stop cascades through reference levels), not as a tested mechanism.
- Verified passages:
  - P-K4-043-a (Abstract): "As expected, trades involving stop orders are found to be highly correlated with intraday price volatility. Existence of stop orders is generally unknown to market participants as stop orders are not visible in the orderbook but must be triggered by a trade in the market at the corresponding price. More importantly, our analysis indicates that many traders are not only using stop orders for hedging purposes but also using them for latency reduction strategies."
  - P-K4-043-b [K4] (Sec. 4): "Stop orders are most frequently used by market participants in the WTI crude oil futures, followed by E-mini S&P 500 futures, and then followed by 10 Year US Treasury Note futures. Specifcally, for WTI crude oil futures, total trade volume from 2014 to 2016 was 607.6 million, of which 2% of volume (13.6 million contracts) was transacted using stop orders."
  - P-K4-043-c [K2] (Sec. 4): "For 10 Year US Treasury Note futures, total trade volume was 1.8 billion, of which 0.3% of trades (about 5.4 million contracts) were placed using stop orders."
  - P-K4-043-d (Sec. 2): "Protection points for WTI crude oil futures is $0.5 (50 ticks)".
- Numeric claims: CL stop share 2% of 2014-2016 volume (P-K4-043-b); ZN 0.3% (P-K4-043-c).
- Tags: port of D.1 family B (reference-level breakout; supporting microstructure fact), CL. Intraday-feasible: n/a (descriptive).
- Clusters tagged: K4, [K2] (P-K4-043-c), ES is the D.1/MES exposure (P-K4-043-a covers all three; the ES volume sentence is in P-K4-043-b's paragraph).

### K4-044
- Citation: Fishe, R. P. H., Haynes, R. W., Onur, E. (2019). "Anticipatory Traders and Trading Speed." Journal of Financial and Quantitative Analysis (DOI 10.1017/s0022109018000832; OpenAlex lists 2018 online). SSRN 2606949 (2015 WP, CFTC-affiliated authors). The registry line K4-044 lists the authors only generically; the names come from OpenAlex.
- Retrieval: abstract only, via the Wayback copy of the SSRN page (curl): http://web.archive.org/web/20250425184704/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2606949. Failed routes: SSRN PDF (bot wall), JFQA/Cambridge (paywall; Unpaywall not OA), two guessed CFTC OCE URLs (404).
- Mechanism: some CL traders, mostly not HFTs, trade ahead of local price trends identified in order-book data and act like informed traders. A follow-up sample shows attrition and difficulty sustaining these anticipatory strategies.
- Products and horizon: CL (WTI) order book; local (intraday) price trends, horizon [unverified].
- Verified passages:
  - P-K4-044-a (Abstract): "These anticipatory participants correctly trade prior to the overall market and systematically act before other participants. They use manual and algorithmic order entry methods, but most are not fast enough to be high frequency traders (HFTs). ... A follow-up sample shows significant attrition in accounts and difficulty maintaining the anticipatory strategies. To identify anticipatory traders, we devise novel methods to isolate local price trends using order book data from the WTI crude oil futures market."
- Numeric claims: none.
- Tags: port of D.1 family C (short-horizon momentum; account-level evidence that non-HFT trend anticipation exists in CL but is hard to sustain). Intraday-feasible: [unverified] (the trend horizon is not in the abstract); the method needs account and order-book data that the program does not have.
- Clusters tagged: K4 only.

### K4-046
- Citation: CME Group OpenMarkets (2025). "What API and EIA Data Reveal About Crude Oil Markets." https://www.cmegroup.com/openmarkets/energy/2025/What-API-and-EIA-Data-Reveal-About-Crude-Oil-Markets.html (no author named in the extracted text).
- Retrieval: full article, Wayback snapshot 21 Apr 2026, via curl (https://web.archive.org/web/2026/<url> resolved to 20260421170733) + BeautifulSoup. cmegroup.com itself refuses this machine.
- Mechanism (practitioner claim, untested): the API report (Tuesday evening) is a quicker, voluntary-survey preview of the EIA report (Wednesday). Traders use it to anticipate the EIA, and large API/EIA discrepancies cause sharp price adjustments.
- Products and horizon: CL; Tuesday evening to Wednesday 09:30 CT.
- Cost assumptions / data window: none.
- Quality tells: exchange marketing (it promotes WTI Weekly options). The "correlation coefficient of 0.6-0.8" is unsourced ("analysts often observe"). There is no data or test. Discovery value only; the tested version of this mechanism is K4-009 (abstract only) and K4-023.
- Verified passages:
  - P-K4-046-a: "Traders often use the API report to anticipate the EIA report, but large discrepancies can lead to sharp price adjustments. It's important to note that the API report should not be taken as a definitive guide to EIA data, especially for exact inventory changes and trade placement."
  - P-K4-046-b: "Statistically, while the correlation between API and EIA reports can vary, analysts often observe a correlation coefficient of 0.6-0.8, indicating a moderate to strong positive relationship but not perfect alignment."
- Numeric claims: API/EIA correlation 0.6-0.8 (P-K4-046-b), unsourced by the article itself and therefore [unverified] as a fact.
- Tags: new to the program (API-to-EIA sequential information; same mechanism as K4-009). Intraday-feasible: yes (read API after the flat time, act Wednesday before or after 09:30 CT).
- Clusters tagged: K4 only.

### K4-047 (market-structure documentation; not a finding)
- Citation: CME Group, "Energy Trading at Marker – Frequently Asked Questions." https://www.cmegroup.com/education/articles-and-reports/energy-trading-at-marker-frequently-asked-questions.html
- Retrieval: full page, Wayback snapshot 5 Oct 2022 (20221005175230) via curl + BeautifulSoup. The page may have changed since then, and current TAM availability is [unverified].
- Content: CME runs Trading-at-Marker (TAM) contracts whose price is a one-minute VWAP at fixed clock times: London 16:29-16:30 London time (10:29-10:30 CT for most of the year) for CL, RB, HO; Singapore 16:29-16:30 SGT (about 03:29-03:30 CT) for CL. These are scheduled benchmark windows, analogous to the settlement window, where marker-linked flow concentrates. No source tests whether they carry a price effect.
- Verified passages:
  - P-K4-047-a: "For TAM Light Sweet Crude Oil, New York Harbor No. 2 Heating Oil and RBOB Gasoline futures, the marker price in the front month is the volume weighted average price (VWAP) of outright trades on CME Globex for the one-minute period from 4:29 – 4:30 p.m. London time, rounded to the nearest tradable tick."
  - P-K4-047-b: "For Singapore TAM in Light Sweet Crude Oil futures, the marker price in the front month is the volume weighted average price (VWAP) of outright trades on CME Globex for the one-minute period from 4:29 – 4:30 p.m. Singapore time".
  - P-K4-047-c: "TAM is a pricing mechanism analogous to Trading at Settlement (TAS) wherein parties are permitted to trade at a differential that represents a not-yet-known price."
- Tags: documentation. It is a candidate event time (London marker at about 10:30 CT) for a session-clock test, D.1 family A. Intraday-feasible: the London marker falls inside the XFA day. No evidence of any effect was found.
- Clusters tagged: K4.

### K4-048 (blocked)
- Citation: Wong, P. (2022). "Predicting Intraday Crude Oil Returns with Higher Order Risk-Neutral Moments." SSRN 4019829.
- Retrieval: blocked; title only. Failed routes: SSRN page (bot wall; no Wayback snapshot), OpenAlex (no abstract), SSRN PDF (bot wall). WebSearch did return a search-model summary (option-implied semi-moments "explain and predict returns in crude oil futures at high frequency"), but by rule it is not retrieved text and is not used.
- Why it passed pre-filter (title): intraday CL return prediction from option-implied moments.
- Mechanism, data, costs, numbers: [unverified] (nothing retrieved).
- Tags: new to the program (options-implied signal for CL), provisional. Intraday-feasible: [unverified]; it would need CL options data.

### K4-049 (blocked)
- Citation: Ewald, C.-O., Zhang, S. (2026). "High-frequency Dynamics of Crude Oil Futures Forward Premia: The Roles of Intraday Liquidity and Volatility." SSRN 7225178.
- Retrieval: blocked; title only (SSRN bot wall; no Wayback snapshot; OpenAlex no abstract). The WebSearch summary is not used.
- Why it passed pre-filter (title): intraday dynamics of the CL forward premium (a nearby-versus-deferred or spot relationship), conditioned on liquidity and volatility.
- Everything else: [unverified].

### K4-050 (blocked; possible panel source)
- Citation: Fetna, M. (2026). "Opening-Range Breakout Does Not Survive Trading Costs: A Pre-Registered 225-Cell Study on Sixteen Years of Futures Data." SSRN 7428398.
- Retrieval: blocked; title only (SSRN bot wall; no Wayback snapshot; OpenAlex no abstract).
- Why it passed pre-filter (title): a pre-registered, cost-aware test of D.1 family B (opening-range breakout) on futures. Whether energy futures are among the products is [unverified]. If it is a multi-cluster panel, it is registered here so it is not fetched twice, but no [K#] passages exist yet; other clusters should treat it as unread.
- Everything else: [unverified].

## 4. Flags for K8 (no full-text reads)

- JFM | Alquist, Ellwanger & Jin (2020), "The effect of oil price shocks on asset markets: Evidence from oil inventory news" (registry K4-008, claimed by the first reader, not read) | legs: WPSR-identified oil shock (K4) and equities, Treasuries, FX (K1, K2, K3) | oil inventory news as an instrument for cross-asset responses. Open copy: Bank of Canada SWP 2020-8.
- JFM | Alturki & Kurov (2022), "Market inefficiencies surrounding energy announcements" (K4-009) | legs: CL (K4) and the stock market (K1) | inventory-announcement inefficiency spans CL and stocks; the CL-only part is in section 3
- Quantpedia | "Crude Oil Predicts Equity Returns" | legs: crude (K4) and equity index (K1) | crude price as an equity timing signal
- Skidmore College WP / J. Commodity Markets (2024) | Basistha, Kurov & Wolfe, "Have the causal effects between equities, oil prices, and monetary policy changed over time?" | legs: oil (K4), equities (K1), monetary policy (K2) | time-varying causal links
- JFM | "Trading around the clock: Revisit volatility spillover between crude oil and equity markets in different trading sessions" (2023, fut.22410) | legs: WTI (K4) and G7 equity indices (K1) | session-specific volatility spillover
- NY Fed SR 598 | Rosa (2013) (K4-025) | legs: FOMC-driven USD (K3) and CL (K4) | the energy response to FOMC runs through the dollar; the USD/energy link is K8's
- J. Banking & Finance (2014) | "How does public information affect the frequency of trading in airline stocks?" | legs: crude futures returns (K4) and airline equities (non-CME, K1 side) | crude returns driving stock trading intensity
- JFM (2010) | "Volatility spillover effects and cross hedging in corn and crude oil futures" | legs: CL (K4) and ZC (K6) | ethanol-era volatility spillover
- J. Agricultural Economics (2025, agr.70089) | "Spillover Effects of Energy and Grain Futures Volatility" | legs: WTI (K4) and grains (K6) | volatility spillover
- SSRN | Chiang & Hughen, "Do Oil Futures Prices Predict Stock Returns?" | legs: CL (K4) and equities (K1) | oil futures as an equity predictor
- Quantpedia blog | "Financialization of crude oil market" (summarizing "Has Crude Oil Become a Financial Asset? Evidence from Ten Years of Financialization") | legs: VIX and S&P 500 (K1) and CL (K4) | financial variables explain crude return variance
- Quantocracy / Milton FMR | "Pairs Trading An Advanced Strategy: CAD – Crude Oil" | legs: 6C (K3) and CL (K4) | CAD-crude pairs
- arXiv 1209.0900 | "Time-Frequency Dynamics of Biofuels-Fuels-Food System" | legs: gasoline and crude (K4), corn, wheat, soybeans (K6) | wavelet co-movement, ethanol link

## 5. Registry ids owned by K4

- K4-001 to K4-020: claimed by the first reader (20:20-20:28 PDT); now owned by this log. Status per id: 001-007, 009, 010, 012, 014, 017, 018, 020 in section 3; 008 K8 flag; 011, 015, 016, 019 rejected; 013 see D.1 B4.
- K4-021 to K4-050: appended by this worker, 20:42-21:22 PDT (30 lines). 021-038 and 040-050 are in section 3 (045 is inside the K4-017/018/045 documentation block); 039 is rejected (R-K4-040).
- Panel sources claimed with passages for other clusters: K4-034 [K5][K6], K4-035 [K5][K6], K4-036 [K6], K4-043 [K2] (ES as the D.1/MES leg). K4-050 may be a multi-cluster panel but is blocked, with no [K#] passages; other clusters should treat it as unread.
