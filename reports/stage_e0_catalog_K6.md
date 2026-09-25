# Stage E.0 hypothesis catalog, cluster K6 (agriculture and livestock: ZC, ZW, ZS, ZM, ZL, HE, LE)

> **[Stage E.1, 2026-09-24: the user's decisions applied (docs/DECISIONS.md, U1 to U9; every edit in
> reports/stage_e1_changes.md).]** U6: K6-ml-01 is excluded: superseded by the Stage E ML route
> (user decision 2026-09-24); its text stays visible below and it adds 0 trials.
> **K6 after the decisions: 7 active members, 27 confirmation trials** (4 new + 3 core ports (K6-ovr-01 excluded by the lead); 21 port + 6 new trials). Header
> and section 6 totals below are superseded where they differ.

Writer: CatalogWriter-K6-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from 01:29 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any K6 product existed on this machine. The only product-specific numbers it uses are:
- contract specifications and public ADV (reports/stage_e0_liquidity.json);
- Topstep's published fees, hours and release table (reports/stage_e0_topstep_facts.md);
- calendar metadata (USDA release dates and clock times) and CME's price-limit rules as text (the
  limit levels in P-K6-047-a are rule parameters, not prices).

No price level, range or volatility of any K6 product is used or assumed below. Two logged passages
describe a single date inside the confirmation window: the August 12, 2019 corn report day,
P-K6-011-b and P-K6-011-e. They are cited only as illustrations of the D9.7 risk, and no parameter
is taken from them.

**Inputs read in full:**
- reports/stage_e0_research_K6.md.
- Every `[K6]`-tagged passage elsewhere: K3-007 (P-K3-007-j) and K3-040 (title only) in
  reports/stage_e0_research_K3.md; K4-034, K4-035 and K4-036 (and the R-K4-040 and R-K4-063 rows) in
  reports/stage_e0_research_K4.md; K5-023, K5-029 and K5-030 in reports/stage_e0_research_K5.md.
- reports/stage_e0_source_registry.jsonl: K6 lines and every line tagged K6.
- docs/STAGE_E_DESIGN.md: D1 to D15, including the 21:12 and 21:52 amendments recorded in
  reports/stage_e0_STATE.md.
- reports/stage_e0_partition.md, reports/stage_e0_topstep_facts.md, and the K6 rows of
  reports/stage_e0_liquidity.json.
- reports/stage_d1f_confirmation_list.md 2.1 A3 (Family H mechanics).
- reports/stage_e0_catalog_K4.md and reports/stage_e0_catalog_K2.md, for format only.

**Official pages fetched in this task.** These were fetched with curl on 2026-09-24 between 01:33 and
01:36 PDT, only to confirm that a data source exists and has history. No mechanism research was done.
Files are saved under the session scratchpad at fetch/k6cat.
- https://usda.library.cornell.edu/concern/publications/3t945q76s redirects (301) to
  https://esmis.nal.usda.gov/publication/world-agricultural-supply-and-demand-estimates (HTTP 200).
  - It lists dated WASDE releases with pdf, txt, xls and xml files. The month index runs back past 2018.
  - The index shows "December 2025 November 2025 September 2025": no October 2025 release is listed.
- https://usda.library.cornell.edu/concern/publications/8336h188j redirects (301) to
  https://esmis.nal.usda.gov/publication/crop-progress (HTTP 200).
  - It lists dated weekly releases (pdf, txt) for April to November of each year, back past 2017.
  - No October 2025 entry is listed.
- https://esmis.nal.usda.gov/publication/grain-stocks, /crop-production, /acreage and
  /prospective-plantings (HTTP 200 each). Each lists dated releases back past 2019. The latest
  releases shown are Grain Stocks Jun 30 2026, Crop Production Sep 11 2026, Acreage Jun 30 2026 and
  Prospective Plantings Mar 31 2026.

---

## 0. Header

| Item | Value |
|---|---|
| Exposures | corn {ZC}, wheat {ZW}, soybeans {ZS}, soybean meal {ZM}, soybean oil {ZL}, lean hogs {HE}, live cattle {LE}. One contract each; there are no Topstep-permitted micros (Topstep F1 lists only these seven K6 contracts) |
| D1 | **D1 applied: all seven K6 exposures IN; no starred product.** 2026 Jan-Aug ADV: ZC 505,663; ZW 180,405; ZS 302,997; ZM 181,637; ZL 232,819; HE 67,267; LE 68,652. Day-session coverage 0.990 to 1.000 (design D1 table). No K6 product appears in the D9.11 volatility caps or the D9.12 CPI window |
| D2 | Each exposure has exactly one admissible contract, so D2 has no vehicle choice. It either admits the contract (rho <= 2.0 at q = 1) or drops the exposure. An admitted exposure with rho < 0.5 trades at q = 1 and is flagged "undersized". Every entry reads "Vehicle: D2 (chosen in E.2)", and every trial is **traded only if D2 admits the exposure** |
| Members | **9 = 5 new + 3 core ports + 1 ML member.** Budget 15, so 6 slots are unused (section 3) |
| Trials in N (confirmation) | **39 if D2 admits all seven:** 21 port + 17 new + 1 ML. In general: 4E + (a_ZS + a_ZM + a_ZL) + (a_ZC + a_ZS) + a_ZC + (a_ZW + a_ZC + a_ZS + a_ZL) + a_ZC, where E is the number of admitted exposures and a_X = 1 if X is admitted |
| ML grid | ~~48 configurations, counted only in the K6 screening session's research-window accounting (D15.8)~~ [superseded, U6: no ML member] |
| Sizing | q = 1 contract in every member, which is 1 lot-equivalent: the D9.5 cap, half the 50K XFA's 2-lot maximum |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.**
  - Times are America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose ts_event (its open)
    is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values are usable from
    then on.
  - USDA releases published at "12:00pm ET" are 11:00 CT all year (P-K6-049-a: "11:00 a.m. CT (12:00
    p.m. ET)"), because both zones change clocks on the same dates.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open, as in D6 and D15.3.
  "Market intent on the bar at X" fills at the open of the bar at X + 1 min. Harness rules D9.5a
  (event-minute guard) and D9.7 (price-limit proximity) override a fill where they apply.
- **C3 Trade date.**
  - The program window for trade date d is [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md).
  - **Grains (ZC, ZW, ZS, ZM, ZL).** Trade date d opens with the evening session before d (19:00 CT;
    Sunday evening for a Monday) and ends at the 13:20 CT close on d. Between them is the 07:45-08:30
    CT pause (Topstep F4: "CBOT Commodity Market Pause (Mon-Fri): 7:45 AM - 8:30 AM CT. No orders
    accepted during this window"). The "trade date's first bar" is the first bar at or after that
    19:00 CT open. O = 08:30, C = 13:15, F = 13:18 (D6 table).
  - **Livestock (HE, LE).** Trade date d is the day session 08:30-13:05 CT only. The night session was
    cancelled in October 2014 (P-K6-023-d), and Topstep lists "Monday-Friday: 8:30 AM - 1:05 PM CT". The
    first bar is the 08:30 bar. O = 08:30, C = 13:00, F = 13:03 (D6 table).
- **C4 Exclusions for the five new members.** The ports follow D6 as written. A new member does not
  trade on:
  - roll-blackout dates (`screen_candidate` with `roll_blackout`);
  - dates the D10 grain or livestock calendar marks as early close or early halt ("Days with
    early_halt_ct set: no trade", Family H);
  - dates on which a bar the rule reads, or the entry bar, is missing, or on which bars that one
    computation reads carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar, with the engine's
  forced flatten at F as the backstop. A lock at the daily limit shows up as bars at one price, and
  D9.7 governs it (C13).
- **C5 Flat time.**
  - F = 13:18 CT for grains and 13:03 CT for livestock. On early-close days F is the early close minus
    15 minutes (D9.1, D10).
  - No member holds any position across the 07:45-08:30 grain pause or overnight. The only overnight
    input any member reads is CP1's open of the 19:00 CT bar.
  - Every new member's last fill is at or before 13:14 (grains) or 12:59 (livestock).
- **C6 Size.**
  - q = 1 contract of the exposure's single admissible contract. That is 1 lot-equivalent ("minis 1",
    D9.6) and the D9.5 member cap.
  - No member sizes by signal, and no member holds two legs (section 2, X-01 and X-02).
- **C7 Ticks and fees.** Ticks are from reports/stage_e0_liquidity.json (CME specifications, fetched
  2026-09-23 20:49 PDT). Round turns are Topstep F3. The only fee change D8 applies (from 2026-10-01)
  is to MCL and MNG, not K6.

  | Contract | Tick | Tick value | CP2 buffer (4 ticks) | Topstep round turn |
  |---|---|---|---|---|
  | ZC | 0.0025 USD/bu (1/4 cent) | $12.50 | 0.01 USD/bu ($50) | $5.28 |
  | ZW | 0.0025 USD/bu | $12.50 | 0.01 USD/bu ($50) | $5.28 |
  | ZS | 0.0025 USD/bu | $12.50 | 0.01 USD/bu ($50) | $5.28 |
  | ZM | 0.10 USD/short ton | $10.00 | 0.40 USD/short ton ($40) | $5.28 |
  | ZL | 0.0001 USD/lb (0.01 cent) | $6.00 | 0.0004 USD/lb ($24) | $5.28 |
  | HE | 0.00025 USD/lb | $10.00 | 0.001 USD/lb ($40) | $5.22 |
  | LE | 0.00025 USD/lb | $10.00 | 0.001 USD/lb ($40) | $5.22 |

  These are 2026 specifications. E.2 confirms that each tick was unchanged over 2019-05..2026-06
  before any bar is read, because CP2's buffer, the ML features and several sign checks are in ticks.
  E.2 also confirms each product's raw price units in GLBX.MDP3 (cents or dollars per unit), which
  K6-crushgap-01's GPM needs.
- **C8 Price data.**
  - Source: Databento GLBX.MDP3 ohlcv-1m of the vehicle. It is paid: the research window is bought in
    E.1, and the confirmation and holdout-2 history of each admitted vehicle in E.2b (D13; K6 about
    $5.32 + $26.52 + $0.77 mbp-1).
  - History: all seven contracts have history from 2019-05. None is a micro with a late listing.
  - **Legs of non-admitted exposures.** If an exposure is not admitted by D2, D13 does not buy its
    history. E.2 must buy it as a leg where a member reads it: ZS, ZM and ZL for K6-crushgap-01; ZS
    for K6-ml-01.
  - Availability: a bar is available at its close (C1).
  - mbp-1 enters only through D8's shared five-date cost sample. No member reads order-book data.
- **C9 Event calendars.** All are external and free. A rule reads only dates and scheduled clock
  times, except K6-ml-01's feature cp_ge_chg, which reads a published USDA value (C9d).
  - **(a) EC-USDA: the scheduled 11:00 CT grain releases.**
    - Covered releases: WASDE and Crop Production, which share a date (P-K6-038-b dates against
      P-K6-040-a "CropProduction1 / 12 10 10 9 12 11 10 12 11 9 10 10"); Grain Stocks; Prospective
      Plantings; Acreage.
    - Times:
      - "2026 WASDE Release Dates (12:00pm ET)" (P-K6-038-a);
      - "1 / Noonrelease" for Crop Production, Grain Stocks and Prospective Plantings (P-K6-040-a,
        P-K6-040-b);
      - WASDE "11:00 a.m. CT (12:00 p.m. ET)" (P-K6-049-a) and Grain Stocks "at 11:00 a.m. CT"
        (P-K6-049-c);
      - releases have been at 12:00 ET since January 2013, so throughout 2019-2026 (P-K6-012-b,
        P-K6-017-b, P-K6-018-b, P-K6-037-b).
    - Schedule sources: the USDA OCE WASDE page (yearly lists, Wayback captures for 2019-2025) and
      the NASS PFEI schedule PDF for each year (the 2026 one is K6-040; E.2 retrieves 2019-2025
      through Wayback).
    - Actual releases: the ESMIS record (esmis.nal.usda.gov, fetched above).
    - **Drop rule.** An event whose actual ESMIS date differs from the year's published schedule is
      kept only if a USDA notice of the new date, dated before d, is found. Otherwise it is dropped.
      ESMIS lists no October 2025 WASDE or Crop Progress, which E.2 must expect as gaps.
    - Subset **EC-WASDE**: the WASDE dates.
    - Notation: T = 11:00 CT on an EC-USDA date.
  - **(b) EC-CAL.** The D10 grain and livestock calendars (trade dates, holidays, early closes and
    halts, session hours), built by E.2 from CME schedules.
  - **(c) EC-FOMC.** No member reads it. It is used only by the harness for D9.5a and D8's event
    window, because Topstep lists "FOMC Statement | 1:00 PM | All products" (F6).
  - **(d) EC-CP: NASS Crop Progress, weekly.**
    - Timing: "4:00 pm ET - Crop Progress" on Mondays (P-K6-039-a), that is "3:00 p.m. CT (4:00 p.m. ET)
      on the first business day of each week, April through November" (P-K6-049-b).
    - Source: ESMIS dated txt and pdf releases, back past 2017 (fetched above).
    - Used only by K6-ml-01 cp_ge_chg.
- **C10 EC-LIM: settlements and price limits.** D9.7 needs these for every K6 member, ports included.
  - **S(c, d)**, the official CME daily settlement of contract c on trade date d.
    - Source: CME settlements, for example the Databento GLBX.MDP3 statistics schema (settlement
      statistic). It is paid and **not in D13's plan**. No free source with 2019-2026 history was found
      in E.0 [unverified] (section 7, item 2).
    - Availability: after d's settlement (grains 13:15 CT, livestock 13:00 CT, plus publication lag;
      E.2 records the timestamp). A rule reads S(c, d-1) and S(c, d-2) only on d.
  - **L(p, d)**, the daily price limit of product p in force on d, and whether it is the expanded limit.
    - Grain limits are "reset for the first trade date in May and the first trade date in November"
      (P-K6-048-b). Each is a 45-day average settlement times a product percentage, "Corn is
      multiplied by 7%" (P-K6-048-a).
    - "Expanded price limits are approximately 50 percent higher than daily price limits and remain
      in place until no futures contracts settle at limit". Expansion is linked across the soybean
      complex and across Chicago and KC wheat (P-K6-048-c).
    - "Spot month contracts are not subject to price limits. In Grain and Oilseed contracts, price
      limits are removed on the business day prior to first notice day" (P-K6-048-d).
    - Levels as of 2026-09-08: corn $0.30, SRW wheat $0.45, soybeans $0.85, meal $20.00, oil $0.045,
      lean hog $0.0425, live cattle $0.0850. Expanded levels: $0.45, $0.70, $1.30, $30.00, $0.070,
      $0.0625, $0.1275 (P-K6-047-a, P-K6-047-b).
    - **E.2 builds the historical limit table for 2019-2026** from CME's notices (dated, through
      Wayback), including the expanded state, the linkages and livestock limit changes. Limits
      change over time, so no 2026 level is used for an earlier date.
  - Limit prices: U(c, d) = S(c, d-1) + L(p, d) and D(c, d) = S(c, d-1) - L(p, d).
- **C11 Frequency (arithmetic from calendar counts, no price data).**
  - Research window 2025-04-01..2026-06-19: about 300 grain and livestock trade dates. It holds about
    14 WASDE releases (15 monthly dates from April 2025 to June 2026, with no October 2025 entry in
    ESMIS) and about 3 Grain Stocks dates that are not WASDE dates (end of June, September, March).
  - Confirmation window 2019-05-06..2024-02-29: about 1,200 trade dates and 58 WASDE releases (May
    2019 to February 2024).
  - **Consequence.** A WASDE-day member trades on about 5% of dates, with zeros on the rest (D5). It
    needs a net P&L of about 20 x eps_X per event to reach eps_X per trade date, so it is a likely
    "null at eps" or "inconclusive by design" case (D4; lead ruling 21:52, Q4: the power check
    decides).
- **C12 Release-minute cost.**
  - D8's five sample dates are 2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11 and 2026-04-15. E.2
    checks whether any is an EC-USDA date. If none is, the grain 11:00 bucket is calibrated on
    non-release minutes.
  - Either way, D8's event-window rule charges every fill in [11:00, 11:30) on EC-USDA dates, and in
    [13:00, 13:30) on FOMC dates, the product's largest bucket. The same holds for the 07:30 Export
    Sales release, which no member trades.
  - Supporting evidence: the corn spread widens on report days, "USDA Grain Stock and Production-WASDE
    announcements significantly widen the BAS" (P-K6-021-b). Real-time releases bring "higher market
    liquidity costs" (P-K6-024-c).
- **C13 Price-limit proximity (D9.7) in K6.**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  - All seven products carry CME daily limits (P-K6-047-a). Topstep prohibits "Holding a position
    within 2% of a product's price lock limit" (F2.1). The harness encodes it: no entry, and an
    immediate exit, while the price is within 2% of U(c, d) or D(c, d).
  - This bites on report days. "prices reached a limit move only in about 2% of total observations"
    in crops, 4.4% in cattle and 8% in hogs, and "28.5% of the days with Hogs and Pigs report releases
    were subject to price limit moves" (P-K6-018-c, 1985-2018).
  - **Every member that holds across the 11:00 release** (CP2 and CP3 on grains, K6-crushgap-01,
    K6-wasdepre-01, K6-limitcont-01 on grain release days, K6-ml-01):
    - it is never in a position when the market is already locked or within the band before the
      release, because the entry guard blocks entry and the immediate exit closes a position when
      the price enters the band;
    - if the release itself carries the price into the band, the D9.7 exit fills at the first bar
      D9.5a allows, 11:02 at the earliest;
    - so the position can sit inside the band for up to about two minutes. This residual is common to
      the ports and is put to the lead (section 7, item 3). The arithmetic of "within 2%" is item 4.

---

## 1. Members

### K6-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording. R-03: on HE and LE, which have no overnight session, the trade date's first bar is the 08:30 open, so the signal is the first 30 minutes of the day session (the (b) form); D6 now says so; the two trials are kept.]
- **Cluster:** K6. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures** (each a separate trial): ZC, ZW, ZS, ZM, ZL, HE, LE. Each is traded only if D2
  admits the exposure. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** Port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log
  A10 and A28), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the
    trade date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in
    the signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after
    C-2 min (fills at the next open). Both signal bars must exist with one instrument_id, else no
    trade."
  - **K6 log.** No passed K6 item tests this family on a K6 product. Rosa's intraday momentum names no
    K6 product (R-K6-006), and the coffee intraday momentum paper is not a K6 product (R-K6-032). The
    port is not a duplicate of any cluster member.
- **Instantiated.**
  - **Grains (O 08:30, C 13:15, F 13:18).**
    - Signal: close of the bar at 08:59 minus the open of the trade date's first bar, the first bar
      at or after the 19:00 CT evening open before d (C3).
    - Entry: market intent on the bar at 12:44, filling at the 12:45 open.
    - Exit: market intent on the first bar at or after 13:13, filling nominally at the 13:14 open.
    - Hold 29 minutes; window 12:45-13:14.
  - **Livestock (O 08:30, C 13:00, F 13:03).**
    - Signal: the trade date's first bar is the 08:30 bar (C3), so the signal is the first half hour
      only: close of the 08:59 bar minus open of the 08:30 bar. The (a) form's overnight component
      does not exist for livestock (section 7, item 6).
    - Entry: market intent on the bar at 12:29, filling at 12:30.
    - Exit: market intent on the first bar at or after 12:58, filling at 12:59. Hold 29 minutes.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid, with history
  2019-05..2026-06. The latest signal input, the 08:59 bar, is available at 09:00 CT.
- **Order type:** market. **Sizing:** q = 1 (C6).
- **Parameters:** O+29, C-31 and C-2 from D6. **Grid:** none.
- **Expected entries and hold:** at most 1 per trade date, held 29 minutes. Floor (at most 20 entries
  a day, 2-minute minimum hold, 10-minute mean hold): ok.
- **Falsification:** the standard condition only (a port). UCB95 of the member's mean net daily P&L
  per contract below eps_X, at >= 80% achieved null power on the confirmation window, counts against
  it.
- **Topstep check:**
  1. Flat by F: last fill 13:14 (grains) or 12:59 (livestock).
  2. Order type: market.
  3. D9.4: one trade a day, no stops or brackets.
  4. Star: no K6 product is starred.
  5. News: on FOMC days the grain position spans the 13:00 statement ("All products", F6) at 1 lot,
     which F6.3 allows, and the 13:14 exit pays D8's event-window cost (C12). Livestock exits at
     12:59, before the statement.
  6. D9.5a: no fill falls in [13:00, 13:02) or [11:00, 11:02).
  7. Position limit: 1 lot-equivalent.
  8. D9.7: the harness guard applies (C13). The grain window 12:45-13:14 does not contain 11:00.
- **Data needed:** ohlcv-1m of each admitted K6 vehicle, research window 2025-04-01..2026-06-19 and
  confirmation window S_X..2024-02-29 (D4). External: EC-CAL, EC-LIM (for D9.7).
- **Trials in N:** 1 per admitted exposure (at most 7).

### K6-cp2-01 (core port CP2, opening-range breakout)
- **Cluster:** K6. **Products read:** own vehicle.
- **Traded exposures:** ZC, ZW, ZS, ZM, ZL, HE, LE, one trial each. Each is traded only if D2 admits
  it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** Port of MES B-H1 hold 75 (class C2), as fixed in D6 row CP2 with the 21:12 and 21:52
  amendments.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first bar
    opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market
    intent in the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes
    after the fill, or the engine's forced flatten at F if earlier."
  - "4 ticks of P" means 4 minimum increments of the exposure's most active contract (D6, ruling
    21:52). Each K6 exposure has one contract, so there is no ambiguity.
  - **K6 log:** no opening-range-breakout source on a K6 product was logged.
- **Instantiated.**
  - Opening range: the bars opening in [08:30, 08:45).
  - Eligible bars: those opening in [08:45, 13:15) for grains and [08:45, 13:00) for livestock.
  - Buffer: the table in C7 (ZC, ZW, ZS 0.01 USD/bu; ZM 0.40 USD/short ton; ZL 0.0004 USD/lb; HE and
    LE 0.001 USD/lb).
  - Entry: the first eligible bar whose close is >= OR_high + buffer buys, and one whose close is
    <= OR_low - buffer sells. One entry per trade date.
  - Exit: 75 minutes after the fill (the exit intent on the 75th bar after the entry-intent bar,
    filling at the next open), or F. For grains an entry filled after 12:03 is closed at F = 13:18;
    for livestock, after 11:48 at F = 13:03.
  - Holding horizon: up to 75 minutes. Session window 08:46-13:18 (grains) or 08:46-13:03
    (livestock).
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is known
  at 08:45 CT.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:** OR 15 minutes, buffer 4 ticks, hold 75 minutes (D6, a literal port). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held up to 75 minutes. Floor: see Topstep item 3.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F.
  2. Order type: market.
  3. D9.4: one trade a day, no stops. **Edge case for the lead** (section 7, item 5). On FOMC days a
     livestock entry intent on the 12:59 bar would fill at 13:00, which D9.5a defers to 13:02. That
     leaves one bar to F = 13:03, breaking D9.3(b)'s 2-minute minimum. The grain latest fill (13:15)
     still leaves three bars to F.
  4. Star: none.
  5. News: a grain position may span the 11:00 Crop Production release ("Crop Production | 11:00 AM
     | ZC, ZS, ZW, ZM, ZL", F6) at 1 lot, which F6.3 allows.
  6. D9.5a: a fill that would land in [11:00, 11:02) or [13:00, 13:02) is deferred to +2 min.
  7. Position limit: 1 lot-equivalent.
  8. D9.7: C13, including the release residual.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows;
  EC-CAL, EC-USDA, EC-FOMC (harness), EC-LIM.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K6-cp3-01 (core port CP3, prior-close location)
- **Cluster:** K6. **Products read:** own vehicle.
- **Traded exposures:** ZC, ZW, ZS, ZM, ZL, HE, LE. Each is traded only if D2 admits it.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** Port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6), as
  fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L
    over [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family
    H. CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market
    intent on the O bar of day d. Exit: first bar at or after C-2 min."
  - **K6 log.** A close at the daily limit has CLV = 1 (limit up) or 0 (limit down). Every
    K6-limitcont-01 trade is therefore a same-direction subset of CP3's trades, entered 14 minutes
    later. That is a correlated member, not a duplicate (see K6-limitcont-01 and section 7, item 8).
- **Instantiated.**
  - **Grains.** The daily bar is [08:30, 13:15): O_d is the 08:30 open, and C_d the close of the 13:14
    bar. The complete-day test requires the 08:30 and 13:14 bars, a date with no early halt, and one
    instrument_id over [08:30, 13:15). Entry: market intent on the 08:30 bar of d, filling at the
    08:31 open. Exit: first bar at or after 13:13, filling at 13:14. Hold about 283 minutes.
  - **Livestock.** The daily bar is [08:30, 13:00), with C_d the close of the 12:59 bar. Entry fills
    at 08:31. Exit: first bar at or after 12:58, filling at 12:59. Hold about 268 minutes.
  - **Instrument guard:** d-1's daily bar carries the instrument_id of d's 08:30 bar.
  - **CLV cuts:** non-strict 0.8 and 0.2 (H6).
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's bar
  is complete at 13:15 CT (grains) or 13:00 CT (livestock) on d-1.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:** CLV cuts 0.2 and 0.8, lookback 1 (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 4.5 hours. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 13:14 or 12:59.
  2. Order type: market.
  3. D9.4: the grain entry fills one minute after the 08:30 reopen that follows the pause. It is a
     market order in a two-sided reopened market, not a stray-fill strategy (section 7, item 12).
  4. Star: none.
  5. News: grains hold through the 11:00 release on EC-USDA days, and every product holds through
     13:00 on FOMC days, at 1 lot (F6.3).
  6. D9.5a: no fill in a guard window.
  7. Position limit: 1 lot-equivalent.
  8. D9.7: C13. The day after a limit close is where CP3 is most exposed to the band, since it buys
     after limit-up closes.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows;
  EC-CAL, EC-LIM.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K6-crushgap-01 (soybean crush: the overnight gap in the processing margin reverses in the day session; single-leg)

> [Lead ruling, 01:52 PDT 2026-09-24, on this writer's question 1: traded on ZS ONLY (1 trial); ZM and ZL removed. The evidence is about the crush spread, and a spread cannot meet the 1-lot cap; the most liquid leg is kept. Where this entry says ZM or ZL are traded, read ZS only.]
- **Cluster:** K6. **Products read:** ZS, ZM and ZL bars (all three are needed for the margin); EC-CAL.
- **Traded exposures** (each a separate trial, one leg per trial): ZS, ZM, ZL. Each is traded only if
  D2 admits it. The other two legs are read even if not admitted (C8). **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism.**
  - **What is claimed** (K6-001, full text; pit era 1978-1991).
    - The gross processing margin (GPM = meal and oil value minus beans) reverses at the open. "If
      the GPM on the open is less (greater) than the previous day's close, a reverse crush (normal
      crush) spread is placed. In all cases, the position is liquidated on the close of the same day"
      (P-K6-001-a).
    - The GPM's open-to-close change and its close-to-open gap correlate at -0.49 (1978-1987) and
      -0.43 (1987-1991) (P-K6-001-d).
    - "the GPM at the opening tends to be lower than the previous close and then 'trade up' during the
      day" (P-K6-001-e).
    - Net of 1.5 cents per bushel round-trip costs (P-K6-001-b), the mean profit per trade at filters
      of 0 / 1 / 2 / 3 cents is "-0.36 0.35 1.02 1.74", over "3352 1861 922 457" trades (P-K6-001-f).
  - **Why it should survive the modern session** (reasoned from K6-026). In 2015 one-minute data, "A
    high level of cointegration is indeed observed during session 2 trading hours, which fades away
    during session 1" (P-K6-026-c). Session 2 is 8.30 AM to 1.20 PM and session 1 the 7 PM to 7.45 AM
    electronic session (P-K6-026-b). A margin that drifts from equilibrium overnight and is pulled back
    in the day session is the pattern K6-001 trades.
  - **Direction.** From P-K6-001-d and P-K6-001-e: after a GPM gap down, the day-session GPM change is
    expected positive. The position that gains is long GPM, that is long meal, long oil and short
    beans. This agrees with the source's "reverse crush" after a gap down.
  - **The single-leg step** (an inference, untested by any source).
    - A spread position is not allowed (D9.5; section 2, X-01 and X-02), so each leg is traded alone,
      in its GPM-reversal direction.
    - The claim tested is that a leg carries part of the documented spread reversal. The leg's own
      directional move, which the GPM gap does not predict, is noise in this test.
    - The source does not say which leg adjusts, so all three are tested (3 trials). Section 7, item 1
      gives the lead the 1-trial alternative.
  - **Evidence limits and against.**
    - Pit-era prints ("small unrepresentative trades occurring at the open", log quality tells).
    - Floor-trader costs, strongly year-dependent profits, and filters with no out-of-sample split
      (log quality tells).
    - K6-026 finds that "Hardly any cointegration was detected using Johansen's approach"
      (P-K6-026-e), and has one year of data (P-K6-026-d).
    - Simon's reversion to "its most recent 5-day average" (P-K6-008-a) and Mitchell's "Winning trades
      are significantly shorter" (P-K6-044-a) are abstracts only and support reversion in general.
  - **Classification:** new to the program (an inside-K6 spread signal; the log tags the
    opening-reversal element as a spread version of D.1 family C).
- **Margin definition.**
  - GPM = 0.022 x P_ZM + 11 x P_ZL - P_ZS, in USD per bushel, with P_ZM in USD per short ton, P_ZL in
    USD per pound and P_ZS in USD per bushel.
  - Each is converted from GLBX.MDP3's raw units by the contract specification (C7). E.2 confirms the
    units.
  - The weights come from CME: "11 pounds of soybean oil, 44 pounds of 48 percent protein soybean
    meal" per 60-lb bushel (P-K6-050-a), and 44/2000 = 0.022.
  - CME's quoted formula, "[(Price of Soybean Meal ($/short ton) x .022) + Price of Soybean Oil (¢/lb)
    x 11] – Price of Soybeans ($/bu.)" (P-K6-050-b), puts the oil term in cents. The unit-consistent
    form above uses USD per pound.
  - K6-001 used 48 lb of meal. The current 44 lb is used here (log note to K6-050).
  - **Contract months.** Each leg uses its own vehicle's contract under E.2's roll convention, so the
    months may differ (for example November soybeans against December meal and oil). The signal is
    the change of the GPM from one close to the next open, in which a fixed inter-month difference
    cancels, so the mismatch is accepted (section 7, item 10).
- **Signal.** G(d) = GPM_open(d) - GPM_close(d-1).
  - GPM_close(d-1) uses the closes of the three 13:14 bars of the previous grain trade date d-1 in
    EC-CAL.
  - GPM_open(d) uses the opens of the three 08:30 bars of d.
  - For each leg, its 13:14 bar on d-1 and its 08:30 bar on d must exist and carry the same
    instrument_id. Otherwise there is no trade on d.
- **Entry rule.**
  - If G(d) <= -0.02: on the traded leg, BUY ZM, BUY ZL, or SELL ZS.
  - If G(d) >= +0.02: SELL ZM, SELL ZL, or BUY ZS.
  - Otherwise no trade.
  - Market intent on the 08:30 bar of d, filling at the 08:31 open.
- **Exit rule:** market intent on the first bar at or after 13:13, filling at the 13:14 open.
- **Holding horizon:** about 283 minutes. **Session window:** 08:31-13:14 CT. Flat by F.
- **Data fields read:**
  - ZS, ZM and ZL ohlcv-1m open, close and instrument_id (C8). Paid, with 2019-05..2026-06 history.
    The d-1 inputs are available at 13:15 CT on d-1, and the 08:30 bars at 08:31 CT on d.
  - EC-CAL, known in advance.
- **Order type:** market. **Sizing:** q = 1 of the traded leg.
- **Parameters.**
  - Weights 0.022 and 11 (P-K6-050-a, P-K6-050-b).
  - **Filter 0.02 USD/bu (2 cents per bushel).** P-K6-001-f: the 1, 2 and 3 cent filters are all
    positive net. The middle value is a judgment. The 3-cent filter's larger mean is deliberately not
    chosen, to avoid taking the best in-sample value.
  - Anchor at the previous close, entry at the open, exit at the close (P-K6-001-a). The pit open and
    close map to the 08:30 day open and the C-1 (13:14) bar, as in CP3 (judgment).
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per trade date per leg, held about 4.7 hours.
  - Frequency is unknown for 2019-2026. In the source, the 2-cent filter traded 922 of 3,352 days
    (P-K6-001-f), about 28%. Today's overnight session and price levels may change that; E.2
    measures it on the research window.
  - Floor ok.
- **Falsification.**
  - The standard condition, per traded leg.
  - **Sign check (reported beside the verdict, not a separate test):** the mean over trades of
    w_leg x (-sign(G)) x (open of the 13:14 bar - open of the 08:31 bar), in the leg's ticks, is
    positive, where w_leg = +1 for ZM and ZL and -1 for ZS.
  - **Diagnostic (reported):** on eligible days, corr(G(d), GPM at the 13:14 open minus GPM at the
    08:31 open). The mechanism predicts it is negative (the source's -0.49 and -0.43, P-K6-001-d). A
    negative spread correlation with a failing leg would locate the failure in the single-leg step,
    not in the mechanism.
- **Topstep check:**
  1. Flat by F: last fill 13:14.
  2. Order type: market.
  3. D9.4: one trade a day, no stops. The entry is one minute after the 08:30 reopen, as in CP3
     (section 7, item 12).
  4. Star: none.
  5. News: holds through the 11:00 Crop Production release on EC-USDA days at 1 lot. ZS, ZM and ZL
     are all on Topstep's Crop Production row. F6.3 allows it.
  6. D9.5a: no fill in a guard window.
  7. Position limit: 1 contract, never two legs.
  8. D9.7: the entry guard applies to the traded leg at 08:31. Expanded limits are linked across the
     soybean complex (P-K6-048-c), so E.2's table must carry the linkage. The release residual is in
     C13.
- **Data needed:** ohlcv-1m of ZS, ZM and ZL (all three, whichever is traded) over the research and
  confirmation windows; EC-CAL, EC-LIM.
- **Trials in N:** 1 per admitted leg among ZS, ZM and ZL (at most 3).

### K6-limitcont-01 (day after a limit close: day-session continuation in the limit direction)

> [Lead ruling, 01:52 PDT, question 6: traded on HE and LE ONLY (2 trials); the five grain exposures removed. Its trades are largely a subset of CP3's, so the grain trials add little information. Where this entry lists grain exposures, read HE and LE only.]
- **Cluster:** K6. **Products read:** the traded vehicle; EC-LIM (settlements and limit table);
  EC-CAL.
- **Traded exposures** (each a separate trial): ZC, ZW, ZS, ZM, ZL, HE, LE. The source's nine
  commodities include "soybean oil (BO), corn (C), ... live cattle (LC), lean hogs (LH), soybean (S),
  soybean meal (SM), and soft red winter wheat (W)" (P-K6-002-e). Each is traded only if D2 admits
  it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed.**
    - "Consistent with delayed price discovery, returns continue in the same direction after limit
      days and do not reverse after one week, whereas returns are small after large price moves that
      do not hit limits" (P-K6-002-a).
    - "For limit up days, the average return on the following day is 40 to 62 basis points, and for
      limit down days, the average return on the following day is -38 to -63 basis points"
      (P-K6-002-b; P-K6-002-c). These are close-to-close, 1991-2016 (P-K6-002-e), over 2,063 limit ups
      and 2,393 limit downs (P-K6-002-f).
    - Park (abstract only, contracts unnamed): "prices continue to rise on average the day after an
      up-limit day" (P-K6-003-a).
  - **What the program can hold, and the evidence against.**
    - The next day's open-to-close part, which is all a day-session rule can hold, is not reported
      [unverified].
    - The one split the source gives points the other way. "a 1% increase in the return calculated
      from limit day close to options-implied prices is associated with a 0.76% increase in the
      close-to-open futures returns, and 0.15% increase in the close-to-close futures returns"
      (P-K6-002-d). If both coefficients come from the same events (not stated), then on that
      regressor the open-to-close part is 0.15 - 0.76 = -0.61. The day session would then partly
      reverse what the open priced.
    - After a lock in LE and HE, price limits "add to the high uncertainty that precedes the limit
      move, leading to significantly higher volatility and lower liquidity when trading resumes"
      (P-K6-035-a, abstract).
    - Limit sizes have changed since the sample: they are now reset semi-annually (P-K6-048-a,
      P-K6-048-b). The 1991-2016 frequency does not carry over.
  - **Classification:** new to the program (limit state).
  - **Relation to CP3:** every trade is a same-direction subset of K6-cp3-01's trades (C13; section
    7, item 8). The distinguishing claim is the limit itself: P-K6-002-a contrasts limit days with
    large moves that do not hit the limit.
- **Event.** Trade date d whose previous trade date d-1 closed at the limit for contract c, the
  contract of d's 08:30 bar:
  - limit-up close: S(c, d-1) = S(c, d-2) + L(p, d-1);
  - limit-down close: S(c, d-1) = S(c, d-2) - L(p, d-1);
  - where L is the limit in force on d-1 (expanded where in force), from EC-LIM (C10).
  - A contract without a limit on d-1 (P-K6-048-d) does not qualify.
- **Entry rule:** market intent on the bar at 08:44, filling at the 08:45 open. BUY after a limit-up
  close; SELL after a limit-down close. The D9.7 entry guard applies.
- **Exit rule:** market intent on the first bar at or after C-2 (grains 13:13, filling at 13:14;
  livestock 12:58, filling at 12:59), or earlier by D9.7's immediate exit.
- **Holding horizon:** about 269 minutes (grains) or 254 minutes (livestock). **Session window:**
  08:45-13:14 or 08:45-12:59. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m open and instrument_id (C8). Paid, 2019-05..2026-06. The 08:44 bar is available
    at 08:45 CT.
  - S(c, d-1) and S(c, d-2): official settlements (C10). Paid, not yet in D13. Available after d-1's
    settlement, before d's 08:30 open.
  - L(p, d-1) and the expanded state: the CME limit table E.2 builds (C10; free CME notices, dated).
    Known before d-1.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters.**
  - **Entry at 08:45 (O + 15), a judgment.** It avoids the first 15 minutes after the day open, where
    the lock-release illiquidity (P-K6-035-a) and the open's concentration of quotes (P-K6-023-c,
    LE) fall. It also stays clear of the D9.4 "gapped markets" clause. The source measures
    close-to-close, which gives no intraday entry time.
  - **Exit at C-2:** the port convention. The source's horizon is the next day's close (P-K6-002-b).
  - **Limit close:** exact equality of the settlement with the limit price (judgment: the source's
    limit days are closes at the limit, per the log's mechanism line). E.2 applies CME's settlement
    rounding.
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per qualifying day.
  - The 2019-2026 frequency is unknown (variable limits since the source's sample).
  - Upper-bound guide: a limit move on about 2% of crop days, 4.4% of cattle days and 8% of hog days
    (P-K6-018-c, 1985-2018, "reached a limit move", which may count intraday touches). That is at most
    about 6, 13 and 24 events per product in the research window, and about 24, 53 and 96 in the
    confirmation window.
  - Grains will likely be "inconclusive by design" at D4's power check (section 7, item 7).
  - Floor ok.
- **Falsification.**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean of direction x (open at the exit fill - open at the entry
    fill), in ticks, is positive over qualifying days. It is reported with the event count per
    exposure.
  - **Also reported:** the mean close-to-open part, S(c, d-1) to d's 08:30 open, in the same
    direction. The source's continuation may lie there, outside the member's hold.
- **Topstep check:**
  1. Flat by F.
  2. Order type: market.
  3. D9.4: one entry, 15 minutes after the day open. It never trades on the lock day itself or at a
     lock's reopening (X-12).
  4. Star: none.
  5. News: on grain EC-USDA days the hold spans 11:00 at 1 lot (F6.3).
  6. D9.5a: fills at 08:45, 13:14 and 12:59 are outside the guard windows.
  7. Position limit: 1 lot-equivalent.
  8. **D9.7.** The day after a limit close is exactly when the price may sit near the (expanded)
     limit. The entry guard blocks an 08:45 entry within 2% of U(c, d) or D(c, d), and the immediate
     exit applies afterwards. E.2 builds the historical limit table with the expanded state and its
     linkages (P-K6-048-c). The release residual on grain EC-USDA days is in C13.
- **Data needed:** ohlcv-1m of the admitted vehicles over the research and confirmation windows.
  External: settlements (C10), the CME limit table, EC-CAL.
- **Trials in N:** 1 per admitted exposure (at most 7).

### K6-wasdepre-01 (WASDE day: the day-session drift before the 11:00 CT release continues through it)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP: K6-027's sample window is not recorded (a 2026 paper); treated as overlapping until E.1 records it. R-10: the D9.7 "release residual" text in this entry is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard.]
- **Cluster:** K6. **Products read:** the traded vehicle; EC-WASDE; EC-CAL.
- **Traded exposures** (each a trial): ZC and ZS, the products of the source ("U.S. corn and soybean
  ending stock data and relevant corn and soybean futures", P-K6-027-a). Each is traded only if D2
  admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed.**
    - "directionally correct drift prior to release suggests that we also observed informed trading
      and/or superior internal research" (P-K6-027-a, WASDE, abstract only; its window and magnitudes
      are [unverified]).
    - "we provide evidence that informed trading exists in commodity markets before the release date"
      (P-K6-043-a, WASDE, abstract only; the horizon is likely daily).
    - "Other more subtle reactions occur in the last trading session before USDA announcements as
      traders adjust their market exposure in anticipation of the release" (P-K6-015-b, corn,
      2009-2012).
  - **The rule-3 route.** The surprise itself needs proprietary polls (P-K6-049-e), so it is observed
    through price. The reasoning:
    1. If informed trading moves the price toward the not-yet-public number before the release, the
       sign of the day-session move before the release carries the sign of the coming surprise.
    2. The release response has the surprise's sign: "a 1% larger-than-expected USDA production
       surprise is followed by a reduction in futures price of about 1.1%" (P-K6-011-a).
    3. So a position in the direction of the pre-release drift, held across the release, collects the
       rest of the drift and the release response.
  - **Evidence limits.**
    - K6-027 and K6-043 are abstracts. K6-027's venue and peer-review status are [unverified], and its
      sample may overlap the confirmation window [unverified] (section 7, item 11).
    - The logged efficiency results, "little evidence exists to support systematic under‐ or
      overreactions" (P-K6-015-b) and "Return correlations provide little evidence to support
      systematic under- or overreaction" (P-K6-014-b), concern returns after the release. They do not
      test the pre-release drift, so they neither support nor contradict it.
  - **Classification:** port of D.1 family E (pre-release window), grain-specific. D6 does not port
    family E, so this is a cluster member.
- **Event set:** EC-WASDE dates (C9a), T = 11:00 CT. WASDE and Crop Production share every date.
- **Signal:** Dr = close of the vehicle's bar at 10:29 minus the open of its bar at 08:30, in ticks.
  Both bars must exist with one instrument_id. Dr = 0 means no trade.
- **Entry rule:** market intent on the bar at 10:29, filling at the 10:30 open, in the direction of
  sign(Dr).
- **Exit rule:** market intent on the bar at 11:14, filling at the 11:15 open.
- **Holding horizon:** 45 minutes. **Session window:** 10:30-11:15 CT. Flat by F.
- **Data fields read:**
  - Vehicle ohlcv-1m open, close and instrument_id (C8). Paid. The inputs are available at 08:31 and
    10:30 CT.
  - EC-WASDE date. Free; the USDA schedule and ESMIS record have 2019-2026 history (C9a). Known before
    d.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters.**
  - **Drift window 08:30-10:29, a judgment.** It is the day session, which "contains the most trading
    activity" (P-K6-026-b), up to 30 minutes before the release. The source's drift window is
    [unverified].
  - **Entry 30 minutes before the release, a judgment.** It precedes the pre-release volatility rise
    "between 20 and 10 minutes before the report release" (P-K6-029-a), so the entry fill is not in
    that window.
  - **Exit at T + 15.** Reactions "persist for approximately ten minutes" (P-K6-015-b). In-session
    releases produce a spike "for five to six minutes" (P-K6-014-a). T + 15 is after both and clear of
    D9.5a.
  - **Sign only, with no threshold** (judgment, as CP1).
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per WASDE date: about 14 research and 58 confirmation
  events (C11), about 5% of trade dates. Held 45 minutes. Floor ok.
- **Falsification.**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(Dr) x (open of the 11:15 bar - open of the 10:30 bar),
    in ticks, is positive.
  - **Reported split:** the pre-release part (10:30 to the 11:00 open) and the release part (the 11:00
    open to 11:15).
- **Topstep check:**
  1. Flat by F: last fill 11:15.
  2. Order type: market.
  3. D9.4: entry 30 minutes before and exit 15 minutes after the release. No fill in a release minute,
     no gapped-market entry.
  4. Star: none.
  5. News: holds through the Crop Production and WASDE release at 1 lot ("Crop Production | 11:00 AM
     | ZC, ZS, ZW, ZM, ZL", F6). F6.3 prohibits only full maximum size.
  6. D9.5a: no fill in [11:00, 11:02) by construction. The 11:15 exit pays D8's event-window cost
     (C12).
  7. Position limit: 1 lot-equivalent.
  8. **D9.7.** The 10:30 entry is blocked when the price is within 2% of U or D, so the member is never
     in when the market is near its limit before the release. If the release carries the price into
     the band (report-day locks: P-K6-011-e; P-K6-018-c), the immediate exit fills at 11:02 at the
     earliest (C13; section 7, item 3).
- **Data needed:** ohlcv-1m of ZC and ZS over the research and confirmation windows; EC-WASDE,
  EC-CAL, EC-LIM.
- **Trials in N:** 1 per admitted exposure among ZC and ZS (at most 2).

### K6-wasdepost-01 (WASDE day: corn continues its release response to the close)
- **Cluster:** K6. **Products read:** ZC; EC-WASDE; EC-CAL.
- **Traded exposure:** ZC only, the source's product (K6-037 is corn). Traded only if D2 admits it.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed.**
    - "the USDA's influence on corn prices remains embodied in corn futures for several days after
      the release of USDA's WASDE report" (P-K6-037-a). Lag dummies for days 2-4 are used
      (P-K6-037-c). This is daily OHLC, 1999-2017 (P-K6-037-d), and the open-to-close part is not
      separated.
    - "unconditional elasticities that are persistently below unity, consistent with incomplete
      post-report alignment of trader expectations" (P-K6-028-b, abstract, corn, 2013-2020).
    - Reasoning: if the adjustment to the WASDE news is incomplete at the end of the release window,
      the rest of the day session continues the release response.
  - **Evidence against (the balance of the log predicts a null).**
    - "on average, corn market prices respond to USDA news and those prices tend to remain at about
      the level of the initial response over the next two trading weeks" (P-K6-011-d, August reports
      2009-2019, figure-based).
    - "little evidence exists to support systematic under‐ or overreactions in prices" (P-K6-015-b).
    - "Return correlations provide little evidence to support systematic under- or overreaction"
      (P-K6-014-b, soybeans).
    - The member tests the null at the funnel's bar.
  - **Classification:** port of D.1 family E (the E-H2 post-release momentum form), corn-specific,
    as a cluster member.
- **Event set:** EC-WASDE dates, T = 11:00 CT.
- **Signal:** R = close of the ZC bar at 11:14 minus close of the ZC bar at 10:59, in ticks. Both bars
  must exist with one instrument_id. R = 0 means no trade.
- **Entry rule:** market intent on the bar at 11:14, filling at the 11:15 open, in the direction of
  sign(R).
- **Exit rule:** market intent on the first bar at or after 13:13, filling at the 13:14 open.
- **Holding horizon:** about 119 minutes. **Session window:** 11:15-13:14 CT. Flat by F.
- **Data fields read:** ZC ohlcv-1m close, open and instrument_id (C8). Paid. The signal is available
  at 11:15 CT. EC-WASDE is free and known before d.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters.**
  - **Response window from the T - 1 to the T + 14 bar close, a judgment.** It covers the spike
    (P-K6-014-a) and the ten-minute reaction (P-K6-015-b), and ends where K6-wasdepre-01 exits.
  - **Exit at C-2:** the port convention. The source's horizon is several days, and the day-session
    remainder is what the program can hold.
  - **Grid:** none.
- **Expected entries and hold:** at most 1 per WASDE date: about 14 research and 58 confirmation
  events. Held about 2 hours. Floor ok.
- **Falsification.**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(R) x (open of the 13:14 bar - open of the 11:15 bar),
    in ticks, is positive.
- **Topstep check:**
  1. Flat by F: 13:14.
  2. Order type: market.
  3. D9.4: entry 15 minutes after the release, after the spike, not in a gapped market.
  4. Star: none.
  5. News: 1 lot. The position spans 13:00 on the rare dates that are both WASDE and FOMC dates (E.2
     counts them).
  6. D9.5a: the 11:15 entry is outside [11:00, 11:02) but inside D8's 30-minute event window, so it
     pays the largest bucket.
  7. Position limit: 1 lot-equivalent.
  8. **D9.7.** The entry guard blocks the 11:15 entry when the release has moved the price within 2%
     of the limit, the kind of day in P-K6-011-e ("the market locked limit down"). The member never
     enters a near-limit market. The largest-response days are therefore excluded by construction,
     and the reported sign check states how many were.
- **Data needed:** ohlcv-1m of ZC over the research and confirmation windows; EC-WASDE, EC-CAL, EC-LIM.
- **Trials in N:** 1.

### K6-ovr-01 (hourly overreaction reversal in grains)

> [EXCLUDED by the lead, 01:52 PDT, question 6: no grain-specific result is logged and one logged source argues against it (K6-025). Moved to the excluded list; 0 trials. The entry is kept below for the record only.]
- **Cluster:** K6. **Products read:** the traded vehicle; EC-USDA; EC-CAL.
- **Traded exposures** (each a trial): ZW, ZC, ZS, ZL, the K6 products in the source's sample:
  "wheat (W), corn (C), soybeans (S), soybean oil (BO)" (P-K5-029-b [K6]). Soybean meal and livestock
  are not in the sample and are not traded. Each is traded only if D2 admits it. **Vehicle:** D2
  (chosen in E.2).
- **Mechanism.**
  - **What is claimed.** K5-029 is a panel source; its [K6] passages are in the K5 log.
    - It examines "the overreaction behavior of 20 commodity futures based on intraday data"
      (P-K5-029-a [K6]).
    - Method: large intraday price changes beyond a decile threshold, at 1-minute to 1-hour
      frequencies, are followed by reversals (K5 log mechanism line). The decile and 1-hour wording
      is in P-K5-029-c ("first decile overreactions for the 1-h frequency"), which is tagged [K5] and
      [K4]. It is used here for the method only, not as a grain result.
    - Costs: "As transaction costs in futures trading are negligible, the net-of-fees trading results
      would be still positive in both periods" (P-K5-029-d [K6]).
  - **Evidence limits.**
    - No grain-specific result is in the verified passages. The abstract ranks "soft and metal
      commodities" below "precious metals and especially energy commodities" and does not rank
      grains (P-K5-029-a).
    - The data are six months, Covid-dominated (2019-11-20..2020-06-03), inside the confirmation
      window.
    - The holding period is [unverified]. Costs are asserted, not modelled.
  - **Evidence against, for ZC.**
    - Flash events in corn and lean hogs "are heavily influenced by unanticipated changes in
      fundamentals that may lead to a new equilibrium price" (P-K6-025-a, abstract).
    - About two thirds of corn 5-minute jump clusters have no same-day news (P-K6-033-a). There is no
      reversal test either way.
  - **Classification:** port of D.1 family C (magnitude-conditioned reversal), tested
    product-specifically. D6 does not port family C, so this is a cluster member.
- **Decision times:** t in {09:30, 10:30, 11:30, 12:30} CT. These are the four whole hours after
  O = 08:30 whose 40-minute hold ends before C-2.
  - On EC-USDA dates the 10:30 and 11:30 decisions are skipped: their holding or signal interval
    contains the 11:00 release and D8's event window.
  - Reason (judgment): the logged report responses are efficient (P-K6-014-b, P-K6-015-b), which is
    a different mechanism from overreaction.
- **Signal:** r(t) = (close of the bar at t - 1 - open of the bar at t - 60) / open of the bar at
  t - 60. Both bars must exist with one instrument_id, and the denominator must be > 0.
- **Reference set and cuts.**
  - The reference set is r(tau) at the same four clock times on the 20 most recent earlier eligible
    trade dates (full sessions in EC-CAL, not roll-blackout), excluding skipped (tau, date) pairs.
  - At least 60 values are required, else no trade at t.
  - P10 and P90 = np.percentile(values, [10, 90], method="linear").
  - Warm-up: the first 20 eligible dates of each window. Holdout-2 is sealed, so no earlier bars are
    used.
- **Entry rule:** r(t) <= P10 means BUY; r(t) >= P90 means SELL; otherwise no trade. Market intent on
  the bar at t - 1, filling at the open of the bar at t.
- **Exit rule:** market intent on the bar at t + 39, filling at the open of t + 40. At most one
  position is open; the next entry fills at t + 60.
- **Holding horizon:** 40 minutes. **Session windows:** 09:30-10:10, 10:30-11:10, 11:30-12:10 and
  12:30-13:10 CT. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8), all closed at or before
  t; EC-USDA; EC-CAL. All free except the bars.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters.**
  - 60-minute signal: the source's 1-hour frequency.
  - P10 and P90: the source's decile (P-K5-029-c, method).
  - **20-date reference, a judgment:** the program's trailing-state length (D15.4 B4). The source's
    threshold construction is not in the logged passages.
  - **40-minute hold, a judgment:** the longest uniform hold at which the 12:30 position is flat by
    13:10, before C-2 and F. The source's holding period is [unverified].
  - The EC-USDA skip rule (above).
  - **Grid:** none.
- **Expected entries and hold:** if the trailing distribution is stable, about 20% of eligible
  decisions qualify, about 0.8 entries per day per exposure (at most 4; at most 2 on EC-USDA dates).
  Held 40 minutes. Floor ok.
- **Falsification.**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean of -sign(r(t)) x (open at t + 40 - open at t), in ticks, is
    positive.
- **Topstep check:**
  1. Flat by F: last fill 13:10.
  2. Order type: market.
  3. D9.4: at most 4 entries a day, 40-minute holds, no stops. Not scalping.
  4. Star: none.
  5. News: the 12:30 position spans the 13:00 FOMC statement on FOMC days at 1 lot. No position spans
     11:00 on EC-USDA dates.
  6. D9.5a: fills fall at :30 and :10, never in [11:00, 11:02) or [13:00, 13:02). The 13:10 exit on
     FOMC days pays D8's event-window cost.
  7. Position limit: 1 lot-equivalent.
  8. D9.7: a large hourly move can end near the limit. The entry guard blocks entry within 2% (C13).
- **Data needed:** ohlcv-1m of the ZW, ZC, ZS and ZL vehicles over the research and confirmation
  windows; EC-USDA, EC-CAL, EC-LIM.
- **Trials in N:** 1 per admitted exposure among ZW, ZC, ZS and ZL (at most 4).

### K6-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> **[EXCLUDED: superseded by the Stage E ML route (user decision 2026-09-24, U6). Stage E.1.
> The text below stays visible for the record. This entry is not a Stage E member and adds 0
> trials; the ML route (docs/STAGE_E_ML_DESIGN.md) is separate.]**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: fallback order declared now (D1 ADV order): ZC, ZS, ZL, ZM, ZW, LE, HE; if none is admitted, no ML member. Features unchanged. R-11 (NOTE): the first decision time that cannot trade is dropped from the decision grid by D15.3's row rule.]
- **Traded vehicle: corn, ZC** (D2 chosen in E.2; ZC is the exposure's only contract).
  - **Reason:** corn is the K6 product the log documents most at intraday and release horizons:
    K6-006, 010, 011, 015, 016, 017, 018, 021, 024, 025, 027, 028, 029, 030, 031, 033, 034, 037 and
    045, against about twelve soybean items and six livestock items. It also has the cluster's highest
    public ADV (505,663, 2026 Jan-Aug; D1 table).
  - **No fallback is declared.** The features are corn-specific (the ZC limit state and corn Crop
    Progress). If D2 does not admit ZC, the lead decides.
- **Products the features read:**
  - ZC, and ZS bars. ZS is needed as a leg even if soybeans are not admitted; E.2 then buys its
    history (C8).
  - Calendars: EC-USDA, EC-CAL.
  - EC-LIM (settlements and limit table, C10) and EC-CP (NASS Crop Progress, C9d).
- **Cluster features.** There are 7; with D15.4's B1-B5 that makes 12. Throughout, t_j is the decision
  time, "the bar at t_j - 1" is the last bar closed at t_j, and tick is ZC's 0.0025 USD/bu unless
  stated.

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | usda_phase | If d is an EC-USDA date: -1 if t_j < 11:00, +1 if t_j >= 11:00. If d is not: 0 | K6-038 P-K6-038-a, P-K6-038-b; K6-040 P-K6-040-a, P-K6-040-b; K6-049 P-K6-049-a, P-K6-049-c (schedule, 11:00 CT); K6-029 P-K6-029-a (effects begin before the release and "last till the end of the trading session"); K6-027 P-K6-027-a (pre-release drift) | schedule known before d (C9a); depends on the clock only |
| KF2 | usda_resp | If d is an EC-USDA date and t_j >= 11:14: (close of the ZC bar at 11:13 - close of the ZC bar at 10:59) / tick. Otherwise 0. On such a d with t_j >= 11:14, a missing bar or a change of instrument_id means no trade at t_j | K6-011 P-K6-011-a, P-K6-011-d; K6-037 P-K6-037-a; K6-015 P-K6-015-b ("persist for approximately ten minutes"); K6-014 P-K6-014-a (spike of five to six minutes) | 11:14 CT (close of the bar at 11:13) |
| KF3 | zs_ret30 | (close of the ZS bar at t_j - 1 - open of the ZS bar at t_j - 30) / 0.0025, in ZS ticks. Both bars must exist with one ZS instrument_id, else no trade at t_j | K6-029 P-K6-029-c ("Efficient return correlations increase right after announcement and remain about 50% higher than regular days till the end of the session"), P-K6-029-b | ZS bars closed <= t_j |
| KF4 | lim_pos | (close of the ZC bar at t_j - 1 - S(c, d-1)) / L(ZC, d), where c is the contract traded at t_j and L the limit in force on d (expanded where in force). It lies in [-1, 1] inside the band. If no limit applies to c on d (P-K6-048-d), no trade at t_j | K6-036 P-K6-036-a (tighter limits raise the chance an extreme move ends at the limit, "Magnet"), P-K6-036-b (volume concentrates before a limit hit); K6-047 P-K6-047-a, P-K6-047-b; K6-048 P-K6-048-a to P-K6-048-d (levels, resets, expansion) | S(c, d-1) after d-1's settlement (C10); L from E.2's dated limit table, known before d; bar closed <= t_j |
| KF5 | prev_limit | +1 if S(c, d-1) = S(c, d-2) + L(ZC, d-1); -1 if S(c, d-1) = S(c, d-2) - L(ZC, d-1); else 0. c is the contract traded on d; settlements exist for every listed month | K6-002 P-K6-002-a, P-K6-002-b, P-K6-002-c; K6-003 P-K6-003-a | after d-1's settlement (C10), before d's first decision |
| KF6 | cp_ge_chg | On the first grain trade date whose session opens after an EC-CP release (the 19:00 CT open that follows the 15:00 CT release): the national corn condition's (good + excellent) percentage this week minus the same last week, in percentage points, both as printed in that release's corn condition table (not a later revision). 0 on every other trade date, and when the release carries no corn condition table | K6-034 P-K6-034-a (released after the session, "before the subsequent trading session opens"), P-K6-034-b (the reaction is in the close-to-open return), P-K6-034-c (strongest in July and August); K6-039 P-K6-039-a; K6-049 P-K6-049-b | 15:00 CT on the release date (ESMIS txt; free, dated, 2019-2026 history, C9d) |
| KF7 | pre_usda | 1 if the next trade date in EC-CAL is an EC-USDA date, else 0 | K6-015 P-K6-015-b ("the last trading session before USDA announcements as traders adjust their market exposure"); K6-043 P-K6-043-a ("informed trading exists ... before the release date") | schedule known in advance |

- **Decision window [W0, W1] = [08:44, 12:44] CT; horizon h = 30 minutes.**
  - **Decision times:** t_j = 08:44, 09:14, ..., 12:44, which is 9 a day. W1 + h = 13:14 <= F = 13:18.
  - **Fills:** by D15.3's convention a position runs from the open of t_j + 1 to the open of
    t_j + 30. Entry fills fall at :45 and :15, exit fills at :14 and :44.
  - **Why this window.**
    - It starts 14 minutes after the 08:30 reopen that follows the grain pause, which is the D9.4
      gapped-market caution. It ends with an exit at 13:14, the ports' C-2 exit.
    - The 11:00 release lies strictly inside the position interval [10:45, 11:14], and the 13:00 FOMC
      statement inside [12:45, 13:14]. No ML fill lands in [11:00, 11:02) or [13:00, 13:02).
    - The window is the day session only: the overnight session's coverage is unmeasured, and the
      crush cointegration "fades away during session 1" (P-K6-026-c).
  - **Why h = 30.**
    - The report variance difference "is significant in the second period for 30 to 40 minutes after
      the release" (P-K6-014-d).
    - "observed returns correlation fades in about 30 minutes after the announcement" (P-K6-029-c).
    - "the higher volatility did not persist much beyond 60 minutes" (P-K6-030-a).
    - h = 15 would split the release response window (P-K6-014-a, P-K6-015-b). h = 60 or 120 would
      leave at most 4 or 2 decisions in the 4.8-hour grain session and fold the release into a longer
      interval.
- **Expected rows:** 9 x the eligible research-window trade dates. That is about 300 dates, less
  roll-blackout, vendor-degraded and early-halt dates (D15.3), and less the 20-date warm-up of B4:
  roughly 2,000-2,500 rows. E.2 gives the exact count.
- **Expected entries:** at most 9 per day (<= 20), each held 30 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps at
  >= 80% achieved null power on the confirmation window counts against it). Failing the D5 screen
  puts it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 13:14.
  2. Order type: market (D15.6).
  3. D9.4: at most 9 entries a day, 30-minute holds, no stops or brackets. No fill in a release
     minute.
  4. Star: none.
  5. News: q = 1 lot, not the full maximum. A position may span the 11:00 release or the 13:00
     statement. The 11:14 and 13:14 exits pay D8's event-window cost.
  6. D9.5a: no fill in a guard window.
  7. Position limit: 1 lot-equivalent.
  8. D9.7: the harness guard and the release residual (C13).
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for
    every ML member.
- **Data needed:** ohlcv-1m of ZC and ZS: the research window for training and tuning, the
  confirmation window for the frozen model. The member-level coverage check covers 08:45-13:14.
  External: EC-USDA, EC-CAL, EC-CP, EC-LIM.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K6-crush3-01 | The soybean crush spread as published: long or short ZS, ZM and ZL together, open to close, after a GPM gap (K6-001 P-K6-001-a, P-K6-001-f; a 10-12-9 contract ratio, 31 contracts, per the log) | D9.5 / D9.6 (position) | No K6 product has a Topstep-permitted micro (F1). Three full-size legs are 3 lot-equivalents: over the 1-lot member cap (D9.5) and over the 50K XFA's 2-lot maximum (F5.2). The same mechanism is carried single-leg by K6-crushgap-01 |
| X-02 K6-crush2-01 | Two-leg crush or oilshare spreads (ZS against ZM or ZL; ZL against ZM), including a minute-scale version of the day-session cointegration (K6-026 P-K6-026-a, P-K6-026-c) | D9.5 | Two full-size legs are 2 lot-equivalents, over the 1-lot cap. That is also the full XFA maximum, which F6.3 forbids trading into a scheduled major release, and every grain report day is one. K6-026 has no trading rule and one year of data (P-K6-026-d) |
| X-03 K6-crushavg-01 | Trade the GPM back toward its 5-day average (K6-008 P-K6-008-a, P-K6-008-b; K6-044 P-K6-044-a) | Rule 1 (evidence, parameters) | Abstracts only. The filter, the holding period and whether the reversion shows within one session are in no passage. The intraday crush reversion is carried by K6-crushgap-01. As a two-leg rule it would also fail D9.5 |
| X-04 K6-surprise-01 | Trade a USDA report by the sign of its surprise (USDA minus trade guess) (K6-010 P-K6-010-a; K6-011 P-K6-011-a; K6-017 P-K6-017-a; K6-027 P-K6-027-a; K6-045 P-K6-045-a) | Rule 3 | The trade guess is a newswire poll: "surveyed by newswire services, such as Thompson/Reuters and Bloomberg" (P-K6-010-e); "aggregated by business intelligence firms Bloomberg LP and LSEG" (P-K6-049-e); "analysts' forecasts published by Bloomberg" (P-K6-045-a). No named, obtainable free historical source was found. With the obtainable proxy (the first minutes' price response), the post-release part is K6-wasdepost-01. The pre-release part, read from price, is K6-wasdepre-01. The release-minute part is X-06 |
| X-05 K6-stocksrev-01 | Fade the Grain Stocks surprise ("the corn market may have read too much into those surprises", K6-010 P-K6-010-c, P-K6-010-d) | Rule 3; rule 1; flat by F | It needs the trade guess. The overreaction is a conjecture inferred from later feed-and-residual revisions, not a price test. Its horizon is later WASDE months (multi-day). An intraday version is [unverified] (log tag) |
| X-06 K6-relmin-01 | A position opened in the release minute or the first minutes after 11:00 (K6-012 P-K6-012-d, P-K6-012-e; K6-014 P-K6-014-a, P-K6-014-e; K6-016 P-K6-016-b; K6-024 P-K6-024-a, P-K6-024-c; K6-020 P-K6-020-b) | D9.5a; D9.4; D9.3(c) | No fill is simulated in [T, T + 2 min). The first minutes are a speed race: "it can still easily be a five-minute delay" to download a report, and a "two-second speed advantage" (P-K6-012-d, P-K6-012-e). That is the gapped-market case of D9.4, where a bar-open fill is not a real fill. The first-minute overreaction pattern is "difficult to establish" (P-K6-014-e). A hold matching the 5-10 minute spike (P-K6-014-a, P-K6-020-b) would breach the 10-minute mean hold |
| X-07 K6-cpfade-01 | Fade soybeans' Crop Progress response during the next day session (K6-034 P-K6-034-d) | Rule 1 (evidence) | The main result is a null for the day session: "Significant results could not be found for the open-to-close return of the report-release trading day" (P-K6-034-b). The overreaction hint is one subsample, and the author warns "these ex post results do not necessarily imply that a profitable trading strategy could have been developed" (P-K6-034-d). The release (15:00 CT) now meets the 19:00 CT evening session, so the documented close-to-open response is today an overnight move the program cannot hold. The condition change survives as feature KF6 of K6-ml-01 |
| X-08 K6-lvrpt-01 | HE or LE traded at the next morning's open after Cattle on Feed, Hogs and Pigs or Cold Storage (14:00 CT; K6-018 P-K6-018-a, P-K6-018-e; K6-040 P-K6-040-a, P-K6-040-b; K6-039 P-K6-039-c, P-K6-039-d) | Rule 1; D9.7; rule 3 | No intraday post-open mechanism is logged. "very few reports had a statistically significant impact on the cattle markets ... Market reaction to USDA information was even less common in lean hog markets" (P-K6-018-e). The volatility impact "largely disappeared after 2000" (R-K6-046). "28.5% of the days with Hogs and Pigs report releases were subject to price limit moves" (P-K6-018-c), so a report-morning entry often meets the 2% band. The surprise needs proprietary polls |
| X-09 K6-expsales-01 | Trade the Thursday 07:30 CT Export Sales release (K6-041 P-K6-041-a; K6-049 P-K6-049-d) | Rule 1; D9.1; D9.3 | No price-response passage was logged (the only export study, R-K6-029, is daily and pre-electronic). Fills are possible only from 07:32 (D9.5a) to 07:43 (the pre-pause exit, D9.1): at most an 11-minute position at the thin end of the overnight session, whose coverage is unmeasured. The daily flash-sales release at 08:00 CT falls inside the pause (P-K6-041-b) |
| X-10 K6-settle-01 | Fade the move into the settlement minute (K6-007 P-K6-007-a, P-K6-007-b, P-K6-007-c; K6-009 P-K6-009-a to P-K6-009-c) | Flat by F; rule 1 | The reversal is measured from settlement to the next open, an overnight hold the XFA flat rule and the grain pause forbid. The effect belonged to pit-only settlement: "the percentage of reversals falls from 57.3% under the old regime to 48.7% under the new" (P-K6-007-c). The whole 2019-2026 window is under the new regime |
| X-11 K6-magnet-01 | Trade toward the limit as the price approaches it ("the probability of limit moves conditional to extreme movements increases when limit levels are tighter", K6-036 P-K6-036-a; P-K6-036-b) | D9.7; D9.4 | The payoff lies inside the 2% band where the program must not hold a position. Volume collapses at the limit (P-K6-036-b), the gapped-market case. The limit state survives as feature KF4 of K6-ml-01 |
| X-12 K6-lockday-01 | Trade on the limit day itself, or at the reopening after a lock, by the options-implied futures price (K6-002 P-K6-002-d; K6-035 P-K6-035-a, P-K6-035-b) | D9.7; data; D9.4 | On the lock day the price is in the band. Options data are not in the plan, and on locked days the options-implied price is "only a biased, inefficient, and highly noisy estimate" (P-K6-035-b). The reopening after a lock is the gapped, illiquid moment (P-K6-035-a). The next-day part is K6-limitcont-01 |
| X-13 K6-idxroll-01 | Commodity-index roll in grains and livestock: nearby against deferred during the GSCI or DJ-UBSCI roll, or front-running it (K4-034 P-K4-034-a, P-K4-034-b; K4-035 P-K4-035-b, P-K4-035-c; K4-036 P-K4-036-b, P-K4-036-d, all [K6]) | Flat by F; D9.5; rule 1 | The effects are multi-day, settlement-to-settlement nearby-minus-deferred differentials; front-running holds for weeks. Two legs fail D9.5, and deferred months are not in the data plan. The ag differentials are "on order of the typical bid/ask spreads" (P-K4-036-b): for example "Corn C 48 ... 0.0012*", "Soybeans S 48 ... -0.0016" (P-K4-036-d). The pooled effect is "never significant once we adjust the standard errors" (P-K4-034-a). A single-leg intraday version has no passage |
| X-14 K6-biofuel-01 | ZL on the trade date after an EPA or CARB biofuel-policy event, in the direction of the event response: "Post-Announcement-Leak Drift" (K6-032 P-K6-032-a, P-K6-032-b; kept in K6 by lead ruling) | Rule 3; rule 1 | Abstract only. The 36 events "including ... news 'leaks' from media sources with early information access" were not retrieved, and leaks have no named, obtainable, timestamped historical source. The day-session share of the next-day +0.62% is unreported. The source sample (2021-2025) overlaps the confirmation and research windows, so a confirmation pass would partly re-test the discovery sample. A re-specified member is sketched for the lead in section 7, item 9 |
| X-15 K6-flashrev-01 | Fade flash moves in ZC and HE (K6-025 P-K6-025-a) | Rule 1 (evidence against) | The abstract finds that flash events "are heavily influenced by unanticipated changes in fundamentals that may lead to a new equilibrium price", which argues against a reversal. It is recorded as counter-evidence in K6-ovr-01 |
| X-16 K6-mktstruct-01 | Trade with the day's directional-trader share (K6-045 P-K6-045-a, P-K6-045-c) | Rule 3 | The trader-group shares come from confidential CFTC transaction data, and the surprise from Bloomberg surveys |
| X-17 K6-chpmi-01 | Grains traded on the Chinese PMI surprise (K3-007 P-K3-007-j [K6]) | Rule 1 (null); rule 3 | "Agricultural commodities used in the food industry (corn, soybeans and wheat) show no significant reaction to the PMI news" (P-K3-007-j). The surprise needs a proprietary consensus |
| X-18 K6-ovnrev-01 | Overnight-to-intraday reversal on grains (K3-040 [K6]) | Rule 1 | Title only; content [unverified]. A single-product gap fade is D.1 family D-H4, which D6 does not port |

---

## 3. Beyond budget (lead decides)

None. The log supports 5 new members inside the budget of 11. These candidates were considered and not
written; none is a budget overflow:
- **ZW, ZM and ZL versions of K6-wasdepre-01, and ZS and ZW versions of K6-wasdepost-01.** Topstep's
  Crop Production row lists all five grains, but the pre-release drift source is corn and soybeans
  (P-K6-027-a) and the lingering source is corn (P-K6-037-a). Extending them is an untested
  inference. Cost: up to +5 trials.
- **Grain Stocks, Prospective Plantings and Acreage days in the two WASDE members.** These releases
  move markets most (P-K6-018-f), but the drift and lingering sources are WASDE-specific. Cost: no
  extra trials, but the event set would widen away from the evidence.
- **A fade variant of K6-limitcont-01**, trading against the opening move on the day after a limit
  close. It would rest on the -0.61 arithmetic from P-K6-002-d, whose same-sample premise is not
  stated. Cost: +7 trials, and it is correlated with K6-limitcont-01's sign check, which already
  reports the direction.
- **A month filter for the report members** (K6-013: quiet WASDE months, P-K6-013-a). It describes
  balance-sheet changes, not price responses, and would add an untraced parameter.

---

## 4. Routed to K8

| Source (log section 4) | Legs | One phrase |
|---|---|---|
| CME OpenMarkets 2023, "Are Soybean Oil and Crude Oil Playing a Game of Tag?" | ZL (K6) and CL (K4) | soybean oil against crude, lead-lag |
| CME Articles 2021, "Energy Demand Revives Soybean Complex Trading Dynamics" | ZS, ZL, ZM (K6) and energy (K4) | biofuel demand links |
| CME education, "Relationship Between Major Grain Commodity Benchmarks and Equities Prices During Economic Downturns" | ZC, ZS, ZW (K6) and equity indices (K1) | grains against equities in downturns |
| JCM 2024 (Cao, Heckelei, Ionici, Robe), "USDA reports affect the stock market, too" | USDA grain reports (K6) and equities (K1) | one cluster's announcement moving another's product |
| CFTC OCE 2024, "Do Agricultural Swaps Co-Move with Equity Markets? Evidence from the COVID-19 Crisis" | ag swaps (K6) and equities (K1) | crisis co-movement |
| CFTC OCE, "Convective Risk Flows in Commodity Futures Markets" | VIX (K1) and commodity positions including ags (K6) | risk flows conditioned on VIX, daily |
| Agribusiness 2026 (Zhang), "Spillover Effects of Energy and Grain Futures Volatility: WTI, Natural Gas, and EUA Futures on U.S. Wheat, Corn, and Soybean Markets" | CL, NG (K4) and ZC, ZS, ZW (K6) | energy-to-grain volatility spillover |
| arXiv 1209.0900 and arXiv 1210.6080 | ethanol and crude (K4) and corn (K6) | biofuel links |

K4's catalog routes three more K4-K6 items (JFM 2010 corn-crude spillover; J. Agricultural Economics
2025 WTI and grains; arXiv 1209.0900, the same item as above). K6-032 (EPA and CARB) is **not** routed:
it stays in K6 by lead ruling (STATE 01:23) and is excluded here on its own merits (X-14).

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K6.md section 3 and every `[K6]`-tagged
passage elsewhere.

| Item | Disposition |
|---|---|
| K6-001 Rechner, Poitras | Used: K6-crushgap-01 (P-a, b, d, e, f; quality tells stated). The published three-leg spread is excluded, X-01 |
| K6-002 Janardanan, Qiao, Rouwenhorst | Used: K6-limitcont-01 (P-a to P-f, with P-d as counter-evidence); K6-ml-01 prev_limit. The options-implied lock-day signal is excluded, X-12 |
| K6-003 Park | Used: K6-limitcont-01 (P-a, supporting; abstract only); K6-ml-01 prev_limit |
| K6-004 Brorsen (blocked) | Insufficient evidence: title only, with no content retrieved. Not used |
| K6-005 = K5-023 Martell, Trevino | Duplicate registry line (the claim is K5-023). Title only, retrieved by neither reader: insufficient evidence |
| K6-006 Silveira et al. | Insufficient evidence for a member: WASDE raises corn's intraday volatility and volume with no direction (P-a, P-b). Supports the event set and C12 |
| K6-007 Onur, Reiffen | Excluded, X-10 |
| K6-008 Simon | Excluded as its own member, X-03. Supporting evidence (reversion) in K6-crushgap-01 |
| K6-009 Peterson | Excluded, X-10 (settlement-construction facts; P-c on livestock settlement noted) |
| K6-010 Irwin, Good | Excluded, X-04 and X-05. P-e is cited for rule 3 |
| K6-011 Adjemian et al. | Used: K6-wasdepre-01 (response direction, P-a); K6-wasdepost-01 (counter-evidence, P-d); K6-ml-01 usda_resp; C13 and the D9.7 notes (P-b, P-e, a confirmation-window date, no parameter taken). The surprise version is excluded, X-04 |
| K6-012 Irwin | Used for timing (P-b 11:00 CT since January 2013; P-c livestock after the close) in C9. The release-minute trade is excluded, X-06 (P-d, P-e) |
| K6-013 Janzen | Not used as a filter (section 3): it describes balance-sheet changes by month, not price responses |
| K6-014 Joseph, Garcia | Used: K6-wasdepre-01 (exit timing, P-a; efficiency scope, P-b); K6-wasdepost-01 (counter-evidence, P-b); K6-ovr-01 skip rule (P-b); K6-ml-01 h (P-d) and usda_resp (P-a). The first-minute pattern is excluded, X-06 (P-e) |
| K6-015 Lehecka, Wang, Garcia | Used: K6-wasdepre-01 (pre-release adjustment and ten-minute persistence, P-b); K6-wasdepost-01 (counter-evidence, P-b); K6-ml-01 pre_usda and usda_resp |
| K6-016 Adjemian, Irwin | Used for timing context in X-06 (P-b: volatility "dissipates within the space of a few trading minutes"). No direction; no member |
| K6-017 Karali et al. | Used: release-time history in C9 (P-b). Supporting for the surprise-response direction in K6-wasdepre-01 (P-a). Daily: not intraday-feasible as measured |
| K6-018 Isengildina-Massa et al. | Used: C9 livestock times (P-a) and Grain Stocks times (P-b); limit frequencies (P-c) in K6-limitcont-01 and C13; X-08 (P-e); report importance (P-f) in section 3 |
| K6-019 Indriawan, Martinez, Tse | Context only: the 2018 end of media early access precedes the window, and market-quality proxies are "not statistically different before and after" (P-b). No member |
| K6-020 Bunek, Janzen | Insufficient evidence for a member: a KC wheat volatility fact (P-a, P-b). Used in X-06 |
| K6-021 Wang, Garcia, Irwin | Cost input: corn spread about one tick (P-c) and wider on report days (P-b). A cross-check for D8, used in C12 |
| K6-022 Frank, Garcia | Cost input for LE and HE (P-b, P-c): a cross-check for D8. No member |
| K6-023 Couleau, Serra, Garcia | Context: the night-session cancellation (P-d) is used in C3. The open's quote concentration (P-c) supports K6-limitcont-01's 08:45 entry. The noise horizon (P-a, P-b) is a reason no new member reads a sub-15-minute livestock signal |
| K6-024 Couleau, Serra, Garcia | Supports D9.5a, C12 and X-06 (jumps cluster at the release, P-a, P-c). No member |
| K6-025 He, Serra, Garcia | Counter-evidence in K6-ovr-01 (P-a); excluded as a member, X-15 |
| K6-026 Zhou et al. | Used: K6-crushgap-01 (P-b, P-c; P-d and P-e as limits); K6-wasdepre-01 (P-b); K6-ml-01 window (P-c). The two-leg version is excluded, X-02 |
| K6-027 Aitkulova, Balsamo, Seamon | Used: K6-wasdepre-01 (P-a); K6-ml-01 usda_phase. The surprise version is excluded, X-04 |
| K6-028 Zhu et al. | Used: supporting evidence in K6-wasdepost-01 (P-b) |
| K6-029 Bian, Serra, Garcia | Used: K6-wasdepre-01 entry timing (P-a); K6-ml-01 usda_phase (P-a), zs_ret30 (P-b, P-c) and h (P-c) |
| K6-030 Kauffman | Used: K6-ml-01 h (P-a) |
| K6-031 Hu, Mallory, Serra, Garcia | Not a mechanism: a roll-timing input for E.2 (section 7, item 10) |
| K6-032 Avileis, Swanson | Excluded, X-14 (stays in K6 by lead ruling; section 7, item 9) |
| K6-033 Li, Wang, Diersen | Context in K6-ovr-01 (P-a). No rule; news is matched by day only (P-b) |
| K6-034 Lehecka | Used: K6-ml-01 cp_ge_chg (P-a, b, c). The fade member is excluded, X-07 (P-b, P-d) |
| K6-035 He, Serra | Used: K6-limitcont-01 (entry delay and counter-evidence, P-a). X-12 (P-b) |
| K6-036 Fontinelle, Janzen | Used: K6-ml-01 lim_pos (P-a, P-b). The member is excluded, X-11 |
| K6-037 Arnade, Hoffman, Effland | Used: K6-wasdepost-01 (P-a, c, d); K6-ml-01 usda_resp; release-time history (P-b) |
| K6-038 WASDE page | Used: C9a (P-a, P-b) |
| K6-039 NASS calendar | Used: C9d (P-a); X-08 (P-c, P-d); Crop Production time (P-b) |
| K6-040 NASS PFEI schedule | Used: C9a (P-a, P-b); X-08 |
| K6-041 FAS Export Sales | Used in X-09 (P-a, P-b) |
| K6-042 AMS livestock reports | Not used: the afternoon cash reports come after the livestock close, and the morning times are [unverified] |
| K6-043 Zhang | Used: K6-wasdepre-01 (P-a, supporting); K6-ml-01 pre_usda |
| K6-044 Mitchell | Supporting for reversion (P-a); X-03. No member |
| K6-045 Du, Kane | Excluded, X-16; P-a is cited for rule 3 in X-04 |
| K6-046 | Crude only, K4's region (log section 5). Not a K6 source; not used |
| K6-047 CME price limits | Used: C10, C13, K6-limitcont-01, K6-ml-01 lim_pos (P-a, P-b, P-c) |
| K6-048 CME limit FAQ | Used: C10, C13, K6-limitcont-01, K6-crushgap-01's linkage note, K6-ml-01 (P-a to P-d) |
| K6-049 CME USDA reports guide | Used: C1 and C9 (P-a to P-d); rule 3 (P-e) in X-04 |
| K6-050 CME crush reference guide | Used: K6-crushgap-01 GPM weights (P-a, P-b) |
| K6-051 CME Asian-hours soybeans | Context: overnight ZS liquidity (P-a to P-c). No overnight member is written (C5), so it is not used |
| K3-007 [K6] Baum, Kurov, Wolfe (P-K3-007-j) | Excluded, X-17 (null for corn, wheat and soybeans) |
| K3-040 [K6] Kosowski et al. | Excluded, X-18 (title only) |
| K4-016 (registry tags K4, K6) | Rejected by K4 (R-K4-038: a multi-day ETF hold). There is no [K6] passage and it is not intraday-feasible. Not used |
| K4-034 [K6] Dubois, Maréchal | Excluded, X-13 (P-a, P-b) |
| K4-035 [K6] Mou | Not intraday-feasible (multi-week calendar spreads, P-b, P-c); X-13 |
| K4-036 [K6] Stoll, Whaley | Excluded, X-13 (P-b, P-d) |
| K4-039 (registry tags K4, K5, K6) | Rejected by K4 (R-K4-040: non-public CFTC positions). Not used |
| R-K4-063 (K4 log) | A K6-region title rejected by K4 (delivery convergence). Not a passed item. Delivery-period mechanisms need positions into delivery (compare R-K6-012, R-K6-055) |
| K5-023 Martell, Trevino | Title only, not retrieved: insufficient evidence |
| K5-029 [K6] Borgards, Czudaj, Hoang (P-a, P-b, P-d) | Used: K6-ovr-01. P-c ([K5]/[K4]) is used for the method only |
| K5-030 Gu, Kurov, Stan | Unread by K5, and K6 coverage is [unverified]. Not used |
| R-K6-001 to R-K6-070 | Rejected by the reader. Not used, except as cited: R-K6-006 and R-K6-032 in CP1, R-K6-029 in X-09, R-K6-046 in X-08 |
| Partition seeds with no passed item | Weather-forecast updates (R-K6-011 daily, R-K6-027 seasonal, R-K6-049 satellite); wheat against corn and hogs against cattle (R-K6-014 is daily cointegration; no intraday source); first notice day and delivery (R-K6-012, R-K6-055). No member |

**Correlated members, flagged for the lead's Tier-A accounting (not duplication).**
- K6-limitcont-01's trades are a same-direction subset of K6-cp3-01's (section 7, item 8).
- K6-wasdepre-01 and K6-wasdepost-01 on ZC meet at 11:15: one exits and the other may enter. They are
  separate hypotheses: the pre-release drift, and continuation after the release.
- K6-ml-01 carries the release, limit and Crop Progress states as features, which overlaps the
  information of the hand-written members by design (D15).

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all seven admitted) |
|---|---|---|---|
| K6-cp1-01 | ZC, ZW, ZS, ZM, ZL, HE, LE | 1 | 7 |
| K6-cp2-01 | ZC, ZW, ZS, ZM, ZL, HE, LE | 1 | 7 |
| K6-cp3-01 | ZC, ZW, ZS, ZM, ZL, HE, LE | 1 | 7 |
| K6-crushgap-01 | ZS only (lead ruling; ZM, ZL removed) | 1 | 1 |
| K6-limitcont-01 | HE, LE (lead ruling; grains removed) | 1 | 2 |
| K6-wasdepre-01 | ZC, ZS | 1 | 2 |
| K6-wasdepost-01 | ZC | 1 | 1 |
| K6-ovr-01 | EXCLUDED by the lead (01:52) | - | 0 |
| ~~K6-ml-01~~ [excluded, U6] | ZC (no fallback) | ~~48 in research-window accounting only (D15.8)~~ | 0 (E.0: 1) |
| **Cluster total** | | | **39** = 21 port + 17 new + 1 ML. In general 4E + (a_ZS + a_ZM + a_ZL) + (a_ZC + a_ZS) + a_ZC + (a_ZW + a_ZC + a_ZS + a_ZL) + a_ZC. The cuts in section 7, item 7 would bring it to 28 |

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **Spreads in K6 cannot meet D9.5.**
   - No K6 product has a Topstep-permitted micro, so every inside-K6 spread (crush, oilshare,
     wheat-corn, hogs-cattle) needs at least 2 full-size lots. That exceeds the 1-lot-equivalent member
     cap; a three-leg crush exceeds even the XFA maximum (X-01, X-02).
   - K6-crushgap-01 is the single-leg reading, an explicit inference.
   - Options: keep it on all three legs (3 trials), keep it on ZS only (1 trial; the most liquid leg,
     ADV 302,997), or drop it.
2. **D9.7 inputs are not in the spend plan.**
   - Encoding D9.7 for any K6 member, ports included, needs:
     - the official daily settlement of each vehicle contract on every date (C10);
     - CME's historical limit tables, with the semi-annual grain resets, the expanded state and its
       linkages, the spot-month and pre-FND exemptions, and livestock limit changes.
   - The settlements are paid, for example the GLBX.MDP3 statistics schema. They are not in D13 and
     need a quote in E.1. No free source with 2019-2026 history was found.
   - A bar-close proxy would misclassify limit closes, because the settlement is not the last trade
     (K6-009).
   - K6-limitcont-01 and K6-ml-01 (lim_pos, prev_limit) read the same inputs.
3. **The D9.7 residual across the 11:00 release.**
   - A position held through a release that jumps into the 2% band is exited at the first bar D9.5a
     allows (11:02 at the earliest). It is therefore "held" inside the band for up to about 2 minutes.
   - This affects CP2 and CP3 on grains, K6-crushgap-01, K6-wasdepre-01, K6-limitcont-01 (grains) and
     K6-ml-01.
   - Should this be accepted, or should grain members be flat across 11:00 on EC-USDA dates? For the
     ports that would be a D6 change.
4. **The arithmetic of D9.7.** "within 2% of the day's limit price" could mean 2% of the price level
   (|P - U| <= 0.02 U) or 2% of the limit amount. For corn, whose limit is 7% of a 45-day average
   price (P-K6-048-a), the first reading blocks from about 70% of the limit move and the second only
   at the limit itself: roughly an order of magnitude apart. E.2 or the lead fixes the reading before
   any bar is read.
5. **CP2 on livestock on FOMC days.** An entry intent on the 12:59 bar fills at 13:00, which D9.5a
   defers to 13:02, leaving one bar to F = 13:03 and breaking D9.3(b). A harness rule would fix it
   (skip an entry whose deferred fill leaves fewer than three bars to F). This is a D6 or D9 matter.
6. **CP1 on livestock** has no overnight component: the first bar is 08:30 (C3). The D6 text is
   applied as written.
7. **Trial count 39.** Possible cuts, each the lead's call:
   - K6-limitcont-01 to HE and LE only, where limit moves are 2 to 4 times as frequent as in crops
     (P-K6-018-c), so the grain trials are likely "inconclusive by design": -5.
   - K6-ovr-01, which has no grain-specific result and counter-evidence in K6-025: -4.
   - K6-crushgap-01 to ZS only: -2.
   - With all three cuts: 28.
   - The two WASDE members trade on about 5% of dates (C11) and are likely null at eps or
     inconclusive (lead ruling Q4: the power check decides).
8. **K6-limitcont-01 is nested in K6-cp3-01.** A limit close has CLV of 1 or 0. It is a distinct
   hypothesis (the limit itself, P-K6-002-a) but a correlated one in Tier A.
9. **K6-032 (EPA and CARB) is excluded (X-14).** If the lead wants it, a re-specified member (1 trial)
   would be:
   - event set: EPA Renewable Fuel Standard volume rules and small-refinery-exemption decisions, and
     CARB Low Carbon Fuel Standard rulemaking releases, each dated by the agency's own press release
     or Federal Register record (the lead names the sources);
   - signal: the ZL move from the close of the 13:14 bar on the last trade date before the event date
     to the 08:30 open of the first trade date after it;
   - trade: that trade date's day session, from 08:45 to 13:14, in the signal's direction.

   It would test the post-announcement drift without the leak events, which the source includes.
10. **Roll convention for the K6 vehicles (E.2).**
    - Grain limits are removed on the business day before first notice day (P-K6-048-d).
    - Nearby price-discovery leadership ends when the nearby's volume share falls below 50%, "about
      2-3 weeks before expiration in corn and 5-6 weeks before expiration in live cattle"
      (P-K6-031-a).
    - A convention that rolls before those points keeps D9.7 defined and trades the leading contract.
    - K6-crushgap-01 accepts month mismatches across the crush legs.
11. **Source samples inside the confirmation window.** These matter for an edge claim only:
    - K6-027 (window [unverified], 2026), which K6-wasdepre-01 rests on;
    - K6-028 (2013-2020);
    - K6-033 (2013-2022);
    - K6-011 (August reports 2009-2019);
    - K5-029 (2019-11..2020-06), which K6-ovr-01 rests on.

    No parameter was taken from any confirmation-window date. A pass by K6-wasdepre-01 or K6-ovr-01
    would partly re-test its source's own sample.
12. **Entries one minute after the 08:30 reopen** (CP3 and K6-crushgap-01 on grains). They are read
    here as ordinary market orders, not D9.4 "reckless trades in gapped markets". The lead confirms
    that reading.
13. **E.2 checks named in this catalog:**
    - (a) tick-size and price-unit history, 2019-2026 (C7);
    - (b) grain and livestock session hours and early closes, 2019-2026 (D10);
    - (c) EC-USDA from the yearly schedules and the ESMIS record, with the drop rule; ESMIS shows no
      October 2025 WASDE or Crop Progress (C9a);
    - (d) the Crop Progress corn-condition table format across 2019-2026, parsed from each release as
      published (C9d, KF6);
    - (e) settlements and the historical limit table (C10);
    - (f) member-level coverage for 08:45-13:14 (ML) and CP1's reading of the 19:00 CT bar;
    - (g) legs bought for non-admitted exposures (C8).
14. **Seeds with no member:** weather-forecast updates, wheat against corn, hogs against cattle,
    Export Sales, and livestock reports (section 5 and X-08, X-09). Livestock is covered only by the
    ports and K6-limitcont-01.
15. **Registry hygiene** (from the reader): K6-005 duplicates K5-023; K6-046 is a crude-only K4-region
    line; K6-019's registry line carries only a partial DOI, and the log resolves it to
    10.1016/j.jcomm.2020.100149.
