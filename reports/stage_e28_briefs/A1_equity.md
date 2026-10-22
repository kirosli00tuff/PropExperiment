# A1_equity: Layer 1 fact sheets, equity index family (M2K, RTY, MYM, YM, MNQ baseline, NQ)

Worker: A1_equity (Opus 5.5), Stage E.28 Part A, started 2026-10-21 05:18 PDT. Facts only; no scoring.
All source files are under reports/stage_e28_briefs/pages/A1_equity/ (log: log.tsv there, with URL, UTC and PDT
fetch times, method and sha256). Quotes are verbatim from the saved files (PDFs through `pdftotext -layout`, HTML
through a tag stripper, files `*.html.txt`). In quotes, curly quotes, en dashes and Unicode hyphens of the
source are written as ASCII quotes and hyphens; pipes in table quotes mark table-cell breaks. No market data was read. Owned-bar magnitudes (sigma_1m, R_d, owned
ADV) belong to A0 and are not computed here. Machine-readable twin: A1_equity.json.

Status notes (write-time): cmegroup.com is not fetched directly (known IP block). Wayback's availability and CDX
APIs answered HTTP 429 (Too Many Requests) at about 05:20 PDT, so Wayback was paused and CFTC copies of CME
submissions (cftc.gov) were used first.

## F. Family-wide facts (referenced from each sheet as F1..Fn)

### F1. Contract terms of the micros (MNQ, M2K, MYM): CME Submission No. 19-140, 2019-04-12

File: cftc_ptc041519_micro_emini_launch.txt (CME/CBOT Regulation 40.2(a) certification, filed 04/12/19).

- Filing description: "Initial Listing of Micro E-mini Standard and Poor's 500 Stock Price Index Futures, Micro
  E-mini Nasdaq-100 Index Futures, Micro E-mini Russell 2000 Index Futures and Micro E-mini Dow Jones Industrial
  Average Index Futures Contracts".
- Tick: "Micro E-mini Nasdaq-100 Index Futures: 0.25 Index points, equal to $0.50 per contract"; "Micro E-mini
  Russell 2000 Index Futures: 0.10 Index points, equal to $0.50 per contract"; "Micro E-mini Dow Jones Industrial
  Average Index Futures: 1.00 Index points, equal to $0.50 per contract".
- Matching algorithm (all four micros): "CME Globex Matching Algorithm ... F: First In, First Out (FIFO)" (table
  row "CME Globex / Matching / Algorithm | F: First In, First Out (FIFO)").
- Hours at launch: "CME Globex: Sunday - Friday 6:00 pm - 5:00 pm Eastern Time (ET) with trading halt 4:15 pm -
  4:30 pm ET" (the halt was later removed: F3).
- Price limits at launch: "5:00 pm to 8:30 am 5% above Fixing Price to 5% below Fixing Price"; "8:30 am to 3:00
  pm Sequential circuit breaker limits at 7%, 13%, and 20% below Fixing Price"; the Fixing Price is "equal to
  volume weighted average price calculated on basis of futures trading activity between 2:59:30 pm and 3:00:00
  pm" (times CT). Superseded overnight by F2.
- Rule 589 association: "Micro E-mini NASDAQ-100 Index Futures ... MNQ Associated NQ"; "Micro E-mini Russell 2000
  ... M2K Associated RTY"; "Micro E-mini Dow Index Futures ... MYM Associated YM". So a limit or halt in the
  primary (NQ, RTY, YM) applies to the micro.
- Exchange fees in the filing: "Individual Members CME Globex $0.04" up to non-member rates (e.g. "CME Globex -
  Outrights $0.19" in the last row seen). Fees to the trader at a prop firm are Layer 2 facts, not used here.
- Launch date: CME Special Executive Report SER-8360 (search snippet only, not fetched: [unverified]) said listing
  "effective Sunday, May 5, 2019, for trade date Monday, May 6, 2019". The Micro E-mini Futures Market Maker
  Program filing (F5) independently gives "Start date is May 6, 2019" and "The proposed Program will become
  effective on May 6, 2019", consistent with a 2019-05-06 first trade date.
- Exchange of listing: MNQ and M2K on CME; MYM on CBOT (filing cover: "Micro E-mini Dow Jones Industrial Average
  Index Futures contract certified herein appear in Appendix D" under the CBOT rulebook; Rule 589 table chapter 27
  is a CBOT chapter).

### F2. Price limits since 2020-10-12 (all six candidates): CME Submission, filed 2020-09-25

File: cftc_ptc093020_rule589_equity_7pct.txt.

- "The Exchanges will amend the Overnight Trading Hours ("OTH") price limits for certain CME and CBOT equity index
  futures and options on futures from the current ±5% hard limits to ±7% hard limits. During OTH, these contracts
  will also be subject to dynamic price fluctuation limits, pursuant to CME and CBOT Rule 589.D. ("Dynamic Price
  Fluctuation Limits") with a ±3.5% dynamically calculated variant, provided that the ±7% hard limit is not
  exceeded." Effective "Sunday, October 11, 2020 for trade date Monday, October 12, 2020."
- Regular hours: "during Regular Trading Hours ("RTH"), CME and CBOT equity index futures and options on futures
  contracts are coordinated with the Primary Listing Exchange price limits. At such time as a Regulatory Halt is
  declared in response to a Level 1 (7%) or a Level 2 (13%) Market Decline, trading is halted." After the change,
  futures "resume trading 10 minutes after a Regulatory Halt commences on the Primary Listing Exchange."
- Table rows (Exhibit A): "E-mini NASDAQ 100 Futures 359 NQ Primary Primary Daily Price Limit Table 3.5% of
  Dynamically Calculated Reference Price"; "E-mini Russell 2000 Index Futures 393 RTY Primary ... 3.5% of
  Dynamically Calculated Reference Price"; "CBOT E-mini Dow Jones Industrial Average Index Futures ($5 Multiplier)
  27 YM Primary ... 3.5% of Dynamically Calculated Reference Price"; "Micro E-mini NASDAQ-100 Index Futures 361 MNQ
  Associated NQ"; "Micro E-mini Russell 2000 Index Futures 363 M2K Associated RTY"; "Micro E-mini Dow Index Futures
  28 MYM Associated YM". (Rulebook chapters: NQ 359, MNQ 361, RTY 393, M2K 363, YM 27, MYM 28; the 2019 launch
  filing had listed the micros under the mini's chapter, F1.)
- Limit-hit days 2019-2024: see F8.

### F3. Trading hours (all six)

- Before 2021-06-28: old CME spec pages (Wayback snapshots 2020-12 to 2021-01, files cme_old_specs_*.html.txt)
  all read "CME Globex: Sunday - Friday 6:00 p.m. - 5:00 p.m. ET with trading halt 4:15 p.m. - 4:30 p.m." (NQ, RTY,
  YM add BTIC and TACO venues; micros do not).
- Halt removed: cftc_rule061421_equity_halt_removal.txt (CME Submission No. 20-244, filed 2021-06-11): "CME and
  CBOT will eliminate the 3:15 p.m. - 3:30 p.m. Central Time (CT) trading halt on CME Globex which currently exists
  for certain Equity futures and options contracts. The halt was initially implemented to account for transactions
  conducted via open outcry in the trading pits and is therefore no longer necessary." Effective "Sunday, June 27,
  2021 for trade date Monday, June 28, 2021." Exhibit A lists "Micro E-mini Russell 2000 Index Futures 363 M2K",
  "Micro E-mini Nasdaq 100 Index Futures 361 MNQ", "E-mini NASDAQ 100 Index Futures 359 NQ", "E-mini® Russell 2000®
  Index Futures 393 RTY", "Micro E-mini Dow Jones Industrial Average Index Futures 28 MYM", "CBOT E-mini Dow Jones
  Industrial Average Index Futures ($5 Multiplier) 27 YM".
- So, for the pilot window (2023-11..2024-02), the schedule implied by the sources is Sunday-Friday 18:00-17:00 ET
  with the daily 17:00-18:00 ET break and no 16:15-16:30 halt. A current CME spec page stating this directly was
  not fetched [the current-hours sentence is an inference from the two filings, not a quote].
- Relation to cash-equity hours: the cash market (NYSE/Nasdaq) runs 09:30-16:00 ET, the spec's main session for
  this stage (06:30-13:00 PT). Futures trade about 23 hours a day; RTH price limits are coordinated with the
  primary listing exchange (F2 quote), overnight hard limits of ±7% apply otherwise.

### F4. Weekend-gap exposure

- Globex is closed from Friday 17:00 ET to Sunday 18:00 ET (F3). The underlying indexes (Nasdaq-100, Russell 2000,
  DJIA) are computed from US cash-equity prices, which do not trade on weekends. No sourced fact was found of any
  underlying for these indexes trading while Globex is closed. [The statement that US cash equities do not trade on
  weekends is general knowledge, not quoted from a fetched page.]

### F5. Market-maker and incentive programs (CFTC copies of CME notifications)

- Micro E-mini Futures Market Maker Program (MNQ, M2K, MYM, and MES): cftc_rule041619_micro_emini_mm_program.txt
  (CME Submission No. 19-161, 2019-04-16): "Micro E-mini Standard and Poor's 500 Stock Price Index Futures ("MES"),
  Micro E-mini Nasdaq-100 Index Futures ("MNQ"), Micro E-mini Russell 2000 Index Futures ("M2K"), and Micro E-mini
  Dow Jones Industrial Average Index Futures ("MYM") that are traded on the CME Globex Platform ("Products")." "The
  Exchanges may designate up to thirty (30) participants in the Program." "Start date is May 6, 2019. End date is
  October 31, 2019." "Hours 8:00AM - 3:15PM CT and 5:00PM - 8:00AM CT." "participants must quote two-sided markets
  in the Products at predetermined average bid/ask spreads and minimum quote sizes during a specified percentage of
  time-in-market." Purpose: "The resulting increase in liquidity on the central limit order book benefits all
  participant segments in the market."
- Modification, cftc_rule041620_micro_emini_mm_mod.txt (CME Submission No. 20-196, 2020-04-16, effective
  2020-05-01): text reads "The Exchanges may designate up to twenty (20) ten (10) participants" and "End date is
  April 30, 2020 January 31, 2021." The filing says "Modifications appear below, with additions underlined and
  deletions overstruck"; the text extraction loses the underline/overstrike, so which number is the new one is not
  determinable from the text (most likely the program was extended to 2021-01-31). Whether the program ran in
  2022-2024 was NOT found (no later futures-program filing was fetched; one WebSearch, call 6, found only Micro
  E-mini OPTIONS market-maker filings for 2021-2024, which are not futures programs: cftc_rule081821_cme005.txt
  "Modifications to the Micro E-mini Options Market Maker Program", cftc_rule021621_cme001.txt, cftc_rule041322_
  cme015.txt, cftc_rules01022410273.txt).
- E-mini Russell 2000 Futures Market Maker Program (RTY): cftc_rule053017_RTY_mm_program.txt (filed 2017-05-30,
  effective 2017-07-10): "E-mini Russell 2000 Index Futures ("RTY") ..." in Product Scope; "CME may designate up to
  fifteen (15) participants in the Program."; "Start date is July 10, 2017. End date is December 31, 2017 March 31,
  2018." (same overstrike caveat); "Participants must quote continuous two-sided markets in the Products at maximum
  bid/ask spreads and minimum quote sizes." Status after 2018: not found.
- E-mini equity index futures program (NQ, YM): a CME/CBOT supplemental filing 14-084S on the "E-mini Equity Index
  Futures Market Maker Program" appeared in WebSearch call 6 (snippet only, incentive details confidential); not
  fetched: [unverified]. Programs specific to NQ or YM in 2022-2024: not found.

### F6. Automated (ATS) trading shares, CFTC Office of the Chief Economist

Files: cftc_haynes_roberts_2015.txt (Haynes and Roberts, "Automated Trading in Futures Markets", CFTC OCE, 2015;
sample "CME transaction data, November 12, 2012 - October 31, 2014"), cftc_haynes_roberts_2017_update.txt (second
period Nov 2014-Oct 2016), cftc_ats_update2_2019.txt (third period "November 1, 2016 - October 31, 2018").
These cover NQ ("E-mini NASDAQ 100") and YM ("E-mini Dow ($5)") but not RTY (on ICE until July 2017) or any micro
(launched May 2019). No CFTC table for any of the micros or RTY was found.

- 2015, Table 4 (volume mm; ATS-ATS %; ATS-MAN %; MAN-MAN %): "E-mini NASDAQ 100 131 58.2 34.8 6.9"; "E-mini Dow
  ($5) 73 60.9 33.6 5.4"; for comparison "E-mini S&P 500 866 43.4 42.6 13.8".
- 2015, Table 6 (small vs large volume traders; large = "at least 0.5 percent to total daily volume across all
  expirations"): "E-mini NASDAQ 100 52,793 17.4 20.0 544 58.2 4.3" (small traders: N accounts, ATS %, MAN %; large
  traders: N, ATS %, MAN %), i.e. small traders 37.4% of NQ volume, large 62.5%.
- 2019 update, Table 3 (Nov 2014-Oct 2016 vs Nov 2016-Oct 2018; volume; ATS; MAN; ATS-ATS; ATS-MAN; MAN-MAN): "E-mini
  NASDAQ 100 134 176 77.1 74.0 22.2 25.4 60.1 54.4 33.9 39.1 5.2 5.8"; "E-mini Dow ($5) 82 88 80.2 81.2 19.7 18.7
  64.6 66.1 31.1 30.1 4.1 3.6". Text: "We find only one product with a decrease in automated trading - the E-mini
  NASDAQ 100 futures contract."
- 2019 update, Table 5 (small vs large, latest period): "E-mini NASDAQ 100 59,030 58,910 16.8 17.5 17.2 19.5 446
  410 60.3 56.5 5.0 5.8" (small-trader ATS 17.5% and MAN 19.5% of volume in 2016-2018).
- 2017 update, passive resting-time table (Table 6, "Time Between Order Placement and Execution for Liquidity
  Providers", share of two-sided volume, first/second period): "E-mini NASDAQ 100 8.9 11.3 0.8 0.9 5.5 6.7 0.6 0.6
  3.5 3.8 0.5 0.5 11.8 10.8 2.9 2.8 5.0 4.0 2.4 2.1 8.0 6.2" (column pairs ATS/MAN for 0-100 ms, 100-500 ms, 500
  ms-1 s, 1-10 s, 10 s-1 min, then remaining). The paper defines "automated" by the CME manual order indicator, not
  as HFT; no HFT share by contract was found.

### F7. CFTC Traders in Financial Futures (futures only), window 2022-11-01..2023-10-31

Files: cftc_fut_fin_txt_2022.zip and cftc_fut_fin_txt_2023.zip (unzipped to cot22/, cot23/ FinFutYY.txt);
script work/A1_equity/A1_equity_cot.py; output work/A1_equity/A1_equity_cot_out.txt. Rows dated 2023-11-01 or
later were dropped in the script before any value was used. Share = (long + short + 2 x spread) / (2 x open
interest), averaged over weekly reports; the five shares sum to 1. TFF has no "commercial hedger" category; its
categories are Dealer/Intermediary, Asset Manager/Institutional, Leveraged Funds, Other Reportables and
Nonreportable (small traders below reporting levels).

| CFTC code | Market name (verbatim) | reports | mean OI | Dealer | Asset Mgr | Lev Money | Other Rept | NonRept | mean traders |
|---|---|---|---|---|---|---|---|---|---|
| 209742 | NASDAQ MINI - CHICAGO MERCANTILE EXCHANGE (NQ) | 53 | 263,220 | 0.215 | 0.269 | 0.289 | 0.071 | 0.157 | 291 |
| 209747 | MICRO E-MINI NASDAQ-100 INDEX - CHICAGO MERCANTILE EXCHANGE (MNQ) | 53 | 113,447 | 0.051 | 0.019 | 0.452 | 0.041 | 0.438 | 42 |
| 239742 | RUSSELL E-MINI - CHICAGO MERCANTILE EXCHANGE (RTY) | 53 | 494,756 | 0.207 | 0.450 | 0.232 | 0.063 | 0.049 | 337 |
| 239747 | MICRO E-MINI RUSSELL 2000 INDX - CHICAGO MERCANTILE EXCHANGE (M2K) | 6 | 24,229 | 0.054 | 0.022 | 0.441 | 0.043 | 0.439 | 21 |
| 124603 | DJIA x $5 - CHICAGO BOARD OF TRADE (YM) | 53 | 91,745 | 0.311 | 0.155 | 0.244 | 0.130 | 0.160 | 93 |
| 124608 | MICRO E-MINI DJIA (x$0.5) - CHICAGO BOARD OF TRADE (MYM) | 20 | 29,312 | 0.027 | 0.015 | 0.418 | 0.065 | 0.475 | 21 |

- M2K appears in only 6 of 53 weekly reports and MYM in 20 (first 2022-11-22, last 2023-08-01), so their means are
  over published weeks only. [Reason for the gaps not sourced; CFTC publishes a market only when enough traders hold
  reportable positions, which is general knowledge, not quoted here.]
- Mapping of CFTC names to Globex codes is by product name (NASDAQ MINI = E-mini Nasdaq-100; RUSSELL E-MINI =
  E-mini Russell 2000; DJIA x $5 = E-mini Dow) and is this worker's reading.
- These are shares of open interest (positions), not of traded volume.

### F8. Price-limit and circuit-breaker hits, 2019-2024

- Regular-hours halts (apply to all six; F2 says CME equity index futures halt with the primary listing exchange
  on a Level 1 or Level 2 decline): fr_2021-22941_mwcb.txt (SEC Release No. 34-93364, Federal Register document
  2021-22941): "In the Spring of 2020, at the outset of the worldwide COVID-19 pandemic, U.S. equities markets
  experienced four MWCB Level 1 halts, on March 9, 12, 16, and 18, 2020. In each instance, the markets halted as
  intended upon a 7% drop in the S&P 500 Index, and resumed as intended 15 minutes later." Same file: "The
  Taskforce also asked CME to consider modifying its rules to enter into a limit-down state in the futures
  pre-market after a 7% decline instead of 5%." (CME did so from 2020-10-12, F2.)
- Overnight limit hits (5% hard limit then in force): NOT verified from a primary source. WebSearch calls 4 and
  19 returned only news and broker pages, used as pointers and not as evidence: a Bloomberg headline dated
  2020-03-12 ("S&P 500 Futures for June Hit Limit Down Again amid Global Rout", snippet: "for the third time this
  week"), forexlive pages dated 2020-03-15 and 2020-03-22 ("US equity index futures trading on Globex have hit
  limit down"), and a Bloomberg page dated 2020-03-17 (snippet: contracts "on the S&P 500, Nasdaq 100 and Dow
  Jones Industrial Average all at some point reached the so-called limit down level"). [unverified, snippets
  only]. A CME FAQ snapshot on equity price limits (cme_faq_equity_price_limits.html, Wayback 2020-10-14) held no
  page text (Wayback banner only).
- Count, sourced: at least 4 trade dates with a regular-hours circuit-breaker halt in 2019-2024, all in March
  2020 (S&P 500 trigger, common to the family). Overnight hits in March 2020 add an unknown number of further days
  (pointers suggest at least 3-4). No sourced hit in 2019, 2021, 2022, 2023 or 2024 was found; that is absence of
  evidence within the budget, not a sourced zero. Per-product (NQ vs RTY vs YM) overnight hit dates: unknown.

### F9. Information events, cash-equity link and the ES/MES book

- Product-specific scheduled releases (the kind C4 counts, like EIA or USDA): none found for equity index futures
  in any fetched source. The US macro calendar (CPI, payrolls, FOMC) is shared and excluded by the spec. Constituent
  earnings (quarterly) and index reconstitutions (Russell annual, Nasdaq-100 annual) are product-relevant but not
  weekly; no source was fetched for their dates [unverified].
- Cash-equity hours: the main session (06:30-13:00 PT = 09:30-16:00 ET) is the cash session; futures trade about
  23 hours (F3). Share of micro volume outside US hours: cme_pr_20230317_micro_2bn.html.txt (CME press release
  2023-03-17): "20% of volume occurs outside of U.S. trading hours" (all four Micro E-mini equity index futures,
  "2.73 million contracts in average daily volume in 2023-to-date"); cme_om_2024_micro_five_years_v2.html.txt
  (CME OpenMarkets 2024): "international participation has been strong with 24% of volume now occurring outside of
  U.S. trading hours." Not split by product.
- Micro-mini linkage: the micros are "Associated" with the minis for price limits (F1, F2); CME Rule 855 allows
  offsetting different-sized positions at "10" micro per mini (launch filing Appendix H: "MNQ/MNQ ... 361 10 NQ/NQ
  ... 359"; "M2K/M2K ... 363 10 RTY/RTY ... 393"). Price discovery: Fassas (2021), The Journal of Derivatives,
  doi 10.3905/jod.2021.1.131 (crossref_fassas2021_jod.json; abstract from icbe_fassas_micro_emini.html.txt):
  "Using intraday data during a three-month period, we find that the new smaller-sized stock index futures
  contracts function surprisingly well in their price discovery performance at their infancy stage, as they
  contribute approximately equal amounts to the information transmission process with the established E-Mini
  index futures." [abstract only; full text not read].
- Relation to ES/MES: all six track US large- or small-cap indexes that co-move with the S&P 500; the same
  MWCB trigger (S&P 500 7%/13%/20%) halts all of them (F8). No source was fetched for intraday correlation or
  lead-lag between NQ/RTY/YM and ES. [A0 holds owned-bar magnitudes; correlations were not requested of A0.]

### F10. Spread, depth, queue size and volume per minute

- No public source with a median bid-ask spread in ticks, depth at the best level, touch queue size or traded
  volume per minute for NQ, MNQ, RTY, M2K, YM or MYM was found. Searched: WebSearch calls 13 and 14 (CME liquidity
  tool, liquidity reports); fetched cme_RTY_liquidity_report.html (Wayback 2024-03-03), which says only "This
  report highlights activity in E-mini Russell 2000 futures, including historical CME Globex and Block volume, ADV
  and open interest, and bid/ask spread." with the data in an interactive chart that the snapshot does not hold;
  cme_alternative_liquidity_measures.html covers ES only ("E-mini S&P 500 futures traded approximately 65% more
  volume despite the orderbook depth decreasing by 75% (vs. Sep 2018)"). The CME Liquidity Tool needs a login
  (search snippet, not fetched).
- Tick-size evidence for NQ: Kurov (2008), Journal of Futures Markets 28:871-888, doi 10.1002/fut.20341
  (crossref_kurov2008_fut20341.json, abstract): "On April 2, 2006, the Chicago Mercantile Exchange reduced the
  minimum tick size of the floor-traded and E-mini Nasdaq-100 futures from 0.5 to 0.25 index points ... The
  results show a significant reduction in the effective spreads in both of the contract markets but especially in
  the electronically traded E-mini futures." [abstract only].
- Passive resting times for NQ, CFTC 2017 (F6): share of NQ two-sided volume whose passive side rested 10 s-1 min
  "5.0 4.0" (ATS) and "2.4 2.1" (MAN), and 0-100 ms "8.9 11.3" (ATS), first/second period.
- Volume per minute from owned bars: A0 (A0_contract_stats.md, field vol_per_min_main_median) has NQ, RTY, YM
  for the standard window; the micros have no owned bars before 2025-04-01 (A0_contract_stats.md line 62: "MNQ,
  the baseline, has no owned bars before 2025-04-01 ... The same holds for M2K, MYM").

### F11. Published microstructure evidence (relation to each candidate, and result)

Relation codes: SAME (the product itself), MMF (its micro, mini or full version on the same underlying), COUSIN
(another CME Globex equity index future, e.g. ES), CLASS (futures or the asset class only). Result: positive
(short-horizon predictability from order-book variables, or profitable passive provision net of costs), null, or
negative (patterns absent, or passive provision loses).

| # | Study | Product | Relation to NQ / MNQ | to RTY / M2K, YM / MYM | Result | Evidence status |
|---|---|---|---|---|---|---|
| R1 | Rodas (2026), "The Touch Carries No Direction: A Pre-Registered Null on Order-Flow Imbalance and Queue Depletion in Index Futures", SSRN 10.2139/ssrn.7330219 | NQ, 20 RTH sessions | NQ: SAME; MNQ: MMF | COUSIN | negative/null | abstract only (crossref_rodas2026_ssrn7330219.json); SSRN preprint, not peer-reviewed |
| R2 | Lalor and Swishchuk (2024, v3), "Market Simulation under Adverse Selection", arXiv 2409.12721 | ES, NQ, CL, ZN | NQ: SAME; MNQ: MMF | COUSIN | negative for naive passive posting (adverse fills dominate) | full text (arxiv_2409.12721v3_lalor_swishchuk.txt) |
| R3 | Dixon (2017), "Sequence Classification of the Limit Order Book using Recurrent Neural Networks", arXiv 1707.05642; and Dixon (2017) arXiv 1710.03870 | ES (ESU6), Aug 2016 | COUSIN | COUSIN | positive (price-flip classification), no realistic net test | full text in C2_DeepLOB's folder (pages/C2_DeepLOB/dixon_rnn_seq2017.txt) |
| R4 | Baron, Brogaard and Kirilenko (2014 draft), "Risk and Return in High Frequency Trading", CFTC OCE | ES | COUSIN | COUSIN | negative for slow passive traders (revenue to fast liquidity takers) | full text in C2_Control's folder (pages/C2_Control/baron_brogaard_kirilenko_2014_cftc.txt) |
| R5 | Takahashi (2025, v4), "Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomic News Effects", arXiv 2508.06788 | ES | COUSIN | COUSIN | OFI price impact at 1 s, shocks dissipate within 1 s (contemporaneous impact, not a tradable forecast) | abstract only (arxiv_api_abstracts_batch1.xml) |
| R6 | Fassas (2021), J. Derivatives, "Price Discovery in a New Futures Market: Micro E-Mini Index Futures" | MES, MNQ, M2K, MYM vs minis | MNQ: SAME; NQ: MMF | M2K, MYM: SAME; RTY, YM: MMF | not a predictability test (price-discovery shares) | abstract only |
| R7 | Kurov (2008), JFM, tick size and NQ | NQ, 2006 | NQ: SAME; MNQ: MMF | COUSIN | not a predictability test (spreads fell after tick cut) | abstract only |
| R8 | Mesfin (2026), arXiv 2605.04004, 2605.17724 (and 2605.11423) | MNQ 5-minute OHLCV bars 2021-2025 | MNQ: SAME; NQ: MMF | COUSIN | null for bar-based signals (not order-book variables) | abstract only; arXiv preprints, single author |

Verbatim quotes:

- R1 (crossref_rodas2026_ssrn7330219.json, abstract): "Two order-book features widely believed to carry
  short-horizon directional informationaggressor imbalance at the touch (OFI) and trade-driven queue depletion
  (DEPL)-are tested against a symmetric ±3-tick first-passage barrier on 45,700 races drawn from 20 regular-hours
  sessions of NQ index futures." "Neither feature departs measurably from the unconditional base rate: OFI resolves
  up-first in 49.91% of races and DEPL in 50.20%, against an unconditional 49.71% and a breakeven requirement of
  63.00% at the measured passive cost line." "at free execution the required rate is 50.00 percent and the better
  arm's interval of [49.74, 50.66] contains it". (The text "informationaggressor" is as in the Crossref record.)
- R2 (arxiv_2409.12721v3_lalor_swishchuk.txt): "We specifically focus on a stochastic optimal control
  market-making problem and test the strategy on ES (E-mini S&P 500), NQ (E-mini Nasdaq 100), CL (Crude Oil) and
  ZN (10-Year Treasury Note)" (abstract, arxiv_api_abstracts_batch1.xml). Table 2: "2024/04/25 NQ Jun24 1929 1269
  660" (total LO fills, adverse, non-adverse; 1-lot static quotes "16 ticks for NQ" apart, "over active trading
  trading hours (8:30 EST - 16:00 EST)"). Table 1: "NQ 1.54 1" (mean and median trade size). Conclusion:
  "excluding adverse fills and realistic non-adverse fill probabilities substantially inflates trading
  performance." "This is just as evident in ES, NQ and ZN". Also: "NQ exhibits substantially more frequent price
  changes than ES, CL, and especially ZN". Data: "We use futures LOB data sourced from Futures First Inc." (up to
  five levels).
- R3 (pages/C2_DeepLOB/dixon_rnn_seq2017.txt, abstract): "a short sequence of observations of limit order book
  depths and market orders is used to predict a next event price-flip. The capability to adjust quotes according
  to this prediction reduces the likelihood of adverse price selection." "using S&P500 E-mini futures level II data
  over the month of August 2016." C2_DeepLOB.md records the execution paper's outperformance only "With perfect
  information, and 0ms latency".
- R4 (pages/C2_Control/baron_brogaard_kirilenko_2014_cftc.txt): "This paper studies high frequency trading (HFT)
  in the E-mini S&P 500 futures contract over a two-year period and finds that revenue is concentrated among a
  small number of HFT firms who achieve greater investment performance through liquidity-taking activity and
  higher speed." "Small traders experience a much larger loss of -$3.49 (Column 2, Row 7)" (when trading with
  aggressive HFTs).
- R5 (arxiv_api_abstracts_batch1.xml): "Pooling across days, both price and flow impacts are significant at the
  one-second horizon ... Impulse responses indicate that shocks dissipate almost entirely within a second."
- R8 (arxiv_api_abstracts_batch1.xml, 2605.04004): "Fourteen signal families were evaluated on 947 trading days of
  five-minute data from 2021-2025 ... None passed all five." 2605.17724: "No configuration produces statistically
  significant out-of-sample accuracy above the 51.8% base rate."
- Searched and not found: any study on RTY, M2K, YM or MYM order books (Crossref queries in work/A1_equity/
  A1_equity_crossref.txt, arXiv queries in work/A1_equity/A1_equity_arxiv.txt, WebSearch calls 15, 16). Futures
  studies on other index futures (BankNifty, arXiv 2507.22712; CSI 300, arXiv 2505.17388) are CLASS only and not
  on CME Globex.

### F12. Published ADV and open interest (CME monthly Equity Index Product Review, and CME releases)

Files: cme_eqreview_2022-11.html.txt (YTD "Through November 30, 2022"), cme_eqreview_2022-12.html.txt (YTD
"Through December 31, 2022"), cme_eqreview_2023-10.html.txt (YTD "*Through October 31, 2023"); Wayback copies
of www.cmegroup.com/newsletters/monthly-equity-index-review/. Columns are "Oct ADV | YTD ADV* | Open Interest"
(month ADV, year-to-date ADV, open interest), rows "E-mini|NQ|...", "Micro E-mini|MNQ|...", etc. The newsletter
series on Wayback ends at 2023-11 (CDX listing, work/A1_equity/A1_equity_cdx_eqreview.txt); 2023-11 was not read
(pilot window).

| Code | Nov-2022 ADV | Dec-2022 ADV | 2022 full-year ADV | Oct-2023 ADV | Jan-Oct 2023 ADV | OI end Nov-22 / Dec-22 / Oct-23 | Derived 2022-11..2023-10 ADV (see note) |
|---|---|---|---|---|---|---|---|
| NQ | 624,366 | 657,682 | 699,898 | 762,475 | 671,995 | 256,803 / 241,785 / 259,306 | 666,813 |
| MNQ | 1,241,292 | 1,096,418 | 1,453,985 | 1,420,645 | 1,114,224 | 121,214 / 66,138 / 110,189 | 1,123,365 |
| RTY | 190,254 | 236,193 | 237,489 | 231,303 | 218,224 | 483,060 / 445,567 / 559,075 | 217,387 |
| M2K | 106,682 | 82,745 | 130,807 | 78,372 | 76,712 | 24,794 / 14,471 / 23,021 | 79,724 |
| YM | 200,321 | 182,876 | 202,211 | 208,407 | 175,187 | 79,187 / 76,110 / 103,936 | 177,933 |
| MYM | 153,494 | 138,518 | 179,017 | 115,096 | 108,504 | listed 121,214 / 66,138 / 110,189 (copy error, see below); implied 37,630 / 20,722 / 25,224 | 114,779 |

- Verbatim rows (2023-10): "E-mini|NQ|NQA Index|762,475|671,995|259,306", "Micro E-mini|MNQ|HWB Index|1,420,645|
  1,114,224|110,189", "E-mini|RTY|RTYA Index|231,303|218,224|559,075", "Micro E-mini|M2K|HWR Index|78,372|76,712|
  23,021", "E-mini|YM|DMA Index|208,407|175,187|103,936", "Micro E-mini|MYM|HWI Index|115,096|108,504|110,189"
  (pipes mark cell breaks in the stripped table).
- MYM open interest: in all three issues the MYM OI cell equals the MNQ OI cell (110,189 / 121,214 / 66,138), which
  looks like a copy error in CME's table. The Dow Jones "Futures" subtotal minus YM gives the implied MYM OI:
  2023-10 "Futures|324,919|285,133|129,160" minus 103,936 = 25,224 (BTIC carries no OI, "-"). The ADV subtotal checks
  (208,407 + 115,096 + 1,416 = 324,919), so the ADV cells are consistent. Implied values are this worker's
  arithmetic.
- Russell 2000, 2023-10: the "Futures" OI subtotal 605,940 does not equal RTY 559,075 + M2K 23,021 = 582,096
  (difference 23,844); the Nov-22 and Dec-22 subtotals do add up. One of the 2023-10 OI cells is inconsistent;
  which one is unknown.
- Derived window ADV (last column) = (Nov-22 ADV x 21 + Dec-22 ADV x 21 + Jan-Oct-23 ADV x 209) / 251, with 21,
  21 and 209 CME trade dates ASSUMED (weekdays less US exchange holidays), not sourced. It is an approximation for
  the spec's standard window; A0's owned ADV is the spec's primary ADV for NQ, RTY, YM (A0_contract_stats.md row
  "NQ | yes | ... | 618,345"), and A0 has none for the micros.
- Latest published (product level, only MNQ and RTY found): cme_pr_20260105_annual2025.html.txt: "Record annual
  Micro E-mini Nasdaq-100 futures ADV of 1.6 million contracts" (full-year 2025); Q4 2025: "Micro E-mini Nasdaq 100
  futures ADV increased 41% to 1.8 million contracts", "E-Mini Russell 2000 futures ADV increased 20% to 218,000
  contracts". cme_pr_20261002_sep_q3_2026.html.txt (2026-10-02): September 2026 "Micro E-mini Nasdaq-100 futures
  ADV increased 73% to 2.4 million contracts"; Q3 2026 "Micro E-mini Nasdaq-100 futures ADV increased 101% to 2.6
  million contracts". No 12-month product ADV for NQ, YM, MYM or M2K after 2023-10 was found.
- An FIA annual review for 2023 (fia_etd_trends_2023_annual.pdf) was fetched; its calendar-2023 totals include
  Nov-Dec 2023 (inside the pilot window) and are not used.

### F13. Retail and participant descriptions (CME), all micros

- cme_micro_emini_faq.html.txt (CME FAQ, Wayback 2024): "The amount of capital needed to access the futures market
  has become too burdensome for many individual traders. To make our more market accessible to all, CME will launch
  the Micro E-mini suite of futures".
- cme_om_2024_micro_five_years_v2.html.txt (CME OpenMarkets, 2024): "At one-tenth the size of its regular E-mini
  futures contract, the micros offer retail traders an opportunity to execute trades with smaller sums and lower
  margin requirements." "While the pandemic era surge in retail trading fueled some of the popularity of these
  contracts".
- cme_om_brokers_micro_boom.html.txt (CME OpenMarkets, 2021): "During the first ten months of 2021, those four
  Micro contracts combined traded an average of 2.06 million contracts a day ... That represents 38% of overall
  equity index ADV at CME Group over that period." (Broker quotes in that article are interviews: pointers only.)
- cme_pr_20230317_micro_2bn.html.txt: "More than 324 firms and 172,000 unique accounts have traded these contracts
  in the last year".
- No CME, CFTC or regulator statement giving a percentage of micro (or mini) volume that is retail was found
  (WebSearch calls 2, 9, 12). Quantitative proxies: CFTC nonreportable share of OI (F7) and the CFTC small-trader
  volume shares for NQ (F6).

## Candidate fact sheets

Each sheet lists product-specific facts and points to the family sections. "Unknown" means searched and not
found; the search is named.

### MNQ: Micro E-mini Nasdaq-100 Index Futures (the baseline)

- Code and exchange: CME Globex MNQ, CME rulebook chapter 361 (F2 table: "Micro E-mini NASDAQ-100 Index Futures
  361 MNQ Associated NQ").
- Contract size: "$2 x Nasdaq-100 Index" (cme_old_specs_micro-e-mini-nasdaq-100.html.txt, Wayback 2020-12-01).
- Tick: 0.25 index points = USD 0.50 (F1: "Micro E-mini Nasdaq-100 Index Futures: 0.25 Index points, equal to $0.50
  per contract"); calendar spread 0.05 = USD 0.10.
- Launch: 2019-05-06 (F1). Gate (60 Globex trade dates in 2023-11..2024-02): launched before 2023-11 and listed
  continuously as far as sources show (COT weekly reports 53 of 53 weeks to 2023-10-31, F7; product in CME releases
  through 2026-10, F12). No delisting found.
- Matching: FIFO (F1, "F: First In, First Out (FIFO)").
- Hours: F3. Limits: F2 (associated with NQ); hits: F8.
- ADV/OI: F12 (Oct-2023 ADV 1,420,645; Jan-Oct 2023 1,114,224; OI 110,189 at end Oct-2023; full-year 2025 ADV 1.6
  million; Q3 2026 2.6 million). No owned bars before 2025-04-01 (A0).
- Participants: COT TFF 2022-11..2023-10 (F7): Lev Money 0.452, NonRept 0.438, Dealer 0.051, Asset Mgr 0.019,
  Other 0.041 of OI; mean 42 reportable traders. Retail descriptions F13 (qualitative). ATS/HFT shares: none
  published for MNQ (F6 covers NQ only).
- Market-maker program: Micro E-mini Futures Market Maker Program, 2019-05-06 to at least 2020 (F5); status
  2022-2024 unknown.
- Spread, depth, queue, volume per minute: unknown (F10).
- Product-specific scheduled releases: none found (F9). Weekend gap: no underlying trading while Globex is closed
  found (F4).
- Microstructure evidence: R1 (MMF, negative/null on NQ OFI and queue depletion), R2 (MMF, adverse fills dominate
  passive posting on NQ), R6 (SAME, price discovery), R8 (SAME, bar-based null), R3/R4/R5 (COUSIN, ES).
- Relation to ES/MES: F9. Fees in the launch filing (exchange fee schedule, not prop-firm fees): F1.

### NQ: E-mini Nasdaq-100 Futures

- Code and exchange: CME Globex NQ, chapter 359, Rule 589 "Primary" (F2).
- Contract size: "$20 x Nasdaq-100 Index" (cme_old_specs_e-mini-nasdaq-100.html.txt, Wayback 2021-01-15).
- Tick: "Outright: 0.25 index points = $5.00"; "Calendar Spread: 0.05 ndex points = $1.00" (sic, same file).
- Launch: June 1999. mondovisione_2009_NQ_10th.html.txt (reprint of the CME Group / NASDAQ OMX release): "Since
  the product launch in June 1999, more than 636 million E-mini" [NASDAQ-100 futures had traded]. Traded in
  2012-2014 (F6) and 2022-2023 (F7, 53 of 53 weekly COT reports). Gate: met on the same reasoning as MNQ.
- Matching: FIFO. databento_cme_matching_algos.html.txt (Databento blog, 2025-08-01): "First in, first out (FIFO)
  ... Aggressing orders match resting orders at the same price level by time priority until filled ... Popular
  products: ES, NQ, ZN, ZF, ZB, CL outrights". [Vendor source, not CME; no CME filing for NQ's algorithm was
  fetched.]
- Hours F3; limits F2 (primary, 3.5% dynamic variant overnight); hits F8.
- ADV/OI: F12 (Oct-2023 762,475; Jan-Oct 2023 671,995; OI 259,306). A0 has owned ADV (median 618,345 for the
  standard window, A0_contract_stats.md).
- Participants: COT TFF (F7): Dealer 0.215, Asset Mgr 0.269, Lev Money 0.289, Other 0.071, NonRept 0.157; mean 291
  reportable traders. CFTC ATS (F6): 2016-2018 ATS share 74.0%, ATS-ATS 54.4%, MAN-MAN 5.8% of volume; small
  traders (below 0.5% of daily volume) 37.0% of volume (17.5 ATS + 19.5 MAN) in 2016-2018. CFTC 2019: "only one
  product with a decrease in automated trading - the E-mini NASDAQ 100 futures contract."
- Market-maker program: CME/CBOT E-mini Equity Index Futures Market Maker Program, cftc_rule012819_emini_eq_mm_
  program.txt (filed 2019-01-15): "Product Scope E-mini S&P 500 Futures ("ES"), E-mini Nasdaq-100 Futures ("NQ"),
  E-mini S&P MidCap 400 Futures ("EMD"), and E-mini Dow ($5) Futures ("YM") on Globex"; "Start date is April 1,
  2013. End date is January 31, 2019 January 31, 2021." (overstrike caveat, F5); "Designated hours during RTH
  (8:30AM - 3:00PM)"; "participants must quote pre-determined continuous two-sided markets in designated contract
  months of the Products at maximum bid/offer spreads and minimum quote sizes"; participants "must also be
  participating in the CME Group E-mini Equity Liquidity Provider Program". Earlier version 2014 (cftc_rul031214_
  emini_eq_mm_program.txt) has the same scope. Status 2022-2024 unknown (WebSearch call 20 found no 2022-2023
  filing).
- Spread/depth: unknown (F10); Kurov (2008) on spreads after the 2006 tick cut (abstract only).
- Releases F9; weekend gap F4.
- Microstructure evidence: R1 (SAME, negative/null), R2 (SAME, negative for naive passive posting), R7 (SAME,
  spreads), R8 (MMF, bar-based null), R3/R4/R5 (COUSIN).

### RTY: E-mini Russell 2000 Index Futures

- Code and exchange: CME Globex RTY, chapter 393, Rule 589 "Primary" (F2). BTIC code RLT.
- Contract size: "$50 x Russell 2000 Index" (cme_old_specs_e-mini-russell-2000.html.txt, Wayback 2021-01-25).
- Tick: "Outright: 0.10 index points = $5.00"; "Calendar Spread: 0.05 index points = $2.50".
- Launch at CME: cftc_ptc041317_cme003_RTY_listing.txt (CME Submission 17-110, filed 2017-04-12): "for trading on
  the CME Globex electronic trading platform ... effective on Sunday, July 9, 2017, for trade date of Monday, July
  10, 2017." (Russell 2000 futures traded on ICE before; Nadex notice in WebSearch call 8, snippet only.) Gate:
  traded 2022-2023 (F7, 53 of 53 weeks); no delisting found.
- Matching: FIFO. Same filing: "CME Globex F: First In First Out (FIFO) Matching Algorithm". Hours at launch:
  "CME Globex: 5:00pm to 4:00pm, Sun-Fri, with trading halt from 3:15pm to 3:30pm, Mon-Fri." (CT; halt removed
  2021, F3). Position limits at launch: "All-Month Position Limit: 60,000 contracts" (later raised; WebSearch call
  8 snippet on submission 17-262 [unverified]).
- Limits F2; hits F8.
- ADV/OI: F12 (Oct-2023 231,303; Jan-Oct 2023 218,224; OI 559,075 with the subtotal inconsistency noted; Q4 2025
  ADV 218,000). A0 has owned ADV (median 181,060).
- Participants: COT TFF (F7): Asset Mgr 0.450, Lev Money 0.232, Dealer 0.207, Other 0.063, NonRept 0.049; mean 337
  reportable traders. No CFTC ATS table covers RTY (F6).
- Market-maker program: E-mini Russell 2000 Futures Market Maker Program, 2017-07-10 to "December 31, 2017 March
  31, 2018" (F5), up to 15 participants, "continuous two-sided markets ... at maximum bid/ask spreads and minimum
  quote sizes". Status after 2018 unknown.
- Spread/depth: unknown (F10; CME RTY liquidity report holds only an interactive chart).
- Releases F9 (Russell reconstitution annual, unverified); weekend gap F4.
- Microstructure evidence: none on RTY or M2K found; R1, R2 (COUSIN on NQ), R3-R5 (COUSIN on ES).

### M2K: Micro E-mini Russell 2000 Index Futures

- Code and exchange: CME Globex M2K, chapter 363, Rule 589 "Associated" with RTY (F2).
- Contract size: "$5 x Russell 2000 Index" (cme_old_specs_micro-e-mini-russell-2000.html.txt, Wayback 2021-01-15).
- Tick: 0.10 index points = USD 0.50 (F1); calendar spread 0.05 = USD 0.25.
- Launch: 2019-05-06 (F1). Gate: COT shows M2K in only 6 of 53 weekly reports in 2022-11..2023-10 (F7), which
  reflects CFTC publication thresholds [reason unverified], not trading; CME's monthly review shows M2K ADV of
  78,372 in Oct-2023 and OI 23,021 (F12), so it traded through 2023-10. No delisting found.
- Matching: FIFO (F1). Hours F3; limits F2; hits F8.
- ADV/OI: F12 (Oct-2023 78,372; Jan-Oct 2023 76,712; 2022 full-year 130,807; OI 23,021). No owned bars before
  2025-04-01 (A0). No published product ADV after 2023-10 found.
- Participants: COT TFF (F7, 6 reports): Lev Money 0.441, NonRept 0.439, Dealer 0.054, Asset Mgr 0.022, Other 0.043;
  mean 21 reportable traders. Retail descriptions F13. ATS shares: none published.
- Market-maker program: Micro E-mini Futures Market Maker Program (F5).
- Spread/depth: unknown (F10). Releases F9; weekend gap F4.
- Microstructure evidence: R6 (SAME, price discovery); none on order-book predictability; R1/R2 COUSIN; R3-R5
  COUSIN.

### YM: E-mini Dow ($5) Futures (CBOT)

- Code and exchange: CME Globex YM, CBOT rulebook chapter 27, Rule 589 "Primary" (F2: "CBOT E-mini Dow Jones
  Industrial Average Index Futures ($5 Multiplier) 27 YM Primary ... 3.5% of Dynamically Calculated Reference
  Price").
- Contract size: "$5 x Dow Jones Industrial Average ("DJIA")" (cme_old_specs_e-mini-dow.html.txt, Wayback
  2020-12-03).
- Tick: "1.00 index point = $5.00" (same file).
- Launch: before 2012 (CFTC F6 tables cover "E-mini Dow ($5)" from 2012-11-12). Exact launch date not fetched
  [unverified; commonly given as April 2002 at CBOT]. Gate: traded 2022-2023 (F7, 53 of 53 weeks).
- Matching: UNKNOWN. Not in the fetched filings; Databento's FIFO list names "ES, NQ, ZN, ZF, ZB, CL outrights"
  only. The associated micro MYM is FIFO (F1).
- Hours F3; limits F2; hits F8.
- ADV/OI: F12 (Oct-2023 208,407; Jan-Oct 2023 175,187; OI 103,936). A0 has owned ADV (median 163,416).
- Participants: COT TFF (F7): Dealer 0.311, Lev Money 0.244, Asset Mgr 0.155, Other 0.130, NonRept 0.160; mean 93
  reportable traders. CFTC ATS (F6): 2016-2018 ATS 81.2%, ATS-ATS 66.1%, MAN-MAN 3.6% of volume.
- Market-maker program: in scope of the E-mini Equity Index Futures Market Maker Program (NQ sheet), to at least
  2019-2021; status 2022-2024 unknown.
- Spread/depth: unknown (F10). Releases F9; weekend gap F4.
- Microstructure evidence: none on YM or MYM found; R1/R2 COUSIN; R3-R5 COUSIN.

### MYM: Micro E-mini Dow Jones Industrial Average Index Futures (CBOT)

- Code and exchange: CME Globex MYM, CBOT chapter 28, Rule 589 "Associated" with YM (F2).
- Contract size: "$0.50 x DJIA Index" (cme_old_specs_micro-e-mini-dow.html.txt, Wayback 2020-12-02).
- Tick: 1.00 index point = USD 0.50 (F1; spec page: "Outright: 1.0 index points = $0.50").
- Launch: 2019-05-06 (F1). Gate: COT shows MYM in 20 of 53 weekly reports, last 2023-08-01 (F7, publication
  threshold, reason unverified); CME's review shows Oct-2023 ADV 115,096 (F12), so it traded through 2023-10.
- Matching: FIFO (F1). Hours F3; limits F2; hits F8.
- ADV/OI: F12 (Oct-2023 115,096; Jan-Oct 2023 108,504; listed OI is a copy of MNQ's, implied OI 25,224 at end
  Oct-2023). No owned bars before 2025-04-01 (A0). No published product ADV after 2023-10 found.
- Participants: COT TFF (F7, 20 reports): NonRept 0.475, Lev Money 0.418, Other 0.065, Dealer 0.027, Asset Mgr 0.015;
  mean 21 reportable traders. Retail descriptions F13. ATS shares: none published.
- Market-maker program: Micro E-mini Futures Market Maker Program (F5).
- Spread/depth: unknown (F10). Releases F9; weekend gap F4.
- Microstructure evidence: R6 (SAME, price discovery); none on order-book predictability; R1/R2 COUSIN; R3-R5
  COUSIN.

## Unknowns, failures and negative results (summary)

- Unknown for all six: median bid-ask spread (main and overnight), depth at the best level, touch queue size,
  traded volume per minute for the micros (A0 has NQ, RTY, YM), HFT share by contract, any retail percentage,
  per-product overnight price-limit hit dates, intraday correlation with ES.
- Unknown for some: YM matching algorithm and exact launch date; NQ, YM, MYM, M2K product ADV after 2023-10; whether
  any of the market-maker programs (F5, NQ sheet) ran in 2022-2024; CFTC ATS shares for RTY and the micros.
- Data-quality flags in CME's own tables: MYM open interest cells copy MNQ's (F12); Russell 2000 OI subtotal for
  2023-10 does not add up (F12).
- Negative or null evidence found: R1 (NQ, OFI and queue depletion carry no direction against a 3-tick barrier;
  abstract only), R2 (NQ, about two thirds of naive passive fills adverse on one day), R8 (MNQ bar-based signals
  null; not order-book). Positive order-book evidence exists only on ES (R3; classification, no realistic net test).
- Fetch failures: cmegroup.com direct (HTTP 403, checked once at about 05:31 PDT); investor.cmegroup.com and cmegroupinc.gcs-web.com
  HTTP 403; sec.gov HTTP 403 (exhibit 3-148); several Wayback snapshots returned 404 pages (cme_om_2024_micro_five_
  years.html, cme_pr_20241209_micro_3bn.html, cme_eqreview_2025-12/2026-08/2026-09.html, cme_2025_equity_insights_
  report.html, cme_pr_20090622_NQ_10th.html: saved 404 pages, not evidence); Wayback availability/CDX API HTTP 429 at
  about 05:20 PDT; a CME price-limit FAQ snapshot held no text. No Scrapling or Firecrawl was used (not needed after
  Wayback and cftc.gov copies worked; no terms check was therefore required).
- Budget: 22 of 40 WebSearch calls used; no budget notice was seen. Crossref and arXiv APIs used for discovery.
- No market data was read; COT rows dated 2023-11-01 or later were dropped in the script before use; the FIA 2023
  annual totals (which include Nov-Dec 2023) were fetched but not used.
