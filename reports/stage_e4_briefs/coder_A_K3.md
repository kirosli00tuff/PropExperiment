# Brief: MemberCoder-A-OpusXHigh (Stage E.4 Part 3, K3, Task 2)

Read reports/stage_e4_briefs/coder_common_K3.md first. It governs, together with the specs
(reports/stage_e4c_member_specs.md).

Objective: code K3-cp1-01, K3-cp2-01 and K3-cp3-01 (specs sections 1-3) on all seven roots, with their tests. When you have
finished, report to the lead: K3-mehedge-01 goes to whichever coder finishes first (the prompt), and the lead will send it
to you with a short brief if you are first.

Your files (only these):
- strategy/members/k3/cp1.py, cp2.py, cp3.py (factories make_6e, make_6a, make_6b, make_6c, make_6j, make_6s, make_6n).
- strategy/members/k3/_port_common.py if you want shared helpers (optional).
- tests/test_e4_k3_members_a.py (more files allowed, each starting tests/test_e4_k3_members_a).
- reports/stage_e4c_coder_A.md (your report).

The K3 ports use the same clock as E.3's K2 rates ports (O 07:20, C 14:00): strategy/members/k2/cp1.py, cp2.py, cp3.py and
_port_common.py are the audited pattern; copy them (never import) and change only the roots and names. Points to pin by
name in your tests, on every root where it applies: CP1 (17:00 bar of d-1 to 07:49; entry 13:29/13:30; exit at or after
13:58; the missing Globex bar, zero signal, two instrument_ids, missing entry bar, missing exit bar); CP2 (OR [07:20,
07:35) with the RANGE_MINUTES = 15 literal pinned and a sell-side pair so that a 14-minute range fails; the buffers 0.0002,
0.0004 on 6B and 0.000002 on 6J equal to 4 x vendor_tick; exactly at 4 ticks; the 75-bar present-bar hold; no C-2 exit; no
entry from 14:00; one entry per trade date); CP3 (daily bar [07:20, 14:00), d-1 complete, early-halt day, guard, CLV 0.8 and
0.2, zero range); q_c 1 on all seven; D9.7 (test-only forced exit, as K4/K5).

MemberCoder-B-OpusXHigh codes ldnrev.py, ldnmom.py, ecbfix.py, tkypre.py, tkypost.py, _calendar.py, _clocks.py,
_event_common.py and tests/test_e4_k3_members_b*.py in the same directory. Do not touch them.
