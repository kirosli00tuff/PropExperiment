# Stage E.3 Task 2: MemberCoder-A-OpusXHigh report

Worker file worker-xhigh, model opus, effort xhigh. Brief: reports/stage_e3_briefs/coder_common.md and
coder_A.md. Spec: reports/stage_e3_member_specs.md sections 0, 1, 2, 3, 8 and 10. Written 2026-09-27 (PDT).

Members coded: K2-cp1-01, K2-cp2-01, K2-cp3-01, K2-monthend-01 (24 trials, ordinals 1-18 and 39-44).
Nothing is unfinished. No open question blocks a trade (the notes in section 5 are for the lead's
information).

## 1. Files and sha256

| File | sha256 |
|---|---|
| strategy/members/k2/cp1.py | b1b52eb3dd6c76d501a27286b19a28aec6a0bee392e931509b2a00a88b097002 |
| strategy/members/k2/cp2.py | 4957faafc0a9475d9f4136fc1339754f5502b1f8494ae22d9ba3c7602d7a76f4 |
| strategy/members/k2/cp3.py | 3985d957f593a959ec201fff64442a56db83be1635cb16d7aa99cd86a93386b3 |
| strategy/members/k2/monthend.py | ca801d5a85be2e6854d280fbd2506b6e89cdf2ec523baf27792c8f7cf855561d |
| strategy/members/k2/_month_end.py (generated) | b2eb207d1d30e185cc592727890daf2d60be3a60dee0771d882ca58b6fd7ab2a |
| strategy/members/k2/_port_common.py | 556b1012c8c6525f70e222f830cc2aa9189b9602e72292230a9192c0186e7211 |
| tests/test_e3_k2_members.py | c1b8e6a3dd99329da6df183e00fea1d3819084805e7628df6eccb8575a107bb3 |
| reports/stage_e3_briefs/gen_k2_month_end.py (one-off, not imported) | 4a79aa16338b1766e094d61c0ea378c9c846737ecbf4fb5d6d3046de4a5da8b1 |

All six member-directory files pass `screening.stage_e_freeze.check_member_source` (pinned by
`test_every_coder_a_file_passes_the_freeze_static_check`) and ruff. strategy/members/__init__.py and
strategy/members/k2/__init__.py were not touched. No file of MemberCoder-B was opened, edited or imported.

## 2. Findings the brief asked for

- **Is a one-leg member called on a minute where its leg has no bar?** No. `iter_minutes`
  (screening/stage_e_engine.py lines 239-263) builds the grid from the union of the legs' bar
  timestamps, so for one leg every call carries the bar. The members still return `()` on a None bar
  and change no state (pinned by `test_a_none_bar_is_no_decision_and_changes_no_state`, direct calls).
- **What EC-CAL counts as a trade date.** `GroupCalendar.is_trade_date` (data/group_session.py
  lines 146-148): a weekday that is not a FULL_CLOSURE holiday and not a booked-forward day. EARLY_HALT
  days ARE trade dates. The rates calendar: coverage 2019-05-01..2026-06-19, 63 EARLY_HALT and
  17 FULL_CLOSURE holidays, no booked-forward days, one late open (2025-11-28, 07:30 CT, also an early halt).
- **The month-end table.** 85 months, 2019-05..2026-05 (June 2026 has N = 2026-06-30, outside coverage;
  L-16). 170 dates. 9 of them are early-halt days, listed in the table and dropped by the member at
  run time: 2019-11-28, 2019-11-29, 2020-11-27 (N-1 of Nov 2020), 2021-05-31 (N of May 2021, Memorial
  Day), 2022-05-30 (N-1 of May 2022), 2024-11-28, 2024-11-29, 2025-11-27, 2025-11-28.
  `MONTH_END_SOURCE_SHA256` = sha256 of data/calendars/rates.py (449c1529...), which is in the E.2b
  harness freeze.

## 3. Spec field to code to test

Line numbers are the files' current lines. `_port_common.py` helpers: `leg_facts` 57-62, `shift` 70-72,
`ct_open` 75-77, `to_ticks` 80-82, `is_flat` 85-86, `exit_if_due` 89-101.
Test names are in tests/test_e3_k2_members.py (prefix `test_` omitted).

### K2-cp1-01 (spec section 1)

| Spec field | Code | Tests |
|---|---|---|
| Exposures, one leg, q_c, label, factories (S0.1-S0.3) | cp1.py 46, 77-83, 135-156; _port_common leg_facts, label | factories_name_the_label_and_trade_one_leg; the_24_declarations_freeze_and_verify_under_tmp_path; cp1_buys_... (six roots, qty 1) |
| First bar = 17:00 CT on the calendar day before d, trade_date d (L-05) | 47, 118-120; its open read at 54-57 (lead ruling idiom) | cp1_buys_... (MON: Sunday 17:00); cp1_missing_globex_open_bar_is_no_trade_l05 |
| Signal bar O+29 = 07:49, close; s in ticks | 48, 79, 123-125, 101-104 | cp1_buys_... and cp1_sells_... (paths make close-close and open-open give the opposite side) |
| Both signal bars present, one instrument_id (L-06) | 96-100 | cp1_missing_globex_open_bar...; cp1_missing_0749_signal_bar_is_no_trade; cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06 (entry bar id is not guarded) |
| Zero signal: no trade | 102-103 | cp1_zero_signal_is_no_trade |
| Entry on the bar at C-31 = 13:29 exactly; side by s; fill 13:30 (S0.6, L-04) | 49, 80, 126-132 | cp1_buys_... (intent 13:29, fill 13:30); cp1_missing_1329_entry_bar_is_no_trade_l04 |
| Exit on first present bar at or after C-2 = 13:58, resent while refused (S0.7, L-22) | 50, 81, 116-117; exit_if_due | cp1_buys_... (fill 13:59); cp1_missing_1358_bar_sends_the_exit_on_1359 (fill 14:00); cp1_a_refused_exit_is_resent_on_the_next_bar_l22 (engine_min_hold, then accepted); an_exit_is_not_sent_while_an_order_is_pending |
| Early halts not tested (port) | none (by design) | cp1_does_not_test_early_halts_the_engine_refuses_the_entry (2021-05-31: engine_flatten_window) |
| D9.5a fill guard (engine) | none | cp1_fill_in_the_d95a_guard_waits_two_minutes (release 13:30: fill 13:32) |
| Forced flatten at F (engine) | none | cp1_position_open_at_a_synthetic_f_is_flattened_by_the_engine |
| Per-trade-date reset; one trade a day | 91-92, 111-112, 128 | cp1_trades_once_per_trade_date_on_consecutive_days |
| trading_windows (S0.12) | 85-89 | trading_windows_are_the_s0_12_intervals |

### K2-cp2-01 (spec section 2)

| Spec field | Code | Tests |
|---|---|---|
| Exposures, leg, q_c, label, factories | cp2.py 47, 70-75, 124-145 | factories_...; freeze test; cp2_breakout_... (six roots) |
| OR = present bars in [O, O+15) of CT date d; no OR bar: no trade (L-08) | 48, 74, 102-108, 109-110 | cp2_without_an_opening_range_bar_there_is_no_trade_l08; cp2_the_range_is_taken_from_the_present_bars_l08; cp2_bars_before_o_and_on_the_previous_evening_are_not_range_bars |
| Buffer 4 vendor ticks, >= and <= (S0.10) | 49, 113-119 | cp2_the_buffer_is_exactly_four_ticks_either_side (3 ticks: no entry; 4: entry, both sides) |
| Eligible bars [O+15, C); no entry from 14:00 | 111-112 | cp2_no_entry_from_1400; cp2_entry_at_1359_is_flattened_by_the_engine_at_f |
| One entry per trade date, even if refused (L-08) | 109, 120 | cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it_l08 (one refused intent, no second) |
| Exit: 75 present bars with the position open, from after the decision bar; resent while refused (L-07, L-22) | 50, 81-90, 99-100 | cp2_breakout_fills_next_open_and_exits_after_75_present_bars (08:01 to 09:16); cp2_a_missing_bar_inside_the_hold_moves_the_exit_one_bar_l07 (09:17); cp2_a_deferred_entry_fill_starts_the_count_at_the_fill (08:03 to 09:18) |
| No C-2 exit (L-07) | (absent by design) | cp2_has_no_c_minus_2_exit (13:01 to 14:16) |
| Forced flatten at F if earlier | none (engine) | cp2_entry_at_1359_is_flattened_by_the_engine_at_f (forced_flatten 15:08) |
| No instrument guard, no early-halt test (port) | none (by design) | (no guard exists to test) |
| Per-trade-date reset | 78-79, 97-98 | cp2_state_resets_each_trade_date |
| trading_windows (S0.12) | 51, 76 | trading_windows_are_the_s0_12_intervals |

### K2-cp3-01 (spec section 3)

| Spec field | Code | Tests |
|---|---|---|
| Exposures, leg, q_c, label, factories | cp3.py 53, 110-117, 187-208 | factories_...; freeze test; cp3_prior_clv_at_08_buys_... (six roots) |
| Daily bar from bars of CT date d in [O, C): H, L, C_d = 13:59 close | 57, 114, 138-149, 172-175 | the `daily()` paths put extreme bars at 07:10 and 14:30 that would change the CLV if read: every cp3 engine test |
| Complete day: 07:20 and 13:59 bars, no early_halt_ct on CT date d, one instrument_id; finalised on a later trade date's bar | 120-128, 130-134, 139-140 | cp3_d_minus_1_is_the_most_recent_complete_day_l09; cp3_a_day_with_two_instrument_ids_is_incomplete; cp3_missing_0720_bar_is_no_trade_and_the_day_is_incomplete; cp3_early_halt_day_is_not_traded_and_is_incomplete; cp3_uses_d_minus_1_only_after_it_is_finalised |
| d-1 = most recent complete daily bar (L-09); warm-up no trade | 134, 156-157 | cp3_d_minus_1_is_the_most_recent_complete_day_l09; cp3_prior_clv_... (MON not traded) |
| Instrument guard, one bar (H6) | 158-159 | cp3_instrument_guard_compares_d_minus_1_with_the_0720_bar |
| Range > 0; CLV >= 0.8 buys, <= 0.2 sells, exact integer compare (L-19) | 54-55, 72-86 | cp3_clv_cuts_are_compared_exactly (13 cases incl. 4/5, 12/15, 1/5, 3/15); cp3_prior_clv_at_08_buys...; cp3_prior_clv_at_02_sells; cp3_clv_strictly_between_the_cuts_is_no_trade; cp3_zero_range_is_no_trade |
| Day d early halt read from the 07:20 bar (L-09, L-11) | 153-154 | cp3_early_halt_day_is_not_traded_and_is_incomplete (2021-05-31) |
| Entry on the 07:20 bar exactly; fill 07:21 | 178-184 | cp3_prior_clv_at_08_buys_... (intent 07:20, fill 07:21); cp3_missing_0720_bar... |
| Exit first bar at or after 13:58, resent while refused (L-10, L-22) | 58, 115, 176-177; exit_if_due | cp3_prior_clv_... (fill 13:59); cp3_missing_1358_bar_sends_the_exit_on_1359 (14:00) |
| D9.5a fill guard; forced flatten (engine) | none | cp3_fill_in_the_d95a_guard_waits_two_minutes (07:23); cp3_position_open_at_a_synthetic_f_is_flattened_by_the_engine |
| trading_windows (S0.12) | 117 | trading_windows_are_the_s0_12_intervals |

### K2-monthend-01 (spec section 8)

| Spec field | Code | Tests |
|---|---|---|
| Exposures, leg, q_c, label, factories | monthend.py 45, 65-70, 93-114 | factories_...; freeze test; monthend_buys_n_minus_1_and_n_... (six roots) |
| Event set N-1 and N from the literal table (S0.11, L-16) | 27, 48-50, 83; _month_end.py | monthend_buys_n_minus_1_and_n_... (06-26 and 07-01 not traded); the_month_end_test_rows_are_in_the_table; the_month_end_table_is_the_calendar_recomputed |
| BUY on the bar at O = 07:20 exactly, fill 07:21 | 46, 83-90 | monthend_buys_...; monthend_a_missing_0720_bar_is_no_trade_that_date |
| C4 early halt (entry bar), dropped not moved (L-11, L-16) | 85-86 | monthend_an_early_halt_n_is_dropped_and_n_minus_1_still_trades_l16 (2021-05-28 traded, 05-31 no intent, 06-01 no intent) |
| Instrument guard = entry bar only, cannot fail (L-12) | none needed (docstring) | monthend_guards_only_the_entry_bar_l12 |
| Exit on the 15:04 bar (fill 15:05); missing: first later bar; resent while refused | 47, 81-82; exit_if_due | monthend_buys_... (15:05); monthend_a_missing_1504_bar_sends_the_exit_on_the_next_bar (15:06) |
| D9.5a guard, F (engine) | none | monthend_fills_in_the_d95a_guard_wait_two_minutes (07:23; exit 15:07 before F); monthend_position_open_at_a_synthetic_f_is_flattened_by_the_engine |
| trading_windows (S0.12) | 70 | trading_windows_are_the_s0_12_intervals |
| Table pin (recomputed independently from EC-CAL, plus source sha) | _month_end.py | the_month_end_table_is_the_calendar_recomputed; early_halt_days_are_trade_dates_of_the_calendar |

Mutation check (scratch script, members patched in memory, not kept): a CP3 without its day-d halt
test, a month-end member without its halt test, CP1 on the "first present bar" reading, CP2 with a
5-tick buffer and CP2 with a 74-bar hold each make their pinned test fail.

## 4. Implementation choices (none can change a trade)

1. **The bar's open, per the lead's ruling (E.3 Task 2).** CP1 reads the Globex-open bar's open as
   `asdict(bar)["open"]` in `cp1._globex_open_ticks` (cp1.py 54-57), called only on that bar (line 119),
   with the ruled comment on the line above the read. My first version used the same asdict read
   through a shared helper `_port_common.bar_open` without the comment; after the ruling I moved it
   into cp1.py and deleted the shared helper, so the idiom appears once, next to its only use. The
   read sits in a module-level function because the ruled one-line comment is exactly 100 characters
   at 4-space indentation (the ruff limit), and would exceed it at the method body's 12. No other
   member of mine reads an open (CP3 does not read O_d; see choice 4).
2. Ticks: `round(Decimal(repr(price)) / vendor_tick)` (exact for on-grid prices). Highs and lows are
   kept as floats (max/min, no arithmetic) and converted to ticks only at the decision.
3. CP3's CLV cuts are Decimal("0.8") and Decimal("0.2"), compared as integer cross-products via
   `as_integer_ratio()` (4/5, 1/5), so no float can move a cut.
4. CP3 does not read O_d (the 07:20 open): no H6 condition uses it. The 07:20 bar's presence is
   required, as specified. `LOOKBACK = 1` is a documentary constant (d-1 is one stored bar).
5. CP3's day-d halt test reads the 07:20 bar only (spec); completeness reads every bar of CT date d
   (Family H). The two agree because bars carry early_halt_ct per CT date (data/group_session.py 583-589).
6. CP2's trading-window end 15:08 is a named literal (`F_REGULAR_CT`): members cannot import
   rules.sessions. Month-end's window end 15:06 is derived as the exit bar + 2 minutes (through the
   15:05 fill bar). CP1's windows are derived from O, C and the 17:00 literal.
7. Exits of CP1, CP3 and month-end share `exit_if_due`: any present bar of CT date d at or after the
   named exit bar, position non-zero, nothing pending on the leg. A pending order of any kind
   (including the engine's forced flatten) suppresses a new exit.
8. `_month_end.py` also carries `MONTH_END_SOURCE_SHA256`; the pin test checks it against
   data/calendars/rates.py, so any edit to that frozen file fails the test until the table is regenerated.
9. Tests build their own synthetic frames (evening segment 17:00-17:05 on d-1 plus day segment
   07:00-15:12 on d, flags from rules/sessions.py, optional synthetic F via in_flatten_window) rather
   than tests/_stage_e_synthetic.product_frame, whose random highs/lows would blur the CP3 and CP2 cases.
10. The freeze test copies only my six files into tmp_path and writes a K2 freeze there with the S0.2
    ordinals; it never touches reports/stage_e_k2_member_freeze.json.

## 5. Notes for the lead (not blocking)

- Choice 1 follows the lead's ruling on `open`; the audit may confirm the function wrapper (it
  exists only to keep the ruled comment within the line limit).
- CP1 on real data: on 2025-11-28 (late open 07:30 after the Globex outage, also an early halt) there
  is no 17:00 bar on 11-27 for that trade date, so no trade (L-05). The engine would refuse it anyway.

## 6. Test run

Command (no PYTHONPYCACHEPREFIX set):

    nice -n 10 uv run pytest -q tests/test_e3_k2_members.py tests/test_stage_e_freeze.py tests/test_stage_e_template.py

Last line, verbatim:

    145 passed in 1.85s

tests/test_e3_k2_members.py alone: 98 tests.
