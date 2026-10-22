# A1_rates: Layer 1 fact sheets, rates family (2YY, 5YY, 10Y, 30Y; ZT, ZF, ZN, ZB)

Worker: A1_rates (Opus 5.5), Stage E.28 Part A, started 2026-10-21 05:31 PDT. Facts only; no scoring.
All source files are under reports/stage_e28_briefs/pages/A1_rates/ (log: log.tsv there, with URL, UTC and PDT
fetch times, method and sha256). Quotes are verbatim from the saved files (PDFs read through `pdftotext -layout`,
files `*.pdf.txt`; HTML through a tag stripper, files `*.html.txt`; whitespace runs collapsed in quotes). No market
data was read. Owned-bar magnitudes (sigma_1m, R_d, owned ADV, owned jump counts) for ZT, ZF, ZN, ZB belong to A0
(reports/stage_e28_briefs/A0_contract_stats.md); A0 has no owned bars for 2YY, 5YY, 10Y, 30Y (A0 line 211).

Route notes: cmegroup.com refuses this machine (known block), so CME rulebook chapters, SERs, the Rule 589 table and
the CME monthly ADV and open-interest reports were taken from Wayback raw captures (`id_` URLs; the capture
timestamp is given with each). CBOT submissions to the CFTC were fetched from cftc.gov directly. CFTC Commitments of
Traders data came from the CFTC public reporting API (publicreporting.cftc.gov, dataset gpe5-46if, Traders in
Financial Futures, futures only). Wayback answered "Temporarily Offline" intermittently; a retry wrapper refetched.
No Scrapling or Firecrawl call was needed so far.

## F. Family-wide facts (referenced from each sheet as F1..F9)

### F1. Two different product designs

- ZT, ZF, ZN, ZB are physically delivered Treasury futures priced in points and 32nds of par, quarterly
  (March-June-September-December) expiries, deliverable baskets of Treasury notes/bonds (CBOT rulebook chapters 21,
  20, 19, 18).
- 2YY, 5YY, 10Y, 30Y are cash-settled futures priced directly in yield, "Cash-Settled to BrokerTec benchmark"
  (cftc_ptc072921cbotdcm001.pdf.txt, Exhibit 1), monthly expiries with "2 Nearest Monthly Contracts", and they
  "settle to the most recently auctioned On-the-Run CUSIP at each tenor, which updates monthly and the expectation is
  that the front contract month will dominate trading, with a second contract month listed mainly for roll activity"
  (same file, Section 1). Listed "effective on Sunday, August 15, 2021, for trade date Monday, August 16, 2021"
  (same file). Rulebook chapters 80 (2YY), 81 (5YY), 82 (10Y), 83 (30Y) (same file, table).
- A rising yield is a falling Treasury futures price: the micro yield contracts move opposite in sign to ZT..ZB.
- Contract titles: CBOT dropped "Micro" from the four titles "Effective Monday, February 5, 2024" (CBOT Submission
  No. 24-116, cftc_rules02132411742.pdf.txt: "Effective Monday, February 5, 2024, the Exchange implemented
  administrative amendments to the contract title of all Micro Yield futures contracts"). The Rule 589 table (F3)
  and the CME ADV reports (F5) list them as "2-Year Yield Futures" / "2Y YIELD" and so on. Codes unchanged.

### F2. CME Globex matching algorithms

- Micro yields: "F - FIFO" in the Exhibit 2 cell labelled CME GLOBEX MATCHING ALGORITHM (cftc_ptc072921cbotdcm001.pdf.txt).
- ZT (2-Year): CFTC Office of the Chief Economist, EFFECT OF MATCHING ALGORITHM CHANGES (title page), March 2019
  (cftc_two_year_analysis_2019.pdf.txt): "The 2Y Treasury contract is traded using a partial pro-rata matching
  algorithm." and "For a few days in May of 2015, the 2Y Treasury contract unexpectedly defaulted to a pure FIFO
  algorithm, matching the other Treasury contracts' algorithms". Databento, "CME matching algorithms explained"
  (datePublished 2025-08-01; databento_cme_matching_algorithms.html.txt) lists under "Configurable": "Popular CME
  products: ZT, ZQ, ZC, ZS, ZW outrights", and under FIFO: "Popular products: ES, NQ, ZN, ZF, ZB, CL outrights".
  History: CME Globex notice of 2008-06-16 (cme_globex_notice_20080616.html.txt): the Split FIFO/Pro Rata (K)
  "algorithm was only applied to the 2-Year U.S. Treasury Note futures" and "Only the 2-Year Treasury Note futures
  have a FIFO" allocation at the third step. The exact current ZT outright parameters (TOP order, pro-rata share,
  minimum allocation) were not found: CBOT Rule 580 points to the GCC Product Resources page (cbot_rulebook_I_5.pdf.txt:
  "Information concerning the matching algorithm applicable to a particular product is set forth on the GCC Product
  Resources page"), which is on the blocked cmegroup.com domain.
- ZF, ZN, ZB outrights: FIFO (CFTC 2019 quote above: "the other Treasury contracts' algorithms" are pure FIFO;
  Databento list above). Cousin confirmation: the Ultra 10-Year (TN) listing filing, CBOT 2015
  (cftc_ptc122315cbotdcm001.pdf.txt): "Trade Matching F: FIFO for outright transactions" and "K: Split FIFO/Pro
  Rata, with settings of 20% FIFO and 80% Pro Rata for calendar spreads."
- Treasury calendar spreads (all tenors): since trade date 2014-10-06 "The allocation mix of the Trade Matching
  Algorithms for 2-Year, 3-Year, and 5-Year Treasury Note futures calendar spreads will be changed from 100%
  Pro-Rata to 20% First In First Out (FIFO)/80% Pro-Rata" (CBOT Submission 14-348, cftc_ptc102314cbotdcm011.pdf.txt;
  SER-7193, cme_SER-7193.html.txt). SER-8867 (2021, cme_SER-8867.pdf.txt): "Modification of Residual Allocation
  Step in All Treasury Futures Calendar Spreads".
- Implied liquidity: Treasury inter-commodity spreads (for example the TUF, ZT vs ZF) imply into the outright books
  (CME client wiki, cme_wiki_matching_algorithms.html.txt: "a source composed of a TUF 05-04 and ZF contributes an
  implied OUT to ZT"). The ZT..ZB outright books therefore carry implied orders from spreads.

### F3. Price limits: CBOT Rule 589 dynamic circuit breakers (no fixed daily limit found)

- Each chapter: "At the commencement of each trading day, the contract shall be subject to special price fluctuation
  limits as set forth in Rule 589 and in the Special Price Fluctuation Limits Table" (ZB 18102.D, ZN 19102.D,
  ZF 20102.D, ZT 21102.D; micro yields 80102.D..83102.D).
- Rule 589.D (cbot_rulebook_I_5.pdf.txt, Wayback capture 2025-04-11): a "dynamic variant" equal to a percentage of
  the prior settlement "or a price deemed appropriate by the GCC" is "applied in rolling 60-minute look-back
  periods"; a trade, bid or offer beyond the dynamic limit "shall be considered a triggering event which shall begin
  a two (2) minute temporary trading halt".
- Table (cme_special_price_fluctuation_limits.xlsx, Wayback capture 2024-10-01, sheet "Interest Rates", column
  "Dynamically Calculated Variant - All Hours"): ZT "0.75 of 1 point"; ZF "1.50 points"; ZN "2.00 points"; ZB
  "4.50 points"; 2YY, 5YY, 10Y, 30Y "20 basis points" each. Same 20 bp variant in the 2021 listing filing
  (cftc_ptc072921cbotdcm001.pdf.txt, Appendix D: "Micro 10-Year Yield Futures 82 10Y Primary Primary 20 basis
  points"). The table's "DAILY PRICE LIMIT" column holds only a link label ("Daily Price Limit Table") for these rows;
  no fixed daily limit value for Treasury or yield futures was found.
- Limit-hit (halt) days 2019-2024: see F8.

### F4. Trading hours

- Micro yields (cftc_ptc072921cbotdcm001.pdf.txt, Exhibit 2): "CME Globex: Sunday - Friday 6:00 - 5:00 p.m. ET
  (5:00 - 4:00 p.m. CT). Monday - Thursday 5:00 - 6:00 p.m. ET (4:00 - 5:00 p.m. CT) daily maintenance period".
- Treasury futures: the CBOT Treasury options filing of 2023 (cftc_ptc1005237330.pdf.txt, Monday weekly options on
  ZT, ZF, ZN, ZB and others) gives "CME Globex: Sunday 5:00 p.m. - Friday - 4:00 p.m. CT with a daily maintenance
  period from 4:00 p.m. - 5:00 p.m. CT". This quote is for the options on these futures; the futures' own spec page
  is on the blocked cmegroup.com domain and its Wayback copy carries spec values only through JavaScript. The Micro
  Ultra Treasury filing (cftc_ptc02232412041.pdf.txt, 2024) gives the same schedule for its cousin futures: "CME
  Globex: Sunday - Friday 5:00 p.m.-4:00 p.m. CPT with a 60-minute break" ... "each day beginning at 4:00 p.m. CPT".
- Micro yield market maker program hours: "RTH (7:00AM - 4:00PM Chicago Time) and ETH (5:00PM - 7:00AM)"
  (cftc_rule011323cbotdcm003.pdf.txt).

### F5. Published ADV and open interest (CME Group monthly reports, Wayback captures)

Files: cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt (CBOT ADV report, "August 2023"; columns "AUG 2023 AUG 2022
% CHG JUL 2023 % CHG Y.T.D 2023 Y.T.D 2022 % CHG"), cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt (CME Group ADV
report, "November 2023"; columns "NOV 2023 NOV 2022 % CHG OCT 2023 % CHG Y.T.D 2023 Y.T.D 2022 % CHG"),
cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt ("September 2026"; columns "SEP 2026 SEP 2025 % CHG AUG 2026 % CHG
Y.T.D 2026 Y.T.D 2025 % CHG"), cme_Web_OI_Report_CBOT_20240416143839.pdf.txt ("MAR 2024 MAR 2023 % CHG FEB 2024 %
CHG"), cme_Web_OI_Report_CBOT_20251112073031.pdf.txt ("OCT 2025 OCT 2024 % CHG SEP 2025 % CHG"). All rows below are
in the "Interest Rate Futures" section of each report (options rows excluded). Units: contracts per day (ADV) and
contracts (OI), all expiries.

| Row label in report | YTD Jan-Aug 2023 | Nov 2022 | Oct 2023 | Nov 2023 | YTD Jan-Sep 2026 | Sep 2026 | OI Mar 2023 | OI Oct 2025 |
|---|---|---|---|---|---|---|---|---|
| 2-YR NOTE (ZT) | 797,491 | 882,991.9 | 675,122.09 | 1,464,550 | 1,317,555 | 1,250,894 | 2,373,250 | 4,606,433 |
| 5-YR NOTE (ZF) | 1,542,263 | 1,659,547.95 | 1,335,160.5 | 2,740,659 | 1,938,361 | 1,913,161 | 4,415,991 | 6,990,134 |
| 10-YR NOTE (ZN) | 1,971,131 | 2,174,701.33 | 1,961,964.73 | 3,007,906 | 2,595,499 | 2,646,717 | 4,248,005 | 5,511,626 |
| 30-YR BOND (ZB) | 405,796 | 452,782.14 | 554,315 | 679,777 | 609,587 | 609,453 | 1,191,819 | 1,920,369 |
| 2Y YIELD (2YY) | 320 | 428.71 | 175.91 | 213 | 0 | 0 | 461 | 20 |
| 5Y YIELD (5YY) | 6 | 24.76 | 0.45 | 0 | 0 | 0 | 0 | 0 |
| 10Y YIELD (10Y) | 4,230 | 2,481.62 | 9,071 | 7,282 | 1,277 | 1,398 | 2,921 | 3,454 |
| 30Y YIELD (30Y) | 47 | 201.1 | 103.5 | 48 | 0 | 2 | 178 | 9 |

Verbatim rows (whitespace collapsed), for example: "10Y YIELD 7,282 2,481.62 193.4% 9,071 -19.7% 5,163 4,702 9.8%"
(November 2023 report); "5Y YIELD 0 24.76 -100.0% 0.45 -100.0% 4 97 -95.7%" (November 2023 report); "2Y YIELD 0 8
-97.6% 0 - 0 36 -99.5%" (September 2026 report); "5Y YIELD 0 0 - 0 -" (OI, March 2024 report). The full 12-month
average for 2022-11..2023-10 is not printed in any report fetched; the months and the YTD figures above are what is
published. The November 2023 figures fall inside the pilot window; they are CME's published aggregates, not market
data. A0 computes owned ADV for ZT..ZB in the standard window; A0 has no bars for the micro yields.

Pilot-window feasibility (2023-11-01..2024-02-29) for the micro yields: November 2023 ADV of 0 for 5YY (and 0.45 in
October 2023) and 48 for 30Y; a launch date of 2021-08-16 and continuous listing hold for all four, but whether 5YY
traded on 60 or more trade dates in the window is doubtful from these ADVs (no daily count was read, by rule).

Other published volume statements: CME's 2023 rates review (cme_ir_liquidity_trading_review_2023.pdf.txt, January
2024) prints "Avg. Daily Volume 0.93m 2.22m" (2-Year, 2021 vs 2023), "2.28m 3.52m" (5-Year), "4.82m 5.65m" (10-Year).
These are about 2.7 times the ADV report figures for the same products and year; the basis of the review's volume
count is not stated in the file. Micro yield milestones: "Since their August 16 launch, more than 1,000 participants
have traded across Micro 2-Year, Micro 5-Year, Micro 10-Year and Micro 30-Year Yield futures, including 860,000 Micro
10-Year Yield futures contracts traded." (CME press release 2022-02-02, cme_pr_2022-02-02_micro_yield_1m.html.txt).

### F6. Participants: CFTC Traders in Financial Futures (futures only), and automated-trading shares

CFTC TFF categories are dealer/intermediary, asset manager/institutional, leveraged funds, other reportables and
nonreportables; TFF has no "commercial hedger" category. Means of the weekly "pct_of_oi_*" fields (percent of open
interest) computed by work/A1_rates/A1_rates_tff.py from cftc_tff_rates_2022-11_2023-10.json and
cftc_tff_rates_latest.json (summary in work/A1_rates/A1_rates_tff_summary.json). Market names in the data: "UST 2Y
NOTE - CHICAGO BOARD OF TRADE" (042601), "UST 5Y NOTE" (044601), "UST 10Y NOTE" (043602), "UST BOND" (020601),
"MICRO 10 YEAR YIELD - CHICAGO BOARD OF TRADE" (04360Y). No TFF rows exist since 2022-11 for 2YY, 5YY or 30Y (the
market list query cftc_tff_04_market_list.json and cftc_tff_rates_market_list.json return none): they were below the
reporting thresholds.

| Contract | Window (reports) | Mean OI | Nonrept % long / short | Dealer % L/S | Asset mgr % L/S | Lev funds % L/S | Other rept % L/S | Mean traders |
|---|---|---|---|---|---|---|---|---|
| ZT | 2022-11-01..2023-10-31 (53) | 3,025,798 | 7.7 / 6.0 | 2.7 / 9.4 | 49.6 / 15.9 | 17.4 / 49.3 | 8.5 / 5.3 | 398.0 |
| ZF | same (53) | 4,817,604 | 7.6 / 7.5 | 1.2 / 13.1 | 47.6 / 16.5 | 15.8 / 41.4 | 10.7 / 4.4 | 371.4 |
| ZN | same (53) | 4,410,188 | 8.9 / 9.0 | 2.9 / 7.3 | 52.8 / 25.4 | 7.5 / 32.7 | 7.9 / 5.5 | 408.1 |
| ZB | same (53) | 1,258,813 | 14.4 / 11.1 | 2.5 / 11.8 | 55.3 / 23.4 | 5.0 / 31.4 | 6.3 / 5.7 | 192.9 |
| 10Y | same (32 weeks published) | 4,471 | 31.2 / 29.7 | 0.0 / 0.0 | 0.0 / 0.0 | 27.9 / 36.6 | 22.6 / 15.3 | 26.5 |
| ZT | 2025-10-07..2026-10-13 (54) | 4,560,912 | 5.1 / 3.2 | 2.7 / 11.6 | 57.4 / 12.3 | 10.8 / 51.7 | 7.0 / 4.1 | 488.4 |
| ZF | same (54) | 6,660,184 | 6.5 / 5.0 | 1.7 / 12.6 | 61.7 / 14.0 | 6.9 / 46.9 | 4.2 / 2.6 | 453.4 |
| ZN | same (54) | 5,500,502 | 7.9 / 6.7 | 4.8 / 11.3 | 57.8 / 16.0 | 7.9 / 46.3 | 5.2 / 3.4 | 425.1 |
| ZB | same (54) | 1,862,887 | 13.3 / 7.4 | 1.3 / 13.9 | 58.6 / 33.0 | 7.4 / 24.6 | 4.2 / 5.8 | 243.3 |
| 10Y | 2025-10-21..2026-10-06 (34 weeks published) | 2,774 | 16.9 / 41.9 | 0.0 / 0.0 | 0.0 / 0.1 | 68.7 / 14.5 | 10.8 / 39.9 | 24.3 |

These are shares of open interest, not of volume. Nonreportable positions are the small-trader proxy named in the
brief.

Automated trading (CFTC Office of the Chief Economist, Haynes and Roberts; CME transaction data):
- 2015 paper (cftc_oce_automatedtrading_2015.pdf.txt, sample November 12, 2012 - October 31, 2014) and the 2017 update
  (cftc_oce_automatedtrading_update_2017.pdf.txt, adds November 1, 2014 - October 31, 2016). Table 2 of the update,
  "Interest Rate - US Treasury 5 5 5.9 (1.5) 4.5 (1.1) 64.0 (16.6) 68.4 (16.4) 30.2 (7.8) 27.1 (6.5)": columns
  "Non-Electronic (%) ATS (%) Manual (%)", first number of each pair the 2012-2014 period, second 2014-2016. So ATS
  (automated trading system) participation in US Treasury futures volume was 64.0% then 68.4%.
- Table 3 of the update (columns "Total Volume (mm) ATS-ATS (%) ATS-MAN (%) MAN-MAN (%)"): "Interest Rate - US
  Treasury 10 Yr Note 643 661 42.6 48.0 41.1 39.7 11.9 8.7" and "5 Yr Note 360 378 50.5 53.2 32.8 34.0 8.6 7.4".
  ZT and ZB are not among the "top three products by volume in each product group" and are not tabulated.
- Table 5 (small vs large volume traders; "large volume trader" if at least 0.5 percent of daily volume): "10 Yr Note
  47,773 50,232 20.5 21.3 27.4 23.7 716 702 42.7 46.5 5.1 4.9", columns Small Volume Trader (N, ATS %, MAN %) then
  Large Volume Trader (N, ATS %, MAN %), each with two periods. Small manual traders: 27.4% then 23.7% of ZN volume; 5-Year 18.7% then 18.0%.
- Resting time of the passive side (Table of time between order placement or modification and execution, share of
  two-sided volume): "10 Yr Note 5.4 6.5 0.6 0.5 2.0 2.1 0.4 0.3 1.2 1.4 0.3 0.2 7.2 7.8 2.2 1.9 7.7 7.9 3.3 2.8 17.8
  17.0", header columns 0 - 100 ms, 100 ms - 500 ms, 500 ms - 1 sec, 1 sec - 10 sec, 10 sec - 1 min (each split ATS and
  MAN), and Remaining Elec Volume; two periods per cell. The last pair (17.8, 17.0) is passive volume resting more than one
  minute, as a share of two-sided volume (passive volume is about half of two-sided volume).
- Principal trading firms (PTFs; the Joint Staff Report of 2015-07-13, jsr_oct15_2014.pdf.txt): "PTFs accounted for
  more than 50 percent of the total trading volume across various maturities in both cash and futures markets, while
  bank-dealers accounted for roughly 30 to 40 percent of volume in the cash market, but under 20 percent in the
  futures market"; "PTFs represented around 80 percent of traffic in both futures and cash on October 15"; during
  the event window "the PTF share of the order book increased to an average of 80 percent of depth at the top 3
  levels of the book in cash and 64 percent in futures".
- ZN liquidity provision (Gousgounis, Mixon, Tuzun and Vega, FEDS 2025-038, feds_2025-038_tsy_futures_liquidity_
  march2020.pdf.txt, 10-year Treasury futures): "PTFs and bank dealers are the main liquidity providers, accounting
  for 70 and 15 percent of the volume of liquidity providing trades, respectively"; "PTFs, as a group, accounted for
  about 40 percent of all passive orders, and in 2021 they account for about 72 percent."
- Micro yields: no HFT or automated-trading share found. The CFTC 2019 2-year study and the Haynes-Roberts tables
  predate the micros. Market makers are present by program (F7).

Retail share: no CME or regulator figure for the retail share of any of the eight products was found. CME's launch
release for the micro yields (Mondo Visione copy of the 2021-06-09 release, mondovisione_cme_micro_yield_launch_
2021-06-09.html.txt) says: "These innovative, micro-sized contracts will provide market participants - from
institutions to sophisticated, active, individual traders - exposure to the yield of on-the-run" Treasuries.
Searched: CME press releases on the micro yields (launch, 30,000 contracts, 1 million contracts), CME rates reviews,
CBOT filings to the CFTC; no retail percentage appears in any fetched file.

### F7. Market-maker and incentive programs

- Micro yields: the "Micro Treasury Yield Futures Market Maker Program" (renamed "Yield Futures Market Maker
  Program" by 2024), CBOT filings to the CFTC. Purpose: "to support the development of the products listed below. A
  more liquid contract on the central limit order book benefits all participants in the market." Products: "Micro
  2-Year Yield Futures ("2YY"), Micro 5-Year Yield Futures ("5YY"), Micro 10-Year Yield Futures ("10Y"), and Micro
  30-Year Yield Futures ("30Y") traded on Globex" (cftc_rule011323cbotdcm003.pdf.txt, CBOT Submission No. 23-025).
  Term: "Start date is August 16, 2021." and extensions: 21-389 "End date is January 31, 2022"; 23-285
  (cftc_rules0706233776.pdf.txt, effective August 1, 2023) "End date is July 31, 2023 January 31, 2024" (blackline:
  old then new); 24-303 (cftc_rules0715243320.pdf.txt) "End date is July 31, 2024 January 31, 2025"; 24-518
  "January 31, 2025 July 31, 2025"; 26-340 (cftc_rules0708269230.pdf.txt, effective August 1, 2026) "End date is July
  31, 2026 February 29, 2028". The program therefore ran through the pilot window 2023-11..2024-02 (a January 2024
  extension filing was not fetched, but 24-303 shows the end date then in force was July 31, 2024).
- Obligations (23-285, in force from August 2023): quoting tiers on the 10Y outright and on 10Y-2YY, 10Y-5YY and
  30Y-10Y inter-commodity spreads, for example "1 10-Year 10Y 10 65% of RTH" with two width values "0.5" and "1.0" printed in the
  width cell (maximum width in bps; the filing is a blackline, and which value is the deletion and which the addition
  is not recoverable from the text layer; minimum size 10; time in market 65% of RTH), Tier 2 "10-Year Outright 10Y
  150 65% of RTH" with widths "0.3" and "0.6", ETH "10-Year 10Y 2.0 5 75% of ETH". 2YY, 5YY and 30Y have quoting obligations only through their spread
  against 10Y. Incentives: fee waivers ("10Y Fee Waivers: Upon meeting the Tier 1 obligations ... participants will
  receive fee waivers for Globex volume in the applicable Product") and, in 26-340, a "Monthly Incentive Pool ...
  participants will receive a pro-rata portion of $10,000".
- ZT, ZF, ZN, ZB: no market-maker program for the outrights was found in the CBOT filings fetched or in the search
  results (the Treasury programs found were for the micro yields and, from 2024-03-25, a "Micro Treasury Futures
  Market Development Program" for the Micro Ultra contracts, cftc_rules02262412120.pdf.txt: "Start date is March 25,
  2024. End date is August 31, 2024."). The 2014 filing on Top-order parameters (F2) and the PTF depth shares (F6)
  document professional liquidity provision without a program. Searched: CFTC rule filings by WebSearch (two
  queries); a full scan of CBOT incentive filings for Treasury futures was not done.

### F8. Circuit-breaker (limit) events 2019-2024

- Dynamic limits replaced the older special price fluctuation limits for Treasury futures from trade date
  2020-07-27: SER-8542 (cme_SER-8542.pdf.txt): "Effective Sunday, July 26, 2020 for trade date Monday, July 27, 2020"
  ... "apply Dynamic Price Fluctuation Limits to the following CBOT Treasury and Interest Rate Swap (LTIR) contracts",
  listing ZT, ZF, ZN, ZB; "the primary contract month for the 10-Year Treasury Note (ZN) futures would have a fixed
  dynamic variant of 2.00 points"; "Posted trades, bids or offers through the dynamic price fluctuation limits will
  trigger a two (2) minute trading halt."
- Days with a triggered halt, 2019-2024: none found. No CME notice, regulator report or press item reporting a
  Rule 589 halt in ZT, ZF, ZN, ZB or the micro yields in 2019-2024 was found (one WebSearch; the search results also
  pointed to an undated Nanex note on a five-second halt in Treasury futures around a jobs report, not fetched).
  This is a gap, not a finding of zero. For scale only: the ZN variant is 2.00 points = 128 ticks of 1/64 within a
  rolling 60 minutes; A0 reports owned daily ranges for ZT..ZB.
- Jump frequency (days with |daily return| above 4 daily SD): owned-bar counts for ZT..ZB are in A0
  (A0_contract_stats.md, lines 148-155). No published count was found for the micro yields.

### F9. Spreads, depth at the best level, queue and trade size

- CME, "Interest Rate Futures Liquidity Update - 2018" (7 Jan 2019; cme_ir_futures_liquidity_update_2018.html.txt):
  "For all Treasury futures products, for example, best bid/offered price spreads matched corresponding contract
  minimum price increments throughout more than 99% of each trading day." Table "Average Central Limit Order Book
  Size for Treasury Futures", "Avg Book Size at Best Bid/Offer Level" 2016 / 2017 / 2018: "2-Yr Note (ZT) 3,854
  38,852 99,471"; "5-Yr Note (ZF) 596 866 1,319"; "10-Yr Note (ZN) 1,166 1,649 2,507"; "Bond (ZB) 154 253 377";
  "Avg Book Size at Best 3 Bid/Offer Levels" 2018: ZT 131,254, ZF 6,632, ZN 12,322, ZB 1,898; "Outright front-month
  only, measured during regular trading hours (7:00 am to 4:00pm, CT)". Units: contracts. These are 2018 figures;
  no later published depth table by product was found.
- ZN tick-constrained spread: FEDS 2025-038: "bid-ask spreads over our sample period were often constrained by the
  minimum tick size (e.g., in March 2020, 94% of bid-ask spread observations are "stuck" at one tick)."
- ZT price grid: CFTC 2019 2-year study: "During the active trading day, prices move very slowly, hitting only a
  few price points".
- Cost to trade (CME 2023 review): "2-Year ... Avg. Cost to Trade, 1000 Lots 1.10 (ticks) 1.78 (ticks)" (2021, 2023);
  "5-Year ... 1000 Lots 1.20 (ticks) 1.60 (ticks)"; "10-Year ... 500 Lots 1.03 (ticks) 1.07 (ticks)"; "Avg. Daily True
  Range" 2023: 2-Year "65.21 (ticks)", 5-Year "73.21 (ticks)", 10-Year "52.58 (ticks)".
- Trade size and queues, ZN (Lalor and Swishchuk, arXiv 2409.12721v3, LOB data of 2024-04-09): "ZN 16.01 2" (mean
  and median trade size, contracts; ES 3.47 and 1). They note ZN "often remains unchanged for extended periods" and
  "queue sizes are much larger relative to CL, ES, and NQ while trade sizes are very similar".
- Session split (overnight vs main session spreads): no published figure found for any of the eight products. CME's
  2023 review shows interest rate ADV in European and Asian hours only as charts (no numbers in the text layer).
- 10Y (micro 10-year yield) spread: CME article on key macroeconomic events and Yield futures trading
  opportunities (2024) (cme_article_2023_yield_futures_macro_events.html.txt, Wayback copy, figures for H1 2024): "In 2024,
  the average bid-ask spread at the top of book (TOB) has been 0.167 bps during RTH (regular trading hours: generally
  7:00 a.m. - 4:00 p.m. CT), while the minimum tick size is 0.1 bps." That is 1.67 ticks on average. Same table:
  average 10Y daily range "All other Days 8.17" bps (81.7 ticks), "CPI 15.65", "Employment Situation 14.25", "FOMC
  11.15". CME marketing article; no depth figure. No spread figure was found for 2YY, 5YY or 30Y.
- Micro yields depth: no published depth figure found. The market-maker obligations bound the quoted width for
  participants who meet them: 10Y Tier 1 maximum width 0.5 or 1.0 bp (5 or 10 ticks of 0.1 bp; blackline, see F7), Tier 2 0.3 or 0.6 bp, minimum size 10 or 150 contracts, 65% of RTH (F7). These are program terms, not measured spreads.
- Traded volume per minute and QV (displayed size over volume per minute): not published for any of the eight.

### F10. Scheduled product-specific releases, weekend gaps

- Treasury auctions (US Treasury, Tentative Auction Schedule, ust_tentative_auction_schedule.pdf.txt, covering
  auctions from August 11, 2026 to January 2027): each nominal coupon tenor is auctioned once per month; the
  schedule lists 6 auctions each of the 2-, 3-, 5-, 7-, 10-, 20- and 30-year securities over six months, for example
  "2-Year NOTE Thursday, August 20, 2026 Tuesday, August 25, 2026 Monday, August 31, 2026" and "10-Year NOTE
  Wednesday, August 05, 2026 Wednesday, August 12, 2026 Monday, August 17, 2026" (announcement, auction, settlement
  dates). So per tenor about one auction a month (about 0.23 per week); the 2-, 5- and 7-year auctions fall in the
  same week each month, and the 3-, 10- and 30-year auctions in another week. Treasury bills are auctioned several
  times a week. Whether the scorer counts Treasury auctions as product-specific or as part of the shared US macro
  calendar is a scoring question, not decided here. Order-flow effects around auctions: NY Fed Staff Report 1188
  (nyfed_sr1188_auction_price_pressure.pdf.txt, "Intraday Price Pressure and Order Flow Around U.S. Treasury
  Auctions", March 2026, revised July 2026), fetched, not yet read for results.
- Micro yields roll monthly to the newly auctioned on-the-run issue (F1), so each auction changes the reference
  CUSIP of the next contract month.
- Weekend gap: no source fetched states that cash Treasuries trade while CME Globex is closed (Friday 4:00 p.m. CT
  to Sunday 5:00 p.m. CT). Not verified either way from a primary source.

### F11. Cash-Treasury (BrokerTec) link

- Micro yields settle to BrokerTec cash benchmarks: "The final settlement value, applied on the last business day of
  the month, will be determined by the 3:00 p.m. ET BrokerTec US Treasury Benchmark1, or latest available fixing. The
  fixings are calculated as a Volume Weighted Average Yield ("VWAY") of cash Treasury transactions during the 15
  minutes leading up" to the fixing time (cftc_ptc072921cbotdcm001.pdf.txt). "On February 1, 2021, BrokerTec cash
  Treasuries transitioned to CME Globex." BrokerTec cash volume, February-May 2021, median daily $MM: "UB02 (2yr)
  7,728", "UB05 (5yr) 30,403", "UB10 (10yr) 29,269", "UB30 (30yr) 9,561" (Exhibit 4, same file).
- Treasury futures and BrokerTec share participants and price discovery: Joint Staff Report (above) analyses the
  10-year note in "cash and futures markets" jointly; Mixon and Tuzun (FEDS 2018-065,
  feds_2018-065_price_pressure_term_structure.pdf.txt): "Price discovery in the level of interest rates is most
  strongly linked to non-dealer order flow in the 10-year futures contract, while price discovery in the slope of the
  curve is linked to order flow in the 10-year futures and the 5-year cash market."
- Implied inter-commodity spreads link the four Treasury futures books to each other (F2).

### F12. Published microstructure research on these products and cousins

Relation codes: SAME (same product), FAM (micro/mini/full version on the same underlying; here the Treasury futures
and the yield futures of the same tenor are treated as related but different designs), COUSIN (close cousin on CME
Globex: other Treasury futures tenors), CLASS (asset class only: cash Treasuries, non-CME bond futures, theory).
Result codes: POS (findable short-horizon pattern or profitable passive provision), NULL (descriptive only, or no
pattern), NEG (patterns absent, arbitraged away, or passive provision loses to adverse selection).

| # | Study | Product | Relation to ZN (others in note) | Result | Evidence file and quote |
|---|---|---|---|---|---|
| R1 | DeLise (2024), "The Negative Drift of a Limit Order Fill", arXiv 2407.16527v1 | ZN ("Ten Year Treasury Bond futures (TY) data set", 10 levels, Dec 2023) | SAME for ZN; COUSIN for ZT, ZF, ZB; FAM for 10Y | NEG (passive fills adversely selected) | arxiv_2407.16527v1_negative_drift_fill.pdf.txt: "There is a significant downward price drift following buy order fills and an equally significant upward drift following sell order fills"; "a limit order fill does incur a type of slippage penalty, and the magnitude of that penalty is shown to here to be very close to 1/2 tick"; "1/3 of orders were not filled at all"; "Each sample consists of 521 data points." Simulated fills on recorded book data; one dataset |
| R2 | Lalor and Swishchuk, "Market Simulation under Adverse Selection", arXiv 2409.12721v3 (2026-06) | ES, NQ, CL, ZN (CME) | SAME for ZN | NEG for naive quoting (adverse fills dominate) | arxiv_2409.12721v3_market_sim_adverse_selection.pdf.txt: "2024/04/24 ZN Jun24 224 199 25" (total LO fills, adverse, non-adverse; 1-lot quotes 1 tick from the touch, one day); "we can see that a significant portion of the total number of LO fills in ES, NQ, CL and ZN were adverse"; "queue sizes are much larger relative to CL, ES, and NQ" |
| R3 | Gousgounis, Mixon, Tuzun and Vega (2025), FEDS 2025-038 | ZN | SAME for ZN | NULL on predictability; documents PTF dominance of passive liquidity and a tick-constrained spread | feds_2025-038_tsy_futures_liquidity_march2020.pdf.txt: "PTFs and bank dealers are the main liquidity providers, accounting for 70 and 15 percent of the volume of liquidity providing trades"; "94% of bid-ask spread observations are "stuck" at one tick" (March 2020) |
| R4 | CFTC Office of the Chief Economist (March 2019), EFFECT OF MATCHING ALGORITHM CHANGES | ZT (control: 30Y bond futures) | SAME for ZT | NULL (mechanics): under FIFO "Passive order fill ratios will increase (Yes, especially for largest orders)"; "Trade sizes almost triple" | cftc_two_year_analysis_2019.pdf.txt |
| R5 | Haynes and Roberts (2015; 2017 update), CFTC OCE | ZN, ZF (Treasury group) | SAME for ZN, ZF | NULL (descriptive): automation shares | cftc_oce_automatedtrading_update_2017.pdf.txt (F6) |
| R6 | Joint Staff Report (2015-07-13), "The U.S. Treasury Market on October 15, 2014" | ZN and 10-year cash | SAME for ZN | NULL (descriptive): PTF shares of volume, traffic and top-3 depth | jsr_oct15_2014.pdf.txt (F6) |
| R7 | Mixon and Tuzun (2018), FEDS 2018-065 | ZN, ZF, ZT, ZB futures and cash dealer positions | SAME | POS for order-flow price discovery, but weekly data, not short-horizon | feds_2018-065_price_pressure_term_structure.pdf.txt: "Price discovery in the level of interest rates is most strongly linked to non-dealer order flow in the 10-year futures contract"; "The final sample of data is weekly" |
| R8 | (authors include F. Ruela) (2023), "Tick Size, Competition for Liquidity Provision, and Price Discovery: Evidence from the U.S. Treasury Market", Management Science, doi 10.1287/mnsc.2022.4663 | 2-year cash note (BrokerTec) and ZT | SAME for ZT | NULL (mechanism, no trading-rule test): per the abstract, HFTs "find liquidity provision less profitable in the smaller tick size environment" (after the cuts), and short-run price discovery moves to the market with the finer grid | [unverified: OpenAlex abstract only, openalex_abstracts_batch1.json]: "a tick size change ... around the November 19, 2018, tick size reduction in the 2-year Treasury note and a similar change in the 2-year futures eight weeks later"; "the finer pricing grid in the cash market allows traders to act on small information signals that are not profitable to exploit in the larger-tick futures market" |
| R9 | Brandt, Kavajecz and Underwood (2007), "Price discovery in the treasury futures market", J. Futures Markets 27: 1021-1051 | Treasury futures and cash | SAME/COUSIN (tenors not visible in the abstract) | POS for futures order flow in price discovery; horizon not visible | [unverified: OpenAlex abstract only]: "utilizing both futures and cash market prices and net orderflow to determine where price discovery takes place" |
| R10 | Brandt and Kavajecz (2004), J. Finance | cash Treasuries | CLASS | POS at the daily horizon (order-flow imbalance and yields) | [unverified: OpenAlex abstract only; Wiley PDF answered 403]: "orderflow imbalances (excess buying or selling pressure) account for up to 26% of the day-to-day variation in yields on days without major macroeconomic announcements" |
| R11 | Fleming, Liu and Nguyen (2026), NY Fed Staff Report 1188 | cash Treasuries around auctions | CLASS | POS at an hours horizon (auction-day price pressure explained by net order flow) | nyfed_sr1188_auction_price_pressure.pdf.txt: "yields rise in the hours before auction and reverse afterward"; "net order flow dominates in explaining the pressure" |
| R12 | Arxiv 1210.7215v2, "Heavy-Tailed Features and Empirical Analysis of the Limit Order Book Volume Profiles in Futures Markets" | includes "5 Year T-Note 5YTN 7:30:00 to 14:00:00 CBOT" | SAME for ZF | NULL (volume profile distribution only) | arxiv_1210.7215v2_lob_volume_profiles_futures.pdf.txt |
| R13 | Arxiv 2401.10722v1, "Stylized Facts and Market Microstructure: ... German Bond Futures Market" (Schatz, Bobl, Bund, Buxl; Eurex) | Eurex bond futures | CLASS | NULL (stylized facts) | [unverified: arXiv abstract only, arxiv_abstracts_batch1.xml] |
| R14 | Guilbaud and Pham (2012), arXiv 1205.3051, "Optimal High Frequency Trading in a Pro-Rata Microstructure with Predictive Information" | theory, "one-tick pro-rata limit order book, as typically arises in short-term interest rate futures" | CLASS (relevant to ZT's partial pro-rata) | NULL (theory) | [unverified: arXiv abstract only] |
| R15 | Mizrach and Neely (2005 WP; J. Banking & Finance 2008), "Information shares in the US Treasury market" | cash and futures | SAME/COUSIN | not read | stlfed_wp2005-070_mizrach_neely_info_shares.pdf.txt has an unreadable font layer (pdftotext output garbled); no claim used |

No study was found on the micro yield futures (2YY, 5YY, 10Y, 30Y) themselves (one WebSearch, arXiv API queries
"Treasury futures", "Treasury note futures", "bond futures" + "order book", "interest rate futures" + "limit order",
"CME" + "order book", OpenAlex keyword searches; hits in work/A1_rates/A1_rates_arxiv_hits.txt and
work/A1_rates/A1_rates_openalex_hits.txt). No study was found that tests order-flow imbalance, queue imbalance or
trade-sign predictability at seconds-to-minutes horizons on any CME Treasury future (one WebSearch returned only
equity studies such as Gould and Bonart on Nasdaq stocks; those belong to the C2 readers).

Note on R8: the ZT minimum tick was halved in early 2019 ("a similar change in the 2-year futures eight weeks
later" than 2018-11-19, abstract-only); the current rulebook tick is one-eighth of 1/32 (F-sheet ZT). The CME 2018
depth figures for ZT (F9) predate that change; the CME 2016 RFI response (cme_treasury_rfi_response_2016.pdf.txt)
says the average best bid/offer spread "has held steady at" one-quarter of 1/32 for Short-Term (2-Year) Note (TU)
and FV futures, one-half of 1/32 for TY futures and 1/32 for US futures over the six years to 2016 (the text layer
prints "¼ of 1/32", "½ of 1/32" with the "nd" superscripts on a separate line).

## Run notes, gaps and failures

- Finished 2026-10-21 06:12 PDT. WebSearch calls used: 15 of 40; no budget notice was returned. arXiv API and OpenAlex
  (polite pool) were used for discovery. No Scrapling, Firecrawl or stealthy fetch was used. No market data was read;
  no key was printed. Holdout status at the end: "unlocks_logged": 0.
- Failed or abandoned fetches: the Joint Staff Report at treasury.gov URLs (404 or an HTML page; the treasurydirect.gov
  copy was used); Brandt and Kavajecz (2004) Wiley PDF (403; abstract from OpenAlex only); Jiang, Lo and Valente (HFT
  around announcements, BrokerTec) EconStor link (returned HTML; not used); CME press release of 2021-08-24 via Wayback
  (timeouts); Mizrach and Neely working paper (fetched, text layer garbled; not used).
- Not found within budget (recorded as null with what was searched): current ZT outright matching parameters; launch
  years of ZT, ZF, ZN; any retail-share percentage; any HFT share for the micro yields; overnight spreads; depth after
  2018 for ZT..ZB; any spread or depth for 2YY, 5YY, 30Y; traded volume per minute; any Rule 589 halt record
  2019-2024; a source on cash-Treasury weekend trading; any study of short-horizon order-book predictability on a CME
  Treasury future or the micro yields.
- Facts that a scorer may need to weigh (not judged here): the micro yields' published ADV (5YY 0 and 30Y 48 in
  November 2023; all three of 2YY, 5YY, 30Y at or near 0 in 2026); ZT's partial pro-rata outright book; the 2018
  displayed size at the best level (ZT 99,471 before its 2019 tick halving; ZN 2,507; ZF 1,319; ZB 377); two ZN
  studies (R1, R2) finding passive fills adversely selected; CME's micro-yield market maker program running through
  2028.
- Helper scripts (all mine, in work/A1_rates/): A1_rates_fetch.sh, A1_rates_rfetch.sh (fetch and log), A1_rates_tff.py
  (TFF means), A1_rates_arxiv.py, A1_rates_openalex.py (discovery), A1_rates_build_json.py (JSON), A1_rates_render_
  sheets.py (sheets below), A1_rates_verify_quotes.py and A1_rates_verify_md.py (every JSON quote and every quoted
  string of 25+ characters in this file checked against the saved sources; 0 misses in the JSON, 0 in this file apart
  from one abstract whose hyphens are escaped in the saved JSON).

## Candidate fact sheets (generated from A1_rates.json by work/A1_rates/A1_rates_render_sheets.py)

Quotes for every field are in A1_rates.json and in the F sections above. "Source" gives file base names under
pages/A1_rates/ unless another path is shown. Family-wide facts are referenced as F1..F12.

### 2YY

| Field | Value | Unit | Window | Source | Note |
|---|---|---|---|---|---|
| product_name | Micro 2-Year Yield Futures (titled '2-Year Yield Futures' since 2024-02-05) |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Title change: CBOT 24-116 (cftc_rules02132411742.pdf.txt) 'Effective Monday, February 5, 2024, the Exchange implemented administrative amendments to the contract title of all Micro Yield futures contracts'. |
| product_code | 2YY |  |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| tick_size | 0.001 | index points of yield (0.1 basis point) |  | cftc_ptc072921cbotdcm001.pdf.txt | Rulebook text in the filing, Rule 80102.C-83102.C; spec table: 'All delivery months: 0.001 Index points (1/10th basis point per annum) =' $1.00. |
| tick_value | 1.0 | USD per contract |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| contract_size | $1,000 x index points ($10 DV01) |  |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| settlement | cash-settled to the BrokerTec US Treasury benchmark (3:00 p.m. ET VWAY) of the on-the-run issue; 2 nearest monthly contracts; terminates last business day of the month |  |  | cftc_ptc072921cbotdcm001.pdf.txt | 'The Contracts settle to the most recently auctioned On-the-Run CUSIP at each tenor, which updates monthly and the expectation is that the front contract month will dominate trading'. |
| launch_date | 2021-08-16 | trade date |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| globex_60_dates_in_2023-11..2024-02 | True |  | 2023-11-01..2024-02-29 | cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Launch 2021-08-16 and continuous listing (the brief's sufficient condition). ADV 213 in Nov 2023 and OI ~500 (Feb-Mar 2024) are low; per-date trade counts not read. |
| match_algorithm | FIFO |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Exhibit 2 table cell labelled 'CME GLOBEX MATCHING ALGORITHM' (label split over three lines in the text layer). |
| trading_hours | Sunday-Friday 6:00 p.m. - 5:00 p.m. ET (5:00 p.m. - 4:00 p.m. CT); Mon-Thu 5:00-6:00 p.m. ET maintenance |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Exhibit 2, row CME Globex; next cell: 'Monday - Thursday 5:00 - 6:00 p.m. ET (4:00 - 5:00 p.m. CT) daily maintenance period'. |
| price_limits | daily_limit: null (unknown); dynamic_variant: 20 basis points; halt: 2-minute halt (Rule 589.D) |  | Rule 589 table Wayback capture 2024-10-01; listing filing 2021 | cme_special_price_fluctuation_limits.xlsx | Same 20 bp variant in the 2021 listing filing Appendix D. 20 bp = 200 ticks of 0.1 bp. |
| adv_published_latest | YTD_Jan-Sep_2026: 0; Sep_2026: 0 | contracts per day | Jan-Sep 2026 | cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt | Row label in report '2Y YIELD'. |
| adv_2022_11_2023_10 | YTD_Jan-Aug_2023: 320; Nov_2022: 428.71; Oct_2023: 175.91 | contracts per day | 2022-11..2023-10 (pieces published) | cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt; cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | No owned bars (A0 line 211). |
| open_interest | Mar_2023: 461; Oct_2025: 20 | contracts, month-end | Mar 2023; Oct 2025 | cme_Web_OI_Report_CBOT_20240416143839.pdf.txt; cme_Web_OI_Report_CBOT_20251112073031.pdf.txt |  |
| retail_share | null (unknown) | % of volume |  | mondovisione_cme_micro_yield_launch_2021-06-09.html.txt | No retail percentage published in any file found (CME launch, 30k and 1M-contract releases, CBOT filings). CME targets individual traders among others; it does not describe the product as predominantly retail. |
| commercial_hedger_share | null (unknown) | % of OI |  |  | CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset manager, leveraged funds, other reportables, nonreportables. See tff_category_shares. |
| tff_category_shares | null (unknown) | % of open interest | 2022-11..2026-10 | cftc_tff_04_market_list.json; cftc_tff_rates_market_list.json | No CFTC TFF rows for this contract since 2022-11 (below reporting thresholds); the only micro yield in TFF is 'MICRO 10 YEAR YIELD' (04360Y). |
| nonreportable_share | null (unknown) | % of open interest | 2022-11..2026-10 | cftc_tff_04_market_list.json; cftc_tff_rates_market_list.json | No CFTC TFF rows for this contract since 2022-11 (below reporting thresholds); the only micro yield in TFF is 'MICRO 10 YEAR YIELD' (04360Y). |
| market_maker_program | True |  | 2021-08-16 .. 2028-02-29 (successive extensions) | cftc_rules0706233776.pdf.txt; cftc_rules0708269230.pdf.txt | Micro Treasury Yield Futures Market Maker Program / Yield Futures Market Maker Program; in force through the pilot window. For 2YY: quoting obligations only via the 10Y-2YY inter-commodity spread; fee waivers for 2YY Globex volume on meeting Tier 1 10Y-2YY obligations. See A1_rates.md F7. |
| hft_automated_share | null (unknown) | % of volume |  |  | No automated or HFT share published for the micro yields (Haynes-Roberts and JSR predate them). Market makers present by program (F7). |
| median_spread_ticks_main | null (unknown) | ticks |  |  | No published spread found (searched CME articles, MM program filings, one WebSearch on micro yield spreads). MM program obligations bound quoted widths only for participants meeting them, and for this tenor only via spreads against 10Y. |
| depth_best_level | null (unknown) | contracts |  | cftc_rules0706233776.pdf.txt | No published depth figure. MM program minimum sizes (10Y outright Tier 1: 10 contracts; Tier 2: 150; ETH: 5) are program terms, not measured depth. |
| touch_queue_size | null (unknown) | contracts |  |  | Not published. |
| brokertec_link | Final settlement to the BrokerTec US Treasury Benchmark (15-minute VWAY of on-the-run cash trades before 3:00 p.m. ET); daily settlement 30-second VWAP before 2:00 p.m. CT |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Price is yield, so it moves opposite to ZT futures prices. See F11. |
| jump_frequency | null (unknown) | days per year with /daily return/ > 4 SD | 2019-2024 |  | No owned bars (A0) and no published count found; product launched 2021-08-16, so 2019-2021 do not exist for it. The full-size cousin's counts are in A0. |
| limit_hit_days_2019_2024 | null (unknown) | days per year | 2019-2024 |  | No CME notice, regulator report or press item reporting a Rule 589 halt in this product in 2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8. |
| weekend_gap_exposure | null (unknown) |  |  |  | Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a primary source either way, so recorded as unknown (expected no, but unsourced). |
| median_spread_ticks_overnight | null (unknown) | ticks |  |  | No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, JSR 2015. |
| volume_per_minute | null (unknown) | contracts per minute |  |  | Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute is derivable there), none for the micro yields. |
| scheduled_releases_per_week | 0.23 | auctions of the matching Treasury tenor per week (about 1 per month) | Treasury tentative schedule Aug 2026 - Jan 2027 | ust_tentative_auction_schedule.pdf.txt | Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). Whether auctions count as product-specific releases or as the shared US macro calendar is for the scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills several per week. No other product-specific scheduled release found. |
| microstructure_research | No study on this product found. Evidence on the full-size cousin ZT (FAM relation, different design): see F12 R1-R3, R7-R9. CLASS: R10, R11. |  |  | reports/stage_e28_briefs/A1_rates.md (section F12) | Study IDs refer to the F12 table, which carries each study's file, quote, relation and result. |

### 5YY

| Field | Value | Unit | Window | Source | Note |
|---|---|---|---|---|---|
| product_name | Micro 5-Year Yield Futures (titled '5-Year Yield Futures' since 2024-02-05) |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Title change: CBOT 24-116 (cftc_rules02132411742.pdf.txt) 'Effective Monday, February 5, 2024, the Exchange implemented administrative amendments to the contract title of all Micro Yield futures contracts'. |
| product_code | 5YY |  |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| tick_size | 0.001 | index points of yield (0.1 basis point) |  | cftc_ptc072921cbotdcm001.pdf.txt | Rulebook text in the filing, Rule 80102.C-83102.C; spec table: 'All delivery months: 0.001 Index points (1/10th basis point per annum) =' $1.00. |
| tick_value | 1.0 | USD per contract |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| contract_size | $1,000 x index points ($10 DV01) |  |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| settlement | cash-settled to the BrokerTec US Treasury benchmark (3:00 p.m. ET VWAY) of the on-the-run issue; 2 nearest monthly contracts; terminates last business day of the month |  |  | cftc_ptc072921cbotdcm001.pdf.txt | 'The Contracts settle to the most recently auctioned On-the-Run CUSIP at each tenor, which updates monthly and the expectation is that the front contract month will dominate trading'. |
| launch_date | 2021-08-16 | trade date |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| globex_60_dates_in_2023-11..2024-02 | null (unknown) |  | 2023-11-01..2024-02-29 | cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Launched 2021-08-16 and listed continuously (brief: launch before 2023-11 and continuous listing suffice), but published ADV was 0 in Nov 2023 and 0.45 in Oct 2023, and OI 0 in Feb-Mar 2024 ('5Y YIELD 0 0 - 0 -'); trading on >= 60 dates in the window is doubtful. Daily trade-date counts not read (market data rule). |
| match_algorithm | FIFO |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Exhibit 2 table cell labelled 'CME GLOBEX MATCHING ALGORITHM' (label split over three lines in the text layer). |
| trading_hours | Sunday-Friday 6:00 p.m. - 5:00 p.m. ET (5:00 p.m. - 4:00 p.m. CT); Mon-Thu 5:00-6:00 p.m. ET maintenance |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Exhibit 2, row CME Globex; next cell: 'Monday - Thursday 5:00 - 6:00 p.m. ET (4:00 - 5:00 p.m. CT) daily maintenance period'. |
| price_limits | daily_limit: null (unknown); dynamic_variant: 20 basis points; halt: 2-minute halt (Rule 589.D) |  | Rule 589 table Wayback capture 2024-10-01; listing filing 2021 | cme_special_price_fluctuation_limits.xlsx | Same 20 bp variant in the 2021 listing filing Appendix D. 20 bp = 200 ticks of 0.1 bp. |
| adv_published_latest | YTD_Jan-Sep_2026: 0; Sep_2026: 0 | contracts per day | Jan-Sep 2026 | cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt | Row label in report '5Y YIELD'. |
| adv_2022_11_2023_10 | YTD_Jan-Aug_2023: 6; Nov_2022: 24.76; Oct_2023: 0.45 | contracts per day | 2022-11..2023-10 (pieces published) | cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt; cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | No owned bars (A0 line 211). |
| open_interest | Mar_2023: 0; Oct_2025: 0 | contracts, month-end | Mar 2023; Oct 2025 | cme_Web_OI_Report_CBOT_20240416143839.pdf.txt; cme_Web_OI_Report_CBOT_20251112073031.pdf.txt |  |
| retail_share | null (unknown) | % of volume |  | mondovisione_cme_micro_yield_launch_2021-06-09.html.txt | No retail percentage published in any file found (CME launch, 30k and 1M-contract releases, CBOT filings). CME targets individual traders among others; it does not describe the product as predominantly retail. |
| commercial_hedger_share | null (unknown) | % of OI |  |  | CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset manager, leveraged funds, other reportables, nonreportables. See tff_category_shares. |
| tff_category_shares | null (unknown) | % of open interest | 2022-11..2026-10 | cftc_tff_04_market_list.json; cftc_tff_rates_market_list.json | No CFTC TFF rows for this contract since 2022-11 (below reporting thresholds); the only micro yield in TFF is 'MICRO 10 YEAR YIELD' (04360Y). |
| nonreportable_share | null (unknown) | % of open interest | 2022-11..2026-10 | cftc_tff_04_market_list.json; cftc_tff_rates_market_list.json | No CFTC TFF rows for this contract since 2022-11 (below reporting thresholds); the only micro yield in TFF is 'MICRO 10 YEAR YIELD' (04360Y). |
| market_maker_program | True |  | 2021-08-16 .. 2028-02-29 (successive extensions) | cftc_rules0706233776.pdf.txt; cftc_rules0708269230.pdf.txt | Micro Treasury Yield Futures Market Maker Program / Yield Futures Market Maker Program; in force through the pilot window. For 5YY: quoting obligations only via the 10Y-5YY inter-commodity spread; fee waivers for 5YY Globex volume on meeting Tier 1 10Y-5YY obligations. See A1_rates.md F7. |
| hft_automated_share | null (unknown) | % of volume |  |  | No automated or HFT share published for the micro yields (Haynes-Roberts and JSR predate them). Market makers present by program (F7). |
| median_spread_ticks_main | null (unknown) | ticks |  |  | No published spread found (searched CME articles, MM program filings, one WebSearch on micro yield spreads). MM program obligations bound quoted widths only for participants meeting them, and for this tenor only via spreads against 10Y. |
| depth_best_level | null (unknown) | contracts |  | cftc_rules0706233776.pdf.txt | No published depth figure. MM program minimum sizes (10Y outright Tier 1: 10 contracts; Tier 2: 150; ETH: 5) are program terms, not measured depth. |
| touch_queue_size | null (unknown) | contracts |  |  | Not published. |
| brokertec_link | Final settlement to the BrokerTec US Treasury Benchmark (15-minute VWAY of on-the-run cash trades before 3:00 p.m. ET); daily settlement 30-second VWAP before 2:00 p.m. CT |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Price is yield, so it moves opposite to ZF futures prices. See F11. |
| jump_frequency | null (unknown) | days per year with /daily return/ > 4 SD | 2019-2024 |  | No owned bars (A0) and no published count found; product launched 2021-08-16, so 2019-2021 do not exist for it. The full-size cousin's counts are in A0. |
| limit_hit_days_2019_2024 | null (unknown) | days per year | 2019-2024 |  | No CME notice, regulator report or press item reporting a Rule 589 halt in this product in 2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8. |
| weekend_gap_exposure | null (unknown) |  |  |  | Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a primary source either way, so recorded as unknown (expected no, but unsourced). |
| median_spread_ticks_overnight | null (unknown) | ticks |  |  | No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, JSR 2015. |
| volume_per_minute | null (unknown) | contracts per minute |  |  | Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute is derivable there), none for the micro yields. |
| scheduled_releases_per_week | 0.23 | auctions of the matching Treasury tenor per week (about 1 per month) | Treasury tentative schedule Aug 2026 - Jan 2027 | ust_tentative_auction_schedule.pdf.txt | Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). Whether auctions count as product-specific releases or as the shared US macro calendar is for the scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills several per week. No other product-specific scheduled release found. |
| microstructure_research | No study on this product found. Evidence on the full-size cousin ZF (FAM relation, different design): see F12 R1-R3, R7-R9. CLASS: R10, R11. |  |  | reports/stage_e28_briefs/A1_rates.md (section F12) | Study IDs refer to the F12 table, which carries each study's file, quote, relation and result. |

### 10Y

| Field | Value | Unit | Window | Source | Note |
|---|---|---|---|---|---|
| product_name | Micro 10-Year Yield Futures (titled '10-Year Yield Futures' since 2024-02-05) |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Title change: CBOT 24-116 (cftc_rules02132411742.pdf.txt) 'Effective Monday, February 5, 2024, the Exchange implemented administrative amendments to the contract title of all Micro Yield futures contracts'. |
| product_code | 10Y |  |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| tick_size | 0.001 | index points of yield (0.1 basis point) |  | cftc_ptc072921cbotdcm001.pdf.txt | Rulebook text in the filing, Rule 80102.C-83102.C; spec table: 'All delivery months: 0.001 Index points (1/10th basis point per annum) =' $1.00. |
| tick_value | 1.0 | USD per contract |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| contract_size | $1,000 x index points ($10 DV01) |  |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| settlement | cash-settled to the BrokerTec US Treasury benchmark (3:00 p.m. ET VWAY) of the on-the-run issue; 2 nearest monthly contracts; terminates last business day of the month |  |  | cftc_ptc072921cbotdcm001.pdf.txt | 'The Contracts settle to the most recently auctioned On-the-Run CUSIP at each tenor, which updates monthly and the expectation is that the front contract month will dominate trading'. |
| launch_date | 2021-08-16 | trade date |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| globex_60_dates_in_2023-11..2024-02 | True |  | 2023-11-01..2024-02-29 | cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Launch 2021-08-16 and continuous listing; ADV 7,282 in Nov 2023. |
| match_algorithm | FIFO |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Exhibit 2 table cell labelled 'CME GLOBEX MATCHING ALGORITHM' (label split over three lines in the text layer). |
| trading_hours | Sunday-Friday 6:00 p.m. - 5:00 p.m. ET (5:00 p.m. - 4:00 p.m. CT); Mon-Thu 5:00-6:00 p.m. ET maintenance |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Exhibit 2, row CME Globex; next cell: 'Monday - Thursday 5:00 - 6:00 p.m. ET (4:00 - 5:00 p.m. CT) daily maintenance period'. |
| price_limits | daily_limit: null (unknown); dynamic_variant: 20 basis points; halt: 2-minute halt (Rule 589.D) |  | Rule 589 table Wayback capture 2024-10-01; listing filing 2021 | cme_special_price_fluctuation_limits.xlsx | Same 20 bp variant in the 2021 listing filing Appendix D. 20 bp = 200 ticks of 0.1 bp. |
| adv_published_latest | YTD_Jan-Sep_2026: 1277; Sep_2026: 1398 | contracts per day | Jan-Sep 2026 | cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt | Row label in report '10Y YIELD'. |
| adv_2022_11_2023_10 | YTD_Jan-Aug_2023: 4230; Nov_2022: 2481.62; Oct_2023: 9071 | contracts per day | 2022-11..2023-10 (pieces published) | cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt; cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | No owned bars (A0 line 211). |
| open_interest | Mar_2023: 2921; Oct_2025: 3454 | contracts, month-end | Mar 2023; Oct 2025 | cme_Web_OI_Report_CBOT_20240416143839.pdf.txt; cme_Web_OI_Report_CBOT_20251112073031.pdf.txt |  |
| retail_share | null (unknown) | % of volume |  | mondovisione_cme_micro_yield_launch_2021-06-09.html.txt | No retail percentage published in any file found (CME launch, 30k and 1M-contract releases, CBOT filings). CME targets individual traders among others; it does not describe the product as predominantly retail. |
| commercial_hedger_share | null (unknown) | % of OI |  |  | CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset manager, leveraged funds, other reportables, nonreportables. See tff_category_shares. |
| tff_category_shares | see F6 table | % of open interest (mean of weekly values) | 2022-11..2023-10 and 2025-10..2026-10 | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | CFTC Traders in Financial Futures, futures only; summary in work/A1_rates/A1_rates_tff_summary.json |
| nonreportable_share | 2022-11..2023-10: long: 31.2; short: 29.7; latest_52w: long: 16.9; short: 41.9 | % of open interest (mean of weekly values) | 2022-11-01..2023-10-31 (32 reports); 2025-10-21..2026-10-06 (34 reports) | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | Computed by work/A1_rates/A1_rates_tff.py as the mean of pct_of_oi_nonrept_long_all / _short_all (CFTC TFF futures-only, Socrata gpe5-46if). Share of OI, not of volume. Published only in weeks that met CFTC reporting criteria (32 of 53 weeks in 2022-11..2023-10; 34 weeks in the latest window). |
| market_maker_program | True |  | 2021-08-16 .. 2028-02-29 (successive extensions) | cftc_rules0706233776.pdf.txt; cftc_rules0708269230.pdf.txt | Micro Treasury Yield Futures Market Maker Program / Yield Futures Market Maker Program; in force through the pilot window. For 10Y: direct outright quoting tiers (Tier 1/2/3 RTH, ETH) plus 10Y legs of all three inter-commodity spreads; fee waivers; from Aug 2026 a $10,000 monthly incentive pool. See A1_rates.md F7. |
| hft_automated_share | null (unknown) | % of volume |  |  | No automated or HFT share published for the micro yields (Haynes-Roberts and JSR predate them). Market makers present by program (F7). |
| median_spread_ticks_main | 1.67 | ticks (average, not median; 0.167 bp / 0.1 bp tick) | 2024 (H1), RTH 7:00 a.m.-4:00 p.m. CT | cme_article_2023_yield_futures_macro_events.html.txt | CME marketing article (Wayback copy). Average daily range 'All other Days 8.17' bps in the same table. |
| depth_best_level | null (unknown) | contracts |  | cftc_rules0706233776.pdf.txt | No published depth figure. MM program minimum sizes (10Y outright Tier 1: 10 contracts; Tier 2: 150; ETH: 5) are program terms, not measured depth. |
| touch_queue_size | null (unknown) | contracts |  |  | Not published. |
| brokertec_link | Final settlement to the BrokerTec US Treasury Benchmark (15-minute VWAY of on-the-run cash trades before 3:00 p.m. ET); daily settlement 30-second VWAP before 2:00 p.m. CT |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Price is yield, so it moves opposite to ZN futures prices. See F11. |
| jump_frequency | null (unknown) | days per year with /daily return/ > 4 SD | 2019-2024 |  | No owned bars (A0) and no published count found; product launched 2021-08-16, so 2019-2021 do not exist for it. The full-size cousin's counts are in A0. |
| limit_hit_days_2019_2024 | null (unknown) | days per year | 2019-2024 |  | No CME notice, regulator report or press item reporting a Rule 589 halt in this product in 2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8. |
| weekend_gap_exposure | null (unknown) |  |  |  | Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a primary source either way, so recorded as unknown (expected no, but unsourced). |
| median_spread_ticks_overnight | null (unknown) | ticks |  |  | No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, JSR 2015. |
| volume_per_minute | null (unknown) | contracts per minute |  |  | Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute is derivable there), none for the micro yields. |
| scheduled_releases_per_week | 0.23 | auctions of the matching Treasury tenor per week (about 1 per month) | Treasury tentative schedule Aug 2026 - Jan 2027 | ust_tentative_auction_schedule.pdf.txt | Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). Whether auctions count as product-specific releases or as the shared US macro calendar is for the scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills several per week. No other product-specific scheduled release found. |
| microstructure_research | No study on this product found. Evidence on the full-size cousin ZN (FAM relation, different design): see F12 R1-R3, R7-R9. CLASS: R10, R11. |  |  | reports/stage_e28_briefs/A1_rates.md (section F12) | Study IDs refer to the F12 table, which carries each study's file, quote, relation and result. |

### 30Y

| Field | Value | Unit | Window | Source | Note |
|---|---|---|---|---|---|
| product_name | Micro 30-Year Yield Futures (titled '30-Year Yield Futures' since 2024-02-05) |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Title change: CBOT 24-116 (cftc_rules02132411742.pdf.txt) 'Effective Monday, February 5, 2024, the Exchange implemented administrative amendments to the contract title of all Micro Yield futures contracts'. |
| product_code | 30Y |  |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| tick_size | 0.001 | index points of yield (0.1 basis point) |  | cftc_ptc072921cbotdcm001.pdf.txt | Rulebook text in the filing, Rule 80102.C-83102.C; spec table: 'All delivery months: 0.001 Index points (1/10th basis point per annum) =' $1.00. |
| tick_value | 1.0 | USD per contract |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| contract_size | $1,000 x index points ($10 DV01) |  |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| settlement | cash-settled to the BrokerTec US Treasury benchmark (3:00 p.m. ET VWAY) of the on-the-run issue; 2 nearest monthly contracts; terminates last business day of the month |  |  | cftc_ptc072921cbotdcm001.pdf.txt | 'The Contracts settle to the most recently auctioned On-the-Run CUSIP at each tenor, which updates monthly and the expectation is that the front contract month will dominate trading'. |
| launch_date | 2021-08-16 | trade date |  | cftc_ptc072921cbotdcm001.pdf.txt |  |
| globex_60_dates_in_2023-11..2024-02 | null (unknown) |  | 2023-11-01..2024-02-29 | cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Launched 2021-08-16 and listed continuously, but published ADV only 48 in Nov 2023 and OI 29 (Feb 2024) / 22 (Mar 2024); whether trades occurred on >= 60 dates is not established from published aggregates. |
| match_algorithm | FIFO |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Exhibit 2 table cell labelled 'CME GLOBEX MATCHING ALGORITHM' (label split over three lines in the text layer). |
| trading_hours | Sunday-Friday 6:00 p.m. - 5:00 p.m. ET (5:00 p.m. - 4:00 p.m. CT); Mon-Thu 5:00-6:00 p.m. ET maintenance |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Exhibit 2, row CME Globex; next cell: 'Monday - Thursday 5:00 - 6:00 p.m. ET (4:00 - 5:00 p.m. CT) daily maintenance period'. |
| price_limits | daily_limit: null (unknown); dynamic_variant: 20 basis points; halt: 2-minute halt (Rule 589.D) |  | Rule 589 table Wayback capture 2024-10-01; listing filing 2021 | cme_special_price_fluctuation_limits.xlsx | Same 20 bp variant in the 2021 listing filing Appendix D. 20 bp = 200 ticks of 0.1 bp. |
| adv_published_latest | YTD_Jan-Sep_2026: 0; Sep_2026: 2 | contracts per day | Jan-Sep 2026 | cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt | Row label in report '30Y YIELD'. |
| adv_2022_11_2023_10 | YTD_Jan-Aug_2023: 47; Nov_2022: 201.1; Oct_2023: 103.5 | contracts per day | 2022-11..2023-10 (pieces published) | cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt; cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | No owned bars (A0 line 211). |
| open_interest | Mar_2023: 178; Oct_2025: 9 | contracts, month-end | Mar 2023; Oct 2025 | cme_Web_OI_Report_CBOT_20240416143839.pdf.txt; cme_Web_OI_Report_CBOT_20251112073031.pdf.txt |  |
| retail_share | null (unknown) | % of volume |  | mondovisione_cme_micro_yield_launch_2021-06-09.html.txt | No retail percentage published in any file found (CME launch, 30k and 1M-contract releases, CBOT filings). CME targets individual traders among others; it does not describe the product as predominantly retail. |
| commercial_hedger_share | null (unknown) | % of OI |  |  | CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset manager, leveraged funds, other reportables, nonreportables. See tff_category_shares. |
| tff_category_shares | null (unknown) | % of open interest | 2022-11..2026-10 | cftc_tff_04_market_list.json; cftc_tff_rates_market_list.json | No CFTC TFF rows for this contract since 2022-11 (below reporting thresholds); the only micro yield in TFF is 'MICRO 10 YEAR YIELD' (04360Y). |
| nonreportable_share | null (unknown) | % of open interest | 2022-11..2026-10 | cftc_tff_04_market_list.json; cftc_tff_rates_market_list.json | No CFTC TFF rows for this contract since 2022-11 (below reporting thresholds); the only micro yield in TFF is 'MICRO 10 YEAR YIELD' (04360Y). |
| market_maker_program | True |  | 2021-08-16 .. 2028-02-29 (successive extensions) | cftc_rules0706233776.pdf.txt; cftc_rules0708269230.pdf.txt | Micro Treasury Yield Futures Market Maker Program / Yield Futures Market Maker Program; in force through the pilot window. For 30Y: quoting obligations only via the 30Y-10Y inter-commodity spread. See A1_rates.md F7. |
| hft_automated_share | null (unknown) | % of volume |  |  | No automated or HFT share published for the micro yields (Haynes-Roberts and JSR predate them). Market makers present by program (F7). |
| median_spread_ticks_main | null (unknown) | ticks |  |  | No published spread found (searched CME articles, MM program filings, one WebSearch on micro yield spreads). MM program obligations bound quoted widths only for participants meeting them, and for this tenor only via spreads against 10Y. |
| depth_best_level | null (unknown) | contracts |  | cftc_rules0706233776.pdf.txt | No published depth figure. MM program minimum sizes (10Y outright Tier 1: 10 contracts; Tier 2: 150; ETH: 5) are program terms, not measured depth. |
| touch_queue_size | null (unknown) | contracts |  |  | Not published. |
| brokertec_link | Final settlement to the BrokerTec US Treasury Benchmark (15-minute VWAY of on-the-run cash trades before 3:00 p.m. ET); daily settlement 30-second VWAP before 2:00 p.m. CT |  |  | cftc_ptc072921cbotdcm001.pdf.txt | Price is yield, so it moves opposite to ZB futures prices. See F11. |
| jump_frequency | null (unknown) | days per year with /daily return/ > 4 SD | 2019-2024 |  | No owned bars (A0) and no published count found; product launched 2021-08-16, so 2019-2021 do not exist for it. The full-size cousin's counts are in A0. |
| limit_hit_days_2019_2024 | null (unknown) | days per year | 2019-2024 |  | No CME notice, regulator report or press item reporting a Rule 589 halt in this product in 2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8. |
| weekend_gap_exposure | null (unknown) |  |  |  | Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a primary source either way, so recorded as unknown (expected no, but unsourced). |
| median_spread_ticks_overnight | null (unknown) | ticks |  |  | No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, JSR 2015. |
| volume_per_minute | null (unknown) | contracts per minute |  |  | Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute is derivable there), none for the micro yields. |
| scheduled_releases_per_week | 0.23 | auctions of the matching Treasury tenor per week (about 1 per month) | Treasury tentative schedule Aug 2026 - Jan 2027 | ust_tentative_auction_schedule.pdf.txt | Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). Whether auctions count as product-specific releases or as the shared US macro calendar is for the scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills several per week. No other product-specific scheduled release found. |
| microstructure_research | No study on this product found. Evidence on the full-size cousin ZB (FAM relation, different design): see F12 R1-R3, R7-R9. CLASS: R10, R11. |  |  | reports/stage_e28_briefs/A1_rates.md (section F12) | Study IDs refer to the F12 table, which carries each study's file, quote, relation and result. |

### ZT

| Field | Value | Unit | Window | Source | Note |
|---|---|---|---|---|---|
| product_name | Short-Term U.S. Treasury Note Futures (2-Year) |  |  | cbot_rulebook_II_21.pdf.txt | CBOT rulebook chapter 21; Wayback capture 2026-04-22 of CBOT rulebook II/21.pdf |
| product_code | ZT |  |  | cme_SER-7193.html.txt | SER-7193 product table lists the Globex code next to the product title (ZT, ZF, ZN, ZB). |
| tick_size | 0.00390625 | points of par (1/8 of 1/32) |  | cbot_rulebook_II_21.pdf.txt | Wayback capture 2026-04-22 of CBOT rulebook II/21.pdf |
| tick_value | 7.8125 | USD per contract |  | cbot_rulebook_II_21.pdf.txt |  |
| contract_size | 200000 | USD face value |  | cbot_rulebook_II_21.pdf.txt |  |
| settlement | physical delivery of eligible Treasury securities; March-June-September-December expiries |  |  | cbot_rulebook_II_21.pdf.txt | Rulebook chapter delivery rules; quarterly cycle per CBOT 2015 TN filing ('Nearest 3 months in the March-June-September-December quarterly cycle', cftc_ptc122315cbotdcm001.pdf.txt) for the cousin TN; not quoted for this product. |
| launch_date | null (unknown) |  |  | cme_understanding_treasury_futures.pdf.txt | Exact launch year not found in fetched files; listed and traded since at least 2014 (CBOT 14-348 algorithm filing names it) and through 2023-2026 (CME ADV reports). |
| globex_60_dates_in_2023-11..2024-02 | True |  | 2023-11-01..2024-02-29 | cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Launch long before 2023-11 and continuous listing; November 2023 ADV in the millions (published aggregate; no market data read). |
| match_algorithm | partial pro-rata (CME 'K' configurable / split FIFO-pro-rata family); exact current parameters not found |  |  | cftc_two_year_analysis_2019.pdf.txt | Databento 2025-08-01 (databento_cme_matching_algorithms.html.txt) lists 'Configurable' with 'Popular CME products: ZT, ZQ, ZC, ZS, ZW outrights'. CME 2008 notice: K algorithm 'was only applied to the 2-Year U.S. Treasury Note futures'. GCC Product Resources page (authoritative per CBOT Rule 580) is on blocked cmegroup.com. |
| trading_hours | Sunday 5:00 p.m. - Friday 4:00 p.m. CT, daily maintenance 4:00-5:00 p.m. CT |  |  | cftc_ptc1005237330.pdf.txt | Quote is from the 2023 CBOT filing for Monday weekly options on these futures; futures spec page blocked. Cousin Micro Ultra futures filing gives the same schedule (cftc_ptc02232412041.pdf.txt). |
| price_limits | daily_limit: null (unknown); dynamic_variant: 0.75 of 1 point; halt: 2-minute halt when traded/bid/offered through the dynamic limit in a rolling 60-minute look-back |  | Rule 589 table Wayback capture 2024-10-01 | cme_special_price_fluctuation_limits.xlsx | Sheet 'Interest Rates', column 'Dynamically Calculated Variant - All Hours'. Dynamic limits in force since trade date 2020-07-27 (SER-8542). No fixed daily limit value found. |
| adv_published_latest | YTD_Jan-Sep_2026: 1317555; Sep_2026: 1250894 | contracts per day, all expiries | Jan-Sep 2026 | cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt | CME Group Exchange ADV Report - Monthly, September 2026 (Wayback capture 2026-10-11). |
| adv_2022_11_2023_10 | YTD_Jan-Aug_2023: 797491; Nov_2022: 882991.9; Oct_2023: 675122.09 | contracts per day, all expiries | 2022-11..2023-10 (pieces published; no 12-month average printed) | cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt; cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Aug 2023 report columns: AUG 2023, AUG 2022, %, JUL 2023, %, YTD 2023, YTD 2022, %. Nov 2023 report columns: NOV 2023, NOV 2022, %, OCT 2023, %, YTD 2023, YTD 2022, %. Owned-bar ADV for the standard window is A0's. |
| open_interest | Mar_2023: 2373250; Oct_2025: 4606433 | contracts, month-end | Mar 2023; Oct 2025 | cme_Web_OI_Report_CBOT_20240416143839.pdf.txt; cme_Web_OI_Report_CBOT_20251112073031.pdf.txt |  |
| retail_share | null (unknown) | % of volume |  |  | No CME or regulator retail-share figure found (searched CME press releases and rates reviews, CBOT filings, CFTC OCE papers). Proxy: Haynes-Roberts small manual traders share (see hft_automated_share note) and TFF nonreportable share of OI. |
| commercial_hedger_share | null (unknown) | % of OI |  |  | CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset manager, leveraged funds, other reportables, nonreportables. See tff_category_shares. |
| tff_category_shares | see F6 table | % of open interest (mean of weekly values) | 2022-11..2023-10 and 2025-10..2026-10 | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | CFTC Traders in Financial Futures, futures only; summary in work/A1_rates/A1_rates_tff_summary.json |
| nonreportable_share | 2022-11..2023-10: long: 7.7; short: 6.0; latest_52w: long: 5.1; short: 3.2 | % of open interest (mean of weekly values) | 2022-11-01..2023-10-31 (53 reports); 2025-10-07..2026-10-13 (54 reports) | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | Computed by work/A1_rates/A1_rates_tff.py as the mean of pct_of_oi_nonrept_long_all / _short_all (CFTC TFF futures-only, Socrata gpe5-46if). Share of OI, not of volume. |
| market_maker_program | False |  |  |  | No market-maker or incentive program for this outright found (CFTC rule filings searched by two WebSearch queries; programs found were for the micro yields and the Micro Ultra contracts). Not a full scan of CBOT incentive filings. |
| hft_automated_share | ZT not tabulated by product in Haynes-Roberts (only the top 3 by volume per group: 10 Yr, 5 Yr). Group 'Interest Rate - US Treasury' ATS share 64.0% (2012-14) and 68.4% (2014-16) of volume. | % of volume | 2012-11..2016-10 (Haynes-Roberts); 2014 (JSR); 2012-2021 (FEDS 2025-038) | cftc_oce_automatedtrading_update_2017.pdf.txt; jsr_oct15_2014.pdf.txt; feds_2025-038_tsy_futures_liquidity_march2020.pdf.txt | ATS = automated trading system (not only HFT). Quote is Table 2 (Non-Electronic %, ATS %, Manual %; two periods). |
| median_spread_ticks_main | 1 | ticks (best bid/offer spread equals the minimum tick > 99% of the day) | 2018, RTH 7:00-16:00 CT | cme_ir_futures_liquidity_update_2018.html.txt | Median not published; value inferred from '>99% of each trading day at the minimum increment'. ZN also: FEDS 2025-038 '94% of bid-ask spread observations are "stuck" at one tick' (March 2020). ZT's tick was halved in early 2019 (abstract-only, R8), after which no ZT spread figure was found. |
| depth_best_level | best_level: 99471; best_3_levels: 131254 | contracts (average book size, front month outright) | 2018, RTH 7:00 a.m.-4:00 p.m. CT | cme_ir_futures_liquidity_update_2018.html.txt | Columns: best level 2016, 2017, 2018, % growth; best 3 levels 2016, 2017, 2018, % growth. Not split by side; definition per CME. No later figure found. ZT figure predates the early-2019 tick halving. |
| touch_queue_size | 99471 | contracts | 2018 RTH | cme_ir_futures_liquidity_update_2018.html.txt | Same as depth_best_level; no separate queue statistic published. |
| brokertec_link | Cash Treasuries trade on BrokerTec (CME Group; on CME Globex since 2021-02-01); futures and cash share price discovery; deliverable basket links futures to cash notes/bonds |  |  | cftc_ptc072921cbotdcm001.pdf.txt; feds_2018-065_price_pressure_term_structure.pdf.txt | See A1_rates.md F11. |
| jump_frequency | null (unknown) | days per year with /daily return/ > 4 SD | 2019-2024 | reports/stage_e28_briefs/A0_contract_stats.md | Owned-bar counts are A0's (A0_contract_stats.md lines 148-155); not computed here. No published count found. |
| limit_hit_days_2019_2024 | null (unknown) | days per year | 2019-2024 |  | No CME notice, regulator report or press item reporting a Rule 589 halt in this product in 2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8. |
| weekend_gap_exposure | null (unknown) |  |  |  | Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a primary source either way, so recorded as unknown (expected no, but unsourced). |
| median_spread_ticks_overnight | null (unknown) | ticks |  |  | No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, JSR 2015. |
| volume_per_minute | null (unknown) | contracts per minute |  |  | Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute is derivable there), none for the micro yields. |
| scheduled_releases_per_week | 0.23 | auctions of the matching Treasury tenor per week (about 1 per month) | Treasury tentative schedule Aug 2026 - Jan 2027 | ust_tentative_auction_schedule.pdf.txt | Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). Whether auctions count as product-specific releases or as the shared US macro calendar is for the scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills several per week. No other product-specific scheduled release found. |
| microstructure_research | R1 (COUSIN, NEG), R2 (COUSIN, NEG), R3 (COUSIN, NULL), R4 (SAME, NULL: matching-algorithm mechanics), R7 (SAME, POS weekly), R8 (SAME, NULL mechanism; abstract only), R9 (SAME/COUSIN, POS, abstract only), R14 (CLASS theory for pro-rata) |  |  | reports/stage_e28_briefs/A1_rates.md (section F12) | Study IDs refer to the F12 table, which carries each study's file, quote, relation and result. |

### ZF

| Field | Value | Unit | Window | Source | Note |
|---|---|---|---|---|---|
| product_name | Medium-Term U.S. Treasury Note Futures (5-Year) |  |  | cbot_rulebook_II_20.pdf.txt | CBOT rulebook chapter 20; Wayback capture 2024-03-01 of CBOT rulebook II/20.pdf |
| product_code | ZF |  |  | cme_SER-7193.html.txt | SER-7193 product table lists the Globex code next to the product title (ZT, ZF, ZN, ZB). |
| tick_size | 0.0078125 | points of par (1/4 of 1/32) |  | cbot_rulebook_II_20.pdf.txt | Wayback capture 2024-03-01 of CBOT rulebook II/20.pdf |
| tick_value | 7.8125 | USD per contract |  | cbot_rulebook_II_20.pdf.txt |  |
| contract_size | 100000 | USD face value |  | cbot_rulebook_II_20.pdf.txt |  |
| settlement | physical delivery of eligible Treasury securities; March-June-September-December expiries |  |  | cbot_rulebook_II_20.pdf.txt | Rulebook chapter delivery rules; quarterly cycle per CBOT 2015 TN filing ('Nearest 3 months in the March-June-September-December quarterly cycle', cftc_ptc122315cbotdcm001.pdf.txt) for the cousin TN; not quoted for this product. |
| launch_date | null (unknown) |  |  | cme_understanding_treasury_futures.pdf.txt | Exact launch year not found in fetched files; listed and traded since at least 2014 (CBOT 14-348 algorithm filing names it) and through 2023-2026 (CME ADV reports). |
| globex_60_dates_in_2023-11..2024-02 | True |  | 2023-11-01..2024-02-29 | cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Launch long before 2023-11 and continuous listing; November 2023 ADV in the millions (published aggregate; no market data read). |
| match_algorithm | FIFO (outrights) |  |  | cftc_two_year_analysis_2019.pdf.txt | Databento 2025-08-01: FIFO 'Popular products: ES, NQ, ZN, ZF, ZB, CL outrights'. Calendar spreads 20% FIFO / 80% pro-rata since 2014-10-06 (CBOT 14-348). |
| trading_hours | Sunday 5:00 p.m. - Friday 4:00 p.m. CT, daily maintenance 4:00-5:00 p.m. CT |  |  | cftc_ptc1005237330.pdf.txt | Quote is from the 2023 CBOT filing for Monday weekly options on these futures; futures spec page blocked. Cousin Micro Ultra futures filing gives the same schedule (cftc_ptc02232412041.pdf.txt). |
| price_limits | daily_limit: null (unknown); dynamic_variant: 1.50 points; halt: 2-minute halt when traded/bid/offered through the dynamic limit in a rolling 60-minute look-back |  | Rule 589 table Wayback capture 2024-10-01 | cme_special_price_fluctuation_limits.xlsx | Sheet 'Interest Rates', column 'Dynamically Calculated Variant - All Hours'. Dynamic limits in force since trade date 2020-07-27 (SER-8542). No fixed daily limit value found. |
| adv_published_latest | YTD_Jan-Sep_2026: 1938361; Sep_2026: 1913161 | contracts per day, all expiries | Jan-Sep 2026 | cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt | CME Group Exchange ADV Report - Monthly, September 2026 (Wayback capture 2026-10-11). |
| adv_2022_11_2023_10 | YTD_Jan-Aug_2023: 1542263; Nov_2022: 1659547.95; Oct_2023: 1335160.5 | contracts per day, all expiries | 2022-11..2023-10 (pieces published; no 12-month average printed) | cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt; cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Aug 2023 report columns: AUG 2023, AUG 2022, %, JUL 2023, %, YTD 2023, YTD 2022, %. Nov 2023 report columns: NOV 2023, NOV 2022, %, OCT 2023, %, YTD 2023, YTD 2022, %. Owned-bar ADV for the standard window is A0's. |
| open_interest | Mar_2023: 4415991; Oct_2025: 6990134 | contracts, month-end | Mar 2023; Oct 2025 | cme_Web_OI_Report_CBOT_20240416143839.pdf.txt; cme_Web_OI_Report_CBOT_20251112073031.pdf.txt |  |
| retail_share | null (unknown) | % of volume |  |  | No CME or regulator retail-share figure found (searched CME press releases and rates reviews, CBOT filings, CFTC OCE papers). Proxy: Haynes-Roberts small manual traders share (see hft_automated_share note) and TFF nonreportable share of OI. |
| commercial_hedger_share | null (unknown) | % of OI |  |  | CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset manager, leveraged funds, other reportables, nonreportables. See tff_category_shares. |
| tff_category_shares | see F6 table | % of open interest (mean of weekly values) | 2022-11..2023-10 and 2025-10..2026-10 | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | CFTC Traders in Financial Futures, futures only; summary in work/A1_rates/A1_rates_tff_summary.json |
| nonreportable_share | 2022-11..2023-10: long: 7.6; short: 7.5; latest_52w: long: 6.5; short: 5.0 | % of open interest (mean of weekly values) | 2022-11-01..2023-10-31 (53 reports); 2025-10-07..2026-10-13 (54 reports) | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | Computed by work/A1_rates/A1_rates_tff.py as the mean of pct_of_oi_nonrept_long_all / _short_all (CFTC TFF futures-only, Socrata gpe5-46if). Share of OI, not of volume. |
| market_maker_program | False |  |  |  | No market-maker or incentive program for this outright found (CFTC rule filings searched by two WebSearch queries; programs found were for the micro yields and the Micro Ultra contracts). Not a full scan of CBOT incentive filings. |
| hft_automated_share | Haynes-Roberts 2017 Table 3: '5 Yr Note 360 378 50.5 53.2 32.8 34.0 8.6 7.4' (total volume mm; ATS-ATS %; ATS-MAN %; MAN-MAN %; 2012-14 then 2014-16). Table 5: small manual traders 18.7% then 18.0% of volume. | % of volume | 2012-11..2016-10 (Haynes-Roberts); 2014 (JSR); 2012-2021 (FEDS 2025-038) | cftc_oce_automatedtrading_update_2017.pdf.txt; jsr_oct15_2014.pdf.txt; feds_2025-038_tsy_futures_liquidity_march2020.pdf.txt | ATS = automated trading system (not only HFT). Quote is Table 2 (Non-Electronic %, ATS %, Manual %; two periods). |
| median_spread_ticks_main | 1 | ticks (best bid/offer spread equals the minimum tick > 99% of the day) | 2018, RTH 7:00-16:00 CT | cme_ir_futures_liquidity_update_2018.html.txt | Median not published; value inferred from '>99% of each trading day at the minimum increment'. ZN also: FEDS 2025-038 '94% of bid-ask spread observations are "stuck" at one tick' (March 2020). ZT's tick was halved in early 2019 (abstract-only, R8), after which no ZT spread figure was found. |
| depth_best_level | best_level: 1319; best_3_levels: 6632 | contracts (average book size, front month outright) | 2018, RTH 7:00 a.m.-4:00 p.m. CT | cme_ir_futures_liquidity_update_2018.html.txt | Columns: best level 2016, 2017, 2018, % growth; best 3 levels 2016, 2017, 2018, % growth. Not split by side; definition per CME. No later figure found. |
| touch_queue_size | 1319 | contracts | 2018 RTH | cme_ir_futures_liquidity_update_2018.html.txt | Same as depth_best_level; no separate queue statistic published. |
| brokertec_link | Cash Treasuries trade on BrokerTec (CME Group; on CME Globex since 2021-02-01); futures and cash share price discovery; deliverable basket links futures to cash notes/bonds |  |  | cftc_ptc072921cbotdcm001.pdf.txt; feds_2018-065_price_pressure_term_structure.pdf.txt | See A1_rates.md F11. |
| jump_frequency | null (unknown) | days per year with /daily return/ > 4 SD | 2019-2024 | reports/stage_e28_briefs/A0_contract_stats.md | Owned-bar counts are A0's (A0_contract_stats.md lines 148-155); not computed here. No published count found. |
| limit_hit_days_2019_2024 | null (unknown) | days per year | 2019-2024 |  | No CME notice, regulator report or press item reporting a Rule 589 halt in this product in 2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8. |
| weekend_gap_exposure | null (unknown) |  |  |  | Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a primary source either way, so recorded as unknown (expected no, but unsourced). |
| median_spread_ticks_overnight | null (unknown) | ticks |  |  | No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, JSR 2015. |
| volume_per_minute | null (unknown) | contracts per minute |  |  | Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute is derivable there), none for the micro yields. |
| scheduled_releases_per_week | 0.23 | auctions of the matching Treasury tenor per week (about 1 per month) | Treasury tentative schedule Aug 2026 - Jan 2027 | ust_tentative_auction_schedule.pdf.txt | Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). Whether auctions count as product-specific releases or as the shared US macro calendar is for the scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills several per week. No other product-specific scheduled release found. |
| microstructure_research | R1 (COUSIN, NEG), R2 (COUSIN, NEG), R3 (COUSIN, NULL), R5 (SAME, NULL descriptive), R7 (SAME, POS weekly), R9 (SAME/COUSIN, POS, abstract only), R12 (SAME, NULL descriptive) |  |  | reports/stage_e28_briefs/A1_rates.md (section F12) | Study IDs refer to the F12 table, which carries each study's file, quote, relation and result. |

### ZN

| Field | Value | Unit | Window | Source | Note |
|---|---|---|---|---|---|
| product_name | U.S. Treasury Note Futures (6 1/2 to 7 3/4-Year), the 10-Year T-Note futures |  |  | cbot_rulebook_II_19.pdf.txt | CBOT rulebook chapter 19; Wayback capture 2023-12-06 of CBOT rulebook II/19.pdf; the Rule 589 table (capture 2024-10-01) titles it 'U.S. Treasury Note Futures (6½ to 8-Year)' and SER-7193 (2014) 'Long-Term U.S. Treasury Note Futures (6 ½ to 10-Year)': the deliverable window has changed over time |
| product_code | ZN |  |  | cme_SER-7193.html.txt | SER-7193 product table lists the Globex code next to the product title (ZT, ZF, ZN, ZB). |
| tick_size | 0.015625 | points of par (1/2 of 1/32) |  | cbot_rulebook_II_19.pdf.txt | Wayback capture 2023-12-06 of CBOT rulebook II/19.pdf |
| tick_value | 15.625 | USD per contract |  | cbot_rulebook_II_19.pdf.txt |  |
| contract_size | 100000 | USD face value |  | cbot_rulebook_II_19.pdf.txt |  |
| settlement | physical delivery of eligible Treasury securities; March-June-September-December expiries |  |  | cbot_rulebook_II_19.pdf.txt | Rulebook chapter delivery rules; quarterly cycle per CBOT 2015 TN filing ('Nearest 3 months in the March-June-September-December quarterly cycle', cftc_ptc122315cbotdcm001.pdf.txt) for the cousin TN; not quoted for this product. |
| launch_date | null (unknown) |  |  | cme_understanding_treasury_futures.pdf.txt | Exact launch year not found in fetched files; listed and traded since at least 2014 (CBOT 14-348 algorithm filing names it) and through 2023-2026 (CME ADV reports). |
| globex_60_dates_in_2023-11..2024-02 | True |  | 2023-11-01..2024-02-29 | cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Launch long before 2023-11 and continuous listing; November 2023 ADV in the millions (published aggregate; no market data read). |
| match_algorithm | FIFO (outrights) |  |  | cftc_two_year_analysis_2019.pdf.txt | Databento 2025-08-01: FIFO 'Popular products: ES, NQ, ZN, ZF, ZB, CL outrights'. Calendar spreads 20% FIFO / 80% pro-rata (CBOT 14-348 conformed 2-,3-,5-year spreads 'to the 10-Year U.S. Treasury Note calendar spread allocation mix'). |
| trading_hours | Sunday 5:00 p.m. - Friday 4:00 p.m. CT, daily maintenance 4:00-5:00 p.m. CT |  |  | cftc_ptc1005237330.pdf.txt | Quote is from the 2023 CBOT filing for Monday weekly options on these futures; futures spec page blocked. Cousin Micro Ultra futures filing gives the same schedule (cftc_ptc02232412041.pdf.txt). |
| price_limits | daily_limit: null (unknown); dynamic_variant: 2.00 points; halt: 2-minute halt when traded/bid/offered through the dynamic limit in a rolling 60-minute look-back |  | Rule 589 table Wayback capture 2024-10-01 | cme_special_price_fluctuation_limits.xlsx | Sheet 'Interest Rates', column 'Dynamically Calculated Variant - All Hours'. Dynamic limits in force since trade date 2020-07-27 (SER-8542). No fixed daily limit value found. |
| adv_published_latest | YTD_Jan-Sep_2026: 2595499; Sep_2026: 2646717 | contracts per day, all expiries | Jan-Sep 2026 | cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt | CME Group Exchange ADV Report - Monthly, September 2026 (Wayback capture 2026-10-11). |
| adv_2022_11_2023_10 | YTD_Jan-Aug_2023: 1971131; Nov_2022: 2174701.33; Oct_2023: 1961964.73 | contracts per day, all expiries | 2022-11..2023-10 (pieces published; no 12-month average printed) | cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt; cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Aug 2023 report columns: AUG 2023, AUG 2022, %, JUL 2023, %, YTD 2023, YTD 2022, %. Nov 2023 report columns: NOV 2023, NOV 2022, %, OCT 2023, %, YTD 2023, YTD 2022, %. Owned-bar ADV for the standard window is A0's. |
| open_interest | Mar_2023: 4248005; Oct_2025: 5511626 | contracts, month-end | Mar 2023; Oct 2025 | cme_Web_OI_Report_CBOT_20240416143839.pdf.txt; cme_Web_OI_Report_CBOT_20251112073031.pdf.txt |  |
| retail_share | null (unknown) | % of volume |  |  | No CME or regulator retail-share figure found (searched CME press releases and rates reviews, CBOT filings, CFTC OCE papers). Proxy: Haynes-Roberts small manual traders share (see hft_automated_share note) and TFF nonreportable share of OI. |
| commercial_hedger_share | null (unknown) | % of OI |  |  | CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset manager, leveraged funds, other reportables, nonreportables. See tff_category_shares. |
| tff_category_shares | see F6 table | % of open interest (mean of weekly values) | 2022-11..2023-10 and 2025-10..2026-10 | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | CFTC Traders in Financial Futures, futures only; summary in work/A1_rates/A1_rates_tff_summary.json |
| nonreportable_share | 2022-11..2023-10: long: 8.9; short: 9.0; latest_52w: long: 7.9; short: 6.7 | % of open interest (mean of weekly values) | 2022-11-01..2023-10-31 (53 reports); 2025-10-07..2026-10-13 (54 reports) | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | Computed by work/A1_rates/A1_rates_tff.py as the mean of pct_of_oi_nonrept_long_all / _short_all (CFTC TFF futures-only, Socrata gpe5-46if). Share of OI, not of volume. |
| market_maker_program | False |  |  |  | No market-maker or incentive program for this outright found (CFTC rule filings searched by two WebSearch queries; programs found were for the micro yields and the Micro Ultra contracts). Not a full scan of CBOT incentive filings. |
| hft_automated_share | Haynes-Roberts 2017 Table 3: '10 Yr Note 643 661 42.6 48.0 41.1 39.7 11.9 8.7' (ATS-ATS 42.6% then 48.0%; MAN-MAN 11.9% then 8.7%). Table 5: small manual traders 27.4% then 23.7%. JSR 2015: PTFs 68.4% of 10-year futures volume in the Oct 15 2014 event window and >50% generally. FEDS 2025-038: PTFs 70% of liquidity-providing volume; ~72% of passive orders in 2021. | % of volume | 2012-11..2016-10 (Haynes-Roberts); 2014 (JSR); 2012-2021 (FEDS 2025-038) | cftc_oce_automatedtrading_update_2017.pdf.txt; jsr_oct15_2014.pdf.txt; feds_2025-038_tsy_futures_liquidity_march2020.pdf.txt | ATS = automated trading system (not only HFT). Quote is Table 2 (Non-Electronic %, ATS %, Manual %; two periods). |
| median_spread_ticks_main | 1 | ticks (best bid/offer spread equals the minimum tick > 99% of the day) | 2018, RTH 7:00-16:00 CT | cme_ir_futures_liquidity_update_2018.html.txt | Median not published; value inferred from '>99% of each trading day at the minimum increment'. ZN also: FEDS 2025-038 '94% of bid-ask spread observations are "stuck" at one tick' (March 2020). ZT's tick was halved in early 2019 (abstract-only, R8), after which no ZT spread figure was found. |
| depth_best_level | best_level: 2507; best_3_levels: 12322 | contracts (average book size, front month outright) | 2018, RTH 7:00 a.m.-4:00 p.m. CT | cme_ir_futures_liquidity_update_2018.html.txt | Columns: best level 2016, 2017, 2018, % growth; best 3 levels 2016, 2017, 2018, % growth. Not split by side; definition per CME. No later figure found. |
| touch_queue_size | 2507 | contracts | 2018 RTH | cme_ir_futures_liquidity_update_2018.html.txt | Same as depth_best_level (average displayed size at the best level); no separate queue statistic published. ZN trade size: arXiv 2409.12721 'ZN 16.01 2' (mean, median contracts, 2024-04-09). |
| brokertec_link | Cash Treasuries trade on BrokerTec (CME Group; on CME Globex since 2021-02-01); futures and cash share price discovery; deliverable basket links futures to cash notes/bonds |  |  | cftc_ptc072921cbotdcm001.pdf.txt; feds_2018-065_price_pressure_term_structure.pdf.txt | See A1_rates.md F11. |
| jump_frequency | null (unknown) | days per year with /daily return/ > 4 SD | 2019-2024 | reports/stage_e28_briefs/A0_contract_stats.md | Owned-bar counts are A0's (A0_contract_stats.md lines 148-155); not computed here. No published count found. |
| limit_hit_days_2019_2024 | null (unknown) | days per year | 2019-2024 |  | No CME notice, regulator report or press item reporting a Rule 589 halt in this product in 2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8. |
| weekend_gap_exposure | null (unknown) |  |  |  | Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a primary source either way, so recorded as unknown (expected no, but unsourced). |
| median_spread_ticks_overnight | null (unknown) | ticks |  |  | No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, JSR 2015. |
| volume_per_minute | null (unknown) | contracts per minute |  |  | Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute is derivable there), none for the micro yields. |
| scheduled_releases_per_week | 0.23 | auctions of the matching Treasury tenor per week (about 1 per month) | Treasury tentative schedule Aug 2026 - Jan 2027 | ust_tentative_auction_schedule.pdf.txt | Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). Whether auctions count as product-specific releases or as the shared US macro calendar is for the scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills several per week. No other product-specific scheduled release found. |
| microstructure_research | R1 (SAME, NEG: passive fills adversely selected, ~1/2 tick), R2 (SAME, NEG: 199 of 224 fills adverse), R3 (SAME, NULL), R5 (SAME, NULL), R6 (SAME, NULL), R7 (SAME, POS weekly), R9 (SAME/COUSIN, POS, abstract only) |  |  | reports/stage_e28_briefs/A1_rates.md (section F12) | Study IDs refer to the F12 table, which carries each study's file, quote, relation and result. |

### ZB

| Field | Value | Unit | Window | Source | Note |
|---|---|---|---|---|---|
| product_name | U.S. Treasury Bond Futures |  |  | cbot_rulebook_II_18.pdf.txt | CBOT rulebook chapter 18; Wayback capture 2023-12-26 of CBOT rulebook II/18.pdf |
| product_code | ZB |  |  | cme_SER-7193.html.txt | SER-7193 product table lists the Globex code next to the product title (ZT, ZF, ZN, ZB). |
| tick_size | 0.03125 | points of par (1/32) |  | cbot_rulebook_II_18.pdf.txt | Wayback capture 2023-12-26 of CBOT rulebook II/18.pdf |
| tick_value | 31.25 | USD per contract |  | cbot_rulebook_II_18.pdf.txt |  |
| contract_size | 100000 | USD face value |  | cbot_rulebook_II_18.pdf.txt |  |
| settlement | physical delivery of eligible Treasury securities; March-June-September-December expiries |  |  | cbot_rulebook_II_18.pdf.txt | Rulebook chapter delivery rules; quarterly cycle per CBOT 2015 TN filing ('Nearest 3 months in the March-June-September-December quarterly cycle', cftc_ptc122315cbotdcm001.pdf.txt) for the cousin TN; not quoted for this product. |
| launch_date | 1977 | year |  | cme_understanding_treasury_futures.pdf.txt | Two-column layout: the sentence spans two lines with a chart label between them. |
| globex_60_dates_in_2023-11..2024-02 | True |  | 2023-11-01..2024-02-29 | cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Launch long before 2023-11 and continuous listing; November 2023 ADV in the millions (published aggregate; no market data read). |
| match_algorithm | FIFO (outrights) |  |  | cftc_two_year_analysis_2019.pdf.txt | Databento 2025-08-01: FIFO 'Popular products: ES, NQ, ZN, ZF, ZB, CL outrights'. The CFTC 2019 study used the 30-year bond contract as its FIFO control. |
| trading_hours | Sunday 5:00 p.m. - Friday 4:00 p.m. CT, daily maintenance 4:00-5:00 p.m. CT |  |  | cftc_ptc1005237330.pdf.txt | Quote is from the 2023 CBOT filing for Monday weekly options on these futures; futures spec page blocked. Cousin Micro Ultra futures filing gives the same schedule (cftc_ptc02232412041.pdf.txt). |
| price_limits | daily_limit: null (unknown); dynamic_variant: 4.50 points; halt: 2-minute halt when traded/bid/offered through the dynamic limit in a rolling 60-minute look-back |  | Rule 589 table Wayback capture 2024-10-01 | cme_special_price_fluctuation_limits.xlsx | Sheet 'Interest Rates', column 'Dynamically Calculated Variant - All Hours'. Dynamic limits in force since trade date 2020-07-27 (SER-8542). No fixed daily limit value found. |
| adv_published_latest | YTD_Jan-Sep_2026: 609587; Sep_2026: 609453 | contracts per day, all expiries | Jan-Sep 2026 | cme_Web_ADV_Report_CMEG_20261011043127.pdf.txt | CME Group Exchange ADV Report - Monthly, September 2026 (Wayback capture 2026-10-11). |
| adv_2022_11_2023_10 | YTD_Jan-Aug_2023: 405796; Nov_2022: 452782.14; Oct_2023: 554315 | contracts per day, all expiries | 2022-11..2023-10 (pieces published; no 12-month average printed) | cme_Web_ADV_Report_CBOT_20230924143322.pdf.txt; cme_Web_ADV_Report_CMEG_20231218025648.pdf.txt | Aug 2023 report columns: AUG 2023, AUG 2022, %, JUL 2023, %, YTD 2023, YTD 2022, %. Nov 2023 report columns: NOV 2023, NOV 2022, %, OCT 2023, %, YTD 2023, YTD 2022, %. Owned-bar ADV for the standard window is A0's. |
| open_interest | Mar_2023: 1191819; Oct_2025: 1920369 | contracts, month-end | Mar 2023; Oct 2025 | cme_Web_OI_Report_CBOT_20240416143839.pdf.txt; cme_Web_OI_Report_CBOT_20251112073031.pdf.txt |  |
| retail_share | null (unknown) | % of volume |  |  | No CME or regulator retail-share figure found (searched CME press releases and rates reviews, CBOT filings, CFTC OCE papers). Proxy: Haynes-Roberts small manual traders share (see hft_automated_share note) and TFF nonreportable share of OI. |
| commercial_hedger_share | null (unknown) | % of OI |  |  | CFTC TFF (the report for rates) has no commercial-hedger category: categories are dealer, asset manager, leveraged funds, other reportables, nonreportables. See tff_category_shares. |
| tff_category_shares | see F6 table | % of open interest (mean of weekly values) | 2022-11..2023-10 and 2025-10..2026-10 | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | CFTC Traders in Financial Futures, futures only; summary in work/A1_rates/A1_rates_tff_summary.json |
| nonreportable_share | 2022-11..2023-10: long: 14.4; short: 11.1; latest_52w: long: 13.3; short: 7.4 | % of open interest (mean of weekly values) | 2022-11-01..2023-10-31 (53 reports); 2025-10-07..2026-10-13 (54 reports) | cftc_tff_rates_2022-11_2023-10.json; cftc_tff_rates_latest.json | Computed by work/A1_rates/A1_rates_tff.py as the mean of pct_of_oi_nonrept_long_all / _short_all (CFTC TFF futures-only, Socrata gpe5-46if). Share of OI, not of volume. |
| market_maker_program | False |  |  |  | No market-maker or incentive program for this outright found (CFTC rule filings searched by two WebSearch queries; programs found were for the micro yields and the Micro Ultra contracts). Not a full scan of CBOT incentive filings. |
| hft_automated_share | ZB not tabulated by product in Haynes-Roberts (top 3 per group only). Group ATS share 64.0% then 68.4%. JSR 2015: PTFs >50% of futures volume across maturities. | % of volume | 2012-11..2016-10 (Haynes-Roberts); 2014 (JSR); 2012-2021 (FEDS 2025-038) | cftc_oce_automatedtrading_update_2017.pdf.txt; jsr_oct15_2014.pdf.txt; feds_2025-038_tsy_futures_liquidity_march2020.pdf.txt | ATS = automated trading system (not only HFT). Quote is Table 2 (Non-Electronic %, ATS %, Manual %; two periods). |
| median_spread_ticks_main | 1 | ticks (best bid/offer spread equals the minimum tick > 99% of the day) | 2018, RTH 7:00-16:00 CT | cme_ir_futures_liquidity_update_2018.html.txt | Median not published; value inferred from '>99% of each trading day at the minimum increment'. ZN also: FEDS 2025-038 '94% of bid-ask spread observations are "stuck" at one tick' (March 2020). ZT's tick was halved in early 2019 (abstract-only, R8), after which no ZT spread figure was found. |
| depth_best_level | best_level: 377; best_3_levels: 1898 | contracts (average book size, front month outright) | 2018, RTH 7:00 a.m.-4:00 p.m. CT | cme_ir_futures_liquidity_update_2018.html.txt | Columns: best level 2016, 2017, 2018, % growth; best 3 levels 2016, 2017, 2018, % growth. Not split by side; definition per CME. No later figure found. |
| touch_queue_size | 377 | contracts | 2018 RTH | cme_ir_futures_liquidity_update_2018.html.txt | Same as depth_best_level; no separate queue statistic published. |
| brokertec_link | Cash Treasuries trade on BrokerTec (CME Group; on CME Globex since 2021-02-01); futures and cash share price discovery; deliverable basket links futures to cash notes/bonds |  |  | cftc_ptc072921cbotdcm001.pdf.txt; feds_2018-065_price_pressure_term_structure.pdf.txt | See A1_rates.md F11. |
| jump_frequency | null (unknown) | days per year with /daily return/ > 4 SD | 2019-2024 | reports/stage_e28_briefs/A0_contract_stats.md | Owned-bar counts are A0's (A0_contract_stats.md lines 148-155); not computed here. No published count found. |
| limit_hit_days_2019_2024 | null (unknown) | days per year | 2019-2024 |  | No CME notice, regulator report or press item reporting a Rule 589 halt in this product in 2019-2024 was found (one WebSearch on Treasury futures halts and dynamic circuit breakers; SER-8542 read). Gap, not a finding of zero. See A1_rates.md F8. |
| weekend_gap_exposure | null (unknown) |  |  |  | Underlying is the US Treasury yield/price; no source fetched states that cash Treasuries trade while CME Globex is closed (Fri 4:00 p.m. CT to Sun 5:00 p.m. CT). Not crypto spot. Not verified from a primary source either way, so recorded as unknown (expected no, but unsourced). |
| median_spread_ticks_overnight | null (unknown) | ticks |  |  | No published overnight (ETH) spread found for this product; CME 2023 rates review shows ETH/ATH ADV only as charts. Searched CME liquidity reports (2018 update, 2023 review), FEDS 2025-038, JSR 2015. |
| volume_per_minute | null (unknown) | contracts per minute |  |  | Not published for this product in any source found; A0 owns 1-minute bars for ZT..ZB (volume per minute is derivable there), none for the micro yields. |
| scheduled_releases_per_week | 0.23 | auctions of the matching Treasury tenor per week (about 1 per month) | Treasury tentative schedule Aug 2026 - Jan 2027 | ust_tentative_auction_schedule.pdf.txt | Each nominal coupon tenor is auctioned once a month (6 auctions per tenor in the 6-month schedule). Whether auctions count as product-specific releases or as the shared US macro calendar is for the scorer. Other tenors' auctions (2,3,5,7,10,20,30-year) total about 7 per month across the curve; bills several per week. No other product-specific scheduled release found. |
| microstructure_research | R1 (COUSIN, NEG), R2 (COUSIN, NEG), R3 (COUSIN, NULL), R4 (control contract in a ZT study), R7 (SAME, POS weekly), R9 (SAME/COUSIN, POS, abstract only) |  |  | reports/stage_e28_briefs/A1_rates.md (section F12) | Study IDs refer to the F12 table, which carries each study's file, quote, relation and result. |

