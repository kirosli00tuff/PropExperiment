# Stage E.8, K6 member audit

Auditor: MemberAuditor-K6-FableXHigh (worker-xhigh, fable, xhigh). Brief: reports/stage_e8_briefs/auditor_task3_K6.md.
The auditor wrote none of the code, specs or tests. Read-only on the repository except this report and the
scripts under reports/stage_e8_briefs/audit_k6/. No bar file was opened, the runner was not run, no freeze was
written, no web.

## Part 1: fidelity audit (Task 3)

Started 2026-10-01 01:28 PDT. Ended 01:56 PDT.

### 0. Files as audited (sha256), method, incident

All 21 entries of reports/stage_e8_briefs/k6_files_pre_audit.sha256 verified at the start (`sha256sum -c`: 21 OK)
and again at the end (01:56 PDT: 21 OK, no mismatch; `git status --short strategy tests` shows no tracked change; holdout all_ok true, unlocks_logged 0). The files audited are therefore exactly:

| File | sha256 |
|---|---|
| strategy/members/k6/_calendar.py | 1d143c605dfaf6187619a0be1c8fa0c45446dfe9946e628db7628f8f441cc123 |
| strategy/members/k6/cp1.py | 250b615c0d08e7c16fcf3d27800f24c68c548ea5484da420c1f8ae112bb1748e |
| strategy/members/k6/cp2.py | fc25ff092bef1d7a8a8333ad027c9ff4c1be7e02c089aa8922142bc5afded001 |
| strategy/members/k6/cp3.py | cfb9b6672505fef3a036655f9c549370e292510cf6993bac075ad599008b2411 |
| strategy/members/k6/crushgap.py | 339a5ed7fcac3dbb30ce77d63b2f6746ad6c0b8059dd8d73bf5f90ab520839fb |
| strategy/members/k6/_event_common.py | 31e3fbf4dadc27e082b440ee1283f20d09bf134d2de327967156d8b09acb5cc4 |
| strategy/members/k6/__init__.py (0 bytes) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| strategy/members/k6/limitcont.py | 9b142644bc4f429089a5524851ecc52c2f109ac8e5e0e3004e2a459a88507c97 |
| strategy/members/k6/_limits.py | aa2dee3dd9df8ea83cf9a2b5444be55758e862d4bbd4500fb88d6fab3fc8629c |
| strategy/members/k6/_port_common.py | b37d068267619e1bb437197a8d36be33c875f255c097605fd1305de6035d79ff |
| strategy/members/k6/wasdepost.py | 75f6704db77bbbe449f801b5cabe8548e40c69e406fc5f2ea974f813764bd4d2 |
| strategy/members/k6/wasdepre.py | 4708688aac9e3d4051454a6aa884f15d91b512fa5aa752b6e83d21c46f270849 |
| strategy/members/k6/_wasde.py | d8f8e32407d45d9d0a6eb96b262b417b80d3476cea26c7a532f0279777be9332 |
| tests/test_k6_members_crushgap.py | b6112559407449e7939a0ebc82c1da95603b56c1abe86233d4d68480d7523574 |
| tests/test_k6_members_limitcont.py | e95d5658719e50b4068feb90201aec7e3f74a73478493988485d1def459b9fc3 |
| tests/test_k6_members_ports_cp2.py | 43f6233f4faa1a339bd2001ce15f7d902d5038d8c40c409f81f4df412fa55769 |
| tests/test_k6_members_ports_cp3.py | a3648c212c0cc5c2717fc2826b6b9b2057d27f7935c82efc3d53656da030e96b |
| tests/test_k6_members_ports.py | b0017f38a82b19daa5b900f06618007233a6d688b1322521cf4fc14d145df37c |
| tests/test_k6_members_tables.py | 4a58cef6e01ca1ebb50d6d5b0d1ce9c07144dedb0a434168b694197027594720 |
| tests/test_k6_members_wasde.py | 7be91fdec79768c135812118e62ec0151b7daabf79339b50b42c6bd1944ce518 |
| reports/stage_e8_briefs/gen_k6_tables.py | 1aa4d3695373f28602cb0aa133014a1281b6eab925e4f3afda66c102c4963af6 |

Method. (1) The frozen entries (reports/stage_e0_catalog_K6.md banner, header, C1-C13, the seven member sections,
section 7), the E.0 01:52 rulings (reports/stage_e0_STATE.md line 70), D5/D6/D9, the template and interface, the
engine's refusals, forced exits and settlement tracker (screening/stage_e_rules.py, stage_e_engine.py),
rules/price_limits.py, the MES references (_mechanics.py, h6, B-H1 lines 135-182) and the K1 ports were read by
section and every K6 module and its K1 counterpart were diffed. (2) Every table was recomputed from its sources
by the auditor's own code (audit_k6/recompute_tables.py). (3) The member's settlement proxy was compared with the
engine's `_Settlement` on synthetic bars (audit_k6/proxy_compare.py). (4) Five engine probes on synthetic bars
(audit_k6/probes.py). (5) The seven test files were run as-is (630 passed, 17.6 s) and then 102 auditor
mutants were run against an out-of-tree copy of the code (audit_k6/mutants.py, results in audit_k6/mutants.jsonl
and mutants_pass2.jsonl). (6) Static check: `check_member_source` reports 0 problems on all 13 files;
`write_k6_freeze.py --dry-run` prints the 27 declarations of specs S0.2 in order with the right factories and
legs; `python -m data.holdout status`: all_ok true, unlocks_logged 0 (start and end).

Incident (noted at the lead's request). The auditor's first rsync for the out-of-tree copy excluded only
`data/processed*` and so descended into `data/vendor` (raw Databento files), filling the RAM-backed scratchpad
quota; the lead deleted that partial `data/` copy. No repository file was touched (the pre-audit hashes verify
at the end). The copy was redone with code, data/calendars, data/*.py, tests and the six JSON inputs the tests
read (16 MB); it is deleted at the end of Part 1. No bar file was opened by any script.

### 1. Per-member checklist (brief items 1-12)

Legend: OK = implements the frozen entry as the specs read it; file:line is the code audited. "engine" = the
behaviour is the engine's by the specs' list of what a member does not implement.

#### 1.1 K6-cp1-01 (cp1.py, _port_common.py), 7 trials

| Item | Verdict | Where |
|---|---|---|
| 1 Literals and clock | OK. O, C from `load_frozen_tables().day_session_ct` (_port_common.py:80-82); signal bar O+29 = 08:59 (cp1.py:60, 93); entry C-31 = 12:44 / 12:29 (61, 94); exit C-2 = 13:13 / 12:58 (62, 95); grain first bar at or after 19:00 CT on d-1 (59, 111-117); livestock first bar 08:30 exactly (117) | cp1.py:59-62, 89-117 |
| 2 Direction | OK. s = close(08:59) - open(first) in ticks; buy if s > 0, sell if s < 0, zero no trade | cp1.py:119-129 |
| 3 Exits | OK. First present bar of CT date d at or after C-2 while the position is non-zero and nothing pending; resent after a refusal; nothing after an engine closure (position 0, `_entered` True) | _port_common.py:109-121; cp1.py:141-142, 151-153 |
| 4 Sizing | OK. `self._leg.q` = vehicles[root].q_c (1); exits send `abs(position)` | cp1.py:157; _port_common.py:82, 120-121 |
| 5 Tables | none read | - |
| 6 Availability | OK. First-bar open recorded on that bar; 08:59 close on that bar; the entry decision at 12:44 reads only those. Fields read: open, close, instrument_id, trade_date, ts_event_ns | cp1.py:143-157 |
| 7 Trade dates | OK. Bars identified by CT date and clock; the evening bar (CT d-1) is the first bar through `bar.trade_date == d` and the instant test; signal and entry bars on CT date d only (146-147); late-open date: the earliest bar of d (see K6-L-01 ruling, finding N-1) | cp1.py:111-117, 136-147 |
| 8 C4 | OK. No C4 guard beyond D6's (both signal bars present, one instrument_id) | cp1.py:121-125 |
| 9 Flatten and D9 floor | OK. No exit before C-2 (hold 29 min > 2 min); the F flatten and D9.7 exit leave a flat account and the member sends nothing more (tests `test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry`, `..._synthetic_f_...`); trading_windows = S0.12 (verified for all 7 roots); the day -1 (19:00, 19:01) interval is clipped by the coverage check to the calendar's open sessions, so a late open costs no coverage | cp1.py:96-106; screening/stage_e_align.py:100-112 |
| 10 Nothing more | OK. One entry decision per date (`_entered`), no filter, no size rule | cp1.py:151-157 |
| 11 Factories, names, legs | OK. make_zc..make_le, name = label, one traded leg; ordinals 1-7 in the freeze dry run | cp1.py:160-185 |
| 12 Tests | OK. 13/13 auditor mutants killed (section 5); the stage prompt's cases are pinned (entry/exit fills per group, missing 08:59 / entry / exit bars, synthetic F, real D9.7 exit, halt day, Monday/Tuesday-after-holiday first bar) | tests/test_k6_members_ports.py:531-833 |

#### 1.2 K6-cp2-01 (cp2.py), 7 trials

| Item | Verdict | Where |
|---|---|---|
| 1 Literals and clock | OK. OR = present bars opening in [O, O+15) of CT date d (59, 86, 118-121); eligible [O+15, C) (124); buffer 4 x vendor_tick compared in integer ticks (60, 126-130): ZC/ZW/ZS 1.00 c/bu, ZM 0.40, ZL 0.04 c/lb, HE/LE 0.100 c/lb = C7's 0.01 USD/bu, 0.40, 0.0004 USD/lb, 0.001 USD/lb; hold 75 present bars (61, 94-103) | cp2.py:59-63, 118-134 |
| 2 Direction | OK. close >= OR_high + 4 ticks buys, <= OR_low - 4 ticks sells (non-strict) | cp2.py:127-130 |
| 3 Exits | OK. The 75th present bar after the entry-intent bar (fill at the 76th open = fill + 75 min), as B-H1 counts (h1 lines 146-151); no C-2 exit; F is the engine's; resent while refused; nothing after an engine closure | cp2.py:94-103, 112-113 |
| 4 Sizing | OK. q_c; exits `abs(position)` | cp2.py:103, 134 |
| 5 Tables | none read; F_REGULAR_CT is a literal per group used only for trading_windows (finding N-3) | cp2.py:63, 88-89 |
| 6 Availability | OK. Range from closed bars; the trigger reads the current bar's close | cp2.py:118-130 |
| 7 Trade dates | OK. Grain evening and overnight bars (CT date d-1, or before 08:30) never enter the range (115-116) | cp2.py:114-118 |
| 8 C4 | OK. No instrument guard, no minimum bar count (D6/B-H1 have none; E.3-L-08) | cp2.py:122-123 |
| 9 Flatten and D9 floor | OK. The late-fill D9.3 skip and the fill guard are the engine's (admit_fill); trading_windows [O, F) = S0.12 | cp2.py:88-89 |
| 10 Nothing more | OK. `_triggered` consumes the day's entry even when refused (E.3-L-08) | cp2.py:133 |
| 11 Factories | OK. Ordinals 8-14 | cp2.py:137-162 |
| 12 Tests | OK. 12/12 mutants killed; literal mutants also killed by behavioural tests in the second pass (section 5) | tests/test_k6_members_ports_cp2.py |

#### 1.3 K6-cp3-01 (cp3.py), 7 trials

| Item | Verdict | Where |
|---|---|---|
| 1 Literals and clock | OK. Daily bar over [O, C) of CT date d (150), C_d = close at C-1 = 13:14 / 12:59 (66, 123, 157-158), entry on the O bar (187), exit first bar at or after C-2 (67, 124, 185-186), CLV cuts 0.8 / 0.2 as exact integer cross-products (64-65, 81-94) | cp3.py:64-67, 81-94, 147-158 |
| 2 Direction | OK. CLV >= 0.8 buys, <= 0.2 sells, range > 0 | cp3.py:84-94 |
| 3 Exits | OK. As CP1 (exit_if_due) | cp3.py:185-186 |
| 4 Sizing | OK | cp3.py:193 |
| 5 Tables | none (Family H's bar test, K6-L-18) | - |
| 6 Availability | OK. The daily bar of d is finalised in `_roll` when a later trade date's bar arrives; day d's decision reads `_prior` only (complete bars of earlier dates) | cp3.py:139-145, 160-169 |
| 7 Trade dates | OK. Evening bars never part of a daily bar (181-182); an early-halt d (bar label) is not traded and is incomplete; d-1 = most recent complete day (E.3-L-09) | cp3.py:129-137, 162-163, 181-182 |
| 8 C4 | OK. Family H's complete-day and instrument guard only (08:30 and C-1 bars, no halt label, one id over [O, C); d-1's id = the 08:30 bar's) | cp3.py:129-137, 167-168 |
| 9 Flatten and D9 floor | OK. Nothing after an engine closure (test `test_cp3_d97_real_stop_level_engine_exit_then_nothing_more`); windows [O, C) = S0.12 | cp3.py:126 |
| 10 Nothing more | OK | cp3.py:187-193 |
| 11 Factories | OK. Ordinals 15-21 | cp3.py:196-221 |
| 12 Tests | OK. 15/15 mutants killed, including the exact-cut, halt, instrument-guard and [O, C)-boundary mutants | tests/test_k6_members_ports_cp3.py |

#### 1.4 K6-crushgap-01 (crushgap.py), 1 trial (ZS; ZM, ZL signal legs)

| Item | Verdict | Where |
|---|---|---|
| 1 Literals and clock | OK. Weights 0.022, 11, -1 (70); unit 0.0001 USD/bu (71); filter 0.02 = 200 units (72, 92); units per vendor tick derived from rules.products: ZM 22, ZL 11, ZS -25 (84-89; verified by the test and by hand: ZM tick 0.10 USD/st x 0.022 = 0.0022; ZL tick 0.01 c/lb = 0.0001 USD/lb x 11 = 0.0011; ZS tick 0.25 c/bu = 0.0025 USD/bu); 13:14 bars of d-1 (73, 124, 138-147) and 08:30 bars of d (187) | crushgap.py:65-92, 119-136 |
| 2 Direction | OK. G >= +200 units BUYS ZS, G <= -200 SELLS ZS (C lines 445-448), non-strict | crushgap.py:168-171 |
| 3 Exits | OK. First ZS bar of CT date d at or after 13:13 (74, 126, 184-185); nothing after an engine closure (probe 1: after a D9.7 exit at 10:31 the member sends nothing) | crushgap.py:184-185 |
| 4 Sizing | OK. `zs.q`; intents only on ZS (`leg_market_intent(view, TRADED, ...)`) | crushgap.py:195 |
| 5 Tables | GRAIN_TRADE_DATES, GRAIN_FULL_SESSIONS, previous_trade_date: recomputed, identical (section 3) | crushgap.py:41-45, 151-153 |
| 6 Availability | OK. Each leg's 13:14 close recorded at that bar's close on its own date (138-147); the 08:30 opens read from the current view (158, 167); no hindsight field | crushgap.py:138-172 |
| 7 Trade dates | OK. d-1 = previous EC-CAL grain trade date (K6-L-04): an early-halt d-1 has no 13:14 bars, so d is not traded (test and probe 5); the 13:14 bar must be on its trade date's CT date (145) | crushgap.py:145, 153, 161-163 |
| 8 C4 | OK. Full-session table (151); per-leg missing-bar and instrument guard (157-166); roll blackout and D11.5 are the engine's (and the member returns no intent when a leg lacks its 08:30 bar, consistent with D11.5) | crushgap.py:149-172 |
| 9 Flatten and D9 floor | OK. Windows = S0.12 for ZS, ZM, ZL | crushgap.py:129-136 |
| 10 Nothing more | OK. The only narrowing beyond the entry is C4-by-table (S0.8) | crushgap.py:151 |
| 11 Factories, legs | OK. make_zs; legs (ZS True, ZM False, ZL False); ordinal 22 | crushgap.py:128, 198-199 |
| 12 Tests | OK. 17/17 mutants killed (weights, unit, filter, both comparisons, direction, per-leg guards, d-1 mapping, entry/exit bars, open-vs-close fields) | tests/test_k6_members_crushgap.py |

#### 1.5 K6-limitcont-01 (limitcont.py, _limits.py, _event_common.py), 2 trials (HE, LE)

| Item | Verdict | Where |
|---|---|---|
| 1 Literals and clock | OK. Entry bar 08:44 (67, 229), exit C-2 = 12:58 from the frozen C (68, 170-171), c = the 08:30 bar's id (225-226), d-1..d-3 = the three LIVESTOCK_TRADE_DATES before d (69, 186-195), settlement window [12:59:30, 13:00) or the 30 s ending at an early halt (73-82), limits in vendor ticks from LIMIT_PERIODS (126-136) | limitcont.py:65-82, 126-136, 186-240 |
| 2 Direction | OK. S(d-1) - S(d-2) = +L(d-1) BUY, = -L(d-1) SELL, exactly | limitcont.py:210-213 |
| 3 Exits | OK. First present bar at or after 12:58 while in position and no opposite-sign pending; nothing after the engine's D9.7 exit (test `test_engine_d97_forced_exit_and_no_further_member_order`) | _event_common.py:66-78; limitcont.py:227-228 |
| 4 Sizing | OK | limitcont.py:169, 240 |
| 5 Tables | LIMIT_PERIODS (11 HE, 10 LE periods), SETTLEMENT_WINDOW_LIVESTOCK, DROPPED_LIMIT_DATES (14 LE dates), LIVESTOCK_* tables: recomputed, identical (section 3) | _limits.py:36-91 |
| 6 Availability and the proxy | OK. S(x) is built from x's bars as they close and read only on later dates; the proxy equals the engine's `_Settlement` value on every scenario tried, the window equals `settlement_window_ct` on all 1,795 livestock trade dates (14 moved by halts), and the d-1/d-2/d-3 chain equals the engine's `previous_trade_date` chain on every date (section 4) | limitcont.py:85-123, 175-184 |
| 7 Trade dates | OK. d in LIVESTOCK_FULL_SESSIONS (232); an early-halt d-1 is read through the halt window (probe 3: 12-26 trades off 12-24's 12:14 close at +L, and not one tick short) | limitcont.py:73-82, 232 |
| 8 C4 | OK. Full-session table; the 08:30 and 08:44 bars and every bar S uses must carry c (201, 235) | limitcont.py:199-203, 232-236 |
| 9 Flatten and D9 floor | OK. D9.7's entry refusal is not retried (`_entry_done` set before the refusal is known); windows (08:30, 13:00) = S0.12 | limitcont.py:70, 231 |
| 10 Nothing more | Two narrowings, both from the specs: the d-2 guard (208-209, K6-L-07) and the R-1b-2 dropped dates (196-197). Both only remove dates. The requirement that S's bars carry c is the definition of S(c, .) (K6-L-09), not an addition | limitcont.py:196-209 |
| 11 Factories | OK. make_he, make_le; ordinals 23-24 | limitcont.py:243-248 |
| 12 Tests | OK. 17/17 limitcont mutants and 3/3 _event_common mutants killed (section 5); the prompt's limit-close and D9.7 limit-proximity-exit cases are pinned through the real engine | tests/test_k6_members_limitcont.py |

#### 1.6 K6-wasdepre-01 (wasdepre.py, _wasde.py), 2 trials (ZC, ZS)

| Item | Verdict | Where |
|---|---|---|
| 1 Literals and clock | OK. 08:30 open (47, 82-83), entry on the 10:29 bar (48, 86), exit on the 11:14 bar or the first later bar (49, 84-85) | wasdepre.py:45-51, 74-100 |
| 2 Direction | OK. sign(Dr), Dr = close(10:29) - open(08:30) in ticks; zero no trade | wasdepre.py:96-99 |
| 3 Exits | OK (K6-L-12; probe 2: after a D9.7 exit at 11:01 the member sends nothing) | wasdepre.py:84-85 |
| 4 Sizing | OK | wasdepre.py:71, 100 |
| 5 Tables | WASDE_DATES (85 rows), DROPPED_WASDE (empty), GRAIN_FULL_SESSIONS: recomputed, identical | _wasde.py:39-66 |
| 6 Availability | OK. The 08:30 open at 08:31; the 10:29 close at 10:30; the date from the table | wasdepre.py:82-96 |
| 7 Trade dates | OK. Named bars by exact UTC instant of CT date d | _event_common.py:43-47 |
| 8 C4 | OK. WASDE date and full-session table (91-92); both bars present with one id (89, 94-95) | wasdepre.py:89-95 |
| 9 Flatten and D9 floor | OK. No fill can land in [11:00, 11:02) (entry fills 10:30, exit 11:15); windows = S0.12 | wasdepre.py:50-51 |
| 10 Nothing more | OK | - |
| 11 Factories | OK. make_zc, make_zs; ordinals 25-26 | wasdepre.py:103-108 |
| 12 Tests | OK. 9/9 mutants killed; the moved (2025-11-14) and cancelled (2025-10-09) releases and a monkeypatched drop are pinned | tests/test_k6_members_wasde.py |

#### 1.7 K6-wasdepost-01 (wasdepost.py), 1 trial (ZC)

| Item | Verdict | Where |
|---|---|---|
| 1 Literals and clock | OK. Signal bar 10:59 close (44, 78-79), entry on the 11:14 bar (45, 82), exit first bar at or after 13:13 (46, 80-81) | wasdepost.py:42-47, 70-96 |
| 2 Direction | OK. sign(R), R = close(11:14) - close(10:59); zero no trade | wasdepost.py:92-95 |
| 3 Exits | OK | wasdepost.py:80-81 |
| 4 Sizing | OK | wasdepost.py:67, 96 |
| 5 Tables | as wasdepre | - |
| 6 Availability | OK. The 10:59 close at 11:00; the 11:14 close at 11:15 | wasdepost.py:78-92 |
| 7 Trade dates | OK | - |
| 8 C4 | OK. WASDE date, full-session table, both bars with one id | wasdepost.py:85-91 |
| 9 Flatten and D9 floor | OK. The 11:15 entry is outside [11:00, 11:02); the event-window cost is the engine's; windows = S0.12 | wasdepost.py:47 |
| 10 Nothing more | OK | - |
| 11 Factories | OK. make_zc; ordinal 27 | wasdepost.py:99-100 |
| 12 Tests | OK. 9/9 mutants killed | tests/test_k6_members_wasde.py |

Cross-member checks. `strategy/members/k6/__init__.py` is 0 bytes. The 13 files pass `check_member_source` (0
problems each). The 27 factories return objects whose `name` equals the S0.2 label, whose `legs` equal the freeze
script's declarations and whose `trading_windows` equal S0.12 (auditor script, 27/27). Bar fields read across the
package: close, early_halt_ct, high, instrument_id, low, open, trade_date, ts_event_ns, volume; account fields:
position, pending. No hindsight field, no balance, no file, no release value.

### 2. The readings (items 13 and 14)

One line per reading. "Fixed" = the frozen text or a cited reference fixes it; "narrowest" = a reading the text
leaves open, judged the narrowest; "agree" = the auditor would take the same reading.

Adopted readings (specs section 9):
- E.3-L-01 literal tables: fixed (template import allowlist, lines 12-21). Agree.
- E.3-L-03 "the bar at hh:mm" is on CT date d: fixed (C1 lines 69-71). Agree.
- E.3-L-04 named entry bar exact: narrowest (C4 lines 96-98 extend only exits to "the first later bar"). Agree.
- E.3-L-06 CP1's guard is D6's: fixed (D6 line 364). Agree.
- E.3-L-07 CP2 counts present bars, no C-2 exit: fixed by the entry's own gloss ("the exit intent on the 75th bar after the entry-intent bar", C line 308-309) and B-H1 lines 146-151. Agree.
- E.3-L-08 CP2's range from present bars, the first qualifying bar uses the day's entry: fixed (D6 "one entry per trade date"; B-H1 has no minimum). Agree.
- E.3-L-09 / E.3-L-10 / E.3-L-11 CP3 by Family H, exit at or after C-2, halt = the bar's label: fixed (D6 line 366 "as Family H"; _mechanics.py). Agree.
- E.3-L-12 / E.3-L-13 C4's "a bar the rule reads" / "entry bar": narrowest. Agree.
- E.3-L-15 release rows at another time left out: moot (all 85 WASDE rows are 12:00 ET). Agree.
- E.3-L-17 fixed trading_windows; E.3-L-19 integer vendor ticks: fixed (interface, template). Agree.
- E.3-L-20 ZC (undersized) coded at q_c 1: fixed (header D2 row, C line 59). Agree.
- E.3-L-22 refused exit resent: fixed (C4's backstop clause). Agree.
- K4-L-01, K4-L-03, K4-L-05, K4-L-13, K3-L-11, K7-L-01, K1-L-10: agree; K3-L-11's only extra exclusion (2024-07-03, F 11:30 with no CME halt) lies outside the research window and removes a date.
- K4-L-06 CP2's buffer = 4 x vendor_tick: fixed (D6 ruling 21:52) and equal to C7's table on all seven roots (verified). Agree.
- K1-L-14 10(c), K1-L-16: the lead's labels and N rule; not member matters.
- Not adopted E.3-L-05: agree (K2's text named one instant; K6's C3 says "the first bar at or after").
- Not adopted K7-L-03: agree (K6's C4 has no vendor-degraded clause; the field arrives masked anyway).

New readings:
- **K6-L-01** (ruling asked): the grain first bar as "the earliest bar of trade date d at or after 19:00 CT on the calendar day before d" is fixed by C3 lines 83-84 for every date that has the evening session (a missing 19:00 bar gives 19:01; every evening bar missing gives the earliest overnight bar of CT date d, which is still the evening session, 19:00-07:45). On a scheduled late open the clause's "that 19:00 CT open" has no referent, and the lead's route to the 08:30 bar (D6's "trade date's first bar" with R-03's principle that a session starting at the day open has the day open as its first bar) is the reading fixed by a cited reference; the alternative "no trade on a late-open date" is an exclusion the text does not state and E.3-L-05's exact-bar reading belongs to different text. Agree. **On coder A's item 1** (a late-open date whose 08:30 bar is missing: the code takes 08:31, cp1.py:116): that is the same clause applied once more, and the lead's K6-L-01 text ("the first bar at or after that instant is the 08:30 bar of d") states the normal result, not an exactness requirement; an exact-08:30 reading for grains would import K6-L-02's livestock rule, which R-03 wrote for livestock only. The code stands; the spec wording should say "normally the 08:30 bar; if it is missing, the first later bar of d by the same clause" (finding N-1). It can touch 2025-12-26 and 2026-01-02 only, and only if their 08:30 bar is missing.
- K6-L-02 livestock first bar 08:30 exactly: fixed (R-03, C lines 259-261 name "the 08:30 bar"). Agree.
- **K6-L-03** GPM in exact integer units: fixed by the entry's weights and units (C lines 425-434) and E.2a's vendor_price_factor; 22 t_ZM + 11 t_ZL - 25 t_ZS in 0.0001 USD/bu and the filter 200 are arithmetic, verified by the auditor by hand and by the code's derivation from rules.products. CME's cents-per-pound formula is superseded by the entry's unit-consistent USD/lb form (C lines 431-433), so there is no second reading. Agree.
- K6-L-04 crushgap's d-1 = the EC-CAL grain trade date before d: fixed (C lines 440-441). Agree.
- K6-L-05 per-leg guard: fixed (C lines 443-444). Agree.
- **K6-L-06** (ruling asked): the 01:52 ruling on section 7 item 2 ("settlements from Databento statistics schema (quote in E.1) or settlement-window VWAP proxy") was a ruling on D9.7's inputs, and item 2 itself says "K6-limitcont-01 and K6-ml-01 (lim_pos, prev_limit) read the same inputs"; D9.7 line 542 wrote the proxy into the frozen design and the schema was not bought (rules/price_limits.py lines 39-42). So the proxy is the frozen input for the member, the member is implementable as frozen, and S(c, x) must be the engine's number (verified equal, section 4). Agree. Two consequences for the record: (a) because the livestock window [12:59:30, 13:00) overlaps exactly one one-minute bar, S is always one bar's close (or the fallback close), so "VWAP" never averages and K6-L-08's exactness is on the tick grid by construction; (b) the entry's event is "closed at the limit by the official settlement" and the member's is "the 12:59 close moved exactly L from the previous 12:59 close", which agree only where both proxies equal the official settlements to the tick (section 7 item 2's own warning). The auditor would put that on both trials as a label (finding N-2); it is not a code defect.
- **K6-L-07** (ruling asked): the entry's L is "the limit in force on d-1 (expanded where in force)" (C lines 537-538); the frozen EC-LIM holds the initial limit only (R-L2) and CME's expanded amounts are not 1.5 x initial exactly (HE 0.0475 -> 0.07, LE 0.0725 -> 0.1075, R-1b-4), so an expanded table cannot be derived from the frozen text and would be a new input. Of the readings inside the frozen inputs, the plain initial-limit test would count a move of exactly the initial L on a day whose limit was expanded (a non-event); the lead's d-2 guard removes those where c's own settlements show the expansion. It removes dates and never adds one. Agree, with the two residuals the lead named (a second consecutive limit day is never traded; an expansion triggered by another month or by Feeder Cattle is invisible and could count a non-event only on an exact-tick coincidence) and the labels in section 10. The entry's "a contract without a limit on d-1 does not qualify" (C line 539) is not encodable from the frozen table; it is moot while E.2a's roll keeps the vehicle out of its last two trading days (R-1b-4), which the lead should state.
- **K6-L-08** (ruling asked): exact equality in vendor ticks is fixed (C line 560 "exact equality"); with S one bar's close (see K6-L-06 (a)) the comparison is between tick-grid numbers, and `moved_exactly` compares the exact rationals (limitcont.py:139-144). "E.2 applies CME's settlement rounding" (C line 562) is moot, as the lead says. Agree.
- K6-L-09 c and the guard: fixed (C line 535; C4). Agree. Known consequence: the window's first three livestock dates never trade (no S), and any d with a bar-less d-1..d-3 does not trade.
- K6-L-10 C4 by table: agree (recomputed identical).
- K6-L-11 EC-WASDE = the frozen calendar's 12:00 ET WASDE rows after the drop rule: fixed (C9a); 85 rows, all at 12:00 ET, 14 in the window. Agree.
- K6-L-12 wasdepre's exit on 11:14 or the first later bar: fixed (C4 lines 96-98). Agree.
- K6-L-13, K6-L-14, K6-L-15: verified (27 declarations, S0.12 windows, file split).
- K6-L-16 (item 14 of the brief; section 7 as settled): item 1 ZS only: the 01:52 ruling, banner C line 382, agree. Item 2 the proxy: as K6-L-06. Item 3 D9.7 exit exempt from the fill guard: in the engine (admit_fill defers only `reason == "strategy"` orders; probe 2 shows a D9.7 exit filling at 11:01). Item 4 two percentage points inside the limit: engine (rules/price_limits.py TOPSTEP_BUFFER); not a member matter. Item 5 D9.3 skip: engine (admit_fill `entry_skipped_min_hold_before_flatten`). Item 6 CP1 livestock (b) form: R-03, agree. Item 7 cuts: banners, 27 trials, agree. Item 8 limitcont nested in CP3: no action, both screened, agree. Item 9 K6-032 excluded: 01:52. Item 10 roll: E.2a's per vehicle; crushgap accepts month mismatches (C lines 435-438). Item 11 source-overlap labels: confirmation only. Item 12 the 08:31 entries: ordinary market orders; the entries fix the bar, agree. Item 13 (a)-(g): as the lead lists; (e) is the proxy and R-L2. Items 14, 15: no action. Each settlement follows the frozen text and the 01:52 rulings.
- K6-L-17 N rule: the lead's.
- K6-L-18 ports and early halts: fixed (C line 89). Agree.

Section 10 rulings:
- R-1b-1 all 14 WASDE rows kept: agree; the auditor recomputed the 14 dates; 2025-11-14 is kept under C9a's drop rule because the NASS notice is dated 2025-10-31, before the new date.
- **R-1b-2** (ruling asked): drop, rather than use CME's $0.0850. The frozen table holds $0.0725 on 2026-06-01..06-18 (bracketed) and CME's SER-9736 resets LE to $0.0850 from trade date 2026-06-01. Keeping $0.0725 would test a non-event (a $0.0725 move is no longer a limit close) and miss true ones; using $0.0850 adds an input the freeze does not hold and would put the member's L out of step with the engine's D9.7 L on the same dates; dropping removes trade possibilities only. Agree. The quote was checked against the saved page reports/stage_e8_briefs/pages/cme_ser-9736.txt (sha256 4c311205...e4c29d; pdf d5f10661...4814d1): line 9 "Effective, Sunday May 31, 2026 for trade date Monday, June 1, 2026, Chicago Mercantile Exchange" and line 22 "Cattle 101 48 LE $0.0725/lb. $0.0850/lb. $0.1275/lb." The 14 dropped dates equal the livestock trade dates 2026-06-01..06-18 (recomputed). The code drops a d whose d-1 or d-2 is dropped (L is read on d-1 and d-2 only; d-3 enters through S only), which is the right set.
- R-1b-3 HE 2025-08-30..09-01 kept: agree (no trade date inside).
- R-1b-4 record only: agree; residual (b) named.
- R-1b-5 EC-CAL: the auditor's recomputation agrees (1,795 trade dates, 1,780 full sessions per group; research-window exclusions 2025-11-28 and 2025-12-24; late opens 2025-12-26 and 2026-01-02 kept as full sessions).
- R-1b-6: no member reads any release other than WASDE or any release value (grep of the package).

### 3. Table recomputation (item 5), audit_k6/recompute_tables.py

| Table | Recomputed from | Count (mine / module) | Differences |
|---|---|---|---|
| GRAIN_TRADE_DATES | load_group_calendar("grains").is_trade_date, weekdays 2019-05-01..2026-06-19 | 1795 / 1795 | none |
| LIVESTOCK_TRADE_DATES | the same, "livestock" | 1795 / 1795 | none |
| GRAIN_FULL_SESSIONS | trade dates with early_halt_ct None and flatten_time_ct(r, d) == 13:18 for all of ZC, ZW, ZS, ZM, ZL (one F per date on every date) | 1780 / 1780 | none; the only early-halt/F disagreement is 2024-07-03 (no halt, F 11:30), as the module comment says; research-window removals 2025-11-28, 2025-12-24; late opens 2025-12-26, 2026-01-02 are full sessions |
| LIVESTOCK_FULL_SESSIONS | the same with HE, LE and 13:03 | 1780 / 1780 | none; same disagreement date and removals |
| LIVESTOCK_EARLY_HALT_CT | every livestock trade date with a halt | 14 / 14 | none (dates and times) |
| previous_trade_date | against data.group_session.previous_trade_date on every date in the range, both groups | 0 mismatches | none |
| WASDE_DATES | reports/stage_e2b_release_calendar.json rows with release WASDE at 12:00 America/New_York, CT date in range | 85 / 85 (85 WASDE rows in the file, 0 at another time) | none; 14 research-window dates as the spec header; 2025-10-09 and 2025-11-10 absent; DROPPED_WASDE empty |
| LIMIT_PERIODS[HE] | rules.price_limits.LIMITS HARD_DAILY periods intersecting the range | 11 / 11 | none; bracketed: 2020-04-02..04-21, 2020-08-20..09-21, 2024-09-04..09-12, 2025-08-30..09-01 |
| LIMIT_PERIODS[LE] | the same | 10 / 10 | none; bracketed: 2024-10-09..11-05, 2026-05-19..06-19 |
| limit_ticks vs limit_period | on every livestock trade date, amount x vendor_price_factor / vendor_tick, integer | 0 mismatches | HE 0.03->120, 0.0375->150, 0.0400->160, 0.0475->190; LE 0.03->120, 0.04->160, 0.05->200, 0.0575->230, 0.0650->260, 0.0675->270, 0.0725->290, 0.0750->300 |
| DROPPED_LIMIT_DATES[LE] | livestock trade dates 2026-06-01..06-18 | 14 / 14 | none; each in the bracketed 0.0725 period; HE empty |
| SETTLEMENT_WINDOW_LIVESTOCK | rules.price_limits.SETTLEMENT_WINDOW_CT["livestock"] | (12:59:30, 13:00) | none |
| SOURCE_SHA256 of the three modules | sha256 of each named source now | 8 / 8 | all unchanged |

### 4. The proxy and the engine (item 6), audit_k6/proxy_compare.py

The member's `ProxyInputs` / `settlement()` fed through `on_minute` and the engine's `_Settlement.add`/`finalize`
fed the same bars, for HE and LE: regular day (S = the 12:59 close); 12:59 bar missing (fallback to the 12:58
close, the fallback bar's id recorded); zero volume in the window (fallback to the same bar's close); zero volume
with 12:58 also missing; bars only after 13:00 (both undefined); halt 12:15 on 2025-12-24 (S = the 12:14 close);
halt 12:15 with 12:14 missing (fallback 12:13); halt 12:05 on 2025-11-28 (the 12:04 close); a halt-labelled day
whose bars run to 13:05 (both use the 12:14 close: the window is the calendar's); three days with a different id
on d-2 (ids per date recorded); a date with no bars at all between two dates. 28 comparisons, 28 equal. The
member's `settlement_window(d)` equals `settlement_window_ct(root, d)` on all 1,795 livestock trade dates (14
moved by halts); the member's d-1, d-2, d-3 chain equals the engine's `previous_trade_date` chain on every date.
Probe 3 runs the whole path through the real engine (2025-12-26 trades off 12-24's halt-window close at +L; one
tick short does not trade).

### 5. Mutants (item 12), audit_k6/mutants.py, run against the out-of-tree copy

Baseline: the seven K6 test files pass in the repository (630 passed, 17.6 s) and in the copy (630 passed), and
the copy's pytest imports the copy's modules (checked). Each mutant changes one exact string, runs the named
test files with `-x`, and the file is restored from the pristine text.

Auditor mutants: 102 (one or more per literal, clock, comparison, direction, guard, table row and plumbing function). Pass 1 runs the member's own test file(s); pass 2 reruns every mutant whose first killer was a literal-pin, window or declaration test with those tests deselected, so a kill must come from a trade.

| Id | File | Mutation (old -> new) | Pass 1 | First killer (pass 1) | Pass 2 (pin tests deselected) |
|---|---|---|---|---|---|
| A-C1-01 | cp1.py | `SIGNAL_AFTER_O_MIN = 29` -> `SIGNAL_AFTER_O_MIN = 30` (signal bar 08:59) | killed | test_trading_windows_are_the_s0_12_intervals[ZC] | killed (test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_) |
| A-C1-02 | cp1.py | `ENTRY_BEFORE_C_MIN = 31` -> `ENTRY_BEFORE_C_MIN = 30` (entry bar C-31) | killed | test_trading_windows_are_the_s0_12_intervals[ZC] | killed (test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_) |
| A-C1-03 | cp1.py | `EXIT_BEFORE_C_MIN = 2  #` -> `EXIT_BEFORE_C_MIN = 1  #` (exit bar C-2) | killed | test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_ |  |
| A-C1-04 | cp1.py | `return "buy" if s > 0 else "sell"` -> `return "sell" if s > 0 else "buy"` (direction) | killed | test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_ |  |
| A-C1-05 | cp1.py | `GRAIN_EVENING_OPEN_CT = time(19, 0)` -> `GRAIN_EVENING_OPEN_CT = time(18, 0)` (19:00 evening open) | killed | test_trading_windows_are_the_s0_12_intervals[ZC] | killed (test_cp1_grain_first_bar_is_at_or_after_1900_of_the_calendar_day_befor) |
| A-C1-06 | cp1.py | `if first_id != signal_id:` -> `if False:` (signal-bar instrument guard) | killed | test_cp1_signal_bars_with_two_instrument_ids_are_no_trade[ZC] |  |
| A-C1-07 | cp1.py | `if s == 0:             return None` -> `if False:             return None` (zero signal no trade) | killed | test_cp1_zero_signal_is_no_trade[ZC] |  |
| A-C1-08 | cp1.py | `return opened.date() == day and opened.time() == self._leg.o` -> `return opened.date() == day and opened.time() >= self._leg.o` (livestock first bar exact 08:30 (K6-L-02)) | killed | test_cp1_livestock_first_bar_is_the_0830_bar_exactly_l02[HE] |  |
| A-C1-09 | cp1.py | `if self._first is not None:             return False` -> `if False:             return False` (earliest bar only (K6-L-01)) | killed | test_cp1_grain_monday_first_bar_is_sunday_1900_l01[ZC] |  |
| A-C1-10 | cp1.py | `return to_ticks(asdict(bar)["open"], tick)` -> `return to_ticks(asdict(bar)["close"], tick)` (first bar OPEN) | killed | test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_ |  |
| A-C1-11 | cp1.py | `return (leg_market_intent(view, self.root, side, self._le...` -> `return (leg_market_intent(view, self.root, side, self._le...` (size q_c) | killed | test_the_kit_adds_the_price_limit_reference_the_engine_needs | killed (test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_) |
| A-C1-12 | cp1.py | `self._signal = (to_ticks(bar.close, self._leg.tick), bar....` -> `self._signal = (to_ticks(asdict(bar)["open"], self._leg.t...` (signal bar CLOSE) | killed | test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_ |  |
| A-C1-13 | cp1.py | `return opened >= datetime.combine(day - ONE_DAY, GRAIN_EV...` -> `return opened >= datetime.combine(day - ONE_DAY, GRAIN_EV...` (grain first bar may be on CT date d-1) | killed | test_cp1_grain_monday_first_bar_is_sunday_1900_l01[ZC] |  |
| A-C2-01 | cp2.py | `RANGE_MINUTES = 15` -> `RANGE_MINUTES = 16` (OR 15 minutes) | killed | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] | killed (test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC]) |
| A-C2-02 | cp2.py | `BUFFER_TICKS = 4` -> `BUFFER_TICKS = 3` (buffer 4 ticks) | killed | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] | killed (test_cp2_the_buffer_is_exactly_four_ticks_either_side[ZC]) |
| A-C2-03 | cp2.py | `HOLD_BARS = 75` -> `HOLD_BARS = 74` (hold 75 bars) | killed | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] | killed (test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC]) |
| A-C2-04 | cp2.py | `if close >= to_ticks(self._hi, self._leg.tick) + BUFFER_T...` -> `if close > to_ticks(self._hi, self._leg.tick) + BUFFER_TI...` (non-strict >= on the high) | killed | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |  |
| A-C2-05 | cp2.py | `elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER...` -> `elif close < to_ticks(self._lo, self._leg.tick) - BUFFER_...` (non-strict <= on the low) | killed | test_cp2_breakout_down_sells[ZC] |  |
| A-C2-06 | cp2.py | `side = "buy"         elif close` -> `side = "sell"         elif close` (direction (up break buys)) | killed | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |  |
| A-C2-07 | cp2.py | `if not self._range_end <= at < self._leg.c or not is_flat...` -> `if not self._range_end <= at <= self._leg.c or not is_fla...` (no entry from C on) | killed | test_cp2_no_entry_from_c[ZC] |  |
| A-C2-08 | cp2.py | `if self._held < HOLD_BARS or account.pending.get(self.roo...` -> `if self._held <= HOLD_BARS or account.pending.get(self.ro...` (exit on the 75th bar) | killed | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |  |
| A-C2-09 | cp2.py | `self._triggered = True  # one entry per trade date, even ...` -> `pass  # one entry per trade date, even if the engine refu...` (one entry per trade date) | killed | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |  |
| A-C2-10 | cp2.py | `F_REGULAR_CT = {GRAINS: time(13, 18), LIVESTOCK: time(13,...` -> `F_REGULAR_CT = {GRAINS: time(13, 15), LIVESTOCK: time(13,...` (trading window to F) | killed | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] | survived |
| A-C2-11 | cp2.py | `self._hi = bar.high if self._hi is None else max(self._hi...` -> `self._hi = bar.close if self._hi is None else max(self._h...` (OR_high from highs) | killed | test_cp2_the_buffer_is_exactly_four_ticks_either_side[ZC] |  |
| A-C2-12 | cp2.py | `if self._leg.o <= at < self._range_end:` -> `if self._leg.o < at < self._range_end:` (08:30 bar in the range) | killed | test_cp2_the_range_is_the_max_high_and_min_low |  |
| A-C3-01 | cp3.py | `CLV_BUY_AT_OR_ABOVE = Decimal("0.8")` -> `CLV_BUY_AT_OR_ABOVE = Decimal("0.75")` (CLV 0.8) | killed | test_cp3_literals_are_the_clv_cuts_and_the_clock | killed (test_cp3_clv_cuts_are_compared_exactly[100-79-None]) |
| A-C3-02 | cp3.py | `CLV_SELL_AT_OR_BELOW = Decimal("0.2")` -> `CLV_SELL_AT_OR_BELOW = Decimal("0.25")` (CLV 0.2) | killed | test_cp3_literals_are_the_clv_cuts_and_the_clock | killed (test_cp3_clv_cuts_are_compared_exactly[100-21-None]) |
| A-C3-03 | cp3.py | `if num * buy_d >= buy_n * span:` -> `if num * buy_d > buy_n * span:` (non-strict >= 0.8) | killed | test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[Z |  |
| A-C3-04 | cp3.py | `if num * sell_d <= sell_n * span:` -> `if num * sell_d < sell_n * span:` (non-strict <= 0.2) | killed | test_cp3_prior_clv_at_02_sells[ZC] |  |
| A-C3-05 | cp3.py | `return "buy"     if num * sell_d` -> `return "sell"     if num * sell_d` (direction) | killed | test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[Z |  |
| A-C3-06 | cp3.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 2` (C_d = close of C-1) | killed | test_cp3_literals_are_the_clv_cuts_and_the_clock | killed (test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[Z) |
| A-C3-07 | cp3.py | `EXIT_BEFORE_C_MIN = 2  #` -> `EXIT_BEFORE_C_MIN = 3  #` (exit C-2) | killed | test_cp3_literals_are_the_clv_cuts_and_the_clock | killed (test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[Z) |
| A-C3-08 | cp3.py | `if span <= 0:` -> `if span < 0:` (range > 0) | killed | test_cp3_clv_cuts_are_compared_exactly[0-0-None] |  |
| A-C3-09 | cp3.py | `if prior.instrument_id != bar.instrument_id:` -> `if False:` (instrument guard) | killed | test_cp3_d_minus_1_is_the_most_recent_complete_day[ZC] |  |
| A-C3-10 | cp3.py | `complete = (self._has_open_bar and self._close is not Non...` -> `complete = (self._has_open_bar and self._close is not None` (halt day incomplete) | killed | test_cp3_a_halt_day_with_all_bars_to_c_is_still_incomplete[ZL] |  |
| A-C3-11 | cp3.py | `if bar.early_halt_ct is not None:             return None...` -> `if False:             return None  # an early-halt day d` (halt day d not traded) | killed | test_cp3_early_halt_day_is_not_traded_and_is_incomplete[ZC] |  |
| A-C3-12 | cp3.py | `and len(self._ids) == 1)` -> `and len(self._ids) >= 1)` (one instrument_id over [O, C)) | killed | test_cp3_d_minus_1_is_the_most_recent_complete_day[ZC] |  |
| A-C3-13 | cp3.py | `if at != self._leg.o or self._entered or not is_flat(acco...` -> `if at != shift(self._leg.o, 1) or self._entered or not is...` (entry on the 08:30 bar) | killed | test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[Z |  |
| A-C3-14 | cp3.py | `self._lo = bar.low if self._lo is None else min(self._lo,...` -> `self._lo = bar.close if self._lo is None else min(self._l...` (L from lows) | killed | test_cp3_the_daily_low_is_the_min_low[-2-buy] |  |
| A-C3-15 | cp3.py | `if not self._leg.o <= at < self._leg.c:             return` -> `if not self._leg.o <= at <= self._leg.c:             return` (daily bar [O, C)) | killed | test_cp3_grain_ids_outside_the_daily_window_do_not_make_it_incomplete[ |  |
| A-CG-01 | crushgap.py | `"ZM": Decimal("0.022")` -> `"ZM": Decimal("0.024")` (weight 0.022) | killed | test_gpm_units_are_derived_from_rules_products_and_the_weights |  |
| A-CG-02 | crushgap.py | `"ZL": Decimal("11")` -> `"ZL": Decimal("10")` (weight 11) | killed | test_gpm_units_are_derived_from_rules_products_and_the_weights |  |
| A-CG-03 | crushgap.py | `"ZS": Decimal("-1")` -> `"ZS": Decimal("1")` (minus P_ZS) | killed | test_gpm_units_are_derived_from_rules_products_and_the_weights |  |
| A-CG-04 | crushgap.py | `FILTER_USD_PER_BU = Decimal("0.02")` -> `FILTER_USD_PER_BU = Decimal("0.03")` (filter 0.02) | killed | test_gpm_units_are_derived_from_rules_products_and_the_weights |  |
| A-CG-05 | crushgap.py | `if g_units >= FILTER_UNITS:             return "buy"     ...` -> `if g_units >= FILTER_UNITS:             return "sell"    ...` (direction (gap up buys ZS)) | killed | test_the_filter_exactly_at_plus_and_minus_002_trades |  |
| A-CG-06 | crushgap.py | `if g_units >= FILTER_UNITS:` -> `if g_units > FILTER_UNITS:` (non-strict >=) | killed | test_the_filter_exactly_at_plus_and_minus_002_trades |  |
| A-CG-07 | crushgap.py | `if g_units <= -FILTER_UNITS:` -> `if g_units < -FILTER_UNITS:` (non-strict <=) | killed | test_the_filter_exactly_at_plus_and_minus_002_trades |  |
| A-CG-08 | crushgap.py | `if day not in GRAIN_FULL_SESSIONS:` -> `if day not in GRAIN_TRADE_DATES:` (C4 full-session table) | killed | test_d_not_in_grain_full_sessions_is_no_trade |  |
| A-CG-09 | crushgap.py | `if last is None or last[0] != prev:` -> `if last is None or last[0] > prev:` (13:14 bar is d-1's (K6-L-04)) | killed | test_d_minus_1_is_the_calendar_date_not_the_last_date_with_bars |  |
| A-CG-10 | crushgap.py | `if close_id != bar.instrument_id:` -> `if False:` (per-leg instrument guard) | killed | test_an_instrument_change_on_any_leg_is_no_trade[ZS] |  |
| A-CG-11 | crushgap.py | `EXIT_BEFORE_C_MIN = 2  #` -> `EXIT_BEFORE_C_MIN = 1  #` (exit 13:13) | killed | test_the_filter_exactly_at_plus_and_minus_002_trades |  |
| A-CG-12 | crushgap.py | `if opened.date() != day or opened.time() != zs.o:` -> `if opened.date() != day or opened.time() != shift(zs.o, 1):` (entry on the 08:30 bar) | killed | test_the_filter_exactly_at_plus_and_minus_002_trades |  |
| A-CG-13 | crushgap.py | `return to_ticks(asdict(bar)["open"], tick)` -> `return to_ticks(asdict(bar)["close"], tick)` (08:30 OPEN) | killed | test_the_filter_exactly_at_plus_and_minus_002_trades |  |
| A-CG-14 | crushgap.py | `close = to_ticks(bar.close, self._facts[r].tick)` -> `close = to_ticks(asdict(bar)["open"], self._facts[r].tick)` (13:14 CLOSE) | killed | test_g_is_open_of_d_minus_close_of_d_minus_1 |  |
| A-CG-15 | crushgap.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 2` (13:14 bar) | killed | test_crushgap_trading_windows_are_the_s0_12_intervals | killed (test_g_is_open_of_d_minus_close_of_d_minus_1) |
| A-CG-16 | crushgap.py | `if bar is None:                 return None  # K6-L-05: a...` -> `if bar is None:                 continue  # K6-L-05: a mi...` (missing 08:30 bar on a signal leg) | killed | test_engine_refuses_the_open_when_a_signal_leg_lacks_the_0830_bar_d11_ |  |
| A-CG-17 | crushgap.py | `if opened.date() == bar.trade_date and opened.time() == s...` -> `if opened.time() == self._close_at[r]:` (13:14 bar on its trade date's CT date) | killed | test_direct_the_1314_bar_must_be_on_its_trade_dates_ct_date |  |
| B-EC-01 | _event_common.py | `if bar is None or not position or exit_ns is None or bar....` -> `if bar is None or not position or exit_ns is None or bar....` (exit at or after the named bar) | killed | test_the_exit_is_on_the_first_bar_at_or_after_1258 |  |
| B-EC-02 | _event_common.py | `side = SELL if position > 0 else BUY` -> `side = BUY if position > 0 else SELL` (exit side) | killed | test_no_entry_while_a_position_or_an_order_is_pending |  |
| B-EC-03 | _event_common.py | `if pending and (pending > 0) != (position > 0):` -> `if False:` (no duplicate exit while one is pending) | killed | test_the_exit_is_on_the_first_bar_at_or_after_1258 |  |
| B-LC-01 | limitcont.py | `ENTRY_BAR = time(8, 44)` -> `ENTRY_BAR = time(8, 45)` (entry bar 08:44) | killed | test_declaration_legs_windows_and_size[HE] | killed (test_a_limit_up_close_buys_on_the_0844_bar[HE]) |
| B-LC-02 | limitcont.py | `EXIT_LEAD_MINUTES = 2` -> `EXIT_LEAD_MINUTES = 1` (exit C-2) | killed | test_declaration_legs_windows_and_size[HE] | killed (test_the_exit_is_on_the_first_bar_at_or_after_1258) |
| B-LC-03 | limitcont.py | `if moved_exactly(s1, s2, l1, self._tick):             ret...` -> `if moved_exactly(s1, s2, l1, self._tick):             ret...` (direction) | killed | test_a_limit_up_close_buys_on_the_0844_bar[HE] |  |
| B-LC-04 | limitcont.py | `if moved_exactly(s2, s3, l2, self._tick) or moved_exactly...` -> `if False:` (d-2 guard (K6-L-07)) | killed | test_d2_a_limit_close_itself_blocks_d[1-HE] |  |
| B-LC-05 | limitcont.py | `if d1 in self._dropped or d2 in self._dropped:` -> `if False:` (R-1b-2 dropped dates) | killed | test_a_dropped_limit_date_as_d1_gives_no_trade |  |
| B-LC-06 | limitcont.py | `or d not in LIVESTOCK_FULL_SESSIONS:` -> `or d not in LIVESTOCK_TRADE_DATES:` (C4 full-session table) | killed | test_d_outside_livestock_full_sessions_gives_no_trade[d0-prior0] |  |
| B-LC-07 | limitcont.py | `if value is None or ids != {c}:` -> `if value is None:` (S's bars carry c) | killed | test_a_settlement_bar_with_another_instrument_id_gives_no_trade[0] |  |
| B-LC-08 | limitcont.py | `return (nn * od - on * nd) * td == ticks * tn * nd * od` -> `return abs((nn * od - on * nd) * td - ticks * tn * nd * o...` (exact equality (K6-L-08)) | killed | test_moved_exactly_is_exact |  |
| B-LC-09 | limitcont.py | `if first <= day <= last:` -> `if first < day <= last:` (period boundary) | killed | test_the_limit_period_boundary_reads_each_dates_own_limit |  |
| B-LC-10 | limitcont.py | `if halt is None or halt > end:` -> `if True:` (early-halt window) | killed | test_member_settlement_window_is_the_engines_on_every_livestock_trade_ |  |
| B-LC-11 | limitcont.py | `if ts_ns >= self.lo_ns and volume > 0:` -> `if ts_ns >= self.lo_ns and volume >= 0:` (volume > 0 in the VWAP) | killed | test_proxy_vwap_arithmetic_mirrors_settlement_proxy_on_a_wider_window |  |
| B-LC-12 | limitcont.py | `if bar.ts_event_ns == ct_open_ns(d, self._open):` -> `if bar.ts_event_ns == ct_open_ns(d, time(8, 31)):` (c = the 08:30 bar's id) | killed | test_c_is_the_0830_bars_instrument_id |  |
| B-LC-13 | limitcont.py | `if c is None or bar.instrument_id != c:` -> `if c is None:` (entry bar carries c) | killed | test_c_is_the_0830_bars_instrument_id |  |
| B-LC-14 | limitcont.py | `l1, l2 = limit_ticks(self.root, d1), limit_ticks(self.roo...` -> `l1, l2 = limit_ticks(self.root, d2), limit_ticks(self.roo...` (L(d-1) for d-1's move) | killed | test_the_limit_period_boundary_reads_each_dates_own_limit |  |
| B-LC-15 | limitcont.py | `if ts_ns >= self.end_ns:             return` -> `if ts_ns > self.end_ns:             return` (window end exclusive) | killed | test_proxy_on_a_regular_day_is_the_1259_close[HE] |  |
| B-LC-16 | limitcont.py | `lo = time(start.hour, start.minute)` -> `lo = start` (window start floored to the minute) | survived |  |  |
| B-LC-17 | limitcont.py | `return (leg_market_intent(view, self.root, side, self._q),)` -> `return (leg_market_intent(view, self.root, side, self._q ...` (size q_c) | killed | test_engine_fills_the_entry_at_0845_and_the_exit_at_1259[HE] |  |
| A-PC-01 | _port_common.py | `if opened.date() != day or opened.time() < exit_at:` -> `if opened.date() != day or opened.time() <= exit_at:` (exit at or after C-2) | killed | test_an_exit_is_not_sent_while_an_order_is_pending |  |
| A-PC-02 | _port_common.py | `side = "sell" if position > 0 else "buy"     return (leg_...` -> `side = "buy" if position > 0 else "sell"     return (leg_...` (exit side) | killed | test_an_exit_is_not_sent_while_an_order_is_pending |  |
| A-PC-03 | _port_common.py | `if position == 0 or account.pending.get(root, 0):` -> `if position == 0:` (no exit while pending) | killed | test_an_exit_is_not_sent_while_an_order_is_pending |  |
| A-PC-04 | _port_common.py | `return round(Decimal(repr(price)) / tick)` -> `return int(Decimal(repr(price)) / tick)` (round vs truncate (expected equivalent on-grid)) | killed | test_prices_become_integer_vendor_ticks[ZC] |  |
| B-TB-01 | _wasde.py | `"2025-11-14",` -> `"2025-11-10",` (moved WASDE date) | killed | test_the_modules_are_exactly_the_generators_output | killed (test_wasde_dates_are_every_1200_et_wasde_row_of_the_frozen_calendar) |
| B-TB-02 | _limits.py | `        date(2026, 6, 18): _LE_DROP_REASON, ` -> `` (a dropped LE date) | killed | test_the_modules_are_exactly_the_generators_output | killed (test_dropped_limit_dates_are_the_14_le_trade_dates_of_r_1b_2) |
| B-TB-03 | _calendar.py | `    ("2025-12-24", "early halt 12:05; F 11:45"), ` -> `` (the grain not-full row 2025-12-24 removed (the livestock row reads 12:15, so the string is unique)) | killed | test_the_modules_are_exactly_the_generators_output | killed (test_d_not_in_grain_full_sessions_is_no_trade, tests/test_k6_members_crushgap.py) |
| B-WO-01 | wasdepost.py | `SIGNAL_BAR = time(10, 59)` -> `SIGNAL_BAR = time(11, 0)` (signal 10:59) | killed | test_wasdepost_signal_is_the_1114_close_minus_the_1059_close |  |
| B-WO-02 | wasdepost.py | `ENTRY_BAR = time(11, 14)` -> `ENTRY_BAR = time(11, 15)` (entry 11:14) | killed | test_wasdepost_trades_a_wasde_date_and_not_another |  |
| B-WO-03 | wasdepost.py | `EXIT_BAR = time(13, 13)` -> `EXIT_BAR = time(13, 14)` (exit 13:13) | killed | test_wasdepost_exit_on_the_first_bar_at_or_after_1313 |  |
| B-WO-04 | wasdepost.py | `side = BUY if response > 0 else SELL` -> `side = SELL if response > 0 else BUY` (direction) | killed | test_wasdepost_trades_a_wasde_date_and_not_another |  |
| B-WO-05 | wasdepost.py | `if response == 0:             return ()` -> `if False:             return ()` (zero response no trade) | killed | test_wasdepost_zero_response_does_not_trade |  |
| B-WO-06 | wasdepost.py | `if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SES...` -> `if d not in GRAIN_FULL_SESSIONS:` (WASDE dates only) | killed | test_wasdepost_trades_a_wasde_date_and_not_another |  |
| B-WO-07 | wasdepost.py | `if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SES...` -> `if not _wasde.is_wasde_date(d):` (C4 full-session table) | killed | test_wasdepost_needs_a_full_grain_session |  |
| B-WO-08 | wasdepost.py | `if bar.instrument_id != signal_id:` -> `if False:` (instrument guard) | killed | test_wasdepost_instrument_guard[659] |  |
| B-WO-09 | wasdepost.py | `self._signal = (price_ticks(bar.close, self._tick), bar.i...` -> `self._signal = (price_ticks(bar_open(bar), self._tick), b...` (10:59 CLOSE (needs bar_open import: expect crash-kill or NameError)) | killed | test_wasdepost_trades_a_wasde_date_and_not_another |  |
| B-WP-01 | wasdepre.py | `ENTRY_BAR = time(10, 29)` -> `ENTRY_BAR = time(10, 30)` (entry 10:29) | killed | test_wasdepre_trades_a_wasde_date_and_not_another[ZC] |  |
| B-WP-02 | wasdepre.py | `EXIT_BAR = time(11, 14)` -> `EXIT_BAR = time(11, 15)` (exit 11:14) | killed | test_wasdepre_exit_on_the_1114_bar_or_the_first_later_bar[ZC] |  |
| B-WP-03 | wasdepre.py | `DRIFT_START_BAR = time(8, 30)` -> `DRIFT_START_BAR = time(8, 31)` (drift from the 08:30 open) | killed | test_wasdepre_zero_drift_does_not_trade |  |
| B-WP-04 | wasdepre.py | `side = BUY if drift > 0 else SELL` -> `side = SELL if drift > 0 else BUY` (direction) | killed | test_wasdepre_trades_a_wasde_date_and_not_another[ZC] |  |
| B-WP-05 | wasdepre.py | `if drift == 0:             return ()` -> `if False:             return ()` (zero drift no trade) | killed | test_wasdepre_zero_drift_does_not_trade |  |
| B-WP-06 | wasdepre.py | `if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SES...` -> `if d not in GRAIN_FULL_SESSIONS:` (WASDE dates only) | killed | test_wasdepre_trades_a_wasde_date_and_not_another[ZC] |  |
| B-WP-07 | wasdepre.py | `if not _wasde.is_wasde_date(d) or d not in GRAIN_FULL_SES...` -> `if not _wasde.is_wasde_date(d):` (C4 full-session table) | killed | test_wasdepre_needs_a_full_grain_session |  |
| B-WP-08 | wasdepre.py | `if bar.instrument_id != start_id:` -> `if False:` (instrument guard) | killed | test_wasdepre_instrument_guard[510] |  |
| B-WP-09 | wasdepre.py | `self._start = (price_ticks(bar_open(bar), self._tick), ba...` -> `self._start = (price_ticks(bar.close, self._tick), bar.in...` (08:30 OPEN) | killed | test_wasdepre_signal_is_the_1029_close_minus_the_0830_open[ZC] |  |

Total 102: killed 101, survived 1 (B-LC-16, equivalent), skipped 0. Second pass on the 18 mutants whose first killer was a literal-pin, window, declaration or generator-equality test: killed 17 by a trade, survived 1 (A-C2-10, the CP2 window end, a declaration with no trade effect).


### 6. Findings

Counts: BLOCKING 0, SHOULD FIX 0, NOTE 11. No module implements anything other than its frozen entry as the
specs read it, and no module leaks: every input is read at or after its bar's close, the only account fields
read are position and pending, and no hindsight field is read. Every rule literal, clock, comparison and
direction has a failing mutant (101 of 102 killed; the survivor is equivalent, N-4).

- **N-1 (NOTE) K6-L-01 on a late-open date whose 08:30 bar is missing** (coder A's item for review).
  cp1.py:111-117 takes the earliest bar of d at or after 19:00 CT of d-1, so 08:31 when 08:30 is missing on
  2025-12-26 or 2026-01-02; the specs' row "Trade date's first bar, grains" and K6-L-01 say "that is the 08:30
  bar of d". Ruling (section 2): the code is the frozen clause applied once more and stands; an exact-08:30
  reading would import K6-L-02's livestock rule and would also need a late-open table (a member cannot tell a
  late open from a date whose evening bars are all missing), a new input. Smallest fix, in the specs only: "normally
  the 08:30 bar of d; if it is missing, the first later bar of d by the same clause". The lead flagged K6-L-01 for
  the user already; the pinning test is tests/test_k6_members_ports.py:604-616 (second half).
- **N-2 (NOTE) K6-L-06 label.** The member's event is "the 12:59 close (or the fallback close) moved exactly L
  from the previous one"; the entry's is "the official settlement closed at the limit". They agree only where the
  proxies of d-1 and d-2 equal the official settlements to the tick (section 7 item 2's own warning). The auditor
  would add to both K6-limitcont-01 trials the label "settlements by the D9.7 proxy (one bar's close); official
  settlements not tested" beside the two labels section 10 already gives. A label, the lead's call; no code change.
- **N-3 (NOTE) cp2.py:63 `F_REGULAR_CT`** is a clock literal (13:18 / 13:03) not read from a frozen table, used
  only for `trading_windows` (coverage); the template forbids importing rules.sessions. Pinned by
  `test_cp2_window_ends_are_the_engine_f_of_a_regular_day` and the S0.12 test; behaviourally inert (mutant A-C2-10
  survives pass 2 as a declaration should). No fix.
- **N-4 (NOTE) Surviving mutant B-LC-16** (limitcont.py:122, window start not floored to its minute): equivalent
  for every livestock window (30 seconds inside one minute, so the VWAP branch and the fallback select the same
  bar and id), as coder B's LC20 also found; the floor matters only for a multi-minute window, which no livestock
  date has, and the member copies the engine's `settlement_proxy`, which floors. No fix.
- **N-5 (NOTE) The coders' surviving mutants** (A: C1-20, C2-13, C3-23, CG-20, PC-05; B: LC11, LC20, LC42, LC45,
  PR13) were each checked against the code; all are equivalent as explained in the coders' reports (s == 0 returns
  first; a position implies this member's own same-date entry; inside [O, C) only the C-1 bar has at >= C-1;
  `last[0] != None` is always true once a close is recorded; the group test is unreachable for the seven roots; a
  halt at exactly 13:00 gives the regular window; `None != c`; one 08:44 bar per date; zero already returned).
- **N-6 (NOTE) Tests that pin only a literal.** Coder A named CG-09 (the 0.0001 unit, which scales coefficients and
  filter together) and C2-08/09 (window ends); the auditor's pass 2 confirms every other clock, comparison and
  direction literal is also pinned by a trade (16 of 17 pin-first mutants killed behaviourally; the exception is
  the CP2 window end, N-3). No test passes vacuously: every negative-case test in the seven files has a positive
  control in the same file, and every guard-removal mutant was killed by its negative-case test.
- **N-7 (NOTE) K6-L-07's "a contract without a limit on d-1" (C line 539)** is not encodable from the frozen
  table (every date has a limit) and is moot only while E.2a's roll keeps the vehicle out of its last two trading
  days (R-1b-4). The specs should state that dependence; no code change.
- **N-8 (NOTE) Coder A's observation 2** (on ZS the lower D9.7 stop at one contract lies beyond the $2,000 MLL,
  so a lower-stop touch becomes an MLL liquidation before D9.7 fires) is a harness and sizing observation for the
  lead's return, not a member defect; the ports' D9.7 tests use the upper stop on all seven roots.
- **N-9 (NOTE) Fresh-state consequences at a window's start**, all by the specs: limitcont cannot trade the first
  three livestock dates of a run (no S for d-3, K6-L-09); crushgap cannot trade the first grain date (no 13:14 bars
  of d-1 seen); CP3 cannot trade until a complete daily bar exists (warm-up). Record them beside the event counts.
- **N-10 (NOTE) Unreachable error paths.** limitcont.py:132-134 and crushgap.py:77-81 raise ValueError if a limit
  amount or weighted tick is not an integer number of units; every frozen amount is (section 3), so neither is
  reachable with the frozen tables. If a table ever changed, the run would stop rather than trade: acceptable.
- **N-11 (NOTE) Incident.** The auditor's first rsync for the out-of-tree copy descended into data/vendor and
  filled the tmpfs scratchpad (section 0); the lead removed it. No repository file was touched; the pre-audit
  hashes verify at the end; the code-only copy (16 MB) is deleted at the end of Part 1.

Verified without finding: 27 declarations, names, legs, factories and ordinals (S0.2, freeze dry run); every
trading_windows entry (S0.12); every literal clock against the frozen O and C; every direction; every exit's
"first bar at or after" and resend; q_c from the frozen table everywhere; crushgap sends intents on ZS only;
the per-leg guard; all seven tables recomputed identical; the proxy equal to the engine's on 28 scenarios and
the window and d-k chain equal on all 1,795 livestock trade dates; no member acts after an engine closure
(tests and probes 1-2); the D9.7 exit is exempt from the fill guard in the engine (probe 2, 11:01 fill); the
coverage check clips a day -1 interval to the calendar's sessions, so a late open costs CP1 no coverage.

## Part 2: recomputation (Task 6)

