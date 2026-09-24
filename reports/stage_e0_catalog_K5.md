# Stage E.0 hypothesis catalog, cluster K5 (metals: GC, MGC, SI, SIL, HG, MHG, PL)

Writer: CatalogWriter-K5-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from 01:23 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** No price, bar, tick or order-book data for any K5 product
existed on this machine while it was written, and none was opened. The only product-specific numbers
used are:
- contract specifications and public ADV (reports/stage_e0_liquidity.json; design D1 table);
- Topstep's published fees, hours, release table and risk-adjustment rules
  (reports/stage_e0_topstep_facts.md F3, F4, F6, F12);
- calendar metadata: LBMA auction clock times, UK bank-holiday dates, FOMC, BLS and Fed G.17 release
  dates and clock times.

Calendar metadata carries no prices. No price level, range, trend or volatility of any product is used or
assumed below. **No K5 rule reads an LBMA auction result, a CME settlement price, or any released
macro value.** The calendars supply dates and clock times only.

**Inputs read in full:**
- reports/stage_e0_research_K5.md (supersedes the sonnet partial log, which was not used).
- Every `[K5]`-tagged passage elsewhere: K3-007 (P-K3-007-h, reports/stage_e0_research_K3.md); K4-034
  and K4-035 (index-roll passages, reports/stage_e0_research_K4.md, lines 505-536); K4-036's line saying
  it has no metals. The registry also tags K3-040 (title only) and K4-039 (rejected as R-K4-040) with K5.
- reports/stage_e0_source_registry.jsonl (K5 lines and every non-K5 line tagged K5).
- docs/STAGE_E_DESIGN.md: D1-D15, including the 21:12 and 21:52 amendments and D9 points 5a, 8, 11, 12, 13.
- reports/stage_e0_partition.md.
- reports/stage_e0_topstep_facts.md (F3 fees, F4 hours, F6 news, F7 prohibited, F12 risk adjustments,
  CPI window, holidays).
- reports/stage_e0_liquidity.json (K5 rows).
- reports/stage_d1f_confirmation_list.md 2.1 A3 (Family H mechanics).
- strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py (the CP2 hold count).
- reports/stage_d1b_family_f_declaration.md F3.3 (CP1's origin).
- reports/stage_e0_STATE.md, for the lead's rulings of 21:12 and 21:52.
- reports/stage_e0_catalog_K4.md and reports/stage_e0_catalog_K2.md, for format only. No mechanism was
  taken from them. K5-029 is a K5-claimed panel source that K4 also used for its own products; where this
  catalog makes the same judgment K4 made about that source, the entry says so.

**Official pages fetched in this task** (curl, 2026-09-24 01:28-01:33 PDT). They were fetched only to
confirm auction and release times and calendar availability; no mechanism research was done. Saved under
the scratchpad `fetch/` directory with a `k5_` prefix.
- https://www.ice.com/iba/lbma-gold-silver-price (HTTP 200): "The auctions are run at 10:30 and 15:00
  London time for gold, 12:00 London time for silver, and 09:45 and 14:00 London time for platinum and
  palladium."
- http://web.archive.org/web/20190718185125id_/https://www.theice.com/iba/lbma-gold-silver-price (HTTP 200):
  "The auctions are run at 10:30am and 3:00pm London time for gold and at 12:00pm London time for
  silver." So the gold and silver times are the same in July 2019 and now.
- http://web.archive.org/web/20210414221544id_/https://www.lbma.org.uk/prices-and-data/lbma-platinum-and-palladium-price
  (HTTP 200): "The LBMA Platinum and Palladium Price is administered independently by the London Metal
  Exchange (LME)." The captured text gives no auction times. Platinum's 09:45 and 14:00 are verified only
  on the current pages (K5 log 3.0 and the IBA page above). E.2 confirms 2019-2026 (section 7, item 9).
- https://www.gov.uk/bank-holidays.json (HTTP 200): 83 England-and-Wales dates, 2019-01-01 to 2028-12-26.
- https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm (HTTP 200): meetings 2021-2026.
  Scheduled two-day meetings, eight a year; 2025 also lists "August 22 (notation vote)".
- https://www.federalreserve.gov/monetarypolicy/fomchistorical2019.htm and ...2020.htm (HTTP 200); the
  2021-2024 historical URLs returned 404, but the calendar page above covers those years.
- https://www.federalreserve.gov/newsevents/pressreleases/monetary20190731a.htm and
  .../monetary20250507a.htm (HTTP 200): both read "For release at 2:00 p.m. EDT".
- https://www.bls.gov/schedule/news_release/cpi.htm (HTTP 403 "Access Denied"). The Wayback captures
  http://web.archive.org/web/20190820223142id_/https://www.bls.gov/schedule/news_release/cpi.htm and
  http://web.archive.org/web/20190613093518id_/https://www.bls.gov/schedule/news_release/empsit.htm
  (HTTP 200) list every CPI and Employment Situation release with "Release Time ... 08:30 AM".
- https://www.federalreserve.gov/releases/g17/default.htm (HTTP 200): "The monthly releases are issued
  at 9:15 a.m." and "Historical release dates are also available."
- https://www.census.gov/manufacturing/m3/adv/index.html (HTTP 404). The durable-goods schedule is not
  confirmed (section 7, item 2).

---

## 0. Header

| Item | Value |
|---|---|
| Products | GC, MGC, SI, SIL, HG, MHG (COMEX); PL (NYMEX) |
| Exposures | gold {GC, MGC}; silver {SI, SIL}; copper {HG, MHG}; platinum {PL} (partition section 1) |
| D1 | **D1 applied: all four K5 exposures IN; platinum flagged (may be suspended).** Admissible vehicles, 2026 Jan-Aug ADV (design D1 table): gold MGC 429,702 and GC 212,764; silver SIL 134,882 and SI 83,587; copper HG 77,679 and MHG 21,803; platinum PL 22,360 |
| Members | **8 = 4 new + 3 core ports + 1 ML member.** Budget 15, so 7 slots are unused (section 3) |
| Trials in N (confirmation) | **22 if D2 admits all four exposures:** 12 port + 9 new + 1 ML. In general 4E + 3a_G + a_S + a_P + 1, where E is the number of admitted exposures and a_G, a_S, a_P are 1 when gold, silver or platinum is admitted (the ML member assumes gold, section 7 item 7). Each exposure of K5-preauc-01 also needs its member-level coverage check (C14) |
| ML grid | 48 configurations, counted only in the K5 screening session's research-window accounting (D15.8) |
| Starred products | **MGC and SIL** (Topstep F1). The star's referent is Topstep's "Risk Adjustments: High Risk/High Volatility" article (D9.8, F12.1), encoded as D9.11 and D9.12. **MGC:** volatility cap 30 contracts on the 50K account, so the 1-lot cap of 10 binds first; at most 3 contracts in an opening fill inside the CPI window. **SIL:** volatility cap 2 contracts, which binds, since D2's 1-lot cap would allow 5; the same CPI-window cap of 3; counts 0.2 lot. MHG is unstarred but the same article names it: cap 2 contracts, CPI-window cap 3 |
| Suspension risk (D9.11) | "Silver (SI) = 0; ... Copper (HG) = 0; ... Platinum (PL) = 0" at Topstep's discretion in extreme volatility (F12.1). D2 prefers SIL and MHG whenever they are candidates. **Platinum has no micro and may be suspended in volatile periods**; every platinum trial carries that flag |
| CPI window (D9.12) | No opening fill on GC, SI, HG or PL in [CPI - 5 min, CPI + 5 min] = [07:25, 07:35] CT (CPI 08:30 ET, C9). Such an entry is skipped for the day, not deferred. On MGC, SIL and MHG an opening fill in the window is at most 3 contracts. Only K5-cp2-01 on copper can open inside the window (C11) |
| D2 | Vehicle "D2 (chosen in E.2)" throughout. Every entry is written for every exposure its evidence names, each traded only if D2 admits the exposure |

### Common conventions (apply to every entry unless it says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose ts_event
  (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values can be used
  from then on. US Eastern times convert to CT by subtracting one hour, since both zones change clocks on
  the same dates. London times convert by C10.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open, the engine convention
  that D6 and D15.3 use. "Market intent on the bar at X" fills at the open of the bar at X + 1 min.
- **C3 Trade date and hours.**
  - Trade date d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md).
  - Metals Globex hours: "CME Globex Open: Sunday 5:00 p.m. - Friday 4:00 p.m. CT with a daily
    maintenance period from 4:00 p.m. - 5:00 p.m. CT" (K5 log 3.0, CME weekly metals options fact card).
    E.2 confirms the futures hours; the futures pages did not show them in the captures read.
  - So the first bar of trade date d is the 17:00 CT bar of d-1 (Sunday for a Monday). A London-morning
    auction on calendar date d (03:45-07:00 CT) falls in trade date d.
- **C4 Exclusions for the four new members.** The ports follow D6 as written. A new member does not trade
  on:
  - roll-blackout dates (`screen_candidate` with `roll_blackout`, the program convention);
  - dates the D10 metals calendar marks as early close or early halt (Family H's "Days with
    early_halt_ct set: no trade");
  - dates on which a bar the rule reads, or its entry-intent bar, is missing, or on which the signal bars
    of one computation carry different instrument_ids.

  If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced flatten
  at F is the backstop.
- **C5 Flat time.** F = 15:08 CT for every K5 product (D9.1; D6 rows: gold O 07:20, C 12:30; silver O
  07:20, C 12:25; copper O 07:10, C 12:00; platinum O 07:20, C 12:05). No new member's last fill is later
  than 13:19 CT.
  - The log verifies C for gold and copper against CME's settlement periods: GC "13:29:00 to 13:30:00 ET"
    (12:29-12:30 CT) and HG "12:59:00 to 13:00:00 ET" (11:59-12:00 CT) (K5 log 3.0).
  - Silver's 12:25 and platinum's 12:05 are not verified in E.0. D6 says E.2 confirms them.
- **C6 Size.** q_c of the exposure's D2 vehicle, never above 1 lot-equivalent (D2, D9.5) and within the
  50K volatility caps (D9.11). No member sizes by signal.

  | Contract | Lot-equivalent (D9.6) | D2 cap (1 lot) | D9.11 cap, 50K | Largest q_c |
  |---|---|---|---|---|
  | GC | 1 | 1 | 3 | 1 |
  | MGC* | 0.1 | 10 | 30 | 10 |
  | SI | 1 | 1 | 0 at Topstep's discretion | 1 (may be suspended) |
  | SIL* | 0.2 | 5 | 2 | **2** |
  | HG | 1 | 1 | 0 at Topstep's discretion | 1 (may be suspended) |
  | MHG | 0.1 | 10 | 2 | **2** |
  | PL | 1 | 1 | 0 at Topstep's discretion | 1 (may be suspended) |

- **C7 Ticks and fees.** Ticks are from reports/stage_e0_liquidity.json (CME contract specifications,
  fetched 2026-09-23 20:48 PDT). Round turns are Topstep F3.

  | Contract | Tick | Tick value | Topstep round turn | Round turn in ticks |
  |---|---|---|---|---|
  | GC | 0.10 | $10.00 | $4.32 | 0.43 |
  | MGC | 0.10 | $1.00 | $1.92 | 1.92 |
  | SI | 0.005 | $25.00 | $4.32 | 0.17 |
  | SIL | 0.005 | $5.00 | $2.72 | 0.54 |
  | HG | 0.0005 | $12.50 | $4.32 | 0.35 |
  | MHG | 0.0005 | $1.25 | $1.92 | 1.54 |
  | PL | 0.10 | $5.00 | $4.32 | 0.86 |

  - Within each exposure both contracts have the same tick in price units (0.10, 0.005, 0.0005). So CP2's
    buffer, "4 ticks of the exposure's most active contract", and every tick-denominated ML feature mean
    the same price distance whichever vehicle D2 picks.
  - These are 2026 specifications. E.2 confirms each tick was unchanged over 2019-05..2026-06 before any
    bar is read.
- **C8 Price data.** Databento GLBX.MDP3 ohlcv-1m of the vehicle. It is paid: the research window is bought
  in E.1, and the confirmation and holdout-2 history of the chosen vehicle in E.2b (D13).
  - **History.** GC, SI, HG and PL exist from 2019-05. MGC was listed 2010-10-04 and SIL in June 2013
    (year inferred, liquidity JSON). MHG was listed 2022-05-02, and its quotes before 2022-04 failed (D13).
    If D2 picks MHG, E.2 may declare HG's bars as the price path for the confirmation window (D2, D4).
  - **Availability.** A bar is available at its close (C1).
  - **Tick-free rules.** The new members' signals are signs (K5-pmfix-01, K5-fomc-01), percent returns
    (K5-ovr-01) or nothing (K5-preauc-01). They give the same decision on either contract of an exposure.
  - mbp-1 enters only through D8's shared five-date cost sample. No member reads order-book data.
- **C9 Event calendars.** All are external and free. Each supplies dates and scheduled clock times only.
  - **EC-LBMA, LBMA auction start times (London).** Gold 10:30 (AM) and 15:00 (PM); silver 12:00; platinum
    09:45 (AM) and 14:00 (PM).
    - Sources: the IBA page (current and the 2019 capture above) and the LBMA platinum page (K5 log 3.0).
    - The schedule is fixed and known in advance. The results "do not have set publication times" (LBMA
      page, K5 log 3.0), so no rule times itself on a result, and no rule reads one.
    - A scheduled auction day is a weekday that is not an England-and-Wales bank holiday in EC-UKBH.
    - A member trades every scheduled auction day as scheduled. No day is dropped after the fact, for
      example because an auction started late; that would be look-ahead.
    - E.2 confirms the platinum times for 2019-2021 (LME era) and checks for any UK half-day or special
      schedule announced in advance (IBA and LME notices). A day announced in advance as having no auction
      is not a scheduled auction day.
  - **EC-UKBH, UK bank holidays.** https://www.gov.uk/bank-holidays.json, England and Wales, 2019-01-01 to
    2028-12-26. The file lists dates years ahead, which shows they are published in advance.
  - **EC-FOMC, scheduled FOMC statement days.**
    - Sources: federalreserve.gov FOMC calendars (2021-2026 on the calendar page; 2019 and 2020 on the
      historical pages). The statement release time is read from each statement page ("For release at 2:00
      p.m. EDT", verified for 2019-07-31 and 2025-05-07). 14:00 ET = 13:00 CT.
    - Included: the second day of each scheduled meeting, when that page shows a 14:00 ET release.
    - Excluded: unscheduled meetings and actions, notation votes, and any statement released at another
      time.
    - Known in advance: the calendar is published before the year.
  - **EC-BLS, Employment Situation and CPI.** The BLS release schedules give each release at "08:30 AM" ET
    = 07:30 CT (verified in the 2019 captures above). The live pages refuse curl, so E.2 builds each year
    from Wayback captures dated before the releases.
    - A release whose actual date or time differs from the schedule published before it is handled as K4's
      C9 handles moved releases: the ML feature uses only the schedule known the evening before d.
    - The D8 cost and D9.5a guard use the actual release time, which can only make the harness more
      conservative.
  - **EC-G17, Fed G.17 Industrial Production and Capacity Utilization.** "The monthly releases are issued
    at 9:15 a.m." ET = 08:15 CT; historical release dates are published (page above). Used only for
    copper's D8 cost and D9.5a guard (C11).
  - **EC-CAL.** The D10 metals calendar (trade dates, holidays, early closes and halts), built by E.2 from
    CME schedules.
- **C10 London to Chicago conversion (every date, including the weeks when the US and UK change clocks on
  different dates).**
  - **Rule.** For an auction at London wall-clock time L on calendar date d:
    T_CT(d, L) = the America/Chicago wall-clock time of the instant whose Europe/London wall-clock time is
    L on d, computed with the IANA time-zone database (Python `zoneinfo`: build
    `datetime(d, L, tzinfo=ZoneInfo("Europe/London"))`, then `.astimezone(ZoneInfo("America/Chicago"))`).
  - **Equivalent statement.** London minus Chicago is 6 hours, except 5 hours from the US spring change
    (second Sunday of March) to the UK spring change (last Sunday of March), and from the UK autumn change
    (last Sunday of October) to the US autumn change (first Sunday of November).
  - **Weekday ranges with the 5-hour offset** (computed with `zoneinfo`; calendar arithmetic only):

    | Year | Spring (weekdays) | Autumn (weekdays) |
    |---|---|---|
    | 2019 | 2019-03-11..03-29 (15) | 2019-10-28..11-01 (5) |
    | 2020 | 2020-03-09..03-27 (15) | 2020-10-26..10-30 (5) |
    | 2021 | 2021-03-15..03-26 (10) | 2021-11-01..11-05 (5) |
    | 2022 | 2022-03-14..03-25 (10) | 2022-10-31..11-04 (5) |
    | 2023 | 2023-03-13..03-24 (10) | 2023-10-30..11-03 (5) |
    | 2024 | 2024-03-11..03-29 (15) | 2024-10-28..11-01 (5) |
    | 2025 | 2025-03-10..03-28 (15) | 2025-10-27..10-31 (5) |
    | 2026 | 2026-03-09..03-27 (15) | 2026-10-26..10-30 (5) |

  - **Auction start times in CT:**

    | Auction (London) | CT, normal (6 h) | CT, 5-hour weeks |
    |---|---|---|
    | Platinum AM 09:45 | 03:45 | 04:45 |
    | Gold AM 10:30 | 04:30 | 05:30 |
    | Silver 12:00 | 06:00 | 07:00 |
    | Platinum PM 14:00 | 08:00 | 09:00 |
    | Gold PM 15:00 | 09:00 | 10:00 |

    The log's K5-010 and K5-012 entries give the same conversion. Run 1's "05:00 CT-ish" was corrected
    there.
  - **Worked check.** 10:30 GMT = 04:30 CST (UTC-6); 10:30 BST = 09:30 UTC = 04:30 CDT; on 2025-03-12,
    10:30 GMT = 10:30 UTC = 05:30 CDT.
- **C11 Releases K5 names for D8's event-window cost and D9.5a's fill guard.** D8 reads "Topstep's
  release table, F6.4, plus the releases the product's catalog members name".

  | Release (CT) | Gold | Silver | Copper | Platinum | Basis |
  |---|---|---|---|---|---|
  | Employment Situation 07:30 | yes | yes | yes | no | F6.4 "Unemployment Rate / 7:30 AM" names GC, SI, HG ("**Micro contracts also apply"); P-K5-014-a, P-K5-014-c |
  | CPI 07:30 | yes | yes | yes | yes | D9.12 names GC, SI, HG, PL and the micros; P-K5-015-a ("consumer price index") |
  | FOMC statement 13:00 | yes | yes | yes | yes | F6.4 "FOMC Statement / 1:00 PM / All products"; P-K5-024-a |
  | G.17 industrial production 08:15 | no | no | yes | no | P-K5-014-c: "Copper returns ... are more sensitive to the 9:15 set of announcements which include capacity utilization and industrial production" |
  | The exposure's own LBMA auction starts (C10) | yes | yes | n/a | yes | **D8 cost only, pending the lead** (section 7, item 1) |

  - **Effect on this catalog's rules.** No new-member or ML fill lands in [release, release + 2 min) for any
    row, auction starts included. Every new member and the ML member are timed so.
  - **Ports.** A port fill can land in a guarded minute: CP2 entries around 07:30, 08:15, 09:00 or 10:00 CT,
    and CP2 exits at 13:00-13:01. The harness defers such a fill (D9.5a).
  - **CP2 on copper in the CPI window.** If the vehicle is HG, an opening fill in [07:26, 07:35] on a CPI
    day is skipped for the day (D9.12). A fill deferred by D9.5a to 07:32 would still be inside the window,
    so the skip takes precedence. On MHG (q <= 2 <= 3) the fill is allowed.
  - **Durable goods (08:30 ET)** is also among Elder's largest-impact releases for gold and silver
    (P-K5-014-a). It is not named because its schedule source was not confirmed (Census page 404; section
    7, item 2).
- **C12 Frequency (arithmetic from calendar counts, no price data).**
  - **Research window 2025-04-01..2026-06-19:** 319 weekdays, 12 of them England-and-Wales bank holidays.
    About 305 CME trade dates (K4 catalog C11, same window). About 290-300 dates are both CME trade dates
    and scheduled auction days, before roll-blackout exclusions (E.2 gives the exact count). 20 weekdays
    fall in 5-hour weeks (2025-10-27..31, 2026-03-09..27).
  - **FOMC statement days in the research window, 10:** 2025-05-07, 06-18, 07-30, 09-17, 10-29, 12-10;
    2026-01-28, 03-18, 04-29, 06-17 (fomccalendars.htm).
  - **Confirmation window 2019-05-06..2024-02-29** (the earliest S_X): 1,259 weekdays, 41 England-and-Wales
    bank holidays, 70 weekdays in 5-hour weeks. About 37-38 scheduled statement days (eight a year; E.2
    counts them from EC-FOMC).
  - **Consequence.** A member trading on k of about 305 research dates, with zeros on the rest (D5), needs a
    net P&L per event of about (305 / k) x eps_X to reach eps_X per trade date. That is about 1 x for the
    daily members and about 30 x for K5-fomc-01 (section 7, item 4).
- **C13 Price-limit proximity (D9.7).** Whether COMEX and NYMEX metals carried daily price limits or

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  dynamic circuit breakers over 2019-2026 is not verified in E.0 (outside this task's permitted fetches).
  - E.2 builds the per-product table from CME rules, and decides with the user whether Topstep's "Holding a
    position within 2% of a product's price lock limit" [F2.1] applies to a dynamic band.
  - If it does, it is encoded as D9.7: no entry, and an immediate exit, while the price is within 2% of the
    limit. The catalog assumes no limit either way.
- **C14 Member-level coverage (D9).** Each member's own window must show ohlcv-1m coverage >= 0.95 on the
  research window for its vehicle before it is screened. D1 measured coverage only in 07:20-12:30 CT.
  - Outside that window are K5-preauc-01 (03:15-06:59 CT, by exposure) and the first ML position
    (07:16-07:20).
  - A trial whose window fails is excluded before screening, with the reason logged. Platinum's 03:15-03:44
    window is the likeliest to fail (section 7, item 3).

---

## 1. Members

### K5-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K5. **Products read:** the traded exposure's own vehicle only.
- **Traded exposures** (each a separate trial): gold {GC, MGC}, silver {SI, SIL}, copper {HG, MHG},
  platinum {PL}. Each is traded only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log A10
  and A28; reports/stage_d1b_family_f_declaration.md F3.3), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the trade
    date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the
    signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min
    (fills at the next open). Both signal bars must exist with one instrument_id, else no trade."
  - **D6 note, verbatim:** "Every port trades q_c of the exposure's D2 vehicle and follows D9 (flat by F,
    trade-through for any limit order, which none of the three uses)." D6's text governs this entry.
  - **K5 log:** K5-028's same-day continuation after an abnormal gold return ("Prices tend to move in the
    direction of abnormal returns till the end of the day when these occur", P-K5-028-a) is the same family
    (intraday continuation). It is recorded as **covered by CP1** for the unconditional form; its threshold
    variant is excluded (X-07). The reader's rejected R-K5-018 (Rosa, generic intraday momentum) is also
    this family.
- **Instantiated** (D6 rows; the first bar of trade date d is the 17:00 CT bar of d-1, C3):

  | Exposure | O / C / F | Signal: open of first bar to close of bar at | Entry intent bar, fill | Exit intent bar, fill | Hold |
  |---|---|---|---|---|---|
  | gold | 07:20 / 12:30 / 15:08 | 07:49 (known 07:50) | 11:59, 12:00 | 12:28, 12:29 | 29 min |
  | silver | 07:20 / 12:25 / 15:08 | 07:49 | 11:54, 11:55 | 12:23, 12:24 | 29 min |
  | copper | 07:10 / 12:00 / 15:08 | 07:39 | 11:29, 11:30 | 11:58, 11:59 | 29 min |
  | platinum | 07:20 / 12:05 / 15:08 | 07:49 | 11:34, 11:35 | 12:03, 12:04 | 29 min |

  - **Holding horizon:** 29 minutes on every exposure.
  - **Session window:** the entry-to-exit rows above. Flat at least 2 h 39 min before F (gold's 12:29).
  - The gold exit fill (12:29) is the first minute of GC's settlement period, and copper's (11:59) of HG's
    (C5). This is how the port falls on these products; it is not a design choice.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8). Paid; history 2019-05..2026-06
  (MHG from 2022-05, C8). The signal is known at O+30 CT.
- **Order type:** market. **Sizing:** q_c (C6).
- **Parameters:** O+29, C-31 and C-2 as instantiated (D6). **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date (D6 criterion 2), held 29 minutes. Floor:
  at most 20 entries a day, 2-minute minimum and 10-minute mean hold, all ok.
- **Falsification:** the standard condition only (a port; D6 unchanged): UCB95 of the member's mean net
  daily P&L per contract below eps_X at >= 80% achieved null power on the confirmation window counts
  against it.
- **Topstep check:**
  1. Flat by F: last fill 12:29.
  2. Order type: market.
  3. D9.4: one trade a day; no stops, brackets or passive fills.
  4. Star rules: MGC or SIL if D2 picks them. Size is within D9.11 (C6), and no fill falls in the CPI
     window.
  5. News: <= 1 lot-equivalent, half the 2-lot maximum.
  6. D9.5a guard: no fill in any C11 minute.
  7. CPI window: no opening fill in [07:25, 07:35].
  8. Position and volatility caps: within C6. SI, HG and PL may be suspended at Topstep's discretion.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of each admitted K5 vehicle over the research window 2025-04-01..2026-06-19
  and the confirmation window S_X..2024-02-29 (D4). No external data.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K5-cp2-01 (core port CP2, opening-range breakout)
- **Cluster** K5. **Products read:** own vehicle.
- **Exposures:** gold, silver, copper, platinum, one trial each, each traded only if D2 admits it.
  **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py, hold_minutes = 75), as
  fixed in D6 row CP2 with the 21:12 amendment and the 21:52 ruling.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first bar
    opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market intent in
    the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes after the fill, or
    the engine's forced flatten at F if earlier."
  - **D6 note, verbatim:** ""4 ticks of P" in CP2 means 4 minimum price increments of the exposure's most
    active contract (D1 table), in price units, fixed whatever vehicle D2 chooses."
  - **K5 log:** no K5 source tests an opening-range breakout on a metals futures contract. K5-008's 60-minute
    Keltner-channel breakout is family G, not this port (X-08).
- **Instantiated:**

  | Exposure | OR bars | Eligible entry bars | Buffer = 4 ticks of the most active contract | Per contract | Earliest / latest entry fill | Latest exit |
  |---|---|---|---|---|---|---|
  | gold | [07:20, 07:35) | opening in [07:35, 12:30) | MGC tick 0.10, so 0.40 | GC $40, MGC $4 | 07:36 / 12:30 | 13:45 |
  | silver | [07:20, 07:35) | [07:35, 12:25) | SIL tick 0.005, so 0.020 | SI $100, SIL $20 | 07:36 / 12:25 | 13:40 |
  | copper | [07:10, 07:25) | [07:25, 12:00) | HG tick 0.0005, so 0.0020 | HG $50, MHG $5 | 07:26 / 12:00 | 13:15 |
  | platinum | [07:20, 07:35) | [07:35, 12:05) | PL tick 0.10, so 0.40 | PL $20 | 07:36 / 12:05 | 13:20 |

  - **Entry:** the first eligible bar whose close is >= OR_high + buffer buys; one whose close is <= OR_low -
    buffer sells. One entry per trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it. The exit intent is emitted on
    the 75th bar after the entry-intent bar and fills at the next open. The engine's flatten at F is the
    backstop and never binds on a full session.
  - **Holding horizon:** 75 minutes.
- **Data fields read:** vehicle ohlcv-1m high, low, close and instrument_id (C8). The range is known at O+15.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** OR 15 minutes, buffer 4 ticks of the most active contract, hold 75 minutes (D6, a literal
  port). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held 75 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: latest exit 13:45.
  2. Order type: market.
  3. D9.4: one trade a day, no stops.
  4. Star rules: MGC or SIL per C6.
  5. News: <= 1 lot-equivalent. A position may be open at 07:30, 08:15 (copper) or 13:00 CT releases,
     which F6.3 allows below the full maximum.
  6. D9.5a: entry fills that would land at 07:30-07:31 (Employment Situation or CPI days), 08:15-08:16
     (copper, G.17 days) or at an auction-start minute (if the lead confirms, C11), and exits at
     13:00-13:01 on FOMC days, are deferred by the harness.
  7. CPI window: gold, silver and platinum entries start at 07:36, outside it. **Copper on HG: entries whose
     fill falls in [07:26, 07:35] on CPI days are skipped for the day (C11); on MHG they are allowed.**
  8. Position and volatility caps: C6.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of the admitted vehicles, research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K5-cp3-01 (core port CP3, prior-close location)
- **Cluster** K5. **Products read:** own vehicle.
- **Exposures:** gold, silver, copper, platinum, each traded only if D2 admits it. **Vehicle:** D2 (chosen in
  E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6;
  strategy/research/h_daily_bar/h6_prior_close_location.py), as fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L over [O,
    C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family H. CLV = (C_d -
    L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market intent on the O bar of day
    d. Exit: first bar at or after C-2 min."
  - **Family H rules carried over** (2.1 A3):
    - A day is complete only if its O bar and C-1 bar exist, it has no early halt, and all its bars in
      [O, C) carry one instrument_id.
    - Instrument guard: d-1's daily bar must carry the instrument_id of day d's O bar.
    - CLV cuts are non-strict.
  - **K5 log:** no K5 source tests a prior-day follow-through on metals. K5-028's next-day effect for gold is
    contrarian, the opposite sign, and "Not rejected" against random (P-K5-028-e, P-K5-028-f), so it is not
    evidence for or against this port (X-07).
- **Instantiated:**

  | Exposure | Daily bar | C_d = close of the bar at | Entry intent bar, fill | Exit intent bar, fill | Hold |
  |---|---|---|---|---|---|
  | gold | [07:20, 12:30) | 12:29 | 07:20, 07:21 | 12:28, 12:29 | 308 min |
  | silver | [07:20, 12:25) | 12:24 | 07:20, 07:21 | 12:23, 12:24 | 303 min |
  | copper | [07:10, 12:00) | 11:59 | 07:10, 07:11 | 11:58, 11:59 | 288 min |
  | platinum | [07:20, 12:05) | 12:04 | 07:20, 07:21 | 12:03, 12:04 | 283 min |

  CLV is computed with Range[d-1] > 0. CLV >= 0.8 buys; CLV <= 0.2 sells.
  - **Holding horizon:** 283-308 minutes, by exposure (table).
  - **Session window:** from the O + 1 fill to the C - 1 fill. Flat at least 2 h 39 min before F.
- **Data fields read:** vehicle ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's bar is
  complete at C on d-1.
- **Order type:** market. **Sizing:** q_c.
- **Parameters:** CLV cuts 0.2 and 0.8; lookback 1 (D6, H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held 283-308 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 12:29.
  2. Order type: market.
  3. D9.4: ok.
  4. Star rules: C6.
  5. News: holds through the 07:30 releases, the gold PM auction, G.17 (copper) and never FOMC (exits by
     12:29), at <= 1 lot-equivalent.
  6. D9.5a: no fill in a guarded minute.
  7. CPI window: the entry fill at 07:11 or 07:21 is before 07:25.
  8. Caps: C6.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of the admitted vehicles, research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K5-preauc-01 (short into the LBMA auctions held outside US trading hours)
- **Cluster** K5. **Products read:** the traded exposure's vehicle; EC-LBMA; EC-UKBH; EC-CAL.
- **Traded exposures** (each a separate trial; each only if D2 admits it and its window passes C14):
  - gold {GC, MGC}, into the gold AM auction (10:30 London);
  - silver {SI, SIL}, into the silver auction (12:00 London);
  - platinum {PL}, into the platinum AM auction (09:45 London). [REMOVED by the lead, 01:47 PDT 2026-09-24, answering this writer's question 3: one abstract (Nilsson) supports the member, and platinum carries the coverage and "may be suspended" risks; K5-preauc-01 is kept on gold and silver only, 2 trials.]

  **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed** (K5-002, P-K5-002-a): "We find that there is negative price pressure going into the
    auctions, for all precious metals, outside active US trading hours regardless of Fixing structure. For
    active US trading hours, there is no obvious, observable persistent price pressures." "Regardless of
    Fixing structure" covers both the telephone fix and the electronic auctions of 2014-2015 onward, the
    regime of the program's windows.
  - **Which auctions (reasoning; the passage does not define "active US trading hours").**
    - The three auctions traded here start at 03:45-07:00 CT (C10), before the metals day session opens
      at 07:20 CT (D6). The old COMEX floor opened at 08:20 ET (07:20 CT): "All announcements occur at
      08:30AM (EST), just 10-minutes after the official market open" (P-K5-019-b); "the COMEX opens at
      8:20 a.m. EST" (P-K5-020-a).
    - The gold PM auction (09:00 or 10:00 CT) and the platinum PM auction (08:00 or 09:00 CT) fall inside
      US trading hours. The passage's second sentence says those show no persistent pressure, so they are
      not traded.
  - **Microstructure context (a cost headwind, not evidence for or against the drift).**
    - "quoted spreads are typically at their highest point immediately prior to the start of the fix"
      (K5-012, P-K5-012-f).
    - "we observe a noticeable decline in depth prior to the start of the fix" (P-K5-012-g).
    - The exit is therefore placed one minute before the start (Parameters), and C11 names the auction for
      D8's cost.
  - **What the log does not contradict.** K5-012's post-reform "no significant leakage prior to the start
    of the fix" (P-K5-012-i) concerns informed returns signed by the eventual fix direction. It does not
    address an unsigned downward pressure, so it is not a direct test of this claim. No source in the log
    tests pre-auction pressure after 2015 on its own.
  - **Evidence quality.**
    - Abstract only: SSRN blocked, no mirror (K5 log).
    - A practitioner working paper, never published.
    - The window length, magnitude, costs and data window are [unverified].
    - The lead may cut it (section 7, item 3).
  - **Classification:** new to the program (a London-auction clock effect specific to precious metals). It
    is not a D.1 family A port: its reference clock is the auction, not the product's session. It is
    written as a product-specific test under partition rule 6.
- **Entry rule.**
  - **Days:** each eligible trade date d (C4) on which d is a scheduled auction day (C9 EC-LBMA, EC-UKBH).
  - **Auction time:** T = T_CT(d, L_X) (C10), with L_X = 10:30 (gold), 12:00 (silver) or 09:45
    (platinum). That gives T = 04:30 or 05:30 CT (gold), 06:00 or 07:00 (silver), 03:45 or 04:45
    (platinum).
  - **Order:** SELL q_c. Market intent on the bar at T - 31 min, filling at the open of the bar at
    T - 30 min.
  - **Conditions:** unconditional; there is no signal. If the bar at T - 31 is missing, there is no trade
    that day (no late entry).
- **Exit rule:** market intent on the bar at T - 2 min, filling at the open of the bar at T - 1 min (C4 if
  that bar is missing).
- **Holding horizon:** 29 minutes. **Session window:** [T - 30, T - 1], for example gold 04:00-04:29 CT in
  normal weeks. Flat more than eight hours before F.
- **Data fields read:**
  - The vehicle's ohlcv-1m bar existence and instrument_id at T - 31 and T - 2, and the fills (C8). Paid;
    history 2019-05 on (MHG not involved). Available at each bar's close.
  - EC-LBMA and EC-UKBH (C9). Free, 2019-2026 available, known in advance.
  - EC-CAL (E.2).
  - No auction result is read.
- **Order type:** market. **Sizing:** q_c (C6: SIL at most 2; MGC at most 10; GC, SI, PL 1).
- **Parameters.**
  - **Window of 30 minutes before the auction: a judgment.** It is the pre-fix span of K5-012's event
    window, which the K5 log's product line for K5-012 describes as "a window from 30 minutes before to 60
    minutes after the fix start". That line is the reader's description, not a quoted passage.
    Nilsson's own window is not in the passage.
  - **Exit at T - 1: a judgment.** It is the last full minute before the start. It avoids the start minute,
    where spreads peak (P-K5-012-f), and keeps the member out of any D9.5a window should the lead count
    auction starts as releases (section 7, item 1).
  - **Grid:** none.
- **Expected entries and hold:** 1 per eligible date per exposure: about 290 research and about 1,150
  confirmation dates per exposure before roll-blackout exclusions (C12). Held 29 minutes. Floor ok (1 entry
  a day; 29-minute holds).
- **Falsification.**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean over traded dates of (open at T - 30 minus open at T - 1), in ticks
    (the gross return of the short), is positive.
  - **Descriptive clock control (not a trial):** the same statistic for the window one hour earlier (open
    at T - 90 minus open at T - 61). It separates an auction effect from a clock-wide overnight drift.
- **Topstep check:**
  1. Flat by F: last fill no later than 06:59 CT.
  2. Order type: market.
  3. D9.4: one trade a day, entered 30 minutes before a scheduled event, not in a gapped market; no stops.
  4. Star rules: SIL at most 2, MGC at most 10 (C6).
  5. News: no C11 release in any window (07:30 is after the latest exit, 06:59). <= 1 lot-equivalent.
  6. D9.5a: no fill in [T, T + 2) or in any C11 minute.
  7. CPI window: all fills before 07:00, outside it.
  8. Caps: C6. **Platinum may be suspended** (D9.11).
  9. Price limit: C13.
  - Also C14: each window lies outside D1's coverage window, and platinum's 03:15-03:44 is the likeliest
    to fail the member-level check.
- **Data needed:** ohlcv-1m of the gold, silver and platinum vehicles over 03:00-07:00 CT and the fills'
  buckets, in the research and confirmation windows. D8 needs slippage buckets for 03:00-07:00 CT. External:
  EC-LBMA, EC-UKBH, EC-CAL.
- **Trials in N:** 3 (one per exposure).

### K5-pmfix-01 (gold PM auction: continuation of the auction's first two minutes)
- **Cluster** K5. **Products read:** the gold vehicle; EC-LBMA; EC-UKBH; EC-CAL.
- **Traded exposure:** gold {GC, MGC}, only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** The seed of the K5 region (partition section 3: "the LBMA gold price auctions ... and their
  effect on COMEX futures (seed: Caminschi and Heaney 2014, JFM)").
  - **For (legacy telephone fixing, GC, 2007-2012, K5-001):**
    - "Trades in the opening minutes of the fixing are significantly predictive of the price direction of
      the fixings, in some cases exceeding 90%" (P-K5-001-a).
    - "trades in GC and GLD following the start of the fixing are found to be predictive of the fixing
      price direction, with higher prediction rates (80-95%) for fixings resulting in larger price
      movements" (P-K5-001-c).
    - An informed advantage of "around 10bps in the four minutes following the start of the fixing, and a
      possible further 4bps in the two minutes before the end" (P-K5-001-c).
    - Trade volume up over 50% and volatility up over 40% after the start (P-K5-001-b).
    - K5-012: in "the former fix period, significant return advantages accrue to informed participants
      ahead of the announcement of the benchmark price ... consistent across all the precious metals"
      (P-K5-012-d).
    - Crain et al. (K5-006), trend-controlled: "the fix change significantly increased volatility of prices
      in silver and gold markets" (P-K5-006-f); "the gold fix change led to an increase in volatility in gold
      futures following the change to the gold fixing process" (P-K5-006-g). So the fix window may remain
      eventful after the reform.
  - **Against (post-reform electronic auction):**
    - K5-012 finds "a reduction in the adjusted returns, volatility, and return predictability of the
      associated futures contract" (P-K5-012-a).
    - "there is no significant leakage prior to the start of the fix and within minutes of the start, most of
      the price discovery process is complete" (P-K5-012-i).
    - "For gold and silver, the fix is almost always complete within ten minutes of the opening submission"
      (P-K5-012-h).
    - The gold post-reform change is "statistically insignificant", attributed to "the small sample of data
      in the post period" (P-K5-012-e).
    - "reforms to the Fix have reduced quoted and effective bid-ask spreads and improved overall market
      depth" (K5-013, P-K5-013-a).
    - Crain et al., raw: "the standard deviations are significantly lower in the post-fix change period"
      (P-K5-006-c).
    - Crain's evidence on both sides is DAILY (P-K5-006-b), so it bears on the fix window only indirectly.
    - Old regime, end of the fixing: "the two minutes leading to the end of the fixing do show statistically
      significant negative returns ... overshoot" (P-K5-001-g), and "no significant returns following the
      end of the fixing" (P-K5-001-c).
  - **What a public trader can use (reasoning).**
    - Caminschi's return advantage belongs to "an informed trader, with directional foresight of the fixing
      price" (P-K5-001-f), which no rule has.
    - What is observable is the price change in the auction's first minutes. The source's predictor is
      trade direction; ohlcv-1m has no trade sign, so the price change is the proxy.
    - The member tests whether the direction of the first two minutes continues over the next ten, that
      is, whether part of the move toward the auction price is still ahead after two minutes.
    - The post-reform evidence leans against it. The member is the direct test of the seed in the
      program's 2019-2026 windows.
  - **Confound, not conditioned on:** in normal weeks T_P = 09:00 CT = 10:00 ET, the release time of several
    US data series that are not in C11. The rule does not condition on them.
  - **Classification:** new to the program.
- **Entry rule.**
  - **Days:** eligible trade dates (C4) that are scheduled gold PM auction days (C9).
  - **Auction time:** T_P = T_CT(d, 15:00) (C10): 09:00 CT, or 10:00 CT in 5-hour weeks.
  - **Signal:** s = close of the bar at T_P + 1 min minus close of the bar at T_P - 1 min, that is, from the
    last pre-auction minute to the end of the auction's second minute. Both bars must exist with one
    instrument_id.
  - **Order:** s > 0 BUY q_c; s < 0 SELL q_c; s = 0 no trade. Market intent on the bar at T_P + 1 (emitted
    at T_P + 2), filling at the open of the bar at T_P + 2.
- **Exit rule:** market intent on the bar at T_P + 11, filling at the open of the bar at T_P + 12.
- **Holding horizon:** 10 minutes. **Session window:** 09:02-09:12 CT, or 10:02-10:12 CT in 5-hour weeks.
  Flat by F.
- **Data fields read:**
  - Gold vehicle ohlcv-1m close and instrument_id at T_P - 1 and T_P + 1 (C8). Paid; available at the
    close of the bar at T_P + 1, which is T_P + 2.
  - EC-LBMA and EC-UKBH (C9). Free, 2019-2026, known in advance.
  - EC-CAL.
  - No auction result is read.
- **Order type:** market. **Sizing:** q_c (GC 1 or MGC at most 10).
- **Parameters.**
  - **Signal span of 2 minutes: a judgment.** It lies inside the source's "4 minutes following the start"
    (P-K5-001-c) and its "opening minutes" (P-K5-001-a). It is also the shortest span that puts the entry
    fill at or after T_P + 2, outside [T_P, T_P + 2) should the auction start count for D9.5a.
  - **Hold of 10 minutes: a judgment.** It is D9.3's minimum mean hold. The exit comes 12 minutes after
    the start, just after the post-reform auction "is almost always complete within ten minutes"
    (P-K5-012-h).
  - **No size threshold: a judgment.** The source's higher prediction rates for larger moves (P-K5-001-c)
    suggest one, but no threshold value is logged, so the split is reported descriptively (Falsification).
  - **Grid:** none.
- **Expected entries and hold:** about 1 per eligible date (about 290 research and 1,150 confirmation dates,
  less s = 0 days). Held 10 minutes. Floor: the 10-minute mean hold is met exactly, at the boundary.
- **Falsification.**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(s) x (open at T_P + 12 minus open at T_P + 2), in ticks, on
    traded days is positive.
  - **Descriptive split (not a trial):** the same statistic for |s| above and at-or-below the research
    window's median |s|, following P-K5-001-c's larger-move result.
- **Topstep check:**
  1. Flat by F: last fill 10:12 at the latest.
  2. Order type: market.
  3. D9.4: one trade a day, entered two minutes after a scheduled auction start, not a gapped release
     minute; no stops.
  4. Star rules: MGC per C6.
  5. News: no C11 release inside the window. <= 1 lot-equivalent.
  6. D9.5a: fills at T_P + 2 and T_P + 12 are outside [T_P, T_P + 2). If the lead confirms C11's auction
     row, both fills pay D8's largest-bucket cost (fills within 30 minutes after the start).
  7. CPI window: outside it.
  8. Caps: C6.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of the gold vehicle, research and confirmation windows. External: EC-LBMA,
  EC-UKBH, EC-CAL.
- **Trials in N:** 1.

### K5-fomc-01 (gold: continuation of the first five minutes after the FOMC statement)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source covers 2007-2020, overlapping the confirmation window.]
- **Cluster** K5. **Products read:** the gold vehicle; EC-FOMC; EC-CAL.
- **Traded exposure:** gold {GC, MGC}, only if D2 admits it. **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed** (K5-024, Awartani, Hussain, Virk 2024; GC 5-minute data 2007-2020, P-K5-024-c):
    - "we find that the gold price adjustment and its volatility adjustment continue for longer than five
      minutes after the FOMC shock. This suggests potential short-term inefficiencies in the gold market
      concerning the short-term rates" (P-K5-024-a).
    - "positive monetary policy shocks tend to reduce the price of gold ... However, the adjustment 10
      minutes after the shock is significantly threefold higher than after 5 minutes" (P-K5-024-b).
    - "The gold returns and volatility 5 min after the shock are found to be more sensitive to looser than
      tighter FOMC rate announcement changes" (P-K5-024-a).
  - **The rule-3 route.** The source's surprise measure is not in the logged passages. A fed-funds-futures
    surprise would be a rates leg, which is K8's (section 4). The proxy is gold's own first five minutes.
  - **Reasoning.**
    - A tightening shock lowers gold (P-K5-024-b). When the shock dominates the first five minutes, the sign
      of gold's move over 13:00-13:05 CT is the sign of the gold response to the surprise.
    - The 10-minute adjustment is three times the 5-minute one, so the response continues in that
      direction between minutes 5 and 10.
    - The loosening/tightening asymmetry does not enter a sign rule.
  - **Counter-evidence in the log (other events).**
    - For 08:30 ET releases, gold's reaction is fast: "the majority of the reaction complete within 90-s"
      (K5-004, P-K5-004-a); "returning to normal within approximately 2½-min" (K5-019, P-K5-019-c).
    - Elder et al.: "the effect of macroeconomic news dissipates quickly, within about 60 minutes"
      (P-K5-014-d).
    - The source's "inefficiency" is not costed (log quality tells).
    - K5-030 (Gu, Kurov, Stan 2023, FOMC and commodity markets) was never read and is not used.
  - **Classification:** port of D.1 family E (FOMC event), tested on gold specifically (rule 6). New member.
    Not extended to silver, copper or platinum: the evidence is gold-only (the lead's 21:52 Q6 logic).
- **Entry rule.**
  - **Days:** eligible trade dates (C4) that are EC-FOMC statement days, statement at 13:00 CT.
  - **Signal:** s = close of the bar at 13:04 minus close of the bar at 12:59. Both bars must exist with one
    instrument_id.
  - **Order:** s > 0 BUY q_c; s < 0 SELL q_c; s = 0 no trade. Market intent on the bar at 13:04, filling at
    the open of the bar at 13:05.
- **Exit rule:** market intent on the bar at 13:14, filling at the open of the bar at 13:15.
- **Holding horizon:** 10 minutes. **Session window:** 13:05-13:15 CT. Flat 113 minutes before F.
- **Data fields read:**
  - Gold vehicle ohlcv-1m close and instrument_id at 12:59 and 13:04 (C8). Paid; available at 13:05.
  - EC-FOMC (C9). Free, 2019-2026, published before each year; release time verified per statement page.
  - EC-CAL.
- **Order type:** market. **Sizing:** q_c.
- **Parameters.**
  - **Signal of 5 minutes:** the source's "5 min after the shock" (P-K5-024-a).
  - **Entry at 13:05:** the start of the 5-to-10-minute continuation (P-K5-024-b).
  - **Exit at 13:15: a judgment.** It is D9.3's 10-minute minimum mean hold. The last five minutes
    (13:10-13:15) lie beyond the source's 10-minute horizon.
  - **Grid:** none.
- **Expected entries and hold:** 10 research events (C12), about 37-38 confirmation events. Held 10
  minutes. Floor ok (mean exactly 10). Power: probably "inconclusive by design" (D4); the lead's 21:52 Q4
  ruling keeps low-frequency event members for the power check to decide (section 7, item 4).
- **Falsification.**
  - The standard condition.
  - **Sign check (reported):** the mean of sign(s) x (open at 13:15 minus open at 13:05), in ticks, is
    positive.
- **Topstep check:**
  1. Flat by F: last fill 13:15.
  2. Order type: market.
  3. D9.4: one trade per meeting, entered five minutes after the statement, not in the release minute;
     no stops.
  4. Star rules: MGC per C6.
  5. News: the position opens after the release. <= 1 lot-equivalent.
  6. D9.5a: fills at 13:05 and 13:15 are outside [13:00, 13:02). Both are within 30 minutes after FOMC, so
     both pay D8's largest-bucket cost.
  7. CPI window: not applicable (13:05).
  8. Caps: C6.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of the gold vehicle, research and confirmation windows. External: EC-FOMC,
  EC-CAL.
- **Trials in N:** 1.

### K5-ovr-01 (hourly overreaction reversal)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP (same source and sample as K4-ovr-01, 2019-11-20 to 2020-06-03). K4-ovr-01 and K5-ovr-01 must carry one identical rule text (review R-24); E.1 checks it before hashing.]
- **Cluster** K5. **Products read:** each traded exposure's own vehicle; EC-CAL.
- **Traded exposures** (each a separate trial; each only if D2 admits it): gold, silver, platinum and copper.
  - These are the K5 exposures in the source's sample: "gold (GC), silver (SI), platinum (PL), palladium
    (PA), copper (HG)" (P-K5-029-b).
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism.**
  - **What is claimed** (K5-029, Borgards, Czudaj, Hoang 2021, a panel source claimed by K5):
    - Large intraday price changes beyond a decile threshold, at 1-minute to 1-hour frequencies, are
      followed by reversals.
    - "soft and metal commodities show much less overreactions than precious metals and especially energy
      commodities" (P-K5-029-a).
    - "almost all commodities have higher trading returns with exception of industrial metals which have a
      0.98% lower but still positive return in the first decile" (P-K5-029-c).
    - "the metals index would have generated a 4.0% (5.0%) compounded return over the pandemic period after
      positive (negative) first decile overreactions for the 1-h frequency" (P-K5-029-c).
    - Costs are asserted, not modelled: "the net-of-fees trading results would be still positive in both
      periods" (P-K5-029-d).
  - **Why copper is included.** "Metal commodities" in P-K5-029-a are the industrial metals (copper,
    aluminium, zinc, nickel in P-K5-029-b), which show fewer overreactions than the precious metals. Their
    first-decile return is "lower but still positive" (P-K5-029-c). The lead may cut copper (section 7,
    item 5).
  - **Evidence quality.**
    - About six months of data, 2019-11-20 to 2020-06-03, dominated by Covid (P-K5-029-a).
    - The holding period and threshold construction are [unverified].
    - The per-commodity tables were not transcribed (log quality tells).
  - **Classification:** a family C magnitude-conditioned reversal, tested per commodity. D6 does not port
    family C, so under partition rule 6 this is a cluster member. K4-ovr-01 uses the same panel source for
    energy (its [K4] passages). The judgments below are made independently, and where they coincide with
    K4's the entry says so, so that the lead can keep the source tested the same way across clusters.
- **Decision times:** t = O + 60k for k = 1, 2, ... while t <= C (D6 rows). Gold and silver: 08:20, 09:20,
  10:20, 11:20, 12:20 (five). Copper: 08:10, 09:10, 10:10, 11:10 (four). Platinum: 08:20, 09:20, 10:20,
  11:20 (four).
- **Signal:** r(t) = (close of the bar at t - 1 minus open of the bar at t - 60) / open of the bar at t -
  60, the return over the hour [t - 60, t). Both bars must exist with one instrument_id.
- **Reference set and cuts.**
  - The reference set is the values r(tau) at the same decision clock times on the 20 most recent earlier
    eligible trade dates (C4) of the exposure.
  - At least 80% of the possible values must exist: 80 of 100 for gold and silver, 64 of 80 for copper and
    platinum. Otherwise no trade at t.
  - P10 and P90 = np.percentile(values, [10, 90], method="linear").
  - Warm-up: the first 20 eligible dates of each window. No bars before the research window exist, because
    holdout-2 is sealed.
- **Entry rule.**
  - r(t) <= P10: BUY q_c. r(t) >= P90: SELL q_c. Otherwise no trade.
  - Market intent on the bar at t - 1, filling at the open of the bar at t.
- **Exit rule:** market intent on the bar at t + 58, filling at the open of the bar at t + 59. At most one
  position is open. The next decision's entry fills at t + 60, so positions never overlap.
- **Holding horizon:** 59 minutes. **Session window:** gold and silver 08:20-13:19; copper 08:10-12:09;
  platinum 08:20-12:19. Flat by F.
- **Data fields read:** vehicle ohlcv-1m open, close and instrument_id (C8), all closed at or before t, and
  earlier trade dates; EC-CAL. Paid; history 2019-05 on (MHG 2022-05, C8).
- **Order type:** market. **Sizing:** q_c.
- **Parameters.**
  - **60-minute signal and decile cuts:** the source's "1-h frequency" and "first decile" (P-K5-029-c). The
    symmetric cuts follow "positive (negative) first decile overreactions" (P-K5-029-c) and P-K5-029-d.
  - **20-trade-date trailing reference: a judgment.** It is the program's trailing-state length (D15.4 B4).
    The source's own threshold construction is not in the logged passages. This is the same length K4
    chose.
  - **59-minute hold: a judgment.** It is one signal period less the one minute that keeps positions from
    overlapping. The source's holding period is [unverified].
  - **Grid:** none.
- **Expected entries and hold:** by construction about 2 in 10 decision times qualify if the trailing
  distribution is stable. That is about 1 entry per day per exposure (at most 5), held 59 minutes. Floor ok.
- **Falsification.**
  - The standard condition, per exposure.
  - **Sign check (reported):** the mean of -sign(r(t)) x (open at t + 59 minus open at t), in ticks, is
    positive. It is reported split by the sign of r(t).
- **Topstep check:**
  1. Flat by F: last fill 13:19.
  2. Order type: market.
  3. D9.4: at most 5 entries a day, 59-minute holds, no stops or brackets. The first decision (08:10 or
     08:20) fades an hour that contains the 07:30 releases, 40-50 minutes after them, not in a gapped
     minute.
  4. Star rules: C6.
  5. News: gold and silver 12:20 positions hold through the 13:00 FOMC statement; copper 08:10 positions
     hold through G.17 (08:15). <= 1 lot-equivalent.
  6. D9.5a: fills fall at :20 and :19 (gold, silver, platinum) or :10 and :09 (copper). None is in a
     guarded minute (07:30-07:31, 08:15-08:16, 13:00-13:01, or an auction start at 08:00-08:01,
     09:00-09:01 or 10:00-10:01). Two groups of fills pay D8's largest-bucket cost:
     - the gold and silver 13:19 exit on FOMC days;
     - if C11's auction row is confirmed, fills within 30 minutes after the exposure's own auction start:
       gold at 09:19-09:20 (10:19-10:20 in 5-hour weeks) and platinum at 08:20 (09:19-09:20 in 5-hour
       weeks).
  7. CPI window: the first fill is 08:10, outside it.
  8. Caps: C6. Platinum may be suspended.
  9. Price limit: C13.
- **Data needed:** ohlcv-1m of all four admitted vehicles, research and confirmation windows.
- **Trials in N:** 1 per admitted exposure (at most 4).

### K5-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: the 01:47 fallback ruling (gold, then silver, then copper) governs; this entry's "No fallback is declared" is superseded; KF1-KF3 and KF5 remain gold-event features whichever metal becomes the vehicle.]
- **Traded vehicle: the gold exposure** {GC, MGC}; the contract is chosen by D2 in E.2. [Lead ruling, 01:47 PDT, question 6: fallback order if D2 does not admit gold: silver, then copper; the features stay as written, reading silver bars (an IN exposure) whether or not silver is traded.]
  - **Reason 1, the log:** gold is the exposure the K5 log documents most at intraday horizons. Of the 31
    passed K5 items, gold is a product in 27 (all but K5-009, K5-010, K5-023 and K5-030 [unverified]),
    silver in 14, platinum in 7, and copper in 4 (5 with K3-007). Each count is from the item's "Products"
    line in the log.
  - **Reason 2, activity:** gold has the cluster's highest public ADV (MGC 429,702 contracts a day,
    2026 Jan-Aug, D1 table).
  - **Reason 3, caps:** gold is the only K5 exposure none of whose contracts can be set to zero under
    D9.11.
  - **No fallback is declared.** The cluster features below are gold-specific (gold auctions, gold FOMC
    evidence). If D2 admits no gold contract, the lead decides.
- **Products the features read:**
  - The gold vehicle.
  - The silver vehicle's bars, for KF6. D13 buys history only for each traded exposure's chosen vehicle,
    so E.2 must add silver bars (SIL, the most active silver contract) if silver is not admitted.
  - Calendars: EC-LBMA, EC-UKBH, EC-FOMC, EC-BLS, EC-CAL.
- **Cluster features.** There are 7; with D15.4's B1-B5 that makes 12.
  - Throughout, t_j is the decision time, and "the bar at t_j - 1" is the last bar closed at t_j.
  - tick = 0.10 (GC and MGC alike, C7).
  - T_P(d) = T_CT(d, 15:00) and T_A(d) = T_CT(d, 10:30) (C10), defined on scheduled auction days (C9).

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | pm_minutes | If d is a scheduled gold PM auction day: t_j - T_P(d) in minutes (signed). Otherwise the literal 999 | K5-001 P-K5-001-a, P-K5-001-b; K5-012 P-K5-012-f, P-K5-012-g, P-K5-012-h, P-K5-012-i; K5-011 P-K5-011-f; K5-006 P-K5-006-f, P-K5-006-g | calendar and clock only; schedule known before d (C9) |
| KF2 | pm_open_move | If d is a PM auction day and t_j >= T_P + 2 min: (close of the bar at T_P + 1 - close of the bar at T_P - 1) / tick. Otherwise 0. On such a d with t_j >= T_P + 2, a missing bar or a change of instrument_id means no trade at t_j | K5-001 P-K5-001-a, P-K5-001-c, P-K5-001-g; K5-012 P-K5-012-h, P-K5-012-i (the K5-pmfix-01 signal) | T_P + 2 (close of the bar at T_P + 1) |
| KF3 | am_move | If d is a gold AM auction day: (close of the bar at T_A + 9 - close of the bar at T_A - 31) / tick, the move from 30 minutes before the AM auction to the end of its tenth minute. Otherwise 0. A missing bar or a change of instrument_id means no trade on d | K5-002 P-K5-002-a (pre-auction pressure outside US hours); K5-012 P-K5-012-h ("complete within ten minutes"); K5-001 P-K5-001-a | T_A + 10 = 04:40 or 05:40 CT, before W0 |
| KF4 | event_code | 0 = no event; 1 = d has an Employment Situation or CPI release at 07:30 CT (EC-BLS); 2 = d is an EC-FOMC statement day; 3 = both | K5-014 P-K5-014-a, P-K5-014-c, P-K5-014-d; K5-015 P-K5-015-a; K5-004 P-K5-004-c, P-K5-004-e; K5-019 P-K5-019-c; K5-024 P-K5-024-a | schedules known before d (C9; the schedule as published by the evening before d) |
| KF5 | fomc_move | If d is an EC-FOMC statement day and t_j >= 13:05: (close of the bar at 13:04 - close of the bar at 12:59) / tick. Otherwise 0. On such a d with t_j >= 13:05, a missing bar or a change of instrument_id means no trade at t_j | K5-024 P-K5-024-a, P-K5-024-b (the K5-fomc-01 signal) | 13:05 CT |
| KF6 | gs_ratio_dev | R(tau, d) = ln(close of the gold vehicle's bar at tau - 1 / close of the silver vehicle's bar at tau - 1), both in USD per troy ounce. Value = (R(t_j, d) - m) / s, where m and s (ddof = 1) are the mean and standard deviation of R at the same clock time t_j on the 20 most recent earlier eligible trade dates with both bars present. At least 16 values and s > 0 are required, else no trade at t_j. The 20-date z-score stands in for the source's "unexpected deviations", whose model is not logged: a judgment | K5-031 P-K5-031-a (valuation pressure from unexpected gold-silver ratio deviations predicts variance). R-K5-031's negative mean-reversion finding is why this is a feature and not a member (X-10) | bars closed at or before t_j |
| KF7 | ret60_pct | r60(tau) = (close of the gold vehicle's bar at tau - 1 - open of its bar at tau - 60) / tick. Value = (number of reference values < r60(t_j) + 0.5 x number equal) / number of reference values. The reference set is r60 at the 14 decision clock times on the 20 most recent earlier eligible trade dates, counting each value whose bars exist with one instrument_id. At least 224 values are required, else no trade at t_j | K5-029 P-K5-029-a, P-K5-029-c, P-K5-029-d (decile overreactions at the 1-hour frequency) | bars closed at or before t_j, and earlier trade dates |

- **Decision window [W0, W1] = [07:15, 13:45] CT; horizon h = 30 minutes.**
  - **Decision times:** t_j = 07:15, 07:45, ..., 13:45, which is 14 a day. W1 + h = 14:15 <= F = 15:08.
  - **Fills:** by D15.3's convention a position covers the open of t_j + 1 to the open of t_j + 30. Every
    fill therefore falls at :15, :16, :45 or :46.
  - **Why this window:** it spans every scheduled gold event the log documents inside the US day, each
    strictly inside a position interval and never at a fill:
    - the 07:30 CT Employment Situation and CPI releases, inside [07:16, 07:45];
    - the gold PM auction start, 09:00 CT inside [08:46, 09:15], or 10:00 CT in 5-hour weeks inside
      [09:46, 10:15];
    - the London/New York overlap, 2-4 pm London (Chai et al.: "the information share of London/New York is
      over two and half times of those of the rest of Europe and U.S.", P-K5-016-a);
    - the GC settlement period, 12:29-12:30 CT, inside [12:16, 12:45];
    - the 13:00 CT FOMC statement, inside [12:46, 13:15], with the fomc_move continuation in [13:16, 13:45].
  - **Consequences of the offset:**
    - No opening fill lands in the CPI window [07:25, 07:35]; entries are at 07:16 and 07:46. So D9.12 never
      binds, and MGC's 3-contract CPI cap is never reached.
    - No fill lands in any C11 minute.
  - **Why it starts at 07:15:** the first :15/:45 time before the 07:20 open lets the first position span
    the 07:30 releases. Its entry at 07:16 is four minutes before the day session (C14).
  - **The AM auctions (04:30 or 05:30 CT) are not decision times.** They enter as a feature (KF3); the
    pre-auction trade itself is K5-preauc-01.
  - **Why h = 30:** it is the scale on which the logged gold effects play out:
    - the post-reform auction completes "within ten minutes" (P-K5-012-h);
    - the FOMC adjustment continues past 5 and to 10 minutes (P-K5-024-b);
    - macro effects dissipate "within about 60 minutes" (P-K5-014-d);
    - K5-012's event window runs from 30 minutes before to 60 minutes after the fix start (log product
      line).

    h = 15 would split the release and auction responses into many costly intervals. h = 60 or 120 would
    fold the 07:30 releases, the PM auction and its aftermath, and FOMC with its continuation into single
    intervals. h = 30 keeps each event in its own interval.
- **Expected rows:** 14 x the eligible research-window trade dates. That is about 305 dates, less
  roll-blackout, vendor-degraded and early-halt dates (D15.3), less the 20-date warm-up of KF6, KF7 and B4:
  roughly 3,500-4,000 rows. E.2 gives the exact count.
- **Expected entries:** at most 14 per day (<= 20), each held 30 minutes. Floor ok by construction.
- **Falsification:** the standard condition (UCB95 of mean net daily P&L per contract below eps at >= 80%
  achieved null power on the confirmation window counts against it). Failing the D5 screen puts it in Tier
  B.
- **Topstep check:**
  1. Flat by F: last exit 14:15.
  2. Order type: market (D15.6).
  3. D9.4: at most 14 entries a day, 30-minute holds, no stops or brackets. No fill in a release or
     auction-start minute.
  4. Star rules: MGC at most 10 (C6). No opening fill in the CPI window, so the 3-contract cap never binds.
  5. News: q_c <= 1 lot-equivalent, not the full maximum. A position may span a release.
  6. D9.5a: no fill in any C11 minute.
  7. CPI window: entries at 07:16 and 07:46, outside [07:25, 07:35].
  8. Caps: C6.
  9. Price limit: C13.
  - Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as the design does for every ML
    member.
- **Data needed:**
  - ohlcv-1m of the gold vehicle and the silver vehicle (or SIL, per above). The research window is used for
    training and tuning, the confirmation window for the frozen model.
  - Gold bars around the AM auction (03:59-05:40 CT) for KF3.
  - The member-level coverage check covers 07:16-14:15 (C14).
  - External: EC-LBMA, EC-UKBH, EC-FOMC, EC-BLS, EC-CAL.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K5-fixrev-01 | Fade the last two minutes of the gold fix: "the two minutes leading to the end of the fixing do show statistically significant negative returns ... overshoot" (K5-001 P-K5-001-g) | Rule 3 (timing); D9.3; rule 1 | The auction end is not scheduled: the benchmarks "do not have set publication times" (LBMA page, K5 log 3.0). Timing a rule on it would need each day's result timestamp, which is either read after the fact (look-ahead) or from a source whose licensing and history are unverified. A two-minute effect cannot meet the 10-minute mean hold. The evidence is from the old regime only. |
| X-02 K5-fixsil-01 (and gold AM / platinum variants) | K5-pmfix-01's continuation rule applied to the silver auction (06:00 or 07:00 CT), the gold AM auction or the platinum auctions | Rule 1 (evidence) | Silver shows "a significant decline in cumulative adjusted returns" after the reform (P-K5-012-e), which is evidence against. Caminschi tests the PM gold fixing only (P-K5-001-b, P-K5-001-d). The post-reform gold and platinum results are insignificant (P-K5-012-e). The seed test is written once, as K5-pmfix-01. |
| X-03 K5-relsurp-01 | A post-release trade on GC, SI or HG signed by the consensus surprise of NFP, CPI, GDP, durable goods or industrial production (K5-014 P-K5-014-a, P-K5-014-c; K5-015 P-K5-015-a; K5-018 via P-K5-014-f; K5-004 P-K5-004-b) | Rule 3 (proprietary consensus); contemporaneous; D9.4 and D9.5a | Consensus surveys are proprietary, and no named, obtainable history is in the log. With a price proxy nothing is left to trade: "the majority of the reaction complete within 90-s" (P-K5-004-a); volatility and returns normal "within approximately 2½-min" (P-K5-019-c). A release-minute fill is the gapped-market case the guard exists for. The releases enter only as C11's cost and guard list and as the ML feature event_code. |
| X-04 K5-dispersion-01 | Gold's release response conditioned on analyst belief dispersion (K5-004, title and P-K5-004-a context) | Rule 3 | Analyst-level forecast dispersion is proprietary; no obtainable history is named. |
| X-05 K5-liqwd-01 | Trade the liquidity withdrawal and recovery around monetary-policy announcements: "liquidity is removed from the market around 5-minutes prior to the announcement and reverts to normal within 10-minutes (gold market) and 20-minutes (silver market)" (K5-005 P-K5-005-a) | Brief rule 13 (lead ruling) | The paper conditions on investor sentiment. The lead ruled K5-005 excluded (reports/stage_e0_STATE.md, 3-K5b row). The log notes that the liquidity timing itself does not need sentiment; the ruling stands, and the question is not reopened here. |
| X-06 K5-chpmi-01 | HG or SI traded on the Chinese PMI: "coefficient estimates of 0.18 and 0.06 for copper and silver, respectively" (K3-007 P-K3-007-h [K5]) | Rule 3; rule 1 | It is a surprise response against a proprietary consensus. With a price proxy nothing is left: the K3 log records the impact "appears to be permanent" (first-run passage, not re-checked), and the response lies inside a 20-minute window at US night (P-K3-007-c). The pre-announcement CARs are "available upon request" (P-K3-007-g, [K3] only). |
| X-07 K5-abnret-01 | Gold momentum after an intraday-detected abnormal daily return, and next-day gold contrarian (K5-028 P-K5-028-a, P-K5-028-d, P-K5-028-e, P-K5-028-f) | Rule 1 (parameters; evidence) | The abnormal-return threshold is not in the logged passages; only gold's timing is ("after 5 p.m. ... after 7 p.m.", GMT+3 clock, P-K5-028-d). The data are MetaQuotes broker prices with no named instrument (P-K5-028-b), and there are no costs (P-K5-028-c). The simulated exit at the GMT+3 day end is 16:00 CDT in summer, after F. The gold contrarian leg is "Not rejected", no better than random (P-K5-028-e, P-K5-028-f). The same-day continuation is **covered by CP1** in its unconditional form. |
| X-08 K5-rsi-01 / K5-kc-01 | RSI reversal on 1-minute bars, and a 60-minute Keltner-channel breakout with "1.5 Average True rang Multiplier", on GC, SI, PL, HG (K5-008 P-K5-008-a, P-K5-008-b) | Rule 1 (parameters; evidence quality) | The RSI length and cut levels and the channel's average and ATR lengths are not in the retrieved text. Whether positions are held overnight is [unverified]. Parameters were optimized by PSO over one 21-month window (P-K5-008-c) with no out-of-sample test seen, and the text read was abstract plus snippets. These are D.1 families C and G, which D6 does not port, and no product-specific parameter can be traced. |
| X-09 K5-tokfade-01 | Fade the Tokyo-session move of GC or PL during the New York session, reasoning that "uninformed trading is more prevalent during the Tokyo day session while informed trading dominates the New York day session" (K5-025 P-K5-025-a) | Rule 1 (no directional claim) | The passage is descriptive (abstract only). The reversal is this writer's inference, not a tested claim. It would also bet against CP1's overnight-continuation form without evidence. |
| X-10 K5-gsratio-01 | Gold-silver ratio (spread) mean reversion, intraday | Rule 1 (evidence against); D2 | K5-031 predicts variance, not direction (P-K5-031-a). R-K5-031 (Batten, Ciner, Lucey) is negative: "limited opportunity to profit from strategies based on mean reversion of the spread". R-K5-034 has no intraday horizon. A two-leg member would also need D2's parity sizing across a starred SIL leg capped at 2 contracts. The ratio enters K5-ml-01 as KF6 only. |
| X-11 K5-shfe-01 | GC or SI traded on an SHFE night-session lead (K5-020) | Rule 1 (evidence against); data | The evidence says COMEX leads: SHFE gold's price-discovery share "falls relative to the United States", and spillovers grow "particularly from the United States to China" (P-K5-020-c, P-K5-020-d). No free intraday SHFE history for 2019-2026 is named in the log. |
| X-12 K5-efp-01 | Trade GC on reversion of the futures-minus-spot EFP spread (K5-032 P-K5-032-a, P-K5-032-b) | Tradability; data | It needs the OTC spot leg, which the account cannot trade and the data plan does not hold. Direct arbitrage is rare because "one would have to cross two spreads" (P-K5-032-c). |
| X-13 K5-idxroll-01 | GC or HG around the S&P GSCI roll, 5th-9th business day (K4-034 P-K4-034-b, P-K4-034-c [K5]; K4-035 P-K4-035-b, P-K4-035-c [K5]) | Flat by F; rule 1 | As documented, the effect is a multi-day nearby-minus-deferred differential or a 1-3-week calendar spread, which breaks the 15:08 flat rule and is not an exposure's D2 vehicle. The pooled effect "is of 17 basis points at most" and "never significant" after standard-error adjustment (P-K4-034-a). K4-036 has no metals. A single-leg intraday version has no passage. |
| X-14 K5-ip-01 | HG traded on the 09:15 ET industrial production release (P-K5-014-c) | Rule 3; contemporaneous | This is the copper case of X-03. The release enters only C11's copper cost and guard list. |
| X-15 K5-open-01 | Trade the day-session open (07:20 CT) jump in volume and volatility (P-K5-004-f; P-K5-019-c "A spike in market activity of a lower magnitude is also registered as the trading pit opens") | Rule 1; D6 | The claim is descriptive and dates from the pit era. It is a family A session-clock effect, which D6 does not port. After COMEX's move to Globex "the price discovery shares remain relatively stable throughout the day" (P-K5-011-d). |
| X-16 K5-fixvol-01 | A daily-bar volatility regime member built on the 2014-2015 fix change (K5-006) | Not intraday-feasible; rule 1 | Crain et al. is a daily structural-break study (P-K5-006-b). Its raw and trend-controlled results point opposite ways (P-K5-006-c against P-K5-006-f and P-K5-006-g), and both are stated in K5-pmfix-01. |
| X-17 K5-fomc-ext-01 | K5-fomc-01 extended to silver, copper or platinum | Rule 1 (no evidence) | K5-024 tests gold only. Following the lead's 21:52 ruling Q6 (no extension without logged evidence), not written. It would cost up to 3 trials. |

---

## 3. Beyond budget (lead decides)

None. The log supports 4 new members inside the budget of 11. These candidates were considered and not
written; none is a budget overflow:
- **A post-auction recovery leg for K5-preauc-01** (long from T to T + 30). P-K5-012-g's "steady recovery"
  of depth suggests it, but no passage claims a price reversal after the start. Not written.
- **A size-thresholded K5-pmfix-01** (trade only when |s| is large). This would follow P-K5-001-c's 80-95%
  for larger moves, but no threshold value is logged. The split is reported descriptively instead.
- **The X-02 and X-17 extensions**, which have no evidence (section 2).

---

## 4. Routed to K8

| Source | Legs | One phrase |
|---|---|---|
| Multiple sources (not pinned), K5 log section 4 | gold (K5); dollar and real rates (K3, K2) | the dollar-and-gold relationship (partition section 3) |
| Wright Blogs, "Metals as Macro Signals ..." (not read) | metals (K5); macro and cross-asset (K1, K2, K3) | metals as a cross-asset signal |
| Baur and Kuck (2019), FRL, "The timing of the flight to gold ..." (SSRN 3243111) | gold (K5); S&P 500 (K1) | intraday flight-to-safety timing |
| "Effects of idiosyncratic jumps and co-jumps on oil, gold, and copper markets" (Energy Economics 2021, 10.1016/j.eneco.2021.105660) | oil (K4); gold and copper (K5) | one-minute co-jumps across commodities |
| arXiv 2409.08355, copper and S&P 500 dynamic correlations | copper (K5); S&P 500 (K1) | low-frequency equities-against-copper |
| Quantpedia, "Cross-asset price-based regimes for gold" (not read) | gold (K5); other clusters | cross-asset regime signal |
| JFM 2025, "Gold Jump Risk, Rare Macroeconomic Disaster Probability, and Expected Stock Returns" (10.1002/fut.70074) | gold (K5); equities (K1) | gold jumps predicting stock returns |
| K5-024's FOMC rate surprise, if measured from fed funds futures (this catalog) | rates surprise (K2); gold (K5) | a surprise-signed gold FOMC trade needs a rates instrument; K5-fomc-01 uses gold's own response instead |

The first seven rows are the reader's own flags (K5 log section 4). The last row is this catalog's
routing. Other clusters' logs also flag gold or copper legs (K1 log line 527; K7 log lines 747-757); those
are theirs to route.

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K5.md section 3, and every `[K5]`-tagged
passage or registry tag elsewhere.

| Item | Disposition |
|---|---|
| 3.0 timing facts (LBMA and IBA times, LME and SHFE hours, CME settlement windows, Globex hours) | Used: C3, C5, C9, C10; K5-preauc-01, K5-pmfix-01, K5-ml-01. SHFE and LME hours are background only (X-11; no copper Asian-session source passed) |
| K5-001 Caminschi, Heaney | Used: K5-pmfix-01 (P-a, b, c, f, g); K5-ml-01 KF1, KF2, KF3. The end-of-fix reversal is excluded, X-01 |
| K5-002 Nilsson | Used: K5-preauc-01 (P-a); K5-ml-01 KF3 |
| K5-003 | Duplicate of K5-006 (log) |
| K5-004 Smales, Yang | Used as counter-evidence in K5-fomc-01 (P-a) and in K5-ml-01 KF4 (P-c, P-e). The surprise-signed trade is excluded, X-03; the dispersion member is excluded, X-04. The pit-open fact (P-f) is excluded, X-15 |
| K5-005 Smales, Lucey | Excluded, X-05 (lead ruling, sentiment) |
| K5-006 Crain, Hoelscher, Jones | Both sides stated in K5-pmfix-01 (P-c against P-f and P-g); K5-ml-01 KF1. As a member it is not intraday-feasible, X-16 |
| K5-007 Batten et al. (stylized facts) | Insufficient evidence for a member: descriptive periodicity (P-a) of spot metals, family A, which D6 does not port. Not used |
| K5-008 Cohen | Excluded, X-08 |
| K5-009 Wang, Lu | Insufficient evidence: a volatility-forecasting comparison with no trading claim (P-a). Not used; B4 carries volatility state in the ML member |
| K5-010 LBMA silver FAQ | Used for auction mechanics and timing (C9, C10; K5-preauc-01's silver leg) |
| K5-011 Hauptfleisch, Putnins, Lucey | Used: K5-pmfix-01 context and K5-ml-01 KF1 (P-f, noise around the fix). P-d is used in X-15. Otherwise descriptive price-discovery shares: insufficient evidence for a member |
| K5-012 Aspris, Foley, Gratton, O'Neill | Used: K5-pmfix-01 (P-a, d, e, h, i); K5-preauc-01 (P-f, P-g, and the log's window line); K5-ml-01 KF1, KF2, KF3 and the h choice. Silver and other auction variants are excluded, X-02 |
| K5-013 Aspris, Foley, O'Neill | Used as counter-evidence in K5-pmfix-01 (P-a) |
| K5-014 Elder, Miao, Ramchander | Used: C11 (P-a, P-c); K5-fomc-01 counter-evidence (P-d); K5-ml-01 KF4 and the h choice. Surprise members are excluded, X-03 and X-14 |
| K5-015 Cai, Cheung, Wong | Used: C11 (CPI, P-a); K5-ml-01 KF4. The surprise member is excluded, X-03 |
| K5-016 Chai, Lee, Wang | Used only for K5-ml-01's window placement (P-a). Descriptive shares: insufficient evidence for a member (family A) |
| K5-017 Sobti, Sehgal, Ilango | Insufficient evidence: descriptive price discovery (P-a), abstract only. Not used |
| K5-018 Christie-David, Chaudhry, Koch | Insufficient evidence: retrieval failed, secondary description only (P-K5-014-f). Its topic is covered by X-03 |
| K5-019 Smales | Used as counter-evidence in K5-fomc-01 (P-c); K5-ml-01 KF4; K5-preauc-01 (P-b, the floor-open clock). The pit-open fact is excluded, X-15 |
| K5-020 Jiang, Kellard, Liu | Excluded, X-11. P-a is used in K5-preauc-01 (the COMEX floor-open clock) |
| K5-021 Sehgal, Sobti, Diesting | Insufficient evidence: descriptive (P-a), abstract only. Not used |
| K5-022 Lauterbach, Monroe | Insufficient evidence: retrieval failed, title only |
| K5-023 Martell, Trevino | Insufficient evidence: retrieval failed, title only (K6's duplicate claim K6-005 points here) |
| K5-024 Awartani, Hussain, Virk | Used: K5-fomc-01 (P-a, b, c); K5-ml-01 KF4, KF5 and the h choice. The rates-surprise variant is routed to K8 (section 4); extensions are excluded, X-17 |
| K5-025 Iwatsubo, Watkins, Xu | Excluded, X-09 |
| K5-026 Batten, Lucey, Peat | Insufficient evidence: retrieval failed, title only |
| K5-027 Sobti | Insufficient evidence: retrieval failed, title only |
| K5-028 Caporale, Plastun ([K5] passages) | Same-day continuation **covered by CP1**; the threshold member and the next-day contrarian are excluded, X-07. The [K4] passages are K4's |
| K5-029 Borgards, Czudaj, Hoang ([K5] passages) | Used: K5-ovr-01 (P-a, b, c, d); K5-ml-01 KF7. The [K4] and [K6] passages are those writers' |
| K5-030 Gu, Kurov, Stan | Not used (never read; brief rule 13). Noted in K5-fomc-01 as unread |
| K5-031 Lyocsa, Todorova, Zhu | Excluded as a member, X-10. Used in K5-ml-01 KF6 (P-a) |
| K5-032 Barzykin, Bergault, Gueant | Excluded, X-12 |
| K3-007 [K5] Baum, Kurov, Wolfe, P-K3-007-h | Excluded, X-06 |
| K3-040 (registry tag K5; title only) Kosowski et al., "Overnight-Intraday Reversal Everywhere" | Insufficient evidence: content [unverified]. Note that CP1's (a) form bets the opposite way, overnight continuation |
| K4-034 [K5] Dubois, Maréchal | Excluded, X-13 (P-a null; P-b roll days; P-c constituents) |
| K4-035 [K5] Mou | Excluded, X-13 (multi-day spread, P-b; metals sector figures not extracted, P-c) |
| K4-036 (registry tag K5) Stoll, Whaley | No [K5] passage: "[K5] none (no metals in the roll tests)" (K4 log). Not used |
| K4-039 (registry tag K5) Brunetti, Reiffen | Rejected by K4 (R-K4-040), no [K5] passage. Not used |
| `[K5]` search in the K1, K2, K6, K7 logs and the K3 and K4 partial logs | No further [K5]-tagged passage. The K3 sonnet partial log's K3-007 tags are superseded by the K3 log. The K1 and K7 mentions are those readers' own K8 flags or rejections |
| R-K5-001 to R-K5-053 | Rejected at pre-filter or on reading. Not used. R-K5-018 (Rosa) is family CP1; R-K5-031 and R-K5-034 inform X-10; R-K5-046 (Kinlay GDX, "has recently begun to fail") is an ETF, not a K5 product |

---

## 6. Trial count table

| Member | Exposures (max) | Grid points | Trials in N (all four admitted) |
|---|---|---|---|
| K5-cp1-01 | gold, silver, copper, platinum | 1 | 4 |
| K5-cp2-01 | gold, silver, copper, platinum | 1 | 4 |
| K5-cp3-01 | gold, silver, copper, platinum | 1 | 4 |
| K5-preauc-01 | gold (AM), silver (platinum removed by the lead) | 1 | 2 |
| K5-pmfix-01 | gold | 1 | 1 |
| K5-fomc-01 | gold | 1 | 1 |
| K5-ovr-01 | gold, silver, platinum, copper | 1 | 4 |
| K5-ml-01 | gold (fallback silver, then copper: lead ruling) | 48 in research-window accounting only (D15.8) | 1 |
| **Cluster total** | | | **22** = 12 port + 9 new + 1 ML. In general 4E + 3a_G + a_S + a_P + 1. Without platinum: 17. Gold only: 8 |

The "without platinum" figure: 3 x 3 ports + 3 ovr + 2 preauc + 1 pmfix + 1 fomc + 1 ML = 17.

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **Do LBMA auction starts count as "scheduled major releases"?**
   - C11 names each exposure's own auction starts for D8's event-window cost. That is conservative, and it
     raises the cost of K5-pmfix-01's two fills and of any port or K5-ovr-01 fill within 30 minutes after
     an auction start.
   - Whether auction starts also count for the D9.5a fill guard is the lead's call.
   - Every new member and the ML member are timed so that their fills never land in [T, T + 2), so the
     answer changes only the ports' fills (CP2 entries at 09:00-09:01 or 10:00-10:01 on gold, 08:00 or
     09:00 on platinum).
2. **C11's named releases.** Named: Employment Situation, CPI, FOMC, and G.17 for copper. Durable goods
   (08:30 ET) is also among Elder's largest-impact releases for gold and silver (P-K5-014-a), but its
   schedule source was not confirmed (census.gov 404). Should E.2 source it and add it?
3. **K5-preauc-01 rests on one abstract** (a practitioner SSRN paper, window and magnitude unverified).
   - It costs 3 trials.
   - Platinum's window (03:15-03:44 CT, or 04:15-04:44 in 5-hour weeks) is the likeliest to fail the
     member-level coverage check (C14).
   - The lead may cut it, or keep gold and silver only.
4. **Low-frequency member.** K5-fomc-01 has 10 research and about 37-38 confirmation events. By arithmetic
   it needs about 30 x eps_X per event, so it is likely "inconclusive by design" (D4). It is kept under the
   21:52 Q4 ruling; the power check decides.
5. **K5-ovr-01 on copper.** The source reports fewer overreactions in industrial metals, with a "lower but
   still positive" return (P-K5-029-a, P-K5-029-c). Copper is included as a tested sample member (1
   trial).
   - The trailing-reference length (20 dates) and the 59-minute hold match K4-ovr-01's judgments for the
     same panel source.
   - If K6 writes the same source, the lead may want one rule text for all three clusters.
6. **K5-pmfix-01's post-reform evidence leans against it** (P-K5-012-a, P-K5-012-i; P-K5-013-a). It is kept
   as the partition's seed test (1 trial), with both sides stated, including Crain's daily results (P-K5-006-c
   against P-K5-006-f and P-K5-006-g).
7. **K5-ml-01 has no fallback exposure.** Its features are gold-specific. It also needs silver bars (KF6)
   even if silver is not admitted, which E.2 must add to D13's purchase.
8. **Platinum.**
   - PL has no micro and "Platinum (PL) = 0" is possible at Topstep's discretion (D9.11). Every platinum
     trial carries the "may be suspended" flag.
   - Platinum carries 3 ports + K5-preauc-01 + K5-ovr-01 = 5 trials.
   - Whether an exposure that can be switched off mid-program should carry trials at all is a user or lead
     decision (the "without platinum" total is 17).
9. **E.2 checks named in this catalog:**
   - (a) the platinum auction times for 2019-2021, when the LME administered the price, and any
     advance-announced UK half-days or special auction schedules (C9);
   - (b) the SI (12:25) and PL (12:05) settlement times behind D6's C (C5);
   - (c) the metals futures Globex hours (C3);
   - (d) the tick-size history 2019-2026 (C7);
   - (e) COMEX and NYMEX metals price limits or dynamic circuit breakers against Topstep's 2% rule (C13);
   - (f) member-level coverage for 03:15-06:59 CT (K5-preauc-01) and 07:16-07:20 (K5-ml-01) (C14);
   - (g) D8 slippage buckets for 03:00-07:00 CT (K5-preauc-01);
   - (h) MHG's short history and the HG price-path declaration (C8);
   - (i) EC-BLS from yearly Wayback captures, EC-FOMC statement times, EC-G17 dates (C9).
10. **Region gaps.** The partition asked K5 to read the COMEX settlement window, options expiry, the roll
    and delivery period, and copper's Asian session. The log found no passing source on any of them, so
    there is no member. No log item gives a copper-specific intraday mechanism other than K5-029's
    reversal and Elder's contemporaneous 09:15 response.
11. **Registry hygiene** (already noted by the reader, not rewritten): K5-004's DOI should be
    10.1016/j.irfa.2015.01.017; K5-005's should be 10.1016/j.intfin.2018.12.003; K5-003 duplicates K5-006.
    The registry also tags K4-036 and K4-039 with K5, but neither has a [K5] passage.
