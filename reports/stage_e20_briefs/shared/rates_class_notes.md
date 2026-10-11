# Rates-class notes: published intraday evidence on US Treasury futures since 2015

Stage E.20 Part A, shared source notes. Reader: ProductReader-ZN-OpusHigh. Written 2026-10-11 (PDT).
The ZT, ZF, TN, ZB and UB readers cite this file for class evidence as
`reports/stage_e20_briefs/shared/rates_class_notes.md`. Raw pages are in `reports/stage_e20_briefs/pages/ZN/`
unless stated otherwise. Every number below has a verbatim quote from a saved full text, or a grade tag.

## 0. Conversions used (state these with any figure you reuse)

- **Tick in bp of price.** One tick is 1/64 of a point (ZN, TN) = 0.015625 points; at a price of 110 that
  is 0.015625 / 110 = **1.42 bp**. ZN traded at roughly 110 to 135 over 2010-2024, so one tick is 1.16 to
  1.42 bp. 110 is used throughout, which is conservative because it gives the fewest ticks per bp. The
  110 level is an assumption; the planning brief gives "about 1.4 bp". ZT and ZF ticks are 1/128 of a
  point. ZB and UB ticks are 1/32 of a point. Readers of those roots convert with their own tick.
- **Yield to price, 10-year futures.** Hartley and Schwarz (2019, p. 31), verbatim: "So a 10-year
  futures contract has a duration of about 6 years." So 1 bp of yield is about 6 bp of ZN price, about
  4.2 ZN ticks. This applies the 10-year cash yield change to the futures' cheapest-to-deliver, which is an
  approximation [assumption].
- **10-year cash price to ZN price.** The on-the-run 10-year note's modified duration is taken as about
  8.7 [assumption, not sourced]. So ZN price bp is about 6 / 8.7 = **0.69 x** the cash price bp.
- **ZN D8 round trip.** 1.17 ticks ($18.28) from `root_table.md`. The 1.5x hurdle is **1.755 ticks**.

## 1. Evidence table (rates class)

Each row: effect | rule | hold | gross per trade (ZN) | sample | decay | source | grade.

### R1. Market intraday momentum, rest-of-day to last half-hour (bond futures)
- Rule (Baltussen, Da, Lammers, Martens, JFE 2021): at close-30, go long if r_ROD = P(close-30)/P(prior
  close) - 1 > 0, else short; exit at the close. **US bond futures' "close" is the end of the settlement
  period.** Table A: "US 10-year T-note futures | TY | 1983-01-05 | 2020-05-01 | 9296 | 08:20-15:00 |
  USA", with "U.S.-listed futures denoted in Eastern Standard Time (EST)". So the window is 13:30-14:00 CT.
  Section 2: "For all but Australian and Japanese bond futures, this results in using the regular opening
  hours of the futures as open, and the end of the daily settlement period as close."
- Portfolio result (Table 6, Panel B, government bond futures, 1/N of 16 contracts): "η(rROD) | 2.16 | 1.33
  | 1.62 | 0.55" (average return %/yr, sd, SR, success rate), gross, "Samples range from December 1974 to
  May 2020."
- Per trade: 2.16% / about 252 trades a year = **0.86 bp, or 0.60 ZN ticks**, against D8's 1.17. Ratio
  **0.51**: fails 1.5x. (Derived from the 1/N portfolio mean. A single contract's mean is the same order
  of size; the portfolio only lowers the sd.)
- TY row (Table B2, Panel B, individual regressions, slopes x100): "TY | 1.68*** (3.41) | 0.24 | 0.16*** |
  1.81*** (3.68) | 2.60*** (5.21) | 7.51*** (4.07) | 1.33 | 0.91*** | 2.53*** (6.96) | 1.06 | 0.86***". The
  last three are β_ROD 2.53 (t 6.96), R2 1.06%, R2_OOS 0.86%. So a 1% r_ROD (large for ZN) predicts
  about 2.5 bp in the last half-hour, about 1.8 ticks. Typical |r_ROD| is a fraction of that.
  Other US rows: "TU ... 2.07*** (4.45) | 0.71 | 0.70***", "FV ... 2.33*** (6.25) | 1.05 | 0.93***",
  "US ... 2.11*** (3.85) | 0.64 | 0.22***", "UB ... 3.39*** (4.36) | 2.35 | -3.40*" (UB's OOS R2 is
  negative).
- Decay (Table 5): bonds β_ROD "3.19*** (8.38) | 1.28" in 1974-1999 and "1.53*** (3.61) | 0.47" in
  2000-2020. The slope roughly halved and R2 fell by about two-thirds.
- Mechanism tests for bonds (Section 4.2): "the bond market results remain positive but insignificantly
  so" (leveraged-ETF difference-in-difference).
- E.20 clock: no rates decision time falls in 13:30-14:00 CT (t3 12:50, t4 14:08). The effect is not
  reachable with E.20's rates clock except through the prompt-added r_ROD feature at other times.
- Source: `reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md` (grep, lines 1004-1016,
  1655-1668, 1704-1750, 2355-2400, 3255-3270, 3600-3625, 548-575). Grade: primary. The NQ reader's
  `shared/baltussen_notes.md` is the full read.

### R2. Aalto thesis (Majorin 2025), 20 equity, bond and currency futures, 2008-01..2024-10
- Abstract only. Full text restricted, see `shared/aalto_thesis_notes.md`. Bond-relevant sentence:
  "we find that most intraday momentum and reversal trading strategies may not be feasible after
  transactions costs, especially in bond and currency futures." Also: "most of the predictability in the
  return of the last half an hour stems from the last ten-minute period". No figures. Grade: primary
  abstract, figures [unverified]. Whether US Treasury futures are among the 20 is not known.

### R3. Auction-day intraday price pressure (Fleming, Liu, Nguyen, NY Fed Staff Report 1188, 2026)
- Rule: on a coupon auction day (competitive close 13:00 ET = 12:00 CT for notes and bonds), yields rise
  over [close - 180 min, close) and fall over (results release, release + 180 min]. Table 2's notes give
  the definitions, verbatim: "∆Y (pre) = Y0− −Y−180 and ∆Y (post) = Y180 −Y0+". Trading reading: short
  09:00-12:00 CT, long about 12:02-15:02 CT. This is the program's K2-aucpre-01 and K2-aucpost-01.
- Data: on-the-run cash securities, "GovPX (June 1991–December 2000) and BrokerTec (January
  2001–July 2024)". Not futures.
- Table 2 (yield, bp), 10-year column: "Yield Pressure (bps) ... 1.192∗∗∗"; "∆Y (pre) ... 0.442∗∗∗"; "∆Y
  (post) ... −0.750∗∗∗"; subsamples "S1: 1991-2006 ... 1.491∗∗∗", "S2: 2007-2014 ... 1.732∗∗∗", "S3:
  2015-2024 ... 0.593∗". 2-year 0.712, 5-year 1.038, 30-year 0.869 (full sample). 2015-2024: 2Y 0.419,
  5Y 0.919, 30Y 0.592.
- Table 3 (price return, bp), 10-year column: "Price Pressure (bps) ... 9.905∗∗∗", "Pre-auction Return
  (bps) ... −3.822∗∗∗", "Post-auction Return (bps) ... 6.084∗∗∗"; "S3: 2015-2024 ... 5.165∗" (total only,
  no pre/post split by subsample). 30-year: 17.106 total, pre −12.075, post 5.031 (not significant);
  "S3: 2015-2024 ... 14.224∗". 5-year: pre −2.523, post 2.107; S3 4.482. 2-year: pre −0.733, post 0.603;
  S3 0.887.
- ZN conversion (cash 10-year price x 0.69, then / 1.42 bp per tick):
  - pre leg, full sample: 3.822 x 0.69 = 2.64 bp = **1.86 ticks** (ratio 1.59 to D8, clears 1.5x
    narrowly);
  - post leg, full sample: 6.084 x 0.69 = 4.20 bp = **2.96 ticks** (ratio 2.53);
  - 2015-2024, both legs together: 5.165 x 0.69 = 3.56 bp = **2.51 ticks for two trades**, about 1.25
    per leg if split evenly (assumption; ratio about 1.07, fails 1.5x).
  - Yield route check: pre 0.442 bp x 6 = 2.65 bp = 1.87 ticks, which agrees.
- Decay: Section 4.1, verbatim: "the post-2015 period displays markedly weaker yield pressure—less than
  half the earlier magnitudes. Formal F-tests confirm that yield pressure declines significantly after
  2014 for the 3- and 10-year notes." Controls, verbatim: "yield changes over the same intraday windows on
  control days are not statistically different from zero".
- Cross-tenor spillovers (Table 4, 10-year secondary-market column, full sample only): "5-Year ...
  0.736∗∗∗", "7-Year ... 0.490∗∗", "2-Year ... 0.190", "3-Year ... −0.035", "30-Year ... 0.395". Text,
  verbatim: "Auctions of 5-, 7-, and 10-year notes are associated with significant yield pressure across
  the entire curve."
- Source: `pages/ZN/nyfed_sr1188.pdf` (+ .txt lines 140-160, 660-720, 740-770, 778-812, 1622-1735).
  Grade: primary (working paper, not peer-reviewed).

### R4. 10-year auction, ZN futures (Robeco quant chart, 2025-03-27; practitioner)
- Verbatim: "ahead of the auction, on average futures prices decline by 6 basis points, only to recover in
  the hours that follow." Figure note: "The figure shows the difference in the performance of the US
  10-year T-Note futures on the day of a US 10-year auction vs a regular day. Sample January 1983 to
  August 2024." 6 bp of ZN price = **4.2 ticks** (pre leg, relative to a regular day; window not stated).
  The authors say they implemented it "while carefully taking risk considerations and transaction costs
  into account" and give no net figures. No subsample.
- Source: `pages/ZN/robeco_quant_chart_auctions.html` (.txt). Grade: primary but practitioner,
  unreviewed.

### R5. Pre-announcement drift (Kurov, Sancetta, Strasser, Wolfe; ECB WP 1901, 2016; JFQA 2019)
- 10-year T-note and ES futures, second-by-second, "January 2008 to March 2014". Conclusion, verbatim:
  "About 30 minutes before the release time, prices begin to drift in the direction of the market's
  subsequent reaction to the news. This drift accounts for 49 per- cent and 39 percent of the overall
  price adjustments in the E-mini S&P 500 and 10-year Treasury note futures markets". On the bond
  [t-60, t-30] window, verbatim: "some drift (only about one basis point)". Costs, verbatim: "The median
  bid-ask spread is 0.020% for the E-mini S&P 500 futures and 0.013% for 10-year Treasury notes futures."
- Not codable causally. The direction is the sign of the later surprise, unknown at decision time. The
  data are pre-2015 (published 2016 and 2019). V34 dropped it as unsized. No per-trade figure. Grade:
  primary (ECB working-paper version; the JFQA numbers differ, 9 of 20 announcements, [secondary-only]).
- Source: `pages/ZN/kssw_ecbwp1901.pdf` (.txt lines 855-880, 1080-1122, 2072-2085).

### R6. Pre-FOMC drift: null in Treasuries (Lucca and Moench, NY Fed SR 512, rev. 2013; JF 2015)
- Verbatim: "we find no such effect in U.S. Treasury securities and money market futures." And: "For the
  1994-2011 sample none of the coefficients is statistically significant at conventional confidence
  levels. For the 1980-2011 sample the on-the-run ten-year Treasury is significant at the 10% level with
  a coefficient of less than a basis point." Window: the pre-FOMC (2pm-to-2pm) day. A null result.
- Source: `shared/lucca_moench_sr512.pdf.txt` (saved by another reader; grepped lines 40-46, 786-802).
  Grade: primary.

### R7. Post-FOMC drift in bond futures (Indriawan, Jiao, Tse, J. Banking & Finance 2021)
- Abstract only (ScienceDirect blocks automation; IDEAS record saved). Verbatim: "we observe a sizable
  post-announcement drift in government bond markets. A trading strategy of investing in the market
  after expansionary shocks and shorting the market following contractionary surprises yields up to four
  times the Sharpe ratio of buy-and-hold investment. The post-FOMC announcement drift ... persists for 15
  days. Moreover, our study shows an absence of pre-FOMC announcement drift."
- Multi-day. It needs the shock's sign, and the intraday part is not stated. Grade: [secondary-only]
  (abstract), no figures.
- Source: `pages/ZN/ideas_indriawan_jiao_tse_2021.html`.

### R8. End-of-month Treasury returns (Hartley and Schwarz 2019, Wharton Rodney White WP)
- Table 8, 10-year futures, long over the last t days of the month: "10-Year 0.09*** 0.14*** 0.17***
  0.18*** 0.22*** 0.20*** -0.06 -0.08* -0.10** -0.04"; notes: "100 times the average returns ... The
  units are (approximate) percentage points per month", "The sample period is from 1990 to 2018." The last
  day is +0.09 percentage points = 9 bp, about 6.3 ZN ticks, **close-to-close, overnight included**. It is
  not intraday evidence. The intraday share is unknown. This is the program's K2-monthend-01, which buys
  07:20 to 15:04 CT on N-1 and N.
- Source: `pages/ZN/hartley_schwarz_2019.pdf` (.txt lines 804-826, 1510-1540). Grade: primary
  (working paper).

### R9. Month-end intraday timing (Dyer, Fleming, Shachar, Liberty Street Economics, 2026-09-22)
- Verbatim: "We also document a marked shift in trading activity from around 3 p.m. (ET) to around 4 p.m.
  after a major fixed-income index provider moved its strike time from 3 p.m. to 4 p.m. in January
  2021." This covers activity, not returns. It is a structural break inside the search window: the strike
  moved from 14:00 CT to 15:00 CT, still before F = 15:08.
- Source: `pages/ZN/lse_index_strike.html` (.txt). Grade: primary (blog of record), no return figure.

### R10. Bond intraday momentum, Chinese Treasury bond futures (Zhang, Wang, Li, JBEF 2021)
- Abstract only, verbatim: "we find that the first fifteen-minute return is a good predictor of the last
  fifteen-minute return. The predictive power ... is stronger on trading days with low trading volume,
  high trading volatility, positive first fifteen-minute return, and no news release". No figures. CFFEX,
  not CBOT. Grade: [secondary-only]. Source: `pages/ZN/ideas_zhang_wang_li_2021_bond_intraday_momentum.html`.

### R11. Intraday trend and reversion, pooled futures incl. US 10-year (Safari and Schmidhuber, arXiv 2501.16772v2, 2025)
- End-of-minute data 2010-2023. Interest rates: "US 10-year | Can. 10-year | Ger. 10-year | UK
  10-year". Horizons of 1 hour or more (Table 6): b "+0.132% ±0.046% +2.9"; "R2adj 0.009 bp ... 0.020 bp"
  (OOS, by cross-validation). Up to 16 minutes (Table 5): b "−0.912% ... −13.6" (reversion). Pooled
  across asset classes, so no rates-only per-trade figure. The R2 is too small to size a trade.
  Grade: primary. Source: `pages/ZN/arxiv_2501.16772.pdf` (.txt lines 545-600, 660-692).

## 2. Searched and not found (gaps, not rejections)
- A US Treasury futures intraday momentum or reversal study since 2015 other than Baltussen et al. (and
  the restricted Aalto thesis): none found in 6 searches.
- Settlement-window (13:59:30-14:00 CT) return effects in Treasury futures: none found.
- ES to ZN (or any equity to rates) lead-lag at retail latency, post-2015: none found. HFT-latency
  cross-market studies exist but were not pursued (not retail-tradable).
- Lunchtime or time-of-day return seasonality in Treasury futures since 2015: none found.
- "Drift Begone" (the planning brief's 2022 draft on pre-announcement drift): not found by search.
- The KSSW 2017 Skidmore draft returned 404. The ECB 2016 version was used instead.

## 3. Reading for the rates readers
- The only rates-class effect with a published size that reaches ZN's 1.5x hurdle on full-sample averages
  is the **auction-day V** (R3, R4): about 1.9 ticks for the pre leg and about 3.0 ticks for the post leg,
  1991-2024. After 2014 it falls to less than half (10-year S3 total 0.593 bp of yield, p<0.1). The
  program already carries it as K2-aucpre/aucpost and the `k2_auction_*` features.
- ROD to LH momentum in bond futures is about 0.6 ZN ticks per trade gross (R1). It halved after 2000,
  sits outside E.20's rates clock, and the Aalto abstract says it is "especially" infeasible after costs
  for bonds.
- FOMC: no pre-drift (R6, R7). A post-drift exists over days (R7), with no intraday size.
- Month-end: a close-to-close effect (R8). Intraday size unknown. The strike time moved in Jan 2021 (R9).
