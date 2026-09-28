# Auditor mutant sweep (K1), 2026-09-28 02:24-02:40 PDT

Mutants 113: killed 106, survived 6, pattern-skipped 1. Mirror restored: True. Repository K1 files unchanged: True.

| Id | File | Change | Result | Failed | First killing test |
|---|---|---|---|---|---|
| PC-1 | _port_common.py | exit one minute late (14:59 instead of 14:58) | killed | 81 | tests/test_k1_members_ports.py::test_an_exit_is_not_sent_while_an_order_is_pending[MNQ] |
| PC-2 | _port_common.py | exit side flipped | killed | 87 | tests/test_k1_members_ports.py::test_an_exit_is_not_sent_while_an_order_is_pending[MNQ] |
| PC-3 | _port_common.py | ticks by truncation | killed | 3 | tests/test_k1_members_ports.py::test_prices_become_integer_vendor_ticks[MNQ] |
| PC-4 | _port_common.py | is_flat ignores pending | killed | 9 | tests/test_k1_members_ports.py::test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[MNQ] |
| PC-5 | _port_common.py | exit sent while an order is pending | killed | 3 | tests/test_k1_members_ports.py::test_an_exit_is_not_sent_while_an_order_is_pending[MNQ] |
| PC-6 | _port_common.py | exit bar not tied to CT date d | killed | 3 | tests/test_k1_members_ports.py::test_an_exit_is_not_sent_while_an_order_is_pending[MNQ] |
| C1-1 | cp1.py | signal bar 08:58 | killed | 52 | tests/test_k1_members_ports.py::test_trading_windows_are_the_s0_12_intervals[MNQ] |
| C1-2 | cp1.py | entry bar 14:30 | killed | 52 | tests/test_k1_members_ports.py::test_trading_windows_are_the_s0_12_intervals[MNQ] |
| C1-3 | cp1.py | exit bar 14:59 | killed | 31 | tests/test_k1_members_ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[MNQ] |
| C1-4 | cp1.py | first bar 17:01 | killed | 17 | tests/test_k1_members_ports.py::test_trading_windows_are_the_s0_12_intervals[MNQ] |
| C1-5 | cp1.py | signal sign flipped | killed | 38 | tests/test_k1_members_ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[MNQ] |
| C1-6 | cp1.py | zero signal buys | killed | 6 | tests/test_k1_members_ports.py::test_cp1_zero_signal_is_no_trade[MNQ] |
| C1-7 | cp1.py | signal-bar instrument guard removed | killed | 3 | tests/test_k1_members_ports.py::test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06[MNQ] |
| C1-8 | cp1.py | direction flipped | killed | 38 | tests/test_k1_members_ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[MNQ] |
| C1-9 | cp1.py | first bar = the last evening bar | killed | 10 | tests/test_k1_members_ports.py::test_cp1_missing_first_bar_is_no_trade_l05[MNQ] |
| C1-10 | cp1.py | entry decision repeatable | killed | 3 | tests/test_k1_members_ports.py::test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[MNQ] |
| C1-11 | cp1.py | size literal 1 (not q_c) | killed | 8 | tests/test_k1_members_ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[M2K] |
| C1-12 | cp1.py | signal uses the 08:59 open | killed | 40 | tests/test_k1_members_ports.py::test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459[MNQ] |
| C1-13 | cp1.py | entry while not flat | killed | 3 | tests/test_k1_members_ports.py::test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[MNQ] |
| C2-1 | cp2.py | range [08:30, 08:44) | killed | 4 | tests/test_k1_members_ports_cp2.py::test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[MNQ] |
| C2-2 | cp2.py | buffer 3 ticks | killed | 14 | tests/test_k1_members_ports_cp2.py::test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[MNQ] |
| C2-3 | cp2.py | hold 74 bars | killed | 57 | tests/test_k1_members_ports_cp2.py::test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[MNQ] |
| C2-4 | cp2.py | buy compare strict | killed | 62 | tests/test_k1_members_ports_cp2.py::test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MNQ] |
| C2-5 | cp2.py | sell compare strict | killed | 16 | tests/test_k1_members_ports_cp2.py::test_cp2_breakout_down_sells[MNQ] |
| C2-6 | cp2.py | up-break sells | killed | 59 | tests/test_k1_members_ports_cp2.py::test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MNQ] |
| C2-7 | cp2.py | entry allowed on the 15:00 bar | killed | 3 | tests/test_k1_members_ports_cp2.py::test_cp2_no_entry_from_1500[MNQ] |
| C2-8 | cp2.py | exit on the 76th bar | killed | 54 | tests/test_k1_members_ports_cp2.py::test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MNQ] |
| C2-9 | cp2.py | re-entry allowed | killed | 60 | tests/test_k1_members_ports_cp2.py::test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[MNQ] |
| C2-10 | cp2.py | range high from closes | killed | 11 | tests/test_k1_members_ports_cp2.py::test_cp2_the_buffer_is_exactly_four_ticks_either_side[MNQ] |
| C2-11 | cp2.py | 08:30 bar not a range bar | killed | 1 | tests/test_k1_members_ports_cp2.py::test_cp2_the_0830_bar_is_a_range_bar |
| C2-12 | cp2.py | hold exit sent while pending | killed | 4 | tests/test_k1_members_ports_cp2.py::test_cp2_a_deferred_exit_is_not_sent_twice |
| C2-13 | cp2.py | evening bars enter the range | killed | 1 | tests/test_k1_members_ports_cp2.py::test_cp2_range_and_eligible_bars_are_bars_of_ct_date_d |
| C3-1 | cp3.py | buy cut 0.81 | killed | 43 | tests/test_k1_members_ports_cp3.py::test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-2 | cp3.py | sell cut 0.19 | killed | 19 | tests/test_k1_members_ports_cp3.py::test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-3 | cp3.py | C_d = 14:58 close | killed | 56 | tests/test_k1_members_ports_cp3.py::test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-4 | cp3.py | exit bar 14:59 | killed | 48 | tests/test_k1_members_ports_cp3.py::test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-5 | cp3.py | buy compare strict | killed | 42 | tests/test_k1_members_ports_cp3.py::test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459[MNQ] |
| C3-6 | cp3.py | sell compare strict | killed | 18 | tests/test_k1_members_ports_cp3.py::test_cp3_prior_clv_at_02_sells[MNQ] |
| C3-7 | cp3.py | high CLV sells | killed | 49 | tests/test_k1_members_ports_cp3.py::test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459[MNQ] |
| C3-8 | cp3.py | zero range allowed | killed | 4 | tests/test_k1_members_ports_cp3.py::test_cp3_clv_cuts_are_compared_exactly[0-0-None] |
| C3-9 | cp3.py | halt day d traded | killed | 9 | tests/test_k1_members_ports_cp3.py::test_cp3_early_halt_day_is_not_traded_and_is_incomplete[MNQ] |
| C3-10 | cp3.py | instrument guard removed | killed | 3 | tests/test_k1_members_ports_cp3.py::test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar[MNQ] |
| C3-11 | cp3.py | halt day complete | killed | 4 | tests/test_k1_members_ports_cp3.py::test_cp3_early_halt_day_is_not_traded_and_is_incomplete[MNQ] |
| C3-12 | cp3.py | two-id day complete | killed | 1 | tests/test_k1_members_ports_cp3.py::test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| C3-13 | cp3.py | entry on any bar from 08:30 | killed | 1 | tests/test_k1_members_ports_cp3.py::test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete |
| C3-14 | cp3.py | daily low from closes | killed | 2 | tests/test_k1_members_ports_cp3.py::test_cp3_the_daily_low_is_the_min_low[6-buy] |
| C3-15 | cp3.py | evening bars enter the daily bar | killed | 2 | tests/test_k1_members_ports_cp3.py::test_cp3_the_tuesday_after_memorial_day_is_not_a_halt_day |
| EC-1 | _event_common.py | one-minute gaps allowed | killed | 4 | tests/test_k1_members_vxnband.py::test_a_missing_scan_bar_before_the_first_breach_ends_the_search |
| EC-2 | _event_common.py | close_items side flipped | killed | 35 | tests/test_k1_members_vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |
| EC-3 | _event_common.py | close_items while pending | killed | 2 | tests/test_k1_members_vxnband.py::test_no_exit_while_an_order_is_pending_and_a_refused_exit_is_resent |
| EC-4 | _event_common.py | d-2 instead of d-1 | killed | 26 | tests/test_k1_members_vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |
| EC-5 | _event_common.py | every date a full session | killed | 2 | tests/test_k1_members_vxnband.py::test_a_not_full_session_date_is_not_traded |
| EC-6 | _event_common.py | sign flipped | killed | 27 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| EC-7 | _event_common.py | is_flat ignores pending | killed | 1 | tests/test_k1_members_vxnband.py::test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day |
| VB-1 | vxnband.py | divisor 1500 | killed | 13 | tests/test_k1_members_vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] |
| VB-2 | vxnband.py | low cut 21 | killed | 2 | tests/test_k1_members_vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False] |
| VB-3 | vxnband.py | high cut 29 | killed | 2 | tests/test_k1_members_vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[29.990000-False] |
| VB-4 | vxnband.py | scan to 14:30 | killed | 1 | tests/test_k1_members_vxnband.py::test_the_scan_ends_before_1429[869-False] |
| VB-5 | vxnband.py | hold 31 | killed | 21 | tests/test_k1_members_vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |
| VB-6 | vxnband.py | C_prev = 14:58 close | killed | 3 | tests/test_k1_members_vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[complete] |
| VB-7 | vxnband.py | low cut non-strict | killed | 2 | tests/test_k1_members_vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False] |
| VB-8 | vxnband.py | high cut strict | killed | 2 | tests/test_k1_members_vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[30.000000-True] |
| VB-9 | vxnband.py | upper breach non-strict | killed | 3 | tests/test_k1_members_vxnband.py::test_the_band_is_exact_a_close_on_u_or_l_does_not_trade[1999-None] |
| VB-10 | vxnband.py | lower breach non-strict | killed | 3 | tests/test_k1_members_vxnband.py::test_the_band_is_exact_a_close_on_u_or_l_does_not_trade[-1999-None] |
| VB-11 | vxnband.py | fade direction flipped | killed | 32 | tests/test_k1_members_vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |
| VB-12 | vxnband.py | V of d itself (leak) | killed | 28 | tests/test_k1_members_vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |
| VB-13 | vxnband.py | instrument guard removed | killed | 1 | tests/test_k1_members_vxnband.py::test_the_c_prev_instrument_guard_against_the_0830_bar |
| VB-14 | vxnband.py | second entries allowed | killed | 9 | tests/test_k1_members_vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] |
| VB-15 | vxnband.py | exit one minute late | killed | 21 | tests/test_k1_members_vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |
| VB-16 | vxnband.py | non-full sessions traded | killed | 1 | tests/test_k1_members_vxnband.py::test_a_not_full_session_date_is_not_traded |
| VB-17 | vxnband.py | V read on a later bar when 08:30 fails | SURVIVED | 0 |  |
| VB-18 | vxnband.py | halt day complete for C_prev | killed | 1 | tests/test_k1_members_vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] |
| VB-19 | vxnband.py | 15:00 bar in the id set | killed | 1 | tests/test_k1_members_vxnband.py::test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[other_id_at_1500] |
| VB-20 | vxnband.py | gap check removed | killed | 1 | tests/test_k1_members_vxnband.py::test_a_missing_scan_bar_before_the_first_breach_ends_the_search |
| VB-21 | vxnband.py | scan instrument change ignored | killed | 2 | tests/test_k1_members_vxnband.py::test_an_instrument_change_before_the_first_breach_ends_the_search[540] |
| VB-22 | vxnband.py | 08:30 bar not scanned | killed | 26 | tests/test_k1_members_vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |
| VB-23 | vxnband.py | exit at intent + 31 | killed | 21 | tests/test_k1_members_vxnband.py::test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell] |
| VB-24 | vxnband.py | entry while not flat | killed | 1 | tests/test_k1_members_vxnband.py::test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day |
| VB-25 | vxnband.py | size literal 2 | killed | 1 | tests/test_k1_members_vxnband.py::test_no_exit_while_an_order_is_pending_and_a_refused_exit_is_resent |
| VB-26 | vxnband.py | evening bars read | SURVIVED | 0 |  |
| VB-27 | vxnband.py | regime filter removed | killed | 2 | tests/test_k1_members_vxnband.py::test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False] |
| VW-1 | vwap.py | TP parts 2 | killed | 30 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-2 | vwap.py | rule to 14:58 | killed | 2 | tests/test_k1_members_vwap.py::test_no_entry_from_the_1457_bar[897-expected1] |
| VW-3 | vwap.py | final exit 14:59 | killed | 9 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-4 | vwap.py | cap 21 | killed | 3 | tests/test_k1_members_vwap.py::test_declaration_label_leg_and_trading_window |
| VW-5 | vwap.py | exit on the fill bar | killed | 5 | tests/test_k1_members_vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |
| VW-6 | vwap.py | exit from k+2 | killed | 5 | tests/test_k1_members_vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |
| VW-7 | vwap.py | sign flipped | killed | 27 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-8 | vwap.py | tie resets the sign | killed | 2 | tests/test_k1_members_vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |
| VW-9 | vwap.py | VWAP of closes | killed | 3 | tests/test_k1_members_vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |
| VW-10 | vwap.py | unweighted | killed | 30 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-11 | vwap.py | gap ignored | killed | 3 | tests/test_k1_members_vwap.py::test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit |
| VW-12 | vwap.py | id change ignored for entries | killed | 2 | tests/test_k1_members_vwap.py::test_an_instrument_change_sends_an_exit_and_ends_new_entries |
| VW-13 | vwap.py | hold one bar longer | killed | 5 | tests/test_k1_members_vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |
| VW-14 | vwap.py | reversal leg despite the cap | killed | 2 | tests/test_k1_members_vwap.py::test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |
| VW-15 | vwap.py | final exit 14:59 | killed | 9 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-16 | vwap.py | rule on the 14:57 bar | killed | 2 | tests/test_k1_members_vwap.py::test_no_entry_from_the_1457_bar[897-expected1] |
| VW-17 | vwap.py | entries never counted | killed | 2 | tests/test_k1_members_vwap.py::test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |
| VW-18 | vwap.py | VWAP from bars before 08:30 | killed | 22 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-19 | vwap.py | non-full sessions traded | killed | 1 | tests/test_k1_members_vwap.py::test_a_not_full_session_date_is_not_traded |
| VW-20 | vwap.py | entry direction flipped | killed | 25 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-21 | vwap.py | reverse on the same sign | killed | 18 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-22 | vwap.py | hold restarts every bar | killed | 8 | tests/test_k1_members_vwap.py::test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold |
| VW-23 | vwap.py | no instrument-change exit | killed | 1 | tests/test_k1_members_vwap.py::test_an_instrument_change_sends_an_exit_and_ends_new_entries |
| VW-24 | vwap.py | intents while pending | killed | 2 | tests/test_k1_members_vwap.py::test_no_intent_while_an_order_is_pending |
| VW-25 | vwap.py | reversal order entry-then-exit | SURVIVED | 0 |  |
| VW-26 | vwap.py | flat entry on s = 0 | killed | 28 | tests/test_k1_members_vwap.py::test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| VW-27 | vwap.py | sum(vol) = 0 acts (sign 0) | SURVIVED | 0 |  |
| VW-28 | vwap.py | evening bars read | SURVIVED | 0 |  |
| VW-29 | vwap.py | reference id from the first bar | SURVIVED | 0 |  |
| CAL-1 | _calendar.py | a full session removed from both tables | PATTERN x2 |  |  |
| VX-1 | _vxn.py | one CLOSE string changed | killed | 2 | tests/test_k1_members_tables.py::test_the_modules_are_exactly_the_generators_output |
| VX-2 | _vxn.py | a dropped row put back | killed | 4 | tests/test_k1_members_tables.py::test_the_modules_are_exactly_the_generators_output |
