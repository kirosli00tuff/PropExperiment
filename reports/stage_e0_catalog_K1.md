# Stage E.0 hypothesis catalog, cluster K1 (equity index: MNQ, NQ, M2K, RTY, MYM, YM)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K1-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials. U3: K1 runs only if the user decides, after K7, that it is needed; its members stay in the frozen catalog so that a later K1 session is pre-registered.
> **K1 after the decisions: 5 active members, 11 confirmation trials** (2 new + 3 core ports; 9 port + 2 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K1-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from about 01:30 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any K1 product existed on this machine.
- The MES bars on disk were not opened. No MES result table was read. The only MES result used is
  the class-level statement in commit ca8befb ("Stage D.1f run, MES classes C1-C5 and C7 null on
  2020-02-03..2024-02-29"), with docs/NULL_CRITERIA.md as the definition of "null".
- Product-specific numbers used: contract specifications and public ADV
  (reports/stage_e0_liquidity.json; the design D1 table), Topstep's fees, hours and rules
  (reports/stage_e0_topstep_facts.md), and event-calendar metadata (ISM release dates and clock
  time).
- No price level, range or volatility of any instrument is used or assumed below, and no VXN or VIX
  value either.

**Inputs read in full:**
- reports/stage_e0_research_K1.md.
- Every `[K1]`-tagged passage in the other logs:
  - K2-007 and K2-015 in reports/stage_e0_research_K2.md;
  - K3-007, K3-030, K3-035 and K3-040 in reports/stage_e0_research_K3.md;
  - the K4-043 and K4-050 entries and the K1-leg flags in reports/stage_e0_research_K4.md;
  - the K8 entries with a K1 leg in reports/stage_e0_research_K8.md.
  - The K5, K6 and K7 logs hold no `[K1]`-tagged passage, only K8 flags. The superseded sonnet
    partial logs were not used.
- reports/stage_e0_source_registry.jsonl (the K1 lines and every line tagged K1).
- The D.1 literature log (432f46d4.../d1/task1_log.md).
- reports/stage_d1f_confirmation_list.md: sections 0 to 2, and 2.1 A3 in full.
- docs/STAGE_E_DESIGN.md (D1-D15, with the amendments of 21:12, 21:52 and 01:40 PDT).
- reports/stage_e0_partition.md.
- reports/stage_e0_topstep_facts.md: F1 to F6 and F12.
- reports/stage_e0_liquidity.json: the K1 rows.
- MES modules named in D6:
  - strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py;
  - strategy/research/h_daily_bar/h6_prior_close_location.py and _mechanics.py (constants);
  - reports/stage_d1b_family_f_declaration.md F3.3.
- Docstrings only, to check for duplicates: the MES modules e_calendar_event/h1 and h2,
  c_short_horizon_reversal/h1 and d_volatility_state/h1.
- For format only: reports/stage_e0_catalog_K4.md and reports/stage_e0_catalog_K3.md.

**Official pages fetched in this task** (curl, 2026-09-24 01:51-01:58 PDT). Fetches were limited to
confirming data availability and release times. No mechanism research was done and no index value
was downloaded. Saved copies are in the session scratchpad under fetch/, not in the repository.
1. `curl -sI` (headers only, no body) of
   https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv: "HTTP/2 200",
   "content-type: text/csv", "content-length: 218502", "last-modified: Wed, 23 Sep 2026 01:51:09 GMT".
2. `curl -sI` of https://cdn.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv: "HTTP/2 200",
   "content-type: text/csv", "content-length: 472921", same last-modified.
3. `curl -sI` of https://fred.stlouisfed.org/series/VXNCLS and .../VIXCLS: no status line returned, so
   the FRED copies are **not confirmed**.
4. https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/ redirects to
   an SSO login page, so the calendar could not be read directly.
5. Wayback CDX of that page returned 26 captures, 2020-08-09 to 2026-08-04 (collapsed by month).
   Two were read:
   - http://web.archive.org/web/20260415040000id_/https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/
     says: "The ISM Services PMI® Report is released on the third business day of the month at 10:00
     a.m. (EST)." Its 2026 table lists every month's date, with the footnote "**Services PMI moved
     due to 4th of July holiday observed on July 3, 2026".
   - http://web.archive.org/web/20200809022121id_/https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/
     says: "The Services ISM Report On Business® is released on the third business day of the month
     at 10:00 a.m. (EST)."
6. Wayback CDX of lseg.com/en/ftse-russell/russell-reconstitution*. One capture was read:
   http://web.archive.org/web/20251214041535id_/https://www.lseg.com/en/ftse-russell/russell-reconstitution?kui=pap7J6zdqa-iS3776etidA
   - It says: "Following market consultation, FTSE Russell has announced the reconstitution of the
     Russell US Indexes will change from an annual to a semi-annual schedule in 2026."
   - The lines matched do not name the second 2026 month, so the log's November-against-December
     conflict (K1-018 against K1-023) stays open. No member depends on it.

---

## 0. Header

| Item | Value |
|---|---|
| Products | MNQ*, NQ, M2K*, RTY, MYM*, YM (Topstep F1; * = starred) |
| Exposures IN | Nasdaq-100 {MNQ, NQ}; Russell 2000 {RTY, M2K}; Dow {MYM, YM}. Design D1 table, 2026 Jan-Aug ADV: MNQ 2,363,465, NQ 593,595; RTY 209,871, M2K 115,832; MYM 152,686, YM 108,142. Coverage 1.000 for each exposure |
| **D1 applied: NKD out; S&P leg only** | NKD fails D1(a) (7,969) and D1(b) (0.621), so no member trades or reads it. ES and MES are closed (D1.5). MES bars, already owned, appear only as a signal leg in K1-ml-01, and only on research-window and confirmation-window dates, never holdout dates. No member trades ES or MES |
| Members | **7 = 3 new + 3 core ports + 1 ML member.** The budget is 15 (at most 11 new), so 8 slots are unused (section 3) |
| Trials in N (confirmation) | **13 if D2 admits all three exposures:** 9 port + 3 new + 1 ML. In general 3E + 3a_N + a_D, where E is the number of admitted exposures and a_N, a_D are 1 if the Nasdaq-100 and the Dow are admitted |
| ML grid | ~~48 configurations, counted only in the K1 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Starred products and the rules that apply | **MNQ, M2K, MYM** are starred (F1). Their referent is Topstep's "Risk Adjustments: High Risk/High Volatility" article (F12.1), which names them, and D9.8 encodes it through D9.11 and D9.12. So, unlike M6E and M6A, they stay D2 candidates. **D9.12 CPI window:** opening transactions in [CPI - 5 min, CPI + 5 min] are limited to 3 contracts on MNQ, M2K and MYM, and are not allowed at all on NQ, RTY and YM. CPI is released at 07:30 CT, so the window is 07:25-07:35 CT. No K1 member fills before 08:31 CT, so the window never binds (checked in every entry). **D9.11:** no equity-index position figure is published. The same page says "Trading on mini-sized contracts or larger may be temporarily halted for affected products" (F12.1), a deployability risk if D2 picks NQ, RTY or YM (section 7) |
| D2 | Every entry says "D2 (chosen in E.2)". Within each exposure, the micro and the mini quote the same index in the same tick size in points (C7), so a rule makes the same decisions on either vehicle; only size, cost and tick value differ. Every entry is **traded only if D2 admits the exposure** |

### Common conventions (they apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.**
  - Times are America/Chicago (CT).
  - "The bar at hh:mm" is the ohlcv-1m bar whose ts_event (its open) is hh:mm:00 CT (D.1f
    convention H-8). It closes at hh:mm + 1 min, and its values are usable from then on.
  - Eastern-time releases convert to CT by subtracting one hour; both zones change clocks on the
    same dates.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine
  convention D6 and D15.3 use).
- **C3 Trade date.** d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md, line 40). "The
  trade date's first bar" is the 17:00 CT bar of d-1 (Sunday's for a Monday).
- **C4 Exclusions for the three new members.** The ports follow D6 as written. A new member does
  not trade on:
  - roll-blackout dates ("The splice trade date plus the 2 sessions before it", docs/SCREENING.md);
  - dates that the D10 equity calendar marks as an early close or early halt (Family H: "Days with
    early_halt_ct set: no trade");
  - dates on which a bar the rule reads, or the entry bar, is missing, or on which the bars of one
    computation or one position carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced
  flatten at F is the backstop.
- **C5 Flat time.**
  - F = 15:08 CT (D9.1). D6 equity row: O = 08:30, C = 15:00, F = 15:08.
  - No new member's last fill is later than 14:59 CT; K1-ml-01's is 14:35.
  - Early-close days: F = the early close minus 15 minutes (D9.1; F12.3: "Close all positions 15
    minutes before early close"). The new members do not trade on those days (C4).
- **C6 Size.** q_c of the exposure's D2 vehicle, at most 1 lot-equivalent (D2; D9.5).
  - Micros count 0.1 and minis 1 (D9.6), so q_c <= 10 on a micro and q_c = 1 on a mini.
  - No member sizes by signal.
- **C7 Ticks, fees and rulebook chapters.**
  - Sources: tick size, tick value and rulebook chapter from reports/stage_e0_liquidity.json (CME
    contract specifications, fetched 2026-09-23 20:41-20:42 PDT); round turns from Topstep F3.

  | Contract | Exposure | Tick (index points) | Tick value | Topstep round turn | Lot-equivalent | Rulebook |
  |---|---|---|---|---|---|---|
  | MNQ* | Nasdaq-100 | 0.25 | $0.50 | $1.22 | 0.1 | CME 361 |
  | NQ | Nasdaq-100 | 0.25 | $5.00 | $3.78 | 1 | CME 359 |
  | M2K* | Russell 2000 | 0.10 | $0.50 | $1.22 | 0.1 | CME 363 |
  | RTY | Russell 2000 | 0.10 | $5.00 | $3.78 | 1 | CME 393 |
  | MYM* | Dow | 1.0 | $0.50 | $1.22 | 0.1 | CBOT 28 |
  | YM | Dow | 1.00 | $5.00 | $3.78 | 1 | CBOT 27 |

  - These are 2026 specifications. E.2 confirms that each tick was unchanged over 2019-05..2026-06
    before any bar is read, because CP2's buffer and several ML features are in ticks.
- **C8 Price data.**
  - Source: Databento GLBX.MDP3 ohlcv-1m of the vehicle. It is paid: the research window is bought
    in E.1, and the confirmation and holdout-2 history of the chosen vehicle in E.2b (D13).
  - Listing dates (liquidity JSON): MNQ, M2K and MYM 2019-05-06 (CME press release: "announced the
    successful launch of its new Micro E-mini futures"); NQ 1999-06-21; RTY 2017-07-10 (a
    planned-date announcement); YM 2002-04 (month only).
  - D2 and D4 let E.2 declare the full-size contract's bars as the price path of a micro vehicle.
  - A bar is available at its close (C1).
  - Every new-member rule compares prices as percentages, signs or VWAP deviations, so it decides
    the same way on either contract of an exposure. Tick-denominated quantities appear only in CP2's
    buffer and in the ML features.
- **C9 External data read by any K1 member** (other than the vehicle's own bars):
  - **VXN** (Cboe Nasdaq-100 Volatility Index), daily close.
    - Source: Cboe's public daily file (fetch 1: HTTP 200, text/csv, 218,502 bytes). It is free.
    - E.2 confirms, when it builds the input, that the file covers 2019-04-30..2026-06-18 (every
      trade date before a research or confirmation date). The file size implies thousands of
      daily rows [inference]; no row was read.
    - FRED VXNCLS is a possible second copy, not confirmed (fetch 3).
    - Availability: the close of trade date d-1 is used only from 08:30 CT on d. Cboe's exact
      publication time is [unverified]; E.2 confirms it.
    - Used by K1-vxnband-01 and K1-ml-01.
  - **ISM Services (formerly Non-Manufacturing) PMI release calendar.** Dates and clock time only;
    no released value is read.
    - Source: ISM's "Report Release Date Calendar" (fetch 4-5). It is free through Wayback: 26
      captures, 2020-08-09..2026-08-04.
    - The tables for 2019-05..2020-07 are not confirmed in E.0. E.2 sources them, for example from
      captures of ISM's earlier URL or from ISM's press-release record.
    - Rule: "released on the third business day of the month at 10:00 a.m. (EST)". The page writes
      "(EST)" year-round; it is read as US Eastern clock time [inference], that is 09:00 CT. E.2
      confirms this against actual publication times.
    - Each year's table is published ahead of the year: the 2026-04-15 capture already lists every
      2026 date through December.
    - Used by K1-predrift-01. The rename from "Non-Manufacturing" to "Services" is taken to be the
      same report [inference: the 2020 capture already says "Services ISM Report On Business"; the
      source paper uses the Non-Manufacturing name for 2008-2014]. E.2 confirms the continuity.
  - **MES ohlcv-1m bars**: owned; built in D.1f for the research window (2025-04-01..2026-06-19) and
    the confirmation window (2019-05..2024-02). Used only by K1-ml-01, never on a holdout date.
    Not opened in E.0.
  - **The Russell 2000 vehicle's bars** (or the price path declared for it): paid, as in C8. Used
    only by K1-ml-01.
  - **Not read by any member.** Their availability is stated here because the brief's rule 3 asks
    for it:
    - VIX daily: Cboe's public file, free (fetch 2).
    - Cash-index levels (Nasdaq-100, Russell 2000, DJIA): no member needs them. Every member uses
      the futures' own bars. A free intraday history was not searched for in E.0 [not checked].
    - Index reconstitution calendars:
      - FTSE Russell publishes its schedule in advance (the lseg.com reconstitution page, fetch 6;
        P-K1-018-c gives the 2025 rank day and effective date). The Nov-Dec 2026 conflict is open.
      - Nasdaq-100 reconstitution dates follow Nasdaq's index methodology, which was not fetched.
      - No member uses either calendar (X-03, X-04). Were one ever used, its dates must come from
        these published schedules, never from volume.
    - NYSE closing-auction imbalance messages (K1-024): paid Databento US Equities data, not in the
      spend plan; the history start is not confirmed. Not used (X-05).
- **C10 Releases inside the K1 session.**
  - Topstep's release table (F6) has "Unemployment Rate | 7:30 AM | ES, NKD, NQ, ... YM, ... RTY,
    ..." (before the 08:30 open, so no K1 fill can meet it) and "FOMC Statement | 1:00 PM | All
    products".
  - K1-predrift-01 names the ISM Services release at 09:00 CT for the Dow exposure. The D9.5a guard
    and the D8 event-window cost therefore apply to the Dow at [09:00, 09:02) and [09:00, 09:30).
  - D9.5a event-minute fill guard: any K1 fill that would land in [13:00, 13:02) on a scheduled FOMC
    day fills at the 13:02 open. The same holds at [09:00, 09:02) on ISM Services days for the Dow.
  - D8 event-window cost: fills in [13:00, 13:30) on FOMC days pay the largest s_b of the product's
    buckets. So do Dow fills in [09:00, 09:30) on ISM Services days.
  - Whether ISM Services also concerns NQ and RTY (for the guard and the cost) is the lead's
    decision (section 7, item 6).
  - CPI: D9.12, as in the header; it never binds.
- **C11 Price-limit proximity (D9.7).**
  - Topstep F12.1: "Equity products ES, MES, NQ, MNQ, RTY, M2K, YM, and MYM overnight price limits
    have expanded from 5% to 7%".
  - E.2 builds the K1 limit tables from the rulebook chapters in C7: the overnight and
    regular-hours limits, their reference prices, and their 2019-2026 history.
  - Every K1 member obeys the encoded rule: no entry, and an immediate exit, while the price is
    within 2% of the day's limit price. No K1 rule reads a limit.
- **C12 Frequency (arithmetic from calendar counts only).**
  - The research window 2025-04-01..2026-06-19 has 319 weekdays (about 305 CME trade dates).
  - The confirmation window from the earliest S_X (2019-05-06) to 2024-02-29 has 1,259 weekdays.
  - The equity-index quarterly roll blacks out about 12 trade dates a year (4 rolls x 3 dates).

---

## 1. Members

### K1-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K1. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures** (each a separate trial, each traded only if D2 admits it): Nasdaq-100
  {MNQ, NQ}, Russell 2000 {RTY, M2K}, Dow {MYM, YM}. **Vehicle:** D2 (chosen in E.2).
- **Session constants** (D6 equity row): O = 08:30, C = 15:00, F = 15:08 CT.
- **Mechanism:** port of MES F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log A10
  and A28; reports/stage_d1b_family_f_declaration.md F3.3), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the
    trade date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open),
    in the signal's direction; zero signal, no trade. Exit: market intent on the first bar at or
    after C-2 min (fills at the next open). Both signal bars must exist with one instrument_id, else
    no trade."
  - **Covered by CP1.** D.1 A10 (Baltussen, Da, Lammers, Martens) is on-instrument for NQ ("Directly
    on-instrument (S&P E-mini, NQ)", D.1 log row A10; cited by the K1 log's header, not re-read).
    Three K1-log rejections are this family: R-K1-067 (Shum et al., LETF close hedging, "the LETF
    close-hedging mechanism is D.1 A10's"), R-K1-068 (Rosa 2022, "D.1 A10/A28 family, generic") and
    R-K1-069 (Baltussen et al. 2021, "see D.1 A10").
  - **Conflicting evidence:** K3-040 (Kosowski et al., "Overnight-Intraday Reversal Everywhere",
    registry-tagged K1; title only, content [unverified]) says the overnight return reverses
    intraday. That is the opposite sign to CP1's (a) form, whose signal is mostly the overnight
    move.
- **MES record:** the same family was null on MES. docs/NULL_CRITERIA.md defines the statement; the
  D.1f result is commit ca8befb, "MES classes C1-C5 and C7 null on 2020-02-03..2024-02-29", and
  F3.3 is class C3. The sibling indices are highly correlated with the S&P (the lead's note; no
  correlation figure is logged or computed here), so these three trials are close to the MES record.
- **Instantiated:**
  - **Signal:** close of the bar at 08:59 minus the open of the trade date's first bar (the 17:00 CT
    bar of d-1, C3).
  - **Entry:** market intent on the bar at 14:29 in the signal's direction, filling at the 14:30
    open. A zero signal means no trade.
  - **Exit:** market intent on the first bar at or after 14:58, filling at the 14:59 open.
  - **Holding horizon:** 29 minutes. **Session window:** 14:30-14:59 CT. Flat well before F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8; paid; history
  2019-05..2026-06). The latest signal input, the 08:59 bar, is available at 09:00 CT.
- **Order type:** market. **Sizing:** q_c of the D2 vehicle (C6).
- **Parameters:** O+29 = 08:59, C-31 = 14:29, C-2 = 14:58 (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29 minutes.
  Floor: at most 20 entries a day, ok; 2-minute minimum hold, ok; 10-minute mean hold, ok.
- **Falsification:** the standard condition only (a port; D6 is unchanged). UCB95 of the member's
  mean net daily P&L per contract below eps_X, at >= 80% achieved null power on the confirmation
  window, counts against it.
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: one trade a day; no stops, brackets or passive fills.
  4. Star rules (D9.8, D9.12): MNQ, M2K and MYM are starred. The CPI window is never touched (fills
     at 14:30 and 14:59). D9.11 has no equity figure. The mini-halt note applies if D2 picks a mini.
  5. News: 1 lot-equivalent at most. No Topstep-table release falls in 14:30-14:59.
  6. Event-minute guard: no fill can land in [13:00, 13:02) or [09:00, 09:02).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
- **Data needed:** ohlcv-1m of each admitted K1 vehicle over the research window 2025-04-01..2026-06-19
  and the confirmation window S_X..2024-02-29 (D4), including the 17:00 CT reopen bar that the signal
  reads. No external data.
- **Trials in N:** 3 (one per admitted exposure).

### K1-cp2-01 (core port CP2, opening-range breakout)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP on the Nasdaq-100 trial: the 75-minute hold came from Mesfin's MNQ result (D.1 B5), whose sample window is not recorded; treated as overlapping until E.1 records it.]
- **Cluster** K1. **Products read:** own vehicle.
- **Exposures:** Nasdaq-100, Russell 2000, Dow, one trial each, each traded only if D2 admits it.
  **Vehicle:** D2 (chosen in E.2).
- **Session constants:** O = 08:30, C = 15:00, F = 15:08 CT.
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py,
  hold_minutes = 75), as fixed in D6 row CP2 with the 21:12 amendment and the 21:52 buffer ruling.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first
    bar opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P;
    market intent in the break direction; one entry per trade date; no entry from C on. Exit: 75
    minutes after the fill, or the engine's forced flatten at F if earlier." The ruling adds: "'4
    ticks of P' in CP2 means 4 minimum price increments of the exposure's most active contract (D1
    table), in price units, fixed whatever vehicle D2 chooses."
  - **Covered by CP2:**
    - K1-026 (Zarattini and Aziz, a 5-minute opening-range rule on QQQ): family B on the Nasdaq-100.
      Its stop and 10R target are excluded by the brief's rule 4 (X-06).
    - K1-013 (ICT liquidity sweeps on MNQ): family B, no evidential weight (X-08).
    - R-K1-079 (Pineda, the QQQ ORB retest): descriptive.
    - D.1 B4 and B8 (ORB on index futures).
  - **MNQ-specific prior already in the program:** D.1 B5 (Mesfin, arXiv 2605.04004, ORB on MNQ). The
    MES B-H1 module's pre-registration quotes it: HOLD_MINUTES = 5 "did NOT clear friction
    (T=-0.82)"; HOLD_MINUTES = 75 "cleared friction on the point estimate (T=0.88) for MNQ's lower
    cost structure" (Mesfin 2026, Table 4, as cited in that docstring).
  - **Counter-evidence:** R-K1-078 (Fetna 2026, "Opening-range breakout does not survive trading
    costs", a pre-registered study on nine futures including equity indices). Its abstract is
    reachable through Crossref, but no [K1] passage is logged.
- **MES record:** B-H1 hold 75 is class C2, which was null on MES (docs/NULL_CRITERIA.md; D.1f,
  commit ca8befb). Given the siblings' correlation with the S&P (the lead's note), these trials are
  close to the MES record.
- **Instantiated:**
  - **Opening range:** the bars opening in [08:30, 08:45).
  - **Eligible entry bars:** those opening in [08:45, 15:00). No entry from 15:00 CT on.
  - **Buffer:** 4 ticks of the exposure's most active contract (D1 table). Micro and mini share
    the tick in points, so the buffer does not depend on the vehicle.

    | Exposure | Most active contract (D1) | Buffer | Per contract (micro / mini) |
    |---|---|---|---|
    | Nasdaq-100 | MNQ, tick 0.25 | 1.00 index point | $2.00 MNQ / $20.00 NQ |
    | Russell 2000 | RTY, tick 0.10 | 0.40 index point | $2.00 M2K / $20.00 RTY |
    | Dow | MYM, tick 1.0 | 4 index points | $2.00 MYM / $20.00 YM |

  - **Entry:** the first eligible bar whose close is >= OR_high + buffer buys; one whose close is
    <= OR_low - buffer sells. The comparisons are non-strict, as in the MES module. One entry per
    trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it: the exit intent is
    emitted on the 75th bar after the entry-intent bar and fills at the next open. The engine's
    flatten at F applies to entries filled after 13:53, so the shortest possible hold is 8 minutes
    (a fill at 15:00 flattened at 15:08).
  - **Holding horizon:** 75 minutes, shorter only when F binds. **Session window:** 08:46 to 15:08
    at the latest.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is
  known at 08:45 CT.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** OR 15 minutes, buffer 4 ticks of the most active contract, hold 75 minutes (D6, a
  literal port). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held 75 minutes (at least 8). Floor ok; the
  10-minute mean is checked at screening.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: yes, by the forced flatten at the latest.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. Star rules: CPI window not touched (the earliest fill is 08:46); mini-halt note.
  5. News: <= 1 lot-equivalent. A position may be open at the 13:00 FOMC statement, which F6.3
     allows below full maximum size.
  6. Event-minute guard: an entry or exit fill landing in [13:00, 13:02) on an FOMC day fills at
     13:02. Dow fills in [09:00, 09:02) on ISM Services days do the same (C10).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows.
- **Trials in N:** 3.

### K1-cp3-01 (core port CP3, prior-close location)
- **Cluster** K1. **Products read:** own vehicle.
- **Exposures:** Nasdaq-100, Russell 2000, Dow, each traded only if D2 admits it. **Vehicle:** D2
  (chosen in E.2).
- **Session constants:** O = 08:30, C = 15:00, F = 15:08 CT.
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L
    over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as
    Family H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells,
    market intent on the O bar of day d. Exit: first bar at or after C-2 min."
  - **Same clock as MES H6.** The equity row gives exactly the H6 module's constants (08:30 open,
    [08:30, 15:00) range, 14:59 close, 14:58 exit), so this port is H6 verbatim on the sibling
    indices.
  - **K1 log:** no passed item is H6. K1-002 (daily MACD) is a family H construction but not H6.
    D6 ports H6 only, so K1-002 is not covered (X-13).
- **MES record:** H6 is class C7, which was null on MES (docs/NULL_CRITERIA.md; D.1f, commit ca8befb).
  Given the siblings' correlation with the S&P (the lead's note), these trials are close to the MES
  record.
- **Instantiated:**
  - **Daily bar:** O_d = open of the 08:30 bar. H and L are taken over the bars opening in
    [08:30, 15:00). C_d = close of the 14:59 bar.
  - **Complete day** (Family H): the 08:30 and 14:59 bars exist, the date is not an early halt, and
    every bar in [08:30, 15:00) carries one instrument_id.
  - **Instrument guard:** d-1's bar carries the instrument_id of day d's 08:30 bar.
  - **CLV:** computed in ticks, with Range[d-1] > 0. CLV >= 0.8 buys and CLV <= 0.2 sells
    (non-strict, as H6).
  - **Entry:** market intent on the 08:30 bar of d, filling at the 08:31 open.
  - **Exit:** market intent on the first bar at or after 14:58, filling at the 14:59 open.
  - **Holding horizon:** 388 minutes. **Session window:** 08:31-14:59.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's
  bar is complete at 15:00 CT on d-1.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held 388 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: ok.
  4. Star rules: the CPI window is never touched (the entry is 08:31); mini-halt note.
  5. News: holds through the 13:00 FOMC statement and the 09:00 ISM release at <= 1 lot-equivalent,
     below the full maximum (D9.5).
  6. Event-minute guard: no fill lands in a release minute (08:31 and 14:59).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows.
- **Trials in N:** 3.

### K1-vxnband-01 (Nasdaq-100: fade a breach of the VXN/16 band, only at VXN extremes)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source (Seeck) covers 2018-2026 with an out-of-sample 2023-2026, overlapping both the confirmation and the research windows (docs/NULL_CRITERIA_E.md section 3).]
- **Cluster** K1. **Products read:** the Nasdaq-100 vehicle's bars and the VXN daily close (C9).
- **Traded exposure:** Nasdaq-100 {MNQ, NQ} only; the source tests NQ. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:** when NQ moves beyond a band of plus or minus one implied daily standard deviation
  (VXN/16) around the prior close, the move tends to revert before the session closes. A fade with
  a 30-minute exit earns only when VXN is at an extreme.
  - K1-005 (Seeck 2026, abstract only), P-K1-005-a: "The band is set daily as ± VXN/16 relative to
    the prior-session close; dividing by 16 converts the annualised VXN to a one-day
    standard-deviation estimate."
  - P-K1-005-b: "the 30-minute exit rule generates positive Sharpe only at the extremes (VXN < 20:
    0.38; VXN >= 30: 0.64), with slightly negative values in between. Walk-forward validation
    confirms the pattern out of sample (IS 2018–2022, n = 298, Sharpe = 0.47; OOS 2023–2026, n =
    191, Sharpe = 1.29)."
  - **Support for the band scale:** K1-006 P-K1-006-a. Using prior-day VIX, "The estimated slope is
    1.001" for the Nasdaq-100's maximum one-sided excursion from the open on VIX/√252. An
    implied-volatility index divided by about 16 therefore sizes the Nasdaq-100's typical daily
    excursion.
  - **Support for the high-VXN side:** K1-025 P-K1-025-b, "very high levels of implied volatility
    can on a statistical basis be viewed as signalling an imminent increase in stock indices, at
    least on a short term basis". This fits fading downside breaches when VXN >= 30 [inference].
  - **New to the program.** The log tags this as a port of D.1 families C and D with a new element:
    the band and the regime come from an external implied-volatility index. It is not an MES re-run:
    - MES C-H1 fades only small-to-moderate moves: "Large moves are deliberately NOT faded"
      (C-H1 module docstring).
    - MES D-H1 gates on trailing realized volatility.
    - MES D-H4 fades the overnight gap at the open.
    - This member reads an implied-volatility index, fades moves beyond one implied daily standard
      deviation at any RTH minute, and trades only at the index's extremes.
- **Conflicting evidence and quality:**
  - Abstract only (SSRN returned 403); single author.
  - The Sharpe ratio is non-monotone across the VXN buckets ("slightly negative values in between",
    P-K1-005-b).
  - "A pre-sample from 2010–2017 gives a Sharpe of -0.94 without the regime filter" (P-K1-005-b).
  - The 85.2% "reversion rate" (P-K1-005-a) is a touch-back rate, not a P&L.
  - The bucket edges 20 and 30 and the IS/OOS split are the author's own choices.
- **Definitions (day d):**
  - C_prev = close of the vehicle's 14:59 bar on the previous complete trade date (Family H
    completeness). Instrument guard: that bar carries the instrument_id of d's 08:30 bar; otherwise
    no trade on d.
  - V = the Cboe VXN close for the calendar date of trade date d-1. If it is missing, no trade on d.
  - w = C_prev x V / 1600. The band is U = C_prev + w and L = C_prev - w.
- **Regime condition:** trade on d only if V < 20 or V >= 30.
- **Entry rule:** on the first bar opening in [08:30, 14:29) whose close is > U, SELL q_c; whose
  close is < L, BUY q_c (market intent, filling at the next open). At most one entry per trade date:
  the first breach on either side.
- **Exit rule:** market intent on the 30th bar after the entry-intent bar, filling 30 minutes after
  the entry fill. The latest entry-intent bar is 14:28, which fills at 14:29 and exits at 14:59.
- **Holding horizon:** 30 minutes. **Session window:** 08:31-14:59 CT. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m close and instrument_id (C8; paid; history 2019-05..2026-06). C_prev is
    available at 15:00 CT on d-1.
  - VXN daily close: Cboe's public file (C9; free; E.2 confirms coverage 2019-04-30..2026-06-18).
    It is used from 08:30 CT on d.
- **Order type:** market. **Sizing:** q_c.
- **Parameters (every value):**
  - 16 (P-K1-005-a). 1600 = 100 x 16, because VXN is quoted in percentage points (P-K1-005-a).
  - VXN cuts 20 (strict) and 30 (non-strict), exactly as P-K1-005-b writes them.
  - Hold 30 minutes (P-K1-005-b).
  - Entry-intent bars opening in [08:30, 14:29). Judgment: every hold then ends by the 14:59 fill,
    before the settlement minute.
  - C_prev = the 14:59 bar close. Judgment: the abstract does not define "prior-session close"
    further. The RTH close is the program's daily-bar close (CP3's C_d) and the futures close
    nearest in time to VXN's own daily close.
  - RTH bars only (judgment, for the same reason).
  - Strict breach inequalities (judgment: "beyond" the band).
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per trade date, held 30 minutes.
  - P-K1-005-b's counts (298 events in 2018-2022 and 191 in 2023-2026) imply roughly 0.2-0.25
    entries per trade date, if the counts are the extreme-bucket events [inference]. If they
    include every bucket, the member trades less.
  - Floor ok: 1 entry a day at most, holds of 30 minutes.
- **Falsification:**
  - The standard condition.
  - Member-specific (descriptive, not a separate trial): report the confirmation-window mean net P&L
    separately for V < 20 days and V >= 30 days. The source claims both extremes are positive
    (P-K1-005-b), so a negative mean in either regime counts against the mechanism as sourced.
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: one trade a day, no stops. A breach can occur at the 08:30 bar after a gap. The fill is
     still the engine's next-open fill with modelled slippage, not a stray fill, so this is not the
     "reckless trades in gapped markets" pattern [judgment].
  4. Star rules: MNQ is starred. The CPI window is never touched (the earliest fill is 08:31).
     Mini-halt note if D2 picks NQ.
  5. News: <= 1 lot-equivalent.
  6. Event-minute guard: an entry or exit fill landing in [13:00, 13:02) on an FOMC day fills at
     13:02. D8 charges the event-window cost on fills in [13:00, 13:30).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11. On V >= 30 days the 2% proximity rule and Topstep's temporary mini halts
     are the most likely to bind. Both skip or cut trades and are part of the member as deployed.
- **Data needed:**
  - Nasdaq-100 vehicle ohlcv-1m over the research and confirmation windows.
  - VXN daily closes for every trade date before a research or confirmation date (Cboe, free).
- **Trials in N:** 1.

### K1-vwap-01 (Nasdaq-100: stop-and-reverse around the session VWAP, rewritten to D9's floor)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source sample is 2018-01 to 2023-09, overlapping the confirmation window.]
- **Cluster** K1. **Products read:** the Nasdaq-100 vehicle's bars only.
- **Traded exposure:** Nasdaq-100 {MNQ, NQ}; the source trades QQQ and TQQQ on the same index.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** hold long while price is above the session VWAP and short while it is below, and
  hold nothing overnight.
  - K1-027 (Zarattini and Aziz 2023, full text), P-K1-027-a: "The portfolio maintains a long
    exposure when QQQ is trading above the VWAP and reverses its exposure when the price of QQQ
    moves below the VWAP. No positions are held overnight."
  - P-K1-027-d: "a maximum drawdown of just 9.4% and a Sharpe Ratio of 2.1", on 1-minute QQQ data,
    2018-01-02..2023-09-28.
  - **New to the program.** No MES member uses VWAP. The log tags this as a port of D.1 families B
    and F. D.1 C24 (a Databento note on VWAP-to-mid deviations, not carried) is the only VWAP row
    in D.1's log.
- **Conflicting evidence and quality:**
  - "we assumed no slippage in our order fills" (P-K1-027-b).
  - Trade count: "The active VWAP strategies incurred about 22,000 trades" (P-K1-027-c). Over about
    1,440 trade dates (1,498 weekdays less holidays) that is about 15 a day [arithmetic].
  - The hit ratio is "approximately 17%" (log, Sec. 3.7).
  - At Topstep's $1.22 MNQ round turn, commissions alone come to about 15 x $1.22 = $18.30 per
    contract per day before slippage [arithmetic]. The result is cost-fragile.
  - No out-of-sample test; practitioner authors.
  - D6 criterion 2 records that MES's high-frequency trials (C3 and C6) were its most negative
    members.
- **D9 rewrite.** The source's rule can breach D9.3(a) (no daily cap) and D9.3(b) (1-minute flips),
  so the minimum hold and the entry cap below are added. This is a declared change to the source's
  rule.
- **Definitions (on the vehicle's bars, trade date d):**
  - Typical price TP_b = (high_b + low_b + close_b) / 3.
  - VWAP_t = sum(TP_b x volume_b) / sum(volume_b) over the bars b opening from 08:30 through bar t
    inclusive. It is known at the close of bar t.
  - s_t = +1 if close_t > VWAP_t; -1 if close_t < VWAP_t; otherwise s_{t-1} (0 before the first
    sign of the day). If sum(volume) = 0, no action is taken on that bar.
- **Entry and exit rule**, evaluated on every bar t opening in [08:30, 14:57):
  - If flat, s_t is non-zero and fewer than 20 entries have been made today: a market intent in
    direction s_t.
  - If the position is opposite to s_t and its minimum hold is met: a market intent to exit. If
    fewer than 20 entries have been made today, it is accompanied by a second market intent in
    direction s_t. Both fill at the next open.
  - Otherwise nothing.
  - **Minimum hold (D9.3(b)):** a position filled at the open of bar k may be exited only by an
    intent on bar k+1 or later. It therefore fills at the open of bar k+2 or later, at least 2 full
    minutes after entry.
  - **Entry cap (D9.3(a)):** entries are counted per trade date, including the new leg of each
    reversal, with at most 20. After the 20th, the next opposite signal (once the minimum hold is
    met) exits to flat for the rest of the day.
  - **Final exit:** a market intent on the first bar at or after 14:58, filling at the 14:59 open.
    No entry intent is sent from the 14:57 bar on; the latest entry fills at 14:57 and exits at
    14:59.
- **Holding horizon:** variable, from 2 to 388 minutes. The source's rate implies a mean near 25
  minutes (a 390-minute session over about 15 positions) [inference]. **Session window:**
  08:31-14:59 CT. Flat by F.
- **Data fields read:** vehicle ohlcv-1m high, low, close, volume and instrument_id (C8; paid). If
  E.2 declares the full-size contract's bars as the price path, that contract's volume enters VWAP
  (same underlying). A change of instrument_id within the day: no new entry after it, and the
  position is closed on the next bar.
- **Order type:** market only. A reversal is two market intents, never a stop order. **Sizing:**
  q_c.
- **Parameters (every value):**
  - RTH start 08:30 and flat before the close: P-K1-027-a ("No positions are held overnight";
    QQQ's session is 08:30-15:00 CT).
  - Exit at 14:58 = C-2. Judgment: the program's daily exit convention, as in CP1 and CP3.
  - TP-based VWAP. Judgment: the standard ohlcv-1m approximation; the source's exact computation is
    [unverified].
  - A tie keeps the previous sign (judgment).
  - 20 entries and the 2-minute hold (D9.3).
  - **Grid:** none.
- **Expected entries and hold:** about 15 entries a day (the source's rate), capped at 20. The floor
  holds by construction for (a) and (b); (c) is checked at screening.
- **Falsification:**
  - The standard condition.
  - Member-specific (descriptive): report the confirmation-window mean entries per day and the mean
    gross (pre-cost) P&L per contract per day beside the net figure. If gross is positive and net
    is not, the cost-fragile reading of the source is confirmed.
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: at most 20 entries a day, each held at least 2 minutes, far from "hundreds of rapid
     trades". It is not built to exploit SIM fills: the harness charges slippage on every fill.
  4. Star rules: MNQ is starred. The CPI window is never touched (the earliest fill is 08:31).
     Mini-halt note.
  5. News: <= 1 lot-equivalent; the position never exceeds q_c.
  6. Event-minute guard: fills in [13:00, 13:02) on FOMC days are moved to 13:02, which can delay a
     reversal. D8 charges the event-window cost on fills in [13:00, 13:30).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent. A reversal's two intents net to q_c.
  9. Price limit: C11.
- **Data needed:** Nasdaq-100 vehicle ohlcv-1m, with volume, over the research and confirmation
  windows.
- **Trials in N:** 1.

### K1-predrift-01 (Dow: follow the pre-release move into the ISM Services release)

> [EXCLUDED by the lead, 02:15 PDT 2026-09-24, answering this writer's question 2: this is MES's scheduled-macro-drift family (E-H1/E-H2, class C5, null on MES under docs/NULL_CRITERIA.md) re-run on the Dow, a sibling index highly correlated with the S&P; the K1 brief allows MES families only through the core ports. K2-predrift-01 (the rates version) is unaffected. 0 trials. The entry is kept below for the record only.]
- **Cluster** K1. **Products read:** the Dow vehicle's bars and the ISM release calendar (C9).
- **Traded exposure:** Dow {MYM, YM}. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** Prices drift in the direction of the news before scheduled US releases, and this
  catalog's trade rule follows that drift through the release.
  - K2-007 (Kurov, Sancetta, Strasser, Wolfe 2019, JFQA; full text; panel source claimed by K2),
    P-K2-007-a [K1][K2]: "Prices begin to move in the 'correct' direction about 30 minutes before
    the release time. The pre-announcement price drift accounts on average for about 40% of the
    total price adjustment."
  - It is shown on E-mini S&P 500 futures, with the E-mini Dow among the robustness markets:
    "markets (E-mini Dow stock index and 30-year Treasury bond futures). All tests confirm
    robustness of our [results]." (P-K2-007-f).
  - ISM Non-Manufacturing is one of the drift announcements: "the S&P 500 futures prices increase
    on average by 0.104 percent before a one standard deviation positive surprise in the ISM
    Non-Manufacturing Index" (P-K2-007-c). Table 2 gives "0.104 (0.017)***" (P-K2-007-d).
  - Against costs: "The median effective bid-ask spread is 0.020% for the E-mini S&P 500 futures
    ... far below the two standard deviation band of the CAR around drift announcements"
    (P-K2-007-e).
  - **Reasoning (the trade rule is this catalog's, not the paper's):** if the pre-release move
    carries about 40% of the adjustment in the direction of the news, its sign predicts the sign of
    the remaining adjustment, which arrives at the release. A position taken in the drift's
    direction one minute before the release, and held through it, collects that remainder.
  - **New to the program, not an MES re-run.** This paper is D.1 log row E19 ("Price drift before
    U.S. macroeconomic news: private information?", ECB WP 1901), which was not retrieved or carried
    and was never an MES member. MES E-H1 goes long before FOMC, CPI and NFP releases whatever the
    direction; E-H2 trades post-release momentum after a range expansion (module docstrings).
    Neither signs a position by the pre-release move.
- **Conflicting and weakening evidence:**
  - The paper's primary product is the S&P. The Dow evidence is one robustness sentence
    (P-K2-007-f).
  - The [K1] passages name only ISM Non-Manufacturing among the "Nine of the 20 announcements"
    (P-K2-007-a), so only that release is used.
  - The sample is 2008-2014 (K2 log).
  - The drift per one standard deviation of surprise (0.104%) is smaller than "one standard deviation
    of 5-minute returns ... for the stock ... markets is 0.12" percent (P-K2-007-c). So the sign of a
    single pre-release move is a noisy predictor [inference].
  - K2-015 P-K2-015-a [K1] ("news produces conditional mean jumps") implies no drift after the
    release, which is why the exit comes soon after it.
- **Event days:** trade dates carrying ISM's Services (formerly Non-Manufacturing) PMI release,
  "released on the third business day of the month at 10:00 a.m. (EST)" (both captures). The
  release time is T = 09:00 CT.
  - A date counts only if it appears in the ISM table for its year as captured before that date.
    E.2 builds the tables from the captures (C9) and cross-checks them against ISM's actual
    publication record.
  - Dates the table moves use the table's date, for example "**Services PMI moved due to 4th of July
    holiday observed on July 3, 2026".
- **Entry rule:**
  - D = close of the bar at 08:58 minus close of the bar at 08:29, the move from 08:30 to 08:59
    (T-30 to T-1).
  - D > 0: BUY q_c. D < 0: SELL q_c. D = 0: no trade.
  - Market intent on the 08:58 bar, filling at the 08:59 open, one minute before T.
  - Both bars must exist with one instrument_id.
- **Exit rule:** market intent on the 09:09 bar, filling at the 09:10 open (T + 10).
- **Holding horizon:** 11 minutes. **Session window:** 08:59-09:10 CT. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m close and instrument_id (C8; paid).
  - The ISM calendar: free through Wayback, 2020-08..2026-08. The 2019-05..2020-07 tables are for
    E.2 to source. Each year's table is published ahead of time (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters (every value):**
  - T = 09:00 CT (ISM calendar).
  - The 30-minute signal window (P-K2-007-a, "about 30 minutes before the release time").
  - Entry at T-1. Judgment: the last bar-open fill before the release, which also lets the signal
    cover 29 of the 30 minutes.
  - Exit at T+10. Judgment: the paper's total-impact window ends 5 minutes after the release (K2
    log, products-and-horizon line), but an exit at T+5 would hold 6 minutes and break D9.3(c)'s
    10-minute mean. T+10 is the first whole-minute exit that meets it with a margin. The extra 5
    minutes are undocumented and, per P-K2-015-a, expected to carry no drift.
  - **Grid:** none.
- **Expected entries and hold:**
  - 12 releases a year: about 15 on research-window dates (April 2025-June 2026) and about 57 on
    confirmation dates (June 2019-February 2024; May 2019's third business day falls before the
    earliest S_X), before exclusions [calendar arithmetic].
  - At most 1 entry per event day, held 11 minutes. Floor ok.
- **Falsification:**
  - The standard condition. With about 57 confirmation events, the D4 power check may label it
    "inconclusive by design" (section 7).
  - Member-specific (descriptive): report the hit rate of sign(D) against the sign of the move from
    the 08:59 open to the 09:10 open.
- **Topstep check:**
  1. Flat by F: last fill 09:10.
  2. Order type: market.
  3. D9.4: one trade per event day. The entry fills before the release at the engine's next-open
     fill, not in a gapped market.
  4. Star rules: MYM is starred. The CPI window (07:25-07:35) is never touched. Mini-halt note if D2
     picks YM.
  5. News: the member holds at most 1 lot-equivalent through a scheduled release. F6.1 allows that,
     and F6.3's prohibition covers only "full Maximum Position Size".
  6. Event-minute guard: no fill in [09:00, 09:02); the fills are at 08:59 and 09:10. The D8
     event-window cost applies to the 09:10 exit (C10).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
- **Data needed:**
  - Dow vehicle ohlcv-1m over the research and confirmation windows (the rule reads only 08:29-09:10
    on event dates).
  - The ISM Services release calendar, 2019-2026.
- **Trials in N:** 1.

### K1-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: fallback order declared now (D1 table, 2026 Jan-Aug ADV): Nasdaq-100, then Russell 2000, then Dow; if none is admitted, no ML member. The features are unchanged (they read their named products as signals).]
- **Traded vehicle: Nasdaq-100 exposure** {MNQ, NQ}; D2 chooses the contract in E.2.
  - **Reason:** most of the log's intraday evidence is on the Nasdaq-100:
    - K1-001, 005, 006, 007, 009, 010, 013, 014, 015, 025, 026 and 027 (12 items; K1-012 covers
      all four pairs);
    - the Dow has K1-008, K2-007's robustness sentence and the daily K1-002;
    - the Russell 2000 has only reconstitution descriptions (K1-017, 018, 019, 022, 023) and a
      spread construction (K1-021), none directional.
  - MNQ also has the cluster's highest ADV, 2,363,465 (D1 table).
  - **No fallback is declared.** KF1 and KF2 are Nasdaq-100-specific (VXN). If D2 admits no
    Nasdaq-100 contract, the lead decides.
- **Products the features read:**
  - the Nasdaq-100 vehicle (v; tick 0.25);
  - MES ohlcv-1m bars (the S&P leg; owned; research-window and confirmation-window dates only, never
    holdout);
  - the Russell 2000 exposure's vehicle bars, or its declared price path (r);
  - VXN daily closes (C9).
- **Cluster features.** There are 7; with D15.4's B1-B5 that makes 12. Throughout, t_j is the
  decision time, and "the bar at t_j - 1" is the last bar closed at t_j. Every constant is a
  literal written here.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | vxn_prev | V_prev = Cboe VXN close for the calendar date of trade date d-1. Missing: no trade on d | K1-005 P-K1-005-b (the VXN buckets); K1-025 P-K1-025-a, P-K1-025-b (the implied-volatility level as a leading indicator) | published after d-1's session; used from 08:35 CT on d |
| KF2 | band_pos | (close of v's bar at t_j - 1 - C_prev) / (C_prev x V_prev / 1600). C_prev is the close of v's 14:59 bar on the previous complete trade date, whose instrument_id must equal that of d's 08:30 bar; otherwise no trade on d | K1-005 P-K1-005-a; K1-006 P-K1-006-a, P-K1-006-b | t_j |
| KF3 | nq_es_rel | 10000 x [close_v(t_j - 1) / open_v(08:30) - close_MES(t_j - 1) / open_MES(08:30)], in basis points. If any of the four bars is missing, or either leg changes instrument_id within [08:30, t_j): no trade at t_j | K1-020 P-K1-020-a, P-K1-020-b (the Nasdaq against S&P relative-value construction) | t_j (MES bars closed <= t_j) |
| KF4 | rty_es_rel | 10000 x [close_r(t_j - 1) / open_r(08:30) - close_MES(t_j - 1) / open_MES(08:30)], same missing-bar rule | K1-021 P-K1-021-a (the small against large cap construction) | t_j |
| KF5 | vwap_dev | (close_v(t_j - 1) - VWAP_v) / 0.25, where VWAP_v = sum(TP x volume) / sum(volume) over v's bars opening in [08:30, t_j) and TP = (high + low + close) / 3. If sum(volume) = 0: no trade at t_j | K1-027 P-K1-027-a | t_j |
| KF6 | or5 | (close of v's 08:34 bar - open of v's 08:30 bar) / 0.25 | K1-026 P-K1-026-b (the first 5-minute candle's direction) | 08:35 CT |
| KF7 | vol_open_ratio | volume of v's 08:30 bar / the mean volume of v's 08:30 bar over the 20 most recent earlier complete trade dates (all 20 required; otherwise no trade on d) | K1-014: the classifier's "first-bar volume well above baseline" component (log mechanism line) and P-K1-014-a | 08:31 CT; earlier dates only |

- **Decision window [W0, W1] = [08:35, 14:05] CT; horizon h = 30 minutes.**
  - **Decision times:** t_j = 08:35, 09:05, ..., 14:05, 12 a day. W1 + h = 14:35 <= F.
  - **Fills:** by D15.3's convention a position covers the open of t_j + 1 to the open of t_j + 30.
    Entry fills therefore fall at :06 or :36, and exit fills at :05 or :35.
  - **Why W0 = 08:35:** the first five-minute candle (P-K1-026-b), and so KF6, is complete at 08:35.
    The :05/:35 grid keeps every fill out of the 09:00 CT ISM release minutes and the 13:00 CT FOMC
    minutes (D9.5a), and out of the 07:25-07:35 CPI window.
  - **Why W1 = 14:05:** the last position ends at the 14:35 open. That is before the 14:50-15:00
    closing-auction period, which the log flags as behaving differently in the futures
    (P-K1-011-a, P-K1-011-b; P-K1-024-b) and which no member here models, and before the 15:00
    settlement minute.
  - **Why h = 30:**
    - The log's only tested intraday exit horizon on NQ is K1-005's "30-minute exit rule"
      (P-K1-005-b).
    - K1-003's holds of 5 ms to 5 minutes lose after the spread (P-K1-003-c), which argues against
      15.
    - K1-009's null target runs from the 10:30 ET bar to the close (P-K1-009-a). As a prior
      [judgment], that argues against the long horizons (60, 120).
- **Expected rows:** 12 x the eligible research-window trade dates. That is about 305 trade dates,
  less about 15 roll-blackout dates, early-halt and vendor-degraded dates, and the 20-date warm-up of
  B4 and KF7: roughly 3,000-3,400 rows. E.2 gives the exact count.
- **Expected entries:** at most 12 a day (<= 20), each held 30 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of the mean net daily P&L per contract below eps
  at >= 80% achieved null power on the confirmation window counts against it). Failing the D5
  screen puts it in Tier B. Prior: K1-009, an ML study on MNQ, found "No configuration produces
  out-of-sample accuracy materially above base rate" (P-K1-009-a).
- **Topstep check:**
  1. Flat by F: last exit 14:35.
  2. Order type: market (D15.6).
  3. D9.4: at most 12 entries a day, 30-minute holds, no stops or brackets.
  4. Star rules: MNQ is starred. The CPI window is not touched. Mini-halt note if D2 picks NQ.
  5. News: q_c <= 1 lot-equivalent, not the full maximum. A position may span the 09:00 ISM and
     13:00 FOMC releases.
  6. Event-minute guard: no fill in [09:00, 09:02) or [13:00, 13:02). D8 charges the event-window
     cost on the 13:05 exit and 13:06 entry fills on FOMC days, and on the 09:05 and 09:06 fills
     on ISM days if the lead extends ISM to the Nasdaq-100 (C10).
  7. CPI window: not touched.
  8. Position limit: <= 1 lot-equivalent.
  9. Price limit: C11.
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for
    every ML member.
- **Data needed:**
  - ohlcv-1m of v and r over the research window (training and tuning) and the confirmation window
    (the frozen model).
  - MES bars on those two windows only (owned).
  - VXN daily closes.
  - Member-level coverage checks for v, r and MES over 08:30-14:35.
  - If D2 does not admit the Russell 2000, E.2 must still buy r's history for KF4, or the lead drops
    KF4 before any fit.
- **Trials in N:** 1 at confirmation. In the research-window accounting the grid counts as 48
  (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K1-vixfut-01 | Trade NQ or ES on VIX-futures moves (K1-003) | D9.3 floor; evidence; data | The lead exists only at 5 ms to 5 minutes and loses after the spread: "this strategy generates negative returns irrespective of the holding period" (P-K1-003-c). VX is a CFE contract, not in GLBX.MDP3. The traded product in the paper is ES, which is closed. Non-survivor |
| X-02 K1-microlead-01 | Micro against E-mini lead-lag within one exposure (K1-012, K1-001, K1-015, K1-016) | D9.3 floor; evidence; data | Price leadership is measured "up to one second" (P-K1-001-b), and the micros "contribute approximately equal amounts" (P-K1-012-a), which is evidence against a tradable gap. K1-015 and K1-016 need trader-type codes (P-K1-015-a, P-K1-016-a) and a floor contract that no longer trades |
| X-03 K1-ndxrecon-01 | NQ on the Nasdaq-100 rebalancing date (last 30 minutes) and the next morning (K1-004) | Rule 1 (no index-level sign) | The effect is stock-level: promotions and demotions move in opposite directions, "especially during the last 30 minutes" and reversing "during the early trading hours on the day following" (P-K1-004-b). The net index-level sign is not measured, so no direction can be traced. Abstract only; working paper |
| X-04 K1-rtyrecon-01 | RTY or M2K on the Russell reconstitution day (K1-017, 018, 019, 022, 023) | Rule 1 (no directional claim); frequency | The CME pages describe volume, "one of the highest trading volume days of the year" (P-K1-017-a), and index-tracker trades "on the cash close" (P-K1-022-a), with no claim about RTY's price path. The flow sits at 15:00 CT, C itself. There are one or two events a year. The 2026 schedule is in conflict (November, P-K1-018-b, against December, P-K1-023-a; fetch 6 did not resolve it) |
| X-05 K1-closeauct-01 | Short NQ, RTY or YM over the closing-auction window [14:50, 15:00) (K1-011; K1-024) | Rule 1; D9.3(c); data | The only futures-side evidence is TAIFEX, abstract only, with a garbled direction claim ("will increase their price and lowers their average return", P-K1-011-b) and a hidden auction unlike the published US imbalances (log). The documented window is 5 minutes, which fails the 10-minute mean hold unless stretched to an undocumented 10. NYSE imbalance data is paid and not in the plan, with an unconfirmed history start; Nasdaq's closing-cross data is not covered (P-K1-024-a). The lead may admit a 3-trial version (market intent on the 14:49 bar, exit intent on the 14:59 bar, short, on each exposure); it is not written here |
| X-06 K1-orb5-01 | The first 5-minute candle's direction on the Nasdaq-100, entered at 08:35 (K1-026) | Rule 4 (stops and targets); covered by CP2 | The sourced rule depends on "The stop loss was placed at the low of the day ... We set the profit target at 10x the $R" (P-K1-026-b). Both are prohibited. A stop-free version is an untested construction. Its family (opening range on the Nasdaq-100) is **covered by CP2**. Counter-evidence: no slippage (P-K1-026-b), stop parameters tuned in-sample (log), D.1 B5 on MNQ, R-K1-078 |
| X-07 K1-ictamd-01 | ICT "accumulation-manipulation-distribution" on NQ (K1-007) | Non-survivor | "no directional information beyond the daily trend regime was observed" (P-K1-007-b); "57% of valid signals see full target delivery before the 9:40 AM New York entry window opens" (P-K1-007-a) |
| X-08 K1-ictconf-01 | ICT confluence entries on MNQ (K1-013) | Rule 1 | A one-page high-school abstract with no sample, costs or test ("11% increase in win rate compared to manually trading", P-K1-013-b). The confluences are discretionary and unspecified. Family B, covered by CP2 |
| X-09 K1-dowopen-01 | YM short-side opening reversal (K1-008) | Rule 1 (parameters) | "Exact trading parameters are withheld, limiting independent replication" (P-K1-008-b), so no trigger can be traced. The source's own pre-2023 sample is "below breakeven" at 45.22% (P-K1-008-b), and the confirmation window 2019-05..2024-02 is mostly pre-2023. The expectancy is gross only |
| X-10 K1-stress-01 | Trade MNQ's late-session reversal on "high-stress" classifier days (K1-014) | Non-survivor | "Eight directional strategy configurations were tested on classifier-positive days. None passed" (P-K1-014-b). It rests on 40 event days, and "2024 produced a net loss". The first-bar volume component enters K1-ml-01 as KF7 |
| X-11 K1-mnqml-ext | Another hand-built ML forecast of the MNQ close (K1-009) | Non-survivor; D15 | "No configuration produces out-of-sample accuracy materially above base rate" (P-K1-009-a); the permutation p-value is 0.135 (P-K1-009-d). The cluster's one ML trial is K1-ml-01 (D15), which cites this as its prior |
| X-12 K1-hurst-01 | Hurst-regime filter on NQ 5-minute bars (K1-010) | Rule 1 (unspecified base rule) | The base entry rule is not in the abstract. The validation is Monte Carlo, not out-of-sample (P-K1-010-b). The P&L is quoted per trade in dollars without a contract count (P-K1-010-a) |
| X-13 K1-macd-01 | MACD crossover on YM and NQ (K1-002) | Flat by F; D6 | "a buy (or sell) order ... is executed at the closing price ... on the next day ... a reverse trade is automatically executed" (P-K1-002-b) means holding across days. An intraday-hold variant would be an untested family H construction, and D6 ports H6 only. Also "Transaction fees are not taken into account" (P-K1-002-c) and "no 'P-P' model that consistently generated significant returns" (P-K1-002-d). The Nikkei leg is out (D1) |
| X-14 K1-vxnlong-01 | Long NQ intraday when VXN is "extremely high" (K1-025) | Rule 1 (threshold, horizon) | P-K1-025-b gives no threshold and an unverified horizon ("at least on a short term basis"; the log thinks it is multi-day). The sample predates 2003. An intraday hold would test an undocumented horizon. Used only as support: K1-vxnband-01 and K1-ml-01 KF1 |
| X-15 K1-vixrange-01 | Trade the VIX/√252 expected-move band on the Nasdaq-100 (K1-006) | Rule 1 (no P&L, no direction) | It is a range calibration: "touched intraday in 37.5% of sessions" (P-K1-006-a). The 54.8% lower-first touch (P-K1-006-b) has no cost or P&L test. Used as support for K1-vxnband-01 and KF2 |
| X-16 K1-spread-01 | NQ-ES or RTY-ES intraday relative value (K1-020, K1-021) | Rule 1; D1.5 | These are definitions, not evidence: "The point of entering into an inter-market spread is to trade on the differences" (P-K1-020-b); "two E-mini Russell 2000 futures for every one E-mini S&P 500" (P-K1-021-b, illustrative). The ES leg cannot be traded (D1.5). An NQ-RTY spread has no logged source. Used as KF3 and KF4 |
| X-17 K1-chpmi-01 | NQ or YM on the Chinese PMI release (K3-007 [K1], P-K3-007-h, P-K3-007-i: "E-mini Nasdaq-100 35 0.10 (0.03)*** 0.463; E-mini Dow 35 0.09 (0.02)*** 0.467") | Rule 3 (consensus); contemporaneous | The effect is a surprise response against a consensus that is proprietary. It is measured in a [-10, +10] minute window ("from 10 minutes before to 10 minutes after", P-K3-007-c [K3]) and "appears to be permanent" (K3 log, first-run passage, not re-checked), so nothing is left to trade afterwards. N = 35 |
| X-18 K1-macrojump-01 | Post-release trade on US macro surprises (K2-015 [K1], P-K2-015-a) | Rule 3; contemporaneous; product | "news produces conditional mean jumps" at the release, with state-dependent signs (K2 log). The K1 products in the paper are the S&P 500 and Euro Stoxx 50 futures (not traded). It needs consensus surveys |
| X-19 K1-polunc-01 | Condition a K1 release member on monetary-policy uncertainty (K3-035 [K1], P-K3-035-a: "the response to macroeconomic news weakens in the stock and crude oil markets") | Rule 1; partition rule 4 | It is a conditioning variable for surprise responses, and K1 has no surprise member (X-17, X-18). The uncertainty measure is rates-derived and unspecified [unverified], so it is routed to K8 (section 4) |
| X-20 K1-volheat-01 | Volatility-transmission state on ES (K3-030 [K1], P-K3-030-a) | Rule 1; product | Volatility only, with no return claim, on ES (closed). B4 in the ML member already carries volatility state |
| X-21 K1-oireversal-01 | Overnight-intraday reversal on K1 products (K3-040, registry-tagged K1) | Rule 1 | Title only; content [unverified]. It is opposite in sign to CP1's (a) form |

---

## 3. Beyond budget (lead decides)

None. The log supports 3 new members inside a budget of 11. These candidates were considered and
not written (none is a budget overflow):
- **K1-vxnband-01 on the Russell 2000 and the Dow**, using those indices' own Cboe volatility
  indices.
  - Why not: the evidence is on NQ with VXN only (K1-005). The Russell and Dow volatility indices'
    names, availability and history were not checked in E.0.
  - Cost: +2 trials.
- **An unfiltered VXN-band fade** (every VXN level).
  - Why not: the source reports "slightly negative values" in the middle buckets and a -0.94
    pre-sample Sharpe without the filter (P-K1-005-b).
  - Cost: +1 trial.
- **K1-vwap-01 on the Russell 2000 and the Dow.**
  - Why not: the evidence is QQQ and TQQQ only.
  - Cost: +2 trials.
- **K1-predrift-01 variants.**
  - Candidates: on NQ or RTY (untested there); with the MES pre-release move as the signal (the
    paper's primary product, a K1 leg); or on the other eight drift announcements (not named in the
    [K1] passages).
  - Cost: +1 to +3 trials.
- **The stop-free first-candle rule (X-06)** and **the closing-auction short (X-05)**: +1 and +3
  trials.

---

## 4. Routed to K8

| Source | Legs | One phrase | K8 disposition (K8 log) |
|---|---|---|---|
| Kurov, Olson, Wolfe (2024), J. Commodity Markets, "Have the causal effects between equities, oil prices, and monetary policy changed over time?" (K1 log section 4) | equity index (K1), crude (K4), rates (K2) | time-varying equity-oil causality | F01, rejected (R-K8-001: contemporaneous) |
| Zangelidis and Rezitis (2026), Resources Policy, HAR-VAR volatility topology (K1 log section 4) | NASDAQ (K1), copper (K5), dollar (K3), commodity indices | volatility spillover topology | F02, rejected (R-K8-002) |
| Kurov, Stan (2018), K3-035 [K1] | monetary-policy uncertainty (rates-derived) conditioning the equity response to US news | conditioning variable from rates | routed by this catalog (X-19); not yet in K8's log |
| Alquist, Ellwanger, Jin (2020), K4-008 = K8-001 | WPSR oil shock (K4) and the S&P via SPY (K1 leg), Treasuries (K2), FX (K3) | oil inventory news as a cross-asset instrument | read by K8 |
| Baur, Kuck (2020), K8-003 | S&P 500 5-minute return (K1 signal) and gold (K5 traded) | flight-to-safety lead into gold | read by K8 |
| Mourey et al. (2025), K8-004 | weekend crypto (K7) and Monday equity indices (K1) | weekend crypto as an equity-open signal | read by K8 |
| Phan, Sharma, Narayan (2016), K8-007 | crude (K4) and the US equity market (K1) | intraday volatility interaction | read by K8 |
| K8-006 (CAD and crude, S&P as a conditioning leg); K8-008 (US cash-equity open and ZN) | K1 as a conditioning or clock leg | cross-cluster | read by K8 |

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K1.md section 3, every `[K1]`-tagged
passage in the other logs, the registry lines tagged K1, the log's rejection rows as a group, and the
D.1 rows the K1 log cites.

| Item | Disposition |
|---|---|
| K1-001 Hasbrouck (2003) | Excluded, X-02 (one-second price discovery; the lagging instruments are an ETF and a defunct floor contract). Background only |
| K1-002 Kang (2023), MACD | Not intraday-feasible (holds across days, P-K1-002-b); excluded, X-13 |
| K1-003 Bangsgaard, Kokholm (2024) | Excluded, X-01 (non-survivor after costs; 5 ms to 5 minutes). Used as a reason against h = 15 in K1-ml-01 |
| K1-004 Franz (2019) | Excluded, X-03 (stock-level; no index-level sign; abstract only) |
| K1-005 Seeck (2026) | **Used: K1-vxnband-01** (P-a, P-b); K1-ml-01 KF1 and KF2, and the choice of h |
| K1-006 Backhaus (2026) | Supporting evidence for K1-vxnband-01's band scale and K1-ml-01 KF2 (P-a, P-b). As a member, excluded, X-15 |
| K1-007 Taylor (2026), ICT AMD | Excluded, X-07 (non-survivor) |
| K1-008 Ladia (2026) | Excluded, X-09 (parameters withheld; the pre-2023 null covers most of the confirmation window) |
| K1-009 Mesfin (2026), LSTM and GB on MNQ | Non-survivor, X-11. Cited as K1-ml-01's prior and in its h choice |
| K1-010 Ntingana (2026) | Insufficient evidence: the base rule is unspecified; X-12 |
| K1-011 Chen, Tai, Yang (2013) | Excluded, X-05 (insufficient evidence; D9.3(c)). Cited for K1-ml-01's W1 |
| K1-012 Fassas (2021) | Excluded, X-02 (evidence against a micro-mini gap; sub-second) |
| K1-013 Parekh, Heller (2026) | Excluded, X-08 (no evidential weight). Family B, **covered by CP2** |
| K1-014 Mesfin (2026b) | Non-survivor, X-10. Its first-bar volume component is used as K1-ml-01 KF7 |
| K1-015 Kurov, Lasser (2004) | Insufficient evidence: background only, needs trader-type codes; X-02 |
| K1-016 Kurov (2008) | Insufficient evidence: background only, needs trader-type codes; X-02 |
| K1-017 CME (2023), Russell reconstitution | Excluded, X-04 (no directional claim) |
| K1-018 CME (2025), Russell reconstitution | Excluded, X-04. The source of the "November" side of the 2026 conflict |
| K1-019 CME (2021), reconstitution results | No mechanism (the log says "empty on reading"). Not used |
| K1-020 CME course, intermarket spreads | Construction only; excluded as a member, X-16. **Used: K1-ml-01 KF3** |
| K1-021 CME course, RTY spreads | Construction only; excluded as a member, X-16. **Used: K1-ml-01 KF4** |
| K1-022 CME, managing a reconstitution | Excluded, X-04 |
| K1-023 CME (2026), 2026 Russell reconstitution | Excluded, X-04. The source of the "December" side of the 2026 conflict |
| K1-024 Databento (2025), NYSE imbalance feeds | Data availability only; excluded, X-05 (paid, not in the plan). Cited for K1-ml-01's W1 |
| K1-025 Giot (2003/2005) | Excluded as a member, X-14. Supports K1-vxnband-01 (the high-VXN side) and K1-ml-01 KF1 |
| K1-026 Zarattini, Aziz (2023), ORB | **Covered by CP2** (family B on the Nasdaq-100); its stop and target structure is excluded, X-06. **Used: K1-ml-01 KF6** and W0 |
| K1-027 Zarattini, Aziz (2023), VWAP | **Used: K1-vwap-01** (P-a to P-d); K1-ml-01 KF5 |
| K2-007 [K1] Kurov, Sancetta, Strasser, Wolfe (P-a, P-c, P-d, P-e, P-f) | **Used: K1-predrift-01** (P-a mechanism; P-c, P-d for the ISM release; P-e cost context; P-f for the E-mini Dow). The same paper is D.1 log E19 (not retrieved there) |
| K2-015 [K1] Andersen, Bollerslev, Diebold, Vega (P-a) | Excluded as a member, X-18 (contemporaneous jumps; S&P and Euro Stoxx). Used in K1-predrift-01's exit reasoning |
| K3-007 [K1] Baum, Kurov, Wolfe (P-h, P-i) | Excluded, X-17 (proprietary consensus; contemporaneous; N = 35) |
| K3-030 [K1] Martínez, Tse (P-a) | Insufficient evidence for K1: volatility only, ES (closed); X-20 |
| K3-035 [K1] Kurov, Stan (P-a) | Excluded, X-19; routed to K8 (section 4) |
| K3-040 (registry-tagged K1) Kosowski et al. | Insufficient evidence: title only; X-21. Noted as counter-evidence in CP1 |
| K4-008 = K8-001 (registry-tagged K1) Alquist, Ellwanger, Jin | Routed to K8 and read by K8. The K1 leg there is SPY (S&P), not a traded K1 product |
| K4-043 Fett, McPhail (ES leg; no `[K1]` passage) | Not used: ES stop-order facts are D.1 B2's (generic S&P) |
| K4-050 / R-K1-078 Fetna (2026) | Insufficient evidence (no [K1] passage logged). Noted as counter-evidence for CP2 |
| K8-003, K8-004, K8-006, K8-007, K8-008 (K1 legs) | K8's (section 4) |
| R-K1-067, R-K1-068, R-K1-069 | Rejected in the log; the mechanism is **covered by CP1** (D.1 A10 and A28 family) |
| R-K1-078, R-K1-079 | Rejected or pointed elsewhere in the log; family B, **covered by CP2** |
| R-K1-028, 088, 090, 092 | Sentiment or attention, shelved (brief rule 13). No member conditions on sentiment. VXN and VIX are option-implied volatility indices, not sentiment measures |
| R-K1-001 to R-K1-095 (all others) | Rejected at pre-filter or on reading; not used |
| D.1 rows cited by the K1 log: A10 (and A28) | Covered by CP1 |
| D.1 B4, B5 (with A14 and C5), B8 | Covered by CP2; B5 is quoted there as an MNQ prior |
| D.1 E10, E13, E14 (S&P rebalance and passive-flow pressure) | Generic S&P (D.1 territory); no K1 member. K1's own reconstitution items are X-03 and X-04 |
| D.1 C16 (end-of-day reversal, cross-sectional stocks) | Not a K1 product; not used |
| D.1 E19 (price drift before US news) | The same paper as K2-007; used through K2-007's [K1] passages in K1-predrift-01 |
| Registry note | The K1-001 claim line carries a wrong DOI, as the log says (correct: 10.1046/j.1540-6261.2003.00609.x). The registry is append-only, so it is not edited here |

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all three admitted) |
|---|---|---|---|
| K1-cp1-01 | Nasdaq-100, Russell 2000, Dow | 1 | 3 |
| K1-cp2-01 | Nasdaq-100, Russell 2000, Dow | 1 | 3 |
| K1-cp3-01 | Nasdaq-100, Russell 2000, Dow | 1 | 3 |
| K1-vxnband-01 | Nasdaq-100 | 1 | 1 |
| K1-vwap-01 | Nasdaq-100 | 1 | 1 |
| K1-predrift-01 | EXCLUDED by the lead (02:15) | - | 0 |
| ~~K1-ml-01~~ [excluded, U6] | Nasdaq-100 (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | **13** = 9 port + 3 new + 1 ML. In general 3E + 3a_N + a_D. Without the Dow: 9. Nasdaq-100 only: 6 |

The cumulative program N before Stage E is 58 (design, standing inputs). K1's confirmation trials
add up to 13.

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **Thin K1-specific evidence.**
   - Only 3 new members are written, and 8 budget slots are unused.
   - The log found no minute-horizon lead-lag or spread-reversion evidence inside the complex
     (containers 1 and 3). It found no directional evidence for any reconstitution day, and NKD is
     out.
   - The lead decides whether a K1 screening session is worth running with mostly port trials. The
     9 port trials sit close to the MES record (C3, C2 and C7 were null on MES).
2. **K1-predrift-01 and the "generic S&P" rule.**
   - Its mechanism is documented mainly on ES, with one robustness sentence on the E-mini Dow
     (P-K2-007-f).
   - If the lead reads it as a generic S&P mechanism, it should be cut (1 trial).
   - It is also low-frequency (about 57 confirmation events), so D4 may label it inconclusive by
     design.
3. **K1-vwap-01's rewrite and its cost fragility.**
   - The D9 floor forced a 2-minute minimum hold and a 20-entry cap onto the source's rule.
   - The source assumed no slippage, with about 15 flips a day. The lead may cut it (1 trial).
4. **K1-vxnband-01's regime filter.**
   - The cuts 20 and 30 are the source author's in-sample bucket edges, and are written as one
     trial.
   - The unfiltered variant, or variants on the Russell 2000 and the Dow, would each add trials
     (section 3).
5. **Mini halts under volatility** (F12.1: "Trading on mini-sized contracts or larger may be
   temporarily halted for affected products").
   - If D2 picks NQ, RTY or YM, a member could be untradeable exactly on high-volatility days
     (for example K1-vxnband-01's VXN >= 30 regime).
   - The lead decides whether D2 should prefer the micros for deployability, or whether the risk is
     only noted.
6. **Scope of the ISM release (D8 and D9.5a).**
   - K1-predrift-01 names ISM Services at 09:00 CT for the Dow.
   - The lead decides whether it also "concerns" NQ and RTY, for the event-window cost and the fill
     guard (C10). That would change costs for CP2, CP3, K1-vxnband-01, K1-vwap-01 and K1-ml-01.
7. **K1-ml-01's Russell leg.**
   - KF4 needs Russell 2000 bars on the research and confirmation windows even if D2 does not admit
     that exposure.
   - The lead decides whether to buy them, or to drop KF4 before any fit.
8. **Optional additions not written:**
   - the closing-auction short, X-05 (3 trials);
   - the stop-free first-candle rule, X-06 (1 trial).
9. **The Russell reconstitution calendar conflict for 2026.** November (K1-018) against December
   (K1-023) remains unresolved after fetch 6. No member depends on it.
10. **E.2 checks named in this catalog:**
    - (a) the VXN file's coverage from 2019-04-30 and Cboe's publication time (C9);
    - (b) ISM Services tables for 2019-05..2020-07, the "(EST)" reading, and continuity with the
      Non-Manufacturing name (C9);
    - (c) tick-size history 2019-2026 (C7);
    - (d) K1 price-limit tables from the rulebook chapters (C11);
    - (e) short micro histories and the full-size price-path declaration (C8);
    - (f) member-level coverage for the overnight reopen bar CP1 reads (17:00 CT) and for K1-ml-01's
      three legs.
11. **Registry hygiene** (already noted by the reader): the K1-001 DOI is wrong in the registry.
