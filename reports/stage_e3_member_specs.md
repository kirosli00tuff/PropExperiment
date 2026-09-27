# Stage E.3 member specifications, cluster K2 (Task 1)

Written by the Stage E.3 lead (Opus 5.5, xhigh), 2026-09-26 23:47-23:52 PDT, before
any member code exists and before any K2 bar has been read by this session. It restates each frozen
entry as the code must implement it, with line references, and records every reading the lead took
where the entry leaves a detail open (section 10). It changes no rule. A reading is the narrowest
one the text allows unless the text fixes the detail by reference (then the reference governs and
the reading says so).

Sources and their state:
- C = reports/stage_e0_catalog_K2.md, frozen by reports/stage_e1_freeze.json (manifest sha256
  96166eb3...). Line numbers below are this file's. E.1 edits to K2 (reports/stage_e1_changes.md
  K2-00..K2-03, K2-10, K2-11) touch only the banner, the excluded K2-ml-01 and the superseded CP2
  notes: no active member's rule changed. K2-ml-01 is excluded (U6) and is not coded.
- D = docs/STAGE_E_DESIGN.md (frozen): D6 table lines 364-366 (the port rule texts), rates session
  row line 393 (O 07:20, C 14:00, F 15:08), D9.1 lines 482-495, D9.3 lines 499-505, D9.5a lines
  515-521, D9 floor lines 603-610, coverage check lines 612-614.
- Source-window amendment (reports/stage_e2a_source_window_amendment.md lines 36, 44-48): K2-predrift-01
  loses "source-overlap"; K2-cp1-01, K2-cp2-01, K2-cp3-01 and K2-monthend-01 keep it; K2-aucpre-01,
  K2-aucpost-01 and K2-fomcpost-01 carry it by R-04 (C lines 270, 353, 407). Labels matter only for
  the confirmation session.
- Vehicles (reports/stage_e2a_vehicles.md, frozen table reports/stage_e2a_vehicles.json via
  screening.stage_e_frozen): ZT and ZF status "undersized", ZN, TN, ZB, UB "chosen", q_c = 1 for all
  six; the frozen runner trades both statuses (stage_e_frozen.TRADED_STATUSES). Operative eps (net
  ticks per contract per day, stage_e2a_epsilon.json): ZT 5, ZF 6, ZN 3, TN 4, ZB 2, UB 2.
- Frozen per-root values read through screening.stage_e_frozen.load_frozen_tables() and
  rules.products.product(root) (checked 2026-09-26 23:44): day_session_ct = (07:20, 14:00) for all
  six; vendor_tick ZT 0.00390625, ZF 0.0078125, ZN 0.015625, TN 0.015625, ZB 0.03125, UB 0.03125.
  F (rules/sessions.py, enforced by the engine) = 15:08 CT on a regular day, earlier on early-halt
  days (for example 11:45 CT on 2025-11-28).
- Release calendar reports/stage_e2b_release_calendar.json (frozen harness input, sha256
  839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8): TREASURY_AUCTION rows (EC-AUC,
  built with the catalog's filter, reports/stage_e2b_release_sources_named_log.md lines 81-99, all
  nominal tenors, tenor = id suffix from original_security_term), FOMC rows (EC-FOMC, 57, all
  14:00 ET, the cancelled 2020-03-18 meeting absent, unscheduled meetings absent), ISM_SERVICES rows
  (EC-ISM, 86, all 10:00 ET). Research-window counts match the catalog (C lines 323-328, 445-447,
  512-514): 2Y 13 (3 at 11:30 ET), 5Y 15, 10Y 15, 30Y 15, FOMC 10, ISM 15.
- EC-CAL = the D10 rates calendar, data/calendars/rates.py, read through
  data.group_session.load_group_calendar("rates") (is_trade_date, trade_dates_between,
  early_halt_ct). Bars carry `early_halt_ct` per CT calendar date (data/group_session.py line 584).

What the member does NOT implement (the engine and runner do, and a member must not duplicate or
second-guess them): the window's trade dates and the removal of roll-blackout dates (runner step 2;
C4's roll-blackout clause is met there); 2026-06-18/19 (UR-1); F and the forced flatten (D9.1);
costs and the event-window cost (D8); the event-minute fill guard (D9.5a); the entry cap and the
2-minute minimum hold (D9.3a/b, refused and counted by the engine); the skip of an entry whose fill
would come less than 2 full minutes before F (screening/stage_e_rules.py line 399); price-limit
proximity (D9.7); the CPI window (D9.12, not a K2 product); the lot-equivalent cap (D9.5).

---

## 0. Common to all eight members

S0.1 Legs. Each member reads and trades exactly one leg: the traded exposure's own vehicle,
`LegSpec(root, True)`. No signal legs. (C lines 140, 184, 230, 271, 354, 408, 466, 537.)

S0.2 Declarations. One `MemberDecl` per (member, exposure) trial, 44 in all (C section 6 lines
747-757; header banner line 6: 44 confirmation trials). Label `"<member id> <ROOT>"`, for example
`"K2-cp1-01 ZT"`; the member object's `name` equals its label. Module per member under
strategy/members/k2/; one zero-argument factory per exposure, `make_zt`, `make_zf`, `make_zn`,
`make_tn`, `make_zb`, `make_ub` (only the exposures the member trades). Ordinals (L-18): catalog
order, then ZT, ZF, ZN, TN, ZB, UB:

| Member | Module | ZT | ZF | ZN | TN | ZB | UB |
|---|---|---|---|---|---|---|---|
| K2-cp1-01 | strategy.members.k2.cp1 | 1 | 2 | 3 | 4 | 5 | 6 |
| K2-cp2-01 | strategy.members.k2.cp2 | 7 | 8 | 9 | 10 | 11 | 12 |
| K2-cp3-01 | strategy.members.k2.cp3 | 13 | 14 | 15 | 16 | 17 | 18 |
| K2-aucpre-01 | strategy.members.k2.aucpre | 19 | 20 | 21 | 22 | 23 | 24 |
| K2-aucpost-01 | strategy.members.k2.aucpost | 25 | 26 | 27 | 28 | 29 | 30 |
| K2-fomcpost-01 | strategy.members.k2.fomcpost | 31 | 32 | 33 | 34 | 35 | 36 |
| K2-predrift-01 | strategy.members.k2.predrift | - | - | 37 | - | 38 | - |
| K2-monthend-01 | strategy.members.k2.monthend | 39 | 40 | 41 | 42 | 43 | 44 |

S0.3 Size. Every entry is `q_c` contracts of the vehicle, read from
`load_frozen_tables().vehicles[root].q_c` (= 1), never a literal (C6 lines 58-61; template lines
42-43). Every exit closes the whole position.

S0.4 Clock. America/Chicago. "The bar at hh:mm" of trade date d is the bar with `trade_date == d`
whose open (`ts_event_ns`) is hh:mm:00 CT on CT calendar date d; the one exception is CP1's
Globex-open bar at 17:00 CT on the calendar day before d (L-03, L-05). O and C come from
`load_frozen_tables().day_session_ct[root]` = (07:20, 14:00) (template lines 44-45; D line 393);
every other clock time below is a literal of the entry, written in the module as a named
constant or as an offset from O, C, T_a or T as the entry states it. A bar is usable at its close
(C1 lines 42-44); `on_minute` is called at the bar's close with the bar in `view.bars[root]`.

S0.5 Orders. Market intents only (`leg_market_intent`), filled by the engine at the open of a later
bar of the leg (C2 lines 45-46). No limit orders, stops or brackets.

S0.6 Named entry bar. "Market intent on the bar at X" (an entry) is emitted only when the view's bar
is the bar at X. If that bar is missing (`view.bars[root] is None` at X, or no call at X), there is
no entry that trade date (L-04). An entry is emitted at most once per trade date per member
instance, and never while a position or a pending order exists on the leg.

S0.7 Exits. Every exit is sent on the first present bar at or after the named exit bar, while the
position is non-zero and no exit order is pending (C4 line 54: "If an exit's named bar is missing,
the exit is sent on the first later bar"; D6 CP1 and CP3 say "first bar at or after"). If an exit
intent is refused by the engine, it is sent again on the next present bar under the same condition
(L-22). The engine's forced flatten at F is the backstop (C4 line 55).

S0.8 Early halts (C4 lines 51-53, five new members; CP3 through Family H). A trade date is an
early-halt date when the entry decision bar (a bar of CT date d) carries `early_halt_ct` not None.
No entry on such a date (L-11). CP1 and CP2 follow D6 and do not test it (the engine's F governs).

S0.9 Instrument guard (C4 line 53, five new members). Every bar the rule reads at or before the
entry decision carries the entry decision bar's `instrument_id`, else no trade that date (L-12,
L-13). Exit bars are not guarded.

S0.10 Prices. Every price comparison and sign is computed in integer vendor ticks,
`round(price / vendor_tick)` with `rules.products.product(root).vendor_tick` (template lines
39-41), never with a literal tick (L-19).

S0.11 Event and calendar data. A member cannot read a file (template lines 9-21). The dates it
needs are literal tables in the cluster package, generated from the frozen sources above and
pinned by tests that recompute them from those sources (L-01):
- strategy/members/k2/_releases.py (MemberCoder-B): TREASURY_AUCTIONS (date, tenor, T_a CT) for
  tenors 2Y, 5Y, 10Y, 30Y, less any auction the lead drops on the C9 XML check (L-02);
  FOMC_STATEMENT_DATES (instant 13:00 CT); ISM_SERVICES_DATES (instant 09:00 CT); and the source
  sha256.
- strategy/members/k2/_month_end.py (MemberCoder-A): (N-1, N) per calendar month from EC-CAL (L-16).

S0.12 trading_windows (D9 coverage check, D lines 612-614; interface lines 51-61). Per member, the
CT intervals below on its one leg (L-17). The interface has no event-date condition, so the
check measures these minutes on every research date.

| Member | Intervals [start, end) CT |
|---|---|
| CP1 | (17:00, 17:01) on day -1; (07:49, 07:50); (13:29, 14:00) |
| CP2 | (07:20, 15:08) |
| CP3 | (07:20, 14:00) |
| aucpre | (07:29, 12:00) |
| aucpost | (10:34, 15:06) |
| fomcpost | (13:29, 15:06) |
| predrift | (08:30, 09:06) |
| monthend | (07:20, 15:06) |

S0.13 Topstep checks common to all (C lines 168-178 and each entry's list): flat by F (engine);
market orders only; at most one entry per trade date (D9.3a floor of 20 is never approached);
every hold is at least 15 minutes by rule (D9.3b); no stops, brackets or passive fills (D9.4); no
starred product (D9.8); size 1 lot-equivalent, half the XFA's 2-lot maximum, so holding through a
release is allowed (D9.5, F6.3); position limit 1 contract; price limit per D9.7 in the engine.

---

## 1. K2-cp1-01 (core port CP1, intraday momentum). C lines 137-181; D line 364

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicle | ZT, ZF, ZN, TN, ZB, UB; each its own vehicle, q_c = 1 | C 140-143; S0.3 |
| Signal | s = sign(close of the bar at O+29 = 07:49 minus open of the trade date's first bar), in ticks | C 147-148, 152-153; D 364 |
| Trade date's first bar | the bar opening 17:00 CT on the calendar day before d, with trade_date d (the Globex open) | C 152-153; L-05 |
| Signal-bar guard | both signal bars (17:00 on d-1, 07:49 on d) present and carrying one instrument_id, else no trade | C 150; L-06 |
| Zero signal | s = 0: no trade | C 149 |
| Entry | market intent on the bar at C-31 = 13:29, side buy if s > 0, sell if s < 0; fills at the 13:30 open | C 148-149, 154; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 13:58; fills nominally at the 13:59 open | C 149-150, 155-156; S0.7 |
| Hold | 29 minutes nominal | C 157 |
| Early halts | not tested by the member (port; on an early-halt day F precedes 13:30 and the engine refuses the entry) | C 49-50 ("The ports follow D6 as written") |
| Parameters (literals) | O+29 = 07:49, C-31 = 13:29, C-2 = 13:58; no grid | C 162 |
| Release instants read | none | C 158-160, 180 |
| Trials in N | 6 | C 181 |
| Topstep | flat by F (last fill 13:59); market; one trade a day; 1 contract; on FOMC days the position starts 30 minutes after the 13:00 statement | C 168-178 |

## 2. K2-cp2-01 (core port CP2, opening-range breakout). C lines 183-227; D line 365

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicle | ZT, ZF, ZN, TN, ZB, UB; q_c = 1 | C 184-186 |
| Opening range | OR_high = max high, OR_low = min low of the present bars opening in [O, O+15) = [07:20, 07:35) of CT date d; no OR bar: no trade | C 190, 197; L-08 |
| Buffer | 4 ticks of the product: 4 x vendor_tick (ZT 0.015625, ZF 0.03125, ZN 0.0625, TN 0.0625, ZB 0.125, UB 0.125 pt) | C 191, 199-200; D 369-372 |
| Eligible bars | bars opening in [O+15, C) = [07:35, 14:00) of CT date d; no entry from 14:00 on | C 191-193, 198; D 365 (amended) |
| Entry | the first eligible bar whose close >= OR_high + buffer: buy; <= OR_low - buffer: sell; market intent on that bar; one entry per trade date (the first qualifying bar ends the day's entry search, whatever the engine does with the intent) | C 191-192, 201; L-08 |
| Exit | 75 minutes after the fill, counted as the MES module counts it: count the present bars seen while the position is non-zero, starting after the entry decision bar; on the 75th, a market intent closing the position (fills at the next open); or the engine's forced flatten at F if earlier. No exit at C-2 (the template's C-2 exit is NOT part of CP2). | C 192-193, 202-203; strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py lines 147-152; L-07 |
| Hold | 75 minutes nominal, less if F intervenes | C 204 |
| Instrument guard | none (D6 and B-H1 have none) | L-08 |
| Early halts | not tested by the member (port; the engine's F and entry skip govern) | C 49-50 |
| Parameters (literals) | OR 15 minutes, buffer 4 ticks, hold 75 minutes; no grid | C 208-209 |
| Release instants read | none | C 205-206 |
| Trials in N | 6 | C 221 |
| Topstep | flatten by the engine at F; market; one trade a day; may hold through a 09:00 release at 1 lot-equivalent | C 212-219 |

## 3. K2-cp3-01 (core port CP3, prior-close location). C lines 229-266; D line 366

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicle | ZT, ZF, ZN, TN, ZB, UB; q_c = 1 | C 230-232 |
| Daily bar of trade date d | from the bars of trade date d on CT date d opening in [O, C) = [07:20, 14:00): O_d = open of the 07:20 bar, H_d / L_d = max high / min low over the present bars, C_d = close of the 13:59 bar (C-1) | C 235-236, 240-241 |
| Complete day (Family H) | the 07:20 and 13:59 bars exist, the date is not an early halt (no bar of CT date d carries early_halt_ct), and all bars in [07:20, 14:00) carry one instrument_id; finalised when a bar of a later trade date arrives | C 237, 242-243; _mechanics.py lines 10-15 |
| "d-1" (Family H) | the most recent COMPLETE daily bar of a trade date before d; incomplete days are dropped | _mechanics.py lines 13-15; C 237 ("rules as Family H"); L-09 |
| Warm-up | no complete earlier bar yet (the window's start): no trade | _mechanics.py lines 20-21 |
| Instrument guard (Family H, 1 bar) | d-1's instrument_id equals the instrument_id of day d's 07:20 bar, else no trade | C 244; _mechanics.py lines 16-19; H6 GUARDED_BARS = 1 |
| Condition | Range = H - L of d-1 in ticks, required > 0; CLV = (C - L) / (H - L) in ticks; CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict); otherwise no trade | C 237-238, 245-246; h6_prior_close_location.py lines 27-43 |
| Day d exclusion (Family H) | a trade date d whose bars carry early_halt_ct: no trade (read from day d's 07:20 bar) | _mechanics.py line 34; L-09, L-11 |
| Entry | market intent on the 07:20 bar of d (fills at the 07:21 open); the 07:20 bar must exist | C 238, 247; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 13:58 (fills nominally at the 13:59 open) | C 238, 248; S0.7 |
| Hold | about 398 minutes | C 249 |
| Parameters (literals) | CLV cuts 0.2 and 0.8, lookback 1; no grid | C 253 |
| Release instants read | none | C 250-251 |
| Trials in N | 6 | C 266 |
| Topstep | last fill 13:59; market; holds through morning releases, the 12:00 CT auction closes and the 13:00 FOMC statement at 1 lot-equivalent | C 256-264 |

## 4. K2-aucpre-01 (pre-auction concession). C lines 268-349

| Field | Rule | Reference |
|---|---|---|
| Exposures, tenor match | ZT: 2-Year; ZF: 5-Year; ZN and TN: 10-Year; ZB and UB: 30-Year; reopenings included; 3-, 7- and 20-year auctions not traded | C 272-275, 288-294 |
| Event set | EC-AUC records: security_type Note or Bond, floating_rate No, inflation_index_security No, announcemt_date < auction_date, tenor matched; less any auction whose announcement XML disagrees with the query on closing_time_comp (C9 check) | C 286-294, 74-92; S0.11; L-02 |
| T_a | closing_time_comp (ET) - 1 h, in CT = the release calendar's instant_utc in America/Chicago (12:00 CT for 13:00 ET closes, 10:30 for 11:30 ET, 09:00 for the one 10:00 ET close) | C 89, 295, 301-305; L-14 |
| Side | SELL, unconditional | C 296, 317 |
| Entry | market intent on the bar at T_a - 181 min (fills at the T_a - 180 open) | C 296-297 |
| Exit | market intent on the first bar at or after T_a - 2 min (fills at the next open, nominally T_a - 1) | C 298-299 |
| Hold | 179 minutes | C 300 |
| C4 exclusions | early-halt date (entry decision bar's early_halt_ct): no trade; missing entry decision bar: no trade; instrument guard on the bars read (the entry decision bar only); roll blackout by the runner | C 49-55, 305; S0.6, S0.8, S0.9 |
| Parameters (literals) | 180-minute window ending 1 minute before the close: offsets -181 (decision), -2 (exit decision); no grid | C 314-318 |
| Release instants read | EC-AUC auction_date and closing_time_comp via _releases.py (announced at least 4 days earlier, C 80-86); EC-CAL via the bar's early_halt_ct | C 307-312 |
| Trials in N | 6 | C 349 |
| Topstep | latest fill 11:59 CT; market; one trade per event; flat before the auction close; a 07:30 or 09:00 CT release inside the window held at 1 lot-equivalent | C 338-346 |

## 5. K2-aucpost-01 (post-auction recovery). C lines 351-403

| Field | Rule | Reference |
|---|---|---|
| Exposures, tenor match, event set, T_a | as K2-aucpre-01 | C 354-357, 366 |
| Side | BUY, unconditional | C 367 |
| Entry | market intent on the bar at T_a + 4 min (fills at the T_a + 5 open) | C 367-368 |
| Exit | market intent on the bar at T_a + 184 min (fills at the T_a + 185 open), or F if earlier; a missing exit bar: the first later bar | C 369-370; C4 line 54; S0.7 |
| Hold | 180 minutes | C 371 |
| Session windows | 12:05-15:05 CT (13:00 ET closes); 10:35-13:35 CT (11:30 ET closes) | C 372-373 |
| C4 exclusions | as K2-aucpre-01 | C 49-55 |
| Parameters (literals) | hold 180 minutes; entry lag 5 minutes after the competitive close (the entry's judgment, kept); offsets +4 (decision), +184 (exit decision); no grid | C 376-388 |
| Release instants read | as K2-aucpre-01; no results field | C 374 |
| Trials in N | 6 | C 403 |
| Topstep | last fill 15:05; market; may hold through a late results release at 1 lot-equivalent | C 393-401 |

## 6. K2-fomcpost-01 (post-FOMC drift). C lines 405-463

| Field | Rule | Reference |
|---|---|---|
| Exposures | ZT, ZF, ZN, TN, ZB, UB; q_c = 1 | C 408-410 |
| Event set | statement day of each regularly scheduled FOMC meeting whose statement is released at 13:00 CT that day; unscheduled meetings, notation votes and conference calls excluded | C 425-428, 93-102; L-15 |
| Side | BUY, unconditional | C 415, 429 |
| Entry | market intent on the bar at 13:29 (fills at the 13:30 open) | C 429 |
| Exit | market intent on the bar at 15:04 (fills at the 15:05 open), or F; a missing exit bar: the first later bar | C 430; S0.7 |
| Hold | 95 minutes | C 431 |
| C4 exclusions | early-halt date; missing 13:29 bar; instrument guard (entry bar only); roll blackout by the runner | C 49-55 |
| Parameters (literals) | entry 13:30 fill, exit 15:05 fill (the entry's judgment, kept); no grid | C 439-443 |
| Release instants read | FOMC statement dates via _releases.py (schedule public before each year) | C 432-437 |
| Trials in N | 6 | C 463 |
| Topstep | last fill 15:05; market; entry 30 minutes after the statement, at 1 lot-equivalent | C 453-461 |

## 7. K2-predrift-01 (pre-release drift, ISM Services). C lines 465-534

| Field | Rule | Reference |
|---|---|---|
| Exposures | ZN and ZB only | C 466-469 |
| Event set | EC-ISM Services release dates, release T = 09:00 CT (10:00 ET); a release not stamped 10:00 ET is not in the set | C 488, 103-111; L-15 |
| Signal | s = sign(close of the bar at T-11 = 08:49 minus open of the bar at T-30 = 08:30), in ticks; s = 0: no trade | C 490-491 |
| Guard | the 08:30 and 08:49 bars present and carrying one instrument_id (C4) | C 53; S0.9 |
| Entry | market intent on the bar at 08:49 in direction s (fills at the 08:50 open) | C 492 |
| Exit | market intent on the bar at 09:04 (fills at the 09:05 open, T + 5); a missing exit bar: the first later bar | C 493; S0.7 |
| Hold | 15 minutes | C 494-495 |
| C4 exclusions | early-halt date; missing entry bar; roll blackout by the runner | C 49-55 |
| Parameters (literals) | signal start T-30, signal end T-11, entry fill T-10, exit fill T+5; no grid | C 503-511 |
| Release instants read | ISM Services release dates via _releases.py; the index value is never read | C 496-501 |
| Trials in N | 2 | C 534 |
| Topstep | last fill 09:05; holds into a scheduled release by design at 1 lot-equivalent (not the full maximum) | C 521-532 |

## 8. K2-monthend-01 (month-end, intraday slices). C lines 536-592

| Field | Rule | Reference |
|---|---|---|
| Exposures | ZT, ZF, ZN, TN, ZB, UB; q_c = 1 | C 537-539 |
| Event set | N = the last EC-CAL trade date of each calendar month, N-1 = the EC-CAL trade date before it; both traded, each independently under C4; a date C4 or the roll blackout excludes is dropped, not moved | C 556-557, 578-579; L-16 |
| Side | BUY, unconditional | C 558 |
| Entry | market intent on the bar at O = 07:20 (fills at the 07:21 open) | C 558 |
| Exit | market intent on the bar at 15:04 (fills at the 15:05 open), or F; a missing exit bar: the first later bar | C 559; S0.7 |
| Hold | 464 minutes | C 560 |
| C4 exclusions | early-halt date; missing 07:20 bar; instrument guard (entry bar only) | C 49-55 |
| Parameters (literals) | days N-1 and N; entry at O; exit fill 15:05; no grid | C 566-572 |
| Calendar read | EC-CAL trade dates via _month_end.py (known in advance) | C 563-564 |
| Trials in N | 6 | C 592 |
| Topstep | last fill 15:05; holds through same-day releases at 1 lot-equivalent | C 583-590 |

---

## 9. Trial count

44 trials (6 + 6 + 6 + 6 + 6 + 6 + 2 + 6), all six exposures traded (C line 6; section 6 lines
747-757 with E = 6 and E_pd = 2: 7E + E_pd = 44). Sign checks (C lines 335-337, 391-392, 451-452,
517-518, 580-582) are reported beside the confirmation verdict and are not computed in this
screening session.

## 10. Lead readings (each is also an open choice in reports/E.3_RETURN.md section 6)

- **L-01 Event data as literal tables.** The template's static check forbids file reads and allows
  only listed imports (template lines 9-21), and the interface passes no calendar to a member. The
  event dates therefore enter as literal tables in strategy/members/k2/ (_releases.py,
  _month_end.py), generated from the frozen release calendar (sha256 839f2437...) and EC-CAL, frozen
  by the cluster freeze, and pinned by tests that recompute them from the sources. The runner's D8
  and D9.5a rules read the same release calendar, so member and harness agree on every instant.
- **L-02 The C9 XML check.** C lines 91-92 required E.2 to compare each auction's announcement XML
  with the query's closing_time_comp and drop disagreements. No earlier stage ran it (grep of the
  reports finds only the catalog text). It is run in this stage (Task 1b,
  reports/stage_e3_auction_xml_check.md); an auction with a disagreement is dropped from
  TREASURY_AUCTIONS and listed; an auction whose XML cannot be fetched is kept and listed
  [unverified], because the entry drops only on a disagreement.
- **L-03 The bar at hh:mm.** The bar of trade date d whose CT open is hh:mm on CT calendar date d
  (C1; Family H's reading, _mechanics.py lines 37-38). The one bar on another CT date is CP1's
  Globex-open bar (L-05).
- **L-04 Named entry bars are exact.** "Market intent on the bar at X" for an entry means that bar
  only; if it is missing, no entry that date. Narrowest: an entry on a later bar would be a trade the
  entry never names. The entries contrast "on the bar at" (entries) with "on the first bar at or
  after" (CP1 and CP3 exits), and C4 sends only exits on a later bar (line 54).
- **L-05 CP1's first bar.** "The trade date's first bar" is the bar opening at 17:00 CT on the
  calendar day before d, carrying trade_date d (C lines 152-153: "the Globex open, 17:00 CT on d-1").
  If it is missing, no trade (D6: "Both signal bars must exist ... else no trade"). Not adopted, the
  wider reading: the first present bar of d, as MES F3.3's statistic used
  (strategy/research/f_data_native/_stylized_facts.py lines 294-305).
- **L-06 CP1's guard is D6's.** Only the two signal bars must share one instrument_id (D6 as
  written; C4 does not apply to ports, C line 49). Roll dates are removed from the window by the
  runner.
- **L-07 CP2's hold count.** C lines 202-203 fix it by reference: present bars counted while the
  position is open, exit on the 75th (B-H1 lines 147-152). With no missing bar this is exactly 75
  minutes fill to fill. The template's C-2 exit (template lines 132-135) is not in D6's CP2 text and is
  not implemented.
- **L-08 CP2's range and trigger.** The range is taken from the present bars in [07:20, 07:35); no
  minimum bar count and no instrument guard, as D6 and B-H1 (lines 157-166) have none; with no range
  bar there is no trade. The first qualifying bar uses the day's one entry even if the engine
  refuses the intent (B-H1 sets its trigger when it emits, lines 174-181).
- **L-09 CP3 follows Family H by reference.** D6 says "complete-day and instrument-guard rules as
  Family H" (C line 237), so Family H's definitions govern: d-1 is the most recent complete daily
  bar (_mechanics.py lines 13-15), an early-halt day d is not traded (line 34), and the guard covers
  one bar (H6 GUARDED_BARS = 1). Not adopted, a narrower alternative that the reference excludes:
  requiring the immediately preceding trade date to be complete.
- **L-10 CP3's exit.** D6's "first bar at or after C-2" (13:58). Family H's extra clause "before the
  engine's no-new-positions time" is not needed: the engine flattens at F.
- **L-11 Early halt or early close.** C4 defines the test by its parenthesis "(as Family H: 'Days
  with early_halt_ct set: no trade')" (C lines 51-53): a date is excluded when its bars carry
  early_halt_ct, read from the entry decision bar (a bar of CT date d, as bars carry the halt per CT
  date). Rates days on which CME only settled early but Globex traded to its regular close
  (data/calendars/rates.py EARLY_SETTLEMENT_CT, which the module says nothing reads) are not early
  closes and are traded.
- **L-12 C4's instrument guard.** "Any bar the rule reads" is read as the bars read at or before the
  entry decision. Bars after the entry cannot make a date "no trade" once the position exists, and C4
  line 54 governs a missing exit bar. So predrift guards the 08:30 and 08:49 bars; aucpre, aucpost,
  fomcpost and monthend read only the entry decision bar.
- **L-13 "The entry bar" in C4.** The bar on which the entry intent is emitted, in C2's usage ("market
  intent on the bar at X"). The fill bar is the engine's (C2), and a market order cannot be withdrawn
  after it is sent.
- **L-14 T_a from the calendar instant.** T_a = the release calendar row's instant_utc in
  America/Chicago. This equals closing_time_comp (ET) - 1 h on every date, because ET and CT change on
  the same dates (C line 89). Offsets are in clock minutes on CT date d.
- **L-15 FOMC and ISM event sets.** FOMC: the release calendar's FOMC rows (scheduled statements only;
  the cancelled 2020-03-18 meeting and the unscheduled 2020 meetings are absent) whose instant is
  13:00 CT. ISM: ISM_SERVICES rows whose instant is 10:00 ET. All 57 FOMC and 86 ISM rows satisfy this.
  A row with any other time would be left out, not re-timed.
- **L-16 Month-end dates.** N = the last trade date of the calendar month under
  data.group_session.load_group_calendar("rates") (halt days are trade dates there, as the module
  keeps each halt day as its own short trade date). N-1 = the calendar's trade date before N. C4
  applies to each separately, and nothing moves: for example, if N is an early-halt date, N is dropped
  and N-1 is still traded. Months whose N is outside the calendar's coverage (June 2026) contribute no
  date.
- **L-17 trading_windows.** The intervals in S0.12: each member's signal bars and position minutes,
  with the union over T_a variants for the auction members. The frozen interface has no event-date
  condition, so D9's coverage is measured on these minutes on every research date.
- **L-18 Declarations and ordinals.** 44 declarations, ordinals in catalog order then exposure order
  ZT, ZF, ZN, TN, ZB, UB (S0.2). The ordinal seeds the confirmation power check (NULL_CRITERIA_E
  3). It is fixed here, before any result.
- **L-19 Tick arithmetic.** All comparisons in integer vendor ticks (S0.10), so no float rounding can
  move a threshold.
- **L-20 Undersized vehicles.** ZT and ZF are "undersized" at one contract (E.2a). The frozen runner
  trades both statuses, and C6 keeps q_c = 1, so both are coded and screened.
- **L-21 Two test files.** The stage prompt names tests/test_e3_k2_members.py. The two coders work in
  parallel, so MemberCoder-A writes tests/test_e3_k2_members.py (ports, month-end, the month-end table
  pin) and MemberCoder-B writes tests/test_e3_k2_members_events.py (event members, the release table
  pin). Both files go into the Task 4 commit.
- **L-22 A refused exit is resent.** On each later present bar while the position is open and no exit
  is pending, never by opening a new position.
- **L-23 (added 00:08 PDT after Task 1b) The C9 result and two re-keyed reopenings.** The XML check
  (reports/stage_e3_auction_xml_check.md) found all 340 in-scope auctions in agreement (2Y 84, 5Y 83,
  10Y 87, 30Y 86; the same (date, tenor) set as the release calendar), none unavailable. DROPPED_AUCTIONS
  is therefore empty. Two records are reopenings whose original term differs from the term actually
  auctioned: 2019-11-05 (CUSIP 912828TY6, security_term 3-Year, original_security_term 10-Year) and
  2026-01-26 (CUSIP 91282CGH8, security_term 2-Year, original_security_term 5-Year; research window).
  The entry keys the tenor explicitly on original_security_term ("Reopenings are included, because
  original_security_term carries the tenor", C lines 288-290), and its frozen research counts
  (2Y 13, 5Y 15, C lines 325-326) are the counts under that key, 2026-01-26 counted as a 5-year event.
  So the text is not open: both records stay, as 10Y (ZN, TN) and 5Y (ZF), and ZT does not trade
  2026-01-26. Flagged for the user: in substance these two auctions sold a 3-year and a 2-year note.
  Not adopted: re-keying by security_term (it changes the frozen event set and counts), or dropping
  both (it removes events the text includes).
