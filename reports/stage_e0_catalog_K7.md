# Stage E.0 hypothesis catalog, cluster K7 (crypto: MBT traded; MET as a signal leg only)

Writer: CatalogWriter-K7-OpusXHigh (Stage E.0 Task 4), 2026-09-24, from 01:41 PDT.
Status: DRAFT declaration for the lead. Nothing here is hashed, frozen or registered.

**What this catalog was written from.** It was written before any price, bar, tick or order-book data
for any product (MBT, MET, BTC, spot bitcoin, ETFs) existed on this machine. It uses only these
product-specific numbers:
- contract specifications and public ADV (reports/stage_e0_liquidity.json);
- Topstep's published fees, hours and release table (reports/stage_e0_topstep_facts.md);
- calendar metadata: MBT contract terms, UK and US holiday lists, BLS release dates, FOMC dates, time
  zones.

No price level, range or volatility of any product is used or assumed anywhere below. The arithmetic
in ticks and dollars (C11) uses only tick values, fees and the design's $85 bar.

**Inputs read in full:**
- reports/stage_e0_research_K7.md (sections 0 to 5).
- `[K7]`-tagged passages in the other logs: none exist. `grep -n '\[K7\]' reports/stage_e0_research_K*.md`
  finds only the K7 log's own header sentence. The K8 log's rows F35 to F46 are K8's dispositions of
  K7's flags, not `[K7]` passages (section 4).
- reports/stage_e0_source_registry.jsonl (the 43 K7 lines, and K8-004, which is tagged K7).
- docs/STAGE_E_DESIGN.md D1 to D15, with the 21:12 and 21:52 amendments; the lead rulings in
  reports/stage_e0_STATE.md (21:12, 21:52, 21:55, and the 01:40 note that event windows are
  half-open, [release, release + 30 min)).
- reports/stage_e0_partition.md; reports/stage_e0_topstep_facts.md (F1 to F12);
  reports/stage_e0_liquidity.json (MBT and MET rows); reports/stage_e0_symbology.json (MBT.v.0).
- reports/stage_d1f_confirmation_list.md 2.1 A3; strategy/research/b_reference_breakout/
  h1_friction_aware_opening_range_breakout.py (the exit count of CP2); docs/SCREENING.md (roll
  blackout = "The splice trade date plus the 2 sessions before it").
- reports/stage_e0_catalog_K4.md, reports/stage_e0_catalog_K3.md, and reports/stage_e0_catalog_K2.md
  C9 (EC-FOMC and EC-NFP sources, reused), for format only.

**Official pages fetched in this task** (curl, 2026-09-24 01:44-01:52 PDT). Files are saved under the
scratchpad `fetch/` folder with the prefix `k7cw_`, never in the repository. They were fetched only to
confirm session times, methodology and data-source availability. No mechanism research was done.
- Wayback CDX listing of cmegroup.com/media-room/press-releases/2026/* (92 captures). It lists the two
  releases below.
- CME Group press release, 19 Feb 2026, "CME Group to launch 24/7 cryptocurrency futures and options
  trading on May 29" (Wayback capture 20260219141120 of
  https://www.cmegroup.com/media-room/press-releases/2026/2/19/cme_group_to_launch247cryptocurrencyfuturesandoptionstradingonma.html).
  Verbatim quotes:
  - "Beginning Friday, May 29 at 4:00 p.m. CT, CME Group Cryptocurrency futures and options will
    trade continuously on CME Globex with at least a two-hour weekly maintenance period over the
    weekend."
  - "All holiday or weekend trading from Friday evening through Sunday evening will have a trade date
    of the following business day, with clearing, settlement and regulatory reporting processed the
    following business day as well."
- CME Group press release, 1 June 2026 (Wayback capture 20260602010915 of
  https://www.cmegroup.com/media-room/press-releases/2026/6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html).
  Verbatim: "today announced it launched 24/7 trading for Cryptocurrency futures and options. The
  expanded trading hours, which went live on Friday, May 29, ..."
- https://www.cfbenchmarks.com/data/indices/BRR (HTTP 200). Verbatim: "If you require access to real
  time or historic data for this index to power a product or service or are interested in licensing the
  index for the creation of a financial product, investment fund or derivative instrument please
  contact". No free historical download is offered on the page.
- https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproductcandles (HTTP 200).
  Documentation only; no candle was requested. Verbatim:
  - "Historic rates for a product."
  - granularity "{60, 300, 900, 3600, 21600, 86400}"
  - "The maximum number of data points for a single request is 300 candles."
  - "time bucket start time".
- BLS release archives https://www.bls.gov/bls/news-release/cpi.htm and .../ppi.htm return HTTP 403
  to curl. The Wayback captures 20260830144214 (CPI) and 20260821235014 (PPI) list 326 CPI and 327 PPI
  release files, named by date. 14 of each fall inside the research window, including the irregular
  2025 dates (for example CPI 2025-10-24 and PPI 2025-11-25).

**Read from the shared scratchpad, not fetched by this writer:**
- gov_uk_bank_holidays.json, England and Wales, 2019-2028 (fetched by CatalogWriter-K3).
- blasco.pdf, the K7 reader's copy of K7-005. It was re-read only to trace the length of the expiry
  window. Its method section says: "The first one, D1, takes a value of 1 at the hour of the expiration
  and 0 otherwise. Subsequently D2 takes a value of 1 both at the hour of expiration and 1 h beforehand
  and 0 otherwise".

**Time-zone conversions** were computed locally with Python zoneinfo (the IANA tz database).

---

## 0. Header

| Item | Value |
|---|---|
| Products | MBT (CME Micro Bitcoin, 0.10 bitcoin, CME rulebook chapter 348 per the liquidity JSON). Topstep lists it as "Micro Bitcoin (MBT)*" inside "CME Equity Futures" (F1). MET (Micro Ether) is on the permitted list but out of the traded universe |
| Traded exposure | **bitcoin {MBT}**, the only K7 exposure left after D1. MBT is its only admissible contract: 2026 Jan-Aug ADV 69,615, coverage 0.996 (D1 table) |
| D1 | **D1 applied: MET out** (day-session coverage 0.947 < 0.95; ADV 61,082 passes). MET may appear only as a signal leg that passes D9's member-level coverage check. **No member in this catalog reads MET** (K7-ml-01 explains why) |
| D2 | Vehicle "D2 (chosen in E.2)". The only candidate is MBT at q = 1 (the 1-lot-equivalent cap; Topstep "Micro Bitcoin (MBT): Capped at mini-equivalent lot sizes, not standard micro scaling", F5.4). Bitcoin is traded only if MBT's rho = r_MBT / R* <= 2.0 at q = 1 (measured in E.2). If rho > 2.0, no K7 member trades |
| Members | **7 = 3 new + 3 core ports + 1 ML member.** The budget is 15, so 8 slots are unused (section 3). The cluster is thin, and nothing is padded |
| Trials in N (confirmation) | **7** if D2 admits bitcoin (3 port + 3 new + 1 ML); 0 otherwise |
| ML grid | 48 configurations, counted only in the K7 screening session's research-window accounting (D15.8) |
| Starred product | **MBT\*** (F1.9). Its referent is Topstep's "Risk Adjustments: High Risk/High Volatility" page (F12.1). That page bans MBT only in the small Challenge tiers: "In the $3K Challenge, you cannot trade MHG, MET, MBT, or SIL" (the same for the $1.5K Challenge). It sets no MBT restriction for the 50K XFA. The page's volatility caps name energies and metals only, and its CPI-window rules name other products. **For the 50K XFA the star imposes nothing beyond F5.4's mini-equivalent weighting**, so q = 1 MBT = 1 lot-equivalent. Whether a volatility halt of "mini-sized contracts or larger" could reach MBT is [unverified]; that is a deployment question, not a design one |
| 24/7 CME crypto trading | **Verified in this task.** CME's 1 June 2026 release says 24/7 trading "went live on Friday, May 29" (2026-05-29, from 16:00 CT per the 19 Feb release). The K7 log carried this as K7-036, unverified. See the next row and C3 |
| Effect on the windows | **Research window** 2025-04-01..2026-06-19: the program trade dates 2026-06-01..2026-06-19 (15 of about 305, the last three weeks) come after the change. From 2026-05-29 16:00 CT, the MBT data contain weekend bars and weekday 16:00-16:59 CT bars, which did not exist before. Under the program's trade-date convention (C3) none of them belongs to a program trade date, and no K7 member reads them. D2's risk measure (day session) and D8's five cost-sample dates (2025-05-14..2026-04-15) are unaffected. **Confirmation window** (S_X..2024-02-29) and **holdout-2** (2024-04..2025-03) are entirely pre-change. **Forward deployment is entirely post-change**, and TopstepX itself stays closed "Friday close 3:10 PM CT (closed till Sunday at 5:00 PM)" (F4, page read 2026-09-23). A K7 confirmation result therefore describes the pre-change regime (section 7, items 1 to 3) |
| Members that touch the weekend or the Sunday reopen | CME-gap members: **excluded** (X-01, with the brief's reason). CP1's Monday signal and K7-montrend-01 read MBT bars from Sunday 17:00 CT. Each states its definition before and after 2026-05-29; both are identical by the C3 convention |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** Times are America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose
  ts_event (its open) is hh:mm:00 CT (D.1f convention H-8). It closes at hh:mm + 1 min, and its values
  are usable from then on. Eastern times convert to CT by subtracting one hour (the two zones change
  clocks on the same dates). London times are converted per date with zoneinfo. They are not a fixed
  offset, because the UK and US change clocks on different dates.
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (the engine convention of
  D6 and D15). "Market intent on the bar at X" fills at the open of the bar at X + 1 min.
  - **Orders never exceed q.** In the three new members, a change of direction is a flatten followed by
    a new entry, never one 2q order:
    - The flatten intent is emitted on the bar that closes at the decision time and fills at the open
      of the decision-time bar.
    - The entry intent is emitted on the next bar and fills one minute later.
- **C3 Trade date (the program convention, reports/stage_e0_STATE.md).**
  - **Definition:** trade date d = [d-1 17:00 CT, d 16:00 CT). The first bar of trade date d is the
    17:00 CT bar of the previous calendar day (Sunday for a Monday).
  - **Before 2026-05-29:** the definition matches CME's session, with the daily 16:00-17:00 CT break
    and the weekend closure from Friday 16:00 CT to Sunday 17:00 CT (P-K7-033-b; P-K7-002-e).
  - **After 2026-05-29:** CME trades continuously and gives weekend trading "a trade date of the
    following business day" (19 Feb 2026 release). **This catalog keeps the program convention in both
    regimes.** Bars from Friday 16:00 CT to Sunday 17:00 CT, and weekday bars from 16:00 to 16:59 CT,
    belong to no program trade date. No member reads them, and no daily bar includes them.
  - **Consequence:** the first bar of a Monday trade date is the Sunday 17:00 CT bar in both regimes.
    If the lead instead adopts CME's post-change assignment, CP1's Monday signal and the ML member's B2
    on Mondays would start at Friday 16:00 CT and read weekend prices (section 7, item 2).
- **C4 Exclusions for the three new members** (the ports follow D6 as written; the ML member follows
  D15.3). A new member does not trade on:
  - roll-blackout dates (`screen_candidate` with `roll_blackout`: the splice trade date plus the 2
    sessions before it);
  - dates the D10 equity-and-crypto calendar marks as early close or early halt (Family H's "Days with
    early_halt_ct set: no trade");
  - vendor-degraded dates.

  A rule whose required bar is missing, or whose signal bars of one computation carry different
  instrument_ids, treats that signal as 0 (flat). If an exit's named bar is missing, the exit is sent
  on the first later bar, and the engine's forced flatten at F is the backstop. A CME price-limit halt
  shows up as missing bars and is handled the same way.
- **C5 Flat time.** F = 15:08 CT (D9.1). D6 crypto row: O = 08:30, C = 15:00, F = 15:08. MBT itself
  trades until 16:00 CT (before the change) or continuously (after it); TopstepX flattens at 15:10 CT
  (F4). Early-close days: F = the early close minus 15 minutes (D9.1, D9.13).
- **C6 Size.** q = 1 MBT = 1 lot-equivalent (D2 cap; F5.4; D9.6 weight "MBT 1"). This is half the 50K
  XFA's starting 2-lot maximum. No member sizes by signal. At most one position.
- **C7 Tick, fees, epsilon.** From reports/stage_e0_liquidity.json (CME MBT specification page,
  fetched 2026-09-23 20:51 PDT):
  - tick "5.00 (USD per bitcoin)", "$0.50 per contract";
  - contract unit "0.10 bitcoin";
  - listed 2021-05-03.

  Topstep's round turn is $2.82 (F3), which is 5.64 ticks.

  D3's translated bar: eps_bitcoin = floor(85.00 / (1 x 0.50)) = **170 net ticks per contract per
  day**. The operative eps is min(translated, funnel-derived), set in E.2 (D3). E.2 confirms the tick
  was unchanged from 2021-05 to 2026-06 before any bar is read (CP2's buffer and the ML features are in
  ticks).
- **C8 Price data.**
  - **Source:** Databento GLBX.MDP3 ohlcv-1m of MBT. It is paid. D13 quotes K7 at $1.49 (research
    window) + $3.11 (2019-05..2025-03 history) + $1.20 (mbp-1 sample).
  - **History:** the quotes for months before 2021-04 failed with "None of the symbols could be
    resolved" (D13), so MBT history starts at its 2021-05-03 listing.
  - **Continuous series:** MBT.v.0 (volume roll; 62 roll intervals over 2019-05..2026-06 in
    reports/stage_e0_symbology.json, that is, monthly from 2021).
  - **Availability:** a bar is available at its close (C1).
  - **No sealed data is read.** A lookback that would reach a sealed trade date (holdout-2 ends on
    trade date 2025-03-31) counts as missing, so a rule that needs d-1 does not trade on the first
    research trade date.
  - **Expiring contract:** no member holds an expiring MBT contract on its last trading day. If the
    continuous series still holds the expiring month on its final trading day, the splice must fall on
    the next trade date at the latest. The roll blackout (splice date plus the 2 sessions before it)
    then covers that final trading day.
- **C9 Calendars.** All are free, and every rule reads them only as dates and clock times.
  - **EC-CAL.** The D10 equity-and-crypto calendar (trade dates, holidays, early closes and halts),
    built by E.2 from CME schedules. It needs a crypto note for dates after 2026-05-29 (section 7,
    item 1).
  - **EC-MBTX, MBT final trading days and T_exp.**
    - **Rule:** "Trading terminates at 4:00 p.m. London time on the last Friday of the contract month.
      If that day is not a business day in both the U.K. and the U.S., trading terminates on the
      preceding day that is a business day for both the U.K. and the U.S." (P-K7-033-c). Final
      settlement: "the CME CF Bitcoin Reference Rate (BRR) at 4:00 p.m. London time on the expiration
      day" (P-K7-033-d).
    - **T_exp(d):** 16:00 Europe/London on d, converted to CT with zoneinfo. It is normally 10:00 CT,
      and 11:00 CT in the weeks when UK and US clocks differ.
    - **Dates by the rule** (computed here from the gov.uk list and US federal holidays plus Good
      Friday; E.2 confirms each against CME's published MBT contract calendar):
      - Research window, 14 dates: 2025-04-25, 05-30, 06-27, 07-25, 08-29, 09-26, 10-31 (T_exp 11:00
        CT), 11-28, 12-24 (a Wednesday: 26 December is a UK holiday and 25 December a holiday in
        both), 2026-01-30, 02-27, 03-27 (T_exp 11:00 CT), 04-24, 05-29.
      - Confirmation window (2021-05-03..2024-02-29), 34 dates: 2021-05-28 to 2024-02-23, including
        2021-12-30 (a Thursday) and 2022-03-25 (T_exp 11:00 CT).
    - **Availability:** contract terms known in advance.
  - **EC-FOMC.** Scheduled FOMC statement days, reused from reports/stage_e0_catalog_K2.md C9:
    - source https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm plus the historical
      pages;
    - regularly scheduled meetings only;
    - statement at 13:00 CT (Topstep F6 "FOMC Statement | 1:00 PM | All products"; P-K7-029-b
      "14:00 (New York time)");
    - published before each year.
  - **EC-NFP.** BLS Employment Situation release dates (K2 C9: https://www.bls.gov/bls/news-release/empsit.htm),
    08:30 ET = 07:30 CT (Topstep F6 "Unemployment Rate | 7:30 AM | ... MBT, MET").
  - **EC-CPI, EC-PPI.** BLS CPI and PPI release dates from the archive pages above (Wayback captures
    fetched here). The standard 08:30 ET time is [not re-confirmed per release in this task]. E.2
    reads each release file's embargo line and drops any release not published at 08:30 ET.
  - **Availability of release dates.** As used in K7-ml-01 KF1, a release's occurrence on d is known
    at its publication time, 07:30 CT, which is before any K7 decision that reads it.
- **C10 Spot, reference-rate and flow data: none is read by any member.**
  - **BRR and BRRNY values:** historical data require a licence (CF Benchmarks page above), so they
    are not free. The obtainable proxy for the final-settlement price is MBT's own bars, which is what
    K7-expiry-01 trades.
  - **Spot bitcoin minute data:** free through Coinbase's public candles endpoint (1-minute buckets,
    300 per request). How far back 1-minute history goes was not checked in this task.
  - **Offshore perpetual data** (Huobi, OKEx, BitMEX in K7-002): not checked.
  - **Spot-ETF daily flows:** the publication times are unverified (X-03).
- **C11 Frequency and the eps multiple (arithmetic from calendar counts and C7; no price data).**
  - **Size of the windows:** the research window has 319 weekdays (about 305 CME trade dates) and 63
    Mondays. The confirmation window, from MBT's listing, has 739 weekdays and 148 Mondays.
  - **The multiple:** a member that trades on k of about 305 research dates, with zeros on the others
    (D5), needs a net P&L per trading day of about (305 / k) x 170 ticks to reach eps.
    - K7-expiry-01 (k about 12): about 25 x eps per event, about 4,300 ticks, about $2,150 on one MBT.
    - K7-montrend-01 (k about 55): about 5.5 x eps per Monday.

    Both are likely to end "null at eps" or "inconclusive by design" (D4). That is a structural
    outcome (section 7, item 6).
- **C12 Coverage.** D1's coverage figure (0.996) was measured only inside 08:30-15:00 CT on the five
  calibration dates. K7-expiry-01 (from 05:00 or 06:00 CT) and K7-montrend-01 (Sunday 17:00 CT to
  Monday 14:00 CT) trade outside that window, so each depends on E.2's member-level coverage check
  (>= 0.95 in its own window, D9). No fallback window is written (section 7, item 5).
- **C13 Price-limit proximity (D9.7).** MBT carries CME price fluctuation limits. The FAQ describes a

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-10: the "release residual" paragraph of C13 is superseded: since the 01:52 ruling the D9.7 exit is exempt from the fill guard (D9.7).]
  dynamic variant "applied in rolling 60-minute look-back periods to establish dynamic lower and upper
  price fluctuation limits" (P-K7-033-e). E.2 reads the MBT rulebook chapter and builds the limit
  table. The liquidity JSON says chapter 348; the K7 log's R-K7-061 looked for "chapter 350".
  Encoded as D9.7: no entry, and an immediate exit, while the price is within 2% of a limit price.
  This catalog assumes no limit is hit.
- **C14 Release minutes and event-window cost.**
  - **Releases concerning MBT:**
    - Topstep's table: the Employment Situation at 07:30 CT and the FOMC statement at 13:00 CT (F6).
    - Named by this catalog's members: CPI and PPI at 07:30 CT (K7-ml-01 KF1).
  - **D8 event-window cost:** fills in [07:30, 08:00) on those release days and in [13:00, 13:30) on
    FOMC days pay the largest bucket (half-open per the 01:40 ruling).
  - **D9.5a guard:** no fill in [release, release + 2 min).
  - **Which members are exposed:** only CP2 can fill inside such a window. Every other member's fill
    times avoid them by construction, as each entry states.

---

## 1. Members

### K7-cp1-01 (core port CP1, intraday momentum)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-02: this entry's statement that the family was null on MES is corrected. MES's confirmation tested the reversal-signed F3.3 statistics (s = -1, reports/stage_d1f_confirmation_list.md) and found them null; the momentum form ported here, the literature's form, was negative on MES's mined window and is untested on MES's confirmation. The port is kept; D6 carries the corrected wording.]
- **Cluster** K7.
  - **Products read:** MBT only.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits the exposure.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES Family F3.3(a), the Gao-Han-Li-Zhou / Baltussen form (class C3; D.1 log A10
  and A28), as fixed in D6 row CP1.
  - **D6 rule text, verbatim:** "Signal: sign of (close of the bar at O+29 min minus open of the trade
    date's first bar). Entry: market intent on the bar at C-31 min (fills at the C-30 open), in the
    signal's direction; zero signal, no trade. Exit: market intent on the first bar at or after C-2 min
    (fills at the next open). Both signal bars must exist with one instrument_id, else no trade."
  - **K7 log, recorded as covered by CP1:**
    - K7-011, Shen, Urquhart and Wang, on spot bitcoin: the return from the previous day's close,
      "when the 60-minute break of CME Bitcoin futures trading begins at 5pm EST" (P-K7-011-a), to 30
      minutes after the exchange open "significantly predicts the last half hour with a slope of
      0.968" (P-K7-011-b). This is the same mechanism.
    - The paper's predicted half hour ends at 16:00 CT, after F, so CP1 tests the in-session analogue,
      which the paper did not test.
    - Evidence against it in the same paper: the 10am-4pm re-test is "a lot smaller in magnitude and
      statistical significance" (P-K7-011-e), and breakeven costs are 3 to 10 bps (P-K7-011-d).
    - The momentum half of K7-018 (P-K7-018-a, -c; abstract only) is in the same family.
- **Instantiated with the crypto row (O = 08:30, C = 15:00, F = 15:08):**
  - **Signal:** close of the bar at 08:59 minus the open of the trade date's first bar, which is the
    17:00 CT bar of d-1 (C3).
  - **Entry:** market intent on the bar at 14:29, filling at the 14:30 open, in the signal's
    direction. A zero signal means no trade.
  - **Exit:** market intent on the first bar at or after 14:58, filling nominally at the 14:59 open.
    14:59 is the first second of MBT's daily-settlement minute: "VWAP of CME Globex trades between
    3:59:00 p.m. and 4:00:00 p.m. Eastern Time" (P-K7-033-a).
  - **Holding horizon:** 29 minutes. **Session window:** 14:30-14:59 CT. Flat 9 minutes before F.
  - **Context only:** the holding period lies inside the BRRNY hour, 14:00-15:00 CT, in which "more
    than 20% of a day's notional volume is transacted" (P-K7-038-a).
- **Before and after 2026-05-29 (Monday trade dates):**
  - **Before:** the first bar is the 17:00 CT Sunday reopen bar. The signal starts at that bar's open,
    so the Friday-to-Sunday gap is never part of it.
  - **After:** by C3 the first bar is still the Sunday 17:00 CT bar, now an ordinary bar of continuous
    trading. Weekend bars are not read.
  - **Tuesday to Friday:** unchanged in both regimes (after the change, the 16:00-16:59 CT bars of
    d-1 are not read).
- **Data fields read:** MBT ohlcv-1m open, close and instrument_id (C8). Paid; history from 2021-05-03.
  The first bar is available at 17:01 CT on d-1, and the 08:59 bar at 09:00 CT.
- **Order type:** market. **Sizing:** q = 1 MBT (C6).
- **Parameters:** O+29 min = the 08:59 bar, C-31 min = the 14:29 bar, C-2 min = the 14:58 bar (D6).
  **Grid:** none.
- **Expected entries and hold:** at most 1 entry per trade date, held 29 minutes. Floor: <= 20
  entries, ok; 2-minute minimum hold, ok; 10-minute mean, ok.
- **Falsification:** the standard condition only (a port; D6 unchanged). UCB95 of the member's mean net
  daily P&L per contract below eps_bitcoin, at >= 80% achieved null power on the confirmation window,
  counts against it.
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: one trade a day; no stops, brackets or passive fills. Neither fill is at a reopen or
     release minute, so this is not a gapped-market fill.
  4. Star: MBT\*; nothing applies to the 50K XFA beyond F5.4 (header).
  5. News: 1 lot-equivalent, not the full maximum. No release falls in 14:30-14:59.
  6. D9.5a guard: no fill in a release minute. The FOMC statement at 13:00 CT is before the entry.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.
- **Data needed:** MBT ohlcv-1m, research window 2025-04-01..2026-06-19 and confirmation S_X..2024-02-29
  (S_X >= 2021-05-03, D4). No external data.
- **Trials in N:** 1.

### K7-cp2-01 (core port CP2, opening-range breakout)
- **Cluster** K7.
  - **Products read:** MBT only.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES B-H1 hold 75 (class C2;
  strategy/research/b_reference_breakout/h1_friction_aware_opening_range_breakout.py, hold_minutes =
  75), as fixed in D6 row CP2 with the 21:12 amendment and the 21:52 buffer ruling.
  - **D6 rule text, verbatim:** "OR = high and low of the bars in [O, O+15 min). Entry: the first bar
    opening in [O+15, C) whose close is beyond OR_high or OR_low by at least 4 ticks of P; market
    intent in the break direction; one entry per trade date; no entry from C on. Exit: 75 minutes after
    the fill, or the engine's forced flatten at F if earlier."
  - **K7 log:** K7-022 (Deprez and Frömmel) tests channel-breakout and support-resistance rules among
    75,360 rules on Bitstamp bitcoin (P-K7-022-a). The breakout family on bitcoin is therefore
    **covered by CP2**, with a negative prior:
    - "only 1.68% of the trading rules, on average, outperformed the benchmark in terms of mean excess
      return" (P-K7-022-d);
    - the best portfolios are "not statistically significant" (P-K7-022-b).

    No crypto-specific opening-range source was found (R-K7-053: Fetna's ORB panel is K4-050, with no
    crypto).
- **Instantiated:**
  - **Opening range:** high and low of the bars opening in [08:30, 08:45). Context: this is the
    window of the post-ETF opening volatility spike (P-K7-014-a).
  - **Eligible bars:** those opening in [08:45, 15:00). No entry from 15:00 CT on.
  - **Buffer:** 4 ticks of MBT, the exposure's most active and only contract (D6 ruling of 21:52).
    That is 20.00 in price units (USD per bitcoin), $2.00 per contract.
  - **Entry:** the first eligible bar whose close is >= OR_high + 20.00 buys; the first whose close
    is <= OR_low - 20.00 sells. The intent fills at the next open. One entry per trade date.
  - **Exit:** 75 minutes after the fill, counted as the MES module counts it: the exit intent is
    emitted on the 75th bar after the entry-intent bar and fills at the next open. The engine's forced
    flatten at F = 15:08 applies to fills after 13:53. As in MES's D.1 run, a late break (latest fill
    15:00) is held at most 8 minutes.
  - **Holding horizon:** 75 minutes, less when F binds. **Session window:** 08:46-15:08 CT.
- **Before and after 2026-05-29:** unaffected (it reads only the day session).
- **Data fields read:** MBT ohlcv-1m high, low, close and instrument_id (C8). The range is known at
  08:45 CT.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:** OR 15 minutes, buffer 4 ticks (20.00), hold 75 minutes (D6, a literal port).
  **Grid:** none.
- **Expected entries and hold:** at most 1 per day. The hold is 75 minutes, or 8 to 75 minutes when F
  binds. Floor: ok, since the minimum hold of 8 minutes is >= 2. The 10-minute mean is checked at
  screening.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: forced flatten at 15:08 at the latest.
  2. Order type: market.
  3. D9.4: one trade a day; no stops.
  4. Star: as CP1.
  5. News: 1 lot-equivalent. A position may be open at the 13:00 FOMC statement, which F6.3 allows
     below full maximum size.
  6. D9.5a guard: an entry whose fill would land in [13:00, 13:02) on an FOMC day fills at the 13:02
     open. Fills in [13:00, 13:30) pay D8's event-window cost (C14).
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.
- **Data needed:** MBT ohlcv-1m, research and confirmation windows.
- **Trials in N:** 1.

### K7-cp3-01 (core port CP3, prior-close location)
- **Cluster** K7.
  - **Products read:** MBT only.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of MES H6 (class C7; reports/stage_d1f_confirmation_list.md 2.1 A3 row H6), as
  fixed in D6 row CP3.
  - **D6 rule text, verbatim:** "Daily bar of day d from [O, C): O_d = open of the O bar, H and L over
    [O, C), C_d = close of the bar at C-1 min; complete-day and instrument-guard rules as Family H.
    CLV = (C_d - L_d)/(H_d - L_d) of d-1, range > 0; CLV >= 0.8 buys, CLV <= 0.2 sells, market intent
    on the O bar of day d. Exit: first bar at or after C-2 min."
  - **K7 log:** no crypto-specific prior-close-location source. The daily-bar constructions in the log
    are of other kinds:
    - K7-040's MAX(10), an overnight hold;
    - K7-041's N-day high around holidays, close-to-close.

    Both are infeasible (section 2). No K7 item is covered by CP3.
- **Instantiated:**
  - **Daily bar:** O_d is the open of the 08:30 bar. H and L are taken over the bars opening in
    [08:30, 15:00). C_d is the close of the 14:59 bar (the settlement-minute bar, P-K7-033-a).
  - **Complete day:** the 08:30 and 14:59 bars exist, the date is not an early halt, and all its bars
    in [08:30, 15:00) carry one instrument_id.
  - **Instrument guard:** d-1's bar carries the instrument_id of day d's 08:30 bar.
  - **d-1:** the previous complete trade date in EC-CAL. For a Monday that is Friday's bar in both
    regimes, since no weekend bar enters any daily bar (C3).
  - **CLV:** computed with Range[d-1] > 0. CLV >= 0.8 buys, CLV <= 0.2 sells (non-strict, as H6).
  - **Entry:** market intent on the 08:30 bar of d, filling at the 08:31 open.
  - **Exit:** market intent on the first bar at or after 14:58, filling nominally at the 14:59 open.
  - **Holding horizon:** about 388 minutes. **Session window:** 08:31-14:59 CT.
- **Data fields read:** MBT ohlcv-1m open, high, low, close and instrument_id (C8). Day d-1's bar is
  complete at 15:00 CT on d-1.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:** CLV cuts 0.2 and 0.8; lookback 1 complete bar (D6 and H6). **Grid:** none.
- **Expected entries and hold:** at most 1 per day, held about 388 minutes. Floor ok.
- **Falsification:** the standard condition only (port).
- **Topstep check:**
  1. Flat by F: last fill 14:59.
  2. Order type: market.
  3. D9.4: ok.
  4. Star: as CP1.
  5. News: the position holds through FOMC statements at 1 lot-equivalent, not the full maximum
     (D9.5). The 07:30 releases come before the entry.
  6. D9.5a guard: the fills at 08:31 and 14:59 are not in any release minute.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.
- **Data needed:** MBT ohlcv-1m, research and confirmation windows.
- **Trials in N:** 1.

### K7-expiry-01 (long MBT in the five hours before the BRR final-settlement time on MBT's last trading day)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source covers 2017-12 to 2020-11, overlapping MBT's confirmation window where MBT exists.]
- **Cluster** K7.
  - **Products read:** MBT; EC-MBTX; EC-CAL.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism.** New to the program. Settlement-window and expiry effects are the product's cluster's
  (partition section 4). It is also a family E calendar event with an hourly horizon.
  - **The evidence:** around the CME bitcoin futures expiry, spot bitcoin shows abnormal positive
    returns in the hours before expiry. "a clear effect on prices at the maturity time and 5 h prior to
    the expiration time in all the exchanges under analysis. Returns are significantly higher than the
    mean return at the 1% significance level" (P-K7-005-b).
  - **The authors' attribution:** "Typically, this effect is attributed to the unwinding of short
    arbitrage positions" (P-K7-005-c).
  - **The clock:** final settlement is the BRR at 4:00 p.m. London (P-K7-005-a, P-K7-033-d). The BRR is
    the equal-weighted average of twelve 5-minute volume-weighted medians of constituent spot trades
    from 3:00 to 4:00 p.m. London (P-K7-019-a, -b). The BRR window "sees the greatest number of
    transactions" (P-K7-032-b).
  - **Transfer to MBT (reasoned, untested):** MBT is priced off the same spot market and absorbs spot
    moves within minutes at most. CME absorbed shocks "between 4 and 5 minutes" in 2019-2020
    (P-K7-002-b), and MBT led Binance by fractions of a second in 2024 (P-K7-025-b). A spot move over a
    five-hour window therefore appears in MBT's price. On a traded expiry day the vehicle holds the
    next month's contract (C8), which tracks spot plus a basis. That basis changes slowly relative to
    a five-hour move (a judgment).
- **Conflicting evidence, stated in advance:**
  - **Sign:** K7-004 (daily spot bars cut at 00:00 UTC) finds that after the October 2021 BITO launch
    "the pattern in the daily returns after the BITO ETF introduction (2021-2024) is reversed,
    especially on days preceding the expiration and on the expiration day itself" (P-K7-004-b). MBT's
    whole history (from 2021-05) falls in that later period. K7-005's own sample is 2017-12..2020-11
    (P-K7-005-e): pre-MBT and pre-spot-ETF.
  - **Last hour:** the pooled robustness finds the effect "about 5 h before expiration, although not
    in the last hour" (P-K7-005-d). The per-exchange result says "The strongest effect is reflected in
    D2 and D1" (P-K7-005-b).
  - **Multiplicity:** "we have finally run 576 models" (log, K7-005 quality tells).
  - **Other exchanges' expiries:** CBOE expiries show "scarce" effects (P-K7-005-f).
- **Rule:**
  - **Dates:** each EC-MBTX final trading day d that is a full trade date (C4).
  - **Clock:** T_exp(d) = 16:00 Europe/London on d, in CT (C9): 10:00 CT normally, 11:00 CT in the
    weeks when UK and US clocks differ.
  - **Entry:** market intent BUY on the bar at T_exp - 301 min, filling at the open of the bar at
    T_exp - 300 min (05:00 CT, or 06:00 CT).
  - **Exit:** market intent on the bar at T_exp - 2 min, filling at the open of the bar at T_exp - 1
    min (09:59 CT, or 10:59 CT).
  - **Holding horizon:** 299 minutes. **Session window:** 05:00-09:59 CT (06:00-10:59 CT in
    mismatch weeks). Flat hours before F.
- **Before and after 2026-05-29:** unaffected. The rule reads no weekend or reopen bar. 2026-05-29
  is both an EC-MBTX date and the day 24/7 trading began, but the change started at 16:00 CT, after
  the window. The BRR method is in version 17.4, dated 24 August 2026 (P-K7-019-d).
- **Data fields read:**
  - **MBT ohlcv-1m open and instrument_id (C8):** paid; history from 2021-05-03. The bars are
    available at their close.
  - **EC-MBTX:** the rule text P-K7-033-c, plus the gov.uk England-and-Wales holidays (free,
    2019-2028) and US holidays (EC-CAL). Known in advance.
  - **Time zones:** tz database, free. Known in advance.

  The rule reads **no BRR value** (licensed, C10) and no spot data.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:**
  - **Direction long:** P-K7-005-b, -c.
  - **Window start at T_exp - 300 min:** "5 h prior" (P-K7-005-b); "about 5 h before expiration"
    (P-K7-005-d). The paper's cumulative dummy D5 covers "the hour of expiration" and the 4 hours
    before (its method section, quoted in the preamble). This catalog reads that as [T_exp - 5 h,
    T_exp]. The paper's hour-labelling convention is not stated in the text read [unverified].
  - **Exit at T_exp - 1 min (a judgment):** it keeps the whole position inside the documented window
    and off the settlement instant. The last hour is kept despite P-K7-005-d, because the per-exchange
    result puts the strongest effect there (P-K7-005-b).

  **Grid:** none.
- **Expected entries and hold:**
  - **Research window:** 1 entry per surviving EC-MBTX date, out of 14 dates. 2025-11-28 and
    2025-12-24 are likely D10 early-close dates [E.2 confirms], which leaves about 12, less any
    roll-blackout dates.
  - **Confirmation window:** 34 dates, less early closes and roll blackouts.
  - **Hold:** 299 minutes. Floor ok.
  - **Roll blackout:** an expiry day survives the blackout only if the MBT.v.0 splice came on or
    before the Thursday of that week (C8). E.2 reports how many survive. If none survive, the member
    has no trade dates, and the lead decides before screening (section 7, item 8).
  - **Frequency:** about 25 x eps per event (C11).
- **Falsification:** the standard condition. No member-specific check. The competing sign from K7-004
  is recorded above, before any data.
- **Topstep check:**
  1. Flat by F: last fill 09:59 CT (10:59 CT).
  2. Order type: market.
  3. D9.4: one trade per event day. The entry is not at a reopen, a gap or a release minute. The exit
     is before the BRR window closes. No stops.
  4. Star: as CP1.
  5. News: the position may hold through a 07:30 CT release on d at 1 lot-equivalent (allowed; F6.3
     bars only full maximum size).
  6. D9.5a guard: no fill in [07:30, 07:32) or [13:00, 13:02). No fill in a C14 event window.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.
- **Data needed:**
  - MBT ohlcv-1m, research and confirmation windows. The member-level coverage check covers
    [T_exp - 300 min, T_exp - 1 min] on EC-MBTX dates, which lies outside D1's measured window (C12).
  - Calendars EC-MBTX and EC-CAL.
- **Trials in N:** 1.

### K7-rev2h-01 (two-hour reversal in the MBT day session)
- **Cluster** K7.
  - **Products read:** MBT; EC-CAL.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of D.1 family C (short-horizon reversal) at family G's coarser bars. The
  evidence is bitcoin-specific (partition rule 6). D6's core set does not port family C, so this is
  not covered by a port.
  - **The evidence:** spot bitcoin returns show significant negative first-order autocorrelation at
    1-, 2- and 4-hour horizons, beyond what microstructure explains: "significant levels of negative
    autocorrelation found for returns calculated on intervals as wide as one, two and even four hours
    cannot usually be attributed to microstructural components" (P-K7-012-a). The values are "1 hour
    -0.0557 ... 2 hours -0.0858 ... 4 hours -0.0564 ... 1 day -0.0071 0.8047" (P-K7-012-b).
  - **The source's rule:** "it bets on the market (goes long) if the last price movement was large and
    negative, and against the market (goes short) if the movement in the last period was large and
    positive. The trade is then closed after a single time unit has passed" (P-K7-012-c). The headline
    run uses 2-hour bars and a zero threshold (P-K7-012-f).
  - **Transfer to MBT (reasoned, untested):** MBT prices spot within minutes at most (P-K7-002-b;
    P-K7-025-b), so a two-hour autocorrelation in spot is present in MBT.
- **Conflicting evidence:**
  - The source sample is 2015-03..2018-06 on one exchange, almost all before CME futures
    (P-K7-012-e), with fees excluded and no out-of-sample test (log quality tells).
  - K7-042's intraday trend-following ensemble earned a gross Sharpe of about 1.6 over 2018-2025
    (P-K7-042-a): the opposite bet. That source also calls US Sunday morning mean-reverting
    (P-K7-042-c).
  - K7-018 finds both momentum and reversal, depending on state (P-K7-018-a, -c).
  - K7-011 finds anti-persistence of the second-to-last half hour (P-K7-011-f), the same sign at 30
    minutes.
  - K7-022's technical rules mostly fail after costs (P-K7-022-b, -d).
- **Rule:**
  - **Blocks:** B1 = [08:30, 10:30), B2 = [10:30, 12:30), B3 = [12:30, 14:30), in CT.
  - **Decision at 10:30:** r1 = close of the 10:29 bar - open of the 08:30 bar. Target = -sign(r1)
    x q; 0 if r1 = 0.
  - **Decision at 12:30:** r2 = close of the 12:29 bar - open of the 10:30 bar. Target = -sign(r2)
    x q.
  - **Orders (C2):**
    - If the target equals the current position, hold.
    - Otherwise, if a position is open, the flatten intent is on the bar at the decision time - 1 min
      (it fills at the decision-time open).
    - If the target is nonzero, the entry intent is on the decision-time bar (it fills one minute
      later, at 10:31 or 12:31).
  - **Final exit:** market intent on the 14:29 bar, filling at the 14:30 open.
  - **Missing data:** a missing endpoint bar or an instrument change between endpoints sets that
    target to 0 (C4).
  - **Holding horizon:** 119 or 120 minutes per block, up to about 239 minutes if the second target
    agrees. **Session window:** 10:31-14:30 CT. Flat 38 minutes before F.
- **Before and after 2026-05-29:** unaffected (day session only).
- **Data fields read:** MBT ohlcv-1m open, close and instrument_id (C8). The latest input is the bar
  closing at the decision time.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:**
  - **Block 120 minutes:** the strongest autocorrelation (P-K7-012-b) and the headline bar size
    (P-K7-012-f).
  - **Threshold 0:** P-K7-012-f.
  - **Hold one block:** P-K7-012-c.
  - **Anchor 08:30 (a judgment):**
    - it is D6's O for crypto and the window where D1 measured coverage at 0.996;
    - it keeps every fill at :30 or :31, off the 13:00 FOMC minute and the 14:59 settlement minute;
    - its third block ends at 14:30, 38 minutes before F.

  **Grid:** none.
- **Expected entries and hold:** at most 2 entries per day (<= 20); each position is held >= 119
  minutes. Floor ok.
- **Falsification:** the standard condition only.
- **Topstep check:**
  1. Flat by F: last fill 14:30.
  2. Order type: market.
  3. D9.4: at most 2 trades a day, 2-hour holds, no stops, no gapped fills.
  4. Star: as CP1.
  5. News: the B3 position spans the 13:00 FOMC statement at 1 lot-equivalent (allowed).
  6. D9.5a guard: the fills at 10:30, 10:31, 12:30, 12:31 and 14:30 are not in any release minute
     or any C14 event window.
  7. Position limit: <= 1 lot-equivalent (the order never exceeds 1, C2).
  8. Price limit: C13.
- **Data needed:** MBT ohlcv-1m, research and confirmation windows.
- **Trials in N:** 1.

### K7-montrend-01 (Sunday-evening trend window: hourly time-series momentum on the Monday trade date)

> [Lead ruling on the Task 6 review, 06:20 PDT 2026-09-24: R-04: labelled SOURCE-OVERLAP. Its source covers 2018-2025, overlapping the confirmation window.]
- **Cluster** K7.
  - **Products read:** MBT; EC-CAL.
  - **Traded exposure:** bitcoin {MBT}, traded only if D2 admits it.
  - **Vehicle:** D2 (chosen in E.2).
- **Mechanism:** port of D.1 family C (intraday trend and momentum), limited to a family A/E clock
  window specific to bitcoin. It is new to the program as an MBT window.
  - **The evidence:** an ensemble of high-frequency trend-following models on bitcoin "delivers
    strongly positive returns starting on Sunday at around 7:00 PM New York time, with performance
    remaining elevated for roughly the next 24 hours into Monday. Notably, this upswing closely aligns
    with the Monday open of Asian cash equity markets" (P-K7-042-b).
  - **Robustness in the source:** the effect "becomes substantially more pronounced in the latter
    subsample" (after mid-2020, P-K7-042-d). The ensemble is long-short and volatility-targeted
    (P-K7-042-e), with a gross Sharpe of about 1.6 (P-K7-042-a).
  - **Feasibility:** Sunday 18:00 CT to Monday 14:00 CT lies inside one TopstepX trading day ("Sunday
    open | 5:00 PM CT", "Weekday close | 3:10 PM CT", F4) and one program trade date (C3). No position
    is held past a daily flatten.
- **Conflicting evidence:**
  - K7-012's negative 1-hour autocorrelation (P-K7-012-b) makes the opposite bet at the same horizon.
  - Concretum's result is gross of fees, and its models and parameters are undisclosed.
  - The Sunday-evening seasonality was found by inspecting a figure, with no test statistic (log
    quality tells).
- **Before and after 2026-05-29.** The rule reads only MBT bars opening at or after Sunday 17:00 CT,
  the first bar of the Monday trade date (C3).
  - **Before the change** (Monday trade dates up to 2026-05-25): the Sunday 17:00 CT bar is CME's
    reopen bar. The first signal (the 17:00-17:59 hour) starts at that bar's open, so the
    Friday-to-Sunday gap is never in a signal. The first fill is at 18:01 CT, one hour after the
    reopen, never at the reopen.
  - **After the change** (from 2026-06-01): the same clock bars are ordinary bars of continuous
    trading. Weekend bars before Sunday 17:00 CT are not read.
  - **Why the mechanism does not depend on CME's weekend closure:** the source attributes the effect
    to the Monday Asian cash open (P-K7-042-b) and measures it on bitcoin itself. The venue is not
    stated in the text read [unverified]; bitcoin itself trades continuously.
  - **The rule is identical in both regimes.** The first hour after a pre-change CME reopen may still
    behave differently from the same hour after the change. The confirmation window is entirely
    pre-change (header; section 7, item 3).
- **Rule:**
  - **Dates:** trade dates d that are Mondays and full trade dates (C4). A Monday holiday with an
    early halt does not trade.
  - **Decision times, 20 of them:** Sunday 18:00, 19:00, 20:00, 21:00, 22:00, 23:00; Monday 00:00,
    01:00, ..., 13:00 (CT).
  - **Signal at each decision time t:** s_t = sign(close of the bar at t - 1 min - open of the bar at
    t - 60 min). If either bar is missing, or the two carry different instrument_ids, then s_t = 0
    (C4).
  - **Orders (C2):**
    - If a position is open and its sign differs from s_t (including s_t = 0), a flatten intent on
      the bar at t - 1 min fills at the open of the bar at t.
    - If s_t is nonzero and the position is then flat, an entry intent in direction s_t on the bar at
      t fills at the open of the bar at t + 1 min.
    - If s_t equals the open position's sign, hold.
  - **Final exit:** market intent on Monday's 13:59 bar, filling at the 14:00 open.
  - **Holding horizon:** each position is held from an entry at t + 1 min to at least the next
    decision (>= 59 minutes). **Session window:** Sunday 18:01 CT to Monday 14:00 CT. Flat 68 minutes
    before F.
- **Data fields read:** MBT ohlcv-1m open, close and instrument_id (C8). The inputs are available at
  the close of the bar at t - 1 min.
- **Order type:** market. **Sizing:** q = 1.
- **Parameters:**
  - **Start at Sunday 18:00 CT:** "Sunday at around 7:00 PM New York time" (P-K7-042-b); 19:00 ET =
    18:00 CT in all weeks (C1).
  - **Last decision Monday 13:00 CT, flat at 14:00 CT (a judgment):** F = 15:08 cuts the source's
    roughly 24-hour window, and 20 decisions is D9.3(a)'s maximum of 20 entries a day.
  - **Lookback 60 minutes and decision step 60 minutes (a judgment):**
    - the source's models are undisclosed "high-frequency trend-following models" (P-K7-042-e);
    - one-hour time-series momentum is the simplest trend rule at the resolution the source reports
      its clock in ("around 7:00 PM", "roughly the next 24 hours", P-K7-042-b);
    - it is also the horizon of K7-012's opposite evidence (P-K7-012-b), so the member bets directly
      on which of the two holds in this window.
  - **Threshold 0.**

  **Grid:** none.
- **Expected entries and hold:**
  - At most 20 entries per Monday trade date, none on other days. Each position is held >= 59 minutes.
    Floor: (a) ok, (b) ok, (c) ok.
  - **Research window:** 63 Mondays, less four with likely early halts (2025-05-26, 2025-09-01,
    2026-01-19, 2026-02-16, [E.2 confirms]) and less roll blackouts: about 50 to 55.
  - **Confirmation window:** 148 Mondays, less the same exclusions.
  - **Frequency:** about 5.5 x eps per traded Monday (C11).
- **Falsification:** the standard condition only.
- **Topstep check:**
  1. Flat by F: last fill 14:00 Monday.
  2. Order type: market.
  3. D9.4: at most 20 trades a day, hourly holds, no stops or brackets. No fill in the first 60
     minutes after the Sunday 17:00 CT reopen (before the change), so there are no "reckless trades
     in gapped markets to profit from stray fills" [F7.2].
  4. Star: as CP1.
  5. News: 1 lot-equivalent. A Monday 07:30 CT release is held through at 1 lot (allowed).
  6. D9.5a guard: fills are at hh:00 or hh:01. None falls in [07:30, 07:32) or in the half-open
     event window [07:30, 08:00): 08:00 is outside it.
  7. Position limit: <= 1 lot-equivalent (the order never exceeds 1, C2).
  8. Price limit: C13.
- **Data needed:**
  - MBT ohlcv-1m from Sunday 17:00 CT to Monday 14:00 CT on Monday trade dates, research and
    confirmation windows. The full-session ohlcv-1m purchase in D13 already contains these bars.
  - The member-level coverage check covers [Sunday 17:00, Monday 14:00) CT, which lies outside D1's
    measured window (C12).
  - D8's cost buckets for Sunday evening are calibrated on Tuesday evenings (section 7, item 9).
- **Trials in N:** 1.

### K7-ml-01 (the ML member, D15; this entry fills only D15.10's fields)
- **Traded vehicle: the bitcoin exposure {MBT}**, the contract chosen by D2 in E.2 (MBT is the only
  admissible one).
  - **Reason:** it is the only traded K7 exposure (D1), and every intraday item in the K7 log concerns
    bitcoin.
  - **No fallback:** if D2 does not admit bitcoin, K7 has no traded exposure and no ML member.
- **Products the features read:** MBT only, plus the calendars EC-CAL, EC-MBTX, EC-FOMC, EC-NFP,
  EC-CPI and EC-PPI (C9).
  - **Why MET is not read:**
    1. MET's day-session coverage is 0.947 (D1 table). A MET leg would very likely fail D9's
       member-level check (>= 0.95 in the member's own window), which would exclude the whole ML member
       before screening.
    2. D13 buys no MET history.
    3. The log's inside-crypto evidence runs from bitcoin to ether, "BTC leads ETH price adjustment"
       (P-K7-021-b), so a MET feature has no logged predictive direction for MBT (X-12).
  - **Why no spot, BRR or ETF-flow feature:** none is in the data plan. BRR history is licensed (C10),
    and ETF-flow publication times are unverified (X-03).
- **Cluster features.** There are 7; with D15.4's B1 to B5 that makes 12. Throughout, t_j is the
  decision time, "the bar at t_j - 1" is the last bar closed at t_j, and tick = 5.00 (MBT).

| # | Name | Exact formula | Source (registry id, passage) | Availability |
|---|---|---|---|---|
| KF1 | usrel_day | 1 if a BLS Employment Situation, CPI or PPI release was published at 08:30 ET (07:30 CT) on d (EC-NFP, EC-CPI, EC-PPI); else 0 | K7-026 P-K7-026-a, P-K7-026-b (bitcoin's 30-minute response to inflationary surprises); K7-023 P-K7-023-a, P-K7-023-b, P-K7-023-c (activity bursts and a negative return component at US release times); K7-031 P-K7-031-b, P-K7-031-c (US news drives BTC jumps; the unemployment rate is named); K7-003 P-K7-003-c (futures lead more "around macroeconomic surprises"); Topstep F6 (07:30 CT release lists MBT) | 07:30 CT on d, before W0 = 09:30 |
| KF2 | fomc_phase | 0 if d is not an EC-FOMC statement day; 1 if it is and t_j < 13:00 CT; 2 if it is and t_j >= 13:00 CT | K7-029 P-K7-029-a, P-K7-029-b, P-K7-029-c (volatility and volume jump in the first hour after the 14:00 ET statement; placebo-controlled); K7-018 P-K7-018-a (intraday predictability changes on FOMC days); Topstep F6 | schedule known in advance; depends only on the clock |
| KF3 | expiry_phase | 0 if d is not an EC-MBTX final trading day; 1 if it is and t_j < T_exp(d); 2 if it is and t_j >= T_exp(d) (T_exp from C9) | K7-005 P-K7-005-a, P-K7-005-b, P-K7-005-d; K7-033 P-K7-033-c, P-K7-033-d; K7-019 P-K7-019-b | contract terms known in advance |
| KF4 | dow | weekday of d: 0 = Monday, ..., 4 = Friday | K7-042 P-K7-042-b, P-K7-042-d (Monday window); K7-038 P-K7-038-b (weekly Friday BFF settlement to BRRNY); K7-040 P-K7-040-c (returns differ by night of the week); K7-015 P-K7-015-b (a Friday effect) | calendar known in advance |
| KF5 | ret60 | (close of the bar at t_j - 1 - open of the bar at t_j - 60) / tick. Both bars must exist with one instrument_id, else no trade at t_j | K7-012 P-K7-012-a, P-K7-012-b (1-hour autocorrelation -0.0557); K7-042 P-K7-042-b, P-K7-042-e (hourly trend window); K7-018 P-K7-018-c | bars closed <= t_j |
| KF6 | ret120 | (close of the bar at t_j - 1 - open of the bar at t_j - 120) / tick. Both bars must exist with one instrument_id, else no trade at t_j | K7-012 P-K7-012-b (2-hour autocorrelation -0.0858, the strongest), P-K7-012-f | bars closed <= t_j (at t_j = 09:30 the earlier bar is the 07:30 bar) |
| KF7 | open30 | (close of the 08:59 bar - open of the 08:30 bar on d) / tick. Both bars must exist with one instrument_id, else no trade on d | K7-014 P-K7-014-a, P-K7-014-b (post-ETF volatility spike and wider tails in 08:30-09:00 CT, "the only window surviving multiple testing correction"); K7-011 P-K7-011-b, P-K7-011-c (the first half hour predicts the last) | 09:00 CT on d, before W0 |

- **Decision window [W0, W1] = [09:30, 13:30] CT; horizon h = 60 minutes.**
  - **Decision times:** t_j = 09:30, 10:30, 11:30, 12:30, 13:30, which is 5 a day. W1 + h = 14:30 <=
    F.
  - **Fills:** by D15.3's convention a position covers the open of t_j + 1 min to the open of
    t_j + 60. Every fill is at :31 (entry) or :30 (exit).
  - **Why h = 60:** the logged intraday return evidence for bitcoin is at one to two hours:
    - K7-012's autocorrelation at 1 h and 2 h (P-K7-012-b);
    - K7-042's hourly trend window (P-K7-042-b);
    - K7-029's first post-FOMC hour (P-K7-029-a);
    - K7-024's 1-2 hour flow horizon (P-K7-024-a), a feature not used here (X-07).

    h = 30 matches only K7-011's half-hour construction, whose target window lies after F (covered by
    CP1), and it doubles the round trips per hour of exposure. h = 120 leaves 2 decisions a day in the
    window.
  - **Why this window:**
    1. **It starts at 09:30,** so the 08:30-09:00 opening spike, whose tails widen (P-K7-014-b), is
       never an entry interval. Its move is still available as KF7.
    2. **It stays inside D1's measured day session (0.996).** Volume and volatility are concentrated
       in European and North American hours (P-K7-013-a), which avoids the overnight coverage risk of
       C12.
    3. **The :30 grid keeps every fill off the scheduled minutes:**
       - the 13:00 FOMC statement, which the 12:30 position spans;
       - the 10:00 or 11:00 CT BRR expiry time;
       - the 14:59 settlement minute;
       - the 07:30 releases.

       No ML fill lands in a release minute or a C14 event window, which is the gapped-market case of
       D9.4.
- **Expected rows:** about 5 x the eligible research-window trade dates, where eligible dates are:
  - about 305 trade dates,
  - less about 45 roll-blackout dates (15 monthly splices x 3),
  - less about 8 early-halt and early-close dates,
  - less the 20-date warm-up of B4. That warm-up lies inside the research window, since holdout-2 is
    sealed (C8).

  That is roughly 1,100-1,200 rows. E.2 gives the exact count.
- **Expected entries:** at most 5 per day (<= 20), each held 59 minutes. Floor ok by construction.
- **Falsification:** the standard condition: UCB95 of mean net daily P&L per contract below eps at
  >= 80% achieved null power on the confirmation window counts against it. Failing the D5 screen puts
  it in Tier B.
- **Topstep check:**
  1. Flat by F: last exit 14:30.
  2. Order type: market (D15.6).
  3. D9.4: at most 5 entries a day, 59-minute holds, no stops or brackets, no fill in a release or
     reopen minute.
  4. Star: as CP1.
  5. News: q = 1 lot-equivalent, not the full maximum. The 12:30 position spans the FOMC statement.
  6. D9.5a guard: never triggered by construction.
  7. Position limit: <= 1 lot-equivalent.
  8. Price limit: C13.

  Also D9.9: the "Unfair technology ... AI" line is flagged for the user, as for every ML member.
- **Data needed:**
  - MBT ohlcv-1m. The research window trains and tunes; the confirmation window scores the frozen
    model.
  - The member-level coverage check covers 09:31-14:30 CT. Features also read the 07:30 CT bar (KF6
    at 09:30) and the trade date's first bar (B2). A missing bar means no trade at that t_j.
  - External: EC-CAL, EC-MBTX, EC-FOMC, EC-NFP, EC-CPI, EC-PPI.
- **Before and after 2026-05-29:** every feature is a clock or calendar value or an MBT day-session
  bar, except B2, which reads the trade date's first bar: Sunday 17:00 CT for Mondays in both regimes
  under C3 (section 7, item 2). No weekend bar is read.
- **Trials in N:** 1 at confirmation. In research-window accounting the grid counts as 48 (D15.8).
- **Not chosen here (D15):** model type, grid, selection rule, trade rule.

---

## 2. Excluded members

| Id | What it would have been | Failed check | Reason |
|---|---|---|---|
| X-01 K7-gap-01 | Trade MBT after the Sunday 17:00 CT reopen on the weekend move, following or fading the "gap" between the Friday close and the Sunday open (K7-036 P-K7-036-b; weekend spot volatility "approximately 75% of weekday levels", P-K7-036-c) | CME weekend closure; D9.4; rule 1 | **Depends on CME's weekend closure, announced to end 2026-05-29 (K7-036, unverified); not deployable if in effect; E.1 may revive it only if the closure is confirmed to persist.** Update from this task's fetch: CME's 1 June 2026 release states the 24/7 hours "went live on Friday, May 29". The closure has ended, so nothing is left to revive. The design had two more problems. First, the signal needs weekend spot prices (free Coinbase candles would serve, C10). Second, the first fills after a reopen are the "reckless trades in gapped markets to profit from stray fills" case of D9.4 [F7.2]. The log also found no study of the gap's direction ("No academic study of the CME weekend gap itself was found", log container 2) |
| X-02 K7-spotlead-01 | Trade MBT in the direction of a price move on spot or offshore venues, which CME absorbs in "between 4 and 5 minutes" (K7-002 P-K7-002-a, P-K7-002-b, P-K7-002-c, P-K7-002-d; K7-001 P-K7-001-a) | D9.3; D9.4; rule 1 (conflicting evidence) | The documented edge ends within 5 minutes of the shock, so a one-minute-bar rule filling at the next open keeps at most a few minutes. Holding to the 10-minute mean-hold floor, D9.3(c), means holding beyond the documented horizon, and the edge sits at Topstep's "durations measured in seconds, not minutes" line [F7.3]. Evidence from the MBT era is the other way: CME "leads price discovery" (P-K7-021-b); "CME bitcoin futures have consistently led price formation" (P-K7-006-b); "the futures market generally leads spot" (P-K7-003-b); and MBT itself led Binance by 0.055 to 0.15 seconds in 2024 (P-K7-025-b, -c). K7-003 calls the direction specification-sensitive (P-K7-003-a). Data: spot minute bars are free (C10); offshore perpetual history was not checked |
| X-03 K7-etfflow-01 | Trade MBT in the day session in the direction of the prior day's net flow into US spot bitcoin ETFs (K7-020 P-K7-020-a, P-K7-020-b; K7-027 P-K7-027-a) | Rule 3 (availability timestamp); D4 (window) | (a) When the day-d flow becomes public relative to 08:30 CT on d+1 is not stated ("[unverified], which decides feasibility", log K7-020). No archive of publication times was found, so a rule reading flow(d-1) cannot be shown to be free of look-ahead. (b) The flows exist only from January 2024 (P-K7-020-d window). The confirmation window ends 2024-02-29, so it holds only about 40 ETF-era trade dates, and the member would be "inconclusive by design". (c) The source itself finds that "individual flow shocks reverse significantly" once future flows are controlled (P-K7-020-c). Revival would need a timestamped flow source and a confirmation design that covers the ETF era |
| X-04 K7-cpisurp-01 | Trade MBT after the 07:30 CT CPI or PPI release, signed by the inflation surprise: "Bitcoin price decreases by 24 bps (t-statistics 2.44)" per 1 SD (K7-026 P-K7-026-a) | Rule 3; D9.5a; rule 1 | The surprise needs the survey consensus the source uses (a Bloomberg survey, log K7-026 mechanism), which is proprietary, and no obtainable history was named. The documented response is contemporaneous, in a window "10 minutes before ... 20 minutes after" the release (P-K7-026-b), and the first two minutes are unfillable under D9.5a. A post-release drift is untested. The sample is 2013-2021, before the ETFs. The release calendar enters K7-ml-01 as KF1 |
| X-05 K7-relshort-01 | Short MBT around the 07:30 CT US release, following the eigen-signal that "points out to the occurrence of negative log-returns during that period" (K7-023 P-K7-023-c) | Rule 1 | It is descriptive: a correlation-matrix component on Binance 2020-2022 (P-K7-023-d), with no conditional-mean test and no window or event list. "12:30 UTC" equals 08:30 ET only while US summer time is in force; in winter 08:30 ET is 13:30 UTC (arithmetic), so the timing is ambiguous. It enters K7-ml-01 as KF1 |
| X-06 K7-basisfb-01 | Five-minute momentum or reversal on MBT, switched by the level or change of the futures-spot basis (K7-007 P-K7-007-a, P-K7-007-b); the crash-state basis of K7-008 (P-K7-008-b) | Rule 1; not intraday-feasible (K7-008) | K7-007 is abstract only. The quantiles and state definitions that switch the sign ("When the basis declines by varying magnitudes across quantiles", P-K7-007-b) are not given, so no parameter can be traced. A five-minute horizon also sits against the 10-minute mean-hold floor. K7-008 is two-legged arbitrage held to expiry on CBOE futures (P-K7-008-a), and the spot leg is not tradable on Topstep |
| X-07 K7-onchain-01 | Buy MBT for 1 to 2 hours after large USDT net inflows to exchanges, "US$ 100 million of USDT net inflows predict ... 0.065% of BTC return in the next hour" (K7-024 P-K7-024-a, P-K7-024-c) | Rule 3 | Exchange net inflows need exchange-wallet attribution from an on-chain data vendor (log: "on-chain data vendor dependence (a data source this program does not hold)"). No free, timestamped historical series was named. BTC's own flows "generally lack predictive power" (P-K7-024-d), and USDT is insignificant beyond 2 hours (P-K7-024-b) |
| X-08 K7-brrny-01 | A directional MBT trade in the BRRNY hour, 14:00-15:00 CT, the benchmark of "six out of the 10 new spot bitcoin" ETFs with "more than 20% of a day's notional volume" (K7-038 P-K7-038-a, P-K7-038-d; K7-019 P-K7-019-b, P-K7-019-c; K7-034 P-K7-034-b, P-K7-034-c) | Rule 1 | Only volume and replication facts are logged. The methodology anticipates even spreading of hedge flow ("transacting Y/K units of the cryptocurrency during each partition", P-K7-019-c), and no return or direction for the hour is documented. The ETF regime is absent from the confirmation window (as X-03). BRRNY values are licensed (C10). The clock enters the ML member through B3 and KF4 |
| X-09 K7-tas-01 | Trade the MBT settlement minute (14:59-15:00 CT, P-K7-033-a) through the offsetting flow of TAS counterparties (K7-037 P-K7-037-a, P-K7-037-b) | Rule 1; D9.3 | TAS size and direction are not reported ("no volume data", log). A post-settlement trade has only 15:00 to 15:08, 8 minutes, before F. Nothing is documented to trade |
| X-10 K7-fomcvol-01 | An FOMC-hour or release-minute volatility member for MBT (K7-029 P-K7-029-a; K7-031 P-K7-031-a, P-K7-031-b; K7-030 P-K7-030-a) | D6 (family D gates not ported); rule 1 | The evidence covers mean absolute returns, jumps and spreads, not signed returns (P-K7-029-a "mean absolute hourly returns"). Family D state gates condition a base strategy and are not ported (D6). The FOMC and release clocks enter K7-ml-01 (KF1, KF2). K7-030's spread widening at release minutes is what D8's event-window cost and D9.5a already encode |
| X-11 K7-daysess-01 | Short MBT over the US day session, because bitcoin's gains accrue outside US hours (K7-027 P-K7-027-a; K7-039 P-K7-039-e; K7-040 P-K7-040-b) | D6 (family A clock drift not ported); rule 1 | The sources say day-session returns "diminished" (P-K7-040-b) and are "relatively small and volatile" (P-K7-039-e); none documents a negative day-session mean. It is a drift bet on the clock, which D6 does not port, because on a product without a documented drift it measures the window's trend |
| X-12 K7-ethlead-01 | Trade MBT on a lagged MET or ether move (inside K7; MET as a signal leg) | Rule 1; D1/D9 coverage | The only lead-lag passage runs the other way: "BTC leads ETH price adjustment" (P-K7-021-b). ETH jumps are more news-sensitive, but "co-jumps among Bitcoin and Ethereum are scarce" (P-K7-031-a, P-K7-031-c). MET's day-session coverage is 0.947 < 0.95 (D1), so the leg would likely fail D9's check. CME's ETH/BTC relative-value pieces are daily and trade MET (R-K7-063) |
| X-13 K7-fda-01 | Forecast the next day's intraday return curve by functional data analysis; buy at the forecast minimum and sell at the forecast maximum (K7-017 P-K7-017-a, P-K7-017-b, P-K7-017-c) | Rule 1; D15.2 | The curves are 24-hour Bitstamp curves, and a CME-session redefinition with an exit by F is untested (log). The result flips sign with the training length: "a positive Sharpe ratio if S = 182, while a negative Sharpe ratio if S = 365" (P-K7-017-e). A rolling re-estimated forecast model is a flexible-model search, and the cluster's one flexible model is K7-ml-01 |
| X-14 K7-fri-01 | Long bitcoin from Friday 3 p.m. EST (14:00 CT) for 4 to 24 hours (K7-015 P-K7-015-b, P-K7-015-c) | Not intraday-feasible | The hold crosses Friday's 15:08 CT flatten and the weekend (TopstepX "closed till Sunday at 5:00 PM", F4). The one-hour Friday variant is the paper's benchmark ("only investing from 3:00:00 p.m. to 3:59:59 p.m. on Fridays"), which its strategies outperform (P-K7-015-c); it is not a hypothesis. Only a few hourly means are significant (P-K7-015-d) |
| X-15 K7-preholiday-01 | Buy bitcoin at the close before a US holiday and sell at the close after (K7-041 P-K7-041-b, P-K7-041-c) | Not intraday-feasible | Close-to-close holds through the holiday and nights. A same-day pre-holiday session variant has no passage |
| X-16 K7-utc2100-01 | Long 21:00-23:00 UTC (K7-039 P-K7-039-c), or overnight after NYSE close at a 10-day high (K7-040 P-K7-040-e) | Not intraday-feasible | 21:00-23:00 UTC is 15:00-17:00 CT in winter and 16:00-18:00 CT in summer: after F, and across CME's daily break before 2026-05-29. K7-040's rule holds overnight |
| X-17 K7-hftlead-01 | Trade MBT's sub-second lead over spot (K7-025 P-K7-025-b, P-K7-025-c; K7-003 P-K7-003-b) | D9.3; D9.4 | The lead is 0.055 to 0.15 seconds. Any rule on it is the "average durations measured in seconds" pattern [F7.3] and needs latency the program does not model |
| X-18 K7-mlprec-01 | A second learned model: LSTM classification at 15-minute or hourly bars (K7-028 P-K7-028-a, P-K7-028-b), or LASSO-BMA predictor selection (K7-016 P-K7-016-a, P-K7-016-b) | D15.2 | One ML member per cluster (D15). Their horizons for a same-day trade are [unverified] (log). They are precedents for K7-ml-01 only |

---

## 3. Beyond budget (lead decides)

None. The log supports 3 new members inside the budget of 11 non-port, non-ML slots. The following
were considered and not written; none is a budget overflow:
- **A day-session variant of K7-expiry-01,** entering at 08:30 CT instead of T_exp - 300 min.
  - What it would do: survive a failed overnight coverage check (C12).
  - Why not written: it is a different window from the documented one, P-K7-005-b's 5 hours. It would
    be one more trial. The lead may add it now as a declared fallback, but not after the coverage
    result is seen.
- **1-hour and 4-hour versions of K7-rev2h-01** (P-K7-012-b: -0.0557 and -0.0564). Not written: the
  source's headline and strongest horizon is 2 hours. Each would be one more trial.
- **A Friday BFF / BRRNY-window member** (P-K7-038-b). No direction is documented (X-08).
- **A post-expiry member.** K7-005's pooled robustness says "No effects are detected after then"
  (P-K7-005-d). Nothing to write.

---

## 4. Routed to K8

These are the K7 reader's flags (log section 4). K8's dispositions are copied from
reports/stage_e0_research_K8.md rows F35 to F46 for the record. None was read by this writer.

| Source | Legs | One phrase | K8 disposition (K8 log) |
|---|---|---|---|
| Conlon, Corbet, Oxley (2024), JFM 10.1002/fut.22541 | VIX-family (K1) and CME bitcoin basis (K7) | equity-volatility sentiment and bitcoin basis | F35: sentiment, shelved |
| Kose et al. (2024), JFM 10.1002/fut.22487 | VIX, dollar, gold, oil (K1, K3, K5, K4) and bitcoin (K7) | global drivers of the bitcoin price | F36: rejected (daily and weekly SVAR) |
| Aalborg et al. (2018), SSRN 3233977 | VIX (K1) and bitcoin (K7) | daily drivers | F37: rejected (daily drivers) |
| Mourey et al. (2025), SSRN 5382090 (registry K8-004, tagged K7 and K1) | weekend crypto returns (K7 signal) and Monday equity indices (K1) | weekend crypto move as a Monday equity signal | F38: passed by K8 (abstract only). Note for K8: since 2026-05-29 the weekend crypto move is also visible in CME's own MBT bars, but those bars belong to no program trade date (C3), and TopstepX stays closed at weekends (F4) |
| arXiv 2505.14655, (Micro)Strategy and bitcoin | bitcoin (K7) and single stocks | crypto-equity link | F39: rejected |
| Krause (2026) SSRN 6925619; Lee (2024) SSRN 5033066 | bitcoin (K7) and equity indices (K1) | ETF-era correlation change | F40: rejected |
| Shakourloo (2026), SSRN 6377464 | bitcoin (K7) and macro variables | lead-lag | F41: rejected |
| Joo (2023), SSRN 4355765 | bitcoin (K7) and HG, NG, GC, CL (K5, K4) | hedge ratios | F42: rejected |
| Mazur (2024), SSRN 4810965 (K7-027), gold-ETF item P-K7-027-c | bitcoin-ETF inflows (K7) and gold-ETF outflows (K5) | flow substitution | F43: duplicate of K7-027 |
| CME economic research, bitcoin with equities and gold (2025, 2026) | bitcoin (K7), equities (K1), gold (K5) | correlation regime commentary | F44: rejected |
| Pinchuk (K7-026), 5-year note futures as a control | bitcoin (K7), rates (K2) | rates only as a control | F45: duplicate of K7-026 |
| Quantpedia bitcoin-and-gold / equities items (five titles) | bitcoin (K7), gold (K5), equities (K1) | allocation and ETF-spread ideas | F46: rejected |

This catalog adds no new K8 routing.

---

## 5. Log accounting

This covers every passed item in reports/stage_e0_research_K7.md section 3 (K7-001 to K7-043, of
which K7-035 is a blocked stub). No `[K7]`-tagged passage exists in any other log.

| Item | Disposition |
|---|---|
| K7-001 Baur, Dimpfl (spot leads futures; abstract only) | Excluded as a member, X-02. Evidence only |
| K7-002 Alexander, Heck (CME absorbs shocks in 4-5 minutes, 2019-2020) | Excluded as a member, X-02. Used as transfer reasoning in K7-expiry-01 and K7-rev2h-01 (P-b). Used for clock facts in C3 (P-e). P-f (saw-tooth near monthly expiry) is context for C8's roll reasoning |
| K7-003 Frino et al. (futures generally lead; specification-sensitive) | Evidence against X-02 and in X-17 (P-a, P-b). Used in K7-ml-01 KF1 (P-c). The Tether-tweet part is social media, shelved |
| K7-004 Quantpedia, expiry-event daily study | Conflicting evidence stated in K7-expiry-01 (P-b, P-c). Its d+1 and d+2 legs cross the weekend: not intraday-feasible. P-d's time is superseded by K7-033's primary text |
| K7-005 Blasco, Corredor, Satrústegui (pre-expiry spot returns) | **Used:** K7-expiry-01 (P-a, b, c, d, e, f); K7-ml-01 KF3 |
| K7-006 Robertson, Zhang (CME leads) | Evidence against X-02 (P-b) |
| K7-007 Ngene, Wang (basis-conditioned 5-minute feedback) | Excluded, X-06 (insufficient evidence: no traceable parameters) |
| K7-008 Hattori, Ishida (crash arbitrage, CBOE) | Excluded, X-06 (not intraday-feasible: two legs to expiry) |
| K7-009 Pati (MBT informativeness, intraday) | Insufficient evidence: blocked, title only. The only MBT-specific item; an open lead (section 7, item 12) |
| K7-010 Baur, Cahill, Godfrey, Liu (time-of-day effects; "no consistent or persistent patterns") | Insufficient evidence for a member. It is negative evidence for family A/E clock effects (P-b); D6 does not port family A |
| K7-011 Shen, Urquhart, Wang (first half hour predicts last) | **Covered by CP1.** The paper's own target window (to 16:00 CT) is not intraday-feasible under F. P-f's anti-persistence is cited in K7-rev2h-01. Used in K7-ml-01 KF7 (P-b, P-c) |
| K7-012 De Nicola (1-4 hour negative autocorrelation) | **Used:** K7-rev2h-01 (P-a, b, c, e, f); K7-ml-01 KF5, KF6. Conflicting evidence stated in K7-montrend-01 |
| K7-013 Eross et al. (n-shaped volume, spread, volatility) | Insufficient evidence for a directional member (stylized facts). Used as reasoning for K7-ml-01's day-session window (P-a) |
| K7-014 Lee et al. (post-ETF volatility spike 08:30-09:00 CT) | Insufficient evidence for a directional member (volatility and tails; the median is unaffected, P-b). Used in K7-ml-01 KF7 and window placement; context for CP2's opening range |
| K7-015 Miralles-Quirós (Friday 3 p.m.) | Excluded, X-14 (not intraday-feasible). Used in K7-ml-01 KF4 (P-b) |
| K7-016 Huang, Gao (LASSO-BMA) | Excluded, X-18 |
| K7-017 Bouri et al. (functional return curves) | Excluded, X-13 |
| K7-018 Wen, Bouri, Xu, Zhao (momentum and reversal; FOMC days) | Momentum part **covered by CP1**. FOMC conditioning used in K7-ml-01 KF2 (P-a). Reversal part: insufficient evidence (segment definitions unverified); cited as conflicting evidence in K7-rev2h-01 |
| K7-019 CF Benchmarks methodology v17.4 | **Used:** K7-expiry-01 (P-a, P-b, P-d); K7-ml-01 KF3. BRRNY part excluded, X-08 (P-c) |
| K7-020 Lim (ETF flows) | Excluded, X-03 |
| K7-021 Aleti, Mizrach (CME leads; BTC leads ETH) | Evidence against X-02 (P-b). Excluded as a MET-signal member, X-12; the reason MET is not read by K7-ml-01 |
| K7-022 Deprez, Frömmel (75,360 technical rules) | **Covered by CP2** (the breakout family), with a negative prior. Conflicting evidence for K7-rev2h-01 |
| K7-023 Wątorek et al. (release-time bursts; 12:30 UTC component) | Excluded as a member, X-05. Used in K7-ml-01 KF1 |
| K7-024 Chi, Chu, Hao (on-chain flows) | Excluded, X-07 (rule 3). Cited for K7-ml-01's h (P-a) |
| K7-025 Plazuelo Pascual et al. (MBT leads Binance, sub-second) | Excluded, X-17. Used as transfer reasoning in K7-expiry-01 and K7-rev2h-01 (P-b). Evidence against X-02 |
| K7-026 Pinchuk (bitcoin falls on inflation surprises) | Excluded as a member, X-04. Used in K7-ml-01 KF1. Rates-control part routed to K8 (section 4) |
| K7-027 Mazur (spot ETF facts) | Excluded, X-03 and X-11. Gold-ETF item routed to K8 |
| K7-028 Kryńska, Ślepaczuk (LSTM) | Excluded, X-18 |
| K7-029 Yang, Wang (FOMC volatility and volume) | Excluded as a member, X-10. Used in K7-ml-01 KF2 and the h choice |
| K7-030 Mercik, Będowska-Sójka (spreads at release minutes) | Excluded as a member, X-10 (a cost state, which D8 and D9.5a already encode) |
| K7-031 Ben Omrane et al. (macro news and BTC/ETH jumps) | Excluded as a member, X-10 and X-12. Used in K7-ml-01 KF1 |
| K7-032 CME, Analysis of the BRR | **Used:** K7-expiry-01 (P-a, P-b; the BRR window). P-e is background for X-08 |
| K7-033 CME, MBT FAQ | **Used:** C3 (P-b), C9 EC-MBTX (P-c, P-d), C13 (P-e), CP1 and CP3 (P-a), K7-expiry-01, K7-ml-01 KF3. The settlement-minute mechanism is excluded, X-09 |
| K7-034 CME, BTIC on crypto futures | Excluded as a member, X-08 (no direction). P-d (no BTIC on the last trade date) is noted, not used |
| K7-035 CME Bitcoin Futures Liquidity Report | Blocked (stub). Nothing |
| K7-036 CME, 24/7 trading article | Excluded as a member, X-01 (the brief's reason). **Its 29 May 2026 date is now verified** by CME's own releases (preamble). Header and C3 |
| K7-037 CME, TAS FAQ | Excluded, X-09 |
| K7-038 CME, Bitcoin Friday futures (BRRNY) | Excluded as a member, X-08. Used in K7-ml-01 KF4 (P-b); context for CP1 (P-a) |
| K7-039 Padyšák, Vojtko (21:00-23:00 UTC) | Excluded, X-16 (not intraday-feasible). Evidence in X-11 |
| K7-040 Dujava (overnight sessions) | Excluded, X-16 (not intraday-feasible). Evidence in X-11. Used in K7-ml-01 KF4 (P-c) |
| K7-041 Dujava (pre-holiday) | Excluded, X-15 (not intraday-feasible) |
| K7-042 Pagani (Concretum, Sunday-evening trend) | **Used:** K7-montrend-01 (P-a, b, c, d, e); K7-ml-01 KF4, KF5. Conflicting evidence for K7-rev2h-01 |
| K7-043 Quant Fiction (month-of-year, max-statistic permutation) | Not intraday-feasible (monthly) and negative. Its max-statistic permutation design is a methodological note for the lead's multiple-comparisons work; no member |
| `[K7]` passages in the K1 to K6 and K8 logs | None. The K8 log's F35 to F46 are dispositions of K7's flags (section 4). Registry line K8-004 (tagged K7) is K8's claim |
| R-K7-019 Howard (2026), SSRN 7067778 | Not passed by the reader. A possible panel of eight CME futures with MBO order-book data, left unclaimed for the lead; its seconds-horizon mechanism would fail D9.3/D9.4 anyway |
| R-K7-026 Su et al. (2022); R-K7-036 Kia, Song, Xu (2024) | Not passed (no abstract reachable); open leads for the lead. Not used |
| R-K7-001 to R-K7-073 (the rest) | Rejected at pre-filter or on reading. Not used |

**Correlated members, flagged for the lead's Tier-A accounting (not duplicates).**
- **K7-rev2h-01 and K7-montrend-01** bet opposite signs at related horizons: a 2-hour reversal in
  every day session, and a 1-hour trend in the Monday window. Their only overlap is Mondays 10:31-14:00
  CT, where both can hold positions.
- **CP1 and K7-ml-01's B2 and KF7** read the same overnight and first-half-hour moves.
- **K7-expiry-01 and K7-ml-01's KF3** use the same expiry clock.

---

## 6. Trial count table

| Member | Exposure | Grid points | Trials in N (bitcoin admitted by D2) |
|---|---|---|---|
| K7-cp1-01 | bitcoin | 1 | 1 |
| K7-cp2-01 | bitcoin | 1 | 1 |
| K7-cp3-01 | bitcoin | 1 | 1 |
| K7-expiry-01 | bitcoin | 1 | 1 |
| K7-rev2h-01 | bitcoin | 1 | 1 |
| K7-montrend-01 | bitcoin | 1 | 1 |
| K7-ml-01 | bitcoin (no fallback) | 48 in research-window accounting only (D15.8) | 1 |
| **Cluster total** | | | **7** = 3 port + 3 new + 1 ML. **0** if D2 does not admit bitcoin |

If the user re-admits MET (borderline at 0.947), ether would add 3 port trials. No new member here
is written for ether.

---

## 7. Questions for the lead (decisions reserved for the lead; none taken here)

1. **24/7 CME crypto trading is confirmed.** CME's 1 June 2026 release says it "went live on Friday,
   May 29" (preamble). So:
   - X-01's exclusion holds, and the brief's "(K7-036, unverified)" can be upgraded.
   - D6's crypto session table, D10's equity-and-crypto calendar and E.2's bar builder need a crypto
     note for dates from 2026-05-29: bars now exist at weekends and at 16:00-16:59 CT on weekdays.
   - The lead decides the design wording.
2. **Trade-date convention after the change.**
   - CME now assigns weekend and holiday trading "a trade date of the following business day". This
     catalog keeps the program convention, [d-1 17:00, d 16:00) CT (C3).
   - Under that convention, Monday's first bar is Sunday 17:00 CT in both regimes, and no member reads
     weekend bars.
   - If the lead adopts CME's assignment, CP1's Monday signal and K7-ml-01's B2 on Mondays would start
     at Friday 16:00 CT and read weekend prices. That would change their meaning on the research
     window's last three Mondays and on every deployed Monday.
3. **Regime mismatch.**
   - The confirmation window (MBT's listing on 2021-05-03 to 2024-02-29) is entirely pre-24/7 and
     almost entirely pre-spot-ETF. Deployment would be post-both.
   - A K7 null or edge therefore describes the older regime. That matters most for the Monday members
     (CP1 on Mondays, K7-montrend-01) and for K7-expiry-01, whose only post-2021 evidence reverses
     sign (P-K7-004-b).
   - The lead may want NULL_CRITERIA_E's K7 statement to say this.
4. **Short history.**
   - MBT listed 2021-05-03, so its confirmation window has at most 739 weekdays. D4's start rule may
     shorten it further if MBT's 2021-2022 one-minute volume was below 0.25 x the 2025-26 reference.
   - D2 and D4 allow "the exposure's full-size contract bars" as a price path. For bitcoin that would
     be CME BTC (5 bitcoin, P-K7-005-a), which is not Topstep-permitted, not in the D1 table and not
     in D13's purchase plan.
   - Whether BTC bars may stand in is for the lead and the user.
5. **Coverage outside the day session (C12).**
   - K7-expiry-01 (from 05:00 or 06:00 CT) and K7-montrend-01 (Sunday 17:00 CT to Monday 14:00 CT)
     depend on MBT's overnight coverage, which D1 did not measure.
   - If they fail D9's check, they drop before screening. No fallback is written; a day-session expiry
     variant would be one more trial (section 3).
   - The lead may declare such a fallback now, before E.2 computes coverage.
6. **Low-frequency members.**
   - K7-expiry-01 trades about 12 research dates and needs about 25 x eps per event. K7-montrend-01
     trades about 55 Mondays and needs about 5.5 x eps per Monday (C11).
   - Both are likely "null at eps" or "inconclusive by design".
   - The 21:52 ruling on K4 (Q4) kept such members and let the power check decide. The lead may cut
     either (1 trial each).
7. **ML sample size.**
   - K7-ml-01 has about 1,100-1,200 research rows, fewer than D15.1's "few thousand". The monthly roll
     blackout alone removes about 45 dates.
   - Each of D15.5's six blocks holds about 190 rows. With min_data_in_leaf = 200, the early inner
     folds (2 to 3 blocks of training) can grow only one to three leaves.
   - D15 is common to all clusters, so this is flagged, not changed.
8. **Expiry days and the roll blackout.**
   - K7-expiry-01 trades only expiry days whose MBT.v.0 splice came on or before the Thursday of that
     week (C8). E.2 should report the count before screening.
   - If it is zero or near zero, the lead decides whether the member is withdrawn (logged) or whether
     the roll convention for MBT should differ.
9. **Cost sample.**
   - D8's five sample dates are Wednesdays, so the Sunday-evening buckets used by K7-montrend-01 are
     calibrated on Tuesday evenings. The 05:00-11:00 buckets of K7-expiry-01 are calibrated on
     ordinary Wednesdays, never on an expiry Friday.
   - Sunday-evening costs just after a pre-change CME reopen may be understated.
   - The lead decides whether to add a Monday trade date (with its Sunday evening) to MBT's mbp-1
     sample: a small spend, quoted in E.1.
10. **MET.** MET is out at 0.947, and no member reads it. If the user re-admits it:
    - ether gains the three ports (+3 trials);
    - the ML member could be re-written to read MET, but only with the coverage check passed.
11. **Rulebook chapter.**
    - The liquidity JSON gives MBT as "CME 348". The K7 log looked for "chapter 350/350A" (R-K7-061).
    - E.2 reads the correct chapter for MBT's price-fluctuation limits (C13) and for the expiry rule
      (checked against P-K7-033-c).
12. **Open leads (not researched here; no search tools):**
    - K7-009, Pati (2022), the only MBT-specific intraday study (blocked);
    - R-K7-026, Su et al. (2022);
    - R-K7-036, Kia, Song and Xu (2024), ETF price discovery;
    - R-K7-019, Howard (2026), a possible CME panel.
13. **E.2 checks named in this catalog:**
    - (a) EC-MBTX dates against CME's published MBT calendar, and T_exp by zoneinfo (C9).
    - (b) The standard 08:30 ET time of each CPI and PPI release in the BLS files (C9).
    - (c) MBT tick history, 2021-2026 (C7).
    - (d) MBT price-limit rules against Topstep's 2% rule (C13).
    - (e) Member-level coverage for [T_exp - 300, T_exp - 1] on expiry days, [Sunday 17:00, Monday
      14:00) on Mondays, the day session, and 09:31-14:30.
    - (f) The number of expiry days outside the roll blackout (item 8).
    - (g) D10 crypto entries after 2026-05-29, and the early-close status of 2025-11-28 and 2025-12-24.
    - (h) Whether D1's liquidity and coverage figures are affected by the regime change. They are not:
      the five calibration dates all predate it.
