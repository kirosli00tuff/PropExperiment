# Stage E.4 member audit, cluster K4 (MemberAuditor-K4-FableXHigh)

Worker file worker-xhigh, model fable, effort xhigh. Brief: reports/stage_e4_briefs/auditor_task3.md.
I wrote none of the code, specs or tests. Read-only except this file and my scripts under
reports/stage_e4_briefs/audit/ (recompute_tables.py, mutation_probe.py). Synthetic bars only; no
runner, no freeze, no commits, no web.

## Part 1: fidelity audit (Task 3)

Started 2026-09-27 04:12 PDT, ended 04:30 PDT.

Files as audited (sha256; every one matches reports/stage_e4_briefs/k4_files_pre_audit.sha256, the
lead's 04:12 record, and the coders' reports):

| File | sha256 |
|---|---|
| strategy/members/k4/__init__.py (0 bytes) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| strategy/members/k4/_port_common.py | 920a92a0769e236b58c42eeea0e76bfed4725cafd50ea22ce2972effc88790df |
| strategy/members/k4/_event_common.py | 9adadde84d2030404571f4963801d5a75000483af018260eab61692f6270c632 |
| strategy/members/k4/_calendar.py | a674e806169aec193dd920157289447132d6a848a252bc63b6d8efa8be763d78 |
| strategy/members/k4/_releases.py | 7c6eb13c27482fb56816bc4cb33bca7895541787715c6f3f2da4b9755559c3bf |
| strategy/members/k4/cp1.py | 6f310ba708991562e00ce5b974f89e33747447df0a16e37eb9134fa8512a6bba |
| strategy/members/k4/cp2.py | 5b81d670b167c40e4fea5a1b0bf741811e92e01e1dcbea0d4d734b64da6be3c1 |
| strategy/members/k4/cp3.py | cc9b17c12719fe6a4f0d24220a59758c64a90bed686c64401e0f4a5cf1e5fe7a |
| strategy/members/k4/ngpre.py | 1465ff3e098816897ea30a971266b922e0a391d08e8fb41d988e72b611241e90 |
| strategy/members/k4/apipre.py | d630f1c388a1740335e4dbfdcd599bd527acb711ad04fd2b1f4867d6e6a0644e |
| strategy/members/k4/eiafade.py | 8a78fa63c65a980ac8b4787de3ae2becd3bae43d94206f0f9f8d7a0db4e2f3bc |
| strategy/members/k4/eiamom.py | a3e02a4c5d09cd2412c7b94cd3417652d6332bf9c016f8dd48760e4838cd9e99 |
| strategy/members/k4/ovr.py | c221eada1cb67db2a1656b255980f67a03036c1a79972baa05e97884b0ce7494 |
| tests/test_e4_k4_members_a.py | 405e6f824abbeda9aab99e558835577ad9d61ffa39b8f4493f20b6d6df504296 |
| tests/test_e4_k4_members_a_ovr.py | 947ec504b79be0b17292c7212b684ece72980ce9081c3998c84f6ae34b495d56 |
| tests/test_e4_k4_members_b.py | af918d60b924eb7e238d33a768ca48f5bbc76a5df378d07aaf3c397a5731d6bf |
| tests/test_e4_k4_members_b_eia.py | 1d417ef9dcd8acfa244416d44cd5cfeb6fe502877df95b639970f33453192d0a |
| reports/stage_e4_member_specs.md | 464b527b50713ef01ec7196fb3ee03c33431a74d36243a6031746c8f7864c6d1 |
| reports/stage_e0_catalog_K4.md | 537acfb2e14a657a27fff3f3e8e7d50702713bc6ff58f9dca05b4953e2b3b8fd |
| reports/stage_e2b_release_calendar.json | 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8 (= brief) |
| reports/stage_e4_release_check.json | bb1b10719536f5c5bd35ee1d0f2da96e7bcd1c4750f6eb7f560b39f694537e24 (= brief) |
| data/calendars/energy.py | ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806 (= _calendar.py pin) |
| reports/stage_e4_briefs/write_k4_freeze.py | e54824b2a3ed160b9ae6177ac6e9432a33f51f34007e56ab95db5bf184fb6ba4 |

Checks run: `check_member_source(..., "K4")` passes on all 13 files under strategy/members/k4/;
`write_k4_freeze.py --dry-run` prints the 12 declarations, ordinals 1-12 in S0.2's order;
`nice -n 10 uv run pytest -q` on the four K4 test files: 236 passed in 3.17 s; my table
recomputation (audit/recompute_tables.py) and 31 in-memory mutation probes (audit/mutation_probe.py).

### Summary

Findings: 1 BLOCKING, 0 SHOULD FIX, 9 NOTE.

- BLOCKING B-1: DROPPED_WPSR 2025-07-16 rests on a mis-attributed Wayback capture. The saved file the
  check cites as "95 minutes after the scheduled time" was served from the 2025-07-15 04:43 UTC
  snapshot (manifest effective_url); the real 2025-07-16 16:04 UTC capture (saved under the "191212"
  retry name) already shows the July 16 release. Read correctly, the evidence gives no sign that the
  actual time differed from the schedule, so the row passes C9 like the 60 kept rows with
  time_basis "schedule". The literal table therefore drops one release the frozen entry keeps, for
  three trials (apipre, eiafade, eiamom). The verdict is the lead's (section 11, K4-L-15); I do not
  change it.
- The twelve modules implement their frozen entries and nothing more. Every literal, clock time,
  side, exit, size and guard checks out; the ports are line-for-line the E.3 K2 ports with the
  energy clock; the tables (apart from B-1's one verdict) equal my recomputation row for row.

### 1. Per-member checklists (items 1-11)

Legend: OK = as the frozen entry and the spec; file:line points at the code. "S" = specs section.

#### K4-cp1-01 (cp1.py; C 234-282; D6 line 364; S1)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Literals: O+29 = 08:29 signal, C-31 = 12:59 entry, C-2 = 13:28 exit, all as offsets from the frozen O/C; Globex open 17:00 CT of d-1 | OK | cp1.py:49-52, 83-85, 120 |
| 2 | Direction: buy if s > 0, sell if s < 0, s = close(08:29) - open(17:00 of d-1) in ticks; zero: no trade | OK | cp1.py:96-106 |
| 3 | Exit: first present bar at or after 13:28, resent while refused; no duplicate after an engine exit | OK | cp1.py:118-119; _port_common.py:92-104 |
| 4 | Size q_c from the frozen table; exit closes the whole position | OK | _port_common.py:65, 104; cp1.py:134 |
| 5 | Event sets: none read (release instants not read; D9.5a is the engine's) | OK | docstring line 16 |
| 6 | Availability: 17:00 bar read at its close, 08:29 at its close; entry decided at 12:59 close; no hindsight field, no account field beyond position/pending | OK | cp1.py:120-127; grep of hindsight/account fields: none |
| 7 | C4: ports carry D6's guard only (both signal bars present, one instrument_id); no early-halt test, as C line 85 | OK | cp1.py:98-102 |
| 8 | Flatten/D9: last fill 13:29; one entry; 29-minute hold; windows (17:00,17:01)@-1, (08:29,08:30), (12:59,13:30) = S0.12 | OK | cp1.py:87-91 |
| 9 | Nothing more: no filter, state = the two signal captures + entered flag | OK | cp1.py:74-77 |
| 10 | make_mcl/make_ng, name "K4-cp1-01 MCL"/"NG", one traded leg; freeze check passes; ordinals 1, 2 | OK | cp1.py:137-142; write_k4_freeze.py |
| 11 | Tests pin: entry/exit times (both roots, q_c 4/1), missing 17:00, 08:29, 12:59, 13:28 bars, two ids, zero signal, refused exit resent, D9.5a at 13:00 and next to it, synthetic F, engine D9.7 exit, early-halt day refused by the engine, consecutive days | OK | test_e4_k4_members_a.py:381-483 |

Diff against strategy/members/k2/cp1.py: docstring, comments, MEMBER_ID, the two factories and
`__all__` only; the rule body is identical.

#### K4-cp2-01 (cp2.py; C 283-342; D6 line 365; S2)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | OR = [O, O+15) = [08:00, 08:15); eligible [O+15, C); buffer 4 x vendor_tick = MCL 0.04, NG 0.004 (R-07, K4-L-06); hold 75 bars | OK | cp2.py:50-52, 76, 107-118; literals pinned test_a.py:496-499 |
| 2 | Direction: close >= OR_high + 4 ticks buys; <= OR_low - 4 ticks sells, integer ticks | OK | cp2.py:115-119 |
| 3 | Exit: 75th present bar with the position open after the entry decision bar (B-H1 lines 146-153 count), fill next open; NO C-2 exit; F is the engine's | OK | cp2.py:83-92, 101-102; test_a.py:524-527 |
| 4 | q_c from the frozen table; whole position | OK | cp2.py:88-92, 123 |
| 5 | Event sets: none | OK | |
| 6 | Availability: range from closed bars; entry on the bar's close; no hindsight field | OK | cp2.py:107-115 |
| 7 | C4: no guard beyond D6 (none); no early-halt test (port) | OK | docstring 6-7, 20 |
| 8 | Window (08:00, 15:08) = S0.12; one entry; latest fill 13:30 exits 14:45 | OK | cp2.py:53, 78; test_a.py:534-536 |
| 9 | Nothing more: `_triggered` uses the day's entry even when refused (E.3-L-08) | OK | cp2.py:122 |
| 10 | Factories, names, legs; ordinals 3, 4 | OK | cp2.py:126-131 |
| 11 | Tests: 75-bar hold both roots, exact buffer both sides both roots, missing bar in the hold, no C-2 exit, no entry from 13:30, 13:29 entry, F, refused entry uses the day, second trigger after exit ignored, no OR bar, range from present bars, evening/pre-O bars not range bars, deferred fill starts the count, D9.7, early-halt day flattened by the engine at 11:30, state reset | OK | test_a.py:496-602 |

Diff against k2/cp2.py: docstring, comments, MEMBER_ID, factories, `__all__` only.

#### K4-cp3-01 (cp3.py; C 343-382; D6 line 366; Family H; S3)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Daily bar over [08:00, 13:30) of CT date d: H/L over present bars, C_d = 13:29 close; entry on the 08:00 bar; exit C-2 = 13:28; cuts 0.8/0.2; lookback 1 | OK | cp3.py:54-58, 114-117, 138-149 |
| 2 | CLV >= 0.8 buys, <= 0.2 sells (non-strict), exact integer cross-products; Range > 0 | OK | cp3.py:72-85; 13-case test_a.py:635-641 |
| 3 | Exit: first present bar at or after 13:28, resent; no duplicate after engine exit | OK | cp3.py:176-177 |
| 4 | q_c; whole position | OK | cp3.py:184 |
| 5 | Event sets: none | OK | |
| 6 | Availability: d-1's bar finalised only when a bar of a later trade date arrives; day d decides on its 08:00 bar from d-1 only | OK | cp3.py:130-136, 151-160 |
| 7 | Family H: complete day = 08:00 and 13:29 bars exist, no bar of CT date d carries early_halt_ct, one instrument_id; incomplete days dropped; day d with early_halt_ct not traded; guard d-1 vs the 08:00 bar | OK | cp3.py:120-128, 139-140, 153-159 |
| 8 | Window (08:00, 13:30); one entry; last fill 13:29 | OK | cp3.py:117, 178-180 |
| 9 | Nothing more (O_d not read: it enters no condition) | OK | docstring 8 |
| 10 | Factories, names; ordinals 5, 6 | OK | cp3.py:187-192 |
| 11 | Tests: CLV 0.8/0.2 both roots with decoy bars outside [O, C), strictly-between cases, exact cuts, zero range, d-1 finalisation, most recent complete day, two-id day incomplete, guard, missing 08:00, early-halt day (engine would accept; the member blocks), missing 13:28, D9.5a, F, D9.7 | OK | test_a.py:605-717 |

Diff against k2/cp3.py: docstring, comments, MEMBER_ID, factories, `__all__` only.

#### K4-ngpre-01 (ngpre.py; C 384-439; S4)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Entry decision T-91 (fill T-90), exit decision T+29 (fill T+30), T from the NGS table (09:30 or 11:00 CT) | OK | ngpre.py:44-45, 53-57 |
| 2 | Side SELL always | OK | ngpre.py:43, 103 |
| 3 | Exit on the first present bar at or after T+29; resent; engine exits not duplicated | OK | ngpre.py:96-97; _event_common.py:67-79 |
| 4 | q_c NG = 1 from the frozen table; whole position | OK | ngpre.py:79 |
| 5 | Event set = NGS table rows (372 = 373 calendar rows less 2025-12-29), T = instant in CT: Thu 09:30 (355), Fri 09:30 (3), Wed 11:00 (14); no Monday row remains | OK | _releases.py:245-370; section 3 below |
| 6 | Availability: the only bar read before the entry is the entry bar; dates from a literal table | OK | ngpre.py:98-103 |
| 7 | C4: early halt on the entry bar; missing entry bar; instrument guard by construction; C10 n/a | OK | ngpre.py:98-102 |
| 8 | Windows (07:59, 10:01), (09:29, 11:31) = S0.12; hold 120 min; latest fill 11:30 | OK | ngpre.py:46-47 |
| 9 | Nothing more | OK | |
| 10 | make_ng only, name "K4-ngpre-01 NG"; ordinal 7; refuses MCL | OK | ngpre.py:106-107; test_b.py:412-414 |
| 11 | Tests: Thursday 07:59/09:59 decisions and 08:00/10:00 fills (qty 1), Wednesday 12:00 ET moves both to 09:29/11:29, Friday 10:30 ET, dropped and non-table dates, early halt, missing entry bar, missing T+29 bar, fill guard at T untouched, D9.5a at the entry fill, the frozen-calendar 09:30 WPSR guard on 2025-06-18 (fill 09:32), F, D9.7, consecutive releases | OK | test_b.py:429-534 |

#### K4-apipre-01 (apipre.py; C 514-587; S5)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Signal bars 15:24 and 15:39 of CT date W-1; entry 07:29 (fill 07:30); exit 09:28 (fill 09:29) | OK | apipre.py:52-55 |
| 2 | Side sign(R_API); R_API = ticks(close 15:39) - ticks(close 15:24); 0: no trade | OK | apipre.py:112-120, 155-157 |
| 3 | Exit first present bar at or after 09:28; resent; no duplicate | OK | apipre.py:146-147 |
| 4 | q_c MCL = 4 from the frozen table | OK | apipre.py:107 |
| 5 | Event set: standard WPSR rows (Wednesday 10:30 ET) with W-1 in ENERGY_FULL_SESSIONS, W-2 not in FEDERAL_MONDAY_HOLIDAYS, W not in API_DROPPED_WEEKS (empty); the API rows are not read (K4-L-04); 315 events in the table, 55 in the research window (56 with B-1 reversed) | OK | apipre.py:65-74; section 3 |
| 6 | Availability: the Tuesday closes are read at their closes (after F, 15:25/15:40 CT of W-1) and used on W only when W-1 + 1 day = the captured Tuesday; nothing forward-filled across weeks | OK | apipre.py:112-133, 142-145; test_b.py:645-652 |
| 7 | C4: early halt on W; 15:24, 15:39 and 07:29 bars present with one instrument_id; missing entry bar | OK | apipre.py:151-154 |
| 8 | Windows (15:24,15:25), (15:39,15:40), (07:29,09:30) at offset 0 (K4-L-07); flat before 09:30; hold 119 min | OK | apipre.py:57-59 |
| 9 | Nothing more: state = the two Tuesday captures | OK | apipre.py:96-100 |
| 10 | make_mcl only; ordinal 8; refuses NG | OK | apipre.py:161-162 |
| 11 | Tests: event set of the frozen tables (55 window weeks, 2019-05-01 out by K4-L-13, Thursday weeks out), buy/sell/zero, three-bar guard, missing bars, exit before the release with the guard untouched, missing 09:28 (09:29 exit, 09:30 fill moved to 09:32 by D9.5a), non-standard week, injected holiday-Monday week, Tuesday not full, api-dropped week, W early halt, signal used by the next calendar day only, F, D9.7, two consecutive weeks | OK | test_b.py:536-674 |

#### K4-eiafade-01 (eiafade.py; C 588-659; S6)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Base bar T_W-1, entry bar T_W+14 (fill T_W+15), threshold 0.005 = 1/200, filter T_W+15 <= 13:13, exit 13:28 (= C-2, pinned test_b.py:383-385) | OK | eiafade.py:49-54, 58-62 |
| 2 | BUY iff 200(t14 - t0) <= -t0; SELL iff 200(t14 - t0) >= t0; t0 > 0 (C10); exact integers (K4-L-05) | OK | eiafade.py:65-75 |
| 3 | Exit first present bar at or after 13:28; resent; no duplicate | OK | eiafade.py:122-123 |
| 4 | q_c 4 | OK | eiafade.py:100 |
| 5 | Event set: WPSR table rows with T_W + 15 <= 13:13 (all 368 rows qualify after the drops; the only row the filter would remove, 2025-12-29 16:00 CT, is also dropped) | OK | eiafade.py:58-62; section 3 |
| 6 | Availability: base captured at the T_W-1 close; decision at the T_W+14 close | OK | eiafade.py:120-121, 124-131 |
| 7 | C4: early halt, missing base or entry bar, one instrument_id over both; C10 guard | OK | eiafade.py:127-133, 68-69 |
| 8 | Window (09:29, 13:30); last fill 13:29; hold 224/194/134/74 min by slot | OK | eiafade.py:55 |
| 9 | Nothing more | OK | |
| 10 | make_mcl only; ordinal 9 | OK | eiafade.py:137-138 |
| 11 | Tests: exact-integer side rule incl. C10 cases, exactly -0.5 % buys (09:44 decision, 09:45 fill, qty 4), exactly +0.5 % sells, just inside no trade (3 cases), C10 through the engine (t0 = 0.00 and -1.00), every slot 09:30/10:00/11:00/12:00 enters at T_W+15 and exits 13:29, a moved release (2025-05-29, 11:00 CT) moves the decisions and the usual slot is ignored, dropped and non-table dates, the 13:13 bound on injected 12:58/12:59/16:00 rows, two ids, missing bars, early halt, missing 13:28, release guard at 09:30 untouched and a synthetic 09:45 release defers the entry, F, D9.7 | OK | test_b_eia.py:48-181 |

#### K4-eiamom-01 (eiamom.py; C 660-722; S7)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Signal bars 09:29 and 09:59; entry 14:29 (fill 14:30); exit 14:58 (fill 14:59) | OK | eiamom.py:48-51 |
| 2 | Side sign(r3), r3 = ticks(close 09:59) - ticks(close 09:29); 0: no trade | OK | eiamom.py:129-132 |
| 3 | Exit first present bar at or after 14:58; resent; no duplicate | OK | eiamom.py:117-118 |
| 4 | q_c 4 | OK | eiamom.py:92 |
| 5 | Event set: standard WPSR rows not in NYSE_NOT_FULL (314 in the table; the two standard Wednesdays removed are the NYSE early closes 2019-07-03 and 2024-07-03, outside both windows); early halt via the bar (EC-CAL) | OK | eiamom.py:59-64; section 3 |
| 6 | Availability: captures at the 09:29 and 09:59 closes; decision at the 14:29 close | OK | eiamom.py:113-116, 119-132 |
| 7 | C4: early halt, missing 09:29/09:59/14:29, one instrument_id over the three | OK | eiamom.py:122-128 |
| 8 | Windows (09:29,10:00), (14:29,15:00); last fill 14:59, 9 minutes before F; hold 29 min | OK | eiamom.py:52-53 |
| 9 | Nothing more | OK | |
| 10 | make_mcl only; ordinal 10 | OK | eiamom.py:135-136 |
| 11 | Tests: event set (drops 2019-07-03, 2024-07-03, the moved Thursday and the dropped week), buy/sell/zero (with a decoy 09:45 bar), injected NYSE_NOT_FULL date, non-standard and dropped weeks, early halt, three-bar guard, missing bars, missing 14:58, the 09:30 WPSR leaves the 14:30 fill alone and a synthetic 14:30 release defers it, F, D9.7, consecutive weeks | OK | test_b_eia.py:183-281 |

#### K4-ovr-01 (ovr.py; C 723-793; S8; F-7)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Decision times 09:00-13:00; signal open at t-60, close at t-1; entry on the bar at t-1 (fill t); exit t+58 (fill t+59); 20 reference dates; 80 values; deciles 10/90, numpy linear | OK | ovr.py:61-69, 124-126 |
| 2 | r <= P10 buys, r >= P90 sells; both (tie) or neither: no trade (K4-L-10); r = (tc - to)/to as a float from integer ticks; to > 0 | OK | ovr.py:83-98 |
| 3 | Exit first present bar at or after t+58; resent; after an engine exit no exit and no re-entry at that t, later t proceed | OK | ovr.py:188-191, 197; test_a_ovr.py:350-364 |
| 4 | q_c 4 / 1 | OK | ovr.py:198 |
| 5 | Reference dates = the 20 ENERGY_FULL_SESSIONS dates strictly before d (searchsorted); values r(tau) at the five t on those dates, each counted only with both bars, one instrument_id, open > 0; absent dates keep their slot (K4-L-08); values of every day are filed, traded or not | OK | ovr.py:72-80, 131-141, 143-152, 162-164, 186-187 |
| 6 | Availability: reference values come only from earlier trade dates (today's values are filed at the roll); the day's r(t) from the t-60 open and the t-1 close, both closed | OK | ovr.py:136-137, 180-187 |
| 7 | C4: early halt on the decision bar; per-t guard on the t-60 and t-1 bars (K4-L-14); missing bar: no trade at t; C10 on r(t) and on each reference value | OK | ovr.py:85-86, 150-151, 155-158 |
| 8 | Window (08:00, 14:00); at most 5 entries; 59-minute hold; entry only when flat with no pending order (positions never overlap, incl. a deferred or moved exit) | OK | ovr.py:70, 128, 192-193; test_a_ovr.py:174-180, 313-340 |
| 9 | Nothing more: warm-up (K4-L-09) and the fewer-than-20-table-dates rule (K4-L-13) are the lead's readings; state = opens, today's values, history, exit time | OK | ovr.py:159-161 |
| 10 | make_mcl/make_ng; ordinals 11, 12 | OK | ovr.py:201-206 |
| 11 | Tests: ladder cuts, reference dates (July 4 excluded, an early-halt d shares the next day's set, table start), hourly_return incl. C10, non-strict cuts and the tie, numpy linear vs lower/higher/nearest, entry/exit both roots with q_c, cut boundaries, five back-to-back trades, decoy prices for the t-60 open / t-1 close, warm-up (K4-L-09), fewer than 20 table dates (K4-L-13), early-halt dates not reference dates, early-halt trade date not traded (engine would accept), only the 20 most recent dates, exactly 80 vs 75 values, missing bars reduce the count (84 vs 79), roll-blackout reference date counts, two-id reference value not counted, earlier-contract values count (K4-L-14), day-d two ids block that t only, missing signal bars, missing exit bar moves the exit and skips the next t, D9.5a at t / next to t / on the exit, F, D9.7 (later t still trade; on the exit bar not duplicated), state across days, C10 direct calls | OK | test_a_ovr.py:106-392 |

Item 13 (F-7): energy-specific content of ovr.py beyond the decision clock: (a) the import of
ENERGY_FULL_SESSIONS (EC-CAL; K5 would import its own group's table), (b) `WINDOW_END_CT = 14:00`
(ovr.py:70), a literal that equals the last decision time + 60 and would differ on K5's clock, (c)
EXPOSURES ("MCL", "NG") through _port_common. The rule body (deciles over a 20-trade-date trailing
reference, entry on the bar at t-1, exit t+58 for a 59-minute hold, 80 values, tie rule) carries
nothing energy-specific. NOTE N-7.

### 2. The lead's readings (item 12) and F-7 (item 13)

Adopted E.3 readings (E.3-L-01, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 17, 19, 22): the K4 text
is the same as K2's for every one of them (the port texts are D6's, the C4 wording is identical);
adopting them is the narrowest consistent reading and the code implements each (checklists above).

| Reading | Verdict | Basis |
|---|---|---|
| K4-L-01 tables span 2019-05..2026-06, drops applied only in the research window | Agree, with the caveat the lead already states: confirmation-window rows are kept unchecked (C9's "passes C9's checks" is not yet true of them). The alternative, an empty table outside the research window, would force a re-freeze at confirmation anyway. NOTE N-8 | C 402, 608; K4-L-01 |
| K4-L-02 T = instant_utc in CT | Agree; verified on all 371 WPSR and 373 NGS rows: CT = ET - 1 h on every row, the CT date equals the row's date, and the slots are exactly the entries' enumerations (WPSR Wed 09:30 / Thu 10:00, 11:00 / Fri 10:00, 12:00; NGS Thu, Fri 09:30 / Wed 11:00) | C1 line 78 |
| K4-L-03 event sets are the table rows on dates with no early halt; eiafade's 13:13 filter in the member | Agree; no WPSR or NGS row falls on an EC-CAL early-halt date or a non-trade date (recomputed) | C 402-404, 608-610 |
| K4-L-04 apipre uses the rule, not the API rows; the Monday-holiday drop whatever the table says | Agree: C line 172-176 says "the rule only". The calendar's 48 API_WSB rows off Tuesday 16:30 ET (all Wednesdays of holiday weeks) never meet a standard WPSR week (no standard week 2019-2026 has a holiday Monday, recomputed), so API_DROPPED_WEEKS is empty by both routes | C 172-186 |
| K4-L-05 exact integer thresholds; ovr's float r with numpy linear | Agree; the algebra M <= -1/200 iff 200(t14 - t0) <= -t0 for t0 > 0 is exact; the entry names np.percentile | C 611-617, 753 |
| K4-L-06 buffer 4 x vendor_tick = R-07's | Agree (CL and MCL share 0.01; NG is the gas vehicle); both literals pinned | C 285; D 368-372 |
| K4-L-07 apipre's minutes at offset 0 | Agree; verified with screening.stage_e_align._expected_ranges on 2025-06-04: offset 0 counts (15:24, 15:25) and (15:39, 15:40) on the date, offset -1 counts nothing of the Tuesday (the session starts 17:00 of d-1). The declared minutes are a proxy measured on every date, as E.3 did | align.py:100-113 |
| K4-L-08 reference dates from EC-CAL; roll blackouts count; missing bars reduce the count | Agree: the text fixes the dates by EC-CAL and counts values separately | C 750-752 |
| K4-L-09 warm-up = all 20 reference dates on or after the first bar's trade date | Agree; it equals "the first 20 eligible dates of the window" when the window opens on a full session and is the stricter side otherwise | C 754-755 |
| K4-L-10 tie: no trade | Agree, narrowest | C 756-759 |
| K4-L-11, K4-L-12 | Agree; the dry-run prints the 12 declarations in that order | S0.2 |
| K4-L-13 ENERGY_FULL_SESSIONS = EC-CAL's coverage only | Agree, narrowest (listing a date the calendar does not cover would widen the rule); the table's last date is 2026-06-18 (06-19 is an early halt) | |
| K4-L-14 ovr's instrument check per computation | Agree: the entry's own text ("Every value whose two bars exist with one instrument_id counts") governs under C line 73 | C 751 |
| K4-L-15 the two stale-capture drops applied as recorded | **Disagree for 2025-07-16** (B-1): the capture the checker read as "95 minutes after the slot, still showing the previous release" is the 2025-07-15 04:43 UTC snapshot; the actual 2025-07-16 16:04 UTC capture shows the July 16 release. There is no evidence the actual time differed from the schedule, so C9's first rule does not fire; the row is in the same evidentiary state as the 60 kept rows with time_basis "schedule". I would keep it. **2026-05-28**: the manifest's effective_url matches the requested capture (16:37 UTC, 12:37 ET), it shows the previous week, and the next capture (18:14 UTC) shows the new one; a 37-minute-plus gap is evidence under C9's first rule if the capture is fresh, and the lead's cache caveat stands. The "We are delaying today's release ... Dec. 19" text on that page is inside an HTML comment present on every May 2026 capture, so it is neither a live notice nor evidence of a stale page. I would leave 2026-05-28 as the lead ruled, flagged | section 4 below |

Readings the spec takes without a K4-L number (all consistent with the frozen text):
- eiafade's event set includes the 12:00 CT slot (the entry's inequality governs its "covers the
  09:30, 10:00 and 11:00 CT slots" sentence). One such row exists, 2024-12-27 (Friday 13:00 ET),
  outside both windows. The spec's 74-minute hold follows. Agree.
- NGS rows with verdict "unverifiable" (2025-05-01, 05-29, 06-18) are kept and labelled. Neither C9
  drop rule fires on "no record obtained", so keeping them is C9's letter; the label carries the
  uncertainty. Agree (NOTE N-9).
- Early halts for the event members are read from the entry decision bar's early_halt_ct (S0.8,
  E.3-L-11); since data/bars.py labels every bar of the CT date, this equals "the date is an early
  halt".

### 3. Table recomputation (item 5; audit/recompute_tables.py, independent of gen_k4_*.py)

Sources: reports/stage_e2b_release_calendar.json (sha256 = pinned), reports/stage_e4_release_check.json
(sha256 = pinned), data/calendars/energy.py through load_group_calendar("energy") (sha256 = pinned).

| Table | Recomputed | Module | Difference |
|---|---|---|---|
| WPSR (date, T_W CT, weekday, standard) | 371 calendar rows 2019-05-01..2026-06-17 less 3 drops = 368; 316 standard; slots by weekday: Wed 09:30 (316), Thu 10:00 (40), Thu 11:00 (8), Fri 10:00 (3), Fri 12:00 (1) | 368, 316 standard | EQUAL row for row. Research window 61 rows, 55 standard. (With B-1 reversed: 369/317, window 62/56) |
| NGS (date, T_N CT) | 373 rows 2019-05-02..2026-06-18 less 1 drop = 372; Thu 09:30 (355), Fri 09:30 (3), Wed 11:00 (14) | 372 | EQUAL. Research window 63 rows; 11:00 CT rows in window 2025-06-18, 11-26, 12-31; Friday row 2025-11-14 |
| DROPPED_WPSR | check verdicts != keep: 2025-07-16, 2025-12-29, 2026-05-28 (all drop_actual_differs) | same 3 | EQUAL to the check; B-1 disputes the first verdict's evidence |
| DROPPED_NGS | check verdicts: updated 2025-12-29; unverifiable 2025-05-01, 05-29, 06-18 | DROPPED_NGS = (2025-12-29); NGS_UNVERIFIED_IN_WINDOW = the 3 | Drops = "updated" only; the 3 unverifiable non-keep verdicts are kept with the label, as section 11 rules (N-9) |
| API_DROPPED_WEEKS | 56 api_weeks; none with a holiday Monday, an API row off its Tuesday or off 16:30 ET | () | EQUAL. api_weeks' dates = the 56 standard Wednesdays of the window before drops |
| FEDERAL_MONDAY_HOLIDAYS | 47 entries, 46 distinct dates, all Mondays, 2019-05-27..2026-05-25 | 46 | EQUAL |
| NYSE_NOT_FULL | 69 full closures + 15 early closes (all 13:00 ET), no overlap, 84 dates 2019-05-27..2026-06-19; research window 13 + 3 | 84 | EQUAL |
| ENERGY_FULL_SESSIONS | trade_dates_between(2019-05-01, 2026-06-19) with early_halt_ct None: 1843 trade dates, 59 early halts, 1784 full sessions, 2019-05-01..2026-06-18; an independent is_trade_date walk over every calendar day gives the same list | 1784 | EQUAL, sorted, unique. Research-window early halts = the 11 the spec lists |
| Standard flag | Wednesday and 10:30 ET by instant_utc; identical by time_local; no Wednesday row at another time | | EQUAL |
| RESEARCH_CHECK_WINDOW | check window 2025-04-01..2026-06-19 | same | EQUAL |

Cross-checks the members rely on: no WPSR or NGS row is on a non-trade date or an early-halt date;
no WPSR row after the drops fails eiafade's 13:13 bound; apipre's event set is 315 (55 in the window;
the only standard row excluded by the Tuesday rule is 2019-05-01, K4-L-13; none by the holiday
rule); eiamom's is 314 (55 in the window). Section 11's counts (WPSR 61 keep / 3 drop; NGS 60 / 1 /
3; API 56 weeks; NYSE 69 + 15, 13 + 3; federal 47 rows, 46 dates) all reproduce.

### 4. The four drops against the saved pages (item 5)

All five cited files exist under data/vendor/release_pages/e4/ with the manifest's sha256; I grepped
each for its release-date strings and read the manifest's `effective_url` (the capture Wayback
actually served) and the CDX listings the checker saved.

| Drop | Evidence as cited | What the files say | Follows C9? |
|---|---|---|---|
| WPSR 2025-07-16 (Wed 10:30 ET, standard) | "capture 20250716160433 UTC, 95 min after the slot, still shows the previous release (week ending July 4); next capture 20250716191212 shows July 11" | CDX (cdx_wpsr_home_202504_202606.txt) lists exactly two captures around the date: 20250715044331 and 20250716160433. Manifest line 136: the request for 20250716160433 was served from effective_url **20250715044331** (the day before the release; digest 7EAS...) and saved as wpsr_home_20250716160433.html, which shows "Data for week ending July 4, 2025" as a 07-15 page must. Manifest line 184: the "retry" for 20250716191212, a timestamp that does not exist in CDX, was served from effective_url **20250716160433** (digest V6YX...) and saved as wpsr_home_20250716191212.html/.txt, which shows "Data for week ending July 11, 2025 Release Date: July 16, 2025". So the only post-slot capture that day (16:04 UTC = 12:04 ET) already carries the July 16 release; nothing shows the previous release after the slot | **No.** C9 drops a release whose actual date or time differs from its schedule entry. The date is confirmed by EIA's archive; no record of the clock time exists (the same state as the 60 kept rows with time_basis "schedule"). The drop rests on a mis-attributed file. See B-1 |
| WPSR 2025-12-29 (Mon; calendar 17:00 ET) | schedule row in the last capture before the release (20251228152631) read "Monday 10:30 a.m."; home page 20251229205315 carries "We are delaying today's release ..."; 20251229235027 shows the release | Confirmed: wpsr_sched_20251228152631.html carries the 10:30 a.m. row (effective_url matches); wpsr_home_20251229205315.html shows the Dec. 17 release plus the live delay notice; 20251229235027 shows Dec. 19 data | Yes: the actual time (after 15:53 ET) differs from the schedule entry knowable that morning (10:30 a.m.); first drop rule. No member trades it anyway (Monday, 16:00 CT) |
| WPSR 2026-05-28 (Thu 12:00 ET exception) | capture 20260528163711 (37 min after the slot) shows the previous release; 20260528181428 shows the new one | Confirmed: effective_url = requested for both; 163711 shows "week ending May 15, 2026", 181428 shows "May 22, 2026"; CDX has 150009, 163711, 181428 that day. The "delaying today's release ... Dec. 19" string is inside an HTML comment (`<!--div class="notice"...`) present on every May 2026 capture, so it is not a live notice | Yes, conditionally: if the 12:37 ET capture is fresh, the release appeared between 12:37 and 14:14 ET, at least 37 minutes off its 12:00 ET entry (first rule). The lead's caveat (a cached page cannot be ruled out; needs_lead_review = true) stands |
| NGS 2025-12-29 (Mon 12:00 ET "(Updated)") | the "(Updated)" row first appears in capture 20260126101407; the latest capture before it, 20251203063824, has no row | Confirmed: ngs_sched_20260126101407.html carries "December 29, 2025 - (Updated)"; the file cited for 20251203063824 is ngs_sched_20251128165312.html, and CDX shows the 20251128165312, 20251201233356, 20251202212951 and 20251203063824 captures share one digest (Q42ZBIS...), so the content is the same; that page lists December 31 but no December 29 row; no capture exists between 2025-12-03 and 2026-01-26 | Yes: second drop rule (no capture before the member's entry shows the update). The actual release (12:00 p.m., stated on ngs.html) equals the calendar's time, so the drop is about knowability, not a time change |

### 5. Tests (item 11)

- Result: 236 passed in 3.17 s on the four files (my run at 04:20, nice 10, no PYTHONPYCACHEPREFIX).
- The cases the stage prompt names are pinned for every member where they apply (entry and exit
  times with q_c; the event window through D9.5a at the fill and next to it; the flatten at a
  synthetic F; a missing bar at every decision time; a moved release for ngpre (Wednesday and
  Friday slots) and eiafade (2025-05-29); a dropped release for all four event members; the C10 guard
  for eiafade and ovr, both direct and through the engine; the engine's price_limit_exit for all
  eight). The four ports and ovr correctly have no moved/dropped-release case (they read no release
  instant).
- D9.7 cannot fire on MCL or NG in the real engine (DCB-only products), so every "D9.7" test uses a
  test-only rules subclass that queues a `price_limit_exit`; they pin the member's reaction to an
  engine-forced exit, which is what S0.7 requires of the member. NOTE N-3.
- No test passes vacuously. I checked each against what would happen under the wrong rule and
  ran 31 in-memory literal mutants (audit/mutation_probe.py): every mutant is killed by at least one
  test (ngpre side/entry/exit offsets; apipre signal end, entry, exit; eiafade threshold 1/199 and
  1/201, entry T+15, base T-2, the 13:13 bound, exit 13:29; eiamom signal end, entry, exit; cp1
  entry C-30, signal O+30, exit C-1; cp2 hold 74, buffer 3, range 16; cp3 cuts 0.81/0.19, close bar
  C-2; ovr exit t+59, 79 and 81 values, percentile nearest, low percentile 11, 19 reference dates,
  61-minute signal). Two mutants survive a single test I paired them with but die on another:
  eiafade base T-2 survives the exact-threshold engine test (all other bars sit at the base price)
  and dies on the missing-T_W-1 and two-id tests; eiafade 1/201 survives "just inside" (no integer
  tick move at base 7000 separates 1/200 from 1/201) and dies on the direct side-rule test.
- Not pinned, and unreachable in practice: cp2's `_hold_exit` resend after a refused exit
  (cp2.py:89-92); the 75-bar exit can never meet engine_min_hold. NOTE N-4.
- `test_a_none_bar_is_no_decision_and_changes_no_state` (both files) is a direct call the engine
  never makes for a one-leg member; it is not vacuous (state is compared) but pins nothing a run
  can reach.

### 6. Findings

**BLOCKING**

- **B-1. DROPPED_WPSR 2025-07-16 is not supported by its cited evidence, so the event tables (and
  through them K4-apipre-01, K4-eiafade-01 and K4-eiamom-01) exclude a release that C9 keeps.**
  Where: strategy/members/k4/_releases.py:29-33 (the entry); reports/stage_e4_release_check.json
  row WPSR-2025-07-16 (`home_page_probe.saved_path`, `release_time_bracket`, `verdict`);
  reports/stage_e4_release_check.md:18, 26, 448; reports/stage_e4_member_specs.md section 11 lines
  403-404 and K4-L-15 lines 431-437; data/vendor/release_pages/e4/manifest.jsonl lines 136 and 184.
  What is wrong: the manifest records that the request for Wayback capture 20250716160433 was
  served from 20250715044331 (effective_url), a snapshot from the day before the release, and that
  the "retry" 20250716191212 (no such capture in CDX) was served from 20250716160433. The checker
  read the 07-15 page as "95 minutes after the slot, still the previous release" and the true 07-16
  12:04 ET page as a later capture. Read correctly, the only post-slot capture shows the release
  already posted; there is no evidence of a delay, and C9's first rule ("actual date or time
  differs from its schedule entry") does not fire. The row's evidentiary state equals that of the
  60 rows kept with time_basis "schedule". Effect if left: one standard week fewer for apipre and
  eiamom and one release fewer for eiafade in the research window (55 instead of 56 events).
  Decision reserved for the lead (section 11 and K4-L-15 are lead rulings). Smallest fix inside
  the frozen entry, if the lead reverses the verdict: set WPSR-2025-07-16 to `keep` in the check
  JSON (reason: date confirmed by EIA's archive; time from schedule; the 20250716160433 capture,
  12:04 ET, shows the release) and correct its .md; update RELEASE_CHECK_SHA256 in _releases.py:26
  and CHECK_SHA256 in tests/test_e4_k4_members_b.py:69; remove 2025-07-16 from SECTION11_WPSR in
  reports/stage_e4_briefs/gen_k4_releases.py:54-58 and regenerate _releases.py (WPSR 369 rows, 317
  standard; window 62 / 56; docstring counts); update SECTION_11_WPSR_DROPS (test_b.py:236), the
  counts at test_b.py:273 and 277 (371 - 2; 62, 56), the apipre event-set test (test_b.py:547,
  551: 56), and DROPPED in tests/test_e4_k4_members_b_eia.py:34 (use 2025-12-29 or 2026-05-28);
  amend specs section 11 and K4-L-15. No member module changes. If the lead keeps the drop, K4-L-15
  and section 11 must state that 2025-07-16 is dropped without evidence of a delay (the capture
  cited does not exist as described), which is no longer a C9 drop.

**SHOULD FIX**

- None.

**NOTE**

- N-1. NGS 2025-12-29's `latest_prior_path` names ngs_sched_20251128165312.html for the capture
  20251203063824 (check JSON, updated_markers.ngs and the row). The CDX digests of the 11-28,
  12-01, 12-02 and 12-03 captures are identical, so the content is right; the path label is not.
  Documentation only; the verdict follows C9.
- N-2. ngpre meets the engine's D9.5a guard on Wednesday 12:00 ET storage days: the frozen
  calendar lists NG among the WPSR's products, so the T-90 entry fill at 09:30 CT on 2025-06-18,
  2025-11-26 and 2025-12-31 is moved to 09:32 (hold 118 minutes). The member decides on the T-91
  bar as the entry states; this is the harness's rule (specs section 0). Coder B's note 1; the
  return should list it beside CP1's FOMC case. Pinned by test_b.py:499-511.
- N-3. Every "D9.7" test uses a test-only `ForcedLimitRules` subclass because MCL and NG are
  DCB-only (rules.price_limits.HARD_LIMIT_PRODUCTS excludes them); the tests pin the member's
  reaction to an engine-forced `price_limit_exit`, not the price bands. Adequate for S0.7.
- N-4. cp2.py:89-92: the resend of a refused 75-bar exit is untested; the exit can never be refused
  for min-hold (75 bars after the fill) and any other refusal is the engine's own flatten path.
- N-5. ovr.py:70 `WINDOW_END_CT = time(14, 0)` is a literal that equals
  `shift(DECISION_TIMES_CT[-1], 60)`; it enters only the coverage window. Cosmetic; deriving it
  would make the module identical to K5's apart from the clock and the calendar table (F-7).
- N-6. apipre's Tuesday minutes are declared at offset 0 (K4-L-07) and are therefore measured on
  every research date, not only Tuesdays before standard Wednesdays; a coverage shortfall on other
  weekdays' 15:24/15:39 minutes would count against the member. Verified with
  screening.stage_e_align._expected_ranges (offset -1 would count nothing). The lead's reading; a
  proxy, as E.3-L-17.
- N-7. F-7 (item 13): ovr.py's energy-specific content is the decision clock, the ENERGY_FULL_SESSIONS
  import and N-5's literal; nothing in the rule body.
- N-8. K4-L-01: the 307 WPSR and 309 NGS rows before 2025-04-01 are kept unchecked (the check's
  updated_markers already show an NGS "(Updated)" row on 2025-01-08 whose earliest capture with
  the marker, 20250117233342, is after the release; it lies in neither window, so no run reads it).
  A Tier A event member's confirmation session must run the C9 checks on 2019-05..2024-02 before
  its confirmation run, as the spec says.
- N-9. Three NGS rows are kept with verdict "unverifiable" (2025-05-01, 05-29, 06-18). Neither C9
  drop rule fires on "no record obtained", so keeping them is C9's letter; the "calendar partly
  unverified" label on K4-ngpre-01 NG carries it into the return.

Non-findings worth recording: no member reads a hindsight field, `in_flatten_window`,
`in_no_new_positions_window`, `is_roll_session`, `gap_before_minutes`, `raw_symbol`, `volume`, or any
account field beyond `position`/`positions` and `pending` (grep over strategy/members/k4/*.py); no
member reads a bar before its close or a future bar; no RB or HO factory exists (pinned by
test_a.py:265 and test_b.py:364); q_c is never a literal; every clock time of the ports is an
offset from the frozen O/C; the freeze static check passes on all 13 files; the dry-run's 12
declarations match S0.2 and the coders' tmp_path freezes.

## Part 2: recomputation (Task 6)

