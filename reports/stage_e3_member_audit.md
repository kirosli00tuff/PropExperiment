# Stage E.3 member audit (MemberAuditor-FableXHigh)

Worker file worker-xhigh, model fable, effort xhigh. Brief: reports/stage_e3_briefs/auditor_task3.md.
I wrote none of the code, specs or tests. Read-only on the repository except this report and the
scripts under reports/stage_e3_briefs/audit/. Synthetic bars only; no bar file read, no runner run, no
freeze written (the freeze script was run with `--dry-run` only), no web, no git change.

# Part 1: fidelity audit (Task 3)

Started 2026-09-27 00:11 PDT. Ended 2026-09-27 00:28 PDT (all times America/Vancouver).

## 0. Files audited (sha256 as seen; `sha256sum -c reports/stage_e3_briefs/k2_files_pre_audit.sha256`: 15 OK at 00:11 and again at 00:24)

| File | sha256 |
|---|---|
| strategy/members/k2/__init__.py (0 bytes) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| strategy/members/k2/_port_common.py | 556b1012c8c6525f70e222f830cc2aa9189b9602e72292230a9192c0186e7211 |
| strategy/members/k2/cp1.py | b1b52eb3dd6c76d501a27286b19a28aec6a0bee392e931509b2a00a88b097002 |
| strategy/members/k2/cp2.py | 4957faafc0a9475d9f4136fc1339754f5502b1f8494ae22d9ba3c7602d7a76f4 |
| strategy/members/k2/cp3.py | 3985d957f593a959ec201fff64442a56db83be1635cb16d7aa99cd86a93386b3 |
| strategy/members/k2/monthend.py | ca801d5a85be2e6854d280fbd2506b6e89cdf2ec523baf27792c8f7cf855561d |
| strategy/members/k2/_month_end.py | b2eb207d1d30e185cc592727890daf2d60be3a60dee0771d882ca58b6fd7ab2a |
| strategy/members/k2/_event_common.py | 5b3b62ee024be329f0f5bda047043f7300d828c2eca93e60b7921e9c77b77f64 |
| strategy/members/k2/_releases.py | a64a041789057a64a1da1fd9ff426b8cafecadbf59b3e6c21ff307ab87cab277 |
| strategy/members/k2/aucpre.py | 1b2d312e9d36b66e4e48762b0e2da19789661fc9ec9274e30266be0d1dcbb688 |
| strategy/members/k2/aucpost.py | 2ad1b5ed20ae3847521286c0df4106bbffaef0400507a3394b13542c6e411086 |
| strategy/members/k2/fomcpost.py | 5130925a72445107f89fcbc5da9fdc9019a22dfec43181d20e44185f0a1e9910 |
| strategy/members/k2/predrift.py | 3d2d362efc1f5ce5d76c5329ad44a81d325acdca6218a1b076f46838772b6378 |
| tests/test_e3_k2_members.py | c1b8e6a3dd99329da6df183e00fea1d3819084805e7628df6eccb8575a107bb3 |
| tests/test_e3_k2_members_events.py | 04351c46d330bc873403b873e33757b7e4df362e6f29823deed49faba1ca88ba |

Frozen sources as read: reports/stage_e2b_release_calendar.json sha256 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8 (matches
_releases.RELEASE_CALENDAR_SHA256); data/calendars/rates.py sha256 449c152977d21dc84721871d970960845bc3e21e603361f5d59e71841ef4df23 (matches
_month_end.MONTH_END_SOURCE_SHA256). strategy/members/__init__.py is 0 bytes. No reports/stage_e_k2_member_freeze.json exists.

## 1. What I did

- Read the frozen entries (catalog K2 lines 27-131, 137-592 with every bracketed note), D6 lines 348-411, D9 lines 478-614, the specs in full, the
  contract (interface.py, _template.py), the engine's grid, masking and step order (stage_e_engine.py 239-262, 584-660), the rules module's
  admit_fill, account_view and call_member (stage_e_rules.py 196-232, 370-470), the MES references (_mechanics.py 1-45, h6 1-50, B-H1 135-182,
  _stylized_facts.py 290-312), both coder reports, both test files in full.
- Recomputed every literal table from its frozen source in my own scripts (reports/stage_e3_briefs/audit/recompute_month_end.py,
  recompute_releases.py, csv_availability.py): all equal. Counts below.
- Ran screening.stage_e_freeze.check_member_source on all 13 files (all pass), probed the `open` ban (`bar.open` -> `banned_name: .open`;
  `asdict(bar)["open"]` passes), ran the freeze script `--dry-run` (44 declarations, S0.2 order; see finding N-1), and the two K2 test files
  (`env -u PYTHONPYCACHEPREFIX nice -n 10 uv run pytest -q`: `145 passed in 20.25s`).
- Ran nine scenarios of my own through the real engine on synthetic bars (reports/stage_e3_briefs/audit/scenarios.py), covering boundaries the
  tests leave open (section 5).

## 2. Verdict

No BLOCKING finding. No SHOULD FIX finding. 12 NOTEs (section 6). Every module implements its frozen entry and nothing more; every lead reading
L-01..L-23 is either the narrowest the text allows or fixed by the cited reference; I take the same reading in every case.

## 3. Per-member checklists (brief items 1-11; "ok" = implemented as frozen, evidence file:line)

Common plumbing (all eight): O and C from `load_frozen_tables().day_session_ct` (_port_common.py:60-62; the event members use literal clock
times, which the entries state as literals); q_c from the frozen vehicle table (_port_common.py:62; _event_common.py:130; predrift.py:77; all six
= 1, checked); integer vendor ticks `round(Decimal(repr(price)) / vendor_tick)` (_port_common.py:80-82; _event_common.py:67-69; the engine
hands Python floats, stage_e_rules.py:222, and rejects off-grid prices and off-minute timestamps, lines 196-204); a None bar is no decision
(every on_minute's first lines); no hindsight field is read anywhere (grep: the only Bar fields read are ts_event_ns, trade_date, open via
asdict, high, low, close, instrument_id, early_halt_ct; the only account fields are positions and pending).

### K2-cp1-01 (cp1.py; catalog 137-181; D6 line 364)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Literals: first bar 17:00 CT on d-1; O+29 = 07:49; C-31 = 13:29; C-2 = 13:58 | ok | cp1.py:47-50, 81-83 (offsets from the frozen O and C) |
| 2 | Direction: sign(close 07:49 - open 17:00) in ticks; buy > 0, sell < 0; 0 no trade | ok | cp1.py:101-104, 123-124, 119 |
| 3 | Exit: first present bar at or after 13:58, next open; resent while refused | ok | cp1.py:116-117; _port_common.py:89-101 |
| 4 | Sizing q_c; exit closes abs(position) | ok | cp1.py:132; _port_common.py:100-101 |
| 5 | Event set | n/a (none) | |
| 6 | Availability: 07:49 bar used at 13:29; 17:00 bar's open read at its close; no future bar | ok | cp1.py:118-125 (each recorded on its own bar) |
| 7 | C4: none (port follows D6); guard = the two signal bars share one instrument_id | ok | cp1.py:99-100; no halt test (C 49-50) |
| 8 | Flatten/floor: last fill 13:59 nominal; F backstop; one entry/day; hold 29 min; windows S0.12 | ok | cp1.py:85-89, 126-128 |
| 9 | Nothing more | ok | the `is_flat` gate at 126 is unreachable-as-filter (a position can only come from this member) |
| 10 | Factories, name, leg; static check | ok | cp1.py:79-80, 135-156; dry-run ordinals 1-6 |
| 11 | Tests pin the cases | ok | tests A 286-371: signal pair vs the other pairings (273-276), L-05, L-06 (entry bar unguarded), L-04, missing exit bar, refused exit resent (min-hold), D9.5a, synthetic F, early halt left to the engine (2021-05-31), one trade/day |

### K2-cp2-01 (cp2.py; catalog 183-227; D6 line 365 amended)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Literals: OR [O, O+15); buffer 4 vendor ticks; hold 75; eligible [O+15, C) | ok | cp2.py:48-50, 74, 105, 111, 114-116 |
| 2 | Direction: close >= OR_high + 4 buys; <= OR_low - 4 sells; first qualifying bar | ok | cp2.py:113-121 |
| 3 | Exit: 75 present bars with the position open, from the bar after the decision bar (B-H1 146-152); no C-2 exit; F if earlier | ok | cp2.py:81-90, 99-100; no C-2 code path; test A 407-420 |
| 4 | Sizing q_c; exit abs(position) | ok | cp2.py:90, 121 |
| 5 | Event set | n/a | |
| 6 | Availability: range from closed bars; trigger on the bar's own close | ok | cp2.py:105-108, 113 |
| 7 | C4: none (port); no instrument guard, no halt test (D6, B-H1 have none) | ok | cp2.py docstring 6-7, 18; code has none |
| 8 | Flatten/floor: entries stop at C; F flatten; one entry/day; window (07:20, 15:08) | ok | cp2.py:111, 120, 76 |
| 9 | Nothing more | ok | |
| 10 | Factories, name, leg; static check | ok | cp2.py:72-73, 124-145; ordinals 7-12 |
| 11 | Tests | ok | tests A 388-458: 75 bars fill to fill, 3 vs 4 ticks both sides, missing bar inside the hold (L-07), no C-2 exit, no entry from 14:00, 13:59 entry flattened at real F 15:08, one entry even when refused (L-08), no OR bar, present-bar range, pre-O and evening bars excluded, deferred fill starts the count, reset |

### K2-cp3-01 (cp3.py; catalog 229-266; D6 line 366; Family H by reference)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Literals: daily bar [O, C) on CT date d; C_d = close at C-1; cuts 0.8/0.2; lookback 1; exit C-2 | ok | cp3.py:54-58, 114-115, 141-149 |
| 2 | Direction: Range > 0; CLV >= 0.8 buy, <= 0.2 sell, non-strict; exact integer cross-products (4/5, 1/5) | ok | cp3.py:72-85; equals H6's float test on every exact ratio (h6 lines 33-41) |
| 3 | Exit: first present bar at or after 13:58; resent | ok | cp3.py:176-177 |
| 4 | Sizing | ok | cp3.py:184 |
| 5 | Event set | n/a | |
| 6 | Availability: d-1 finalised on the first bar of a later trade date; day d's own bar never enters day d | ok | cp3.py:130-136, 168-169 (Family H, _mechanics.py 12-13) |
| 7 | Family H rules: complete day (07:20 and 13:59 bars, no halt on CT date d, one instrument_id over [O, C)); d-1 = most recent complete; halt day d not traded; guard 1 bar vs the 07:20 bar; warm-up no trade | ok | cp3.py:120-128, 138-149, 151-160 |
| 8 | Flatten/floor: last fill 13:59; one entry/day; window (07:20, 14:00) | ok | cp3.py:117, 178-180 |
| 9 | Nothing more (O_d not read: no H6 condition uses it; see N-7) | ok | |
| 10 | Factories, name, leg; static check | ok | cp3.py:112-113, 187-208; ordinals 13-18 |
| 11 | Tests | ok | tests A 475-561: 0.8 buys / 0.2 sells / between no trade, 13 exact-cut cases, zero range, d-1 only after finalisation, most-recent-complete (L-09), two ids incomplete, guard, missing 07:20, halt day (2021-05-31) not traded and incomplete, missing exit bar, D9.5a, synthetic F; `daily()` puts extreme bars at 07:10 and 14:30 in every case so a wrong window would flip the CLV |

### K2-aucpre-01 (aucpre.py, _event_common.py, _releases.py; catalog 268-349)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Literals: entry bar T_a - 181; exit T_a - 2; T_a = closing_time_comp (ET) - 1 h in CT | ok | aucpre.py:34-35; _event_common.py:78-84; _releases.py rows |
| 2 | Direction: SELL unconditional | ok | aucpre.py:33; _event_common.py:153 |
| 3 | Exit: first present bar at or after T_a - 2; resent | ok | _event_common.py:92-104, 146-147 |
| 4 | Sizing | ok | _event_common.py:130, 153 |
| 5 | Event set: 340 rows = calendar TREASURY_AUCTION rows of tenor 2Y/5Y/10Y/30Y (2Y 84, 5Y 83, 10Y 87, 30Y 86); tenor map ZT 2Y, ZF 5Y, ZN/TN 10Y, ZB/UB 30Y; T_a 12:00 (317), 10:30 (22), 09:00 (1: 2019-12-24 5Y); DROPPED empty = XML check 340/340 agree; no (date, tenor) twice; coverage 2019-05-08..2026-06-11 | ok | _event_common.py:43; my recompute equal; XML check .md counts table |
| 6 | Availability: every retained record announced >= 4 calendar days before its auction (saved FiscalData CSV, announcement fields only; the one same-day record, 2019-06-21 10Y 11:00 AM, is excluded and absent from the table); halt read from the entry bar; no results field anywhere | ok | audit/csv_availability.py: 340 retained, csv set == table |
| 7 | C4: halt on the entry bar -> no entry; missing entry bar -> no entry (exact instant); instrument guard on the bars read at or before the decision = the entry bar only; roll blackout by the runner (stage_e_runner.py 313-315 passes the blackout union to StageERules) | ok | _event_common.py:148-152 |
| 8 | Flatten/floor: latest fill 11:59; F backstop; one entry/day; hold 179; window (07:29, 12:00) | ok | aucpre.py:36-37, 52 |
| 9 | Nothing more | ok | |
| 10 | Factories, name, leg; static check | ok | aucpre.py:49-51, 61-82; ordinals 19-24 |
| 11 | Tests | ok | tests B 377-462: 13:00 ET close (08:59/09:00 -> 11:58/11:59), 11:30 ET close, two-auction date per tenor, wrong tenor, each event once, real 2019-12-24 halt with the counterfactual 05:59/06:00, missing entry bar, missing exit bar (one and three), fill guard at T_a and a 07:30 release, synthetic F |

### K2-aucpost-01 (aucpost.py; catalog 351-403)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Literals: entry T_a + 4; exit T_a + 184 (fills T_a + 185) | ok | aucpost.py:34-35 |
| 2 | Direction: BUY unconditional | ok | aucpost.py:33 |
| 3 | Exit: the bar at T_a + 184, or the first later bar; F if earlier | ok | _event_common.py:92-104; test B 492-501 |
| 4 | Sizing | ok | _event_common.py:130 |
| 5 | Event set and T_a as aucpre | ok | aucpost.py:53-54 |
| 6 | Availability as aucpre; no results field | ok | |
| 7 | C4 as aucpre | ok | _event_common.py:148-152 |
| 8 | Flatten/floor: last fill 15:05 < F; window (10:34, 15:06) | ok | aucpost.py:36-37 |
| 9 | Nothing more | ok | |
| 10 | Factories etc. | ok | aucpost.py:49-51, 61-82; ordinals 25-30 |
| 11 | Tests | ok | tests B 466-501: 12:04/12:05 -> 15:04/15:05, 11:30 ET variant, fill guard at T_a leaves T_a + 5 alone (D8 cost billed), wrong tenor / missing entry / halt, missing exit bar, missing bars to F -> forced flatten 15:08/15:09 |

### K2-fomcpost-01 (fomcpost.py; catalog 405-463)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Literals: entry bar 13:29 (fill 13:30); exit bar 15:04 (fill 15:05) | ok | fomcpost.py:35-36 |
| 2 | Direction: BUY unconditional | ok | fomcpost.py:34 |
| 3 | Exit: 15:04 or first later bar; F | ok | _event_common.py:92-104 |
| 4 | Sizing | ok | |
| 5 | Event set: 57 FOMC rows, all 13:00 CT (generator filters on 13:00 CT, gen_k2_releases.py 64-67); the cancelled 2020-03-18 meeting and unscheduled meetings are absent from the calendar; research window = the catalog's ten dates; confirmation 37 (catalog "about 38") | ok | my recompute equal; test B 212-224 |
| 6 | Availability: schedule public before each year (catalog C9); halt from the 13:29 bar | ok | |
| 7 | C4 as aucpre | ok | _event_common.py:148-152 |
| 8 | Flatten/floor: last fill 15:05; window (13:29, 15:06) | ok | fomcpost.py:37-38 |
| 9 | Nothing more | ok | |
| 10 | Factories etc. | ok | fomcpost.py:50-52, 62-83; ordinals 31-36 |
| 11 | Tests | ok | tests B 505-535: 13:29/13:30 -> 15:04/15:05 with the 13:00 release guard untouched and no event-window fill, non-FOMC date, missing entry / halt, missing exit bar, missing bars to F |

### K2-predrift-01 (predrift.py; catalog 465-534)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Literals: T = 09:00 CT; signal open at T-30 = 08:30, close at T-11 = 08:49; entry bar 08:49 (fill 08:50); exit bar 09:04 (fill 09:05) | ok | predrift.py:47-50, 81-90 |
| 2 | Direction: s = sign(close 08:49 - open 08:30) in ticks; buy > 0, sell < 0; 0 no trade | ok | predrift.py:111-114 |
| 3 | Exit: 09:04 or first later bar | ok | predrift.py:102-103 |
| 4 | Sizing | ok | predrift.py:77, 114 |
| 5 | Event set: 86 ISM_SERVICES rows, all 10:00 ET (generator filters, gen 69-72); research 15, confirmation 57; the harness calendar lists ISM as concerning ZN and ZB only | ok | my recompute equal |
| 6 | Availability: the 08:30 open is read at that bar's close and used at 08:49; release dates published in advance; the index value is never read (no such field exists in the table) | ok | predrift.py:99-101, 109-111 |
| 7 | C4: 08:30 and 08:49 present with one instrument_id, else no trade; halt on the 08:49 bar; missing entry bar; ZN and ZB only | ok | predrift.py:46, 73, 107-110 |
| 8 | Flatten/floor: hold 15 min (> 2 min, > 10 min mean); window (08:30, 09:06) | ok | predrift.py:51-52, 76 |
| 9 | Nothing more | ok | |
| 10 | Factories make_zn, make_zb only; refuses others | ok | predrift.py:117-122; ordinals 37-38 |
| 11 | Tests | ok | tests B 555-621: the rule's pair vs every other open/close pairing, s = 0, two ids, missing 08:30 or 08:49, held through the 09:00 release (0 deferrals, D8 on the exit), missing exit bar, non-ISM date / halt, synthetic F |

### K2-monthend-01 (monthend.py, _month_end.py; catalog 536-592)

| # | Item | Verdict | Evidence |
|---|---|---|---|
| 1 | Literals: entry bar O = 07:20 (from the frozen table); exit bar 15:04 (fill 15:05) | ok | monthend.py:47, 83 |
| 2 | Direction: BUY unconditional | ok | monthend.py:46, 90 |
| 3 | Exit: 15:04 or first later bar; F | ok | monthend.py:81-82 |
| 4 | Sizing | ok | monthend.py:90 |
| 5 | Event set: 85 months 2019-05..2026-05, N = last EC-CAL trade date of the month, N-1 = the trade date before; 170 dates; June 2026 excluded (N outside coverage 2019-05-01..2026-06-19); 9 dates are early halts (2019-11-28, 2019-11-29, 2020-11-27, 2021-05-31, 2022-05-30, 2024-11-28, 2024-11-29, 2025-11-27, 2025-11-28) | ok | my recompute equal (audit/recompute_month_end.py) |
| 6 | Availability: calendar known in advance; halt from the 07:20 bar | ok | monthend.py:85-86 |
| 7 | C4: halt -> dropped not moved; missing 07:20 bar -> no trade; instrument guard = entry bar only (cannot bind) | ok | monthend.py:83-88 |
| 8 | Flatten/floor: last fill 15:05; window (07:20, 15:06) | ok | monthend.py:70 |
| 9 | Nothing more | ok | |
| 10 | Factories etc. | ok | monthend.py:67-68, 93-114; ordinals 39-44 |
| 11 | Tests | ok | tests A 570-655: N-1 and N traded, neighbours not; halt N dropped and N-1 traded (L-16); missing 07:20; missing 15:04; D9.5a on entry and exit (15:07 < F); synthetic F; L-12; table recomputed independently from EC-CAL and the source sha pinned; 9 halt dates |

## 4. R-T2-1: reading a bar's open as `dataclasses.asdict(bar)["open"]`

Checked: `check_member_source` refuses `bar.open` (`banned_name: .open`) and passes the asdict form. `Bar` is a frozen slots dataclass
(strategy/interface.py:78-79); the engine hands the member either the Bar itself or `dataclasses.replace(bar, ...)` with hindsight fields masked
(stage_e_engine.py:584-587), both dataclass instances, so `asdict` returns a plain dict of the bar's own 16 fields and `["open"]` is the bar's
own open price. It opens no file: `asdict` only walks the instance's fields and deep-copies their values (all atomic here). It is called once per
trade date (cp1.py:119) and once per ISM date (predrift.py:100), so the copy cost is negligible. `getattr`, `vars` and dunder access are banned;
`astuple(bar)[1]` would depend on field order. I see no problem with the ruling; the idiom is the least bad one the frozen check allows (N-2).

## 5. My scenarios beyond the tests (reports/stage_e3_briefs/audit/scenarios.py; all through run_engine, synthetic bars)

1. CP2: a 4-tick close on the 07:34 bar is a range bar (OR_high widens, no entry); on the 07:35 bar it is the entry (fill 07:36, exit 08:51).
2. CP2: a range widened by a late range bar raises the trigger accordingly (entry only on a later B+10 close).
3. CP3: a different instrument_id on a bar after 14:00 and on the evening bars does not make the day incomplete (Family H: RTH bars only); a different id on the 13:59 bar does.
4. CP3: a halt label carried only by the evening bars (the previous CT date's halt) does not exclude day d.
5. Month-end November 2019 (N-1 = 11-28 and N = 11-29 both halts): nothing traded, 11-27 not traded (L-16: dropped, not moved).
6. aucpre ZN on a standard-time date (2025-12-09): fills 09:00 and 11:59 CT (DST handled end to end; the test suite also checks all 340 instants against the harness calendar).
7. predrift uses the 08:30 open (a path where close-to-close has the opposite sign buys as the rule says).
8. CP2 with a synthetic F at 13:30: forced flatten 13:31, and the next day's entry and count start fresh.

## 6. Lead readings L-01..L-23 (brief item 12)

- L-01 literal tables: the only route under the frozen template (no file reads, no calendar in the interface); both tables recompute exactly from their sources, and test B 227-240 ties every member instant to the harness calendar. Agree.
- L-02 C9 XML check: run this stage, 340/340 agree, none unavailable; DROPPED empty is the only reading the result allows. Agree.
- L-03 the bar at hh:mm on CT date d: Family H's reading (_mechanics.py 37-38); every module implements it (ct_open / ct_open_ns). Agree.
- L-04 named entry bars are exact: C4 line 54 sends only exits on a later bar, and D6 says "first bar at or after" only for exits; the narrowest reading. Agree.
- L-05 CP1's first bar = the 17:00 bar on d-1: the catalog names the clock time (C 152-153), and D6's "both signal bars must exist" only has content for a named bar; the wider MES reading (first present bar, _stylized_facts.py 294-305) would trade when the 17:00 bar is missing. Narrowest. Agree (see N-3 on open vs close).
- L-06 CP1's guard is D6's only: C line 49 "The ports follow D6 as written". Agree.
- L-07 CP2's hold fixed by reference: B-H1 lines 146-152 count bars with the position open from the bar after the decision and exit on the 75th; cp2.py matches; no C-2 exit in D6's CP2 text. Agree.
- L-08 CP2's range and trigger: B-H1 157-166 (present bars, no minimum, no guard) and 174-181 (trigger set on emit). Agree.
- L-09 CP3 follows Family H: _mechanics.py 13-15 defines d-1 as the most recent complete daily bar; "as Family H" fixes it by reference, so the "immediately preceding trade date" alternative is excluded. Agree.
- L-10 CP3's exit: D6's "first bar at or after C-2"; Family H's "before the no-new-positions time" clause is the engine's F. Agree.
- L-11 early halt = early_halt_ct: C4's parenthesis defines the test; EARLY_SETTLEMENT_CT days (CME settled early, Globex traded to 16:00) are not early closes of trading and the module says nothing reads it; the engine's F does not move on them either (sessions.day_rule reads EARLY_HALT only). Agree.
- L-12 guard = bars read at or before the entry decision: the only causal reading (a bar after the entry cannot un-trade a date; C4 line 54 governs a missing exit bar); the engine itself raises if an instrument changed while a position is open. Agree.
- L-13 "the entry bar" = the decision bar: C2's usage. Agree.
- L-14 T_a from the calendar instant: verified equal to closing_time_comp - 1 h on all 340 (csv_availability.py), and ET/CT change together. Agree.
- L-15 FOMC/ISM sets by instant: all 57 and 86 rows are at the stated times; the generator filters as stated (gen_k2_releases.py 64-72); no row exercises the filter (N-4). Agree.
- L-16 month-end dates: recomputed equal; halt days are calendar trade dates; "dropped, not moved" is the text's own words (C 578-579) and the narrowest. Agree.
- L-17 trading_windows: code equals S0.12 for all eight; the union for aucpre omits the one 09:00 T_a (N-6). Agree.
- L-18 ordinals: dry-run prints 1..44 in catalog then exposure order. Agree.
- L-19 integer vendor ticks: implemented everywhere; the 0.8 and 0.2 cuts compared as integer cross-products, identical to H6's float test on every exact ratio. Agree.
- L-20 undersized vehicles traded: TRADED_STATUSES = ("chosen", "undersized") (stage_e_frozen.py:55); q_c = 1 for all six. Agree.
- L-21 two test files: both pass (145). Agree.
- L-22 refused exit resent: never opens a position (both exit helpers require a non-zero position and nothing pending against it); the backstop stays the engine's F. Agree.
- L-23 re-keyed reopenings: the CSV shows 2019-11-05 (security_term 3-Year, original 10-Year, reopening Yes) and 2026-01-26 (2-Year, original 5-Year, reopening Yes); the entry keys on original_security_term explicitly, and the frozen research counts (2Y 13, 5Y 15) hold only under that key (a security_term key gives 2Y 14, 5Y 14). Agree; flag stays with the user as the lead wrote.

## 7. Findings

BLOCKING: none. SHOULD FIX: none. NOTE: 12.

- N-1 (NOTE, lead's script) reports/stage_e3_briefs/write_k2_freeze.py fails as documented: `uv run python reports/stage_e3_briefs/write_k2_freeze.py --dry-run` raises `ModuleNotFoundError: No module named 'screening'` because the repository root is not on sys.path when a script under reports/ is run. With `PYTHONPATH=.` it prints the 44 declarations in S0.2 order and exits 0. Smallest fix: run it as `PYTHONPATH=. PYTHONPYCACHEPREFIX=<fresh> uv run python reports/stage_e3_briefs/write_k2_freeze.py`, or add the usual `sys.path.insert(0, ...)` line. No member code involved.
- N-2 (NOTE) cp1.py:54-57 and _event_common.py:72-75 both read a bar's open via `asdict` (R-T2-1), correct in both; two copies of one idiom is cosmetic. A future harness revision could allow the attribute read; nothing to change now.
- N-3 (NOTE, informational for the E.3 return) D6's CP1 text takes the OPEN of the trade date's first bar; MES's F3.3(a) statistic (_stylized_facts.py 294-305) used that bar's CLOSE. The code follows D6, as the port texts govern; the difference is one minute of overnight return and is a property of the frozen text, not of the code.
- N-4 (NOTE, tests) L-15's time filter (FOMC 13:00 CT, ISM 10:00 ET) is not exercised by any calendar row (all rows are at those times), so `test_release_tables_are_recomputed_from_the_calendar` would also pass with the filter removed. The generator's filter is correct by reading (gen_k2_releases.py 64-72). A one-row synthetic test of the generator's `build` would pin it; optional.
- N-5 (NOTE) cp2.py:51 `F_REGULAR_CT = time(15, 8)` is a literal used only as the trading window's end (members cannot import rules.sessions). On early-halt days the window overstates the tradable minutes; the coverage check is per research date and the same is true of every member's fixed window. No trade depends on it.
- N-6 (NOTE, specs) S0.12's aucpre window (07:29, 12:00) is the union over T_a 10:30 and 12:00 only; L-17 says "the union over T_a variants" but the one 09:00 T_a (2019-12-24, window 05:59-12:00 for that date) is left out. Harmless: that date is an early halt (never traded) in the confirmation window, and coverage is measured on the research window. The code matches S0.12.
- N-7 (NOTE) cp3.py does not read O_d (the 07:20 open); D6 defines it in the daily bar but no H6 condition uses it, and the 07:20 bar's presence is still required (cp3.py:146-147, 121). Equivalent to the frozen rule.
- N-8 (NOTE, tests) Behaviours pinned only by my scripts, not by the test files: CP2's 07:34/07:35 boundary, CP3's RTH-only instrument set and evening-halt labels, a month whose N-1 and N are both halts, a standard-time auction date. All behave as frozen (section 5). Optional additions to the tests.
- N-9 (NOTE) _event_common.exit_items (92-104) suppresses an exit only for a pending order opposite to the position; _port_common.exit_if_due (89-101) suppresses on any pending order. The cases differ only for a same-signed pending order with an open position, which no K2 member can produce (one entry per day, none while a position exists). No trade differs.
- N-10 (NOTE, engine and calendar, informational) The harness release calendar lists ISM Services as concerning ZN and ZB only, so K2-aucpre-01's 09:00 CT entry fill on an ISM day is deferred to 09:02 for ZN (and ZB, no tenor match) but not for TN; coder B counted 3 confirmation-window dates (2019-11-05, 2024-11-05, 2025-01-07). This is D9.5a as frozen, not a member matter; recorded for part 2.
- N-11 (NOTE) _releases.FOMC_STATEMENT_DATES starts 2019-05-01, five days before the confirmation window; the runner's window bounds the dates. Harmless.
- N-12 (NOTE) cp2.py resets `_triggered` on a trade-date change (97-98), after which `_hold_exit` is never called; a position surviving into the next trade date would not be exited by the member. That cannot happen under the engine's F flatten (D6: "or the engine's forced flatten at F if earlier"), and the engine raises rather than lets a position span a session end with a locked exit. Documented reliance, not a defect.

Tests that pass vacuously: none found. Every test I read asserts exact fill or intent times, and the coders' mutation probes (their reports, sections 3 and 6) are consistent with what I saw.

## 8. Notes kept for part 2 (recomputation, Task 6)

- Event counts from my recompute: research window 2025-04-01..2026-06-19: 2Y 13 (3 at 10:30 CT), 5Y 15, 10Y 15, 30Y 15, FOMC 10, ISM 15; confirmation 2019-05-06..2024-02-29: 2Y 58 (15 at 10:30), 5Y 56, 10Y 59, 30Y 58, FOMC 37, ISM 57 (before roll-blackout and halt exclusions). Month-end: 170 dates, 9 halts.
- Expected fill minutes per member (CT): cp1 13:30 / 13:59; cp2 next open after the first break / 75 present bars later or F; cp3 07:21 / 13:59; aucpre T_a-180 / T_a-1; aucpost T_a+5 / T_a+185 or F; fomcpost 13:30 / 15:05; predrift 08:50 / 09:05; monthend 07:21 / 15:05. Deviations expected from D9.5a (fills in [release, release+2) move to release+2; aucpre ZN 09:00 -> 09:02 on ISM days) and from missing bars (next present bar).
- My scripts: reports/stage_e3_briefs/audit/{probe_sources,recompute_month_end,recompute_releases,csv_availability,scenarios}.py (probe_sources.py's last lines fail on import path; superseded by recompute_month_end.py).

# Part 2: recomputation (Task 6)

Brief: reports/stage_e3_briefs/auditor_task6.md. Started 2026-09-27 00:51 PDT. Ended 2026-09-27 01:02 PDT.
Read-only except this section and reports/stage_e3_briefs/audit/{item1_screen,replay_two,rebuild_costs,item4_counts}.py,
item1_verdicts.json, trips_K2-cp1-01_ZN.json, trips_K2-aucpost-01_ZN.json. No runner run, no bar file opened by me (item 3's two replays
went through the runner's own loader), nothing written under reports/stage_e3_k2_screen/.

Inputs as seen: 44 member records plus K2_research_cluster.json (cluster file written 00:50 PDT); harness sha256
cf939270f0a00be74aa29a43f0c7de964256411a9cdcebc36f22fd3bdc021a45 (preflight passed in my replay); cluster freeze sha256
8815a775e74996419b57751b1104ffa07cd4b3450eb18a9a92c6cbbd5615b7c5 (44 members, verified); release calendar sha256 839f2437...; frozen
tables costs f4360bb7..., epsilon 4e2c7731..., sizes 280d7e9d..., vehicles 1f1cafee...; ZN research parquet sha256
f4a403f8641c593daac8b8ea42674233c90574181fac3a001d26c4c31e487ee0 (396,178 rows, 1 closure bar), equal in the record and in my replay.

## Summary of verdicts

| Item | Verdict | One line |
|---|---|---|
| 1 Screen figures, 44 records | VERIFIED WITH NOTES (44 of 44) | mean, sd, t and passes reproduce to 1e-9 relative for every record; series shape correct; notes: power check not run (all 44), MLL liquidations in 24 records |
| 2 Tiers | VERIFIED (44 of 44) | all 44 Tier B: none passes, no label, coverage 0.9611..0.9986 (all >= 0.95); floor labels recomputed from trade_rate: none |
| 3 Replay and cost rebuild, 2 trials | VERIFIED (2 of 2) | replayed series equal the records exactly; my own cost rebuild matches every fill and every day (worst relative difference 0) |
| 4 Trade counts and fill minutes | VERIFIED WITH NOTES | every event-member count explained except 7 predrift dates (consistent with s = 0, not checkable from the records); the two replayed trials' fill minutes match the rules, one MLL liquidation aside |
| 5 Program N | VERIFIED | 44 screened, 0 refused, N = 58 + 44 = 102; the 44 records are exactly the freeze's 44 declarations |

## Item 1: the D5 screen recomputed (reports/stage_e3_briefs/audit/item1_screen.py)

Method, in my own code: mean = fmean(values), sd = pstdev(values) (population), t = mean / (sd / sqrt(n)), passes = mean > 0 and t >= 1.0
(D5 lines 302-305; the runner's t is funnel.multiple_comparisons.harvey_liu_zhu_verdict line 124, the same formula). Series shape: the
window's trade dates recomputed from data.group_session.load_group_calendar("rates") over 2025-04-01..2026-06-19 (316 trade dates) less
the record's exclusions (15 roll-blackout dates 2025-05-28..30, 08-27..29, 11-25..27, 2026-02-25..27, 05-27..29; UR-1 2026-06-18/19)
= 299 dates, first 2025-04-01, last 2026-06-17; equal to series.dates in every record (one identical window_dates block across all 44).
Non-zero days = n_trips in every record (one trip per day at most, no zero-net trip); n_days = 299 everywhere; daily_net_usd = values x
the vehicle's tick value on every day (so every trip is one contract, q_c = 1).

| Ord | Member | n_trips | mean ticks/ct/day | daily t | passes | Verdict | Notes |
|---|---|---|---|---|---|---|---|
| 1 | K2-cp1-01 ZT | 264 | -0.580772 | -2.327964 | no | VERIFIED WITH NOTES | power not run |
| 2 | K2-cp1-01 ZF | 275 | -0.314140 | -1.123614 | no | VERIFIED WITH NOTES | power not run |
| 3 | K2-cp1-01 ZN | 276 | -0.473393 | -2.554656 | no | VERIFIED WITH NOTES | power not run; MLL liquidation x1 (accounts started 2) |
| 4 | K2-cp1-01 TN | 270 | -0.890496 | -3.689914 | no | VERIFIED WITH NOTES | power not run; MLL x2 |
| 5 | K2-cp1-01 ZB | 272 | -0.866589 | -5.340199 | no | VERIFIED WITH NOTES | power not run; MLL x4 |
| 6 | K2-cp1-01 UB | 276 | -1.076514 | -5.193316 | no | VERIFIED WITH NOTES | power not run; MLL x4 |
| 7 | K2-cp2-01 ZT | 265 | -0.713846 | -1.365797 | no | VERIFIED WITH NOTES | power not run; MLL x1 |
| 8 | K2-cp2-01 ZF | 283 | -0.212673 | -0.342713 | no | VERIFIED WITH NOTES | power not run |
| 9 | K2-cp2-01 ZN | 278 | -0.976232 | -1.980745 | no | VERIFIED WITH NOTES | power not run; MLL x2 |
| 10 | K2-cp2-01 TN | 286 | -0.798365 | -1.293993 | no | VERIFIED WITH NOTES | power not run; MLL x3 |
| 11 | K2-cp2-01 ZB | 285 | -0.608458 | -1.359407 | no | VERIFIED WITH NOTES | power not run; MLL x5 |
| 12 | K2-cp2-01 UB | 291 | -0.499264 | -0.914781 | no | VERIFIED WITH NOTES | power not run; MLL x5 |
| 13 | K2-cp3-01 ZT | 121 | -0.378649 | -0.428015 | no | VERIFIED WITH NOTES | power not run; MLL x1 |
| 14 | K2-cp3-01 ZF | 127 | -1.197328 | -1.173917 | no | VERIFIED WITH NOTES | power not run; MLL x3 |
| 15 | K2-cp3-01 ZN | 131 | -0.635759 | -0.881876 | no | VERIFIED WITH NOTES | power not run; MLL x3 |
| 16 | K2-cp3-01 TN | 136 | -1.157407 | -1.256501 | no | VERIFIED WITH NOTES | power not run; MLL x5 |
| 17 | K2-cp3-01 ZB | 130 | -1.223253 | -1.784604 | no | VERIFIED WITH NOTES | power not run; MLL x11 |
| 18 | K2-cp3-01 UB | 134 | -1.184508 | -1.556922 | no | VERIFIED WITH NOTES | power not run; MLL x11 |
| 19 | K2-aucpre-01 ZT | 13 | -0.050003 | -0.523387 | no | VERIFIED WITH NOTES | power not run |
| 20 | K2-aucpre-01 ZF | 10 | -0.163853 | -1.360682 | no | VERIFIED WITH NOTES | power not run |
| 21 | K2-aucpre-01 ZN | 15 | +0.038363 | +0.226383 | no | VERIFIED WITH NOTES | power not run |
| 22 | K2-aucpre-01 TN | 15 | +0.098338 | +0.397251 | no | VERIFIED WITH NOTES | power not run |
| 23 | K2-aucpre-01 ZB | 15 | +0.038935 | +0.271226 | no | VERIFIED WITH NOTES | power not run |
| 24 | K2-aucpre-01 UB | 15 | +0.085469 | +0.484355 | no | VERIFIED WITH NOTES | power not run |
| 25 | K2-aucpost-01 ZT | 13 | +0.050036 | +0.839348 | no | VERIFIED WITH NOTES | power not run |
| 26 | K2-aucpost-01 ZF | 10 | -0.060388 | -0.774136 | no | VERIFIED WITH NOTES | power not run |
| 27 | K2-aucpost-01 ZN | 15 | -0.165683 | -2.020520 | no | VERIFIED WITH NOTES | power not run |
| 28 | K2-aucpost-01 TN | 15 | -0.087149 | -0.811638 | no | VERIFIED WITH NOTES | power not run |
| 29 | K2-aucpost-01 ZB | 15 | -0.162545 | -0.825379 | no | VERIFIED WITH NOTES | power not run |
| 30 | K2-aucpost-01 UB | 15 | -0.199420 | -0.819896 | no | VERIFIED WITH NOTES | power not run; MLL x1 |
| 31 | K2-fomcpost-01 ZT | 10 | -0.565148 | -2.055790 | no | VERIFIED WITH NOTES | power not run |
| 32 | K2-fomcpost-01 ZF | 10 | -0.571837 | -1.989312 | no | VERIFIED WITH NOTES | power not run |
| 33 | K2-fomcpost-01 ZN | 10 | -0.390256 | -1.992230 | no | VERIFIED WITH NOTES | power not run |
| 34 | K2-fomcpost-01 TN | 10 | -0.417183 | -1.937702 | no | VERIFIED WITH NOTES | power not run |
| 35 | K2-fomcpost-01 ZB | 10 | -0.253801 | -1.921874 | no | VERIFIED WITH NOTES | power not run; MLL x1 |
| 36 | K2-fomcpost-01 UB | 10 | -0.280757 | -2.078464 | no | VERIFIED WITH NOTES | power not run; MLL x1 |
| 37 | K2-predrift-01 ZN | 12 | -0.030205 | -0.428879 | no | VERIFIED WITH NOTES | power not run |
| 38 | K2-predrift-01 ZB | 11 | -0.070798 | -1.241194 | no | VERIFIED WITH NOTES | power not run |
| 39 | K2-monthend-01 ZT | 18 | +0.008744 | +0.043508 | no | VERIFIED WITH NOTES | power not run |
| 40 | K2-monthend-01 ZF | 18 | -0.031390 | -0.125874 | no | VERIFIED WITH NOTES | power not run |
| 41 | K2-monthend-01 ZN | 18 | -0.087075 | -0.482553 | no | VERIFIED WITH NOTES | power not run |
| 42 | K2-monthend-01 TN | 18 | -0.114255 | -0.525601 | no | VERIFIED WITH NOTES | power not run |
| 43 | K2-monthend-01 ZB | 18 | -0.226174 | -1.161352 | no | VERIFIED WITH NOTES | power not run; MLL x1 |
| 44 | K2-monthend-01 UB | 18 | -0.434085 | -1.415467 | no | VERIFIED WITH NOTES | power not run; MLL x2 |

(Figures are the records' values, which my recomputation matched to 1e-9 relative; full precision in item1_verdicts.json and the records.)

The two notes, which apply to the recorded run and not to my recomputation:
- **Power check not run, all 44.** Every record's `power` is `{"status": "not_run", "reason": "StartRuleMissing: no frozen S_X for [<root>]: no reports/stage_e_start_rule_<SET>.json lists ..."}`: `_research_statistics` needs the confirmation supply days (the D4 start rule S_X of the root), and no frozen start-rule file exists for the rates roots. This is the same refusal that crashed the CLI (C-1) and that the imported `main()` records by name (R-T5-1). The D5 screen and the tiers do not depend on it. The D4 power label (the "achieved null power" of the falsification condition) is therefore absent for K2 and is for the lead to carry as an open item; the runner's own tests expect exactly this recording (STATE C-1).
- **MLL liquidations (24 records, 1 to 11 each).** The frozen engine simulates the XFA account (rules/xfa_rules.py XFA_50K: MLL $2,000 below the start balance, trailing to $0 then locked); when a member's cumulative losses reach the floor intraday, the engine liquidates the position at that bar (stage_e_engine.py check_mll lines 543-568: the worse of the bar's open and the floor-touch price), counts `mll_liquidation`, closes the day as breached, and starts a new account at the next trade date (roll_session lines 421-429, restart_on_terminal). The liquidation exit enters the series as that trip's close. For the losing port members this happens repeatedly (cp3 ZB and UB: 11 restarts in 299 days). It is the frozen harness's rule, not a recomputation matter; it explains the sub-rule holding minima in trade_rate (cp1 TN/ZB min hold 2 min, cp2 TN 6, cp3 ZN 9) and it means these series are the series of a member whose account is repeatedly stopped out and restarted, which D5's screen does not distinguish. In cp1 ZN's one case (2026-04-29, an FOMC statement day): entry sell 13:30 at 110.40625, liquidated 13:35 at 110.453125 (3 ticks against), trip net -$65.135; the day's loss itself was small, the floor was reached by the account's cumulative drift (mean -0.47 ticks/day over 13 months).

## Item 2: tiers (item1_screen.py)

Rule applied in my code (stage_e_stats._tier_one lines 214-238, read only): a coverage label -> "excluded" before screening (screen None);
any other D9 label (mean_holding_below_10min, entries_above_20_per_day, hold_below_2min) -> "excluded" whatever the screen says (ruling
OC-H), keeping its screen result; otherwise passes -> A, else B. Floor labels recomputed from each record's trade_rate: entry cap
refusals 0 and max entries per product-day 1 everywhere; min-hold refusals 0 everywhere; mean hold >= 15 min everywhere (the minima:
aucpre/aucpost/fomcpost/monthend fixed holds; cp1 28.6-29.0; cp2 74.8-75.9; cp3 376-398; predrift 15). Coverage ratios 0.9611 (fomcpost
TN) to 0.9986 (cp1 ZN), all >= 0.95, all `passes: true`. So no member carries a label, none passes the screen (every mean is negative or
t < 1.0; the highest t is aucpost ZT at 0.839), and all 44 belong in Tier B. K2_research_cluster.json: tiers.members has 44 entries, all
`tier: "B"`, `labels: []`, note "fails the D5 screen"; not_tiered {}, refused_members {}, power_check_undefined []. Tier A is empty, so K2
contributes no Holm family (k_from_tiers counts clusters with a non-empty Tier A). VERIFIED for all 44.

## Item 3: replay of two trials and rebuild from the trips (replay_two.py, rebuild_costs.py)

Replay, through the runner's own functions in the prescribed order: `harness_freeze.preflight(cf939270...)`; `load_cluster_freeze("K2")`
and `verify_cluster_code`; `resolve_member`; `_legs_inputs`; `load_release_calendar`; `_load_frames(..., "research",
data/processed, data/processed_step2)` (the loader verified the parquet sha256 f4a403f8... against the frozen table); `member_window`
(299 dates, the same exclusions); `factory()`; `_run_member`; `extract_trips`; `_series`. Fresh PYTHONPYCACHEPREFIX outside the
repository, nice 10, 00:55 PDT.

Determinism: for both trials the replayed `series.values` equal the record's list exactly (float for float), the dates and n_trips are
equal, the engine counters are equal, and the bar sha256 is equal. K2-cp1-01 ZN: 552 fills, 276 trips, counters {engine_not_a_window_date
9, mll_liquidation 1, closure_bars_seen:ZN 1}, 2 account starts (2025-04-01 and 2026-04-30 after the 2026-04-29 breach). K2-aucpost-01 ZN:
30 fills, 15 trips, 1 account. My own flat-to-flat pairing of the fills reproduces the runner's TripRecord list (dates and net cents).

Trip lists written: reports/stage_e3_briefs/audit/trips_K2-cp1-01_ZN.json and trips_K2-aucpost-01_ZN.json (per trip: entry and exit
fill times in CT, decision times, side, quantity, entry and exit prices, gross, commission, slippage and net cents, exit reason,
event-window flags; plus every fill, the runner's trips, the account starts and the breach days).

Rebuild in my own code (rebuild_costs.py; nothing from the runner's cost functions): commission per side = round-turn $2.62 -> 262 cents
/ 2 = 131 cents (reports/stage_e2a_costs.json products.ZN.commission_rt_usd; rules/products.py agrees); tick value 15.625 USD = 3125/2
cents; slippage per side = ceil(round(qty x s x 1562.5 cents, 6)) with s = the fill bar's 30-minute CT bucket's half-spread + that
bucket's depth term (46 buckets 17:00..16:00, no fallback bucket), or, for a fill in [release, release + 30 min) of a release whose
`products` list contains ZN (815 instants in the frozen calendar, read from the JSON), the largest half-spread of all buckets
(0.5010625313606667, the 17:00 bucket) + the bucket's depth term (D8 as read by ruling T12-4, stage_e_frozen.py lines 12-15); gross =
(exit ticks - entry ticks) x sign x qty x tick value, exact in Fractions; day value = sum over trips closing that trade date of
net_usd / (contracts x 15.625).

Results: K2-cp1-01 ZN: 552 fills, 0 commission or slippage mismatches against the engine's per-fill figures, 0 gross mismatches, 0
event-window flag mismatches (no cp1 fill lies in an event window: 13:30 and 13:59 are outside every ZN release's 30 minutes), all 299
days equal to the record within 1e-9 relative (worst difference 0). K2-aucpost-01 ZN: 30 fills, 0/0/0 mismatches, 15 event-window fills
(every 12:05 entry lies in [12:00, 12:30) of its own auction's close; no 15:05 exit does), all 299 days equal (worst difference 0). Both
VERIFIED. The replay is a replication for verification; the recorded run stays the only result.

## Item 4: trade counts and fill minutes (item4_counts.py; the replayed trips for 4b)

Event dates from the frozen tables (verified in part 1), restricted to 2025-04-01..2026-06-19, then to the 299 window dates, then less
early-halt dates (rates calendar; the window's halts are 2025-05-26, 06-19, 07-04, 09-01, 11-27, 11-28, 12-24, 2026-01-19, 02-16,
04-03, 05-25, 06-19). "Refused" is the record's `engine_not_a_window_date` counter (an intent on a blackout or UR-1 date).

| Member | Events in window | Blackout | Halt (not blackout) | Expected | n_trips (six roots) | Refused | Verdict |
|---|---|---|---|---|---|---|---|
| aucpre / aucpost ZT (2Y) | 13 | 0 | 0 | 13 | 13 / 13 | 0 | VERIFIED |
| aucpre / aucpost ZF (5Y) | 15 | 5 (2025-05-28, 08-27, 11-25, 2026-02-25, 05-27: the 5-year auctions fall in the roll blackouts) | 0 | 10 | 10 / 10 | 5 / 5 | VERIFIED |
| aucpre / aucpost ZN, TN (10Y) | 15 | 0 | 0 | 15 | 15 / 15, 15 / 15 | 0 | VERIFIED |
| aucpre / aucpost ZB, UB (30Y) | 15 | 0 | 0 | 15 | 15 / 15, 15 / 15 | 0 | VERIFIED |
| fomcpost (all six) | 10 | 0 | 0 | 10 | 10 x 6 | 0 | VERIFIED |
| predrift ZN | 15 | 0 | 0 | 15 | 12 | 0 | VERIFIED WITH NOTES: 3 dates untraded (2025-07-03, 2026-05-05, 2026-06-03) |
| predrift ZB | 15 | 0 | 0 | 15 | 11 | 0 | VERIFIED WITH NOTES: 4 dates untraded (2025-07-03, 2025-08-05, 2026-05-05, 2026-06-03) |
| monthend (all six) | 28 | 9 (the May, Aug, Nov, Feb and May month-ends sit in the roll blackouts; 2025-11-27 is also a halt) | 1 (2025-11-28) | 18 | 18 x 6 | 8 (ZT 7) | VERIFIED |

Every event member traded on every expected date and on no other date (my per-date check of the non-zero series days against the event
tables). The predrift shortfalls: the member trades only when s != 0; on the 7 untraded (date, root) pairs the record holds no signal, so
the reason (s = 0, or a missing 08:30 or 08:49 bar) is not checkable from the records; s = 0 over a 19-minute window is ordinary for ZB's
1/32 tick and plausible for ZN. Listed as unexplained in the brief's sense; a replay of the two predrift trials would settle it (not in my
brief). Monthend ZT's 7 refusals against 8 for the other roots: one blackout month-end date without a ZT 07:20 bar or with a halt-carrying
bar (also not checkable from the records; the date is excluded from the window either way, so no trade is affected).

Ports (no fixed expectation; n of 299 window dates): cp1 264-276 trips (7-10 refused on excluded dates; the rest zero-signal or missing
signal/entry bars), cp2 265-291 (14-16 refused; forced flattens at F on 1-2 days for ZT, ZF, TN, ZB; one D9.5a deferral each on ZN and
ZB; one entry refused inside the flatten window on ZT and TN, an early-halt day), cp3 121-136 (CLV outside the cuts on the other days;
4-7 refused). All consistent with the rules; the MLL liquidations (item 1 note) are the only engine exits besides F.

4b, fill minutes of the two replayed trials: K2-cp1-01 ZN: 275 of 276 trips entered at 13:30 and exited at 13:59 CT (decision bars
13:29 and 13:58; no deferred fill, no missing-bar shift in this trial); the one exception is the 2026-04-29 MLL liquidation at 13:35
(engine rule, documented above). K2-aucpost-01 ZN: all 15 trips entered at 12:05 and exited at 15:05 CT (T_a 12:00 for every 10-year
auction in the window, decision bars 12:04 and 15:04), no deferral. VERIFIED WITH NOTES (the liquidation).

## Item 5: program N

44 records, all `status: "run"` and screened; refused_members {} (0); every record's `member` is one of the freeze's 44 labels and the
cluster file's members list equals the freeze's ordinal order (K2-cp1-01 ZT ... K2-monthend-01 UB); no record names a trial the freeze
does not declare, and no declared trial lacks a record. N = 58 + 44 = 102. VERIFIED.

## Notes for the lead

- The two things a reader of the records should carry: the D4 power check is absent for all 44 (StartRuleMissing for the rates roots,
  as in C-1), and 24 of the 44 series include MLL-liquidation exits from the frozen XFA account model (up to 11 restarts per member).
  Neither changes a screen figure, a tier or N.
- Every 5-year auction in the research window that fell in a roll blackout (5 of 15) is lost to aucpre/aucpost ZF by the runner's
  exclusion, not by the members; the catalog's "15" is the pre-exclusion count.
- Unfinished: nothing in the brief. The 7 predrift (date, root) pairs and the one monthend ZT date stay unexplained at the level the
  records allow.

## Part 2, item 4 follow-up: the untraded predrift dates (lead request, R-T6-1 conditions)

01:02-01:04 PDT. Script reports/stage_e3_briefs/audit/replay_predrift.py, results predrift_followup.json. Preflight first
(cf939270...), cluster freeze verified, the runner's own loader (bar sha256 equal to the records for ZN and ZB), fresh
PYTHONPYCACHEPREFIX outside the repository, nice 10, nothing written under reports/stage_e3_k2_screen/, no repository file modified.

Determinism: for K2-predrift-01 ZN and ZB, a plain replay's series, dates and engine counters equal the records exactly (n_trips 12 and
11). A second replay with the member wrapped in an observer that only records and delegates (`Observer.on_minute` calls the real member's
`on_minute` and returns its items unchanged) also equals the records exactly, so the observation changed nothing.

What the member saw on each untraded ISM date (bars of CT date d at 08:30 and 08:49 CT; prices in vendor units; ZN tick 1/64, ZB tick 1/32):

| Root, date | In window, ISM date | 08:30 bar: id, halt, open, close | 08:49 bar: id, halt, open, close | s = close(08:49) - open(08:30), ticks | Intent | Refusal | Cause |
|---|---|---|---|---|---|---|---|
| ZN 2025-07-03 | yes, yes | 42066706, none, 111.25, 111.234375 | 42066706, none, 111.265625, 111.25 | 0 | none | none | s = 0 |
| ZN 2026-05-05 | yes, yes | 42000661, none, 110.3125, 110.3125 | 42000661, none, 110.3125, 110.3125 | 0 | none | none | s = 0 |
| ZN 2026-06-03 | yes, yes | 42001136, none, 109.4375, 109.4375 | 42001136, none, 109.421875, 109.4375 | 0 | none | none | s = 0 |
| ZB 2025-07-03 | yes, yes | 42144138, none, 114.40625, 114.375 | 42144138, none, 114.4375, 114.40625 | 0 | none | none | s = 0 |
| ZB 2025-08-05 (ZB only) | yes, yes | 42144138, none, 115.625, 115.625 | 42144138, none, 115.625, 115.625 | 0 | none | none | s = 0 |
| ZB 2026-05-05 | yes, yes | 42004655, none, 112.46875, 112.4375 | 42004655, none, 112.46875, 112.46875 | 0 | none | none | s = 0 |
| ZB 2026-06-03 | yes, yes | 42004736, none, 112.09375, 112.09375 | 42004736, none, 112.0625, 112.09375 | 0 | none | none | s = 0 |

On every one of the seven (date, root) pairs both signal bars were present and carried one instrument_id and no early_halt_ct; the
member's recorded 08:30 open ticks matched the bar; at 08:49 the 08:49 close equalled the 08:30 open to the tick, so s = 0 and the rule's
own clause "If s = 0, no trade" (catalog line 491) applied; the member emitted nothing and the engine recorded no intent, refusal or fill on
those dates. No missing bar, no halt, no guard, no engine refusal and no member defect. (Note that on 2025-07-03 and 2026-06-03 the
close-to-close difference is non-zero; the frozen rule takes the 08:30 open, and the member did.) Verdict: VERIFIED. The item 4 row for
predrift is therefore fully explained: 15 events, 12 (ZN) and 11 (ZB) with s != 0, all traded.
