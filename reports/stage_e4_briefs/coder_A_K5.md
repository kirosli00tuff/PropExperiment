# Brief: MemberCoder-A-OpusXHigh (Stage E.4 Part 2, K5, Task 2)

Read reports/stage_e4_briefs/coder_common_K5.md first. It governs, together with the specs
(reports/stage_e4b_member_specs.md).

Objective: code K5-cp1-01, K5-cp2-01, K5-cp3-01 and K5-ovr-01 (specs sections 1, 2, 3 and 7) with their tests, and the
EC-CAL literal table.

Your files (only these):
- strategy/members/k5/cp1.py, cp2.py, cp3.py, ovr.py (factories make_mgc and make_mhg in each).
- strategy/members/k5/_calendar.py: METALS_FULL_SESSIONS, a tuple of ISO date strings of every EC-CAL metals trade
  date whose early_halt_ct is None, over the calendar's own coverage (K4-L-13), from
  data.group_session.load_group_calendar("metals"), plus a constant naming its source (module and the sha256 of
  data/calendars/metals.py). Generate it with a one-off script kept at reports/stage_e4_briefs/gen_k5_calendar.py.
- strategy/members/k5/_port_common.py if you want shared helpers (optional).
- tests/test_e4_k5_members_a.py (more files allowed, each starting tests/test_e4_k5_members_a): your members' tests and a
  pin test that recomputes METALS_FULL_SESSIONS from the calendar and asserts equality.
- reports/stage_e4b_coder_A.md (your report).

Points the lead wants pinned by name in your tests:
- CP1 on MGC (signal 17:00 of d-1 to 07:49; entry 11:59/12:00; exit first bar at or after 12:28) and on MHG (07:39;
  11:29/11:30; 11:58); the Globex-open bar missing, zero signal, two instrument_ids: no trade; a missing entry bar: no
  trade; a missing exit bar: the next present bar; q_c 1 on MGC and 2 on MHG.
- CP2: OR [07:20, 07:35) on MGC and [07:10, 07:25) on MHG; buffer 0.40 and 0.0020 (K5-L-07: equal to 4 x vendor_tick);
  buffer exactly at 4 ticks; the 75-bar present-bar hold including a missing bar; no C-2 exit; no entry from C (12:30,
  12:00); one entry per trade date even when the first trigger's intent is refused.
- CP3: the daily bar, d-1 = the most recent complete bar, early-halt day, instrument guard, CLV exactly 0.8 and 0.2,
  zero range, entry on the O bar, exit at C-2, on both roots.
- ovr: MGC's five decision times 08:20..12:20 and MHG's four 08:10..11:10 with their fill minutes; the value floor 80 of
  100 (MGC) and 64 of 80 (MHG); the 20 METALS_FULL_SESSIONS reference dates (a roll-blackout date counts; an early-halt
  date does not; a full-session date with missing bars occupies a slot); fewer than 20 table dates before d: no trade;
  the warm-up (K4-L-09); the tie (K4-L-10); C10 (open <= 0); the t+58 exit and the missing exit bar; no overlap; an
  early-halt day; D9.7. Add a short diff note in your report (k4/ovr.py against k5/ovr.py) so the auditor can confirm
  F-7: the two differ only in the clock, the calendar table and the value floor.

MemberCoder-B-OpusXHigh codes preauc.py, pmfix.py, fomc.py, _releases.py, _event_common.py and tests/test_e4_k5_members_b*.py
in the same directory at the same time. Do not touch them.
