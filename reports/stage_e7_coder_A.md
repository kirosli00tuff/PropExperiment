<!-- Saved by the Stage E.7 lead from MemberCoder-A-OpusXHigh's final message (the harness refused the subagent's .md write), 2026-09-28 02:08 PDT; text unchanged. -->

# Stage E.7 Task 2, coder A: the K1 core ports (K1-cp1-01, K1-cp2-01, K1-cp3-01 on MNQ, M2K, MYM)

MemberCoder-A-OpusXHigh (worker-xhigh on opus), 2026-09-28, 01:00 to 02:06 PDT.
- **Brief:** reports/stage_e7_briefs/2A_member_coder_A.md.
- **Governing text:** reports/stage_e7_member_specs.md: the header, section 0, sections 1-3 and section 8. I also checked D6 (docs/STAGE_E_DESIGN.md lines 364-391) and catalog C3/C4 (C lines 101-112).
- **Precedent adapted, never imported:** strategy/members/k7/{_port_common,cp1,cp2,cp3}.py and tests/test_k7_members_ports*.py (E.6). The one-module-several-factories pattern comes from strategy/members/k3.
- **What I did not do:** open a bar file or call a bar loader or runner; change any harness file; commit; spawn a worker; touch coder B's files.

## 1. Files

| File | What it is |
|---|---|
| strategy/members/k1/_port_common.py | Shared plumbing. `EXPOSURES = ("MNQ", "M2K", "MYM")`. `leg_facts` returns O 08:30 and C 15:00 from `day_session_ct`, q_c from `vehicles[root].q_c` (1, 3, 3) and the vendor tick from `rules.products` (0.25, 0.10, 1.00). Also `label`, `shift`, `ct_open`, `to_ticks` (round(price / tick) in Decimal), `is_flat`, and `exit_if_due` (S0.7: sent on a present bar of CT date d at or after the named bar, resent while refused, never while pending). |
| strategy/members/k1/cp1.py | `Cp1Momentum` and the three factories. Spec section 1. |
| strategy/members/k1/cp2.py | `Cp2Breakout` and the three factories. Section 2. `F_REGULAR_CT = time(15, 8)` is a literal used only in `trading_windows` (`rules.sessions` is not an allowed import). |
| strategy/members/k1/cp3.py | `Cp3CloseLocation`, `DailyBar`, `clv_side` and the three factories. Section 3. |
| tests/test_k1_members_ports.py | The kit (root-aware), the EC-CAL anchor, declarations, helpers and K1-cp1-01. |
| tests/test_k1_members_ports_cp2.py | K1-cp2-01. |
| tests/test_k1_members_ports_cp3.py | K1-cp3-01. |
| tests/test_k1_members_ports_events.py | The CPI window and the FOMC / ISM event minutes for all three ports. It uses real rows of the frozen release calendar, read-only. |

strategy/members/k1/__init__.py is untouched and still 0 bytes.

**Equity calendar handling.** A bar is identified by its CT date and clock (K7-L-01).
- CP1 records the first bar only when it opens at 17:00 on CT date `trade_date - 1`. That covers Sunday 17:00 for a Monday, Monday 05-26 17:00 for Tuesday 05-27, and Thursday 12-25 17:00 for Friday 12-26.
- CP2 and CP3 read only bars of CT date d.
- The kit builds the evening bars after Memorial Day the way `data.group_session.early_halt_labels` labels real bars: they carry the holiday's "12:00", because the label follows the CT calendar date. CP3 therefore tests the early halt only on bars of CT date d, so the Tuesday after the holiday is traded and counts as complete. This is pinned.

**Declarations to freeze:** `MemberDecl("<id> <root>", ordinal, "strategy.members.k1.cpN", "make_<root>", (LegSpec(root, True),))` with ordinals 1-9 as in the S0.2 table. The tmp_path test writes and verifies exactly these 9.

## 2. What each test pins

**Main file (kit, declarations, K1-cp1-01)**

Anchors and declarations:
- **EC-CAL anchor:** every date the kit uses is checked against EC-CAL. 19 regular dates have F 15:08 on all three roots. 05-26 (halt 12:00, F 11:30), 07-03 (12:15, F 11:45) and 07-04 (12:00, F 11:30) are trade dates; 04-18 and 12-25 are not; there are no booked-forward dates.
- **Declarations and static check:**
  - the F-1 check on all 4 files;
  - label equals name and the single leg `LegSpec(root, True)`;
  - exactly the three factories;
  - the member ids;
  - S0.12 windows per root;
  - frozen O, C, q_c and tick per root;
  - roots outside the cluster refused (MES, ES, NQ, RTY, YM);
  - the 9-declaration freeze write and verify under tmp_path, after `check_cluster_sources`.
- **Kit and helper checks:**
  - ticks per root;
  - `shift`;
  - a None bar changes nothing;
  - `exit_if_due` (pending, flat, closes q_c, CT date d only);
  - without a bar of the previous trade date the engine refuses any open (`engine_price_limit_reference_unavailable`), so `run` adds that date's five evening bars, on which no port acts.

CP1 rules (all on three roots unless noted):
- **Signal and entry:**
  - The buy and sell cases use paths where close-close or open-open would give the opposite sign.
  - Fills are 14:30 and 14:59, q_c each way.
  - One tick either side of zero decides the side; zero signal gives no trade.
- **Missing bars:**
  - A missing 17:00, 08:59 or 14:29 bar gives no trade.
  - With 14:58 missing, the exit goes on 14:59.
  - No exit before 14:58.
  - A refused exit (`engine_min_hold`) is resent.
- **Instrument guard:** only the two signal bars are compared, not the entry bar.
- **Engine closes and early halts:**
  - After an engine flatten or a D9.7 exit: no member exit and no re-entry.
  - On Memorial Day with real-shaped bars there is no 14:29 bar and no trade.
  - With bars kept to 15:12 the member emits at 14:29 and the engine refuses it (`engine_flatten_window`).
- **First bar by calendar case:**
  - Monday opens Sunday 17:00.
  - After Memorial Day the first bar is the Monday 17:00 reopen carrying "12:00", and the holiday's own 08:59 bar does not carry over; without the reopen bar there is no trade.
  - After a full closure: Thursday 12-25 17:00 and Sunday 04-20 17:00.
- **CT-date identification (direct calls):** a 17:00 bar of CT date d-2 or d-3 is not the first bar; 08:59 or 14:29 bars of CT date d-1 are not the signal or entry bar.
- **Once per day:** once per trade date and never while pending (direct); state resets across dates.

**cp2 file**

Rules on three roots:
- **Literals:** 15, 4, 75 and 15:08, and 4 ticks = 1.00 / 0.40 / 4.
- **Breakout and exit:** buy and sell; exit on the 75th present bar (08:45 → fills 08:46 and 10:01), q_c each way.
- **Buffer in ticks:** 3 ticks beyond gives no entry, 4 ticks gives an entry, on both sides.
- **Buffer in prices:**
  - MNQ: OR_high 20000.50 → a close of 20001.50 triggers, 20001.25 does not.
  - M2K: 2000.20 → 2000.60 triggers, 2000.50 does not.
  - MYM: 40002 → 40006 triggers, 40005 does not.
  - The same holds on the sell side.
- **Entry use:** no entry while pending (direct); a missing bar inside the hold moves the exit one bar; no entry from 15:00; a 14:59 trigger is held to F 15:08; the first qualifying bar uses the day even when the engine refuses it.
- **Range:** taken from the present bars; a D9.7 exit ends the day; Memorial Day trades until the engine flattens at 11:30.

On one root:
- The 08:30 bar is a range bar; the 08:45 bar is eligible and not a range bar.
- One OR bar is enough; no OR bar gives no trade.
- max high and min low; bars at 08:29 and the evening bars are not range bars.
- No instrument guard.
- A deferred entry fill starts the count; a deferred exit is not resent.
- No C-2 exit; F binds from a 13:53 fill; a synthetic F flattens.
- One entry after the exit; state and range reset across dates.
- The holiday's range and trigger stay on 05-26; Sunday evening bars are not Monday's range.
- Direct: bars of CT date d-1 are neither range nor eligible bars and do not use the day's entry.

**cp3 file**

- **Literals:** cuts Decimal 0.8 and 0.2; C-1 and C-2.
- **Cut behaviour on three roots:**
  - CLV exactly 0.8 buys and exactly 0.2 sells (08:31 / 14:59, q_c).
  - 0.3, 0.5 and 0.7 give no trade; 1.0 and 0.9 buy; 0.1 and 0.0 sell.
- **Exactness:**
  - On M2K a float CLV is 0.7999… and 0.2000…, yet the member trades on both cuts.
  - The `clv_side` table includes one part in 15, 100 and 1000 inside each cut, plus span 1, span 0 and a negative span.
- **Complete days and d-1:**
  - min low; accumulators reset.
  - Range 0 gives no trade; warm-up; d-1 is used only after it is finalised.
  - d-1 is the most recent complete day. The test day has a wide range, so a close carried over from the day before would change the trade.
  - Two instrument ids in the window make a day incomplete; ids outside the window do not.
  - The guard compares d-1 with the 08:30 bar only.
  - A missing 08:30 bar means no trade and an incomplete day.
- **Early halts:**
  - The Memorial Day halt is not traded and is incomplete: Tuesday reads Friday, both with bars to 15:12 and with the real 12:00 end.
  - A buy prior is still not traded on the halt day.
  - The Tuesday after is not a halt day: it is traded and complete for Wednesday.
  - 07-03 and 07-04 are both skipped (Monday reads 07-02), and the flag resets for 07-08.
- **Weekends and closures:** Good Friday (Monday reads Thursday); Sunday evening bars are not part of Monday's daily bar.
- **Exits and engine:** a missing 14:58 bar puts the exit on 14:59; the D9.5a guard moves the fill; a synthetic F flattens; a D9.7 exit ends the day.
- **Direct calls:** bars of CT date d-1 are neither the entry bar nor part of the daily bar; once per day; never while pending.

**events file (real frozen release calendar)**
- **Anchor:** FOMC 2025-05-07 13:00 CT and ISM 2025-05-05 09:00 CT carry MNQ, M2K and MYM; CPI 2025-05-13 07:30 CT is a CPI row.
- **CPI window:** for all 3 ports on 3 roots, with a 200-tick jump on every bar from 07:25 to 07:35 on 2025-05-13, no port emits an intent from a bar in [07:25, 07:35], nothing is emitted before 08:30, and each port's own trade is unchanged.
- **Event minutes:**
  - CP1 and CP3 intents and fills are identical with and without the calendar on FOMC and ISM dates.
  - CP2 on an ISM date: a trigger at 08:59 or 09:00 fills at 09:02, and the 75-bar count starts at that fill (exit 10:16 / 10:17). Without the calendar the fill is 09:00 and the exit 10:14 / 10:15.
  - CP2 on an FOMC date: a trigger at 12:59 or 13:00 fills at 13:02. An exit due at 12:59 fills at 13:02 and is sent once.

## 3. Mutants

**Method.** coderA_mutants.py runs in the isolated copy coderA_mut_repo, which holds the code and reports but no bar data and no sealed store. For each mutant it applies one textual change, runs the relevant port test files (PYTHONDONTWRITEBYTECODE=1), records the failing tests, restores the original bytes, and finally asserts the copy equals the originals.

**Runs.**
- **Run 1 (01:17-01:40 PDT):** 182 mutants, 177 killed. One survivor was a real gap: C3-24, where `_close` is not reset between days. I fixed the test `test_cp3_d_minus_1_is_the_most_recent_complete_day` by giving Tuesday a range of B to B+30.
- **Script loss:** coder B overwrote the shared mutants.py at 01:21. Run 1 was already loaded and unaffected. I rebuilt the script as coderA_mutants.py, with the list recovered verbatim from run 1's JSON.
- **Final run (01:42-02:05):** 182 mutants, 178 killed, 4 survivors. Each survivor behaves exactly like the original on every input:
  - **PC-05:** `_ANCHOR_DAY` 2000-01-03 → 01-04. `shift` never crosses midnight.
  - **C2-19:** `self._triggered and position` → `position`. The leg holds a position only after its own entry, and `_triggered` is set at that entry.
  - **C2-34:** eligibility test `not self._range_end <= at < c` → `not at < c`. Bars before O come before any range bar, when `_hi` is None, and bars in [O, O+15) return earlier; with bars in time order the lower bound can never matter.
  - **C3-34:** `at == self._close_at` → `>=`. `_accumulate` has already returned for any bar at or after 15:00.

**Tests no mutant failed.** Four are anchors or contracts rather than member rules: the EC-CAL facts, the release-row facts, the static check, and the exact-three-factories test. The fifth is the `clv_side` case with a negative span, an input that cannot occur because H ≥ L.

**Reading the table.** The "first" killing test is the most specific one. C3-01 and C3-04 are also killed by the behaviour cases `clv[100-79]`, `[1000-799]`, `[100-21]` and `[1000-201]`. C3-33 is `at == self._leg.o` → `>=` on the `_has_open_bar` line; C3-34 is the `_close_at` line.

| Id | Change | Result | n; first killing test |
|---|---|---|---|
| PC-01 | EXPOSURES drops MYM | killed | 81; cp1_buys_on_a_positive_signal… |
| PC-02 | EXPOSURES adds MES | killed | 10; leg_facts_refuses_a_root_outside_the_cluster |
| PC-03 | EXPOSURES reordered | killed | 9; factories_name_the_label_and_trade_one_leg |
| PC-04 | NS_PER_S 1e9 → 1e6 | killed | 207; cp1_buys… |
| PC-05 | anchor day +1 | SURVIVED | - |
| PC-06 | `not in` → `in` EXPOSURES | killed | 226; leg_facts_refuses… |
| PC-07 | label space → dash | killed | 9; factories_name… |
| PC-08 | shift + → - | killed | 179; shift_moves_a_clock_time |
| PC-09 | astimezone CT → UTC | killed | 175; cp1_buys… |
| PC-10 | Chicago → New_York | killed | 175; cp1_buys… |
| PC-11 | round → int | killed | 3; prices_become_integer_vendor_ticks |
| PC-12 | is_flat `== 0` → `!= 0` | killed | 175; cp1_buys… |
| PC-13 | is_flat ignores pending | killed | 9; cp1_emits_at_most_one_entry…_none_while_pending |
| PC-14 | exit `position == 0` → `!=` | killed | 87; an_exit_is_not_sent_while_an_order_is_pending |
| PC-15 | exit `or` → `and` | killed | 3; an_exit_is_not_sent… |
| PC-16 | exit drops pending | killed | 3; an_exit_is_not_sent… |
| PC-17 | exit date `!=` → `==` | killed | 87; an_exit_is_not_sent… |
| PC-18 | exit drops CT-date test | killed | 3; an_exit_is_not_sent… |
| PC-19 | exit `<` → `<=` | killed | 81; an_exit_is_not_sent… |
| PC-20 | exit `<` → `>` | killed | 95; an_exit_is_not_sent… |
| PC-21 | exit side flipped | killed | 87; an_exit_is_not_sent… |
| PC-22 | abs(position) → position | killed | 35; an_exit_is_not_sent… |
| PC-23 | q_c → 1 | killed | 24; cp1_buys… |
| PC-24 | tick → 0.25 literal | killed | 47; cp1_the_signal_is_one_tick_either_side_of_zero |
| PC-25 | tick of MNQ for all | killed | 47; cp1_the_signal_is_one_tick… |
| PC-26 | O and C swapped | killed | 181; cp1_buys… |
| PC-27 | LegSpec traded False | killed | 203; cp1_buys… |
| C1-01 | 17:00 → 17:01 | killed | 17; cp1_missing_first_bar_is_no_trade_l05 |
| C1-02 | 17:00 → 16:59 | killed | 49; cp1_buys… |
| C1-03 / 04 | O+29 → 28 / 30 | killed | 52 / 52; cp1_buys… |
| C1-05 / 06 | C-31 → 30 / 32 | killed | 52 / 52; cp1_buys… |
| C1-07 / 08 | C-2 → 1 / 3 | killed | 31 / 31; cp1_buys… |
| C1-09 / 10 | ONE_DAY 2 / 0 | killed | 46 / 46; cp1_buys… |
| C1-11 | first bar open → close | killed | 37; cp1_buys… |
| C1-12..16 | the five trading-window edits | killed | 3 each; trading_windows_are_the_s0_12_intervals |
| C1-17 / 18 / 19 | sign of O+29, C-31, C-2 | killed | 49 / 49 / 34; cp1_buys… |
| C1-20 | first/signal not reset | killed | 7; cp1_missing_first_bar… |
| C1-21 | _entered not reset | killed | 11; cp1_trades_once_per_trade_date_on_consecutive_days |
| C1-22 | drop signal-None check | killed | 5; cp1_missing_0859_signal_bar_is_no_trade |
| C1-23 | drop first-None check | killed | 7; cp1_missing_first_bar… |
| C1-24 | ids `!=` → `==` | killed | 46; cp1_buys… |
| C1-25 | drop id check | killed | 3; cp1_signal_bars_with_two_instrument_ids…_l06 |
| C1-26 | signal sign flipped | killed | 38; cp1_buys… |
| C1-27 | drop zero check | killed | 6; cp1_zero_signal_is_no_trade |
| C1-28 | `s == 0` → `s <= 0` | killed | 13; cp1_sells_on_a_negative_signal |
| C1-29 | side `>` → `<` | killed | 38; cp1_buys… |
| C1-30 | `s > 0` → `s > 1` | killed | 3; cp1_the_signal_is_one_tick… |
| C1-31 / 32 | reset test inverted / removed | killed | 14 / 14; cp1_missing_first_bar… |
| C1-33 | position test inverted | killed | 46; cp1_buys… |
| C1-34 | first bar: drop CT-date test | killed | 1; cp1_the_first_bar_is_the_1700_bar_of_ct_date_d_minus_1_only |
| C1-35 | `day - 1` → `day + 1` | killed | 46; cp1_buys… |
| C1-36 | `at ==` → `>=` 17:00 | killed | 10; cp1_missing_first_bar… |
| C1-37 | `== day-1` → `< day` | killed | 1; cp1_the_first_bar_is_the_1700_bar_of_ct_date_d_minus_1_only |
| C1-38 | any clock of d-1 | killed | 10; cp1_missing_first_bar… |
| C1-39 | drop CT-date-d return | killed | 1; cp1_signal_and_entry_bars_are_bars_of_ct_date_d |
| C1-40 | signal `==` → `>=` | killed | 46; cp1_buys… |
| C1-41 | signal close → high | killed | 6; cp1_sells… |
| C1-42 | entry `!=` → `==` | killed | 46; cp1_buys… |
| C1-43 | drop _entered | killed | 3; cp1_emits_at_most_one_entry… |
| C1-44 | drop is_flat | killed | 3; cp1_emits_at_most_one_entry… |
| C1-45 | entry `!=` → `<` | killed | 3; cp1_missing_1429_entry_bar_is_no_trade_l04 |
| C1-46 | _entered = False | killed | 3; cp1_emits_at_most_one_entry… |
| C1-47 | qty q → 1 | killed | 8; cp1_buys… |
| C1-48 / 49 / 50 | factory roots swapped | killed | 9 / 7 / 4 |
| C1-51 | member id | killed | 2; member_ids_are_the_catalog_ids |
| C2-01 / 02 | RANGE 14 / 16 | killed | 4 / 49; cp2_literals… |
| C2-03 / 04 | BUFFER 3 / 5 | killed | 14 / 74; cp2_literals… |
| C2-05 / 06 | HOLD 74 / 76 | killed | 57 / 57; cp2_literals… |
| C2-07 | F 15:07 | killed | 6; cp2_literals… |
| C2-08 | range end O-15 | killed | 71; cp2_breakout_fills…75_present_bars |
| C2-09 | window starts O+15 | killed | 3; trading_windows… |
| C2-10 | hi/lo not reset | killed | 2; cp2_the_range_resets_each_trade_date |
| C2-11 | _triggered not reset | killed | 2; cp2_state_resets_each_trade_date |
| C2-12 | _held not reset | killed | 2; cp2_state_resets… |
| C2-13 | held += 2 | killed | 58; cp2_breakout_fills… |
| C2-14 | `<` → `<=` HOLD | killed | 54; cp2_breakout_fills… |
| C2-15 | hold exit ignores pending | killed | 4; cp2_a_deferred_exit_is_not_sent_twice |
| C2-16 | exit side flipped | killed | 54; cp2_breakout_fills… |
| C2-17 | abs dropped | killed | 16; cp2_breakout_down_sells |
| C2-18 | reset inverted | killed | 3; cp2_state_resets… |
| C2-19 | drop `_triggered and` | SURVIVED | - |
| C2-20 | hold on `_triggered` alone | killed | 24; cp2_breakout_fills… |
| C2-21 | drop CT-date test | killed | 1; cp2_range_and_eligible_bars_are_bars_of_ct_date_d |
| C2-22 | `o <=` → `o <` | killed | 1; cp2_the_0830_bar_is_a_range_bar |
| C2-23 | `< end` → `<= end` | killed | 46; cp2_breakout_fills… |
| C2-24 | range without lower bound | killed | 6; cp2_without_an_opening_range_bar… |
| C2-25 / 26 | max ↔ min | killed | 11 / 7; cp2_the_buffer_is_exactly_four_ticks… |
| C2-27 / 28 | hi / lo from close | killed | 11 / 7; cp2_the_buffer_is_exactly… |
| C2-29 | drop `_triggered` return | killed | 7; cp2_one_entry…_engine_refuses_it |
| C2-30 | drop None checks | killed | 2; cp2_without_an_opening_range_bar… |
| C2-31 | `< C` → `<= C` | killed | 3; cp2_no_entry_from_1500 |
| C2-32 | `end <=` → `end <` | killed | 43; cp2_breakout_fills… |
| C2-33 | drop is_flat | killed | 3; cp2_no_entry_while_an_order_is_pending |
| C2-34 | drop eligibility lower bound | SURVIVED | - |
| C2-35 | close → high | killed | 17; cp2_breakout_down_sells |
| C2-36 | `>=` → `>` | killed | 62; cp2_breakout_fills… |
| C2-37 | `+ buffer` → `- buffer` | killed | 46; cp2_the_buffer_is_exactly… |
| C2-38 | `<=` → `<` | killed | 16; cp2_breakout_down_sells |
| C2-39 | `- buffer` → `+ buffer` | killed | 46; cp2_the_buffer_is_exactly… |
| C2-40 | sell against hi | killed | 9; cp2_the_buffer_is_exactly… |
| C2-41 | buy → sell | killed | 59; cp2_breakout_fills… |
| C2-42 | _triggered = False | killed | 60; cp2_breakout_fills… |
| C2-43 | qty → 1 | killed | 7; cp2_breakout_fills… |
| C2-44 / 45 / 46 | factory roots swapped | killed | 6 / 9 / 4 |
| C2-47 | member id | killed | 1; member_ids… |
| C3-01 / 02 | 0.8 → 0.79 / 0.81 | killed | 3 / 43; cp3_literals… |
| C3-03 / 04 | 0.2 → 0.19 / 0.21 | killed | 19 / 3; cp3_literals… |
| C3-05 / 06 | C-1 → C-2 / C | killed | 56 / 59; cp3_literals… |
| C3-07 / 08 | C-2 → 1 / 3 | killed | 48 / 51; cp3_literals… |
| C3-09 | span uses close | killed | 33; cp3_prior_clv_at_02_sells |
| C3-10 | `span <= 0` → `< 0` | killed | 4; cp3_clv_cuts_are_compared_exactly |
| C3-11 | num = high - close | killed | 68; cp3_prior_clv_at_08_buys… |
| C3-12 / 13 | `>=` → `>`, `<=` → `<` | killed | 42 / 18 |
| C3-14 / 15 | cut comparisons inverted | killed | 50 / 25 |
| C3-16 | drop 08:30-bar requirement | killed | 1; cp3_missing_0830_bar…incomplete |
| C3-17 | drop halt requirement | killed | 4; cp3_early_halt_day_is_not_traded… |
| C3-18 | `== 1` → `>= 1` ids | killed | 1; cp3_a_day_with_two_instrument_ids… |
| C3-19 | incomplete replaces d-1 | killed | 10; cp3_d_minus_1_is_the_most_recent_complete_day |
| C3-20 | halt not reset | killed | 2; cp3_the_tuesday_after_memorial_day_is_not_a_halt_day |
| C3-21 | open-bar flag not reset | killed | 1; cp3_missing_0830_bar… |
| C3-22 | _entered not reset | killed | 58; cp3_prior_clv_at_08_buys… |
| C3-23 | hi/lo not reset | killed | 1; cp3_day_accumulators_reset… |
| C3-24 | _close not reset | killed | 1; cp3_d_minus_1_is_the_most_recent_complete_day |
| C3-25 | ids not reset | killed | 4; cp3_a_day_with_two_instrument_ids… |
| C3-26 / 27 | halt test inverted / removed | killed | 58 / 4 |
| C3-28 / 29 | window `o <` / `<= C` | killed | 58 / 57 |
| C3-30 | only the last id kept | killed | 1; cp3_a_day_with_two_instrument_ids… |
| C3-31 / 32 | max ↔ min | killed | 57 / 2 |
| C3-33 | open-bar `==` → `>=` | killed | 1; cp3_missing_0830_bar… |
| C3-34 | close-bar `==` → `>=` | SURVIVED | - |
| C3-35 | close-bar `==` → `<=` | killed | 2; cp3_warm_up… |
| C3-36 | C from high | killed | 1; cp3_the_daily_low_is_the_min_low |
| C3-37 | drop day-d halt exclusion | killed | 9; cp3_early_halt_day_is_not_traded… |
| C3-38 / 39 | guard inverted / removed | killed | 58 / 3 |
| C3-40 | reset inverted | killed | 58 |
| C3-41 | drop CT-date test | killed | 2; cp3_the_tuesday_after_memorial_day_is_not_a_halt_day |
| C3-42 | position test inverted | killed | 58 |
| C3-43..47 | entry-condition edits | killed | 58 / 3 / 3 / 1 / 3 |
| C3-48 / 49 | H↔L swapped, C → H | killed | 58 / 30 |
| C3-50 | qty → 1 | killed | 7 |
| C3-51 / 52 / 53 | C-1 sign, C-2 sign, window | killed | 58 / 50 / 3 |
| C3-54 / 55 / 56 | factory roots swapped | killed | 7 / 4 / 7 |
| C3-57 | member id | killed | 1 |

Total 182: killed 178, survived 4. The per-mutant failing-test lists are in coderA_mutants_result.json.

## 4. Commands and results (PDT, 2026-09-28)

| Command | Result |
|---|---|
| `uv run pytest -q tests/test_k1_members_ports.py tests/test_k1_members_ports_cp2.py tests/test_k1_members_ports_cp3.py tests/test_k1_members_ports_events.py tests/test_stage_e_template.py tests/test_stage_e_freeze.py` (PYTHONPYCACHEPREFIX unset), 02:05 | 315 passed in 11.35s (268 port cases) |
| `uv run ruff check` on the 4 member files and 4 test files | All checks passed |
| `check_member_source(rel, src, "K1")` on each of the 4 files, plus `check_cluster_sources("K1", scratch freeze_root)` holding only my 4 files and empty `__init__` files | [] for each; None |
| `nice -n 10 .venv/bin/python coderA_mutants.py` (isolated copy), 01:42-02:05 | 182 mutants: 178 killed, 4 equivalent survivors |
| `uv run python -m data.holdout status` | unlocks_logged 0 |

sha256 of the delivered files:
- _port_common.py 55ba92ef01591c66241b2698d8fc99e23210c8fb0826658b158af129637447dc
- cp1.py ccc9d83e2b20db011ba34d314d4b494b0dac55f89d0d9b7c75f3ec48131e848c
- cp2.py 430206138665cdda12497bdd9d2de777ac8156a107974e6d0a19d61c9b6f6c3e
- cp3.py f8e533d589b50ac817f87647be7de400d57a388f065cd6f740849c5c47374882
- test_k1_members_ports.py 525877ba6d71e2855ba3198761ff37674fad30e3798cd5ebcbb664beacf62225
- test_k1_members_ports_cp2.py 96dbc764bc71554a227cbacdde79e681b71caf439ca6c29ff4485888f51ed42f
- test_k1_members_ports_cp3.py 2840f07869432d2278fbcf4b31e5ce4c0fd5ae91253e11001d5005dfe8fc866e
- test_k1_members_ports_events.py 93763b1f157fb3d8f5479d2f02c79757362d20934f8f2ee2a81e5e79ffa77a0f

## 5. Questions and notes for the lead

No question stopped the work: the spec and section 8 fixed every detail the ports need.

1. **Engine fact, harness-level, check it before the real screen.** MNQ, M2K and MYM are hard-limit products. Without a settlement proxy from the previous EC-CAL trade date, the engine refuses every open (`engine_price_limit_reference_unavailable`). If the runner does not feed that previous date's bars, the window's first trade date cannot open for any K1 member. The kit adds five evening bars of the previous date for this reason; the test `test_the_kit_adds_the_price_limit_reference_the_engine_needs` shows both the refusal and the fix.
2. **Early-halt labels after a holiday.** `early_halt_ct` follows the CT calendar date, so trade date 05-27's evening bars (Monday from 17:00) carry "12:00". CP3 tests the halt only on bars of CT date d, which is pinned. A member reading the label on every bar of trade date d would wrongly treat each post-holiday trade date as a halt.
3. **CT-date mutants the equity calendar cannot tell apart.** Four mutants weaken the CT-date identification: C1-34, C1-37, C1-39 and C2-21. Real equity bars could never reveal them, because the equity calendar produces no bar at a rule's clock on another CT date. They are killed only by direct-call tests using bars that never occur. C3-41 is the exception: the post-holiday label test kills it with bars shaped like the real ones.
4. **CPI rows in the release calendar.** The CPI rows' `products` list MNQ but not M2K or MYM. The spec says the engine applies D9.12 to all three through rules/constraints. No K1 port fills before 08:31, so it never matters here.
5. **Scratch overwrite.** Coder B overwrote my shared scratch script at 01:21. I rewrote it under coder-specific names, and no repository file was affected.
