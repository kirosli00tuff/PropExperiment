# Stage E.8 member specifications, cluster K6 grains, oilseeds and livestock (Task 1)

Written by the Stage E.8 lead (Opus 5.5, xhigh), 2026-10-01 00:00-00:19 PDT, before any K6 member code
exists and before any K6 bar has been read by this session. It restates each frozen entry as the code
must implement it, with line references, and records every reading the lead took where the entry leaves
a detail open (section 9). It changes no rule. A reading is the narrowest one the text allows unless the
text fixes the detail (then the text governs). Where K6's text is the same as an earlier cluster's, the
earlier reading is adopted and cited (E.3-L-nn: reports/stage_e3_member_specs.md section 10; K4-L-nn:
reports/stage_e4_member_specs.md section 10; K3-L-nn: reports/stage_e4c_member_specs.md section 10;
K7-L-nn: reports/stage_e6_member_specs.md section 8; K1-L-nn: reports/stage_e7_member_specs.md
section 8).

Sources and their state:
- C = reports/stage_e0_catalog_K6.md, frozen by reports/stage_e1_freeze.json (manifest 96166eb3...).
  Line numbers below are this file's. Banner lines 3-7 (E.1: U6; 7 active members, 27 trials); header
  table lines 57-65; conventions C1-C13 lines 67-231; members lines 235-743; section 6 lines 1057-1070;
  section 7 lines 1074-1164. Lead banners: R-03 line 237 (CP1 livestock = the (b) form), crushgap ZS
  only line 382, limitcont HE and LE only line 498, R-04 and R-10 on wasdepre line 598, R-10 on C13 line
  214. E.1 edits to K6 (reports/stage_e1_changes.md K6-00..K6-03) touch only the banner, the excluded
  K6-ml-01 and the ML rows of sections 0 and 6. No active member's rule changed. K6-ovr-01 is excluded
  by the E.0 lead (section 6, 0 trials); K6-ml-01 is excluded (U6). Neither is coded.
- Section 7 "as amended": the E.0 lead's 01:52 rulings on K6's questions (reports/stage_e0_STATE.md line
  70) as written into the frozen design: item 2 (settlements: Databento statistics schema or the
  settlement-window VWAP proxy; D9.7), item 3 (the D9.7 exit is exempt from the fill guard; D9.7), item 4
  (2 percentage points of price inside the limit; D9.7), item 5 (an entry whose earliest exit is less
  than 2 full minutes after its fill is skipped; D9.3), items 1, 6, 7 (the banners above, R-03). Section
  9 K6-L-16 settles each item.
- D = docs/STAGE_E_DESIGN.md (frozen): D5 lines 298-312; D6 port texts lines 364-366, the "4 ticks of P"
  paragraph lines 368-372, the grains row (O 08:30, C 13:15, F 13:18) and livestock row (O 08:30, C
  13:00, F 13:03) of the session table lines 400-401; D9.3 line 497-503; D9.7 lines 531-551 (the proxy:
  line 542).
- Vehicles (reports/stage_e2a_vehicles.md lines 38-44; frozen via
  screening.stage_e_frozen.load_frozen_tables): ZC q_c 1 "undersized" (rho 0.4385 < 0.5); ZW, ZS, ZM,
  ZL, HE, LE q_c 1 "chosen". Operative eps (reports/stage_e2a_epsilon.md lines 28-34): ZC 4, ZW 4, ZS
  5, ZM 5, ZL 11, HE 7, LE 11 net ticks per contract per day.
- Frozen per-root values (checked by the lead 00:00-00:13 PDT through load_frozen_tables() and rules.products.product):
  day_session_ct = (08:30, 13:15) for ZC, ZW, ZS, ZM, ZL and (08:30, 13:00) for HE, LE. vendor_tick and
  vendor_price_factor: ZC, ZW, ZS 0.25 / 100 (cents per bushel); ZM 0.10 / 1 (USD per short ton); ZL
  0.01 / 100 (cents per pound); HE, LE 0.025 / 100 (cents per pound). E.2a found 0 off-tick raw prices
  and confirmed the cents quoting for every K6 product (reports/stage_e2a_bars.md line 13 and the
  per-product lines 634-744). F (rules/sessions.py, enforced by the engine) = 13:18 CT grains, 13:03 CT
  livestock on a regular day.
- EC-CAL = the D10 grain and livestock calendars, data/calendars/grains.py and livestock.py, read through
  data.group_session.load_group_calendar("grains" / "livestock") and rules.sessions.default_holidays().
  Research window (checked by the lead 00:00-00:13 PDT): full closures (both groups) 2025-04-18, 05-26, 06-19, 07-04, 09-01,
  11-27, 12-25, 2026-01-01, 01-19, 02-16, 04-03, 05-25, 06-19; early halts 2025-11-28 (grains 12:05,
  livestock 12:05) and 2025-12-24 (grains 12:05, livestock 12:15); grain late opens with no evening
  session (scheduled_late_opens, open 08:30) 2025-11-28, 2025-12-26, 2026-01-02; livestock none. Task 1b
  item C checks these dates.
- Release calendar reports/stage_e2b_release_calendar.json (frozen, sha256 839f2437...; loaded by the
  runner): 14 research-window WASDE rows (2025-04-10, 05-12, 06-12, 07-11, 08-12, 09-12, 11-14, 12-09,
  2026-01-12, 02-10, 03-10, 04-09, 05-12, 06-11), each 12:00 America/New_York, products HE, LE, ZC, ZL,
  ZM, ZS, ZW. No October 2025 row (cancelled). The engine's D9.5a guard and D8's event-window cost read
  every row whose products include the root (WASDE, CROP, CROP_ANNUAL, CROP_PROGRESS, FOMC; Task 1b item
  D counts them). Only the two WASDE members read a release, and only its date.
- EC-LIM = rules/price_limits.py LIMITS (HARD_DAILY periods for all seven roots; initial limits only,
  flag R-L2) and the D9.7 settlement proxy (settlement_window_ct, settlement_proxy; grains window
  [13:14:00, 13:15:00) CT, livestock [12:59:30, 13:00:00) CT; an early halt moves the window to end at
  the halt). Research-window periods: HE 0.0400 to 2025-08-29 (sourced), 0.0400 2025-08-30..09-01
  (bracketed), 0.0475 from 2025-09-02 (sourced); LE 0.0650 to 2025-06-01 (sourced), 0.0725 2025-06-02..
  2026-05-18 (sourced), 0.0725 2026-05-19..06-19 (bracketed). Only K6-limitcont-01 reads it as a member;
  the engine reads it for D9.7 on every K6 trial.
- External series: none. No K6 member reads a price series from outside the bars.
- Source-window labels (reports/stage_e2a_source_window_amendment.md lines 67-72; wasdepre by R-04, C
  line 598): every K6 member is source-overlap. Labels matter only for confirmation.

What the member does NOT implement (the engine and runner do; a member must not duplicate or
second-guess them; same list as E.3, E.4, E.6 and E.7): the window's trade dates and the removal of
roll-blackout dates (the engine refuses opens there by name, `engine_roll_blackout`; for a member with
signal legs, the union over every leg it reads, D4); 2026-06-18/19 (UR-1); F and the forced flatten
(D9.1); costs and the event-window cost (D8: fills in [11:00, 11:30) on USDA release dates and [13:00,
13:30) on FOMC dates pay the largest bucket); the event-minute fill guard (D9.5a: a fill that would land
in [release, release + 2 min) moves to the first bar at or after release + 2 min); the entry cap and the
2-minute minimum hold (D9.3a/b) as refusals; the skip of an entry whose earliest exit would come less
than 2 full minutes after its fill (D9.3, ruling 01:52 on section 7 item 5); the refusal of an open when
any leg the member reads has no bar at that minute (D11.5); price-limit proximity, its entry refusal and
its forced exit, exempt from the fill guard, and the locked-market exit rule (D9.7, R-08;
rules/price_limits.py, settlements by the proxy); the lot-equivalent cap (D9.5).

---

## 0. Common to all seven members

S0.1 Legs. Every declaration trades exactly one leg, `LegSpec(root, True)`, the exposure's single
admissible full-size contract (C header line 59: no Topstep-permitted K6 micro). K6-crushgap-01 also
reads ZM and ZL as signal legs, `LegSpec("ZM", False)` and `LegSpec("ZL", False)`, after the traded ZS
(C lines 382-386; the template's rule that the first traded leg is the primary leg). No other member
reads a second leg.

S0.2 Declarations. 27 `MemberDecl`s, label `"<member id> <root>"` (for example `"K6-cp1-01 ZC"`); the
member object's `name` equals its label. One module per member under strategy/members/k6/;
zero-argument factories `make_zc`, `make_zw`, `make_zs`, `make_zm`, `make_zl`, `make_he`, `make_le`,
only those the member trades. Ordinals in catalog order, then ZC, ZW, ZS, ZM, ZL, HE, LE (K6-L-14):

| Ordinal | Label | Module | Factory | Legs | q_c |
|---|---|---|---|---|---|
| 1 | K6-cp1-01 ZC | strategy.members.k6.cp1 | make_zc | ZC | 1 |
| 2 | K6-cp1-01 ZW | strategy.members.k6.cp1 | make_zw | ZW | 1 |
| 3 | K6-cp1-01 ZS | strategy.members.k6.cp1 | make_zs | ZS | 1 |
| 4 | K6-cp1-01 ZM | strategy.members.k6.cp1 | make_zm | ZM | 1 |
| 5 | K6-cp1-01 ZL | strategy.members.k6.cp1 | make_zl | ZL | 1 |
| 6 | K6-cp1-01 HE | strategy.members.k6.cp1 | make_he | HE | 1 |
| 7 | K6-cp1-01 LE | strategy.members.k6.cp1 | make_le | LE | 1 |
| 8 | K6-cp2-01 ZC | strategy.members.k6.cp2 | make_zc | ZC | 1 |
| 9 | K6-cp2-01 ZW | strategy.members.k6.cp2 | make_zw | ZW | 1 |
| 10 | K6-cp2-01 ZS | strategy.members.k6.cp2 | make_zs | ZS | 1 |
| 11 | K6-cp2-01 ZM | strategy.members.k6.cp2 | make_zm | ZM | 1 |
| 12 | K6-cp2-01 ZL | strategy.members.k6.cp2 | make_zl | ZL | 1 |
| 13 | K6-cp2-01 HE | strategy.members.k6.cp2 | make_he | HE | 1 |
| 14 | K6-cp2-01 LE | strategy.members.k6.cp2 | make_le | LE | 1 |
| 15 | K6-cp3-01 ZC | strategy.members.k6.cp3 | make_zc | ZC | 1 |
| 16 | K6-cp3-01 ZW | strategy.members.k6.cp3 | make_zw | ZW | 1 |
| 17 | K6-cp3-01 ZS | strategy.members.k6.cp3 | make_zs | ZS | 1 |
| 18 | K6-cp3-01 ZM | strategy.members.k6.cp3 | make_zm | ZM | 1 |
| 19 | K6-cp3-01 ZL | strategy.members.k6.cp3 | make_zl | ZL | 1 |
| 20 | K6-cp3-01 HE | strategy.members.k6.cp3 | make_he | HE | 1 |
| 21 | K6-cp3-01 LE | strategy.members.k6.cp3 | make_le | LE | 1 |
| 22 | K6-crushgap-01 ZS | strategy.members.k6.crushgap | make_zs | ZS (traded), ZM, ZL (signal) | 1 |
| 23 | K6-limitcont-01 HE | strategy.members.k6.limitcont | make_he | HE | 1 |
| 24 | K6-limitcont-01 LE | strategy.members.k6.limitcont | make_le | LE | 1 |
| 25 | K6-wasdepre-01 ZC | strategy.members.k6.wasdepre | make_zc | ZC | 1 |
| 26 | K6-wasdepre-01 ZS | strategy.members.k6.wasdepre | make_zs | ZS | 1 |
| 27 | K6-wasdepost-01 ZC | strategy.members.k6.wasdepost | make_zc | ZC | 1 |

S0.3 Size. Every entry is `q_c` contracts, read from `load_frozen_tables().vehicles[root].q_c` (1 for
every K6 root), never a literal (C6 lines 105-108). Every exit closes the whole position. No member
sizes by signal, holds two legs or reverses. At most one position and one entry per trade date.

S0.4 Clock and the trade date. America/Chicago. "The bar at hh:mm" of trade date d is the bar with
`trade_date == d` whose open (`ts_event_ns`) is hh:mm:00 CT on CT calendar date d (C1 lines 69-71;
E.3-L-03). The only bars on another CT date that any member reads are grain CP1's first bar (19:00 CT
on the calendar day before d, K6-L-01) and the d-1 / d-2 / d-3 bars that crushgap and limitcont read
by their own trade date (sections 4 and 5). C3 (lines 78-87): trade date d = [d-1 17:00 CT, d 16:00
CT); grains open with the 19:00 CT evening session before d and close 13:20 CT on d, with the 07:45-
08:30 pause; livestock is the 08:30-13:05 day session only. O and C come from
`load_frozen_tables().day_session_ct[root]` (grains (08:30, 13:15), livestock (08:30, 13:00); D lines
400-401). A bar is usable at its close (C1 line 71); `on_minute` is called at each grid minute's close
with the bar in `view.bars[root]`, or None. A member's grid may skip minutes with no bar, so a missing
bar is detected by clock (the bar's CT open), never assumed from the call sequence. Bars are identified
by CT date and clock (K7-L-01); a bar of trade date d always carries `trade_date == d`.

S0.5 Orders. Market intents only (`leg_market_intent`), filled by the engine at the open of a later bar
(C2 lines 75-77). No limit orders, stops or brackets.

S0.6 Named entry bar. "Market intent on the bar at X" for an entry is emitted only when the view's bar
is the bar at X. If that bar is missing, there is no entry at X (E.3-L-04). An entry is emitted at most
once per trade date, and never while a position or a pending order exists on the leg. The first
qualifying decision uses the day's entry even if the engine refuses the intent (E.3-L-08).

S0.7 Exits and flattens. Every exit is sent on the first present bar of the traded leg at or after the
named bar, while the position is non-zero and no exit order is pending (C4 lines 96-98: "If an exit's
named bar is missing, the exit is sent on the first later bar, with the engine's forced flatten at F as
the backstop"). A refused exit is sent again on the next present bar under the same condition
(E.3-L-22). If the engine closes the position itself (D9.7's forced exit, the flatten, an MLL
liquidation), the member sees a flat account and sends no exit, and makes no further entry that trade
date. A position that exists at the named exit bar is closed there however it arose. CP2's exit is its
own (section 2).

S0.8 Trade-date exclusions of the four new members (C4 lines 88-98; the ports follow D6). crushgap,
limitcont, wasdepre and wasdepost enter only on a trade date d in the group's full-session set
(K6-L-10): GRAIN_FULL_SESSIONS (EC-CAL grain trade dates with no early halt and the regular engine F,
13:18 CT, on CT date d for all five grain roots) or LIVESTOCK_FULL_SESSIONS (livestock trade dates with
no early halt and F = 13:03 CT for HE and LE), coverage 2019-05-01..2026-06-19 (EC-CAL's coverage,
K4-L-13; K3-L-11). A grain late open (no evening session) is not an early close. Roll-blackout dates are
the engine's (D4, every leg read). K6's C4 names no vendor-degraded exclusion (K7-L-03 not adopted).

S0.9 Instrument guard and missing bars of the new members (C4 lines 93-95). "A bar the rule reads" is a
bar read at or before the entry decision (E.3-L-12); "the entry bar" is the bar the entry intent is
emitted on (E.3-L-13). Every such bar of one computation must be present and carry one instrument_id;
otherwise no trade on d. Each member's own list is in its section. Exit and flatten bars are not
guarded. For crushgap the guard is per leg (the three legs are different products).

S0.10 Prices. Every price comparison and sign is computed in integer vendor ticks,
`round(price / vendor_tick)` with `rules.products.product(root).vendor_tick`, never a literal tick
(E.3-L-19). Ratios, thresholds and sums are compared exactly (integers, Fraction or Decimal; K4-L-05),
never with floats: CP3's CLV, crushgap's GPM (K6-L-03), limitcont's equalities (K6-L-08).

S0.11 Tables (a member cannot read a file and cannot import rules.price_limits, data.* or the release
calendar: template lines 9-21; E.3-L-01). Literal tables in the cluster package, generated by a script
under reports/stage_e8_briefs/ (gen_k6_tables.py) from the named sources, each module recording the
sources' sha256, and pinned by tests that recompute them from those sources (tests may import rules.*,
data.*). Coder B writes them, _calendar.py FIRST (coder A's crushgap imports it):
- strategy/members/k6/_calendar.py:
  - GRAIN_TRADE_DATES, LIVESTOCK_TRADE_DATES: tuple[date, ...], sorted, every EC-CAL trade date of the
    group 2019-05-01..2026-06-19;
  - GRAIN_FULL_SESSIONS, LIVESTOCK_FULL_SESSIONS: frozenset[date] (S0.8), with a comment naming any date
    where the early-halt test and the F test disagree, and a check (in the generator and the test) that
    every root of the group gives the same F on every date;
  - LIVESTOCK_EARLY_HALT_CT: dict[date, time], the livestock early-halt time of every early-halt trade
    date in the coverage (for limitcont's settlement window, K6-L-06);
  - `previous_trade_date(dates, d) -> date | None`: the latest element of `dates` before d.
- strategy/members/k6/_wasde.py: WASDE_DATES, frozenset[date]: the CT dates of every row of the frozen
  release calendar with release "WASDE" and local time 12:00 America/New_York, 2019-05-01..2026-06-19
  (K4-L-01: the table spans both windows; only research-window rows are checked, by Task 1b), less
  DROPPED_WASDE (each with its reason, from Task 1b's verdicts, section 10). A row at another time is
  left out, not re-timed (E.3-L-15), and listed.
- strategy/members/k6/_limits.py: LIMIT_PERIODS: dict root -> tuple of (first date, last date, amount as
  an exact decimal string in USD per pound) for HE and LE, every HARD_DAILY period of
  rules.price_limits.LIMITS intersecting 2019-05-01..2026-06-19, with its status (sourced / bracketed /
  carried) as a comment; SETTLEMENT_WINDOW_LIVESTOCK = (time(12, 59, 30), time(13, 0)) from
  rules.price_limits.SETTLEMENT_WINDOW_CT["livestock"]. The member converts an amount to vendor ticks as
  amount x vendor_price_factor / vendor_tick, which must be an integer (HE 0.0400 -> 160, 0.0475 -> 190;
  LE 0.0650 -> 260, 0.0725 -> 290); the table test pins every period's tick count and its equality with
  `rules.price_limits.limit_period(root, d)` on every livestock trade date of the coverage.

S0.12 trading_windows (D9 coverage; interface lines 51-61; E.3-L-17: fixed intervals measured on every
research date; a bar of an earlier trade date that a rule reads is measured on that date's own
intervals, as K1's vxnband). Day offsets are calendar days from d:

| Member | Leg | Intervals [start, end) CT | Reference |
|---|---|---|---|
| CP1 grains | own | (19:00, 19:01) on day -1; (08:59, 09:00); (12:44, 13:15) | first bar, signal bar, entry bar to the 13:14 exit fill bar (E.4/E.7 CP1 pattern) |
| CP1 livestock | own | (08:30, 08:31); (08:59, 09:00); (12:29, 13:00) | first bar 08:30, signal bar, entry bar to the 12:59 exit fill bar |
| CP2 | own | (08:30, 13:18) grains; (08:30, 13:03) livestock | [O, F) (E.4, E.7 pattern; interface example) |
| CP3 | own | (08:30, 13:15) grains; (08:30, 13:00) livestock | [O, C) |
| crushgap | ZS | (08:30, 13:15) | entry 08:30 to the 13:14 exit fill bar; the 13:14 bar of d-1 on d-1's own date |
| crushgap | ZM, ZL | (08:30, 08:31); (13:14, 13:15) | the 08:30 bar of d and the 13:14 bar (measured on d-1's own date) |
| limitcont | own | (08:30, 13:00) | the 08:30 bar, the 08:44 entry bar, the 12:59 exit fill bar and settlement bar |
| wasdepre | own | (08:30, 08:31); (10:29, 11:16) | signal bars, entry bar 10:29 to the 11:15 exit fill bar |
| wasdepost | own | (10:59, 13:15) | signal bars 10:59 and 11:14, entry, to the 13:14 exit fill bar |

S0.13 Topstep checks common to all (each entry's list: C lines 273-283, 319-331, 364-375, 479-491,
579-591, 663-677, 728-741): flat by F (last member fill 13:14 grains or 12:59 livestock, CP2 by the
engine's flatten at F at the latest); market orders only; one entry a day; holds of at least 29 minutes
by rule (CP2's shortest hold is cut by F, and D9.3's skip is the engine's); no stops, brackets or passive
fills (D9.4); no K6 product is starred and none is in D9.11's caps or D9.12's CPI window (C header line
60); q_c = 1 contract = 1 lot-equivalent (minis 1, D9.6), the D9.5 cap; price limits per D9.7 in the
engine (C13). Entries one minute after the 08:30 reopen (CP3, crushgap) are ordinary market orders
(section 7 item 12; K6-L-16).

---

## 1. K6-cp1-01 (core port CP1, intraday momentum). C lines 235-286; D line 364

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicles | ZC, ZW, ZS, ZM, ZL, HE, LE, q_c 1 each; one trial each | C 239-240; S0.2 |
| Signal | s = sign(close of the bar at O+29 = 08:59 minus open of the trade date's first bar), in ticks | C 253-254, 259-261; D 364 |
| Trade date's first bar, grains | the earliest bar with trade_date d whose CT open is at or after 19:00 on the calendar day before d (normally the 19:00 bar; Sunday 19:00 for a Monday); on a date with no evening session (2025-11-28, 2025-12-26, 2026-01-02 in the window) that is normally the 08:30 bar of d, and the first later bar of d if the 08:30 bar is missing, by the same clause (amended after audit N-1, R-T3-1) | C 83-84, 253-254; D 364; K6-L-01 |
| Trade date's first bar, livestock | the 08:30 bar of d exactly (no overnight session; the (b) form, R-03); missing: no trade | C 85-87, 237, 259-261; K6-L-02 |
| Signal-bar guard | both signal bars present with one instrument_id, else no trade | D 364; E.3-L-06 |
| Zero signal | s = 0: no trade | D 364 |
| Entry | market intent on the bar at C-31: grains 12:44 (fills 12:45), livestock 12:29 (fills 12:30); buy if s > 0, sell if s < 0 | C 255, 262; S0.6 |
| Exit | market intent on the first bar at or after C-2: grains 13:13 (fills nominally 13:14), livestock 12:58 (fills 12:59) | C 256, 263; S0.7 |
| Hold | 29 minutes nominal | C 257, 263 |
| Early halts | not tested by the member (port; on an early-halt day F precedes the entry bar and the bar is absent or the engine refuses) | C 89 ("the ports follow D6 as written") |
| Parameters (literals) | O+29, C-31, C-2 from D6 with O and C from the frozen table; no grid | C 267 |
| Release instants read | none; the grain window 12:45-13:14 spans 13:00 on FOMC dates (D8 event cost on the exit, the engine's) | C 279-282 |
| Trials in N | 7 | C 286 |
| Topstep | last fill 13:14 or 12:59; market; one trade a day | C 273-283 |

## 2. K6-cp2-01 (core port CP2, opening-range breakout). C lines 288-334; D line 365

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicles | ZC, ZW, ZS, ZM, ZL, HE, LE, q_c 1 each | C 290-291 |
| Opening range | OR_high = max high, OR_low = min low of the present bars opening in [O, O+15) = [08:30, 08:45) of CT date d; no OR bar: no trade; no minimum bar count, no instrument guard | C 302; E.3-L-08 |
| Buffer | 4 x vendor_tick of the traded vehicle: ZC, ZW, ZS 1.00 (cents/bu = 0.01 USD/bu); ZM 0.40 (USD/short ton); ZL 0.04 (cents/lb = 0.0004 USD/lb); HE, LE 0.100 (cents/lb = 0.001 USD/lb). Each equals C's table (C lines 113-121) because each exposure has one contract; a test pins all seven | C 304-305; D 368-372; K4-L-06 |
| Eligible bars | bars opening in [O+15, C): grains [08:45, 13:15), livestock [08:45, 13:00) of CT date d; no entry from C on | C 303 |
| Entry | the first eligible bar whose close >= OR_high + buffer buys; whose close <= OR_low - buffer sells (non-strict); market intent on that bar; one entry per trade date (the first qualifying bar uses the day's entry even if the engine refuses it) | C 306-307; E.3-L-08 |
| Exit | 75 minutes after the fill, counted as the MES module counts it: count present bars while the position is non-zero, starting after the entry intent bar; on the 75th, a market intent closing the position; or the engine's flatten at F if earlier. No C-2 exit | C 308-310; E.3-L-07 |
| Hold | up to 75 minutes; grain fills after 12:03 and livestock fills after 11:48 are cut by F | C 309-311 |
| Early halts, guard | none (port) | C 89; E.3-L-08 |
| Parameters (literals) | OR 15 minutes, buffer 4 ticks, hold 75 minutes; no grid | C 316 |
| Release instants read | none; fills in [11:00, 11:02) on USDA release dates and [13:00, 13:02) on FOMC dates are moved by the engine (D9.5a); the D9.3 skip of a deferred livestock 13:02 fill before F = 13:03 is the engine's (item 5) | C 319-331; D9.3 |
| Label | "tick history not source-verified for the research window" on all 7 trials (the buffer is in ticks; K1-L-14 10(c), R-T3-2 adopted) | K6-L-16 |
| Trials in N | 7 | C 334 |
| Topstep | flatten by the engine at F; market; one trade a day | C 319-331 |

## 3. K6-cp3-01 (core port CP3, prior-close location). C lines 336-378; D line 366

| Field | Rule | Reference |
|---|---|---|
| Exposures, vehicles | ZC, ZW, ZS, ZM, ZL, HE, LE, q_c 1 each | C 338-339 |
| Daily bar of trade date d | from the bars of CT date d opening in [O, C): grains [08:30, 13:15), livestock [08:30, 13:00): O_d = open of the 08:30 bar, H_d / L_d = max high / min low over the present bars, C_d = close of the C-1 bar (13:14 grains, 12:59 livestock) | C 350-355 |
| Complete day (Family H) | the 08:30 and C-1 bars exist, the date is not an early halt (the bars carry early_halt_ct), and all bars in [O, C) carry one instrument_id; finalised when a bar of a later trade date arrives | C 351-352; E.3 spec section 3 |
| "d-1" | the most recent COMPLETE daily bar of a trade date before d; incomplete days are dropped | C 342-346; E.3-L-09 |
| Warm-up | no complete earlier bar yet: no trade | E.3 spec section 3 |
| Instrument guard | d-1's instrument_id equals the instrument_id of day d's 08:30 bar, else no trade | C 356 |
| Condition | Range = H - L of d-1 in ticks, > 0; CLV = (C - L) / (H - L) in ticks, exact; CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict) | C 343-345, 357 |
| Day d exclusion | a trade date d whose 08:30 bar carries early_halt_ct: no trade | E.3-L-09, E.3-L-11 |
| Entry | market intent on the 08:30 bar of d (fills at the 08:31 open); the 08:30 bar must exist | C 352-353; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 13:13 grains (fills 13:14), 12:58 livestock (fills 12:59) | C 353, 355; E.3-L-10 |
| Hold | about 283 minutes (grains), 268 (livestock) | C 353-355 |
| Parameters (literals) | CLV cuts 0.2 and 0.8, lookback 1; no grid | C 361 |
| Release instants read | none; holds through 11:00 on USDA dates and 13:00 on FOMC dates (engine costs) | C 370-371 |
| Trials in N | 7 | C 378 |
| Topstep | last fill 13:14 or 12:59; market; the 08:31 fill after the reopen is an ordinary market order (item 12) | C 364-375 |

## 4. K6-crushgap-01 (soybean crush gap, single leg ZS). C lines 380-494

| Field | Rule | Reference |
|---|---|---|
| Traded exposure | ZS only, q_c 1 (1 trial); ZM and ZL are signal legs, read only | C 382-386; S0.1 |
| GPM | GPM = 0.022 x P_ZM + 11 x P_ZL - P_ZS in USD per bushel, P_ZM in USD per short ton, P_ZL in USD per pound, P_ZS in USD per bushel, each converted from the vendor price by the product's vendor_price_factor (ZM 1, ZL 100, ZS 100). In ticks (S0.10): GPM x 10^4 = 22 t_ZM + 11 t_ZL - 25 t_ZS exactly (units of 0.0001 USD/bu); a test pins the identity | C 425-434; K6-L-03 |
| d-1 | the EC-CAL grain trade date before d (GRAIN_TRADE_DATES), not the most recent complete date | C 440-441; K6-L-04 |
| GPM_close(d-1) | from the closes of the three 13:14 bars (ZS, ZM, ZL) of trade date d-1 | C 440-441 |
| GPM_open(d) | from the opens of the three 08:30 bars of d | C 442 |
| Guard | per leg: its 13:14 bar of d-1 and its 08:30 bar of d exist and carry the same instrument_id; else no trade on d (C4's guard per leg, S0.9) | C 443-444; K6-L-05 |
| Signal | G(d) = GPM_open(d) - GPM_close(d-1) | C 439 |
| Entry | G <= -0.02 USD/bu: SELL ZS; G >= +0.02: BUY ZS (non-strict; 200 units of 0.0001); otherwise no trade. Market intent on the 08:30 ZS bar of d, filling at the 08:31 open | C 445-449 |
| Exit | market intent on the first ZS bar at or after 13:13 (fills nominally 13:14) | C 450; S0.7 |
| Hold | about 283 minutes | C 451 |
| Exclusions | d not in GRAIN_FULL_SESSIONS: no trade; roll blackout of any of ZS, ZM, ZL (engine, D4); D11.5 refuses an open when any of the three legs lacks the 08:30 bar (consistent with the guard) | S0.8; C 88-95 |
| Parameters (literals) | weights 0.022 and 11; filter 0.02 USD/bu; entry 08:30 bar, exit 13:13; no grid | C 457-464 |
| Inputs and availability | d-1's 13:14 bars at 13:15 CT on d-1; the 08:30 bars at 08:31 CT on d; EC-CAL known in advance | C 452-455 |
| Not implemented | the sign check and the correlation diagnostic are reported beside a confirmation verdict (C 470-478), not part of the member or the screen | C 470-478 |
| Trials in N | 1 | C 382, 494 |
| Topstep | last fill 13:14; holds through 11:00 on USDA dates at 1 lot; one contract, never two legs | C 479-491 |

## 5. K6-limitcont-01 (day after a limit close, HE and LE). C lines 496-594

| Field | Rule | Reference |
|---|---|---|
| Traded exposures | HE, LE, q_c 1 each (2 trials) | C 498 |
| c | the instrument_id of d's 08:30 bar; the 08:30 bar must exist | C 534-535; K6-L-09 |
| S(c, x) | D9.7's settlement proxy of trade date x, computed exactly as rules.price_limits.settlement_proxy over settlement_window_ct(root, x) (the engine's screening/stage_e_rules.py lines 241-273), from the bars of trade date x: if a bar of x opening in [window start minute, window end) has volume > 0, S = the volume-weighted close of those bars (regular day: the 12:59 bar alone, so S = its close; early-halt day: the bar opening one minute before the halt); else S = the close of the last bar of x opening before the window end (fallback R-P2); no such bar: S undefined. Every bar S uses must carry c | D9.7 (D 531-551, line 542); C10 lines 170-176; K6-L-06 |
| Days | d-1, d-2, d-3 = the three EC-CAL livestock trade dates before d (LIVESTOCK_TRADE_DATES) | C 534; K6-L-07, K6-L-09 |
| L(p, x) | the initial daily limit of p in force on trade date x, from LIMIT_PERIODS (= rules.price_limits.LIMITS), in vendor ticks | C 537-538, 546-552; K6-L-07 |
| Event | S(c, d-1) - S(c, d-2) = +L(p, d-1) (limit-up close) or = -L(p, d-1) (limit-down close), exactly in ticks; and d-1's limit was the initial one: S(c, d-2) - S(c, d-3) is neither +L(p, d-2) nor -L(p, d-2). Any S undefined: no trade | C 534-539; K6-L-07, K6-L-08 |
| Contract without a limit | does not qualify; the frozen table gives every livestock date a limit (no spot-month exemption encoded), so none is excluded on that ground. This is moot only while E.2a's roll keeps the vehicle out of its contract's last two trading days (CME: no HE limit, and the expanded LE limit, there; R-1b-4; amended after audit N-7, R-T3-3) | C 539; K6-L-07 |
| Entry | market intent on the bar at 08:44 (fills at the 08:45 open): BUY after a limit-up close, SELL after a limit-down close; the 08:44 bar must exist and carry c | C 540-541; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 12:58 (fills 12:59), or earlier by the engine's D9.7 forced exit | C 542-543; S0.7 |
| Hold | about 254 minutes | C 544-545 |
| Exclusions | d not in LIVESTOCK_FULL_SESSIONS: no trade; roll blackout (engine); missing or off-contract bars as above | S0.8 |
| Inputs and availability | S(c, d-1) at 13:00 CT on d-1 (the 12:59 bar's close), before d's 08:30 open; the limit table known in advance | C 546-552 |
| Not implemented | the sign check and the close-to-open part are reported beside a confirmation verdict (C 572-578) | C 572-578 |
| Trials in N | 2 | C 498, 594 |
| Topstep | one entry 15 minutes after the open; never on the lock day itself; D9.7's entry guard and forced exit are the engine's | C 579-591 |

## 6. K6-wasdepre-01 (WASDE-day pre-release drift through the release, ZC and ZS). C lines 596-680

| Field | Rule | Reference |
|---|---|---|
| Traded exposures | ZC, ZS, q_c 1 each (2 trials) | C 600-602 |
| Event set | d in WASDE_DATES (EC-WASDE, C9a, after the drop rule) and in GRAIN_FULL_SESSIONS; T = 11:00 CT | C 158, 630; K6-L-11 |
| Signal | Dr = close of the bar at 10:29 minus open of the bar at 08:30, in ticks; both bars present with one instrument_id; Dr = 0: no trade | C 631-632 |
| Entry | market intent on the bar at 10:29 (fills at the 10:30 open), in the direction of sign(Dr) | C 633-634 |
| Exit | market intent on the bar at 11:14 (fills at the 11:15 open); if the 11:14 bar is missing, on the first later bar | C 635; C 96-98; K6-L-12 |
| Hold | 45 minutes | C 636 |
| Parameters (literals) | drift window 08:30-10:29, entry 10:29, exit 11:14; no threshold; no grid | C 643-654 |
| Inputs and availability | the 08:30 bar at 08:31, the 10:29 bar at 10:30; the WASDE date known before d | C 637-641 |
| Not implemented | the sign check and the pre-release / release split are reported beside a confirmation verdict (C 657-662) | C 657-662 |
| Trials in N | 2 | C 680 |
| Topstep | no fill in [11:00, 11:02) by construction; the 11:15 exit pays D8's event cost (engine) | C 663-677 |

## 7. K6-wasdepost-01 (WASDE-day post-release continuation, ZC). C lines 682-743

| Field | Rule | Reference |
|---|---|---|
| Traded exposure | ZC, q_c 1 (1 trial) | C 684-685 |
| Event set | d in WASDE_DATES and in GRAIN_FULL_SESSIONS; T = 11:00 CT | C 706; K6-L-11 |
| Signal | R = close of the ZC bar at 11:14 minus close of the ZC bar at 10:59, in ticks; both bars present with one instrument_id; R = 0: no trade | C 707-708 |
| Entry | market intent on the bar at 11:14 (fills at the 11:15 open), in the direction of sign(R) | C 709-710 |
| Exit | market intent on the first bar at or after 13:13 (fills at the 13:14 open) | C 711 |
| Hold | about 119 minutes | C 712 |
| Parameters (literals) | response window 10:59-11:14 bar closes; entry 11:14; exit 13:13; no grid | C 716-721 |
| Inputs and availability | the signal at 11:15 CT; the WASDE date known before d | C 713-714 |
| Not implemented | the sign check (C 724-727) | C 724-727 |
| Trials in N | 1 | C 743 |
| Topstep | the 11:15 entry pays D8's event cost (engine); D9.7's entry guard blocks a near-limit entry (engine) | C 728-741 |

## 8. Trial count

27 declarations (S0.2): 21 port trials (3 ports x 7 exposures) + crushgap ZS + limitcont HE, LE +
wasdepre ZC, ZS + wasdepost ZC. This matches the E.1 JSON (reports/stage_e1_changes.md line 1855: K6
members_active 7, trials 27), the banner (C lines 6-7) and the prompt's expectation. Program N after K6:
167 + the K6 trials screened (K6-L-17).

## 9. Lead readings (each is also an open choice in reports/E.8_RETURN.md section 6)

Adopted from earlier clusters (the text is the same): E.3-L-01 (literal tables), E.3-L-03 (the bar at
hh:mm is on CT date d), E.3-L-04 (named entry bar exact), E.3-L-06 (CP1's guard is D6's), E.3-L-07 (CP2
counts present bars, no C-2 exit), E.3-L-08 (CP2's range from present bars; the first qualifying bar uses
the day's entry), E.3-L-09 (CP3 by Family H), E.3-L-10 (CP3 exits at the first bar at or after C-2),
E.3-L-11 (early halt = the bar's early_halt_ct, for the ports), E.3-L-12 (C4's "a bar the rule reads" =
at or before the entry decision), E.3-L-13 (C4's "entry bar" = the bar the entry intent is emitted on),
E.3-L-15 (release rows at another time are left out, not re-timed), E.3-L-17 (fixed trading_windows),
E.3-L-19 (integer vendor ticks), E.3-L-20 (an undersized vehicle, ZC, is coded and screened at q_c 1),
E.3-L-22 (a refused exit is resent), K4-L-01 (tables span the whole period; only research-window rows
are checked), K4-L-03 (event sets are the table rows, on dates with no early halt), K4-L-05 (exact
threshold compares), K4-L-06 (CP2's buffer as 4 x vendor_tick), K4-L-13 (full-session table over
EC-CAL's coverage only), K3-L-11 (an early engine F is an early close for C4), K7-L-01 (bars identified
by CT date and clock), K1-L-10 (C4's early-close test by table for the new members), K1-L-14 10(c) (the
CP2 tick-history label), K1-L-16 (the N rule). Not adopted: E.3-L-05 (K6's text differs, K6-L-01);
K7-L-03 (vendor-degraded dates; K6's C4 has no such clause).

New readings for K6:
- **K6-L-01 Grain CP1's first bar is the earliest bar of trade date d at or after 19:00 CT on the
  calendar day before d.** C3 (lines 83-84: "The 'trade date's first bar' is the first bar at or after
  that 19:00 CT open") and the CP1 entry (lines 253-254) fix it; D6 governs ports ("open of the trade
  date's first bar"). Normally the 19:00 bar (Sunday 19:00 for a Monday). If the 19:00 bar is missing,
  the first later bar of the evening session (the text's "at or after"). On a grain trade date with no
  evening session (the calendar's scheduled late opens; in the window 2025-11-28, 2025-12-26,
  2026-01-02, open 08:30) the first bar at or after that instant is normally the 08:30 bar of d (if it is
  missing, the first later bar of d by the same clause; amended after audit N-1, R-T3-1), which is also D6's
  "trade date's first bar" (R-03's gloss for a session that starts at the day open). E.3-L-05 (the bar
  at the open exactly, else no trade) is not adopted: K2's text named "the Globex open, 17:00 CT on d-1",
  K6's says "the first bar at or after". The difference can only touch dates whose 19:00 bar is missing
  and the two late-open dates that CP1 can trade (2025-11-28 is an early-halt date: no 12:44 bar).
  Flagged for the user.
- **K6-L-02 Livestock CP1's first bar is the 08:30 bar exactly.** C lines 259-261 name "the 08:30 bar"
  (C3 line 85-87: the night session was cancelled; R-03, line 237). If it is missing: no trade.
- **K6-L-03 crushgap's GPM in exact integer units.** The weights are the entry's literals 0.022 and 11
  (C lines 425-434); the unit conversion is the frozen vendor_price_factor (ZM 1, ZL 100, ZS 100), which
  E.2a confirmed against the bars (cents quoting, 0 off-tick prices). With prices in ticks
  (t = price / vendor_tick), GPM x 10^4 = 22 t_ZM + 11 t_ZL - 25 t_ZS in 0.0001 USD/bu, and the 0.02
  filter is 200 of those units. The code derives the coefficients from product(root) and the weights
  (Fraction or Decimal), and a test pins the identity and the filter. Comparisons are non-strict as
  written ("<= -0.02", ">= +0.02").
- **K6-L-04 crushgap's d-1 is the EC-CAL grain trade date before d,** as the entry says ("the previous
  grain trade date d-1 in EC-CAL", C lines 440-441), not CP3's "most recent complete" day. If d-1 is an
  early-halt date its 13:14 bars do not exist and d is not traded (C lines 443-444).
- **K6-L-05 crushgap's guard is per leg.** "Bars that one computation reads carry different
  instrument_ids" (C4 line 95) is applied per leg: each leg's 13:14 bar of d-1 and 08:30 bar of d carry
  one instrument_id (C lines 443-444). The three legs are different products, so their ids always
  differ. Contract-month mismatches across legs are accepted (C lines 435-438, section 7 item 10).
- **K6-L-06 limitcont's settlements are D9.7's proxy, computed as the engine computes it.** The entry
  reads official settlements (C lines 546-552); section 7 item 2 put their source to the lead, who ruled
  at 01:52 (reports/stage_e0_STATE.md line 70) "settlements from Databento statistics schema (quote in
  E.1) or settlement-window VWAP proxy", written into D9.7 (D line 542: "if not bought, the
  volume-weighted price of the one-minute bars in the product's settlement window as the proxy"). The
  statistics schema was not bought (rules/price_limits.py lines 39-42). So S(c, x) is the harness's
  proxy for x, the same number the engine's D9.7 rule uses as x's settlement (screening/stage_e_rules.py
  lines 241-273, 329-334). The member cannot import rules.price_limits, so it re-implements
  settlement_window_ct (livestock: [12:59:30, 13:00:00) CT; on an early-halt date the 30-second window
  ending at the halt, LIVESTOCK_EARLY_HALT_CT) and settlement_proxy (the volume-weighted close of the
  bars whose minute overlaps the window, else the last close before the window end) exactly; a test
  compares the member's function with rules.price_limits on synthetic bars, including the fallback and
  an early-halt date. The proxy adds one requirement the engine does not have: the bars it uses carry c
  (K6-L-09). Known limit of the proxy (C section 7 item 2: "A bar-close proxy would misclassify limit
  closes, because the settlement is not the last trade"): a true limit close is missed when the proxy
  of d-2 differs from the official settlement, and a close one tick from the official limit can be
  counted when the proxy of d-2 is off by that tick. Flagged for the user.
- **K6-L-07 limitcont's limit is the frozen initial limit, and d-1 must not have carried an expanded
  limit.** The entry's L is "the limit in force on d-1 (expanded where in force), from EC-LIM" (C lines
  537-538). The frozen EC-LIM encodes the initial limit only (rules/price_limits.py lines 16-18, flag
  R-L2), and E.2a's captures show expanded livestock limits inside the window (LE 2025-08-11 and
  2025-10-20, reports/stage_e2a_price_limits.json captures_parsed). Building an expanded table would add
  an input the freeze does not hold, so the member reads LIMIT_PERIODS (= LIMITS) and adds the condition
  that d-2 was not itself a limit close of c (|S(c, d-2) - S(c, d-3)| != L(p, d-2)): on such a d, d-1's
  limit was expanded by CME's rule, the initial-limit test is not the entry's test, and the date is not
  traded. This only removes dates; it never adds one. Two residuals, flagged for the user: (a) a
  limit-close continuation on the second consecutive limit day (d-1 closed at its expanded limit) is
  never traded; (b) an expansion triggered by another contract month, which c's settlements cannot show,
  is not detected (a d whose d-1 moved exactly the initial limit under an expanded limit would count;
  it needs an exact tick coincidence). Not adopted: (i) the plain initial-limit test without the d-2
  condition (it can count non-events on expanded days); (ii) an expanded-limit table from CME's rulebook
  (an input outside the frozen EC-LIM). Task 1b B3 records CME's expansion rule for the record.
- **K6-L-08 limitcont's equality is exact in vendor ticks.** "Exact equality of the settlement with the
  limit price" (C line 560). On a regular day the proxy is one bar's close, on the tick grid; on any day
  it is compared as an exact Decimal or Fraction (a volume-weighted mean of several bars is off the grid
  and equals a tick-grid limit price only if it lands on it exactly). L in ticks is an integer for every
  period (S0.11). "E.2 applies CME's settlement rounding" (C line 562) is moot: the proxy is not rounded,
  as the engine does not round it.
- **K6-L-09 limitcont's contract and guard.** c = the instrument_id of d's 08:30 bar (C line 535); the
  08:30 bar must exist. The bars read at or before the entry decision (E.3-L-12) are the 08:30 bar of d,
  the bars that give S(c, d-1), S(c, d-2) and S(c, d-3), and the 08:44 entry bar; each must carry c, else
  no trade (C4 lines 93-95). d-1, d-2 and d-3 are consecutive EC-CAL livestock trade dates; a date before
  the first one the member has seen (the window's first three dates) gives no trade.
- **K6-L-10 C4's early-close test by table** for the four new members: GRAIN_FULL_SESSIONS and
  LIVESTOCK_FULL_SESSIONS (S0.8), as K1-L-10 and K3-L-11. The generator lists any date where the
  early-halt test and the F test disagree. CP3 keeps Family H's bar test (E.3-L-09).
- **K6-L-11 EC-WASDE is the frozen release calendar's WASDE rows at 12:00 ET, after C9a's drop rule.**
  The entries read the date only (T = 11:00 CT is fixed, C line 72-74). Task 1b checks every
  research-window row against USDA's schedule and ESMIS record; a row whose date differs from the
  year's published schedule is kept only with a USDA notice of the new date dated before it (C lines
  155-157), otherwise it goes into DROPPED_WASDE (section 10). A WASDE that USDA published but the
  calendar lacks is not added (the members read the frozen calendar; adding would widen). Dates that are
  WASDE and early-halt dates are not traded (S0.8).
- **K6-L-12 wasdepre's exit bar.** "Market intent on the bar at 11:14" (C line 635) is an exit; if the
  11:14 bar is missing, the exit goes on the first later bar (C4 lines 96-98).
- **K6-L-13 trading_windows** as S0.12.
- **K6-L-14 27 declarations**, ordinals in catalog order then ZC, ZW, ZS, ZM, ZL, HE, LE (the stage
  prompt's order).
- **K6-L-15 Two coders and their test files.** MemberCoder-A: _port_common.py, cp1.py, cp2.py, cp3.py,
  crushgap.py; tests/test_k6_members_ports*.py and tests/test_k6_members_crushgap.py. MemberCoder-B:
  _calendar.py (first), _wasde.py, _limits.py, _event_common.py, limitcont.py, wasdepre.py,
  wasdepost.py; tests/test_k6_members_tables.py, tests/test_k6_members_limitcont.py,
  tests/test_k6_members_wasde.py; the generator reports/stage_e8_briefs/gen_k6_tables.py. The lead
  creates strategy/members/k6/__init__.py empty (0 bytes).
- **K6-L-16 C section 7 settled.** Item 1: ZS only (banner line 382). Item 2: the proxy (K6-L-06). Item
  3: the D9.7 exit is exempt from the fill guard (D9.7, 01:52; engine). Item 4: 2 percentage points of
  price inside the limit (D9.7; engine). Item 5: D9.3's skip (engine). Item 6: R-03, the (b) form
  (K6-L-02). Item 7: the cuts as the banners give them, 27 trials. Item 8: no action (a correlated
  member, both screened). Item 9: K6-032 stays excluded (01:52). Item 10: each vehicle's own roll as
  E.2a built it; crushgap accepts month mismatches (C lines 435-438). Item 11: every K6 member carries
  source-overlap (confirmation only). Item 12: the 08:31 entries after the reopen are ordinary market
  orders; the entries fix the entry bar and D9.4's "gapped markets" clause concerns strategies built on
  stray fills, which the engine's slippage charge does not reward. Item 13: (a) the research bars are on
  the frozen tick grid and in the frozen units (E.2a, 0 off-tick prices); the tick history is not
  source-verified, and only CP2's buffer depends on the tick size, so the seven K6-cp2-01 trials carry
  the label "tick history not source-verified for the research window" (K1-L-14 10(c), R-T3-2); (b)
  Task 1b item C; (c) Task 1b item A; (d) ML only, moot (U6); (e) the proxy and R-L2 (K6-L-06,
  K6-L-07); (f) the runner's D9 coverage on S0.12's windows; (g) moot (all seven exposures admitted).
  Items 14 and 15: no action.
- **K6-L-17 The N rule** (K1-L-16, K7-L-05, pre-declared before any run): a trial counts when the runner
  writes its screen record (status "run"); a trial the runner excludes before screening (coverage) or
  refuses does not count.
- **K6-L-18 The ports' early halts and F.** The ports test no K6 calendar set (C line 89); on an
  early-halt or early-F date the engine's F governs, and CP3 applies Family H's bar test.

## 10. The research-window check and the rulings (lead, 00:18 PDT, after Task 1b)

Source: reports/stage_e8_release_check.md and .json (ReleaseChecker-OpusMed, 00:06-00:17 PDT; 199k
tokens). Evidence pages under reports/stage_e8_briefs/pages/ with URL, UTC fetch time and sha256 in the
.json.

- **R-1b-1 EC-WASDE: all 14 research-window rows kept; DROPPED_WASDE is empty.** Each row's date equals
  USDA OCE's published 2025 or 2026 list (Wayback captures 2025-03-11 and 2025-12-19, "Release Dates
  (12:00pm ET)") and ESMIS's record, except 2025-11-14: scheduled Nov. 10, moved by the NASS notice of
  2025-10-31 ("The World Agricultural Outlook Board will release the World Agricultural Supply and
  Demand Estimates (WASDE) in conjunction with the Crop Production release on November 14th"; a Wayback
  capture of 2025-11-07 already holds the sentence). The notice is dated before the new date, so C9a's
  drop rule keeps it. The October 2025 WASDE (scheduled Oct. 9) was not published (the lapse in
  appropriations) and the calendar has no row for it. All 14 are at 12:00 ET. ESMIS lists no WASDE the
  calendar lacks. No release time is on ESMIS; the 12:00 ET time rests on the schedule headers.
- **R-1b-2 LE limit 2026-06-01..2026-06-18 DROPPED for the member.** The frozen table's bracketed period
  LE 2026-05-19..06-19 holds the initial limit at $0.0725; CME SER-9736 (May 14, 2026) resets Live
  Cattle to a new initial $0.0850 "Effective, Sunday May 31, 2026 for trade date Monday, June 1, 2026".
  The table is right on 2026-05-19..05-29 and wrong on the 14 trade dates 2026-06-01..06-18. A limit its
  own exchange contradicts cannot be the L the entry tests, and the verdict set is keep, drop or
  unverifiable, so those dates are dropped: K6-limitcont-01 LE does not trade a d whose event test reads
  L on a dropped date (d-1 or d-2 in 2026-06-01..06-18; DROPPED_LIMIT_DATES["LE"] in _limits.py, each
  date with the reason). It removes trade possibilities and never adds one. The member does not use
  CME's $0.0850 (an input outside the frozen EC-LIM). HE: no dropped date.
  - Harness consequence, recorded, not acted on (no harness change in this stage): the engine's D9.7
    uses $0.0725 for LE on those 14 dates, a narrower limit than CME's, so its stop levels are closer
    than Topstep's rule would put them (stricter, as R-L2's bracketed convention intends). It touches
    every LE trial on at most those dates. For the user (return section 7), with the two
    confirmation-window mismatches 1b found outside the window (HE 2024-09-04..09-12 bracketed at
    $0.0375 against CME's $0.04 from 2024-09-03, SER-9424; LE 2024-10-09..10-24 bracketed at $0.0650
    against CME's $0.065 effective 2024-10-25, SER-9426): a confirmation of K6 must first rule on them.
- **R-1b-3 HE 2025-08-30..09-01 (bracketed) kept:** no trade date inside it, and SER-9609 keeps $0.04 in
  force until trade date 2025-09-02, which the table has.
- **R-1b-4 Expanded limits (record only, B3).** CME Rule 15202.D (HE): any of the first eight listed
  months settling at the limit expands all months by 50 percent the next business day ($0.07 from
  2025-09-02). Rule 10102.D (LE): any of the first four Live Cattle OR Feeder Cattle months settling at
  the limit expands the next business day ($0.1075 from 2025-06-02). K6-L-07's guard sees only c's own
  settlements, so an expansion triggered by another month, or by Feeder Cattle for LE, is invisible to
  the member (residual (b), now named). Captures show an expanded LE limit on 2025-08-11 and 2025-10-20;
  none for HE. CME also has no HE limit, and the expanded LE limit, in the expiring contract's last two
  trading days; the frozen table encodes neither, and the member reads the frozen table (a vehicle in
  its last two trading days would be a roll matter, outside the member).
- **R-1b-5 EC-CAL: all 32 research-window grain and livestock dates kept,** each cited in the calendar
  module from CME's trading-hours service; F agrees across the five grain roots and across HE and LE on
  all 319 weekdays. The four halt days carry F = 11:45 (Topstep's close-by), the engine's.
- **R-1b-6 Other inputs.** No active member reads a release other than WASDE, or any release value.
  Harness rows in the window for K6 roots: WASDE 14, CROP 14, CROP_PROGRESS 39 (16:00 ET), FOMC 10,
  CROP_ANNUAL 1. No date is both a WASDE and an FOMC date. Catalog K6-cp2-01's "Data needed" line names
  EC-USDA and EC-FOMC for the harness (its D9.5a and D8 use); the member reads no release.

So WASDE_DATES = every 12:00 ET WASDE row of the frozen calendar 2019-05-01..2026-06-19 (no drop), and
LIMIT_PERIODS = LIMITS for HE and LE with DROPPED_LIMIT_DATES = {"LE": the 14 trade dates
2026-06-01..2026-06-18}, pinned by the table test. Labels into the return: K6-limitcont-01 LE "limit
table partly contradicted by CME in the window (14 dates dropped)"; K6-limitcont-01 HE and LE "limits
are the frozen initial limits; expanded limits not encoded (K6-L-07)"; K6-limitcont-01 HE and LE "settlements by
the D9.7 proxy (one bar's close); official settlements not tested" (added after audit N-2, R-T3-2).
