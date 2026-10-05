# Brief: CalendarBuilder-Commod-OpusHigh (Stage E.14 Task 2: energy and metals)

Read reports/stage_e14_briefs/calendar_rules.md first. It binds you. Your pages folder:
reports/stage_e14_briefs/pages/cal_commod/ (CME holiday files go in the shared pages/cme_holiday/; another worker
is saving CME's per-holiday schedules there now; look there before fetching and reuse what is saved).

## Objective
Build the CME group calendars for 2010-06-01..2019-05-31, in schema e14_hist_calendar/1, writing each file when
complete:
1. ENERGY (NYMEX energy: NG, CL and the group in data/calendars/__init__.py) -> reports/stage_e14_cal_energy.json.
   NG is test C1's price path, so this is the most important calendar of C1. A separate probe worker is
   sourcing 2012 alone (reports/stage_e14_probe.md and reports/stage_e14_briefs/probe_energy_2012.json may
   appear while you work); build 2012 yourself anyway (it is an independent check), and note any disagreement
   with the probe's file in your report if it exists by then.
2. METALS (COMEX metals: GC and group) -> reports/stage_e14_cal_metals.json.

For both: every holiday full closure and early halt (with halt time), late opens, unscheduled closures or halts
(Hurricane Sandy 2012-10-29/30; the 2018-12-05 national day of mourning; any CME Globex outage CME announced),
Good Fridays, and every dated change of the regular Globex session hours and of the daily break (for example the
energy and metals 16:15-17:00 CT break and its later change to 16:00-17:00 CT, if and when it happened) as dated
"sessions" rows, with the day session (D6's O and C: energy's 14:30 ET settlement-period close, i.e. 13:30 CT;
metals' own) as CME states it for each period. The data/calendars/energy.py and metals.py docstrings describe
how 2019-2026 differed by period; do not assume the same for 2010-2019.

Also, derived from your energy file (no new source; a short script; record the rule): the list of ENERGY full
sessions in 2010-06-01..2019-05-31 in the format of strategy/members/k4/_calendar.py's ENERGY_FULL_SESSIONS (read
its header lines 1-30 for the rule that defines a "full session"), written as
reports/stage_e14_cal_energy_full_sessions.json with the rule quoted and the count.

Method: start from reports/stage_e2a_calendar_sources_energy.md and _metals.md and the module docstrings (by
grep). Find 2010-2019 captures with the Wayback CDX API (prefix search on
cmegroup.com/tools-information/holiday-calendar/, cmegroup.com/trading-hours/files/, cmegroup.com/globex/ and
CME notices; also NYMEX's own pages nymex.com, which CME ran until about 2010-2012).

Output also reports/stage_e14_cal_commod.md: per group, per year, the documents used, the counts (trade dates,
closures, halts, unsourced, unsourced share over 2010-06-07..2019-04-30), every unsourced or unverified date with
the reason, and every judgment call.

Boundaries: no price or market data. CalendarProbe builds the 2012 energy probe and the release calendars (NGS,
WPSR, FOMC); CalendarBuilder-Equity builds equity, rates, FX and grains; do not build those. No code edits.
Stop rule: finish both group files and the full-sessions file, or return with what is done if a budget notice
stops you; energy comes first whatever happens.
