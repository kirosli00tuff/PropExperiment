# Stage E.14 Task 2: CME energy and metals calendars, 2010-06-01..2019-05-31

Worker CalendarBuilder-Commod-OpusHigh, 2026-10-05 (about 00:35-01:35 PDT). No market data was opened.
Outputs:
- `reports/stage_e14_cal_energy.json` (schema e14_hist_calendar/1, group energy: CL, MCL, QM, NG, MNG, QG, RB, HO)
- `reports/stage_e14_cal_metals.json` (group metals: GC, MGC, SI, SIL, HG, MHG)
- `reports/stage_e14_cal_energy_full_sessions.json` (ENERGY_FULL_SESSIONS format, 2,250 dates)
- Evidence: `reports/stage_e14_briefs/pages/cme_holiday/` (CME yearly `holiday-calendars.zip` 2010-2019 and the
  cross-check and full-year-list files), `reports/stage_e14_briefs/pages/cal_commod/` (spec pages, notices, the
  press release, `zip_text/` text renderings of every zip member with a README, `fetch_log.md`).
- Build and verbatim check: `scratchpad/cal_commod/build.py`, `data_entries.py`, `common.py` (outside the repo).

## Method

- **Sources.** CME Group documents only, all from Wayback captures. cmegroup.com itself was never fetched.
  The core source is CME's yearly `YYYY-holiday-calendars.zip` for 2010-2019. Each zip holds CME's Globex
  schedule for every holiday of that year: PDFs for 2010, 2011 and 2013; Word source files for 2012; XLS files
  for 2014-2019. From 2018 the zips also hold settlement notices and clearing advisories.
- **Rows read.** Every schedule read has one row for both groups:
  - "NYMEX, COMEX® and DME Products on CME Globex" (2010-2012)
  - "NYMEX, COMEX & Dubai Mercantile (DME) Products" (2013)
  - "Energy, Metals & DME Products" (2014-2016)
  - "Energy, Metals & DME" (2017-2019)

  The energy and metals entries are therefore identical. Only the session rows differ.
- **Exceptions in those rows.** Every exception listed in those rows concerns TAS/TAM contracts, NYMEX Softs TAS,
  EUA, Environmental, Oman or palm-oil products. None concerns outright CL/NG/RB/HO/GC/SI/HG futures.
- **Verbatim check.** Every quote fragment (split on " ... ") must be a substring of the cited document's text
  after whitespace normalization. It passed for all 99 entries, 102 no-entry findings, 10 year-list quotes and
  every session quote. The build asserts this check.
- **Full-year holiday lists.**

  | Year | Full-year list |
  |---|---|
  | 2010 | CME Globex 2010 holiday calendar PDF (all twelve 2010 schedules) and ClearPort 2010 |
  | 2011 | ClearPort 2011 |
  | 2012 | ClearPort 2012 (in the 2012 zip) and the Nov 2012 holiday-calendar page |
  | 2013, 2014 | ClearPort lists inside the zips |
  | 2015-2017 | ClearPort schedules (fetched) |
  | 2018, 2019 | The holiday-calendar page's "CME Globex will observe the following holidays in 2018/2019" lists |

  Files fetched by other workers were reused, not refetched, and the reuse is logged.

## Counts

| | Energy | Metals |
|---|---|---|
| Weekdays 2010-06-01..2019-05-31 | 2,349 | 2,349 |
| Trade dates | 2,323 | 2,323 |
| Full closures | 26 | 26 |
| Early halts | 73 | 73 |
| Late opens | 0 | 0 |
| No-entry findings (holiday-adjacent or event days found normal) | 102 | 102 |
| Unsourced | 0 | 0 |
| Trade dates in 2010-06-07..2019-04-30 | 2,296 | 2,296 |
| Unsourced share in that window | 0.0% | 0.0% |

Per year (both groups):

| Year | Full-year list | Closures | Halts | Trade dates | Unsourced |
|---|---|---|---|---|---|
| 2010 (Jun-Dec) | wb_2010_globex_holcal, wb_clearport_2010 + z2010 | 1 | 8 | 153 | 0 |
| 2011 | wb_clearport_2011 + z2011 | 2 | 8 | 258 | 0 |
| 2012 | ClearPort 2012 (z2012), holiday page Nov 2012 + z2012 | 3 | 8 | 258 | 0 |
| 2013 | ClearPort 2013 (z2013) | 3 | 8 | 258 | 0 |
| 2014 | ClearPort 2014 (z2014) | 3 | 8 | 258 | 0 |
| 2015 | wb_clearport_2015 + z2015 | 3 | 8 | 258 | 0 |
| 2016 | wb_clearport_2016 + z2016 | 3 | 7 | 258 | 0 |
| 2017 | wb_clearport_2017 + z2017 | 3 | 7 | 257 | 0 |
| 2018 | holiday page 2018-02-17 + z2018 | 3 | 8 | 258 | 0 |
| 2019 (Jan-May) | holiday page 2019-01-22 + z2019 | 2 | 3 | 107 | 0 |

Every status grade is "cme". Every time grade is "cme", or "n/a" for the closures. No date is secondary or
unverified.

## What differs from the 2019-2026 calendars (findings)

- **Regular Globex session.**
  - 17:00-16:15 CT with a 45-minute break up to trade date 2015-09-18.
  - 17:00-16:00 CT with a 60-minute break from trade date Monday 2015-09-21. The source is CME's Globex notice of
    2015-09-14: "Effective this Monday, September 21 ... the closing times for the following markets will now occur
    15 minutes earlier Monday through Friday at 16:00 CT. CME Equity CBOT Equity COMEX NYMEX DME". The CL
    specification page still showed 16:15 on 2015-09-23 and 16:00 on 2015-10-08. That gap is a lag on the web
    page, not a second change.
- **Holiday halt times (Monday holidays, July 4, Thanksgiving Day).**
  - 12:15 CT from 2010 to 2014-02-17. The last 12:15 halts were MLK and Presidents Day 2014.
  - 12:00 CT from Memorial Day 2014-05-26 on.
- **Early closes on 2010-2011 Fridays.** Five Fridays closed early at 15:15 CT, which CME labels "Early CME Globex
  close":
  - 2010-07-02
  - 2010-09-03
  - 2010-10-08 (the Friday before Columbus Day, although Columbus Day itself was normal)
  - 2010-12-31
  - 2011-01-14

  From Presidents Day 2011 on, these Fridays have the regular close. Two contemporaneous captures of the original
  CME files (2010-06-02 Labor Day, 2011-01-14 MLK) carry the same text as the zip copies. CME's 2010 combined
  Globex calendar (captured 2010-02-15) agrees as well.
- **Day after Thanksgiving.** 12:45 CT every year.
- **Christmas Eve on a weekday that is not the observed holiday.** 12:45 CT in 2012, 2013, 2014, 2015 and 2018.
- **Regular days.** These had the regular close:
  - 2010-12-23 and 2011-12-23, 2016-12-23 and 2017-12-22 (Fridays or Thursdays before an observed Christmas)
  - every New Year's Eve except 2010-12-31
  - every day before July 4

  On 2010-12-23, 2011-12-23 and 2016-12-23 only TAS contracts closed early.
- **Columbus Day and Veterans Day.** Normal every year. In 2013-2017 the CME sheet says "Products listed on Globex
  are unaffected and will run on a normal schedule". For 2018 the evidence is CME's "All products will settle at
  their normal times" notices.
- **Good Friday.** A full closure every year, including the jobs-report Good Fridays 2012-04-06 and 2015-04-03.
- **Unscheduled events.** Both are recorded as no-entry findings with grade "cme".
  - Hurricane Sandy, 2012-10-29 and 2012-10-30. Only the NYMEX/COMEX trading floor was closed. CME Clearing
    advisory 12-464 says "All New York floor-traded products will be available on ClearPort as well as CME Globex
    during their regular market hours". CME Submission 12-363, posted by the CFTC, corroborates it (secondary).
  - National Day of Mourning, 2018-12-05. CME's press release says "All other markets on CME Globex ... will remain
    open for regular trading hours on Dec. 5". Only U.S. equity and interest-rate products closed.
- **Day session (D6 O, C).**
  - **Energy.**
    - 2010 to 2015-09: O 08:00 and C 13:30 CT, from the CL and NG open-outcry hours "9:00 a.m. – 2:30 p.m. (8:00
      a.m. – 1:30 p.m. CT)".
    - 2015-09 to 2019: C 13:30 CT from CME's settlement period 14:28-14:30 ET (CL wiki 2018, NG wiki 2016). The
      2019 CL page also says "TAS Trading ceases daily at 2:30 PM ET".
  - **Metals.**
    - 2010 to 2015-09: open-outcry gold 07:20-12:30, silver **07:25**-12:25, copper 07:10-12:00 CT.
    - 2015-09 to 2019: C from the 2016 settlement periods. Gold 13:29-13:30 ET, silver 13:24-13:25 ET, copper
      12:59-13:00 ET, all equal to the open-outcry closes.

## Judgment calls (for the lead to accept or overrule)

1. **Short trade dates.** A holiday halt keeps its own short trade date, under the rules convention and as in
   data/calendars/energy.py. This covers Monday holidays, midweek July 4, Thanksgiving Day, and Fridays that are
   themselves holidays (2014-07-04, 2015-07-03, close 12:00 CT). CME's own sheets book these sessions to the next
   trade date.
2. **Pre-holiday Friday 15:15 CT closes (2010-2011).** These are recorded as early_halt entries. They are therefore
   excluded from the full-sessions list.
3. **Monday closures with no "closed" line in the NYMEX section.** On 2011-12-26 and 2012-01-02 the NYMEX/COMEX
   section lists only the Monday 17:00 CT open for Tuesday's trade date. The status quote combines that line with
   the "Christmas Day Observed – Globex closed" / "New Years Observed – Globex closed" line in the same document.
   Both entries are graded "cme".
4. **2012 sources.** 2012 is sourced from the 2012 zip, which holds CME's Word source files of the 2012 schedules
   (.doc/.docx). It does not use the 2012 PDFs.
5. **2014 Presidents Day and Good Friday.** The 2014 PDFs in the zip are unreadable (broken xref), so the XLS
   versions in the same zip are used.
6. **Columbus Day and Veterans Day 2018.** CME's normal-settlement notices are taken as evidence of normal trading.
   The 2018 zip has no Globex sheet for these days, and CME's 2018 Globex holiday list omits them.
7. **Metals day_session_ct.** It is keyed by product: MGC, SIL and MHG take the full-size contract's hours. The
   silver O of 07:25 CT is CME's value. Design D6's 07:20 CT differs; this is not resolved here.
8. **Energy D6 O after 2015-09-21 (UNVERIFIED).** No CME document retrieved states an energy day-session open
   after the open-outcry hours left CME's spec pages in 2015. O 08:00 is carried forward. The same holds for the
   metals O values. The session rows say so. These are session-hour gaps, not trade-date status gaps, so they do
   not count as unsourced dates.
9. **"Complete exception list" basis.** I graded each year as having a complete exception list on two grounds: the
   full-year holiday list, plus CME's own schedule for each listed holiday.
10. **Limit of the unscheduled-closure check (the main caveat on the 0% figure).** The check covered:
    - every document in the yearly zips
    - the holiday-calendar pages
    - the Sandy and 2018 mourning-day sources
    - one WebSearch restricted to cmegroup.com, which returned no 2010-2019 hit

    I did not read CME's roughly 500 weekly Globex notices for 2010-2019 one by one. An announced intraday Globex
    outage in energy or metals could therefore be missing. If the lead wants that closed, a notice-by-notice sweep
    of `cmegroup.com/tools-information/lookups/advisories/electronic-trading/` and
    `cmegroup.com/notices/electronic-trading/` (CDX lists them) is the next step.

## Independent check against the probe

`reports/stage_e14_briefs/probe_energy_2012.json` (CalendarProbe) appeared while I worked. It agrees with this file
on all 11 entries for 2012:

| Count | Value |
|---|---|
| Full closures | 3 |
| Early halts | 8 |
| Halt times | all match |
| Trade dates | 258 |
| Regular session | 17:00-16:15 CT |
| NG day session | 08:00-13:30 |

There is no disagreement.

## Full-sessions list

`reports/stage_e14_cal_energy_full_sessions.json` uses the rule quoted from strategy/members/k4/_calendar.py: trade
dates with early_halt_ct None. Applied here, that is weekdays minus full closures minus early halts, over
2010-06-01..2019-05-31. The result is 2,349 - 26 - 73 = **2,250 dates**. The file records the energy file's sha256.

## Fetch accounting

- About 47 successful fetches logged in `pages/cal_commod/fetch_log.md`: 10 yearly zips, 3 ClearPort schedules,
  2 cross-check PDFs, 23 spec, wiki and notice pages, 1 press release, the terms page, and CDX queries. Six other
  workers' files were reused.
- 4 failure groups, logged: Wayback refused connections or showed "Temporarily Offline" at about 07:37-07:39Z,
  07:47-07:53Z and 07:54-07:59Z, plus one CDX 504.
- WebSearch: 1. Firecrawl: 0.
