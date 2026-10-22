# A1_fx: Layer 1 fact sheets for M6E, 6E, M6A, 6A (Stage E.28 Part A)

Worker: A1_fx (Opus 5.5). Started 2026-10-21 03:07 PDT. Facts only; nothing is scored here (the blind scorer and the
script score later against reports/stage_e28_ranking_spec.md sections 0 to 2). Every page cited is saved under
reports/stage_e28_briefs/pages/A1_fx/ and logged in pages/A1_fx/log.tsv (URL, UTC and PDT fetch time, sha256).
"File:" names below are relative to that folder. No market data was read. Owned 1-minute magnitudes (sigma_1m, R_d,
owned ADV, 4-sigma day counts) belong to A0 (reports/stage_e28_briefs/A0_contract_stats.md) and are not computed here.
CFTC Commitments of Traders files were read only for report dates 2022-11-01..2023-10-31 (rows dated later were
filtered out by the script before any statistic was computed: work/A1_fx/A1_fx_cot.py).

Status: complete as of 2026-10-21 05:38 PDT (resumed 05:12 PDT after a usage cut). Sections F1-F12 hold family facts (F5 and F6 were written first, before the cut, so they appear first); per-candidate sheets follow; open items are listed at the end.

## F. Family-wide facts (CME FX futures: Euro FX and Australian dollar complexes)

### F5. Automated (ATS) and manual trading shares: CFTC OCE, Haynes and Roberts

Three CFTC Office of the Chief Economist papers tabulate CME transaction data by ATS (automated trading system) vs
manual (MAN) vs non-electronic.

- 2015 paper (File: cftc_haynes_roberts_2015.pdf/.txt; sample "November 12, 2012 – October 31, 2014"), Table 1
  product groups (.txt line 234): "FX 51 3.4 (0.2) 79.9 (5.8) 16.8 (1.2)" (columns Products, Non-Electronic %, ATS %,
  Manual %). Text (line 244-250): "decreasing order, FX (80 percent), equities (67 percent) and interest rates (62
  percent). ... tools for automated trading have been in use in this asset class since at ... product class remains
  one of the most mature for automated execution".
  Table 2 subgroups (lines 321, 323): "FX - E Micros 8 0.0 (0.0) 66.3 (0.1) 33.7 (0.0)" and "FX - G10 25 2.8 (0.2)
  80.7 (5.4) 16.4 (1.1)". So the E-micro FX group (8 products, M6E and M6A among them; the paper does not list the
  members) had 66.3% ATS and 33.7% manual volume; G10 full-size 80.7% ATS.
  Table 4 most active (line 429): "FX - G10 Euro 110 64.5 28.9 4.4" (total volume 110 mm contracts; ATS–ATS 64.5%,
  ATS–MAN 28.9%, MAN–MAN 4.4%). The Australian dollar is not among the top three FX products (Euro, Yen, Pound), so
  no per-product 6A figure exists in this table.
- 2017 update (File: cftc_haynes_roberts_2017_update.pdf/.txt; samples 2012-11..2014-10 and 2014-11..2016-10),
  line 298: "FX - E Micros 8 8 0.0 (0.0) 0.0 (0.0) 66.3 (0.1) 69.3 (0.1) 33.7 (0.0) 30.7 (0.1)"; line 300: "FX - G10
  25 24 2.8 (0.2) 0.7 (0.0) 80.7 (5.4) 83.7 (5.1) 16.4 (1.1) 15.6 (1.0)"; line 321 Euro: "110 115 64.5 66.3 28.9 28.0
  4.4 5.1" (ATS–ATS 66.3% in 2014-16).
- 2019 update #2 (File: cftc_ats_update2_2019.pdf/.txt, "Automated Trading in Futures Markets — Update #2", Haynes
  and Roberts, March 26, 2019; samples 2014-11..2016-10 and 2016-11..2018-10), Table 1 line 433: "FX - E Micros 8 7
  0.0 (0.0) 0.0 (0.0) 69.3 (0.1) 70.9 (0.1) 30.7 (0.1) 29.1 (0.1)"; line 435: "FX - G10 24 25 0.7 (0.0) 0.8 (0.0)
  83.7 (5.1) 85.4 (4.8) 15.6 (1.0) 13.8 (0.8)". Table 3 line 458 Euro (columns Total Volume, ATS, MAN, ATS–ATS,
  ATS–MAN, MAN–MAN, each early/late): "Euro 115 125 80.3 82.0 19.1 17.2 66.3 69.4 28.0 25.1 5.1 4.6". So in
  2016-11..2018-10 the Euro FX future was 82.0% ATS by volume, 69.4% of volume ATS on both sides, 4.6% manual on both
  sides.
  Table 6, "Time Between Order Placement and Execution for Liquidity Providers" (lines 518-541; volume share of the
  passive side by resting time, ATS/MAN, early/late period, scaled by two-sided volume): "Euro 12.4 14.0 0.9 0.8 5.1
  4.4 0.4 0.3 2.7 2.5 0.3 0.2 10.6 10.2 1.8 1.5 4.9 4.7 1.6 1.3 9.1 9.9". Reading the column header (line 523-524:
  "0 – 100 ms | 100 ms – 500 ms | 500 ms – 1 sec | 1 sec – 10 sec | 10 sec – 1 min | Remaining Elec Volume"), in
  2016-18 the passive side of 14.0% (of two-sided volume) was ATS orders filled within 100 ms of placement or last
  modification, and only 9.9% rested longer than one minute ("Remaining"), against 19.5% for Crude Oil, 23.9% for
  Natural Gas, 33.7% for Corn and 11.2% for E-mini S&P 500 in the same table. Euro and Japanese Yen have the fastest
  liquidity-provision profile of the 14 products listed after the Nasdaq-100 E-mini.
  Text (lines 139-148): "the predictable cyclicality in these shares, most clearly observed in the E-mini S&P, Euro FX,
  and 10 Yr Treasury Note, results from the requirement to roll positions as contracts expire, a period when
  non-automated trading increases."
- No CFTC table in these three papers reports a per-product number for 6A, M6E or M6A; the E-micro subgroup figure
  (ATS 70.9% of volume, 2016-11..2018-10) is the closest for M6E and M6A, and the G10 subgroup (ATS 85.4%) for 6A.

### F6. Positions by trader type: CFTC Traders in Financial Futures (TFF), futures only

Files: cftc_fut_fin_txt_2022.zip, cftc_fut_fin_txt_2023.zip (CFTC historical compressed TFF, futures-only); script
work/A1_fx/A1_fx_cot.py, output work/A1_fx/A1_fx_cot_out.txt. Window: the 53 weekly reports 2022-11-01..2023-10-31.
Share = (long + short + 2 x spread) / (2 x open interest) for each TFF category; the five categories sum to 100%.

| CFTC market (code) | Mean OI | Dealer/Intermediary | Asset Manager/Institutional | Leveraged Funds | Other Reportables | Nonreportable |
|---|---|---|---|---|---|---|
| EURO FX - CHICAGO MERCANTILE EXCHANGE (099741) = 6E | 745,734 | 34.7% | 40.3% | 11.9% | 3.9% | 9.2% (range 8.5-10.3) |
| AUSTRALIAN DOLLAR - CHICAGO MERCANTILE EXCHANGE (232741) = 6A | 167,984 | 21.0% | 42.9% | 20.9% | 0.9% | 14.3% (range 11.3-17.9) |

Mean number of reportable traders: 301 (Euro FX), 90 (AUD). The TFF has no commercial-hedger category; the closest
are Dealer/Intermediary (sell-side banks) and Asset Manager/Institutional. Neither micro contract (M6E, M6A) appears
as its own market in either year's TFF file (the script listed every market name containing "EURO", "AUSTRAL" or
"MICRO"; the micro markets returned were Micro 10 Year Yield, Micro Bitcoin, Micro E-mini DJIA/Nasdaq-100/Russell
2000/S&P 500 and Micro Ether, and no micro FX market), so no position-based trader split exists for M6E or M6A. The 099741 open interest (about 0.75 million)
matches the full-size Euro FX contract; whether micro positions are aggregated into it is not stated in the file
[unverified].


### F1. Contract specifications (resumed 2026-10-21 05:12 PDT after a usage cut)

| Code | Name | Contract unit | Tick (outright, Globex) | Tick value | Rulebook ch. | Source file and quote |
|---|---|---|---|---|---|---|
| 6E | Euro FX (EUR/USD) futures | 125,000 EUR | 0.00005 USD/EUR | $6.25 | CME 261 | cme_rulebook_ch261_6E.txt (Wayback snapshot 2023-09-28) l.13-17: "The unit of trading shall be 125,000 Euro." / "minimum price fluctuations shall be in multiples of $.00005 per Euro, equivalent to $6.25 per contract" |
| M6E | E-micro / Micro EUR/USD futures | 12,500 EUR | 0.0001 USD/EUR | $1.25 | CME 292 | cme_old_specs_e-micro-euro.html.txt (Wayback 2021-04-20): "12,500 euros" / "0.0001 per euro = $1.25" / "CME Globex: M6E" / "Exchange Rulebook CME 292". cme_rulebook_ch292.txt (Wayback 2025-05-15) l.16-18: "The unit of trading shall be 12,500 Euro." / "Minimum price fluctuations shall be in multiples of $.0001 per Euro, equivalent to $1.25 per contract." Same tick in 2021 and 2025, so taken as unchanged over the pilot window (no change notice found) |
| 6A | Australian dollar (AUD/USD) futures | 100,000 AUD | 0.00005 USD/AUD | $5.00 | CME 255 | cme_rulebook_ch255_6A.txt (Wayback 2023 snapshot) l.16-17: "The unit of trading shall be 100,000 Australian dollars." / "minimum price fluctuations shall be in multiplies of $.00005 per Australian dollar, equivalent to $5.00 per contract" |
| M6A | E-micro / Micro AUD/USD futures | 10,000 AUD | 0.0001 USD/AUD | $1.00 | CME 291 | cme_rulebook_ch291.txt (Wayback 2025 snapshot) l.16-19: "The unit of trading shall be 10,000 Australian dollars." / "Minimum price fluctuations shall be in multiples of $.0001 per Australian dollar, equivalent to $1.00 per contract." |

Tick history note (6A): in January 2020 the 6A outright tick was still $.0001 ($10.00): cftc_cme_ptc011020_aud_algo.txt
l.193: "Minimum price fluctuations shall be in multiplies of $.0001 per Australian dollar, equivalent to $10.00 per
contract." By the Wayback snapshot of 2020-12-02 the spec page shows the half tick (cme_old_specs_australian-dollar.html.txt
l.65: "Outrights: 0.00005 USD per AUD increments ($5.00 USD)."). So the half tick predates the standard window and the
pilot window. Note that M6E and M6A ticks are 2 x the full-size tick in price terms (0.0001 vs 0.00005): one M6E tick
equals two 6E ticks in price.

Trading hours (all four, CME Globex): 6E, cme_old_specs_euro-fx.html.txt l.59 (Wayback 2021-01-21): "Sunday - Friday
5:00 p.m. - 4:00 p.m. (6:00 p.m. - 5:00 p.m. ET) with a 60-minute break each day beginning at 4:00 p.m. (5:00 p.m.
ET)"; 6A, cme_old_specs_australian-dollar.html.txt l.61: "Sunday – Friday 5:00 p.m. – 4:00 p.m. CT (with a 60-minute
break each day beginning at 4:00 p.m.CT)"; M6E, cme_old_specs_e-micro-euro.html.txt: "Sunday - Friday 5:00 p.m. - 4:00
p.m. CT with a 60-minute break each day beginning at 4:00 p.m. CT"; M6A, cme_old_specs_e-micro-australian-dollar.html.txt
(Wayback 2021-04-21): "Monday – Friday: 5:00 p.m. – 4:00 p.m. CT the next day, except on Friday – closes at 4:00 p.m.
and reopens Sunday at 5:00 p.m. CT." The 2026 Wayback copies of the new-style spec pages (cme_*_specs.html) hold the
field names only (values are loaded by script), so the 2021 pages are the latest rendered text found.

Listing cycles: 6E "Quarterly contracts (Mar, Jun, Sep, Dec) listed for 20 consecutive quarters and serial contracts
listed for 3 consecutive months"; M6E "Quarterly contracts (Mar, Jun, Sep, Dec) listed for 2 consecutive quarters";
6A "Contracts listed for the first 3 consecutive months and 20 months in the March quarterly cycle"; M6A "Two months in
the March quarterly cycle (Mar, Jun, Sep, Dec)". All physically delivered; trading terminates 9:16 a.m. CT two
business days before the third Wednesday of the contract month (6E page: "Trading terminates at 9:16 a.m. CT on the
second business day prior to the third Wednesday of the contract month.").

### F2. Matching algorithm (outrights)

- 6E outright: FIFO (CME Algorithm F). cftc_cme_rule071819_fx_spread_algo.txt (CME submission to CFTC, July 2019,
  effective trade date 2019-08-12) l.65-68: "CME is amending the CME Globex trade matching algorithm for all calendar
  spread transactions of FX contracts from Matching Algorithm C to Matching Algorithm K ... No changes are being made to
  the CME Globex trading matching algorithm for outright transactions in the Contracts." Table l.94: "6E 6E Outright F
  F"; l.96 "6E-6E 6E SD C K".
- 6A outright: FIFO (Algorithm F). cftc_cme_ptc011020_aud_algo.txt (filed 2020-01-09) l.77-78: "No changes are being
  made to the CME Globex trading matching algorithm for outright transactions of the Contracts."; table l.109: "AUD/USD
  Futures 6A 6A Outright F F"; l.110 "6A-6A 6A SD C K" (calendar spreads split FIFO/pro rata).
- What F means: cme_wiki_matching_algorithms.html.txt (CME client wiki) l.77: "Distribute quantity to resting orders
  in FIFO order."
- M6E, M6A outright: no product-level source found (CME client wiki page lists algorithms, not products; Databento's
  blog lists algorithm types only). Value null; searched: CFTC filings for E-micro FX, CME client wiki, Databento blog.
  Both filings above are dated 2019-2020; no later change notice was found, but none was specifically searched for
  after 2020 [unverified for 2023-24].

### F3. Market-maker and incentive programs

- FX Micros Market Maker Program (M6A, M6E and other micros), in force across the standard and pilot windows.
  cftc_cme_rules0901235937_fx_mm_2023.txt (CME notice to CFTC, effective 2023-10-01) Exhibit 1: "Product Scope Micro
  AUD/USD Futures (“M6A”), Micro GBP/USD Futures (“M6B”), Micro USD/CAD Futures (“M6C”), Micro EUR/USD Futures
  (“M6E”), ..." ; "Program Term Start date is August 1, 2021. End date is September 30, 2023 March 31, 2024." (the
  underlined new date is March 31, 2024); "Participants must quote continuous two-sided markets in the Products at
  maximum bid/ask spreads and minimum quote sizes during a certain percentage of time-in-market."; "There is no limit
  to the number of participants in the Program." The 2024 filing (cftc_cme_rules0808244211_fx_mm_2024.txt l.137)
  extends it: "Start date is August 1, 2021. End date is August 31, 2024 August 31, 2025."
- Predecessor programs: FX Futures Market Maker Program (cftc_cme_rule091719_fx_mm_2019.txt, effective 2019-10-01):
  "The following CME FX E-micro futures products available for trading on the Globex® Platform (“Products”): AUD/USD,
  CAD/USD, CHF/USD, EUR/USD, GBP/USD, and JPY/USD." and "Start date is September 1, 2008. End date is January 31,
  2020." Its full-size scope lists crosses and emerging-market pairs only (EUR/AUD, EUR/CAD, ..., PLN/EUR), not EUR/USD
  (6E) or AUD/USD (6A). CME E-Micro FX Market Maker Program (cftc_cme_rule120816_emicro_mm_2016.txt, effective
  2017-01-01).
- 6E and 6A (full size): no market-maker or incentive program found (searched CFTC filings, WebSearch-5 and -6 in log.tsv; results covered crosses, EM pairs, an Asia FX program for CNH/KRW/INR and a bank fee program, the Asia-Pacific Incentive Program [snippet only]). Value null.

### F4. Daily price limits and circuit breakers

- No daily price limit is documented for these FX futures; they carry CME Rule 589 dynamic price fluctuation limits
  (two-minute halts), not limit-up/limit-down days. 6E and 6A were moved to dynamic limits on trade date 2021-07-12:
  cftc_cme_ptc062121_fx_dcb.txt (CME submission 21-204) l.77-80: "to apply dynamic price fluctuation limits to certain
  CME foreign exchange (“FX”) futures ... (effective on trade date Monday, July 12, 2021)"; table l.88 "Euro FX Futures
  261 6E / EC" and l.92 "Australian Dollar Futures 255 6A / AD"; mechanism l.159-163: "the dynamic variant will be
  utilized in rolling 60 minutes look-back periods to establish dynamic upper and lower price fluctuation limits.
  Posted trades, bids or offers through the dynamic price fluctuation limits will trigger a two (2) minute trading
  halt." l.153: "The related associated futures and options contracts regarding the primary futures contracts noted
  above will also appear in the Table." Before 2021-07-12 "traditional special price fluctuation limits only apply to
  certain FX contracts" (l.175-176).
- All CME FX futures from trade date 2022-05-02: cftc_cme_ptc041222_fx_dcb.txt (submission 22-065) l.74-76: "effective
  on trade date Monday, May 2, 2022. Upon the effective date, dynamic price fluctuation limits shall apply to all CME FX
  futures contracts."
- The percentage variants for 6E/6A and whether M6E/M6A are listed as associated products are in the Table, which the
  filing says is "provided under separate cover" (l.667); not obtained [unverified]. The CME dynamic circuit breaker
  FAQ and price-limits pages returned Wayback 404 or timeouts (log rows cme_dcb_faq.html, cme_price_limits.html).
- Limit-hit or halt days 2019-2024: no published count found for 6E, 6A, M6E or M6A (no source searched lists
  FX dynamic-halt events by day). Value null. Large-move day counts (4-sigma) are A0's (A0_contract_stats.md lines
  125-128 give 6A and 6E by year; none for M6E/M6A).

### F7. Launch and listing (pilot-window eligibility)

- M6E and M6A: launched March 2009. cme_ser5311.html.txt (CME Market Regulation SER 5311 page, July 2010) l.51: "In
  March 2009, E-micro FX futures were listed for trading. The E-micro FX contracts have been successful, serving a need
  in the market place for retail customers looking to trade the FX asset class in a transparent, open market place.
  Initially the E-micro FX contracts were averaging over 5,500 contracts per day (around $70 million per day). This
  volume had leveled off at around 3,500 contracts per day (around $50 million per day) although more recently it has
  increased to 4,857 contracts per day." mv_cme_emicro_additional_2010.html.txt (CME release 2010-12-06, Mondo Visione
  reprint) l.27: "the six existing E-micro Forex futures contracts launched in 2009, which are quoted in interbank
  (European) terms"; the 2009-launch set included EUR/USD and AUD/USD [the six pairs are not listed in the fetched
  text; the 2019 MM filing lists AUD/USD and EUR/USD among the E-micros]. The contracts were re-specified to physical
  delivery and IMM (USD per foreign unit) terms from the December 2010 contract (SER 5311 title l.40: "E-MICRO FX
  FUTURES SWITCHING TO PHYSICAL DELIVERY BEGINNING WITH THE DECEMBER 2010 CONTRACT TO BE RELISTED ON JULY 25, 2010").
  Listed and quoted in the pilot window: the FX Micros Market Maker Program covered M6E and M6A on CME Globex through
  2024-03-31 and then 2025-08-31 (F3). No owned M6E/M6A file covers 2023-11..2024-02 (A0_contract_stats.md line 212).
- 6E and 6A: launch dates not found (CME FX history page, cme_fxhistory.html, has no product dates; a search found
  none) [launch date null]. Listed before 2023-11 and continuously since: CFTC TFF reports carry both every week in
  2022-11..2023-10 with mean open interest 745,734 (6E) and 167,984 (6A) (F6); CME rule filings of 2019-2022 name both
  (F2, F4); owned GLBX files exist for 6E from 2010-06-06 and 6A from 2019-05-01, including pilot-window months by file
  name (A0_contract_stats.md lines 162-165; not read here).

### F8. Published ADV (CME Group Exchange ADV Report, monthly)

Files: cme_adv_report_snap20230924.pdf/.txt (Wayback snapshot 2023-09-24 of
https://www.cmegroup.com/daily_bulletin/monthly_volume/Web_ADV_Report_CMEG.pdf, the "August 2023" report) and
cme_adv_report_snap20261011.pdf/.txt (snapshot 2026-10-11, the "September 2026" report). The 2023-12-18 snapshot
(the November 2023 report) was deliberately not fetched because it reports pilot-window volume. The report is the
exchange-wide ADV (all venues; it does not say Globex-only). Columns: month, same month prior year, % change, prior
month, % change, year to date, prior year to date, % change.

| Product (report row) | YTD 2023 (Jan-Aug) | YTD 2022 (Jan-Aug) | Aug 2023 | YTD 2026 (Jan-Sep) | YTD 2025 (Jan-Sep) | Sep 2026 |
|---|---|---|---|---|---|---|
| EURO FX (6E) | 223,555 | 227,222 | 181,181 | 227,726 | 237,823 | 317,270 |
| MICRO EUR/USD (M6E) | 30,128 | 35,780 | 26,200 | 23,742 | 36,978 | 17,296 |
| AUSTRALIAN DOLLAR (6A) | 93,860 | 97,935 | 83,581 | 120,862 | 101,374 | 134,033 |
| MICRO AUD/USD (M6A) | 13,103 | 12,441 | 13,000 | 7,384 | 11,030 | 4,356 |

Verbatim rows, 2023 file l.35: "EURO FX 181,181 218,188.48 -17.0% 198,201.7 -8.6% 223,555 227,222 -1.6%"; l.45: "MICRO
EUR/USD 26,200 36,258.87 -27.7% 28,910.4 -9.4% 30,128 35,780 -15.8%"; l.12: "AUSTRALIAN DOLLAR 83,581 87,592.17 -4.6%
90,273.3 -7.4% 93,860 97,935 -4.2%"; l.42: "MICRO AUD/USD 13,000 10,498.61 23.8% 13,824.35 -6.0% 13,103 12,441 5.3%".
2026 file l.31: "EURO FX 317,270 278,609.05 13.9% 138,686.19 128.8% 227,726 237,823 -4.2%"; l.41: "MICRO EUR/USD 17,296
32,474.48 -46.7% 12,815.29 35.0% 23,742 36,978 -35.8%"; l.12: "AUSTRALIAN DOLLAR 134,033 109,197.9 22.7% 72,461.38 85.0%
120,862 101,374 19.2%"; l.38: "MICRO AUD/USD 4,356 6,307.62 -30.9% 3,351.76 30.0% 7,384 11,030 -33.1%".

Notes: no published ADV for exactly 2022-11..2023-10 was obtained; YTD Jan-Aug 2023 is the closest pre-pilot figure.
Owned-bar ADV for 6E and 6A over 2022-11..2023-10 is A0's (A0_contract_stats.md l.88, l.91); A0 has no owned M6E/M6A
window. The latest twelve full months are not in one report; YTD Jan-Sep 2026 is the latest published figure.
Arithmetic (mine, from the rows above): YTD-2023 M6E ADV in 6E-equivalent notional is 30,128 x 12,500 / 125,000 = 3,013
6E contracts, 1.3% of 6E ADV; M6A is 13,103 x 10,000 / 100,000 = 1,310 6A equivalents, 1.4% of 6A ADV.
Early E-micro volume (all six E-micros together): SER 5311 (2010) "averaging over 5,500 contracts per day" initially, then
"4,857 contracts per day"; CME release 2010-12-06: "November E-micro Forex average daily volume was more than 7,800
contracts" (mv_cme_emicro_additional_2010.html.txt l.29).

Open interest: CFTC TFF mean OI 2022-11..2023-10 is 745,734 (6E) and 167,984 (6A) (F6). No OI source was found for M6E or
M6A (not separate TFF markets; the ADV report has no OI column; CME's OI pages are script-rendered). Value null.

### F9. Participants: retail, hedgers, small traders

- Retail: no numeric retail share was found for any of the four products (searched: CME releases on E-micro FX,
  CME micro-suite releases, CME investor/retail statements, Risk.net). Qualitative CME statements on the micros:
  mv_cme_emicro_launch_2009.html.txt (CME release 2009-02-18, reprint) title l.1: "CME Group to Launch Forex E-Micro
  Contracts - - Smaller Contract Size And Proportionally Reduced Margins Aimed To Attract Retail Participation"; l.26-28:
  "called Forex E-Micros, designed to enable retail traders and investors to cost-effectively access the security,
  transparency and liquidity of CME Group's FX products"; l.59-61: "one-tenth the size of the corresponding CME FX
  contracts, making them accessible to active individual traders, small" [CTAs and SMEs; line break]. cme_ser5311.html.txt
  l.51: "serving a need in the market place for retail customers looking to trade the FX asset class". CME release
  2010-12-06 l.26: "provide our retail customers with a product that has the right risk/reward ratio".
  fxnewsgroup_cme_micro_1bn.html.txt (reprint of a CME release on 1 billion Micro contracts) l.58: "Since the launch of its
  first Micro contracts – Micro FX in 2009 – CME Group has rapidly expanded these offerings"; l.59: "Micro equity
  contracts represent 87% (870 million) of the cumulative 1 billion Micro contracts traded." CME-wide (not FX):
  risknet_cme_exchange_innovation.html.txt l.325: "with 27% of its volumes coming from this contingent in 2018" (retail,
  all CME products).
- Manual (non-ATS) share as a proxy for non-professional flow: E-micro FX subgroup 33.7% (2012-14), 30.7% (2014-16),
  29.1% (2016-18) of volume manual; Euro FX (6E) 17.2% manual and 4.6% manual-on-both-sides in 2016-18 (F5). G10 FX
  subgroup (6A among them) 13.8% manual in 2016-18.
- Commercial hedgers: the TFF has no hedger category (F6). Dealer/Intermediary 34.7% (6E), 21.0% (6A); Asset
  Manager/Institutional 40.3% (6E), 42.9% (6A); Leveraged Funds 11.9% (6E), 20.9% (6A) of open interest,
  2022-11..2023-10.
- Nonreportable (small-trader proxy) share of OI: 9.2% (6E), 14.3% (6A) (F6). None for M6E/M6A (not separate markets).
- Trader-type link to price discovery (6E vs E-mini euro E7, 2010): Malhotra and Corelli (2021), Risks 9(6):111,
  abstract only via OpenAlex (openalex_10.3390_risks9060111_abstract.txt): "regular futures market contributes
  significantly to the price discovery, accounting for approximately 66.5% of price discovery in the EURO/USD market ...
  the IS of regular futures can be better explained by speculators than hedgers." [abstract only; mdpi.com answered 403
  and the Wayback copy 404]

### F10. Spreads, depth, queue and the spot market

- 6E spread: cme_fx_market_profile_usecase.html.txt (CME article on its FX Market Profile tool, data June 2021;
  Wayback 2025-10-20) l.57: "At the top of the book, outright FX futures have the tightest pricing (white line), at an
  average of around 0.6 pips." One pip is 0.0001, so 0.6 pips = 0.00006 = 1.2 ticks of 6E (tick 0.00005) [arithmetic
  mine; the article does not state ticks]. l.54: "The top of book (“TOB”) spreads for both EBS Market and CME futures
  are consistent throughout the trading day, and whilst Futures (the white line) are inside OTC Spot FX (the yellow
  line) for the whole day". l.58: "For the top of book, futures order size is low and rising through the trading day,
  while EBS Market order size is consistently high. Typically, around 33% more volume is available on EBS at the top
  of book until later in the day." The article gives no contract count at the touch. l.52 and l.54 imply the spread
  figure is time-weighted ("TOB Spread data is not volume weighted").
- 6E replenishment: cme_2024_fx_liquidity_speaks_volumes.html.txt (CME article, 2024) l.44: "Representing over 98% of
  global volume in EUR/USD futures and 97% USD/JPY futures, the FX futures central limit order book (CLOB) at CME
  Group"; l.47-48: "In a single second, $458M was executed, rising to close to $1B by 30 seconds and $1.5B by 120
  seconds." ($458M is about 2,900 6E contracts at EUR/USD near 1.08; arithmetic mine, rate assumed.)
- Liquidity-provision speed (6E, 2016-18): 14.0% of two-sided volume was passive ATS orders filled within 100 ms of
  placement, and only 9.9% rested over one minute (F5, Haynes and Roberts 2019 Table 6).
- 6A, M6E, M6A spreads and depth: no source found (searched CME FX Market Profile article, CME liquidity articles,
  CME 2010 Liquidity Monitor: Wayback 404). Value null. Structural fact: the M6E and M6A tick (0.0001) is one pip, twice
  the full-size tick, so the micro spread is at least 1 pip while 6E averaged about 0.6 pips in June 2021.
- Traded volume per minute and session split for 6E and 6A over the standard window are A0's (A0_contract_stats.md
  l.88, l.91: "Vol/min main median (mean)" 118 (195.2) for 6E, 46 (83.0) for 6A). No touch-size source exists here,
  so QV cannot be formed from published data.
- Overnight vs main-session spread: no published session split found for any of the four. CME's Market Profile article
  says spreads are "consistent throughout the trading day" for 6E (June 2021) but does not tabulate a ratio.
- Where price discovery happens:
  - Rosenberg and Traub, FRBNY Staff Report 262 (Oct 2006, rev. Feb 2008; J. Derivatives 2009), full text
    (rosenberg_traub_frbny_sr262.txt, abstract l.33-46): "the amount of information contained in currency futures
    prices in 1996 is much greater than one would expect based on relative market size. Using data from 2006, we
    obtain quite different results, perhaps because of an increase in spot market transparency. In particular, we find
    in our more recent sample that the spot market has the dominant information share."
  - Cabrera, Wang and Yang (2009), J. Futures Markets 29:137-156, abstract only via OpenAlex
    (openalex_10.1002_fut.20352_abstract.txt): "the spot market is found to consistently lead the price discovery
    process for both currencies during the sample period. Furthermore, E‐mini futures do not contribute more to the
    price discovery than the electronically traded regular futures." (Euro and yen; CME Globex regular, E-mini, EBS.)
    [abstract only]
  - Chen and Gau (2010), J. Banking & Finance, "News announcements and price discovery in foreign exchange spot and
    futures markets": title only (OpenAlex returned no abstract) [unverified; no finding quoted].
  - HFT across venues: bis_mktc05_hft_fx_2011.txt (BIS Markets Committee, Sept 2011) l.401-404: "HFT firms conduct
    their FX activities mainly on inter-dealer electronic broking platforms (EBS and Reuters, both London-based
    companies) and multi-bank electronic communication networks ... They are also active on the Chicago Mercantile
    Exchange (CME) for trades involving FX futures."; l.333-334: "Arbitrage could also be done across the spot and
    futures prices of the same currency pair."; l.670: HFT estimated at "about 24–30% of spot turnover".
  - CME's FX Link (a Globex spread between OTC spot and the future) ties the two: cme_6E_specs.html.txt l.66: "CME FX
    Link connects OTC FX and FX futures with one Globex spread".

### F11. Scheduled releases, weekend gap, jumps

- Product-specific scheduled releases (not the shared US macro calendar):
  - EUR/USD (6E, M6E): ECB monetary-policy decisions, eight per year. ecb_meeting_calendar.html.txt lists for 2027
    eight lines of the form "Governing Council of the ECB: monetary policy meeting in Frankfurt (Day 2), followed by
    press conference" (04/02, 18/03, 29/04, 10/06, 22/07, 09/09, 28/10, 16/12/2027). That is 8/52 = 0.15 per week.
    The 2019-2024 meeting count is not in the fetched page [the 8-per-year rhythm for earlier years is unverified].
  - AUD/USD (6A, M6A): RBA Monetary Policy Board decisions, eight per year in 2025 and 2026.
    rba_board_meeting_schedules.html.txt (Wayback 2025-03-05) lists for 2026 under "Monetary Policy Board": "2–3
    February", "16–17 March", "4–5 May", "15–16 June", "10–11 August 2026", "28–29 September", "2–3 November", "7–8
    December". The pre-2024 count (11 meetings a year) is [unverified, not fetched].
  - Other euro-area and Australian releases (euro-area flash HICP, PMIs, German Ifo/ZEW; Australian labour force, CPI,
    and Chinese activity data for AUD) are monthly or quarterly; no source was fetched for their dates or for a
    high-impact classification [unverified]. Even counting each monthly release, the sum is of the order of one per
    week per currency, not the two or more per week of the EIA inventory reports [count unverified].
- Weekend gap: Globex trades all four from Sunday 5:00 p.m. CT to Friday 4:00 p.m. CT (F1). The OTC spot market also
  closes over the weekend; broker and forum pages place its week from about Sunday 5 p.m. New York to Friday 5 p.m. New
  York (WebSearch-15 results: forexbrokers.com, tradermade.com, babypips forum), but these are pointers, not evidence,
  and no official (BIS, Federal Reserve, CLS) statement was found [unverified]. There is no 24/7 underlying of the
  crypto kind. The rule's weekend-gap fact for FX is therefore "no 7-day underlying documented"; any Sunday-open gap
  from weekend news is not quantified by any source found.
- Jumps: published per-product jump frequencies for 2019-2024 were not found. The 4-sigma day counts from owned bars
  are A0's: A0_contract_stats.md Table 2 l.128 (6E): "2019: 0/254, 2020: 1/255, 2021: 0/255, 2022: 0/254, 2023: 0/213";
  l.125 (6A): "2019: 0/170, 2020: 2/255, 2021: 0/255, 2022: 0/254, 2023: 0/213". No owned counts exist for M6E/M6A
  (same underlying as 6E/6A).

### F12. Published microstructure research on the products or close cousins

Search effort: 19 WebSearch calls in total (of 40), OpenAlex (11 queries, work/A1_fx/A1_fx_oa1.txt, A1_fx_oa2.txt);
the arXiv API answered 503 every time. No study was found that tests order-flow imbalance, queue imbalance or
trade-sign predictability, or passive market-making profitability net of costs, on 6E, M6E, 6A, M6A or their E-mini
(E7) versions. Studies found, with their relation to the products and their result for the C6 question:

| Study | Relation | Topic | Result for short-horizon OB predictability / passive MM | Evidence level |
|---|---|---|---|---|
| Haynes and Roberts (CFTC 2015, 2017, 2019) | same products (6E per product; micros as a group) | ATS shares, passive resting times | not a predictability test; documents fast automated liquidity provision (14.0% of 6E volume passive ATS filled within 100 ms, 2016-18) | full text (F5) |
| Rosenberg and Traub (FRBNY SR 262; J. Derivatives 2009) | same products (CME currency futures, pit-era order flow, 1996 and 2006) | price discovery, order flow | futures order flow carried information in 1996; by 2006 "the spot market has the dominant information share" | full text |
| Cabrera, Wang and Yang (JFM 2009) | same product (Euro on Globex regular and E-mini) and EBS spot | price discovery | spot EBS leads; E-mini adds nothing over regular | abstract only |
| Malhotra and Corelli (Risks 2021) | same product (6E vs E-mini euro, 2010) | price discovery, trader types | 6E has about 66.5% information share | abstract only |
| Aidov and Lobanova (JRFM 2021) | asset class incl. FX futures (contracts not named in the abstract) | depth vs volatility | depth falls as volatility rises; not a predictability test | abstract only |
| Martinez and Tse (FRL 2019, 28:32-38) | same product (euro future) plus yen and peso futures | tick-size reductions | "significant evidence of increased market quality for the Mexican peso contracts, but less significant evidence for the other two contracts" | abstract (IDEAS page, ideas_martinez_tse_2019_tick_fx_futures.html.txt l.51) |
| Andersen, Bondarenko, Gousgounis, Onur (J. Econometrics 2026, 106165) | CME FX futures, tick data (currencies not named in the abstract) | trading invariance: spread, depth, intensity around tick cuts | not a predictability test; depth and trading intensity adjust to tick cuts | abstract (kellogg_fx_futures_invariance.html.txt l.192) |
| Chaboud, Chiquoine, Hjalmarsson, Vega (FRB IFDP 980; JF 2014) | asset class (EBS spot EUR/USD, USD/JPY, EUR/JPY, 2006-07) | algorithmic trading | algorithmic trades correlated; no causal link to volatility; algorithms supply liquidity after releases | full text (abstract read) |
| BIS Markets Committee (2011) | asset class (spot FX, with mention of CME futures) | HFT | HFT about 24-30% of spot turnover; spot-futures arbitrage named as an HFT strategy | full text |
| Rambaldi, Pennesi, Lillo (2015) | asset class (spot FX around news) | Hawkes activity models | not read here; pointer from C2_Hawkes.md l.1028 | [unverified] |
| Stenfors and Susai (spot EBS, limit order cancellations) | asset class | order informativeness | algorithmic-looking limit orders "perceived to be more informed or predatory" | search snippet only [unverified] |

Added after WebSearch-20 (same F12 table, continued):

| Study | Relation | Topic | Result for short-horizon OB predictability / passive MM | Evidence level |
|---|---|---|---|---|
| Chen (An-Sing) et al., EFMA 2009 paper 0102, "Momentum and Reversals in Weekly Euro FX Futures Returns during Periods of Extreme Trading Imbalance" | same product (6E, CME, 1999-12-17..2005-03-04) | trade imbalance vs weekly returns | weekly horizon, not short-horizon: "Standard regression analyses do not show any significant dynamic relation between weekly returns and trading imbalance ... However, when the analyses are focused on periods with extreme imbalance levels, we find weekly returns in Euro FX futures exhibit significant reversals following periods of extreme (negative) trade imbalances ... economically significant, even after accounting for transaction costs." (efma2009_0102_euro_fx_trade_imbalance.txt l.35-47) | full text; conference paper |
| Kao and Fung (Int. Rev. Econ. & Finance 21(1), 2012, 195-209) | same product (euro FX futures on GLOBEX) plus yen and E-mini S&P | volume, trade imbalance and intraday volatility | not a return-predictability test: "the net effect of trading imbalance is negative, supporting the asymmetrical information hypothesis" (on volatility) | abstract (ideas_kao_fung_2012.html.txt l.51) |
| Rentzler, Tandon and Yu (JFM 26(11), 2006, 1089-1130) | same products (seven CME currency futures, 1988-2003) | intraday reversals after large 1-day moves and opening gaps | daily-to-intraday, not order-book: "Significant intraday price‐reversal patterns are observed in five of the seven currency futures contracts" and GLOBEX in 1992 made the markets "fairly efficient", with renewed patterns after 1999 | abstract (ideas_rentzler_2006_jfm.html.txt l.50) |
| "The information effect of order flows in foreign currency futures and spot markets" (JFM 2022 per the search summary; NCU scholars page) | same products (EUR-USD and JPY-USD futures and spot, intraday) | order flow and price discovery | search summary says "the futures market dominates price discovery when compared with the spot market" | search snippet only; page fetch timed out [unverified] |

Not relevant after checking (recorded so they are not re-read): arXiv 2408.03594 (OFI forecasting with Hawkes, NSE
India data), arXiv 1402.6583 (Russian futures), Baule, Frijns, Schlie (JFM 2024, German retail derivatives).

## Per-candidate fact sheets

Each line points to the family section holding the source file and the verbatim quote. "null" means not found,
with the search recorded there. The same facts, field by field with source file, quote and note, are in A1_fx.json
(written by work/A1_fx/A1_fx_build_json.py; every quote in it was re-checked verbatim against its saved file by
work/A1_fx/A1_fx_check_quotes.py: 105 quotes checked, 0 not found).

### M6E: Micro EUR/USD futures (E-micro EUR/USD)
- Contract: 12,500 EUR; tick 0.0001 USD/EUR = $1.25 (twice the 6E price tick); CME ch. 292 (F1).
- Launched March 2009; listed through the pilot window (FX Micros MM Program on Globex to 2024-03-31, then 2025-08-31);
  no owned file for the window (F7).
- Matching algorithm: null (F2). Daily limit: none; dynamic 2-minute halts; micro coverage unverified (F4). Limit-hit days: null.
- Published ADV: 30,128 (Jan-Aug 2023), 35,780 (Jan-Aug 2022), 23,742 (Jan-Sep 2026) (F8). OI: null.
- Retail: CME calls the E-micros retail products; no numeric share (F9). Manual share of E-micro FX group 29.1%
  (2016-18) (F5). TFF: not a separate market (F6).
- MM program: yes, FX Micros Market Maker Program with maximum spreads and minimum sizes (F3).
- Spread, depth, queue, volume per minute: null; tick = 1 pip vs 6E's ~0.6-pip average spread (F10).
- Releases: ECB about 0.15 per week; other monthly releases unsourced (F11). Weekend gap: no 7-day underlying (F11).
  Jumps: same underlying as 6E (A0 counts for 6E) (F11).
- Research: nothing on M6E itself; on 6E (full size) only price-discovery, weekly-imbalance and tick-size studies;
  no OFI or queue-imbalance or passive-MM study found (F12).

### 6E: Euro FX futures
- Contract: 125,000 EUR; tick 0.00005 USD/EUR = $6.25; CME ch. 261 (F1). Launch date null; continuously listed (F7).
- Matching: FIFO (Algorithm F) for outrights, calendar spreads Algorithm K, from 2019-08-12 (F2).
- Daily limit: none; dynamic price fluctuation limits from 2021-07-12 (F4). Limit-hit days: null.
- Published ADV: 223,555 (Jan-Aug 2023), 227,726 (Jan-Sep 2026) (F8); owned window ADV and volume per minute from A0.
  OI: mean 745,734 (TFF, 2022-11..2023-10) (F6).
- Participants (TFF OI shares, 2022-11..2023-10): Dealer 34.7%, Asset Manager 40.3%, Leveraged Funds 11.9%, Other 3.9%,
  Nonreportable 9.2% (F6). ATS 82.0% of volume, ATS-ATS 69.4%, manual-manual 4.6% (2016-18) (F5). Retail: null (F9).
- MM program: none found for the outright (F3).
- Spread: about 0.6 pips = 1.2 ticks average at the top of book, June 2021, time-weighted (F10). Touch size: null.
  Liquidity provision is fast: 14.0% of volume passive ATS filled within 100 ms; 9.9% rested over one minute (F5).
- CME has over 98% of global EUR/USD futures volume; spot EBS led price discovery in 2006-era studies (F10).
- Releases: ECB about 0.15 per week (F11). Weekend gap: no 7-day underlying (F11). Jumps: A0 4-sigma days 0-1 per year.
- Research: same-product studies on price discovery (Cabrera et al.; Malhotra and Corelli; Rosenberg and Traub),
  weekly trade-imbalance reversals (EFMA 2009, weekly horizon), imbalance vs volatility (Kao and Fung), tick-size
  cut (Martinez and Tse), trading invariance (Andersen et al. 2026); no short-horizon OFI, queue-imbalance or net
  passive-MM study found (F12).

### M6A: Micro AUD/USD futures (E-micro AUD/USD)
- Contract: 10,000 AUD; tick 0.0001 USD/AUD = $1.00 (twice the 6A price tick); CME ch. 291 (F1).
- Launched March 2009; listed through the pilot window (FX Micros MM Program to 2024-03-31, then 2025-08-31) (F7).
- Matching algorithm: null (F2). Daily limit: none; dynamic halts; micro coverage unverified (F4).
- Published ADV: 13,103 (Jan-Aug 2023), 12,441 (Jan-Aug 2022), 7,384 (Jan-Sep 2026) (F8). OI: null.
- Retail: CME calls the E-micros retail products; no numeric share (F9). Manual share of the E-micro FX group 29.1% (F5).
- MM program: yes, FX Micros Market Maker Program (F3).
- Spread, depth, queue, volume per minute: null (F10).
- Releases: RBA 8 per year (about 0.15 per week) in 2025-26 (F11). Weekend gap: no 7-day underlying. Jumps: as 6A.
- Research: nothing on M6A or 6A specifically beyond multi-contract CME currency-futures studies (F12).

### 6A: Australian dollar futures
- Contract: 100,000 AUD; tick 0.00005 USD/AUD = $5.00 (half tick since 2020; $10.00 in January 2020); CME ch. 255 (F1).
- Matching: FIFO (Algorithm F) for outrights; calendar spreads Algorithm K from 2020-01-27 (F2).
- Daily limit: none; dynamic price fluctuation limits from 2021-07-12 (F4).
- Published ADV: 93,860 (Jan-Aug 2023), 120,862 (Jan-Sep 2026) (F8); owned window figures from A0. OI: mean 167,984 (F6).
- Participants (TFF OI shares): Dealer 21.0%, Asset Manager 42.9%, Leveraged Funds 20.9%, Other 0.9%, Nonreportable
  14.3% (F6). ATS share: G10 FX subgroup 85.4% (2016-18), no per-product figure (F5). Retail: null.
- MM program: none found for the outright (F3).
- Spread, depth, queue: null (F10).
- Releases: RBA about 0.15 per week (F11). Weekend gap: no 7-day underlying. Jumps: A0 4-sigma days 0-2 per year.
- Research: no study on 6A order-book predictability found; CME currency-futures multi-contract studies only (F12).

## Not finished or not verified

- No numeric retail share for any of the four; no spread, depth or touch size for 6A, M6E, M6A; no session spread
  split for any; no OI for the micros; no matching algorithm for the micros; no limit-hit or halt-day counts.
- 6E and 6A launch dates not found (listing before 2023-11 is established).
- Percentage variants of the FX dynamic limits, and whether M6E/M6A are associated products, not obtained (Table
  filed "under separate cover").
- Several studies are abstract-only (Cabrera et al.; Malhotra and Corelli; Aidov and Lobanova; Martinez and Tse; Kao
  and Fung; Rentzler et al.; Andersen et al. 2026); one is snippet-only (the NCU/JFM 2022 order-flow paper; page
  fetch timed out); MDPI answered 403 and Wayback 404/429 for its pages; arXiv API answered 503.
- WebSearch calls used: 20 of 40 (2 before the usage cut returned the session-limit notice).
