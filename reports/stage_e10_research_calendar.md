# Stage E.10 research log: Reader 3, calendar effects (C1, C2, C3)

- Reader: LitReader-Calendar-OpusHigh. Model: Opus 5.5 (claude-opus-5-5), effort high.
- Start: 2026-10-02 22:32 PDT. End: see the closing line of this log.
- Inputs read: reports/stage_e10_search_plan.md (common rules, Reader 3 topics), reports/stage_e10_design_target.md
  sections (a)-(c), reports/stage_e10_briefs/e0_logged_sources.txt (grep only).
- Counts:
  - Records screened: 440 OpenAlex records (21 keyword queries x 20, plus 5 title-filtered futures queries that
    returned 20 records in total) plus about 190 WebSearch result links (20 calls). Semantic Scholar: 1 call,
    HTTP 403 (the SEMANTIC_SCHOLAR_API_KEY line in .env holds a 1-character value, so no usable key; an
    unauthenticated retry returned HTTP 429). Semantic Scholar was not used after that; OpenAlex replaced it.
  - Sources logged: 22 (K9C-001 to K9C-022).
  - Full text: 15. Abstract only: 7 (K9C-011, -012, -016, -017, -021, -022 from publisher or RePEc abstract pages;
    none of them is load-bearing for a candidate except as conflicting evidence).
  - Blocked or failed fetches: 9 (see the fetch log: tandfonline x2 HTTP 403, DIW 403, Skidmore 404 (recovered
    from the Wayback Machine), economic-research.pl 404, ojs.aut.ac.nz 404, UCD repository behind a human
    verification page, cesifo.org first attempt an HTML stub (recovered with a referer), two NBER URLs that served
    the wrong paper).
  - WebSearch calls used: 20 of 120. No over-budget notice was seen. Firecrawl: not used.
- Stop reason per topic:
  - C1 (day of week, turn of week): saturation. The last OpenAlex queries (c1d to c1h, about 100 records) and the
    title-filtered futures queries added no new mechanism beyond the weekend/Monday seasonal already logged.
  - C2 (announcement-day premia): saturation. The last 3 OpenAlex queries (c2i to c2k, 60 records) and the last two
    WebSearch calls added no mechanism beyond the full-day announcement premium, the pre-announcement uncertainty
    premium, the FOMC cycle and the FOMC-day FX premium.
  - C3 (pre-holiday, options expiration, seasonal months): saturation within the queries run (c3a to c3c and two
    WebSearch calls, the last 15 records added nothing new). Index-level options-expiration evidence was found
    only in practitioner blogs (not logged as evidence).
- Incident (logged for the lead): my first fetch helper lived in the shared scratchpad and was overwritten by
  another reader's helper at 22:34 PDT, so four of my PDFs (lucca_moench_sr512, hu_pan_wang_zhu_w25817, and two
  wrong-paper downloads) were written into reports/stage_e10_research/regime/ and four rows into
  regime/api/fetchlog.tsv. At 22:37 PDT I moved my four files to calendar/, copied their rows (same UTC time and
  sha256) into calendar/fetchlog.tsv, and deleted exactly those four rows from the regime log. Nothing else of the
  regime reader was touched. From then on my helpers ran from scratchpad/calendar_reader/.
- Unit conversions in the reader's notes: the design target gives M_X and G(f) in ticks of the vehicle. To compare
  with sources quoted in basis points I convert with price levels that are the reader's own round assumptions,
  not program data: NQ 20,000 (MNQ tick 0.25 pt = 0.125 bp), Russell 2,200 (M2K tick 0.1 pt = 0.45 bp), Dow 44,000
  (MYM tick 1 pt = 0.23 bp), ZF 108 (tick 1/128 pt = 0.72 bp), ZN 111 (tick 1/64 pt = 1.41 bp), ZB 115 (tick
  1/32 pt = 2.72 bp), AUD 0.65 (6A tick 0.00005 = 0.77 bp), bitcoin 100,000 (MBT tick 5 pts = 0.5 bp). The resulting
  bp figures for M_X and G(f): MNQ M 2.0 bp, G(0.2) 107 bp, G(0.1) 213 bp; M2K M 8.6 bp, G(0.2) 115 bp; MYM M 5.2 bp,
  G(0.2) 65 bp; ZF M 2.8 bp, G(0.2) 22.5 bp; ZN M 4.9 bp, G(0.2) 22.8 bp; ZB M 9.2 bp, G(0.2) 30 bp; 6A M 5.7 bp,
  G(0.1) 87 bp; MBT M 16 bp, G(0.2) 230 bp. The lead should redo these with the program's own prices.
- Calendar arithmetic for the 299-date window (2025-04-01 to 2026-06-19), by the reader, from the calendar only:
  319 weekdays (63 Mondays, 64 each Tuesday-Friday); 15 third Fridays. CME holidays and other exclusions remove
  about 20 weekdays, so Mondays are about 58 trade dates (five Monday holidays) and Fridays about 60. Monthly BLS
  releases in the window: about 15 each for employment, CPI and PPI (April 2025 to June 2026), fewer if the autumn
  2025 federal shutdown cancelled or merged any release (the reader did not fetch the BLS archive; the lead should
  count from it). Scheduled FOMC announcement days in the window, from the reader's knowledge of the Fed calendar
  and NOT verified from a fetched page: 2025-05-07, 06-18, 07-30, 09-17, 10-29, 12-10, 2026-01-28, 03-18, 04-29,
  06-17 (10 dates). Pre-holiday trade dates (the trade date before a CME closure or holiday session): about 13.

---

## C2. Macro-announcement-day premia

### K9C-001 Savor and Wilson, announcement-day equity and bond premia
- Citation: Savor, Pavel; Wilson, Mungo (2013). "How Much Do Investors Care About Macroeconomic Risk? Evidence
  from Scheduled Economic Announcements." Journal of Financial and Quantitative Analysis 48(2), 343-375.
  DOI 10.1017/S002210901300015X.
- Retrieval: curl of the authors' accepted draft on the Wharton faculty site; reports/stage_e10_research/calendar/
  savor_wilson_2013_draft.pdf (.txt beside it). Full text (the 2011-11-28 edited draft, not the typeset version).
- Mechanism: the market earns a risk premium for bearing scheduled macroeconomic news risk; the expected excess
  return is higher on days when inflation (CPI before 1971, PPI after), employment or FOMC news is scheduled, and the
  premium is larger when uncertainty (market variance) is high. Long-maturity Treasuries also earn more on those days.
- Products and horizon: CRSP value-weighted stock index (cash, not futures), CRSP Treasury bond returns at 1, 5, 10,
  20 and 30-year maturities, 30-day T-bills. Horizon: one trading day, close to close.
- Sample window: January 1958 to December 2009 for stocks (FOMC from January 1978); 1961 to 2009 for Treasuries.
  Exact first and last trade dates not stated beyond month and year.
- Market and data frequency: US cash equity and Treasury markets, daily.
- Pooled release dates: PPI (CPI before February 1971), employment situation, scheduled FOMC decisions. 1,450
  announcement days against 11,641 other days (about 13% of trading days).
- Cost assumptions: none (no transaction costs; index returns).
- Quality tells: published JFQA; long sample; robustness to subsamples, outliers, each announcement type, calendar
  anomalies; mechanism stated ex ante from a model. Cash index, not futures. Unscheduled FOMC days strongly negative,
  which supports the scheduled-news reading.
- Verified passages:
  - P-K9C-001-a (abstract): "The average announcement day excess return from 1958 to 2009 is 11.4 basis points versus
    1.1 basis points for all the other days, suggesting that over 60% of the cumulative annual equity risk premium is
    earned on announcement days. The Sharpe ratio is ten times higher."
  - P-K9C-001-b (Introduction, p. 3): "over 60% of the cumulative annual excess return is earned on just 13% of the
    trading days, whose timing is known to investors well in advance."
  - P-K9C-001-c (Section III.A): "We have 157 pre-scheduled CPI announcements from January 1958 to January 1971 and 467
    for the PPI from February 1971 to December 2009." ... "We have 621 employment announcements from January 1958 to
    December 2009. FOMC interest rate announcements start in January 1978 and end in December 2009." ... "The remaining
    sample contains 1,450 announcement days versus 11,641 non-announcement days."
  - P-K9C-001-d (Section III.D): "For 5-year bonds, the return di¤erential is 2.6 bps (t-statistic = 2.57), and it then
    grows to 3.4 bps (t-statistic = 2.23), 4.1 bps (t-statistic = 2.04), and 4.5 bps (t-statistic = 2.02) for 10-, 20-,
    and 30-year bonds respectively."
  - P-K9C-001-e (Section III.D): "For a 1-year bond, the average announcement day excess return is actually 0.5 bps
    lower than the average on other days, with a t-statistic of 2.22."
  - P-K9C-001-f (Introduction, p. 4): "We estimate that a doubling of stock market variance increases the di¤erential
    by 60%."
  - P-K9C-001-g (footnote 1): "the average excess return on days of unscheduled FOMC announcements is strongly negative
    (-89.2 bps for 15 such days between 2001 and 2009)."
  - P-K9C-001-h (robustness): "the stock market excess return is higher on announcement days in 9 out of 10 periods".
  - P-K9C-001-i (Section III.A): "only 29 of the pre-scheduled announcements in our sample occurred on a Monday,
    representing about 2% of overall announcements."
- Numeric claims: equity announcement-day excess return 11.4 bp versus 1.1 bp (P-K9C-001-a); 13% of days (-b);
  bond differentials 2.6 / 3.4 / 4.1 / 4.5 bp for 5 / 10 / 20 / 30 years (-d); 1-year -0.5 bp (-e); higher with
  variance (-f); 9 of 10 five-year subperiods (-h).
- Conflicting evidence: K9C-004 (Ernst, Gilbert, Hrdlicka) attributes much of this premium to day-of-the-month
  timing (P-K9C-004-b, -c). K9C-011 finds the bond pre-announcement premium insignificant after the financial
  crisis (P-K9C-011-a). K9C-002 notes the bond premium is "moderate" (P-K9C-002-d).
- Reader's note: Fits the K9 shape on the date set: a pooled set of scheduled releases. In the window, the union of
  employment, CPI, PPI and FOMC days is about 50 to 55 trade dates (15 + 15 + 15 + 10 less same-day overlaps), 17-18%
  of 299, above the 40-trip requirement; the paper's own set (one inflation release a month, employment, FOMC) is about
  40 dates, at the requirement. Hold: the full trade date (the paper measures close to close, so by D-entry the entry
  is the 17:00 CT reopen and by D-exit the exit is at C_X - 2 min). Sign: long. Weekly cap: a week can hold CPI, PPI and
  employment together, so a third signal is sometimes skipped. Exclusions: not X4 (no signal read from a pre-release
  move; an unconditional long on the whole day), not X6 (no post-FOMC conditioning). Closest to X12 through the
  timing overlap K9C-004 documents (employment Fridays fall at the turn of the month). Size versus the cost wall: 11.4
  bp per day on the S&P cash index is about 5x M_X for MNQ (about 2 bp) but about one tenth of G(0.2) for MNQ (about
  107 bp) and about one sixth of G(0.2) for MYM (65 bp). For bonds, 3.4 bp (10-year) is below M_X for ZN (about 4.9
  bp), 4.5 bp (30-year) is below M_X for ZB (about 9.2 bp), and 2.6 bp (5-year) is at M_X for ZF (about 2.8 bp): the
  bond version does not clear the round-trip wall. Evidence is on the cash index, flagged.

### K9C-002 Ai and Bansal, risk preferences and the announcement premium
- Citation: Ai, Hengjie; Bansal, Ravi (2018). "Risk Preferences and the Macroeconomic Announcement Premium."
  Econometrica 86(4), 1383-1430. DOI 10.3982/ECTA14607 (volume, pages and DOI from the reader's memory, unverified).
- Retrieval: curl of the author-hosted version (Duke); calendar/ai_bansal_2018_econometrica.pdf (.txt). Full text
  (version dated January 28, 2018).
- Mechanism: a premium for the resolution of macroeconomic uncertainty exists only under generalized risk sensitivity
  (preference for early resolution); the premium is earned at the announcement for non-FOMC releases and before it for
  FOMC.
- Products and horizon: S&P 500 index excess return, daily; hourly windows around announcements.
- Sample window: 1961 to 2014 (years only).
- Market and data frequency: US equity, daily and hourly.
- Pooled release dates: the top five pre-scheduled announcements by Bloomberg user attention at monthly or lower
  frequency (about 30 days a year in 1961-2014). The constituent list is in its Appendix A (not extracted).
- Cost assumptions: none.
- Quality tells: Econometrica; theory-led; the empirical part is a stylized-facts section.
- Verified passages:
  - P-K9C-002-a (Introduction): "In the 1961-2014 period, during the thirty days per year with significant
    macroeconomic announcements, the cumulative excess returns of the S&P 500 index averaged 3.36%, which accounts for
    55% of the total annual equity premium of 6.19%. The average return on days with macroeconomic announcements is
    11.2 basis points (bps), which is significantly higher than the 1.27 bps average return on non-announcement days."
  - P-K9C-002-b (Section 2): "Most of the premiums for FOMC announcements are realized in several hours prior to the
    announcements. Premiums for other macroeconomic announcements are realized upon the release of these
    announcements."
  - P-K9C-002-c (Section 2): "There is a “pre-announcement drift” for FOMC announcements, but not for other
    macroeconomic announcements. The premiums for non-FOMC announcements are mainly realized at the announcement."
  - P-K9C-002-d (Section 2): "Savor and Wilson (2013) present evidence of a moderate level of announcement premiums
    for Treasury bonds, which averages about 3 bps on announcement days during the longer sample period of 1961-2009."
- Numeric claims: 30 days a year, 11.2 bp versus 1.27 bp, 55% of the premium (P-K9C-002-a); bond premium about 3 bp
  (-d).
- Conflicting evidence: on timing, K9C-006 finds the non-FOMC premium earned overnight before the release
  (P-K9C-006-a), against P-K9C-002-c. On size, K9C-004 (P-K9C-004-c).
- Reader's note: same candidate as K9C-001 (date set about 30 a year in the source; about 36 in the window). The
  timing claim matters for the hold: if the non-FOMC premium is realized at the release (P-K9C-002-c), a hold from the
  17:00 CT reopen through the release to F captures it; the D9 event-minute fill guard (5a) and the CPI window (12)
  only constrain the entry and exit minutes, not a position held through the release. Exclusion: none of X1-X15 by
  mechanism; X12 overlap as for K9C-001. Size: 11.2 bp, as in K9C-001's note (above M_X, about one tenth of G(0.2) on
  MNQ).

### K9C-003 Ai, Bansal and Guo, review with a sample to 2023
- Citation: Ai, Hengjie; Bansal, Ravi; Guo, Hongye (2023, revised December 2023). "Macroeconomic Announcement
  Premium." NBER Working Paper 31923. DOI 10.3386/w31923.
- Retrieval: curl of the NBER PDF; calendar/ai_bansal_guo_2023_w31923.pdf (.txt). Full text.
- Mechanism: as K9C-002 (review).
- Products and horizon: US stock market excess return, daily; S&P 500 E-mini futures for the pre-FOMC window.
- Sample window: 1961 to 2023 (years only) for Table 1; 2020-01 to 2023-08 for the recent sub-sample; September 1997
  to August 2022 for the E-mini pre-FOMC figure.
- Market and data frequency: daily; one-minute E-mini for the intraday figures.
- Pooled release dates: FOMC, non-farm payroll, GDP (first and last), ISM manufacturing PMI, and the earlier of CPI and
  PPI each month: 44 days a year.
- Cost assumptions: none.
- Quality tells: NBER review by the leading authors of the literature; it carries the sample forward to 2023, which is
  the most recent evidence found; it names the 2016-2019 weakness.
- Verified passages:
  - P-K9C-003-a (Section 1): "In this period, on average, 44 trading days per year have significant macroeconomic
    announcements. At the daily level, the average stock market excess return is 10.68 basis points (bps) on announcement
    days and 0.93 bps on days without major macroeconomic announcements. As a result, the cumulative excess stock market
    return on the 44 announcement days averages 4.65% per year, accounting for about 71% of the annual equity premium
    (6.59%)."
  - P-K9C-003-b (Table 1): "Ann               44          10.68 bps     4.65%        5.36" and "FOMC              10
    17.61 bps     1.74%        4.71" and "Non-FOMC          34          8.65 bps      2.91%        3.71"
  - P-K9C-003-c (Table 1 note): "The announcements are the FOMC, Non-farm payroll, GDP (first and last), ISM
    manufacturing PMI, and the earlier of the CPI and PPI announcements."
  - P-K9C-003-d (Section 1): "We combine the PPI and CPI announcements into one “inflation” announcement by using the
    earlier one each month, as they reveal information of a similar nature. This additional step becomes necessary
    because in recent years the CPI announcement starts to regularly occur before the PPI announcement"
  - P-K9C-003-e (Section 1): "the premium for the FOMC announcement was low between January 2016 and December 2019 and
    attribute the decline to reduced uncertainty over this period. Since then, the announcement premium has been above
    historical average. Specifically, from January 2020 to August 2023, the average announcement premium was 16.33 basis
    points per announcement, higher than the full sample average of 10.68 basis points."
  - P-K9C-003-f (Section 2): "we find that the 24-hour return before the pre-scheduled FOMC announcement during the
    period of September 1997 to August 2022 is 37.5 basis points on average."
- Numeric claims: 44 days a year, 10.68 bp versus 0.93 bp, t = 5.36 (P-K9C-003-a, -b); non-FOMC 8.65 bp, t = 3.71
  (-b); 16.33 bp per announcement in 2020-01 to 2023-08 (-e); pre-FOMC 24 h 37.5 bp on E-mini 1997-2022 (-f).
- Conflicting evidence: K9C-004 (day-of-month timing); K9C-007 (pre-FOMC drift gone 2016-2019, which -e acknowledges).
- Reader's note: The strongest single source for a K9 calendar member. Date set: the 44-a-year union in -c, which is
  about 52 dates in 299 by proportion (44 x 299 / 252), 17% of dates; or the non-FOMC 34 a year (about 40 dates). Hold:
  full trade date (daily close-to-close in the source; D-entry 17:00 CT reopen, D-exit C_X - 2 min). Sign: long.
  Products: MNQ, M2K, MYM (evidence on the US market index, flagged; not on the Nasdaq-100 or Russell 2000
  specifically). Weekly cap: ISM (first business day) and payrolls (first Friday) often fall in the same week as other
  releases; the K9 cap skips a third. Exclusions: not X4 or X6 by mechanism (no conditioning on a pre-release or
  post-release move); X12 timing overlap as in K9C-004 (ISM and payrolls cluster at the turn of the month). Size:
  10.68 bp per date (16.33 bp in 2020-2023) against MNQ M_X about 2 bp (clears) and G(0.2) about 107 bp (about one
  tenth; one sixth at the 2020-2023 level). Against MYM G(0.2) about 65 bp, about one sixth to one quarter.

### K9C-004 Ernst, Gilbert and Hrdlicka, how much is really earned on announcement days (conflicting)
- Citation: Ernst, Rory; Gilbert, Thomas; Hrdlicka, Christopher (2021, July 31 draft; first version 2019). "More than
  100% of the equity premium: How much is really earned on macroeconomic announcement days?" Working paper, University
  of Washington (AEA 2022 conference paper). SSRN DOI 10.2139/ssrn.3469703.
- Retrieval: curl of the AEA conference PDF; calendar/ernst_gilbert_hrdlicka_2021.pdf (.txt). Full text.
- Mechanism (critique): the prior literature's announcement days were selected from a large set of series, and
  announcements cluster on days of the month with high average returns; controlling for day-of-the-month fixed effects
  shrinks the per-day announcement premium and removes its joint significance; announcements as a whole carry about
  half the equity premium spread over 62% of days.
- Products and horizon: CRSP value-weighted market excess return, daily.
- Sample window: January 1990 to June 2018 (Table 1 and Table 2; series start dates from 1990-01-02).
- Market and data frequency: US equity, daily.
- Pooled release dates: all major monthly US series released in the sample (Table 2 lists 19 monthly series plus FOMC).
- Cost assumptions: none.
- Quality tells: by authors who also publish on the pre-FOMC drift (Gilbert is a co-author of K9C-007); it
  re-examines the prior papers' own day sets; working paper (not yet published at this version).
- Verified passages:
  - P-K9C-004-a (abstract): "One can earn well over 100% of the equity risk premium on macroeconomic announcement days
    identified by the prior literature. This is a robust phenomenon present across many other subsets of macroeconomic
    variables. We show how inadvertent sample selection along with the timing of macroeconomic announcements throughout
    the month produces this too-much-return puzzle."
  - P-K9C-004-b (Introduction, p. 4): "Including the day-of-the-month fixed effects lowers the average macroeconomic
    announcement fixed effect. Though the announcement fixed effects’ point estimates remain economically meaningful on
    average, they lose their joint statistical significance in the presence of the day-of-the-month fixed effects."
  - P-K9C-004-c (Introduction, p. 5): "macroeconomic announcements happen to occur on days with high average market
    returns, and may not in and of themselves be special." and "Controlling for the day-of-the-month fixed effects, the
    macroeconomic announcement fixed effects show that macroeconomic variables as a whole account for 56% of the equity
    premium."
  - P-K9C-004-d (footnote 5): "Only the FOMC fixed effects are routinely statistically significant."
  - P-K9C-004-e (Introduction, p. 5): "The Sharpe ratio on all macroeconomic announcement days after controlling for
    the day-of-the-month effect is 0.027, virtually the same as the Sharpe ratio on all days of 0.029."
  - P-K9C-004-f (Table 1): "Average market excess return         7.7***       -1.9        9.6***" with "N
    3,820      3,615" and "Percent of equity premium            149.1%" (days from Savor and Wilson, Lucca and Moench,
    and Cieslak et al. combined, January 1990 to June 2018).
  - P-K9C-004-g (Table 2 rows): "FOMC                   Federal Reserve 2/8/1990        6/13/2018   228    31.9%",
    "Unemployment Rate         Bureau of Labor Statistics 1/5/1990         6/1/2018   335    14.3%",
    "Producer Price Index      Bureau of Labor Statistics 1/12/1990       6/13/2018   340    12.9%",
    "Consumer Price Index       Bureau of Labor Statistics 1/18/1990       6/12/2018   340     6.3%"
- Numeric claims: union of prior-literature days earns 149.1% of the premium (P-K9C-004-f); with day-of-month
  controls announcements carry 56% (-c), only FOMC routinely significant (-d); Sharpe 0.027 vs 0.029 (-e); per-series
  shares: FOMC 31.9%, unemployment 14.3%, PPI 12.9%, CPI 6.3% (-g).
- Conflicting evidence: this source is itself the main conflict for K9C-001 to K9C-003.
- Reader's note: Decisive for the C2 candidate's interpretation. If the premium is a day-of-month effect, an
  announcement-day member partly re-tests the turn-of-month family X12 (employment reports fall on the first Friday,
  ISM on the first business day). The lead should rule whether a member keyed to release dates differs in mechanism
  from X12 when the source's own critique says the dates matter through their position in the month. Only FOMC days
  survive the controls, and FOMC alone (10 dates in the window) is below the 30-trip floor.

### K9C-005 Lucca and Moench, the pre-FOMC announcement drift
- Citation: Lucca, David O.; Moench, Emanuel (2015). "The Pre-FOMC Announcement Drift." Journal of Finance 70(1),
  329-371 (volume and pages from the reader's memory, unverified). DOI 10.1111/jofi.12196 (OpenAlex). Read as Federal Reserve Bank of New York Staff Report 512 (September 2011, revised
  August 2013).
- Retrieval: curl of the NY Fed staff report; calendar/lucca_moench_sr512.pdf (.txt). Full text. (Fetched through a
  misrouted helper, moved; see the header incident note.)
- Mechanism: US equities rise in the 24 hours before scheduled FOMC announcements (2 p.m. to 2 p.m. ET), with no
  reversal afterwards; unexplained by standard risk measures.
- Products and horizon: S&P 500 index (and futures, per K9C-007's footnote), international equity indices, Treasury
  securities and money-market futures; 24-hour window before 2:15 p.m. ET.
- Sample window: September 1994 to March 2011 (main); 1980 to 2011 including the pre-1994 analysis.
- Market and data frequency: intraday and daily.
- Cost assumptions: none.
- Quality tells: Journal of Finance; widely replicated; but see K9C-007 for post-publication decay.
- Verified passages:
  - P-K9C-005-a (abstract): "While other major international equity indices experienced similar pre-FOMC returns, we
    find no such effect in U.S. Treasury securities and money market futures. Other major U.S. macroeconomic new
    announcements also do not give rise to pre-announcement excess equity returns."
  - P-K9C-005-b (Introduction): "We document that since 1994, the S&P500 index has on average increased 49 basis points
    in the 24 hours before scheduled FOMC announcements. These returns do not revert in subsequent trading days"
  - P-K9C-005-c (Introduction): "about 80% of annual realized excess stock returns since 1994 are accounted for by the
    pre-FOMC announcement drift." and "a simple trading strategy of holding the index only in the 24 hours leading up to
    right-before an FOMC announcement would have yielded an annualized Sharpe ratio of above 1.1."
  - P-K9C-005-d (abstract): "Pre-FOMC returns are higher in periods when the slope of the Treasury yield curve is low,
    implied equity market volatility is high, and when past pre-FOMC returns have been high."
- Numeric claims: 49 bp in 24 h (P-K9C-005-b); about 80% of annual excess returns; Sharpe above 1.1 (-c); none in
  Treasuries (-a).
- Conflicting evidence: K9C-007 (gone after 2015, P-K9C-007-a, -b); K9C-006 Table 2 (FOMC pre-announcement 3.96 bp,
  insignificant in 2012-2018, P-K9C-006-e); K9C-003-e acknowledges 2016-2019 weakness.
- Reader's note: Date set 8 a year (10 in the window), below the 30-trip floor on its own. Hold: 13:00 CT prior day to
  13:00 CT announcement day spans two trade dates, so a K9 version (inside one trade date, flat by F) can only take the
  17:00 CT reopen to just before the 13:00 CT release (about 20 hours). Exclusion: X4 is "a pre-release drift on any
  release, unless the mechanism is shown to differ"; the pre-FOMC drift is unconditional (no signal read from the
  pre-release move), and its sources argue a risk-premium or news mechanism, so it is X4-adjacent; the lead rules.
  Size: 49 bp (1994-2011) is about half of MNQ G(0.2) (107 bp), but the frequency is f about 0.03, where G rises to
  several hundred bp. Usable only inside a pooled date set (K9C-006).

### K9C-006 Hu, Pan, Wang and Zhu, premium for heightened uncertainty before announcements
- Citation: Hu, Grace Xing; Pan, Jun; Wang, Jiang; Zhu, Haoxiang (2022). "Premium for Heightened Uncertainty:
  Explaining Pre-Announcement Market Returns." Journal of Financial Economics 145(3), 909-936 (volume and pages from the reader's memory, unverified).
  DOI 10.1016/j.jfineco.2021.09.015. Read as NBER Working Paper 25817 (May 2019, revised March 2021).
- Retrieval: curl of the NBER PDF; calendar/hu_pan_wang_zhu_w25817.pdf (.txt). Full text. (Misrouted helper, moved;
  see header.)
- Mechanism: uncertainty about the impact of impending news builds up before a scheduled release and resolves before
  it; the premium for this heightened uncertainty is earned in the pre-announcement window, mostly overnight, with low
  variance; post-announcement returns are small with high variance.
- Products and horizon: S&P 500 index futures (E-mini). Window: from the prior trading day's 4 p.m. ET close to 5
  minutes before the release (8:30 a.m. ET for NFP and GDP, 10 a.m. ET for ISM, about 2 p.m. ET for FOMC).
- Sample window: September 1994 to May 2018.
- Market and data frequency: intraday futures prices.
- Pooled release dates: NFP, ISM manufacturing, GDP, FOMC (44 a year; 36 a year without FOMC).
- Cost assumptions: none.
- Quality tells: JFE; futures data; sub-period table to 2018; explicit model with testable VIX predictions.
- Verified passages:
  - P-K9C-006-a (abstract): "We find large overnight returns, with no abnormal variance, before the release of nonfarm
    payrolls, ISM, and GDP, similar to the pre-FOMC returns."
  - P-K9C-006-b (Introduction): "From September 1994 to May 2018, the pre-announcement returns for NFP, ISM, and GDP are
    on average 10.1 bps, 9.1 bps, and 7.5 bps, respectively, and all statistically significant. Using S&P 500 index
    futures, these pre-announcement returns are calculated from the close of the previous trading day at 4 pm to 5
    minutes before the respective announcements, which are pre-scheduled at 8:30 am for NFP and GDP and 10 am for ISM."
  - P-K9C-006-c (Introduction): "Benchmarked against the average overnight return of 0.69 bps for non-announcement
    days, the pre-announcement returns documented in our paper are large economically" and "Post announcement, the
    average returns for NFP, ISM, and GDP are small and insignificant, while exhibiting large variances"
  - P-K9C-006-d (Section 2): "as shown in Bernile, Hu, and Tang (2016) and Kurov, Sancetta, Strasser, and Wolfe (2019),
    evidence on informed trading, if any, is only detected 30 minutes before macroe- conomic announcements."
  - P-K9C-006-e (Section 4, Table 2 text): "the sub-period performance for FOMC remains large and significant pre-2011
    and becomes insignificant during 2012–2018. By contrast, the performance of the non-FOMC macro announcements remains
    stable and significant across all three subperiods. In particular, during the last subperiod of 2012–2018, the
    pre-announcement return is on average 6.98 basis point and statistically significant for the non-FOMC macro
    announcements, compared with the statistically insignificant 3.96 basis points for the FOMC announcements."
  - P-K9C-006-f (Table 2, Panel A): "2012-2018             7.02             6.98              3.96
    5.14" (columns: All 4, Ex FOMC, FOMC, All Days close-to-close) and "1994-2018            12.86             9.48
    27.14                       3.61"
  - P-K9C-006-g (Section 2): "Pooling the four announcements together, the average pre-announcement return is 5.66%
    annually, realized over the pre-announcement windows of a mere 44 announcements per year." and "Excluding FOMC ...
    the average pre-announcement re- turn remains important and significant at 3.41% per year, realized over the
    pre-announcement windows, mostly overnight, of 36 announcements per year."
- Numeric claims: NFP 10.1, ISM 9.1, GDP 7.5 bp per event (P-K9C-006-b); overnight non-announcement 0.69 bp (-c);
  ex-FOMC 6.98 bp in 2012-2018, FOMC 3.96 bp insignificant (-e, -f); 44 and 36 events a year (-g).
- Conflicting evidence: P-K9C-002-c (Ai and Bansal: no pre-announcement drift for non-FOMC releases in their hourly
  data, 1961-2014 sample; the two papers use different windows, K9C-006 includes the overnight). Within K9C-006: in
  2012-2018 the ex-FOMC pre-announcement return (6.98 bp) is close to the all-days close-to-close return (5.14 bp) of
  the same sub-period (P-K9C-006-f), so the recent excess over an ordinary full day is small, although the window is
  only the overnight part.
- Reader's note: A K9 candidate in its own right. Date set: NFP, ISM manufacturing and GDP release dates (36 a year,
  about 43 in 299), optionally with FOMC (44 a year, about 52). Hold: from the 17:00 CT reopen to 07:25 CT for 07:30 CT
  releases (NFP, GDP), to 08:55 CT for the 09:00 CT ISM release, to about 12:55 CT for FOMC; at least 14 hours, inside
  one trade date, flat well before F. The source's window starts at 15:00 CT (the 4 p.m. ET cash close) of the prior
  day; the K9 entry at the 17:00 CT reopen misses 15:00-16:00 CT, a deviation the catalog must state. Sign: long.
  Products: MNQ, M2K, MYM (S&P futures evidence, flagged). Exclusion: X4 (pre-release drift) is the nearest family.
  K9C-006 argues a different mechanism (an uncertainty premium, unconditional long, earned overnight, with informed
  trading confined to the last 30 minutes, P-K9C-006-d), and X4's members follow the sign of the pre-release move, so
  the lead must rule whether "unconditional long into the release" differs in mechanism from X4. Size: 9.48 bp per event
  (1994-2018), 6.98 bp (2012-2018) against MNQ M_X about 2 bp (clears) and G(0.2) about 107 bp (6-9%).

### K9C-007 Kurov, Wolfe and Gilbert, the disappearing pre-FOMC drift (non-survivor)
- Citation: Kurov, Alexander; Wolfe, Marketa Halova; Gilbert, Thomas (2021). "The Disappearing Pre-FOMC Announcement
  Drift." Finance Research Letters 40, 101781. DOI 10.1016/j.frl.2020.101781. Read as the draft of September 14, 2020.
- Retrieval: live Skidmore URL returned HTTP 404; curl of the Wayback Machine snapshot (2022-06-26) of that URL;
  calendar/kurov_wolfe_gilbert_2020.pdf (.txt). Full text.
- Mechanism (non-survivor): the pre-FOMC drift appeared before press-conference meetings to 2015 and disappeared after
  2015 for all meetings; the authors link the decline to lower uncertainty.
- Products and horizon: E-mini S&P 500 nearby futures (S&P 500 futures before September 1997); 24 hours before the
  announcement, from the prior day's open in some columns.
- Sample window: September 1994 to December 2019; sub-periods April 2011 to December 2015 and January 2016 to December
  2019.
- Market and data frequency: intraday futures.
- Cost assumptions: none.
- Quality tells: published; futures data; nonparametric tests; authors active in the announcement literature.
- Verified passages:
  - P-K9C-007-a (abstract): "We extend the sample to December 2019. We find that after first appearing before FOMC
    announcements accompanied by the Fed Chair press conferences, the pre-FOMC drift essentially disappeared after 2015
    in both announcements accompanied by press conferences and announcements not accompanied by press conferences."
  - P-K9C-007-b (Section 3): "In the first half of the sample (April 2011 to December 2015), the mean pre-FOMC return is
    0.445, indicating a positive return of approximately 44 basis points" ... "In contrast, the mean pre-FOMC return in
    the second half of the sample (January 2016 to December 2019) is 0.092."
  - P-K9C-007-c (Section 3): "We cannot reject the null hypothesis of equal central tendency at conventional
    significance levels. This suggests that stock returns do not tend to be higher before FOMC announcements that have
    press conferences relative to days that do not have FOMC announcements."
  - P-K9C-007-d (Data): "We use intraday E-mini S&P 500 nearby contract futures prices."
- Numeric claims: 44 bp (2011-04 to 2015-12) versus 9.2 bp (2016-2019) (P-K9C-007-b), not different from ordinary
  days (-c).
- Conflicting evidence: P-K9C-003-e reports an above-average FOMC-day premium in 2020-01 to 2023-08 (a full-day
  premium, not the 24-hour pre-window).
- Reader's note: Non-survivor for the pre-FOMC drift as a stand-alone rule. Logged so the lead does not treat FOMC as
  the core of a pooled date set; any pooled member should be judged mainly on its non-FOMC days.

### K9C-008 Cieslak, Morse and Vissing-Jorgensen, stock returns over the FOMC cycle
- Citation: Cieslak, Anna; Morse, Adair; Vissing-Jorgensen, Annette (2019). "Stock Returns over the FOMC Cycle."
  Journal of Finance 74(5), 2201-2248. DOI 10.1111/jofi.12818 (volume, pages and DOI from the reader's memory, unverified; the journal and year are confirmed by a WebSearch result page). Read as the draft of October 2, 2015 (NYU Stern host).
- Retrieval: curl; calendar/cieslak_morse_vj_fomccycle.pdf (.txt). Full text. (A first attempt at NBER w22806 served
  an unrelated paper and was deleted.)
- Mechanism: since 1994 the equity premium is earned in even weeks of FOMC cycle time (weeks 0, 2, 4, 6 counted from
  the last scheduled meeting), attributed to Fed news reaching markets through informal communication on a bi-weekly
  internal decision cycle.
- Products and horizon: US stock market excess returns (and world indices; 10-year Treasury), 5-day and daily.
- Sample window: 1994 to 2013 (years only; 160 scheduled meetings); sub-periods 1994-2000, 2001-2007, 2008-2013.
- Market and data frequency: daily.
- Cost assumptions: none in the passages read; the paper reports strategy Sharpe ratios.
- Quality tells: Journal of Finance; robust across three sub-periods with irregular FOMC calendars; mechanism later
  re-examined by two of the authors (K9C-009).
- Verified passages:
  - P-K9C-008-a (abstract): "We document that since 1994 the equity premium in the US and in the rest of the world is
    earned entirely in weeks 0, 2, 4 and 6 in FOMC cycle time, i.e. in time since the last Federal Open Market Committee
    meeting."
  - P-K9C-008-b (Section 2): "the average excess return has been 0.57 percent in week zero in FOMC cycle time (which we
    define as day -1 to 3), 0.30 percent in week two in FOMC cycle time (defined as days 9 to 13), 0.42 percent in week
    four in FOMC cycle time (defined as days 19 to 23), and 0.61 percent in week six in FOMC cycle time (defined as days
    29 to 33)."
  - P-K9C-008-c (Section 2): "the average excess return per day is 13.6 basis points (bps) higher on days that fall in
    week 0 in FOMC cycle time and 10 bps higher on days that fall in week 2, 4, or 6 compared to days that fall in odd
    weeks in FOMC cycle time."
  - P-K9C-008-d (Section 2): "5-day excess returns are significantly positive at the 10 percent level or better at the
    start of weeks 0, 4 and 6, with the significance slightly worse for the 5-day excess return at the start of week 2."
  - P-K9C-008-e (Treasuries): "Over the 1994-2013 period, the 10-year excess bond return is on average 2.4 bps per day
    higher in week 0 and 1.3 bps per day higher in weeks 2, 4 and 6 compared to odd weeks in FOMC cycle time."
- Numeric claims: 5-day returns 0.57 / 0.30 / 0.42 / 0.61% in weeks 0 / 2 / 4 / 6 (P-K9C-008-b); +13.6 bp per day in
  week 0 and +10 bp in weeks 2, 4, 6 versus odd weeks (-c); 10-year bond +2.4 / +1.3 bp per day (-e).
- Conflicting evidence: K9C-009 (the even-week returns are unexpected news, not a risk premium, P-K9C-009-a).
  K9C-004 used these days in its union (P-K9C-004-f) and found the combined set over-explains the premium.
- Reader's note: Fails the K9 frequency shape as stated: even weeks are about half of all dates (above the 40% cap),
  each a 5-day block (above two entries a week). Week 0 alone (days -1 to 3) is about 50 dates in the window, but with
  the two-a-week cap at most about 20 trips, below the 40 required. A capped variant (for example the first two trade
  dates of each even week) is a design choice the source does not make; the lead decides whether that is a parameter
  or a new member. Exclusion: not X6 (it is not a post-FOMC drift conditioned on the announcement outcome), but week 0
  contains the FOMC day and the days after it, so it overlaps X6's dates. Size: 10-13.6 bp per day on the index, the
  same order as K9C-003; bonds 1.3-2.4 bp per day, below ZN M_X (about 4.9 bp).

### K9C-009 Morse and Vissing-Jorgensen, governors' calendars and the FOMC cycle (conflicting on mechanism)
- Citation: Morse, Adair; Vissing-Jorgensen, Annette (2020, December 23 version). "Information Transmission from the
  Federal Reserve to the Stock Market: Evidence from Governors' Calendars." Working paper (AEA 2021 conference paper).
  No DOI found.
- Retrieval: curl of the AEA conference PDF; calendar/morse_vj_2020_governors.pdf (.txt). Full text.
- Mechanism: even-week returns are driven by communication between Fed governors and Reserve Bank presidents at times
  not known in advance, so the FOMC cycle reflects unexpectedly positive policy news, not a risk premium.
- Products and horizon: US stock market, daily and hourly.
- Sample window: governors' calendars 2007 to 2018 (years only).
- Market and data frequency: daily and hourly.
- Cost assumptions: none.
- Quality tells: by two of K9C-008's authors; hand-collected calendar data.
- Verified passages:
  - P-K9C-009-a (abstract): "Since the times of governor-president interactions are not publicly known ahead of time,
    the results furthermore indicate that the FOMC cycle in stock returns is not a risk premium, but instead reflects
    unexpectedly positive policy news."
- Numeric claims: none extracted.
- Conflicting evidence: conflicts with K9C-008's risk-premium reading.
- Reader's note: If the even-week returns are realized news that happened to be positive in 1994-2018, there is no
  ex-ante reason for them to persist; this weakens any FOMC-cycle member.

### K9C-010 Mueller, Tahbaz-Salehi and Vedolin, FX returns on FOMC days
- Citation: Mueller, Philippe; Tahbaz-Salehi, Alireza; Vedolin, Andrea (2017). "Exchange Rates and Monetary Policy
  Uncertainty." Journal of Finance 72(3), 1213-1252 (from a WebSearch result page). DOI 10.1111/jofi.12499 (reader's memory, unverified). Read as LSE Financial Markets Group
  Discussion Paper 54.
- Retrieval: curl; calendar/mueller_tsv_2017_fmgdp54.pdf (.txt). Full text.
- Mechanism: short-dollar positions earn a premium on scheduled FOMC days for bearing monetary-policy uncertainty;
  larger for high-interest-rate currencies, and larger when policy uncertainty is high or the Fed eases.
- Products and horizon: spot currencies against the US dollar (interbank tick data), portfolios sorted by forward
  discount; the whole announcement day (pre and post components).
- Sample window: 1994-01-01 to 2010-12-31.
- Market and data frequency: tick data aggregated to daily (4 p.m. London) and intraday.
- Cost assumptions: none stated in the passages read.
- Quality tells: Journal of Finance; tick data; theory with testable cross-currency predictions.
- Verified passages:
  - P-K9C-010-a (Introduction): "we ﬁnd that a portfolio consisting of currencies with low interest rates earns an
    average daily return of 5.71 basis points (bps) during days when the Federal Reserve makes an announcement,
    compared to an average of −0.55bps on all other days. This differ- ence becomes larger for the portfolio consisting
    of high interest rate currencies, with a daily return of 16.83bps on announcement days compared to 1.66bps on
    non-announcement days. This 15.17bps difference is not only highly statistically signiﬁcant (with a t-statistic of
    2.43)"
  - P-K9C-010-b (Introduction): "we document that cur- rency excess returns span the entire announcement day, thus
    consisting of a pre- as well as a post- announcement component."
  - P-K9C-010-c (Data): "We work with tick-by-tick high frequency data that runs from January 1, 1994 to December 31,
    2010."
- Numeric claims: low-rate portfolio 5.71 bp versus -0.55 bp; high-rate 16.83 bp versus 1.66 bp; difference 15.17 bp,
  t = 2.43 (P-K9C-010-a).
- Conflicting evidence: none found in this reader's search; no post-2010 evidence found.
- Reader's note: Date set FOMC only (10 in the window), below the floor; would need pooling with other releases, for
  which this source gives no FX evidence. Products: 6A, 6N (high-rate legs in the source's era), 6E, 6J, 6S (low-rate);
  sign: long the foreign currency future (short USD). Hold: the full trade date fits (the source's daily return spans the
  day). Exclusion: not X6 (whole day, unconditional on the decision), not X9 (not fix-timed). Size: 16.83 bp for the
  high-rate portfolio against 6A M_X about 5.7 bp (clears) but at f about 0.03 G is several hundred bp. Not a candidate
  on its own.

### K9C-011 Balduzzi and Moneta, bond risk premia around announcements (abstract only; conflicting for bonds)
- Citation: Balduzzi, Pierluigi; Moneta, Fabio (2017). "Economic Risk Premia in the Fixed-Income Markets: The Intraday
  Evidence." Journal of Financial and Quantitative Analysis 52(5), 1927-1950. DOI 10.1017/S0022109017000631.
- Retrieval: curl of the Cambridge abstract page; calendar/jfqa_fixedincome_intraday_abs.html. Abstract only (no open
  full text found; one WebSearch for an author copy).
- Mechanism: one factor summarizes bond price reactions to announcements; its premium was earned before releases
  before the financial crisis and became insignificant after it.
- Products, horizon, sample, frequency: Treasury bonds, high-frequency; exact sample dates not in the abstract.
- Cost assumptions: not known.
- Verified passages:
  - P-K9C-011-a (abstract): "Before the financial crisis, the factor risk premium is substantial, significant, and
    mainly earned before announcement releases. After the crisis, the stock–bond covariance becomes negative and the
    preannouncement factor risk premium becomes insignificant."
- Reader's note: Conflicting evidence for any Treasury announcement-day member (K9C-001 bond results end in 2009);
  together with the sub-M_X size (K9C-001 note), the bond version is not a candidate.

### K9C-012 Faust and Wright, risk premia in the 8:30 economy (abstract only)
- Citation: Faust, Jon; Wright, Jonathan H. (2018). "Risk Premia in the 8:30 Economy." Quarterly Journal of Finance
  8(3), 1850010. DOI 10.1142/S2010139218500106.
- Retrieval: curl of the RePEc/IDEAS page; calendar/faust_wright_2018_ideas.html. Abstract only (publisher
  subscription).
- Mechanism: part of the time-varying expected bond excess return accrues in short windows around 8:30 a.m. releases.
- Verified passages:
  - P-K9C-012-a (abstract): "Using intradaily data, we find that some, but not all, of the time-varying expected excess
    returns accrue right around macroeconomic announcements. In forecasting six-month cumulative bond returns, there is
    more predictability in announcement windows than at other times."
- Reader's note: Context only. It concerns predictability of bond returns in announcement windows from a forecasting
  model, not a fixed-sign calendar trade; sample dates and products not available from the abstract.

### K9C-013 Monaco and Murgia, retail attention and the FOMC equity premium
- Citation: Monaco, Eleonora; Murgia, Lucia Milena (2022). "Retail Attention and the FOMC Equity Premium." Finance
  Research Letters, 103597. DOI 10.1016/j.frl.2022.103597.
- Retrieval: curl of the UEA repository accepted manuscript; calendar/monaco_2022_retail_fomc.pdf (.txt). Full text.
- Mechanism: Google search attention around FOMC days heightens the FOMC equity premium.
- Sample window: September 2004 to December 2019 (from table notes, "M9:2004, M12:2019").
- Verified passages:
  - P-K9C-013-a (abstract): "Our measure shows that investors’ attention contributes and heightens the FOMC equity
    premium and reduces the volatility around the announcement."
  - P-K9C-013-b (table notes): "Sample Period: M9:2004, M12:2019."
- Reader's note: Context for FOMC days only (below the floor); the attention series (Google SVI) is not an admissible
  program input. Not a candidate.

---

## C1. Day-of-week and turn-of-week effects

### K9C-014 Caporale and Plastun, the day-of-the-week effect in crypto currencies (bitcoin Monday)
- Citation: Caporale, Guglielmo Maria; Plastun, Alex (2019). "The day of the week effect in the cryptocurrency
  market." Finance Research Letters 31, 258-269 (volume and pages from the reader's memory, unverified). DOI 10.1016/j.frl.2018.11.012 (OpenAlex). Read as CESifo Working Paper 6716
  (October 2017).
- Retrieval: plain curl returned a 3 KB HTML stub; scrapling extract get returned a text-mangled PDF (unreadable);
  curl with a referer and cookie jar returned the PDF; calendar/caporale_plastun_2017_cesifo6716.pdf (.txt). Full text.
- Mechanism: bitcoin returns are higher on Mondays (a weekly seasonal), found only for bitcoin among four coins.
- Products and horizon: bitcoin spot (also LiteCoin, Ripple, Dash); daily open-to-close returns; trading simulation
  long on Monday, closed at the end of the day.
- Sample window: 2013 to 2017 (daily data; the simulation table begins 2013-01-07; exact end date not extracted).
- Market and data frequency: crypto spot, daily.
- Cost assumptions: a trading simulation is run; cost settings not extracted.
- Quality tells: short sample, single asset, many tests across days and coins (multiple comparisons); the authors'
  own per-year results reverse.
- Verified passages:
  - P-K9C-014-a (abstract): "The only exception is BitCoin, for which returns on Mondays are significantly higher than
    those on the other days of the week. In this case the trading simulation analysis shows that there exist exploitable
    profit opportunities"
  - P-K9C-014-b (Section 4): "open long positions on Monday and close them at the end of this day."
  - P-K9C-014-c (Conclusions): "a trading strategy based on this anomaly is profitable for the whole sample
    (2013-2017): it generates net profit with probability 60% and these results significantly differ from the random
    ones. However, in the case of individual years the opposite conclusions are reached."
  - P-K9C-014-d (Appendix F, Table F.1, BitCoin column): "0.0091" for "Monday (a0 )" with "(0.002)" beneath.
- Numeric claims: Monday coefficient 0.0091 (0.91% a day), p = 0.002 (P-K9C-014-d); 60% profitable (-c).
- Conflicting evidence: within the source, the per-year results reverse (P-K9C-014-c). No post-2017 replication with
  full text was retrieved (a UCD repository copy of Kinateder and Papavassiliou 2021 sat behind a human-verification
  page; a later bitcoin event-study paper returned HTTP 404).
- Reader's note: Date set: Mondays, about 58 in the window (19% of dates), one a week. Hold: MBT Monday trade date,
  17:00 CT Sunday reopen to F (the source's day is a calendar day in UTC terms, a mismatch to state). Sign: long.
  Exclusion: X15 is hourly time-series momentum on the MBT Monday; a plain Monday long is a weekly seasonal, which X15's
  note names as an admissible different mechanism. X14 (weekend bitcoin to Monday Nasdaq-100) is a cross-market lead,
  not this. Evidence is 2013-2017 only, before CME bitcoin futures matured. Size: 0.91% (91 bp) per Monday against MBT
  M_X about 16 bp (clears) and G(0.2) about 230 bp (about 40%), but the sample is short and unstable.

### K9C-015 Décourt, Chohan and Perugini, bitcoin returns and the Monday effect
- Citation: Décourt, Roberto Frota; Chohan, Usman W.; Perugini, Maria Letizia. "Bitcoin Returns and the Monday
  Effect." Horizontes Empresariales, año 16, no. 2, pp. 4-14 (Universidad del Bío-Bío). Year printed only as the
  volume ("año 16"); sample ends 2017-10-25. DOI not found.
- Retrieval: curl; calendar/ubiobio_btc_dow.pdf (.txt). Full text.
- Mechanism: Monday returns are higher in bitcoin; the authors link Monday effects to periods following interrupted
  trading.
- Products and horizon: bitcoin, daily.
- Sample window: 2013-01-01 to 2017-10-25.
- Verified passages:
  - P-K9C-015-a (Section 3): "We analyzed daily returns of Bitcoin from January 1, 2013 until October 25, 2017"
  - P-K9C-015-b (Conclusion): "During the period studied from 2013 until October 2017, the daily return of Bitcoin on
    Monday was significantly different from other days. The returns on Monday for Bitcoin are above average, which
    denotes evidence of market inefficiency."
- Quality tells: low-tier regional journal; the same 2013-2017 window as K9C-014, so it is not independent evidence.
- Reader's note: Corroborates K9C-014 on the same sample only. Same candidate notes.

### K9C-016 Singal and Tayal, the weekend effect in futures markets (abstract only)
- Citation: Singal, Vijay; Tayal, Jitendra (2020). "Risky short positions and investor sentiment: Evidence from the
  weekend effect in futures markets." Journal of Futures Markets 40(3), 479-500. DOI 10.1002/fut.22069.
- Retrieval: curl of the RePEc/IDEAS page; calendar/singal_tayal_2020_ideas.html. Abstract only (two WebSearch calls
  found no open full text; the 2014 SSRN version is at SSRN, which blocks automated fetches).
- Mechanism: Friday returns exceed the following Monday's in futures; partly a premium for the higher risk of short
  positions held over weekends, partly investor mood (better on Fridays, worse on Mondays).
- Products, horizon, sample, frequency: futures markets (which contracts and which years are not in the abstract);
  daily.
- Verified passages:
  - P-K9C-016-a (abstract): "we document a weekend effect (Friday's return minus the following Monday's return) in
    futures markets. The weekend effect occurs partly because of asymmetric risk between long and short positions
    around weekends; the weekend effect increases when short positions are relatively more risky."
  - P-K9C-016-b (abstract): "we find that both lagged and contemporaneous changes in investor sentiment are related to
    the weekend effect. These results are consistent with the investor sentiment literature that finds that mood
    improves on Fridays but deteriorates on Mondays."
- Reader's note: The only recent futures-specific day-of-week paper found. Possible members: long the Friday session,
  or short the Monday session (each about 58-60 dates, 20%). Without the full text the products, sample and effect
  size are unknown; the lead should treat it as a pointer until the full text is obtained. Exclusion: none by
  mechanism (a weekend-risk premium, which X15's note admits).

### K9C-017 Robins and Smith, no more weekend effect (abstract only; non-survivor)
- Citation: Robins, Russell P.; Smith, Geoffrey Peter (2016). "No More Weekend Effect." Critical Finance Review 5(2),
  417-424. DOI 10.1561/104.00000038.
- Retrieval: curl of the RePEc/IDEAS page; calendar/robins_smith_2016_ideas.html. Abstract only.
- Verified passages:
  - P-K9C-017-a (abstract): "Before 1975, the mean weekend rate of return on the equal-weight (value-weight) stock
    market portfolio is significant -18bp (-19bp). After 1975, it is insignificant -5bp (-1bp). This break date is
    determined by a structural break test with unknown break date. The weekend effect is no longer an anomaly."
- Sample window: per the abstract, before and after 1975 (CRSP; exact span not in the abstract).
- Reader's note: Non-survivor for the US equity weekend (Monday) effect after 1975. Counts against an equity-index
  Monday member.

### K9C-018 Schwert, anomalies and market efficiency (weekend effect gone)
- Citation: Schwert, G. William (2003). "Anomalies and Market Efficiency." In Handbook of the Economics of Finance,
  vol. 1B, 939-974 (book details from the reader's memory, unverified). Read as NBER Working Paper 9277 (2002). DOI 10.3386/w9277.
- Retrieval: curl; calendar/schwert_2002_w9277.pdf (.txt). Full text.
- Verified passages:
  - P-K9C-018-a (Introduction): "The evidence in this paper shows that the size effect, the value effect, the weekend
    effect, and the dividend yield effect seem to have weakened or disappeared after the papers that highlighted them
    were published."
  - P-K9C-018-b (The Weekend Effect): "Interestingly, the estimate of the weekend effect since 1978 is not reliably
    different from the other days of the week." and "Thus, like the size effect, the weekend effect seems to have
    disappeared, or at least substantially attenuated, since it was first documented in 1980."
- Sample window: February 1885 to May 2002 (US stock indices, daily), with sub-period 1978-2002.
- Reader's note: Non-survivor evidence, consistent with K9C-017.

### K9C-019 Johnston, Kracaw and McConnell, day-of-the-week effects in financial futures
- Citation: Johnston, Elizabeth Tashjian; Kracaw, William A.; McConnell, John J. (1991). "Day-of-the-Week Effects in
  Financial Futures: An Analysis of GNMA, T-Bond, T-Note, and T-Bill Contracts." Journal of Financial and Quantitative
  Analysis 26(1), 23-44 (from the IDEAS URL v26y1991i01p23-44). DOI 10.2307/2331241 (reader's memory, unverified).
- Retrieval: curl of the author-hosted PDF (Purdue); calendar/johnston_kracaw_mcconnell_1991.pdf (.txt). Full text
  (scanned, with a usable text layer).
- Mechanism: a negative Monday and a positive Tuesday seasonal in Treasury futures, each confined to particular
  sub-periods and to months before a delivery month.
- Products and horizon: GNMA, T-bond, T-note, T-bill futures; daily open and close.
- Sample window: from contract listing in the late 1970s to about 1987-1988 (the exact span is in the table on p. 26,
  not extracted).
- Verified passages:
  - P-K9C-019-a (abstract): "A negative Monday seasonal?similar to the well-known Monday effect in stock returns?is
    found for GNMA and T-bond contracts. A positive Tuesday seasonal is found on GNMA, T-bond, and T-note contracts."
    (as in the text layer, which renders the em dashes as "?"; runs of spaces collapsed)
  - P-K9C-019-b (abstract): "The negative Monday phenomenon occurs only in the data before 1982, while the positive
    Tuesday effect is present only after 1984. In addition, we find that both seasonal phenomena occur only during
    months prior to a delivery month."
- Reader's note: Old, sub-period-dependent and tied to pre-delivery months (X13 territory: delivery-cycle keyed).
  Context and conflicting evidence for any Treasury day-of-week member; not a candidate.

---

## C3. Pre-holiday and other calendar dates

### K9C-020 Ko and Yang, the pre-holiday premium out of sample
- Citation: Ko, Kuan-Cheng; Yang, Nien-Tzu (2021). "The Pre-Holiday Premium of Ariel (1990) Has Largely Become A
  Small-Firm Effect Out of Sample." Critical Finance Review (replication issue). DOI not printed in the extracted pages.
- Retrieval: curl of the CFR-hosted PDF (cfr.ivo-welch.info); calendar/ko_2021_preholiday_cfr.pdf (.txt). Full text.
- Mechanism (non-survivor test): Ariel's pre-holiday premium replicates in 1963-1982 but, out of sample, survives only
  among small firms.
- Products and horizon: CRSP equal- and value-weighted indices, DJIA, S&P 500; one trading day (pre-holiday).
- Sample window: 1963-1982 (replication) and 1983-2019 (out of sample), with sub-periods 1990-2019 and 1995-2019.
- Market and data frequency: US equity, daily.
- Cost assumptions: none.
- Verified passages:
  - P-K9C-020-a (abstract): "Extending the sample to 1983-2019, we find that the pre-holiday effect now exists only
    among small firms. For large firms, the differences in returns between pre-holidays and non-pre-holidays have become
    insignificant, and especially after 1990."
  - P-K9C-020-b (p. 3): "The average pre-holiday returns of CRSP EW and VW indices decline to 0.37% and 0.14%,
    respectively." and "The pre-holiday premium of the CRSP VW index completely vanished after 1990 without controlling
    for other day effects."
  - P-K9C-020-c (p. 3): "From 1983 to 2019, the t-statistics for the differences in returns between pre-holidays and
    non-pre-holidays are 0.64 and 0.93 for DJIA and S&P 500, respectively."
- Numeric claims: EW 0.37%, VW 0.14% on pre-holidays 1983-2019 (P-K9C-020-b); DJIA and S&P 500 t = 0.64 and 0.93 (-c).
- Conflicting evidence: none found that restores the large-cap effect.
- Reader's note: Frequency fails: about 13 pre-holiday trade dates in the window (about 9-10 a year), below the 30-trip
  floor, and no source found pools pre-holiday dates with others. Non-survivor for large-cap indices (MNQ, MYM). The
  small-firm survivor would point to M2K (the Russell 2000 is a small-cap index, but CRSP EW is not the same index), at
  0.35-0.37% per date, well above M2K M_X (about 8.6 bp) but only about 13 trips. The E.0 catalog already logged a
  bitcoin pre-holiday drift (E.0 K7-041, Quantpedia blog); not re-screened.

### K9C-021 Stivers and Sun, option-expiration week returns (abstract only)
- Citation: Stivers, Chris; Sun, Licheng (2013). "Returns and option activity over the option-expiration week for S&P
  100 stocks." Journal of Banking and Finance 37(11), 4226-4240. DOI 10.1016/j.jbankfin.2013.07.030.
- Retrieval: curl of the RePEc/IDEAS page; calendar/stivers_sun_2013_ideas.html. Abstract only (one WebSearch; no
  open full text; SSRN 1571786 not attempted because SSRN blocks automated fetches).
- Mechanism: in option-active large caps, option market makers' delta-hedge rebalancing (less short-stock hedging) and
  falling implied volatility raise returns over the week ending on the third Friday; the next week underperforms.
- Verified passages:
  - P-K9C-021-a (abstract): "For S&P 100 stocks, we find that the weekly returns over option-expiration (OE) weeks (a
    month’s third-Friday week) tend to be high, relative to: (1) the third-Friday weekly returns of other stocks with
    less option activity, (2) the own stock’s other weekly returns, (3) the risk, based on asset-pricing alphas. For
    these same stocks, a month’s fourth-Friday weekly returns underperform modestly."
  - P-K9C-021-b (abstract): "(1) delta-hedge rebalancing by option market makers, with a reduction in short-stock hedge
    positions over the OE week, and (2) declining risk perceptions over the OE week"
- Sample window, size: not in the abstract (a practitioner summary cites 1996-2008 and 0.45% a week; not logged as
  evidence).
- Reader's note: Frequency: 15 expiration weeks in the window; with the two-a-week cap at most about 30 trips, exactly
  the proposed floor and below the 40 required. Evidence is on individual S&P 100 stocks, not an index future.
  Exclusion: X13 bars "a trade keyed to a futures expiry, roll window or index roll"; monthly equity-option expiry is not
  a futures expiry, but the quarterly expirations coincide with equity-index futures expiry, so the lead must rule.
  Index-level options-expiration evidence found only in blogs (quantpedia.com, cxoadvisory.com, quantifiedstrategies),
  not logged as evidence; one of them reports deterioration in recent years (pointer only).

### K9C-022 Maberly and Pierce, the Halloween effect in S&P 500 futures (abstract only; non-survivor)
- Citation: Maberly, Edwin D.; Pierce, Raylene M. (2004). "Stock Market Efficiency Withstands another Challenge:
  Solving the 'Sell in May/Buy after Halloween' Puzzle." Econ Journal Watch 1(1), 29-46. No DOI found.
- Retrieval: curl of the Econ Journal Watch article page; calendar/maberly_pierce_2004_ejw.html. Abstract only (the
  page links a PDF that was not fetched).
- Verified passages:
  - P-K9C-022-a (abstract): "After inserting a dummy variable to account for the impact of the two identified outliers,
    the Halloween effect becomes statistically insignificant. This anomaly is not economically exploitable for U.S.
    equity markets. We extend the research to the S&P 500 futures contract and find no evidence of an exploitable
    Halloween effect over the period April 1982-April 2003."
- Reader's note: Seasonal months do not reduce to a K9 rule here: November-April covers about half of all dates (above
  the 40% cap) and has no daily trigger. Non-survivor in S&P futures (1982-04 to 2003-04). Not a candidate.

---

## Fetch log

All files under reports/stage_e10_research/calendar/. UTC times. Rows with "-" for sha256 and size are failed or
wrong fetches whose files were deleted. The full machine log is calendar/fetchlog.tsv. API search records (not
evidence) are in calendar/api/ (oa_*.json from OpenAlex; ss_c2a.json holds the Semantic Scholar 403 response).

| File | URL | UTC fetch time | sha256 | Bytes | Tool / note |
|---|---|---|---|---|---|
| savor_wilson_2013_draft.pdf | https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/Draft20111128p_edited.pdf | 2026-10-03T05:34:30Z | eaeb786b44842b13916c99111074150f23443ba624cd1d02681047da62872f4a | 312729 | curl |
| ernst_gilbert_hrdlicka_2021.pdf | https://www.aeaweb.org/conference/2022/preliminary/paper/ktNibY2Y | 2026-10-03T05:34:31Z | be23b86a3b4cb2277d0568502efffae2420738fdfce887f34ae00b45d80e036c | 518337 | curl (saved first under an .html name, renamed; same bytes) |
| ai_bansal_guo_2023_w31923.pdf | https://www.nber.org/system/files/working_papers/w31923/w31923.pdf | 2026-10-03T05:34:33Z | 4d5d1972c1815ad5cb7a2e5b99bc93e94623c44a10da057fd265f506a0076d40 | 588012 | curl |
| lucca_moench_sr512.pdf | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr512.pdf | 2026-10-03T05:35:26Z | c7cb0f335c60cb9fc305189935fb7c51e98fa8461c2b33efd51eb5a5c3f2e34b | 1177349 | curl (misrouted to regime/, moved 22:37 PDT) |
| hu_pan_wang_zhu_w25817.pdf | https://www.nber.org/system/files/working_papers/w25817/w25817.pdf | 2026-10-03T05:35:27Z | 3c66010b1582e55b9f5722f162003baa761e1c872b76cc47ced6f1588c3e3ae4 | 634417 | curl (misrouted to regime/, moved 22:37 PDT) |
| cieslak_morse_vj_w22806.pdf | https://www.nber.org/system/files/working_papers/w22806/w22806.pdf | 2026-10-03T05:35:28Z | - | - | wrong paper (Chavaz and Rose), deleted |
| jones_lamont_lumsdaine_w5150.pdf | https://www.nber.org/system/files/working_papers/w5150/w5150.pdf | 2026-10-03T05:35:29Z | - | - | wrong paper (not Jones-Lamont-Lumsdaine), deleted |
| ignatieva_2024_prefomc.pdf | https://www.tandfonline.com/doi/pdf/10.1080/00036846.2024.2322573?download=true | 2026-10-03T05:36:19Z | - | - | HTTP 403 (a 5,834-byte block page was logged at 05:36:19Z, then deleted at 05:36:26Z) |
| monaco_2022_retail_fomc.pdf | https://ueaeprints.uea.ac.uk/id/eprint/90347/1/1_s2.0_S1544612322007735_main.pdf | 2026-10-03T05:36:21Z | da6dcc27143120f2e7924c1eae6939da361198472401077d5dd31a00c022ac71 | 1110873 | curl |
| kurov_wolfe_gilbert_2020.pdf (live) | https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf | 2026-10-03T05:36:27Z | - | - | HTTP 404, deleted |
| kurov_wolfe_gilbert_2020.pdf | https://web.archive.org/web/2021id_/https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf | 2026-10-03T05:36:38Z | 240c994c85ab2244912be09fc80526d21754b2b9301e3235b079e6aefbf5a495 | 513133 | curl (Wayback snapshot 2022-06-26) |
| cieslak_morse_vj_fomccycle.pdf | https://stern.nyu.edu/sites/default/files/assets/documents/cycle_paper_cieslak_morse_vissingjorgensen.pdf | 2026-10-03T05:37:13Z | c45108b8ab390585452585ed7a8a31484f7defe5928c05c1ac67bc1a2786a88f | 859710 | curl |
| morse_vj_2020_governors.pdf | https://www.aeaweb.org/conference/2021/preliminary/paper/nAzyfDkE | 2026-10-03T05:37:42Z | 97ba1eafd092d10d15e2389dd7b93a3d3ff470e1d58c63370b5028bd0bc3e363 | 489450 | curl |
| jones_lamont_lumsdaine_nber_abstract.html | https://www.nber.org/papers/w5150 | 2026-10-03T05:37:55Z | - | - | wrong paper, deleted |
| faust_wright_2018_ideas.html | https://ideas.repec.org/a/wsi/qjfxxx/v08y2018i03ns2010139218500106.html | 2026-10-03T05:38:24Z | ec517941710f06eae0ab7bd3d5f26b703bfc87cf7f0e6e2f7407639ba8ac79c2 | 55144 | curl |
| jfqa_fixedincome_intraday_abs.html | https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/economic-risk-premia-in-the-fixedincome-markets-the-intraday-evidence/4F05044DB91F87D417FFE796BDDAEB61 | 2026-10-03T05:38:25Z | c30a0b8d1d30f27d23a35842aa4bb907726b75e8407304320bf0125ee8324894 | 881494 | curl |
| caporale_plastun_2017_cesifo6716.pdf (1st) | https://cesifo.org/DocDL/cesifo1_wp6716.pdf | 2026-10-03T05:39:03Z | - | - | HTML stub (3 KB), deleted; scrapling extract get then returned a text-mangled PDF (not kept) |
| robins_smith_2016_ideas.html | https://ideas.repec.org/a/now/jnlcfr/104.00000038.html | 2026-10-03T05:39:03Z | a33cb7d783d75e777fdc03af59ed45836fe9e78de2b310eb5c1e36eb3f63f4c6 | 34095 | curl |
| caporale_plastun_2017_diw1694.pdf | https://www.diw.de/documents/publikationen/73/diw_01.c.567282.de/dp1694.pdf | 2026-10-03T05:39:11Z | - | - | HTTP 403, deleted |
| caporale_plastun_2017_cesifo6716.pdf | https://cesifo.org/DocDL/cesifo1_wp6716.pdf | 2026-10-03T05:39:36Z | 0f7915711fe6ca98afef061ceb2a06f43c3c9a1227308bbc2d16eb86b9b5e98d | 354495 | curl with referer and cookie jar |
| quiros_2022_btc_dow.pdf | http://economic-research.pl/Journals/index.php/oc/article/download/2091/1935 | 2026-10-03T05:40:04Z | - | - | HTTP 404, deleted |
| ubiobio_btc_dow.pdf | https://revistas.ubiobio.cl/index.php/HHEE/article/download/3103/3116/13466 | 2026-10-03T05:40:24Z | 6895fa1114d990f69f34ad1b50ca3e965387f4971054042e918fd5e2f7400bd7 | 609274 | curl |
| aut_afl_266.pdf | https://ojs.aut.ac.nz/applied-finance-letters/article/download/266/85 | 2026-10-03T05:40:25Z | - | - | HTTP 404, deleted |
| brunel_21825.pdf | https://bura.brunel.ac.uk/bitstream/2438/21825/6/FullText.pdf | 2026-10-03T05:40:56Z | - | - | off-topic (large-move abnormal returns; Regime reader), deleted |
| singal_tayal_2020_ideas.html | https://ideas.repec.org/a/wly/jfutmk/v40y2020i3p479-500.html | 2026-10-03T05:41:31Z | 7a3d9c13567906b17003a5f01810591d544673e4e1f783266fe18a6160ea8733 | 61957 | curl |
| ko_2021_preholiday_cfr.pdf | https://cfr.ivo-welch.info/published/papers/ko2021pre.pdf | 2026-10-03T05:42:08Z | 039d0939df6c5096a9b4aa4918fea95db0230f21cde1f9eabab772e430637b1b | 205438 | curl |
| caporale_plastun_2023_witching.pdf | https://www.tandfonline.com/doi/pdf/10.1080/23322039.2023.2182016?needAccess=true | 2026-10-03T05:42:25Z | - | - | HTTP 403, deleted |
| stivers_sun_2013_ideas.html | https://ideas.repec.org/a/eee/jbfina/v37y2013i11p4226-4240.html | 2026-10-03T05:42:33Z | cb4a713e44c69d0c26253783874cb4bb859ab036b5423a0cc07593948b5a8a81 | 54665 | curl |
| mueller_tsv_2017_fmgdp54.pdf | https://www.fmg.ac.uk/sites/default/files/publications/dp-54.pdf | 2026-10-03T05:43:10Z | e7ec83f9f6650435707974c9d356279119fc592f507d175c6f5c330b77175d7c | 668847 | curl |
| schwert_2002_w9277.pdf | https://www.nber.org/system/files/working_papers/w9277/w9277.pdf | 2026-10-03T05:44:07Z | 0db4a9d54f22b7c41886323f2b0d5dcfd7472c0abf3ce20d52372da4f7a16bba | 344595 | curl |
| ai_bansal_2018_econometrica.pdf | https://people.duke.edu/~rb7/bio/announcement_premium_econometrica.pdf | 2026-10-03T05:44:28Z | aefdc8806d642fb0a696805ccf0105b6a3fbb206f005b3cb2100ab42145c2bbb | 883670 | curl |
| maberly_pierce_2004_ideas.html | https://ideas.repec.org/a/ejw/journl/v1y2004i1p29-46.html | 2026-10-03T05:44:41Z | - | - | HTTP 404, deleted |
| maberly_pierce_2004_ejw.html | https://econjwatch.org/articles/stock-market-efficiency-withstands-another-challenge-solving-the-sell-in-may-buy-after-halloween-puzzle | 2026-10-03T05:44:47Z | d95d246237761f4719eb3aa490f980ae8642680128c8bc06382094115f23b7ff | 13603 | curl |
| johnston_kracaw_mcconnell_1991.pdf | https://business.purdue.edu/faculty/mcconnell/publications/Day-of-the-Week-Effects-in-Financial-Futures.pdf | 2026-10-03T05:45:51Z | a7e46ef006662c2b2f06f99b8bb6cd8dd6d3f4093670484664b796213ce40476 | 2750869 | curl |

Not saved (screening only, no evidence logged): http://hdl.handle.net/10197/25018 (UCD, human-verification page);
https://fedinprint.org/item/fedgfe/34334/original (curl returned nothing usable); a Morse-VJ copy was first downloaded
to the scratchpad and then moved into calendar/ (row above).

---

## Rejection table (records screened and rejected, one line each)

| Record | Reason |
|---|---|
| Jones, Lamont, Lumsdaine (1998) "Macroeconomic news and bond market volatility" JFE | Not retrieved (NBER w5150 guess served a different paper); its bond announcement-day returns are reported second-hand in K9C-001 (P-K9C-001-d text cites it); bond premium below M_X anyway |
| Ignatieva (2024) "The pre-FOMC announcement drift: short-lived or long-lasting?" Applied Economics | Blocked (tandfonline HTTP 403); FOMC-only date set, below the floor |
| Ying (2020) "The Pre-FOMC Announcement Drift and Private Information" SSRN | FOMC-only; SSRN blocks automated fetches; informed-trading mechanism (X4-like) |
| Bodilsen et al. (2021) "Asset pricing and FOMC press conferences" JBF | FOMC-only, below the floor; covered by K9C-007 |
| Guo et al. (2020) "Investor sentiment and the pre-FOMC announcement drift" FRL | FOMC-only, below the floor |
| Cujean (2023) "Asset Pricing on FOMC Announcements" SSRN | FOMC-only; SSRN |
| Jacobs (2025) "Tail Risk Around FOMC Announcements" JFQA | Option tail-risk pricing, not a directional futures trade |
| Indriawan et al. (2020) "The FOMC announcement returns on long-term US and German bond futures" JBF | FOMC-only bond futures; below the floor; not retrieved (no OA link) |
| Kurov, Sancetta, Strasser, Wolfe (2019) "Price Drift Before U.S. Macroeconomic News" JFQA | Already in E.0 (K2-007); it is the X4 mechanism |
| Savor and Wilson (2014) "Asset pricing: A tale of two days" JFE | Cross-sectional CAPM test on announcement days, not a directional index trade |
| Savor and Wilson (2011) "Stock Market Beta and Average Returns on Macroeconomic Announcement Days" | Earlier version of the 2014 cross-section paper |
| Gilbert (2011) "Information aggregation around macroeconomic announcements: revisions matter" JFE | Revision effects at the release, not a full-session premium |
| Faust et al. (2007) high-frequency response of FX and rates to announcements, JME | Response to surprises (sign unknown in advance), not a fixed-sign trade |
| Corbet et al. (2020) "The impact of macroeconomic news on Bitcoin returns" | Surprise-response study; no fixed-sign date rule |
| Du (NAU) "Currency risk premium and U.S. macroeconomic announcement" | Cross-sectional FX-risk pricing in equities, not a futures trade |
| Liu and Shaliastovich (2021), Wachter and Zhu (2022), Ai, Han, Pan, Xu (2022) | Theory or cross-section of the announcement premium; covered by K9C-003's review |
| Altavilla et al., OMT announcements | One-off policy events, not a recurring calendar |
| Aharon and Qadan (2019) "Bitcoin and the day-of-the-week effect" FRL | No OA copy found; 2010-2017 sample, same era as K9C-014 |
| Baur, Cahill, Godfrey, Liu (2019) "Bitcoin time-of-day, day-of-week and month-of-year effects" FRL | No OA copy fetched (sciencedirect); time-of-day parts belong to the Overnight reader |
| Kinateder and Papavassiliou (2021) "Calendar effects in Bitcoin returns and volatility" FRL | UCD repository behind human verification; not retrieved |
| Ma and Tanizaki (2019) "The day-of-the-week effect on Bitcoin return and volatility" RIBAF | No OA link; same pre-2019 era |
| Quirós et al. (2022) "A new perspective of the day-of-the-week effect on Bitcoin returns" Oeconomia Copernicana | OA link returned HTTP 404 |
| Berument and Kiymaz (2001); Kiymaz and Berument (2003) | Day-of-week effects on volatility, not returns |
| Cornell (1985) "The weekly pattern in stock returns: cash versus futures" JF | 1980s sample, superseded by K9C-017/-018 |
| Day-of-week papers on silver, iron ore, Chinese soybean, WIG20, Taiwan and Indian futures (2008-2023) | Non-traded exposures or forecasting papers, no fixed-sign US futures rule |
| Clute JABR (2011) "On the day of the week effect: intraday prices for the S&P 500 futures contract" | Low-tier journal, intraday patterns (Overnight reader's area) |
| Singal and Tayal (2014) SSRN "Does Unconstrained Short Selling Result in Unbiased Security Prices? ... Weekend Effect in Futures" | Earlier version of K9C-016; SSRN |
| Bakar (2014) "Does mood explain the Monday effect?" | Equity mood study, no futures rule |
| Keim and Stambaugh (1984), Jaffe and Westerfield (1985), Smirlock and Starks (1986), Gibbons and Hess (1981), French (1980) | Pre-1990 equity weekend studies; their decay is documented in K9C-017/-018 |
| Agrawal and Tandon (1994), Liano et al. (1994), Keef and Roush (2005), Meneu and Pardo (2004), Marrett and Worthington (2008), McGuinness (2005) | Pre-holiday in equity (old or non-US); frequency below the floor; K9C-020 is the out-of-sample test |
| Caporale and Plastun (2023) "Witching days and abnormal profits in the US stock market" Cogent | Blocked (tandfonline HTTP 403); quarterly witching (4 a year) below the floor, X13-adjacent |
| Expiration-day effects in Indian, Polish, Malaysian index futures (Vipul 2005; Samineni 2020; Suliga 2017; Gurgul 2019; Bacha 1999) | Non-US, expiry-day (X13) |
| Edmans et al. (2007) sports sentiment; Kamstra et al. (2003) SAD; Yuan et al. (2006) lunar | Not a calendar of the K9 type (event dates not fixed, or seasonal over months) |
| Quantpedia, CXO Advisory, QuantifiedStrategies, SentimenTrader, Hull Tactical pages | Blogs and practitioner pages: pointers only, never evidence |

---

## Routed (other readers' topics; not read)

- Caporale and Plastun (2021) "Gold and oil prices: abnormal returns, momentum and contrarian effects," Financial
  Markets and Portfolio Management 35, 353-368 (large prior-day moves) -> Regime reader.
- Baur, Cahill, Godfrey, Liu (2019) bitcoin time-of-day effects (intraday/overnight decomposition) -> Overnight reader.
- Gorton, Hayashi, Rouwenhorst (2012) "The Fundamentals of Commodity Futures Returns" (inventories, basis) ->
  Commodity reader.
- Lehecka, Wang and Garcia; Isengildina-Massa et al.; Karali (USDA report effects) -> Commodity reader (and X8 for
  WASDE).
- Diebold et al. (2017) "Commodity Connectedness" -> Commodity reader.

---

## Candidate mechanisms (what this log supports; the lead decides)

1. Macro-announcement-day long, full session, equity index futures.
   - Sources: K9C-003 (P-K9C-003-a, -b, -c, -e), K9C-001 (P-K9C-001-a, -b, -c, -h), K9C-002 (P-K9C-002-a, -b).
     Conflicting: K9C-004 (P-K9C-004-b, -c, -d, -e), K9C-007 (P-K9C-007-a, -b) for the FOMC part.
   - Date set: trade dates with a scheduled release of employment (NFP), the earlier of CPI/PPI (or both), ISM
     manufacturing, GDP (advance and third), FOMC (K9C-003's list); 44 a year, about 50-55 dates in the window (17-18%);
     the K9C-001 variant (inflation, employment, FOMC) about 40 dates.
   - Sign: long. Hold: the 17:00 CT reopen to C_X - 2 min (close-to-close in the source), flat by F.
   - Products: MNQ, M2K, MYM (US market index evidence, flagged; no Nasdaq-100 or Russell-specific result found).
   - Closest exclusion: X12 (turn-of-month), through the day-of-month overlap K9C-004 documents; X4 and X6 differ by
     mechanism (no pre- or post-release move is read). The bond version fails M_X (K9C-001 note, K9C-011).
2. Pre-announcement overnight long (uncertainty premium), equity index futures.
   - Sources: K9C-006 (P-K9C-006-a, -b, -c, -e, -f, -g); supporting K9C-005 (P-K9C-005-b) for FOMC; conflicting
     K9C-002 (P-K9C-002-c), K9C-007 (FOMC part gone), and K9C-006's own 2012-2018 row (P-K9C-006-f).
   - Date set: NFP, ISM manufacturing and GDP release dates (36 a year, about 43 in the window, 14%), FOMC optional (44
     a year, about 52).
   - Sign: long. Hold: 17:00 CT reopen to 5 minutes before the release (07:25 CT for 07:30 CT releases, 08:55 CT for
     ISM, about 12:55 CT for FOMC); at least 14 hours. The source starts at the 15:00 CT cash close of the prior day.
   - Products: MNQ, M2K, MYM (S&P 500 futures evidence, flagged).
   - Closest exclusion: X4 (pre-release drift). The source argues a different mechanism (P-K9C-006-d); the lead rules.
3. Bitcoin Monday long (weekly seasonal), MBT. Weak.
   - Sources: K9C-014 (P-K9C-014-a, -b, -d), K9C-015 (P-K9C-015-a, -b). Conflicting: P-K9C-014-c (per-year reversal);
     no post-2017 full-text evidence found.
   - Date set: Mondays, about 58 in the window (19%). Sign: long. Hold: the Monday trade date, 17:00 CT Sunday reopen to
     F. Product: MBT. Closest exclusion: X15 (Monday MBT; differs in mechanism, a weekly seasonal rather than hourly
     TSMOM) and X14 (no cross-market signal here).
4. Futures weekend effect (long Friday session or short Monday session). Pointer only.
   - Source: K9C-016 (P-K9C-016-a, -b), abstract only. Conflicting: K9C-017 (P-K9C-017-a), K9C-018 (P-K9C-018-b) for
     equities; K9C-019 (P-K9C-019-b) for old Treasury futures.
   - Date set: Fridays (about 60) or Mondays (about 58), 20%. Products: unknown until the full text is read. Closest
     exclusion: none by mechanism; X15's note admits a weekend-risk premium.

Not candidates as stated (logged honestly):
- Pre-FOMC drift alone (K9C-005): 10 dates in the window, and a non-survivor after 2015 (K9C-007).
- FOMC-day FX short-dollar (K9C-010): 10 dates, below the floor, no post-2010 evidence.
- FOMC-cycle even weeks (K9C-008): above the frequency cap; week 0 with the cap gives about 20 trips; the mechanism is
  disputed by two of its authors (K9C-009).
- Treasury announcement-day premium (K9C-001 bonds, K9C-008 bonds, K9C-011): per-day premium below M_X for ZF, ZN, ZB,
  and insignificant after the financial crisis (K9C-011).
- Pre-holiday (K9C-020): about 13 dates in the window; non-survivor for large caps after 1990; small-firm survivor only.
- Options-expiration week (K9C-021): stocks, abstract only; at most about 30 trips with the cap; X13-adjacent.
- Halloween / seasonal months (K9C-022): no daily trigger, half of all dates, non-survivor in S&P futures.

End: 2026-10-02 22:52 PDT.
