# Stage E.4 member specifications, cluster K4 energy (Part 1, Task 1)

Written by the Stage E.4 lead (Opus 5.5, xhigh), 2026-09-27 02:05-02:12 PDT (section 11 at 02:50, readings K4-L-13..K4-L-15 at 02:40-02:50), before any K4 member
code exists and before any K4 bar has been read by this session. It restates each frozen entry as
the code must implement it, with line references, and records every reading the lead took where
the entry leaves a detail open (section 10). It changes no rule. A reading is the narrowest one the
text allows unless the text fixes the detail by reference (then the reference governs and the
reading says so). Where K4's text is the same as K2's, E.3's reading is adopted and cited (E.3-L-nn,
reports/E.3_RETURN.md section 6; reports/stage_e3_member_specs.md).

Sources and their state:
- C = reports/stage_e0_catalog_K4.md, frozen by reports/stage_e1_freeze.json (manifest sha256
  96166eb3...). Line numbers below are this file's. Header C1-C13 lines 73-230. E.1 edits to K4
  (reports/stage_e1_changes.md K4-00..K4-03, F-4, F-7) touch the banner (C lines 3-7), the excluded
  K4-ml-01 and the section 0/6 ML rows; F-7 confirms K4-ovr-01 and K5-ovr-01 carry one rule text.
  No active member's rule changed. K4-ngrev-01 is excluded (E.0 review R-06); K4-ml-01 is excluded
  (U6). Neither is coded.
- D = docs/STAGE_E_DESIGN.md (frozen): D6 port texts lines 364-366, the "4 ticks of P" paragraph
  lines 368-374, the energy session row line 395 (O 08:00, C 13:30, F 15:08); D9.5a lines 516-522;
  D9.7 lines 531-550.
- Vehicles (reports/stage_e2a_vehicles.md lines 31-34; frozen reports/stage_e2a_vehicles.json via
  screening.stage_e_frozen): WTI crude -> MCL, status chosen, q_c = 4 (0.4 lot-equivalent);
  Henry Hub gas -> NG, status chosen, q_c = 1; RBOB and ULSD: no candidate, not traded. Operative
  eps (reports/stage_e2a_epsilon.md lines 17-18): MCL 21 ticks, NG 8 ticks (net ticks per contract
  per day).
- Frozen per-root values (checked 2026-09-27 02:20 through load_frozen_tables() and
  rules.products.product): day_session_ct MCL = NG = (08:00, 13:30); vendor_tick MCL 0.01, NG 0.001.
  F (rules/sessions.py, enforced by the engine) = 15:08 CT on a regular day, earlier on early-halt
  days.
- Release calendar reports/stage_e2b_release_calendar.json (frozen harness input, sha256
  839f2437...): WPSR rows (EC-WPSR; 371 rows 2019-05-01..2026-06-17; 64 in the research window, all
  "verified"), NGS rows (EC-NGS; 373 rows 2019-05-02..2026-06-18; 64 in the window, 59 "[unverified]"
  from EIA's standing rule, 5 verified), API_WSB rows (EC-API; 372 rows, all 16:30 ET, "announced
  schedule"). No WPSR, NGS or API cancellation is listed.
- The research-window release check: reports/stage_e4_release_check.md and .json (Task 1b,
  ReleaseChecker-OpusMed). Section 11 applies its verdicts.
- Source-window labels (reports/stage_e2a_source_window_amendment.md lines 36, 58-61): K4-ngpre-01
  is NOT source-overlap; K4-cp1-01, K4-cp2-01, K4-cp3-01 keep it; K4-apipre-01, K4-eiafade-01,
  K4-eiamom-01 and K4-ovr-01 carry it by R-04 (C lines 516, 590, 662, 725). Labels matter only for
  the confirmation session.
- EC-CAL = the D10 energy calendar, data/calendars/energy.py, read through
  data.group_session.load_group_calendar("energy") (is_trade_date, trade_dates_between,
  early_halt_ct). Research window: 315 trade dates; early halts 2025-05-26, 06-19, 07-04, 09-01,
  11-27, 11-28, 12-24, 2026-01-19, 02-16, 05-25, 06-19; weekday non-trade dates 2025-04-18,
  12-25, 2026-01-01, 04-03 (checked 02:22). Bars carry `early_halt_ct` per CT calendar date.

What the member does NOT implement (the engine and runner do, and a member must not duplicate or
second-guess them; same list as E.3): the window's trade dates and the removal of roll-blackout
dates (the engine refuses opens there by name, `engine_roll_blackout`; bars of those dates are still
delivered); 2026-06-18/19 (UR-1); F and the forced flatten (D9.1); costs and the event-window cost
(D8); the event-minute fill guard (D9.5a: a fill that would land in [release, release + 2 min) is
moved to the first bar at or after release + 2 min; this touches CP1's 13:00 fill on FOMC days, C
item 3 of section 7, and ngpre's 09:30 entry fill on Wednesday 12:00 ET storage days, which falls on
the 09:30 CT WPSR instant that the frozen calendar lists for NG (moved to 09:32; MemberCoder-B's finding); the entry cap and the 2-minute minimum hold (D9.3a/b); the skip of an entry
whose fill would come less than 2 full minutes before F; price-limit proximity and its forced exit
(D9.7); the lot-equivalent cap (D9.5).

---

## 0. Common to all eight members

S0.1 Legs. Each member reads and trades exactly one leg: the traded exposure's own vehicle,
`LegSpec(root, True)`, root MCL (crude) or NG (gas). No signal legs. RB and HO are never read or
traded. (C lines 238-240, 287, 345, 386, 518, 592, 664, 727-730; vehicles lines 31-34.)

S0.2 Declarations. One `MemberDecl` per (member, exposure) trial, 12 in all. Label
`"<member id> <ROOT>"`, for example `"K4-cp1-01 MCL"`; the member object's `name` equals its
label. Module per member under strategy/members/k4/; one zero-argument factory per exposure,
`make_mcl`, `make_ng` (only the exposures the member trades). Ordinals: catalog order, then crude
before gas (the prompt's rule):

| Member | Module | MCL (crude) | NG (gas) |
|---|---|---|---|
| K4-cp1-01 | strategy.members.k4.cp1 | 1 | 2 |
| K4-cp2-01 | strategy.members.k4.cp2 | 3 | 4 |
| K4-cp3-01 | strategy.members.k4.cp3 | 5 | 6 |
| K4-ngpre-01 | strategy.members.k4.ngpre | - | 7 |
| K4-apipre-01 | strategy.members.k4.apipre | 8 | - |
| K4-eiafade-01 | strategy.members.k4.eiafade | 9 | - |
| K4-eiamom-01 | strategy.members.k4.eiamom | 10 | - |
| K4-ovr-01 | strategy.members.k4.ovr | 11 | 12 |

S0.3 Size. Every entry is `q_c` contracts of the vehicle, read from
`load_frozen_tables().vehicles[root].q_c` (MCL 4, NG 1), never a literal (C6 lines 98-104; template
lines 42-43). Every exit closes the whole position. No member sizes by signal (C line 104).

S0.4 Clock. America/Chicago. "The bar at hh:mm" of trade date d is the bar with `trade_date == d`
whose open (`ts_event_ns`) is hh:mm:00 CT on CT calendar date d (C1 lines 75-78; E.3-L-03); the
exceptions are CP1's Globex-open bar (17:00 CT on the calendar day before d, C3 lines 82-84;
E.3-L-05) and apipre's Tuesday signal bars (CT date W-1, section 5). O and C come from
`load_frozen_tables().day_session_ct[root]` = (08:00, 13:30) (D line 395). Every other clock time
below is a literal of the entry, written as a named constant or as an offset from O, C or the
release instant T as the entry states it. A bar is usable at its close (C1 line 77); `on_minute` is
called at the bar's close with the bar in `view.bars[root]`.

S0.5 Orders. Market intents only (`leg_market_intent`), filled by the engine at the open of a later
bar of the leg (C2 lines 79-81). No limit orders, stops or brackets.

S0.6 Named entry bar. "Market intent on the bar at X" (an entry) is emitted only when the view's bar
is the bar at X. If that bar is missing, there is no entry at X (E.3-L-04). An entry is emitted at
most once per trade date per member instance (per decision time for K4-ovr-01), and never while a
position or a pending order exists on the leg.

S0.7 Exits. Every exit is sent on the first present bar at or after the named exit bar, while the
position is non-zero and no exit order is pending (C4 lines 93-94: "If an exit's named bar is
missing, the exit is sent on the first later bar"). A refused exit is sent again on the next present
bar under the same condition (E.3-L-22). The engine's forced flatten at F is the backstop (C4 line
94). If the engine closes the position itself (D9.7, the flatten, an MLL liquidation), the member
sees a flat account, sends no exit and makes no further entry that trade date (for ovr: at that
decision time; later decision times proceed as usual).

S0.8 Early halts (C4 lines 88-89, the new members; CP3 through Family H). A trade date is an
early-halt date when the entry decision bar (a bar of CT date d) carries `early_halt_ct` not None
(E.3-L-11). No entry on such a date. CP1 and CP2 follow D6 and do not test it (C line 85: "The
ports follow D6 as written").

S0.9 Instrument guard (C4 lines 90-91, the new members). Every bar the rule reads at or before the
entry decision carries the entry decision bar's `instrument_id`, else no trade that date (E.3-L-12,
E.3-L-13). Exit bars are not guarded. For K4-ovr-01 the guard is per decision time (section 8).

S0.10 Prices. Every price comparison and sign is computed in integer vendor ticks,
`round(price / vendor_tick)` with `rules.products.product(root).vendor_tick`, never a literal tick
(E.3-L-19). Percent returns (eiafade, ovr) are ratios of integer ticks (section 10, K4-L-05).

S0.11 Event and calendar data. A member cannot read a file (template lines 9-21). The dates it needs
are literal tables in the cluster package, generated from the frozen sources and pinned by tests
that recompute them from those sources (E.3-L-01). Coder B writes strategy/members/k4/_releases.py
(WPSR, NGS, FEDERAL_MONDAY_HOLIDAYS, NYSE_NOT_FULL); Coder A writes strategy/members/k4/_calendar.py
(ENERGY_FULL_SESSIONS), which apipre imports:
- WPSR: (date, T_W as CT time, weekday, standard flag) for every calendar WPSR row 2019-05-01..
  2026-06-17, less the research-window rows that section 11 drops; `standard` = a Wednesday at
  10:30 ET. T_W = the row's instant_utc in America/Chicago (K4-L-02).
- NGS: (date, T_N as CT time) for every calendar NGS row, less section 11's drops.
- ENERGY_FULL_SESSIONS: every EC-CAL energy trade date 2019-05-01..2026-06-19 (the calendar's coverage, K4-L-13) with no early halt
  (from data.group_session; used for apipre's Tuesday and ovr's reference dates).
- FEDERAL_MONDAY_HOLIDAYS: US federal holidays on a Monday, 2019-05-01..2026-06-19 (Task 1b's
  list; used by apipre).
- NYSE_NOT_FULL: NYSE full closures and early closes, 2019-05-01..2026-06-19 (Task 1b's list; used
  by eiamom).
- The sha256 of each source file the tables were generated from, and a comment naming the
  research-window drops.

S0.12 trading_windows (D9 coverage check; interface lines 51-61). Per member, the CT intervals below
on its one leg, all on day d (offset 0) except CP1's Globex-open minute (E.3-L-17). The check
intersects each interval with trade date d's own session (screening/stage_e_align.py lines 100-113),
so an interval on day -1 before 17:00 CT would count nothing: apipre's Tuesday minutes are declared
at offset 0 and measured on every research date (K4-L-07).

| Member | Intervals [start, end) CT |
|---|---|
| CP1 | (17:00, 17:01) on day -1; (08:29, 08:30); (12:59, 13:30) |
| CP2 | (08:00, 15:08) |
| CP3 | (08:00, 13:30) |
| ngpre | (07:59, 10:01) and (09:29, 11:31) (the standard and 11:00 CT slots) |
| apipre | (15:24, 15:25); (15:39, 15:40); (07:29, 09:30) |
| eiafade | (09:29, 13:30) |
| eiamom | (09:29, 10:00); (14:29, 15:00) |
| ovr | (08:00, 14:00) |

S0.13 Topstep checks common to all (C lines 272-280 and each entry's list): flat by F (engine);
market orders only; entries per trade date at most 1 (ovr at most 5), far below D9.3a's 20; every
hold is at least 29 minutes by rule (D9.3b's 2 minutes never binds); no stops, brackets or passive
fills (D9.4); MCL is starred (Topstep F1) with its restriction unresolved (D9.8, C line 69): every
crude trial carries the flag (section 7 item 1 is moot: D2 chose MCL); size MCL 4 = 0.4
lot-equivalent, NG 1 = 1 lot-equivalent, at most half the XFA's 2-lot maximum, so holding through a
release is allowed (D9.5, F6.3); position limit <= 1 lot-equivalent; price limit per D9.7 in the
engine (C13 lines 216-230; E.0 R-10: the D9.7 exit is exempt from the fill guard).

S0.14 C10 (lines 192-198). Every percent return (P1 - P0) / P0 requires P0 > 0, else the rule does
not trade. It binds on K4-eiafade-01 (M) and K4-ovr-01 (r). Tick differences, signs and the ports
are unaffected (C line 198): CP1-CP3, ngpre, apipre and eiamom need no guard.

---

## 1. K4-cp1-01 (core port CP1, intraday momentum). C lines 234-282; D line 364

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicle | crude MCL (q_c 4), gas NG (q_c 1); RBOB, ULSD not traded | C 238-240; S0.1 |
| Signal | s = sign(close of the bar at O+29 = 08:29 minus open of the trade date's first bar), in ticks | C 253-254; D 364 |
| Trade date's first bar | the bar opening 17:00 CT on the calendar day before d, with trade_date d (the Globex open) | C 253-254 (C3 lines 82-84); E.3-L-05 |
| Signal-bar guard | both signal bars (17:00 on d-1, 08:29 on d) present with one instrument_id, else no trade | D 364; E.3-L-06 |
| Zero signal | s = 0: no trade | D 364 |
| Entry | market intent on the bar at C-31 = 12:59; buy if s > 0, sell if s < 0; fills at the 13:00 open | C 255; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 13:28; fills nominally at the 13:29 open | C 256; S0.7 |
| Hold | 29 minutes nominal | C 257 |
| Early halts | not tested by the member (port; on an early-halt day F precedes 13:00 or the engine refuses) | C 85 |
| Parameters (literals) | O+29 = 08:29, C-31 = 12:59, C-2 = 13:28; no grid | C 262 |
| Release instants read | none. On FOMC days the 13:00 fill meets the statement minute: the engine's D9.5a guard moves it (section 7 item 3 stays as D6 is written) | C 274-276; D 516-522 |
| C10 | not applicable (tick difference) | C 198 |
| Trials in N | 2 | C 281; S0.2 |
| Topstep | last fill 13:29; market; one trade a day; MCL flag on crude | C 270-280 |

## 2. K4-cp2-01 (core port CP2, opening-range breakout). C lines 283-342; D line 365

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicle | crude MCL, gas NG | C 287-288 |
| Opening range | OR_high = max high, OR_low = min low of the present bars opening in [O, O+15) = [08:00, 08:15) of CT date d; no OR bar: no trade | C 302; E.3-L-08 |
| Buffer | 4 x vendor_tick of the vehicle: MCL 0.04, NG 0.004. These equal R-07's buffer, 4 ticks of the exposure's most active contract (CL 0.04, NG 0.004), so D's "fixed whatever vehicle D2 chooses" holds; a test pins both literals | C 285 (R-07); D 368-374; K4-L-06 |
| Eligible bars | bars opening in [O+15, C) = [08:15, 13:30) of CT date d; no entry from 13:30 on | C 303 |
| Entry | the first eligible bar whose close >= OR_high + buffer: buy; <= OR_low - buffer: sell; market intent on that bar; one entry per trade date (the first qualifying bar ends the day's search) | C 317-318; E.3-L-08 |
| Exit | 75 minutes after the fill, counted as the MES module counts it: count present bars while the position is non-zero, starting after the entry decision bar; on the 75th, a market intent closing the position; or the engine's flatten at F if earlier. No C-2 exit | C 319-321; E.3-L-07 |
| Hold | 75 minutes nominal; the latest entry fill 13:30 exits about 14:45 | C 322-323 |
| Instrument guard | none (D6 and B-H1 have none) | E.3-L-08 |
| Early halts | not tested by the member | C 85 |
| Parameters (literals) | OR 15 minutes, buffer 4 ticks, hold 75 minutes; no grid | C 327-328 |
| Release instants read | none | C 324-325 |
| C10 | not applicable | C 198 |
| Trials in N | 2 | C 341 |
| Topstep | flatten by the engine at F; market; one trade a day; may hold through a 09:30 release or the 13:00 FOMC statement at <= 1 lot-equivalent | C 331-340 |

## 3. K4-cp3-01 (core port CP3, prior-close location). C lines 343-382; D line 366

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicle | crude MCL, gas NG | C 345-346 |
| Daily bar of trade date d | from the bars of trade date d on CT date d opening in [O, C) = [08:00, 13:30): O_d = open of the 08:00 bar, H_d / L_d = max high / min low over the present bars, C_d = close of the 13:29 bar | C 356-357 |
| Complete day (Family H) | the 08:00 and 13:29 bars exist, the date is not an early halt, and all bars in [08:00, 13:30) carry one instrument_id; finalised when a bar of a later trade date arrives | C 358-359; E.3 spec section 3 |
| "d-1" (Family H) | the most recent COMPLETE daily bar of a trade date before d; incomplete days are dropped | C 358-360; E.3-L-09 |
| Warm-up | no complete earlier bar yet: no trade | E.3 spec section 3 |
| Instrument guard | d-1's instrument_id equals the instrument_id of day d's 08:00 bar, else no trade | C 360 |
| Condition | Range = H - L of d-1 in ticks, > 0; CLV = (C - L) / (H - L) in ticks; CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict) | C 361-362 |
| Day d exclusion | a trade date d whose 08:00 bar carries early_halt_ct: no trade | E.3-L-09, E.3-L-11 |
| Entry | market intent on the 08:00 bar of d (fills at the 08:01 open); the 08:00 bar must exist | C 363; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 13:28 (fills nominally at 13:29) | C 364; E.3-L-10 |
| Hold | about 328 minutes | C 365 |
| Parameters (literals) | CLV cuts 0.2 and 0.8, lookback 1; no grid | C 369 |
| Release instants read | none | C 366-367 |
| C10 | not applicable (CLV is a ratio of tick ranges; Range > 0 is its own guard) | C 198 |
| Trials in N | 2 | C 382 |
| Topstep | last fill 13:29; holds through the WPSR, the storage report and FOMC at <= 1 lot-equivalent | C 372-381 |

## 4. K4-ngpre-01 (storage-report day short). C lines 384-439

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | gas NG, q_c 1 | C 386-387 |
| Event set | every EC-NGS release in the NGS table (S0.11), that is, every calendar NGS row less section 11's drops; the date is a trade date with no early halt (C4) | C 402-404; C9 lines 150-175; K4-L-03 |
| T | the release instant in CT: 09:30 for 10:30 ET (Thursday standard or Friday exception), 11:00 for 12:00 ET (Wednesday or Monday exception); generally the row's instant_utc in America/Chicago | C 402-404; C1 line 78; K4-L-02 |
| Entry | SELL, market intent on the bar at T-91 (standard 07:59), filling at the open of T-90 (08:00) | C 405-406; S0.6 |
| Exit | market intent on the bar at T+29 (standard 09:59), filling at the open of T+30 (10:00); if that bar is missing, the first later present bar | C 407; S0.7 |
| Hold | 120 minutes; latest fill 11:30 | C 408-409 |
| Instrument guard | the only bar read before the entry is the entry bar: satisfied by construction | S0.9 |
| Early halts | entry bar's early_halt_ct not None: no trade | S0.8 |
| Parameters (literals) | entry T-90, exit T+30, side SELL; no grid | C 415-416 |
| C10 | not applicable (no return computed) | C 198 |
| Trials in N | 1 | C 438 |
| Topstep | holds into the storage release at 1 lot-equivalent (F6.3, D9.5); no fill in the release minute | C 428-436 |
| Limitation (section 7 item 5) | D8's cost sample holds no Thursday: NG's 09:30 bucket is calibrated on non-release minutes and may understate the release-window cost. Reported, no new sample (frozen D8 table) | C 211-215 |

## 5. K4-apipre-01 (API-to-EIA continuation). C lines 514-587

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | crude MCL, q_c 4 | C 518-519 |
| Event set | standard weeks: a WPSR row on a Wednesday W at 10:30 ET (not an exception) in the WPSR table; the Tuesday W-1 is in ENERGY_FULL_SESSIONS; the Monday W-2 is not in FEDERAL_MONDAY_HOLIDAYS (C9's E.2 check); W itself has no early halt (C4) | C 538-539; C9 lines 176-188; K4-L-04 |
| Signal | R_API = ticks(close of the 15:39 bar of CT date W-1) - ticks(close of the 15:24 bar of CT date W-1); both bars present with one instrument_id; R_API = 0: no trade | C 540-543 |
| Instrument guard | the 15:24 and 15:39 bars of W-1 and the 07:29 bar of W carry one instrument_id | S0.9; E.3-L-12 |
| Entry | market intent on the bar at 07:29 of W, side sign(R_API), filling at the 07:30 open | C 544-545; S0.6 |
| Exit | market intent on the bar at 09:28 of W, filling at the 09:29 open; if missing, the first later present bar | C 546-547; S0.7 |
| Hold | 119 minutes | C 548 |
| Parameters (literals) | signal bars 15:24 and 15:39 (Tuesday), entry 07:29, exit 09:28; no grid | C 561-566 |
| Release instants read | the WPSR table (standard flag, date); the API bulletin itself is never read | C 555-559 |
| C10 | not applicable (tick difference) | C 198 |
| Trials in N | 1 | C 586 |
| Topstep | flat before the 09:30 WPSR; MCL flag | C 575-584 |

## 6. K4-eiafade-01 (post-WPSR overreaction fade). C lines 588-659

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | crude MCL, q_c 4 | C 592-593 |
| Event set | every WPSR row in the WPSR table with T_W + 15 <= 13:13 CT (09:30, 10:00, 11:00 and 12:00 CT slots; the 16:00 CT row 2025-12-29 is excluded); the date has no early halt (C4) | C 608-610; K4-L-03 |
| Signal | M = (close(T_W+14) - close(T_W-1)) / close(T_W-1), in integer ticks t14 and t0; t0 > 0 (C10); both bars present with one instrument_id | C 611-612; K4-L-05 |
| Entry | BUY if M <= -0.005, i.e. 200 x (t14 - t0) <= -t0; SELL if M >= +0.005, i.e. 200 x (t14 - t0) >= t0; else no trade; market intent on the bar at T_W+14, filling at T_W+15 | C 613-617; K4-L-05 |
| Instrument guard | the T_W-1 and T_W+14 bars (the entry decision bar is T_W+14) carry one instrument_id | S0.9 |
| Exit | market intent on the first bar at or after 13:28, filling nominally at 13:29 | C 618-620; S0.7 |
| Hold | 224 minutes (09:30 slot), 194 (10:00), 134 (11:00), 74 (12:00) | C 621-622 |
| Parameters (literals) | window 15 minutes, threshold 0.005, exit 13:28; no grid | C 627-635 |
| C10 | t0 > 0 required | C 611-612 |
| Trials in N | 1 | C 658 |
| Topstep | enters 15 minutes after the release; MCL flag | C 648-656 |

## 7. K4-eiamom-01 (WPSR-day release half-hour predicts the last NYSE half-hour). C lines 660-722

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | crude MCL, q_c 4 | C 664-665 |
| Event set | a WPSR row on a Wednesday at 10:30 ET (T_W = 09:30 CT, standard) in the WPSR table; the date has no early halt (EC-CAL, S0.8) and is not in NYSE_NOT_FULL (EC-NYSE) | C 686-687 |
| Signal | r3 = ticks(close of the 09:59 bar) - ticks(close of the 09:29 bar); both present with one instrument_id; r3 = 0: no trade | C 688-690 |
| Instrument guard | the 09:29, 09:59 and 14:29 bars carry one instrument_id | S0.9 |
| Entry | market intent on the bar at 14:29, side sign(r3), filling at the 14:30 open | C 691-692; S0.6 |
| Exit | market intent on the first bar at or after 14:58, filling nominally at 14:59 | C 693-694; S0.7 |
| Hold | 29 minutes; flat 9 minutes before F | C 695 |
| Parameters (literals) | signal bars 09:29 and 09:59, entry 14:29, exit 14:58; no grid | C 699-701 |
| C10 | not applicable (tick difference) | C 198 |
| Trials in N | 1 | C 721 |
| Topstep | last fill 14:59; MCL flag | C 710-718 |

## 8. K4-ovr-01 (hourly overreaction reversal). C lines 723-793

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicle | crude MCL (q_c 4), gas NG (q_c 1); ULSD not traded (no vehicle); RBOB not in the source | C 727-730 |
| Decision times | t in {09:00, 10:00, 11:00, 12:00, 13:00} CT | C 745-746 |
| Signal | r(t) = (close of the bar at t-1 - open of the bar at t-60) / open of the bar at t-60, from integer ticks (tc - to) / to as a Python float; to > 0 (C10); both bars present with one instrument_id | C 747-748; K4-L-05 |
| Reference dates | the 20 most recent ENERGY_FULL_SESSIONS dates strictly before d (EC-CAL; roll-blackout dates count, since the text names EC-CAL only) | C 750-751; K4-L-08 |
| Reference values | r(tau) at the same five clock times on those dates, each counted only when its two bars exist with one instrument_id and its open is > 0; at least 80 values, else no trade at t | C 751-752; K4-L-08 |
| Warm-up | no trade while any of the 20 reference dates precedes the trade date of the first bar the member received in this run (the first 20 eligible dates of the window) | C 754-755; K4-L-09 |
| Cuts | P10, P90 = numpy.percentile(values, [10, 90], method="linear") | C 753 |
| Entry | r(t) <= P10: BUY; r(t) >= P90: SELL; both (P10 = P90 = r): no trade; otherwise no trade. Market intent on the bar at t-1 (the entry decision bar), filling at t; only when flat with no pending order | C 756-760; K4-L-10 |
| Exit | market intent on the bar at t+58, filling at t+59; if missing, the first later present bar | C 761-762; S0.7 |
| Early halts | a trade date d whose bars carry early_halt_ct: no trade at any t | S0.8 |
| Hold | 59 minutes; at most 5 entries a day; positions never overlap | C 761-763 |
| Parameters (literals) | the five t, 60-minute signal, deciles 10 and 90, 20 reference dates, 80 values, 59-minute hold; no grid | C 767-775 |
| C10 | open of t-60 > 0 for r(t) and for every reference value | C 747-748 |
| Trials in N | 2 | C 792 |
| Topstep | at most 5 entries a day, each held 59 minutes; MCL flag on crude | C 781-790 |
| F-7 | the same rule text as K5-ovr-01, differing only in the decision clock (reports/stage_e1_changes.md line 32) | E.1 F-7 |

## 9. Trial count

12 declarations (S0.2): 7 on crude (cp1, cp2, cp3, apipre, eiafade, eiamom, ovr) and 5 on gas (cp1,
cp2, cp3, ngpre, ovr). This matches the E.1 JSON exposure table (reports/stage_e1_changes.md lines
1861-1862: crude 7, gas 5) with RBOB and ULSD untraded. Program N after K4: 102 + 12 = 114 if all 12
are screened (the lead takes the count from the freeze declarations).

## 10. Lead readings (each is also an open choice in reports/E.4_RETURN.md section 6)

Adopted from E.3 (the K4 text is the same): E.3-L-01 (literal tables), E.3-L-03 (the bar at hh:mm
is on CT date d), E.3-L-04 (named entry bar exact), E.3-L-05 (CP1's first bar is the 17:00 bar of
d-1), E.3-L-06 (CP1's guard is D6's), E.3-L-07 (CP2 counts present bars, no C-2 exit), E.3-L-08
(CP2's range from present bars, first qualifying bar uses the day's entry), E.3-L-09 (CP3 by Family
H), E.3-L-10 (CP3 exits first bar at or after C-2), E.3-L-11 (early halt = the bar's early_halt_ct),
E.3-L-12 (C4's guard covers the bars read at or before the entry decision), E.3-L-13 (C4's entry bar
is the bar the intent is emitted on), E.3-L-17 (fixed trading_windows measured on every date),
E.3-L-19 (integer vendor ticks), E.3-L-22 (a refused exit is resent).

New readings for K4:
- **K4-L-01 Tables span 2019-05..2026-06.** The WPSR and NGS tables carry every calendar row, so the
  frozen code serves the confirmation window. C9's drop rules are applied only to the research window,
  the scope of Task 1b; earlier rows are kept as the calendar gives them and are unchecked. An event
  member that reaches Tier A must have its confirmation-window dates checked before its confirmation
  run (the prompt's Task 1b failure path). Reason: a member can read no file, and re-coding at
  confirmation would break the freeze.
- **K4-L-02 T is the calendar instant in CT.** T = instant_utc converted to America/Chicago, which is
  the ET clock time minus one hour (C1 line 78). The entries' enumerations (ngpre C 402-404, eiafade
  C 608-610) agree with it on every row.
- **K4-L-03 The event sets of ngpre and eiafade are the table rows** (every release that passes C9,
  section 11), on dates with no early halt. eiafade's T_W + 15 <= 13:13 CT filter is applied in the
  member. A release on a date with no bars simply does not trade.
- **K4-L-04 apipre's standard week uses the rule, not the API rows.** EC-API is "the rule only" (C line
  176): the Tuesday 15:30 CT bulletin time is fixed; the calendar's API_WSB rows are not read. The
  Monday-holiday drop is applied whatever the WPSR table says (C9 line 186). If Task 1b shows an API
  row off its Tuesday in a standard week, section 11 drops that week (the narrowest reading: the
  rule's premise fails that week).
- **K4-L-05 Percent returns from integer ticks.** eiafade compares exactly: M <= -0.005 iff
  200 x (t14 - t0) <= -t0 with t0 > 0, and M >= 0.005 iff 200 x (t14 - t0) >= t0. ovr computes r as
  a float (tc - to) / to from integer ticks and uses numpy's linear percentile on those floats, as the
  entry names numpy. The tick scale cancels in the ratio, so these equal the price-unit returns up to
  float rounding.
- **K4-L-06 CP2's buffer is coded as 4 x vendor_tick** (MCL 0.04, NG 0.004), which equals R-07's
  most-active-contract buffer for both exposures (CL and MCL share the 0.01 tick; NG is the gas
  vehicle); section 7 item 2 is moot. A test pins both literals.
- **K4-L-07 apipre's coverage minutes are declared on day d.** The coverage check intersects every
  interval with trade date d's session (17:00 of d-1 to 16:00 of d), so the Tuesday 15:24 and 15:39
  minutes, declared at offset -1, would count nothing; declared at offset 0 they are measured on every
  research date, which is how E.3 measured its event members' minutes (E.3-L-17).
- **K4-L-08 ovr's reference dates come from EC-CAL, missing bars reduce the count.** The 20 dates are
  the 20 most recent energy full-session trade dates before d (a literal table from EC-CAL), whether or
  not the runner excludes them (roll blackouts), and whether or not their bars exist; a value whose bars
  are missing, carry two instrument_ids or have open <= 0 is left out, and fewer than 80 values means no
  trade at t. Reason: the text defines the dates by EC-CAL and counts values separately.
- **K4-L-09 ovr's warm-up is the first 20 eligible dates of the window.** The member trades at t only
  when all 20 reference dates are on or after the trade date of the first bar it received in the run.
  Without this, a date late in the warm-up could reach 80 values from in-window dates alone, which the
  text's warm-up forbids.
- **K4-L-10 ovr's tie.** When P10 = P90 and r(t) equals them, both cuts hold and the direction is
  undefined: no trade (the narrowest reading).
- **K4-L-11 12 declarations**, ordinals in catalog order, then crude (MCL) before gas (NG).
- **K4-L-12 Two coders, two or more test files** (tests/test_e4_k4_members*.py), as E.3-L-21.
- **K4-L-13 ENERGY_FULL_SESSIONS spans EC-CAL's coverage only** (2019-05-01..2026-06-19; ruling 02:40
  on MemberCoder-A's question 1). Outside its coverage the calendar says nothing, so listing a date
  there as a full session (for example 2019-04-19, Good Friday) would widen the rule. A date with fewer
  than 20 table dates before it cannot trade (ovr warm-up); an apipre Tuesday outside the table is not a
  full session (no trade).
- **K4-L-14 ovr's instrument check is per computation** (ruling 02:40 on MemberCoder-A's question 2).
  Each reference value counts when its own two bars carry one instrument_id; it need not match day d's
  contract. Day d's guard covers the t-60 and t-1 bars (t-1 is the entry decision bar). Reason: the
  entry's own text fixes it ("Every value whose two bars exist with one instrument_id counts", C line
  751), which C1-C13 yield to ("unless the entry says otherwise", C line 73), and C4's clause is about
  "the signal bars of one computation" (C line 91). The stricter reading would contradict that text.

## 11. The research-window release check and the drops (lead ruling 02:50 PDT, after Task 1b)

Source: reports/stage_e4_release_check.json and .md (ReleaseChecker-OpusMed, 02:01-02:48 with the
restart pause). The JSON's per-row verdicts govern; the member tables are generated from them.

- **WPSR, 64 research-window rows:** 62 keep, 2 drop_actual_differs (after the lead's ruling R-T3-1 at
  04:35 on audit finding B-1, which restored 2025-07-16; the checker had dropped it on a mis-attributed
  capture). EIA's issue pages confirm every release date; EIA states no clock time, so every WPSR time is
  the schedule's (time_basis "schedule"). DROPPED_WPSR:
  - 2025-12-29 (Monday; calendar 17:00 ET): the schedule row in the last capture before the release
    (20251228152631 UTC) read "Monday 10:30 a.m."; EIA's page carried "We are delaying today's release";
    the release came after 15:53 ET.
  - 2026-05-28 (Thursday 12:00 ET, exception): a capture 37 minutes after the scheduled time
    (20260528163711 UTC, served as requested) still shows the previous release; the next capture
    (20260528181428 UTC) shows the new one.
  Restored (R-T3-1): 2025-07-16 (Wednesday 10:30 ET, standard). The capture the checker cited as
  "95 minutes after the slot" was served from the 2025-07-15 snapshot (manifest effective_url); the real
  07-16 12:04 ET capture already shows the release.
- **NGS, 64 rows:** 60 keep (61 of the 64 times are stated on Wayback copies of EIA's weekly NGS page), 1
  updated, 3 unverifiable. DROPPED_NGS: 2025-12-29 (Monday 12:00 ET, "(Updated)"): the row first appears in
  the capture of 20260126101407 UTC; the latest capture before it (20251203063824 UTC) has no row for the
  date, so no capture before the member's entry shows the update (C9's second drop rule, C line 169-170).
  Kept with the calendar's value and labelled unverifiable: 2025-05-01, 2025-05-29, 2025-06-18
  (NGS_UNVERIFIED_IN_WINDOW).
- **API (EC-API):** 56 standard weeks in the window; no Monday before any of them is a federal holiday;
  every standard week's API_WSB row is on its Tuesday at 16:30 ET. API_DROPPED_WEEKS is empty. apipre's
  research-window event set is the 56 standard weeks before its own exclusions (early halts, full-session
  Tuesday, missing bars, R_API = 0, roll blackouts).
- **NYSE (EC-NYSE):** 69 full closures and 15 early closes (13:00 ET), 2019-05-01..2026-06-19; in the
  research window 13 closures and 3 early closes (2025-07-03, 2025-11-28, 2025-12-24). NYSE_NOT_FULL holds
  all 84 dates. The 2020-21 and 2023-24 rows rest on captures made in advance; 2025-01-09 (national day of
  mourning) is from ICE's press release.
- **FEDERAL_MONDAY_HOLIDAYS:** 47 rows, 46 distinct dates (2025-01-20 is both Birthday of Martin Luther King, Jr.
  and Inauguration Day), 2019-05-01..2026-06-19, from OPM.

Labels carried into the return: K4-ngpre-01 NG "calendar partly unverified" (3 unverifiable storage
releases kept). If it reaches Tier A, its confirmation session verifies those dates and the
confirmation-window rows before it runs (K4-L-01).

- **K4-L-15 The WPSR drop that rests on a capture showing the previous week (2026-05-28) is applied as
  the checker recorded it.** C9 drops a release whose actual time differs from its schedule entry; the
  captures are the only record of the publication time, and a capture 37 minutes after the slot, served
  as requested, showing the previous week is evidence that it did not appear on time. Dropping is also
  the narrower event set. Flagged for the user: EIA posted no delay notice that was captured for that
  date (the "delaying" text on the May pages is an HTML comment left from December), and a cached page
  cannot be ruled out. The effect is one Thursday release fewer for eiafade. The checker's second such
  drop (2025-07-16) was reversed by ruling R-T3-1 (audit B-1): its evidence was a mis-attributed capture.
