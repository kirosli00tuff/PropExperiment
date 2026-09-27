# Stage E.4 Part 2 member audit, cluster K5 (MemberAuditor-K5-FableXHigh)

Worker: worker-xhigh, Fable 5.1, effort xhigh. Brief: reports/stage_e4_briefs/auditor_task3_K5.md.
Started 2026-09-27 05:23 PDT, ended 05:43 PDT. Read-only on the repository except this file and
reports/stage_e4_briefs/audit_k5/ (recompute_tables.py, mutants.py). Synthetic bars only; no runner,
no freeze, no commit, no web. The mutation check ran on a scratch copy of the code tree under the
session scratchpad, never on the repository (the K5 files were compared byte for byte before and after).

## Part 1: fidelity audit (Task 3)

### Files as audited (sha256)

| File | sha256 |
|---|---|
| strategy/members/k5/_calendar.py | 8c23f8f17d56136ff69adb72e8f81a5fa60f2707a7f62fd67576b9219a3b71d1 |
| strategy/members/k5/_event_common.py | 3c1053d9284dfcb5f49b28ed32a89848ab04197724cf462299ee7ac3e86ec05c |
| strategy/members/k5/_port_common.py | 832cd2efa5db1c5c98a95c32e1518b835839faebca2440e67475ba7c137bf4b1 |
| strategy/members/k5/_releases.py | 9b183f14a6eaf61c48fa84686ba239d3139c208377a9c4f88c7e01058cd7d1e6 |
| strategy/members/k5/cp1.py | 7681195b250ef7f0da5f1f7e4e1d241384750117e491aeff79f79ed6f45730b7 |
| strategy/members/k5/cp2.py | aa123ffe1d5b62827c29db98306154484d97bf4cc4b1827f94b607c03d525184 |
| strategy/members/k5/cp3.py | 24f319618b0d54817e6204c4d335e4479b4bdde20447f000c67c8d35cbf924ef |
| strategy/members/k5/fomc.py | 0fb73eb152fbba173d4a5d34bfae60dc6dfba18312690201d7db0a7148a68122 |
| strategy/members/k5/ovr.py | d079967be413cc54ea7c59603c1625410b3c9c0907d4c32239daff482d726270 |
| strategy/members/k5/pmfix.py | 4167234fcb30b81235a1ddd1c38838cc18e352b75a547c45115ee074381a47a4 |
| strategy/members/k5/preauc.py | 0dcaeda8e715267857e95aef1b04571d508e3b58249a8ead407e0bd6429adede |
| strategy/members/k5/__init__.py | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 (empty) |
| tests/test_e4_k5_members_a.py | 1f453149ad5f44f4ab650b026834073437e4e1f33f97e7004d31f88fdf236a11 |
| tests/test_e4_k5_members_a_ovr.py | d8d49fd28670240f8d1e2c324a433beee3102734a8ab9437026cbfe32947d8d6 |
| tests/test_e4_k5_members_b.py | c84689aa9649cf3163e031dc2b25a0153a750f009ddce7d3dadc30b0464bebb9 |
| tests/test_e4_k5_members_b_signal.py | 7759b839ad77d7069bf5104ef4d5e1db7962f9de246951bc41cca6f9825cb73d |
| reports/stage_e4b_member_specs.md | 409070805cc1f6f06f6717d193fe001548033a0e757497f313c70d5db22ee220 |
| reports/stage_e0_catalog_K5.md | 5773f841771f18f17c426cee513a5d8dce192c8a83770149fdef72ff186e22f8 |
| reports/stage_e2b_release_calendar.json | 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8 |
| reports/stage_e4b_release_check.json | 0715d01f0ab7f9176a7d559e4f8bde151e656c29271a9a1de22bece3218789b7 |
| reports/stage_e4_briefs/write_k5_freeze.py | ad19e06b0505fb89b142872f8361031d14a0bc9e5fe7348f66507835e7bec290 |
| strategy/members/k4/ovr.py (the audited K4 module, for F-7) | c221eada1cb67db2a1656b255980f67a03036c1a79972baa05e97884b0ce7494 |

The hashes of the eleven K5 member files equal the ones in the coders' reports (stage_e4b_coder_A.md,
stage_e4b_coder_B.md). The _port_common.py hash above is the one computed at 05:23; it equals coder A's.

### Summary

Findings: 0 BLOCKING, 1 SHOULD FIX, 9 NOTE.

- SHOULD FIX S-1: `test_cp2_the_opening_range_is_o_to_o_plus_15` (tests/test_e4_k5_members_a.py:587-599)
  does not pin the range's end. With `RANGE_MINUTES = 14` (cp2.py:54) every test in the file still
  passes (mutation check), so the 15-minute range literal is unpinned. The module is correct; the test
  claims more than it checks.
- Every module implements its frozen entry and nothing more (checklists below). Every clock time of the
  ports and of ovr is an offset from the frozen O/C; every event time comes from the literal tables or
  the entry's literal (fomc); q_c is never a literal; no member reads a hindsight field, a future bar,
  or any account field beyond `position`/`positions` and `pending` (grep over strategy/members/k5/*.py).
- All four literal tables recompute exactly from their sources (section 3): GOLD_AM_AUCTIONS 1802,
  GOLD_PM_AUCTIONS 1788, NO_AUCTION_DAYS 14 (all PM only), FOMC_STATEMENT_DATES 57 (equal to E.3's K2
  table), METALS_FULL_SESSIONS 1784. C10's 5-hour-week table matches zoneinfo in all eight years. Every
  one of the 14 no-auction days rests on a dated LBMA notice that predates it, read from the saved page
  the manifest says was served (section 4): all 14 follow C9.
- F-7 holds: strategy/members/k5/ovr.py differs from the audited k4/ovr.py only in the decision clock
  (derived from O and C), the calendar table, the value floor (80% of the possible values, derived), and
  names, docstrings and comments; the coverage window's end follows from the clock (section 2, item 13).
- The freeze static check passes on all 12 files; the dry-run prints the 11 declarations of S0.2 in order
  (cp1 1-2, cp2 3-4, cp3 5-6, preauc 7, pmfix 8, fomc 9, ovr 10-11). The four K5 test files pass on the
  repository (269 passed in 4.00s).
- Mutation check (section 5): 56 single-point mutants over the seven members and the two tables; 52
  killed; 4 survived, of which 2 are equivalent mutants (no test can distinguish them under the engine's
  trade-date convention), 1 was a mis-built mutant of my own (re-run correctly and killed), and 1 is S-1.

### 1. Per-member checklists (items 1-11)

Line numbers are of the file as hashed above. "C" is reports/stage_e0_catalog_K5.md, "S" the specs.

#### K5-cp1-01 (cp1.py; C 284-339; D6 line 364; S section 1)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Signal bar O+29 (MGC 07:49, MHG 07:39), entry C-31 (11:59 / 11:29, fill 12:00 / 11:30), exit C-2 (12:28 / 11:58), Globex-open bar 17:00 of d-1; every time an offset from the frozen O/C | OK | cp1.py:52-55, 86-88; _port_common.py:60-65 (O, C from `load_frozen_tables().day_session_ct`) |
| 2 | sign(close of O+29 minus open of the first bar) in vendor ticks; s > 0 buy, s < 0 sell, 0 no trade | OK | cp1.py:103-109, 124, 129 |
| 3 | Exit on the first present bar at or after C-2, resent while refused, never while an exit is pending | OK | cp1.py:121-122; _port_common.py:92-104 |
| 4 | q_c from the frozen vehicle table (MGC 1, MHG 2); the exit closes abs(position) | OK | cp1.py:137; _port_common.py:65, 103-104 |
| 5 | Event sets | n/a | |
| 6 | The first bar's open and the O+29 close are read on those bars (closed); the entry decision at C-31 | OK | cp1.py:123-130 |
| 7 | A port: D6's guard only (the two signal bars share one instrument_id), no C4 guard | OK | cp1.py:104-105 |
| 8 | Entry only when flat with nothing pending and once per date; exit only with a position; windows (17:00, 17:01) day -1, (07:49, 07:50), (11:59, 12:30) and the MHG twins | OK | cp1.py:131-133, 90-94 |
| 9 | State = day, first, signal, entered; no filter, size rule or re-entry | OK | cp1.py:96-97 |
| 10 | make_mgc / make_mhg; label "K5-cp1-01 MGC"; one traded leg; ordinals 1, 2 | OK | cp1.py:140-145; _port_common.py:55-57, 68-70; dry-run |
| 11 | Tests: entry/exit times both roots with q_c, decoy prices, missing Globex/signal/entry/exit bars, two ids, zero signal, refused exit resent, D9.5a in and next to the guard, synthetic F, D9.7, early halt (engine refuses), once per date. Mutants killed: O+28, C-30, C-3, guard off, zero-signal off | OK | test_a.py:423-560 |

Equivalent survivor: removing the `opened.date() == day - ONE_DAY` half of cp1.py:123 changes nothing
because the only 17:00 CT bar carrying trade_date d is on d-1 (the metals calendar has no booked-forward
day; recompute_tables.py prints `booked_forward: {}`). NOTE N-4.

#### K5-cp2-01 (cp2.py; C 340-392; D6 line 365; S section 2)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | OR = present bars in [O, O+15); buffer 4 vendor ticks (MGC 0.40, MHG 0.0020; K5-L-07); eligible bars [O+15, C); hold 75 present bars; window (O, 15:08) | OK | cp2.py:54-57, 80, 111-117 |
| 2 | close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells, compared in integer ticks | OK | cp2.py:119-123 |
| 3 | Exit on the 75th present bar with the position open, counted from the fill (B-H1's count, E.3-L-07); no C-2 exit; F is the backstop | OK | cp2.py:87-96, 105-106 |
| 4 | q_c; exit abs(position) | OK | cp2.py:96, 127 |
| 5 | Event sets | n/a | |
| 6 | Range from closed bars; trigger on the bar's own close at its decision time | OK | cp2.py:107-123 |
| 7 | A port: no guard (D6 and B-H1 have none) | OK | cp2.py:8-9 |
| 8 | One entry per date even if refused; entry only flat; exit only with a position and nothing pending; window (O, 15:08) | OK | cp2.py:115-117, 126, 93 |
| 9 | State = day, hi, lo, triggered, held | OK | cp2.py:84-85 |
| 10 | make_mgc / make_mhg; ordinals 3, 4 | OK | cp2.py:130-135 |
| 11 | Tests: 75-bar hold both roots with q_c, buffer exactly 4 either side both roots, missing bar in the hold, no C-2 exit, no entry from C, last eligible bar C-1 (fills 12:30 / 12:00, exits 13:45 / 13:15 as the catalog table), F, one entry even when refused, no range bar, present bars only, evening bars excluded, deferred entry fill starts the count, D9.7, state reset. Mutants killed: buffer 3, hold 74, entry at C, strict sell trigger, range end inclusive, count not reset. **Survivor: RANGE_MINUTES 14** | SHOULD FIX S-1 | test_a.py:572-720 |

#### K5-cp3-01 (cp3.py; C 393-442; D6 line 366; Family H; S section 3)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Daily bar [O, C) of CT date d, C_d = close of C-1 (12:29 / 11:59); entry on the O bar (07:20 / 07:10); exit C-2 (12:28 / 11:58); cuts 0.8 / 0.2 | OK | cp3.py:57-61, 117-118, 141-152, 181 |
| 2 | CLV >= 0.8 buys, <= 0.2 sells, non-strict, exact integer cross-products; Range > 0 | OK | cp3.py:75-88 |
| 3 | Exit on the first present bar at or after C-2 | OK | cp3.py:179-180 |
| 4 | q_c; exit abs(position) | OK | cp3.py:187 |
| 5 | Event sets | n/a | |
| 6 | d-1 is the most recent COMPLETE daily bar of an earlier trade date, finalised at the roll; day d's own bar never enters day d's condition | OK | cp3.py:123-139, 158-160 |
| 7 | Family H: complete day = O and C-1 bars present, no early_halt_ct on any bar of CT date d, one instrument_id over [O, C); guard d-1 against the O bar; early-halt day d not traded | OK | cp3.py:124-125, 142-143, 156-162 |
| 8 | Entry once per date, only flat; exit only with a position; window [O, C) | OK | cp3.py:181-183, 120 |
| 9 | State = prior, day accumulators | OK | cp3.py:133-139 |
| 10 | make_mgc / make_mhg; ordinals 5, 6 | OK | cp3.py:190-195 |
| 11 | Tests: cuts exactly at 0.8 / 0.2 both roots, between the cuts, exact comparison, zero range, d-1 finalised, most recent complete day, two ids incomplete, guard, missing O bar, early-halt day, missing exit bar, D9.5a, F, D9.7. Mutants killed: 0.81, 0.19, C_d at C-2, halt off, guard off, zero range allowed, two-id day kept, O bar not required | OK | test_a.py:749-895 |

#### K5-preauc-01 (preauc.py; C 443-537; S section 4)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Entry on the bar at T-31 (fill T-30), exit on the bar at T-2 (fill T-1); T from GOLD_AM_AUCTIONS (04:30, or 05:30 in 5-hour weeks); windows (03:59, 04:30) and (04:59, 05:30) | OK | preauc.py:32, 45-48, 54-58 |
| 2 | SELL, unconditional | OK | preauc.py:44, 104 |
| 3 | Exit on the first present bar at or after T-2 while no exit is pending | OK | preauc.py:97-98; _event_common.py:80-92 |
| 4 | q_c from the frozen vehicle table (1); exit abs(position) | OK | preauc.py:80; _event_common.py:91-92 |
| 5 | GOLD_AM_AUCTIONS: 1802 rows, recomputed equal (section 3); a PM-only no-auction day keeps its AM row (K5-L-03) | OK | _releases.py:75-677 |
| 6 | Only the T-31 bar is read before the entry; the table is known in advance (gov.uk file lists to 2028; every notice predates its day) | OK | preauc.py:99-104 |
| 7 | C4: no trade when the entry bar carries early_halt_ct; missing entry bar: no trade (S0.6); the instrument guard is vacuous; no percent return | OK | preauc.py:99-102 |
| 8 | One entry per date (the flag is set on the exact bar); no entry while pending; the exit branch precedes the entry so no entry with a position; windows S0.12 with both slots (K5-L-08) | OK | preauc.py:97-104, 47-48 |
| 9 | A date not in the table is not traded; nothing else | OK | preauc.py:83-88 |
| 10 | make_mgc only, no make_mhg; ordinal 7 | OK | preauc.py:43, 107-108 |
| 11 | Tests: 03:59 / 04:00 / 04:28 / 04:29 with qty 1, unconditional, 5-hour week 04:59 / 05:00 / 05:28 / 05:29 (nothing at 03:59), bank holiday, dropped and moved rows, PM-only day traded (2025-12-31), early halt, missing T-31 bar, missing T-2 bar (04:30, 04:31), D9.5a at the entry fill, at T (no deferral, synthetic and frozen calendar, both slots), at the exit fill, F, D9.7, consecutive days, direct calls. Mutants killed: -30, -3, buy, halt off, window end, flag off | OK | test_b.py:483-614 |

#### K5-pmfix-01 (pmfix.py + _event_common.py; C 538-639; S section 5)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Signal bars T_P-1 and T_P+1, entry on T_P+1 (fill T_P+2), exit on T_P+11 (fill T_P+12); T_P from GOLD_PM_AUCTIONS (09:00 / 10:00); windows (08:59, 09:13), (09:59, 10:13) | OK | pmfix.py:29, 40-44, 47-53 |
| 2 | s = ticks(close T_P+1) - ticks(close T_P-1); s > 0 BUY, s < 0 SELL, s = 0 no trade | OK | _event_common.py:136-137, 150-153 |
| 3 | Exit on the first present bar at or after T_P+11 while no exit is pending | OK | _event_common.py:138-139, 80-92 |
| 4 | q_c (1); exit abs(position) | OK | _event_common.py:117, 153, 92 |
| 5 | GOLD_PM_AUCTIONS: 1788 rows = 1802 less the 14 PM-only days, recomputed equal | OK | _releases.py:680-1277 |
| 6 | Both closes read at their bars' closes; the entry decision at T_P+2 | OK | _event_common.py:136-137, 150 |
| 7 | C4: early halt on the entry bar, both signal bars one instrument_id, either bar missing: no trade | OK | _event_common.py:140-149 |
| 8 | One entry per date; no entry while pending; the exit branch precedes | OK | _event_common.py:138-144 |
| 9 | Nothing more (plans per date, the capture, the flag) | OK | _event_common.py:120-127 |
| 10 | make_mgc only; ordinal 8 | OK | pmfix.py:39, 77-78 |
| 11 | Tests: 09:01 / 09:02 / 09:11 / 09:12 both signs with qty 1, s = 0 whatever 09:00 does, only the two closes make s, 5-hour week 10:01 / 10:02 / 10:11 / 10:12, two ids (each bar), missing bar (each), missing exit bar, PM no-auction day and bank holiday not traded, dropped and moved rows, early halt, D9.5a at the entry fill and at T_P (no deferral; frozen calendar both slots), F, D9.7, per-date reset, direct calls. Mutants killed: -2, +2, +12, s = 0 off, sign flipped, guard off, exit later, pending check off, halt off | OK | test_b_signal.py:64-191, 293-305 |

#### K5-fomc-01 (fomc.py + _event_common.py; C 640-712; S section 6)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | 12:59 / 13:04 (fill 13:05) / 13:14 (fill 13:15) CT, the same in 5-hour weeks; FOMC_STATEMENT_DATES; window (12:59, 13:16) | OK | fomc.py:28, 39-42, 45-49 |
| 2-4 | As pmfix (the shared SignedMoveEvent) | OK | _event_common.py:100-153 |
| 5 | FOMC_STATEMENT_DATES: 57 dates, the calendar's FOMC rows at 13:00 CT, equal to E.3's table; 10 in the research window (C12's list); none on an early halt or a non-trade date | OK | _releases.py:1279-1290 |
| 6-9 | As pmfix | OK | |
| 10 | make_mgc only; ordinal 9 | OK | fomc.py:38, 73-74 |
| 11 | Tests: 13:04 / 13:05 / 13:14 / 13:15 both signs with qty 1, s = 0, non-FOMC date (and an injected row trades), 5-hour week keeps 13:00 CT, two ids, missing bars, missing 13:14 and 13:15 (13:16 / 13:17), early halt, the frozen calendar's guard at [13:00, 13:02) and event window, D9.5a at the entry fill, F, D9.7, direct calls. Mutants killed: 12:58, 13:05, 13:15 | OK | test_b_signal.py:194-305 |

#### K5-ovr-01 (ovr.py; C 713-804; S section 7; F-7)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | t = O + 60k while t <= C from the frozen O/C: MGC 08:20..12:20 (5), MHG 08:10..11:10 (4) (printed by a direct call: equal); signal open at t-60, close at t-1; entry on t-1 (fill t); exit t+58 (fill t+59); 20 reference dates; floor 80% of the possible values = 80 / 64 (printed: equal); deciles 10 / 90 numpy linear; window (O, last t + 60) = (07:20, 13:20) / (07:10, 12:10) | OK | ovr.py:65-73, 83-94, 147-154 |
| 2 | r <= P10 buys, r >= P90 sells (a fade); the tie is no trade (K4-L-10); r = (tc - to) / to from integer ticks with to > 0 | OK | ovr.py:104-119 |
| 3 | Exit on the first present bar at or after t+58; after an engine exit no exit of its own and no re-entry at that t | OK | ovr.py:214-217, 223 |
| 4 | q_c (1 / 2); exit abs(position) | OK | ovr.py:224 |
| 5 | Reference dates = the 20 METALS_FULL_SESSIONS dates strictly before d (1784 dates, recomputed equal); values r(tau) at the same clock times, each counted only with both bars, one id, open > 0; absent dates keep their slot | OK | ovr.py:75-76, 97-101, 169-178, 185-190 |
| 6 | Reference values only from earlier trade dates (today's are filed at the roll); the day's r from two closed bars | OK | ovr.py:157-167, 206-213 |
| 7 | C4: early halt on the decision bar; per-t guard on the t-60 and t-1 bars (K4-L-14); a missing bar: no trade at t; C10's open > 0 on r(t) and on every reference value | OK | ovr.py:104-108, 172-178, 181-184 |
| 8 | Entry only when flat with nothing pending (positions never overlap); at most 5 / 4 entries; windows | OK | ovr.py:218-224, 152-154 |
| 9 | Warm-up (K4-L-09) and the fewer-than-20-table-dates rule (K4-L-13) are the lead's readings; nothing else | OK | ovr.py:186-187 |
| 10 | make_mgc / make_mhg; ordinals 10, 11 | OK | ovr.py:227-232 |
| 11 | Tests: decision times both roots (and K4's clock gives K4's five literal times), the floor 80 / 64, ladder cuts, reference dates (halts excluded, table start), hourly_return incl. C10, non-strict cuts and the tie, numpy linear, entry/exit both roots with q_c, cut boundaries, back-to-back trades never overlap (last fill 13:19 / 12:09), decoy prices, warm-up, fewer than 20 table dates, early-halt dates not referenced, early-halt trade date not traded, only 20 dates, exactly 80 vs 75 and 64 vs 60, missing bars reduce the count (84 / 79, 67 / 63), roll-blackout date counts, two-id value not counted, earlier-contract values count, day-d two ids block that t only, missing signal bars, missing exit bar skips the next t, D9.5a at t / next to t / deferred exit, F, D9.7 (later t trade; not duplicated), state across days. Mutants killed: 57, 19 dates, 79%, 81%, 11/89, open < 0, halt off, warm-up off, floor off by one, t = C excluded, tie -> buy, per-t guard off, history pruning | OK | test_a_ovr.py:153-506 |

Equivalent survivor: replacing `is_flat` by `position` at ovr.py:218 cannot be distinguished by a
test: a pending order with a zero position at a decision bar would need an entry unfilled for 60
minutes, which the engine's next-open fill excludes. NOTE N-4.

### 2. The lead's readings (item 12) and F-7 (item 13)

Adopted E.3 readings (E.3-L-01, 03-13, 15, 17, 19, 22): K5's port texts are D6's verbatim and K5's C4
(lines 105-114) has the same three clauses and the same "first later bar" sentence as K2's, so the K2
readings apply unchanged; each is implemented (checklists above). Adopted K4 readings (K4-L-05, 09, 10,
13, 14, and K4-L-08 through K5-L-05): the K5 ovr text is the same rule text (R-24), so they apply; each
is implemented.

| Reading | Verdict | Basis |
|---|---|---|
| K5-L-01 tables span 2019-05..2026-06 | Agree, with K4-L-01's caveat: the confirmation-window rows are kept as the sources give them. For K5 the 14 half days ARE verified by dated notices for every year (section 4); what is unverified is the IBA calendars' own advance publication (PDF metadata) and the 10:30 / 15:00 start times page by page for 2020-2025. NOTE N-3 | C9 lines 167-174; check JSON `unverified` |
| K5-L-02 instants by zoneinfo | Agree; verified on every row: the CT instants recomputed from Europe/London 10:30 and 15:00 equal the table's on all 1802 / 1788 rows, only the pairs 04:30 / 09:00 and 05:30 / 10:00 occur, and C10's weekday ranges match in all eight years | C10 lines 195-230 |
| K5-L-03 a scheduled auction day is per auction | Agree, and it is the narrowest reading of C9 line 171-172: "a day announced in advance as having no auction" is a day with no auction; a half day with an AM auction and no PM auction is such a day for the PM auction only. Dropping the AM auction on those days would exclude an auction the text schedules | C9 lines 167-172 |
| K5-L-04 section 7 item 1 settled by the frozen harness | Agree (a lead decision, quoted from the prompt). Verified: the frozen calendar's rows naming MGC or MHG are CPI 07:30 (85), NFP 07:30 (85), G17 08:15 (85) and FOMC 13:00 (57); no release of any auction kind exists in the calendar. Pinned by test_b.py:384 on 7,294 fill instants | recompute_tables.py |
| K5-L-05 ovr's "eligible trade dates (C4)" = EC-CAL full sessions, roll blackouts included | Agree, fixed by the cited reference rather than by the words alone. The literal words admit a stricter reading (drop roll-blackout dates and dates with missing bars), but (a) the entry's banner (C line 715, R-24) and E.1 F-7 fix K5's rule text as identical to K4's, whose words are "full sessions in EC-CAL"; (b) the roll-blackout dates are computed by the runner from contract splices in the bars, which a frozen member cannot read (E.3-L-01), so the stricter reading is not codable before the bars are read; (c) C4's missing-bar clause is met per computation by the entry's own "at least 80% of the possible values must exist ... otherwise no trade at t" (C 753-754), which shows the entry counts values, not dates. I would take the same reading | C 715, 751-754; E.1 F-7 |
| K5-L-06 the floor is 80% of the possible values | Agree; literal in C line 753 ("80 of 100 for gold ..., 64 of 80 for copper") | C 753 |
| K5-L-07 CP2's buffer 4 x vendor_tick | Agree: gold's most active contract by the D1 table is MGC (429,702 vs GC 212,764), copper's is HG (77,679 vs MHG 21,803); both pairs share one tick (C7 lines 147-149), so 0.40 and 0.0020 are D6's "4 ticks of P" whatever the vehicle. Pinned as Decimal literals (test_a.py:572-575) | C 81, 145-149; D 368-374 |
| K5-L-08 two coverage slots for preauc and pmfix | Agree; the frozen interface has no event-date condition (E.3-L-17), so both slots are measured on every research date, a proxy as K4's ngpre. A shortfall in the other slot's minutes would count against the member; the lead's reading | S0.12 |
| K5-L-09 the 10-minute hold at D9's floor | Agree; the entry names T_P+11 and 13:14 as the exit bars; a label, not a drop, is the D9 text ("checked at screening ... labelled") | C 596, 610, 677, 687 |
| K5-L-10 preauc unconditional | Agree; C 490-491 says "unconditional; there is no signal"; the only member-side conditions are the entry bar's presence and its early_halt_ct (C4), both implemented | C 488-491 |
| K5-L-11 11 declarations; preauc 1 trial | Agree; "each traded only if D2 admits it" (C 445) and silver has no vehicle (E.2a), so U9's 2 becomes 1; the dry-run prints 11 in S0.2's order | C 445, 536 |
| K5-L-12 two coders, four test files | Agree (organisational) | |

Readings the specs take without a K5-L number, all consistent with the frozen text: preauc's entry
bar is T-31 on CT date d (03:59 belongs to trade date d, whose session began at 17:00 of d-1); fomc's
clock is unchanged in 5-hour weeks (an ET event; C1 line 94); early halts read from the entry decision
bar (E.3-L-11; data/bars.py labels every bar of the CT date). CP2's "75 minutes after the fill" (D6)
versus "the 75th bar after the entry-intent bar" (C 366-367) differ only when D9.5a defers the fill; the
code follows D6, which the entry says governs (C 297). NOTE N-8.

**Item 13, F-7.** `diff strategy/members/k4/ovr.py strategy/members/k5/ovr.py` changes:
(a) the clock: K4's literal `DECISION_TIMES_CT` (09:00..13:00) becomes `DECISION_STEP_MIN = 60` and
`decision_times(o, c)` = O + 60k while t <= C (ovr.py:65, 83-87, 147); applied to K4's O/C it returns
K4's five literals (test_a_ovr.py:153-165); (b) the calendar table: ENERGY_FULL_SESSIONS becomes
METALS_FULL_SESSIONS (ovr.py:44, 75); (c) the value floor: K4's `MIN_VALUES = 80` becomes
`VALUE_FLOOR_PERCENT = 80` and `min_values(n_times)` = ceil(0.8 x 20 x n_times) = 80 on MGC, 64 on MHG
(ovr.py:70, 90-94, 148, 189); (d) the coverage window's end: K4's literal 14:00 (= its last t + 60, K4
audit N-5) becomes `shift(self._times[-1], 60)` (ovr.py:73, 152-154), a consequence of (a);
(e) module path, MEMBER_ID, factories, `__all__`, docstrings and comments. Every other line is identical:
the signal, C10, reference dates, warm-up, percentile cuts, tie, entry, exit, early halt and state
handling. F-7 as recorded in reports/stage_e1_changes.md line 32 holds; the two modules carry one rule
text with K5's clocks.

### 3. Table recomputation (item 5; reports/stage_e4_briefs/audit_k5/recompute_tables.py, independent of gen_k5_*.py)

Sources read: the saved gov.uk file data/vendor/release_pages/e4b/govuk_bank-holidays.json (sha256 equals
the manifest's), the check JSON's 14 no-auction rows, the frozen release calendar's FOMC rows, E.3's
strategy/members/k2/_releases.py as text (ast), and EC-CAL through `load_group_calendar("metals")`.
Both source hashes equal the constants in _releases.py:24-25; data/calendars/metals.py's sha256 equals
_calendar.py:21.

| Table | Recomputed | Module | Equal | Detail |
|---|---|---|---|---|
| EC-UKBH (England and Wales) | 61 in 2019-05-01..2026-06-19, all on weekdays; the gov.uk file lists 2019-01-01..2028-12-26 (83 rows) | check JSON 61 | yes | no weekend row; the check's list equals the saved file's |
| GOLD_AM_AUCTIONS | 1863 weekdays - 61 = 1802; 1678 at 04:30, 124 at 05:30 | 1802 | yes, row for row | AM-not-held rows: 0 |
| GOLD_PM_AUCTIONS | 1802 - 14 = 1788; 1664 at 09:00, 124 at 10:00 | 1788 | yes, row for row | |
| NO_AUCTION_DAYS | 14, all PM only, all weekdays that are not bank holidays, every notice_date < date | 14 | yes | section 11's list exactly |
| 5-hour weeks (C10 table) | recomputed from zoneinfo alone per year: 2019 03-11..03-29 (15) / 10-28..11-01 (5); 2020 03-09..03-27 (15) / 10-26..10-30 (5); 2021 03-15..03-26 (10) / 11-01..11-05 (5); 2022 03-14..03-25 (10) / 10-31..11-04 (5); 2023 03-13..03-24 (10) / 10-30..11-03 (5); 2024 03-11..03-29 (15) / 10-28..11-01 (5); 2025 03-10..03-28 (15) / 10-27..10-31 (5); 2026 03-09..03-27 (15) / 10-26..10-30 (5) | C10 lines 208-215 | all 8 match | in the table 2024's spring has 14 rows (03-29 is Good Friday) and 2019's spring and 2026's autumn lie outside the range |
| Research window | 319 weekdays, 12 bank holidays, 307 AM days (20 at 05:30), 305 PM days, PM-not-held 2025-12-24 and 2025-12-31 | specs section 11 | yes | |
| The check's auction_days | the same 1802 dates; am_ct / pm_ct equal mine on every row | | yes | |
| FOMC_STATEMENT_DATES | the calendar's 57 FOMC rows, all 13:00 CT (14:00 America/New_York), all naming MGC and MHG | 57 | yes | equal to E.3's K2 table (57); 10 in the window = C12's list; all EC-CAL trade dates, none an early halt; the cancelled 2020-03-18 meeting has no row and is in the calendar's cancellations list |
| METALS_FULL_SESSIONS | 1843 metals trade dates 2019-05-01..2026-06-19 less 59 early halts = 1784, 2019-05-01..2026-06-18 | 1784 | yes | booked_forward is empty; window 315 trade dates, 11 halts and 4 weekday closures as specs lines 27-28 |
| Frozen calendar rows naming MGC / MHG (K5-L-04) | CPI 07:30 (85), NFP 07:30 (85), G17 08:15 (85), FOMC 13:00 (57); the calendar's 14 release kinds contain no auction | | | |

Informational (for Task 6's trade counts): 52 AM auction days are EC-CAL early halts, 9 in the research
window (2025-06-19, 07-04, 09-01, 11-27, 11-28, 12-24, 2026-01-19, 02-16, 06-19): preauc and pmfix skip
them by the entry bar's early_halt_ct. 42 bank holidays are CME trade dates (8 in the window: 2025-04-21,
05-05, 05-26, 08-25, 12-26, 2026-04-06, 05-04, 05-25): no auction, so no preauc or pmfix trade, the other
members unaffected. One AM auction day (outside the window) is not an EC-CAL trade date: no bars, no
trade. Coder A's observation checks: METALS_FULL_SESSIONS equals K4's ENERGY_FULL_SESSIONS entry for
entry (1784 dates), as data/calendars/metals.py says the two calendars coincide.

### 4. The 14 no-auction days against the saved pages (item 5)

Each page was read from data/vendor/release_pages/e4b/ by grep; the manifest's `url_served` and note
were compared with the request. C9 asks that the day be "announced in advance as having no auction".

| Day | Evidence (saved page, its own dateline) | Served as requested | C9 |
|---|---|---|---|
| 2019-12-24, 12-31 | wb_20191218064424_...2019-festive-period.html, post dated "Friday, December 13, 2019": "There will also be no pm LBMA Precious Metal Prices published on Tuesday 24 December 2019 and Tuesday 31 December 2019. On both of these days only the am LBMA Gold ... will be published" | yes (manifest: "served capture 2019-12-18 06:44:24 UTC (as requested)") | follows: notice 11 days before. The IBA 2019 calendar (Auction (1500) "O = No Auction") was served from a 2020-12-02 capture, recorded as such in the manifest; it corroborates and is not the advance evidence. NOTE N-9 |
| 2020-12-24, 12-31 | wb_20201216163829_...2020-21-festive-period.html, post dated "Tuesday, December 15, 2020" (and the live 2020-2021 article, dateline December 15, 2020): the same wording for Thursday 24 and Thursday 31 December 2020 | yes (as requested) | follows; IBA 2020 calendar marks 1500 "O" |
| 2021-12-24 | lbma_lbma-precious-metals-auctions.html, dateline November 23, 2021: "ICE Benchmark Administration has also confirmed that on Friday, 24 December there will be an AM auction for LBMA Gold and Silver prices but no PM auction for either metal" | live | follows |
| 2021-12-31 | lbma_closing_times_base.html, dateline December 07, 2021: "There will also be no PM LBMA Precious Metal Prices published on Friday 31 December 2021" (the same article repeats the 24 December AM-only statement) | live | follows; IBA 2021 calendar marks 1500 "O" on both |
| 2022-12-23, 12-30 | lbma_closing_times-2022.html, dateline December 07, 2022: "on Friday 23 and Friday 30 December there will only be AM auctions" | live | follows; IBA 2022 "Day Before Christmas Eve / New Year's Eve", 1500 "O" |
| 2023-12-22, 12-29 | lbma_closing_times-2023.html, dateline December 14, 2023: "There will be no gold, platinum or palladium PM auction on Friday 22nd or Friday 29th December 2023" | live | follows; IBA 2023 1500 "O" |
| 2024-12-24, 12-31 | lbma_closing_times-2024.html, dateline December 17, 2024: "There will be no gold, platinum or palladium PM auction on Tuesday, 24 or Tuesday, 31 December 2024" | live | follows; IBA 2024 1500 "O" |
| 2025-12-24, 12-31 | lbma_closing_times-2025.html, dateline December 15, 2025: "There will be no gold, platinum or palladium PM auction on Wednesday, 24 or Wednesday, 31 December 2025" | live | follows; IBA 2025 1500 "O" |

Every IBA calendar 2019-2025 marks Auction (1030) "P = Auction Unaffected" and Auction (1500) "O = No
Auction" on these 14 days (pdftotext, the key read from each PDF). The notice dates in the check JSON
equal the pages' datelines on all 14 rows. No mis-dated capture: the one substitution (the 2019 PDF)
is declared in the manifest and the check's `unverified` list.

### 5. Tests (item 11) and the mutation check

The four files pass on the repository: `nice -n 10 uv run pytest -q tests/test_e4_k5_members_a.py
tests/test_e4_k5_members_a_ovr.py tests/test_e4_k5_members_b.py tests/test_e4_k5_members_b_signal.py`
-> `269 passed in 4.00s`. Every case the brief names is pinned with literal expected times
per root (entry and exit fills, the event window, the synthetic flatten, a missing bar at each decision
time, a 5-hour-week auction and a moved or dropped row, the PM-only no-auction day, the percent-return
guard for ovr, and the D9.7 exit through the test-only ForcedLimitRules). No test passes vacuously: each
asserts fills or intents with explicit times and sides, and the table pins recompute from the sources.

Mutation check (reports/stage_e4_briefs/audit_k5/mutants.py on the scratch copy): 56 mutants, each one
textual change; killed unless stated.

| Member | Mutants (all killed unless marked) |
|---|---|
| preauc | entry -30, exit -3, side buy, halt check off, 5-hour window end, one-chance flag off |
| pmfix / fomc / _event_common | offsets -2 / +2 / +12, 12:58 / 13:05 / 13:15, s = 0 off, sign flipped, guard off, exit one bar later, pending-exit check off, halt off |
| cp1 | O+28, C-30, C-3, guard off, zero signal -> sell; **Globex-bar date check off: survived, equivalent** (N-4) |
| cp2 | buffer 3, hold 74, entry at C, strict sell trigger, range end inclusive, count not reset; **RANGE_MINUTES 14: survived** (S-1) |
| cp3 | 0.81, 0.19, C_d at C-2, halt off, guard off, zero range allowed, two-id day kept, O bar not required |
| ovr | exit 57, 19 dates, 79%, 81%, 11/89, open < 0, halt off, warm-up off, floor off by one, t = C excluded, tie -> buy, per-t guard off, history pruning; **is_flat -> position: survived, equivalent** (N-4) |
| tables | extra FOMC date, PM no-auction day added back, one AM row dropped, an early-halt date inserted in METALS_FULL_SESSIONS |

(A first calendar mutant of mine only added an unused constant and "survived" for that reason; it was
re-built as a table insertion and killed by 5 tests.)

### 6. Item 14: catalog section 7 as settled

| Item | Settlement | Follows the frozen text and the prompt? |
|---|---|---|
| 1 auction starts and D9.5a | K5-L-04: the frozen release calendar has no LBMA row, so neither D8's cost nor D9.5a's guard applies at an auction start; C11's "D8 cost only, pending the lead" row is not in force | Yes: C11 leaves it to the lead, and the prompt (as quoted in K5-L-04) says to use what the frozen D8/D9 text and the E.2b calendar already do. Verified that the calendar names MGC/MHG only at CPI, NFP, G.17 and FOMC. No member's fill lands in [T, T+2) of an auction (preauc exits at T-1, pmfix enters at T_P+2; pinned) |
| 3 preauc rests on one abstract | Kept on gold only, 1 trial (silver has no vehicle; platinum out by U2) | Yes: C 448 (the 01:47 ruling kept gold and silver), C 445 ("only if D2 admits it") |
| 4 fomc low frequency | Kept, 1 trial; the power check decides | Yes: C 690-692 (the 21:52 Q4 ruling) |
| 5 ovr on copper | Included, 1 trial (make_mhg, ordinal 11) | Yes: C 735-736, 1051-1053 |
| 6 pmfix's evidence leans against it | Kept, 1 trial | Yes: C 1057-1059 |

Items 2 (durable goods, C11 only), 7 (K5-ml-01, excluded by U6), 8 (platinum OUT, U2) and 9-11 touch no
member module; no SI, SIL, PL, GC or HG factory exists (test_a.py:275-276, test_b.py:425).

### 7. Findings

**BLOCKING**

- None.

**SHOULD FIX**

- **S-1. The CP2 opening-range test does not pin the range's end.** Where:
  tests/test_e4_k5_members_a.py:587-599 (`test_cp2_the_opening_range_is_o_to_o_plus_15`); the literal
  is cp2.py:54 (`RANGE_MINUTES = 15`). What is wrong: the test's comment says "the bars at O and O+14 are
  inside it", but the O+14 bar carries only a low extreme (`hi - 1: (0, 0, -3, 0)`) and the test checks
  the buy side only, so the O+14 bar's membership never enters an assertion. With `RANGE_MINUTES = 14`
  (range [O, O+14), the O+14 bar eligible) all 135 tests in the file pass (mutation check), while
  `range end inclusive` and `BUFFER_TICKS = 3` are killed. The module is correct; the 15-minute literal
  of D6 is unpinned. Smallest fix, inside the frozen entry: add a sell-side pair to the same test (a
  close of B-7 at O+15 sells, B-6 does not: with a 14-minute range OR_low would be B-2 and B-6 would
  sell), or give the O+14 bar the high extreme instead of the O bar; and assert `cp2.RANGE_MINUTES == 15`
  beside the buffer literal at test_a.py:572-575. The K5 test is adapted from K4's twin, which likely
  shares the gap (outside this brief; for the lead).

**NOTE**

- N-1. cp2.py:89-96: the resend of a refused 75-bar exit is untested (K4 audit N-4 carried over: the exit
  cannot be refused for min-hold, and any other refusal is the engine's own flatten path).
- N-2. Every D9.7 test uses the test-only `ForcedLimitRules` subclass (test_a.py:173-187,
  test_b.py:154-168) because MGC and MHG are DCB-only (not in rules.price_limits.HARD_LIMIT_PRODUCTS,
  asserted at test_a.py:309); the tests pin the member's reaction to an engine-forced
  `price_limit_exit`, not the price bands. Adequate for S0.7, as K4 audit N-3.
- N-3. K5-L-01: for the confirmation window the 14 half days are verified by dated notices (section 4),
  but the IBA calendars' advance publication rests on PDF CreationDate metadata, the 2019 calendar was
  served from a 2020-12-02 capture, and the 10:30 / 15:00 start times were not checked page by page for
  2020-2025 (the check's `unverified` list). No research-window date is affected. A Tier A preauc or
  pmfix confirmation session should re-check 2019-2024 first, as the specs say.
- N-4. Two equivalent mutants survive: cp1.py:123 (the `opened.date() == day - ONE_DAY` half of the
  Globex-bar test; the only 17:00 CT bar carrying trade_date d is on d-1, and the metals calendar has
  no booked-forward day) and ovr.py:218 (`is_flat` versus `position`; a pending order with a zero
  position cannot exist at a decision bar under the engine's next-open fill). Not defects; recorded so
  the lead does not read the survivors as gaps.
- N-5. METALS_FULL_SESSIONS equals K4's ENERGY_FULL_SESSIONS entry for entry (1784 dates); expected,
  since data/calendars/metals.py states the two calendars coincide. No action.
- N-6. For Task 6's counts: preauc's research-window event set is 307 AM days less the 9 EC-CAL
  early halts less roll-blackout dates; pmfix's is 305 PM days less the same 9 halts less s = 0 days
  less roll blackouts; fomc's is 10; the 8 bank holidays that are CME trade dates trade nothing on the
  two auction members. The two PM-not-held window dates: 2025-12-24 (a halt: no member trades) and
  2025-12-31 (preauc trades its AM auction; pmfix does not), both pinned (test_b.py:528-532,
  test_b_signal.py:126-129).
- N-7. _event_common.py:86: with `exit_ns` None and an open position the member sends nothing. A
  position on a date without a plan is unreachable (positions open only on plan dates and the engine
  flattens at F), so the engine's forced flatten is the only path; harmless.
- N-8. CP2's D6 text "75 minutes after the fill" and the entry's "the 75th bar after the entry-intent
  bar" (C 366-367) coincide except when D9.5a defers the fill (by up to 2 bars). The code counts from
  the fill (cp2.py:87-96), which D6 says governs (C 297) and E.3-L-07 reads; pinned by
  test_a.py:682-687. Consistent; recorded because the two frozen sentences differ.
- N-9. The 2019 IBA gold holiday calendar in data/vendor/release_pages/e4b/ is the 2020-12-02 Wayback
  capture, declared as such in the manifest and the check (`unverified`). The advance evidence for
  2019-12-24 and 12-31 is the LBMA notice of 2019-12-13 (Wayback 2019-12-18, served as requested), so
  both days follow C9; the calendar is corroboration only.

Non-findings worth recording: no member reads `vendor_degraded_day`, `in_flatten_window`,
`in_no_new_positions_window`, `is_roll_session`, `gap_before_minutes`, `raw_symbol`, `volume`,
`avg_entry_price`, `balance_cents`, `entries_today`, `phase` or `status` (grep); bar fields read
are open (cp1 and ovr, through `asdict` because the freeze bans the name), high, low, close,
instrument_id, trade_date, ts_event_ns and early_halt_ct; `screening.stage_e_freeze.check_member_source`
returns no refusal on any of the 12 files (including `__init__.py`); `write_k5_freeze.py --dry-run`
prints the 11 declarations of S0.2 in order; the two source hashes in _releases.py and the calendar
hash in _calendar.py equal the files' hashes; no tracked file changed during this audit (`git status`
at 05:43 shows only the three files already modified before it and the untracked audit_k5/ scripts).

## Part 2: recomputation (Task 6)

MemberAuditor-K5-FableXHigh, resumed with reports/stage_e4_briefs/auditor_task6_K5.md and the lead's
message (items 0, 2 and 5 extended). Started 05:58 PDT, ended 06:08 PDT, 2026-09-27. Read-only; no
runner, no member, no bar file. Every figure below is recomputed in my own code from the runner's recorded
outputs (reports/stage_e4b_k5_screen/, 23 files) and the frozen tables:
reports/stage_e4_briefs/audit_k5/recompute_screen.py (its printout recompute_screen.out) and two inline
checks (expected coverage minutes; cp2's halt-day trips and event-window fills). The frozen definitions I
computed against, and matched to 1e-9: series value = the sum over the date's trips of net_cents / (the
trip's own contracts) / tick value cents, zeros on window dates without a trip (runner docstring item 5);
t = mean / (population sd / sqrt(n)); passes = mean > 0 and t >= 1.0 (D5 lines 305-306;
screening/stage_e_stats.py:141-168); tiers as ruling OC-H (reports/stage_e2b_task1_stats_worker.md:171-183;
stage_e_stats._tier_one lines 215-238); trip net = gross - 192 c x contracts - slippage(open side) -
slippage(close side), slippage per side = ceil(round(contracts x ticks x tick value cents, 6)), ticks from
the fill's 30-minute CT bucket of reports/stage_e2a_costs.json or, inside [release, release + 30 min) of a
release naming the product in reports/stage_e2b_release_calendar.json, the product's largest half spread
plus the bucket's depth term (screening/stage_e_frozen.py:91-128, 278-280; stage_e_rules.py:338-345).

Verdicts: items 0, 1, 3, 5 VERIFIED; items 2, 4, 6 VERIFIED WITH NOTES; no DISCREPANCY.

### Item 0: the frozen files against the audited ones (VERIFIED)

- reports/stage_e_k5_member_freeze.json (sha256 1d0c974f18e884e1ad073d8f6f94d7bb70ee6f43971c7f23ccacab54103b3655,
  commit 09f1999) lists 13 files; each listed sha256 equals the file on disk, and the 11 module files'
  hashes equal my Part 1 table entry for entry (cp1 7681195b..., cp2 aa123ffe..., cp3 24f31961..., ovr
  d079967b..., preauc 0dcaeda8..., pmfix 4167234f..., fomc 0fb73eb1..., _calendar 8c23f8f1..., _releases
  9b183f14..., _event_common 3c1053d9..., _port_common 832cd2ef...; both __init__.py empty). Against
  reports/stage_e4_briefs/k5_files_pre_audit.sha256 exactly one file differs: tests/test_e4_k5_members_a.py
  (1f453149... -> 73636c95...), the R-K5-1 test fix; the other three test files are unchanged.
- The manifest's 11 members carry S0.2's labels, modules, factories and ordinals 1-11; the 11 records'
  member/ordinal pairs equal them; K5_research_cluster.json lists the same 11 in that order. Every record
  carries cluster_freeze_sha256 1d0c974f..., harness_sha256 82ae8536738ca43395f43356840c0b799a7925b7b75ddb4fc1353d3ab7491009,
  release_calendar_sha256 839f2437..., and the frozen tables costs f4360bb7..., epsilon 4e2c7731...,
  sizes 280d7e9d..., vehicles 1f1cafee...; the MGC bars file (429,238 rows, f6bcdd63...) and the MHG file
  (367,105 rows, 4c3deb8e...) are the same in every record that names them.

### Item 1: the screen from series.values (VERIFIED, 9 of 9; 2 records carry no screen)

| Trial | n | trips | mean ticks/ct/day | sd (pop) | t daily | passes | record agrees (1e-9) |
|---|---|---|---|---|---|---|---|
| K5-cp1-01 MGC | 295 | 284 | -0.603695 | 79.320453 | -0.130720 | no | yes |
| K5-cp2-01 MGC | 295 | 295 | +10.557017 | 200.218450 | +0.905624 | no | yes |
| K5-cp3-01 MGC | 295 | 101 | +8.494508 | 183.933455 | +0.793211 | no | yes |
| K5-cp3-01 MHG | 295 | 126 | +3.246753 | 80.211813 | +0.695219 | no | yes |
| K5-preauc-01 MGC | 295 | 280 | +1.305220 | 62.627375 | +0.357957 | no | yes |
| K5-pmfix-01 MGC | 295 | 278 | -9.989559 | 78.206306 | -2.193894 | no | yes |
| K5-fomc-01 MGC | 295 | 8 | +2.349831 | 21.864171 | +1.845927 | **yes** | yes |
| K5-ovr-01 MGC | 295 | 289 | -3.560780 | 185.067549 | -0.330465 | no | yes |
| K5-ovr-01 MHG | 295 | 190 | -3.397708 | 48.577621 | -1.201326 | no | yes |

For every run record: mean_ticks, sd_pop_ticks, t_daily and passes agree to 1e-9 relative (the largest
relative difference is 1.7e-16); n_days = len(values) = len(dates) = len(daily_net_usd) = window_dates.n =
295; n_trips agrees across series, screen, trade_rate and the trip list. The dates equal EC-CAL's 315
metals trade dates 2025-04-01..2026-06-19 less the record's own exclusions (18 roll-blackout dates, which
differ by vehicle: MGC 2025-05-28..30, 07-29..31, 11-25..27, 2026-01-28..30, 03-26..30, 05-27..29; MHG
2025-04-24..28, 06-25..27, 08-26..28, 11-24..26, 2026-02-24..26, 04-27..29; UR-1's 2026-06-18 and 06-19;
not_every_leg_trades empty), first 2025-04-01, last 2026-06-17; one value per date; every trip's trade
date is a window date; non-zero dates <= n_trips (equal for the one-trip-a-day members; ovr MGC 180 of
289 trips, MHG 134 of 190). series.values and daily_net_usd rebuild exactly from the trip lists under the
frozen definition (9 of 9). Each trip list's record_sha256 equals its record file's sha256 and names the
record file (11 of 11, the two excluded ones included). Power is not_run on all 9 (StartRuleMissing: no
frozen S_X for MGC / MHG); it does not enter a tier. The two coverage-excluded records carry screen None,
series None, power None, no engine section and 0 trips, as OC-H requires.

### Item 2: tiers against D5, the coverage check, the floor and OC-H (VERIFIED WITH NOTES)

OC-H (12:58 PDT 2026-09-25, reports/stage_e2b_task1_stats_worker.md:171-183; the STATE line 40 and the
harness review line 344 say the same): "D9, read literally: Coverage below 0.95 means 'excluded before
screening'. Mean hold below 10 minutes (floor (c)) means 'excluded before confirmation'. A breach of (a)
... or of (b) ... is excluded the same way. `tier` therefore takes the values 'A', 'B' or 'excluded'. An
excluded member stays in the record with its label(s) and belongs to neither Tier A nor Tier B. A
coverage-excluded member must have screen=None ... A member excluded for (a), (b) or (c) must carry its
computed ScreenResult ... The exclusion applies whatever the screen says." D9's floor text (docs
lines 592-599): "(c) mean holding time over the research window of at least 10 minutes ... (c) is checked at
screening, and a member failing it is excluded before confirmation with the reason logged."

Tiers, recomputed as OC-H from each record's labels and my item 1 screen: coverage label -> excluded;
another D9 label -> excluded; else A iff passes, else B. All 11 equal K5_research_cluster.json: Tier A
K5-fomc-01 MGC (mean 2.3498 > 0, t 1.8459 >= 1.0); Tier B cp1 MGC, cp2 MGC, cp3 MGC, cp3 MHG, preauc MGC,
ovr MGC, ovr MHG; excluded cp1 MHG, cp2 MHG, pmfix MGC. The cluster file's per-member screen dicts equal
the records' screens; not_tiered, refused_members and power_check_undefined are empty.

The two coverage exclusions (D9: "coverage of at least 0.95 on the research window for its vehicle";
screening/stage_e_align.py COVERAGE_MIN = 0.95, present / expected over the member's window dates and
declared intervals, cut to the calendar's session intervals):

| Trial | present | expected | ratio | expected, recomputed from the declared windows over its 295 window dates | why the window is thin |
|---|---|---|---|---|---|
| K5-cp1-01 MHG | 8,952 | 9,735 | 0.91957 | 9,735 = 295 x 33 (the 17:00 evening bar, the 07:39 bar, 11:29-12:00) | the MHG 17:00 CT bar and single minutes; cp3 MHG's [07:10, 12:00) passed at 0.95760 and ovr MHG's (07:10, 12:10) at 0.95592 |
| K5-cp2-01 MHG | 125,441 | 139,910 | 0.89658 | 139,910 = 295 x 478 less the halt-day cuts (13:30 halts 380, 11-28 395, 12-24 335, 07-04 290) | the window runs to 15:08 through the post-settlement hours (S0.12, the E.3-L-17 proxy) |

Both ratios are present / expected to 1e-12 and both are below 0.95, so the label and the "excluded before
screening" tier follow the frozen rule and OC-H. The expected counts of all 11 trials recompute exactly
(cp1 MGC 9,705; cp2 MGC 137,058; cp3 MGC 91,420; cp3 MHG 85,550; preauc 18,290; pmfix 8,260; fomc 4,981;
ovr MGC 106,085; ovr MHG 88,490). The present counts cannot be checked without the bar file (never
opened); the record's own numbers are taken as they stand.

The floor exclusion, K5-pmfix-01 MGC (label mean_holding_below_10min; runner floor_labels,
screening/stage_e_runner.py:262-265: mean hold < 10 -> label): the trip list has 278 trips, 277 with
hold_minutes exactly 10.0 (entry fill T_P + 2, exit fill T_P + 12, the rule) and one with 0.0: 2026-02-20,
entry fill 09:02 CT (T_P + 2 on a normal week, the rule's minute), close_reason mll_liquidation at the same
bar (open_ts = close_ts 15:02Z), gross -23,700 c, net -24,112 c (the day's value -241.12 ticks);
counters.mll_liquidation 1, accounts_started 2. Mean hold = 2,770 / 278 = 9.9640 < 10, so the label is
set; without that engine-closed trip the mean is 2,770 / 277 = 10.0 exactly and no label would apply.
min_hold_minutes 0.0 is that trip; min_hold_refusals 0 (the member never attempted an early exit) and
max entries per day 1, so floors (a) and (b) are untouched. The exclusion therefore follows the frozen
code and OC-H's words ("the exclusion applies whatever the screen says"), and rests entirely on one XFA
liquidation of a 10-minute rule. NOTES for the lead: (i) the reading of floor (c), whether an engine
liquidation counts toward "the member's mean holding time", is the lead's (Part 1's K5-L-09 expected an
engine-shortened hold to draw "a label, not a drop"; the runner docstring item 6 says a labelled member is
"screened and labelled, never dropped"; OC-H, which the code implements, says excluded before
confirmation); (ii) no verdict turns on it: pmfix fails the screen (mean -9.99, t -2.19) and would be
Tier B under either reading, so the only effect is that it sits in neither tier instead of on the null
side; (iii) the K5 label is the first floor exclusion of the program (K4 had none), so this is the first
time OC-H's clause has applied.

### Item 3: trips rebuilt from the frozen cost table, no replay (VERIFIED)

For K5-cp1-01 MGC (284 trips) and K5-pmfix-01 MGC (278), and for the other seven run trials as an
extra check (1,289 trips): every one of the 1,851 trips' net_cents equals gross_cents - 192 c x contracts
(MGC and MHG round turn $1.92) - slippage(open side) - slippage(close side) under the frozen rule above,
with tick values 100 c (MGC) and 125 c (MHG); contracts 1 on MGC and 2 on MHG throughout (q_c). The trip
list carries no side; every bucket a K5 fill landed in has equal buy and sell side ticks and depth, so
both side assignments match (0 side-determined, 0 unmatched). Event-window fills (a fill inside [release,
release + 30 min) of a release naming the root; the calendar names MGC and MHG only at CPI and NFP 07:30,
G.17 08:15 and FOMC 13:00): cp2 MGC 20 (18 entries at 07:36-07:52 on CPI and NFP days, 2 G.17-day
entries at 08:17 and 08:33), fomc 8 (both fills of every trip, 13:05 and 13:15, inside the FOMC window,
as Part 1 predicted), ovr MGC 5 (08:20 entries inside the G.17 window), all others 0, preauc and pmfix 0
(K5-L-04: no auction row exists). Daily sums equal daily_net_usd, and divided by contracts and the tick
value equal series.values, on every date (9 of 9). Gross P&L cannot be checked without prices;
everything else was.

### Item 4: trade counts, untraded events, fill minutes, ovr limits (VERIFIED WITH NOTES)

Event reconciliation (my event sets from the frozen tables, Part 1 section 3; halts and window dates from
EC-CAL; blackout and UR-1 dates from each record):

| Member | Events in window | Trips | Untraded | Explained | Silent (no intent, no counter) |
|---|---|---|---|---|---|
| K5-preauc-01 MGC | 307 AM auction days | 280 | 27 | 9 EC-CAL early halts (2025-06-19, 07-04, 09-01, 11-27, 11-28, 12-24, 2026-01-19, 02-16, 06-19), 17 MGC roll-blackout dates, 1 UR-1 date (2026-06-18); engine_not_a_window_date = 15 on the 18 blackout/UR-1 dates that are not halts | 3 blackout/UR-1 dates with no intent: a missing 03:59 bar (the member's S0.6 rule), not separable from the records; no other untraded event |
| K5-pmfix-01 MGC | 305 PM auction days (12-24 and 12-31 are not PM days) | 278 | 27 | 8 halts (the nine above less 12-24), 17 blackout dates, 1 UR-1 date; engine_not_a_window_date = 18 = every non-halt blackout/UR-1 event date | 1: 2025-07-24 (s = 0, or a missing 08:59 / 09:01 bar) |
| K5-fomc-01 MGC | 10 statement dates | 8 | 2 | 2025-07-30 and 2026-01-28, both MGC roll-blackout dates; engine_not_a_window_date = 1 | on one of the two blackout dates the member emitted nothing (s = 0 or a missing bar); no non-blackout event untraded |

No event member traded a date outside its set. Fill minutes, all 1,851 trips classified against the rule's
fill minutes (preauc T - 30 / T - 1 and pmfix T_P + 2 / T_P + 12 from the table's own instant per date,
so the 5-hour-week dates are checked at 05:00 / 05:29 and 10:02 / 10:12; fomc 13:05 / 13:15; cp1 12:00 /
12:29; cp3 07:21 / 12:29 and 07:11 / 11:59; ovr the :20 or :10 entry and + 59; cp2 an eligible entry
minute and 75 present bars): 1,821 exact (preauc 280 of 280, pmfix 277, fomc 8, cp1 283, cp2 293 entries
in [07:36, 11:43] with 75-bar holds, cp3 MGC 98, cp3 MHG 116, ovr MGC 287, ovr MHG 179); 7 engine MLL
liquidations (item 6); 1 D9.5a deferral (cp2 MGC 2026-03-16: the trigger bar 08:14, nominal fill 08:15 in
the G.17 guard, filled 08:17; counters.fill_guard_deferral = 1; the 75-bar count then ran from the fill,
exit 09:32); 22 fills one or more minutes late with no release nearby, consistent with a missing bar at
the nominal minute and not verifiable without the bar file: cp1 MGC and cp3 MGC exits on 2026-02-25 both
at 13:46 (nominal 12:28 / 12:29 fills, + 77 minutes: an MGC gap from 12:28 to 13:45 that day, inside the
114 missing minutes of cp2 MGC's coverage), cp3 MHG 8 exits at 12:00 (+ 1) and 2 entries at 07:12 (+ 1),
ovr MHG 10 exits + 1 to + 4 minutes (holds 60-63). No forced flatten, no price-limit exit, no locked
trip. Every exit closes the whole position (one trip per entry). ovr: at most 4 entries on any day (caps
5 on MGC, 4 on MHG), no overlapping trips, entries only at 08:20-12:20 / 08:10-11:10, no early-halt or
non-full-session date traded, holds 59 except the liquidations and the late MHG exits. cp1 MGC's 10
engine_flatten_window refusals are its 11:59 entries on the 10 halt days in its window (rules/sessions.py
sets F earlier than 12:00 on those days; the port follows D6 and does not test halts, C4). cp2 MGC
traded on 9 halt days (a port) and exited each by the 75-bar rule before F (latest halt-day exit 09:16).
cp3 and ovr traded no halt day (their rule). ovr MGC's account_not_active 3 and ovr MHG's 1 are the
engine's cancellations of orders after a liquidation, an engine matter. NOTES: (a) the 4 silent
no-trades above are the members' own rule conditions (S0.6, s = 0), which the records cannot distinguish
from a missing bar (the same note as K4's item 4); (b) the 2026-02-25 gap is worth a look by the lead in
the bar report, since it moved two ports' exits by 77 minutes.

### Item 5: program N (VERIFIED)

Records with status "run" and a screen: 9 (cp1 MGC, cp2 MGC, cp3 MGC, cp3 MHG, preauc MGC, pmfix MGC,
fomc MGC, ovr MGC, ovr MHG; pmfix is screened and labelled, so it counts). Excluded before screening, no
screen: 2 (cp1 MHG, cp2 MHG). Refused members: 0. No record shows a trial the freeze does not declare, and
every declared trial has a record (11 of 11). N = 114 + 9 = 123, the lead's figure. Whether the two
coverage-excluded trials count is the lead's decision; my reading: they do not. D5's words are "every
screened member and grid point adds to it", the D9 coverage rule says such a member "is excluded before
screening ... it is not run", and the two records hold no series, no screen and no trip, so no statistic
was computed and no selection on results could occur; a multiple-comparisons count of trials that yielded
nothing to compare would overstate the family. The conservative alternative (count every frozen
declaration) gives 125; if the lead takes it, the entry should say so, since the K4 session had no
excluded trial and set no precedent.

### Item 6: MLL liquidations (VERIFIED WITH NOTES)

accounts_started - 1 equals counters.mll_liquidation and the count of trips closed mll_liquidation on all 9
run trials: cp1 MGC 0, cp2 MGC 1 (2026-02-13, day value -306.10 ticks), cp3 MGC 2 (2025-10-22 -467.18,
2025-12-12 -792.12), cp3 MHG 0, preauc 0, pmfix 1 (2026-02-20 -241.12, the 0.0-minute trip of item 2),
fomc 0, ovr MGC 2 (2026-01-22 -441.09, 2026-03-23 -1,028.20), ovr MHG 1 (2025-10-10 -448.26): 7 in all,
no locked trip. The Tier A trial, K5-fomc-01 MGC, has none, so its tier cannot depend on them. NOTE: one
Tier B tier does. K5-cp3-01 MGC fails the screen at t +0.793; zeroing or dropping its two liquidation days
gives mean +12.76 / +12.85 and t +1.248 (passes), so without the XFA liquidations it would be Tier A. The
liquidations are the frozen harness's rule (the XFA MLL with a fresh account after each), so the record
stands; the lead may want to say so in the entry. The other Tier B trials keep their verdict: cp2 MGC
+0.906 -> +0.999 (still below 1.0), ovr MGC -0.330 -> +0.141, ovr MHG -1.201 -> -0.786, pmfix -2.194 ->
-2.045. Tier A sensitivity for the lead's verdict: fomc's 8 trade days (ticks per contract) are 2026-06-17
+318.4, 2026-04-29 +152.4, 2025-10-29 +99.4, 2025-12-10 +56.4, 2025-06-18 +44.4, 2025-05-07 +42.4,
2026-03-18 +12.4, 2025-09-17 -32.6 (7 positive, 1 negative); without its best day the screen still passes
(zeroed: mean 1.2705, t 1.8556; dropped: 1.2748, 1.8557; the sd falls faster than the mean), and with its
one losing day zeroed t is 1.9411. All 8 trips filled at 13:05 and 13:15 with hold 10.0; 8 non-zero days
of 295 (C12's low-frequency caveat; power not run for want of a frozen S_X).
