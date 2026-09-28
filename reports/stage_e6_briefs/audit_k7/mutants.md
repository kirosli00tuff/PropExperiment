| # | Mutant | File | What it tests | Result | Killing tests (count; first two) |
|---|---|---|---|---|---|
| 1 | cp1-direction | cp1.py | direction with the signal | KILLED | 16; test_cp1_a_refused_exit_is_resent_on_the_next_bar, test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| 2 | cp1-entry-31 | cp1.py | entry bar C-31 (14:29) | KILLED | 20; test_cp1_a_refused_exit_is_resent_on_the_next_bar, test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| 3 | cp1-exit-2 | cp1.py | exit bar C-2 (14:58) | KILLED | 13; test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700, test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides |
| 4 | cp1-first-1700 | cp1.py | first bar 17:00 on CT date d-1 | KILLED | 6; test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides, test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| 5 | cp1-first-day | cp1.py | first bar by clock alone (K7-L-01) | KILLED | 2; test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides, test_cp1_monday_from_2026_06_01_the_sunday_1700_open_decides |
| 6 | cp1-first-open | cp1.py | signal uses the first bar's OPEN | KILLED | 16; test_cp1_a_refused_exit_is_resent_on_the_next_bar, test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| 7 | cp1-idguard | cp1.py | two instrument_ids: no trade | KILLED | 1; test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06 |
| 8 | cp1-once | cp1.py | one entry decision per date | KILLED | 1; test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| 9 | cp1-otherdate | cp1.py | bars of another CT date never read | KILLED | 4; test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700, test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides |
| 10 | cp1-signal-29 | cp1.py | signal bar O+29 (08:59) | KILLED | 17; test_cp1_a_refused_exit_is_resent_on_the_next_bar, test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| 11 | cp1-signal-close | cp1.py | signal uses the 08:59 CLOSE | KILLED | 2; test_cp1_sells_on_a_negative_signal, test_cp1_the_signal_is_one_tick_either_side_of_zero |
| 12 | cp1-zero | cp1.py | zero signal: no trade | KILLED | 1; test_cp1_zero_signal_is_no_trade |
| 13 | pc-exit-date | _port_common.py | exit only on CT date d | KILLED | 1; test_an_exit_is_not_sent_while_an_order_is_pending |
| 14 | pc-exit-lt | _port_common.py | exit at or AFTER the named bar | KILLED | 36; test_an_exit_is_not_sent_while_an_order_is_pending, test_cp1_a_refused_exit_is_resent_on_the_next_bar |
| 15 | pc-exit-pending | _port_common.py | no exit while an order is pending | KILLED | 1; test_an_exit_is_not_sent_while_an_order_is_pending |
| 16 | pc-flat-pending | _port_common.py | flat means no pending order | KILLED | 3; test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending, test_cp2_no_entry_while_an_order_is_pending |
| 17 | pc-ticks-trunc | _port_common.py | integer ticks by round() | KILLED | 1; test_prices_become_integer_vendor_ticks |
| 18 | cp2-buffer-3 | cp2.py | buffer 4 ticks (20.00) | KILLED | 5; test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06, test_cp2_the_0830_bar_is_a_range_bar |
| 19 | cp2-buffer-5 | cp2.py | buffer 4 ticks (20.00) | KILLED | 29; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 20 | cp2-c2exit | cp2.py | no C-2 exit (E.3-L-07) | KILLED | 2; test_cp2_f_binds_from_a_1353_fill, test_cp2_the_last_eligible_bar_1459_is_held_to_f |
| 21 | cp2-direction | cp2.py | break direction | KILLED | 25; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 22 | cp2-elig-c | cp2.py | no entry from C on | KILLED | 1; test_cp2_no_entry_from_1500 |
| 23 | cp2-elig-start | cp2.py | the 08:45 bar is eligible | KILLED | 19; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 24 | cp2-ge | cp2.py | close >= OR_high + buffer | KILLED | 26; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 25 | cp2-hold-74 | cp2.py | 75-bar count | KILLED | 24; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 26 | cp2-hold-76 | cp2.py | 75-bar count | KILLED | 24; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 27 | cp2-hold-count-start | cp2.py | count starts after the fill (present bars with a position) | KILLED | 2; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_an_fomc_1300_fill_is_moved_by_the_engine |
| 28 | cp2-le | cp2.py | close <= OR_low - buffer | KILLED | 5; test_cp2_breakout_down_sells, test_cp2_state_resets_each_trade_date |
| 29 | cp2-once | cp2.py | one entry per trade date | KILLED | 3; test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry, test_cp2_one_entry_per_trade_date_after_the_exit |
| 30 | cp2-otherdate | cp2.py | bars of another CT date never read | KILLED | 2; test_cp2_after_a_booked_forward_monday_reads_only_the_tuesday, test_cp2_monday_from_2026_06_01_reads_no_weekend_bar |
| 31 | cp2-range-15 | cp2.py | range [O, O+15) | KILLED | 23; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 32 | cp2-range-end | cp2.py | the 08:45 bar is not a range bar | KILLED | 22; test_cp2_a_deferred_entry_fill_starts_the_count_at_the_fill, test_cp2_a_deferred_exit_is_not_sent_twice |
| 33 | cp2-range-start | cp2.py | the 08:30 bar is a range bar | KILLED | 1; test_cp2_the_0830_bar_is_a_range_bar |
| 34 | cp2-window-f | cp2.py | trading window to F 15:08 | KILLED | 1; test_trading_windows_are_the_s0_12_intervals |
| 35 | cp3-buy-079 | cp3.py | CLV >= 0.8 buys | KILLED | 1; test_cp3_literals_are_the_clv_cuts_and_the_clock |
| 36 | cp3-buy-081 | cp3.py | CLV >= 0.8 buys | KILLED | 23; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 37 | cp3-close-1 | cp3.py | C_d = close of 14:59 | KILLED | 27; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 38 | cp3-direction | cp3.py | direction by CLV | KILLED | 25; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 39 | cp3-entry-bar | cp3.py | entry on the 08:30 bar | KILLED | 25; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| 40 | cp3-exit-2 | cp3.py | exit bar C-2 (14:58) | KILLED | 24; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| 41 | cp3-ge | cp3.py | non-strict buy cut | KILLED | 22; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 42 | cp3-halt-complete | cp3.py | a halt day's bar is incomplete | KILLED | 2; test_cp3_early_halt_day_is_not_traded_and_is_incomplete, test_cp3_the_halt_flag_resets_each_trade_date |
| 43 | cp3-halt-entry | cp3.py | an early-halt day d is not traded | KILLED | 3; test_cp3_a_halt_day_with_a_buy_prior_is_still_not_traded, test_cp3_early_halt_day_is_not_traded_and_is_incomplete |
| 44 | cp3-idguard | cp3.py | instrument guard d-1 vs the 08:30 bar | KILLED | 1; test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar |
| 45 | cp3-incomplete-used | cp3.py | incomplete days are dropped, never used as d-1 | KILLED | 4; test_cp3_a_day_with_two_instrument_ids_is_incomplete, test_cp3_early_halt_day_is_not_traded_and_is_incomplete |
| 46 | cp3-le | cp3.py | non-strict sell cut | KILLED | 10; test_cp3_a_day_with_two_instrument_ids_is_incomplete, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 47 | cp3-needs-close | cp3.py | the 14:59 bar must exist for a complete day | KILLED | 3; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_d_minus_1_is_the_most_recent_complete_day |
| 48 | cp3-needs-open | cp3.py | the 08:30 bar must exist for a complete day | KILLED | 1; test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete |
| 49 | cp3-oneid | cp3.py | one instrument_id per daily bar | KILLED | 1; test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| 50 | cp3-otherdate | cp3.py | bars of another CT date never read | KILLED | 3; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 51 | cp3-range0 | cp3.py | Range > 0 | KILLED | 2; test_cp3_clv_cuts_are_compared_exactly[0-0-None], test_cp3_zero_range_is_no_trade |
| 52 | cp3-sell-019 | cp3.py | CLV <= 0.2 sells | KILLED | 11; test_cp3_a_day_with_two_instrument_ids_is_incomplete, test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday |
| 53 | cp3-sell-021 | cp3.py | CLV <= 0.2 sells | KILLED | 1; test_cp3_literals_are_the_clv_cuts_and_the_clock |
| 54 | cp3-window | cp3.py | daily bar over [O, C) | KILLED | 26; test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar, test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| 55 | exp-dates | expiry.py | C4 exclusions (full sessions, vendor-degraded) | KILLED | 4; test_expiry_a_vendor_degraded_mbtx_date_is_not_traded, test_expiry_no_trade_off_the_event_set[day1] |
| 56 | exp-delay | expiry.py | entry intent one bar before the fill | KILLED | 8; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 57 | exp-direction | expiry.py | long only | KILLED | 6; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 58 | exp-entry-300 | expiry.py | entry bar T_exp - 301 | KILLED | 8; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 59 | exp-exact-bar | expiry.py | entry on the exact T_exp - 301 bar only | KILLED | 7; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 60 | exp-exit-1 | expiry.py | exit bar T_exp - 2 | KILLED | 6; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 61 | exp-exit-early | expiry.py | no exit before the exit bar | KILLED | 5; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 62 | exp-window | expiry.py | trading window (05:00, 11:00) | KILLED | 1; test_trading_windows_are_the_s0_12_intervals |
| 63 | rev-block-119 | rev2h.py | 120-minute blocks | KILLED | 17; test_trading_windows_are_the_s0_12_intervals, test_a_missing_10_30_bar_means_no_entry_and_no_b2_signal |
| 64 | rev-dates | rev2h.py | C4 exclusions (full sessions, vendor-degraded) | KILLED | 3; test_no_trade_off_the_entry_dates[d0], test_no_trade_off_the_entry_dates[d1] |
| 65 | rev-direction | rev2h.py | against sign(r) | KILLED | 14; test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter, test_a_missing_12_30_bar_flattens_but_does_not_enter |
| 66 | rev-final-1 | rev2h.py | final exit on 14:29 | KILLED | 7; test_an_engine_closed_position_leaves_the_12_30_decision_as_written, test_an_entry_bar_with_another_instrument_is_no_entry |
| 67 | rev-one-decision | rev2h.py | decisions at 10:30 and 12:30 | KILLED | 11; test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter, test_a_missing_12_30_bar_flattens_but_does_not_enter |
| 68 | rev-sigend-1 | rev2h.py | r closes on the t-1 bar | KILLED | 12; test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter, test_a_missing_12_30_bar_flattens_but_does_not_enter |
| 69 | rev-start | rev2h.py | r opens on the block's first bar | KILLED | 6; test_a_missing_10_30_bar_means_no_entry_and_no_b2_signal, test_a_missing_b1_endpoint_is_target_zero[510] |
| 70 | rev-window | rev2h.py | trading window to 14:31 | KILLED | 1; test_trading_windows_are_the_s0_12_intervals |
| 71 | mon-dates | montrend.py | C4 exclusions (full sessions, vendor-degraded) | KILLED | 2; test_no_trade_off_the_monday_entry_dates[d0], test_no_trade_off_the_monday_entry_dates[d1] |
| 72 | mon-direction | montrend.py | with s_t | KILLED | 14; test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent, test_a_missing_13_59_bar_exits_on_the_first_later_bar |
| 73 | mon-final-1 | montrend.py | final exit on the 13:59 bar | KILLED | 3; test_at_most_20_entries_one_per_decision, test_monday_morning_decisions_and_the_final_exit_on_13_59 |
| 74 | mon-first-1700 | montrend.py | no decision at Sunday 17:00 | KILLED | 4; test_trading_windows_are_the_s0_12_intervals, test_at_most_20_entries_one_per_decision |
| 75 | mon-first-1900 | montrend.py | first decision Sunday 18:00 | KILLED | 12; test_trading_windows_are_the_s0_12_intervals, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 76 | mon-flat-1401 | montrend.py | flat at 14:00 | KILLED | 4; test_trading_windows_are_the_s0_12_intervals, test_at_most_20_entries_one_per_decision |
| 77 | mon-last-1200 | montrend.py | 20 decisions | KILLED | 4; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_at_most_20_entries_one_per_decision |
| 78 | mon-last-1400 | montrend.py | last decision Monday 13:00 | KILLED | 3; test_at_most_20_entries_one_per_decision, test_no_decision_after_13_00 |
| 79 | mon-lookback-59 | montrend.py | t - 60 open | KILLED | 11; test_trading_windows_are_the_s0_12_intervals, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 80 | mon-sigend-1 | montrend.py | t - 1 close | KILLED | 14; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 81 | mon-step-30 | montrend.py | hourly decisions | KILLED | 12; test_a_missing_t_bar_means_no_entry_but_the_flatten_stands, test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry |
| 82 | mon-weekday | montrend.py | Mondays only | KILLED | 15; test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent, test_a_missing_13_59_bar_exits_on_the_first_later_bar |
| 83 | mon-window | montrend.py | trading window from Sunday 17:00 | KILLED | 1; test_trading_windows_are_the_s0_12_intervals |
| 84 | ec-close-pending | _event_common.py | no flatten while an order is pending | KILLED | 3; test_expiry_no_entry_while_pending_and_the_exit_waits_while_pending, test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent |
| 85 | ec-close-side | _event_common.py | the flatten closes the position | KILLED | 30; test_expiry_10_00_enters_at_04_59_for_05_00_and_exits_at_09_58_for_09_59, test_expiry_11_00_enters_at_05_59_for_06_00_and_exits_at_10_58_for_10_59 |
| 86 | ec-end-close | _event_common.py | the signal uses the end bar's CLOSE | SURVIVED | none |
| 87 | ec-entry-dates | _event_common.py | ENTRY_DATES excludes VENDOR_DEGRADED | KILLED | 3; test_entry_dates_are_full_sessions_less_vendor_degraded, test_no_trade_off_the_monday_entry_dates[d0] |
| 88 | ec-entry-exact | _event_common.py | entry on the exact t bar only | KILLED | 16; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 89 | ec-entry-flat | _event_common.py | entry only when flat (no pending) | KILLED | 2; test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent, test_no_flatten_and_no_entry_while_an_order_is_pending |
| 90 | ec-entry-id | _event_common.py | the entry bar carries the signal bars' id | KILLED | 2; test_an_entry_bar_with_another_instrument_is_no_entry, test_an_entry_bar_with_another_instrument_is_no_entry |
| 91 | ec-entry-zero | _event_common.py | target 0: no entry | KILLED | 22; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 92 | ec-final-ge | _event_common.py | final exit at or after the named bar | KILLED | 8; test_at_most_20_entries_one_per_decision, test_monday_morning_decisions_and_the_final_exit_on_13_59 |
| 93 | ec-flatten-zero | _event_common.py | s_t = 0 flattens | KILLED | 13; test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry, test_a_missing_t_minus_60_bar_is_signal_zero |
| 94 | ec-hold | _event_common.py | hold on an equal target (flatten only on a sign change) | KILLED | 10; test_a_flatten_is_not_sent_while_an_order_is_pending_and_is_resent, test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry |
| 95 | ec-idguard | _event_common.py | signal endpoints with two ids: target 0 | KILLED | 3; test_signal_bars_with_two_instruments_are_signal_zero, test_an_instrument_change_between_the_b1_endpoints_is_target_zero |
| 96 | ec-missed | _event_common.py | a missing t-1 bar gives target 0 (K7-L-08) | KILLED | 2; test_a_missing_t_minus_1_bar_flattens_on_the_first_later_bar_without_entry, test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter |
| 97 | ec-missing-start | _event_common.py | a missing start bar gives target 0 | KILLED | 4; test_a_missing_t_bar_means_no_entry_but_the_flatten_stands, test_a_missing_t_minus_60_bar_is_signal_zero |
| 98 | ec-q | _event_common.py | size q_c | KILLED | 26; test_a_missing_13_59_bar_exits_on_the_first_later_bar, test_a_missing_t_bar_means_no_entry_but_the_flatten_stands |
| 99 | ec-start-open | _event_common.py | the signal uses the start bar's OPEN | KILLED | 13; test_a_missing_12_29_bar_flattens_on_the_first_later_bar_and_does_not_enter, test_a_missing_12_30_bar_flattens_but_does_not_enter |
| 100 | ec-ticks-trunc | _event_common.py | integer ticks by round() | KILLED | 1; test_size_is_the_frozen_q_c_and_prices_are_integer_ticks |
| 101 | cal-degraded-drop | _calendar.py | VENDOR_DEGRADED row | KILLED | 2; test_entry_dates_are_full_sessions_less_vendor_degraded, test_vendor_degraded_is_the_build_bars_mapping_of_both_condition_files |
| 102 | cal-full-drop | _calendar.py | CRYPTO_FULL_SESSIONS row | KILLED | 15; test_crypto_full_sessions_are_ec_cal_dates_without_halt_and_with_the_regular_f, test_entry_dates_are_full_sessions_less_vendor_degraded |
| 103 | cal-mbtx-add | _calendar.py | R-1b-1: CME's 2025-12-26 not added | KILLED | 3; test_expiry_no_trade_off_the_event_set[day4], test_mbtx_is_the_c9_rule_less_the_two_r_1b_1_drops |
| 104 | cal-mbtx-drop | _calendar.py | an MBTX row | KILLED | 2; test_mbtx_is_the_c9_rule_less_the_two_r_1b_1_drops, test_the_expiry_event_set_and_its_clocks |
| 105 | cal-mbtx-texp | _calendar.py | T_exp 11:00 on 2026-03-27 | KILLED | 1; test_mbtx_is_the_c9_rule_less_the_two_r_1b_1_drops |

Totals: 105 mutants; KILLED 104, SURVIVED 1, PATTERN-MISS 0
