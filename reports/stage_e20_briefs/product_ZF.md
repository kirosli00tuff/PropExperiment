# Stage E.20 Part A: product file for ZF (5-year Treasury note futures; vehicle ZF)

Reader: ProductReader-ZF-OpusHigh (opus, high). Written 2026-10-11, 10:32 to about 11:00 PDT.
Brief: reports/stage_e20_briefs/brief_partA_shared.md. Shared assignment: root-specific evidence only
(the 5-year contract and the belly of the curve intraday, including 5-year auction and release windows).
Rates-class evidence: the ZN reader (shared/rates_class_notes.md); Aalto thesis: shared/aalto_thesis_notes.md;
Baltussen et al.: grepped from the on-disk copy; macro calendars: the RTY reader (shared/macro_calendars.md).
No data store opened, no bar read, no E.15/E.17/E.18 or Gate 0 result read. 12 WebSearch calls used (budget about 50).

Cost wall used throughout (root table): ZF D8 round trip 1.313 ticks = $10.26; 1.5x hurdle = 1.97 ticks.
Tick conversion: 1 tick = 1/128 point = 0.0078125 points. Price level: a 6% semiannual 5-year bond (the
contract's 6% notional coupon) priced at the Treasury 5-year par yield, from the Treasury daily par yield CSVs
(saved, pages/ZF/treasury_par/, script pages/ZF/zf_conversions.py, output pages/ZF/zf_conversions_output.txt):
mean 5-year yield 2.20% (2015-2024), price 117.88, so **1 tick = 0.663 bp of notional** (0.660 bp in the search
window, 0.655 bp in 2015..2019-05-05). Modified duration of that bond 4.40, close to the 4.45 implied by
SR 1188's own 5-year price/yield ratio (Table 3 4.615 / Table 2 1.038). Mean absolute daily change of the
5-year par yield: 4.01 bp (2015-2024), 4.63 bp (search window), so E|daily return| is about 17.6 bp and 20.4 bp.
These are public-price conversions only, not program data.

## 1. Evidence

| ID | Effect | Rule | Hold | Gross per trade (bp; ZF ticks) | Gross/net | Sample | Decay evidence | Source | Grade |
|---|---|---|---|---|---|---|---|---|---|
| E1 | Market intraday momentum, ROD to last half hour, FV alone | At 14:30 ET (13:30 CT), long FV if r_ROD = P(14:30 ET)/P(prior 15:00 ET close) - 1 > 0, else short; exit 15:00 ET (14:00 CT). Paper's FV hours 08:20-15:00 ET | 30 min | Paper gives the slope only: beta_ROD = 2.33 (x100), t 6.25, R2 1.05%, R2_OOS 0.93%. Derived: beta x E\|r_ROD\| = 0.0233 x 17.6 bp = 0.41 bp = 0.62 ticks (2015-2024 vol); 0.48 bp = 0.72 ticks at search-window vol. Ratio to D8 0.47-0.55 | gross | FV 1988-07-06..2020-05-01, 7,907 days, 1-min (Tickdata) | None for FV in the paper. Class: Aalto thesis abstract says bond intraday momentum "may not be feasible" after costs, "especially" bonds [shared, see shared/aalto_thesis_notes.md]; Rosa 2022 [shared, see shared/rosa_2022_notes.md] | Baltussen, Da, Lammers, Martens, JFE 142 (2021), Table B2 Panel B; on-disk copy reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md | primary (slope); per-trade derived |
| E1b | Same, government bond 1/N portfolio (class) | eta(r_ROD) as E1, 16 bond futures equally weighted | 30 min | 2.16%/yr; about 2.16%/252 = 0.86 bp a day = 1.29 ticks (if every day trades). Ratio 0.98 | gross | 16 bond futures, to 2020-05 | as E1 | same, Table 6 Panel B [shared, see shared/baltussen_notes.md] | primary (annual figure); per-trade derived |
| E2 | 5-year auction pre-auction price pressure (short leg) | Short the on-the-run 5-year 180 min before the competitive close (13:00 ET = 12:00 CT), exit 1 min before the close | 180 min | Full window: -2.523 bp (pre-auction return) = 3.81 ticks to a short. At the V2.2 clock (t2 = 10:20 CT = close - 100 min, h60 to close - 40 min): yield +0.18 bp read from Figure 2(c), about 0.79 bp = 1.19 ticks. Ratio 0.91 | gross (mid-quote, cash) | On-the-run 5-year note, GovPX 1991-2000 and BrokerTec 2001-2024, auctions 1991-06-25..2024-07-24, 1-min | 5-year yield pressure S1 1991-2006 0.869, S2 2007-2014 1.436, S3 2015-2024 0.919 (all significant); F-test S3 = S1 0.012 (no decline for the 5-year). Price pressure S3 4.482 bp | Fleming, Liu, Nguyen, FRBNY Staff Report 1188 (March 2026, rev. July 2026), Tables 2 and 3, Figure 2(c) | primary (cash market; futures transfer assumed) |
| E3 | 5-year auction post-auction reversal (long leg) | Long from 1 min after the result release (about 13:03 ET) for 180 min | 180 min | Full window: +2.107 bp = 3.18 ticks. At the clock (t3 = 12:50 CT, about release + 47 min, to F = 15:08 CT, release + about 185 min; h120 ends at release + 167): yield -0.25 bp from Figure 2(c), about 1.10 bp = 1.66 ticks. Ratio 1.26 | gross (cash) | as E2 | as E2 | SR 1188 Table 3, Figure 2(c) | primary (cash); clock share read from a chart |
| E4 | Cross-tenor spillover onto the 5-year | 5-year yield pressure (pre minus post, six-hour window) around auctions of other tenors | 2 x 180 min | 10-year auctions: 1.259 bp yield (x4.40 = 5.54 bp price, both legs together); 7-year: 0.715 bp (3.15 bp price); 2-year 0.280, 3-year 0.347, 30-year 0.182 (not significant). Clock shares from Figure 2(c) (post leg 24%, pre leg 17%): 10-year post leg at t3/F about 1.33 bp = 2.01 ticks, ratio 1.53; pre leg at t2/h60 1.45 ticks, ratio 1.10; 7-year post leg 1.14 ticks, ratio 0.87 | gross (cash) | as E2, full sample only | Not reported per subsample for spillovers. The 10-year's own pressure halves after 2014 (S3 0.593 vs 1.192 full); if the spillover decays alike, the 10-year post leg falls to about 1.0 tick, ratio 0.76 | SR 1188 Table 4 | primary (full-sample); clock share and decay are this reader's assumptions |
| E5 | FOMC and payrolls windows (null, and an unreachable drift) | Yield change 3 h before, and 3 h after, FOMC and employment releases | 180 min | Pre-FOMC and pre/post-NFP: "not systematically different from zero". Post-FOMC: yields fall 0.5-1.5 bp across maturities (5-year panel not tabulated); FOMC at 13:00 CT is after t3 (12:50), so no V2.2 decision time can trade it | gross (cash) | 1997..2024-07-24 | none given | SR 1188 p. 25 and Online Appendix Figures A4, A5 | primary (text); 5-year magnitude not tabulated |

Quotes (verbatim, with location):
- E1, Baltussen et al. Table B2 caption (md copy line 3537): "Adjusted R<sup>2</sup>, R<sup>2</sup><sub>OOS</sub>, and slope coefficients are multiplied by 100." Panel B header and FV row (lines 3611, 3613): "|  | βONFH | R2 (%) | R2OOS (%) | βrONFH | βM | βSLH | R2 (%) | R2OOS (%) | βROD | R2 (%) | R2OOS (%) |" / "| FV | 1.67*** (3.35) | 0.27 | 0.19*** | 1.82*** (3.72) | 2.01*** (3.89) | 8.77*** (2.93) | 1.56 | 1.12*** | 2.33*** (6.25) | 1.05 | 0.93*** |". Table A2 (line 3263): "| US 5-year T-note futures | FV | 1988-07-06 | 2020-05-01 | 7907 | 08:20-15:00 | USA |"; Table 1 caption (line 887): "U.S.-listed futures are expressed in Eastern Standard Time (EST)."
- E1b, Table 6 Panel B (line 1729): "| η(rROD) | 6.86 | 3.96 | 1.73 | 0.55 | 2.16 | 1.33 | 1.62 | 0.55 |" (the last four columns are government bond futures: Avg ret %, Std dev %, SR, Success).
- E2, SR 1188 section 4.1 (p. 18): "The pre-auction yield change is defined as the difference between the yield observed the minute before the auction close time and that 180 minutes earlier." Table 3 Panel A (p. 48), 5-Year column: "Price Pressure (bps) 1.336∗∗∗ 2.255∗∗∗ 4.615∗∗∗ ..." and "Pre-auction Return (bps) −0.733∗∗∗ −1.134∗∗∗ −2.523∗∗∗ ...". Panel B: "S3: 2015-2024 0.887∗∗∗ 1.216∗∗ 4.482∗∗∗ 2.509 5.165∗ 14.224∗". Table 2 Panel B (p. 47): "S3: 2015-2024 0.419∗∗∗ 0.340∗ 0.919∗∗∗ 0.417∗ 0.593∗ 0.592" and "H0 : S3 = S1 0.834 0.887 0.012 3.019∗ 2.361 0.093". Figure 2 caption (p. 56): "Pre-auction yield changes are computed relative to the auction closing time and post-auction yield changes are computed relative to the auction result release time."
- E3, Table 3 Panel A: "Post-auction Return (bps) 0.603∗∗ 1.120∗∗∗ 2.107∗∗∗ 2.816∗∗∗ 6.084∗∗∗ 5.031". Section 4.1 (pp. 19-20): "yields rise steadily in the hours leading up to the auction and decline after the announcement of auction results."
- E4, Table 4 (p. 49), 5-Year column by auctioned maturity: "5-Year 0.966∗∗∗ 0.921∗∗∗ 1.038∗∗∗ 0.497∗ 0.736∗∗∗ 0.562∗∗∗", "7-Year 0.297∗ 0.531∗∗∗ 0.715∗∗∗ 0.659∗∗∗ 0.490∗∗ 0.353∗", "10-Year 1.013∗∗∗ 1.076∗∗∗ 1.259∗∗∗ 0.796∗∗∗ 1.192∗∗∗ 1.294∗∗∗". Text (p. 23): "Auctions of 5-, 7-, and 10-year notes are associated with significant yield pressure across the entire curve."
- E5, SR 1188 (p. 25): "In the three hours prior to each announcement, yield changes are not systematically different from zero. Following employment report releases, yield changes remain largely insignificant. FOMC announcements are followed by a significant and persistent decline in yields—on the order of 0.5–1.5 bps".

Chart readings (E2, E3, E4 clock shares) come from Figure 2(c), rendered at 300 dpi from page 58 of the saved PDF
(pages/ZF/nyfed_sr1188_p58_fig2_render.png is the 110-dpi render). Readings: yield relative to the close
-0.40 bp at -100 min and -0.22 bp at -40 min; relative to the release -0.22 bp at +47 min and -0.47 bp at
+167 to +180 min. Reading error about +-0.05 bp, which moves each clock estimate by about 0.3 tick.
They are this reader's readings, not published numbers.

Reading of decay and costs.
- The FV-specific ROD to last-half-hour slope is strong in-sample (t 6.25) and out-of-sample (R2_OOS 0.93%),
  but at public 5-year volatility it implies about 0.4-0.5 bp a trade, 0.6-0.7 ZF ticks, half the D8 wall.
  The class portfolio figure is near one tick, still under the wall. Class-level post-2020 evidence (Aalto,
  abstract only) says bonds are the class where it is least feasible after costs. This does not clear 1.5x on
  ZF.
- The 5-year auction effect is the one ZF-specific effect that **has not decayed**: the 5-year is the only
  tenor whose 2015-2024 yield pressure (0.919) matches its 1991-2006 level (F 0.012). Over the full 180-minute
  windows each leg is 3.2-3.8 ticks gross, 2.4-2.9x the D8 wall. But the V2.2 clock samples the windows
  badly: t2 sees the last 100 minutes before the close and h60 exits 40 minutes early; t3 starts 47 minutes
  after the release, when about half of the post-auction decline (to -0.37 bp at +70 min) is already done.
  At the clock the legs are about 1.2 and 1.7 ticks, ratios 0.9 and 1.3, under 1.5x. These two legs are the
  existing K2-aucpre and K2-aucpost members and the existing features k2_auction_mto and k2_auction_msince;
  nothing new is proposed for them.
- Every SR 1188 figure is a cash, on-the-run mid-quote change with no cost. Transfer to ZF futures (which track
  the cheapest-to-deliver, about 4 to 5.25 years) is assumed, not shown.
- Null results: no pre-FOMC drift and no NFP drift in the 3-hour windows (SR 1188), so no NFP or pre-FOMC
  feature is proposed for ZF.

Sources searched and not used as ZF evidence (non-survivors):
- Lou, Yan, Zhang (RFS 2013) multi-day auction cycle: pre-2015 sample (to 2008) and daily; SR 1188 shows the
  multi-day magnitudes do not persist after 2014. Not fetched [secondary-only].
- Robeco quant chart (2025), 10-year note futures auction pattern (-6 bp before the auction): a 10-year
  contract, so ZN's; not fetched [secondary-only, search snippet].
- Indriawan, Jiao, Tse (JBF 2021), post-FOMC drift in long-term US and German bond futures: rates class (ZN),
  and post-13:00 CT, out of the clock's reach. Not fetched.
- Hartley and Schwarz (2019) month-end Treasury returns and the NY Fed month-end liquidity notes: rates class
  (ZN). Not fetched.
- arXiv 1512.06228 (Stanford, 2015): ZF and ZN machine learning on daily data, weekly direction; not intraday.
  Not fetched [secondary-only].
- 2009 Banking and Finance Review paper (Treasury note futures intraday serial correlation) and Fleming and
  Lopez / Fleming (1997) 5-year volatility by trading centre (FRBSF Economic Letter 2000-04, saved): pre-2015.
  The letter was read only to confirm the New York-hours concentration of 5-year volatility (6.2 bp vs 1.4 bp
  in Tokyo and London hours, 1990s data); no number from it enters a conversion.
- Fed purchase-operation (2020 QE) studies: daily or execution-quality only, no intraday price pattern by
  maturity, and no operation calendar covers 2010-2019 usefully (QE ended 2014). Not fetched.
- No study since 2015 on 5-year futures lead-lag at retail latency, settlement-window or time-of-day returns
  was found in 12 searches. Unknown, not rejected.

## 2. Feature availability (ZF rows)

Calendar files: rates group calendar 2019-2026 `data/calendars/rates.py` (2019-05-01..2026-06-19, sha256
449c1529...); 2010-2019 `data/calendars/hist2010/rates.json` (= reports/stage_e14_cal_rates.json, sha256
099ac84e...; 2010-06-01..2019-05-31; 2,324 trade dates, 0 unsourced; sessions R1 2010-06-01..2011-09-30
Globex 17:30-16:00 CT, R2 2011-10-03..2019-05-31 17:00-16:00 CT; day session 07:20-14:00; grade "cme").
Frozen release calendar `reports/stage_e2b_release_calendar.json` (sha256 839f2437...; 2019-05-01..2026-06-21).
EC-AUC 2010-2019 `reports/stage_e16_calendars/ec_auc_2010_2019.json` (sha256 e3b5f452...; 2010-01-01..
2019-06-30; FiscalData API, 684 rows, 0.0% unsourced; exact match with the frozen file over 2019-05..06).
FOMC 2010-2019 `reports/stage_e14_cal_releases.json` (2010-06-01..2019-05-31; 72 statements).
Listing: ZF (Tickdata FV) from 1988-07-06 (Baltussen et al. Table A2), well before both windows; E.16 windows:
ZF start 2010-07, bars from the E.17 purchase. E.12's D4 start rule (ZF 2020-10-01) does not apply (E.16 R-O2).

| Feature | Legs | Calendars / tables | 2010-2019 (2010-07-01..2019-05-05) | 2019-2024 | Basis |
|---|---|---|---|---|---|
| cp1_ret | ZF | rates calendar; D6 O = 07:20; first bar fixed at 17:00 CT of d-1 (ports.py GLOBEX_OPEN_MIN) | **partial**: 2011-10-03..2019-05-05 | yes | hist2010 rates.json session R1: Globex opened 17:30 CT until 2011-09-30, so the coded first bar (17:00 CT) does not exist on 2010-07-01..2011-09-30 and the value is missing by construction (row excluded as missing for data reasons), unless the lead re-reads the first-bar rule |
| cp2_range, cp2_brk | ZF | rates calendar, O = 07:20 (bars of [O, O+15)) | yes | yes | day session 07:20-14:00 in both calendars |
| cp3_clv | ZF | rates calendar (previous port-complete day) | yes | yes | both calendars cover the windows |
| k2_auction_mto (t1, t2), k2_auction_msince (t3) | ZF | own tenor "5Y" (AUCTION_TENOR, by original_security_term); 2019+: k2/_releases.py TREASURY_AUCTIONS (2019-05-08..2026-06-11; 56 5Y rows in the window); 2010-2019: EC-AUC file (107 5Y-tagged rows in the window), not yet generated into a K2 literal table | yes (calendar exists; literal table not built) | yes | Tenor mapping facts: in the backward window 6 of the 107 "5Y" rows are 2-year-term sales (2015-05-26, 2015-08-25, 2015-09-22, 2015-11-04, 2016-02-23, 2017-10-24; closes 11:30 ET) and 5 five-year sales carry "7Y" and are left out (2013-08-28, 2013-09-25, 2017-11-27, 2017-12-27, 2019-03-27). In the search window the 5-year sales of 2019-05-28 and 2022-01-25 carry "7Y" and are left out; 2019-12-24 (5Y, 10:00 CT) is an early-close date |
| k2_fomc_mto | ZF | FOMC_STATEMENT_DATES: statements at 13:00 CT only (L-15); 2019+: 2019-05-01..2026-06-17; 2010-2019: E.14 FOMC rows | **partial**: 2013-03-20..2019-05-05 (50 statements at 14:00 ET, all time-graded official) | yes | E.14 FOMC times: 2010-2012 statements at 12:20-12:35 or 14:15 ET (14 of them inferred), and 2013-01-30 at 14:15 ET; none is at 13:00 CT, so under the frozen definition no event exists before 2013-03-20 |
| k2_monthend_msince | ZF | MONTH_END (N-1, N of each month), from rates.py (2019-05-30..2026-05-28) | yes (derivable; not built) | yes | The same N/N-1 rule applies to hist2010/rates.json (0 unsourced); no 2010-2019 table exists yet |
| k2_predrift_move | ZN, ZB only | ISM services | n/a on ZF rows | n/a | predrift EXPOSURES = (ZN, ZB) |
| g01_ret30, g02_ret60, g03_ret120, g04_ret_day | ZF | none | yes | yes | own bars; listed since 1988 |
| g05_gap | ZF | rates calendar (previous trade date, C_X = 14:00; early halt gives not applicable) | yes | yes | both calendars carry early halts |
| g06_rv60, g09_vol_state, g10_logvol30 | ZF | none (20 and 120 previous dates) | yes, after warm-up | yes | warm-up at the start of the 2010-07 bars is a data matter, not a calendar one |
| g07_range, g08_prev_ret | ZF | rates calendar | yes | yes | |
| g11_t_index, g12_dow | none | none | yes | yes | |
| g13_min_to_rel, g14_min_since_rel, g15_rel_day | ZF | ZF's D8 list: FOMC, NFP and Treasury auctions of every coupon tenor (2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y); no CPI. Search window: 488 rows (FOMC 37, NFP 57; auctions 2Y 58, 3Y 57, 5Y 56, 7Y 60, 10Y 59, 20Y 46, 30Y 58) | **partial / undetermined**: auctions yes (EC-AUC, every coupon tenor; the 20-year was not auctioned before 2020-05), FOMC yes (E.14), NFP [shared, see shared/macro_calendars.md] | yes | g13-g15 read the release file's coverage; a 2010-2019 file needs the three sources merged |
| g16_month_end | none | rates calendar (last two trade dates) | yes | yes | |
| g17_nq, g17_6e, g17_cl, g17_gc, g17_zc | NQ, 6E, CL, GC, ZC | none | [shared, see product_NQ/6E/CL/GC/ZC.md] | [shared] | lead listings audited by those readers |
| g17_zn | ZN | none | n/a on ZF rows | n/a | ZF's own cluster lead (K2) is not applicable (generic.py SG-2) |
| g17_mbt | MBT (not one of the 17) | none | no | partial (MBT listed 2021-05) | |
| g17_mes | MES (not one of the 17) | none | no | yes (MES listed 2019-05) | |
| k9_anncday | MNQ, M2K, MYM only | EC-K9 | n/a on ZF rows | n/a | |

Excluded by the clock (E.11 section 3): k2_fomc_msince (13:00 CT is after t3), k2_monthend_mto (07:20 anchor
before t1).

## 3. Proposed features

One proposal, which does **not** clear 1.5x on the decay-adjusted reading. Zero would also be defensible;
it is listed so that the lead has the arithmetic.

P1 `zf_auc10y_mto` / `zf_auc10y_msince`: minutes to and since today's 10-year note auction close, on ZF rows.
- Source: Fleming, Liu, Nguyen (FRBNY SR 1188, 2026), Table 4: the 5-year's yield pressure around 10-year
  auctions is 1.259 bp (t-significant at 1%), larger than around its own auctions (1.038). Quote: "10-Year
  1.013∗∗∗ 1.076∗∗∗ 1.259∗∗∗ 0.796∗∗∗ 1.192∗∗∗ 1.294∗∗∗" (5-Year column third) and "Auctions of 5-, 7-, and
  10-year notes are associated with significant yield pressure across the entire curve."
- Formula: A10 = the dates with a TREASURY_AUCTION row of tenor "10Y" (frozen release calendar from 2019-05;
  EC-AUC file before), T = that row's instant_utc in America/Chicago. On a ZF row (d, t): if d is in A10 and
  t <= T, mto = (T - t) in minutes, applicable; if t > T, msince = (t - T), applicable; otherwise 0 with flag 0.
  The same fixed_clock helper as k2_auction (ml_route_v2/signals/k2.py `_auction`), with the tenor set to 10Y.
- Decision times and horizons: t2 (mto, about 100 min before a 12:00 CT close; h60) and t3 (msince, about 47
  min after the release; h120 and F).
- Legs: ZF only. Calendars: Treasury auction rows of tenor 10Y; both exist causally (announcement before the
  auction date, E.0 C9 rule) over both windows: 2010-07-01..2019-05-05 106 rows, 2019-05-06..2024-02-29 59 rows.
- Expected gross: the 5-year's spillover price pressure is about 1.259 x 4.40 = 5.54 bp over both 180-minute
  legs. Applying the clock shares of the 5-year's own Figure 2(c) path (post leg t3 to F 24%, pre leg t2/h60
  17%): post leg 1.33 bp = 2.01 ticks, ratio 1.53 to the D8 wall; pre leg 0.96 bp = 1.45 ticks, ratio 1.10.
  Both rest on full-sample (1991-2024) figures and on a transferred path shape. The 10-year's own pressure
  halved after 2014 (0.593 vs 1.192); with the same decay the post leg is about 1.0 tick, ratio 0.76.
- Clears 1.5x: no on the decay-adjusted reading (0.76); the full-sample reading (1.53) is at the hurdle and
  rests on two assumptions. Overlap: g13-g15 already include 10Y auctions in ZF's D8 list, mixed with 2Y, 3Y,
  20Y, 30Y auctions (no significant spillover onto the 5-year) and FOMC and NFP.

The 7-year spillover (0.715 bp) gives about 1.14 ticks at t3/F (ratio 0.87) and is not proposed.

## 4. NQ only

n/a.

## 5. Fetch log, terms read, budget notices

All times UTC (PDT = UTC - 7). Pages under reports/stage_e20_briefs/pages/ZF/.

| URL | UTC | sha256 | Path | Status |
|---|---|---|---|---|
| https://www.newyorkfed.org/robots.txt | 2026-10-11T17:37:13Z | 0102c8c4...51e | nyfed_robots.txt | ok |
| https://www.newyorkfed.org/privacy/termsofuse | 2026-10-11T17:37:31Z | 96482020...5cf8 | nyfed_terms.html (+ .txt a3eca218...) | ok |
| https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1188.pdf | 2026-10-11T17:37:40Z | 93f9b196946d3c41e9670052eb3d8d0fce30fb892f8f1553c1b469c05193095b | nyfed_sr1188.pdf (+ pdftotext nyfed_sr1188.txt 0103fe18...; page 58 render aa5ee150...) | ok |
| https://www.frbsf.org/robots.txt | 2026-10-11T17:42:4xZ (file mtime 17:42:41) | 3d0d93ef...a1e | frbsf_robots.txt | ok |
| https://www.frbsf.org/economic-research/publications/economic-letter/2000/february/volatility-spillovers-in-the-us-treasury-market | 2026-10-11T17:42:45Z | aee5b178...c212 | frbsf_el2000_feb_volspill.html (+ .txt) | ok (context only) |
| https://www.frbsf.org/privacy | 2026-10-11T17:42:58Z | f80ad8f4...4421 | frbsf_privacy.html | ok |
| https://home.treasury.gov/robots.txt | 2026-10-11T17:44:10Z | d1a67686...aab | treasury_robots.txt | ok |
| https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/<year>/all?type=daily_treasury_yield_curve&field_tdr_date_value=<year>&page&_format=csv, years 2015-2024 | 2026-10-11T17:44:20Z..17:44:53Z (3 s apart) | treasury_par/SHA256SUMS | treasury_par/par_<year>.csv | ok |
| https://fred.stlouisfed.org/robots.txt | 2026-10-11T17:43Z | none | none | failed (HTTP/2 stream error, then the retry was killed); FRED not used |
| (no fetch) Baltussen et al. on-disk copy | n/a | 18cb436e9d18cb3eff3565cddfe85b35fa1c5d5d8bf2afb85df42b6ab49e0465 | reports/stage_e13_briefs/pages/InfoSource/baltussen_etal_2021_jfe.md | grep only |

Terms read:
- newyorkfed.org: robots.txt disallows only /PrincipleInterest/ and two calendar PDFs. Terms of Use (last
  updated 6/9/2023): "The New York Fed grants you a non-exclusive license, subject to the Terms, to use, copy,
  and distribute Content for your personal or business purposes." Ruling: one PDF download allowed, with
  attribution.
- frbsf.org: robots.txt disallows only /wp-admin/. No terms-of-use page found (the site links only a privacy
  notice). The letter says "Permission to reprint portions of articles or whole articles must be obtained in
  writing." Ruling: one fetch for reading and a short quotation is allowed; nothing reprinted.
- home.treasury.gov: robots.txt "Allow: /". U.S. government data. Ruling: 10 CSV downloads allowed.
- fred.stlouisfed.org: robots.txt could not be read; nothing fetched from FRED.

Budget notices: none. WebSearch calls: 12. No Firecrawl or Scrapling use.

## 6. Unfinished and unverified items

- The clock shares (E2, E3, E4, P1) are readings from SR 1188 Figure 2(c), +-0.05 bp, not published numbers.
  The spillover path shape is assumed equal to the own-auction shape. Spillovers have no subsample split in
  the paper.
- All SR 1188 magnitudes are cash on-the-run mid quotes. Transfer to ZF futures prices is assumed.
- E1's per-trade figure is derived (slope x public mean absolute daily return); the paper gives no per-trade
  FV figure. The proxy uses close-to-close par-yield changes (Treasury's daily curve), not 14:00-to-13:30 CT
  returns.
- g13-g15 2010-2019: NFP coverage depends on the RTY reader's shared/macro_calendars.md (not on disk when
  this file was written).
- The 2010-2019 K2 literal tables (auction, month-end) are not built; their source calendars exist.
- cp1_ret 2010-07-01..2011-09-30: whether the lead re-reads the first-bar rule (17:00 CT bar vs first bar of
  the trade date) is the lead's call.
- Class evidence (rates intraday since 2015, pre-announcement drift, month-end, Rosa): see the ZN and NQ
  readers' notes. shared/rates_class_notes.md was not on disk when this file was written.
