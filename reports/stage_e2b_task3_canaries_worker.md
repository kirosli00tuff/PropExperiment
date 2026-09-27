# Stage E.2b Task 3 (leakage canaries): CanaryCoder-OpusXHigh worker report

Worker: CanaryCoder-OpusXHigh (worker-xhigh, Opus 5.5, xhigh). Started about 14:36 PDT,
stopped at about 15:07 PDT on the session usage limit, resumed 16:43 PDT, report written 16:53 PDT,
2026-09-26. Status: DONE. No BLOCKING finding: every canary fails on its planted leak.
One RUNNER FINDING (C-1): a canary that the current engine fails, recorded as a strict xfail.

## 0. Findings for the lead (read first)

- **C-1 (runner change needed; I did not edit the runner).** The engine can fill AT a bar inside a
  scheduled closure. Case: a vendor gap from just before F to the session's close minute, where a
  closure bar (lead ruling L-3: booked to the session it closes) is the leg's next bar while the
  member holds a position. `_Run.fill_pending_at_open`, `try_passive` and `check_mll` have no
  closure check, so:
  (a) a member exit pending at that bar fills at the closure print;
  (b) the forced flatten pending at that bar fills at the closure print;
  (c) with nothing pending, the MLL check reads the closure bar's range and liquidates at it.
  On an EARLY-CLOSE date the D8 cost table has a bucket at that minute (buckets are by CT minute
  of day), so all three fill silently: 24 of 24 cases (8 groups x 3), for example rates
  2025-05-26 12:00 CT, equity 2025-07-03 12:15 CT, grains 2025-11-28 12:05 CT. The test
  `test_a_closure_bar_after_a_vendor_gap_on_an_early_close_date_is_never_traded` carries
  `xfail(strict=True, raises=AssertionError, reason=FINDING_C1)`, so the suite stays green, the
  24 cases are listed as xfailed, and the day the engine refuses such fills the strict xfail
  turns into a failure that forces the marker's removal. If you want a hard failure instead,
  delete the one marker line. A ruling is also needed on WHERE a forced flatten should fill when
  the leg's next bar is a closure print: at the prior bar's close, as the session-end path does,
  or at the next open bar.
- **C-2 (accidental defence).** On a REGULAR date the same three scenarios do not trade, but only
  because the D8 table has no bucket at closure minutes: the fill raises `CostLookupError` (a
  `FrozenInputError`). `screening/stage_e_runner.py` catches `EngineRefusedCase`, `RunnerRefusal`
  and `StageEBarRefusal` only, so in a real run this would abort `screen_cluster` rather than
  record a named refusal. The regular-date canary accepts the raise as "refused" and says so in
  its docstring. A named engine check (C-1's fix) would cover both cases.
- **C-3 (flagging).** An intent decided on a closure bar is refused by name
  (`engine_scheduled_closure`, counted in `counters`). When the builder did not flag the bar,
  rules/sessions.py still refuses the intent (`engine_flatten_window`). Nothing else records that
  a closure bar was seen: the runner's record has no closure count.
- **C-4 (ML wrapper, for information).** The wrapper's lead-history filter
  (`_History.bars(closed_by_ns=t)`) is redundant with `ml_route.rows._fill_f16`, which reads
  "the latest lead bar closing <= t" by searchsorted, and with the lead's Daily, which reads
  earlier dates only. With the filter switched off AND every lead bar (a planted future
  included) handed over early, every feature row is unchanged. This is two defences, not a
  leak, and it means "filter off" cannot serve as the positive control. The ML canary's
  cross-product positive control is a MISALIGNED lead (its bars stamped 2 minutes early), which
  it catches. Similarly, a one-bar engine peek gives the wrapper nothing new, because it reads
  only bars closed before its decision bar. The engine positive control is therefore a two-bar
  peek, which it catches.
- **Not a finding, a reading:** DCB-only products (rates, FX, energy, metals, crypto) consult no
  settlement value at all (D9.7 applies to hard-limit products only, ruling L-13). For them the
  settlement canary asserts that the engine consults none (a spy on `prior_settlement`) and that
  a planted settlement changes nothing. If D9.7 is ever extended to them, that assertion fails
  and demands the full canary.

## 1. Files

Created (test files only; nothing else touched):
- `tests/_stage_e_canary_kit.py` (about 840 lines). This is the helper module:
  - planting: `plant_jumps`, `plant_future`, `plant_one_bar`, `plant_bar`, `shift_leg`,
    `gap_before`;
  - canary members: `CanaryReader`, `ReactiveMember` (honest), `FramePeekingMember` (leaky on
    purpose), `ScriptMember`, `HindsightReader`, `ClosureTrader`, `ViewSpy`, `TripwireSpy`,
    `MLSpy`, `EarlyLeadMember`;
  - DELIBERATELY BROKEN positive controls: `SameBarFillRun`, `LookaheadViewRules` (peek k bars
    or backward fill), `SameDaySettlementRules`, `ClosureBlindRules`, `LookaheadReleaseCalendar`,
    `TripwireRules(eager=True)`;
  - scoring: `leg_trips` and `jump_score`, which reuse sim.leakage_canaries' `score_canary`,
    `leak_canary_passes` and `edge_detected` unchanged; `ledger_until`, `ledger_after`,
    `views_until`, `closure_trades`, `tripwire_violations`;
  - product and calendar helpers: `GROUP_PRODUCTS`, `DAYS`, `frame_bounds`, `mark_minutes`,
    `closure_booking` (the builder's own `assign_trade_dates` with L-3), `session_end_ts`,
    `rules_for`, `release_calendar`, `settlement_proxies` (the engine's own `_Settlement`).
- `tests/test_stage_e_canaries.py` (about 830 lines, 208 tests). This is the file name that
  MLTestCoder's `freeze_scope.required_files` expects.

Not touched: `tests/test_leakage_canaries.py`, `sim/leakage_canaries.py`, `screening/*`,
`ml_route/*`, `strategy/*`, `rules/*`, `data/*`, and every frozen file. No real bar parquet was
opened: all data is synthetic (`tests/_stage_e_synthetic.product_frame`,
`ml_route.synthetic.synthetic_bars`). The E.2a hashed cost, vehicle and epsilon tables are read
through `screening.stage_e_frozen.leg_inputs`, as the runner does.

## 2. What runs through the runner, and the products

Every canary drives the generalized engine through its own lower-level functions: `run_engine`,
`StageERules`, `product_bar_iterator` and the frozen `leg_inputs` (runner report section 8). The
mutants subclass the engine's `_Run` or `StageERules`; the real classes are never edited. There
is one traded vehicle per group:

| group | root | why |
|---|---|---|
| equity | MNQ | hard-limit (D9.7 applies) |
| rates | ZN | fractional-cent tick value (Fraction money) |
| fx | 6E | DCB only |
| energy | MCL | DCB only |
| metals | MGC | DCB only |
| grains | ZC | hard-limit, cent-quoted vendor grid, grain F 13:18 |
| livestock | LE | hard-limit, 08:30 open, F 13:03 |
| crypto | MBT | DCB only |

The trade dates are 15 regular dates, 2025-05-05 to 2025-05-23. `check_days` asserts that every
group has no holiday and a regular F on them. Each synthetic frame spans the product's D6 day
session from O_X to F + 2 min.

## 3. Tests: 208 in tests/test_stage_e_canaries.py (184 pass, 24 strict xfail = C-1)

Each canary is paired with a positive control that it must flag ("caught" = the canary's own
check fails on it).

**Planting checks**
- `test_planted_jumps_stay_on_the_vendor_grid_and_never_mutate_the_input` (8): the input frame is
  unchanged. The jump sits inside the marked bar and is carried to the next open. Every
  latency marker is one minute before its leak marker. `product_bar_iterator` accepts the
  planted frame.
- `test_planted_future_changes_only_bars_after_the_cutoff` (8): bars at or before the cutoff are
  bit-identical.

**(1a) Jump canary**, per group. This is sim/leakage_canaries' recipe and thresholds:
JUMP_TICKS = 16, markers every 20 minutes, `leak_canary_passes`, `edge_detected`. One Stage E
change: the reader holds 2 minutes (the D9.3b minimum hold), so the jump reverts inside the bar
6 minutes later. That is after every exit, and it keeps ZC and LE inside their D9.7 stop levels.
- `test_real_engine_shows_no_edge_from_a_jump_planted_inside_the_decision_bar` (8): passes on the
  real engine, with at least 150 trades.
- `test_the_jump_canary_catches_a_leaky_engine` (16): the same-bar-fill engine and the
  peek-next-bar engine are both caught (the leak check fails, and edge_detected with hit rate
  > 0.9).
- `test_latency_control_is_captured_by_the_real_engine` (8): a marker on the bar before the jump
  is captured. This rules out an engine that passes only because it fills late.

**(1b) Perturbation canary**, per group, 2 cutoffs. The future after the cutoff is mirrored and
moved 40 ticks against the clean next move, so the first planted close always moves the other
way.
- `test_an_honest_member_is_unaffected_by_planted_future_bars` (8): the views handed to the
  member and every ledger event up to the cutoff are identical. There are at least 10 fills
  before the cutoff. The ledger after the cutoff differs, so the plant is not inert.
- `test_a_member_that_peeks_at_the_next_bar_is_caught` (8): the member reads its data frame one
  bar ahead. The engine hands both runs identical views, and the ledger is equal up to
  cutoff - 1 min. At the cutoff it differs, so the member is caught.

**(2) Values before their availability**, per group.
- `test_a_planted_settlement_is_not_read_before_its_trade_date_ends` (8):
  - The plant: D1's settlement-window bar moved 1.25 x the D9.7 stop distance.
  - Nothing on D0 or D1 changes.
  - Hard-limit products: every settlement consulted is the prior date's (spy). On D2 the planted
    value refuses entries (`price_limit_zone_no_entry`) in the planted run only.
  - DCB products: no settlement is consulted, and the whole ledger is unchanged.
- `test_a_same_day_settlement_rule_set_is_caught` (3: equity, grains, livestock): a rule set
  whose D9.7 reads the current date's settlement (hindsight proxies of the planted frame)
  diverges before D1's settlement window.
- `test_a_release_never_reaches_a_fill_before_its_instant` (8), with a release at 10:00 CT:
  - the 4 fills before the release equal the no-release run's, with no event window;
  - from the release, the D9.5a guard defers the fill (to 10:02 or later) and the event cost
    applies;
  - after the 30-minute window, the fills and costs are the clean run's again.
- `test_an_off_by_one_release_lookup_is_caught` (8): a lookup of "the first release at or after"
  changes the fills before the release.
- `test_a_hindsight_flag_never_reaches_the_member` (8): with vendor_degraded_day=True on D1, the
  member sees only False, makes no fill, and the ledger equals the unflagged run's.
- `test_an_engine_that_does_not_mask_the_hindsight_flag_is_caught` (8): the real engine switch
  `mask_hindsight_fields=False` makes the flag visible and trades on it.

**(3) A bar inside a scheduled closure**, per group. The planted minute is verified against the
group calendar (`assign_trade_dates`, L-3): 16:30 CT (equity, rates, FX, energy, metals, crypto),
08:00 CT (the grain pause) and 14:00 CT (livestock).
- `test_an_intent_on_a_flagged_closure_bar_is_refused_by_name` (8): refused as
  `engine_scheduled_closure`, counted once, and nothing traded on it.
- `test_an_unflagged_closure_bar_is_still_refused_by_the_session_rules` (8): with every flag
  False (a builder that flagged nothing), rules/sessions.py refuses it (`engine_flatten_window`).
- `test_a_closure_blind_rule_set_is_caught` (8): a rule set that skips the closure and session
  checks on closure bars accepts the intent and trades, and the canary catches it.
- `test_a_closure_bar_after_a_vendor_gap_on_a_regular_date_is_never_traded` (24): passes today
  through C-2's CostLookupError.
- `test_a_closure_bar_after_a_vendor_gap_on_an_early_close_date_is_never_traded` (24): strict
  xfail, finding C-1. Setup preconditions raise `CanaryPrecondition`, not AssertionError, so only
  the canary's own assertion can satisfy the xfail. I checked that all 24 fail on exactly that
  assertion: 8 strategy fills, 8 forced-flatten fills and 8 MLL liquidations at the closure
  print.

**Cross-product.** MNQ (equity) is traded; ZN (rates) is read as a signal leg, on two group
calendars and one UTC grid.
- `test_a_jump_planted_in_the_signal_leg_gives_the_traded_leg_no_edge` (2): the real engine, and
  the signal leg with a gap before every marked bar. The plant is a common shock in both legs,
  with the marker on the ZN bar.
- `test_the_cross_product_jump_canary_catches_a_leaking_signal_leg` (3): an engine that peeks
  only the signal leg; the signal leg stamped one minute early (misaligned); the signal leg's gap
  filled with the NEXT bar (backfilled). All three are caught.
- `test_cross_product_latency_control_is_captured` (1).
- `test_a_view_level_backward_fill_is_neutralized_by_the_missing_bar_rule` (1): defence in
  depth. A member shown ZN's next bar where ZN has none wants to open, and D11.5 refuses every
  such opening (285 `engine_leg_missing_bar`). No edge results.
- `test_a_planted_future_in_one_leg_changes_no_decision_on_the_other` (4): {signal leg, both
  traded} x {whole future planted, one bar planted}, 2 cutoffs each. The MNQ views and ledger up
  to the cutoff are identical, and the plant is visible or acted on later.
- `test_a_member_that_reads_the_other_legs_next_bar_is_caught` (1).

**Tripwire**
- `test_the_engine_never_pulls_a_bar_before_the_minute_it_decides` (9: 8 groups + cross-product
  with a thin signal leg): at every member call, each leg's feed has handed over exactly the bars
  opening at or before that minute.
- `test_the_tripwire_catches_a_feed_that_reads_ahead` (2): an eager feed is caught.

**ML rule wrapper (M7.7 through the Stage E engine).** This uses MLTestCoder's single-exposure
path (`exposure_plans`, `build_exposure_member`, lead ruling OC-P): a K1 rule, the M2K exposure,
legs M2K traded plus RTY and NQ as signals, synthetic 2019-05-06..2019-12-04. The wrapper's first
complete feature row comes on the 141st date, so there are 64 complete rows before cutoff A.
Cutoff A is 10:58 CT on the 145th date; cutoff B is 11:00 CT on the same date.
- `test_the_ml_wrapper_is_unaffected_by_planted_future_bars` (2: own price path, F16 lead): every
  feature row, Decision and ledger event emitted by cutoff A is identical, with at least 40
  complete rows, at least 10 fired decisions and at least 10 fills. The 11:00 features differ, so
  the plant is not inert.
- `test_the_ml_wrapper_ignores_lead_bars_handed_over_early` (1): every lead bar, the planted
  future included, is handed over before the run. The whole run's features, decisions and ledger
  equal the normal handover's.
- `test_the_ml_lead_stays_aligned_even_without_the_wrappers_lead_filter` (1): defence in depth
  (C-4).
- `test_the_ml_canary_catches_a_misaligned_lead` (1): the honest pipeline is identical up to
  cutoff B. A lead stamped 2 minutes early lets the 11:00 decision read the planted 11:01 bar, and
  the canary catches it.
- `test_the_ml_canary_catches_an_engine_that_hands_the_wrapper_a_later_bar` (1): a two-bar peek
  is caught.

Coverage (pytest-cov, the full file): `tests/_stage_e_canary_kit.py` 98% (11 of 522 statements
uncovered, all defensive branches).

## 4. Numbers (trades / mean captured ticks / z / direction hit rate; JUMP_TICKS = 16)

| group | real engine | same-bar fill | peek next bar | latency control |
|---|---|---|---|---|
| equity MNQ | 266 / -0.16 / -1.8 / 0.45 | 266 / +15.85 / +160.8 / 1.00 | same | same |
| rates ZN | 266 / -0.08 / -0.9 / 0.47 | 285 / +16.01 / +165.8 / 1.00 | same | same |
| fx 6E | 268 / -0.05 / -0.5 / 0.49 | 285 / +16.01 / +165.8 / 1.00 | same | same |
| energy MCL | 240 / -0.05 / -0.6 / 0.48 | 240 / +16.05 / +170.9 / 1.00 | same | same |
| metals MGC | 225 / -0.02 / -0.2 / 0.49 | 225 / +16.01 / +147.2 / 1.00 | same | same |
| grains ZC | 183 / +0.03 / +0.2 / 0.50 | 196 / +16.03 / +134.6 / 1.00 | same | same |
| livestock LE | 177 / -0.05 / -0.4 / 0.47 | 182 / +16.03 / +134.3 / 1.00 | same | same |
| crypto MBT | 285 / -0.15 / -1.7 / 0.46 | 285 / +15.88 / +169.7 / 1.00 | same | same |
| cross MNQ<-ZN | 266 / -0.03 / -0.3 / 0.50 | peek ZN, misaligned ZN, backfilled ZN: 266 / +15.99 / +161.5 / 1.00 | | 266 / +15.99 / +161.5 / 1.00 |

"Same" means an identical row: all three leaky routes fill the reader before the jump. Where the
real engine has fewer trades than the mutants, the honest reader lost the account on costs: an
MLL breach followed by `account_not_active` until the restart. On day 1 the hard-limit products
have no prior settlement, so those entries are refused by name.

## 5. Commands run (results)

- `uv run --no-sync pytest -q tests/test_stage_e_canaries.py` (non-ML parts, repeatedly while
  building, about 26 s): final 184 passed and 24 xfailed; C-1 and C-2 surfaced here.
- The full file with coverage, through `reports/stage_e2b_briefs/heavy.sh` (16:44 PDT,
  OMP_NUM_THREADS=4): 182 passed, 2 failed, 24 xfailed in 187 s. The 2 failures were my
  one-bar teeth check: a single planted signal bar is visible but the reactive member was busy.
  I changed that assertion to view level. The rerun of those cases gave 5 passed.
- The ML parts, through heavy.sh (15:05 PDT): 6 passed in 80 s. The slowest single test is 37 s.
- The existing canaries and every Stage E test, through heavy.sh (16:47 to 16:51 PDT):
  `pytest -q tests/test_leakage_canaries.py tests/test_stage_e_*.py`, giving **457 passed,
  24 xfailed** (the xfails are C-1) in 225 s; see section 7.
- `ruff check` on both new files: clean.
- Before the heavy runs about 9.7 GB was available; no job went above 1 GB.

## 6. Readings and deviations

- R-1: the Stage E jump canary uses sim/leakage_canaries' thresholds unchanged. The only changes
  are the 2-minute hold (D9.3b) and the jump reversion after 6 bars, which leaves every exit on
  the shifted level, so the arithmetic of the test is unchanged.
- R-2: "a member that peeks ahead" is modelled as a member holding its data frame. The engine
  cannot stop that by construction, so the perturbation canary is what catches it. Engine-side
  peeks are caught by the jump canary.
- R-3: "a settlement or release value visible before its availability time" is covered in three
  ways: settlement (D9.7's proxy), releases (the event window and fill guard lookups) and
  hindsight fields (vendor_degraded_day). The release calendar holds instants only (scheduled and
  known in advance). No release VALUE enters the engine.
- R-4: a raised `CostLookupError` counts as "refused" on regular dates (C-2).
- D-1: the ML canary builds its world with a synthetic release calendar: 10:29 CT on the 131st
  date onward, as in MLTestCoder's adapter test. With only one early release the wrapper produced
  no complete feature row, so this construction is needed.
- D-2: the brief's `tests/test_stage_e_*.py` glob now includes my own file. It ran in the same
  gated run.

## 7. Existing tests (unchanged files)

The gated run covered `tests/test_leakage_canaries.py` (the existing MES canaries, 15) and all
14 `tests/test_stage_e_*.py` files: alignment, canaries (mine), engine_mes_parity, freeze, frozen,
loader, mes_regression, rules, runner, start_dates, stats, stats_power, stats_start and template.
Result: 457 passed, 24 xfailed (all C-1), 0 failed. There was one RuntimeWarning, from
screening/stage_e_stats_power.py:218 in
`test_stage_e_runner.py::test_an_empty_window_supplies_0_days_...`; it is another worker's code
and not a test failure. Every existing canary and runner test passes unchanged.

## 8. Unfinished

Nothing in the brief is unfinished. Open for the lead: C-1 (a runner change plus a ruling on
where a forced flatten fills when the next bar is a closure print) and C-2 (catching
FrozenInputError or a named check).
