# Stage E.0 Task 3 — K5 metals literature log

Cluster K5. Products: GC, MGC, SI, SIL, HG, MHG, PL (gold {GC,MGC}; silver {SI,SIL}; copper
{HG,MHG}; platinum {PL}).

Start: 2026-09-23 20:15 PDT. End: 2026-09-23 20:40 PDT.

**Stop reason: resource/cost constraint flagged mid-task (session cost warning), not exhaustion of
the container list under the lead's stopping rule (60 full-text reads, or every container queried
>=4 times with the last 2 producing nothing new).** Containers 1–4, 7 and part of 8 received
several queries each and are reasonably covered. Containers 5 (arXiv, one query only), 6 (CFTC,
one query), 9 (Databento, one query, nothing found), 10 (Quantpedia, two queries, both rejected on
horizon), and 11 (practitioner blogs, one query, nothing K5-specific found) did NOT reach the
4-query floor. This is reported as an incomplete stop, not a clean one — see final reply.

Counts: items considered (titles/abstracts screened) ~28; passed pre-filter and logged in full: 9;
full text obtained: 5 (K5-006 Crain et al, K5-007 Batten et al PLOS, K5-009 Wang & Lu arXiv,
K5-010 LBMA FAQ page, plus substantial "section snippets" for K5-008 Cohen); abstract-only
(publisher paywalled, all documented retrieval routes failed): 4 (K5-001, K5-002, K5-004, K5-005);
blocked with nothing usable: 1 (CME gold settlements page, timeout twice); [unverified] numeric
claims: none logged as passing numeric claims without a matching verbatim passage — any number not
directly quoted below is omitted rather than asserted.

Retrieval standard applied per lead addendum: every "verbatim" passage below was obtained either
via `firecrawl_scrape` (markdown of the live page) or via a PDF fetched to disk and read with
`pdftotext`. Passages sourced only from a WebSearch summary or an unlabelled WebFetch rendering
were re-fetched to this standard before being logged; none remain from the earlier, non-compliant
pass.

## 1. Container log

| # | Container | Queries run | Start | Pre-filter done | Full-text done | Considered | Passed | Full-text read | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Journal of Futures Markets (Wiley) | 5 (LBMA/COMEX fix search; Caminschi/Heaney; copper microstructure; gold-silver ratio/platinum; metals macro announcements) | 20:15 | 20:28 | 20:35 | 8 | 2 (K5-001 abstract-only; also surfaced K5-004/005 via citation chain) | 20:35 | seed paper confirmed live on Wiley (DOI 10.1002/fut.21636); full text paywalled |
| 2 | Caminschi & Heaney seed: refs/citing papers | 3 (title search; Nilsson; Crain/BearWorks) | 20:15 | 20:27 | 20:33 | 3 | 2 (K5-002 abstract-only, K5-006 full text) | 20:33 | Crain et al. is CC-BY-SA open access; full text recovered from the journal's own PDF after the university mirror was Cloudflare-blocked |
| 3 | Alexander Kurov, multi-asset papers | 3 (WVU macro news search; gold FOMC liquidity search; Smales/Yang belief-dispersion search) | 20:27 | 20:31 | 20:31 | 3 | 0 direct Kurov hits on metals (his 2017 panel paper is S&P500/10Y-Treasury only, rejected below); surfaced two non-Kurov, metals-specific papers instead (K5-004, K5-005) | 20:31 | no Kurov paper found that tests gold/silver/copper specifically; container queried 3x, stopped short of the 4x floor |
| 4 | SSRN (Market Microstructure / Derivatives / Commodities eJournals) | 2 (Nilsson SSRN page; Smales/Yang working-paper search) | 20:27 | 20:31 | 20:31 | 1 (Nilsson, already counted under container 2) | 0 new | 20:31 | firecrawl_scrape reaches SSRN abstract + "Open PDF" link, but the PDF link redirects back to the abstract page — full text confirmed blocked, not just unattempted; under the 4-query floor |
| 5 | arXiv q-fin.TR / q-fin.ST | 1 (gold/silver/copper intraday search) | 20:37 | 20:37 | 20:37 | 2 (Cohen-adjacent PLOS/ScienceDirect hit counted under container 1/2; Wang & Lu copper vol.) | 1 (K5-009, full text) | 20:37 | under the 4-query floor; q-fin.ST not separately searched |
| 6 | CFTC Office of Chief Economist | 1 | 20:31 | 20:31 | 20:31 | 1 ("Convective Risk Flows in Commodity Futures Markets") | 0 (rejected, weekly COT frequency, not intraday) | 20:31 | under the 4-query floor |
| 7 | LBMA / ICE Benchmark Administration; LME/SHFE vs CME hours | 3 (LBMA auction methodology; LME/SHFE/CME hours; LBMA Silver Price FAQ scrape) | 20:28 | 20:29 | 20:37 | 3 | 1 logged as primary documentation (K5-010); LME/SHFE/CME hours logged as background facts under the same container, not a separate registry id (public factual pages, not a "finding") | 20:37 | ICE PDF (Precious_Metals_Benchmark_statement.pdf) fetched but text was not extractable from its PDF structure; LBMA's own FAQ page substituted successfully |
| 8 | CME Group research/education (metals) | 3 (CME education/settlement search; gold settlement page fetch, twice — both timed out) | 20:28 | 20:31 | timed out, not completed | 1 (gold settlement window fact, sourced from search snippet quoting CME's settlement page, not independently re-verified verbatim — flagged below) | 0 confirmed via direct scrape | not completed | CME settlement page fetch failed twice (60s timeout); the settlement-window figure below is marked [unverified] pending a successful direct fetch |
| 9 | Databento blog | 1 | 20:32 | 20:32 | 20:32 | 0 | 0 | 20:32 | no Databento blog post on metals microstructure found; under the 4-query floor |
| 10 | Quantpedia (gold/silver/copper/platinum) | 2 | 20:34 | 20:34 | 20:34 | 2 | 0 (both rejected on horizon — daily/monthly rebalanced, cross-sectional or portfolio strategies) | 20:34 | under the 4-query floor |
| 11 | Practitioner blogs (Kinlay, QB, Carver, Robot Wealth, Quantocracy) | 1 | 20:33 | 20:33 | 20:33 | 0 K5-specific | 0 | 20:33 | no K5-specific practitioner material surfaced; under the 4-query floor |

## 2. Rejected items

- R-K5-001 | Journal of Futures Markets | Bracker (1999), "Detecting and modeling changing volatility in the copper futures market" | pre-1999, superseded search noise, not pursued (title-level, no abstract read)
- R-K5-002 | arXiv | "Construction of an SDE Model from Intraday Copper Futures Prices" (MDPI Risks) | pure stochastic-model construction paper, no trading mechanism or timing claim in the title/abstract
- R-K5-003 | Kurov, Sancetta, Strasser, Wolfe (2017/2019 JFQA), "Price Drift before U.S. Macroeconomic News" | full text confirmed (pdftotext of the Skidmore working-paper PDF): "We use second-by-second E-mini S&P 500 stock index and 10-year Treasury note futures data... to analyze the impact of 30 U.S. macroeconomic announcements" — no gold/silver/copper/platinum instrument; K1/K2 territory, not K5
- R-K5-004 | CFTC OCE | "Convective Risk Flows in Commodity Futures Markets" | weekly time series matched to Tuesday-to-Tuesday COT reports (2000–2011); not an intraday horizon, rule 8
- R-K5-005 | Quantpedia | "A New Return Asymmetry Investment Factor in Commodity Futures" (22 commodities incl. copper, platinum, silver, Apr 1991–Jul 2021) | cross-sectional/portfolio factor strategy at (implied) monthly rebalance frequency; not intraday, rule 8; not read further
- R-K5-006 | Quantpedia | "Commodity Portfolio Strategy for a Potential 2026 Inflationary and Supply Shock Regime" (ETF cross-sectional momentum incl. CPER, PPLT, SLV) | portfolio-level, monthly-rebalanced ETF momentum; not intraday, rule 8
- R-K5-007 | practitioner/social | "silver declines before COMEX options expiration due to delta hedging" (discoveryalert.com.au) | vendor/content-marketing site, speculative framing, no data or citation; quality tell noted, not pursued to full text
- R-K5-008 | JFM (via search) | "Who Sets the Price of Gold? London or New York" (Hauptfleisch 2016 JFM) | plausible K5 fit (London/COMEX price discovery) but not reached before the stop; flagged for the lead as an unread candidate, not rejected on merit

## 3. Passed items

### K5-001
- **Citation:** Caminschi, A. & Heaney, R. (2014). "Fixing a Leaky Fixing: Short-Term Market Reactions to the London PM Gold Price Fixing." Journal of Futures Markets, 34(11), 1003–1039. DOI 10.1002/fut.21636.
- **Retrieval:** Abstract only. Full text is paywalled at Wiley (direct fetch returned HTTP 403). Routes tried and failed: (1) publisher (onlinelibrary.wiley.com) — 403; (2) RePEc/IDEAS mirror — abstract only, `File URL: http://hdl.handle.net/` with no usable full text; (3) Wayback Machine capture of the Wiley page — redirected to a cookie-set page, no article body. Abstract obtained via `firecrawl_scrape` of the RePEc/IDEAS page (genuine markdown fetch, not a search summary).
- **Mechanism:** Studies the London PM gold price fixing's effect on the GC futures contract and the GLD ETF; finds elevated volume/volatility and informed-trader returns in the minutes after the fixing opens, before the fixing result is published.
- **Products/horizon:** GC gold futures (and GLD, non-CME, K5-relevant as background); horizon is minutes (intraday, within the PM fixing window, 15:00 London / 09:00–10:00 CT depending on DST — well before the 15:08 CT flatten).
- **Cost assumptions:** not stated in the abstract; [unverified], full text needed.
- **Data window:** not stated in the abstract; [unverified].
- **Quality tells:** none observable from the abstract; the paper is widely cited and is credited (per secondary UWA press material, not independently verified here) with contributing to the 2015 replacement of the London Fix — this attribution itself is [unverified], not drawn from the paper's own text.
- **Verified passages:**
  - P-K5-001-a (abstract, RePEc mirror of Wiley abstract): "We find significantly elevated levels of trade volume and price volatility immediately following the fixing's start, well before the conclusion of the fixing and the publication of its results... we find statistically significant return advantages in the 4 minutes following the start of the fixing for informed traders... Trades in the opening minutes of the fixing are significantly predictive of the price direction of the fixings, in some cases exceeding 90%."
- **Numeric claims:** "4 minutes" advantage window — P-K5-001-a; "exceeding 90%" predictive accuracy — P-K5-001-a. Both verbatim from the abstract; all other numbers (effect sizes, sample stats) [unverified], full text not obtained.
- **Tags:** new to the program. Intraday-feasible: yes — mechanism is a same-session reaction to a scheduled twice-daily auction, flat well before 15:08 CT, uses market-order-compatible directional signals (not queue-position or SIM-fill dependent as described).
- **Clusters tagged:** [K5] only.

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

### K5-004
- **Citation:** Smales, L.A. & Yang, Y. (2015). "The importance of belief dispersion in the response of gold futures to macroeconomic announcements." International Review of Financial Analysis, 41(C), 292–302. DOI 10.1016/j.irfa.2015.01.017.
- **Retrieval:** Abstract only. Routes tried and failed: (1) ScienceDirect direct — paywalled (confirmed via RePEc download-restriction note: "Full text for ScienceDirect subscribers only"); (2) RePEc/IDEAS abstract mirror — abstract only, `firecrawl_scrape` genuine fetch; (3) Wayback Machine capture of the ScienceDirect abstract page (2020-07-29 snapshot) — abstract + "Highlights" only, "View full text" link leads back to the paywalled live site.
- **Mechanism:** Gold futures' trading volume, returns and volatility response to US macro announcements (esp. unemployment, GDP), with a novel "belief dispersion" measure amplifying the response.
- **Products/horizon:** COMEX gold futures (per keywords: "Gold futures... COMEX... High-frequency"); horizon: seconds to ~90 seconds post-release, intraday.
- **Cost assumptions:** [unverified].
- **Data window:** [unverified] (not in abstract/highlights).
- **Quality tells:** none apparent from abstract; peer-reviewed Elsevier journal.
- **Verified passages:**
  - P-K5-004-a (RePEc/IDEAS abstract, firecrawl_scrape): "Market activity, in terms of traded volume, returns, and volatility, responds to new information quickly, with the majority of the reaction complete within 90-s."
  - P-K5-004-b (same source): "gold futures exhibit greater reactions to 'good' economic news (which is negative for gold prices) and the magnitude of the response does not appear to increase during recession."
- **Numeric claims:** "90-s" reaction window — P-K5-004-a.
- **Tags:** new to the program (product-specific announcement-response study on gold; distinct from the K4/D.1 generic announcement family since it is gold-specific with a belief-dispersion conditioning variable). Intraday-feasible: yes — reaction window is under 2 minutes, well inside a single session, market-order compatible.
- **Clusters tagged:** [K5] only.

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

### K5-006
- **Citation:** Crain, S.J., Hoelscher, S.A. & Jones, J.S. (2020). "Fixing the Fix for Silver and Gold." ACRN Journal of Finance and Risk Perspectives, 9, 177–197. DOI 10.35944/jofrp.2020.9.1.013.
- **Retrieval:** Full text obtained. University mirror (bearworks.missouristate.edu) PDF was Cloudflare-blocked (`curl` returned a "Just a moment..." challenge page; `firecrawl_scrape` of the article landing page worked and gave the abstract, but the PDF link itself stayed blocked). Full text recovered from the journal's own site: DOAJ's record linked directly to `http://www.acrn-journals.eu/resources/jofrp09m.pdf` (the full Volume 9 issue PDF, 21 pages as fetched, containing this article at its original pagination 177–197), downloaded with `curl` and read with `pdftotext -layout`. CC-BY-SA open access (per the article's own rights statement).
- **Mechanism:** Compares gold and silver futures/spot volatility before vs. after the London gold/silver fix's 2014–2015 change from a small-bank telephone negotiation to an electronic multi-participant auction, testing whether the change reduced volatility consistent with reduced manipulation.
- **Products/horizon:** Silver and gold futures on "the Chicago Mercantile Exchange Globex platform" (i.e., SI/GC-equivalent continuous series) plus LBMA spot fix prices; horizon is DAILY — this is a daily-bar structural-break study, not an intraday trading signal.
- **Cost assumptions:** not modeled; the paper studies volatility levels, not a tradeable strategy with costs.
- **Data window:** "January 1, 2008, through June 27, 2018" (silver); gold analysis uses the same window split at the 2015-03-20 fix-change date.
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
- **Data window:** not explicitly stated as a date range in the extracted introduction/abstract text; [unverified] (full paper has a data section not transcribed here).
- **Quality tells:** none apparent from the retrieved abstract/introduction; standard econometrics/ML comparison paper, methodologically explicit (GARCH, HAR, RNN, LSTM, GRU named).
- **Verified passage:**
  - P-K5-009-a (Abstract, pdftotext of the arXiv PDF): "In forecasting daily realized volatility for COMEX copper futures with a rolling window approach, the econometric models, particularly HAR, outperform recurrent neural networks overall, with HAR achieving the lowest QLIKE loss function value. However, when the data is replaced with hourly high-frequency realized volatility, the deep learning models outperform the GARCH model."
- **Numeric claims:** none with a specific number quoted (QLIKE values not extracted); no numeric claim logged beyond the qualitative model-ranking above.
- **Tags:** port of D.1 family D (volatility state), tested product-specifically on COMEX copper. Intraday-feasible: this is a forecasting-accuracy study, not itself a trading rule — the volatility-state distinction (HAR wins daily, deep learning wins hourly) could inform a volatility-regime filter for an intraday copper rule, but the paper itself makes no trading claim and no flatten-by-15:08-CT question arises since nothing is held.
- **Clusters tagged:** [K5] only.

### K5-010
- **Citation:** LBMA / ICE Benchmark Administration. "LBMA Silver Price FAQs" (public documentation page, undated/current as of 2026-09-23).
- **Retrieval:** Full page obtained via `firecrawl_scrape` (genuine markdown fetch of the live LBMA page).
- **Mechanism:** Documents the LBMA Silver Price auction mechanics: a 30-second-round electronic auction starting at 12:00 London time, algorithmic matching of lakh-denominated buy/sell orders within a tolerance band, restarting rounds until equilibrium.
- **Products/horizon:** Silver (spot fix, a non-CME leading instrument for SI/SIL per partition section 1); horizon: the auction itself runs in the minutes around 12:00 London (07:00 ET / 06:00 CT in winter, 05:00 CT-ish adjustments for DST) — this is background/reference documentation, not a study with a mechanism-and-effect claim.
- **Cost assumptions:** n/a (not a strategy source).
- **Data window:** n/a (current operational documentation).
- **Quality tells:** primary source (the benchmark administrator itself); fully reliable for mechanics, not for market-impact claims.
- **Verified passage:**
  - P-K5-010-a: "The auction takes place at 12 noon (UK time) each working day... The LBMA Silver Price is set in US dollars per troy ounce in a series of auction rounds, each lasting 30 seconds... In the first round the system algorithm will attempt to match buy and sell orders within the permitted tolerance level (3 lakhs). If the buy and sell orders are out of tolerance, the auction price will change and the auction will restart until the buy and sell volumes are in tolerance and the equilibrium price is set."
- **Numeric claims:** "30 seconds" per round, "3 lakhs" tolerance — both P-K5-010-a.
- **Tags:** background/reference, not a family port (this is documentation, not a research finding) — supports the mechanism claims in K5-001/002/006 above rather than standing alone as a candidate. Intraday-feasible: n/a (reference material).
- **Clusters tagged:** [K5] only.

## 4. Background facts (not separate registry ids, supporting the CatalogWriter)

- LME Copper: "The LME Select electronic platform opens at 01:00 London time and closes at 19:00... the famous 'Ring' sessions... begin at 11:40 AM London time" — sourced from a WebSearch summary only, NOT independently re-verified via firecrawl_scrape or a fetched primary LME page within this pass. Marked [unverified — search-summary only, not to be cited as a checked fact].
- SHFE Copper hours: "9 AM–11:30 AM and 1:30 PM–3:00 PM China Standard Time" — same caveat, [unverified — search-summary only].
- CME Globex HG copper: "Sunday 6:00 PM ET through Friday 5:00 PM ET, with a brief daily break between 5:00 PM and 6:00 PM ET" — same caveat, [unverified — search-summary only].
- CME gold (GC) settlement window: "13:29:00 to 13:30:00 ET" for the active month — sourced from a WebSearch summary of the CME Group Confluence wiki; the direct fetch of `cmegroup.com/markets/metals/precious/gold.settlements.html` timed out twice (container 8, incomplete) and this figure was NOT independently re-verified via a genuine scrape. Marked [unverified — search-summary only, retrieval incomplete].

These four items need a follow-up fetch (direct or via Wayback) before any design document treats them as checked; they are flagged here rather than silently dropped or silently asserted as verified.

## 5. Flags for K8 (cross-cluster, not read further)

- Source: multiple (general commodity literature, not individually pinned down in this pass) | Item: gold vs. the US dollar / real interest rates as a driver of gold price moves | Legs: gold (K5) and the dollar/rates (K3/K2) | one phrase: "dollar-and-gold relationship, K8's per partition section 3"
- Source: Wright Blogs, "Metals as Macro Signals: Reading Gold, Silver and Copper in a Fragile World" (surfaced in a Databento-container search, not read) | Item: metals used as a macro/cross-asset signal | Legs: metals (K5) and broader macro/cross-asset regime (K8 or K1/K2 depending on the specific pairing) | one phrase: "cross-asset macro-signal framing, not a single-cluster mechanism, not read"

## 6. Sentiment items shelved

- None encountered directly in this pass (no social-media-sentiment-specific K5 item was surfaced by the queries run).

## 7. Registry ids appended by this worker

K5-001, K5-002, K5-003 (superseded — see note), K5-004, K5-005, K5-006, K5-007, K5-008, K5-009,
K5-010.

Note on K5-003: an early registry line `K5-003` was appended for Crain, Hoelscher & Jones (2020)
before the lead's retrieval-standard addendum arrived; K5-006 is the same source, re-registered
after full text was actually obtained. K5-003 and K5-006 are the SAME paper — the lead or the next
reader should treat K5-003 as a duplicate id pointing to K5-006, not a second source. This
duplication is a partitioning/registry-hygiene error on this worker's part, reported rather than
hidden.
