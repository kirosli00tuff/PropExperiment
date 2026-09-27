# Brief: MemberCoder-B-OpusXHigh (Stage E.4 Part 1, Task 2)

Read reports/stage_e4_briefs/coder_common.md first. It governs, together with the specs
(reports/stage_e4_member_specs.md; section 11 lists the release-check drops and is final).

Objective: code K4-ngpre-01, K4-apipre-01, K4-eiafade-01 and K4-eiamom-01 (specs sections 4, 5, 6 and 7)
with their tests, and the release tables.

Your files (only these):
- strategy/members/k4/ngpre.py (make_ng), apipre.py, eiafade.py, eiamom.py (make_mcl).
- strategy/members/k4/_releases.py: the literal tables (S0.11, K4-L-01, K4-L-02):
  - RELEASE_CALENDAR_SHA256 = 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8 and
    RELEASE_CHECK_SHA256 = the sha256 of reports/stage_e4_release_check.json;
  - WPSR: a tuple of (date ISO, T_W "HH:MM" CT, weekday 0-6, standard bool) for every WPSR row of
    reports/stage_e2b_release_calendar.json, T_W = the row's instant_utc in America/Chicago,
    standard = Wednesday and 10:30 America/New_York; less DROPPED_WPSR;
  - NGS: a tuple of (date ISO, T_N "HH:MM" CT) for every NGS row, less DROPPED_NGS;
  - DROPPED_WPSR, DROPPED_NGS: tuples of (date, reason) exactly as specs section 11 lists them;
  - API_DROPPED_WEEKS: tuple of WPSR dates whose standard week section 11 drops for apipre (K4-L-04);
  - FEDERAL_MONDAY_HOLIDAYS: tuple of ISO dates from reports/stage_e4_release_check.json key
    "federal_monday_holidays" (2019-05-01..2026-06-19);
  - NYSE_NOT_FULL: tuple of ISO dates, every NYSE full closure and early close in the release check's
    "nyse" lists (both windows);
  - the calendar-verification labels, for the return: NGS_UNVERIFIED_IN_WINDOW (dates section 11 keeps
    with the label "unverifiable").
  Generate it with a one-off script kept at reports/stage_e4_briefs/gen_k4_releases.py (not imported by
  anything; it reads the JSON files with short scripts and never prints them whole).
- strategy/members/k4/_event_common.py, if you want shared helpers for your four modules (optional).
- tests/test_e4_k4_members_b.py (more files allowed, each starting tests/test_e4_k4_members_b): your
  members' tests, and a pin test that checks both source files' sha256 and recomputes every table from
  them (WPSR and NGS = calendar rows minus the drops; the drops equal section 11's list as recorded in the
  release check JSON; the holiday and NYSE lists equal the JSON's).
- reports/stage_e4_coder_B.md (your report).

apipre imports ENERGY_FULL_SESSIONS from strategy/members/k4/_calendar.py, written by MemberCoder-A
(a tuple of ISO date strings). Do not edit that file; if it is not there yet when you need it, write the
rest first.

Points the lead wants pinned by name in your tests:
- ngpre: standard Thursday (T 09:30 CT: entry decision 07:59, fill 08:00, exit decision 09:59, fill 10:00);
  a Wednesday 12:00 ET release (T 11:00 CT: entry decision 09:29, fill 09:30, exit decision 11:29, fill
  11:30); a Friday 10:30 ET release (T 09:30 CT); side SELL; a dropped release and a non-table date not
  traded; an early-halt date not traded; a missing entry bar means no trade; a missing T+29 bar sends the
  exit on the next present bar; the fill guard at T does not touch the T-90 or T+30 fills.
- apipre: R_API from the Tuesday 15:24 and 15:39 closes (CT date W-1, after F and after the 13:30
  settlement); R_API = 0 no trade; the two signal bars or the Wednesday 07:29 bar with another
  instrument_id: no trade; entry decision 07:29, fill 07:30; exit decision 09:28, fill 09:29, before the
  09:30 release; a non-standard week (Thursday 12:00 ET WPSR) not traded; a Monday federal holiday week not
  traded; a Tuesday that is not in ENERGY_FULL_SESSIONS not traded; the Wednesday with an early halt not
  traded; a missing 07:29 bar means no trade.
- eiafade: M at exactly -0.005 buys and exactly +0.005 sells (exact integer comparison, K4-L-05), just inside
  either threshold no trade; C10 (close of T_W-1 <= 0: no trade); the 09:30, 10:00 and 11:00 CT slots
  (entry fills 09:45, 10:15, 11:15; exit first bar at or after 13:28); the 16:00 CT row (2025-12-29) not
  traded (T_W + 15 > 13:13); the two signal bars with two instrument_ids: no trade; early halt: no trade.
- eiamom: r3 from the 09:29 and 09:59 closes; r3 = 0 no trade; entry decision 14:29, fill 14:30; exit first
  bar at or after 14:58; a date in NYSE_NOT_FULL not traded; a non-standard WPSR (Thursday) not traded; an
  early-halt date not traded; the guard over 09:29, 09:59 and 14:29.
- All four: D9.7 (an engine-forced exit: no duplicate exit, no re-entry that trade date).

MemberCoder-A-OpusXHigh codes cp1.py, cp2.py, cp3.py, ovr.py, _calendar.py, _port_common.py and
tests/test_e4_k4_members_a*.py in the same directory at the same time. Do not touch them.
