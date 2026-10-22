# A1_crude: Layer 1 fact sheets, crude oil family (MCL, QM, CL)

Worker: A1_crude (Opus 5.5), Stage E.28 Part A, started 2026-10-21 02:57 PDT. Facts only; no scoring.
All source files are under reports/stage_e28_briefs/pages/A1_crude/ (log: log.tsv there, with URL, UTC and PDT
fetch times, method and sha256). Quotes are verbatim from the saved files (PDFs read through pdftotext; HTML through
a tag stripper, files `*.html.txt`). No market data was read. Owned-bar magnitudes (sigma_1m, R_d, owned ADV) belong
to A0 and are not computed here.

Status notes (first pass): WebSearch stopped at call 10 of 40 at 03:07 PDT on 2026-10-21, when a call returned
"You've hit your session limit · resets 5:10am (America/Vancouver)". Firecrawl returned "Insufficient credits" at
about 03:01 PDT. cmegroup.com refuses this machine's IP (HTTP 403, confirmed); the CME contract-spec pages saved
from Wayback carry their spec values only through JavaScript, which Wayback did not archive, so they hold no spec
values. Spec facts below come from the NYMEX rulebook chapters (Wayback raw copies) and NYMEX submissions to the
CFTC (cftc.gov).

## F. Family-wide facts (referenced from each sheet)

### F1. Price limits: NYMEX Rule 589 dynamic circuit breakers (CL, and MCL and QM as associated products)

- CL rulebook (nymex_rulebook_ch200_CL.txt, Chapter 200, 200102.D): "At the commencement of each trading day, the
  contract shall be subject to special fluctuation limits as set forth in Rule 589 and in the Special Price
  Fluctuation Limits Table in the Interpretations & Special Notices Section of Chapter 5."
- QM rulebook (nymex_rulebook_ch401_QM.txt, Chapter 401, 401102.D) and MCL (cftc_ptc060721_MCL_launch.txt,
  309102.D) carry the same Rule 589 reference. The MCL launch filing's Rule 589 table entry lists MCL as
  "Associated" with "CL" and a "15% of Dynamically Calculated Reference Price" variant (Exhibit D).
- Level, CL: raised from 7% to 15% by emergency action, then made permanent. cftc_ptc032020_rule589_15pct.txt:
  "Specifically, GCC increased the dynamic price fluctuation limits of Light Sweet Crude Oil and Brent Crude Oil
  Last Day Financial Futures and all Associated Products from 7% to 15%." cftc_ptc120820_rule589_perm.txt: "The
  GCC increased the dynamic price fluctuation limits for the Contracts from 7% to 15% as an emergency action on
  Friday, March 13, 2020 and Thursday, March 19, 2020. The emergency action was taken in light of recent price
  movements" ... "the permanent amendment to Rule 589. with respect to the Contracts (the "Rule Amendments")
  effective on Monday, December 21, 2020."
- Mechanism (cftc_ptc032020_rule589_15pct.txt, Rule 589.B): "If the lead contract month ... is bid or offered via
  Globex at the upper or lower price fluctuation limit at the first special price fluctuation limit level, as
  applicable, it will be considered a triggering event that will begin a two (2) minute monitoring period ... If,
  however, at the end of the two (2) minute monitoring period, the lead contract month of the primary futures
  contract is bid or offered at the applicable special price fluctuation limit, a two (2) minute temporary trading
  halt will commence in all contract months of the primary futures contract and in all contract months of
  associated products". Earlier history (cftc_ptc020918_rule589.txt, 2018): "The targets were set at 10% for
  energy products and 7% for metals products."
- Limit-hit days 2019-2024: NOT FOUND as a count. The only sourced evidence is that the GCC raised the limits by
  emergency action twice in March 2020 "in light of recent price movements" (quote above), which shows limit stress
  in March 2020 but does not state that a limit was hit or on which days. One WebSearch (call 8) found no CME halt
  log for 2019-2024; forum and news snippets that mention a CL halt were pointers only and are not used. Unknown.

### F2. Trading hours (CME Globex)

- MCL, from the NYMEX launch submission (cftc_ptc060721_MCL_launch.txt): "CME Globex and CME ClearPort: Sunday -
  Friday 6:00 p.m. - 5:00 p.m. Eastern Time/ET (5:00 p.m. - 4:00 p.m. Central Time/CT) with a 60- minute break each
  day beginning at 5:00 p.m. ET (4:00 p.m. CT)". Pre-open: "Monday - Thursday 5:45 p.m. - 6:00 p.m. ET".
- CL and QM: the rulebook chapters say only "The hours for trading shall be determined by the Exchange." (Ch. 200,
  200102.A) and "The hours of trading for this contract shall be determined by the Exchange." (Ch. 401, 401102.A).
  The CME spec pages that state the hours could not be read (see status notes). CL and QM hours are therefore
  [unverified]; they are commonly the same Sunday-Friday 18:00-17:00 ET schedule as MCL, but that is not sourced
  here.

### F3. Weekend-gap exposure

- Globex is closed from Friday 17:00 ET to Sunday 18:00 ET (F2, MCL quote). No source was fetched for whether any
  crude-oil instrument trades while Globex is closed. The C4 item is about an underlying that trades while Globex is
  closed (crypto spot); WTI is a physical commodity whose benchmark price discovery is the CL futures itself
  (MCL and QM settle on the CL final settlement price: Ch. 309 "Floating Price" and Ch. 401 401101 "The Floating
  Price for each contract month will be equal to the Light Sweet Crude Oil Futures contract final settlement price
  for the corresponding contract month"). A 24/7 crude venue was not searched for. Note as a pointer only, not
  evidence: a WebSearch result summary (call 7) mentioned a July 2026 Law360 item that the CFTC paused a CME plan for
  round-the-clock crude futures trading; it postdates every window here and was not fetched.

### F4. Commercial-hedger and small-trader shares (CFTC COT, Disaggregated, futures only)

- Source files: cftc_fut_disagg_txt_2022.zip and cftc_fut_disagg_txt_2023.zip (CFTC annual history files), unzipped
  to cot22/ and cot23/; script work/A1_crude/A1_crude_cot.py; output work/A1_crude/A1_crude_cot_out.txt. Only
  report dates 2022-11-01..2023-10-31 were used (53 weekly reports).
- Market used: CFTC code 067651 "WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE" (named "CRUDE OIL, LIGHT SWEET - NEW
  YORK MERCANTILE EXCHANGE" in some rows), Contract_Units "(CONTRACTS OF 1,000 BARRELS)", that is CL.
- Shares of open interest, mean over the 53 reports, computed as (long + short [+ 2 x spread]) / (2 x OI):
  producer/merchant/processor/user 26.7%; swap dealers 18.3%; managed money 33.2%; nonreportable 4.2% (min 3.6%,
  max 4.8%). Mean OI 1,708,817 contracts (median 1,752,072); mean number of reportable traders 332.
- MCL and QM: no separate COT market exists in the disaggregated file (searched all market names containing CRUDE,
  WTI, MICRO, MINI; only "MICRO GOLD" and "MINI SOYBEANS" appear among micro/mini names). Whether CFTC folds MCL
  and QM positions into 067651 was not verified. Unknown for MCL and QM.
- Caveat: COT shares are shares of open interest, not of volume. They say little about intraday flow.

### F5. Automated and HFT participation (CFTC research, CL only)

- Haynes and Roberts (2015), "Automated Trading in Futures Markets", CFTC OCE, March 13, 2015
  (cftc_haynes_roberts_2015_automated_trading.txt). Sample: "CME transaction data, November 12, 2012 - October 31,
  2014." Their "Crude Oil" is the NYMEX crude oil futures (CL); MCL did not exist and QM is not tabulated.
  - Table 3 (columns "Products  Non-Electronic (%)  ATS (%)  Manual (%)"; parentheses are shares of the full
    sample), subgroup row: "Energy - Crude Oil 22 5.5 (0.3) 54.3 (3.2) 40.2 (2.4)" = 22 products, non-electronic
    5.5%, automated (ATS) 54.3%, manual 40.2% of crude-oil-subgroup volume (all crude products, not CL alone).
  - Table 4: "Energy - Crude Oil Crude Oil 280 30.2 45.5 19.5" = total volume 280 million, ATS-ATS 30.2%,
    ATS-MAN 45.5%, MAN-MAN 19.5% of volume. So about 75.7% of CL volume had at least one automated side.
  - Table 6 (small vs large volume traders; large = at least 0.5% of daily volume): "Crude Oil 65,410 18.4 30.5 538
    34.6 11.8" (small traders: N 65,410, ATS 18.4%, MAN 30.5%; large traders: N 538, ATS 34.6%, MAN 11.8%).
  - Text: "In crude oil, for instance, 77 percent of all spread to spread trades have an automated participant on
    the buy or sell side." and "The widest disparity in speeds occurs in the crude oil market, where, as above,
    manual activity is more prevalent than in the other three markets."
  - Table 7, liquidity-providing side, share of two-sided volume by time from order placement to execution: "Crude
    Oil 3.9 1.3 2.2 0.6 1.4 0.4 6.2 2.7 5.0 3.5 22.8" (ATS/MAN for 0-100 ms, 100-500 ms, 500 ms-1 s, 1-10 s,
    10 s-1 min, then remaining electronic volume).
- Raman, Robe and Yadav, "Electronic Market Makers, Trader Anonymity and Market Fragility", CFTC-hosted working paper
  (Dec 2012, released 2014; cftc_raman_robe_yadav_2012_EMM.txt), NYMEX WTI crude futures, intraday position-level
  data 2006-2011. EMM definition: "EMMs are traders who trade more than 2000 trades a day and carry less than 5% of
  their daily trading volume overnight." Share: "we identify 52 traders as the de facto EMMs ... those 52 traders
  (0.35% of all trading accounts) account for about 50% of the overall trading volume in the world's most heavily
  traded commodity". Result: "electronic market makers reduce their participation and their liquidity provision in
  periods of significantly high and persistent volatility, in periods of significantly high and persistent customer
  order imbalances, and in periods of significantly high and persistent bid ask spreads."
- No CFTC update of Haynes-Roberts with per-contract shares was retrieved (one WebSearch, call 9, did not find it;
  searching stopped afterwards).

(Resumed 2026-10-21 05:11 PDT after the usage cut; WebSearch count restarts at call 11 of 40.)

### F1b. Limit and circuit-breaker events found (addendum to F1)

- CFTC Interim Staff Report, Nov 2020 (cftc_2020_interim_staff_report_WTI_april20.txt): "During the April 20
  trading session, exchange-based control mechanisms (such as dynamic circuit breakers ("DCBs") designed to impose
  pauses in the event of rapid or large price moves) were triggered." and "In total, on April 20, over 30 DCBs were
  triggered in the May Contract and more than 10 DCBs were triggered in the May-June Spread contract." Mechanism as
  stated there: "If markets move +/- 15% in that time, a two-minute halt is initiated" (rolling 60-minute
  lookback). Note: "On April 20, the active contract was the June Contract. To the extent a non-active period or
  underlying spreads are triggered, the market only halts for that particular contract." So 2020-04-20 is one
  sourced DCB day (expiring May 2020 contract, CL). TAS: "the number of TAS contracts traded at the maximum price
  limit was more than 70 times higher than all of 2019".
- A count of DCB or limit days per year 2019-2024 was not found. The only sourced day is 2020-04-20. Unknown
  whether at least one per year on average occurred.

### F6. Scheduled crude-specific releases (EIA WPSR, API) and measured impact

- EIA Weekly Petroleum Status Report (eia_wpsr_schedule.html.txt): "The standard release time and day of the week
  will be at 10:30 a.m. eastern time on Wednesday with the following exceptions." Holiday weeks move to Thursday
  11:00 or 12:00 ET (table on the same page, e.g. "January 2, 2025 Thursday 11:00 a.m. New Year's Day").
  10:30 ET = 07:30 PDT, inside the main session (06:30-13:00 PT).
- API Weekly Statistical Bulletin: the api.org page fetched returned a 404 (api_wsb.html.txt: "404 Page Not
  Found"). Timing from Rousse and Sevi (2016, FEEM NDL2016-070, rousse_sevi_2016_feem.txt): "the inventory news
  reported by API every Tuesday afternoon at 4:30 p.m." (ET; 13:30 PT, after the 13:00 PT main-session end, inside
  the Globex overnight session).
- Count of scheduled crude-specific high-impact releases per week: EIA WPSR, 1 per week (sourced). API, 1 per week
  (sourced timing; impact weak, see below). Whether API counts as "high-impact" is a scorer's call; the evidence
  below says its price impact is small. Baker Hughes rig count (Fridays) and OPEC meetings were not searched.
- Measured impact, EIA: Alquist, Ellwanger and Jin (2020, Bank of Canada SWP 2020-8, published in J. Futures
  Markets; boc_swp2020-8_oil_inventory_news.txt), nearby WTI futures, 2003-10..2017-10, 15-minute window
  [-5,+10] min around the release: Table 2 "Nearby WTI contract 01/10/2003 733 -7.8 91.4 732 0.4 39.8", i.e.
  std of the 15-minute return 91.4 bp on announcement days vs 39.8 bp in the same window on the previous day.
  First stage: "Crude Oil inventory news -56.56***" (bp per 1 SD of crude inventory surprise). Text: "higher-than-
  expected (lower-than-expected) U.S. oil inventories lead to systematic decreases (increases) in oil prices in the
  minutes following the announcement."
- Measured impact, API: Rousse and Sevi (2016) summarise Ye and Karali (2016, Energy Economics): "They find no
  significant, or at best a weakly significant, price impact of the API is and that the market mover for oil is
  indeed the EIA release." [Ye and Karali full text not fetched: the AgEcon PDF returned an AWS WAF challenge
  (HTTP 202); secondary quote only.]
- Pre-release order flow: Rousse and Sevi (2016), CL front month 2007-2014: "there are significantly more orders
  initiated by buyers in the two hours preceding the official release of the inventory level" and "a clear drop in
  the average price of -0.25% ahead of the news release. This is consistent with informed trading."
- Spread around releases (Roberts 2018 thesis, CL 2012-08..2013-07, umd_2018_depth_quoting_CL.txt): "During the
  day, there are clear drops in the volume share during the minutes surrounding 8:30am, 10am, and 10:30am. The
  bid-ask spread is affected by periods where expected news is released." (times appear to be ET, US macro at
  8:30 and 10:00 and EIA at 10:30; the thesis text does not state the zone in this passage.)

### F7. Spread, depth and queue facts (CL; none found for MCL or QM)

- Roberts (2018), PhD thesis, University of Maryland (supervisor A. S. Kyle), CL, CME market-depth (MBP-10) data
  "covering a time range from August 1, 2012 to the end of July 2013" (umd_2018_depth_quoting_CL.txt).
  - Spread: "Figure 3.5 shows that the majority of volume occurs when the bid-ask spread is equal to the minimum
    tick size." and "while the bid-ask spread is commonly equal to the minimum tick size, there are many instances
    where the spread opens up to two cents (two-ticks). Second, when the bid-ask spread is two-ticks or wider, the
    market returns to a one-tick spread very quickly."
  - Depth at the best level (Table 4.4, randomly selected timestamps, bid side): "1 8.8 8.6 1 1 2 4 7 11 17 21 39"
    = mean 8.8, SD 8.6, median 7 contracts, Q1 4, Q3 11. Session of the random timestamps not stated in the
    passage read.
  - Resting order size: "resting limit orders are most often a small size - close to one contract in our market
    during the sample period."
- CFTC Interim Staff Report (2020), Table 8 "Resting Depth in the Limit Order Book by Date and Product (1-minute
  Average)", CL outrights April 13-20, 2020: CLK0 best bid/ask 8/8 (4/13), 12/11, 10/11, 7/8, 4/6, 4/5 (4/20);
  CLM0 5/5 (4/13), 8/6, 8/7, 9/9, 11/10, 12/11 (4/20). Stress period, roll week.
- Lalor and Swishchuk (arXiv 2409.12721v3, 2026; arxiv_2409.12721v3_lalor_swishchuk_adverse.txt), CL Jun24,
  2024-04-09: "CL 1.70 1" (mean trade size 1.70, median 1 contract).
- Median spread in ticks by session, traded volume per minute, touch queue size for MCL and QM: not found.
  QV (depth / volume per minute) cannot be formed from sourced numbers for any of the three; A0 owns volume.

### F4b. COT addendum

- The four category shares in F4 sum to 82.4%; the remainder (about 17.6%, by subtraction, not computed directly)
  is "other reportables". The same script output also lists "06765A WTI FINANCIAL CRUDE OIL - NEW YORK MERCANTILE
  EXCHANGE" (OI mean 139,659, nonreportable 23.6%); that is a different cash-settled NYMEX product (not MCL or QM;
  name only, product code not verified).

### F5b. Automated-trading update (CFTC, through 2016)

- Haynes and Roberts, "Automated Trading in Futures Markets - Update", CFTC OCE, March 29, 2017
  (cftc_haynes_roberts_update.txt). Second sample "November 1, 2014 - October 31, 2016", CME transaction data.
  - Table 2, subgroup "Energy - Crude Oil 22 21 5.5 (0.3) 3.5 (0.3) 54.3 (3.2) 63.0 (5.5) 40.2 (2.4) 33.6 (2.9)":
    automated share of crude-subgroup volume 54.3% -> 63.0%, manual 40.2% -> 33.6%.
  - Table 3, CL: "Crude Oil 280 454 30.2 38.1 45.5 44.5 19.5 14.2": volume 454 million in 2014-16; ATS-ATS 38.1%,
    ATS-MAN 44.5%, MAN-MAN 14.2% (so about 82.6% of CL volume had at least one automated side in 2014-16).
  - Table 5 (large = at least 0.5% of daily volume): "Crude Oil 65,410 91,325 18.4 18.3 30.5 27.7 538 388 34.6 42.1
    11.8 8.8": in 2014-16 small traders ATS 18.3% + manual 27.7% = 46.0% of CL volume; large traders (388 accounts)
    ATS 42.1% + manual 8.8% = 50.9%.
  - Table 8, non-directional (intraday-netted) share of large traders' volume, full day: "Crude Oil 68.8 78.7 ..."
    (ATS, 2012-14 then 2014-16), i.e. 78.7% of automated large-trader CL volume nets out within the day.
  - Text: "the largest growth in the commodities starting from a lower base (e.g. crude oil)".
- No update after 2016 with per-contract crude rows was found (one WebSearch; the CFTC research index pages list
  only the 2015 paper, this update and "Macro News Announcements and Automated Trading").

### F8. Published microstructure research (crude family)

Each entry: relation to MCL/QM/CL; result for the C6 question (short-horizon predictability from order-book
variables, or passive liquidity provision net of costs).

1. Lalor and Swishchuk (2026, arXiv 2409.12721v3), CL Jun24, LOB data, a basic posting strategy and a stochastic
   optimal control market-making strategy. Relation: same product (CL). Result: negative for naive passive posting:
   "2024/04/23 CL Jun24 625 518 107" (625 limit-order fills, 518 adverse, 107 non-adverse) and "excluding adverse
   fills and realistic non-adverse fill probabilities substantially inflates trading performance." Not a
   peer-reviewed paper (arXiv). No net-of-cost profitability shown.
2. Roberts (2018), UMD PhD thesis, CL MBP-10 2012-08..2013-07. Relation: same product. Result: descriptive with
   some within-book predictability: "We show there exist certain predictable periods of both sides adjusting
   quotes conditional on certain well defined events." (lines 724-725); "We find
   empirical evidence that changes in market depth explains movement in the bid-ask spread. We show how combining
   movements in best quotes and visible depth provides a clearer picture of market direction." No trading
   strategy or cost analysis. Classed as positive-but-weak (descriptive, not a documented profitable signal); the
   scorer decides.
3. Tian, Duong and Kalev (2019), Energy Economics 81, 584-597 (abstract only, from IDEAS: ideas_tian_duong_kalev_2019
   .html.txt) [full text not fetched: SSRN-only; abstract-level, unverified beyond the abstract]. Relation: "crude
   oil futures market" (exchange not stated in the abstract). Result: LOB slope predicts volatility one day ahead
   ("the time-weighted limit order book slope is informative about price volatility one day ahead"); volatility,
   not direction. Not a short-horizon direction result.
4. Rousse and Sevi (2016, FEEM NDL2016-070), CL front month 2007-2014, trade-sign order imbalance before EIA
   releases. Relation: same product. Result: order imbalance before the release is related to the surprise
   ("significantly more orders initiated by buyers in the two hours preceding the official release"); an
   event-window trade-sign pattern, not a general short-horizon predictor and no costed strategy.
5. Raman, Robe and Yadav (2012/2014, CFTC), NYMEX WTI, electronic market makers. Relation: same product. Result:
   about 50% of volume from 52 EMM accounts; EMMs withdraw in high volatility and imbalance. Evidence of
   professional liquidity provision intensity, not of findable patterns.
6. Tse and Xiang (2005), "Market quality and price discovery: Introduction of the E-mini energy futures", Global
   Finance Journal 16(2), 164-179. Relation: QM (E-mini crude) and its full-size CL. Result: unknown: IDEAS page
   says "No abstract is available for this item." and the full text was not reachable [unverified; title only].
7. OFI, queue imbalance or trade-sign predictability studies on CL, MCL or QM: none found. Searches: WebSearch
   calls 11-40 log (queries on "order flow imbalance" crude, "limit order book" crude queue imbalance, Tian et al.),
   OpenAlex 8 queries (work/A1_crude/A1_crude_oa_2.txt), arXiv API throttled (HTTP 429, A1_crude_arxiv_hits2.txt).
   Sibling worker C2_OFI reports the same gap ("Crude oil (CL) | No OFI or queue-imbalance predictability study
   found"). Evidence on futures broadly (E-mini equity, Treasuries) belongs to other workers.
8. Not found: any study showing that short-horizon patterns are absent or arbitraged away on CL specifically;
   Lalor and Swishchuk (item 1) is the nearest, and it is about adverse fills of a naive strategy.

## Product fact sheets

Common to all three (see family sections): Rule 589 dynamic circuit breakers, 15% (F1, F1b); EIA Wednesday 10:30 ET
and API Tuesday 16:30 ET (F6); no 24/7 crude venue sourced, Globex closed Fri 17:00 to Sun 18:00 ET (F3); COT and
automation shares are for CL only (F4, F5, F5b). Owned 1-minute magnitudes (sigma_1m, R_d, owned ADV, 4-sigma
day counts) are A0's (A0_contract_stats.md has CL and MCL rows; QM has no owned file before 2023-11, per A0 line
191 "QM | rules/products.py:177 | 2025-04-01 | ... | none | no").

### S1. MCL, Micro WTI Crude Oil futures (NYMEX, Chapter 309)

| Field | Value | Source and quote |
|---|---|---|
| Code, name | MCL, Micro WTI Crude Oil Futures | cftc_ptc060721_MCL_launch.txt: "Contract Title Micro WTI Crude Oil Futures ... Commodity Code MCL" |
| Contract size | 100 barrels | nymex_rulebook_ch309_MCL.txt: "The contract quantity shall be 100 U.S. barrels." |
| Tick size, value | $0.01/bbl = $1.00 | launch filing: "Minimum Price Fluctuation $0.01 / Value per Tick $1.00"; cme_MCL_fact_card.txt: "$1 per contract" |
| Settlement | cash, on CL final settlement | Ch. 309: "Final settlement under the contract shall be by cash settlement." |
| Launch | trade date 2021-07-12 | launch filing: "effective on Sunday, July 11, 2021 for trade date Monday, July 12, 2021" |
| Globex in 2023-11..2024-02 | launched 2021-07, continuous listing; liquidity program "Start date is July 12, 2021. End date is ... January 31, 2026" (cftc_nymex_24-499_micro_crude_LPP.txt); volume releases through 2026 (stockwatch_cme_april2026_adv.html.txt). Gate fact: launch before 2023-11 holds. | |
| Match algorithm | FIFO | launch filing: "CME Globex Match Algorithm First-In, First-Out (FIFO)" |
| Hours | Sun-Fri 18:00-17:00 ET, 60-min daily break from 17:00 ET | launch filing (F2 quote); fact card: "CME Globex: Sunday - Friday: 5:00 p.m. to 4:00 p.m. Central Time (CT)" |
| Price limits | Rule 589 dynamic, associated with CL, 15% | F1 |
| Limit-hit days 2019-2024 | unknown (MCL not listed in 2020; no MCL DCB log found) | F1, F1b |
| ADV, published | 2022 YTD (to 2022-12-13) "over 122,000"; 2023 YTD (to 2023-06-28) "over 95,000"; April 2026 "410,000" (+421% vs April 2025); Dec 2025 MCL = 1.8% of Energy ADV of 2.3 million (about 41,000, derived); Dec 2023 MCL = 4.9% of Energy ADV (search summary only, [unverified]) | mondovisione_2022-12-14_MCL_options.html.txt: "2022 ADV year-to-date is up 292% at over 122,000 contracts."; mondovisione_2023-06-29_MCL_50M.html.txt: "Average daily volume (ADV) year-to-date for Micro WTI futures is over 95,000 contracts"; stockwatch_cme_april2026_adv.html.txt: "Micro WTI Crude Oil futures ADV increased 421% to 410,000 contracts"; finviz_cme_2025_annual_adv.html.txt (December 2025 section): "Micro WTI Crude Oil futures accounted for 1.8% of overall Energy ADV", "Energy ADV of 2.3 million contracts" |
| ADV 2022-11..2023-10 | not published as a window; nearest CME figure 2023 YTD to June over 95,000; owned-bar ADV is A0's | as above |
| Open interest | 2022: "Open interest has surpassed 40,000 contracts"; 2023 YTD ADOI "approximately 31,000" | same two releases |
| Retail | no retail volume share published. CME: "27 retail channels" (2021); "Over 86,000 unique market participants from 215 firms ... More than 42,000 of those traders had never previously traded a crude oil contract" (2022); "Over 250 firms and approximately 109,000 unique individual traders" (2023); "one third of all Micro WTI trades occurring during non-U.S. trading hours" (2023); "In 2022, 37% of volume has traded during non-U.S. hours. 46% of Micro WTI futures total volume has originated outside of North America" | hellenic_2021_MCL_50000.html.txt; mondovisione_2022-12-14; mondovisione_2023-06-29 |
| Commercial hedgers (COT) | no separate COT market for MCL in the disaggregated file | F4 |
| Market-maker program | NYMEX Micro Crude Oil Liquidity Provider Program, product scope MCL on Globex, from 2021-07-12, end extended to 2026-01-31; obligations "quote continuous two-sided markets in the Product at designated bid/ask spreads and quote sizes during a specified percentage of time-in-market"; hours "7:00AM - 1:30PM CT ("RTH") and 5:00PM to 7:00AM CT ("ETH")"; spread and size parameters not public in the filing | cftc_nymex_24-499_micro_crude_LPP.txt: "Micro WTI Crude Oil Futures ("MCL") traded on the CME Globex Platform ("Product")." Whether it ran through 2023-11..2024-02: the 24-499 text shows the end date before modification as "January 31, 2025", so it was in force over the pilot window. |
| HFT/automation share | not tabulated (product postdates the CFTC studies) | F5, F5b |
| Spread, depth, queue, volume/min | not found (one WebSearch) | F7 |
| Product-specific releases/week | EIA WPSR 1 (Wed 10:30 ET, main session); API 1 (Tue 16:30 ET, overnight, weak impact) | F6 |
| Weekend gap | same as CL; no crude venue trading while Globex is closed was sourced | F3 |
| Jump frequency | owned-bar counts are A0's; literature: F8 and Ensor et al. (2020, abstract only: "a significant proportion of volatility is explained by news arrival") [abstract only, full text not fetched: Springer returned an HTML page] | work/A1_crude/A1_crude_oaw_1.txt |
| Microstructure research | none on MCL itself; CL studies are its full-size version (F8 items 1-5) | F8 |

### S2. QM, E-mini Crude Oil futures (NYMEX, Chapter 401)

| Field | Value | Source and quote |
|---|---|---|
| Code, name | QM, E-mini Crude Oil Futures | cme_QM_specs_old2019.html.txt (Wayback capture 2019-12-13): "CME Globex: QM"; Ch. 401 title "E-mini Crude Oil Futures" |
| Contract size | 500 barrels | Ch. 401: "The contract quantity shall be 500 U.S. barrels." Original 2002 size was 400 bbl: mondovisione_2002_eminy_specs.html.txt "40 percent of the size of the underlying contracts or 400 barrels of crude oil" (date of the change to 500 not found) |
| Tick size, value | $0.025/bbl = $12.50 (2.5 CL ticks in price) | Ch. 401: "The minimum tradeable price fluctuation shall be $0.025 per barrel."; spec page: "0.025 per barrel = $12.50"; fact card: "$12.50 per contract" |
| Settlement | cash, on CL final settlement | spec page: "Financially Settled" |
| Launch | Globex 2002-06-17 | mondovisione_2002_eminy_begin_june17.html.txt: "e-miNY crude oil and natural gas contracts will begin trading on CME's GLOBEX electronic trading platform on June 17." (dated 30/05/2002); first day: "The trades included 1,404 e-miNY crude oil futures contracts" |
| Globex in 2023-11..2024-02 | listed since 2002 and still in the 2021 CME fact card and the 2025 rulebook copy; continuous listing through the window not directly sourced by a dated volume figure (no QM ADV found). A0: owned QM files start 2025-04-01. | |
| Match algorithm | unknown. Not stated on the 2019 spec page or in Ch. 401; CL outrights are FIFO (Databento) and MCL is FIFO (filing); QM not sourced. Two WebSearches. | |
| Hours | Sun-Fri 18:00-17:00 ET with 60-min break | spec page: "Sunday - Friday 6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m. CT) with a 60-minute break each day beginning at 5:00 p.m. (4:00 p.m. CT)" |
| Price limits | Rule 589 (Ch. 401 401102.D); spec page "Price Limit Or Circuit: Price Limits" (link only) | F1 |
| Limit-hit days 2019-2024 | unknown | F1b |
| ADV, OI | unknown. Searched: 3 WebSearches (QM ADV, QM OI, QM liquidity); CME volume pages blocked/JS. A PVM note on cmegroup.com (cme_pvm_wti_insights_2023-06-20.html.txt) says only: "Similar tendency is observed on the WTI E-mini contract and this trend seems to be reversing lately" and "smaller investors will continue to favour the E-mini and the Micro contracts". | |
| Retail | NYMEX 2002: "The e-miNY crude oil and natural gas futures contracts offer an attractive alternative instrument to complement retail trading portfolios and make it easier for individual investors to participate" (mondovisione_2002_eminy_first_day.html.txt). No share figure. | |
| Commercial hedgers (COT) | no separate COT market | F4 |
| Market-maker program | NYMEX Crude and Refined Futures Market Maker Program (2013), scope "All NYMEX Crude and Refined futures products traded on CME Globex ... with the exception of Light Sweet Crude Oil Futures (CL), New York Harbor ULSD Heating Oil Futures (HO) and RBOB Gasoline Futures (RB)", term "Start date is March 28, 2013. End date is May 31, 2013 February 28, 2015" (cftc_nymex_13-181_crude_refined_MMP.txt). QM would fall in that scope (not named). No program in force in 2023-24 found. | |
| HFT/automation | not tabulated | F5 |
| Spread, depth, queue | not found | F7 |
| Releases, weekend gap | as CL | F6, F3 |
| Microstructure research | Tse and Xiang (2005) on the introduction of the E-mini energy futures, result unknown (title only) | F8 item 6 |

### S3. CL, Light Sweet Crude Oil (WTI) futures (NYMEX, Chapter 200)

| Field | Value | Source and quote |
|---|---|---|
| Code, name | CL, Light Sweet Crude Oil Futures | Ch. 200; fact card "PRODUCT CODE ... CL" |
| Contract size | 1,000 barrels | Ch. 200: "The unit of trading shall be 1,000 U.S. barrels (42,000 U.S. gallons)." |
| Tick size, value | $0.01/bbl = $10 | Ch. 200: "The minimum price fluctuation shall be $0.01 (1 cent) per barrel."; fact card: "$10 per contract" |
| Settlement | physical delivery | fact card: "SETTLEMENT ... Physical" |
| Launch | 1983 (cftc_2020_interim_staff_report_WTI_april20.txt: "since the inception of the WTI Contract in 1983"); Globex: NYMEX board voted 2006-03-05 to list energy futures on CME Globex (mondovisione_2006_nymex_side_by_side.html.txt: "voted today to offer both cash-settled and physically delivered NYMEX Division energy futures contracts for trading on CME Globex") | Exact CL Globex start (2006-09-05 per search summary) [unverified] |
| Globex in 2023-11..2024-02 | yes: on Globex since 2006; A0 lists owned CL files 2010-07-01..2026-06-21 (A0 line 169) | |
| Match algorithm | FIFO (vendor source) | databento_cme_matching_algos.html.txt: "First in, first out (FIFO) ... Popular products: ES, NQ, ZN, ZF, ZB, CL outrights" |
| Hours | "nearly 24 hours, Sunday through Friday", session from 18:00 ET | cftc_2020_interim_staff_report_WTI_april20.txt: "The trading day for WTI Contracts (and many other CME contracts) is nearly 24 hours, Sunday through Friday. The April 20 trading session actually began at 6:00 p.m. Eastern Time"; same schedule as MCL/QM per the fact card's shared hours row |
| Price limits | Rule 589 dynamic, 15% since 2020 (permanent 2020-12-21) | F1 |
| Limit/DCB days 2019-2024 | at least 2020-04-20 (over 30 DCBs in the May 2020 contract); other days unknown | F1b |
| ADV, published | Feb 2022 1.34 million, May 2022 769,000; "monthly ADV now frequently breaks above the 900,000 contracts barrier" (June 2023) | cme_pvm_wti_insights_2023-06-20.html.txt: "Its average daily volume (ADV) plunged from 1.34 million contracts in February 2022 to 769,000 contacts three months later." Latest 12 months: not found. Owned-bar ADV is A0's. |
| Open interest | COT futures-only mean 1,708,817, median 1,752,072 (53 reports, 2022-11-01..2023-10-31) | F4 |
| Commercial share (COT) | producer/merchant 26.7%, swap dealers 18.3%, managed money 33.2%, other reportables about 17.6% (by difference), nonreportable 4.2% of OI | F4, F4b |
| Retail/small | nonreportable 4.2% of OI; small volume traders (below 0.5% of daily volume, not "retail") 46.0% of volume in 2014-16 | F4, F5b |
| Market-maker program | none found for CL; the 2013 crude MMP excluded CL | cftc_nymex_13-181_crude_refined_MMP.txt (quote in S2) |
| Professional liquidity | EMMs: 52 accounts, about 50% of volume (2006-2011); automated at least one side 82.6% of volume (2014-16); ATS-ATS 38.1% | F5, F5b |
| Spread | majority of volume at a 1-tick spread; spreads reopen to 2 ticks and return to 1 quickly (2012-13); wider around 8:30, 10:00, 10:30 | F7 |
| Depth at best | median 7, mean 8.8 contracts (2012-13, random timestamps); 4-12 contracts (1-min average, April 2020) | F7 |
| Trade size | median 1, mean 1.70 contracts (2024-04-09) | F7 |
| Volume per minute, QV | not sourced (A0 owns volume) | F7 |
| Releases | EIA 1/week (main session), API 1/week (overnight) | F6 |
| Weekend gap | none sourced | F3 |
| Microstructure research | F8 items 1-5 (same product): naive passive posting mostly adversely filled; depth explains spread moves; pre-EIA order imbalance; LOB slope predicts next-day volatility; no OFI or queue-imbalance study found | F8 |

## Unknowns and gaps (for the scorer and the lead)

- QM: match algorithm, ADV, open interest, spread, depth, any limit day, any program after 2015: all unknown.
  QM's continuous listing through 2023-11..2024-02 is inferred from listing since 2002 and later documents, not
  from a dated volume figure; the lead may want it confirmed from a source this worker may not read (for example
  the Databento definition schema).
- MCL: spread, depth, queue, volume per minute, retail volume share, COT split, HFT share: unknown. MCL ADV for
  the standard window is not published (A0 owns the owned-bar figure).
- CL: session-split median spread, volume per minute, QV, latest 12-month published ADV, limit-day count per
  year 2019-2024 (only 2020-04-20 sourced): unknown.
- No OFI, queue-imbalance or trade-sign predictability study on any of the three was found; no study showing
  such patterns are absent either.
- Blocks met: cmegroup.com refuses this IP (WebFetch also timed out); Wayback was throttled for a period (HTTP 429
  and refused connections) and later worked; arXiv API returned HTTP 429; AgEcon (AWS WAF) and HAL returned
  challenge pages; api.org page 404; Schwab 403; Lakehead thesis 404; Springer returned an HTML page. All logged
  in pages/A1_crude/log.tsv. These are gaps, not findings.
- Budget: WebSearch 30 of 40 used (10 before the usage cut, 20 after). Firecrawl had no credits at 03:01 PDT and
  was not retried.

Finished 2026-10-21 05:30 PDT. JSON: reports/stage_e28_briefs/A1_crude.json (MCL, QM, CL; every field a
{value, unit, window, source_file, quote, note} object; quotes machine-checked against the saved files: 57 checked,
0 missing; JSON built by work/A1_crude/A1_crude_json.py).
