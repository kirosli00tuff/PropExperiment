# Stage E.14 Task 2: calendars for both tests (no prices)

Lead summary, 2026-10-05. Workers: CalendarBuilder-Equity-OpusHigh (equity, rates, FX, grains), CalendarBuilder-
Commod-OpusHigh (energy, metals, energy full sessions), CalendarProbe-OpusHigh (2012 probe, then the release
calendar). Rules and schema: reports/stage_e14_briefs/calendar_rules.md. Worker reports:
reports/stage_e14_cal_financials.md, reports/stage_e14_cal_commod.md, reports/stage_e14_cal_releases.md,
reports/stage_e14_probe.md. Evidence: reports/stage_e14_briefs/pages/ (cme_holiday/, cal_equity/, cal_commod/,
probe/; fetch logs with UTC time and sha256 per file; terms_checks.md). No price, bar, store or quote was read.

## The files (every one loads through its frozen reader)

| File (copied byte-identical to data/calendars/hist2010/<group>.json for the six groups) | sha256 | Trade dates | Closures | Early halts | Late opens | Unsourced |
|---|---|---|---|---|---|---|
| reports/stage_e14_cal_equity.json | b12aee433635bc8334adb15d8f06c21255b0cb24889ea123a4d4375fb22657be | 2,325 | 24 | 78 | 6 | 0 |
| reports/stage_e14_cal_rates.json | 099ac84eb88c4e2bef67814e668d04fc4e88ad2ef1b3ea52114c53abd25382a4 | 2,324 | 25 | 97 | 6 | 0 |
| reports/stage_e14_cal_fx.json | 463c256b38a530fb1b150b542db21449d704d5b4cfa5308bd018d2e0e05b0591 | 2,325 | 24 | 96 | 6 | 0 |
| reports/stage_e14_cal_energy.json | c7a58e904571028f412dfe7f1039aa3c6cc89da8117e112e99a39d6d0bdeee6c | 2,323 | 26 | 73 | 0 | 0 |
| reports/stage_e14_cal_metals.json | 7eb64ead635aafb932422f5f31d2ff483ed22247ae0eaacccc71f798386991e9 | 2,323 | 26 | 73 | 0 | 0 |
| reports/stage_e14_cal_grains.json | 1197496f224636e7330f6da0b50ae45063ffb085fc780e95b54bc078955a7a61 | 2,269 | 80 | 23 | 25 | 0 |
| reports/stage_e14_cal_energy_full_sessions.json | 3f2a273a61613a73867929160d777367e06749b963fcf18b0b27e3f325083d74 | 2,250 full sessions (C1's recomputed rule agrees) | | | | |
| reports/stage_e14_cal_releases.json | see section "Release calendar" | NGS 470, WPSR 470, FOMC 72 | | | | 1 time |

Coverage 2010-06-01..2019-05-31 for every file. Counts from v10's loader (data.hist_calendar.load_hist_group_calendar).
Every status is graded "cme"; no time is graded "unverified" in the six group files.

## The 2% stops (checked before any price is bought)

| Rule | Window | Unsourced | Share | Result |
|---|---|---|---|---|
| C2 section 3 (equity) | 2011-05-03..2019-04-30 | 0 of 2,064 trade dates | 0.0% | does not fire (C2 stopped on its power rule instead; reports/stage_e14_gex.md) |
| C1 ruling C12, each group | 2010-06-07..2019-04-30 | equity 0/2,298, rates 0/2,297, FX 0/2,298, energy 0/2,296, metals 0/2,296, grains 0/2,243 | 0.0% | does not fire |
| C1 ruling C12, releases | 2010-06-07..2019-04-30 | 1 release instant (WPSR 2012-11-01, the post-Sandy delayed release: date sourced, time not) | 1 NG date at most | does not fire |

## Findings that differ from the 2019-2026 calendars

- Energy and metals share one CME schedule row in every year; Globex close 16:15 CT until trade date 2015-09-18,
  16:00 CT from 2015-09-21 (CME Globex notice of 2015-09-14). Holiday halts 12:15 CT until 2014-02-17, 12:00 CT
  from 2014-05-26; the day after Thanksgiving and Christmas Eve close 12:45 CT. Five 2010-2011 pre-holiday
  Fridays closed at 15:15 CT. Energy and metals traded regular hours on 2012-10-29/30 (Sandy) and 2018-12-05.
  The commodity builder's 2012 energy file equals the probe's, built independently.
- Equity: three session regimes (to 2012-11-16 the 15:30-16:30 CT segment opened the next trade date; from
  2012-11-19 the 15:30-16:15 CT segment belongs to the same trade date; from 2015-09-21 it ends 16:00 CT).
  Holiday halts 10:30 CT until 2014-02, then 12:00 CT. Sandy: equity halted 08:15 CT on 2012-10-29 and 10-30.
  2018-12-05: equity halt 08:30 CT, rates closed, FX and grains normal.
- Rates: Sandy halt 11:00 CT on 2012-10-29 only. Grains: Monday-holiday full closures (hence 80 closures), the
  day after Thanksgiving both a late open and an early halt (as grains.py holds it), the day close 13:15 -> 13:20
  CT dated 2015-07-06.

## Release calendar (C1's D8 list: NGS, WPSR, FOMC)

reports/stage_e14_cal_releases.json (schema e14_release_calendar/1) and .md: 470 NGS, 470 WPSR and 72 FOMC
releases; every date graded official; NGS times official (EIA schedule), with 72 actual releases confirmed by the
report's own page and 43 by EIA's Natural Gas Weekly Update of the same day; FOMC times official for 58 and
inferred for 14; one WPSR time unsourced (2012-11-01). C13's drop rule: see the .md (drop_actual_differs per NGS
row).

## Limits the lead accepts (disclosed in C1's freeze)

1. The unscheduled-closure check rests on CME's yearly CFTC rule-filing indexes (2011-2019), Wayback scans of
   CME press releases, the Sandy and 2018 sources and every document in CME's yearly holiday archives. CME's
   roughly 500 weekly Globex notices were not read one by one, so an announced intraday Globex outage could be
   missing; June-December 2010 has no filing index. A missing outage would show as missing bars, which the frozen
   code already drops; it cannot add a bar.
2. Day-session opens (design D6's O) after 2015-09 are carried forward for energy (08:00 CT) and metals; equity
   keeps D6's (08:30, 15:00). These are the design's constants, the same values the E.12 training panel used,
   not calendar facts.
3. Holiday-halt sessions keep their own short trade date (the data.cme_calendar convention), although CME booked
   them to the next trade date.
4. The pre-2012-11-19 equity segment 15:30-16:30 CT is written as an offset -1 segment; on Monday trade dates and
   after closures it maps to hours with no bars, so it books nothing.
