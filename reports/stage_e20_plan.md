# Stage E.20 Part C plan: the ML route's net pipeline on 17 roots (search, screen, backward test)

**Status: FROZEN (lead, 2026-10-11; reviewed reports/stage_e20_review_plan.md with recheck, code review
reports/stage_e20_review_search_code.md, rulings reports/stage_e20_rulings.md sections 4-6; hashed in
reports/stage_e20_search_freeze.json before the E20S registration).** Written before any search-window bar is read
for this stage and before any fit. Binding order: docs/prompts/STAGE_E.20.md's FIXED DESIGN (F1, F2, F3, F6, F7, F8,
F9), then docs/STAGE_E_ML_V2_DESIGN.md as frozen (reports/stage_e12_ml_v2_freeze.json), then the
E.16 rulings on the 2010-2019 windows. It becomes binding when PlanReviewer-FableXHigh's BLOCKING and
SHOULD FIX findings are fixed and it is hashed into reports/stage_e20_search_freeze.json, before the
45 registrations and before any fit. Code facts cite reports/stage_e20_briefs/codemap_*.md
(read-only maps of the frozen code, 2026-10-11).

## 1. Universe (F1)

The 17 roots with owned 2010-2019 stores, each with the vehicle, tick value and D8 cost E.12 froze
(reports/stage_e20_briefs/root_table.md, generated from reports/stage_e12_ranking.json and
reports/stage_e10_research/cost_wall.json):

| Cluster | Vehicles (price path) |
|---|---|
| K1 | MNQ (NQ), M2K (RTY) |
| K2 | ZT, ZF, ZN, TN, ZB, UB |
| K3 | 6E |
| K4 | MCL (CL), NG |
| K5 | MGC (GC) |
| K6 | ZC, ZS, ZL, HE, LE |

No K7 vehicle (MBT) and no MES. One pooled model per horizon over the 17 vehicles, with the frozen
product and cluster identifiers (V2.6). Every vehicle is a key of ml_route_v2.constants.UNIVERSE, so
the frozen per-product facts, caps and costs resolve without edits (codemap_phase1_world Q1,
codemap_sizing_sim_engine Q5). The frozen panel builds identifier columns for all 28 UNIVERSE
vehicles and K1-K7; the columns of absent vehicles and of K7 are constant zero and stay as built.

## 2. Windows (F2)

- Search: trade dates 2019-05-06..2024-02-29 from the E.12 step2 stores of the 17 roots
  (data/processed_step2/<ROOT>/ohlcv-1m_<ROOT>_v_0_2019-05-06_2024-02-29_step2.parquet, sha256s in
  reports/stage_e17_run_manifest.json, verified at start). Each root's first date is the S_X E.12
  computed under the frozen D4 rule and recorded in reports/stage_e12_phase1_bars.json ("roots" ->
  "s_x"): 2019-05-06 for 15 roots, ZF 2020-10-01, ZT 2021-10-01. The rule is not rerun: it reads
  research-window store bytes, which F2 forbids; its recorded output for the same stores is used.
- Training calendar for the CPCV blocks: the union of the 17 vehicles' group trade dates in
  [2019-05-06, 2024-02-29] (the frozen synthetic.training_calendar rule).
- Backward (E20-B1 only, behind its registration and marker): each root's window in
  reports/stage_e16_windows.json, starting at the later of the json's window_start_on_or_after and
  E.16 R-S4's sourced listing date, and ending at the stores' last date, 2019-04-30 (2019-05-01..05
  are outside the stores and not in the B1 calendar; review PR-8): 2010-07-01 for most; TN
  2016-01-11 and RTY 2017-07-10 (R-S4); HE 2017-07-01; LE 2014-12-15 (2010-06-07..2014-12-14
  excluded, R-S3); from data/processed_hist/ext2010 (NG NQ ZN 6E
  GC ZC) and ext2010h (the other 11).
- Never read: anything dated 2024-03-01 or later; data/sealed/; the holdout stores; MES's stores
  (MES is not loaded at all; section 6); the research-window stores; any 2010-2019 byte before
  E20-B1's registration line and marker exist.

## 3. Read guard (F3)

pattern_search/guard.py, imported by every pattern_search entry point before anything else:
- refuses any path under data/processed_hist/, data/sealed/, any holdout store (paths taken from
  data/holdout.py), data/processed/ (the research and MES stores; this also keeps MES out), and any
  store of a root outside the 17;
- refuses any bar with ts_event or trade_date on or after 2024-03-01 after load (the frozen loader
  already refuses holdout, embargo and out-of-store dates; the guard repeats it);
- the primary refusal sits on every path handed to any loader (load_confirmation_leg, read_leg and
  any direct parquet read are wrapped), because pyarrow opens files natively; a sys.addaudithook hook
  repeats the path refusals for Python-level opens (review PR-10);
- the start and end checks hash the backward stores as bytes in a separate shell process
  (reports/stage_e20_briefs/checks.sh), outside every guarded process, and decode nothing;
- only the E20-B1 evaluation may open data/processed_hist/<plan>/<root>/, and only after (a) the
  registry holds E20-B1 with the B1 freeze's sha256 and (b) reports/stage_e20_B1_RUN_ONCE.json has
  been written by that same process before its first processed_hist open (the marker is created
  with O_EXCL; an existing marker refuses the run); any other caller is refused;
- tests plant each case (a processed_hist path before registration, after registration without the
  marker, a sealed path, a holdout path, an MES path, a research-store path, another root's store, a
  2024-03-01 bar) and show each raises.

## 4. Decision clock (V2.2 plus F6 addition 1)

- t1, t2, t3: the frozen V2.2 rule (clock.decision_rows), with its exclusions as frozen: non-trade
  dates, early-halt dates, early-close dates (F_X not the group's regular F), and each vehicle's own
  roll-blackout dates (pipeline.own_blackout). No CPI exclusion exists for the v2 vehicles.
- t4 = F_X - 60 min on every (vehicle, trade date) the frozen clock kept: 14:08 CT for equity,
  rates, FX, energy and gold; 12:18 for grains; 12:03 for livestock. t4 rows carry t_index 4 and the
  same identifier columns. They are built by pattern_search from the frozen rows (codemap_clock Q1);
  clock.py is not edited.
- Horizons: t4 rows enter h60 and hF only. build_targets marks h120 unavailable on t4 rows by its
  own rule (t + h <= F_X); on t4 rows h60's exit is the bar opening at F_X, the same bar as hF's.
- Entries: at most one open position per product (the frozen portfolio admit rule). V2.2's "at
  most 3 entries per product per trade date" follows from three decision times; with t4 the frozen
  code allows one entry per decision time, at most 4 (constants.MAX_ENTRIES_PER_PRODUCT_DAY is not
  read by any v2 module; the engine's D9.3 cap is 20). Recorded as part of the clock departure.
- G11 (the decision-time index, a raw flag) takes the value 4 on t4 rows; G6 and G10 baselines are
  per t_index, so t4 forms its own (codemap_clock Q1).
- Structure (review PR-9): under an hF configuration a t3 position stays open to F, so t4 is skipped
  whenever t3 traded (one open position per product); under h120 likewise where t3 + 120 > t4
  (equity, grains). t4 therefore trades only when no earlier decision of that product is open, which
  shapes the reported t4 share. For energy, rates, FX and gold, t4 = 14:08 is after D6's C, so their
  t4 hold is post-settlement and rod_ret at t4 spans past that day's close; H6's late-session reading
  applies to equity, grains and livestock only.

## 5. Features (V2.3 plus F6 additions 2 and 3, after F6's cut)

### 5.1 The cut (before any fit)

Start: the 62 signals the frozen coverage rule (phase1 world.signal_coverage) gives for the 17
vehicles with MES bars present; MES is not loaded, so g17_mes, k8_flight_ret and k8_flight_tail are
uncovered as well (59). Then F6's rule: a feature enters only if every leg it reads is one of the 17
roots and every calendar it needs exists causally over both windows (2019-2024 and each root's
2010-2019 window), and no feature is "not applicable by design" in the backward window. A table
that a frozen rule derives from a calendar existing over both windows (for example a "full
sessions" list) counts as existing. Every member table a KEPT feature reads is a 2019-on module
literal; section 10.1 lists, for each, its 2010-2019 source and swap mechanism (review PR-1), and the
Step 6 sentinel dry check (section 13) must show every KEPT feature computes, and is applicable on
its event rows, under the 2010-2019 tables before the search freeze. A feature that does not is
dropped before the freeze, with the reason logged.

The cut, applied by the lead to Part A's availability facts (reports/stage_e20_product_summary.md
section 1.3, which gives every dropped feature's reason and source reader):

KEPT (34 frozen signals): cp1_ret, cp2_range, cp2_brk, cp3_clv; k1_vwap_dist; k2_auction_mto,
k2_auction_msince, k2_monthend_msince; k4_eiafade_move, k4_ngpre_mto, k4_ngpre_msince,
k4_ovr_ret, k4_ovr_pct; k5_ovr_ret, k5_ovr_pct; g01_ret30, g02_ret60, g03_ret120, g04_ret_day,
g05_gap, g06_rv60, g07_range, g08_prev_ret, g09_vol_state, g10_logvol30, g11_t_index, g12_dow;
g16_month_end; g17_nq, g17_zn, g17_6e, g17_cl, g17_gc, g17_zc. With section 5.2's two features the
model sees 36 features (each its z column and, where not always applicable, its flag), plus the
frozen identifier columns. pattern_search passes exactly these 34 names to build_panel's signals=
argument and appends the two r_ROD features.

DROPPED (33): by the calendar rule, k1_vxn_regime, k1_vxn_band (VXN table), k2_predrift_move (ISM
Services), k3_ldnmom_trend, k3_ldnrev_move, k3_ecbfix_mto, k3_ecbfix_msince (FX fix and session
tables start 2019), k4_apipre_ret (API dropped-weeks table undetermined), k4_eiamom_r3 (NYSE
not-full table), k5_pmfix_move, k5_preauc_msince (gold fix calendar), k6_limitcont_dir (limit table
starts 2019-05), k6_wasdepre_drift (WASDE calendar), k9_anncday (EC-K9 has only FOMC for
2010-2019), g13_min_to_rel, g14_min_since_rel, g15_rel_day (2010-2019 release calendars lack NFP,
CPI, PPI, GDP, ISM, WASDE, Crop Production, API); k2_fomc_mto (review PR-2: its frozen 13:00 CT
event minute misplaces or omits every FOMC statement before 2013-03-20, released at 12:15 or 13:15
CT, so the feature would change meaning by design over 2010-07..2013-03); and the rest below.

Dropped by the leg rule: g17_mbt, g17_mes, k7_montrend_ret, k7_rev2h_ret,
k7_expiry_mto, k7_expiry_msince (MBT rows or legs), k8_wkndbtc_move (MBT leg), k8_flight_ret,
k8_flight_tail (MES leg), k6_crushgap_gap (ZM leg). Dropped as not applicable on any row of the
universe in either window: k8_oilcad_ret, k8_oilcad_z (6C rows only), k3_mehedge_req,
k3_tkypost_msince, k3_tkypre_msince (6J rows only).

Not re-admitted: the v2 families excluded for timing (K5-fomc-01, K6-wasdepost-01, and
k2_fomc_msince's reach) become reachable at t4, but they are not in the frozen signal library's code
and F6 allows no added features beyond its list; none was proposed as a sized Part A feature.

Kept with partial row loss in the backward window (the feature exists; some rows have a missing
input and are excluded for data reasons, V2.3's missing-value rule, never imputed): the ports
(cp1_ret needs the 17:00 CT first bar, absent on rates before 2011-10-03; cp1/cp2 need the 08:30
grains open, absent before 2012-05-21) and the generic features reading O_X (G4, G5, G7) on grains
before 2012-05-21, and livestock rows by session era. In the code's terms these values are missing,
never "not applicable", so no flag-0 state reaches the model (review PR-15). These spans lose their
rows in E20-B1; the expected share per root, computed from the 2010-2019 calendars alone, is declared
in section 10.1 now, and the dry check and the B1 result report it.

### 5.2 Added: the two r_ROD features (F6 addition 2)

Computed by pattern_search from frozen helpers, normalized with the frozen normalize.zscore_causal
(250 / 60 / clip 5, per vehicle over all its rows), attached to the frozen Panel by
dataclasses.replace with feature_cols extended (codemap_clock Q2, Q6):
- rod_ret(t) = P(t) / P(prior C) - 1. P(t): the close of the bar closing at t (generic._own, the
  G1-G4 convention). P(prior C): the close of the bar opening at C-1 on the previous trade date of
  the vehicle's group calendar, C from D6's frozen day session (_daily.daily_of c1_close; the G5
  pattern, generic._previous_trade_day). Not applicable (0 plus flag 0) when the previous trade date
  is an early-halt date (as G5); missing (row excluded) when P(t) or the prior C bar is absent on a
  normal date.
- rod_absratio(t) = |rod_ret(t)| / median(|rod_ret|) over the previous 60 trade dates of the same
  vehicle and the same t_index on which rod_ret is applicable and present (strictly before d).
  Fewer than 60 such dates: missing (warm-up, row excluded). Not applicable when rod_ret is not
  applicable. A zero median: not applicable.
- Each gets an applicability flag column (app_rod_ret, app_rod_absratio) and a z column, like the
  frozen signals; the caller applies build_panel's rules itself: values not applicable are 0 with
  flag 0; a row with an applicable but missing value is dropped; every value's availability is at
  or before decision_ts_ns (asserted); every value on a fitted row is finite.

### 5.3 Added: Part A features accepted (F6 addition 3)

Acceptance rule (lead): a proposal is accepted only if (a) its rule and size come from a primary
source quoted verbatim; (b) it is computable causally at a decision time from the 17 roots' bars and
calendars that exist over both windows; (c) its expected gross per trade from the published
evidence is at least 1.5 x the root's D8 round trip (V31, at V2.7's loosest hurdle), where the
published figure is for the instrument class and the hold the feature would serve, and, when decay
after a date is documented, the most recent published subsample governs (review PR-7: the rule as
it was applied); (d) it is not already in the library or in section 5.2.
Accepted: none. Seven proposals came in (RTY fomc_r1, ZS zs_wasde_post_t4, 6E p6e_mehedge_nq and
p6e_post_ldnfix, ZT zt_cpnauc, ZF zf_auc10y, ZB k2_auc10_mto_zb); every one fails (c), and two also
fail (b); reasons in reports/stage_e20_product_summary.md section 1.4. RTY's fomc_r1 is the only one
whose reader computed a ratio above 1.5 on a published figure (2.51): that figure is for SPY's
15:30-16:00 ET hold in 1993-2013, not for the t4 to F hold on Russell the feature would serve, so
its expected gross for that use is not established by published evidence ((c) alone carries the
rejection; the product summary's ground (d) is withdrawn: with k9_anncday and k2_fomc_mto dropped,
no FOMC-day indicator exists on equity rows). ZF's zf_auc10y clears 1.5 only on its full sample
(1.53); at post-2014 strength, the governing subsample, it is 0.76.

## 6. World, panel and targets (V2.4, V2.5 unchanged)

- World: the frozen phase-1 loaders (data.stage_e_bars.load_confirmation_leg with its sha256, L-3
  booking, holdout, embargo, store-range and roll-metadata checks), called per root by pattern_search
  for the 17 price paths with E.12's recorded S_X; MES is never opened (the coverage rule then
  excludes its readers, as P-1a would); the frozen release calendar
  (screening.stage_e_rules.load_release_calendar) and frozen D8 costs (targets.frozen_costs); roll
  blackouts from the loaded legs (world.blackout). A new state directory outside the repository
  (~/.cache/propexp_e20_search) and a new reports subdirectory (reports/stage_e20_search/), never
  E.12's.
- Rows: section 4. Signals: section 5. Targets: targets.build_targets on the rows including t4.
- Frozen checks the composed builder re-applies (review PR-4), by name: on synthetic worlds
  pipeline.assert_bars_on_session_grid (V2.9's shifted-product guard); on real bars, as V2.2b says ("On
  real bars the session-grid check of the synthetic pipeline is replaced by the frozen loader's own L-3
  booking check") and as E.12's phase-1 world did, the L-3 booking check instead, with scheduled-closure
  bars counted and kept (phase1 world.closure_counts; harness v9's keep-and-flag ruling; the first real
  check --world found 7 such NQ bars and was refused by the grid assertion before this correction); phase1 world.refuse_late (or the guard's
  equivalent) on every loaded root, with the degraded-day record, closure_counts and compact_bars;
  panel.assert_window(..., "train"); the calendar cut (rows outside the training calendar dropped and
  counted) and the empty-panel refusal as build_world_panel applies them; on the two rod columns,
  build_panel's three rules (not-applicable values 0 with flag 0, a row with an applicable missing
  value dropped, avail_max <= decision_ts_ns) and signals.assert_causal on the rod frames.
- The real 17-root panel is built only after the 45 registrations (review PR-13); no filter
  statistic, fit or score exists before the registry line. Before the registration, `check --world`
  loads the real world once through the frozen loaders and their checks (review SC-1), and builds no row,
  feature or panel.
- Normalization: frozen. t4 rows join each vehicle's pooled trailing windows, so the t1-t3 z-scores
  differ slightly from a three-time panel; accepted as a consequence of F6 addition 1.

## 7. The 45 configurations (F6, F9)

The frozen grid, in the frozen CONFIGS order (models outermost: ridge lambda 0.01, 0.1, 1.0, then
LightGBM depth 2, 3; then k 1.5, 2, 3; then horizon h60, h120, hF), with the fixed LightGBM settings
(min_data_in_leaf 2000, lambda_l2 100, learning rate 0.02, 300 rounds, feature and bagging fractions
0.7, deterministic, 8 threads, seed 20261003). E20-S01 = ridge_l0.01_k1.5_h60, E20-S02 =
ridge_l0.01_k1.5_h120, E20-S03 = ridge_l0.01_k1.5_hF, ..., E20-S45 = lgbm_d3_k3_hF; E20-Snn =
CONFIGS[nn - 1]. [Full 45-row table generated at the freeze from configs.CONFIGS.] The frozen trial
registry allows no hyphen in a label, so the prompt's E20-S01..E20-S45 are registered as label E20S
with ids E20S-01..E20S-45 (E20S-nn = E20-Snn = CONFIGS[nn - 1]), as H6 was (E20H6). No other
configuration exists. Market orders only. Cost-gate reading "gross" (frozen constant).

## 8. Decision layer, sizing, CPCV, selection (V2.7, V2.8, V2.9 unchanged)

- Cost gate: trade sign(r_hat) iff |r_hat_ticks| > k x c (gross reading), c the row's D8 round trip
  with the event-window rule; ranking at one clock time by edge over cost, then root.
- Sizing and caps at 50K: the frozen selection metric (selection_metric.score_split): D held at the
  MLL ($2,000), per-trade budget b = 0.10 x D / sqrt(3), the daily variance budget, the rounding
  band, the loss cap, one lot-equivalent per product and the D9.11 caps, the base tier less 0.1 lot,
  at most 3 open positions and one per cluster, the release-window rule, the beyond-q_c cost.
- Admissibility: one pass of the frozen c/sigma filter (tau 0.167) on the whole search panel
  (pipeline._filter). If no (vehicle, horizon) pair is admissible, the search has no model and the
  screen fails (the frozen pipeline would turn an empty set into no filter; pattern_search refuses
  that).
- Nested CPCV: cpcv.nested_cpcv(panel, the 45 configs, score_fn_for(risk), ledger, state_dir,
  admissible, calendar = the training calendar, risk_fn = split_risk_fn(panel)): 6 blocks, 2 test
  blocks, 15 outer splits, 4 inner folds, purge, one-date embargo, risk table per split and fold,
  eligibility (>= 30 trades, finite on every fold), ties as frozen. Final configuration:
  cpcv.final_selection with the same arguments, refit on all six blocks.
- The frozen ConfigLedger in the state directory registers the 45 config ids before the first fit
  (cpcv._prepare); program N is the trial registry's (section 11).

## 9. SCREEN (F7), on the nested OOS record

The record: nested.path_daily, the 5 paths' daily net dollars at 50K over every date of the training
calendar (zeros on no-trade dates, on dates without rows and on splits with no eligible
configuration).
1. Median-path daily t: the median over the 5 paths of mean / (sd ddof 1 / sqrt n) of each path's
   daily series (pipeline._daily_t); must be >= 2.0.
2. PBO: cpcv.pbo_cscv(nested.config_daily) (16 blocks, C(16,8) combinations); must be < 0.5. PBO
   counts as not < 0.5 when pbo_cscv returns degenerate = True or a NaN pbo, or raises (review PR-11).
3. Annualized net Sharpe at 50K: mean / sd (ddof 1) of path_daily.mean(axis=1) x sqrt(252); must be
   >= 0.5 and <= 4.0. Above 4.0 fails item 3 as written (review PR-3, fixed before the fit): the
   screen fails and Part C ends; the result is held and an independent FableLeakageAudit (fable
   xhigh) runs for the record (the V2.9 controls rerun on the real panel, the composition path of
   section 6, the r_ROD and t4 paths); a clean audit does not turn the fail into a pass.
The screen passes iff 1, 2 and 3 hold and final_selection returns a configuration (V2.9: "if none
is eligible for the final model, the route has no model, and that is a fail"; not an addition). A failed screen
ends Part C: no freeze, no backward read.

Reported, not gating: the DSR (cpcv.dsr_at_n(path_daily.mean(axis=1), 528, sharpe_variance(finite
config_sharpes)); 528 = the registry's N after the 45 registrations, 483 + 45; review PR-11), Sharpe variance over the 45 configurations' CPCV OOS
daily Sharpes); per-configuration table (inner and outer scores, CPCV OOS daily t and Sharpe, trades);
the final configuration's own CPCV OOS t and Sharpe; per-product OOS round trips with products below
30 flagged (V2.9 criterion 6; the lead's reading: on the nested record, each split's selected configuration, round
trips per product per path, flagged when the median over the 5 paths is below 30, matching criterion 2's median path;
the minimum-path and all-paths readings and the final configuration's counts are reported beside it); the 1.5 x slippage re-pricing of the nested record (score_split with
slippage_multiple 1.5 on each split's selected configuration); the share of the final configuration's
CPCV OOS net P&L from t4 rows (sum over its accepted t4 trades over the total) and from the r_ROD
features (1 - P&L with the rod_* z columns set to 0 at prediction, no refit, over P&L as fitted; both
P&L figures shown). The ruin probability (V2.9 criterion 7) needs engine trade records; no real-data
engine run exists in the frozen code (Phase1World has no engine frames; codemap_sizing Q3), and
building one is new code. Fixed now (review PR-6): on a failed screen it is reported as not
computed, with this reason; on a passed screen, the adapter (composition, no edit) is written, tested
and hashed by the B1 freeze before the B1 registration, and the figure is reported with the screen.

## 10. Freeze and backward test E20-B1 (F8), only after a passed screen

[Written in full in reports/stage_e20_prereg_B1.md at Step 8.] The freeze holds: the final
configuration and its model payload with sha256; the feature list; the normalization rule
(250 / 60 / clip 5, computed in the backward window from that window's own earlier dates); the risk
table from all six blocks; k; vehicles and the D8 cost table; the backward windows of section 2;
the statistic and bar below; the code hashes. Before the freeze commit, a dry check on synthetic
sentinel frames that mimic each leg's 2010-2019 listing and calendar state shows every feature
computes; removing one leg's frames must stop it.
- The backward world: the 17 roots' 2010-2019 stores under the frozen loaders' booking checks, with
  the 2010-2019 group calendars (data/calendars/hist2010, E.16's livestock calendar) and every member
  table of section 10.1 swapped in for the frozen 2019-on objects by setattr, as C1 did
  (c1_replication/context.hist_tables, extended to all seven groups and the KEPT members' tables), the 2010-2019 release
  calendars (E.14, E.16) for the event-window cost and the release-window rule, with E.16's
  conservative fallback (base_rules/costs.py) for release types that have no 2010-2019 rows. The
  clock is section 4's rule applied to each date's session as the 2010-2019 calendars give it; a
  decision row whose bar does not exist is excluded, never imputed.
- Construction (review PR-5, the lead's reading of F8's "V2.7 and V2.8 as frozen"): the frozen
  score_split construction, D held at $2,000, the same one that produces the screen's nested record
  (V2.9 describes the selection metric as "built with V2.7 and V2.8"; F8 asks for the screen's daily
  t). It excludes the engine's path-dependent D, the kill switches, the combined MLL audit, D9.5a
  deferral, the D9.12 CPI window and D9.7 price-limit locks, as the screen's record does; no
  real-data engine path exists in the frozen code. E.16 F-07's price-limit convention: before
  2019-05-01 no limit table exists, so entries and exits whose fill bar is a single-price bar (open =
  high = low = close) are counted and reported per product as a diagnostic and stay in the statistic.
- Carried from 2019-2024 by F8's design (review PR-12): the model payload, the risk table from all six
  blocks (sigma(p,h), L(p,h); a look-ahead in sizing only, mandated by F8), the admissible pairs, k,
  and the D8 cost table. Recomputed from the backward window's own earlier dates, with nothing from
  2019-2024: every trailing quantity (z-score means and sds, sigma_X,d, the G6/G10 baselines, G9's
  120-date median, rod_absratio's 60-date median); the first trade dates of each vehicle's window
  are warm-up and lost. D6's (O, C) table stays the frozen one (date-independent, as C1); O_X and
  F_X come from the swapped 2010-2019 calendars and rules.sessions.
- Evaluation: once, at 50K, with V2.7 and V2.8 as frozen (the construction above), at 1.0 x D8. Statistic: the daily net P&L in dollars over every trade date of
  the backward calendar (the union of the 17 roots' group trade dates from 2010-07-01 to 2019-04-30;
  zero on no-trade dates); daily t as in section 9 item 1; one-sided p from the t distribution with
  n_dates - 1 degrees of freedom; annualized net Sharpe as in section 9 item 3.
- PASS iff one-sided p <= 0.025, annualized net Sharpe >= 0.5, and at least 100 round trips.
  Descriptive only: per year, per product, 1.5 x slippage, the DSR at the final N.

### 10.1 The 2010-2019 swap table and the declared row losses (review PR-1, PR-15)

Source: reports/stage_e20_briefs/backward_swap_table.md (sha256 d40d0ed38626597c739c322f149465d48f6b3021be78b76a3c23d2d5f6a7f396)
and .json (sha256 e34a2241a808202ebe9e544fb12e314b78cb7ad4e3acb8274303260ef62a7397), BackwardTables-OpusXHigh,
calendars and code only. Its tables S1-S12 give, for every 2019-on module literal, constant or factory a
KEPT feature, the clock or the cost path reads: the module attribute and file:line, the 2010-2019 source
(path, sha256, schema, coverage) and the swap mechanism (setattr on the attribute, or a factory swap as C1
did for ngpre.make_ng). Every derived table (EQUITY_FULL_SESSIONS, TREASURY_AUCTIONS and AUCTION_TENOR from
EC-AUC, the month-end dates, WPSR in eiafade's schema from the E.14 file, the metals full sessions) is built
by the frozen generator's own code and reproduces the frozen table on the 2019-05 overlap. Per-feature
verdicts: every KEPT feature is SWAP-READY or NEEDS-DERIVATION (verified); none is NO-SOURCE; the g17 leads
read no table. The Step 6 sentinel dry check (section 13) must confirm each before the search freeze.

Lead rulings on the table's open items (fixed now, before any fit; reports/stage_e20_rulings.md section 4):
1. The B1 swap context adds what C1's never needed: the frozen metals product-group mapping copied onto
   the 2010-2019 metals calendar in memory (without it the clock and the ports raise on MGC), and E.16's
   livestock calendar wired into the hist-calendar loader and the flatten tables.
2. LE's 08:00 era (2014-12-15..2016-02-26, 296 dates): the frozen clock puts t1 at 08:30, before the
   ports are known (cp1 09:00, cp2 08:45, cp3 08:31), where the frozen causality check would raise. Rule:
   in the backward run a decision row whose decision time precedes the availability of an
   always-applicable feature is excluded and counted (calendar analysis: only LE's t1 rows in that era).
3. Grains F after a 13:15 close (1,031 backward dates; F_X = 13:18 has no bar): the hF exit and t4's h60
   exit (the same bar) take E.16 R-B1's closure convention, the frozen engine's own forced fill at a
   session end: the close of the last bar before the session close, priced with that bar's bucket. The
   shifted grains and LE 08:00-era clock times (the frozen rule on each date's session) are disclosed.
4. Release types with no 2010-2019 rows: the actual 2010-2019 rows (FOMC, WPSR, NGS, EC-AUC and the
   others on file) drive every rule (event-window cost, D9.5a deferral, the release-window refusal). For
   each type that touches a vehicle in the frozen 2019-on calendar and has no 2010-2019 rows, E.16's cost
   fallback (base_rules/costs.py): every backward fill of that vehicle whose minute lies in [m, m + 30)
   for any of the type's frozen release minutes m pays the event-window cost, on every trade date
   (applied to the targets' cost columns before scoring). The deferral and the release-window refusal are
   not applied for those types (the one element that is not conservative; disclosed).
5. WPSR 2012-11-01 (no sourced release time): the date is excluded for MCL as unsourced (C1's C12).
6. Hist-calendar unsourced dates (LE 14, HE 4): excluded as action dates (E.16 R-C3).
7. Cross-tenor reopenings follow the frozen original-term labelling (recorded, not corrected).

Recheck additions (reports/stage_e20_review_plan.md "Recheck", rulings section 4b):
- Ruling 4's reach (PR-16): the fallback window [m, m + 30) of a release type with no 2010-2019 rows
  contains, on every backward trade date, the entry minute of: t1 (07:50) on ZT, ZF, ZN, TN, ZB, UB,
  6E and MGC (NFP, CPI at 07:30 CT); t1 (09:00) on MNQ and M2K (ISM at 09:00 CT); t3 (11:00) on ZC,
  ZS, ZL, HE and LE (WASDE, Crop Production at 11:00 CT); and some exits (for example grains t2 h60
  exiting at 11:00). In the search window the same cost applies only on actual release dates. The
  Step 6 dry check computes the exact (vehicle, decision time, horizon, entry or exit) table from the
  calendars and the frozen release minutes before the search freeze, and the lead copies it here;
  B1 reports the share of its trades that paid the fallback cost. The fallback stays: it is E.16's
  convention (F2) and conservative; it lowers B1's power at those rows, which is disclosed.
- Ruling 3's mechanism (PR-17): the R-B1 exit is a pattern_search post-step on the targets frame
  (y_gross_hF, the hF cost columns and exit_ts_ns_hF, and the same for t4's h60), written before the
  purge reads exit_ts_ns; a hand-computed test covers it (section 13); B1 reports the hF and t4-h60
  P&L on those dates separately.
- Ruling 2's count (PR-18): the dry check reports the rows excluded by ruling 2 per root and t_index
  (the calendar analysis expects LE's t1 on 296 dates only), and the B1 result carries the same count.

Declared row losses from the session structure (calendars only; the dry check and B1 report them):
| Root | Backward dates | Dates losing every row | Share | Cause |
|---|---|---|---|---|
| NQ, 6E | 2280 | 6 | 0.3% | post-holiday 05:00 CT Globex first opens (no 17:00 bar on d-1) |
| ZT, ZF, ZN, ZB, UB (each) | 2279 | 313 | 13.7% | Globex opened 17:30 CT before 2011-10-03 (no 17:00 first bar for cp1) |
| ZC, ZS, ZL (each) | 2225 | 477 (about 615 with the warm-up extension) | 21.4% (about 27.6%) | no 08:30 bar before 2012-05-21 |
| LE | 1103 | 63, plus t1 on 296 08:00-era dates | 5.7% (+ t1 rows) | 09:05 late opens; 08:00 era t1 (ruling 2) |
| RTY, TN, CL, NG, GC, HE | - | 0 | 0% | - |
| every root | - | 1 (its first window date) | - | no prior-day bars at the window start (G5's prior C, cp3's prior day); reported by the Step 6 dry check (search_build.md item 4) |

Step 6 dry check results (reports/stage_e20_dry_check_step6.md and .json, SearchCoder, before the freeze): all 36 features
compute and are applicable on their event rows under the swaps; removing any one of the 17 legs' frames stops the build;
the declared losses above are reproduced exactly; ruling 2 excludes only LE's t1 rows (296). PR-16's exact table (section 4
of the dry-check report): the fallback windows catch one decision time's entry on every kept backward date, 25.0% of
entries, for ZT, ZF, ZN, TN, ZB, UB, 6E, MGC (t1 07:50; NFP or CPI at 07:30), MNQ, M2K (t1 09:00; ISM) and ZC, ZS, ZL,
HE, LE (t3 11:00; WASDE, Crop Production); exits are caught on 15.3% of ZC, ZS, ZL exits, 18.2% of HE's and 13.2% of LE's,
0% elsewhere; MCL and NG 0%.

## 11. Trial accounting (F9)

In order: H6 (registered 15:36:20 as r004-E20H6, N 480 -> 483; all three tests FAILED, verified); then, after this plan's review fixes and
before any fit, the 45 configurations as one registry line (label E20S, ids E20S-01..E20S-45,
freeze reports/stage_e20_search_freeze.json with its sha256; N 483 -> 528), the line quoted in
STATE; E20-B1 only after a passed screen and its freeze commit (label E20B1, id E20B1-T1; 528 -> 529). The search
registration's manifest hashes this plan, the pattern_search package and tests, and every input
file the search reads (store sha256s from the E.17 manifest, the calendars, the release calendar,
the frozen tables).

## 12. Compute

Measured: E.12's 28-product panel 266 s at 2.89 GB peak RSS (codemap_phase1_world Q3); E.11's
synthetic full pipeline 4.8 GB, about 44 min. Expected here: panel about 4-6 min, about 3-4 GB (17
vehicles, 4 decision times); nested CPCV 1,125 fits (about 450 LightGBM at 8 threads, the frozen
setting, within CLAUDE.md's half-the-cores limit) plus 3,375 selection-metric passes, about 1 to 3
hours (a guess until the build's synthetic timing). nice 10; free memory checked before launch; one
heavy job at a time; resumable by configuration and split (cpcv_units.jsonl) and per stage.

## 13. Tests (Step 6)

New test files only (the frozen tests stay unchanged): the guard's planted cases; V2.9's
perturbation, fold and canary tests rerun on a synthetic 17-vehicle world with t4 rows and the r_ROD
features (and accepted Part A features), calling the frozen helpers; the grid count is 45 and its
order equals section 7; the feature list equals section 5's KEPT plus added list exactly; t4 rows
and both r_ROD features on synthetic bars (hand-computed values, the early-halt and warm-up cases,
availability at or before t); the empty-admissible refusal; the registry and marker checks;
added by review PR-4 and PR-14: a shifted root makes the composed builder raise; a planted-edge
canary at t4 (a pattern_search-side plant on a copy of the synthetic bars, since the frozen plant
stays on t1-t3); the cross-date target-shuffle null on the composed 17-vehicle, t4, 36-feature panel;
signals.assert_causal on the rod frames. The Step 6 sentinel dry check (review PR-1): synthetic
sentinel frames for every leg in its 2010-2019 listing and calendar state, the section 10.1 swaps
applied, every KEPT feature computed and shown applicable on its event rows; removing one leg's
frames must stop the build; the declared row-loss shares reproduced.

## 14. v2 amendments

None. Every addition is composition around the frozen code (codemap_* "composition" findings). If
the build finds an edit to a hashed file unavoidable, it stops; the lead writes a v2 amendment, Fable
reviews it, and it is committed before any fit.

## 15. Order of events

Part A; H6 review, freeze, registration, evaluation, verification; this plan's review and fixes;
the build and its tests, with the Step 6 sentinel dry check (any feature failing it dropped before
the freeze); the search freeze manifest; check --world on the real stores (no row, feature or fit);
the 45 registrations; then the real panel, the search and the screen;
(on a pass: the B1 prereg, dry check, freeze review, freeze commit, registration, evaluation,
verification).
