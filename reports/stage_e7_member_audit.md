# Stage E.7, cluster K1: member audit

## Part 1: fidelity audit (Task 3)

Auditor: MemberAuditor-K1-FableXHigh (worker-xhigh, Fable 5.1, xhigh). Brief:
reports/stage_e7_briefs/auditor_task3_K1.md. Started 02:09 PDT 2026-09-28, ended 02:45 PDT (times America/Vancouver).
I wrote none of the code, the specs or the tests. Read-only on the repository except this report and my scripts
under reports/stage_e7_briefs/audit_k1/ (auditor_recompute_tables.py and .json, auditor_scenarios.py,
auditor_mutants.py with its .log, .jsonl and _summary.md, auditor_sha256_at_start.txt). Mutants ran only on a scratch
mirror under the session scratchpad (auditor_mut_repo); the repository's K1 files were unchanged after the sweep
(sha256 checked by the runner). Holdout status at start (02:09) and end (02:43): all_ok true, unlocks_logged 0.

Verdict in one line: **every one of the five modules implements its frozen entry and nothing more; no BLOCKING finding; one
SHOULD FIX (a test gap: the two new members' engine tests never feed the previous evening's bars, so two of my
mutants that read them survive although they change trades on real bars); 9 NOTEs.** The literal tables recompute identical from their sources. Every lead reading is the
narrowest the frozen text allows or is fixed by a cited reference; K1-L-01's 08:30 stands against the prompt's 08:35.

### Files as audited (sha256, 02:09 PDT; the coders' reported hashes agree)

| File | sha256 |
|---|---|
| strategy/members/k1/__init__.py | e3b0c442...b855 (0 bytes) |
| strategy/members/k1/_port_common.py | 55ba92ef01591c66241b2698d8fc99e23210c8fb0826658b158af129637447dc |
| strategy/members/k1/cp1.py | ccc9d83e2b20db011ba34d314d4b494b0dac55f89d0d9b7c75f3ec48131e848c |
| strategy/members/k1/cp2.py | 430206138665cdda12497bdd9d2de777ac8156a107974e6d0a19d61c9b6f6c3e |
| strategy/members/k1/cp3.py | f8e533d589b50ac817f87647be7de400d57a388f065cd6f740849c5c47374882 |
| strategy/members/k1/_event_common.py | 07ca23a8437510212c6320611ccafae390c252a2ecb0ae1a4498206c64ac22bd |
| strategy/members/k1/vxnband.py | 685b5018c139e8463f7cc55b62966e70e75d68a0499c2c90a36b07898f2be151 |
| strategy/members/k1/vwap.py | daffd93131b34b5221c0d66372333344fae4c88843818c68db03a0aebcc93622 |
| strategy/members/k1/_calendar.py | 1f9488bd3eb8c5e7aec29bd62ef2c7efbf187f14bdfda1cf7d97c3635681719c |
| strategy/members/k1/_vxn.py | 1d585e4fdffc530ec86871cda5e71b66d7fd33183249a485bbda24de005cc6b5 |
| tests/test_k1_members_ports.py | 525877ba6d71e2855ba3198761ff37674fad30e3798cd5ebcbb664beacf62225 |
| tests/test_k1_members_ports_cp2.py | 96dbc764bc71554a227cbacdde79e681b71caf439ca6c29ff4485888f51ed42f |
| tests/test_k1_members_ports_cp3.py | 2840f07869432d2278fbcf4b31e5ce4c0fd5ae91253e11001d5005dfe8fc866e |
| tests/test_k1_members_ports_events.py | 93763b1f157fb3d8f5479d2f02c79757362d20934f8f2ee2a81e5e79ffa77a0f |
| tests/test_k1_members_vxnband.py | b580828bff2f12afc1b7f38bb61783207b23a9c49d7e17a5c907e45d2016cdf5 |
| tests/test_k1_members_vwap.py | 2854fa36d7697b0519ae24b0d5a30fb385e0dc040da1a6bab416133c074f56e1 |
| tests/test_k1_members_tables.py | 3e00e5dba8d2f4d59f13d01247f5e144c845261479fd2c8f107641136f66a6ae |
| reports/stage_e7_member_specs.md | a1a942cccc7110e3577bc5091d4a53b96f2188f14d488024b984b93b63e2a224 |
| reports/stage_e0_catalog_K1.md | 9360e0d6fc66ca306f669f1b628ba9c8c4fd924cafec0e9f7ce60cc994594944 |
| reports/stage_e7_briefs/gen_k1_tables.py | d18000a17d071959edfca68e4bd9d98e9a38ae9806de6cc7cfc743ff3066f759 |
| reports/stage_e7_briefs/write_k1_freeze.py | fee59a6926dd578ea753098c77eb469065f3cf9ec249c250c34b61ebf0d9ecee |
| data/vendor/index_history/vxn/VXN_History.csv | f1b00135c4922ea756cd22cfeaa1d483700a6aed580f8da562f61574b5e1cdcc |
| reports/stage_e7_release_check.json | 2e68fb6555ebcc7a8e1eac614a3b8d08a364ed1a065a703a2a06b4f92fe59712 |

The full list (docs/STAGE_E_DESIGN.md and the prompt included) is in audit_k1/auditor_sha256_at_start.txt.

### Method

1. Read the frozen entries (catalog banner, header, C1-C12, the five member sections, KF1, section 7), D5, D6 and D9,
   the specs in full, the stage prompt's Task 2 and Task 3 text, all ten member files, all seven test files, the
   coders' reports, the generator, the freeze script, the engine and rules paths the brief names (ask_member,
   fill_pending_at_open, call_member, account_view, structural_refusal, _exit_refusal, admit_fill, gate), the
   interface, the template's allowlist, the Bar fields and their availability classes, the MES references (B-H1
   lines 135-182, H6, _mechanics docstring) and the K7 ports.
2. Diffed each K1 port against its audited K7 sibling: the rule bodies are byte-identical apart from the docstrings,
   EXPOSURES = (MNQ, M2K, MYM), the three factories and __all__ (audit_k1 command log; see "Ports" below).
3. Recomputed the three literal tables from their sources with my own code (auditor_recompute_tables.py).
4. Ran my own scenarios and three exact-rational oracles (auditor_scenarios.py): 100k random band cases, 50k random
   CLV cases and 3k random VWAP days against Fraction arithmetic; ten engine or direct-call scenarios the coders'
   tests do not make.
5. Ran my own 113-mutant sweep over all seven K1 source files (auditor_mutants.py), independent of the coders' lists.
6. Checked the static freeze check on all ten files, the empty __init__.py, the frozen tables (O, C, q_c, tick) and
   the freeze script's dry run (11 declarations, ordinals 1-11 as S0.2).

The lead's gate suite was running on the same files; I ran the K1 test files once as a baseline (268 + 99 passed,
02:19 PDT) and touched nothing under strategy/ or tests/.

### 1. Checklists per member (brief items 1-12)

Verdict key: OK = implements the frozen text; NOTE n = see finding n. Line numbers are the files' own.

#### K1-cp1-01 (cp1.py, _port_common.py), trials 1-3 on MNQ, M2K, MYM

| # | Check | Verdict | Where |
|---|---|---|---|
| 1 | O 08:30, C 15:00 from the frozen day_session_ct; signal bar O+29 = 08:59; entry C-31 = 14:29; exit C-2 = 14:58; the first bar 17:00 CT on CT date d-1 | OK | _port_common.py:66-71 (leg_facts), cp1.py:57-60 (literals), :91-93 (shifted from O and C), :128 (17:00 on day-1), :133 (08:59), :136 (14:29), :127 (exit via exit_if_due, _port_common.py:98-110) |
| 2 | Direction with the signal: buy if close(08:59) - open(17:00) > 0, sell if < 0, zero no trade | OK | cp1.py:111-114 |
| 3 | Exit on the first present bar of CT date d at or after 14:58; refused exit resent; nothing while pending | OK | _port_common.py:105-110 (position != 0, nothing pending, date == d, time >= exit_at) |
| 4 | q_c from the frozen vehicle table (1, 3, 3), exits close abs(position) | OK | _port_common.py:71, cp1.py:142, _port_common.py:110; my scenario check "q_c from the frozen table" on all nine port objects |
| 5 | Tables | n/a (the ports read none) | |
| 6 | Availability: the 17:00 bar read at its close, the 08:59 bar at 09:00, decision at 14:29's close; no hindsight field, no account field beyond position and pending | OK | cp1.py:128-135; grep of strategy/members/k1 for vendor_degraded_day, gap_before_minutes, is_roll_session, in_*_window, entries_today, balance, avg_entry: no hit |
| 7 | Trade date: only the 17:00 bar of CT date d-1 and bars of CT date d; identified by CT date and clock; after an early-halt holiday the holiday's 17:00 reopen is the first bar (its "12:00" label is not read) | OK | cp1.py:128-131; tests test_cp1_after_memorial_day_the_first_bar_is_the_holidays_1700_reopen, test_cp1_the_first_bar_is_the_1700_bar_of_ct_date_d_minus_1_only |
| 8 | No C4 guard beyond D6's signal-bar guard (both bars present, one instrument_id) | OK | cp1.py:106-110; no halt test, no vendor-degraded test (test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry) |
| 9 | Nothing against F, the entry cap, the 2-minute rule, D9.12, D9.7; after an engine closure nothing more that date; trading_windows = S0.12 | OK | cp1.py:95-99 (windows), :126-127 (exit only while a position exists and nothing pending: a forced order is pending); test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry |
| 10 | Nothing more: no filter, size rule or state beyond the two signal bars, _entered, _day | OK | cp1.py:82-85 state fields |
| 11 | Factories make_mnq/make_m2k/make_mym, name = label, legs = (LegSpec(root, True),); static check passes | OK | cp1.py:145-154; check_member_source [] on all ten files (02:17 PDT); write_k1_freeze.py --dry-run ordinals 1-3 |
| 12 | Tests pin entry/exit times, direction, zero signal, missing 17:00 / 08:59 / 14:29 / 14:58 bars, the id guard, the refused exit resend, a synthetic F flatten, the D9.7 closure, Memorial Day, Good Friday, Christmas, the CPI window, FOMC/ISM unchanged; my 19 cp1 and _port_common mutants all killed | OK | tests/test_k1_members_ports.py:468-686, tests/test_k1_members_ports_events.py; section 4 |

#### K1-cp2-01 (cp2.py), trials 4-6

| # | Check | Verdict | Where |
|---|---|---|---|
| 1 | OR over present bars opening in [08:30, 08:45) of CT date d; eligible bars [08:45, 15:00); buffer 4 x vendor_tick = 1.00 / 0.40 / 4 index points; 75 present bars | OK | cp2.py:56-58 (15, 4, 75), :82 (range end = O+15), :113-116 (range), :119 (eligibility, no entry from 15:00), :122-124 (buffer in integer ticks), :89-98 (count) |
| 2 | Break direction: close >= OR_high + 4 ticks buys, close <= OR_low - 4 ticks sells, non-strict, the first qualifying bar | OK | cp2.py:121-127 |
| 3 | Exit on the 75th present bar with the position open, counted from the fill bar (the bar after the entry-intent bar), fill 75 minutes after the fill; resent while refused; no C-2 exit; F by the engine | OK | cp2.py:93-98 (count while position != 0, exit from 75 while nothing pending); tests ...fills_next_open_and_exits_after_75_present_bars (08:46 -> 10:01), ...has_no_c_minus_2_exit, ...a_deferred_entry_fill_starts_the_count_at_the_fill, ...the_last_eligible_bar_1459_is_held_to_f |
| 4 | q_c, exits close abs(position) | OK | cp2.py:129, :97-98 |
| 5 | Tables | n/a | |
| 6 | Range bars read at their close; the trigger bar's close at its close; no hindsight field | OK | cp2.py:113-121 |
| 7 | Bars of CT date d only; the evening never enters the range or triggers | OK | cp2.py:110-111; tests ...bars_before_o_and_on_the_previous_evening_are_not_range_bars, ...a_monday_reads_no_sunday_evening_bar, ...after_memorial_day_reads_only_the_tuesday |
| 8 | No C4 guard (no minimum bar count, no instrument guard, no halt test): D6 and B-H1 have none | OK | cp2.py docstring 9-11, tests ...has_no_instrument_guard, ...one_opening_range_bar_is_enough, ...does_not_test_early_halts_the_engine_flattens_at_f |
| 9 | Engine's F closes a late entry (fills after 13:53); no duplicate exit while the forced order is pending; no re-entry after a D9.7 closure (_triggered stays set) | OK | cp2.py:95, :117-118; tests ...f_binds_from_a_1353_fill, ...d97_engine_exit_no_duplicate_exit_and_no_reentry |
| 10 | Nothing more; F_REGULAR_CT literal serves the trading window only | OK, NOTE 8 | cp2.py:59, :84 |
| 11 | Factories, label, one leg, static check, ordinals 4-6 | OK | cp2.py:132-141 |
| 12 | Tests pin the literals in prices per root (1.00 / 0.40 / 4 and one tick short), both directions, the count (a missing bar inside the hold), deferred fills (D9.5a) on entry and exit, no entry from 15:00, one entry per date even when refused, no range bar, present-bar range, CT-date identification, FOMC/ISM/CPI; my 13 cp2 mutants all killed | OK | tests/test_k1_members_ports_cp2.py, _events.py; section 4 |

#### K1-cp3-01 (cp3.py), trials 7-9

| # | Check | Verdict | Where |
|---|---|---|---|
| 1 | Daily bar from bars of CT date d in [08:30, 15:00): H/L over present bars, C_d = the 14:59 close; entry on the 08:30 bar; exit at or after 14:58; CLV cuts 0.8 / 0.2 | OK | cp3.py:62-65 (literals), :145-156 (accumulate: halt from any bar of CT date d, ids/H/L in [O, C), 08:30 and 14:59 flags), :185-191 (entry on the 08:30 bar), :183-184 (exit) |
| 2 | Direction by CLV of d-1: >= 0.8 buys, <= 0.2 sells, non-strict, exact integer cross-products | OK | cp3.py:79-92; my Fraction oracle (50k cases, 0 mismatches) |
| 3 | Exit on the first present bar at or after 14:58, resent while refused | OK | via exit_if_due; test ...missing_1458_bar_sends_the_exit_on_1459 |
| 4 | q_c, whole position | OK | cp3.py:191 |
| 5 | Tables | n/a | |
| 6 | d-1 is finalised only when a bar of a later trade date arrives (day d's own bar never enters day d); early_halt_ct is a calendar field (Family H reads it); no hindsight field | OK | cp3.py:137-143 (_roll), :127-135 (_complete_bar); test ...uses_d_minus_1_only_after_it_is_finalised |
| 7 | Bars of CT date d only; the post-holiday evening bars (label "12:00") are not read, so the Tuesday after Memorial Day is traded and complete; d-1 skips the incomplete holiday | OK | cp3.py:179-180; tests ...the_tuesday_after_memorial_day_reads_friday, ..._is_not_a_halt_day, ...two_early_halt_dates_in_a_row_are_both_skipped, ...after_good_friday_monday_reads_thursday |
| 8 | Family H's rules only: complete day (08:30 and 14:59 bars, no early_halt_ct, one instrument_id over [08:30, 15:00)); instrument guard d-1 vs the 08:30 bar; halt day d not traded; warm-up no trade; range > 0 | OK | cp3.py:128-129, :160-167, :83 |
| 9 | Nothing against the engine; no duplicate exit; no re-entry after D9.7 (_entered) | OK | cp3.py:187; tests ...position_open_at_a_synthetic_f..., ...d97_engine_exit... |
| 10 | Nothing more (O_d is not read: it enters no condition) | OK | cp3.py docstring 13 |
| 11 | Factories, label, static check, ordinals 7-9 | OK | cp3.py:194-203 |
| 12 | Tests pin the cuts exactly where floats miss them (M2K), both directions, strictly-between no trade, zero range, warm-up, incomplete days dropped, two ids, the guard, missing 08:30 bar, halt days, holidays, D9.5a on the 08:31 fill, F, D9.7, CPI, FOMC/ISM hold; my 15 cp3 mutants all killed | OK | tests/test_k1_members_ports_cp3.py; section 4 |

#### K1-vxnband-01 (vxnband.py, _event_common.py, _calendar.py, _vxn.py), trial 10 on MNQ

| # | Check | Verdict | Where |
|---|---|---|---|
| 1 | 16 -> 1600 (w = C_prev x V / 1600); cuts 20 strict, 30 non-strict; scan [08:30, 14:29); exit at entry-intent + 30 min; C_prev = the 14:59 close | OK | vxnband.py:68-73 (literals), :86-87 (regime), :90-100 (band), :201 (scan window), :237 (exit_at = intent minute + 30), :183-186 (14:59 close) |
| 2 | Fade: close > U sells, close < L buys, strict; exact integers with V as n/m | OK | vxnband.py:93-100; my Fraction oracle, 100k cases, 0 mismatches; test ...band_is_exact_a_close_on_u_or_l_does_not_trade |
| 3 | Exit on the first present bar of CT date d at or after intent + 30, only while a position exists and nothing pending; resent while refused; after an engine closure nothing more (searching is False) | OK | vxnband.py:231-234, _event_common.py:108-114; my S1 (14:58 and 14:59 missing: exit intent 15:00, fill 15:01, accepted by the engine), S2 (an id change during the hold changes nothing); tests ...a_missing_exit_bar..., ...no_exit_while_an_order_is_pending_and_a_refused_exit_is_resent, ...an_engine_closure_ends_the_day |
| 4 | q_c = 1 from the frozen table, whole position | OK | _event_common.py:70-73, vxnband.py:238, _event_common.py:114 |
| 5 | EQUITY_TRADE_DATES, EQUITY_FULL_SESSIONS, VXN_CLOSE equal my recomputation, every row | OK | section 2 |
| 6 | V is read once, at d's 08:30 bar's close (08:31 CT), inside _day_setup called only when minute == O; never V of d or later (PREVIOUS_TRADE_DATE maps every date to the EC-CAL trade date before it; my S4 checks all 1846 dates); C_prev from complete earlier dates finalised at the roll; no hindsight field | OK, NOTE 3 | vxnband.py:79-83, :188-196, :206-207, :166-174; test ...v_is_read_at_the_0830_bar_and_never_before (a recording table: one read, at the 08:30 bar) |
| 7 | Bars of CT date d only (the previous evening is skipped before any accumulation); V's date = the EC-CAL trade date before d (a holiday with an early halt is a trade date, so its Tuesday has no V); C_prev skips incomplete (halt) dates; the post-holiday evening label is not read | OK | vxnband.py:226-227, :79-83; tests ...missing_v_the_tuesday_after_memorial_day_2025_does_not_trade (on the real table), ...a_mondays_v_is_fridays_close_not_sundays, ...c_prev_is_the_1459_close_of_the_most_recent_complete_date |
| 8 | C4: entry only on EQUITY_FULL_SESSIONS dates (searching = is_full_session); a minute of [08:30, t] without a bar, or a scan bar with another id, before the first breach ends the search; C_prev by Family H; the 08:30 bar missing means no trade | OK | vxnband.py:173, :203-204, :209-210, :159-164 |
| 9 | Nothing against the engine: one entry per date, hold 30 (28 when D9.5a moves the fill), exits check pending, trading_windows (08:30, 15:00) = S0.12 | OK, NOTE 6 | vxnband.py:156, :235; test ...event_minutes_fomc_1300_and_ism_0900 (12:59 intent, fill 13:02, exit 13:29 -> 13:30) |
| 10 | Nothing more: no extra filter or state beyond the Family H accumulators, the search flag, the clock run, the setup and exit_at | OK | vxnband.py:135-146 state fields |
| 11 | make_mnq only, label "K1-vxnband-01 MNQ", one leg, static check, ordinal 10 | OK | vxnband.py:241-242 |
| 12 | Tests pin the round trip both sides, the 08:30-bar breach, C_prev completeness (six kinds), the 14:59 bar (not 14:58/15:00), warm-up, the guard, missing 08:30, V of d-1 never d, Friday not Sunday, the real-table Memorial Day case, the read clock, the exact band and regime edges, first breach only, refused breach uses the day, scan end 14:28/14:29, gap and id change before the breach, gap after the breach, missing exit bar, pending and resend, engine closure, non-full session, CPI, FOMC/ISM; my 27 vxnband + 7 _event_common mutants: 32 killed, VB-17 equivalent, VB-26 survives and is a real gap (section 4) | Test gap: SHOULD FIX 1; NOTE 4 | tests/test_k1_members_vxnband.py; section 4 |

#### K1-vwap-01 (vwap.py, _event_common.py, _calendar.py), trial 11 on MNQ

| # | Check | Verdict | Where |
|---|---|---|---|
| 1 | TP = (H+L+C)/3; VWAP over present bars of CT date d from 08:30 through t; rule window [08:30, 14:57); 20 entries; hold: exit intent from bar k+1; final exit at or after 14:58 | OK | vwap.py:70-74 (literals), :137-142 (sums in ticks, sign of 3 C sum(vol) - sum((H+L+C) vol)), :183-184 (bars before 08:30 skipped), :190 (rule window), :155 (cap), :162-164 (hold), :188-189 (final exit) |
| 2 | Direction s_t: +1 above, -1 below, tie keeps the sign, 0 before the first sign; sum(vol) = 0 no action and no update | OK | vwap.py:140-144; my Fraction VWAP oracle (3k random days incl. zero-volume bars, 0 mismatches); tests ...a_close_exactly_at_vwap_keeps_the_previous_sign..., ...volume_weights_the_vwap, ...zero_volume_bars_take_no_action |
| 3 | Reversal = exit intent then entry intent on one bar, both q_c, both accepted and filled at the same next open (engine: exposure = position + pending so the entry leg opens from 0; _exit_refusal passes because decision = fill + 120 s); exit to flat after the 20th entry; instrument-change exit on that bar; final exit resent while refused | OK | vwap.py:165-169, :188-189; engine screening/stage_e_engine.py:589-616, rules :471-472, :546-555; my S7 (every intent accepted), S8 (40 accepted, none refused, ends flat), S6 (14:56 entry, 14:58 missing: final exit 14:59, fill 15:00); tests ...the_reversal_pair_is_accepted..., ...twenty_entry_intents..., ...an_instrument_change_sends_an_exit... |
| 4 | q_c = 1 from the frozen table; exits close abs(position); never a 2 q_c order | OK | vwap.py:148, :165-166 |
| 5 | Tables | OK | section 2 |
| 6 | Each bar's H, L, C, volume, instrument_id read at its close; the fill bar k is the bar at whose call the position is first seen; no hindsight field | OK | vwap.py:121-125, :186-187 |
| 7 | Bars of CT date d from 08:30 only; non-full sessions never traded | OK | vwap.py:180-184, :115 |
| 8 | C4: gap by clock from 08:30 (a missing 08:30 bar is a gap) ends new entries, position keeps the rule's exits; id change (reference = the 08:30 bar's id) ends new entries and exits the position | OK | vwap.py:129-134, :155, :167-168, :188 |
| 9 | Nothing against the engine: at most 20 entry intents, hold >= 2 full minutes by construction, no intent while pending, D9.5a-delayed reversals wait; after an engine closure the rule continues (K7-L-07); trading_windows (08:30, 15:00) | OK, NOTE 5 | vwap.py:152-153, :111; tests ...event_minutes_ism_0900_and_fomc_1300, ...after_an_engine_closure_the_rule_continues |
| 10 | Nothing more | OK | vwap.py:90-101 state fields |
| 11 | make_mnq only, label, one leg, static check, ordinal 11 | OK | vwap.py:195-196 |
| 12 | Tests pin the sign and the tie, weighting, zero volume, the 08:30 start, the pair's acceptance, k+1 hold and its restart, pending, the cap incl. refused intents, 14:56/14:57 edge, 14:58/14:59 final exit, gaps (before and after an entry), id change, engine closure, non-full session, CPI, ISM/FOMC; my 29 vwap mutants: 25 killed, VW-25, VW-27 and VW-29 equivalent, VW-28 survives and is a real gap (section 4) | Test gap: SHOULD FIX 1; NOTE 4 | tests/test_k1_members_vwap.py; section 4 |

**Ports against K7 (brief input):** `diff` of each K1 port against strategy/members/k7/cp{1,2,3}.py and
_port_common.py after neutralising the cluster names shows differences only in the docstrings, EXPOSURES, the
LegFacts comments, the three factories and __all__; every rule line is identical to the E.6-audited K7 code.

### 2. Table recomputation (brief item 5; auditor_recompute_tables.py, 02:27 PDT)

| Table | Source (my code) | Mine | Module | Equal | Differences |
|---|---|---|---|---|---|
| EQUITY_TRADE_DATES | load_group_calendar("equity").is_trade_date over every calendar day 2019-05-01..2026-06-19 | 1846 | 1846 | yes | none |
| EQUITY_FULL_SESSIONS | the above with early_halt_ct None AND rules.sessions.flatten_time_ct(root, d) == 15:08 for MNQ, M2K and MYM | 1779 | 1779 | yes | none; the halt test and the F test disagree on 0 dates; F equal across the three roots on all 1846; 67 removed, 13 in the research window (2025-05-26, 06-19, 07-03, 07-04, 09-01, 11-27, 11-28, 12-24, 2026-01-19, 02-16, 04-03, 05-25, 06-19) = the specs' early-F list and R-1b-7 |
| PREVIOUS_TRADE_DATE | consecutive pairs of the above | 1845 | 1845 | yes | 2019-05-01 has no predecessor (NOTE 7) |
| VXN_CLOSE | csv module on the saved file (sha256 = section 9's), rows dated 2019-04-30..2026-06-19, less {2021-04-02, 2021-12-24, 2024-02-01}, CLOSE as the raw last field of each line | 1794 (1797 in range, 0 duplicates) | 1794 | yes, exact strings and order | none; the member's date -> Decimal map equals the module |
| Source pins | sha256 of data/calendars/__init__.py, data/calendars/equity.py, data/cme_calendar.py, rules/sessions.py, the VXN file | | | all equal the pinned values | |

Section 9 checks: the file has 4,287 rows 2009-09-14..2026-09-25, header DATE,OPEN,HIGH,LOW,CLOSE, every CLOSE with
six decimals; the two R-1b-3 rows repeat the prior row on all four fields (2021-04-02 is an equity trade date with an
08:15 halt, F 07:45; 2021-12-24 is not an equity trade date); the R-1b-2 row reads 17.330000 now and 11.200000 in the
saved 2024-04-19 Wayback copy (LOW 11.200000 in both). After the drops no row of the range falls on a non-trade date.
Trade dates 2019-05-02..2026-06-19 without V: 52 (the module's comment says 52). Research trade dates without V: the
nine of R-1b-5. vxn_for: 2025-04-21 -> the 2025-04-17 row (32.830000; no 04-18 row); 2025-05-27 -> None; 2019-05-06
(S_X) -> 15.980000; 2024-02-02 and 2021-04-05 -> None; 2026-06-19 -> 26.310000 (the 06-18 row).

### 3. The lead's readings (brief items 13-14): narrowest, or fixed by reference?

Adopted readings (E.3-L-01/03/04/05/06/07/08/09/10/11/12/13/17/19/22, K4-L-01/05/06/13, K3-L-11, K7-L-01/07): each is
applied to text that is the same as the earlier cluster's; I checked E.3-L-07 and E.3-L-08 against the B-H1 module
(the count runs while position != 0, `_triggered` is set on emission) and E.3-L-09/10/11 against _mechanics; all hold.
K7-L-03 correctly not adopted (K1's C4 has no vendor-degraded clause; no module reads vendor_degraded_day).

| Reading | My ruling | Why |
|---|---|---|
| K1-L-01 VXN used from 08:30 CT on d, read at the 08:30 bar's close | **Stands; the prompt's "(the catalog KF1 row: from 08:35 CT on d)" is a mis-citation.** | The vxnband entry (C 458) and C9 (C 154; the specs cite it as 150-151, a line drift only) both say 08:30. KF1 (C 725) is the feature table of K1-ml-01, excluded by U6 with 0 trials; its "used from 08:35" is the ML decision-window start W0, which the catalog derives from KF6's first five-minute candle (C 733-737: "Why W0 = 08:35: the first five-minute candle ... is complete at 08:35"), not from Cboe's publication (C 737). Applying 08:35 to vxnband would remove the entry-intent bars 08:30-08:33 from a scan the entry fixes at [08:30, 14:29) and would change the frozen rule. Availability: R-1b-4's three informative observations (Last-Modified 17:01 CDT on the last row's date; Wayback captures at 08:05 CST and 04:12 CDT on D+1 holding D's row) all put publication before 08:30 CT on D+1; no Cboe statement exists, so this is observational (NOTE 3). The code reads V exactly once, at the 08:30 bar's close (vxnband.py:206-207, :193), and my S4 shows V(d) is always the row of a date before d for all 1846 dates. |
| K1-L-02 V's date = the EC-CAL trade date before d; missing -> no trade | Stands, literal and narrowest | C 445 says "trade date d-1" under C3's trade dates; an early-halt holiday is an equity trade date (EC-CAL, R-1b-7). The wider reading (C_prev's date, or the last published close) would trade nine more research dates; the entry distinguishes "the previous complete trade date" (C_prev) from "trade date d-1" (V). Cost: 9 research dates untraded (R-1b-5), recomputed above. |
| K1-L-03 C_prev by Family H completeness, as CP3's d-1 | Fixed by reference | C 442-443 "(Family H completeness)"; _mechanics docstring defines complete and "d-1 = the most recent complete daily bar". The instrument guard against d's 08:30 bar is C 443-444 verbatim. |
| K1-L-04 exact integer band; scan by clock; a gap or another id before the first breach ends the search; the first breach uses the day's entry | Stands, narrowest | The scan reads every bar of [08:30, t] (each close is compared), so a missing one is "a bar the rule reads" (C4 108-110; E.3-L-12 limits it to bars before the entry decision). Ending the search adds nothing and admits no entry the text forbids. The tick cancels in 1600 (close - C_prev) vs C_prev x V, so the integer compare is exact (my oracle). |
| K1-L-05 exit by clock at entry-intent + 30, first later bar if missing | Stands, fixed by C4 and the source | C 451 names both "the 30th bar after the entry-intent bar" and "filling 30 minutes after the entry fill"; C4 111-112 ("If an exit's named bar is missing, the exit is sent on the first later bar") presupposes a named clock bar, which a present-bar count would not have; the source's rule is a "30-minute exit". Under D9.5a's deferral the hold is 28 minutes (NOTE 6); the alternative anchor (30 minutes after the moved fill) is not what the entry names. |
| K1-L-06 VWAP over present bars; exact integer sign | Stands | Databento writes no bar for a minute without trades, so a missing minute adds no volume either way; the integer form is the exact sign (my oracle). |
| K1-L-07 vwap gap: no new entry for the rest of d, an open position keeps the rule's exits; id change as C 558-559 | Stands, narrowest | The gap clause is C4's (silent in the entry); ending entries is the least that "no trade on d" can mean once a position exists without inventing an exit the entry does not state; the exits kept are the entry's own (opposite-signal exit to flat, final exit). My S9 confirms the code: a gap right after the fill makes the 09:03 reversal an exit to flat with no new leg. |
| K1-L-08 entry intents counted when sent, refused ones included | Acceptable; the conservative of two readings | "entries have been made" (C 538, 547) can mean sent or filled. Counting sent intents never exceeds counting fills, so the member stays inside D9.3(a) whatever the engine refuses; the alternative could send more intents on days with refusals (roll blackouts, where nothing fills anyway; D9.7 proximity; skipped_today). No research-window trade is expected to differ. I would keep the lead's reading (NOTE 5 records the alternative). |
| K1-L-09 fill bar k = the bar at whose call the position is first seen; exit or reversal from k+1; no intent while pending | Stands, literal | C 544-546 "may be exited only by an intent on bar k+1 or later ... fills at the open of bar k+2 or later". The engine fills at a bar's open before calling the member at that bar's close (engine fill_pending_at_open then ask_member), and MIN_HOLD_NS = 2 minutes on the decision instant, so the k+1 intent is exactly the earliest the engine accepts (my S7). |
| K1-L-10 C4's early close by table (EQUITY_FULL_SESSIONS), K3-L-11's F test added | Stands; the F test changes nothing here | The halt test and the F test never disagree in EC-CAL (0 dates), so the adoption adds and removes no date. |
| K1-L-11 trading_windows as S0.12 | Stands | Code matches (cp1.py:95-99, cp2.py:84, cp3.py:124, vxnband.py:156, vwap.py:111); the intervals cover every bar each member reads or holds through. |
| K1-L-12 11 declarations, ordinals catalog order then MNQ, M2K, MYM | Stands | write_k1_freeze.py --dry-run prints 1..11 as S0.2. |
| K1-L-13 two coders, file split | Stands (process) | |
| K1-L-14 section 7 as settled | Follows the frozen text and the prompt on items 1-9, 10(a), 10(b), 10(d)-(f), 11; item 10(c) defers a check the catalog places before any bar is read (NOTE 2) | Item 1: DECISIONS.md line 261, V15 (K1 screened now). Item 2: C 597, predrift EXCLUDED by the E.0 lead. Item 3-4: the banner's 5 members, 11 trials. Item 5: E.2a's vehicles are the micros. Item 6: the frozen release calendar's ISM_SERVICES rows carry MNQ, M2K and MYM (release check D). Items 7-9: as stated. 10(c): C7 says "E.2 confirms that each tick was unchanged over 2019-05..2026-06 before any bar is read"; reports/stage_e2a_vehicles.md contains no tick-history confirmation (grep "tick": cost arithmetic only). |
| K1-L-15 CPI never binds | Stands | No K1 intent fills before 08:31 (earliest entry intents are on the 08:30 bar); q_c <= 3 = D9.12's 50K micro limit; the engine applies every `cpi: true` row to any root in CPI_MICRO_LIMITED (rules/constraints.py:11, screening/stage_e_rules.py:159-167), so coder A's note 4 (the CPI rows' products list MNQ only) does not change the spec's claim. |
| K1-L-16 N rule | The lead's pre-declared rule (K7-L-05); not mine to change | |

Section 9 rulings: R-1b-1 (kept; the label "VXN values not point-in-time checked for the research window" must travel
with the trial), R-1b-2 and R-1b-3 (confirmation-window drops, conservative: each removes one trade possibility and
adds none; consistent with the Task 1b verdict set keep / drop / unverifiable), R-1b-4 (observational, NOTE 3),
R-1b-5 (recomputed: the nine dates), R-1b-6 (14 CPI instants; never binds), R-1b-7 (recomputed: 3 closures and 13
early-F dates), R-1b-8 (no member reads a release).

### 4. Mutant sweep (brief item 12; auditor_mutants.py, scratch mirror, nice 10)

Sweep 02:24-02:40 PDT on the scratch mirror: **113 mutants over all seven source files: 106 killed, 6 survived, 1
pattern-skipped (rerun by hand, killed).** Of the six survivors four are equivalent by inspection and two are real
test gaps (the same gap, proved non-equivalent with auditor_evening_probe.py at 02:43 PDT). Baselines before the
sweep: ports 268 passed, vxnband+tables 68, vwap 31, tables+vxnband+vwap 99. The repository's K1 files were
byte-identical after the sweep (sha256 checked by the runner and again by hand). Full per-mutant records:
reports/stage_e7_briefs/audit_k1/auditor_mutants_result.jsonl; the runner names each mutant's exact text change.

| Id | File | Change | Result | Failed | First killing test | Auditor's reading of a survivor |
|---|---|---|---|---|---|---|
| PC-1 | _port_common.py | exit one minute late (14:59 instead of 14:58) | killed | 81 | ports.py::test_an_exit_is_not_sent_while_an_order_is_pending[MNQ] |  |
| PC-2 | _port_common.py | exit side flipped | killed | 87 | ports.py::test_an_exit_is_not_sent_while_an_order_is_pending[MNQ] |  |
| PC-3 | _port_common.py | ticks by truncation | killed | 3 | ports.py::test_prices_become_integer_vendor_ticks[MNQ] |  |
| PC-4 | _port_common.py | is_flat ignores pending | killed | 9 | ports.py::test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[MNQ] |  |
| PC-5 | _port_common.py | exit sent while an order is pending | killed | 3 | ports.py::test_an_exit_is_not_sent_while_an_order_is_pending[MNQ] |  |
| PC-6 | _port_common.py | exit bar not tied to CT date d | killed | 3 | ports.py::test_an_exit_is_not_sent_while_an_order_is_pending[MNQ] |  |
| C1-1 | cp1.py | signal bar 08:58 | killed | 52 | ports.py::test_trading_windows_are_the_s0_12_intervals[MNQ] |  |
| C1-2 | cp1.py | entry bar 14:30 | killed | 52 | ports.py::test_trading_windows_are_the_s0_12_intervals[MNQ] |  |
| C1-3 | cp1.py | exit bar 14:59 | killed | 31 | ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[MNQ] |  |
| C1-4 | cp1.py | first bar 17:01 | killed | 17 | ports.py::test_trading_windows_are_the_s0_12_intervals[MNQ] |  |
| C1-5 | cp1.py | signal sign flipped | killed | 38 | ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[MNQ] |  |
| C1-6 | cp1.py | zero signal buys | killed | 6 | ports.py::test_cp1_zero_signal_is_no_trade[MNQ] |  |
| C1-7 | cp1.py | signal-bar instrument guard removed | killed | 3 | ports.py::test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06[MNQ] |  |
| C1-8 | cp1.py | direction flipped | killed | 38 | ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[MNQ] |  |
| C1-9 | cp1.py | first bar = the last evening bar | killed | 10 | ports.py::test_cp1_missing_first_bar_is_no_trade_l05[MNQ] |  |
| C1-10 | cp1.py | entry decision repeatable | killed | 3 | ports.py::test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[MNQ] |  |
| C1-11 | cp1.py | size literal 1 (not q_c) | killed | 8 | ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[M2K] |  |
| C1-12 | cp1.py | signal uses the 08:59 open | killed | 40 | ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[MNQ] |  |
| C1-13 | cp1.py | entry while not flat | killed | 3 | ports.py::test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[MNQ] |  |
| C2-1 | cp2.py | range [08:30, 08:44) | killed | 4 | ports_cp2.py::test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[MNQ] |  |
| C2-2 | cp2.py | buffer 3 ticks | killed | 14 | ports_cp2.py::test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[MNQ] |  |
| C2-3 | cp2.py | hold 74 bars | killed | 57 | ports_cp2.py::test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[MNQ] |  |
| C2-4 | cp2.py | buy compare strict | killed | 62 | ports_cp2.py::test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MNQ] |  |
| C2-5 | cp2.py | sell compare strict | killed | 16 | ports_cp2.py::test_cp2_breakout_down_sells[MNQ] |  |
| C2-6 | cp2.py | up-break sells | killed | 59 | ports_cp2.py::test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MNQ] |  |
| C2-7 | cp2.py | entry allowed on the 15:00 bar | killed | 3 | ports_cp2.py::test_cp2_no_entry_from_1500[MNQ] |  |
| C2-8 | cp2.py | exit on the 76th bar | killed | 54 | ports_cp2.py::test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MNQ] |  |
| C2-9 | cp2.py | re-entry allowed | killed | 60 | ports_cp2.py::test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MNQ] |  |
| C2-10 | cp2.py | range high from closes | killed | 11 | ports_cp2.py::test_cp2_the_buffer_is_exactly_four_ticks_either_side[MNQ] |  |
| C2-11 | cp2.py | 08:30 bar not a range bar | killed | 1 | ports_cp2.py::test_cp2_the_0830_bar_is_a_range_bar |  |
| C2-12 | cp2.py | hold exit sent while pending | killed | 4 | ports_cp2.py::test_cp2_a_deferred_exit_is_not_sent_twice |  |
| C2-13 | cp2.py | evening bars enter the range | killed | 1 | ports_cp2.py::test_cp2_range_and_eligible_bars_are_bars_of_ct_date_d |  |
| C3-1 | cp3.py | buy cut 0.81 | killed | 43 | ports_cp3.py::test_cp3_literals_are_the_clv_cuts_and_the_clock |  |
| C3-2 | cp3.py | sell cut 0.19 | killed | 19 | ports_cp3.py::test_cp3_literals_are_the_clv_cuts_and_the_clock |  |
| C3-3 | cp3.py | C_d = 14:58 close | killed | 56 | ports_cp3.py::test_cp3_literals_are_the_clv_cuts_and_the_clock |  |
| C3-4 | cp3.py | exit bar 14:59 | killed | 48 | ports_cp3.py::test_cp3_literals_are_the_clv_cuts_and_the_clock |  |
| C3-5 | cp3.py | buy compare strict | killed | 42 | ports_cp3.py::test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459[MNQ] |  |
| C3-6 | cp3.py | sell compare strict | killed | 18 | ports_cp3.py::test_cp3_prior_clv_at_02_sells[MNQ] |  |
| C3-7 | cp3.py | high CLV sells | killed | 49 | ports_cp3.py::test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459[MNQ] |  |
| C3-8 | cp3.py | zero range allowed | killed | 4 | ports_cp3.py::test_cp3_clv_cuts_are_compared_exactly[0-0-None] |  |
| C3-9 | cp3.py | halt day d traded | killed | 9 | ports_cp3.py::test_cp3_early_halt_day_is_not_traded_and_is_incomplete[MNQ] |  |
| C3-10 | cp3.py | instrument guard removed | killed | 3 | ports_cp3.py::test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar[MNQ] |  |
| C3-11 | cp3.py | halt day complete | killed | 4 | ports_cp3.py::test_cp3_early_halt_day_is_not_traded_and_is_incomplete[MNQ] |  |
| C3-12 | cp3.py | two-id day complete | killed | 1 | ports_cp3.py::test_cp3_a_day_with_two_instrument_ids_is_incomplete |  |
| C3-13 | cp3.py | entry on any bar from 08:30 | killed | 1 | ports_cp3.py::test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete |  |
| C3-14 | cp3.py | daily low from closes | killed | 2 | ports_cp3.py::test_cp3_the_daily_low_is_the_min_low[6-buy] |  |
| C3-15 | cp3.py | evening bars enter the daily bar | killed | 2 | ports_cp3.py::test_cp3_the_tuesday_after_memorial_day_is_not_a_halt_day |  |
| EC-1 | _event_common.py | one-minute gaps allowed | killed | 4 | vxnband.py::test_a_missing_scan_bar_before_the_first_breach_ends_the_search |  |
| EC-2 | _event_common.py | close_items side flipped | killed | 35 | vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |  |
| EC-3 | _event_common.py | close_items while pending | killed | 2 | vxnband.py::test_no_exit_while_an_order_is_pending_and_a_refused_exit_is_resent |  |
| EC-4 | _event_common.py | d-2 instead of d-1 | killed | 26 | vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |  |
| EC-5 | _event_common.py | every date a full session | killed | 2 | vxnband.py::test_a_not_full_session_date_is_not_traded |  |
| EC-6 | _event_common.py | sign flipped | killed | 27 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| EC-7 | _event_common.py | is_flat ignores pending | killed | 1 | vxnband.py::test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day |  |
| VB-1 | vxnband.py | divisor 1500 | killed | 13 | vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] |  |
| VB-2 | vxnband.py | low cut 21 | killed | 2 | vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False] |  |
| VB-3 | vxnband.py | high cut 29 | killed | 2 | vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[29.990000-False] |  |
| VB-4 | vxnband.py | scan to 14:30 | killed | 1 | vxnband.py::test_the_scan_ends_before_1429[869-False] |  |
| VB-5 | vxnband.py | hold 31 | killed | 21 | vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |  |
| VB-6 | vxnband.py | C_prev = 14:58 close | killed | 3 | vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[complete] |  |
| VB-7 | vxnband.py | low cut non-strict | killed | 2 | vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False] |  |
| VB-8 | vxnband.py | high cut strict | killed | 2 | vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[30.000000-True] |  |
| VB-9 | vxnband.py | upper breach non-strict | killed | 3 | vxnband.py::test_the_band_is_exact_a_close_on_u_or_l_does_not_trade[1999-None] |  |
| VB-10 | vxnband.py | lower breach non-strict | killed | 3 | vxnband.py::test_the_band_is_exact_a_close_on_u_or_l_does_not_trade[-1999-None] |  |
| VB-11 | vxnband.py | fade direction flipped | killed | 32 | vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |  |
| VB-12 | vxnband.py | V of d itself (leak) | killed | 28 | vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |  |
| VB-13 | vxnband.py | instrument guard removed | killed | 1 | vxnband.py::test_the_c_prev_instrument_guard_against_the_0830_bar |  |
| VB-14 | vxnband.py | second entries allowed | killed | 9 | vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] |  |
| VB-15 | vxnband.py | exit one minute late | killed | 21 | vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |  |
| VB-16 | vxnband.py | non-full sessions traded | killed | 1 | vxnband.py::test_a_not_full_session_date_is_not_traded |  |
| VB-17 | vxnband.py | V read on a later bar when 08:30 fails | SURVIVED | 0 |  | equivalent: the setup line is reachable only on the 08:30 bar (a missing 08:30 bar breaks the clock run first; a failed setup ends the search), so V is still read once, there |
| VB-18 | vxnband.py | halt day complete for C_prev | killed | 1 | vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] |  |
| VB-19 | vxnband.py | 15:00 bar in the id set | killed | 1 | vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[other_id_at_1500] |  |
| VB-20 | vxnband.py | gap check removed | killed | 1 | vxnband.py::test_a_missing_scan_bar_before_the_first_breach_ends_the_search |  |
| VB-21 | vxnband.py | scan instrument change ignored | killed | 2 | vxnband.py::test_an_instrument_change_before_the_first_breach_ends_the_search[540] |  |
| VB-22 | vxnband.py | 08:30 bar not scanned | killed | 26 | vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |  |
| VB-23 | vxnband.py | exit at intent + 31 | killed | 21 | vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |  |
| VB-24 | vxnband.py | entry while not flat | killed | 1 | vxnband.py::test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day |  |
| VB-25 | vxnband.py | size literal 2 | killed | 1 | vxnband.py::test_no_exit_while_an_order_is_pending_and_a_refused_exit_is_resent |  |
| VB-26 | vxnband.py | evening bars read | SURVIVED | 0 |  | NOT equivalent: on real bars the evening after an early-halt holiday carries the holiday's label and would make that trade date incomplete as C_prev (probe: Wednesday 2025-05-28 sells under the mutant, no trade under the code); no coder-B engine test feeds evening bars. SHOULD FIX 1 |
| VB-27 | vxnband.py | regime filter removed | killed | 2 | vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False] |  |
| VW-1 | vwap.py | TP parts 2 | killed | 30 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-2 | vwap.py | rule to 14:58 | killed | 2 | vwap.py::test_no_entry_from_the_1457_bar[897-expected1] |  |
| VW-3 | vwap.py | final exit 14:59 | killed | 9 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-4 | vwap.py | cap 21 | killed | 3 | vwap.py::test_declaration_label_leg_and_trading_window |  |
| VW-5 | vwap.py | exit on the fill bar | killed | 5 | vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |  |
| VW-6 | vwap.py | exit from k+2 | killed | 5 | vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |  |
| VW-7 | vwap.py | sign flipped | killed | 27 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-8 | vwap.py | tie resets the sign | killed | 2 | vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |  |
| VW-9 | vwap.py | VWAP of closes | killed | 3 | vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |  |
| VW-10 | vwap.py | unweighted | killed | 30 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-11 | vwap.py | gap ignored | killed | 3 | vwap.py::test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit |  |
| VW-12 | vwap.py | id change ignored for entries | killed | 2 | vwap.py::test_an_instrument_change_sends_an_exit_and_ends_new_entries |  |
| VW-13 | vwap.py | hold one bar longer | killed | 5 | vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |  |
| VW-14 | vwap.py | reversal leg despite the cap | killed | 2 | vwap.py::test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |  |
| VW-15 | vwap.py | final exit 14:59 | killed | 9 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-16 | vwap.py | rule on the 14:57 bar | killed | 2 | vwap.py::test_no_entry_from_the_1457_bar[897-expected1] |  |
| VW-17 | vwap.py | entries never counted | killed | 2 | vwap.py::test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |  |
| VW-18 | vwap.py | VWAP from bars before 08:30 | killed | 22 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-19 | vwap.py | non-full sessions traded | killed | 1 | vwap.py::test_a_not_full_session_date_is_not_traded |  |
| VW-20 | vwap.py | entry direction flipped | killed | 25 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-21 | vwap.py | reverse on the same sign | killed | 18 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-22 | vwap.py | hold restarts every bar | killed | 8 | vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |  |
| VW-23 | vwap.py | no instrument-change exit | killed | 1 | vwap.py::test_an_instrument_change_sends_an_exit_and_ends_new_entries |  |
| VW-24 | vwap.py | intents while pending | killed | 2 | vwap.py::test_no_intent_while_an_order_is_pending |  |
| VW-25 | vwap.py | reversal order entry-then-exit | SURVIVED | 0 |  | equivalent: the two reversal intents are identical market orders of q_c; the engine's fills and ledger do not depend on their order |
| VW-26 | vwap.py | flat entry on s = 0 | killed | 28 | vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |  |
| VW-27 | vwap.py | sum(vol) = 0 acts (sign 0) | SURVIVED | 0 |  | equivalent: with sum(vol) = 0 the sign is 0 and s is not updated; on_minute line 190 still returns before the rule |
| VW-28 | vwap.py | evening bars read | SURVIVED | 0 |  | NOT equivalent: on real bars the evening's first bar breaks the 08:30 clock run, so vwap would never enter (probe: no fills under the mutant, the normal round trip under the code). SHOULD FIX 1 |
| VW-29 | vwap.py | reference id from the first bar | SURVIVED | 0 |  | equivalent: the member is called only on bars at or after 08:30 of CT date d, so the first bar seen is the 08:30 bar or the day is already a gap |
| CAL-1 | _calendar.py | a full session removed from both tables | skipped |  |  | ill-formed (the date occurs in both tables); rerun by hand removing it from EQUITY_FULL_SESSIONS only: killed (5+ tests, first test_the_modules_are_exactly_the_generators_output) |
| VX-1 | _vxn.py | one CLOSE string changed | killed | 2 | tables.py::test_the_modules_are_exactly_the_generators_output |  |
| VX-2 | _vxn.py | a dropped row put back | killed | 4 | tables.py::test_the_modules_are_exactly_the_generators_output |  |

### 5. Tests: what they pin, and what they do not

- Every case the stage prompt's Task 2 names is pinned: entry and exit times (all five), the event window (FOMC 13:00
  and ISM 09:00 on real research-window rows for all five; D9.5a moves the fills and the members emit what their rule
  says), a missing bar at a decision time (17:00, 08:59, 14:29, 14:58 for CP1; range bars, 15:00 for CP2; 08:30, 14:59,
  14:58 for CP3; 08:30, a scan bar, the exit bar for vxnband; 08:30, 08:45, 14:58 for vwap), the VXN value used only
  from its availability time (a recording table shows one read, at the 08:30 bar of d, of d-1's date), a CPI window
  (2025-05-13 07:30, bars 07:25-07:35: no intent for any of the five).
- The flatten: pinned with a synthetic F for the three ports (forced_flatten fills; no member exit). For vxnband and
  vwap the engine-closure path is pinned through the D9.7 forced exit (ForcedLimitRules), which exercises the same
  member code (a pending engine order, then a closed position); there is no synthetic-F case for them (NOTE 4).
- The previous evening's bars: the ports' kit builds them (17:00-17:05 on CT date d-1, with the post-holiday label)
  and the port tests pin that they are not read (my C1-9, C2-13 and C3-15 are killed). Coder B's engine-run tests
  never build them (only the direct-call V-read test starts at EVENING), so for vxnband and vwap the rule "only bars
  of CT date d are read" has no failing mutant (SHOULD FIX 1).
- No test passes vacuously: every "sends nothing" assertion has a sibling with the same bars that trades (for
  example the pending-order, non-full-session, CPI-window and instrument-change tests), and the mutant sweep shows
  which test kills each rule change.
- Direct-call tests are used only where the engine cannot reach the case (a None bar; bars the equity calendar never
  produces; a pending order held fixed; a position across a splice), as the coders' reports say.

### 6. Findings

No BLOCKING finding. One SHOULD FIX (a test gap, not a rule defect). Nine NOTEs.

1. **SHOULD FIX (tests). The engine-run tests of K1-vxnband-01 and K1-vwap-01 never feed the previous evening's
   bars, so the rule "only bars of CT date d are read" (S0.4, K7-L-01; vxnband.py:226-227, vwap.py:180-181) has no
   failing mutant.** tests/test_k1_members_vxnband.py and tests/test_k1_members_vwap.py (coder B's Day kit builds
   bars of CT date d only unless a test passes a negative start; only the direct-call V-read test does). My mutants
   VB-26 (vxnband reads the evening) and VW-28 (vwap reads it) pass all 89 coder-B tests, and on realistic bars
   they change trades: VB-26 lets the post-holiday evening's early_halt_ct label (the holiday's, by CT calendar date)
   mark the trade date after every early-halt holiday incomplete as C_prev, so the next date's band uses an older
   close (probe auditor_evening_probe.py: Wednesday 2025-05-28 sells under the mutant and does not trade under the
   code); VW-28 breaks vwap's 08:30 clock run on every date (no entry ever). The module code is correct on both
   counts (both skip the evening before any accumulation, and CP3's sibling pin kills the same mutant, C3-15).
   Smallest fix: one engine-run test per member whose days start at EVENING (the kit already supports negative
   minutes), for vxnband with the post-holiday evening carrying the holiday's label as a separate Day of the same
   trade date (the probe's construction), asserting the normal round trip and, for vxnband, that the Tuesday after
   Memorial Day stays a complete C_prev. No member code change.

2. **NOTE. K1-L-14 item 10(c) defers the tick-history check the catalog places before any bar is read.**
   reports/stage_e7_member_specs.md section 8, K1-L-14 "(c) the research window uses the frozen vendor_tick, the tick
   history is a confirmation-session check". C7 (C lines 134-135): "E.2 confirms that each tick was unchanged over
   2019-05..2026-06 before any bar is read, because CP2's buffer and several ML features are in ticks."
   reports/stage_e2a_vehicles.md holds no such confirmation. For the research window the exposure is a tick change
   on MNQ, M2K or MYM inside 2025-04-01..2026-06-19 (it would move CP2's buffer and every to_ticks conversion); I
   could not verify the history (no web in this brief). Smallest fix inside the frozen entry: in the Task 4 rulings,
   either cite a source for the three minimum price increments over the research window (CME rulebook chapters 361,
   363, CBOT 28, as C7 names them) or label the nine port trials "tick history unverified for the research window"
   in the return.
3. **NOTE. Cboe's publication time is observational (R-1b-4), and the frozen rule needs it before 08:30 CT.**
   vxnband.py:193 reads V at the 08:30 bar's close. The evidence is three consistent observations and no statement;
   the FRED copy (not the member's source) updates after 08:30 CT. The lead already flags this for the user; the
   return should carry "VXN availability before 08:30 CT observational, not stated" with the R-1b-1 label. No code
   change: the frozen text fixes 08:30 and the evidence supports it.
4. **NOTE. No synthetic-F flatten test for K1-vxnband-01 and K1-vwap-01** (tests/test_k1_members_vxnband.py,
   tests/test_k1_members_vwap.py). The prompt's Task 2 list names "the flatten"; the ports have it
   (test_cp*_position_open_at_a_synthetic_f_is_flattened_by_the_engine). The D9.7 forced-exit tests
   (test_an_engine_closure_ends_the_day, test_after_an_engine_closure_the_rule_continues) exercise the identical
   member path, and both members are flat by 14:59 by rule, so the gap is in the pin, not the rule. Smallest fix: one
   test per member with a synthetic F during the hold (coder B's Day kit would need a `flatten_from` field like coder
   A's); optional.
5. **NOTE. K1-L-08 (vwap counts sent entry intents, refused ones included) is one of two defensible readings of
   "entries have been made" (C 538, 547).** The other counts fills. The lead's is the conservative one (never more
   intents than the other), never sends an intent D9.3(a) would refuse, and differs only on full-session dates with
   engine refusals. Record the alternative in the rulings; no change.
6. **NOTE. vxnband's hold under a D9.5a-deferred entry fill is 28 minutes** (intent 12:59 -> fill 13:02 -> exit
   intent 13:29 -> fill 13:30; the same at 08:59 on ISM days), as K1-L-05 records. This follows from anchoring the
   exit on the entry-intent bar, which the entry names; the alternative anchor (30 minutes after the moved fill)
   would be two minutes later on at most one bar per FOMC or ISM date. No change.
7. **NOTE. `_calendar.py` starts at 2019-05-01, so vxn_for(2019-05-01) is None although the 2019-04-30 VXN row is in
   the table** (strategy/members/k1/_calendar.py:33 TABLE_RANGE; _event_common.py:51-52). No trade date is affected:
   MNQ's listing and S_X are 2019-05-06 (C8), whose V is the 2019-05-03 row. Coder B recorded it. No change.
8. **NOTE. cp2.py:59 `F_REGULAR_CT = time(15, 8)` is a literal** used only to close the trading window
   (cp2.py:84), never in a rule; it equals D line 391 and the K7 port has the same. If the lead prefers no clock
   literal, `rules.sessions.REGULAR_FLATTEN_CT["equity"]` would replace it; no behaviour change.
9. **NOTE. Two member behaviours are reachable only by direct calls and are pinned that way** (coder B's notes 3
   and 4): vwap's instrument-change exit is sent without the minimum hold (the engine's D9.3b refuses an early one
   and the member resends; in a run the engine raises on a splice with exposure), and vxnband's first breach uses the
   day's entry even when the account is not flat (impossible in a run: one entry per date, flat by F). Both follow
   the specs (C 558-559; E.3-L-08). No change.
10. **NOTE. The nine research dates without V (R-1b-5) and the R-1b-1 label** reduce K1-vxnband-01's research
   sample by 9 of 303 full-session dates; the entry's "If it is missing, no trade on d" makes this the rule as
   frozen. Report the count with the trial's result.

What I could not do: verify the tick history (finding 2) and Cboe's publication time (finding 3) beyond the saved
evidence, since this brief allows no web access; run the freeze itself (Task 4 is the lead's).

## Part 2: recomputation (Task 6)
