# Stage E.11 Task 2: signal coverage of ML route v2 (V2.3)

Written by SignalCoder-OpusXHigh (Task 2), 2026-10-03. Synthetic data only; no market data, result
report or holdout file was opened. Code: `ml_route_v2/clock.py`, `ml_route_v2/signals/`,
`ml_route_v2/normalize.py`, `ml_route_v2/targets.py`, `ml_route_v2/cost_filter.py`,
`ml_route_v2/panel.py`. Contract: `reports/stage_e11_interfaces.md` sections 2-4.

## 1. Summary

- 54 inventory families (`reports/stage_e11_briefs/member_inventory.json`): 51 carried by signals,
  3 in `EXCLUDED` with a logged reason. `signals.FAMILY_SIGNALS` maps every family to its signals.
- Lead ruling after the first return: the core ports are pooled. D6 defines each port as one rule
  ported to every product, so the 21 port families (K1-cp1-01 .. K7-cp3-01) enter as four
  signals: `cp1_ret`, `cp2_range`, `cp2_brk` and `cp3_clv`. Each is computed for every product by
  the same frozen definition with its own O, C and first-bar rule. `FAMILY_SIGNALS` lists all 21
  ids against them.
- 66 signals in `REGISTRY`:
  - 42 member signals: the 4 pooled port signals, plus 38 from the 30 other coded families;
  - 24 generic: G1-G16, plus 8 G17 leads.
  G18/G19 are the 35 identifier columns built in `panel.py`. 5 signals are not normalized:
  `k6_limitcont_dir` (a direction), G11, G12, G15 and G16.
- `Panel.feature_cols` has 154 columns:
  - 66 `z_`;
  - 53 `app_`, since the 13 always-applicable flags are left out (the 4 pooled ports and 9 generic
    features, `signals.ALWAYS_APPLICABLE`; reading PN-1);
  - 28 `id_root_` and 7 `id_cluster_`.
  The design's "under 100 columns" is still not met. Trimming the list is the lead's call (V2.3:
  "Open: the generic list").

## 2. Families and their signals

Applicability: the pooled port signals apply on every product's rows once known (all from t1).
Every other member signal applies only on the rows of the member's traded vehicles (reading SC-2),
and is "not applicable" (0, flag 0) on other rows. The share of rows where a signal applies
at each decision time (t1, t2, t3) comes from the timed build (section 7). The calendars are real;
prices are synthetic.

| Family | Signals | Rows | Applies at t1/t2/t3 (share of all rows) |
|---|---|---|---|
| K1..K7-cp1-01 (7, pooled) | `cp1_ret` | all 28 vehicles | 1/1/1 |
| K1..K7-cp2-01 (7, pooled) | `cp2_range`, `cp2_brk` | all 28 vehicles | 1/1/1 |
| K1..K7-cp3-01 (7, pooled) | `cp3_clv` | all 28 vehicles | 1/1/1 |
| K1-vwap-01 | `k1_vwap_dist` | MNQ, EQUITY_FULL_SESSIONS | .036/.036/.036 |
| K1-vxnband-01 | `k1_vxn_regime`, `k1_vxn_band` | MNQ, full sessions with a VXN row | .035/.035/.035 |
| K2-aucpre-01, K2-aucpost-01 | `k2_auction_mto`, `k2_auction_msince` (shared, SC-4) | rates, own tenor | .010/.010/0; 0/0/.010 |
| K2-fomcpost-01 | `k2_fomc_mto` | rates | .007 each |
| K2-monthend-01 | `k2_monthend_msince` | rates, N-1 and N | .020 each |
| K2-predrift-01 | `k2_predrift_move` | ZN, ZB, ISM Services days | 0/.003/.003 |
| K3-ldnmom-01 | `k3_ldnmom_trend` | 6E, 6J | 0/.066/.070 |
| K3-ldnrev-01 | `k3_ldnrev_move` | 6E, 6J, 6S month ends | 0/.005/.005 |
| K3-mehedge-01 | `k3_mehedge_req` | 6J month ends | .002 each |
| K3-ecbfix-01 | `k3_ecbfix_mto`, `k3_ecbfix_msince` | 6E | .002/0/0; .033/.035/.035 |
| K3-tkypost-01 | `k3_tkypost_msince` | 6J Tokyo business days | .034 each |
| K3-tkypre-01 | `k3_tkypre_msince` | 6J gotobi days | .007 each |
| K4-apipre-01 | `k4_apipre_ret` | MCL, standard WPSR Wednesdays | .006 each |
| K4-eiafade-01 | `k4_eiafade_move` | MCL, WPSR days | 0/.007/.007 |
| K4-eiamom-01 | `k4_eiamom_r3` | MCL, standard WPSR days | 0/.006/.006 |
| K4-ngpre-01 | `k4_ngpre_mto`, `k4_ngpre_msince` | NG, NGS days | .007/0/0; 0/.007/.007 |
| K4-ovr-01 | `k4_ovr_ret`, `k4_ovr_pct` | MCL, NG | 0/.072/.072 |
| K5-ovr-01 | `k5_ovr_ret`, `k5_ovr_pct` | MGC, MHG | 0/.072/.072 |
| K5-pmfix-01 | `k5_pmfix_move` | MGC, PM auction days | 0/.035/.035 |
| K5-preauc-01 | `k5_preauc_msince` | MGC, AM auction days | .035 each |
| K6-crushgap-01 | `k6_crushgap_gap` | ZS (reads ZM, ZL) | .035 each |
| K6-limitcont-01 | `k6_limitcont_dir` | HE, LE after a limit close | rare (0 on random walks) |
| K6-wasdepre-01 | `k6_wasdepre_drift` | ZC, ZS, WASDE days | 0/0/.003 |
| K7-expiry-01 | `k7_expiry_mto`, `k7_expiry_msince` | MBT, MBTX dates | .001/0/0; 0/.001/.001 |
| K7-montrend-01 | `k7_montrend_ret` | MBT Mondays | .007 each |
| K7-rev2h-01 | `k7_rev2h_ret` | MBT | 0/.036/.036 |
| K8-flight-01 | `k8_flight_ret`, `k8_flight_tail` | MGC (reads MES) | 0/.036/.036 |
| K8-oilcad-01 | `k8_oilcad_ret`, `k8_oilcad_z` | 6C (reads CL) | 0/.036/.036 |
| K8-wkndbtc-01 | `k8_wkndbtc_move` | MNQ (reads MBT), Mondays | .006 each |
| K5-fomc-01 | none | EXCLUDED | |
| K6-wasdepost-01 | none | EXCLUDED | |
| K9-anncday-01 | none | EXCLUDED | |

Each signal's `source` field gives the member file and lines. Every literal, date set and bar
instant comes from the member's own functions (`schedule`, `event_dates`, `event_wednesdays`,
`release_minutes`, `reference_dates`, `vxn_for`, `is_trade_day`, `is_trade_monday`,
`event_schedule`, `settlement_window`, `limit_ticks`) or module tables. Nothing is re-typed.

## 3. EXCLUDED (logged reasons, `signals.EXCLUDED`)

- **K5-fomc-01**: not available at any decision time. The FOMC 5-minute move is known at
  13:05 CT (`k5/fomc.py:39-40`), after the last metals decision time of 12:50 CT. Its most recent
  value on the same trade date is never available at t.
- **K6-wasdepost-01**: not available at any decision time. The WASDE 5-minute move is known at
  11:15 CT (`k6/wasdepost.py:44-45`), after the last grain decision time of 11:00 CT. The design's
  V2.3 example ("a WASDE 5-minute move before the release") cannot be applicable at any t of the
  V2.2 clock. The pre-release drift, K6-wasdepre-01, is coded.
- **K9-anncday-01**: input not covered on the training window. EC-K9
  (`reports/stage_e10_catalog_K9.json` members[0].event_dates) covers 2025-04-01..2026-06-17. The
  frozen release calendar has FOMC, NFP, CPI and PPI rows from 2019-05, but no GDP or ISM
  manufacturing rows. So the EC-K9 set cannot be formed on 2019-05-06..2024-02-29 without new
  data. The 2025 lapse dates are [unverified] and fall outside the training window either way.

Fixed-clock sides the clock never reaches are left out rather than kept as constant-zero columns
(reading SC-9):
- `k2_fomc_msince`: 13:00 CT is after 12:50.
- `k2_monthend_mto`: the 07:20 anchor is before 07:50.
- `k3_tkypost_mto`, `k3_tkypre_mto`: T_T falls on the evening of d-1.
- `k5_preauc_mto`: the AM auction is at 04:30 or 05:30 CT.

## 4. Literal-table coverage against the training window 2019-05-06..2024-02-29

Every table the coded families read covers the window, by its own declared range and by its
entries. "Entries in window" counts table rows dated inside the window.

| Module (strategy/members/) | Table | Entries span | Entries in window | Rows | Declared range |
|---|---|---|---|---|---|
| k1/_calendar | EQUITY_FULL_SESSIONS | 2019-05-01..2026-06-18 | 1205 | 1779 | 2019-05-01..2026-06-19 |
| k1/_calendar | EQUITY_TRADE_DATES | 2019-05-01..2026-06-19 | 1248 | 1846 | same |
| k1/_vxn | VXN_CLOSE | 2019-04-30..2026-06-18 | 1213 | 1794 | 2019-04-30..2026-06-19 |
| k1/_vxn | DROPPED_VXN | 2021-04-02..2024-02-01 | 3 | 3 | |
| k2/_releases | TREASURY_AUCTIONS | 2019-05-08..2026-06-11 | 231 | 340 | release calendar 2019-05-01..2026-06-21 |
| k2/_releases | FOMC_STATEMENT_DATES | 2019-05-01..2026-06-17 | 37 | 57 | same |
| k2/_releases | ISM_SERVICES_DATES | 2019-05-03..2026-06-03 | 57 | 86 | same |
| k2/_month_end | MONTH_END | 2019-05-30..2026-05-28 | 58 | 85 | EC-CAL rates |
| k3/_clocks | T_L, T_E | 2019-04-01..2026-06-19 | 1259 | 1885 | 2019-04-01..2026-06-19 |
| k3/_clocks | T_T | 2019-04-01..2026-06-19 | 1179 | 1761 | same |
| k3/_calendar | FX_FULL_SESSIONS | 2019-05-01..2026-06-18 | 1221 | 1797 | 2019-05-01..2026-06-19 |
| k3/_calendar | EW_BANK_HOLIDAYS | 2019-04-19..2026-05-25 | 41 | 63 | |
| k3/_calendar | TGT_CLOSING_DAYS | 2019-01-01..2026-12-26 | 27 | 48 | |
| k3/_calendar | GOTOBI_OR_TOKYO_MONTH_END | 2019-04-05..2026-06-15 | 271 | 404 | |
| k3/_calendar | TOKYO_BUSINESS_DAYS | 2019-04-01..2026-06-19 | 1179 | 1761 | 2019-04-01..2026-06-19 |
| k3/_calendar | MONTH_ENDS | 2019-05-31..2026-05-29 | 58 | 85 | |
| k3/_mehedge_signal | MEHEDGE_R_EQ_6J (Nikkei) | 2019-05-31..2026-05-29 | 58 | 85 | every ME(m) of the window |
| k4/_releases | WPSR | 2019-05-01..2026-06-17 | 250 | 369 | release calendar |
| k4/_releases | NGS | 2019-05-02..2026-06-18 | 247 | 367 | release calendar |
| k4/_releases | FEDERAL_MONDAY_HOLIDAYS | 2019-05-27..2026-05-25 | 34 | 46 | |
| k4/_releases | NYSE_NOT_FULL | 2019-05-27..2026-06-19 | 54 | 84 | |
| k4/_releases | API_DROPPED_WEEKS | empty | 0 | 0 | |
| k4/_calendar | ENERGY_FULL_SESSIONS | 2019-05-01..2026-06-18 | 1207 | 1784 | |
| k5/_releases | GOLD_AM_AUCTIONS | 2019-05-01..2026-06-19 | 1218 | 1802 | 2019-05-01..2026-06-19 |
| k5/_releases | GOLD_PM_AUCTIONS | 2019-05-01..2026-06-19 | 1208 | 1788 | same |
| k5/_calendar | METALS_FULL_SESSIONS | 2019-05-01..2026-06-18 | 1207 | 1784 | |
| k6/_calendar | GRAIN_FULL_SESSIONS, LIVESTOCK_FULL_SESSIONS | 2019-05-01..2026-06-18 | 1205 | 1780 | 2019-05-01..2026-06-19 |
| k6/_calendar | GRAIN_TRADE_DATES, LIVESTOCK_TRADE_DATES | 2019-05-01..2026-06-18 | 1214 | 1795 | same |
| k6/_calendar | LIVESTOCK_EARLY_HALT_CT | 2019-07-03..2025-12-24 | 9 | 14 | |
| k6/_wasde | WASDE_DATES | 2019-05-10..2026-06-11 | 58 | 85 | 2019-05-01..2026-06-19 |
| k6/_limits | LIMIT_PERIODS (HE, LE) | 2019-05-01..2026-06-19 | 12 periods | 2 roots | 2019-05-01..2026-06-19 |
| k6/_limits | DROPPED_LIMIT_DATES | 2026-06-01..2026-06-18 | 0 | 2 | |
| k7/_calendar | CRYPTO_FULL_SESSIONS | 2019-05-01..2026-06-18 | 1206 | 1782 | 2019-05-01..2026-06-19 |
| k7/_calendar | VENDOR_DEGRADED | 2020-02-27..2026-04-10 | 5 | 11 | |
| k7/_calendar | MBTX | 2021-05-28..2026-06-26 | 33 | 60 | 2021-05..2026-06 |
| k8/_calendar | FLIGHT_DATES, WKNDBTC_DATES | 2019-05-01..2026-06-18 | 1205 | 1779 | 2019-05-01..2026-06-19 |
| k8/_calendar | OILCAD_DATES | 2019-05-01..2026-06-18 | 1207 | 1783 | same |

Notes:
- **MBTX starts 2021-05.** MBT (Micro Bitcoin) was listed in May 2021, so before then there is no
  MBT contract to expire. "Not applicable" there follows from the member's own definition, not
  from missing data, and K7-expiry-01 is coded.
- **VXN** covers the window, so K1-vxnband-01 is coded. The design expected it might not.
- **Nikkei R_eq** covers every month-end of the window, so K3-mehedge-01 is coded. The design
  expected it might not.
- **The frozen release calendar** (`reports/stage_e2b_release_calendar.json`, loaded through
  `screening.stage_e_rules.load_release_calendar`, sha256 839f2437...7bcb8) covers 2019-05-01..
  2026-06-21, with 85 CPI instants. Every one of the 28 vehicles is listed. Releases inside the
  training window per vehicle:
  - MNQ 209; M2K 151; MYM 151;
  - ZT, ZF, TN, UB 488 each; ZN, ZB 545 each;
  - 6E, 6A, 6B, 6J, 6S, 6N 94 each; 6C 344;
  - MCL 791; NG 539;
  - MGC 210; MHG 210;
  - ZC 267; ZW, ZS, ZM, ZL, HE, LE 95 each;
  - MBT 210.
- **EC-K9** (`reports/stage_e10_catalog_K9.json`) holds 60 dates over 2025-04-01..2026-06-17:
  FOMC 10, NFP 14, GDP 9, ISM manufacturing 15 and inflation 14, less 2 same-day overlaps. None is
  in the training window (section 3).
- **The group calendars** (data/calendars via data.group_session) give each date's sessions, early
  halts and open intervals for 2019-05..2026-06. The DecisionRows clock reads them through
  `ml_route.inputs.day_times`.

## 5. Readings taken (each one is the worker's; the lead may overrule any)

- **TC-1** (clock): a date whose F_X is earlier than the group's regular flatten is excluded
  whole, as an early close. These are Topstep close-by days that are not group-calendar halts:
  2022-01-17, for example, is F 11:30 on FX. Under the rule such a date has fewer than three
  admissible times.
- **SC-2**: a member signal other than the pooled ports applies only on its traded vehicles'
  rows, computed from its own legs on the price-path bars. Cross-product information is G17's
  job. The pooled ports (lead ruling) apply on every product's rows. Missing for data reasons
  stays NaN there, as everywhere (V2.3).
- **SC-3**: a member's sign DV enters as the signed move (sign and size): vwap s_t, CP1 s,
  montrend s_t, predrift s, ldnmom S, eiamom r3, pmfix s, wkndbtc G and rev2h r. CP2's breakout
  enters as the latest close's distance beyond the opening range, and vxnband's breach as
  x = 1600 (close - C_prev) / (C_prev V).
- **SC-4**: K2-aucpre-01 and K2-aucpost-01 share one event (T_a) and its two signals.
- **SC-5**: K2-monthend-01 has no release instant, so its anchor is its own 07:20 entry bar.
- **SC-6**: a member guard that names a later bar is reduced to the bars read by t: ldnrev's
  T_L+4 entry bar, and eiamom's 14:29 entry bar.
- **SC-7**: the members' percentile and tail cuts enter as positions. ovr gives the share of
  reference values below r (ties half). flight gives r_k / |Q(d)|, where -1 is the member's
  trigger. oilcad gives z = r / s(d).
- **SC-8**: no VXN row (the prior equity date was an NYSE holiday) makes both K1-vxnband signals
  not applicable on d. The member does not trade d.
- **SC-9**: fixed-clock events enter as minutes-to (while ahead on d) and minutes-since (once
  passed), with availability t. The same-day flag is the sum of the two applicability flags. A side
  the clock never reaches is not a signal (section 3).
- **SG-1**: G1-G5, G7 and G8 are divided by sigma_X,d (v1 F1-F7). G17 is a log return x 1e4.
- **SG-2**: a G17 lead with no bar of the row's trade date by t, or the row's own cluster lead,
  is not applicable rather than missing. Lookups are as-of: the latest lead bar closed by t, and
  the latest bar at least 60 minutes before it.
- **SG-3**: G1-G3 are not applicable when the lookback bar falls outside the trade date's open
  session intervals. Examples: grains at 09:00 with 30 minutes back (the pause), livestock at t1.
  They are missing only when an in-session bar is absent.
- **SG-4**: G5 is not applicable after an early-halt date, since no C_X close exists.
- **NZ-1**: the z-score window counts the product's own row dates; an excluded date is not a slot.
  Statistics use the present values (not-applicable values are masked).
- **NZ-2**: a window of equal values gives z = 0 at that value and +-Z_CLIP away from it, so a
  constant feature never drops rows. Fewer than 2 values gives NaN.
- **PN-1**: `feature_cols` leave out the `app_` columns of always-applicable signals
  (constant 1): the 4 pooled ports and 9 generic features.
- **PF-1**: bar arrays hold views of the frame's price columns. Volume and instrument_id keep
  their dtype, and the trade date is int32. Window sums are gathered per row, with no
  full-length cumulative arrays (memory).

Missing for data reasons (V2.3): a member value whose bars are absent or carry two instrument_ids,
a lookback not yet full (sigma 20 dates, ovr/flight/oilcad reference floors, CP3's first complete
day), or a z-score warm-up excludes the row. `Panel.counts` gives the drops by cause and signal.

## 6. Causality evidence (tests)

`tests/test_ml_v2_signals.py`, parametrized over all 66 signals, the pooled ports included:
- every present value has `avail_ts_ns <= decision_ts_ns`;
- for two cut times t*, every bar with ts_event > t* - 60 s, on every root (a superset of the roots
  a signal reads), gets random values and 20% are removed. Values, flags and availability of all
  rows with decision_ts_ns <= t* stay unchanged, and the perturbation provably moves later rows;
- a spy on `ctx.bars` shows no signal reads a root outside its `roots_read`;
- `assert_causal` and `compute_signals` raise on a planted signal available after t;
- sigma_X,d is unchanged on dates up to the cut.

Further tests check that the pooled ports carry all 21 port families and hold values on every one
of the 28 products. Hand checks recompute values from bar lookups:
- the pooled CP1 on an equity, a grain (first bar at or after 19:00 on d-1) and a livestock
  product (the 08:30 bar);
- predrift, FOMC minutes, G1, mehedge R_eq,
tkypost minutes since, and eiafade. A planted limit-up and limit-down settlement checks
K6-limitcont's +1 and -1.

## 7. Timed realistic-size build (synthetic, measured once)

Setup: 28 vehicles plus MES on full-session random-walk bars for 2019-05-06..2024-02-29. That is
1,207 trade dates and 44.7 M bars; the frames take 2.24 GB, with a categorical trade_date and
uint32 volume. Run under `nice -n 10`, single process, `OPENBLAS_NUM_THREADS=1`.

| Stage | Wall time |
|---|---|
| Bars (generation) | 2.3 s |
| `decision_rows` (101,325 rows) | 6.1 s |
| `build_targets` | 2.4 s |
| `build_panel` (66 signals, z-scores, panel) | 6.4 s |
| `c_sigma_table` | 0.1 s |
| **Total** | **17.2 s** |

- Peak RSS: 3.11 GiB (`/usr/bin/time` 3,261,736 kB), of which 2.24 GB is the bar frames.
  These figures are from the rerun after pooling.
- Panel: 89,696 of 101,325 rows kept.
  - 11,541 dropped for missing data. These are dominated by G9's 20 + 120-date warm-up: each
    product's first ~140 dates.
  - 88 dropped for no statistic.

## 8. For the lead

1. The column count (154 feature columns after pooling) is above the design's "under 100".
2. G9's 120-date median removes each product's first ~140 dates (about 7 months) from the panel.
3. K6-wasdepost-01 and K5-fomc-01 are excluded by the V2.2 clock, not by data.
4. Ports are pooled per the lead's ruling: 4 signals carry the 21 families.
5. TC-1 excludes Topstep close-by dates: 31 FX dates in 2019-05..2026-06, for example.
