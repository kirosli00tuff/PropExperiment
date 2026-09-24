# Stage E.0 research log, cluster K7 (crypto: MBT; MET as signal leg only)

Worker: ClusterReader-K7-OpusHigh. COMPLETE.

## 0. Header

- Cluster: K7. Traded product: MBT (CME Micro Bitcoin). MET (CME Micro Ether) is out of the traded universe after the D1 liquidity floor (day-session coverage 0.947 < 0.95) and appears only as a signal leg.
- Start 21:26 PDT 2026-09-23; paused 21:58 to 01:10 PDT (usage limit, excluded from work time); resumed 01:12; end 01:20 PDT 2026-09-24. Work time about 40 minutes.
- Stop reason: container rule. Every one of the 11 containers had at least 4 distinct logged queries, and its last 2 queries produced no new passing item (container 9 had no crypto content at all). The 60-full-text cap was not reached (24 full-text reads).
- Counts: 43 registry claims (K7-001..K7-043). Passed items: 42 logged in section 3 (the 43rd claim, K7-035, was a stub page, counted as blocked). Full text read: 24 (K7-002, 004, 005, 011, 012, 015, 017, 019, 022, 023, 024, 025, 026, 032, 033, 034, 036, 037, 038, 039, 040, 041, 042, 043). Abstract only: 17 (K7-001, 003, 006, 007, 008, 010, 013, 014, 016, 018, 020, 021, 027, 028, 029, 030, 031). Blocked: 2 (K7-009 title only, no abstract anywhere; K7-035 stub). Rejected: 73 reject lines in section 2 (several lines group more than one title; titles-only pre-filter, no fetch). Items considered: 43 claimed + the titles in the 73 reject lines (not summed exactly because lines group titles). [unverified] markers in section 3: 44 bracketed tags.
- Seeds from the lead's memory: Baur and Dimpfl (K7-001, JFM 2019: verified, abstract only), Alexander and Heck (K7-002, JFS 2020: verified, full text), Eross et al. (K7-013, RIBAF 2019: verified, abstract only).
- Researched without WebSearch or Firecrawl (session budget exhausted). Discovery: Crossref REST, Semantic Scholar Graph API (rate-limited, 429 on most calls), arXiv API, OpenAlex (abstract reconstruction and OA locations), Unpaywall (placeholder address, no personal email), RePEc IDEAS (search returned no results), direct listings (CF Benchmarks, CFTC OCE, Databento blog and sitemap, Quantocracy), Wayback CDX (cmegroup.com, quantpedia.com, robotwealth.com, jonathankinlay.com, quantitativebrokers.com, qoppac.blogspot.com). Retrieval: curl + pdftotext / BeautifulSoup; Wayback for cmegroup.com, quantpedia.com, quantfiction.com. SSRN, Wiley, Sage and ScienceDirect blocked every full-text route tried (Cloudflare challenges, HTTP 403); the Elsevier article API returned metadata only. This is why 17 passed items are abstract only.
- Registry pre-check (21:26): no line in reports/stage_e0_source_registry.jsonl mentioned bitcoin, crypto, ether or K7; no `[K7]` tag in any other cluster's log; D.1's log has only pure-crypto rejects (B10-B16, B50, C13), none re-read. No panel source was claimed by K7; one possible panel (Howard 2026, eight CME futures, SSRN 7067778) was left unclaimed for the lead (R-K7-019); Fetna (2026) ORB panel is K4-050 (no crypto).
- Items the lead should see first (facts, not rankings): K7-036 (CME announced 24/7 crypto futures trading from 29 May 2026, pending regulatory review: ends the Sunday-reopen gap on later dates and may change MBT's session on TopstepX, unverified); K7-033 (MBT daily settlement = VWAP 14:59-15:00 CT; final settlement BRR 4:00 p.m. London on the last Friday); K7-038 (BRRNY 14:00-15:00 CT window is the benchmark of six of ten spot ETFs; more than 20% of BTC/MBT daily notional trades in that hour).
- Process notes: one arXiv response (ax4.xml) was saved to the repository root at 21:44 by a command that lacked a cd; the lead moved it to the scratch fetch directory. The K7-026 claim line was written with a placeholder author and corrected in place to "Pinchuk" at 21:45 (the only non-append edit to the registry; no other worker's line touched).

## 1. Containers and queries

| # | Container | Queries (engine: terms) | Start | Pre-filter done | Full text done | Passed (ids) | Notes |
|---|---|---|---|---|---|---|---|
| 1 | JFM and futures journals | q1 Crossref "bitcoin futures price discovery CME spot"; q2 Crossref "bitcoin futures basis expiration CME"; q3 Crossref "CME bitcoin futures intraday lead-lag high frequency"; q4 Crossref "Alexander Heck price discovery bitcoin unregulated markets"; q5 Crossref "ether futures CME ethereum futures price discovery"; q6 Crossref "micro bitcoin futures"; q7 Crossref "bitcoin futures settlement manipulation reference rate" | 21:26 | 21:34 | 21:34 | K7-001..009 | last 2 (q6, q7) no new pass. Seeds: Baur and Dimpfl (K7-001, abstract only) and Alexander and Heck (K7-002, full text) verified. |
| 2 | Weekend gap and time-of-day | q1 Crossref "bitcoin weekend effect CME gap futures"; q2 Crossref "intraday seasonality bitcoin returns time of day"; q3 Crossref "Eross intraday dynamics bitcoin"; q4 Crossref "bitcoin CME futures weekend gap Sunday open"; q5 Crossref "bitcoin day-of-the-week weekend returns anomaly"; q6 Crossref "bitcoin returns US trading hours overnight Asian European session"; q7 Crossref "bitcoin intraday return predictability hourly trading strategy"; q8 Crossref "cryptocurrency intraday momentum reversal futures"; q9 Crossref "bitcoin Monday weekend return reversal intraday"; q10 Crossref "bitcoin futures opening gap Sunday CME trading hours" | 21:34 | 21:39 | 21:39 | K7-010..018 | last 2 (q9, q10) no new pass. Eross seed verified (K7-013, abstract only). No academic study of the CME weekend gap itself was found; the venue source is K7-036 (container 8). |
| 3 | CME CF BRR / RTI and settlement window | q1 CF Benchmarks index page (direct listing) -> methodology PDF; q2 Crossref "CME CF Bitcoin Reference Rate"; q3 Crossref "bitcoin ETF net asset value 4 pm benchmark price pressure"; q4 Crossref "bitcoin futures final settlement expiration spot price manipulation evidence"; q5 Crossref "bitcoin benchmark fixing window London 4pm trading volume" | 21:39 | 21:41 | 21:41 | K7-019, K7-020 | last 2 (q4, q5) no new pass. |
| 4 | BIS, Fed, CFTC OCE, regulators | q1 BIS site search (236-byte stub) + Crossref "Bank for International Settlements bitcoin futures crypto derivatives market"; q2 Crossref "Finance and Economics Discussion Series cryptocurrency bitcoin trading"; q3 Crossref "Commodity Futures Trading Commission bitcoin futures market participants analysis"; q4 CFTC OCE Research Papers listing (static list; keyword filter is script-driven) | 21:41 | 21:43 | 21:43 | K7-021, K7-022 | last 2 (q3, q4) no new pass. |
| 5 | arXiv q-fin | q1 "all:bitcoin AND all:futures AND all:CME"; q2 "all:bitcoin AND all:intraday"; q3 "all:bitcoin AND (FOMC OR announcement OR CPI)"; q4 "all:bitcoin AND all:weekend" (0 results); q5 "all:bitcoin AND all:\"lead-lag\""; q6 "all:weekend AND all:cryptocurrency" (0); q7 "all:bitcoin AND all:seasonality" (none); q8 "all:ethereum AND all:bitcoin AND all:intraday" | 21:43 | 21:46 | 21:46 | K7-023..026 | last 5 no new pass. |
| 6 | SSRN via Crossref (prefix 10.2139) | q1 "CME bitcoin futures intraday trading"; q2 "bitcoin futures basis spot ETF arbitrage intraday"; q3 "bitcoin intraday momentum reversal futures CME trading hours"; q4 "ether bitcoin lead lag intraday"; q5 "bitcoin futures expiration last Friday settlement CME"; q6 "bitcoin macroeconomic announcement intraday CPI FOMC futures"; q7 "bitcoin opening range breakout intraday"; q8 "bitcoin volatility regime intraday trading rule realized volatility" | 21:47 | 21:49 | 21:49 | K7-027..030 | last 2 (q7, q8) no new pass. All SSRN passes are abstract only (SSRN blocked). |
| 7 | Macro announcements and bitcoin intraday | q1 Crossref "bitcoin jumps intraday volatility US macroeconomic announcements"; q2 Crossref "bitcoin CPI release intraday price reaction inflation surprise"; q3 Crossref "cryptocurrency FOMC announcement returns drift intraday"; q4 Crossref "bitcoin futures macroeconomic news jumps nonfarm payrolls"; q5 Semantic Scholar "bitcoin macroeconomic announcements intraday" (HTTP 429, failed); q6 Crossref "cryptocurrency reaction to US macroeconomic news high frequency returns"; q7 Crossref "monetary policy surprise bitcoin intraday event study" | 21:39 | 21:52 | 21:52 | K7-031 (plus K7-023, 026, 029, 030 found via containers 5 and 6) | last 2 valid queries (q6, q7) no new pass. |
| 8 | CME Group research/education (Wayback) | q1 direct cmegroup.com (HTTP 403); q2 Wayback CDX rulebook/CME/VII (no ch. 350); q3 Wayback CDX prefixes education/, insights/, openmarkets/ (crypto URLs filtered); q4 liquidity-report page (stub); q5 Wayback CDX prefix articles/; q6 Wayback CDX prefix trading/cryptocurrency-indices/; q7 articles/faqs crypto FAQs (facts duplicate K7-033/037) | 21:52 | 01:14 | 01:14 | K7-032..034, K7-036..038 (K7-035 stub, blocked) | pause 21:58-01:10 inside this container (not work). Last 2 (q6, q7) no new pass. |
| 9 | Databento blog | q1 blog index; q2 category pages learning/engineering/announcements; q3 search parameter crypto, bitcoin; q4 marketing sitemap (182 blog URLs filtered) | 01:14 | 01:15 | 01:15 | none | no crypto post exists; container exhausted. |
| 10 | Quantpedia (Wayback) | q1 Wayback availability for the expiry article (read at 21:30 as K7-004); q2 Wayback CDX quantpedia.com (20,599 URLs, crypto/seasonality filtered); q3 intraday/overnight anomalies article; q4 overnight sessions article; q5 pre-holiday drift article; q6 strategy page intraday-seasonality-in-bitcoin (source paper = K7-039); q7 strategy-tags/cryptocurrencies (view-limited) | 21:30 / 01:15 | 01:16 | 01:17 | K7-004, K7-039..041 | last 2 (q6, q7) no new pass. Each strategy followed to its primary: Padysak and Vojtko SSRN (same source as K7-039, SSRN blocked); Blasco et al. (K7-005) from K7-004. |
| 11 | Practitioner blogs (discovery only) | q1 Wayback CDX robotwealth.com; q2 Wayback CDX jonathankinlay.com, quantitativebrokers.com, qoppac.blogspot.com; q3 Kinlay category bitcoin-futures; q4 Quantocracy "bitcoin futures"; q5 Quantocracy "bitcoin intraday"; q6 Quantocracy "bitcoin weekend" (none); q7 Quantocracy "crypto seasonality"; q8 Quantocracy "cme bitcoin"; q9 Quantocracy "bitcoin settlement" (none) | 01:17 | 01:19 | 01:19 | K7-042 (Concretum, primary research post), K7-043 (Quant Fiction) | last 2 (q8, q9) no new pass. |

## 2. Rejected items

- R-K7-001 | C1 Crossref q1 | Kapar and Olmo (2019), An analysis of price discovery between Bitcoin futures and spot markets, Economics Letters, 10.1016/j.econlet.2018.10.031 | abstract: Dec 2017 to May 2018 window, horizon not stated as intraday, and the basis predicts SPOT returns "but not on the futures price", so the traded leg carries no signal.
- R-K7-002 | C1 Crossref q1 | Gokhale (2018), CME Bitcoin Futures Market: Challenges in Bitcoin Price Discovery, International Business Review (Korea), 10.21739/ibr.2018.09.22.3.161 | title/venue: descriptive policy piece, no abstract, no testable intraday mechanism apparent.
- R-K7-003 | C1 Crossref q1 | Apostolakis (2023), Examining Bitcoin Price Volatility Transmission between Spot and Futures Markets, SSRN 4390742 | volatility spillover, no directional intraday mechanism in title; no abstract.
- R-K7-004 | C1 Crossref q1 | Thaneeyatammakun (2025), Speculative efficiency and news-driven short-run price adjustment between bitcoin futures and spot markets, Chula thesis 10.58837/chula.is.2025.270 | abstract: futures including unregulated and ether, daily-to-weekly speculative-efficiency tests, student thesis; no CME intraday mechanism stated.
- R-K7-005 | C1 Crossref q1 | Pan et al. (2023), The Impact of Bitcoin Futures Introduction on Spot Price Crash Risk, SSRN 4349886 | one-off event study of futures listing; not a repeatable intraday mechanism.
- R-K7-006 | C1 Crossref q1 | Christopher (2025), Price Discovery Mechanisms in Spot vs. Futures Crypto Markets, SSRN 5517725 | no abstract; generic title with no CME angle stated.
- R-K7-007 | C1 Crossref q1 | Karkkainen (2018; Routledge chapter 2021), Price discovery in the Bitcoin futures and cash markets, 10.2139/ssrn.3243969 | abstract: CBOE (not CME) mid-quotes, futures lead; duplicates K7-001/003/006 question on a delisted contract; not claimed.
- R-K7-008 | C1 Crossref q1 | Choi et al. (2019), Price Discovery in Bitcoin Futures: Evidence From BitMEX, SSRN 3353583 | BitMEX, no CME angle.
- R-K7-009 | C1 Crossref q1 | Kose et al. (2024), The Bitcoin price and Bitcoin price uncertainty, JFM 10.1002/fut.22487 | abstract: VIX, dollar index, gold, oil drivers of the bitcoin price: cross-cluster, flagged to K8 (see section 4); horizon not intraday.
- R-K7-010 | C1 Crossref q1 | Ozdemir (2021), Causality Relationship between Spot and Futures Bitcoin Prices in CME, 10.51410/jcgirm.8.2.11 | abstract: causality between spot and CME futures prices, daily data implied, hedging framing; no intraday horizon stated.
- R-K7-011 | C1 Crossref q2 | Zhou (2023), Checking the Box on the Efficiency of CME Bitcoin Futures Options, J. Investing | options efficiency, not futures intraday.
- R-K7-012 | C1 Crossref q2 | Grover (2023), Returns Correspondence Between Bitcoin Futures & Bitcoin, SSRN 4619679 | abstract: futures-ETF tracking of bitcoin returns, not a trading mechanism.
- R-K7-013 | C1 Crossref q2 | Shynkevich (2020), Impact of bitcoin futures on the informational efficiency of bitcoin spot market, JFM 10.1002/fut.22164 | abstract: trend-chasing rules on SPOT lose their predictive power after the December 2017 futures listing (negative evidence for family C on bitcoin spot; horizon not stated as intraday); nothing to port to MBT.
- R-K7-014 | C1 Crossref q2 | Kachnowski (2022), Futures As Prelude: Bitcoin Price Forecasting From Perpetual Futures Data, SSRN 4097789 | perpetual swaps leading spot at tens of minutes; no CME angle and no transfer argument in the abstract (K7-002 already covers offshore-derivatives-lead-CME with CME data).
- R-K7-015 | C1 Crossref q2 | Liu (2021) Hedging Bitcoin with Futures; Bragin (2016) Inverse Futures; Ryznar (2018) The Future of Bitcoin Futures | hedging, product design, regulation: no intraday mechanism.
- R-K7-016 | C1 Crossref q3 | Shi (2018), The Impact of Futures Trading on Intraday Spot Volatility and Liquidity: Evidence from Bitcoin Market, SSRN 3094647 | one-off listing event study.
- R-K7-017 | C1 Crossref q4 | Alexander and Heck, BitMEX bitcoin derivatives: price discovery, informational efficiency, and hedging effectiveness, JFM 10.1002/fut.22050; Alexander et al. (2022) Price Discovery in Bitcoin: The Role of Limit Orders (Coinbase only) | no CME angle; the CME-relevant result is in K7-002.
- R-K7-018 | C1 Crossref q4 | Pagnottoni et al. (2018), Price Discovery on Bitcoin Markets, SSRN 3280261 | spot exchanges only.
- R-K7-019 | C1 Crossref q5 (ether futures) | Nie (2019) Eurodollar HF price discovery; Aggarwal and Thomas (2018) single-stock futures; Boyd and Locke (2013) natural gas options; Howard (2026) Matching Algorithm Design and Short-Horizon Price Predictability in CME Futures, SSRN 7067778 | off-cluster. Howard is a possible PANEL source (eight CME futures, MBO order-book data, 2025); its instrument list is not in the abstract and the full text is on SSRN (blocked), so it was NOT claimed; abstract says "0/46 cells profit at retail costs"; seconds-horizon order-book mechanism conflicts with Topstep's high-rate prohibition. Left for the lead to route.
- R-K7-020 | C1 Crossref q6 (micro bitcoin futures) | Chen et al. (2024), Market Impact of the Bitcoin ETF Introduction on Bitcoin Futures, SSRN 4767336; Rouxelin et al. (2024), Are Bitcoin Futures Options a Cheaper Way to Play the Bitcoin Lottery?, SSRN 4737260 | one-off event study; options pricing. No new passing item from this query.
- R-K7-021 | C1 Crossref q7 (settlement manipulation reference rate) | Wang (2026), Does a TWAP Deter Settlement Manipulation? Polymarket five-minute bitcoin markets, SSRN 7445139; Pirrong (2023) TAS manipulation (generic); Kumar and Seppi (1992) (generic); CSI 300 settlement-window papers | Polymarket has no CME angle; the others are not bitcoin-specific. No new passing item.
- R-K7-022 | C2 Crossref q1 (weekend CME gap) | Singal and Tayal (2019), Risky short positions and investor sentiment: Evidence from the weekend effect in futures markets, JFM 10.1002/fut.22069 | multi-futures weekend effect with no bitcoin (2019 sample); generic family E and partly sentiment; not K7's to claim. Other hits repeated C1 items. No bitcoin-specific weekend-gap study surfaced.
- R-K7-023 | C2 Crossref q2 (intraday seasonality) | Kuerzinger et al. (2024), The Influence of Intraday Sentiment on Bitcoin Returns, SSRN 4853867 | sentiment, shelved.
- R-K7-024 | C2 Crossref q2 | Espel (2025), Impact of US Bitcoin ETF Introduction on BTC and ETH Intraday Regime Seasonality, SSRN 4779488 | abstract: volume/volatility seasonality over two months either side of the ETF launch; no return mechanism; four-month window.
- R-K7-025 | C2 Crossref q2 | Memon et al. (2026), Extreme Perpetual Futures Funding and Subsequent Bitcoin Returns: Intraday Evidence from Binance | Binance perpetual funding, no CME angle, no transfer argument (MBT has no funding rate).
- R-K7-026 | C2 Crossref q3 | Su et al. (2022), The intraday dynamics and intraday price discovery of bitcoin, RIBAF 10.1016/j.ribaf.2022.101625 | UNRESOLVED: title only; no abstract in Crossref, OpenAlex, Semantic Scholar or the Elsevier API; closed. Not passed because the pre-filter cannot see whether CME is in the sample; the lead may treat it as an open lead.
- R-K7-027 | C2 Crossref q3 | Koy (2024), Intraday regime switching volatility dynamics of bitcoin liquidity, Multidisciplinary Business Review | liquidity-regime volatility model, no directional or CME angle.
- R-K7-028 | C2 Crossref q4 | Shanaev et al. (2026), The Election Anomaly in Bitcoin Returns, SSRN 6823239 | daily returns on G20 election days; rare events, daily horizon. Evci (2020, Turkish) and Demirhan et al. (2026) day-of-week effects: daily returns, no intraday construction.
- R-K7-029 | C2 Crossref q6 (US hours / overnight) | all hits equity or Chinese markets (Huang 2026 extended-hours broker orders; Chen 2026 A-share overnight; Lim 2026 Blue Ocean ATS; Riedel 2014) | off-cluster; no new K7 passing item from this query.
- R-K7-030 | C2 Crossref q7 | Novinsalari et al. (2025), Return Predictability in Bitcoin ETFs: A Machine Learning Approach, SSRN 5614913; Sanhueza et al. (2025), A Comprehensive Look at Bitcoin Return Predictability, SSRN 5660581 | no abstract reachable (Crossref, OpenAlex); ETF equity product / horizon unknown; not passed. Ma et al. (2022) SHFE metals night trading and Wen et al. (2021) INE crude: other clusters' non-CME products (K5, K4), not K7's.
- R-K7-031 | C2 Crossref q8 | Dobrynskaya (2021, 2023) cryptocurrency momentum and reversal (cross-sectional, 1 week to 2 years); Yang (2018); Ficura et al. (2023) weekly reversal in small coins | cross-sectional altcoin sorts at weekly or longer horizons; not intraday, no CME angle. Rosa (2022), Understanding intraday momentum strategies, JFM 10.1002/fut.22375 | generic D.1 family A/C on other markets (rule 6: not K7's to read).
- R-K7-032 | C2 Crossref q9 | Mourey et al. (2025), A Crypto-Stock Weekend Effect: Predicting Monday Stock Returns Using Weekend Cryptocurrency Returns, SSRN 5382090 | crypto signal for equities: flagged to K8. Indonesian/Korean weekend-effect equity papers off-cluster. No new K7 passing item.
- R-K7-033 | C2 Crossref q10 | Baur and Smales (2022), Trading behavior in bitcoin futures: Following the "smart money", JFM 10.1002/fut.22332 | abstract: CFTC Commitments of Traders positioning in CME bitcoin futures, weekly data; strategies follow leveraged-money position changes over subsequent weeks; not intraday (at most a weekly regime input). Yuan (2020) The CME Vulnerability (book); Deng et al. (2019) inverse futures (BitMEX-type); Alam (2017) opinion piece. No new K7 passing item.
- R-K7-034 | C7 Crossref q1 (macro announcements, jumps) | "Volatility Clustering and Market Sentiment: ... Bitcoin and Ethereum's Reaction to Macroeconomic Announcements" (2025), American Journal of Management and Economics Innovations 10.37547/tajmei/volume07issue07-07 | GARCH daily-style volatility study in a low-tell venue with a sentiment framing; no intraday return mechanism in the abstract. Evans (2011), Huang (2015/2018), Chan and Gray (2018), Naveen (2026) SPY/QQQ, Lee (2019) KOSPI: not bitcoin.
- R-K7-035 | C3 Crossref q1 (CME CF BRR) | Gajo (2025), CME Group fuehrt Bitcoin-Volatilitaetsindizes ein, Die Aktiengesellschaft | news item on a volatility index launch; no mechanism. Other hits off-topic (medical "CME", Venezuela/Lebanon parallel exchange rates, Ordinals). The BRR methodology itself was retrieved from CF Benchmarks' page (K7-019).
- R-K7-036 | C3 Crossref q2 | Guliyev et al. (2025), From Flows to Value: Cointegration Between Bitcoin Spot ETF Assets and Bitcoin Price, Ledger | daily cointegration, not intraday. Kia, Song and Xu (2024), Price Discovery in Bitcoin ETF Market, SSRN 4776832 / 5046810 | UNRESOLVED: no abstract reachable (Crossref, SSRN blocked); title suggests ETF-vs-spot/futures price discovery; left open for the lead. Chang, Tai and Lin (2026) Taiwanese ETFs: off-cluster.
- R-K7-037 | C3 Crossref q3 | TAIEX expiration manipulation papers (Chung et al. 2023; Chang et al. 2022) | K1-type non-CME products, not K7. No new K7 passing item.
- R-K7-038 | C3 Crossref q4 | Evans et al. (2018) Fixing the Fix; Husselmann and van Vuuren (2019) trend-following at the 4pm BFIX/WMR windows; Melvin and Prins; Colla et al. (2024) London 4pm Fix manipulation | FX fixing (K3's region), not bitcoin; the BRR window analogue is logged as K7-019. Dickerson (2018) Wikipedia/Google search volume: sentiment, shelved. Aalborg et al. (2018): daily drivers including VIX, flagged to K8 as part of the crypto-vs-equity-volatility family. No new K7 passing item.
- R-K7-039 | C4 Crossref q1 (BIS) | Acet (2019) bitcoin market in Turkey; Hong (2022) The Effects of Bitcoin Futures on Bitcoin Market (BCP review); Dallas Fed GWP 381 (2020) Cryptocurrency Market Reactions to Regulatory News | descriptive or unscheduled regulatory news (not a scheduled release; daily event study); no CME intraday mechanism. BIS search page (bis.org/cgi-bin/search.pl) returned a 236-byte stub; the BIS cryptoassets topic page loaded but was not mined further for lack of a paper with a CME intraday angle in its titles [not exhaustively checked].
- R-K7-040 | C4 Crossref q2 (FEDS) | Badev and Chen (2014), Bitcoin: Technical Background and Data Analysis, FEDS 2014-104 | blockchain usage statistics, no trading mechanism. Takaishi (2026) rough volatility in trade counts: no directional mechanism.
- R-K7-041 | C4 Crossref q3 (CFTC) | encyclopedia entries on the CFTC; Peirce (2014) | no research content. No new K7 passing item.
- R-K7-042 | C4 CFTC OCE Research Papers listing (keyword filter "Bitcoin Futures"/"Micro Bitcoin Futures" exists but the page's filter is script-driven; the static list was read) | Ferko, Mixon and Onur (2024), Retail Traders in Futures Markets, OCE Staff Paper 2023-002 | abstract (page 1, read as lede only): overnight-position data, median 4 trades lasting 4 days, retail contrarian entry; multi-day holding behaviour, not an intraday mechanism. Fett and McPhail, Stop Orders in Select Futures Markets: see K4-043 (already claimed; not re-read). No new K7 passing item.
- R-K7-043 | C5 arXiv q1 (bitcoin futures CME) | "Causal effect of regulated Bitcoin futures on volatility and volume" (arXiv 2109.15052) | one-off listing event. "Implied ETF Carry Rates and the Limits of Arbitrage in Segmented Bitcoin Markets" (arXiv 2605.29309) | IBIT-options vs CME-futures carry, daily arbitrage bounds; not a one-legged intraday MBT rule (a CME-basis state at most). ByteGen (2508.02247): LOB generative model, no mechanism.
- R-K7-044 | C5 arXiv q2 (bitcoin intraday) | Twitter nowcasting (1406.7577): sentiment, shelved; Tether minting and "whale alerts" on Twitter (2501.05232): sentiment/social, shelved; FPCA interval forecasting (2505.20508): duplicate method of K7-017 with no trading test; Hurst/efficiency papers (1709.08090, 2306.13371), stationarity comparison (2408.02973), stylized facts (2402.11930, 2004.05870), effects of futures introduction on volatility (1906.03430): no tradable mechanism; LLT feature transform (2305.04884) and recurrent RL agent (2201.04699): ML engineering on spot without a CME angle; EMA walk-forward (2602.10785): generic method; Konczal and Poloczanski (2608.09576) European crypto ETP anomalies: Xetra/Stockholm ETPs, one-minute anomaly classification, no CME angle.
- R-K7-045 | C5 arXiv q3 (bitcoin FOMC/CPI) | Kalshi macro contracts forecasting crypto volatility (2604.01431) | daily realized-volatility forecasts from a prediction market; daily horizon; not a return mechanism (a D-family regime input at most). Monetary-policy-uncertainty MSM-VAR on monthly BTC (2311.10739): monthly. LLM multi-agent trading (2510.08068): no testable mechanism. MicroStrategy-bitcoin interactions (2505.14655): equity-crypto, flagged to K8. Network/protocol papers: off-topic.
- R-K7-046 | C5 arXiv q4-q8 (weekend; lead-lag; weekend+cryptocurrency; seasonality; ETH+BTC intraday) | "Cross Cryptocurrency Relationship Mining for Bitcoin Price Prediction" (2205.00974): ML price prediction from other coins, horizon not intraday in the abstract; "Cryptocurrency market structure: connecting emotions and economics" (1903.00472): sentiment, shelved; multiscale review (2010.15403): survey; loop-gain matrix for leveraged ETPs (2608.22768): stability monitoring, no bitcoin mechanism. Weekend and weekend+cryptocurrency queries returned 0 results; seasonality returned none; ETH+BTC intraday returned only items already logged. No new K7 passing item in the last five arXiv queries.
- R-K7-047 | C6 Crossref SSRN q1 (CME bitcoin futures intraday) | Zhang et al. (2020 SSRN; 2023 Pacific-Basin Finance Journal 10.1016/j.pacfin.2023.101950; 2022 FRL), futures trading activity and spot jump risk | futures-listing/activity effects on spot jump risk: structural, no tradable intraday rule in the titles; no abstract reachable. MaxAI (index futures, K1), NQ long-memory (K1), crude/corn/metals (K4/K6/K5, non-CME), Deng (2019) inverse futures (BitMEX-type): not K7.
- R-K7-048 | C6 Crossref SSRN q2 (basis / ETF arbitrage) | Krause (2024), The Ethereum Spot ETF Basis Trade Explained, SSRN 4879674 | ETH basis carry trade, multi-day, and ETH is not traded (MET out). Almubarak (2026) IBIT and volatility dynamics; Boulanouar (2026) ETF launch impact; Chen (2023) futures traders' reaction to ETF and hacking shocks (no abstract): event studies of one-off or unscheduled events. Krause (2026) Bitcoin Financialization and Market Correlation; Lee (2024) Shifting Dynamics: ETF approval and bitcoin's relationships with financial markets | crypto vs other asset classes: flagged to K8.
- R-K7-049 | C6 Crossref SSRN q3 (intraday momentum CME trading hours) | only items already logged (Wen K7-018, Ngene K7-007) plus other clusters' products (Chinese commodities, NQ, TOPIX, spot FX); Liu (2020) realized-semivariance momentum (generic). No new K7 passing item.
- R-K7-050 | C6 Crossref SSRN q4 (ether bitcoin lead-lag) | Nakagawa and Sakemoto (2022), Market Uncertainty and Correlation Between Bitcoin and Ether, SSRN 4076411 | no abstract reachable; correlation-regime study, horizon unknown; not passed. Wang (2023) hacks and BTC-ETH synchronicity: unscheduled events. Yang (2026) perpetual roughness and funding asymmetry (two papers): perpetuals, no CME angle. Shakourloo (2026) bitcoin and global macro variables: flagged to K8. Callens (2020): accounting. Schmidt (2024) generic lead-lag microstructure: not bitcoin.
- R-K7-051 | C6 Crossref SSRN q5 (expiration last Friday) | Ferko, Moin, Onur and Penick (2021), Who Trades Bitcoin Futures and Why?, SSRN 3959984 (CFTC data) | abstract: descriptive trader-type composition of CME BTC and MBT holders; no price mechanism. Joo (2023) hedging bitcoin with commodity futures: flagged to K8. Shao (2026) transaction-fee priority; Lim (2026) perpetual hidden liquidity; Khondoker (2022) currency hedging; Santaolalla (2024) CBDC: no K7 mechanism.
- R-K7-052 | C6 Crossref SSRN q6 / C7 | Ryabinin (2023), Gerchik (2026), Lin (2025), Lee (2023) FOMC premium and drift papers; Wafo Nomsi (2026) B3 DI, FX and index futures | not bitcoin (other clusters' or non-CME products). Dai (2026) NLP CPI nowcasting from Google Trends: sentiment/search, shelved.
- R-K7-053 | C6 Crossref SSRN q7 (opening range breakout) | Fetna (2026), Opening-Range Breakout Does Not Survive Trading Costs, SSRN 7428398 | see K4-050 (claimed by K4; abstract lists equity indices, metals, energy; no crypto), not re-read. QQQ/SPY/NSE/NAS100 ORB papers: other clusters or non-CME. Jia (2026) crypto-specific investor sentiment and range: sentiment, shelved. Kachnowski (2020) stochastic-volatility range forecasting: volatility model, no rule. No new K7 passing item.
- R-K7-054 | C6 Crossref SSRN q8 (volatility regime) | Liu (2026), Huang (2026), Djanga (2023), Manevich (2023), Ougou (2026) bitcoin realized-volatility forecasting; "Econometric Modelling and Algorithmic Trading of Bitcoin: ARIMA-GARCH" (2026, SSRN 6467818) | volatility forecasts without a return rule, or a low-tell single backtest; Mercik and Bedowska-Sojka SSRN 6401099 is an earlier version of K7-030 (one source). E-mini/MNQ/NQ regime papers: K1. No new K7 passing item.
- R-K7-055 | C7 Crossref q2 (CPI intraday bitcoin) | OECD CPI tables, Japan/India CPI notes; Ma et al. (2022) intraday price clustering in BTC-JPY, Financial Innovation | no bitcoin announcement mechanism; price clustering on a yen pair has no CME angle. Su et al. (2022): see R-K7-026. No new K7 passing item.
- R-K7-056 | C7 Crossref q3 (FOMC drift crypto) | Yang et al. (2026), Scheduled FOMC statements and intraday macro event risk in cryptocurrency markets, Finance Research Letters 10.1016/j.frl.2026.110073 | published version of K7-029 (one source). Lalwani et al. (2024), Predicting Intraday cryptocurrency returns - A Sparse Signals approach, SSRN 4748907 | 1-minute-ahead LASSO forecasts on minute data: holding horizon of one minute sits in Topstep's prohibited high-rate/seconds-duration zone and has no CME angle. Pre-FOMC drift papers (Lucca-Moench, Gilbert et al., Tsukioka, Ying, Baglioni), post-FOMC bond drift (Brooks et al.), FOMC minutes and equities (Jubinski): not bitcoin. No new K7 passing item.
- R-K7-057 | C7 Semantic Scholar q5 | query "bitcoin macroeconomic announcements intraday" returned HTTP 429 four times (rate limit); logged as a failed query, not as an empty one.
- R-K7-058 | C7 Crossref q6 | Corbet et al. (2018), The Volatility Generating Effects of Macroeconomic News on Cryptocurrency Returns, SSRN 3141986 | news-coverage counts and daily returns; not scheduled-release timing at an intraday horizon. Huynh (2025) sentiment and macro news: sentiment, shelved. Tzeng et al. (2025) monthly macro predictors; Ah Mand (2021/2025) uncertainty index wavelets; Katta (2024) websocket ML: not intraday-mechanism or no CME angle. No new K7 passing item.
- R-K7-059 | C7 Crossref q7 | Karau (2021 SSRN 3988527 / 3949549; 2023 JIMF 10.1016/j.jimonfin.2023.102880), Monetary policy and Bitcoin | abstract: weekly proxy VAR (high-frequency surprises only as instruments); weekly horizon, not intraday. Mehdian et al. (2025) intraday reaction to spot ETF approvals (one-off events); Krause (2025) Trump-era policy events (unscheduled); Marmora (2022) emerging-market monetary policy and bitcoin demand (daily); monetary-policy database papers (not bitcoin). No new K7 passing item.
- R-K7-060 | C8 direct cmegroup.com (contract specs, confluence) | HTTP 403 to curl; the MBT contract-specs page exists on Wayback (2026-04-11) but is script-rendered; the FAQ (K7-033) was read instead.
- R-K7-061 | C8 Wayback CDX, CME rulebook chapter 350/350A (Micro Bitcoin) | no snapshot of the chapter PDFs; rulebook facts taken from the FAQ (K7-033) [rulebook text unverified].
- R-K7-062 | C8 CME Bitcoin Futures Liquidity Report (claimed as K7-035) | the archived page is a stub linking to an external report ("View report"); no data or text to extract. Counted as blocked.
- R-K7-063 | C8 CME education/insights/openmarkets listings | Norland (2023) "Three factors driving the ether-bitcoin price nexus"; "Trading the ether-bitcoin correlation" (2023); "Relative value and momentum in ether-bitcoin pair" (2025); "Capitalizing on ether's positive momentum relative to bitcoin" (2025) | ETH/BTC relative value requires trading MET (out of the traded universe) and the pieces are macro/daily; not passed (a MET signal-leg idea at most). "Why is bitcoin moving in tandem with equities" (2025), "Why Bitcoin's relationship with equities has changed" (2025), "Is Bitcoin's digital gold narrative losing its shine" (2026): flagged to K8. Halving, mining revenue, election-rally, SOL/XRP/Cardano pieces, Glassnode reports: no intraday mechanism. "Bitcoin options volatility spikes and recovery signals" (2026): options-implied volatility regime at a daily horizon, not read. "What are your options for the upcoming bitcoin catalysts" (2023): event calendar commentary.
- R-K7-064 | C8 Wayback CDX cmegroup.com/trading/cryptocurrency-indices/ (q6) | index specification, historical-data and oversight pages for BRR/ETH RR | methodology duplicates of K7-019/K7-032; no new mechanism. C8 q7: CME articles/faqs crypto items (cryptocurrency futures FAQ, benchmarks FAQ, pricing-products FAQ, options FAQ) | contract/benchmark facts already captured in K7-033/K7-037; not read. No new K7 passing item in q6-q7.
- R-K7-065 | C9 Databento blog: q1 index page (https://databento.com/blog), q2 category pages learning/engineering/announcements, q3 blog search parameter "crypto" and "bitcoin" (no server-side search results), q4 marketing sitemap (182 blog URLs; none with crypto, bitcoin, BTC, ether, coin, weekend, settle or micro in the slug) | no crypto or CME crypto post exists; the only crypto mention is an external Forbes link inside a self-match-prevention post. Container exhausted.
- R-K7-066 | C10 Quantpedia (Wayback CDX listing, 20,599 captured URLs filtered) | "Are there any simple calendar effects in bitcoin market", "The day-of-the-week effect in the cryptocurrency market", "The seasonality of bitcoin": daily calendar effects (K7-015 and K7-039 cover the intraday versions); "Price overreactions in the cryptocurrency market", "Persistence in cryptocurrencies": daily horizons; "Trend-following and mean reversion in bitcoin" and "Revisiting ..." (Padysak and Vojtko): daily MAX/MIN rules with multi-day holds, a family B/H port that is infeasible (overnight holds); "Periodicity in cryptocurrencies: recurrent patterns in volatility and volume": appears to summarise the Watorek et al. line of work, see K7-023 [identity unverified, not read]; "How much are bitcoin returns driven by news", "Can Google Trends sentiment be useful", "Bitcoin returns resemble high-sentiment-beta stocks", "The attention factor": sentiment/attention, shelved; "Bitcoin returns and volatility predicted by exchange reserves": daily on-chain (K7-024 covers the intraday version); "Investigating price reaction around bitcoin/ethereum events" (halvings, upgrades): rare events; "Arbitrage opportunities in cryptocurrency markets", "Crypto covered interest parity deviations": cross-exchange/perpetual arbitrage with no CME leg; "Bitcoin is not the new gold", "Dual momentum gold vs bitcoin", "When crypto stopped diversifying", "Are cryptocurrencies exposed to traditional factor risks", "Trading the spread bitcoin ETFs vs crypto-infrastructure ETFs": cross-asset, flagged to K8 as one line; allocation, rebalancing-premium, skewness, pump-and-dump, wash-trading, Benford, Tether-manipulation, DCA and portfolio pieces: no intraday mechanism.
- R-K7-067 | C10 Quantpedia strategy page "intraday-seasonality-in-bitcoin" (q5) | names its source paper: Padysak and Vojtko, "Seasonality, Trend-following, and Mean reversion in Bitcoin" (SSRN) | same authors and analysis as K7-039 (one source); SSRN not readable. Quantpedia "strategy-tags/cryptocurrencies" (q6) | listing behind a free-view limit ("You've reached your limit for viewing up to 5 strategies for free"); no new item.
- R-K7-068 | C11 Robot Wealth (Wayback CDX listing) | crypto posts are about perpetual funding carry, cross-sectional altcoin momentum/reversal, Binance stat-arb features and members-only webinar updates ("intraday crypto seasonality" in the 1 March 2024 RW Pro update is members-only, no primary paper) | no CME angle or no reachable primary source; discovery only, nothing passed. Their GLD weekend-effect webinar: K5, not K7.
- R-K7-069 | C11 Kinlay (Wayback CDX; category "Bitcoin futures") | only "Trading Bitcoin" (2017) and "Hedged cryptocurrency strategies" (2021) | pre-CME-era commentary / hedged altcoin portfolios; not passed. Quantitative Brokers: no crypto URLs in the capture. Carver (qoppac): "Obligatory bitcoin post" (2017), "Skew preferences for crypto degens" (2024), "Bitcoin, money, gold" (2014): opinion pieces, no intraday mechanism.
- R-K7-070 | C11 Quantocracy search "bitcoin futures" (direct curl) | Factor Research "Quant Strategies in the Cryptocurrency Space" (cross-sectional factors, daily/weekly); Rulyfi "100 Million Bitcoin Backtests ... Deflated Sharpe" (method note on backtest overfitting, generic, not a mechanism); Unravel Markets "Can Miner Economics Predict Bitcoin Returns?" (miner fundamentals, daily or slower); Six Figure Investing quote pages (no content); Quantpedia items already logged (K7-004, K7-041). Concretum passed as K7-042.
- R-K7-071 | C11 Quantocracy "bitcoin intraday" (q5) | Quant at Risk (2020), intraday algo-trading model for cryptocurrencies using bitcoin-based signals | bitcoin as a signal for altcoins (altcoins not tradable here; no CME angle); Grzegorz Link "A Decade of Cryptocurrencies", Sanz Prophet data post, Ennlightenment pattern matching (2017): no mechanism or pre-CME. Other hits already logged (K7-039, K7-042; Quantpedia trend/mean-reversion in R-K7-066). No new pass. Quantocracy "bitcoin weekend" (q6): no results.
- R-K7-072 | C11 Quantocracy "crypto seasonality" (q7) | Unexpected Correlations "How Speculative Money Flows into Crypto", Quant Hedge "Should You Buy A New Crypto Listing?", Sepp "Optimal Allocation to Cryptocurrencies" | flows/listings/allocation, not intraday CME mechanisms. Quant Fiction passed on title (K7-043; month-of-year on reading). Financial Hacker "Deep Learning Systems for Bitcoins" (2017): pre-CME ML on spot.
- R-K7-073 | C11 Quantocracy "cme bitcoin" (q8) and "bitcoin settlement" (q9) | only the Financial Hacker post (see R-K7-072); no results for settlement. No new pass in the last two queries.

## 3. Passed items

### K7-001. Baur and Dimpfl (2019), Price discovery in bitcoin spot or futures?
- Citation: Dirk G. Baur and Thomas Dimpfl, Journal of Futures Markets 39(7) (2019) 803-817, doi 10.1002/fut.22004 (SSRN 3171464 working paper; one source). Seed from the lead's memory: verified (title, authors, journal).
- Retrieval: ABSTRACT ONLY. Routes failed: SSRN Delivery.cfm (HTML challenge by curl, HTTP 403 by WebFetch), Wayback copies of the SSRN PDF (HTML, not PDF), OpenAlex reports closed access, UWA repository page has no PDF link. Abstract read verbatim from Crossref (both the JFM and SSRN records).
- Mechanism (abstract only): Hasbrouck and Gonzalo-Granger information shares between CBOE/CME bitcoin futures and spot; spot leads futures, attributed to spot's volume and 24/7 hours.
- Products and horizon: CBOE and CME bitcoin futures vs spot; intraday frequency [unverified, not in abstract].
- Cost assumptions: [unverified]. Data window: [unverified] (starts no earlier than December 2017 per abstract).
- Quality tells: published JFM; early sample right after launch; later contested by Frino et al. (2025) and Alexander and Heck (2020) (see K7-002 introduction, which says CME "play a less important role than the three major spot exchanges, which is in line with the results of Baur and Dimpfl (2019)").
- Verbatim passages:
  - P-K7-001-a (abstract, Crossref record of 10.1002/fut.22004): "We rely on the information share methodology of Hasbrouck (1995 ...) and Gonzalo and Granger (1995 ...) and find that the spot price leads the futures price."
  - P-K7-001-b (abstract): "We attribute this result to the higher trading volume and the longer trading hours of the globally distributed bitcoin spot market, compared to the relatively restricted access to the US‐based futures markets."
- Numeric claims: none beyond the abstract; all information-share values [unverified].
- Tags: new to the program (spot leads MBT); intraday-feasible in principle (a lead-lag read at intraday frequency) [horizon unverified]; clusters tagged: K7.

### K7-002. Alexander and Heck (2020), Price discovery in Bitcoin: The impact of unregulated markets
- Citation: Carol Alexander and Daniel F. Heck, Journal of Financial Stability 50 (2020) 100776, doi 10.1016/j.jfs.2020.100776 (SSRN 3583843 is the working paper; one source). Seed from the lead's memory: verified (title, authors, journal correct).
- Retrieval: full text, author accepted manuscript dated July 24, 2020, https://ndownloader.figshare.com/files/41093948 (Sussex figshare record 23308262), pdftotext. Read: abstract, introduction, sections 3 to 6 on the passages cited.
- Mechanism: minute-level information shares and impulse responses; CME bitcoin futures are followers, not leaders: unregulated perpetuals and futures (Huobi, OKEx, BitMEX) and major spot exchanges lead, and CME futures take about 4 to 5 minutes to absorb a price shock on those venues. A transferable rule would read offshore/spot price moves and trade MBT's lagged adjustment.
- Products and horizon: CME bitcoin futures (BTC, full size; MBT did not exist yet), Bakkt futures, 10 spot exchanges, perpetual swaps; 1-minute; adjustment horizon 1 to 5 minutes.
- Cost assumptions: none (econometric; no trading-rule P&L).
- Data window: 1 April 2019 to 31 January 2020 (CME vs Bakkt from 1 October 2019); CME series rolled at midnight the day before expiration.
- Quality tells: published journal; multi-venue VECM/VAR; no out-of-sample trading test; pre-MBT and pre-spot-ETF window; CME-to-unregulated cointegration described as "quite weak" (footnote 38), so the VAR impulse responses rest on a model the authors concede decouples.
- Verbatim passages:
  - P-K7-002-a (abstract): "Prices on the regulated CME bitcoin futures and the US-based spot exchanges react to, rather than lead, price movements on the unregulated exchanges and they may do so relatively slowly."
  - P-K7-002-b (section 6, p. 29): "There is a strong immediate response of the CME futures to price shocks on all these unregulated products. All the spreads become almost constant from 4–5 minutes after the shock, implying that it takes the CME futures between 4 and 5 minutes to absorb and price the information content of price shocks on Huobi futures, BitMEX perpetual or Coinbase."
  - P-K7-002-c (section 4.3): "with shares between 25% and 36%, the OKEx futures clearly led price discovery ... Bitfinex (14%-21%), Coinbase (13%-18%), Bitstamp (14%-21%) and at last CME futures (3%-9%)."
  - P-K7-002-d (conclusion): "just four derivative contracts traded on Huobi, BitMEX and OKEx those products combined account for more than 60% of total price discovery in the bitcoin market – compared to only 5% from CME futures."
  - P-K7-002-e (section 4.2): "The CME interrupts trading over the weekend and between 4pm and 5pm Chicago Time on each working day"
  - P-K7-002-f (footnote 40): "CME futures expire monthly but the unregulated futures are quarterly contracts due in March 2020. This causes a saw-tooth pattern in the spread between CME and other instruments – as the monthly maturity approaches the CME futures price moves towards the spot prices and away from the unregulated futures prices."
- Numeric claims: CME adjustment 4 to 5 minutes (P-K7-002-b); CME GIS 3% to 9% (P-K7-002-c); unregulated four > 60% vs CME 5% (P-K7-002-d); window (section 3, "covers the period from 1 April 2019 to 31 January 2020", checked).
- Tags: new to the program (non-CME signal instrument leading MBT: spot/offshore lead-lag); intraday-feasible (minutes horizon, reads spot/offshore prices only) but the edge window of 1 to 5 minutes sits near Topstep's "average durations measured in seconds, not minutes" line and demands a live spot feed; clusters tagged: K7.

### K7-003. Frino, Gaudiosi, Webb and Zhou (2025), Price Discovery in Bitcoin Spot or Futures? The Jury Is Out
- Citation: Alex Frino, Ruggero Gaudiosi, Robert I. Webb, Zeyu I. Zhou, Journal of Futures Markets (2025), doi 10.1002/fut.22560.
- Retrieval: ABSTRACT ONLY. Routes failed: Wiley pdfdirect (Cloudflare "Just a moment..." challenge by curl; HTTP 403 by WebFetch), Wiley epdf (challenge), Wayback has no snapshot of the full or abstract page; Unpaywall and OpenAlex list only the Wiley copy (bronze). Abstract read verbatim from the Semantic Scholar record.
- Mechanism (abstract only): at 1-second sampling, regulated (CME) bitcoin futures generally lead spot, with daily variation in leadership; futures' share of price discovery rises around macroeconomic surprises.
- Products and horizon: regulated bitcoin futures (CME implied by "regulated") vs spot exchanges; 1-second sampling [contract list and exchanges unverified].
- Cost assumptions: [unverified]. Data window: [unverified].
- Quality tells: published JFM 2025; explicitly reconciles conflicting findings (K7-001 spot leads vs others futures lead) by measure, frequency, window, contract and exchange choice, which says the lead-lag direction is specification-sensitive.
- Verbatim passages:
  - P-K7-003-a (abstract): "We identify potential reasons behind these conflicting findings, including the choice of price discovery measures, sampling frequencies, modeling windows, futures contracts, and spot exchanges."
  - P-K7-003-b (abstract): "Using 1‐s sampling frequencies to accurately capture price discovery in the fast‐paced markets and accounting for substantial noise differences between spot and futures markets, we find that the futures market generally leads spot markets, though this price leadership exhibits daily fluctuations."
  - P-K7-003-c (abstract): "Moreover, we observe a pronounced increase in the futures market's contribution to price discovery around macroeconomic surprises and Tether stablecoin minting tweets."
- Numeric claims: none in the abstract; all information-share values [unverified].
- Tags: new to the program (CME-vs-spot lead-lag; announcement-conditional leadership also touches scheduled releases); intraday-feasible for the announcement angle (1-second measurement, but a rule would act on MBT itself); the "Tether minting tweets" part is social-media, shelved; clusters tagged: K7.

### K7-004. Quantpedia (Dujava; SSRN listing Vojtko et al.) (2024), Cryptocurrency Market Dynamics Around Bitcoin Futures Expiration Events
- Citation: Quantpedia blog article, author line "Cyril Dujava, Quant Analyst, Quantpedia"; SSRN 4779669 (Crossref lists first author Vojtko; the SSRN paper and the blog are treated as one source).
- Retrieval: full text of the blog version via Wayback, https://web.archive.org/web/20241113115621/https://quantpedia.com/cryptocurrency-market-dynamics-around-bitcoin-futures-expiration-events/ (direct quantpedia.com returned "Access Forbidden"). SSRN PDF not read (SSRN blocked). Charts and the performance table are images; their numbers were not readable.
- Mechanism: event study of daily spot BTC and BITO returns from d-3 to d+3 around CME monthly bitcoin futures expiry (last Friday); positive expiry-day spot return and negative day before in the full sample, with the pattern reversed after the October 2021 BITO launch.
- Products and horizon: BTC-USD spot (Yahoo/CoinMarketCap daily closes at 00:00 UTC) and BITO ETF; DAILY bars. Not CME futures data.
- Cost assumptions: none stated in the text read.
- Data window: 29 December 2017 to 28 February 2024.
- Quality tells: blog, daily bars, 00:00 UTC day boundary (not aligned with the CME session), roughly 75 expiry events, pattern flips sign across sub-samples, no significance tests visible in the text; points to a primary intraday paper (Blasco, Corredor and Satrustegui 2023, followed up as its own item).
- Verbatim passages:
  - P-K7-004-a: "The data sample starts with the first BTC futures expiration day on Friday, 12/29/2017 and runs until 28/2/2024. Bitcoin spot is traded 24/7 and each trading day in our data ends at 0.00 UTC time."
  - P-K7-004-b: "The daily pattern in the BTC returns in the period before the BITO introduction (2017-2021) is similar to the whole period (2017-2024). On the other hand, the pattern in the daily returns after the BITO ETF introduction (2021-2024) is reversed, especially on days preceding the expiration and on the expiration day itself."
  - P-K7-004-c: "We can see that BTC gains significantly during expiration day but have negative returns on the preceding day."
  - P-K7-004-d: "Bitcoin contract positions expire on CME at 16:00 London time on the last Friday of every month." (secondary; to be checked against CME's own contract terms)
- Numeric claims: window dates (P-K7-004-a); all return magnitudes are in images [unverified].
- Tags: port of D.1 family E (calendar and events: expiry day) at daily-bar level (family H construction); intraday-feasible only as an expiry-day session trade from the CME open to 15:08 CT; the d+1/d+2 weekend legs are not feasible (weekend hold); sign instability across sub-samples; clusters tagged: K7.

### K7-005. Blasco, Corredor and Satrustegui (2023), Is there an expiration effect in the bitcoin market?
- Citation: N. Blasco, P. Corredor, N. Satrústegui, International Review of Economics and Finance 85 (2023) 647-663, doi 10.1016/j.iref.2023.02.013 (open access, CC BY-NC-ND). Found through K7-004's literature section.
- Retrieval: full text, publisher PDF from the Zaragoza repository, https://zaguan.unizar.es/record/125822/files/texto_completo.pdf, pdftotext. Read: abstract, sections 1 to 3, section 4.3 (returns), robustness (pooled) and conclusions.
- Mechanism: around the CME monthly bitcoin futures expiry (final settlement at the CME CF BRR, 4:00 p.m. London on the last Friday), spot bitcoin shows abnormal positive hourly returns in the roughly 5 hours before expiry, plus volume and volatility increases before and decreases after. Authors attribute the positive return to unwinding of short spot/long futures arbitrage. CBOE and Bakkt expiries show no clear return effect.
- Products and horizon: seven spot exchanges (Bitstamp, Coinbase, Itbit, Kraken, Gemini, Binance, Bitfinex), hourly bars; CME, CBOE and Bakkt expiry calendars. Effect horizon: about 1 to 5 hours before expiry, 1 hour after. 4:00 p.m. London is normally 10:00 CT, so the window before expiry falls inside the CME Globex session on a Friday [conversion is this worker's arithmetic, not the paper's].
- Cost assumptions: none (regression study, no trading rule, no costs).
- Data window: 31 December 2017 to 20 November 2020; 25,305 hourly observations per exchange; roughly 35 CME expiries [count is this worker's arithmetic from the window, unverified].
- Quality tells: published (peer-reviewed), open access; 576 models over 48 cumulative dummies (heavy multiplicity: "we have finally run 576 models"); significance claimed at 1% for the CME return effect; SPOT returns, not CME futures returns; pooled robustness says the CME return effect holds "about 5 h before expiration, although not in the last hour", which differs from the per-exchange result that the strongest effect is at D1/D2; pre-MBT, pre-spot-ETF sample. K7-004 (2021-2024 daily) reports sign reversal after October 2021, which bears on persistence.
- Verbatim passages:
  - P-K7-005-a (section 3): "The multiplier of the bitcoin futures contract traded in CME is 5 bitcoins and the final settlement price is equal to the CME Bitcoin Reference Rate (BRR) at 4:00 p.m. London time on the last Friday of the contract month."
  - P-K7-005-b (section 4.3): "When we estimate the effect using the expiration dates for the CME bitcoin futures, we appreciate a clear effect on prices at the maturity time and 5 h prior to the expiration time in all the exchanges under analysis. Returns are significantly higher than the mean return at the 1% significance level. The strongest effect is reflected in D2 and D1, that is, at the time of the expiration effect and 1 h before."
  - P-K7-005-c (section 4.3): "Our prevailing result is an abnormal positive return induced by the CME. ... Typically, this effect is attributed to the unwinding of short arbitrage positions."
  - P-K7-005-d (robustness): "In the specific case of CME expiration, the results show a significant positive effect on returns in a short time before maturity (about 5 h before expiration, although not in the last hour). No effects are detected after then."
  - P-K7-005-e (section 3): "The total period covers the beginning of the futures contracts in December 2017 (we take December 31, 2017 as the initial date) until November 20, 2020. The total number of observations is 25,305 for each variable and exchange."
  - P-K7-005-f (section 4.3): "The effects in relation to the monthly expiration times of CBOE bitcoin futures are scarce."
- Numeric claims: 1% significance, 5 h window (P-K7-005-b, -d); 25,305 observations and window (P-K7-005-e); 576 models (method section, "Thus, we have finally run 576 models, using 48 alternative cumulative hourly dummies", checked); 15-day-coincidence percentages 29.4%/27.7%/42.8% (section 4.3, checked).
- Tags: new to the program (MBT settlement-window / expiry flow; also port of D.1 family E calendar at an hourly horizon); intraday-feasible: the pre-expiry window (about 05:00 to 10:00 CT on the last Friday, [conversion unverified for DST mismatch weeks]) lies inside the CME session and ends before 15:08 CT; clusters tagged: K7.

### K7-006. Robertson and Zhang (2025; SSRN 2022), Price discovery in bitcoin spot and futures markets
- Citation: Kevin Robertson and Ren-Jian Zhang, Journal of International Money and Finance (2025) 103415, doi 10.1016/j.jimonfin.2025.103415; SSRN working paper "Suitable Price Discovery Measurement of Bitcoin Spot and Futures Markets" (2022), doi 10.2139/ssrn.4012165; treated as one source (same authors and question; the link is this worker's judgement from titles and authors, [unverified] that the content is identical).
- Retrieval: ABSTRACT ONLY (SSRN working-paper abstract from the Crossref record). Routes failed: SSRN (blocked), Elsevier article API returns metadata only, Unpaywall and OpenAlex report closed; the JIMF record carries no abstract.
- Mechanism (abstract only): information share and component share are distorted by bitcoin trade-activity nuances; a Hayashi-Yoshida lead-lag estimator finds CME bitcoin futures lead price formation.
- Products and horizon: CME bitcoin futures, Binance futures, spot; high-frequency (asynchronous tick) lead-lag.
- Cost assumptions: [unverified]. Data window: "the last two years" before the 2022 working paper [exact dates unverified].
- Quality tells: SSRN working paper later published in JIMF; direction opposite to K7-001 and K7-002, consistent with K7-003's specification-sensitivity point.
- Verbatim passages:
  - P-K7-006-a (SSRN abstract): "We also apply a more suitable framework for high frequency lead-lag analysis on bitcoin spot and futures markets by using the Hayashi-Yoshida (HY) estimator (Hayashi and Yoshida, 2005)."
  - P-K7-006-b (SSRN abstract): "Our results show that CME bitcoin futures have consistently led price formation over the last two years."
- Numeric claims: none; all lead-lag magnitudes [unverified].
- Tags: new to the program (CME-spot lead-lag; relevant to whether MBT is a leader or a follower); intraday-feasible as a signal only if MBT follows (this source says it leads, which would make spot-to-MBT rules empty); clusters tagged: K7.

### K7-007. Ngene and Wang (2024), Arbitrage opportunities and feedback trading in regulated bitcoin futures market: An intraday analysis
- Citation: Geoffrey Ngene and Jinghua Wang [second author's given name unverified], International Review of Economics and Finance 89 (2024) 743-761, doi 10.1016/j.iref.2023.10.032; SSRN 4291254 (2022) is the working paper.
- Retrieval: ABSTRACT ONLY (SSRN abstract from the Crossref record). Routes failed: SSRN (blocked); Elsevier API metadata only; Unpaywall closed.
- Mechanism (abstract only): 5-minute quantile regressions of regulated bitcoin futures returns on lagged returns interacted with the futures-spot basis; the sign of feedback trading (momentum vs reversal at 5 minutes) switches with market state and with changes in the basis.
- Products and horizon: regulated (CME implied) bitcoin futures and spot, 5-minute bars.
- Cost assumptions: [unverified]. Data window: [unverified].
- Quality tells: quantile-regression evidence, "episodic" effects; the closing sentence about maximizing returns is not backed by a stated trading test in the abstract.
- Verbatim passages:
  - P-K7-007-a (abstract): "The study investigates the impact of arbitrage opportunities on feedback trading using intraday 5-minute Bitcoin futures and spot prices."
  - P-K7-007-b (abstract): "When the basis declines by varying magnitudes across quantiles, positive feedback trading shifts to negative feedback trading. The findings suggest widening basis intensifies negative feedback trading during bull market conditions."
- Numeric claims: none; [unverified].
- Tags: port of D.1 family C (short-horizon reversal/momentum) conditioned on the MBT basis (a K7-specific state variable); intraday-feasible (5-minute horizon; basis readable from spot); clusters tagged: K7.

### K7-008. Hattori and Ishida (2020/2021), The relationship between arbitrage in futures and spot markets and Bitcoin price movements: Evidence from the Bitcoin markets
- Citation: Takahiro Hattori and Ryo Ishida, Journal of Futures Markets 41(1) 105-114 (issue dated January 2021, Crossref issued December 2020), doi 10.1002/fut.22171.
- Retrieval: ABSTRACT ONLY (Semantic Scholar record). Routes failed: Wiley (Cloudflare challenge / 403), Unpaywall closed, no working paper found.
- Mechanism (abstract only): reconstructed intraday CBOE futures-spot arbitrage bounds; few arbitrage profits in normal markets, large ones in crashes.
- Products and horizon: CBOE bitcoin futures (delisted 2019) and spot; intraday.
- Cost assumptions: the arbitrage condition includes the costs investors face [detail unverified]. Data window: [unverified].
- Quality tells: CBOE, not CME; crash-conditional; arbitrage requires holding both legs to expiry (not a one-legged MBT rule).
- Verbatim passages:
  - P-K7-008-a (abstract): "Using intraday data of the Chicago Board Options Exchange (CBOE), we reconstruct the actual arbitrage condition that investors confront."
  - P-K7-008-b (abstract): "We find that there are few arbitrage profit opportunities in “normal” markets, but large arbitrage profit opportunities arise during Bitcoin market “crashes"."
- Numeric claims: none; [unverified].
- Tags: new to the program (basis dislocation in crashes, a state for MBT basis rules); intraday-infeasible as arbitrage (two legs held to expiry; spot leg not tradable on Topstep); only a state flag transfers; clusters tagged: K7.

### K7-009. Pati (2022), Informativeness of CME Micro Bitcoin Futures in Pricing of Bitcoin: Intraday Evidence
- Citation: P. Pati [given name unverified], Finance Research Letters (October 2022) 103084, doi 10.1016/j.frl.2022.103084.
- Retrieval: BLOCKED, TITLE ONLY. No abstract in Crossref, OpenAlex or Semantic Scholar; ScienceDirect HTTP 403 (WebFetch); Elsevier article API returns metadata only; Unpaywall closed.
- Mechanism, products, horizon, cost, data window: [unverified]; the title says CME Micro Bitcoin (MBT) futures and intraday evidence on its informativeness for bitcoin pricing.
- Verbatim passages: none beyond the title.
- Tags: the only MBT-specific item found; left for the lead as an unreadable lead (institutional access would be needed); clusters tagged: K7.

### K7-010. Baur, Cahill, Godfrey and Liu (2019), Bitcoin time-of-day, day-of-week and month-of-year effects in returns and trading volume
- Citation: Dirk G. Baur, Daniel Cahill, Keith Godfrey, Zhangxin (Frank) Liu [given names unverified], Finance Research Letters 31 (December 2019) [volume unverified], doi 10.1016/j.frl.2019.04.023; SSRN 3088472 (2017) is the working paper.
- Retrieval: ABSTRACT ONLY (SSRN abstract, Crossref record). Routes failed: Unpaywall lists a ScienceDirect OA location but the Elsevier article API returned metadata only and ScienceDirect blocks WebFetch; SSRN blocked; UWA repository landing page not tried further [route left open].
- Mechanism (abstract only): intraday time-of-day, day-of-week and month effects in bitcoin returns and volume across seven exchanges; effects are time-varying and not persistent.
- Products and horizon: spot bitcoin, seven exchanges, intraday (hourly implied) [unverified].
- Cost assumptions: [unverified]. Data window: [unverified] ("more than 15 million price and trading volume observations").
- Quality tells: negative result; spot only; pre-CME-dominance window.
- Verbatim passages:
  - P-K7-010-a (abstract): "This study is the first to report intra-day time-of-day, day-of-week, and month-of-year effects for Bitcoin returns and trading volume."
  - P-K7-010-b (abstract): "Using more than 15 million price and trading volume observations from seven global Bitcoin exchanges reveal time-varying effects but no consistent or persistent patterns across the sample period. The results suggest that Bitcoin markets are efficient."
- Numeric claims: 15 million observations, seven exchanges (P-K7-010-b).
- Tags: port of D.1 family A (session clock) and E (calendar) on bitcoin: negative evidence; intraday-feasible as a test design; clusters tagged: K7.

### K7-011. Shen, Urquhart and Wang (2022), Bitcoin intraday time series momentum
- Citation: Dehua Shen, Andrew Urquhart, Pengfei Wang, The Financial Review 57 (2022) [volume unverified], doi 10.1111/fire.12290.
- Retrieval: full text, accepted manuscript R2 dated 21 September 2021, https://centaur.reading.ac.uk/100181/3/21Sep2021Bitcoin%20Intraday%20Time-Series%20Momentum.R2.pdf, pdftotext. Read: abstract, introduction, data (section 2), section 3.1 and out-of-sample, transaction costs, robustness (10am-4pm window), conclusions.
- Mechanism: intraday time-series momentum on spot bitcoin: the return from the previous day's close (5pm EST, the start of the CME bitcoin futures break) to 30 minutes after the exchange's volume-spike "open" predicts the last half-hour return (4:30 to 5pm EST); the second-to-last half hour predicts it negatively. Attributed to liquidity provision.
- Products and horizon: five spot exchanges (Bitfinex, Bitstamp, CEX.IO, Coinbase, Kraken), 1-minute aggregated; half-hour returns; day defined as ending 5pm EST.
- Cost assumptions: zero in the main tests; breakeven costs 3, 7 and 10 bps for the three signals versus a Bitstamp fee of 25 bps (not profitable unlevered).
- Data window: exchange start dates 2013-01-01 to 2014-12-03 through 31 December 2020.
- Quality tells: published; in-sample R2 1.44%, pooled out-of-sample R2 1.09% to 1.61%; the 10am-4pm EST re-test is "a lot smaller in magnitude and statistical significance"; breakeven below spot fees; target window (last half-hour to 5pm EST = 15:30 to 16:00 CT when EST is in force) lies after the 15:08 CT flat time.
- Verbatim passages:
  - P-K7-011-a (section 2): "we select the opening time of each exchange when volumes spikes and the closing time when the 60-minute break of CME Bitcoin futures trading begins at 5pm EST."
  - P-K7-011-b (section 3.1): "we conduct pooled regressions and find that the first half hour significantly predicts the last half hour with a slope of 0.968. The Newey West t-statistic is 4.38 ... The R2 is 1.44%"
  - P-K7-011-c (out-of-sample): "when we use just the first half-hour return, where the R_OOS^2 is 1.09%. When we use the second last half-hour return alone, the R_OOS^2 is 1.40%, and when we use both, we get a R_OOS^2 [of] 1.61%." (subscripts flattened by pdftotext)
  - P-K7-011-d (transaction costs): "the entire-sample breakeven costs of η(r_ONFH), η(r_SLH) and η(r_ONFH, r_SLH) are 3, 7 and 10 bps respectively, indicating that all of these three strategies are not profitable given that the trading fee of Bitstamp is 25bps."
  - P-K7-011-e (robustness): "Table 12 reports the results and shows that the first half hour does predict the last half hour, but the magnitude of the prediction is a lot smaller in magnitude and statistical significance to our previous results."
  - P-K7-011-f (section 3.1): "we can see that strong evidence of anti-persistence where the second last half-hour return is negatively significantly related with the last half-hour return."
- Numeric claims: slope 0.968, t 4.38, R2 1.44% (P-K7-011-b); OOS R2 (P-K7-011-c); breakeven 3/7/10 bps vs 25 bps fee (P-K7-011-d); window end 31 December 2020 (data section "from the earliest date to 31st December 2020", checked).
- Tags: port of D.1 family A/C (intraday momentum, first-to-last half hour) on bitcoin; intraday-INFEASIBLE as specified (the predicted half hour ends at the 16:00 CT CME break, after 15:08 CT; a variant ending at 15:08 CT is untested here); clusters tagged: K7.

### K7-012. De Nicola (2021), On the Intraday Behavior of Bitcoin
- Citation: Francesco De Nicola [given name unverified], Ledger 6 (2021) 58-80, doi 10.5195/ledger.2021.213 (open access).
- Retrieval: full text, publisher PDF https://ledger.pitt.edu/ojs/ledger/article/download/213/212, pdftotext. Read: abstract, introduction, data, stylized facts (autocorrelation, Tables 2 and 3), strategy section and conclusions.
- Mechanism: significant negative first-order autocorrelation of spot bitcoin returns at 1-, 2- and 4-hour horizons (beyond bid-ask bounce); reversal is larger after larger moves; a fade-the-last-bar rule (long after a large down bar, short after a large up bar, close after one bar) is profitable before fees, best at 2 hours. Attributed to overreaction, excess volatility and liquidation cascades.
- Products and horizon: Bitstamp BTC/USD, 1-minute data aggregated to 5 min to 1 day; holding one bar (1 to 4 hours).
- Cost assumptions: Table 5 and Figure 10 exclude fees; text argues taker fees "below 0.1% per trade" leave it viable; no slippage model; conclusion asserts profit "even after considering trading fees" without a net table in the text read.
- Data window: 1 March 2015 to 27 June 2018 (Kaggle Bitstamp dump by Zielinski).
- Quality tells: single exchange, free Kaggle data, single-author, no out-of-sample split, thresholds "chosen in a completely arbitrary manner, without looking at the data" (claimed), pre-CME-futures-dominance sample (mostly before December 2017); no significance test on strategy P&L.
- Verbatim passages:
  - P-K7-012-a (section 3): "significant levels of negative autocorrelation found for returns calculated on intervals as wide as one, two and even four hours cannot usually be attributed to microstructural components of the market or orderbook effects. Significant levels of negative autocorrelation of returns imply systematic mean-reversion"
  - P-K7-012-b (Table 3): "1 hour -0.0557 1.86x10-21 *** 2 hours -0.0858 3.20x10-25 *** 4 hours -0.0564 1.46x10-6 *** 1 day -0.0071 0.8047"
  - P-K7-012-c (strategy): "it bets on the market (goes long) if the last price movement was large and negative, and against the market (goes short) if the movement in the last period was large and positive. The trade is then closed after a single time unit has passed"
  - P-K7-012-d (strategy): "Given that taker fees on some of the more prominent cryptocurrency exchanges are below 0.1% per trade, and given that liquidity should not be an issue when dealing with a relatively low trade frequency, it looks like the proposed strategy could even be viable in practice, barring microstructural anomalies."
  - P-K7-012-e (data): "The original series spans from 1 December 2012 to 27 June 2018, but for our analysis we only used data from 1 March 2015 onwards"
  - P-K7-012-f (strategy): "the strategy would have produced a significant return, multiplying initial capital by a factor greater than eight in a period of approximately three years" (no fees, non-compounded, 2-hour bars, zero threshold)
- Numeric claims: autocorrelations (P-K7-012-b); x8 gross (P-K7-012-f); fee < 0.1% (P-K7-012-d); window (P-K7-012-e).
- Tags: port of D.1 family C (short-horizon reversal) and G (coarser bars) on bitcoin; intraday-feasible (1 to 4 hour holds fit inside the CME day session, entries after 15:08 CT excluded); clusters tagged: K7.

### K7-013. Eross, McGroarty, Urquhart and Wolfe (2019), The intraday dynamics of bitcoin
- Citation: Andrea Eross, Frank McGroarty, Andrew Urquhart, Simon Wolfe, Research in International Business and Finance (2019), doi 10.1016/j.ribaf.2019.01.008; SSRN 3013699 (2017) working paper. Seed from the lead's memory: verified (title; "Eross and co-authors").
- Retrieval: ABSTRACT ONLY (SSRN abstract, Crossref record). Routes failed: Southampton eprints accepted-manuscript .docx links (412048, 429352) return an HTML "Error" page; ScienceDirect/Elsevier API metadata only; SSRN blocked.
- Mechanism (abstract only): stylized facts: n-shaped intraday patterns in volume, spread and volatility (European and North American hours dominate); lead-lag and Granger causality among intraday variables. No directional return rule.
- Products and horizon: one spot exchange ("the leading Bitcoin exchange with the highest information share"), 5-minute, GMT-stamped.
- Cost assumptions: none. Data window: 1 November 2014 to 31 October 2016.
- Quality tells: early, pre-futures sample; volatility/volume seasonality only (a D.1 family D volatility-state input, not a return signal).
- Verbatim passages:
  - P-K7-013-a (abstract): "Employing GMT-stamped tick data aggregated to the 5-mintuely frequency, we find that volume, bid-ask spread and volatility all experience n-shaped patterns throughout the day which suggests that European and North American traders are the main drivers of Bitcoin trading and volatility."
  - P-K7-013-b (abstract): "examining the intraday variables of the leading Bitcoin exchange with the highest information share from 1st November 2014 to 31st October 2016"
- Numeric claims: window (P-K7-013-b).
- Tags: port of D.1 family A/D (session-clock volatility profile) on bitcoin; intraday-feasible as a volatility-state input; clusters tagged: K7.

### K7-014. Lee et al. (2026), Spot Bitcoin ETF Approval and the Intraday Risk Profile of Bitcoin: A Difference-in-Differences Analysis
- Citation: Lee et al. [co-authors unverified], SSRN working paper (2026), doi 10.2139/ssrn.6713392.
- Retrieval: ABSTRACT ONLY (Crossref record). SSRN full text blocked (curl challenge; WebFetch 403 on SSRN generally).
- Mechanism (abstract only): after US spot ETF approval (January 2024), bitcoin volatility spikes in the first 30 minutes of NYSE trading (9:30-10:00 ET = 8:30-9:00 CT), the only window surviving multiple testing; left tail of US-hour returns deepens; volume surges at open and close; ETH shows no such pattern.
- Products and horizon: Coinbase BTC/USD (hourly and sub-hourly), ETH/USD control; one year before vs one year after.
- Cost assumptions: none (risk study). Data window: symmetric one-year windows around January 2024 [exact dates unverified].
- Quality tells: working paper; multiple-testing correction stated; describes volatility and tails, not mean returns; post-ETF regime is the regime MBT trades in now.
- Verbatim passages:
  - P-K7-014-a (abstract): "The aggregate US-hour effect is null, but hour-specific and sub-hourly decomposition reveals a volatility spike concentrated in the first 30 minutes of ETF trading (9:30-10:00 ET), the only window surviving multiple testing correction."
  - P-K7-014-b (abstract): "Quantile analysis shows left-tail deepening at the 5th and 10th percentiles of US-hour returns while the median is unaffected, and both tails widen at the opening window."
  - P-K7-014-c (abstract): "an ETH/USD comparison on the same exchange, which lacked comparable ETF exposure, shows no similar pattern"
- Numeric claims: none beyond windows and percentiles quoted.
- Tags: port of D.1 family A/D (session clock, volatility state) on MBT: the 08:30 CT equity-open window is a volatility regime for MBT; intraday-feasible; clusters tagged: K7 (the mechanism is the ETF's NYSE clock acting on bitcoin, i.e., inside K7's product through an equity-market schedule; no equity price leg is used, so not flagged to K8).

### K7-015. Miralles-Quirós and Miralles-Quirós (2022), A new perspective of the day-of-the-week effect on Bitcoin returns: evidence from an event study hourly approach
- Citation: José Luis Miralles-Quirós and María Mar Miralles-Quirós [given names unverified], Oeconomia Copernicana 13(3) (2022) 745-782, doi 10.24136/oc.2022.022 (open access).
- Retrieval: full text, publisher PDF https://journals.economic-research.pl/oc/article/download/2091/1935, pdftotext. Read: abstract, introduction, data and methodology, results (rolling windows, strategies, Sharpe tests), discussion.
- Mechanism: hour-of-day by day-of-week event study on Kraken hourly closes; mean returns at single hours are mostly insignificant, but post-event cumulative returns after Friday 3 p.m. (and 4 p.m.) EST over 4 to 24 hours are significant, and holding 4 to 24 hours from Friday 3 p.m. beats buy-and-hold on Sharpe. Explained by retail buy-before-weekend behaviour and late-informed traders.
- Products and horizon: Kraken BTC/USD hourly; holds of 4 to 24 hours starting Friday 3 p.m. EST (the paper states EST as its time zone throughout).
- Cost assumptions: none ("these costs in internet trading are negligible").
- Data window: 1 January 2016 to 31 December 2021, 52,608 hourly observations; 1-, 2- and 3-year rolling windows.
- Quality tells: 24 x 7 event cells x several holding windows x several rolling windows (heavy multiplicity, no correction mentioned in the text read); Sharpe values "not annualized" read off figures; the only exploitable effect straddles the Friday CME close and the weekend.
- Verbatim passages:
  - P-K7-015-a (data): "for the period spanning from 1 January 2016 to 31 December 2021 (which amounts to 52,608 hourly observations). Eastern Standard Time (EST) is the standard time zone used in this paper."
  - P-K7-015-b (results): "by considering these different rolling windows we add robustness to the results obtained mainly on Fridays, where there is a clear inefficiency, especially at 3 p.m. that can be exploited by investors."
  - P-K7-015-c (results): "We find that the proposed strategies of investing on Fridays following the event –those that show 100% of statistically significant average returns– clearly outperform the performances of the other two investment options considered (buy and hold and only investing from 3:00:00 p.m. to 3:59:59 p.m. on Fridays)."
  - P-K7-015-d (results): "We find low percentages of statistically significant hourly mean returns, those defined as the event, for all the days, time slots or rolling windows considered."
  - P-K7-015-e (method): "the average cumulative returns do not incorporate transaction costs because these costs in internet trading are negligible and excluding them does not affect the results."
- Numeric claims: window and 52,608 observations (P-K7-015-a); ">90%" significance share for Fridays with a 2-year window (results: "significance percentages higher than 90%", checked).
- Tags: port of D.1 family E (day-of-week) with an A (clock) component, on bitcoin; intraday-INFEASIBLE for MBT: the long starts Friday 3 p.m. EST (14:00 CT) and needs 4 to 24 hours, i.e., past the Friday CME close and into the weekend; the 3:00-3:59 p.m. hour alone is "always negative" in Sharpe; clusters tagged: K7.

### K7-016. Huang and Gao (2023), Forecasting Bitcoin Futures: A Lasso-BMA Two-Step Predictor Selection for Investment and Hedging Strategies
- Citation: Huang and Gao [given names unverified], SAGE Open 13 (2023), doi 10.1177/21582440231151652 (open access, DOAJ-listed).
- Retrieval: ABSTRACT ONLY (Crossref record). Routes failed: Sage PDF and full-XML (Cloudflare challenge by curl; HTTP 403 by WebFetch); Wayback availability API returned 429; DOAJ record only points back to Sage.
- Mechanism (abstract only): LASSO then Bayesian model averaging selects predictors built from intraday spot trades and daily futures variables to forecast CME bitcoin futures returns and volatility; forecast-based strategies do well out of sample.
- Products and horizon: CME bitcoin futures; "different time horizons" [horizons unverified; daily inputs imply daily or longer forecasts].
- Cost assumptions: [unverified]. Data window: [unverified] (after December 2017).
- Quality tells: large predictor universe with two-stage selection (data-mining risk); SAGE Open venue; out-of-sample claim unquantified in the abstract.
- Verbatim passages:
  - P-K7-016-a (abstract): "this paper first applies LASSO to pick out best-fitting predictors by shrinking the dimension of a universe of potential determinants sourced from intraday Bitcoin spot trades and daily futures variables."
  - P-K7-016-b (abstract): "We find that factors standing out from this two-step procedure possess a strong predictive power for Bitcoin futures return and volatility in different time horizons. It is further demonstrated that the investment and hedging strategies established based on our forecasts perform well in out-of-sample validations."
- Numeric claims: none; [unverified].
- Tags: port of D.1 family F/H (data-native statistics, daily-bar constructions) on CME bitcoin futures, and relevant to design D15 (one pre-registered ML member per cluster) as a feature-selection precedent; intraday-feasible only if the forecast is used for a same-day session trade [unverified]; clusters tagged: K7.

### K7-017. Bouri, Lau, Saeed, Wang and Zhao (2021), On the intraday return curves of Bitcoin: Predictability and trading opportunities
- Citation: E. Bouri, C. K. M. Lau, T. Saeed, S. Wang, Y. Zhao, International Review of Financial Analysis 76 (2021) 101784, doi 10.1016/j.irfa.2021.101784.
- Retrieval: full text, accepted version, https://centaur.reading.ac.uk/97607/1/Bitcoin_Functional_Accepted.pdf, pdftotext. Read: abstract, introduction, data, forecasting results, trading strategy, transaction costs.
- Mechanism: functional data analysis of cumulative intraday return (CIDR) curves; forecast tomorrow's curve from serially correlated principal-component scores, buy at the forecast minimum time and sell at the forecast maximum time after it (long-only because of short-sale constraints).
- Products and horizon: Bitstamp BTC/USD, 5-minute, 24-hour "day" (entry and exit times anywhere within it, e.g. "buy Bitcoin at 5:45:00 and sell it at 23:45:00").
- Cost assumptions: main results without costs; Appendix A3 with a 0.03% fee: Sharpe 0.74 for FPAR, entire sample, S = 182.
- Data window: 1 November 2014 to 10 August 2019 (T = 1367 days, 5-10 January 2015 removed); rolling training windows S = 182 or 365 days.
- Quality tells: published; free Kaggle data (same source as K7-012); results sensitive to S (the both-scores-correlated sub-sample flips to a negative Sharpe at S = 365); Sharpe above 1 before costs with high drawdown; no slippage; the 24-hour curve does not map to the CME session.
- Verbatim passages:
  - P-K7-017-a (section 2): "We download the intraday price data (in the currency of US dollars) of Bitcoin at 5-minute frequency from https://www.kaggle.com/mczielinski/bitcoin-historical-data, which collects the high frequency data from the Bitstamp exchange. ... The sample ranges from 01-November-2014 to 10-August-2019, covering T = 1367 days."
  - P-K7-017-b (strategy): "Overall, the developed three trading strategies can exploit the trading opportunities in the intraday market as measured by more than 1 of Sharpe ratio, while the risk level is also high indicated by their maximum drawdown."
  - P-K7-017-c (costs): "we have assumed that the fee rate is 0.03% and revaluated the trading performance ... the FRAR remains the superior strategy with a Sharpe ratio of 0.74 if trading is done in the entire sample period with S = 182." (the text says "FRAR"; the method elsewhere is FPAR)
  - P-K7-017-d (footnote 8): "Our calculation on the return of the trading strategy is without transaction cost."
  - P-K7-017-e (strategy): "The result is sensitive to the parameter S. We have a positive Sharpe ratio if S = 182, while a negative Sharpe ratio if S = 365."
- Numeric claims: Sharpe > 1 gross (P-K7-017-b); 0.74 net of 0.03% (P-K7-017-c); window and T (P-K7-017-a).
- Tags: port of D.1 family F (data-native statistics: forecasting the intraday return profile) on bitcoin; relevant to D15 as an ML-ish member precedent; intraday-feasible only if the curve is re-defined on the CME session and exits forced by 15:08 CT (untested here); clusters tagged: K7.

### K7-018. Wen, Bouri, Xu and Zhao (2022), Intraday return predictability in the cryptocurrency markets: Momentum, reversal, or both
- Citation: Zhuzhu Wen, Elie Bouri, Yahua Xu, Yang Zhao, North American Journal of Economics and Finance 62 (2022) 101733, doi 10.1016/j.najef.2022.101733; SSRN 4080253 working paper (one source).
- Retrieval: ABSTRACT ONLY (SSRN abstract from Crossref). Routes failed: SSRN blocked; OpenAlex reports closed with no repository copy; ScienceDirect/Elsevier API not usable (metadata only elsewhere).
- Mechanism (abstract only): bitcoin intraday momentum (late-informed investors) and intraday reversal (overreaction), with predictability conditioned on large intraday jumps, FOMC announcement days, liquidity and COVID; a timing strategy beats always-long and buy-and-hold. Also present in ETH, LTC, XRP.
- Products and horizon: spot bitcoin (and ETH, LTC, XRP), intraday half-hour or similar segments [segment definitions unverified].
- Cost assumptions: [unverified]. Data window: 3 March 2013 to 31 May 2020.
- Quality tells: published; state-dependence on jumps and FOMC days makes it relevant to the scheduled-release angle; overlaps K7-011 (same question, different design).
- Verbatim passages:
  - P-K7-018-a (abstract): "Using high-frequency price data on Bitcoin from March 3, 2013, to May 31, 2020, it shows that the patterns of intraday return predictability change in the presence of large intraday price jumps, FOMC announcement release, liquidity levels, and the outbreak of the COVID-19."
  - P-K7-018-b (abstract): "Further analysis shows that the timing strategy based on the intraday predictors produces higher economic value than the benchmark strategy such as the always-long or the buy-and-hold."
  - P-K7-018-c (abstract): "Evidence of intraday momentum can be explained in light of the theory of late-informed investors, whereas evidence of intraday reversal, which is unique to the cryptocurrency market, can be related to investors’ overreaction to non-fundamental information and overconfidence bias."
- Numeric claims: window (P-K7-018-a); all magnitudes [unverified].
- Tags: port of D.1 family C (momentum/reversal) with an E (FOMC day) conditioner, on bitcoin; intraday-feasible depending on the segment definitions [unverified]; ETH evidence usable for MET only as a signal leg; clusters tagged: K7.

### K7-019. CF Benchmarks (2026), CME CF Cryptocurrency Reference Rates Methodology Guide, version 17.4
- Citation: CF Benchmarks Ltd, "CME CF Cryptocurrency Reference Rates Methodology Guide", Version 17.4, 24 August 2026, https://docs.cfbenchmarks.com/CME%20CF%20Reference%20Rates%20Methodology.pdf (linked from https://www.cfbenchmarks.com/data/indices/BRR).
- Retrieval: full text, publisher PDF (49 pages), pdftotext -layout. Read: version history (first rows), definitions (section 3), methodology 4.1 and design rationale, section 8 parameter table for BRR, ETHUSD_RR, BRRNY, ETHUSD_NY.
- Mechanism (a methodology fact, not a study): the BRR (the CME bitcoin futures final settlement reference per K7-005's P-K7-005-a) is the equal-weighted average of twelve 5-minute volume-weighted medians of constituent-exchange spot trades from 3:00 to 4:00 p.m. London; the New York variant BRRNY uses 3:00 to 4:00 p.m. New York (14:00 to 15:00 CT), inside the MBT day session before 15:08 CT. The methodology itself says the rate can be replicated by trading Y/K units per partition, i.e., the design anticipates hedgers spreading flow evenly across the hour.
- Products and horizon: bitcoin and ether spot reference rates; 60-minute window, 5-minute partitions.
- Cost assumptions: not applicable. Data window: not applicable (methodology as of 24 August 2026).
- Quality tells: primary administrator document, current version; which funds or contracts reference BRRNY is not stated in the sections read [unverified that spot ETFs value at BRRNY].
- Verbatim passages:
  - P-K7-019-a (section 4.1.1): "The list is partitioned into a number of equally-sized time intervals ... For each partition separately, the volume-weighted median trade price is calculated from the trade prices and sizes of all Relevant Transactions, i.e. across all Constituent Exchanges. ... The CME CF Cryptocurrency Reference Rate is then given by the equally-weighted average of the volume-weighted medians of all partitions."
  - P-K7-019-b (section 8 table): "BRR ... Effective Time (T) 4:00 p.m. London Time ... TWAP Period Length 60 minutes ... 3:00pm to 4:00 pm London time ... Partition Length 5 minutes ... Number of Partitions 12" and for BRRNY "4:00 p.m. New York Time ... 3:00pm to 4:00 pm New York time"
  - P-K7-019-c (design rationale): "Assuming K partitions, a trader aiming to transact Y units of the relevant cryptocurrency at the CME CF Cryptocurrency Reference Rates can do so with little tracking error by transacting Y/K units of the cryptocurrency during each partition."
  - P-K7-019-d (version header): "Version: 17.4 Version Date: 24th August 2026"
- Numeric claims: 60 minutes, 12 partitions of 5 minutes, effective times (P-K7-019-b).
- Tags: new to the program (settlement-window flow: BRR 09:00 to 10:00 CT on expiry Fridays for MBT final settlement; BRRNY 14:00 to 15:00 CT daily); intraday-feasible (both windows end before 15:08 CT; London/Chicago DST-mismatch weeks shift the BRR window [conversion is this worker's arithmetic, unverified]); clusters tagged: K7.

### K7-020. Lim (2026), The Price Impact of Spot Bitcoin ETF Flows
- Citation: Lim [given name unverified], SSRN working paper (2026), doi 10.2139/ssrn.6592830 (a second SSRN record 10.2139/ssrn.6564338 carries the same title and abstract; one source).
- Retrieval: ABSTRACT ONLY (Crossref record of the SSRN abstract). SSRN full text blocked.
- Mechanism (abstract only): daily net creations into the five largest US spot bitcoin ETFs move bitcoin the same day (Kyle lambda 53 bps per $100M) and predict next-day returns; individual flow shocks reverse, but flow autocorrelation produces cumulative drift. A rule could read the prior day's published ETF flow and trade MBT in the next CME day session.
- Products and horizon: bitcoin (spot), five US spot ETFs; daily; next-day return prediction.
- Cost assumptions: [unverified]. Data window: January 2024 to April 2025 (313 trading days); ETF trading data from Databento (the author's, not this program's).
- Quality tells: single-author working paper; 313 days; the next-day predictability is one t-statistic in the abstract; flow publication timing (when the prior day's flow is public relative to the CME open) is not stated in the abstract [unverified], which decides feasibility.
- Verbatim passages:
  - P-K7-020-a (abstract): "A $100 million net flow into spot Bitcoin ETFs is associated with a 53 basis point same-day Bitcoin return."
  - P-K7-020-b (abstract): "Flows explain 21% of daily return variation (t = 8.99) and predict next-day returns (Newey-West t = 3.12)."
  - P-K7-020-c (abstract): "However, after controlling for future flows, individual flow shocks reverse significantly (t = -2.42 to -3.99 at all horizons). The resolution is a flow-persistence illusion"
  - P-K7-020-d (abstract): "Using daily net flow data and ETF trading data from Databento for the five largest U.S. spot Bitcoin ETFs over January 2024 to April 2025 (313 trading days)"
- Numeric claims: 53 bps/$100M (P-K7-020-a); 21%, t 8.99, next-day NW t 3.12 (P-K7-020-b); reversal t (P-K7-020-c); window (P-K7-020-d).
- Tags: new to the program (ETF-flow signal, read the prior day, trade MBT in the day session; a non-CME signal instrument on the bitcoin exposure, so K7); intraday-feasible if the flow is public before the entry time [unverified]; clusters tagged: K7.

### K7-021. Aleti and Mizrach (2021), Bitcoin spot and futures market microstructure
- Citation: Saketh Aleti and Bruce Mizrach, Journal of Futures Markets 41 (2021) [issue and pages unverified], doi 10.1002/fut.22163; SSRN 3459111 (2019) working paper (one source).
- Retrieval: ABSTRACT ONLY (SSRN abstract via Crossref, JFM abstract via Crossref). Routes failed: Wiley (Cloudflare/403), SSRN blocked, the author's Rutgers page lists only a CV PDF, the Google Sites page carried no paper link.
- Mechanism (abstract only): CME bitcoin futures lead price discovery over the four BRR settlement spot exchanges; BTC leads ETH price adjustment; spot executions often trade through better quotes.
- Products and horizon: CME bitcoin futures; four settlement spot exchanges (BRR constituents); ETH; millisecond to minute microstructure.
- Cost assumptions: reports spreads (average 0.0298%), not a trading cost model. Data window: [unverified].
- Quality tells: published JFM; contradicts K7-001 and K7-002 on the CME-vs-spot direction (see K7-003 on specification sensitivity); the BTC-leads-ETH finding bears on MET as a signal leg (inside K7).
- Verbatim passages:
  - P-K7-021-a (abstract): "We study Bitcoin (BTC) trading at the CME and four settlement spot exchanges that transact $146 million per day in the BTC/USD pair."
  - P-K7-021-b (abstract): "The CME leads price discovery. BTC leads ETH price adjustment."
  - P-K7-021-c (abstract): "Bid-ask spreads average 0.0298%. Trade sizes of over $1 million move markets by less than 1%. ... Most executions trade-through better quotes, with estimated losses of $36 million."
- Numeric claims: $146 million per day, 0.0298%, $36 million (P-K7-021-a, -c).
- Tags: new to the program (CME-leads-spot; BTC-leads-ETH, an inside-K7 pair with MET as a signal leg or ETH spot as a lagging reference); intraday-feasible as a lead-lag design; clusters tagged: K7.

### K7-022. Deprez and Frömmel (2024), Are simple technical trading rules profitable in bitcoin markets?
- Citation: Niek Deprez and Michael Frömmel, International Review of Economics and Finance (2024), doi 10.1016/j.iref.2024.05.003 [volume unverified].
- Retrieval: full text, preprint "submitted to Elsevier, May 1, 2024", Ghent University repository, https://biblio.ugent.be/publication/01HY3C3S169G1N6QNYR55NZMFB/file/01HY60XZGZYHNQ6188MSVJT0SG.pdf, pdftotext. Read: abstract, literature table and discussion, data, method (in-or-out, FDR+), results section 4.
- Mechanism: 75,360 moving-average, filter, support-resistance, channel-breakout, OBV and RSI rules on Bitstamp BTC-USD at daily, 60-, 30- and 10-minute frequencies; best rules selected with a false-discovery-rate (FDR+) procedure after costs; out-of-sample portfolios mostly cut drawdown and VaR rather than raise return.
- Products and horizon: Bitstamp BTC-USD spot; daily (midnight UTC), 60, 30 and 10 minutes; long-or-flat (no shorting), positions held across days as signals dictate.
- Cost assumptions: average daily log bid-ask spread plus Bitstamp minimum fee (0.20% before 2 March 2015, 0.10% after); average cost about 0.14 percentage points per trade.
- Data window: 2012 to 2022 tick data (pre-2013 used to initialise the rules).
- Quality tells: published; multiple-testing control (FDR+) and out-of-sample portfolios (strong design); only 1.68% of rules beat the benchmark on mean excess return in-sample; outperformance in return is "not statistically significant"; intraday portfolios beat daily ones on return and risk-adjusted measures but have much lower breakeven costs.
- Verbatim passages:
  - P-K7-022-a (abstract): "Realistic investor behavior is replicated by first employing 75,360 simple technical trading rules, divided over 6 commonly used trading rule classes and daily and intraday frequencies. Next, we select the best performing rules after transaction costs using a multiple hypothesis procedure."
  - P-K7-022-b (section 4): "the three mean-return portfolios perform slightly better, but not statistically significant, in absolute terms, than the benchmark portfolio, while the FDR+ portfolio based on the Sharpe ratio has a similar performance as the benchmark."
  - P-K7-022-c (section 4): "All portfolios have a comparable amount of transactions between 450 and 750 (more than 55 per year) and average transaction costs of around -0.14%points per trade. ... Our outperforming rules only need an increase of less than 0.05%-points before breaking even with the benchmark."
  - P-K7-022-d (section 4): "We see that only 1.68% of the trading rules, on average, outperformed the benchmark in terms of mean excess return and 2.95% in terms of the Sharpe ratio."
  - P-K7-022-e (section 4, panel b): "we see that intraday portfolios outperform the daily portfolios, showing us that there is indeed some value in trading on higher frequencies. ... the BEC of the daily portfolio is much higher, making their performance more robust against small increases of transaction costs"
  - P-K7-022-f (data): "we re-sample it at a daily, 60, 30 and 10 minute frequency, with the daily exchange rate being determined at midnight UTC."
- Numeric claims: 75,360 rules (P-K7-022-a); 450-750 trades, 0.14 pp cost, < 0.05 pp margin (P-K7-022-c); 1.68%/2.95% (P-K7-022-d).
- Tags: port of D.1 families B (breakout/channel), C (trend/momentum via MA and filter rules) and G (coarser bars) on bitcoin, with a multiple-testing design the program can borrow; intraday-feasible only for the intraday-frequency rules with a forced 15:08 CT exit (the paper's positions carry across days); clusters tagged: K7.

### K7-023. Wątorek, Skupień, Kwapień and Drożdż (2023), Decomposing cryptocurrency high-frequency price dynamics into recurring and noisy components
- Citation: Marcin Wątorek, Maria Skupień, Jarosław Kwapień, Stanisław Drożdż, arXiv:2306.17095 (2023) [journal version, if any, unverified].
- Retrieval: full text, https://arxiv.org/pdf/2306.17095, pdftotext. Read: abstract, introduction, data, intraday activity profiles, correlation-matrix and eigen-signal results.
- Mechanism: correlation-matrix decomposition of 10-second returns, volume and trade counts into recurring vs noise components; three session phases (Asia, Europe, US); activity bursts at full hours; the leading recurring return component for BTC and ETH is synchronised around 12:30 UTC, the time of US macro releases (NFP, CPI), and the third eigen-signal points to negative log-returns at that time.
- Products and horizon: Binance BTC, ETH, DOGE, WIN vs USDT, 10-second sampling; intraday profiles.
- Cost assumptions: none (descriptive). Data window: 1 January 2020 to 31 December 2022.
- Quality tells: physics-style descriptive study; no trading test; Binance USDT pairs (not CME); the return result is a recurring-structure eigen-signal, not a tested conditional mean; most eigenvalues sit in the random (Marchenko-Pastur) bulk.
- Verbatim passages:
  - P-K7-023-a (abstract): "Most notably, recurring bursts of activity in bitcoin and ether were identified to coincide with the release times of significant U.S. macroeconomic reports such as Nonfarm payrolls, Consumer Price Index data, and Federal Reserve statements."
  - P-K7-023-b (results): "the most collective signal associated with λ1 portrays the most profound synchronicity of BTC and ETH, which occurs around 12:30 UTC. At this time, the numerous U.S. economic data are published."
  - P-K7-023-c (results): "The third eigensignal Rλ3 also pinpoints the timeframe around 12:30 UTC. In contrast to λ1, it points out to the occurrence of negative log-returns during that period."
  - P-K7-023-d (data): "Time series spanning 3 years (Jan 1, 2020 to Dec 31, 2022) have been downloaded from the Binance exchange, which offers price quotations recorded with 10-second frequency."
  - P-K7-023-e (abstract): "An intriguing pattern of activity surge in 15-minute intervals, particularly at full hours, was also noticed, implying the potential role of algorithmic trading."
- Numeric claims: 12:30 UTC (P-K7-023-b); window (P-K7-023-d).
- Tags: port of D.1 family E (scheduled US releases: 07:30 CT CPI/NFP) and A (session clock) on bitcoin; intraday-feasible (07:30 CT is inside the MBT session); news trading allowed on Topstep except full-size into the event; clusters tagged: K7.

### K7-024. Chi, Chu and Hao (2024), Return and Volatility Forecasting Using On-Chain Flows in Cryptocurrency Markets
- Citation: Yeguang Chi, Qionghua Chu, Wenyan Hao, arXiv:2411.06327 (v2) [journal version unverified].
- Retrieval: full text, https://arxiv.org/pdf/2411.06327, pdftotext. Read: abstract, data (section 2.1), results sections 3.2 to 3.5, appendix notes on samples.
- Mechanism: on-chain exchange net inflows as predictors at 1- to 6-hour horizons: USDT net inflows into exchanges ("dry powder") predict higher BTC and ETH returns over the next 1 to 2 hours; ETH net inflows predict lower ETH returns; BTC net inflows mostly do not predict BTC returns.
- Products and horizon: BTC, ETH, USDT on-chain flows (aggregated across many exchanges); 1, 2, 3, 4 and 6 hour intervals.
- Cost assumptions: none for the return regressions; option-strategy illustrations for ETH only.
- Data window: 16 December 2017 to 20 January 2023 (a 2021-2022 sub-sample appears in robustness).
- Quality tells: working paper; in- and out-of-sample regressions claimed; effects insignificant at 3, 4 and 6 hours for USDT; BTC's own flows "generally lack predictive power"; on-chain data vendor dependence (a data source this program does not hold).
- Verbatim passages:
  - P-K7-024-a (section 3.2.1): "We find that USDT net inflows positively predict both ETH and BTC returns, especially for intervals of 1 and 2 hours for both models."
  - P-K7-024-b (section 3.2.1): "However, we are aware that the forecasting relationship of USDT net inflows on BTC and ETH returns is not statistically significant for either models for the intervals of 3, 4, or 6 hours."
  - P-K7-024-c (section 3.2.2): "US$ 100 million of USDT net inflows predict 0.11% of ETH return and 0.065% of BTC return in the next hour."
  - P-K7-024-d (abstract): "Third, BTC net inflows generally lack predictive power for BTC returns(except at 4 hours) but are negatively associated with volatility across all intraday intervals."
  - P-K7-024-e (section 2.1): "Our sample period is from December 16, 2017 to January 20, 2023."
- Numeric claims: 0.065% per $100M for BTC next hour (P-K7-024-c); window (P-K7-024-e).
- Tags: new to the program (on-chain stablecoin-flow signal for MBT; F data-native if the data were held); intraday-feasible in horizon (1-2 hours) but needs an on-chain data feed the program does not have; clusters tagged: K7.

### K7-025. Plazuelo Pascual, Tardón Rubio, Toro Cebada and Hernando Veciana (2025), Price Discovery in Cryptocurrency Markets
- Citation: Juan Plazuelo Pascual, Carlos Tardón Rubio, Juan Toro Cebada, Ángel Hernando Veciana, arXiv:2506.08718 (q-fin.TR), 10 June 2025; project report (arfima consulting / UC3M, MCIN grant TED2021-131844B-I00).
- Retrieval: full text, https://arxiv.org/pdf/2506.08718 (92-page report), pdftotext. Read: front matter, chapter 3 section on spot BTC vs CME futures (data, per-event results, section 3.4 conclusions).
- Mechanism: on five volatile 2024 event days, CME Micro Bitcoin futures (MBT) mostly lead Binance spot by Hasbrouck information share and Hayashi-Yoshida lead-lag, with lead times of fractions of a second; Gonzalo-Granger often inconclusive.
- Products and horizon: MBT (the program's traded product) vs Binance BTC spot, tick-by-tick; sub-second lead-lag.
- Cost assumptions: none. Data window: five event days in 2024 (March 5, April 30, August 5 and two others) [full date list unverified].
- Quality tells: consultancy/academic project report, not peer-reviewed; five days only; the lead is 0.055 to 0.15 seconds, far below any horizon Topstep allows; August 5 is an exception.
- Verbatim passages:
  - P-K7-025-a (section 3.3): "The futures data come from the CME Micro Bitcoin Futures (MBT), which represent 1/10th the size of a standard Bitcoin futures contract."
  - P-K7-025-b (event results): "We obtain a lead-lag time of 0.055 seconds, with a lead-lag ratio (LLR) of 1.11. This indicates that the futures market on CME leads the spot BTC market on Binance, with a minimal lag time."
  - P-K7-025-c (event results): "We obtain a lead-lag time of 0.15 seconds, with a lead-lag ratio (LLR) of 1.94."
  - P-K7-025-d (section 3.4): "We find that the futures market seems to lead on most dates according to both the Hasbrouck and Hayashi-Yoshida metrics, with the exception of August 5th."
- Numeric claims: 0.055 s, LLR 1.11; 0.15 s, LLR 1.94 (P-K7-025-b, -c).
- Tags: new to the program (MBT-vs-spot lead-lag measured on MBT itself); intraday-INFEASIBLE as a trading edge (sub-second lead; Topstep prohibits seconds-duration high-rate trading) but informative: MBT is not a slow follower on these days, contra K7-002's 2019 result; clusters tagged: K7.

### K7-026. Pinchuk (2021/2023), Bitcoin Does Not Hedge Inflation
- Citation: Mykola Pinchuk (Simon Business School, University of Rochester), "Bitcoin Does Not Hedge Inflation", working paper dated 30 May 2021, arXiv:2301.10117 (q-fin.PR, 24 January 2023).
- Retrieval: full text, https://arxiv.org/pdf/2301.10117, pdftotext. Read: abstract, introduction, data (MNA, surveys, prices), methodology, main results.
- Mechanism: intraday event study: bitcoin's return in a 30-minute window (10 minutes before to 20 minutes after) around US macro announcements regressed on the Bloomberg-survey surprise; bitcoin falls on inflationary CPI/PPI surprises; growth news has no significant effect; other cryptocurrencies show no reaction.
- Products and horizon: bitcoin (and ETH, XRP, LTC, ADA, BCH), 1-minute prices; 30-minute event window around 8:30 ET releases (07:30 CT). 5-year Treasury note futures used only as a control for the rate channel.
- Cost assumptions: none (event study; contemporaneous response, not a trading rule).
- Data window: bitcoin March 2013 to May 2021; announcements 1 January 2013 to 12 May 2021, 99 to 101 events per announcement type.
- Quality tells: single-author working paper; one significant coefficient (t 2.44) among several announcement groups; contemporaneous (needs the surprise, so a rule must act after the release); pre-CME-dominance and pre-ETF sample.
- Verbatim passages:
  - P-K7-026-a (introduction): "In response to 1 standard deviation inflationary surprise, Bitcoin price decreases by 24 bps (t-statistics 2.44)."
  - P-K7-026-b (methodology): "I estimate all regressions using 30-minutes window around MNA. The window starts 10 minutes before MNA and ends 20 minutes after it and is the most commonly used window in intraday event study literature."
  - P-K7-026-c (data): "Bitcoin has the longest sample, covering the period between March 2013 and May 2021. For each cryptocurrency, I use pricing data, aggregated at 1-minute frequency."
  - P-K7-026-d (results): "These responses are not significant either statistically (t-statistic below 0.5) or economically (less than 2 bps per 1 standard deviation surprise)." (growth-news responses)
  - P-K7-026-e (data): "The sample spans the period between 1 January 2013 and 12 May 2021 and includes 99-101 observations for each type of MNA."
- Numeric claims: 24 bps per 1 SD, t 2.44 (P-K7-026-a); window (P-K7-026-b); samples (P-K7-026-c, -e).
- Tags: port of D.1 family E (scheduled releases) on bitcoin, K7-owned by partition rule 5; intraday-feasible (07:30 CT release inside the MBT session; a post-release surprise-conditioned trade is untested here); clusters tagged: K7.

### K7-027. Mazur (2024), Spot Bitcoin ETF
- Citation: Mazur [given name unverified], SSRN working paper (2024), doi 10.2139/ssrn.4810965.
- Retrieval: ABSTRACT ONLY (Crossref record). SSRN full text blocked.
- Mechanism (abstract only): early spot-ETF era facts: daily ETF net flows are a strong positive predictor of bitcoin price; most of bitcoin's price appreciation is generated outside ETF (NYSE) trading hours; price rises lead abnormal ETF volume; bitcoin ETF inflows coincide with gold ETF outflows (K8 flag).
- Products and horizon: US spot bitcoin ETFs, bitcoin; daily flows; intraday split of returns into ETF-hours vs outside-hours [split definition unverified].
- Cost assumptions: [unverified]. Data window: the first several weeks to months after the January 2024 launch [exact dates unverified].
- Quality tells: very short early sample; "R-squared of 95%" for flows vs price is almost surely a levels or cumulative relation (spurious-regression risk) [unverified]; the hours split is the part relevant to MBT's session.
- Verbatim passages:
  - P-K7-027-a (abstract): "(2) net flows to ETFs are a strong positive predictor of bitcoin price with R-squared of 95%; (3) most of bitcoin price appreciation is generated outside of the ETF trading hours;"
  - P-K7-027-b (abstract): "(1) daily capital flows to spot bitcoin ETFs exceed $500 million or roughly 10,000 bitcoins and surpass daily production of bitcoin by the factor of 5;"
  - P-K7-027-c (abstract): "(5) inflows to bitcoin ETFs witness outflows from gold ETFs."
- Numeric claims: R-squared 95% (P-K7-027-a); $500 million, 10,000 bitcoins, factor 5 (P-K7-027-b).
- Tags: port of D.1 family A (session clock: overnight vs US-hours return split, the "overnight drift" shape) on bitcoin; intraday-feasible only for the US-hours leg (the outside-hours gains need an overnight hold, infeasible); clusters tagged: K7 (gold-ETF item flagged to K8).

### K7-028. Kryńska and Ślepaczuk (2023), Daily and intraday application of various architectures of the LSTM model in algorithmic investment strategies on Bitcoin and the S&P 500 Index
- Citation: Kryńska and Robert Ślepaczuk [first author's given name unverified], SSRN working paper / thesis (2023), doi 10.2139/ssrn.4628806.
- Retrieval: ABSTRACT ONLY (Crossref record). Routes failed: SSRN blocked; OpenAlex lists only the SSRN DOI; no arXiv version found by title search; the Warsaw WNE working-paper page gave no link.
- Mechanism (abstract only): LSTM regression and classification models on past prices generate buy/sell signals for bitcoin (and the S&P 500 separately) at daily, hourly and 15-minute frequencies with walk-forward optimisation; classification works better intraday.
- Products and horizon: bitcoin (spot index or exchange price [unverified]) and the S&P 500 index; daily, hourly, 15-minute.
- Cost assumptions: [unverified]. Data window: out-of-sample 1 February 2014 to 26 August 2022 for bitcoin.
- Quality tells: a thesis; many architectures and hyperparameters (the sensitivity analysis itself shows hyperparameter dependence); walk-forward with many IS/OOS periods is a sound design; the S&P 500 half is a closed product (MES/ES) and is not tagged.
- Verbatim passages:
  - P-K7-028-a (abstract): "All approaches are applied to daily, hourly, and 15-minute data and use a walk-forward optimization procedure with numerous IS and OOS periods. The out-of-sample period for the S&P 500 Index is from February 6, 2014, to August 26, 2022, and for Bitcoin, it is from February 1, 2014, to August 26, 2022."
  - P-K7-028-b (abstract): "We discover that classification techniques beat regression methods on average and that intraday models perform much better in the classification approach, while daily ones produce outperforming results in the regression methods."
- Numeric claims: OOS window (P-K7-028-a); performance figures [unverified].
- Tags: port of D.1 family F (data-native statistics) as an ML precedent for design D15 (one pre-registered ML member per cluster) on bitcoin; intraday-feasible for the 15-minute and hourly variants with a forced 15:08 CT exit [unverified whether positions carry overnight]; clusters tagged: K7.

### K7-029. Yang and Wang (2026), Scheduled FOMC Statements and Cryptocurrency Trading Activity: Intraday Evidence from a 24/7 Market
- Citation: Yang and Wang [given names unverified], SSRN working paper (2026), doi 10.2139/ssrn.6299551.
- Retrieval: ABSTRACT ONLY (Crossref record). SSRN full text blocked.
- Mechanism (abstract only): at scheduled FOMC statements (14:00 New York = 13:00 CT), bitcoin and ether volatility and volume jump in the first post-statement hour; controls rule out seasonality. A volatility-state, not a direction, finding.
- Products and horizon: BTC-USD and ETH-USD hourly (plus Bitfinex replication); first hour after 14:00 ET.
- Cost assumptions: none (event study). Data window: 41 scheduled FOMC statements, January 2021 to January 2026.
- Quality tells: working paper; 41 events; matched-week and hour-matched placebo controls; mean absolute returns, not signed returns.
- Verbatim passages:
  - P-K7-029-a (abstract): "For Bitcoin, mean absolute hourly returns rise from 0.66% in the hour before the announcement to 1.25% in the first post-announcement hour, while USD trading volume increases by a factor of 2.54."
  - P-K7-029-b (abstract): "Combining 41 scheduled FOMC meeting statements (January 2021–January 2026) with hourly BTC–USD and ETH–USD data, we document sharp, concentrated jumps in both volatility and trading activity in the first hour after the 14:00 (New York time) statement release."
  - P-K7-029-c (abstract): "Matched-week controls, hour-matched placebos, and fixed-effects regressions confirm that these jumps are not explained by intraday seasonality or slow-moving time variation."
- Numeric claims: 0.66% to 1.25%, volume x2.54; ETH 0.85% to 1.50%, x2.81 (abstract, checked); 41 events (P-K7-029-b).
- Tags: port of D.1 family E (FOMC) and D (volatility state) on MBT; intraday-feasible (13:00 to 14:00 CT is inside the session; Topstep bars only full-size into the event); clusters tagged: K7.

### K7-030. Mercik and Będowska-Sójka (2026), When Markets Never Sleep: Intraday Liquidity Patterns and Macroeconomic Announcement Effects in Cryptocurrency Trading
- Citation: Mercik and Barbara Będowska-Sójka [first author's given name unverified], SSRN working paper (2026), doi 10.2139/ssrn.7434697.
- Retrieval: ABSTRACT ONLY (Crossref record). SSRN full text blocked.
- Mechanism (abstract only): crypto spreads and depth shortfalls spike at scheduled US macro release minutes (spreads x2.5 to 2.8, fill-failure probability +20 pp for $100,000), regardless of surprise; the release calendar improves out-of-sample spread forecasts by 30% inside announcement windows. An execution-cost state, relevant to MBT market-order slippage around releases.
- Products and horizon: 27 pairs on Binance and Coinbase, 15-minute order-book snapshots.
- Cost assumptions: the paper is itself about costs (volume-weighted spread at $100,000 notional). Data window: [unverified].
- Quality tells: working paper; spot-venue order books, not CME; mechanism (liquidity withdrawal at scheduled minutes) plausibly transfers to MBT's book [transfer is this worker's argument, unverified].
- Verbatim passages:
  - P-K7-030-a (abstract): "Scheduled U.S. macroeconomic releases dominate this calendar: spreads jump by a factor of roughly 2.5 to 2.8 and the probability that the book cannot fill $100,000 rises by 20 percentage points, regardless of how the news surprises."
  - P-K7-030-b (abstract): "The calendar is public, and using it improves out-of-sample spread forecasts by 30% inside announcement windows, and avoids a measurable execution cost."
- Numeric claims: x2.5 to 2.8, +20 pp (P-K7-030-a); 30% (P-K7-030-b).
- Tags: port of D.1 family E as a cost filter (a no-trade or reduced-size window around releases for MBT market orders), not a return signal; intraday-feasible; clusters tagged: K7.

### K7-031. Ben Omrane, Guesmi, Qi and Saadi (2021), The high-frequency impact of macroeconomic news on jumps and co-jumps in the cryptocurrency markets
- Citation: Walid Ben Omrane, Khaled Guesmi, Qianru Qi, Samir Saadi, Annals of Operations Research (2021), doi 10.1007/s10479-021-04353-0; SSRN 3915116 working paper (one source).
- Retrieval: ABSTRACT ONLY (SSRN abstract via Crossref). Routes failed: Springer closed (Unpaywall: not OA), SSRN blocked.
- Mechanism (abstract only): 5-minute jumps in BTC and ETH are linked to scheduled macro news; US releases matter more than German or Japanese ones; ETH jumps three times more often and are more news-sensitive; BTC-ETH co-jumps are rare and tied to a few US releases (unemployment rate, new home sales, housing starts, Beige Book).
- Products and horizon: BTC-USD and ETH-USD, 5-minute; announcement windows.
- Cost assumptions: none (jump study). Data window: 2016 to 2019.
- Quality tells: published (operations-research journal); jump detection, not signed returns; pre-CME-dominance sample.
- Verbatim passages:
  - P-K7-031-a (abstract): "Using 5-min frequency prices for Bitcoin and Ethereum quoted against the U.S. dollar over the 2016-2019 period, we find that intra-day jumps are three times more frequent in Ethereum than in Bitcoin."
  - P-K7-031-b (abstract): "we show that jumps in Ethereum are more sensitive to macroeconomic news than jumps in Bitcoin, and that U.S. news releases exhibit higher influence on jumps in both cryptocurrencies than German and Japanese news announcements."
  - P-K7-031-c (abstract): "We also find that co-jumps among Bitcoin and Ethereum are scarce and tend be associated only with a few U.S. news announcements, and in particular those related to the unemployment rate, new home sales, housing starts and Fed Beige Book."
- Numeric claims: "three times more frequent" (P-K7-031-a); window 2016-2019 (P-K7-031-a).
- Tags: port of D.1 family E (scheduled releases) and D (jump/volatility state) on bitcoin, with ETH as a leg (MET signal-leg use only); intraday-feasible (release times 07:30 and 09:00 CT inside the MBT session); clusters tagged: K7.

### K7-032. CME Group (2019), Analysis of CME CF Bitcoin Reference Rate
- Citation: CME Group education article "Analysis of CME CF Bitcoin Reference Rate" (data through March 2019; author not named on the page; "The views in this report reflect solely those of the author"), https://www.cmegroup.com/education/articles-and-reports/analysis-of-cme-cf-bitcoin-reference-rate.html.
- Retrieval: full text via Wayback raw capture, https://web.archive.org/web/2026id_/https://www.cmegroup.com/education/articles-and-reports/analysis-of-cme-cf-bitcoin-reference-rate.html (cmegroup.com returns HTTP 403 to curl), BeautifulSoup text. Charts and tables are images (not read).
- Mechanism (a venue fact with data): the BRR window (3-4 p.m. London) was chosen as the hour with the most global BTC-USD spot volume; the BRR is replicable by trading evenly across the hour (10 BTC sold uniformly: average tracking error 0.033%, January 2018 to March 2019); it settles CME bitcoin futures and is used for fund NAVs. Supports a settlement-window flow hypothesis for MBT on expiry Fridays (with K7-005 and K7-019).
- Products and horizon: BRR constituent spot exchanges; 60-minute window, 5-minute partitions; CME bitcoin futures final settlement.
- Cost assumptions: not applicable (replication tracking error 0.033%).
- Data window: 14 November 2016 to 31 March 2019 (exchange-exclusion analysis); volume-by-hour chart 1 August to 1 November 2018.
- Quality tells: exchange marketing/education (conflict of interest: CME promotes its benchmark); the page says "3-4pm UTC" in one place and "3-4pm London Time" in another (inconsistent; the methodology K7-019 says London time).
- Verbatim passages:
  - P-K7-032-a (section 1): "The BRR is the underlying rate used to determine the final settlement of the CME Bitcoin Futures Contracts. It also serves as a reference rate in the settlement of financial derivatives based on the bitcoin price, and in the net asset value (NAV) calculation of funds."
  - P-K7-032-b (section 7): "Looking at the number and volume of transactions in the BTC:USD pair, on a global basis, including all spot exchanges, the 15:00 – 16:00 time period sees the greatest number of transactions."
  - P-K7-032-c (section 7): "The below chart shows bitcoin volume across all spot exchanges, by hour, for the three-month period 1 Aug 2018 – 1 Nov 2018. The 3-4pm UTC time period continues to see the most volume and continues to be the calculation window for the BRR"
  - P-K7-032-d (section 8.4): "Average Daily Volume captured by CME CF BRR is circa 2000 BTC since November 16, 2017, 10 BTC = 0.5% of the average observed volume during the BRR 60-minute window ... For the period Jan 2018 – Mar 2019, the average tracking error was 0.033%."
  - P-K7-032-e (summary): "Influencing the BRR would therefore require trading activity during multiple partitions on several exchanges over an extended period, which would prove a costly and an operationally intensive undertaking."
- Numeric claims: 0.033% tracking error and 2000 BTC ADV (P-K7-032-d); over USD 3 billion and 1.8 million trades in the year to March 2019 (summary: "over USD 3 billion worth of bitcoin trades were executed, over 1.8 million trades were included in the BRR based on a total of 607,000 bitcoins traded", checked).
- Tags: new to the program (MBT expiry-day settlement window 09:00-10:00 CT in winter, flow and volume concentration); intraday-feasible; clusters tagged: K7.

### K7-033. CME Group, Micro Bitcoin futures frequently asked questions
- Citation: CME Group education page "Micro Bitcoin futures frequently asked questions", https://www.cmegroup.com/education/articles-and-reports/micro-bitcoin-futures-frequently-asked-questions.html (page dated 30 Mar 2021 in the capture; Wayback capture of 2026).
- Retrieval: full text via Wayback raw capture, https://web.archive.org/web/2026id_/https://www.cmegroup.com/education/articles-and-reports/micro-bitcoin-futures-frequently-asked-questions.html, BeautifulSoup text.
- Mechanism (venue facts): MBT's daily settlement is the VWAP of Globex trades from 3:59:00 to 4:00:00 p.m. ET (14:59 to 15:00 CT), i.e., before the program's 15:08 CT flat time; final settlement is the BRR at 4:00 p.m. London on the last Friday; Globex trades Sunday 5:00 p.m. CT to Friday 4:00 p.m. CT with a daily 4:00-5:00 p.m. CT break; dynamic price limits on a rolling 60-minute look-back. These fix the clock for any settlement-window, expiry or weekend-reopen rule.
- Products and horizon: MBT (0.1 bitcoin [contract size stated elsewhere on the page, not quoted here]); daily and final settlement windows.
- Cost assumptions: not applicable. Data window: not applicable.
- Quality tells: primary exchange document; undated capture, so rule changes after the capture are possible [unverified against the current rulebook, chapter 350, which was not reachable: no Wayback snapshot].
- Verbatim passages:
  - P-K7-033-a (Q14): "Daily settlement for Micro Bitcoin futures are the same as Bitcoin futures. The daily settlement of the Bitcoin futures contract is based on the volume-weighted average price (VWAP) of CME Globex trades between 3:59:00 p.m. and 4:00:00 p.m. Eastern Time."
  - P-K7-033-b (contract specs): "CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. ET (5:00 p.m. - 4:00 p.m. CT) with a 60-minute break each day beginning at 5:00 p.m. ET (4:00 p.m. CT)"
  - P-K7-033-c (contract specs): "Trading terminates at 4:00 p.m. London time on the last Friday of the contract month. If that day is not a business day in both the U.K. and the US, trading terminates on the preceding day that is a business day for both the U.K. and the U.S."
  - P-K7-033-d (Q16): "The final settlement value is based on the CME CF Bitcoin Reference Rate (BRR) at 4:00 p.m. London time on the expiration day of the futures contract."
  - P-K7-033-e (Q15): "During the trading day, the dynamic variant is applied in rolling 60-minute look-back periods to establish dynamic lower and upper price fluctuation limits"
- Numeric claims: settlement window 3:59:00-4:00:00 p.m. ET (P-K7-033-a); hours (P-K7-033-b); termination (P-K7-033-c); minimum block 10 contracts (Q12 "The minimum block threshold is 10 contracts.", checked).
- Tags: new to the program (MBT daily-settlement minute 14:59-15:00 CT and expiry-day termination 10:00 CT in normal weeks: clock facts for settlement-window rules; the Sunday 17:00 CT reopen for weekend-gap rules); intraday-feasible (all windows before 15:08 CT); clusters tagged: K7.

### K7-034. CME Group, BTIC Transactions on Cryptocurrency Futures
- Citation: CME Group education page "BTIC Transactions on Cryptocurrency Futures", https://www.cmegroup.com/education/articles-and-reports/btic-transactions-on-cryptocurrency-futures.html (undated in the text read).
- Retrieval: full text via Wayback raw capture (fetched with --compressed), https://web.archive.org/web/2026id_/https://www.cmegroup.com/education/articles-and-reports/btic-transactions-on-cryptocurrency-futures.html.
- Mechanism (venue facts): bitcoin futures (BTC and, per the ticker list, the micros [unverified for MBT specifically]) can be traded at a basis to the CME CF reference rate for London (BRR), New York (BRRNY, 4:00 p.m. ET = 15:00 CT) or APAC close; a BTIC position is priced at the published rate plus the basis. Whoever sells or buys BTIC and hedges must trade spot or futures through the one-hour reference window (per K7-019's replication design), which is a scheduled flow inside MBT's day session (BRRNY window 14:00-15:00 CT).
- Products and horizon: CME cryptocurrency futures; reference windows 3-4 p.m. London / New York / Hong Kong.
- Cost assumptions: not applicable. Data window: not applicable.
- Quality tells: primary venue document; describes the instrument, not the size of hedging flows (no volume data read) [flow size unverified].
- Verbatim passages:
  - P-K7-034-a: "For Cryptocurrency futures, the basis is defined as the difference in price between the futures contract and the respective CME CF Reference Rate."
  - P-K7-034-b: "Market participants interested in accessing a Cryptocurrency futures contract through a BTIC transaction have the flexibility to the trade the respective cryptocurrency futures contract against a reference rate calculated at 4:00 p.m. London time, 4:00 p.m. New York time or 4:00 p.m. Hong Kong/Singapore time. Each reference rate will have its own BTIC ticker."
  - P-K7-034-c: "a BTIC on Bitcoin futures against New York Close transaction (ticker BNB) executed by 4:00 p.m. New York time will be transposed to a futures price against that day’s respective CME CF Reference Rate New York."
  - P-K7-034-d: "BTIC transactions are not permitted on the last trade date of an expiring futures contract."
- Numeric claims: none beyond times.
- Tags: new to the program (reference-window hedging flow at 14:00-15:00 CT via BRRNY; London window on expiry days); intraday-feasible; clusters tagged: K7.

### K7-036. CME Group (2026), Aligning Cryptocurrency Derivatives with Spot Markets: Measuring the 24/7 Trading Opportunity
- Citation: CME Group article (2026; author not named in the text read), https://www.cmegroup.com/articles/2026/aligning-cryptocurrency-derivatives-with-spot-markets-measuring-the-247-trading-opportunity.html.
- Retrieval: full text via Wayback, https://web.archive.org/web/2026/https://www.cmegroup.com/articles/2026/aligning-cryptocurrency-derivatives-with-spot-markets-measuring-the-247-trading-opportunity.html (three retries after Wayback timeouts), BeautifulSoup text. Figures are images.
- Mechanism (venue fact plus descriptive data): CME announced a move of its cryptocurrency futures and options to 24/7 trading starting 29 May 2026, pending regulatory review. Until then the Friday 4:00 p.m. CT close to Sunday 5:00 p.m. CT reopen produced "gap" risk (example: a $10,000 gap after the 2 March 2025 Strategic Crypto Reserve announcement). Weekend spot volatility runs about 75% of weekday levels. For the program: any weekend-gap or Sunday-reopen rule on MBT is confined to dates before the 24/7 switch (if it took effect), and the Topstep session clock for MBT after that date needs checking [whether the switch took effect, and how TopstepX treats MBT hours after it, unverified].
- Products and horizon: CME crypto futures and options (MBT included by implication, "our Cryptocurrency futures and options"); spot bitcoin volatility (Parkinson, hourly high-low scaled to daily).
- Cost assumptions: not applicable. Data window: 1 January 2020 to 8 March 2026 (volatility distribution).
- Quality tells: exchange marketing for a product change (conflict of interest); descriptive volatility, not returns; announcement conditional on regulatory review.
- Verbatim passages:
  - P-K7-036-a: "Starting on May 29, 2026, pending regulatory review, we are transitioning our Cryptocurrency futures and options to 24/7 trading."
  - P-K7-036-b: "Historically, holding our Cryptocurrency futures and options positions over the weekend has exposed traders to "gap” risk. This price dislocation, defined as the variance between the Friday session close and the Sunday session open, occurs because underlying spot assets continue to trade while the crypto market is paused. A significant example occurred following the announcement of the U.S. Strategic Crypto Reserve on March 2, 2025: as $300 billion in market capitalization was added to spot markets, a $10,000 gap emerged in Bitcoin futures by the time trading resumed."
  - P-K7-036-c: "Notably, weekend volatility has consistently remained at approximately 75% of weekday levels, confirming that price discovery remains robust even while our markets were closed."
  - P-K7-036-d: "The chart (Figure 5) captures the full range of daily volatility from January 1, 2020, to March 8, 2026. The “X” marks the average daily move, which stands at 3.10% for weekdays and 2.33% for weekends."
  - P-K7-036-e: "As over $19 billion in long positions were liquidated following the Friday close, spot bitcoin daily volatility reached 7.83%. This figure significantly exceeded the 2.14% recorded earlier that day while regulated markets were open."
- Numeric claims: 29 May 2026 (P-K7-036-a); $10,000 gap, $300 billion (P-K7-036-b); 75% (P-K7-036-c); 3.10%/2.33%, medians 2.66%/1.91% (P-K7-036-d and the following paragraph "a typical weekday move of 2.66% compared to 1.91% on weekends", checked); 7.83% vs 2.14% (P-K7-036-e).
- Tags: new to the program (weekend-gap mechanism on MBT, readable weekend spot move traded after the Sunday 17:00 CT reopen, and its expiry under 24/7 trading); intraday-feasible only as a post-reopen same-day trade and only on pre-switch dates; flag for the lead: the 24/7 switch also changes the brief's session assumptions for MBT; clusters tagged: K7.

### K7-037. CME Group, TAS on Bitcoin and Micro Bitcoin futures: Frequently Asked Questions
- Citation: CME Group FAQ, https://www.cmegroup.com/articles/faqs/tas-on-bitcoin-and-micro-bitcoin-futures-faq.html (undated in the text read).
- Retrieval: full text via Wayback, https://web.archive.org/web/2026/https://www.cmegroup.com/articles/faqs/tas-on-bitcoin-and-micro-bitcoin-futures-faq.html, BeautifulSoup text.
- Mechanism (venue fact): Trading-at-Settlement exists for MBT (ticker TBM) and BTC (TBT): participants trade at 0 or +/- 20 ticks to the yet-unknown daily settlement (VWAP 3:59-4:00 p.m. ET = 14:59-15:00 CT, per K7-033); the counterparties who fill TAS offset in the settlement minute. A settlement-minute flow exists in MBT before 15:08 CT; its size and direction are not reported here [unverified].
- Products and horizon: BTC and MBT futures; settlement minute.
- Cost assumptions: not applicable. Data window: not applicable.
- Quality tells: primary venue document; no volume data.
- Verbatim passages:
  - P-K7-037-a (Q1): "Trading at Settlement (TAS) functionality allows market participants to enter a trade at a spread to the yet-to-be-determined daily settlement price of the underlying futures contract calculated at 4:00 p.m. Eastern Time (ET), for subsequent clearing into the existing futures contract. TAS enables clients to transact at or near the futures settlement price, making it particularly useful when replicating an index."
  - P-K7-037-b (Q2): "TAS: TBM" and "TAS: $1 per bitcoin = $5.00 per contract. Zero or +/- 20 ticks."
  - P-K7-037-c (Q3): "TAS transactions are at a spread, or basis, to the yet-to-be-determined daily settlement price of the underlying futures contract. Basis Trade at Index Close (BTIC) transactions are at a spread, or basis, to the corresponding underlying reference rate."
- Numeric claims: +/- 20 ticks (P-K7-037-b).
- Tags: new to the program (MBT settlement-minute flow, the K4-style TAS/settlement-window mechanism ported to K7); intraday-feasible (14:59-15:00 CT, but the 8-minute gap to 15:08 CT leaves little room for a post-settlement reversal trade); clusters tagged: K7.

### K7-038. CME Group (2024), Bitcoin Friday Futures: Your New BFF
- Citation: CME Group article, https://www.cmegroup.com/articles/2024/bitcoin-friday-futures-your-new-bff.html (2024 per the URL; author not named in the text read).
- Retrieval: full text via Wayback, https://web.archive.org/web/2026/https://www.cmegroup.com/articles/2024/bitcoin-friday-futures-your-new-bff.html, BeautifulSoup text.
- Mechanism (venue fact with a volume statistic): BRRNY (3-4 p.m. New York, 14:00-15:00 CT) is the benchmark for six of the ten first US spot bitcoin ETFs; since those ETFs launched, more than 20% of a day's BTC and MBT notional volume trades in the hour to 4:00 p.m. New York. Weekly BFF contracts (0.02 BTC) settle to BRRNY every Friday. This confirms the ETF-NAV flow behind the BRRNY window that K7-019 left unverified and puts a concentration of MBT volume in 14:00-15:00 CT, before the 15:08 CT flat time.
- Products and horizon: BFF, BTC, MBT; the 14:00-15:00 CT hour; weekly Friday settlement.
- Cost assumptions: not applicable. Data window: not stated for the ">20%" figure [period unverified].
- Quality tells: exchange marketing for a product launch; a single volume share without a period or method.
- Verbatim passages:
  - P-K7-038-a: "The BRRNY is the benchmark used by six out of the 10 new spot bitcoin exchange-traded funds (ETFs) that hold bitcoin directly. Since the launch of these popular ETFs, volume for BTC and MBT has increased in the hour leading to 4:00 p.m. New York time where now more than 20% of a day’s notional volume is transacted."
  - P-K7-038-b: "These shorter-dated contracts expire to the CME CF Bitcoin Reference Rate New York Variant (BRRNY) every Friday at 4:00 p.m. New York time"
  - P-K7-038-c: "Each contract represents 1/50 (0.02) of a bitcoin"
  - P-K7-038-d: "The BRRNY represents the aggregated, executed U.S. dollar trade flow of bitcoin from major cryptocurrency spot exchanges between 3:00 p.m. and 4:00 p.m. New York time."
- Numeric claims: six of ten ETFs, > 20% of daily notional in the last hour (P-K7-038-a); 0.02 BTC (P-K7-038-c).
- Tags: new to the program (ETF-NAV benchmark hour 14:00-15:00 CT: volume and flow concentration in MBT; weekly Friday BFF settlement adds a Friday flow); intraday-feasible; clusters tagged: K7.

### K7-039. Padyšák and Vojtko (Quantpedia, 18 February 2022), Are There Seasonal Intraday or Overnight Anomalies in Bitcoin?
- Citation: Matúš Padyšák and Radovan Vojtko, Quantpedia blog, 18 February 2022, https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/ (the related Quantpedia strategy page "intraday-seasonality-in-bitcoin" names its source paper as Padyšák and Vojtko, "Seasonality, Trend-following, and Mean reversion in Bitcoin" (SSRN; not read, SSRN blocked); blog, strategy page and SSRN paper are one source. The strategy page states the rule as "open a long position in the BTC at 22:00 (UTC +0) and hold it for two hours", the blog as buy 21:00, sell 23:00: an hour-labelling difference, same two bars).
- Retrieval: full text via Wayback, https://web.archive.org/web/2026/https://quantpedia.com/are-there-seasonal-intraday-or-overnight-anomalies-in-bitcoin/ (direct quantpedia.com returns "Access Forbidden"). Charts are images.
- Mechanism: hour-of-day returns of BTC on Gemini: the 22:00 and 23:00 UTC hours are the strongest (significant at 5%), 03:00-04:00 UTC weakest (insignificant); a rule long 21:00 to 23:00 UTC; on NYSE-open days most of the return accrues outside 10:00-16:00 New York time.
- Products and horizon: Gemini BTC-USD hourly; 2-hour hold.
- Cost assumptions: none stated in the text read.
- Data window: 9 October 2015 to 3 February 2022.
- Quality tells: practitioner blog, single exchange, 24 hourly cells tested (multiplicity) with the best two chosen in-sample and then backtested on the same data (no out-of-sample); UTC clock ignores DST.
- Verbatim passages:
  - P-K7-039-a: "This research aims to examine some possible seasonality effects in BTC using the hourly data from the Gemini exchange during 9.10.2015 – 3.2.2022."
  - P-K7-039-b: "Nonetheless, the negative returns are insignificant, while several positive returns are statistically significant on the 5% level. From both statistical and economic points of view, the returns 22:00 and 23:00 dominate."
  - P-K7-039-c: "Based on the previous results, we propose a simple seasonality strategy with a simple rule: buy Bitcoin at 21:00 (UTC +0) and sell it at 23:00 (UTC +0)."
  - P-K7-039-d: "the annualized volatility is 20.93%, and the maximum drawdown is only -22.45%. The annualized return is 33%."
  - P-K7-039-e: "The intraday return is relatively small and volatile, and the performance is driven mostly by the overnight component." (NYSE-open days; "intraday" = 10:00-16:00 New York)
- Numeric claims: 33% annualised, 20.93% vol, -22.45% MDD (P-K7-039-d); window (P-K7-039-a).
- Tags: port of D.1 family A (session clock) on bitcoin; intraday-INFEASIBLE for MBT: 21:00-23:00 UTC is 15:00-17:00 CT in winter and 16:00-18:00 CT in summer, after the 15:08 CT flat time and across the CME daily break; the US-hours-vs-overnight split agrees with K7-027 (gains accrue outside US hours), which is negative for a day-session long bias; clusters tagged: K7.

### K7-040. Dujava (Quantpedia, 12 November 2024), How To Profitably Trade Bitcoin’s Overnight Sessions?
- Citation: Cyril Dujava, Quantpedia blog, 12 November 2024, https://quantpedia.com/how-to-profitably-trade-bitcoins-overnight-sessions/.
- Retrieval: full text via Wayback, https://web.archive.org/web/2026/https://quantpedia.com/how-to-profitably-trade-bitcoins-overnight-sessions/. Charts and performance tables are images.
- Mechanism: splitting Gemini BTC hourly returns into a US "daily session" (10 a.m. to 4 p.m. EST on NYSE days) and "overnight" (all other hours): up to about 2021 the day session carried positive returns; since then most returns accrue overnight (the equity-style overnight effect), and returns concentrate Friday close to Monday open, Monday-Tuesday and Tuesday-Wednesday nights. The proposed rule (buy at NYSE close when BTC is at a 10-day high, hold to the next open, only on those nights) is overnight-only.
- Products and horizon: Gemini BTC-USD hourly; NYSE-clock sessions; overnight holds.
- Cost assumptions: none stated in the text read.
- Data window: 8 October 2015 to 15 October 2024; in-sample to October 2021 (BITO launch), out-of-sample after (the author calls the split "very arbitrary").
- Quality tells: practitioner blog; the out-of-sample split is chosen on an event; multiple filters (MAX(10), nights of week) combined after inspection.
- Verbatim passages:
  - P-K7-040-a: "We define the daily session as performance between 10 am EST and 4 pm EST during trading days when the NYSE exchange is opened. All of the hours out of this interval are defined as overnight sessions."
  - P-K7-040-b: "Initially (until around 2021), the performance of the BTC during daily sessions was significantly positive ... returns over the daily sessions diminished, and most of the BTC returns since 2021 were realized during the nightly sessions."
  - P-K7-040-c: "So Bitcoin moves to the positive territory mainly between Friday’s close and Monday’s open (so over the weekend), between Monday’s close and Tuesday’s open, and between Tuesday’s close and Wednesday’s open."
  - P-K7-040-d: "Our analysis is based on the hourly BTC data from the Gemini Data page in intervals ranging from 2015-10-08 to 2024-10-15."
  - P-K7-040-e: "most returns of the MAX(10) strategy throughout history, both in-sample and out-of-sample, are generated during the overnight trading session (from close to open)"
- Numeric claims: window (P-K7-040-d); "over 35% performance with a minimal -12% maximal drawdown" for MAX(10) out of sample (text line on the MAX strategy, checked); other figures in images [unverified].
- Tags: port of D.1 family A (overnight vs day session) and B (10-day MAX breakout, family B/H) on bitcoin; intraday-INFEASIBLE as specified (overnight holds); informative negative for day-session long bias in MBT after 2021 (agrees with K7-027, K7-039); clusters tagged: K7.

### K7-041. Dujava (Quantpedia, 8 September 2025), Surprisingly Profitable Pre-Holiday Drift Signal for Bitcoin
- Citation: Cyril Dujava, Quantpedia blog, 8 September 2025, https://quantpedia.com/surprisingly-profitable-pre-holiday-drift-signal-for-bitcoin/.
- Retrieval: full text via Wayback, https://web.archive.org/web/2026/https://quantpedia.com/surprisingly-profitable-pre-holiday-drift-signal-for-bitcoin/. Equity curves and tables are images.
- Mechanism: bitcoin (BITO ETF, with bitcoin futures as the 2018-2021 proxy) is bought at the close before a US public holiday and sold at the close of the day after; a variant enters at the close on days within D-5 to D+5 of a holiday when price is at an N-day high (N = 5, 10, 20) and exits at the next close.
- Products and horizon: BITO / CME bitcoin futures proxy; daily close-to-close, multi-day holds through the holiday.
- Cost assumptions: none stated in the text read.
- Data window: January 2018 to June 2025.
- Quality tells: practitioner blog; few holidays per year (small event count); variants chosen among N values and windows; "Sharpe ratio over 2.0 and Calmar ratio over 7.0 (for the 10-day variant)" without costs or significance tests.
- Verbatim passages:
  - P-K7-041-a: "Data span daily closing prices of Bitcoin in the form of BITO ETF from January 2018 to June 2025, sourced from our internal database (2018-2021 as futures proxy, 2021 – 2025 as ETF itself)."
  - P-K7-041-b: "we can define a simple trading strategy that buys crypto on the day preceding the holiday (D-1), holds through the holiday, and liquidates at the close of the day after the holiday (D+1)."
  - P-K7-041-c: "For each qualifying date, one enters a long position at the close and liquidates at the next trading day’s close."
  - P-K7-041-d: "Still, the Sharpe ratio over 2.0 and Calmar ratio over 7.0 (for the 10-day variant) look really attractive for us."
- Numeric claims: Sharpe > 2.0, Calmar > 7.0 (P-K7-041-d); window (P-K7-041-a).
- Tags: port of D.1 family E (pre-holiday) with B/H (N-day high) on bitcoin; intraday-INFEASIBLE (close-to-close holds through holidays and nights); only a same-day pre-holiday session variant would be feasible, untested here; clusters tagged: K7.

### K7-042. Pagani (Concretum Group, 2025/2026), Seasonality in Bitcoin Intraday Trend Trading
- Citation: Alberto Pagani (Concretum Group), "Seasonality in Bitcoin Intraday Trend Trading", Concretum Group research article, https://concretumgroup.com/seasonality-in-bitcoin-intraday-trend-trading/ (date not shown in the text read; it cites the SSRN paper revised 2 October 2025, so it is later than that). Found through Quantocracy (container 11, discovery only); the article is the primary source for this finding.
- Retrieval: full text, direct curl of the article page, BeautifulSoup text. Figures are images.
- Mechanism: an ensemble of high-frequency trend-following models on bitcoin (long-short, volatility-targeted to 20%) earns most of its return from about Sunday 7:00 p.m. New York time (18:00 CT) for roughly 24 hours, aligned with the Monday Asian cash open ("Monday Asia Open Effect"); US Sunday morning is choppy and mean-reverting. The effect strengthened after mid-2020. For MBT: the window starts one hour after the Sunday 17:00 CT CME reopen and lies inside Monday's CME trade date, which ends before 15:08 CT on Monday, so it is reachable without an overnight hold (pre-24/7 dates, see K7-036).
- Products and horizon: bitcoin (venue not stated in the text read [unverified]); high-frequency trend models (intraday); intraweek seasonality of strategy returns.
- Cost assumptions: gross of fees ("gross-of-fees Sharpe ratio of approximately 1.6").
- Data window: 2018 to 2025 (split 2018-2020H1 vs 2020H2-2025).
- Quality tells: practitioner research by a firm that trades such models; ensemble and parameters undisclosed; seasonality found by inspection of a figure (no test statistics in the text); gross of costs; companion SSRN paper (Zarattini, Pagani, Barbon, "Catching Crypto Trends", SFI Research Paper 25-80) covers multi-day trends and was not read (SSRN blocked; multi-day holds are infeasible anyway).
- Verbatim passages:
  - P-K7-042-a: "Over the 2018–2025 period, this benchmark produced compelling results, achieving a gross-of-fees Sharpe ratio of approximately 1.6. For comparison, a volatility-targeted long-only Bitcoin portfolio (20% target volatility) delivered a Sharpe ratio just below 0.8"
  - P-K7-042-b: "our intraday trend benchmark delivers strongly positive returns starting on Sunday at around 7:00 PM New York time, with performance remaining elevated for roughly the next 24 hours into Monday. Notably, this upswing closely aligns with the Monday open of Asian cash equity markets"
  - P-K7-042-c: "In contrast, US Sunday morning is associated with negative benchmark performance, consistent with choppier price action, weaker trend persistence, and a higher propensity for mean reversion."
  - P-K7-042-d: "When splitting the sample into pre- and post-mid-2020 periods, the “Monday Asia Open Effect” becomes substantially more pronounced in the latter subsample."
  - P-K7-042-e: "To address this question, we constructed a long–short portfolio based on an ensemble of multiple high-frequency trend-following models. ... portfolio exposure is volatility-scaled to target an annualized volatility of 20%."
- Numeric claims: Sharpe about 1.6 gross vs just below 0.8 (P-K7-042-a); 7:00 p.m. New York start, about 24 hours (P-K7-042-b); 20% vol target (P-K7-042-e).
- Tags: port of D.1 family C (intraday trend/momentum) conditioned on family A/E (session clock: Sunday-evening reopen / Monday) on bitcoin; new to the program as a MBT post-reopen trend window; intraday-feasible (Sunday 18:00 CT to Monday 15:08 CT is one CME trade date); clusters tagged: K7.

### K7-043. Quant Fiction (2018), Bitcoin Seasonality: Fooled by Randomness
- Citation: "Quant Fiction" (pseudonymous blog), "Bitcoin Seasonality: Fooled by Randomness", 28 September 2018, http://quantfiction.com/2018/09/28/bitcoin-seasonality-fooled-by-randomness/. Found via Quantocracy (container 11).
- Retrieval: full text via Wayback 2019 capture, https://web.archive.org/web/2019/http://quantfiction.com/2018/09/28/bitcoin-seasonality-fooled-by-randomness/ (the live site returned "Not Acceptable!" from Mod_Security; the 2020 capture was that error page). Passed on an ambiguous title; the full text shows a month-of-year study, so it carries no intraday mechanism.
- Mechanism: month-of-year Sharpe of daily bitcoin returns (November best), tested against a permutation distribution of the MAXIMUM monthly Sharpe (5,000 shuffles) to correct for picking the best month; the best month does not clear the 95th percentile.
- Products and horizon: spot bitcoin ("XBT") daily bars; monthly bins.
- Cost assumptions: none. Data window: from 2012 to September 2018 ("dates back only to 2012").
- Quality tells: pseudonymous practitioner post; the value is the max-statistic permutation design (a multiple-comparisons control relevant to any seasonality member), not the effect.
- Verbatim passages:
  - P-K7-043-a: "It’s important to use the greatest value as a benchmark, because the only reason we’ve selected a given month is by looking at all of them and selecting the best. We had no pre-existing thesis for why prices should behave a certain way at a certain time."
  - P-K7-043-b: "95th percentile: 5.12 Maximum Observed Sharpe Ratio: 5.10"
  - P-K7-043-c: "While we can’t technically reject the null with 95% confidence, (1) it’s not a magical hard limit, and (2) we’re extremely close."
  - P-K7-043-d: "We’re dealing with a limited sample size here. The price series used for this testing dates back only to 2012"
- Numeric claims: 5.12 vs 5.10, 5,000 permutations (P-K7-043-b; code "for i in range(5000)", checked).
- Tags: port of D.1 family E (month-of-year) on bitcoin: negative; intraday-infeasible as an effect (monthly holding); methodological precedent only; clusters tagged: K7.


## 4. Flags for K8

- K8 flag | Conlon, Corbet and Oxley (2024), Investor Sentiment, Unexpected Inflation, and Bitcoin Basis Risk, JFM 10.1002/fut.22541 | legs: VIX-family tail risk (K1 signal) and CME bitcoin basis (K7) | extreme equity-volatility sentiment coincides with negative bitcoin basis, stronger in inflation-surprise periods (abstract only seen; sentiment framing).
- K8 flag | Kose et al. (2024), The Bitcoin price and Bitcoin price uncertainty, JFM 10.1002/fut.22487 | legs: VIX, dollar index, gold, oil (K1/K3/K5/K4) and bitcoin (K7) | global-factor drivers of the bitcoin price.
- K8 flag | Aalborg et al. (2018), What Can Explain the Price, Volatility and Trading Volume of Bitcoin?, SSRN 3233977 | legs: VIX (K1) and bitcoin (K7) | daily drivers.
- K8 flag | Mourey et al. (2025), A Crypto-Stock Weekend Effect: Predicting Monday Stock Returns Using Weekend Cryptocurrency Returns, SSRN 5382090 | legs: weekend crypto returns (K7 signal) and Monday equity index returns (K1) | weekend crypto move as an equity-open signal.
- K8 flag | "Cryptocurrencies in the Balance Sheet: Insights from (Micro)Strategy - Bitcoin Interactions" (arXiv 2505.14655) | legs: bitcoin (K7) and treasury-holding equities (single stocks, off-universe) | crypto-equity link.
- K8 flag | Krause (2026), Bitcoin Financialization and Market Correlation: Evidence from the Spot ETF Era, SSRN 6925619; Lee (2024), Shifting Dynamics: Bitcoin Spot ETF Approval and Bitcoin's Relationships with Financial Markets, SSRN 5033066 | legs: bitcoin (K7) and equity indices / other assets (K1 and others) | post-ETF correlation change.
- K8 flag | Shakourloo (2026), Lead-Lag Dynamics and Nonlinear Spillover between Bitcoin and Global Macro Variables, SSRN 6377464 | legs: bitcoin (K7) and macro/market variables (dollar, rates, equities) | lead-lag.
- K8 flag | Joo (2023), Hedging Bitcoin with Commodity Futures: Copper, Gas, Gold, and Crude Oil, SSRN 4355765 | legs: bitcoin (K7) and HG/NG/GC/CL (K5/K4) | hedge ratios, daily.
- K8 flag | Mazur (2024), Spot Bitcoin ETF, SSRN 4810965 (K7-027) | legs: bitcoin ETF inflows (K7) and gold ETF outflows (K5 exposure) | flow substitution between bitcoin and gold.
- K8 flag | CME Group economic research: "Why is bitcoin moving in tandem with equities" (2025), openmarkets "Why Bitcoin's Relationship with Equities Has Changed" (2025), "Is Bitcoin's Digital Gold Narrative Losing Its Shine" (2026) | legs: bitcoin (K7) and equity indices (K1) / gold (K5) | correlation regime commentary.
- K8 flag | Pinchuk (K7-026) uses 5-year Treasury note futures (K2) only as a control for the rate channel of bitcoin's CPI response; if K8 studies rates-to-crypto transmission, it is a source (already read by K7; passages in K7-026).
- K8 flag | Quantpedia blog items "Bitcoin is not the new gold", "Dual momentum allocation between physical gold and bitcoin", "When crypto stopped diversifying: the ETF regime shift", "Are cryptocurrencies exposed to traditional factor risks", "Trading the spread: bitcoin ETFs vs cryptocurrency-infrastructure ETFs" | legs: bitcoin (K7) and gold (K5) / equities (K1) | cross-asset allocation and spread ideas, daily or longer (not read).

## 5. Registry ids appended by K7

K7-001, K7-002, K7-003, K7-004, K7-005, K7-006, K7-007, K7-008, K7-009, K7-010, K7-011, K7-012, K7-013, K7-014, K7-015, K7-016, K7-017, K7-018, K7-019, K7-020, K7-021, K7-022, K7-023, K7-024, K7-025, K7-026, K7-027, K7-028, K7-029, K7-030, K7-031, K7-032, K7-033, K7-034, K7-035, K7-036, K7-037, K7-038, K7-039, K7-040, K7-041, K7-042, K7-043 (43 lines; all K7 claims are single appended lines; K7-026 had its authors field corrected in place from a placeholder to "Pinchuk" within a minute of claiming.)
