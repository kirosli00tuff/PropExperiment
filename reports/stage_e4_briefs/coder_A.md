# Brief: MemberCoder-A-OpusXHigh (Stage E.4 Part 1, Task 2)

Read reports/stage_e4_briefs/coder_common.md first. It governs, together with the specs
(reports/stage_e4_member_specs.md).

Objective: code K4-cp1-01, K4-cp2-01, K4-cp3-01 and K4-ovr-01 (specs sections 1, 2, 3 and 8) with their
tests, and the EC-CAL literal table.

Your files (only these):
- strategy/members/k4/cp1.py, cp2.py, cp3.py, ovr.py (factories make_mcl and make_ng in each).
- strategy/members/k4/_calendar.py: ENERGY_FULL_SESSIONS, a tuple of ISO date strings of every EC-CAL
  energy trade date 2019-04-01..2026-06-30 whose early_halt_ct is None, built from
  data.group_session.load_group_calendar("energy") (is_trade_date, trade_dates_between, early_halt_ct),
  plus a constant naming its source (module and the sha256 of data/calendars/energy.py). Generate it with
  a one-off script kept at reports/stage_e4_briefs/gen_k4_calendar.py (not imported by anything).
  MemberCoder-B's apipre imports ENERGY_FULL_SESSIONS from it: write this file FIRST (within your first
  few minutes) and keep its name and format stable.
- strategy/members/k4/_port_common.py if you want shared helpers for your modules (optional).
- tests/test_e4_k4_members_a.py (more files allowed, each starting tests/test_e4_k4_members_a): your
  members' tests and a pin test that recomputes ENERGY_FULL_SESSIONS from the calendar and asserts
  equality.
- reports/stage_e4_coder_A.md (your report).

Points the lead wants pinned by name in your tests:
- CP1: 08:29 and the 17:00 CT Globex-open bar on d-1 are the signal bars; the 17:00 bar missing means no
  trade (E.3-L-05); zero signal means no trade; two instrument_ids mean no trade; a missing 12:59 bar means
  no trade (E.3-L-04); a missing 13:28 bar sends the exit on 13:29; q_c = 4 on MCL and 1 on NG.
- CP2: OR from [08:00, 08:15); the buffer is 0.04 on MCL and 0.004 on NG (K4-L-06: assert these literals
  equal 4 x vendor_tick); the buffer exactly at 4 ticks (>= and <=); the 75-bar hold in present bars
  including a missing bar inside the hold; no C-2 exit; no entry from 13:30; one entry per trade date even
  when the first trigger's intent is refused; no OR bars means no trade.
- CP3: [08:00, 13:30) daily bar with C_d = close of the 13:29 bar; d-1 = the most recent complete daily bar;
  an early-halt day d not traded; an incomplete d-1 skipped; the instrument guard; CLV exactly 0.8 and 0.2;
  a zero range; entry on the 08:00 bar, exit first bar at or after 13:28.
- ovr: the five decision times and their fill minutes; r(t) from the t-60 open and the t-1 close; the 20
  reference dates from ENERGY_FULL_SESSIONS (a roll-blackout date counts; an early-halt date does not; a
  full-session date with missing bars occupies a slot and contributes fewer values: K4-L-08); fewer than 80
  values means no trade at t; the warm-up (K4-L-09: no trade until all 20 reference dates are on or after
  the first trade date seen); numpy.percentile(..., method="linear") on floats; r <= P10 buys, r >= P90
  sells, the tie P10 = P90 = r does not trade (K4-L-10); C10 (open of t-60 <= 0: no trade at t, and such a
  reference value is not counted); the t+58 exit and the missing-exit-bar case; no overlap (an entry at
  t+60 only when flat with no pending order); an early-halt day d not traded; D9.7 (an engine-forced exit:
  no duplicate exit, no re-entry at that decision time, later decision times still trade).

MemberCoder-B-OpusXHigh codes ngpre.py, apipre.py, eiafade.py, eiamom.py, _releases.py, _event_common.py and
tests/test_e4_k4_members_b*.py in the same directory at the same time. Do not touch them.
