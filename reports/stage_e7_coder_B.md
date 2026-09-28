# Stage E.7 Task 2, coder B (MemberCoder-B-OpusXHigh): K1-vxnband-01, K1-vwap-01 and the K1 tables

Written by MemberCoder-B (opus, xhigh), 2026-09-28 01:00-01:40 PDT (America/Vancouver). Brief:
reports/stage_e7_briefs/2B_member_coder_B.md. Spec: reports/stage_e7_member_specs.md sections 0,
4, 5, 8 and section 9 (lead rulings of 01:12 PDT, received as a follow-up and applied). No bar file
was opened, no bar loader called, no web access, nothing committed, no harness file touched.

## 1. Files

| File | sha256 (first 16) | What |
|---|---|---|
| reports/stage_e7_briefs/gen_k1_tables.py | d18000a17d071959 | generator of the two table modules (run once; asserts every source fact before writing) |
| strategy/members/k1/_calendar.py | 1f9488bd3eb8c5e7 | EQUITY_TRADE_DATES (1846), EQUITY_FULL_SESSIONS (1779), SOURCE_SHA256 (generated) |
| strategy/members/k1/_vxn.py | 1d585e4fdffc530e | VXN_CLOSE (1794 rows), DROPPED_VXN (3 rows with reasons), VXN_SOURCE_SHA256 (generated) |
| strategy/members/k1/_event_common.py | 07ca23a843751021 | shared helpers of the two members (leg facts, clock, ticks, ClockRun, close_items, FULL_SESSIONS, PREVIOUS_TRADE_DATE) |
| strategy/members/k1/vxnband.py | 685b5018c139e846 | K1-vxnband-01, class VxnBand, factory make_mnq |
| strategy/members/k1/vwap.py | daffd93131b34b52 | K1-vwap-01, class SessionVwap, factory make_mnq |
| tests/test_k1_members_tables.py | 3e00e5dba8d2f4d5 | table pins (10 tests) |
| tests/test_k1_members_vxnband.py | b580828bff2f12af | vxnband pins and the synthetic kit (58 tests) |
| tests/test_k1_members_vwap.py | 2854fa36d7697b05 | vwap pins (31 tests) |

Not written: strategy/members/k1/__init__.py (stays 0 bytes; a test asserts it), cp1.py, cp2.py,
cp3.py, _port_common.py (coder A). The final sha256 values are those after the last edit; the
freeze is the lead's.

## 2. Table sources and sha256

_calendar.py (spec S0.8, S0.11, K1-L-02, K1-L-10):
- EC-CAL equity through data.group_session.load_group_calendar("equity"): data/calendars/__init__.py
  a13255d8f91a806a..., data/calendars/equity.py 3315e81225400add..., data/cme_calendar.py
  61218c13635ca735...; the engine's F from rules/sessions.py beb9501d6235299c... (flatten_time_ct
  for MNQ, M2K and MYM, asserted equal on every date).
- EQUITY_TRADE_DATES: every is_trade_date of 2019-05-01..2026-06-19, 1846 dates.
- EQUITY_FULL_SESSIONS: no early_halt_ct AND F = 15:08 CT, 1779 dates.
- Dates where the early-halt test and the F test disagree: none (the module's comment says so; a
  test pins it). In the research window both remove exactly the spec header's 13 dates
  (2025-05-26 ... 2026-06-19); the non-trade weekdays are exactly 2025-04-18, 2025-12-25, 2026-01-01.

_vxn.py (spec S0.11, section 9):
- data/vendor/index_history/vxn/VXN_History.csv, sha256
  f1b00135c4922ea756cd22cfeaa1d483700a6aed580f8da562f61574b5e1cdcc (asserted by the generator and
  the test), header DATE,OPEN,HIGH,LOW,CLOSE, DATE as MM/DD/YYYY.
- 1797 rows dated 2019-04-30..2026-06-19 (last row 2026-06-18), less DROPPED_VXN = 2021-04-02
  (R-1b-3), 2021-12-24 (R-1b-3), 2024-02-01 (R-1b-2): 1794 rows.
- Storage: the CLOSE field is stored as the file's exact string (for example "17.330000"); the
  member converts it once to Decimal. Every comparison is exact: the regime by Decimal, the band in
  integers (V's exact integer ratio, prices in vendor ticks).
- The research dates without V equal R-1b-5's list (2025-05-27, 06-20, 07-07, 09-02, 11-28,
  2026-01-20, 02-17, 04-06, 05-26); 2021-04-05 and 2024-02-02 also have no V. 52 trade dates of
  2019-05-02..2026-06-19 have no V in all.
- The test also checks the rulings' stated facts against the file: the 2021-04-02 and 2021-12-24
  rows repeat the prior row's close on all four fields; 2024-02-01's CLOSE is 17.330000.

## 3. The members as coded

K1-vxnband-01 (VxnBand). Day d is traded only if in EQUITY_FULL_SESSIONS. C_prev is kept by Family H
exactly as CP3 (08:30 and 14:59 bars of CT date d present, no bar of CT date d with
early_halt_ct, one instrument_id over [08:30, 15:00)), finalised when a bar of a later trade date
arrives. On d's 08:30 bar: instrument guard, then V = VXN of PREVIOUS_TRADE_DATE[d] (the first and
only read of V that day), then the regime. The scan runs over present bars of [08:30, 14:29) by
clock (ClockRun: a minute without a bar, including a missing 08:30 bar, ends the search; so does an
instrument_id other than the 08:30 bar's). The first breach closes the search even if the engine
refuses it. The exit goes on the first present bar of CT date d at or after intent bar + 30 min,
only while the position is non-zero and nothing is pending (resent while refused).

K1-vwap-01 (SessionVwap). Active only on EQUITY_FULL_SESSIONS dates, bars of CT date d from 08:30.
Sums in vendor ticks: sum(vol) and sum((H + L + C) x vol); s_t = sign(3 C sum(vol) - sum(...)),
a tie keeps the sign; sum(vol) = 0 takes no action. Per bar: record the position (a new position
first seen at bar k starts the hold), update gap / instrument flags and the sums; with a position,
an instrument change or a bar at or after 14:58 sends the exit (close_items: not while pending);
from 14:57 nothing else; otherwise, with nothing pending: flat entry, or reversal (exit, then an
entry leg if fewer than 20 entry intents and no gap or id change), or exit to flat. The entry count
increments when an entry intent is sent (refused ones count).

## 4. What the tests pin

Commands: `uv run pytest -q tests/test_k1_members_tables.py tests/test_k1_members_vxnband.py
tests/test_k1_members_vwap.py tests/test_stage_e_template.py tests/test_stage_e_freeze.py`
(PYTHONPYCACHEPREFIX unset). Engine tests use screening.stage_e_engine.run_engine with the real
StageERules (NO_RELEASES, or the frozen release calendar via load_release_calendar for the CPI and
event-minute tests). Each engine test on vwap has a flat prior date, because the engine refuses
opens without a prior-settlement proxy (engine_price_limit_reference_unavailable).

Result: 146 passed (99 in the three K1 coder-B files, 47 in test_stage_e_template.py and
test_stage_e_freeze.py), 4.8 s, at 01:36 PDT. ruff clean on every file written. The freeze static check
(check_member_source, cluster K1) returns no refusal for _calendar.py, _vxn.py, _event_common.py,
vxnband.py and vwap.py (pinned by test_member_files_pass_the_freeze_static_check).

Tables (tests/test_k1_members_tables.py; recomputed by independent code, the generator loaded only
for the byte-equality check):

| Pin | Test |
|---|---|
| source sha256 of the calendar modules and rules/sessions.py; range, roots, 15:08 | test_calendar_sources_carry_the_pinned_sha256 |
| each module is exactly the generator's output | test_the_modules_are_exactly_the_generators_output |
| EQUITY_TRADE_DATES = is_trade_date over 2019-05-01..2026-06-19 (1846); research non-trade weekdays | test_equity_trade_dates_are_every_ec_cal_trade_date_of_the_range |
| EQUITY_FULL_SESSIONS (1779); one F for MNQ, M2K, MYM; no disagreement; research removals = spec header's 13 | test_full_sessions_have_no_early_halt_and_the_regular_f_on_all_three_roots |
| PREVIOUS_TRADE_DATE (Memorial Day, Good Friday, Monday cases) | test_previous_trade_date_is_the_table_entry_immediately_before |
| VXN file sha256 = section 9's | test_the_vxn_file_is_section_9s |
| VXN_CLOSE = 1797 rows less 3 drops = 1794, exact strings, member mapping equal | test_vxn_close_is_every_row_of_the_range_less_the_three_drops |
| DROPPED_VXN dates, reasons, and the rulings' stated row facts | test_the_dropped_rows_and_their_reasons |
| R-1b-5 research no-V dates; 2021-04-05 and 2024-02-02 no V | test_research_trade_dates_without_v_are_r_1b_5s |
| strategy/members/k1/__init__.py is 0 bytes | test_the_cluster_init_is_empty |

K1-vxnband-01 (tests/test_k1_members_vxnband.py; synthetic MNQ at 40000.00 = 160000 ticks):

| Brief item | Test(s) |
|---|---|
| declaration, q_c from the frozen table, window (08:30, 15:00) | test_declaration_label_leg_size_and_trading_window |
| sell above, buy below; exit on intent bar + 30 | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar |
| C_prev = most recent complete date; halt, missing 14:59, missing 08:30, two ids skipped; an other id at 15:00 does not | test_c_prev_is_the_1459_close_of_the_most_recent_complete_date (6 cases) |
| C_prev is the 14:59 bar (not 14:58 or 15:00) | test_c_prev_reads_the_1459_bar_not_the_1458_or_1500_bar |
| warm-up | test_warm_up_without_a_complete_earlier_date_does_not_trade |
| C_prev's guard against d's 08:30 bar | test_the_c_prev_instrument_guard_against_the_0830_bar |
| missing 08:30 bar | test_a_missing_0830_bar_means_no_trade |
| V of d-1's calendar date, never d's own | test_v_is_the_close_of_trade_date_d_minus_1_never_ds_own (3 cases), test_a_mondays_v_is_fridays_close_not_sundays |
| missing V, 2025-05-27 (real table), with a positive control | test_missing_v_the_tuesday_after_memorial_day_2025_does_not_trade |
| V read at the 08:30 bar only (a recording table; breaches from 17:00 on d-1 send nothing) | test_v_is_read_at_the_0830_bar_and_never_before |
| a breach on the 08:30 bar trades | test_a_breach_on_the_0830_bar_itself_trades |
| band exact, V = 19.99 (w = 1999 ticks): on U or L no trade, one tick beyond trades | test_the_band_is_exact_a_close_on_u_or_l_does_not_trade (4), test_breach_side_in_integers (13, incl. a non-integer band) |
| regime: 19.99 and 30.00 trade, 20.00 and 29.99 do not | test_the_regime_cuts_v_below_20_or_at_least_30 (4), test_in_regime_exactly |
| first breach uses the day (later other-side breach ignored; none after the exit) | test_the_first_breach_uses_the_day_a_later_breach_is_ignored |
| a refused first breach still uses the day; no entry while an order is pending (the breach still uses the day) | test_a_refused_first_breach_still_uses_the_day, test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day |
| scan end: 14:28 trades (exit 14:58, fill 14:59), 14:29 does not | test_the_scan_ends_before_1429 (2) |
| missing scan bar / id change before the first breach | test_a_missing_scan_bar_before_the_first_breach_ends_the_search, test_an_instrument_change_before_the_first_breach_ends_the_search (2) |
| a missing bar after the first breach does not matter | test_a_missing_bar_after_the_first_breach_does_not_matter |
| exit bar missing: first later bar | test_a_missing_exit_bar_sends_the_exit_on_the_first_later_bar |
| no exit while pending; a refused exit is resent (direct calls) | test_no_exit_while_an_order_is_pending_and_a_refused_exit_is_resent |
| engine closure ends the day | test_an_engine_closure_ends_the_day |
| not-full-session d (2025-07-03) not traded | test_a_not_full_session_date_is_not_traded |
| CPI 2025-05-13: bars 07:25-07:35 send nothing (frozen release calendar) | test_the_cpi_window_bars_send_nothing |
| FOMC 2025-05-07 12:59 intent, fill 13:02, exit intent 13:29; ISM 2025-05-05 09:00 intent, fill 09:02, exit intent 09:30 | test_event_minutes_fomc_1300_and_ism_0900 |
| static check of all five files | test_member_files_pass_the_freeze_static_check |

K1-vwap-01 (tests/test_k1_members_vwap.py):

| Brief item | Test(s) |
|---|---|
| declaration, window | test_declaration_label_leg_and_trading_window |
| 0 before the first sign; hold to the final exit | test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit |
| flat entry in s_t's direction | test_a_flat_entry_goes_in_s_ts_direction (2) |
| close exactly at VWAP keeps the sign (exact tie 3 x 1 x 30 = 90); no exit on fill bar k, exit on k+1 | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_the_sign_matches_exact_integer_vwap_arithmetic |
| volume weighting | test_volume_weights_the_vwap |
| sum(volume) = 0: no action | test_zero_volume_bars_take_no_action |
| VWAP from 08:30 only | test_vwap_starts_at_0830 |
| engine level: reversal pair accepted, both fill at the same next open (position 1 -> 0 -> -1) | test_the_reversal_pair_is_accepted_and_both_legs_fill_at_the_same_next_open |
| minimum hold | test_no_exit_on_the_fill_bar_k_an_exit_on_k_plus_1, test_the_hold_restarts_at_the_reversal_fill, test_a_flip_on_k_and_back_on_k_plus_1_does_not_reverse |
| no intent while pending (direct calls; and the ISM deferral in the engine) | test_no_intent_while_an_order_is_pending, test_no_final_exit_while_an_order_is_pending |
| 20-entry cap on intents incl. reversal legs; exit to flat after the 20th | test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |
| a refused entry counts | test_a_refused_entry_intent_counts_toward_the_cap |
| no entry from 14:57; no reversal on 14:57 | test_no_entry_from_the_1457_bar (2), test_no_reversal_on_the_1457_bar |
| final exit on 14:58, missing: 14:59 | test_no_sign_before_the_first_and_a_long_hold_to_the_final_exit, test_a_missing_1458_bar_sends_the_final_exit_on_the_1459_bar |
| missing bar: no new entry, an open position keeps its exits | test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit, test_a_gap_keeps_the_final_exit, test_a_gap_before_any_entry_means_no_trade (08:30 and 08:45) |
| instrument change: exit on that bar (resent), no new entry; the reference is the 08:30 bar's id | test_an_instrument_change_sends_an_exit_and_ends_new_entries (direct calls), test_an_instrument_change_while_flat_ends_new_entries |
| engine-closed position: the rule continues | test_after_an_engine_closure_the_rule_continues |
| not-full-session d not traded | test_a_not_full_session_date_is_not_traded |
| CPI window | test_the_cpi_window_bars_send_nothing |
| event minutes: ISM 08:59 buy fills 09:02, the flip waits for pending and hold, reverses 09:03; FOMC 13:00 reversal sent on 13:00, both legs fill 13:02 | test_event_minutes_ism_0900_and_fomc_1300 |

## 5. Mutants

Method (scratchpad/coderB_mutants.py; results scratchpad/coderB_mutants.jsonl, first pass kept as
coderB_mutants_pass1.jsonl): each mutant is one exact, unique text replacement in a copy of the
file inside a scratch mirror of the repository (scratchpad/coderB_mut_repo); the three K1 coder-B
test files run with a fresh bytecode prefix (PYTHONDONTWRITEBYTECODE, nice 10); the original bytes
are restored and every file's sha256 is checked equal after the sweep ("all restored"). No
repository file was mutated. Sweep 01:23-01:33 PDT, rerun of three 01:34, 84 mutants: 11 on
_event_common.py, 35 on vxnband.py, 35 on vwap.py (literals, times, comparisons, guards, sides),
3 on the generated tables.

Result: 82 killed, 2 survived (both equivalent). The first pass left EC-09, VB-34 (vxnband's "flat
and nothing pending" at the entry) and VW-35 (vwap's instrument reference taken from 08:31) alive;
three pins were added (test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day;
the 08:30-only id case in test_an_instrument_change_while_flat_ends_new_entries) and the three were
rerun: all killed. The table's killing tests are the first three failing test names (count of
failures in brackets).

| Mutant | File | Change | Result | Killing tests |
|---|---|---|---|---|
| EC-01 | _event_common.py | `expected = self.start if self._last is None else self._last + 1` -> `expected = self.start if self._last is None else self._last + 2` | killed (44) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold (+40) |
| EC-02 | _event_common.py | `expected = self.start if self._last is None` -> `expected = minute if self._last is None` | killed (1) | test_a_gap_before_any_entry_means_no_trade[510] |
| EC-03 | _event_common.py | `if minute != expected:` -> `if False:` | killed (4) | test_a_gap_before_any_entry_means_no_trade[510], test_a_gap_before_any_entry_means_no_trade[525], test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit (+1) |
| EC-04 | _event_common.py | `return (value > 0) - (value < 0)` -> `return (value >= 0) - (value < 0)` | killed (30) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flat_entry_goes_in_s_ts_direction[-40-sell], test_a_flat_entry_goes_in_s_ts_direction[40-buy] (+27) |
| EC-05 | _event_common.py | `return (value > 0) - (value < 0)` -> `return (value > 0) - (value <= 0)` | killed (29) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flat_entry_goes_in_s_ts_direction[-40-sell], test_a_flat_entry_goes_in_s_ts_direction[40-buy] (+26) |
| EC-06 | _event_common.py | `NS_PER_MINUTE = 60 * NS_PER_S` -> `NS_PER_MINUTE = 120 * NS_PER_S` | killed (5) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_event_minutes_ism_0900_and_fomc_1300, test_no_exit_on_the_fill_bar_k_an_exit_on_k_plus_1 (+2) |
| EC-07 | _event_common.py | `if position == 0 or account.pending.get(root, 0):` -> `if position == 0:` | killed (2) | test_no_exit_while_an_order_is_pending_and_a_refused_exit_is_resent, test_no_final_exit_while_an_order_is_pending |
| EC-08 | _event_common.py | `root, SELL if position > 0 else BUY, abs(position)),)` -> `root, BUY if position > 0 else SELL, abs(position)),)` | killed (35) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+30) |
| EC-09 | _event_common.py | `return account.position(root) == 0 and not account.pending.get(root, 0)` -> `return account.position(root) == 0` | killed (1) | test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day |
| EC-10 | _event_common.py | `return f"{member_id} {ROOT}"` -> `return f"{member_id}"` | killed (2) | test_declaration_label_leg_and_trading_window, test_declaration_label_leg_size_and_trading_window |
| EC-11 | _event_common.py | `PREVIOUS_TRADE_DATE: dict[date, date] = dict(zip(_TRADE_DATES[1:], _TRADE_DATES[:-1],` -> `PREVIOUS_TRADE_DATE: dict[date, date] = dict(zip(_TRADE_DATES[1:], _TRADE_DATES[1:],` | killed (29) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+26) |
| VB-01 | vxnband.py | `BAND_DIVISOR = 1600` -> `BAND_DIVISOR = 1601` | killed (8) | test_breach_side_in_integers[157000-160000-30.00-None], test_breach_side_in_integers[158001-160000-19.990000-None], test_breach_side_in_integers[158002-160001-19.99-None] (+5) |
| VB-02 | vxnband.py | `BAND_DIVISOR = 1600` -> `BAND_DIVISOR = 1599` | killed (8) | test_breach_side_in_integers[156999-160000-30.00-buy], test_breach_side_in_integers[158000-160000-19.990000-buy], test_breach_side_in_integers[158001-160001-19.99-buy] (+5) |
| VB-03 | vxnband.py | `VXN_LOW_CUT = Decimal(20)` -> `VXN_LOW_CUT = Decimal(19)` | killed (4) | test_in_regime_exactly, test_the_band_is_exact_a_close_on_u_or_l_does_not_trade[-2000-buy], test_the_band_is_exact_a_close_on_u_or_l_does_not_trade[2000-sell] (+1) |
| VB-04 | vxnband.py | `VXN_LOW_CUT = Decimal(20)` -> `VXN_LOW_CUT = Decimal(21)` | killed (2) | test_in_regime_exactly, test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False] |
| VB-05 | vxnband.py | `VXN_HIGH_CUT = Decimal(30)` -> `VXN_HIGH_CUT = Decimal(29)` | killed (2) | test_in_regime_exactly, test_the_regime_cuts_v_below_20_or_at_least_30[29.990000-False] |
| VB-06 | vxnband.py | `VXN_HIGH_CUT = Decimal(30)` -> `VXN_HIGH_CUT = Decimal(31)` | killed (2) | test_in_regime_exactly, test_the_regime_cuts_v_below_20_or_at_least_30[30.000000-True] |
| VB-07 | vxnband.py | `return v < VXN_LOW_CUT or` -> `return v <= VXN_LOW_CUT or` | killed (2) | test_in_regime_exactly, test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False] |
| VB-08 | vxnband.py | `or v >= VXN_HIGH_CUT` -> `or v > VXN_HIGH_CUT` | killed (2) | test_in_regime_exactly, test_the_regime_cuts_v_below_20_or_at_least_30[30.000000-True] |
| VB-09 | vxnband.py | `SCAN_END_CT = time(14, 29)` -> `SCAN_END_CT = time(14, 30)` | killed (1) | test_the_scan_ends_before_1429[869-False] |
| VB-10 | vxnband.py | `SCAN_END_CT = time(14, 29)` -> `SCAN_END_CT = time(14, 28)` | killed (1) | test_the_scan_ends_before_1429[868-True] |
| VB-11 | vxnband.py | `HOLD_MINUTES = 30` -> `HOLD_MINUTES = 29` | killed (23) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+20) |
| VB-12 | vxnband.py | `HOLD_MINUTES = 30` -> `HOLD_MINUTES = 31` | killed (21) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+18) |
| VB-13 | vxnband.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 2` | killed (3) | test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[complete], test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[other_id_at_1500], test_c_prev_reads_the_1459_bar_not_the_1458_or_1500_bar |
| VB-14 | vxnband.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 0` | killed (26) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+23) |
| VB-15 | vxnband.py | `if move > width:` -> `if move >= width:` | killed (3) | test_breach_side_in_integers[161999-160000-19.990000-None], test_breach_side_in_integers[163000-160000-30.00-None], test_the_band_is_exact_a_close_on_u_or_l_does_not_trade[1999-None] |
| VB-16 | vxnband.py | `if move < -width:` -> `if move <= -width:` | killed (3) | test_breach_side_in_integers[157000-160000-30.00-None], test_breach_side_in_integers[158001-160000-19.990000-None], test_the_band_is_exact_a_close_on_u_or_l_does_not_trade[-1999-None] |
| VB-17 | vxnband.py | `return SELL` -> `return BUY` | killed (32) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+29) |
| VB-18 | vxnband.py | `move = BAND_DIVISOR * m * (close_ticks - prev_ticks)` -> `move = BAND_DIVISOR * n * (close_ticks - prev_ticks)` | killed (10) | test_breach_side_in_integers[157000-160000-30.00-None], test_breach_side_in_integers[158001-160000-19.990000-None], test_breach_side_in_integers[158002-160001-19.99-None] (+7) |
| VB-19 | vxnband.py | `prior = PREVIOUS_TRADE_DATE.get(day)` -> `prior = day` | killed (28) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+25) |
| VB-20 | vxnband.py | `if prior is None or prior.instrument_id != bar.instrument_id:` -> `if prior is None:` | killed (1) | test_the_c_prev_instrument_guard_against_the_0830_bar |
| VB-21 | vxnband.py | `if v is None or not in_regime(v):` -> `if v is None:` | killed (2) | test_the_regime_cuts_v_below_20_or_at_least_30[20.000000-False], test_the_regime_cuts_v_below_20_or_at_least_30[29.990000-False] |
| VB-22 | vxnband.py | `self._close is None or self._halt` -> `self._close is None` | killed (1) | test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] |
| VB-23 | vxnband.py | `or len(self._ids) != 1):` -> `or len(self._ids) < 1):` | killed (1) | test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[two_ids] |
| VB-24 | vxnband.py | `if (self._day is None or not self._has_open_bar or self._close is None` -> `if (self._day is None or self._close is None` | killed (1) | test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[missing_0830] |
| VB-25 | vxnband.py | `if not self._o <= minute < self._c:` -> `if not self._o <= minute <= self._c:` | killed (1) | test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[other_id_at_1500] |
| VB-26 | vxnband.py | `if minute == self._o:` -> `if minute == self._o + 1:` | killed (1) | test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[missing_0830] |
| VB-27 | vxnband.py | `if setup is None or bar.instrument_id != setup.instrument_id:` -> `if setup is None:` | killed (2) | test_an_instrument_change_before_the_first_breach_ends_the_search[540], test_an_instrument_change_before_the_first_breach_ends_the_search[545] |
| VB-28 | vxnband.py | `if side is not None:` -> `if False:` | killed (8) | test_a_refused_first_breach_still_uses_the_day, test_an_engine_closure_ends_the_day, test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] (+5) |
| VB-29 | vxnband.py | `if self._exit_at is None or minute < self._exit_at:` -> `if self._exit_at is None or minute <= self._exit_at:` | killed (21) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+18) |
| VB-30 | vxnband.py | `self._searching = is_full_session(day)` -> `self._searching = True` | killed (1) | test_a_not_full_session_date_is_not_traded |
| VB-31 | vxnband.py | `if self._run is None or not self._run.see(minute):` -> `if self._run is None or not (self._run.see(minute) or True):` | killed (1) | test_a_missing_scan_bar_before_the_first_breach_ends_the_search |
| VB-32 | vxnband.py | `if minute == self._o:` -> `if minute == self._o + 1:` | killed (26) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+23) |
| VB-33 | vxnband.py | `self._prior = finished` -> `pass` | killed (26) | test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[-2000-buy], test_a_breach_fades_and_exits_on_the_bar_30_minutes_after_the_intent_bar[2000-sell], test_a_breach_on_the_0830_bar_itself_trades (+23) |
| VB-34 | vxnband.py | `if side is None or not is_flat(account, self.root):` -> `if side is None:` | killed (1) | test_no_entry_while_an_order_is_pending_and_the_breach_still_uses_the_day |
| VB-35 | vxnband.py | `if bar.early_halt_ct is not None:` -> `if False:` | killed (1) | test_c_prev_is_the_1459_close_of_the_most_recent_complete_date[early_halt] |
| VW-01 | vwap.py | `TP_PARTS = 3` -> `TP_PARTS = 2` | killed (30) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flat_entry_goes_in_s_ts_direction[-40-sell], test_a_flat_entry_goes_in_s_ts_direction[40-buy] (+27) |
| VW-02 | vwap.py | `RULE_END_CT = time(14, 57)` -> `RULE_END_CT = time(14, 58)` | killed (2) | test_no_entry_from_the_1457_bar[897-expected1], test_no_reversal_on_the_1457_bar |
| VW-03 | vwap.py | `RULE_END_CT = time(14, 57)` -> `RULE_END_CT = time(14, 56)` | killed (1) | test_no_entry_from_the_1457_bar[896-expected0] |
| VW-04 | vwap.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 1` | killed (9) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flip_on_k_and_back_on_k_plus_1_does_not_reverse, test_a_gap_keeps_the_final_exit (+6) |
| VW-05 | vwap.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 3` | killed (11) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flip_on_k_and_back_on_k_plus_1_does_not_reverse, test_a_gap_keeps_the_final_exit (+8) |
| VW-06 | vwap.py | `MAX_ENTRIES = 20` -> `MAX_ENTRIES = 19` | killed (3) | test_a_refused_entry_intent_counts_toward_the_cap, test_declaration_label_leg_and_trading_window, test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |
| VW-07 | vwap.py | `MAX_ENTRIES = 20` -> `MAX_ENTRIES = 21` | killed (3) | test_a_refused_entry_intent_counts_toward_the_cap, test_declaration_label_leg_and_trading_window, test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |
| VW-08 | vwap.py | `MIN_HOLD_MINUTES = 1` -> `MIN_HOLD_MINUTES = 0` | killed (5) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flip_on_k_and_back_on_k_plus_1_does_not_reverse, test_event_minutes_ism_0900_and_fomc_1300 (+2) |
| VW-09 | vwap.py | `MIN_HOLD_MINUTES = 1` -> `MIN_HOLD_MINUTES = 2` | killed (5) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_event_minutes_ism_0900_and_fomc_1300, test_no_exit_on_the_fill_bar_k_an_exit_on_k_plus_1 (+2) |
| VW-10 | vwap.py | `if side != 0:` -> `if True:` | killed (2) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_the_sign_matches_exact_integer_vwap_arithmetic |
| VW-11 | vwap.py | `self._entries += 1` -> `self._entries += 0` | killed (2) | test_a_refused_entry_intent_counts_toward_the_cap, test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |
| VW-12 | vwap.py | `can_enter = self._entries < MAX_ENTRIES` -> `can_enter = self._entries <= MAX_ENTRIES` | killed (2) | test_a_refused_entry_intent_counts_toward_the_cap, test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |
| VW-13 | vwap.py | `and not self._gap and not self._id_changed` -> `and not self._id_changed` | killed (3) | test_a_gap_before_any_entry_means_no_trade[510], test_a_gap_before_any_entry_means_no_trade[525], test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit |
| VW-14 | vwap.py | `and not self._gap and not self._id_changed` -> `and not self._gap` | killed (2) | test_an_instrument_change_sends_an_exit_and_ends_new_entries, test_an_instrument_change_while_flat_ends_new_entries |
| VW-15 | vwap.py | `if s == 0 or not can_enter:` -> `if not can_enter:` | killed (28) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flat_entry_goes_in_s_ts_direction[-40-sell], test_a_flat_entry_goes_in_s_ts_direction[40-buy] (+25) |
| VW-16 | vwap.py | `if s == 0 or sign(position) == s:` -> `if sign(position) == s:` | killed (1) | test_no_intent_while_an_order_is_pending |
| VW-17 | vwap.py | `or bar.ts_event_ns < self._held_from_ns + MIN_HOLD_MINUTES` -> `or bar.ts_event_ns <= self._held_from_ns + MIN_HOLD_MINUTES` | killed (5) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_event_minutes_ism_0900_and_fomc_1300, test_no_exit_on_the_fill_bar_k_an_exit_on_k_plus_1 (+2) |
| VW-18 | vwap.py | `if account.pending.get(self.root, 0):` -> `if False:` | killed (2) | test_event_minutes_ism_0900_and_fomc_1300, test_no_intent_while_an_order_is_pending |
| VW-19 | vwap.py | `self._id_changed = True` -> `pass` | killed (2) | test_an_instrument_change_sends_an_exit_and_ends_new_entries, test_an_instrument_change_while_flat_ends_new_entries |
| VW-20 | vwap.py | `self._gap = True` -> `pass` | killed (3) | test_a_gap_before_any_entry_means_no_trade[510], test_a_gap_before_any_entry_means_no_trade[525], test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit |
| VW-21 | vwap.py | `(self._id_changed or minute >= self._final_exit)` -> `(self._id_changed or minute > self._final_exit)` | killed (9) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flip_on_k_and_back_on_k_plus_1_does_not_reverse, test_a_gap_keeps_the_final_exit (+6) |
| VW-22 | vwap.py | `if minute >= self._rule_end or` -> `if minute > self._rule_end or` | killed (2) | test_no_entry_from_the_1457_bar[897-expected1], test_no_reversal_on_the_1457_bar |
| VW-23 | vwap.py | `if minute < self._o:` removed | killed (22) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flat_entry_goes_in_s_ts_direction[-40-sell], test_a_flat_entry_goes_in_s_ts_direction[40-buy] (+19) |
| VW-24 | vwap.py | `if position != self._seen_position:` -> `if position and not self._seen_position or not position:` | killed (1) | test_the_hold_restarts_at_the_reversal_fill |
| VW-25 | vwap.py | `self._active = day, is_full_session(day)` -> `self._active = day, True` | killed (1) | test_a_not_full_session_date_is_not_traded |
| VW-26 | vwap.py | `exit_item = leg_market_intent(view, self.root, SELL if position > 0 else BUY` -> `exit_item = leg_market_intent(view, self.root, BUY if position > 0 else SELL` | killed (8) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit, test_event_minutes_ism_0900_and_fomc_1300 (+5) |
| VW-27 | vwap.py | `BUY if direction > 0 else SELL, self._leg.q)` -> `SELL if direction > 0 else BUY, self._leg.q)` | killed (25) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flat_entry_goes_in_s_ts_direction[-40-sell], test_a_flat_entry_goes_in_s_ts_direction[40-buy] (+22) |
| VW-28 | vwap.py | `hlc = to_ticks(bar.high, tick) + to_ticks(bar.low, tick) + close` -> `hlc = to_ticks(bar.high, tick) + to_ticks(bar.high, tick) + close` | killed (3) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_the_sign_matches_exact_integer_vwap_arithmetic, test_zero_volume_bars_take_no_action |
| VW-29 | vwap.py | `self._sum_vol += bar.volume` -> `self._sum_vol += 1` | killed (30) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flat_entry_goes_in_s_ts_direction[-40-sell], test_a_flat_entry_goes_in_s_ts_direction[40-buy] (+27) |
| VW-30 | vwap.py | `self._sum_hlc_vol += hlc * bar.volume` -> `self._sum_hlc_vol += hlc` | killed (30) | test_a_close_exactly_at_vwap_keeps_the_previous_sign_and_the_minimum_hold, test_a_flat_entry_goes_in_s_ts_direction[-40-sell], test_a_flat_entry_goes_in_s_ts_direction[40-buy] (+27) |
| VW-31 | vwap.py | `if self._sum_vol == 0:` -> `if False:` | SURVIVED | equivalent, see below |
| VW-32 | vwap.py | `if minute >= self._rule_end or self._sum_vol == 0:` -> `if minute >= self._rule_end:` | SURVIVED | equivalent, see below |
| VW-33 | vwap.py | `if not can_enter:` -> `if False:` | killed (2) | test_a_gap_ends_new_entries_an_open_position_keeps_the_opposite_signal_exit, test_twenty_entry_intents_reversal_legs_included_then_an_exit_to_flat |
| VW-34 | vwap.py | `elif self._ref_id is not None and bar.instrument_id != self._ref_id:` -> `elif False:` | killed (2) | test_an_instrument_change_sends_an_exit_and_ends_new_entries, test_an_instrument_change_while_flat_ends_new_entries |
| VW-35 | vwap.py | `if minute == self._o:` -> `if minute == self._o + 1:` | killed (1) | test_an_instrument_change_while_flat_ends_new_entries |
| TB-01 | _vxn.py | `("2025-06-02", "19.430000")` -> `("2025-06-02", "19.430001")` | killed (2) | test_the_modules_are_exactly_the_generators_output, test_vxn_close_is_every_row_of_the_range_less_the_three_drops |
| TB-02 | _calendar.py | `REGULAR_F_CT = "15:08"` -> `REGULAR_F_CT = "15:07"` | killed (2) | test_calendar_sources_carry_the_pinned_sha256, test_the_modules_are_exactly_the_generators_output |
| TB-03 | _vxn.py | `("2021-04-02",` -> `("2021-04-05",` | killed (2) | test_the_dropped_rows_and_their_reasons, test_the_modules_are_exactly_the_generators_output |

Survivors (equivalent mutants, no test can kill them):
- VW-31 removes `if self._sum_vol == 0: return` in the sign update; VW-32 removes `or
  self._sum_vol == 0` before the rule. With sum(volume) = 0 the sign expression is 3 x C x 0 - 0 =
  0, a tie, so s is not updated either way; and the sums are cumulative from 08:30, so sum(volume)
  = 0 only happens before the day's first bar with volume, when s = 0 and the account is flat, where
  the rule does nothing anyway. Both checks are kept because the spec states the clause.

Not mutated (no literal, time or comparison of the rule): to_ticks' round (prices are on the tick
grid, the engine refuses others), the evening-bar return in vxnband (evening minutes are at or
after 17:00, outside every window, so removing it changes nothing but the halt flag, which is per
trade date).

## 6. Questions and notes for the lead

No question that changes a trade was left open; nothing was chosen where the spec was silent on a
trade-changing detail. Points for the record:

1. Table range vs EC-CAL coverage. The spec calls 2019-05-01..2026-06-19 "EC-CAL's coverage", but
   data/cme_calendar.py CALENDAR_COVERAGE is 2019-01-01..2026-12-31. The tables use the spec's range,
   as the brief says (the module comment records the difference). Effect: d = 2019-05-01 has no
   predecessor in EQUITY_TRADE_DATES, so no V, even though VXN_CLOSE holds 2019-04-30. MNQ bars
   start 2019-05-06 (C8), so no trade can change.
2. vwap: sum(volume) = 0 can only occur before the first bar with volume of the day, when s = 0
   and the account is flat (positions never cross F), so the clause "no action on that bar" is
   coded as stated but its two checks are equivalent mutants (VW-31, VW-32). The id-change and
   final exits are placed before it; with sum(volume) = 0 no position exists.
3. vwap: the instrument-change exit is sent without the minimum hold, as the entry states ("an
   open position gets an exit intent on that bar"); an early one is refused by D9.3b and resent.
   In a run the engine raises EngineInvariantError on an instrument change with exposure, so the
   case is covered by direct calls only.
4. vxnband: at the first breach the day's entry is used even when the account is not flat (then no
   intent is sent). It cannot arise in a run (one entry per day, positions flat by F); a
   direct-call test pins it.
5. Family H's early-halt test reads early_halt_ct on the bars of CT date d (K7 CP3's form, bars of
   the evening before are not read); the flag is per trade date, so the two forms agree. Coder A's
   CP3 should use the same form; I did not read or touch coder A's files.
6. Scratchpad incident (01:21 PDT): my Write of scratchpad/mutants.py replaced coder A's file of
   the same name (the scratchpad is shared). Its content is lost; I left a stub that exits with an
   explanation, moved mine to coderB_mutants.py, and messaged the lead at once. Coder A's running
   process (its log was still being written) was unaffected. No repository file was involved. The
   mutants then ran in a scratch mirror (scratchpad/coderB_mut_repo: symlinks to the repository,
   real copies of strategy/members/k1 and my three test files), so no repository file was ever
   mutated.

## 7. R-T3-1 fix (lead ruling, test-only; audit reports/stage_e7_member_audit.md Part 1 section 6, findings 1 and 4)

Done 02:47 PDT (machine clock). Test files only; no member module or table changed.

Kit: tests/test_k1_members_vxnband.py's Day gains `flatten_from` (a synthetic F: in_flatten_window
and in_no_new_positions_window set from that minute), as coder A's kit has it.

Tests added (4):
- vxnband, finding 1: test_evening_bars_after_an_early_halt_holiday_are_not_read. The real bars'
  shape (the auditor's probe): Friday 2025-05-23 complete; Memorial Day 2025-05-26 halts at 12:00;
  Tuesday 2025-05-27 opens at 17:00 CT on the holiday with evening bars labelled "12:00". Asserts
  Tuesday's normal round trip (sell 09:00, fill 09:01, exit 09:30, fill 09:31) and that Tuesday
  stays a complete C_prev: Wednesday 2025-05-28 (its own evening from Tuesday 17:00 included) buys
  its 10:00 close of +987, 1013 ticks below Tuesday's 14:59 close (w = 1012.5); with Friday's close
  it would sell at 08:30 instead.
- vwap, finding 1: test_evening_bars_do_not_enter_the_vwap_or_the_0830_clock_run. D1 opens at 17:00
  CT the evening before at +1000; the 09:00 step to +4 buys (fill 09:01) and exits 14:58 (fill
  14:59): the evening is in neither the VWAP nor the 08:30 clock run.
- vxnband, finding 4: test_a_position_open_at_a_synthetic_f_is_flattened_by_the_engine. F from
  09:10: the engine's forced_flatten fills at 09:11; the member sends no exit and no entry on the
  09:40 breach (its only intent is the 09:00 sell).
- vwap, finding 4: test_after_the_engines_flatten_at_a_synthetic_f_the_rule_continues. F from 10:00:
  forced_flatten fills at 10:01; the member sends no exit of its own and, flat with s = +1, sends
  the rule's flat entries on 10:01..10:19 (all refused, engine_flatten_window) until its 20 entry
  intents are used (K1-L-08, K1-L-09).

Mutants (same scratch mirror and runner, scratchpad/coderB_mutants.py, results in
coderB_mutants.jsonl):

| Mutant | Change | Result | Killing test |
|---|---|---|---|
| VB-36 (the auditor's VB-26) | vxnband.py:226-227 `if opened.date() != self._day: return ()` removed | killed (1 failure) | test_evening_bars_after_an_early_halt_holiday_are_not_read |
| VW-36 (the auditor's VW-28) | vwap.py:180 `if not self._active or opened.date() != self._day:` -> `if not self._active:` | killed (1 failure) | test_evening_bars_do_not_enter_the_vwap_or_the_0830_clock_run |

Both new tests pass on the code. Run: `uv run pytest -q tests/test_k1_members_tables.py
tests/test_k1_members_vxnband.py tests/test_k1_members_vwap.py tests/test_stage_e_template.py
tests/test_stage_e_freeze.py` (PYTHONPYCACHEPREFIX unset): 150 passed (103 K1 coder-B tests: 10
tables, 60 vxnband, 33 vwap; 47 template and freeze), 5.1 s. ruff clean.

Member modules, sha256 unchanged (every strategy/members/k1/*.py byte-identical to before the fix):
- _event_common.py 07ca23a8437510212c6320611ccafae390c252a2ecb0ae1a4498206c64ac22bd
- vxnband.py 685b5018c139e8463f7cc55b62966e70e75d68a0499c2c90a36b07898f2be151
- vwap.py daffd93131b34b5221c0d66372333344fae4c88843818c68db03a0aebcc93622
- _calendar.py 1f9488bd3eb8c5e7aec29bd62ef2c7efbf187f14bdfda1cf7d97c3635681719c
- _vxn.py 1d585e4fdffc530ec86871cda5e71b66d7fd33183249a485bbda24de005cc6b5

Test files after the fix: tests/test_k1_members_vxnband.py
7337fc5a292db9fd9b4d6e5ebd07cec8635630d14a7cba630e1a70d4af3fb3b7, tests/test_k1_members_vwap.py
d7ad21678bcedbac0b68aef0e91c9736b2be7bc889c4fab5c3b0ddc26d940caf (tests/test_k1_members_tables.py
unchanged).
