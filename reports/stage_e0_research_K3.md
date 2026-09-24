# Stage E.0 research log: Cluster K3 (FX futures)

## 0. Header

- Cluster: K3, CME FX futures. Products: 6A, 6B, 6C, 6E, 6J, 6S, 6M, 6N, E7, M6E, M6A, M6B.
- **This log supersedes the partial run's copy, reports/stage_e0_research_K3_sonnet_partial.md.**
- Lead note received 21:25 PDT: 6M (MXN) is out of the traded universe (D1 liquidity floor). No run-2 full-text read went to an MXN-specific item. K3-043 (EM currencies) is annotated; K3-008's emerging-market results are likewise moot for trading.
- Run 1 (ClusterReader-K3-SonnetMed): 20:38-20:49 PDT per reports/stage_e0_STATE.md. That log's own timestamps (research "20:39-21:38", registry claim times up to 21:38 for K3-006 to K3-015) run past its actual end, so they are not reliable.
- Run 2 (ClusterReader-K3b-OpusHigh): start 20:51 PDT, end 21:24 PDT.
- Stop reason: branch (b) of the stopping rule. Every container now has at least 4 distinct logged queries (both runs together), and its last 2 queries produced no new passing item. Branch (a) was not reached: 24 full-text reads against the 60 cap.
- Tool conditions in run 2, which limited retrieval: Firecrawl had no credits (from 20:52). WebSearch hit the session's 200-call budget at about 21:05. The OpenAlex API ran out of its shared per-IP daily budget at about 21:18. SSRN and ScienceDirect serve captchas to curl; Wiley and cmegroup.com return 403, and cmegroup.com was read only through Wayback copies. After about 21:05, discovery ran on the OpenAlex, Crossref, arXiv and Semantic Scholar APIs and direct curl of site listings, all logged in section 1.
- Counts, both runs:
  - Registry ids K3-001 to K3-045 (45).
  - Passed pre-filter and logged in section 3: 45 ids. Two of them are first-run items reclassified as should-have-been-rejected (K3-012 carry, K3-015 weekly COT). Six are title-only (K3-031, K3-036, K3-037, K3-040, K3-042, K3-043).
  - Full-text reads: 24. Run 1: K3-002, 004, 005, 006, 007, 013, 015. Run 2: K3-001, 003, 016, 017, 018, 019, 020 (Stage 1 protocol only), 021, 022, 023, 024, 032, 033, 038, 039, 044, 045.
  - Abstract-only: 15 (K3-008, 009, 010, 011, 012, 014, 025, 026, 027, 028, 029, 030, 034, 035, 041). Title-only: 6.
  - Rejected at pre-filter: 44 lines in section 2 (R-K3-001 to R-K3-044), with some grouped lines covering several items.
  - Items first flagged abstract-only or blocked in run 1 and upgraded to full text in run 2: K3-001 (Melvin and Prins, found at the ECB workshop) and K3-003 (Evans, found at MPRA).
  - Still abstract-only after run-2 retries: K3-008, 009, 010, 011, 014.
- Panel sources claimed by K3: K3-007 (tagged [K1][K4][K5][K6]), K3-030 ([K1][K2]), K3-035 ([K1][K2][K4]), K3-040 ([K1][K2][K4][K5][K6], title only). Panel sources seen and not re-read: K2-015 (ABDV, claimed by K2) and D.1 A10 (Baltussen et al.).
- First-run blocks re-worked in run 2: K3-001, 002, 003, 004, 005, 007, 011, 012, 014, 015.
  - Changes: citations corrected (K3-002 second author; K3-011 authors; K3-012, 014 and 015 authors).
  - Unsourced CT-time conversions removed from K3-002, 004 and 005; K3-005's conversions also contained arithmetic errors.
  - K3-002's data window and pair count corrected.
  - Missing blocks written for K3-014 and K3-015.
  - K3-012 and K3-015 reclassified as pre-filter failures.
  - K3-010 kept, but its passages are not re-verified: SSRN is blocked and Firecrawl had no credits.
- Registry note: registry line K3-018 names the author as "Panagiotou, K."; the correct authors are Marsh, Panagiotou, Payne (see the K3-018 block). Run 1's log says it "corrected in place" two registry lines (K3-007, K3-009). That was a rewrite of the registry file, which rule 1 forbids; run 2 appended only.

## 1. Container log table

Run-1 queries are listed as that log recorded them. Run-2 queries are in execution order. "New" means a new passing item. Times are PDT.

| # | Container | Queries (run 1) | Queries (run 2, in order, with result) | Run-2 start / pre-filter done / full text done | New passing items, run 2 | Last 2 queries null? |
|---|---|---|---|---|---|---|
| 1 | Journal of Futures Markets and similar journals | 1: "Journal of Futures Markets" currency futures intraday | (1) Cornett Schwarz Szakmary title search: new K3-025; (2) OpenAlex JFM "currency futures intraday": new K3-027, 028, 029; (3) OpenAlex JFM since 1998 "foreign exchange futures": new K3-026, 030 (+ K3-031 by follow-up); (4) OpenAlex JFM "FX futures": null; (5) OpenAlex JFM "exchange rate fixing": null | 21:04 / 21:07 / 21:08 (all JFM items paywalled: abstracts only) | K3-025 to K3-031 | yes |
| 2 | Melvin and Prins 2015 and the WM/Reuters fix literature | 2: Melvin Prins citation search; WM/Reuters fix pre/post-fix reversal | (1) Melvin Prins pdf: null (K3-001 full text found); (2) Evans WMR fix pdf: null (K3-003 full text found); (3) month-end 4pm fix reversal after 2015 reform: new K3-018; (4) Osler Turnbull dealer trading at the fix: new K3-017; (5) Krohn Mueller Whelan fixings around the clock: new K3-016; (6) FCA Fixing the Fix: new K3-019, K3-020; (7) ECB reference rate 14:15 CET intraday: null; (8) WM/Reuters fix CME futures month-end: new K3-021; (9) To fix or not to fix pre-registered: null; (10) Michelberger Witte JFDS: null | 20:52 / 21:01 / 21:01 | K3-016 to K3-021 | yes |
| 3 | Tokyo 9:55 JST fix and gotobi | 1: gotobi days Tokyo fixing | (1) Tokyo fixing 9:55 gotobi academic: new K3-022; (2) Breedon Ranaldo intraday patterns: new K3-023; (3) Japanese importers Tokyo fix month-end: null; (4) gotobi five-ten day 6J out-of-sample: null | 21:02 / 21:03 / 21:03 | K3-022, K3-023 | yes |
| 4 | BIS, Fed, ECB, BoE, FSB | 2: BIS FX microstructure benchmark; FSB FX benchmarks final report | (1) OpenAlex Fed IFDP "foreign exchange intraday": new K3-032, 033; (2) OpenAlex FEDS: null; (3) OpenAlex FEDS Notes: null; (4) OpenAlex NY Fed Staff reports (S4393919745): null; (5) OpenAlex NY Fed Staff Reports (S2764819169): null; (6) OpenAlex BIS Quarterly Review: null | 21:09 / 21:10 / 21:10 | K3-032, K3-033 | yes |
| 5 | Alexander Kurov (panel rule) | 3: Kurov currency futures announcements; Kurov FOMC currency futures; What Chinese macro tells us | (1) OpenAlex author A5060535200 all works, screened: new K3-034, K3-035; (2) OpenAlex "Kurov exchange rate futures announcement": null (0 hits); (3) OpenAlex author Marketa Halova Wolfe: null; (4) OpenAlex since 2010 "currency futures announcement surprise": null | 21:10 / 21:11 / 21:11 (both abstract only) | K3-034, K3-035 | yes |
| 6 | SSRN (Market Microstructure, Derivatives) | 2: currency futures intraday momentum/reversal; carry trade order flow | (1) Ranaldo segmentation time-of-day: new K3-024; (2) OpenAlex SSRN "currency futures intraday": new K3-036, 037; (3) OpenAlex SSRN "FX fixing reversal": null; (4) OpenAlex SSRN "foreign exchange intraday seasonality returns": null | 21:03 / 21:12 / 21:05 | K3-024, K3-036, K3-037 | yes |
| 7 | arXiv q-fin.TR / q-fin.ST | 2: arxiv q-fin currency futures intraday; arxiv currency futures order flow CME | (1) arXiv abs "currency futures": null; (2) arXiv (q-fin.TR or ST) "foreign exchange" + intraday: new K3-038, 039; (3) (q-fin.TR or ST) EURUSD: null; (4) (q-fin.TR or ST) "FX market(s)" + "high-frequency": null | 21:12 / 21:13 / 21:14 | K3-038, K3-039 | yes |
| 8 | CFTC Office of the Chief Economist | 2: CFTC OCE currency futures; CFTC currency futures informed trading | (1) cftc.gov OCE research papers page 0, all titles: null; (2) OCE pages 1-8 FX/intraday title filter: null; (3) cftc.gov site search (3 phrasings): null | 21:11 / 21:12 / 21:12 | none | yes |
| 9 | CME Group research and education (Wayback) | 1: CME FX futures liquidity intraday session E-micro | (1) Wayback economic-research listing: null; (2) Wayback markets/fx.html listing and FX Markers article: null (documentation); (3) Wayback case study on the WM/R 4pm fix (FX BTIC): null (documentation) | 21:14 / 21:15 / 21:15 | none | yes |
| 10 | Databento blog | 1: Databento blog FX futures | (1) blog main listing: null; (2) blog/learning: null; (3) microstructure glossary index: null; (4) FX-term scan of 3 posts: null | 21:15 / 21:16 / 21:16 | none | yes |
| 11 | Quantpedia (to primary papers) | 2: Quantpedia currency futures IMM roll month-end; Quantpedia FX opening range breakout | (1) quantpedia.com site search (3 phrasings; JS-rendered, no results): null; (2) WP sitemaps, 3,170 URLs filtered: candidate titles only, and strategy pages return HTTP 500; (3) Crossref "overnight intraday reversal currency futures": new K3-040; (4) Crossref "intraday reversal currency markets": new K3-041, 042, 043; (5) Quantpedia blog on FX daily volatility and time of day: null; (6) Quantpedia blog on BoE/BoJ/SNB pre-announcement drift: null | 21:16 / 21:19 / 21:19 | K3-040 to K3-043 | yes |
| 12 | Practitioner blogs (discovery only) | 1: jonathankinlay.com currency futures | (1) Carver qoppac search FX: null; (2) Carver search currency: null; (3) Robot Wealth ?s=fx and ?s=currency: null; (4) Robot Wealth asset-class and strategy indexes, FX section: null (paywalled course content); (5) Quantocracy ?s=currency: new K3-044, 045 (via the Aligrithm post, then arXiv); (6) Quantocracy ?s=forex: null; (7) Quantocracy ?s=fx fix: null; (8) Quantitative Brokers blog listing: null; (9) Kinlay ?s=currency: null; (10) Kinlay ?s=forex: null | 21:20 / 21:23 / 21:23 | K3-044, K3-045 | yes |

Totals across both runs: container 1, 6 queries; 2, 12; 3, 5; 4, 8; 5, 7; 6, 6; 7, 6; 8, 5; 9, 4; 10, 5; 11, 8; 12, 11.

## 2. Rejected items

Run-1 rejections (kept; R-K3-001 revised):
- R-K3-001 | run 1 | mirrors of Melvin and Prins working-paper drafts | superseded: run 2 found and read the full working paper (K3-001).
- R-K3-002 | run 1 | Titan FX "Gotobi (Five-Ten Days)" page | practitioner restatement, no primary data.
- R-K3-003 | run 1 | ForexDetox Substack, Tokyo fix reversal on gotobi days | practitioner blog.
- R-K3-004 | run 1 | Alpha in Academia gotobi backtest | practitioner newsletter; same mechanism as K3-005 and K3-022.
- R-K3-005 | run 1 | EBC, YuRa Trading and ForexFactory gotobi posts | retail restatements.
- R-K3-006 | run 1 | BIS 2025 triennial survey commentary | turnover statistics, no intraday mechanism.
- R-K3-007 | run 1 | Takahashi (2025) arXiv 2508.06788 | E-mini S&P only, no FX leg.
- R-K3-008 | run 1 | CME Euro FX overview, Micro FX page, E-micro sell sheet | product documentation.
- R-K3-009 | run 1 | Quantpedia "FX Carry Trade" | multi-day holding.
- R-K3-010 | run 1 | Kinlay "Bond Futures Archives" | FX mentioned only in passing.
- R-K3-011 | run 1 | spot-FX robustness note inside K3-007 | not a separate source.
- R-K3-012 | run 1 (left open) and run 2 | "Is Trend Still Your Friend" trend-following panel on arXiv | trend-following across futures with multi-day holding; not intraday on its face. Rejected in run 2 on the run-1 title and lede; not fetched.

Run-2 rejections:
- R-K3-013 | C2 query 7 | ECB "Framework for the euro foreign exchange reference rates" and central-bank mirror pages | official documentation, no tested mechanism. The search-result text said the rate is set at 14:15 CET; this was not fetched, so it is [unverified here]. K3-016 states "the 'ECB fix' at 8:15 a.m. ET (2:15 p.m. local time)".
- R-K3-014 | C2 query 8, C9 query 3 | CME case study "Asset managers' exposure to the WM/Refinitiv 4:00 p.m. fixing rate" (Wayback raw HTML) | product documentation for FX BTIC, no tested mechanism. Verbatim fact: "The use of FX Basis Trade at Index Close (BTIC) to accurately manage and hedge exposure to the WMR 4:00 p.m. benchmark rate; a true bridge between the printed rate in the OTC market and the cleared, regulated FX futures order book." So month-end fix flow can route into CME FX futures.
- R-K3-015 | C9 query 2 | CME "FX Markers: Price Reference Points for Global Currency Exposure" (2026, Wayback raw HTML) | product documentation. Official times stated verbatim: "Daily Settlement 2:00 p.m. Central Time"; "FX markers are calculated at different times—specifically, at 16:00 London or New York time or 15:00 Tokyo time"; VWAP "over a 30-second time span (e.g., from 15:59:30 to 16:00:00 p.m. London/New York time)".
- R-K3-016 | C1 query 3 | Ding (1999) JFM, determinants of bid-ask spreads in FX futures | spread determinants; no return mechanism.
- R-K3-017 | C1 query 3 | Ferguson, Mann, Schneck (1998) JFM, concentrated trading in FX futures | pit-era volume concentration; no return mechanism.
- R-K3-018 | C1 query 3 | Chaboud and LeBaron (2001) JFM, FX volume and Fed intervention | unscheduled intervention; not tradeable in advance.
- R-K3-019 | C1 queries 3-4 | other JFM hits (Taiwan, Korea, S&P options, soybean hedging, Bund tails and so on) | not FX.
- R-K3-020 | C4 query 1 | Wongswan (2005) IFDP, equity indexes and FOMC | equity (K1), not FX.
- R-K3-021 | C4 query 1 | Chaboud, Chernenko, Wright (2007) IFDP, trading activity and exchange rates in EBS data | needs interdealer order-flow data the program cannot observe; the mechanism is a contemporaneous price impact, not a forecast. Judgment made on the title and listing text; not fetched.
- R-K3-022 | C4 queries 4-6 | NY Fed Staff Reports and BIS Quarterly Review hits (reserve shares, CIP deviations, beer pass-through, Chinese deposits, turnover) | no intraday FX mechanism.
- R-K3-023 | C5 query 1 | Kurov co-authored works with no FX leg (E-mini, energy, VIX, tweets, COVID vaccine news) | not K3. "A shot in the arm" (COVID news) covers rates, stocks and commodities, and its events are unscheduled.
- R-K3-024 | C5 query 4 | Délèze and Hussain (2014), jumps in European futures around US news | European-listed futures; the mechanism duplicates K3-032.
- R-K3-025 | C5 query 4 | Gu, Chen, Stan (2022), unemployment-rate announcements | no FX in the title; abstract unavailable.
- R-K3-026 | C6 query 2 | Torul (2026), "Reflex without Persistence: The Dollar's Multi-Day Safe-Haven Reversal" | multi-day horizon.
- R-K3-027 | C6 query 2 | Wehrli, Wheatley, Sornette (2020) Hawkes estimates; Martins et al. (2026) volume-driven time-of-day volatility models; Guloglu and Ekinci (2021) Borsa Istanbul spreads; Ballocchi et al. (1998) Eurofutures | methodology papers or not FX.
- R-K3-028 | C6 query 2 | Peng et al. (2026), forecasting volatility of currencies and oil with brown firms | cross-asset volatility forecasting (equity to FX, oil); flagged for K8, section 4.
- R-K3-029 | C7 query 2 | arXiv 2406.08013 (DRL with positional context), 2410.23294 (Fitted Natural Actor-Critic FX), 2008.09471 (GA-MSSR) | ML and RL method papers; no stated market mechanism.
- R-K3-030 | C7 query 3 | arXiv 1011.6097 (MKL EURUSD forecasting), 2311.02088 (DL on order books with RL), 1703.03195 (colloidal dynamics of EURUSD) | ML method, high-frequency order-book trading (prohibited rate), or a physics analogy.
- R-K3-031 | C7 query 1 | arXiv 2410.08477 (cross-currency basis swaps), 1205.1861, 2609.18157 | not intraday FX.
- R-K3-032 | C8 query 1 | CFTC OCE "Which Witch is Which? Deconstructing the FX Markets Activity" (GFJ 2024) | positioning during COVID stress; no intraday mechanism.
- R-K3-033 | C8 query 1 | CFTC OCE "Retail Traders in Futures Markets" | behavioural description; median holding 4 days.
- R-K3-034 | C8 query 2 | CFTC OCE Haynes and Roberts (2015), "Macro News Announcements and Automated Trading" (PDF lede read) | E-mini S&P and 10-year note only: "the Chicago Mercantile Exchange's E-mini S&P 500 and 10 Year U.S. Treasury Note contracts".
- R-K3-035 | C8 query 2 | CFTC OCE "High-Frequency Trading and Market Quality" (abstract read) | HFT market quality; no FX mechanism.
- R-K3-036 | C10 queries 1-4 | Databento posts (pairs trading = CL/Brent; futures spreads; matching algorithms; colocation) | no FX content.
- R-K3-037 | C11 query 2 | Quantpedia FX strategy pages on carry, value, momentum, PPP, term spread, CDS, Taylor rule, ESG, political risk and other factors (about 60 slugs) | monthly or longer rebalancing; multi-day holding.
- R-K3-038 | C11 query 4 | He (2020), "Jump-Only Momentum and Reversal in Currency Markets" (SSRN 3493732; Crossref abstract) | cross-sectional currency portfolios after jumps; the horizon is not intraday per the abstract.
- R-K3-039 | C11 query 4 | Pasquariello (2001/2010), central bank intervention and intraday price formation | unscheduled intervention.
- R-K3-040 | C11 query 5 | Doman and Doman, "How Does the Daily Volatility of Foreign Exchange Rates Depend on the Time of Day at Which the Daily Returns Are Calculated?" (SSRN 3651344, via the Quantpedia blog) | daily-return volatility estimation for risk management; no intraday trading mechanism.
- R-K3-041 | C11 query 6 | Quantpedia blog on pre-announcement drift for BoE, BoJ and SNB | US equity country ETFs, daily holding.
- R-K3-042 | C12 queries 1-4, 8-10 | Carver posts (statistical estimation), Robot Wealth course pages (FX Intraday Seasonality, Weekend Gap, Squeeze MR: paywalled, no primary paper), Quantitative Brokers posts (no FX), Kinlay posts (HFT stat-arb, crypto, E-mini) | no primary source, not FX, or high-rate trading.
- R-K3-043 | C12 query 6 | EP Chan blog, "FX Order Flow as a Predictor" (curl, text read) | daily order flow predicting the next day's return, on proprietary FXCM data, one year (2017); multi-day holding and data the program cannot get.
- R-K3-044 | C12 query 7 | SR-SV post "U.S. dollar exchange rate before FOMC decisions" | HTTP 403; lead only. Its primary paper was not identified: [unverified].
- Sentiment items: none met in either run.

## 3. Passed items

Retrieval labels used in this log. "PDF (curl + pdftotext)": the PDF was saved to disk by curl and
read with pdftotext; passages are copied from that text (line breaks and hyphenation normalised).
"Wayback raw HTML": the archived HTML page was fetched with curl from web.archive.org and its tags
stripped by a script, no model rendering. "WebFetch rendering, not verbatim": model rendering, used
only to locate text. First-run passages that this run re-checked against a saved copy are marked
"re-verified 2nd run"; those it could not re-check are marked so.

### K3-001
- Citation: Melvin, M., Prins, J. (2015). "Equity hedging and exchange rates at the London 4 p.m. fix." Journal of Financial Markets (2015). The volume and pages are [unverified]: a search summary said "22, 50-72", and the first run said "26" with DOI 10.1016/j.finmar.2015.09.002. A search-result URL gives the ScienceDirect pii S1386418114000779. Working-paper version read: "Equity hedging and exchange rates at the London 4pm Fix", BlackRock, Nov 2013, presented at the ECB Third FX Workshop. One source.
- Retrieval: full text, 2nd run. PDF (curl + pdftotext) from https://www.ecb.europa.eu/events/pdf/conferences/131216/Third_FX_Workshop_MELVIN_PRINS_Equity%20hedging%20and%20exchange%20rates%20Nov%202013.pdf (7,546 words). The first run had not found it.
- Mechanism: international equity managers hedge their currency exposure and resize the hedges at the month-end London 4pm fix. Where the local equity market has risen over the month, a foreign investor holds more of that currency and sells it into the fix, so the currency depreciates in the hour before the month-end fix and partly reverts afterwards. The reversion after the fix is present on all days and is about twice as large at month-end.
- Products and horizon: spot G10 currencies against USD (EUR, JPY, GBP, CAD, AUD, SEK, NOK, CHF, NZD), 5-minute TWAPs. Signal: equity return over the month up to the second-last day. Trade window: 15:00-16:00 GMT on the last day of the month. The reversion regression runs from 16:00 GMT on day t to noon GMT on day t+1.
- Cost assumptions: none; regression study, no trading-cost model.
- Data window: 28 April 2004 to 31 December 2012 (8.66 years). Equity: Datastream Total Market indices. Flows: aggregate NBFI spot and forward buys and sells.
- Quality tells: authors are BlackRock practitioners, so the hedging-flow story comes from inside the industry. The reversion regression has R2 of 1.9%. The authors call the per-hour effect "quite a small effect" before arguing that it is economically meaningful.
- Verified passages:
  - P-K3-001-a (abstract, mechanism): "A key institutional feature of the foreign exchange market, the "London 4pm fix", is used to identify times when hedging trades concentrate. The direction of hedging trades is identified by past equity returns. Equity market appreciation over the month predicts currency depreciation before the end-of-month fix, providing evidence that hedging activity plays a role in exchange rate determination."
  - P-K3-001-b (numeric, section on the end-of-month regression): "The results show that an equity market appreciation over the month predicts a statistically significant depreciation in the currency in the hour leading up to the end of month fix. The implied magnitude is that a 10% equity appreciation leads to 14 basis points of currency depreciation. Though significant, this seems like quite a small effect."
  - P-K3-001-c (numeric, reversion): "the dependent variable is the exchange rate return from 16:00 GMT on day t to noon the next day t+1, and the independent variable is the same return from 15:00 to 16:00 GMT on day t ... The first interesting result to emerge from this analysis is that there is evidence for price reversion after the fix on all days." followed by "The second interesting result is that this reversion effect is two times larger on end-of-month". The pooled equation reads: coefficient -0.339 on r(15:00-16:00) and -0.387 on the end-of-month interaction, R2 1.9%. The minus signs were lost in pdftotext's rendering of the equation, so the signs are inferred from "reversion" [signs unverified].
  - P-K3-001-d (data): "These prices are available starting from April 28, 2004 and end on December 31, 2012 giving us a sample period of 8.66 years."
  - P-K3-001-e (flows): month-end flows "range from 1.39 times the non-month-end flows for New Zealand to 2.36 times the nonmonth-end flows for the Eurozone. All of the countries' ratios are significantly greater than 1 at a 1 percent significance level."
- Numeric claims: a 10% monthly equity outperformance maps to 14 bp of currency depreciation in the pre-fix hour (P-K3-001-b). Reversion coefficient magnitudes 0.339 on all days plus 0.387 at month-end (P-K3-001-c; signs [unverified] from the extracted text). Month-end NBFI flow ratio 1.39x to 2.36x (P-K3-001-e).
- Tags: new to the program; also a port of D.1 family E (month-end calendar). The pre-fix hour leg is intraday-feasible: the source gives it as 15:00-16:00 GMT, and it closes before the flatten. The post-fix reversion as specified (to noon next day) is NOT intraday-feasible as written; a same-day truncation would have to be tested. The source gives no CT times.
- Note on ownership: the signal is a non-US equity-index return, not a CME product traded here. The partition (section 3, K3 region) assigns "month-end fix flows and equity-hedging rebalancing" to K3 by name, so the item is logged here rather than flagged to K8.

### K3-002
- Citation: Ito, T., Yamada, M. (2017). "Did the Reform Fix the London Fix Problem?" NBER Working Paper 23327; published in Journal of International Money and Finance 80 (2018), 75-95 (IDEAS handle jimfin v80y2018 p75-95, seen in a search-result list only). One source. The first run gave the second author as "K. Yamada"; the title page reads "Masahiro Yamada, Hitotsubashi University".
- Retrieval: full text. PDF (curl + pdftotext) from https://www.nber.org/system/files/working_papers/w23327/w23327.pdf. First-run passages a-e re-verified 2nd run (string match on the saved text).
- Mechanism: before the February 2015 reform, rates that trended into the 4pm London fix tended to reverse after the fixing window, more strongly at month-end. After the reform the month-end reversal persists at the longer holding horizon, the one-minute version is gone, and the intra-month contrarian trade loses money after spreads.
- Products and horizon: spot AUD-USD, EUR-GBP, EUR-JPY, EUR-USD, GBP-USD, USD-CAD, USD-CHF and USD-JPY on EBS (eight pairs; the first run listed five). Holding 1, 5 and 15 minutes after the fixing window.
- Cost assumptions: entry and exit at the bid or ask by direction, so the spread is charged: "The profit considers the transaction cost of spreads: when the investment starts from short (long), the triggering price is at the bid (ask) and liquidating price is at the ask (bid)." No commissions.
- Data window: ICAP EBS Level 5 / Level 2, 2 January 2006 to 30 June 2016 (the first run did not have the dates).
- Quality tells: the Table 2 note gives holding times of 15, 5 and 1 minutes, while the text says "1, 5, and 10 minutes": an internal inconsistency. The authors warn that annualising a once-a-month opportunity "exaggerates the magnitude of annualized Sharpe ratio". The post-reform month-end sample is short (about 16 months).
- Verified passages:
  - P-K3-002-a: "The reform was brought about by the discovery of banks colluding before the start of fixing window by sharing information regarding customers' orders."
  - P-K3-002-b (mechanism): "Before the reform, as Evans (2014) pointed, the average price path showed a small reversal after the end of fixing window: the rates tend to drop after rising toward the fix, and tend to rise after dropping towards the fix. The larger reversal is found at the end-of-month trading days than intra-month days."
  - P-K3-002-c: "Table 3 reports the tail probability of pre- and post-fix rate volatility. The value of 0.05 is ..." (re-verified; the first run's longer quotation continues past the saved line and was not re-checked beyond this point).
  - P-K3-002-d: "the fixing time window was widened from 1 minute to 5 minutes" (re-verified). The reform date "Feb 15, 2015" appears in the Table 2 note.
  - P-K3-002-e: "The predictable pattern of price around the fixing can imply a profitable contrarian investment strategy: taking a long (short) position after the end of fixing if the rates fell (rose) towards the fix."
  - P-K3-002-f (post-reform, 2nd run): "After the reform, the end-of-month profitability is still available, consistent with the visual findings in Figure 1. While the profitability of holding one minute is no longer available, the profitability of 15 minutes holding becomes even stronger than before. In the intra-month sample, there are no profitability, the same as before the reform."
  - P-K3-002-g (Table 2, numeric, 2nd run; average profit in bp after spread, holding 15/5/1 min): After Reform, End of month: "EUR/USD ... 1.21 1.32 -1.02", Sharpe "2.28 7.41 -31.1"; "USD/JPY ... 2.39 2.27 -0.511", Sharpe "6.99 8.48 -28.6"; "USD/CHF ... 6.19 -0.0809 -1.45". After Reform, Intra month: "EUR/USD -0.519 -0.395 -0.861"; "USD/JPY -0.501 -0.556 -0.811" (all intra-month cells negative).
- Numeric claims: post-reform month-end contrarian trade after spread, EUR/USD +1.21 bp at 15 minutes and +1.32 bp at 5 minutes, -1.02 bp at 1 minute; USD/JPY +2.39 / +2.27 / -0.511 bp (P-K3-002-g). Intra-month trade is negative after spread in every pair and horizon, before and after the reform (P-K3-002-f, g). Tail-probability benchmark 0.05 (P-K3-002-c).
- Tags: port of D.1 family C (short-horizon reversal) and family E (month-end); new to the program as an FX benchmark event. Intraday-feasible: the trade lasts minutes after the 4pm London fix. The source gives London time only; no CT time is stated.

### K3-003
- Citation: Evans, M.D.D. (2018). "Forex trading and the WMR Fix." Journal of Banking and Finance 87, 233-247. Read version: MPRA Paper 81583, 25 September 2017, marked "(forthcoming, Journal of Banking and Finance)". Same work as SSRN 2487991. One source.
- Retrieval: full text, 2nd run. PDF (curl + pdftotext) from https://mpra.ub.uni-muenchen.de/81583/1/MPRA_paper_81583.pdf (28,082 words). The first run's SSRN route failed on a captcha; the MPRA route had not been tried.
- Mechanism: price changes before and after the 4pm WMR fix are unusually large and negatively serially correlated, especially at month-end. A month-end contrarian trade (go long at 4:00 pm if prices fell into the fix, short if they rose; hold 1, 5 or 15 minutes) earned positive returns net of half-spread costs in most pairs.
- Products and horizon: spot FX, 21 currency pairs, tick data from Gain Capital (Forex.com's parent). Horizon 1-15 minutes after the month-end fix.
- Cost assumptions: entry cost is taken as zero at the fix, and the exit pays half the normal EBS spread from a 2013 sample: "Returns are inclusive of trading costs, computed to be zero at the Fix and one half the average bid-ask spread when the position is closed."
- Data window: "from the start of 2004 until the end of 2013".
- Quality tells: returns are ex-post; the author re-runs the analysis on pre-2010 data and reports an out-of-sample post-2010 average of 3.25%. Assuming zero entry cost at the fix is generous for a futures trader who pays the spread. The data are retail-platform indicative quotes, whose spread "is roughly twice as large as the inside spreads" on interbank venues.
- Verified passages:
  - P-K3-003-a (abstract): "I then compare the model with the empirical behavior of forex prices across 21 currencies over a decade. Contrary to the predictions of the model, forex price changes display extraordinary volatility and negative serial correlation around the Fix."
  - P-K3-003-b (strategy): "a simple end-of-month trading strategy of taking a long (short) position at 4:00 pm if prices fell (rose) towards the Fix should generate positive returns on average."
  - P-K3-003-c (numeric): "the average returns are well over five percent (on an annualized basis) for nine currency pairs at some horizons. The strategies for many currency pairs also appear attractive when judged by the Sharpe Ratios and Drawdown Statistics. The ratios are above one for at least one horizon in 15 of the currency pairs, and over two in eight pairs."
  - P-K3-003-d (numeric, out-of-sample check): "I also calculated the post-2010 returns on the strategy for each currency pair that had the highest Sharpe Ratio in the pre-2010 data. This produced an average return across the currencies of 3.25 percent."
  - P-K3-003-e (exceptions): "the returns are positive for at least one horizon in all but the JPY/USD and USD/GBP."
  - P-K3-003-f (data): "My empirical analysis covers forex trading from the start of 2004 until the end of 2013."
- Numeric claims: annualised Sharpe above 1 for at least one horizon in 15 of 21 pairs and above 2 in 8 (P-K3-003-c). Post-2010 average return 3.25% from pairs selected on pre-2010 data (P-K3-003-d). JPY/USD and USD/GBP negative at every horizon (P-K3-003-e).
- Tags: port of D.1 family C (reversal) and family E (month-end); intraday-feasible, minutes after the 4pm London fix. No CT time is stated by the source.

### K3-004
- Citation: Xu, H., Øwre-Johnsen, M. (2014). "The use of reference rates and their impact on the currency market." Norges Bank Economic Commentaries 8/2014.
- Retrieval: full text. PDF (curl + pdftotext) from https://core.ac.uk/download/250072485.pdf. Passages a, b and d re-verified 2nd run.
- Mechanism: activity and volatility rise around the WM/Reuters 4pm fix and the ECB fix, because clients route rebalancing orders to banks at the fix and banks pre-hedge. Directional drift appears only for NOK ahead of the ECB fix; there is none at the WM fix.
- Products and horizon: spot EURNOK, EURSEK, EURGBP, AUDUSD, NZDUSD, USDCAD; 15-minute bins around the fixes. The source gives the times in CET.
- Cost assumptions: none; descriptive study.
- Data window: 2002-2013 per the first run [the date range was not re-checked against the text in the 2nd run].
- Quality tells: a central-bank commentary rather than a peer-reviewed paper; it reports a null directional result at the WM fix.
- Verified passages:
  - P-K3-004-a: "A study by Melvin and Prins (2010) finds that activity in the currency market is particularly high around the time of the WM fix, especially at the month-end."
  - P-K3-004-b (numeric): "More precisely, the Norwegian krone has gained an average of 0.02 per cent ahead of the ECB fix."
  - P-K3-004-c: "there is also a clear tendency for market activity in all of the currency pairs to increase ahead of the WM fix." (first run; not re-checked 2nd run)
  - P-K3-004-d: "we have not found any significant price changes around the WM fix for either the krone or the other currencies"
- Numeric claims: NOK +0.02% ahead of the ECB fix (P-K3-004-b). The first run's "significant at the 1% level" is [unverified]: no passage was quoted for it.
- Tags: new to the program; a session-clock and fix-time activity pattern (D.1 families A and E). The directional finding is NOK-specific, and NOK is not a CME product in the K3 list. The fixes fall intraday. The source gives CET only; the first run's "07:15 and 10:00 CT" conversion is removed because no source states it.

### K3-005
- Citation: Bessho, H., Sugimoto, T., Suzuki, T. (2023). "Forex Trading Strategy That Might Be Executed Due to the Popularity of Gotobi Anomaly." arXiv:2301.13204 [q-fin.CP]. Affiliations: Ibaraki University, and Gaika ex byGMO (an FX broker).
- Retrieval: full text. PDF (curl + pdftotext) from https://arxiv.org/pdf/2301.13204 (4 pages). Passages re-verified 2nd run; spacing differs ("PF = 2.62").
- Mechanism: on Gotobi days (dates divisible by 5), Japanese importers buy USD at the 9:55 JST TTM fix. Banks buy dollars ahead of the fix, so USD/JPY rises toward 9:55 JST and the move corrects afterwards.
- Products and horizon: spot USD/JPY, 1-minute data (the program's vehicle would be 6J). Leg 1 enters at 3:00 JST (or on a moving-average golden cross between 2:30 and 3:00) and exits at 9:55 JST. Leg 2 is short from just after 9:55 to 12:00 JST.
- Cost assumptions: "we subtracted the bid-ask spread when entering into the market and exiting from the market".
- Data window: 1 January 2018 to 31 December 2020.
- Quality tells: a 4-page conference-style paper. Three years of in-sample data only; no out-of-sample or walk-forward test. N is 65 to 185 trades. The window filter (n = 3) was chosen as "the best" in sample. One author works at an FX broker.
- Verified passages:
  - P-K3-005-a (mechanism): the abstract says "Our previous research has confirmed that the USD/JPY rate tends to rise toward 9:55 every morning in the Gotobi days, which are divisible by five. This is called the Gotobi anomaly."
  - P-K3-005-b (Hypothesis 2): "The mispricing caused by the Gotobi anomaly is immediately corrected, and therefore it is effective to reverse trading positions of buy and sell just after 9:55 when the occurrence of mispricing was comfirmed." and "we verify the profitability of taking a sell position just after 9:55 and closing its position at 12:00."
  - P-K3-005-c (numeric, Figures 4 and 5 captions): Gotobi days: "In using the GC strategy, N = 65, PF = 2.62, PR = 1.11, and W = 0.68. In not using the GC strategy, N = 185, PF = 1.46, PR = 0.94, and W = 0.60." Non-Gotobi days: "In using the GC strategy, N = 69, PF = 0.52, PR = 0.60, and W = 0.46. In not using the GC strategy, N = 185, PF = 0.51, PR = 0.69, and W = 0.41."
  - P-K3-005-d (numeric, Figure 7, first run): "In the days when the Gotobi anomaly occurred, N = 113, PF= 2.09 ..." (N = 113 string re-verified).
- Numeric claims: pre-fix leg profit factor 1.46 on Gotobi days against 0.51 on non-Gotobi days (no filter), and 2.62 against 0.52 with the golden-cross filter (P-K3-005-c). Reversal leg profit factor 2.09 when the anomaly occurred (P-K3-005-d; conditional on an ex-post classification of whether it occurred, a look-ahead flag).
- Tags: new to the program; port of D.1 families E (day of month) and A (fixed clock time). Intraday-feasible in the sense that no position is held past 15:08 CT. The source gives JST times only, which fall in the CME overnight session. The first run's CT conversions contained errors and are removed; converting the times and deciding how the session boundary is treated are left to the lead.

### K3-006
- Citation: Baldwin, H., Lewejohann, S. (2023). "Unique Liquidity, Clear Benefits: Unlocking Asian Hour Trading Potential with CME FX Futures." CME Group article.
- Retrieval: full text. Wayback raw HTML of https://www.cmegroup.com/articles/2023/unlocking-potential-during-asian-trading-hours-with-cme-fx-futures.html (snapshot 2026-05-15). All four first-run passages were re-verified in the 2nd run.
- Mechanism: none is tested. The article describes the liquidity and spread profile of CME G7 FX futures during Asian hours.
- Products and horizon: 6E, 6J, 6A, 6B, 6C, 6N, 6S; the source defines Asian hours as "(00:00 – 09:00a.m. GMT)"; full-year 2022.
- Cost assumptions: not a strategy; the article reports spreads.
- Data window: full-year 2022; volume figure as of 3 July 2023.
- Quality tells: a venue-authored promotional piece, so the numbers are useful but the framing is not independent.
- Verified passages:
  - P-K3-006-a (table row): "EUR/USD 0.60 0.614 79.4 77.3 33,237 12 USD/JPY 1.09 1.08 83.0 82.9 14,979 21 AUD/USD 0.65 0.66 70.5 67.3 7,132 19 GBP/USD 1.14 1.15". The columns are ATOB spread for the whole day and for Asian hours in pips, % of time at the lowest MPI (whole day, Asian hours), ADV in USD millions, and % of ADV in Asian hours.
  - P-K3-006-b: "As of July 3, 2023, an average of over 180,000 G7 futures contracts were traded daily during Asian trading hours, which is more than 20% of the global G7 futures volume, and over 47,000 unique users"
  - P-K3-006-c: "USD/JPY is lowest during Asian trading hours between 1.03 and 1.15 pips."
- Numeric claims: ATOB spreads EUR/USD 0.60 whole day and 0.614 in Asian hours; USD/JPY 1.09 and 1.08; AUD/USD 0.65 and 0.66; GBP/USD 1.14 and 1.15. Share of ADV in Asian hours: 12% EUR/USD, 21% USD/JPY, 19% AUD/USD (P-K3-006-a). Asian-hours volume above 20% of G7 futures volume (P-K3-006-b).
- Tags: a cost and liquidity input rather than a mechanism; relevant to D.1 family A (session clock) for FX. Intraday-feasible (descriptive).

### K3-007 (PANEL SOURCE, rule 3)
- Citation: Baum, C.F., Kurov, A., Wolfe, M.H. (2015). "What do Chinese Macro Announcements Tell Us About the World Economy?" Journal of International Money and Finance (forthcoming at the working-paper date).
- Retrieval: full text. PDF (curl + pdftotext) from https://www.skidmore.edu/economics/documents/WhatDoChineseMacroAnnouncementsTellUsAboutTheWorldEconomy.pdf. First-run passages re-verified 2nd run; Table 3 coefficients added in the 2nd run.
- Mechanism: surprises in Chinese output announcements (PMI, industrial production, GDP) move world futures within a 20-minute window, and the price impact looks permanent. Positive PMI surprises lift the commodity currencies (AUD, NZD, CAD) and lower JPY.
- Products and horizon: CME 6A, 6N, 6C, 6E, 6B, 6J (plus ICE DX). Event window from 10 minutes before to 10 minutes after the release, using 5-minute prices of the nearby contract. The releases fall at US night.
- Cost assumptions: none; event-study regressions.
- Data window: 30 September 2009 to 31 December 2013 (52 months); 35 PMI observations for FX.
- Quality tells: reports a null for consumption news. N = 35 is small. Pre-announcement CARs are said to be "significant in most cases", but the results are "available upon request" and not shown.
- Verified passages:
  - P-K3-007-a (abstract): "All announcements related to Chinese manufacturing and industrial output move stock markets, energy and industrial commodities as well as commodity currencies. News about Chinese domestic consumption leaves most markets unaffected."
  - P-K3-007-b [K3]: "From foreign exchange futures markets, we include the Australian dollar, New Zealand dollar and Canadian dollar, considered commodity currencies ... Also included are the British Pound, Euro and Japanese Yen that, along with the Australian dollar, rank as the four most actively traded currency futures contracts on Globex."
  - P-K3-007-c [K3] (window): "The futures returns used in regression analysis are computed in the event window from 10 minutes before to 10 minutes after the announcement time"
  - P-K3-007-d [K3] (numeric, Table 3, response to a one-standard-deviation PMI surprise, N = 35): "Australian dollar 35 0.12 (0.03)*** 0.410; New Zealand dollar 35 0.09 (0.02)*** 0.313; Canadian dollar 35 0.04 (0.01)*** 0.309; Euro 35 0.03 (0.01)*** 0.171; British Pound 35 0.03 (0.01)*** 0.381; Japanese Yen 35 -0.04 (0.02)** 0.123"
  - P-K3-007-e [K3]: "in the Australian dollar and New Zealand dollar markets, the impact of China's PMI is twice as strong as that of the U.S. PMI."
  - P-K3-007-f [K3] (spot robustness): "We have analyzed the six currencies for which we have intraday spot data (Australian dollar, New Zealand dollar, Canadian dollar, Euro, British Pound and Japanese Yen). The results are similar to the futures markets results"
  - P-K3-007-g [K3] (pre-announcement): "The CARs in the 30-minute window before the official announcement time are significant in most cases. These results are available upon request."
  - P-K3-007-h [K1] [K4] [K5] (Table 3 and text): "a one-standard-deviation PMI positive surprise increases the E-mini S&P 500 futures price by 0.10 percent, with the PMI surprises explaining 45 percent of the price variation in the announcement window. The effect on the crude oil market is also strong with a coefficient of 0.11 ... with coefficient estimates of 0.18 and 0.06 for copper and silver, respectively."
  - P-K3-007-i [K1] (Table 3): "E-mini Nasdaq-100 35 0.10 (0.03)*** 0.463; E-mini Dow 35 0.09 (0.02)*** 0.467; Nikkei 225 (Japan) 35 0.07 (0.05) 0.101"
  - P-K3-007-j [K6] (Table 3 and text): "Cotton 18 0.32 (0.14)** 0.240; Corn 33 0.04 (0.06) 0.013; Wheat 33 0.06 (0.08) 0.019; Soybeans 33 0.06 (0.04) 0.033" and "Agricultural commodities used in the food industry (corn, soybeans and wheat) show no significant reaction to the PMI news."
- Numeric claims: 6A responds +0.12% per one-SD PMI surprise (R2 0.41), 6N +0.09%, 6C +0.04%, 6E +0.03%, 6B +0.03%, 6J -0.04% (P-K3-007-d). The response is permanent rather than drifting (first-run passage "The figure shows that the price impact of the news appears to be permanent", not re-checked 2nd run).
- Tags: new to the program; port of D.1 family E (a scheduled foreign release). The response lies inside a 20-minute window during the CME overnight session. It is a surprise response and needs the consensus forecast as input. Intraday-feasible: no position crosses 15:08 CT.
- Clusters tagged: [K3], [K1] (P-K3-007-h, i), [K4] (crude, P-K3-007-h), [K5] (copper and silver, P-K3-007-h), [K6] (P-K3-007-j).

### K3-008
- Citation: Tse, Y. (2019). "The impact of FOMC announcements on currency futures markets." Applied Economics Letters 26(19), 1590-1596. DOI 10.1080/13504851.2019.1588940.
- Retrieval: abstract only. Verbatim abstract from IDEAS raw HTML (curl, tags stripped): https://ideas.repec.org/a/taf/apeclt/v26y2019i19p1590-1596.html. Failed routes: the Taylor & Francis abstract page (curl returned a 60-character body); the UMSL PDF the search engine offered turned out to be Tse's CV, not the paper; no working-paper version found. Firecrawl had no credits left in this run.
- Mechanism (abstract): FOMC shocks move currency futures of high-yield and emerging-market currencies, on the announcement day and in the three weeks either side.
- Products and horizon: currency futures, developed and emerging, 1994-2017. The horizon is daily and multi-week per the abstract.
- Cost assumptions and data details: [unverified].
- Verified passages:
  - P-K3-008-a (abstract, full): "We examine the impact on developed and emerging markets of the FOMC announcements on currency futures during the period 1994–2017. The effects are significant for high-yielding major currencies and emerging market currencies. Expansionary monetary policy shocks give positive returns, and contractionary shocks give negative returns, not only on the day of announcements but also three weeks before and after the announcements."
- Numeric claims: none beyond the sample years (P-K3-008-a).
- Tags: port of D.1 family E (FOMC). Mostly NOT intraday-feasible: the three-week drift needs multi-day holding. Whether the announcement-day effect is intraday or close-to-close is [unverified]. The only CME emerging-market product in K3 is 6M.

### K3-009
- Citation: Wang, T., Yang, J., Simpson, M.W. (2008). "U.S. Monetary Policy Surprises and Currency Futures Markets: A New Look." The Financial Review 43(4), 509-541. DOI 10.1111/j.1540-6288.2008.00206.x.
- Retrieval: abstract only. Verbatim abstract from IDEAS raw HTML (curl): https://ideas.repec.org/a/bla/finrev/v43y2008i4p509-541.html. Failed routes: the Wiley full text is paywalled (the DOI link was not fetched because Wiley blocks curl); a web search for a working-paper version found none; Firecrawl had no credits left.
- Mechanism (abstract): intraday currency futures react to both the target and the path surprise of the FOMC, briefly, and asymmetrically (hawkish surprises move prices; dovish ones barely do).
- Products, horizon, costs, data window: intraday CME currency futures; other details [unverified].
- Verified passages:
  - P-K3-009-a (abstract): "Intraday currency futures prices react to both surprises in the federal funds target rate (the target factor) and surprises in the anticipated future direction of Federal Reserve monetary policy (the path factor) in similar magnitude, and the reaction is short‐lived. Dollar‐denominated currency futures prices drop significantly in response to positive surprises (i.e., unexpected increases) in the target and path factors, but have generally little response to negative surprises."
- Numeric claims: [unverified].
- Tags: port of D.1 family E (FOMC) on FX futures; intraday-feasible per the abstract ("short-lived").

### K3-010
- Citation: Seeck, L. (2026). "Intraday Momentum in Spot FX and Currency Futures: Signal Persistence, the JPY Amplification Mechanism, and the Cost Barrier to Retail Exploitability." SSRN 7008318 (posted June 2026).
- Retrieval: abstract only, and in this run NOT re-verified. The first run quoted the abstract from the SSRN page (route not recorded). In the 2nd run: curl to SSRN returned the captcha page; WebFetch returned HTTP 403; no Wayback snapshot exists; Firecrawl had no credits left. A web search surfaced the same numbers in a snippet, which is not retrieval. The passages below are therefore first-run text, not checked by this run.
- Mechanism: the sign of the London-open 30-minute return predicts the rest of the day. The paper reports a larger effect in JPY pairs, and every instrument except spot USDJPY fails after costs, including 6J.
- Products and horizon: 6J (Databento M1, 2019-2024) and five spot CFD pairs (Dukascopy M5, 2012-2024); IS 2012-2018, OOS 2019-2024. Holding runs to the end of the day.
- Quality tells: single author, private firm, 11 pages, a recent unrefereed posting; reports its own cost failure.
- Passages (first run, not re-verified): P-K3-010-a: "USDJPY spot is the sole instrument producing a positive cost-adjusted edge (OOS Sortino: +0.748), while four spot pairs and 6J futures fail to clear their respective cost hurdles." P-K3-010-b: "6J futures maintained positive performance (annual Sharpe: +0.383 vs. −0.557)".
- Numeric claims: all [unverified] in this run.
- Tags: port of D.1 family C (opening-window momentum) and family A. Intraday-feasible if the day ends by 15:08 CT; the source's "end of day" definition is unverified. For 6J the result is negative: it fails its cost hurdle.

### K3-011
- Citation: Rentzler, J., Tandon, K., Yu, S. (2006). "Intraday price-reversal patterns in the currency futures market: The impact of the introduction of GLOBEX and the euro." Journal of Futures Markets 26(11), 1089-1130. DOI 10.1002/fut.20226; SSRN 885686. The first run's citation "Yu, S." omitted the first two authors. D.1 lists this article as row C21 (rejected on product scope, not read).
- Retrieval: abstract only. Verbatim abstract from Wayback raw HTML of the SSRN page (snapshot 2021-09-16), and the same abstract from the Montclair Digital Commons page (curl): https://digitalcommons.montclair.edu/acctg-finance-facpubs/71/. Failed routes: SSRN Delivery (captcha HTML); the Montclair page has no full-text file; Wiley is paywalled; academia.edu needs a login (not attempted); Firecrawl had no credits left.
- Mechanism (abstract): after large one-day returns and large opening gaps, seven CME currency futures show intraday reversals, in five of the seven significantly. The pattern fell after GLOBEX (1993-1998) and returned after the euro (1999-2003).
- Products and horizon: seven CME currency futures, 1988-2003; intraday, from the open to the close of the day after a large move or gap.
- Cost assumptions: [unverified].
- Verified passages:
  - P-K3-011-a (abstract, SSRN via Wayback): "This paper assesses the intraday price reversal patterns of seven major currency futures contracts traded on the Chicago Mercantile Exchange over 1988-2003 after one-day returns and opening gaps. We observe significant intraday price reversal patterns in five of the seven currency futures contracts, following large price changes."
  - P-K3-011-b (abstract): "We find that the introduction of the GLOBEX in 1992 significantly reduced pricing errors in currency futures in the second sub-period making the currency futures markets fairly efficient. However, the introduction of the new currency, the Euro, and the disappearance of several European currencies in 1999, resulted in significant price patterns (mostly reversals and some persistence) in most of the currency futures, indicating inefficiencies in the third sub-period."
- Numeric claims: 5 of 7 contracts (P-K3-011-a). Magnitudes [unverified].
- Tags: port of D.1 family C (reversal after large moves or gaps) tested on currency futures; intraday-feasible. The data are old (to 2003), and the pit-session open no longer exists.

### K3-012
- Citation: Breedon, F., Rime, D., Vitale, P. (2015). "Carry Trades, Order Flow and the Forward Bias Puzzle." SSRN 2643531. The first run recorded the authors as "unspecified".
- Retrieval: abstract only. Verbatim from Wayback raw HTML of the SSRN page (snapshot 2025-12-28).
- Status: this item should have been rejected at pre-filter: its horizon is the forward bias and carry, which require multi-day holding. It is kept here only because the first run registered it. No full text was sought.
- P-K3-012-a (abstract): "Using ten years of data on FX order flow we find that more than half of the forward bias is accounted for by order flow --- with the rest being explained by expectational errors. We also find that carry trading increases currency-crash risk in that order flow generates negative skewness in FX returns."
- Tags: NOT intraday-feasible (carry held overnight; partition rule 8 and the K3 "does not read" line).

### K3-013
- Citation: Financial Stability Board (2014). "Foreign Exchange Benchmarks: Final Report." 30 September 2014.
- Retrieval: full text. PDF (curl + pdftotext) from https://www.fsb.org/uploads/r_140930.pdf (42,946 words). First-run passages a, b and d re-verified 2nd run (string match).
- Mechanism: the 4pm fix window produces the day's largest volume spike, but the largest one-minute volatility spike is at the 8:30am ET US data release, and the report also associates elevated volatility with the 10am ET option expiry. The report recommended a 5-minute fix window.
- Products and horizon: major spot pairs; minute-by-minute across the day.
- Cost assumptions: none.
- Data window: pre-reform; exact range [unverified].
- Quality tells: an official regulator report.
- Verified passages:
  - P-K3-013-a: "... at least 10 times greater ..." (re-verified string; the full sentence is as quoted in the partial-run copy).
  - P-K3-013-b: "the highest average volatility experienced during the day in a 1 minute trading window is associated with the 8:30am ET North American data release" (re-verified).
  - P-K3-013-d: "... over 10% of the platform's daily trading volume." (re-verified string)
- Numeric claims: fix volume spike at least 10 times the average (P-K3-013-a); the fix minute exceeds 10% of platform daily volume on some days (P-K3-013-d).
- Tags: session clock for FX (D.1 family A) and fix (family E); intraday-feasible. ET times are stated by the source.

### K3-014
- Citation: Park, Y.-H. (2022). "Informed trading in foreign exchange futures: Payroll news timing." Journal of Banking & Finance 135, 106372. DOI 10.1016/j.jbankfin.2021.106372; SSRN 3983210. The first run recorded the author as "unspecified" and wrote no block for this item.
- Retrieval: abstract only. Verbatim abstract from IDEAS raw HTML (curl): https://ideas.repec.org/a/eee/jbfina/v135y2022ics037842662100323x.html. Failed routes: ScienceDirect (Firecrawl had no credits left; the journal is subscriber-only per IDEAS); SSRN Delivery (captcha); no Wayback snapshot of the SSRN page; the author's Google Site links only to ScienceDirect and SSRN.
- Mechanism (abstract): speculators position in FX futures ahead of payroll news, and their exposures carry information.
- P-K3-014-a (abstract): "I find that speculators such as hedge funds are more likely to be sellers than buyers of FX futures ahead of good U.S. payroll news and thus appear to have earned significant gains around payroll announcements. ... I show that mimicking speculators' FX exposures around payroll announcements can add a large economic gain to various reference portfolios. My analysis also uncovers that information in FX trading is long-lived"
- Tags: port of D.1 family E (NFP). Horizon [unverified]. The positioning data are most likely the CFTC weekly trader reports (not confirmed from the text), and "long-lived" information points to multi-day holding: probably NOT intraday-feasible as a strategy. A rule could still read the latest positioning as a daily input [inference, not a source claim].

### K3-015
- Citation: Tornell, A., Yuan, C. (2009). "Speculation and Hedging in the Currency Futures Markets: Are They Informative to the Spot Exchange Rates." UMBC Economics working paper 09-116. The first run recorded the authors as "unspecified" and wrote no block.
- Retrieval: full text (PDF, curl + pdftotext) from https://economics.umbc.edu/files/2014/09/wp_09_116.pdf. Read in the 2nd run only to the point of checking the horizon.
- Status: should have been rejected at pre-filter. It uses weekly CFTC Commitments of Traders positions to forecast spot rates over weeks.
- P-K3-015-a (abstract): "We find that the peaks and troughs of net positions are generally useful predictors to the evolution of spot exchange rates but other trader position measures are less correlated with future market movements. In addition, speculative position measures usually forecast price-continuations in spot rates while hedging position measures forecast price-reversals in these markets."
- P-K3-015-b (data): "The currency futures trader positions data used for our analysis are extracted from the Commitments of Traders (COT) reports distributed by the Commodity Futures Trading Commission (CFTC)."
- Tags: NOT intraday-feasible (weekly signal, multi-week horizon).

<!-- NEW ITEMS BELOW -->

### K3-016
- Citation: Krohn, I., Mueller, P., Whelan, P. (2024). "Foreign Exchange Fixings and Returns around the Clock." Journal of Finance 79(1), 541-578, DOI 10.1111/jofi.13306. Read version: working paper dated June 2020. One source.
- Retrieval: full text. PDF (curl + pdftotext) from https://sites.insead.edu/facultyresearch/research/file.cfm?fid=66802 (18,222 words).
- Mechanism: dealers meet an unconditional demand for USD at the three major fixes (Tokyo 9:55 JST, ECB 14:15 CET, London 16:00). The dollar appreciates into each fix and depreciates after it, tracing a W shape over the 24-hour day. The authors link it to dealers' inventory risk.
- Products and horizon: G9 currencies against USD, spot (TRTH, Reuters D5). CME futures for EUR, GBP and JPY are used as a robustness check (the trading test covers January 2009 to December 2018). The windows are stated in ET. Tokyo: long USD 5:00 pm-8:55 pm ET, short 8:55 pm-2:00 am ET. ECB: long 2:00 am-8:15 am, short 8:15 am-5:00 pm. London: long 2:00 am-11:00 am, short 11:00 am-5:00 pm ET.
- Cost assumptions: for spot, indicative bid-ask at 100%, 50% and 0%; for CME, the full bid-ask from firm CME quotes.
- Data window: January 1999 to December 2018 (spot); CME, 2009-2018 (2,515 daily observations).
- Quality tells: published in the Journal of Finance. The text says the CME euro ECB-fix trade has a Sharpe ratio of 0.61, while Table 8 reports 0.65 for the pre/post-ECB cell: an internal inconsistency. Gross returns look large, but after full spread costs most spot windows turn negative. The authors themselves conclude "it is not obvious that this can be exploited by the average trader."
- Verified passages:
  - P-K3-016-a (abstract): "intraday currency returns display prolonged reversals around the major benchmark fixings, characterised by an appreciation of the U.S. dollar pre-fixing and a depreciation thereafter. Moreover, they are a systematic feature of the data being present every day of the week, month of the year, and during each of the twenty years in our sample."
  - P-K3-016-b (numeric, introduction): "in the run up to the Tokyo fix the DOL appreciates by ∼5.3% per annum (2.1 bps per day) with a t-statistic of ∼12.0. Immediately after the Tokyo fix the price path of the DOL reverses, depreciating by ∼5.5% per annum (2.2 bps per day) with a t-statistic of ∼9.2." and "the DOL, again, appreciates by ∼4.3% per annum (1.7 bps per day) with a t-statistic of ∼4.1 until the London fix, after which the DOL reverses, depreciating until New York close by ∼4.8% per annum (1.9 bps per day) with a t-statistic of ∼5.5."
  - P-K3-016-c (timing, source-stated): "at 9:55 a.m. local time which is 8:55 p.m. ET (or 7:55 p.m. depending on daylight saving time (DST))"; "the 'ECB fix' at 8:15 a.m. ET (2:15 p.m. local time)"; "the London fix at 4:00 p.m. local time (or 11:00 a.m. ET)".
  - P-K3-016-d (strategy windows): "For the Tokyo fix we take long dollar positions between 5:00 p.m. and 8:55 p.m. and short dollar positions between 8:55 p.m. and 2:00 a.m. For the ECB fix we go long the dollar between 2:00 a.m. and 8:15 a.m. and short the U.S. dollar between 8:15 a.m. and 5:00 p.m. Finally, for the London fix we long the dollar between 2:00 a.m. and 11:00 a.m. and short the dollar between 11:00 a.m. and 5:00 p.m."
  - P-K3-016-e (CME test, numeric): "we repeat the same exercise and implement the trading strategy in FX futures markets. As the reported prices refer to firm quotes, we only consider the case with full transaction costs that are derived from bid and ask prices recorded on the CME platform. ... While returns and Sharpe ratios are negative for the pound and the yen, after accounting for the full spread returns for trading the euro are extremely large and generate a Sharpe ratio for the ECB fix trade of 0.61"
  - P-K3-016-f (Table 8, BA100% CME row, annualised % return, then Sharpe; columns pre-E, post-E, pre/post-E, pre-L, post-L, pre/post-L, pre-T, post-T, pre/post-T): returns "5.53 0.58 6.11 0.06 -4.89 -4.83 -11.23 2.41 -8.82"; Sharpe "0.99 0.08 0.65 0.01 -0.99 -0.51 -2.25 0.52 -1.27".
  - P-K3-016-g (spot with full cost, Table 8 BA100% row, returns): "0.04 -0.59 -0.55 -1.92 -0.82 -2.74 -4.91 -1.22 -6.13".
  - P-K3-016-h (authors' conclusion): "while there is strong intraday predictability around the fixings, it is not obvious that this can be exploited by the average trader. First, returns from trading a relatively small window around the fix are usually more than offset by transaction costs."
- Numeric claims: t-statistics of about 12.0 and 9.2 for the pre- and post-Tokyo dollar moves, and about 4.1 and 5.5 for pre- and post-London (P-K3-016-b). CME 6E around the ECB fix after full spread: +6.11% a year, Sharpe 0.65 in the table (0.61 in the text). The pre-ECB leg alone gives +5.53%, Sharpe 0.99. CME 6B around London: -4.83%. CME 6J around Tokyo: -8.82% (P-K3-016-e, f).
- Tags: new to the program; also a port of D.1 family A (session clock) and family E. The CME test is on the program's own products. The ECB and London legs run to 5:00 pm ET, which the source states; that is later than 15:08 CT, so the XFA version must truncate the post-fix leg. The Tokyo leg (source-stated 5:00 pm to 2:00 am ET) lies in the CME overnight session and does not cross 15:08 CT. How the session boundary is treated is the lead's decision.

### K3-017
- Citation: Osler, C., Turnbull, A. (2017). "Dealer Trading at the Fix." Brandeis University IBS Working Paper 101R; SSRN 4781675. One source.
- Retrieval: full text. PDF (curl + pdftotext) from https://www.brandeis.edu/economics/RePEc/brd/doc/Brandeis_WP101R.pdf (18,566 words).
- Mechanism: a model of fix dealers. Pre-fix volatility and post-fix retracements arise even without collusion, because dealers with fix-order information front-run one another and proprietary positions unwind after the fix. After the 2015 reforms, non-dealers can infer fix-order direction from the price trend just after 3:45 pm London and copy the informed strategy.
- Products and horizon: spot EUR, JPY, GBP, CHF, CAD, NZD, DKK against USD, 1996-2013; minutes around 4pm London.
- Cost assumptions: none; a model plus statistical tests of the convexity of the pre-fix path.
- Data window: 1996-2013.
- Quality tells: mainly theory. The empirical part tests convexity, not profitability. The claim that the dynamics persisted after the reform rests on other papers (Ito and Yamada; van der Linden).
- Verified passages:
  - P-K3-017-a (abstract): "Fix prices will be unusually volatile without collusion. Collusion is profitable because it shuts down a form of free-riding in which dealers front-run each other. The price trend accelerates more as the fix approaches under collusion than under independent trading."
  - P-K3-017-b (post-reform mechanism): "non-dealers can now glean information about fix orders from the price trend immediately following 3:45, given the dealers' reliance on execution algorithms. Non-dealers with that information can adopt the optimal strategy identified by the model for an informed dealer: front-run the rest of the market by opening a speculative position immediately after 3:45 and then liquidate that position partly before and partly after the fix."
  - P-K3-017-c (data): "apply it to high-frequency exchange-rate data covering the years 1996 through 2013 for seven major currencies vis-à-vis the US dollar: EUR, JPY, GBP, CHF, CAD, NZD, and DKK."
- Numeric claims: none on returns.
- Tags: new to the program. It adds a trend-following entry at 3:45 pm London into the fix, the counterpart of the reversal after it (D.1 family C: momentum into the fix, reversal after). Intraday-feasible. The source states London time only.

### K3-018
- Citation: Marsh, I.W., Panagiotou, P., Payne, R. (2017). "The WMR Fix and its Impact on Currency Markets." Working paper, 29 September 2017, marked "Preliminary and Incomplete"; hosted by Norges Bank as conference paper no. 39. The registry line K3-018 names "Panagiotou, K." as author, which is wrong: the title page lists Marsh, Panagiotou and Payne.
- Retrieval: full text. PDF (curl + pdftotext) from https://www.norges-bank.no/contentassets/619c8b75e1ed4ba691e8ad6a006855e6/39-panagiotou---the-wmr-fix-and-its-impact-on-currency-markets-.pdf (15,497 words).
- Mechanism: inside the one-minute fix window, interbank order flow has no price impact and spreads are narrow, so dealers cheaply unwind excess positions built before the fix. Price discovery moves to CME futures at the fix, and positions built in futures before the fix reverse over a longer interval.
- Products and horizon: spot GBP/USD, AUD/USD, NZD/USD (Reuters Dealing) and the matching CME futures (6B, 6A, 6N; nearest contract, TRTH). 1-minute bars, London hours 08:00-17:00.
- Cost assumptions: none; a flow and returns study.
- Data window: 1 January 2010 to 31 December 2013 (pre-reform, 1-minute fix window).
- Quality tells: marked "Preliminary and Incomplete"; four years of data, all before the reform.
- Verified passages:
  - P-K3-018-a (findings): "(2) There is a small price reversal in the one minute after the 4pm Fix for both markets that is not observed at other fixing points. ... (5) Price discovery temporarily migrates from the spot to futures markets at the Fix since futures order flow maintains price impact. (6) Positions accumulated in the futures market during the pre-Fix are also reversed, though over a significantly longer time interval than in the spot market probably due to the more consistent price impact seen in the futures market. This reversal of futures positions is common across all 'extreme' intervals in the trading day."
  - P-K3-018-b (futures data): "The futures database consists trade and quote activity on GBP/USD, AUD/USD and NZD/USD futures contracts listed on the Chicago Mercantile Exchange collected from Thomson Reuters Tick History. We focus on the contract closest to maturity."
  - P-K3-018-c (data window): "Our spot data include all GBP/USD, AUD/USD and NZD/USD transactions between January 1, 2010 and December 31, 2013 on the Reuters Dealing electronic inter-dealer trading system."
- Numeric claims: none extracted (reversal magnitudes are not stated in the summary passage).
- Tags: new to the program; port of D.1 family C (reversal after extreme-flow intervals) tested on CME 6B, 6A and 6N. Intraday-feasible. The source states London time only.

### K3-019
- Citation: Evans, M.D.D., O'Neill, P., Rime, D., Saakvitne, J. (2018). "Fixing the Fix? Assessing the Effectiveness of the 4pm Fix." FCA Occasional Paper 46, October 2018; SSRN 3270844. One source.
- Retrieval: full text. PDF (curl + pdftotext) from https://www.fca.org.uk/publication/occasional-papers/occasional-paper-46.pdf (32,508 words). Process note: the PDF was fetched a minute before the registry claim line was appended. The registry had no match, so nothing was read twice.
- Mechanism: the study measures whether the fix-reversal inefficiency survived the 2015 lengthening of the window to 5 minutes. The correlation between the fix-window return and the return over the 15 minutes after is negative and significant in most quarters of 2012-2014, and generally insignificant from 2015 on. In other words, the regulator's own data show the post-fix reversal gone after 2015.
- Products and horizon: spot AUDUSD, EURHUF, EURSEK, EURUSD, GBPUSD on Thomson Reuters Matching, with trader-identified order-book data; horizon of 15 minutes before and after the fix.
- Cost assumptions: none (efficiency and liquidity measures). The paper reports that direct trading costs at the fix fell 5-10% relative to other times.
- Data window: 28 October 2010 to 5 June 2015, and 15 January 2017 to 14 June 2017. 2016 is excluded.
- Quality tells: a regulator's dataset with trader identities. It uses a correlation test, not a trading backtest. Its post-reform sample is only six months (2017), shorter than Ito and Yamada's (K3-002). Its finding conflicts with K3-002, whose post-reform month-end trade stays profitable. The two pool different days: this paper pools all days by quarter, while K3-002 splits out month-end. The conflict is left for the CatalogWriter to weigh.
- Verified passages:
  - P-K3-019-a (summary): "We find that short-term price reversals in prices around the fix decrease steadily throughout our sample period, and disappear from 2015 onwards. This coincided with changes in trading behaviour of several types of market participants — dealer banks began doing relatively less trading before the fix and more during the fix, the total trading volume of dealers that were subsequently fined for rigging decreased by one fifth, and direct trading costs in the largest currencies in our sample decreased by 5 to 10% relative to other times of the day."
  - P-K3-019-b (method and result): "let v1, v2, v3 denote the market-wide VWAPs in the 15 minutes before the fix, during the fix, and the 15 minutes after the fix ... We find a negative and statistical significant correlation coefficient r for most quarters in the period 2012 to 2014. There is a visible change around the time the fix window was lengthened (the first quarter of 2015), and from 2015 onwards the correlations are generally insignificant."
  - P-K3-019-c (data): "Our sample period is approximately two and a half years from the 28 October 2010, to the 5 June 2015, and around 6 months from the 15 January 2017 to the 14 June 2017." and "The currency pairs in our sample are AUDUSD, EURHUF, EURSEK, EURUSD and GBPUSD."
- Numeric claims: dealers later fined cut their fix volume by one fifth; direct trading costs at the fix fell 5-10% (P-K3-019-a). The correlation values are shown only in a figure (Figure 1.4) and were not extracted [unverified].
- Tags: evidence AGAINST the post-fix reversal (D.1 family C) after 2015, on all days pooled. Intraday horizon. Reported because the brief asks for non-survivors.

### K3-020
- Citation: Benenchia, M., Galati, L., Lepone, A. (2024). "To fix or not to fix: The representativeness of the WM/R methodology that underpins the FX benchmark rates. A pre-registered report." Pacific-Basin Finance Journal 84, 102311 (Stage 1, protocol). Stage 2 results: same authors (per the search listing; not confirmed from text), "To fix or not to fix, the Fix: Reassessing the effectiveness of the 4 pm Fix. A pre-registered study." Pacific-Basin Finance Journal 93 (2025), 102652, DOI 10.1016/j.pacfin.2024.102652. Registered together under K3-020.
- Retrieval: Stage 1 full text, PDF (curl + pdftotext) from https://iris.unitn.it/bitstream/11572/404030/2/1-s2.0-S0927538X24000623-main.pdf (10,906 words). Stage 2: abstract only, from the Macquarie research portal raw HTML (curl): https://researchers.mq.edu.au/en/publications/to-fix-or-not-to-fix-the-fix-reassessing-the-effectiveness-of-the/. Failed routes for the Stage 2 PDF: the Macquarie file link (Cloudflare 403), ScienceDirect (captcha, and WebFetch 403), a pdf.sciencedirectassets guess (HTML), no Wayback snapshot, a Trento IRIS search (no Stage 2 record found), and Firecrawl (no credits left).
- Mechanism: the study is a pre-registered re-test of the Evans et al. (2018) efficiency measure (K3-019) on 2015-2023 data. The Stage 1 protocol commits to a quarterly correlation test of short-term reversals around the 4 pm fix. The Stage 2 abstract does not report the reversal result.
- Products and horizon: GBP/USD, EUR/USD, CAD/USD, AUD/USD, NZD/USD, JPY/USD and further Asia-Pacific pairs (Stage 1, section on the unit of analysis); 15 minutes before and after the fix.
- Data window: "from February 15, 2015 ... to the end of 2023" (Stage 1).
- Quality tells: pre-registered, which is the strongest design seen in K3. But the one result that matters here (the post-2015 reversal correlation) is not in the retrieved text.
- Verified passages:
  - P-K3-020-a (Stage 1, method): "Consistent with Evans et al. (2018), we also compute a measure of market efficiency by examining price dynamics around the benchmark window through a correlation analysis of short-term reversals ... where p1, p2, and p3 are the market-wide average prices in the 15 min before the fix, during the fix, and the 15 min after the fix, respectively. We undertake t-tests on whether the correlation in each quarter of our sample period is equal to zero".
  - P-K3-020-b (Stage 1, data): "The sample period available for the analysis covers over 9 years, from February 15, 2015, the day in which the current methodology became effective, to the end of 2023."
  - P-K3-020-c (Stage 2 abstract): "Findings indicate that while limited improvements in robustness can be achieved with longer windows, the current 5-min window remains broadly effective."
- Numeric claims: none. The Stage 2 reversal result is [unverified]; its full text was not retrieved.
- Tags: the reversal test is intraday, a port of D.1 family C. Pending the Stage 2 full text, which would be the most recent out-of-sample check on post-reform reversals.

### K3-021
- Citation: Michelberger, P.S., Witte, J.H. (2016). "Foreign exchange market microstructure and the WM/Reuters 4 pm fix." Journal of Finance and Data Science; arXiv:1501.07778 (v2, 29 Feb 2016, marked "To be published in: The Journal of Finance and Data Science"). One source.
- Retrieval: full text. PDF (curl + pdftotext) from https://arxiv.org/pdf/1501.07778 (14,729 words).
- Mechanism: volatility and the probability of the day's extreme price clustering both spike in the minute before the 4pm fix. A second, consistent volatility cluster falls at 15:00-15:02 London, which the authors tie to US data releases and the 10am EST FX option expiry. The authors are practitioners at Record Currency Management, and they argue the fix hurts the clients who use it.
- Products and horizon: 12 spot pairs (EURUSD, USDJPY, EURJPY, EURGBP, USDGBP, AUDUSD, EURCHF, USDCHF, GBPCHF, EURSEK, USDMXN, USDSGD); minute bars.
- Cost assumptions: none; volatility and extreme-move study.
- Data window: 01/2010-03/2014 for most pairs; 01/2008-03/2014 for EURSEK, AUDUSD, USDMXN, USDSGD. The data are split at June 2013. All of it predates the reform.
- Quality tells: descriptive, pre-reform only; no trading test.
- Verified passages:
  - P-K3-021-a: "Amongst the consistent extrema are the minutes 15:59-16:00 ... and 16:00-16:01 ..., which are the minutes just before and after the WM/R 4pm fix. Here, particularly the minute leading up to the fix shows a significant increase in volatility compared to the minutes in the ∼ 50-min. beforehand."
  - P-K3-021-b: "A second set of consistently elevated volatility occurs at 15:00-15:01 and 15:01-15:02. This sudden volatility increase happens right after the release of market-relevant information [15] in the US and the expiry of FX options at 10am EST."
  - P-K3-021-c: "there is indeed a significant increase in the probability for spot rate extrema around 4pm, and that the movement sizes are, on average, larger than their comparable counterparts at other hours during the day."
- Numeric claims: none extracted (the magnitudes are in figures).
- Tags: session clock for FX (D.1 family A): the 4pm London minute and the 10am ET option-expiry minute. Also relevant to family D, since the fix sets the day's high or low with raised probability. Intraday. The source states the 10am EST expiry time itself.

### K3-022
- Citation: Ito, T., Yamada, M. (2016). "Puzzles in the Forex Tokyo 'Fixing': Order Imbalances and Biased Pricing by Banks." NBER Working Paper 22820, November 2016. (A published version was not checked.)
- Retrieval: full text. PDF (curl + pdftotext) from https://www.nber.org/system/files/working_papers/w22820/w22820.pdf (15,505 words).
- Mechanism: at the Tokyo fix, customer orders lean predictably toward buying foreign currency (importers), so USD and EUR appreciate against JPY into the fix. The lean is strongest on the 5th, 10th, 15th, 20th, 25th and 30th and at month-end. Unlike London, the Tokyo fix shows no reversal correlation; the edge is a switch from long to short at the fix minute.
- Products and horizon: spot USD/JPY and EUR/JPY on EBS; a 5-minute long before and 5-minute short after the fix. The source gives the fix time as 00:55 GMT.
- Cost assumptions: returns use transaction prices. The authors describe the 1.8 bp as "slightly above the transaction cost from the bid-ask spread"; no explicit cost model.
- Data window: EBS Level 2, January 1999 to December 2005 (USD-JPY); Level 5, January 2006 to December 2013 (eight pairs).
- Quality tells: NBER working paper by the same team as K3-002. It trims the top and bottom 1% of returns. The edge is small, about the size of the spread.
- Verified passages:
  - P-K3-022-a (abstract): "(2) The customer orders are biased toward buying the foreign currencies, which is predictable. ... (5) The calendar effects also matter for determination of the fixing rate and the price fluctuation around fixing time."
  - P-K3-022-b (mechanism): "around the fixing period in the Tokyo market, the buying orders of foreign currency (US dollar and Euro) by importers regularly exceed the selling orders by exporters. It is commonly known that the USD tends to appreciate vis-à-vis the yen around the fixing time. This situation is more evident when large amounts of payments are due, typically on the days of the 5th, 10th, 15th, 20th, 25th, and 30th, (hereafter 5th and 10th days) as well as the end-of-month trading day."
  - P-K3-022-c (numeric): "While return reversals are reported at the London fixing (Melvin and Prins (2015), Evans (2014)), they are not found at the Tokyo fixing (Table 4). ... we calculated the average return of the investment incurred by holding the USD/JPY long for five minutes and then shorting it for the following five minutes. ... For 15 years of this simple strategy, if the switching time is at the moment of the Tokyo fixing (00:55GMT), the average return becomes 1.8bp. This return is slightly above the transaction cost from the bid-ask spread."
  - P-K3-022-d (calendar): "the return becomes particularly high at 5th and 10th days (except for the days close to the end of month), and the 31st day of month or the end of month."
- Numeric claims: a long-5/short-5 minute switch at the Tokyo fix averages 1.8 bp over 15 years, "slightly above" the spread (P-K3-022-c). No reversal correlation at Tokyo (P-K3-022-c).
- Tags: new to the program; port of D.1 families A and E (gotobi days). It corroborates K3-005's mechanism with longer data but a smaller edge. Intraday-feasible: the trade sits in the CME overnight session and does not cross 15:08 CT. The source states 00:55 GMT, not CT.

### K3-023
- Citation: Breedon, F., Ranaldo, A. (2013). "Intraday Patterns in FX Returns and Order Flow." Journal of Money, Credit and Banking 45(5), 953-965. Read version: Swiss National Bank Working Paper 2011-04 (dated November 2010). One source.
- Retrieval: full text. PDF (curl + pdftotext) from https://www.snb.ch/public/asset/en/www-snb-ch/publications/research/working-papers/2011/working_paper_2011_04/publications0_en/working_paper_2011_04.n.pdf (7,131 words).
- Mechanism: currencies tend to depreciate during their own local trading hours and appreciate outside them, because local participants are net buyers of foreign exchange in their own hours. The order flow shows the same pattern. For EUR/USD: short EUR in European hours and long EUR in US hours.
- Products and horizon: EBS EUR/USD, USD/JPY, GBP/USD, EUR/JPY, USD/CHF, AUD/USD; hourly bars, session open to close. The source defines sessions by futures-market hours (Table 1): US 08.00-16.00 and Europe 07.00-15.00 local time.
- Cost assumptions: session trades priced at the firm EBS bid and ask.
- Data window: January 1997 to the beginning of June 2007.
- Quality tells: the authors say they made no holiday or other adjustments, to avoid data-mining. The spread pattern between sessions is stable year by year (2004 is the one exception). Only EUR/USD survives costs.
- Verified passages:
  - P-K3-023-a (abstract): "we present evidence of time‐of‐day effects in foreign exchange returns through a significant tendency for currencies to depreciate during local trading hours. We confirm this pattern across a range of currencies and find that, in the case of EUR/USD, it can form a simple, profitable trading strategy."
  - P-K3-023-b (numeric, with costs): "As might be expected, most of these simple time‐of‐day trading strategies are not profitable when trading costs are included. However, the notable exception is EUR/USD where the significant intraday pattern combined with narrow spreads in this cross means that this basic strategy has been profitable on average with Sharpe Ratios of 1.3 and 0.9 respectively for the morning short and afternoon long."
  - P-K3-023-c (stability): "although the returns over each session individually show considerable variation, the difference in returns between the two sessions remains remarkably stable. Only in 2004 do we find marginally higher returns in the EUR session than in the USD session"
  - P-K3-023-d (prior futures evidence, cited): "Cornett et al (1995) studies hourly data for US trading hours of FX futures from the IMM market for the period 1977 to 1991. ... they find a significant tendency for the foreign currency to rise during US trading hours, with the majority of that rise occurring in the first and last two hours of trading."
  - P-K3-023-e (holiday, footnote 6): "the dollar has appreciated against the euro (or DM) over the July 4 Federal holiday on 15 of the last 20 occasions."
- Numeric claims: EUR/USD after costs, Sharpe 1.3 for the European-morning short and 0.9 for the US-afternoon long (P-K3-023-b). July 4: USD up against EUR on 15 of 20 occasions (P-K3-023-e; an anecdote, not a test).
- Tags: new to the program; port of D.1 family A (session clock) applied to FX. Intraday-feasible for 6E: the US-hours long ends at 16:00 New York local time, which is after 15:08 CT, so it would need truncation. The source states local times only.

### K3-024
- Citation: Ranaldo, A. (2009). "Segmentation and time-of-day patterns in foreign exchange markets." Journal of Banking & Finance 33(12), 2199-2206. Read version: Swiss National Bank Working Paper 2007-03. One source.
- Retrieval: full text. PDF (curl + pdftotext) from https://www.snb.ch/public/asset/en/www-snb-ch/publications/research/working-papers/2007/working_paper_2007_03/publications0_en/working_paper_2007_03.n.pdf (13,831 words).
- Mechanism: a currency tends to depreciate during its own working hours and appreciate during the foreign counterpart's. The paper's explanation is domestic-currency bias plus market segmentation, which leave dealer inventory imbalances that swing with the clock. This is the same pattern as K3-023, on a longer sample and with day-of-week variants.
- Products and horizon: spot CHF/USD, DEM/USD, EUR/USD, JPY/EUR, JPY/USD in 4-hour blocks (GMT). The source states the windows: long USD 8:00-12:00 GMT against CHF, DEM and EUR; short USD 12:00-16:00 GMT against CHF, DEM and JPY, and 16:00-20:00 GMT against EUR.
- Cost assumptions: a break-even analysis against Reuters indicative spreads, which the author says overstate interdealer costs.
- Data window: January 1993 to August 2005 (CHF/USD, JPY/USD); January 1999 to August 2005 (EUR/USD, JPY/EUR); DEM/USD 1993-1998.
- Quality tells: the rules deliberately use fixed 4-hour blocks rather than the best windows. The day-of-week variants (Sharpe above 3.5) are chosen after the fact from Table 3 effects, a data-mining flag. The quotes are indicative.
- Verified passages:
  - P-K3-024-a (abstract): "Domestic currencies appreciate (depreciate) systematically during foreign (domestic) working hours. These time-of-day patterns are statistically and economically highly significant. They pervasively persist across many years, even after accounting for calendar effects."
  - P-K3-024-b (numeric): "Long-short strategy performance ranges from 6.7% (JPY/USD) to 16.7% (EUR/USD). These numbers translate into 0.96 and 2.41 in terms of Sharpe ratios. The implementation of day-of-the-week strategies magnifies these yields further. The long-short strategy on Mondays and Thursdays attains almost 20% of annual returns, with a Sharpe ratio of more than 3.5."
  - P-K3-024-c (costs): "it appears that the EUR/USD pair, at least, provides lucrative speculation, even after adjusting for transaction costs. In these cases, time-of-day currency strategies can bear transaction costs as high as 4 pips before moving into a negative range." and "In most cases, break-even costs are between 10 and 19 pips" (day-of-week strategies).
  - P-K3-024-d (windows): "The long position on US dollars is from 8:00 to noon if the counterpart currency is the Swiss franc, German mark or euro ... The short position on the dollar spans the hours from midday to 16:00 if the counterpart currency is the Swiss franc, German mark or Japanese yen, and from 16:00 to 20:00 for the euro."
- Numeric claims: long-short annualised return 6.7% (JPY/USD) to 16.7% (EUR/USD), Sharpe 0.96 to 2.41, gross (P-K3-024-b). EUR/USD break-even cost of 4 pips (P-K3-024-c).
- Tags: port of D.1 family A (session clock) for FX. Intraday-feasible; the EUR long to 20:00 GMT needs truncation to 15:08 CT. The source states GMT only.

### K3-025
- Citation: Cornett, M.M., Schwarz, T.V., Szakmary, A.C. (1995). "Seasonalities and intraday return patterns in the foreign currency futures market." Journal of Banking & Finance 19(5), 843-869. DOI 10.1016/0378-4266(95)00084-T.
- Retrieval: abstract only. Verbatim abstract from Wayback raw HTML of the ScienceDirect abstract page (snapshot 2024-04-24). Failed routes: ScienceDirect full text (subscriber-only per IDEAS; live page captcha); IDEAS (no abstract); academia.edu (needs a login, not attempted); no working-paper version found. A second-hand description is in K3-023 (P-K3-023-d).
- Mechanism (abstract): on IMM currency futures, foreign currencies strengthen during the US pit session (concentrated in the opening hour and the last two hours) and weaken overnight, netting to insignificant daily returns.
- Products and horizon: IMM currency futures (DM, GBP, CHF, JPY, CAD per P-K3-023-d); hourly, 1977-1991 (per P-K3-023-d).
- Verified passages:
  - P-K3-025-a (abstract): "We find that insignificant daily returns are generally the result of significant negative returns overnight (when measured relative to the dollar) and significant positive returns during the trading day. The strengthening of foreign currencies intraday is concentrated during the opening hour, as well as during the last two hours of the U.S. trading day."
- Numeric claims: [unverified].
- Tags: port of D.1 family A (session clock), tested on CME currency futures themselves. Intraday-feasible. The data are pit-era and old (to 1991); the session hours then differ from Globex today.

### Journal of Futures Markets and Journal of Banking & Finance group (K3-026 to K3-031): paywalled; abstracts only
Common retrieval note: in the 2nd run, WebSearch hit the session's 200-call budget at about 21:05 PDT and Firecrawl had no credits left. Discovery for this group ran on the OpenAlex API (curl, JSON). The abstracts below are OpenAlex's stored abstracts, rebuilt word for word from its inverted index; punctuation is as indexed, and they are otherwise verbatim publisher abstracts. Full-text routes tried for every item: the Wiley PDF and abstract pages (curl, HTTP 403); OpenAlex and Semantic Scholar open-access locations (none open); CiteSeerX (bot page) where OpenAlex listed it. Every numeric claim beyond the abstracts is [unverified].

### K3-026
- Citation: Tse, Y., Xiang, J., Fung, J.K.W. (2006). "Price discovery in the foreign exchange futures market." Journal of Futures Markets 26, 1131-1143. DOI 10.1002/fut.20229.
- Retrieval: abstract only (OpenAlex).
- Mechanism (abstract): price-discovery shares for euro and yen across floor futures, GLOBEX futures and retail online spot. GLOBEX leads in the euro, online spot leads in the yen, and the floor contributes least.
- P-K3-026-a: "GLOBEX electronic futures contracts provide the most price discovery in the euro; the on-line trading spot market provides the most in the Japanese yen. The floor-traded futures markets contribute the least to price discovery in both the euro and the Japanese yen markets. ... Futures traders may also extract information from on-line spot prices."
- Tags: lead-lag between 6E/6J and spot (a K3 region item). Old data. Intraday.

### K3-027
- Citation: Cabrera, J., Wang, T., Yang, J. (2009). "Do futures lead price discovery in electronic foreign exchange markets?" Journal of Futures Markets 29, 137-156. DOI 10.1002/fut.20352; also SSRN 1115056 (2008). One source.
- Retrieval: abstract only (OpenAlex). The CiteSeerX PDF returned a bot page; SSRN is blocked.
- P-K3-027-a: "Using intraday data, this study investigates the contribution to the price discovery of Euro and Japanese Yen exchange rates in three foreign exchange markets based on electronic trading systems: the CME GLOBEX regular futures, E‐mini futures, and the EBS interdealer spot market. Contrary to evidence in equity markets and more recent evidence in foreign exchange markets, the spot market is found to consistently lead the price discovery process for both currencies during the sample period. Furthermore, E‐mini futures do not contribute more to the price discovery than the electronically traded regular futures."
- Tags: lead-lag, spot (EBS) leading 6E and 6J. This conflicts with K3-026 and K3-029 on which market leads. It concerns a non-CME signal instrument (EBS spot) for a K3 product. Intraday.

### K3-028
- Citation: Han, L.-M., Kling, J.L., Sell, C.W. (1999). "Foreign exchange futures volatility: Day-of-the-week, intraday, and maturity patterns in the presence of macroeconomic announcements." Journal of Futures Markets 19, 665-693.
- Retrieval: abstract only (OpenAlex).
- P-K3-028-a: "this study finds strong day-of-the-week effects for both the Deutsche mark and Japanese yen, mild effects for the British pound, and no effects for the Canadian dollar after controlling for scheduled macroeconomic announcements and days to contract expiration. The day-of-the-week effects are found to be caused either by Mondays' low volatility, or by Thursdays' or Fridays' high volatility."
- Tags: port of D.1 families D (volatility state) and E (day of week) on currency futures; pit-era data. Intraday.

### K3-029
- Citation: Chen, Y.-L., Gau, Y.-F. (2022). "The information effect of order flows in foreign currency futures and spot markets." Journal of Futures Markets. DOI 10.1002/fut.22345.
- Retrieval: abstract only (OpenAlex).
- P-K3-029-a: "Using intraday EUR–USD and JPY–USD data in both electronic futures and spot markets, we examine the important role played by order flow in price discovery and in intermediating the exchange‐rate reactions to macroeconomic news. We find that, after considering the order flows of futures and spot markets, the futures market dominates price discovery when compared with the spot market ... Furthermore, announcement surprises in gross domestic product, jobless claims, and nonfarm payroll affect both order flows and exchange‐rate changes."
- Tags: lead-lag and announcements for 6E/6J (D.1 family E). Intraday.

### K3-030 (PANEL SOURCE, rule 3)
- Citation: Martínez, V., Tse, Y. (2008). "Intraday volatility in the bond, foreign exchange, and stock index futures markets." Journal of Futures Markets 28, 313-334. DOI 10.1002/fut.20315.
- Retrieval: abstract only (OpenAlex).
- P-K3-030-a [K3] [K2] [K1]: "Intraday volatility for the Eurodollar, the Euro/dollar foreign exchange rate, and the E‐mini S&P 500 futures contracts traded on a continuous 23‐hour schedule on the Chicago Mercantile Exchange Globex electronic platform is studied. Volatility transmission in a single market across different regions is mainly explained by intraregion volatility (heat waves); interregion volatility (meteor showers) plays a secondary role. ... Volume tends to increase volatility, but open interest does not affect it."
- Tags: volatility state across regional sessions (D.1 families D and A) on 6E. The same passage serves K1 (E-mini S&P, which is the closed MES exposure, so of limited use) and K2 (Eurodollar is a STIR future, not on the K2 list). Intraday.

### K3-031
- Citation: Chen, Y.-L., Gau, Y.-F. (2010). "News announcements and price discovery in foreign exchange spot and futures markets." Journal of Banking & Finance 34. DOI 10.1016/j.jbankfin.2010.03.009.
- Retrieval: title only. It passed pre-filter on the title. No abstract could be retrieved: OpenAlex has none; Semantic Scholar says "abstract elided by the publisher"; Crossref has no abstract; ScienceDirect is behind a captcha; there is no Wayback snapshot; IDEAS search returned no hit.
- Tags: announcements and lead-lag for FX futures against spot; all content [unverified].

### K3-032
- Citation: Chaboud, A.P., Chernenko, S.V., Howorka, E., Krishnasami Iyer, R.S., Liu, D., Wright, J.H. (2004). "The High-Frequency Effects of U.S. Macroeconomic Data Releases on Prices and Trading Activity in the Global Interdealer Foreign Exchange Market." Federal Reserve Board IFDP 823.
- Retrieval: full text. PDF (curl + pdftotext) from https://www.federalreserve.gov/pubs/ifdp/2004/823/ifdp823.pdf (10,918 words). Found through the OpenAlex API (source: IFDP).
- Mechanism: US data surprises move EUR/USD and USD/JPY within minutes, and there is no drift afterwards. Volume spikes even for in-line releases. Volume clusters at 8:30am, 10am (option expiry) and 11am New York time (the WM/Reuters fix).
- Products and horizon: EBS EUR/USD and USD/JPY, 1-minute; the source gives New York times.
- Cost assumptions: none; event regressions.
- Data window: January 1999 to January 2004.
- Quality tells: Fed staff paper using firm EBS quotes. The finding is a null on post-announcement drift, which argues against slow-drift news trades in FX.
- Verified passages:
  - P-K3-032-a (clock, source-stated New York times): "We see that average one-minute volume spikes at or just after 8:30am, 10am and 11am. ... The 10am spike is likely related to the convention that 10am New York time is the expiration time for many foreign currency options ... The 11am spike is likely related to the WM/Reuters spot foreign exchange fixing, which is at 4pm London time."
  - P-K3-032-b (no drift): "the surprise component of the announcement produces a movement in the conditional mean that is generally completed within a few minutes, and that is effectively a jump. That is, the exchange rate returns subsequent to the few minutes around the time of the data release are orthogonal to the unexpected component of the macroeconomic announcement."
  - P-K3-032-c (numeric, volume): "the predicted peak effect of an announcement right in line with median market expectations is to immediately raise the trading volume index to 1,800, or to 18 times the average per-minute volume. ... if the announcement surprise is plus or minus 100,000 ... making a predicted peak volume of 2,200, or 22 times the average per minute volume."
- Numeric claims: in-line NFP raises EUR/USD per-minute volume to 18x average, and a one-SD surprise to 22x (P-K3-032-c).
- Tags: port of D.1 family E (US releases) on FX. It is evidence AGAINST post-release drift in FX (a non-survivor for drift rules); a release-minute response needs a consensus input and faster execution than the program has. It is also a session-clock input (8:30, 10:00 and 11:00 New York). Intraday.

### K3-033
- Citation: Cai, F., Howorka, E., Wongswan, J. (2006). "Transmission of Volatility and Trading Activity in the Global Interdealer Foreign Exchange Market: Evidence from Electronic Broking Services (EBS) Data." Federal Reserve Board IFDP 863.
- Retrieval: full text. PDF (curl + pdftotext) from https://www.federalreserve.gov/pubs/ifdp/2006/863/ifdp863.pdf (7,578 words).
- Mechanism: volatility and activity in one trading region predict the same region the next day ("heat wave") far more than they predict the next region ("meteor shower").
- Products and horizon: EBS EUR/USD and USD/JPY across five regions (Asia Pacific, Asia-Europe overlap, Europe, Europe-America overlap, America); realised volatility.
- Data window: January 1999 to February 2004.
- Verified passages:
  - P-K3-033-a (abstract): "we find statistically significant evidence for volatility spillovers at both the own-region and the inter-region levels, but the economic significance of own-region spillovers is much more important than that of inter-region spillovers."
  - P-K3-033-b (data): "Broking Services (EBS) covering the period from January 1999 to February 2004."
- Numeric claims: none extracted.
- Tags: volatility-state input (D.1 family D) for 6E and 6J, keyed by session region. Not a return mechanism. Intraday.

### K3-034
- Citation: Kurov, A., Sancetta, A., Wolfe, M.H. (2022). "Drift Begone! Release policies and preannouncement informed trading." Journal of International Money and Finance, 102718. DOI 10.1016/j.jimonfin.2022.102718; SSRN 3502748 (2019). One source.
- Retrieval: abstract only. Verbatim abstract from Wayback raw HTML of the SSRN page. Failed routes: SSRN Delivery (captcha; no Wayback copy of the PDF); ScienceDirect (captcha); OpenAlex lists no open-access location; the co-author's Google Site redirects to a Drive sign-in; Firecrawl had no credits left.
- Mechanism (abstract): FX futures drifted before three UK releases while UK officials had pre-release access. The drift weakened after the UK ended pre-release access in 2017, and the release-time reaction became larger and slower.
- Products and horizon: FX futures around UK CPI, industrial production and retail sales. This is presumably 6B, but the abstract says only "foreign exchange futures market" [product unverified]. The horizon is minutes to hours before and after the release.
- Verified passages:
  - P-K3-034-a (abstract): "In 2017 the UK Statistics Authority discontinued the early access of government officials to market-sensitive macroeconomic data. We examine the effect of this policy change on price adjustment in the foreign exchange futures market around major U.K. macroeconomic announcements. Three macroeconomic announcements (consumer price index, industrial production, and retail sales) show strong evidence of informed trading before their public releases until 2017. This preannouncement price drift weakens with the end of the prerelease access. Consistent with less informed trading before the announcements, the market reaction to the announcements at the official release time has become larger, and the speed of adjustment has become slower."
- Numeric claims: [unverified].
- Tags: port of D.1 family E (release drift) for 6B, with a decay finding: the pre-release drift is gone after 2017. The post-release adjustment became slower, which could matter for a post-release drift rule [inference]. Intraday.

### K3-035 (PANEL SOURCE, rule 3)
- Citation: Kurov, A., Stan, R. (2018). "Monetary policy uncertainty and the market reaction to macroeconomic news." Journal of Banking & Finance 86. DOI 10.1016/j.jbankfin.2017.09.005; SSRN 2776357. One source.
- Retrieval: abstract only. Verbatim abstract from Wayback raw HTML of the SSRN page. Failed routes: SSRN Delivery (captcha; no Wayback PDF), ScienceDirect (captcha), OpenAlex (no open-access location), Firecrawl (no credits).
- P-K3-035-a [K3] [K1] [K2] [K4] (abstract): "We examine whether monetary policy uncertainty influences the reaction of the equity, Treasury security, foreign exchange and crude oil markets, as well as medium-term interest rates, to U.S macroeconomic announcements. Using intraday futures data, we show that in the presence of higher policy uncertainty the response to macroeconomic news weakens in the stock and crude oil markets and strengthens in the Treasury, interest rate and foreign exchange markets."
- Tags: a conditioning variable for announcement responses (D.1 families D and E): FX futures react more strongly to US data when monetary-policy uncertainty is high. Intraday. The same passage serves K1, K2 and K4. Numbers [unverified].

### K3-036
- Citation: Andersen, T.G., Bondarenko, O., Gousgounis, E., Onur, E. (2025). "FX Futures Invariance." SSRN 5315873. Gousgounis and Onur have appeared as CFTC OCE authors (the CFTC OCE page lists Onur); their affiliation on this paper is not verified.
- Retrieval: title only. It passed pre-filter on the title (microstructure invariance on CME FX futures: trade size, volume and volatility scaling). Failed routes: SSRN (captcha), no Wayback snapshot, OpenAlex (no abstract), Semantic Scholar ("not found"), the CFTC OCE research list pages 0-8 (not listed), Firecrawl (no credits).
- Tags: data-native statistics (D.1 family F) and cost modelling for 6E and the other FX futures; content [unverified].

### K3-037
- Citation: Cabrera, J.F.A. (2009). "The Size and Adjustment Speed of Mispricing in Forex Markets." SSRN 1401063.
- Retrieval: title only. Failed routes: SSRN (captcha), no Wayback snapshot, OpenAlex (no abstract), Semantic Scholar (HTTP 429). The author also wrote K3-027 (futures against EBS spot), so the title most likely refers to futures-spot mispricing [inference].
- Tags: a lead-lag or arbitrage item (CME against spot); content [unverified].

### Panel source already read by D.1 (no re-read)
- Baltussen, Da, Lammers, Martens, "Hedging Demand and Market Intraday Momentum" (JFE 2021): D.1 row A10, read in full by D.1 for MES. It surfaced again in the 2nd run's OpenAlex SSRN query "currency futures intraday". Under partition rule 2 it is not re-read here. Whether its futures panel includes currency futures, and what the FX results are, is [unverified from K3's side]. The CatalogWriter should check D.1's A10 entry or ask the lead whether an FX-tagged pass is wanted.

### K3-038
- Citation: Cotter, J., Dowd, K. (2011 arXiv posting). "Intra-Day Seasonality in Foreign Exchange Market Transactions." arXiv:1103.5664.
- Retrieval: full text. PDF (curl + pdftotext) from https://arxiv.org/pdf/1103.5664 (4,452 words). Found through the arXiv API.
- Mechanism: intraday seasonality in returns, volatility and tail outcomes for limit and market orders in DEM/USD on Reuters Dealing 2000-2.
- Products and horizon: DEM/USD (the predecessor pair of 6E), 5-minute to 3-hour GMT blocks.
- Data window: one trading week, 6-10 October 1997 (130,535 entries).
- Quality tells: a one-week sample; it cannot support a trading rule.
- Verified passages:
  - P-K3-038-a: "The D2000-2 data set contains all trading activity in USD/DEM for the trading week covering the 6th to the 10th of October 1997, incorporating 130,535 entries in all."
  - P-K3-038-b: "The majority of trading activity takes place between 9-18 GMT when almost 70% of all orders are processed and the remaining intervals involve relatively thin trades. The quietest period is between 21-24 GMT when less than 1% of orders are filled."
- Tags: session clock (D.1 family A), descriptive only. Intraday. Weak.

### K3-039
- Citation: Batten, J.A., Ellis, C.A., Hogan, W.P. (2004 arXiv posting). "Decomposing Intraday Dependence in Currency Markets: Evidence from the AUD/USD Spot Market." arXiv:math/0412344.
- Retrieval: full text. PDF (curl + pdftotext) from https://arxiv.org/pdf/math/0412344 (6,801 words).
- Mechanism: the local Hurst exponent, range and volatility of AUD/USD change across the 24-hour day and line up with market opens and closes.
- Products and horizon: spot AUD/USD (6A's pair); intraday by GMT.
- Data window: 5 May to 15 June 2000 (42 calendar days, about 30,000 Reuters indicative quotes).
- Quality tells: a tiny sample of indicative quotes; descriptive.
- Verified passages:
  - P-K3-039-a (abstract): "a high-frequency data set of the spot Australian dollar/U.S. dollar provides evidence of the returns distribution across the 24-hour trading 'day', with time-varying dependence and volatility clearly aligning with the opening and closing of markets."
  - P-K3-039-b (data): "from Friday 5th May 9:49:11AM GMT 2000 ... to Thursday 15th June 0:56:6AM GMT, 2000 ... This comprises 42 calendar days."
- Tags: volatility and dependence by session (D.1 families A and D) for 6A; descriptive. Weak.

### Discovery tool note (2nd run, from about 21:18 PDT)
The OpenAlex API refused further queries after its shared free daily budget for this machine's IP ran out ("Insufficient budget ... resets at midnight UTC"). Discovery then used the Crossref API (titles, rarely abstracts), the arXiv API, the Semantic Scholar API (rate-limited, HTTP 429 at times) and direct curl of site listings. Quantpedia strategy pages (quantpedia.com/strategies/...) returned HTTP 500 to both curl and WebFetch and have no Wayback copies, so their primary papers were sought through Crossref by title keywords.

### K3-040 (PANEL SOURCE, rule 3; likely)
- Citation: Kosowski, R., Liu, ?, Liu, ?, Wang, ? (2023). "Overnight-Intraday Reversal Everywhere." SSRN 4605208. First names were not retrieved.
- Retrieval: title only. It passed pre-filter on the title: the overnight return predicts an opposite-signed intraday return across asset classes. It is the probable primary source for the Quantpedia strategy "overnight-intraday-weekly-reversal-in-currency-futures", but that link is [unverified] because the Quantpedia page was unreachable. Failed routes: SSRN (captcha), no Wayback snapshot, Semantic Scholar ("not found"), arXiv (no match), Crossref (no abstract), Firecrawl (no credits).
- Tags: port of D.1 family C (overnight-to-intraday reversal) on currency futures, probably also covering other clusters' futures. The strategy name says "weekly", so the rebalance frequency and the intraday holding are [unverified]. Content [unverified].

### K3-041
- Citation: Khademalomoom, S., Narayan, P.K. (2019). "Intraday effects of the currency market." Journal of International Financial Markets, Institutions and Money. DOI 10.1016/j.intfin.2018.09.008.
- Retrieval: abstract only, verbatim from the Semantic Scholar API (JSON). Failed routes: ScienceDirect (captcha); the figshare record 20784991 is metadata only, with no file; Firecrawl (no credits).
- P-K3-041-a (abstract): "We use hourly exchange rates of the six most liquid currencies (i.e. the Australian Dollar, British Pound, Canadian Dollar, Euro, Japanese Yen, and Swiss-Franc) vis-a-vis the United States Dollar over the period 2004–2014. We show that the bilateral exchange rates of these currencies exhibit a strong presence of time-of-the-day effects. Specifically, we uncover three new intraday effects previously unknown in the literature, namely, local markets post-opening effect, major markets activities effect, and markets overlapping times effect."
- Tags: port of D.1 family A (session clock) for 6A, 6B, 6C, 6E, 6J, 6S; hourly; 2004-2014. Magnitudes [unverified].

### K3-042
- Citation: Elyasiani, E., Kocagil, A.E. (2001). "Interdependence and dynamics in currency futures markets: A multivariate analysis of intraday data." Journal of Banking & Finance 25. DOI 10.1016/s0378-4266(00)00126-6.
- Retrieval: title only. Failed routes: Semantic Scholar (no abstract), Crossref (no abstract), ScienceDirect (captcha), OpenAlex (daily budget exhausted before this item), Firecrawl (no credits).
- Tags: INSIDE FX: lead-lag and interdependence among CME currency futures (a K3 region item: cross-rates and triangular relationships); intraday; pit-era. Content [unverified].

### K3-043
- Citation: Ayadi, ?, Ben Omrane, W., Das, ? (2024). "Macroeconomic news, senior officials' speeches, and emerging currency markets: An intraday analysis of price jump reactions." Emerging Markets Review, 101147.
- Retrieval: title only. Semantic Scholar marks it open access at the DOI, but the DOI resolves to ScienceDirect (captcha). No abstract came from Crossref or Semantic Scholar.
- Tags: announcements and officials' speeches as jump triggers in emerging-market currencies. K3's only EM product is 6M (MXN); whether MXN is covered is [unverified]. Intraday. Lead note, 21:25 PDT: 6M dropped by D1 (day-session coverage 0.903 < 0.95), so this item is relevant only if it also covers G10 pairs. No full-text read was spent on it.

### K3-044
- Citation: Fenn, D.J., Howison, S.D., McDonald, M., Williams, S., Johnson, N.F. (2009). "The Mirage of Triangular Arbitrage in the Spot Foreign Exchange Market." arXiv:0812.0913. Co-authors after Fenn were not re-checked against the title page; the registry line records "Fenn, D.J., et al."
- Retrieval: full text. PDF (curl + pdftotext) from https://arxiv.org/pdf/0812.0913 (7,576 words). Found through a Quantocracy-listed practitioner post (Aligrithm, "FX Edge Lives in Other Markets") that cites it, then located with the arXiv API.
- Mechanism: triangular arbitrage opportunities (EUR/USD, USD/CHF, EUR/CHF; EUR/USD, USD/JPY, EUR/JPY) exist on executable prices but last seconds. Profiting would require beating other participants to an "unfeasibly large proportion" of them.
- Products and horizon: spot FX on Reuters D2000-2 executable prices; seconds.
- Data window: includes 10/02/2005 to 10/27/2005 (the second-by-second executable dataset); times in GMT.
- Verified passages:
  - P-K3-044-a (abstract): "We show that triangular arbitrage opportunities do exist, but that most have short durations and small magnitudes. ... We demonstrate further that the number of arbitrage opportunities has decreased in recent years, implying a corresponding increase in pricing efficiency. Using trading simulations, we show that a trader would need to beat other market participants to an unfeasibly large proportion of arbitrage prices to profit from triangular arbitrage over a prolonged period of time."
  - P-K3-044-b (data): "consists of second-by-second executable ... over the period 10/02/2005–10/27/2005" (the passage is broken across lines in the extracted text).
- Tags: INSIDE FX (triangular relationship); a non-survivor. The horizon is seconds and would need high-rate trading, which Topstep prohibits. NOT feasible for the program. Logged because the brief asks for failures.

### K3-045
- Citation: Aiba, Y., Hatano, N., Takayasu, H., Marumo, K., Shimizu, T. (2002). "Triangular arbitrage as an interaction among foreign exchange rates." Physica A; arXiv:cond-mat/0202391.
- Retrieval: full text. PDF (curl + pdftotext) from https://arxiv.org/pdf/cond-mat/0202391 (3,237 words).
- P-K3-045-a (abstract): "We first show that there are in fact triangular arbitrage opportunities in the spot foreign exchange markets, analyzing the time dependence of the yen-dollar rate, the dollar-euro rate and the yen-euro rate. Next, we propose a model of foreign exchange rates with an interaction."
- Tags: INSIDE FX; the arbitrage horizon is seconds (per K3-044's review of it, execution delays of "up to 4 seconds"). NOT feasible for the program. An econophysics model paper.

## 4. Flags for K8

- Run 1 | Alquist, Ellwanger, Jin (2020) JFM, oil-inventory news and asset markets | crude (K4) to FX (K3), rates and equities | already registered and flagged by K4 as K4-008; not read by K3.
- Run 2 | Aligrithm, "FX Edge Lives in Other Markets (cross-asset series)" (Quantocracy listing; practitioner) | government-bond rates (K2) to FX (K3) via interest-rate parity on a graph | cross-asset FX signal; only its triangular-arbitrage citations were followed (K3-044, K3-045).
- Run 2 | Peng, Chollete, Hughen, Lu (2026), "Forecasting Volatility of Currencies and Oil with Brown Firms" (SSRN; OpenAlex listing) | equity (brown-firm stocks) to FX and crude volatility | cross-asset volatility forecast.
- Run 2 | Quantpedia strategy titles "equity-momentum-spillover-to-currencies" and "stock-and-bond-returns-predict-currency-returns" (sitemap slugs only; pages HTTP 500) | equity (K1) and bonds (K2) to FX (K3) | cross-asset; horizon unknown.
- Ownership note, no flag: K3-001 (Melvin and Prins) uses non-US equity-index returns as its signal for the FX trade into the month-end fix. The partition's K3 region names "month-end fix flows and equity-hedging rebalancing" as K3's, so it stays here. The lead may re-route it if equity-index signals count as a K1 leg.

## 5. Registry ids owned

K3-001 to K3-045, 45 lines in reports/stage_e0_source_registry.jsonl.
- K3-001 to K3-015 are run 1's; run 1 edited two of them in place (see section 0).
- K3-016 to K3-045 are run 2's, appended only, with claim times 20:52-21:21 PDT.
- Known registry errors, not rewritten:
  - K3-018 names the author as "Panagiotou, K." (correct: Marsh, I.W., Panagiotou, P., Payne, R.).
  - K3-005 says "unspecified" (Bessho, Sugimoto, Suzuki).
  - K3-012, K3-014 and K3-015 say "unspecified" (Breedon, Rime, Vitale; Park; Tornell, Yuan).
  - K3-038 and K3-039 say "unspecified" (Cotter, Dowd; Batten, Ellis, Hogan).
  - K3-040 and K3-043 carry "?" first names.
- Process slip: K3-019's PDF was fetched about a minute before its claim line was appended. No other registry entry matched, so nothing was read twice.
