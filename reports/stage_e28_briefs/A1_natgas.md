# A1_natgas: Layer 1 fact sheets for MNG, QG, NG (Stage E.28 Part A)

Worker: A1_natgas (Opus 5.5). Started 2026-10-21 02:58 PDT. Facts only; nothing is scored here (the blind scorer
and the script score later against reports/stage_e28_ranking_spec.md sections 0 to 2). Every page cited is saved under
reports/stage_e28_briefs/pages/A1_natgas/ and logged in pages/A1_natgas/log.tsv (URL, UTC and PDT fetch time, sha256).
"File:" names below are relative to that folder. No market data was read. Owned 1-minute magnitudes (sigma_1m, R_d,
owned ADV, 4-sigma day counts) belong to A0 (reports/stage_e28_briefs/A0_contract_stats.md) and are not computed here.

Status: complete as of 2026-10-21 05:30 PDT (resumed 2026-10-21 05:11 PDT after a usage cut; the first pass wrote F1-F5). Machine-readable version: reports/stage_e28_briefs/A1_natgas.json (built by work/A1_natgas/A1_natgas_json.py; every quote in it was checked by script against its saved source file, 0 mismatches).

## F. Family-wide facts (Henry Hub natural gas complex, NYMEX, on CME Globex)

### F1. The three outrights side by side

CME's Micro Henry Hub FAQ compares all three (File: cme_faq_MNG.html, .txt lines 60-125; Wayback copy of
https://www.cmegroup.com/articles/faqs/micro-henry-hub-natural-gas-futures-and-options-frequently-asked-questions.html):

| Field | MNG (Micro Henry Hub) | QG (E-mini Natural Gas) | NG (Henry Hub Natural Gas) |
|---|---|---|---|
| Contract size | 1,000 MMBtu | 2,500 MMBtu | 10,000 MMBtu |
| Ratio to NG | 10:1 | 4:1 | 1 |
| Tick | $0.001/MMBtu | $0.005/MMBtu | $0.001/MMBtu |
| Tick value | $1 | $12.50 | $10 |
| Settlement | Financial | Financial | Physical |
| Expiry | 1 business day before NG expiry | business day before NG's last trading day | 3rd last business day of the month before the contract month |
| NYMEX rulebook chapter | 440 | 402 | 220 |

Verbatim (FAQ): "MINIMUM TICK INCREMENT $0.001 per MMBtu $0.005 per MMBtu ... DOLLAR VALUE OF ONE TICK $1 per contract
$12.50 per contract ... $10 per contract PRODUCT CODE MNG QG MNO MN1; MN2; MN3; MN4; MN5 NG". NG expiry: "Trading
terminates on the 3rd last business day of the month prior to the contract month." QG expiry: "Trading shall cease on
the business day immediately preceding the last day of trading in the current delivery month of the Henry Hub Natural
Gas Futures contract (NG)." MNG expiry: "Trading terminates one (1) business day prior to the expiration of the
corresponding contract month of the Henry Hub Natural Gas Futures contract (NG)."

Rulebook confirmations:
- NG (File: nymex_rulebook_ch220_NG.pdf/.txt): "The unit of trading shall be 10,000 MMBtu." "The minimum fluctuation
  shall be $0.001 (one tenth of one cent) per MMBtu." "Trades may also occur in multiples of $ 0.00025 per MMBtu for
  Henry Hub Natural Gas Futures inter-commodity spreads executed as simultaneous transactions on GLOBEX". "No trades in
  Henry Hub Natural Gas futures in the expiring contract month shall be made after the third business day prior to the
  first day of the delivery month for such expiring contract."
- QG (File: nymex_rulebook_ch402_QG.pdf/.txt): "The contract quantity shall be 2,500 MMBtu"; "$0.005 per MMBtu ($12.50
  per Contract)"; "Trading in the current delivery month shall cease on the business day immediately preceding the ...".
  CME Japanese-language spec page (File: cme_ja_QG.html.txt line 127-129): "1mmBtu当たり0.005ドル刻み" (in $0.005 steps
  per MMBtu) and "CME Globex: QG 清算: QG"; contract months (line 131): "当年の残りの月から5年先までの連続暦月" (consecutive
  calendar months from the rest of the current year through 5 years ahead).
- MNG (File: nymex_rulebook_ch440_MNG.pdf/.txt and the CFTC launch filing cftc_ptc0926237029_MNG_launch.pdf/.txt,
  NYMEX Submission No. 23-371): "The contract quantity shall be 1,000 MMBtu."; "The minimum price fluctuation shall be
  $0.001 per MMBtu."; filing table: "Value per Tick $1.00", "Settlement Type Financial".
- NG:QG intercommodity spread listed on Globex from trade date 2024-01-22 (File: cme_chadv23_372_NG_QG_spread.pdf/.txt,
  CME Clearing Advisory 23-372): "Henry Hub Natural Gas Futures vs. E- mini Natural Gas Futures NG:QG 1:4 0.00025" and
  "there is no change to the outright futures trade tick which remains at 0.005". Note: a 1:4 NG:QG spread on Globex
  ties QG's book to NG's (implied or spread-driven QG liquidity); the advisory does not say whether implied prices are
  disseminated into the QG outright book.

Tick in price terms: QG's tick ($0.005) is 5 times NG's and MNG's ($0.001) in price; per contract-dollar, QG tick
$12.50, NG $10, MNG $1.

### F2. Trading hours (all three)

CME Globex Sunday-Friday 17:00-16:00 CT with a 60-minute daily halt at 16:00 CT (= Sunday-Friday 15:00-14:00
America/Vancouver, halt 14:00-15:00 PT). FAQ (File: cme_faq_MNG.html.txt): "CME Globex: Sunday – Friday: 5:00 p.m. to
4:00 p.m. Central Time (CT) Monday – Friday: 60-minute daily trading halt beginning at 4:00 p.m. CT"; MNG filing:
"CME Globex Pre-open: Sunday 4:00 p.m. - 5:00 p.m. Central Time/CT Monday – Thursday 4:45 p.m. - 5:00 p.m. CT" and
"CME Globex: Sunday 5:00 p.m. - Friday 4:00 p.m. CT with a daily maintenance period from 4:00 p.m. - 5:00 p.m. CT".
QG, CME Japanese page (File: cme_ja_QG.html.txt line 121): "日曜日―金曜日：6:00 p.m. - 5:00 p.m. (5:00 p.m. - 4:00 p.m.
シカゴ時間/CT) ただし、5:00 p.m. (4:00 p.m. CT) から60分間は取引休止" (Sunday-Friday 6 pm - 5 pm ET (5 pm - 4 pm CT),
with a 60-minute halt from 5 pm ET (4 pm CT)). NG has the same Globex schedule as its micro per the FAQ comparison table
(one TRADING SCHEDULE row shared by all five columns).

### F3. Matching algorithm (outrights)

- MNG: F-FIFO. MNG filing table: "CME Globex F-FIFO Matching Algorithm".
- NG: FIFO. FAQ Q10 (File: cme_faq_MNG.html.txt line 149): "Micro Henry Hub futures and options use a FIFO (first in,
  first out) algorithm, identical to their standard-sized counterparts." The standard-sized counterpart of MNG is NG.
- QG: not found. The MNG FAQ's "identical to their standard-sized counterparts" refers to NG; no source names QG's
  algorithm. Searched: CME client wiki "CME Globex Matching Algorithms" (cme_wiki_matching_algorithms.html.txt, no
  per-product table), Databento's CME matching blog (databento_blog_cme_matching.html.txt, no per-product table), the
  NYMEX 2018 algorithm filing (cftc_rule102518_nymex.txt, three energy options only), one WebSearch. The QG contract
  specification page on Wayback returned 404 (cme_QG_specs.html, log line 4). Unknown.

### F4. Price limits and circuit breakers (NYMEX Rule 589)

NG is the "Primary" product; QG (and the other Henry Hub look-alikes) are "Associated" with NG and share its limits.
Mechanism: dynamic circuit breakers, no hard daily limit; a triggering event starts a 2-minute monitoring period and,
if the lead month is still bid/offered at the limit, a 2-minute temporary halt; limits then expand.
- SER-8569 (File: cme_SER8569.pdf/.txt): "Effective Sunday, April 5, 2020 for trade date Monday, April 6, 2020 ...
  NYMEX is increasing the dynamic circuit breakers for the energy contracts from 7% to 15%." Exhibit row: "Henry Hub
  Natural Gas Futures 220 NG Primary Primary" and "E-mini Natural Gas Futures 402 QG Associated NG".
- Rule 589 text (File: cftc_ptc032320_nymex_dcb15.pdf/.txt lines 164-205): "it will be considered a triggering event
  that will begin a two (2) minute monitoring period in the lead contract month. If, at the end of the two (2) minute
  monitoring period, the lead contract month of the primary futures contract is bid or offered at the applicable special
  price fluctuation limit, a two (2) minute temporary trading halt will" [begin].
- History: CME emergency action of 2018-11-14 (File: cftc_ptc111618_nymex_emergency.pdf/.txt, CME Submission 18-464):
  "the CME Group Global Command Center (“GCC”) took emergency action on November 14, 2018, effective for trade date
  November 15, 2018. The emergency action was taken in light of recent natural gas price movements ... GCC amended the
  special price fluctuation limits of the Contracts from 30 cents to 50 cents." The 2020 amendment (filing
  cftc_ptc032320): "the Exchanges are increasing the special price fluctuation limits from 7% to 15% in light of recent
  market volatility. These changes are intended to reduce market interruptions".
- MNG: subject to Rule 589 (MNG filing rule 440102.D: "the contract shall be subject to special price fluctuation
  limits as set forth in Rule 589"); its row in the Rule 589 table is an image in the filing (Exhibit E), not readable
  from the text.
- Limit-hit (halt) days 2019-2024: not found in any public CME or CFTC tabulation within this search (see F13 and F16).
  The 2018 and 2020 filings show that limit levels were tight enough to cause "market interruptions" before April 2020;
  that is not a day count.

### F5. Automated (algorithmic) trading shares for Henry Hub NG (CFTC, Haynes and Roberts)

These are for "Natural Gas (Henry Hub)" futures in CME transaction data (NG; the papers do not say whether QG is
pooled in; MNG did not exist). ATS = automated trading system (orders entered by algorithm), MAN = manual.

| Window | ATS share of volume | ATS-ATS | ATS-MAN | MAN-MAN | Source |
|---|---|---|---|---|---|
| 2012-11-12..2014-10-31 | (not given as one column) | 30.7 | 45.8 | 19.1 | Haynes and Roberts 2015, Table 4 |
| 2014-11-01..2016-10-31 | 63.3 | 42.5 | 41.6 | 12.3 | Update #2 (2019), Table 3 (black) |
| 2016-11-01..2018-10-31 | 69.9 | 50.9 | 38.0 | 7.9 | Update #2 (2019), Table 3 (red) |

- Haynes and Roberts (2015), "Automated Trading in Futures Markets", CFTC OCE white paper, March 13, 2015 (File:
  cftc_haynes_roberts_2015_automated_trading.pdf/.txt line 423): "Energy - Natural Gas Natural Gas (Henry Hub) 153 30.7
  45.8 19.1" under header "Total Volume (mm) ATS–ATS (%) ATS–MAN (%) MAN–MAN (%)" and note "Source: CME transaction data,
  November 12, 2012 – October 31, 2014."
- Haynes and Roberts (2019), "Automated Trading in Futures Markets — Update #2", March 26, 2019 (File:
  cftc_ats_update2_2019.pdf/.txt line 453): "Energy - Natural Gas Natural Gas (Henry Hub) 175 219 63.3 69.9 33.1 26.9
  42.5 50.9 41.6 38.0 12.3 7.9", header "Total Volume ATS MAN ATS–ATS ATS–MAN MAN–MAN", note "Black numbers correspond to
  the original sample period: November 1, 2014 – October 31, 2016. Red numbers correspond to the new sample period:
  November 1, 2016 – October 31, 2018." For comparison, the same table's Crude Oil row: "454 618 60.4 69.4".
- Large vs small traders (Update #2 Table 5, line 507): "Natural Gas (Henry Hub) 35,136 31,291 17.8 17.0 21.7 19.1 565
  459 45.6 52.9 11.4 7.8" (small-trader N, ATS%, MAN%; large-trader N, ATS%, MAN%; large = at least 0.5% of daily
  volume). In 2016-11..2018-10: large automated traders 52.9% of volume, small automated 17.0%, small manual 19.1%,
  large manual 7.8%.
- Speed of passive fills (2015 paper, p. 11 text, line 596): "over 90 percent of passive executed corn orders remained in
  the book longer than one second, as are 85 percent of natural gas futures." Table 7 (2015) NG row (line 662), share of
  two-sided volume where the passive order rested 0-100 ms: ATS 3.2, MAN 1.2; 100-500 ms: 1.4, 0.5; 500 ms-1 s: 1.0, 0.3;
  1-10 s: 5.8, 2.4; 10 s-1 min: 5.4, 3.6; remaining electronic volume (resting > 1 min): 26.3. Update #2 Table 6 (line
  534) for 2016-11..2018-10: 0-100 ms ATS 5.7, MAN 1.2; ... "Remaining Elec Volume" 23.9.
- Non-directional (market-making-like) trading of large traders (Update #2 Table 8, line 585): "Natural Gas (Henry Hub)
  69.6 76.5 9.9 4.6 32.3 34.6 1.4 0.6 41.3 43.5 2.2 0.9 45.4 47.8 2.7 1.1" (columns: Full Day ATS, MAN; 1 Min ATS, MAN;
  3 Min; 5 Min; each early, late). In 2016-11..2018-10, 76.5% of large automated traders' NG volume was non-directional
  over the full day and 34.6% within 1 minute.

Reader's note (not a score): NG's passive side is slower than equity-index futures (85% of passive fills rested more
than 1 second, versus about 80% for S&P per the same paragraph: "around 20 percent in Treasury and S&P futures" executed
within one second), but automation rose to about 70% of volume by 2018. No CFTC breakdown for QG or MNG was found.

### F6. Commitments of Traders (CFTC Disaggregated, futures only), 2022-11-01..2023-10-31

Computed by work/A1_natgas/A1_natgas_cot.py from the CFTC annual files (Files: cftc_fut_disagg_txt_2022.zip,
cftc_fut_disagg_txt_2023.zip, unzipped to cot_unzip_2022/2023/f_year.txt); rows with report date on or after
2023-11-01 are dropped before any field is read. 53 weekly reports, 2022-11-01..2023-10-31. Shares are mean percent of
open interest (spread positions added to both sides for swap, managed money and other reportables).

| CFTC code, market name | Units | OI mean (median) | Producer/merchant long, short | Swap long, short | Managed money long, short | Other reportable long, short | Nonreportable long, short | Reportable traders (mean) |
|---|---|---|---|---|---|---|---|---|
| 023651 "NAT GAS NYME" / "NATURAL GAS - NEW YORK MERCANTILE EXCHANGE" (NG) | 10,000 MMBtu | 1,189,842 (1,186,140) | 14.0, 21.3 | 26.4, 10.5 | 41.0, 44.4 | 12.7, 20.4 | 5.9, 3.5 | 286 |

- Commercial-hedger share proxy for NG (producer/merchant/processor/user, average of long and short): 17.6% of OI;
  adding swap dealers (often classed as commercial in the legacy report): about 36% (17.6 + 18.5).
- Nonreportable (small-trader proxy) share for NG: 4.7% of OI (average of long 5.9 and short 3.5).
- QG: no CFTC market named "E-mini" natural gas, or carrying QG's name, appears in the 2022-2023 disaggregated
  files (all names containing NAT, HENRY or GAS were listed; the NYMEX Henry Hub entries are "NAT GAS NYME"/"NATURAL
  GAS" 023651, "HENRY HUB" 03565B in 2,500 MMBtu units, "HENRY HUB LAST DAY FIN" 023A55, "HENRY HUB PENULTIMATE FIN"
  023A56, "HENRY HUB PENULTIMATE NAT GAS" 03565C in 2,500 MMBtu units). Code 03565B carries QG's contract unit
  (2,500 MMBtu) but an OI near 440,000 and a swap-dealer short share of 85%. It matches the NYMEX "HENRY HUB SWAP" (NN)
  contract, whose CME-reported open interest was 417,298 in August 2023 (File: cme_OI_report_NYMEX_COMEX_202310snap.txt
  line 164: "HENRY HUB SWAP NN 417,298 481,292"), against QG's 9,044 (line 23). So 03565B is NN, not QG, and no COT
  figure exists for QG (its open interest is too small for a separate report, or it is not reported separately).
  For reference only, 03565B: producer/merchant 17.1 long, 9.0 short; swap 27.3, 85.3; managed money 0.9, 0.3;
  other 49.1, 2.8; nonreportable 5.6, 2.7; 42 reportable traders.
- MNG: launched 2023-11-06, after the window; no pre-2023-11 COT exists. Later COT reports were not read (pilot-window
  rule).

### F7. Market-maker and incentive programs found

- NG, Physical Henry Hub (NG) Market Maker Program, NYMEX Submission 23-312, filed 2023-07-12 (File:
  cftc_rules071223_NG_MM_program.pdf/.txt): "The purpose of this Program is to build electronic liquidity in deferred
  Henry Hub spreads, strips, and strip spreads." Product scope: "Henry Hub Natural Gas Futures (“NG”) spreads and strips
  that are traded on the CME Globex Platform". Term: "Start date is July 1, 2017. End date is July 31, 2023 July 31,
  2024." (deleted and added end dates both appear in the text). Hours "8:00AM – 3:00PM CST." Obligations: "participants
  must quote two-sided markets in the applicable Products, at predetermined average bid/ask spreads and minimum quote
  sizes during a certain percentage of time-in-market." The same program, Submission 21-282, effective 2021-07-01
  (File: cftc_rule061721_NG_MM_program.pdf/.txt). Scope is deferred spreads and strips, not the front-month outright.
- Henry Hub look-alike and last-day financial futures on Globex (not NG, QG or MNG): NYMEX Submission 12-171,
  market making program, "Start date is July 1, 2012. End date is December 31, 2012." (File:
  cftc_rul061312_HH_lookalike_MM.pdf/.txt).
- MNG: the launch filing (NYMEX 23-371, File: cftc_ptc0926237029_MNG_launch.txt) contains no incentive or market-maker
  program (grep for "incentive", "market mak", "program" found none in that sense). Its fee exhibit: "Micro Natural Gas
  Futures (MNG) ... CME Globex $0.30 $0.60" (member, non-member, per side), "Cash Settlement $0.30 $0.60",
  "Facilitation Fee $0.06".
- QG: no program found. One discovery search (WebSearch, cftc.gov NYMEX "Micro Henry Hub" incentive or market maker
  program) returned only the NG and look-alike programs above. Not exhaustive: CME's own rule-filings pages are blocked
  from this IP.

### F8. Launch and listing (pilot-window eligibility, 60 Globex trade dates in 2023-11-01..2024-02-29)

- MNG: "Starting trade date November 06, 2023, Micro Henry Hub Natural Gas futures and options will be available for
  trading on CME Globex" (File: cme_faq_MNG.html.txt line 55). Press release 2023-11-08 (File:
  cme_pr_20231108_MNG_50k.html.txt line 48): "trading in its new Micro Henry Hub futures has surpassed 50,000
  contracts since launching on November 6, 2023". 24 serial months listed (FAQ Q4: "There are 24 serial contract
  months listed for Micro Henry Hub Natural Gas futures"; "The first listed month is December 2023"). MNG launched
  after 2023-11-01, so the "launch before 2023-11" shortcut does not apply. From 2023-11-06 to 2024-02-29 there are
  79 weekdays after removing 2023-11-23, 2023-12-25, 2024-01-01, 2024-01-15 and 2024-02-19 (a calendar count by the
  reader, assuming those five dates carry no separate trade date; no market data read), so 60 trade dates needs MNG
  to have traded on at least 60 of 79; that it kept trading every day is not shown by any
  source read here (no market data read). The owned-data inventory (A0_contract_stats.md line 185) shows owned MNG
  files only from 2025-04-01. Fact for the lead: eligibility for MNG rests on continuous listing from 2023-11-06; a
  Databento definition or statistics check (not done here) would confirm it.
- NG: listed since 1990 [unverified: date not in a saved source]. Electronic trading on CME Globex from 2006-09-05:
  Betancourt et al. (arxiv_1710.01415_betancourt_NG_networks.txt lines 200-201): "September 5, 2006, when electronic
  trading was introduced in this market." On Globex in the standard window (A0 owned NG bars from 2010-06-06, A0_contract_stats.md line 188). Launch before 2023-11 with
  continuous listing: yes.
- QG: launched as the NYMEX "e-miNY" natural gas contract on CME Globex on 2002-06-17. Source: two Mondo Visione
  copies of the 2002 NYMEX/CME announcements, saved by the crude worker (pages/A1_crude/mondovisione_2002_eminy_begin_
  june17.html.txt line 27, dated 30/05/2002: "e-miNY crude oil and natural gas contracts will begin trading on CME's
  GLOBEX electronic trading platform on June 17."; pages/A1_crude/mondovisione_2002_eminy_specs.html.txt lines 27-29,
  dated 22/05/2002: "4,000 million British thermal units of natural gas" and "Minimum Price Fluctuation: ... $.005
  for natural gas"). The 2002 contract was 4,000 MMBtu; today's QG is 2,500 MMBtu (rulebook ch. 402), so the contract
  size changed at some date not found. It was listed before 2023-11 in any case: the CME Clearing Advisory 23-372 (dated December 2023, File:
  cme_chadv23_372_NG_QG_spread.txt) refers to the existing "outright futures trade tick which remains at 0.005", and the
  NYMEX rulebook chapter 402 exists in the 2025 copy. Continuous listing through 2024-02 is consistent with the NG:QG
  spread being listed from trade date 2024-01-22, which requires a listed QG outright.

### F9. Published ADV and open interest (CME monthly reports, Wayback copies)

CME Group "Exchange ADV Report - Monthly" and "Exchange Open Interest Report - Monthly" (Wayback copies of
cmegroup.com/daily_bulletin/monthly_volume/...). These are exchange totals for the product code (all venues; the reports
do not split Globex from ClearPort or blocks). Product labels in the reports: NG = "NATURAL GAS PHY", QG = "MINY NATURAL
GAS", MNG = "NATURAL GAS PHY MNG" (listed among the micro rows).

| Window | NG | QG | MNG | File and line |
|---|---|---|---|---|
| ADV Aug 2023 | 376,529 | 8,340 | (not listed) | cme_ADV_report_CMEG_202309snap.txt lines 603, 588 |
| ADV YTD 2023 (Jan-Aug 2023) | 400,923 | 11,317 | - | same lines |
| ADV YTD 2022 (Jan-Aug 2022) | 353,594 | 15,732 | - | same lines |
| ADV Oct 2023 (CME press release) | "approximately 421,000" | - | - | cme_pr_20231108_MNG_50k.html.txt line 50 |
| ADV Oct 2025 | 557,219 | 3,565 | 14,609 | cme_ADV_report_NYMEX_COMEX_202511snap.txt lines 231, 230, 393 |
| ADV YTD 2025 (Jan-Oct 2025) | 534,766 | 4,502 | 13,781 | same lines |
| ADV YTD 2024 (Jan-Oct 2024) [overlaps the pilot months Jan-Feb 2024; aggregate published figure] | 500,071.56 | 6,404.15 | 5,178.97 | same lines |
| ADV Sep 2026 (latest published month found) | 569,681 | 2,961 | (no row found) | cme_ADV_report_CMEG_202610snap.txt lines 643, 613 |
| ADV YTD 2026 (Jan-Sep 2026) | 540,414 | 3,937 | (no row found) | same lines |
| ADV YTD 2025 (Jan-Sep 2025), same report | 545,684 | 4,618 | - | same lines |
| ADV Q4 2025 (CME release 2026-01-05) | 655,000 ("Henry Hub Natural Gas futures ADV increased 4% to 655,000 contracts") | - | - | mm_cme_2025_annual_adv.html.txt line 93 |
| ADV Dec 2025 | 708,000 ("Henry Hub Natural Gas futures ADV increased 9% to 708,000 contracts") | - | - | same file line 116 |
| OI end Aug 2023 | 1,148,827 | 9,044 | - | cme_OI_report_NYMEX_COMEX_202310snap.txt lines 24, 23 |
| OI end May 2024 | 1,495,281 | 10,448 | 4,890 | cme_OI_report_NYMEX_COMEX_202406snap.txt lines 24, 23, 178 |

Verbatim rows: "NATURAL GAS PHY NG 557,219 511,880.91 8.9% 462,646.95 20.4% 534,766 500,071.56 6.9%"; "MINY NATURAL GAS QG
3,565 5,009.48 -28.8% 2,877.29 23.9% 4,502 6,404.15 -29.7%"; "NATURAL GAS PHY MNG 14,609 7,631.78 91.4% 13,095.76 11.6%
13,781 5,178.97 166.1%" (header: "ADV OCT 2025 ADV OCT 2024 % CHG SEP 2025 % CHG Y.T.D 2025 Y.T.D 2024 % CHG"). August 2023
report: "MINY NATURAL GAS 8,340 16,712.52 -50.1% 7,409.95 12.6% 11,317 15,732 -28.1%"; "NATURAL GAS PHY 376,529
253,432.35 48.6% 323,929 16.2% 400,923 353,594 13.4%" (header "AUG 2023 AUG 2022 % CHG JUL 2023 % CHG Y.T.D 2023 Y.T.D
2022 % CHG"). The 2025 annual release: "Record annual Henry Hub Natural Gas futures and options ADV of 904,000 contracts"
(line 66; futures and options combined).

Not found: a CME 12-month ADV for exactly 2022-11..2023-10 (Wayback holds no NYMEX ADV report snapshot dated
2023-10/11 except a 2023-12-18 copy that reports November 2023, inside the pilot window, which was not read). A0 owns
NG 1-minute bars for the standard window (A0_contract_stats.md line 105, owned ADV column); A0's owned figure and the CME
exchange totals measure different things (A0: its own definition; CME: all venues, all expiries) and are not reconciled
here. The September 2026 CME Group report (Wayback 2026-10-10, fetched on a retry after Wayback refused connections
intermittently, logged http=000) has rows "MINY NATURAL GAS 2,961 2,877.29 2.9% 2,299.62 28.8% 3,937 4,618 -14.7%"
and "NATURAL GAS PHY 569,681 475,742.71 19.7% 465,679.71 22.3% 540,414 545,684 -1.0%" (header "SEP 2026 SEP 2025 %
CHG AUG 2026 % CHG Y.T.D 2026 Y.T.D 2025 % CHG"). That group-level report has no product codes and no MNG row (the
September 2025 MNG value 13,095.76 does not appear in it); the latest MNG figure found is therefore October 2025
(14,609; YTD Jan-Oct 2025 13,781). Latest open interest found: May 2024 (Wayback holds no later NYMEX OI report).

### F10. Spread, depth, queue and volume per minute

- NG spread, CME "Liquidity Insights: Henry Hub Attracts Global Interest", 15 Sep 2020 (File:
  cme_liqinsights_henryhub_2020.html.txt lines 29, 45; Wayback copy 2021-01-15): "Throughout Q2, US spreads remained
  fairly steady. Though non-US spreads were slightly elevated, they remained below 1.5 ticks on average." and (line 35)
  "CME Group price spreads during non-US trading hours were nearly as tight as during US trading hours". Non-US hours are
  defined there as "(5 p.m. – 7 a.m. CT)" (line 42). Window: H1/Q2 2020. The article gives no US-hours spread number and
  no depth number. It is a CME marketing article, and the spread statistic is an average, not a median.
- Median spread in ticks by session, depth at the best level, touch queue size: not found for NG, QG or MNG. The CME
  Liquidity Tool that holds these numbers needs a login (line 49: "the CME Group Liquidity Tool ... allows users access
  to multiple liquidity metrics, including the B/A spreads discussed above, for 18 core products across three time
  zones"), and cmegroup.com refuses this machine's IP. Haynes and Roberts (2015, 2019) give resting-time shares (F5), not
  depth. No academic depth study of NG was found (searches in F12).
- Traded volume per minute: owned by A0 (A0_contract_stats.md line 105, NG main-session volume per minute median 99,
  mean 150.0; overnight median 7, mean 27.7). QG and MNG: no owned files before 2023-11 (A0 line 212), so no volume per
  minute; from CME ADV (F9), MNG's Oct 2025 ADV of 14,609 is about 2.6% of NG's 557,219, and QG's 3,565 about 0.6%.
- QV (depth / volume per minute) cannot be formed for any of the three from sourced numbers (no depth source).

### F11. Scheduled product-specific releases: EIA Weekly Natural Gas Storage Report (WNGSR)

- Timing (File: eia_wngsr_schedule.html.txt line 5): "The standard release time and day of the week will be at 10:30
  a.m. eastern time on Thursdays with the following exceptions. All times are eastern." 10:30 ET = 07:30 America/
  Vancouver, inside the main session (06:30-13:00 PT). Holiday weeks move the release (table on the same page).
- Count: 1 product-specific scheduled high-impact release per week (WNGSR). No second weekly natural-gas-specific
  release was found; weather model updates (unscheduled in the exchange sense, several per day) and the monthly EIA
  STEO and Natural Gas Monthly were not counted (not searched as high-impact). Baker Hughes rig count (Fridays) is
  shared with crude and was not searched for natural gas impact.
- Impact, Linn and Zhu (2004), J. Futures Markets 24(3) 283-313, nearby NYMEX NG, five-minute intraday returns,
  1999-01-01..2002 (full text, File: linn_zhu_2004_JFM_ou.pdf/.txt, University of Oklahoma copy; abstract also in
  openalex_linn_zhu_2004_JFM.json). Lines 47-49: "the weekly gas storage report announcement was responsible for
  considerable volatility at the time of its release and that volatility up to 30 minutes following the announcement
  was also higher than normal." Line 484: "volatility also spikes around the EIA announcement at 10:30 AM on
  Thursday." Lines 666-671 (the earlier AGA report, Wednesday 2:00 PM): "the 2:00–2:05 PM Wednesday standard
  deviation for the second two calendar periods is on the order of six times the standard deviations for the same
  time periods on the other days of the week". Pit-era data (open-outcry hours "open 10:00 AM, close 2:30 PM", line
  321), before Globex NG (2006).
- Impact on returns, Prokopczuk, Wese Simen and Wichmann (2021), "The Natural Gas Announcement Day Puzzle", Energy
  Journal 42(2) (File: openalex_prokopczuk_2021_EJ.json, abstract only [unverified beyond the abstract]; the
  Liverpool repository copy is embargoed, per a WebSearch result, and the IAEE executive summary URL returned 404):
  "More than 50% of the annual return is earned on these days." "At the intraday level, the return splits half into a
  pre- and post-announcement part. The pre-announcement return is entirely generated on days when storage levels
  exceed analysts’ expectations casting doubt on explanations based on informed trading." "After transaction and
  funding cost, a simple trading strategy yields substantial returns."
- News and jumps, Borovkova and Mahakena (2015), Quantitative Finance 15(7) 1217-1242 (File:
  vu_borovkova_mahakena_landing.html.txt line 28, publisher abstract on the VU portal; full text not fetched): "the
  arrival of news in non-trading periods causes overnight returns" and "we find strong evidence that news sentiment
  severely Granger causes price jumps".
- Program-internal context: the program's own scheduled-event members included an NG storage pre-release member
  (C1_inventory.md line 86: "EIA/API, NG storage ... strategy/members/k4/ngpre.py").

### F12. Weekend gap, roll and expiry

- Weekend gap: Globex closes Friday 16:00 CT and reopens Sunday 17:00 CT (F2). No listed Henry Hub instrument that
  trades through the weekend was found; physical next-day gas for Saturday-Monday delivery is normally traded on the
  Friday [reader's note, unverified: not sourced]. So there is no crypto-style 24/7 underlying. News over the weekend
  still produces Sunday-open gaps: Borovkova and Mahakena (2015) report that "the arrival of news in non-trading
  periods causes overnight returns" (F11). A count of weekend gaps was not computed (A0 owns bar magnitudes).
- Expiry and roll: NG's last trade is the 3rd last business day of the month before delivery (F1); QG ceases "on the
  business day immediately preceding the last day of trading" of NG, and MNG "one (1) business day prior to the
  expiration" of NG (F1). So QG and MNG expire one business day before NG, and roll liquidity in the micro and E-mini
  shifts a day earlier. NG is monthly (all 12 months listed), so the front contract rolls every month, about 4-5
  business days of front-month expiry week per month. Haynes and Roberts (2015) on rolls generally (File:
  cftc_haynes_roberts_2015_automated_trading.txt lines 632-634): "During a futures roll, order-to-execution times
  increase, with spread quotes on average sitting in the book for a longer period".
  A0's owned-data method drops roll jumps (A0_contract_stats.md line 41: "instrument_id (so roll jumps are dropped)").
- Fungibility (FAQ Q12, File: cme_faq_MNG.html.txt): "Micro Henry Hub Natural Gas futures are fungible with E-mini
  Henry Hub Natural Gas futures, Natural Gas (Henry Hub) Penultimate Financial futures, and Henry Hub Natural Gas
  Penultimate Financial futures." (fungible for clearing offsets; separate Globex books).

### F13. Jump frequency and limit-hit days

- Days with |daily return| > 4 daily SD, per year: owned by A0 (A0_contract_stats.md line 142, NG, years 2010-2023,
  e.g. "2018: 3/246, 2019: 1/246, 2020: 1/245, 2021: 0/246, 2022: 0/246, 2023: 0/205"). Not computed here. No
  QG or MNG owned files before 2023-11.
- Circuit-breaker (DCB) or limit-hit days 2019-2024: not found. One search route tried in the earlier pass (CME and
  CFTC filings, F4); the 2018 GCC emergency action (limits 30 to 50 cents after "recent natural gas price movements")
  and the 2020 move to 15% "to reduce market interruptions" show that pre-2020 limits were being reached, but no
  per-day list exists in the saved sources. Unknown.

### F14. Published microstructure research on Henry Hub natural gas futures, and cousins

Searches: OpenAlex (11 queries: order flow, limit order book, HFT liquidity, storage report intraday, bid-ask
intraday, energy order imbalance, microstructure, informed trading intraday, jumps high-frequency, price discovery
electronic, Henry Hub liquidity providers), arXiv API (2 queries, no hits), WebSearch (4 queries on NG order-flow,
order-book or price-impact studies). No study of order-flow imbalance, queue imbalance, trade-sign predictability or
passive market-making profitability on NG, QG or MNG was found. What was found:

| Study | Relation to product | Topic | Result for short-horizon order-book patterns | Evidence level |
|---|---|---|---|---|
| Haynes and Roberts (2015; 2019 Update #2), CFTC OCE | same product (NG) | automation shares, resting times (F5) | descriptive; none | full text |
| Betancourt, Rodríguez and Boyd (arXiv 1710.01415, 2017; JRSS-C 2019), NYMEX NG 2005-01..2008-12 | same product | trading-network model; "make accurate short-term prediction of future transactions" (abstract) | predicts who trades with whom, not prices; not an order-book price signal | full text saved (arxiv_1710.01415_betancourt_NG_networks.txt; lines 25-26, 198-201) |
| Masteika and Vaitonis (2015), LNBIP, "Quantitative Research in High Frequency Trading for Natural Gas Futures Market" | same product (NYMEX NG, bid/ask and trade records) | calendar-spread statistical arbitrage in HFT | "Statistical arbitrage and HFT has given positive results and refuted the efficient market hypothesis" (abstract). Positive, but an inter-contract spread rule, not order-book imbalance; cost treatment unknown | abstract only [unverified] (openalex_masteika_vaitonis_2015.json) |
| Linn and Zhu (2004), JFM | same product (pit era) | storage-report volatility | volatility spike at release, up to 30 min elevated; not a directional signal | full text (F11) |
| Prokopczuk, Wese Simen and Wichmann (2021), Energy Journal | same product (front month) | announcement-day returns | daily and intraday drift around releases; "After transaction and funding cost, a simple trading strategy yields substantial returns" (abstract). A directional event pattern, not an order-book one | abstract only [unverified] |
| Borovkova and Mahakena (2015), Quantitative Finance | same product | news sentiment, jumps, volatility | news Granger-causes jumps; volatility forecasts improve; not order-book | abstract only [unverified] |
| Chevallier and Sévi (2012), Energy Economics (WP version saved) | same product (NYMEX NG, 2006-09-28..2010-01-15) and CL | volume-volatility | "a contemporaneous and largely positive relationship" (lines 42-45); not predictive of direction | full text (economix_chevallier_sevi_2011_vol_volume.txt) |
| Pinto-Gutierrez (2012), SSRN 2139767, "The Informational Content of the Limit Order Book and Trade Duration in the Electronic Energy Market" | unknown market (title says energy; no abstract in OpenAlex; SSRN blocked) | LOB information content | unknown | title only [unverified] (openalex_pinto_gutierrez_2012.json) |
| Benato (MSc thesis, Padova), "The information content of the limit order book on energy markets" | asset class only (EEX Germany Baseload power futures, not CME) | LOB and short-term returns | positive in-sample: "the book imbalance coefficients beyond the top price quote are jointly significantly different from zero. This confirms the informativeness of the limit orders behind the best price level, even if it appears to be little." (lines 1571-1573); a master's thesis, no costs | full text (unipd_benato_lob_energy_thesis.txt) |
| CL studies collected by A1_crude (Raman, Robe and Yadav 2012/2014 on electronic market makers; Rousse and Sevi 2016 on pre-EIA order flow; Roberts 2018 on CL depth; Lalor and Swishchuk 2024-2026 on CL adverse selection) | close cousin (CME Globex energy) | see A1_crude.md section F1 and F6-F7 (lines 101-178) | Rousse and Sevi: "there are significantly more orders initiated by buyers in the two hours preceding the official release" (informed trading before the release, as quoted in A1_crude.md); no CL OFI or queue-imbalance price-prediction study found (C2_OFI.md line 1037) | cited from A1_crude's saved files, not re-read here |
| ES OFI (Cont, Kukanov and Stoikov style, CME BBO) collected by C2_OFI | futures broadly (CME Globex, equity index, not the same asset class) | OFI and price impact | "both price and flow impacts are significant at the one-second" [horizon] (C2_OFI.md line 1032) | cited from C2_OFI |
| Program-internal (not published): E.12 Gate 0 ridge on 1-minute bars | same product (NG) | 64-signal library, gross edge at 1.5x cost | "The best pair (NG h60, t 2.51) is not evidence after Holm" (C1_inventory.md line 213); the backward replication on NG 2010-2019 failed ("C1b FAIL (E.18)", line 91) | program records; bar features, not order-book |

Null and negative evidence: no published study showing order-book patterns absent or arbitraged away on NG was found
either. Passive-side speed evidence (F5): 85% of passive NG fills rested more than one second (2012-2014), and large
automated traders' NG volume was 76.5% non-directional over the day in 2016-2018 (market-making-like), which documents
professional liquidity provision but says nothing about its profitability.

### F15. Participant facts (retail, small traders, commercials)

- Retail share: no CME or regulator figure for retail share of NG, QG or MNG volume was found (one WebSearch; CME's
  investor pages are blocked from this IP). Proxies only:
  - CFTC small traders in NG (Haynes and Roberts 2019 Update #2, Table 5; "large" = at least 0.5% of daily volume, so
    "small" is not "retail"): small automated 17.0% and small manual 19.1% of NG volume in 2016-11..2018-10, so
    small traders about 36% (F5).
  - COT nonreportable share of NG open interest: 4.7% (2022-11..2023-10, F6).
  - MNG launch release (File: cme_pr_20230927_MNG_launch.html.txt line 50), Interactive Brokers EVP: micro contracts
    "continue to be a popular way for our active trader clients to manage their exposure with less upfront
    commitment." CME (line 49): "help a wider range of global investors access the liquidity". This frames MNG for
    smaller traders but gives no share.
  - FAQ Q2 (cme_faq_MNG.html.txt line 58): "responds directly to customer demand for a smaller, more precise
    instrument for managing natural gas price exposure".
- Commercial hedgers: NG producer/merchant 17.6% of OI (36% with swap dealers), managed money about 43% (F6). QG and
  MNG: no COT.
- Non-US share of NG: "over 22% of volume originating outside of the U.S." (October 2023, cme_pr_20231108_MNG_50k
  line 50); "Volume originating outside of the U.S. has also grown 3% this year to 21% of total volume" (2023 to
  September, launch release line 51).

## Candidate sheets

Each sheet lists the product's own facts and points to the family sections above for shared facts. "u" = unknown.

### MNG: Micro Henry Hub Natural Gas futures (NYMEX, rulebook chapter 440)

| Field | Fact | Source |
|---|---|---|
| Code, size | MNG; 1,000 MMBtu (1/10 of NG); financially settled | F1; nymex_rulebook_ch440_MNG.txt |
| Tick | $0.001/MMBtu = $1.00 per contract | F1 |
| Launch | trade date 2023-11-06 on CME Globex; 50,000 contracts by 2023-11-08 | F8 |
| Pilot-window eligibility | launched after 2023-11-01; 79 weekday trade dates 2023-11-06..2024-02-29; trading on each not verified (no market data read) | F8 |
| Matching | FIFO ("F-FIFO" in the launch filing; FAQ: "FIFO ... identical to their standard-sized counterparts") | F3 |
| Hours | Sun-Fri 17:00-16:00 CT, 60-min halt from 16:00 CT (15:00-14:00 PT) | F2 |
| Limits | dynamic circuit breakers under NYMEX Rule 589 (as NG); MNG's row in the Rule 589 table not readable; limit-hit days u | F4, F13 |
| ADV | Oct 2025 14,609; Jan-Oct 2025 13,781; Jan-Oct 2024 5,179 | F9 |
| OI | May 2024 4,890 | F9 |
| ADV 2022-11..2023-10 | not applicable (not listed) | F8 |
| Retail share | u (launch release: micros "a popular way for our active trader clients", IBKR quote) | F15 |
| Commercial share (COT) | u (no COT row in the pre-2023-11 window; later reports not read) | F6 |
| MM / incentive program | none found in the launch filing; exchange fee $0.30 member / $0.60 non-member per side on Globex | F7 |
| HFT / ATS share | u for MNG (CFTC tables are for NG, before MNG existed) | F5 |
| Spread, depth, queue, volume per minute | u; no owned bars before 2023-11 (A0 line 212) | F10 |
| Scheduled releases | EIA WNGSR, 1 per week, Thursday 10:30 ET (07:30 PT) | F11 |
| Weekend gap | Globex closed Fri 16:00 to Sun 17:00 CT; no 24/7 underlying found | F12 |
| Jumps | A0 owns; no owned MNG bars before 2023-11 | F13 |
| Expiry | 1 business day before NG's last trade day | F1, F12 |
| Fungibility | fungible with QG and the penultimate financial contracts (clearing) | F12 |
| Research on MNG itself | none found; NG studies apply as "its full-size version" | F14 |

### QG: E-mini Henry Hub Natural Gas futures (NYMEX, chapter 402; report label "MINY NATURAL GAS")

| Field | Fact | Source |
|---|---|---|
| Code, size | QG; 2,500 MMBtu (1/4 of NG); financially settled | F1; nymex_rulebook_ch402_QG.txt |
| Tick | $0.005/MMBtu = $12.50 per contract (5 times NG's tick in price) | F1 |
| Launch | e-miNY natural gas on CME Globex from 2002-06-17 (then 4,000 MMBtu); listed throughout 2023-2024 | F8 |
| Pilot-window eligibility | launch before 2023-11 and continuous listing: yes (NG:QG spread listed 2024-01-22 requires the QG outright) | F8 |
| Matching | u | F3 |
| Hours | Sun-Fri 17:00-16:00 CT, 60-min halt (CME Japanese spec page) | F2 |
| Limits | "Associated" with NG under Rule 589 dynamic circuit breakers (15% since 2020-04-06); limit-hit days u | F4, F13 |
| ADV | Sep 2026 2,961; Jan-Sep 2026 3,937; Oct 2025 3,565; Jan-Oct 2025 4,502; Aug 2023 8,340; Jan-Aug 2023 11,317 | F9 |
| OI | Aug 2023 9,044; May 2024 10,448 | F9 |
| Retail share | u | F15 |
| Commercial share (COT) | u (no separate COT market; 03565B is NN, not QG) | F6 |
| MM / incentive program | none found | F7 |
| HFT / ATS share | u (CFTC tables give NG only) | F5 |
| Spread, depth, queue, volume per minute | u; no owned bars before 2023-11 | F10 |
| Book links | NG:QG 1:4 intercommodity spread on Globex from 2024-01-22, spread tick 0.00025; outright tick stays 0.005 | F1 |
| Scheduled releases | EIA WNGSR, 1 per week | F11 |
| Weekend gap | as MNG | F12 |
| Jumps | A0 owns; no owned QG bars before 2023-11 | F13 |
| Expiry | business day before NG's last trade day | F1 |
| Research on QG itself | none found | F14 |

### NG: Henry Hub Natural Gas futures (NYMEX, chapter 220; report label "NATURAL GAS PHY")

| Field | Fact | Source |
|---|---|---|
| Code, size | NG; 10,000 MMBtu; physically delivered at Henry Hub | F1; nymex_rulebook_ch220_NG.txt |
| Tick | $0.001/MMBtu = $10.00 per contract | F1 |
| Launch | 1990 [unverified]; electronic on Globex from 2006-09-05 | F8 |
| Pilot-window eligibility | yes (launch before 2023-11, continuous listing; owned bars from 2010) | F8 |
| Matching | FIFO (per the MNG FAQ's "identical to their standard-sized counterparts") | F3 |
| Hours | Sun-Fri 17:00-16:00 CT, 60-min halt | F2 |
| Limits | Rule 589 "Primary" product; dynamic circuit breakers 15% since 2020-04-06 (7% before), 2-min monitoring then 2-min halt; 2018-11-14 emergency widening after "recent natural gas price movements"; limit-hit days 2019-2024 u | F4, F13 |
| ADV | Sep 2026 569,681; Jan-Sep 2026 540,414; Oct 2025 557,219; Jan-Oct 2025 534,766; Q4 2025 655,000; Dec 2025 708,000 | F9 |
| ADV near the standard window | Oct 2023 ~421,000; Aug 2023 376,529; Jan-Aug 2023 400,923 (owned-bar ADV: A0 line 105) | F9 |
| OI | Aug 2023 1,148,827; May 2024 1,495,281; COT mean 2022-11..2023-10 1,189,842 | F6, F9 |
| Retail share | u; small traders (<0.5% of daily volume) about 36% of volume in 2016-2018 (CFTC); nonreportable 4.7% of OI | F5, F6, F15 |
| Commercial share (COT) | producer/merchant 17.6% of OI (36% with swap dealers); managed money ~43% | F6 |
| MM / incentive program | Physical Henry Hub (NG) Market Maker Program since 2017-07-01, extended to 2024-07-31, for deferred spreads and strips (not the front outright) | F7 |
| HFT / ATS share | ATS 69.9% of volume 2016-11..2018-10 (63.3% in 2014-2016); ATS-ATS 50.9%; large ATS traders 52.9% of volume; 76.5% of large ATS volume non-directional over the day | F5 |
| Spread | "below 1.5 ticks on average" in non-US hours, Q2 2020 (CME); US-hours number not given; median by session u | F10 |
| Depth, touch queue | u | F10 |
| Volume per minute | A0 owns (main median 99, overnight median 7) | F10 |
| Passive resting times | 85% of passive fills rested more than 1 s (2012-2014) | F5 |
| Scheduled releases | EIA WNGSR, 1 per week, Thursday 10:30 ET; volatility spike and up to 30 min elevated (Linn and Zhu 2004) | F11 |
| Weekend gap | as MNG | F12 |
| Jumps | A0 owns (4-SD days per year 2010-2023) | F13 |
| Expiry, roll | monthly; last trade 3rd last business day of the prior month; physical delivery | F1, F12 |
| Research | same-product studies on volatility, events, networks, calendar-spread HFT (abstract only); none on OFI, queue imbalance or passive market-making profitability | F14 |

## F16. Unknowns, failures and search log

Unknown (value null in the JSON, with what was searched): MNG pilot-window trade-date count (launched 2023-11-06;
needs a definition or statistics check), QG matching algorithm, limit or DCB hit days 2019-2024 (all three), retail
share (all three; proxies only for NG), COT shares for QG and MNG, incentive programs for QG (none found) and MNG
(none in the launch filing), ATS shares for QG and MNG, median spread by session, depth at the best level and touch
queue size (all three; NG has one CME average for non-US hours in Q2 2020), QV for all three, NG listing date (1990,
unverified), the date QG changed from 4,000 to 2,500 MMBtu.

Failures and blocks: cmegroup.com and investor.cmegroup.com answer 403 from this IP (first pass); Firecrawl account out
of credits (first pass); Wayback refused connections intermittently (several http=000 entries in log.tsv, all retried
or noted); WebFetch cannot fetch web.archive.org and timed out on cmegroup.com; the AgEcon PDF (Farhangdoost and
Etienne 2020) returned an HTTP 202 challenge page and was not used; the IAEE executive summary of Prokopczuk et al.
returned 404; the Liverpool repository copy is embargoed (WebSearch result); SSRN not tried (known block).
Scrapling was not used (no fetch needed it after the curl and Wayback routes).

WebSearch calls in the resumed pass: 11 (QG launch; MNG ADV; NYMEX incentive programs; 2025 Henry Hub ADV; NG
order-flow studies; NG spread and depth; QG matching algorithm; Pinto-Gutierrez; Prokopczuk full text; retail share;
NG price-impact studies). The first pass did not log its WebSearch count; its log shows one failed Firecrawl search.
No budget notice was seen. OpenAlex: 16 calls; arXiv API: 2.

Pages read from other workers' folders (read only, not modified): pages/A1_crude/mondovisione_2002_eminy_begin_june17.html.txt
and mondovisione_2002_eminy_specs.html.txt (QG launch), A1_crude.md, C2_OFI.md, C1_inventory.md and
A0_contract_stats.md (cross-references only).
