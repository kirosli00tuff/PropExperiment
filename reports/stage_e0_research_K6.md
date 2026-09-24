# Stage E.0 research log, cluster K6 (agriculture and livestock)

Worker: ClusterReader-K6-OpusHigh. STATUS: COMPLETE.

## 0. Header

- Cluster: K6. Products: ZC corn, ZW wheat, ZS soybeans, ZM soybean meal, ZL soybean oil, HE lean hogs, LE live cattle.
- Start 21:20 PDT (2026-09-23). Paused 21:58 to 01:10 PDT (usage limit; not work time). Resumed 01:12. End 01:22 PDT (2026-09-24).
  Work time about 38 + 11 minutes.
- Stop reason: branch 2 of rule (d). Every container (1-12) had at least 4 distinct logged queries or page lookups and its
  last two produced no new passing item. The 60-full-text branch was not reached (34 full-text reads).
- Counts: considered about 2,300 titles or records (about 1,000 of them farmdoc daily titles screened in bulk; per-container
  figures in section 1); rejected rows R-K6-001 to R-K6-070 (many rows group several items); passed 49 K6 sources
  (K6-001 to K6-051, excluding K6-005 and K6-046); full text read 34; abstract only 14 (K6-003, 006, 008, 015, 016, 019, 025,
  027, 028, 030, 032, 035, 043, 044); blocked with no abstract 1 (K6-004); [unverified] markers in this log: 23.
- Retrieval note: the session's WebSearch budget was already exhausted (200/200) at this worker's first call; DuckDuckGo,
  Mojeek and Startpage returned bot challenges; Brave worked for about 10 queries before a captcha; OpenAlex hit its daily
  limit; Semantic Scholar is rate-limited and elides publisher abstracts. Discovery therefore used the Crossref REST API
  (journal ISSN and SSRN-prefix filters), the DataCite API (AgEcon Search DOIs 10.22004), the arXiv API, IDEAS/RePEc
  abstract pages, Unpaywall (placeholder e-mail parameter), site listing pages crawled by curl (farmdoc daily, CFTC OCE,
  Databento) and Wayback CDX listings (cmegroup.com, quantpedia.com, blogs). Blocked hosts: Wiley (Cloudflare), OUP,
  ScienceDirect (captcha), AgEcon Search (AWS WAF; 403 to WebFetch), usda.gov / nass / fas / ams (Akamai), cmegroup.com,
  papers.ssrn.com, quantpedia.com (after a few requests). Where a blocked page had a Wayback capture, the capture was read
  by curl and is named in the item. No Firecrawl, no WebFetch text used as a verbatim source. Every query is in section 1.
- Panel sources met, already claimed by others (not re-read): K3-007 (Chinese macro news, [K6] passage P-K3-007-j);
  K3-040 (overnight-intraday reversal everywhere, tagged [K6], title only); K4-016 (pre-holiday effect in commodities);
  K4-034, K4-035, K4-036, K4-039 (commodity-index roll, K4's [K6] passages); K5-023 (Martell and Trevino 1990, intraday
  commodity futures, not retrieved by K5); K5-029 (Borgards et al. 2021 overreaction, [K6] passages for W, C, S, BO);
  K5-030 (Gu, Kurov, Stan 2023, unread by K5). K6 claimed no panel source of its own.

## 1. Containers

| # | container | queries run, listed | start | pre-filter done | full-text done | considered | passed | full-text read | notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Journal of Futures Markets (Crossref REST API filtered to ISSN 0270-7314; abstracts from Crossref, IDEAS or Wayback where deposited) | Crossref/JFM: "USDA report announcement agricultural futures"; "intraday grain futures corn soybeans wheat"; "livestock futures hogs cattle report" (x2, first timed out); "overnight trading electronic grain futures day session"; "price limits limit moves agricultural futures"; "soybean crush spread"; "USDA WASDE crop report intraday price volatility"; "cattle on feed hogs and pigs report futures"; "grain futures opening gap overnight news"; "wheat futures intraday return"; "corn futures high frequency liquidity"; "lean hog live cattle futures intraday volatility jumps"; "USDA report release time trading hours agricultural futures"; "soybean futures intraday price discovery trading session"; "agricultural futures electronic trading bid-ask spread"; "crop progress condition report futures"; "settlement price close agricultural futures manipulation"; "weather forecast grain futures prices"; "wheat corn spread futures trading"; "first notice day delivery grain futures roll"; "hog feeding margin corn soybean meal futures spread"; "cold storage report pork bellies futures announcement". Full-text location: Bing RSS x4 (useless), Brave x8 | 21:21 | 21:25 | 21:27 | 52 | 9 (K6-001..K6-007, Simon 1999, Martell-Trevino = K5-023) | 3 (K6-001, K6-002, K6-007) | K6-003, K6-004, K6-006, Simon 1999 blocked (Wiley Cloudflare; no Wayback copy); Martell-Trevino already claimed by K5 (K5-023), see note in section 5. Last two queries (hog feeding margin; cold storage) gave no new pass. |
| 2 | farmdoc daily (farmdocdaily.illinois.edu). The site search is rendered client-side, so category and author listing pages were crawled by curl and filtered on title | (1) category marketing-and-outlook/usda-reports (205 links); (2) category marketing-and-outlook/futures-and-options-markets (55 articles); (3) author Scott Irwin (402 articles); (4) author Joe Janzen (95 articles); (5) category livestock-outlook (about 190 links); (6) category ag-market-insights (77 links). Ledes fetched for 9 candidates | 21:28 | 21:31 | 21:33 | about 1000 titles screened; 9 ledes | 5 (K6-009..K6-013) | 5 | Most report articles are single-report recaps (rejected as one-off commentary). Queries 5 and 6 gave no new pass. The seed "Irwin on the 2013 move of releases into trading hours" is covered by K6-012 and by the academic papers under container 3. |
| 3 | AgEcon Search and applied ag-econ journals (AJAE, AEPP, JAAE, JARE, J. Commodity Markets, Food Policy). AgEcon Search blocks curl (AWS WAF) and WebFetch (403): discovery through the DataCite API (AgEcon DOIs 10.22004), full text through Wayback copies of AgEcon PDFs, VTechWorks, WUR edepot | Crossref/AJAE 0002-9092: "USDA report announcement intraday futures"; "intraday corn soybean futures market microstructure"; "livestock futures report reaction hogs cattle". Crossref/AEPP 2040-5790: same three. Crossref/JCM 2405-8513: same three. Crossref (no filter): "Adjemian Irwin USDA announcement effects real-time"; "Karali are USDA reports still news..."; "Lehecka value of USDA crop progress..."; "USDA report release during trading hours corn soybean futures price discovery". Crossref/JAAE 1074-0708: "intraday futures USDA report corn hogs cattle". DataCite/AgEcon: "intraday AND (USDA OR WASDE OR report) AND (corn OR soybean OR wheat)"; "(hog OR cattle OR livestock) AND futures AND (intraday OR report OR announcement)"; "(overnight OR trading hours OR electronic trading) AND grains AND futures"; nine title searches (Gone in Ten Minutes; Announcement Effects in Real; still news; most impact; release procedures; flash events; microstructure noise cattle; soybean complex; bid-ask corn); "flash AND ..."; "Adjemian AND Irwin ..."; "Lehecka"; "He AND Serra ..."; "(crush OR soybean oil OR soybean meal) AND futures AND ..."; "(price limit OR limit move OR limit-lock) AND futures"; "(overnight OR night session OR opening) AND ... AND (return OR gap OR price)"; "(weather OR forecast) AND (corn OR soybean) AND futures AND ..."; "export sales AND ..."; "(cattle on feed OR hogs and pigs OR cold storage) AND futures" | 21:33 | 21:47 | 21:53 | about 330 records | 24 (K6-014..K6-037) | 15 (K6-014, 017, 018, 020, 021, 022, 023, 024, 026, 029, 031, 033, 034, 036, 037) | Abstract only: K6-015, 016, 019, 025, 027, 028, 030, 032, 035. Semantic Scholar and ScienceDirect blocked or elided; Kauffman PDF truncated in Wayback. Last two queries (export sales; livestock reports) gave no new pass. |
| 4 | USDA's own pages (WAOB/OCE, NASS, FAS, AMS, ERS). Hosts return an Akamai error to curl; Wayback copies used | Page lookups (not keyword searches): (1) usda.gov WASDE page (direct, blocked; Wayback 2026 capture read); (2) NASS calendar index and reports_by_date (direct blocked; Wayback Aug 2026 read), then the linked 2026 PFEI schedule PDF; (3) FAS export sales pages x3 (esrd1.html not archived in 2026; programs page 2023 capture read); (4) AMS report PDFs ams_2453, ams_2511, ams_2452, ams_2498, ams_2675 (two archived). ERS: ERR-293 already read as K6-037 | 21:53 | 21:54 | 21:55 | 9 pages | 5 (K6-038..K6-042) | 5 | Release times now stated from official pages for all nine reports named in the brief. Last two lookups (ams_2452, ams_2498) gave nothing new. |
| - | PAUSE (usage limit, lead-side) | none | 21:58 | - | 01:10 | - | - | - | Session paused from 21:58 to 01:10 PDT (2026-09-23/24); not work time. Resumed 01:12. |
| 5 | Named author Alexander Kurov (WVU): scheduled announcements including agricultural futures | Crossref author listing "Alexander Kurov" (80 records screened); Crossref: "Kurov agricultural commodity futures announcement USDA"; "Kurov Wolfe corn soybean wheat futures informed trading"; "Kurov Stan Gu commodity futures announcement" | 21:55 (resumed 01:12) | 01:13 | 01:13 | 83 | 1 (K6-043, found by query 1; not a Kurov paper) | 0 | No Kurov paper is ag-specific. Panel sources already claimed and tagged [K6] by others: K3-007 (Baum, Kurov, Wolfe 2015, Chinese macro news; K3 log P-K3-007-j reports no significant corn, wheat, soybean reaction); K5-030 (Gu, Kurov, Stan 2023, FOMC and commodity markets; K5 could not read it, K6 coverage [unverified]). "A shot in the arm" (Kurov et al. 2023, COVID vaccine news, some agricultural commodities) rejected as one-off 2020 events. Queries 2 and 3 gave no new pass. |
| 6 | SSRN (Commodities, Derivatives eJournals) via Crossref prefix 10.2139, abstract pages and PDFs via Wayback | Crossref/SSRN: "USDA report intraday corn soybean wheat futures"; "lean hog live cattle futures intraday"; "agricultural futures overnight intraday return reversal"; "soybean crush spread intraday"; "grain futures price limit"; "agricultural commodity futures intraday momentum seasonality"; "WASDE surprise futures returns drift"; "hogs and pigs cattle on feed report futures reaction"; "grain futures trading hours settlement close" | 01:13 | 01:14 | 01:15 | 90 | 2 (K6-043, K6-044) | 0 | Both abstract only: SSRN Delivery.cfm captures in Wayback are interstitial HTML, not PDFs. Kosowski et al. "Overnight-Intraday Reversal Everywhere" is K3-040 (panel, tagged [K6], title only in K3's log). Last three queries gave no new pass. |
| 7 | arXiv q-fin.TR / q-fin.ST (export.arxiv.org API) | (1) abs:(corn OR soybean OR wheat OR "lean hog" OR "live cattle") AND abs:futures AND abs:(intraday OR "high-frequency" OR announcement); (2) abs:(agricultural OR grain OR livestock) AND futures AND (intraday OR "high frequency" OR USDA) (API returned mostly off-topic records); (3) cat:(q-fin.TR OR q-fin.ST OR q-fin.GN OR econ.GN) AND abs:(corn OR soybean OR wheat OR hog OR cattle OR grain) (40 records); (4) cat:(q-fin.TR OR q-fin.ST) AND abs:commodity AND abs:intraday | 01:15 | 01:16 | 01:16 | 120 | 0 new (1711.03506 = K6-031, see) | 0 | Everything else daily, spillover, Chinese, forecasting or off-topic. Queries 3 and 4 gave no new pass. |
| 8 | CFTC Office of the Chief Economist papers | (1) OCE research-papers listing, pages 0-8 (66 titles), keyword-filtered; (2) ledes of three listed PDFs (Convective Risk Flows; Liquidity in Select Futures Markets; Third Dimension of Financialization); (3) Crossref "CFTC Office of the Chief Economist agricultural futures intraday trading"; (4) Crossref "CFTC live cattle futures volatility high frequency trading 2016 staff"; (5) Crossref "CFTC flash events agricultural futures corn hogs" | 01:16 | 01:17 | 01:17 | 66 titles + 30 records | 1 (K6-045; K6-046 claimed then rejected on its abstract: crude oil only) | 2 (K6-045; K6-046 read to the abstract only, K4 region) | Onur-Reiffen (K6-007) and the pit-closure papers came up again (see K6-007, R-K6-031). Stop Orders = K4-043 (ES, ZN, CL). Queries 3-5 gave no new pass. |
| 9 | CME Group agriculture research and education (cmegroup.com refuses this IP; Wayback CDX listings and captures by curl) | (1) CDX cmegroup.com/education/ filtered on crush, soybean, grain, corn, wheat, livestock, cattle, hog, price-limit, usda, wasde (200 URLs); (2) CDX cmegroup.com/openmarkets/ same filter; (3) CDX cmegroup.com/articles/ same filter; (4) direct page lookup cmegroup.com/trading/price-limits.html | 01:17 | 01:18 | 01:19 | about 180 page titles | 5 (K6-047..K6-051) | 5 | Rejected by title: Black Sea, Australian, Canadian, Brazilian and FX-hedging pages; options pages; KC-vs-Chicago and pork-cutout spreads (legs outside the program's products); oilshare product pages; seasonal and outlook commentary. K8 flags in section 4. Query 3's two passes (USDA reports; limit FAQ) came late; the direct lookup (4) added nothing new beyond K6-047, which it is. |
| 10 | Databento blog | (1) blog index page; (2) sitemap.xml (no blog URLs listed); (3) category "learning" pages 1-4; (4) categories "engineering" and "announcements" pages 1-4 (115 post links in all), title filter on ag, CBOT, commodity, settlement, spread, session terms | 01:19 | 01:20 | 01:20 | 115 | 0 | 0 | Only "What are futures spreads?" (generic) and a connection-limits notice matched. No ag content. |
| 11 | Quantpedia (grains and livestock) | (1-7) site search ?s= corn, soybean, wheat, lean hog, cattle, agricultural, grain (results are rendered client-side: the returned HTML holds only the sidebar); (8) sitemap and robots probes (quantpedia.com then returned "Access Forbidden"); (9) Wayback CDX of quantpedia.com URLs containing ag terms; (10) Wayback CDX of quantpedia.com/strategies/ (85 URLs) filtered on commodity terms | 01:20 | 01:21 | 01:21 | about 95 | 0 | 0 | Found: "Sunspots as a natural signal for trading wheat futures" (multi-year cycle) and cross-sectional monthly commodity factors (momentum, term structure, skewness, return asymmetry). K4-016 (pre-holiday effect in commodities, tagged [K6]) is K4's. |
| 12 | Practitioner blogs, discovery only (Kinlay, Quantitative Brokers, Carver, Robot Wealth, Quantocracy) | Wayback CDX with ag-term URL filters on jonathankinlay.com, quantitativebrokers.com, qoppac.blogspot.com, robotwealth.com, quantocracy.com (5 queries, no hits); CDX of quantitativebrokers.com/blog/ (21 posts, title filter); Quantocracy ?s=corn and ?s=soybean | 01:21 | 01:22 | 01:22 | about 80 | 0 | 0 | One hit: Golden Compass 2017 "Statistical Arbitrage on a Cross-border Soybean Crush Spread" (Dalian legs, rejected). |

## 2. Rejected items

| id | source | item | reason |
|---|---|---|---|
| R-K6-001 | JFM 2025 (Hu, Mallory) | Overseas Impact of USDA Reports: Evidence From Chinese Soybean Complex Futures | Dalian products reacting at their own open; not a CME product and the mechanism (report released while the Chinese market is shut) does not transfer |
| R-K6-002 | JFM 2021 (Cao, Robe) | Market uncertainty and sentiment around USDA announcements | option implied volatility over several days; no intraday futures mechanism |
| R-K6-003 | JFM 2025 (Yang, McKenzie) | Do Corn Options Update Volatility Expectations in the Wake of USDA Reports? | option implied volatility, daily |
| R-K6-004 | JFM 2015 (Mattos, Silveira) | Futures Price Response to Crop Reports in Grain Markets | daily TARCH volatility dummies 2004-2014; no intraday horizon (the same group's 2025 intraday paper passed as K6-006) |
| R-K6-005 | JFM 1993 (Fortenbery, Sumner); 1987 (Milonas); 1994 (McNew, Espinosa) | USDA report effects on futures (three items) | daily close-to-close report-day effects, pre-electronic era |
| R-K6-006 | JFM 2022 (Rosa) | Understanding intraday momentum strategies | generic overnight-predicts-last-half-hour (D.1 families A/C); abstract names no K6 product |
| R-K6-007 | JFM 2024 (Martins) | Short-term market impact of Black Sea Grain Initiative on four grain markets | one-off geopolitical event study |
| R-K6-008 | JFM 2024 (Xia, Xiong, Li) | Can night trading reduce price volatility? China corn and corn starch | Dalian products |
| R-K6-009 | JFM 2016 (Liu, Sono) | China's soybean crush spread | Dalian products |
| R-K6-010 | JFM 2016 (Frino, Lepone, Mollica, Zhang) | Are Hedgers Informed? large trades in illiquid agricultural futures | illiquid non-US grain market; microstructure not comparable to CBOT |
| R-K6-011 | JFM 1991 (Stevens) | Weather persistence effect on corn, wheat, soybean growing season price dynamics | daily/seasonal horizon |
| R-K6-012 | JFM 2010 (Aulerich, Fishe, Harris) | Why do expiring futures and cash prices diverge for grain markets? | delivery-period convergence; needs positions into delivery |
| R-K6-013 | JFM 2010 (Karali, Dorfman, Thurman) | Delivery horizon and grain market volatility | Samuelson-effect volatility by maturity; no intraday mechanism |
| R-K6-014 | JFM 2005 (Liu) | Price relations among hog, corn, and soybean meal futures | cointegration at daily or longer horizon (title) |
| R-K6-015 | JFM 1998, 1997 (Mann, Dowen) | pork belly cold storage reports; proprietary-public information on pork futures | pork bellies (delisted); no abstract, no intraday horizon in title |
| R-K6-016 | JFM 1992 (Liu, Thompson, Newbold) | Impact of the price adjustment process and trading noise on return patterns of grain futures | no abstract anywhere (IDEAS: none); title gives no intraday horizon |
| R-K6-017 | JFM 2021 (Li, Hayes); 1991 (Johnson, Zulauf, Irwin, Gerlow) | soybean reverse crush risk premium; soybean complex spread efficiency | monthly or multi-month holding (Johnson et al. described in K6-001 as 1.5 to 9.5 month holds) |
| R-K6-018 | JFM misc. (Brorsen/Yang 1995 pork bellies limits; Hall-Kofman 2001; Chen 1998; Holder et al. 2002; Ma-Rao-Sears 1989 T-bond; Adrangi-Chatrath 1999 margins; Rothig-Chiarella 2007) | price-limit theory, margins, speculation | theory, T-bond or daily speculation studies; K6-002 and K6-003 carry the limit mechanism |
| R-K6-019 | JFM 2026 (Han, Hsieh, Zhang) | Commodity Futures Report Text Sentiment and Returns | sentiment, shelved |
| R-K6-020 | farmdoc daily 2015/08 (Good, Irwin) | Reaction to USDA Corn and Soybean Production, Consumption, and Price Projections | lede read: a recap of one August report, no systematic reaction study |
| R-K6-021 | farmdoc daily 2022/07 (Janzen) | WASDE Recap: What Happens When USDA Updates Yield Expectations? | lede read: recap of one July report |
| R-K6-022 | farmdoc daily 2013/10 | When Exchanges Change the Rules of the Game | lede read: one-off lean hog final settlement change during the 2013 shutdown |
| R-K6-023 | farmdoc daily (about 60 titles: WASDE recaps, "USDA Reports Provide Surprises", Hogs and Pigs and Cattle report recaps 2014-2026) | single-report recaps | one-off commentary, no systematic reaction measure |
| R-K6-024 | farmdoc daily 2011-2024 (Irwin, Sanders, Good series on corn stocks surprises and sampling errors; yield forecast errors; acreage revisions) | USDA estimate accuracy | forecast-error statistics, not market reaction |
| R-K6-025 | farmdoc daily 2015/12-2016/01 | Who's Spoofing Whom? (three posts) | order-book manipulation; the program has no order-book data or limit-order strategy |
| R-K6-026 | farmdoc daily 2015/03, 2015/05 | How Will Closing the Trading Pits Affect Market Performance?; Flash Crash, or Flash in the Pan? | historical structural change; one-off event |
| R-K6-027 | farmdoc daily 2021/06, 2023/12 (Janzen) | Weather Risk Premium in New-Crop Corn / Soybean / Coffee Futures Prices | seasonal drift over months |
| R-K6-028 | AJAE 2019 (Ying, Chen, Dorfman) | Flexible Tests for USDA Report Announcement Effects in Futures Markets | daily volatility and returns (abstract) |
| R-K6-029 | AJAE 1989-1993 (Sumner-Mueller; Colling-Irwin 1990 Hogs and Pigs; Grunewald et al. 1993 Cattle on Feed); AEPP 1990 (Schroeder et al.), 1996 (Colling et al. Export Inspections); AgEcon 1991 (Colling, Irwin, Zulauf) | report reaction studies | daily, pre-electronic |
| R-K6-030 | AJAE 2008 (McKenzie); AEPP 2017 (Isengildina-Massa, Karali, Irwin; Xiao et al.) | forecast smoothing and ending-stocks forecasts | forecast evaluation, daily |
| R-K6-031 | AJAE 2023, JCM 2018 (Gousgounis, Onur) | livestock pit closure; effect of pit closure on futures trading | historical pit-to-screen transition |
| R-K6-032 | JCM 2026 (Couleau, Trujillo-Barrera, Etienne) | Intraday market momentum in coffee futures | coffee is not a K6 product; generic D.1 family C |
| R-K6-033 | JCM 2022 (McKenzie, Ke) | How do USDA announcements affect international commodity prices? | non-US prices |
| R-K6-034 | JCM 2026 (Yang, Karali); SSRN 2024 (Yang, Karali) | Information shocks and coexceedances in agricultural futures; USDA reports and extreme price comovements | no abstract retrievable; title indicates daily joint-tail comovement |
| R-K6-035 | JCM 2019, 2020, 2025 (Schroeder et al. thin cash cattle; Adhikari-Putnam comovement; Santos-Almeida Brazil cattle); JCM 2020 (Elliott et al. new generation grain contracts) | livestock cash markets, sector comovement, Brazil | daily, non-CME, or contract design |
| R-K6-036 | AgEcon 2013, 2015 (Dorfman, Karali) | A Nonparametric Search for Information Effects from USDA Reports | daily returns (abstract) |
| R-K6-037 | AgEcon 2010 (Karali, Park) | Do USDA Announcements Affect the Correlations Across Commodity Futures Returns? | daily bivariate GARCH |
| R-K6-038 | AgEcon 2007 (Frank, Garcia, Irwin) | To What Surprises Do Hog Futures Markets Respond? | daily reaction; Hogs and Pigs released after the close |
| R-K6-039 | AgEcon 2016 (Joseph, Garcia, Peterson) | Does the Boxed Beef Price Inform the Live Cattle Futures Price? | daily settlement lead-lag; futures lead |
| R-K6-040 | AgEcon 2019 (Janzen, Legrand) | Wheat Futures Trading Volume Forecasting and the Value of Extended Trading Hours | volume forecasting, no return mechanism |
| R-K6-041 | AgEcon 2017 (Arzandeh, Frank) | Price Discovery in Agricultural Futures Markets: Should We Look Beyond the Best Bid-Ask Spread? | order-book depth; no order-book data in the program |
| R-K6-042 | AgEcon 2021 (Peng, Hu, Robe) x2 | Maximum order size in corn calendar spreads; COVID-19 and soybean futures liquidity | calendar-spread order limits; one-off period |
| R-K6-043 | AgEcon 2010-2011 (Shah, Brorsen); 2000 (Leuthold, Kim) | KCBT wheat electronic transition; overnight corn e-hedging vs Tokyo | historical transitions |
| R-K6-044 | AgEcon 2015 (Mathews, Brorsen, Hahn) and older livestock items | Mandatory price reporting and livestock price discovery | cash-market reporting, daily |
| R-K6-045 | AgEcon 2022 (Hu, Mallory) | Overseas Impact of USDA Reports (NCCC version of R-K6-001) | same source as R-K6-001 |
| R-K6-046 | AgEcon 2019 (Karali, Isengildina-Massa, Irwin) | The Changing Role of USDA Inventory Reports in Livestock Markets | daily (abstract: Cattle on Feed and Hogs and Pigs volatility impact "largely disappeared after 2000") |
| R-K6-047 | AgEcon 1989-1994 (Colling, Irwin; Carter, Galopin; Aradhyula, Kesavan) | Hogs and Pigs and Cold Storage report reactions | daily, pre-electronic |
| R-K6-048 | AgEcon 2016 (Abbott et al.) | Valuing Public Information: WASDE Corn Reports | welfare simulation, no price mechanism |
| R-K6-049 | AgEcon 2019 (Piette) | Can Satellite Data Forecast Valuable Information from USDA Reports? | needs satellite data the program does not have; forecast study |
| R-K6-050 | AgEcon 1995 (Murphy, Purcell); 2004 (Egelkraut, Garcia); 1999 (Cole et al.) | trader activity in LC limit moves; options forecasts with limit moves; seasonal processing calendar spreads | pit era; options; multi-week holds |
| R-K6-051 | AgEcon 2026 (Xu); 2015 (Wang, Houston) | China algorithmic trading; China GM soybean comovement | Dalian products |
| R-K6-052 | AgEcon 2024 (Wu, Huang, Serra) | The Economic Value of Intraday Data in Hedging Commodity Spot Prices | hedging, not a trading mechanism |
| R-K6-053 | Financial Review 2023 (Kurov et al.) | A shot in the arm: COVID-19 vaccine news and financial and commodity markets | one-off 2020 events, daily |
| R-K6-054 | SSRN 2005/2006 (Good, Irwin) | Understanding USDA Corn and Soybean Production Forecasts: Methods, Performance and Market Impacts | forecast methods and daily impacts |
| R-K6-055 | SSRN 2009 (Irwin, Garcia, Good, Kunda); 2009 (Isengildina-Massa et al.) | Poor convergence of CBOT contracts; WASDE price-forecast intervals | delivery-period convergence; forecast intervals |
| R-K6-056 | SSRN 2015, 2013, 2024 (Bego; Santos, Almeida) | Brazilian soybean, corn and live cattle futures | non-CME |
| R-K6-057 | SSRN 2025 (Xia, Xiong, Li); 2020, 2024, 2017 (Chinese intraday momentum and reversal papers); 2022 (Ma et al. Chinese metals night trading) | Chinese commodity futures intraday | Dalian/Zhengzhou/Shanghai products |
| R-K6-058 | SSRN 2016 (Marowka et al.) | Bayesian dynamic cointegration, soybean crush | econometric method, no abstract, daily data (title) |
| R-K6-059 | SSRN 2023 (Li, Liu, Miao, Tse); 2000 (Sorensen); 2016 (Hevia et al.); 2005 (Miffre, Rallis); 2024 (Qian et al.) | commodity return seasonality, risk premia, momentum | monthly cross-sectional factors |
| R-K6-060 | SSRN 2023 (Wang, Diersen) | Weekly Options on Grain Futures | options |
| R-K6-061 | SSRN 2019 (Bosch) | Information content of WASDE vs COT reports | daily GARCH 1996-2014 |
| R-K6-062 | SSRN 2023 (Anderson et al.) | Futures Volatility and Cash Price Discovery for Feeder Cattle | feeder cattle (not K6), cash discovery |
| R-K6-063 | arXiv 2017 ("The Wandering of Corn"), 2021-2025 (Sino-US spillovers; Brazil grain spillovers; Covid Chinese futures; multifractality of grain indices; renewable diesel and soybean basis) | agricultural price dynamics | daily, spillover, cash basis or Chinese markets |
| R-K6-064 | CFTC OCE 2016 (Robe, Raman, Yadav) | The Third Dimension of Financialization: Electronification, Intraday Institutional Trading, and Commodity Market Quality | read to the abstract after fetching: WTI crude only (K4 region). Registry line K6-046 was appended before the abstract was seen; flagged in section 5 |
| R-K6-065 | CFTC OCE (Convective Risk Flows; Liquidity in Select Futures Markets; Automated Trading in Futures Markets and update; Who Participates in Agricultural Futures Markets; Effect of Matching Algorithm Changes; Retail Traders) | CFTC staff papers | VIX-to-positions daily (K8-type, not a price rule); ES/ZN/CL liquidity; descriptive participation statistics; matching rules; retail rejected by K1/K4 |
| R-K6-066 | JFM 1995 (Kastens, Schroeder) | A trading simulation test for weak-form efficiency in live cattle futures | daily technical rules (title) |
| R-K6-067 | CME education/articles (about 170 titles) | Black Sea, Australian, Canadian and Brazilian wheat/soy products; FX hedging of grain trades; options strategy pages; KC-Chicago wheat spread; pork cutout vs lean hog; soybean oilshare product pages; seasonal and outlook commentary; roll liquidity in corn spreads; CME wheat leads global price discovery | non-program products or legs, options, commentary, or no intraday mechanism |
| R-K6-068 | Databento blog | "What are futures spreads?" and 114 other posts | generic or no ag content |
| R-K6-069 | Quantpedia | Sunspots as a natural signal for trading wheat futures; momentum, term-structure, skewness and return-asymmetry effects in commodities | multi-year or monthly cross-sectional |
| R-K6-070 | Golden Compass (via Quantocracy) 2017 | Statistical Arbitrage on a Cross-border Soybean Crush Spread | Dalian legs, not program products |

## 3. Passed items

### K6-001 (container 1)
- Citation: Rechner, D. and Poitras, G. (1993). "Putting on the Crush: Day Trading the Soybean Complex Spread." Journal of Futures Markets 13(1), 61-75. DOI 10.1002/fut.3990130107.
- Retrieval: full text, author-hosted PDF https://www.sfu.ca/~poitras/soy.pdf (16 pages, text layer read with pdftotext).
- Mechanism: the gross processing margin (GPM = meal and oil value minus beans) tends to reverse at the open: if the GPM at the open is below (above) the previous close, put on a reverse (normal) crush at the open and lift it at the same day's close, with a filter on the size of the opening gap.
- Products and horizon: ZS, ZM, ZL as a 10-12-9 contract crush; open-to-close, one day.
- Cost assumptions: 1.5 cents per bushel round trip for the whole spread (one tick in and out per leg plus floor-level commissions); floor-trader execution.
- Data window: daily open and close, February 1, 1978 to July 31, 1991 (CSI data), March/August/December GPM series.
- Quality tells: pit era, opening and closing prints (the authors concede "small unrepresentative trades occurring at the open"); filter sizes 0-3 cents with no out-of-sample split; profits vary strongly by year; OCR shows a table labelled "Table IV" that the text calls Table II.
- Verbatim passages:
  - P-K6-001-a (p. 63, Trading Rule Specification): "If the GPM on the open is less (greater) than the previous day's close, a reverse crush (normal crush) spread is placed. In all cases, the position is liquidated on the close of the same day."
  - P-K6-001-b (p. 63): "roundtrip transaction costs per trade are estimated to be 1.5 cents per bushel. This value is composed of both execution costs and commissions."
  - P-K6-001-c (p. 64): "from February 1, 1978 to July 31, 1991." (the introduction, p. 61, says "over the period February 1, 1978 to July 30, 1991")
  - P-K6-001-d (Table IA, GPM, 1978-1987): "(Close, - Open,) and (Open, - Close,-]) -0.49 (-23.7)"; Table IB (1987-1991): "(Close, - Open,) and (Open, - Close,-i -0.43 (-14.2)".
  - P-K6-001-e (p. 67): "the GPM at the opening tends to be lower than the previous close and then \"trade up\" during the day."
  - P-K6-001-f (aggregate table, net of costs, filters 0 / 1 / 2 / 3 cents): "Mean profit per trade -0.36 0.35 1.02 1.74" ... "Number of trades 3352 1861 922 457" ... "Percentage trades profitable 39.6 52.3 62.3 69.0"; t-values "-7.69 5.08 9.10 9.30".
  - P-K6-001-g (p. 64): "It is argued that the results of this study refiect the potential profitability of fioor trading in the soybean pits." (OCR spelling as extracted)
- Numeric claims: overnight-intraday GPM correlation -0.49 and -0.43 (P-K6-001-d); net mean profit 0.35 to 1.74 cents per bushel for 1-3 cent filters, 1861 to 457 trades (P-K6-001-f); cost 1.5 cents per bushel (P-K6-001-b).
- Tags: new to the program (inside-K6 spread; the opening-reversal element is a spread version of D.1 family C). Intraday-feasible: yes (entry at the day open, exit at the close), subject to the day open now being 08:30 CT after the overnight session rather than a pit open, and to a 31-contract ratio that must be scaled down.
- Clusters tagged: K6.

### K6-002 (container 1)
- Citation: Janardanan, R., Qiao, X. and Rouwenhorst, K.G. (2019). "On commodity price limits." Journal of Futures Markets 39(8). DOI 10.1002/fut.21999; working paper SSRN 3076090 (one source).
- Retrieval: full text of the February 2017 working-paper version, https://www.ou.edu/content/dam/price/Finance/energyfinanceconference/papers/Janardanan-et-al-Limits%20Paper.pdf (41 pages). The published JFM version was not read.
- Mechanism: a close at the daily limit is followed by next-day continuation in the limit direction (delayed price discovery); a large move of 90-100% of the limit without a lock is not followed by continuation. The limit-day options-implied futures price predicts the next open.
- Products and horizon: soybean oil, corn, soybeans, soybean meal, SRW wheat, live cattle, lean hogs (plus cotton and feeder cattle, not K6 products); next day close-to-close and close-to-open.
- Cost assumptions: none stated.
- Data window: daily open and close from Bloomberg, 01/07/1991 to 05/23/2016.
- Quality tells: continuation is measured close-to-close; the open-to-close part of the next day is not reported, and the options result says most of the adjustment happens at the open. Authors are at a commodity investment manager (SummerHaven). Limit sizes have changed since (CME now resets ag limits semi-annually), so historical limit-day frequency does not carry over directly.
- Verbatim passages:
  - P-K6-002-a (Abstract): "Consistent with delayed price discovery, returns continue in the same direction after limit days and do not reverse after one week, whereas returns are small after large price moves that do not hit limits."
  - P-K6-002-b (Introduction, p. 1): "For limit up days, the average return on the following day is 40 to 62 basis points, and for limit down days, the average return on the following day is -38 to -63 basis points."
  - P-K6-002-c (p. 11): "On the day after a limit up day, on average across the nine commodities the next day return is 63 basis points if we include all limit days and 39 basis points if we only include non-consecutive limit days."
  - P-K6-002-d (p. 2): "a 1% increase in the return calculated from limit day close to options-implied prices is associated with a 0.76% increase in the close-to-open futures returns, and 0.15% increase in the close-to-close futures returns."
  - P-K6-002-e (Section 2.3): "We consider nine commodities with price limits on the futures contracts: soybean oil (BO), corn (C), cotton (CT), feeder cattle (FC), live cattle (LC), lean hogs (LH), soybean (S), soybean meal (SM), and soft red winter wheat (W)." and "Our sample is from 01/07/1991 to 05/23/2016."
  - P-K6-002-f (Section 2.4): "There are a total of 2063 limit ups and 2393 limit downs in our sample."
- Numeric claims: next-day +40 to +62 bp after limit up, -38 to -63 bp after limit down (P-K6-002-b, c); 0.76 and 0.15 forecasting coefficients (P-K6-002-d); 2063 limit ups and 2393 limit downs (P-K6-002-f). Open-to-close continuation on the next day: not reported [unverified].
- Tags: new to the program (limit-lock continuation; read prior-day limit state, trade next day). Intraday-feasible: only the next day's open-to-close part, which the source does not measure; the close-to-open part is not capturable without holding overnight. Topstep's "within 2% of a product's price lock limit" prohibition applies on the limit day itself.
- Clusters tagged: K6.

### K6-003 (container 1) ABSTRACT ONLY
- Citation: Park, C.W. (2000). "Examining futures price changes and volatility on the trading day after a limit-lock day." Journal of Futures Markets 20(5), 445-466.
- Retrieval: abstract only, from IDEAS https://ideas.repec.org/a/wly/jfutmk/v20y2000i5p445-466.html. Failed routes: Wiley (Cloudflare challenge to curl), ProQuest openview (preview page without text), Wayback (not archived).
- Mechanism (from abstract): prices continue to rise on the day after an up-limit day.
- P-K6-003-a (abstract): "The results show evidence that prices continue to rise on average the day after an up‐limit day. In addition, limits appear to influence price volatility for some but not all of the futures contracts."
- Products, window, costs, magnitudes: [unverified] (the abstract names no contracts).
- Tags: new to the program (same mechanism as K6-002). Intraday-feasible: unknown, the horizon is the next trading day.
- Clusters tagged: K6.

### K6-004 (container 1) BLOCKED, TITLE ONLY
- Citation: Brorsen, B.W. (1989). "Liquidity costs and scalping returns in the corn futures market." Journal of Futures Markets 9(3), 225-236.
- Retrieval: failed. IDEAS: "No abstract is available for this item."; Semantic Scholar: abstract elided by publisher; Wiley: Cloudflare; Wayback copy of the Wiley page (2024-06-02) has no abstract; Unpaywall: no OA copy.
- Passed on title only (corn execution costs at intraday horizon, relevant to cost assumptions). All content [unverified].
- Clusters tagged: K6.

### K6-006 (container 1) ABSTRACT ONLY
- Citation: Silveira, R.L.F., Silva, ?, Mattos, F.L. and Junior, ? (2025). "The Reaction of Corn Futures Markets to US and Brazilian Crop Reports." Journal of Futures Markets. DOI 10.1002/fut.22601 (author initials beyond Crossref surnames [unverified]).
- Retrieval: abstract only, from the Crossref record of DOI 10.1002/fut.22601. Unpaywall lists an open copy at https://onlinelibrary.wiley.com/doi/pdfdirect/10.1002/fut.22601, but curl gets a Cloudflare page and WebFetch got HTTP 403; Wayback has no copy of the pdfdirect, full or epdf URLs.
- P-K6-006-a (abstract): "Employing an intraday announcement analysis, we investigate how return volatilities and trading volumes respond to the release of these reports. Specifically, we compare prices and volume behavior on report days with the 5 days preceding and following the announcements."
- P-K6-006-b (abstract): "our results indicate that WASDE report announcements significantly influence returns and trading volumes in both markets."
- Mechanism: WASDE release raises intraday return volatility and volume in CBOT corn; direction or drift not stated. Window, costs, magnitudes: [unverified].
- Tags: port of D.1 family E (scheduled event) to ZC. Intraday-feasible: yes if WASDE is released inside the session (release time is logged under container 4 from USDA's own page).
- Clusters tagged: K6.

### K6-007 (container 1)
- Citation: Onur, E. and Reiffen, D. (2018). "The effect of settlement rules on the incentive to Bang the Close." Journal of Futures Markets 38(12). DOI 10.1002/fut.21915.
- Retrieval: full text, CFTC manuscript dated January 2018, https://www.cftc.gov/sites/default/files/2019-05/onur_reiffen_Manuscript_ada.pdf.
- Mechanism: before June 25, 2012 CBOT corn settlement used only floor trades in the final minute; traders with positions had an incentive to push the settlement print, and the move into settlement was reversed at the next open more often than chance. After the rule change (all venues count) the reversal rate fell to about half.
- Products and horizon: ZC (soybeans in an appendix); settlement minute to next open.
- Cost assumptions: none (not a trading study).
- Data window: CFTC trade-capture (TCR) data; sample starts March 1, 2012 (May 2012 lead contract) and spans the June 25, 2012 change.
- Quality tells: regulator's proprietary data; a short event window around one rule change; the reversal statistic spans the overnight gap.
- Verbatim passages:
  - P-K6-007-a (Introduction, p. 3): "prior to June 25, 2012, settlement prices were based only on trades made on the CBT exchange floor during the final minute of trading. After that date, all trades made during the final minute of trading were included in settlement price determination -- whether those trades were made on the trading floor or on the CBT's electronic platform."
  - P-K6-007-b (p. 3): "on average, about 12% of the entire daily floor trading volume in corn occurred during that one minute (the trading day was 3.75 hours long). In contrast, the volume of electronic trading during that same minute averaged about 4.5% of the total daily electronic trading volume."
  - P-K6-007-c (Section b, Reversals): "We find that the percentage of reversals falls from 57.3% under the old regime to 48.7% under the new, a decline which is statistically significant at the 1% level."
  - P-K6-007-d (footnote 11): "Prior to June 25, 2012, the settlement period minute was from 1:14 p.m. – 1:15 p.m. and after the change it became 1:59 p.m. – 2:00 p.m.." (time zone not stated in the passage)
  - P-K6-007-e (footnote 21): "For our sample, the lead month was the May, 2012 contract between March 1 and April 16".
- Numeric claims: 12% and 4.5% of daily volume in the settlement minute (P-K6-007-b); reversal rate 57.3% to 48.7% (P-K6-007-c).
- Tags: new to the program (settlement window). Intraday-feasible: a settlement-minute reversal needs a position held to the next open, so not as measured; the program's flatten (grains 13:18 CT) precedes or overlaps the settlement minute. The source is mainly evidence that the current settlement rule removed the old effect.
- Clusters tagged: K6.

### K6-008 (container 1) ABSTRACT ONLY
- Citation: Simon, D.P. (1999). "The soybean crush spread: Empirical evidence and trading strategies." Journal of Futures Markets 19(3), 271-289.
- Retrieval: abstract only, from IDEAS https://ideas.repec.org/a/wly/jfutmk/v19y1999i3p271-289.html. Failed routes: Wiley (Cloudflare), Unpaywall (is_oa false, no location).
- P-K6-008-a (abstract): "A tendency also exists for the crush spread to revert toward its most recent 5‐day average. Simulations demonstrate that trading rules based on these results would have been profitable."
- P-K6-008-b (abstract): "deviations of the soybean crush spread from its long‐run equilibrium were transitory during the sample period from January 1985 through February 1995."
- Holding period, costs, magnitudes: [unverified].
- Tags: new to the program (inside-K6 spread reversion). Intraday-feasible: unknown; a 5-day-average anchor can be read before the open, but whether the reversion shows up within one session is not in the abstract.
- Clusters tagged: K6.

### K6-009 (container 2)
- Citation: Peterson, P.E. (2012). "Trading Hours and Daily Settlement Prices." farmdoc daily (2):122, June 27, 2012.
- Retrieval: full text, https://farmdocdaily.illinois.edu/2012/06/trading-hours-and-daily-settle.html (the summary table is an image and was not read).
- Mechanism: none tested; institutional description of how CBOT grain settlement prices were built before and after June 25, 2012 (pit-only versus all-venue volume-weighted closing-period prices), and how livestock settlement uses better bids and offers.
- Products and horizon: ZW, ZC, ZS, livestock; settlement window.
- Cost assumptions, data window: none; pit volume shares for January-May 2012.
- Quality tells: descriptive extension article; 2012 rules, since changed again (pits closed 2015).
- Verbatim passages:
  - P-K6-009-a: "Prior to June 25, CBOT Wheat futures used a weighted average of Globex (but not pit) prices for the lead month, Globex (but not pit) spreads for the next 4 months, and pit (but not Globex) spreads for everything else. In contrast, CBOT Corn and Soybean futures used pit (but not Globex) prices for the lead month and pit (but not Globex) spreads for all other months."
  - P-K6-009-b: "For the period January-May 2012, pit trading accounted for just 2.07% of total CBOT Wheat futures volume, 6.48% of total CBOT Corn futures volume and 5.98% of total CBOT Soybean futures volume"
  - P-K6-009-c: "storable commodities such as grains and oilseeds commonly rely on spreads to settle months within the same crop year, while non-storable commodities like livestock and dairy establish \"flat\" prices for each contract month. ... Livestock futures take into consideration \"better bid\" (unmet offers to buy at a price above the last trade) and \"better ask\" (unmet offers to sell at a price below the last trade) prices when determining the closing range"
- Numeric claims: pit shares 2.07%, 6.48%, 5.98% (P-K6-009-b).
- Tags: new to the program (settlement-window facts; context for K6-007). Intraday-feasible: not a mechanism.
- Clusters tagged: K6.

### K6-010 (container 2)
- Citation: Irwin, S. and Good, D. (2016). "Does the Market Read Too Much into the USDA's March 1 and June 1 Corn Stocks Estimates?" farmdoc daily (6):114, June 16, 2016.
- Retrieval: full text, https://farmdocdaily.illinois.edu/2016/06/market-read-much-usda-estimates.html (figures are images, not read).
- Mechanism: the Grain Stocks surprise (USDA estimate minus average trade guess) implies a feed-and-residual surprise, but later USDA revisions to feed use are only about half to 60% of the surprise, so the authors suggest the market "may have read too much" into stocks surprises. No price data are analysed; the overreaction claim is inferred, not measured.
- Products and horizon: ZC; report day versus later WASDE months (not intraday).
- Cost assumptions: none. Data window: March 1 and June 1 stocks reports, 1991-2015.
- Quality tells: extension article; the price-overreaction statement is a conjecture ("may have").
- Verbatim passages:
  - P-K6-010-a: "Here, we examine USDA March 1 and June 1 stocks estimates over 1991-2015. For each report, we calculate the difference between the stocks estimates and the average trade guess."
  - P-K6-010-b: "The March 1 surprise was generally in the range of +/- 100 million bushels from 1991-2007, but has since been in a much wider range of roughly -200 million to +400 million bushels."
  - P-K6-010-c: "For June, the change has tended to be about 60 percent of the magnitude of the surprise and the fit between the magnitude of the surprise and the magnitude of the change in the feed and residual projection is relatively good (R2 of 0.72)."
  - P-K6-010-d: "the corn market may have read too much into those surprises at times in the past as adjustments to USDA feed and residual use projections have tended to be smaller than the surprises in the stocks estimates"
  - P-K6-010-e: "A number of market participants are surveyed by newswire services, such as Thompson/Reuters and Bloomberg, to ascertain the market's expectation, or \"trade guess\" for the soon-to-be released USDA stock estimates."
- Numeric claims: surprise ranges (P-K6-010-b); 60% and R2 0.72 for June (P-K6-010-c); the March passage "opposite direction of the surprise by about half the magnitude" and "R2 of only 0.52" are in the same section.
- Tags: port of D.1 family E (Grain Stocks release; possible post-release reversal, untested). Intraday-feasible: the reversal hypothesis is multi-day as written; any intraday version is [unverified]. Needs trade-guess data (Reuters/Bloomberg surveys), which the program does not hold.
- Clusters tagged: K6.

### K6-011 (container 2)
- Citation: Adjemian, M., Arita, S., Breneman, V., Hungerford, A. and Johansson, R. (2019). "Market Reaction to USDA's August Corn Crop Reports." farmdoc daily (9):186, October 4, 2019.
- Retrieval: full text, https://farmdocdaily.illinois.edu/2019/10/market-reaction-to-usda-august-corn-crop-reports.html (figures are images, not read).
- Mechanism: the August Crop Production / WASDE production surprise (USDA minus trade guess) moves December corn in the opposite direction, about 1.1% per 1% surprise on the report day; on average prices then stay near the initial response for two weeks (no reversal); report day brings a high-low range spike.
- Products and horizon: ZC December contract; report day, next open, and 10 trading days.
- Cost assumptions: none. Data window: August reports, 2009-2019 (figures), surprise history "at least two decades".
- Quality tells: authors from USDA's Office of the Chief Economist defending the 2019 report; figure-based, no test statistics given in the text.
- Verbatim passages:
  - P-K6-011-a: "On average, a 1% larger-than-expected USDA production surprise is followed by a reduction in futures price of about 1.1%."
  - P-K6-011-b: "Because the corn market locked limit down that day, and the next day was followed by a lower price, the market reaction in the chart may be understated. However, when the analysis in Figure 3 is performed using the day-after-USDA-report opening prices, we find very similar results."
  - P-K6-011-c: "We measure that volatility as the percentage difference between the highest and lowest prices that corn traded on a given trading day. As shown in the chart, the USDA August reports' release day is normally associated with a volatility spike."
  - P-K6-011-d: "The blue and yellow series in Figure 6 indicate that, on average, corn market prices respond to USDA news and those prices tend to remain at about the level of the initial response over the next two trading weeks."
  - P-K6-011-e: "Chicago Mercantile Exchange (CME) December delivery corn prices fell by 25 cents/bushel, or 6%, and the market locked limit down"
- Numeric claims: 1.1% per 1% surprise (P-K6-011-a); 25 cents limit down on August 12, 2019 (P-K6-011-e).
- Tags: port of D.1 family E (report day). Intraday-feasible: the surprise itself needs trade-guess data; the report-day range spike is a volatility-state fact (family D). Report-day limit locks bear on Topstep's 2% price-lock rule.
- Clusters tagged: K6.

### K6-012 (container 2)
- Citation: Irwin, S. (2020). "A Simple Proposal to Re-Level the Playing Field after the Release of USDA Crop Reports." farmdoc daily (10):12, January 23, 2020.
- Retrieval: full text, https://farmdocdaily.illinois.edu/2020/01/a-simple-proposal-to-re-level-the-playing-field-after-the-release-of-usda-crop-reports.html.
- Mechanism: since 2012-2013 major USDA crop reports are released into live trading at 11:00 CT; access to the PDF is uneven (server congestion, a two-second media-network advantage until July 2018), so the first seconds to minutes after release are a speed race. A retail-speed participant is structurally late in the release minute.
- Products and horizon: grain futures; seconds to minutes after release. Livestock reports are released after the close.
- Cost assumptions, data window: none; practitioner and policy essay.
- Quality tells: opinion piece; delay magnitudes are the author's personal experience.
- Verbatim passages:
  - P-K6-012-a: "Everything changed in May 2012 when USDA crop reports began to be released during regular trading hours of futures exchanges."
  - P-K6-012-b: "the USDA moved the release time for important crop reports to 11am CST in January 2013, roughly midway through the traditional daytime trading session for grain futures markets."
  - P-K6-012-c: "(livestock reports are still released after futures markets are closed)"
  - P-K6-012-d: "Wait times in the first few years of real-time release could be as much as 15-20 minutes to download the reports. This has improved over time as the USDA has increased server capacity, but in my experience it can still easily be a five-minute delay."
  - P-K6-012-e: "approximately a two-second speed advantage to subscribers to the news organizations over the general public when accessing the report through USDA servers. In light of this disparity, the USDA stopped allowing news organizations to have early access to crop reports starting in July 2018."
- Numeric claims: 11:00 CT release since January 2013 (P-K6-012-b); two-second advantage (P-K6-012-e); 15-20 and 5 minute delays (P-K6-012-d, anecdotal).
- Tags: port of D.1 family E. Intraday-feasible: yes, 11:00 CT is inside the 08:30-13:20 CT grain session (consistent with container 4 where checked). A release-minute entry is not feasible for this program (speed); only post-release windows are.
- Clusters tagged: K6.

### K6-013 (container 2)
- Citation: Janzen, J. (2025). "Quiet Signals: Why Boring Crop Reports Matter." farmdoc daily, March 2025.
- Retrieval: full text, https://farmdocdaily.illinois.edu/2025/03/quiet-signals-why-boring-crop-reports-matter.html (figures are images).
- Mechanism: none on prices; documents which WASDE months usually change the US corn, soybean and wheat balance sheets (growing-season months) and which are quiet (December and March for corn and soybeans; September, November and March for wheat). Useful for choosing which report months to treat as events.
- Products and horizon: ZC, ZS, ZW; monthly WASDE calendar.
- Cost assumptions: none. Data window: every WASDE since the 2010/11 marketing year.
- Quality tells: descriptive; balance-sheet changes, not price moves.
- Verbatim passages:
  - P-K6-013-a: "For corn and soybeans, December and March are especially quiet months. For instance, soybean total use and stocks changes rarely exceed 50 million bushels in these months. September, November, and March are quiet months for wheat."
  - P-K6-013-b: "It is relatively rare to see changes over roughly 300 million bushels for corn, 150 million bushels for soybeans, or 75 million bushels for wheat. Changes in excess of these thresholds occurred in only 5-8% of report releases since June 2010, depending on the crop."
  - P-K6-013-c: "Production updates are extremely rare after November for wheat and after January for corn and soybeans."
- Numeric claims: thresholds and 5-8% frequency (P-K6-013-b).
- Tags: port of D.1 family E (event selection by month). Intraday-feasible: n/a (a filter, not a mechanism).
- Clusters tagged: K6.

### K6-014 (container 3)
- Citation: Joseph, K. and Garcia, P. (2016). "Intraday Market Effects in Electronic Soybean Futures Market during Non-Trading and Trading Hour Announcements." Selected paper, AAEA Annual Meeting, Boston, July 31-August 2, 2016. AgEcon Search DOI 10.22004/ag.econ.235772.
- Retrieval: full text, Wayback copy of the AgEcon PDF, https://web.archive.org/web/20241117204227/https://ageconsearch.umn.edu/record/235772/files/AAEA2016_USDA%20Report%20Effects.pdf (AgEcon Search itself returns an AWS WAF challenge to curl and 403 to WebFetch).
- Mechanism: USDA reports (WASDE, Crop Production, Grain Stocks, Acreage, Prospective Plantings) released inside the session produce a smaller but longer volatility spike than releases before the open; no systematic under- or overreaction in the first 15 minutes.
- Products and horizon: ZS nearby; 15-second returns, 15 minutes before to 60 minutes after release.
- Cost assumptions: none. Data window: June 2010-May 2014 (30 non-trading-hour and 29 trading-hour releases), CME Globex time and sales.
- Quality tells: small event counts; the authors caution that the correlation tests rest on small samples. Note an apparent typo in the source ("January 2011-May 2014" for the 11:00 releases, which began January 2013).
- Verbatim passages:
  - P-K6-014-a (Abstract): "report releases during non-trading hours cause a large spike in volatility at the onset of trading which subsides quickly. In contrast, releases during trading hours result in a smaller volatility spike which extends for five to six minutes at a higher magnitude."
  - P-K6-014-b (Abstract): "Return correlations provide little evidence to support systematic under- or overreaction in prices regardless of when the report is released, reflecting the efficiency of the market."
  - P-K6-014-c (Introduction): "major United Stated Department of Agriculture (USDA) reports released at 7:30 a.m. central time ... coincided with real-time trading hours. In January 2013, USDA officially shifted these reports releases to 11:00 a.m., formalizing trading hour re- leases."
  - P-K6-014-d (Results): "While, the difference in return variance is short lived for the first period, it is significant in the second period for 30 to 40 minutes after the release and appears to persist intermittently for nearly 60 minutes."
  - P-K6-014-e (Results): "For both periods, the first significant interval correlation is negative which raises the possibility that the market overreacts to news within the first minute and then corrects quickly in later periods. ... Nevertheless, it is difficult to establish a solid pattern from the results."
  - P-K6-014-f (Data): "The announcement data reflect WASDE, CP, GS, AC, and PP reports from June 2010-May 2014."
- Numeric claims: 5-6 minute spike (P-K6-014-a); 30-40 minute significant variance difference (P-K6-014-d).
- Tags: port of D.1 family E (release-time volatility). Intraday-feasible: yes (11:00 CT inside session); the source finds no directional continuation or reversal to exploit.
- Clusters tagged: K6.

### K6-017 (container 3)
- Citation: Karali, B., Isengildina-Massa, O., Irwin, S.H., Adjemian, M.K. and Johansson, R. (2019). "Are USDA reports still news to changing crop markets?" Food Policy 84, 66-76. DOI 10.1016/j.foodpol.2019.02.005.
- Retrieval: full text (published PDF), VTechWorks https://vtechworks.lib.vt.edu/bitstreams/fa60c40a-70c1-4520-a7e2-13131ec3cdfb/download (handle 10919/97116).
- Mechanism: the report surprise (USDA estimate minus private expectation) moves corn, soybean and wheat futures; surprise sizes have not shrunk and price reaction to most reports has increased after 2007.
- Products and horizon: ZC, ZS, ZW (winter and spring wheat); daily close-to-close.
- Cost assumptions: none. Data window: 1984/85-2016/17 marketing years (wheat from 1994/95).
- Quality tells: seed paper (Karali and co-authors); daily data by design because release times changed.
- Verbatim passages:
  - P-K6-017-a (Abstract): "The stable size of market surprises over time suggests that competition from alternative data sources has not reduced the news component of USDA crop reports. Increasing price reaction to most reports, including those facing competition from alternative information sources, suggests that value of public information may be enhanced in uncertain markets affected by structural changes."
  - P-K6-017-b (Section 3): "the release times of the considered USDA reports during our study period are 3:00pm EST (January 1984-April 1994), 8:30am EST (May 1994-December 2012), and 12:00pm EST (January 2013- January 2017). While close-to-close returns, Pt , may not reflect the full price reaction to USDA news (Isengildina et al., 2006), their use is required in this study due to changes in both trading times and the report release times during our sample period." (two-column extraction; words joined across the column break)
  - P-K6-017-c (Figure notes): "Sample period is 1984/85–2016/17 marketing years for corn and soybeans and 1994/95–2016/17 marketing years for winter and spring wheat."
- Numeric claims: release-time history (P-K6-017-b). Reaction coefficients not transcribed.
- Tags: port of D.1 family E. Intraday-feasible: not as measured (daily); the release-time passage places the current release at 12:00 ET = 11:00 CT, inside the session.
- Clusters tagged: K6.

### K6-018 (container 3)
- Citation: Isengildina-Massa, O., Cao, X., Karali, B., Irwin, S.H., Adjemian, M. and Johansson, R.C. (2021). "When does USDA information have the most impact on crop and livestock markets?" Journal of Commodity Markets 22, 100137. DOI 10.1016/j.jcomm.2020.100137.
- Retrieval: full text (journal pre-proof layout), VTechWorks https://vtechworks.lib.vt.edu/bitstreams/25def527-0597-478a-821f-c18b709cfdc7/download (handle 10919/106679).
- Mechanism: report-day variance ratios by report cluster and month; the largest reactions come from clusters containing Grain Stocks, Prospective Plantings, Acreage and the Annual Summary; WASDE alone moves markets less; Cattle on Feed and Hogs and Pigs move livestock only in a few months.
- Products and horizon: ZC, ZS, ZW, LE, HE (and cotton); daily close-to-close, with afternoon releases assigned to the next session.
- Cost assumptions: none. Data window: 1985-2018.
- Quality tells: daily data; hog limit days adjusted by carrying the return forward.
- Verbatim passages:
  - P-K6-018-a (Section 2): "Cattle on Feed reports ... are typically released at 3:00pm EST on the third Friday of the month" and "Hogs and Pigs reports ... are typically released at 3:00pm EST on Friday near the end of March, June, September, and December".
  - P-K6-018-b (Section 2): "The release schedule for Grain Stocks reports changed similarly to the other reports described above with 3pm EST release time through June 1994, 8:30 a.m. EST release time from September 1994–September 2012 and 12pm EST release time from January 2013 to present."
  - P-K6-018-c (Section 3): "in crops, prices reached a limit move only in about 2% of total observations, a frequency low enough not to warrant any adjustments. The presence of limit moves was also low in cattle (4.4% of total observations), but not in hogs, where prices reached the limit in 8% of total observations. More importantly, 28.5% of the days with Hogs and Pigs report releases were subject to price limit moves."
  - P-K6-018-d (Section 4): "January report clusters that included Grain Stocks, Crop Production Annual Summary and WASDE reports increased the variance of nearby corn prices by about 7.7 times."
  - P-K6-018-e (Section 4): "very few reports had a statistically significant impact on the cattle markets, namely May through July and September COF reports and June HPR reports. The magnitude of these market reactions was moderate with cattle futures volatility increasing by less than two times in all cases. Market reaction to USDA information was even less common in lean hog markets with significant reaction observed only for June HPR reports, when hog market variance increased by 2.8 times"
  - P-K6-018-f (Section 4): "the clusters containing Grain Stocks, Prospective Plantings, Acreage reports and Crop Production Annual Summary reports appear to cause largest market reactions, while WASDE reports do not seem to move the markets as much."
- Numeric claims: limit frequencies 2%, 4.4%, 8%, 28.5% (P-K6-018-c); 7.7x corn variance (P-K6-018-d); <2x cattle, 2.8x hogs (P-K6-018-e).
- Tags: port of D.1 family E (event selection). Intraday-feasible: livestock reports at 3:00pm ET = 2:00pm CT fall after the 13:05 CT livestock close, so their effect is a next-morning gap a rule can read but not hold into; the Hogs and Pigs limit frequency (28.5%) bears on Topstep's 2%-of-lock-limit rule.
- Clusters tagged: K6.

### K6-021 (container 3)
- Citation: Wang, X., Garcia, P. and Irwin, S.H. (2014). "The Behavior of Bid-Ask Spreads in the Electronically-Traded Corn Futures Market." American Journal of Agricultural Economics 96(2). DOI 10.1093/ajae/aat096. Version read: NCCC-134 2012 conference paper, AgEcon 10.22004/ag.econ.285781 (one source; Unpaywall lists this as the OA copy of the AJAE article).
- Retrieval: full text, https://web.archive.org/web/20231124234452/https://ageconsearch.umn.edu/record/285781/files/confp04-12.pdf.
- Mechanism: none tradable; measures the observed corn bid-ask spread and its drivers (widens on Grain Stocks and Production-WASDE days, with short-term trends, near expiry).
- Products and horizon: ZC nearby and next nearby; daily averages of intraday quotes.
- Cost assumptions: this is a cost source. Data window: 2008 to early 2010.
- Quality tells: turbulent sample; pre-11:00-release era.
- Verbatim passages:
  - P-K6-021-a (Abstract): "indicates that the BAS is generally small (well below two ticks), despite the turbulent market in the 2008 to early 2010 sample period."
  - P-K6-021-b (Abstract): "In both periods, USDA Grain Stock and Production-WASDE announcements significantly widen the BAS, as do short-term price trends."
  - P-K6-021-c (Conclusions): "During the last forty trading days prior to the expiration month, the average BAS is slightly more than one tick, 0.314 cents/bushel, supporting the notion that the corn futures market is highly liquid."
- Numeric claims: average BAS 0.314 cents/bu, slightly more than one 0.25-cent tick (P-K6-021-c).
- Tags: cost input for ZC (not a mechanism). Intraday-feasible: n/a.
- Clusters tagged: K6.

### K6-023 (container 3)
- Citation: Couleau, A., Serra, T. and Garcia, P. (2019). "Microstructure Noise and Realized Variance in the Live Cattle Futures Market." American Journal of Agricultural Economics 101(2). DOI 10.1093/ajae/aay052. Version read: NCCC-134 2017 paper "The Effects of Microstructure Noise on Realized Volatility in the Live Cattle Futures Market", AgEcon 10.22004/ag.econ.285873 (one source).
- Retrieval: full text, https://web.archive.org/web/20240828232526/https://ageconsearch.umn.edu/record/285873/files/Couleau_Serra_Garcia_NCCC-134_2017.pdf. The AJAE abstract was read from Crossref.
- Mechanism: none tradable; microstructure noise inflates LE realized variance below about 4-minute sampling; quote activity is U-shaped (first and last 15 minutes); 2015 volatility was fundamental.
- Products and horizon: LE June contracts; intraday.
- Cost assumptions: none. Data window: 2011-2015 (AJAE version 2011-2016).
- Quality tells: one contract month per year.
- Verbatim passages:
  - P-K6-023-a (WP abstract): "While market microstructure noise is found to increase realized volatility when the sampling frequency is below 4-minute time intervals, the particularly high volatility in live cattle markets in 2015 is found to be strongly driven by market fundamentals"
  - P-K6-023-b (AJAE abstract, Crossref): "Market microstructure noise increases observed price variance, but its effects are not large and do not last more than three to four minutes in response to changing information."
  - P-K6-023-c (WP, Data): "The U-shape reveals a concentration of quotes at the beginning and the end of the day. This likely corresponds to the accumulation of information overnight, which is reflected in the first 15 minutes, or adjustments to expected overnight information, which is reflected in the 15 minutes before the futures pit trading closes"
  - P-K6-023-d (WP, Data): "the cancelation of the night session by the exchange in October 2014 is likely to have shifted the overnight trading to the day trading sessions"
- Numeric claims: 4-minute noise threshold (P-K6-023-a, b).
- Tags: bar-size guidance for LE (G family: bars under about 4-5 minutes are noise-dominated). Intraday-feasible: n/a.
- Clusters tagged: K6.

### K6-024 (container 3)
- Citation: Couleau, A., Serra, T. and Garcia, P. (2020). "Are Corn Futures Prices Getting 'Jumpy'?" American Journal of Agricultural Economics 102(2). DOI 10.1002/ajae.12030. Version read: NCCC-134 2018 paper, AgEcon 10.22004/ag.econ.285883 (one source).
- Retrieval: full text of the working paper, https://web.archive.org/web/20220108004832/https://ageconsearch.umn.edu/record/285883/files/Couleau_Serra_Garcia_NCCC-134_2018.pdf; AJAE abstract from Crossref.
- Mechanism: since USDA reports moved into the session, intraday jumps cluster around the release time and are larger on report days; on non-report days jumps are more frequent but smaller.
- Products and horizon: ZC nearby; second-level ticks.
- Cost assumptions: none; AJAE abstract says real-time release raises liquidity costs.
- Data window: January 2008-December 2015.
- Quality tells: the WP and the AJAE abstract disagree on who bears the most jump risk (WP: slow traders; AJAE: high-frequency traders).
- Verbatim passages:
  - P-K6-024-a (WP, Introduction): "The new report release policy has also changed intraday jump times, from a relatively even distribution throughout the day to a concentration of jumps around the report release time. Jump size has increased after May 21, 2012 for announcement days, but has declined for non-announcement days."
  - P-K6-024-b (WP, Introduction): "We also show that traders operating at slow frequency face more jump risk than traders operating at higher frequency during announcement days."
  - P-K6-024-c (AJAE abstract, Crossref): "Real‐time trading of major USDA reports has substantially increased the frequency and clustering of price jumps, and results in higher market liquidity costs. In contrast, although the presence of jumps on non‐announcement days has doubled recently, their magnitude has declined as have transactions costs during their occurrence. The largest jump risk or execution risk is experienced by high frequency traders"
- Numeric claims: none transcribed beyond "doubled" (P-K6-024-c).
- Tags: port of D.1 family D/E (report-time jump risk; stop placement and slippage around 11:00 CT). Intraday-feasible: n/a as a signal; relevant to risk around releases.
- Clusters tagged: K6.

### K6-026 (container 3)
- Citation: Zhou, X., Bagnarosa, G., Gohin, A., Pennings, J.M.E. and Debie, P. (2023). "Microstructure and high-frequency price discovery in the soybean complex." Journal of Commodity Markets 30, 100314. DOI 10.1016/j.jcomm.2023.100314 (CC BY). NCCC-134 2022 version (10.22004/ag.econ.329789) is the same source and was not read separately.
- Retrieval: full text, https://edepot.wur.nl/629433.
- Mechanism: at one-minute frequency the ZS/ZM/ZL crush is cointegrated during the 08:30-13:20 CT session once non-synchronous trading and noise are filtered, but the cointegration fades in the overnight session; speed of reversion depends on traded volume; stronger on USDA days.
- Products and horizon: ZS, ZM, ZL; one-minute snapshots within a day.
- Cost assumptions: none. Data window: all of 2015 (243 trading days), CME market-by-order data.
- Quality tells: one year; econometric, no trading rule.
- Verbatim passages:
  - P-K6-026-a (Abstract): "Our analysis further suggests that the presence of cointegration among assets is related to the time of day and the contract maturities traded at a given time."
  - P-K6-026-b (Section 4): "we distinguish two periods within a trading day: the electronic trading session from 7 PM to 7.45 AM (session 1) and the market trading session from 8.30 AM to 1.20 PM (session 2). While the latter trading session is shorter, it contains the most trading activity."
  - P-K6-026-c (Section 5.1): "A high level of cointegration is indeed observed during session 2 trading hours, which fades away during session 1. Another interesting result is the stronger intraday cointegration observed on average on USDA announcement days, although the number of observations available is limited."
  - P-K6-026-d (Section 4): "The high-frequency data used in this study covers the total trading activity of 2015, amounting to 243 trading days."
  - P-K6-026-e (Section 5.1): "Hardly any cointegration was detected using Johansen's approach, regardless of the matching method applied."
- Numeric claims: 243 days (P-K6-026-d).
- Tags: new to the program (intraday crush reversion; complements K6-001). Intraday-feasible: yes, day session only.
- Clusters tagged: K6.

### K6-029 (container 3)
- Citation: Bian, S., Serra, T. and Garcia, P. (2018). "The Value of Public Information: Market Microstructure Noise and Price Volatility Spillovers in Agricultural Commodity Markets." Proceedings of the NCCC-134 Conference, Minneapolis, April 16-17, 2018. AgEcon 10.22004/ag.econ.285882.
- Retrieval: full text, https://web.archive.org/web/20240828231502/https://ageconsearch.umn.edu/record/285882/files/Bian_Serra_Garcia_NCCC-134_2018.pdf.
- Mechanism: on 11:00 release days corn and soybean volatility and corn-soy correlation rise from 10-20 minutes before release and stay above normal to the close; noise effects fade in about 30 minutes.
- Products and horizon: ZC, ZS nearby; 5-minute and finer mid-quotes, 9:00-13:00.
- Cost assumptions: none. Data window: January 2014 to May 2017.
- Quality tells: conference paper; "profit opportunities" stated without a test.
- Verbatim passages:
  - P-K6-029-a (Conclusion): "Research results suggest that USDA announcements elevate intraday mid-quote observed, efficient and noise return volatility between 20 and 10 minutes before the report release. The USDA impacts do not dissipate after the announcement and last till the end of the trading session."
  - P-K6-029-b (Conclusion): "Relative to non-announcement days, the magnitudes of the increases are substantial, with volatility in efficient and observed returns increasing five/six-fold and noise volatility increasing 10/12-fold."
  - P-K6-029-c (Conclusion): "Efficient return correlations increase right after announcement and remain about 50% higher than regular days till the end of the session. In contrast, observed returns correlation fades in about 30 minutes after the announcement."
  - P-K6-029-d (Data): "The analysis focuses on the period from January 2014 to May 2017."
  - P-K6-029-e (Abstract): "After 2013, major grain-related USDA announcements have been rescheduled to be released at 11:00 am CDT."
- Numeric claims: five/six-fold and 10/12-fold (P-K6-029-b); 50% higher correlation (P-K6-029-c).
- Tags: port of D.1 family D/E (report-day volatility state lasting to the close). Intraday-feasible: yes.
- Clusters tagged: K6.

### K6-034 (container 3)
- Citation: Lehecka, G.V. (2014). "The Value of USDA Crop Progress and Condition Information: Reactions of Corn and Soybean Futures Markets." Journal of Agricultural and Resource Economics 39(1), 88-105. AgEcon 10.22004/ag.econ.168261 (the 2013 NCCC version, 10.22004/ag.econ.142491, is the same source and was not read).
- Retrieval: full text, https://web.archive.org/web/20251016021529/https://ageconsearch.umn.edu/record/168261/files/JARE_Apr2014__6_Lehecka_pp88-105.pdf.
- Mechanism: weekly Crop Progress condition changes move corn and soybeans in the expected direction at the next open (close-to-open); no significant follow-through in the report day's open-to-close or the next two days.
- Products and horizon: ZC, ZS; close-to-open and open-to-close on the first trading day after the Monday release.
- Cost assumptions: none. Data window: 1986-2012, April to November.
- Quality tells: pre-2012 session structure (no evening session in most of the sample); the author warns the ex post patterns are not a trading strategy.
- Verbatim passages:
  - P-K6-034-a (Section 2): "CP reports are released at 4:00 p.m. EST on the first business day of the week, after the end of the daily trading session and before the subsequent trading session opens at the Chicago Board of Trade (CBOT)."
  - P-K6-034-b (Results): "For the entire sample period, coefficient estimates are significant only for the close-to-open return on the report-release trading day. Significant results could not be found for the open-to-close return of the report-release trading day or close-to-close returns on the following two postreport trading days."
  - P-K6-034-c (Results): "Price impacts are strongest in summer (July and August) when weather conditions (precipitation and temperature) are critical for the crop."
  - P-K6-034-d (Results): "for soybeans in the fourth subsample, the relatively large change in sign and magnitude of coefficients from the close-to-open to the following open-to-close return on the report-release day suggests that overreaction may be present. However, these ex post results do not necessarily imply that a profitable trading strategy could have been developed"
  - P-K6-034-e (Abstract): "analyzing reactions of corn and soybean futures markets from 1986 to 2012."
- Numeric claims: none transcribed (coefficient tables not transcribed).
- Tags: port of D.1 family E (weekly Monday release). Intraday-feasible: the reaction is overnight (4:00 p.m. ET = 3:00 p.m. CT Monday, before the 7:00 p.m. CT evening open); the source finds no day-session follow-through, i.e. evidence against an intraday continuation rule. The soybean late-sample reversal hint (P-K6-034-d) is the only intraday lead.
- Clusters tagged: K6.

### K6-020 (container 3)
- Citation: Bunek, G.D. and Janzen, J.P. (2024). "Does public information facilitate price consensus? Characterizing USDA announcement effects using realized volatility." Journal of Commodity Markets, DOI 10.1016/j.jcomm.2024.100382. Version read: NCCC-134 2015 paper "Characterizing the Effect of USDA Report Announcements in the Winter Wheat Futures Market Using Realized Volatility", AgEcon 10.22004/ag.econ.285838 (treated as one source; whether the 2024 article widened the product set is [unverified]).
- Retrieval: full text of the 2015 paper, https://web.archive.org/web/20240828092147/https://ageconsearch.umn.edu/record/285838/files/Bunek_Janzen_NCCC_134_2015.pdf. The JCM version: ScienceDirect blocked, Crossref has no abstract.
- Mechanism: on USDA report days realized volatility rises rather than falls (contrary to the implied-volatility literature); the increase fades in under 10 minutes.
- Products and horizon: KC hard red winter wheat (KE; a close microstructure analogue of ZW, not ZW itself); daily, first 15 minutes, and within-minute RV.
- Cost assumptions: none. Data window: 2008-2012, KCBT transaction data (reports then released before the open).
- Verbatim passages:
  - P-K6-020-a (Abstract): "All results suggest that realized volatility does not decrease following USDA wheat report releases but instead increases."
  - P-K6-020-b (Introduction): "the speed at which increased RV disappears, less than 10 minutes, attests to the efficiency of the wheat futures market."
  - P-K6-020-c (Data): "Only a five year period of 2008 to 2012 is used where this data"
- Numeric claims: under 10 minutes (P-K6-020-b).
- Tags: port of D.1 family D/E (report-open volatility). Intraday-feasible: n/a (volatility fact).
- Clusters tagged: K6.

### K6-022 (container 3)
- Citation: Frank, J. and Garcia, P. (2011). "Bid-Ask Spreads, Volume, and Volatility: Evidence from Livestock Markets." American Journal of Agricultural Economics 93(1). DOI 10.1093/ajae/aaq116. Version read: 2009 AAEA paper, AgEcon 10.22004/ag.econ.49575 (one source).
- Retrieval: full text, https://web.archive.org/web/20170923064118/http://ageconsearch.umn.edu/record/49575/files/2009_AAEA_Frank-Garcia.pdf.
- Mechanism: none tradable; liquidity-cost estimates for LE and HE and their drivers (volume lowers, volatility raises the spread; electronic trading lowers costs, mainly in cattle).
- Products and horizon: LE, HE; daily estimates from intraday prices.
- Cost assumptions: this is a cost source. Data window: 2005-2008 (pit era with growing electronic share).
- Verbatim passages:
  - P-K6-022-a (Abstract): "Daily volume is negatively related to the spread while volatility and volume per transaction display positive relationships. Electronic trading has a significant competitive effect on liquidity costs, particularly in the live cattle market."
  - P-K6-022-b (Results): "The ABS estimates are the closest to the tick level—the minimum price changed allowed by the exchange—of 0.025 cents/lb."
  - P-K6-022-c (Table 1, spread estimators, cents/lb; lean hogs Apr-Aug-Dec, Feb-Jun-Oct; live cattle Apr-Aug-Dec, Feb-Jun-Oct): "ABS 0.0300 0.0297 0.0245 0.0244"
  - P-K6-022-d (Data): "In hogs and cattle markets the open outcry regular trading hours are 9:05am to 1:00pm."
- Numeric claims: tick 0.025 cents/lb (P-K6-022-b); ABS spread estimates 0.024-0.030 cents/lb (P-K6-022-c).
- Tags: cost input for LE/HE. Intraday-feasible: n/a.
- Clusters tagged: K6.

### K6-031 (container 3)
- Citation: Hu, Z., Mallory, M., Serra, T. and Garcia, P. (2017). "Measuring Price Discovery between Nearby and Deferred Contracts in Storable and Non-Storable Commodity Futures Markets." NCCC-134 2017; AgEcon 10.22004/ag.econ.285866; arXiv 1711.03506 (one source).
- Retrieval: full text, https://web.archive.org/web/20231125222525/https://ageconsearch.umn.edu/record/285866/files/Hu_Mallory_Serra_Garcia_NCCC-134_2017.pdf.
- Mechanism: none tradable at bar frequency (one-second information leadership); the nearby contract leads deferreds in corn until its volume share falls below 50%, about 2-3 weeks before expiry (5-6 weeks in live cattle). Relevant to which contract a rule should trade and when to roll.
- Products and horizon: ZC, LE; one-second data.
- Data window: corn January 14, 2008-December 14, 2015; live cattle January 1, 2008-December 31, 2015; CME Top-of-Book.
- Verbatim passages:
  - P-K6-031-a (Abstract): "On average, nearby contracts lead all deferred contracts in price discovery in the corn market, but have a relatively less dominant role in the live cattle market. In both markets, the nearby contract loses dominance when its relative volume share dips below 50%, which occurs about 2-3 weeks before expiration in corn and 5-6 weeks before expiration in live cattle."
  - P-K6-031-b (Data): "The sample period studied for corn is from January 14, 2008 through December 14, 2015, and the period used for live cattle ranges from January 1, 2008 to December 31, 2015."
- Numeric claims: 2-3 and 5-6 weeks (P-K6-031-a).
- Tags: contract-selection input (roll timing). Intraday-feasible: n/a.
- Clusters tagged: K6.

### K6-033 (container 3)
- Citation: Li, Z., Wang, Z. and Diersen, M. (2024). "Do Agricultural Commodity Price Spikes Always Stem from News?" NCCC-134 2024; AgEcon 10.22004/ag.econ.379009.
- Retrieval: full text, https://web.archive.org/web/20251211151956/https://ageconsearch.umn.edu/record/379009/files/Li_Wang_Diersen_NCCC-134_2024.pdf.
- Mechanism: classifies 5-minute corn jump clusters as news-matched (same-day news) or endogenous; about two thirds have no same-day news; describes pre- and post-jump volatility profiles. No trading rule.
- Products and horizon: ZC; 5-minute returns.
- Data window: 01/01/2013-12/31/2022; news from ProQuest "U.S. Major Dailies", matched by date only.
- Quality tells: news matched by day, not timestamp (the authors say so); conference draft.
- Verbatim passages:
  - P-K6-033-a (Data/Method): "we record 3,094 clusters of jumps that occurred over a total of 2,403 trading days. Of these, there are 994 news- related clusters of jumps on 494 days, which occupy 32.13% of all clusters. The non-news-related clusters account for 67.87%."
  - P-K6-033-b (Introduction): "we could not match the daily news precisely to the timestamp of our intraday trading data."
  - P-K6-033-c (Data): "The end-of-5-minute ... from 01/01/2013 to 12/31/2022." (text interrupted in extraction)
- Numeric claims: 3,094 clusters, 32.13% news-related (P-K6-033-a).
- Tags: port of D.1 family D/F (jump state). Intraday-feasible: n/a as a rule.
- Clusters tagged: K6.

### K6-015 (container 3) ABSTRACT ONLY
- Citation: Lehecka, G.V., Wang, X. and Garcia, P. (2014). "Gone in Ten Minutes: Intraday Evidence of Announcement Effects in the Electronic Corn Futures Market." Applied Economic Perspectives and Policy 36(3), 504-526. DOI 10.1093/aepp/ppu010.
- Retrieval: abstract only (Crossref record). Failed: Semantic Scholar (openAccessPdf CLOSED), Unpaywall (no OA), Wiley and OUP (Cloudflare / not archived in Wayback), no AgEcon working-paper version found by DataCite; web search engines unavailable.
- P-K6-015-a (abstract): "intraday Chicago Board of Trade corn futures prices and trading volume from the electronic trading platform for July 2009 to May 2012."
- P-K6-015-b (abstract): "Strongest price reactions to the releases are found immediately after the market opens, and market reactions persist for approximately ten minutes. The electronic corn futures market quickly incorporates this new public information, and little evidence exists to support systematic under‐ or overreactions in prices. Other more subtle reactions occur in the last trading session before USDA announcements as traders adjust their market exposure in anticipation of the release."
- Tags: port of D.1 family E. Intraday-feasible: pre-2012 releases before the open; the "last trading session before" adjustment is a pre-release positioning effect, magnitude [unverified]. Summaries in K6-014 (Joseph and Garcia, p. 2) agree with the abstract.
- Clusters tagged: K6.

### K6-016 (container 3) ABSTRACT ONLY
- Citation: Adjemian, M.K. and Irwin, S.H. (2018). "USDA Announcement Effects in Real-Time." American Journal of Agricultural Economics 100(4), 1151-1171. DOI 10.1093/ajae/aay018.
- Retrieval: abstract only (Crossref record). Failed: Unpaywall (no OA), OUP page archived only as a 301 redirect, Wiley Cloudflare, DataCite found no working-paper version.
- P-K6-016-a (abstract): "In 2012, the Chicago Board of Trade eliminated a morning trading halt that coincided with the normal publication time for important USDA commodity reports."
- P-K6-016-b (abstract): "We use 2009–2014 intraday grain futures market price and volume data to show that, without a trading halt, ensuing real‐time trading on USDA crop announcements exhibits noticeable volatility spikes in agricultural futures markets, but that this heightened volatility dissipates within the space of a few trading minutes."
- Products (which grains), magnitudes: [unverified].
- Tags: port of D.1 family E (seed paper, "Adjemian and Irwin on release timing", verified to exist). Intraday-feasible: yes (11:00 CT releases).
- Clusters tagged: K6.

### K6-019 (container 3) ABSTRACT ONLY
- Citation: Indriawan, I., Martinez, V. and Tse, Y. (2021). "The impact of the change in USDA announcement release procedures on agricultural commodity futures." Journal of Commodity Markets. DOI 10.1016/j.jcomm.2020.100149 (registry line K6-019 names the journal only; DOI resolved afterwards).
- Retrieval: abstract only, from a Wayback copy of the ScienceDirect abstract page (https://web.archive.org/web/20240416214233/https://www.sciencedirect.com/science/article/abs/pii/S240585132030026X). ScienceDirect itself returns a captcha; WebFetch 403; Unpaywall no OA.
- P-K6-019-a (abstract): "In August 2018, the US Department of Agriculture (USDA) ceased its practice of early media access during lockup, in which the news media have access to crop and livestock reports ahead of scheduled announcements."
- P-K6-019-b (abstract): "Although the majority of our market quality proxies react to USDA news releases, they are not statistically different before and after the regulatory change."
- Note: K6-012 (Irwin) dates the end of media early access to July 2018; this source says August 2018.
- Tags: port of D.1 family E (release microstructure). Products and window: [unverified].
- Clusters tagged: K6.

### K6-025 (container 3) ABSTRACT ONLY
- Citation: He, ?, Serra, T. and Garcia, P. (2020). "Resilience in 'Flash Events' in the Corn and Lean Hog Futures Markets." American Journal of Agricultural Economics. DOI 10.1111/ajae.12146.
- Retrieval: abstract only (Crossref). Unpaywall lists https://onlinelibrary.wiley.com/doi/pdfdirect/10.1111/ajae.12146 as OA, but Wiley serves Cloudflare to curl and it is not in Wayback.
- P-K6-025-a (abstract): "Using intra‐day data, we examine liquidity resilience during \"flash events\" in corn and lean hog futures markets from 2014 to 2019. Overall, we find little evidence that the liquidity provision in these two markets relative to normal days becomes fragile when large price movements occur. Our analysis suggests that flash events are heavily influenced by unanticipated changes in fundamentals that may lead to a new equilibrium price."
- Tags: port of D.1 family C/D (large intraday moves; the abstract points against a reversal after flash moves). Magnitudes [unverified].
- Clusters tagged: K6.

### K6-027 (container 3) ABSTRACT ONLY
- Citation: Aitkulova, I., Balsamo, E. and Seamon, F. (2026). "WASDE Surprises and Futures Prices: What Moves Markets?" AgEcon 10.22004/ag.econ.410270.
- Retrieval: abstract only (DataCite record). AgEcon Search blocks curl (AWS WAF) and WebFetch (403); no Wayback capture of the files.
- P-K6-027-a (abstract): "Using polling estimations to calculate a degree of \"surprise\" for each WASDE release, we found statistically significant relationships between U.S. corn and soybean ending stock data and relevant corn and soybean futures intraday price movements post-release, with the nature of correlations changing as time from the release passed. Additionally, directionally correct drift prior to release suggests that we also observed informed trading and/or superior internal research."
- Tags: port of D.1 family E (pre-release drift and post-release path). Needs trade-guess data. Window, magnitudes: [unverified]. Venue and peer review status [unverified].
- Clusters tagged: K6.

### K6-028 (container 3) ABSTRACT ONLY
- Citation: Zhu, X., Adjemian, M., Bagnarosa, G. and Gohin, A. (2026). "Do USDA Reports Align Trader Expectations?" AgEcon 10.22004/ag.econ.404355.
- Retrieval: abstract only (DataCite). Same failures as K6-027.
- P-K6-028-a (abstract): "We test that premise by estimating the volume–volatility elasticity around WASDE and Grain Stocks releases in the CME corn futures market using high-frequency data from 2013 to 2020."
- P-K6-028-b (abstract): "we estimate unconditional elasticities that are persistently below unity, consistent with incomplete post-report alignment of trader expectations."
- Tags: port of D.1 family E/D. Magnitudes [unverified].
- Clusters tagged: K6.

### K6-030 (container 3) ABSTRACT ONLY
- Citation: Kauffman, N.S. (2013). "Have Extended Trading Hours Made Agricultural Commodity Markets More Risky?" NCCC-134 2013; AgEcon 10.22004/ag.econ.285787.
- Retrieval: abstract only (DataCite). The Wayback capture of the PDF (https://web.archive.org/web/20240829104944/https://ageconsearch.umn.edu/record/285787/files/Kauffman_NCCC-134_2013.pdf) is truncated at exactly 1,048,576 bytes; pdftotext and Ghostscript both fail. Two later papers summarise it (K6-014 p. 2-3).
- P-K6-030-a (abstract): "The results suggest that trading during the information releases in 2012 has led to brief periods of excessive volatility immediately after the reports were released, but the higher volatility did not persist much beyond 60 minutes."
- Tags: port of D.1 family D/E (ZC). Window beyond "2012": [unverified].
- Clusters tagged: K6.

### K6-032 (container 3) ABSTRACT ONLY
- Citation: Avileis, F.G. and Swanson, A. (2025). "EPA and CARB Announcements and the Balancing Act Between Soybeans, Soybean Oil, and Meal." AgEcon 10.22004/ag.econ.379000.
- Retrieval: abstract only (DataCite); no Wayback capture of the files.
- P-K6-032-a (abstract): "we analyze 36 policy events between 2021 and 2025, including Environmental Protection Agency (EPA) announcements, California Air Resources Board (CARB) reports, and news \"leaks\" from media sources with early information access. We find that soybean oil futures return increase significantly on announcement days (0.59%) and continue rising the following day (0.62%), exhibiting what we term Post-Announcement-Leak Drift (PALD)."
- P-K6-032-b (abstract): "a 1% biofuel-induced price increase in soybean oil leads to a 0.19% rise in soybean prices and a 0.30% drop in soybean meal prices."
- Tags: new to the program (biofuel-policy events in the crush). Intraday-feasible: only the next day's day-session part of the drift, split not reported [unverified]. Boundary note: the event is a regulatory announcement, not an energy price leg, so it is logged here; the lead may route it to K8 if biofuel policy counts as "ags against energy".
- Clusters tagged: K6 (possible K8).

### K6-035 (container 3; found via a container-1 Brave result) ABSTRACT ONLY
- Citation: He, X. and Serra, T. (2022). "Are price limits cooling off agricultural futures markets?" American Journal of Agricultural Economics 104(5), 1724-1746. DOI 10.1111/ajae.12306.
- Retrieval: abstract only, IDEAS https://ideas.repec.org/a/wly/ajagec/v104y2022i5p1724-1746.html. Failed: Unpaywall (no OA), Wiley Cloudflare, DataCite found no working paper.
- P-K6-035-a (abstract): "In the past few years, the lean hog and live cattle futures markets have experienced significantly heightened volatility and frequent limit moves. ... we use intraday futures and options data from 2014 to 2019 that allows for a better characterization of market behavior around limit moves. Consistent with microstructure theories, we find that price limits neither reduce volatility nor improve liquidity. Instead, they add to the high uncertainty that precedes the limit move, leading to significantly higher volatility and lower liquidity when trading resumes."
- P-K6-035-b (abstract): "The options‐implied futures price is only a biased, inefficient, and highly noisy estimate of the equilibrium futures price on locked‐limit days."
- Tags: new to the program (limit mechanics in LE/HE; complements K6-002). Intraday-feasible: relevant as a risk state (volatility and illiquidity after a lock releases); Topstep 2%-of-lock rule applies. Magnitudes [unverified].
- Clusters tagged: K6.

### K6-036 (container 3)
- Citation: Fontinelle, G.B. and Janzen, J.P. (2020). "Ex-ante and Ex-post Effects of Price Limits in Commodity Futures Markets." NCCC-134 2020; AgEcon 10.22004/ag.econ.309645.
- Retrieval: full text, https://web.archive.org/web/20241204124032/https://ageconsearch.umn.edu/record/309645/files/Blair_Janzen_NCCC-134_2020.pdf.
- Mechanism: in wheat futures, tighter limits lower the chance of an extreme move but raise the chance that an extreme move ends at the limit ("magnet"); volume concentrates seconds before a limit hit and collapses at the limit.
- Products and horizon: ZW (Chicago SRW), KC HRW, MGEX spring wheat, Euronext milling wheat; daily and intraday.
- Cost assumptions: none. Data window: January 2007 to April 2019.
- Quality tells: conference paper; the probability effects are tiny in absolute terms.
- Verbatim passages:
  - P-K6-036-a (Abstract): "tighter limit levels decrease the probability of extreme movements by approximately 0.008% having an overall (four markets included) baseline probability of extreme moves equals 1.11% which agrees with the Holding Back hypothesis ... the probability of limit moves conditional to extreme movements increases when limit levels are tighter by approximately 0.066% with an overall baseline of 0.05% which supports the \"Magnet\" hypothesis."
  - P-K6-036-b (Introduction): "Around a limit hit, trading activity shifts concentrating seconds before a limit hit and creating a peak on volume. Seconds before the hit, trading activity tends to reduce drastically surging again if prices return inside the limit bound."
  - P-K6-036-c (Methodology): "we use daily and intraday wheat futures contracts price and volume data from January 2007 to April 2019 for the world wheat futures market complex"
- Numeric claims: P-K6-036-a as quoted (percentages as the authors state them).
- Tags: new to the program (limit magnet). Intraday-feasible: as a risk state only.
- Clusters tagged: K6.

### K6-037 (container 3)
- Citation: Arnade, C., Hoffman, L. and Effland, A. (2021). "The Impact of Public Information on Commodity Market Performance: The Response of Corn Futures to USDA Corn Production Forecasts." USDA Economic Research Service, ERR-293, August 2021. AgEcon 10.22004/ag.econ.313488.
- Retrieval: full text, Wayback copy of the AgEcon PDF (https://web.archive.org/web/20241126074523/https://ageconsearch.umn.edu/record/313488/files/...pdf).
- Mechanism: the WASDE corn production projection moves December corn toward the eventual harvest price and the effect persists for several days (lag dummies for days 2-4); effects differ across open, high, low and close.
- Products and horizon: ZC; daily open, high, low, close, report day plus three days.
- Cost assumptions: none. Data window: 1999-2017 (one table 1992-2017).
- Quality tells: government report; daily OHLC regressions; "lingered" is a regression-dummy result, not a trading test.
- Verbatim passages:
  - P-K6-037-a (Summary): "this study shows the USDA's influence on corn prices remains embodied in corn futures for several days after the release of USDA's WASDE report."
  - P-K6-037-b (Section on release times): "In 1992 and 1993, the WASDE projections—which represent USDA forecasts—were released at 3 p.m. eastern standard time (EST) on the day of release, after the Chicago Board of Trade (CBOT) closed for the day. Starting in 1994, WASDE projections were released at 8:30 a.m. EST in time for the opening of the futures markets. In January 2013, the release time of the WASDE projections was moved to noon EST, which is after the opening of the futures market but leaves time for the report to influence prices during the remainder of the day."
  - P-K6-037-c (Summary): "There were other variables—such as daily lags—which included a second, third, and fourth zero/one variable to test impacts over several days after the report's release."
  - P-K6-037-d (Summary): "data from 1999 to 2017."
- Numeric claims: none transcribed (coefficients not transcribed).
- Tags: port of D.1 family E (post-WASDE multi-day drift). Intraday-feasible: only as day-session exposure on days 1-3 after the release, read from the report; the source does not split open-to-close from overnight.
- Clusters tagged: K6.

### K6-038 to K6-042 (container 4): USDA release times, official pages
All usda.gov, nass.usda.gov, fas.usda.gov and ams.usda.gov hosts returned an Akamai error page to curl from this IP; every passage below was read from a Wayback copy fetched by curl (verbatim text).
Conversion used in the tags: ET minus one hour = CT (both observe daylight time on the same dates). Sessions from the brief: grains day 08:30-13:20 CT, overnight 19:00-07:45 CT, pause 07:45-08:30 CT; livestock 08:30-13:05 CT; program flatten grains 13:18 CT, livestock 13:03 CT.

- K6-038 WASDE page (USDA OCE/WAOB), Wayback 20260912172831 of https://www.usda.gov/about-usda/general-information/staff-offices/office-chief-economist/commodity-markets/wasde-report
  - P-K6-038-a: "2026 WASDE Release Dates (12:00pm ET)"
  - P-K6-038-b: "In 2026 the WASDE report will be released on Jan. 12, Feb. 10, Mar. 10, Apr. 9, May 12, Jun. 11, Jul. 10, Aug. 12, Sep. 11, Oct. 9, Nov. 10, and Dec. 10."
  - CT and session: 11:00 CT, inside the grain day session (and inside the livestock session).
- K6-040 NASS PFEI schedule 2026 (PDF), Wayback 20260826034911 of https://www.nass.usda.gov/Publications/2026-NASS-PFEI-Schedule.pdf (read with pdftotext -raw so the footnote marks stay attached)
  - P-K6-040-a: "CropProduction1 / 12 10 10 9 12 11 10 12 11 9 10 10"; "GrainStocks1 / 12 -- 31 -- -- 30 -- -- 30 -- -- --"; "CattleonFeed2 / 23 20 20 17 22 18 24 21 18 23 20 18"; "HogsandPigs2 / -- -- 26 -- -- 25 -- -- 24 -- -- 23"; "ProspectivePlantings1 / -- -- 31 -- -- 30 -- -- -- -- -- --" (the June 30 entry is the Acreage release; the calendar lists "Acreage and Grain Stocks (June 2026)").
  - P-K6-040-b: "1 / Noonrelease" and "2 / 3pmreleaseunlessindicatedotherwise" (footnotes; the schedule does not repeat the time zone, the NASS calendar in K6-039 states ET).
  - CT and session: Crop Production, Grain Stocks, Prospective Plantings, Acreage at 11:00 CT, inside the grain session. Cattle on Feed and Hogs and Pigs at 14:00 CT, after the 13:05 CT livestock close: effect first tradable at the 08:30 CT open of the next session (Monday after a Friday Cattle on Feed release).
- K6-039 NASS Reports by Date calendar, August 2026, Wayback 20260826034911
  - P-K6-039-a (Mondays): "4:00 pm ET - Crop Progress"
  - P-K6-039-b (Aug 12): "12:00 pm ET - Cotton Ginnings - Crop Production"
  - P-K6-039-c (Aug 21): "3:00 pm ET - Cattle on Feed - Milk Production - Peanut Prices"
  - P-K6-039-d (Aug 24): "3:00 pm ET - Chickens and Eggs - Cold Storage"
  - CT and session: Crop Progress 15:00 CT Monday (after the grain close, before the 19:00 CT evening open; consistent with K6-034's 4:00 p.m. EST in its sample). Cold Storage 14:00 CT, after the livestock close.
- K6-041 FAS Export Sales Reporting Program page, Wayback 20230326201947 (latest capture read; 2026 capture not checked)
  - P-K6-041-a: "FAS publishes a weekly summary of export sales activity every Thursday at 8:30 a.m. ET, unless a change is announced. If the preceding Friday or Monday is a national holiday, the reporting deadline moves to Tuesday and the weekly summary is published Friday."
  - P-K6-041-b: "FAS publishes this information on the subsequent business day at 9 a.m. ET." (daily reports of large sales)
  - CT and session: weekly Export Sales at 07:30 CT, inside the last 15 minutes of the overnight session (which ends 07:45 CT), then the pause; the first day-session trade is 08:30 CT. Daily flash sales at 08:00 CT, inside the pause.
- K6-042 AMS livestock reports (PDFs, closest 2026 Wayback captures of https://www.ams.usda.gov/mnreports/ams_2453.pdf and ams_2675.pdf)
  - P-K6-042-a: "USDA Estimated Boxed Beef Cut-out Values - as of 1:30pm" (LM_XB403, afternoon; time zone not stated in the passage)
  - P-K6-042-b: "(Includes information from 1:30 PM to 1:30 PM.)" (LM_HG217 Daily Direct Afternoon Hog Report; time zone not stated)
  - Session: if these are 13:30 CT, both come after the 13:05 CT livestock close. Morning AMS report times: not retrieved (ams_2452 and ams_2498 not in Wayback) [unverified].
- Tags for all five: port of D.1 family E (event calendar and times). Clusters tagged: K6.

### K6-043 (container 5, found by a Kurov query) ABSTRACT ONLY
- Citation: Zhang, ? (2024). "Trading Activity of Commodity Futures and Options Around USDA Announcements." SSRN working paper, DOI 10.2139/ssrn.4841490.
- Retrieval: abstract only (Crossref record). SSRN abstract page exists in Wayback (2024-06-09); no PDF capture; papers.ssrn.com blocks curl.
- P-K6-043-a (abstract): "We find that the trading volumes of futures and options fluctuate significantly before and after the release of the monthly World Agricultural Supply and Demand Estimates (WASDE) reports for seven agricultural commodities. ... Furthermore, we provide evidence that informed trading exists in commodity markets before the release date. The information contained in the commodity futures and options has a longer predictive horizon for post-announcement futures returns than the ending stocks forecasts in the reports."
- Products, horizon, magnitudes: [unverified] (horizon likely daily).
- Tags: port of D.1 family E (pre-WASDE informed trading). Clusters tagged: K6.

### K6-044 (container 6) ABSTRACT ONLY
- Citation: Mitchell, J.B. (2007). "Soybean Crush Spread Arbitrage: Trading Strategies and Market Efficiency." SSRN working paper, DOI 10.2139/ssrn.987507 (author initials [unverified]).
- Retrieval: abstract only (Crossref). SSRN download link found in a Wayback abstract page (Delivery.cfm/SSRN_ID987507_code251466.pdf), but every Wayback capture of it is HTML (302/400 or interstitial).
- P-K6-044-a (abstract): "This paper revisits the soybean crush spread arbitrage work of Simon (JFM, 1999). Major findings are that contrary to the results reported by Simon, the length of winning and losing trades differ systematically. Winning trades are significantly shorter on average than losing trades. This result leads to trading rules designed to prevent lengthy trades."
- Holding period, costs, data window: [unverified].
- Tags: new to the program (crush reversion, companion to K6-008). Intraday-feasible: unknown. Clusters tagged: K6.

### K6-045 (container 8)
- Citation: Du, X. and Kane, S. (2019). "Fundamental Surprises, Market Structure, and Price Formation in Agricultural Commodity Futures Markets." CFTC OCE working paper, version April 25, 2019.
- Retrieval: full text, https://www.cftc.gov/sites/default/files/2019-05/Du_Kane_Apr%252022_ada.pdf (the listing's triple-encoded link returns 404; the double-encoded one works).
- Mechanism: USDA surprises (announced value minus Bloomberg analyst survey) and the day's transaction shares of trader groups (CFTC confidential data) both explain the day's first-to-last-trade corn and soybean return and realized volatility; directional traders' share pushes price in their direction.
- Products and horizon: ZC, ZS; daily (first to last trade of the day).
- Cost assumptions: none. Data window: December 1, 2011-November 30, 2017 (corn), to October 31, 2017 (soybeans).
- Quality tells: market-structure variables are non-public, so not usable by the program; surprise needs Bloomberg survey data.
- Verbatim passages:
  - P-K6-045-a (Abstract): "Fundamental changes are captured by the deviations of the supply and demand condition estimates released by USDA from the pre-announcement analysts' forecasts published by Bloomberg. We employ the transaction databases of CFTC (Commodity Futures Trading Commission) to construct the percentage shares of detailed participation group trading in the market."
  - P-K6-045-b (Section 4): "we define the daily log price difference as the log difference between the last and the first transaction prices of each trading day over the sample period, which is December 1st, 2011-November 30th, 2017 for corn and December 1st, 2011-October 31, 2017 for soybean."
  - P-K6-045-c (Conclusion): "we find a higher proportion of directional traders in both long and short transactions exert price pressure in the direction of their trades. Also, both the fundamental surprises and other market structure related variables have statistically significant effects on logs price differences and price volatility."
- Numeric claims: none transcribed.
- Tags: port of D.1 family E. Intraday-feasible: the dependent return is first-to-last trade of the day, which includes the overnight session; the day-session part is not separated [unverified]. Clusters tagged: K6.

### K6-047 to K6-051 (container 9): CME Group pages (exchange material; vendor source, no performance claims)
cmegroup.com refuses this IP; all read from Wayback copies by curl.
- K6-047 Price Limits page, Wayback 20260907145625 of https://www.cmegroup.com/trading/price-limits.html, plus "Understanding Price Limits and Circuit Breakers" (Wayback 20260120025249).
  - P-K6-047-a: "For trade date Tuesday, September 8, 2026, price limits for the following agricultural commodities will be:" followed by rows (Commodity, Outrights, Calendar Spreads): "Chicago SRW Wheat, micro and mini-sized Chicago SRW Wheat $0.45 $0.90"; "Corn, micro and mini-sized Corn $0.30 $0.600"; "Lean Hog $0.0425 $0.0850"; "Live Cattle $0.0850 $0.1700"; "Soybean Meal & micro-sized Soybean Meal $20.00 $40.00"; "Soybean Oil & micro-sized Soybean Oil $0.045 $0.090"; "Soybeans, micro and mini-sized Soybeans $0.85 $1.70".
  - P-K6-047-b (Expanded Price Limits table): "Chicago SRW Wheat $0.70"; "Corn $0.45"; "Lean Hog $0.0625"; "Live Cattle $0.1275"; "Soybean Meal $30.00"; "Soybean Oil $0.070"; "Soybeans $1.30".
  - P-K6-047-c (Understanding page): "Some markets may temporarily halt until price limits can be expanded or trading may be stopped for the day based on each exchange's rulebook (grain futures have daily hard limits, for example)."
  - Use: Topstep prohibits "Holding a position within 2% of a product's price lock limit"; these are the lock levels as of September 2026 (they reset in May and November, K6-048).
- K6-048 Grain, Oilseed and Lumber Price Limit FAQ, Wayback 2026 capture of https://www.cmegroup.com/articles/faqs/grain-oilseed-and-lumber-price-limit-faq.html
  - P-K6-048-a: "Twice a year, prior to the resetting of price limits, daily futures settlement prices for each product are collected and averaged over a 45-day period ... The average of those prices is multiplied by a specific percentage to get the effective price limit for the next six months. ... For example, Corn is multiplied by 7%."
  - P-K6-048-b: "Price limits for each product are reset for the first trade date in May and the first trade date in November."
  - P-K6-048-c: "Expanded price limits are approximately 50 percent higher than daily price limits and remain in place until no futures contracts settle at limit. Triggering of expanded limits in one Soybean Complex (Soybean, Soybean Meal, and Soybean Oil) futures triggers expanded limits in the others; triggering of expanded limits in either Chicago Wheat futures or KC HRW Wheat futures triggers expanded limits in the other."
  - P-K6-048-d: "Spot month contracts are not subject to price limits. In Grain and Oilseed contracts, price limits are removed on the business day prior to first notice day of an expiring contract month."
  - Use: K6-002's limit-day events must be re-identified against these variable limits.
- K6-049 "Understanding Major USDA Reports for Grains and Oilseed Markets" (2026), Wayback 20260519194956
  - P-K6-049-a: "The report is released at 11:00 a.m. CT (12:00 p.m. ET) between the 8th and 12th calendar days of each month." (WASDE)
  - P-K6-049-b: "is released at 3:00 p.m. CT (4:00 p.m. ET) on the first business day of each week, April through November." (Crop Progress)
  - P-K6-049-c: "is released on the last business day of January, March, June and September at 11:00 a.m. CT (12:00 p.m. ET)" (Grain Stocks)
  - P-K6-049-d: "Released each Thursday at 7:30 a.m. CT (8:30 a.m. ET) throughout the year, Export Sales covers new sales" 
  - P-K6-049-e: "Each month, industry players submit predictions to be aggregated by business intelligence firms Bloomberg LP and LSEG, with polling medians priced into futures markets by participants trading in anticipation of the number."
  - Agrees with the USDA pages in K6-038 to K6-041 (independent confirmation of the CT times).
- K6-050 Soybean Crush Reference Guide (PDF), Wayback 20260117183628
  - P-K6-050-a: "When a bushel of soybeans weighing 60 pounds is crushed, the typical result is 11 pounds of soybean oil, 44 pounds of 48 percent protein soybean meal, 4 pounds of hulls and 1 pound of waste."
  - P-K6-050-b: "[(Price of Soybean Meal ($/short ton) x .022) + Price of Soybean Oil (¢/lb) x 11] – Price of Soybeans ($/bu.)"
  - Note: K6-001 (1993) used 48 lb of meal per bushel ("11 lbs. of oil and 48 lbs. of meal [USDA (1988)]"); CME now uses 44 lb.
- K6-051 "China's High Demand for Soybeans Fuels Asian Hours Futures Trading" (CME, data to November 2020), Wayback 20260123104844
  - P-K6-051-a: "Based on the latest data for January to November 2020, the total volume of Soybean futures in Asian hours represented about 16 percent of total daily volume, an increase from less than nine percent of total volume in 2011."
  - P-K6-051-b: "Exchange data shows that the spread between the best bid and best offer in Asia specific hours ranged from 1.03 ticks to 1.08 ticks with an average of 1.06 ticks, just shy of the whole day average bid/offer spread, which includes US hours (1.04 ticks)."
  - P-K6-051-c: "Futures trading volumes in Asian hours, defined as 8 a.m. to 8 p.m. Singapore time, are increasing year on year"
  - Use: overnight-session ZS liquidity (a rule may read the overnight session); exchange marketing, January 2021 contract only.
- Tags for all: cost, calendar and limit inputs (D.1 family E; limit state new to the program). Clusters tagged: K6.

## 4. Flags for K8

- CME OpenMarkets 2023, "Are Soybean Oil and Crude Oil Playing a Game of Tag?" | ZL and CL | soybean oil vs crude lead-lag (title only).
- CME Articles 2021, "Energy Demand Revives Soybean Complex Trading Dynamics" | ZS/ZL/ZM and energy | biofuel demand links (title only).
- CME education, "Relationship Between Major Grain Commodity Benchmarks and Equities Prices During Economic Downturns" | ZC/ZS/ZW and equity indices | grains vs equities in downturns (title only).
- JCM 2024 (Cao, Heckelei, Ionici, Robe), "USDA reports affect the stock market, too" | USDA grain reports and equities | one cluster's announcement moving another's product.
- CFTC OCE 2024, "Do Agricultural Swaps Co-Move with Equity Markets? Evidence from the COVID-19 Crisis" | ag swaps and equities | co-movement in crisis.
- CFTC OCE, "Convective Risk Flows in Commodity Futures Markets" | VIX (K1 signal) and commodity futures positions, ags included | risk flows conditioned on VIX, daily.
- Agribusiness 2026 (Zhang), "Spillover Effects of Energy and Grain Futures Volatility: WTI, Natural Gas, and EUA Futures on U.S. Wheat, Corn, and Soybean Markets" | CL/NG and ZC/ZS/ZW | energy-to-grain volatility spillover (title only).
- arXiv 1209.0900 "Time-Frequency Dynamics of Biofuels-Fuels-Food System"; arXiv 1210.6080 "Food for fuel: The price of ethanol" | ethanol/crude and corn | biofuel links (titles only).
- AgEcon 2025 (Avileis, Swanson) EPA/CARB announcements and the soybean complex, logged as K6-032: all legs are K6 products and the event is a regulatory release, so kept in K6; lead may reroute to K8.

## 5. Registry ids appended

- K6-001 .. K6-008 (container 1); K6-009 .. K6-013 (container 2); K6-014 .. K6-037 (container 3; K6-038 .. K6-042 container 4; K6-043 container 5; K6-044 container 6; K6-045, K6-046 container 8; K6-047 .. K6-051 container 9 (K6-046 was claimed before its abstract showed it is crude-only, K4 region; not logged as a K6 source); K6-019 registry line carries the journal name, DOI 10.1016/j.jcomm.2020.100149 resolved afterwards). K6-005 (Martell and Trevino 1990) is a duplicate: K5 had already claimed the same DOI as K5-023; my line was appended before I saw it. Not read by K6 (K5's log reports retrieval failed). Treat K5-023 as the claim.
