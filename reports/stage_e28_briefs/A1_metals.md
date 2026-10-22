# A1_metals: Layer 1 fact sheets, COMEX metals (MGC, GC, SIL, SI, MHG, HG)

Worker: A1_metals (Opus 5.5), Stage E.28 Part A. Re-spawned after a usage cut; resumed 2026-10-21 05:11 PDT from
the first worker's saved pages (10 files, log.tsv). Facts only; nothing is scored here.
Finished 2026-10-21 05:45 PDT. WebSearch: 20 of 40 calls used; no budget notice seen. JSON twin: A1_metals.json (90 quotes
checked verbatim against the saved files by work/A1_metals/A1_metals_check_quotes.py, 0 misses).

Evidence files: reports/stage_e28_briefs/pages/A1_metals/ (log.tsv holds URL, UTC and PDT fetch times, method,
sha256). Quotes are verbatim from the saved files (PDFs through pdftotext -layout, HTML through a tag stripper,
files `*.html.txt`). Scripts: reports/stage_e28_briefs/work/A1_metals/. No market data was read. Owned-bar
magnitudes (sigma_1m, R_d, owned ADV) belong to A0 and are not computed here.

Route notes: cmegroup.com refuses this machine (Wayback copies used); the CME contract-spec pages in Wayback carry
the spec table only through JavaScript, so spec values come from the COMEX rulebook chapters (Wayback copies), CME
advisories and COMEX filings on cftc.gov. One saved file is unusable: comex_rulebook_ch914_MHG.pdf is a Wayback
HTML error page, not the PDF (kept, marked in this note; MHG specs come from the MHG FAQ and the launch advisory).
cme_dcb_faq.html (dynamic circuit breakers FAQ, Wayback 2024) holds only Wayback chrome, no FAQ text.

## F. Family-wide facts (referenced from each sheet as F1, F2, ...)

### F1. Matching algorithm (CME Globex, outrights)
- Silver and copper futures (SI, SIL, HG, MHG): FIFO. COMEX filing to the CFTC (June 2022), file
  cftc_rule062122comexdcm002_SI_HG_weekly_algo.pdf: "The Rule Amendments are intended to align the CME Globex
  matching algorithm of the Contracts with that of the existing CME Globex matching algorithm of the balance of the
  Exchange's Silver and Copper futures and option contracts." The amendment moved the Monday and Wednesday weekly
  options "from K to FIFO", and "The CME Globex matching algorithm in connection with the Friday Silver and Copper
  Option contracts shall remain unchanged at FIFO." So the balance of silver and copper futures is FIFO (stated by
  reference, not by product code; SIL and MHG are not named).
- Gold (GC): FIFO stated for TAS outrights and, until Oct 2023, TAS calendar spreads. COMEX filing (Sept 2023),
  file cftc_rules0926237018_gold_TAS_algo.pdf: "Upon the implementation of TAS eligibility for the Gold Futures
  contract, the Exchange determined that for both outright and calendar spread transactions, the appropriate CME
  Globex matching algorithm was F- FIFO." and "The CME Globex matching algorithm for Gold Futures TAS outright
  trades will remain unchanged." Gold TAS calendar spreads moved to K-Configurable effective trade date
  2023-10-23. The regular (non-TAS) GC outright and MGC outright algorithm: not stated in any saved file
  [unverified; FIFO is the inference, not a sourced fact].
- Context (Databento, file databento_cme_matching_algos.html.txt): "First in, first out (FIFO) Aggressing orders
  match resting orders at the same price level by time priority until filled. ... Popular products: ES, NQ, ZN,
  ZF, ZB, CL outrights Volume: 70.3%". No metals product is named there.

### F2. Trading hours
- MHG (file cme_chadv22_133R_MHG_launch.txt, CME Clearing Advisory 22-133): "Trading Hours Sunday - Friday 5:00
  p.m. - 4:00 p.m. CT with a 60-minute break each day beginning at 4:00 p.m. CT". MHG FAQ (cme_MHG_faq.html.txt,
  Wayback 2026-07-13): "CME Globex: Sunday - Friday 5:00 p.m. Central Time/CT with a daily maintenance period from
  4:00 p.m. - 5:00 p.m. CT".
- SIL at launch (2013 article, cme_micro_silver_article.txt): "The new contract is designed to replicate the
  established full-size contract in most respects, including trading hours, termination of trading,
  deliverability" (2013 hours were "CME Globex: Sun.-Fri. 6 p.m.-5:15 p.m., with a 45-minute break beginning at
  5:15 p.m." [Eastern], since changed).
- Current GC, SI, HG, MGC, SIL Globex hours: see the hours section added below (searched; result recorded there).

### F3. Automated trading and HFT shares (CFTC Office of the Chief Economist; GC, SI, HG only; micros not covered)
- Haynes and Roberts (2015), "Automated Trading in Futures Markets", file cftc_haynes_roberts_2015.txt, sample
  2012-11-12..2014-10-31, Table 4 (shares of total volume; columns Total Volume (mm), ATS-ATS, ATS-MAN, MAN-MAN):
  "Metals - Precious Gold 85 24.0 43.9 25.5"; "Metals - Base Copper 31 27.5 43.5 26.0"; "Metals - Precious
  Silver 27 27.9 37.0 31.3". Text: "the frequency of trading between automated participants can be as low as 24
  percent (gold) and as high as 72 percent (British pound)."
- Haynes and Roberts, update 2 (2019), file cftc_ats_update2_2019.txt, periods 2014-11-01..2016-10-31 (first
  number) and 2016-11-01..2018-10-31 (second), Table 3 (Total Volume mm, ATS, MAN, ATS-ATS, ATS-MAN, MAN-MAN):
  "Metals - Base Copper 97 61 53.2 70.2 41.3 28.7 31.7 52.2 42.9 36.0 19.8 10.7"; "Metals - Precious Gold 162
  153 65.0 67.6 28.5 28.8 46.1 50.2 37.8 34.8 9.6 11.4"; "Metals - Precious Silver 31 47 54.1 67.1 42.6 30.3
  36.0 51.5 36.2 31.2 24.5 14.7". So in 2016-11..2018-10 automated (ATS) volume share: GC 67.6%, SI 67.1%, HG
  70.2%; both sides automated: GC 50.2%, SI 51.5%, HG 52.2%. Text: "increases in the level of automation were
  largest for metals contracts (54.1 to 67.6 percent automated, a group that includes gold, silver and copper)".
- Small versus large traders (2019 update Table 5; "large volume trader" = at least 0.5% of daily volume; columns
  small N, ATS%, MAN%, large N, ATS%, MAN%, two periods each): "Gold 56,301 49,405 19.4 17.3 26.4 19.3 626 428
  33.7 50.4 14.8 9.5"; "Silver 23,186 21,722 18.1 17.6 20.5 15.5 709 505 35.9 49.5 22.1 14.8". So in
  2016-11..2018-10 small-trader share of volume was GC 36.6% (17.3 + 19.3), SI 33.1% (17.6 + 15.5); large
  automated traders GC 50.4%, SI 49.5%. "Small" is a size class, not retail.
- Passive-side speed (2019 update Table 6, share of two-sided volume by time from order placement or
  modification to execution for the passive side; pairs = two periods; columns 0-100 ms ATS, MAN; 100-500 ms ATS,
  MAN; 500 ms-1 s ATS, MAN; 1-10 s ATS, MAN; 10 s-1 min ATS, MAN; Remaining): "Gold 4.8 8.2 1.3 0.5 3.3 3.7 0.6
  0.3 2.1 2.3 0.5 0.2 8.8 10.8 3.1 1.9 4.5 5.7 2.8 1.9 16.7 13.4"; "Silver 5.0 7.9 0.9 0.4 2.2 2.2 0.3 0.1 1.5
  1.5 0.3 0.1 8.2 8.3 2.1 1.2 6.3 7.5 3.0 2.0 19.7 18.1". In 2016-11..2018-10, 8.2% (GC) and 7.9% (SI) of
  two-sided volume was passive automated volume executed within 100 ms of order entry or modification.
- 2017 update (file cftc_haynes_roberts_2017_update.txt) repeats the 2014-16 numbers above (Gold 162 mm, ATS-ATS
  46.1%).
- Current Globex hours, all COMEX metals (CME Metals Product Guide 2024, file cme_metals_prod_guide_2024.txt,
  "Trading Hours CME Globex: Chicago (Central Time): Sunday – Opens at 5:00 p.m. (for the next trade date) – 4:00
  p.m. the following day. Monday through Friday – Opens at 5:00 p.m. (for the next trade date) – 4:00 p.m. the
  next day. Except on Friday – Closes at 4:00 p.m. and reopens Sundays at 5:00 p.m." The guide adds "Note 1: for
  detailed trading hours by product, please visit cmegroup.com/trading-hours.html#metals" (not reachable here).
  So Globex runs 23 hours a day, Sunday 17:00 CT to Friday 16:00 CT (15:00-14:00 America/Vancouver), with a
  60-minute break 16:00-17:00 CT.
- Later change (outside the pilot window, 2026): CME quarterly metals update Q3 2026 (cme_metals_update_2026-q3)
  for 1-Ounce Gold: "The removal of the 60-minute daily electronic trading break provides uninterrupted risk
  mitigation and liquidity access"; micro metals newsletter Oct 2026 (cme_newsletter_2026-10-...): "Market
  participants can now access 1-Ounce Gold (1OZ) futures and 100-Ounce Silver (SIC) futures) liquidity over the
  weekends as our marketplace goes 24/7 for selected markets." Neither names MGC, GC, SIL, SI, MHG or HG.

### F4. Commercial-hedger and small-trader shares of open interest (CFTC COT, Disaggregated, futures only)
- Files: cftc_fut_disagg_txt_{2022,2023,2025,2026}.zip; script work/A1_metals/A1_metals_cot.py; output
  work/A1_metals/A1_metals_cot_out.txt. Share of a category = (long + short + 2 x spread) / (2 x OI), weekly,
  averaged; [min, max] in brackets. Only report dates inside the window were read for 2022-11..2023-10; the
  "latest 52 weeks" are the last 52 published reports (2025-10-21..2026-10-13).
- Window 2022-11-01..2023-10-31:
  - GC (088691, 53 reports): OI mean 456,983; producer/merchant 6.8%; swap dealers 37.4%; managed money 27.9%;
    other reportables 20.3%; nonreportable 7.6% [6.7, 8.4].
  - SI (084691, 53): OI mean 132,890; producer/merchant 13.8%; swap 31.5%; managed money 29.6%; other 11.0%;
    nonreportable 14.0% [12.3, 16.6].
  - HG (085692, 53): OI mean 201,194; producer/merchant 21.8%; swap 19.4%; managed money 37.3%; other 13.7%;
    nonreportable 7.7% [6.3, 9.6].
  - MGC ("MICRO GOLD", 088695): published in only 13 of the window's weeks (the CFTC prints a market only when
    it meets its reporting thresholds); in those weeks OI mean 29,244; producer/merchant 0.2%; swap 0.0%; managed
    money 2.6%; other reportables 46.8%; nonreportable 50.4% [41.0, 64.5].
  - SIL and MHG: no COT market in 2022 or 2023 files (searched every market name containing GOLD, SILVER,
    COPPER). First appear in 2026 as "MICRO SILVER" (6 reports) and "MICRO COPPER" (3 reports).
- Latest 52 reports (2025-10-21..2026-10-13): GC OI mean 410,422, producer/merchant 7.0%, swap 38.7%, nonrept
  8.5%; SI OI 123,798, producer/merchant 11.0%, swap 35.9%, nonrept 15.9%; HG OI 264,823, producer/merchant
  27.9%, swap 18.7%, nonrept 5.8%; MGC (52 reports) OI 69,367, producer/merchant 0.1%, swap 3.8%, other 50.4%,
  nonrept 45.1%; SIL (6 reports, 2026-01-13..2026-10-13) OI 27,254, nonrept 42.3%, other 57.3%; MHG (3 reports,
  2026-01-27..2026-05-12) OI 15,220, nonrept 44.3%, other 52.0%.
- Caveat: COT shares are shares of open interest held overnight, not of intraday volume.

### F5. Volume and open interest published by CME (product level)
- Window 2022-11..2023-10 (closest published figures):
  - MHG: micro metals newsletter Dec 2022 (cme_newsletter_2022-12-...): "November is the best month for MHG since
    launch with Average Daily Volume of 4,381 contracts and Average Daily Open Interest of 2,122 contracts."
    Newsletter Oct 2023 (cme_newsletter_2023-10-...): "Micro Copper futures (MHG) Q3 ADV of 4,578 contracts".
    Metals Product Guide 2024: "Micro Copper futures ADV grew to 4,882 contracts, an increase of 117% year-
    over-year" (calendar 2023).
  - SIL: newsletter Oct 2023: "Micro Silver futures (SIL) YTD ADV of 10,496 contracts" (2023-01..2023-09).
  - Micro metals combined: Q3 2023 metals update (cme_metals_update_2023-q3): "Combined average daily volume
    (ADV) for Micro Gold, Silver, and Copper futures is 90K contracts, up 39% compared to the same period in
    2022." By subtraction with SIL about 10.5K and MHG about 4.6K, MGC was roughly 75K (derived, not stated).
  - MGC: CME release 2023-09-11 (mondovisione_2023-09-11_MGC_options_retail): "average daily volume in Micro Gold
    futures increasing 40% from last year"; no level given.
  - GC, SI, HG futures ADV for the window: not found in any fetched CME text (searched the 2023 and 2024 metals
    product guides, Q4 2022, Q3 2023 and Q4 2023 metals updates, the micro metals newsletters). Unknown.
- Latest published:
  - Q2 2026 (cme_metals_update_2026-q3): "Micro Gold and 1-Ounce Gold contracts traded 350K and 58K in average
    daily volume (ADV) respectively"; "Benchmark Silver (SI) futures averaged 64K ADV in Q2"; "Micro Silver (SIL)
    futures averaged 74K ADV"; "Benchmark Copper (HG) futures averaged 258K ADOI during the quarter. Micro Copper
    futures are up 76% YTD at the end of Q2, with 25K ADV."
  - Q3 2026 (cme_newsletter_2026-10-...): "Micro Gold, Silver and Copper futures Q3 2026 average daily volume
    (ADV) and average daily open interest (ADOI) reached 404,916 contracts and 103,649 contracts".
  - 2025 calendar year: the CME annual release was not retrievable (barchart reprint returned a bot page; CME IR
    hosts refuse this machine). Search-result text, not fetched [unverified, search snippet only]: record 2025
    ADV of 325,000 Micro Gold and 48,000 Micro Silver; metals ADV 988,000. The fetched Q1 2026 metals update
    (hellenic_cme_q1_2026_metals_update) confirms only the total: "metals volume increase by 35% to a record
    average daily volume (ADV) of 988K contracts".
  - Dec 2025 (cme_newsletter_2025-12-...): "Micro Gold (MGC) futures average daily volume (ADV) reached 475,825
    contracts"; "Micro Silver (SIL) futures ADV was 74,901 contracts". Nov 2025 (Kitco news report of CME monthly
    data, kitco_2025-12-02_retail_cme): "Micro Gold futures ... saw ADV of 476,000 contracts"; "Silver futures saw
    ADV of 108,000 contracts"; "micro silver futures ... saw average volume of 75,000 contracts".
  - GC futures ADV, latest 12 months: not found in fetched text. Unknown. (The CME GC page, fetched via Wayback,
    says only "The world's leading benchmark futures contract for gold trades the equivalent of nearly 27 million
    ounces daily", file cme_GC_specs.html.txt; 27 million oz / 100 oz = about 270,000 GC-equivalent contracts a
    day, but the sentence may count all gold contracts in GC equivalents; snapshot 2025-12-28.)

### F6. Retail and participant statements (CME)
- CME release 2023-09-11 (mondovisione_2023-09-11_MGC_options_retail), headline "CME Group To Launch Options On
  Micro Gold Futures As Retail Participation Jumps"; quote of CME's Global Head of Metals: "Growing demand has
  driven a spike in CME Group gold markets, with average daily volume in Micro Gold futures increasing 40% from
  last year and retail participation in our benchmark Gold futures contract up 17% year-over-year." Also "30% of
  trading volume in our gold markets now occurs during non- U.S. trading hours". No retail share is given.
- Q3 2026 metals update: "led primarily by our active trader-friendly suite: Micro Gold and 1-Ounce Gold".
- MGC launch release 2010 (mondovisione_2010_MGC_launch): "The E-micro gold contract is one-tenth the size of the
  benchmark 100-oz" and trades "exclusively" on Globex.
- SIL launch release 2013 (mondovisione_2013_SIL_launch): the smaller size will "serve as a more cost-effective
  tool for individual investors"; the 2013 article (cme_micro_silver_article): "The CME Group's new, smaller
  silver futures contract was designed with smaller traders in mind."
- No CME or regulator figure for the retail share of volume was found for any of the six products.
- Kitco headline (news, pointer only): "Retail investors are in the driver's seat in gold and silver, according
  to CME" (2025-12-02).

### F7. Market-maker and incentive programs (COMEX filings to the CFTC)
- MHG: "Micro Copper Market Development Program" (cftc_rule041422comexdcm011_MHG_MDP.txt; modified by
  cftc_rules01162410870_MHG_MDP_mod2024.txt): "Product Scope Micro Copper Futures ("MHG") traded on the CME Globex
  Platform"; "Program Term Start date is May 1, 2022. End date is January 31, 2024 January 31, 2025." (the 2024
  modification shows the old end date struck and the new one underlined); "Hours 7:00AM – 12:00PM CT ("RTH") and
  5:00PM to 7:00AM CT ("ETH")"; "Obligations Participants must meet certain volume thresholds and quote continuous
  two-sided markets in the Product at designated bid/ask spreads and quote sizes during a specified percentage of
  time-in-market." So a quoting program covered the whole pilot window 2023-11..2024-02.
- SIL: "Korea Retail FCM Micro Silver Rebate Program" (cftc_rules07162610546_Korea_retail_SIL_rebate.txt, COMEX
  Submission 26-312): "Micro Silver Futures ("SIL") that are traded on the CME Globex Platform"; open to
  non-members "(i) located in Korea, and (ii) registered with the Exchange as a retail brokerage firm"; "Start date
  is November 1, 2022. End date is July 31, 2026 July 31, 2028"; "Participants must meet certain volume thresholds
  in the Product". A volume rebate for retail brokers (it routes retail flow), not a quoting program.
- MGC: "E-micro Gold Futures Market Maker Program on Globex" (cftc_rul101311comex002_MGC_MM_2011.txt): "Start date
  is October 4,2010. End date is Ootober 31,2011 March 31, 2-G-142012" [OCR as printed; extended to March 31,
  2012]. Whether any MGC futures quoting program ran in 2023-24: not found. A "Micro Gold Options Market Maker
  Program" exists (cftc_rules0914236526_MGC_options_MM.txt, "The Program will become effective on October 1,
  2023"), for options on MGC, not the futures.
- GC: "Gold (Enhanced Delivery) Futures Market Maker Program" (cftc_rule032720comexdcm001.txt), "Start date is
  April 13, 2020. End date is September 30, 2020." It covers a different contract (enhanced delivery), not GC.
  Search-result text only [unverified]: Asia-Pacific Incentive Program filings 2011-2014 gave Asian banks a
  Globex fee discount covering COMEX Gold and Copper futures; no 2023 term found.
- SI, HG futures: no market-maker program found within the search budget. Fee waiver at MGC launch (search
  snippet of CME SER-5391R [unverified]): fees waived for six months from October 2010.

### F8. Spread and depth at the best level (published sources only; none for the micros)
- GC and SI, CME article "Liquidity of COMEX Gold & Silver is Excellent" (cme_liquidity_gold_silver_asia_hours,
  Wayback 2025-10-16; figures use 2017-Q1 2018 data, by its text "in the first quarter of 2018"): "The gold market
  exhibited tight bid/ask spread of one tick during almost all trading hours. The average bid/ask quantity was also
  robust; while it tends to be higher during U.S. peak hours, the average quantity during Asia hours is healthy,
  ranging from 15 to 24 lots"; "Like Gold Futures, bid/ask spread of Silver Futures is also tight at one tick wide
  most of the hours. Bid/ask quantity is at its highest during U.S. trading hours; nevertheless, it is still decent
  during Asia hours, ranging from 22 lots to 27 lots"; "the bid-ask spread at the best prices are consistently 1
  tick wide for both gold and silver futures, and even when comparing the fifth best bid verses fifth best ask
  prices, the spread is only 9 ticks wide during Asia hours." The U.S.-hours values are in figures only (images,
  not in the text). Same article: "In 2012, around 190,000 lots a day of Gold futures were traded ... increased to
  380,000 lots and 35% respectively in the first quarter of 2018. For Silver futures, liquidity has hugely improved
  from around 55,000 lots ADV in 2012 to more than 100,000 lots in the first quarter of 2018."
- GC and SI, Richards, Peters and Dunsmuir, "Heavy-tailed features and dependence in limit order book volume
  profiles in futures markets", Quantitative Finance (to appear 2015), arXiv 1210.7215v2 (file
  arxiv_1210.7215_LOB_volume_profiles_futures.txt), 250 trading days of 2010, window "06:30:00 to 13:30:00"
  (GOLD) and "08:30:00 to 13:00:00" (SILVER), Table 2 "Descriptive statistics for all trading days for 2010, using
  sub-sample data for level one of the LOB": "GOLD Bid 172.96 1 4.62 6.78 8.66 139.65 7.61 / Ask 206.85 1 4.62
  6.80 9.64 184.71 8.74"; "SILVER Bid 79.17 1 6.56 7.83 6.39 46.77 3.63 / Ask 76.02 1 6.56 7.81 6.30 38.63 3.38"
  (columns Max, Min, Median, Mean, Std, Kurtosis, Skew). So level-1 median displayed size was 4.62 contracts (GC)
  and 6.56 (SI) in 2010.
- HG, MGC, SIL, MHG: no published spread, depth, touch-queue or volume-per-minute figure found (searched CME
  articles and newsletters, OpenAlex, WebSearch). Unknown. Traded volume per minute: not published anywhere found.
- Gold options aside (not in scope): Q4 2022 metals update says copper options "Book Size outside RTH has shown
  exceptional growth, with up to 30 lots markets at the top of book" (options, not futures).

### F9. Daily price limits and circuit breakers (COMEX Rule 589)
- Rulebook chapters for all five COMEX contracts in hand (GC 113, SI 112, HG 111, MGC 120, SIL 121) say: "At the
  commencement of each trading day, the contract shall be subject to special fluctuation limits as set forth in
  Rule 589 and in the Special Price Fluctuation Limits Table". MHG FAQ: "Micro Copper Futures utilize dynamic
  price limits (circuit breakers)."
- Dynamic limits since 2019 (cftc_ptc031819_dynamic_limits_2019.txt): "Application of Dynamic Price Fluctuation
  Limits to Various NYMEX Energy and NYMEX and COMEX Metals Contracts", "effective on Sunday, March 31, 2019, for
  trade date Monday, April 1, 2019"; the table lists GC, "E-micro Gold Futures ... MGC", SI, "1,000 oz. Silver
  Futures 121 SIL", HG.
- Mechanics and level (cftc_ptc032320comex_DCB_5to10pct.txt, effective trade date 2020-04-06): GC, SI and HG are
  "Primary"; MGC (Associated, GC), SIL (Associated, SI) and the copper associates follow their primary. "the
  Exchanges are increasing the special price fluctuation limits from 5% to 10% in light of recent market
  volatility." Rule text: "the dynamic variant shall be applied in rolling 60-minute look-back periods to establish
  dynamic lower and upper price fluctuation limits"; a trade, bid or offer through the limit is "a triggering event
  that will begin a two (2) minute monitoring period"; "a two (2) minute temporary trading halt" follows if still at
  the limit. No hard daily limit-lock exists for these contracts (none appears in any saved rule text).
- Limit-hit or halt days 2019-2024: none found for GC, SI, HG or the micros (searched WebSearch and CME/CFTC
  filings; CME does not publish a halt log that I could reach). Unknown, not "zero". Outside the window: a COMEX
  copper halt after the July 2025 tariff announcement (Reuters reprint, title and date only, body login-gated:
  "Copper trade on Comex halted Wednesday after tariff-related price plunge Reuters 2025/08/01", file
  itiger_reuters_2025_copper_halt.html.txt); the search snippet [unverified] said it was the second copper trigger
  in under a month.

### F10. Scheduled product-specific releases, weekend gaps, jumps
- Releases: no weekly product-specific government report exists for these metals in any fetched source (unlike EIA
  for energy). CME's own metals calendar lists only macro events: the Oct 2026 micro metals newsletter "Key
  Economic Events" are "U.S. ISM Manufacturing PMI; U.S. Non Farm Payrolls; FOMC Minutes; China Balance of Trade;
  U.S. Inflation Numbers; China Industrial Production YoY; Fed Interest Rate Decision and Fed Press Conference; U.S.
  Core PCE Price Index; China NBS Manufacturing PMI; RatingDog Manufacturing PMI" (all monthly or less frequent).
  Elder, Miao and Ramchander (J. Banking & Finance 2012; repository copy csu_elder_miao_ramchander_metal_futures_
  news.txt, "This version: June 7, 2011"): "the response of metal futures to economic news surprises is both swift
  and significant, with the 8:30 am set of announcements – in particular, nonfarm payrolls and durable goods orders
  – having the largest impact". So the shared US macro calendar (excluded by C4) is the main scheduled driver.
- Weekend gaps: Globex closes Friday 16:00 CT and reopens Sunday 17:00 CT (F2). The underlying OTC spot metals
  markets are not documented in any fetched file; that they are closed at weekends is [unverified]. In 2026 (after
  the pilot window) CME made 1-Ounce Gold and 100-Ounce Silver tradable at weekends (F2), which creates weekend price
  discovery in the gold and silver complex from 2026 on; none of the six candidates is named as weekend-traded.
- Jumps: Sobti (EFMA 2024 paper, efma2024_sobti_gold_jumps.txt), COMEX gold futures, 5-minute data 2010-01-01..
  2018-03-31: "the total number of jumps days for COMEX gold futures is 664 and the probability of having a jump day
  is 32.15% for COMEX"; "COMEX gold futures has 1101 intraday jump observations, of which it has greater number of
  negative jumps (562) while only 539 are positive jumps"; "US scheduled macroeconomic news is the most dominant
  predictor of intraday price jumps and co-jumps." These are intraday jump tests, not the C4 count of days with
  |daily return| > 4 daily SD; that count for 2019-2024 was not found published for any of the six. Unknown.

### F11. Published microstructure research (C6 evidence)
Search: 20 WebSearch calls in all (of 40), OpenAlex (5 queries, work/A1_metals/A1_metals_openalex_out1.txt), arXiv API
(4 failed queries, 1 working query on "gold futures"). Findings, with relation to product and result:
1. Iwatsubo, Watkins and Xu, "Intraday Seasonality in Efficiency, Liquidity, Volatility and Volume: Platinum and
   Gold Futures in Tokyo and New York", Kobe University DP 1722 (2017), published J. Commodity Markets 2018 (file
   kobe_2017_intraday_seasonality_platinum_gold_futures.txt). Data: "1-minute intraday bid and ask futures prices
   ... for gold are from COMEX", "128 trading days from 1 September 2014 to 31 March 2015"; efficiency measured by
   "Lo and MacKinlay's (1988) variance ratio". Result: "both platinum and gold markets in Tokyo are dominated by
   uninformed trading, while there is evidence supporting both uninformed and informed trading in New York"; "The
   mean and median variance ratio statistics for both platinum and gold are lower in New York than Tokyo, suggesting
   that the New York markets are more efficient on average." Relation: same product (GC). Result: not an
   order-book predictability test; 1-minute efficiency, mixed (no profitable pattern shown). Counts as neither
   positive nor negative order-book evidence.
2. Richards, Peters and Dunsmuir (QF 2015, arXiv 1210.7215; F8): GC and SI level-1 to level-10 volume profiles,
   2010. Relation: same product (GC, SI). Result: descriptive (heavy-tailed queue sizes); no predictability test.
3. Haynes and Roberts (CFTC 2015, 2017, 2019; F3): automated shares and passive-order speeds by contract (GC, SI,
   HG). Relation: same product. Result: descriptive; no predictability or profitability test.
4. Elder, Miao and Ramchander (JBF 2012; F10): news impact on GC, SI, HG returns, volatility and volume, 2002-2008.
   Relation: same product. Result: descriptive event study; not order-book.
5. Sobti (EFMA 2024; F10): intraday jumps in COMEX gold 2010-2018. Relation: same product. Not order-book.
6. Forecast-to-Fill (arXiv 2511.08571, 2025, not peer reviewed; file arxiv_2511.08571_forecast_to_fill_gold.txt):
   "a smoothed trend–momentum regime signal" on gold futures, "Out-of-sample, the strategy delivers a Sharpe ratio
   of 2.88". Relation: same product (CME gold). Result: positive claim, but daily trend/momentum, not order-book or
   short-horizon; unrefereed.
7. Not found for any of the six: a study of order-flow imbalance, queue imbalance, trade-sign predictability or
   net-of-cost passive market-making profitability on COMEX metals futures. Closest asset-class-wide evidence seen
   only as search-result text [unverified, snippet only]: a 2018 Agricultural Finance Review study on CME grain and
   livestock futures found "for some contracts, returns can be predicted using lagged order imbalance" (futures
   broadly, not metals). Not retrieved: Bhanot, Martinez, Ning and Tse (2008 UTSA WP, COMEX gold and silver market
   quality on Globex; three curl attempts timed out); JRFM 2021 "Volatility and Depth in Commodity and FX Futures
   Markets" (MDPI 403); FIU 2013 thesis "Three Essays on Market Depth in Futures Markets" (bot page). These may hold
   relevant depth facts and were not read.
   MDPI refused curl (403) for the PDF and HTML, and its robots.txt also returned "Access Denied", so its terms
   could not be checked; Scrapling was therefore not used on mdpi.com (rule: terms check before Scrapling).

### F12. Listing continuity through the pilot window 2023-11-01..2024-02-29 (no market data read)
- All six were listed before 2023-11: GC, MGC, SI, SIL, HG appear in the COMEX dynamic-limits filing effective
  2019-04-01 and the 5%-to-10% filing effective 2020-04-06 (F9); MHG first traded on trade date 2022-05-02 (MHG
  sheet). Continuity evidence: the SIL rulebook chapter has the same Wayback content digest from 2022-07-06 to
  2024-06-19 (CDX listing, work/A1_metals; digest CIZZRDQXLB3UH4H44DXL42MFWZOP6XQX), the MHG quoting program ran to
  2025-01-31 (F7), CME's micro metals newsletters exist for each month 2023-11..2024-02 (Wayback CDX listing,
  work/A1_metals/A1_metals_cdx_micro_metals.txt; not read), and the CFTC printed GC, SI and HG every week of 2023
  (52 rows each in the 2023 file; a row count only). No source suggests any of the six was suspended in the window.
  Whether each traded on at least 60 Globex dates in the window is inferred from listing plus the ADV levels in
  F5 (SIL about 10.5K, MHG about 4.6K a day in 2023), not counted.

## Candidate fact sheets

### MGC: Micro Gold futures (COMEX, Globex code MGC)
- Name: "Micro Gold Futures 120 MGC" (cftc_ptc032320comex_DCB_5to10pct.txt); originally "E-micro Gold".
- Contract size: "The contract unit shall be ten (10) troy ounces." Tick: "The minimum price fluctuation shall be
  ten cents ($0.10) per troy ounce." (comex_rulebook_ch120_MGC.txt). Tick value 10 x 0.10 = $1.00 (derived).
- Launch: "Globex to begin trading on October 3 for trade date October 4" (2010; mondovisione_2010_MGC_launch);
  CFTC self-certification (cftc_rul092410_comex_MGC_selfcert.txt): "contract for trading onCME Globexeffective Sunday,
  OctoberS; 2010 for trade date Monday, October4," (OCR as printed; read: October 3 and October 4, 2010). Pilot-window trading: F12.
- Matching: not stated in any saved file (F1) [unverified].
- Hours: F2 (Globex 17:00-16:00 CT Sun-Fri, 60-minute break).
- Limits: Associated contract of GC under Rule 589 dynamic limits, 10% rolling 60-minute since 2020-04-06 (F9).
  Limit-hit days 2019-2024: unknown (F9).
- ADV and OI: window 2022-11..2023-10: level not published in fetched text; about 75K derived by subtraction from
  "Combined ... 90K" in Q3 2023 (F5); COT OI mean 29,244 over the 13 printed weeks (F4). Latest: Q2 2026 ADV 350K;
  Dec 2025 ADV 475,825; COT OI mean 69,367 over the last 52 reports (F4, F5).
- Participants: COT nonreportable 50.4% of OI (window, 13 weeks), 45.1% (latest 52); producer/merchant 0.2% and
  0.1%; swap 0.0% and 3.8% (F4). Retail: CME calls it part of its "active trader-friendly suite" (F6); no share
  figure. Automated share: not covered by the CFTC studies (GC only).
- Market-maker programs: E-micro Gold futures market maker program 2010-10-04..2012-03-31 (F7); no futures program
  found for 2023-24; a Micro Gold OPTIONS market maker program from 2023-10-01 (F7).
- Spread, depth, queue, volume per minute: none published (F8). Unknown.
- Releases, weekend gap, jumps: F10 (no product-specific weekly release; Globex weekend closure; gold jump study on
  GC 2010-2018).
- Research: none on MGC itself; GC studies apply as the full-size version on the same underlying (F11).

### GC: Gold futures (COMEX, GC)
- Contract size: "The contract unit shall be one hundred (100) troy ounces." Tick: "The minimum price fluctuation
  shall be ten cents ($0.10) per troy ounce." (comex_rulebook_ch113_GC.txt). Tick value $10.00 (derived).
- Launch date: not sourced (listed in the 2019 and 2020 filings; F12).
- Matching: TAS outrights F-FIFO; regular outright FIFO not stated in a saved file (F1).
- Hours F2. Limits: Primary contract, Rule 589 dynamic 10% (F9); limit-hit days 2019-2024 unknown.
- ADV: window: not found. Latest: not found (CME page: "trades the equivalent of nearly 27 million ounces daily",
  snapshot 2025-12-28, F5). Historical: "380,000 lots" ADV in Q1 2018 (F8 article). CFTC 2016-11..2018-10 total
  volume 153 million contracts (F3).
- OI: COT mean 456,983 (window), 410,422 (latest 52) (F4).
- Participants: COT producer/merchant 6.8%, swap dealers 37.4%, managed money 27.9%, other 20.3%, nonreportable 7.6%
  (window) (F4). CME: "retail participation in our benchmark Gold futures contract up 17% year-over-year" (2023,
  F6), no level. Automated: 67.6% of volume ATS, 50.2% ATS-ATS (2016-11..2018-10); small traders 36.6% of volume;
  8.2% of two-sided volume was passive automated volume filled within 100 ms (F3).
- Market-maker programs: none found for GC itself (F7; the 2020 program covered Gold Enhanced Delivery futures).
- Spread and depth: "tight bid/ask spread of one tick during almost all trading hours"; Asia-hours best-level
  quantity "15 to 24 lots" (2017-18 data, F8); 2010 level-1 median 4.62 contracts (F8). Volume per minute: none.
- Releases, weekend gap, jumps: F10. Sobti: 664 jump days of 2010-2018 (32.15%), 1101 intraday 5-minute jumps.
- Research: F11 items 1-6 (same product; none tests order-book predictability).

### SIL: Micro Silver futures (COMEX, SIL; 1,000 troy ounces)
- Name: "Micro Silver Futures 121 SIL" (2020 filing); "1,000 oz. Silver Futures 121 SIL" (2019 filing).
- Contract size: "The contract unit shall be one thousand (1,000) troy ounces." Tick: "The minimum price fluctuation
  shall be one half of one cent ($0.005) per troy ounce for outright transactions" (comex_rulebook_ch121_SIL.txt,
  2025 snapshot; same text in the 2021 snapshot, comex_rulebook_ch121_SIL_2021snap.txt, and the 2024-05-15
  snapshot, comex_rulebook_ch121_SIL_2023snap.txt). Tick value 1,000 x 0.005 = $5.00 (derived). At launch in 2013
  the outright tick was "$0.01 per troy ounce ($10)" (cme_micro_silver_article.txt); changed by 2021.
- Launch: "scheduled to begin trading in June 2013" (mondovisione_2013_SIL_launch); article: "begins trading on
  June 15" (cme_micro_silver_article.txt; year 2013 from context [the article's own date is not printed]).
- Matching: FIFO by reference to "the balance of the Exchange's Silver and Copper futures" (F1); SIL not named.
- Hours F2. Limits: Associated contract of SI, Rule 589 dynamic 10% (F9). Limit-hit days unknown.
- ADV: window: "Micro Silver futures (SIL) YTD ADV of 10,496 contracts" (2023-01..09; F5). Latest: Q2 2026 74K;
  Dec 2025 74,901; Nov 2025 about 75,000 (F5). OI: no COT market in the window; 2026 COT OI mean 27,254 (6 reports).
- Participants: COT (2026 only) nonreportable 42.3%, other reportables 57.3%, commercial about 0% (F4). Retail: 2013
  launch aimed at "individual investors" and "smaller traders" (F6). Korea retail-broker volume rebate program since
  2022-11-01 (F7). No retail share figure.
- Market-maker programs: none found for SIL (only the Korea retail volume rebate) (F7).
- Spread, depth, queue, volume per minute: none published (F8). Unknown.
- Releases, weekend gap, jumps: F10 (no silver jump study found).
- Research: none on SIL; SI items in F11 apply as the full-size version.

### SI: Silver futures (COMEX, SI; 5,000 troy ounces)
- Contract size: "The contract unit shall be five thousand (5,000) troy ounces." Tick: "The minimum price fluctuation
  shall be $0.005 per troy ounce for outright transactions" (comex_rulebook_ch112_SI.txt). Tick value $25.00
  (derived).
- Launch date: not sourced (listed in 2019 and 2020 filings, F12).
- Matching: FIFO (F1, silver futures by reference). Hours F2. Limits: Primary, Rule 589 dynamic 10% (F9).
- ADV: window: not found. Latest: Q2 2026 "Benchmark Silver (SI) futures averaged 64K ADV"; Nov 2025 108,000 (Kitco
  report of CME data) (F5). Historical: "more than 100,000 lots in the first quarter of 2018" (F8).
- OI: COT mean 132,890 (window), 123,798 (latest 52) (F4).
- Participants: COT producer/merchant 13.8%, swap 31.5%, managed money 29.6%, other 11.0%, nonreportable 14.0%
  (window) (F4). Automated 67.1% of volume, ATS-ATS 51.5% (2016-11..2018-10); small traders 33.1%; 7.9% passive
  automated within 100 ms (F3). In 2012-14 "manual participation in spread trading peaks across the identified
  commodities at 86 percent in silver" (cftc_haynes_roberts_2015.txt).
- Market-maker programs: none found for SI futures (F7).
- Spread and depth: "tight at one tick wide most of the hours"; Asia hours "22 lots to 27 lots" (2017-18, F8); 2010
  level-1 median 6.56 contracts (F8).
- Releases, weekend gap, jumps: F10. Research: F11 items 2-4 (same product, descriptive only).

### MHG: Micro Copper futures (COMEX, MHG; 2,500 lb)
- Name and codes: "Micro Copper Futures MHG MHG CX MHG" (clearing, Globex, SPAN codes; cme_chadv22_133R_MHG_launch.txt).
- Contract size "Product Size 2,500 pounds"; tick "Minimum Price Increment 0.0005"; "Value Per Tick / Currency 2,500
  x 0.0005 = $1.25" (advisory 22-133). FAQ table: "2,500 pounds", "$0.0005 per pound", "$1.25 per contract".
  Financially settled: "Delivery Financially settled" (advisory); "there is no available trading in the
  current/spot month" (FAQ).
- Launch: "Listing Date Trade Date Monday, May 2, 2022" (advisory 22-133); "A Micro Copper futures contract was
  launched in May 2022" (metals product guide 2023).
- Matching: FIFO by reference to the balance of copper futures (F1); MHG not named.
- Hours: "Sunday - Friday 5:00 p.m. - 4:00 p.m. CT with a 60-minute break each day beginning at 4:00 p.m. CT".
- Limits: "Micro Copper Futures utilize dynamic price limits (circuit breakers)." (FAQ); the HG copper complex is
  under Rule 589 dynamic 10% (F9). Limit-hit days 2019-2024 unknown; HG halts in July 2025 (F9).
- ADV: Nov 2022 4,381 (ADOI 2,122); Q3 2023 4,578; calendar 2023 4,882 (F5). Latest: Q2 2026 "25K ADV". OI: COT
  2026 mean 15,220 (3 reports).
- Participants: COT 2026 only: nonreportable 44.3%, other reportables 52.0%, producer/merchant 1.0% (F4). No retail
  figure.
- Market-maker program: Micro Copper Market Development Program 2022-05-01..2025-01-31 with quoting obligations
  ("quote continuous two-sided markets ... at designated bid/ask spreads and quote sizes"), RTH 07:00-12:00 CT and
  ETH 17:00-07:00 CT (F7). Covers the pilot window.
- Spread, depth, queue, volume per minute: none published. Unknown.
- Releases, weekend gap, jumps: F10. Research: none on MHG; HG items apply as the full-size version.

### HG: Copper futures (COMEX, HG; 25,000 lb)
- Contract size: "The contract unit shall be twenty-five thousand (25,000) pounds." Tick: "Prices shall be quoted in
  multiples of five one-hundredths of one cent per pound." (comex_rulebook_ch111_HG.txt), i.e. $0.0005/lb, tick
  value $12.50 (derived; the MHG FAQ table gives "$12.50 per contract" for Copper futures).
- Launch date: not sourced (listed in 2019 and 2020 filings, F12).
- Matching: FIFO (F1, copper futures by reference). Hours F2. Limits: Primary, Rule 589 dynamic 10% (F9); 2025
  halts outside window (F9).
- ADV: window: not found. Latest: not found as ADV; Q2 2026 "Benchmark Copper (HG) futures averaged 258K ADOI"
  (F5). CFTC 2016-11..2018-10 total volume 61 million contracts (F3).
- OI: COT mean 201,194 (window), 264,823 (latest 52) (F4).
- Participants: COT producer/merchant 21.8% (the highest commercial share of the six), swap 19.4%, managed money
  37.3%, other 13.7%, nonreportable 7.7% (window) (F4). Automated 70.2% of volume, ATS-ATS 52.2% (2016-11..2018-10)
  (F3). CFTC 2015 text: "Physical commodity futures trading often has a higher level of both buy- and sell-side end
  users" (preceded by "the physical commodity classes, encompassing energy, metals and agricultural products like oil,
  copper and wheat", and followed by "who consume and produce these goods, and often trade on a manual basis.";
  cftc_haynes_roberts_2015.txt lines 272-277).
- Market-maker programs: none found for HG (Asia-Pacific bank fee discount 2011-2014 per search snippet only, F7).
- Spread, depth, queue, volume per minute: none published. Unknown.
- Releases: no weekly product-specific release; China macro data appear in CME's metals calendar (F10).
- Research: F11 items 3-4 (same product, descriptive only).
