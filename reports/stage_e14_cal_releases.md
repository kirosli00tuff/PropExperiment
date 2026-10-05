# Stage E.14 release calendar: EIA NGS, EIA WPSR, FOMC statements, 2010-06-01..2019-05-31

Worker CalendarProbe-OpusHigh (Part B), built 2026-10-05T10:05:37Z. JSON: reports/stage_e14_cal_releases.json (schema e14_release_calendar/1). Pages and fetch log: reports/stage_e14_briefs/pages/probe/ (subfolders ngs/, wpsr/, fomc/; fetch_log.md). Terms checks: reports/stage_e14_briefs/pages/terms_checks.md (archive.org, eia.gov, federalreserve.gov rows). No market data opened.

## Method

- Grades: evidence/time_evidence: official = the issuer's own record (EIA schedule, report page or archive; Fed statement or meeting page or the Fed's stated release-time rule), secondary = another allowed official record, inferred = derived from a stated rule, unverified = not sourced. Every row carries its quote, its schedule source and, where found, the record of the actual release.
- NGS: EIA's WNGSR holiday release schedule (ir.eia.gov/ngs/schedule.html), every distinct Wayback capture 2010-04..2019-12 (27), gives the standing rule ("The standard release time and day of the week will be at 10:30 a.m. (Eastern time) on Thursdays with the following exceptions.") and each year's exception rows; a row replaces the Thursday of its week, an "EIA Closed" row the previous Thursday, and a later capture's row supersedes an earlier one for the same week. Actual releases: every distinct Wayback capture of ir.eia.gov/ngs/ngs.html 2010-05..2019-06 ("Released: <date> at <time> ... for the Week Ending <date>"); otherwise EIA's Natural Gas Weekly Update of the scheduled day quoting that week's WNGSR storage figure (date corroboration only). C13's drop_actual_differs is set where a report page shows a date or time different from the schedule.
- WPSR: EIA's WPSR holiday schedule (old URL .../weekly_petroleum_status_report/schedule.html 2010-2012, schedule.cfm 2013-2017, schedule.php 2017-2019; 46 distinct Wayback captures) keyed by data week; actual release dates from EIA's WPSR archive index ("Release date" / "Data ending" table, from 2011-08-03). Before 2011-08 no EIA archive page exists (probed: 404) and no Wayback list of 2010-2011 issues exists (wpsr_2010_11.html never captured); those weeks rest on the schedule, with EIA's This Week in Petroleum archive list as same-day corroboration.
- FOMC: the Fed's FOMC historical pages 2010-2019 list every meeting and conference call; each statement press release was read for its date. Times: the statement header ("For release at 2:00 p.m. ...", 2016 on), else the Fed's meeting page for press-conference meetings ("Released <date> at <time>"), else the Fed's 2013-03-13 rule (2 p.m. for all regularly scheduled meetings), else 14:15 inferred from the Fed's 2011-03-24 release (press-conference statements "around 12:30 p.m., one hour and forty-five minutes earlier than for other FOMC meetings").

## Counts

| Release | Total | official | inferred time | unverified (date or time) | by year |
|---|---|---|---|---|---|
| NGS | 470 | 470 | 0 | 0 | 2010: 31, 2011: 52, 2012: 52, 2013: 52, 2014: 53, 2015: 52, 2016: 52, 2017: 52, 2018: 52, 2019: 22 |
| WPSR | 470 | 469 | 0 | 1 | 2010: 31, 2011: 52, 2012: 52, 2013: 52, 2014: 53, 2015: 52, 2016: 52, 2017: 52, 2018: 52, 2019: 22 |
| FOMC | 72 | 58 | 14 | 0 | 2010: 5, 2011: 8, 2012: 8, 2013: 8, 2014: 8, 2015: 8, 2016: 8, 2017: 8, 2018: 8, 2019: 3 |

NGS actual-release evidence: report page 304, NGWU states the release time 11, NGWU same day 126, NGWU other day 1, schedule only 28. drop_actual_differs rows: 0.

| NGS year | releases | report page | NGWU states time | NGWU same day | NGWU other day | schedule only |
|---|---|---|---|---|---|---|
| 2010 | 31 | 18 | 0 | 10 | 0 | 3 |
| 2011 | 52 | 27 | 0 | 24 | 0 | 1 |
| 2012 | 52 | 25 | 0 | 26 | 0 | 1 |
| 2013 | 52 | 17 | 0 | 26 | 1 | 8 |
| 2014 | 53 | 18 | 2 | 31 | 0 | 2 |
| 2015 | 52 | 36 | 9 | 1 | 0 | 6 |
| 2016 | 52 | 49 | 0 | 0 | 0 | 3 |
| 2017 | 52 | 42 | 0 | 7 | 0 | 3 |
| 2018 | 52 | 52 | 0 | 0 | 0 | 0 |
| 2019 | 22 | 20 | 0 | 1 | 0 | 1 |

## Every unsourced or unverified instant

| id | what | reason |
|---|---|---|
| WPSR-2012-11-01 | time | release moved off schedule; no EIA record of the time found |

Inferred FOMC times (date official, time inferred from the Fed's 2011-03-24 rule):

| id | time ET | note |
|---|---|---|
| FOMC-2010-06-23 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; the statement predates that release (practice described as existing, no document dated this year read) |
| FOMC-2010-08-10 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; the statement predates that release (practice described as existing, no document dated this year read) |
| FOMC-2010-09-21 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; the statement predates that release (practice described as existing, no document dated this year read) |
| FOMC-2010-11-03 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; the statement predates that release (practice described as existing, no document dated this year read) |
| FOMC-2010-12-14 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; the statement predates that release (practice described as existing, no document dated this year read) |
| FOMC-2011-01-26 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; the statement predates that release (practice described as existing, no document dated this year read) |
| FOMC-2011-03-15 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; the statement predates that release (practice described as existing, no document dated this year read) |
| FOMC-2011-08-09 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; no meeting-specific time found |
| FOMC-2011-09-21 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; no meeting-specific time found |
| FOMC-2011-12-13 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; no meeting-specific time found |
| FOMC-2012-03-13 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; no meeting-specific time found |
| FOMC-2012-08-01 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; no meeting-specific time found |
| FOMC-2012-10-24 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; no meeting-specific time found |
| FOMC-2013-01-30 | 14:15 | 14:15 inferred: the Fed's 2011-03-24 release puts non-press-conference statements 1 h 45 min after ~12:30 p.m.; no meeting-specific time found |

## Every deviation from schedule, cancellation and superseded schedule row

| release | week ending | scheduled (ET) | actual | re-release seen | note | source |
|---|---|---|---|---|---|---|
| WPSR | 2012-10-26 | 2012-10-31 10:30 | 2012-11-01 | - | date moved off schedule (Hurricane Sandy week); time unverified | wpsr_archive_index |
| NGS | 2015-11-06 | 2015-11-13 10:30 | 2015-11-13 10:30 (original, per NGWU) | 2015-11-16 15:00 | report page shows a re-release (re-estimate); original release on schedule per EIA's NGWU | wb_20151117040020_ngs |
| NGS | 2018-08-31 | 2018-09-06 10:30 | 2018-09-06 10:30 (earliest capture) | 2018-09-10 15:00 | a later capture of the report page shows a re-release; the earliest capture matches the schedule | wb_20180911024448_ngs |

- FOMC: Unscheduled FOMC conference calls in range (2010-10-15, 2011-08-01, 2011-11-28) list no statement on the Fed's historical pages; no rows. Other releases issued with statements (Statement on Longer-Run Goals, 2014-09-17 Policy Normalization Principles, 2017-06-14 addendum, 2019-01-30 and 2019-03-20 balance-sheet statements) share the statement's instant and add no row.
- WPSR: originally scheduled 2012-10-31 10:30 America/New_York (week ending 2012-10-26), replaced by 2012-11-01: not released on the scheduled day; EIA's archive dates the release 2012-11-01 (no EIA notice of the reason or time found); quote ""
- WPSR: originally scheduled 2013-10-17 11:00 America/New_York (week ending 2013-10-11), replaced by 2013-10-21: schedule row superseded in a later EIA schedule capture; quote "October 11, 2013 October 17, 2013 Thursday 11:00 a.m. Columbus"
- WPSR: originally scheduled 2013-12-26 11:00 America/New_York (week ending 2013-12-20), replaced by 2013-12-27: schedule row superseded in a later EIA schedule capture; quote "December 20, 2013 December 26, 2013 Thursday 11:00 a.m. Christmas"
- WPSR: originally scheduled 2014-01-02 11:00 America/New_York (week ending 2013-12-27), replaced by 2014-01-03: schedule row superseded in a later EIA schedule capture; quote "December 27, 2013 January 2, 2014 Thursday 11:00 a.m. New Year's"
- NGS: originally scheduled 2013-10-17 10:30 America/New_York (week ending 2013-10-11), replaced by 2013-10-22: normal Thursday release not made; EIA schedule row gives an alternate date with reason 'EIA Closed' (2013 lapse in appropriations); quote "10/22/2013 Tuesday 10:30 a.m. EIA Closed"

FOMC statements whose time comes from a meeting page and is not 12:30 or 14:00:

- FOMC-2012-01-25 12:20 ET: Released January 25, 2012 at 12:20 p.m.
- FOMC-2012-04-25 12:35 ET: Released April 25, 2012 at 12:35 p.m.
- FOMC-2012-06-20 12:35 ET: Released June 20, 2012 at 12:35 p.m.
- FOMC-2012-09-13 12:35 ET: Released September 13, 2012 at 12:35 p.m.

Schedule-only NGS weeks (no report capture, no matching NGWU): 2010-11-24, 2010-12-23, 2010-12-30, 2011-12-29, 2012-12-28, 2013-04-25, 2013-06-20, 2013-07-03, 2013-08-08, 2013-10-22, 2013-11-21, 2013-12-19, 2013-12-27, 2014-04-17, 2014-11-14, 2015-06-18, 2015-07-02, 2015-07-23, 2015-07-30, 2015-10-15, 2015-12-31, 2016-02-11, 2016-10-13, 2016-11-23, 2017-04-13, 2017-06-08, 2017-06-29, 2019-04-18.

Quote check: every row's quotes were re-found in the saved source pages by script (NGS 1365, WPSR 940, FOMC 117 quotes; failures 0). Record: reports/stage_e14_briefs/pages/probe/verify_releases.json.

## Limits

- NGS weeks with neither a report capture nor an NGWU rest on EIA's schedule alone (graded official under calendar_rules.md); their actual release is not confirmed.
- WPSR 2010-06..2011-07: no EIA archive; actual dates are not confirmed by a WPSR page (TWIP same-day corroboration only).
- FOMC 14:15 times before 2013-03-20 for non-press-conference meetings are inferred; 2010 statements predate the rule document.
