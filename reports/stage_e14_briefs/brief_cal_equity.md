# Brief: CalendarBuilder-Equity-OpusHigh (Stage E.14 Task 2: equity first, then rates, FX, grains)

Read reports/stage_e14_briefs/calendar_rules.md first. It binds you. Your pages folder:
reports/stage_e14_briefs/pages/cal_equity/ (CME holiday files go in the shared pages/cme_holiday/).

## Objective
Build the CME group calendars for 2010-06-01..2019-05-31, in schema e14_hist_calendar/1, in this order, writing
each file as soon as it is complete:
1. EQUITY (CME equity index futures: ES, NQ and the group in data/calendars/__init__.py). This one is needed
   first, by test C2 (ES, 2011-05..2019-04) and C1 (NQ). Write reports/stage_e14_cal_equity.json, then print
   "EQUITY WRITTEN" in your log, then continue.
2. RATES (CBOT Treasury futures: ZN and group) -> reports/stage_e14_cal_rates.json
3. FX (CME FX futures: 6E and group) -> reports/stage_e14_cal_fx.json
4. GRAINS (CBOT grains: ZC and group; note grains' own day session, daily break and any LATE_OPENS pattern, as
   data/calendars/grains.py describes for 2019-2026) -> reports/stage_e14_cal_grains.json

CME's per-holiday Globex schedules list every product group as a row in one file, so one document serves all
four groups: fetch each once (into pages/cme_holiday/) and read every row you need from it.

For every group: every holiday full closure and early halt (with halt time), late opens, unscheduled closures
or halts (Hurricane Sandy 2012-10-29/30; the 2018-12-05 national day of mourning; Good Fridays, including the
ones with a jobs report on which equity and rates traded a short session, e.g. 2012-04-06 and 2015-04-03; any
CME Globex outage announced by CME), and every dated change of the regular Globex session hours (for example the
equity 15:15-15:30 CT maintenance halt and the 16:15-17:00 CT break; rates and FX hour changes) as dated
"sessions" rows. The day session close matters: ES's regular cash-session close is 15:00 CT and its Globex day
continues to 15:15 CT; record what CME states for each period.

Method: start from how Stage D.1f and E.2a sourced 2019-2026 (reports/stage_e2a_calendar_sources_equity.md and
_rates.md, _fx.md, _grains.md, and the docstrings of data/cme_calendar.py and data/calendars/<group>.py, by
grep). Find 2010-2019 captures of CME's holiday-calendar folder and files with the Wayback CDX API (prefix
search on cmegroup.com/tools-information/holiday-calendar/ and cmegroup.com/trading-hours/files/ and
cmegroup.com/globex/ notices). NYSE's holiday pages (nyse.com, via Wayback) are an allowed SECONDARY source for
equity cash-market closures only; CME documents rule where they exist.

Output also reports/stage_e14_cal_financials.md: per group, per year, the documents used, the counts (trade
dates, closures, halts, unsourced, unsourced share), every unsourced or unverified date with the reason, and
every judgment call you made.

The 2% stop: C2 stops if more than 2% of the equity trade dates in 2011-05-03..2019-04-30 are unsourced; C1
stops if more than 2% of any needed group's dates in 2010-06-07..2019-04-30 are unsourced. Report both shares
for equity, and the share for each other group over 2010-06-07..2019-04-30. The lead rules on them.

Boundaries: no price or market data. CalendarProbe builds energy 2012 and the release calendars;
CalendarBuilder-Commod builds energy and metals; do not build those. No code edits. Stop rule: finish all four
files, or return with what is done if a budget notice stops you; equity comes first whatever happens.
