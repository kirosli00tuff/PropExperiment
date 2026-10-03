# Stage E.10 Task 1: the K9 design target and the exclusion list

Written by the lead (Opus 5.5, xhigh), 2026-10-02 22:40-23:10 PDT, **before any literature source is
read**. Every number below traces to a frozen table (reports/stage_e2a_costs.json,
reports/stage_e2a_epsilon.json, docs/STAGE_E_DESIGN.md D2-D9, reports/stage_e0_topstep_facts.json)
or to a design rule stated here. No bar, quote, cost sample or Stage E screen figure was read.
Machine-readable cost wall: reports/stage_e10_research/cost_wall.json (script
reports/stage_e10_briefs/cost_wall.py; input sha256 values recorded in the JSON).

---

## (a) The cost wall per traded exposure

### Rules (fixed here)

- **RT_X** (round-trip cost wall, ticks per contract of the vehicle) = Topstep round-turn commission
  in ticks + 2 x the largest one-side slippage of any 30-minute bucket of the vehicle (D8). This is the
  worst entry/exit bucket pair, so it holds whatever entry time a member uses (the 17:00 CT reopen
  bucket included) and it equals D8's event-window round turn. For MYM it is 0.33 ticks above
  the JSON's event-window figure, because the script takes the larger of the buy and sell side per
  bucket. That is the conservative reading.
- **M_X = 3 x RT_X**: the minimum gross move per trade a K9 member must target (prompt rule).
- **G_X(f) = eps_X / f + RT_X**: the gross move per trade a member trading on a fraction f of trade
  dates needs to net eps_X per trade date, with zeros on no-trade dates (C11's arithmetic: net per
  trade = (dates / trades) x eps_X). Shown at f = 0.40 (the cap, two entries a week), 0.20 (one a
  week) and 0.10 (30 trips in 299 dates, the proposed floor in (d)).
- eps_X is the operative eps (D3: min of translated and funnel-derived, reports/stage_e2a_epsilon.md).
- Context column only: G / E|m_1|, where E|m_1| is the vehicle's mean absolute day-session move
  (O_X to C_X, ticks per contract) from the frozen E.2a epsilon report (D2/D3 sizing input). **No
  member literal may be derived from E|m_1|.** It is shown only to judge whether a target is
  reachable at all.

### Table (ticks per contract of the vehicle; $ at q_c)

| Cl | Exposure | Veh | q_c | eps_X | comm | max side | RT_X | day RT (mean) | M_X | G(0.4) | G(0.2) | G(0.1) | $ G(0.4) at q_c | G(0.4)/E\|m1\| | G(0.2)/E\|m1\| |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K1 | Nasdaq-100 | MNQ | 1 | 170 | 2.44 | 1.49 | 5.41 | 4.12 | 16.2 | 430.4 | 855.4 | 1705.4 | 215 | 0.59 | 1.18 |
| K1 | Russell 2000 | M2K | 3 | 50 | 2.44 | 1.95 | 6.35 | 3.95 | 19.0 | 131.3 | 256.3 | 506.3 | 197 | 0.62 | 1.21 |
| K1 | Dow | MYM | 3 | 56 | 2.44 | 2.54 | 7.52 | 3.98 | 22.6 | 147.5 | 287.5 | 567.5 | 221 | 0.56 | 1.10 |
| K2 | 2-year | ZT | 1 | 5 | 0.30 | 0.51 | 1.32 | 1.30 | 4.0 | 13.8 | 26.3 | 51.3 | 108 | 0.96 | 1.83 |
| K2 | 5-year | ZF | 1 | 6 | 0.30 | 0.51 | 1.31 | 1.30 | 3.9 | 16.3 | 31.3 | 61.3 | 127 | 0.94 | 1.80 |
| K2 | 10-year | ZN | 1 | 3 | 0.17 | 0.50 | 1.17 | 1.17 | 3.5 | 8.7 | 16.2 | 31.2 | 135 | 0.66 | 1.23 |
| K2 | Ultra 10-year | TN | 1 | 4 | 0.17 | 0.53 | 1.24 | 1.17 | 3.7 | 11.2 | 21.2 | 41.2 | 176 | 0.68 | 1.28 |
| K2 | Bond | ZB | 1 | 2 | 0.09 | 0.52 | 1.12 | 1.09 | 3.4 | 6.1 | 11.1 | 21.1 | 191 | 0.48 | 0.86 |
| K2 | Ultra bond | UB | 1 | 2 | 0.09 | 0.51 | 1.12 | 1.10 | 3.4 | 6.1 | 11.1 | 21.1 | 191 | 0.38 | 0.69 |
| K3 | EUR | 6E | 1 | 12 | 0.68 | 0.81 | 2.31 | 1.94 | 6.9 | 32.3 | 62.3 | 122.3 | 202 | 0.63 | 1.22 |
| K3 | AUD | 6A | 1 | 11 | 0.84 | 0.82 | 2.48 | 2.19 | 7.4 | 30.0 | 57.5 | 112.5 | 150 | 0.82 | 1.56 |
| K3 | GBP | 6B | 1 | 8 | 0.68 | 0.68 | 2.03 | 1.92 | 6.1 | 22.0 | 42.0 | 82.0 | 138 | 0.74 | 1.41 |
| K3 | CAD | 6C | 1 | 9 | 0.84 | 0.69 | 2.21 | 2.03 | 6.6 | 24.7 | 47.2 | 92.2 | 124 | 1.03 | 1.96 |
| K3 | JPY | 6J | 1 | 10 | 0.68 | 0.71 | 2.10 | 1.89 | 6.3 | 27.1 | 52.1 | 102.1 | 169 | 0.83 | 1.59 |
| K3 | CHF | 6S | 1 | 13 | 0.68 | 1.65 | 3.98 | 2.65 | 11.9 | 36.5 | 69.0 | 134.0 | 228 | 0.56 | 1.05 |
| K3 | NZD | 6N | 1 | 10 | 0.84 | 0.89 | 2.62 | 2.25 | 7.9 | 27.6 | 52.6 | 102.6 | 138 | 0.88 | 1.68 |
| K4 | WTI crude | MCL | 4 | 21 | 1.72 | 1.31 | 4.35 | 3.17 | 13.0 | 56.8 | 109.3 | 214.3 | 227 | 0.62 | 1.19 |
| K4 | Henry Hub gas | NG | 1 | 8 | 0.42 | 0.99 | 2.41 | 1.67 | 7.2 | 22.4 | 42.4 | 82.4 | 224 | 0.35 | 0.66 |
| K5 | gold | MGC | 1 | 71 | 1.92 | 1.84 | 5.60 | 4.09 | 16.8 | 183.1 | 360.6 | 715.6 | 183 | 0.71 | 1.39 |
| K5 | copper | MHG | 2 | 27 | 1.54 | 1.74 | 5.01 | 3.70 | 15.0 | 72.5 | 140.0 | 275.0 | 181 | 0.82 | 1.59 |
| K6 | corn | ZC | 1 | 4 | 0.42 | 0.54 | 1.50 | 1.43 | 4.5 | 11.5 | 21.5 | 41.5 | 144 | 0.91 | 1.70 |
| K6 | wheat | ZW | 1 | 4 | 0.42 | 0.64 | 1.69 | 1.48 | 5.1 | 11.7 | 21.7 | 41.7 | 146 | 0.62 | 1.16 |
| K6 | soybeans | ZS | 1 | 5 | 0.42 | 0.61 | 1.64 | 1.47 | 4.9 | 14.1 | 26.6 | 51.6 | 177 | 0.58 | 1.09 |
| K6 | soybean meal | ZM | 1 | 5 | 0.53 | 0.63 | 1.79 | 1.61 | 5.4 | 14.3 | 26.8 | 51.8 | 143 | 0.67 | 1.26 |
| K6 | soybean oil | ZL | 1 | 11 | 0.88 | 0.90 | 2.67 | 2.17 | 8.0 | 30.2 | 57.7 | 112.7 | 181 | 0.59 | 1.14 |
| K6 | lean hogs | HE | 1 | 7 | 0.52 | 0.72 | 1.97 | 1.86 | 5.9 | 19.5 | 37.0 | 72.0 | 195 | 0.60 | 1.14 |
| K6 | live cattle | LE | 1 | 8 | 0.52 | 0.99 | 2.50 | 2.39 | 7.5 | 22.5 | 42.5 | 82.5 | 225 | 0.32 | 0.60 |
| K7 | bitcoin | MBT | 1 | 90 | 5.64 | 2.61 | 10.87 | 8.85 | 32.6 | 235.9 | 460.9 | 910.9 | 118 | 0.98 | 1.91 |

Not traded in Stage E (no D2 candidate) and therefore not K9 exposures: RBOB, ULSD, silver (E.2a
vehicle table). The S&P 500 (MES, ES) is not a traded exposure (D1.5). M6E and M6A stay non-candidates
(U7).

### What the cost wall says (reading, for the catalog writer and the user)

1. **The round trip is not the binding constraint for full-session holds.** M_X ranges from 3.4 ticks
   (ZB, UB) to 32.6 ticks (MBT). A hold of several hours is exposed to a typical move many times
   that. Any source-documented effect of a few tenths of a percent per trade clears M_X on most
   exposures. The catalog must still show it per member, in the member's own units.
2. **The eps bar is the binding constraint.** A member trading on 40% of dates (two a week, the cap)
   needs a mean gross move per trade of 0.32-1.03 x E|m_1|; at one trade a week, 0.60-1.96 x. A
   mean net gain per trade near or above a typical absolute session move is not plausible for any
   published effect. So a single K9 trial is very unlikely to reach eps_X on its own. The realistic
   K9 outcome is a statistically supported edge below eps_X per trial, which matters as a component
   of a portfolio (V20's ML route v2 builds that combination) and not as a stand-alone funnel pass.
   The design draft states this plainly for the user (decision point in docs/STAGE_E_DESIGN_K9_DRAFT.md).
3. Consequence for member design: prefer conditions that fire near the upper end of the band (one to
   two trades a week) over very rare conditions. A rarer condition raises G(f) in proportion and
   lowers the trip count toward the floor in (d).

---

## (b) The shape every K9 member must have

1. **Frequency.** At most two entries per product per calendar week (Monday-Friday by trade date). If
   a rule's condition would fire a third time in a week, the third and later signals are skipped
   (first come, first taken). The expected trip count on the 299-date research window must be at
   least 40 by calendar arithmetic, or by construction for state conditions defined as trailing
   percentiles (rule D-pct below). 40 is a one-third margin over the proposed 30-trip floor.
2. **One position at a time** per member per product. No pyramiding, no reversal inside a trip.
3. **Inside one trade date.** Entry at or after the trade date's first bar and exit no later than F.
   The trade date's first bar is 17:00 CT of the prior calendar day for products that trade from the
   17:00 CT Globex open (equity index, rates, FX, energy, metals, crypto). For grains it is the
   19:00 CT overnight open. Livestock has no overnight session, so its first bar is 08:30 CT.
4. **Hold at least two hours** from fill to exit, by rule construction (not only on average).
5. **Flat by F** (D9.1): 15:08 CT for products trading through 15:10 CT, 13:18 CT for grains and
   13:03 CT for livestock. On CME early-close days, F is 15 minutes before the early close. A grain
   position may not be held into the 07:45 CT CBOT pause: an overnight grain trip exits by 07:43 CT,
   and a day-session grain trip runs from 08:30 CT. No grain trip spans the pause, so the longest grain
   holds are 19:00-07:43 or 08:30-13:18.
6. **Market orders** (D9.2), no stops, targets or brackets (D9.4).
7. **Size q_c** of the exposure's D2 vehicle (table above). Never above q_c, and at most one
   lot-equivalent (D9.5).
8. **Every D9 constraint**: the event-minute fill guard (5a), the CPI window (12; no opening fill in
   [CPI - 5, CPI + 5] min on the starred minis and capped size on micros), price-limit proximity (7;
   long holds after volatile days meet the 2% zone more often, so every member records its D9.7 exits),
   volatility position caps (11), holidays (13), the trade-rate floor (3; trivially met by holds of
   two hours or more), roll blackouts (D4).
9. **Signals from admissible inputs only**: the vehicle's own one-minute bars (the program's ohlcv-1m
   store), public calendars, and public daily series with a free history and a documented
   publication time (look-ahead stated per member). A member needing deferred-contract (curve) bars, or
   a series the program does not hold, names the data item for E.11/E.12 and is flagged. Nothing is
   bought in E.10.

### Default definitions (design rules, used only where a source gives no definition)

- **D-ret**: the close of trade date d, C_d = close of the bar at C_X - 1 min (CP3's convention).
  The day-session return of d = C_d / open(O_X bar of d) - 1. The overnight return of d =
  open(O_X bar of d) / C_{d-1} - 1. The close-to-close return of d = C_d / C_{d-1} - 1. All prices come
  from the vehicle's own bars, with the instrument guard as in Family H (no return across a contract
  change).
- **D-rng**: the day range of d = (H_d - L_d) / C_d over [O_X, C_X) (CP3's daily bar).
- **D-pct**: "extreme" means at or above the 80th percentile (or at or below the 20th) of the same
  statistic over the trailing 250 completed trade dates before d, computed from prior dates only. The
  80/20 cut makes a one-sided condition fire on about 20% of dates (about one a week) by
  construction. 250 is one year of trade dates. Both are fixed here, not tuned.
- **D-exit**: if a source measures its effect to the close or settlement, exit by market intent on the
  first bar at or after C_X - 2 min (the ports' convention). If it measures over the full trade date,
  exit at F. Otherwise exit at the source's stated time.
- **D-entry**: if a source measures from the prior close, entry is the trade date's first bar after the
  decision time (on the 17:00 CT reopen this is the first bar at or after 17:00 CT). If it measures from
  the open, entry is the O_X bar. Otherwise entry is at the source's stated time.
- **D-wk**: the weekly cap in (b)1.
- **No grids**: one literal set per member. A trial is one (member, exposure) pair.

---

## (c) The exclusion list: families Stage E already tested, by mechanism

Sources: the member headings and one-line mechanisms of reports/stage_e0_catalog_K1.md to K8.md
(sections 1 and 2) and D6. A K9 member must differ from each family below **in mechanism**, not only
in parameters, conditioning frequency, product or holding time.

| # | Family (mechanism) | Members tested (E.3-E.9) | What a K9 member may NOT be |
|---|---|---|---|
| X1 | Intraday momentum: the overnight plus first-half-hour return predicts the last half hour (Gao-Han-Li-Zhou) | CP1 on every exposure | any "early-session return predicts the later session" rule, conditioned or not |
| X2 | Opening-range breakout: break of the first 15-minute range, held 75 minutes | CP2 on every exposure | a breakout of an intraday range, with or without a volatility gate (a gate alone is a parameter) |
| X3 | Prior-close location: the prior day's close position in its range (CLV >= 0.8 buy, <= 0.2 sell) sets the next day session's direction | CP3 on every exposure | a rule signed by where the prior close sits in the prior range |
| X4 | Pre-release informed-trading drift: follow the pre-release move into a scheduled release | K1-predrift, K2-predrift (ISM Services) | a pre-release drift on any release, unless the mechanism is shown to differ |
| X5 | Treasury auction cycle: pre-auction concession, post-auction recovery | K2-aucpre, K2-aucpost | any auction-cycle trade |
| X6 | Post-announcement continuation or drift after FOMC | K2-fomcpost (rates), K5-fomc (gold) | post-FOMC drift on any product |
| X7 | Energy inventory releases: NG storage-day short, storage-response reversal, API-to-EIA continuation, post-WPSR fade, WPSR half-hour to last half-hour | K4-ngpre, K4-ngrev (excluded at E.0 review), K4-apipre, K4-eiafade, K4-eiamom | any trade keyed to the weekly EIA/API release times |
| X8 | USDA WASDE: pre-release drift continuation, post-release continuation | K6-wasdepre, K6-wasdepost | any WASDE-keyed trade |
| X9 | Benchmark fixes and auctions: London 4 p.m. fix (reversal, front-running, month-end hedge), ECB fix, Tokyo fix (gotobi, daily), LBMA gold/silver auctions | K3-ldnrev, K3-ldnmom, K3-mehedge, K3-ecbfix, K3-tkypre, K3-tkypost, K5-preauc, K5-pmfix | any fix- or auction-timed trade |
| X10 | Overreaction reversal: fade a large recent move (hourly overreaction, two-hour reversal, VXN-band breach fade, VWAP stop-and-reverse, crush-margin overnight gap reversal) | K4-ovr, K5-ovr, K6-ovr, K7-rev2h, K1-vxnband, K1-vwap, K6-crushgap | a fade of a large prior move at any frequency (hourly, overnight gap, daily): "reversal after an extreme move" at the daily scale is the same mechanism at a different frequency |
| X11 | Continuation after a limit close | K6-limitcont | continuation keyed to a limit move |
| X12 | Month-end flows: index-extension demand, month-end FX hedging | K2-monthend, K3-mehedge, K3-ldnrev | any turn-of-month or month-end trade |
| X13 | Roll and expiry: BRR final-settlement expiry; index-roll members (excluded at E.0 for flat-by-F) | K7-expiry; K4/K5/K6-idxroll, K2-rollspread (not tested) | a trade keyed to a futures expiry, roll window or index roll |
| X14 | Cross-market leads: S&P extreme 5-minute drop to gold, crude to CAD, weekend bitcoin to Monday Nasdaq-100 | K8-flight, K8-oilcad, K8-wkndbtc | a signal read from another market's move (the K8 class; V16) |
| X15 | Monday trend window: Sunday-evening hourly time-series momentum on the Monday trade date (MBT) | K7-montrend | hourly TSMOM on Monday; a day-of-week member must have a different mechanism (a weekly seasonal or weekend-risk premium, not trend) |

E.0's excluded entries (section 2 of each catalog) were never tested. A K9 member may revisit one
only if it states why E.0's failure reason no longer applies. Most failed on flat-by-F, proprietary
data or missing parameters, and those reasons still bind.

Borderline cases to be ruled per member in Task 4 (named now so they are not decided after reading
results):
- **Regime conditioning versus X10.** "Long the session after a volatility spike" differs from X10
  only if the mechanism is a state-dependent risk premium, with no fade of a specific move (the
  condition reads a volatility level, not the sign of the last move). A rule signed against the prior
  move is X10.
- **Range compression versus X2.** A breakout after a narrow-range day is X2 with a gate. A
  compression member qualifies only if its direction comes from a different mechanism, for example a
  drift signed by something other than the breakout.
- **Daily-scale TSMOM versus X1 and X15.** A trend over weeks or months, applied as a session hold,
  differs from X1 (overnight plus first half hour) and X15 (hourly, Mondays) in horizon and in
  mechanism (slow-moving capital and underreaction over weeks). It is admissible if sourced at that
  horizon.
- **Overnight-to-day continuation versus X1.** CP1's signal window includes the overnight return.
  A rule "the overnight return signs the day session" overlaps X1's signal and differs only in the
  holding window, so it is X1 unless its source states a different mechanism.

---

## (d) The proposed K9 screen (for the user to decide)

- **D5 as frozen**: research-window mean net P&L > 0 and daily t >= 1.0 (per contract, zeros on
  no-trade dates).
- **Plus a minimum trade count (V18)**, set here before any data is read: at least **30 completed
  round trips** per trial on the research window, counted after roll-blackout and data-quality
  exclusions. A trial below 30 is "insufficient trades" and goes to Tier B (null side only).

Arithmetic on the 299-date research window (316 trade dates less 15 roll-blackout dates and 2 UR-1
dates, the count used since E.3):
- 30 trips in 299 dates is a trade on 10.0% of dates, about one every two weeks. The cap of two a week
  gives at most about 0.40 x 299 = 120 trips.
- With k trips of per-trip mean mu and standard deviation sigma, and zeros elsewhere, the daily-series t
  is about sqrt(k) x mu / sqrt(sigma^2 + mu^2 (1 - k/n)), close to sqrt(k) x mu / sigma when mu is
  small. D5's t >= 1.0 then needs a per-trip mu/sigma of about 1/sqrt(k): 0.18 at k = 30, 0.13 at
  k = 60, 0.09 at k = 120. The edge chain's t > 3.0 (on the confirmation window) needs 3/sqrt(k_conf).
- **Why 30.** V18's failure was a pass on one trade: one positive date among n gives t =
  sqrt(n/(n-1)) >= 1.0 whatever its size. At k >= 30, a pass on one or two lucky trades needs those
  trades to outweigh 28 or more others, and the t-statistic's sampling distribution is close enough to
  normal for D5's one-sided reading. The floor also matches the frequency band in (b): any member
  meeting the shape's 40-trip expectation clears 30 unless its condition is far rarer in the window
  than its construction implies. That outcome is itself informative and is reported.
- Alternatives for the user: 20 trips (more members admissible, weaker protection) or 50 (protects
  better, and excludes conditions rarer than one a week).
