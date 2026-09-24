# Stage E.0 Task 3: research log, cluster K1 (equity index)

Worker: ClusterReader-K1-OpusHigh (Opus, high). Pre-filtering and verbatim extraction only: no ranking, no hypotheses, no conclusions.

## 0. Header

- Cluster: K1 equity index. Traded: MNQ, M2K, MYM (NQ, RTY, YM as alternate vehicles). ES and MES as legs only. NKD dropped by D1 (not researched; NKD items logged in one line).
- Start 2026-09-23 21:25 PDT. Usage-limit pause 21:58 to 01:10 PDT (not work time). Resumed 2026-09-24 01:12 PDT. End 01:24 PDT. Work time about 45 minutes.
- Stop reason: the container branch of the stopping rule. Every container 1 to 11 had at least 4 distinct logged queries or listings, and its last 2 produced no new passing item (section 1). The 60-full-text branch was not reached (15 full-text reads).
- Counts:
  - considered: 27 passed items (K1-001 to K1-027) plus 95 rejection rows (R-K1-001 to R-K1-095). Some rejection rows group several same-reason items, so the item count is higher than 122; the rows name each item.
  - passed pre-filter: 27.
  - full-text read: 15 (K1-002, 003, 009, 013, 014, 017, 018, 019, 020, 021, 022, 023, 024, 026, 027). Of these, 8 are exchange or vendor web pages (CME, Databento) and 1 is a one-page high-school abstract (K1-013).
  - abstract-only: 12 (K1-001, 004, 005, 006, 007, 008, 010, 011, 012, 015, 016, 025). Each one's failed routes are named in its entry.
  - blocked: the same 12. SSRN returned 403 to curl and WebFetch, and Wayback held no PDF copies. The Wiley, JFQA, JoD and JPM PDFs were not open access.
  - [unverified] markers in section 3: 24.
- Panel sources: none newly claimed by K1. Seen and not re-read: K2-007, K2-015, K3-007, K3-030, K3-035, K3-040, K4-008 (their [K1] passages are in those logs), K3-034 ("Drift Begone!"), and K4-050 (Fetna ORB on nine futures including equity indices; see R-K1-078).
- D.1 rows that matter to K1 (cited, not re-read): A10 (Baltussen et al., hedging demand and intraday momentum, includes NQ), A14/B5/C5 (Mesfin, MNQ OHLCV falsification), E10 (CME S&P 500 rebalance article), E13/E14 (rebalancing and passive-flow pressure), C16 (end-of-day reversal), B4/B8 (ORB on index futures).
- Registry note: the K1-001 claim line carries a wrong DOI (10.1111/1540-6261.00616). The correct DOI is 10.1046/j.1540-6261.2003.00609.x. The registry is append-only, so the correction is recorded in the K1-001 entry.
- Source conflict for the lead: K1-018 (CME, 2025) dates the second 2026 Russell reconstitution to November, and K1-023 (CME, 2026) dates it to December.
- Researched without WebSearch or Firecrawl (session budget exhausted). Discovery used Crossref, arXiv, Semantic Scholar (heavily rate-limited, used for single lookups), Unpaywall, Wayback CDX listings and site searches. OpenAlex was over its daily quota.

## 1. Container table

Times are PDT, taken from checkpoint timestamps. Containers overlapped in time, because some candidates surfaced in one container's query and were read under another.

| # | Container | Queries or listings (distinct, logged) | Start | Pre-filter done | Full-text done | Passed items (registry id) | Last 2 queries new pass? |
|---|---|---|---|---|---|---|---|
| 1 | Journal of Futures Markets (Crossref ISSN 1096-9934 filter; Semantic Scholar venue filter; unfiltered Crossref) | JFM filter: "Nasdaq-100 futures S&P 500 futures lead lag"; "Russell 2000 futures"; "E-mini futures price discovery Nasdaq Dow"; "stock index futures spread intermarket Nasdaq Russell". S2 venue filter, same 4 queries: all returned no data or 429 (failed route). Unfiltered Crossref: "lead-lag relationship among stock index futures S&P 500 Nasdaq-100 Dow Jones Russell 2000"; "price discovery E-mini Nasdaq-100 E-mini S&P 500 intraday"; "small-cap large-cap index futures lead lag Russell"; "stock index futures pairs trading spread mean reversion Nasdaq S&P". JFM filter from 2005: "E-mini Russell 2000 Nasdaq-100 Dow intraday returns"; "stock index futures intermarket spread small cap large cap" | 21:25 | 21:38 | 21:45 (resumed 01:20) | K1-002, K1-003, K1-012 (and K1-005, K1-006, K1-007, K1-004 surfaced here) | no, no |
| 2 | Index reconstitution and rebalance | Crossref: "Russell reconstitution day closing auction price pressure intraday"; "S&P 500 index rebalance closing auction index futures"; "Nasdaq-100 special rebalance reconstitution intraday"; "index reconstitution futures price impact rebalancing day"; "Russell reconstitution"; "Russell 2000 annual reconstitution returns liquidity June"; "market-on-close imbalance closing auction Nasdaq NYSE price reversal"; "S&P 500 index additions deletions intraday price pressure effective day close"; "leveraged ETF rebalancing end of day index futures returns last hour"; "leveraged inverse ETF rebalancing Nasdaq-100 close momentum"; "gamma hedging dealer positioning intraday momentum index futures close"; "Nasdaq-100 annual reconstitution December QQQ additions deletions"; "Russell 2000 futures intraday return reconstitution day" | 21:33 | 21:36 (resumed 01:14) | 21:42 (abstract-only) | K1-004, K1-011 | no, no |
| 3 | High-frequency lead-lag (arXiv, Crossref, Semantic Scholar) | arXiv: '"lead-lag" futures Nasdaq'; '"E-mini" "lead-lag"'; '"Russell 2000" futures'; '"index futures" "lead-lag" "high frequency"'; '"Nasdaq" "S&P" "lead-lag"'; '"equity index futures" intraday'; '"index rebalancing" "closing auction"'; 'reconstitution Russell'; '"E-mini" "Nasdaq"'; 'ti:"lead-lag" cat:q-fin.TR'; 'ti:"lead-lag" cat:q-fin.ST'; '"small cap" "large cap" intraday'; '"index futures" "relative value"'. arXiv title lookups for the SSRN items (5). S2: 4 queries rate-limited (failed route) | 21:29 | 21:44 (resumed 01:21) | 21:44 | K1-001, K1-009, K1-014 | no, no |
| 4 | SSRN (Crossref prefix 10.2139) | "Russell 2000 futures"; "Nasdaq futures intraday"; "E-mini Dow futures"; "lead-lag equity index futures intraday"; "micro E-mini futures"; "index rebalancing futures intraday". SSRN pages and Delivery.cfm: 403 (failed route); Wayback SSRN abstract pages used for abstracts | 21:36 | 21:40 | 21:42 (abstract-only) | K1-005, K1-006, K1-007, K1-008, K1-009, K1-010 | no, no |
| 5 | CFTC Office of the Chief Economist | research-paper listing; keyword filters: E-mini, VIX, Announcements, Arbitrage, Price Discovery, Intraday Transactions Data, High Frequency Traders, Spreads | 21:46 | 21:47 | none | none | no, no |
| 6 | CME Group through Wayback | CDX listings: cmegroup.com/openmarkets/equity-index/*; articles/*; education/articles-and-reports/*; education/courses/*; trading/equity-index/*; newsletters/*; insights/economic-research/* | 21:47 | 21:52 | 21:52 | K1-017, K1-018, K1-019, K1-020, K1-021, K1-022, K1-023 | no, no |
| 7 | Databento blog | blog index; blog/learning; blog/engineering; Wayback CDX of databento.com/blog/*; CDX of databento.com/microstructure/*; CDX of databento.com/docs/examples/* | 21:52 | 21:54 (resumed 01:20) | 21:54 | K1-024 | no, no |
| 8 | VIX index and K1 products | Crossref: "VXN Nasdaq-100 volatility index futures returns intraday"; "RVX Russell 2000 volatility index"; "VIX intraday changes predict stock index futures returns"; "implied volatility index lead lag stock index futures high frequency"; "VIX Nasdaq futures intraday reversal". arXiv: 'VIX intraday futures'; 'VXN'; '"volatility index" "Nasdaq"' | 21:54 | 21:56 | 21:56 (abstract-only) | K1-025 (and K1-003, K1-005, K1-006 overlap here) | no, no |
| 9 | Quantpedia | site search ?s= "russell reconstitution", "index rebalancing", "nasdaq futures", "small cap large cap" (returns only a generic recent-post list: failed route); Wayback CDX quantpedia.com/strategies/*; CDX quantpedia.com/* keyword filter; 4 article pages read for their primary papers | 21:57 (resumed 01:12) | 01:14 | none | none (primaries all stock-level or multi-day) | no, no |
| 10 | Alexander Kurov (not already claimed) | Crossref query.author=Alexander Kurov (2 pages); RePEc IDEAS author page and htsearch (failed route); Semantic Scholar author record 144028003 paper list; Crossref query.author=Kurov with "Nasdaq Russell Dow index futures" | 21:43 (resumed 01:16) | 21:45 | 21:45 (abstract-only) | K1-015, K1-016 | no, no |
| 11 | Practitioner blogs (discovery only) | Wayback CDX: jonathankinlay.com, robotwealth.com, qoppac.blogspot.com, quantitativebrokers.com (keyword filtered); Quantocracy CDX; Quantocracy searches "russell", "reconstitution", "nasdaq futures", "closing auction", "rebalance close", "QQQ intraday", "russell 2000 futures", "e-mini nasdaq"; Alpha Architect posts through Wayback (followed to primaries); Crossref follow-up of named practitioner authors: "Zarattini opening range breakout QQQ day trading profitable", "Zarattini intraday momentum Nasdaq"; Concretum PDF list (Wayback CDX) and 3 title lookups | 01:14 | 01:22 | 01:19 | K1-026, K1-027 | no, no |

## 2. Rejected items

| id | container | source | item | reason (one phrase) |
|---|---|---|---|---|
| R-K1-001 | 1 | Crossref (JFM) | Kurov 2008, "Tick size reduction, execution costs, and informational efficiency in the regular and E-mini Nasdaq-100 index futures markets", 10.1002/fut.20341 | contract-design history (2006 tick change, floor NQ discontinued); no trading mechanism |
| R-K1-002 | 1 | Crossref (JFM) | Kurov and Lasser 2002, "The effect of the introduction of Cubes on the Nasdaq-100 index spot-futures pricing relationship", 10.1002/fut.2214 | spot-futures (index) arbitrage needing a cash basket leg; not tradable on TopstepX |
| R-K1-003 | 1 | Crossref (JFM) | Chen and Locke 2004, "Splitting the S&P 500 futures", 10.1002/fut.20133 | S&P contract split; generic S&P (D.1 territory) |
| R-K1-004 | 1 | Crossref (JFM) | Kawaller, Koch, Peterson 2001, "Volume and volatility surrounding quarterly redesignation of the lead S&P 500 futures contract", 10.1002/fut.2202 | S&P roll-week volume; generic S&P, no K1 product |
| R-K1-005 | 1 | Crossref (JFM) | Frino, Walter, West 2000, "The lead-lag relationship between equities and stock index futures markets around information releases", 10.1002/(sici)1096-9934(200005)20:5<467::aid-fut4>3.0.co;2-l | Australian SPI futures vs cash; futures-to-cash direction, cash leg not tradable |
| R-K1-006 | 1 | Crossref (JFM) | Herbst, McCormack, West 1987; Chan 1992 RFS; Tse 1995 J Forecasting (Nikkei); several Korea, China, Malaysia, Turkey, Greece, Pakistan spot-futures lead-lag papers (listed in section 1 query output) | spot index vs its own futures: futures lead cash; signal flows to an untradable leg (NKD dropped by D1 for the Nikkei item) |
| R-K1-007 | 1 | Crossref (JFM) | Fung, Lau, Tse 2015, "The impact of sampling frequency on intraday correlation and lead-lag relationships between index futures and individual stocks", 10.1002/fut.21715 | Hang Seng futures vs single stocks; traded leg is stocks |
| R-K1-008 | 1 | Crossref (JFM) | Monoyios and Sarno 2002, "Mean reversion in stock index futures markets: a nonlinear analysis", 10.1002/fut.10008 | basis (futures minus fair value) mean reversion at daily frequency; needs cash leg |
| R-K1-009 | 1 | Crossref | Hsi Liu, Cheng Lin 2021, "Relationships among US S&P500 stock index, its futures and NASDAQ index futures with volatility spillover and jump diffusion: modeling and hedging", 10.47260/bae/818 | hedging-model study (title); no abstract in Crossref; no intraday trading angle stated |
| R-K1-010 | 1 | Crossref | Ivanov, Jones, Zaima 2013, "Analysis of DJIA, S&P 500, S&P 400, NASDAQ 100 and Russell 2000 ETFs and their influence on price discovery", 10.1016/j.gfj.2013.10.005 | ETF vs cash-index price discovery; no futures leg (title) |
| R-K1-011 | 3 | Crossref | Jiang 2026, "The one-minute edge: do Nasdaq futures lead QQQ?", 10.2139/ssrn.7217599 | direction is MNQ leading QQQ; traded leg would be the ETF, not a K1 product |
| R-K1-012 | 3 | Crossref | Vengavillagam 2026, "Volatility, retracement, and mean reversion inside NASDAQ futures", 10.2139/ssrn.7494858 | imbalance fill needs median 4.7 h, tail of weeks, 23.4% pass a 1% drawdown: needs holding past 15:08 CT (rule 8) |
| R-K1-013 | 3 | Crossref | Zhang and Pinsky 2025, "S&P-500 vs. Nasdaq-100 price movement prediction with LSTM for different daily periods", 10.1016/j.mlwa.2024.100617 | index-level LSTM direction forecast, no futures or cost framing (title; abstract not in Crossref) |
| R-K1-014 | 2 | Crossref | Madhavan 2003 FAJ "The Russell reconstitution effect"; Chen 2006 "On Russell index reconstitution"; Wei and Young 2017/2024 "Selection bias or treatment effect?"; Onayev and Zdorovtsov 2008 "Predatory trading around Russell reconstitution" (10.2139/ssrn.1101341) | stock-level additions/deletions returns (daily or rank-day closing prices); no index- or futures-level effect |
| R-K1-015 | 2 | Crossref | Micheli and Neuman 2020, "Evidence of crowding on Russell 3000 reconstitution events", 10.1142/s2382626620500094 | stock-level price impact of additions and deletions; index-replication tool |
| R-K1-016 | 2 | Crossref | Chen, Noronha, Singal 2004 JF; Kumar et al. 2023 JBF; Chan, Kot, Tang 2013 JBF; Kappou, Brooks, Ward 2007 (S&P 500 index effect) | stock-level S&P 500 inclusion effect; S&P exposure not traded in Stage E |
| R-K1-017 | 2 | Crossref | Jegadeesh and Wu 2022 JFE "Closing auctions: Nasdaq versus NYSE"; Bacidore and Lipson 2001; Pagano, Schwartz, Speiser; Shao et al. 2023 | stock-level closing-auction design; no futures leg |
| R-K1-018 | 2 | Crossref | Hagströmer and Nordén 2013, "Closing call auctions at the index futures market", 10.1002/fut.21603 | futures-market closing auction (Stockholm); CME equity futures have no closing auction, and the effect sits at the futures close, past 15:08 CT |
| R-K1-019 | 4 | Crossref (SSRN) | Lu 2026, "Breakeven geometry of reward-to-risk ratios in Micro E-mini futures", 10.2139/ssrn.7226278 | MES only, and an arithmetic note; closed product |
| R-K1-020 | 4 | Crossref (SSRN) | Chatzimanolakis 2025, "Weekly Nasdaq futures strategy", 10.2139/ssrn.5630830 | weekly holding; intraday-infeasible (rule 8) |
| R-K1-021 | 4 | Crossref (SSRN) | Kurov and Zabotina 2004, "Is it time to reduce the minimum tick sizes of the E-mini futures?", 10.2139/ssrn.483162 | contract-design policy paper |
| R-K1-022 | 4 | Crossref (SSRN) | Okada and Hamuro 2026 (TOPIX futures); Wang 2002 "Dependence of the intraday Nikkei stock index futures" (10.2139/ssrn.314888) | NKD dropped by D1; TOPIX not a CME product |
| R-K1-023 | 4 | Crossref (SSRN) | Shi, Cucuringu, Cartea 2026 "Intraday lead-lag relationships in idiosyncratic stock returns"; Curme et al. 2014/2015 (lead-lag in stocks) | single-stock lead-lag; no index-futures leg |
| R-K1-024 | 4 | Crossref (SSRN) | Rossi and Fantazzini 2009 "Long memory and periodicity in intraday volatility of stock index futures"; Brown 2026 (two ES memory papers); Howard 2026 (ES value-area) ; Salov 2021 (ES randomness) | generic S&P / volatility modelling; D.1 territory or no K1 product |
| R-K1-025 | 1 | Crossref | Kang 2023 SSRN version 10.2139/ssrn.4658378 | same paper as K1-002 (published version read) |
| R-K1-026 | 10 | Crossref author list (Kurov) | Erenburg, Kurov, Lasser 2006 JFI, "Trading around macroeconomic announcements: are all traders created equal?", 10.1016/j.jfi.2005.07.003 (abstract read on Wayback SSRN 694801) | S&P 500 regular and E-mini only; first-20-seconds trader-type result; generic S&P (D.1 E) and HFT horizon |
| R-K1-027 | 10 | Crossref (Kurov) | Kurov 2005 JFM "Execution quality in open-outcry futures markets", 10.1002/fut.20176 | floor trading, defunct |
| R-K1-028 | 10 | Crossref (Kurov) | Kurov 2008 Fin. Review "Investor sentiment, trading behavior and informational efficiency in index futures markets"; Kurov 2010 JBF "Investor sentiment and the stock market's reaction to monetary policy"; Gu and Kurov 2020 (Twitter sentiment); Jain, Kurov, Li, Pathak 2024 (Twitter image sentiment) | sentiment, shelved |
| R-K1-029 | 10 | Crossref (Kurov) | Basistha and Kurov 2008 JBF; Kurov 2012 RFE; Kurov and Gu 2016 JFM ("Fed put"); Gu, Kurov, Wolfe 2018 JEF ("Relief rallies after FOMC"); Kurov, Olson, Zaynutdinova 2022 JBF | FOMC effect on the S&P 500 generically; D.1 family E (E1 to E3 cover FOMC) |
| R-K1-030 | 10 | Crossref (Kurov) | Kurov, Sancetta, Wolfe 2022 "Drift Begone!" | see K3-034 |
| R-K1-031 | 10 | Crossref (Kurov) | Gu, Guo, Kurov, Stan 2021 JFM, "The information content of the volatility index options trading volume", 10.1002/fut.22297 | predicts the VIX index itself, not a K1 product |
| R-K1-032 | 8/10 | Crossref (Kurov) | Aikins and Kurov 2024, "Which way does the wind blow between SPX futures and VIX futures?", 10.2139/ssrn.4960465 | contemporaneous causality (identification through heteroskedasticity), no predictive lead; ES and VX only |
| R-K1-033 | 10 | Crossref (Kurov) | Kurov, Olson, Wolfe 2025, "Contemporaneous causality between global stock markets", 10.2139/ssrn.5938629 | contemporaneous (title), no lead to trade; abstract unreachable (Crossref none, Wayback 404, S2 not found) |
| R-K1-034 | 10 | Crossref (Kurov) | Chordia, Kurov, Muravyev, Subrahmanyam 2021 MS "Index option trading activity and market returns", 10.1287/mnsc.2019.3529 | SPX option flow predicting S&P returns: S&P exposure not traded; daily (title) |
| R-K1-035 | 10 | Crossref (Kurov) | Ge, Kurov, Wolfe 2019 (presidential company tweets); Kucher, Kurov, Wolfe 2023 (COVID vaccine news); John, Kurov, Li 2024 (bitcoin) | single stocks; one-off event; crypto (K7) |
| R-K1-036 | 3 | arXiv | "Market simulation under adverse selection", arXiv:2409.12721 (ES, NQ, CL, ZN market making) | limit-order market making; TopstepX limit orders fill only on trade-through; HFT |
| R-K1-037 | 3 | arXiv | "Scale-free avalanche dynamics in the stock market", physics/0601171 | physics of avalanches; no strategy |
| R-K1-038 | 5 | CFTC OCE listing (keyword filters) | Ferko, Mixon, Onur 2024, "Retail traders in futures markets", OCE 2023-002 (abstract page read) | non-public position data; multi-day holding (median 4 days); not a readable signal |
| R-K1-039 | 5 | CFTC OCE listing | "Volatility derivatives in practice: activity and impact" (oce_volderivatives.pdf) | descriptive VIX-derivatives activity; no K1 mechanism (title) |
| R-K1-040 | 5 | CFTC OCE listing | "High-frequency trading and market quality: evidence from account-level futures data" (2022); "Anticipatory traders and trading speed" | HFT account-level studies; horizon far below the account's |
| R-K1-041 | 5 | CFTC OCE listing | "Macro news announcements and automated trading"; "High frequency traders and the price process"; "Stop orders in select futures markets" | see D.1 E5, C23, B2 |
| R-K1-042 | 6 | Wayback CDX (CME OpenMarkets) | "After five years micro equity futures still gaining steam" (2024); "Why around-the-clock liquidity matters" (2025); "The growth of tech and 25 years of Nasdaq futures" (2024); "Small caps stage quiet comeback" (2026); "The Dow Jones Industrial Average turns 125" | descriptive or commentary (title) |
| R-K1-043 | 6 | Wayback CDX (CME OpenMarkets) | "The trick behind the Halloween strategy"; "Three reasons for the September effect"; "Will Santa Claus come to Wall Street"; "What happens when the January effect meets midterm elections"; "Elections and volatility" | multi-week calendar seasonality on the broad index; D.1 family E, multi-day |
| R-K1-044 | 6 | Wayback CDX (CME articles) | 2023 "The Russell 2000 reconstitution because markets change"; 2024 "Tap into small-cap stocks through the Russell 2000 reconstitution"; 2025 "Changes at the top as tech surges"; education "Russell US equity indices 2019 reconstitution results" | same publisher and content as K1-017/018/023 (reconstitution marketing) |
| R-K1-045 | 6 | Wayback CDX (CME education) | BTIC pages ("About BTIC", "BTIC liquidity report", "BTIC versatility", "BTIC trading at index option expirations"); "A cost comparison of Russell 2000 futures and ETFs"; "E-mini Russell 2000 futures liquidity report"; "Keeping the pulse of the small-cap markets"; "Rebalancing: don't forget derivatives" | trade-type or product documentation; BTIC is not an order type the program uses |
| R-K1-046 | 6 | Wayback CDX (CME) | FAQ pages (Micro E-mini FAQ, weekly options FAQ, AIR total return futures, dividend index futures, VOLQ futures FAQ) | product documentation |
| R-K1-047 | 6 | Wayback CDX (CME) | "Nikkei 225 implied intercommodity spreads"; "FAQ BTIC on Nikkei 225 futures"; "Japan's Nikkei 225 faces uncertainty as rates rise"; TOPIX BTIC course | NKD dropped by D1 |
| R-K1-048 | 6 | Wayback CDX (CME) | "Rolling an equity position using spreads" (course) | calendar roll mechanics; no mechanism |
| R-K1-049 | 6 | Wayback CDX (cmegroup.com/trading/equity-index, newsletters, insights/economic-research) | quote and settlement pages; InFocus daily recaps ("Nasdaq leads equities higher", "Russell leads equities higher" and similar, 2024 to 2026); economic-research valuation pieces ("Are S&P 600 / Russell 2000 small caps due for a rebound?", "Are US small caps undervalued relative to larger S&P 500 peers?", "Nasdaq's stellar returns") | market recaps or multi-month valuation commentary; no intraday mechanism |
| R-K1-050 | 7 | Databento blog index | "Build a pairs trading strategy in Python" (2025) (lede read) | WTI against Brent crude: K4's region |
| R-K1-051 | 7 | Databento blog (engineering) | "High-frequency, liquidity-taking strategy" (2024); "Building high-frequency trading signals with sklearn" (2024) (ledes read) | ES order-book HFT signals; ES not traded and horizon far below the account's (D.1 C24/D10 cover Databento microstructure) |
| R-K1-052 | 7 | Databento blog (learning, CDX list) | "What are futures spreads?", "What are 0DTE options?", "CME matching algorithms explained", "When technical indicators are a red flag", "Self-match prevention", "Tick sizes and values", "VWAP in Python", remaining product and company posts | education or product documentation; no K1 mechanism (title) |
| R-K1-053 | 8 | Crossref | Kittiakarasakun, Tse, Wang 2012, "The impact of trades by traders on asymmetric volatility for Nasdaq-100 index futures", 10.1108/03074351211239388 | daily volatility asymmetry using 2002 to 2004 trader-type data; not a return predictor, not observable |
| R-K1-054 | 8 | Crossref | Fu, Sandri, Shackleton 2016 JFM, "Asymmetric effects of volatility risk on stock returns: VIX and VIX futures", 10.1002/fut.21772 | cross-section of stock returns (asset pricing), not index futures |
| R-K1-055 | 8 | Crossref | Frijns et al. 2015/2016 (VIX and its futures); Bollen, O'Neill, Whaley 2016 ("Tail wags dog"); Kao et al. 2017; Huang et al. 2023 JBF (intraday momentum in VIX futures); Fernandez-Perez et al. 2018 (VIX ETNs); Simon 2016; Yoon, Ruan, Zhang 2022 | traded product is VIX futures, ETNs or options, not K1 |
| R-K1-056 | 8 | Crossref | Giot 2003 "Information content of implied volatility indexes for forecasting volatility and market risk" (10.2139/ssrn.362440) | volatility forecasting at 5 to 22 days; no return signal |
| R-K1-057 | 8 | Crossref | Lin, Luo, Shao 2026 "When does intraday options trading predict stock returns?"; Amaya and Vasquez 2011 | single-stock cross-section |
| R-K1-058 | 8 | Crossref | Fang, Zhang, Xu 2024 (VIX-Lasso-GRU for Chinese index futures); Li, Yu, Luo 2019 (Chinese options VIX); Lee and Chung 2005 (Korea); Korean/Japanese VIX lead-lag papers | non-US index futures; ML forecast; mechanism transfer weak (title/abstract) |
| R-K1-059 | 8 | Crossref | Rhoads 2018 "Systematic Russell 2000 index option strategies in different volatility regimes"; Rhoads and Ravalli 2017 (Russell 2000 PutWrite); Kapadia and Szado 2011 (Russell 2000 buy-write) | option-selling strategies held to expiry; not futures, multi-day |
| R-K1-060 | 9 | Quantpedia (Wayback CDX slug list; page read for lede) | "How to utilize anticipated ETF rebalances" -> primary Li (2021), "Should passive investors actively manage their trades?", SSRN 3967799 | stock-level: added stocks rise 67 bp over the 5 days before the rebalance, reverse over 20 days; multi-day, not an index-futures effect |
| R-K1-061 | 9 | Quantpedia | "Should we rebalance index changes immediately?" -> Arnott et al. (2022) | S&P 500 stock selection around additions; multi-month; S&P not traded |
| R-K1-062 | 9 | Quantpedia | "Leveraged ETFs in low volatility environments" (SPXL/SPXU daily allocation 2013 to 2025) | daily ETF allocation; not intraday, S&P |
| R-K1-063 | 9 | Quantpedia | "Can technology sector leadership be systematically exploited?" (monthly Fama-French industries 1926 to 2025) | monthly; intraday-infeasible |
| R-K1-064 | 9 | Quantpedia | "Do S&P 500 0DTE options increase market volatility?"; "Is VIX index manipulated?"; "VVIX index predicts value/growth return spread"; "Timing value vs growth ... small value large growth spread"; "Better small-cap premium"; "When big gets small" | S&P generic, VIX settlement, or multi-month style/size spreads |
| R-K1-065 | 9 | Quantpedia | strategies/pairs-trading-with-country-etfs, mean-reversion/momentum in country equity indexes, turn-of-the-month in equity indexes, market seasonality in world equity indexes | multi-day or monthly country-index strategies; turn-of-month see D.1 E8/E46 |
| R-K1-066 | 9 | Quantpedia site search (quantpedia.com/?s=) for "russell reconstitution", "index rebalancing", "nasdaq futures", "small cap large cap" | search returns only the site's generic recent-post list; no hits (logged as failed route) |
| R-K1-067 | 2 | Crossref | Shum, Hejazi, Haryanto, Rodier 2015 RoF, "Intraday share price volatility and leveraged ETF rebalancing", 10.1093/rof/rfv061 (SSRN 2161057 same) | end-of-day VOLATILITY in stocks 2006 to 2011, no return direction; LETF close-hedging mechanism is D.1 A10's (Baltussen et al.) |
| R-K1-068 | 2 | Crossref | Rosa 2022 JFM, "Understanding intraday momentum strategies", 10.1002/fut.22375 | overnight-return-predicts-last-half-hour on the market (no K1 product named); D.1 A10/A28 family, generic |
| R-K1-069 | 2 | Crossref | Baltussen, Da, Lammers, Martens 2021 JFE (SSRN 3760365) | see D.1 A10 |
| R-K1-070 | 2 | Crossref | Hayase, Mizuta, Yagi 2026 (L-ETF and Nikkei futures arbitrage, artificial market); Horan 2025 JAI (LETP rebalancing counterparties, no abstract); Avellaneda and Zhang; Leung et al.; Geissmann; Peterburgsky; Jiang and Peterburgsky | Nikkei (NKD dropped by D1) simulation; LETF pricing/decay or multi-day pair holdings; no K1 intraday signal |
| R-K1-071 | 2 | Crossref | Herbst and Maberly 1992 JFM "The informational role of end-of-the-day returns in stock index futures"; Hiraki, Maberly et al. 1995 (Osaka Nikkei end-of-day) | S&P end-of-day returns predicting next day (generic S&P, D.1 A family, overnight hold); Nikkei dropped |
| R-K1-072 | 2 | Crossref | Sen 2026 "Gamma exposure (GEX) without the paywall ... gold and S&P 500 futures"; Yuan and Li 2022 (China delta-hedging); JIN 2024 (Nikkei intraday momentum); Chinese index/commodity intraday momentum papers | S&P or gold (K5) or non-US; not K1 products |
| R-K1-073 | 11 | Quantocracy search "closing auction" -> Alpha Architect "Why the last few minutes of trading might matter more than you think" (Wayback) -> Baltussen, Da, Soebhag, "End of day reversal" | see D.1 C16 (cross-sectional single-stock reversal) |
| R-K1-074 | 11 | Quantocracy search "rebalance close" -> Alpha Architect "Adverse effects of index replication" (Wayback) -> Sammon and Shim 2025 "Index rebalancing and stock market composition"; Hendrix, Liu, Roberts 2024 "Measuring the costs of index reconstitution: a 10-year perspective"; Arnott et al. 2023 | index-fund replication costs, stock-level, multi-day |
| R-K1-075 | 11 | Quantocracy -> Alpha Architect "Markets becoming more efficient: the disappearing index effect" (2024) | S&P 500 stock-level inclusion effect |
| R-K1-076 | 11 | Quantocracy search "russell" | "Russell death cross implications for SPX" (Quantifiable Edges; daily, SPX); "QQQ:IWM for risk-on" (CXO; monthly ETF allocation) | daily/monthly, no intraday mechanism |
| R-K1-077 | 11 | Wayback CDX jonathankinlay.com, robotwealth.com, qoppac.blogspot.com, quantitativebrokers.com (keyword filter nasdaq, russell, dow, e-mini, rebalance, reconstitution, lead-lag, spread, pairs, vix) | only VIX-futures systems, ES overnight/meta-strategy posts (D.1 A8, B7), ETF/stock pairs, VIX calendar trades, ES roll and liquidity reports; no NQ/RTY/YM post found |
| R-K1-078 | 11 | Crossref follow-up | Fetna 2026, "Opening-range breakout does not survive trading costs: a pre-registered 225-cell study on sixteen years of futures data", SSRN 7428398 (nine futures incl. equity indices, metals, energy) | see K4-050 (panel source already claimed by K4 as "title only"; note for K4 and the lead: its abstract is available verbatim from api.crossref.org, 10.2139/ssrn.7428398, and covers equity-index futures, i.e. K1 passages would be tagged [K1]) |
| R-K1-079 | 11 | Crossref follow-up | Pineda 2026, "Anatomy of the retest in the QQQ opening range breakout", SSRN 6745958 | descriptive associations only, author disclaims exploitability; ORB covered by K1-026 and D.1 B |
| R-K1-080 | 11 | Crossref follow-up | Zarattini, Aziz, Barbon 2024 "Beat the market: an effective intraday momentum strategy for S&P500 ETF (SPY)" (SSRN 4824172); Zarattini, Barbon, Aziz 2024 "A profitable day trading strategy for the U.S. equity market" (SSRN 4729284, stocks in play) | SPY = S&P exposure (D.1 A/B family, generic); single stocks |
| R-K1-081 | 11 | Crossref follow-up | Xu 2017 "Reversal, momentum and intraday returns" (SSRN 2991183) | cross-section of stocks |
| R-K1-082 | 3 | arXiv q-fin.TR | Huth and Abergel 2014, "High frequency lead/lag relationships: empirical facts", arXiv:1111.7103 | futures-lead-stocks at tick level (European futures and stocks); traded lag leg is stocks; HFT horizon |
| R-K1-083 | 3 | arXiv q-fin.ST | Hayashi-Koike / wavelet / transfer-entropy lead-lag estimators (arXiv:1708.03992, 1612.01232, 2206.10173, 2601.01871, 1402.3820, 1504.06235, 2002.00724) | estimation methodology, no K1 trading result |
| R-K1-084 | 3 | arXiv q-fin.ST | lead-lag in FX (1906.10388, 1609.04640, 2004.10560, 1803.09432); VIX vs VIX futures (1910.13729); stock networks (1401.0462, 2312.10084, 2201.08283, 2305.06704, 2309.08800, 2608.24703, 1906.05057); prediction markets (2602.07048) | not K1 products (FX is K3's; VIX futures not traded) |
| R-K1-085 | 11 | Crossref follow-up (Concretum list) | Zarattini, Aziz, Mele 2025 "The volatility edge: a dual approach for VIX ETNs trading" (SSRN 5316487); Zarattini and Stamatoudis 2024 "The power of price action reading" (SSRN 4879527) | VIX ETNs; not a K1 product (price-action paper: no index-futures angle in title) |
| R-K1-086 | 10 | Semantic Scholar author record (A. Kurov, id 144028003) | "Price discovery in the E-mini futures markets: is the tail wagging the dog?" (2002); "Price dynamics in the E-mini futures markets" (2002) | working-paper versions of K1-015 (one source) |
| R-K1-087 | 10 | Semantic Scholar author record | "Price pressure in commodity futures or informed trading in commodity futures options" (2017); "Energy commodity basis, returns and the business cycle" (2012); "Monetary policy and uncertainty resolution in commodity markets" (2023) | commodity products (K4/K5/K6 region), not K1 |
| R-K1-088 | 10 | Semantic Scholar author record | "Volatility forecasting: the role of internet search activity and implied volatility" (2016); "Stock market reactions to presidential statements" (2018) | attention/sentiment, shelved; single stocks |
| R-K1-089 | 10 | RePEc IDEAS | author page e/pku20 (404) and htsearch "Kurov futures" (no result list returned) | failed route |
| R-K1-090 | 1 | Crossref (JFM, 2005+) | Lee, Liao, Lee 2022 JFM, "Overnight returns of industry ETFs, investor sentiment, and futures market returns", 10.1002/fut.22321 | sentiment, shelved |
| R-K1-091 | 1 | Crossref (JFM, 2005+) | Frino, Bjursell, Wang, Lepone 2008, "Large trades and intraday futures price behavior", 10.1002/fut.20366 | needs customer-type large-trade identification (not observable); price-impact study |
| R-K1-092 | 1 | Crossref (JFM, 2005+) | Chen, Liu, Lu, Tang 2015 (CSI 300, Baidu attention); Baule, Frijns, Schlie 2024 (retail feedback trading, German derivatives); Jin et al. 2019 (China intraday momentum); Bianco and Renò 2005 (Italian futures) | non-US products or attention/sentiment |
| R-K1-093 | 7 | Wayback CDX databento.com/docs/examples | "equities/auction-imbalance", "algo-trading/pairs-trading", "algo-trading/high-frequency" and other API examples | code documentation; no mechanism or evidence (auction-imbalance data source already logged as K1-024) |
| R-K1-094 | 2 | Crossref | Altinkilic and Becker 2007, "Downward sloping demand curves: Nasdaq-100 additions and deletions" (SSRN 972800); Broom, Van Ness, Warr 2007 (QQQ listing move); Lo 2025 (Nasdaq-100 derivatives ETF portfolio) | stock-level index effect or ETF listing; no futures-level intraday effect |
| R-K1-095 | 11 | Quantocracy searches "QQQ intraday", "russell 2000 futures", "e-mini nasdaq" | no K1 hits (managed-futures and VIX-term-structure posts only) |

## 3. Passed items

### K1-001 Hasbrouck (2003), Intraday Price Formation in U.S. Equity Index Markets
- Registry id: K1-001. Citation: Hasbrouck, J. (2003), Journal of Finance 58(6); working paper SSRN 252304 (2001). Correct published DOI is 10.1046/j.1540-6261.2003.00609.x (the claim line in the registry carries a wrong DOI, 10.1111/1540-6261.00616; the registry is append-only, so the correction is recorded here).
- Container: 2/3 (found by container-2 query; belongs to container 3, lead-lag).
- Retrieval: ABSTRACT ONLY. Routes tried and failed: author site pages.stern.nyu.edu/~jhasbrou (working-paper index lists only the SAS programme documentation for this paper; guessed PDF paths 404), Wiley pdfdirect via Unpaywall (403), Wayback copies of the Wiley PDF and of the author PDF (404), SSRN (403). Text read: the two abstracts from api.crossref.org (JF and SSRN versions).
- Mechanism: price discovery (information share) across the instruments on ONE index: for the S&P 500 and the Nasdaq-100 the E-mini leads the floor futures and the ETF; for the S&P 400 the ETF dominates. It does not test lead-lag between different indices (NQ against ES).
- Products and horizon: ES, NQ E-minis, floor SP and ND futures, SPY, QQQ, MDY, sector ETFs; up to one-second resolution.
- Cost assumptions: none stated in the abstract [unverified beyond abstract]. Data window: [unverified] (not in the abstract).
- Quality tells: Journal of Finance; the established reference for "E-mini leads" in the equity-index complex; pre-dates micros and the end of floor trading.
- Verbatim passages:
  - P-K1-001-a (JF abstract, Crossref): "For the S&P 500 and Nasdaq‐100 indexes, most of the price discovery occurs in the E‐mini market. For the S&P 400 MidCap index, price discovery is shared between the regular futures contract and the ETF."
  - P-K1-001-b (SSRN abstract, Crossref): "The specifications are estimated at very fine (up to one second) time resolution. ... price changes in the E-mini futures prices generally lead those in the regular futures contracts and the ETFs."
- Numeric claims: none beyond "one second" resolution (P-K1-001-b); information-share numbers [unverified].
- Tags: new to the program (price leadership within one index exposure; transfers at best to micro against E-mini, see K1-00x Fassas). Intraday-feasible as a fact about who leads; not a strategy (the lagging instruments here are an ETF and a defunct floor contract).
- Clusters tagged: [K1].

### K1-002 Kang (2023), Optimal and Non-Optimal MACD Parameter Values ... Nikkei, Dow Jones, and Nasdaq
- Registry id: K1-002. Citation: Kang, B.-K. (2023), Journal of Risk and Financial Management 16(12) 508, 10.3390/jrfm16120508 (SSRN 4658378 is the same paper).
- Container: 1 (surfaced by Crossref container-1 query).
- Retrieval: full text, HTML, Wayback copy https://web.archive.org/web/2024/https://www.mdpi.com/1911-8074/16/12/508 (mdpi.com direct and PDF: 403).
- Mechanism: MACD signal-line crossover on DAILY closes, always in the market (stop-and-reverse), parameter-set search on Nikkei, Dow and Nasdaq futures.
- Products and horizon: Nikkei 225 futures (JPX), "Dow Jones futures" and "Nasdaq futures" (Investing.com daily closes, contract not specified); multi-day holding.
- Cost assumptions: none (fees ignored, P-K1-002-c).
- Data window: 2011 to 2021 daily.
- Quality tells: in-sample parameter mining over thousands of MACD sets; Investing.com continuous series; no costs; results reported as "outperformed buy-and-hold in individual years", no consistent significance.
- Verbatim passages:
  - P-K1-002-a (Data section): "This study utilizes the daily closing index values of Nikkei 225 futures (contracts near maturity), Dow Jones futures, and Nasdaq futures over the last 11 years (2011–2021)."
  - P-K1-002-b (Trading rule): "When a 'buy' (or 'sell') signal is generated based on the signal line crossover, a buy (or sell) order for 'one trading unit' is executed at the closing price (index value) on the next day. ... when a position is closed, a reverse trade is automatically executed."
  - P-K1-002-c (Trading rule): "Transaction fees are not taken into account in this study, similarly to the previous study."
  - P-K1-002-d (Results): "while there is no 'P-P' model that consistently generated significant returns over the entire test period, there are numerous 'P-P' models that outperformed the buy-and-hold strategy in individual or consecutive years."
- Numeric claims: sample 2011 to 2021 (P-K1-002-a). No return figure carried.
- Tags: port of D.1 family H (daily-bar construction) on YM and NQ. NOT intraday-feasible: positions held from close to a later close (P-K1-002-b), violating rule 8. Nikkei leg: NKD dropped by D1.
- Clusters tagged: [K1].

### K1-003 Bangsgaard and Kokholm (2024), The lead-lag relation between VIX futures and SPX futures
- Registry id: K1-003. Citation: Bangsgaard, C., Kokholm, T. (2024), Journal of Financial Markets 67, 100851, 10.1016/j.finmar.2023.100851; SSRN 4003464 (2022) is the same paper.
- Container: 1/8 (VIX-family signal instrument; traded product in the paper is ES, a leg-only exposure in Stage E; mechanism plausibly transfers to NQ).
- Retrieval: full text PDF, https://pure.au.dk/ws/files/448941848/1-s2.0-S1386418123000496-main.pdf (Aarhus repository, found via Unpaywall).
- Mechanism: in high-volatility regimes VIX futures lead E-mini S&P futures at millisecond-to-second horizons (volatility feedback, VIX-futures dealer hedging in ES, dealer gamma); in low volatility the two are weakly connected. Trading ES on VX price changes is profitable at midquotes but loses at bid and ask for holding periods from 5 ms to 5 min.
- Products and horizon: ES and VX (CFE), regular trading hours 9:30 to 16:15 ET; holding 5 ms to 5 min.
- Cost assumptions: two cases, midquote execution and execution at prevailing bid/ask (P-K1-003-c).
- Data window: January 2013 to September 2020, tick data (Tick Data Inc.) with millisecond stamps.
- Quality tells: peer-reviewed; explicit negative result after costs; horizons are far below anything a market-order, non-HFT XFA account can use.
- Verbatim passages:
  - P-K1-003-a (abstract): "The two futures markets are weakly connected when market volatility is low. In contrast, when volatility is high, their prices are highly negatively correlated, with VIX futures leading SPX futures. However, the tightness of the lead–lag relation prevents the formation of profitable trading strategies in a setup that includes transaction costs."
  - P-K1-003-b (Sec. 4.1): "Tick-by-tick trade and quote data on SPX futures (ES) and VIX futures (VX) are obtained from Tick Data and cover the period from January 2013 to September 2020. The timestamps of the trades are available with millisecond precision."
  - P-K1-003-c (Sec. 4.4): "we let the holding period of each position in the futures contract vary from five milliseconds to five minutes. ... Overall, this strategy generates negative returns irrespective of the holding period. Due to the tightness of the lead–lag relation, the position in the SPX futures is held for very short horizons and the cost from trading at the bid and ask prices outweighs the SPX futures price change signaled by the realized VIX futures return."
  - P-K1-003-d (Introduction): "we conclude that the two markets are too synchronized for the relation to be systematically monetized by investors."
- Numeric claims: sample 2013-01 to 2020-09 (P-K1-003-b); holding 5 ms to 5 min (P-K1-003-c).
- Tags: new to the program (VIX-futures signal into equity-index futures). NOT intraday-feasible in the usable sense: edge exists only at millisecond to one-minute holding and is negative after the spread (P-K1-003-c); also conflicts with Topstep's high-rate prohibition. Non-survivor.
- Clusters tagged: [K1].

**Retrieval note for the SSRN-only items K1-004 to K1-011 (except K1-009, later found on arXiv and read in full).** Full text failed on every route tried: papers.ssrn.com abstract page and Delivery.cfm by curl (HTTP 403, tested on 7364204 and 3459744), Delivery.cfm by WebFetch (403), Wayback copies of Delivery.cfm (404, tested on 3459744), Unpaywall (only the SSRN DOI landing page is listed for every one of them), and a Crossref author search for a published version (none found for Franz; the 2026 items are single-author SSRN postings). Text read: the abstract, verbatim from api.crossref.org, and for K1-004 also the Wayback copy of the SSRN abstract page (https://web.archive.org/web/20250510103003/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3459744). Every claim beyond the abstract is [unverified]. None of these counts as a full-text read.

### K1-004 Franz (2019), The Index Effect Minute by Minute: Intraday Returns at NASDAQ-100 and MSCI U.S. Rebalancings
- Registry id: K1-004. Citation: Franz, F.-C. (2019), SSRN 3459744, 10.2139/ssrn.3459744 (Goethe University Frankfurt). Container 2.
- Retrieval: ABSTRACT ONLY (see note above).
- Mechanism: stock-level abnormal returns around Nasdaq-100 and MSCI USA constituent changes: post-announcement jump plus intraday drift; for small-cap changes, same-sign abnormal returns on the rebalancing date concentrated in the last 30 minutes; reversal early the next morning (price pressure).
- Products and horizon: constituent stocks (not futures); minutes around announcement and the rebalancing close.
- Cost assumptions: [unverified]. Data window: 2013 to 2017 intraday (P-K1-004-a).
- Quality tells: working paper, not found published; stock-level, so the index-futures effect is not measured; relevance to NQ is indirect (does a Nasdaq-100 reconstitution day show a net index-level close-of-day pressure?) and untested in the abstract.
- Verbatim passages:
  - P-K1-004-a (abstract, Wayback SSRN page): "I use intraday data from 2013 to 2017 and a dataset of NASDAQ-100, MSCI USA and MSCI USA Small Cap Index constituent changes to investigate abnormal returns and trading volume around index rebalancings. The results show no pre-announcement speculation but a significantly positive (negative) post-announcement jump followed by an intraday drift for promotions (demotions)."
  - P-K1-004-b (abstract): "For small-cap changes, the post-announcement jump is smaller but abnormal returns with the same sign are also found on the rebalancing date and especially during the last 30 minutes of trading. Large-cap index changes have higher abnormal trading volume but much smaller abnormal returns on the rebalancing date. Consistent with the price pressure hypothesis, I find a reversal during the early trading hours on the day following the rebalancing date."
- Numeric claims: sample 2013 to 2017 (P-K1-004-a); last 30 minutes (P-K1-004-b). Effect sizes [unverified].
- Tags: port of D.1 family E (calendar and events: D.1 E10, E14 cover S&P rebalances and passive-flow reconstitution pressure generically) onto the Nasdaq-100 reconstitution date. Intraday-feasible only for the rebalancing-day window up to 15:00 CT; the next-morning reversal leg needs no overnight hold (a morning trade), so feasible, but the effect is stock-level and its index-level sign is unknown.
- Clusters tagged: [K1].

### K1-005 Seeck (2026), Volatility as a Signal Switch: Regime-dependent Intraday Mean Reversion in Nasdaq-100 Futures
- Registry id: K1-005. Citation: Seeck (2026), SSRN 7364204, 10.2139/ssrn.7364204. Containers 1 and 8 (VXN signal into NQ).
- Retrieval: ABSTRACT ONLY.
- Mechanism: a daily band of prior close ± VXN/16 on NQ; intraday breaches of the band revert before the session close; fade entries with a 30-minute exit; the edge appears only at the VXN extremes.
- Products and horizon: NQ; intraday, 30-minute exit, same session. Signal instrument: VXN (Cboe Nasdaq-100 volatility index).
- Cost assumptions: [unverified]. Data window: 2018 to 2026 events; pre-sample 2010 to 2017.
- Quality tells: single-author SSRN posting; 860 events, OOS n = 191; non-monotone Sharpe by bucket (two of four buckets positive) is a data-mining warning; pre-sample Sharpe negative without the filter; "reversion rate 85.2%" is a touch-back rate, not P&L.
- Verbatim passages:
  - P-K1-005-a (abstract): "We ask whether intraday price moves beyond an implied-volatility band in E-mini Nasdaq-100 futures (NQ) revert before the session closes. The band is set daily as ± VXN/16 relative to the prior-session close; dividing by 16 converts the annualised VXN to a one-day standard-deviation estimate. Over 860 algorithmically detected band-breach events (2018–2026), the unconditional same-session reversion rate is 85.2%."
  - P-K1-005-b (abstract): "Reversion probability is statistically significant in all four VXN buckets (BH-adjusted p < 0.001), but the 30-minute exit rule generates positive Sharpe only at the extremes (VXN < 20: 0.38; VXN >= 30: 0.64), with slightly negative values in between. Walk-forward validation confirms the pattern out of sample (IS 2018–2022, n = 298, Sharpe = 0.47; OOS 2023–2026, n = 191, Sharpe = 1.29). A pre-sample from 2010–2017 gives a Sharpe of -0.94 without the regime filter."
- Numeric claims: 860 events, 85.2% (P-K1-005-a); Sharpe 0.38 / 0.64, IS 0.47 n = 298, OOS 1.29 n = 191, pre-sample -0.94 (P-K1-005-b). All from the abstract; not re-checked against tables [unverified beyond abstract].
- Tags: port of D.1 families C (short-horizon reversal) and D (volatility state) on NQ, with a new element: implied-volatility index (VXN) as the band and regime variable. Intraday-feasible (same-session exit, reads prior-day VXN).
- Clusters tagged: [K1].

### K1-006 Backhaus (2026), Expected Intraday Range and the VIX ... Nasdaq-100 Regular-Trading-Hours Sessions
- Registry id: K1-006. Citation: Backhaus (2026), SSRN 7154758, 10.2139/ssrn.7154758. Container 8.
- Retrieval: ABSTRACT ONLY.
- Mechanism: prior-day VIX/√252 as the expected one-sided excursion from the RTH open of the Nasdaq-100; calibration (slope ≈ 1) and touch probabilities by VIX regime and weekday. A range forecast, not a directional signal.
- Products and horizon: Nasdaq-100 cash index (one-minute), RTH; transfer to NQ is direct (same index). Intraday.
- Cost assumptions: none (not a P&L study). Data window: January 2015 to April 2026, 2,909 sessions.
- Quality tells: single-author SSRN; honest calibration framing; "touch-probability backtest" has no P&L.
- Verbatim passages:
  - P-K1-006-a (abstract): "Using one-minute data on the Nasdaq-100 cash index from January 2015 to April 2026 (2,909 RTH sessions) and prior-day VIX closes (strict no-look-ahead), we calibrate the expected move by a regression through the origin of the realized maximum one-sided excursion from the open on VIX/ √ 252. The estimated slope is 1.001 ... (R 2 ≈ 0.34). The expected-move band is touched intraday in 37.5% of sessions."
  - P-K1-006-b (abstract): "Touch probability rises monotonically with the volatility regime, from 31.7% when VIX < 14 to 43.9% when VIX > 25 ... Conditional on a touch, the median time-to-hit is 144 minutes from the open, and the lower band is touched first in 54.8% of hit sessions."
- Numeric claims: slope 1.001, R² ≈ 0.34, 37.5% touch (P-K1-006-a); 31.7% / 43.9%, 144 min, 54.8% (P-K1-006-b).
- Tags: port of D.1 family D (volatility state) and B (reference level) on the Nasdaq-100, VIX as the non-CME input. Intraday-feasible (reads prior-day VIX). Useful as a range/stop calibration fact rather than an edge.
- Clusters tagged: [K1].

### K1-007 Taylor (2026), Evaluating the Predictive Validity of ICT's AMD Model on CME E-Mini NASDAQ-100 Futures
- Registry id: K1-007. Citation: Taylor (2026), SSRN 7150238, 10.2139/ssrn.7150238. Container 4.
- Retrieval: ABSTRACT ONLY.
- Mechanism: Asia-session range, London false breakout, New York morning "delivery" (ICT AMD). Finding: no directional information beyond the daily trend regime; most target moves happen before the 9:40 ET entry.
- Products and horizon: NQ, 15-minute bars, Databento data; intraday (Asia to NY morning).
- Cost assumptions: [unverified]. Data window: January 2022 to July 2026, 484 signal days.
- Quality tells: single-author SSRN; BH correction reported; a null for the ICT pattern itself; the surviving cells are trend-regime conditioning, i.e., a daily-trend effect.
- Verbatim passages:
  - P-K1-007-a (abstract): "Using four years of real 15-minute OHLCV data from Databento (January 2022 to July 2026), we operationalize the AMD rules into a strict mechanical strategy and analyze the statistical properties of the resulting signal across N = 484 manipulation signal days ... Second, 57% of valid signals see full target delivery before the 9:40 AM New York entry window opens"
  - P-K1-007-b (abstract): "within this operationalization of the AMD model, no directional information beyond the daily trend regime was observed: when the signal aligns with the trend it is correct 62–71% of the time (Cohen's h = 0.23–0.43); when it opposes the trend it is correct only 25–30% of the time"
- Numeric claims: N = 484, 57% (P-K1-007-a); 62–71%, 25–30% (P-K1-007-b).
- Tags: port of D.1 families A (session clock) and B (reference-level breakout) on NQ. Intraday-feasible. Non-survivor for the AMD pattern itself.
- Clusters tagged: [K1].

### K1-008 Ladia (2026), Opening-Range Reversal in Dow Jones Futures: Evidence Consistent with 0DTE Hedging Pressure
- Registry id: K1-008. Citation: Ladia (2026), SSRN 7124578, 10.2139/ssrn.7124578. Container 4.
- Retrieval: ABSTRACT ONLY.
- Mechanism: short-side reversal after the open in YM; performance concentrated in the earliest entry windows; regime break around 2023, attributed tentatively to 0DTE option hedging flow.
- Products and horizon: E-mini Dow (YM); intraday, opening window.
- Cost assumptions: gross expectancy only (P-K1-008-a); net [unverified]. Data window: January 2023 to March 2026 (194 trades); reconstructed 2021 to 2022 sample (115 trades).
- Quality tells: exact parameters withheld (P-K1-008-b); small N; pre-2023 sample below breakeven; single author.
- Verbatim passages:
  - P-K1-008-a (abstract): "This paper documents a short-side opening reversal pattern in E-mini Dow futures over 194 trades from January 2023-March 2026. Under a symmetric 1:1 payoff structure, the strategy produced a 59.79% win rate and gross expectancy of 0.196R per trade. Performance was concentrated in the earliest entry windows: trades in the first three timing buckets won 65.56% of the time, compared with 39.53% of the time in the final two."
  - P-K1-008-b (abstract): "A reconstructed pre-2023 historical sample (N = 115, provisionally dated to approximately 2021-2022) shows a win rate of 45.22%, below breakeven and significantly lower than the 2023-2026 sample (Fisher's exact test, p = 0.0135). ... Exact trading parameters are withheld, limiting independent replication."
- Numeric claims: 194 trades, 59.79%, 0.196R, 65.56% / 39.53% (P-K1-008-a); N = 115, 45.22%, p = 0.0135 (P-K1-008-b).
- Tags: port of D.1 families B and C (opening-range reversal) on YM, with a new mechanism story (0DTE hedging flow). Intraday-feasible.
- Clusters tagged: [K1].

### K1-009 Mesfin (2026), Sequential Structure in Intraday Futures Data: LSTM vs Gradient Boosting on MNQ
- Registry id: K1-009. Citation: Mesfin, M. (2026), SSRN 6792161 = arXiv:2605.17724 (one source). Container 4 (found), full text via container 3 (arXiv). Same author as D.1 A14/B5/C5 (arXiv 2605.04004 = SSRN 6709401, MNQ OHLCV falsification study: see D.1, not re-read).
- Retrieval: full text, PDF https://arxiv.org/pdf/2605.17724 (8 pages). (SSRN route 403; superseded.)
- Mechanism: gradient boosting on engineered daily/intraday features and an LSTM on 5-minute return sequences, predicting whether the MNQ session close exceeds the 10:30 ET bar open by more than 10 points; null out of sample.
- Products and horizon: MNQ, 5-minute RTH bars (09:30 to 16:00 ET); 10:30 ET to the RTH close (16:00 ET = 15:00 CT, before 15:08 CT).
- Cost assumptions: none (accuracy study).
- Data window: December 2021 to September 2025, 944 usable days (P-K1-009-c); OOS folds 2023, 2024, 2025.
- Quality tells: independent researcher; walk-forward, permutation tests, explicit null; best fold (54.76%) rejected by permutation (P-K1-009-d).
- Verbatim passages:
  - P-K1-009-a (abstract): "The target variable is binary: whether the session close exceeds the 10:30 AM bar open by more than ten points. All models are evaluated against a 51.8% base rate. No configuration produces out-of-sample accuracy materially above base rate."
  - P-K1-009-b (abstract): "Combined out-of-sample accuracies range from 50.00% to 50.89% ... The LSTM produces a combined OOS accuracy of 50.59%. Permutation test p-values are 0.135 for the best gradient boosting configuration and"
  - P-K1-009-c (Table 1): "Primary instrument MNQ (Micro E-Mini Nasdaq 100) / Bar resolution 5-minute OHLCV (RTH only) / Session definition 09:30–16:00 ET ... Date range December 2021 – September 2025"
  - P-K1-009-d (Sec. on GB-Intraday): "the permutation test result is decisive: actual Fold 3 accuracy of 54.76% against a shuffled mean of 50.04% (standard deviation 3.99%) produces a p-value of 0.135."
- Numeric claims: 51.8% base (P-K1-009-a); 50.00–50.89%, 50.59%, 0.135 (P-K1-009-b); Dec 2021 to Sep 2025 (P-K1-009-c); 54.76% vs 50.04%, p = 0.135 (P-K1-009-d). Checked against the full text.
- Tags: port of D.1 family F (data-native statistics / ML) on MNQ. Intraday-feasible. Non-survivor.
- Clusters tagged: [K1].

### K1-014 Mesfin (2026), A Validated Volatility-Volume-Gap Classifier for Regime Identification in MNQ Intraday Data
- Registry id: K1-014. Citation: Mesfin, M. (2026b), arXiv:2605.11423. Container 3 (arXiv).
- Retrieval: full text, PDF https://arxiv.org/pdf/2605.11423 (8 pages).
- Mechanism: a day-type classifier (large overnight gap AND large first-30-minute return AND first-bar volume well above baseline, expanding-window thresholds) marks "high-stress" MNQ days; on those days price drifts up through the morning, peaks 14:00 to 15:30 ET, and gives back late. Eight directional strategies on those days: none passed.
- Products and horizon: MNQ 5-minute bars; intraday (entries after the first 30 minutes, exit by the close). The peak window 14:00 to 15:30 ET is 13:00 to 14:30 CT, inside the XFA window.
- Cost assumptions: 2.0 points round trip on all net figures (P-K1-014-c).
- Data window: 947 trading days, 2021 to 2025.
- Quality tells: independent researcher; honest null; tiny event sample (40 days); year-to-year sign flips.
- Verbatim passages:
  - P-K1-014-a (abstract): "The classifier activates on roughly 4.4% of trading days — 40 days across the full dataset. Those days show a mean next-day return spread of 25.6 basis points above non-classifier days, and 77.6% of them reverse from their intraday peak before the session closes, with a mean peak-to-close giveback of 11.73 points. The intraday path is characteristic: gradual drift through the morning, a peak between 14:00 and 15:30, and then a late-session reversal."
  - P-K1-014-b (abstract): "Eight directional strategy configurations were tested on classifier-positive days. None passed. The best result was T = 1.46 on 127 out-of-sample (OOS) trades with a mean net of +7.80 points, using a reversal entry with an OLS regression filter. 2024 produced a net loss that broke year stability."
  - P-K1-014-c (data table): "Friction assumption 2.0 points round-trip (all net figures)"
- Numeric claims: 4.4%, 40 days, 25.6 bp, 77.6%, 11.73 points (P-K1-014-a); T = 1.46, 127 trades, +7.80 points (P-K1-014-b); 2.0 points (P-K1-014-c). Checked against the full text abstract.
- Tags: port of D.1 families D (volatility state) and A (session clock: late-session reversal) on MNQ. Intraday-feasible (the 14:00 to 15:30 ET peak is 13:00 to 14:30 CT). Non-survivor as a strategy.
- Clusters tagged: [K1].

### K1-010 Ntingana (2026), Fractal Market Dynamics: Mandelbrot's Long-Memory Theory and Intraday NQ Futures Trading
- Registry id: K1-010. Citation: Ntingana (2026), SSRN 6744643, 10.2139/ssrn.6744643. Container 4.
- Retrieval: ABSTRACT ONLY.
- Mechanism: rolling Hurst exponent (variance-ratio) regime filter on 5-minute NQ bars; trades in "persistent" regimes do better; realised-vol z-score sizing.
- Products and horizon: NQ, 5-minute bars, intraday; base strategy unspecified in the abstract [unverified].
- Cost assumptions: "average net P&L" reported (P-K1-010-a); cost model [unverified]. Data window: 2018 to 2025.
- Quality tells: single author; the underlying entry rule is not stated in the abstract; Monte Carlo "Davey framework" thresholds, not an out-of-sample test; per-trade dollar P&L without contract count.
- Verbatim passages:
  - P-K1-010-a (abstract, Crossref single-unescape copy): "Using 565,481 five-minute bars from 2018 to 2025, I compute rolling Hurst exponents via the variance ratio method and classify each bar into one of three regimes: persistent (H > 0.55), neutral (0.45 ≤ H ≤ 0.55), and antipersistent (H < 0.45). Trades taken during persistent regimes achieve a win rate of ... 52.5% and an average net P&L of $153. The same trades in anti-persistent conditions yield a 44.8% win rate and $47 average P&L"
  - P-K1-010-b (abstract): "Across 2,500 Monte Carlo simulations using the Davey validation framework, the combined system achieves a return-to-drawdown ratio of 6.36x and a risk of ruin of 1.2%."
- Numeric claims: 565,481 bars; 52.5%, $153; 44.8%, $47 (P-K1-010-a); 6.36x, 1.2% (P-K1-010-b).
- Tags: port of D.1 families D and F (volatility/persistence state filter) on NQ. Intraday-feasible (as described).
- Clusters tagged: [K1].

### K1-011 Chen, Tai, Yang (2013), How the Last Call Auction of Underlying Stock Market Affects the Price Behaviors of Continuous Trading Index Futures
- Registry id: K1-011. Citation: SSRN 2318843, 10.2139/ssrn.2318843. Container 2 (closing-auction flows).
- Retrieval: ABSTRACT ONLY.
- Mechanism: index futures trade continuously while the cash market runs a hidden 5-minute closing call auction; futures show higher volume and excess volatility, and lower average return, in that window.
- Products and horizon: TAIFEX index futures (Taiwan); last 5 minutes of the cash session. Transfer to CME equity futures: the NYSE/Nasdaq closing auctions end 15:00 CT (imbalance publication from 14:50 CT); the window sits before 15:08 CT.
- Cost assumptions: [unverified]. Data window: [unverified].
- Quality tells: SSRN working paper, English unclear, market structure differs (Taiwan hidden auction vs published US imbalances).
- Verbatim passages:
  - P-K1-011-a (abstract): "we study the effects of around the last five minutes call auction of underlying stock market on price behaviors of continuous trading TAIFEX index futures. First, continuous trading enables a better reaction to new information and improved risk sharing, resulting in a larger trading volume."
  - P-K1-011-b (abstract): "high systematic volatility loadings, during the hided call auction period in stock market, will increase their price and lowers their average return. With high uncertainty during last 5 minutes call auction period with hided information, futures markets are characterized by price volatility in excess of the theoretical volatility of equilibrium prices."
- Numeric claims: "last five minutes" only (P-K1-011-a).
- Tags: port of D.1 family A (session clock: cash-close window) with a new element (the closing-auction window). Intraday-feasible (window ends before 15:08 CT on US markets).
- Clusters tagged: [K1].

### K1-012 Fassas (2021), Price Discovery in a New Futures Market: Micro E-Mini Index Futures
- Registry id: K1-012. Citation: Fassas, A. P. (2021), The Journal of Derivatives, 10.3905/jod.2021.1.131. Container 1/3.
- Retrieval: ABSTRACT ONLY. Routes failed: doi.org to pm-research.com (HTTP 429), Wayback of the journal page (404), Unpaywall (not OA), Semantic Scholar (no open PDF). Text read: abstract and "Key Findings" from api.semanticscholar.org (single-paper lookup).
- Mechanism: price discovery between each Micro E-mini and its E-mini (MES/ES, MNQ/NQ, MYM/YM, M2K/RTY) in the first three months after launch: micros contribute about equally.
- Products and horizon: all four micro/E-mini pairs; intraday data. Data window: 3 months after the May 2019 launch [launch date unverified; "3-month period" verbatim].
- Cost assumptions: none (price-discovery measures).
- Quality tells: journal article (practitioner-academic journal); very short sample at launch; micro liquidity has changed since.
- Verbatim passages:
  - P-K1-012-a (abstract, S2): "These contracts (sized at the one-tenth of their E-mini counterpart value) allow investors to gain a more affordable exposure to the S&P 500, Nasdaq 100, Dow Jones Industrial Average, and Russell 2000 indices. Using intraday data during a 3-month period, this article finds that the new smaller-sized stock index futures contracts function surprisingly well in their price discovery performance at their infancy stage, as they contribute approximately equal amounts to the information transmission process with the established E-mini index futures."
  - P-K1-012-b (Key Findings, S2): "The new smaller-sized Micro E-mini futures contracts function surprisingly well in their price discovery performance at their infancy stage, as they contribute approximately equal amounts to the information transmission process with the established E-mini index futures."
- Numeric claims: "3-month period", "one-tenth" (P-K1-012-a). Information shares [unverified].
- Tags: new to the program (micro against E-mini lead-lag inside one exposure). Intraday-feasible as a fact; as a strategy it would need sub-second reaction (not feasible for this account). Evidence against a tradable micro-lags-mini gap.
- Clusters tagged: [K1].

### K1-013 Parekh and Heller (2026), A liquidity-driven framework for Micro E-mini NASDAQ-100 Futures (MNQ1)
- Registry id: K1-013. Citation: Journal of Science & Engineering (Manalapan High School authors), 10.64804/y4pjsg07. Container 4 (surfaced by Crossref).
- Retrieval: full text, PDF https://j.snerds.org/index.php/jse/article/download/132/117 (the published item is a one-page abstract; nothing more exists to read).
- Mechanism: discretionary ICT-style confluences (liquidity sweeps, fair value gaps, order blocks, breaks of structure) coded in Pine Script on MNQ.
- Products and horizon: MNQ, intraday. Cost assumptions: none stated. Data window: none stated.
- Quality tells: high-school project; the only metric is a win-rate gain against the authors' own manual trading; no sample, no costs, no test.
- Verbatim passages:
  - P-K1-013-a (abstract): "The model utilizes a multitude of technical confluences, including liquidity sweeps, fair value gaps (FVGs), inverse fair value gaps (iFVGs), breaks of structure, and order blocks, to identify high probability trade entries. Each confluence was individually programmed using TradingView's Pine script"
  - P-K1-013-b (abstract): "highlight the importance of algorithmic trading in intraday futures trading strategies, evident through our 11% increase in win rate compared to manually trading without our tool."
- Numeric claims: "11% increase in win rate" (P-K1-013-b), baseline unstated.
- Tags: port of D.1 family B (reference-level breakout / sweep) on MNQ. Intraday-feasible. No evidential weight.
- Clusters tagged: [K1].

### K1-015 Kurov and Lasser (2004), Price Dynamics in the Regular and E-Mini Futures Markets
- Registry id: K1-015. Citation: Journal of Financial and Quantitative Analysis 39(2), 10.1017/s0022109000003112; SSRN 386965 (2003) same paper. Container 10 (Kurov).
- Retrieval: ABSTRACT ONLY. Routes failed: SSRN (403), Unpaywall (no OA location for the JFQA DOI; SSRN landing only for the WP), Semantic Scholar (not found). Text read: Crossref abstracts (JFQA and SSRN).
- Mechanism: in ES and NQ, price discovery starts in the E-mini; exchange locals trade informatively in the E-mini around large floor trades (proximity to order flow).
- Products and horizon: S&P 500 and Nasdaq-100 regular (floor) and E-mini futures; transaction-level, intraday.
- Cost assumptions: [unverified]. Data window: [unverified].
- Quality tells: JFQA; uses CFTC trader-type codes the program cannot observe; the floor contracts no longer trade.
- Verbatim passages:
  - P-K1-015-a (JFQA abstract, Crossref): "This paper examines the price dynamics in the S&P 500 and Nasdaq-100 index futures contracts. By utilizing transactions data with attached trader type identification codes, we are able to analyze price dynamics for trades initiated by exchange locals and off-exchange customers."
  - P-K1-015-b (SSRN abstract, Crossref): "The empirical results show that price discovery appears to be initiated in the E-mini index futures contracts and that trades initiated by exchange locals seem to be more informative than those initiated by off-exchange traders. Furthermore, results show that exchange locals appear to make informed trades on the E-mini contracts around large trades that occur on the open outcry floor."
- Numeric claims: none.
- Tags: new to the program only as background (price leadership inside one exposure; corroborates K1-001 for NQ). Not implementable: needs trader-type codes and a floor contract. Intraday, but no tradable signal.
- Clusters tagged: [K1].

### K1-016 Kurov (2008), Information and Noise in Financial Markets: Evidence from the E-Mini Index Futures
- Registry id: K1-016. Citation: Journal of Financial Research 31(3), 10.1111/j.1475-6803.2008.00239.x; SSRN 1086021 same paper. Container 10.
- Retrieval: ABSTRACT ONLY. Routes failed: SSRN (403), Unpaywall (not OA). Text read: Crossref abstracts.
- Mechanism: exchange member firms' trades carry over 60% of intraday price discovery in three E-mini index futures; off-exchange traders add noise.
- Products and horizon: "three actively traded index futures markets" (which three is [unverified]; presumably E-mini S&P, Nasdaq-100 and a third); intraday.
- Cost assumptions: [unverified]. Data window: [unverified].
- Quality tells: peer-reviewed; trader-type data unobservable to the program.
- Verbatim passages:
  - P-K1-016-a (JFR abstract): "I examine the informational contributions and effects on transitory volatility of trades initiated by different types of traders in three actively traded index futures markets. The results show that trades initiated by exchange member firms account for more than 60% of price discovery during the trading day."
  - P-K1-016-b (JFR abstract): "I also find that off‐exchange traders introduce more noise into the prices than do exchange members."
- Numeric claims: "more than 60%" (P-K1-016-a).
- Tags: background only; not implementable (needs trader-type codes). Intraday.
- Clusters tagged: [K1].

### K1-017 CME Group OpenMarkets (2023), What the Russell Reconstitution Means for Equity Markets
- Registry id: K1-017. Citation: Payal Shah, CME Group OpenMarkets, 2023. Container 6.
- Retrieval: full text, HTML, Wayback https://web.archive.org/web/20250715002020/https://www.cmegroup.com/openmarkets/equity-index/2023/What-the-Russell-Reconstitution-Means-for-Equity-Markets.html
- Mechanism (as described, no test): the June reconstitution is a large supply/demand shift in single names and one of the highest-volume days; RTY is presented as a hedging tool, with BTIC at the index close on reconstitution day. No claim about the index-level (RTY) price path.
- Products and horizon: RTY (E-mini Russell 2000); reconstitution day, close.
- Cost assumptions: none. Data window: 2023 preliminary reconstitution statistics.
- Quality tells: exchange marketing article; descriptive; no data on futures returns.
- Verbatim passages:
  - P-K1-017-a: "The annual reconstitution is one of the most significant drivers of short-term shifts in supply and demand for U.S. equities, often leading to sizable price movements and volatility in individual company names or industry sectors. The final day of the reconstitution is typically one of the highest trading volume days of the year in U.S. equity markets."
  - P-K1-017-b: "On the reconstitution day, The Basis Trade at Index Close (BTIC) mechanism permits RTY contracts to be traded at a spread to the day's official index closing value and serves as an alternative to trading many cash baskets."
  - P-K1-017-c: "A total of 297 companies will be joining the Russell 2000 Index ... 192 companies are departing the index."
- Numeric claims: 297 joining, 192 departing (P-K1-017-c); "$12 trillion" benchmarked [in text, not load-bearing].
- Tags: port of D.1 family E (calendar and events) to RTY; the stated effect is stock-level and volume-level, not a directional index effect. Intraday-feasible as a calendar flag (the close is 15:00 CT; BTIC is a close-referenced trade type the program does not use).
- Clusters tagged: [K1].

### K1-018 CME Group OpenMarkets (2025), How Does the Russell Reconstitution Impact Equity Markets?
- Registry id: K1-018. Citation: Bob Iaccino, CME Group OpenMarkets, 2025. Container 6.
- Retrieval: full text, HTML, Wayback https://web.archive.org/web/20250906141922id_/https://www.cmegroup.com/openmarkets/equity-index/2025/How-Does-the-Russell-Reconstitution-Impact-Equity-Markets.html
- Mechanism (as described): passive funds rebalance into the closing auction of the final pre-reconstitution session; heavy volume; FROM 2026 the reconstitution becomes semi-annual (June and November), which the article expects to spread the flow.
- Products and horizon: RTY, M2K; the reconstitution-day close.
- Cost assumptions: none. Data window: 2025 calendar.
- Quality tells: exchange marketing; descriptive; the calendar change matters for any date-based rule.
- Verbatim passages:
  - P-K1-018-a: "The final trading session before the reconstitution, which falls on June 27 this year, is typically one of the highest-volume days of the year for U.S. stocks. During the last hour of that session, known as the "closing auction," trillions of dollars may shift across portfolios as fund managers execute trades to align with the new index compositions."
  - P-K1-018-b: "FTSE Russell announced plans to transition to a semi-annual reconstitution schedule starting in 2026. Instead of one major reshuffle in June, the indexes will now be updated twice a year – once in June and again in November."
  - P-K1-018-c: "Rank Day: April 30, 2025 ... Reconstitution Effective Date: June 27, 2025. The actual reconstitution takes effect after the market closes."
- Numeric claims: dates (P-K1-018-c); "trillions of dollars" (P-K1-018-a) is rhetorical, [unverified].
- Tags: port of D.1 family E (event calendar) to RTY/M2K. Intraday-feasible as a calendar flag; no directional evidence.
- Clusters tagged: [K1].

### K1-019 CME Group OpenMarkets (2021), 2021 Russell Index Reconstitution Results
- Registry id: K1-019. Container 6.
- Retrieval: full text, HTML, Wayback https://web.archive.org/web/20220227003615/https://www.cmegroup.com/openmarkets/equity-index/2021-russell-index-reconstitution-results.html
- Mechanism: none; a descriptive recap (growth/value shifts, Russell futures open interest). Passed the title pre-filter, empty on reading.
- Verbatim passages:
  - P-K1-019-a: "Russell 1000 Value futures have shown tremendous growth since the 2020 reconstitution, with open interest reaching a record high of 43,302 on June 17, 2021."
  - P-K1-019-b: "Since the start of the year, we have seen notable increases in volume on Russell 2000 Index-based futures (RTY) as market participants have used our markets to manage small-cap equity market price risk"
- Numeric claims: 43,302 open interest (P-K1-019-a), not load-bearing.
- Tags: no mechanism; not a candidate. Clusters tagged: [K1].

### K1-020 CME Institute course, Understanding Intermarket Spreads
- Registry id: K1-020. Container 6. Retrieval: full text, HTML, Wayback https://web.archive.org/web/20251214111129id_/https://www.cmegroup.com/education/courses/introduction-to-equity-index-products/understanding-equity-intermarket-spreads.html
- Mechanism: none tested; defines the NQ against ES relative-value (inter-market) spread as a view on tech against the broad market.
- Products and horizon: NQ, ES; no horizon. Cost assumptions: none. Data window: none.
- Quality tells: exchange education page; no evidence.
- Verbatim passages:
  - P-K1-020-a: "you could take a spread position between two different stock indexes by buying one and selling another. If you're bullish on the technology sector versus the broad market, you could buy the NASDAQ futures and sell the E-mini S&P."
  - P-K1-020-b: "The point of entering into an inter-market spread is to trade on the differences in the two respective contracts rather than the direction of the overall market. These types of trades are sometimes referred to as relative value trades."
- Numeric claims: none. Tags: new to the program as a construction (inside-K1 relative value); no evidence of an edge. Intraday-feasible as a construction. Clusters tagged: [K1].

### K1-021 CME Institute course, Spread Trading with E-mini Russell 2000 Futures
- Registry id: K1-021. Container 6. Retrieval: full text, HTML, Wayback https://web.archive.org/web/20251018171812id_/https://www.cmegroup.com/education/courses/learn-about-e-mini-russell-2000-futures/spread-trading-with-e-mini-russell-2000-futures.html
- Mechanism: none tested; RTY against ES (small against large cap) spreads, notional ratioing (about two RTY per ES), exchange margin offsets.
- Products and horizon: RTY, ES, S&P MidCap, Russell 1000 and style futures. No horizon, no costs, no data.
- Quality tells: education page; the ratio and margin-offset facts matter for construction (TopstepX margin treatment of spreads is not covered here).
- Verbatim passages:
  - P-K1-021-a: "a trader believes that small cap stocks will outperform large cap stocks. To take advantage of this viewpoint the trader would initiate a spread trade that would consist of going long the E-mini Russell 2000 futures contract and simultaneously shorting the E-mini S&P 500 futures contract."
  - P-K1-021-b: "the contract notional size of all stock index futures is not identical, hence if you were going to spread stock index futures, you might have to do a ratio such as two E-mini Russell 2000 futures for every one E-mini S&P 500 futures to obtain a more dollar-neutral position."
- Numeric claims: "two ... for every one" (P-K1-021-b), illustrative. Tags: construction only (inside-K1 relative value, RTY against ES). Clusters tagged: [K1].

### K1-022 CME Group, Managing an Equity Index Reconstitution
- Registry id: K1-022. Container 6. Retrieval: full text, HTML, Wayback https://web.archive.org/web/20250209023120id_/https://www.cmegroup.com/education/articles-and-reports/managing-an-equity-index-reconstitution.html
- Mechanism (described, untested): index trackers trade additions/deletions at the reconstitution-day cash close; futures used to carry exposure (EFP, BTIC); small-cap liquidity concentrates at the close and the open.
- Products and horizon: ES, RTY; reconstitution-day close. No data, no costs.
- Verbatim passages:
  - P-K1-022-a: "To eliminate tracking error vs. the index, the investor must buy all the additions to the index and sell all the deletions on the cash close of the reconstitution day."
  - P-K1-022-b: "Intraday liquidity in small caps tends to be much thinner than large caps stocks. Thus, more volume tends to trade at the close and to some degree at the open."
- Numeric claims: none. Tags: port of D.1 family E (event calendar) and A (close window) to RTY; no directional claim. Intraday-feasible as a calendar flag. Clusters tagged: [K1].

### K1-023 CME Group (2026), The 2026 Russell Reconstitution: Twice the Friction, Twice the Need for Futures
- Registry id: K1-023. Container 6. Retrieval: full text, HTML, Wayback https://web.archive.org/web/20260513102145id_/https://www.cmegroup.com/articles/2026/the-2026-russell-reconstitution.html
- Mechanism (described): semi-annual reconstitution from 2026; closing-auction volume on reconstitution Friday; RTY and M2K as tools.
- Products and horizon: RTY, M2K; reconstitution-day close. Data window: closing-auction dollar volume 2017 to 2025 (Exhibit 1).
- Quality tells: marketing. CONFLICT: this page says the second 2026 reconstitution is in December; K1-018 (2025) says November (P-K1-018-b against P-K1-023-a). The schedule must be taken from FTSE Russell directly before any date rule is built [unverified which is right].
- Verbatim passages:
  - P-K1-023-a: "with the transition from an annual to a semi-annual reconstitution schedule, starting in 2026 (June and December). This shift – culminating with the June rebalance after the market close on Friday, June 26"
  - P-K1-023-b: "At last year's reconstitution, $217.2 billion U.S. stocks traded in the closing moments of Friday trading on the New York Stock Exchange (NYSE) and Nasdaq exchanges."
- Numeric claims: $217.2 billion (P-K1-023-b), source "Nasdaq, NYSE data as of June 2025"; June 26, 2026 (P-K1-023-a).
- Tags: port of D.1 family E (event calendar) to RTY/M2K. Intraday-feasible as a calendar flag; no directional evidence. Clusters tagged: [K1].

### K1-024 Databento (2025), Real-time NYSE imbalance feeds added to Databento US Equities
- Registry id: K1-024. Container 7. Retrieval: full text, HTML, https://databento.com/blog/NYSE-imbalance-feeds (direct).
- Mechanism (data availability, not a tested edge): NYSE, NYSE Arca and NYSE American auction imbalance messages (reference price, imbalance and paired quantity, indicative match price) are available real-time and historically (from the January 2025 release) in Databento US Equities; the post asserts they help anticipate direction at the open or close. Relevant to K1 as the only named source for a closing-imbalance signal ahead of the 15:00 CT cash close (inside the XFA window). Nasdaq closing-cross (NOII) data are not covered by this post.
- Products and horizon: cash equities auction data (signal instrument), for a possible K1 close-window rule. Cost: data subscription (no spend authorised; noted only).
- Quality tells: vendor announcement; the directional claim is marketing, untested.
- Verbatim passages:
  - P-K1-024-a: "our Databento US Equities service now includes real-time imbalance data from the NYSE, NYSE Arca, and NYSE American. Historical imbalance data for these venues was already made available earlier as part of the full order book Integrated feeds in our January 2025 release."
  - P-K1-024-b: "By revealing unmatched buy and sell interest in real time, imbalances show how supply and demand shift leading up to the auction, helping firms anticipate match prices and market direction at the open or close."
  - P-K1-024-c: "With floor interest contributing over 40% of Closing Auction volume, NYSE imbalance data plays a critical role in sizi[ng]"
- Numeric claims: history from January 2025 (P-K1-024-a); "over 40%" floor share (P-K1-024-c), vendor figure [unverified].
- Tags: new to the program (closing-auction imbalance as a signal for K1 futures in the 14:50 to 15:00 CT window). Intraday-feasible (window ends before 15:08 CT). No evidence of an edge in this source; see K1-011 for the only futures-side evidence (Taiwan, abstract only).
- Clusters tagged: [K1].

### K1-025 Giot (2003/2005), Implied Volatility Indices as Leading Indicators of Stock Index Returns?
- Registry id: K1-025. Citation: CORE Discussion Paper 2002/50, SSRN 371461 (2003); published as "Relationships Between Implied Volatility Indexes and Stock Index Returns", Journal of Portfolio Management (2005), 10.3905/jpm.2005.500363 (one source). Container 8.
- Retrieval: ABSTRACT ONLY. Routes failed: SSRN (403), Unpaywall (SSRN landing only), guessed CORE (UCLouvain) PDF paths and their Wayback copies (404), JPM (not OA). Text read: Wayback SSRN abstract page https://web.archive.org/web/2024/https://papers.ssrn.com/sol3/papers.cfm?abstract_id=371461 and the Crossref abstract.
- Mechanism: rising VXN (VIX) goes with falling Nasdaq-100 (S&P 100) returns contemporaneously; very high implied-volatility LEVELS precede positive short-term index returns ("oversold" contrarian signal).
- Products and horizon: Nasdaq-100 and S&P 100 cash indices; VXN and VIX. Horizon "short term" - the forward-return windows are [unverified] from the abstract (believed multi-day; not confirmed).
- Cost assumptions: [unverified]. Data window: [unverified].
- Quality tells: published practitioner journal; pre-2003 sample; level-based, overlapping-horizon statistics likely [unverified].
- Verbatim passages:
  - P-K1-025-a (abstract): "when the VIX or VXN indices of implied volatility increase, the S&P100 and NASDAQ100 stock indices exhibit on average negative returns, hence the 'fear factor' associated with high levels of implied volatility in financial markets."
  - P-K1-025-b (abstract): "very high levels of implied volatility can on a statistical basis be viewed as signalling an imminent increase in stock indices, at least on a short term basis. ... traders willing to enter 'oversold' markets should wait until extremely high levels of implied volatility are witnessed, and their strategy should be strictly on a short-term basis."
- Numeric claims: none in the abstract.
- Tags: port of D.1 family D (volatility state) with VXN as the non-CME input for NQ; related to K1-005 (Seeck, VXN band). Intraday feasibility UNKNOWN: horizon unverified; if multi-day (likely), NOT intraday-feasible as a hold, though a rule could read the VXN level and trade intraday.
- Clusters tagged: [K1].

### K1-026 Zarattini and Aziz (2023), Can Day Trading Really Be Profitable? (5-minute ORB on QQQ)
- Registry id: K1-026. Citation: SSRN 4416622 (2023); 10.2139/ssrn.4898296 is a later SSRN posting of the same title (one source). Container 11 (found through a Crossref follow-up of practitioner discovery; not in D.1's log, grep "zarattini" = 0).
- Retrieval: full text, PDF from the authors' firm site, https://concretumgroup.com/wp-content/uploads/2026/02/Can-Day-Trading-Really-Be-Profitable.pdf (SSRN 403).
- Mechanism: 5-minute opening-range breakout on the Nasdaq-100 ETF: direction of the first 5-minute candle, enter at the open of the second candle, stop at the first candle's opposite extreme, target 10R or exit at the close.
- Products and horizon: QQQ and TQQQ (Nasdaq-100); intraday, flat at the close (P-K1-026-b). Transfer to NQ/MNQ is direct in exposure; note the ETF close is 15:00 CT, before 15:08 CT.
- Cost assumptions: $0.0005/share commission; no slippage (P-K1-026-b, and "We assumed no slippage in fills" in the rules table).
- Data window: 1 January 2016 to 17 February 2023 (P-K1-026-a), 1,795 trades.
- Quality tells: practitioner authors (Concretum); one instrument, one parameter set shown then stop-loss sensitivity optimised (ATR stop grid) in-sample; leverage-driven headline returns; no slippage; no out-of-sample; D.1 B-family evidence on MES (D.1 B5 MNQ falsification, B4/B8) and the K4-050 panel (ORB fails after $25 futures costs) point the other way.
- Verbatim passages:
  - P-K1-026-a (Sec. 2): "Our analysis was conducted during the period of January 1, 2016 to February 17, 2023."
  - P-K1-026-b (Sec. 2): "if during the first 5 minutes the market moved up, we took a bullish position starting from the second candle's opening price. Conversely, if the first 5-minute candle was negative, we took a bearish position at the open of the second 5-minute candle. ... The stop loss was placed at the low of the day (which was the low of the first 5-minute candle) for a long trade ... We set the profit target at 10x the $R. Should the target not have been reached by the end of the day (EoD), we liquidated the position at market closure. We assumed a starting capital of $25,000, a maximum leverage of 4x, and a commission of $0.0005/share traded."
  - P-K1-026-c (Sec. 3): "a $25,000 day trading account on January 1, 2016 would be worth $192,806 (net of commissions) as of February 17, 2023. That is an outstanding total return of 675%."
  - P-K1-026-d (Sec. 3): "The annualized alpha was 33% (net of commissions) and is highly significant (p.value = 0.0025). ... out of 1,795 trades, 51% were long trades while 49% were short. The annualized Sharpe Ratio was 1.12 while the annualized rate of return was 31%."
- Numeric claims: sample dates (P-K1-026-a); $0.0005/share, 10R, 4x (P-K1-026-b); $192,806, 675% (P-K1-026-c); alpha 33%, p = 0.0025, 1,795 trades, Sharpe 1.12, 31% (P-K1-026-d). Checked against the full text.
- Tags: port of D.1 family B (reference-level breakout: opening range) on the Nasdaq-100. Intraday-feasible (exit at the 15:00 CT cash close).
- Clusters tagged: [K1].

### K1-027 Zarattini and Aziz (2023), Volume Weighted Average Price (VWAP): The Holy Grail for Day Trading Systems
- Registry id: K1-027. Citation: SSRN 4631351. Container 11 (Crossref follow-up).
- Retrieval: full text, PDF https://concretumgroup.com/wp-content/uploads/2026/02/Volume-Weighted-Average-Price.pdf
- Mechanism: stop-and-reverse on the Nasdaq-100 ETF relative to the session VWAP, 1-minute bars: long above VWAP, short below; flat overnight.
- Products and horizon: QQQ, TQQQ; intraday, about 22,000 trades over the sample (roughly 15 a day) (P-K1-027-c).
- Cost assumptions: $0.0005/share; no slippage (P-K1-027-b).
- Data window: 2 January 2018 to 28 September 2023, 1-minute data.
- Quality tells: practitioner; no slippage with ~15 flips a day and a 17% hit ratio makes the result cost-fragile; for MNQ market orders each flip pays the spread and fees, and the trade rate approaches Topstep's high-rate language; no out-of-sample.
- Verbatim passages:
  - P-K1-027-a (Sec. 3): "The portfolio maintains a long exposure when QQQ is trading above the VWAP and reverses its exposure when the price of QQQ moves below the VWAP. No positions are held overnight."
  - P-K1-027-b (Sec. 3.4): "Since we initiated our system with a small account of only $25,000, we assumed no slippage in our order fills. ... For all the backtest, we factored in a commission rate of $0.0005 per share"
  - P-K1-027-c (Sec. 3.7 and Table 3): "the VWAP day trading system for QQQ, with a total commission of only $6,547, achieves an ending capital of $192,656. ... The active VWAP strategies incurred about 22,000 trades." Table 3: "VWAP TT (QQQ) $25,000 $192,656 13,094,444 6,547 21,967"
  - P-K1-027-d (abstract): "This performance is marked by a maximum drawdown of just 9.4% and a Sharpe Ratio of 2.1. In contrast, a passive buy-and-hold strategy in QQQ during the same period would have returned 126%"
- Numeric claims: $192,656, 21,967 trades, $6,547 (P-K1-027-c); MDD 9.4%, Sharpe 2.1, B&H 126% (P-K1-027-d). Checked against the full text. Hit ratio "approximately 17%" (Sec. 3.7 text).
- Tags: port of D.1 families B and F (VWAP as a data-native reference level) on the Nasdaq-100. Intraday-feasible in horizon; cost and trade-rate feasibility doubtful at 1-minute flips.
- Clusters tagged: [K1].


## 4. Flags for K8

- Kurov, Olson, Wolfe 2023/2024 J. Commodity Markets, "Have the causal effects between equities, oil prices, and monetary policy changed over time?" (10.1016/j.jcomm.2024.100446): legs equity index and crude oil (and rates); equity-oil causality. K1 x K4 (x K2).
- Zangelidis and Rezitis 2026, Resources Policy, "Topology of intraday realized volatilities across commodity indices, copper futures, the U.S. dollar index, and the NASDAQ: an unrestricted multivariate HAR-VAR" (10.1016/j.resourpol.2026.105934): legs NASDAQ (K1) with copper (K5), dollar (K3) and commodity indices (K4/K5/K6); volatility spillover topology.

## 5. Registry ids appended

- K1-001 to K1-027 (27 claim lines, worker K1, all clusters_tagged ["K1"]). K1-001 carries a wrong DOI (see section 0). No K1 claim is a panel source.
