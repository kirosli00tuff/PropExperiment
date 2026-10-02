Totals: 146 mutants, 143 killed, 3 survived (AF41, AC04, AC05), 0 badly built (none); controls ['control_ok', 'control_ok', 'control_ok', 'control_ok', 'control_ok']; guarded files changed: none; wall time 11.5 min.

| Id | Module | Mutant | Result | Tests failing (count; first two) |
|---|---|---|---|---|
| AF01 | flight | block clock starts 08:31 | killed | 56; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF02 | flight | 4-minute blocks | killed | 56; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF03 | flight | 78 blocks | killed | 4; test_trading_windows_are_the_s0_12_intervals, test_decision_times_are_0835_to_1455_every_5_minutes |
| AF04 | flight | 76 blocks | killed | 4; test_trading_windows_are_the_s0_12_intervals, test_decision_times_are_0835_to_1455_every_5_minutes |
| AF05 | flight | end bar t_k - 2 | killed | 55; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF06 | flight | start bar t_k - 5 | killed | 55; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF07 | flight | start bar t_k - 7 | killed | 55; test_trading_windows_are_the_s0_12_intervals, test_the_entry_size_is_the_frozen_q_c |
| AF08 | flight | 19 reference dates | killed | 52; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF09 | flight | 21 reference dates | killed | 51; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF10 | flight | n >= 1,199 | killed | 2; test_threshold_m_and_the_value_floor, test_member_n_1199_is_no_trade_and_n_1200_trades |
| AF11 | flight | n >= 1,201 | killed | 3; test_threshold_m_and_the_value_floor, test_m_is_ceil_of_n_over_200[1200-6] |
| AF12 | flight | tail 1/199 | killed | 4; test_threshold_m_and_the_value_floor, test_m_is_ceil_of_n_over_200[1200-6] |
| AF13 | flight | m = floor(n/200) | killed | 11; test_r_equal_to_q_in_another_form_triggers, test_threshold_m_and_the_value_floor |
| AF14 | flight | (m+1)-th smallest | killed | 11; test_threshold_m_and_the_value_floor, test_threshold_counts_duplicates |
| AF15 | flight | H30 intent T_e + 30 | killed | 8; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF16 | flight | H30 intent T_e + 28 | killed | 11; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF17 | flight | exit bar 15:05 | killed | 6; test_trading_windows_are_the_s0_12_intervals, test_heod_exit_is_sent_on_the_bar_at_1504 |
| AF18 | flight | exit bar 15:03 | killed | 9; test_trading_windows_are_the_s0_12_intervals, test_heod_exit_is_sent_on_the_bar_at_1504 |
| AF19 | flight | float compare | killed | 1; test_compare_and_trigger_are_exact_beyond_float |
| AF20 | flight | c6 = 0 allowed | killed | 1; test_block_return_is_the_tick_ratio_and_needs_c6_positive |
| AF21 | flight | r over c1 | killed | 1; test_block_return_is_the_tick_ratio_and_needs_c6_positive |
| AF22 | flight | no r < 0 condition | killed | 2; test_trigger_needs_r_negative_even_at_or_below_q, test_a_positive_q_never_triggers_a_non_negative_r |
| AF23 | flight | r < Q strict | killed | 7; test_r_equal_to_q_in_another_form_triggers, test_member_n_1199_is_no_trade_and_n_1200_trades |
| AF24 | flight | ticks truncated | killed | 1; test_ticks_round_a_near_grid_float_to_the_nearest_tick |
| AF25 | flight | no MES instrument guard | killed | 2; test_an_mes_roll_inside_a_block_is_no_trigger_and_later_blocks_trigger, test_undefined_reference_computations_are_not_values |
| AF26 | flight | no MES CT-date check | killed | 1; test_a_bar_whose_trade_date_is_not_its_ct_date_is_not_a_block_bar |
| AF27 | flight | d need not be a FLIGHT date | killed | 1; test_a_non_full_date_is_skipped_as_a_reference_and_as_d |
| AF28 | flight | no warm-up | killed | 1; test_warm_up_the_20th_date_does_not_trade_and_the_21st_does |
| AF29 | flight | fewer than 20 refs accepted | killed | 1; test_fewer_than_20_reference_dates_at_the_tables_start_is_no_trade |
| AF30 | flight | C6 tests the entry-bar minute | killed | 5; test_values_of_d_itself_never_enter_q_of_d, test_c6_skips_the_1300_trigger_on_an_fomc_date_and_enters_at_1305 |
| AF31 | flight | no C6 | killed | 5; test_values_of_d_itself_never_enter_q_of_d, test_c6_skips_the_1300_trigger_on_an_fomc_date_and_enters_at_1305 |
| AF32 | flight | C6 skip uses the day's entry | killed | 5; test_values_of_d_itself_never_enter_q_of_d, test_c6_skips_the_1300_trigger_on_an_fomc_date_and_enters_at_1305 |
| AF33 | flight | missing entry bar does not end the day | killed | 2; test_a_missing_entry_bar_at_the_first_trigger_ends_the_day, test_an_entry_bar_of_another_trade_date_counts_as_missing |
| AF34 | flight | entry bar trade date unchecked | killed | 1; test_an_entry_bar_of_another_trade_date_counts_as_missing |
| AF35 | flight | entry while pending | killed | 1; test_no_entry_while_an_order_is_pending_on_mgc |
| AF36 | flight | sells | killed | 51; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF37 | flight | q_c + 1 | killed | 49; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF38 | flight | every trigger enters | killed | 7; test_only_the_first_trigger_of_d_enters_even_when_refused, test_a_second_trigger_while_long_and_after_the_exit_does_nothing |
| AF39 | flight | HEOD exits like H30 | killed | 5; test_heod_exit_is_sent_on_the_bar_at_1504, test_a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[HEOD-missing2-905] |
| AF40 | flight | H30 uncapped | killed | 3; test_h30_exit_is_capped_at_1504[74-904], test_h30_exit_is_capped_at_1504[77-904] |
| AF41 | flight | T_e one minute late | SURVIVED | 0;  |
| AF42 | flight | exit while pending | killed | 2; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_a_refused_exit_is_resent_and_a_pending_exit_is_not_duplicated |
| AF43 | flight | exit one bar late | killed | 14; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF44 | flight | exit side reversed | killed | 18; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF45 | flight | exit quantity + 1 | killed | 18; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
| AF46 | flight | T_e not reset when flat | killed | 1; test_t_e_resets_when_flat |
| AF47 | flight | only negative r recorded | killed | 54; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF48 | flight | prune the oldest reference | killed | 3; test_member_n_1199_is_no_trade_and_n_1200_trades, test_member_m_at_1201_and_1540 |
| AF49 | flight | a filed date keeps no values | killed | 54; test_the_entry_size_is_the_frozen_q_c, test_k1_reads_the_0829_and_0834_bars |
| AF50 | flight | signal leg declared first | killed | 1; test_declarations_names_legs_and_factories |
| AF51 | flight | label order | killed | 1; test_declarations_names_legs_and_factories |
| AF52 | flight | MGC window ends 15:05 | killed | 1; test_trading_windows_are_the_s0_12_intervals |
| AO01 | oilcad | first t 08:00 | killed | 3; test_trading_windows_are_s0_12, test_decision_clock_is_08_05_to_13_25_every_5_minutes |
| AO02 | oilcad | last t 13:30 | killed | 3; test_trading_windows_are_s0_12, test_decision_clock_is_08_05_to_13_25_every_5_minutes |
| AO03 | oilcad | last t 13:20 | killed | 4; test_trading_windows_are_s0_12, test_decision_clock_is_08_05_to_13_25_every_5_minutes |
| AO04 | oilcad | 10-minute step | killed | 32; test_decision_clock_is_08_05_to_13_25_every_5_minutes, test_first_and_last_decisions_trade |
| AO05 | oilcad | c1 bar t - 2 | killed | 32; test_trading_windows_are_s0_12, test_first_and_last_decisions_trade |
| AO06 | oilcad | c6 bar t - 5 | killed | 32; test_trading_windows_are_s0_12, test_first_and_last_decisions_trade |
| AO07 | oilcad | 19 reference dates | killed | 31; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AO08 | oilcad | n >= 999 | killed | 2; test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation, test_n_1000_trades_and_n_999_does_not |
| AO09 | oilcad | n >= 1001 | killed | 2; test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation, test_n_1000_trades_and_n_999_does_not |
| AO10 | oilcad | \|z\| >= 1.9999 | killed | 1; test_threshold_is_inclusive_at_exactly_2 |
| AO11 | oilcad | \|z\| >= 2.0001 | killed | 4; test_threshold_is_inclusive_at_exactly_2, test_z_exactly_2_trades_end_to_end |
| AO12 | oilcad | exit T_e + 13 | killed | 14; test_trading_windows_are_s0_12, test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending |
| AO13 | oilcad | exit T_e + 15 | killed | 12; test_trading_windows_are_s0_12, test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending |
| AO14 | oilcad | c6 = 0 allowed | killed | 2; test_block_return_requires_a_positive_denominator, test_a_zero_mcl_close_at_t_minus_6_leaves_r_t_undefined |
| AO15 | oilcad | r over c1 | killed | 4; test_block_return_requires_a_positive_denominator, test_z_exactly_2_trades_end_to_end |
| AO16 | oilcad | pstdev (ddof 0) | killed | 3; test_scale_is_the_sample_standard_deviation_ddof_1, test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation |
| AO17 | oilcad | n < MIN -> <= | killed | 2; test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation, test_n_1000_trades_and_n_999_does_not |
| AO18 | oilcad | s = 0 allowed | killed | 2; test_scale_refuses_fewer_than_1000_values_and_a_zero_deviation, test_zero_scale_is_no_trade_on_d |
| AO19 | oilcad | \|z\| > 2 strict | killed | 4; test_threshold_is_inclusive_at_exactly_2, test_z_exactly_2_trades_end_to_end |
| AO20 | oilcad | no abs (one side) | killed | 5; test_threshold_is_inclusive_at_exactly_2, test_z_exactly_2_trades_end_to_end |
| AO21 | oilcad | no MCL instrument guard | killed | 5; test_z_exactly_2_trades_end_to_end, test_n_1000_trades_and_n_999_does_not |
| AO22 | oilcad | no MCL CT-date check | killed | 1; test_an_mcl_bar_is_read_on_its_own_ct_date_only |
| AO23 | oilcad | t-6 store not reset per day | killed | 1; test_a_previous_dates_t_minus_6_bar_is_never_used |
| AO24 | oilcad | prune the oldest reference | killed | 29; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AO25 | oilcad | no warm-up | killed | 1; test_warm_up_20th_eligible_date_no_trade_21st_trades |
| AO26 | oilcad | fewer than 20 refs accepted | killed | 1; test_too_few_reference_dates_at_the_table_start_no_trade |
| AO27 | oilcad | T_e not reset when flat | killed | 14; test_no_entry_while_a_position_or_a_pending_order_exists[1-0], test_no_entry_while_a_position_or_a_pending_order_exists[-1-0] |
| AO28 | oilcad | T_e one minute late | killed | 10; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending, test_exit_of_a_short_buys_the_whole_position |
| AO29 | oilcad | entry while pending | killed | 2; test_no_entry_while_a_position_or_a_pending_order_exists[0-1], test_no_entry_while_a_position_or_a_pending_order_exists[0--1] |
| AO30 | oilcad | exit while pending | killed | 1; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending |
| AO31 | oilcad | exit one bar late | killed | 10; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending, test_exit_of_a_short_buys_the_whole_position |
| AO32 | oilcad | exit side reversed | killed | 12; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending, test_exit_of_a_short_buys_the_whole_position |
| AO33 | oilcad | exit quantity + 1 | killed | 11; test_exit_on_the_first_6c_bar_at_t_e_plus_14_resent_while_not_pending, test_exit_of_a_short_buys_the_whole_position |
| AO34 | oilcad | no 6C CT-date check | killed | 1; test_bars_are_identified_by_ct_date_not_trade_date_alone |
| AO35 | oilcad | d need not be an OILCAD date | killed | 1; test_a_date_outside_oilcad_dates_never_trades |
| AO36 | oilcad | C6 tests t - 1 | killed | 5; test_c6_skips_09_30_on_a_standard_wpsr_date_and_not_09_35, test_c6_skips_13_00_on_an_fomc_date |
| AO37 | oilcad | no C6 | killed | 5; test_c6_skips_09_30_on_a_standard_wpsr_date_and_not_09_35, test_c6_skips_13_00_on_an_fomc_date |
| AO38 | oilcad | entry side reversed | killed | 31; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AO39 | oilcad | q_c + 1 | killed | 26; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AO40 | oilcad | signal leg declared first | killed | 1; test_factory_name_legs_size_and_protocol |
| AO41 | oilcad | 6C window ends 13:40 | killed | 1; test_trading_windows_are_s0_12 |
| AO42 | oilcad | only positive r filed | killed | 31; test_first_and_last_decisions_trade, test_r_t_reads_the_mcl_bars_at_t_minus_1_and_t_minus_6 |
| AW01 | wkndbtc | Tuesday | killed | 18; test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW02 | wkndbtc | Friday d - 2 | killed | 18; test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW03 | wkndbtc | Sunday d - 2 | killed | 17; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW04 | wkndbtc | P_F 14:58 | killed | 21; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW05 | wkndbtc | P_F 15:00 | killed | 21; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW06 | wkndbtc | P_S 17:58 | killed | 24; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW07 | wkndbtc | P_S 18:00 | killed | 24; test_trading_windows_are_s0_12, test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f |
| AW08 | wkndbtc | exit bar 14:57 | killed | 7; test_trading_windows_are_s0_12, test_exit_at_monday_14_58_resent_while_not_pending |
| AW09 | wkndbtc | exit bar 14:59 | killed | 5; test_trading_windows_are_s0_12, test_exit_at_monday_14_58_resent_while_not_pending |
| AW10 | wkndbtc | weekday check removed | killed | 2; test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00, test_a_non_monday_never_trades |
| AW11 | wkndbtc | d full-session check removed | killed | 2; test_excluded_mondays_do_not_trade[monday0], test_is_trade_monday_needs_both_d_and_d_minus_3 |
| AW12 | wkndbtc | Friday full-session check removed | killed | 4; test_research_window_mondays_and_no_mnq_guard_at_sunday_18_00, test_excluded_mondays_do_not_trade[monday1] |
| AW13 | wkndbtc | G = 0 buys | killed | 2; test_g_zero_is_no_trade, test_side_of_is_the_sign_of_the_tick_difference |
| AW14 | wkndbtc | sides swapped | killed | 17; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW15 | wkndbtc | P_F CT-date check removed | killed | 3; test_both_regimes_read_the_same_two_bars[monday1], test_a_saturday_mnq_bar_booked_to_monday_is_not_the_entry_bar |
| AW16 | wkndbtc | entry CT-date check removed | killed | 1; test_a_saturday_mnq_bar_booked_to_monday_is_not_the_entry_bar |
| AW17 | wkndbtc | P_S trade_date check removed | killed | 1; test_mbt_sunday_bar_must_carry_trade_date_d |
| AW18 | wkndbtc | P_F date check removed (stale Friday) | killed | 1; test_p_f_comes_from_ct_date_d_minus_3_only_never_a_stale_friday |
| AW19 | wkndbtc | instrument guard removed | killed | 1; test_one_instrument_id_across_p_f_and_p_s |
| AW20 | wkndbtc | C6 tests 17:59 | killed | 2; test_c6_tests_the_mnq_sunday_18_00_fill, test_c6_skips_a_guarded_sunday_18_00_fill |
| AW21 | wkndbtc | no C6 | killed | 2; test_c6_tests_the_mnq_sunday_18_00_fill, test_c6_skips_a_guarded_sunday_18_00_fill |
| AW22 | wkndbtc | exit instant on the Sunday | killed | 6; test_exit_at_monday_14_58_resent_while_not_pending, test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar |
| AW23 | wkndbtc | exit while pending | killed | 3; test_exit_at_monday_14_58_resent_while_not_pending, test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar |
| AW24 | wkndbtc | exit one bar late | killed | 4; test_exit_at_monday_14_58_resent_while_not_pending, test_every_exit_closes_the_whole_position |
| AW25 | wkndbtc | exit side reversed | killed | 6; test_exit_at_monday_14_58_resent_while_not_pending, test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar |
| AW26 | wkndbtc | exit quantity + 1 | killed | 6; test_exit_at_monday_14_58_resent_while_not_pending, test_exit_of_a_short_buys_and_a_missing_exit_bar_goes_to_the_next_bar |
| AW27 | wkndbtc | entry while pending | killed | 2; test_no_entry_while_a_position_or_a_pending_order_exists[0-1], test_no_entry_while_a_position_or_a_pending_order_exists[0--1] |
| AW28 | wkndbtc | q_c + 1 | killed | 12; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW29 | wkndbtc | signal leg declared first | killed | 1; test_factory_name_legs_size_and_protocol |
| AW30 | wkndbtc | G sign flipped | killed | 16; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW31 | wkndbtc | MNQ Monday window ends 14:59 | killed | 1; test_trading_windows_are_s0_12 |
| AR01 | _releases | 1-minute guard | killed | 4; test_releases_source_is_the_frozen_calendar, test_in_guard_edges |
| AR02 | _releases | 3-minute guard | killed | 3; test_releases_source_is_the_frozen_calendar, test_in_guard_edges |
| AR03 | _releases | R itself not guarded | killed | 10; test_in_guard_edges, test_mgc_guards_on_the_flight_fill_grid_are_the_fomc_1300_dates |
| AR04 | _releases | R + 120 s guarded | killed | 2; test_in_guard_edges, test_c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[658-True] |
| AC01 | _calendar | previous_dates includes d | killed | 61; test_previous_dates_are_the_k_most_recent_strictly_before_d, test_k1_reads_the_0829_and_0834_bars |
| AC02 | _calendar | previous_dates k - 1 | killed | 107; test_previous_dates_are_the_k_most_recent_strictly_before_d, test_the_entry_size_is_the_frozen_q_c |
| AC03 | _calendar | FLIGHT_DATES a union | killed | 1; test_member_dates_are_the_sorted_intersections |
| AC04 | _calendar | OILCAD_DATES energy only | SURVIVED | 0;  |
| AC05 | _calendar | WKNDBTC_DATES equity only | SURVIVED | 0;  |
| AF53 | flight | missing entry bar checked BEFORE C6 ends the day | killed | 1; test_a_skipped_trigger_with_a_missing_entry_bar_does_not_end_the_day |
| AF54 | flight | C6 on the wrong root (6C) | killed | 4; test_values_of_d_itself_never_enter_q_of_d, test_c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[659-False] |
| AF55 | flight | a late MES bar (at t_k) used as the t_k - 1 bar | killed | 2; test_an_mes_bar_absent_at_tk_minus_1_and_present_at_tk_is_never_used, test_no_entry_from_a_view_after_1454 |
| AF56 | flight | t_k - 6 store not reset per MES day | killed | 2; test_k1_reads_the_0829_and_0834_bars, test_a_bar_at_0830_is_not_the_start_bar_of_k1 |
| AF57 | flight | any variant accepted | killed | 1; test_declarations_names_legs_and_factories |
| AF59 | flight | blocks shifted to 08:30..14:50 | killed | 4; test_trading_windows_are_the_s0_12_intervals, test_decision_times_are_0835_to_1455_every_5_minutes |
| AO43 | oilcad | a late MCL bar (at t) used as the t - 1 bar | killed | 1; test_mcl_bar_arriving_late_is_never_used |
| AO44 | oilcad | C6 on the wrong root (MGC) | killed | 3; test_c6_skips_09_30_on_a_standard_wpsr_date_and_not_09_35, test_c6_skips_11_00_on_holiday_week_wpsr_dates_including_the_e4_dropped_row |
| AW32 | wkndbtc | the 18:00 MNQ bar also accepted as the entry bar | killed | 16; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW33 | wkndbtc | the Friday 15:00 MBT bar also accepted as P_F | killed | 20; test_buy_on_the_sunday_17_59_view_when_p_s_above_p_f, test_sell_when_p_s_below_p_f |
| AW34 | wkndbtc | C6 on the wrong root (6C) | killed | 1; test_c6_tests_the_mnq_sunday_18_00_fill |
| AF41b | flight | exit clock computed from T_e + 1 min (the real T_e mutant; AF41 only moved a flag) | killed | 8; test_a_second_trigger_while_long_and_after_the_exit_does_nothing, test_h30_exit_is_sent_on_the_bar_at_te_plus_29 |
