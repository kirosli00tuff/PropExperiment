# Code map: ml_route_v2 clock, panel, normalization, targets, signals (Stage E.20 Part C)

Read-only map, 2026-10-11. All paths are relative to the repo root. Every file under ml_route_v2/
cited here is hashed by reports/stage_e12_ml_v2_freeze.json (48 ml_route_v2 entries, including
clock.py, constants.py, panel.py, normalize.py, targets.py, pipeline.py, cpcv.py and every
signals/*.py). No data store was opened. Two read-only probes ran on code and on frozen report
tables only: REGISTRY metadata, and D6 (O, C) plus D8 cost-bucket coverage at the t4 minutes.

## Q1 Decision rows

- Signature (clock.py:163-164):
  `decision_rows(roots: Sequence[str], trade_dates: Mapping[str, Sequence[date]], *, exclude: Mapping[str, frozenset[date]] | None = None) -> pd.DataFrame`
  Columns: `ROW_COLUMNS = ("root","path_root","cluster","group","trade_date","t_index","decision_ts_ns","flatten_ts_ns")`
  (clock.py:46-47). `root` is the vehicle (MNQ, M2K, MCL, MGC, ...) and `path_root` is the price path from
  `constants.UNIVERSE` (constants.py:22). Dtypes: trade_date datetime64[ns], t_index int8, ts int64. Sort
  order is (decision_ts_ns, root), mergesort, then reset_index (clock.py:176-189).
- Rule: `decision_times_from(open_ct: time, flatten_ct: time) -> tuple[time, ...]` (clock.py:70-80):
  k3 = (F - 120 - O) // 30, first_k = 30 // 30 = 1, k2 = (1 + k3) // 2, and it returns exactly
  (O+30, O+30*k2, O+30*k3). It raises ClockError if k3 < first_k + N_DECISION_TIMES - 1. Constants:
  DECISION_STEP_MIN 30, FIRST_DECISION_OFFSET_MIN 30, N_DECISION_TIMES 3, LONGEST_FIXED_HORIZON_MIN 120
  (constants.py:41-46).
- Per date (`_date_rows(root, day)`, clock.py:145-160): O_X and F_X come from
  `ml_route.inputs.day_times(root, group, day)` (cached `_day_times`, clock.py:132-136).
  decision_ts_ns = dt.open_ns + (t - O) minutes; flatten_ts_ns = dt.flatten_ns. t_index runs 1..3
  (enumerate start=1).
- Session table source: per-date opens come from ml_route.inputs.day_times (the group calendar's D6
  session). The pinned group table, `decision_times_ct(group)` (clock.py:114-124), uses
  `screening.stage_e_frozen.load_frozen_tables().day_session_ct` together with
  `rules.sessions.REGULAR_FLATTEN_CT` (rules/sessions.py:67-70: 15:08 for every group except grains
  13:18 and livestock 13:03). DECISION_TIMES_CT (constants.py:49-59) is the pinned result.
- Exclusions (clock.py:148-153, 172-176):
  - day_times returns None: not a trade date, or no flatten.
  - `dt.early_halt`.
  - Early close: F_X minute != the group's regular F, so the whole date is dropped.
  - `exclude[root]` dates. The v2 pipeline passes
    `pipeline.own_blackout(blackout, vehicles) -> dict[str, frozenset[date]]` (pipeline.py:260), which is
    `exclude_union` with the price path as the only leg (clock.py:210-219). Only the product's own roll
    blackout drops rows.
  - CPI: the clock has no CPI exclusion. targets.py:192-193 drops the entry only for vehicles in
    rules.constraints.CPI_NO_OPEN, and none of the v2 vehicles is in it (targets.py:9-10).
- Can t4 be injected? No parameter exists: decision_times_from always returns 3 times, and
  decision_rows takes no rows or times argument. `pipeline.build_world_panel(world, *, check_grid=True, signals=None)`
  (pipeline.py:269-298) calls decision_rows internally (pipeline.py:282-283) and takes no rows argument.
  - Composition without edits is possible. Replicate build_world_panel's ~15 lines: rows =
    decision_rows(...), then add t4 rows built from each (root, trade_date)'s flatten_ts_ns minus
    3,600e9 ns with t_index = 4 and the other identifier columns copied. Re-sort by
    (decision_ts_ns, root) with mergesort and reset the index. Then build SignalContext(rows, bars,
    releases, sigma_d(rows, bars), blackout=...), build_targets and build_panel.
  - t4 rows then exist only on dates the clock kept, and F_X is always the regular F on those dates.
    t4 CT: 14:08 for equity, rates, fx, energy and gold; 12:18 for grains; 12:03 for livestock. All are
    later than t3. t4 is off the 30-minute grid, and nothing in the code requires the grid.
  - The probe found D8 cost buckets calibrated at the t4 minute and at t4 + 60 for all 17 vehicles.
  - The probe also found t4 = 14:08 later than D6 C for energy (C 13:30), rates and fx (14:00) and gold
    (12:30). It is earlier than C for equity (15:00), grains (13:15) and livestock (13:00).
- Downstream code that assumes 3 decision times or t_index 1..3:
  - N_DECISION_TIMES appears only in clock.py (the rule's ClockError guard).
  - MAX_ENTRIES_PER_PRODUCT_DAY = 3 (constants.py:47) is not referenced by any non-test module.
  - RISK_SPLIT_M = 3 (constants.py:101) sets the per-trade budget b = sigma_target/sqrt(3) (sizing.py:57,
    payout_sim.py:466). The literal is fixed and is not derived from the number of decision times.
  - G11 `g11_t_index` (generic.py:267-269, 380) passes the raw t_index as a flag that is not normalized,
    so t4 would enter as the value 4.
  - G6 and G10 baselines `_base_ratio` (generic.py:167-177) group by `np.unique(t_index)` with no
    hard-coded set, so t4 rows would form their own same-clock 20-row-date baseline.
  - DECISION_TIMES_CT is read only by synthetic.py:167 (synthetic worlds) and pinned_table.
  - Horizon availability t+h <= F_X is computed per row in targets.py (Q4) and does not depend on
    t_index.
  - One test, tests/test_ml_v2_panel.py:73, asserts z_g11_t_index is in {1,2,3}. Tests are not in the
    freeze list, and that test builds its own panel.
  - No grep hit for t_index in decide.py, portfolio.py or cpcv.py.

## Q2 Panel

- `build_panel(ctx: SignalContext, targets: pd.DataFrame, *, mode: str = "train", signals: Sequence[str] | None = None) -> Panel`
  (panel.py:107-132).
- `Panel` is a frozen dataclass (panel.py:43-50): frame, feature_cols, signal_names, horizons,
  avail_max_ts_ns, counts.
- Frame = concat of ctx.rows[ROW_COLUMNS], z_<n>, app_<n> (every name), id_root_<v> for all 28
  UNIVERSE vehicles, id_cluster_<K> for K1..K7, and the whole `targets` frame (panel.py:99-104, 119).
  Rows are then filtered by `keep = ~drop`.
- Targets columns (targets.py:256-260): entry_price, entry_ts_ns, release_window, sigma_d, then per
  horizon y_gross, cost_long, cost_short, exit_ts_ns, y_norm and ok.
- `_features` (panel.py:67-96) masks values that are not applicable to NaN and computes zscore_causal
  for specs with `normalize=True`. Flags pass through raw. z = 0 where not applicable.
  - A row is dropped if any applicable feature has a NaN raw value (missing_<n>) or no z statistic
    (no_statistic_<n>).
  - It raises if a kept row's avail_max > decision_ts_ns (panel.py:126-127).
- feature_cols = all z_ + app_ of signals not in ALWAYS_APPLICABLE + id columns (panel.py:128-130).
- signals= is a tuple of REGISTRY names (None = all 67, REGISTRY order). Duplicates raise.
  compute_signals raises KeyError on an unknown name (signals/__init__.py:98-101). Phase 1 passes the
  covered names (`phase1/world.py:149 signal_coverage`).
- Appending extra features. These are facts about the code, not a recommendation.
  - A name not in REGISTRY cannot pass through signals=. REGISTRY is a MappingProxyType built at import
    from each module's SPECS (signals/__init__.py:43-49), and build_panel reads REGISTRY[n].normalize
    (panel.py:73). Registering a signal needs an edit to signals/__init__.py or a k*/generic module,
    all hashed.
  - Extra columns on ctx.rows are dropped, because only ROW_COLUMNS are taken (panel.py:119).
  - Extra columns on the `targets` argument pass through into frame, row filter included. Only index
    alignment is checked (panel.py:112).
  - After build, `dataclasses.replace(panel, frame=..., feature_cols=...)` works; pipeline.py:294-295
    already uses replace. cpcv.horizon_data reads `panel.feature_cols` and `panel.frame` (cpcv.py:324-344)
    and raises unless X is all finite (cpcv.py:340).
  - Appended columns get none of build_panel's drop rule, avail check or app_ masking. The caller must
    do all of that.
  - Identifier handling is unaffected: the id columns are built from rows.root and rows.cluster only.

## Q3 Normalization

- `zscore_causal(raw: pd.DataFrame, rows: pd.DataFrame, cols: Sequence[str], *, window_dates=250, min_dates=60, clip=5.0) -> pd.DataFrame`
  (normalize.py:79-94). Constants are at constants.py:65-67.
- It works per `rows.root` (the vehicle), over that root's own row dates. The window is the 250 row
  dates strictly before d, warm-up needs 60 dates, and z is clipped to ±5.
  - All of a root's rows are pooled, whatever their t_index. Adding t4 rows therefore changes the window
    statistics of the t1-t3 rows too.
  - NaN values are skipped. Same-date rows never use each other.
- It is applied only inside panel._features (panel.py:73-76), on the masked raw values of
  `REGISTRY[n].normalize` signals: every member and generic except flags (k6_limitcont_dir, k9_anncday,
  G11, G12, G15, G16).
- A column added before build (on rows or targets) or after build is not normalized. zscore_causal is a
  public function and can be called by a caller on ctx.rows; the result is then subset to
  panel.frame.index. This is composition, with no edit.

## Q4 Targets

- `build_targets(rows: pd.DataFrame, bars: Mapping[str, pd.DataFrame], *, releases: Any, costs: Mapping[str, Any]) -> pd.DataFrame`
  (targets.py:223-260). costs come from `frozen_costs(vehicles: tuple[str, ...] | None = None) -> dict[str, Any]`
  (targets.py:72-76).
- Entry is the open of the bar opening at t, with the D9.5a guard deferral `_defer`
  (targets.py:145-169). The entry is refused if the deferral reaches F, or if fewer than MIN_HOLD 2 min
  are left before F (targets.py:189-194).
- Exit for h60/h120: nominal = t + h, and the exit exists only if nominal <= flatten_ts_ns
  (targets.py:205-207). A guarded exit is deferred, and a deferral that reaches F becomes the F fill.
- Exit for hF: x_ns = flatten_ts_ns, the open of the bar opening at F_X (the forced flatten fill, exempt
  from the guard; targets.py:201-203). F_X comes from the row's `flatten_ts_ns`, set by
  clock._date_rows from day_times.
- y_gross_<h> = (open(exit) - open(entry)) x per_unit(vehicle) in vehicle ticks (targets.py:210).
  Both bars must be on the row's trade date.
- cost_long/short_<h> = commission ticks + side slippage at the entry minute + side slippage at the exit
  minute, with the event-window flag [release, release+30) (targets.py:211-218). Net is not formed in
  targets.py; net is computed downstream in decide/score, which is outside this map: UNKNOWN here.
- y_norm = y_gross / sigma_d. ok_<h> = finite y and both costs, and sigma > 0 (targets.py:250-255).
- sigma_X,d: `sigma_d(rows, bars, *, _memo=None) -> pd.Series` (targets.py:91-103) uses
  `_daily.build_daily` (`_sigma`, _daily.py:138-151). It is the mean over the 20 complete dates strictly
  before d of |close(C-1 bar) - open(O bar)| in vehicle ticks, with O and C taken from the D6 frozen
  day_session_ct of the vehicle. It is a per-date value, the same for every t_index.
- Availability by decision time:
  - t1 to t3 have all three horizons, because t3 + 120 <= F by the rule.
  - t4 = F - 60: h60 has nominal = F, so it exists, and its exit is the bar opening at F_X, the same bar
    as hF. A guard deferral also ends at F, so y_gross_h60 equals y_gross_hF on t4 rows.
  - t4 h120 does not exist (F + 60 > F), so ok_h120 = False automatically. No code change is needed to
    keep t4 out of h120.
- Release lists: `release_times(releases, vehicle)` (_core.py:323-334) raises SignalInputMissing when
  neither the vehicle nor its path key is listed. Every one of the 17 vehicles must be in the calendar.

## Q5 SignalContext, bars, releases, flags, leads and legs

- SignalContext (frozen dataclass, _core.py:70-81): `rows` (DecisionRows), `bars` (Mapping root ->
  frame, keyed by price-path root plus signal-only roots such as MES), `releases` (ReleaseCalendar or
  EventCalendar), `sigma_d` (Series aligned to rows), `blackout` (Mapping root -> frozenset[date],
  default {}), and `cache` (a memo dict).
- Bars:
  - `bars_of(ctx, root) -> BarArrays` (_core.py:189-195) raises
    `SignalInputMissing("the context holds no bars for <root>")` when the root is absent.
  - BarArrays methods: `at(when)` (the bar opening at an instant), `last_closed(t)` (ts_event <= t-60s),
    `day_pos`, `on_day` (_core.py:102-131).
  - The convention is that a value used at t reads bars with ts_event <= t - 60 s (_core.py:6-7).
    Generic features use the "bar closing at t" (opening at t-1min, same trade date) via
    `generic._own` (generic.py:79-97).
- Rows view: `rows_of(ctx) -> RowsView` (_core.py:226-236) holds root, path, cluster, group, day (epoch
  days), t, t_index, flatten and sigma.
- Calendars come through data.calendars.GROUP_OF_PRODUCT, ml_route.inputs._group_calendar and
  data.group_session (previous_trade_date, trade_dates_between, session_intervals); see generic.py:136-143
  and 315-325 and _daily.py:74-88 and 154-176.
- Releases: release_times, cpi_times and release_coverage (_core.py:323-350). G13 and G14 are not
  applicable outside the calendar's coverage (generic.py:277-312).
- Not-applicable rows: a signal fn fills `empty(view)` and returns
  `result(view, value, app, avail)` (_core.py:354-367). Where not applicable, value is 0 and
  avail_ts_ns = t. Where applicable but missing, value is NaN and avail is -1. Event helpers
  (`event_rows`, `slot_rows`, `nothing`, `per_vehicle`) are in signals/_events.py:33-131.
  compute_signals then applies `apply_leg_blackout` (_core.py:385-401; mask at _core.py:370-382). On
  rows whose trade date is in ctx.blackout[R] for a root R in spec.roots_read with R != the row's path,
  the signal is not applicable. Specs with own_path_only are never blanked.
- Registration: each k*.py/ports.py/generic.py defines `SPECS = (SignalSpec(...), ...)`. The fields are
  name, family, cluster, kind, source, roots_read, normalize, fn and own_path_only (_core.py:55-67).
  signals/__init__.py:43-49 concatenates them into REGISTRY (67 names).
- G17 (generic.py:339-356, 390-392): there is one spec per lead in CLUSTER_LEADS (NQ, ZN, 6E, CL, GC,
  ZC, MBT; constants.py:36-37) plus MES (constants.py:38). roots_read = (lead,).
  - The value is the 60-min log return x 1e4 between the lead's last bar closed by t and its latest bar
    at least 60 min earlier, both on the row's trade date.
  - The signal is not applicable on the lead's own cluster rows, and where the lead has no such bar.
  - g17_mes has no own cluster, so it applies to all rows.
- K8 legs (k8.py:80-167):
  - k8_flight_*: MGC rows, MES bars.
  - k8_oilcad_*: 6C rows, CL bars.
  - k8_wkndbtc_move: MNQ rows, MBT bars.
  - Each returns `nothing(view)` when its vehicle has no rows (k8.py:113, 137), before any bars are
    read. Otherwise it calls bars_of(leg) (k8.py:115, 139), which raises SignalInputMissing when the
    leg is absent.
- A leg root missing from the world:
  - Phase 1's `signal_coverage(vehicles, registry=None, unavailable=None) -> Coverage`
    (phase1/world.py:149-169) leaves out any spec without own_path_only that reads a root not
    available. The caller passes the covered names through signals=.
  - In a world of the 17 roots, the roots_read show uncovered: g17_mbt, k7_montrend_ret, k7_rev2h_ret
    and k8_wkndbtc_move (MBT), and k6_crushgap_gap (ZM missing).
  - The MES readers (g17_mes, k8_flight_*) are covered only if MES bars are loaded. Whether E.20's world
    includes MES is UNKNOWN.
  - k8_oilcad_* is covered (CL is present) but has no 6C rows, so it is not applicable on every row.
    This gives a constant app_ column of 0 and z = 0.
  - Other leg readers that are not own-path: k1_vwap_dist and k1_vxn_band read NQ, k4_apipre, eiafade
    and eiamom read CL, k5_pmfix reads GC. All of these roots are present.
- Ports CP1-CP3 (ports.py:83-206): own path, and ALWAYS_APPLICABLE because they are "known by t1 = O+30"
  (ports.py:220-221). Any t >= t1, t4 included, satisfies this.
- K4-ovr and K8 members take the latest slot known by t (`slot_rows`, _events.py:81-97). t4 rows may
  therefore get a later slot.

## Q6 Previous close C (D6) for r_ROD

- D6 (O, C) per vehicle: `_daily.session_minutes(vehicle) -> tuple[int, int]` (_daily.py:65-71) reads
  load_frozen_tables().day_session_ct.
  - Probe values (O, C): MNQ and M2K 08:30/15:00; rates and 6E 07:20/14:00; NG and MCL 08:00/13:30;
    MGC 07:20/12:30; ZC, ZL and ZS 08:30/13:15; HE and LE 08:30/13:00.
- `_daily.daily_of(ctx, vehicle) -> Daily` (_daily.py:179-183) runs on the vehicle's price-path bars.
  - `Daily.c1_close` is the close of the bar opening at C - 1 min on CT date d with trade date d (NaN if
    absent). Related fields: `Daily.c1_idx`, `Daily.days`, `Daily.halt` and `Daily.pos(days)`
    (_daily.py:38-62, 104-135).
- Previous trade date: `generic._previous_trade_day(vehicle: str, day: int) -> int` (generic.py:136-143)
  uses data.group_session.previous_trade_date on the vehicle's group calendar (data/group_session.py:318)
  and returns -1 if there is none.
  - G5 `_gap` (generic.py:146-164) is the existing pattern: c1 of the previous trade date's Daily row,
    with availability = that bar's ts + 60 s. After an early-halt previous date G5 is not applicable.
  - G8 instead uses the most recent complete date before d (generic.py:218-230).
- P(t): the close of the bar closing at t, from `generic._own(ctx)["it"]` (generic.py:79-97), in vendor
  units of the path. The ratio P(t)/C - 1 is unit-free.
- The |r_ROD| / 60-date median: there is no existing helper with 60 dates. `_base_ratio`
  (generic.py:167-177) is the 20-row-date, same-t_index analogue (mean or median, shift(1)).
- Doability: computing r_ROD needs no edit. pattern_search can import these (partly private) helpers
  and build the frames with `_core.result`.
  - Making r_ROD a REGISTRY signal that flows through build_panel's masking, normalization, drop rule
    and causality check needs an edit to a hashed file (signals/__init__.py plus a module), so a v2
    amendment.
  - The alternative is composition: compute the feature, run normalize.zscore_causal on ctx.rows, then
    attach it via the targets argument or dataclasses.replace and extend feature_cols. The caller then
    owns the masking, NaN-drop and avail checks.
