# Stage E.4 Part 3 (K3 FX), Task 2: MemberCoder-A report

Worker: MemberCoder-A-OpusXHigh (worker-xhigh, opus). Brief: reports/stage_e4_briefs/coder_common_K3.md
and coder_A_K3.md. Spec: reports/stage_e4c_member_specs.md sections 0-3 and 10. Finished 2026-09-27
(system clock 06:30 PDT). No commit, no bar data, no runner, no freeze in the repository, no web.

## Files

| File | sha256 | Lines |
|---|---|---|
| strategy/members/k3/_port_common.py | b4987d6028df07717075bbd8b909f29e6b8d1a4d0d738527617cb4dfb0c5c554 | 111 |
| strategy/members/k3/cp1.py | 6539cfd03d2cfbf9f634d666c94693821a3a0049696f66ba2e667dbc5dd018af | 168 |
| strategy/members/k3/cp2.py | 6551e9613d8b9f17fe2c5144dc6ea622e33dbe30eccf21198de78a8080fa0b80 | 160 |
| strategy/members/k3/cp3.py | b8d0b4c9a62b9973524c8f3e0d320fdb0fce5419a04da83b9bee56c184bb2432 | 219 |
| tests/test_e4_k3_members_a.py | 1101a0fa0f45150131507e922440ea7851d44ee0fdf1f007a6d3be28fed0a811 | 612 |
| tests/test_e4_k3_members_a_cp2.py | fa0115f50e848a5a4f231ce6a06a4170947df50d01eb1fad4ec9f25178f9c3b2 | 241 |
| tests/test_e4_k3_members_a_cp3.py | 98fcfa907183afda96e0ab47de8cefbfb4eb4a170eab0e88d7d438ab09fa6f0d | 246 |
| strategy/members/k3/mehedge.py | 81a6b2088fd0c712b05f28d3b7ee2fb6758bb711728514114cd3102b2e27d887 | 167 |
| strategy/members/k3/_mehedge_signal.py (generated) | b8cfa399cac9a0cc68298beb7c79891ee4f932bfd176d24cc386711fd03a24c8 | 300 |
| reports/stage_e4_briefs/gen_k3_mehedge.py (its generator) | e45980e25f488b41f7ed2fedb2772373e8fe01cba18fcf3a9b2db05e5da8ed08 | 226 |
| tests/test_e4_k3_members_m.py | 63259150ad6c63baba15ca778a91c647a9327b9c4ed5f2e1a6b99b41da3f08f2 | 309 |
| tests/test_e4_k3_members_m_signal.py | 99e2ed997821d2e190b4d24a525218213be265fb652f73be2e3b11f1a330a594 | 218 |

Copy check: an AST comparison with docstrings blanked shows the four modules equal to
strategy/members/k2/_port_common.py, cp1.py, cp2.py and cp3.py except in these places: the
exposure tuple, the error text ("K3 exposure"), MEMBER_ID, the import path (k3), the seven
factories and `__all__`. cp2's `__all__` also exports BUFFER_TICKS and RANGE_MINUTES. No rule
line differs. Nothing is imported from k2, k4 or k5 (pinned by
test_the_port_helpers_are_copied_not_imported). strategy/members/k3/__init__.py and all of
coder B's files are untouched.

## Declarations (S0.2), as the freeze test declares them under tmp_path

| Member | Module | 6E | 6A | 6B | 6C | 6J | 6S | 6N |
|---|---|---|---|---|---|---|---|---|
| K3-cp1-01 | strategy.members.k3.cp1 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| K3-cp2-01 | strategy.members.k3.cp2 | 8 | 9 | 10 | 11 | 12 | 13 | 14 |
| K3-cp3-01 | strategy.members.k3.cp3 | 15 | 16 | 17 | 18 | 19 | 20 | 21 |

Label `"<member id> <ROOT>"`, factory `make_<root lower>` (make_6e ... make_6n), legs
`(LegSpec(root, True),)`. The test is test_the_21_declarations_freeze_and_verify_under_tmp_path, which runs
write_cluster_freeze, load_cluster_freeze and verify_cluster_code on a tmp_path copy.

## Common (section 0) in _port_common.py

| Spec field | Code | Tests |
|---|---|---|
| S0.1 one leg, the vehicle; no E7/M6E/M6A/M6B | EXPOSURES l.42, LegFacts.legs l.56-57, leg_facts refusal l.61-63 | test_factories_name_the_label_and_trade_one_leg, test_leg_facts_refuses_a_root_outside_the_seven_vehicles |
| S0.2 label, factories, order | label l.69; factories in each module | test_factories_..., the freeze test |
| S0.3 q_c from the frozen table (1 on all seven) | leg_facts l.64-66 | test_frozen_clock_size_and_ticks_are_the_spec_values; qty checks in the buy tests |
| S0.4 CT clock, O/C from day_session_ct | ct_open l.79-81, leg_facts l.65 | test_frozen_clock_..., the *_keeps_the_ct_clock_in_both_regimes tests |
| S0.7 exit on the first present bar at/after the named bar; resent while refused; never duplicated while pending | exit_if_due l.93-106 | test_an_exit_is_not_sent_while_an_order_is_pending, test_cp1_a_refused_exit_is_resent_on_the_next_bar, *_missing_exit_bar_* |
| S0.10 integer vendor ticks | to_ticks l.84-86 | test_prices_become_integer_vendor_ticks (includes a float sum off the grid) |
| Never forward fill a None bar | each on_minute's first lines | test_a_none_bar_is_no_decision_and_changes_no_state |

## K3-cp1-01 (cp1.py)

| Spec field | Code | Tests (tests/test_e4_k3_members_a.py) |
|---|---|---|
| Signal: close of the 07:49 bar minus open of the 17:00 bar of d-1 (E.3-L-05) | constants l.51-52; first bar l.122-124 (open via asdict, R-T2-1, l.58-61); signal bar l.127-129; _side l.98-109 | test_cp1_buys_on_a_positive_signal_with_the_spec_clock, test_cp1_sells_on_a_negative_signal (the sign fixture makes close-close and open-open disagree) |
| Missing Globex bar or signal bar: no trade | _side l.100-101 | test_cp1_missing_globex_open_bar_is_no_trade_l05, test_cp1_missing_signal_bar_is_no_trade |
| Two instrument_ids on the signal bars: no trade; entry bar not guarded (E.3-L-06) | l.103-104 | test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06 |
| Zero signal: no trade | l.106-107 | test_cp1_zero_signal_is_no_trade |
| Entry on the 13:29 bar exactly (fills 13:30), q_c; one decision a day | l.53, l.130-136 | the buy/sell tests, test_cp1_missing_entry_bar_is_no_trade_l04, test_cp1_trades_once_per_trade_date_on_consecutive_days, test_cp1_state_resets_each_trade_date |
| Exit at or after 13:58 (fills 13:59); missing exit bar goes on the next present bar | l.54, l.120-121 | test_cp1_missing_exit_bar_sends_the_exit_on_the_next_present_bar (13:59 then 14:00), test_cp1_a_refused_exit_is_resent_on_the_next_bar |
| trading_windows (17:00-17:01 day -1; 07:49-07:50; 13:29-14:00) | l.88-93 | test_trading_windows_are_the_s0_12_intervals |
| Both clock regimes | CT only (ct_open) | test_cp1_keeps_the_ct_clock_in_both_regimes (CST 2026-01-13; CDT 2025-06-03; mismatch weeks 2026-03-10 and 2025-10-28; Globex opens on the clock-change Sundays for 2026-03-09 and 2025-11-03) |
| D9.5a (engine) | not read by the member | test_cp1_fill_in_the_d95a_guard_waits_two_minutes (13:30 gives 13:32, 13:29 gives 13:31), test_cp1_a_release_next_to_or_before_the_fill_leaves_it_alone (13:28, 13:31, FOMC 13:00, 07:30, 07:49), test_cp1_a_release_at_the_exit_fill_holds_the_exit |
| Flatten at F / D9.7 (engine) | no own exit after either | test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine, test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry (ForcedLimitRules, test only) |
| Early halts not tested by the port (engine F) | none | test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry (all five EC-CAL FX research halts: the 13:29 entry is refused with engine_flatten_window) |
| Roll blackout (engine) | none | test_cp1_a_roll_blackout_date_refuses_the_entry_and_nothing_is_resent |

## K3-cp2-01 (cp2.py)

| Spec field | Code | Tests (tests/test_e4_k3_members_a_cp2.py) |
|---|---|---|
| OR = present bars in [07:20, 07:35); RANGE_MINUTES = 15 | l.55, l.81, l.112-115 | test_cp2_literals_are_the_spec_values, test_cp2_the_opening_range_is_0720_to_0735 (the buy pair plus the sell-side pair: B-7 sells, B-6 does not, and a 14-minute range would sell at B-6), test_cp2_the_range_is_taken_from_the_present_bars, test_cp2_bars_before_0720_and_on_the_previous_evening_are_not_range_bars, test_cp2_the_range_has_no_instrument_guard |
| No range bar: no trade (E.3-L-08) | l.116-117 | test_cp2_without_an_opening_range_bar_there_is_no_trade |
| Buffer 4 x vendor_tick = 0.0002 (6E, 6A, 6C, 6S, 6N), 0.0004 (6B), 0.000002 (6J) | l.56, l.121-124 | test_cp2_literals_are_the_spec_values, test_cp2_buffer_table_is_recomputed_from_the_frozen_catalog (in the part-1 file), test_cp2_the_buffer_is_exactly_four_ticks_either_side (3 ticks: none; exactly 4: entry; both sides, all seven) |
| Eligible [07:35, 14:00); no entry from 14:00 | l.118 | test_cp2_no_entry_from_1400, test_cp2_entry_at_1359_is_flattened_by_the_engine_at_f |
| First qualifying bar uses the one entry, even if refused | l.127 | test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it, test_cp2_one_entry_per_trade_date_after_the_exit, test_cp2_state_resets_each_trade_date |
| Hold: 75 present bars from the bar after the decision bar; resent while refused; not while pending | l.57, l.88-97, l.106-107 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars (07:36 to 08:51), test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar, test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_release_at_the_exit_fill_holds_the_exit |
| No C-2 exit (E.3-L-07) | none | test_cp2_has_no_c_minus_2_exit (13:01 to 14:16) |
| F cuts an entry filled at 13:53 or later | engine | test_cp2_entry_at_1359_is_flattened_by_the_engine_at_f (14:00 to 15:08 forced), test_cp2_an_entry_filled_at_1353_meets_f_and_one_at_1352_exits_itself |
| trading_windows (07:20, 15:08) | l.58, l.83 | test_trading_windows_are_the_s0_12_intervals |
| Both clock regimes | CT only | test_cp2_keeps_the_ct_clock_in_both_regimes |
| D9.5a: the 07:30 release inside the range meets no fill | engine | test_cp2_the_0730_release_inside_the_range_meets_no_fill, test_cp2_a_release_next_to_the_fill_leaves_it_alone |
| Flatten / D9.7 / early halts (engine F) | none | test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine, test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry, test_cp2_does_not_test_early_halts_the_engine_flattens_at_f (five halts; 2026-04-03 F 08:00) |
| Missing trigger bar | a missing bar is not a bar | test_cp2_a_missing_trigger_bar_moves_the_entry_to_the_next_qualifying_bar |

## K3-cp3-01 (cp3.py)

| Spec field | Code | Tests (tests/test_e4_k3_members_a_cp3.py) |
|---|---|---|
| Daily bar [07:20, 14:00): H, L over present bars; C_d = 13:59 close | l.60, l.141-152 | test_cp3_the_daily_bar_is_0720_to_1400_with_the_1359_close (extremes at 07:10, 14:15 and a 14:00 close excluded; the 07:20 bar included) |
| Complete day: 07:20 and 13:59 bars, no halt, one instrument_id; finalised on the next trade date | l.123-139 | test_cp3_uses_d_minus_1_only_after_it_is_finalised, test_cp3_a_day_with_two_instrument_ids_is_incomplete, test_cp3_missing_0720_bar_is_no_trade_and_the_day_is_incomplete |
| d-1 = the most recent complete day (E.3-L-09); warm-up: no trade | l.133-137, l.157-159 | test_cp3_d_minus_1_is_the_most_recent_complete_day, the buy test (MON is warm-up) |
| Early-halt day d not traded (E.3-L-11; the 07:20 bar's CT date is d, K3-L-04) | l.142-143, l.156-157 | test_cp3_early_halt_day_is_not_traded_and_is_incomplete (all five EC-CAL FX research halts, all seven roots), test_cp3_a_halt_label_on_the_evening_bars_only_does_not_block_day_d |
| Guard: d-1's instrument_id = the 07:20 bar's | l.161-162 | test_cp3_instrument_guard_compares_d_minus_1_with_the_0720_bar, test_cp3_the_guard_reads_the_0720_bar_only |
| Range > 0; CLV >= 0.8 buys, <= 0.2 sells, exact integers | l.57-58, l.75-89 | test_cp3_prior_clv_at_08_buys_..., test_cp3_prior_clv_at_02_sells, test_cp3_clv_strictly_between_the_cuts_is_no_trade, test_cp3_clv_cuts_are_compared_exactly, test_cp3_zero_range_is_no_trade |
| Entry on the 07:20 bar exactly (fills 07:21); one decision a day | l.181-188 | the buy test, test_cp3_missing_entry_bar_is_no_trade_on_a_later_bar, test_cp3_one_entry_per_trade_date_even_when_the_engine_refuses_it |
| Exit at or after 13:58 (fills 13:59); missing exit bar goes on the next present bar | l.61, l.179-180 | test_cp3_prior_clv_at_08_buys_..., test_cp3_missing_exit_bar_sends_the_exit_on_the_next_present_bar |
| trading_windows (07:20, 14:00) | l.120 | test_trading_windows_are_the_s0_12_intervals |
| Both clock regimes | CT only | test_cp3_keeps_the_ct_clock_in_both_regimes |
| D9.5a / flatten / D9.7 (engine) | none | test_cp3_fill_in_the_d95a_guard_waits_two_minutes, test_cp3_releases_while_holding_meet_no_fill_and_one_at_the_exit_holds_it, test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine, test_cp3_d97_engine_exit_no_duplicate_exit_and_no_reentry |

## Tables pinned

- CP2 buffer table: test_cp2_buffer_table_is_recomputed_from_the_frozen_catalog checks the catalog's
  sha256 against reports/stage_e1_freeze.json, parses C lines 304-312 and asserts
  BUFFER_TICKS x vendor_tick equals the catalog's buffer on all seven, with the most active contract
  equal to the vehicle. The ports have no other literal table.
- The five EC-CAL FX research-window halts the tests use (and Topstep F on each, from rules.sessions)
  are recomputed in test_ec_cal_fx_research_window_halts_are_the_spec_dates. 316 trade dates, matching
  specs line 36.

## Mutation spot-check (scratch script, not in the repository)

Each of these changes to a module constant or method made a named test fail: RANGE_MINUTES 14 or 16,
BUFFER_TICKS 3 or 5, HOLD_BARS 74, CP1 signal/entry/exit offsets, CP3 C-1 and C-2 offsets, CLV buy
cut 0.81, CP3 ignoring the halt, CP1 ignoring the instrument guard. For RANGE_MINUTES = 14 the buy
pair still passes and the sell-side pair is what fails, as the brief intends.

## Implementation choices (none can change a trade)

- The helper module is named _port_common.py, and it is the K2 helper module with its exposure tuple changed.
- cp2 exports BUFFER_TICKS and RANGE_MINUTES in `__all__` (K5 did the same).
- The tests are split into three files that share the kit in tests/test_e4_k3_members_a.py, adapted from
  tests/test_e4_k5_members_a.py (a copy, not an import).
- The synthetic base prices sit on the tick grid: 6E 1.10, 6A 0.65, 6B 1.30, 6C 0.73, 6J 0.0067,
  6S 1.15, 6N 0.60.

## Brief items that do not apply to the ports

- "A moved and a dropped event": the ports read no fix instant and no event table (the spec says so
  in S0.4 and in section 1-3's "copied unchanged"). The tests cover the other side of this: the CT
  times do not move in the mismatch weeks, and a date outside the engine's window is refused.
- There is no K3-L-04 FX_FULL_SESSIONS read. K3-L-04 binds the new members. CP3 keeps E.3-L-11,
  and CP1 and CP2 do not test halts (a port).

## Observation for the lead (ruled: K3-L-11, 06:50; the ports are unchanged by it)

EC-CAL FX (data.group_session.load_group_calendar("fx")) lists the US holidays 2025-09-01,
2025-11-27, 2026-01-19, 2026-02-16 and 2026-05-25 as trade dates with no early halt. The metals and
rates calendars mark all five (13:30 and 12:00). rules.sessions puts Topstep's F on the five FX dates at
11:30 (09-01, 11-27) or 11:45 (the others). Their bars therefore carry no early_halt_ct. Under the spec as written
(E.3-L-11 reads the bar's label), the results are:
- CP3 enters on the 07:20 bar and the engine flattens at F. This is pinned by
  test_cp3_a_us_holiday_ec_cal_fx_does_not_mark_is_traded_and_flattened_at_f.
- CP1's 13:29 entry is refused.
- CP2 trades and is flattened at F.

The lead ruled K3-L-11 at 06:50: an FX date with an early engine F is an early close for C4.
Coder B's FX_FULL_SESSIONS excludes these dates, and K3-mehedge-01 reads that table. The ports
follow D6 and are unchanged (the engine's F governs them), so the CP3 test above stays as written.

## K3-mehedge-01 (6J only; the lead's message after Task 2, specs sections 6 and 11)

Files: strategy/members/k3/mehedge.py (factory make_6j only: the EURO STOXX 50 was not obtained,
so there is no 6E trial and no make_6e); strategy/members/k3/_mehedge_signal.py, generated by
reports/stage_e4_briefs/gen_k3_mehedge.py; tests/test_e4_k3_members_m.py (the member) and
tests/test_e4_k3_members_m_signal.py (the table pin). mehedge imports MONTH_ENDS,
FX_FULL_SESSIONS and EW_BANK_HOLIDAYS from coder B's _calendar.py and T_L from _clocks.py. It
reads them only; T_L is a tuple of (ISO date, "HH:MM") pairs. Declared ordinal 27: the ordinals
close up after the undeclared 6E (the freeze test runs under tmp_path).

**The table.** There are 85 months, 2019-05 to 2026-05, with ME(m) equal to MONTH_ENDS and to the
release check's in-coverage month_ends. None is None and none is zero.
- R_eq(m) = ln(P_a / P_b), computed in Decimal (prec 34) and stored as a float.
- The four saved Nikkei files are sha256-checked against reports/stage_e4c_release_check.json
  index.N225.
- Overlaps: every date's close is equal in all files holding it (checked). MEHEDGE_CLOSES_6J lists,
  for each month, the P_a and P_b dates and closes, and the newest capture holding each close.
- "Missing": the Tokyo business day that holds P_a or P_b (EC-JP from the release check) has no
  close. The files' dates over 2019-04-01..2026-06-19 equal EC-JP's 1,761 business days, so no month
  is None.
- The footer's one non-ASCII byte means the files are read as latin-1.

| Spec field | Code (mehedge.py) | Tests |
|---|---|---|
| Event set: ME(m) in FX_FULL_SESSIONS (K3-L-04, K3-L-11), not an E&W bank holiday, no shift (K3-L-06) | event_sides l.75-90 | test_the_event_set_is_recomputed_from_ec_cal_and_ec_ew (EC-CAL halt, engine F 15:08 and the release check's EC-EW, recomputed independently), test_a_halted_month_end_is_not_traded (2025-11-28, with and without the bar label), test_an_england_and_wales_bank_holiday_month_end_is_not_traded (2020-08-31; 2021-05-31), test_a_day_that_is_not_a_month_end_is_not_traded |
| Signal: R_eq from the literal table for the same ME(m); 0 or None: no trade | hedge_side l.67-72; event_sides l.84-87 | test_hedge_side, test_a_missing_close_or_a_zero_r_eq_is_no_trade (None, 0.0, -0.0), test_a_signal_row_for_another_date_is_no_trade, test_the_signal_rows_name_the_same_month_ends_as_month_ends |
| Table: P_a strictly before ME's date, P_b in m-1, no close on/after ME | generator r_eq_row; _mehedge_signal.py | test_the_table_is_recomputed_from_the_saved_files, test_no_close_on_or_after_the_month_end_enters_the_table (every close dated on or after ME(m) replaced by garbage: each value unchanged), test_the_closes_used_are_listed_with_a_file_that_holds_them, test_spot_rows_by_hand (FRED spot values), test_a_missing_close_gives_none_in_the_generator_and_here, test_the_generator_rebuilds_the_written_table |
| Entry: SELL if R_eq > 0, BUY if < 0; the bar at T_L-61 exactly (fill T_L-60) | l.57, fix_minutes l.93-99, on_minute l.154-159 | test_entry_at_t_l_minus_61_and_exit_at_t_l_minus_4_in_both_regimes (CDT 2025-09-30; mismatch 2025-10-31 and 2024-03-28 at 11:00; CST 2026-01-30 and 2025-02-28 buy; 2026-03-31 buy), test_the_literal_times_standard_and_mismatch, test_the_clock_is_the_16_00_london_fix_in_ct_on_every_traded_month_end (zoneinfo), test_the_missing_t_l_minus_61_bar_is_no_trade |
| Exit: first bar at or after T_L-4 (fill T_L-3); resent while refused; whatever the instrument_id (K3-L-03) | l.58, l.152-153 | the regime test, test_the_missing_t_l_minus_4_bar_moves_the_exit_to_the_next_present_bar, test_a_refused_exit_is_resent, test_the_exit_is_sent_whatever_the_exit_bars_instrument_id (a direct call: the engine refuses a position across a contract change) |
| trading_windows (08:59, 09:58); (09:59, 10:58) | trading_windows_for l.102-106 | test_trading_windows_are_the_s0_12_intervals |
| Engine backstops | none | test_d97_engine_exit_no_duplicate_exit_and_no_reentry, test_a_position_open_at_a_synthetic_f_is_flattened_by_the_engine, test_the_d95a_guard_moves_a_fill_and_a_release_beside_it_does_not (a 09:00 release), test_a_roll_blackout_month_end_refuses_the_entry_and_nothing_is_resent, test_consecutive_month_ends_each_trade_once |

Mutation spot-check (scratch): each of these changes made a named test fail:
- entry offset 60, or exit offset 3;
- a flipped side;
- ignoring EW_BANK_HOLIDAYS, or ignoring FX_FULL_SESSIONS.

Implementation choices (none changes a trade):
- The event map joins MONTH_ENDS and the signal table by month and requires the same ME date. A test
  pins that they agree on all 85 months.
- The trading windows are derived from T_L's distinct CT values; a test pins them to S0.12.
- The generator was written by me. The lead named its path, but it did not exist.

## Not finished

Nothing in scope.

## Test command and result

`nice -n 10 uv run pytest -q tests/test_e4_k3_members_a.py tests/test_e4_k3_members_a_cp2.py tests/test_e4_k3_members_a_cp3.py tests/test_e4_k3_members_m.py tests/test_e4_k3_members_m_signal.py tests/test_stage_e_freeze.py tests/test_stage_e_template.py`
(no PYTHONPYCACHEPREFIX set; run after coder B's _calendar.py and _clocks.py appeared, 06:43).
Last line, verbatim:

    414 passed in 10.97s

(Before mehedge: the ports' run was `362 passed in 10.12s`.) `uv run ruff check` on all my files,
including the generator: "All checks passed!".
