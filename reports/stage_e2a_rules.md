# Stage E.2a Task 5: the rules engine per product ($50K XFA)

Written by RulesCoder-OpusXHigh, 2026-09-25 (PDT). Design: docs/STAGE_E_DESIGN.md D9 (points 1-13), D8,
D11.1, D6, D1. Scope: the $50K XFA only. rules/xfa_rules.py (the MES engine) is not changed; its tests
pass unchanged. No market data was read. Sources are Topstep's help pages and CME's own publications:
the price-limit page, the Special Price Fluctuation Limits table, notices, and the client wiki.
Price-limit sources with verbatim quotes are in reports/stage_e2a_price_limits.json: 193 sources and
2,306 quotes. Each quote was checked twice by script as a verbatim substring of the fetched text, once
by the builder and once by an independent reader, with file sha256 checked too (0 missing, 0 hash
mismatches).

## 1. The modules

| Module | What it encodes |
|---|---|
| rules/products.py | Product table: 45 admissible contracts plus the ES and MES leg (47 rows). Fields: root, group, D6 sub-group, exposure, contract type (mini, micro, SIL, MBT), tick size and value, USD multiplier, vendor price factor, round-turn commission, and the source of each field. Also: lot-equivalent weights in tenths, the D9.5 member cap `member_cap_contracts`, the D9.11 volatility caps, and exact tick and USD arithmetic in vendor units. |
| rules/constraints.py | The member size check (per-product cap, and at most 1 lot-equivalent across legs), and the D9.12 CPI window: no opening fill on NQ, RTY, YM, GC, SI or HG (or the ES leg), with the entry skipped for the day; at most 3 contracts on MNQ, M2K, MYM, MGC, SIL or MHG (or MES). CPI instants are an input. |
| rules/sessions.py | F per group and date (D9.1, D9.13, brief item 6b). Regular F: 15:08 CT; grains 13:18 CT; livestock 13:03 CT. Grains are flat from 07:43 CT until the 08:30 CT open (the 07:45 pause). On a CME early close, F is the close minus 15 minutes. A full closure has no trading. Topstep's published holiday schedule also binds: F is the earliest of the three. Also handled: grains' scheduled late opens, the weekend, and the forced flatten. |
| rules/price_limits.py | D9.7, with per-product CME limit tables (generated from the JSON, and a test asserts equality). It covers Topstep's stop levels, the no-entry check, the forced exit (next open, exempt from the fill guard, event-window cost), and the R-08 locked-market fill. It also holds the per-product settlement windows and the settlement proxy. |

Interfaces for E.2b: `session_state(root, ts)` returns can_open and must_be_flat;
`required_flatten(...)`; `check_member_size(positions)`; `check_cpi_opening(root, fill_ts, qty,
cpi_releases)`; `settlement_window_utc(root, trade_date)` and `settlement_proxy(bars, lo, hi)`;
`check_price_limit_entry(...)` and `required_price_limit_exit(...)`, both taking a `DcbReading`;
`limit_prices(band, S)` and `locked_exit_fill(side, limit_up, limit_down, bars, tolerance)`.
Every price is in vendor units.

## 2. The product table

- Count: 47 rows, 45 admissible (D1 after U2) plus the ES and MES leg (D1.5). Every field is sourced.
  No field was left unsourced.
- Tick size and tick value come from reports/stage_e0_liquidity.json. The tick size is the numeric
  part of the string, which comes first (or sits in parentheses after a fraction, for rates).
  `tick_size x multiplier = tick_value` holds on every row.
- Vendor units (the lead's late note): ZC, ZW, ZS, ZL, HE and LE have `vendor_price_factor = 100`
  (Databento quotes them in cents); every other product has 1, ZM included (USD per short ton). A
  test checks this against BarsCoder's grid-scale probe in reports/stage_e2a_bars.json: 0 off-grid
  prices at 100x for the six, and 0 at 1x with many at 10x for the other 39. Note for the lead:
  bars.json still records the E.0 tick (for example ZC "0.0025"), not a vendor-unit tick. My check
  uses the probe instead.
- Commissions: F3.7 round-turn totals, plus the F3.6 increase applied as D8 says (MCL $1.72, MNG
  $1.92). The MES row repeats rules/xfa_rules.py's tick constants (test).
- Against sim/cost_inputs.py (CostCoder): 0 disagreements on commission, tick size, tick value or
  vendor factor across all 46 shared rows. MES is absent from the E.0 census, so it has no
  cost_inputs tick row.
- Member caps equal VehicleCoder's `cap_c` in reports/stage_e2a_vehicle_sizes.json for all 45
  (test).

## 3. Readings and flags (none is silent)

### Lot counting and caps
- **R-W1 (unpublished).** QM, QG and E7 have weight 1. Topstep names no weighting for them (facts
  F12.4, not_published). They are E-mini contracts, so D9.6's "minis 1" applies, as the K4 catalog
  already reads it. The conservative reading (the larger weight) gives the same answer.
- **R-W2 (unpublished).** M6E, M6A and M6B have weight 0.1. Topstep calls them "Micro" and leaves
  them out of its exception table (F12.4), so D9.6's "micros 0.1" applies. M6E and M6A stay
  non-candidates under U7; that is not a rules-engine matter.
- **R-V1.** SI and HG keep the D9.5 cap of 1, with the flag `MAY_BE_SUSPENDED`: Topstep's 50K
  figure for them is 0 at its discretion. This follows D9.11's encoded list and the lead's answer
  Q-1.

### Flatten times (D9.1, D9.13, brief item 6b)
- **R-F1 (for the lead): Topstep's holiday rule was 30 minutes in 2024 and 2025.** Topstep's article
  "Which holidays affect my trading schedule for Funded Level Accounts?" (8284222) was captured
  2024-01-05, 2024-10-14, 2025-03-16 and 2025-10-17. It reads: "Topstep requires traders in Funded
  Accounts to close all positions 30 minutes before the early close." It lists 11:30 CT for the 2024
  and 2025 US holidays (MLK, Presidents', Memorial, Juneteenth, July 4, Labor Day, Thanksgiving),
  11:45 CT for the Friday after Thanksgiving and Christmas Eve, and "Markets closed" for Good Friday,
  Christmas and New Year's Day. The 15-minute rule appears only in the new article 13350348, first
  captured 2026-02-19: "All account types must close positions 15 minutes before any early close."
  Encoded: F on a holiday is the earliest of the regular F, the CME early close minus 15 minutes, and
  Topstep's published close-by time for that date. For an early-close date missing from Topstep's
  list for a year it covers, that year's published lead applies (2025-07-03: 12:15 - 30 = 11:45). The
  30-minute finding is encoded in rules/ only (rules/sessions.py, `TOPSTEP_HOLIDAYS` and
  `TOPSTEP_EARLY_CLOSE_LEAD`). The MES engine (rules/xfa_rules.py, 15 minutes before an early close)
  was not changed. Its convention
  matches Topstep's 2026 article but not the 2024-2025 XFA rule, which matters for MES dates in
  2024-2025. The lead should decide whether that needs a note or a change.
- **R-F2.** In 2024 and 2025 Topstep's Combine rule was "Before 12:00 PM CT" (flat by the halt),
  against 11:30 for the XFA, on the article's example day. The engine encodes the XFA time for both
  phases, the stricter choice.
- **R-F3.** No Topstep schedule was retrieved for 2019-2023. F on those dates is D9.1's rule alone
  (the CME early close minus 15). Flagged: `TOPSTEP_SCHEDULE_YEARS = {2024, 2025, 2026}`.
- **R-F4.** Topstep's blanket US-holiday flatten binds where CME keeps a group trading. Example: FX
  on MLK Day 2025 trades to 16:00 CT at CME, but F = 11:30 (Topstep). On 2025-11-28 energy closes at
  13:45 CT at CME, but F = 11:45 (Topstep).
- **R-F5.** Juneteenth 2026: "SIM: 11:45 CT / Live: 11:10 CT". The XFA is SIM, so 11:45 is encoded.
  Good Friday 2026: 08:00 CT for every group.
- **R-F6.** Grains: no evening session into a scheduled late open (grains LATE_OPENS, lead ruling
  L-6). The unscheduled 2025-11-28 outage entries in other groups are not a rule and are not
  encoded.
- **R-F7.** F starts both windows: no new position from F and flat by F (D9.1). MES's separate
  "no new positions 2 minutes earlier" window is not used for Stage E.

### Price limits (D9.7)
- **Products with a hard daily limit (CME lock limits).** Grains ZC, ZW, ZS, ZM and ZL: price units,
  up and down, reset "for the first trade date in May and the first trade date in November" (CME
  grain FAQ). Livestock LE and HE: price units, reset each June (LE) and September (HE), per CME's
  livestock notices. Equity NQ, MNQ, RTY, M2K, YM and MYM (and the ES and MES leg): up and down
  `eth_pct` from 17:00 to 08:30 CT and from 15:00 CT on; 7% down only from 08:30 CT until 14:25 CT;
  20% down only from 14:25 to 15:00 CT. The reference is the fixing price (VWAP 14:59:30-15:00:00
  CT). `eth_pct` was 5% until the change to 7%, first seen for trade date 2020-11-02, and 7% after.
  The RTH window ran to 15:00 CT until the 14:25 rule, first seen for trade date 2019-11-08.
- **R-L1: products with only dynamic circuit breakers (DCB). Settled by lead ruling L-13
  (2026-09-25 06:58 PDT): the 2% rule does not apply to them.** These are rates, FX, energy, metals
  and MBT. CME's price-limit page says "These products use Dynamic Circuit Breakers" on every tab
  for these groups, and the Special Price Fluctuation Limits table gives only a "Dynamically
  Calculated Variant". A DCB halts trading for about two minutes and then resumes. Two readings are
  encoded as a switch (`DcbReading`), and both keep known-answer tests:
  - **NO_LOCK_LIMIT (the default, `DCB_READING_DEFAULT`, ruling L-13): no restriction.** The
    ruling's reasons:
    1. Topstep's prohibited-conduct text is "Holding a position within 2% of a product's price lock
       limit".
    2. A dynamic circuit breaker is a temporary halt that never locks the market, so these products
       have no price lock limit.
    3. Frozen D9.7 speaks of locked markets, and its examples are grain and equity limits.
    4. The alternative reading would make Topstep-permitted Treasury futures (ZT, ZF, ZN)
       untradeable every day, which Topstep's own permitted-products list contradicts.
  - VARIANT_AS_LIMIT (the alternative, available through the switch): the DCB variant, taken as a
    daily limit around the prior settlement. It was the module default before L-13. Its
    consequences in the research window:

    | Product | Variant | Band under VARIANT_AS_LIMIT |
    |---|---|---|
    | ZT, ZF, ZN | 0.75, 1.50, 2.00 points (below 2% of price) | no tradable band: the products cannot be traded at all |
    | TN | 3.00 points | about +/-0.6% |
    | ZB | 4.50 points | about +/-1.9% |
    | UB | 8.00 points | about +/-5% |
    | FX | 4% | +/-2% |
    | energy, metals, MBT | 10% | +/-8% |

  The hard-limit tables (grains, livestock, and equity including ES and MES) are unchanged and apply
  under either setting (test `default_leaves_the_hard_limit_products_unchanged`).
  **For the user:** whether Topstep applies its 2% rule to circuit-breaker-only products is a
  question Topstep can answer. It could go in the same support email as the M6E/M6A star question
  (U7).
- **R-L2.** Only the initial limit is encoded. The expanded limit, used the day after a limit close,
  is about 150% of it, so the initial limit is the stricter choice.
- **R-L3.** Equity RTH: the 7% level is kept from 08:30 to 14:25 CT even after a 7% halt, when CME
  moves to 13%. The stricter choice.
- **R-L4.** At a stop level counts as beyond it ("touches", as the MLL is read).
- **R-L5. Bracketed periods.** A change fell between two captures and no CME-stated date was found,
  so the narrower limit is encoded:

  | Product | Period(s) |
  |---|---|
  | ZW | 2022-01-29..2022-03-06 (CME's wheat limit rose to $0.85 by 2022-03-07; no notice read) |
  | LE | 2024-10-09..2024-11-05 (0.0750 to 0.0650, unexplained, holdout-2); 2026-05-19..2026-06-19 (0.0725 encoded; 0.0850 was in force by 2026-08-20; the June 2026 reset date is not quoted) |
  | HE | 2020-04-02..04-21; 2020-08-20..09-21; 2024-09-04..09-12; 2025-08-30..09-01 (no trade date) |
  | equity | 2019-09-24..2019-11-07 (15:00 RTH end kept); 2020-10-01..2020-11-01 (5% kept) |
  | CL, MCL, QM, RB, HO, NG, MNG, QG | 2021-07-25..2022-01-23 (DCB 15% or 7% to 10%; 10% or 7% kept) |
  | metals | 2019-07-19..2020-06-17 (DCB 5% to 10%; 5% kept) |

  In the research window only LE (24 weekdays) and HE (1 weekday, Labor Day) are bracketed.
- **R-L6. Carried (unverified).** DCB variants for FX, energy and metals from 2026-03-11 to
  2026-06-19 (73 research weekdays) are carried past the last capture of the Special Price
  Fluctuation Limits table (2026-03-10). CME's price-limit page confirms the DCB regime through
  2026-08-20, but not the variants. Treasury variants (price-limit page, 2026-05-18 and 2026-08-20)
  and MBT's +/-10% (crypto tab) are sourced through the window. This matters only under the
  alternative reading VARIANT_AS_LIMIT, not under the L-13 default.
- **R-L7. Pending (unsourced, confirmation window only).** These periods raise `LimitPending` only
  under the alternative reading VARIANT_AS_LIMIT. Rates, 2019-05-01..2020-10-09: CME ran fixed-level circuit breakers then, not
  DCB. FX, 2019-05-01..2022-01-23: fixed 400-tick levels. Energy and metals,
  2019-05-01..2019-07-17: no capture between 2018-01 and 2019-07. Under the NO_LOCK_LIMIT default
  nothing is pending. No hard-limit product has a pending period in 2019-05-01..2026-06-19.
- **R-L8.** CME suspends grain and livestock limits in the spot month near delivery. This is not
  encoded: the limit always applies, the stricter choice. The continuous series roll earlier anyway.

### Settlement proxy
- **Settlement windows.** Source: CME wiki "Daily Settlement Time Details", version of 2025-01-03,
  quoted.

  | Product | Window (CT) |
  |---|---|
  | equity | 14:59:30-15:00:00 (the fixing window, R-P4) |
  | rates, FX | 13:59:30-14:00:00 |
  | energy | 13:28-13:30 (14:28-14:30 ET) |
  | gold | 12:29-12:30 |
  | silver | 12:24-12:25 |
  | copper | 11:59-12:00 |
  | grains | 13:14-13:15 |
  | livestock | 12:59:30-13:00:00 |
  | MBT | 14:59-15:00 |

  Cross-check against D6 (the calendar modules' `day_session_ct`, which the CalendarBuilders
  confirmed): every window ends at D6's C for every product. **No disagreement.** The equity
  settlement was 15:15 CT before 2020-10-26; the equity CalendarBuilder already reported that. It is
  not used here, because CME computes the equity limits from the fixing price.
- **R-P1.** Lock detection tolerance defaults to 0. The proxy settlement may put the computed limit a
  few ticks off CME's, so E.2b may pass a tolerance in vendor units.
- **R-P2.** The proxy is the volume-weighted close of the bars whose minute overlaps the window.
  With no volume in the window, it falls back to the last close before the window end, and the
  method is flagged.
- **R-P3.** On an early-close day the window is the regular length ending at the halt. The
  exception is rates, which use the module's EARLY_SETTLEMENT_CT (for example 11:59:30-12:00 on
  2025-12-24). CME moves settlement to group-specific times on those days. FX's early-settlement
  days listed in its sources report (12:00 CT on 2019-12-31, 2025-11-28 and 2025-12-24; 10:00 CT on
  2023-04-07) are not a table in data/calendars/fx.py, so the regular 14:00 window is used there.
- **R-P4.** For equity, CME's limit reference is the fixing price, and Topstep says "settlement".
  The fixing window is used.
- **R-P5.** Topstep: "Price limits are calculated from the previous day’s settlement price. They
  update at 4:05 PM CT after each session". The reference is therefore held for the whole trade
  date, including 15:00-15:08 CT. CME's own reset at 15:00 CT is not modeled.

### CPI
- **R-C1.** The window is inclusive: [CPI - 5 min, CPI + 5 min]. A closing fill is never restricted.
  The release calendar is E.2b's input.

## 4. Tests: tests/test_e2a_rules.py, 110 cases in 41 functions

A mutation check planted 23 errors (commissions, the vendor factor, weights, caps, the grain pause,
F, early-close leads, Topstep's schedule, late opens, the 2% buffer, the stop-level touch, the RTH
window, the lock rule, the settlement window, price-unit scaling, the CPI limit and window
endpoints, the lot cap, the DCB default, the DCB percentage, and the no-limit reading leaking into
hard-limit products). All 23 were caught.

| Test | What it proves |
|---|---|
| `product_table_is_the_45_admissible_contracts_plus_the_leg` | 45 plus ES and MES; groups equal GROUP_OF_PRODUCT; tick x multiplier = tick value on every row |
| `ticks_equal_the_e0_liquidity_census` | tick size (numeric part parsed) and tick value equal E.0 for all 46 census rows |
| `mes_row_repeats_the_mes_engine_constants` | the MES row equals rules/xfa_rules.py (0.25, $1.25, 10 micros per mini) |
| `commissions_are_topstep_f37_plus_the_f36_increase` | every commission equals F3.7; MCL $1.72 and MNG $1.92; $ arithmetic |
| `vendor_price_factor_matches_the_bar_builds_grid_probe` | factor 100 exactly for ZC, ZW, ZS, ZL, HE, LE, each at 0 off-grid prices at 100x; the rest on the 1x grid, not the 10x grid |
| `tick_value_arithmetic_in_vendor_units` (16 cases) | ticks and USD in every group: NQ, MNQ, ZN, ZT ($7.8125), 6J, M6B ($0.625), CL, MNG, GC, SIL, ZC and ZL in cents, ZM in USD, HE and LE in cents, MBT |
| `off_grid_price_and_bool_are_refused` | an off-grid price and a USD price for a cent product are refused; fixed-point conversion |
| `lot_weights_d96_and_the_unpublished_readings` | minis 1, micros 0.1, SIL 0.2, MBT 1; the QM, QG, E7 and M6x readings |
| `member_cap_is_floor_one_lot_then_the_volatility_cap` | caps per product; equal to VehicleCoder's cap_c |
| `volatility_caps_are_the_50k_figures` | the D9.11 table; SI and HG flagged; caps enforced |
| `member_size_check` (11 cases) | per-product cap and the 1-lot sum across legs (signs do not net) |
| `cpi_window` (12 cases), `cpi_window_refuses_naive_timestamps` | skip on minis at both window edges, open 1 s outside; micro 3 allowed and 4 refused; CL unaffected; closing fills unaffected |
| `regular_flatten_time_per_group` (8 cases) | F = 15:08 for 6 groups, 13:18 for grains, 13:03 for livestock; open 1 minute before F, flat at F |
| `early_close_flatten_is_the_close_minus_15` (9 cases) | early close minus 15 in every group; forced flatten at F and not before |
| `full_closure_has_no_trading` (4 cases) | a closure is flat all day; the evening before stays closed; the next evening opens |
| `grain_pause_and_overnight_session` | 07:42 open, 07:43 flat, 08:30 open, 13:18 flat, 19:00 reopen; the forced exit reason |
| `livestock_close_and_no_evening_session` | 08:30 to 13:03 only |
| `weekend_is_flat_from_friday_f_to_sunday_reopen` | Friday F to Sunday 17:00 |
| `holiday_flatten_is_the_earlier_of_topstep_and_cme` (7 cases, real calendars) | FX on MLK 2025 = 11:30; MLK 2026 = 11:45; 2025-07-03 = 11:45 (the 2025 rule); CL on 2025-11-28 = 11:45; Good Friday 2026 = 08:00; a normal day = 15:08 |
| `topstep_markets_closed_days_and_cme_grain_closures` | Topstep's "Markets closed" days and CME's grain and livestock closures |
| `grain_scheduled_late_open_after_a_closure` | no overnight grain session after Thanksgiving 2025; the 08:30 open |
| `every_research_window_weekday_has_a_rule_for_every_product` | the calendars resolve every weekday of 2025-04-01..2026-06-19 for all 45; F never later than the regular F |
| `limit_table_equals_the_report_json` | the code table equals reports/stage_e2a_price_limits.json period by period |
| `limit_table_covers_the_research_window_without_pending` | contiguous periods; no pending period in the research window |
| `hard_limits_exist_only_for_grains_livestock_and_equity` | the hard-limit product set |
| `grain_limits_reset_on_the_first_trade_dates_of_may_and_november` | ZC 0.30 to 0.35 on 2025-05-01 and back to 0.30 on 2025-11-03; ZS 0.85 in May 2026; the LE June and HE September resets |
| `pending_period_raises_only_under_the_alternative_dcb_reading` | LimitPending under VARIANT_AS_LIMIT; no restriction under the default |
| `percentage_limit_stop_levels_topstep_es_example` | Topstep's own ES 2,814 example: 2,898.42 and 2,729.58 at 5%; 2,673.30 at 7% down |
| `equity_bands_by_time_of_day_in_the_research_window` | 7% up and down overnight, 7% down in RTH, 20% down after 14:25, 7% after 15:00 |
| `price_unit_limit_stop_levels_grains_and_livestock` | ZC in cents (S 440, limit 35: 466.20 and 413.80; limit prices 475 and 405); LE 222.85 and 217.15; ZM in USD 314 and 286 |
| `entry_refused_and_exit_forced_beyond_a_stop_level` | entry refused at or beyond either level; the exit is next open, exempt from the fill guard, event-window cost |
| `default_dcb_reading_is_no_lock_limit_ruling_l13` | the default is NO_LOCK_LIMIT; the 32 DCB-only products are exactly rates, FX, energy, metals and MBT; none has stop levels, an entry refusal or a forced exit under the default; ZT, ZF, ZN tradable |
| `default_leaves_the_hard_limit_products_unchanged` | ZC, NQ and LE stop levels are identical under both readings |
| `dcb_products_under_the_alternative_reading` | VARIANT_AS_LIMIT: CL levels, limit prices and forced exit; 6E, GC, MBT variants; ZN has no tradable band; UB 120.70 and 109.30 |
| `locked_market_exit_waits_for_a_bar_trading_through_the_limit` | R-08: a sell waits through locked bars and fills at the open of the first bar trading through; buys against limit-up; no lock without a limit on that side; tolerance |
| `regular_settlement_windows` (10 cases) | one window per group and sub-group |
| `settlement_window_ends_at_d6_c_for_every_product` | the D6 cross-check against the calendar modules |
| `early_settlement_and_early_halt_windows` | rates EARLY_SETTLEMENT_CT; the early-halt window; closure refused; UTC conversion |
| `settlement_proxy_is_the_volume_weighted_close` | VWAP of closes; a 30-second window; the no-volume fallback; no bars |
| `mes_engine_constants_unchanged` | the MES engine's F, leads and position limit |

Existing rules tests: tests/test_xfa_rules.py and tests/test_xfa_rules_sequences.py pass unchanged
(67 tests, run together with the new file: 177 passed after ruling L-13).

Full suite (`nice -n 10 uv run pytest -q -p no:cacheprovider`), run before ruling L-13, which
changed only rules/price_limits.py's default and tests/test_e2a_rules.py: `1889 passed, 2 skipped, 1 xfailed, 53 warnings in 792.91s (0:13:12)` (run 06:43-06:57 PDT, machine load 16-20 from another worker's job).

## 5. Files

- rules/products.py, rules/constraints.py, rules/sessions.py and rules/price_limits.py (new).
  rules/xfa_rules.py is unchanged.
- tests/test_e2a_rules.py (new).
- reports/stage_e2a_price_limits.json: the limit periods per product, with status and source ids;
  coverage; settlement windows and the D6 cross-check; each of the 166 parsed price-limit page
  captures; the spreadsheet rows; and the 193 sources with verbatim quotes, file paths and sha256.
- Builder scripts (scratch, not repo): e2a_rules_cache/build_price_limits.py, finalize_json.py and
  gen_table.py. They generate the JSON and the code table from the fetched files in the same
  cache directory (166 price-limit page captures, 16 spreadsheet captures, wiki pages, Topstep
  pages).
