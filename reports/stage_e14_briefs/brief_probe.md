# Brief: CalendarProbe-OpusHigh (Stage E.14 Task 1, then the release calendars)

Read reports/stage_e14_briefs/calendar_rules.md first. It binds you. Your pages folder: reports/stage_e14_briefs/pages/probe/.

## Part A (first, and write it before Part B): the calendar probe that gates test C1
Objective: for calendar year 2012, source at evidence grade (C1 ruling C12, defined in calendar_rules.md):
1. the CME ENERGY group calendar (NYMEX energy: NG, CL): every 2012 weekday's status (normal trade date, full
   closure, early halt with its halt time, late open), including unscheduled events (Hurricane Sandy
   2012-10-29/30 and anything else CME announced), and the regular Globex session hours in force in 2012;
2. the EIA Weekly Natural Gas Storage Report (NGS, "WNGSR") release dates and times for 2012: every weekly
   release, including holiday-shifted ones (normally Thursday 10:30 ET), each with its grade.

Fixed rule (stage prompt, not yours to change): if more than 2% of 2012's energy trade dates, or more than 2 NGS
release dates, cannot be sourced at "cme"/"official" or "secondary" grade, C1 is dropped. Compute both counts
honestly and state whether the rule fires; the lead rules.

Method hints (verify, do not trust): CME published yearly holiday calendars and per-holiday "Globex holiday
trading schedule" files under cmegroup.com/tools-information/holiday-calendar/ (look for 2012 captures via the
Wayback CDX API, prefix search); earlier stages' method is in reports/stage_e2a_calendar_sources_energy.md (grep
it). EIA's storage report has a release schedule page (ir.eia.gov/ngs/schedule.html and eia.gov/naturalgas/
storage/ pages; check Wayback captures from 2011-2013) and each weekly report states its own release date.
Look at how E.2b/E.5 sourced NGS (reports/stage_e2b_release_sources_commodity_log.md, strategy/members/k4/
_releases.py header, by grep) for the drop rule "drop_actual_differs" (C1 ruling C13).

Output A: reports/stage_e14_probe.md with: a table of every 2012 energy exception date and every unsourced date
(day, status, halt time, grade, time grade, source id, verbatim quote); the count of 2012 energy trade dates, the
count unsourced and the share; the 2012 NGS table (every release: scheduled date, release date and ET time,
grade, source id, quote, any delay); the count of NGS dates unsourced; the rule's result; a sources table (URL,
capture timestamp, fetched UTC, saved file, sha256). Also write the 2012 energy calendar as JSON
reports/stage_e14_briefs/probe_energy_2012.json in the e14_hist_calendar/1 schema (coverage 2012-01-01..
2012-12-31). When Part A is written, print one line "PROBE WRITTEN" in your log and continue.

## Part B (after Part A): the release calendar for NG's D8 list, 2010-06-01..2019-05-31
Only if Part A's rule does NOT fire (if it fires, stop after Part A and return).
Objective: every release instant of (1) EIA NGS, (2) EIA WPSR (Weekly Petroleum Status Report, normally
Wednesday 10:30 ET, holiday-shifted), (3) FOMC statements (scheduled and unscheduled), 2010-06-01..2019-05-31,
each with date, local time, tz, UTC instant, grade, source id and verbatim quote, plus cancellations and delays.
Follow the format and verification of reports/stage_e2b_release_calendar.json "releases" rows (read its schema
with a short script; never load it whole): {"id": "NGS-2012-01-05", "release": "NGS", "release_name", "date",
"time_local", "tz", "instant_utc", "evidence", "source": {...}}. For NGS also record, per release, whether the
actual release differed from the schedule (for C13's drop rule as E.5 applied it: read
strategy/members/k4/_releases.py lines 1-40 for the rule's exact wording).
Output B: reports/stage_e14_cal_releases.json (schema "e14_release_calendar/1": coverage, releases[],
cancellations[], unsourced[], sources{}, counts per release type and per year) and
reports/stage_e14_cal_releases.md (method, counts, every unsourced or unverified instant, every deviation).

Boundaries: no price or market data (calendar_rules.md). Other workers build the CME group calendars (equity,
rates, FX, grains: CalendarBuilder-Equity; energy and metals: CalendarBuilder-Commod); do not build those. The
GEX file and all code belong to others. Stop rule: finish Part B, or return early with what is done if a budget
notice stops your searches. Return per calendar_rules.md, with Part A's two counts and the rule's result first.
