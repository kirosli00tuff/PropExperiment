# Grains class notes (Stage E.20 Part A, shared source; reader ProductReader-ZC-OpusHigh)

Written 2026-10-11 (PDT). The ZS and ZL readers cite this file as
`reports/stage_e20_briefs/shared/grains_class_notes.md`. Raw pages: `reports/stage_e20_briefs/pages/ZC/`
(fetch log `pages/ZC/fetch_log.tsv`; the URL, UTC time and sha256 of each page are also in
`reports/stage_e20_briefs/product_ZC.json`, key `fetch_log`).

## Bottom line for other readers

1. **The grains literature since 2015 is almost all about variance, jumps, volume and spreads around
   USDA releases. It contains no direction.** In every intraday study read, USDA reports raise
   volatility. The spike starts at the 11:00 CT release and lasts from about 10 minutes to about an
   hour. None of these studies gives a price-only directional rule with a per-trade size.
2. **Direction appears only when a proprietary analyst-survey surprise is used.** The Bloomberg and
   Reuters polls cannot be computed from bars or from calendars known in advance. In corn, the
   surprise response is complete within about 30 minutes, with no further drift to the day's close.
   Soybeans keep adjusting after 30 minutes (Anderson, McKenzie and Noyes 2024; see E4 below).
3. **The only sized directional intraday rule for grains is Baltussen et al.'s ROD to last-half-hour
   regression.** Corn: beta_ROD 0.82 (x100), t 2.09, R2 0.05%, out-of-sample R2 -0.01% (1982-07..
   2020-05). The pooled "Softs" group, which includes the grains and livestock, gives 0.65 (t 2.16),
   with out-of-sample R2 -0.01%. Rows: `shared/baltussen_notes.md` (NQ reader) and the on-disk copy,
   lines L3715 and L3774. r_ROD is already added by the E.20 prompt and must not be proposed again.
4. **The Aalto thesis has no commodities.** Per `shared/aalto_thesis_notes.md` (ZN reader), its sample
   is 20 equity, bond and currency futures. No grains reader should cite it.
5. **Limit-move continuation is sized only close-to-close, pooled over 9 commodities.** The next-day
   return is +40 to +62 bp after limit-up days and -38 to -63 bp after limit-down days, 1991-2016
   (Janardanan, Qiao and Rouwenhorst, JFM 2019; quoted from E.0's on-disk record). The paper's options
   result says most of the continuation shows up at the next open. The day-session share is not
   published. The corn-specific row is not retained (ou.edu's robots.txt disallows the PDF's path).

## Evidence rows (verbatim quotes; page/line refer to the saved text file)

| ID | Effect | Sample | Direction / size | Decay or OOS | Source, file | Grade |
|---|---|---|---|---|---|---|
| E1 | ROD -> LH momentum, corn (CN) | 1982-07-06..2020-05-01, 1-min, 08:30-13:20 CT | beta_ROD 0.82** (t 2.09), adj R2 0.05%, R2_OOS -0.01% | R2_OOS negative over the full sample; Fig. 4 panel (c), 2006-06..2020-05: CN t 2.8 (in-sample) | Baltussen, Da, Lammers, Martens, JFE 142 (2021); on-disk copy L3774, L2463 | primary |
| E2 | ROD -> LH, "Softs" pool (grains + livestock + softs) | 1981-04..2020-05 | beta_ROD 0.65** (t 2.16), R2 0.04%, R2_OOS -0.01% | as E1 | same, L3715 | primary |
| E3 | Commodity class, eta(r_ROD) portfolio | to 2020-05 | 4.34%/yr, SR 1.42, hit 0.56; about 1.72 bp per trade (NQ reader's /252 derivation) | 2000-2020 class beta 1.04 (t 2.86) vs 1974-1999 1.59 (t 3.92) | `shared/baltussen_notes.md` | [shared] |
| E4 | WASDE intraday surprise response, corn and soybeans | 2010-2021, 122 WASDE releases | corn news coefficient -0.023 (10 min, n.s.), -0.041** (30 min), -0.044* (day); soy -0.028, -0.061**, -0.124** | corn: "adjusts very little past the initial 30-minute time window"; needs Bloomberg poll (not causal from bars) | Anderson, McKenzie, Noyes, NCCC-134 2024; `anderson_mckenzie_noyes_2024.pdf.txt` lines 186-202 | primary (working paper) |
| E5 | WASDE-day intraday volatility curve | corn, soybeans, 2013-01..2023-04, 08:30-14:00 CT | volatility "subdued at the open", spike "right after 11:00 a.m. CT", fades "within about an hour"; no direction | n/a | Lee and Park (2024), summarized by co-author Park (Southern Ag Today); `tamu_afpc_wasde_days.txt` | secondary (author's summary) |
| E6 | Jumps around USDA reports, corn | 2008-2015, transaction prices | real-time trading of reports "substantially increased the frequency and the magnitude of jump risk"; no direction | n/a | Couleau, Serra, Garcia, NCCC-134 2018 (AJAE 2020); `couleau_serra_garcia_2018.pdf.txt` lines 36-43 | primary (working paper) |
| E7 | Volatility and spillover, corn-soy, USDA days | mid-quotes, 11:00 releases | volatility "would not settle down within the first hour after announcements"; no direction | n/a | Bian, Serra, Garcia, NCCC-134 2018; `bian_serra_garcia_2018.pdf.txt` lines 59-61 | primary (working paper) |
| E8 | Adjustment after continuous trading of reports | 2009-2014 intraday | adjustment "not instantaneous"; differences "persist only for a handful of trading minutes" | n/a | Adjemian and Irwin, AJAE 100(4) 2018, p. 1169, quoted by Isengildina-Massa (VT); `vt_isengildina_insights.txt` | secondary-only |
| E9 | Trend in USDA announcement effects (daily volatility) | corn, soybeans | "still informative and influential ... with a generally increasing trend", with "some reports whose impact show a declining potential" | n/a | Ying, Chen, Dorfman, NCCC-134 2017; `ying_chen_dorfman_2017.pdf.txt` lines 55-58 | primary (working paper), daily |
| E10 | Limit-day continuation | 1991-01-07..2016-05-23, daily, 9 commodities | pooled next-day close-to-close +40 to +62 bp (limit up), -38 to -63 bp (limit down); corn row not retained | close-to-open dominates (options result) | Janardanan, Qiao, Rouwenhorst, JFM 39(8) 2019; E.0 quotes in `reports/stage_e0_research_K6.md` lines 155-158 | secondary (on-disk quotes); not intraday |

Abstract-only items (not fetched again; E.0's quotes are in `reports/stage_e0_research_K6.md`):
- Aitkulova, Balsamo and Seamon (2026), AgEcon 10.22004/ag.econ.410270: "directionally correct drift
  prior to release suggests that we also observed informed trading". This is the source behind
  K6-wasdepre-01. Window and magnitudes are [unverified]. AgEcon Search blocks automated access (AWS
  WAF "verify that you're not a robot", logged 2026-10-11T17:38Z), and no other host was found.
- Zhang (2024), SSRN 4841490: "informed trading exists in commodity markets before the release date";
  horizon likely daily [unverified].
- Lehecka, Wang and Garcia (AEPP 2014), corn 2009-2012: reaction "persist[s] for approximately ten
  minutes"; no systematic over- or under-reaction. Pre-2015 and outside the "since 2015" scope; known
  here only through secondary summaries [secondary-only].
- Lee, Noyes, Park, McKenzie, Anderson, Yang (Agribusiness 2025, DOI 10.1002/agr.70150): returns from
  the private-forecast release close to the WASDE release close; "the corn mean is statistically
  indistinguishable from zero" (search snippet only, [unverified]). The window is close to close
  (overnight) and needs a survey: out of scope.

Checked and not used: ERS Amber Waves 2021 (corn projections, monthly horizon, not intraday); Jones
(2018 slides, HFT, no grains intraday result); Janzen and Legrand (2019, wheat volume forecasting);
Yang and McKenzie (2024, implied-volatility expectations, daily); Baltussen, Da and Soebhag "End-of-Day
Reversal" (EFMA 2024, individual stocks only).

## Release-time eras (USDA grain reports)

- "Since May 21, 2012, all sensitive USDA reports are released during trading hours (at 7:30:00 am CT
  until December 2012 and at 11:00:00 am CT since January 2013)" (Couleau, Serra, Garcia 2018, lines
  80-81).
- "From January 2008 to May 2012, the report release time was 07:30:00 when markets were closed"
  (same, line 406). WASDE and Grain Stocks: "Since January 2013, both reports are released at
  11:00:00 am CT" (lines 400-401).
- USDA's own notice (Federal Register 2012-06-08, doc. 2012-13951) lists the reports under review and
  states that "The current release times of 8:30 a.m. and 3 p.m. ET will remain unchanged until
  official comments are considered" (`fr_2012-06-08_nass_release_times.pdf.txt`, right column, lines
  32-36). NASS news release of 2012-08-03: "Current USDA schedules and release times of 8:30 a.m. and
  3:00 p.m. ET remain in effect until further notice" (`nass_newsroom_2012-08-03.pdf.txt`).
- USDA's 2012-09-19 decision document (usda.gov) could not be fetched: HTTP 403 (Akamai), with no
  Wayback capture (17:42Z and 17:51Z). The noon-ET start in January 2013 therefore rests on the two
  academic sources quoted above (Couleau et al.; Bian et al., line 192: "since January 2013 was
  rescheduled to take place at noon").
- Crop Progress: Mondays at 16:00 ET (15:00 CT), after the grain close. This is the frozen release
  calendar's time (245 rows at 16:00 ET and one at 17:00 ET, 2021-04-05).

## Grain session eras, 2010-2019 (CT)

Source: `data/calendars/hist2010/grains.json` "sessions" (E.14, CME schedules), the E.16 settlement
table `reports/stage_e16_settlement.md` lines 50-53 and 67-76, and Couleau et al.'s footnote 2 (lines
414-415).

| Era | Globex segments | Day session (calendar) | Settlement | USDA report time |
|---|---|---|---|---|
| 2010-06-01..2012-05-18 | 18:00 (d-1)-07:15, 09:30-13:15 | 09:30-13:15 | 13:15 | 07:30 CT, market closed |
| 2012-05-21..2013-04-05 | 17:00 (d-1)-14:00, continuous | 09:30-14:00 | 13:15 to 2012-06-22, then 14:00 from 2012-06-25 (E.16) | 07:30 CT during trading (to Dec 2012); 11:00 CT from Jan 2013 |
| 2013-04-08..2015-07-03 | 19:00 (d-1)-07:45, 08:30-13:15 | 08:30-13:15 | 13:15 | 11:00 CT |
| 2015-07-06..2019-05-31 | 19:00 (d-1)-07:45, 08:30-13:20 | 08:30-13:20 (hist2010) | 13:14-13:15 window (E.16 S25) | 11:00 CT |
| 2019-05-01..2026-06-19 | per `data/calendars/grains.py` | 08:30-13:15 (grains.py) | 13:14-13:15 | 11:00 CT |

Couleau et al. name the hours they used differently ("May 21-December 31, 2012: 7:00 to 14:00;
January 2, - April 5, 2013, from 9:30 to 14:00; since April 8, 2013, from 8:30 to 13:15, and since July
6, 2015, from 8:30 to 13:20"). These are analysis windows, not exchange hours.

## Calendars for the K6 / grains features

- WASDE dates: `strategy/members/k6/_wasde.py` covers 2019-05-01..2026-06-19 (85 dates, 58 in the
  search window), generated from the frozen release calendar `reports/stage_e2b_release_calendar.json`
  (2019-05-01..2026-06-21).
- 2010-2019: **no WASDE, Crop Production, Crop Progress or Grain Stocks calendar exists on disk.** E.14's
  `reports/stage_e14_cal_releases.json` (2010-06-01..2019-05-31) holds NGS 470, WPSR 470 and FOMC 72
  only. A public source for the dates exists: USDA ESMIS lists dated WASDE releases with a month filter
  back to 1973-09 (`esmis_wasde_publication.html`; the 2012-12 filter returns "Dec 11 2012"). The
  2013-01 filter returned no dated entry, so month-by-month completeness was not checked. ESMIS gives
  dates, not times. The times come from the release-time eras above.
- Not in the frozen D8 release list for any grain: Grain Stocks, Acreage and Prospective Plantings,
  all 11:00 CT reports since 2013. ZC's list is CROP_PROGRESS (246), CROP (85), WASDE (85), FOMC (57)
  and CROP_ANNUAL (7); counts are 2019-05..2026-06. Couleau et al. single out WASDE and Grain Stocks as
  the two reports "identified to have a major impact on corn futures prices".

## ZC listing (G17 lead)

ZC trades on Globex in both windows. The E.14 hist2010 calendar's Globex segments run from 2010-06-01
(CME schedules, sources in the file), and `data/calendars/grains.py` runs from 2019-05-01. That CBOT
agricultural futures began side-by-side electronic trading on 2006-08-01 is [secondary-only]: it rests
on search snippets of CBOT press releases on cmegroup.com, which is not fetched. The SEC copy of the
CBOT exhibit returned 403 without a declared contact. Databento pricing for ZC starts in 2010-07
(`reports/stage_e16_windows.json`).
