# Stage E.21 Step 1: published post-2010 evidence (SpecReaderPost2010)

Reader: SpecReaderPost2010 (opus). Started 2026-10-14T03:13:30-07:00. Report written about 03:30-07:00.
Evidence folder: reports/stage_e21_briefs/pages/SpecReaderPost2010/ (fetch_log.md has one row per fetch, failures
included). Repo files reused from E.13 are cited by path and were not fetched again. No program market data was read.
Both computations below use published external spreadsheets only.

Everything here is evidence that sits beside the E.21 verdicts (F6). None of it is a parameter choice. Section 5
has one presentation PROPOSAL for the lead.

## 1. Published post-2010 figures: futures trend-following / TSMOM

Gross = before transaction costs and fees. Net = after them (the row says which). SR = annualized Sharpe ratio.
Rows marked "computed" come from a published file using the formula in section 2.

| # | Source | Period | Universe | Net / gross | Sharpe or mean | Verbatim quote | File |
|---|---|---|---|---|---|---|---|
| P1 | AQR TSMOM factor (MOP 2012 update), computed here (A1) | 2010-07..2024-02 (164 months) | AQR's MOP universe (all assets) | gross (file: "excess returns"; it deducts no costs or fees) | SR 0.389, mean 5.31%/yr, vol 13.65%, t 1.44 | "This file contains the excess returns of the long/short Time Series Momentum (TSMOM) factors." | reports/stage_e13_briefs/pages/TrendCarry/aqr_tsmom_factors_monthly.xlsx |
| P2 | Same, computed here (A1) | 2010-01..2026-05 (197 months, the file's last month) | same | gross | SR 0.402, mean 5.25%, vol 13.06%, t 1.63 | "The TSMOM factor here is a 12-month time series momentum strategy with a 1-month holding period." | same |
| P3 | Same file, E.13 computation | 2010-01..2025-12; 2012-01..2025-12 | same | gross | SR 0.34 (t 1.37); SR 0.31 (t 1.18) | E.13 table: "2010-01..2025-12 \| 192 \| 4.48% \| 13.11% \| 0.34" | reports/stage_e13_trend_carry.md lines 43-44 |
| P4 | SG Trend Index from AQR's fund workbook, computed here | 2010-07..2024-02 (164 months) | about 10 largest trend CTAs (SG definition, E.13 T-07) | net of fees and costs | SR 0.352, excess mean 4.03%/yr, vol 11.46%, t 1.30 | column header in the workbook: "SG Trend Index" (E.13 T-05) | reports/stage_e13_briefs/pages/TrendCarry/aqmix_trackrecord.xls |
| P5 | SG Trend Index, E.13 computation (reproduced here: 0.237, n 192) | 2010-01..2025-12; 2010-2019; 2013-2025; 2020-2025 | same | net | SR 0.24; 0.14; 0.30; 0.40 | E.13: "SG Trend Index \| 2010-2025 \| 3.50% \| 11.33% \| 0.24" | reports/stage_e13_trend_carry.md lines 93-96 |
| P6 | Babu, Levine, Ooi, Schroeder, Stamelos, "You Can't Always Trend When You Want", JPM (March 2020) | 2010-01-01..2018-12-31 | SG Trend Index | net (live index) | SR 0.05 (versus 0.28 for 2000-2018) | "From January 1, 2010, through" / "December 31, 2018, the SG Trend Index realized an annualized" / "Sharpe ratio of 0.05, versus a Sharpe ratio of 0.28 from the incep-" (split at PDF line breaks) | reports/stage_e13_briefs/pages/TrendCarry/aqr_cant_always_trend_jpm.txt lines 136-138 |
| P7 | Same paper, own backtest | 2010-2018 decade | 67-market HOP trend (1/3/12m) | "net of estimated transaction costs, and gross of fees" | Decade Sharpe values are in image exhibits (Exhibits 4, 7, 8). The text layer has no numbers. UNSOURCED. | "The Sharpe ratios are based on the hypothetical trend-following strategy backtest, net of estimated transaction costs, and gross of fees." | same file, line 767 |
| P8 | AQR, "Trend-Following: Why Now? A Macro Perspective" (Fourth Quarter 2022) | 2010-2019; 2000-01..2022-09 | SG Trend Index | net (live index) | 2010-2019: total return 1.8%/yr, vol 11.3% (no Sharpe given for the decade). 2000-2022/09: SR 0.4. | "2000 - 2009 2010 - 2019 2020 - Present Full Sample" / "SG Trend Index Return (Annl.) 8.2% 1.8% 17.9% 6.4%" / "SG Trend Index Realized Volatility 16.1% 11.3% 11.0% 13.6%"; "(Sharpe ratios of 0.4 versus 0.3 for" / "the SG Trend Index and 60/40, respectively)" | pages/SpecReaderPost2010/aqr_trend_why_now_2022.txt lines 70-90 |
| P9 | Hurst and Ooi, "Trend Following and Rising Rates" (AQR, dated May 2015; the URL says 2023). This is the only post-2010 HOP-strategy figure found. | 2010-01..2013-04 | HOP century strategy (1/3/12m, 10% vol target) | net of 2/20 fees and estimated transaction costs | return 6.2%/yr, vol 7.7%, SR 0.80 | "Jan 2010–Apr 2013 -215 bps 6.2% 7.7% 0.80 -0.18 0.16" (columns: change in 10Y yield, net-of-2/20 return, realized vol, Sharpe, equity corr, bond corr); "The Hypothetical Trend-Following Strategy performance is a backtest net of 2/20 fees and estimated transaction costs." | pages/SpecReaderPost2010/aqr_trend_rising_rates_2023.txt lines 94-118 |
| P10 | Babu, Levine, Ooi, Pedersen, Stamelos, "Trends Everywhere", JOIM 18(1), 2020 | 1985-01..2017-12 (no post-2010 subperiod reported) | 58 traditional futures/forwards plus alternative assets and equity factors | gross of costs | 12m TSMOM SR: traditional 1.17, alternative 1.34, factors 0.95, combined 1.60 | "Over our sample period, the gross Sharpe ratio" / "of 12-month time series momentum for tradi-" / "tional assets is 1.17"; "This figure shows the gross Sharpe ratio of time series momentum by asset and factor, from 1985 to 2017." | pages/SpecReaderPost2010/aqr_trends_everywhere_joim.txt lines 80-88, 334 |
| P11 | Huang, Li, Wang, Zhou, "Time series momentum: Is it there?", JFE 135 (2020) | 1985-01..2015-12 (no post-2010 subperiod found by grep) | 55 assets | gross | No post-2010 figure. Critique: TSM is about the same as a sample-mean strategy. | "sample period is from January 1985 to December 2015." (also E.13 lines 128-133) | reports/stage_e13_briefs/pages/TrendCarry/hlwz_w717.txt line 162 |
| P12 | Kim, Tse, Wald, "Time series momentum and volatility scaling", JFM 30 (2016) | 1985-2013, subperiod 2009-2013 | 55 futures | not stated in the quoted text | No magnitude for 2009-2013. Qualitative: the TSMOM edge "vanishes" after the crisis and does worse than buy-and-hold. | Quoted by Quantpedia from the paper: "We also examine the results for several sub-periods: pre and post-2001, and following the financial crisis, 2009-2013." ... "When we use more recent periods, we find that the performance of TSMOM is worse than that of a buy-and-hold strategy." Bepress abstract: "The superior performance of the time series momentum strategy also vanishes in the more recent post-crisis period of 2009 to 2013." | pages/SpecReaderPost2010/quantpedia_ktw.txt lines 23-30; ktw_bepress.html. Full text [unverified] (see section 4) |
| P13 | Lim, Zohren, Roberts, "Enhancing Time-Series Momentum Strategies Using Deep Neural Networks" (arXiv v3, 27 Sep 2020; JFDS 2019) | 1995-2015 out-of-sample (mostly before 2010) | 88 continuous futures | gross, then with costs | MOP sign benchmark "Sgn(Returns)": SR 1.192 raw, 1.392 rescaled to 15% vol, 0.861 at c = 10 bp | Exhibit 2 row "Sgn(Returns) 0.054 0.046 0.032 0.083 1.192 ..."; Exhibit 8 (c = 10bps) row "Sgn(Returns) 0.133 0.154* 0.102* 0.373 0.861 ..." | pages/SpecReaderPost2010/lim_zohren_roberts_2019_arxiv.txt lines 555, 586, 768 |

What the figures say together:
- Every live or post-publication trend record after 2010 has a Sharpe between 0.05 and 0.40: SG Trend net, 0.05 for 2010-2018 and 0.24-0.35 depending on the window; the AQR TSMOM factor gross, 0.31-0.40.
- None of these is significant at t > 2. The largest t is 1.63 (P2).
- The only figure above 0.5 is P9 (0.80, 2010-01..2013-04). It is a backtest inside HOP's own sample, which ends in 2013, so it is not post-publication evidence.
- No HOP post-publication update with numbers in text was found. The JPM 2017 table (to 2016) is an image (E.13 line 59) and the 2018 AQR note was not retrieved (section 4).

## 2. A1 computation (AQR TSMOM factor, published data)

- Input: reports/stage_e13_briefs/pages/TrendCarry/aqr_tsmom_factors_monthly.xlsx. E.13 fetched it as F39 (2026-10-03,
  https://www.aqr.com/-/media/AQR/Documents/Insights/Data-Sets/Time-Series-Momentum-Factors-Monthly.xlsx).
  sha256 33470930e2269c0d97be4732ec2d9c27ddbc69ac8133b059a263e27400263eeb, checked again today.
- The file runs from 1985-01-31 to 2026-05-29 (497 monthly rows). That is past 2024-02, so it was not downloaded
  again, as the brief says.
- Sheet and column: sheet "TSMOM Factors", header row 18, column "TSMOM" (the diversified all-asset factor). The
  per-class columns TSMOM^CM/EQ/FI/FX are shown below for reference.
- The values are monthly excess returns: the file says "This file contains the excess returns of the long/short Time
  Series Momentum (TSMOM) factors." No T-bill is subtracted again.
- Formula: SR = mean(r_m) / sd(r_m, ddof=1) x sqrt(12), with r_m the monthly excess return. Also mean_ann = 12 x mean,
  vol_ann = sd x sqrt(12), t = mean / (sd / sqrt(n)). Windows include both end months.
- Script: /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/13fe2d4e-086f-4929-8325-9ef707bdf0cf/scratchpad/SpecReaderPost2010/a1_tsmom_sharpe.py
  (sha256 6f7a8eb40f2165216b21ad5d11f0de0e981ae89cf8c92cb9b7a341bbee8d43da). Run with
  `uv run --no-project --with openpyxl python -I a1_tsmom_sharpe.py <xlsx>`.
- Check: the script gives 1985-01..2009-12 SR 1.411 (t 7.06). This matches E.13's 1.41.

| Window | n | Column | Mean/yr | Vol/yr | Sharpe | t |
|---|---|---|---|---|---|---|
| 2010-07..2024-02 | 164 | TSMOM | 5.31% | 13.65% | **0.389** | 1.44 |
| 2010-01..2024-02 | 170 | TSMOM | 5.18% | 13.63% | 0.380 | 1.43 |
| 2010-01..2026-05 (last month in file) | 197 | TSMOM | 5.25% | 13.06% | **0.402** | 1.63 |
| 2010-07..2024-02 | 164 | CM / EQ / FI / FX | 2.40 / 0.00 / 15.51 / 4.08% | 16.46 / 25.78 / 30.62 / 18.14% | 0.146 / 0.000 / 0.506 / 0.225 | 0.54 / 0.00 / 1.87 / 0.83 |
| 2010-01..2026-05 | 197 | CM / EQ / FI / FX | 2.92 / 2.34 / 13.25 / 3.44% | | 0.182 / 0.089 / 0.454 / 0.190 | |

SG Trend Index over the same windows. This is an extra, computed with the same formula on (SG Trend - ICE BofA 3M
T-bill) monthly from reports/stage_e13_briefs/pages/TrendCarry/aqmix_trackrecord.xls, sheet "Monthly Returns", columns
"SG Trend Index" and "ICE BofA US 3M T-Bill Index". Script: .../SpecReaderPost2010/sg_trend_sharpe.py (sha256
288f4f08dbe89dcb88a8b658e9655e614cd21af786fcb45f3f669cb84848cd57).
- 2010-07..2024-02: n 164, SR 0.352, t 1.30.
- 2010-01..2024-02: SR 0.324.
- 2010-01..2025-12: SR 0.237, which reproduces E.13's 0.24.

Comparability caveats (facts, not decisions):
- These are monthly Sharpe ratios. E.21 F6 uses daily x sqrt(252).
- AQR's factor covers MOP's 58-market universe. E.21 covers 17 US roots.
- P1/P2 are gross. E.21 is net of D8 costs.
- The AQR file says "AQR reconstructs the full history each time the returns are updated", so later downloads can differ.

## 3. Turn-of-month (TOM) evidence in equity INDEX FUTURES with samples past 2010

Main finding (negative): no peer-reviewed study was found that measures TOM on ES, NQ or RTY futures prices with a
sample running past 2010.
- Searches: 9 WebSearch queries aimed at TOM in futures, plus 3 OpenAlex queries (publications from 2012 on, saved in
  the scratch folder).
- Peer-reviewed futures studies found end in 2008 (Carchano and Pardo) or 2011 (Floros and Salvador; abstract only,
  and it does not say TOM was tested).
- Cash-index TOM belongs to SpecReaderTOM and is not repeated here.

| Source | Data / sample | Instrument | TOM definition | Magnitude (bp/day) | Costs | Verbatim quote | File / status |
|---|---|---|---|---|---|---|---|
| ATB Research (Substack, "The Turn-of-the-Month Effect, Tested on Current Data", Jul 27, 2026). Practitioner post, not peer-reviewed. | 60-minute futures bars, ES from 1997 (also GC from 2002, US from 2001), to 2026 | ES (S&P 500 E-mini) | last trading day + first 3 trading days | Not in the text; the result tables are images. UNSOURCED. | No mention of costs (grep for cost, commission, slippage) | "None of these results are statistically significant. Every p-value sits well above 0.05. Worse, in ES and the bond, the TOM window actually underperforms the rest of the month."; "ES's TOM edge has decayed to essentially zero and gone negative in the most recent decade, while the rest of the month has been strongly positive" | pages/SpecReaderPost2010/atb_tom_tested.txt lines 12-20 |
| Carchano and Pardo, "Calendar Anomalies in Stock Index Futures" (2011). Context only: the sample ends before 2010. | daily, Dec 1991..Apr 2008 | S&P 500 futures (also DAX, Nikkei) | "+1": buy at the close of the last trading day, sell at the close of the next | not given in the CXO summary | 0.05% round trip | CXO summary (secondary): "Turn-of-the-month effect in S&P 500 futures generated 27.5% net cumulative profit (Dec 1991–Apr 2008; +1 day strategy with 0.05% round-trip costs; only 1 of 188 calendar effects persistent across subperiods)." | pages/SpecReaderPost2010/cxo_index_futures_calendar.txt lines 63-73. Paper full text not retrieved: [unverified] |
| Floros and Salvador, "Calendar anomalies in cash and stock index futures: International evidence", Economic Modelling 37 (2014) 216-223 | daily, 2004-2011 | S&P500 and Nasdaq100 futures (also FTSE100, FTSE/ASE-20) | "monthly seasonal effects"; whether TOM itself is tested is [unverified] | none in the abstract | not stated | "We consider daily data from FTSE100 (UK), FTSE/ASE-20 (Greece), S&P500 (US) and Nasdaq100 (US) spot and future indexes over the period 2004–2011."; "Calendar effects are also conditioned to the market situation. During a low volatile situation these calendar effects tend to be positive, but these effects turn negative if the market is under a high volatile period." | pages/SpecReaderPost2010/ideas_floros_salvador_2014.txt line 65 (abstract only; full text paywalled) |
| Etula, Rinne, Suominen, Vaittinen, "Dash for Cash", RFS 33(1) 2020. Not a futures-return study. | | cash markets | month-end payment cycle | | | Relevant only for mechanism: "we find that funds in managed futures and global macro" (provide month-end liquidity; lines 717-718) | pages/SpecReaderPost2010/etula_dash_for_cash_rfs.txt. Left to SpecReaderTOM. |
| Boyarchenko et al., NY Fed Staff Report 917 ("The Overnight Drift") | E-mini intraday | ES | | | | Non-finding: grep for turn-of-the-month, month-end and calendar found no TOM analysis | pages/SpecReaderPost2010/nyfed_sr917_overnight_drift.txt |

The search also turned up two pre-2010 futures results. Neither was retrieved and both are [unverified]:
- Maberly and Waggoner (Atlanta Fed WP 2000-11): S&P 500 futures TOM "disappear after 1990".
- Dzhabarov and Ziemba: futures 1993-2009.

## 4. Implementation costs for futures trend-following (task C)

| Source | Cost figure | Scope | Verbatim quote | File |
|---|---|---|---|---|
| HOP 2014 white paper, Appendix B | One-way, % of notional traded, 2003-2013: equities 0.06%, bonds 0.01%, commodities 0.10%, currencies 0.03% (6 / 1 / 10 / 3 bp one-way). 1993-2002 is twice these; 1880-1992 is six times. | AQR's 2012 estimates, including market impact and commissions; excludes roll costs | "One-Way Transaction Costs" ... "2003-2013 0.06%" (equities) ... "2003-2013 0.01%" (bonds) ... "2003-2013 0.10%" (commodities) ... "2003-2013 0.03%" (currencies); "The transactions costs used in the strategy are based on AQR's 2012 estimates of average transaction costs for each of the four asset classes, including market impact and commissions." | reports/stage_e13_briefs/pages/TrendCarry/hop_century_tf.txt lines 530-548 |
| Babu et al. 2020 JPM (same method) | Same method. The Exhibit B1 numbers are font-garbled in the text layer, so the 2020 values were not read. | per-asset-class averages; roll costs excluded | "we note that there may be other costs, including" / "the costs of rolling futures contracts, which are not" / "accounted for. Overall, transaction costs are estimated" / "with a significant amount of uncertainty." | reports/stage_e13_briefs/pages/TrendCarry/aqr_cant_always_trend_jpm.txt lines 187-198 |
| Trends Everywhere (JOIM 2020) | No cost figure | 12m TSMOM chosen for its low turnover | "While a study of transaction costs is beyond the scope" / "of our analysis, we note that the trading costs are likely" / "higher for alternative assets and factors than for tradi-" / "tional assets." | pages/SpecReaderPost2010/aqr_trends_everywhere_joim.txt lines 778-781 |
| Lim, Zohren, Roberts (arXiv 2020) | Benchmarks (incl. MOP sign rule) "resilient" up to 5 bp per unit of turnover. At c = 10 bp the MOP sign rule's SR falls from 1.392 to 0.861 (1995-2015, daily rebalancing). | cost per unit of turnover, all 88 futures | "the reference benchmarks demonstrate the most resilience to high transaction costs (up to 5bps)" | pages/SpecReaderPost2010/lim_zohren_roberts_2019_arxiv.txt lines 723-726, 768 |
| Carver (via E.13) | Rule of thumb: maximum cost per trade 0.01 SR units | retail futures trend system | "As a rule of thumb anything with a cost above 0.01SR is going to be too expensive" | reports/stage_e13_trend_carry.md line 187 (T-18) |
| Carchano and Pardo (via CXO) | 0.05% round trip, S&P 500 futures | TOM, not trend | quoted in section 3 | cxo_index_futures_calendar.txt line 63 |

No primary source states a full-strategy cost drag in bp per year for diversified futures trend-following. HOP gives
per-trade costs and net-of-cost results but no pre-cost return, so the drag cannot be read off. That figure is
UNSOURCED.

## 5. Items not verified, failures, and one proposal

[unverified] / not retrieved:
- **Kim, Tse, Wald (2016), full text.**
  - The working-paper PDF at world-finance-conference.com returned 404 (G05, G06).
  - SSRN is the only open-access location OpenAlex lists (SSRN usually returns 403; not tried).
  - The Wayback availability API returned 429 twice (W1).
  - P12's quotes come from Quantpedia's reproduction of the paper text and the bepress abstract. No 2009-2013 magnitude is available.
- **AQR, "Trend Following in Focus" (September 2018).** The aqr.com PDF and landing page now serve AQR's "page does not exist" template (G19, G23). The Wayback id_ capture was not found (G24, HTTP 404) and the Wayback availability API was throttled (W2). A search snippet claims SG Trend made +1.0% a year from Apr 2009 to Jun 2018. That is not retrieved text, so it is [unverified] and is not used.
- **HOP JPM 2017 decade table (2014-2016 values).** It is an image. UNSOURCED (as in E.13).
- **Babu et al. 2020 Exhibits 4, 7, 8 (2010-2018 backtest Sharpe and its decomposition).** They are images. UNSOURCED.
- **Baltas and Kosowski, "Demystifying Time-Series Momentum Strategies" (turnover and costs).** The Imperial repository URL returned 404 (G09). The CME-hosted copy was not fetched because cmegroup.com refuses automation (E.12 record).
- **Carchano and Pardo (2011), full text.** The open copy returned S3 AccessDenied 403 to both curl and scrapling get (G16, G16b). Only CXO's summary was used.
- **Floros and Salvador (2014).** Abstract only. Whether TOM is tested is unknown.
- **ATB TOM magnitudes.** They are in images only.
- **Futures Magazine 2014 TOM piece.** HTTP 403 (G12).
- **Financial Innovation 2020 paper.** The open-access link returned a redirect stub (G15). It was not pursued.
- **AQR "Trend Following" topic hub.** Returns the 404 template (G17, G18). The AQR datasets index (G01) lists no "Century of Evidence" trend dataset, so there is no published monthly HOP series to compute a post-2014 Sharpe from.

PROPOSAL to the lead (presentation only, not a design change):
- F6 quotes "E.13: SG Trend 0.24 over 2010-2025" beside the verdicts. Over E.21's own 2010-07..2024-02 window, SG Trend is 0.35 (net) and the AQR TSMOM factor is 0.39 (gross).
- The lead may wish to show the window-matched figures next to the 0.24, with the caveats in section 2.
