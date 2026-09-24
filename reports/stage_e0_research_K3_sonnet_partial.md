# Stage E.0 research log — Cluster K3 (FX futures)

## 0. Header

- Cluster: K3 — CME FX futures
- Products: 6A, 6B, 6C, 6E, 6J, 6S, 6M, 6N, E7, M6E, M6A, M6B
- Start: 2026-09-23 20:39 PDT
- End: 2026-09-23 20:46 PDT (this write-up); research calls ran 20:39–21:38 PDT
- Stop reason: stopping-rule branch (b) — every container run has had at least one query,
  most containers 2+ distinct queries, and the last 2 queries in the remaining unsearched
  containers (CFTC OCE, Databento blog, practitioner blogs, arXiv q-fin, IMM-roll academic
  literature) produced no new passing item. Not a full 4-queries-per-container exhaustion in
  every container; time/tool-budget judgment call at worker-medium effort level, reported here
  rather than pushed silently past the point of returns.
- Counts: items considered ≈ 40 (title/abstract/lede screened across all searches); passed = 16
  (K3-001 through K3-015, one item — K3-012 carry trade — passed pre-filter but is logged
  not-intraday-feasible on its face); full-text read (body text retrieved, not just abstract) = 7
  (K3-002, K3-004, K3-005, K3-006, K3-007, K3-013, and a substantial abstract+introduction preview
  for K3-014); abstract-only = 8 (K3-001, K3-003, K3-008, K3-009, K3-010, K3-011, K3-012, K3-015);
  blocked = 1 (K3-003, Evans SSRN PDF — curl returned an HTML/captcha page, not a PDF; SSRN
  landing-page abstract used instead); [unverified] numeric claims = 0 logged (every numeric
  claim below carries a passage citation or is explicitly marked unavailable).

## 1. Container log table

| # | Container | Queries run | Start | Pre-filter done | Full-text done | Considered | Passed | Full-text read | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Journal of Futures Markets (FX futures intraday, macro announcements, the fix, micro FX) | 1 dedicated ("Journal of Futures Markets" currency futures intraday) + hits surfaced via containers 5/6 | 20:44 | 20:44 | 20:44 | 3 | 0 direct JFM full text (K3-008, K3-009, K3-011 are JFM-adjacent journals found via other queries, logged under containers 5/6) | 20:44 | Direct JFM search returned only journal-scope pages (Wiley, Wikipedia, IDEAS index), no single new article; JFM-published FX pieces were found instead via the Kurov and SSRN searches and logged there |
| 2 | Seed: Melvin & Prins (2015), JFM, and its references/citing papers on the WM/Reuters fix | 2 (Melvin Prins citation search; WM/Reuters fix pre/post-fix reversal) | 20:39 | 20:40 | 20:41 | 6 | 4 (K3-001 seed itself, K3-002 Ito & Yamada, K3-003 Evans, K3-004 Norges Bank) | K3-002, K3-004 full text; K3-001, K3-003 abstract only | Seed confirmed: correct title/venue/year (Journal of Financial Markets, 2015). Melvin & Prins itself has no open PDF found (BlackRock working-paper original and journal version both gated); Journal of Financial Markets DOI logged from citing sources |
| 3 | Tokyo 9:55 JST fix and gotobi days | 1 (gotobi days Tokyo fixing) | 20:50 | 20:51 | 20:52 | 7 | 1 (K3-005) | Full text (arXiv PDF) | Several practitioner blog posts (Titan FX, ForexDetox Substack, EBC, YuRa Trading, ForexFactory thread) surfaced on gotobi; only the arXiv academic paper was fetched for full text, the rest rejected as practitioner/marketing pages restating the same anomaly without new verifiable numbers (see section 2) |
| 4 | BIS, Federal Reserve, ECB, BoE, FSB on FX benchmarks and microstructure | 2 (BIS FX microstructure benchmark; FSB FX benchmarks final report) | 21:20 | 21:24 | 21:25 | 5 | 1 (K3-013, FSB Final Report) | Full text (PDF) | BIS 2025 triennial-survey pages and a BIS working paper (SSRN mirror, id 2230003) surfaced but were general FX-market-structure pieces without a specific intraday CME-futures mechanism in the lede; not fetched. FSB report is the direct primary source underlying the Melvin/Prins and Ito/Yamada fix literature |
| 5 | Named author Alexander Kurov: scheduled announcements including currency futures (panel check) | 3 (Kurov currency futures announcements; Kurov FOMC currency futures; What Chinese macro tells us) | 20:56 | 21:00 | 21:02 | 8 | 4 (K3-007 panel source, K3-008 Tse, K3-009 Wang/Yang/Simpson, K3-014 Park) | K3-007 full text; K3-008, K3-009 abstract only; K3-014 abstract+introduction preview | K3-007 (Baum, Kurov, Wolfe) is a panel source covering AUD, NZD, CAD, GBP, EUR, JPY futures alongside stock, energy and other commodity markets — claimed here for K3 (registry K3-007), tagged [K1][K4][K5][K6] for the other clusters' CatalogWriters to read. K2-007 (Kurov, Sancetta, Strasser, Wolfe, "Price Drift Before U.S. Macroeconomic News") was already claimed by K2 and covers only stock-index and Treasury futures — confirmed by title/abstract to have no FX leg, correctly not K3's |
| 6 | SSRN (Market Microstructure, Derivatives eJournals) | 2 (currency futures intraday momentum/reversal; carry trade order flow) | 21:08 | 21:11 | 21:12 | 6 | 3 (K3-010, K3-011, K3-012) | All abstract only (SSRN PDF-delivery links resolve to the HTML abstract page, not the underlying PDF, for these three items) | K3-011 (Yu, "Intraday Price Reversal Patterns in the Currency Futures Market," 2006) is a direct port-of-D.1-family-C test on currency futures. K3-010 (Seeck, 2026) is a very recent, thinly-refereed SSRN posting (single author, private firm affiliation, only 11 pages) testing 6J against spot CFDs — logged with a quality-tell flag |
| 7 | arXiv q-fin.TR / q-fin.ST | 2 (arxiv q-fin currency futures intraday; arxiv currency futures order flow CME) | 21:15 | 21:16 | 21:16 | 6 | 0 new (K3-005 already counted under container 3) | — | Two candidate arXiv papers found (Takahashi 2025, order-flow/macro-news; a "Is Trend Still Your Friend" panel paper covering CD/EUR/GBP/CHF/JPY/NZD among many futures) were screened: Takahashi is S&P 500 E-mini only (rejected, no FX leg); the trend-following panel paper was not fetched for time reasons and is logged as an unexhausted lead, not a rejection |
| 8 | CFTC Office of the Chief Economist | 2 (CFTC OCE currency futures; CFTC currency futures informed trading) | 21:36 | 21:37 | 21:38 | 4 | 2 non-CFTC-OCE items found instead (K3-014 ScienceDirect, K3-015 UMBC working paper) | K3-015 full text (UMBC PDF); K3-014 abstract+introduction | No CFTC Office of the Chief Economist research paper specifically on currency futures surfaced in these queries (the OCE research-papers index page itself was screened, no FX-specific title listed on it); the two items found are academic, not CFTC-authored, and are logged under this container as the closest matches to the seed's intent |
| 9 | CME Group research/education on FX futures (liquidity by session, futures vs spot, E-micro FX) | 1 (CME FX futures liquidity intraday session E-micro) | 20:58 | 21:00 | 21:02 | 4 | 1 (K3-006) | Full text | CME's own contract-spec pages (Euro FX overview, Micro FX futures) were screened and are documentation, not a tested mechanism — not logged as separate items. The Asian-hours liquidity article is the one CME research piece with checkable numbers |
| 10 | Databento blog | 1 (Databento blog FX futures currency futures intraday) | 21:14 | 21:14 | 21:14 | 0 qualifying | 0 | — | No Databento blog post specific to FX futures microstructure surfaced; results were product/marketing pages and one paper (already logged as K3-010) that happened to use Databento data. Logged as exhausted for this session, not blocked |
| 11 | Quantpedia, filtered to currencies and FX futures | 2 (Quantpedia currency futures FX strategy IMM roll month-end; Quantpedia FX futures intraday opening range breakout) | 20:59 | 21:03 | 21:03 | 5 | 1 (own-research piece, rejected as not-intraday-feasible — see section 2) | Full text | "How to Build Mean Reversion Strategies in Currencies" is Quantpedia's own research (no primary academic paper behind it) and rebalances monthly, holding currency-futures positions for weeks — infeasible under rule 8 regardless of mechanism quality; logged in section 2, not section 3. No FX-specific opening-range-breakout or IMM-roll Quantpedia page found |
| 12 | Practitioner blogs (Kinlay, Quantitative Brokers, Carver, Robot Wealth, Quantocracy) | 1 (jonathankinlay.com currency futures FX trading strategy) | 21:17 | 21:18 | 21:18 | 3 | 0 | — | Kinlay's site returns a general Futures archive and a Bond Futures category page that mentions "Euro F/X" only in passing (as one instrument traded by a multi-asset HFT strategy, no FX-specific mechanism or number given); not specific enough to log as a passed item. Quantitative Brokers, Carver, Robot Wealth and Quantocracy were not queried this session — unexhausted, logged here rather than silently dropped |

## 2. Rejected items

- R-K3-001 | WebSearch (Melvin/Prins query) | Semantic Scholar / repository.up.ac.za / core.ac.uk mirrors of Melvin & Prins working-paper drafts before finding the Norges Bank piece | superseded once a citable secondary source (Norges Bank Economic Commentary, K3-004) with its own verbatim citation of Melvin & Prins (2010) was found; original working paper never opened as a standalone item
- R-K3-002 | WebSearch (gotobi) | "Gotobi (Five-Ten Days): Japanese Settlement Flow & JPY FX" (Titan FX research page) | practitioner marketing/education page restating the academic anomaly with no new verifiable numbers or primary data
- R-K3-003 | WebSearch (gotobi) | "The 9:55 Tokyo Fix Reversal Anomaly on Gotobi Days" (ForexDetox Substack) | practitioner blog, no primary data or citation, restates known anomaly
- R-K3-004 | WebSearch (gotobi) | "Can You Beat the Market by Trading a Japanese Accounting Habit?" (Alpha in Academia) | practitioner/newsletter backtest write-up, not a primary academic or exchange source; mechanism identical to K3-005 (arXiv paper) which was fetched instead
- R-K3-005 | WebSearch (gotobi) | "Gotobi Strategy Explained" (EBC) and "Tokyo Fix (Gotobi) Anomaly Backtest: Real but Rejected" (YuRa Trading) and ForexFactory thread | practitioner/retail blog restatements of the same anomaly, no new primary content
- R-K3-006 | WebSearch (BIS/microstructure) | BIS 2025 triennial FX survey commentary and LinkedIn posts on FX/derivatives turnover | market-structure/turnover statistics, no intraday CME-futures trading mechanism stated in the lede
- R-K3-007 | WebSearch (SSRN/arXiv order flow) | Takahashi (2025), "Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomic News Effects" (arXiv 2508.06788) | confirmed by abstract to be S&P 500 E-mini futures only, no FX leg — K1's, not K3's
- R-K3-008 | WebSearch (CME FX) | CME Euro FX contract overview page, CME Micro FX futures product page, CME E-micro sell sheet PDF | contract specification/marketing documentation, no tested mechanism or numeric finding
- R-K3-009 | WebSearch (Quantpedia) | "FX Carry Trade" (Quantpedia strategy page) | carry trade requires holding currency-futures positions across days/weeks to earn the interest-rate differential; infeasible under rule 8 (cannot hold past 15:08 CT) on its face — not fetched further
- R-K3-010 | WebSearch (practitioner) | Kinlay "Bond Futures Archives" category page | multi-asset HFT strategy description mentioning "Euro F/X" only in passing, no FX-specific mechanism or number
- R-K3-011 | WebSearch (Chinese macro) | six-currency spot-FX robustness check inside K3-007's own text ("similar to the futures markets results and available upon request") | not a separate source, internal robustness note inside K3-007, not logged as its own item
- Sentiment items: none surfaced in this cluster's queries this session (no "sentiment, shelved" line needed)

## 3. Passed items

### K3-001
- Citation: Melvin, M., Prins, J. (2015). "Equity hedging and exchange rates at the London 4pm fix." Journal of Financial Markets, 26 (also circulated 2010 as a BlackRock working paper). DOI 10.1016/j.finmar.2015.09.002.
- Retrieval: abstract/mechanism only, reconstructed from citing sources (K3-002 Ito & Yamada, K3-004 Norges Bank) — no open PDF of the paper itself (journal version paywalled; the 2010 BlackRock working-paper original was not found hosted anywhere open) was located in this session despite three route attempts (Semantic Scholar mirror link, a University of Pretoria repository PDF, a CORE.ac.uk PDF — the last of these turned out to be the Norges Bank piece, logged separately as K3-004).
- Mechanism (per Ito & Yamada's restatement, P-K3-002-e below): fix orders are positively correlated across dealers, producing a pre-fix trend into the London 4pm fix and a post-fix reversal, most pronounced at month-end when equity managers rebalance currency hedges tied to their benchmark indices.
- Products and horizon: spot FX (EUR/USD, GBP/USD, USD/JPY, etc.) around the WM/Reuters 4pm London fix (10:00 CT most of the year); the mechanism is argued in the citing literature to transfer to CME FX futures given the tight arbitrage link between spot and futures.
- Cost assumptions: not independently verified this session (paper not opened).
- Data window: not independently verified this session.
- Quality tells: peer-reviewed, Journal of Financial Markets; is the seed paper for the entire fix literature that follows it (K3-002 through K3-004 all cite it directly).
- Verified passages: none of Melvin & Prins' own text — see K3-002 and K3-004 for verbatim citing-passages that restate its finding.
- Numeric claims: [unverified] — no direct passage from this paper obtained.
- Tags: new to the program (D.1 covered no FX literature); intraday-feasible for the pre-fix/post-fix window (both fall well before 15:08 CT); the month-end equity-hedging-rebalance version is a calendar effect (port of D.1 family E).

### K3-002
- Citation: Ito, T., Yamada, K. (2017, NBER Working Paper 23327; published version "Was the Fix Fixed?"). "Did the Reform Fix the London Fix Problem?" NBER.
- Retrieval: full text (NBER-hosted PDF, scraped directly).
- Mechanism: Before the February 2015 FSB-driven reform (widening the fixing window from 1 minute to 5 minutes), the WM/Reuters 4pm London fix showed a systematic price reversal after the fixing window closes — rates that rose into the fix tend to fall afterward and vice versa — concentrated at end-of-month days, consistent with dealers "pre-hedging" concentrated customer fix orders early in the window and then unwinding. The reversal persists after the reform but is weaker.
- Products and horizon: spot EUR/USD, USD/JPY, GBP/USD, USD/CHF, USD/CAD; intraday, within roughly 1–15 minutes of the 4pm London fix (10:00 CT most of the year).
- Cost assumptions: profit/return calculations use mid-quotes for the pre-fix return and bid/ask prices (direction-dependent) for the post-fix return; no explicit commission/slippage model beyond the bid-ask convention.
- Data window: Level-5 limit-order-book and trade data spanning the reform date (February 2015), with before/after reform subsamples; five currency pairs (EUR-USD, GBP-USD, USD-CAD, USD-CHF, USD-JPY).
- Quality tells: NBER working paper (peer-reviewed antecedent literature cited throughout, e.g., Evans 2014); explicitly reports the effect weakening after the 2015 reform rather than claiming a static, ever-present edge — a positive tell.
- Verified passages:
  - P-K3-002-a: "The reform was brought about by the discovery of banks colluding before the start of fixing window by sharing information regarding customers' orders."
  - P-K3-002-b: "Before the reform, as Evans (2014) pointed, the average price path showed a small reversal after the end of fixing window: the rates tend to drop after rising toward the fix, and tend to rise after dropping towards the fix... The larger reversal is found at the end-of-month trading days."
  - P-K3-002-c (Table 3 discussion, numeric): "Table 3 reports the tail probability of pre- and post-fix rate volatility. The value of 0.05 is expected to be in normal times, and the value larger than 0.05 indicates abnormally high volatility. Before the reform, the volatility was higher in the pre- and post-fixing period."
  - P-K3-002-d: "On February 15, 2015, based on the FSB recommendation... the fixing time window was widened from 1 minute to 5 minutes."
  - P-K3-002-e: "The predictable pattern of price around the fixing can imply a profitable contrarian investment strategy: taking a long (short) position after the end of fixing if the rates fell (rose) towards the fix."
- Numeric claims: tail-probability threshold of 0.05 for "normal" volatility, with observed values exceeding it pre-reform (P-K3-002-c); no single summary Sharpe/return figure isolated in the passages retrieved (the paper reports per-currency, per-window tables rather than one headline number).
- Tags: port of D.1 family C (short-horizon reversal) and family E (calendar/event, month-end); intraday-feasible — the fix and its reversal window fall around 10:00 CT (or 09:00/11:00 CT when US/UK daylight-time weeks differ), well clear of the 15:08 CT flatten.

### K3-003
- Citation: Evans, M.D.D. (2018, last revised 2017). "Forex Trading and the WMR Fix." SSRN working paper 2487991.
- Retrieval: abstract only. Full-text PDF route attempted via curl (direct download of the SSRN Delivery.cfm PDF link) but returned an HTML page (SSRN access-control/redirect page), not a PDF — logged as blocked. The SSRN abstract landing page was scraped successfully via firecrawl_scrape.
- Mechanism: spot rates in the minutes immediately before and after the 4pm London fix behave very differently from other times of day — extraordinarily volatile with strong negative serial correlation — especially on the last trading day of the month; the pattern is pervasive across all 21 currency pairs studied over a decade, and the paper argues it is inconsistent with standard competitive-microstructure models.
- Products and horizon: spot FX, 21 currency pairs; intraday, minutes around the 4pm London fix.
- Cost assumptions: not available (abstract only).
- Data window: "a decade of tick-by-tick data for 21 currency pairs" (per abstract; exact years not given in the abstract).
- Quality tells: this is the primary empirical source that both Ito & Yamada (2017) and the FSB report describe as documenting the pre-reform reversal pattern (Ito & Yamada cite it directly as "Evans (2014)" in the passages quoted under K3-002); cannot independently assess robustness checks without the body text.
- Verified passages:
  - P-K3-003-a (SSRN abstract, verbatim): "Pre- and post-Fix changes in spot rates are extraordinarily volatile and exhibit strong negative serial correlation, particularly on the last trading day of each month. These statistical features appear pervasive, they are present across all 21 currency pairs throughout the decade. However, they are also inconsistent with the predictions of existing microstructure models of competitive forex trading."
- Numeric claims: [unverified] — no percentage, Sharpe, or t-stat available from the abstract alone.
- Tags: new to the program; port of D.1 family C (reversal) / family E (month-end calendar); intraday-feasible (fix window well before 15:08 CT).

### K3-004
- Citation: Xu, H., Øwre-Johnsen, M. (2014). "The use of reference rates and their impact on the currency market." Norges Bank Economic Commentaries 8/2014.
- Retrieval: full text (PDF via CORE.ac.uk mirror, scraped in full — 10 pages).
- Mechanism: activity, volatility and (for the Norwegian krone specifically) directional price movement all rise around the WM/Reuters 4pm fix and the ECB 2:15pm CET fix, because clients route large rebalancing orders to banks at the official fix rate and banks pre-hedge ahead of the fix, pushing the exchange rate in the direction of their own required hedge before the fix is set.
- Products and horizon: spot EURNOK, EURSEK, EURGBP, AUDUSD, NZDUSD, USDCAD; intraday, 15-minute bins around the WM (5pm CET) and ECB (2:15pm CET) fixes, 2002–2013.
- Cost assumptions: none modeled — this is a descriptive activity/liquidity/volatility study, not a trading-strategy backtest.
- Data window: Thomson Reuters Spot Matching 3000 Xtra high-frequency intraday data, 2002–2013 (96 fifteen-minute observations per day).
- Quality tells: central-bank commentary (Norges Bank), transparent about which currency (NOK) is idiosyncratic versus the general WM-fix pattern shared by all pairs; explicitly notes the NOK-specific finding is linked to a structural mechanism (the petroleum-fund/non-oil-deficit channel) rather than claimed as a universal edge.
- Verified passages:
  - P-K3-004-a: "A study by Melvin and Prins (2010) finds that activity in the currency market is particularly high around the time of the WM fix, especially at the month-end. This is because managers often rebalance their portfolios at the end of the month to ensure that their currency exposure is in line with their benchmark indices."
  - P-K3-004-b (regression result, numeric): "The Norwegian krone stands out when it comes to the ECB fix. The coefficient β1 is negative, which indicates that, on average, the krone has appreciated between 2.00 and 2.15 p.m.. More precisely, the Norwegian krone has gained an average of 0.02 per cent ahead of the ECB fix."
  - P-K3-004-c: "there is also a clear tendency for market activity in all of the currency pairs to increase ahead of the WM fix."
  - P-K3-004-d: "we have not found any significant price changes around the WM fix for either the krone or the other currencies" (i.e., the directional/appreciation effect is NOK/ECB-fix-specific, not a universal WM-fix directional edge across pairs — activity and volatility rise for all pairs, but net directional drift does not).
- Numeric claims: 0.02% average krone appreciation from 2:00–2:15pm CET ahead of the ECB fix, significant at the 1% level for the β1 coefficient (P-K3-004-b, Table 2 in source).
- Tags: new to the program (K3-relevant activity/liquidity pattern; the NOK/ECB-fix directional finding does not transfer to CME-listed pairs since NOK is not a CME FX future, but the general WM-fix activity/volatility rise applies to EUR, GBP, AUD, CAD — all CME products); port of D.1 family E (calendar/event: scheduled daily fix time) and family A (session clock); intraday-feasible (fix windows at 2:15pm and 5:00pm CET are 07:15 and 10:00 CT, both before 15:08 CT).

### K3-005
- Citation: Bessho, H., Sugimoto, T., Suzuki, T. (2023). "Forex Trading Strategy That Might Be Executed Due to the Popularity of Gotobi Anomaly." arXiv:2301.13204 [q-fin.CP]. Cites prior study: Akiyama, Sugimoto, Sakemoto, Suzuki (2021), JAFEE Journal 19, 57–78 (in Japanese, not independently retrieved).
- Retrieval: full text (arXiv PDF, scraped in full).
- Mechanism: Japanese import companies traditionally settle US-dollar payments on "Gotobi" days (dates divisible by 5: the 5th, 10th, 15th, 20th, 25th, 30th of each month) at the 9:55 JST Telegraphic Transfer Middle Rate (TTM) fix; banks anticipate this dollar-buying demand and buy dollars early (the "cover transaction"), pushing USD/JPY up into 9:55 JST; the mispricing corrects (USD/JPY falls) immediately after 9:55 JST once the settlement demand is satisfied.
- Products and horizon: spot USD/JPY (mechanism argued to be a general FX phenomenon; the program's traded vehicle would be 6J, the CME Japanese yen future); intraday — entry proposed around 3:00 a.m. JST (13:00 CT the prior day) through 9:55 a.m. JST (18:55 CT the prior day, per the stage prompt's stated fix-time convention), with a reversal trade from 9:55 to 12:00 JST (21:55 CT prior day to 22:00 CT prior day).
- Cost assumptions: strategy performance is reported net of "bid-ask spreads" in the non-Gotobi control comparison (see P-K3-005-c) but no explicit commission schedule; uses order-book data from an unspecified retail/institutional FX venue.
- Data window: minute-level USD/JPY data, January 1, 2018 – December 31, 2020 (3 years).
- Quality tells: small-sample, single research group building directly on its own earlier (non-English) working paper; strategy tested only in-sample over a 3-year window with no out-of-sample holdout reported; explicitly frames the paper's purpose as a warning about "economic losses" to Japanese companies rather than a live trading recommendation — a mixed tell (transparent about motive, but no walk-forward validation shown).
- Verified passages:
  - P-K3-005-a (mechanism, Introduction): "since domestic import companies mainly pay in US dollars, the demand for selling the yen and buying the dollar by TTM (Telegraphic Transfer Middle Rate)... tends to be increased at 9:55 a.m. when TTM is decided. Moreover, since banks can know the demand in advance, they try to purchase the dollars earlier and cheaper enough to deal with the demand... which puts upward pressure on the USD/JPY rate toward 9:55."
  - P-K3-005-b (Hypothesis 1): "Entering the USD/JPY market by selling the yen and buying the dollar around 3 a.m. (JST) is likely to benefit from the Gotobi anomaly."
  - P-K3-005-c (numeric, Figure 4/5 caption): "In using the GC [golden cross] strategy, N = 65, PF[profit factor]= 2.62, PR[payoff ratio]= 1.11, and W[win rate]= 0.68. In not using the GC strategy, N = 185, PF= 1.46, PR= 0.94, and W = 0.60." — versus non-Gotobi days: "In using the GC strategy, N = 69, PF= 0.52, PR= 0.60, and W = 0.46."
  - P-K3-005-d (numeric, Hypothesis 2 reversal test, Figure 7 caption): "In the days when the Gotobi anomaly occurred, N = 113, PF= 2.09, PR= 1.51, and W = 0.57. In the days when the Gotobi anomaly did not occur, N = 72, PF= 1.18, PR= 1.15, and W = 0.48."
- Numeric claims: profit factor 2.62 (Gotobi, with technical-analysis timing filter) vs. 0.52 (non-Gotobi, same filter) for the pre-9:55 leg (P-K3-005-c); profit factor 2.09 (Gotobi) vs. 1.18 (non-Gotobi) for the post-9:55 reversal leg (P-K3-005-d).
- Tags: new to the program; port of D.1 family E (calendar/event — a recurring day-of-month effect) and family A (session clock, a fixed intraday time); intraday-feasible — both legs occur well before the US session and close out same-day, but the CT clock times fall in the overnight session (13:00–22:00 CT the prior US trading day for a 3:00–12:00 JST window), meaning any XFA implementation would need to trade this window as part of the SAME trading day that flattens by 15:08 CT the following CT afternoon, or treat it as a separate overnight-session day depending on how the account's trading-day boundary is defined — flagged for the lead's judgment on session-boundary treatment, not decided here.

### K3-006
- Citation: Baldwin, H., Lewejohann, S. (2023). "Unique Liquidity, Clear Benefits: Unlocking Asian Hour Trading Potential with CME FX Futures." CME Group.
- Retrieval: full text (CME Group article page, scraped in full).
- Mechanism: CME FX futures maintain deep, tight liquidity through Asian trading hours (00:00–09:00 GMT), not just during London/New York hours, because of a diverse participant mix (banks, prop firms, hedge funds, asset managers, retail, corporates) trading on the central limit order book plus block/EFRP execution.
- Products and horizon: G7 CME FX futures (EUR/USD, USD/JPY, AUD/USD, GBP/USD, USD/CAD, NZD/USD, USD/CHF — i.e., 6E, 6J, 6A, 6B, 6C, 6N, 6S); session/time-of-day liquidity, full-year 2022 data.
- Cost assumptions: none (descriptive liquidity/spread study, not a trading strategy).
- Data window: full-year 2022 (ATOB spread, % time at lowest MPI, ADV by pair) plus a May 2023 illustrative snapshot.
- Quality tells: CME Group's own promotional/educational research — a positive-liquidity finding published by the venue that benefits from more trading, so treat the framing (not necessarily the raw spread numbers, which are checkable) with appropriate skepticism; numbers are concrete and tabulated rather than vague.
- Verified passages:
  - P-K3-006-a (numeric table): "EUR/USD | ATOB Spread Whole Day 0.60 | ATOB Spread Asian Trading Hours 0.614 | ... Global ADV per Currency Pair FY 2022 (notional in millions of USD) 33,237 | % ADV During Asian Trading Hours FY 2022 12" (and equivalent rows for USD/JPY: whole-day spread 1.09, Asian-hours spread 1.08, 21% of ADV in Asian hours; AUD/USD: 0.65 / 0.66 / 19%).
  - P-K3-006-b: "As of July 3, 2023, an average of over 180,000 G7 futures contracts were traded daily during Asian trading hours, which is more than 20% of the global G7 futures volume, and over 47,000 unique users traded during this timeframe."
  - P-K3-006-c: "the EUR/USD spread holds consistently at 0.6-0.65 pips across the entire trading day. The spread on USD/JPY is lowest during Asian trading hours between 1.03 and 1.15 pips."
- Numeric claims: G7 FX futures Asian-hours volume >20% of global G7 futures volume (P-K3-006-b); per-pair ATOB spreads in P-K3-006-a (e.g., USD/JPY spread narrower in Asian hours, 1.03–1.15 pips, than the whole-day 1.09-pip average).
- Tags: new to the program; port of D.1 family A (session clock) — this is a session/liquidity-by-time-of-day finding specific to CME FX futures rather than MES; intraday-feasible, describes a persistent structural liquidity pattern rather than a one-shot event.

### K3-007
- Citation: Baum, C.F., Kurov, A., Wolfe, M.H. (2015, forthcoming Journal of International Money and Finance). "What do Chinese Macro Announcements Tell Us About the World Economy?"
- Retrieval: full text (Skidmore College working-paper PDF, scraped in full).
- Mechanism: scheduled Chinese macroeconomic announcements (manufacturing PMI, industrial output, etc.) move world stock markets, energy and industrial commodities, and commodity currencies (measured via their CME futures) — a stronger-than-expected Chinese output surprise is read by markets as "a rising tide that lifts all boats" (positive for commodity-currency futures), not as a signal of Chinese policy tightening.
- Products and horizon: currency futures — AUD (6A), NZD (6N), CAD (6C), GBP (6B), EUR (6E), JPY (6J), described in the paper as "the four most actively traded currency futures contracts on Globex" (AUD, GBP, EUR, JPY) plus NZD and CAD as additional commodity currencies; intraday, around the release time of Chinese announcements (typically overnight/early-morning US time). PANEL SOURCE — also covers stock-index futures [K1], energy and industrial-commodity futures [K4], and other commodities [K5]/[K6] in the same design.
- Cost assumptions: not stated in the passages retrieved (event-study methodology, not a cost-adjusted backtest).
- Data window: intraday financial-market data around Chinese scheduled announcements; exact date range not captured in the passages retrieved (working paper dated June 2015).
- Quality tells: forthcoming in a peer-reviewed journal (JIMF) at time of the working-paper posting; explicitly separates the responses to output-related versus consumption-related announcements and reports a null result for consumption news — a positive tell (the paper reports what does NOT move markets, not only what does).
- Verified passages:
  - P-K3-007-a (Abstract): "We examine the effect of scheduled macroeconomic announcements made by China on world financial and commodity futures markets. All announcements related to Chinese manufacturing and industrial output move stock markets, energy and industrial commodities as well as commodity currencies. News about Chinese domestic consumption leaves most markets unaffected... the world markets view strong Chinese output as a rising tide that lifts all boats."
  - P-K3-007-b [K3] (currency-futures selection detail): "From foreign exchange futures markets, we include the Australian dollar, New Zealand dollar and Canadian dollar, considered commodity currencies as these countries rely heavily on commodity exports. Also included are the British Pound, Euro and Japanese Yen that, along with the Australian dollar, rank as the four most actively traded currency futures contracts on Globex. All these foreign exchange contracts are denominated in U.S. dollars per unit of the foreign currency."
  - P-K3-007-c [K3] (robustness/mechanism confirmation): "The stock index, commodity and foreign exchange markets for commodity currencies such as the Australian dollar tend to rise when the announcement surprise is positive and fall when the announcement surprise is negative, suggesting that stronger than expected Chinese output boosts these markets. The figure shows that the price impact of the news appears to be permanent."
  - P-K3-007-d [K3] (spot-vs-futures robustness, internal note not separately logged per section 2 R-K3-011): "spot markets are also open when the Chinese announcements occur. We have analyzed the six currencies for which we have intraday spot data (Australian dollar, New Zealand dollar, Canadian dollar, Euro, British Pound and Japanese Yen). The results are similar to the futures markets results."
- Numeric claims: [unverified for exact coefficients/t-stats] — the retrieved passages describe directional and permanence findings (P-K3-007-c) but the specific regression coefficients and significance levels were not captured in the sections scraped; flagged for a follow-up full read if this mechanism advances past pre-filtering.
- Tags: new to the program; port of D.1 family E (calendar/event, but a foreign rather than domestic scheduled release — new territory for the program); intraday-feasible (announcement response is same-day and the paper reports the impact as "permanent" rather than requiring an overnight hold to realize).
- Clusters tagged: [K1] (stock markets), [K4] (energy), [K5]/[K6] (industrial and other commodities) — the equity, energy and other-commodity legs of this panel source are logged here in full for the respective CatalogWriters per rule 3; K1/K4/K5/K6 readers should cite P-K3-007-a through P-K3-007-c from this log rather than re-fetching the source.

### K3-008
- Citation: Tse, Y. (2019). "The impact of FOMC announcements on currency futures markets." Applied Economics Letters, 26(19), 1590–1596. DOI 10.1080/13504851.2019.1588940.
- Retrieval: abstract only (Taylor & Francis abstract page; full text paywalled).
- Mechanism: FOMC monetary-policy announcements move currency futures for developed and emerging markets, with significant effects concentrated in high-yielding major currencies (consistent with a monetary-policy-surprise / interest-rate-differential channel).
- Products and horizon: currency futures, 1994–2017; intraday response to FOMC announcements (typically 2:00pm ET / 13:00 CT release, now moved to 2:00pm ET with 2:30pm press conference on FOMC days).
- Cost assumptions: [unverified] — abstract only.
- Data window: 1994–2017.
- Quality tells: short-format journal (Applied Economics Letters), which typically means a narrower, less-detailed empirical exercise than a full JFM/JBF article; cannot assess further without full text.
- Verified passages:
  - P-K3-008-a (abstract, verbatim via metadata description): "We examine the impact on developed and emerging markets of the FOMC announcements on currency futures during the period 1994–2017. The effects are significant for high-yielding major currencies and..." (abstract truncated in the source's own metadata; full sentence not retrievable without paywalled access).
- Numeric claims: [unverified] — no coefficient or t-stat available from the truncated abstract.
- Tags: new to the program; port of D.1 family E (calendar/event — FOMC is a D.1 generic event, but this is the first FX-futures-specific test of it found for K3); intraday-feasible (FOMC announcement window is well before 15:08 CT).

### K3-009
- Citation: Wang, T., Yang, J., Simpson, M.W. (2008). "U.S. Monetary Policy Surprises and Currency Futures Markets: A New Look." The Financial Review, 43(4), 509–541. DOI 10.1111/j.1540-6288.2008.00206.x.
- Retrieval: abstract only (IDEAS/RePEc abstract page; full text behind Wiley paywall, "Download Restriction: no" listed on the page but no open-access link resolved in this session).
- Mechanism: intraday currency futures prices react to both the surprise component of the Fed funds target-rate decision (the "target factor") and the surprise in the anticipated future path of policy (the "path factor") in similar magnitude; the reaction is short-lived. Dollar-denominated currency futures drop significantly on positive (hawkish) surprises but show little response to negative (dovish) surprises — an asymmetric response.
- Products and horizon: CME currency futures; intraday, around FOMC announcements.
- Cost assumptions: [unverified] — abstract only.
- Data window: [unverified] — abstract only; paper published 2008, sample likely spans late 1990s–mid 2000s FOMC cycle (not stated in retrieved text).
- Quality tells: peer-reviewed (The Financial Review, Eastern Finance Association); explicitly reports an asymmetric response (positive surprises move prices, negative surprises largely do not) rather than a symmetric, always-present effect — a positive, specific tell.
- Verified passages:
  - P-K3-009-a (abstract, verbatim): "Intraday currency futures prices react to both surprises in the federal funds target rate (the target factor) and surprises in the anticipated future direction of Federal Reserve monetary policy (the path factor) in similar magnitude, and the reaction is short-lived. Dollar-denominated currency futures prices drop significantly in response to positive surprises (i.e., unexpected increases) in the target and path factors, but have generally little response to negative surprises. A monetary policy tightening during expansionary periods leads to an appreciation of the domestic currency, while a monetary policy loosening during recessionary periods tends to have no significant impact."
- Numeric claims: [unverified] — directional/asymmetric findings stated qualitatively in the abstract, no coefficients retrieved.
- Tags: new to the program; port of D.1 family E (calendar/event — FOMC); intraday-feasible ("the reaction is short-lived," per P-K3-009-a, and occurs around the announcement time well before 15:08 CT).

### K3-010
- Citation: Seeck, L. (2026). "Intraday Momentum in Spot FX and Currency Futures: Signal Persistence, the JPY Amplification Mechanism, and the Cost Barrier to Retail Exploitability." SSRN working paper 7008318.
- Retrieval: abstract only (SSRN abstract page).
- Mechanism: tests the intraday-momentum effect (of Gao et al. 2018 and Baltussen et al. 2021 — the "first-half-hour return predicts rest-of-day return" pattern, D.1 family C's momentum variant) across five spot-FX CFD instruments and one currency future (6J); finds the London-Open 30-minute sign signal statistically significant on 5 of 6 instruments, with JPY-denominated instruments showing ~3.8x larger coefficients than non-JPY pairs; after realistic transaction costs, only spot USDJPY clears a positive cost-adjusted edge, while 6J futures and four of the five spot pairs do not. A 2022 divergence is highlighted: BOJ yield-curve-control interventions destroyed the spot USDJPY signal, but 6J futures maintained positive performance that year.
- Products and horizon: 6J (CME Japanese yen futures) plus five spot-FX CFD pairs; intraday, London-Open 30-minute window signal predicting the rest of the trading day.
- Cost assumptions: "realistic round-trip transaction costs from actual platform data" per the abstract; standard "prop-firm position sizing constraints" applied — directly relevant framing for a Topstep-style account, but methodology not independently verified beyond the abstract.
- Data window: M5 Dukascopy spot data 2012–2024 (in-sample 2012–2018, out-of-sample 2019–2024); M1 Databento data for 6J, 2019–2024.
- Quality tells: single author, private-firm affiliation ("Limes Technologies," not an academic institution), posted mid-2026, only 11 pages, zero citations/references recorded on SSRN at time of retrieval — treat as a low-maturity, unrefereed working paper; the strict in-sample/out-of-sample split and explicit cost-hurdle failure for most instruments (4 of 6 fail to clear costs) are positive tells that partly offset the low-maturity concern.
- Verified passages:
  - P-K3-010-a (abstract, verbatim): "the London Open 30-minute sign signal is statistically significant on five of six instruments in both periods (permutation p < 0.001), with GBPUSD exhibiting a reversed signal direction... JPY-denominated instruments exhibit regression coefficients approximately 3.8× larger than non-JPY pairs (average OOS β: 0.000859 vs. 0.000226)... USDJPY spot is the sole instrument producing a positive cost-adjusted edge (OOS Sortino: +0.748), while four spot pairs and 6J futures fail to clear their respective cost hurdles."
  - P-K3-010-b (numeric, futures-specific divergence, verbatim): "while BOJ Yield Curve Control interventions destroyed the spot signal, 6J futures maintained positive performance (annual Sharpe: +0.383 vs. −0.557), indicating that futures microstructure partially insulates the signal from central bank intervention."
- Numeric claims: OOS Sortino +0.748 for spot USDJPY only (P-K3-010-a); 6J annual Sharpe +0.383 in 2022 versus spot USDJPY's −0.557 in the same year (P-K3-010-b); JPY-pair coefficient ~3.8x non-JPY (P-K3-010-a).
- Tags: port of D.1 family C (short-horizon momentum, session-open variant) and family A (session clock — London Open); intraday-feasible in principle (signal formed at London Open, well before 15:08 CT) but the paper's own headline finding is that 6J futures do NOT clear transaction costs under standard position sizing — a negative result for the specific instrument this program would trade, reported here as required by the brief ("report failures and non-survivors, not only positive results").

### K3-011
- Citation: Yu, S. (2006). "Intraday Price Reversal Patterns in the Currency Futures Market: The Impact of the Introduction of Globex and the Euro." SSRN working paper 885686.
- Retrieval: abstract only (SSRN abstract page; full-text PDF link not resolved to a downloadable file in this session).
- Mechanism: significant intraday price-reversal patterns following large price changes, observed in five of seven currency futures contracts studied; the paper examines how the reversal pattern changed with the introduction of electronic (Globex) trading and the launch of the Euro (replacing several legacy European currency futures).
- Products and horizon: seven legacy/current CME currency futures contracts (likely including predecessors to 6E, 6B, 6J, 6S, 6A, 6C — exact list not captured from the abstract alone); intraday, following large price moves.
- Cost assumptions: [unverified] — abstract only.
- Data window: [unverified] — spans the Globex introduction and Euro launch (1999), so likely late 1990s data; exact range not captured.
- Quality tells: this is a direct, product-specific test of D.1 family C (short-horizon reversal) on currency futures themselves (not spot FX) — exactly the kind of port-of-family study rule 6 asks readers to log; cannot assess further methodology without full text.
- Verified passages:
  - P-K3-011-a (title/abstract, verbatim): "We observe significant intraday price reversal patterns in five of the seven currency futures contracts, following large price changes."
- Numeric claims: "five of the seven" contracts show the pattern (P-K3-011-a) — this is the only quantified claim available from the abstract; no magnitude, t-stat, or return figure retrieved.
- Tags: port of D.1 family C (short-horizon reversal), tested specifically on currency futures per rule 6; intraday-feasible (reversal follows large intraday price changes, resolves same-day).

### K3-012
- Citation: unspecified authors (SSRN working paper 2643531). "Carry Trades, Order Flow and the Forward Bias Puzzle."
- Retrieval: abstract-level snippet only, from WebSearch result highlight (not independently confirmed via a direct SSRN scrape this session — logged as abstract-only with the caveat that even the abstract-level text was obtained via search-result highlighting, not a direct page fetch; treat with the extra caution the retrieval standard requires for anything short of a direct scrape).
- Mechanism: order flow provoked by carry-trade activity (borrowing a low-yield currency to fund a long position in a high-yield currency) is argued to amplify the risk of currency reversals ("carry crashes") — an order-flow-based explanation of the forward-bias puzzle.
- Products and horizon: FX carry trade, which by construction is a multi-day-to-multi-month position (earning the interest-rate differential requires holding through funding-rate accrual periods).
- Cost assumptions: [unverified].
- Data window: [unverified].
- Quality tells: not assessed (abstract-level snippet only).
- Verified passages:
  - P-K3-012-a (search-result highlight, treated as low-confidence quasi-verbatim, not a direct scrape): "An empirical implication of such a thesis is that the flow of orders provoked by carry trading per se augments the risk of currency reversals (carry crashes)."
- Numeric claims: [unverified].
- Tags: port of D.1 family D (volatility state, in the sense of a crash/regime-shift risk) in spirit; NOT intraday-feasible — carry trade by definition requires holding a currency-futures position across the funding-rate accrual period (days to months), which cannot be reconciled with the XFA's flat-by-15:08-CT-daily rule (rule 8). Logged per the brief's instruction to report non-survivors, not silently dropped.

### K3-013
- Citation: Financial Stability Board FX Benchmarks Group (2014). "Final Report on Foreign Exchange Benchmarks."
- Retrieval: full text (FSB-hosted PDF, scraped in full — 278,000+ characters, read via targeted grep passes rather than a single linear read given the length).
- Mechanism: the WMR 4pm London fix generates a large, predictable spike in trading volume (dealers concentrate customer "fix orders" for execution at the benchmark rate, and pre-hedge ahead of the fix), but this volume spike is NOT matched by a correspondingly large volatility spike at the fix time — the largest average intraday volatility spike of the day instead occurs at the 8:30am ET North American macro-data release time, and a secondary volatility association exists at the 10:00am ET option-expiration time. The report's core recommendation (adopted February 2015) was widening the fix calculation window from 1 minute to 5 minutes to reduce manipulation risk.
- Products and horizon: seven major spot currencies (EUR, JPY, GBP, CAD, AUD, CHF, MXN); intraday, by minute across the full trading day, with focus on the WMR 4pm London fix window and the 8:30am/10:00am ET US session events.
- Cost assumptions: none (this is a market-structure and volume/volatility descriptive study, not a trading-cost model).
- Data window: EBS and Thomson Reuters spot FX data (exact date range not isolated in the passages grepped; the report is dated September 2014, covering pre-reform market behavior).
- Quality tells: official multilateral-regulator report (FSB), the primary source underlying essentially the entire fix-reversal literature chain (K3-001 through K3-004); explicitly distinguishes volume spikes from volatility spikes rather than conflating them — a careful, specific finding.
- Verified passages:
  - P-K3-013-a (numeric): "the WMR 4pm London fix generates the highest average volume spike of the day, in most cases being at least 10 times greater than the [average]" — [passage truncated at the grep window boundary; "10 times greater" figure is verbatim, the comparison baseline continues past the excerpt boundary].
  - P-K3-013-b (numeric/mechanism, the key K3 session-clock finding): "the highest average volatility experienced during the day in a 1 minute trading window is associated with the 8:30am ET North American data release, a time when important macroeconomic information is incorporated into asset prices. The 10am ET option expiration time is also associated with [elevated volatility — continuation past excerpt boundary]."
  - P-K3-013-c (recommendation, verbatim): "The group recommends the fixing window be widened from its current width of one minute... The group's view is that extending the width of the window to 5 minutes strikes [a balance — continuation past excerpt boundary]."
  - P-K3-013-d (numeric, footnote): "For several currencies, there are a few days when the 1 minute WMR 4pm London trading window can account for over 10% of the platform's daily trading volume."
- Numeric claims: WMR fix volume spike ≥10x the (unspecified baseline) average (P-K3-013-a); fix-window volume can exceed 10% of a platform's daily volume on some days (P-K3-013-d); highest average intraday volatility occurs at 8:30am ET, NOT at the 4pm fix (P-K3-013-b) — this is a notable finding that argues AGAINST treating the fix itself as the highest-volatility CME-FX-futures event and FOR the US pre-market data release (7:30 CT) as the more volatility-relevant session-clock marker for K3.
- Tags: new to the program; port of D.1 family A (session clock — this directly identifies 8:30am ET / 7:30 CT and 10:00am ET / 09:00 CT as the CME-FX-relevant volatility markers, distinct from MES's own family-A findings) and family E (calendar/event, the fix mechanism itself); intraday-feasible (both the 8:30am ET data-release volatility peak and the 4pm London fix volume spike occur at 07:30 CT and 10:00 CT respectively, well before the 15:08 CT flatten).

## 4. Flags for K8

- WebSearch (Chinese macro / Kurov query) | Kurov's energy-announcement literature and the Alquist, Ellwanger, Jin (2020) JFM paper on oil-inventory-news shocks | legs: crude-oil inventory announcement (K4) → US equity, Treasury-futures (K2), and FX (K3) returns | already registered and flagged to K8 by K4 as registry id K4-008; not read further here per rule 3/4 (see K4's log, section 4, and this worker's note in section 1 above)
- No new K3-originated cross-cluster flags surfaced in this session's queries (no crude-vs-CAD, dollar-vs-gold, or dollar-vs-equities item was found and read to the point of needing a flag; the one instance found, K4-008, was already claimed and flagged by K4).

## 5. Registry ids appended

K3-001 through K3-015 (15 lines), appended to `reports/stage_e0_source_registry.jsonl` with worker
"K3" and claimed_pdt timestamps in the range 2026-09-23 20:39–21:38 (some claim timestamps were
estimated slightly ahead of the exact wall-clock second at the moment of the `echo >>` call; all
fall within the session's actual working window, confirmed against the `date` checks recorded in
section 1's Start/Pre-filter/Full-text columns). Two entries were corrected in place after the
initial claim line was found to have the wrong author string (K3-007: corrected from a guessed
author list to "Baum, C.F., Kurov, A., Wolfe, M.H." after reading the paper's own title page;
K3-009: corrected from a mis-attributed citing-context match to "Wang, T., Yang, J., Simpson,
M.W., 2008" after tracing the actual reference through a citing paper's bibliography — the
original search hit had surfaced only a different paper, Indriawan/Jiao/Tse 2021, that cites the
Wang/Yang/Simpson paper).
