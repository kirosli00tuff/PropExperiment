# Stage E.2b Task 1 (runner core): RunnerCoder-OpusXHigh worker report

Worker: RunnerCoder-OpusXHigh (worker-xhigh, Opus 5.5, xhigh). Started 12:43 PDT, report written
13:35 PDT, 2026-09-26. Status: DONE, with the open questions of section 7 (two of them block real
Stage E screening runs by design: the runner refuses by name until they are answered).

## 0. Public interface

```python
# screening/stage_e_runner.py -- the one Stage E screening / confirmation entry
screen_member(cluster: str, label: str, factory: Callable[[], Any] | None,
              legs: Sequence[LegSpec] | None, window: str, *, harness_sha256: str,
              research_root: Path, step2_root: Path, out_dir: Path) -> dict   # the record
screen_cluster(cluster: str, window: str, *, harness_sha256: str, research_root: Path,
               step2_root: Path, out_dir: Path) -> dict          # every frozen member + tiers
main(argv) # python -m screening.stage_e_runner --harness-sha256 SHA --cluster K1
           #   (--member LABEL | --all) --window research|confirmation
           #   --research-root DIR --step2-root DIR --out-dir DIR
WINDOWS = ("research", "confirmation"); START_RULE_PATH = "reports/stage_e_start_rule.json"
extract_trips(result) -> tuple[TripRecord, ...]; trade_rate(result, trips) -> dict
class RunnerRefusal(RuntimeError); class StartRuleMissing(RunnerRefusal)

# screening/stage_e_engine.py -- the generalized engine (sim/engine.py untouched)
run_engine(frames: Mapping[str, DataFrame], member, legs: Sequence[LegSpec], rules) -> EngineResult
iter_minutes(frames, make_bar) -> Iterator[(ts_ns, {root: Bar})]   # shared UTC grid, no ffill
MesRules(table, roll_blackout, slippage_statistic="mean", restart_on_terminal=True, ...)
EngineResult(ledger, final_state, bars_processed, minutes_processed, accounts_started, counters)
Fill / IntentRecord / Cancel / DayClose / AccountStart; EngineInvariantError; EngineRefusedCase

# screening/stage_e_rules.py -- the Stage E constraint set
StageERules(legs: Mapping[str, LegInputs], window_dates: frozenset[date],
            blackout: frozenset[date], releases: ReleaseCalendar)
ReleaseCalendar(by_root, cpi, first, last, sha256, source); load_release_calendar()
release_calendar_from_dict(raw, sha256, source); RELEASE_CALENDAR_PATH =
    "reports/stage_e2b_release_calendar.json" (schema "stage_e_release_calendar/1")
product_bar_iterator(root); STAGE_E_REFUSAL_ORDER; ReleaseCalendarMissing

# screening/stage_e_frozen.py -- hash-checked E.2a tables
load_frozen_tables() -> FrozenTables; leg_inputs(root, *, traded) -> LegInputs
E2A_TABLES (4 tables with recorded sha256); MES_RESEARCH_SHA256; slippage_cents(qty, ticks, tv)

# data/stage_e_bars.py -- bars with trade-date refusals
load_research_leg(root, research_root, *, expected_sha256) -> LegFrame
load_confirmation_leg(root, step2_root, start: date) -> LegFrame   # cuts at S_X
read_leg_dates(root, step2_root, start) -> (dates, blackout)       # no price column read
HoldoutRowRefused, TradeDateUnbookable, TradeDateMismatch, ConfirmationStoreMissing,
ParquetHashMismatch, RollMetadataMismatch (all StageEBarRefusal)

# screening/stage_e_align.py -- D4 windows and D9 coverage
member_window(legs: Mapping[str, LegFrame], store) -> MemberWindow   # UR-1 on research
member_coverage(legs, dates, windows) -> {root: Coverage}; COVERAGE_MIN = 0.95

# screening/stage_e_freeze.py -- per-cluster member code freeze
MemberDecl(label, ordinal, module, factory, legs)
write_cluster_freeze(cluster, members) -> sha256   # reports/stage_e_<k#>_member_freeze.json
load_cluster_freeze(cluster); verify_cluster_code(freeze); resolve_member(freeze, label, factory)
MEMBERS_ROOT = strategy/members  (members live in strategy/members/<k#>/, never strategy/stage_e/)

# strategy/stage_e/interface.py -- the member contract
LegSpec(root, traded); MinuteView(ts_event_ns, bars); MemberAccountView(...);
LegIntent(root, side, quantity, ts_utc, limit_price=None, ttl_bars=None);
TradingInterval(start_ct, end_ct, start_offset_days=0, end_offset_days=0)
leg_market_intent(view, root, side, qty); leg_limit_intent(view, root, side, qty, price, ttl)
StageEMember protocol: name, trading_windows, on_minute(view, account)

# screening/stage_e_mes_regression.py
mes_new_path(label, factory, research_root) -> dict; regression_factory(label)
```

## 1. Files

Created (all new; no existing file was edited):
- screening/stage_e_frozen.py (288 lines), screening/stage_e_engine.py (786),
  screening/stage_e_rules.py (574), screening/stage_e_align.py (145),
  screening/stage_e_freeze.py (200), screening/stage_e_runner.py (456),
  screening/stage_e_mes_regression.py (86), data/stage_e_bars.py (332),
  strategy/stage_e/__init__.py, strategy/stage_e/interface.py (169),
  strategy/stage_e/_template.py (145).
- Tests: tests/_stage_e_synthetic.py (helper), tests/test_stage_e_engine_mes_parity.py,
  tests/test_stage_e_loader.py, tests/test_stage_e_frozen.py, tests/test_stage_e_rules.py,
  tests/test_stage_e_alignment.py, tests/test_stage_e_freeze.py, tests/test_stage_e_runner.py,
  tests/test_stage_e_template.py, tests/test_stage_e_mes_regression.py.

Not touched: screening/runner.py, sim/, rules/, strategy/interface.py, every frozen file,
screening/harness_freeze.py, compute/, other workers' files (git status shows none of them changed
by me). The harness manifest (Task 6) must list the 11 new harness files above.

## 2. How each brief item is met

1. Frozen inputs: stage_e_frozen reads rules/products.py, the cost table, vehicles, sizes and
   epsilon from repository paths fixed as constants and refuses unless each table's sha256 equals
   the recorded value (the four full hashes of the brief). leg_inputs gives tick value (exact
   cents), vendor tick, commission, the D8 bucket table, q_c and the operative eps. The public entry
   takes only cluster, label, factory, legs (checked against the freeze) and a window NAME, plus the
   harness hash and the data and output roots.
2. Bars: data/stage_e_bars books every row by the group calendar (the builder's own
   assign_trade_dates call, L-3 close-minute rule) and refuses the whole leg for any row booked to
   holdout-1, holdout-2, the March 2024 embargo, outside the store's range, unbookable past the
   calendar's coverage, or labelled differently from its booking. The named L-9 test is
   `tests/test_stage_e_loader.py::test_mbt_rows_booked_to_holdout1_trade_date_2026_06_22_are_refused_ruling_L9`.
   Research parquets must match E.2a's recorded sha256 (MES: the pinned aea959a5...6ae0).
   Confirmation: data.step2_store.step2_parquet_path(root, step2_root) (PurchaseCoder2's module,
   now present; tested with the real function), refused by name when the module or file is absent;
   cut at S_X after the whole file is checked.
3. Alignment (D11.5): iter_minutes builds the union UTC minute grid; a leg without a bar is absent
   (None in the member's view), never forward filled; the engine refuses opening exposure at a
   minute where any read leg lacks a bar (engine_leg_missing_bar). D4: member_window = common trade
   dates less the union of every leg's roll blackout; every read leg passes the coverage check.
4. Coverage >= 0.95 per read leg on the member's declared TradingIntervals (expected minutes =
   intervals intersected with the group calendar's open intervals); below it the member is labelled
   coverage_below_0.95 and not run (lead ruling OC-H). Trade-rate floor: the engine refuses (and
   counts) a 21st entry per product per trade date and an exit < 2 full minutes after the last
   opening fill, and skips for the day an entry whose forced exit (F, grain pause) would come within
   2 minutes; labels entries_above_20_per_day, hold_below_2min, mean_holding_below_10min (strings
   from stage_e_stats.D9_LABELS, checked at run time). Labelled members are kept.
5. E.2a carried items: roll blackouts on each group calendar, recomputed from the rolls metadata
   and checked against the file's recorded dates (L-8); vendor-unit ticks via
   Product.vendor_tick_fixed (cent-quoted ZC, ZW, ZS, ZL, HE, LE); flatten from
   rules.sessions.session_state (R-F1, R-F4), united with the bar flags; the event-window cost as
   the largest s_b plus the own bucket's depth term (T12-4, never the table's
   event_window_side_ticks field); the MBT refusal (item 2); the unseen roll: rule UR-1 (below).
6. Series and statistics: trips per leg (flat to flat), the daily series through
   stage_e_stats.daily_series_from_trips (one traded leg) or daily_series_from_leg_dollars (several),
   stage_e_stats.screen (D5), stage_e_stats.power_check(series, cluster, ordinal, supply_days)
   (D4; ordinal from the freeze; supply from the step 2 store's trade dates and blackouts only),
   stage_e_stats.assign_tiers in screen_cluster. ScreenUndefined and PowerCheckUndefined are
   recorded as named statuses and the run continues (lead relay).
7. Template strategy/stage_e/_template.py (a CP2-shaped breakout reading O, C and q_c from the
   frozen tables) and the per-cluster freeze (write once, read-only, every *.py under
   strategy/members/<k#>/ hashed; unlisted, changed or missing files, undeclared labels, other
   factories and other legs refused; the freeze sha256 goes into every record).
8. Entry discipline: screen_member calls harness_freeze.preflight(harness_sha256) as its first
   statement (lead's new signature), writes the returned sha256 into every record; the CLI requires
   --harness-sha256, --research-root, --step2-root and --out-dir; screen_cluster preflights too.
9. MES regressions: section 3.

## 3. MES regression table

Generalized path = data.stage_e_bars.load_research_leg (MES research parquet, sha256-checked, every
row booked by the equity group calendar) + D.1's train-union window (289 dates) + group-calendar roll
blackout + stage_e_engine under MesRules + stage_e_runner.extract_trips. "Recorded" =
reports/stage_d1d_accounting.json (runs and per_trial). All four series (daily_net_usd,
trip_pnls_usd, daily_n_trips, trip_micros) are also tuple-equal, float for float, to the unchanged
screening.runner.screen_candidate on the same window (True for all three trials).

| Trial (class) | Field | Recorded (D.1d) | New path | Equal |
|---|---|---|---|---|
| A-H2 rth close window (buy) (C1) | n_trips | 266 | 266 | yes |
| | net_pnl_usd | 587.95 | 587.95 | yes |
| | p / R | 0.4924812030075188 / 1.128193644654443 | same | yes |
| | daily mean / sd / t | 2.034429 / 64.415517 / 0.5369 | same | yes |
| B-H1 ORB hold 75 (C2) | n_trips | 276 | 276 | yes |
| | net_pnl_usd | -292.95 | -292.95 | yes |
| | p / R | 0.532608695652174 / 0.8568404899916324 | same | yes |
| | daily mean / sd / t | -1.013668 / 121.35494 / -0.142 | same | yes |
| D-H2 inverse-vol sizing (C4; 1 to 5 micros) | n_trips | 276 | 276 | yes |
| | net_pnl_usd | -2320.19 | -2320.19 | yes |
| | p / R | 0.4601449275362319 / 0.8434999096869101 | same | yes |
| | daily mean / sd / t | -8.028339 / 69.528841 / -1.963 | same | yes |

(tests/test_stage_e_mes_regression.py also checks skew, kurtosis and Sharpe to 6 decimals and
blackout_dates_in_window; 7 passed in 72.9 s through heavy.sh.)

## 4. Tests (93 new, all pass)

- test_stage_e_engine_mes_parity.py (9): the generalized engine under MesRules equals sim/engine.py
  fill for fill (15 fields), day for day, intent for intent, final state and account count, on
  synthetic MES bars with random market and limit orders (6 seeds), MLL breaches with restarts,
  sessions ending with no flatten bar plus gaps, and roll-blackout refusals. A mutation (the MLL
  touch rounding swapped) is caught.
- test_stage_e_loader.py (14): forbidden classes; a clean MBT file; the L-9 MBT test (row stamped
  2026-06-19 12:00 CT, labelled 2026-06-19, refused as holdout-1 2026-06-22); MBT rows labelled
  2026-06-22; a row past calendar coverage (unbookable); holdout-2 and embargo rows in the step 2
  store; out-of-store research rows; a label/booking mismatch; a research hash mismatch; grain roll
  blackout on the grain calendar and a disagreeing metadata record (L-8); store absent (module and
  file); the S_X cut and the dates-only reader; caller-given roots; the real step2 path layout.
- test_stage_e_frozen.py (10): recorded hashes; a one-byte change to each of the four tables
  refused; missing table refused; q_c and operative eps for 14 vehicles; non-vehicles only as
  signal legs; exact fractional tick values (ZN 3125/2, ZT 3125/4 cents); commissions (MCL 86,
  ZC 264, MNQ 61 per side); T12-4 event cost; no-bucket time raises; ceil-to-cent slippage.
- test_stage_e_rules.py (19): ZN round trip exact in fractional cents with D8 costs; cent-quoted
  ZC on its vendor grid; energy forced flatten at 15:08 CT; no new position from F; Topstep's
  2025-11-28 close-by (R-F1) moves F; grain overnight position closed at 07:43; entry skipped when
  the forced exit would come within 2 minutes (fill guard pushing to 15:07); event-window cost and
  the 2-minute fill guard (09:30 release -> 09:32 fill); member and volatility caps (ZN 2, MCL 11);
  the 21st entry refused; min hold (exit at 1 minute refused, fills 2 minutes apart); window and
  blackout refusals; signal leg not tradable and second-leg refusal; limit orders fill on
  trade-through at the limit, commission only; D9.7 entry refusal and forced exit with event cost
  (ZC 35-cent limit, 440.00 prior settlement proxy); no proxy -> no entry; a locked exit waits 19
  bars then fills at the first trade-through, and a lock through the session end raises
  EngineRefusedCase; CPI window skip for the day (NQ); StageERules takes no cost or tick argument.
- test_stage_e_alignment.py (10): union grid; the member sees None for a missing bar and never a
  later bar; opening refused when a signal leg lacks a bar, exit allowed; window = common dates less
  every leg's blackout; UR-1 on research only; two stores refused; coverage 30/30, 28/30 (fails),
  29/30 (passes); coverage counts only calendar-open minutes; every read leg needs a window;
  equity signal leg vs grain traded leg (grain has no bar -> no trade).
- test_stage_e_freeze.py (7): written once, read-only, loads back; changed file refused; unlisted
  and missing files refused; undeclared label and other factory refused; bad declarations refused
  before writing; member code outside the harness directories; no freeze -> refused.
- test_stage_e_runner.py (14): the entry refuses when preflight raises, before reading anything and
  writing nothing; a screened member's record (harness sha, freeze sha, table hashes, ordinal,
  series dates, screen, power not_run: StartRuleMissing), written once; series = daily USD / 15.625
  for ZN; coverage 0.9 -> excluded and the engine not run; the floor labels (hold_below_2min,
  mean_holding_below_10min) without dropping; legs other than frozen refused; unknown window
  refused; confirmation needs S_X; release calendar absent refused by name; screen_cluster tiers;
  CLI requires the hash and roots; CLI passes its hash to preflight; two traded legs use the
  combined-dollar series of the primary vehicle; traded legs on two calendars refused.
- test_stage_e_template.py (3): the template's clock and size from the frozen tables; one breakout
  entry and the 75-minute exit on synthetic MNQ; no breakout, no trade.
- test_stage_e_mes_regression.py (7): section 3 (3 x new path vs screen_candidate, 3 x vs D.1d's
  record, and the class check C1, C2, C4 against the frozen list).

Coverage (pytest-cov, all nine files): 92% of the new modules (engine 92, rules 92, frozen 93,
align 96, freeze 94, runner 84, bars 94, mes_regression 95, template 96, interface 89).
Ruff clean on every new file.

## 5. Commands run (results)

- `uv run --no-sync pytest -q tests/test_stage_e_*.py` (fast files): 86 passed in about 6 s.
- `reports/stage_e2b_briefs/heavy.sh uv run --no-sync pytest -q tests/test_stage_e_mes_regression.py`
  (OMP 6 threads, 13:16 PDT): 7 passed in 72.9 s.
- heavy.sh, the regression table script (scratchpad mes_table.py, 13:18): all equal (section 3).
- heavy.sh `pytest -q tests/test_screening_runner.py tests/test_d1f_runner_hardening.py
  tests/test_leakage_canaries.py` (13:19): 40 passed in 17.7 s (unchanged existing tests).
- heavy.sh coverage run of the nine test files (13:24): 92 passed in 186 s, 92% coverage.
- Memory before heavy runs: about 9.6 GB available; no job above 2 GB.

## 6. Readings (each can be overturned by the lead)

- RR-1 D11.5 "does not trade": applied to opening exposure; an exit of an open position is allowed
  at a minute where a signal leg has no bar.
- RR-2 Flatten: rules/sessions.py's must-be-flat state OR the bar's own flatten flags.
- RR-3 D9.5a fill guard: strategy orders (market and limit); forced flattens and D9.7 exits are
  exempt (the 01:52 ruling's "conduct outranks fidelity"); MLL liquidations are not orders.
- RR-4 R-08 lock rule: applied to order exits (strategy, forced flatten, D9.7); not to the MLL
  liquidation (kept at the MES engine's touch price); with no prior-settlement proxy no lock can be
  shown and the exit fills.
- RR-5 Roll-blackout dates are removed from every member's window, single-leg members included
  (D4's union rule, NULL_CRITERIA_E 4 and D11.4 "removes"). D.1 kept them as zero days; the MES
  regressions use D.1's own window.
- RR-6 The 01:52 ruling's "earliest exit (the member's own exit or F)": the engine enforces F and the
  grain pause at the fill; the member's own exit is the member's job (template text), since the
  engine cannot know a member's exit time.
- RR-7 An entry (D9.3a) is an opening strategy fill (from flat, a scale-in, or a flip); pending
  opening orders count toward the cap at intent time.
- RR-8 Floor labels come from refused attempts (entry cap, min hold) and the measured mean hold;
  forced exits (MLL, D9.7) that come within 2 minutes are not labelled.
- RR-9 D9.7 applies to hard-limit products only (grains, livestock, equity; L-13). No proxy for the
  prior trade date (the store's first date, or a prior date without settlement-window bars) refuses
  entries on those products. The price tested is the decision bar's close.
- RR-10 Passive fills pay commission only (D.1 convention); slippage is ceiled to the cent.
- RR-11 One traded position at a time across legs; traded legs on two group calendars are refused
  (the catalog has neither); the primary leg is the first traded leg of the frozen declaration.
- RR-12 The XFA account (MLL, restart on breach, Scaling Plan in lot-equivalent tenths) is kept as
  in D.1's canonical configuration.
- RR-13 Signal-leg roll blackouts ARE excluded (D4: "a roll-blackout date of ANY leg the member
  reads"); the K8 catalog text says signal-leg rolls are not excluded. D4 (frozen) is applied.
- RR-14 After a CPI skip or a min-hold-before-F skip, further entries on that product that trade date
  are refused ("skipped for the day").
- RR-15 UR-1: 2026-06-18 and 2026-06-19 are excluded from every product's research window as
  possible roll-blackout dates of an unseen splice on 2026-06-22/23 (symbology ends before
  2026-06-21 00:00 UTC; NG, MNG, QG, grains, metals and MBT had rolls due; a volume-ranked series can
  also flip back after a roll, e.g. CL rolled 06-18 while CLN6 still trades on 06-22).

## 7. Questions for the user / lead

- Q1 (blocks real runs) Release calendar. D8's event-window cost, D9.5a's fill guard and D9.12's
  CPI window need a frozen calendar of scheduled major releases per product (Topstep F6.4 plus the
  releases the catalog members name) and CPI instants, covering the research and confirmation
  windows. None exists. The runner refuses (ReleaseCalendarMissing) until
  reports/stage_e2b_release_calendar.json exists (schema in screening/stage_e_rules.py:
  {"schema": "stage_e_release_calendar/1", "coverage": {"first", "last"}, "releases":
  [{"id", "instant_utc", "products": [...], "cpi": bool, "source"}]}). Who builds it, and should the
  harness manifest freeze it?
- Q2 (blocks confirmation runs and the power check) S_X per product: the runner reads
  reports/stage_e_start_rule.json (schema "stage_e_start_rule/1": {"products": {ROOT: {"s_x"}}}),
  refused by name when absent. It must be computed from the step 2 store with stage_e_stats'
  start_rule and frozen before any confirmation read. Who writes it?
- Q3 UR-1 (RR-15): accept the blanket exclusion of 2026-06-18/19, or refine per product from
  contract calendars?
- Q4 A limit-locked exit still locked at the session end is refused by name
  (EngineRefusedCase "locked_exit_through_session_end", the member recorded as refused_case). Carry
  the position into the next session until a trade-through (R-08 literally), or close at the last
  close with a flag?
- Q5 RR-6: should members declare their own exit clock so the engine can apply the 01:52 ruling's
  "member's own exit" part itself?
- Q6 RR-13: D4's union (signal-leg blackouts excluded) versus the K8 catalog's "not excluded".
- Q7 RR-5: blackout dates removed (not zero days) for single-leg members too.
- Q8 Member modules at strategy/members/<k#>/ (outside the harness directories, so preflight does
  not refuse them): please confirm the location for the cluster sessions.
- Q9 The step 2 store's parquet hashes are recorded in each record but not checked against a
  frozen value (the research store's come from E.2a's size table). Should each cluster's
  confirmation list freeze them before its confirmation run?
- Q10 A zero-variance research series makes the D5 screen or the D4 power check undefined; the
  record carries "screen_undefined" / "power check undefined" and the member is left out of the
  tier assignment (listed under not_tiered). Ruling on how such a member is tiered.

## 8. Deviations and anything unfinished

- D-1 (boundary): at about 13:03 PDT I read the parquet SCHEMA and metadata (no rows) of
  data/processed/ZN/ohlcv-1m_ZN_v_0_2025-04-01_2026-06-19_research.parquet with
  pyarrow.read_schema, to learn the Stage E store's metadata keys. It showed column names and types,
  the metadata key names and ZN's first roll record (2025-05-30, ZNM5 to ZNU5). No bar row, price or
  volume was read. The common brief forbids opening a non-MES product parquet, so I report it. All
  later work used MES's own parquet (the regressions) and synthetic files only.
- Read, as the brief allows for the unseen-roll check: every product's roll cache and symbology
  cache under data/vendor/databento/rolls/ (last roll date and target symbol printed per product).
- Not done here (other owners): canaries through the runner (Task 3, CanaryCoder: use run_engine,
  StageERules, product_bar_iterator and tests/_stage_e_synthetic.product_frame); the release
  calendar and the start-rule file (Q1, Q2); adding the 11 new harness files to the manifest (Task 6).

## Follow-up OC-T (16:50-17:02 PDT, 2026-09-26)

On CanaryCoder's findings C-1 to C-3 (reports/stage_e2b_task3_canaries_worker.md section 0), under
lead ruling OC-T. InputsCoder's edits to screening/stage_e_runner.py and stage_e_align.py are kept.

Engine (screening/stage_e_engine.py, Stage E rule set only):
- C-1: no fill and no MLL mark ever uses a scheduled-closure print. On a closure bar of a traded
  leg, `fill_pending_at_open`, `try_passive` (never reached), `check_mll` and `queue_forced` are
  skipped. `close_on_closure_bar` fills a pending member exit or forced order, and any position
  still open (reason `forced_flatten`), at the CLOSE of the leg's last tradable bar before the
  print. This is the session-end convention: fill stamped at that bar's decision time, `Fill.closure_gap`
  True, counted `fill_at_prior_close_closure_gap`. A pending opening order, or a resting limit
  order, is cancelled (`closure_bar_no_fill`). An intent decided on the print stays refused
  (`engine_scheduled_closure`). A lock-deferred exit meeting a closure print raises
  EngineRefusedCase (`locked_exit_through_session_end`), as at a session change. Session-change
  closes (`roll_session`) and `finish` also use the last tradable bar and never a closure print.
- C-3: closure bars seen are counted per leg (`closure_bars_seen:<ROOT>` in the counters).
- MES: `MesRules.skip_closure_bars = False`. sim/engine.py has no closure check, so the MES rule
  set keeps its behaviour exactly; `StageERules.skip_closure_bars = True`.
- `MesRules` moved to a new module, screening/stage_e_mes_rules.py, to keep the engine under 800
  lines (691 now). **The harness manifest must list this new file.**

Runner (screening/stage_e_runner.py):
- C-2: a FrozenInputError (CostLookupError included) raised during a member's run becomes
  status `refused_case` with refusal "<ExceptionName>: <message>", exactly like EngineRefusedCase.
  `screen_cluster` continues and puts `refused_members` {member: refusal} third in its summary
  (after cluster and window). The CLI prints one `REFUSED` line per refused member.
- Fixed while testing: with every member refused, `assign_tiers` raised on an empty list. Tiers
  are now None and the run completes.
- C-3 in the record: `bars.<ROOT>.closure_bars` (closure prints in the loaded frame) and
  `engine.closure_bars_seen` {root: n} with `engine.closure_gap_fills`.

Canary file (the two permitted edits only):
- The strict xfail marker line on
  `test_a_closure_bar_after_a_vendor_gap_on_an_early_close_date_is_never_traded` is removed; its
  24 cases now pass.
- The regular-date canary now fails on any FrozenInputError. It asserts that nothing trades at
  the print and that `fill_at_prior_close_closure_gap` == 1 (24 cases pass).

New tests (mine):
- tests/test_stage_e_rules.py, +4:
  - a pending exit fills at the 15:03 bar's close, not at the print;
  - an open position with nothing pending closes at the prior close, with no MLL liquidation;
  - a pending opening order at a print is cancelled;
  - MesRules and StageERules closure flags.
- tests/test_stage_e_runner.py, +2:
  - a CostLookupError becomes a named refusal and the cluster continues with `refused_members`;
  - closure counts appear in the record.

Run (heavy.sh, 6 threads, 16:57-17:00 PDT):
- `pytest -q tests/test_stage_e_*.py tests/test_leakage_canaries.py`: **487 passed, 0 xfailed**,
  1 warning. The warning is a RuntimeWarning in screening/stage_e_stats_power.py, ScreenStatsCoder's
  file.
- The MES parity (9) and the three MES regressions (7) are still bit for bit.
- Ruff is clean on every file I touched.

Readings (the lead may overturn):
- RR-16: an open position with nothing pending that meets a closure print is closed at the prior
  tradable close. The member must already be flat there: every calendar closure lies inside a
  TopstepX must-be-flat window.
- RR-17: a resting limit order on that leg is cancelled rather than left resting.
- RR-18: the MLL liquidation is not deferred past a print. It simply never reads the print's
  range.

## Follow-up F-1 (18:10-18:35 PDT, 2026-09-26)

Fable review finding F-1 (BLOCKING): `strategy/members/__init__.py` ran on every screening run
and was hashed by nothing. Lead ruling, Task 8. Files changed: screening/stage_e_freeze.py,
strategy/stage_e/_template.py (docstring), tests/test_stage_e_freeze.py and the test helper
tests/_stage_e_synthetic.py. screening/stage_e_runner.py and data/stage_e_bars.py are not
touched (InputsCoder's files).

(a) The members package init.
- `check_members_init` refuses unless `strategy/members/__init__.py` exists and is 0 bytes.
- Every cluster freeze hashes it beside the cluster directory's *.py files. The per-cluster
  `<k#>/__init__.py` stays hashed as before.
- `load_cluster_freeze` refuses a freeze that does not hash it ("written before F-1's fix").
- `ClusterFreeze` now carries the root it was loaded from, so verify and resolve check files there.
- Importable non-source files (*.pyc, *.pyo, *.so, *.pyd outside __pycache__) in a cluster
  directory are refused.

(b) The static check.
- `check_member_source` (ast only, nothing executed) runs on every *.py file of the cluster
  directory: members, helpers, and the cluster init. It runs in `write_cluster_freeze`, in
  `verify_cluster_code`, and in `resolve_member`, which re-verifies before importing.
- Each refusal names file:line: rule.
- Ruling forms:
  - `import_not_allowed`: the exact allowlist `ALLOWED_IMPORTS` plus the member's own cluster
    package. A relative import may not leave that package. `from rules import products` counts
    as rules.products.
  - `banned_name`: the ruling's builtins and modules, whether used as a name, an attribute or an
    import alias.
  - `assigns_imported`: assignment, augmented assignment or deletion of an attribute or item
    reached from an imported name.
- Additions beyond the ruling. The lead may drop any of them; each closes a route the ruling's
  forms leave open:
  - `star_import`.
  - getattr, vars, locals, `__builtins__`, breakpoint and input as `banned_name`. They reach the
    banned objects through a constructed string.
  - `dunder_attribute`, except __init__, __post_init__, __name__ and __doc__. This blocks the
    `().__class__.__subclasses__()` and `__globals__` escapes.
  - `mutating_call_on_imported`: update, pop, clear, cache_clear and similar methods called on an
    object imported from rules, screening or strategy. Example: `PRODUCTS.update(...)` would
    change ticks and commissions for every member.
  - `file_io`: numpy load, save, loadtxt, fromfile, tofile, memmap, lib and ctypeslib, and Path
    read_text, write_bytes and similar methods.
- Before the import, `importable_origins` locates the files Python would load for
  strategy.members, the cluster package and the module. It uses PathFinder, which executes
  nothing, and requires them to be the checked files. A copy earlier on the path is refused.

(c) The template text.
- `strategy/members/__init__.py` is provided by the harness, empty and frozen; never create,
  edit or fill it.
- Create an empty `strategy/members/<k#>/__init__.py`.
- The allowlist and the banned forms are stated in full. The template passes the check (tested).

Tests (tests/test_stage_e_freeze.py, now 44):
- The F-1 exploit reproduced (an init that sets `screening.stage_e_runner.MEAN_HOLD_MIN_MINUTES`
  = 0.0):
  - the freeze refuses it (the init must be empty);
  - planted after the freeze, `verify_cluster_code` and `resolve_member` refuse it before any
    import, and the constant stays 10.0.
- The same patch inside a member module is refused (`import_not_allowed` and
  `assigns_imported`).
- A freeze written before the fix is refused.
- The allowlist accepts the template, the synthetic member, own-cluster absolute and relative
  imports, and numpy.
- 31 banned forms are refused, each with file, line and rule.
- A .pyc in a cluster directory is refused.
- `resolve_member` refuses when Python would import another copy of the module.

Test-helper fix (lead's note of 18:24): the real, empty `strategy/members/__init__.py` now shadowed
the temporary member packages. `install_member_package` now PREPENDS the temporary strategy
directory to `strategy.__path__`, and still clears `strategy.members*` from sys.modules. The
repository's init is untouched.

Run (heavy.sh, 6 threads, 18:29-18:33 PDT):
- `pytest -q tests/test_stage_e_*.py`: 528 passed, 0 failed, 1 warning (screening/stage_e_stats_power.py,
  not mine). This covers test_stage_e_runner.py, test_stage_e_freeze.py, test_stage_e_template.py,
  the canaries, the MES parity and the MES regressions (still bit for bit).
- Ruff is clean on the changed files.

For the lead:
- screening/stage_e_freeze.py changed, so the harness manifest needs its new sha256.
- Residual risk (not closed here): Python may load a crafted `__pycache__` .pyc whose recorded
  source mtime and size match. The source hash and the static check do not see bytecode.
- numpy remains a large allowed surface.
