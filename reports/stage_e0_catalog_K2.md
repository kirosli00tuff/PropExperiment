# Stage E.0 hypothesis catalog, cluster K2 (rates: ZT, ZF, ZN, TN, ZB, UB)

Writer: CatalogWriter-K2-OpusXHigh (Stage E.0 Task 4), 2026-09-23, 21:03-21:40 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.
Written before any price, bar, tick or order-book data for any K2 product existed on this machine.
The only product-specific numbers used are contract specifications and public ADV
(reports/stage_e0_liquidity.json), Topstep's published fees and hours
(reports/stage_e0_topstep_facts.md), and event-calendar metadata: auction dates, closing times and
FOMC meeting dates. Calendar metadata carries no prices.

Inputs read in full: reports/stage_e0_research_K2.md; `[K2]` passages in the other logs (none
exist beyond K2's own log; see section 5); reports/stage_e0_source_registry.jsonl (K2 lines and
K4-008); docs/STAGE_E_DESIGN.md (D1-D15); reports/stage_e0_partition.md;
reports/stage_e0_topstep_facts.md; reports/stage_e0_liquidity.json (rates rows);
reports/stage_d1f_confirmation_list.md 2.1 A3; strategy/research/b_reference_breakout/
h1_friction_aware_opening_range_breakout.py; strategy/research/h_daily_bar/h6_prior_close_location.py;
reports/stage_d1b_family_f_declaration.md F3.3.

---

## 0. Header

| Item | Value |
|---|---|
| Products | ZT, ZF, ZN, TN, ZB, UB (CBOT Treasury futures; Topstep F1 "CME CBOT Financial/Interest Rate Futures", none starred) |
| Exposures | six, one per tenor, each with exactly one admissible contract (partition section 1): ZT, ZF, ZN, TN, ZB, UB |
| Members | 9 = 5 new + 3 core ports + 1 ML member (budget 15; 6 slots unused, see section 3) |
| Trials in N (confirmation) | 45 if D2 admits all six exposures (18 port + 26 new + 1 ML). In general 3E + 4E + E_pd + 1, where E = number of admitted exposures and E_pd = admitted exposures among {ZN, ZB}. Example: without ZB and UB, 30. |
| ML grid (research-window accounting only, D15.8) | 48 configurations, counted in the K2 screening session's research-window DSR for K2-ml-01 |
| Starred products | none (Topstep F1: no K2 product carries "*") |
| D1 | **D1 is applied by the lead.** No K2 exposure is assumed IN. Every member below is written for all six. |
| D2 | Vehicle "D2 (chosen in E.2)" throughout. Rule 13: ZB and UB may be outside D2's risk band at one contract; every entry marks them "traded only if D2 admits the exposure". The same condition applies to every K2 exposure (see C6). |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the one-minute ohlcv-1m bar
  whose ts_event (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its
  values are usable from then on.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine convention
  D6 and D15.3 use): "market intent on the bar at X" fills at the open of the bar at X + 1 min.
- **C3 Trade date.** Trade date d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md). "Calendar
  month of d" is the month of the date d.
- **C4 Exclusions for the five new members.** The ports follow D6 as written. The new members do not
  trade on: roll-blackout dates (the program convention, `screen_candidate` with `roll_blackout`);
  dates the D10 rates calendar marks as early halt or early close (as Family H: "Days with
  early_halt_ct set: no trade"); or dates on which any bar the rule reads, or the entry bar, is
  missing or carries a different instrument_id from the entry bar (the instrument guard D6 CP1
  uses). If an exit's named bar is missing, the exit is sent on the first later bar. The engine's
  forced flatten at F is the backstop.
- **C5 Flat time.** F = 15:08 CT (D9.1; D6 rates row). No new member's last fill is later than
  15:05 CT.
- **C6 Size.** q_c of the exposure's D2 vehicle. Every K2 contract is a mini (1 lot-equivalent,
  D9.6), so D9.5's cap of 1 lot-equivalent makes q_c = 1 contract for every K2 member. At q = 1,
  D2's risk ratio is rho = r_c / R*. E.2 measures whether each exposure's r_c lies in
  [0.5 R*, 2.0 R*]. Nothing here assumes it does, for any exposure.
- **C7 Ticks and fees.** Tick size and value from reports/stage_e0_liquidity.json (CME contract
  specs, fetched 2026-09-23 20:43-20:44 PDT): ZT 0.00390625 pt = $7.8125; ZF 0.0078125 pt =
  $7.8125; ZN 0.015625 pt = $15.625; TN 0.015625 pt = $15.625; ZB 0.03125 pt = $31.25; UB
  0.03125 pt = $31.25. Topstep round turns (F3): ZT $2.32, ZF $2.32, ZN $2.62, TN $2.62, ZB $2.76,
  UB $2.92. These are 2026 specifications. E.2 must confirm that each tick size was unchanged over
  2019-05..2026-06 before any bar is read, and log any change, because CP2's buffer is in ticks.
- **C8 Price data source.** Databento GLBX.MDP3 ohlcv-1m of the vehicle (and, for K2-ml-01, of
  ZF, ZB and ZT). It is paid, bought in E.1 (D13), and available from the start-rule bound
  2019-05-06 (D4) to 2026-06-19. A bar is available at its close (C1). mbp-1 enters only through
  D8's shared five-date cost-calibration sample. No member reads order-book data.
- **C9 Event calendars (external, free, history covering 2019-05..2026-06).** Each rule reads only
  dates and scheduled clock times, never a released value (no index level, no auction result).
  - **EC-AUC, Treasury auctions.** Source: FiscalData "auctions_query" API
    (https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query).
    Queried 2026-09-23 21:05-21:13 PDT (metadata fields only, no price or result fields read).
    - **Fields read:** security_type, original_security_term, floating_rate,
      inflation_index_security, auction_date, announcemt_date, closing_time_comp ("Closing Time
      (ET) - Competitive").
    - **Availability:** these are auction-announcement fields, published on announcemt_date. A
      record counts only if announcemt_date is strictly before auction_date. Five same-day records
      exist in the 2019-05..2026-06 table and are excluded by this guard. Among the 2-, 5-, 10- and
      30-year fixed-rate nominal records, only one is affected: a 10-year reopening on 2019-06-21
      with an 11:00 ET close, announced the same day. Every retained tenor-matched record was
      announced at least 4 calendar days before its auction, so all retained fields are known
      before the trade date begins.
    - **Results fields are never read.** The same record also carries bid_to_cover_ratio,
      high_yield and other results fields.
    - **Clock:** T_a (CT) = closing_time_comp (ET) - 1 hour. Eastern and Central time change on
      the same dates.
    - **Checks for E.2:** if the announcement XML (xml_filenm_announcemt) and the query disagree
      on closing_time_comp for any auction, that auction is dropped and logged.
  - **EC-FOMC, scheduled FOMC meetings.**
    - **Source:** https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (lists 2021-2027,
      fetched 2026-09-23 21:14 PDT), plus the page's "Transcripts and other historical materials"
      for 2019-2020.
    - **Statement time 13:00 CT:** Topstep F6 table "FOMC Statement | 1:00 PM" (CT) and
      P-K2-018-c "13:00 CST".
    - **Event set:** the last day of each regularly scheduled meeting. Unscheduled meetings,
      notation votes (for example "August 22 (notation vote)" in 2025) and conference calls are
      excluded.
    - **Availability:** the schedule is published before the year begins.
  - **EC-ISM, ISM Services (Non-Manufacturing in K2-007's sample) Report On Business release
    dates.**
    - **Source:** the PR Newswire ISM newsroom
      (https://www.prnewswire.com/news/institute-for-supply-management/, WebFetch 2026-09-23
      21:10 PDT), which shows each Services PMI release stamped "10:00 ET" (for example
      "September 3, 2026, 10:00 ET"). 10:00 ET = 09:00 CT.
    - **Caveats:** WebFetch returns a paraphrase with the timestamps quoted. ISM's own calendar
      (ismworld.org rob-report-calendar) redirected to a login page and was not read. E.2 pages
      the newsroom archive back to 2019 and drops any release not stamped 10:00 ET.
  - **EC-NFP, BLS Employment Situation release dates.**
    - **Source:** https://www.bls.gov/bls/news-release/empsit.htm lists every release from January
      1994 to August 2026, with the release date in each file name (for example
      empsit_08022019). Release time "08:30 AM" (ET) is from
      https://www.bls.gov/schedule/news_release/empsit.htm, and Topstep F6 gives "Unemployment
      Rate | 7:30 AM" CT. Both fetched 2026-09-23 21:15 PDT.
  - **EC-CAL.** The D10 rates calendar (trade dates, holidays, early closes), built by E.2 from
    CME schedules.
  - **EC-NYSE.** NYSE holiday schedule, used only by K2-ml-01. It is free and published in advance.
    Not fetched in E.0, so its availability is unconfirmed here.
- **C10 Frequency (arithmetic from the calendar counts above, no price data).**
  - A member that trades on k of the ~290 eligible research-window trade dates, with zeros on
    other days (D5), needs a net P&L per event of about (290 / k) x eps_X to reach a mean of
    eps_X per trade date.
  - That multiple is about 19 to 22 for the auction members (k = 15 to 13), about 29 for the FOMC
    member (k = 10), about 19 for the ISM member (k about 15) and about 10 for the month-end
    member (k = 28).
  - These members can therefore be expected to end "null at eps" unless each event carries a
    large move. That is a legitimate funnel statement, but it is structural. See section 7,
    item 2.

---

## 1. Members

### K2-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K2. **Products read:** the traded exposure's own vehicle only. **Traded exposures
  and admissible contracts:** ZT {ZT}, ZF {ZF}, ZN {ZN}, TN {TN}, ZB {ZB}, UB {UB}, each a separate
  trial. ZB and UB are traded only if D2 admits the exposure (so is every exposure, C6).
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1
  log A10 and A28; reports/stage_d1b_family_f_declaration.md F3.3), as fixed in D6 row CP1. It
  rests on no K2 passage; the K2 log holds no intraday-momentum source (section 5). D6 rule text,
  verbatim: "Signal: sign of (close of the bar at O+29 min minus open of the trade date's first
  bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the signal's
  direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min
  (fills at the next open). Both signal bars must exist with one instrument_id, else no trade."
- **Instantiated with the D6 rates row (O = 07:20, C = 14:00, F = 15:08):**
  - **Signal:** close of the bar at 07:49 minus the open of the trade date's first bar (the
    Globex open, 17:00 CT on d-1).
  - **Entry:** market intent on the bar at 13:29, filling at the 13:30 open.
  - **Exit:** market intent on the first bar at or after 13:58, filling nominally at the 13:59
    open.
  - **Holding horizon:** 29 minutes. **Session window:** 13:30-13:59. Flat well before F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid (E.1), with
  history 2019-05..2026-06. The latest signal input, the 07:49 bar, is available at 07:50 CT, and
  the decision is at 13:30.
- **Order type:** market. **Sizing:** q_c of the D2 vehicle (= 1 contract, C6).
- **Parameters:** O+29 = 07:49, C-31 = 13:29, C-2 = 13:58 (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29
  minutes. Floor: 20 entries per day ok, 2-minute minimum ok, 10-minute mean ok.
- **Falsification:** the standard condition. UCB95 of the member's mean net daily P&L per
  contract below eps_X, at >= 80% achieved null power on the confirmation window, counts against
  it. No member-specific check, because it is a port and D6 is unchanged.
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market orders only.
  3. D9.4 prohibited patterns: one trade a day, no stops, brackets or passive fills.
  4. * restriction: none applies.
  5. News: 1 lot-equivalent, which is half the 2-lot maximum. On FOMC days the position starts
     30 minutes after the 13:00 statement.
  6. Position limit: 1 contract.
  7. Price-limit proximity: no E.0 artifact establishes a CME daily limit for CBOT Treasury
     futures. If E.2's D9.7 tables find one, the harness rule applies. The catalog assumes
     nothing.
- **Data needed:** ohlcv-1m of each admitted K2 vehicle, research window 2025-04-01..2026-06-19
  and confirmation S_X..2024-02-29 (D4). No external data.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-cp2-01 (core port CP2, opening-range breakout)
- **Cluster** K2. **Products read:** own vehicle. **Exposures:** ZT, ZF, ZN, TN, ZB, UB, one
  contract each. ZB and UB (and every exposure) are traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py,
  hold_minutes = 75), as fixed in D6 row CP2. It rests on no K2 passage. D6 rule text, verbatim:
  "OR = high and low of the bars in [O, O+15 min). Entry: the first bar opening in [O+15, C) whose
  close is beyond OR_high or OR_low by at least 4 ticks of P; market intent in the break direction;
  one entry per trade date; no entry from C on. Exit: 75 minutes after the fill, or the engine's
  forced flatten at F if earlier."
  [Amended by the lead, 21:12 PDT, to D6's amended CP2 text (entry window bounded at C), answering
  this writer's note below.]
- **Instantiated:**
  - **Opening range:** the bars with open time in [07:20, 07:35).
  - **Eligible bars:** those opening in [07:35, 14:00). No entry from 14:00 CT on.
  - **Entry buffer, 4 ticks of P:** ZT 0.015625 pt, ZF 0.03125 pt, ZN 0.0625 pt, TN 0.0625 pt,
    ZB 0.125 pt, UB 0.125 pt (C7).
  - **Entry:** a close >= OR_high + buffer buys; a close <= OR_low - buffer sells.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it, or the forced
    flatten at F.
  - **Holding horizon:** 75 minutes, or less if F intervenes. **Session window:** 07:35 to F.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is
  known at 07:35 CT.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:** OR 15 minutes, buffer 4 ticks, hold 75 minutes (D6, a literal port). **Grid:**
  none.
- **Expected entries and hold:** at most 1 per day, held 75 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: engine flatten.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. *: none.
  5. News: 1 lot-equivalent, which may be held through a 09:00 CT release.
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2, as in CP1.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 6).
- **Note for the lead (not a change; the text is copied unchanged):** D6's text has no
  latest-entry time. On MES the gap between C (15:00) and F (15:08) was 8 minutes. On K2 it is 68
  minutes (14:00 to 15:08), so a first break after 14:00 CT can be entered here with a hold that F
  truncates. See section 7, item 1.

### K2-cp3-01 (core port CP3, prior-close location)
- **Cluster** K2. **Products read:** own vehicle. **Exposures:** ZT, ZF, ZN, TN, ZB, UB. ZB and UB
  (and every exposure) are traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3. It rests on
  no K2 passage. D6 rule text, verbatim: "Daily bar of day d from [O, C): O_d = open of the O bar,
  H and L over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules
  as Family H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells,
  market intent on the O bar of day d. Exit: first bar at or after C-2 min."
- **Instantiated:**
  - **Daily bar:** O_d = open of the 07:20 bar. H and L are taken over the bars opening in
    [07:20, 14:00). C_d = close of the 13:59 bar.
  - **Complete day** (Family H): the 07:20 and 13:59 bars exist, the date is not an early halt,
    and all bars in [07:20, 14:00) carry one instrument_id.
  - **Instrument guard:** d-1's daily bar carries the instrument_id of day d's 07:20 bar.
  - **CLV:** computed in ticks, with Range[d-1] > 0. CLV >= 0.8 buys and CLV <= 0.2 sells
    (non-strict, as H6).
  - **Entry:** market intent on the 07:20 bar of d, filling at the 07:21 open.
  - **Exit:** first bar at or after 13:58, filling nominally at the 13:59 open.
  - **Holding horizon:** about 398 minutes. **Session window:** 07:21-13:59.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's
  bar is complete at 14:00 CT on d-1, before d begins.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 398 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market.
  3. D9.4: ok.
  4. *: none.
  5. News: holds through the morning releases, the 12:00 CT auction closes and the 13:00 FOMC
     statement at 1 lot-equivalent, which is not the full maximum (D9.5).
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-aucpre-01 (pre-auction concession)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source (NY Fed SR 1188) covers 1991-2024, overlapping the confirmation window.]
- **Cluster** K2. **Products read:** the traded vehicle; EC-AUC; EC-CAL.
- **Traded exposures (tenor-matched):** ZT on 2-year auctions; ZF on 5-year; ZN on 10-year; TN
  on 10-year; ZB on 30-year; UB on 30-year. Each exposure has one admissible contract. ZB and UB
  (and every exposure) are traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:**
  - **What is claimed:** dealers sell ahead of a Treasury auction and cover afterwards. The
    intraday trace is a V-shaped yield path centred on the auction close. Yields rise over the
    180 minutes before the close (prices fall) and reverse after the results.
  - **Verified passages:** K2-002 P-K2-002-b ("V-shaped pattern ... 0.7 to 1.2 basis points"),
    P-K2-002-c (the 180-minute pre-window definition) and P-K2-002-d. The multi-day version is
    K2-001 P-K2-001-a. Daily-frequency support that "the occurrence of an auction ... pushes
    futures prices lower" is K2-006 P-K2-006-a (abstract only).
  - **Classification:** new to the program (log tag for K2-002).
- **Event set:**
  - **Records:** EC-AUC records with security_type Note or Bond, floating_rate "No",
    inflation_index_security "No", and announcemt_date < auction_date.
  - **Tenor match:** original_security_term = "2-Year" for ZT, "5-Year" for ZF, "10-Year" for ZN
    and TN, "30-Year" for ZB and UB. Reopenings are included, because original_security_term
    carries the tenor.
  - **Mapping rule:** the permitted contract's nominal tenor, by its Topstep/CME name, equals the
    auctioned security's original term. This is a judgment. The log holds no deliverable-basket
    passage; K2-004 logged only the CTD definition, P-K2-004-a. 3-, 7- and 20-year auctions are
    therefore not traded (excluded X-06).
  - **T_a:** closing_time_comp - 1 h, in CT.
- **Entry rule:** SELL, market intent on the bar at T_a - 181 min, filling at the open of the bar
  at T_a - 180 min.
- **Exit rule:** market intent on the first bar at or after T_a - 2 min, filling at the next
  open (nominally T_a - 1 min), so the position is flat before the competitive close.
- **Holding horizon:** 179 minutes.
- **Session window by close time:**
  - 13:00 ET closes (T_a = 12:00 CT): 09:00-11:59 CT.
  - 11:30 ET closes (T_a = 10:30 CT): 07:30-10:29 CT.
  - The single 10:00 ET close (5-year, 2019-12-24): T_a = 09:00 CT, window 06:00-08:59 CT, and
    no trade if EC-CAL marks the date an early close (C4).
  - Flat by F in every case.
- **Data fields read:**
  - Vehicle ohlcv-1m open, close and instrument_id (C8), each available at its bar's close.
  - EC-AUC auction_date, closing_time_comp, original_security_term, floating_rate,
    inflation_index_security, announcemt_date. Free; 2019-2026 history confirmed by query.
    Available from announcemt_date, at least 4 days before the auction (C9).
  - EC-CAL (roll blackout, early close), known in advance.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - 180-minute window ending 1 minute before the close, from P-K2-002-c: "the difference between
    the yield observed the minute before the auction close time and that 180 minutes earlier".
  - Side SELL, from P-K2-002-b and P-K2-002-d (yields rise pre-auction).
  - **Grid:** none.
- **Expected entries and hold:**
  - One entry on each tenor-matched auction day. From the FiscalData metadata count on
    2026-09-23, before the roll-blackout, early-close and S_X exclusions:

    | Tenor | Exposures | Research window 2025-04-01..2026-06-19 | Confirmation window 2019-05-06..2024-02-29 |
    |---|---|---|---|
    | 2-year | ZT | 13 (3 at 11:30 ET) | 58 (15 at 11:30 ET) |
    | 5-year | ZF | 15 | 56 |
    | 10-year | ZN, TN | 15 | 59 |
    | 30-year | ZB, UB | 15 | 58 |

  - That is about 0.05 entries per trade date, each held 179 minutes. Floor ok. Frequency: see
    C10.
- **Falsification:**
  - The standard condition (UCB95 of mean net daily P&L per contract below eps_X at >= 80%
    achieved null power on the confirmation window counts against it).
  - **Sign check, reported beside the verdict and not a separate test:** the mechanism predicts
    a negative mean gross move of the vehicle, in ticks, from the T_a - 180 open to the T_a - 1
    open on event days. A non-negative confirmation-window mean counts against the mechanism.
- **Topstep check:**
  1. Flat by F: latest fill 11:59 CT.
  2. Order type: market.
  3. D9.4: one trade per event, no stops or brackets, no passive fill.
  4. *: none.
  5. News: flat before the auction close by design. A 07:30 or 09:00 CT release inside the
     window is held at 1 lot-equivalent, half the 2-lot maximum, which F6.3 and D9.5 allow.
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of the admitted vehicles (research and confirmation windows);
  external EC-AUC and EC-CAL.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-aucpost-01 (post-auction recovery)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP (SR 1188, 1991-2024).]
- **Cluster** K2. **Products read:** the traded vehicle; EC-AUC; EC-CAL. **Traded exposures:** the
  same tenor match as K2-aucpre-01 (ZT 2-year, ZF 5-year, ZN and TN 10-year, ZB and UB 30-year).
  ZB and UB (and every exposure) are traded only if D2 admits the exposure. **Vehicle:** D2
  (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** the second arm of the V. After the auction result, dealers cover (buy)
    and yields fall back.
  - **Verified passages:** K2-002 P-K2-002-b, P-K2-002-c (the post-window definition: "from the
    yield observed the minute after the auction results announcement to that 180 minutes
    later") and P-K2-002-d ("reversal (-0.32 to -0.75 bps for most maturities)"). Supporting:
    K2-001 P-K2-001-a ("recover shortly thereafter").
  - **Classification:** new (log tag). This is a separate hypothesis from the pre-auction arm.
- **Event set and T_a:** as K2-aucpre-01.
- **Entry rule:** BUY, market intent on the bar at T_a + 4 min, filling at the open of the bar at
  T_a + 5 min.
- **Exit rule:** market intent on the bar at T_a + 184 min, filling at the open of T_a + 185 min,
  or the forced flatten at F if earlier.
- **Holding horizon:** 180 minutes.
- **Session window:** 12:05-15:05 CT for 13:00 ET closes; 10:35-13:35 CT for 11:30 ET closes.
  Flat by F (15:05 < 15:08).
- **Data fields read:** as K2-aucpre-01. No results field (bid-to-cover, high yield) is read.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - 180-minute hold, from P-K2-002-c.
  - **Entry lag 5 minutes after the competitive close: a judgment.** P-K2-002-c starts the
    window at "the minute after the auction results announcement". No obtainable source found
    gives a per-auction results release time: the FiscalData record carries the results but no
    release timestamp. A fixed lag therefore stands in. 5 minutes sits at the start of the
    interval over which K2-011 P-K2-011-b finds spreads back to normal ("revert to normal values
    after five to 15 minutes"). K2-002 P-K2-002-f says depth "normalize[s] quickly" after the
    auction.
  - **No leakage:** the rule reads no result, so the lag cannot leak information. On an auction
    whose results appeared after T_a + 5, the member is simply positioned before the release
    that day.
  - **Grid:** none.
- **Expected entries and hold:** as K2-aucpre-01: research 13 (ZT) or 15 (other exposures),
  confirmation 56 to 59; about 0.05 per trade date, held 180 minutes. Floor ok.
- **Falsification:** the standard condition. Sign check (reported): the mechanism predicts a
  positive mean gross move, in ticks, from the T_a + 5 open to the T_a + 185 open on event days.
- **Topstep check:**
  1. Flat by F: last fill 15:05.
  2. Order type: market.
  3. D9.4: ok.
  4. *: none.
  5. News: may be positioned before a late results release, at 1 lot-equivalent (not the full
     maximum).
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** as K2-aucpre-01.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-fomcpost-01 (post-FOMC drift)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP (SR 1188, 1991-2024).]
- **Cluster** K2. **Products read:** the traded vehicle; EC-FOMC; EC-CAL. **Traded exposures:**
  ZT, ZF, ZN, TN, ZB, UB. ZB and UB (and every exposure) are traded only if D2 admits the
  exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "FOMC announcements are followed by a significant and persistent
    decline in yields - on the order of 0.5-1.5 bps - consistent with the previously documented
    post-FOMC drift in bond markets" (K2-002 P-K2-002-e). Falling yields mean rising futures
    prices, so the member is unconditionally long after the announcement's jump window.
  - **Why the entry waits:** K2-018 P-K2-018-c and P-K2-018-d place the announcement's co-jump
    in the 30 minutes after 13:00 CST, and its direction depends on the surprise ("17 positive
    policy surprise days ... 14 negative"). The member starts after that window, so it trades
    the drift, not the jump.
  - **Maturities:** P-K2-002-e is not split by maturity. K2-002's sample spans 2- to 30-year
    maturities (log product field), so the member covers all six tenors. K2-020 P-K2-020-a notes
    that post-FOMC return connections are amplified "except for 30-year futures". That is
    context, not a reason to drop ZB or UB.
  - **Classification:** new (log tag for K2-002).
- **Event set:**
  - The statement day of each regularly scheduled FOMC meeting (EC-FOMC). The statement must be
    released at 13:00 CT that day, a fact public at 13:00, before the 13:29 decision.
  - Unscheduled meetings, notation votes and conference calls are excluded.
- **Entry rule:** BUY, market intent on the bar at 13:29, filling at the 13:30 open.
- **Exit rule:** market intent on the bar at 15:04, filling at the 15:05 open, or F.
- **Holding horizon:** 95 minutes. **Session window:** 13:30-15:05 CT. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m (C8).
  - EC-FOMC meeting schedule: free; the calendar page covers 2021-2027 and the historical
    materials cover 2019-2020. Available before each year.
  - Statement release at 13:00 CT (Topstep F6; P-K2-018-c): public at 13:00 CT.
  - EC-CAL.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - Entry at 13:30, after the 30-minute announcement window of P-K2-018-c.
  - **Exit at 15:05: a judgment.** It is the last fill before F. K2-002's 180-minute post-window
    would end at 16:00 CT, past F.
  - **Grid:** none.
- **Expected entries and hold:**
  - Research window: 10 statement days (Fed calendar, fetched 2026-09-23): 2025-05-07,
    2025-06-18, 2025-07-30, 2025-09-17, 2025-10-29, 2025-12-10, 2026-01-28, 2026-03-18,
    2026-04-29, 2026-06-17.
  - Confirmation window: about 38 (8 scheduled meetings a year on the calendar pages; E.2 counts
    them).
  - That is about 0.03 per trade date, held 95 minutes. Floor ok.
- **Falsification:** the standard condition. Sign check (reported): the mechanism predicts a
  positive mean gross move from the 13:30 open to the 15:05 open on event days.
- **Topstep check:**
  1. Flat by F: 15:05.
  2. Order type: market.
  3. D9.4: ok.
  4. *: none.
  5. News: the entry is 30 minutes after the statement. It overlaps whatever follows the
     statement that afternoon, at 1 lot-equivalent (not the full maximum).
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of the admitted vehicles; EC-FOMC; EC-CAL.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-predrift-01 (pre-release informed-trading drift, ISM Services)
- **Cluster** K2. **Products read:** the traded vehicle; EC-ISM; EC-CAL. **Traded exposures:** ZN
  {ZN} and ZB {ZB}, the two exposures the source documents: ZN by ticker, P-K2-007-b; 30-year bond
  futures in the robustness check, P-K2-007-f. ZB (and ZN) are traded only if D2 admits the
  exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** "Prices begin to move in the 'correct' direction about 30 minutes before
    the release time. The pre-announcement price drift accounts on average for about 40% of the
    total price adjustment" (K2-007 P-K2-007-a).
  - **The ZN row for this release:** ISM Non-Manufacturing, with a pre-release drift of
    "-0.044 (0.009)***" for the 10-year note per one-standard-deviation positive surprise
    (P-K2-007-d). This is the only release whose ZN drift is in a logged passage.
  - **Context passages:** bond 5-minute sd 0.04% (P-K2-007-c) and ZN median effective spread
    0.013% (P-K2-007-e).
  - **The inference, stated:** the sign of the early drift proxies the sign of the coming
    surprise, and part of the adjustment (about 60%) is still to come at and after the release.
    The rule therefore trades continuation of the early drift through the release.
  - **No consensus data:** the rule reads no survey consensus. Rule 3's proxy route is used: the
    price path itself stands in for the surprise.
  - **Classification:** new (log tag for K2-007).
  - **Not a CP1 duplicate:** CP1 is a fixed-clock, late-session trade on the overnight-plus-first-
    30-minute return. This member is event-conditioned, in a pre-release window, with a 15-minute
    hold that ends after the release.
- **Event set:** EC-ISM Services release dates, T = 09:00 CT (10:00 ET).
- **Entry rule:**
  - s = sign(close of the bar at 08:49 - open of the bar at 08:30), in ticks, that is the
    [T-30, T-11] return. If s = 0, no trade.
  - Market intent on the bar at 08:49 in direction s, filling at the 08:50 open.
- **Exit rule:** market intent on the bar at 09:04, filling at the 09:05 open (T + 5 min).
- **Holding horizon:** 15 minutes. **Session window:** 08:30-09:05 CT (signal 08:30-08:49;
  position 08:50-09:05). Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m open, close and instrument_id (C8). The latest input is available at
    08:50 CT, the decision time.
  - EC-ISM release date and time: free (PR Newswire archive); release schedule published in
    advance; the index value is never read.
  - EC-CAL.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - Signal start at T-30, from P-K2-007-a ("about 30 minutes before").
  - Exit at T+5, from the paper's total-impact window "30 minutes before to 5 minutes after
    release" (log K2-007, horizon field).
  - **Signal end T-11 and entry T-10: a judgment.** This leaves the last 10 pre-release minutes
    of drift, plus the release move, to the position. It also makes the hold 15 minutes, above
    D9's 10-minute mean floor. A T-5 entry would give a 10-minute hold, exactly at that floor,
    with no margin.
  - **Grid:** none.
- **Expected entries and hold:** 1 per ISM Services release day with s != 0. That is about 15 in
  the research window and about 58 in the confirmation window (monthly; E.2 counts them from the
  archive), about 0.05 per trade date, held 15 minutes. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** hit rate P[sign(open 09:05 - open 08:50) = s] > 0.5, and the mean
    signed gross move > 0, on event days, as the mechanism predicts.
  - **Out of sample:** the paper's sample is 2008-2014 (log), so both windows here are out of
    the source's sample.
- **Topstep check:**
  1. Flat by F: 09:05.
  2. Order type: market.
  3. D9.4: one trade per event; not a stray-fill gap trade, since the entry precedes the release
     by 10 minutes.
  4. *: none.
  5. News: **holds into a scheduled release by design.** Size is 1 lot-equivalent, half the XFA
     starting maximum, so the trade is not "full Maximum Position Size directly into a scheduled
     major news event" (F6.3, D9.5). Flagged to the lead as the one K2 member that enters
     because of a release.
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of ZN and ZB (research and confirmation windows); EC-ISM; EC-CAL.
- **Trials in N:** 1 per admitted exposure among {ZN, ZB} (at most 2).

### K2-monthend-01 (month-end index-extension demand, intraday slices)
- **Cluster** K2. **Products read:** the traded vehicle; EC-CAL. **Traded exposures:** ZT, ZF, ZN,
  TN, ZB, UB. ZB and UB (and every exposure) are traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **Returns side:** "Average returns are positive and highly significant in the last few days
    of the month, and are not significantly different from zero at other times" (K2-021
    P-K2-021-a). About 20 bp a month at the 10-year point (P-K2-021-b). The paper's own trade
    buys two trading days before month-end and sells at the last day's close (P-K2-021-c). The
    last-day Sharpe is close to 1, and the two-day position earns 4.5% annualized
    (P-K2-021-d). The cost benchmark is a 2-3 bp spread (P-K2-021-e).
  - **Flow side:** month-end trading concentrates at the index strike times: 3 p.m. ET until
    2021, "now largely 4:00 p.m. ET" (K2-003 P-K2-003-a/b/c/d; for example, more than a quarter
    of month-end daily activity falls in 3:45-4:15 p.m. ET in 2025).
  - **How the member uses them:** the two-day hold is infeasible under flat-by-F (X-04). The
    member takes the day-session slice of each of the two days the paper holds, and exits after
    the later strike time.
  - **Classification:** port of D.1 family E (calendar/events; the log's tag for K2-003 and
    K2-021), written on K2's own clock. It is not one of D6's core ports; D6 ports no family E
    member.
- **Event set:** N = the last trade date of each calendar month in EC-CAL, and N-1 = the trade
  date before it. Both are traded, each independently (C4 applies per date).
- **Entry rule:** BUY, market intent on the bar at 07:20 (O), filling at the 07:21 open.
- **Exit rule:** market intent on the bar at 15:04, filling at the 15:05 open, or F.
- **Holding horizon:** 464 minutes. **Session window:** 07:21-15:05 CT. This covers the pre-2021
  strike (3 p.m. ET = 14:00 CT) and the later one (4 p.m. ET = 15:00 CT), so no date switch is
  needed. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open and instrument_id (C8); EC-CAL trade dates, known
  in advance.
- **Order type:** market. **Sizing:** q_c (= 1).
- **Parameters:**
  - Days N-1 and N, from P-K2-021-c.
  - **Entry at O: a judgment.** K2-003's flows are cash-session flows, measured over
    "7:00 a.m.-5:30 p.m. ET", with the strike times inside the day. D9's member-level coverage
    check is built for the day session. The Globex-night part of each day is not held.
  - **Exit at 15:05:** after the 15:00 CT strike and the last fill before F.
  - **Grid:** none.
- **Expected entries and hold:**
  - Two entries a month: 28 in the research window (April 2025 to May 2026; June 2026's last
    dates fall after 2026-06-19) and 116 in the confirmation window (May 2019 to February 2024).
    These counts are before exclusions.
  - That is about 0.1 per trade date, held 464 minutes. Floor ok.
  - **Roll interaction:** K2-005 places the quarterly roll in the days before First Intention
    Day. Month-end dates that E.2's roll table blacks out are dropped, not moved.
- **Falsification:** the standard condition. Sign check (reported): positive mean gross move
  from the 07:21 open to the 15:05 open on event days. Days N and N-1 are reported separately
  (descriptive).
- **Topstep check:**
  1. Flat by F: 15:05.
  2. Order type: market.
  3. D9.4: ok.
  4. *: none.
  5. News: holds through any same-day release at 1 lot-equivalent (not the full maximum).
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of the admitted vehicles (research and confirmation windows); EC-CAL.
- **Trials in N:** 1 per admitted exposure (at most 6).

### K2-ml-01 (the ML member, D15; this entry fills only D15.10's fields)
- **Traded vehicle: ZN.**
  - **Reason:** ZN is the single K2 exposure the log documents most often:
    - K2-007 (ZN by ticker, P-K2-007-b);
    - K2-017 (the 10-year note futures, P-K2-017-a);
    - K2-018 (TY in the curve, P-K2-018-b);
    - K2-011 (10-year note, P-K2-011-c/e);
    - K2-021 (10-year figure, P-K2-021-b).
    It also has the highest public ADV in the cluster: 2,589,058 contracts per day, YTD 2026
    (liquidity JSON).
  - **Fallback, declared now so it is not chosen later:** if D2 does not admit ZN, the vehicle is
    ZF (K2-008's 5-year, P-K2-008-e; K2-020's 5-year transmitter, P-K2-020-a). If D2 admits
    neither, the lead decides.
- **Products the features read:** ZN (vehicle), ZF, ZB and ZT. Their bars are needed even where
  an exposure is not traded (D2: a non-traded exposure may serve as a leg). The calendars read
  are EC-FOMC, EC-AUC, EC-NFP, EC-ISM, EC-CAL and EC-NYSE.
- **Cluster features.** There are 7; together with D15.4's B1-B5 that makes 12. For every
  feature, t_j is the decision time, and "bar at t_j - 1 min" is the last bar closed at t_j.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| K1 | fomc_post | 1 if d is the statement day of a regularly scheduled FOMC meeting on the schedule published before d, and t_j >= 13:00 CT; else 0 | K2-002 P-K2-002-e; K2-018 P-K2-018-c, P-K2-018-d | schedule known in advance (EC-FOMC); depends only on the clock |
| K2 | auction_phase | Over EC-AUC records with auction_date = d, security_type Note or Bond, floating_rate "No", inflation_index_security "No", original_security_term in {2-, 5-, 7-, 10-, 20-, 30-Year} (K2-002's maturity set) and announcemt_date < d. The value is +1 if some record has T_a <= t_j < T_a + 180 min; else -1 if some record has T_a - 180 min <= t_j < T_a; else 0 | K2-002 P-K2-002-b, P-K2-002-c, P-K2-002-d; K2-001 P-K2-001-a; K2-006 P-K2-006-a | announcement fields, published on announcemt_date, before d (C9); no result field read |
| K3 | month_end | 2 if d is the last trade date of its calendar month in EC-CAL; 1 if it is the second-to-last; else 0 | K2-021 P-K2-021-a, P-K2-021-c, P-K2-021-d; K2-003 P-K2-003-c, P-K2-003-d | calendar known in advance |
| K4 | release_min | On d, let tau be the latest scheduled release time <= t_j among the Employment Situation (07:30 CT, EC-NFP) and ISM Services (09:00 CT, EC-ISM) releases scheduled for d. The value is min(t_j - tau, 120) in minutes if such tau exists; else -1 | K2-008 P-K2-008-b, P-K2-008-c, P-K2-008-d ("volatility for 40 minutes and slight effects for several hours"); K2-011 P-K2-011-a, P-K2-011-b; K2-006 P-K2-006-b (NFP and ISM_NonM listed); K2-007 P-K2-007-d; Topstep F6 (07:30 CT) | release schedules known in advance; depends only on the clock |
| K5 | zf_ret30 | (close of the ZF bar at t_j - 1 min - open of the ZF bar at t_j - 30 min) / 0.0078125, in ZF ticks. Both bars must exist with one ZF instrument_id, else no trade at t_j. With the ZF fallback vehicle, this reads ZN instead (/ 0.015625) | K2-020 P-K2-020-a (the 5-year's "central information-transmitting role"); K2-008 P-K2-008-e | ZF bar closes <= t_j |
| K6 | curve_ret30 | 10^4 x [ln(ZB close_{t_j - 1 min} / ZB open_{t_j - 30 min}) - ln(ZT close_{t_j - 1 min} / ZT open_{t_j - 30 min})], using the same bar convention as K5. Each leg's two bars must exist with one instrument_id, else no trade at t_j | K2-018 P-K2-018-a, P-K2-018-d (co-jumps and level shifts across the curve); K2-020 P-K2-020-a (cross-tenor return connections) | ZB and ZT bar closes <= t_j |
| K7 | eqopen_ret | If d is an NYSE trading day and t_j >= 09:00 CT: (close of the vehicle's 08:59 bar - open of its 08:30 bar) / vehicle tick. If t_j <= 08:30 CT, or the NYSE is closed on d: 0. This 0 is a fixed literal because the window has not happened; it is not an imputation, and a missing 08:30 or 08:59 bar means no trade | K2-017 P-K2-017-a, P-K2-017-b ("more informative for permanent price changes in the 30-min period after the US stock market opens"; placebo on US holidays) | 09:00 CT, from the vehicle's own bars; NYSE holidays published in advance |

- **Decision window [W0, W1] = [07:30, 14:30] CT; horizon h = 30 minutes.**
  - Decision times are t_j = 07:30, 08:00, ..., 14:30, which is 15 a day. W1 + h = 15:00 <= F.
  - **Why this window:** every scheduled K2 event in the log falls on a :00 or :30 CT boundary.
    That covers the 07:30 releases, the 09:00 ISM release, the auction closes (10:30, and 12:00
    for 13:00 ET), the 13:00 FOMC statement, and the 14:00 and 15:00 index strikes. Each event
    minute therefore coincides with a decision time.
  - **Consequence of D15.3's fill convention:** a position covers [t_j + 1 min, t_j + h] and
    exits at the open of t_{j+1}. The member is therefore flat during the first minute of every
    event, which is the minute K2-011 P-K2-011-b says carries the adjustment ("generally occurs
    within one minute"). It trades the post-event dynamics, never the jump.
  - **Why h = 30:** it is the horizon over which the logged responses play out. K2-007's drift
    runs over the 30 minutes before a release (P-K2-007-a). K2-017's window is the 30 minutes
    after the equity open (P-K2-017-b). K2-018 uses a 30-minute post-FOMC window (P-K2-018-c).
    K2-008 finds volatility elevated for about 40 minutes (P-K2-008-d).
    - h = 15 would sit inside the 5-15 minute widened-spread period (P-K2-011-b).
    - h = 60 or 120 would average across consecutive events (07:30 then 09:00; 12:00 then
      13:00).
- **Expected rows:** about 4,350 in the research window: 15 per eligible trade date x about 290
  eligible dates, after the roll-blackout, vendor-degraded and early-halt exclusions of D15.3.
  E.2 gives the exact count.
- **Expected entries:** at most 15 per day (<= 20), each held 30 minutes. Floor ok by
  construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps
  at >= 80% achieved null power on the confirmation window counts against it). Failing the D5
  screen puts it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 15:00.
  2. Order type: market (D15.6).
  3. D9.4: at most 15 entries a day, 30-minute holds, no stops or brackets.
  4. *: none.
  5. News: q_c = 1 lot-equivalent, not the full maximum. The member is also flat in the first
     minute of every :00/:30 scheduled event.
  6. Position limit: 1 contract.
  7. Price limit: D9.7 per E.2.
- **Data needed:** ohlcv-1m of ZN, ZF, ZB and ZT. The research window is used for training and
  tuning, the confirmation window for the frozen model. External data: EC-FOMC, EC-AUC, EC-NFP,
  EC-ISM, EC-CAL, EC-NYSE.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48
  (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K2-scalp-01 | ZB scalping: about 10 trades per session targeting 8 ticks and averaging about 1 tick (K2-012 P-K2-012-b, P-K2-012-c) | D9.4 prohibited patterns; rule 4 (orders) | "Running scalping algorithms designed to exploit unrealistic SIM fills" [F7.2]. The edge rests on passive fills and queue position at about 1 tick per trade. The performance claims are vendor-asserted and unverified (P-K2-012-c). |
| X-02 K2-hftbook-01 | ZB quote-level fair-price trading with order-book and cash-futures cointegration features (K2-019 P-K2-019-a) | D9.4; rule 4 (market orders only); data | The benefit is cost reduction versus a one-tick spread, which needs passive order placement and queue priority. Its inputs are quote-level cash and futures books, which the program does not hold. |
| X-03 K2-auc5d-01 | Short 5 days before an auction, long 5 days after (K2-001 P-K2-001-a, P-K2-001-b, P-K2-001-c) | Flat by F | Multi-day positions. The same-day slice is K2-aucpre-01 and K2-aucpost-01. |
| X-04 K2-eom2d-01 | Long from the close two trading days before month-end to the last day's close (K2-021 P-K2-021-c) | Flat by F | Two-night hold. The day-session slices are K2-monthend-01. |
| X-05 K2-basis-01 | Cash-futures basis trade (K2-009 P-K2-009-a, P-K2-009-b, P-K2-009-c) | Flat by F; tradability | Multi-quarter repo-financed position with a cash Treasury leg that is not tradable on Topstep. The source is descriptive, with no signal. |
| X-06 K2-aucother-01 | The auction V (K2-002) traded on 3-, 7- and 20-year auctions, or on TIPS and FRN auctions | Rule 1 (sourcing) | No permitted contract carries those nominal tenors. Mapping them to ZT, ZF, ZN or ZB would need deliverable-basket facts the log does not hold (K2-004 logged only the CTD definition, P-K2-004-a). TIPS and FRNs are outside K2-002's nominal-coupon sample (log product field). These auctions do enter K2-ml-01's auction_phase feature (7-, 20-year) as a clock input, which needs no mapping. |
| X-07 K2-btc-01 | Trade the futures on the bid-to-cover ratio after the results: a high ratio raises futures prices (K2-006 P-K2-006-a) | Rule 3 (data availability and look-ahead); intraday evidence | No confirmed source gives a per-auction results publication time (FiscalData carries results with no release timestamp), so no decision time can be proven to follow publication. With a lag long enough to be safe, only a daily-frequency effect is documented, and only in an abstract; the log has no intraday post-result drift. |
| X-08 K2-surprise-01 | Trade the post-release move signed by the announcement surprise (K2-011 P-K2-011-a; K2-015 P-K2-015-a; K2-008 P-K2-008-b) | Rule 3 (proprietary data); evidence for the proxy | The surprise needs consensus surveys (Bloomberg or MMS). No named, obtainable historical source was found in E.0. The obtainable proxy, the first minutes' price response, leaves nothing documented to trade: "the adjustment to news generally occurs within one minute" (P-K2-011-b), and no post-jump drift is in the log. The one documented drift, pre-release, is K2-predrift-01. |
| X-09 K2-rollspread-01 | Trade the calendar spread, or the legs, during the quarterly roll (K2-005 P-K2-005-a, P-K2-005-b, P-K2-005-c, P-K2-005-d) | D9.4; D2 vehicle; roll blackout | The documented effect is pro-rata passive fill allocation, an execution effect that depends on resting orders. The spread is not an exposure's D2 vehicle. The program removes roll-blackout dates. |

---

## 3. Beyond budget (lead decides)

None. The log supports 5 new members inside the budget of 11. Three candidates were considered
and not written:
- **Extending K2-predrift-01 to the other drift announcements.** K2-007's abstract says "Nine of
  the 20 announcements that move markets show evidence of substantial informed trading"
  (P-K2-007-a), but the nine are not in any logged passage. This is insufficient evidence in the
  log, not a budget overflow. The lead decides whether to have those passages logged (section 7,
  item 4).
- **A strike-window-only month-end member.** K2-003 documents volume, not price direction:
  insufficient evidence.
- **A last-day-only month-end variant.** It is the paper's sub-result, already inside
  K2-monthend-01's day N.

---

## 4. Routed to K8

| Source | Legs | One phrase |
|---|---|---|
| Sharma (arXiv:1705.08022), "Using Macroeconomic Forecasts to Improve Mean Reverting Trading Strategies" (K2 log section 4; no registry id) | K2 10-year Treasury yield signal -> K3 FX pairs | the 10-year yield used as a forecast input to trade FX |
| Alquist, Ellwanger, Jin (2020), K4-008 (registry tags K4, K1, K2, K3) | K4 oil-inventory news -> K2 Treasury futures (and K1, K3) | one cluster's announcement response on another's product; K4 already flagged it; no K2 passage was ever logged |

---

## 5. Log accounting

Every passed item in reports/stage_e0_research_K2.md, and every `[K2]`-tagged passage elsewhere.

| Item | Disposition |
|---|---|
| K2-001 Lou, Yan, Zhang | Supporting evidence in K2-aucpre-01, K2-aucpost-01 and K2-ml-01 (P-K2-001-a). The literal multi-day strategy is not intraday-feasible: X-03. |
| K2-002 Fleming, Liu, Nguyen (SR1188) | Used: K2-aucpre-01 and K2-aucpost-01 (P-b, c, d, f); K2-fomcpost-01 (P-e); K2-ml-01 auction_phase and fomc_post. |
| K2-003 Dyer, Fleming, Shachar | Used: K2-monthend-01 (exit timing and flow side, P-a to d); K2-ml-01 month_end. A strike-window-only member is insufficient evidence (volume, not price; section 3). |
| K2-004 CME "Understanding Treasury Futures" | Reference only, with no mechanism. P-K2-004-a is cited for why the tenor mapping stops at nominal tenors (X-06). |
| K2-005 Quantitative Brokers roll | Excluded, X-09 (execution and pro-rata fills, the roll blackout, not a vehicle). P-K2-005-d informs no rule. |
| K2-006 / K2-014 Smales (duplicate registry lines; one source) | Daily-frequency supporting evidence for K2-aucpre-01 (P-a). P-b lists NFP and ISM_NonM, supporting K2-ml-01 release_min. The bid-to-cover direction is excluded, X-07. Not intraday-feasible as documented (daily, abstract only). The duplicate registry id is left for the lead. |
| K2-007 Kurov, Sancetta, Strasser, Wolfe (panel K1/K2) | Used: K2-predrift-01 (P-a to f); K2-ml-01 release_min (P-d). The `[K1]` passages belong to K1's CatalogWriter. |
| K2-008 Fleming, Remolona | Used: K2-ml-01 release_min (P-b, c, d) and zf_ret30 (P-e). No directional member: the documented pattern is volatility, volume and spread, not direction (part of X-08). |
| K2-009 Mixon, Orlov (CFTC) | Excluded, X-05. Not intraday-feasible. |
| K2-010 Bodor, Carlier (Eurex Bund LOB) | Not ported: D.1 family A. D6 does not port family A, and the documented pattern is non-directional activity seasonality whose Eurex timing does not transfer (log quality note). Insufficient evidence for a K2 rule. |
| K2-011 Balduzzi, Elton, Green | Used for timing: K2-aucpost-01 (P-b, the entry lag) and K2-ml-01 (the h choice and release_min, P-a, b). The surprise-response member is excluded, X-08. |
| K2-012 Kinlay | Excluded, X-01. |
| K2-013 Dujava (Quantpedia) | Not intraday-feasible: monthly signals and rebalancing on end-of-month closes (P-K2-013-b). Not covered by any port; CP3 is a prior-day CLV rule, not a multi-week trend. |
| K2-015 Andersen, Bollerslev, Diebold, Vega (panel K1/K2/K3) | The surprise-response member is excluded, X-08. P-a and P-c support K2-ml-01's event-clock design. The `[K1]` and `[K3]` passages belong to those clusters. |
| K2-016 Brandt, Kavajecz, Underwood | Insufficient evidence: abstract only, a cash-futures order-flow description with no directional rule, and P-K2-016-b is itself unverified. |
| K2-017 Indriawan, Jiao, Tse | Used: K2-ml-01 eqopen_ret (P-a, b). A directional member is insufficient evidence: abstract only, and "more informative for permanent price changes" does not predict a drift. |
| K2-018 Barunik, Fiser | Used: K2-fomcpost-01 entry timing (P-c, d); K2-ml-01 fomc_post and curve_ret30 (P-a, d). No directional member: the co-jump direction depends on the surprise (P-d). |
| K2-019 Decrem et al. | Excluded, X-02. |
| K2-020 Chen, Fu, Yang | Used: K2-ml-01 zf_ret30 and curve_ret30 (P-a). A directional tenor lead-lag member is insufficient evidence: abstract only, and it documents volatility transmission and contemporaneous connections, not a signed lead-lag. |
| K2-021 Hartley, Schwarz | Used: K2-monthend-01 (P-a to e); K2-ml-01 month_end. The literal two-day hold is excluded, X-04. |
| K2-022 Zhang, Hung, Chiu | Not intraday-feasible as documented, and insufficient evidence: abstract only, volatility timing with periodic rebalancing. D-family gates are not ported (D6). K2-ml-01's common B4 carries volatility state. |
| Sharma (K2 log section 4) | Routed to K8. |
| K4-008 (registry, tagged K2) | Routed to K8 (K4's flag). No `[K2]` passage exists; K4 did not read it past the pre-filter. |
| `[K2]` search in the other logs (K3, K3 partial, K4 shallow, K5, K5 partial) | No `[K2]`-tagged passage. The mentions of K2 are rejection or flag lines: R-K5-003 (Kurov is K1/K2 territory, already K2-007), the K3 and K4 lines on K4-008, and K5's dollar and rates against gold (K8). Nothing to use. |
| R-K2-001 to R-K2-006; Carver and Robot Wealth (unreached) | Not passed items. Rejected at the pre-filter, or unread by the reader. Not used. |

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all six admitted) |
|---|---|---|---|
| K2-cp1-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-cp2-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-cp3-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-aucpre-01 | ZT, ZF, ZN, TN, ZB, UB (tenor-matched) | 1 | 6 |
| K2-aucpost-01 | ZT, ZF, ZN, TN, ZB, UB (tenor-matched) | 1 | 6 |
| K2-fomcpost-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-predrift-01 | ZN, ZB | 1 | 2 |
| K2-monthend-01 | ZT, ZF, ZN, TN, ZB, UB | 1 | 6 |
| K2-ml-01 | ZN (fallback ZF) | 48 in research-window accounting only (D15.8) | 1 |
| **Cluster total** | | | **45** (18 port + 26 new + 1 ML). With E admitted exposures and E_pd admitted among {ZN, ZB}: 7E + E_pd + 1. Without ZB and UB: 30. |

---

## 7. Open items for the lead (decisions reserved to the lead; none taken here)

1. **CP2 has no latest-entry time.** It is copied verbatim from D6. On K2, C = 14:00 and
   F = 15:08, so a first break between 14:00 and 15:08 can be entered and then cut short by F.
   On MES the equivalent gap was 8 minutes. The lead decides whether the port needs a
   latest-entry time to remain the MES family.
2. **Event-member frequency (C10).** The four event members, 26 trials, trade on about 3% to 10%
   of dates. By arithmetic they need about 10 to 29 x eps_X per event to reach eps_X a day, so
   they are likely to yield "null at eps". That is informative for the funnel but costs trials in
   N. The lead decides whether they stay at one trial per exposure, are pooled, or are cut.
3. **D2 at the 1-lot cap.** Every K2 member trades exactly 1 contract (C6), so D2's band reduces
   to r_c / R* in [0.5, 2.0]. Exposures below the band are possible as well as ZB and UB above
   it. E.2 measures; the catalog assumes neither.
4. **K2-007's nine drift announcements are not logged.** Extending K2-predrift-01 beyond ISM
   Services needs those passages logged first, by a reader follow-up. The full text was fetched
   by the K2 reader.
5. **Duplicate registry lines K2-006 and K2-014** (the same Smales paper), and K2-006's
   "authors: unspecified". Registry hygiene, for the lead.
6. **E.2 checks named in this catalog:**
   - tick-size history for 2019-05..2026-06 (C7; CP2's buffer);
   - the FiscalData announcement against the query for closing_time_comp (C9);
   - paging the PR Newswire ISM archive and re-verifying each 10:00 ET stamp (WebFetch gave a
     paraphrase);
   - the FOMC 2019-2020 schedule from the Fed's historical pages;
   - whether CBOT Treasury futures carry any CME daily price limit (D9.7);
   - the roll-blackout interaction with month-end and late-month auction dates.
7. **Mapping judgments the lead may narrow.** TN is mapped to 10-year auctions and UB to 30-year
   auctions, by the contracts' nominal tenor. K2-predrift-01 is limited to {ZN, ZB} by the
   source's product list.
8. **The ML vehicle's fallback order** (ZN, then ZF) is declared in K2-ml-01. The lead may
   overrule it before E.2.
