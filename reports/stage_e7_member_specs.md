# Stage E.7 member specifications, cluster K1 equity index (Task 1)

Written by the Stage E.7 lead (Opus 5.5, xhigh), 2026-09-28 00:50-01:00 PDT, before any K1 member code
exists and before any K1 bar has been read by this session. It restates each frozen entry as the
code must implement it, with line references, and records every reading the lead took where the
entry leaves a detail open (section 8). It changes no rule. A reading is the narrowest one the text
allows unless the text fixes the detail by reference (then the reference governs). Where K1's text
is the same as an earlier cluster's, the earlier reading is adopted and cited (E.3-L-nn:
reports/stage_e3_member_specs.md section 10; K4-L-nn: reports/stage_e4_member_specs.md section 10;
K3-L-nn: reports/stage_e4c_member_specs.md section 10; K7-L-nn: reports/stage_e6_member_specs.md
section 8).

Sources and their state:
- C = reports/stage_e0_catalog_K1.md, frozen by reports/stage_e1_freeze.json (manifest 96166eb3...).
  Line numbers below are this file's. Banner lines 3-7 (E.1: U6, U3; 5 active members, 11 trials);
  header table lines 80-89; conventions C1-C12 lines 91-214; members lines 218-594; section 6 lines
  915-931; section 7 lines 933-984. E.1 edits to K1 (reports/stage_e1_changes.md K1-00..K1-03) touch
  only the banner, the excluded K1-ml-01 and the ML rows of sections 0 and 6. No active member's rule
  changed. K1-predrift-01 is excluded by the E.0 lead (C line 597, 0 trials); K1-ml-01 is excluded
  (U6). Neither is coded.
- D = docs/STAGE_E_DESIGN.md (frozen): D5 screen lines 300-306; D6 port texts lines 364-366, the
  "4 ticks of P" paragraph lines 367-372, the equity session row line 391 (O 08:30, C 15:00, F 15:08).
- Vehicles (reports/stage_e2a_vehicles.md lines 15-17 and 101-131; frozen via
  screening.stage_e_frozen.load_frozen_tables): Nasdaq-100 -> MNQ q_c 1; Russell 2000 -> M2K q_c 3;
  Dow -> MYM q_c 3; all "chosen". Operative eps (reports/stage_e2a_epsilon.md lines 36-38): MNQ 170,
  M2K 56, MYM 56 net ticks per contract per day.
- Frozen per-root values (checked 00:55 PDT through load_frozen_tables() and rules.products.product):
  day_session_ct = (08:30, 15:00) for MNQ, M2K, MYM; vendor_tick MNQ 0.25, M2K 0.10, MYM 1.00 (index
  points; $0.50 per tick per contract). F (rules/sessions.py, enforced by the engine) = 15:08 CT on a
  regular day.
- EC-CAL = the D10 equity calendar, data/calendars/equity.py, read through
  data.group_session.load_group_calendar("equity"). Research window (checked 00:57): non-trade dates
  2025-04-18, 2025-12-25, 2026-01-01; trade dates with an early engine F: 2025-05-26, 06-19, 07-03,
  07-04, 09-01, 11-27, 11-28, 12-24, 2026-01-19, 02-16, 04-03 (F 08:00), 05-25, 06-19 (flatten 11:30 or
  11:45 otherwise). US exchange holidays on which CME's equity session trades to an early halt are
  equity trade dates here (unlike crypto's BOOKED_FORWARD), so the bars' trade_date and C3's
  convention agree. Task 1b item C checks these dates.
- Release calendar reports/stage_e2b_release_calendar.json (frozen, sha256 839f2437...): research-window
  rows for the three roots are FOMC (13:00 CT, 10), ISM_SERVICES (09:00 CT, 15), NFP (07:30 CT, 14) on
  MNQ, M2K and MYM, and CPI (07:30 CT, 14, "cpi": true). The engine applies every CPI row's D9.12
  window to MNQ, M2K and MYM (rules/constraints.py lines 23-27; screening/stage_e_rules.py lines
  158-167, 391). No active K1 member reads a release instant or value: the engine's D9.5a guard,
  D9.12 and D8's event-window cost read them.
- External series: the Cboe VXN daily close (C lines 148-156), read by K1-vxnband-01 only, as a
  literal table (K1-L-01..K1-L-03). Task 1b fetches it free to data/vendor/index_history/vxn/.
- Source-window labels: K1-cp1-01 and K1-cp3-01 keep source-overlap (reports/
  stage_e2a_source_window_amendment.md lines 42-43); K1-cp2-01 (on the Nasdaq-100 trial, C line
  278; the JSON marks the member source_overlap true), K1-vxnband-01 (C line 405) and K1-vwap-01 (C
  line 504) carry it by R-04. Labels matter only for confirmation.

What the member does NOT implement (the engine and runner do; a member must not duplicate or
second-guess them; same list as E.3, E.4 and E.6): the window's trade dates and the removal of
roll-blackout dates (the engine refuses opens there by name, `engine_roll_blackout`; bars of those
dates are still delivered); 2026-06-18/19 (UR-1); F and the forced flatten (D9.1); costs and the
event-window cost (D8); the event-minute fill guard (D9.5a: a fill that would land in [release,
release + 2 min) moves to the first bar at or after release + 2 min: FOMC 13:00 and ISM Services
09:00 CT on all three roots); the CPI window (D9.12); the entry cap and the 2-minute minimum hold
(D9.3a/b) as refusals; the skip of an entry whose fill would come less than 2 full minutes before F;
price-limit proximity and its forced exit (D9.7, C11; rules/price_limits.py EQUITY_BANDS); the
lot-equivalent cap (D9.5).

---

## 0. Common to all five members

S0.1 Legs. Each declaration reads and trades exactly one leg, `LegSpec(root, True)` with root MNQ,
M2K or MYM. No signal legs; no full-size contract, ES or MES is read (C lines 84, 221, 280, 354, 406,
505). K1-vxnband-01 and K1-vwap-01 trade MNQ only (C lines 407-408, 506-507).

S0.2 Declarations. 11 `MemberDecl`s, label `"<member id> <root>"` (for example `"K1-cp1-01 MNQ"`);
the member object's `name` equals its label. One module per member under strategy/members/k1/;
zero-argument factories `make_mnq`, `make_m2k`, `make_mym` (vxnband and vwap: `make_mnq` only).
Ordinals in catalog order, then MNQ, M2K, MYM (K1-L-12):

| Ordinal | Label | Module | Factory | q_c |
|---|---|---|---|---|
| 1 | K1-cp1-01 MNQ | strategy.members.k1.cp1 | make_mnq | 1 |
| 2 | K1-cp1-01 M2K | strategy.members.k1.cp1 | make_m2k | 3 |
| 3 | K1-cp1-01 MYM | strategy.members.k1.cp1 | make_mym | 3 |
| 4 | K1-cp2-01 MNQ | strategy.members.k1.cp2 | make_mnq | 1 |
| 5 | K1-cp2-01 M2K | strategy.members.k1.cp2 | make_m2k | 3 |
| 6 | K1-cp2-01 MYM | strategy.members.k1.cp2 | make_mym | 3 |
| 7 | K1-cp3-01 MNQ | strategy.members.k1.cp3 | make_mnq | 1 |
| 8 | K1-cp3-01 M2K | strategy.members.k1.cp3 | make_m2k | 3 |
| 9 | K1-cp3-01 MYM | strategy.members.k1.cp3 | make_mym | 3 |
| 10 | K1-vxnband-01 MNQ | strategy.members.k1.vxnband | make_mnq | 1 |
| 11 | K1-vwap-01 MNQ | strategy.members.k1.vwap | make_mnq | 1 |

S0.3 Size. Every entry is `q_c` contracts, read from `load_frozen_tables().vehicles[root].q_c`, never
a literal (C6 lines 118-120). Every exit closes the whole position. No member sizes by signal. At most
one position. K1-vwap-01's reversal is two market intents (exit q_c, then entry q_c in the new
direction) sent on the same bar, never one 2 q_c order and never a stop (C lines 540-543, 570-571);
the engine processes intents in order against position plus pending (screening/stage_e_engine.py
lines 589-616).

S0.4 Clock and the trade date. America/Chicago. "The bar at hh:mm" of trade date d is the bar with
`trade_date == d` whose open (`ts_event_ns`) is hh:mm:00 CT on CT calendar date d (C1 lines 93-98;
E.3-L-03). The only bar on another CT date is CP1's first bar (17:00 CT on CT date d-1, E.3-L-05).
C3 (lines 101-102): trade date d = [d-1 17:00 CT, d 16:00 CT). Bars are identified by CT date and
clock (K7-L-01 adopted; in the equity calendar it agrees with the bars' trade_date). O and C come
from `load_frozen_tables().day_session_ct[root]` = (08:30, 15:00) (D line 391). A bar is usable at its
close (C1); `on_minute` is called at each grid minute's close with the bar in `view.bars[root]`, or
None. A single-leg member's grid may skip minutes with no bar, so a missing bar is detected by clock
(for example `bar.gap_before_minutes` or the previous bar's open), never assumed from the call
sequence.

S0.5 Orders. Market intents only (`leg_market_intent`), filled by the engine at the open of a later
bar (C2 lines 99-100). No limit orders, stops or brackets.

S0.6 Named entry bar. "Market intent on the bar at X" for an entry is emitted only when the view's
bar is the bar at X. If that bar is missing, there is no entry at X (E.3-L-04). An entry is emitted at
most once per decision (the ports and vxnband: once per trade date), and never while a position or a
pending order exists on the leg (vwap's reversal leg excepted, S0.3).

S0.7 Exits and flattens. Every exit is sent on the first present bar at or after the named bar, while
the position is non-zero and no exit order is pending (C4 lines 111-112: "If an exit's named bar is
missing, the exit is sent on the first later bar"). A refused exit is sent again on the next present
bar under the same condition (E.3-L-22). The engine's forced flatten at F is the backstop. If the
engine closes the position itself (D9.7, the flatten, an MLL liquidation), the member sees a flat
account and sends no exit. The ports and vxnband make no further entry that trade date; vwap applies
its rule as written at later bars (K1-L-09; K7-L-07).

S0.8 Trade-date exclusions of the two new members (C4 lines 103-112; the ports follow D6). vxnband and
vwap enter only on a trade date d in EQUITY_FULL_SESSIONS (K1-L-10): EC-CAL equity trade dates with no
early halt (`early_halt_ct` None) and the regular engine F (15:08 CT) on CT date d for MNQ, M2K and MYM
(K3-L-11 adopted), coverage 2019-05-01..2026-06-19 (EC-CAL's coverage, K4-L-13). Roll-blackout dates
are the engine's. K1's C4 names no vendor-degraded exclusion (K7-L-03 is K7's text and is NOT
adopted). The ports do not test these sets: CP1 and CP2 follow D6 (the engine's F governs); CP3 tests
the early halt through Family H (section 3).

S0.9 Instrument guard and missing bars of the new members (C4 lines 108-110). "A bar the rule reads"
is a bar read at or before the entry decision (E.3-L-12); "the entry bar" is the bar the entry intent
is emitted on (E.3-L-13). Each member's own clause is in its section (K1-L-04, K1-L-07). Exit and
flatten bars are not guarded.

S0.10 Prices. Every price comparison and sign is computed in integer vendor ticks,
`round(price / vendor_tick)` with `rules.products.product(root).vendor_tick`, never a literal tick
(E.3-L-19). Ratios and thresholds are compared exactly (integers, Fraction or Decimal; K4-L-05), never
with floats: CP3's CLV, vxnband's band (K1-L-04), vwap's VWAP comparison (K1-L-06).

S0.11 Tables (a member cannot read a file; E.3-L-01). Literal tables in the cluster package, generated
by a script under reports/stage_e7_briefs/ from the named sources, each with the sources' sha256, and
pinned by tests that recompute them from those sources. Coder B writes:
- strategy/members/k1/_calendar.py: EQUITY_TRADE_DATES (every EC-CAL equity trade date
  2019-05-01..2026-06-19, ISO, for vxnband's "trade date d-1") and EQUITY_FULL_SESSIONS (S0.8), with a
  comment naming the dates where the early-halt test and the F test disagree (if any), and a check that
  MNQ, M2K and MYM give the same F on every date.
- strategy/members/k1/_vxn.py: VXN_CLOSE, ISO calendar date -> the CLOSE field as its exact decimal
  string, every row of the saved Cboe file data/vendor/index_history/vxn/VXN_History.csv (sha256 in the
  module) dated 2019-04-30..2026-06-19 (K4-L-01: the table spans both windows; only research-window rows
  are checked, by Task 1b). Rows after 2026-06-19 are not included. Section 9 applies Task 1b's verdicts.

S0.12 trading_windows (D9 coverage; interface lines 51-61; E.3-L-17: fixed intervals measured on every
research date). One leg each:

| Member | Intervals [start, end) CT | Reference |
|---|---|---|
| CP1 | (17:00, 17:01) on day -1; (08:59, 09:00); (14:29, 15:00) | signal bars, entry bar to the 14:59 exit fill bar (E.4 and K7 CP1 pattern) |
| CP2 | (08:30, 15:08) | [O, F) (E.4 and K7 CP2 pattern; the interface's own example, interface lines 53-55) |
| CP3 | (08:30, 15:00) | [O, C) (E.4 and K7 CP3 pattern) |
| vxnband | (08:30, 15:00) | the C_prev bar (14:59 of a prior date), the scan [08:30, 14:29) and the exit fill bar 14:59 |
| vwap | (08:30, 15:00) | the VWAP bars from 08:30, the rule window [08:30, 14:57) and the 14:59 exit fill bar |

S0.13 Topstep checks common to all (each entry's list: C lines 261-273, 338-349, 389-399, 482-498,
578-591): flat by F (last fill 14:59; CP2 by the engine at F at the latest); market orders only; at
most 1 entry a day (vwap at most 20: D9.3a's 20 is never exceeded by rule); holds of at least 8 minutes
by rule except vwap, whose 2-minute minimum is built in (C lines 544-546); no stops, brackets or
passive fills (D9.4); MNQ, M2K and MYM are starred (C line 85): D9.12's CPI window allows up to 3
contracts, q_c <= 3, and no K1 fill lands before 08:31 CT, so it never binds (K1-L-15); position limit
<= 1 lot-equivalent (q_c x 0.1); price limit per D9.7 in the engine (C11).

---

## 1. K1-cp1-01 (core port CP1, intraday momentum). C lines 218-275; D line 364

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicles | MNQ q_c 1, M2K q_c 3, MYM q_c 3; one trial each | C 223-224; S0.2 |
| Signal | s = sign(close of the bar at O+29 = 08:59 minus open of the trade date's first bar), in ticks | C 246-247; D 364 |
| Trade date's first bar | the bar opening 17:00 CT on CT date d-1 (the calendar day before d), with trade_date d; Sunday 17:00 for a Monday; the holiday's 17:00 reopen for the trade date after an early-halt holiday | C 246-247 (C3 lines 101-102); E.3-L-05 |
| Signal-bar guard | both signal bars present with one instrument_id, else no trade | D 364; E.3-L-06 |
| Zero signal | s = 0: no trade | D 364 |
| Entry | market intent on the bar at C-31 = 14:29; buy if s > 0, sell if s < 0; fills at the 14:30 open | C 248-249; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 14:58; fills nominally at the 14:59 open | C 250; S0.7 |
| Hold | 29 minutes nominal | C 251 |
| Early halts | not tested by the member (port; on an early-halt day F precedes 14:29 and the engine refuses) | C 104 ("the ports follow D6 as written") |
| Parameters (literals) | O+29 = 08:59, C-31 = 14:29, C-2 = 14:58; no grid | C 255 |
| Release instants read | none; no release falls in 14:30-14:59 | C 266-267 |
| Trials in N | 3 | C 275 |
| Topstep | last fill 14:59; market; one trade a day; CPI window not touched | C 261-273 |

## 2. K1-cp2-01 (core port CP2, opening-range breakout). C lines 277-351; D line 365

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicles | MNQ 1, M2K 3, MYM 3 | C 281-282 |
| Opening range | OR_high = max high, OR_low = min low of the present bars opening in [O, O+15) = [08:30, 08:45) of CT date d; no OR bar: no trade; no minimum bar count, no instrument guard | C 310; E.3-L-08 |
| Buffer | 4 x vendor_tick of the traded vehicle: MNQ 1.00, M2K 0.40, MYM 4 (index points), 4 ticks each. It equals C's table (lines 313-319: 4 ticks of MNQ, RTY and MYM, the D1 most-active contracts) because M2K's tick equals RTY's (C lines 129-130); a test pins 1.00, 0.40 and 4 | C 312-318; D 367-372; K4-L-06 |
| Eligible bars | bars opening in [O+15, C) = [08:45, 15:00) of CT date d; no entry from 15:00 on | C 311 |
| Entry | the first eligible bar whose close >= OR_high + buffer buys; whose close <= OR_low - buffer sells (non-strict); market intent on that bar; one entry per trade date (the first qualifying bar uses the day's entry even if the engine refuses it) | C 319-321; E.3-L-08 |
| Exit | 75 minutes after the fill, counted as the MES module counts it: count present bars while the position is non-zero, starting after the entry intent bar; on the 75th, a market intent closing the position; or the engine's flatten at F if earlier. No C-2 exit | C 322-325; E.3-L-07 |
| Hold | 75 minutes; fills after 13:53 are cut by F (the shortest, a 15:00 fill, 8 minutes) | C 322-326 |
| Early halts, guard | none (port) | C 104; E.3-L-08 |
| Parameters (literals) | OR 15 minutes, buffer 4 ticks, hold 75 minutes; no grid | C 333-334 |
| Release instants read | none; fills in [13:00, 13:02) on FOMC days and [09:00, 09:02) on ISM Services days are moved by the engine (D9.5a); fills in [13:00, 13:30) and [09:00, 09:30) on those days pay D8's event cost | C 343-345; release calendar |
| Trials in N | 3 | C 351 |
| Topstep | flatten by the engine at F; market; one trade a day | C 338-349 |

## 3. K1-cp3-01 (core port CP3, prior-close location). C lines 353-401; D line 366

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicles | MNQ 1, M2K 3, MYM 3 | C 355-356 |
| Daily bar of trade date d | from the bars of CT date d opening in [O, C) = [08:30, 15:00): O_d = open of the 08:30 bar, H_d / L_d = max high / min low over the present bars, C_d = close of the 14:59 bar | C 373-374 |
| Complete day (Family H) | the 08:30 and 14:59 bars exist, the date is not an early halt (the bars carry early_halt_ct), and all bars in [08:30, 15:00) carry one instrument_id; finalised when a bar of a later trade date arrives | C 375-376; E.3 spec section 3 |
| "d-1" | the most recent COMPLETE daily bar of a trade date before d; incomplete days are dropped (an early-halt holiday is incomplete, so the Tuesday after Memorial Day reads Friday) | C 377-378; E.3-L-09 |
| Warm-up | no complete earlier bar yet: no trade | E.3 spec section 3 |
| Instrument guard | d-1's instrument_id equals the instrument_id of day d's 08:30 bar, else no trade | C 377 |
| Condition | Range = H - L of d-1 in ticks, > 0; CLV = (C - L) / (H - L) in ticks, exact; CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict) | C 378-379 |
| Day d exclusion | a trade date d whose 08:30 bar carries early_halt_ct: no trade | E.3-L-09, E.3-L-11 |
| Entry | market intent on the 08:30 bar of d (fills at the 08:31 open); the 08:30 bar must exist | C 380; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 14:58 (fills nominally at 14:59) | C 381; E.3-L-10 |
| Hold | about 388 minutes | C 382 |
| Parameters (literals) | CLV cuts 0.2 and 0.8, lookback 1; no grid | C 386 |
| Release instants read | none | C 394-395 |
| Trials in N | 3 | C 401 |
| Topstep | last fill 14:59; holds through FOMC and ISM at <= 1 lot-equivalent | C 389-399 |

## 4. K1-vxnband-01 (fade a breach of the VXN/16 band at VXN extremes). C lines 403-500

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | Nasdaq-100 MNQ only, q_c 1 | C 407-408 |
| Trade dates | d in EQUITY_FULL_SESSIONS (S0.8); roll blackouts by the engine | C4 104-110; K1-L-10 |
| C_prev | close of MNQ's 14:59 bar on the most recent COMPLETE trade date before d (Family H completeness exactly as CP3 section 3: 08:30 and 14:59 bars exist, no early_halt_ct, one instrument_id over [08:30, 15:00)) | C 442-443; K1-L-03 |
| Instrument guard | the C_prev bar's instrument_id equals that of d's 08:30 bar, else no trade on d; d's 08:30 bar missing: no trade on d | C 443-444; K1-L-03 |
| V | VXN_CLOSE[the calendar date of trade date d-1], where trade date d-1 is the EQUITY_TRADE_DATES entry immediately before d; no row: no trade on d | C 445; K1-L-02 |
| V availability | the close of trade date d-1 is used only from 08:30 CT on d: the earliest decision that reads V is the close of the 08:30 bar (08:31 CT); V of d itself is never read | C 154, 457-458; K1-L-01 |
| Band | w = C_prev x V / 1600; U = C_prev + w; L = C_prev - w; compared exactly in ticks: sell iff 1600 x (close_t - C_prev) > C_prev x V, buy iff 1600 x (close_t - C_prev) < -(C_prev x V) (strict) | C 446, 460-461, 468; K1-L-04 |
| Regime | trade on d only if V < 20 (strict) or V >= 30 (non-strict), exact decimal compare | C 447, 462 |
| Scan and entry | on the first bar of CT date d opening in [08:30, 14:29) whose close is > U: SELL q_c; < L: BUY q_c; market intent on that bar (fills at the next open). At most one entry per trade date: the first breach on either side uses the day's entry, even if the engine refuses it | C 448-450, 465-466; E.3-L-08; K1-L-04 |
| Missing bar / id change in the scan | a minute in [08:30, t] with no bar, seen before the first breach, or a scan bar whose instrument_id differs from the 08:30 bar's: no entry for the rest of d | C4 108-110; E.3-L-12; K1-L-04 |
| Exit | market intent on the bar opening 30 minutes after the entry-intent bar (fill 31 minutes after the intent bar = 30 minutes after a nominal entry fill); if missing, the first later present bar; latest intent bar 14:28 -> fill 14:29 -> exit intent 14:58 -> fill 14:59 | C 451-452; S0.7; K1-L-05 |
| Hold | 30 minutes nominal | C 453 |
| Parameters (literals) | 16 and 1600; VXN cuts 20 (strict) and 30 (non-strict); hold 30; scan [08:30, 14:29); C_prev = 14:59 close; RTH bars only; strict breach; no grid | C 460-472 |
| Release instants read | none (FOMC 13:00 and ISM 09:00 fills moved by the engine) | C 490-492 |
| Trials in N | 1 | C 500 |
| Topstep | last fill 14:59; market; one trade a day; CPI window not touched (earliest fill 08:31) | C 482-498 |

## 5. K1-vwap-01 (stop-and-reverse around the session VWAP, D9 floor). C lines 502-593

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | Nasdaq-100 MNQ only, q_c 1 | C 506-507 |
| Trade dates | d in EQUITY_FULL_SESSIONS (S0.8); roll blackouts by the engine | C4; K1-L-10 |
| VWAP | TP_b = (H_b + L_b + C_b) / 3; VWAP_t = sum(TP_b x vol_b) / sum(vol_b) over the present bars of CT date d opening from 08:30 through t inclusive; known at t's close | C 531-534; K1-L-06 |
| Sign | s_t = +1 if close_t > VWAP_t, -1 if close_t < VWAP_t, else s_(t-1) (0 before the first sign of the day); exact: sign(3 x close_t x sum(vol) - sum((H + L + C) x vol)) in ticks; sum(vol) = 0: no action on that bar (s not updated) | C 535-536; K1-L-06 |
| Rule window | evaluated on every bar t opening in [08:30, 14:57) | C 537 |
| Flat entry | if flat (no position, no pending), s_t != 0 and fewer than 20 entries today: market intent q_c in direction s_t | C 538 |
| Reversal | if the position is opposite to s_t (s_t != 0), no order is pending, and the minimum hold is met: exit intent (close the position), and if fewer than 20 entries today, a second intent q_c in direction s_t; both on bar t, both fill at the next open | C 539-543; S0.3 |
| Otherwise | nothing (same sign, or hold not met: wait; the next bar re-evaluates) | C 543 |
| Minimum hold | a position filled at the open of bar k (the bar at whose call the member first sees it) may be exited only by an intent on a bar opening at or after k + 1 minute | C 544-546; K1-L-09 |
| Entry cap | entry intents per trade date, including reversal legs, at most 20, counted when sent; after the 20th, the next opposite signal (hold met) exits to flat for the rest of the day | C 547-549; K1-L-08 |
| Final exit | market intent on the first bar at or after 14:58 (fills at 14:59); no entry intent from the 14:57 bar on; 14:57 is outside the rule window | C 550-552 |
| Missing bar | a minute in [08:30, t] with no bar (by clock): no new entry (flat entries and reversal legs) for the rest of d; an open position keeps the rule's exits (opposite-signal exit to flat, final exit) | C4 108-110; K1-L-07 |
| Instrument change | reference = d's 08:30 bar's id; from the first bar with another id: no new entry for the rest of d, and an open position gets an exit intent on that bar (fills at the next open) | C 558-559; K1-L-07 |
| Hold | 2 to 388 minutes | C 553-555 |
| Parameters (literals) | RTH start 08:30; C-2 = 14:58; TP-based VWAP; tie keeps the sign; 20 entries; 2-minute hold; no grid | C 562-575 |
| Release instants read | none (fills in [13:00, 13:02) on FOMC days and [09:00, 09:02) on ISM Services days are moved by the engine, which can delay a reversal) | C 586-588 |
| Trials in N | 1 | C 593 |
| Topstep | last fill 14:59; market; at most 20 entries a day, each held >= 2 minutes; reversal nets to q_c | C 578-591 |

## 6. Trial count

11 declarations (S0.2): 9 port trials (3 ports x MNQ, M2K, MYM) + K1-vxnband-01 MNQ + K1-vwap-01 MNQ.
This matches the E.1 JSON (reports/stage_e1_changes.md line 1850: K1 members_active 5, trials 11) and
the prompt's expectation. Program N after K1: 156 + the K1 trials screened (K1-L-16).

## 7. (reserved)

## 8. Lead readings (each is also an open choice in reports/E.7_RETURN.md section 6)

Adopted from earlier clusters (the text is the same): E.3-L-01 (literal tables), E.3-L-03 (the bar at
hh:mm is on CT date d), E.3-L-04 (named entry bar exact), E.3-L-05 (CP1's first bar is the 17:00 bar of
CT date d-1), E.3-L-06 (CP1's guard is D6's), E.3-L-07 (CP2 counts present bars, no C-2 exit), E.3-L-08
(CP2's range from present bars; the first qualifying bar uses the day's entry), E.3-L-09 (CP3 by Family
H), E.3-L-10 (CP3 exits at the first bar at or after C-2), E.3-L-11 (early halt = the bar's
early_halt_ct), E.3-L-12 (C4's "a bar the rule reads" = at or before the entry decision), E.3-L-13 (C4's
"entry bar" = the bar the entry intent is emitted on), E.3-L-17 (fixed trading_windows), E.3-L-19
(integer vendor ticks), E.3-L-22 (a refused exit is resent), K4-L-01 (tables span the whole period;
only research-window rows are checked), K4-L-05 (exact threshold compares), K4-L-06 (CP2's buffer as 4 x
vendor_tick), K4-L-13 (full-session table over EC-CAL's coverage only), K3-L-11 (an early engine F is an
early close for C4), K7-L-01 (bars identified by CT date and clock), K7-L-07 (engine closures in a
multi-decision member). Not adopted: K7-L-03 (vendor-degraded dates; K1's C4 has no such clause).

New readings for K1:
- **K1-L-01 VXN availability is 08:30 CT on d, as the entry states.** vxnband's entry (C lines 457-458:
  "It is used from 08:30 CT on d") and C9 (line 154: "the close of trade date d-1 is used only
  from 08:30 CT on d") fix it. The stage prompt's test list cites "the catalog KF1 row: from 08:35 CT on
  d"; KF1 (C line 725) is K1-ml-01's feature table (excluded, U6), whose 08:35 is the ML decision window
  start W0, set by KF6's first five-minute candle (C lines 733-737), not by VXN's publication. Using
  08:35 would drop breaches on the 08:30-08:33 bars and change the frozen rule, which the prompt forbids.
  The earliest decision that reads V is the 08:30 bar's close (08:31 CT). Task 1b records Cboe's
  publication time, which must precede 08:30 CT on d. Flagged for the user.
- **K1-L-02 V's date is the calendar date of the EC-CAL trade date before d.** C line 445 ("the Cboe VXN
  close for the calendar date of trade date d-1") with C3's trade dates. Early-halt exchange holidays
  (Memorial Day, Juneteenth, July 4, Labor Day, MLK, Presidents' Day, Good Friday 2026) are equity trade
  dates, and Cboe publishes no VXN for them, so the trade date after each has no V and no trade ("If it
  is missing, no trade on d", C line 445). Not adopted, the wider reading: V of C_prev's date. The entry
  distinguishes "the previous complete trade date" (C_prev) from "trade date d-1" (V).
- **K1-L-03 C_prev by Family H completeness, as CP3's d-1.** The most recent complete trade date before
  d, completeness tested exactly as CP3 (section 3), finalised when a later date's bar arrives; its 14:59
  close; guard against d's 08:30 bar (missing: no trade).
- **K1-L-04 vxnband's scan.** Exact integer compare in ticks (the tick cancels: both sides are linear in
  price); V as an exact decimal. The scan is by clock over [08:30, 14:29) of CT date d. C4's missing-bar
  and instrument clauses apply to the bars read at or before the entry decision (E.3-L-12): a minute
  without a bar, or a bar with another instrument_id, seen before the first breach ends the day's entry
  search (narrowest: the first breach cannot be established). The first breach uses the day's one entry
  even if the engine refuses the intent (E.3-L-08).
- **K1-L-05 vxnband's exit by clock.** C line 451 names both "the 30th bar after the entry-intent bar"
  and "filling 30 minutes after the entry fill": the exit intent goes on the bar opening at entry-intent
  bar + 30 minutes (a clock minute), or on the first later present bar if it is missing (C4 line 111).
  When the engine moves the entry fill (D9.5a, 13:00 FOMC or 09:00 ISM), the exit intent bar stays
  entry-intent + 30, so that hold is up to 2 minutes shorter (still >= 28 minutes). An exit is sent only
  while a position is open.
- **K1-L-06 vwap's arithmetic.** VWAP over the present bars of CT date d from 08:30 (Databento writes
  no ohlcv-1m bar for a minute without trades, so a missing minute adds no volume); the sign by exact
  integer arithmetic in ticks.
- **K1-L-07 vwap's missing bars and instrument change.** The entry fixes the instrument change (C lines
  558-559). For a missing bar the entry is silent and C4 applies (bars read at or before the entry
  decision, E.3-L-12): from the bar after a gap, no new entry for the rest of d, as if the cap were
  reached; an open position keeps the rule's own exits (the opposite-signal exit to flat, the final
  exit). A missing 08:30 bar is a gap at the start: no trade on d. Narrowest reading that adds no exit
  rule the entry does not state.
- **K1-L-08 vwap's entry count.** Entry intents sent on d, reversal legs included, counted when sent
  (a refused entry still counts), at most 20: fewer or equal fills than a count of fills.
- **K1-L-09 vwap's minimum hold and pending orders.** The engine fills at a bar's open before calling the
  member at that bar's close, so the fill bar k is the bar at which the member first sees the new
  position; exit or reversal intents only on bars opening at or after k + 1 minute (fill at k + 2 or
  later, D9.3b's 2 minutes exactly). No intent is sent while an order is pending on the leg (a deferred
  fill, D9.5a). A position the engine closes leaves the account flat; the rule applies as written at
  later bars (K7-L-07).
- **K1-L-10 C4's early-close test by table.** EQUITY_FULL_SESSIONS (S0.8) for vxnband's and vwap's day
  d; CP3 and vxnband's C_prev use Family H's bar test. The generator lists any date where the two tests
  disagree.
- **K1-L-11 trading_windows** as S0.12.
- **K1-L-12 11 declarations**, ordinals in catalog order then MNQ, M2K, MYM.
- **K1-L-13 Two coders, test files tests/test_k1_members_ports*.py (coder A) and
  tests/test_k1_members_vxnband*.py, tests/test_k1_members_vwap*.py, tests/test_k1_members_tables.py
  (coder B)**, as E.3-L-21.
- **K1-L-14 C section 7 settled by the frozen text:** item 1 (the user ran K1, V15); item 2 (predrift
  excluded by the E.0 lead, C line 597); item 3 (vwap kept as frozen and counted; its cost fragility is
  a reported limitation, D8 frozen); item 4 (one trial, cuts as written); item 5 (E.2a chose the micros
  MNQ, M2K, MYM, so the mini-halt note is moot); item 6 (settled by the frozen release calendar: its
  ISM_SERVICES rows carry MNQ, M2K and MYM, so the engine applies D8 and D9.5a to all three; no member
  reads it); item 7 (ML excluded); item 8 (not written); item 9 (no member uses it); item 10 (a) Task 1b,
  (b) moot (predrift excluded), (c) the research window uses the frozen vendor_tick, the tick history is
  a confirmation-session check (amended 02:47 after audit finding 2, R-T3-2: the research bars are on the frozen grid,
  0 off-tick prices in reports/stage_e2a_bars.json raw_checks; only CP2's buffer depends on the tick size, so the three
  K1-cp2-01 trials carry the label "tick history not source-verified for the research window"), (d) settled by the harness (rules/price_limits.py EQUITY_BANDS for MNQ,
  M2K, MYM), (e) E.2a's vehicles use their own bars, (f) the runner's D9 coverage on S0.12's windows;
  item 11 no action.
- **K1-L-15 The CPI window.** No K1 member emits an intent that fills before 08:31 CT (CP1 only reads the
  17:00 bar of d-1), and q_c <= 3 = D9.12's micro limit, so D9.12 never binds (C line 85). Tests pin that
  no member emits an intent on bars in [07:25, 07:35] CT of a CPI date.
- **K1-L-16 The N rule** (K7-L-05's, pre-declared before any run): a trial counts when the runner writes
  its screen record (status "run"); a trial the runner excludes before screening (coverage) or refuses
  does not count.

## 9. The research-window check and the rulings (lead, 01:12 PDT, after Task 1b)

Source: reports/stage_e7_release_check.md and .json (ReleaseChecker-OpusMed, 00:52-01:08 PDT). The VXN file:
data/vendor/index_history/vxn/VXN_History.csv, sha256 f1b00135c4922ea756cd22cfeaa1d483700a6aed580f8da562f61574b5e1cdcc,
fetched 2026-09-28 00:55:48 PDT from https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv (served by
cdn-api.cboe.com), 4,287 rows 2009-09-14..2026-09-25, Last-Modified 2026-09-25 22:01:14 GMT; manifest
data/vendor/index_history/vxn/manifest.jsonl.

- **R-1b-1 VXN kept.** Obtained free; 1,797 rows in 2019-04-30..2026-06-19; the 67 weekdays without a row are all NYSE
  closures (none on an open day); every CLOSE parses as an exact decimal (6 decimals, none beyond the second non-zero).
  Research-window values equal FRED VXNCLS's current copy on every date (0 differences); no 2025-2026 capture of the Cboe
  file exists, so they are not point-in-time checked. K1-vxnband-01 therefore carries the label "VXN values not
  point-in-time checked for the research window" into the return (the prompt's failure path: kept as the frozen input
  gives them, and labelled). The 2020-10-16 row (O = H = L = C = 35.02 on an open day) is kept: the member reads CLOSE, and
  CLOSE equals FRED's.
- **R-1b-2 2024-02-01 DROPPED (confirmation window only).** The 2024-04-19 Wayback copy of the same file has CLOSE 11.20;
  the current file (and FRED) 17.33. A value its own vendor has revised cannot be fixed as the value available at 08:30
  CT on 2024-02-02, and the verdict set is keep, drop or unverifiable, so the row is dropped: V is missing for
  d = 2024-02-02, which is not traded. It removes one trade possibility and never adds or times one. Both values are
  below 20, so the regime would admit the date either way; only the band width differs. Flagged for the user.
- **R-1b-3 2021-04-02 and 2021-12-24 DROPPED (confirmation window only).** NYSE was closed on both (Good Friday;
  Christmas observed), and each row repeats the prior day's close on all four fields: it is not a close of that date.
  Dropping them makes these two closures like the other 67 (no row). Effect: d = 2021-04-05 (whose EC-CAL trade date
  d-1 is 2021-04-02, an 08:15 halt) has no V and is not traded; 2021-12-24 is not an equity trade date, so its drop
  changes nothing.
- **R-1b-4 Publication time.** No Cboe statement exists; the file's Last-Modified (17:01 CDT on the last row's date) and
  two Wayback captures (08:05 CST and 04:12 CDT on D+1, each already holding D's row) put publication before 08:30 CT on
  D+1 in every informative observation. K1-L-01's 08:30 availability stands; observational, not a stated guarantee.
- **R-1b-5 The research dates without V** (K1-L-02 confirmed): 2025-05-27, 06-20, 07-07, 09-02, 11-28, 2026-01-20,
  02-17, 04-06, 05-26 read a trade date d-1 with no VXN row (Cboe closed), so K1-vxnband-01 does not trade them
  (2025-11-28 is an early-halt date anyway).
- **R-1b-6 CPI.** All 14 research-window CPI instants kept (BLS schedule pages; the delayed 2025-10-24 and 2025-12-18
  releases and the cancelled October 2025 CPI confirmed by BLS notices). D9.12 never binds on K1 (K1-L-15).
- **R-1b-7 Calendar.** All 16 research-window equity dates the members meet (3 closures, 13 early halts or early F) are
  cited in data/calendars/equity.py and agree across MNQ, M2K and MYM; keep. The early flatten times (11:30 in 2025,
  11:45 in 2026 on 12:00-halt days) are rules/sessions.py's (harness).
- **R-1b-8 Other inputs.** No active K1 member reads a release; the FOMC (10), NFP (14) and ISM_SERVICES (15) rows per root
  are harness inputs (D8, D9.5a).

VXN_CLOSE is therefore every row of the file dated 2019-04-30..2026-06-19 less DROPPED_VXN = {2021-04-02, 2021-12-24,
2024-02-01}, each listed in _vxn.py with its reason, and pinned by the table test.
