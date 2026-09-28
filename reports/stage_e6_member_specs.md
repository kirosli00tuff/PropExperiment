# Stage E.6 member specifications, cluster K7 bitcoin (Task 1)

Written by the Stage E.6 lead (Opus 5.5, xhigh), 2026-09-27 21:30-21:40 PDT, before any K7 member code
exists and before any MBT bar has been read by this session. It restates each frozen entry as the
code must implement it, with line references, and records every reading the lead took where the
entry leaves a detail open (section 8). It changes no rule. A reading is the narrowest one the text
allows unless the text fixes the detail by reference (then the reference governs). Where K7's text
is the same as an earlier cluster's, the earlier reading is adopted and cited (E.3-L-nn:
reports/stage_e3_member_specs.md section 10; K4-L-nn: reports/stage_e4_member_specs.md section 10;
K3-L-nn: reports/stage_e4c_member_specs.md section 10).

Sources and their state:
- C = reports/stage_e0_catalog_K7.md, frozen by reports/stage_e1_freeze.json (manifest 96166eb3...).
  Line numbers below are this file's. Header and conventions C1-C14 lines 85-243; members lines
  249-694; section 7 lines 944-1026. E.1 edits to K7 (reports/stage_e1_changes.md K7-00..K7-03)
  touch only the banner (C lines 3-7), the excluded K7-ml-01 and the ML rows of sections 0 and 6.
  No active member's rule changed. K7-ml-01 is excluded (U6) and not coded.
- D = docs/STAGE_E_DESIGN.md (frozen): D5 screen lines 301-306; D6 port texts lines 364-366, the
  "4 ticks of P" paragraph lines 368-372, the crypto session row line 402 (O 08:30, C 15:00, F 15:08).
- Vehicle (reports/stage_e2a_vehicles.md line 45 and lines 403-409; frozen via
  screening.stage_e_frozen.load_frozen_tables): bitcoin -> MBT, status undersized, q_c = 1
  (1 lot-equivalent; Topstep caps MBT at mini-equivalent sizes, C6 lines 142-143). Operative eps
  (reports/stage_e2a_epsilon.md line 35): 90 net ticks per contract per day (translated 170).
  Undersized at 1 contract is screened, as E.3 screened ZT and ZF (E.3-L-20).
- Frozen per-root values (checked 21:28 PDT through load_frozen_tables() and rules.products.product):
  day_session_ct MBT = (08:30, 15:00); vendor_tick 5.00 (USD per bitcoin; $0.50 per tick per
  contract). F (rules/sessions.py, enforced by the engine) = 15:08 CT on a regular day.
- EC-CAL = the D10 crypto calendar, data/calendars/crypto.py, read through
  data.group_session.load_group_calendar("crypto"). Research window facts (checked 21:28):
  HOLIDAYS 2025-04-18 full closure, 2025-07-04 early halt 12:00, 2025-11-28 early halt 13:45 (and the
  07:30 CT outage late open), 2025-12-24 early halt 12:45, 2025-12-25 and 2026-01-01 full closures,
  2026-04-03 early halt 10:15. BOOKED_FORWARD (not trade dates; each holiday's regular session
  belongs to the next business day's trade date): 2025-05-26, 06-19, 09-01, 11-27, 2026-01-19,
  02-16, 05-25 (2026-06-19 is booked to 2026-06-22, holdout-1, never delivered: E.2a L-9, E.2b
  guard). From 2026-06-01 weekend trading belongs to Monday's trade date
  (WEEKEND_TO_NEXT_TRADE_DATE_FROM); 2026-06-01 opened Friday 2026-05-29 16:30 CT
  (EXTENDED_MAINTENANCE). The engine's flatten time (rules.sessions.flatten_time_ct("MBT", d)) is
  early on 2025-07-04 11:30, 11-28 11:45, 12-24 11:45, 2026-04-03 08:00 and on every booked-forward
  holiday's CT date (11:30 or 11:45).
- Release calendar reports/stage_e2b_release_calendar.json (frozen, sha256 839f2437...): MBT rows in
  the window are NFP, CPI, PPI (08:30 ET = 07:30 CT, 14 each) and FOMC (14:00 ET = 13:00 CT, 10).
  No MBT expiry row exists; EC-MBTX is generated from the rule (section 0, S0.11). No K7 member reads
  a release: the engine's D9.5a guard and D8's event-window cost read them.
- Vendor condition files (Databento GLBX.MDP3, on disk, untracked):
  data/vendor/databento/condition/GLBX.MDP3_2019-04-01_2025-04-01.json and
  GLBX.MDP3_2025-04-01_2026-09-16.json. MBT research trade dates flagged degraded (reports/
  stage_e2a_bars.json, products/MBT/degraded/on_research_trade_dates): 2025-09-17, 2025-09-24,
  2025-11-28, 2026-03-16, 2026-04-10.
- E.2a ruling L-11 (reports/E.2a_RETURN.md line 331; reports/stage_e2a_calendar_bar_checks.md lines
  663-675): MBT.v.0 holds the expiring contract to its last trading day, and every one of MBT's 15
  expiry Fridays in the research window lies inside a roll blackout.
- The research-window check: reports/stage_e6_release_check.md and .json (Task 1b,
  ReleaseChecker-OpusMed). Section 9 applies its verdicts.
- Source-window labels: K7-cp1-01, K7-cp2-01, K7-cp3-01 and K7-rev2h-01 keep source-overlap
  (reports/stage_e2a_source_window_amendment.md lines 73-76); K7-expiry-01 and K7-montrend-01 carry
  it by R-04 (C lines 422, 597). All six are source-overlap. Labels matter only for confirmation.

What the member does NOT implement (the engine and runner do; a member must not duplicate or
second-guess them; same list as E.3 and E.4): the window's trade dates and the removal of
roll-blackout dates (the engine refuses opens there by name, `engine_roll_blackout`; bars of those
dates are still delivered); 2026-06-18/19 (UR-1); F and the forced flatten (D9.1); costs and the
event-window cost (D8); the event-minute fill guard (D9.5a: a fill that would land in [release,
release + 2 min) moves to the first bar at or after release + 2 min; only CP2 can meet it, on FOMC
days, C14 lines 241-243); the entry cap and the 2-minute minimum hold (D9.3a/b); the skip of an entry
whose fill would come less than 2 full minutes before F; price-limit proximity and its forced exit
(D9.7, C13); the lot-equivalent cap (D9.5).

---

## 0. Common to all six members

S0.1 Legs. Each member reads and trades exactly one leg, `LegSpec("MBT", True)`. No signal legs; MET
is never read (C line 91). (C lines 253, 316, 374, 424, 520, 599.)

S0.2 Declarations. One `MemberDecl` per member, 6 in all, label `"<member id> MBT"` (for example
`"K7-cp1-01 MBT"`); the member object's `name` equals its label. Module per member under
strategy/members/k7/; one zero-argument factory `make_mbt`. Ordinals in catalog order (K7-L-10):

| Member | Module | Ordinal |
|---|---|---|
| K7-cp1-01 | strategy.members.k7.cp1 | 1 |
| K7-cp2-01 | strategy.members.k7.cp2 | 2 |
| K7-cp3-01 | strategy.members.k7.cp3 | 3 |
| K7-expiry-01 | strategy.members.k7.expiry | 4 |
| K7-rev2h-01 | strategy.members.k7.rev2h | 5 |
| K7-montrend-01 | strategy.members.k7.montrend | 6 |

S0.3 Size. Every entry is `q_c` contracts, read from `load_frozen_tables().vehicles["MBT"].q_c` (1),
never a literal (C6 lines 142-143). Every exit closes the whole position. No member sizes by signal.
At most one position (C6). A change of direction is a flatten followed by a new entry, never one 2q
order (C2 lines 110-114).

S0.4 Clock and the trade date (K7-L-01). America/Chicago. "The bar at hh:mm" of trade date d is the
bar with `trade_date == d` whose open (`ts_event_ns`) is hh:mm:00 CT on CT calendar date d (C1 lines
103-108; E.3-L-03). The only bars on another CT date are CP1's first bar (17:00 CT on CT date d-1,
E.3-L-05) and K7-montrend-01's Sunday bars (17:00-23:59 CT on CT date d-1, a Sunday). The program
convention governs in both regimes (C3 lines 115-126): trade date d = [d-1 17:00 CT, d 16:00 CT). The
bars carry CME's trade date, which from 2026-06-01 also books the weekend (Friday 16:02 to Sunday
17:00 CT) and, on the seven booked-forward holidays, the holiday's whole session (Sunday or the
prior evening 17:00 to the holiday's 16:00 CT) to the next trade date. No member reads any bar outside
[d-1 17:00, d 16:00) CT for trade date d, and no member reads a bar by `trade_date` and clock time
alone: CT date and clock both identify it. O and C come from `load_frozen_tables().day_session_ct["MBT"]`
= (08:30, 15:00) (D line 402). A bar is usable at its close (C1 line 104); `on_minute` is called at each
grid minute's close with the bar in `view.bars["MBT"]`, or None when there is no bar.

S0.5 Orders. Market intents only (`leg_market_intent`), filled by the engine at the open of a later
bar (C2 lines 108-109). No limit orders, stops or brackets.

S0.6 Named entry bar. "Market intent on the bar at X" for an entry is emitted only when the view's bar
is the bar at X. If that bar is missing, there is no entry at X (E.3-L-04). An entry is emitted at most
once per decision (the ports and K7-expiry-01: once per trade date), and never while a position or a
pending order exists on the leg.

S0.7 Exits and flattens. Every exit or flatten is sent on the first present bar at or after the named
bar, while the position is non-zero and no exit order is pending (C4 lines 135-138: "If an exit's named
bar is missing, the exit is sent on the first later bar"). A refused exit is sent again on the next
present bar under the same condition (E.3-L-22). The engine's forced flatten at F is the backstop. If
the engine closes the position itself (D9.7, the flatten, an MLL liquidation), the member sees a flat
account and sends no exit. A one-decision member (ports, expiry) makes no further entry that trade
date; a multi-decision member (rev2h, montrend) applies its rule at its later decisions as written,
comparing each target with the account's position (K7-L-07; E.4's ovr reading).

S0.8 Trade-date exclusions of the three new members (C4 lines 127-134; the ports follow D6). A new
member enters only on a trade date d in CRYPTO_FULL_SESSIONS and not in VENDOR_DEGRADED (S0.11):
- CRYPTO_FULL_SESSIONS: EC-CAL crypto trade dates with no early halt on d and the regular engine F
  (15:08 CT) on CT date d (K3-L-11 adopted: C4 excludes "dates the D10 equity-and-crypto calendar
  marks as early close or early halt", and D10 marks them through F; in the crypto calendar the two
  tests agree on every trade date of the window, and the generator lists any date the F test alone
  removes). Coverage 2019-05-01..2026-06-19 (EC-CAL's coverage, K4-L-13).
- VENDOR_DEGRADED: K7-L-03.
Roll-blackout dates are the engine's (it refuses the open by name). The ports do not test these sets:
CP1 and CP2 follow D6 (the engine's F governs); CP3 tests the early halt through Family H (section 3).

S0.9 Instrument guard (C4 lines 135-137, the new members). The signal bars of one computation carry one
instrument_id, else that signal is 0 (flat) (C4; rev2h C line 560, montrend C lines 638-640). In addition
an entry intent is sent only if the bar it is emitted on carries the signal bars' instrument_id (K7-L-06,
a K7 narrowing; amended 22:47 after audit F-2). Exit, flatten and hold decisions are not gated by the
entry bar, and exit and flatten bars are not guarded.

S0.10 Prices. Every price comparison and sign is computed in integer vendor ticks,
`round(price / vendor_tick)` with `rules.products.product("MBT").vendor_tick` (5.00), never a literal
tick (E.3-L-19). CP3's CLV is a ratio of tick ranges.

S0.11 Tables (a member cannot read a file; E.3-L-01). Literal tables in the cluster package, generated
by a script under reports/stage_e6_briefs/ from the named sources, each with the sources' sha256, and
pinned by tests that recompute them from those sources. Coder B writes strategy/members/k7/_calendar.py:
- CRYPTO_FULL_SESSIONS (S0.8), ISO dates 2019-05-01..2026-06-19, plus a comment naming the dates the F
  test alone removes (if any).
- VENDOR_DEGRADED (K7-L-03): ISO trade dates, from both condition files, by data/build_bars.py's
  mapping (a trade date whose ISO date is a degraded UTC date; build_bars.py lines 685-687 and 728),
  over 2019-05-01..2026-06-19.
- MBTX: (date, T_exp as CT "HH:MM") for every MBT last trading day 2021-05..2026-06 (K7-L-04): by
  the rule quoted in C9 lines 176-180 (last Friday of the month; if that day is not a business day in
  both the UK and the US, the preceding day that is), with England-and-Wales bank holidays (source
  reports/stage_e4c_release_check.json, as K3's EW_BANK_HOLIDAYS) and US federal holidays (observed
  dates) plus Good Friday (C9 lines 183-184); T_exp = 16:00 Europe/London on the date, in
  America/Chicago by zoneinfo (C9 lines 181-182). Research-window rows then follow section 9 (Task 1b's
  verdicts). Earlier rows are kept as the rule gives them, unchecked (K4-L-01).

S0.12 trading_windows (D9 coverage; interface lines 51-61; E.3-L-17: fixed intervals measured on every
research date). All on the one leg MBT:

| Member | Intervals [start, end) CT | Reference |
|---|---|---|
| CP1 | (17:00, 17:01) on day -1; (08:59, 09:00); (14:29, 15:00) | signal bars, entry bar to the 14:59 exit fill bar (E.4 CP1 pattern) |
| CP2 | (08:30, 15:08) | [O, F) (E.4 CP2 pattern) |
| CP3 | (08:30, 15:00) | [O, C) (E.4 CP3 pattern) |
| expiry | (05:00, 11:00) | C lines 513-514 "[T_exp - 300 min, T_exp - 1 min]", the union over both T_exp slots (10:00, 11:00), as K5 and K3 declared both clock slots |
| rev2h | (08:30, 14:31) | the first signal bar to the 14:30 exit fill bar (C lines 548-559) |
| montrend | (17:00 on day -1, 14:00 on day 0) | C lines 691-692 "[Sunday 17:00, Monday 14:00) CT", as stated |

S0.13 Topstep checks common to all (C lines 300-309 and each entry's list): flat by F (engine); market
orders only; at most 1 entry a day (rev2h at most 2, montrend at most 20: D9.3a's 20 is never
exceeded); every hold is at least 29 minutes by rule (D9.3b's 2 minutes never binds); no stops,
brackets or passive fills (D9.4); MBT is starred (F1.9) and for the 50K XFA the star imposes nothing
beyond F5.4's mini-equivalent weighting (C line 96); q = 1 MBT = 1 lot-equivalent, half the XFA's
2-lot maximum, so holding through a release is allowed (F6.3); position limit <= 1 lot-equivalent;
price limit per D9.7 in the engine (C13; E.0 R-10: the D9.7 exit is exempt from the fill guard).

S0.14 No member reads spot, BRR or flow data (C10 lines 205-212). K7-expiry-01 reads no BRR value (C
line 476).

---

## 1. K7-cp1-01 (core port CP1, intraday momentum). C lines 249-312; D line 364

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | bitcoin MBT, q_c 1 | C 252-255; S0.1 |
| Signal | s = sign(close of the bar at O+29 = 08:59 minus open of the trade date's first bar), in ticks | C 273-274; D 364 |
| Trade date's first bar | the bar opening 17:00 CT on CT date d-1 (the calendar day before d), with trade_date d: Sunday 17:00 for a Monday in both regimes; the Monday 17:00 bar for the trade date after a booked-forward Monday | C 273-274, 283-289 (C3 lines 115-126); E.3-L-05; K7-L-01 |
| Signal-bar guard | both signal bars present with one instrument_id, else no trade | D 364; E.3-L-06 |
| Zero signal | s = 0: no trade | D 364 |
| Entry | market intent on the bar at C-31 = 14:29; buy if s > 0, sell if s < 0; fills at the 14:30 open | C 275-276; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 14:58; fills nominally at the 14:59 open | C 277-279; S0.7 |
| Hold | 29 minutes nominal | C 280 |
| Early halts, vendor-degraded | not tested by the member (port; on an early-halt day F precedes 14:29 and the engine refuses) | C 127 ("the ports follow D6 as written") |
| Parameters (literals) | O+29 = 08:59, C-31 = 14:29, C-2 = 14:58; no grid | C 293-294 |
| Release instants read | none; no release falls in 14:30-14:59 | C 306 |
| Trials in N | 1 | C 312 |
| Topstep | last fill 14:59; market; one trade a day | C 300-309 |

## 2. K7-cp2-01 (core port CP2, opening-range breakout). C lines 314-370; D line 365

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | bitcoin MBT, q_c 1 | C 316-318 |
| Opening range | OR_high = max high, OR_low = min low of the present bars opening in [O, O+15) = [08:30, 08:45) of CT date d; no OR bar: no trade; no minimum bar count, no instrument guard | C 336-337; E.3-L-08 |
| Buffer | 4 x vendor_tick = 20.00 (USD per bitcoin), in ticks 4; MBT is the exposure's only and most active contract, so D's "fixed whatever vehicle D2 chooses" holds; a test pins 20.00 | C 339-340; D 368-372; K4-L-06 |
| Eligible bars | bars opening in [O+15, C) = [08:45, 15:00) of CT date d; no entry from 15:00 on | C 338 |
| Entry | the first eligible bar whose close >= OR_high + buffer buys; whose close <= OR_low - buffer sells; market intent on that bar; one entry per trade date (the first qualifying bar uses the day's entry even if the engine refuses it) | C 341-342; E.3-L-08 |
| Exit | 75 minutes after the fill, counted as the MES module counts it: count present bars while the position is non-zero, starting after the entry intent bar; on the 75th, a market intent closing the position; or the engine's flatten at F if earlier. No C-2 exit | C 343-346; E.3-L-07 |
| Hold | 75 minutes; the latest fill (15:00) is held at most 8 minutes (F binds after 13:53) | C 345-347 |
| Early halts, vendor-degraded, guard | none (port) | C 127; E.3-L-08 |
| Parameters (literals) | OR 15 minutes, buffer 4 ticks, hold 75 minutes; no grid | C 352 |
| Release instants read | none; an entry or exit fill in [13:00, 13:02) on an FOMC day is moved by the engine (D9.5a); fills in [13:00, 13:30) pay D8's event cost | C 363-366 |
| Trials in N | 1 | C 370 |
| Topstep | flatten by the engine at F; market; one trade a day | C 358-368 |

## 3. K7-cp3-01 (core port CP3, prior-close location). C lines 372-418; D line 366

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | bitcoin MBT, q_c 1 | C 374-376 |
| Daily bar of trade date d | from the bars of trade date d on CT date d opening in [O, C) = [08:30, 15:00): O_d = open of the 08:30 bar, H_d / L_d = max high / min low over the present bars, C_d = close of the 14:59 bar | C 390-391; K7-L-01 |
| Complete day (Family H) | the 08:30 and 14:59 bars exist, the date is not an early halt (the bars carry early_halt_ct), and all bars in [08:30, 15:00) carry one instrument_id; finalised when a bar of a later trade date arrives | C 392-393; E.3 spec section 3 |
| "d-1" | the most recent COMPLETE daily bar of a trade date before d; incomplete days are dropped. For a Monday that is Friday's bar in both regimes; after a booked-forward Monday it is the Friday before (the holiday is not a trade date and its session is never a daily bar) | C 394-396; E.3-L-09; K7-L-01 |
| Warm-up | no complete earlier bar yet: no trade | E.3 spec section 3 |
| Instrument guard | d-1's instrument_id equals the instrument_id of day d's 08:30 bar, else no trade | C 393-394 |
| Condition | Range = H - L of d-1 in ticks, > 0; CLV = (C - L) / (H - L) in ticks; CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict) | C 397 |
| Day d exclusion | a trade date d whose 08:30 bar carries early_halt_ct: no trade | E.3-L-09, E.3-L-11 |
| Entry | market intent on the 08:30 bar of d (fills at the 08:31 open); the 08:30 bar must exist | C 398; S0.6 |
| Exit | market intent on the first bar at or after C-2 = 14:58 (fills nominally at 14:59) | C 399; E.3-L-10 |
| Hold | about 388 minutes | C 400 |
| Parameters (literals) | CLV cuts 0.2 and 0.8, lookback 1; no grid | C 404 |
| Release instants read | none | C 412-414 |
| Trials in N | 1 | C 418 |
| Topstep | last fill 14:59; holds through FOMC at 1 lot-equivalent | C 407-416 |

## 4. K7-expiry-01 (long before the BRR final-settlement time on MBT's last trading day). C lines 420-516

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | bitcoin MBT, q_c 1 | C 424-426 |
| Event set | each MBTX date d (S0.11) that is in CRYPTO_FULL_SESSIONS and not in VENDOR_DEGRADED (S0.8) | C 457; C9 lines 175-190 |
| Clock | T_exp(d) from the MBTX table: 16:00 Europe/London in CT (normally 10:00, 11:00 in UK/US clock-mismatch weeks; research window 2025-10-31 and 2026-03-27) | C 458-459; C9 181-182 |
| Direction | long only | C 460; C 479 |
| Entry | market intent BUY on the bar at T_exp - 301 min (04:59 or 05:59 CT on CT date d), filling at the open of the bar at T_exp - 300 min (05:00 or 06:00) | C 460-461; S0.6 |
| Guard | the rule reads only the entry bar (no signal), so S0.9 is met by that bar alone | C 470-476; S0.9 |
| Exit | market intent on the bar at T_exp - 2 min (09:58 or 10:58), filling at the open of the bar at T_exp - 1 min (09:59 or 10:59); if that bar is missing, the first later present bar | C 462-463; S0.7 |
| Hold | 299 minutes | C 464 |
| Parameters (literals) | window start T_exp - 300 min, exit fill T_exp - 1 min; no grid | C 478-488 |
| Release instants read | none (a 07:30 CT release on d is held through at 1 lot-equivalent) | C 507-509 |
| Research window | every MBTX date in the window is a roll-blackout date (E.2a L-11), and 2025-11-28 and 2025-12-24 are also early halts, so the engine refuses every entry: expected 0 trades (K7-L-05) | C 489-497; C section 7 item 8 |
| Trials in N | 1 | C 516 |
| Topstep | last fill 09:59 (10:59) CT; market; one trade per event day | C 501-511 |

## 5. K7-rev2h-01 (two-hour reversal in the MBT day session). C lines 518-593

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | bitcoin MBT, q_c 1 | C 520-522 |
| Dates | every trade date d in CRYPTO_FULL_SESSIONS and not in VENDOR_DEGRADED | C4; S0.8 |
| Blocks | B1 = [08:30, 10:30), B2 = [10:30, 12:30), B3 = [12:30, 14:30), CT date d | C 548 |
| Decision 10:30 | r1 = close of the 10:29 bar - open of the 08:30 bar (ticks); target1 = -sign(r1) x q; 0 if r1 = 0, if the 08:30 or 10:29 bar is missing, or if the two carry different instrument_ids; the entry on the 10:30 bar is sent only if that bar carries their instrument_id (K7-L-06; amended after audit F-2) | C 549-550, 560-561; S0.9 |
| Decision 12:30 | r2 = close of the 12:29 bar - open of the 10:30 bar; target2 = -sign(r2) x q; 0 on r2 = 0, a missing endpoint, or the 10:30 and 12:29 bars carrying different instrument_ids; the entry on the 12:30 bar is sent only if that bar carries their instrument_id (K7-L-06; amended after audit F-2) | C 551-552, 560-561; S0.9 |
| Orders at each decision | computed at the close of the bar at decision - 1 min (10:29 or 12:29), with the account's position then: if target equals the position, hold; otherwise, if a position is open, a flatten intent on the bar at decision - 1 min (fills at the decision-time open; if that bar is missing, the first later present bar); then, if the target is nonzero, an entry intent on the decision-time bar (10:30 or 12:30; fills at 10:31 or 12:31), sent only if the account is then flat and the decision-time bar exists | C 553-558; C2 110-114; S0.6, S0.7 |
| Final exit | market intent on the 14:29 bar, filling at the 14:30 open; if missing, the first later present bar | C 559; S0.7 |
| Engine closure | a position closed by the engine before 12:30 leaves the account flat, and the 12:30 decision applies as written | K7-L-07 |
| Hold | 119-120 minutes per block, up to about 239 if target2 equals target1 | C 562-563 |
| Parameters (literals) | block 120 minutes, threshold 0, anchor 08:30, hold one block; no grid | C 568-578 |
| Release instants read | none; fills at 10:30, 10:31, 12:30, 12:31, 14:30 are in no release minute | C 588-589 |
| Trials in N | 1 | C 593 |
| Topstep | last fill 14:30; at most 2 entries a day; B3 spans FOMC at 1 lot-equivalent | C 582-591 |

## 6. K7-montrend-01 (Sunday-evening hourly time-series momentum on the Monday trade date). C lines 595-694

| Field | Rule | Reference |
|---|---|---|
| Exposure, vehicle | bitcoin MBT, q_c 1 | C 599-601 |
| Dates | trade dates d that are Mondays, in CRYPTO_FULL_SESSIONS and not in VENDOR_DEGRADED (a booked-forward Monday is not a trade date and does not trade) | C 634-635; S0.8 |
| Decision times | 20: Sunday (CT date d-1) 18:00, 19:00, 20:00, 21:00, 22:00, 23:00; Monday (CT date d) 00:00, 01:00, ..., 13:00 | C 636-637 |
| Signal at t | s_t = sign(close of the bar at t - 1 min - open of the bar at t - 60 min), in ticks; s_t = 0 if either bar is missing or they carry different instrument_ids | C 638-640 |
| Flatten | at the close of the bar at t - 1 min: if a position is open and its sign differs from s_t (including s_t = 0), a flatten intent on that bar (fills at the open of the bar at t); if that bar is missing, the first later present bar | C 642-643; S0.7 |
| Entry | on the bar at t: if s_t is nonzero, the account is flat (no position, no pending order), and the bar at t exists and carries the instrument_id of the two signal bars, an entry intent in direction s_t (fills at t + 1 min) | C 644-645; S0.6, S0.9 |
| Hold | if s_t equals the open position's sign, hold | C 646 |
| Final exit | market intent on Monday's 13:59 bar, filling at the 14:00 open; if missing, the first later present bar | C 647; S0.7 |
| Bars never read | anything before Sunday 17:00 CT (the weekend bars that carry Monday's trade date from 2026-06-01) | C 619-626; K7-L-01 |
| Engine closure | a position closed by the engine leaves the account flat, and later decisions apply as written | K7-L-07 |
| Hold | at least 59 minutes per position | C 648 |
| Parameters (literals) | start Sunday 18:00, last decision Monday 13:00, flat 14:00, lookback 60 minutes, step 60 minutes, threshold 0; no grid | C 654-667 |
| Release instants read | none; fills at hh:00 or hh:01 miss [07:30, 08:00) | C 684-686 |
| Trials in N | 1 | C 694 |
| Topstep | last fill Monday 14:00; at most 20 entries; no fill in the first 60 minutes after the Sunday reopen | C 676-687 |

---

## 7. Trial count

6 declarations (S0.2), all on bitcoin MBT: 3 ports + 3 new. This matches the E.1 JSON exposure table
(reports/stage_e1_changes.md line 1866: bitcoin 6 members, 6 trials) and the prompt's expectation.
Program N after K7: 150 + the K7 trials screened (the lead takes the count from the freeze
declarations; a trial counts when the runner writes its screen record, as E.4 counted: K7-L-05).

## 8. Lead readings (each is also an open choice in reports/E.6_RETURN.md section 6)

Adopted from earlier clusters (the text is the same): E.3-L-01 (literal tables), E.3-L-03 (the bar at
hh:mm is on CT date d), E.3-L-04 (named entry bar exact), E.3-L-05 (CP1's first bar is the 17:00 bar of
CT date d-1), E.3-L-06 (CP1's guard is D6's), E.3-L-07 (CP2 counts present bars, no C-2 exit), E.3-L-08
(CP2's range from present bars; the first qualifying bar uses the day's entry), E.3-L-09 (CP3 by Family
H), E.3-L-10 (CP3 exits at the first bar at or after C-2), E.3-L-11 (early halt = the bar's
early_halt_ct), E.3-L-13 (C4's "entry bar" is the bar the entry intent is emitted on; E.3-L-12's
entry-bar gate is not the same text in K7, whose C4 names the signal bars of one computation: it is
taken as K7-L-06's own reading, audit F-2), E.3-L-17 (fixed trading_windows measured on every date), E.3-L-19 (integer vendor ticks),
E.3-L-20 (undersized vehicles are screened), E.3-L-22 (a refused exit is resent), K4-L-01 (tables span
the whole period; only research-window rows are checked), K4-L-06 (CP2's buffer as 4 x vendor_tick),
K4-L-13 (full-session table over EC-CAL's coverage only), K3-L-11 (an early engine F is an early close
for C4).

New readings for K7:
- **K7-L-01 The program trade-date convention by clock.** C3 (lines 115-126) keeps [d-1 17:00, d 16:00)
  CT in both regimes, while the bars carry CME's trade date (weekends from 2026-06-01, and the seven
  booked-forward holidays in the window, whose session carries the next business day's trade date:
  data/group_session.py lines 32-37, lead rulings E.2a L-9 and L-10). Every member therefore selects a
  bar by CT date and clock, never by trade_date and clock alone, and reads nothing outside
  [d-1 17:00, d 16:00) CT. Consequences: CP1's first bar after a booked-forward Monday is the Monday
  17:00 bar; CP3's d-1 after a booked-forward Monday is the Friday before; montrend never reads weekend
  bars. Not adopted: CME's assignment, which C3 and C section 7 item 2 name and reject.
- **K7-L-02 CRYPTO_FULL_SESSIONS** = EC-CAL crypto trade dates with no early halt and the regular engine
  F on CT date d, 2019-05-01..2026-06-19 (K3-L-11, K4-L-13).
- **K7-L-03 Vendor-degraded dates are excluded by a literal table.** C4 (lines 127-133) says the three new
  members do not trade on vendor-degraded dates. The engine masks the per-bar flag (hindsight, interface
  lines 8-9) and the runner's window does not remove those dates (screening/stage_e_align.py lines
  57-78), so a member that ignored the clause would trade dates its entry excludes. VENDOR_DEGRADED is
  therefore a literal table built from the two frozen-on-disk Databento condition files with the bar
  builder's mapping (a trade date whose ISO date is a degraded UTC date), 2019-05-01..2026-06-19. It
  only removes trade dates (never adds or times a trade), so it cannot widen a rule; it is a data-quality
  exclusion fixed before any result, as D.1f and D15.3 exclude such dates. Research-window effect: rev2h
  loses 2025-09-17, 2025-09-24, 2026-03-16, 2026-04-10 (2025-11-28 is an early halt anyway); montrend
  loses Monday 2026-03-16; expiry none. Flagged for the user: the ports and other clusters' new members
  trade these dates (their texts do not name them).
- **K7-L-04 MBTX by the rule, 2021-05..2026-06.** Generated from the rule and the holiday lists C9 names;
  T_exp by zoneinfo; research-window rows amended by Task 1b's verdicts (section 9); earlier rows kept
  and unchecked (K4-L-01).
- **K7-L-05 K7-expiry-01 is coded and run as frozen.** C section 7 item 8 (lines 992-995) gives the lead,
  before screening, the choice to withdraw it (logged) if no expiry day survives the roll blackout, or to
  change MBT's roll convention. E.2a L-11 shows none survives in the research window. The roll convention
  is harness (frozen; this stage may not change it), and withdrawal would remove a frozen hypothesis the
  prompt counts among its 6 trials. The member is implementable as written, so it is coded, audited,
  frozen and run once; the runner's record will show its trades (expected 0: the engine refuses each open
  by name). Pre-declared before any run: a trial counts in N when the runner writes its screen record
  (status "run"), as E.4 counted screened trials; a trial the runner excludes before screening
  (coverage) or refuses does not count. A zero-trade series has mean 0 and fails D5's screen (Tier B).
  Flagged for the user: whether a K7-expiry-01 confirmation run is meaningful depends on how many
  confirmation-window expiry days survive MBT.v.0's roll blackout (Task 1b item E could not compute it:
  no 2019-2024 MBT roll metadata is on disk). Consequence (added after audit F-5): C section 7 item 8
  offered withdrawal or a different roll convention; this third course changes nothing in the frozen
  entry, and the trial adds 1 to N with a certain screen fail, which is conservative for the other five.
- **K7-L-06 rev2h's and montrend's guard.** The two signal endpoints must carry one instrument_id (the
  entries' own "instrument change between endpoints" and "carry different instrument_ids" clauses, and
  C4's "signal bars of one computation"), else the target is 0. In addition, an entry intent is sent only
  if its own bar carries the endpoints' instrument_id: a K7 narrowing (fewer entries, never more), taken
  as this reading's own and not as E.3-L-12's text (audit F-2). The flatten or hold is decided at the
  decision - 1 bar's close, before the entry bar exists, so the entry bar gates only the entry. It cannot
  bind on real MBT bars: MBT.v.0 changes instrument_id at 00:00 UTC on a splice trade date, which is a
  roll-blackout date, and the engine refuses a position across a change. Exits and flattens are
  unguarded.
- **K7-L-07 Engine closures in the multi-decision members.** rev2h and montrend compare each decision's
  target with the account's position at that decision; a position the engine closed (D9.7, F, MLL) leaves
  the account flat, and the rule applies as written at the next decision (E.4's ovr reading). The ports
  and expiry make no further entry that day.
- **K7-L-08 rev2h's orders are computed on the bar at decision - 1 min.** r uses that bar's close, so the
  target and any flatten are decided at its close (10:30 or 12:30), and the entry goes on the next bar
  (C2 lines 110-114). A missing decision-1 bar gives target 0 and a flatten on the first later present
  bar; a missing decision-time bar gives no entry (S0.6).
- **K7-L-09 trading_windows** as S0.12: the ports as E.4; expiry and montrend exactly as their entries
  state the coverage window (C lines 513-514, 691-692), expiry's over both T_exp slots; rev2h from its
  first signal bar to its exit fill bar.
- **K7-L-10 6 declarations**, ordinals in catalog order.
- **K7-L-11 Two coders, two or more test files** (tests/test_k7_members*.py), as E.3-L-21: coder A the
  ports (tests/test_k7_members_ports*.py), coder B the new members and the tables
  (tests/test_k7_members_events*.py).
- **K7-L-12 C section 7 settled by the frozen text:** item 1 (24/7 confirmed; no design change here);
  item 2 (the program convention, K7-L-01); item 3 (regime mismatch: a label for the confirmation
  session); item 4 (short history: the start rule's, later); item 5 (overnight coverage: the runner's
  D9 check on S0.12's windows; no fallback is written); item 6 (low frequency: kept, the power check
  decides later); item 7 (ML, excluded); item 8 (K7-L-05); item 9 (cost sample: reported as a
  limitation of montrend and expiry, D8 frozen); items 10-12 (no action); item 13 (a) and (f) Task 1b,
  (e) the runner's coverage, (g) the calendar facts above; (added after audit F-4) (b) moot, since no K7
  member reads a release; (c) MBT's tick history 2021-05..2026-06 is a confirmation-session check, the
  research window uses the frozen 5.00; (d) settled by the harness: MBT has only CME's dynamic circuit
  breaker in rules/price_limits.py, so D9.7 does not fire on it, as C13 assumes; (h) moot, D1's five
  calibration dates predate the change.

## 9. The research-window check and the rulings (lead, 21:47 PDT, after Task 1b)

Source: reports/stage_e6_release_check.md and .json (ReleaseChecker-OpusMed, 21:31-21:47 PDT).

- **R-1b-1 MBTX.** CME's MBT rule (Rulebook ch. 348, 34802.F, captures 2023-12-03, 2024-02-18, 2026-01-09) now ends
  trading "on the last Friday of the contract month if that day is a business day in either the UK or the US"; the
  catalog quotes the older "both" wording (C9 lines 176-180; ch. 348 read "both" on 2021-06-18). With the checker's
  holiday lists the catalog's rule reproduces the catalog's own 14 research and 34 confirmation dates, and differs from
  CME's calendar captures only in 2021-12 (CME 2021-12-31; rule 2021-12-30) and 2025-12 (CME 2025-12-26 in the
  2024-09-29 capture; rule 2025-12-24). Ruling: the table is the rule's rows less exactly those two, which are DROPPED
  (each is not a final trading day); CME's 2025-12-26 and 2021-12-31 are NOT added. Reason: C9 has E.2 confirm the
  rule's dates against CME's calendar, not supply new ones, and the prompt's verdicts are keep, drop or unverifiable;
  adding a date would widen the frozen list (the narrowest reading). Research window: keep 3 (2025-06-27, 2025-09-26,
  2026-03-27), drop 1 (2025-12-24), unverifiable 10, kept as the rule gives them (the Task 1b failure path), so
  K7-expiry-01 carries "calendar partly unverified". T_exp: 11:00 CT on 2025-10-31 and 2026-03-27, 10:00 CT otherwise
  (zoneinfo). Final settlement "the BRR published at 4 p.m. London time on the Last Trade Date" (R3). Confirmation rows
  other than 2021-12-30 are kept unchecked (K4-L-01); under both wordings they are identical. Flagged for the user:
  replacing instead of dropping would add one confirmation event (2021-12-31); in the research window it is moot.
- **R-1b-2 Mondays.** Of 63 Mondays 2025-04-07..2026-06-15, five are not trade dates (the booked-forward holidays
  2025-05-26, 2025-09-01, 2026-01-19, 2026-02-16, 2026-05-25); every other Monday is a full session with the regular F.
  K7-montrend-01 trades none of the five (spec section 6); VENDOR_DEGRADED removes 2026-03-16; the runner removes roll
  blackouts. CME's Sunday 17:00 CT open before the change and continuous trading from Friday 2026-05-29 16:00 CT are
  cited from the E.2a records (item B).
- **R-1b-3 The L-9 guard holds as the prompt defines it.** No MBT bar booked to a trade date on or after 2026-06-22 is in
  the research file (the 1,617 such bars were dropped at build), and data/stage_e_bars.py refuses the whole leg if any
  row books to a holdout-1 trade date; the guard tests pass (49). Bars of trade date 2026-06-18 (UR-1) are loaded and
  delivered to members as grid minutes but are not a window date, so the engine refuses any opening there by name
  (engine_not_a_window_date), and no position can be carried into them (the engine flattens by F on 2026-06-17). They are
  therefore visible but untradable, like roll-blackout bars. No action.
- **R-1b-4 Roll blackout of the expiry days.** 0 of 14 research-window MBTX dates survive the roll blackout (item E):
  K7-L-05's expectation stands (0 trades). The confirmation-window count cannot be computed from the files on disk (no
  2019-2024 MBT roll metadata); it is a question for the confirmation session and the user.
