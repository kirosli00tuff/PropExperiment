# Stage E.4 Part 1 Task 2: MemberCoder-A-OpusXHigh report

Worker file worker-xhigh, model opus, effort xhigh. Brief: reports/stage_e4_briefs/coder_common.md
and coder_A.md, specs reports/stage_e4_member_specs.md sections 0-3, 8, 10 (section 11 is still
PENDING, but none of my members reads a release instant). Finished 2026-09-27 at 02:30 PDT by the
system clock. The lead reported a process restart at about 02:25. Afterwards every file below still
matched the hash recorded before the restart, and the test run was repeated with the same result.

## Files (sha256)

| File | sha256 | Lines |
|---|---|---|
| strategy/members/k4/_calendar.py | a674e806169aec193dd920157289447132d6a848a252bc63b6d8efa8be763d78 | generated (K4-L-13) |
| strategy/members/k4/_port_common.py | 920a92a0769e236b58c42eeea0e76bfed4725cafd50ea22ce2972effc88790df | 110 |
| strategy/members/k4/cp1.py | 6f310ba708991562e00ce5b974f89e33747447df0a16e37eb9134fa8512a6bba | 145 |
| strategy/members/k4/cp2.py | 5b81d670b167c40e4fea5a1b0bf741811e92e01e1dcbea0d4d734b64da6be3c1 | 134 |
| strategy/members/k4/cp3.py | cc9b17c12719fe6a4f0d24220a59758c64a90bed686c64401e0f4a5cf1e5fe7a | 195 |
| strategy/members/k4/ovr.py | c221eada1cb67db2a1656b255980f67a03036c1a79972baa05e97884b0ce7494 | 210 |
| tests/test_e4_k4_members_a.py | 405e6f824abbeda9aab99e558835577ad9d61ffa39b8f4493f20b6d6df504296 | 717 |
| tests/test_e4_k4_members_a_ovr.py | 947ec504b79be0b17292c7212b684ece72980ce9081c3998c84f6ae34b495d56 | 392 |
| reports/stage_e4_briefs/gen_k4_calendar.py | ae96040256811f21e23646b4763d8d0037006da1286efa3c8fd9be9bd501e392 | one-off generator |

All six module files pass `screening.stage_e_freeze.check_member_source(..., "K4")` with no
refusals. The test `test_every_coder_a_file_passes_the_freeze_static_check` checks this. I did not
touch strategy/members/k4/`__init__.py` (still 0 bytes), any of Coder B's files, the harness, or
any frozen file. There are no commits.

Test (reference form, no PYTHONPYCACHEPREFIX, nice 10):

    nice -n 10 uv run pytest -q tests/test_e4_k4_members_a.py tests/test_e4_k4_members_a_ovr.py tests/test_stage_e_freeze.py tests/test_stage_e_template.py

Last line, verbatim (after the 02:40 rulings, run at 02:33 by the system clock): `181 passed in 3.90s`.
My two files hold 134 of the 181 tests. Before the rulings the same command gave `175 passed in 3.40s`.

## ENERGY_FULL_SESSIONS (EC-CAL table, written first; trimmed by K4-L-13)

- Constants, name and format unchanged (Coder B's apipre imports them): `ENERGY_FULL_SESSIONS` (a
  tuple of ISO date strings, oldest first, now **1784 dates, 2019-05-01..2026-06-18**),
  `ENERGY_FULL_SESSIONS_SOURCE` (names `load_group_calendar('energy')`, the file and the rule, now
  `trade_dates_between(2019-05-01, 2026-06-19)`), and `ENERGY_FULL_SESSIONS_SOURCE_SHA256` =
  ef90ef8d19df6e2d87cfeb57a224d49a5ba95c66e22cf27bee67b4741f052806 (data/calendars/energy.py,
  unchanged).
- Rule (lead ruling K4-L-13, 02:40): `trade_dates_between(cal, 2019-05-01, 2026-06-19)`, EC-CAL's own
  coverage, keeping dates whose `early_halt_ct` is None. The first version used the brief's
  2019-04-01..2026-06-30 (1813 dates). Trimming removed the 22 weekdays of April 2019, including
  2019-04-19 (Good Friday, a CME closure the calendar does not cover), and 2026-06-22..30 (7 dates).
  The generator, reports/stage_e4_briefs/gen_k4_calendar.py (imported by nothing), now asserts that
  its range equals `cal.coverage`.
- Pin: `test_energy_full_sessions_is_recomputed_from_ec_cal` asserts the coverage is
  2019-05-01..2026-06-19. It recomputes the table over it, checks equality, the first and last
  dates, the source text and sha256, and that the dates are sorted and unique.
- Spot checks: `test_energy_full_sessions_spot_checks` confirms that 2019-04-19, 2019-04-30,
  2026-06-22, 2026-06-30, the early halts 2025-07-04, 2025-12-24 and 2026-06-19, and the closures
  2025-04-18 and 2025-12-25 are absent. 2019-05-01, 2025-07-03 and 2026-06-18 are present.
- ovr with fewer than 20 table dates before d does not trade. The existing check in ovr.py line 160
  (`len(refs) < REFERENCE_DATES`) enforces this, so ovr.py is unchanged. The new
  `test_ovr_fewer_than_20_table_dates_before_d_is_no_trade_k4_l13` pins it. The run starts on
  2019-05-01, so FULL[19] has 19 in-run dates, 95 values and an r above their P90, and still does not
  trade. FULL[20] trades. An in-memory mutant that pads short reference sets to 20 fails this test.

## K4-cp1-01 (spec section 1), strategy/members/k4/cp1.py

| Spec field | Code lines | Tests (tests/test_e4_k4_members_a.py) |
|---|---|---|
| Legs, label, factories make_mcl / make_ng | 76-80, 137-142; `_port_common` 60-69 | test_factories_name_the_label_and_trade_one_leg |
| q_c from the frozen table (MCL 4, NG 1) | 134; `_port_common` 64-69 | test_cp1_buys_on_a_positive_signal_at_1300_and_exits_at_1329 (checks fill qty per root); test_frozen_clock_and_size_are_o_0800_c_1330_and_q_c_4_mcl_1_ng |
| Signal bars: the 17:00 bar of d-1 (open) and the 08:29 bar (close), in ticks | 49-50, 56-59, 120-126 | ..._at_1300_and_exits_at_1329 (decoy prices), test_cp1_sells_on_a_negative_signal |
| Missing 17:00 bar: no trade (E.3-L-05) | 97-99 | test_cp1_missing_globex_open_bar_is_no_trade_l05 |
| Missing 08:29 bar: no trade | 97-99 | test_cp1_missing_0829_signal_bar_is_no_trade |
| Two instrument_ids: no trade; the entry bar is not guarded (E.3-L-06) | 100-102 | test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06 |
| Zero signal: no trade | 103-105 | test_cp1_zero_signal_is_no_trade |
| Entry on the exact 12:59 bar, fill 13:00 | 51, 84, 127-134 | ..._at_1300_and_exits_at_1329 |
| Missing 12:59 bar: no trade (E.3-L-04) | 127 | test_cp1_missing_1259_entry_bar_is_no_trade_l04 |
| Exit on the first bar at or after 13:28; a missing 13:28 bar sends it on 13:29; a refused exit is resent | 52, 85, 118-119; `_port_common` 94-107 | test_cp1_missing_1328_bar_sends_the_exit_on_1329, test_cp1_a_refused_exit_is_resent_on_the_next_bar |
| One entry per trade date | 130 | test_cp1_trades_once_per_trade_date_on_consecutive_days |
| D9.5a (the FOMC 13:00 fill): moved by the engine; a release next to it leaves the fill alone | none (engine) | test_cp1_fill_in_the_d95a_guard_waits_two_minutes, test_cp1_a_release_next_to_the_fill_leaves_it_alone |
| Flatten at F by the engine | none (engine) | test_cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine |
| D9.7: the engine exits; the member sends no duplicate exit and no re-entry | 118-119, 130 | test_cp1_d97_engine_exit_no_duplicate_exit_and_no_reentry |
| Early halts not tested (a port): the engine refuses the 12:59 entry on 2025-05-26 | none | test_cp1_does_not_test_early_halts_the_engine_refuses_the_entry |
| trading_windows (17:00-17:01 on d-1), (08:29, 08:30), (12:59, 13:30) | 86-90 | test_trading_windows_are_the_s0_12_intervals |

## K4-cp2-01 (spec section 2), strategy/members/k4/cp2.py

| Spec field | Code lines | Tests |
|---|---|---|
| OR from the present bars in [08:00, 08:15); no OR bar: no trade | 50, 76, 107-111 | test_cp2_without_an_opening_range_bar_there_is_no_trade, test_cp2_the_range_is_taken_from_the_present_bars, test_cp2_bars_before_o_and_on_the_previous_evening_are_not_range_bars |
| Buffer = 4 vendor ticks (K4-L-06); the literals 0.04 and 0.004 are pinned | 51, 116-119 | test_cp2_buffer_literals_are_4_vendor_ticks_k4_l06 |
| Buffer at exactly 4 ticks (>= and <=; 3 ticks does not trade), both roots | 116-119 | test_cp2_the_buffer_is_exactly_four_ticks_either_side[MCL/NG] |
| Eligible bars [08:15, 13:30); no entry from 13:30 | 113 | test_cp2_no_entry_from_1330, test_cp2_the_last_eligible_bar_1329_exits_75_bars_later |
| 75-bar hold counted in present bars (E.3-L-07); a missing bar in the hold moves the exit one bar | 52, 83-91, 99-100 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MCL/NG], test_cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar, test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill |
| No C-2 exit | none (by construction) | test_cp2_has_no_c_minus_2_exit |
| One entry per trade date, even when the first trigger is refused (E.3-L-08) | 111, 122 | test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it, test_cp2_one_entry_per_trade_date_after_the_exit |
| Flatten at F by the engine | none | test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine |
| D9.7: no duplicate exit, no re-entry | 99-100, 111 | test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry |
| Early halts not tested: on 2025-05-26 the port trades and the engine flattens at 11:30 | none | test_cp2_does_not_test_early_halts_the_engine_flattens_at_f |
| State reset per trade date | 81-82, 97-98 | test_cp2_state_resets_each_trade_date |
| trading_windows (08:00, 15:08) | 53, 78 | test_trading_windows_are_the_s0_12_intervals |

## K4-cp3-01 (spec section 3), strategy/members/k4/cp3.py

| Spec field | Code lines | Tests |
|---|---|---|
| Daily bar over [08:00, 13:30): H/L from the present bars, C_d = close of 13:29 | 57, 114, 138-149 | test_cp3_prior_clv_at_08_buys_on_the_0800_bar_and_exits_at_1329[MCL/NG] (extreme bars outside the window are ignored) |
| Complete day: the 08:00 and 13:29 bars exist, no halt, one instrument_id; finalised on roll | 120-136 | test_cp3_d_minus_1_is_the_most_recent_complete_day, test_cp3_a_day_with_two_instrument_ids_is_incomplete, test_cp3_missing_0800_bar_is_no_trade_and_the_day_is_incomplete |
| d-1 = the most recent complete daily bar; warm-up: no trade | 130-133, 156-157 | test_cp3_uses_d_minus_1_only_after_it_is_finalised; warm-up in the first cp3 test |
| Instrument guard: d-1 against the 08:00 bar | 158-159 | test_cp3_instrument_guard_compares_d_minus_1_with_the_0800_bar |
| CLV cuts non-strict and exact (0.8, 0.2); zero range | 54-55, 72-86 | test_cp3_clv_cuts_are_compared_exactly (13 cases), test_cp3_prior_clv_at_02_sells, test_cp3_clv_strictly_between_the_cuts_is_no_trade, test_cp3_zero_range_is_no_trade |
| An early-halt day d is not traded and is incomplete | 139-140, 153-154 | test_cp3_early_halt_day_is_not_traded_and_is_incomplete (2025-05-26; the engine would have accepted the 08:00 entry) |
| Entry on the 08:00 bar (fill 08:01); exit on the first bar at or after 13:28 | 58, 115, 176-185 | ..._buys_on_the_0800_bar_..., test_cp3_missing_1328_bar_sends_the_exit_on_1329 |
| D9.5a, flatten, D9.7 | none (engine); 176-180 | test_cp3_fill_in_the_d95a_guard_waits_two_minutes, test_cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine, test_cp3_d97_engine_exit_no_duplicate_exit_and_no_reentry |
| trading_windows (08:00, 13:30) | 117 | test_trading_windows_are_the_s0_12_intervals |

## K4-ovr-01 (spec section 8), strategy/members/k4/ovr.py

| Spec field | Code lines | Tests (tests/test_e4_k4_members_a_ovr.py unless noted) |
|---|---|---|
| Decision times 09:00-13:00; entry on the bar at t-1, fill at t; exit on the first bar at or after t+58, fill t+59 | 61-65, 124-126, 185-198 | test_decision_times_and_the_ladder_cuts, test_ovr_buys_at_or_below_p10_fills_at_t_and_exits_at_t_plus_59[MCL/NG] (checks q_c 4/1), test_ovr_the_five_decision_times_back_to_back_never_overlap |
| r(t) = (tc - to)/to from integer ticks as a float, using the open of the bar at t-60 and the close of the bar at t-1 | 83-87, 143-152, 180-183 | test_hourly_return_from_integer_ticks, test_ovr_r_uses_the_t_minus_60_open_and_the_t_minus_1_close (decoy prices) |
| C10: open of t-60 <= 0 means no trade at t, and such a reference value is not counted | 85-86 | test_ovr_c10_open_of_t_minus_60_at_or_below_zero_is_no_trade_at_t (0 and negative, both roots), test_ovr_c10_a_reference_value_with_open_at_or_below_zero_is_not_counted (direct calls) |
| Signal guard per t: both bars present, one instrument_id | 145-150 | test_ovr_signal_bars_on_two_instrument_ids_block_that_t_only, test_ovr_a_missing_signal_bar_is_no_trade_at_that_t[08:59/08:00] |
| Reference dates = 20 most recent ENERGY_FULL_SESSIONS dates strictly before d | 66, 72-80, 158 | test_reference_dates_are_the_20_full_sessions_strictly_before_d, test_ovr_only_the_20_most_recent_dates_are_referenced |
| Fewer than 20 table dates before d: no trade (K4-L-13) | 160 | test_ovr_fewer_than_20_table_dates_before_d_is_no_trade_k4_l13 |
| Early-halt dates are not reference dates; roll-blackout dates count | 72-80 (table) | test_ovr_early_halt_dates_are_not_reference_dates, test_ovr_a_roll_blackout_reference_date_counts (StageERules with a blackout) |
| Missing bars reduce the count; an absent date keeps its slot (K4-L-08); at least 80 values | 67, 161-164 | test_ovr_absent_dates_keep_their_slot_and_80_values_are_needed (80 trades, 75 does not), test_ovr_a_date_with_missing_bars_contributes_fewer_values (84 trades, 79 does not), test_ovr_a_reference_value_with_two_instrument_ids_is_not_counted |
| Warm-up (K4-L-09) | 133-135, 159-160 | test_ovr_warm_up_needs_all_20_reference_dates_in_the_run_k4_l09 (95 in-run values, still no trade) |
| numpy.percentile linear on floats; r <= P10 buys, r >= P90 sells; tie means no trade (K4-L-10) | 68-69, 90-98 | test_percentile_side_non_strict_cuts_and_the_tie, test_percentile_side_uses_numpy_linear (separates it from lower/higher/nearest), test_ovr_cut_boundaries_on_the_ladder |
| No overlap: entry only when flat with no pending order | 192-193 | ..._five_decision_times_back_to_back_never_overlap, test_ovr_a_missing_exit_bar_moves_the_exit_and_skips_the_overlapping_entry, test_ovr_d95a_deferred_exit_keeps_the_next_t_out |
| Missing exit bar: the exit goes on the first later present bar | 188-191 | test_ovr_a_missing_exit_bar_moves_the_exit_and_skips_the_overlapping_entry |
| An early-halt day d is not traded at any t | 155-156 | test_ovr_an_early_halt_trade_date_is_not_traded (2025-09-01, where F 11:30 would have allowed 08:59 and 09:59) |
| D9.7: no duplicate exit, no re-entry at that t, later t still trade | 188-193; `_port_common` 100-101 | test_ovr_d97_engine_exit_later_decision_times_still_trade, test_ovr_d97_engine_exit_on_the_exit_bar_is_not_duplicated |
| D9.5a release at t and next to t; flatten at F | none (engine) | test_ovr_d95a_release_at_t_defers_the_entry_fill, test_ovr_d95a_release_next_to_t_leaves_the_fill_alone, test_ovr_position_open_at_a_synthetic_f_is_flattened_by_the_engine |
| Values of earlier days carry over; later days trade | 131-141 | test_ovr_state_carries_across_days_and_trades_again_the_next_day |
| trading_windows (08:00, 14:00) | 70, 128 | test_trading_windows_are_the_s0_12_intervals (test_e4_k4_members_a.py) |

## Implementation choices (none can change a trade)

- `_port_common.py` is copied in structure from K2's version (never imported from it), with
  EXPOSURES = ("MCL", "NG"). `exit_if_due` sends nothing while any order is pending, and that
  includes an engine-forced order. This is how "no duplicate exit" after D9.7 or F is implemented.
- cp1, cp2 and cp3 copy the E.3 K2 logic with the energy clock (O 08:00, C 13:30 from the frozen
  tables). `F_REGULAR_CT = 15:08` is used only for cp2's trading window.
- How ovr stores its state:
  - `reference_dates` runs `numpy.searchsorted` over the table's ordinals.
  - A day's valid r values go into history when the trade date changes, so today's values never
    enter today's reference set.
  - History is pruned on each roll to the dates a later reference set can still use.
  - `_exit_at` is set when the entry intent is emitted. If the engine refuses that intent, no
    position exists and the exit test never fires.
  - ovr reads a bar's open through `asdict(bar)["open"]` (ruling R-T2-1).
- _calendar.py prints 5 dates per line.
- The tests reuse E.3's synthetic kit, adapted: sparse days (`only`) and a base of MCL 70.00 and NG
  3.000. The ovr file imports this kit from tests/test_e4_k4_members_a.py.

## Lead rulings applied (02:40)

1. **K4-L-13.** ENERGY_FULL_SESSIONS spans EC-CAL's coverage only (see the table section above).
   Changed files: _calendar.py, gen_k4_calendar.py, tests/test_e4_k4_members_a.py (pin and spot
   checks) and tests/test_e4_k4_members_a_ovr.py (the new fewer-than-20 test). No member module
   changed.
2. **K4-L-14 confirmed my reading, with no code change.** Each ovr reference value counts when its
   own two bars carry one instrument_id; it need not match day d's contract. Day d's guard covers
   the t-60 and t-1 bars. Pinned by test_ovr_reference_values_of_an_earlier_contract_count,
   test_ovr_a_reference_value_with_two_instrument_ids_is_not_counted and
   test_ovr_signal_bars_on_two_instrument_ids_block_that_t_only.
3. The ovr early-halt test is applied to the decision bar (S0.8). Every bar of an early-halt CT
   date carries the label, so this is the same as section 8's "a trade date whose bars carry
   early_halt_ct".

## Observations for the lead

- **D9.7 cannot fire on MCL or NG in the real engine.** Both are DCB-only: `rules.price_limits.HARD_LIMIT_PRODUCTS`
  excludes them, and both the engine's forced_reasons and its entry check test membership in that
  set. The D9.7 tests therefore use a test-only `ForcedLimitRules(StageERules)` subclass that queues
  a `price_limit_exit` at chosen bars. The engine then fills it normally, because `_locked` is False
  for non-hard-limit roots. This tests the member's reaction to an engine-forced exit, not the price
  bands.
- **No moved or dropped release test.** The prompt's "a moved release and a dropped release" cases
  do not apply to my members: none of the four reads a release instant (spec sections 1-3, 8). What
  does apply is the D9.5a guard. For each member it is tested at the fill minute and next to it. For
  ovr it is also tested on a deferred exit, which keeps the next t from trading.
- **cp2 on early-halt days.** The port trades on an early-halt day (C line 85), and the engine
  flattens it at 11:30. **cp1 on early-halt days**: the engine refuses the 12:59 entry with
  `engine_flatten_window`. Both are as the spec states.
- **Mutation check.** An in-memory check was run from the scratchpad; no repository file was
  changed. Each mutant was killed by at least one test: MIN_VALUES 75, warm-up off, exit at t+59,
  no halt check (ovr and cp3), no per-t instrument guard, and percentile method "nearest".

## Not finished

Nothing under the brief is left. Coder B's files did not yet exist when I checked, so no test here
imports them.
