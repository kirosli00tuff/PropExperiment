# Stage E.6 Task 2, coder A: the K7 core ports (K7-cp1-01, K7-cp2-01, K7-cp3-01)

MemberCoder-A-OpusXHigh (worker-xhigh on opus), 2026-09-27, 21:37-22:15 PDT. Brief:
reports/stage_e6_briefs/2A_member_coder_A.md. Governing text: reports/stage_e6_member_specs.md
header, section 0, sections 1-3 and section 8 (readings E.3-L-03..-22, K4-L-06, K7-L-01).
Precedent adapted (never imported): strategy/members/k4/{_port_common,cp1,cp2,cp3}.py and
tests/test_e4_k4_members_a.py. No bar file was opened, no bar loader or runner was called, no
harness file was changed, nothing was committed, and no worker was spawned.

## 1. Files

| File | What it is |
|---|---|
| strategy/members/k7/_port_common.py | Shared plumbing: `leg_facts` (O 08:30 and C 15:00 from `load_frozen_tables().day_session_ct["MBT"]`, q_c 1 from the vehicle table, vendor tick 5.00 from `rules.products`), `label`, `shift`, `ct_open` (bar open in CT), `to_ticks` (round(price / tick) in Decimal), `is_flat`, `exit_if_due` (S0.7 exit on a present bar of CT date d at or after the named bar, resent while refused, never while pending). `EXPOSURES = ("MBT",)`. |
| strategy/members/k7/cp1.py | `Cp1Momentum`, `make_mbt`. Section 1. |
| strategy/members/k7/cp2.py | `Cp2Breakout`, `make_mbt`. Section 2. |
| strategy/members/k7/cp3.py | `Cp3CloseLocation`, `DailyBar`, `clv_side`, `make_mbt`. Section 3. |
| tests/test_k7_members_ports.py | The synthetic kit (with `Segment` for bars of trade date d on other CT dates: weekend bars and a booked-forward holiday's session), the calendar-fact anchor, declarations, helpers, K7-cp1-01. |
| tests/test_k7_members_ports_cp2.py | K7-cp2-01. |
| tests/test_k7_members_ports_cp3.py | K7-cp3-01. |

No other file was added. strategy/members/k7/__init__.py was not written (0 bytes, checked). Coder
B's files (_calendar.py, _event_common.py, expiry.py, rev2h.py, montrend.py) were not touched and
are not imported by anything here.

How K7-L-01 is implemented: every member identifies a bar by `ct_open(bar).date()` and its clock.
CP1 records its first bar only when the bar opens at 17:00 on CT date `trade_date - 1 day`, and
reads its signal and entry bars only on CT date d. CP2 and CP3 return at once for any bar whose
CT date is not its trade date, so weekend bars (Friday 16:02 to Sunday 16:59 CT, carrying Monday's
trade date from 2026-06-01) and a booked-forward holiday's session (carrying the next trade date)
never enter a range, a daily bar, a signal or an entry. State resets when `bar.trade_date`
changes, so a trade date that spans two or three CT dates keeps one state. The exit helper also
requires CT date d.

Declarations the lead will freeze (S0.2): `MemberDecl("K7-cp1-01 MBT", 1, "strategy.members.k7.cp1",
"make_mbt", (LegSpec("MBT", True),))`, and the same for cp2 (ordinal 2) and cp3 (ordinal 3). The
tmp_path freeze test writes and verifies exactly these three with the four coder-A files.

## 2. What each test pins

Synthetic MBT bars at a base of 100000.00 (20000 ticks), run through the real Stage E engine
(`screening.stage_e_engine.run_engine` under `StageERules` from the canary kit's `rules_for`),
plus direct `on_minute` calls where the engine cannot reach a case. Real calendar dates are used
and anchored by `test_the_synthetic_scenarios_are_ec_cal_facts`: regular dates 2025-05-30,
06-02..06-04 (before 2026-05-29); 2026-06-05, 06-08, 06-09 (weekend booked to Monday); booked-forward
Monday 2026-01-19 (session booked to 2026-01-20; 01-16, 01-20, 01-21 regular); early halt
2025-07-04 (12:00 CT, engine F 11:30).

tests/test_k7_members_ports.py (39 cases; cp2 file 33; cp3 file 47; 119 in all):
- Calendar facts: every scenario date is what EC-CAL and rules.sessions say it is.
- Declarations: the static freeze check on the four files; label = name = "<id> MBT"; one traded
  leg MBT; fresh object per factory call; no MET factory; catalog member ids; S0.12 trading
  windows exactly; frozen O 08:30, C 15:00, q_c 1, tick 5.00; `leg_facts` refuses MET and MES;
  the three declarations freeze and verify under tmp_path with ordinals 1-3.
- Helpers: integer ticks (and round-half-even off grid), `shift`, a None bar changes no state,
  `exit_if_due` (not while pending, not when flat, side and quantity, from the named minute on,
  only on CT date d).
- CP1: buy 14:29 -> 14:30 fill, exit 14:58 -> 14:59, q 1; sell; one tick either side of zero;
  zero signal no trade; missing 17:00 first bar (17:01 present) no trade; missing 08:59 bar
  (08:58 and 09:00 present) no trade; instrument guard on the two signal bars, entry bar not
  guarded; missing 14:29 bar no trade; missing 14:58 bar exits on 14:59; no exit before 14:58;
  refused exit resent; synthetic F flatten; engine D9.7 exit with no duplicate or re-entry;
  early-halt day emitted and refused by the engine (port); one trade per trade date on
  consecutive days; state reset; Monday before 2026-05-29 opens Sunday 17:00 (its open decides
  the sign); Monday from 2026-06-01 with 183 weekend bars that would flip the signal or take the
  entry if read (only Monday's bars are used); the Sunday 17:00 open decides and without it there
  is no trade (the Friday 17:00 bar, same trade date, is not the first bar); after the
  booked-forward Monday the first bar is Monday 17:00 (the Sunday 17:00 bar of the same trade date
  would flip the sign, and the holiday's 08:59 and 14:29 bars are not read), and without the
  Monday 17:00 bar there is no trade; direct calls: one entry per trade date and none while an
  order is pending.

tests/test_k7_members_ports_cp2.py:
- Literals OR 15, buffer 4 ticks = 20.00, hold 75. Breakout 08:45 -> 08:46 fill, exit on the
  75th present bar 10:00 -> 10:01, q 1; sell side; buffer exactly 4 ticks (3 ticks no entry, the
  4-tick tie enters) both sides; in prices, OR_high 100010.00 with close 100030.00 enters and
  100025.00 does not; a 19.99-beyond close is off the 5.00 grid and the engine refuses the frame
  (EngineInvariantError) before any member call (section 5, item 1).
- Hold count: a missing bar in the hold moves the exit one bar; a deferred exit (release at the
  exit fill) is not sent twice; a deferred entry fill starts the count at the fill; no C-2 exit;
  the 14:59 trigger fills 15:00 and is flattened at F 15:08; a 13:52 fill exits on its own 75th
  bar at 15:07, a 13:53 fill meets F first (spec: F binds after 13:53).
- Range and eligibility: the 08:30 bar is a range bar; the 08:45 bar is eligible, not a range bar;
  bars before O and the evening are not range bars; no range bar no trade; one range bar is
  enough; range from present bars (high and low sides); max high and min low; no entry from
  15:00; no instrument guard.
- One entry: the first qualifying bar takes the day even when the engine refuses it; no second
  entry after the exit; the first qualifying bar decides the side; none while pending (direct).
- Engine interplay: synthetic F; D9.7 exit; FOMC 13:00 fill moved to 13:02; early-halt day trades
  and is flattened at F 11:30; state reset per trade date.
- State: the range resets each trade date (a previous day's wider range is not carried, and a day
  without its own range bar does not use the previous one).
- K7-L-01: Monday from 2026-06-01 with weekend bars that would widen the range and trigger; the
  trade date after the booked-forward Monday, whose holiday bars would widen the range and
  trigger a fill the engine accepts (holiday F 11:45) if read.

tests/test_k7_members_ports_cp3.py:
- Literals 0.8, 0.2, C-1, C-2. CLV 0.8 exactly buys on the 08:30 bar (08:31 fill), exit 14:58
  (14:59 fill), q 1, warm-up day no trade; CLV 0.2 exactly sells; 0.3, 0.5, 0.7 no trade;
  1.0, 0.9 buy, 0.1, 0.0 sell; the daily low is the min low (H B+10, L B-10: 0.8 buys, 0.2
  sells); `clv_side` exact integer cuts including span 0 and negative; range 0 no trade (only
  extreme bars at 08:29 and 15:00, outside [08:30, 15:00), which never enter a daily bar).
- Complete days (Family H): warm-up (none, or only incomplete earlier days) no trade; d-1 used
  only after it is finalised; the most recent complete day (a day without its 14:59 bar is
  dropped); two instrument_ids in [08:30, 15:00) make the day incomplete, other ids outside that
  window do not; missing 08:30 bar: no trade that day and the day is incomplete; early-halt day
  (2025-07-04, bars kept to 15:12) not traded although the engine would accept, and not a d-1
  (07-07 uses 07-03); a halt day with a buy prior is still not traded.
- State: the day accumulators (range) and the halt flag reset each trade date.
- Guard: d-1's instrument_id against the 08:30 bar only (the evening and 08:29 bars do not count;
  a later differing bar cannot be built while a position is held, the engine refuses a splice).
- Exit and engine: missing 14:58 exits on 14:59; D9.5a deferral of the entry fill; synthetic F;
  D9.7; one entry per trade date and none while pending (direct calls).
- K7-L-01: Monday before 2026-05-29 uses Friday's bar; Monday from 2026-06-01 reads no weekend
  bar (weekend 08:30 bars not entry bars, weekend extremes not in Monday's daily bar, checked
  through Tuesday's trade); after the booked-forward Monday, d-1 is the Friday, the holiday's bars
  are neither an entry bar (the engine would accept one) nor part of Tuesday's daily bar (checked
  through Wednesday's trade); the holiday session is never a daily bar of its own (Tuesday uses
  Thursday when Friday is incomplete).

## 3. Mutants

Method: `/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0f52aad4-207e-43da-84df-b6a0ead28371/scratchpad/mutants.py` (scratch, not in the repository) applies each mutant to an
isolated copy of the code tree (`/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0f52aad4-207e-43da-84df-b6a0ead28371/scratchpad/mut_repo`: rules, screening, sim, strategy,
tests, reports, data code and calendars; no bar data, no sealed store), runs the three port test
files there with `PYTHONDONTWRITEBYTECODE=1` (no stale bytecode), records every failing test,
restores the original bytes and asserts the copy's files equal the originals at the end. The
repository's member files were never mutated (coder B shares the package directory). Final run
22:03-22:13 PDT against the final test files: 153 mutants, 150 killed, 3 survived. A first run
(21:53-22:03) left 7 survivors; four were real gaps and were closed by new tests
(C2-40 -> test_cp2_the_range_resets_each_trade_date; C3-25 -> test_cp3_the_daily_low_is_the_min_low;
C3-44 -> test_cp3_the_halt_flag_resets_each_trade_date; C3-45 ->
test_cp3_day_accumulators_reset_each_trade_date), then everything was rerun.

The three survivors are equivalent mutants (no input can tell them apart from the original):
- PC-03 `_ANCHOR_DAY` 2000-01-03 -> 2000-01-04: the anchor is any date for time-of-day arithmetic
  (`shift`); no clock used (08:30 +/- 31 min, 15:00 - 31 min, 17:00 + 1 min) crosses midnight.
- C2-16 `self._triggered and account.position(...)` -> `account.position(...)`: the member's leg
  holds a position only after its own entry, and `_triggered` is set on the entry bar before any
  fill, so the two conditions agree on every reachable state (kept from the audited K4 code).
- C3-27 `at == self._close_at` -> `at >= self._close_at`: `_accumulate` returns first for any bar
  at or after C = 15:00, so 14:59 is the only bar that can satisfy either form.

Literal mutants that were chosen not to be run: the per-bar `volume` and `raw_symbol` fields are not
read; `ct_open`'s `//` (bars open on whole seconds); `CT = ZoneInfo("America/Chicago")` is covered
through PC-07 (UTC instead of CT).

Legend: file prefix main = tests/test_k7_members_ports.py, cp2 = ..._cp2.py, cp3 = ..._cp3.py.
Only the first three killing tests are named; the count is the number of failing cases.

| Id | File | Change | Result | Killing tests (count; first 3) |
|---|---|---|---|---|
| PC-01 | _port_common.py | `EXPOSURES: tuple[str, ...] = ("MBT",)` -> `EXPOSURES: tuple[str, ...] = ("MET",)` | killed | 93: main:test_factories_name_the_label_and_trade_one_leg[K7-cp1-01]; main:test_factories_name_the_label_and_trade_one_leg[K7-cp2-01]; main:test_factories_name_the_label_and_trade_one_leg[K7-cp3-01] |
| PC-02 | _port_common.py | `NS_PER_S = 1_000_000_000` -> `NS_PER_S = 1_000_000` | killed | 85: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| PC-03 | _port_common.py | `_ANCHOR_DAY = date(2000, 1, 3)` -> `_ANCHOR_DAY = date(2000, 1, 4)` | SURVIVED | 119 passed in 3.77s |
| PC-04 | _port_common.py | `if root not in EXPOSURES:` -> `if root in EXPOSURES:` | killed | 93: main:test_factories_name_the_label_and_trade_one_leg[K7-cp1-01]; main:test_factories_name_the_label_and_trade_one_leg[K7-cp2-01]; main:test_factories_name_the_label_and_trade_one_leg[K7-cp3-01] |
| PC-05 | _port_common.py | `return f"{member_id} {root}"` -> `return f"{member_id}-{root}"` | killed | 3: main:test_factories_name_the_label_and_trade_one_leg[K7-cp1-01]; main:test_factories_name_the_label_and_trade_one_leg[K7-cp2-01]; main:test_factories_name_the_label_and_trade_one_leg[K7-cp3-01] |
| PC-06 | _port_common.py | `+ timedelta(minutes=minutes)).time()` -> `- timedelta(minutes=minutes)).time()` | killed | 74: main:test_trading_windows_are_the_s0_12_intervals; main:test_shift_moves_a_clock_time; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459 |
| PC-07 | _port_common.py | `tz=UTC).astimezone(CT)` -> `tz=UTC).astimezone(UTC)` | killed | 72: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| PC-08 | _port_common.py | `return round(Decimal(repr(price)) / tick)` -> `return int(Decimal(repr(price)) / tick)` | killed | 1: main:test_prices_become_integer_vendor_ticks |
| PC-09 | _port_common.py | `return account.position(root) == 0 and` -> `return account.position(root) != 0 and` | killed | 72: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| PC-10 | _port_common.py | `and not account.pending.get(root, 0)` -> `and account.pending.get(root, 0) == 0 or True` | killed | 3: main:test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending; cp2:test_cp2_no_entry_while_an_order_is_pending; cp3:test_cp3_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| PC-11 | _port_common.py | `if position == 0 or account.pending.get(root, 0):` -> `if position != 0 or account.pending.get(root, 0):` | killed | 38: main:test_an_exit_is_not_sent_while_an_order_is_pending; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| PC-12 | _port_common.py | `if position == 0 or account.pending.get(root, 0):` -> `if position == 0 and account.pending.get(root, 0):` | killed | 1: main:test_an_exit_is_not_sent_while_an_order_is_pending |
| PC-13 | _port_common.py | `if position == 0 or account.pending.get(root, 0):` -> `if position == 0:` | killed | 1: main:test_an_exit_is_not_sent_while_an_order_is_pending |
| PC-14 | _port_common.py | `if opened.date() != day or opened.time() < exit_at:` -> `if opened.date() == day or opened.time() < exit_at:` | killed | 38: main:test_an_exit_is_not_sent_while_an_order_is_pending; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| PC-15 | _port_common.py | `if opened.date() != day or opened.time() < exit_at:` -> `if opened.time() < exit_at:` | killed | 1: main:test_an_exit_is_not_sent_while_an_order_is_pending |
| PC-16 | _port_common.py | `if opened.date() != day or opened.time() < exit_at:` -> `if opened.date() != day or opened.time() <= exit_at:` | killed | 36: main:test_an_exit_is_not_sent_while_an_order_is_pending; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| PC-17 | _port_common.py | `if opened.date() != day or opened.time() < exit_at:` -> `if opened.date() != day or opened.time() > exit_at:` | killed | 42: main:test_an_exit_is_not_sent_while_an_order_is_pending; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| PC-18 | _port_common.py | `side = "sell" if position > 0 else "buy"` -> `side = "sell" if position < 0 else "buy"` | killed | 38: main:test_an_exit_is_not_sent_while_an_order_is_pending; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| PC-19 | _port_common.py | `leg_market_intent(view, root, side, abs(position))` -> `leg_market_intent(view, root, side, position)` | killed | 15: main:test_an_exit_is_not_sent_while_an_order_is_pending; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-01 | cp1.py | `GLOBEX_OPEN_CT = time(17, 0)` -> `GLOBEX_OPEN_CT = time(17, 1)` | killed | 6: main:test_trading_windows_are_the_s0_12_intervals; main:test_cp1_missing_first_bar_is_no_trade_l05; main:test_cp1_monday_before_2026_05_29_opens_sunday_1700 |
| C1-02 | cp1.py | `GLOBEX_OPEN_CT = time(17, 0)` -> `GLOBEX_OPEN_CT = time(16, 59)` | killed | 19: main:test_trading_windows_are_the_s0_12_intervals; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| C1-03 | cp1.py | `SIGNAL_AFTER_O_MIN = 29` -> `SIGNAL_AFTER_O_MIN = 28` | killed | 17: main:test_trading_windows_are_the_s0_12_intervals; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| C1-04 | cp1.py | `SIGNAL_AFTER_O_MIN = 29` -> `SIGNAL_AFTER_O_MIN = 30` | killed | 17: main:test_trading_windows_are_the_s0_12_intervals; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| C1-05 | cp1.py | `ENTRY_BEFORE_C_MIN = 31` -> `ENTRY_BEFORE_C_MIN = 30` | killed | 20: main:test_trading_windows_are_the_s0_12_intervals; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| C1-06 | cp1.py | `ENTRY_BEFORE_C_MIN = 31` -> `ENTRY_BEFORE_C_MIN = 32` | killed | 20: main:test_trading_windows_are_the_s0_12_intervals; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| C1-07 | cp1.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 1` | killed | 13: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-08 | cp1.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 3` | killed | 13: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-09 | cp1.py | `ONE_DAY = timedelta(days=1)` -> `ONE_DAY = timedelta(days=2)` | killed | 18: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-10 | cp1.py | `ONE_DAY = timedelta(days=1)` -> `ONE_DAY = timedelta(days=0)` | killed | 18: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-11 | cp1.py | `TradingInterval(GLOBEX_OPEN_CT, shift(GLOBEX_OPEN_CT, 1), -1, -1)` -> `TradingInterval(GLOBEX_OPEN_CT, shift(GLOBEX_OPEN_CT, 2), -1, -1)` | killed | 1: main:test_trading_windows_are_the_s0_12_intervals |
| C1-12 | cp1.py | `TradingInterval(GLOBEX_OPEN_CT, shift(GLOBEX_OPEN_CT, 1), -1, -1)` -> `TradingInterval(GLOBEX_OPEN_CT, shift(GLOBEX_OPEN_CT, 1), 0, -1)` | killed | 1: main:test_trading_windows_are_the_s0_12_intervals |
| C1-13 | cp1.py | `TradingInterval(GLOBEX_OPEN_CT, shift(GLOBEX_OPEN_CT, 1), -1, -1)` -> `TradingInterval(GLOBEX_OPEN_CT, shift(GLOBEX_OPEN_CT, 1), -1, 0)` | killed | 1: main:test_trading_windows_are_the_s0_12_intervals |
| C1-14 | cp1.py | `TradingInterval(self._signal_at, shift(self._signal_at, 1))` -> `TradingInterval(self._signal_at, shift(self._signal_at, 2))` | killed | 1: main:test_trading_windows_are_the_s0_12_intervals |
| C1-15 | cp1.py | `TradingInterval(self._entry_at, self._leg.c)` -> `TradingInterval(self._entry_at, shift(self._leg.c, 8))` | killed | 1: main:test_trading_windows_are_the_s0_12_intervals |
| C1-16 | cp1.py | `self._signal_at = shift(self._leg.o, SIGNAL_AFTER_O_MIN)` -> `self._signal_at = shift(self._leg.o, -SIGNAL_AFTER_O_MIN)` | killed | 16: main:test_trading_windows_are_the_s0_12_intervals; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| C1-17 | cp1.py | `self._entry_at = shift(self._leg.c, -ENTRY_BEFORE_C_MIN)` -> `self._entry_at = shift(self._leg.c, ENTRY_BEFORE_C_MIN)` | killed | 19: main:test_trading_windows_are_the_s0_12_intervals; main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal |
| C1-18 | cp1.py | `self._exit_at = shift(self._leg.c, -EXIT_BEFORE_C_MIN)` -> `self._exit_at = shift(self._leg.c, EXIT_BEFORE_C_MIN)` | killed | 14: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-19 | cp1.py | `if bar.trade_date != self._day:             self._reset` -> `if bar.trade_date == self._day:             self._reset` | killed | 3: main:test_cp1_trades_once_per_trade_date_on_consecutive_days; main:test_cp1_monday_from_2026_06_01_reads_no_weekend_bar; main:test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| C1-20 | cp1.py | `if bar.trade_date != self._day:             self._reset` -> `if False:             self._reset` | killed | 3: main:test_cp1_trades_once_per_trade_date_on_consecutive_days; main:test_cp1_monday_from_2026_06_01_reads_no_weekend_bar; main:test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| C1-21 | cp1.py | `if account.position(self.root):` -> `if not account.position(self.root):` | killed | 18: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-22 | cp1.py | `if opened.date() == day - ONE_DAY and at == GLOBEX_OPEN_CT:` -> `if at == GLOBEX_OPEN_CT:` | killed | 2: main:test_cp1_monday_from_2026_06_01_the_sunday_1700_open_decides; main:test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides |
| C1-23 | cp1.py | `if opened.date() == day - ONE_DAY and at == GLOBEX_OPEN_CT:` -> `if opened.date() == day + ONE_DAY and at == GLOBEX_OPEN_CT:` | killed | 18: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-24 | cp1.py | `if opened.date() == day - ONE_DAY and at == GLOBEX_OPEN_CT:` -> `if opened.date() == day - ONE_DAY and at >= GLOBEX_OPEN_CT:` | killed | 4: main:test_cp1_missing_first_bar_is_no_trade_l05; main:test_cp1_monday_before_2026_05_29_opens_sunday_1700; main:test_cp1_monday_from_2026_06_01_the_sunday_1700_open_decides |
| C1-25 | cp1.py | `if opened.date() == day - ONE_DAY and at == GLOBEX_OPEN_CT:` -> `if opened.date() < day and at == GLOBEX_OPEN_CT:` | killed | 2: main:test_cp1_monday_from_2026_06_01_the_sunday_1700_open_decides; main:test_cp1_after_a_booked_forward_monday_the_monday_1700_open_decides |
| C1-27 | cp1.py | `if opened.date() != day:             return ()  # weekend` -> `if False:             return ()  # weekend` | killed | 4: main:test_cp1_monday_from_2026_06_01_reads_no_weekend_bar; main:test_cp1_monday_from_2026_06_01_the_sunday_1700_open_decides; main:test_cp1_after_a_booked_forward_monday_the_first_bar_is_monday_1700 |
| C1-28 | cp1.py | `if at == self._signal_at:` -> `if at >= self._signal_at:` | killed | 18: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-29 | cp1.py | `if at != self._entry_at or self._entered or not is_flat(account, self.` -> `if at == self._entry_at or self._entered or not is_flat(account, self.` | killed | 18: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-30 | cp1.py | `if at != self._entry_at or self._entered or not is_flat(account, self.` -> `if at != self._entry_at or not is_flat(account, self.root):` | killed | 1: main:test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| C1-31 | cp1.py | `if at != self._entry_at or self._entered or not is_flat(account, self.` -> `if at != self._entry_at or self._entered:` | killed | 1: main:test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| C1-32 | cp1.py | `if at != self._entry_at or self._entered or not is_flat(account, self.` -> `if at < self._entry_at or self._entered or not is_flat(account, self.r` | killed | 1: main:test_cp1_missing_1429_entry_bar_is_no_trade_l04 |
| C1-33 | cp1.py | `self._entered = True  # the one entry` -> `self._entered = False  # the one entry` | killed | 1: main:test_cp1_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| C1-34 | cp1.py | `if first_id != signal_id:` -> `if first_id == signal_id:` | killed | 18: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-35 | cp1.py | `if first_id != signal_id:` -> `if False:` | killed | 1: main:test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06 |
| C1-36 | cp1.py | `if s == 0:` -> `if s != 0:` | killed | 19: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-37 | cp1.py | `if s == 0:` -> `if False:` | killed | 1: main:test_cp1_zero_signal_is_no_trade |
| C1-38 | cp1.py | `return "buy" if s > 0 else "sell"` -> `return "buy" if s < 0 else "sell"` | killed | 16: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-39 | cp1.py | `return "buy" if s > 0 else "sell"` -> `return "buy" if s > 1 else "sell"` | killed | 1: main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-40 | cp1.py | `return "buy" if s > 0 else "sell"` -> `return "buy" if s >= -1 else "sell"` | killed | 1: main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-41 | cp1.py | `s = signal_close - first_open` -> `s = first_open - signal_close` | killed | 16: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-42 | cp1.py | `return to_ticks(asdict(bar)["open"], tick)` -> `return to_ticks(asdict(bar)["close"], tick)` | killed | 16: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-43 | cp1.py | `self._signal = (to_ticks(bar.close, self._leg.tick), bar.instrument_id` -> `self._signal = (to_ticks(bar.low, self._leg.tick), bar.instrument_id)` | killed | 13: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_the_signal_is_one_tick_either_side_of_zero; main:test_cp1_zero_signal_is_no_trade |
| C1-44 | cp1.py | `if self._first is None or self._signal is None:             return Non` -> `if self._first is None and self._signal is None:             return No` | killed | 5: main:test_cp1_missing_first_bar_is_no_trade_l05; main:test_cp1_missing_0859_signal_bar_is_no_trade; main:test_cp1_state_resets_each_trade_date |
| C1-45 | cp1.py | `return (leg_market_intent(view, self.root, side, self._leg.q),)` -> `return (leg_market_intent(view, self.root, side, 2),)` | killed | 17: main:test_cp1_buys_on_a_positive_signal_at_1430_and_exits_at_1459; main:test_cp1_sells_on_a_negative_signal; main:test_cp1_the_signal_is_one_tick_either_side_of_zero |
| C1-46 | cp1.py | `self._first = (_first_bar_open_ticks(bar, self._leg.tick), bar.instrum` -> `self._first = (_first_bar_open_ticks(bar, self._leg.tick), 777)` | killed | 1: main:test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06 |
| C1-47 | cp1.py | `self._signal = (to_ticks(bar.close, self._leg.tick), bar.instrument_id` -> `self._signal = (to_ticks(bar.close, self._leg.tick), 777)` | killed | 1: main:test_cp1_signal_bars_with_two_instrument_ids_are_no_trade_l06 |
| C1-48 | cp1.py | `MEMBER_ID = "K7-cp1-01"` -> `MEMBER_ID = "K7-cp1-02"` | killed | 1: main:test_member_ids_are_the_catalog_ids |
| C1-49 | cp1.py | `return Cp1Momentum("MBT")` -> `return Cp1Momentum("MET")` | killed | 25: main:test_factories_name_the_label_and_trade_one_leg[K7-cp1-01]; main:test_trading_windows_are_the_s0_12_intervals; main:test_a_none_bar_is_no_decision_and_changes_no_state |
| C2-01 | cp2.py | `RANGE_MINUTES = 15` -> `RANGE_MINUTES = 14` | killed | 2: cp2:test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06; cp2:test_cp2_one_opening_range_bar_is_enough |
| C2-02 | cp2.py | `RANGE_MINUTES = 15` -> `RANGE_MINUTES = 16` | killed | 23: cp2:test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06; cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice |
| C2-03 | cp2.py | `BUFFER_TICKS = 4` -> `BUFFER_TICKS = 3` | killed | 5: cp2:test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06; cp2:test_cp2_the_0830_bar_is_a_range_bar; cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side |
| C2-04 | cp2.py | `BUFFER_TICKS = 4` -> `BUFFER_TICKS = 5` | killed | 29: cp2:test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06; cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice |
| C2-05 | cp2.py | `HOLD_BARS = 75` -> `HOLD_BARS = 74` | killed | 24: cp2:test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06; cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice |
| C2-06 | cp2.py | `HOLD_BARS = 75` -> `HOLD_BARS = 76` | killed | 24: cp2:test_cp2_literals_are_or_15_buffer_4_ticks_hold_75_k4_l06; cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice |
| C2-07 | cp2.py | `F_REGULAR_CT = time(15, 8)` -> `F_REGULAR_CT = time(15, 0)` | killed | 1: main:test_trading_windows_are_the_s0_12_intervals |
| C2-08 | cp2.py | `F_REGULAR_CT = time(15, 8)` -> `F_REGULAR_CT = time(15, 9)` | killed | 1: main:test_trading_windows_are_the_s0_12_intervals |
| C2-09 | cp2.py | `if self._held < HOLD_BARS or account.pending.get(self.root, 0):` -> `if self._held <= HOLD_BARS or account.pending.get(self.root, 0):` | killed | 23: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-10 | cp2.py | `if self._held < HOLD_BARS or account.pending.get(self.root, 0):` -> `if self._held < HOLD_BARS:` | killed | 1: cp2:test_cp2_a_deferred_exit_is_not_sent_twice |
| C2-11 | cp2.py | `self._held += 1` -> `self._held += 2` | killed | 25: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-12 | cp2.py | `side = "sell" if position > 0 else "buy"` -> `side = "sell" if position < 0 else "buy"` | killed | 23: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-13 | cp2.py | `return (leg_market_intent(view, self.root, side, abs(position)),)` -> `return (leg_market_intent(view, self.root, side, position),)` | killed | 5: cp2:test_cp2_breakout_down_sells; cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_first_qualifying_bar_takes_the_entry |
| C2-14 | cp2.py | `if bar.trade_date != self._day:` -> `if bar.trade_date == self._day:` | killed | 2: cp2:test_cp2_state_resets_each_trade_date; cp2:test_cp2_the_range_resets_each_trade_date |
| C2-15 | cp2.py | `if bar.trade_date != self._day:` -> `if False:` | killed | 2: cp2:test_cp2_state_resets_each_trade_date; cp2:test_cp2_the_range_resets_each_trade_date |
| C2-16 | cp2.py | `if self._triggered and account.position(self.root):` -> `if account.position(self.root):` | SURVIVED | 119 passed in 3.70s |
| C2-17 | cp2.py | `if self._triggered and account.position(self.root):` -> `if self._triggered or account.position(self.root):` | killed | 8: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_position_open_at_a_synthetic_f_is_flattened_by_the_engine |
| C2-18 | cp2.py | `if opened.date() != bar.trade_date:             return ()` -> `if False:             return ()` | killed | 2: cp2:test_cp2_monday_from_2026_06_01_reads_no_weekend_bar; cp2:test_cp2_after_a_booked_forward_monday_reads_only_the_tuesday |
| C2-19 | cp2.py | `if self._leg.o <= at < self._range_end:` -> `if self._leg.o < at < self._range_end:` | killed | 1: cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-20 | cp2.py | `if self._leg.o <= at < self._range_end:` -> `if self._leg.o <= at <= self._range_end:` | killed | 22: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-21 | cp2.py | `self._hi = bar.high if self._hi is None else max(self._hi, bar.high)` -> `self._hi = bar.high if self._hi is None else min(self._hi, bar.high)` | killed | 5: cp2:test_cp2_the_0830_bar_is_a_range_bar; cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_buffer_is_20_usd_in_prices |
| C2-22 | cp2.py | `self._lo = bar.low if self._lo is None else min(self._lo, bar.low)` -> `self._lo = bar.low if self._lo is None else max(self._lo, bar.low)` | killed | 2: cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_range_is_the_max_high_and_min_low |
| C2-23 | cp2.py | `self._hi = bar.high if self._hi is None else max(self._hi, bar.high)` -> `self._hi = bar.close if self._hi is None else max(self._hi, bar.close)` | killed | 5: cp2:test_cp2_the_0830_bar_is_a_range_bar; cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_buffer_is_20_usd_in_prices |
| C2-24 | cp2.py | `self._lo = bar.low if self._lo is None else min(self._lo, bar.low)` -> `self._lo = bar.close if self._lo is None else min(self._lo, bar.close)` | killed | 2: cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_range_is_the_max_high_and_min_low |
| C2-25 | cp2.py | `if self._triggered or self._hi is None or self._lo is None:` -> `if self._hi is None or self._lo is None:` | killed | 3: cp2:test_cp2_one_entry_per_trade_date_even_when_the_engine_refuses_it; cp2:test_cp2_one_entry_per_trade_date_after_the_exit; cp2:test_cp2_d97_engine_exit_no_duplicate_exit_and_no_reentry |
| C2-26 | cp2.py | `if not self._range_end <= at < self._leg.c or not is_flat(account, sel` -> `if not self._range_end <= at <= self._leg.c or not is_flat(account, se` | killed | 1: cp2:test_cp2_no_entry_from_1500 |
| C2-27 | cp2.py | `if not self._range_end <= at < self._leg.c or not is_flat(account, sel` -> `if not self._range_end < at < self._leg.c or not is_flat(account, self` | killed | 19: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_breakout_down_sells |
| C2-28 | cp2.py | `if not self._range_end <= at < self._leg.c or not is_flat(account, sel` -> `if not self._range_end <= at < self._leg.c:` | killed | 1: cp2:test_cp2_no_entry_while_an_order_is_pending |
| C2-29 | cp2.py | `if not self._range_end <= at < self._leg.c or not is_flat(account, sel` -> `if not self._range_end <= at < F_REGULAR_CT or not is_flat(account, se` | killed | 1: cp2:test_cp2_no_entry_from_1500 |
| C2-30 | cp2.py | `if close >= to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:` -> `if close > to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:` | killed | 26: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-31 | cp2.py | `if close >= to_ticks(self._hi, self._leg.tick) + BUFFER_TICKS:` -> `if close >= to_ticks(self._hi, self._leg.tick) - BUFFER_TICKS:` | killed | 15: cp2:test_cp2_the_0830_bar_is_a_range_bar; cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_buffer_is_20_usd_in_prices |
| C2-32 | cp2.py | `elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:` -> `elif close < to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:` | killed | 5: cp2:test_cp2_breakout_down_sells; cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_first_qualifying_bar_takes_the_entry |
| C2-33 | cp2.py | `elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:` -> `elif close <= to_ticks(self._lo, self._leg.tick) + BUFFER_TICKS:` | killed | 15: cp2:test_cp2_the_0830_bar_is_a_range_bar; cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_buffer_is_20_usd_in_prices |
| C2-34 | cp2.py | `elif close <= to_ticks(self._lo, self._leg.tick) - BUFFER_TICKS:` -> `elif close <= to_ticks(self._hi, self._leg.tick) - BUFFER_TICKS:` | killed | 3: cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_range_is_the_max_high_and_min_low; cp2:test_cp2_the_range_resets_each_trade_date |
| C2-35 | cp2.py | `side = "buy"         elif` -> `side = "sell"         elif` | killed | 25: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-36 | cp2.py | `side = "sell"         else:` -> `side = "buy"         else:` | killed | 5: cp2:test_cp2_breakout_down_sells; cp2:test_cp2_the_buffer_is_exactly_four_ticks_either_side; cp2:test_cp2_the_first_qualifying_bar_takes_the_entry |
| C2-37 | cp2.py | `self._triggered = True  # one entry per trade date` -> `self._triggered = False  # one entry per trade date` | killed | 25: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-38 | cp2.py | `return (leg_market_intent(view, self.root, side, self._leg.q),)` -> `return (leg_market_intent(view, self.root, side, 2),)` | killed | 27: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-39 | cp2.py | `self._day, self._hi, self._lo, self._triggered, self._held = day, None` -> `self._day, self._hi, self._lo, self._triggered, self._held = day, None` | killed | 23: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-40 | cp2.py | `self._day, self._hi, self._lo, self._triggered, self._held = day, None` -> `self._day, self._triggered, self._held = day, False, 0` | killed | 1: cp2:test_cp2_the_range_resets_each_trade_date |
| C2-41 | cp2.py | `self._range_end = shift(self._leg.o, RANGE_MINUTES)` -> `self._range_end = shift(self._leg.o, -RANGE_MINUTES)` | killed | 28: cp2:test_cp2_breakout_fills_next_open_and_exits_after_75_present_bars; cp2:test_cp2_a_deferred_exit_is_not_sent_twice; cp2:test_cp2_the_0830_bar_is_a_range_bar |
| C2-42 | cp2.py | `MEMBER_ID = "K7-cp2-01"` -> `MEMBER_ID = "K7-cp2-02"` | killed | 1: main:test_member_ids_are_the_catalog_ids |
| C3-01 | cp3.py | `CLV_BUY_AT_OR_ABOVE = Decimal("0.8")` -> `CLV_BUY_AT_OR_ABOVE = Decimal("0.7")` | killed | 4: cp3:test_cp3_literals_are_the_clv_cuts_and_the_clock; cp3:test_cp3_clv_strictly_between_the_cuts_is_no_trade[7]; cp3:test_cp3_clv_cuts_are_compared_exactly[15-11-None] |
| C3-02 | cp3.py | `CLV_BUY_AT_OR_ABOVE = Decimal("0.8")` -> `CLV_BUY_AT_OR_ABOVE = Decimal("0.9")` | killed | 23: cp3:test_cp3_literals_are_the_clv_cuts_and_the_clock; cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_clv_cuts_are_compared_exactly[10-8-buy] |
| C3-03 | cp3.py | `CLV_SELL_AT_OR_BELOW = Decimal("0.2")` -> `CLV_SELL_AT_OR_BELOW = Decimal("0.1")` | killed | 11: cp3:test_cp3_literals_are_the_clv_cuts_and_the_clock; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_cuts_are_compared_exactly[10-2-sell] |
| C3-04 | cp3.py | `CLV_SELL_AT_OR_BELOW = Decimal("0.2")` -> `CLV_SELL_AT_OR_BELOW = Decimal("0.3")` | killed | 4: cp3:test_cp3_literals_are_the_clv_cuts_and_the_clock; cp3:test_cp3_clv_strictly_between_the_cuts_is_no_trade[3]; cp3:test_cp3_clv_cuts_are_compared_exactly[15-4-None] |
| C3-05 | cp3.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 2` | killed | 27: cp3:test_cp3_literals_are_the_clv_cuts_and_the_clock; cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_clv_strictly_between_the_cuts_is_no_trade[3] |
| C3-06 | cp3.py | `CLOSE_BEFORE_C_MIN = 1` -> `CLOSE_BEFORE_C_MIN = 0` | killed | 27: cp3:test_cp3_literals_are_the_clv_cuts_and_the_clock; cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells |
| C3-07 | cp3.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 1` | killed | 23: cp3:test_cp3_literals_are_the_clv_cuts_and_the_clock; cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells |
| C3-08 | cp3.py | `EXIT_BEFORE_C_MIN = 2` -> `EXIT_BEFORE_C_MIN = 3` | killed | 24: cp3:test_cp3_literals_are_the_clv_cuts_and_the_clock; cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells |
| C3-09 | cp3.py | `if span <= 0:` -> `if span < 0:` | killed | 2: cp3:test_cp3_clv_cuts_are_compared_exactly[0-0-None]; cp3:test_cp3_zero_range_is_no_trade |
| C3-10 | cp3.py | `if span <= 0:` -> `if span <= 1:` | killed | 2: cp3:test_cp3_clv_cuts_are_compared_exactly[1-1-buy]; cp3:test_cp3_clv_cuts_are_compared_exactly[1-0-sell] |
| C3-11 | cp3.py | `num = prior.close - prior.low` -> `num = prior.high - prior.close` | killed | 34: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-12 | cp3.py | `if num * buy_d >= buy_n * span:` -> `if num * buy_d > buy_n * span:` | killed | 22: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_clv_cuts_are_compared_exactly[10-8-buy]; cp3:test_cp3_clv_cuts_are_compared_exactly[5-4-buy] |
| C3-13 | cp3.py | `if num * sell_d <= sell_n * span:` -> `if num * sell_d < sell_n * span:` | killed | 10: cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_cuts_are_compared_exactly[10-2-sell]; cp3:test_cp3_clv_cuts_are_compared_exactly[5-1-sell] |
| C3-14 | cp3.py | `if num * buy_d >= buy_n * span:         return "buy"` -> `if num * buy_d >= buy_n * span:         return "sell"` | killed | 25: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy]; cp3:test_cp3_clv_beyond_the_cuts_trades[9-buy] |
| C3-15 | cp3.py | `if num * sell_d <= sell_n * span:         return "sell"` -> `if num * sell_d <= sell_n * span:         return "buy"` | killed | 13: cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[1-sell]; cp3:test_cp3_clv_beyond_the_cuts_trades[0-sell] |
| C3-16 | cp3.py | `complete = (self._has_open_bar and self._close is not None and not sel` -> `complete = (self._close is not None and not self._halt` | killed | 1: cp3:test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete |
| C3-17 | cp3.py | `complete = (self._has_open_bar and self._close is not None and not sel` -> `complete = (self._has_open_bar and self._close is not None` | killed | 2: cp3:test_cp3_the_halt_flag_resets_each_trade_date; cp3:test_cp3_early_halt_day_is_not_traded_and_is_incomplete |
| C3-18 | cp3.py | `and len(self._ids) == 1)` -> `and len(self._ids) >= 1)` | killed | 1: cp3:test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| C3-19 | cp3.py | `if finished is not None:             self._prior = finished` -> `if True:             self._prior = finished` | killed | 5: cp3:test_cp3_the_halt_flag_resets_each_trade_date; cp3:test_cp3_d_minus_1_is_the_most_recent_complete_day; cp3:test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete |
| C3-20 | cp3.py | `if bar.early_halt_ct is not None:  # any bar of CT date d (Family H)` -> `if bar.early_halt_ct is None:  # any bar of CT date d (Family H)` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-21 | cp3.py | `if not self._leg.o <= at < self._leg.c:             return` -> `if not self._leg.o < at < self._leg.c:             return` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-22 | cp3.py | `if not self._leg.o <= at < self._leg.c:             return` -> `if not self._leg.o <= at <= self._leg.c:             return` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-23 | cp3.py | `self._ids = self._ids \| {bar.instrument_id}` -> `self._ids = frozenset({bar.instrument_id})` | killed | 1: cp3:test_cp3_a_day_with_two_instrument_ids_is_incomplete |
| C3-24 | cp3.py | `self._hi = bar.high if self._hi is None else max(self._hi, bar.high)` -> `self._hi = bar.high if self._hi is None else min(self._hi, bar.high)` | killed | 25: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-25 | cp3.py | `self._lo = bar.low if self._lo is None else min(self._lo, bar.low)` -> `self._lo = bar.low if self._lo is None else max(self._lo, bar.low)` | killed | 2: cp3:test_cp3_the_daily_low_is_the_min_low[6-buy]; cp3:test_cp3_day_accumulators_reset_each_trade_date |
| C3-26 | cp3.py | `if at == self._leg.o:             self._has_open_bar = True` -> `if at >= self._leg.o:             self._has_open_bar = True` | killed | 1: cp3:test_cp3_missing_0830_bar_is_no_trade_and_the_day_is_incomplete |
| C3-27 | cp3.py | `if at == self._close_at:` -> `if at >= self._close_at:` | SURVIVED | 119 passed in 3.69s |
| C3-28 | cp3.py | `if at == self._close_at:` -> `if at <= self._close_at:` | killed | 3: cp3:test_cp3_warm_up_no_complete_earlier_bar_is_no_trade; cp3:test_cp3_d_minus_1_is_the_most_recent_complete_day; cp3:test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar |
| C3-29 | cp3.py | `if bar.early_halt_ct is not None:             return None  # a` -> `if False:             return None  # an early-halt day d` | killed | 3: cp3:test_cp3_the_halt_flag_resets_each_trade_date; cp3:test_cp3_early_halt_day_is_not_traded_and_is_incomplete; cp3:test_cp3_a_halt_day_with_a_buy_prior_is_still_not_traded |
| C3-30 | cp3.py | `if prior.instrument_id != bar.instrument_id:` -> `if prior.instrument_id == bar.instrument_id:` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-31 | cp3.py | `if prior.instrument_id != bar.instrument_id:` -> `if False:` | killed | 1: cp3:test_cp3_instrument_guard_compares_d_minus_1_with_the_0830_bar |
| C3-32 | cp3.py | `if bar.trade_date != self._day:` -> `if bar.trade_date == self._day:` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-33 | cp3.py | `if opened.date() != day:             return ()  # another CT d` -> `if False:             return ()  # another CT date` | killed | 3: cp3:test_cp3_monday_from_2026_06_01_reads_no_weekend_bar; cp3:test_cp3_after_a_booked_forward_monday_d_minus_1_is_the_friday; cp3:test_cp3_a_booked_forward_holiday_session_is_never_a_daily_bar |
| C3-34 | cp3.py | `if account.position(self.root):` -> `if not account.position(self.root):` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-35 | cp3.py | `if at != self._leg.o or self._entered or not is_flat(account, self.roo` -> `if at == self._leg.o or self._entered or not is_flat(account, self.roo` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-36 | cp3.py | `if at != self._leg.o or self._entered or not is_flat(account, self.roo` -> `if at != self._leg.o or not is_flat(account, self.root):` | killed | 1: cp3:test_cp3_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| C3-37 | cp3.py | `if at != self._leg.o or self._entered or not is_flat(account, self.roo` -> `if at != self._leg.o or self._entered:` | killed | 1: cp3:test_cp3_emits_at_most_one_entry_per_trade_date_and_none_while_pending |
| C3-38 | cp3.py | `return DailyBar(self._day, to_ticks(self._hi, tick), to_ticks(self._lo` -> `return DailyBar(self._day, to_ticks(self._lo, tick), to_ticks(self._hi` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-39 | cp3.py | `return (leg_market_intent(view, self.root, side, self._leg.q),)` -> `return (leg_market_intent(view, self.root, side, 2),)` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-40 | cp3.py | `self._close_at = shift(self._leg.c, -CLOSE_BEFORE_C_MIN)` -> `self._close_at = shift(self._leg.c, CLOSE_BEFORE_C_MIN)` | killed | 26: cp3:test_cp3_prior_clv_at_08_buys_on_the_0830_bar_and_exits_at_1459; cp3:test_cp3_prior_clv_at_02_sells; cp3:test_cp3_clv_beyond_the_cuts_trades[10-buy] |
| C3-41 | cp3.py | `self.trading_windows = {self.root: (TradingInterval(self._leg.o, self.` -> `self.trading_windows = {self.root: (TradingInterval(self._leg.o, shift` | killed | 1: main:test_trading_windows_are_the_s0_12_intervals |
| C3-43 | cp3.py | `MEMBER_ID = "K7-cp3-01"` -> `MEMBER_ID = "K7-cp3-02"` | killed | 1: main:test_member_ids_are_the_catalog_ids |
| C3-44 | cp3.py | `self._day, self._halt, self._has_open_bar, self._entered = day, False,` -> `self._day, self._halt, self._has_open_bar, self._entered = day, self._` | killed | 1: cp3:test_cp3_the_halt_flag_resets_each_trade_date |
| C3-45 | cp3.py | `self._hi, self._lo, self._close, self._ids = None, None, None, frozens` -> `self._close, self._ids = None, frozenset()` | killed | 1: cp3:test_cp3_day_accumulators_reset_each_trade_date |

Total 153: killed 150, survived 3.


## 4. Commands and results

All times PDT, 2026-09-27.

| Command | Result |
|---|---|
| `uv run pytest -q tests/test_k7_members_ports.py tests/test_k7_members_ports_cp2.py tests/test_k7_members_ports_cp3.py tests/test_stage_e_template.py` (PYTHONPYCACHEPREFIX unset), 22:03 | 122 passed in 3.74s (119 port cases + 3 template tests) |
| `uv run ruff check <the 4 member files> tests/test_k7_members_ports*.py` | All checks passed |
| `screening.stage_e_freeze.check_member_source(rel, source, "K7")` on each of the 4 files (in the test file and by script, PYTHONPYCACHEPREFIX set to the scratchpad) | [] for each |
| `screening.stage_e_freeze.check_cluster_sources("K7", <scratch root holding only the 4 coder-A files and empty __init__.py files>)` | None (passes). Run on a scratch root so coder B's in-progress files are not judged here; the lead's freeze checks the whole directory |
| `test_the_3_port_declarations_freeze_and_verify_under_tmp_path` (write_cluster_freeze, load_cluster_freeze, verify_cluster_code under tmp_path) | passed |
| `stat -c %s strategy/members/k7/__init__.py strategy/members/__init__.py` | 0 and 0 bytes |
| `nice -n 10 .venv/bin/python /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0f52aad4-207e-43da-84df-b6a0ead28371/scratchpad/mutants.py` (in the isolated copy), 22:03-22:13 | 153 mutants: 150 killed, 3 equivalent survivors |

sha256 of the delivered files (22:13):
- strategy/members/k7/_port_common.py 4fd2bc1bbfb5cba1f79bfb2edd70f0b9d8fb19bd76a97d559f5a7cbbfd0ba840
- strategy/members/k7/cp1.py 94202bf614dcc2065604d6c883247069d4c6c215d5157615ba0afb8b93d56ce9
- strategy/members/k7/cp2.py 0ecf4c64becec4e87cb1984f929cd5f610db6ed100987aa9724607ef761a995b
- strategy/members/k7/cp3.py 25b013d07cc70735c735fdc1b8b61a80e910c90a5ce7981f3219971d053acfd0
- tests/test_k7_members_ports.py ee78d12a957859b69043d66f5aee274a3365b5fdfe54498a800c4edb4d274423
- tests/test_k7_members_ports_cp2.py afe934058d801199a726f22dc323d2dfc5dd4d8bb9812a98cef5513bcbafc414
- tests/test_k7_members_ports_cp3.py cfd8785492e4dfe5c86afdaeadcf1450ee937fe3c0967b3272c622faeae7e026

The full suite was not run (the lead runs it). Running pytest with PYTHONPYCACHEPREFIX unset, as
the brief says, leaves __pycache__ directories under strategy/members/k7/ and tests/ (ignored by
git; the freeze hashes only *.py files).

## 5. Questions and notes for the lead

No question stopped the work: the spec fixed every detail the three ports need. Notes for the lead:

1. The brief's "19.99 beyond does not trigger" cannot hold at the member level under S0.10: the
   member compares `round(price / 5.00)` ticks, and an OR_high + 19.99 close rounds to 4 ticks,
   which triggers. It cannot arise in a run: 19.99 is off MBT's 5.00 vendor grid and the engine's
   bar iterator raises EngineInvariantError on the frame before any member call (pinned by
   test_cp2_a_close_1999_beyond_the_range_never_reaches_the_member). On the grid, the closest
   price below the buffer is 15.00 (3 ticks, no entry; pinned) and 20.00 is the tie (entry;
   pinned). No trade can differ between a 4-tick and a 20.00-USD reading, so this was not
   treated as an open detail. I did not write a test that pins the off-grid rounding.
2. CP2's trading window end 15:08 (F) is a literal `F_REGULAR_CT`, as in K4: rules.sessions is not
   an allowed member import. The value matches rules.sessions.flatten_time_ct("MBT", d) on every
   regular scenario date (checked in test_the_synthetic_scenarios_are_ec_cal_facts).
3. CP3 treats a day as an early halt when any bar of CT date d carries early_halt_ct (the K4
   form). data/group_session.early_halt_labels labels bars by CT calendar date, so every bar of
   CT date d carries the same label; a booked-forward holiday's CT date carries no label in the
   research window (checked for 2026-01-19 and 2025-11-27), so the Tuesday after it is not a halt day.
4. Engine behaviour seen in the tests, not a member choice: with a real F of 15:08 the engine's
   forced flatten fills at the 15:08 open (and at 11:30 on 2025-07-04); a position cannot change
   instrument_id (EngineInvariantError on a splice), so CP3's guard test changes the id only on
   bars read before the entry.
