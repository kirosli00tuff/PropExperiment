# Stage E.9 member specifications, cluster K8 cross-market (Task 1)

Written by the Stage E.9 lead (Opus 5.5, xhigh), 2026-10-01 22:21-22:33 PDT, before any K8 member code
exists and before any K8 bar has been read by this session. It restates each frozen entry as the code
must implement it, with line references, and records every reading the lead took where the entry leaves
a detail open (section 6). It changes no rule. A reading is the narrowest one the text allows unless the
text fixes the detail (then the text governs). Where K8's text is the same as an earlier cluster's, the
earlier reading is adopted and cited (E.3-L-nn: reports/stage_e3_member_specs.md section 10; K4-L-nn:
reports/stage_e4_member_specs.md section 10; K5-L-nn: reports/stage_e4b_member_specs.md; K3-L-nn:
reports/stage_e4c_member_specs.md section 10; K7-L-nn: reports/stage_e6_member_specs.md section 8;
K1-L-nn: reports/stage_e7_member_specs.md section 8; K6-L-nn: reports/stage_e8_member_specs.md
section 9).

Sources and their state:
- C = reports/stage_e0_catalog_K8.md, frozen by reports/stage_e1_freeze.json (manifest 96166eb3...).
  Line numbers below are this file's. Banner lines 3-7 (E.1: U6, K8-ml-01 excluded; U3, K8 last;
  3 active members, 4 trials). Header table lines 74-84; conventions C1-C15 lines 86-249 (C1 88, C2 91,
  C3 94-103, C4 104-113, C5 114-128, C6 130-143, C7 145, C8 149-165, C9 166-191, C10 192-208, C12
  220-227, C13 228-236, C14 237-243, C15 244-246); members: K8-flight-01 lines 252-371, K8-oilcad-01
  lines 373-488, K8-wkndbtc-01 lines 490-608; K8-ml-01 lines 610-709 (excluded, U6; not coded); trial
  table section 5 lines 829-845; questions section 6 lines 848-901. E.1's edits to K8
  (reports/stage_e1_changes.md K8-00, K8-01, K8-03, K8-04) touch only the banner, K8-ml-01 and the
  header's ML and trial rows. No active member's rule changed.
- V16 = docs/DECISIONS.md lines 310-321 (user, 2026-09-28): settles C section 6 items 1-4 (section 6
  below, K8-L-15). D4 = docs/STAGE_E_DESIGN.md lines 274-280 (cross-product members: every leg at its
  own S, the union of every leg's roll blackouts, every leg passes D9's coverage check).
- D = docs/STAGE_E_DESIGN.md (frozen): D5 lines 298-347; D6 session table (equity 391: O 08:30, C 15:00,
  F 15:08; FX 394: 07:20, 14:00, 15:08; energy 395: 08:00, 13:30, 15:08; gold 396: 07:20, 12:30, 15:08;
  crypto 402: 08:30, 15:00, 15:08); D9.5a lines 516-521.
- Vehicles (reports/stage_e2a_vehicles.md lines 15, 27, 35; frozen via
  screening.stage_e_frozen.load_frozen_tables, checked by the lead 22:20 PDT): gold MGC q_c 1 "chosen";
  CAD 6C q_c 1 "undersized" (rho 0.3335); Nasdaq-100 MNQ q_c 1 "chosen". Operative eps
  (load_frozen_tables().eps_operative): MGC 71, 6C 9, MNQ 170 net ticks per contract per day. Signal
  legs (no vehicle, no position): MES (S&P 500, owned; research parquet sha256 aea959a5... =
  MES_RESEARCH_SHA256), MCL (crude, V16(c)), MBT (bitcoin). Every leg has a recorded research parquet
  sha256 in the frozen tables (MES aea959a5, MGC f6bcdd63, MCL 6be9bb5b, 6C 5c391439, MBT 78ef1710,
  MNQ 9506eace).
- Frozen per-root values (rules.products.product and rules.sessions, checked by the lead 22:20 PDT):
  groups MES equity, MNQ equity, MBT crypto, MGC metals, MCL energy, 6C fx; vendor_tick MES 0.25, MNQ
  0.25, MBT 5.00, MGC 0.10, MCL 0.01, 6C 0.00005 (vendor_price_factor 1 for all six); engine F
  (rules.sessions.flatten_time_ct) 15:08 CT on a regular day for all six (11:45 on 2025-11-28).
- EC-CAL = the D10 group calendars data/calendars/{equity,crypto,metals,energy,fx}.py, read through
  data.group_session.load_group_calendar(group) and rules.sessions. Task 1b item E lists the research-
  window exceptions.
- Release calendar reports/stage_e2b_release_calendar.json (frozen, sha256 839f2437...; loaded by the
  runner; coverage 2019-05-01..2026-06-21). Research-window rows whose products include a traded K8
  root (lead count 22:20 PDT; Task 1b item A checks them): MGC: NFP 14 (08:30 ET), CPI 14 (08:30 ET),
  G17 14 (09:15 ET), FOMC 10 (14:00 ET); 6C: WPSR 64 (56 at 10:30 ET, 7 at 12:00 ET, 1 at 17:00 ET),
  NFP 14, FOMC 10; MNQ: ISM_SERVICES 15 (10:00 ET), NFP 14, CPI 14, FOMC 10. The engine's D9.5a guard
  and D8's event-window cost read these rows; C6's skip (section 0, S0.10) reads the same rows.
- External series: none. No K8 member reads a price series from outside the bars or any released
  value (Task 1b item F confirms).
- Source-window labels: K8-flight-01 and K8-oilcad-01 not source-overlap
  (reports/stage_e2a_source_window_amendment.md lines 77-78); K8-wkndbtc-01 source-overlap (C lines
  604-607, C15). Labels matter only for confirmation.

What the member does NOT implement (the engine and runner do; a member must not duplicate or
second-guess them; same list as E.3-E.8): the window's trade dates (D4: the trade dates every leg has
bars on, less the union of EVERY leg's roll blackouts, signal legs included, V16(a); less UR-1's
2026-06-18/19), refusing opens there by name (`engine_not_a_window_date`, `engine_roll_blackout`);
F and the forced flatten (D9.1); costs and the event-window cost (D8); the event-minute fill guard for
exits and for any fill the member did not skip (D9.5a: a fill that would land in [release, release +
2 min) moves to the first bar at or after release + 2 min); the entry cap and the 2-minute minimum hold
(D9.3a/b); the refusal of an open when any leg the member reads has no bar at that minute (D11.5);
price-limit proximity (D9.7: MNQ's equity bands, rules/price_limits.py EQUITY_BANDS; MGC and 6C are
DCB_ONLY there, so D9.7 does not fire on them, ruling L-13), the CPI window (D9.12), the lot-equivalent cap (D9.5); D9's coverage check on every leg,
signal legs included (V16, C13), on the intervals the member declares (S0.12).

---

## 0. Common to all three members

S0.1 Legs. Every declaration has exactly one traded leg, declared FIRST (the primary leg whose vehicle,
q_c and eps the series uses; template step 3), then its one signal leg, `LegSpec(root, False)`:
flight (MGC traded, MES signal), oilcad (6C traded, MCL signal), wkndbtc (MNQ traded, MBT signal)
(C header lines 79-80; C lines 254-257, 375-378, 492-495; V16(b), (c)). No member reads NKD, MET or 6M.

S0.2 Declarations. 4 `MemberDecl`s, catalog order (C section 5, lines 833-836; the prompt's ordinal
order), label = member id, grid point (flight only), traded root; the member object's `name` equals its
label. One module per member under strategy/members/k8/:

| Ordinal | Label | Module | Factory | Legs (traded first) | q_c |
|---|---|---|---|---|---|
| 1 | K8-flight-01 H30 MGC | strategy.members.k8.flight | make_h30 | MGC (traded), MES (signal) | 1 |
| 2 | K8-flight-01 HEOD MGC | strategy.members.k8.flight | make_heod | MGC (traded), MES (signal) | 1 |
| 3 | K8-oilcad-01 6C | strategy.members.k8.oilcad | make_6c | 6C (traded), MCL (signal) | 1 |
| 4 | K8-wkndbtc-01 MNQ | strategy.members.k8.wkndbtc | make_mnq | MNQ (traded), MBT (signal) | 1 |

S0.3 Size. Every entry is `q_c` contracts of the traded leg, read from
`load_frozen_tables().vehicles[root].q_c` (1 for MGC, 6C, MNQ), never a literal (C7 lines 145-148). A
signal leg never takes a position. Every exit closes the whole position. No member sizes by signal,
holds two legs or reverses.

S0.4 Clock, bars and the trade date. America/Chicago. "The bar at hh:mm" of leg X on trade date d is
the bar of X whose open (`ts_event_ns`) is hh:mm:00 CT on CT calendar date d and whose `trade_date` is
d (C1 line 88; E.3-L-03). C_X(tau) is that bar's close, usable from its close on (C1). Bars are
identified per leg, by CT date and clock, never by `trade_date` and clock alone (K7-L-01). The only
bars on another CT date that any member reads are wkndbtc's (S3: MBT at 14:59 on the Friday d-3,
trade date d-3; MBT and MNQ at 17:59 and MNQ at 18:00 on the Sunday d-1, trade date d). Trade date d =
[d-1 17:00 CT, d 16:00 CT) (C3 line 95). `on_minute` is called at each minute of the member's shared
UTC grid (the union of its legs' bar minutes) at that minute's close, with each leg's bar or None; a
missing bar is detected by clock, never assumed from the call sequence (K6 S0.4).

S0.5 Orders. Market intents only (`leg_market_intent`) on the traded leg, filled by the engine at the
open of the traded leg's next bar (C2 lines 91-93; C4 lines 107-108). No limit orders, stops or
brackets.

S0.6 Named entry bar (E.3-L-04). "Market intent on the [traded leg's] bar at X" is emitted only on a
view whose traded-leg bar is the bar at X; if that bar is missing there is no entry at X (the reading
per member is in its section: flight K8-L-06, oilcad per decision, wkndbtc no trade). An entry is never
emitted while a position or a pending order exists on the traded leg.

S0.7 Exits. T_e = the entry fill minute: the CT open of the traded-leg bar at which the account first
shows the position (the engine fills at that bar's open before calling the member; K8-L-07). An exit is
"market intent on the bar at X"; it is sent on the first present traded-leg bar at or after X while the
position is non-zero and no exit order is pending (C5 lines 120-121: "If an exit's named bar is missing,
the exit is sent on the first later bar. The engine's forced flatten at F is the backstop"). A refused
exit is resent on the next present bar under the same condition (E.3-L-22). Exit bars are never
guarded (no instrument or signal-bar check) and exits are never skipped (C6: exits deferred by D9.5a
are left to the harness). If the engine closes the position itself (D9.7 exit, flatten, MLL), the
member sees a flat account and sends no exit.

S0.8 Trade-date exclusions (C5 lines 114-128). A member enters only on a trade date d that is a FULL
SESSION in the group calendar of EVERY leg it reads (C5 line 118: "dates that any leg's D10 group
calendar (equity-and-crypto, energy, FX, metals) marks as early close, early halt or closure";
K8-L-03): flight EQUITY and METALS; oilcad ENERGY and FX; wkndbtc EQUITY and CRYPTO (for the Monday d
and its Friday d-3). A full session of a group = an EC-CAL trade date of the group with no early halt
and the regular engine F (15:08 CT) on CT date d for the group's K8 roots (K3-L-11, K7-L-02, K1-L-10),
from literal tables over 2019-05-01..2026-06-19 (K4-L-13; S0.11). Roll-blackout dates of any leg are
the engine's (D4, V16(a)): C5's "Signal-leg rolls ... are not excluded" (C lines 123-125) yields to D4
(V16(a)), and the member does nothing for it. The missing-bar clause (C5 line 119) is applied per
computation as each member's section states.

S0.9 Instrument guard and missing bars (C4 lines 104-113). Every signal computation reads two bars of
the signal leg; both must be present and carry ONE instrument_id, else that computation is undefined
(no trade from it). Instrument ids are compared only within a leg (the legs are different products;
K6 S0.9 crushgap). No forward fill: a None is never a price (interface lines 8-11). The traded leg's
entry bar must be present (S0.6). Exit bars are not guarded.

S0.10 Guarded entries (C6 lines 130-143; K8-L-08). An entry whose fill minute t (the open of the traded
leg's bar at t, the minute after the entry bar) lies in [R, R + 2 min) for a release instant R of the
traded root is SKIPPED, not deferred. The instants are the frozen release calendar's rows whose
"products" include the traded root (the engine's D9.5a set for that root), as a literal table
(S0.11). Since every K8 entry fill is on a whole minute, the test is t == R or t == R + 1 min. For the
research window this skips: flight (MGC) a trigger at 13:00 on an FOMC date (the NFP, CPI and G17
instants, 07:30 and 08:15 CT, precede the first fill 08:35); oilcad (6C) the decision t = 09:30 on a
standard WPSR date, t = 10:00 or 11:00 on a holiday-week WPSR date at those times, and t = 13:00 on an
FOMC date; wkndbtc (MNQ) nothing (no row at Sunday 18:00 or Monday 14:59). Task 1b item A3 lists the
dates.

S0.11 Tables (a member cannot read a file and cannot import data.* or the release calendar: template
lines 9-21; E.3-L-01). Literal tables in the cluster package, generated by
reports/stage_e9_briefs/gen_k8_tables.py from the named sources, each module recording the sources'
sha256, and pinned by tests that recompute them (tests may import rules.*, data.*, screening.*).
MemberCoder-A writes them FIRST; coder B imports them:
- strategy/members/k8/_calendar.py: EQUITY_FULL_SESSIONS, CRYPTO_FULL_SESSIONS, METALS_FULL_SESSIONS,
  ENERGY_FULL_SESSIONS, FX_FULL_SESSIONS: frozenset[date], 2019-05-01..2026-06-19, each the group's
  EC-CAL trade dates with no early halt and engine F = 15:08 CT on CT date d for the K8 roots of the
  group (equity: MES and MNQ; crypto MBT; metals MGC; energy MCL; fx 6C), with a check (generator and
  test) that the roots of a group agree on every date; and member date tuples (sorted):
  FLIGHT_DATES = EQUITY & METALS, OILCAD_DATES = ENERGY & FX, WKNDBTC_DATES = EQUITY & CRYPTO. The
  test also compares each group set with the earlier clusters' frozen tables where one exists
  (strategy.members.k1._calendar for equity, k3 fx, k4 energy, k5 metals, k7 crypto; read-only
  imports in the test, never in a member) and reports any difference to the lead.
- strategy/members/k8/_releases.py: GUARD_INSTANTS: dict root -> tuple of sorted UTC instants (epoch
  seconds, int) for MGC, 6C and MNQ: every row of the frozen release calendar dated
  2019-05-01..2026-06-19 whose "products" include the root (K3-L-01, K4-L-01: the table spans both
  windows; Task 1b checks only research-window rows), plus any correction the lead rules in section 7
  after Task 1b. A helper `in_guard(root, t_ns) -> bool` (t in [R, R + 120 s) for some R).

S0.12 trading_windows (D9 coverage on every leg, V16 and C13; interface lines 51-61; E.3-L-17: fixed
intervals measured on every window date; a bar of another trade date is measured on its own date's
intervals). Day offsets are calendar days from d. Intervals are [start, end) of bar opens:

| Member | Leg | Intervals [start, end) CT | Reference |
|---|---|---|---|
| flight | MGC | (08:34, 15:06) | entry bars 08:34..14:54, fills 08:35..14:55, exit bars to 15:04, last fill 15:05 (C lines 299-300, 362-363) |
| flight | MES | (08:29, 14:55) | bars 08:29..14:54 (C lines 297-298) |
| oilcad | 6C | (08:04, 13:41) | entry bars 08:04..13:24, fills 08:05..13:25, exits to the 13:40 fill (C lines 424, 478) |
| oilcad | MCL | (07:59, 13:25) | bars 07:59..13:24 (C lines 422-423, 479) |
| wkndbtc | MNQ | (17:59, 18:01) day -1; (14:58, 15:00) day 0 | Sunday entry bar and fill bar; Monday exit bar and fill bar (C lines 547-548, 597-598) |
| wkndbtc | MBT | (17:59, 18:00) day -1; (14:59, 15:00) day 0 | the Sunday 17:59 bar of d; the Friday 14:59 bar measured on the Friday's own date (C lines 544-546, 599) |

S0.13 Topstep checks common to all (C lines 346-360, 465-476, 581-595): flat by F (last member fill
15:05 flight, 13:40 oilcad, 14:59 wkndbtc; F 15:08); market orders only; D9.3 within limits by rule
(flight 1 entry a day, holds >= 10 min; oilcad <= 17 a day, 15-min holds; wkndbtc 1 a week, 20 h 59 min);
no stops, brackets or passive fills (D9.4); q_c = 1 contract (MGC 0.1 lot-equivalent, 6C 1, MNQ 0.1), at
or below the D9.5 cap; D9.5a per S0.10 and the engine; D9.6-D9.8 as listed per member; D9.12's CPI window
binds no K8 fill (flight's first fill 08:35, oilcad's 6C is not CPI-restricted, wkndbtc fills at 18:00
and 14:59) and q_c = 1 <= 3 on MGC and MNQ.

---

## 1. K8-flight-01 (flight to gold after an extreme negative 5-minute S&P 500 move). C lines 252-371

Two trials, one module: H30 (ordinal 1) and HEOD (ordinal 2) differ only in the exit.

| Field | Rule | Reference |
|---|---|---|
| Exposures, legs | traded gold, MGC (q_c 1); signal S&P 500 on MES bars (no position) | C 253-257; S0.1 |
| Trade dates | d in FLIGHT_DATES (EQUITY and METALS full sessions); roll blackouts of MGC or MES by the engine | C5 114-128; S0.8 |
| Blocks | B_k = [08:30 + 5(k-1), 08:30 + 5k) CT, k = 1..77; decision t_k = 08:30 + 5k, 08:35..14:55 | C 271-272 |
| Block return | r_k = (C_MES(t_k - 1) - C_MES(t_k - 6)) / C_MES(t_k - 6): the closes of the MES bars at t_k - 1 and t_k - 6 (for k = 1 the bars at 08:34 and 08:29), as an exact Fraction of integer vendor ticks (c1 - c6) / c6; both bars present with one instrument_id and c6 > 0, else r_k undefined and no trigger at t_k | C 273-275; S0.9; K8-L-05, K8-L-09, K8-L-10 |
| Reference dates | the 20 most recent FLIGHT_DATES dates strictly before d (roll-blackout dates included; K5-L-05, K4-L-08) | C 277-278; K8-L-04 |
| Reference values | every defined r_k (k = 1..77) on those dates, each with its own two bars present and one instrument_id; n = their count | C 277-278; K8-L-04 |
| Warm-up | no trade on d while any of the 20 reference dates precedes the trade date of the first bar the member received in the run (the first 20 eligible dates of the window) | C5 126-127; K4-L-09 |
| Threshold | n >= 1,200, else no trade on d; Q(d) = the m-th smallest reference value (duplicates counted), m = ceil(0.005 n) = (n + 199) // 200 (m = 8 at n = 1,540); fixed before d's 08:30 | C 279-281; K8-L-09 |
| Trigger at t_k | r_k <= Q(d) and r_k < 0 (exact) | C 282 |
| Entry | at the FIRST trigger of d that C6 does not skip: BUY q_c MGC, market intent on the MGC bar at t_k - 1 (the view at minute t_k - 1, decision time t_k), filling at the open of the MGC bar at t_k; at most one entry per d | C 283-286; S0.6 |
| C6 | a trigger whose fill minute t_k is in a guarded interval of MGC (S0.10: 13:00 on FOMC dates) is skipped and does NOT use the day's entry; the member keeps watching later blocks | C 284-286; K8-L-08 |
| Entry bar missing | if the MGC bar at t_k - 1 of the first (non-skipped) trigger is missing: no entry, and no trade on d (C5's "the entry bar is missing"; E.3-L-04) | C5 119; K8-L-06 |
| Engine refusal | the first non-skipped trigger uses the day's entry even if the engine refuses the intent (roll blackout, D9.7, any refusal) | E.3-L-08 |
| Exit H30 (ordinal 1) | market intent on the MGC bar at min(T_e + 29, 15:04), filling at the open of T_e + 30 or 15:05; if that bar is missing, the first later present MGC bar (S0.7) | C 288-289; S0.7; K8-L-07 |
| Exit HEOD (ordinal 2) | market intent on the MGC bar at 15:04, filling at the 15:05 open; if missing, the first later present bar (the engine's F 15:08 flatten is the backstop) | C 290; S0.7 |
| Hold | H30: 30 min for entries at or before 14:35, down to 10 min at 14:55; HEOD: 10 min (14:55 entry) to 6 h 30 min (08:35) | C 291-293 |
| Session, flatten | 08:35-15:05 CT; last member fill 15:05; F 15:08 (D6 gold row, D line 396) | C 294-295 |
| Bars read | MES close and instrument_id, bars 08:29..14:54 CT on d and on the 20 reference dates; MGC open (by the engine) and bar presence 08:34..15:05 CT | C 297-302 |
| Events read | the MGC guard instants (S0.11 _releases.py), scheduled, known in advance; EC-CAL (equity, metals), known in advance | C 301-302 |
| Order, size | market; q_c of MGC = 1 (D9.5: 0.1 lot-equivalent) | C 303-304 |
| Parameters (literals) | 5-minute blocks; block clock 08:30-14:55; 77 blocks; tail 0.5% (m = ceil(n/200)); 20 reference dates; n >= 1,200; one entry per d; H30 = 30 min (intent at T_e + 29); HEOD intent 15:04; grid {H30, HEOD} | C 306-329 |
| Trials in N | 2 | C 371 |
| Topstep | flat by 15:05 < F 15:08; market only; 1 entry a day, holds >= 10 min; no fill in [13:00, 13:02) on FOMC dates (C6); MGC 1 contract (D9.6); D9.7 gold per C12 (MGC DCB_ONLY: does not fire, engine); MGC* starred (D9.8); D9.11 caps not binding; D9.12 no fill possible before 08:35; early-close dates excluded | C 346-360 |

## 2. K8-oilcad-01 (crude leads the Canadian dollar by one 5-minute step). C lines 373-488

| Field | Rule | Reference |
|---|---|---|
| Exposures, legs | traded CAD, 6C (q_c 1, "undersized", screened as E.3 screened ZT and ZF, E.3-L-20); signal crude on MCL bars (V16(c)) | C 375-378; S0.1 |
| Trade dates | d in OILCAD_DATES (ENERGY and FX full sessions); roll blackouts of 6C or MCL by the engine (V16(a): MCL's monthly blackouts now remove trade dates) | C5 114-128; S0.8 |
| Decision times | T = {08:05, 08:10, ..., 13:25} CT, 65 a day; each covers the block [t - 5, t) | C 401 |
| Block return | r_t = (C_MCL(t - 1) - C_MCL(t - 6)) / C_MCL(t - 6): closes of the MCL bars at t - 1 and t - 6, from integer vendor ticks (c1 - c6) / c6 as a Python float; c6 > 0 (C10 of K4); both bars present with one instrument_id, else r_t undefined | C 402-403; K4-L-05; K8-L-05, K8-L-09 |
| Reference dates | the 20 most recent OILCAD_DATES dates strictly before d (roll-blackout dates included) | C 404-405; K8-L-04 |
| Scale | s(d) = statistics.stdev of every defined r_t (t in T) on those dates (sample standard deviation, n - 1); n >= 1,000 (max 1,300), else no trade on d; s(d) = 0: no trade on d | C 404-406; K8-L-09 |
| Warm-up | as flight (K4-L-09) | C5 126-127 |
| Standardized move | z_t = r_t / s(d) (float) | C 407 |
| Entry | at t in T, if (i) the account is flat on 6C (no position and no pending order, K8-L-11), (ii) |z_t| >= 2.0, (iii) r_t is defined, (iv) the 6C bar at t - 1 is present, and (v) C6 does not skip t: market intent on the 6C bar at t - 1, filling at the open of the 6C bar at t; BUY if z_t > 0, SELL if z_t < 0 (6C quoted in USD per CAD) | C 409-413; S0.6; K8-L-06 |
| Missing bars | per decision time (K4-L-14's ovr reading): an undefined r_t or a missing 6C bar at t - 1 means no entry at t only; later decisions of d proceed | C5 119; K8-L-06 |
| C6 | skip the decision t whose fill minute t is in a guarded interval of 6C (S0.10): 09:30 on a standard WPSR date (its block is pre-release); 09:35 is not skipped; 10:00 or 11:00 on a WPSR date at those CT times; 13:00 on an FOMC date | C 414-416; K8-L-08 |
| Exit | market intent on the 6C bar at T_e + 14, filling at the open of T_e + 15; if missing, the first later present bar (S0.7) | C 417-418; K8-L-07 |
| Spacing | the exit intent at T_e + 14 is emitted on the same view as the decision t_e + 15; at that view the position is open, so no entry; the next possible entry is t_e + 20 (entries at least 20 min apart) | C 446-449 |
| Engine closures | a position closed by the engine leaves the account flat and later decisions of d apply as written | K7-L-07 |
| Hold, session, flatten | 15 minutes; 08:05-13:40 CT; last member fill 13:40; F 15:08 (D6 FX row, D line 394) | C 419-420 |
| Bars read | MCL close and instrument_id, bars 07:59..13:24 CT on d and on the 20 reference dates; 6C bar presence 08:04..13:39 and open (by the engine) 08:05..13:40 | C 422-426 |
| Events read | the 6C guard instants (S0.11): WPSR, NFP, FOMC rows; scheduled, known in advance | C 426-427 |
| Order, size | market; q_c of 6C = 1 (1 lot-equivalent, the cap; "undersized") | C 428-430 |
| Parameters (literals) | 5-minute block, one-step horizon; 65 decision times 08:05-13:25; |z| >= 2.0; 20 reference dates; n >= 1,000; 15-minute hold (intent at T_e + 14); no grid | C 432-449 |
| Trials in N | 1 | C 488 |
| Topstep | flat by 13:40; market only; <= 17 entries a day, 15-min holds, entries >= 20 min apart; q_c = 1 = 1 lot-equivalent; no entry fill in a guarded interval (C6); 6C counts 1 lot (D9.6); D9.7 per C12 (6C DCB_ONLY: does not fire, engine); 6C unstarred; D9.11 and D9.12 name no FX product | C 465-476 |

## 3. K8-wkndbtc-01 (the weekend bitcoin move predicts the Monday Nasdaq-100 trade date). C lines 490-608

| Field | Rule | Reference |
|---|---|---|
| Exposures, legs | traded Nasdaq-100, MNQ (q_c 1); signal bitcoin on MBT bars | C 492-495; S0.1 |
| Trade dates | Monday trade dates only: d with d.weekday() == 0, d in WKNDBTC_DATES (EQUITY and CRYPTO full sessions), and its Friday d - 3 days in WKNDBTC_DATES; roll blackouts of MNQ or MBT on d by the engine | C 526-527, 539-543; S0.8; K8-L-12 |
| Prices | P_F = close of the MBT bar at 14:59 CT on CT date d - 3 (the Friday; trade_date d - 3); P_S = close of the MBT bar at 17:59 CT on CT date d - 1 (the Sunday; trade_date d). Both present with one instrument_id, else no trade on d | C 524-527; K8-L-12 |
| Signal | G = P_S / P_F - 1; sign(G) = sign of (P_S - P_F) in integer vendor ticks (exact); G = 0: no trade | C 528; K8-L-09 |
| Both regimes | the same definition before and after the 24/7 change (2026-05-29 16:00 CT; C3 99-101); MBT bars carry CME's trade date, and from 2026-06-01 the weekend is booked to Monday, so the Sunday 17:59 bar carries trade_date d in both regimes; no bar outside [d-1 17:00, d 16:00) is read for d other than the Friday 14:59 bar of trade date d - 3 | C 529-532; K7-L-01 |
| Entry | on the view at Sunday 17:59 CT (decision 18:00): market intent on the MNQ bar at 17:59 CT on CT date d - 1 (trade_date d), filling at the open of its 18:00 bar; BUY q_c if G > 0, SELL q_c if G < 0; the MNQ entry bar must be present (else no trade on d) | C 533-534; S0.6 |
| C6 | an entry whose fill minute (Sunday 18:00) is in a guarded interval of MNQ is skipped (no research-window row there; implemented uniformly) | C6 130-143; S0.10 |
| Exit | market intent on the MNQ bar at 14:58 CT on d (Monday), filling at the 14:59 open; if missing, the first later present bar (S0.7) | C 535-536 |
| Hold, session, flatten | 20 h 59 min; Sunday 18:00 to Monday 14:59 CT, inside trade date d; F 15:08 (D6 equity row, D line 391) | C 537-538 |
| Exclusions | Monday trade dates that EC-CAL marks as early halt or closure (research window: 2025-05-26, 2025-09-01, 2026-01-19, 2026-02-16, 2026-05-25); Mondays whose preceding Friday is not a full trade date (for example the Mondays after Good Friday) | C 539-543 |
| Bars read | MBT close and instrument_id at Friday 14:59 (available 15:00 Friday) and Sunday 17:59 (available 18:00 Sunday); MNQ presence at Sunday 17:59, open (by the engine) at Sunday 18:00 and Monday 14:59 | C 544-548 |
| Events read | the MNQ guard instants (S0.11); EC-CAL (equity, crypto) | C 549 |
| Order, size | market; q_c of MNQ = 1 (0.1 lot-equivalent) | C 550-551 |
| Parameters (literals) | P_F at Friday 14:59; P_S at Sunday 17:59; entry fill 18:00; exit intent 14:58, fill 14:59; symmetric sign; no grid | C 553-568 |
| Trials in N | 1 | C 608 |
| Label | source-overlap (labels matter only for confirmation) | C 604-607 |
| Topstep | flat by 14:59 < F 15:08; opens after the Sunday 17:00 open, inside one trade date; market only; 1 entry a week; the entry is 60 min after the reopen (D9.4); q_c <= 1 lot-equivalent; no fill in a guarded interval; MNQ 1 contract (D9.6); D9.7 equity limits by the engine (entry blocked and exit forced beyond the stop level); MNQ* starred (D9.8, referent D9.12); D9.12 no opening fill in a CPI window; D9.11 names no equity product | C 581-595 |

## 4. Trial count

| Ordinal | Trial | Traded | Signal | eps (operative) | Trials in N |
|---|---|---|---|---|---|
| 1 | K8-flight-01 H30 MGC | MGC | MES | 71 | 1 |
| 2 | K8-flight-01 HEOD MGC | MGC | MES | 71 | 1 |
| 3 | K8-oilcad-01 6C | 6C | MCL | 9 | 1 |
| 4 | K8-wkndbtc-01 MNQ | MNQ | MBT | 170 | 1 |
| | Total | | | | 4 (C banner lines 3-7; C section 5 lines 833-836) |

K8-ml-01 is excluded (U6), 0 trials. The count is taken from the freeze declarations (4) and the N rule
is K1-L-16 (K8-L-16).

## 5. What the tests must pin (Task 2; the prompt's list, per member)

Entry and exit times; the event window (C6 skip at the guarded fill minute, and not at the next decision);
the flatten (no fill after 15:05 flight, 13:40 oilcad, 14:59 wkndbtc; the engine's F as backstop); a
missing bar at a decision time; a signal bar from the other leg arriving late or missing (no trade, no
forward fill: a signal-leg bar absent at its minute and present one minute later must not be used);
a roll date on the signal leg only (an instrument_id change between the two signal bars of one
computation: no trade from it; the engine's union blackout is the runner's and is tested in
tests/test_stage_e_alignment.py, not re-implemented); a guarded entry skipped under C6; the Friday and
Sunday clock points (wkndbtc reads exactly the Friday 14:59 and Sunday 17:59 MBT bars, not 15:00 or
17:58 or Saturday bars after the 24/7 change); flight's threshold (n < 1,200, m = ceil(n/200), duplicates,
r_k < 0), first-trigger-only, H30 vs HEOD exit choice; oilcad's |z| >= 2.0 boundary, the s(d) ddof,
n < 1,000, spacing, pending-exit block, sign; wkndbtc's G = 0, Good-Friday and holiday-Monday exclusions.
Every pinned rule must fail on a mutant (E.4 K5 and K3 lessons).

## 6. Lead readings (each is also an open choice in reports/E.9_RETURN.md section 6)

- **K8-L-01 Declarations, labels and leg order.** 4 declarations (S0.2), labels "<member> [grid]
  <traded root>", ordinals in catalog order (C section 5). The traded leg is declared first (the
  template's primary-leg rule), then the signal leg. The ordinal seeds the confirmation power check
  (E.3-L-18); fixed here, before any result.
- **K8-L-02 Bars by CT date and clock, per leg** (E.3-L-03, K7-L-01). Each leg's bar is selected by its
  own CT open and CT date; trade_date is checked to equal the trade date the rule names. For MBT this
  matters after 2026-06-01, when CME books weekend bars to Monday.
- **K8-L-03 C5's calendar exclusion uses every leg's own group calendar.** "Any leg's D10 group
  calendar" (C line 118) is read as: d must be a full session in each leg's group; "equity-and-crypto"
  is read as both the equity calendar (MES, MNQ) and the crypto calendar (MBT), since the program keeps
  two calendars (data/calendars/equity.py, crypto.py): the narrowest reading. Full session as K3-L-11
  and K7-L-02 (no early halt and the regular engine F, 15:08). Tables span 2019-05-01..2026-06-19
  (K4-L-13).
- **K8-L-04 "The 20 most recent earlier eligible dates of the same window" = the member's full-session
  dates, roll-blackout dates included.** As K5-L-05 and K4-L-08: C5's date-level exclusions a member can
  apply are the calendar ones; its roll-blackout clause is met by the runner (the member cannot read a
  roll calendar), and the missing-bar clause is per computation, handled by the entries' own value
  floors (n >= 1,200; n >= 1,000). Warm-up as K4-L-09. A reference date on which the SIGNAL leg has no
  bars at all contributes no values; the traded leg's bars play no part in a reference value (the values
  are defined by the signal leg's two bars only, C lines 273-275, 402-403; wording clarified by R-T3-1).
- **K8-L-05 Signal computations are guarded per computation, within the signal leg.** C4 (lines 110-111)
  and the entries (C lines 274-275, 403): both bars present, one instrument_id. A signal-leg roll inside
  a computation makes it undefined; the date itself is removed only if it is a roll-blackout date (the
  engine, V16(a)).
- **K8-L-06 Missing entry bar.** flight: the first non-skipped trigger whose MGC entry bar is missing
  ends the day (no trade on d): C5 line 119 excludes dates on which "the entry bar" is missing, and the
  first trigger is the day's one event (E.3-L-08's analogue); narrowest. oilcad: per decision time, as
  K4-L-14 read ovr (a multi-decision member): no entry at that t, later decisions proceed. wkndbtc: no
  trade on d (one decision a week).
- **K8-L-07 T_e is the actual fill minute** ("T_e is the entry fill minute", C lines 288, 418): the CT
  open of the traded-leg bar at which the account first shows the position. It equals t_k (t) unless
  the bar at t_k is missing and the engine fills later.
- **K8-L-08 C6's guarded intervals are the engine's D9.5a set for the traded root.** C6's first sentence
  defines the skip by "a D9.5a guarded interval [release, release + 2 min) of the traded product"; the
  frozen release calendar is D9.5a's input (D8: "Topstep F6.4 plus the releases the product's catalog
  members name"). C6's table (C lines 139-143) lists the releases that meet K8's fill minutes; the
  calendar's other rows for these roots (MGC G17 08:15 CT; MNQ ISM_SERVICES 09:00 CT; the NFP/CPI 07:30
  rows) can never equal a K8 entry fill minute, so the two readings give identical decisions on every
  date. Using the engine's set guarantees "skipped, not deferred" for every entry. The skip tests the
  scheduled fill minute t; a fill pushed past t by a missing traded-leg bar into a guard is deferred by
  the engine (D9.5a), not skipped: the member cannot know at its decision that the bar at t will be
  missing (an edge case, logged). A skipped flight trigger does not use the day's entry (C lines
  284-286).
- **K8-L-09 Arithmetic.** flight: r_k as an exact Fraction of integer ticks; the order statistic and the
  trigger compare exactly (E.3-L-19, K4-L-05's exact-compare rule); m = ceil(0.005 n) computed as
  (n + 199) // 200. oilcad: K4-L-05's statistic route (a sample standard deviation needs a square root):
  r_t as a float from integer ticks, s(d) = statistics.stdev (exact internal sums, ddof 1), z = r_t / s(d)
  in float, |z| >= 2.0 compared in float (equality has probability zero and is reported if it occurs);
  the side is the sign of the integer tick difference. wkndbtc: sign of the integer tick difference.
- **K8-L-10 Non-positive denominators.** oilcad requires c6 > 0 (C line 403, K4's C10). flight's text
  names no such condition; c6 > 0 is required only to avoid a division by zero (an MES close is never
  0); it cannot change a decision on real bars.
- **K8-L-11 oilcad's "no open position; no exit of its own is pending at t"** is read as account.is_flat()
  for 6C: no position and no pending order of either side (a pending entry is also not "flat"); narrowest.
- **K8-L-12 wkndbtc's dates and bars.** d is a Monday trade date (weekday 0); "the Friday immediately
  before" is the calendar date d - 3, which must be a full session in both calendars (C 527, 541-543;
  K8-L-03); P_F is the MBT bar at 14:59 on CT date d - 3 with trade_date d - 3; P_S is the MBT bar at
  17:59 on CT date d - 1 with trade_date d; the MNQ entry bar is MNQ's 17:59 bar on CT date d - 1 with
  trade_date d. One instrument_id across P_F and P_S (C 526). If d - 3's MBT bar is a roll-blackout date
  of MBT but d is not, the engine allows the trade and the instrument_id test covers the contract change
  (V16(a) removes trade dates, and d is the trade date).
- **K8-L-13 trading_windows** as S0.12 (E.3-L-17; E.8's pattern: entry decision bars, fill bars and
  signal bars). wkndbtc's Friday bar is measured on each date's own 14:59 (offset 0), so it is measured
  on every window date, Fridays included.
- **K8-L-14 Tables span 2019-05-01..2026-06-19** (K3-L-01, K4-L-01): the frozen code serves the
  confirmation window; Task 1b checks the research-window rows only.
- **K8-L-15 C section 6 settled by V16 and the frozen text.** Items 1-4 by V16: (1) every leg at its own
  S (confirmation only); (2) MBT's short history: the start rule's, later (BTC only under D4's power
  clause and the user's agreement); (3) union of roll blackouts (the engine; V16(a)); (4) every leg's D9
  coverage (the runner, on S0.12's intervals). (5) WPSR concerns 6C: the frozen release calendar
  (E.2b) lists 6C under WPSR, so the engine guards and costs 6C fills at WPSR and C6 skips them;
  program-wide as built (K3's 6C trials were screened under the same calendar). (6) C6's skip: as
  written (S0.10). (7) FOMC-surprise routings: not members, nothing coded. (8) F09 ownership: no member
  effect. (9) Nasdaq-100 only, symmetric sign: as frozen. (10) no action. (11) the 24/7 regime: recorded
  for the user in the return with Task 1b's counts on each side. (12) judgment parameters: as frozen
  literals.
- **K8-L-16 The N rule** (K1-L-16, pre-declared before any run): a trial counts when the runner writes
  its screen record (status "run"); a trial the runner excludes before screening (coverage) or refuses
  does not count.
- **K8-L-17 Two coders** (the prompt): MemberCoder-A writes _calendar.py, _releases.py and the generator
  first, then flight.py, tests/test_k8_members_tables.py and tests/test_k8_members_flight.py;
  MemberCoder-B writes oilcad.py and wkndbtc.py, tests/test_k8_members_oilcad.py and
  tests/test_k8_members_wkndbtc.py, importing A's tables. strategy/members/k8/__init__.py is created
  empty by the lead.

## 7. The research-window check and the rulings (lead, 22:33 PDT, after Task 1b)

Task 1b (ReleaseChecker-OpusMed, 22:21-22:32): reports/stage_e9_release_check.md and .json, 48 pages under
reports/stage_e9_briefs/pages/. A1: row counts per traded root as the header states. A2: NFP 14, FOMC 10,
G17 14, ISM_SERVICES 15 keep (fresh official pages); CPI 14 keep (E.7's check); WPSR 62 keep, 2 drop (E.4's
verdicts: WPSR-2025-12-29 17:00 ET and WPSR-2026-05-28 12:00 ET, actual publication differed). A3: FOMC
13:00 CT on the flight and oilcad entry grids (10 dates each); WPSR 09:30 CT (56) and 11:00 CT (7) on the
oilcad grid; nothing on a wkndbtc fill minute. A4: no scheduled release missing. B: 63 Mondays, 9 excluded
(Fridays 2025-04-18, 2025-07-04, 2025-11-28, 2026-04-03 not full; Mondays 2025-05-26, 2025-09-01,
2026-01-19, 2026-02-16, 2026-05-25 not full, each booked forward in crypto), 54 eligible. C: the 24/7 change
2026-05-29 16:00 CT (CME release 19 Feb 2026, quoted); 51 eligible Mondays before, 3 after (2026-06-01,
06-08, 06-15). D: roll blackouts MGC 18, MCL 45, 6C 15, MBT 42, MNQ 15 (earlier frozen runner records);
MES unverifiable from the named sources. F: no external series.

Lead's own count (22:32 PDT, data.group_session + rules.sessions, the S0.8 definition): research-window
full sessions equity 303, crypto 304, metals 304, energy 304, fx 304; FLIGHT_DATES 303, OILCAD_DATES 304,
WKNDBTC_DATES 303; wkndbtc Mondays with d and d - 3 both in WKNDBTC_DATES: 54. Coder A's table test pins
these.

- **R-1b-1 The C6 skip set is the frozen calendar's rows, unchanged; no correction.** The two WPSR rows E.4
  dropped stay in GUARD_INSTANTS["6C"]. C6 skips an entry whose fill would land in "a D9.5a guarded
  interval", and the engine's D9.5a set is the frozen calendar, which still holds both rows: skipping
  there is what keeps the entry from being deferred (C6's purpose); a member that did not skip at 11:00
  CT on 2026-05-28 would have its fill deferred to 11:02, which C6 forbids. E.4 removed the rows from K4's
  event members because those members TRADE on the release; C6 is a guard. The actual (delayed) times are
  not added: D9.5a concerns scheduled releases known in advance, and a delayed time is known only after
  the fact (hindsight). WPSR-2025-12-29 (16:00 CT) meets no K8 fill minute. Effect: oilcad does not enter
  at 11:00 CT on 2026-05-28 (one decision time of one date).
- **R-1b-2 MES's research-window roll-blackout dates are the runner's.** They are computed by the frozen
  harness from the bars at run time (member_window) and written into each flight record
  (window_dates.excluded.roll_blackout_any_leg); Task 7 reads them there. They are not a member input,
  so flight carries no "calendar partly unverified" label for them; the return states that the pre-run
  check could not list them. The vendor rolls file spanning holdout-1 stays unopened.
- **R-1b-3 2026-06-01 is a crypto full session.** Its delayed start (opened Friday 2026-05-29 16:30 CT
  after extended maintenance) is a late open, not an early close, early halt or closure (C5 line 118;
  K6 S0.8: "A grain late open ... is not an early close"; K7-L-02's definition). Moot for trading: it is
  an MBT roll-blackout date.
- **R-1b-4 Unscheduled items are not added.** The 2025-08-22 FOMC notation vote (not a policy statement,
  no time) and the 2025-11-24 G.17 annual revision (no time; the calendar's known gap) are outside the
  frozen calendar and outside D9.5a's scheduled releases; members read the frozen calendar only.
- **R-1b-5 Expected trade counts (calendar arithmetic, no data):** wkndbtc at most 54 Mondays, of which
  14 fall in MBT/MNQ roll blackouts or UR-1 (1b section D), so at most 40 trades; flight at most one a
  day on FLIGHT_DATES less the union (MGC 18, MES at run time, UR-1); oilcad up to 17 a day on
  OILCAD_DATES less 60 union dates. The power check is not run here.
- **R-1b-6 The 24/7 regime (C section 6 item 11), for the user:** research window 51 eligible Mondays
  before the change and 3 after; the confirmation window lies wholly before it. Recorded in the return.
