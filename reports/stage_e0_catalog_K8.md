# Stage E.0 hypothesis catalog, cluster K8 (cross-cluster relationships)

Writer: CatalogWriter-K8-OpusXHigh (Stage E.0 Task 4), 2026-09-24, about 02:00-02:45 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** No price, bar, tick or order-book data of any product was
opened, downloaded, charted or summarized, including the MES bars on disk. The only product-specific
numbers used are:
- contract specifications and public ADV (reports/stage_e0_liquidity.json; design D1 table);
- Topstep's published fees, hours, release table and risk rules (reports/stage_e0_topstep_facts.md
  F3, F4, F6, F12, as quoted in design D9);
- calendar metadata (dates and clock times only: the EIA WPSR schedule, FOMC, BLS, CME holidays), as
  the K3, K4, K5 and K7 catalogs specified and sourced them;
- MES's own confirmation start S = 2020-02-03 (Stage D.1f run: progress.md 2026-09-23 entry;
  docs/STAGES.md).

No price level, range, trend or volatility of any product is used or assumed below. Every threshold
is either a passage value or a judgment stated with its reason, and every rolling statistic is
computed by the harness from earlier bars at run time.

**Inputs read in full:**
- reports/stage_e0_research_K8.md (sections 0-5, with the routed-flag table F01-F47).
- `[K8]`-tagged passages in the other logs: **none exist.** `grep -n '\[K8\]'` over
  reports/stage_e0_research_K1.md to K7.md returns nothing. The "Flags for K8" sections were read:
  K1 lines 524-528, K2 434-439, K3 631-637, K4 691-704, K5 561-573, K6 692-702, K7 744-757. All of
  them are in the K8 log's F table.
- reports/stage_e0_source_registry.jsonl: K8-001 to K8-008 (lines 271-278). No other line is
  tagged K8.
- docs/STAGE_E_DESIGN.md D1-D15, with the 21:12 and 21:52 amendments and the D9 rulings of 01:40 and
  01:52.
- docs/NULL_CRITERIA_E.md, including section 3 (the "source-overlap" label) and section 8
  (cross-cluster members).
- reports/stage_e0_partition.md.
- reports/stage_e0_topstep_facts.md: F3 fees, F4 hours, F6 releases.
- reports/stage_e0_liquidity.json: the NQ, MNQ, MBT, CL, MCL, 6C, GC and MGC rows.
- reports/stage_e0_catalog_K2.md to K7.md, for duplicates and format and for their "Routed to K8"
  sections. The K1 catalog did not exist when this was written.
- data/research_bars.py and data/build_mes_bars.py: docstrings and constants only, to confirm
  that the owned MES build spans the Globex session (daily halt 16:00-17:00 CT) and which date
  classes its loaders serve. No bar was loaded.

**Checks in the K8 reader's saved copies.** Two checks were made in
scratchpad/fetch/alquist.txt and scratchpad/fetch/zdg.txt. They only read the definitions of numbers
already logged; no mechanism was taken from them.
- **Alquist, Ellwanger, Jin, eq. (4) and Tables 4-5.** The "marginal effects" are coefficients of
  an asset's event-window return on the oil-futures return.
  - P-K8-001-f's CAD value of 0.090 is therefore a return-on-return coefficient.
  - The same table family's equity figure, 0.110 after 2008M9, is the logged "1.1% increase" per
    10% oil (P-K8-001-c).
  - A positive exchange-rate effect is a dollar depreciation (P-K8-001-e). That is a rise in the
    USD price of the foreign currency, the direction in which 6C rises.
- **Zhang, Dufour, Galbraith, Table 1 note** (the same note as P-K8-006-e): "The daily CAD/USD,
  CAD/GBP and CERI are from Statistics Canada. The WTI crude oil price and Brent crude oil price are
  from Energy Information Administration." It is used in X-05.
- The scratchpad files named baur.pdf and baur2.pdf are "Content Blocked" HTML pages, not the paper.
  K8-003 stays abstract-only.

**Official pages fetched in this task:** none. The calendar and session facts are the ones other
CatalogWriters fetched and quoted:
- EC-WPSR: K4 catalog C9;
- EC-FOMC and EC-BLS: K5 catalog C9;
- CME's 24/7 crypto trading from 2026-05-29: K7 catalog preamble and C3.

---

## 0. Header

| Item | Value |
|---|---|
| Cluster | K8, cross-cluster relationships. Each member has a signal leg in one of K1-K7 and a traded leg in another (partition section 3) |
| Members | **4 = 3 new + 1 ML member. No core ports in K8** (K8 has no products of its own; the ports live in K1-K7). The budget is 15, so 11 slots are unused. The log is thin: 7 items passed, of which 3 are abstract-only and 2 carry no direction. Nothing is padded (section 3) |
| Trials in N (confirmation) | **5 if D2 admits gold, CAD and the Nasdaq-100.** K8-flight-01 2 (exit grid), K8-oilcad-01 1, K8-wkndbtc-01 1, K8-ml-01 1. In general 2a_G + 2a_C + a_N, where each a is 1 if D2 admits that exposure |
| ML grid | 48 configurations, counted only in the K8 screening session's research-window accounting (D15.8) |
| Traded legs used | gold {GC, MGC\*} (K5); CAD {6C} (K3); Nasdaq-100 {MNQ\*, NQ} (K1). Each is traded only if D2 admits the exposure. The vehicle is "D2 (chosen in E.2)" throughout |
| Signal legs used | S&P 500 on MES bars (K1; a leg only, D1.5; owned, non-holdout dates). WTI crude on the crude exposure's price-path series (K4). Bitcoin on MBT bars (K7). No member reads NKD, 6M or MET |
| Statement unit | NULL_CRITERIA_E section 8. Each member is stated under K8 only. Its eps is the traded leg's exposure's eps_X, and it enters K8's own Holm family (D5). Its window is the intersection of its legs' windows (D4) |
| Source overlap | **K8-wkndbtc-01 is labelled "source-overlap"**; no other member is (C15) |
| Starred contracts | MGC\* and MNQ\* can be vehicles (D9.8; referent F12.1, encoded as D9.11 and D9.12). GC, 6C and NQ are unstarred |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose ts_event
  (open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values are usable
  from then on. C_X(tau) is the close of leg X's bar at tau.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open, the engine convention
  of D6 and D15. "Market intent on the bar at X" fills at the open of the bar at X + 1 min. The ML
  member follows D15.3 (decision at t_j, fill at the open of the bar at t_j + 1 min).
- **C3 Trade date and hours.**
  - **Trade date:** d = [d-1 17:00 CT, d 16:00 CT) (reports/stage_e0_STATE.md). The first bar of a
    Monday trade date is the Sunday 17:00 CT bar.
  - **Topstep hours** (F4): "Sunday open | 5:00 PM CT", "Weekday reopen | 5:00 PM CT", "All
    positions must be closed by 3:10 PM CT every weekday".
  - **MBT, two regimes.** Before 2026-05-29, CME's crypto session had a daily 16:00-17:00 CT break
    and a weekend closure from Friday 16:00 to Sunday 17:00 CT. From 2026-05-29 16:00 CT it trades
    continuously (K7 catalog preamble and C3, quoting CME's releases of 19 Feb and 1 June 2026).
  - **Program convention kept.** Following the K7 catalog's C3, no K8 rule reads a bar outside a
    program trade date.
- **C4 Cross-leg synchronization (rule 3; D11.5).** Every leg is a set of CME Globex ohlcv-1m bars on
  one UTC minute grid.
  - At decision time t, a signal reads only bars of its own leg whose close is at or before t, that
    is the bar at t - 1 and earlier.
  - The traded leg's intent is emitted on the traded leg's own bar at t - 1 and fills at the open of
    its bar at t (C2). No signal value comes from a bar that closes after the fill.
  - No forward fill. A missing signal bar, or a change of instrument_id between the bars of one
    computation, means no trade at t.
  - Signals are percent returns or signs, so they give the same decision on any contract of the
    signal leg's exposure.
- **C5 Exclusions for the three new members.**
  - A member does not trade on:
    - the traded leg's roll-blackout dates (`screen_candidate` with `roll_blackout`: the splice trade
      date plus the 2 sessions before it);
    - dates that any leg's D10 group calendar (equity-and-crypto, energy, FX, metals) marks as early
      close, early halt or closure;
    - dates on which a bar the rule reads, or the entry bar, is missing.
  - If an exit's named bar is missing, the exit is sent on the first later bar. The engine's forced
    flatten at F is the backstop.
  - **Signal-leg rolls.** Signal-leg roll-blackout dates are not excluded. A signal leg's bars come
    from its exposure's volume-ranked continuous series, and every computation requires one
    instrument_id (C4; question 3).
  - **Warm-up.** A rolling multi-day statistic uses only earlier trade dates of the same window
    (research or confirmation) that pass these exclusions. The first 20 such dates of each window are
    warm-up and carry no trade.
  - Nothing is ever read from embargo, holdout-2 or holdout-1 dates.
- **C6 Guarded entries.** An entry whose fill would land in a D9.5a guarded interval [release,
  release + 2 min) of the traded product is **skipped, not deferred.** Every K8 entry signal is
  measured on bars before its decision time, so a fill deferred past a release would act on a signal
  the release has just made stale. This is stricter than D9.5a's default deferral (question 6).
  Exits deferred by D9.5a are left to the harness; they only lengthen a hold.

  The releases that concern each traded product (D8: Topstep F6.4 plus the releases the product's
  catalog members name) are:

  | Traded exposure | Releases (CT) | Basis |
  |---|---|---|
  | gold | Employment Situation 07:30; CPI 07:30; FOMC statement 13:00 (LBMA auction starts: D8 cost only, pending the lead) | K5 catalog C11 |
  | CAD (6C) | Employment Situation 07:30; FOMC statement 13:00; EIA WPSR at T_W(d) | F6.4 ("Unemployment Rate / 7:30 AM" lists 6C; "FOMC Statement / 1:00 PM / All products"). WPSR is named by K8-ml-01 (KF3, KF4) and is the signal leg's release in K8-oilcad-01 (question 5) |
  | Nasdaq-100 | Employment Situation 07:30; CPI 07:30; FOMC statement 13:00 | F6.4; D9.12 |

- **C7 Size.** Each member trades q_c of its traded leg's D2 vehicle, never above 1 lot-equivalent
  (D2, D9.5). A signal leg takes no position and has lot-equivalent 0. Each member's total position
  is therefore its traded leg's, and no two-leg position exists in this catalog (rule 5). No member
  sizes by signal.
- **C8 Ticks and fees.** Ticks are from reports/stage_e0_liquidity.json (CME contract specifications,
  fetched 2026-09-23 20:41-20:51 PDT). Round turns are Topstep F3.

  | Contract | Role | Exposure (cluster) | Tick | Tick value | Topstep round turn | Round turn in ticks | Lot-equivalent |
  |---|---|---|---|---|---|---|---|
  | GC | traded | gold (K5) | 0.10 | $10.00 | $4.32 | 0.43 | 1 |
  | MGC\* | traded | gold (K5) | 0.10 | $1.00 | $1.92 | 1.92 | 0.1 |
  | 6C | traded | CAD (K3) | 0.00005 | $5.00 | $4.22 | 0.84 | 1 |
  | NQ | traded | Nasdaq-100 (K1) | 0.25 | $5.00 | $3.78 | 0.76 | 1 |
  | MNQ\* | traded | Nasdaq-100 (K1) | 0.25 | $0.50 | $1.22 | 2.44 | 0.1 |
  | MES | signal only | S&P 500 (K1) | 0.25 | $1.25 | n/a | n/a | 0 (no position) |
  | CL, QM, MCL | signal only | crude (K4) | 0.01, 0.025, 0.01 | n/a | n/a | n/a | 0 (no position) |
  | MBT | signal only | bitcoin (K7) | $5.00 per bitcoin | $0.50 | n/a | n/a | 0 (no position) |

  Within the gold and Nasdaq-100 exposures, both contracts have the same tick in price units. No K8
  rule is in ticks; the ML member's B-features are in ticks of 6C, the only CAD contract. E.2
  confirms that the ticks were unchanged over 2019-05..2026-06.
- **C9 Price data.**
  - **MES (signal leg, owned).**
    - The research parquet is `ohlcv-1m_MES_v_0_2025-04-01_2026-06-19_research.parquet`. The
      confirmation bars cover 2019-05-01..2024-02-29.
    - Both are served by data/research_bars.py, whose loaders refuse holdout, embargo and
      wrong-class dates.
    - The build spans the Globex session with the daily 16:00-17:00 CT halt.
    - MES's own start rule gave S = 2020-02-03 (D.1f), so every MES leg's confirmation window starts
      no earlier than 2020-02-03.
    - Holdout-2 (2024-03..2025-03) and holdout-1 (from 2026-06-22) stay sealed. No K8 member reads
      them.
  - **Traded vehicles, crude and MBT.** Databento GLBX.MDP3 ohlcv-1m, paid. The research window is
    bought in E.1; the confirmation and holdout-2 history of the chosen vehicle is bought in E.2b
    (D13).
  - **History** (liquidity JSON listing dates; D13's pre-listing quote failures):
    - GC, NQ, 6C, CL and QM: 2019-05 onward;
    - MGC: listed 2010-10-04;
    - MNQ: listed 2019-05-06;
    - MCL: listed 2021-07-12;
    - **MBT: listed 2021-05-03, so it has no bars for 2019-05..2021-04.**
  - **The crude signal series.** D13 buys one chosen vehicle per exposure. The crude leg reads the
    crude exposure's price-path bars as E.2 declares them under D2 and D4: CL's bars if CL is the
    vehicle or is declared MCL's price path, otherwise the vehicle's own bars. The rules use percent
    returns, so they are the same on any crude contract.
  - **Availability.** Every bar is available at its close (C1).
  - **mbp-1** enters only through D8's shared five-date cost sample. No member reads order-book data.
- **C10 Event calendars.** All are external, free, and known before the trade date. No rule reads a
  released value.
  - **EC-WPSR (EIA Weekly Petroleum Status Report)**, exactly as the K4 catalog's C9 specifies it:
    - standard slot "10:30 a.m. eastern time on Wednesdays", which is 09:30 CT;
    - exceptions from EIA's yearly tables, for example Thursday 11:00 ET in 2019, Thursday 12:00 ET
      in 2025-2026, and 2025-12-29 Monday 5:00 p.m. ET;
    - sources: the EIA schedule page and one Wayback capture per year, 2019-2026;
    - T_W(d) is the scheduled release time in CT on d, from the schedule known the evening before d.
      The D8 cost and the D9.5a guard use the actual time.
  - **EC-FOMC and EC-BLS**, exactly as the K5 catalog's C9: FOMC statement at 13:00 CT; Employment
    Situation and CPI at 07:30 CT.
  - **EC-CAL**: the D10 group calendars (equity-and-crypto, energy, FX, metals), which E.2 builds from
    CME's published schedules.
- **C11 Frequency (arithmetic from calendar counts; no price data).**
  - **Research window** 2025-04-01..2026-06-19:
    - 319 weekdays, about 305 CME trade dates (K4 catalog C11);
    - 63 Mondays, 5 of them US holiday Mondays with an equity early halt (2025-05-26, 2025-09-01,
      2026-01-19, 2026-02-16, 2026-05-25);
    - about 56 standard WPSR Wednesdays (K4 C11);
    - 10 FOMC statement days (K5 C12);
    - 20 warm-up dates per rolling member (C5).
  - **Confirmation window by earliest leg start:**
    - from 2019-05-06: 1,259 weekdays to 2024-02-29;
    - from 2020-02-03 (MES): 1,064 weekdays;
    - from 2021-05-03 (MBT): 739 weekdays, 148 Mondays.
    - All are before exclusions and before each leg's own start rule.
  - **Consequence (D5):** a member trading on k of about 305 research dates, with zeros on the rest,
    needs a net P&L per event of about (305 / k) x eps_X.
- **C12 Price-limit proximity (D9.7), per traded leg.**
  - **Nasdaq-100:** CME equity-index limits (7% overnight, per the Topstep page quoted in D9.7). They
    bite on K8-wkndbtc-01's Sunday-evening entries.
  - **Gold:** as the K5 catalog's C13. Whether a daily limit or a dynamic band applied is not
    verified in E.0; E.2 decides.
  - **6C:** as the K3 catalog's C11. No FX limit is established in E.0; E.2 decides.
  - The harness rule applies wherever a limit exists: no entry, and an immediate exit, beyond the stop
    level.
- **C13 Coverage.**

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  - **Traded vehicle:** D9's member-level check (ohlcv-1m coverage of at least 0.95 in the member's
    own window, on the research window), with each member's window listed in its entry.
  - **Signal leg (K8 addition, proposed; question 4):** E.2 reports, on the research window, the share
    of the member's decision times at which every signal bar it needs is present. A member below
    0.95 is excluded before screening, with the reason logged. This matters most for K8-wkndbtc-01's
    two MBT minutes and for the crude bars before 08:00 CT that K8-ml-01 reads.
- **C14 Cost and statistics.**
  - **Cost:** each member pays its traded leg's D8 cost: Topstep's round turn plus the calibrated
    half-spread per 30-minute bucket, at q_c. A fill in [release, release + 30 min) after a C6
    release pays the event-window cost. Signal legs cost nothing.
  - **Daily series:** net P&L per contract of the traded vehicle, zeros on no-trade dates
    (NULL_CRITERIA_E section 3).
  - **eps:** the traded exposure's eps_X (section 8).
- **C15 Source overlap (NULL_CRITERIA_E section 3).** Each entry records its sources' sample windows
  against its confirmation window. That window ends on 2024-02-29 and starts no earlier than
  2019-05-06.

---

## 1. Members

### K8-flight-01 (flight to gold: long gold after an extreme negative 5-minute S&P 500 move)
- **Cluster** K8.
  - **Signal leg:** the S&P 500 exposure (K1), read on MES bars (C9; a leg only, D1.5).
  - **Traded leg:** gold (K5). Admissible contracts: GC and MGC\* (D1 table).
  - **Vehicle:** D2 (chosen in E.2). Traded only if D2 admits gold.
- **Mechanism:** after an extreme negative 5-minute S&P 500 move, gold rises. The passages:
  "extreme negative 5-min S&P500 returns lead to a positive reaction of the gold price" and "on days
  with extreme price declines in the stock market, gold continues to increase post US stock trading
  hours" (P-K8-003-b); "a fast reaction of gold prices to extreme negative stock returns consistent
  with a flight to gold" (P-K8-003-c). New to the program.
  - **Evidence status:** abstract only (K8-003). The following are [unverified]: the definition of
    "extreme", the lag, the response size, whether the gold series is spot or COMEX futures, and
    costs.
  - **Limits:**
    - A "fast" reaction may sit largely inside the same 5-minute interval as the equity move, which a
      next-open fill cannot capture. The member tests the part that follows the interval.
    - The post-close continuation lies after F (X-09). Only its in-session lead-in is tested (grid
      point HEOD).
- **Signal (on MES, K1 clock):**
  - **Blocks:** B_k = [08:30 + 5(k-1), 08:30 + 5k) CT for k = 1..77; the last is [14:50, 14:55).
    The decision time is t_k = 08:30 + 5k, from 08:35 to 14:55.
  - **Block return:** r_k = (C_MES(t_k - 1) - C_MES(t_k - 6)) / C_MES(t_k - 6), the move from the
    price at the block's start to the price at its end. Both bars must be present with one
    instrument_id; otherwise r_k is undefined and there is no trigger at t_k.
  - **Threshold Q(d):**
    - Collect every defined r_k (k = 1..77) on the 20 most recent earlier eligible dates of the same
      window (C5). Let n be their count.
    - n >= 1,200 is required (the maximum is 1,540); otherwise there is no trade on d.
    - Q(d) = the m-th smallest value, m = ceil(0.005 n); m = 8 when n = 1,540.
    - Q(d) is fixed before d's 08:30.
  - **Trigger at t_k:** r_k <= Q(d) and r_k < 0.
- **Entry rule:** at the first trigger of trade date d, BUY q_c: market intent on the gold vehicle's
  bar at t_k - 1, filling at the open of its bar at t_k. At most one entry per trade date. C6
  applies: on FOMC days a trigger at 13:00 (fill at 13:00) is skipped, and the member keeps watching
  later blocks.
- **Exit rule (grid, two points):**
  - **H30:** market intent on the gold bar at T_e + 29, where T_e is the entry fill minute, filling
    at the open of T_e + 30; or the HEOD exit, if that comes first.
  - **HEOD:** market intent on the gold bar at 15:04, filling at the 15:05 open.
- **Holding horizon:**
  - H30: 30 minutes for entries at or before 14:35, falling to 10 minutes for an entry at 14:55.
  - HEOD: from 10 minutes (entry at 14:55) to 6 h 30 min (entry at 08:35).
  - **Session window:** 08:35-15:05 CT. **Flat by F:** gold's F is 15:08 (D6 metals row); the last
    fill is at 15:05.
- **Data fields read:**
  - **MES ohlcv-1m close and instrument_id**, bars 08:29..14:54 CT. Owned (C9): on disk for
    2019-05-01..2024-02-29 and 2025-04-01..2026-06-19. Used from 2020-02-03 (MES's S). Available at
    each bar's close.
  - **Gold vehicle ohlcv-1m open and instrument_id**, 08:35..15:05 CT. Databento GLBX.MDP3, paid;
    history 2019-05..2026-06 (C9). Available at each bar's close.
  - **EC-CAL** (equity-and-crypto and metals groups), and **EC-FOMC and EC-BLS** (for C6 only).
    Free, known in advance.
- **Order type:** market. **Sizing:** q_c of the gold vehicle (GC: q = 1; MGC: q <= 10). The MES leg
  takes no position.
- **Parameters:**
  - **5-minute blocks:** the source's return interval ("extreme negative 5-min S&P500 returns",
    P-K8-003-b).
  - **Block clock 08:30-14:55 CT:** the US stock trading hours that the source contrasts with "post
    US stock trading hours" (P-K8-003-b). The cash session is 08:30-15:00 CT (D1's equity window).
    The last block ends at 14:55 so that every hold is at least 10 minutes.
  - **Tail at 0.5% of the trailing 20-date distribution (judgment).**
    - "Extreme" is not defined in the logged text.
    - A one-in-200 five-minute move is a tail event on any usual reading.
    - With 77 blocks a day, an unclustered 0.5% tail gives about 0.39 triggers a day. That leaves
      events for the power check (arithmetic from the definition, not a data estimate).
    - A trailing distribution measures "extreme" against the current volatility regime rather than a
      fixed level.
  - **20 trailing dates (judgment):** the lookback of D15's B4 feature. About 1,540 blocks, so the
    0.5% cut rests on about 8 order statistics.
  - **n >= 1,200 (judgment):** about 78% of the maximum, so a date with sparse history does not set
    its threshold from few blocks.
  - **One entry per trade date (judgment):** the claim concerns an event, and a day's first extreme
    block is that event.
  - **H30 (judgment):** stands for the "fast reaction" (P-K8-003-c); it is six of the source's
    5-minute intervals after the trigger.
  - **HEOD:** stands for the second claim, that gold "continues to increase" on extreme-decline days
    (P-K8-003-b). It holds to the last fill the XFA allows, with a 3-minute margin before F.
  - **Grid:** {H30, HEOD}, 2 points, each a trial.
- **Expected entries and holding:**
  - At most 1 entry per trade date.
  - Trigger days will be fewer than the unclustered 0.39 a day, because large equity moves cluster on
    volatile days. E.2 reports the count on the research window before screening.
  - Holds: 10-30 minutes (H30); 10 minutes to 6.5 hours (HEOD).
  - **Floor:** at most 1 entry a day (limit 20); every hold at least 10 minutes (so at least 2 full
    minutes); mean at least 10 minutes by construction. OK.
- **Falsification:**
  - **The standard condition:** UCB95 of the member's mean net daily P&L per contract of the gold
    vehicle below gold's eps_X, at >= 80% achieved null power on the intersected confirmation window,
    counts against it.
  - **Sign check (reported, not a trial):** the mean over trades of (gold open at exit - gold open at
    entry), in ticks, is positive.
  - **Clock control (descriptive):** the same gold interval (the entry minute to the exit minute) on
    the window's non-trigger dates. It separates a time-of-day drift in gold from the trigger's
    effect.
- **Topstep check (traded leg: gold):**
  1. **Flat by F:** last fill 15:05; F is 15:08.
  2. **Orders:** market only; no limit, stop, target or bracket.
  3. **D9.3:** at most 1 entry a day; holds at least 10 minutes.
  4. **D9.4:** one trade a day. The entry follows a closed 5-minute block, not a reopen or a release
     minute.
  5. **News (D9.5):** q_c <= 1 lot-equivalent, never the full maximum. A position may span the 13:00
     FOMC statement.
  6. **D9.5a:** no entry fill in [13:00, 13:02) (C6). The 07:30 Employment and CPI guards fall
     before the first possible fill. A fill in [13:00, 13:30) pays D8's event-window cost.
  7. **D9.6:** GC at 1 lot, or MGC at <= 10 contracts = 1 lot.
  8. **D9.7:** gold per C12.
  9. **D9.8 (star):** MGC\* if D2 chooses it. **D9.11:** GC's cap of 3 and MGC's cap of 30 (50K)
     do not bind below the 1-lot cap. **D9.12:** CPI window [07:25, 07:35]; no fill is possible
     there, since the first fill is at 08:35.
  10. **D9.13:** early-close dates are excluded (C5).
- **Member-level coverage (D9, C13):** the gold vehicle from 08:35 to 15:05 CT. D1 measured gold
  only in 07:20-12:30, so E.2 checks 12:30-15:05. MES's RTH coverage was 1.000 (D1 table).
- **Data needed:** MES ohlcv-1m (owned) and the gold vehicle's ohlcv-1m.
  - **Research window:** 2025-04-01..2026-06-19.
  - **Confirmation window:** [max(S_gold, 2020-02-03), 2024-02-29], the D4 intersection with MES's
    S from D.1f.
- **Source window and label:** the source's sample is 2007 to 2018 (P-K8-003-a). It does not overlap
  a confirmation window that starts no earlier than 2020-02-03, so there is no "source-overlap"
  label.
- **Trials in N:** 2 (H30, HEOD).

### K8-oilcad-01 (crude leads the Canadian dollar by one 5-minute step)
- **Cluster** K8.
  - **Signal leg:** WTI crude (K4), read on the crude exposure's price-path series (C9).
  - **Traded leg:** CAD (K3). The only admissible contract is 6C (D1 table).
  - **Vehicle:** D2 (chosen in E.2), which can only be 6C. Traded only if D2 admits CAD.
- **Mechanism:** a large 5-minute move in crude is followed, over the next 5 minutes, by a move of
  CAD against the dollar in the same direction. Causality runs "in the direction of commodity price
  to exchange rate, at horizon one" in 5-minute WTI and CAD/USD data (P-K8-006-a, P-K8-006-b,
  P-K8-006-d). On the direction: "higher oil prices are associated with a depreciation of the U.S.
  dollar ... particularly strong against ... the Canadian dollar" (P-K8-001-e). CAD has the largest
  post-2008 coefficient of the currencies in K8-001's Table 5, 0.090 (P-K8-001-f). New to the
  program.
  - **Conflicting and limiting evidence:**
    - The source itself: "There is weak evidence of Granger-causality in both directions ... The
      measures drop quickly after horizon one" (P-K8-006-b).
    - The measured intensities are tiny: the log's note on Figure 11 gives a chart axis topping at
      0.0024 ([unverified] as values).
    - The 5-minute sample is 2005-2009, from CQG; whether it is spot or futures is [unverified]
      (P-K8-006-a, P-K8-006-e). The source has no out-of-sample test and no costs (K8-006 block).
    - K8-001 finds CAD's response to the WPSR oil shock inside its 15-minute window, and its
      5-minute window gives estimates "very close to the benchmark" (P-K8-001-h). On release days
      the response therefore looks complete within minutes, which leaves little for a one-step lag
      after the block closes.
    - Whether the lead now resolves within seconds is unknown: the log measures it only at the
      5-minute sampling unit. Rule 7 excludes a lead that resolves in seconds; the logged evidence
      shows no such thing, so the member is kept. If the lead does resolve inside the block, the
      member comes out null, and that is its falsification.
- **Signal (on the crude series, K4 clock):**
  - **Decision times:** T = {08:05, 08:10, ..., 13:25} CT, 65 a day. Each covers the block [t - 5, t).
  - **Block return:** r_t = (C_cl(t - 1) - C_cl(t - 6)) / C_cl(t - 6). The denominator must be
    positive (K4 catalog C10), and both bars must carry one instrument_id.
  - **Scale:** s(d) = the sample standard deviation of all defined r_t (t in T) on the 20 most recent
    earlier eligible dates of the same window (C5). n >= 1,000 is required (the maximum is 1,300);
    otherwise there is no trade on d.
  - **Standardized move:** z_t = r_t / s(d).
- **Entry rule:**
  - At t in T, enter if all three hold: the member has no open position; no exit of its own is
    pending at t; and |z_t| >= 2.0.
  - The intent is a market intent on the 6C bar at t - 1, filling at the open of the 6C bar at t.
    BUY if z_t > 0 and SELL if z_t < 0. 6C is quoted in USD per CAD (K3 catalog C8), so a stronger
    CAD is a higher 6C.
  - C6 applies (FOMC at 13:00; WPSR at T_W on release days). On a standard WPSR day the 09:30
    decision, whose block is pre-release, is skipped. The 09:35 decision, whose block holds the
    release response, is not.
- **Exit rule:** market intent on the 6C bar at T_e + 14, filling at the open of T_e + 15 (T_e is
  the entry fill minute).
- **Holding horizon:** 15 minutes. **Session window:** 08:05-13:40 CT. **Flat by F:** 6C's F is 15:08
  (D6 FX row); the last fill is at 13:40.
- **Data fields read:**
  - **Crude series ohlcv-1m close and instrument_id**, bars 07:59..13:24 CT on d and on the 20
    warm-up dates. Databento GLBX.MDP3, paid. CL has history 2019-05..2026-06; MCL only from
    2021-07-12 (C9). Available at each bar's close.
  - **6C ohlcv-1m open and instrument_id**, 08:05..13:40 CT. Paid; history 2019-05..2026-06.
  - **EC-CAL** (energy and FX groups), and **EC-FOMC, EC-BLS and EC-WPSR** (for C6 only). Free,
    known before d.
- **Order type:** market. **Sizing:** q_c of 6C. That is 1, the cap for a full-size-only exposure,
  and D2 may flag it "undersized". The crude leg takes no position.
- **Parameters:**
  - **5-minute block and one-step horizon:** K8-006's sampling unit and its "horizon one"
    (P-K8-006-a, P-K8-006-b).
  - **Blocks inside 08:00-13:30 CT (judgment):** the energy day session (D6 table: O 08:00, C 13:30),
    which lies inside 6C's day session (O 07:20, C 14:00). K8-006 does not state the session hours
    of its 5-minute series.
  - **|z| >= 2.0 (judgment).** K8-006 fits a linear VAR, which has no threshold.
    - Two standard deviations select the largest few percent of blocks: 4.6% under a normal
      approximation, about 3 of the 65 a day.
    - Those are the blocks where a one-step spillover of a fixed fraction of the crude move is
      largest against 6C's fixed round-turn cost.
    - The cut also keeps entries far below the cap.
  - **20 trailing dates and n >= 1,000 (judgment):** as in K8-flight-01; 1,000 is about 77% of the
    maximum.
  - **Hold of 15 minutes (judgment).**
    - K8-001's benchmark response window is 15 minutes (P-K8-001-a, P-K8-001-b).
    - K8-006's measures last "only about one hour" in the 5-minute VAR (P-K8-006-c), but they sit
      mostly in the first step.
    - A 10-minute hold would sit exactly on D9.3(c)'s mean floor, where any shortened hold (a forced
      D9.7 exit) would fail it. 15 is the next multiple of the block length.
  - **Grid:** none.
- **Expected entries and holding:**
  - About 3 blocks a day pass the threshold under a normal approximation (arithmetic, not a data
    estimate). Entries are fewer, because of the busy skip.
  - At most 17 entries a day by construction. The 15-minute hold plus the pending-exit skip space
    entries at least 20 minutes apart within the 320 minutes from 08:05 to 13:25.
  - Every hold is 15 minutes.
  - **Floor:** at most 17 entries (limit 20); each hold is 15 minutes (at least 2 full minutes); the
    mean is 15 (at least 10). OK.
- **Falsification:**
  - **The standard condition,** on CAD's eps_X.
  - **Sign check (reported):** the mean over trades of sign(z_t) x (6C open at exit - 6C open at
    entry), in ticks and gross of cost, is positive.
  - **Descriptive split:** the same statistic for the 09:35 decision on standard WPSR days alone, and
    for all other decisions.
- **Topstep check (traded leg: 6C):**
  1. **Flat by F:** last fill 13:40.
  2. **Orders:** market only.
  3. **D9.3:** at most 17 entries a day; 15-minute holds.
  4. **D9.4:** entries at least 20 minutes apart; no stops, targets or brackets; not a queue-position
     or stray-fill strategy.
  5. **News:** q_c = 1 = 1 lot-equivalent, half the XFA maximum.
  6. **D9.5a:** no entry fill in a guarded interval (C6). On WPSR and FOMC days, fills in [release,
     release + 30 min) pay D8's event-window cost.
  7. **D9.6:** 6C counts 1 lot.
  8. **D9.7:** 6C per C12.
  9. **D9.8:** 6C is unstarred. **D9.11 and D9.12** name no FX product.
- **Member-level coverage (D9, C13):**
  - 6C, 08:05-13:40: inside D1's measured 07:20-14:00 window, where coverage was 0.985.
  - Crude, 07:59-13:24: the energy window of D1, coverage 1.000, except the single bar at 07:59.
- **Data needed:** ohlcv-1m of the crude series and of 6C.
  - **Research window:** 2025-04-01..2026-06-19.
  - **Confirmation window:** [max(S_crude, S_CAD), 2024-02-29].
- **Source window and label:**
  - K8-006: 2005-01-03..2009-12-31 for the 5-minute data (P-K8-006-a); 1986-2015 for the daily data
    (K8-006 block).
  - K8-001: 2003M10..2017M10 (P-K8-001-g).
  - No overlap, so no label.
- **Trials in N:** 1.

### K8-wkndbtc-01 (the weekend bitcoin move predicts the Monday Nasdaq-100 trade date)
- **Cluster** K8.
  - **Signal leg:** bitcoin (K7), read on MBT bars.
  - **Traded leg:** the Nasdaq-100 (K1). Admissible contracts: MNQ\* and NQ (D1 table).
  - **Vehicle:** D2 (chosen in E.2). Traded only if D2 admits the Nasdaq-100.
- **Mechanism:** a negative weekend move in crypto is followed by a weaker Monday for stocks.
  "negative cryptocurrency returns and increased volatility during weekends predict poorer stock
  market performance on Mondays, an effect that became particularly evident following the LUNA crash
  in mid-2022" (P-K8-004-b). The paper studies "how cryptocurrency weekend returns and volatility
  affect Monday stock returns" with a Bayesian regression and a Kalman filter (P-K8-004-a). New to
  the program.
  - **Evidence status:** abstract only, from a 17-page working paper (K8-004). The following are
    [unverified]: which stock indexes, cash or futures, the definition of the Monday return, the
    crypto series, the sample and costs. The dependence on a regime (after LUNA) is itself a
    stability warning.
  - **Reasoned transfer (not tested by the source).**
    - **The weekend move is read from CME's bitcoin futures:** MBT's change from Friday 14:59 to
      Sunday 17:59 CT. MBT is "0.10 bitcoin, as defined by the CME CF Bitcoin Reference Rate (BRR)"
      (liquidity JSON), so it tracks the bitcoin price the source's crypto returns measure, up to
      changes in the basis.
    - **What remains tradeable:** the XFA cannot hold over the weekend, and the equity futures'
      Sunday reopening gap cannot be traded. If the source's Monday return runs from the Friday close
      ([unverified]), part of its effect sits in that gap. The member tests what remains of the
      Monday trade date after Sunday 18:00 CT.
    - **Scope:** only the return part is used. The volatility part is excluded (X-10).
  - **Choice of traded exposure (judgment): the Nasdaq-100.**
    - The source's "stock market" is [unverified]. Its most likely referent, the S&P 500, is not a
      traded exposure (D1.5).
    - Of the three IN K1 exposures, the Nasdaq-100 is, like the S&P 500, a capitalization-weighted
      large-cap index. The Dow is a price-weighted 30-stock index and the Russell 2000 a small-cap
      index.
    - It is also the most liquid (MNQ ADV 2,363,465).
    - RTY and YM are not written (X-11).
- **Signal (on MBT, K7 clock):**
  - **Prices:** P_F = C_MBT(14:59) on the Friday immediately before Monday trade date d;
    P_S = C_MBT(17:59) on the Sunday that opens d.
  - **Validity:** both bars present with one instrument_id, and the Friday a full trade date in EC-CAL
    (equity-and-crypto). Otherwise there is no trade.
  - **Signal:** G = P_S / P_F - 1. If G = 0, there is no trade.
  - **Both regimes:** before 2026-05-29 the interval spans CME's weekend closure, and the Sunday
    17:59 close comes after one hour of trading following the 17:00 reopen. After 2026-05-29
    16:00 CT the interval spans continuous trading (C3). The definition is the same in both regimes,
    and it reads no bar outside a program trade date.
- **Entry rule:** on Monday trade date d, market intent on the Nasdaq-100 vehicle's bar at 17:59 CT
  Sunday, filling at the open of its 18:00 bar. BUY q_c if G > 0; SELL q_c if G < 0.
- **Exit rule:** market intent on the vehicle's bar at 14:58 CT Monday, filling at the 14:59 open.
  This is the C - 2 convention of D6's CP1, with C = 15:00.
- **Holding horizon:** 20 h 59 min. **Session window:** Sunday 18:00 to Monday 14:59 CT, inside one
  trade date (C3). **Flat by F** (15:08): the last fill is at 14:59.
- **Exclusions (in addition to C5):**
  - Monday trade dates that EC-CAL marks as early halt or closure. These are the US holiday Mondays;
    in the research window 2025-05-26, 2025-09-01, 2026-01-19, 2026-02-16 and 2026-05-25.
  - Monday trade dates whose preceding Friday is not a full trade date, for example Good Friday.
- **Data fields read:**
  - **MBT ohlcv-1m close and instrument_id**, at Friday 14:59 (available at 15:00 Friday) and at
    Sunday 17:59 (available at 18:00 Sunday). Databento GLBX.MDP3, paid. History from 2021-05-03
    only (listing; D13), so there are **no signal data for 2019-05..2021-04.**
  - **Nasdaq-100 vehicle ohlcv-1m open and instrument_id**, at Sunday 18:00 and Monday 14:59. Paid;
    NQ from 2019-05, MNQ from 2019-05-06.
  - **EC-CAL** (equity-and-crypto group). Free, known in advance.
- **Order type:** market. **Sizing:** q_c of the Nasdaq-100 vehicle (NQ: 1; MNQ: <= 10). The MBT leg
  takes no position.
- **Parameters:**
  - **P_F at Friday 14:59 (judgment):** the last minute of the US cash session (08:30-15:00 CT), so G
    starts when the stock market closes for the weekend. The source's starting point is [unverified].
  - **P_S at Sunday 17:59, entry at 18:00 (judgment).**
    - One hour after CME's Sunday 17:00 CT reopen (Topstep F4 "Sunday open | 5:00 PM CT"), the entry
      is clear of the reopen's first minutes. Those minutes are the gapped market of D9.4, as the K7
      catalog's X-01 reads [F7.2].
    - 18:00 CST is 00:00 UTC Monday, the usual end of a weekend in daily UTC crypto data. In CDT,
      18:00 CT is 23:00 UTC. The source's clock is [unverified].
  - **Symmetric sign (judgment).** The source's model relates Monday returns to weekend returns
    (P-K8-004-a), and its abstract states the negative side (P-K8-004-b). A linear reading predicts
    both signs. The negative side is reported separately (see Falsification).
  - **Exit at 14:59:** D6's C - 2 convention for the equity group.
  - **Grid:** none.
- **Expected entries and holding:**
  - At most 1 entry a week: Monday trade dates only, about 0.2 per trade date.
  - About 58 Mondays in the research window after the holiday Mondays (63 - 5). At most 148 in the
    confirmation window from 2021-05-03, before holiday, roll, missing-bar and start-rule exclusions
    (C11).
  - Each hold is 20 h 59 min.
  - **Floor:** OK.
  - **Power:** likely "inconclusive by design" under D4 (question 2).
- **Falsification:**
  - **The standard condition,** on the Nasdaq-100's eps_X.
  - **Sign check (reported):** the mean of sign(G) x (vehicle open at 14:59 - open at 18:00), in
    ticks, is positive.
  - **Splits (descriptive):** by the sign of G, since the abstract's claim is for G < 0; and by
    period, before and after 2022-06-30, since the abstract says the effect appeared "following the
    LUNA crash in mid-2022".
- **Topstep check (traded leg: the Nasdaq-100):**
  1. **Flat by F:** last fill 14:59. The position opens after Topstep's "Sunday open | 5:00 PM CT"
     (F4) and stays inside one trade date.
  2. **Orders:** market only.
  3. **D9.3:** 1 entry a week.
  4. **D9.4:** the entry comes 60 minutes after the reopen; it is not a stray-fill trade in a gapped
     market.
  5. **News:** q_c <= 1 lot-equivalent, never the full maximum. The position spans the Monday 07:30
     releases and any later ones.
  6. **D9.5a:** no fill in a guarded interval; the fills are on Sunday at 18:00 and Monday at 14:59.
  7. **D9.6:** NQ at 1, or MNQ at <= 10.
  8. **D9.7:** equity-index limits bind on Sunday evenings after large weekend news. The harness
     blocks the entry, and forces the exit, beyond the stop level (C12).
  9. **D9.8:** MNQ\* if D2 chooses it (referent D9.12). **D9.12:** no opening fill falls in a CPI
     window, since entries are only at 18:00 on Sundays. **D9.11** names no equity product.
- **Member-level coverage (D9, C13):**
  - The Nasdaq-100 vehicle at Sunday 18:00 and Monday 14:59. D1 measured only 08:30-15:00, so the
    Sunday-evening minute is E.2's check.
  - The MBT signal bars at Friday 14:59 and Sunday 17:59 (C13).
- **Data needed:** MBT and Nasdaq-100 vehicle ohlcv-1m, including the Sunday-evening Globex bars.
  - **Research window:** 2025-04-01..2026-06-19. Three of its Mondays (2026-06-01, 06-08, 06-15)
    fall after the 24/7 change.
  - **Confirmation window:** [max(S_MBT, S_Nasdaq), 2024-02-29], with S_MBT >= 2021-05-03.
- **Source window and label:** the sample is [unverified]. It includes mid-2022 and later
  (P-K8-004-b; the paper was posted on 6 Aug 2025), so it overlaps the confirmation window. The member
  is labelled **"source-overlap"** (NULL_CRITERIA_E section 3). A null statement is unaffected, but no
  edge on it could be claimed without a registered holdout read.
- **Trials in N:** 1.

### K8-ml-01 (the ML member, D15; this entry fills only D15.10's fields)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-09: 6C only; if 6C is not admitted, no ML member (the mechanism is crude to CAD).]
- **Traded vehicle: CAD {6C}.** Traded only if D2 admits CAD.
  - **Why CAD:** it is the exposure the K8 log supports most.
    - Both of the log's full-text directional sources name it. K8-006 has the log's only 5-minute
      lead, crude to CAD (P-K8-006-a, P-K8-006-b). In K8-001, CAD has the largest post-2008 response
      of the currencies to the WPSR oil shock (P-K8-001-e, P-K8-001-f).
    - The partition names "crude and CAD" as a K8 relationship (section 3).
    - The alternatives rest on less. Gold rests on one abstract (K8-003). The Nasdaq-100 rests on one
      abstract (K8-004) plus contemporaneous or off-universe evidence (K8-001, K8-002, K8-007).
  - **Contract:** 6C is CAD's only admissible contract (D1 table; ADV 81,946).
  - **No fallback is declared.** If D2 does not admit CAD, the lead decides.
- **Products the features read:**
  - 6C, its own bars: B1-B5 and KF5.
  - The crude series (K4, C9): KF1, KF2, KF4 and KF5. Crude is named by K8-006 and K8-001.
  - MES (K1): KF6. The S&P 500 is named by K8-006 as its conditioning series and by K8-001 as a
    responding market.
  - Calendars: EC-WPSR (KF3, KF4) and EC-CAL (FX, energy, equity-and-crypto groups).
- **Cluster features (6; with D15.4's B1-B5 the total is 11).** Notation:
  - t_j is the decision time; the last bar closed at t_j is the bar at t_j - 1.
  - C_X(tau) is the close of leg X's bar at tau.
  - Returns are in basis points (10,000 x the fraction), so they are the same on any contract of a
    leg.
  - A missing bar, or a change of instrument_id inside one feature's bars, means no trade at t_j
    (D15.4).

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | cl_ret5 | 10,000 x (C_cl(t_j - 1) - C_cl(t_j - 6)) / C_cl(t_j - 6) | K8-006 P-K8-006-a, P-K8-006-b (5-minute data; the lead is at horizon one) | t_j (the bar at t_j - 1 has closed) |
| KF2 | cl_ret60 | 10,000 x (C_cl(t_j - 1) - C_cl(t_j - 61)) / C_cl(t_j - 61) | K8-006 P-K8-006-c (causality measures over 11 five-minute lags, "only about one hour") | t_j |
| KF3 | wpsr_phase | If d is an EC-WPSR release date with scheduled time T_W(d) (C10, the schedule known the evening before d): -1 if t_j < T_W(d), +1 if t_j >= T_W(d). Otherwise 0 | K8-001 P-K8-001-a, P-K8-001-b (WPSR news moves crude, and CAD with it, inside the release window) | calendar, known before d |
| KF4 | cl_wpsr | If KF3 = +1 and t_j >= T_W(d) + 10: 10,000 x (C_cl(T_W + 9) - C_cl(T_W - 6)) / C_cl(T_W - 6), the crude return over [T_W - 5, T_W + 10]. Otherwise 0. The 0 is a fixed literal (no release, or its window has not closed), not an imputation. A missing bar inside the window means no trade at t_j | K8-001 P-K8-001-b (the [-5; +10]-minute window); P-K8-001-e, P-K8-001-f (the CAD response) | T_W + 10 |
| KF5 | cad_gap30 | 10,000 x [(C_6C(t_j - 1) - C_6C(t_j - 31)) / C_6C(t_j - 31) - 0.090 x (C_cl(t_j - 1) - C_cl(t_j - 31)) / C_cl(t_j - 31)]: CAD's 30-minute move minus the move implied by crude's | K8-001 P-K8-001-f (0.090, the post-2008M9 CAD coefficient, a return-on-return coefficient: see the preamble) and P-K8-001-h (the estimate holds on a 30-minute window); K8-006 P-K8-006-b (direction: crude to CAD) | t_j |
| KF6 | es_ret30 | 10,000 x (C_MES(t_j - 1) - C_MES(t_j - 31)) / C_MES(t_j - 31) | K8-006 P-K8-006-d, P-K8-006-e (the S&P 500 is the conditioning series of the 5-minute analysis); K8-001 P-K8-001-c (the stock market moves with oil in the release window) | t_j |

  - The literal 0.090 is fixed here. It is not estimated on any window (D15.4).
  - No feature reads a released inventory value, a settlement price, or anything published after
    t_j.
  - B1-B5 are computed on 6C. B3 is minutes since O = 07:20 (D6 FX row).
- **Decision window [W0, W1] = [08:10, 12:55] CT; horizon h = 15 minutes.**
  - **Decision times:** 08:10, 08:25, ..., 12:55, which is 20 a day. W1 + h = 13:10, before
    F = 15:08.
  - **Fills (D15.3, D15.6):** entries at t_j + 1 (:11, :26, :41, :56); exits at t_j + h (:25, :40,
    :55, :10).
  - **Why this window:**
    - It starts after the energy day-session open (08:00, D6), so KF1 reads day-session crude from
      the first decision. It also starts after the 07:30 BLS releases.
    - The :10/:25/:40/:55 grid makes t_j = 09:40 = T_W + 10 on standard WPSR days, the first decision
      at which KF4 exists. For exception releases at 10:00 or 11:00 CT, T_W + 10 = 10:10 or 11:10 is
      also a decision time.
    - No fill falls in [:00, :02) or [:30, :32). None therefore meets the D9.5a interval of the
      07:30, 09:30, 10:00, 11:00 or 13:00 releases (C6).
    - W1 = 12:55 gives the 20 decisions the cap allows. On statement days the last position
      (12:56-13:10) spans the FOMC statement without a fill in its guarded interval.
    - The window lies inside 6C's day session (07:20-14:00) and crude's (08:00-13:30).
  - **Why h = 15:** the smallest value on the menu, and the one nearest the logged horizons.
    - K8-006's lead is one 5-minute step, and its measures fade within "about one hour"
      (P-K8-006-b, P-K8-006-c).
    - K8-001's benchmark window is 15 minutes (P-K8-001-a, P-K8-001-b).
    - h = 30 or more would dilute a one-step lead with minutes the log gives no reason to hold, and
      would allow at most 10 decisions in the window.
- **Expected rows:** 20 per eligible research-window trade date. From about 305 trade dates, remove
  6C's roll-blackout dates, early-halt dates, vendor-degraded dates and B4's 20-date warm-up; about
  260-270 dates remain. That gives about 5,200-5,400 rows; E.2 gives the exact count.
- **Expected entries:** at most 20 a day, each held 15 minutes. The floor holds by construction.
- **Falsification:** the standard condition: UCB95 of the mean net daily P&L per contract of 6C below
  CAD's eps_X, at >= 80% achieved null power on the confirmation window, counts against it. Failing
  the D5 screen puts the member in Tier B.
- **Topstep check (6C):**
  1. **Flat by F:** last exit 13:10.
  2. **Orders:** market (D15.6).
  3. **D9.3:** at most 20 entries a day; 15-minute holds.
  4. **D9.4:** no stops or brackets; no fill in a release minute.
  5. **News:** q_c = 1 lot-equivalent.
  6. **D9.5a:** no fill in any guarded interval, by construction. On WPSR days, the fills at 09:40,
     09:41, 09:55 and 09:56 pay D8's event-window cost; on FOMC days, the 13:10 exit does.
  7. **D9.6:** 1 lot.
  8. **D9.7:** 6C per C12.
  9. **D9.8:** 6C is unstarred. **D9.11 and D9.12** name no FX product.
  10. **D9.9:** the "Unfair technology ... AI" line is flagged for the user, as the design does for
      every ML member.
- **Data needed:** ohlcv-1m of 6C, the crude series and MES.
  - **Training and tuning:** on the research window only (MES's research parquet; the other legs are
    bought in E.1).
  - **The frozen model:** runs on the confirmation window [max(S_CAD, S_crude, 2020-02-03),
    2024-02-29].
  - **Coverage (C13):** 6C 08:11-13:10; crude 07:09-12:54 (KF2 at 08:10 reads the crude bar at
    07:09, before the energy day session); MES 07:39-12:54.
- **Source window and label:** K8-001 covers 2003M10..2017M10; K8-006 covers 2005-2009 (5-minute)
  and 1986-2015 (daily). No overlap, so no label.
- **Trials in N:** 1 at confirmation. In the K8 screening session's research-window accounting the
  grid counts as 48 (D15.8).
- **Not chosen here (D15):** the model type, grid, selection rule and trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K8-wpsrcad-01 | 6C traded from T_W + 10 on the sign of crude's [T_W - 5, T_W + 10] return, held 15-30 minutes (K8-001 P-K8-001-b, e, f) | Rule 1 (evidence) | K8-001 measures CAD's response inside the release window and tests no lag. Its 5- and 30-minute windows give point estimates "very close to the benchmark" (P-K8-001-h), so the logged evidence places the whole response inside the window, with no documented move after T_W + 10. The release response enters K8-ml-01 (KF3, KF4), and K8-oilcad-01's 09:35 decision covers the one-step case |
| X-02 K8-wpsreq-01 | NQ, RTY or YM traded after the WPSR on crude's release-window return (P-K8-001-c: +1.1% per +10% oil after 2008) | Rule 1 | The relation is contemporaneous and no lag is measured. The equity leg is SPY and sector ETFs, not NQ, RTY or YM (K8-001 legs line). The sign flips at 2008M9 (-0.8% before, +1.1% after, P-K8-001-c), so the relation is unstable |
| X-03 K8-wpsrzn-01 | ZN, ZF or ZT traded after the WPSR on crude's return (P-K8-001-d) | Rule 1 | Contemporaneous. After 2008 the 10-year yield moves "0.7 bps" per +10% oil, and the shorter tenors are "statistically insignificant" (P-K8-001-d). The authors call the bond effects economically small (K8-001 quality tells) |
| X-04 K8-oilcomfx-01 | 6A and 6N (and 6E, 6B) traded on crude's 5-minute moves, as in K8-oilcad-01 | Rule 1 | The 5-minute evidence is "available for Canada only" (P-K8-006-a). K8-001's coefficients for AUD, NZD, EUR and GBP (P-K8-001-f) are contemporaneous. K8-006's AUD result is daily (K8-006 block) and has X-05's problem |
| X-05 K8-oilcadday-01 | 6C traded in the day session on the sign of crude's prior-day return (K8-006's daily "horizon one", P-K8-006-d) | Rule 3 (timing); rule 1 | The daily series come from different publishers: CAD/USD "from Statistics Canada" and WTI "from Energy Information Administration" (the K8-006 Table 1 note, in the reader's copy; preamble). Their sampling times are not stated and are not shown to be one clock, so a one-day "lead" can come from the sampling offset alone. A rule on synchronized CME bars would be a new test with no logged horizon. The synchronized 5-minute version is K8-oilcad-01 |
| X-06 K8-apieq-01 | NQ, RTY or YM traded 08:30-08:40 CT on Wednesday in the direction of crude's post-API return (Tuesday 15:30-16:00 CT) (K8-002 P-K8-002-a, b, c) | Rule 1; D9.3(c) margin | The responding leg is energy stocks and the NYSE Arca Oil and Gas Index (P-K8-002-c), which are off-universe. The implication for index futures is untested (K8-002 tags), and in a broad index the effect would be diluted by the energy sector's weight. The documented window is 10 minutes, exactly the D9.3(c) mean floor. The crude-only part of the same paper is covered by K4-apipre-01 |
| X-07 K8-oilvol-01 | a crude or equity-index member gated by the other market's 5-minute volatility, spread or volume (K8-007 P-K8-007-a, b) | Rule 1 | Abstract only. The predicted quantity is volatility, not direction, and the "utility gains" are mean-variance certainty equivalents, not net P&L (K8-007 quality tells). A gate needs a base member on crude or an equity index; K8 has none, and K4 and K1 own their own base members |
| X-08 K8-eqopenzn-01 | ZN traded after 08:30 CT in the direction implied by MES's first 30 minutes (K8-008) | Rule 1 | The source measures information shares, not returns (P-K8-008-a, P-K8-008-b). Its link to "returns and net order flows of the US stock market" appears only in the published abstract, with no sign ([unverified] content; P-K8-008-c). The manuscript's state-space check finds "little variation" (P-K8-008-d). ZN's own post-open window is covered by K2-ml-01 (eqopen_ret, from K2-017, the same paper) |
| X-09 K8-flightpost-01 | gold bought at the US stock close on extreme-decline days and held for the "post US stock trading hours" rise (P-K8-003-b) | Flat by F (D9.1) | The continuation comes after 15:00 CT. The XFA allows only the minutes up to 15:08 and no overnight hold. The in-session lead-in is K8-flight-01's HEOD point |
| X-10 K8-wkndvol-01 | a Monday Nasdaq-100 short after high weekend crypto volatility (P-K8-004-b, "increased volatility") | Rule 3; partition section 1 | Before 2026-05-29 CME has no weekend bitcoin bars (C3), so weekend volatility needs spot intraday data. Coinbase's candles are free (K7 catalog preamble and C10), but a non-CME signal for a K1 product belongs to K1's region (partition section 1), not K8's. The source's volatility measure is [unverified] |
| X-11 K8-wkndbtc-01 variants | (a) the same rule on RTY and on YM (+1 trial each); (b) the short-only reading (trade only G < 0); (c) entry at the Monday 08:30 CT cash open instead of Sunday 18:00 | Rule 11 (no padding); judgment | One trial is proportionate for an abstract-only source. (a) The source's index is [unverified], and the Nasdaq-100 was chosen with a reason (K8-wkndbtc-01). (b) is a subset of K8-wkndbtc-01's trades and is reported there as a split. (c) is a sub-interval of the same holding window. The lead may add any of them |
| X-12 K8-cadcl-pair-01 | an intraday crude-CAD spread (F19, Milton FMR) | D2 and rule 5; rule 1 | Two legs at full size are 2 lot-equivalents, and MCL plus 6C is 1.1 (6C has no admissible micro). The logged source is a daily cointegration trade with multi-day holds (R-K8-014) |
| X-13 K8-fomcsurp-01 | gold, 6E, 6J or CL traded on the FOMC target or path surprise measured from fed funds futures. Routed by the K3 catalog (X-06, K3-009), the K4 catalog (Rosa, K4-025) and the K5 catalog (K5-024) | Rule 1 (not in the K8 log); rule 3 | These routings came from catalogs written after the K8 log closed, and the K8 log holds no passage for them. The surprise needs CBOT 30-day fed funds futures bars, a product outside Topstep's list and outside the D13 purchase plan, so a quote would be needed. On the evidence in the other logs: gold's continuation is covered by K5-fomc-01 (gold's own first five minutes as the surprise proxy); the FX reaction is "short-lived" (P-K3-009-a); Rosa's dollar channel is contemporaneous (F13). See question 7 |
| X-14 K8-mpucond-01 | FX or crude macro-release responses conditioned on monetary-policy uncertainty (K3-035, routed by the K3 and K4 catalogs) | Rule 1; rule 3 | Not in the K8 log, and abstract only. The uncertainty measure is [unverified], with no free historical source named. No cluster has a macro-release base member to condition (K3 X-05) |

---

## 3. Beyond budget

None. 4 of the 15 slots are used. No member was dropped for budget. The variants considered and not
written are in section 2 (X-11), each with its reason, and the lead may add any of them.

---

## 4. Log accounting

**Passed items (log section 4).**

| Item | Disposition |
|---|---|
| K8-001 Alquist, Ellwanger, Jin (full text) | **Used.** K8-oilcad-01: direction and the choice of CAD (P-e, P-f), with P-h as conflicting evidence. K8-ml-01: KF3 (P-a, b), KF4 (P-b, e, f), KF5 (P-f, h), KF6 (P-c). **Excluded as standalone members:** X-01 (6C on the release window), X-02 (equity index), X-03 (Treasuries), X-04 (6A, 6N, 6E, 6B). All are contemporaneous, with no lag measured |
| K8-002 Alturki, Kurov (full text, dissertation) | **Excluded:** X-06 (the responding leg is off-universe). The crude-only part is **covered by K4-apipre-01** |
| K8-003 Baur, Kuck (abstract only) | **Used:** K8-flight-01 (P-a, b, c). The post-close part is **not intraday-feasible** (X-09) |
| K8-004 Mourey, Shahrour, Soiman (abstract only) | **Used:** K8-wkndbtc-01 (P-a, b). The volatility part is excluded (X-10); variants in X-11 |
| K8-005 Buccheri, Corsi, Peluso | Did not survive in the log (not cross-cluster; R-K8-040). Not used |
| K8-006 Zhang, Dufour, Galbraith (full text) | **Used.** K8-oilcad-01 (P-a, b, c, d, e). K8-ml-01: KF1 (P-a, b), KF2 (P-c), KF5 (P-b), KF6 (P-d, e). The daily version is excluded (X-05); the other currencies too (X-04) |
| K8-007 Phan, Sharma, Narayan (abstract only) | **Excluded:** X-07 (no direction; needs a base member) |
| K8-008 Indriawan, Jiao, Tse (manuscript) | **Excluded:** X-08 (no direction). ZN's own post-open window is **covered by K2-ml-01** (eqopen_ret) |

**Routed flags (log section 1).**

| Flag | Item | Disposition |
|---|---|---|
| F01 | Kurov, Olson, Wolfe (2024) | Insufficient evidence: rejected in the log (R-K8-001; contemporaneous causal effects, no lead) |
| F02 | Zangelidis, Rezitis (2026) | Insufficient evidence (R-K8-002; volatility topology on daily realized volatility) |
| F03 | Sharma (arXiv 1705.08022) | Not intraday-feasible (R-K8-003; the macro variables' frequency). The K2 and K3 catalogs routed the same item; same disposition |
| F04 | Alquist, Ellwanger, Jin | **Used:** see K8-001 |
| F05 | K2's note to search rates-equity and rates-energy | Handled in containers 2 and 5. The only rates result is K8-001's contemporaneous bond response (X-03) |
| F06 | Aligrithm cross-asset series | Not intraday-feasible (R-K8-004; monthly or daily sources) |
| F07 | Peng, Chollete, Hughen (2026) | Insufficient evidence (R-K8-005; mixed-frequency volatility forecasting) |
| F08 | Quantpedia currency-spillover slugs | Insufficient evidence (R-K8-006; pages unreachable; the described source is monthly) |
| F09 | K3-001 ownership (Melvin and Prins) | **Covered by K3-mehedge-01.** Ownership is reserved for the lead (question 8) |
| F10 | Alturki, Kurov | See K8-002: excluded (X-06); covered by K4-apipre-01 |
| F11 | Quantpedia "Crude Oil Predicts Equity Returns" | Not intraday-feasible (R-K8-007; monthly) |
| F12 | Hao, He, Ma (2023) | Insufficient evidence (R-K8-008; volatility spillover, no return lead) |
| F13 | Rosa (2013), K4-025 | Excluded (X-13): contemporaneous dollar channel; K4-025 is read by K4 |
| F14 | Nowak, Anderson (2014) | Insufficient evidence (R-K8-009; single stocks) |
| F15 | Wu, Guan, Myers (2010) | Insufficient evidence (R-K8-010; volatility spillover, no intraday horizon) |
| F16 | energy-grain volatility spillover items | Insufficient evidence (R-K8-011; volatility) |
| F17 | Chiang, Hughen (2017) | Not intraday-feasible (R-K8-012; monthly) |
| F18 | Quantpedia "Financialization of crude oil market" | Insufficient evidence (R-K8-013; variance decomposition) |
| F19 | Milton FMR CAD-crude pairs | Not intraday-feasible (R-K8-014; daily, multi-day holds). A spread would also fail D2 (X-12) |
| F20 | arXiv 1209.0900, 1210.6080 | Not intraday-feasible (R-K8-015; low frequency) |
| F21 | gold against the dollar and real rates (no source pinned) | Insufficient evidence: the six container-3 queries produced no passing item (log section 2) |
| F22 | Wright Blogs "Metals as Macro Signals" | Insufficient evidence (R-K8-016) |
| F23 | Baur, Kuck | **Used:** K8-flight-01 |
| F24 | Semeyutin, Gozgor, Lau (2021) | Insufficient evidence (R-K8-017; contemporaneous co-jumps) |
| F25 | arXiv 2409.08355 | Not intraday-feasible (R-K8-018; low frequency) |
| F26 | Quantpedia gold regimes | Insufficient evidence (R-K8-019) |
| F27 | Ebrahimi, Ferris (2025) | Not intraday-feasible (R-K8-020; monthly horizon) |
| F28 | CME OpenMarkets soybean oil and crude | Not intraday-feasible (R-K8-021; a lead of months) |
| F29 | CME energy demand and the soybean complex | Insufficient evidence (R-K8-022) |
| F30 | CME grains and equities in downturns | Insufficient evidence (R-K8-023) |
| F31 | Cao, Heckelei, Ionici (2024) | Insufficient evidence (R-K8-024; single food stocks) |
| F32 | CFTC OCE agricultural swaps and equities | Insufficient evidence (R-K8-025) |
| F33 | CFTC OCE convective risk flows | Not intraday-feasible (R-K8-026; daily) |
| F34 | K6-032 (EPA and CARB) | Not K8's: the lead ruled that it stays in K6 |
| F35 | Conlon, Corbet, Oxley (2024) | Excluded: sentiment, shelved (rule 13; R-K8-027) |
| F36 | Kose et al. (2024) | Not intraday-feasible (R-K8-028; daily and weekly) |
| F37 | Aalborg et al. (2018) | Not intraday-feasible (R-K8-029; daily) |
| F38 | Mourey et al. | **Used:** K8-wkndbtc-01 |
| F39 | arXiv 2505.14655 | Insufficient evidence (R-K8-030; single stocks) |
| F40 | Krause (2026); Lee (2024) | Not intraday-feasible (R-K8-031; daily correlation regimes) |
| F41 | Shakourloo (2026) | Insufficient evidence (R-K8-032; no intraday horizon) |
| F42 | Joo (2023) | Not intraday-feasible (R-K8-033; daily hedge ratios) |
| F43 | Mazur (2024), K7-027 | Covered by the K7 log (K7-027). The flow substitution is daily; no K8 member |
| F44 | CME research on bitcoin, equities and gold | Insufficient evidence (R-K8-034; commentary) |
| F45 | Pinchuk, K7-026 | Covered by the K7 log (K7-026); rates enter there only as a control |
| F46 | Quantpedia bitcoin, gold and equity items | Not intraday-feasible (R-K8-035; daily or longer) |
| F47 | Alquist et al. (K2's mention) | Duplicate of F04 |

**Rejected container items R-K8-036 to R-K8-082:** rejected in the log, none passed, none used. The
items the log leaves to the lead are listed unchanged in question 10: R-K8-045, R-K8-048, R-K8-058
and R-K8-071.

**Routings from the other catalogs' "Routed to K8" sections** (written after the K8 log closed):

| Catalog | Rows | Disposition |
|---|---|---|
| K2 | Sharma; Alquist | = F03; = F04 |
| K3 | rows 1-4 (Alquist, Aligrithm, Peng et al., Quantpedia slugs) | = F04, F06, F07, F08 |
| K3 | row 5: K3-009 surprise (the K3 catalog's X-06) | Excluded, X-13 |
| K3 | row 6: K3-035 | Excluded, X-14 |
| K3 | rows 7-10 (Sharma, Rosa, Milton FMR, Zangelidis) | = F03, F13, F19, F02 |
| K4 | rows 1-13 (the reader's flags) | = F04, F10, F11, F01, F12, F13, F14, F15, F16, F17, F18, F19, F20 |
| K4 | row 6's addition (the FOMC surprise measure) | Excluded, X-13 |
| K4 | row 14: K3-035 [K4] | Excluded, X-14 |
| K5 | rows 1-7 | = F21, F22, F23, F24, F25, F26, F27 |
| K5 | row 8: K5-024 rate surprise | Excluded, X-13. The own-price version is covered by K5-fomc-01 |
| K6 | all rows | = F28-F33, F16, F20; K6-032 = F34 |
| K7 | all rows | = F35-F46. Its 24/7 note is used in C3 and K8-wkndbtc-01 |

---

## 5. Trial count table

| Member | Traded exposure (cluster) | Signal leg (cluster) | Trials at confirmation | eps | Confirmation window (D4 intersection) | Label |
|---|---|---|---|---|---|---|
| K8-flight-01 H30 | gold (K5) | S&P 500 on MES (K1) | 1 | gold eps_X | [max(S_gold, 2020-02-03), 2024-02-29] | none |
| K8-flight-01 HEOD | gold (K5) | S&P 500 on MES (K1) | 1 | gold eps_X | same | none |
| K8-oilcad-01 | CAD (K3) | crude (K4) | 1 | CAD eps_X | [max(S_crude, S_CAD), 2024-02-29] | none |
| K8-wkndbtc-01 | Nasdaq-100 (K1) | bitcoin on MBT (K7) | 1 | Nasdaq-100 eps_X | [max(S_MBT, S_Nasdaq), 2024-02-29], with S_MBT >= 2021-05-03 | **source-overlap** |
| K8-ml-01 | CAD (K3) | crude (K4); S&P 500 on MES (K1) | 1 (48 in screening accounting) | CAD eps_X | [max(S_CAD, S_crude, 2020-02-03), 2024-02-29] | none |
| **K8 total** | | | **5** if D2 admits gold, CAD and the Nasdaq-100 (2a_G + 2a_C + a_N in general) | | | |

**Notes:**
- Cumulative program N was 58 before Stage E. K8 adds its trials at confirmation.
- K8's Holm family (D5) contains the members that pass the K8 screening session's screen, plus
  K8-ml-01.
- Each member is stated under K8 only (NULL_CRITERIA_E section 8).

---

## 6. Questions for the lead

1. **Signal-leg windows and MES's start rule.** MES's own start rule gave S = 2020-02-03. Applied as
   the MES leg's window under D4, it cuts about nine months off K8-flight-01's and K8-ml-01's
   confirmation windows. MES bars for 2019-05..2020-01 are owned; the start rule dropped them because
   MES volume was thin in its first months. For a signal leg, bar presence is what matters, and C4's
   missing-bar rule already handles gaps.
   - Does a signal leg's window follow its own start rule, or only the traded leg's?
2. **MBT's short history (K8-wkndbtc-01).** MBT exists from 2021-05-03, and its start rule may move
   S later. The member will likely be "inconclusive by design". CME's full-size bitcoin futures (BTC,
   listed 2017-12) could serve as the signal leg for 2019-05..2021-04, but BTC is not in D13, so a
   quote would be needed.
   - Quote BTC, or accept the short window?
3. **Signal-leg roll blackouts (C5).** This catalog excludes only the traded leg's roll-blackout
   dates. For signal legs it relies on the one-instrument_id rule within each computation.
   - Keep this, or require the union of all legs' blackouts? The union would cost crude's monthly
     blackouts, about 3 dates a month, from K8-oilcad-01 and K8-ml-01.
4. **Signal-leg coverage (C13).** This catalog proposes a signal-leg coverage check: exclude before
   screening if fewer than 95% of decision times have all signal bars. D9's check is defined for the
   traded vehicle only.
   - Confirm or amend.
5. **Does the WPSR "concern" 6C?** D8 counts a release as concerning a product when any catalog
   member trading that product names it. By that wording, K8-ml-01's naming of the WPSR would give
   every 6C trial the WPSR event-window cost and the D9.5a guard on Wednesdays 09:30-10:00, K3's
   ports on 6C included.
   - Apply it program-wide (conservative, one cost model per product), or to K8's members only?
6. **C6's skip rule.** For entries whose fill would land in a D9.5a guarded interval, this catalog
   skips the entry instead of deferring it, because K8 signals are measured before the release.
   - Confirm that a member may adopt this rule, which is stricter than the harness default.
7. **FOMC-surprise routings (X-13).** The K3, K4 and K5 catalogs routed these after the K8 log
   closed. They need CBOT fed funds futures bars, which are not in D13.
   - Close them, or schedule a later K8 pass with a quote?
8. **F09 ownership (K3-001, Melvin and Prins).** This catalog records it as covered by
   K3-mehedge-01. The ownership decision is yours.
9. **K8-wkndbtc-01's choices.** The member trades the Nasdaq-100 only and takes the symmetric sign
   (X-11).
   - Add RTY and YM (+1 trial each)? Use the short-only reading?
10. **Items the K8 log leaves to the lead (unchanged):**
    - R-K8-045: Dobrev and Schaumburg, "High-frequency cross-market trading", not found.
    - R-K8-048: Iwanaga and Sakemoto (2026), K1's region, not in the registry.
    - R-K8-058: Geman and Li (2018), K4's region, not in the registry.
    - R-K8-071: Bu (2021), K4's region, not in the registry.
11. **The 24/7 regime (K8-wkndbtc-01).** The confirmation window lies entirely in the weekend-closure
    regime. Deployment would lie entirely in the continuous regime (from 2026-05-29). The signal's
    definition is unchanged, and the equity futures still close at weekends, so the rule stays
    deployable. But the Friday-to-Sunday MBT move changes from a closed-market gap to a traded return.
    - Say whether a confirmation result on the old regime is acceptable for this member.
12. **Judgment parameters.** These rest on abstract-level or threshold-free evidence:
    - K8-flight-01's 0.5% tail, 20-date lookback and 30-minute exit;
    - K8-oilcad-01's 2.0-sigma cut and 15-minute hold;
    - K8-wkndbtc-01's clock points (Friday 14:59, Sunday 17:59).

    If you prefer other fixed values, they must be set before hashing. None of these values came from
    data.
