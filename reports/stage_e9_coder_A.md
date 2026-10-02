# Stage E.9 Task 2, coder A (MemberCoder-A-OpusXHigh): K8 tables and K8-flight-01

Worker: opus, xhigh (worker-xhigh). Brief: reports/stage_e9_briefs/2A_member_coder_A.md. Spec:
reports/stage_e9_member_specs.md sections 0, 1, 5, 6 and 7 (section 7 arrived by message at 22:33 PDT:
R-1b-1 no correction, R-1b-3, the research-window counts). Spawned 22:29 PDT, finished 23:09 PDT.
No bar file opened, no bar loader called, no web access, no commit. strategy/members/k8/__init__.py
untouched (0 bytes). No harness file and no other cluster changed.

## 1. Files

| File | Lines | sha256 (first 16) | Role |
|---|---|---|---|
| reports/stage_e9_briefs/gen_k8_tables.py | 413 | 77c5041f77cbbad0 | generator of the two table modules |
| strategy/members/k8/_calendar.py | 573 | 1e10dc29234abd5f | GENERATED: full sessions per group, member date tuples, previous_dates |
| strategy/members/k8/_releases.py | 830 | 2acb8ab3fb2d230a | GENERATED: GUARD_ROWS, GUARD_INSTANTS, in_guard |
| strategy/members/k8/flight.py | 319 | 020056632df9eea7 | K8-flight-01, make_h30 and make_heod |
| tests/test_k8_members_tables.py | 323 | | table pins (31 test cases) |
| tests/test_k8_members_flight.py | 488 | | declaration, block clock, r_k, Q(d), trigger, warm-up, references; the shared kit |
| tests/test_k8_members_flight_exits.py | 309 | | first trigger, C6, missing and late bars, T_e, exits |
| tests/test_k8_members_flight_engine.py | 190 | | run_engine on synthetic two-leg frames |

No strategy/members/k8/_common.py was written. Coder B imports _calendar.py and _releases.py.

The tables were written and tested first (first generation about 22:40 PDT). At 22:48 PDT I regenerated
_calendar.py once to drop a redundant `if k <= 0: return ()` guard from previous_dates (the slice already
returns () for k <= 0; the guard could only ever give an equivalent mutant). Behaviour is identical; the
file's sha256 changed to 1e10dc29.... _releases.py was rewritten at the same time with identical bytes.

Regenerate: `uv run python reports/stage_e9_briefs/gen_k8_tables.py` (from the repository root). The
generator asserts the spec header's and section 7's research-window facts before it writes anything.

## 2. Part 1: the tables

### _calendar.py (S0.8, S0.11, K8-L-03, K8-L-14, R-1b-3)

- `<GROUP>_FULL_SESSIONS` (EQUITY, CRYPTO, METALS, ENERGY, FX): frozenset[date] of the group's EC-CAL trade
  dates 2019-05-01..2026-06-19 with `early_halt_ct` None AND `rules.sessions.flatten_time_ct(root, d) ==
  15:08` for every K8 root of the group (equity MES and MNQ, crypto MBT, metals MGC, energy MCL, fx 6C).
  The generator and the test assert the roots of a group give one F on every trade date (MES and MNQ
  agree on all equity dates).
- Encoding: the weekdays of TABLE_RANGE less `<GROUP>_NOT_FULL`, a literal list of every weekday that is not
  a full session with its reason ("not a trade date: full closure", "not a trade date: booked forward to
  <date>", "early halt HH:MM; F HH:MM"). The frozensets are built at import from those literals.
- `FLIGHT_DATES` = sorted EQUITY & METALS, `OILCAD_DATES` = sorted ENERGY & FX, `WKNDBTC_DATES` = sorted
  EQUITY & CRYPTO (tuples of date).
- `previous_dates(dates, d, k)`: the k most recent elements of the sorted `dates` strictly before d,
  OLDEST FIRST; fewer at the table's start; () for k <= 0.
- SOURCE_SHA256: data/calendars/__init__.py, crypto.py, energy.py, equity.py, fx.py, metals.py,
  data/cme_calendar.py, rules/sessions.py (beb9501d...).
- Counts: full sessions equity 1779, crypto 1782, metals 1783, energy 1783, fx 1783; FLIGHT_DATES 1779,
  OILCAD_DATES 1783, WKNDBTC_DATES 1779. Research window 2025-04-01..2026-06-19 (pinned, section 7):
  equity 303, crypto 304, metals 304, energy 304, fx 304; FLIGHT 303, OILCAD 304, WKNDBTC 303; Mondays d
  with d and d - 3 in WKNDBTC_DATES: 54. 2026-06-01 is a crypto full session (R-1b-3, pinned).
- Dates where the early-halt test and the F test disagree (F early, no halt): crypto, metals, energy
  2024-07-03 (F 11:30); fx 31 dates (2022-2026 US holidays with F 11:30 for 6C); equity none.

### _releases.py (S0.10, S0.11, K8-L-08, R-1b-1)

- `GUARD_ROWS`: (UTC epoch seconds, row id, the guard roots among the row's products) for the 769 rows of
  the frozen calendar (sha256 839f2437..., asserted) dated 2019-05-01..2026-06-19 whose products include
  MGC, 6C or MNQ, each with its CT clock as a comment. No correction (R-1b-1): WPSR-2025-12-29 (16:00 CT)
  and WPSR-2026-05-28 (11:00 CT) are in (pinned).
- `GUARD_INSTANTS`: root -> the sorted DISTINCT instants of the rows naming the root: MGC 312, 6C 513,
  MNQ 313 (the engine's D9.5a set also de-duplicates; no duplicate exists among these rows anyway).
  The date filter is not binding: every calendar row is dated 2019-05-01..2026-06-18.
- `in_guard(root, t_ns)`: True iff R * 1e9 <= t_ns < (R + 120) * 1e9 for some R (integer ns, a binary
  search over the sorted tuple; an unknown root raises KeyError).
- Research-window rows (pinned against the spec header): MGC NFP 14, CPI 14, G17 14 (09:15 ET), FOMC 10;
  6C WPSR 56 at 10:30 ET, 7 at 12:00 ET, 1 at 17:00 ET, NFP 14, FOMC 10; MNQ ISM_SERVICES 15, NFP 14,
  CPI 14, FOMC 10. Of the research MGC instants only the 10 FOMC 13:00 CT ones meet a flight fill minute
  (Task 1b A3, pinned).

### Cross-check with the earlier clusters' frozen tables (reported, not fixed)

Over each common range, the K8 set has no date the earlier table lacks. The earlier tables hold these
dates that the K8 definition removes (none in the research window; all pinned in
test_group_sets_against_the_earlier_clusters_frozen_tables):

| Group | Earlier table | Dates only in the earlier table | Cause |
|---|---|---|---|
| equity | k1 EQUITY_FULL_SESSIONS | none | |
| crypto | k7 CRYPTO_FULL_SESSIONS | none | |
| metals | k5 METALS_FULL_SESSIONS | 2024-07-03 | K5 tested the early halt only (no F test); F is 11:30 there |
| energy | k4 ENERGY_FULL_SESSIONS | 2024-07-03 | K4 tested the early halt only (no F test) |
| fx | k3 FX_FULL_SESSIONS | 2022-01-17, 2022-02-21, 2022-05-30, 2022-06-20, 2022-07-04, 2022-09-05, 2022-11-24, 2023-01-16, 2023-02-20, 2023-05-29, 2023-06-19, 2023-07-04, 2023-09-04, 2023-11-23 (14) | K3 was generated under rules/sessions.py d9a7fcfe... (Stage E.4c); E.5 (commit 2c0bfe0, pre-2024 holidays) changed it to beb9501d..., under which 6C's F on these US holidays is 11:30 |

All differences lie in the confirmation window. They concern only the earlier clusters' frozen tables; the
K8 tables follow S0.8 under the current rules/sessions.py.

## 3. Part 2: K8-flight-01 (strategy/members/k8/flight.py)

One dataclass `FlightToGold(variant)`, variant "H30" or "HEOD"; `make_h30`, `make_heod`; names
"K8-flight-01 H30 MGC" and "K8-flight-01 HEOD MGC"; legs (LegSpec("MGC", True), LegSpec("MES", False));
trading_windows MGC (08:34, 15:06), MES (08:29, 14:55); q_c from load_frozen_tables().vehicles["MGC"].q_c;
the MES tick from rules.products.product("MES").vendor_tick. Freeze static check: [] on flight.py,
_calendar.py, _releases.py and __init__.py.

How the spec's rules are coded (section 1; readings K8-L-02..K8-L-10):
- Bars by CT date and clock: an MES bar counts only if its CT open date equals its trade_date; the block
  bars are the bar at t_k - 6 (start; 08:29 for k = 1) and the bar at t_k - 1 (end), k = 1..77. Nothing
  is forward filled: a missing bar at either minute leaves r_k undefined.
- r_k = (c1 - c6) / c6 in integer ticks (round(Decimal(repr(price)) / tick)), both bars one
  instrument_id, c6 > 0. Every defined r_k is recorded, traded or not.
- History: r values per MES trade date, filed when the next MES trade date starts, kept only for dates
  at or after the oldest reference date of the new date (at most about 21 dates).
- Q(d): computed at d's first decision view from the 20 FLIGHT_DATES before d (previous_dates), never
  from d's own values; warm-up K4-L-09 (no trade while fewer than 20 reference dates exist or the oldest
  precedes the first bar's trade date); n < 1,200: none; m = (n + 199) // 200; the m-th smallest,
  duplicates counted.
- Trigger r_k <= Q(d) and r_k < 0, exact; d in FLIGHT_DATES.
- C6: `in_guard("MGC", view.decision_ts_ns)`, the fill minute t_k; a skipped trigger keeps the day's
  entry. The first non-skipped trigger uses the day's entry (E.3-L-08); if the MGC bar at t_k - 1 is
  missing (or carries another trade date) there is no entry and no trade on d (K8-L-06).
- T_e = the minute of the first view whose account shows the position (K8-L-07); exit bar H30
  min(T_e + 29, 15:04 on T_e's CT date), HEOD 15:04; sent on the first present MGC bar at or after it
  while the position is non-zero and nothing is pending (resent after a refusal, E.3-L-22); exit bars
  unguarded; a flat account sends nothing; T_e resets when flat.

Implementation details the spec does not spell out (none changes a trade on real bars; listed for the
lead and the auditor):
1. Exact rationals without `fractions`: the freeze's ALLOWED_IMPORTS has no fractions module, so r_k is a
   pair (numerator, positive denominator) compared by integer cross-multiplication (`compare`), and the
   order statistic sorts with functools.cmp_to_key. Every comparison equals fractions.Fraction's
   (pinned against Fraction, and against float at 10**17 where float collapses).
2. "The first bar the member received" (K4-L-09) is taken over both legs: the earliest trade_date among
   the bars of the first view that has any bar.
3. S0.6 at the first non-skipped trigger: if MGC then holds a position or a pending order, no intent is
   sent and the day's entry counts as used. This cannot occur on real bars (one entry a day; the engine
   flattens at F 15:08 before the next trade date opens). Only "no intent while pending" is tested; the
   "day used" part is not pinned.
4. to_ticks rounds to the nearest tick: the engine accepts prices within 1e-6 of the grid, so truncation
   would read a price just below the grid one tick low (pinned).

## 4. What each test pins

tests/test_k8_members_tables.py (31 cases): source sha256s (calendar modules, rules/sessions.py, the
release calendar 839f2437...); the modules are exactly the generator's output; static check on both
modules; per group, the full sessions equal an independent recomputation (EC-CAL trade date, no halt, F
15:08 on every K8 root, roots agree) and the research counts 303/304/304/304/304; NOT_FULL lists every
other weekday with a reason of the right kind; early halts and closures (2025-11-28, 12-24, 12-25, 11-27)
are not full, 2025-07-03 is an equity halt only; R-1b-3 (2026-06-01 crypto); the member tuples are the
sorted intersections with research counts 303/304/303 and 54 Mondays; the earlier-cluster cross-check
(section 2 table); previous_dates (strictly before d, oldest first, fewer at the start, k = 0, and over
FLIGHT_DATES around 2025-11-28); GUARD_INSTANTS per root recomputed from the JSON with the research
counts; R-1b-1's two WPSR rows; GUARD_ROWS unique and sorted; in_guard edges (R and R + 60 s guarded,
R + 120 s - 1 ns guarded, R + 120 s, R - 60 s and R - 1 ns not, 0 not, MES raises); the A3 fact (MGC
guards on the flight grid are the 10 FOMC 13:00 CT dates; 13:00 and 13:01 guarded, 12:59 and 13:05 not;
the day before not).

tests/test_k8_members_flight.py (direct calls): static check of flight.py and both tables; names, legs,
factories, variant check; trading_windows; size = frozen q_c; freeze and verify under tmp_path (ordinals
1 and 2); decision times 08:35..14:55, none at 15:00; k = 1 reads 08:29 and 08:34 (08:29 missing: no
trigger; an 08:30 bar is not the start bar); k = 77 triggers at 14:54, a 14:59 bar is no block; blocks
2, 30, 54, 76 trigger at their own bars; block_return and c6 > 0; exact compare beyond float; r_k equal to
Q in another form triggers; an MES id change inside a block (no trigger) and later blocks trigger; ids
compared within MES only; bars whose trade_date is not their CT date are no block bars (with control);
threshold: n 1,199 none, 1,200 m 6, 1,201 m 7, 1,400 m 7, 1,401 m 8, 1,540 m 8, duplicates counted,
order independent; the member at n = 1,199 (no trade), 1,200, 1,201, 1,540, with duplicate reference
values, and with undefined reference computations excluded; r_k < 0 required at Q = 0 and at Q > 0;
warm-up (the run's 20th eligible date does not trade, the 21st does); fewer than 20 reference dates at
the table's start (2019) does not trade; ticks round near-grid floats; reference dates are FLIGHT_DATES
(2025-11-28 skipped as a reference and as d); d's own values never enter Q(d) (a value whose trigger a
guard skipped does not move Q) but enter Q(d + 1).

tests/test_k8_members_flight_exits.py (direct calls): only the first trigger enters even when refused; no
second entry while long or after the exit; the next date enters again; no entry while pending; C6 on
FOMC 2025-06-18 (13:00 skipped, 13:05 enters; 13:00 alone: no trade); a non-FOMC 13:00 trigger enters; a
skipped trigger with a missing entry bar does not end the day; the guard edges on t_k with synthetic
instants (R = t - 1 min and R = t skip; R = t - 2 min and R = t + 1 min enter); C6 reads MGC's instants
only; a missing entry bar ends the day; an entry bar of another trade date counts as missing; an MES bar
absent at t_k - 1 and present at t_k is never used (and the next block is undefined, the one after
triggers); no forward fill of an earlier MES close; H30 exit at T_e + 29; HEOD at 15:04; the H30 cap
(entries at 14:30, 14:35, 14:40, 14:55 exit at 14:59, 15:04, 15:04, 15:04); a missing MGC bar at t_k
moves T_e and the H30 exit; missing exit bars (H30 and HEOD, one and two or three missing); a refused exit
is resent and a pending one not duplicated; an engine-closed position gets no exit; T_e resets when flat;
the last fill is 15:05 for both variants; no entry from any view after 14:54; never an MES intent.

tests/test_k8_members_flight_engine.py (run_engine, frozen engine): H30 fills buy 08:45 and sell 09:15;
HEOD buy 08:45 and sell 15:05, MGC only; an MGC bar missing at 08:45 fills at 08:46 and exits at 09:16;
D11.5: with the MES bar at 08:44 missing the member sends nothing, and a scripted MGC open there is refused
`engine_leg_missing_bar`; V16(a) end to end: an MES-only roll blackout through screening.stage_e_align.
member_window (as the runner builds the rules) removes DAY from the window (roll_blackout_any_leg) and the
member's intent is refused `engine_not_a_window_date`, no fill; with DAY kept as a window date but in the
blackout union the engine names `engine_roll_blackout`; control without a blackout fills; fresh state per
factory call.

## 5. Mutants

Method: each mutant changes one literal, time, comparison or rule line. Module mutants (flight.py,
_releases.py, _calendar.py) were injected by a pytest plugin in my scratch folder (the mutated source is
compiled under the real path and installed in sys.modules before any test imports it), so the shared
table files coder B imports were never modified on disk; a no-op injection passes all 108 tests.
Generator mutants were applied in place and restored from a pristine copy (sha256 checked after the run).
Tests run per mutant: the four K8 test files (generator mutants: the tables test). First full run: 87
mutants, 4 survived (F29 filing non-FLIGHT dates: equivalent, so the filter was removed from flight.py;
F36 no 20-date count: a real gap, test added for the table's start; F60 truncating ticks: a real gap,
test added; R08 was a badly built mutant, replaced). A check of the table found one test that
passed vacuously under F06 (a_bar_at_0830_is_not_the_start_bar_of_k1: with the start bar moved,
every reference value is undefined, so no trade either way); it now carries a positive control.
Final run, on the final test files: 87 mutants, 87 killed, 0 survived.

| Id | File | Mutant | Result | Tests failing: count; the two that kill fewest mutants overall |
|---|---|---|---|---|
| F01 | flight | block clock starts 08:31 | killed | 56; decision_times_are_0835_to_1455_every_5_minutes, trading_windows_are_the_s0_12_intervals |
| F02 | flight | 4-minute blocks | killed | 56; decision_times_are_0835_to_1455_every_5_minutes, trading_windows_are_the_s0_12_intervals |
| F03 | flight | 78 blocks (a block at 15:00) | killed | 4; decision_times_are_0835_to_1455_every_5_minutes, no_entry_from_a_view_after_1454 |
| F04 | flight | 76 blocks (no 14:55) | killed | 4; decision_times_are_0835_to_1455_every_5_minutes, trading_windows_are_the_s0_12_intervals |
| F05 | flight | end bar t_k - 2 | killed | 55; trading_windows_are_the_s0_12_intervals, a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a |
| F06 | flight | start bar t_k - 5 | killed | 55; trading_windows_are_the_s0_12_intervals, a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a |
| F07 | flight | start bar t_k - 7 | killed | 55; trading_windows_are_the_s0_12_intervals, a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a |
| F08 | flight | 19 reference dates | killed | 52; no_forward_fill_of_an_earlier_mes_close, no_intent_on_mes_ever |
| F09 | flight | 21 reference dates | killed | 51; no_forward_fill_of_an_earlier_mes_close, no_intent_on_mes_ever |
| F10 | flight | n >= 1,201 | killed | 3; m_is_ceil_of_n_over_200[1200-6], threshold_m_and_the_value_floor |
| F11 | flight | n >= 1,199 | killed | 2; threshold_m_and_the_value_floor, member_n_1199_is_no_trade_and_n_1200_trades |
| F12 | flight | m = ceil(n/199) | killed | 4; m_is_ceil_of_n_over_200[1400-7], m_is_ceil_of_n_over_200[1200-6] |
| F13 | flight | m = ceil(n/201) | killed | 4; m_is_ceil_of_n_over_200[1201-7], m_is_ceil_of_n_over_200[1401-8] |
| F14 | flight | m = floor(n/200) | killed | 11; m_is_ceil_of_n_over_200[1540-8], threshold_counts_duplicates |
| F15 | flight | m = floor(n/200) + 1 | killed | 4; m_is_ceil_of_n_over_200[1400-7], m_is_ceil_of_n_over_200[1200-6] |
| F16 | flight | the (m+1)-th smallest | killed | 11; m_is_ceil_of_n_over_200[1540-8], threshold_counts_duplicates |
| F17 | flight | n > 1,200 required | killed | 3; m_is_ceil_of_n_over_200[1200-6], threshold_m_and_the_value_floor |
| F18 | flight | H30 intent T_e + 30 | killed | 8; an_mgc_bar_missing_at_tk_fills_later_and_h30_counts_from_the_fill, h30_fills_mgc_at_the_tk_open_and_exits_at_te_plus_30 |
| F19 | flight | H30 intent T_e + 28 | killed | 11; a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing0-555], a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing1-557] |
| F20 | flight | exit bar 15:05 | killed | 6; trading_windows_are_the_s0_12_intervals, heod_fills_mgc_at_the_tk_open_and_exits_at_1505 |
| F21 | flight | exit bar 15:03 | killed | 9; trading_windows_are_the_s0_12_intervals, a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[HEOD-missing2-905] |
| F22 | flight | float compare | killed | 1; compare_and_trigger_are_exact_beyond_float |
| F23 | flight | compare reversed | killed | 62; compare_and_trigger_are_exact_beyond_float, m_is_ceil_of_n_over_200[1540-8] |
| F24 | flight | c6 = 0 allowed | killed | 1; block_return_is_the_tick_ratio_and_needs_c6_positive |
| F25 | flight | r over c1 | killed | 1; block_return_is_the_tick_ratio_and_needs_c6_positive |
| F26 | flight | r <= 0 triggers | killed | 2; a_positive_q_never_triggers_a_non_negative_r, trigger_needs_r_negative_even_at_or_below_q |
| F27 | flight | no r < 0 condition | killed | 2; a_positive_q_never_triggers_a_non_negative_r, trigger_needs_r_negative_even_at_or_below_q |
| F28 | flight | r < Q strict | killed | 7; r_equal_to_q_in_another_form_triggers, a_non_full_date_is_skipped_as_a_reference_and_as_d |
| F29 | flight | a filed date keeps no values | killed | 54; a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a, the_engine_names_the_roll_blackout_when_d_is_a_window_date |
| F30 | flight | prune the oldest reference | killed | 3; member_counts_duplicate_reference_values, member_m_at_1201_and_1540 |
| F31 | flight | no CT-date check on MES | killed | 1; a_bar_whose_trade_date_is_not_its_ct_date_is_not_a_block_bar |
| F32 | flight | no instrument guard | killed | 2; an_mes_roll_inside_a_block_is_no_trigger_and_later_blocks_trigger, undefined_reference_computations_are_not_values |
| F33 | flight | d need not be a FLIGHT date | killed | 1; a_non_full_date_is_skipped_as_a_reference_and_as_d |
| F34 | flight | warm-up one date longer | killed | 54; a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a, the_engine_names_the_roll_blackout_when_d_is_a_window_date |
| F35 | flight | no warm-up | killed | 1; warm_up_the_20th_date_does_not_trade_and_the_21st_does |
| F36 | flight | no 20-date count | killed | 1; fewer_than_20_reference_dates_at_the_tables_start_is_no_trade |
| F37 | flight | C6 tests the entry bar minute | killed | 5; c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[658-True], c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[660-False] |
| F38 | flight | C6 tests t_k + 1 | killed | 2; c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[661-True], c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[659-False] |
| F39 | flight | no C6 | killed | 5; c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[659-False], c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[660-False] |
| F40 | flight | a C6 skip uses the day's entry | killed | 5; c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[659-False], c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[660-False] |
| F41 | flight | a missing entry bar does not end the day | killed | 2; a_missing_entry_bar_at_the_first_trigger_ends_the_day, an_entry_bar_of_another_trade_date_counts_as_missing |
| F42 | flight | entry bar trade date unchecked | killed | 1; an_entry_bar_of_another_trade_date_counts_as_missing |
| F43 | flight | entry while pending | killed | 1; no_entry_while_an_order_is_pending_on_mgc |
| F44 | flight | sells | killed | 51; control_without_a_blackout_the_runner_rules_fill, warm_up_the_20th_date_does_not_trade_and_the_21st_does |
| F45 | flight | q_c + 1 | killed | 49; control_without_a_blackout_the_runner_rules_fill, warm_up_the_20th_date_does_not_trade_and_the_21st_does |
| F46 | flight | every trigger enters | killed | 7; a_missing_entry_bar_at_the_first_trigger_ends_the_day, an_entry_bar_of_another_trade_date_counts_as_missing |
| F47 | flight | HEOD exits like H30 | killed | 5; an_engine_closed_position_gets_no_exit, a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[HEOD-missing2-905] |
| F48 | flight | H30 max not min | killed | 13; a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing0-555], a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing1-557] |
| F49 | flight | H30 uncapped | killed | 3; h30_exit_is_capped_at_1504[74-904], the_last_fill_is_1505_for_both_variants |
| F50 | flight | exit while pending | killed | 2; a_refused_exit_is_resent_and_a_pending_exit_is_not_duplicated, a_second_trigger_while_long_and_after_the_exit_does_nothing |
| F51 | flight | exit one bar late | killed | 14; h30_exit_is_capped_at_1504[73-904], heod_fills_mgc_at_the_tk_open_and_exits_at_1505 |
| F52 | flight | T_e one minute late | killed | 8; an_mgc_bar_missing_at_tk_fills_later_and_h30_counts_from_the_fill, h30_fills_mgc_at_the_tk_open_and_exits_at_te_plus_30 |
| F53 | flight | T_e not reset when flat | killed | 1; t_e_resets_when_flat |
| F54 | flight | first day = every day | killed | 54; a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a, the_engine_names_the_roll_blackout_when_d_is_a_window_date |
| F55 | flight | exit side reversed | killed | 18; a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing0-555], a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing1-557] |
| F56 | flight | exit quantity + 1 | killed | 18; a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing0-555], a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing1-557] |
| F57 | flight | MGC window ends 15:05 | killed | 1; trading_windows_are_the_s0_12_intervals |
| F58 | flight | MES window ends 14:56 | killed | 1; trading_windows_are_the_s0_12_intervals |
| F59 | flight | only negative r recorded | killed | 54; a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a, the_engine_names_the_roll_blackout_when_d_is_a_window_date |
| F60 | flight | ticks truncated, not rounded | killed | 1; ticks_round_a_near_grid_float_to_the_nearest_tick |
| F61 | flight | label order | killed | 1; declarations_names_legs_and_factories |
| F62 | flight | signal leg first | killed | 1; declarations_names_legs_and_factories |
| F63 | flight | day flag never resets | killed | 1; the_next_date_enters_again |
| F64 | flight | Q computed once per run | killed | 54; a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a, the_engine_names_the_roll_blackout_when_d_is_a_window_date |
| F65 | flight | exit one bar early | killed | 18; a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing0-555], a_missing_exit_bar_sends_the_exit_on_the_first_later_bar[H30-missing1-557] |
| F66 | flight | any variant accepted | killed | 1; declarations_names_legs_and_factories |
| F67 | flight | history pruned to one date | killed | 54; a_roll_blackout_of_the_signal_leg_only_blocks_the_entry_v16a, the_engine_names_the_roll_blackout_when_d_is_a_window_date |
| R01 | _releases | R itself not guarded | killed | 6; mgc_guards_on_the_flight_fill_grid_are_the_fomc_1300_dates, in_guard_edges |
| R02 | _releases | R + 120 s guarded | killed | 2; in_guard_edges, c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[658-True] |
| R03 | _releases | 1-minute guard | killed | 4; releases_source_is_the_frozen_calendar, mgc_guards_on_the_flight_fill_grid_are_the_fomc_1300_dates |
| R04 | _releases | 3-minute guard | killed | 3; releases_source_is_the_frozen_calendar, in_guard_edges |
| R05 | _releases | lo = 0 wraps to the last instant | killed | 2; in_guard_edges, c6_tests_the_fill_minute_t_k_against_r_and_r_plus_2_min[661-True] |
| R06 | _releases | FOMC-2025-06-18 drops MGC | killed | 4; guard_instants_are_every_calendar_row_naming_the_root[MGC], mgc_guards_on_the_flight_fill_grid_are_the_fomc_1300_dates |
| R07 | _releases | WPSR-2026-05-28 dropped (an E.4 drop applied, R-1b-1) | killed | 3; guard_rows_are_unique_and_name_only_guard_roots, no_correction_the_e4_dropped_wpsr_rows_stay_in_r_1b_1 |
| R08 | _releases | a row guards its first root only | killed | 2; guard_instants_are_every_calendar_row_naming_the_root[MNQ], guard_instants_are_every_calendar_row_naming_the_root[6C] |
| C01 | _calendar | previous_dates includes d | killed | 16; a_missing_mes_bar_at_tk_minus_1_the_engine_refuses_and_the_member_never_asks, previous_dates_are_the_k_most_recent_strictly_before_d |
| C02 | _calendar | k - 1 dates | killed | 62; no_forward_fill_of_an_earlier_mes_close, no_intent_on_mes_ever |
| C03 | _calendar | newest first | killed | 57; a_missing_mes_bar_at_tk_minus_1_the_engine_refuses_and_the_member_never_asks, previous_dates_are_the_k_most_recent_strictly_before_d |
| C04 | _calendar | Saturdays listed | killed | 13; full_sessions_are_every_ec_cal_trade_date_with_no_halt_and_f_1508[crypto], full_sessions_are_every_ec_cal_trade_date_with_no_halt_and_f_1508[energy] |
| C05 | _calendar | 2025-11-28 equity halt row dropped | killed | 4; not_full_lists_every_other_weekday_with_a_reason[equity], an_early_halt_and_a_closure_are_not_full_sessions |
| C06 | _calendar | FLIGHT_DATES a union | killed | 1; member_dates_are_the_sorted_intersections |
| C07 | _calendar | metals = equity | killed | 3; an_early_halt_and_a_closure_are_not_full_sessions, full_sessions_are_every_ec_cal_trade_date_with_no_halt_and_f_1508[metals] |
| C08 | _calendar | full = not full | killed | 68; a_delayed_crypto_start_is_a_full_session_r_1b_3, full_sessions_are_every_ec_cal_trade_date_with_no_halt_and_f_1508[crypto] |
| G01 | generator | generator F 15:09 | killed | 1; the_modules_are_exactly_the_generators_output |
| G02 | generator | equity F checked on MES only | killed | 1; the_modules_are_exactly_the_generators_output |
| G03 | generator | range ends 2026-06-18 | killed | 1; the_modules_are_exactly_the_generators_output |
| G04 | generator | G17 rows left out | killed | 1; the_modules_are_exactly_the_generators_output |

The full per-mutant list of failing tests is in the scratch file mutants.json (session scratchpad,
coderA/), with one pytest log per mutant under coderA/mutlogs/.

## 6. Commands and results

- `uv run python reports/stage_e9_briefs/gen_k8_tables.py` (PYTHONPYCACHEPREFIX set to coderA/pyc): wrote
  _calendar.py (573 lines) and _releases.py (830 lines); every spec assertion held.
- `uv run pytest -q tests/test_k8_members_tables.py tests/test_k8_members_flight.py
  tests/test_k8_members_flight_exits.py tests/test_k8_members_flight_engine.py
  tests/test_stage_e_template.py tests/test_stage_e_freeze.py` (PYTHONPYCACHEPREFIX unset), 23:08 PDT:
  157 passed in 2.41 s.
- Static check (screening.stage_e_freeze.check_member_source, cluster "K8"): [] for flight.py,
  _calendar.py, _releases.py, __init__.py.
- `uv run ruff check` on my eight files: clean. (ruff reports E501 at tests/test_k8_members_oilcad.py:238,
  coder B's file, not mine.)
- Mutation driver (scratch coderA/mutate.py, plugin coderA/mutplugin/k8mut.py), nice 10, sequential:
  87 mutants, 87 killed.
- Full suite not run (the lead runs it).

## 7. For the lead

No open question blocks a trade. Points to note or rule on:
1. The earlier-cluster differences in section 2 (K3 FX 14 dates under the pre-E.5 sessions.py; K4 and K5
   2024-07-03 without the F test). Confirmation window only; no K8 change made.
2. Implementation details 1-4 in section 3 (exact pairs instead of fractions.Fraction, which the freeze
   does not allow; the first bar over both legs; S0.6's unpinned "day used" case, impossible on real
   bars; rounding to the nearest tick).
3. previous_dates returns oldest first; coder B should rely on that order. _calendar.py's sha256 changed
   once at 22:48 PDT (behaviour unchanged).
4. K8-L-08's logged edge (an entry fill pushed past t_k into a guard by a missing MGC bar is deferred by
   the engine, not skipped) is as the spec states; the member tests the scheduled t_k only. Not tested
   beyond that.
