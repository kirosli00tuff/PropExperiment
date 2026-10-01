# Stage E.8 Task 2, MemberCoder-A (opus, xhigh): K6 core ports and K6-crushgap-01

Written 2026-10-01 01:30 PDT by MemberCoder-A-OpusXHigh. Brief: reports/stage_e8_briefs/2A_member_coder_A.md.
Spec: reports/stage_e8_member_specs.md sections 0-4, 9 (and 10, read only for context).
No bar file was opened and no bar loader or runner was called. There was no web access, no commit and no worker.
No file outside the list below was edited. strategy/members/k6/__init__.py is untouched (0 bytes), and none of coder B's files
was written. coder B's `_calendar.py` existed (written 00:26) before crushgap.py was started.

## 1. Files

| File | sha256 (first 16) | Content |
|---|---|---|
| strategy/members/k6/_port_common.py | b37d068267619e1b | `leg_facts` (O, C from `day_session_ct`, q_c from the vehicle table, vendor tick and group from rules.products), `label`, `shift`, `ct_open`, `to_ticks`, `is_flat`, `exit_if_due` (S0.7, E.3-L-22). Copied in structure from k1/_port_common.py. |
| strategy/members/k6/cp1.py | 250b615c0d08e7c1 | `Cp1Momentum`, factories make_zc, make_zw, make_zs, make_zm, make_zl, make_he, make_le |
| strategy/members/k6/cp2.py | fc25ff092bef1d7a | `Cp2Breakout`, the same seven factories, `F_REGULAR_CT` |
| strategy/members/k6/cp3.py | cfb9b6672505fef3 | `Cp3CloseLocation`, `DailyBar`, `clv_side`, the same seven factories |
| strategy/members/k6/crushgap.py | 339a5ed7fcac3dbb | `CrushGap`, `make_zs`, `gpm_units_per_tick`, `FILTER_UNITS`; imports coder B's `_calendar` (GRAIN_TRADE_DATES, GRAIN_FULL_SESSIONS, previous_trade_date) |
| tests/test_k6_members_ports.py | b0017f38a82b19da | the synthetic kit, calendar facts, declarations, K6-cp1-01 (188 tests) |
| tests/test_k6_members_ports_cp2.py | 43f6233f4faa1a33 | K6-cp2-01 (111 tests) |
| tests/test_k6_members_ports_cp3.py | a3648c212c0cc5c2 | K6-cp3-01, including engine-level case (2) (169 tests) |
| tests/test_k6_members_crushgap.py | b6112559407449e7 | K6-crushgap-01, including engine-level case (1) (51 tests) |

Each module has a member class with `name` (= the S0.2 label), `legs`, `trading_windows` (S0.12) and `on_minute`. q_c is always
`load_frozen_tables().vehicles[root].q_c` and ticks always come from `rules.products.product(root).vendor_tick`. O and C come
from `load_frozen_tables().day_session_ct[root]`. Every price comparison is in integer vendor ticks. CP3's CLV and crushgap's
GPM are compared exactly in integers. All five modules pass `screening.stage_e_freeze.check_member_source` (result `[]`
for each). The tests also freeze the 21 port declarations (ordinals 1-21) and crushgap (ordinal 22) under tmp_path and
verify them with the real freeze code.

## 2. How each rule is implemented (with the readings applied)

- **K6-cp1-01.** Signal = close of the 08:59 bar minus open of the first bar, in ticks. The two signal bars must have one
  instrument_id, and zero is no trade. The entry is on the C-31 bar of CT date d exactly (grains 12:44, livestock 12:29).
  The exit is on the first present bar of CT date d at or after C-2 (13:13 / 12:58), resent while refused.
  - Grain first bar (K6-L-01): the first bar seen after the trade-date reset that has `trade_date == d` and a CT open
    `>= datetime(d-1, 19:00 CT)`. Livestock first bar (K6-L-02): the bar at O = 08:30 of CT date d exactly.
  - The grain first bar is recorded without returning, so a bar can be both the first bar and the 08:59 signal bar. That
    happens only if no bar of trade date d exists before 08:59.
- **K6-cp2-01.** Same structure as K1 CP2. The OR is taken from present bars in [O, O+15) of CT date d. The buffer is
  `BUFFER_TICKS = 4` vendor ticks. Eligible bars are [O+15, C). The first qualifying bar uses the day's entry. The exit
  comes after 75 present bars counted from the bar after the entry intent bar, with no C-2 exit.
  - trading_windows end at the regular F, through a literal per-group map `F_REGULAR_CT = {grains: 13:18, livestock: 13:03}`
    (a member cannot import rules.sessions). It is pinned against `rules.sessions.flatten_time_ct` for all seven roots.
- **K6-cp3-01.** Same structure as K1 CP3, Family H. A day is complete when it has the 08:30 and C-1 bars, no
  early_halt_ct label on any bar of CT date d, and one instrument_id in [O, C). It is finalised when the next trade
  date's first bar arrives, and d-1 is the most recent complete day.
  - A d whose 08:30 bar carries early_halt_ct is not traded. The guard compares d-1's id with the 08:30 bar's id. The
    CLV cuts 0.8 and 0.2 are applied as exact integer cross-products, Range must be > 0, and the exit is at C-2.
- **K6-crushgap-01.** Legs are (ZS traded, ZM signal, ZL signal).
  - GPM units per vendor tick = weight x vendor_tick / vendor_price_factor / 0.0001. They are computed in Decimal from
    `GPM_WEIGHTS = {ZM 0.022, ZL 11, ZS -1}` and rules.products, and give ZM 22, ZL 11, ZS -25. The module raises if a
    value is not an integer. `FILTER_UNITS = 0.02 / 0.0001 = 200`, also derived.
  - Each leg's C-1 (13:14) bar is recorded by its own trade date and CT date. This happens on every grid minute,
    including minutes with no ZS bar.
  - On the ZS bar at O = 08:30 of CT date d (exact), the member requires: d in GRAIN_FULL_SESSIONS; d-1 =
    `previous_trade_date(GRAIN_TRADE_DATES, d)`; and, for every leg, its 08:30 bar at the same grid minute and its
    recorded 13:14 bar dated d-1 with the same instrument_id.
  - G units = sum of units[r] x (open_0830 - close_1314). G >= 200 buys ZS and G <= -200 sells, both non-strict. The exit
    is on the first ZS bar of CT date d at or after 13:13. No intent is ever sent on ZM or ZL.

## 3. Points for the lead (no question blocked the work; these are consequences of the text, flagged)

1. **Grain CP1 first bar on a late-open date whose 08:30 bar is missing.** I followed the spec table's definition
   (section 1 row "Trade date's first bar, grains", K6-L-01: "the earliest bar with trade_date d whose CT open is at or
   after 19:00 on the calendar day before d"), with the 08:30 bar as its normal result on a late-open date. If the 08:30
   bar is missing on such a date, the rule takes the next bar (08:31).
   - This is pinned by the second half of `test_cp1_grain_late_open_first_bar_is_the_0830_bar_l01`.
   - The alternative reading ("the 08:30 bar exactly; missing: no trade", as livestock K6-L-02) would change a trade only
     on 2025-12-26 or 2026-01-02, and only if the 08:30 bar is missing there. 2025-11-28 has no 12:44 bar.
   - The same general rule means that on a regular date with every evening bar missing, the first bar is the earliest
     overnight bar of CT date d (the 00:00-07:45 part of the evening session). This is pinned by
     `test_cp1_grain_no_evening_bar_takes_the_first_bar_of_ct_date_d_l01`.
   - If the lead reads either case otherwise, it is a one-line change in `Cp1Momentum._is_first_bar`.
2. **ZS: the D9.7 lower stop sits beyond the MLL at one contract (observation, harness side, no action taken).** With a
   prior settlement of 1050.00 cents/bu (June 2025 initial limit), the D9.7 stops are 216 vendor ticks (54 cents/bu) from
   S. 54 cents x 5,000 bu = $2,700, which is more than a $2,000 drawdown limit.
   - In the synthetic CP1 D9.7 test on ZS, a long hit by a close at the lower stop was closed by the engine as
     `mll_liquidation` at the stop bar, not by D9.7.
   - The D9.7 tests therefore use the upper stop (a gain), which fires D9.7 on all seven roots. Stop offsets in vendor
     ticks: ZC 104, ZW 116, ZS 216, ZM 140, ZL 200, HE 88, LE 114, at the kit's base prices and the 2025-06-03 limits.
3. **Engine timing seen in the tests** (no member change): the engine's forced flatten fills at the open of the F bar
   (13:18 grains, 13:03 livestock, 11:45 on the 2025-12-24 halt day). It is queued at the F-1 bar's decision.
4. **crushgap identifies a signal leg's 08:30 bar by the ZS bar's grid minute** (same CT date and clock, K7-L-01). It
   does not check the signal bar's trade_date field separately, because all grain legs share one calendar.

## 4. What the tests pin

All engine cases run the real `screening.stage_e_engine.run_engine` under `StageERules` (`tests._stage_e_canary_kit.rules_for`).
The kit adds the previous EC-CAL trade date's 10:00-10:05 bars as the D9.7 prior-settlement reference. Every date used
is anchored to EC-CAL by `test_the_synthetic_scenarios_are_ec_cal_facts`: regular dates; Memorial Day closure; early halts
2025-11-28 and 2025-12-24 (grains 12:05, livestock 12:15); grain late opens 2025-11-28, 2025-12-26 and 2026-01-02; F
13:18 / 13:03 and 11:45 on halt days.

- **Declarations (ports file).**
  - Freeze static check on the four port files (crushgap in its own file).
  - Factories: name = label, one traded leg, fresh state, exactly the seven factories, and the member ids.
  - trading_windows for all 3 ports x 7 roots against S0.12.
  - Frozen O/C, q_c = 1, vendor tick and group per root.
  - `leg_facts` refuses non-K6 roots. The 21 port declarations freeze and verify under tmp_path.
  - Tick conversion per root, including rounding. A None bar changes no state. No exit while pending.
  - The kit's reference bars are needed (`engine_price_limit_reference_unavailable` without them) and make no member act.
- **CP1 (7 roots).**
  - Buy and sell. Entry and exit times per group: intents 12:44/13:13 and fills 12:45/13:14 for grains; intents
    12:29/12:58 and fills 12:30/12:59 for livestock.
  - q_c. The signal one tick either side of zero; zero signal gives no trade.
  - Grain first bar: Monday reads Sunday 19:00. A missing 19:00 bar takes 19:01, and two missing take 19:02. With no
    evening bar the first is the first bar of CT date d. On late opens 2025-12-26 and 2026-01-02 it is the 08:30 bar, or
    08:31 if 08:30 is missing.
  - Direct calls on the grain first bar: bars before 19:00 of d-1 (18:59 of d-1, 19:00 of d-2) are never the first bar.
    The first bar may be the 08:59 bar itself.
  - Livestock first bar: 08:30 exactly; missing gives no trade even with 08:31 present; it must be on CT date d.
  - Missing 08:59 bar: no trade. Two instrument_ids across the signal bars: no trade. The entry bar is not guarded.
  - Missing entry bar: no trade. Missing C-2 bar: exit on C-1. No exit before C-2. A refused exit (engine_min_hold) is
    resent.
  - The synthetic-F flatten sends no member exit.
  - Real D9.7 upper stop on all 7 roots: a forced `price_limit_exit` with no member exit or re-entry afterwards; one tick
    inside the stop gives the normal trade.
  - 2025-12-24: with the bars cut at the halt there is no entry bar. With bars to C, the entry is refused by the engine
    (`engine_flatten_window`).
  - One trade a day, state resets, the Tuesday after Memorial Day, once per date and not while pending. Signal and entry
    bars must be on CT date d.
- **CP2 (7 roots).**
  - Literals 15/4/75 and the F map. The buffer is 4 x tick per root: 1.00, 1.00, 1.00, 0.40, 0.04, 0.100, 0.100.
  - Breakouts fill at the next open with exit after 75 present bars, both directions.
  - The buffer exactly: a close at OR_high + 4 ticks buys and OR_high + 3 does not, the same below, for all seven roots.
    The prices equal OR + buffer in vendor units.
  - The first qualifying bar takes the day. One entry even when the engine refuses it: a trigger at the real D9.7 stop
    gives `price_limit_zone_no_entry` and the later trigger is unused. One tick inside, the entry is accepted.
  - One entry after the exit, none while pending. A missing bar in the hold moves the exit one bar. A pending exit is
    not sent twice (direct).
  - No C-2 exit: the 75th bar falls after C-2. No entry from C (13:15 / 13:00). The last eligible bar C-1 is held to the
    F flatten.
  - Synthetic F. No range bar gives no trade, and one range bar is enough. The range comes from present bars and is the
    max high / min low.
  - Grain evening and overnight bars are neither range nor eligible bars. The 08:45 bar is eligible, not a range bar.
    There is no instrument guard.
  - Real D9.7 exit with no duplicate exit or re-entry. Early halt: the engine flattens at 11:45.
  - State and range reset. Monday reads no Sunday bar. Livestock bars of CT date d-1 are ignored (direct).
- **CP3 (7 roots).**
  - Literals. CLV 0.8 buys, 0.2 sells, CLV in between (0.3, 0.5, 0.7) gives no trade, and CLV beyond the cuts trades.
  - Limit close (C = H, CLV 1) buys.
  - Exact cuts where a float CLV misses them: ZM 4/5 and 1/5, ZL 8/10 and 2/10, HE, LE. Direct `clv_side` cases
    include 80/100, 79/100, 20/100, 21/100, 799/1000, 201/1000 and zero range.
  - The daily low is the min low. Zero range gives no trade. Warm-up gives no trade. d-1 is used only once finalised.
  - The most recent complete day is read past incomplete days: a missing 08:30 bar, a missing C-1 bar, or two ids.
    Grain ids and wide bars outside [08:30, 13:15) do not count.
  - Instrument guard. A missing 08:30 bar gives no entry and an incomplete day.
  - Early halt 2025-12-24 on all 7 roots: untraded and incomplete, and 12-26 reads 12-23. A halt-labelled day with bars
    to C is still incomplete. Grain 2025-11-28 (late open and halt): 12-01 reads 11-26.
  - Tuesday after Memorial Day reads Friday. Monday reads Friday.
  - Missing C-2 bar: exit on C-1. No exit before C-2. Synthetic F.
  - Engine-level case (2), all 7 roots (`test_cp3_d97_real_stop_level_engine_exit_then_nothing_more`): d-1's settlement
    proxy is its C-1 close. A TUE close at the real upper stop closes the long at the next open (`price_limit_exit`).
    The member sends no C-2 exit and no entry afterwards. One tick inside, the normal trade. The next date trades again.
  - Daily-bar and entry bars must be on CT date d (direct). Once per date and not while pending. An 08:30 bar with
    early_halt_ct is not traded (direct).
  - Accumulators reset per date (added after the mutant run). The halt flag resets per date (added after the mutant run).
- **crushgap.**
  - Static check, the declaration (ZS traded, ZM and ZL signal), windows, and freeze/verify under tmp_path (with
    _port_common.py and _calendar.py).
  - Units 22/11/-25 derived from rules.products, factors 1/100/100, filter 200, and an off-grid weighted tick is refused.
  - Hand-computed GPM: 1.60 USD/bu = 16000 units at the base. A realistic case: ZM 290.3, ZL 52.17 cents, ZS 1012.25
    cents gives 2.0028 USD/bu = 20028 units.
  - Filter exactly at +200 and -200 trades; ±199 does not.
  - Every leg's coefficient: an exact-200 three-leg case, one tick less on each leg, and single-leg cases on both sides
    of 200.
  - G = open(d) - close(d-1): the 08:30 close and the 13:14 open are not read.
  - Engine-level case (1): fills only on ZS at 08:31 / 13:14, with position_after 1 then 0, all intents on ZS, no ZM or
    ZL fill.
  - Engine-level case (1), D11.5 for ZM and for ZL: the member sends nothing when the leg lacks the 08:30 bar. A
    test-only probe that sends the open anyway is refused with `engine_leg_missing_bar`.
  - d-1: Monday reads Friday. 2025-05-27 reads 2025-05-23. d-1 is the calendar date even when that date has no bars.
    The early-halt d-1 2025-11-28 gives no trade on 2025-12-01 (the 11-26 closes would have traded; the control trades).
  - Guard per leg: a missing 13:14 bar of d-1 on each leg, a missing 08:30 bar on each leg, and an id change on each leg
    (either side) each give no trade. Different ids across legs are accepted.
  - d = 2025-12-24 (not in GRAIN_FULL_SESSIONS) gives no intent. Late open 2026-01-02 (full session) trades.
  - Entry on the 08:30 ZS bar only: 08:31 is not an entry bar even with G = +200 there.
  - A missing 13:13 ZS bar moves the exit to 13:14. The exit needs a ZS bar.
  - One trade per date on consecutive days (WED sells). Synthetic F.
  - Direct calls: once per date and not while pending. The 13:14 bar must be on its trade date's CT date. Signal-leg
    closes are recorded on minutes without a ZS bar. The entry bar must be on CT date d. Intents go to ZS only.

## 5. Mutants

- **Method.** The script is
  /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/94d6572b-fdf2-4814-9116-60c2521d80a0/scratchpad/coderA/mutants.py.
  - Each mutant replaces one exact, unique source string in one of the five modules (a literal, a clock, a comparison,
    a guard or a reset). It then runs the four K6 test files with `PYTHONDONTWRITEBYTECODE=1` at nice 10 and restores the
    file in a `finally` block.
  - Results are in mutants.jsonl and the logs in the same folder. The sha256 of all five sources matched the pre-run
    values after both rounds.
- **Round 1 (00:40-01:14 PDT).** 158 mutants: 150 killed, 8 survived.
- **Tests added.** Three of the survivors were test gaps or an unpinned guard:
  - C3-30 (halt flag not reset on roll) and C3-34 (high/low not reset on roll): two CP3 tests added.
  - CG-38 (the integer guard disabled): a crushgap test added that calls `_exact_units` with an off-grid value.
- **Round 2 (01:24 PDT).** The three were rerun and all killed.
- **Final.** 158 mutants: 153 killed, 5 surviving, all equivalent:
  - **PC-05** (`if group not in (GRAINS, LIVESTOCK)` made false): unreachable. All seven K6 exposures are grains or
    livestock in rules.products, as the frozen-tables test pins.
  - **C1-20** (`s > 0` to `s >= 0`): s = 0 has already returned "no trade" on the line before.
  - **C2-13** (`self._triggered and position` to `position`): a non-zero position can only come from this member's own
    entry on the same trade date, and that sets `_triggered`. The engine flattens at F before the next trade date's
    first bar.
  - **C3-23** (`at == C-1` to `at >= C-1` for C_d): inside the [O, C) filter the only bar with at >= C-1 is the C-1 bar.
  - **CG-20** (`if prev is None: return None` removed): with prev None, the next check `last[0] != prev` is always true
    for a recorded date, and `last is None` returns anyway. The result is the same.
- **Killed only by a literal pin, not by a trade.** CG-09 scales the 0.0001 unit to 0.00001. Coefficients and filter
  scale together, so the trade decisions do not change; the unit-literal test kills it. C2-08 and C2-09 (the F window
  end) change only `trading_windows` and are killed by the S0.12 window test.
- **Crash kill.** CG-39 removes the missing-08:30 check on a signal leg. The member then raises (asdict on None) instead
  of returning "no trade", so the test fails on the exception.

Full table. "Failing tests" is the number of failing tests in the four K6 files. "First killer" is the first failing
test name pytest reported.

| Id | File | Mutation (old -> new) | Result | Failing tests | First killer |
|---|---|---|---|---|---|
| C1-01 | cp1.py | `MEMBER_ID = "K6-cp1-01"` -> `MEMBER_ID = "K6-cp1-02"` | killed | 2 | test_member_ids_are_the_catalog_ids |
| C1-02 | cp1.py | `GRAIN_EVENING_OPEN_CT = time(19, 0)` -> `GRAIN_EVENING_OPEN_CT = time(19, 1)` | killed | 15 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C1-03 | cp1.py | `GRAIN_EVENING_OPEN_CT = time(19, 0)` -> `GRAIN_EVENING_OPEN_CT = time(18, 59)` | killed | 10 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C1-04 | cp1.py | `SIGNAL_AFTER_O_MIN = 29` -> `SIGNAL_AFTER_O_MIN = 28` | killed | 105 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C1-05 | cp1.py | `SIGNAL_AFTER_O_MIN = 29` -> `SIGNAL_AFTER_O_MIN = 30` | killed | 105 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C1-06 | cp1.py | `ENTRY_BEFORE_C_MIN = 31` -> `ENTRY_BEFORE_C_MIN = 30` | killed | 117 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C1-07 | cp1.py | `ENTRY_BEFORE_C_MIN = 31` -> `ENTRY_BEFORE_C_MIN = 32` | killed | 117 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C1-08 | cp1.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 1` | killed | 70 | test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_2[ZC] |
| C1-09 | cp1.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 3` | killed | 75 | test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_2[ZC] |
| C1-10 | cp1.py | `ONE_DAY = timedelta(days=1)` -> `ONE_DAY = timedelta(days=2)` | killed | 5 | test_cp1_grain_first_bar_is_at_or_after_1900_of_the_calendar_day_before_... |
| C1-11 | cp1.py | `if self._first is not None: return False` -> `if False: return False` | killed | 35 | test_cp1_grain_monday_first_bar_is_sunday_1900_l01[ZC] |
| C1-12 | cp1.py | `return opened >= datetime.combine(` -> `return opened > datetime.combine(` | killed | 10 | test_cp1_grain_monday_first_bar_is_sunday_1900_l01[ZC] |
| C1-13 | cp1.py | `return opened.date() == day and opened.time()...` -> `return opened.time() == self._leg.o` | killed | 2 | test_cp1_livestock_first_bar_is_on_ct_date_d[HE] |
| C1-14 | cp1.py | `return opened.date() == day and opened.time()...` -> `return opened.date() == day and opened.time()...` | killed | 4 | test_cp1_livestock_first_bar_is_the_0830_bar_exactly_l02[HE] |
| C1-15 | cp1.py | `if self._leg.is_grain: return` -> `if not self._leg.is_grain: return` | killed | 50 | test_cp1_grain_monday_first_bar_is_sunday_1900_l01[ZC] |
| C1-16 | cp1.py | `shift(GRAIN_EVENING_OPEN_CT, 1), -1, -1)` -> `shift(GRAIN_EVENING_OPEN_CT, 1), 0, 0)` | killed | 5 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C1-17 | cp1.py | `first = TradingInterval(self._leg.o, shift(se...` -> `first = TradingInterval(self._leg.o, shift(se...` | killed | 2 | test_trading_windows_are_the_s0_12_intervals[HE] |
| C1-18 | cp1.py | `if first_id != signal_id: return None` -> `if False: return None` | killed | 7 | test_cp1_signal_bars_with_two_instrument_ids_are_no_trade[ZC] |
| C1-19 | cp1.py | `if s == 0: return None` -> `if False: return None` | killed | 7 | test_cp1_zero_signal_is_no_trade[ZC] |
| C1-20 | cp1.py | `return "buy" if s > 0 else "sell"` -> `return "buy" if s >= 0 else "sell"` | SURVIVED | 0 | - |
| C1-21 | cp1.py | `return "buy" if s > 0 else "sell"` -> `return "buy" if s < 0 else "sell"` | killed | 98 | test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_2[ZC] |
| C1-22 | cp1.py | `s = signal_close - first_open` -> `s = first_open - signal_close` | killed | 98 | test_cp1_buys_on_a_positive_signal_at_c_minus_31_and_exits_at_c_minus_2[ZC] |
| C1-23 | cp1.py | `if opened.date() != day: return () # the rest` -> `if False: return () # the rest` | killed | 2 | test_cp1_signal_and_entry_bars_are_bars_of_ct_date_d[ZS] |
| C1-24 | cp1.py | `if at == self._signal_at:` -> `if at >= self._signal_at and at < self._entry...` | killed | 70 | test_the_kit_adds_the_price_limit_reference_the_engine_needs |
| C1-25 | cp1.py | `if at != self._entry_at or self._entered` -> `if at < self._entry_at or self._entered` | killed | 7 | test_cp1_missing_entry_bar_is_no_trade[ZC] |
| C1-26 | cp1.py | `self._entered = True # the one entry` -> `pass # the one entry` | killed | 7 | test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[ZC] |
| C1-27 | cp1.py | `or self._entered or not is_flat(account, self...` -> `or self._entered:` | killed | 7 | test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[ZC] |
| C1-28 | cp1.py | `self._day, self._first, self._signal, self._e...` -> `self._day, self._first, self._signal, self._e...` | killed | 30 | test_cp1_grain_monday_first_bar_is_sunday_1900_l01[ZC] |
| C1-29 | cp1.py | `self._day, self._first, self._signal, self._e...` -> `self._day, self._first, self._signal, self._e...` | killed | 2 | test_cp1_trades_once_per_trade_date_and_state_resets[ZL] |
| C1-30 | cp1.py | `self._day, self._first, self._signal, self._e...` -> `self._day, self._first, self._signal, self._e...` | killed | 9 | test_cp1_grain_monday_first_bar_is_sunday_1900_l01[ZC] |
| C1-31 | cp1.py | `return (leg_market_intent(view, self.root, si...` -> `return (leg_market_intent(view, self.root, si...` | killed | 92 | test_the_kit_adds_the_price_limit_reference_the_engine_needs |
| C1-32 | cp1.py | `def make_zc() -> Cp1Momentum: return Cp1Momen...` -> `def make_zc() -> Cp1Momentum: return Cp1Momen...` | killed | 6 | test_factories_name_the_label_and_trade_one_leg[K6-cp1-01-ZC] |
| C1-33 | cp1.py | `TradingInterval(self._entry_at, self._leg.c),` -> `TradingInterval(self._entry_at, self._exit_at),` | killed | 7 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C2-01 | cp2.py | `MEMBER_ID = "K6-cp2-01"` -> `MEMBER_ID = "K6-cp2-1"` | killed | 1 | test_member_ids_are_the_catalog_ids |
| C2-02 | cp2.py | `RANGE_MINUTES = 15` -> `RANGE_MINUTES = 14` | killed | 9 | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] |
| C2-03 | cp2.py | `RANGE_MINUTES = 15` -> `RANGE_MINUTES = 16` | killed | 46 | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] |
| C2-04 | cp2.py | `BUFFER_TICKS = 4` -> `BUFFER_TICKS = 3` | killed | 14 | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] |
| C2-05 | cp2.py | `BUFFER_TICKS = 4` -> `BUFFER_TICKS = 5` | killed | 89 | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] |
| C2-06 | cp2.py | `HOLD_BARS = 75` -> `HOLD_BARS = 74` | killed | 74 | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] |
| C2-07 | cp2.py | `HOLD_BARS = 75` -> `HOLD_BARS = 76` | killed | 72 | test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06[ZC] |
| C2-08 | cp2.py | `GRAINS: time(13, 18)` -> `GRAINS: time(13, 17)` | killed | 13 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C2-09 | cp2.py | `LIVESTOCK: time(13, 3)` -> `LIVESTOCK: time(13, 4)` | killed | 10 | test_trading_windows_are_the_s0_12_intervals[HE] |
| C2-10 | cp2.py | `if self._held < HOLD_BARS or` -> `if self._held <= HOLD_BARS or` | killed | 65 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |
| C2-11 | cp2.py | `if self._held < HOLD_BARS or account.pending....` -> `if self._held < HOLD_BARS:` | killed | 2 | test_cp2_a_pending_exit_is_not_sent_twice[ZC] |
| C2-12 | cp2.py | `side = "sell" if position > 0 else "buy"` -> `side = "sell" if position < 0 else "buy"` | killed | 67 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |
| C2-13 | cp2.py | `if self._triggered and account.position(self....` -> `if account.position(self.root):` | SURVIVED | 0 | - |
| C2-14 | cp2.py | `if opened.date() != bar.trade_date: return ()` -> `if False: return ()` | killed | 2 | test_cp2_livestock_range_and_eligible_bars_are_bars_of_ct_date_d[HE] |
| C2-15 | cp2.py | `if self._leg.o <= at < self._range_end:` -> `if self._leg.o < at < self._range_end:` | killed | 1 | test_cp2_the_range_is_the_max_high_and_min_low |
| C2-16 | cp2.py | `if self._leg.o <= at < self._range_end:` -> `if self._leg.o <= at <= self._range_end:` | killed | 39 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |
| C2-17 | cp2.py | `self._hi = bar.high if self._hi is None else ...` -> `self._hi = bar.high if self._hi is None else ...` | killed | 17 | test_cp2_the_buffer_is_exactly_four_ticks_either_side[ZC] |
| C2-18 | cp2.py | `self._lo = bar.low if self._lo is None else m...` -> `self._lo = bar.low if self._lo is None else m...` | killed | 7 | test_cp2_the_buffer_is_exactly_four_ticks_either_side[ZC] |
| C2-19 | cp2.py | `if self._triggered or self._hi is None or sel...` -> `if self._hi is None or self._lo is None:` | killed | 15 | test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it[ZC] |
| C2-20 | cp2.py | `if self._triggered or self._hi is None or sel...` -> `if self._triggered:` | killed | 92 | test_the_kit_adds_the_price_limit_reference_the_engine_needs |
| C2-21 | cp2.py | `if not self._range_end <= at < self._leg.c or` -> `if not self._range_end <= at <= self._leg.c or` | killed | 7 | test_cp2_no_entry_from_c[ZC] |
| C2-22 | cp2.py | `if not self._range_end <= at < self._leg.c or` -> `if not self._range_end < at < self._leg.c or` | killed | 37 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |
| C2-23 | cp2.py | `self._leg.c or not is_flat(account, self.root):` -> `self._leg.c:` | killed | 2 | test_cp2_no_entry_while_an_order_is_pending[ZS] |
| C2-24 | cp2.py | `if close >= to_ticks(self._hi, self._leg.tick...` -> `if close > to_ticks(self._hi, self._leg.tick)...` | killed | 73 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |
| C2-25 | cp2.py | `elif close <= to_ticks(self._lo, self._leg.ti...` -> `elif close < to_ticks(self._lo, self._leg.tic...` | killed | 16 | test_cp2_breakout_down_sells[ZC] |
| C2-26 | cp2.py | `self._triggered = True # one entry` -> `pass # one entry` | killed | 74 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |
| C2-27 | cp2.py | `= day, None, None, False, 0` -> `= day, None, None, False, self._held` | killed | 2 | test_cp2_state_and_range_reset_each_trade_date[ZL] |
| C2-28 | cp2.py | `= day, None, None, False, 0` -> `= day, self._hi, self._lo, False, 0` | killed | 2 | test_cp2_state_and_range_reset_each_trade_date[ZL] |
| C2-29 | cp2.py | `TradingInterval(self._leg.o, F_REGULAR_CT[sel...` -> `TradingInterval(self._leg.o, self._leg.c)` | killed | 7 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| C2-30 | cp2.py | `return (leg_market_intent(view, self.root, si...` -> `return (leg_market_intent(view, self.root, si...` | killed | 85 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |
| C2-31 | cp2.py | `self._range_end = shift(self._leg.o, RANGE_MI...` -> `self._range_end = shift(self._leg.o, -RANGE_M...` | killed | 89 | test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars[ZC] |
| C3-01 | cp3.py | `MEMBER_ID = "K6-cp3-01"` -> `MEMBER_ID = "K6-cp3-1"` | killed | 2 | test_member_ids_are_the_catalog_ids |
| C3-02 | cp3.py | `CLV_BUY_AT_OR_ABOVE = Decimal("0.8")` -> `CLV_BUY_AT_OR_ABOVE = Decimal("0.79")` | killed | 3 | test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-03 | cp3.py | `CLV_BUY_AT_OR_ABOVE = Decimal("0.8")` -> `CLV_BUY_AT_OR_ABOVE = Decimal("0.81")` | killed | 95 | test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-04 | cp3.py | `CLV_SELL_AT_OR_BELOW = Decimal("0.2")` -> `CLV_SELL_AT_OR_BELOW = Decimal("0.19")` | killed | 25 | test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-05 | cp3.py | `CLV_SELL_AT_OR_BELOW = Decimal("0.2")` -> `CLV_SELL_AT_OR_BELOW = Decimal("0.21")` | killed | 3 | test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-06 | cp3.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 0` | killed | 117 | test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-07 | cp3.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 2` | killed | 119 | test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-08 | cp3.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 1` | killed | 92 | test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-09 | cp3.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 3` | killed | 99 | test_cp3_literals_are_the_clv_cuts_and_the_clock |
| C3-10 | cp3.py | `if span <= 0:` -> `if span < 0:` | killed | 8 | test_cp3_clv_cuts_are_compared_exactly[0-0-None] |
| C3-11 | cp3.py | `if num * buy_d >= buy_n * span:` -> `if num * buy_d > buy_n * span:` | killed | 94 | test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[ZC] |
| C3-12 | cp3.py | `if num * sell_d <= sell_n * span:` -> `if num * sell_d < sell_n * span:` | killed | 24 | test_cp3_prior_clv_at_02_sells[ZC] |
| C3-13 | cp3.py | `num = prior.close - prior.low` -> `num = prior.high - prior.close` | killed | 122 | test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[ZC] |
| C3-14 | cp3.py | `complete = (self._has_open_bar and self._clos...` -> `complete = (self._close is not None` | killed | 9 | test_cp3_d_minus_1_is_the_most_recent_complete_day[ZC] |
| C3-15 | cp3.py | `and not self._halt` -> `` | killed | 2 | test_cp3_a_halt_day_with_all_bars_to_c_is_still_incomplete[ZL] |
| C3-16 | cp3.py | `and len(self._ids) == 1)` -> `and len(self._ids) >= 1)` | killed | 7 | test_cp3_d_minus_1_is_the_most_recent_complete_day[ZC] |
| C3-17 | cp3.py | `if finished is not None: self._prior = finished` -> `if True: self._prior = finished` | killed | 23 | test_cp3_d_minus_1_is_the_most_recent_complete_day[ZC] |
| C3-18 | cp3.py | `if bar.early_halt_ct is not None: # any bar` -> `if False: # any bar` | killed | 2 | test_cp3_a_halt_day_with_all_bars_to_c_is_still_incomplete[ZL] |
| C3-19 | cp3.py | `if not self._leg.o <= at < self._leg.c: return` -> `if not self._leg.o <= at <= self._leg.c: return` | killed | 10 | test_cp3_grain_ids_outside_the_daily_window_do_not_make_it_incomplete[ZC] |
| C3-20 | cp3.py | `if not self._leg.o <= at < self._leg.c: return` -> `if not self._leg.o < at < self._leg.c: return` | killed | 116 | test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[ZC] |
| C3-21 | cp3.py | `self._hi = bar.high if self._hi is None else ...` -> `self._hi = bar.high if self._hi is None else ...` | killed | 114 | test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[ZC] |
| C3-22 | cp3.py | `self._lo = bar.low if self._lo is None else m...` -> `self._lo = bar.low if self._lo is None else m...` | killed | 2 | test_cp3_the_daily_low_is_the_min_low[-2-buy] |
| C3-23 | cp3.py | `if at == self._close_at: self._close = bar.close` -> `if at >= self._close_at: self._close = bar.close` | SURVIVED | 0 | - |
| C3-24 | cp3.py | `if bar.early_halt_ct is not None: return None...` -> `if False: return None # an early-halt day d` | killed | 16 | test_cp3_early_halt_day_is_not_traded_and_is_incomplete[ZC] |
| C3-25 | cp3.py | `if prior.instrument_id != bar.instrument_id:` -> `if False:` | killed | 14 | test_cp3_d_minus_1_is_the_most_recent_complete_day[ZC] |
| C3-26 | cp3.py | `return () # the grain evening of trade date d...` -> `pass # the grain evening of trade date d (CT ...` | killed | 7 | test_cp3_daily_bar_and_entry_bar_are_bars_of_ct_date_d[ZC] |
| C3-27 | cp3.py | `if at != self._leg.o or self._entered` -> `if at < self._leg.o or self._entered` | killed | 2 | test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete[ZM] |
| C3-28 | cp3.py | `self._entered = True # the one entry` -> `pass # the one entry` | killed | 7 | test_cp3_emits_at_most_one_entry_per_trade_date_and_none_while_pending[ZC] |
| C3-29 | cp3.py | `or self._entered or not is_flat(account, self...` -> `or self._entered:` | killed | 7 | test_cp3_emits_at_most_one_entry_per_trade_date_and_none_while_pending[ZC] |
| C3-30 | cp3.py | `self._day, self._halt, self._has_open_bar, se...` -> `self._day, self._halt, self._has_open_bar, se...` | killed | 2 | test_cp3_the_halt_flag_resets_on_the_next_trade_date[ZS] |
| C3-31 | cp3.py | `self._hi, self._lo, self._close, self._ids = ...` -> `self._hi, self._lo, self._close, self._ids = ...` | killed | 7 | test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar[ZC] |
| C3-32 | cp3.py | `if at == self._leg.o: self._has_open_bar = True` -> `if at >= self._leg.o: self._has_open_bar = True` | killed | 9 | test_cp3_d_minus_1_is_the_most_recent_complete_day[ZC] |
| C3-33 | cp3.py | `return (leg_market_intent(view, self.root, si...` -> `return (leg_market_intent(view, self.root, si...` | killed | 107 | test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_c_minus_2[ZC] |
| C3-34 | cp3.py | `self._hi, self._lo, self._close, self._ids = ...` -> `self._hi, self._lo, self._close, self._ids = ...` | killed | 2 | test_cp3_day_accumulators_reset_each_trade_date[ZC] |
| CG-01 | crushgap.py | `MEMBER_ID = "K6-crushgap-01"` -> `MEMBER_ID = "K6-crushgap-1"` | killed | 1 | test_crushgap_declaration_is_zs_traded_zm_zl_signal |
| CG-02 | crushgap.py | `GPM_WEIGHTS = {"ZM": Decimal("0.022")` -> `GPM_WEIGHTS = {"ZM": Decimal("0.023")` | killed | 11 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-03 | crushgap.py | `GPM_WEIGHTS = {"ZM": Decimal("0.022")` -> `GPM_WEIGHTS = {"ZM": Decimal("0.021")` | killed | 12 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-04 | crushgap.py | `"ZL": Decimal("11"), "ZS"` -> `"ZL": Decimal("12"), "ZS"` | killed | 10 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-05 | crushgap.py | `"ZL": Decimal("11"), "ZS"` -> `"ZL": Decimal("10"), "ZS"` | killed | 11 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-06 | crushgap.py | `"ZS": Decimal("-1")}` -> `"ZS": Decimal("-0.96")}` | killed | 24 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-07 | crushgap.py | `"ZS": Decimal("-1")}` -> `"ZS": Decimal("-1.04")}` | killed | 11 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-08 | crushgap.py | `"ZS": Decimal("-1")}` -> `"ZS": Decimal("1")}` | killed | 25 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-09 | crushgap.py | `GPM_UNIT_USD_PER_BU = Decimal("0.0001")` -> `GPM_UNIT_USD_PER_BU = Decimal("0.00001")` | killed | 16 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-10 | crushgap.py | `FILTER_USD_PER_BU = Decimal("0.02")` -> `FILTER_USD_PER_BU = Decimal("0.0201")` | killed | 19 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-11 | crushgap.py | `FILTER_USD_PER_BU = Decimal("0.02")` -> `FILTER_USD_PER_BU = Decimal("0.0199")` | killed | 2 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-12 | crushgap.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 2` | killed | 12 | test_crushgap_trading_windows_are_the_s0_12_intervals |
| CG-13 | crushgap.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 0` | killed | 12 | test_crushgap_trading_windows_are_the_s0_12_intervals |
| CG-14 | crushgap.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 1` | killed | 20 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-15 | crushgap.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 3` | killed | 20 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-16 | crushgap.py | `usd = GPM_WEIGHTS[root] * p.vendor_tick / Dec...` -> `usd = GPM_WEIGHTS[root] * p.vendor_tick` | killed | 14 | test_gpm_units_are_derived_from_rules_products_and_the_weights |
| CG-17 | crushgap.py | `if opened.date() == bar.trade_date and opened...` -> `if opened.time() == self._close_at[r]:` | killed | 1 | test_direct_the_1314_bar_must_be_on_its_trade_dates_ct_date |
| CG-18 | crushgap.py | `if opened.date() == bar.trade_date and opened...` -> `if opened.date() == bar.trade_date and opened...` | killed | 7 | test_g_is_open_of_d_minus_close_of_d_minus_1 |
| CG-19 | crushgap.py | `if day not in GRAIN_FULL_SESSIONS:` -> `if False:` | killed | 1 | test_d_not_in_grain_full_sessions_is_no_trade |
| CG-20 | crushgap.py | `if prev is None: return None # K6-L-04` -> `if False: return None # K6-L-04` | SURVIVED | 0 | - |
| CG-21 | crushgap.py | `if last is None or last[0] != prev:` -> `if last is None:` | killed | 2 | test_d_minus_1_is_the_calendar_date_not_the_last_date_with_bars |
| CG-22 | crushgap.py | `if close_id != bar.instrument_id:` -> `if False:` | killed | 3 | test_an_instrument_change_on_any_leg_is_no_trade[ZS] |
| CG-23 | crushgap.py | `if g_units >= FILTER_UNITS:` -> `if g_units > FILTER_UNITS:` | killed | 16 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-24 | crushgap.py | `if g_units <= -FILTER_UNITS:` -> `if g_units < -FILTER_UNITS:` | killed | 4 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-25 | crushgap.py | `if g_units >= FILTER_UNITS: return "buy"` -> `if g_units >= FILTER_UNITS: return "sell"` | killed | 20 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-26 | crushgap.py | `g_units += self._units[r] * (_open_ticks(bar,...` -> `g_units += self._units[r] * (close - _open_ti...` | killed | 24 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-27 | crushgap.py | `if opened.date() != day or opened.time() != z...` -> `if opened.time() != zs.o:` | killed | 1 | test_direct_the_entry_bar_is_the_0830_bar_of_ct_date_d |
| CG-28 | crushgap.py | `if opened.date() != day or opened.time() != z...` -> `if opened.date() != day or opened.time() < zs.o:` | killed | 1 | test_the_entry_is_the_0830_zs_bar_only |
| CG-29 | crushgap.py | `self._entered = True # the one entry` -> `pass # the one entry` | killed | 1 | test_direct_one_entry_per_trade_date_and_none_while_pending |
| CG-30 | crushgap.py | `if self._entered or not is_flat(account, TRAD...` -> `if self._entered:` | killed | 1 | test_direct_one_entry_per_trade_date_and_none_while_pending |
| CG-31 | crushgap.py | `self._day, self._entered = bar.trade_date, False` -> `self._day, self._entered = bar.trade_date, se...` | killed | 19 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-32 | crushgap.py | `windows = {TRADED: (TradingInterval(zs.o, zs....` -> `windows = {TRADED: (TradingInterval(zs.o, sel...` | killed | 1 | test_crushgap_trading_windows_are_the_s0_12_intervals |
| CG-33 | crushgap.py | `windows[r] = (TradingInterval(f.o, shift(f.o,...` -> `windows[r] = (TradingInterval(f.o, shift(f.o,...` | killed | 1 | test_crushgap_trading_windows_are_the_s0_12_intervals |
| CG-34 | crushgap.py | `TradingInterval(self._close_at[r], f.c))` -> `TradingInterval(self._exit_at, f.c))` | killed | 1 | test_crushgap_trading_windows_are_the_s0_12_intervals |
| CG-35 | crushgap.py | `(LegSpec(TRADED, True), *(LegSpec(r, False) f...` -> `(LegSpec(TRADED, True), *(LegSpec(r, True) fo...` | killed | 1 | test_crushgap_declaration_is_zs_traded_zm_zl_signal |
| CG-36 | crushgap.py | `if self.root != TRADED: raise` -> `if False: raise` | killed | 1 | test_crushgap_declaration_is_zs_traded_zm_zl_signal |
| CG-37 | crushgap.py | `return (leg_market_intent(view, TRADED, side,...` -> `return (leg_market_intent(view, TRADED, side,...` | killed | 22 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-38 | crushgap.py | `if units != units.to_integral_value():` -> `if False:` | killed | 1 | test_a_weighted_tick_off_the_unit_grid_is_refused |
| CG-39 | crushgap.py | `if bar is None: return None # K6-L-05: a miss...` -> `if False: return None # K6-L-05: a missing 08:30` | killed | 4 | test_engine_refuses_the_open_when_a_signal_leg_lacks_the_0830_bar_d11_5[ZM] |
| CG-40 | crushgap.py | `if g_units <= -FILTER_UNITS: return "sell"` -> `if g_units <= -FILTER_UNITS: return "buy"` | killed | 6 | test_the_filter_exactly_at_plus_and_minus_002_trades |
| CG-41 | crushgap.py | `SIGNAL_LEGS: tuple[str, ...] = ("ZM", "ZL")` -> `SIGNAL_LEGS: tuple[str, ...] = ("ZL", "ZM")` | killed | 2 | test_crushgap_declaration_is_zs_traded_zm_zl_signal |
| PC-01 | _port_common.py | `("ZC", "ZW", "ZS", "ZM", "ZL", "HE", "LE")` -> `("ZC", "ZW", "ZS", "ZM", "ZL", "HE")` | killed | 75 | test_factories_name_the_label_and_trade_one_leg[K6-cp1-01-ZC] |
| PC-02 | _port_common.py | `GRAINS = "grains"` -> `GRAINS = "grain"` | killed | 347 | test_factories_name_the_label_and_trade_one_leg[K6-cp1-01-ZC] |
| PC-03 | _port_common.py | `LIVESTOCK = "livestock"` -> `LIVESTOCK = "livestocks"` | killed | 126 | test_factories_name_the_label_and_trade_one_leg[K6-cp1-01-HE] |
| PC-04 | _port_common.py | `if root not in EXPOSURES:` -> `if root in EXPOSURES:` | killed | 455 | test_factories_name_the_label_and_trade_one_leg[K6-cp1-01-ZC] |
| PC-05 | _port_common.py | `if group not in (GRAINS, LIVESTOCK):` -> `if False:` | SURVIVED | 0 | - |
| PC-06 | _port_common.py | `o, c = tables.day_session_ct[root]` -> `c, o = tables.day_session_ct[root]` | killed | 348 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| PC-07 | _port_common.py | `tables.vehicles[root].q_c, product` -> `tables.vehicles[root].q_c + 1, product` | killed | 313 | test_frozen_clock_size_and_tick_per_root[ZC] |
| PC-08 | _port_common.py | `q_c, product(root).vendor_tick)` -> `q_c, product(root).vendor_tick * 2)` | killed | 160 | test_frozen_clock_size_and_tick_per_root[ZC] |
| PC-09 | _port_common.py | `return f"{member_id} {root}"` -> `return f"{member_id}-{root}"` | killed | 22 | test_factories_name_the_label_and_trade_one_leg[K6-cp1-01-ZC] |
| PC-10 | _port_common.py | `+ timedelta(minutes=minutes)` -> `- timedelta(minutes=minutes)` | killed | 347 | test_trading_windows_are_the_s0_12_intervals[ZC] |
| PC-11 | _port_common.py | `tz=UTC).astimezone(CT)` -> `tz=UTC).astimezone(UTC)` | killed | 333 | test_the_kit_adds_the_price_limit_reference_the_engine_needs |
| PC-12 | _port_common.py | `return round(Decimal(repr(price)) / tick)` -> `return int(Decimal(repr(price)) / tick)` | killed | 7 | test_prices_become_integer_vendor_ticks[ZC] |
| PC-13 | _port_common.py | `return account.position(root) == 0 and not ac...` -> `return account.position(root) == 0` | killed | 17 | test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending[ZC] |
| PC-14 | _port_common.py | `if position == 0 or account.pending.get(root,...` -> `if position == 0:` | killed | 1 | test_an_exit_is_not_sent_while_an_order_is_pending |
| PC-15 | _port_common.py | `if opened.date() != day or opened.time() < ex...` -> `if opened.time() < exit_at:` | killed | 1 | test_an_exit_is_not_sent_while_an_order_is_pending |
| PC-16 | _port_common.py | `if opened.date() != day or opened.time() < ex...` -> `if opened.date() != day or opened.time() <= e...` | killed | 182 | test_an_exit_is_not_sent_while_an_order_is_pending |
| PC-17 | _port_common.py | `side = "sell" if position > 0 else "buy"` -> `side = "sell" if position < 0 else "buy"` | killed | 197 | test_an_exit_is_not_sent_while_an_order_is_pending |
| PC-18 | _port_common.py | `return (leg_market_intent(view, root, side, a...` -> `return (leg_market_intent(view, root, side, 1),)` | killed | 1 | test_an_exit_is_not_sent_while_an_order_is_pending |
| PC-19 | _port_common.py | `return self.group == GRAINS` -> `return self.group != GRAINS` | killed | 64 | test_trading_windows_are_the_s0_12_intervals[ZC] |

C3-30, C3-34 and CG-38 show their round-2 result (killed). Their round-1 rows (survived) are in mutants_round1.jsonl.

## 6. Command lines and results

- Tests, as the brief prescribes (PYTHONPYCACHEPREFIX unset), final run 01:25 PDT:
  `env -u PYTHONPYCACHEPREFIX uv run pytest -q tests/test_k6_members_ports.py tests/test_k6_members_ports_cp2.py tests/test_k6_members_ports_cp3.py tests/test_k6_members_crushgap.py tests/test_stage_e_template.py tests/test_stage_e_freeze.py`.
  Result: **566 passed** in 10.6 s. Of these, 519 are in the four K6 files: 188 + 111 + 169 + 51.
- Freeze static check:
  `PYTHONPYCACHEPREFIX=<scratch>/coderA/pyc uv run python -c "... check_member_source(rel, text, 'K6') ..."` on
  _port_common.py, cp1.py, cp2.py, cp3.py and crushgap.py. Result: `[]` for each. The tests also run it, and freeze and
  verify the declarations under tmp_path.
- Lint: `uv run ruff check <the 5 modules and 4 test files>`. Result: all checks passed (four SIM300 test-assertion
  forms were rewritten).
- Mutants: `nice -n 10 python3 <scratch>/coderA/mutants.py` (round 1, 158 mutants) and the same with
  `C3-30 C3-34 CG-38` (round 2). Results are in section 5. Source sha256 was verified unchanged afterwards.
- Not run: the full suite (the lead runs it) and the cluster freeze over the real strategy/members/k6 directory
  (coder B's files are still in progress there; the tmp_path freezes cover my files).

## 7. Questions raised

None blocked the work. Section 3 item 1 flags the one reading consequence the lead may want to confirm: on a grain
late-open date whose 08:30 bar is missing, the CP1 first bar is the next bar. Item 2 is a harness-side observation for
the lead's record.
