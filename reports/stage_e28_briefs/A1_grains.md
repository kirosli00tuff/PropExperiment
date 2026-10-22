# A1_grains: Layer 1 fact sheets, grains family

Worker: A1_grains (Opus 5.5), Stage E.28 Part A, started 2026-10-21 05:31 PDT. Facts only; no scoring.
Candidates: micro grains MZC, MZS, MZW, MZL, MZM; mini grains XC, XK, XW; full-size ZC, ZS, ZW, ZL, ZM.
All source files are under reports/stage_e28_briefs/pages/A1_grains/ (log: log.tsv there, with URL, UTC and PDT
fetch times, method and sha256). PDFs were read through pdftotext (`*.txt` beside each PDF), HTML through a tag
stripper (`*.html.txt`). Quotes are verbatim from those files (whitespace collapsed). No market data was read.
Owned-bar magnitudes (sigma_1m, R_d, owned ADV, owned jump counts) belong to A0 and are not computed here.
cmegroup.com refuses this machine's IP, so CME pages and PDFs come from Wayback captures (capture time in the URL in
log.tsv). The CFTC COT shares below were computed by work/A1_grains/A1_grains_cot.py from CFTC's public annual
files (regulator publications, not market data); output in work/A1_grains/A1_grains_cot_out.txt.

## Headline facts for the gate

- Micro grains (MZC, MZS, MZW, MZL, MZM) were first listed for trade date 2025-02-24. They did not exist in
  2023-11-01..2024-02-29, so they cannot have traded on Globex on 60 dates in the pilot window.
  cme_ser9512_micro_grains.txt (SER#9512, January 30, 2025): "Effective Sunday, February 23, 2025, for trade date
  Monday, February 24, 2025, and pending all relevant Commodity Futures Trading Commission ("CFTC") regulatory
  review periods, The Board of Trade of the City of Chicago, Inc. ("CBOT" or "Exchange") will list the Micro Corn,
  Micro Wheat, Micro Soybean, Micro Soybean Oil, and Micro Soybean Meal Futures contracts". The subject line reads
  "Initial Listing of the Micro Corn, Micro Wheat, Micro Soybean, Micro Soybean Oil, and Micro Soybean Meal Futures
  Contracts". cme_pr_20250130_micro_grains.html.txt: "CME Group ... today announced it will launch a suite of micro
  grain and oilseed futures contracts on February 24, 2025".
- Mini grains: still listed. Mini Corn, Mini Soybean and Mini Wheat carry published ADV in both CME ADV reports
  read (August 2023 and September 2026; see F5), the Mini Soybean and Mini Wheat rulebook chapters were current
  in a December 2024 PDF, and SER 9151 (March 2023) amends "Mini-Sized Corn Futures XC YC 10B" and "Mini-Sized
  Soybean Futures XK YK 11B". Launch: mondo_cbot_mini_ag_2003.html.txt (CBOT release reprint, 25/03/2003): "the
  Chicago Board of Trade (CBOT) will launch mini-sized Corn, Wheat, and Soybean futures on Monday, April 7, 2003";
  mondo_cbot_mini_ag_ecbot_2007.html.txt (29/03/2007): "This is the first time these contracts will be available on
  an electronic platform"; the 2007-2009 CBOT program for "Mini-sized Corn, Wheat and Soybean futures contracts
  traded on the Globex platform" (F7) shows Globex trading by November 2007.
- ZC, ZS, ZW, ZL, ZM: listed throughout (owned bars from 2010 or 2019 per A0; CME ADV report rows in 2023 and 2026).

## F. Family-wide facts (referenced from each sheet)

### F1. Trading hours (all grain candidates)

- cme_ser9512_micro_grains.txt (micro grains, 2025): "CME Globex: Sunday - Friday: 7:00 p.m. - 7:45 a.m. CT and
  Monday - Friday, 8:30 a.m. - 1:20 p.m. CT". cme_faq_micro_ag.html.txt: "Trading hours for these contracts will
  match all other standard Agricultural contracts." and "All three classes of futures share the same expiration
  months and trading times, with Minis having a contract size 1/5 of the standard legacy contract and Micros having
  a contract size of 1/10 of standard futures."
- So the grain Globex day is two sessions with a 45-minute break (7:45-8:30 CT). In America/Vancouver time
  (CT minus 2 h): 17:00-05:45 and 06:30-11:20. The day session ends 11:20 PT, before the stage's main-session
  window ends (13:00 PT): the 11:20-13:00 PT part of that window has no grain trading. [Arithmetic from the quote.]
- Weekend: Globex closes Friday 1:20 p.m. CT and reopens Sunday 7:00 p.m. CT (same quote). The underlying cash
  grain markets are not continuous-trading 24/7 assets; no weekend-traded underlying was found (contrast crypto).
  Weekend news (weather, USDA does not publish on weekends in the calendars read) can still gap the Sunday open.
- Historical ETH share: cftc_rul093011cbot001.txt (CBOT Submission, 2011): "As of October 2011, CBOT Agricultural
  volume traded on the CME Globex Platform during "extended trading hours" (ETH, 6:00PM - 7: 15AM Chicago time) in
  Corn, Wheat, Soybean, Soybean Meal, and Soybean Oil futures comprises less than ten percent (10%) of total volume
  traded across those products." (2011 figure; no later figure found.)

### F2. Daily price limits (CBOT rulebook; minis and micros mirror the standard contract)

- Corn, cbot_rulebook_ch10_2019.txt (Chapter 10, Wayback capture 2019-03-14; the 2024/2025 copies were not
  archived), 10102.D: "Daily price limits for Corn futures are reset every six months. ... The average price is
  calculated based on the collected settlement prices and then multiplied by seven percent. The resulting number,
  rounded to the nearest 5 cents per bushel, or 20 cents per bushel, whichever is higher, will be the new initial
  price limit for Corn futures and will become effective on the first trading day in May ... There shall be no
  trading in Corn futures at a price more than the initial price limit above or below the previous day's settlement
  price. Should two or more corn futures contract months within the first five listed non-spot contracts ... settle
  at limit, the daily price limits for all contract months shall increase by 50 percent the next business day".
  Note: the floor (20 cents) is the 2019 text; a later amendment, if any, was not read.
- Soybeans, cbot_rulebook_ch11.txt (PDF dated 2024-12-31), 11102.D: "Initial and expanded daily price limits for
  Soybean futures are reset every six months." Floor: "multiplied by seven percent. The resulting number, rounded
  to the nearest 5 cents per bushel, or 50 cents per bushel, whichever is higher, will be the new initial" (limit);
  expanded = initial "multiplied by 1.5 and rounded up to the nearest 5 cents per bushel".
- Wheat (SRW), cbot_rulebook_ch14.txt (PDF dated 2023-02-13), 14102.D: 7% of average settlement, "rounded to the
  nearest 5 cents per bushel, or 30 cents per bushel, whichever is higher, will be the preliminary new initial price
  limit. This preliminary initial price limit and the preliminary initial price limit for KC HRW Wheat futures shall
  be compared, and the higher of the two shall be the new initial price limit for Wheat futures. The new expanded
  price limit shall be the new initial price limit multiplied by 1.5". Expansion trigger: "Should one or more Wheat
  futures contract months within the first five listed non-spot contracts settle at limit".
- Soybean oil, cbot_rulebook_ch12.txt (PDF dated 2022-12-19), 12102.D: "multiplied by seven percent. The resulting
  number, rounded to the nearest 0.5 cents per pound, or 2 cents per pound, whichever is higher, will be the new
  initial price limits".
- Soybean meal, cbot_rulebook_ch13.txt (PDF dated 2025-12-16), 13102.D: "rounded to the nearest 5 dollars per ton,
  or 20 dollars per ton, whichever is higher, will be the new initial price limits for Soybean Meal futures. The
  new expanded price limit shall be the new initial price limit multiplied by" 1.5.
- Minis: cbot_rulebook_ch11B.txt: "Daily price limits for mini-sized Soybean futures are the same as those for
  standard-sized" Soybean futures; cbot_rulebook_ch14B.txt: "Daily price limits for mini-sized Wheat futures are the
  same as those for standard-sized Wheat" futures. Micros: cme_faq_micro_ag.html.txt: "The daily price limits for
  Micro Agricultural contracts will mirror the daily price limits for the standard-sized contracts."
- Limit level as a share of price: about 7% of the trailing average price by construction (above the floor).

### F3. Scheduled product-specific releases (USDA)

- WASDE, monthly at noon ET. usda_wasde_report.html.txt: "The report is released monthly" ... "2026 WASDE Release
  Dates (12:00pm ET)" ... "In 2026 the WASDE report will be released on Jan. 12, Feb. 10, Mar. 10, Apr. 9, May 12,
  Jun. 11, Jul. 10, Aug. 12, Sep. 11, Oct. 9, Nov. 10, and Dec. 10." NASS Crop Production is released the same day
  at 12:00 pm ET (nass_calendar.html.txt, October 2026 calendar: "9|12:00 pm ET|- Cotton Ginnings|- Crop
  Production").
- Crop Progress, weekly on Mondays at 4:00 pm ET during the season. nass_calendar.html.txt (October 2026):
  "5|...|4:00 pm ET|- Crop Progress", "13|...|4:00 pm ET|- Crop Progress" (Tuesday after the Monday holiday),
  "19|4:00 pm ET|- Crop Progress", "26|4:00 pm ET|- Crop Progress". 4:00 pm ET is 3:00 pm CT, after the 1:20 pm
  CT close and before the 7:00 pm CT reopen: it lands in the evening session open. The season months (April to
  November) are [unverified]: the NASS Crop Progress page saved (nass_crop_progress.html.txt) does not state them.
- Grain Stocks, quarterly. nass_calendar.html.txt lists "09/30/26 Small Grains Summary and Grain Stocks (September
  2026)" among briefings. The quarterly dates (January, end-March with Prospective Plantings, end-June with Acreage,
  end-September) are [unverified]: only the September 2026 entry was read.
- Export Sales, weekly on Thursdays at 8:30 am ET. fas_export_sales_wb.html.txt (Wayback): "FAS publishes a weekly
  summary of export sales activity every Thursday at 8:30 a.m. ET, unless a change is announced." 8:30 ET is 7:30
  CT, inside the overnight session (before the 7:45 CT break).
- Count per week (a fact for C4): in season, Crop Progress (Monday) and Export Sales (Thursday) give two weekly
  product-specific USDA releases, plus WASDE/Crop Production monthly and Grain Stocks quarterly. Out of season
  (December to March), Export Sales is weekly and the rest monthly or quarterly. Whether each counts as "high
  impact" is for the scorer. Market-moving evidence: see F10 (Couleau et al. 2020: jumps cluster at report times; Lehecka et al. 2014 and Adjemian and Irwin 2018, abstracts).

### F4. Matching algorithm

- Vendor source (Databento blog, August 1, 2025), databento_cme_matching_algos.html.txt, under "Configurable":
  "Flexible algorithm with steps that can be turned on or off depending on product requirements. Popular CME
  products: ZT, ZQ, ZC, ZS, ZW outrights Volume: 12.7%". So ZC, ZS, ZW outrights use the Configurable algorithm
  (CME code K), not pure FIFO. Vendor source, not a CME document.
- CME definition, cme_wiki_supported_matching_algos.html.txt (CME client systems wiki): "The Configurable algorithm
  combines steps used with other CME Match Algorithms" ... "TOP - A TOP order has a price that betters the market at
  the time the order is received and is therefore designated as having priority." ... "Split - Based on product
  parameters, quantity is split between a FIFO step and a Pro Rata step. Product parameters can be zero for either
  FIFO or Pro Rata." ... "Pro Rata - ... All fills are rounded down to the nearest integer (which may be zero)." ...
  "Details of the K algorithm parameters and configuration for each product are available in the GCC Product
  Reference Sheet". The GCC sheet was not retrieved (the GCC resources page on atlassian returned HTTP 202 with no
  content, and WebFetch got an empty page), so no CME primary source for the grain parameters was read.
- Documented study: Peng (2022) dissertation, ideals_2022_three_essays_ag_liquidity.txt, footnote 5: "Throughout our
  sample period, the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and
  spread futures markets. The K algorithm first gives priority to the TOP order which is the first incoming limit
  order that betters the market (tightens the bid-ask spread). ... After the TOP order's quantity is exhausted, all
  tradable quantities in the resting of the order book are allocated on a "40 percent FIFO and 60 percent Pro-Rata"
  basis." Sample: 2018. A forum post (NexusFi, pointer only) gives the same 40/60 split for corn. Whether the split
  is unchanged in 2023-2026 is unverified.
- ZL, ZM, minis: covered only by Peng's "all of CBOT agricultural futures" (2018). Micros (2025): not found.
- Relevance (fact, not score): under a pro-rata step a 1-lot resting order gets a pro-rata fill rounded down to
  zero unless it is large relative to the level; a 1-lot order fills mainly through the FIFO share and the final
  FIFO residual step. [This is a reading of the CME definition above.]

### F5. Published ADV (CME Exchange ADV Report, Ag Products Futures, all expiries)

Two Wayback captures of CME's monthly report: cme_web_adv_report_2023-09.txt (report "August 2023") and
cme_web_adv_report_2026-10.txt (report "September 2026"). Columns: month ADV, same month prior year, change, prior
month, change, YTD this year, YTD prior year, change. Rows (verbatim):

| Report | Row |
|---|---|
| Aug 2023 | "CORN 320,584 305,121.35 5.1% 345,825 -7.3% 361,462 340,068 6.3%" |
| Aug 2023 | "SOYBEAN 189,515 155,104.91 22.2% 226,716.9 -16.4% 243,723 202,811 20.2%" |
| Aug 2023 | "CHI WHEAT 128,550 103,224.61 24.5% 139,457.85 -7.8% 128,465 110,180 16.6%" |
| Aug 2023 | "SOYBEAN OIL 124,353 114,709.74 8.4% 153,846.15 -19.2% 147,995 112,117 32.0%" |
| Aug 2023 | "SOYBEAN MEAL 137,490 106,543.78 29.0% 138,946.2 -1.0% 140,498 107,575 30.6%" |
| Aug 2023 | "MINI CORN 1,645 2,111.57 -22.1% 2,666.4 -38.3% 1,711 2,831 -39.6%" |
| Aug 2023 | "MINI SOYBEAN 1,955 2,725.13 -28.3% 3,263.15 -40.1% 2,077 2,951 -29.6%" |
| Aug 2023 | "MINI WHEAT 1,917 1,117.26 71.6% 2,708.55 -29.2% 1,523 1,302 17.0%" |
| Sep 2026 | "CORN 461,528 284,493.81 62.2% 602,349.38 -23.4% 500,733 455,813 9.9%" |
| Sep 2026 | "SOYBEAN 289,853 215,397.62 34.6% 266,856.24 8.6% 301,529 285,015 5.8%" |
| Sep 2026 | "CHI WHEAT 142,002 93,115.24 52.5% 217,204.05 -34.6% 176,115 138,609 27.1%" |
| Sep 2026 | "SOYBEAN OIL 185,351 172,338.33 7.6% 218,667.19 -15.2% 227,516 183,650 23.9%" |
| Sep 2026 | "SOYBEAN MEAL 213,478 170,665.29 25.1% 166,698.48 28.1% 185,193 172,222 7.5%" |
| Sep 2026 | "MINI CORN 1,318 1,048.71 25.6% 1,462.24 -9.9% 1,160 1,533 -24.3%" |
| Sep 2026 | "MINI SOYBEAN 1,587 1,362.9 16.4% 1,659.43 -4.4% 1,980 1,952 1.4%" |
| Sep 2026 | "MINI WHEAT 970 524.14 85.0% 1,122.86 -13.6% 922 958 -3.7%" |

- No micro grain row (MZC etc.) appears anywhere in the September 2026 report (grep for "MICRO" lists FX, equity,
  crypto, rates and gold micros only). Micro grain ADV: see the micro sheets.
- The 2023 YTD figures cover January-August 2023 (inside the standard window 2022-11..2023-10 but not the whole
  of it); the 2026 YTD figures cover January-September 2026. Neither is exactly a trailing 12 months.
- These are all-venue CME totals (Globex plus block/EFP); the report does not split Globex.

### F6. Participants: CFTC Commitments of Traders, Disaggregated, futures only

Computed from cftc_fut_disagg_txt_{2022,2023,2025,2026}.zip (CFTC annual files) by work/A1_grains/A1_grains_cot.py.
Share = mean over weekly reports of (long + short + 2 x spreading) / (2 x open interest), by category, so the five
shares sum to 1. "ProdMerc" = Producer/Merchant/Processor/User (the commercial hedger category); "NonRept" =
nonreportable positions (small-trader proxy). These are position shares, not volume shares.

| CFTC market (code) | Window (reports) | Mean OI | ProdMerc | Swap | Managed money | Other rept | NonRept |
|---|---|---|---|---|---|---|---|
| CORN - CBOT (002602) | 2022-11-01..2023-10-31 (53) | 1,300,458 | 0.384 | 0.108 | 0.254 | 0.140 | 0.114 |
| CORN - CBOT (002602) | 2025-10-14..2026-10-13 (53) | 1,732,054 | 0.349 | 0.116 | 0.287 | 0.156 | 0.092 |
| SOYBEANS - CBOT (005602) | 2022-11-01..2023-10-31 (53) | 676,863 | 0.438 | 0.118 | 0.222 | 0.133 | 0.089 |
| SOYBEANS - CBOT (005602) | 2025-10-14..2026-10-13 (53) | 969,705 | 0.427 | 0.118 | 0.258 | 0.132 | 0.066 |
| WHEAT-SRW - CBOT (001602) | 2022-11-01..2023-10-31 (53) | 363,360 | 0.168 | 0.140 | 0.448 | 0.145 | 0.099 |
| WHEAT-SRW - CBOT (001602) | 2025-10-14..2026-10-13 (53) | 471,403 | 0.174 | 0.148 | 0.479 | 0.128 | 0.071 |
| SOYBEAN OIL - CBOT (007601) | 2022-11-01..2023-10-31 (53) | 459,495 | 0.434 | 0.138 | 0.244 | 0.121 | 0.064 |
| SOYBEAN OIL - CBOT (007601) | 2025-10-14..2026-10-13 (53) | 668,533 | 0.415 | 0.120 | 0.288 | 0.130 | 0.047 |
| SOYBEAN MEAL - CBOT (026603) | 2022-11-01..2023-10-31 (53) | 449,564 | 0.419 | 0.111 | 0.263 | 0.123 | 0.084 |
| SOYBEAN MEAL - CBOT (026603) | 2025-10-14..2026-10-13 (53) | 592,664 | 0.412 | 0.126 | 0.277 | 0.120 | 0.065 |
| MINI SOYBEANS - CBOT (005603) | 2023-07-25..2023-09-26 (10 only) | 21,858 | 0.210 | 0.000 | 0.000 | 0.376 | 0.414 |
| MINI SOYBEANS - CBOT (005603) | 2026-05-05..2026-10-13 (24 only) | 27,728 | 0.184 | 0.000 | 0.000 | 0.453 | 0.362 |

- No separate CFTC market was found for mini corn, mini wheat or any micro grain in these files (grep of market
  names containing CORN, SOYBEAN, WHEAT lists only the rows above plus HRW, HRS and Black Sea wheat). Mini
  Soybeans is published only in some weeks (10 of 53 in the standard window), so its shares are thin.
- The "latest" window ends at the last report in the 2026 file (2026-10-13).

### F7. Market-maker and incentive programs (grains)

- Historical CBOT programs found (all expired by their stated terms; no renewal found):
  - Mini-sized grains, cftc_rul091009cbot001.txt (CBOT, 2009): "Mini-sized Corn, Wheat, and Soybean Futures Market
    Making Program on Globex" ... "Up to 3 market makers slots will be allowed in the Program." ... "Maximum Bid Ask
    Spread: 32 ticks" ... "Minimum Quote Size: 1 contract" ... "Start Date is November 1, 2007 End Date is December
    31, 2009" ... "Waive exchange transaction and clearing fees for designated market making accounts for mini-sized
    Corn, Wheat and Soybean futures contracts."
  - Overnight full-size, cftc_rul100909cbot001.txt: "a new CBOT market maker program for Corn, Wheat, and Soybean
    futures. The program will apply to firms that provide continuous quoting (subject to minimum contract size and
    Bid/Ask criteria) for CBOT Corn, Wheat, and Soybean futures during the nighttime trading session" ... "Minimum
    size: 5 contracts" ... "Minimum bid/ask: 1 cent or (4 ticks wide)" ... "Program will start November 1, 2009 and
    run through December 31 51 , 2010" (sic, pdftotext).
  - ETH fee incentive, cftc_rul093011cbot001.txt: "CBOT ETH Agricultural Trading Incentive Program" for "Corn,
    Wheat, Soybean, Soybean Meal, and Soybean Oil futures during the defined extended trading hours" ... "Start date
    is October 17, 2011. End date is December 31,2011."
  - Options programs (not futures): cftc_rul052809cbot001.txt, cftc_rul120811cbot001.txt ("CBOT Grain and Oilseed
    Options Market Maker Program on Globex"), cftc_rul121313cmeandcbot001.txt ("Agricultural Options Market Maker
    Program").
- Current fee schedule, cbot_fee_schedule_2026-10-01.txt ("CBOT Agricultural Product Fee Schedules as of October 1,
  2026"): its "Fee Waiver" table lists only "Hard Red Spring Wheat Futures (HRS) & Options (HSO)", "Spot-Quoted
  Futures - Dow Jones (QDF)" and "Rapeseed Oil Futures (RSO)". No fee waiver for ZC, ZS, ZW, ZL, ZM, the minis or the
  micros. The schedule lists general programs (e.g. "International Incentive Program (IIP)", "International Volume
  Incentive Program (IVIP)", "Latin American Fund Manager Incentive Program (FMIP)") that apply across products.
- No current (2019 or later) lead-market-maker or futures market-maker program for any grain futures candidate was
  found in two WebSearches (calls 5 and 6) and the fee schedule. The micro grain launch SER (cme_ser9512) lists
  exchange fees and the general IIP/IVIP/FMIP rows, no product-specific program. Absence in a search is not proof
  that none exists: CME market-maker programs are not always public.

### F8. Automated trading shares (CFTC OCE: Haynes and Roberts)

- cftc_haynes_roberts_2015.txt (Haynes and Roberts, "Automated Trading in Futures Markets", CFTC OCE, 2015;
  sample "CME transaction data, November 12, 2012 - October 31, 2014"):
  - Table 3: "Agriculture - Grain and Oilseed 16 5.6 (0.4) 39.0 (2.7) 55.4 (3.8)" (columns: products,
    Non-Electronic %, ATS %, Manual %).
  - Table 4 (ATS-ATS / ATS-MAN / MAN-MAN, % of volume): "Corn 128 15.9 42.8 34.8"; "Soybean 93 15.2 42.5 36.3";
    "Wheat 49 18.5 44.9 33.9" (total volume in millions first). Compare "Crude Oil 280 30.2 45.5 19.5".
  - Table 6 text: "for individual products like corn and soybeans, small traders contribute the majority share of
    volume; these contracts have a wide set of participants who, individually, execute small quantities, but are
    significant in aggregate." Rows: "Corn 76,290 18.7 36.0 868 18.6 20.2"; "Soybean 59,739 19.2 42.2 815 17.2
    15.4" (small traders N, ATS %, MAN %; large traders N, ATS %, MAN %).
  - Passive-fill speed: "over 90 percent of passive executed corn orders remained in the book longer than one
    second, as are 85 percent of natural gas futures." Table 7 (liquidity providers, % of two-sided volume by time
    from order placement to execution, ATS/MAN): "Corn 1.6 0.6 1.0 0.5 0.7 0.4 4.2 3.0 4.5 4.7 30.0" (0-100 ms,
    100-500 ms, 500 ms-1 s, 1-10 s, 10 s-1 min, then remaining electronic volume).
  - Table 8 (non-directional share of large-trader volume, ATS/MAN, full day / 1 / 3 / 5 min): "Corn 42.1 33.6
    19.8 6.2 25.2 9.3 27.9 11.2"; "Soybean 48.8 28.1 25.4 4.8 32.2 7.3 35.2 8.9"; compare "E-mini S&P 500 86.7 8.1
    57.7 3.7 ...".
- cftc_haynes_roberts_2017_update.txt (update, second sample "November 1, 2014 - October 31, 2016"; first number
  is the 2012-14 sample, second the 2014-16 sample):
  - Table 2: "Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7) 49.0 (3.9) 55.4 (3.8) 46.9
    (3.8)" (ATS share rose from 39.0% to 49.0%).
  - Table 3: "Corn 128 168 15.9 23.1 42.8 45.1 34.8 27.1"; "Soybean 93 115 15.2 25.1 42.5 45.6 36.3 24.1";
    "Wheat 49 62 18.5 29.3 44.9 47.5 33.9 21.6" (ATS-ATS rose; MAN-MAN fell to 21-27%).
  - Table 5: "Corn 76,290 72,535 18.7 20.8 36.0 27.8 868 731 18.6 24.9 20.2 21.8"; "Soybean 59,739 61,960 19.2
    22.1 42.2 33.0 815 772 17.2 25.8 15.4 13.9".
  - Its appendix figures cover "(b) Wheat", "(c) Soybean Oil", "(d) Soybean Meal" (daily ATS/MAN volume shares,
    charts only; no numbers extractable from text).
- No per-contract ATS share for soybean oil, soybean meal, minis or micros was found in table form. No CFTC update
  after 2017 was retrieved.

### F9. Spread, depth and flow at the touch (published studies; no owned data)

| Product | Measure | Value | Window and session | Source file and quote |
|---|---|---|---|---|
| ZC | quoted spread | "slightly more than one tick, 0.314 cents/bushel" (tick 0.25 c) in the last 40 days before expiry month; "well below two ticks" | 2008-01-14..2010-01-29, day session (BBO data) | agecon_wang_garcia_irwin_confp04-12.txt (Wang, Garcia, Irwin 2012 NCCC-134; AJAE 2014 version) |
| ZC | quoted spread on USDA and index-roll days | "averaging very near to one 'tick' (0.25 cents)" | 2008-01-14..2011-10-31, Globex | agecon_285856.txt (Shang, Mallory, Garcia 2016) |
| ZC, ZW, ZS | spread | "0.27 cent (1.1 ticks) for grains" (all three pooled), vs "25.6 cents (1 tick) for E-mini S&P 500" | nearby, 2015-11-23..2016-03-31 | agecon_259344.txt (Arzandeh and Frank 2017) |
| ZC | depth at best, mean contracts | "Quant.1 buy ... 377.69", "Quant.1 sell ... 375.27" | same | agecon_259344.txt Table 2 (columns Live Cattle, Lean Hogs, Corn, Wheat, Soybeans, E-mini) |
| ZW | depth at best | "Quant.1 buy" 45.26, "Quant.1 sell" 43.92 | same | same table |
| ZS | depth at best | "Quant.1 buy" 62.45, "Quant.1 sell" 64.00 | same | same table |
| (ES, for scale) | depth at best | 160.35 / 159.31 | same | same table |
| ZC, ZW, ZS | mean contracts per trade | "Volume (contract)" 12.07 (corn), 4.72 (wheat), 5.32 (soybeans) | same | same table |
| ZC, ZS | trades per minute | "Trades per minute 39.405" (corn), 53.881 (soybeans) | 2015-12..2017-05, day session 8:30-13:20 CT, outright book | ideals_hu_2020_three_essays.txt Table 3.1 (Hu 2020 dissertation) |
| ZS | top depth (bid + ask at best, volume-weighted top-5 contracts) | 2019: day 103, night 43; 2020: day 109, night 48 contracts | H1 2019 and H1 2020, day 8:30-13:20 CT vs night 19:00-07:45 CT | ideals_2022_three_essays_ag_liquidity.txt Table 3.2.1 (Peng 2022 dissertation) |
| ZS | quoted spread by session | 2019: day 0.2795, night 0.3055 cents; 2020: day 0.2775, night 0.3068 | same | same table: "Bid-ask spread (cents per bushel) 0.2795 0.0063 0.2672 0.2945 0.3055 ..." |
| ZC | depth at best during large moves | "well below 500 contracts during large price movements in the most traded corn outright futures contracts during the period from January 2014 to May 2017" (citing He, Serra, Garcia 2018) | 2014-01..2017-05 | ideals_2022_three_essays_ag_liquidity.txt |
| ZC | passive fill speed | "over 90 percent of passive executed corn orders remained in the book longer than one second" | 2012-11..2014-10 | cftc_haynes_roberts_2015.txt |

- Session ratio (arithmetic on the Peng table, ZS only): night/day spread = 0.3055/0.2795 = 1.09 (2019) and
  0.3068/0.2775 = 1.11 (2020); night/day depth = 43/103 = 0.42. No session split was found for ZC, ZW, ZL, ZM.
- Note on units: Arzandeh and Frank's depth is per side at the best price; Peng's "top depth" is "the simple daily
  session averages of the sums of the bid and ask depths posted at the best bid and ask quotes", i.e. both sides
  added. The two are not directly comparable.
- QV inputs (median displayed size / median contracts per minute): no source gives a median of either. Arithmetic on
  means from two different samples, for orientation only: ZC 39.4 trades/min x 12.07 contracts/trade = about 476
  contracts/min (2015-17 x 2015-16) against about 376 contracts per side at the best (2015-16): queue/flow about
  0.8 minutes. ZS 53.9 x 5.32 = about 287 contracts/min against about 63 per side: about 0.2 minutes. These are
  means from different windows, not medians, and are older than the standard window. [Worker arithmetic.]
- ZL, ZM: no published spread, depth or flow figure was found. de Boer et al. (2022) study the soybean complex LOB
  (abstract only, see F10). Micro and mini grains: nothing found.

### F10. Published microstructure research (C6 evidence)

Relation codes: same = same product; size = its micro/mini/full version; cousin = close cousin on CME Globex
(another CBOT grain or oilseed); class = asset class only. Result: positive = evidence of findable short-horizon
patterns or profitable passive provision; null; negative = evidence of absence or that passive provision does not
pay.

| Study | Products | Data | Finding (verbatim) | Result | Full text? |
|---|---|---|---|---|---|
| Hu (2020) dissertation ch. 3 = Hu, Serra, Garcia (2020) Applied Economics, "Algorithmic quoting, trading, and market quality in agricultural commodity futures markets" | ZC, ZS (and live cattle) | CME MDP 3.0 LOB, 2015-12..2017-05, day session | Table 3.1 means: corn "Volume-weighted effective spread, bps 3.502", "Volume-weighted realized Spread (5 s), bps 0.374", "Volume-weighted adverse selection cost (5 s), bps 3.128"; soybeans 1.504 / 0.081 / 1.423. Text: "realized spreads which represent returns to liquidity supplier are negative on average in the live cattle market"; abstract: "liquidity provider revenues increase with heightened AQ activity in the corn futures market". Effective spread is the half-spread: "0.128 cent/bushel (3.5 basis points x 336 cents/bushel) for corn ... close to half of their tick size (0.125 cents)". | Passive provision: small positive gross realized spread at 5-10 s, almost all of the half-spread lost to adverse selection (corn 89%, soybeans 95%: worker arithmetic 3.128/3.502 and 1.423/1.504). Gross realized spread in money: corn 0.374 bps x 336 c = 0.0126 c/bu = about $0.63 per 5,000-bu contract per fill; soybeans 0.081 bps x 983 c = about $0.40 (worker arithmetic), before exchange and clearing fees; the study does not net fees. Result code: positive gross realized spread, with net-of-cost profitability not tested (the scorer weighs it against fees). | yes (ideals_hu_2020_three_essays.txt) |
| Volkenand, Filler, Odening (2018) Agricultural Finance Review, "The impact of order imbalance on returns, liquidity, and volatility in agricultural commodity markets" | corn, wheat, soy (and cattle, hogs), CME BBO | March 2008 and March 2016 | Abstract: "Results confirm the positive relation between order imbalance and returns" ... "For some contracts, returns can be predicted using lagged order imbalance. This offers the opportunity to derive profitable trading strategies." | positive (order-flow imbalance, short horizon), same products | abstract only [unverified]: openalex_10_1108_afr_10_2017_0099.json |
| Arzandeh and Frank (2017/2019 AJAE), "Price Discovery in Agricultural Futures Markets: Should We Look Beyond the Best Bid-Ask Spread?" | ZC, ZW, ZS (and cattle, hogs, ES) | full LOB, 2015-11-23..2016-03-31 | "the steps of the LOB beyond the BAS contribute by over 27% to price discovery"; "MIS indicates a 40.10% share for the steps beyond the BAS for wheat, 40.66% for soybeans, and 42.49% for corn"; "informed traders in futures electronic markets actively use limit orders with price steps beyond the BAS" | positive for book information content (price discovery, not a tested trading rule) | yes (agecon_259344.txt) |
| Shang, Mallory, Garcia (2016 NCCC-134; Agricultural Economics 2018), "The Components of the Bid-Ask Spread: Evidence from the Corn Futures Market" | ZC | BBO, 2008-01-14..2011-10-31 | "The mean across days is 12.1%, and 70% of trading days resulted in an adverse selection component that was statistically significant" ... "On USDA announcement days, the daily mean of the adverse selection component, alpha, is 15.028%" | adverse selection is a minority of the spread on average, larger on report days (Huang-Stoll decomposition; not a trading test). Mixed for C6. | yes (agecon_285856.txt) |
| He, Serra, Garcia (2018 NCCC-134), "Cost of Immediacy during Large Price Movements: Evidence from Corn Futures Market" | ZC | top of book, 2014..2017 | "a resilient spread which is expected to narrow substantially within 5 - 20 seconds and completely revert back to normal state within 15 - 40 seconds once being shocked to widen" | spread resilience (fast replenishment by liquidity providers); not a predictability test | yes (agecon_285890.txt) |
| He, Serra, Garcia (2020 AJAE), "Resilience in 'Flash Events' in the Corn and Lean Hog Futures Markets" | ZC | 2014..2019 | abstract: "Liquidity dynamics during these events supports the view that active market making helps absorb the increased volume and stabilize markets." | evidence of active professional market making in ZC | abstract only [unverified] (openalex_10_1111_ajae_12146.json; Wiley PDF 403) |
| Couleau, Serra, Garcia (2020 AJAE), "Are Corn Futures Prices Getting 'Jumpy'?" | ZC | nearby transactions, 2008..2015 | "We find 495 days with at least one jump, which represents 25.3% of the total trading days"; "jumps occur 100% of the time in period 3 [since January 2013] and 83% of those days have a jump cluster within 2 minutes after the announcement time" ... "an average of 2.30 jumps per announcement day"; non-announcement days "0.26 in period 3" | jump frequency fact (C4); intraday jumps concentrate on USDA report days | yes (agecon_285883.txt) |
| Joseph and Garcia (2017 Applied Economics), "Intraday Market Effects in Electronic Soybean Futures Market during Non-Trading and Trading Hour Announcements" | ZS | intraday | "releases during trading hours result in a smaller volatility spike which extends for five to six minutes at a higher magnitude" ... "Return correlations provide little evidence to support systematic under- or overreaction in prices" | null for post-announcement return predictability | yes (agecon_235772.txt) |
| Lehecka, Wang, Garcia (2014 AEPP), "Gone in Ten Minutes" | ZC | 2009-07..2012-05 | abstract: "market reactions persist for approximately ten minutes ... little evidence exists to support systematic under- or overreactions in prices" | null for announcement drift | abstract only [unverified] (openalex_10_1093_aepp_ppu010.json) |
| Adjemian and Irwin (2018 AJAE), "USDA Announcement Effects in Real-Time" | grain futures | 2009..2014 | abstract: "heightened volatility dissipates within the space of a few trading minutes" | null (fast absorption) | abstract only [unverified] (openalex_10_1093_ajae_aay018.json) |
| de Boer, Gardebroek, Pennings, Trujillo-Barrera (2022 JFM), "Intraday liquidity in soybean complex futures markets" | ZS, ZL, ZM | LOB, 30 s to 1 day | abstract: "Liquidity persistence and positive liquidity spillovers mainly occur within 30 s" ... "traders who wish to capitalize on the short-term deviation of price relationships" | liquidity (not return) predictability across ZS/ZL/ZM; the only ZL/ZM-specific LOB study found | abstract only [unverified] (wur_soy_complex_liquidity.html.txt) |
| "Microstructure and high-frequency price discovery in the soybean complex" (2023, J. Commodity Markets) | ZS, ZL, ZM | high frequency | abstract: "the presence of cointegration among assets is related to the time of day and the contract maturities traded at a given time" | cross-asset (crush) price relations at high frequency | abstract only [unverified] (openalex_10_1016_j_jcomm_2023_100314.json) |
| Haynes and Roberts (2015, 2017 CFTC) | ZC, ZS, ZW | CME transactions 2012-2016 | see F8 | participant mix, not predictability | yes |

- Searches that returned nothing specific: queue-imbalance or trade-sign predictability studies on CBOT grains
  (OpenAlex queries "order imbalance agricultural futures intraday", "limit order book soybean futures",
  "intraday return predictability grain futures", "market making corn futures liquidity provider revenue"; files
  work/A1_grains/A1_grains_oa_{1,2,3}.txt). No study on mini or micro grains was found.
- No paper found showing that order-book patterns in grains are absent or arbitraged away; the closest negative
  evidence is the Hu (2020) adverse-selection share (passive provision earns about 0.1 of the half-spread at 5 s).

## S. Per-candidate fact sheets

Generated by work/A1_grains/A1_grains_build.py from the same records as A1_grains.json. Paths are under reports/stage_e28_briefs/pages/A1_grains/ unless stated. Empty value = unknown (the note says what was searched). Fields marked "see Fx" are family-wide.

### ZC: Corn Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Corn Futures |  | cbot_rulebook_ch10_2019.txt | "Chapter 10 Corn Futures" |
| product_code | ZC |  | cme_ser9151_price_limit_amend.txt | "Corn Futures ZC C 10" |
| tick_size | 0.25 (US cents per bushel) |  | cbot_rulebook_ch10_2019.txt | "The minimum fluctuation for Corn futures shall be ¼ cent per bushel ($12.50 per contract)," |
| tick_value | 12.5 (USD per contract) |  | cbot_rulebook_ch10_2019.txt | "The minimum fluctuation for Corn futures shall be ¼ cent per bushel ($12.50 per contract)," |
| contract_size | 5000 (bushels) |  | cbot_rulebook_ch10_2019.txt | "The unit of trading shall be 5,000 bushels of corn." |
| settlement | physical delivery |  | cbot_rulebook_ch10_2019.txt | "The procedures for trading, clearing, inspection, delivery and settlement of Corn futures" |
| launch_date | before 2023-11 (exact date not sourced; long-listed CBOT contract) |  | cme_web_adv_report_2023-09.txt | "CORN 320,584 305,121.35 5.1% 345,825 -7.3% 361,462 340,068 6.3%" Listed in CME ADV report (Aug 2023) and in every weekly CFTC COT report 2022-11..2023-10 and 2025-10..2026-10. |
| globex_60_dates_in_2023-11..2024-02 | True | 2023-11-01..2024-02-29 | cme_web_adv_report_2026-10.txt | "CORN 461,528 284,493.81 62.2% 602,349.38 -23.4% 500,733 455,813 9.9%" Inferred from continuous listing and trading before and after the window (2023 and 2026 ADV rows; weekly COT). No market data for the window was read. |
| match_algorithm | Configurable (CME algorithm K): TOP order first, then split 40% FIFO / 60% pro rata (with leveling), then FIFO residual | K for ZC/ZS/ZW outrights: Databento 2025-08; 40/60 split: Peng (2022) for the 2018 sample | databento_cme_matching_algos.html.txt; ideals_2022_three_essays_ag_liquidity.txt | "Databento: "Configurable ... Popular CME products: ZT, ZQ, ZC, ZS, ZW outrights". Peng: "Throughout our sample period, the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets. ... allocated on a "40 percent FIFO and 60 percent Pro-Rata" basis."" Primary per-product parameters (GCC Product Reference Sheet) not retrieved; current split unverified against CME. |
| trading_hours | see F1 | | | |
| price_limits | initial = 7% of 45-day average settlement (nearest 5c, floor 20c/bu in 2019 text), expanded +50%; reset May and November; since 2023-05-16 one contract settling at limit triggers expansion, and two consecutive days at expanded raise both levels (cents per bushel) | rule text 2019; amendment 2023 | cbot_rulebook_ch10_2019.txt; cme_ser9151_price_limit_amend.txt | ""Daily price limits for Corn futures are reset every six months." ... "multiplied by seven percent. The resulting number, rounded to the nearest 5 cents per bushel, or 20 cents per bushel, whichever is higher, will be the new initial price limit" ; SER 9151: "if current initial price limits in Corn Futures are $0.70 per bushel and expanded price limits are $1.05 per bushel"" |
| limit_hit_days_2019_2024 |  | 2019-2024 | cftc_ptc030422_wheat_limits.txt | "Previous Exchange analysis showed that a 7 percent price move traditionally captures 99 percent of all daily price movements, making limit days rare." No count of limit-settle days 2019-2024 was found (WebSearch calls 8 and 9; CBOT filings 2022-2023). A0 owned bars can count them. |
| adv_published_latest | 500733 (contracts/day, all expiries, all venues) | YTD Jan-Sep 2026 (also Sep 2026 month) | cme_web_adv_report_2026-10.txt | "CORN 461,528 284,493.81 62.2% 602,349.38 -23.4% 500,733 455,813 9.9%" CME Exchange ADV Report; not a trailing 12 months; Globex not split out. |
| adv_2022_11_2023_10 | 361462 (contracts/day, all expiries, all venues) | YTD Jan-Aug 2023 (partial window) | cme_web_adv_report_2023-09.txt | "CORN 320,584 305,121.35 5.1% 345,825 -7.3% 361,462 340,068 6.3%" Owned-bar ADV for the full window belongs to A0. |
| open_interest | {"2022-11..2023-10_mean": 1300458, "latest_52wk_mean": 1732054} (contracts (futures-only OI)) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "002602 / CORN - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=1300458 / ProdMerc=0.384 Swap=0.108 MM=0.254 OtherRept=0.140 NonRept=0.114 // 002602 / CORN - CHICAGO BOARD OF TRADE / latest_52wk ... meanOI=1732054 / ProdMerc=0.349 ... NonRept=0.092" CFTC Disaggregated COT, CORN - CHICAGO BOARD OF TRADE (002602); computed from cftc_fut_disagg_txt_*.zip |
| retail_share |  |  | cftc_haynes_roberts_2015.txt | "for individual products like corn and soybeans, small traders contribute the majority share of volume" Not a retail share: "small" = accounts under 0.5% of daily volume (Haynes-Roberts 2015, 2012-14). Table 6: small traders ATS 18.7% + MAN 36.0% of corn volume. |
| commercial_hedger_share | {"2022-11..2023-10": 0.384, "latest_52wk": 0.349} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "002602 / CORN - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=1300458 / ProdMerc=0.384 Swap=0.108 MM=0.254 OtherRept=0.140 NonRept=0.114" Producer/Merchant/Processor/User share = mean (long+short)/(2 OI). Position share, not volume share. |
| nonreportable_share | {"2022-11..2023-10": 0.114, "latest_52wk": 0.092} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "002602 / CORN - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=1300458 / ProdMerc=0.384 Swap=0.108 MM=0.254 OtherRept=0.140 NonRept=0.114" small-trader proxy |
| market_maker_program | none current found; historical CBOT overnight Corn/Wheat/Soybean futures market-maker program 2009-11-01..2010-12-31 and ETH fee incentive 2011-10-17..2011-12-31 | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt; cftc_rul100909cbot001.txt; cftc_rul093011cbot001.txt | "Fee Waiver table lists only "Hard Red Spring Wheat Futures (HRS) & Options (HSO)", "Spot-Quoted Futures - Dow Jones (QDF)", "Rapeseed Oil Futures (RSO)"" Two WebSearches (calls 5, 6). CME market-maker programs are not always public; absence in search is not proof of none. The 2009 overnight program covered Corn, Wheat and Soybean only. |
| hft_automated_share | {"ATS-ATS": [15.9, 23.1], "ATS-MAN": [42.8, 45.1], "MAN-MAN": [34.8, 27.1]} (% of volume) | 2012-11..2014-10 and 2014-11..2016-10 | cftc_haynes_roberts_2017_update.txt | "Corn 128 168 15.9 23.1 42.8 45.1 34.8 27.1" Group ATS share: Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7) 49.0 (3.9) 55.4 (3.8) 46.9 (3.8). Passive: "over 90 percent of passive executed corn orders remained in the book longer than one second" (2015 report). |
| median_spread_ticks_main | 1.26 (ticks (mean 0.314 c/bu; tick 0.25 c)) | 2008-01-14..2010-01-29, last 40 days before expiry month, day session | agecon_wang_garcia_irwin_confp04-12.txt | "During the last forty trading days prior to the expiration month, the average BAS is slightly more than one tick, 0.314 cents/bushel" Mean, not median; old window. Pooled grains 2015-16: "0.27 cent (1.1 ticks) for grains" (agecon_259344.txt). Shang et al.: "averaging very near to one 'tick' (0.25 cents)". |
| median_spread_ticks_overnight |  |  |  | No ZC session split found (ZS: night/day spread ratio 1.09-1.11, Peng 2022, see F9). |
| depth_best_level | {"bid": 377.69, "ask": 375.27} (contracts at best, mean per side) | nearby, 2015-11-23..2016-03-31 | agecon_259344.txt | "Quant.1 buy 5.91 6.33 377.69 45.26 62.45 160.35 / Quant.1 sell 5.56 6.48 375.27 43.92 64.00 159.31" Columns Live Cattle, Lean Hogs, Corn, Wheat, Soybeans, E-mini S&P 500. Mean, not median. During large moves 2014-17 "well below 500 contracts" (Peng 2022 citing He et al.). |
| touch_queue_size |  |  |  | No queue-size (orders at the touch) figure found; see depth. |
| volume_per_minute | {"trades_per_min": 39.405, "contracts_per_trade": 12.07, "implied_contracts_per_min": 476} (per minute) | trades: 2015-12..2017-05 day session; size: 2015-11..2016-03 | ideals_hu_2020_three_essays.txt; agecon_259344.txt | "Trades per minute 39.405 33.887 ... ; Volume (contract) ... 12.07" Implied contracts/min is worker arithmetic across two samples (means). Implied QV ~ 376/476 = 0.8 min (orientation only). |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency | {"days_with_jump_share": 0.253, "jumps_per_announcement_day_since_2013": 2.3, "jumps_per_non_announcement_day_since_2013": 0.26} | 2008-2015 nearby | agecon_285883.txt | "We find 495 days with at least one jump, which represents 25.3% of the total trading days" Intraday nonparametric jumps (Lee-Mykland), not the >4 sigma daily-return count of C4 (A0 owned). |
| microstructure_research | Hu (2020) ch.3 / Hu, Serra, Garcia (2020) Applied Economics [same]: gross realized spread at 5 s small positive; ~89-95% of half-spread is adverse selection; fees not netted; Volkenand, Filler, Odening (2018) AFR, order imbalance [same]: positive (lagged order imbalance predicts returns for some contracts) [abstract only]; Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes [same]: positive for LOB information share (40-42% for grains); not a trading test; Shang, Mallory, Garcia (2016/2018), spread components [same]: adverse selection 12.1% of spread on average, 15.0% on USDA days; mixed; He, Serra, Garcia (2018; AJAE 2020), spread resilience and flash events [same]: spread reverts within 15-40 s; active market making (professional liquidity provision); Couleau, Serra, Garcia (2020 AJAE), jumps [same]: jumps cluster on USDA report days (2.30 per announcement day since 2013); Lehecka, Wang, Garcia (2014 AEPP) [same]: null (reactions done in ~10 min) [abstract only]; Joseph and Garcia (2017), soybean announcements [cousin]: null (no systematic under/overreaction) |  | see A1_grains.md F10 |  |

### ZS: Soybean Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Soybean Futures |  | cbot_rulebook_ch11.txt | "Chapter 11 Soybean Futures" |
| product_code | ZS |  | cme_ser9151_price_limit_amend.txt | "Soybean Futures ZS S 11" |
| tick_size | 0.25 (US cents per bushel) |  | cbot_rulebook_ch11.txt | "The minimum fluctuation for soybean futures shall be ¼ cent per bushel ($12.50 per contract)," |
| tick_value | 12.5 (USD per contract) |  | cbot_rulebook_ch11.txt | "The minimum fluctuation for soybean futures shall be ¼ cent per bushel ($12.50 per contract)," |
| contract_size | 5000 (bushels) |  | cbot_rulebook_ch11.txt | "The unit of trading shall be 5,000 bushels of soybeans." |
| settlement | physical delivery |  | cbot_rulebook_ch11.txt | "The procedures for trading, clearing, inspection, delivery and settlement of soybean futures" |
| launch_date | before 2023-11 (exact date not sourced; long-listed CBOT contract) |  | cme_web_adv_report_2023-09.txt | "SOYBEAN 189,515 155,104.91 22.2% 226,716.9 -16.4% 243,723 202,811 20.2%" Listed in CME ADV report (Aug 2023) and in every weekly CFTC COT report 2022-11..2023-10 and 2025-10..2026-10. |
| globex_60_dates_in_2023-11..2024-02 | True | 2023-11-01..2024-02-29 | cme_web_adv_report_2026-10.txt | "SOYBEAN 289,853 215,397.62 34.6% 266,856.24 8.6% 301,529 285,015 5.8%" Inferred from continuous listing and trading before and after the window (2023 and 2026 ADV rows; weekly COT). No market data for the window was read. |
| match_algorithm | Configurable (CME algorithm K): TOP order first, then split 40% FIFO / 60% pro rata (with leveling), then FIFO residual | K for ZC/ZS/ZW outrights: Databento 2025-08; 40/60 split: Peng (2022) for the 2018 sample | databento_cme_matching_algos.html.txt; ideals_2022_three_essays_ag_liquidity.txt | "Databento: "Configurable ... Popular CME products: ZT, ZQ, ZC, ZS, ZW outrights". Peng: "Throughout our sample period, the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets. ... allocated on a "40 percent FIFO and 60 percent Pro-Rata" basis."" Primary per-product parameters (GCC Product Reference Sheet) not retrieved; current split unverified against CME. |
| trading_hours | see F1 | | | |
| price_limits | initial = 7% of 45-day average settlement (nearest 5c, floor 50c/bu), expanded = 1.5x; reset May and November; 2023 amendment as for corn (cents per bushel) | PDF 2024-12-31; SER 9151 (2023) | cbot_rulebook_ch11.txt; cme_ser9151_price_limit_amend.txt | ""Initial and expanded daily price limits for Soybean futures are reset every six months." ... "rounded to the nearest 5 cents per bushel, or 50 cents per bushel, whichever is higher, will be the new initial"" |
| limit_hit_days_2019_2024 |  | 2019-2024 | cftc_ptc030422_wheat_limits.txt | "Previous Exchange analysis showed that a 7 percent price move traditionally captures 99 percent of all daily price movements, making limit days rare." No count of limit-settle days 2019-2024 was found (WebSearch calls 8 and 9; CBOT filings 2022-2023). A0 owned bars can count them. |
| adv_published_latest | 301529 (contracts/day, all expiries, all venues) | YTD Jan-Sep 2026 (also Sep 2026 month) | cme_web_adv_report_2026-10.txt | "SOYBEAN 289,853 215,397.62 34.6% 266,856.24 8.6% 301,529 285,015 5.8%" CME Exchange ADV Report; not a trailing 12 months; Globex not split out. |
| adv_2022_11_2023_10 | 243723 (contracts/day, all expiries, all venues) | YTD Jan-Aug 2023 (partial window) | cme_web_adv_report_2023-09.txt | "SOYBEAN 189,515 155,104.91 22.2% 226,716.9 -16.4% 243,723 202,811 20.2%" Owned-bar ADV for the full window belongs to A0. |
| open_interest | {"2022-11..2023-10_mean": 676863, "latest_52wk_mean": 969705} (contracts (futures-only OI)) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "005602 / SOYBEANS - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=676863 / ProdMerc=0.438 Swap=0.118 MM=0.222 OtherRept=0.133 NonRept=0.089 // 005602 / SOYBEANS ... latest_52wk ... meanOI=969705 / ProdMerc=0.427 ... NonRept=0.066" CFTC Disaggregated COT, SOYBEANS - CHICAGO BOARD OF TRADE (005602); computed from cftc_fut_disagg_txt_*.zip |
| retail_share |  |  | cftc_haynes_roberts_2015.txt | "for individual products like corn and soybeans, small traders contribute the majority share of volume" Not a retail share (small = under 0.5% of daily volume). Table 6: small traders ATS 19.2% + MAN 42.2% of soybean volume (2012-14). |
| commercial_hedger_share | {"2022-11..2023-10": 0.438, "latest_52wk": 0.427} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "005602 / SOYBEANS - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=676863 / ProdMerc=0.438 Swap=0.118 MM=0.222 OtherRept=0.133 NonRept=0.089" Producer/Merchant/Processor/User share = mean (long+short)/(2 OI). Position share, not volume share. |
| nonreportable_share | {"2022-11..2023-10": 0.089, "latest_52wk": 0.066} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "005602 / SOYBEANS - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=676863 / ProdMerc=0.438 Swap=0.118 MM=0.222 OtherRept=0.133 NonRept=0.089" small-trader proxy |
| market_maker_program | none current found; historical CBOT overnight Corn/Wheat/Soybean futures market-maker program 2009-11-01..2010-12-31 and ETH fee incentive 2011-10-17..2011-12-31 | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt; cftc_rul100909cbot001.txt; cftc_rul093011cbot001.txt | "Fee Waiver table lists only "Hard Red Spring Wheat Futures (HRS) & Options (HSO)", "Spot-Quoted Futures - Dow Jones (QDF)", "Rapeseed Oil Futures (RSO)"" Two WebSearches (calls 5, 6). CME market-maker programs are not always public; absence in search is not proof of none. The 2009 overnight program covered Corn, Wheat and Soybean only. |
| hft_automated_share | {"ATS-ATS": [15.2, 25.1], "ATS-MAN": [42.5, 45.6], "MAN-MAN": [36.3, 24.1]} (% of volume) | 2012-11..2014-10 and 2014-11..2016-10 | cftc_haynes_roberts_2017_update.txt | "Soybean 93 115 15.2 25.1 42.5 45.6 36.3 24.1" Group ATS share: Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7) 49.0 (3.9) 55.4 (3.8) 46.9 (3.8) |
| median_spread_ticks_main | 1.118 (ticks (mean 0.2795 c/bu)) | H1 2019, day session 08:30-13:20 CT, top-5 contracts volume-weighted | ideals_2022_three_essays_ag_liquidity.txt | "Bid-ask spread (cents per bushel) 0.2795 0.0063 0.2672 0.2945 0.3055 0.0115 0.2761 0.3402" Mean of daily volume-weighted spreads; H1 2020: 0.2775 day. Pooled grains 2015-16: 1.1 ticks. |
| median_spread_ticks_overnight | 1.222 (ticks (mean 0.3055 c/bu)) | H1 2019, night session 19:00-07:45 CT | ideals_2022_three_essays_ag_liquidity.txt | "Bid-ask spread (cents per bushel) 0.2795 0.0063 0.2672 0.2945 0.3055 0.0115 0.2761 0.3402" Night/day ratio 1.09 (2019), 1.11 (2020: 0.3068/0.2775). Worker arithmetic. |
| depth_best_level | {"bid_mean_2015_16": 62.45, "ask_mean_2015_16": 64.0, "top_depth_bid_plus_ask_day_2019": 103, "top_depth_bid_plus_ask_night_2019": 43} (contracts) | 2015-11..2016-03 (per side); H1 2019 and H1 2020 (both sides summed) | agecon_259344.txt; ideals_2022_three_essays_ag_liquidity.txt | "Quant.1 buy ... 62.45 / Quant.1 sell ... 64.00 ; Top depth (number of contract) 103 32 45 212 43 10 24 83" H1 2020: day 109, night 48. COVID: "Soybean depth drops by half for outright futures" (Feb-Apr 2020). |
| touch_queue_size |  |  |  | No queue-size (orders at the touch) figure found; see depth. |
| volume_per_minute | {"trades_per_min": 53.881, "contracts_per_trade": 5.32, "implied_contracts_per_min": 287} (per minute) | trades: 2015-12..2017-05 day session; size: 2015-11..2016-03 | ideals_hu_2020_three_essays.txt; agecon_259344.txt | "Trades per minute 39.405 33.887 53.881 46.992 ... ; Volume (contract) ... 5.32" Implied contracts/min is worker arithmetic across two samples. Implied QV ~ 63/287 = 0.2 min. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  | agecon_235772.txt | "releases during trading hours result in a smaller volatility spike which extends for five to six minutes at a higher magnitude" No ZS jump-frequency count found; ZC (cousin): 25.3% of days with an intraday jump 2008-15. |
| microstructure_research | Hu (2020) ch.3 / Hu, Serra, Garcia (2020) Applied Economics [same]: gross realized spread at 5 s small positive; ~89-95% of half-spread is adverse selection; fees not netted; Volkenand, Filler, Odening (2018) AFR, order imbalance [same]: positive (lagged order imbalance predicts returns for some contracts) [abstract only]; Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes [same]: positive for LOB information share (40-42% for grains); not a trading test; Joseph and Garcia (2017), soybean announcements [same]: null (no systematic under/overreaction); de Boer et al. (2022 JFM), soybean complex LOB liquidity [same]: liquidity spillovers within 30 s across ZS/ZL/ZM; not return predictability [abstract only]; Shang, Mallory, Garcia (2016/2018), spread components [cousin]: adverse selection 12.1% of spread on average, 15.0% on USDA days; mixed; Couleau, Serra, Garcia (2020 AJAE), jumps [cousin]: jumps cluster on USDA report days (2.30 per announcement day since 2013) |  | see A1_grains.md F10 |  |

### ZW: Wheat Futures (Chicago SRW)

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Wheat Futures (Chicago SRW) |  | cbot_rulebook_ch14.txt | "Chapter 14 Wheat Futures" |
| product_code | ZW |  | cftc_ptc071522_wheat_limit_rules.txt | "Wheat Futures ZW W 14" |
| tick_size | 0.25 (US cents per bushel) |  | cbot_rulebook_ch14.txt | "The minimum fluctuation for wheat futures shall be ¼ cent per bushel ($12.50 per contract)," |
| tick_value | 12.5 (USD per contract) |  | cbot_rulebook_ch14.txt | "The minimum fluctuation for wheat futures shall be ¼ cent per bushel ($12.50 per contract)," |
| contract_size | 5000 (bushels) |  | cbot_rulebook_ch14.txt | "The unit of trading shall be 5,000 bushels of Wheat." |
| settlement | physical delivery |  | cbot_rulebook_ch14.txt | "14107. REGISTRATION AND DELIVERY OF WHEAT CERTIFICATES AND DELIVERY" |
| launch_date | before 2023-11 (exact date not sourced; long-listed CBOT contract) |  | cme_web_adv_report_2023-09.txt | "CHI WHEAT 128,550 103,224.61 24.5% 139,457.85 -7.8% 128,465 110,180 16.6%" Listed in CME ADV report (Aug 2023) and in every weekly CFTC COT report 2022-11..2023-10 and 2025-10..2026-10. |
| globex_60_dates_in_2023-11..2024-02 | True | 2023-11-01..2024-02-29 | cme_web_adv_report_2026-10.txt | "CHI WHEAT 142,002 93,115.24 52.5% 217,204.05 -34.6% 176,115 138,609 27.1%" Inferred from continuous listing and trading before and after the window (2023 and 2026 ADV rows; weekly COT). No market data for the window was read. |
| match_algorithm | Configurable (CME algorithm K): TOP order first, then split 40% FIFO / 60% pro rata (with leveling), then FIFO residual | K for ZC/ZS/ZW outrights: Databento 2025-08; 40/60 split: Peng (2022) for the 2018 sample | databento_cme_matching_algos.html.txt; ideals_2022_three_essays_ag_liquidity.txt | "Databento: "Configurable ... Popular CME products: ZT, ZQ, ZC, ZS, ZW outrights". Peng: "Throughout our sample period, the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets. ... allocated on a "40 percent FIFO and 60 percent Pro-Rata" basis."" Primary per-product parameters (GCC Product Reference Sheet) not retrieved; current split unverified against CME. |
| trading_hours | see F1 | | | |
| price_limits | initial = higher of 7% rule (nearest 5c, floor 30c/bu) for SRW and KC HRW; expanded = 1.5x; 2022 amendment (one month at limit triggers; consecutive expanded days raise levels), effective 2022-08-29 (cents per bushel) | PDF 2023-02-13; CBOT submission 22-254 | cbot_rulebook_ch14.txt; cftc_ptc071522_wheat_limit_rules.txt | ""rounded to the nearest 5 cents per bushel, or 30 cents per bushel, whichever is higher, will be the preliminary new initial price limit" ; "Should one or more Wheat futures contract months within the first five listed non-spot contracts settle at limit"" |
| limit_hit_days_2019_2024 | >= 1 multi-day episode (2022) known; count unknown (days per year) | 2019-2024 | cftc_ptc071522_wheat_limit_rules.txt | "On March 4, 2022, the Exchange again requested expedited approval to increase price limits in the Contracts following multiple limit-move days due to significant volatility caused by the war in Ukraine." Number of limit days in 2022 and other years not sourced; A0 owned bars can count. |
| adv_published_latest | 176115 (contracts/day, all expiries, all venues) | YTD Jan-Sep 2026 (also Sep 2026 month) | cme_web_adv_report_2026-10.txt | "CHI WHEAT 142,002 93,115.24 52.5% 217,204.05 -34.6% 176,115 138,609 27.1%" CME Exchange ADV Report; not a trailing 12 months; Globex not split out. |
| adv_2022_11_2023_10 | 128465 (contracts/day, all expiries, all venues) | YTD Jan-Aug 2023 (partial window) | cme_web_adv_report_2023-09.txt | "CHI WHEAT 128,550 103,224.61 24.5% 139,457.85 -7.8% 128,465 110,180 16.6%" Owned-bar ADV for the full window belongs to A0. |
| open_interest | {"2022-11..2023-10_mean": 363360, "latest_52wk_mean": 471403} (contracts (futures-only OI)) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "001602 / WHEAT-SRW - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=363360 / ProdMerc=0.168 Swap=0.140 MM=0.448 OtherRept=0.145 NonRept=0.099 // 001602 / WHEAT-SRW ... latest_52wk ... meanOI=471403 / ProdMerc=0.174 Swap=0.148 MM=0.479 ... NonRept=0.071" CFTC Disaggregated COT, WHEAT-SRW - CHICAGO BOARD OF TRADE (001602); computed from cftc_fut_disagg_txt_*.zip |
| retail_share |  |  | cftc_haynes_roberts_2015.txt | No retail share found. Managed money is the largest COT category (0.448). |
| commercial_hedger_share | {"2022-11..2023-10": 0.168, "latest_52wk": 0.174} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "001602 / WHEAT-SRW - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=363360 / ProdMerc=0.168 Swap=0.140 MM=0.448 OtherRept=0.145 NonRept=0.099" Producer/Merchant/Processor/User share = mean (long+short)/(2 OI). Position share, not volume share. |
| nonreportable_share | {"2022-11..2023-10": 0.099, "latest_52wk": 0.071} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "001602 / WHEAT-SRW - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=363360 / ProdMerc=0.168 Swap=0.140 MM=0.448 OtherRept=0.145 NonRept=0.099" small-trader proxy |
| market_maker_program | none current found; historical CBOT overnight Corn/Wheat/Soybean futures market-maker program 2009-11-01..2010-12-31 and ETH fee incentive 2011-10-17..2011-12-31 | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt; cftc_rul100909cbot001.txt; cftc_rul093011cbot001.txt | "Fee Waiver table lists only "Hard Red Spring Wheat Futures (HRS) & Options (HSO)", "Spot-Quoted Futures - Dow Jones (QDF)", "Rapeseed Oil Futures (RSO)"" Two WebSearches (calls 5, 6). CME market-maker programs are not always public; absence in search is not proof of none. The 2009 overnight program covered Corn, Wheat and Soybean only. |
| hft_automated_share | {"ATS-ATS": [18.5, 29.3], "ATS-MAN": [44.9, 47.5], "MAN-MAN": [33.9, 21.6]} (% of volume) | 2012-11..2014-10 and 2014-11..2016-10 | cftc_haynes_roberts_2017_update.txt | "Wheat 49 62 18.5 29.3 44.9 47.5 33.9 21.6" Group ATS share: Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7) 49.0 (3.9) 55.4 (3.8) 46.9 (3.8) |
| median_spread_ticks_main | 1.1 (ticks (mean, grains pooled ZC/ZW/ZS)) | nearby, 2015-11-23..2016-03-31 | agecon_259344.txt | "0.27 cent (1.1 ticks) for grains" Mean, not median; all sessions pooled as far as stated. |
| median_spread_ticks_overnight |  |  |  | No ZW session split found. |
| depth_best_level | {"bid": 45.26, "ask": 43.92} (contracts at best, mean per side) | nearby, 2015-11-23..2016-03-31 | agecon_259344.txt | "Quant.1 buy 5.91 6.33 377.69 45.26 62.45 160.35 / Quant.1 sell 5.56 6.48 375.27 43.92 64.00 159.31" Mean, not median. |
| touch_queue_size |  |  |  | No queue-size (orders at the touch) figure found; see depth. |
| volume_per_minute | {"contracts_per_trade": 4.72} (contracts per trade) | nearby, 2015-11..2016-03 | agecon_259344.txt | "Volume (2.06) 2.19 12.07 4.72 5.32 10.13" No trades-per-minute figure for wheat found. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | No ZW jump study found; A0 owned bars. |
| microstructure_research | Volkenand, Filler, Odening (2018) AFR, order imbalance [same]: positive (lagged order imbalance predicts returns for some contracts) [abstract only]; Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes [same]: positive for LOB information share (40-42% for grains); not a trading test; Hu (2020) ch.3 / Hu, Serra, Garcia (2020) Applied Economics [cousin]: gross realized spread at 5 s small positive; ~89-95% of half-spread is adverse selection; fees not netted; Couleau, Serra, Garcia (2020 AJAE), jumps [cousin]: jumps cluster on USDA report days (2.30 per announcement day since 2013); He, Serra, Garcia (2018; AJAE 2020), spread resilience and flash events [cousin]: spread reverts within 15-40 s; active market making (professional liquidity provision) |  | see A1_grains.md F10 |  |

### ZL: Soybean Oil Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Soybean Oil Futures |  | cbot_rulebook_ch12.txt | "Chapter 12 Soybean Oil Futures" |
| product_code | ZL |  | cme_ser9151_price_limit_amend.txt | "Soybean Oil Futures ZL 07 12" |
| tick_size | 0.01 (US cents per pound) |  | cbot_rulebook_ch12.txt | "The minimum fluctuation for soybean oil futures shall be 1/100th of one cent per pound ($6.00 per contract), including spreads." |
| tick_value | 6.0 (USD per contract) |  | cbot_rulebook_ch12.txt | "The minimum fluctuation for soybean oil futures shall be 1/100th of one cent per pound ($6.00 per contract), including spreads." |
| contract_size | 60000 (pounds) |  | cbot_rulebook_ch12.txt | "The unit of trading shall be 60,000 lbs. of crude soybean oil." |
| settlement | physical delivery |  | cbot_rulebook_ch12.txt | "12107. REGISTRATION AND DELIVERY OF SOYBEAN OIL RECEIPTS AND DELIVERY" |
| launch_date | before 2023-11 (exact date not sourced; long-listed CBOT contract) |  | cme_web_adv_report_2023-09.txt | "SOYBEAN OIL 124,353 114,709.74 8.4% 153,846.15 -19.2% 147,995 112,117 32.0%" Listed in CME ADV report (Aug 2023) and in every weekly CFTC COT report 2022-11..2023-10 and 2025-10..2026-10. |
| globex_60_dates_in_2023-11..2024-02 | True | 2023-11-01..2024-02-29 | cme_web_adv_report_2026-10.txt | "SOYBEAN OIL 185,351 172,338.33 7.6% 218,667.19 -15.2% 227,516 183,650 23.9%" Inferred from continuous listing and trading before and after the window (2023 and 2026 ADV rows; weekly COT). No market data for the window was read. |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | initial = 7% of 45-day average (nearest 0.5c/lb, floor 2c/lb); expanded per rule; 2023 amendment as for corn (cents per pound) | PDF 2022-12-19; SER 9151 | cbot_rulebook_ch12.txt; cme_ser9151_price_limit_amend.txt | ""rounded to the nearest 0.5 cents per pound, or 2 cents per pound, whichever is higher, will be the new initial price limits"" |
| limit_hit_days_2019_2024 |  | 2019-2024 | cftc_ptc030422_wheat_limits.txt | "Previous Exchange analysis showed that a 7 percent price move traditionally captures 99 percent of all daily price movements, making limit days rare." No count of limit-settle days 2019-2024 was found (WebSearch calls 8 and 9; CBOT filings 2022-2023). A0 owned bars can count them. |
| adv_published_latest | 227516 (contracts/day, all expiries, all venues) | YTD Jan-Sep 2026 (also Sep 2026 month) | cme_web_adv_report_2026-10.txt | "SOYBEAN OIL 185,351 172,338.33 7.6% 218,667.19 -15.2% 227,516 183,650 23.9%" CME Exchange ADV Report; not a trailing 12 months; Globex not split out. |
| adv_2022_11_2023_10 | 147995 (contracts/day, all expiries, all venues) | YTD Jan-Aug 2023 (partial window) | cme_web_adv_report_2023-09.txt | "SOYBEAN OIL 124,353 114,709.74 8.4% 153,846.15 -19.2% 147,995 112,117 32.0%" Owned-bar ADV for the full window belongs to A0. |
| open_interest | {"2022-11..2023-10_mean": 459495, "latest_52wk_mean": 668533} (contracts (futures-only OI)) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "007601 / SOYBEAN OIL - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=459495 / ProdMerc=0.434 Swap=0.138 MM=0.244 OtherRept=0.121 NonRept=0.064 // 007601 / SOYBEAN OIL ... latest_52wk ... meanOI=668533 / ProdMerc=0.415 ... NonRept=0.047" CFTC Disaggregated COT, SOYBEAN OIL - CHICAGO BOARD OF TRADE (007601); computed from cftc_fut_disagg_txt_*.zip |
| retail_share |  |  | cftc_haynes_roberts_2015.txt | No retail share published for this product found. |
| commercial_hedger_share | {"2022-11..2023-10": 0.434, "latest_52wk": 0.415} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "007601 / SOYBEAN OIL - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=459495 / ProdMerc=0.434 Swap=0.138 MM=0.244 OtherRept=0.121 NonRept=0.064" Producer/Merchant/Processor/User share = mean (long+short)/(2 OI). Position share, not volume share. |
| nonreportable_share | {"2022-11..2023-10": 0.064, "latest_52wk": 0.047} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "007601 / SOYBEAN OIL - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=459495 / ProdMerc=0.434 Swap=0.138 MM=0.244 OtherRept=0.121 NonRept=0.064" small-trader proxy |
| market_maker_program | none current found | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt | "Fee Waiver table lists only "Hard Red Spring Wheat Futures (HRS) & Options (HSO)", "Spot-Quoted Futures - Dow Jones (QDF)", "Rapeseed Oil Futures (RSO)"" Historical futures market-maker programs found covered Corn, Wheat, Soybeans only (2007-2010); ETH fee incentive 2011 covered ZL and ZM too (cftc_rul093011cbot001.txt). Not proof that none exists. |
| hft_automated_share |  | 2012-2016 | cftc_haynes_roberts_2017_update.txt | "Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7) 49.0 (3.9) 55.4 (3.8) 46.9 (3.8)" No per-contract table for soybean oil; group "Grain and Oilseed" ATS 39.0% (2012-14) -> 49.0% (2014-16). Update appendix has a soybean oil chart only. |
| median_spread_ticks_main |  |  |  | No ZL spread figure found (OpenAlex queries in work/A1_grains/A1_grains_oa_*.txt). |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | No queue-size (orders at the touch) figure found; see depth. |
| volume_per_minute |  |  |  | Not found. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | No ZL jump study found; A0 owned bars. |
| microstructure_research | de Boer et al. (2022 JFM), soybean complex LOB liquidity [same]: liquidity spillovers within 30 s across ZS/ZL/ZM; not return predictability [abstract only]; Hu (2020) ch.3 / Hu, Serra, Garcia (2020) Applied Economics [cousin]: gross realized spread at 5 s small positive; ~89-95% of half-spread is adverse selection; fees not netted; Volkenand, Filler, Odening (2018) AFR, order imbalance [cousin]: positive (lagged order imbalance predicts returns for some contracts) [abstract only]; Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes [cousin]: positive for LOB information share (40-42% for grains); not a trading test |  | see A1_grains.md F10 | Also "Microstructure and high-frequency price discovery in the soybean complex" (JCM 2023, abstract only). |

### ZM: Soybean Meal Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Soybean Meal Futures |  | cbot_rulebook_ch13.txt | "Chapter 13 Soybean Meal Futures" |
| product_code | ZM |  | cme_ser9151_price_limit_amend.txt | "Soybean Meal Futures ZM 06 13" |
| tick_size | 0.1 (USD per short ton) |  | cbot_rulebook_ch13.txt | "The minimum fluctuation for Soybean Meal futures shall be ten cents ($.10) per ton ($10.00 per contract), including spreads." |
| tick_value | 10.0 (USD per contract) |  | cbot_rulebook_ch13.txt | "The minimum fluctuation for Soybean Meal futures shall be ten cents ($.10) per ton ($10.00 per contract), including spreads." |
| contract_size | 100 (short tons) |  | cbot_rulebook_ch13.txt | "The unit of trading for Soybean Meal shall be 100 tons (2,000 pounds per ton)." |
| settlement | physical delivery |  | cbot_rulebook_ch13.txt | "The procedures for trading, clearing, inspection, delivery and settlement not specifically covered herein" |
| launch_date | before 2023-11 (exact date not sourced; long-listed CBOT contract) |  | cme_web_adv_report_2023-09.txt | "SOYBEAN MEAL 137,490 106,543.78 29.0% 138,946.2 -1.0% 140,498 107,575 30.6%" Listed in CME ADV report (Aug 2023) and in every weekly CFTC COT report 2022-11..2023-10 and 2025-10..2026-10. |
| globex_60_dates_in_2023-11..2024-02 | True | 2023-11-01..2024-02-29 | cme_web_adv_report_2026-10.txt | "SOYBEAN MEAL 213,478 170,665.29 25.1% 166,698.48 28.1% 185,193 172,222 7.5%" Inferred from continuous listing and trading before and after the window (2023 and 2026 ADV rows; weekly COT). No market data for the window was read. |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | initial = 7% of 45-day average (nearest $5/ton, floor $20/ton); expanded = 1.5x; 2023 amendment (USD per short ton) | PDF 2025-12-16; SER 9151 | cbot_rulebook_ch13.txt; cme_ser9151_price_limit_amend.txt | ""rounded to the nearest 5 dollars per ton, or 20 dollars per ton, whichever is higher, will be the new initial price limits for Soybean Meal futures"" |
| limit_hit_days_2019_2024 |  | 2019-2024 | cftc_ptc030422_wheat_limits.txt | "Previous Exchange analysis showed that a 7 percent price move traditionally captures 99 percent of all daily price movements, making limit days rare." No count of limit-settle days 2019-2024 was found (WebSearch calls 8 and 9; CBOT filings 2022-2023). A0 owned bars can count them. |
| adv_published_latest | 185193 (contracts/day, all expiries, all venues) | YTD Jan-Sep 2026 (also Sep 2026 month) | cme_web_adv_report_2026-10.txt | "SOYBEAN MEAL 213,478 170,665.29 25.1% 166,698.48 28.1% 185,193 172,222 7.5%" CME Exchange ADV Report; not a trailing 12 months; Globex not split out. |
| adv_2022_11_2023_10 | 140498 (contracts/day, all expiries, all venues) | YTD Jan-Aug 2023 (partial window) | cme_web_adv_report_2023-09.txt | "SOYBEAN MEAL 137,490 106,543.78 29.0% 138,946.2 -1.0% 140,498 107,575 30.6%" Owned-bar ADV for the full window belongs to A0. |
| open_interest | {"2022-11..2023-10_mean": 449564, "latest_52wk_mean": 592664} (contracts (futures-only OI)) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "026603 / SOYBEAN MEAL - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=449564 / ProdMerc=0.419 Swap=0.111 MM=0.263 OtherRept=0.123 NonRept=0.084 // 026603 / SOYBEAN MEAL ... latest_52wk ... meanOI=592664 / ProdMerc=0.412 ... NonRept=0.065" CFTC Disaggregated COT, SOYBEAN MEAL - CHICAGO BOARD OF TRADE (026603); computed from cftc_fut_disagg_txt_*.zip |
| retail_share |  |  | cftc_haynes_roberts_2015.txt | No retail share published for this product found. |
| commercial_hedger_share | {"2022-11..2023-10": 0.419, "latest_52wk": 0.412} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "026603 / SOYBEAN MEAL - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=449564 / ProdMerc=0.419 Swap=0.111 MM=0.263 OtherRept=0.123 NonRept=0.084" Producer/Merchant/Processor/User share = mean (long+short)/(2 OI). Position share, not volume share. |
| nonreportable_share | {"2022-11..2023-10": 0.084, "latest_52wk": 0.065} (share of OI positions) | 2022-11-01..2023-10-31 (53 weekly reports); 2025-10-14..2026-10-13 (53 weekly reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "026603 / SOYBEAN MEAL - CHICAGO BOARD OF TRADE / 2022-11-01..2023-10-31 ... meanOI=449564 / ProdMerc=0.419 Swap=0.111 MM=0.263 OtherRept=0.123 NonRept=0.084" small-trader proxy |
| market_maker_program | none current found | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt | "Fee Waiver table lists only "Hard Red Spring Wheat Futures (HRS) & Options (HSO)", "Spot-Quoted Futures - Dow Jones (QDF)", "Rapeseed Oil Futures (RSO)"" Historical futures market-maker programs found covered Corn, Wheat, Soybeans only (2007-2010); ETH fee incentive 2011 covered ZL and ZM too (cftc_rul093011cbot001.txt). Not proof that none exists. |
| hft_automated_share |  | 2012-2016 | cftc_haynes_roberts_2017_update.txt | "Agriculture - Grain and Oilseed 16 13 5.6 (0.4) 4.1 (0.3) 39.0 (2.7) 49.0 (3.9) 55.4 (3.8) 46.9 (3.8)" No per-contract table for soybean meal; group-level only (update appendix chart only). |
| median_spread_ticks_main |  |  |  | No ZM spread figure found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | No queue-size (orders at the touch) figure found; see depth. |
| volume_per_minute |  |  |  | Not found. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | No ZM jump study found; A0 owned bars. |
| microstructure_research | de Boer et al. (2022 JFM), soybean complex LOB liquidity [same]: liquidity spillovers within 30 s across ZS/ZL/ZM; not return predictability [abstract only]; Hu (2020) ch.3 / Hu, Serra, Garcia (2020) Applied Economics [cousin]: gross realized spread at 5 s small positive; ~89-95% of half-spread is adverse selection; fees not netted; Volkenand, Filler, Odening (2018) AFR, order imbalance [cousin]: positive (lagged order imbalance predicts returns for some contracts) [abstract only]; Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes [cousin]: positive for LOB information share (40-42% for grains); not a trading test |  | see A1_grains.md F10 | Also JCM 2023 soybean-complex paper (abstract only). |

### XC: Mini-Sized Corn Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Mini-Sized Corn Futures |  | cbot_rulebook_ch10B_2017.txt | "Mini-Sized Corn Futures" |
| product_code | XC |  | cme_ser9151_price_limit_amend.txt | "Mini-Sized Corn Futures XC YC" Globex code; clearing code YC |
| tick_size | 0.125 (US cents per bushel) |  | cbot_rulebook_ch10B_2017.txt | "The minimum fluctuation for mini-sized Corn futures shall be 1/8 cent per bushel ($1.25 per" |
| tick_value | 1.25 (USD per contract) |  | cbot_rulebook_ch10B_2017.txt | "The minimum fluctuation for mini-sized Corn futures shall be 1/8 cent per bushel ($1.25 per" |
| contract_size | 1000 (bushels) |  | cbot_rulebook_ch10B_2017.txt | "The unit of trading shall be 1,000 bushels of corn." |
| settlement | physical delivery (delivery by mini-sized certificates) |  | cbot_rulebook_ch10B_2017.txt | "10B07. DELIVERIES BY MINI-SIZED ... CERTIFICATES AND DELIVERY" |
| launch_date | 2003-04-07 (open auction); electronic from 2007 (e-cbot); on Globex by 2007-11 |  | mondo_cbot_mini_ag_2003.html.txt; mondo_cbot_mini_ag_ecbot_2007.html.txt; cftc_rul091009cbot001.txt | ""will launch mini-sized Corn, Wheat, and Soybean futures on Monday, April 7, 2003" ; "This is the first time these contracts will be available on an electronic platform" ; "Mini-sized Corn, Wheat and Soybean futures contracts traded on the Globex platform" (program start November 1, 2007)" Mondo Visione reprints of CBOT releases. Exact e-cbot date (May 14, 2007) appears only in a CME URL slug from search [unverified]. |
| globex_60_dates_in_2023-11..2024-02 | True | 2023-11-01..2024-02-29 | cme_web_adv_report_2026-10.txt | "MINI CORN 1,318 1,048.71 25.6% 1,462.24 -9.9% 1,160 1,533 -24.3%" Inferred: listed throughout (rule amendments 2022-2023 name it; ADV rows 2023 and 2026). With ADV ~1,000-2,000/day trading on most days is likely but days-with-trades in the window were not verified (no market data read). |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | same as ZC |  | cbot_rulebook_ch10B_2017.txt | "Daily price limits for mini-sized Corn futures are the same as those for standard-sized Corn" SER 9151 / CBOT 22-254: limit levels set to the full-size values each business day. |
| limit_hit_days_2019_2024 |  | 2019-2024 | cftc_ptc030422_wheat_limits.txt | "Previous Exchange analysis showed that a 7 percent price move traditionally captures 99 percent of all daily price movements, making limit days rare." Same limits as ZC; see ZC. |
| adv_published_latest | 1160 (contracts/day) | YTD Jan-Sep 2026 | cme_web_adv_report_2026-10.txt | "MINI CORN 1,318 1,048.71 25.6% 1,462.24 -9.9% 1,160 1,533 -24.3%" |
| adv_2022_11_2023_10 | 1711 (contracts/day) | YTD Jan-Aug 2023 (partial window) | cme_web_adv_report_2023-09.txt | "MINI CORN 1,645 2,111.57 -22.1% 2,666.4 -38.3% 1,711 2,831 -39.6%" |
| open_interest |  |  |  | No CFTC COT market for this contract in the 2022-2026 files; CME OI not retrieved. |
| retail_share |  |  | mondo_cbot_mini_ag_ecbot_2007.html.txt | "offer global customers, particularly in Asia, a smaller contract that is sized to their needs" No retail share found; small-size design (1/5 of full size). |
| commercial_hedger_share |  |  |  | No COT market; parent ZC figures do not transfer. |
| nonreportable_share |  |  |  | No COT market. |
| market_maker_program | none current found; CBOT mini-sized grains MM program 2007-11-01..2009-12-31 (up to 3 market makers, max spread 32 ticks, min size 1, fee waivers) | checked 2026-10-21 | cftc_rul091009cbot001.txt; cbot_fee_schedule_2026-10-01.txt | "Start Date is November 1, 2007 End Date is December 31, 2009" Fee schedule 2026-10-01 waiver table names no mini grain. |
| hft_automated_share |  |  |  | Not tabulated by CFTC OCE for minis. |
| median_spread_ticks_main |  |  |  | Not found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | Not found. |
| volume_per_minute |  |  |  | Not found; ADV ~1,000-2,000/day over ~17 h of trading. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | Same underlying as ZC; see ZC. |
| microstructure_research | Hu (2020) ch.3 / Hu, Serra, Garcia (2020) Applied Economics [size]: gross realized spread at 5 s small positive; ~89-95% of half-spread is adverse selection; fees not netted; Volkenand, Filler, Odening (2018) AFR, order imbalance [size]: positive (lagged order imbalance predicts returns for some contracts) [abstract only]; Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes [size]: positive for LOB information share (40-42% for grains); not a trading test; Couleau, Serra, Garcia (2020 AJAE), jumps [size]: jumps cluster on USDA report days (2.30 per announcement day since 2013) |  | see A1_grains.md F10 | No study on the mini contract itself found. |

### XK: Mini-Sized Soybean Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Mini-Sized Soybean Futures |  | cbot_rulebook_ch11B.txt | "Mini-Sized Soybean Futures" |
| product_code | XK |  | cme_ser9151_price_limit_amend.txt | "Mini-Sized Soybean Futures XK YK" Globex code; clearing code YK |
| tick_size | 0.125 (US cents per bushel) |  | cbot_rulebook_ch11B.txt | "The minimum fluctuation for mini-sized soybean futures shall be 1/8 cent per bushel ($1.25 per" |
| tick_value | 1.25 (USD per contract) |  | cbot_rulebook_ch11B.txt | "The minimum fluctuation for mini-sized soybean futures shall be 1/8 cent per bushel ($1.25 per" |
| contract_size | 1000 (bushels) |  | cbot_rulebook_ch11B.txt | "The unit of trading shall be 1,000 bushels of soybeans." |
| settlement | physical delivery (delivery by mini-sized certificates) |  | cbot_rulebook_ch11B.txt | "11B07. DELIVERIES BY MINI-SIZED ... CERTIFICATES AND DELIVERY" |
| launch_date | 2003-04-07 (open auction); electronic from 2007 (e-cbot); on Globex by 2007-11 |  | mondo_cbot_mini_ag_2003.html.txt; mondo_cbot_mini_ag_ecbot_2007.html.txt; cftc_rul091009cbot001.txt | ""will launch mini-sized Corn, Wheat, and Soybean futures on Monday, April 7, 2003" ; "This is the first time these contracts will be available on an electronic platform" ; "Mini-sized Corn, Wheat and Soybean futures contracts traded on the Globex platform" (program start November 1, 2007)" Mondo Visione reprints of CBOT releases. Exact e-cbot date (May 14, 2007) appears only in a CME URL slug from search [unverified]. |
| globex_60_dates_in_2023-11..2024-02 | True | 2023-11-01..2024-02-29 | cme_web_adv_report_2026-10.txt | "MINI SOYBEAN 1,587 1,362.9 16.4% 1,659.43 -4.4% 1,980 1,952 1.4%" Inferred: listed throughout (rule amendments 2022-2023 name it; ADV rows 2023 and 2026). With ADV ~1,000-2,000/day trading on most days is likely but days-with-trades in the window were not verified (no market data read). |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | same as ZS |  | cbot_rulebook_ch11B.txt | "Daily price limits for mini-sized Soybean futures are the same as those for standard-sized" SER 9151 / CBOT 22-254: limit levels set to the full-size values each business day. |
| limit_hit_days_2019_2024 |  | 2019-2024 | cftc_ptc030422_wheat_limits.txt | "Previous Exchange analysis showed that a 7 percent price move traditionally captures 99 percent of all daily price movements, making limit days rare." Same limits as ZS; see ZS. |
| adv_published_latest | 1980 (contracts/day) | YTD Jan-Sep 2026 | cme_web_adv_report_2026-10.txt | "MINI SOYBEAN 1,587 1,362.9 16.4% 1,659.43 -4.4% 1,980 1,952 1.4%" |
| adv_2022_11_2023_10 | 2077 (contracts/day) | YTD Jan-Aug 2023 (partial window) | cme_web_adv_report_2023-09.txt | "MINI SOYBEAN 1,955 2,725.13 -28.3% 3,263.15 -40.1% 2,077 2,951 -29.6%" |
| open_interest | {"2022-11..2023-10_mean": 21858, "latest_mean": 27728} (contracts) | 2023-07-25..2023-09-26 (10 reports only); 2026-05-05..2026-10-13 (24 reports) | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "005603 / MINI SOYBEANS - CHICAGO BOARD OF TRADE / ... n=10 / meanOI=21858" CFTC publishes this market only in some weeks. |
| retail_share |  |  | mondo_cbot_mini_ag_ecbot_2007.html.txt | "offer global customers, particularly in Asia, a smaller contract that is sized to their needs" No retail share found; small-size design (1/5 of full size). |
| commercial_hedger_share | {"2023 weeks": 0.21, "2026 weeks": 0.184} (share of OI positions) | as above | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "ProdMerc=0.210 Swap=0.000 MM=0.000 OtherRept=0.376 NonRept=0.414" Thin sample. |
| nonreportable_share | {"2023 weeks": 0.414, "2026 weeks": 0.362} (share of OI positions) | as above | reports/stage_e28_briefs/work/A1_grains/A1_grains_cot_out.txt | "NonRept=0.414 ; NonRept=0.362" Thin sample. |
| market_maker_program | none current found; CBOT mini-sized grains MM program 2007-11-01..2009-12-31 (up to 3 market makers, max spread 32 ticks, min size 1, fee waivers) | checked 2026-10-21 | cftc_rul091009cbot001.txt; cbot_fee_schedule_2026-10-01.txt | "Start Date is November 1, 2007 End Date is December 31, 2009" Fee schedule 2026-10-01 waiver table names no mini grain. |
| hft_automated_share |  |  |  | Not tabulated by CFTC OCE for minis. |
| median_spread_ticks_main |  |  |  | Not found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | Not found. |
| volume_per_minute |  |  |  | Not found; ADV ~1,000-2,000/day over ~17 h of trading. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | Same underlying as ZS; see ZS. |
| microstructure_research | Hu (2020) ch.3 / Hu, Serra, Garcia (2020) Applied Economics [size]: gross realized spread at 5 s small positive; ~89-95% of half-spread is adverse selection; fees not netted; Volkenand, Filler, Odening (2018) AFR, order imbalance [size]: positive (lagged order imbalance predicts returns for some contracts) [abstract only]; Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes [size]: positive for LOB information share (40-42% for grains); not a trading test; Joseph and Garcia (2017), soybean announcements [size]: null (no systematic under/overreaction) |  | see A1_grains.md F10 | No study on the mini contract itself found. |

### XW: Mini-Sized Wheat Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Mini-Sized Wheat Futures |  | cbot_rulebook_ch14B.txt | "Mini-Sized Wheat Futures" |
| product_code | XW |  | cftc_ptc071522_wheat_limit_rules.txt | "Mini-Sized Wheat Futures XW YW" Globex code; clearing code YW |
| tick_size | 0.125 (US cents per bushel) |  | cbot_rulebook_ch14B.txt | "The minimum fluctuation for mini-sized wheat futures shall be 1/8 cent per bushel ($1.25 per" |
| tick_value | 1.25 (USD per contract) |  | cbot_rulebook_ch14B.txt | "The minimum fluctuation for mini-sized wheat futures shall be 1/8 cent per bushel ($1.25 per" |
| contract_size | 1000 (bushels) |  | cbot_rulebook_ch14B.txt | "The unit of trading shall be 1,000 bushels of wheat." |
| settlement | physical delivery (delivery by mini-sized certificates) |  | cbot_rulebook_ch14B.txt | "14B07. DELIVERIES BY MINI-SIZED ... CERTIFICATES AND DELIVERY" |
| launch_date | 2003-04-07 (open auction); electronic from 2007 (e-cbot); on Globex by 2007-11 |  | mondo_cbot_mini_ag_2003.html.txt; mondo_cbot_mini_ag_ecbot_2007.html.txt; cftc_rul091009cbot001.txt | ""will launch mini-sized Corn, Wheat, and Soybean futures on Monday, April 7, 2003" ; "This is the first time these contracts will be available on an electronic platform" ; "Mini-sized Corn, Wheat and Soybean futures contracts traded on the Globex platform" (program start November 1, 2007)" Mondo Visione reprints of CBOT releases. Exact e-cbot date (May 14, 2007) appears only in a CME URL slug from search [unverified]. |
| globex_60_dates_in_2023-11..2024-02 | True | 2023-11-01..2024-02-29 | cme_web_adv_report_2026-10.txt | "MINI WHEAT 970 524.14 85.0% 1,122.86 -13.6% 922 958 -3.7%" Inferred: listed throughout (rule amendments 2022-2023 name it; ADV rows 2023 and 2026). With ADV ~1,000-2,000/day trading on most days is likely but days-with-trades in the window were not verified (no market data read). |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | same as ZW |  | cbot_rulebook_ch14B.txt | "Daily price limits for mini-sized Wheat futures are the same as those for standard-sized Wheat" SER 9151 / CBOT 22-254: limit levels set to the full-size values each business day. |
| limit_hit_days_2019_2024 |  | 2019-2024 | cftc_ptc030422_wheat_limits.txt | "Previous Exchange analysis showed that a 7 percent price move traditionally captures 99 percent of all daily price movements, making limit days rare." Same limits as ZW; see ZW. |
| adv_published_latest | 922 (contracts/day) | YTD Jan-Sep 2026 | cme_web_adv_report_2026-10.txt | "MINI WHEAT 970 524.14 85.0% 1,122.86 -13.6% 922 958 -3.7%" |
| adv_2022_11_2023_10 | 1523 (contracts/day) | YTD Jan-Aug 2023 (partial window) | cme_web_adv_report_2023-09.txt | "MINI WHEAT 1,917 1,117.26 71.6% 2,708.55 -29.2% 1,523 1,302 17.0%" |
| open_interest |  |  |  | No CFTC COT market for this contract in the 2022-2026 files; CME OI not retrieved. |
| retail_share |  |  | mondo_cbot_mini_ag_ecbot_2007.html.txt | "offer global customers, particularly in Asia, a smaller contract that is sized to their needs" No retail share found; small-size design (1/5 of full size). |
| commercial_hedger_share |  |  |  | No COT market; parent ZW figures do not transfer. |
| nonreportable_share |  |  |  | No COT market. |
| market_maker_program | none current found; CBOT mini-sized grains MM program 2007-11-01..2009-12-31 (up to 3 market makers, max spread 32 ticks, min size 1, fee waivers) | checked 2026-10-21 | cftc_rul091009cbot001.txt; cbot_fee_schedule_2026-10-01.txt | "Start Date is November 1, 2007 End Date is December 31, 2009" Fee schedule 2026-10-01 waiver table names no mini grain. |
| hft_automated_share |  |  |  | Not tabulated by CFTC OCE for minis. |
| median_spread_ticks_main |  |  |  | Not found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | Not found. |
| volume_per_minute |  |  |  | Not found; ADV ~1,000-2,000/day over ~17 h of trading. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | Same underlying as ZW; see ZW. |
| microstructure_research | Volkenand, Filler, Odening (2018) AFR, order imbalance [size]: positive (lagged order imbalance predicts returns for some contracts) [abstract only]; Arzandeh and Frank (2017; AJAE 2019), LOB beyond best quotes [size]: positive for LOB information share (40-42% for grains); not a trading test |  | see A1_grains.md F10 | No study on the mini contract itself found. |

### MZC: Micro Corn Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Micro Corn Futures |  | cme_faq_micro_ag.html.txt | "Micro Corn Futures" |
| product_code | MZC |  | cme_ser9512_micro_grains.txt | "Commodity Code MZC MZW MZS MZL MZM; Rulebook Chapter 10O 14O 11O 12O 13O" Rulebook chapter 10O |
| tick_size | 0.5 (US cents per bushel) |  | cme_ser9512_micro_grains.txt | "1/2 of one (1) cent ($0.005) per bushel ($2.50 per contract)" Twice the standard tick: "All Micro Agricultural contracts have a tick size that is twice the size of the standard contract." (cme_faq_micro_ag.html.txt; its table prints "$0.050/bu", apparently cents mislabelled as dollars; the SER value is used.) |
| tick_value | 2.5 (USD per contract) |  | cme_ser9512_micro_grains.txt | "1/2 of one (1) cent ($0.005) per bushel ($2.50 per contract)" |
| contract_size | 500 (bushels) |  | cme_ser9512_micro_grains.txt | "Trading Unit 500 bushels" |
| settlement | financially settled to the standard contract settlement |  | cme_ser9512_micro_grains.txt | "Settlement Method Financially Settled" FAQ: "They settle on a daily and final basis to the standard sized contract, which can be at a nontradable tick." |
| launch_date | 2025-02-24 (trade date) |  | cme_ser9512_micro_grains.txt | "Effective Sunday, February 23, 2025, for trade date Monday, February 24, 2025 ... will list the Micro Corn, Micro Wheat, Micro Soybean, Micro Soybean Oil, and Micro Soybean Meal Futures contracts" SER subject: "Initial Listing". cme_pr_20250130_micro_grains.html.txt: "will launch a suite of micro grain and oilseed futures contracts on February 24, 2025". |
| globex_60_dates_in_2023-11..2024-02 | False | 2023-11-01..2024-02-29 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed until 2025-02-24, so zero trade dates in the pilot window. |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | mirror ZC |  | cme_faq_micro_ag.html.txt | "The daily price limits for Micro Agricultural contracts will mirror the daily price limits for the standard-sized contracts." |
| limit_hit_days_2019_2024 |  | 2019-2024 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed in 2019-2024; underlying limits as ZC. |
| adv_published_latest |  | searched Sep 2026 report | cme_web_adv_report_2026-10.txt | No micro grain row in the CME Exchange ADV Report (September 2026). One WebSearch (call 7). News (irei_micro_launch.html.txt, citing Bloomberg): "More than 54,000 contracts had been traded by the morning of Feb. 24, according to CME." [news, all five micros, not evidence-grade]. |
| adv_2022_11_2023_10 |  | 2022-11..2023-10 | cme_ser9512_micro_grains.txt | Not listed. |
| open_interest |  |  |  | No CFTC COT market for micro grains in the 2025-2026 files. |
| retail_share |  |  | cme_pr_20250130_micro_grains.html.txt | ""These products are key to expanding market opportunities for retail investors, and their smaller contract sizes enable our clients to more effectively diversify" (Saxo, quoted in the CME release)" No CME retail share. A Bloomberg headline "CME is targeting retail traders with micro corn soy contracts" seen only as a search-result title [unverified]. |
| commercial_hedger_share |  |  |  | No COT market. |
| nonreportable_share |  |  |  | No COT market. |
| market_maker_program | none found | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt | "Micro Agricultural Cash Settlement/Delivery $0.15 $0.20 $0.50" Fee schedule lists micro ag fees but no waiver; SER 9512 lists fees and general IIP/IVIP/FMIP rows only. Two WebSearches. |
| hft_automated_share |  |  |  | Not tabulated (product post-dates CFTC OCE studies). |
| median_spread_ticks_main |  |  |  | Not found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | Not found. |
| volume_per_minute |  |  |  | Not found. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | Same underlying as ZC. |
| microstructure_research | [] |  | see A1_grains.md F10 | No study on micro grains found; see ZC for full-size studies (relation: size). |

### MZS: Micro Soybean Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Micro Soybean Futures |  | cme_faq_micro_ag.html.txt | "Micro Soybean Futures" |
| product_code | MZS |  | cme_ser9512_micro_grains.txt | "Commodity Code MZC MZW MZS MZL MZM; Rulebook Chapter 10O 14O 11O 12O 13O" Rulebook chapter 11O |
| tick_size | 0.5 (US cents per bushel) |  | cme_ser9512_micro_grains.txt | "1/2 of one (1) cent ($0.005) per bushel ($2.50 per contract)" Twice the standard tick: "All Micro Agricultural contracts have a tick size that is twice the size of the standard contract." (cme_faq_micro_ag.html.txt; its table prints "$0.050/bu", apparently cents mislabelled as dollars; the SER value is used.) |
| tick_value | 2.5 (USD per contract) |  | cme_ser9512_micro_grains.txt | "1/2 of one (1) cent ($0.005) per bushel ($2.50 per contract)" |
| contract_size | 500 (bushels) |  | cme_ser9512_micro_grains.txt | "Trading Unit 500 bushels" |
| settlement | financially settled to the standard contract settlement |  | cme_ser9512_micro_grains.txt | "Settlement Method Financially Settled" FAQ: "They settle on a daily and final basis to the standard sized contract, which can be at a nontradable tick." |
| launch_date | 2025-02-24 (trade date) |  | cme_ser9512_micro_grains.txt | "Effective Sunday, February 23, 2025, for trade date Monday, February 24, 2025 ... will list the Micro Corn, Micro Wheat, Micro Soybean, Micro Soybean Oil, and Micro Soybean Meal Futures contracts" SER subject: "Initial Listing". cme_pr_20250130_micro_grains.html.txt: "will launch a suite of micro grain and oilseed futures contracts on February 24, 2025". |
| globex_60_dates_in_2023-11..2024-02 | False | 2023-11-01..2024-02-29 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed until 2025-02-24, so zero trade dates in the pilot window. |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | mirror ZS |  | cme_faq_micro_ag.html.txt | "The daily price limits for Micro Agricultural contracts will mirror the daily price limits for the standard-sized contracts." |
| limit_hit_days_2019_2024 |  | 2019-2024 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed in 2019-2024; underlying limits as ZS. |
| adv_published_latest |  | searched Sep 2026 report | cme_web_adv_report_2026-10.txt | No micro grain row in the CME Exchange ADV Report (September 2026). One WebSearch (call 7). News (irei_micro_launch.html.txt, citing Bloomberg): "More than 54,000 contracts had been traded by the morning of Feb. 24, according to CME." [news, all five micros, not evidence-grade]. |
| adv_2022_11_2023_10 |  | 2022-11..2023-10 | cme_ser9512_micro_grains.txt | Not listed. |
| open_interest |  |  |  | No CFTC COT market for micro grains in the 2025-2026 files. |
| retail_share |  |  | cme_pr_20250130_micro_grains.html.txt | ""These products are key to expanding market opportunities for retail investors, and their smaller contract sizes enable our clients to more effectively diversify" (Saxo, quoted in the CME release)" No CME retail share. A Bloomberg headline "CME is targeting retail traders with micro corn soy contracts" seen only as a search-result title [unverified]. |
| commercial_hedger_share |  |  |  | No COT market. |
| nonreportable_share |  |  |  | No COT market. |
| market_maker_program | none found | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt | "Micro Agricultural Cash Settlement/Delivery $0.15 $0.20 $0.50" Fee schedule lists micro ag fees but no waiver; SER 9512 lists fees and general IIP/IVIP/FMIP rows only. Two WebSearches. |
| hft_automated_share |  |  |  | Not tabulated (product post-dates CFTC OCE studies). |
| median_spread_ticks_main |  |  |  | Not found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | Not found. |
| volume_per_minute |  |  |  | Not found. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | Same underlying as ZS. |
| microstructure_research | [] |  | see A1_grains.md F10 | No study on micro grains found; see ZS for full-size studies (relation: size). |

### MZW: Micro Wheat Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Micro Wheat Futures |  | cme_faq_micro_ag.html.txt | "Micro Wheat Futures" |
| product_code | MZW |  | cme_ser9512_micro_grains.txt | "Commodity Code MZC MZW MZS MZL MZM; Rulebook Chapter 10O 14O 11O 12O 13O" Rulebook chapter 14O |
| tick_size | 0.5 (US cents per bushel) |  | cme_ser9512_micro_grains.txt | "1/2 of one (1) cent ($0.005) per bushel ($2.50 per contract)" Twice the standard tick: "All Micro Agricultural contracts have a tick size that is twice the size of the standard contract." (cme_faq_micro_ag.html.txt; its table prints "$0.050/bu", apparently cents mislabelled as dollars; the SER value is used.) |
| tick_value | 2.5 (USD per contract) |  | cme_ser9512_micro_grains.txt | "1/2 of one (1) cent ($0.005) per bushel ($2.50 per contract)" |
| contract_size | 500 (bushels) |  | cme_ser9512_micro_grains.txt | "Trading Unit 500 bushels" |
| settlement | financially settled to the standard contract settlement |  | cme_ser9512_micro_grains.txt | "Settlement Method Financially Settled" FAQ: "They settle on a daily and final basis to the standard sized contract, which can be at a nontradable tick." |
| launch_date | 2025-02-24 (trade date) |  | cme_ser9512_micro_grains.txt | "Effective Sunday, February 23, 2025, for trade date Monday, February 24, 2025 ... will list the Micro Corn, Micro Wheat, Micro Soybean, Micro Soybean Oil, and Micro Soybean Meal Futures contracts" SER subject: "Initial Listing". cme_pr_20250130_micro_grains.html.txt: "will launch a suite of micro grain and oilseed futures contracts on February 24, 2025". |
| globex_60_dates_in_2023-11..2024-02 | False | 2023-11-01..2024-02-29 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed until 2025-02-24, so zero trade dates in the pilot window. |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | mirror ZW |  | cme_faq_micro_ag.html.txt | "The daily price limits for Micro Agricultural contracts will mirror the daily price limits for the standard-sized contracts." |
| limit_hit_days_2019_2024 |  | 2019-2024 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed in 2019-2024; underlying limits as ZW. |
| adv_published_latest |  | searched Sep 2026 report | cme_web_adv_report_2026-10.txt | No micro grain row in the CME Exchange ADV Report (September 2026). One WebSearch (call 7). News (irei_micro_launch.html.txt, citing Bloomberg): "More than 54,000 contracts had been traded by the morning of Feb. 24, according to CME." [news, all five micros, not evidence-grade]. |
| adv_2022_11_2023_10 |  | 2022-11..2023-10 | cme_ser9512_micro_grains.txt | Not listed. |
| open_interest |  |  |  | No CFTC COT market for micro grains in the 2025-2026 files. |
| retail_share |  |  | cme_pr_20250130_micro_grains.html.txt | ""These products are key to expanding market opportunities for retail investors, and their smaller contract sizes enable our clients to more effectively diversify" (Saxo, quoted in the CME release)" No CME retail share. A Bloomberg headline "CME is targeting retail traders with micro corn soy contracts" seen only as a search-result title [unverified]. |
| commercial_hedger_share |  |  |  | No COT market. |
| nonreportable_share |  |  |  | No COT market. |
| market_maker_program | none found | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt | "Micro Agricultural Cash Settlement/Delivery $0.15 $0.20 $0.50" Fee schedule lists micro ag fees but no waiver; SER 9512 lists fees and general IIP/IVIP/FMIP rows only. Two WebSearches. |
| hft_automated_share |  |  |  | Not tabulated (product post-dates CFTC OCE studies). |
| median_spread_ticks_main |  |  |  | Not found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | Not found. |
| volume_per_minute |  |  |  | Not found. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | Same underlying as ZW. |
| microstructure_research | [] |  | see A1_grains.md F10 | No study on micro grains found; see ZW for full-size studies (relation: size). |

### MZL: Micro Soybean Oil Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Micro Soybean Oil Futures |  | cme_faq_micro_ag.html.txt | "Micro Soybean Oil Futures" |
| product_code | MZL |  | cme_ser9512_micro_grains.txt | "Commodity Code MZC MZW MZS MZL MZM; Rulebook Chapter 10O 14O 11O 12O 13O" Rulebook chapter 12O |
| tick_size | 0.02 (US cents per pound) |  | cme_ser9512_micro_grains.txt | "1/50th of one (1) cent ($0.0002) per pound ($1.20 per contract)" Twice the standard tick: "All Micro Agricultural contracts have a tick size that is twice the size of the standard contract." (cme_faq_micro_ag.html.txt; its table prints "$0.050/bu", apparently cents mislabelled as dollars; the SER value is used.) |
| tick_value | 1.2 (USD per contract) |  | cme_ser9512_micro_grains.txt | "1/50th of one (1) cent ($0.0002) per pound ($1.20 per contract)" |
| contract_size | 6000 (pounds) |  | cme_ser9512_micro_grains.txt | "Trading Unit ... 6,000 pounds" |
| settlement | financially settled to the standard contract settlement |  | cme_ser9512_micro_grains.txt | "Settlement Method Financially Settled" FAQ: "They settle on a daily and final basis to the standard sized contract, which can be at a nontradable tick." |
| launch_date | 2025-02-24 (trade date) |  | cme_ser9512_micro_grains.txt | "Effective Sunday, February 23, 2025, for trade date Monday, February 24, 2025 ... will list the Micro Corn, Micro Wheat, Micro Soybean, Micro Soybean Oil, and Micro Soybean Meal Futures contracts" SER subject: "Initial Listing". cme_pr_20250130_micro_grains.html.txt: "will launch a suite of micro grain and oilseed futures contracts on February 24, 2025". |
| globex_60_dates_in_2023-11..2024-02 | False | 2023-11-01..2024-02-29 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed until 2025-02-24, so zero trade dates in the pilot window. |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | mirror ZL |  | cme_faq_micro_ag.html.txt | "The daily price limits for Micro Agricultural contracts will mirror the daily price limits for the standard-sized contracts." |
| limit_hit_days_2019_2024 |  | 2019-2024 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed in 2019-2024; underlying limits as ZL. |
| adv_published_latest |  | searched Sep 2026 report | cme_web_adv_report_2026-10.txt | No micro grain row in the CME Exchange ADV Report (September 2026). One WebSearch (call 7). News (irei_micro_launch.html.txt, citing Bloomberg): "More than 54,000 contracts had been traded by the morning of Feb. 24, according to CME." [news, all five micros, not evidence-grade]. |
| adv_2022_11_2023_10 |  | 2022-11..2023-10 | cme_ser9512_micro_grains.txt | Not listed. |
| open_interest |  |  |  | No CFTC COT market for micro grains in the 2025-2026 files. |
| retail_share |  |  | cme_pr_20250130_micro_grains.html.txt | ""These products are key to expanding market opportunities for retail investors, and their smaller contract sizes enable our clients to more effectively diversify" (Saxo, quoted in the CME release)" No CME retail share. A Bloomberg headline "CME is targeting retail traders with micro corn soy contracts" seen only as a search-result title [unverified]. |
| commercial_hedger_share |  |  |  | No COT market. |
| nonreportable_share |  |  |  | No COT market. |
| market_maker_program | none found | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt | "Micro Agricultural Cash Settlement/Delivery $0.15 $0.20 $0.50" Fee schedule lists micro ag fees but no waiver; SER 9512 lists fees and general IIP/IVIP/FMIP rows only. Two WebSearches. |
| hft_automated_share |  |  |  | Not tabulated (product post-dates CFTC OCE studies). |
| median_spread_ticks_main |  |  |  | Not found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | Not found. |
| volume_per_minute |  |  |  | Not found. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | Same underlying as ZL. |
| microstructure_research | [] |  | see A1_grains.md F10 | No study on micro grains found; see ZL for full-size studies (relation: size). |

### MZM: Micro Soybean Meal Futures

| Field | Value | Window | Source | Quote / note |
|---|---|---|---|---|
| product_name | Micro Soybean Meal Futures |  | cme_faq_micro_ag.html.txt | "Micro Soybean Meal Futures" |
| product_code | MZM |  | cme_ser9512_micro_grains.txt | "Commodity Code MZC MZW MZS MZL MZM; Rulebook Chapter 10O 14O 11O 12O 13O" Rulebook chapter 13O |
| tick_size | 0.2 (USD per short ton) |  | cme_ser9512_micro_grains.txt | "$0.20 per short ton ($2.00 per contract)" Twice the standard tick: "All Micro Agricultural contracts have a tick size that is twice the size of the standard contract." (cme_faq_micro_ag.html.txt; its table prints "$0.050/bu", apparently cents mislabelled as dollars; the SER value is used.) |
| tick_value | 2.0 (USD per contract) |  | cme_ser9512_micro_grains.txt | "$0.20 per short ton ($2.00 per contract)" |
| contract_size | 10 (short tons) |  | cme_ser9512_micro_grains.txt | "Trading Unit ... 10 short tons" |
| settlement | financially settled to the standard contract settlement |  | cme_ser9512_micro_grains.txt | "Settlement Method Financially Settled" FAQ: "They settle on a daily and final basis to the standard sized contract, which can be at a nontradable tick." |
| launch_date | 2025-02-24 (trade date) |  | cme_ser9512_micro_grains.txt | "Effective Sunday, February 23, 2025, for trade date Monday, February 24, 2025 ... will list the Micro Corn, Micro Wheat, Micro Soybean, Micro Soybean Oil, and Micro Soybean Meal Futures contracts" SER subject: "Initial Listing". cme_pr_20250130_micro_grains.html.txt: "will launch a suite of micro grain and oilseed futures contracts on February 24, 2025". |
| globex_60_dates_in_2023-11..2024-02 | False | 2023-11-01..2024-02-29 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed until 2025-02-24, so zero trade dates in the pilot window. |
| match_algorithm |  |  | ideals_2022_three_essays_ag_liquidity.txt | "the Split FIFO/Pro-Rata algorithm ("K algorithm") is used in all of CBOT agricultural futures and spread futures markets" Product-specific algorithm not found for this contract. Peng (2022) states K for all CBOT agricultural futures in 2018; whether it covers this contract (or the 2025 micros) is unverified. |
| trading_hours | see F1 | | | |
| price_limits | mirror ZM |  | cme_faq_micro_ag.html.txt | "The daily price limits for Micro Agricultural contracts will mirror the daily price limits for the standard-sized contracts." |
| limit_hit_days_2019_2024 |  | 2019-2024 | cme_ser9512_micro_grains.txt | "for trade date Monday, February 24, 2025" Not listed in 2019-2024; underlying limits as ZM. |
| adv_published_latest |  | searched Sep 2026 report | cme_web_adv_report_2026-10.txt | No micro grain row in the CME Exchange ADV Report (September 2026). One WebSearch (call 7). News (irei_micro_launch.html.txt, citing Bloomberg): "More than 54,000 contracts had been traded by the morning of Feb. 24, according to CME." [news, all five micros, not evidence-grade]. |
| adv_2022_11_2023_10 |  | 2022-11..2023-10 | cme_ser9512_micro_grains.txt | Not listed. |
| open_interest |  |  |  | No CFTC COT market for micro grains in the 2025-2026 files. |
| retail_share |  |  | cme_pr_20250130_micro_grains.html.txt | ""These products are key to expanding market opportunities for retail investors, and their smaller contract sizes enable our clients to more effectively diversify" (Saxo, quoted in the CME release)" No CME retail share. A Bloomberg headline "CME is targeting retail traders with micro corn soy contracts" seen only as a search-result title [unverified]. |
| commercial_hedger_share |  |  |  | No COT market. |
| nonreportable_share |  |  |  | No COT market. |
| market_maker_program | none found | checked 2026-10-21 | cbot_fee_schedule_2026-10-01.txt | "Micro Agricultural Cash Settlement/Delivery $0.15 $0.20 $0.50" Fee schedule lists micro ag fees but no waiver; SER 9512 lists fees and general IIP/IVIP/FMIP rows only. Two WebSearches. |
| hft_automated_share |  |  |  | Not tabulated (product post-dates CFTC OCE studies). |
| median_spread_ticks_main |  |  |  | Not found. |
| median_spread_ticks_overnight |  |  |  | Not found. |
| depth_best_level |  |  |  | Not found. |
| touch_queue_size |  |  |  | Not found. |
| volume_per_minute |  |  |  | Not found. |
| scheduled_releases_per_week | see F3 | | | |
| usda_report_timing | see F3 | | | |
| weekend_gap_exposure | see F1 | | | |
| jump_frequency |  |  |  | Same underlying as ZM. |
| microstructure_research | [] |  | see A1_grains.md F10 | No study on micro grains found; see ZM for full-size studies (relation: size). |


## Run log and gaps

- Worker A1_grains, 2026-10-21 05:31-06:07 PDT. WebSearch calls used: 10 of 40 (micro
  launch; mini delisting; grain matching algorithm; GCC product sheet; grain MM programs; micro MM programs; micro
  volume; limit-day history; 2022 wheat limit filing; mini launch). No budget notice was received. Firecrawl not used.
- Fetch routes: curl for CFTC, USDA, Databento, IDEALS, OpenAlex, Mondo Visione; Wayback (curl, id_ captures) for
  cmegroup.com; Scrapling stealthy session for AgEcon Search after its robots.txt check (logged in log.tsv).
  Blocked: AgEcon to plain curl (AWS WAF 202), Wiley (403, not scraped), USDA OCE and FAS live pages (403, Wayback
  used), Feedstuffs (403), CME GCC product resources on atlassian (202, empty), CFTC filing URLs for the 2025 micro
  grain self-certification (probed patterns, not found).
- Not found (left null with what was searched): micro grain ADV, OI and matching algorithm; limit-settle day counts
  2019-2024 for any grain (only the 2022 wheat episode is documented as "multiple limit-move days"); median spreads
  (all published figures are means); median depth and contracts per minute (QV inputs); ZL and ZM spread, depth,
  flow and automated-trading shares; mini grain spread and depth; any current (post-2011) grain futures
  market-maker program; retail share for any grain product.
- Read only abstracts (marked [unverified] where used): Volkenand et al. 2018, Lehecka et al. 2014, Adjemian and
  Irwin 2018, He et al. 2020, de Boer et al. 2022, JCM 2023 soybean complex.
- Owned-data magnitudes (sigma_1m, R_d, owned ADV, owned >4 sigma day counts, owned limit-day counts) are A0's.
- The per-candidate sheets in section S were generated by work/A1_grains/A1_grains_build.py (it appends to this
  file; re-running it would duplicate section S).
