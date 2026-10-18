# DF3 Treasury drifts: second reader on C4 (pre-refunding) and C5 (pre-FOMC Treasury drift)

Reader: DF3 (DeepReader-TreasuryDrifts-OpusHigh), Stage E.25 wave 2. Started 06:21 PDT, finished about
06:50 PDT on 2026-10-18. Times are PDT except in the fetch log (UTC).

Full texts DF3 re-read from its own `pdftotext -layout` extraction (it did not use RD2's text file):
- WZ: Wang, Zhao, "Pre-Refunding Announcement Gains in U.S. Treasurys", draft of July 16 2025 (74 pp.),
  OSF xucf8. Crossref shows two OSF versions, v1 posted 2024-03-21 and v2 posted 2025-07-17 (DOI
  10.31235/osf.io/xucf8_v2), so RD2's copy is the latest OSF version. File:
  pages/RD2/wang_zhao_2024_prerefunding.pdf, sha256 3fc6bc4f...a476d.
- PP26: Pan, Peng, "The Pre-FOMC Drift in Long-Term Treasury Bonds", "Current draft: June 2, 2026".
  The live author copy (en.saif.sjtu.edu.cn/junpan/FOMC_new.pdf, fetched by DF3) has the same sha256
  (06a73bf3...16326d) as the E.20 copy, so no newer version exists.
- PP25: Pan, Peng, the earlier draft under its old title "The Pre-FOMC Drift and the Secular Decline in
  Long-Term Interest Rates", "Current draft: December 26, 2025" (AFA 2026 program copy, new to E.25).
  pages/DF3/aea2026_pan_peng.pdf.
- Lucca, Moench, SR 512, and Kurov, Wolfe, Gilbert (2021): the E.10 copies.

## 1. Answer (at most 250 words)

C4 checks out. Two points need correcting. First, every WZ number is a cash or ETF return, not a
futures return: the daily figures are CRSP fixed-term indexes and the intraday figures are Tradeweb
dealer mid-quotes, 07:30-17:00 ET (06:30-16:00 CT), 2006-2023. The intraday result is given only as a
figure plus a sentence ("rising by over 10 bps" in the morning); no table gives an intraday number.
The 10-year figures check: 12.62 bp, t 3.32, N 129. Post-2002 is 15.48 (t 3.27, N 88). With
day-of-week and end-of-month fixed effects it is 9.40 bp (SE 4.03). Second, WZ's Table 11 conditions
the effect on FOMC timing: "positive pre-TRA returns are present almost exclusively when an FOMC
announcement occurs within the preceding five days", and the effect is negative after rate cuts.

C5 also checks out (7.26 bp, t 2.82, futures, 2004-01 to 2025-06). The window was read off the
average-return figure: it runs from the Tokyo open, where the drift starts, to the London close, where
it peaks. N for the intraday window is not stated. No post-2015 subsample is reported. The December
2025 draft gave 6.9 bp with t 2.24 for the same window, so the t-statistic moved by 0.58 between drafts.

Event dates in the research window:
- Five TRAs, all Mondays: 2025-04-28, 07-28, 11-03 and 2026-02-02, 05-04. Pre-TRA Fridays: 04-25,
  07-25, 10-31, 01-30, 05-01.
- Ten FOMC statements (section 5).

D8's own book data (not a published source) give ZN at 18:00-18:30 CT the same 1.168-tick round
trip as the day session, with about a third of the top-of-book depth.

## 2. Candidate hypotheses

DF3 proposes no new candidates. It gives corrected inputs for the lead's C4 and C5 (RD2-C1 and RD2-C2),
listed in the json as DF3-C4 and DF3-C5. The lead sets the parameters.

| id | hypothesis | entry window CT | hold | trades/yr | published effect | ZN ticks at 111 (bp x 111/10,000 x 64) | grade | overlap |
|---|---|---|---|---|---|---|---|---|
| DF3-C4 (= C4, RD2-C1) | Long ZN on the trading day before the Monday 15:00 ET Treasury primary release (usually a Friday) | the paper's intraday window is 06:30-16:00 CT; Topstep's flat rule cuts it to 06:30-15:10 CT; or a close-to-close daily hold | 1 session | 4 | 10-year cash: 12.62 bp/day (t 3.32, N 129, 1991Q4-2023); 9.40 bp with DOW+EOM fixed effects; IEF ETF 13.81 bp raw, 10.37 bp with fixed effects (2002-2023); intraday morning gain "over 10 bps" (figure only) | 12.62: 8.97 raw, 6.19 at the lead's x0.69; 9.40 (FE): 6.68, 4.61 at x0.69; IEF 13.81: 9.81; IEF FE 10.37: 7.37; intraday ">10 bp": 7.10, 4.90 at x0.69 | working-paper | K2-monthend-01 shares 2 of the 5 window dates (10-31, 01-30) |
| DF3-C5 (= C5, RD2-C2) | Long ZN from 19:00 ET on day -2 to 12:00 ET on day -1 (day -1 = the first meeting day; the statement comes on day 0) | 18:00 CT on the Monday evening to 11:00 CT on Tuesday | 17 h, inside one Topstep trading day | 8 | 10-year note futures: 7.26 bp, t 2.82 (2004-01..2025-06, PP26); 6.9 bp, t 2.24 (2004-01..2025-07, PP25); rest of day -1 (12:00-17:00 ET) -2.05 bp (t -1.76) | 7.26: 5.16 (futures, so no ratio applied); 6.9: 4.90; rest of day: -1.46 | working-paper | no member holds rates futures on day -1; K2-fomcpost-01 trades day 0 |

The ratios to the 1.75-tick hurdle are left to the lead. The x0.69 cash-to-ZN duration ratio is the
lead's and RD2's assumption. The papers do not give it, and DF3 does not choose it.

## 3. Evidence table

| claim | number | verbatim quote | location | source | grade | saved path |
|---|---|---|---|---|---|---|
| C4 intraday window, in New York hours | 07:30-17:00 ET, 2006-2023 | "average cumulative intraday returns for 10-year Treasury notes during New York trading hours (07:30-17:00 ET) ... The sample period is from 2006 to 2023." | Figure 1 caption, p. 2 (same window in the Figure 5 caption, p. 38) | WZ 2025 | working-paper | pages/RD2/wang_zhao_2024_prerefunding.pdf |
| C4 intraday is cash dealer quotes, not futures | Tradeweb minute mid-quotes | "we use Tradeweb Market Data from Datascope, which provides minute-level dealer bid and ask quotes ... we compute the mid-quote (the midpoint of the closing bid and ask) for each minute" | Section 3.2, p. 10 | WZ 2025 | working-paper | same |
| C4 intraday magnitude: figure and text only | over 10 bp in the morning of day -1 | "Prices increase notably in the morning, with the 10-year Treasury rising by over 10 bps, and then continue to increase marginally for the remainder of New York trading hours. During the TRA day (Day 0) and the subsequent day (Day +1), prices remain at this elevated level" | Section 4.3, p. 19 | WZ 2025 | working-paper | same |
| C4 why the window is New York hours | Fleming 94% | "we follow the practice of Fleming (1997) and Adrian et al. (2023) by confining our analysis to New York trading hours (07:30 to 17:00 Eastern Time)" | Section 4.3, p. 18 | WZ 2025 | working-paper | same |
| C4 daily 10-year figure (CRSP cash) | 12.62 bp, sd 43.15, N 129 | "10Y 129        12.62       43.15      -97.92     121.41     7,933      1.82" | Table 2 Panel A (CRSP Treasury Returns) | WZ 2025 | working-paper | same |
| C4 t-statistic and post-2002 | 12.62 [3.32]; post-2002 15.48 [3.27], N 88; pre-2002 6.48 [1.03], N 41 | "Full 129 0.66 [0.86] 8.25∗∗∗ [3.62] 12.62∗∗∗ [3.32]"; "Post-2002 88 0.57 [0.53] 9.97∗∗∗ [3.66] 15.48∗∗∗ [3.27]" | Table 6 Panels A-B | WZ 2025 | working-paper | same |
| C4 with calendar controls | 10Y pre-TRA 9.40 (SE 4.03) with DOW+EOM FE; 12.63 with DOW only | Panel C row "pre-TRA 0.54 1.86∗∗ 6.01∗∗ 7.46∗∗ 9.40∗∗ 13.20∗∗ 14.78∗" / "(0.79) (0.83) (2.43) (3.38) (4.03) (6.30) (7.86)" | Table 3 Panels B-C | WZ 2025 | working-paper | same |
| C4 tradable instruments | IEF 13.81 (SE 4.25) raw, 10.37 (4.52) with FE; TLT 22.06 / 12.83 | "pre-TRA 2.65∗∗∗ 8.98∗∗∗ 13.81∗∗∗ 13.34∗ 22.06∗∗ ..." (Panel A); "pre-TRA 1.93∗∗ 7.05∗∗ 10.37∗∗ 9.03 12.83 ..." (Panel B, DOW and EOM FE) | Table A.1 | WZ 2025 | working-paper | same |
| C4 day definition | Monday 15:00 ET release, so the pre-TRA day is usually a Friday | "typically released on a Monday between the first and second months of a quarter at 3 PM ET"; "since most TRAs occur on Mondays, the pre-TRA day is typically a Friday" | Section 2, p. 8; Section 4.1, p. 14 | WZ 2025 | working-paper | same |
| C4 depends on FOMC timing | FOMC Earlier 23.65 (SE 6.15); FOMC Far 4.40 (6.50); FOMC Later 3.60 (6.74) | "positive pre-TRA returns are present almost exclusively when an FOMC announcement occurs within the preceding five days" | Section 5, p. 30-31; Table 11 Panel A | WZ 2025 | working-paper | same |
| C4 depends on the last rate decision | after a cut, 10Y -21.34 (SE 11.87) relative to no change at 13.95 | "the pre-TRA drift is strongest and most statistically significant when the Federal Reserve maintains rates unchanged ... it becomes negative following rate cuts" | p. 31; Table 11 Panel B | WZ 2025 | working-paper | same |
| C4 weak subsamples | Q2 -2.81 [-0.36]; recession -2.18; downward curve 4.71 [0.36]; surplus -7.81 | "Q2 32 1.30 [0.44] -1.60 [-0.36] -2.81 [-0.36]" | Table 6 Panels C, F, G, H | WZ 2025 | working-paper | same |
| C4 not yet replicated; cited by one paper | none | "Wang and Zhao (2024) study Treasury pre-refunding announcement effects, finding statistically significant drops in yields ahead of the Monday funding estimate announcements but no average yield changes either during funding estimate announcements or during Wednesday QRAs." | Section 1, p. 3 | Hartley, Rigon, Hoover Economics WP 26112, April 2026 | working-paper | pages/DF3/hartley_rigon_2026_hoover26112.pdf |
| QRA announcements are mostly anticipated | few moves over 1 bp | "Relatively few QRAs elicit market reactions greater than one basis point ... consistent with the 'pre-announcement effect' documented by Wang and Zhao (2024)." | Section 4.1 | Hartley, Rigon 2026 | working-paper | same |
| C5 window, futures, statistics | 19:00 ET day -2 to 12:00 ET day -1; 7.26 bp, t 2.82; rest of day -1 -2.05 (t -1.76) | "The average cumulative return on U.S. Treasury futures begins to rise at 19:00 ET on day -2, coinciding with the start of the Tokyo market, and peaks at 12:00 ET on day -1, aligning with the closing of the London market. The average 10-year Treasury return over this non-U.S. trading window is approximately 7.26 basis points, with a statistically significant t-statistic of 2.82." | Section 3.1, pp. 12-13 | PP26 | working-paper | reports/stage_e20_briefs/pages/ZT/pan_peng_fomc_2026.pdf (identical to pages/DF3/saif_FOMC_new.pdf) |
| C5 instrument: the 10-year note futures contract | futures, front contract by volume | "We use 10-year U.S. Treasury note futures, which trade almost around the clock ... tick-by-tick data on E-mini Treasury futures from January 2004 to June 2025 from the Chicago Mercantile Exchange (CME) ... we select the most active futures contract with the highest trading volume." Figure 2 caption: "The blue line reports returns on 10-year Treasury note futures" | Section 2, pp. 8-9; Figure 2 caption | PP26 | working-paper | same |
| C5 window picked from the average-return figure | post hoc (Tokyo open to London close) | "we mark the opening and closing times of the Tokyo and London markets in Figure 2 ... The futures markets for both stocks and Treasuries close at 17:00 ET and reopen at 18:00 ET" | Section 3.1, p. 12 | PP26 | working-paper | same |
| C5 sample and N | 250 scheduled FOMC meetings, 1994-09..2025-12 (daily); the intraday futures N is not stated | "Our main sample period for the pre-FOMC drift in both markets runs from September 1994 to December 2025 ... we have 250 scheduled FOMC announcements"; footnote 8: "We have missing futures trading data on several trading days ... January 29, 2014, is a scheduled FOMC release day." | Section 2, p. 8 | PP26 | working-paper | same |
| C5 earlier draft: same window, smaller t | 6.9 bp, t 2.24; rest of day -2.40 (t about -1.95); sample 2004-01..2025-07 | "The average 10-year Treasury return over this foreign trading period is approximately 6.9 basis points, with a statistically significant t-statistic of 2.24. In contrast, during the remainder of the day (12:00 ET-17:00 ET) leading up to the FOMC meeting, the return is around -2.40 basis points, with t-statistic around -1.95." | Section 3, p. 12-13; Figure 5 caption | PP25 (Dec 26 2025 draft, AFA 2026 program) | working-paper | pages/DF3/aea2026_pan_peng.pdf |
| C5 day convention | day 0 = announcement day = second day of the meeting | "After 1994, day 0 is the actual announcement day, which is the second day of the two-day FOMC meetings."; "the day before the FOMC, which is also the first day of the two-day FOMC meeting" | Appendix B, p. 53; Introduction, p. 2 | PP26 | working-paper | same |
| C5 daily measure | 10Y zero-coupon yield -0.79 bp on day -1 | "Over the 24-hour window that ends at the market close of the day before the FOMC announcement, the 10-year zero-coupon bond yield drops by a significant 0.79 basis points" | Introduction, p. 2 | PP26 | working-paper | same |
| C5 robustness: QE regime and crisis exclusion | futures 10Y [-1] const -1.00 [-2.19] with QE/QT controls; excluding 2008-09: -0.92 [-2.50], N 234 | "Panel C: Excluding 2008-2009 ... Mean -0.7 -0.92 -0.79 ... [-2.25] [-2.50] [-2.69] ... N 234" | Table A2 | PP26 | working-paper | same |
| C5 pattern changes after March 2022 | qualitative | "Prior to this date, yield declines within the three-day FOMC window are overwhelmingly concentrated on the day preceding the announcement, with little systematic response on the announcement day itself. After March 2022, however, this pattern changes markedly." | Section 3.3, p. 16 | PP26 | working-paper | same |
| Earlier work (Lucca-Moench): no pre-FOMC Treasury drift in the 2pm-to-2pm window | null 1994-2011 | "we find no such effect in U.S. Treasury securities and money market futures"; "For the 1994-2011 sample none of the coefficients is statistically significant at conventional confidence levels." | Abstract; Section 3.7, p. 16 | Lucca, Moench, FRBNY SR 512 (J. Finance 2015) | peer-reviewed | reports/stage_e10_research/calendar/lucca_moench_sr512.pdf |
| PP26 explains the difference from Lucca-Moench by timing | the window starts earlier | "Treasury prices adjust before the standard 24-hour pre-announcement window studied in the equity literature begins." | Section 3.1, p. 12 | PP26 | working-paper | same as PP26 |
| Hillenbrand (2025): three-day FOMC windows capture the secular decline in long yields | pre-FOMC day -3.09 pp of 7.91 pp (1989-2025) | "the 10-year yield declined by approximately 3.09% over the pre-FOMC window from June 1989 to 2025, accounting for nearly 40% of the total 7.91 percentage-point decline over the three-day window" | Section 3.3, p. 15 | PP26 (replicating Hillenbrand 2025, RFS) | working-paper; Hillenbrand [secondary-only] | same |
| Equity pre-FOMC drift disappeared after 2015 | qualitative | "the pre-FOMC drift essentially disappeared after 2015 in both announcements accompanied by press conferences and announcements not accompanied by press conferences" | Abstract | Kurov, Wolfe, Gilbert, FRL 40 (2021), accepted draft | peer-reviewed | reports/stage_e10_research/calendar/kurov_wolfe_gilbert_2020.pdf |
| WZ contrasts its effect with the equity decay | qualitative | "In contrast to the declining pre-FOMC drift in equity markets documented by Kurov, Wolfe, and Gilbert (2021), the pre-TRA effect has intensified in recent years." | Section 4.1.1, p. 15 | WZ 2025 | working-paper | as WZ |
| An independent thesis finds a pre-FOMC Treasury yield drop | about 1 bp on the day before | "pre-FOMC announcement drift exists in terms of Treasury yields declining by 1 bps on the day before the announcement" | Abstract (DSpace metadata) | Li, Xinyang, "Two essays on treasury bond risks", Boston University PhD thesis 2022 | thesis [secondary-only] | pages/DF3/bu_li_2022_thesis_item.json |
| Overseas cash Treasury spreads are wider (1994) | 5-year: 1.5/100 NY, 2.0 London, 2.5 Tokyo | "Bid-ask spreads are found to be wider overseas than in New York and wider in Tokyo than in London."; "the five-year note's spread is 1.5/100ths of a point in New York, 2.0/100ths in London, and 2.5/100ths in Tokyo" | Summary p. 9; p. 19 | Fleming, FRBNY Economic Policy Review, July 1997 | peer-reviewed (Fed review) | pages/DF3/nyfed_fleming_1997_epr.pdf |
| Futures carry more of the risk volume outside U.S. hours, especially the 10-year | 84/12/4% of DV01 in US/Europe/Asia hours; the 10-year future is 16% of US-hours DV01 and over 30% outside US hours | "Of total DV01 volume over the sample, 84% is traded during U.S. trading hours, 12% during European trading hours, and 4% during Asian trading hours."; "The 10-year futures contract comprises 16% of risk volume during U.S. trading hours, but over 30% of volume outside those hours." | p. 5-6 (Fig. 3, July 2017-June 2018) | Baker, McPhail, Tuckman, CFTC OCE note, Dec 3 2018 | exchange-regulator | pages/DF3/cftc_liquidity_hierarchy_2018.pdf |
| Cash liquidity is better on pre-TRA days | 30Y spread 0.5 bp lower | "on pre-TRA days, 30-year Treasurys have on average 0.5 bps lower bid-ask spread and 50 more dealer quotes per 10-minute interval compared to non-TRA days" | Section 4.3, p. 19 | WZ 2025 | working-paper | as WZ |
| Program's own ZN book data (D8): the overnight round trip equals the day round trip | 18:00-18:30 CT RT 1.1677 ticks; median best bid/ask 978/956 lots, against 3,621/3,482 at 11:00-11:30 CT and 2,125/1,975 at 07:00-07:30 CT | rows "18:00-18:30 \| \| 5/5 \| \| 0.5000 ... 978 \| 956 ... 1.1677 \| 18.245" and "11:00-11:30 \| D \| 5/5 ... 3621 \| 3482 ... 1.1677" | ZN (rates) bucket table, around l.2738-2780 | reports/stage_e2a_costs.md (D8; mbp-1 on 5 dates, 2025-05-14..2026-04-15) | program measurement, not published | (repo report) |

## 4. Negative evidence

- C4 is cash or ETF evidence only. ZN futures are never tested, and the intraday result exists only
  as a figure. The calendar controls shrink the 10-year effect from 12.62 to 9.40 bp (SE 4.03,
  t about 2.33). Most of the effect sits in one conditional cell: "FOMC Earlier" 23.65 bp against
  "FOMC Far" 4.40 and "FOMC Later" 3.60, neither significant. After rate cuts the effect turns
  negative (-21.34 relative). Q2 is -2.81. The effect is not significant pre-2002 (6.48, t 1.03).
- C4 has no replication. OpenCitations returns [] for all three DOIs (osf xucf8, xucf8_v2, ssrn
  4764295). The only citing paper DF3 found, Hartley-Rigon 2026, cites it and does not re-test it.
- C5's window was chosen after looking at the data: the authors read the start and the peak off
  their own average-return figure. Between drafts the t-statistic for the same window moved from 2.24
  to 2.82 (6.9 to 7.26 bp) on almost the same sample (2004-01..2025-07 against 2004-01..2025-06). The
  rest of day -1 gives back -2.05 bp (t -1.76). There is no post-2015 subsample. After March 2022 the
  yield decline moves to day 0. The QE3 coefficient is positive (+1.92**, which works against the
  drift) and the QT coefficient is +0.35. Lucca-Moench found no Treasury effect in the 2pm-to-2pm
  window, and the equity analogue disappeared after 2015 (KWG 2021).
- Secular trend: PP26 links the day -1 decline to the 1989-2020 fall in long rates. Rates did not
  fall like that in 2022-2026, and DF3 found no subsample for that period.

## 5. Data, cost and event dates (2025-04-01..2026-06-19)

- Data: ZN 1-minute bars cover the research window (owned). The FOMC dates are in the owned
  calendars. The TRA dates are not owned; they are free on the Treasury pages below. Neither
  candidate needs a purchase.
- Quarterly refunding primary releases (financing estimates, Monday 15:00 ET; the 15:00 time comes
  from the Treasury "most recent documents" page, "DOCUMENTS RELEASED at 3:00 PM Monday, august 3,
  2026"). Pre-TRA day = the trading day before. DF3 checked no holidays beyond weekday and month-end.

| Quarter | Primary release (press release) | Quote | Wednesday refunding statement | Pre-TRA day | Most recent FOMC before (WZ Table 11 cell; DF3 mapping, the lead checks) |
|---|---|---|---|---|---|
| 2025 Q2 | Mon 2025-04-28 (sb0115) | "Treasury Announces Marketable Borrowing Estimates April 28, 2025" | 8:30 a.m. Wed Apr 30 2025 | Fri 2025-04-25 | Mar 19 hold; next FOMC May 7 (7 business days later, likely "Far") |
| 2025 Q3 | Mon 2025-07-28 (sb0209) | "... July 28, 2025" | Wed Jul 30 2025 | Fri 2025-07-25 | Jun 18 hold; FOMC Jul 30 two days after the TRA ("FOMC Later") |
| 2025 Q4 | Mon 2025-11-03 (sb0300) | "... November 3, 2025" | Wed Nov 5 2025 | Fri 2025-10-31 (month-end) | Oct 29 cut ("FOMC Earlier" plus "Cut") |
| 2026 Q1 | Mon 2026-02-02 (sb0377) | "... February 2, 2026" | Wed Feb 4 2026 | Fri 2026-01-30 (month-end) | Jan 28 hold ("FOMC Earlier") |
| 2026 Q2 | Mon 2026-05-04 (sb0485) | "... May 4, 2026" | Wed May 6 2026 | Fri 2026-05-01 | Apr 29 hold ("FOMC Earlier") |

Rate decisions come from federalreserve.gov/monetarypolicy/openmarket.htm (effective dates): "December 11
0 25 3.50-3.75 October 30 0 25 3.75-4.00 September 18 0 25 4.00-4.25". The 2026 table shows only
"September 17 25 0 3.75-4.00", so 2026 had no change before September.

- Scheduled FOMC statements (federalreserve.gov/monetarypolicy/fomccalendars.htm): 2025 "May 6-7",
  "June 17-18*", "July 29-30", "September 16-17*", "October 28-29", "December 9-10*"; 2026 "January
  27-28", "March 17-18*", "April 28-29", "June 16-17*". That is 10 statements in the window (the
  August 22 2025 notation vote is not a meeting). C5's entry on the evening of day -2 at 18:00 CT,
  Monday: 2025-05-05, 06-16, 07-28, 09-15, 10-27, 12-08; 2026-01-26, 03-16, 04-27, 06-15. Exit 11:00 CT
  on the next day (the first meeting day). Note: 2025-07-28 is also a TRA day (primary release 14:00
  CT), so that C5 entry comes 4 hours after a TRA release.
- ET to CT is always one hour (both zones change for DST on the same dates). So 19:00 ET is 18:00
  CT, 12:00 ET is 11:00 CT, and 07:30-17:00 ET is 06:30-16:00 CT.
- ZN overnight liquidity: no published source gives ZN spread or depth by hour (CME pages are off
  limits to automation; the CME "Interest Rate Futures Liquidity Update" appeared only as a search
  hit and was not opened). Published context: CFTC 2018 (futures carry more of the off-hours risk
  volume, and the 10-year future is "over 30%" of it); Fleming 1997 (cash spreads wider overseas). The
  program's own D8 table (stage_e2a_costs.md) answers the cost question directly: 18:00-18:30 CT RT
  1.1677 ticks, the same as the day buckets (1.1677-1.1685), with a 1-tick spread on all 5 dates. Top
  of book is about 960-980 lots at 18:00 CT against about 3,500 around 11:00 CT. Since q_c is 1, a
  1-lot order pays no depth term. So the synthesis's "overnight cost [unverified]" for C5 can be
  replaced by D8's 1.168 ticks (D8 measurement, 5 dates).

## 6. Prop compatibility

- C4: the paper's window ends at 17:00 ET (16:00 CT), and Topstep flattens at 15:10 CT, so the last
  50 minutes are lost. By WZ's text, most of the gain comes "in the morning". A Friday pre-TRA session
  has no scheduled Tier 1 release on these 5 dates as far as DF3 checked from the calendars above. NFP
  and CPI dates come from the owned calendars, which DF3 did not open; the lead checks them. One ZN at
  1 lot.
- C5: 18:00 CT Monday to 11:00 CT Tuesday lies inside one Topstep trading day (17:00-15:10 CT). P06:
  no FOMC statement falls inside the hold (the statement is on day 0). Releases at 07:30 CT on day -1
  (for example retail sales or CPI on a Tuesday) can fall inside the hold; the lead checks them
  against the owned calendars. Whether TopstepX lists ZN was not checked by DF3 (R9 owns that).

## 7. Overlap with tested mechanisms (r0_mechanism_index.md)

- C4: no member uses TRA dates. K2-monthend-01 (dates N-1 and N, 07:20-15:04 CT, long ZN among 6
  roots) shares 2025-10-31 and 2026-01-30 with C4's five dates. E23-MEZNh5 is K2-monthend-01 held for
  5 days. WZ's EOM fixed effect absorbs part of this (12.63 to 9.40). K2-aucpre/aucpost-01 and E16-H3
  use auction dates; WZ: "our pre-TRA windows do not coincide with auction dates" (footnote 5).
- C5: K2-fomcpost-01 (day 0, 13:29-15:04 CT) and K5-fomc-01 (MGC, day 0) are disjoint in time. E-H1
  (D.1, MES; FOMC/CPI/NFP dates, overnight-through-day hold from about 17:00 CT the prior evening)
  covers the evening before the release on MES, not ZN on day -1. Gate 0 g13-g15 hold release-clock
  features on ZF only.

## 8. Earlier verdicts or closures

- E.20 rates_class_notes "FOMC: no pre-drift": WEAKENED (RD2 already said so). DF3 adds that the
  supporting t moved between drafts (2.24 to 2.82), so the claim rests on one unreplicated working
  paper. The independent Li 2022 thesis abstract also reports a 1 bp day -1 decline
  [secondary-only].
- V38 sentence about published post-2015 intraday effects: for C4, WEAKENS only as far as the cash
  evidence goes. No futures and no post-2015 intraday subsample are published, and the intraday
  figure has no number. For C5, no post-2015 split exists.

## 9. Fetch log

| url | UTC | sha256 | saved path | status | tool |
|---|---|---|---|---|---|
| https://home.treasury.gov/robots.txt | 2026-10-18T13:24Z | (saved) | terms/home.treasury.gov_robots.txt | ok | curl |
| https://home.treasury.gov/subfooter/site-policies-and-notices | 2026-10-18T13:24Z | 2d636361100bed666310ae53003980311a2843b093ced3f0e2135f3374b66ef3 | terms/home.treasury.gov_terms.html | ok | curl |
| https://home.treasury.gov/policy-issues/financing-the-government/quarterly-refunding | 2026-10-18T13:24Z | 6e175a37e1c870ae795c478776fc6930987cf048ce4f23a67f6b4a6b7a136056 | pages/DF3/treasury_qr_main.html | ok | curl |
| .../quarterly-refunding/quarterly-refunding-archives | 2026-10-18T13:24Z | 918554a558425d0252628737ae06757bd94114c71be631ce2266f6525d6326f1 | pages/DF3/treasury_qr_archives.html | ok | curl |
| .../quarterly-refunding/most-recent-quarterly-refunding-documents | 2026-10-18T13:24Z | 80018d32e83293afae47ebb463596f401e9ef58e4c90af2d9509313df913cdcb | pages/DF3/treasury_qr_recent.html | ok | curl |
| .../quarterly-refunding-archives/quarterly-refunding-financing-estimates-by-calendar-year | 2026-10-18T13:25Z | c4112a5d65c14a0d814a7df5a0a7f09f38806d7172c29f91b4e3562a9dc79692 | pages/DF3/treasury_qr_financing_estimates.html | ok | curl |
| https://home.treasury.gov/news/press-releases/sb0115 | 2026-10-18T13:25:25Z | 7d8aad37e2f1f79d2051fddff6b910509a46be014a129054ddbfeef70c3b9433 | pages/DF3/treasury_pr_sb0115.html | ok | curl |
| https://home.treasury.gov/news/press-releases/sb0209 | 2026-10-18T13:25:31Z | ecd6eda0f4c8411d8ab8f9c2b33f84297446a5508ad303b63c05faf296793776 | pages/DF3/treasury_pr_sb0209.html | ok | curl |
| https://home.treasury.gov/news/press-releases/sb0300 | 2026-10-18T13:25:37Z | c8cccddd41cf8a4506c8c9a53c8bdb96930b85859ddf0d29bf8c840621af1922 | pages/DF3/treasury_pr_sb0300.html | ok | curl |
| https://home.treasury.gov/news/press-releases/sb0377 | 2026-10-18T13:25:43Z | 7b095ff35cebc127db455feed981467733de220505209374822f313985158e2e | pages/DF3/treasury_pr_sb0377.html | ok | curl |
| https://home.treasury.gov/news/press-releases/sb0485 | 2026-10-18T13:25:49Z | 1ebeee69e06b8b38914145258f4c4d0def7918d3c483ad5b255fc91befb64aa7 | pages/DF3/treasury_pr_sb0485.html | ok | curl |
| https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | 2026-10-18T13:26:16Z | ddd866a47975153228b5100ff759ccf4e4ccd3c2b1dada5985e60e8a9641bc2a | pages/DF3/fed_fomccalendars.html | ok | curl |
| https://en.saif.sjtu.edu.cn/robots.txt | 2026-10-18T13:28Z | f105827f427cadb13f5891d99078447aeab7c57d64f8a2de2387c5312ce21ed9 | terms/en.saif.sjtu.edu.cn_robots.txt | ok | curl |
| https://en.saif.sjtu.edu.cn/junpan/FOMC_new.pdf | 2026-10-18T13:28:47Z | 06a73bf324594a0c01693c89c8b84e87724ad837f83607fd2ff3c4816f16326d | pages/DF3/saif_FOMC_new.pdf | ok (identical to E.20 copy) | curl |
| https://en.saif.sjtu.edu.cn/junpan/slide_FOMC_AFA.pdf | 2026-10-18T13:28:58Z | bb9da6d2efc40abc700a23b37b4fcaf84a85bccc1f096a7820cfcbd9476605b3 | pages/DF3/saif_slide_FOMC_AFA.pdf | ok (no window numbers) | curl |
| https://en.saif.sjtu.edu.cn/junpan/slide_FOMC_CUHK.pdf | 2026-10-18T13:29:10Z | 3816eac6b611c0581c154b4b507d97473d3be7144b614527ac26defe2196ede1 | pages/DF3/saif_slide_FOMC_CUHK.pdf | ok (no window numbers) | curl |
| api.crossref.org works queries (WZ, PP titles; 4 DOIs) | 2026-10-18T13:29-13:30Z | n/a | scratch only | ok | curl |
| api.opencitations.net/index/v2/citations/doi:{10.31235/osf.io/xucf8, xucf8_v2, 10.2139/ssrn.4764295, ssrn.4764451} | 2026-10-18T13:30Z | n/a | (empty arrays) | ok, 0 citers each | curl |
| https://www.hoover.org/research/does-government-debt-management-matter-high-frequency-identification-us-treasury-quarterly | 2026-10-18T13:30:33Z | b1fb490c66319b98af0a70b57bcef0f69e069541c9728944757fd91f7d2c63f4 | pages/DF3/hoover_debt_mgmt_qra.html | ok | curl |
| https://hoover-s3-website.s3.us-west-2.amazonaws.com/s3fs-public/research/docs/26112-Hartley-Rigon.pdf | 2026-10-18T13:30:42Z | c1fd7efdceec3ef3699e6370a66587b452721ad2d011e5584acceabb0854e2be | pages/DF3/hartley_rigon_2026_hoover26112.pdf | ok | curl |
| https://www.cftc.gov/sites/default/files/2018-11/Liquidity%20Hierarchy%20in%20Tsy%20Mkt%20v4_ada.pdf | 2026-10-18T13:31:20Z | 1c36ae6de56d2662ed796739a36c1c15806fdc54af1dec47a0b6dc8b6d8483b6 | pages/DF3/cftc_liquidity_hierarchy_2018.pdf | ok | curl |
| https://www.newyorkfed.org/medialibrary/media/research/epr/97v03n2/9707flem.pdf | 2026-10-18T13:31:38Z | 8490afbe1c4e41d43e3e19b2ba5de4ca2ed380c8b025393dadf0a697c70d602b | pages/DF3/nyfed_fleming_1997_epr.pdf | ok | curl |
| https://www.federalreserve.gov/monetarypolicy/openmarket.htm | 2026-10-18T13:31:50Z | 9d6c7d2f5c5caebb4e619842bd3de5a0dd2d7ed85e28c23de261c8137074cd6b | pages/DF3/fed_openmarket.html | ok | curl |
| https://ftp.aeaweb.org/conference/2026/program/paper/nNSh7NKz | 2026-10-18T13:32:11Z | fab221fbe86ea3811acf46c171d41a4d94aa34c393d80303c03c1746f14f3c30 | pages/DF3/aea2026_pan_peng.pdf | ok (Dec 26 2025 draft) | curl |
| https://open.bu.edu/robots.txt | 2026-10-18T13:32Z | (saved) | terms/open.bu.edu_robots.txt | ok | curl |
| https://open.bu.edu/server/api/core/items/782a5fec-f2ff-4c2e-b327-2dcbbfcf6ce5 | 2026-10-18T13:32Z | 6c877f425db57bf8f0ce8dadcb3e8855c4433d5a1c79415227c069fe93f6efe5 | pages/DF3/bu_li_2022_thesis_item.json | ok (metadata and abstract only) | curl |

Terms lines appended by DF3: home.treasury.gov, en.saif.sjtu.edu.cn, open.bu.edu. Cited from other
readers' lines: osf.io (RD2), www.federalreserve.gov (R5), www.newyorkfed.org (RD2), www.cftc.gov (R8),
www.hoover.org (R6), www.aeaweb.org (R1), api.crossref.org and api.opencitations.net (already logged
13:23Z). WebSearch calls used: 7 of the 25 allowed. No over-budget notice. Firecrawl, OpenAlex and
Semantic Scholar were not called. No scrapling fetches, so no memory guard was needed. No cmegroup.com
or SSRN fetch.

## 10. Unfinished and unverified

- The intraday N for PP26's 7.26 bp is not stated. The implied per-meeting sd of about 33.7 bp (about
  23.9 ZN ticks) assumes N of about 171 and is DF3's inference, not a published number.
- No published source gives ZN spread or depth by hour. The CME liquidity reports could not be fetched
  (automation ban). D8's figure is the program's own measurement.
- Hillenbrand (2025, RFS) was read only through PP26 [secondary-only]. Li 2022: abstract only
  [secondary-only].
- Not checked: NFP/CPI/retail-sales coincidences on the 5 pre-TRA days and the 10 C5 holds (owned
  calendars; the lead checks); whether TopstepX lists ZN (R9).
- Cell labels for WZ Table 11 ("FOMC Earlier/Later/Far") for the 5 window events are DF3's mapping
  using "within five business days"; the lead verifies.
