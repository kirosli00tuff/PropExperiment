# Stage E.8 Task 2, coder B report (MemberCoder-B-OpusXHigh)

Saved by the lead (2026-10-01 00:53 PDT) from the coder's final message: the harness refused the coder's own write of this
file, and the brief told it to return the full text instead. Content as the coder returned it.

Summary: all code, tables and tests written; 158 tests pass (brief's command); 104 mutants, 99 killed, 5 equivalent; no
questions raised. Choices for the lead's review (no rule changed): (1) full-session sets built as trade dates less a 15-row
not-full list with reasons, not a 1780-date literal; (2) DROPPED_LIMIT_DATES has an explicit empty "HE" entry; (3) both
WASDE members check `is_wasde_date`, which reads the drop table at call time; (4) a bar's open is read through
`asdict(bar)["open"]` because the static check bans the name `open` (precedent R-T2-1).

## 1. Files and sha256

| File | sha256 |
|---|---|
| reports/stage_e8_briefs/gen_k6_tables.py | 1aa4d3695373f28602cb0aa133014a1281b6eab925e4f3afda66c102c4963af6 |
| strategy/members/k6/_calendar.py | 1d143c605dfaf6187619a0be1c8fa0c45446dfe9946e628db7628f8f441cc123 |
| strategy/members/k6/_wasde.py | d8f8e32407d45d9d0a6eb96b262b417b80d3476cea26c7a532f0279777be9332 |
| strategy/members/k6/_limits.py | aa2dee3dd9df8ea83cf9a2b5444be55758e862d4bbd4500fb88d6fab3fc8629c |
| strategy/members/k6/_event_common.py | 31e3fbf4dadc27e082b440ee1283f20d09bf134d2de327967156d8b09acb5cc4 |
| strategy/members/k6/limitcont.py | 9b142644bc4f429089a5524851ecc52c2f109ac8e5e0e3004e2a459a88507c97 |
| strategy/members/k6/wasdepre.py | 4708688aac9e3d4051454a6aa884f15d91b512fa5aa752b6e83d21c46f270849 |
| strategy/members/k6/wasdepost.py | 75f6704db77bbbe449f801b5cabe8548e40c69e406fc5f2ea974f813764bd4d2 |
| tests/test_k6_members_tables.py (23 tests) | 4a58cef6e01ca1ebb50d6d5b0d1ce9c07144dedb0a434168b694197027594720 |
| tests/test_k6_members_limitcont.py (55 tests) | e95d5658719e50b4068feb90201aec7e3f74a73478493988485d1def459b9fc3 |
| tests/test_k6_members_wasde.py (33 tests) | 7be91fdec79768c135812118e62ec0151b7daabf79339b50b42c6bd1944ce518 |

strategy/members/k6/__init__.py untouched (0 bytes). No coder A file touched.

## 2. Table sources (each module records them in SOURCE_SHA256)

| Module | Source | sha256 |
|---|---|---|
| _calendar | data/calendars/__init__.py | a13255d8... |
| _calendar | data/calendars/grains.py | a685731b... |
| _calendar | data/calendars/livestock.py | 57727e68... |
| _calendar | rules/sessions.py | beb9501d... |
| _wasde | reports/stage_e2b_release_calendar.json | 839f2437... (= the spec header) |
| _wasde, _limits | reports/stage_e8_release_check.json | 99547c14... |
| _limits | rules/price_limits.py | b9031e13... |

- Trade dates: 1795 per group, ending 2026-06-18; the spec's 13 research-window closures match.
- Engine F: equal across ZC, ZW, ZS, ZM, ZL and across HE, LE on every trade date.
- Early-halt test vs F test: disagree only on 2024-07-03 (no CME halt, F 11:30); the module comment names it.
- Research-window not-full dates: 2025-11-28 and 2025-12-24 in both groups. Grain late opens 2025-12-26 and 2026-01-02 stay
  full sessions. Each group: 1780 full sessions; 14 livestock early halts in the coverage.
- WASDE: 85 rows, all 12:00 ET; 14 in the research window; 2025-10-09 and 2025-11-10 absent, 2025-11-14 present;
  DROPPED_WASDE empty (R-1b-1).
- Limits: 11 HE and 10 LE periods; HE 160 ticks, 190 from 2025-09-02; LE 260, 290 from 2025-06-02; every amount a whole
  number of vendor ticks. DROPPED_LIMIT_DATES: the 14 LE dates 2026-06-01..06-18 (R-1b-2), equal to Task 1b's B1 differing
  dates; "HE" present and empty.
- Settlement window 12:59:30-13:00:00 CT.

## 3. Implementation notes

- limitcont's settlement proxy re-implements the engine's exactly: closes read as `Decimal(repr(close))`; S = the
  volume-weighted close of bars opening in [window start floored to the minute, window end) with volume > 0; else the last
  close before the window end; else undefined. On an early-halt date the window moves to end at the halt (when the halt is
  at or before 13:00).
- Every bar S uses must carry c. Equalities are exact, on the Decimals' integer ratios (`fractions` is not an allowed
  import).
- The d-2 guard uses L(d-2); the drop test reads d-1 and d-2 only.
- The member keeps proxy inputs for at most the three previous seen dates.
- `previous_trade_date` is a manual binary search (`bisect` is not an allowed import).

## 4. What the tests pin

- Tables: every table recomputed from its sources independently of the generator; each module equals the generator output.
- limitcont's settlement window equals `settlement_window_ct` for HE and LE on all 1795 livestock trade dates (14 move for
  halts); `limit_ticks` equals `limit_period` on every livestock trade date.
- limitcont (direct calls): the proxy equals `settlement_proxy` on a regular day, with the 12:59 bar missing, with zero
  volume, on 2025-12-24 (12:15 halt), with no bar before the window end, and on a multi-bar window; limit-up buys and
  limit-down sells; one tick short or over in either direction does not trade; the d-2 guard blocks both directions; the
  HE 2025-09-02 boundary (each date reads its own period); the R-1b-2 drops (a dropped d-1 or d-2 blocks, a dropped d-3 or
  another root's drop does not); every instrument_id check on c; missing 08:30 or 08:44 bars; d-3 or d-1 not seen;
  2025-11-28 or 2025-12-24 as d; an early-halt d-1 read at its 12:14 bar; exits at or after 12:58 closing the whole
  position.
- limitcont through the real engine with D9.7 live: entry fills 08:45 and exit 12:59; a price at the stop level forces
  `price_limit_exit` at 09:01 and the member sends nothing more that day; a price already beyond the stop gets the 08:44
  intent refused as `price_limit_zone_no_entry` and the member does not retry.
- WASDE members: real WASDE dates and the moved or cancelled 2025 ones; monkeypatched drops and full-session set; the signal
  fields (opens set so reading the wrong field flips the direction); zero signal; missing bars; the instrument guard;
  per-day reset; exits. Engine runs with an 11:00 CT release: wasdepre fills 10:30 and exits 11:15, or 11:16 when the 11:14
  bar is missing; wasdepost fills 11:15 and exits 13:14, or 13:15 when the 13:13 bar is missing; neither sends an intent
  at 11:00 or 11:01.

## 5. Commands

- `uv run python reports/stage_e8_briefs/gen_k6_tables.py` (wrote 753, 69 and 93 lines).
- `uv run pytest -q tests/test_k6_members_tables.py tests/test_k6_members_limitcont.py tests/test_k6_members_wasde.py
  tests/test_stage_e_template.py tests/test_stage_e_freeze.py` with PYTHONPYCACHEPREFIX unset: 158 passed.
- ruff clean; `check_member_source(..., "K6")`: 0 problems.
- Mutants: scratchpad coderB/mutate.py (results coderB/mutants.json), run in a scratch rsync copy (no .git, .venv or data),
  304 s at nice 10; the copy deleted afterwards.

## 6. Equivalent mutants (5)

- LC11 (`halt > end` -> `>=`): a halt at exactly 13:00 gives the same window.
- LC20 (window start not floored): on a 30-second window the weighted branch and the fallback pick the same bar and id.
- LC42 (drop `c is None or`): comparing an id to None is already true.
- LC45 (entry flag never set): one 08:44 bar per date.
- PR13 (`drift > 0` -> `>=`): zero has already returned.

## 7. Mutant table (K = killed, with the number of failing tests; EQ = equivalent)

limitcont: LC01 entry 08:44->08:43 K26; LC02 ->08:45 K26; LC03 exit C-2->C-1 K8; LC04 ->C-3 K8; LC05 window end
13:00->12:59 K2; LC06 window start 08:30->08:31 K2; LC07 history 3->1 dates K23; LC08 exposures drop LE K29; LC09 c's bar
08:30->08:31 K4; LC10 early-halt window ignored K2; LC11 EQ; LC12 halt window end ->13:00 K2; LC13 halt window start not
moved K2; LC14 window end inclusive K12; LC15 lo exclusive K1; LC16 zero-volume bars weighted K1; LC17 close as binary float
K7; LC18 VWAP denominator K28; LC19 fallback first bar K5; LC20 EQ; LC21 VWAP bars' ids not recorded K26; LC22 fallback id
lost K3; LC23 period first date exclusive K6; LC24 last date exclusive K6; LC25 amount not scaled K34; LC26 equality ->
`>=` K24; LC27 within one tick K9; LC28 drop test d-1 only K1; LC29 drop test also d-3 K1; LC30 no drop test K2; LC31 no
guard on S's bars K5; LC32 L(d) for L(d-1) K1; LC33 L(d-1) for L(d-2) K1; LC34 no expanded-limit guard K6; LC35 guard up
side only K2; LC36 up->SELL K19; LC37 down->BUY K2; LC38 no limit-down K2; LC39 no full-session test K2; LC40 no pending
test K1; LC41 no guard on the 08:44 bar K1; LC42 EQ; LC43 c not reset K1; LC44 entry flag not reset K23; LC45 EQ; LC46 d-k
by calendar day K3; LC47 exit at the entry bar K6.

wasdepre: PR01 08:30->08:31 K4; PR02 entry 10:29->10:28 K12; PR03 ->10:30 K12; PR04 exit 11:14->11:13 K4; PR05 ->11:15
K4; PR06 window (08:30, 08:31) end K2; PR07 window end 11:16->11:15 K2; PR08 window start 10:29->10:30 K2; PR09 08:30
open->close K3; PR10 10:29 close->open K2; PR11 no zero test K1; PR12 direction reversed K11; PR13 EQ; PR14 no WASDE test
K3; PR15 no full-session test K1; PR16 drops not read at call time K1; PR17 no instrument guard K2; PR18 08:30 record not
reset K1; PR19 no pending test K2; PR20 exposures drop ZS K7.

wasdepost: PO01 10:59->10:58 K5; PO02 ->11:00 K5; PO03 entry 11:14->11:13 K9; PO04 ->11:15 K9; PO05 exit 13:13->13:12 K2;
PO06 ->13:14 K2; PO07 window start 10:59->11:00 K1; PO08 window end 13:15->13:14 K1; PO09 10:59 close->open K2; PO10 11:14
close->open K2; PO11 no zero test K1; PO12 direction reversed K8; PO13 no WASDE test K2; PO14 no full-session test K1;
PO15 no instrument guard K2; PO16 10:59 record not reset K1; PO17 no pending test K1.

_event_common: EC01 named bars in UTC K54; EC02 exit one bar late K12; EC03 pending-exit test inverted K4; EC04 exit side
reversed K14; EC05 exit size 1 K1; EC06 C-2->C+2 K9; EC07 exposure test inverted K73; EC08 round->int K1; EC09 bar_open
reads the close K3.

Tables: TB01 a grain trade date removed K17; TB02 a grain not-full date removed K2; TB03 livestock halt 12:15->12:05 K7;
TB04 previous_trade_date returns d K25; TB05 before the first date K2; TB06 a WASDE date moved K17; TB07 is_wasde_date
ignores drops K4; TB08 HE 0.0475->0.0500 K5; TB09 HE start 09-02->09-03 K5; TB10 a dropped LE date removed K2; TB11
settlement window start 12:59:30->12:59:00 K4.
