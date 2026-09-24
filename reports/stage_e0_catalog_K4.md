# Stage E.0 hypothesis catalog, cluster K4 (energy: CL, QM, MCL, NG, QG, MNG, RB, HO)

Writer: CatalogWriter-K4-OpusXHigh (Stage E.0 Task 4), 2026-09-23, from about 21:30 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any K4 product existed on this machine. It uses only these product-specific numbers:
- contract specifications and public ADV (reports/stage_e0_liquidity.json);
- Topstep's published fees, hours and release table (reports/stage_e0_topstep_facts.md);
- event-calendar metadata: EIA release dates and clock times, and the API release-time rule.

Calendar metadata carries no prices. No price level, range or volatility of any product is used or
assumed anywhere below.

**Inputs read in full:**
- reports/stage_e0_research_K4.md. The superseded sonnet log was not used.
- Every `[K4]`-tagged passage in the other logs: K3-007, K3-035 and K3-040 in
  reports/stage_e0_research_K3.md; K5-028 and K5-029 in reports/stage_e0_research_K5.md. The K2, K6
  and K7 logs hold none.
- reports/stage_e0_source_registry.jsonl (K4 lines and every line tagged K4).
- docs/STAGE_E_DESIGN.md (D1-D15, with the 21:12 amendments to D2 and D6).
- reports/stage_e0_partition.md.
- reports/stage_e0_topstep_facts.md.
- reports/stage_e0_liquidity.json (K4 rows).
- reports/stage_d1f_confirmation_list.md 2.1 A3.
- strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py.
- strategy/research/h_daily_bar/h6_prior_close_location.py.
- reports/stage_d1b_family_f_declaration.md F3.3.
- The D.1 literature log, row B4 only (K4-013 points there). The row is truncated in that file.
- reports/stage_e0_catalog_K2.md, for format only.

**Official pages fetched in this task** (curl, 2026-09-23 about 21:35-21:41 PDT). They were fetched
only to confirm release-time sources; no mechanism research was done:
- https://www.eia.gov/petroleum/supply/weekly/schedule.php (HTTP 200). It holds the 2024-2026
  exception table: "The standard release time and day of the week will be at 10:30 a.m. eastern time
  on Wednesdays with the following exceptions."
- https://ir.eia.gov/ngs/schedule.html (HTTP 200). It holds the 2025-2026 table: "The standard release
  time and day of the week will be at 10:30 a.m. eastern time on Thursdays with the following
  exceptions."
- Wayback CDX listings of both pages, which show one or more captures in every year 2019-2026
  (timestamps in C9). Two captures were opened:
  - http://web.archive.org/web/20200207151454/https://www.eia.gov/petroleum/supply/weekly/schedule.php
    (2019-2020 table);
  - http://web.archive.org/web/20210104203613/https://ir.eia.gov/ngs/schedule.html (2020-2021 table).
- https://www.eia.gov/petroleum/supply/weekly/archive/ (HTTP 200). Title "Weekly Petroleum Status
  Report Archives"; it lists release dates by year, 2011-2026.
- https://ir.eia.gov/ngs/ngs.html (HTTP 200). It links /ngs/ngshistory.xls and /ngs/schedule.html,
  with no archive of release dates.
- https://ir.eia.gov/ngs/archive.html (HTTP 403) and https://www.eia.gov/naturalgas/storage/archive/
  (HTTP 404).

---

## 0. Header

| Item | Value |
|---|---|
| Products | CL, QM, MCL, NG, QG, MNG, RB, HO (NYMEX; Topstep F1 "CME NYMEX Futures") |
| Exposures | WTI crude {CL, QM, MCL}; Henry Hub gas {NG, QG, MNG}; RBOB {RB}; ULSD {HO} (partition section 1) |
| D1 | **D1 applied: all four K4 exposures IN** (design D1 table). Admissible vehicles, 2026 Jan-Aug ADV: crude CL 1,079,857, MCL 252,100, QM 9,446; gas NG 521,792, MNG 14,942, QG 4,060; RB 206,850; HO 187,479 (the D1 table's figure) |
| Members | 10 = 6 new + 3 core ports + 1 ML member. Budget 15, so 5 slots are unused (section 3) |
| Trials in N (confirmation) | **21 if D2 admits all four exposures:** 12 port + 8 new + 1 ML. In general 3E + 5a_C + 3a_G + a_H, where E is the number of admitted exposures and a_C, a_G, a_H are 1 if crude, gas and ULSD are admitted (0 otherwise). Example: without RBOB and ULSD, 14 |
| ML grid | 48 configurations, counted only in the K4 screening session's research-window accounting (D15.8) |
| Starred products | **MCL** (Topstep F1: "Micro Crude Oil (MCL)*"). Its restriction is unresolved (D9.8; topstep facts F2 "not published"). Every crude member carries the flag. CL, QM, NG, QG, MNG, RB and HO are unstarred |
| D2 | Vehicle "D2 (chosen in E.2)" throughout. RB and HO each have one full-size contract. CL and NG may fail rho <= 2.0 at q = 1, leaving MCL/QM and MNG/QG as the vehicles. RB and HO may go untraded. Every entry is written for every exposure its evidence names, each marked **"traded only if D2 admits the exposure"** |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose
  ts_event (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values
  are usable from then on. Eastern-time releases convert to CT by subtracting one hour, since both
  zones change clocks on the same dates.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine
  convention D6 and D15.3 use). "Market intent on the bar at X" fills at the open of the bar at
  X + 1 min.
- **C3 Trade date.** d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md). The energy Globex
  session opens at 17:00 CT, so the first bar of trade date d is the 17:00 CT bar of d-1 (Sunday for
  a Monday).
- **C4 Exclusions for the six new members.** The ports follow D6 as written. A new member does not
  trade on:
  - roll-blackout dates (program convention, `screen_candidate` with `roll_blackout`);
  - dates the D10 energy calendar marks as early close or early halt ("Days with early_halt_ct set:
    no trade", Family H);
  - dates on which a bar the rule reads, or the entry bar, is missing, or on which the signal bars
    of one computation carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced
  flatten at F is the backstop. A CME circuit-breaker halt shows up as missing bars and is handled
  by the same rules.
- **C5 Flat time.** F = 15:08 CT (D9.1; D6 energy row: O = 08:00, C = 13:30, F = 15:08). No new
  member's last fill is later than 14:59 CT.
- **C6 Size.** q_c of the exposure's D2 vehicle, at most 1 lot-equivalent (D2 amended 21:12; D9.5).
  - Lot weights (D9.6): CL, QM, NG, QG, RB and HO count 1 each ("minis 1"). MCL and MNG count 0.1
    each.
  - Topstep's special-weighting list names only SIL, MBT and MET (F5), so no special weight for QM
    or QG is published. E.2 confirms how TopstepX counts them.
  - So q_c = 1 for a full-size or E-mini vehicle, and q_c <= 10 for a micro.
  - No member sizes by signal.
- **C7 Ticks and fees.** Tick sizes and values are from reports/stage_e0_liquidity.json (CME
  contract specifications, fetched 2026-09-23 20:33-20:47 PDT). Round turns are Topstep F3. The
  2026-10-01 fee rise is applied as D8 does.

  | Contract | Exposure | Tick | Tick value | Topstep round turn | Lot-equivalent |
  |---|---|---|---|---|---|
  | CL | crude | 0.01 | $10.00 | $4.02 | 1 |
  | QM | crude | 0.025 | $12.50 | $3.42 | 1 (E.2 confirms) |
  | MCL* | crude | 0.01 | $1.00 | $1.52; $1.72 from 2026-10-01 (D8) | 0.1 |
  | NG | gas | 0.001 | $10.00 | $4.22 | 1 |
  | QG | gas | 0.005 | $12.50 | $2.02 | 1 (E.2 confirms) |
  | MNG | gas | 0.001 | $1.00 | $1.72; $1.92 from 2026-10-01 (D8) | 0.1 |
  | RB | RBOB | 0.0001 | $4.20 | $4.02 | 1 |
  | HO | ULSD | 0.0001 | $4.20 | $4.02 | 1 |

  These are 2026 specifications. E.2 must confirm that each tick was unchanged over 2019-05..2026-06
  before any bar is read, because CP2's buffer and several ML features are in ticks.
- **C8 Price data.** Databento GLBX.MDP3 ohlcv-1m of the vehicle. It is paid: the research window is
  bought in E.1, and the confirmation and holdout-2 history of the chosen vehicle in E.2b (D13).
  - **History.** CL, QM, NG, QG, RB and HO from 2019-05. MCL was listed 2021-07-12 and MNG
    2023-11-06 (liquidity JSON listing dates). Earlier months quoted as "None of the symbols could
    be resolved" (D13).
  - **Short micro histories.** A micro vehicle's own confirmation history is therefore short. D2 and
    D4 let E.2 declare the full-size contract's bars as the price path, per exposure, before any
    confirmation read.
  - **Availability.** A bar is available at its close (C1).
  - **Tick-free rules.** Every new-member rule that compares a price change with a level uses a
    percent return or a sign, so it gives the same decision on any contract of an exposure. The
    tick-denominated quantities are CP2's buffer and the ML features (section 7, item 2).
  - **mbp-1** enters only through D8's shared five-date cost sample. No member reads order-book data.
- **C9 Event calendars.** All are external and free. Each rule reads only dates and scheduled clock
  times, never a released inventory value.
  - **EC-WPSR, EIA Weekly Petroleum Status Report release schedule.**
    - **Standard slot:** "10:30 a.m. eastern time on Wednesdays" = 09:30 CT (P-K4-017-b; confirmed
      on the page above).
    - **Exceptions:** holiday weeks move the release, for example 2019 "Thursday 11:00 a.m." (10:00
      CT, Wayback 2020 capture) and 2025-2026 "Thursday 12:00 p.m." (11:00 CT). One exception is
      "December 29, 2025 Monday 5:00 p.m." (16:00 CT, after F, so no member can trade it).
    - **Sources:** the current page, plus yearly Wayback captures 20190110082341, 20200207151454,
      20210120153010, 20220114004832, 20230113222513, 20240118235307, 20250110211433 and
      20260118223951.
    - **Actual publication dates:** https://www.eia.gov/petroleum/supply/weekly/archive/ (release
      dates by year).
    - **Notation:** T_W(d) is the release time in CT on d.
  - **EC-NGS, EIA Weekly Natural Gas Storage Report schedule.**
    - **Standard slot:** "10:30 a.m. eastern time on Thursdays" = 09:30 CT (P-K4-018-a).
    - **Exceptions:** for example "11/25/2020 Wednesday 12:00 p.m." (11:00 CT), "1/3/2020 Friday
      10:30 a.m.", "December 29, 2025 - (Updated) Monday 12:00 p.m."
    - **Sources:** the current page, plus yearly Wayback captures 20190111124957, 20200128214849,
      20210104203613, 20220114160745, 20230210074654, 20240607000738, 20250117233342 and
      20260126101407.
    - **Actual publication record:** E.2 sources it (for example Wayback captures of
      ir.eia.gov/ngs/ngs.html). ir.eia.gov/ngs/archive.html returned 403.
    - **Notation:** T_N(d) is the release time in CT on d.
  - **Availability rule for EC-WPSR and EC-NGS.**
    - **Timing:** each year's exception table is available early in the year. The captures listed
      date from January or February, except the 2024 storage capture (June).
    - **Mid-year changes** exist (the "(Updated)" entries). When each one was posted is not known
      here, hence the drop rule below.
    - **E.2 builds each table** from the last capture before each release, and cross-checks it
      against the record of actual publication.
    - **Dropped releases:**
      - a release whose actual date or time differs from its schedule entry;
      - a release marked "(Updated)" for which no capture dated before the member's entry time shows
        the update.

      A rule may time itself only on a release time it could have known that morning.
  - **EC-API, American Petroleum Institute bulletin timing (the rule only; no API data is read by
    any member).**
    - **The rule:** "the weekly reports are scheduled for release every Tuesday afternoon at
      approximately 4:30 pm Eastern. If Monday is a Federal holiday, the reports are scheduled for
      release on Wednesday afternoon" (P-K4-045-a), that is, Tuesday about 15:30 CT.
    - **Standard week (definition):** the WPSR is in its standard Wednesday 10:30 ET slot (not in
      that year's exception table), and the Tuesday before it is a full-session trade date in
      EC-CAL.
    - **Why the Monday-holiday case should drop out:** in the WPSR tables read here (2019-2020 and
      2024-2026), every Monday federal holiday moves the WPSR off its Wednesday slot. For example,
      in 2019 "Martin Luther King Jr.", "President's", "Memorial", "Labor", "Columbus" and
      "Veterans" each moved it to "Thursday 11:00 a.m.". So a standard week should never have the
      Wednesday API case. The 2021-2023 tables were not opened in E.0.
    - **E.2 check:** drop any standard week whose Monday is a US federal holiday, whatever the table
      says.
  - **EC-CAL.** The D10 energy calendar (trade dates, holidays, early closes and halts), built by
    E.2 from CME schedules.
  - **EC-NYSE.** NYSE full closures and early closes, used only by K4-eiamom-01. Free and published
    in advance. Not fetched in E.0; E.2 sources it (nyse.com hours-calendars, through Wayback for
    past years).
- **C10 Non-positive prices.** The log records a one-off WTI event on 2020-04-20 (R-K4-061,
  "Arbitrage breakdown in WTI crude oil futures: An analysis of the events on April 20, 2020").
  - That the front contract then traded at non-positive prices is a public fact not verified in
    E.0. E.2 sees it in the bars, if it is there.
  - Every percent return below is (P1 - P0) / P0 and requires P0 > 0; otherwise the rule does not
    trade.
  - Tick differences, the ports and the ML features are unaffected.
- **C11 Frequency (arithmetic from calendar counts, no price data).**
  - **Research window:** 2025-04-01..2026-06-19 has 319 weekdays (about 305 CME trade dates), 64
    Wednesdays and 64 Thursdays. Eight WPSR exceptions fall inside it (2025-05-29, 09-04, 10-16,
    11-13, 12-29; 2026-01-22, 02-19, 05-28), so there are about 56 standard-Wednesday releases.
    About 64 storage releases fall inside it, 5 of them off the Thursday slot (2025-06-18, 11-14,
    11-26, 12-29, 12-31).
  - **Confirmation window:** 2019-05-06..2024-02-29 (the earliest S_X) has 1,259 weekdays and 252
    Wednesdays.
  - **Consequence:** a member trading on k of about 305 research dates, with zeros on the rest (D5),
    needs a net P&L per event of about (305 / k) x eps_X to reach eps_X per trade date. The weekly
    event members (k about 55-64) need about 5 x eps_X per event; K4-eiafade-01 (k about 14, a
    passage-based estimate in its entry) needs about 20 x (section 7, item 4).
- **C12 Release-minute cost.** D8's five calibration dates are all Wednesdays, so crude's 09:30
  bucket contains the WPSR on every date (conservative for crude members). The Thursday gas-storage
  release never appears in the sample, so the gas vehicle's 09:30 bucket is calibrated on
  non-release minutes and may understate K4-ngrev-01's and K4-ngpre-01's release-window cost
  (section 7, item 5).
- **C13 Price-limit proximity (D9.7) for NYMEX energy.**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  - **Premise:** these products carry dynamic circuit breakers rather than fixed daily price limits
    (lead's brief; not verified in E.0).
  - **What E.2 must do:**
    - (a) Read CME's NYMEX price-fluctuation and circuit-breaker rules for CL, QM, MCL, NG, QG, MNG,
      RB and HO as they stood over 2019-2026.
    - (b) Decide, with the user, whether Topstep's "Holding a position within 2% of a product's
      price lock limit" [F2.1] applies to a dynamic band. If it does, encode it as D9.7 does: no
      entry, and an immediate exit, while the price is within 2% of the band edge.
    - (c) Confirm that halts produce missing bars, which C4 handles.
  - **Assumption:** the catalog assumes no limit either way.

---

## 1. Members

### K4-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K4. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures and admissible contracts** (each a separate trial): crude {CL, QM, MCL}, gas
  {NG, QG, MNG}, RBOB {RB}, ULSD {HO}. Each is traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1
  log A10 and A28; reports/stage_d1b_family_f_declaration.md F3.3), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the
    trade date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open),
    in the signal's direction; zero signal, no trade. Exit: market intent on the first bar at or
    after C-2 min (fills at the next open). Both signal bars must exist with one instrument_id, else
    no trade."
  - **K4 log:** K4-037 (USO: the first half-hour return, mostly its overnight part, predicts the last
    half-hour, P-K4-037-a) is this mechanism on a crude vehicle and is recorded as **covered by
    CP1**. K5-028's same-day continuation for oil (P-K5-028-a [K4]) is in the same family (section
    5).
- **Instantiated with the D6 energy row (O = 08:00, C = 13:30, F = 15:08):**
  - **Signal:** close of the bar at 08:29 minus the open of the trade date's first bar (the 17:00 CT
    bar of d-1, C3).
  - **Entry:** market intent on the bar at 12:59, filling at the 13:00 open.
  - **Exit:** market intent on the first bar at or after 13:28, filling nominally at the 13:29 open.
  - **Holding horizon:** 29 minutes. **Session window:** 13:00-13:29 CT. Flat well before F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid, with history
  2019-05..2026-06 (micros shorter, C8). The latest signal input, the 08:29 bar, is available at
  08:30 CT.
- **Order type:** market. **Sizing:** q_c of the D2 vehicle (C6).
- **Parameters:** O+29 = 08:29, C-31 = 12:59, C-2 = 13:28 (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29 minutes.
  Floor: at most 20 entries a day, ok; 2-minute minimum hold, ok; 10-minute mean hold, ok.
- **Falsification:** the standard condition only (a port; D6 is unchanged). UCB95 of the member's
  mean net daily P&L per contract below eps_X, at >= 80% achieved null power on the confirmation
  window, counts against it.
- **Topstep check:**
  1. Flat by F: last fill 13:29.
  2. Order type: market.
  3. D9.4: one trade a day, no stops, brackets or passive fills.
  4. *: MCL is starred with its restriction unresolved (D9.8). This applies only if D2 picks MCL
     for crude.
  5. News: 1 lot-equivalent, half the 2-lot maximum. On scheduled FOMC days the entry fill (13:00)
     falls in the statement minute (Topstep F6 "FOMC Statement | 1:00 PM | All products"). That is
     allowed at 1 lot-equivalent, but noted in section 7, item 3.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of each admitted K4 vehicle, research window 2025-04-01..2026-06-19 and
  confirmation S_X..2024-02-29 (D4). No external data.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K4-cp2-01 (core port CP2, opening-range breakout)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-07: the buffer is 4 ticks of the exposure's MOST ACTIVE contract, per D6: crude 0.04 on CL, QM and MCL alike; natural gas 0.004 on NG, QG and MNG alike. The per-vehicle buffer table below is superseded.]
- **Cluster** K4. **Products read:** own vehicle.
- **Exposures:** crude, gas, RBOB, ULSD, one trial each. Each is traded only if D2 admits the
  exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py,
  hold_minutes = 75), as fixed in D6 row CP2 with the 21:12 amendment.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first
    bar opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P;
    market intent in the break direction; one entry per trade date; no entry from C on. Exit: 75
    minutes after the fill, or the engine's forced flatten at F if earlier."
  - **K4 log:** K4-013 (Holmberg, Lönnbark and Lundström, an opening-range breakout on WTI crude
    futures; D.1 B4) is this family on crude and is recorded as **covered by CP2**. K4-043's stop-order
    fact (CL has the highest stop-order share of the three markets studied, P-K4-043-b) is the
    family's microstructure background. K4-050, a pre-registered ORB-cost study, is blocked at title
    only.
- **Instantiated:**
  - **Opening range:** the bars opening in [08:00, 08:15).
  - **Eligible bars:** those opening in [08:15, 13:30). No entry from 13:30 CT on.
  - **Buffer, 4 ticks of the vehicle (C7):**

    | Vehicle | Buffer | Per contract |
    |---|---|---|
    | CL | 0.04 | $40 |
    | QM | 0.100 | $50 |
    | MCL | 0.04 | $4 |
    | NG | 0.004 | $40 |
    | QG | 0.020 | $50 |
    | MNG | 0.004 | $4 |
    | RB | 0.0004 | $16.80 |
    | HO | 0.0004 | $16.80 |

  - **Entry:** the first eligible bar whose close is >= OR_high + buffer buys; one whose close is
    <= OR_low - buffer sells. One entry per trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it. The exit intent is
    emitted on the 75th bar after the entry-intent bar and fills at the next open. The engine's
    flatten at F is the backstop.
  - **Holding horizon:** 75 minutes. The latest entry fill is 13:30 and its exit 14:45, so F never
    binds on a full session. **Session window:** 08:16 to 14:45 at the latest.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is known
  at 08:15 CT.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** OR 15 minutes, buffer 4 ticks, hold 75 minutes (D6, a literal port). **Grid:**
  none.
- **Expected entries and hold:** at most 1 per day, held 75 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: latest exit 14:45.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. *: MCL flag, as in CP1.
  5. News: 1 lot-equivalent. A position may be open at the 09:30 WPSR or storage release or at the
     13:00 FOMC statement, which F6.3 allows below full maximum size.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K4-cp3-01 (core port CP3, prior-close location)
- **Cluster** K4. **Products read:** own vehicle.
- **Exposures:** crude, gas, RBOB, ULSD. Each is traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L
    over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as
    Family H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells,
    market intent on the O bar of day d. Exit: first bar at or after C-2 min."
  - **K4 log:** K5-028's next-day momentum for oil (P-K5-028-a [K4]) is a prior-day follow-through
    in this family (section 5).
- **Instantiated:**
  - **Daily bar:** O_d = open of the 08:00 bar. H and L are taken over the bars opening in
    [08:00, 13:30). C_d = close of the 13:29 bar.
  - **Complete day** (Family H): the 08:00 and 13:29 bars exist, the date is not an early halt, and
    every bar in [08:00, 13:30) carries one instrument_id.
  - **Instrument guard:** d-1's daily bar carries the instrument_id of day d's 08:00 bar.
  - **CLV:** computed in ticks, with Range[d-1] > 0. CLV >= 0.8 buys and CLV <= 0.2 sells
    (non-strict, as H6).
  - **Entry:** market intent on the 08:00 bar of d, filling at the 08:01 open.
  - **Exit:** first bar at or after 13:28, filling nominally at the 13:29 open.
  - **Holding horizon:** about 328 minutes. **Session window:** 08:01-13:29.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's
  bar is complete at 13:30 CT on d-1.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 328 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 13:29.
  2. Order type: market.
  3. D9.4: ok.
  4. *: MCL flag.
  5. News: holds through the Wednesday WPSR, the Thursday storage report and FOMC statements at 1
     lot-equivalent, which is not the full maximum (D9.5).
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K4-ngpre-01 (natural gas storage-report day: short from 90 minutes before to 30 minutes after)
- **Cluster** K4. **Products read:** the gas vehicle; EC-NGS; EC-CAL.
- **Traded exposure:** Henry Hub gas {NG, QG, MNG}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** NG futures earn a negative average return on EIA storage-report days.
    "The entire effect (99%) stems from the two hour window surrounding the announcement"
    (P-K4-001-b). The return splits half before and half after the release (P-K4-001-a). The
    (-90, 30) window averages -0.37% (p 0.000) (P-K4-001-c). "Opening a short position 90 minutes
    before the announcement and closing it 30 minutes afterwards" is the authors' own strategy
    (P-K4-001-d).
  - **Evidence against, from the same source:** after 2011 the strategy is flat to negative after
    costs: "Raw + TC + FC -0.97 (0.843)" (P-K4-001-e). Its Sharpe ratios are annualized with 252 on
    a weekly trade (P-K4-001-f). The confirmation window (2019-2024) lies wholly after 2011, so the
    expected outcome is null. The member tests whether the puzzle is absent in 2019-2026 at the
    funnel's bar.
  - **Classification:** port of D.1 family E (pre-release window), gas-specific. D6 does not port
    family E, so this is a cluster member (new to Stage E).
- **Event set:** every EC-NGS release that passes C9's checks. The release time T (CT) is 09:30 in
  the standard slot, 11:00 for the Wednesday or Monday 12:00 ET exceptions, and 09:30 for the Friday
  10:30 ET exceptions.
- **Entry rule:** SELL, market intent on the bar at T - 91 min, filling at the open of T - 90
  (standard: intent on the 07:59 bar, fill at the 08:00 open).
- **Exit rule:** market intent on the bar at T + 29, filling at the open of T + 30 (standard 10:00).
- **Holding horizon:** 120 minutes. **Session window:** 08:00-10:00 CT (standard); 09:30-11:30 CT
  for 11:00 CT releases. Flat by F (latest fill 11:30).
- **Data fields read:**
  - Vehicle ohlcv-1m open and instrument_id (C8). Paid, 2019-05..2026-06 (MNG from 2023-11, C8).
  - EC-NGS release date and time. Free, with 2019-2026 history (C9). Known before d.
  - EC-CAL. Known in advance.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** entry at T - 90 and exit at T + 30 (P-K4-001-c, P-K4-001-d); side SELL (the
  window's average return is negative, P-K4-001-c). **Grid:** none.
- **Expected entries and hold:** one per release. That is about 64 in the research window and about
  252 in the confirmation window, before C4's exclusions and S_X (C11): about 0.2 per trade date,
  held 120 minutes. Floor ok.
- **Falsification:**
  - The standard condition (UCB95 of mean net daily P&L per contract below eps_X at >= 80% achieved
    null power on the confirmation window counts against it).
  - **Sign check, reported beside the verdict and not a separate test:** the mechanism predicts a
    negative mean gross move of the vehicle, in ticks, from the T - 90 open to the T + 30 open on
    event days. A non-negative confirmation-window mean counts against the mechanism.
- **Topstep check:**
  1. Flat by F: latest fill 11:30.
  2. Order type: market.
  3. D9.4: one trade per release, no stops. Entry 90 minutes before the release, not in a gapped
     market.
  4. *: none (NG, QG, MNG unstarred).
  5. News: holds into the storage release ("Natural Gas Inventories (EIA) | 9:30 AM | NG, QG";
     "**Micro contracts also apply", F6) at 1 lot-equivalent, which F6.3 and D9.5 allow.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the gas vehicle (research and confirmation windows); external EC-NGS
  and EC-CAL.
- **Trials in N:** 1.

### K4-ngrev-01 (natural gas storage-report response reversal, week to week)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-06: EXCLUDED. Its own source's abstract (K4-006) says "Analyst's natural gas forecasts efficiently impound the available time-series information", which contradicts step 2 (the surprise reversal) the member rests on. 0 trials. The entry is kept below for the record only.]
- **Cluster** K4. **Products read:** the gas vehicle; EC-NGS; EC-CAL.
- **Traded exposure:** Henry Hub gas {NG, QG, MNG}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "Storage flows higher or lower than analysts had expected one week tend to
    be partially reversed the following week" (K4-006 P-K4-006-a, abstract only).
  - **The rule-3 route.** The surprise itself needs the proprietary consensus, so it is observed
    through the price response. That is the route rule 3 names: "the first minutes' price response
    as the surprise". The reasoning, step by step:
    1. The release response is inverse to the storage surprise. P-K4-002-d: "an unexpected 1%
       increase in natural gas in storage results in a 2.4% drop in natural gas futures prices".
       P-K4-028-a: "an inverse empirical relation between changes in futures prices and surprises".
       So the sign of last week's surprise is minus the sign of last week's release response
       R_{k-1}.
    2. By P-K4-006-a, this week's surprise tends to have the opposite sign of last week's.
    3. So this week's release response R_k tends to have the opposite sign of R_{k-1}. The position
       is -sign(R_{k-1}), held across this week's release in the event window P-K4-002-b fixes
       ("from five minutes before to ten minutes after the announcement time").
  - **Open questions:**
    - Step 2 rests on an abstract.
    - Whether the market already prices the reversal is [unverified]. The same abstract says "the
      market promptly incorporates analyst forecasts into oil and gas prices prior to the EIA
      announcements".
    - Whether the reversal also holds for crude is not stated. The sentence sits in the natural-gas
      part of the abstract, so the member is written for gas only.
  - **Classification:** new to the program (K4-006's log tag: "week-to-week surprise reversal as a
    predictor of the next surprise").
- **Event set:** release k in EC-NGS at T_k, with release k-1 the immediately preceding EC-NGS
  entry at T_{k-1}. Both pass C9's checks.
- **Signal:** R_{k-1} = close of the vehicle's bar at T_{k-1} + 9 minus close of its bar at
  T_{k-1} - 1, in ticks. Both bars must exist with one instrument_id; they need not match release
  k's contract, since only the sign is used. R_{k-1} = 0 means no trade.
- **Entry rule:** market intent on the bar at T_k - 6, filling at the open of T_k - 5 (standard:
  09:25). BUY if R_{k-1} < 0; SELL if R_{k-1} > 0.
- **Exit rule:** market intent on the bar at T_k + 9, filling at the open of T_k + 10 (standard:
  09:40).
- **Holding horizon:** 15 minutes. **Session window:** 09:25-09:40 CT (standard); 10:55-11:10 CT for
  11:00 CT releases. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m close, open and instrument_id on release k-1's date and on release k's date
    (C8).
  - EC-NGS and EC-CAL (C9).
  - The signal is available at T_{k-1} + 10, about a week before the entry.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - The signal window, from T - 1 to T + 9 bar closes, is the post-release part of P-K4-002-b's
    window.
  - The trade window, from T - 5 to T + 10, is P-K4-002-b's window.
  - Direction: -sign(R_{k-1}), from P-K4-006-a with P-K4-002-d.
  - **Grid:** none.
- **Expected entries and hold:** about one per week: about 64 research and 252 confirmation events,
  before exclusions and R_{k-1} = 0 cases. Held 15 minutes. Floor ok: the 2-minute minimum and the
  10-minute mean both hold.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of direction x (open at T_k + 10 - open at T_k - 5), in
    ticks, is positive.
  - **Reported beside it:** the correlation of consecutive responses (R_{k-1}, R_k) over the
    window's releases, which the mechanism predicts is negative.
- **Topstep check:**
  1. Flat by F: latest fill 11:10.
  2. Order type: market.
  3. D9.4: one trade per release. It enters 5 minutes before the release and exits 10 minutes
     after, so neither fill is in the release minute. Slippage is charged at the 09:30 bucket (C12).
  4. *: none.
  5. News: holds through the storage release at 1 lot-equivalent (F6.3).
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the gas vehicle; external EC-NGS, EC-CAL.
- **Trials in N:** 1.

### K4-apipre-01 (API-to-EIA continuation before the crude inventory release)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP until E.1 records its source windows (K4-022, K4-023).]
- **Cluster** K4. **Products read:** the crude vehicle; EC-WPSR; EC-API (timing rule only); EC-CAL.
- **Traded exposure:** WTI crude {CL, QM, MCL}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "This inefficiency can be exploited by sophisticated traders. ... We also
    construct a predictor that can predict inventory surprises and pre-announcement returns
    in-sample and out-of-sample" (K4-009 P-K4-009-a, abstract). The log's reading of that abstract:
    the API bulletin is informative about the next day's WPSR, yet CL does not fully absorb it.
  - **The rule-3 route.** The API bulletin is proprietary, so its content is observed through CL's
    response in the API window. API crude-inventory shocks move 15-minute CL returns (P-K4-023-b:
    positive and negative shock coefficients -0.134 and -0.126). The API is released "Tuesdays at
    4:30pm EST" (P-K4-023-a; P-K4-045-a), that is, about 15:30 CT. The sign of that response is the
    market's reading of the API news. Under incomplete absorption, the pre-release return continues
    in the same direction.
  - **Pre-release window:** informed selling and a price run-up begin "around 08:30 ET, two hours
    before the 10:30 release" (log mechanism line for K4-022; verbatim: P-K4-022-b "ahead of the
    EIA-DOE inventory release each Wednesday" and P-K4-022-e "the average OID over the 8:30 – 9:30
    period"). 08:30 ET = 07:30 CT.
  - **Supporting:** K4-026 P-K4-026-c ("the futures market seems to anticipate the surprises
    correctly one day before") and K4-046 P-K4-046-a (practitioner claim, untested).
  - **Classification:** new to the program (API-to-EIA sequential information).
- **Event set:** EC-API standard weeks (C9). The WPSR is on its Wednesday 09:30 CT slot, and the
  preceding Tuesday is a full-session trade date.
- **Signal:** R_API = close of the vehicle's bar at 15:39 CT on the Tuesday minus close of its bar
  at 15:24 CT on the Tuesday, in ticks. That is the (-5, +10)-minute window around 15:30 CT, the
  convention of P-K4-002-b applied to the API time. Both bars must exist with one instrument_id.
  R_API = 0 means no trade.
- **Entry rule:** Wednesday, market intent on the bar at 07:29, filling at the 07:30 open, in the
  direction sign(R_API).
- **Exit rule:** market intent on the bar at 09:28, filling at the 09:29 open. The member is flat
  before the 09:30 release.
- **Holding horizon:** 119 minutes. **Session window:** 07:30-09:29 CT. Flat by F.
- **Why the exit precedes the release:**
  - The verified claim is about "pre-announcement returns" (P-K4-009-a).
  - The release response is contemporaneous (K4-002).
  - A fill in the release minute is the gapped-market case D9.4 warns about.
  - The through-release variant is not written (section 3).
- **Data fields read:**
  - Vehicle ohlcv-1m close, open and instrument_id: on the Tuesday at 15:24 and 15:39 (Globex,
    after the 13:30 settlement; available by 15:40 CT on the Tuesday), and on the Wednesday 07:29 to
    09:29 (C8).
  - EC-WPSR, EC-API rule, EC-CAL (C9), all known before the Tuesday.
  - The API bulletin itself is never read.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - Signal bars 15:24 and 15:39 (P-K4-045-a time with P-K4-002-b's -5/+10 window).
  - Entry 07:30 (P-K4-022-b, P-K4-022-e).
  - Exit 1 minute before T_W.
  - **Grid:** none.
- **Expected entries and hold:** about 56 standard weeks in the research window and about 210 in the
  confirmation window (C11), before exclusions and R_API = 0 days. That is about 0.18 per trade
  date, held 119 minutes. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(R_API) x (open at 09:29 - open at 07:30), in ticks,
    on event days is positive.
- **Topstep check:**
  1. Flat by F: last fill 09:29.
  2. Order type: market.
  3. D9.4: one trade a week, no stops, no fill near the release.
  4. *: MCL flag (crude).
  5. News: flat before the 09:30 WPSR ("Crude Oil Inventories (EIA) | 9:30 AM / 10:00 AM* | CL, QM,
     MCL, RB", F6). 1 lot-equivalent.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Member-level coverage (D9):** E.2's coverage check must cover the entry window (07:30-09:29)
  and the two Tuesday signal minutes, which fall after the settlement.
- **Data needed:** ohlcv-1m of the crude vehicle, including the post-settlement Tuesday minutes;
  external EC-WPSR, EC-API rule, EC-CAL.
- **Trials in N:** 1.

### K4-eiafade-01 (post-WPSR overreaction fade)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP until E.1 records its source window (K4-022 body not retrieved).]
- **Cluster** K4. **Products read:** the crude vehicle; EC-WPSR; EC-CAL.
- **Traded exposure:** WTI crude {CL, QM, MCL}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** CL overreacts to the WPSR and partly reverses over the following hours: "an
    over-reaction that is partly compensated in the hours following the announcement" (P-K4-022-a).
    On positive-surprise days the release brings "a large average price drop of about 0.5% ...
    partly corrected in the hours following the news release. Four hours later, the drop is half as
    large, i.e. 0.25%" (P-K4-022-d).
  - **The rule-3 route.** The source conditions on 3-sigma Bloomberg surprises (P-K4-022-c), which
    are proprietary. The proxy is the first 15 minutes' price response (rule 3), with the source's
    own average release move as the threshold for a large response.
  - **Symmetric:** P-K4-022-a's over-reaction statement is not restricted to positive surprises. The
    0.5% magnitude comes from positive-surprise days (P-K4-022-d). The reversal after large price
    rises is [unverified in the logged passages].
  - **Classification:** port of D.1 family C (reversal after an event shock) conditioned on family E
    (log tag). New member.
- **Event set:** every EC-WPSR release that passes C9's checks with T_W + 15 <= 13:13 CT, so the
  entry precedes the exit by at least 15 minutes. That covers the 09:30, 10:00 and 11:00 CT slots
  and excludes the 16:00 CT Monday release.
- **Signal:** M = (close of the bar at T_W + 14 - close of the bar at T_W - 1) / close of the bar at
  T_W - 1 (C10: the denominator must be > 0). Both bars must exist with one instrument_id.
- **Entry rule:**
  - If M <= -0.005: BUY.
  - If M >= +0.005: SELL.
  - Otherwise no trade.
  - Market intent on the bar at T_W + 14, filling at the open of T_W + 15 (standard 09:45).
- **Exit rule:** market intent on the first bar at or after 13:28, filling nominally at the 13:29
  open. This is the ports' C-2 convention. For the standard 09:30 release it ends the position at
  the end of P-K4-022-d's "Four hours later" horizon (13:30 CT).
- **Holding horizon:** 224 minutes (standard); 194 for 10:00 CT releases; 134 for 11:00 CT
  releases. **Session window:** 09:45-13:29 CT (standard). Flat by F.
- **Data fields read:** vehicle ohlcv-1m close, open and instrument_id (C8), available at the close
  of the bar at T_W + 14; EC-WPSR and EC-CAL (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Measurement window of 15 minutes after the release: a judgment.** It matches the 15-minute
    windows of the log's intraday release studies: P-K4-033-a "During the 15 minutes following
    supply announcements"; K4-023's 15-minute API and EIA windows (P-K4-023-a, P-K4-023-b); and
    P-K4-002-b's +10 minutes, rounded up to the next quarter hour.
  - **Threshold 0.5% of price:** P-K4-022-d.
  - **Exit at C - 2:** P-K4-022-d's four-hour horizon.
  - **Grid:** none.
- **Expected entries and hold:**
  - About 63 eligible releases in the research window and about 250 in the confirmation window.
  - Trades only on large responses. The passages suggest roughly one release in four or five
    qualifies: "90 surprises (22.39%)" of 402 (P-K4-022-c) and "11 out of 50 EIA reports generated
    significant return jumps" (P-K4-023-c). That gives about 14 research and about 55 confirmation
    trades.
  - This is a passage-based expectation, not a price-data estimate.
  - Holds 134-224 minutes. Floor ok.
  - Power: probably "inconclusive by design" under D4 (section 7, item 4).
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of -sign(M) x (open at 13:29 - open at T_W + 15), in ticks,
    on traded days is positive. It is also reported split by the sign of M, since the evidence is
    for price drops.
- **Topstep check:**
  1. Flat by F: last fill 13:29.
  2. Order type: market.
  3. D9.4: one trade per release. It enters 15 minutes after the release, not in the release minute
     or the gapped first minutes.
  4. *: MCL flag.
  5. News: the position starts after the release. 1 lot-equivalent.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the crude vehicle; external EC-WPSR, EC-CAL.
- **Trials in N:** 1.

### K4-eiamom-01 (WPSR-day release half-hour predicts the last NYSE half-hour)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP until E.1 records its source window (K4-021 body not retrieved).]
- **Cluster** K4. **Products read:** the crude vehicle; EC-WPSR; EC-NYSE; EC-CAL.
- **Traded exposure:** WTI crude {CL, QM, MCL}, traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "returns on the third half-hour on EIA announcement days can significantly
    and positively predict the returns in the last half-hour" (K4-021 P-K4-021-a). The EIA-day
    slope is 0.038 (t 2.12), with adjusted R2 3.10% over 591 Wednesday 10:30 ET releases
    (P-K4-021-c).
  - **The source's instrument and clock:** USO, on 1-minute data (P-K4-021-b). The half-hours are
    NYSE half-hours, 09:30-16:00 ET (log product line). The third half-hour is 10:30-11:00 ET, the
    release interval; the last is 15:30-16:00 ET.
  - **Transfer to CL (reasoning, untested by the source; log quality tell 1).** USO holds CL futures
    and its intraday price tracks them. A USO half-hour return is therefore a crude-futures return
    over the same clock interval, up to tracking error. Both half-hours are traded on the same
    clock: 09:30-10:00 CT and 14:30-15:00 CT. 14:30-15:00 CT falls after the 13:30 CL settlement,
    but inside the XFA day.
  - **Counter-evidence:**
    - P-K4-037-b: "the information contained in the inventory announcements does not offer
      predictability to the last half-hour returns" (same first author, 2006-2018).
    - P-K4-021-e: a declining trend, and no predictability in 2014-2016.
    - No costs in the source (log quality tell 3).
  - **Classification:** port of D.1 family C (intraday momentum) conditioned on family E (log tag).
    It differs from CP1 in its signal half-hour, event days and traded window. New member.
- **Event set:** standard WPSR Wednesdays (T_W = 09:30 CT, not in the exception table, the source's
  "Wednesday-10:30" sample). The date must be a full session in both EC-CAL and EC-NYSE.
- **Signal:** r3 = close of the bar at 09:59 minus close of the bar at 09:29, that is, the price at
  11:00 ET minus the price at 10:30 ET, in ticks. Both bars must exist with one instrument_id.
  r3 = 0 means no trade.
- **Entry rule:** market intent on the bar at 14:29, filling at the 14:30 open (15:30 ET), in the
  direction sign(r3).
- **Exit rule:** market intent on the first bar at or after 14:58, filling nominally at the 14:59
  open. This is CP1's C-2 convention with C = 15:00 CT, the NYSE close.
- **Holding horizon:** 29 minutes. **Session window:** 14:30-14:59 CT, flat 9 minutes before F.
- **Data fields read:** vehicle ohlcv-1m close, open and instrument_id (C8), with the signal
  available at 10:00 CT; EC-WPSR, EC-NYSE and EC-CAL (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** signal bars 09:29 and 09:59, the third NYSE half-hour (P-K4-021-a; log product
  line); trade window 14:30-14:59, the last NYSE half-hour. **Grid:** none.
- **Expected entries and hold:** about 56 research and about 210 confirmation events before
  exclusions (C11): about 0.18 per trade date, held 29 minutes. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(r3) x (open at 14:59 - open at 14:30), in ticks, on
    event days is positive.
  - **Descriptive control (not a trial):** the same statistic on full-session Tuesdays, Thursdays
    and Fridays. There, P-K4-021-a says r3 has no predictive power.
- **Topstep check:**
  1. Flat by F: last fill 14:59, 9 minutes before F.
  2. Order type: market.
  3. D9.4: one trade a week, no stops.
  4. *: MCL flag.
  5. News: no scheduled K4 release in the window. 1 lot-equivalent.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Member-level coverage (D9):** the window lies after the 13:30 settlement. E.2's coverage check
  decides whether it can be screened.
- **Data needed:** ohlcv-1m of the crude vehicle; external EC-WPSR, EC-NYSE (to be sourced in E.2),
  EC-CAL.
- **Trials in N:** 1.

### K4-ovr-01 (hourly overreaction reversal)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source sample is 2019-11-20 to 2020-06-03, inside the confirmation window, and its crude figure is driven by the 2020-04-20 negative-price episode (review R-16).]
- **Cluster** K4. **Products read:** each traded exposure's own vehicle; EC-CAL.
- **Traded exposures** (each a separate trial): crude {CL, QM, MCL}, ULSD {HO}, gas {NG, QG, MNG}.
  These are the K4 products in the source's sample: "WTI crude oil (CL), Brent crude oil (CO),
  heating oil (HO), natural gas (NG)" (P-K5-029-b [K4]). RBOB is not in the sample and is not
  traded. Each exposure is traded only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed** (K5-029, a panel source; the [K4] passages are in the K5 log): large
    intraday price changes beyond a decile threshold, at 1-minute to 1-hour frequencies, are
    followed by reversals in commodity futures. "Soft and metal commodities show much less
    overreactions than precious metals and especially energy commodities" (P-K5-029-a).
  - **Crude result:** "An investor who would have traded all crude oil long positions after the
    10% highest negative price changes, would have also traded this price reversal and consequently
    would have realized a trading return of 11.91%" (P-K5-029-c [K4]).
  - **Costs:** net results are asserted positive "for positive and negative initial price changes"
    (P-K5-029-d).
  - **Evidence quality:** about six months of data (2019-11-20 to 2020-06-03, Covid-dominated,
    P-K5-029-a); costs asserted, not modelled; holding period [unverified] (K5 log quality tells).
  - **Classification:** a family C magnitude-conditioned reversal, tested on energy products
    specifically. D6 does not port family C, so under partition rule 6 this is a cluster member.
- **Decision times:** t in {09:00, 10:00, 11:00, 12:00, 13:00} CT, the five whole hours of the
  energy day session from O = 08:00.
- **Signal:** r(t) = (close of the bar at t - 1 - open of the bar at t - 60) / open of the bar at
  t - 60. The denominator must be > 0 (C10), and both bars must exist with one instrument_id.
- **Reference set and cuts:**
  - The reference set is the values r(tau) at the same five clock times on the 20 most recent
    earlier trade dates that are full sessions in EC-CAL. Every value whose two bars exist with one
    instrument_id counts, and at least 80 values are required, else no trade at t.
  - P10 and P90 = np.percentile(values, [10, 90], method="linear").
  - Warm-up: the first 20 eligible dates of each window. No bars before the research window exist:
    holdout-2 is sealed.
- **Entry rule:**
  - r(t) <= P10: BUY.
  - r(t) >= P90: SELL.
  - Otherwise no trade.
  - Market intent on the bar at t - 1, filling at the open of the bar at t.
- **Exit rule:** market intent on the bar at t + 58, filling at the open of t + 59. At most one
  position is open. The next decision's entry fills at t + 60, so positions never overlap.
- **Holding horizon:** 59 minutes. **Session window:** 09:00-13:59 CT. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8), all closed at or before
  t; EC-CAL.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **60-minute signal and decile cuts:** the source's 1-hour frequency and "10% highest negative
    price changes" (P-K5-029-c). The symmetric upper cut follows P-K5-029-d.
  - **20-trade-date trailing reference: a judgment.** It is the program's trailing-state length
    (D15.4 B4). The source's own threshold construction is not in the logged passages.
  - **59-minute hold: a judgment.** It is one signal period less the one-minute gap that keeps
    positions from overlapping. The source's holding period is [unverified].
  - **Grid:** none.
- **Expected entries and hold:** by construction about 2 in 10 decision times qualify if the trailing
  distribution is stable. That is about 1 entry per day per exposure (at most 5), held 59 minutes.
  Floor ok.
- **Falsification:**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean of -sign(r(t)) x (open at t + 59 - open at t), in ticks, is
    positive.
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market.
  3. D9.4: at most 5 entries a day, each held 59 minutes, no stops or brackets. Not scalping.
  4. *: MCL flag for crude.
  5. News: the 10:00 decision on release days reads an hour containing the 09:30 release and may
     fade it at 10:00, 30 minutes after the release. 1 lot-equivalent.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
- **Data needed:** ohlcv-1m of the crude, ULSD and gas vehicles (research and confirmation windows).
- **Trials in N:** 1 per admitted exposure among crude, ULSD and gas (at most 3).

### K4-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: fallback order declared now (D1 ADV order): WTI crude, natural gas, RBOB, ULSD; if none is admitted, no ML member. Features unchanged.]
- **Traded vehicle: WTI crude exposure** {CL, QM, MCL}; the contract is chosen by D2 in E.2.
  - **Reason:** crude is the K4 exposure the log documents most often at intraday horizons:
    K4-002, 003, 007, 009, 020, 021, 022, 023, 025, 026, 032, 033, 037, 043, 044 and 046, against
    nine gas items (K4-001, 004, 005, 006, 012, 028, 029, 031, 038). It also has the cluster's
    highest public ADV: CL 1,079,857 contracts per day, 2026 Jan-Aug (design D1 table).
  - **No fallback is declared.** The cluster features below are crude-specific (API and WPSR
    timing), so they would not transfer to another exposure. If D2 admits no crude contract, the
    lead decides.
  - **MCL flag:** if D2 picks MCL, the unresolved * restriction applies (D9.8).
- **Products the features read:**
  - The crude vehicle.
  - RB bars, needed as a leg even if RBOB is not traded. D13 buys history only for the chosen
    vehicle of each traded exposure, so E.2 must add RB's history if RBOB is not admitted.
  - Calendars: EC-WPSR, EC-NGS, EC-CAL, and the EC-API timing rule.
- **Cluster features.** There are 7; with D15.4's B1-B5 that makes 12. Throughout, t_j is the
  decision time, "the bar at t_j - 1" is the last bar closed at t_j, and tick is the vehicle's tick.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | wpsr_phase | If d carries a WPSR release at T_W (EC-WPSR): -1 if T_W - 120 min <= t_j < T_W; +1 if T_W <= t_j < T_W + 240 min; else 0. If d carries no release: 0 | K4-017 P-K4-017-a, P-K4-017-b (schedule); K4-022 P-K4-022-b, P-K4-022-e (pre-release window from 08:30 ET), P-K4-022-d ("Four hours later") | schedule known before d (C9); depends only on the clock |
| KF2 | wpsr_move | If d carries a WPSR release at T_W and t_j >= T_W + 15: (close of the bar at T_W + 14 - close of the bar at T_W - 1) / tick; else 0. On such a d with t_j >= T_W + 15, a missing bar or a change of instrument_id means no trade at t_j | K4-022 P-K4-022-a, P-K4-022-d; K4-023 P-K4-023-b, P-K4-023-c; K4-002 P-K4-002-b; K4-033 P-K4-033-a (15 minutes); K4-021 P-K4-021-a | T_W + 15 (close of the bar at T_W + 14) |
| KF3 | api_move | If d is an EC-API standard-week Wednesday (C9): (close of the bar at 15:39 CT - close of the bar at 15:24 CT, both on the previous calendar day) / tick; else 0. On such a d, a missing bar or a change of instrument_id means no trade at any t_j of d | K4-009 P-K4-009-a; K4-023 P-K4-023-a, P-K4-023-b; K4-045 P-K4-045-a; K4-046 P-K4-046-a | 15:40 CT on d-1, before d's first decision |
| KF4 | ngs_phase | If d carries a storage release at T_N (EC-NGS): -1 if T_N - 90 min <= t_j < T_N; +1 if T_N <= t_j < T_N + 30 min; else 0. If d carries no release: 0 | K4-018 P-K4-018-a (schedule); K4-002 P-K4-002-e (the gas report moves crude: "Crude Oil -0.14 (0.08)*"); K4-001 P-K4-001-c (the (-90, 30) window) | schedule known before d |
| KF5 | rb_ret30 | (close of the RB bar at t_j - 1 - open of the RB bar at t_j - 30) / 0.0001, in RB ticks. Both bars must exist with one RB instrument_id, else no trade at t_j | K4-020 P-K4-020-a, P-K4-020-d ("the change in gasoline futures price has a significantly greater impact on WTI crude oil futures price than in the opposite case") | RB bar closes <= t_j |
| KF6 | gsci_roll | 1 if d is the 5th, 6th, 7th, 8th or 9th trade date of its calendar month in EC-CAL; else 0. The index's own business-day calendar is not logged, so it is approximated by energy trade dates, a judgment | K4-034 P-K4-034-b ("from the fifth to the ninth business day ... 20% of its positions"); K4-036 P-K4-036-c; K4-003 P-K4-003-c, P-K4-003-d | calendar known in advance |
| KF7 | ret60_pct | Let r60(tau) = (close of the vehicle's bar at tau - 1 - open of its bar at tau - 60) / tick. The value is (number of reference values < r60(t_j) + 0.5 x number equal) / (number of reference values). The reference set is r60 at the 15 decision clock times on the 20 most recent earlier eligible trade dates, counting each value whose bars exist with one instrument_id; at least 240 values are required, else no trade at t_j | K5-029 P-K5-029-a, P-K5-029-c [K4] (decile overreactions at the 1-hour frequency, strongest in energy), P-K5-029-d | bars closed <= t_j, and earlier trade dates |

- **Decision window [W0, W1] = [07:15, 14:15] CT; horizon h = 30 minutes.**
  - **Decision times:** t_j = 07:15, 07:45, ..., 14:15, which is 15 a day. W1 + h = 14:45 <= F.
  - **Fills:** by D15.3's convention a position covers the open of t_j + 1 to the open of t_j + 30.
    Every fill therefore falls at :16, :46, :15 or :45.
  - **Why this window:** it starts before K4-022's informed pre-release window, which opens about
    07:30 CT (P-K4-022-b, P-K4-022-e). The :15 offset puts every scheduled K4 event minute strictly
    inside a position interval and never at a fill:
    - the 09:30 WPSR and storage releases (inside [09:16, 09:45]);
    - the 10:00 and 11:00 CT holiday release slots;
    - the London Trading-at-Marker minute, 16:29-16:30 London time (P-K4-047-a), which is 10:29 CT
      for most of the year and 11:29 CT in the weeks when UK and US clock changes differ;
    - the 13:00 CT FOMC statement;
    - the 13:28-13:30 CT settlement window (K4-003's "14:28-14:30 ET").

    No ML fill lands in a release minute, the gapped-market case of D9.4.
  - **Why h = 30:** it is the horizon over which the logged responses play out:
    - K4-021's half-hour structure (P-K4-021-a);
    - the +30-minute end of K4-001's report window (P-K4-001-c);
    - "volatility up to 30 minutes following the announcement was also higher than normal"
      (P-K4-004-a).

    h = 15 would sit inside the release spike and its 15-minute response windows (K4-002, K4-023).
    h = 60 or 120 would fold the release, the TAM marker and the post-release reversal into one
    interval.
- **Expected rows:** about 15 x the eligible research-window trade dates. That is about 305 trade
  dates, less roll-blackout, vendor-degraded and early-halt dates (D15.3), and less the 20-date
  warm-up of KF7 and B4: roughly 3,700-4,200 rows. E.2 gives the exact count.
- **Expected entries:** at most 15 per day (<= 20), each held 30 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps at
  >= 80% achieved null power on the confirmation window counts against it). Failing the D5 screen
  puts it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 14:45.
  2. Order type: market (D15.6).
  3. D9.4: at most 15 entries a day, 30-minute holds, no stops or brackets. No fill in a release
     minute.
  4. *: MCL flag.
  5. News: q_c <= 1 lot-equivalent, not the full maximum. A position may span a release.
  6. Position limit: <= 1 lot-equivalent.
  7. Price limit: C13.
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for
    every ML member.
- **Data needed:**
  - ohlcv-1m of the crude vehicle and RB. The research window is used for training and tuning, the
    confirmation window for the frozen model.
  - The member-level coverage check covers 07:16-14:45.
  - External: EC-WPSR, EC-NGS, EC-CAL.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K4-ngfcst-01 | NG position before the storage release, signed by the accuracy-weighted analyst predictor: the median forecast of historically accurate analysts minus the consensus (K4-012 P-K4-012-a; K4-005 P-K4-005-a) | Rule 3 (proprietary data) | It needs analyst-level storage forecasts and their accuracy history ("individual forecasts of analysts according to their prior accuracy", P-K4-005-a; Bloomberg per the log). No named, obtainable historical source was found. The crowd alternative (Estimize) is a commercial dataset, and "does not influence the market's expectation ... beyond what is already contained in professional consensus" (K4-031 P-K4-031-a). The obtainable-proxy route to a gas storage predictor is K4-ngrev-01. |
| X-02 K4-surprise-01 | Post-release trade in CL, RB, HO or NG signed by the consensus surprise (K4-002 P-K4-002-a, P-K4-002-d; K4-022 P-K4-022-c; K4-023 P-K4-023-b; K4-028 P-K4-028-a; K4-026 P-K4-026-d) | Rule 3; nothing documented to trade | Consensus surveys (Bloomberg, Reuters) are proprietary, with no named obtainable history. With the price-response proxy, what is documented is contemporaneous: K4-002's -5/+10 window and K4-023's 15-minute windows. NG shows "No evidence ... of economically meaningful reactions to the surprise other than on the date the storage news is released" (P-K4-028-b). The one documented post-release pattern, the partial reversal, is K4-eiafade-01. |
| X-03 K4-ngdisp-01 | NG release reaction conditioned on analyst disagreement (K4-006 P-K4-006-a: "contingent on the level of analyst forecast uncertainty as proxied by analyst forecast disagreement") | Rule 3 | Analyst-level dispersion is proprietary; no obtainable history was named. |
| X-04 K4-anlpub-01 | CL traded on analyst inventory-forecast publications, "prices rise (fall) when analysts forecast a decrease (increase) in supplies" (K4-033 P-K4-033-a) | Rule 3 | Analyst forecasts, their publication times ([unverified] per the log) and the accuracy history the effect depends on are proprietary. |
| X-05 K4-badnews-01 | CL continuation after a bearish WPSR: prices "continue to drift for five minutes when news is negative" (K4-032 P-K4-032-a; abstract only; the event is identified as the WPSR only by the log's reading) | D9.3 floor; D9.4 | A rule that holds only the documented five-minute drift breaks the 10-minute mean-hold floor, D9.3(c). Holding longer to meet it would test an undocumented horizon. The entry would fill in the first minutes after the release, the "reckless trades in gapped markets" case of D9.4 [F7.2], where a bar-open fill cannot represent a real fill. The capturable part after latency is unknown (log tag). |
| X-06 K4-fomcsurp-01 | CL, HO or NG traded on the FOMC target surprise measured from fed funds futures (K4-025 P-K4-025-b, P-K4-025-e; K4-010 P-K4-010-a) | Partition rule 4 (K8); contemporaneous | The surprise is read from a rates instrument, and the channel is the dollar: "Monetary policy affects oil prices mostly by affecting the value of the U.S. dollar" (P-K4-025-a). Energy with rates or the dollar is K8's (section 4). The documented response is contemporaneous (a 1-hour window). For scheduled meetings the intraday crude coefficient is insignificant, "-0.88 (0.8)" (P-K4-010-c, slides). |
| X-07 K4-fomcfade-01 | Fade CL's FOMC-window move into the close (K4-025 P-K4-025-d) | Rule 1 (evidence) | The -0.24 intraday-daily correlation holds "for this specific time series realization", a handful of LSAP events. Scheduled meetings show no significant intraday effect (P-K4-010-c), and scheduled releases do not raise energy jump rates (K4-040 P-K4-040-a). No threshold or window can be traced. |
| X-08 K4-idxroll-01 | Commodity-index roll: short nearby and long deferred CL (or NG, RB, HO) around the GSCI roll ("from the fifth to the ninth business day ... 20% of its positions", P-K4-034-b). Or a single-leg outright short of the nearby into the 13:28-13:30 CT settlement window on roll days (K4-003 P-K4-003-c, P-K4-003-d; K4-036 P-K4-036-c; K4-027 P-K4-027-a) | Flat by F; D2 vehicle; rule 1 | **As documented,** the effect is a nearby-minus-deferred differential over multi-day, settlement-to-settlement windows (P-K4-036-c: 26 bp over the roll window). The front-running strategy holds 1-3 weeks (P-K4-035-b). Both break the 15:08 flat rule. **The spread** is not an exposure's D2 vehicle, and the deferred contract's bars are not in the data plan (D13 buys one vehicle per exposure). **A single-leg intraday version** has no logged passage: the outright nearby's move inside the settlement window is untested. Temporary impact "is reversed within ten minutes" (P-K4-003-b). The pooled roll effect is "17 basis points at most" and "never significant" after standard-error adjustment (P-K4-034-a). Which contract the vehicle holds on roll days depends on E.2's roll convention, which could invert the direction or remove the dates as roll blackout. **What such a member would need:** the S&P GSCI contract schedule per commodity logged (not in the log), E.2's roll convention, and a verified intraday source. **What survives:** the date enters K4-ml-01 as a feature only (gsci_roll). K5 and K6 writers apply the [K5] and [K6] passages to their own products. |
| X-09 K4-tas-01 | Trade alongside large TAS holders' strategic trading around the settlement window (K4-027 P-K4-027-a) | Rule 3 | TAS position concentration is not public; whether any public source exists is [unverified]. The source is an abstract only, and its product coverage is [unverified]. |
| X-10 K4-hogo-01 | HO second contract against ICE Gasoil sixth contract, Ornstein-Uhlenbeck bands (K4-042 P-K4-042-a, P-K4-042-b) | Tradability; flat by F; data | Gasoil is an ICE contract: not Topstep-permitted and not in GLBX.MDP3. Band exits are not bounded by F. The source has one year of data, and its optimal leverage is "too large for practical purposes" (P-K4-042-c). A single-leg HO rule conditioned on the spread would still need ICE bars. |
| X-11 K4-brent-01 | CL traded on a Brent lead, or on the WTI-Brent spread (K4-030 P-K4-030-a; R-K4-037, R-K4-072) | Tradability; evidence | ICE Brent is neither tradeable on Topstep nor in GLBX.MDP3. K4-030 finds that CME WTI "still dominate[s] price discovery" when the two are cointegrated, which argues against a Brent lead. |
| X-12 K4-rblead-01 | CL traded on RB's microstructure lead (K4-020 P-K4-020-a, P-K4-020-d) | D9.3/D9.4; rule 4; rule 1 | The excitation is measured at one-second resolution (P-K4-020-c). A rule at that scale is high-rate and needs limit fills. The paper runs no predictability test, so no minute-scale horizon or threshold can be traced. It enters K4-ml-01 as a feature only (rb_ret30). |
| X-13 K4-ngwx-01 | NG traded on weather-forecast model updates (K4-038 P-K4-038-b) | Rule 1; rule 3 | The logged link is seasonal cointegration with daily price fluctuation. Model-update times and an obtainable record of historical forecast vintages are [unverified]. The reader's dedicated weather-model-update search did not complete (log section 1, row +). |
| X-14 K4-ngfri-01 | NG continuation after the holiday-week Friday storage releases, to which "the market responds 74% weaker" (K4-029 P-K4-029-a) | Rule 1; flat by F; frequency | The source uses daily regressions only, and whether the missing response is recovered later is [unverified]. Recovery on the next trading day would need a weekend hold. There are a few events a year (the 2025 table has two Friday releases, 2025-01-03 and 2025-11-14). |
| X-15 K4-anticip-01 | Trade ahead of local price trends identified in the CL order book (K4-044 P-K4-044-a) | Data; rule 1 | It needs account-level and order-book data the program does not hold. The trend horizon is [unverified], and the source reports attrition ("difficulty maintaining the anticipatory strategies"). |
| X-16 K4-optmom-01 | CL intraday returns predicted from option-implied higher moments (K4-048) | Rule 1; data | Blocked at title only; nothing retrieved. CL options data is not in the plan. |
| X-17 K4-chpmi-01 | CL traded on the Chinese PMI release, "The effect on the crude oil market is also strong with a coefficient of 0.11" (K3-007 P-K3-007-h [K4]) | Rule 3; rule 1 | It is a surprise response against a consensus that is proprietary. With a price proxy, nothing is left to trade: the K3 log reports the impact "appears to be permanent" (first-run passage, not re-checked). The pre-announcement CARs are "available upon request" (P-K3-007-g, [K3] only). |
| X-18 K4-tam-01 | CL, RB or HO around the London Trading-at-Marker minute (K4-047 P-K4-047-a) | Rule 1; D6 | Documentation only: "No source tests whether they carry a price effect" (log). A clock-drift member is D.1 family A, which D6 does not port. The minute is used only in K4-ml-01's window placement. |
| X-19 K4-abnret-01 | Oil momentum after an intraday-detected abnormal daily return, same day and next morning (K5-028 P-K5-028-a, P-K5-028-e, P-K5-028-f [K4]) | Rule 1 (parameters) | The trigger's threshold construction and oil's timing parameters are not in the [K4] passages; only gold's timing is logged (P-K5-028-d [K5]). The data are MetaQuotes broker prices with no named instrument. There are no costs (P-K5-028-c). The same-day continuation is family C (**covered by CP1**), and the next-day follow-through is family H (**covered by CP3**). |

---

## 3. Beyond budget (lead decides)

None. The log supports 6 new members inside the budget of 11. These candidates were considered and
not written (none is a budget overflow):
- **RB and HO versions of K4-apipre-01, K4-eiafade-01 and K4-eiamom-01.**
  - What the log supports: the WPSR moves RB and HO (K4-002), and Topstep lists RB for the crude
    release (F6).
  - What it lacks: each tradeable mechanism (API under-absorption, post-release overreaction, USO
    half-hour momentum) is documented on crude only (K4-009, K4-022, K4-021). Extending them is an
    inference the evidence does not test.
  - Cost: +1 trial per exposure per member, up to 6 (section 7, item 7).
- **A through-release variant of K4-apipre-01.** It would exit at T_W + 10 instead of T_W - 1, on
    the "predict inventory surprises" half of P-K4-009-a. Not written: the release response is
    contemporaneous, and the D9.4 caution applies to any fill near the release. It would be 1 more
    trial.
- **A percent-of-open breakout on CL**, K4-013 / D.1 B4's own formulation ("a predetermined price
    threshold a percentage above/below the opening price", D.1 row B4). Not written: the threshold
    value is in no verified passage (the D.1 row is truncated, and the first reader's K4-013
    passages were never re-verified). The family is covered by CP2.
- **An index-roll member**, which has insufficient evidence (X-08).

---

## 4. Routed to K8

| Source | Legs | One phrase |
|---|---|---|
| Alquist, Ellwanger, Jin (2020), JFM (registry K4-008, not read) | WPSR-identified oil shock (K4) -> equities, Treasuries, FX (K1, K2, K3) | oil inventory news as an instrument for cross-asset responses |
| Alturki, Kurov (2022), K4-009, stock-market leg | CL (K4) and the stock market (K1) | the inefficiency spans CL and stocks; the CL-only part is K4-apipre-01 |
| Quantpedia, "Crude Oil Predicts Equity Returns" (R-K4-004) | crude (K4) -> equity index (K1) | crude as an equity timing signal |
| Basistha, Kurov, Wolfe (2024), J. Commodity Markets | oil (K4), equities (K1), monetary policy (K2) | time-varying causal links |
| JFM 2023 (fut.22410), "Trading around the clock ..." | WTI (K4) and G7 equity indices (K1) | session-specific volatility spillover |
| Rosa (2013), K4-025, the dollar channel; plus X-06's surprise measure | FOMC surprise from fed funds futures (rates) and USD (K3) -> CL, HO, NG (K4) | the energy response to FOMC runs through the dollar; the surprise is a rates instrument |
| J. Banking & Finance (2014), airline stocks | crude returns (K4) -> airline equities (non-CME) | crude returns driving stock trading intensity |
| JFM (2010), corn and crude volatility spillover | CL (K4) and ZC (K6) | ethanol-era volatility spillover |
| J. Agricultural Economics (2025, agr.70089) | WTI (K4) and grains (K6) | volatility spillover |
| Chiang, Hughen, "Do Oil Futures Prices Predict Stock Returns?" | CL (K4) -> equities (K1) | oil futures as an equity predictor |
| Quantpedia, "Financialization of crude oil market" | VIX and S&P 500 (K1) and CL (K4) | financial variables explain crude variance |
| Quantocracy / Milton FMR, "Pairs Trading ... CAD - Crude Oil" | 6C (K3) and CL (K4) | CAD-crude pairs |
| arXiv 1209.0900, biofuels-fuels-food | RB, CL (K4) and ZC, ZW, ZS (K6) | wavelet co-movement, ethanol link |
| Kurov, Stan (2018), K3-035 [K4] | monetary-policy uncertainty (a rates-derived measure) conditioning crude's macro response (K4) | the conditioning variable comes from rates; a CL-only use has no base member (section 5) |

The first 13 rows are the reader's own flags (log section 4). Rows 6 and 14 add this catalog's
routing of X-06 and K3-035.

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K4.md section 3, every `[K4]`-tagged
passage elsewhere, and the status lines for K4's other registry ids.

| Item | Disposition |
|---|---|
| K4-001 Prokopczuk, Wese Simen, Wichmann | Used: K4-ngpre-01 (P-a to g; the post-2011 null P-e is stated as the prior); K4-ml-01 ngs_phase window (P-c) |
| K4-002 Halova Wolfe, Kurov, Kucher | Used: K4-ngrev-01 (event window P-b; response sign P-d); K4-apipre-01 (window convention P-b); K4-ml-01 wpsr_move and ngs_phase (P-b, P-e). The surprise-signed trade is excluded, X-02 |
| K4-003 Bessembinder et al. (USO rolls) | Excluded as a member, X-08 (resiliency P-b, roll cost P-c, TAS P-d). Used in K4-ml-01 gsci_roll (P-c, P-d) and the ML window placement (the settlement window) |
| K4-004 Linn, Zhu | Used for timing only: K4-ml-01's h (P-a). No directional claim, and the open and close effects are from the pit era: insufficient evidence for a member |
| K4-005 Gay, Simkins, Turac | Excluded, X-01 (proprietary analyst data) |
| K4-006 Ederington, Lin, Linn, Yang | Used: K4-ngrev-01 (the week-to-week reversal, P-a). The disagreement-conditioned part is excluded, X-03 |
| K4-007 Miao, Yang (2026) | Insufficient evidence for a member: EIA releases move returns and liquidity with no directional or predictive claim (P-a). It supports the release-time design of the event members |
| K4-009 Alturki, Kurov | Used: K4-apipre-01 (P-a); K4-ml-01 api_move. The stock-market leg is routed to K8 |
| K4-010 Basistha, Kurov | Excluded, X-06 (surprise from rates; K8) and X-07 (scheduled-meeting null, P-c) |
| K4-012 Gu, Kurov | Excluded, X-01 (proprietary predictor). Its reported Sharpe 1.26 is [unverified] per the log |
| K4-013 Holmberg, Lönnbark, Lundström (see D.1 B4) | **Covered by CP2** (family B, ORB on crude). The percent-of-open variant is not written (section 3) |
| K4-014 Ewald et al. (Brent clock seasonality) | Not used: D.1 family A, which D6 does not port. The clock times are not in the passages (abstract only), and the instrument is ICE Brent. Insufficient evidence for a K4 member |
| K4-017 / K4-018 / K4-045 (EIA and API schedule documentation) | Used for timing in every event member (C9) and in K4-ml-01 wpsr_phase, ngs_phase and api_move |
| K4-020 Jang, Lee, Lee (Hawkes, RB and CL) | Excluded as a member, X-12. Used in K4-ml-01 rb_ret30 (P-a, P-d) |
| K4-021 Wen, Indriawan, Lien, Xu | Used: K4-eiamom-01 (P-a to e); K4-ml-01 wpsr_move and the h choice |
| K4-022 Rousse, Sévi | Used: K4-eiafade-01 (P-a, c, d); K4-apipre-01's pre-release window (P-b, P-e); K4-ml-01 wpsr_phase and wpsr_move. The surprise-conditioned pre-release drift needs an ex-ante predictor; the obtainable one is K4-apipre-01's |
| K4-023 Ye, Karali (poster) | Used: K4-apipre-01 (API time and response, P-a, P-b); K4-eiafade-01 (frequency of large responses, P-c; window, P-b); K4-ml-01 api_move and wpsr_move. The API release itself cannot be traded (after F) |
| K4-024 Bjursell, Wang, Zheng (VPIN) | Insufficient evidence for a member: a volatility and toxicity state with no directional claim (P-a). D6 does not port family D gates. B4 in the ML member carries volatility state |
| K4-025 Rosa (FRBNY SR 598) | Excluded, X-06 (surprise from rates, dollar channel; K8) and X-07 (reversal on a handful of LSAP events). Routed to K8 |
| K4-026 Miao, Ramchander, Wang, Yang | Supporting evidence for K4-apipre-01 (day -1 anticipation, P-c). Not intraday-feasible as tested (daily settlement returns). The surprise-signed version is excluded, X-02 |
| K4-027 Pirrong (TAS) | Excluded, X-09 (no public TAS concentration data). Its settlement-window flow enters X-08's reasoning |
| K4-028 Chiou-Wei, Linn, Zhu | Not intraday-feasible as tested (daily). Used as negative evidence against a multi-day NG post-release drift (P-b), in X-02 |
| K4-029 Gu, Kurov, Stan (Friday releases) | Excluded, X-14 |
| K4-030 Liu, Schultz, Swieringa | Excluded as a signal source, X-11. It is evidence against a Brent lead |
| K4-031 Fernandez-Perez, Garel, Indriawan | Not a mechanism: an input evaluation. Used in X-01 to rule out crowd forecasts as a consensus substitute |
| K4-032 Armstrong, Cardella, Sabah | Excluded, X-05 |
| K4-033 Chang, Daouk, Wang | Excluded, X-04. Its 15-minute post-release window (P-a) informs K4-eiafade-01's measurement window and K4-ml-01 wpsr_move |
| K4-034 Dubois, Maréchal | Excluded as a member, X-08 (null after SE adjustment, P-a). Used in K4-ml-01 gsci_roll (roll days, P-b). [K5] and [K6] passages belong to those writers |
| K4-035 Mou (Goldman roll front-running) | Not intraday-feasible: multi-day calendar spreads (P-b). X-08. [K5] and [K6] passages belong to those writers |
| K4-036 Stoll, Whaley | Excluded as a member, X-08. Used in K4-ml-01 gsci_roll (crude roll impact, P-c). [K6] passages belong to K6 |
| K4-037 Wen, Gong, Ma, Xu | **Covered by CP1** (first half-hour, mostly overnight, predicts the last half-hour, P-a). Counter-evidence for K4-eiamom-01 (P-b) |
| K4-038 Song, López de Prado, Simon, Wu | Excluded, X-13 (weather). The TWAP first-second clock (P-a) is seconds-scale and not tradeable under D9 |
| K4-040 Chan, Gray | Insufficient evidence: a null for scheduled macro releases on energy jumps (P-a). Used in X-07 |
| K4-041 Chatrath, Miao, Ramchander | Insufficient evidence: mostly a null for crude's macro-news response (P-a, abstract via OpenAlex). No member |
| K4-042 Baviera, Santagostino Baldi | Excluded, X-10 |
| K4-043 Fett, McPhail (CFTC stop orders) | Background for CP2 (family B): CL has the highest stop-order share (P-b). Descriptive, no member. The [K2] passage belongs to K2 |
| K4-044 Fishe, Haynes, Onur | Excluded, X-15 |
| K4-046 CME OpenMarkets, API and EIA | Supporting (untested practitioner claim) for K4-apipre-01 and api_move (P-a). P-b's 0.6-0.8 correlation is unsourced and unused |
| K4-047 CME TAM FAQ | Excluded as a member, X-18. Used only for K4-ml-01's window placement (P-a) |
| K4-048 Wong (blocked) | Excluded, X-16 |
| K4-049 Ewald, Zhang (blocked) | Insufficient evidence: title only (forward-premium dynamics); nothing retrieved |
| K4-050 Fetna (blocked) | Insufficient evidence: title only. It is relevant as a prior for CP2 if ever retrieved |
| K4-008 | Routed to K8 (the reader's flag; not read) |
| K4-011, K4-015, K4-016 (tagged K4 and K6), K4-019, K4-039 | Rejected in the log (R-K4-019, R-K4-037, R-K4-038, R-K4-039, R-K4-040). Not used. K4-016 (pre-holiday effect, multi-day ETF hold) has no [K6] passage |
| K3-007 [K4] Baum, Kurov, Wolfe (Chinese macro), P-K3-007-h | Excluded, X-17 |
| K3-035 [K4] Kurov, Stan (policy uncertainty), P-K3-035-a | Insufficient evidence as a K4 member: a conditioning variable for macro-release responses, and K4 has no macro-release member (K4-040 and K4-041 are nulls). The uncertainty measure is unspecified and rates-derived, so it is routed to K8 |
| K3-040 [K4] Kosowski et al., "Overnight-Intraday Reversal Everywhere" | Insufficient evidence: title only, content [unverified]. Note that CP1's (a) form bets the opposite way, overnight continuation |
| K5-028 [K4] Caporale, Plastun, P-K5-028-a, b, c, e, f | Excluded as a threshold member, X-19. Its mechanisms are **covered by CP1** (same-day continuation) and **CP3** (next-day follow-through) |
| K5-029 [K4] Borgards, Czudaj, Hoang, P-K5-029-a, b, c, d | Used: K4-ovr-01 (CL, HO, NG); K4-ml-01 ret60_pct |
| `[K4]` search in K2, K6, K7 logs and the K3 and K5 partial logs | No further `[K4]`-tagged passage. The K2 log's mentions are K4-008 and K4-015/016 pointers; K5's R-K5-010 and R-K5-042 are K4-region rejections by K5, not passed items |
| R-K4-001 to R-K4-075 | Rejected at pre-filter or on reading. Not used. R-K4-061 is cited only for C10's guard |

**Correlated members, flagged for the lead's Tier-A accounting (not a duplication).** K4-eiafade-01
and K4-ovr-01's 10:00 decision on WPSR Wednesdays both fade the release move. They use different
windows, thresholds and holds, so they are separate hypotheses. K4-ngpre-01 and K4-ngrev-01 both
hold NG across the storage release: one always short, the other signed by last week's response.

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all four admitted) |
|---|---|---|---|
| K4-cp1-01 | crude, gas, RBOB, ULSD | 1 | 4 |
| K4-cp2-01 | crude, gas, RBOB, ULSD | 1 | 4 |
| K4-cp3-01 | crude, gas, RBOB, ULSD | 1 | 4 |
| K4-ngpre-01 | gas | 1 | 1 |
| K4-ngrev-01 | EXCLUDED by the lead (review R-06) | - | 0 |
| K4-apipre-01 | crude | 1 | 1 |
| K4-eiafade-01 | crude | 1 | 1 |
| K4-eiamom-01 | crude | 1 | 1 |
| K4-ovr-01 | crude, ULSD, gas | 1 | 3 |
| K4-ml-01 | crude (no fallback) | 48 in research-window accounting only (D15.8) | 1 |
| **Cluster total** | | | **21** = 12 port + 8 new + 1 ML. In general 3E + 5a_C + 3a_G + a_H. Without RBOB and ULSD: 14. Crude only: 8 |

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **MCL's unresolved * restriction.**
   - Every crude member carries the MCL flag (D9.8), because D2 may pick MCL for crude.
   - If the user cannot clear it before E.1, D2 must choose between CL and QM.
   - K4-ml-01 has no fallback exposure.
2. **CP2's buffer and the ML features are in the vehicle's ticks.**
   - QM's tick (0.025) is 2.5 times CL's and MCL's (0.01). QG's (0.005) is 5 times NG's and MNG's
     (0.001).
   - So CP2's trades on one underlying depend on which contract D2 picks, while every new member is
     tick-free (C8).
   - The text is copied unchanged from D6. The lead decides whether the port's "4 ticks of P" means
     the vehicle's tick (the literal reading, used here) or the full-size contract's tick for every
     contract of an exposure.
3. **CP1 enters at the FOMC statement minute on energy.**
   - With C = 13:30 the entry fill is the 13:00 open, which on scheduled FOMC days is the statement
     minute.
   - This is copied verbatim and allowed at 1 lot-equivalent. The lead decides whether energy ports
     skip FOMC days, which would be a D6 change.
4. **Event-member frequency (C11).**
   - Five of the six new members trade weekly or less: K4-ngpre-01, K4-ngrev-01, K4-apipre-01 and
     K4-eiamom-01 on about 18-21% of dates, and K4-eiafade-01 on about 5%.
   - By arithmetic they need about 5 x eps_X (weekly) and about 20 x eps_X (K4-eiafade-01) per event
     to reach eps_X a day. They are likely "null at eps" or "inconclusive by design" (D4).
   - They cost 5 trials. The lead decides whether they stay at one trial each.
5. **Cost sample for gas.** D8's five dates are all Wednesdays, so NG's Thursday release minute is
   never sampled (C12). The lead decides whether to add a Thursday to the gas vehicles' mbp-1 sample
   (a small spend, quoted in E.1), or to accept a possibly understated release-window cost for
   K4-ngpre-01 and K4-ngrev-01.
6. **K4-ngpre-01's binding evidence is its own authors' null after 2011** (P-K4-001-e). It is
   written because it is the log's only fully specified, full-text, energy-specific intraday rule
   with a stated window. The lead may cut it (1 trial).
7. **RB and HO extensions.** Extending K4-apipre-01, K4-eiafade-01 and K4-eiamom-01 to RB and HO
   is not written: the evidence is for crude only. Adding them would cost up to 6 trials (section 3).
8. **Index roll (X-08).** If the lead wants a K4 roll member once E.2 fixes the roll convention, it
   needs three things first: the S&P GSCI per-commodity contract schedule logged, a verified
   intraday source, and a check that the roll blackout leaves the 5th-9th trade dates in play.
9. **Unfinished research seed.** The reader could not run the weather-model-update search for
   natural gas (search tools exhausted). No gas weather member exists (X-13).
10. **E.2 checks named in this catalog:**
    - (a) EC-WPSR and EC-NGS tables from the yearly Wayback captures (C9), cross-checked against
      actual publication, with the drop rules of C9.
    - (b) EC-NYSE early closes (K4-eiamom-01).
    - (c) Standard-week Mondays against the federal holiday list (EC-API).
    - (d) Tick-size history 2019-2026 (C7).
    - (e) NYMEX dynamic circuit breakers against Topstep's 2% price-lock rule (C13).
    - (f) Member-level coverage for the off-day-session windows: 07:15-08:00 (K4-ml-01), 07:30
      (K4-apipre-01), Tuesday 15:24-15:39 (K4-apipre-01's signal) and 14:30-14:59 (K4-eiamom-01).
    - (g) The C10 guard against the April 2020 bars.
    - (h) MCL's and MNG's short histories and the full-size price-path declaration (C8; D2 and D4).
    - (i) How TopstepX counts QM and QG against the lot limit (C6).
    - (j) RB history for K4-ml-01 if RBOB is not admitted.
11. **Registry hygiene** (already noted by the reader): the author fields for K4-042 ("Lipton?";
    correct: Baviera and Santagostino Baldi) and K4-044 (correct: Fishe, Haynes and Onur) are wrong.
    K4-039 was claimed before it was rejected.
