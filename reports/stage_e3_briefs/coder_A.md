# Brief: MemberCoder-A-OpusXHigh (Stage E.3, Task 2)

Read reports/stage_e3_briefs/coder_common.md first. It governs, together with the specs.

Objective: code K2-cp1-01, K2-cp2-01, K2-cp3-01 and K2-monthend-01 (specs sections 1, 2, 3 and 8) with
their tests.

Your files (only these):
- strategy/members/k2/cp1.py, cp2.py, cp3.py, monthend.py
- strategy/members/k2/_month_end.py: the literal month-end table (S0.11, L-16), as a tuple of
  ("YYYY-MM", "N-1 date", "N date") ISO strings for every calendar month whose N lies inside the rates
  calendar's coverage, plus a constant naming its source. Build it from data.group_session.load_group_calendar("rates")
  (is_trade_date / trade_dates_between; check what the calendar counts as a trade date, halt days
  included, and report it). Generate it with a one-off script you keep at
  reports/stage_e3_briefs/gen_k2_month_end.py (not imported by anything).
- strategy/members/k2/_port_common.py if you want shared helpers for your four modules (optional).
- tests/test_e3_k2_members.py: your members' tests and a pin test that recomputes the month-end table
  from the calendar and asserts equality with _month_end.py.
- reports/stage_e3_coder_A.md (your report).

Points the lead wants pinned by name in your tests:
- CP1: the 17:00 CT Globex-open bar on d-1 missing means no trade (L-05); zero signal means no trade;
  signal bars with two instrument_ids mean no trade; a missing 13:29 bar means no trade (L-04); a missing
  13:58 bar sends the exit on 13:59.
- CP2: the 75-bar hold counted in present bars (L-07), including a missing bar inside the hold; no C-2
  exit; no entry from 14:00; the buffer exactly at 4 ticks (>= and <=); one entry per trade date even
  when the first trigger's intent is refused; no OR bars means no trade.
- CP3: d-1 = the most recent complete daily bar (L-09), an early-halt day d not traded, an incomplete d-1
  skipped, the instrument guard, CLV exactly 0.8 and 0.2, a zero range.
- Month-end: N and N-1 each traded; an early-halt N dropped while N-1 is still traded (L-16); a date not in
  the table not traded; a missing 07:20 bar means no trade.

MemberCoder-B-OpusXHigh codes the four event members in the same directory at the same time. Its files
are aucpre.py, aucpost.py, fomcpost.py, predrift.py, _releases.py, _event_common.py and
tests/test_e3_k2_members_events.py. Do not touch them.
