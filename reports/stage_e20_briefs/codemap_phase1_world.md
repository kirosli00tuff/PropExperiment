# Stage E.20 code map: phase1-world (read-only)

Written 2026-10-11 by a read-only code mapper. Every reference is file:line in the working tree at
HEAD abfdeb8. No data store was opened. Gate 0 results, E.15, E.17 and E.18 were not read.

Hash status, checked against the manifests themselves:
- reports/stage_e12_ml_v2_freeze.json (schema `ml_v2_freeze/1`, 91 files) hashes every
  ml_route_v2 file named here, including phase1/{__init__,__main__,_io,build,cli,freeze,gate0_stage,world}.py,
  probe.py, synthetic.py, pipeline.py, clock.py, panel.py, constants.py, signals/*.py and
  tests/test_ml_v2_phase1_support.py. It also hashes reports/stage_e2b_release_calendar.json and
  reports/stage_d1f_step5_start_rule.json.
- data/step2_store.py, data/stage_e_bars.py, data/group_session.py, data/calendars/*.py,
  data/research_bars.py, screening/stage_e_start_dates.py, stage_e_rules.py and stage_e_frozen.py
  are not in the v2 manifest. They are hashed by the harness manifest
  reports/stage_e2b_harness_freeze.json (1,062 files; screening/harness_freeze.py:31, preflight at :204).

## Q1. How phase 1 builds a real-data world

Entry point (world.py:518-578):
```python
def phase1_world(vehicles: Sequence[str], *, step2_root: Path | None = None,
                 research_root: Path | None = None, mes_path: Path | None = None,
                 summaries_root: Path | None = None,
                 research_sha256: Mapping[str, str] | None = None,
                 mes_start: RootStart | None = None,
                 repo_root: Path | None = None) -> Phase1World
```
Defaults (world.py:530-541): `data.config.STEP2_ROOT` = DATA_ROOT/"processed_step2" (data/config.py:129),
`PROCESSED_ROOT` = DATA_ROOT/"processed" (config.py:22), MES =
`data.research_bars.CONFIRMATION_SERIES_PATH` (research_bars.py:56;
data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet), summaries =
`data.step2_store.STEP2_REPORTS` = reports/step2 (step2_store.py:93). The step 2 parquet path is
`step2_parquet_path(root, base)` = `base/root/ohlcv-1m_{root}_v_0_2019-05-06_2024-02-29_step2.parquet`
(step2_store.py:113-114).

Order of operations:
1. `check_vehicles` (world.py:125-135): the list must be non-empty, have no duplicates, and use only keys of
   `constants.UNIVERSE` (constants.py:22-33). All 17 E.20 vehicles are UNIVERSE keys: NG, MNQ->NQ, ZN, 6E,
   MGC->GC, ZC, ZT, ZF, ZB, UB, TN, MCL->CL, ZL, ZS, M2K->RTY, HE, LE. `price_path(v)` =
   `UNIVERSE[v][1]` (world.py:121-122).
2. S_X per root, `_starts` (world.py:488-510). It loads `screening.stage_e_frozen.load_frozen_tables()`, takes the
   research sha256s from `tables.research_parquet_sha256` (verified 2026-10-11: all 17 roots present) and calls
   `root_start(root, *, step2_root, research_root, research_sha256, tables)` (world.py:256-276). That
   calls `screening.stage_e_start_dates.product_start_rule(root, research_path=, step2_path=,
   research_sha256=, window=day_session_window(root, tables))`, which reads ts_event, volume and
   trade_date, never a price. The resulting `RootStart` (world.py:240-253) carries s_x, v_ref,
   store_sha256 (= the step 2 sha256 the rule read) and inputs.
   - MES: `mes_root_start(mes_path, *, record_root)` (world.py:279-288) uses `mes_from_d1f`, D4's fixed
     2020-02-03 taken from reports/stage_d1f_step5_start_rule.json, which pins the parquet sha256.
     A `StartDatesRefusal` there makes MES unavailable (P-1a, world.py:504-506).
   - A root with `s_x is None` (empty window) is dropped by name, along with its vehicle (world.py:543-547).
3. Bars per root, `load_root(start, *, step2_root, summaries_root, repo_root)` (world.py:449-463):
   - `load_root_leg` (world.py:354-367) calls step 2 roots through
     `data.stage_e_bars.load_confirmation_leg(root, step2_root, start, *, expected_sha256)`
     (stage_e_bars.py:297-312). MES goes through `read_leg(MES, path, STEP2, expected_sha256=...)`
     and `_cut_at` (world.py:342-351).
   - `read_leg(root, path, store, *, expected_sha256)` (stage_e_bars.py:271-289) runs in this order:
     sha256 format check (:255-260); file present, else `ConfirmationStoreMissing`; hash equal to expected,
     else `ParquetHashMismatch` (:263-268); read BAR_COLUMNS; duplicate timestamps refused; then the
     L-3 booking check `check_bookings` (:154-177). That check books every row with
     `book_trade_dates` (group calendar, `assign_trade_dates(..., close_minute_to_previous=True)`,
     :142-151). An unbookable row raises `TradeDateUnbookable`. A forbidden date raises
     `refuse_trade_dates` -> `HoldoutRowRefused` (:123-135). A label that differs from its booking
     raises `TradeDateMismatch`. Last come the rolls: `splices_and_blackout` (:189-217) books every
     roll instant on the group calendar, computes `group_session.roll_blackout(cal, splices, 2)`
     (group_session.py:468-483: the splice date plus the 2 group trade dates before it) and refuses a
     mismatch with the file's recorded splice and blackout dates (`RollMetadataMismatch`).
   - Holdout and embargo classes (`forbidden_class`, stage_e_bars.py:104-112): holdout-1 from 2026-06-22,
     holdout-2 2024-04-01..2025-03-31, embargo 2024-03-01..2024-03-31. Any date outside the step 2 range
     2019-05-06..2024-02-29 (`store_range`, :115-120) is also refused.
   - Then come `refuse_late` (Q5), the degraded-day record (`_summary_degraded` world.py:370-381: reports/step2/
     bars_<ROOT>.json must record the store's sha256; `_mes_degraded` :384-392 reads the parquet metadata),
     `frozen_start_agreement` (:291-306, recorded only), `closure_counts` (:395-411, counted only)
     and `compact_bars` (:330-339). compact_bars keeps the 8 columns ts_event, OHLC, volume,
     instrument_id and trade_date (categorical). vendor_degraded_day and in_scheduled_closure are not kept.
   - A `StageEBarRefusal` on a price-path root is re-raised and stops the build. On MES it becomes P-1a
     (world.py:552-560).
4. Training calendar: `synthetic.training_calendar(kept, first, TRAIN_LAST)` (synthetic.py:213-214).
   It is the union of the vehicles' group trade dates in [min S_X of the vehicles' paths, 2024-02-29], from
   `ml_route.inputs._group_calendar` (synthetic.py:195-199).
5. Coverage: `signal_coverage(vehicles, registry=None, unavailable=None)` (world.py:149-168), with
   `available_roots` (world.py:138-146) = the price paths plus MES. Verified 2026-10-11 for the 17
   vehicles: 62 signals covered. 5 are uncovered: k6_crushgap_gap (ZM), k7_montrend_ret, k7_rev2h_ret,
   k8_wkndbtc_move and g17_mbt (MBT). If MES is refused (as in E.12), 59 are covered and g17_mes,
   k8_flight_ret and k8_flight_tail are also excluded.
6. Releases: `screening.stage_e_rules.load_release_calendar(repo)` (stage_e_rules.py:175) reads
   reports/stage_e2b_release_calendar.json and refuses when it is absent. Costs:
   `ml_route_v2.targets.frozen_costs(kept)` (targets.py:72-76) gives the D8 `leg_inputs(v, traded=True)`.
7. Legs: `synthetic.legs_by_vehicle((v,))` filtered to the loaded roots (world.py:567). `frames` is
   empty (no engine in phase 1).

`Phase1World` fields (world.py:466-485): vehicles, first, last, bars_first, calendar, bars (root ->
compact frame), frames, releases, costs, blackout, legs, requested, starts, dropped, coverage, roots,
mes_status, mes_refusal. **world.blackout** = {root: frozenset(leg.roll_blackout)}, holding the L-8
group-calendar blackout of every loaded root including MES (world.py:458, 572). The decision-row
exclusion uses only each vehicle's own price path: `pipeline.own_blackout` (pipeline.py:260-266),
called in `build_world_panel` (pipeline.py:269-298) and `build._rows_in` (build.py:119-133).

MES (P-1a). In E.12 MES was refused with `TradeDateMismatch`, 3 rows, first label 2020-03-30 booked
2020-03-31 (reports/stage_e12_STATE.md:20). The same refusal recurs unless the frozen MES parquet,
data/stage_e_bars.py or the equity calendar changes. All three are hashed.

Can a world be built for the explicit list of 17 without editing? **Yes, by composition.**
`phase1_world(vehicles, ...)` takes the vehicles directly, and its docstring defaults are the real
stores (world.py:518-578). The ranking gate (freeze review F-3) lives only in `run_build`, through
`phase1_subset(ranking_path, *, step2_root=None, summaries_root=None)` (world.py:206-233). That function
reads `{"subset": [{"vehicle", "path", ...}]}` from `<reports_dir>/stage_e12_ranking.json` (`RANKING_FILE`,
world.py:172). The file name is fixed, but `reports_dir` is a parameter of `run_build`, so a 17-entry
ranking in another directory also works without edits. The existing reports/stage_e12_ranking.json
subset lists 28 vehicles, a superset of the 17 (no MBT dependency for the vehicles). Step 2 stores and
summaries exist for all 17 roots (reports/step2/bars_<ROOT>.json present).
The CLI (`python -m ml_route_v2.phase1`) cannot take a list or a path. Its paths are module constants
(cli.py:34-40), so using the CLI for a 17-root world would need an edit to cli.py (hashed) or a
monkeypatch.

## Q2. What phase 1 writes, and the preflight checks

CLI constants (cli.py:34-40): `REPORTS_DIR = REPO_ROOT/"reports"`,
`LEDGER_PATH = REPO_ROOT/"ledger"/"ml_v2_config_ledger.jsonl"`,
`STATE_DIR = ~/.cache/propexp_e12_phase1`, `WORLD_KW = {}`. Steps: build, register, run (cli.py:34).

Preflight, every step, before any store, state or ledger is read (cli.py:56-64, `_gates`):
1. `screening.harness_freeze.preflight(expected_sha256, root=REPO_ROOT) -> str`
   (harness_freeze.py:204-215) checks reports/stage_e2b_harness_freeze.json.
2. `verify_v2_freeze(path: Path, expected_sha256: str, *, root: Path | None = None) -> dict`
   (freeze.py:61-96) checks the sha256 of the manifest bytes, the schema `ml_v2_freeze/1`, and the
   size and sha256 of every listed file, and refuses duplicate paths.
3. Then `compute.platform.lower_priority()` (nice 10) (cli.py:110-112).

build: `run_build(*, state_dir, reports_dir, world_kw=None, harness_sha256=None, freeze_sha256=None)
-> dict` (build.py:266-306).
- Stage files: `pipeline._Stages(state_dir, timing=True)` (pipeline.py:205-232) writes
  `state_dir/stages/phase1_panel.pkl` and `phase1_filter.pkl`, each pickled as
  {"constants": constants_fingerprint(), "out": ...}. `_read_stage` (pipeline.py:193-202) refuses a
  file written under other constants. A finished stage is loaded, never recomputed.
- Resume guard (build.py:285-290): a saved panel built from another requested list or another
  ranking sha256 is refused. `check_panel_out` (build.py:194-199) refuses when the panel no longer
  hashes to its input fingerprint. The input fingerprint is `cpcv.input_fingerprint(panel.frame,
  {inputs, signals, feature_cols})` (build.py:87-91). Inputs (build.py:99-116): ranking record,
  requested/vehicles/dropped, per-root s_x, store sha256 and research sha256, release-calendar sha256,
  frozen-table hashes, calendar, covered/uncovered signals, MES status.
- Reports, written atomically to `reports_dir` (build.py:296-297, `_io.write_json` / `write_atomic`,
  _io.py:54-68): `stage_e12_phase1_bars.json` (schema `stage_e12_phase1_bars/1`) and
  `stage_e12_c_sigma.json` (schema `stage_e12_c_sigma/1`). These names are constants (build.py:54-55) and
  are overwritten on every build into the same reports_dir.
- `state_dir/phase1_build.json` (build.py:300-304) records fingerprints, vehicles, stage-file sha256s,
  report sha256s and per-stage wall_s and peak_rss_mb.
- Filter stage: `pipeline._filter(panel)` (pipeline.py:301) runs the c/sigma table, the risk table and
  the admissible pairs.

register: `run_register(state_dir, *, ledger_path, reports_dir) -> dict` (gate0_stage.py:143-165).
It writes `reports/stage_e12_gate0_list.json` once, chmod 0444; a file already there with other bytes is
refused. It appends every Gate 0 test to `configs.ConfigLedger(ledger_path)` (append-only; the same spec
writes nothing). The E.12 ledger holds 273 entries (stage_e12_STATE.md:21).

run (Gate 0, waived in E.20): `run_gate0(state_dir, *, ledger_path, reports_dir,
expected_list_sha256, harness_sha256=None, freeze_sha256=None)` (gate0_stage.py:291-330).
Run-once guards: `_guard_once` (:260-264) refuses when `state_dir/gate0_DONE.json` or
`reports/stage_e12_gate0.json` exists. `_pin_run` (:267-275) pins {constants, inputs, list_sha256} in
`state_dir/gate0_run.json`. Family B state goes to `state_dir/gate0/` (gate0B_*.npy, gate0B_meta.json).

State already on disk (listed by name and size only): ~/.cache/propexp_e12_phase1/ holds the E.12
28-vehicle build: stages/phase1_panel.pkl (103,423,923 bytes), phase1_filter.pkl, phase1_build.json,
gate0_run.json, gate0_DONE.json and gate0/. Because of the resume guard, a 17-root run needs a new
state_dir. Building into reports/ would overwrite stage_e12_phase1_bars.json and stage_e12_c_sigma.json,
so a different reports_dir avoids that. Both are parameters of `run_build`, so no edit is needed.

## Q3. Measured runtimes and memory (timing and memory lines only)

E.12 real data, 28 requested vehicles (reports/stage_e12_STATE.md:20; E.12_RETURN.md:533, 617, 721):
- Phase-1 build 12:09-12:14 PDT, 2026-10-03 (about 5 min wall, including the gates and the world load).
- From ~/.cache/propexp_e12_phase1/phase1_build.json "stages":
  - phase1_panel (world + panel): wall 266.2 s, peak RSS 2,893.5 MB.
  - phase1_filter: wall 0.20 s, peak RSS 1,646.7 MB (measured after a VmHWM reset).
- Panel stage file size: about 98.6 MiB (103,423,923 bytes).
- Register: list registered 12:15:25-26.
- Gate 0 run: result written 12:15:54, about 29 s after registration (E.12_RETURN.md:617).
- Final-table row "Build, register, Gate 0 once": 12:09-12:16, 0:07 (E.12_RETURN.md:721).
- No GB, RSS or elapsed line for Gate 0 itself was found in either file.

E.11 synthetic probe, 28 products (reports/stage_e11_runtime_probe.md:79-95; synthetic, not results):
- world build 7.9 s / 2,439 MB; panel 28.7 s / 3,156 MB; filter 0.2 s; Gate 0 12.9 s / 3,179 MB.
- One outer split (45 configs x 4 inner folds + refit): 48.1 s / 3,295 MB.
- Nested CPCV, 15 outer splits: 722 s (extrapolated).
- Simulate, one path: 341 s / 7,198 MB before FIX 3, 310.6 s / 4,778 MB after FIX 3.
- Payouts, one path: 54.3 s / 4,630 MB.
- Full grid total: 46.1 min (extrapolated before FIX 3).

Code comments: none state runtimes. `panel_peak_note` (build.py:309-311) prints wall and peak RSS per
stage. `_peak_rss_mb` reads VmHWM (pipeline.py:158-166).

## Q4. The synthetic world generator (synthetic.py)

```python
def synthetic_universe(roots: Sequence[str], first: date, last: date, *, seed: int,
                       plant: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None,
                       warmup_dates: int = WARMUP_DATES,            # 210
                       vol_ticks: Mapping[str, float] | None = None,
                       sigma_cost_multiple: float = SIGMA_COST_MULTIPLE,  # 20.0
                       compact: bool = False, eager_frames: bool = True) -> SyntheticWorld
```
(synthetic.py:412-457.) `roots` are vehicle roots (UNIVERSE keys). The returned `SyntheticWorld`
(synthetic.py:86-130) has the same fields `build_world_panel` reads as `Phase1World`, plus
vol_ticks, seed, plant and the methods exclude/engine_frames/engine_blackout.
- Bars cover every root in `legs_by_vehicle(vehicles)` (synthetic.py:133-151): each vehicle's path, all
  CLUSTER_LEADS (including MBT), MES, and the member-signal legs of the vehicle's cluster and K8.
  Verified 2026-10-11 for the 17 vehicles: 23 bar roots (adds 6J, 6S, HG, MBT, MES, ZM). Bars are
  1-minute random walks on the real group-calendar session intervals (synthetic.py:236-253), from
  `warmup_dates` union trade dates before `first`.
- Roll blackout: synthetic splices on the first trade date on or after the 10th of Mar/Jun/Sep/Dec,
  plus 1 session before (synthetic.py:217-231, ROLL_SESSIONS_BEFORE = 1). Real stores use 2.
- Releases come from `signals.synthetic_bars.synthetic_releases`; costs from `frozen_costs`.
- Plants (`PLANT_KINDS = ("sign","noise","shift","leak")`, synthetic.py:78; docstring :30-45):
  - "sign" takes edge_ticks or edge_cost_multiple, feature_minutes (60), horizon_minutes (60) and vehicles.
    It plants edge*x*sign(x) on the trailing feature return at each decision time.
  - "noise" plants nothing.
  - "shift" takes roots and minutes.
  - "leak" takes roots and minutes and adds a leak_fwd column.
  - Plant decision times come from `clock.decision_rows((vehicle,), ...)` (synthetic.py:282-284), which
    gives the frozen t1..t3 only. A t4 row has no planted edge unless a plant is composed outside synthetic.py.
- Sizes: probe size A = all 28 UNIVERSE vehicles, EARLIEST_S_X 2019-05-06..TRAIN_LAST, warmup 0,
  compact=True, eager_frames=False, sign plant at 3 round trips (probe.py:121-126). `probe.products_of`
  accepts only 28 or 8 (probe.py:113-118), so a 17-root probe through its CLI needs an edit to
  probe.py (hashed). `probe.build_world(products)` and `synthetic_universe` accept any list
  (composition).
- Test helpers (not hashed in data/, but tests/* are in the v2 manifest):
  `tests/ml_v2_fixtures.world(roots, first, last, *, seed, plant=None, **kw)` (cached,
  ml_v2_fixtures.py:45-51). `tests/test_ml_v2_phase1_support.build_stores(base, *, plant, mes_path=None,
  mes_sha256=None, extra_bars=None)` (:199-227) writes fixture step 2, research and MES stores in the
  real formats for HE, LE and ZC (2022-06-01..2024-02-29), suitable for `phase1_world(...,
  research_sha256=, mes_start=)`. `write_ranking(reports_dir, vehicles)` (:234) writes a fixture ranking.
  A 17-root fixture store set would have to be written by new test code. The helpers are composable.

## Q5. Date guards that refuse 2024-03-01 or later

- `constants.TRAIN_LAST = date(2024,2,29)`, `FORBIDDEN_FROM = date(2024,3,1)` (constants.py:16-17).
- `world.refuse_late(root, frame)` (world.py:309-320) raises `Phase1WindowError` on any trade_date >=
  2024-03-01 or any ts_event >= `FORBIDDEN_FROM_NS` (00:00 CT 2024-03-01, world.py:83-84). It is called
  in `load_root` (world.py:453).
- `phase1_world` refuses an empty calendar or a calendar ending >= FORBIDDEN_FROM (world.py:563-565).
- `panel.assert_window(panel_or_rows, mode="train")` (panel.py:53-64) raises `WindowError` in train mode
  on any trade_date >= FORBIDDEN_FROM. It is called at panel.py:111 and :131, pipeline.py:295 (end of
  `build_world_panel`) and cost_filter.py:37.
- `stage_e_bars.forbidden_class` / `refuse_trade_dates` (stage_e_bars.py:104-135) refuse embargo
  2024-03, holdout-2 and holdout-1 rows, and anything outside 2019-05-06..2024-02-29 for STEP2.
  `load_confirmation_leg` and `read_leg_dates` raise ValueError for S_X outside that range
  (:301-303, :320-322). The MES branch does the same at world.py:360-361.
- `step2_store.drop_outside_window` (step2_store.py:195-219, build time) drops embargo rows unread and
  raises `HoldoutLeakError` on rows booked to 2024-04-01 or later. `refuse_inputs` (:153-178) refuses
  sealed chunk names and paths. `DATA_END = date(2024,3,1)` is exclusive (:89).
- synthetic.py has no date guard of its own (only first <= last, synthetic.py:425-426). A synthetic
  world past 2024-02-29 is refused downstream by assert_window in `build_world_panel`.

## Additions vs hashed files (facts only)

- 17-root real world: composition (`phase1_world(vehicles, ...)` or `run_build(..., reports_dir=<new>,
  state_dir=<new>)` with a 17-entry ranking file). Using the CLI needs a cli.py edit (hashed).
- t4 rows: the world carries no decision times. Rows come from `clock.decision_rows`, called inside
  `pipeline.build_world_panel` and `build._rows_in`. Both are hashed (clock.py, pipeline.py,
  phase1/build.py). A t4 needs either composition outside them, or edits to clock.py/constants.py
  (`N_DECISION_TIMES = 3`, constants.py:43).
- r_ROD and the other new features: the world's compact bars carry ts_event, OHLC, volume,
  instrument_id and trade_date for every loaded root, which is enough for a prior-close return. Adding
  a feature to `signals.REGISTRY` needs edits to the hashed ml_route_v2/signals/*. A feature built
  outside REGISTRY and joined to the panel is composition.
- UNKNOWN: whether `build_world_panel` / `build_panel` accept extra feature columns without an edit. Not
  examined (outside this area).
