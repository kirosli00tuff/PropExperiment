# Stage E.0 hypothesis catalog, cluster K3 (FX: 6E, E7, M6E, 6A, M6A, 6B, M6B, 6C, 6J, 6S, 6N)

Writer: CatalogWriter-K3-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from 01:15 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any K3 product (or any equity index) existed on this machine. It uses only these product-specific
numbers:
- contract specifications and public ADV (reports/stage_e0_liquidity.json);
- Topstep's published fees, hours and release table (reports/stage_e0_topstep_facts.md);
- calendar metadata: bank-holiday and national-holiday lists, TARGET closing days, fix clock times.

No price level, range or volatility of any product is used or assumed anywhere below.

**Inputs read in full:**
- reports/stage_e0_research_K3.md (the superseded sonnet log was not used).
- Every `[K3]`-tagged passage elsewhere: K2-015 (Andersen, Bollerslev, Diebold, Vega) in
  reports/stage_e0_research_K2.md. No other log holds a `[K3]` tag (grep over all
  reports/stage_e0_research_K*.md).
- reports/stage_e0_source_registry.jsonl (K3 lines, K2-015, K4-008).
- docs/STAGE_E_DESIGN.md D1-D15 with the 21:12 and 21:52 amendments; reports/stage_e0_STATE.md rulings.
- reports/stage_e0_partition.md; reports/stage_e0_topstep_facts.md (F1-F12);
  reports/stage_e0_liquidity.json (K3 rows).
- reports/stage_d1f_confirmation_list.md 2.1 A3; strategy/research/b_reference_breakout/
  h1_friction_aware_opening_range_breakout.py; strategy/research/h_daily_bar/h6_prior_close_location.py.
- reports/stage_e0_catalog_K2.md and reports/stage_e0_catalog_K4.md, for format only.

**Official pages fetched in this task** (curl, 2026-09-24 01:22-01:30 PDT; saved under the
scratchpad `fetch/` folder). Fetched only to confirm fix times and calendar sources; no mechanism
research was done:
- https://www.gov.uk/bank-holidays.json (HTTP 200). England-and-Wales events 2019-01-01 to 2028,
  83 events, including the ad hoc ones (for example 2022-09-19).
- https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv (HTTP 200, Shift-JIS). Japanese national
  holidays 1955-2027.
- https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html
  (HTTP 200), verbatim: "The reference rates are usually updated at around 16:00 CET every working
  day, except on TARGET closing days . They are based on the daily concertation procedure between
  central banks across Europe, which normally takes place around 14:10 CET."
- https://www.ecb.europa.eu/ecb/contacts/working-hours/html/index.en.html (HTTP 200). It marks
  "* : TARGET closing day" on "New Year's Day*", "Good Friday*", "Easter Monday*", "Labour Day*",
  "Christmas Day*", "Christmas Holiday* 26 December", listed for 2026, 2027 and 2028.
- HEAD requests only, no body read (the bodies are equity-index price histories):
  - STOXX h_3msx5e.txt: the certificate chain was rejected from this machine. A Wayback capture exists:
    HEAD on web.archive.org/web/2025/... returned 302.
  - FRED series NIKKEI225: no response (HTTP/2 stream error).
  - indexes.nikkei.co.jp/en/nkave/archives/data: 403 to curl.
  - msci.com/end-of-day-data-search: 200 with an empty body on HEAD.

  None of these confirms that a free history is available (see K3-mehedge-01).

**Time-zone conversions** were computed locally with Python zoneinfo (the IANA tz database). No
network was used for them.

---

## 0. Header

| Item | Value |
|---|---|
| Products | 6E, E7, M6E*, 6A, M6A*, 6B, M6B, 6C, 6J, 6S, 6N (CME; Topstep F1). 6M is on the permitted list but out of the traded universe |
| Exposures IN | EUR {6E, E7, M6E}; AUD {6A, M6A}; GBP {6B, M6B}; CAD {6C}; JPY {6J}; CHF {6S}; NZD {6N} (design D1 table) |
| **D1 applied: 6M out** | MXN (6M) fails D1(b): coverage 0.903 < 0.95. No member trades or reads it |
| Members | **10 = 6 new + 3 core ports + 1 ML member.** Budget 15, so 5 slots are unused (section 3) |
| Trials in N (confirmation) | **36 if D2 admits all seven exposures:** 21 port + 14 new + 1 ML. The general formula is in section 6 |
| ML grid | 48 configurations, counted only in the K3 screening session's research-window accounting (D15.8) |
| Starred products | **M6E and M6A: restriction UNRESOLVED** (D9.8; topstep facts F12.1: "no product-specific restriction naming them was found"). Every EUR and AUD member carries the flag. M6B is not starred |
| D2 | Vehicle "D2 (chosen in E.2)" throughout. CAD, JPY, CHF and NZD have one full-size contract each (q = 1). EUR, AUD and GBP may go to a micro (q <= 10) if the full-size contract fails rho <= 2.0. Every entry is written for the exposures its evidence names, each **traded only if D2 admits the exposure** |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the one-minute ohlcv-1m bar whose
  ts_event (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values are
  usable from then on. "The bar at T - k" means the bar whose open is k minutes before clock time T.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine convention
  of D6 and D15.3). "Market intent on the bar at X" fills at the open of the bar at X + 1 min.
- **C3 Trade date.** d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md). CME FX reopens at
  17:00 CT and Topstep allows trading from "Weekday reopen | 5:00 PM CT" (F4). So a position opened
  after 17:00 CT on calendar day d-1 and closed before 15:08 CT on d lies inside one trade date and
  holds nothing across the daily close. The overnight members below (K3-tkypre-01, K3-tkypost-01,
  K3-ecbfix-01's first leg, K3-ml-01's early decisions) rely on this.
- **C4 Exclusions for the six new members.** The ports follow D6 as written. A new member does not
  trade on:
  - roll-blackout dates (program convention, `screen_candidate` with `roll_blackout`);
  - dates the D10 FX calendar marks as early halt or early close ("Days with early_halt_ct set: no
    trade", Family H);
  - dates on which a bar the rule reads, or the entry bar, is missing, or on which the bars of one
    signal computation or of one position carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced
  flatten at F is the backstop.
- **C5 Flat time.** F = 15:08 CT (D9.1; D6 FX row: O = 07:20, C = 14:00, F = 15:08). No new member's
  last fill is later than 15:05 CT. C = 14:00 CT agrees with CME's "Daily Settlement 2:00 p.m. Central
  Time" (R-K3-015, CME FX Markers page, verbatim in the K3 log).
- **C6 Size.** q_c of the exposure's D2 vehicle, at most 1 lot-equivalent (D2 as amended 21:12;
  D9.5).
  - **Lot weights (D9.6):** 6E, 6A, 6B, 6C, 6J, 6S and 6N count 1 each.
  - **M6E, M6A, M6B:** 0.1 each. This is inferred from Topstep's general 10:1 micro rule; no page
    names them (F12.4).
  - **E7:** counted 1 here, as a non-micro. It is named in no Topstep weighting table (F12.4), so E.2
    confirms.
  - So q_c = 1 for a full-size vehicle or E7, and q_c <= 10 for a micro. No member sizes by signal.
- **C7 Ticks and fees.** From reports/stage_e0_liquidity.json (CME contract specifications, fetched
  2026-09-23 20:44-20:46 PDT) and Topstep F3 round turns:

  | Contract | Exposure | Tick | Tick value | Topstep round turn | Lot-equivalent |
  |---|---|---|---|---|---|
  | 6E | EUR | 0.00005 | $6.25 | $4.22 | 1 |
  | E7 | EUR | 0.0001 | $6.25 | $2.72 | 1 (E.2 confirms) |
  | M6E* | EUR | 0.0001 | $1.25 | $1.00 | 0.1 (inferred) |
  | 6A | AUD | 0.00005 | $5.00 | $4.22 | 1 |
  | M6A* | AUD | 0.0001 | $1.00 | $1.00 | 0.1 (inferred) |
  | 6B | GBP | 0.0001 | $6.25 | $4.22 | 1 |
  | M6B | GBP | 0.0001 | $0.625 | $1.00 | 0.1 (inferred) |
  | 6C | CAD | 0.00005 | $5.00 | $4.22 | 1 |
  | 6J | JPY | 0.0000005 | $6.25 | $4.22 | 1 |
  | 6S | CHF | 0.00005 | $6.25 | $4.22 | 1 |
  | 6N | NZD | 0.00005 | $5.00 | $4.22 | 1 |

  These are 2026 specifications. E.2 must confirm that each tick was unchanged over 2019-05..2026-06
  before any bar is read, because CP2's buffer and several ML features are in ticks.
- **C8 Price data.** Databento GLBX.MDP3 ohlcv-1m of the vehicle.
  - **Cost and timing:** paid. The research window is bought in E.1, and the confirmation and
    holdout-2 history of the chosen vehicle in E.2b (D13; K3 quoted $14.24 research, $41.25-49.34
    step 2, $4.18 mbp-1).
  - **History:** the micros were listed on 2009-03-23 (liquidity JSON), so every K3 contract has
    2019-05..2026-06 history. E7's listing date is not in the JSON; E.2 confirms it.
  - **Availability:** a bar is available at its close (C1).
  - **Tick-free signals:** every new-member signal uses a price difference only through its sign, or
    a percent return, so it gives the same decision on any contract of an exposure.
  - **mbp-1** enters only through D8's shared five-date cost sample. No member reads order-book data.
  - **Quotation:** every K3 contract is quoted in U.S. dollars per unit of the foreign currency ("All
    these foreign exchange contracts are denominated in U.S. dollars per unit of the foreign currency",
    P-K3-007-b). A rise in 6J is a fall in USD/JPY.
- **C9 Fix clocks and calendars.** All are external, free, and known before the trade date. No rule
  reads a fix value, a reference rate or any published price.
  - **T_L(d), the WM/Reuters London 4 p.m. fix.**
    - **Definition:** 16:00 Europe/London on the calendar date of d, converted to America/Chicago
      with the IANA tz database.
    - **Conversion rule:** 16:00 London = 10:00 CT, except in the weeks when the US is on daylight
      time and the UK is not. Those run from the second Sunday of March to the day before the last
      Sunday of March, and from the last Sunday of October to the day before the first Sunday of
      November; in them T_L = 11:00 CT.
    - **Computed weekday ranges at 11:00 CT:** 2019-03-11..03-29, 2019-10-28..11-01,
      2020-03-09..03-27, 2020-10-26..10-30, 2021-03-15..03-26, 2021-11-01..11-05, 2022-03-14..03-25,
      2022-10-31..11-04, 2023-03-13..03-24, 2023-10-30..11-03, 2024-03-11..03-29, 2024-10-28..11-01,
      2025-03-10..03-28, 2025-10-27..10-31, 2026-03-09..03-27.
    - **Sources:** "the London fix at 4:00 p.m. local time (or 11:00 a.m. ET)" (P-K3-016-c); "The
      11am spike is likely related to the WM/Reuters spot foreign exchange fixing, which is at 4pm
      London time" (P-K3-032-a).
  - **T_E(d), the ECB reference-rate fix.**
    - **Definition:** 14:15 Europe/Berlin (CET/CEST) on the date of d, converted to CT.
    - **Conversion rule:** 07:15 CT, except in the same mismatch weeks as T_L (EU and UK clocks change
      on the same dates; computed), when it is 08:15 CT.
    - **Sources:** "the 'ECB fix' at 8:15 a.m. ET (2:15 p.m. local time)" (P-K3-016-c). The ECB page
      fetched above says the concertation "normally takes place around 14:10 CET". The source's
      14:15 is used because it is the end of the source's own strategy window (P-K3-016-d).
  - **T_T(d), the Tokyo 9:55 JST fix.**
    - **Definition:** 09:55 Asia/Tokyo on the Tokyo calendar date that carries d's date label.
      Japan has no daylight time.
    - **In CT:** it falls on the previous CT evening, **18:55 CST or 19:55 CDT on calendar day d-1**,
      which is inside trade date d (C3).
    - **Computed examples:** Tokyo 2025-01-10 09:55 = 2025-01-09 18:55 CST; Tokyo 2025-03-10 = 2025-03-09
      19:55 CDT (the US is already on daylight time); Tokyo 2025-07-10 = 2025-07-09 19:55 CDT.
    - **Sources:** "if the switching time is at the moment of the Tokyo fixing (00:55GMT)"
      (P-K3-022-c); "at 9:55 a.m. local time which is 8:55 p.m. ET (or 7:55 p.m. depending on
      daylight saving time (DST))" (P-K3-016-c).
  - **E.2 known-answer tests for the three clocks:**
    - T_L: 2025-03-10 is 11:00; 2025-03-31 is 10:00; 2025-10-27 is 11:00; 2025-11-03 is 10:00;
      2021-11-01..05 are 11:00.
    - T_E: 2025-03-10 is 08:15; 2025-04-01 is 07:15.
    - T_T: for d = 2025-11-04 it is 2025-11-03 18:55 CT.
  - **EC-EW, England-and-Wales bank holidays.** gov.uk JSON (fetched), free, covering 2019-2028. Each
    holiday is announced before its date.
  - **EC-JP, Tokyo business day.**
    - **Definition:** a weekday that is not a national holiday in the CAO CSV (fetched; 1955-2027) and
      is not 31 December, 1 January, 2 January or 3 January.
    - **The year-end rule is a judgment:** the Japanese banks' year-end closure is not in any logged
      passage. E.2 may check it against any free record of which dates carried a Tokyo fix.
  - **EC-TGT, TARGET closing days.** The six "*" days on the ECB working-hours page (fetched). The page
    lists 2026-2028; E.2 reads 2019-2025 from Wayback captures of the same page and logs any
    difference.
  - **EC-NFP and EC-FOMC.**
    - **Sources:** BLS Employment Situation release dates and the Federal Reserve's scheduled FOMC
      meetings, exactly as CatalogWriter-K2 fetched and specified them (reports/stage_e0_catalog_K2.md
      C9).
    - **Times:** 07:30 CT (Topstep F6 "Unemployment Rate | 7:30 AM", which lists 6A, 6B, 6C, 6E, 6J,
      6S, E7, M6A, M6E, 6N) and 13:00 CT (F6 "FOMC Statement | 1:00 PM | All products").
    - **Availability:** both schedules are published before the year or the release.
  - **EC-CAL.** The D10 FX calendar (trade dates, holidays, early halts and closes), built by E.2 from
    CME schedules.
  - **ME(m), month-end.** The last trade date of calendar month m in EC-CAL, known in advance.
    - **Month-end members** (K3-ldnrev-01, K3-mehedge-01) do not trade in month m if ME(m) is excluded
      by C4 or is an EC-EW bank holiday. Whether the WM/R month-end fix flow happens on a London holiday
      is not in the log. The drop removes 2020-08-31 and 2021-05-31 from the confirmation window and
      nothing from the research window (computed).
- **C10 Frequency (arithmetic from calendar counts, no price data).**
  - **Research window** 2025-04-01..2026-06-19:
    - 319 weekdays, about 305 CME trade dates;
    - 14 month-ends;
    - 298 Tokyo business days, 67 of them gotobi or Tokyo month-end days;
    - 314 weekdays that are not fixed TARGET holidays.
  - **Confirmation window** (the earliest S_X) 2019-05-06..2024-02-29:
    - 1,259 weekdays;
    - 58 month-ends, 56 after the EC-EW drop;
    - 1,179 Tokyo business days, 271 of them gotobi or month-end.
  - **All counts are before C4's exclusions.** A member trading on k of about 305 research dates, with
    zeros on the rest (D5), needs a net P&L per event of about (305 / k) x eps_X to average eps_X per
    trade date.
  - **The month-end members** (k about 14) need about 22 x eps_X per event. K3-tkypre-01 (k about 60)
    needs about 5 x.
  - **Likely verdicts:** the month-end members will probably be "inconclusive by design" or "null at
    eps" (D4's power check decides; the lead's 21:52 ruling Q4 keeps such members).
- **C11 Topstep items that do not bind in K3.**
  - **D9.11 volatility caps and D9.12 CPI window:** neither names any FX product (F12.1).
  - **D9.7 price-limit proximity:** no E.0 artifact establishes a CME daily price limit for FX futures.
    E.2's per-product limit tables decide, and if one exists, the harness rule applies. The catalog
    assumes nothing either way.
- **C12 Overnight coverage.**
  - **The problem:** D1(b) measured coverage only in 07:20-14:00 CT. Several members trade outside
    it: 6J at 17:30-01:00 CT, 6E from 00:46 CT.
  - **The check:** D9's member-level coverage check (>= 0.95 in the member's own window, research
    window) is therefore binding for them. E.2 computes it before screening.
  - **Supporting evidence, not a substitute for the check:** the log's only liquidity evidence for
    Asian hours is P-K3-006-a and b (21% of USD/JPY futures ADV and 12% of EUR/USD ADV trade in
    "(00:00 - 09:00a.m. GMT)"; over 180,000 G7 contracts a day in Asian hours).

---

## 1. Members

### K3-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K3. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures and admissible contracts** (each a separate trial): EUR {6E, E7, M6E*}; AUD
  {6A, M6A*}; GBP {6B, M6B}; CAD {6C}; JPY {6J}; CHF {6S}; NZD {6N}. Each is traded only if D2 admits
  the exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log
  A10 and A28), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the trade
    date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the
    signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min
    (fills at the next open). Both signal bars must exist with one instrument_id, else no trade."
  - **K3 log:** K3-010 (Seeck, London-open 30-minute momentum on spot FX and 6J) is this family on a
    K3 product and is recorded as **covered by CP1**. Its London-clock variant is not written (section
    5). D.1 A10 (Baltussen et al.) reappeared in the K3 search; its FX results are [unverified from
    K3's side].
- **Instantiated with the D6 FX row (O = 07:20, C = 14:00, F = 15:08):**
  - **Signal:** close of the bar at 07:49 minus the open of the trade date's first bar (the 17:00 CT
    bar of d-1, C3).
  - **Entry:** market intent on the bar at 13:29, filling at the 13:30 open.
  - **Exit:** market intent on the first bar at or after 13:58, filling nominally at the 13:59 open.
  - **Holding horizon:** 29 minutes. **Session window:** 13:30-13:59 CT. Flat well before F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid, with history
  2019-05..2026-06. The latest signal input, the 07:49 bar, is available at 07:50 CT; the decision is
  at 13:29.
- **Order type:** market. **Sizing:** q_c of the D2 vehicle (C6).
- **Parameters:** O+29 = 07:49, C-31 = 13:29, C-2 = 13:58 (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29 minutes.
  Floor: at most 20 entries a day, ok; 2-minute minimum hold, ok; 10-minute mean hold, ok.
- **Falsification:** the standard condition only (a port). UCB95 of the member's mean net daily P&L
  per contract below eps_X, at >= 80% achieved null power on the confirmation window, counts against
  it.
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market.
  3. D9.4: one trade a day; no stops, brackets or passive fills.
  4. *: M6E (EUR) and M6A (AUD) are starred with the restriction unresolved. This applies only if D2
     picks them.
  5. News: 1 lot-equivalent, half the 2-lot maximum. On FOMC days the entry fills 30 minutes after the
     13:00 statement. That is exactly at the end of D8's 30-minute event-window cost; section 7, item 9.
  6. D9.5a: no fill in [07:30, 07:32) or [13:00, 13:02).
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of each admitted K3 vehicle, research window 2025-04-01..2026-06-19 and
  confirmation S_X..2024-02-29 (D4). No external data.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K3-cp2-01 (core port CP2, opening-range breakout)
- **Cluster** K3. **Products read:** own vehicle.
- **Exposures:** EUR, AUD, GBP, CAD, JPY, CHF, NZD, one trial each, with the admissible contracts of
  K3-cp1-01. Each is traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py, hold_minutes =
  75), as fixed in D6 row CP2 with the 21:12 amendment and the 21:52 buffer ruling.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first bar
    opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market
    intent in the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes
    after the fill, or the engine's forced flatten at F if earlier."
  - **D6 on the buffer:** "'4 ticks of P' in CP2 means 4 minimum price increments of the exposure's
    most active contract (D1 table), in price units, fixed whatever vehicle D2 chooses".
  - **K3 log:** it holds no opening-range source on FX futures.
- **Instantiated:**
  - **Opening range:** the bars opening in [07:20, 07:35).
  - **Eligible bars:** those opening in [07:35, 14:00). No entry from 14:00 CT on.
  - **Buffer, 4 ticks of the exposure's most active contract** (D1 table; ticks from C7):

    | Exposure | Most active | Buffer (price units) | In the other admissible contracts' ticks |
    |---|---|---|---|
    | EUR | 6E | 0.00020 | E7 2 ticks; M6E 2 ticks |
    | AUD | 6A | 0.00020 | M6A 2 ticks |
    | GBP | 6B | 0.0004 | M6B 4 ticks |
    | CAD | 6C | 0.00020 | none |
    | JPY | 6J | 0.0000020 | none |
    | CHF | 6S | 0.00020 | none |
    | NZD | 6N | 0.00020 | none |

  - **Entry:** the first eligible bar whose close is >= OR_high + buffer buys; one whose close is
    <= OR_low - buffer sells. One entry per trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it (bars since entry), or the
    engine's forced flatten at F. An entry filled after 13:53 is cut short by F.
  - **Holding horizon:** 75 minutes or less. **Session window:** 07:36 to F.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is known
  at 07:35 CT.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** OR 15 minutes, buffer 4 ticks of the most active contract, hold 75 minutes (D6, a
  literal port). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held up to 75 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: engine flatten at the latest.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. *: the M6E and M6A flag, as in CP1.
  5. News: 1 lot-equivalent.
     - On BLS days the opening range contains the 07:30 CT release (section 7, item 9).
     - Entries filled in 07:36-08:00 on those days pay D8's event-window cost.
  6. D9.5a: the earliest possible fill is 07:36, outside [07:30, 07:32).
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K3-cp3-01 (core port CP3, prior-close location)
- **Cluster** K3. **Products read:** own vehicle.
- **Exposures:** EUR, AUD, GBP, CAD, JPY, CHF, NZD. Each is traded only if D2 admits the exposure.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L over
    [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family H.
    CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market intent
    on the O bar of day d. Exit: first bar at or after C-2 min."
- **Instantiated:**
  - **Daily bar:** O_d = open of the 07:20 bar. H and L are taken over the bars opening in
    [07:20, 14:00). C_d = close of the 13:59 bar.
  - **Complete day** (Family H): the 07:20 and 13:59 bars exist, the date is not an early halt, and
    every bar in [07:20, 14:00) carries one instrument_id.
  - **Instrument guard:** d-1's daily bar carries the instrument_id of day d's 07:20 bar.
  - **CLV:** computed in ticks with Range[d-1] > 0. CLV >= 0.8 buys and CLV <= 0.2 sells (non-strict,
    as H6).
  - **Entry:** market intent on the 07:20 bar of d, filling at the 07:21 open.
  - **Exit:** first bar at or after 13:58, filling nominally at the 13:59 open.
  - **Holding horizon:** about 398 minutes. **Session window:** 07:21-13:59 CT.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's bar
  is complete at 14:00 CT on d-1.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 398 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 13:59.
  2. Order type: market.
  3. D9.4: ok.
  4. *: the M6E and M6A flag.
  5. News: it holds through the 07:30 BLS release, the London fix and the 13:00 FOMC statement at
     1 lot-equivalent, which is not the full maximum (D9.5).
  6. D9.5a: the 07:21 entry is 9 minutes before the release; no fill in a guard window.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the admitted vehicles, over the research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K3-ldnrev-01 (month-end London 4 p.m. fix: contrarian trade after the fixing window)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-05: the signal is the 10-minute pre-fix move, the close of the bar at T_L-1 minus the close of the bar at T_L-11, as NBER w23327 footnote 9 measures it ("the first-recorded price during 15:49:30 to 15:59:30" to "16:00:00"); the 15-minute window written below is superseded. The entry at T_L+5 stays as a stated judgment.]
- **Cluster** K3. **Products read:** the traded vehicle; EC-CAL, EC-EW; the T_L clock (C9).
- **Traded exposures:** EUR {6E, E7, M6E*}, JPY {6J}, CHF {6S}. Each is traded only if D2 admits the
  exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** rates that trend into the London 4 p.m. fix partly reverse after it, more at
    month-end: "the rates tend to drop after rising toward the fix, and tend to rise after dropping
    towards the fix. The larger reversal is found at the end-of-month trading days than intra-month
    days" (K3-002 P-K3-002-b).
  - **The trade is the source's own:** "taking a long (short) position after the end of fixing if the
    rates fell (rose) towards the fix" (P-K3-002-e); likewise "a simple end-of-month trading strategy
    of taking a long (short) position at 4:00 pm if prices fell (rose) towards the Fix" (K3-003
    P-K3-003-b).
  - **Post-reform evidence for this member's window:** "After the reform, the end-of-month
    profitability is still available ... While the profitability of holding one minute is no longer
    available, the profitability of 15 minutes holding becomes even stronger than before. In the
    intra-month sample, there are no profitability" (P-K3-002-f).
  - **Post-reform month-end cells, 15/5/1-minute holds, bp after spread** (P-K3-002-g):
    - EUR/USD "1.21 1.32 -1.02";
    - USD/JPY "2.39 2.27 -0.511";
    - USD/CHF "6.19 -0.0809 -1.45".
  - **Futures support:** futures positions built before the fix "are also reversed" (K3-018
    P-K3-018-a (6), CME 6B, 6A, 6N, pre-reform). The reversion is "two times larger on end-of-month"
    (K3-001 P-K3-001-c; the signs there are [unverified] in extraction, and this member's direction
    rests on the verbal statements of K3-002 and K3-003).
  - **Evidence against, stated both ways (rule 1):**
    - The regulator's data show the reversal gone after 2015 on all days pooled: "short-term price
      reversals in prices around the fix decrease steadily throughout our sample period, and disappear
      from 2015 onwards" (K3-019 P-K3-019-a; P-K3-019-b "from 2015 onwards the correlations are
      generally insignificant"). K3-019 pools all days by quarter and has a six-month post-reform
      sample. K3-002 splits out month-end and has about 16 post-reform months. So the two conflict on
      different day sets.
    - The pre-registered re-test on 2015-2023 (K3-020) is logged only as a protocol plus a Stage 2
      abstract, "the current 5-min window remains broadly effective" (P-K3-020-c). Its reversal
      result is [unverified].
    - For JPY, K3-003 (2004-2013) finds "the returns are positive for at least one horizon in all but
      the JPY/USD and USD/GBP" (P-K3-003-e), against K3-002's positive post-reform USD/JPY cell.
  - **Classification:** port of D.1 families C (short-horizon reversal) and E (month-end) on a fix
    event. D6 ports neither, so this is a cluster member (new to Stage E).
- **Exposure choice:** the three exposures whose post-reform month-end 15-minute cells are logged
  (P-K3-002-g). GBP is left out: K3-003 reports USD/GBP negative at every horizon, and K3-016's CME
  London trade on 6B is negative (P-K3-016-f). AUD and CAD are in K3-002's pair list, but their
  post-reform cells are not in the log (section 3).
- **Event set:** ME(m) for each month m, with C4 and the EC-EW drop (C9).
- **Signal:** M = close of the vehicle's bar at T_L - 1 minus close of its bar at T_L - 16. That is
  the move over the 15 minutes 15:45 to 16:00 London, bar closes. Both bars must exist with one
  instrument_id. M = 0 means no trade.
- **Entry rule:** market intent on the bar at T_L + 4, filling at the open of the bar at T_L + 5
  (16:05 London; 10:05 CT, or 11:05 CT in the C9 mismatch weeks). BUY if M < 0; SELL if M > 0.
  - This is contrarian in the futures' own quote, which is the source's rule for every pair: a
    reversal is unchanged by inverting the quote. For example, USD/JPY falling into the fix is 6J
    rising, and the source's long USD/JPY is a SELL of 6J.
- **Exit rule:** market intent on the bar at T_L + 19, filling at the open of T_L + 20 (10:20 CT
  standard).
- **Holding horizon:** 15 minutes. **Session window:** 10:05-10:20 CT (11:05-11:20 in the mismatch
  weeks). Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m close, open and instrument_id (C8). Paid, 2019-05..2026-06. The signal is
    available at T_L (the close of the bar at T_L - 1), 5 minutes before the entry fill.
  - EC-CAL and EC-EW. Free, 2019-2026, known in advance (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Pre-fix window, 15 minutes:** a judgment. The log does not give K3-002's window length. The
    choice follows the 15-minute pre-fix windows of the post-reform efficiency tests ("the 15 minutes
    before the fix", P-K3-019-b and P-K3-020-a) and the 15:45 start of the post-reform fix trend
    (P-K3-017-b).
  - **Entry at T_L + 5:** a judgment. After the reform "the fixing time window was widened from 1
    minute to 5 minutes" (P-K3-002-d), and the log does not say how the window is centred. An entry at
    16:05 London is after that window under either centring, and K3-002 trades "after the end of
    fixing".
  - **Hold 15 minutes:** P-K3-002-f and P-K3-002-g.
  - **Grid:** none.
- **Expected entries and hold:** one per eligible month-end: about 14 in the research window and 56
  in the confirmation window, before C4. Held 15 minutes. Floor ok: the 2-minute minimum and the
  10-minute mean both hold. Frequency: C10, about 22 x eps_X per event.
- **Falsification:**
  - The standard condition (UCB95 of mean net daily P&L per contract below eps_X at >= 80% achieved
    null power on the confirmation window counts against it).
  - **Sign check (reported beside the verdict, not a separate test):** the mean over events of
    direction x (open at T_L + 20 - open at T_L + 5), in ticks, is positive. A non-positive
    confirmation-window mean counts against the mechanism.
- **Topstep check:**
  1. Flat by F: latest fill 11:20 CT.
  2. Order type: market.
  3. D9.4: one trade a month.
     - Both fills are outside the fix minute and the post-reform fixing window.
     - The fix minute is the day's peak-volume minute, "over 10% of the platform's daily trading
       volume" on some days (P-K3-013-d), not a gapped market.
  4. *: M6E flag (EUR only, if D2 picks M6E).
  5. News: 1 lot-equivalent. No Topstep-listed release falls in the window.
  6. D9.5a: not triggered (no fill at 07:30 or 13:00).
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the EUR, JPY and CHF vehicles (research and confirmation windows);
  external EC-CAL and EC-EW.
- **Trials in N:** 1 per admitted exposure (at most 3).

### K3-ldnmom-01 (post-reform front-running into the London 4 p.m. fix)
- **Cluster** K3. **Products read:** the traded vehicle; EC-CAL, EC-EW; the T_L clock.
- **Traded exposures:** EUR {6E, E7, M6E*}, JPY {6J}. [Narrowed by the lead, 01:40 PDT 2026-09-24, answering
  this writer's question 3: the mechanism rests on a flow model with no profitability test, so the trial
  count is cut from 6 to 2, keeping the two most liquid K3 exposures by 2026 Jan-Aug ADV (D1 table). GBP, CHF,
  CAD and NZD are removed; the rest of the entry is unchanged.]
  Each is traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** after the 2015 reforms, fix dealers execute client fix orders with algorithms
    from about 3:45 p.m. London. So "non-dealers can now glean information about fix orders from the
    price trend immediately following 3:45 ... front-run the rest of the market by opening a
    speculative position immediately after 3:45 and then liquidate that position partly before and
    partly after the fix" (K3-017 P-K3-017-b).
  - **The model:** "Fix prices will be unusually volatile without collusion ... dealers front-run each
    other" (P-K3-017-a).
  - **Supporting descriptive evidence:** the pre-fix trend is visible in the average price path
    (P-K3-002-b, "rising toward the fix"). The minute before the fix "shows a significant increase in
    volatility compared to the minutes in the ~50-min. beforehand" (K3-021 P-K3-021-a). The fix raises
    the probability of the day's extreme (P-K3-021-c).
  - **Evidence against, stated:**
    - The source tests the convexity of the pre-fix path, not profitability. Its post-reform claim
      rests on other papers (the K3-017 block, "Quality tells").
    - After 2015 "dealer banks began doing relatively less trading before the fix and more during the
      fix" (P-K3-019-a), which weakens pre-fix pressure.
    - The Norges Bank study found no significant price changes around the WM fix in its currencies
      (K3-004 P-K3-004-d).
    - Futures positions built before the fix reverse afterwards (P-K3-018-a (6)). That works against
      the post-fix part of this member's hold.
  - **Classification:** port of D.1 family C (short-horizon momentum) at the fix clock. D6 does not
    port it, so it is a cluster member (new to Stage E).
- **Exposure choice:** the source's currencies that are K3 exposures, "EUR, JPY, GBP, CHF, CAD, NZD,
  and DKK" (P-K3-017-c). AUD is not in the source's sample.
- **Event set:** every trade date d with C4, excluding EC-EW bank holidays (C9: whether a London fix
  flow exists on a London holiday is not in the log).
- **Signal:** S = close of the vehicle's bar at T_L - 13 minus open of its bar at T_L - 15. That is the
  trend over the three bars opening 15:45, 15:46 and 15:47 London, "immediately following 3:45". Both
  bars must exist with one instrument_id. S = 0 means no trade.
- **Entry rule:** market intent on the bar at T_L - 13, filling at the open of the bar at T_L - 12
  (15:48 London; 09:48 CT standard). BUY if S > 0; SELL if S < 0.
- **Exit rule:** market intent on the bar at T_L + 4, filling at the open of the bar at T_L + 5 (16:05
  London; 10:05 CT standard).
- **Holding horizon:** 17 minutes. **Session window:** 09:48-10:05 CT (10:48-11:05 in the mismatch
  weeks). Flat by F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). The signal is available
  at T_L - 12. EC-CAL and EC-EW (C9).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Signal window of 3 minutes starting at 15:45:** a judgment. The source says only "immediately
    following 3:45". Three bars is the shortest window that measures a trend rather than one bar's
    noise, while still leaving most of the run-up to the fix to be traded.
  - **Exit at T_L + 5:** a judgment within "partly before and partly after the fix". A single-lot
    position cannot be split, so it is held through the fix to the end of the post-reform fixing
    window under either centring (P-K3-002-d).
  - **Why not exit before the fix:** an exit before the fix (at T_L - 3) would make the hold 9
    minutes, below D9.3(c)'s 10-minute mean.
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per trade date (about 290 research dates after C4 and the
  12 EC-EW weekday holidays), held 17 minutes. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean of direction x (open at T_L - 3 - open at T_L - 12), in
    ticks, is positive. That is the pre-fix part, which the mechanism predicts. The post-fix part is
    reported beside it.
- **Topstep check:**
  1. Flat by F: latest fill 11:05 CT.
  2. Order type: market.
  3. D9.4: one trade a day, held 17 minutes. No fill in the fix minute (16:00-16:01 London).
  4. *: M6E flag (EUR).
  5. News: 1 lot-equivalent. No Topstep-listed release falls in the window.
  6. D9.5a: not triggered.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the six vehicles (research and confirmation windows); external EC-CAL
  and EC-EW.
- **Trials in N:** 1 per admitted exposure (at most 2, after the lead's narrowing).

### K3-mehedge-01 (month-end equity-hedge rebalancing in the hour before the London fix)
- **Cluster** K3. **Products read:** the traded vehicle; one non-CME equity index per exposure (a
  signal instrument, which belongs to the traded product's cluster: partition section 1 and the
  lead's 21:52 ruling, "Melvin-Prins stays in K3"); EC-CAL, EC-EW; the T_L clock.
- **Traded exposures:** EUR {6E, E7, M6E*} with the EURO STOXX 50 price index; JPY {6J} with the
  Nikkei 225. Each is traded only if D2 admits the exposure **and** E.2 obtains the index's free daily
  history (below). **Vehicle:** D2 (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** international equity managers resize their currency hedges at the month-end
    London fix. Where the local equity market has risen over the month, foreign holders own more of
    that currency and sell it into the fix. "Equity market appreciation over the month predicts
    currency depreciation before the end-of-month fix" (K3-001 P-K3-001-a).
  - **Magnitude:** "a 10% equity appreciation leads to 14 basis points of currency depreciation. Though
    significant, this seems like quite a small effect" (P-K3-001-b).
  - **Flows:** month-end flows are 1.39 to 2.36 times non-month-end flows, "significantly greater than
    1" in every country (P-K3-001-e). Month-end fix flow can reach CME FX futures through FX BTIC
    (R-K3-014, verbatim in the log).
  - **Sample:** 2004-2012 (P-K3-001-d). The authors are BlackRock practitioners. The regression R2 is
    low (the K3-001 block).
  - **Classification:** new to the program (the partition's K3 seed); a port of D.1 family E (month
    end) with an external signal.
- **Exposure choice (rule 3):**
  - **The source's signal:** "Datastream Total Market indices" (the K3-001 block), which are
    proprietary.
  - **The obtainable proxy:** each currency area's benchmark price index, in local currency, from its
    publisher. Only EUR and JPY have a named publisher history candidate:
    - STOXX Ltd.'s daily history file for the EURO STOXX 50 (h_3msx5e.txt);
    - Nikkei Inc.'s Nikkei 225, which FRED also redistributes as series NIKKEI225.
  - **Not confirmed:** neither was confirmed from this machine (header: certificate error, a Wayback
    capture exists; FRED unreachable; Nikkei 403).
  - **Other exposures:** GBP, AUD, CAD, CHF and NZD are in the source's sample, but no free historical
    source was named for their indices. They are excluded under rule 3 (section 2, X-13).
  - **Judgment on the index:** the broad Datastream index is replaced by the publisher's blue-chip
    index. This is a judgment: the blue-chip index is what the publisher releases free.
- **Event set:** ME(m) with C4 and the EC-EW drop (C9).
- **Signal:**
  - **Formula:** R_eq(m) = ln(P_a / P_b), where P_a is the index's last official daily close on a local
    date strictly before ME(m)'s calendar date, and P_b is its last official daily close in calendar
    month m-1.
  - **Timing:** in the normal case P_a is the close of the local second-last trading day, matching the
    source's "equity return over the month up to the second-last day" (K3-001 block). The Tokyo close
    on ME's own date label is excluded even though it precedes the entry, to match the source.
  - **No trade** if R_eq(m) = 0 or either close is missing.
- **Entry rule:** market intent on the bar at T_L - 61, filling at the open of the bar at T_L - 60
  (15:00 London; 09:00 CT standard). SELL if R_eq(m) > 0 (the currency is predicted to depreciate);
  BUY if R_eq(m) < 0.
- **Exit rule:** market intent on the bar at T_L - 4, filling at the open of the bar at T_L - 3 (15:57
  London; 09:57 CT standard).
- **Holding horizon:** 57 minutes. **Session window:** 09:00-09:57 CT (10:00-10:57 in the mismatch
  weeks). Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m open and instrument_id (C8).
  - EURO STOXX 50 official daily close: source STOXX Ltd. history file. Free per the publisher's
    listing, but its 2019-04..2026-06 availability is **[unverified in E.0]**. Available at the index's
    official close on each date (STOXX closes during European hours, before 12:00 CT), at least 20
    hours before the entry.
  - Nikkei 225 official daily close: source Nikkei Inc. or FRED NIKKEI225. Free, availability
    **[unverified in E.0]**. Available at the Tokyo close on each Tokyo date, before 02:00 CT on the
    same date label, at least one day before the entry.
  - EC-CAL and EC-EW (C9).
  - **E.2 rule:** if an index's free daily history from 2019-04 cannot be obtained before any K3 bar is
    read, that exposure's trial is dropped and logged, never substituted.
- **Order type:** market. **Sizing:** q_c. The source's effect is linear in R_eq, but D2 forbids
  signal-scaled size above q_c, so the size is fixed.
- **Parameters:**
  - **Window, the hour before the fix:** the source says "in the hour leading up to the end of month
    fix" (P-K3-001-b).
  - **How "15:00-16:00 GMT" is read:** as London clock time. The passage defines the window as the
    hour before the 4 p.m. London fix, and a literal UTC reading would put it after the fix in British
    Summer Time months.
  - **Exit 3 minutes early:** a judgment, so that the position is flat before the post-reform 5-minute
    fixing window under either centring (P-K3-002-d).
  - **Grid:** none.
- **Expected entries and hold:** about 14 research and 56 confirmation events (C10), held 57 minutes.
  Floor ok. About 22 x eps_X per event is needed (C10).
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the correlation between R_eq(m) and the vehicle's move from the
    T_L - 60 open to the T_L - 3 open is negative.
- **Topstep check:**
  1. Flat by F: latest fill 10:57 CT.
  2. Order type: market.
  3. D9.4: one trade a month, no stops.
  4. *: M6E flag (EUR).
  5. News: 1 lot-equivalent. The window can contain a 09:00 CT US release that is not in Topstep's
     table, which is allowed at this size.
  6. D9.5a: not triggered.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the EUR and JPY vehicles; external index closes from 2019-04 (the
  confirmation window's first month needs April 2019's last close); EC-CAL and EC-EW.
- **Trials in N:** 1 per admitted exposure with an obtained index (at most 2).

### K3-ecbfix-01 (euro: dollar strength into the ECB fix, dollar weakness after it)
- **Cluster** K3. **Products read:** the EUR vehicle; EC-CAL, EC-TGT; the T_E clock.
- **Traded exposure:** EUR {6E, E7, M6E*}, traded only if D2 admits the exposure. **Vehicle:** D2
  (chosen in E.2).
- **Mechanism:**
  - **What is claimed:** dealers meet an unconditional demand for dollars at the major fixes, so
    "intraday currency returns display prolonged reversals around the major benchmark fixings,
    characterised by an appreciation of the U.S. dollar pre-fixing and a depreciation thereafter",
    present "every day of the week, month of the year, and during each of the twenty years" (K3-016
    P-K3-016-a).
  - **The source's trade:** "For the ECB fix we go long the dollar between 2:00 a.m. and 8:15 a.m. and
    short the U.S. dollar between 8:15 a.m. and 5:00 p.m." (ET; P-K3-016-d).
  - **On CME futures with full bid-ask costs, 2009-2018:** "returns for trading the euro are extremely
    large and generate a Sharpe ratio for the ECB fix trade of 0.61" (P-K3-016-e).
  - **Table 8 CME row** (P-K3-016-f): pre-E 5.53% a year (Sharpe 0.99), post-E 0.58% (0.08), pre/post-E
    6.11% (0.65). The text's 0.61 and the table's 0.65 disagree; the log records it.
  - **Corroboration, the same direction in overlapping hours:**
    - Breedon and Ranaldo: currencies "depreciate during local trading hours". For EUR/USD the
      strategy survives costs, "Sharpe Ratios of 1.3 and 0.9 respectively for the morning short and
      afternoon long" (K3-023 P-K3-023-a, b). The between-session difference is stable year to year
      (P-K3-023-c).
    - Ranaldo: "long position on US dollars is from 8:00 to noon" against the euro, short "from 16:00
      to 20:00 for the euro" (GMT; K3-024 P-K3-024-d). The EUR/USD break-even cost is 4 pips
      (P-K3-024-c).
    - On IMM futures (pit era, abstract only), foreign currencies strengthen during the US day
      (K3-025 P-K3-025-a).
    - Activity rises ahead of the ECB fix (K3-004 P-K3-004-b).
  - **Against:** with full spread costs most spot windows turn negative, and the authors say "it is
    not obvious that this can be exploited by the average trader" (P-K3-016-g, h). Only the CME euro
    cell is positive.
  - **Classification:** new to the program; a port of D.1 family A (session clock) anchored to a fix.
    D6 does not port family A because a clock drift needs a documented drift on the product. This one
    is documented on 6E itself.
- **Exposure choice:** EUR only. It is the only exposure the source's CME test supports ("returns and
  Sharpe ratios are negative for the pound and the yen", P-K3-016-e), and the only pair that survives
  costs in K3-023 (P-K3-023-b).
- **Event set:** every trade date d with C4 that is not an EC-TGT closing day (no ECB fix: "except on
  TARGET closing days", ECB page, header).
- **Entry and exit rules (two legs, sequential, at most one position):**
  - **Leg 1 (pre-fix, SELL):** market intent on the bar at 00:59 CT, filling at the 01:00 CT open.
    The source's 2:00 a.m. ET is 01:00 CT all year, because ET and CT change clocks together. Exit:
    market intent on the bar at T_E - 1, filling at the T_E open (07:15 CT, or 08:15 CT in the C9
    mismatch weeks).
  - **Leg 2 (post-fix, BUY):** market intent on the bar at T_E, filling at the T_E + 1 open. Exit:
    market intent on the bar at 15:04 CT, filling at the 15:05 open. The source's 5:00 p.m. ET = 16:00
    CT is later than F, so the leg is truncated to 15:05 (as the K3-016 block notes).
- **Holding horizon:** leg 1 375 minutes (435 in the mismatch weeks); leg 2 469 minutes (409).
  **Session window:** 01:00-15:05 CT. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open and instrument_id (C8); EC-CAL and EC-TGT (known in
  advance).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Leg 1:** 01:00 CT to T_E (P-K3-016-d). **Leg 2:** T_E to 15:05 CT (P-K3-016-d, truncated by F).
  - **The one-minute gap at the fix:** a judgment. The reversal is written as exit then re-entry, so
    the position never exceeds q_c.
  - **Grid:** none.
- **Expected entries and hold:** 2 entries per eligible trade date (about 300 research dates before
  C4), each held hours. Floor ok: 2 <= 20 entries a day, and every hold exceeds 10 minutes.
- **Falsification:**
  - The standard condition.
  - **Sign checks (reported per leg):** leg 1's mean gross move, SELL-signed, is positive, and so is
    leg 2's, BUY-signed. The source predicts both. A leg with a non-positive confirmation mean counts
    against that leg's half of the mechanism.
- **Topstep check:**
  1. Flat by F: last fill 15:05.
  2. Order type: market.
  3. D9.4: two trades a day, no stops. The 01:00 entry is not at a session reopen.
  4. *: M6E flag.
  5. News: leg 2 holds through the 07:30 BLS release (or leg 1 does, in the mismatch weeks) and the
     13:00 FOMC statement at 1 lot-equivalent (F6.3, D9.5).
  6. D9.5a: no fill in [07:30, 07:32) or [13:00, 13:02). The leg-2 fill at 08:16 in a mismatch week
     is 46 minutes after 07:30, outside D8's 30-minute event-window cost.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the EUR vehicle 01:00-15:05 CT (research and confirmation windows; the
  C12 coverage check applies to 01:00-07:20); external EC-CAL and EC-TGT.
- **Trials in N:** 1.

### K3-tkypre-01 (gotobi days: dollar demand into the Tokyo 9:55 fix)
- **Cluster** K3. **Products read:** the JPY vehicle; EC-CAL, EC-JP; the T_T clock.
- **Traded exposure:** JPY {6J}, traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in
  E.2; 6J is the only admissible contract).
- **Mechanism:**
  - **What is claimed:** at the Tokyo fix, importers' dollar purchases exceed exporters' sales,
    predictably. "It is commonly known that the USD tends to appreciate vis-à-vis the yen around the
    fixing time. This situation is more evident when large amounts of payments are due, typically on
    the days of the 5th, 10th, 15th, 20th, 25th, and 30th ... as well as the end-of-month trading day"
    (K3-022 P-K3-022-b).
  - **Calendar strength:** "the return becomes particularly high at 5th and 10th days (except for the
    days close to the end of month), and the 31st day of month or the end of month" (P-K3-022-d).
  - **Morning path:** "the USD/JPY rate tends to rise toward 9:55 every morning in the Gotobi days"
    (K3-005 P-K3-005-a).
  - **K3-005's pre-fix leg** (long USD/JPY, 3:00 to 9:55 JST, 2018-2020): profit factor 1.46 on gotobi
    days against 0.51 on other days, without the moving-average filter (P-K3-005-c).
  - **Against:**
    - K3-005 is a 4-page paper with three in-sample years, and an author works at an FX broker (the
      K3-005 block).
    - K3-022's own trade earns 1.8 bp, "slightly above the transaction cost from the bid-ask spread"
      (P-K3-022-c).
    - K3-016's unconditional (every-day) pre-Tokyo long-dollar trade on CME 6J loses after full
      spread, "-11.23" % a year (P-K3-016-f). That is evidence against the all-days version; the
      gotobi-conditioned version is not tested there.
  - **Classification:** new to the program; a port of D.1 families A (clock) and E (calendar).
- **Event set:** trade dates d such that d, as a Tokyo date, is an EC-JP Tokyo business day whose day
  of month is 5, 10, 15, 20, 25 or 30, or the last EC-JP business day of its calendar month. C4
  applies.
  - **No shift rule:** a nominal gotobi date that is not a Tokyo business day is not moved to another
    day. The log states no shift rule (P-K3-005-a: "divisible by five"), so only nominal dates are
    traded; this is a judgment.
- **Entry rule:** SELL (a rise in USD/JPY is a fall in 6J, C8). Market intent on the bar at 17:29 CT
  on calendar day d-1, filling at the 17:30 CT open, which is 08:30 JST under CST and 07:30 JST under
  CDT.
- **Exit rule:** market intent on the bar at T_T - 1, filling at the open of the bar at T_T (09:55:00
  JST: 18:55 CST or 19:55 CDT on d-1). That is the source's exit time: K3-005 exits at 9:55, and
  K3-022 switches "at the moment of the Tokyo fixing".
- **Holding horizon:** 85 minutes (CST) or 145 minutes (CDT). **Session window:** 17:30-19:55 CT on
  d-1, inside trade date d (C3). Flat by F.
- **Data fields read:** vehicle ohlcv-1m open and instrument_id (C8); EC-CAL and EC-JP (C9; known years
  ahead).
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Gotobi set:** P-K3-022-b and P-K3-022-d.
  - **Exit at T_T:** P-K3-005-b and P-K3-022-c.
  - **Entry at 17:30 CT:** the source's 3:00 JST entry (P-K3-005 block) is 18:00 UTC, which is 12:00
    CST or 13:00 CDT on calendar day d-1. That falls in trade date d-1's day session, so the position
    would be held across Topstep's 15:10 CT close; it is infeasible (partition rule 8).
    - The earliest feasible entry is the 17:00 CT reopen. Thirty minutes are added so that the entry
      is not a fill at the session reopen, the D9.4 "gapped markets" case.
    - This is a judgment: the log does not locate the drift within the morning.
  - **Grid:** none.
- **Expected entries and hold:** about 67 research and 271 confirmation gotobi or month-end Tokyo
  business days, before C4 and CME closures (C10). Held 85 or 145 minutes. Floor ok. About 5 x eps_X
  per event is needed (C10).
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean gross move of 6J from the 17:30 open to the T_T open on event
    days is negative.
  - **Reported beside it:** the same statistic on non-gotobi Tokyo business days. The mechanism
    predicts it is closer to zero (P-K3-005-c's gotobi/non-gotobi contrast).
- **Topstep check:**
  1. Flat by F: latest fill 19:55 CT on d-1.
  2. Order type: market.
  3. D9.4: one trade per event, entered 30 minutes after the reopen, not in a gap. The exit is at the
     fix minute's open, and the fix is a scheduled benchmark, not a release.
  4. *: none (6J is unstarred).
  5. News: 1 lot-equivalent; no Topstep-listed release at 17:30-19:55 CT.
  6. D9.5a: not triggered.
  7. Position limit: 1 contract.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the JPY vehicle in 17:00-20:00 CT (research and confirmation windows;
  the C12 coverage check applies); external EC-CAL and EC-JP.
- **Trials in N:** 1.

### K3-tkypost-01 (dollar weakness after the Tokyo fix, every Tokyo business day)
- **Cluster** K3. **Products read:** the JPY vehicle; EC-CAL, EC-JP; the T_T clock.
- **Traded exposure:** JPY {6J}, traded only if D2 admits the exposure. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:**
  - **What is claimed:** after the Tokyo fix the dollar depreciates: "Immediately after the Tokyo fix
    the price path of the DOL reverses, depreciating by ~5.5% per annum (2.2 bps per day) with a
    t-statistic of ~9.2" (K3-016 P-K3-016-b, spot dollar factor).
  - **The source's window:** "short dollar positions between 8:55 p.m. and 2:00 a.m." (ET;
    P-K3-016-d).
  - **On CME 6J with full spread, 2009-2018:** the post-Tokyo leg earns 2.41% a year, Sharpe 0.52.
    It is the only positive Tokyo cell; pre-T is -11.23 and pre/post-T -8.82 (P-K3-016-f).
  - **Corroboration:** K3-005's second leg sells USD/JPY "just after 9:55 and closing its position at
    12:00" (P-K3-005-b). Its profit factor 2.09 is conditional on an ex-post classification (a
    look-ahead flag; see X-02), so it is not used as evidence of size.
  - **Against:** K3-022 finds the London-style reversal absent at Tokyo: "While return reversals are
    reported at the London fixing ..., they are not found at the Tokyo fixing (Table 4)" (P-K3-022-c).
    That test is a reversal correlation, whereas this member is an unconditional post-fix drift, but
    the two findings pull in opposite directions.
  - **Classification:** new to the program; a port of D.1 family A anchored to a fix.
- **Event set:** every trade date d such that d, as a Tokyo date, is an EC-JP Tokyo business day. C4
  applies.
- **Entry rule:** BUY (dollar weakness is a rise in 6J). Market intent on the bar at T_T, filling at
  the open of the bar at T_T + 1 (09:56 JST: 18:56 CST or 19:56 CDT on d-1).
- **Exit rule:** market intent on the bar at 00:59 CT on d, filling at the 01:00 CT open. The source's
  2:00 a.m. ET is 01:00 CT all year.
- **Holding horizon:** 364 minutes (CST) or 304 minutes (CDT). **Session window:** 18:56 on d-1 to
  01:00 CT on d, inside trade date d. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open and instrument_id (C8); EC-CAL, EC-JP.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:**
  - **Start after the fix minute; end at 01:00 CT:** P-K3-016-d.
  - **Anchoring:** the source's windows are stated in ET for the daylight-time case ("8:55 p.m. ET (or
    7:55 p.m. depending on ... DST)", P-K3-016-c). This member anchors the start to the actual fix on
    every date (C9), a judgment in line with the fix mechanism.
  - **Grid:** none.
- **Expected entries and hold:** about 298 research and 1,179 confirmation Tokyo business days before
  C4 and CME closures, held 5-6 hours. Floor ok.
- **Falsification:**
  - The standard condition.
  - **Sign check (reported):** the mean gross move of 6J from the T_T + 1 open to the 01:00 open is
    positive.
- **Topstep check:**
  1. Flat by F: last fill 01:00 CT.
  2. Order type: market.
  3. D9.4: one trade a day; entered one minute after the fix minute, not at a reopen.
  4. *: none.
  5. News: 1 lot-equivalent. Asian-hours releases are not in Topstep's table.
  6. D9.5a: not triggered.
  7. Position limit: 1 contract.
  8. Price limit: C11.
- **Data needed:** ohlcv-1m of the JPY vehicle 18:55-01:00 CT (research and confirmation windows; the
  C12 coverage check applies); external EC-CAL, EC-JP.
- **Trials in N:** 1.

### K3-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: fallback order declared now (D1 ADV order): EUR, JPY, AUD, GBP, CAD, NZD, CHF; if none is admitted, no ML member. Features unchanged.]
- **Traded vehicle: the EUR exposure** {6E, E7, M6E*}; the contract is chosen by D2 in E.2.
  - **Reason:** EUR is the K3 exposure the log supports most, and the most tested on CME futures:
    - the only positive CME fix trade (K3-016 P-K3-016-e, f);
    - the only time-of-day strategy that survives costs (K3-023 P-K3-023-b; K3-024 P-K3-024-c);
    - a post-reform month-end fix cell (K3-002 P-K3-002-g);
    - price discovery and volatility studies on the euro future (K3-026, K3-027, K3-029, K3-030,
      K3-033).
  - **Liquidity:** EUR also has the cluster's highest public ADV, 6E 216,466 contracts a day in 2026
    Jan-Aug (D1 table).
  - **No fallback is declared.** The features below are EUR- and fix-specific. If D2 admits no EUR
    contract, the lead decides.
  - **Star flag:** if D2 picks M6E, the unresolved * restriction applies (D9.8).
- **Products the features read:**
  - The EUR vehicle.
  - The vehicles of the other admitted K3 exposures (JPY, GBP, AUD, CAD, CHF, NZD), for KF5 only.
  - Calendars: EC-CAL, EC-NFP, EC-FOMC, and the T_E and T_L clocks (C9).
- **Cluster features (7; with D15.4's B1-B5, 12).** Notation:
  - t_j is the decision time, and the last bar closed at t_j is the bar at t_j - 1.
  - "tick" is the vehicle's tick.
  - A missing bar, or a change of instrument_id inside a feature's bars, means no trade at t_j.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | fix_phase | 0 if t_j < T_E(d); 1 if T_E(d) <= t_j < T_L(d); 2 if t_j >= T_L(d). The clocks are from C9, on every date (a clock-only feature) | K3-016 P-K3-016-a (dollar up before each fix, down after), P-K3-016-c (fix times), P-K3-016-d (windows) | calendar and clock, known before d |
| KF2 | month_end | 1 if d = ME(m) (C9), else 0 | K3-001 P-K3-001-a, P-K3-001-e; K3-002 P-K3-002-b, P-K3-002-f; K3-003 P-K3-003-b | EC-CAL, known in advance |
| KF3 | ldn_prefix_ret | If t_j >= T_L(d): (close of the bar at T_L - 1 - open of the bar at T_L - 60) / tick, the London 15:00-16:00 hour; else 0 | K3-001 P-K3-001-c (the 15:00-16:00 return predicts reversion from 16:00, "on all days", "two times larger on end-of-month"; signs [unverified] in extraction, so the model learns the sign) | T_L (close of the bar at T_L - 1) <= t_j |
| KF4 | heat_wave_rv | Mean of abs(close - open) / tick over the vehicle's bars whose CT open time lies in [t_j, t_j + 60) on the most recent earlier trade date in EC-CAL that is not an early halt. At least 30 of those 60 bars are required, else no trade at t_j | K3-033 P-K3-033-a ("the economic significance of own-region spillovers is much more important than that of inter-region spillovers"); K3-030 P-K3-030-a ("intraregion volatility (heat waves)") | the previous trade date's bars, closed before d begins |
| KF5 | dol_ret60 | -(10,000 / n) x sum over X in S of (close of X's vehicle bar at t_j - 1 - open of X's bar at t_j - 60) / open of X's bar at t_j - 60. S is the set of admitted K3 exposures other than EUR, frozen in E.2 before any fit; n is the number of X in S with both bars on one instrument_id; n >= 4 required, else no trade at t_j. The sign makes a positive value a dollar appreciation (every K3 contract is quoted in USD per foreign unit, P-K3-007-b) | K3-016 P-K3-016-a, P-K3-016-b (the dollar factor "DOL" carries the fix pattern) | bars closed <= t_j |
| KF6 | nfp_phase | If d is an EC-NFP release date: -1 if t_j < 07:30 CT, +1 if t_j >= 07:30 CT; else 0 | K3-032 P-K3-032-b (a jump within minutes, no drift after), P-K3-032-c (volume 18 to 22 times average); K2-015 P-K2-015-a [K3] ("news produces conditional mean jumps"); K3-029 P-K3-029-a (nonfarm payroll surprises move FX futures) | calendar known in advance |
| KF7 | fomc_phase | If d is an EC-FOMC statement date: -1 if t_j < 13:00 CT, +1 if t_j >= 13:00 CT; else 0 | K3-009 P-K3-009-a (intraday currency futures react to FOMC surprises, "the reaction is short-lived", asymmetric) | calendar known in advance |

- **Decision window [W0, W1] = [00:45, 13:45] CT; horizon h = 60 minutes.**
  - **Decision times:** t_j = 00:45, 01:45, ..., 13:45, which is 14 a day. W1 + h = 14:45 <= F.
  - **Fills:** by D15.3's convention a position runs from the open of t_j + 1 to the open of t_j + 60,
    so every fill falls at :46 or :45.
  - **Why this window:**
    - It opens with the European morning, where K3-016's pre-ECB leg starts (01:00 CT, P-K3-016-d)
      and K3-024's European block lies (P-K3-024-d).
    - It ends inside the day session, before C.
    - The :45 offset puts every scheduled K3 event minute strictly inside a position interval, never
      at a fill:
      - the ECB fix at 07:15 or 08:15;
      - the 07:30 BLS release;
      - the 10:00 ET (09:00 CT) option expiry (P-K3-032-a, P-K3-021-b);
      - the London fix at 10:00 or 11:00;
      - the 13:00 FOMC statement;
      - the 14:00 settlement.
  - **Why h = 60:**
    - The logged EUR effects play out over hours (K3-016's multi-hour fix windows; K3-024's 4-hour
      blocks), and K3-001's pre-fix effect is one hour (P-K3-001-b).
    - h = 15 or 30 would sit inside the release jumps, which show no drift afterwards (P-K3-032-b).
      It would also need 20 or more decisions a day to cover the European morning.
    - h = 120 would fold the ECB fix, the 07:30 release and the London fix into one or two intervals.
- **Expected rows:** 14 per eligible research-window trade date: about 305 trade dates, less roll
  blackout, vendor-degraded and early-halt dates (D15.3), and less the 20-date warm-up of B4. That is
  roughly 3,400-4,000 rows; E.2 gives the exact count. B3 (minutes since O = 07:20) is negative before
  07:20, by definition.
- **Expected entries:** at most 14 per day (<= 20), each held 60 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps at
  >= 80% achieved null power on the confirmation window counts against it). Failing the D5 screen puts
  it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 14:45.
  2. Order type: market (D15.6).
  3. D9.4: at most 14 entries a day, 60-minute holds, no stops or brackets. No fill in a release or
     fix minute.
  4. *: M6E flag.
  5. News: q_c <= 1 lot-equivalent, not the full maximum. A position may span a release. On BLS days
     the 07:45 and 07:46 fills pay D8's event-window cost.
  6. D9.5a: no fill in [07:30, 07:32) or [13:00, 13:02) by construction.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C11.
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for
    every ML member.
- **Data needed:**
  - ohlcv-1m of the EUR vehicle and of every vehicle in S. The research window is used for training
    and tuning, the confirmation window for the frozen model.
  - The member-level coverage check covers 00:46-14:45 for the EUR vehicle (C12).
  - External: EC-CAL, EC-NFP, EC-FOMC.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K3-tkyswitch-01 | 6J short 5 minutes before and long 5 minutes after the Tokyo fix, the source's "holding the USD/JPY long for five minutes and then shorting it for the following five minutes" (K3-022 P-K3-022-c) | D9.3 floor; D9.4 | Five-minute holds give a mean hold of 5 minutes, below D9.3(c)'s 10-minute floor. Both fills sit at the fix minute. The edge, 1.8 bp, is "slightly above the transaction cost from the bid-ask spread" (P-K3-022-c), which the futures spread plus commission would consume. The longer-window versions are K3-tkypre-01 and K3-tkypost-01 |
| X-02 K3-gotrev-01 | 6J BUY from just after 9:55 to 12:00 JST on gotobi days only (K3-005 P-K3-005-b) | Rule 14 (look-ahead in the only evidence) | Its only logged figure, profit factor 2.09, is "In the days when the Gotobi anomaly occurred" (P-K3-005-d): conditional on an ex-post classification. No unconditional gotobi-day figure is logged. The all-days post-fix drift, tested on CME 6J, is K3-tkypost-01 |
| X-03 K3-tkypre-src-01 | K3-tkypre-01 with the source's 3:00 JST entry, or its golden-cross entry between 2:30 and 3:00 JST (K3-005 block) | Flat by F (partition rule 8) | 3:00 JST falls at 12:00 CST or 13:00 CDT of the previous trade date, so the position would be held across Topstep's 15:10 CT close. Written truncated as K3-tkypre-01. The golden-cross filter's window "n = 3" was chosen in sample as "the best" (the K3-005 block) and is not ported |
| X-04 K3-chnpmi-01 | 6A, 6N, 6C (and 6J, opposite sign) traded on Chinese PMI surprises: "Australian dollar 35 0.12 (0.03)*** ... Japanese Yen 35 -0.04" per one-SD surprise (K3-007 P-K3-007-d, e) | Rule 3; rule 1 | The surprise needs the consensus forecast, a proprietary survey with no named obtainable history. With the price response as a proxy nothing is left to trade: the move is complete inside the "10 minutes before to 10 minutes after" window (P-K3-007-c) and "appears to be permanent" (first-run passage, not re-checked). The pre-announcement CARs are "available upon request" and not shown (P-K3-007-g), so no direction or window can be traced. The release is also at US night, when D1 coverage was not measured |
| X-05 K3-usrel-01 | 6E or 6J traded on US macro release surprises (NFP and others) (K3-032 P-K3-032-a, b; K2-015 P-K2-015-a [K3]; K3-029 P-K3-029-a; K3-031 title only) | Rule 3; D9.5a; D9.4; evidence | The surprise needs the proprietary consensus. The response is "effectively a jump", and "the exchange rate returns subsequent to the few minutes around the time of the data release are orthogonal to the unexpected component" (P-K3-032-b): no drift to trade after D9.5a's 2-minute guard. A fill in the release minute is the gapped-market case of D9.4. The release clock enters K3-ml-01 as nfp_phase only |
| X-06 K3-fomc-01 | 6E or 6J traded on FOMC target and path surprises, or a fade of the "short-lived" reaction (K3-009 P-K3-009-a) | Partition rule 4 (K8); rule 1 | The surprise is measured from a rates instrument (fed funds futures), so the member has a rates leg: K8 (section 4). A price-proxy fade has no logged horizon or threshold (abstract only; numbers [unverified]). The clock enters K3-ml-01 as fomc_phase |
| X-07 K3-ukrel-01 | 6B before UK CPI, industrial production and retail sales (pre-release drift), or after them (the "slower" adjustment) (K3-034 P-K3-034-a) | Rule 1 (evidence) | The source's own finding is that the pre-release drift "weakens with the end of the prerelease access" in 2017, before this program's windows (2019+). The post-release claim is relative ("the speed of adjustment has become slower") and comes from an abstract with no horizon, magnitude or signal rule. The UK release time is not in the log. The product is "presumably 6B" but [unverified] |
| X-08 K3-payroll-01 | Mimic speculators' FX futures positioning ahead of payroll news (K3-014 P-K3-014-a) | Rule 3; flat by F | The positioning data are "most likely the CFTC weekly trader reports (not confirmed)" (K3-014 block), a weekly series. The information is "long-lived", which points to multi-day holding. No intraday rule is traceable |
| X-09 K3-spotlead-01 | 6E or 6J traded on a spot-FX lead (EBS or retail spot leading the future), or the reverse (K3-026 P-K3-026-a; K3-027 P-K3-027-a; K3-029 P-K3-029-a; K3-031, K3-037 title only) | Rule 3; D9.3/D9.4; rule 1 | Interdealer spot (EBS, Reuters) is proprietary, and a free retail feed is indicative quotes. The sources disagree on which market leads (K3-027: spot leads; K3-026 and K3-029: futures lead or dominate). Price-discovery shares imply second-to-minute horizons, not a traceable minute-scale rule with a threshold |
| X-10 K3-triarb-01 | Triangular arbitrage among EUR, JPY and CHF legs (K3-044 P-K3-044-a, b; K3-045 P-K3-045-a) | D9.3 floor; D9.4 | Opportunities last seconds, and profiting needs beating others "to an unfeasibly large proportion of arbitrage prices" (P-K3-044-a). Topstep's prohibited pattern is "average durations measured in seconds" (F7.3). The three-leg version would also breach the 1 lot-equivalent cap |
| X-11 K3-xrate-01 | Lead-lag or relative value among CME currency futures (cross rates such as EUR/GBP from 6E and 6B) (K3-042) | Rule 1 | Title only; nothing retrieved. No other log item gives a cross-rate rule |
| X-12 K3-gaprev-01 | Intraday reversal after large one-day returns and opening gaps (K3-011 P-K3-011-a, b) | Rule 1 (parameters) | Abstract only. The "large" thresholds and magnitudes are [unverified], and the pattern is from 1988-2003 pit sessions (the "opening gap" of the pit open no longer exists). The prior-day daily-bar family on FX is CP3 (which bets the other way, continuation) |
| X-13 K3-mehedge (GBP, AUD, CAD, CHF, NZD) | K3-mehedge-01 extended to the other currencies in the source's sample (K3-001 block: EUR, JPY, GBP, CAD, AUD, SEK, NOK, CHF, NZD) | Rule 3 (data) | No free historical source of the local benchmark index (FTSE, S&P/ASX 200, S&P/TSX, SMI, NZX 50) was named or confirmed in E.0: the search tools are exhausted. The source's Datastream indices are proprietary. If E.2 names one, the lead may add that exposure (+1 trial each) |
| X-14 K3-fixrevON-01 | K3-001's post-fix reversion as tested, from 16:00 GMT to noon the next day (P-K3-001-c) | Flat by F | The position would be held overnight. A same-day truncation (16:00 London to 15:05 CT) is an untested horizon. The month-end post-fix reversal enters as K3-ldnrev-01 (at K3-002's 15-minute horizon), and the all-days pre-fix-hour return enters K3-ml-01 as ldn_prefix_ret |
| X-15 K3-fomcdrift-01 | Currency futures positioned on FOMC shocks over "three weeks before and after the announcements" (K3-008 P-K3-008-a) | Flat by F | Multi-week drift; whether the announcement-day effect is intraday is [unverified] (abstract only). The high-yield and EM emphasis points to 6M, which is out by D1 |
| X-16 K3-cot-01 / K3-carry-01 | Weekly COT positioning predicting spot rates (K3-015 P-K3-015-a, b); carry and order flow (K3-012 P-K3-012-a) | Flat by F | Weekly signals and multi-week horizons; carry is held overnight (partition rule 8). Both items are logged as should-have-been-rejected |

---

## 3. Beyond budget (lead decides)

None. The log supports 6 new members inside the budget of 11. These candidates were considered and not
written; none is a budget overflow. Each would add trials.
- **Ranaldo's fixed 4-hour blocks for CHF and JPY** (K3-024 P-K3-024-d):
  - The windows: CHF short 08:00-12:00 GMT and long 12:00-16:00 GMT; JPY long 12:00-16:00 GMT.
  - Why not written: the only cost evidence on these pairs is against them. "most of these simple
    time-of-day trading strategies are not profitable when trading costs are included. However, the
    notable exception is EUR/USD" (K3-023 P-K3-023-b). Ranaldo's figures are gross, on indicative
    quotes. The EUR version of the mechanism is carried by K3-ecbfix-01, which is in the same direction
    in overlapping hours.
  - Cost: +2 trials (+1 for a GBP or AUD version from K3-023, which the same cost passage argues
    against).
- **The London-fix W for GBP** (K3-016's pre/post-London trade): its own CME test on 6B is negative,
  "-4.83" % a year, Sharpe "-0.51" (P-K3-016-f). +1 trial.
- **The every-day pre-Tokyo long-dollar trade on 6J** (K3-016): its own CME test is "-11.23" % a year
  (P-K3-016-f). The gotobi-conditioned version is written (K3-tkypre-01). +1 trial.
- **K3-ecbfix-01 as the pre-fix leg only.** The source's table gives the pre-leg alone a Sharpe of 0.99
  against 0.65 for the headline pre/post trade (P-K3-016-f). The headline trade is written, so as not to
  pick the best of the source's nine cells. The lead may substitute (not add) the pre-leg-only version:
  0 extra trials.
- **K3-ldnrev-01 for AUD and CAD.** Both are in K3-002's pair list, but their post-reform month-end
  cells are not in the log. K3-003 is positive "for at least one horizon" in all but JPY and GBP
  (P-K3-003-e), which is pre-reform. +2 trials.

---

## 4. Routed to K8

| Source | Legs | One phrase |
|---|---|---|
| Alquist, Ellwanger, Jin (2020), JFM (registry K4-008, tagged K1-K4; not read by K3) | WPSR-identified oil shock (K4) -> FX (K3), equities, Treasuries | oil inventory news as an instrument for cross-asset responses (K3 log section 4, run 1) |
| Aligrithm, "FX Edge Lives in Other Markets (cross-asset series)" (Quantocracy; practitioner) | government-bond rates (K2) -> FX (K3) | interest-rate-parity signal on a graph (K3 log section 4) |
| Peng, Chollete, Hughen, Lu (2026), "Forecasting Volatility of Currencies and Oil with Brown Firms" (R-K3-028) | equities -> FX and crude volatility | cross-asset volatility forecast (K3 log section 4) |
| Quantpedia slugs "equity-momentum-spillover-to-currencies", "stock-and-bond-returns-predict-currency-returns" (pages HTTP 500) | equity (K1), bonds (K2) -> FX (K3) | cross-asset; horizon unknown (K3 log section 4) |
| Wang, Yang, Simpson (2008), K3-009, the surprise measure | fed funds futures surprise (rates) -> FX futures (K3) | X-06: the FOMC target and path surprise is a rates-instrument signal |
| Kurov, Stan (2018), K3-035 [K3] | monetary-policy uncertainty (a rates-derived measure, [unverified]: abstract only) conditioning FX's macro response | conditioning variable from rates; K3 has no macro-release base member to condition (X-05) |
| Sharma (arXiv 1705.08022), flagged by the K2 reader (K2 log) | 10-year Treasury yield (K2) -> AUD, CAD, NZD, JPY pairs (K3) | macro-forecast input to an FX pairs trade |
| Rosa (2013), K4-025, flagged by the K4 reader | FOMC-driven USD (K3) and CL (K4) | the energy response to FOMC runs through the dollar |
| Quantocracy / Milton FMR, "Pairs Trading ... CAD - Crude Oil", flagged by the K4 reader | 6C (K3) and CL (K4) | CAD-crude pairs |
| Zangelidis, Rezitis (2026), flagged by the K1 reader | US dollar index (K3) with NASDAQ, copper and commodity indices | intraday realized-volatility topology |

The first four rows are the K3 reader's own flags. Rows 5 and 6 are this catalog's routing of X-06
and K3-035. Rows 7-10 are other readers' flags naming a K3 leg, listed for completeness.

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K3.md section 3 (K3-001 to K3-045), every
`[K3]`-tagged passage elsewhere (K2-015), and the panel item the log points to (D.1 A10).

| Item | Disposition |
|---|---|
| K3-001 Melvin, Prins | **Used:** K3-mehedge-01 (P-a, b, d, e); K3-ml-01 ldn_prefix_ret (P-c) and month_end (P-a, e); supporting K3-ldnrev-01 (P-c, month-end reversion twice as large). **Not intraday-feasible as tested:** the reversion to next-day noon, X-14. Other currencies excluded for data, X-13 |
| K3-002 Ito, Yamada (London) | **Used:** K3-ldnrev-01 (P-b, d, e, f, g; P-a context); T_L window reasoning in K3-ldnmom-01 and K3-mehedge-01 (P-d); K3-ml-01 month_end (P-b, f). The intra-month null (P-f, g) is why ldnrev trades month-end only. P-c (tail probability) not used |
| K3-003 Evans (WMR fix) | **Used:** K3-ldnrev-01 (P-b, c, d, f); the JPY and GBP exceptions (P-e) as conflicting evidence and in the GBP exclusion; K3-ml-01 month_end (P-b) |
| K3-004 Xu, Øwre-Johnsen (Norges Bank) | **Supporting and conflicting:** activity rises ahead of the ECB fix (P-b, context for K3-ecbfix-01); no significant price change at the WM fix (P-d, evidence against K3-ldnmom-01). The NOK result concerns a non-K3 product. P-a, P-c are context only |
| K3-005 Bessho, Sugimoto, Suzuki (gotobi) | **Used:** K3-tkypre-01 (P-a, P-c). Leg 2 excluded, X-02 (P-b, P-d look-ahead). The 3:00 JST entry and the golden-cross filter are excluded, X-03 |
| K3-006 Baldwin, Lewejohann (CME Asian hours) | **Not a mechanism:** a liquidity and cost input. Cited in C12 (P-a, b, c) as context for the overnight coverage check of K3-tkypre-01, K3-tkypost-01 and K3-ml-01 |
| K3-007 Baum, Kurov, Wolfe (Chinese PMI) [K3] P-b to P-g | **Excluded,** X-04. P-b's quotation convention is used in C8 and in K3-ml-01 dol_ret60. The [K1], [K4], [K5], [K6] passages belong to those writers |
| K3-008 Tse (FOMC, currency futures) | **Not intraday-feasible** (multi-week), X-15 |
| K3-009 Wang, Yang, Simpson (FOMC surprises) | **Excluded as a member,** X-06 (surprise from rates: K8). Used in K3-ml-01 fomc_phase (P-a) |
| K3-010 Seeck (intraday momentum, 6J) | **Covered by CP1** (family C3, intraday momentum). The London-open variant is not written: the passages are first-run and not re-verified, and the source reports that 6J "fail[s] to clear [its] cost hurdle" (P-a) |
| K3-011 Rentzler, Tandon, Yu | **Excluded,** X-12 (abstract only, thresholds absent, pit era) |
| K3-012 Breedon, Rime, Vitale (carry) | **Not intraday-feasible,** X-16 |
| K3-013 FSB FX Benchmarks | **Not a mechanism.** Used for context: the fix minute's volume (P-d) in K3-ldnrev-01's D9.4 check; the 8:30 ET release as the day's peak one-minute volatility (P-b), which informed K3-ml-01's window placement |
| K3-014 Park (payroll positioning) | **Excluded,** X-08 |
| K3-015 Tornell, Yuan (COT) | **Not intraday-feasible,** X-16 |
| K3-016 Krohn, Mueller, Whelan | **Used:** K3-ecbfix-01 (P-a, c, d, e, f, g, h); K3-tkypost-01 (P-b, c, d, f); clocks T_L, T_E, T_T (P-c); K3-ml-01 fix_phase and dol_ret60 (P-a, b); evidence against K3-tkypre-01's every-day analogue (P-f). The GBP London W and the every-day pre-Tokyo trade are not written, for negative CME results (section 3) |
| K3-017 Osler, Turnbull | **Used:** K3-ldnmom-01 (P-a, b, c); the 15:45 anchor in K3-ldnrev-01's signal window (P-b) |
| K3-018 Marsh, Panagiotou, Payne | **Supporting** K3-ldnrev-01 (P-a (2), (6); P-b, c: CME futures data); evidence against K3-ldnmom-01's post-fix part (P-a (6)) |
| K3-019 Evans, O'Neill, Rime, Saakvitne (FCA) | **Conflicting evidence** for K3-ldnrev-01, stated in its entry (P-a, b, c). Its "less trading before the fix" (P-a) is stated against K3-ldnmom-01. Its 15-minute windows (P-b) set ldnrev's pre-fix window |
| K3-020 Benenchia, Galati, Lepone | **Pending evidence:** Stage 2's reversal result is [unverified] (P-c). Its 15-minute windows (P-a) support ldnrev's pre-fix window. Section 7, item 7 |
| K3-021 Michelberger, Witte | **Supporting** K3-ldnmom-01 (P-a, c). The 10am EST expiry cluster (P-b) informed K3-ml-01's window placement |
| K3-022 Ito, Yamada (Tokyo) | **Used:** K3-tkypre-01 (P-a, b, d); conflicting evidence for K3-tkypost-01 (P-c); the 5/5-minute switch excluded, X-01 (P-c); T_T clock (P-c) |
| K3-023 Breedon, Ranaldo | **Corroborates** K3-ecbfix-01 (P-a, b, c). CHF, JPY, GBP and AUD versions not written: its cost result (P-b) is against them (section 3). P-d (Cornett et al., second hand) is corroborating. P-e (the July 4 anecdote) is insufficient evidence: an anecdote, not a test |
| K3-024 Ranaldo | **Corroborates** K3-ecbfix-01 for EUR (P-a, b, c, d). The CHF and JPY block member was considered and not written (section 3) |
| K3-025 Cornett, Schwarz, Szakmary | **Corroborates** K3-ecbfix-01's second leg (P-a; abstract only, 1977-1991 pit session). Insufficient evidence for a member of its own |
| K3-026 Tse, Xiang, Fung | **Excluded,** X-09 (lead-lag) |
| K3-027 Cabrera, Wang, Yang | **Excluded,** X-09 |
| K3-028 Han, Kling, Sell | **Insufficient evidence:** day-of-week volatility patterns with no directional claim (P-a), pit-era. Not used |
| K3-029 Chen, Gau (2022) | **Excluded** as a lead-lag member (X-09) and as a surprise member (X-05). Used in K3-ml-01 nfp_phase (P-a: "nonfarm payroll affect both order flows and exchange-rate changes") |
| K3-030 Martínez, Tse [K3] P-a | **Used:** K3-ml-01 heat_wave_rv (P-a, "intraregion volatility (heat waves)"). The [K1] and [K2] parts belong to those writers |
| K3-031 Chen, Gau (2010) | **Insufficient evidence:** title only. Listed under X-05 and X-09 |
| K3-032 Chaboud et al. (IFDP 823) | **Excluded as a member,** X-05 (no post-release drift, P-b). Used in K3-ml-01 nfp_phase (P-b, c) and window placement (P-a); T_L confirmation (P-a) |
| K3-033 Cai, Howorka, Wongswan (IFDP 863) | **Used:** K3-ml-01 heat_wave_rv (P-a) |
| K3-034 Kurov, Sancetta, Wolfe | **Excluded,** X-07 |
| K3-035 Kurov, Stan [K3] P-a | **Routed to K8** (section 4). No K3 base member to condition |
| K3-036 Andersen, Bondarenko, Gousgounis, Onur | **Insufficient evidence:** title only (FX futures invariance, cost modelling). Not used |
| K3-037 Cabrera | **Insufficient evidence:** title only. Listed under X-09 |
| K3-038 Cotter, Dowd | **Insufficient evidence:** a one-week 1997 sample, descriptive (P-a, b). Not used |
| K3-039 Batten, Ellis, Hogan | **Insufficient evidence:** 42 days of indicative quotes, descriptive (P-a, b). Not used |
| K3-040 Kosowski et al. | **Insufficient evidence:** title only, content [unverified]. CP1's (a) form bets the opposite way (overnight continuation) |
| K3-041 Khademalomoom, Narayan | **Corroborating** the session-clock family (P-a: time-of-day effects in AUD, GBP, CAD, EUR, JPY, CHF). Abstract only, no windows or magnitudes: insufficient evidence for a member of its own |
| K3-042 Elyasiani, Kocagil | **Excluded,** X-11 (title only) |
| K3-043 Ayadi, Ben Omrane, Das | **Insufficient evidence:** title only. It concerns EM currencies; 6M is out by D1 |
| K3-044 Fenn et al. | **Excluded,** X-10 |
| K3-045 Aiba et al. | **Excluded,** X-10 |
| K2-015 Andersen, Bollerslev, Diebold, Vega, P-K2-015-a [K3] (and P-c's implicit FX comparison) | **Not a member:** a contemporaneous "conditional mean jump" (X-05). Used in K3-ml-01 nfp_phase |
| D.1 A10 Baltussen, Da, Lammers, Martens (panel, not re-read) | **Covered by CP1.** Its FX results are [unverified from K3's side] (K3 log) |
| reports/stage_e0_research_K3_sonnet_partial.md | Not used (superseded, per the brief) |
| R-K3-001 to R-K3-044 | Rejected in the log; not used. Facts from three of them are used: R-K3-013 (ECB fix time, now confirmed from the ECB page: "around 14:10 CET"), R-K3-014 (FX BTIC routes month-end fix flow to CME futures, in K3-mehedge-01), R-K3-015 (CME "Daily Settlement 2:00 p.m. Central Time", in C5) |

**Correlated members, flagged for the lead's Tier-A accounting (not duplicates).**
- **London fix, EUR, JPY and CHF on month-end days:** K3-mehedge-01 (T_L-60 to T_L-3), K3-ldnmom-01
  (T_L-12 to T_L+5) and K3-ldnrev-01 (T_L+5 to T_L+20) trade adjacent windows. Their signals and
  directions are independent by construction.
- **6J on gotobi evenings:** K3-tkypre-01 (SELL into the fix) and K3-tkypost-01 (BUY after it) trade
  consecutively.
- **K3-ecbfix-01 and K3-ml-01** both read the EUR fix clock; K3-ml-01's fix_phase feature encodes the
  same W.

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all seven admitted) |
|---|---|---|---|
| K3-cp1-01 | EUR, AUD, GBP, CAD, JPY, CHF, NZD | 1 | 7 |
| K3-cp2-01 | EUR, AUD, GBP, CAD, JPY, CHF, NZD | 1 | 7 |
| K3-cp3-01 | EUR, AUD, GBP, CAD, JPY, CHF, NZD | 1 | 7 |
| K3-ldnrev-01 | EUR, JPY, CHF | 1 | 3 |
| K3-ldnmom-01 | EUR, JPY (narrowed by the lead from 6) | 1 | 2 |
| K3-mehedge-01 | EUR, JPY (each only with an obtained index history) | 1 | 2 |
| K3-ecbfix-01 | EUR | 1 | 1 |
| K3-tkypre-01 | JPY | 1 | 1 |
| K3-tkypost-01 | JPY | 1 | 1 |
| K3-ml-01 | EUR (no fallback) | 48 in research-window accounting only (D15.8) | 1 |
| **Cluster total** | | | **36** = 21 port + 14 new + 1 ML |

**General formula.** With E the number of admitted exposures and a_X = 1 if exposure X is admitted
(0 otherwise):

N_K3 = 3E + 5 a_EUR + 5 a_JPY + 2 a_CHF + a_GBP + a_CAD + a_NZD - (index drops from K3-mehedge-01).

- a_EUR's 5 = ldnrev + ldnmom + mehedge + ecbfix + ml.
- a_JPY's 5 = ldnrev + ldnmom + mehedge + tkypre + tkypost.
- a_CHF's 2 = ldnrev + ldnmom. GBP, CAD and NZD carry ldnmom only; AUD carries only the ports.
- Check: 21 + 5 + 5 + 2 + 1 + 1 + 1 = 36.
- **Examples:** if D2 admits only 6E, 6J and 6B (and both indices are obtained), 9 + 5 + 5 + 1 = 20.
  If neither index is obtained, subtract 2.

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **M6E and M6A carry an unresolved * restriction** (D9.8; F12.1 found no referent).
   - D2 may pick M6E for EUR or M6A for AUD. Every EUR and AUD member carries the flag, and K3-ml-01
     trades EUR with no fallback.
   - If the user cannot clear the flag before E.1, D2 must choose among 6E and E7 for EUR, and 6A
     alone for AUD.
2. **Overnight windows are outside D1's coverage measurement** (C12). K3-tkypre-01 and K3-tkypost-01
   trade 6J at 17:30-01:00 CT; K3-ecbfix-01 and K3-ml-01 trade the EUR vehicle from 01:00 and 00:46 CT.
   D9's member-level coverage check decides in E.2. If it fails, those members are excluded before
   screening; the catalog does not assume it passes.
3. **K3-ldnmom-01 rests on a model, not a profitability test** (P-K3-017-b; the K3-017 block), and
   has contrary evidence (P-K3-019-a, P-K3-004-d). It costs 6 trials. The lead may cut it, or narrow
   it to month-end days (fewer events, with the flow evidence of P-K3-001-e).
4. **K3-mehedge-01's signal sources are unconfirmed** (header; X-13).
   - The member is written for EUR (EURO STOXX 50) and JPY (Nikkei 225), with an E.2 drop rule.
   - The index choice (the publishers' blue-chip indices instead of the source's Datastream Total
     Market indices) is a judgment for the lead to accept or change.
   - The other five exposures need a named free source.
5. **K3-ecbfix-01's form.** The headline pre/post trade is written. The pre-leg-only version (Sharpe
   0.99 in the source's table against 0.65) is available as a substitution (section 3).
6. **Month-end and holiday definitions** (C9). Three are judgments:
   - ME is CME's last trade date of the month, with a drop when it is an E&W bank holiday (whether the
     WM/R month-end flow happens on a London holiday is not in the log);
   - London members skip E&W bank holidays;
   - Tokyo business days exclude 31 December to 3 January, and gotobi dates are not shifted off
     weekends or holidays (the log states no shift rule).

   Any change moves a few dates a year.
7. **Is the post-fix reversal still alive?** K3-019 (reversals gone after 2015, all days) and K3-002
   (month-end profitable post-reform at 15 minutes) conflict, and the decisive pre-registered re-test
   (K3-020 Stage 2, 2015-2023) was not retrieved (SSRN, ScienceDirect and Macquarie blocked, Firecrawl
   exhausted). If a later session retrieves it and it finds no month-end reversal, the lead may cut
   K3-ldnrev-01 (3 trials) before E.1 hashes the catalog.
8. **The cost sample has no fix-event days.** D8's five dates include no month-end, so the month-end
   fix window's spread is calibrated on ordinary days, which may understate K3-ldnrev-01's and
   K3-mehedge-01's cost. One date, 2026-04-15, is a gotobi day. The lead decides whether to add a
   month-end date to the K3 mbp-1 sample (a small spend, quoted in E.1) or to accept the limitation, as
   was ruled for K4's gas Thursdays (Q5, 21:52).
9. **Port text meets FX release clocks, copied unchanged:**
   - CP2's opening range [07:20, 07:35) contains the 07:30 CT BLS release on NFP days.
   - CP1's entry fill at 13:30 on FOMC days sits exactly 30 minutes after the statement. That is the
     boundary of D8's event-window cost; E.2 must fix whether the window is [release, release + 30 min)
     or closed.
   - Whether FX ports skip these days would be a D6 change.
10. **Frequency** (C10). K3-ldnrev-01 and K3-mehedge-01 trade about 14 research days and need about
    22 x eps_X per event. They are likely "inconclusive by design" (D4). They cost 5 trials. The 21:52
    ruling (Q4) keeps such members; this is noted for the trial budget only.
11. **E.2 checks named in this catalog:**
    - (a) The known-answer tests for T_L, T_E and T_T (C9).
    - (b) EC-TGT for 2019-2025 from Wayback captures.
    - (c) The equity-index histories (K3-mehedge-01).
    - (d) Tick-size history 2019-2026 (C7) and E7's listing date (C8).
    - (e) How TopstepX counts E7, M6E, M6A and M6B against the lot limit (C6).
    - (f) CME FX price limits against D9.7 (C11).
    - (g) Overnight member-level coverage (C12).
    - (h) The set S for K3-ml-01's dol_ret60, frozen before any fit.
    - (i) The Japanese year-end closure (C9).
12. **Registry hygiene** (already listed by the reader, K3 log section 5):
    - Wrong or incomplete author fields: K3-018 (correct: Marsh, Panagiotou, Payne); K3-005, K3-012,
      K3-014, K3-015, K3-038 and K3-039 "unspecified"; K3-040 and K3-043 "?".
    - Run 1 edited K3-007 and K3-009 in place.
    - This catalog cites the corrected authors from the log blocks.
