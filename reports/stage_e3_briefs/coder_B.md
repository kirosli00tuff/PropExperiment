# Brief: MemberCoder-B-OpusXHigh (Stage E.3, Task 2)

Read reports/stage_e3_briefs/coder_common.md first. It governs, together with the specs.

Objective: code K2-aucpre-01, K2-aucpost-01, K2-fomcpost-01 and K2-predrift-01 (specs sections 4, 5, 6
and 7) with their tests.

Your files (only these):
- strategy/members/k2/aucpre.py, aucpost.py, fomcpost.py, predrift.py
- strategy/members/k2/_releases.py: the literal release tables (S0.11, L-01, L-02, L-14, L-15):
  - RELEASE_CALENDAR_SHA256 = the frozen release calendar's sha256 (839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8);
  - TREASURY_AUCTIONS: a tuple of (auction date ISO, tenor "2Y"|"5Y"|"10Y"|"30Y", T_a as "HH:MM" CT)
    for every TREASURY_AUCTION row of reports/stage_e2b_release_calendar.json with tenor suffix 2Y, 5Y,
    10Y or 30Y. T_a is the row's instant_utc converted to America/Chicago. Leave out the entries in
    DROPPED_AUCTIONS;
  - DROPPED_AUCTIONS: a tuple of (date, tenor, reason). Start with it EMPTY. The lead fills it from the C9
    XML check (reports/stage_e3_auction_xml_check.json, being produced now by another worker) and sends
    you the list;
  - FOMC_STATEMENT_DATES: every FOMC row's date whose instant is 13:00 CT (L-15);
  - ISM_SERVICES_DATES: every ISM_SERVICES row's date whose instant is 10:00 ET = 09:00 CT (L-15).
  Generate it with a one-off script you keep at reports/stage_e3_briefs/gen_k2_releases.py (not imported by
  anything; it reads the JSON with a short script and never prints the whole file).
- strategy/members/k2/_event_common.py, if you want shared helpers for your four modules (optional).
- tests/test_e3_k2_members_events.py: your members' tests, and a pin test. The pin test checks the
  calendar file's sha256 and recomputes the three tables from it. It then asserts equality, with
  TREASURY_AUCTIONS = calendar rows minus DROPPED_AUCTIONS, and checks that every dropped entry is marked
  "disagree" in reports/stage_e3_auction_xml_check.json.
- reports/stage_e3_coder_B.md (your report).

Tenor map (specs section 4): ZT 2Y, ZF 5Y, ZN 10Y, TN 10Y, ZB 30Y, UB 30Y. predrift trades ZN and ZB only.

Points the lead wants pinned by name in your tests:
- aucpre: a 13:00 ET close (entry decision 08:59, fill 09:00, exit decision 11:58, fill 11:59) and an 11:30
  ET close (07:29 / 07:30 / 10:28 / 10:29), both on the engine's fills; the wrong tenor for the root is not
  traded; an early-halt date is not traded; a missing entry decision bar means no trade; a missing exit
  bar sends the exit on the next bar.
- aucpost: 12:04 / 12:05 entry and 15:04 / 15:05 exit for a 13:00 ET close; 10:34 / 10:35 and 13:34 / 13:35
  for an 11:30 ET close; the engine's fill guard at the auction instant T_a does not touch the T_a + 5 fill.
- fomcpost: 13:29 / 13:30 and 15:04 / 15:05; the release at 13:00 CT and the fill guard [13:00, 13:02)
  leave the fills alone; a non-FOMC date is not traded.
- predrift: s from the 08:30 open and the 08:49 close, in ticks; s = 0 means no trade; the 08:30 and 08:49
  bars with two instrument_ids mean no trade; a missing 08:30 bar means no trade; held through the 09:00
  release, exit fill at 09:05; only ZN and ZB have factories.

MemberCoder-A-OpusXHigh codes CP1, CP2, CP3 and month-end in the same directory at the same time. Its files
are cp1.py, cp2.py, cp3.py, monthend.py, _month_end.py, _port_common.py and tests/test_e3_k2_members.py. Do
not touch them.
