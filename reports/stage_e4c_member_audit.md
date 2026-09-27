# Stage E.4 Part 3 (K3 FX): member audit

Auditor: MemberAuditor-K3-FableXHigh (worker-xhigh, fable). Brief: reports/stage_e4_briefs/auditor_task3_K3.md.
I wrote none of the code, specs or tests. Read-only on the repository except this file and my scripts under
reports/stage_e4_briefs/audit_k3/ (recompute_tables.py and .out, mutation_probe.py and .out). Synthetic bars only; no
runner, no freeze written, no commit, no web. Times in PDT.

## Part 1: fidelity audit (Task 3)

### 0. Time, method, hashes

- Started 09:13, ended 09:33 (system clock, 2026-09-27).
- Sources read by section: catalog reports/stage_e0_catalog_K3.md (banner 1-7; C1-C12 62-234; the nine entries 237-855
  including the R-05 banner at 382 and the 01:40 narrowing at 481-482; section 7 1115-1177), docs/STAGE_E_DESIGN.md D6
  348-411 and D9 478-614, the specs (all), both coder reports, the contract (strategy/stage_e/_template.py, interface.py,
  screening/stage_e_rules.py forced_reasons / account_view / call_member / _opening_refusal / _exit_refusal,
  screening/stage_e_engine.py queue_forced / ask_member / step / fill_pending_at_open), the MES references (B-H1 lines
  135-182, Family H _mechanics.py docstring), E.3's K2 ports (diffed), rules/sessions.py day_rule, data/group_session.py
  early_halt_labels and assign_trade_dates, data/calendars/fx.py citations for the US holidays.
- The K3 test files were run at the audited hashes: `518 passed in 19.95s` (the nine tests/test_e4_k3_members*.py files,
  `env -u PYTHONPYCACHEPREFIX nice -n 10 uv run pytest -q -p no:cacheprovider`).
- The freeze static check passes on all 15 files of strategy/members/k3/ (my own call of
  screening.stage_e_freeze.check_member_source); the freeze script's dry run prints 30 declarations, ordinals 1-30 in the
  S0.2 order; every factory exists, is labelled `"<member id> <ROOT>"` and trades one leg `LegSpec(root, True)`.
- sha256 as audited (identical to the lead's reports/stage_e4_briefs/k3_files_pre_audit.sha256, all 24 lines):

| File | sha256 |
|---|---|
| strategy/members/k3/_calendar.py | 264fb1e123732eb8687f95a63f7fe445489ff47d7869b6b6d11a145b21f7e772 |
| strategy/members/k3/_clocks.py | eb679c0ecd3b0b7ec530e0baa52335701625a1fc6845dcee37631b04f1991c91 |
| strategy/members/k3/cp1.py | 6539cfd03d2cfbf9f634d666c94693821a3a0049696f66ba2e667dbc5dd018af |
| strategy/members/k3/cp2.py | 6551e9613d8b9f17fe2c5144dc6ea622e33dbe30eccf21198de78a8080fa0b80 |
| strategy/members/k3/cp3.py | b8d0b4c9a62b9973524c8f3e0d320fdb0fce5419a04da83b9bee56c184bb2432 |
| strategy/members/k3/ecbfix.py | 65102d77d244579f4f3d767edd14d606d34b73365dc09afaa8cdf9f624b3c68a |
| strategy/members/k3/_event_common.py | d7b5c6246cfc0609c08011393e13bd375ded2a5cf4bf4b3b65419c6ca98fc9b4 |
| strategy/members/k3/__init__.py | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 (0 bytes) |
| strategy/members/k3/ldnmom.py | 49bece90579ac6ed4d2417c525492d6e3a0d8557e79ed3ad40786e2247c88569 |
| strategy/members/k3/ldnrev.py | 56455c35b46483c14b882345b0fc5f99296d30a2d41fad9cab06cfc2dfe5620b |
| strategy/members/k3/mehedge.py | 81a6b2088fd0c712b05f28d3b7ee2fb6758bb711728514114cd3102b2e27d887 |
| strategy/members/k3/_mehedge_signal.py | b8cfa399cac9a0cc68298beb7c79891ee4f932bfd176d24cc386711fd03a24c8 |
| strategy/members/k3/_port_common.py | b4987d6028df07717075bbd8b909f29e6b8d1a4d0d738527617cb4dfb0c5c554 |
| strategy/members/k3/tkypost.py | 10e43cf820648a78d7f8df9e38d620e5004443fd7f89e88e4aeef90cba441c8e |
| strategy/members/k3/tkypre.py | 03a5a10914986cf5c7703d24182f85fe90665b6c73829fb947f5a195b4499bb4 |
| tests/test_e4_k3_members_a.py | 1101a0fa0f45150131507e922440ea7851d44ee0fdf1f007a6d3be28fed0a811 |
| tests/test_e4_k3_members_a_cp2.py | fa0115f50e848a5a4f231ce6a06a4170947df50d01eb1fad4ec9f25178f9c3b2 |
| tests/test_e4_k3_members_a_cp3.py | 98fcfa907183afda96e0ab47de8cefbfb4eb4a170eab0e88d7d438ab09fa6f0d |
| tests/test_e4_k3_members_b.py | c4445f2b782aefb2a7791e7b3a0c158c8b2a707cfd024ab45fb02e04c22ee0d8 |
| tests/test_e4_k3_members_b_ecb.py | 82631a0921271f79f4310d3cc1fa80a74bae7e23f98e075d52527a1fb4029087 |
| tests/test_e4_k3_members_b_ldn.py | b0f4baa017fb9a3171eeb4743b97294fb65907200793296fe1a4173ab444121d |
| tests/test_e4_k3_members_b_tky.py | e53397534055ca54e58a50ef89f7e260a7a7420290686664c4a1249ca5b0dc0c |
| tests/test_e4_k3_members_m.py | 63259150ad6c63baba15ca778a91c647a9327b9c4ed5f2e1a6b99b41da3f08f2 |
| tests/test_e4_k3_members_m_signal.py | 99e2ed997821d2e190b4d24a525218213be265fb652f73be2e3b11f1a330a594 |
| reports/stage_e4c_member_specs.md | c998d56c1c4ca9c6cf90988761543dc7ec39a3b732633c17a0afd5b157cd37a0 |
| reports/stage_e0_catalog_K3.md | 823b0d894715cf0b029175ba91178a4b321126e457eb8f3839bf789a20d16359 (equal to the E.1 freeze, per the CP2 buffer test) |
| reports/stage_e4c_release_check.json | c63c13a69559c90efdb72969e20244a261343839660436082fcaf44a35f931e9 |
| reports/stage_e4_briefs/write_k3_freeze.py | 85e8f0a4589a3c9f46a2067fc6294d3cd58c01bed1421a40997701285c5192a3 |

Verdict in one line: no BLOCKING finding. Every module implements its frozen entry and nothing more; every literal table
recomputes equal from its sources; two tests do not pin the bar field they claim (SHOULD FIX, tests only); the rest are
notes, the largest being the K3-L-11 harness inconsistency the lead already flagged, with two facts added below.

### 1. Per-member checklists (items 1-11)

Verdicts: OK = implements the frozen text; OK* = OK with a note (section 6). Line numbers are the files' own.

#### K3-cp1-01 (strategy/members/k3/cp1.py; 7 trials, ordinals 1-7)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Clock: signal = close of the O+29 = 07:49 bar minus open of the 17:00 CT bar of d-1; entry on the C-31 = 13:29 bar; exit at or after C-2 = 13:58; O and C from the frozen day_session_ct, never literals; CT only, unchanged in CST/CDT and the mismatch weeks | OK | cp1.py:51-54, 85-87 (shift from the frozen O/C); _port_common.py:61-66, 79-81; tests a.py:473-485 (six clock days) |
| 2 | Direction: s > 0 buys, s < 0 sells, 0 no trade | OK | cp1.py:98-108 |
| 3 | Exit on the first present bar at or after 13:58, fills next open; resent while refused; not duplicated while pending | OK | _port_common.py:93-105; tests a.py:524-541 |
| 4 | q_c from the frozen vehicle table (1 on all seven); exits close abs(position) | OK | _port_common.py:64-66, 104-105; cp1.py:136 |
| 5 | Tables | none (a port) | - |
| 6 | Availability: the 17:00 bar and the 07:49 bar are read after their close; the decision is at 13:29; no hindsight field, no future bar | OK | cp1.py:122-129 (captured on the bar itself, used at 130-136) |
| 7 | C4: none beyond D6 (the ports follow D6 as written, C line 49); D6's guard = the two signal bars share one instrument_id; the Globex-open bar missing = no trade (E.3-L-05) | OK | cp1.py:100-104; tests a.py:493-515 |
| 8 | Flatten and D9 floor: the member sends nothing after an engine close (pending suppresses; `_entered` blocks re-entry); windows (17:00-17:01 day -1), (07:49-07:50), (13:29-14:00) = S0.12 | OK | cp1.py:88-93, 120-121, 130-131; tests a.py:304-314, 569-583 |
| 9 | Nothing more: no filter, size rule or state beyond D6 | OK | whole file; AST-equal to strategy/members/k2/cp1.py except names (section 3) |
| 10 | Factories make_6e..make_6n, labels, ordinals 1-7; static check | OK | cp1.py:139-164; freeze dry run; tests a.py:279-283, 328-349 |
| 11 | Tests pin: entry/exit times, sign (the fixture separates close-open from close-close and open-open), missing Globex/signal/entry/exit bars, two ids, both clock regimes, D9.5a, synthetic F, D9.7 (test-only rules), roll blackout, reset per date | OK | a.py:456-611 |

#### K3-cp2-01 (cp2.py; ordinals 8-14)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | OR = present bars in [07:20, 07:35); eligible bars [07:35, 14:00); buffer 4 x vendor_tick = 0.0002 (6E, 6A, 6C, 6S, 6N), 0.0004 (6B), 0.000002 (6J), equal to the catalog table C 305-314; integer ticks | OK | cp2.py:55-58, 81, 112-126; tests a.py:400-421 (recomputed from the frozen catalog), a_cp2.py:50-59, 76-102 |
| 2 | close >= OR_high + 4 buys, <= OR_low - 4 sells | OK | cp2.py:120-126 |
| 3 | Exit on the 75th present bar with the position open (B-H1 lines 147-152), resent while refused, no C-2 exit; F cuts an entry filled after 13:53 | OK | cp2.py:88-97; tests a_cp2.py:61-67, 104-108, 118-142 |
| 4 | q_c from the table; exit closes abs(position) | OK | cp2.py:96, 128 |
| 5 | Tables | none | - |
| 6 | Availability: range bars closed before use; trigger bar's own close decides on that bar; hold counts bars already seen | OK | cp2.py:112-126 |
| 7 | C4: none beyond D6; no range instrument guard (D6 and B-H1 have none); a missing trigger bar is not a bar | OK | cp2.py:116-119; a_cp2.py:110-116, 183-188 |
| 8 | Window (07:20, 15:08) = S0.12; nothing after an engine close; one entry per date even when refused | OK | cp2.py:83, 106-107, 127; a_cp2.py:144-161, 219-226 |
| 9 | Nothing more | OK | AST-equal to k2/cp2.py except names and `__all__` |
| 10 | Factories, ordinals 8-14 | OK | cp2.py:131-160 |
| 11 | Tests pin the range end (a 14-minute range would sell at B-6), the 3/4-tick boundary both sides, the 75-bar count with a gap and with a deferred fill, no C-2 exit, no entry from 14:00, F at 13:53/13:52, 07:30 release inside the range, halts (engine F), reset | OK | a_cp2.py |

#### K3-cp3-01 (cp3.py; ordinals 15-21)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Daily bar of [07:20, 14:00) with C_d = the 13:59 close; entry on the 07:20 bar; exit at or after 13:58 | OK | cp3.py:60-61, 117-118, 141-152 |
| 2 | CLV >= 0.8 buys, <= 0.2 sells, non-strict, exact integer cross-products; Range > 0 | OK | cp3.py:75-88; tests a_cp3.py:101-110 |
| 3 | Exit first present bar at or after 13:58, resent while refused | OK | cp3.py:179-180 via exit_if_due |
| 4 | q_c; whole position | OK | cp3.py:187 |
| 5 | Tables | none | - |
| 6 | Availability: d-1 = the most recent COMPLETE earlier trade date, finalised only when a later trade date's bar arrives; day d's own bar never enters day d's decision | OK | cp3.py:123-139, 171-172; a_cp3.py:112-133 |
| 7 | Family H: complete day (07:20 and 13:59 bars, no halt label on CT date d, one instrument_id in [07:20, 14:00)); halt day d not traded (label read on the 07:20 bar = trade date d, K3-L-04 agrees with E.3-L-11 here); guard d-1's id = the 07:20 bar's; evening bars (CT date d-1) never enter | OK | cp3.py:142-143, 156-162, 175-176; a_cp3.py:135-177 |
| 8 | Window (07:20, 14:00); nothing after an engine close; one decision a day | OK | cp3.py:120, 181-183 |
| 9 | Nothing more | OK | AST-equal to k2/cp3.py except names |
| 10 | Factories, ordinals 15-21 | OK | cp3.py:190-215 |
| 11 | Tests pin the bar's bounds (07:10 and 14:15 extremes excluded, a 14:00 close ignored), exact cuts, warm-up, incomplete days dropped, the guard, missing 07:20 / 13:58 bars, halts on all five research dates and all seven roots, D9.5a, F, D9.7, the US-holiday observation | OK | a_cp3.py |

#### K3-ldnrev-01 (ldnrev.py; 6E, 6J, 6S; ordinals 22-24)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | T_L from the literal table (10:00, or 11:00 in the C9 weeks); signal bars T_L-11 and T_L-1 (R-05); entry on T_L+4 (fill T_L+5 = 10:05 / 11:05); exit on T_L+19 (fill 10:20 / 11:20); instants by exact UTC open on CT date d | OK | ldnrev.py:48-51, 66-79; _event_common.py:85-91 |
| 2 | M = close(T_L-1) - close(T_L-11) in ticks; M < 0 BUY, M > 0 SELL, 0 no trade (contrarian in the futures' quote, C 429-433) | OK | ldnrev.py:75-76 (CLOSE reads), 82-88 |
| 3 | Exit on the first present bar at or after T_L+19; resent while refused; suppressed only while an opposite-sign order is pending | OK | _event_common.py:115-127, 179-180 |
| 4 | q_c from the frozen table; exit abs(position) | OK | _event_common.py:150, 126-127, 193 |
| 5 | Event set = MONTH_ENDS rows in FX_FULL_SESSIONS and not in EW_BANK_HOLIDAYS; no shift (K3-L-06, C9 196-201); 80 dates, 13 in the research window (2025-11-28 halted) | OK | ldnrev.py:58-63; section 4 |
| 6 | Availability: both closes captured on their own bars, used at T_L+4; tables known in advance (section 4) | OK | _event_common.py:160-165, 177-178, 186-193 |
| 7 | C4: early halt or early F of trade date d from FX_FULL_SESSIONS (K3-L-04, K3-L-11); T_L-11, T_L-1 and T_L+4 carry one id (E.3-L-12); missing signal or entry bar = no trade (E.3-L-04) | OK | _event_common.py:181-189; b_ldn.py:149-164 |
| 8 | Windows (09:49, 10:21), (10:49, 11:21) = S0.12; nothing after an engine close; one entry chance per date | OK | ldnrev.py:52-53; _event_common.py:181-183 |
| 9 | Nothing more | OK | - |
| 10 | Factories make_6e/6j/6s; check_exposure refuses the others; ordinals 22-24 | OK | ldnrev.py:104, 116-125; b.py:558-570, 604-629 |
| 11 | Tests: entry/exit in both regimes, sign, R-05's T_L-11 vs T_L-16, halted and E&W month-ends not shifted, missing bars, guard, exit unguarded, D9.5a, F, D9.7, moved/dropped row. One test does not pin what it claims (S-1) | OK* | b_ldn.py:79-225 |

#### K3-ldnmom-01 (ldnmom.py; 6E, 6J; ordinals 25-26)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Signal bars T_L-15 (open) and T_L-13 (close, the entry decision bar); fill T_L-12 = 09:48 / 10:48; exit on T_L+4 (fill 10:05 / 11:05) | OK | ldnmom.py:49-51, 64-76 |
| 2 | S = close(T_L-13) - open(T_L-15); S > 0 BUY, S < 0 SELL, 0 no trade | OK | ldnmom.py:74 (OPEN then CLOSE), 79-85 |
| 3 | Exit as ldnrev | OK | _event_common.py:115-127 |
| 4 | q_c | OK | _event_common.py:150 |
| 5 | Event set = FX_FULL_SESSIONS minus EW_BANK_HOLIDAYS: 1,761 dates (298 research) | OK | ldnmom.py:58-61 |
| 6 | Availability: the entry decision bar's own close is read on that bar after its close (C1) | OK | _event_common.py:177-178 |
| 7 | C4 as ldnrev; guard T_L-15 and T_L-13 | OK | _event_common.py:186-189; b_ldn.py:276-293 |
| 8 | Windows (09:45, 10:06), (10:45, 11:06) | OK | ldnmom.py:52-53 |
| 9 | Nothing more (the 01:40 narrowing to 6E, 6J is in the frozen text, C 481-482) | OK | ldnmom.py:48 |
| 10 | Factories, ordinals 25-26 | OK | ldnmom.py:112-116 |
| 11 | Tests: times in both regimes, sign, E&W and early-F dates, missing bars, guard on 09:45 (and 09:46 unread), D9.5a, F, D9.7, moved/dropped. The field test pins the 09:45 open but not the 09:47 close (S-2) | OK* | b_ldn.py:229-323 |

#### K3-mehedge-01 (mehedge.py; 6J only; ordinal 27)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Entry on the T_L-61 bar of ME(m) exactly (fill T_L-60 = 09:00 / 10:00); exit first bar at or after T_L-4 (fill 09:57 / 10:57); T_L from the table | OK | mehedge.py:57-58, 93-99, 152-159 |
| 2 | SELL if R_eq > 0, BUY if R_eq < 0; 0 or None no trade | OK | mehedge.py:67-72 |
| 3 | Exit via exit_if_due (first present bar at or after; resent) | OK | mehedge.py:152-153 |
| 4 | q_c; whole position | OK | mehedge.py:159; _port_common.py:104-105 |
| 5 | Event set ME(m) in FX_FULL_SESSIONS and not E&W, with a signal row for the same ME date; R_eq table recomputed equal (section 4) | OK | mehedge.py:75-90 |
| 6 | Availability: P_a = last Nikkei close on a Tokyo date strictly before ME's calendar date (Tokyo closes about 32 hours before the 09:00 CT entry); P_b in month m-1; the ME-date Tokyo close excluded (C 594-596) | OK | _mehedge_signal.py rows; gen r_eq_row; m_signal.py:163-176 |
| 7 | C4 from FX_FULL_SESSIONS (K3-L-04/L-11); the only bar read before the entry is the T_L-61 bar (S0.9); missing entry bar = no trade; C10-style guard: ln of index closes, positive by construction, None/0 handled | OK | mehedge.py:67-72, 154-158 |
| 8 | Windows (08:59, 09:58), (09:59, 10:58) derived from T_L's two values = S0.12; nothing after an engine close | OK | mehedge.py:102-106, 152-153 |
| 9 | Nothing more; no 6E factory, no SX5E table (the entry's drop rule) | OK | mehedge.py:162-163; m_signal.py:193-197 |
| 10 | Factory make_6j, ordinal 27 (ordinals close up) | OK | m.py:119-139; freeze dry run |
| 11 | Tests: event set recomputed from EC-CAL, rules.sessions and the check's EC-EW; T_L by zoneinfo on every traded month-end; times in both regimes; halted, E&W, non-month-end dates; None/0/-0 and a row for another date; missing entry/exit bars; refused exit resent; D9.5a; F; D9.7; blackout; the table pinned against the saved files with a poisoning test for closes on/after ME | OK | m.py, m_signal.py |

#### K3-ecbfix-01 (ecbfix.py; 6E; ordinal 28)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Leg 1: intent on the 00:59 bar (fill 01:00), exit on T_E-1 (fill T_E = 07:15 / 08:15); leg 2: intent on the T_E bar (fill T_E+1), exit on 15:04 (fill 15:05); T_E from the table | OK | ecbfix.py:53-56, 78-91 |
| 2 | Leg 1 SELL, leg 2 BUY; legs told apart by the position's sign | OK | ecbfix.py:125-133, 149-156 |
| 3 | Each leg's exit on the first present bar at or after its named bar, resent while refused; a missing T_E-1 bar leaves leg 1 open at T_E, so no leg 2 (K3-L-05); a missing T_E bar: no leg 2; F 15:08 is leg 2's backstop | OK | ecbfix.py:125-133; b_ecb.py:144-178 |
| 4 | q_c from the table; exits abs(position) | OK | ecbfix.py:118, 151, 156 |
| 5 | Event set FX_FULL_SESSIONS minus TGT_CLOSING_DAYS: 1,780 (299 research) | OK | ecbfix.py:72-75 |
| 6 | Availability: no signal; each leg reads only its own entry bar | OK | ecbfix.py:149-156 |
| 7 | C4: early halt / early F from the table; a missing 00:59 bar excludes the date (no leg 2; K3-L-12); a refused leg 1 intent: no leg 2 (K3-L-12); an engine close of leg 1: no leg 2 (S0.7) | OK | ecbfix.py:149-156 (`_leg1_held and _leg1_exit_sent`); b_ecb.py:109-143, 186-203 |
| 8 | Window (00:59, 15:06); at most two entries, sequential, never while a position or a pending order exists | OK | ecbfix.py:57, 148-156; b_ecb.py:246-270 |
| 9 | Nothing more | OK | - |
| 10 | Factory make_6e, ordinal 28 | OK | ecbfix.py:160-161 |
| 11 | Tests: both legs at the spec minutes in three regimes, unconditional on prices, TARGET day, halt and early-F dates, K3-L-12 both ways, K3-L-05, missing fill bars, missing 15:04, real F 15:08, synthetic F on either leg, D9.7 on either leg, D9.5a at T_E and beside it, consecutive days, moved/dropped rows, direct calls | OK | b_ecb.py |

#### K3-tkypre-01 (tkypre.py; 6J; ordinal 29)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Entry on the 17:29 CT bar of calendar day d-1 (fill 17:30); exit on the T_T-1 bar of d-1 (fill T_T = 18:55 CST / 19:55 CDT); T_T from the table | OK | tkypre.py:46-47, 59-70 |
| 2 | SELL always | OK | tkypre.py:73-76 |
| 3 | Exit on the first present bar at or after T_T-1 | OK | _event_common.py:115-127 |
| 4 | q_c | OK | _event_common.py:150 |
| 5 | Event set GOTOBI_OR_TOKYO_MONTH_END in FX_FULL_SESSIONS: 378 (63 research); no shift | OK | tkypre.py:53-56 |
| 6 | Availability: no signal; the evening bars of d-1 carry trade date d in the real FX calendar (my probe of assign_trade_dates: 2025-06-04 17:29 and 19:55 -> 2025-06-05; Sunday 2025-03-09 -> 03-10; 2025-12-25 -> 12-26; 2025-08-31 -> 09-01; 2025-04-17 and 2025-12-24 evenings are closures) | OK | tkypre.py:66-70 |
| 7 | C4: the early-halt test is trade date d's, from the table, never the d-1 evening bar's label (K3-L-04); missing 17:29 bar = no trade | OK | tkypre.py:53-56; b_tky.py:112-125 |
| 8 | Window (17:29, 19:56) on day -1 | OK | tkypre.py:48 |
| 9 | Nothing more | OK | - |
| 10 | Factory make_6j, ordinal 29 | OK | tkypre.py:103-104 |
| 11 | Tests: CDT, CST, the spring-forward Sunday, three Tokyo month-ends, non-events (non-gotobi, holidays on the 5th and 15th, 2 Jan, 31 Dec), K3-L-04 both ways (2025-11-28 vs 2019-07-05), missing bars, D9.5a, F, D9.7, moved/dropped, consecutive dates | OK | b_tky.py:77-172 |

#### K3-tkypost-01 (tkypost.py; 6J; ordinal 30)

| # | Item | Verdict | Where |
|---|---|---|---|
| 1 | Entry on the T_T bar of d-1 (fill T_T+1 = 18:56 / 19:56); exit on the 00:59 bar of d (fill 01:00) | OK | tkypost.py:45, 57-67 |
| 2 | BUY always | OK | tkypost.py:70-73 |
| 3 | Exit first present bar at or after 00:59 | OK | _event_common.py:115-127 |
| 4 | q_c | OK | _event_common.py:150 |
| 5 | Event set TOKYO_BUSINESS_DAYS in FX_FULL_SESSIONS: 1,681 (284 research) | OK | tkypost.py:51-54 |
| 6 | Availability: no signal; trade-date labelling as tkypre (00:59 of d -> d, probed) | OK | tkypost.py:64-67 |
| 7 | C4 from the table (K3-L-04); missing T_T bar = no trade | OK | b_tky.py:201-214 |
| 8 | Window 18:55 on day -1 to 01:01 on day d (offsets -1, 0) | OK | tkypost.py:46 |
| 9 | Nothing more | OK | - |
| 10 | Factory make_6j, ordinal 30 | OK | tkypost.py:100-101 |
| 11 | Tests: CDT, CST, C9's 2025-11-04 known answer, the spring-forward Sunday, Tokyo holidays and 2 Jan, K3-L-04 both ways, missing bars, D9.5a, F, D9.7, moved/dropped, direct calls | OK | b_tky.py:174-266 |

### 2. The lead's readings (item 12)

Adopted from E.3 / K4 / K5 (each is the narrowest the text allows or is fixed by the cited reference; all applied unchanged):
- E.3-L-01 literal tables: fixed by the template's static check. E.3-L-03 "the bar at hh:mm" on CT date d: C1. E.3-L-04 exact
  entry bars: narrowest ("on the bar at" versus "at or after"). E.3-L-05 CP1's 17:00 bar: C 250-251. E.3-L-06 CP1's guard
  = D6's: D6 text. E.3-L-07 CP2's hold: fixed by B-H1 lines 147-152. E.3-L-08 range from present bars, no guard, one entry
  even if refused: D6 and B-H1. E.3-L-09/L-10/L-11 CP3 by Family H: fixed by _mechanics.py. E.3-L-12 guard on the bars read at
  or before the entry decision: narrowest reading of C4's "one signal computation or ... one position" (it adds the entry
  decision bar to ldnrev's "both bars", a date exclusion, so fewer trades). E.3-L-13 the entry bar = the decision bar: C2.
  E.3-L-17 windows, E.3-L-19 integer ticks, E.3-L-20 undersized 6C/6N screened (C6 keeps q_c = 1), E.3-L-22 a refused exit
  resent: all narrowest. K4-L-06 buffer = 4 x vendor_tick: equal to the catalog's table on all seven (recomputed by the test
  from the frozen catalog and by me). K4-L-13 tables span the calendar's coverage: narrowest. K5-L-02 zoneinfo instants as
  literal tables: C9's rule.

New K3 readings:
- K3-L-01 tables span 2019-04..2026-06: agree (K4-L-01 twin).
- K3-L-02 literal fix tables, no zoneinfo at run time: agree; verified (section 4; test b.py:535-546).
- K3-L-03 the guard covers the bars read at or before the entry decision; the exit is sent whatever the exit bar's id: agree;
  the engine raises before a position can span a splice (stage_e_engine.py step), so the case is unreachable in a run.
- K3-L-04 early halt from trade date d via the table: agree, and it is the only correct reading for tkypre/tkypost (a bar's
  early_halt_ct names its CT calendar date, data/group_session.py 583-590; the bar-label reading would keep 2025-07-04 and
  drop 2019-07-05, both wrong). Same answer as E.3-L-11 for the daytime members.
- K3-L-05 sequential legs; leg 1 still open or pending at T_E means no leg 2: agree (narrowest reading of "sequential, at
  most one position"; the alternative BUY at T_E would net against the pending exit, a trade the entry never names).
- K3-L-06 halted ME(m) in the table, month skipped, no shift: fixed by C9 196-201 ("do not trade in month m if ME(m) is
  excluded by C4"). Agree.
- K3-L-07 index not a leg; monthly literal table with closes before the entry: fixed by C 590-597 and the static check. Agree.
- K3-L-08 EC-JP as C9 defines it: fixed by C9. Agree; the year-end rule's check is in the release check (section 4).
- K3-L-09 section 7 settled: agree on items 1-10 and 12 (section 5); item 11 is not mentioned (N-4).
- K3-L-10 two coders: process only.
- K3-L-11 an FX date whose engine F is early is an early close for C4: this is a lead judgment, not the literal text. C4's
  own parenthesis defines the test as "Days with early_halt_ct set" and the D10 FX calendar does not set it on these 17
  dates; the literal reading would keep them (1,814 sessions instead of 1,797). The ruling is narrower (fewer trades), it
  removes trades the engine would truncate (ecbfix leg 2, and any member's exit after 11:30) or refuse, and it is applied
  uniformly by all five new members through one table. I accept it as a conservative reading and would take the same one,
  with two facts the ruling does not state (N-1): it binds only where rules/sessions.py carries Topstep's schedule (2024 on),
  and the ports are governed by the engine's F on the same dates (N-2).
- K3-L-12 no leg 2 unless leg 1 opened that date (missing 00:59 bar = C4 date exclusion; refused leg 1 = the pair never
  started): agree. The C4 half is the text's ("dates on which ... the entry bar is missing" excludes the date). The
  refused-intent half is the narrowest reading of "two legs, sequential"; in a run the refusals that can hit leg 1 at 00:59
  (window date, roll blackout, closure, inactive account) would refuse leg 2 as well, so the ruling changes a trade only
  under the D9.3 skip, which cannot arise at 01:00.

### 3. The ports against E.3's audited K2 ports; K3-L-04 and K3-L-11 (item 13)

`diff strategy/members/k2/{cp1,cp2,cp3,_port_common}.py strategy/members/k3/...`: the files differ only in docstrings and
comments, MEMBER_ID, the import path (k3), the exposure tuple ("6E", "6A", "6B", "6C", "6J", "6S", "6N") and its error text,
the seven factories and `__all__` (cp2's also exports BUFFER_TICKS and RANGE_MINUTES). No rule line differs; nothing is
imported from k2 (test a.py:386-397). E.3's audit notes on the K2 originals carry over unchanged (N-6).

K3-L-04: ruled above (agree). K3-L-11 and the inconsistency behind it: data/calendars/fx.py records the US holidays as
regular FX Globex sessions with an early settlement or none (for example the 2025-09-01 citation: "US holiday with regular
FX Globex hours: CME's FX halt is 16:00 CT ... no entry"), while rules/sessions.py's TOPSTEP_HOLIDAYS closes every product by
11:30 (2024-2025) or 11:45 (2026) on them, so the engine's F is early where the calendar marks nothing. The 17 dates
(2024-01-15 .. 2026-05-25, seven in the research window: 2025-05-26, 06-19, 09-01, 11-27, 2026-01-19, 02-16, 05-25) are the
same on all seven roots. The metals and rates calendars mark the same dates as halts, so K2 never met the case. Nothing in
the harness is changed by the members; the members read the engine's F only through the generated table.

### 4. Table recomputation (item 5)

All in my own code (reports/stage_e4_briefs/audit_k3/recompute_tables.py; output in recompute_tables.out), from the
sources, not from the generators:

| Table | Source used by me | My rows | Table rows | Equal | Notes |
|---|---|---|---|---|---|
| FX_FULL_SESSIONS | EC-CAL fx trade dates 2019-05-01..2026-06-19 (1,846), minus 32 early-halt dates, minus dates where rules.sessions.flatten_time_ct(root, d) != 15:08 for any of the seven roots | 1,797 | 1,797 | yes | research window: 316 trade dates, 5 halts, 7 early-F, 304 full sessions; F never differs across the seven roots |
| FX_EARLY_F_DATES | the removed dates | 17 | 17 | yes | listed in section 3 |
| MONTH_ENDS | last EC-CAL trade date of each month whose last day is inside the coverage | 85 | 85 | yes | 2019-05..2026-05; June 2026 excluded; halted MEs 2019-11-29, 2021-05-31, 2024-11-29, 2025-11-28 |
| EW_BANK_HOLIDAYS | data/vendor/release_pages/e4b/govuk_bank-holidays.json (sha256 538b3482...), division england-and-wales, 2019-04-01..2026-06-30 | 63 | 63 | yes | 12 in the research window; one-off holidays (2020-05-08, 2022-06-02/03, 2022-09-19, 2023-05-08) were announced before their dates |
| TGT_CLOSING_DAYS | the six-day rule 2019-2026 (computus) | 48 | 48 | yes | spot check on the saved pages: the starred 2025 rows of wb_20241230111431 and the starred 2026 rows of the live page equal the table's 2025 and 2026 rows (my regex found no starred rows on the 2025-12-18 capture's markup; the check reports it equal to the live page) |
| TOKYO_BUSINESS_DAYS | data/vendor/release_pages/e4c/cao_syukujitsu.csv (Shift_JIS, sha256 cec37a74..., 1,067 rows, 148 in 2019-2026) + weekdays, not 31 Dec-3 Jan, 2019-04-01..2026-06-19 | 1,761 | 1,761 | yes | |
| GOTOBI_OR_TOKYO_MONTH_END | day 5/10/15/20/25/30 or the last business day of a complete month | 404 | 404 | yes | 350 gotobi, 86 month-ends in range (June 2026 incomplete), 32 both |
| T_L | 16:00 Europe/London -> America/Chicago, weekdays 2019-04-01..2026-06-19 | 1,885 | 1,885 | yes | 11:00 CT weekdays = C9's list (125 in range); all nine C9 known answers pass |
| T_E | 14:15 Europe/Berlin -> CT | 1,885 | 1,885 | yes | 08:15 weekdays = the T_L 11:00 weekdays; both C9 known answers pass |
| T_T | 09:55 Asia/Tokyo on d -> CT, always on d-1 | 1,761 | 1,761 | yes | four C9 examples pass |
| MEHEDGE_R_EQ_6J | the four saved Nikkei files (sha256 equal to the table's, to the check's and to data/vendor/index_history/manifest.jsonl's served rows), Close column, overlaps checked (0 conflicts), closes in the window = the 1,761 Tokyo business days; P_a = last close strictly before ME, P_b = last close of m-1; Decimal ln, prec 34 | 85 | 85 | yes, exact floats | 0 None, 0 zero; P_a/P_b dates equal MEHEDGE_CLOSES_6J on all 85; 2024-04's P_a is 04-26 (04-29 Showa Day), as the rule requires |

Spot values (mine): 2025-04 ME 04-30, P_a 04-28 35839.99, P_b 03-31 35617.56, R_eq +0.006226; 2025-10 ME 10-31, P_a 10-30
51325.61, P_b 09-30 44932.63, +0.133026; 2026-03 ME 03-31, P_a 03-30 51885.85, P_b 02-27 58850.27, -0.125950.

Dropped EUR mehedge trial: the entry's rule (C 619-620) drops an exposure whose free daily history from 2019-04 cannot be
obtained. The 18 saved STOXX files hold 1,026 distinct dates (960 in the window); against weekdays minus TARGET days 889
are missing (257 in the research window), and for every research month-end from 2025-06-30 to 2026-05-29 the last saved
SX5E close is 2025-06-17, so 13 of the 14 research months have no P_a at all. The drop follows the rule as applied
(obtained = False, no substitute); it is logged in specs section 11 and named for the user. Trials: 30, not the banner's 31.

Event-set sizes from the tables (mine; equal to the coders' and the test's): ldnrev 80 (research 13), ldnmom 1,761 (298),
ecbfix 1,780 (299), tkypre 378 (63), tkypost 1,681 (284), mehedge 80 (13). Every event date has its clock row.

Evidence I could not re-read: the MURC TTM year-end files (data/vendor/release_pages/e4c/murc/*.xls) need xlrd, which is
not installed; the check's JSON records 1,868 TTM dates = 1,868 rule business days with zero mismatches (N-9).

### 5. Catalog section 7 as settled (item 14)

1 M6E/M6A: U7 keeps them out of D2; E.2a chose 6E and 6A; no member names a micro or E7 (tests pin no such factory). Follows.
2 Overnight coverage: the members declare S0.12 windows (tkypost's spans midnight at offsets -1/0); D9's check runs at
  screening. Follows (the runner's, not the members').
3 ldnmom's cost: the 01:40 narrowing to 6E and 6J is in the frozen text. Follows.
4 mehedge's sources: Nikkei obtained from the publisher (four captures, zero conflicts); SX5E not, trial dropped per the
  entry's rule; the blue-chip index judgment kept as frozen. Follows.
5 ecbfix's form: the headline two-leg trade as written; no substitution. Follows.
6 The three judgments (ME with the E&W drop; London members skip E&W days; EC-JP with 31 Dec-3 Jan and no shift): applied
  exactly (K3-L-06, K3-L-08; ldnmom.py:58-61). Follows.
7 Post-fix reversal: K3-020 not retrieved; ldnrev kept at 3 trials as frozen at E.1. Follows.
8 Cost sample without fix-event days: accepted as the K4 Q5 ruling did; a limitation for the verdict, not the code. Follows.
9 Ports vs release clocks: copied unchanged; D9.5a and D8 are the harness's (tests pin the 07:30 release inside CP2's range
  and CP1's 13:30 fill on an FOMC day meeting no guard). Follows.
10 Frequency: kept per Q4. Follows.
11 E.2 checks: (a), (b), (c), (i) done in the K3 check; (e), (h) moot; (f) FX is DCB-only under rules/price_limits.py's
  NO_LOCK_LIMIT reading, so D9.7 does not apply, consistent with C11 (the tests exercise the members' response with a
  test-only rules class); (g) at screening; (d) see N-4: confirmed for the research-window bars, no record found for the
  confirmation window. K3-L-09 does not mention this item.
12 Registry hygiene: not code. Follows.

### 6. Findings

BLOCKING: none.

SHOULD FIX (tests only; the code is right):
- S-1 tests/test_e4_k3_members_b_ldn.py:102-106 `test_ldnrev_signal_reads_closes_not_opens` does not pin closes: with the
  fixture (09:49 open -5 / close 0; 09:59 open 9 / close 1) the open-to-open move (+14) and the close-to-close move (+1)
  have the same sign, and the test passes with the member's reads mutated to OPEN (mutation_probe.out). Every other ldnrev
  scenario uses flat bars (rev_day, line 66-69: open = close), so no test separates the field. Smallest fix: make the two
  moves disagree, for example 09:49 (5, 5, -2, -2) and 09:59 (-4, 3, -4, 3): the code sells (closes rise) and an
  open-reading buys (probe verified).
- S-2 tests/test_e4_k3_members_b_ldn.py:242-247 `test_ldnmom_signal_is_the_open_of_t_l_minus_15_to_the_close_of_t_l_minus_13`
  pins the 09:45 open (a close-reading fails) but not the 09:47 close: with 09:47 = (8, 8, 1, 1) both open (8) and close (1)
  minus the 09:45 open (-3) are positive, and the test passes with the entry-bar read mutated to OPEN. Smallest fix: 09:47 =
  (8, 8, -6, -6), so close - open(09:45) = -3 sells while open - open(09:45) = +11 buys (probe verified).

NOTE:
- N-1 K3-L-11, two facts to record with the ruling. (a) The literal C4 test (early_halt_ct) keeps 1,814 sessions; the
  ruling keeps 1,797. (b) The second condition binds only where rules/sessions.py has Topstep's schedule (2024 on): 15
  US-holiday trade dates in 2019-07..2023 with no FX halt stay in FX_FULL_SESSIONS (2019-07-03, 2022-01-17, 02-21, 05-30,
  07-04, 09-05, 11-24, 2023-01-16, 02-20, 05-29, 06-19, 07-03, 07-04, 09-04, 11-23; 2019-2021's other US holidays carry FX
  halts and are excluded). On those 15 dates the engine's F is regular, so the confirmation-window simulation holds trades
  to their natural exits where a live Topstep account would have closed by 11:30 or 11:45. The research window is fully
  covered. A harness-coverage fact for the confirmation session (reports/stage_e2a_rules.md, rules/sessions.py), not a
  member defect; no fix inside the frozen entries.
- N-2 The ports on the same dates: CP2 and CP3 trade and are flattened by the engine at 11:30 / 11:45 (cp3 test
  a_cp3.py:234-246; cp2 a_cp2.py:228-236 for the halt dates), CP1's 13:29 entry is refused. This follows D6 ("or the engine's
  forced flatten at F if earlier") and E.3-L-11; the same dates are excluded for the five new members. Documented, no change.
- N-3 Data-gap case not pinned by any test: an entry fill deferred past the member's exit bar by missing bars (ldnrev: no
  bars 10:05-10:24) fills at the next present bar, the member's exit on that bar is refused by D9.3b (engine_min_hold),
  resent on the next bar and filled two minutes after the entry (probe: fills 10:25 sell, 10:27 buy). Consistent with "the
  first bar at or after" and with the engine's floor; report only.
- N-4 K3-L-09 is silent on section 7 item 11(d) (tick history 2019-05..2026-06; C7 says E.2 must confirm it before any bar
  is read because CP2's buffer is in ticks). reports/stage_e2a_bars.md records "raw off-tick prices 0" at the E.0 tick for
  every FX root on the research-window bars (lines 75, 90, 105, 120, 135, 150, 165), which confirms it for this screen. I
  found no equivalent record for the confirmation-window bars; the lead should name where it is, or have it checked before
  the confirmation session reads bars.
- N-5 tests/test_e4_k3_members_b_ldn.py:92-99 pins T_L-11 against T_L-16 but its "nor are the bars between" clause is not
  discriminated (a T_L-10 reading gives the same sides). Minor.
- N-6 Inherited E.3 notes apply to the K3 copies unchanged: the asdict idiom in two places (cp1.py:58-61,
  _event_common.py:99-103); cp2.py:58 `F_REGULAR_CT` literal used only as the window's end; `exit_items` (opposite-sign
  pending only) and `exit_if_due` (any pending) differ only for a same-sign pending order, unreachable; cp2's `_triggered`
  reset relies on the engine's F. No trade differs.
- N-7 tkypre.py:73-76 and tkypost.py:70-73 use `assert ticks == ()` in member code; unreachable with FixEvent's empty reads;
  cosmetic.
- N-8 TARGET 2026: the 2025-12-18 capture's markup did not match my starred-row regex; the live page's starred 2026 rows and
  the saved 2025 page's starred rows equal the table. The check reports the capture equal to the live page. Informational.
- N-9 Unverified by me: the MURC year-end evidence (xlrd missing here); the FRED Nikkei spot check (not saved, as the check
  says). Neither enters a research-window decision: the Nikkei closes used are the publisher's own file, checked across
  four captures.
- N-10 Trial count: the frozen banner's 31 assumed both index histories; 30 are declared and screened; the dropped 6E
  mehedge trial adds nothing to N (never screened). The lead's N accounting should say so.

## Part 2: recomputation (Task 6)
