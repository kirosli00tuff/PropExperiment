# Stage E.10 hypothesis catalog, cluster K9 (low-frequency, condition-gated session holds)

Writer: CatalogWriter-OpusXHigh (Stage E.10 Task 4), 2026-10-02, 22:58-23:25 PDT.
Status: **DRAFT declaration for the lead (not frozen).** Nothing here is hashed, frozen or registered.
**Round 2 applied** (the lead's rulings of 2026-10-02 23:25 PDT, "Round 2: rulings on CatalogWriter's
section 7", items 1-17, appended to the rulings file), 23:27-23:31 PDT. K9-vixback-01 is withdrawn to
Appendix A.
**Round 3 applied** (the lead's rulings on the Fable review, reports/stage_e10_catalog_rulings.md, R-01 to
R-16), 2026-10-03 00:05-00:09 PDT. K9-vixspike-01 is withdrawn to Appendix B. **1 active member, 3 trials, projected
N = 201.**
Machine-readable copy: reports/stage_e10_catalog_K9.json.

**What this catalog was written from.** No price, bar, tick, order-book or settlement data of any
product or index was opened. No Stage E screen, confirmation record, `*_RETURN.md`, results JSON or
file under data/ was opened. The only numbers used are:
- the lead's rulings (reports/stage_e10_briefs/task4_lead_rulings.md, read in full);
- the frozen cost wall as the design target carries it (reports/stage_e10_design_target.md (a) and its
  machine-readable table reports/stage_e10_research/cost_wall.json, which the design target names);
  E|m_1| enters only as the context denominator the rulings prescribe, never as a literal;
- passages and tables of the saved source papers, each verified by grep (section 8);
- official release calendars fetched in this task (dates and clock times only; no released value).

**Inputs read (by section):** the rulings; the design target (a)-(d); the research-log entries the
rulings name (regime K9R-001 to -005, -008, -012, -014; calendar K9C-001 to -004, -006, -007; commodity
K9M-001 to -011 and -019 to -022 by their numeric-claims lines only); the saved papers behind the three
members; reports/stage_e0_catalog_K8.md (format: header, C1-C15, K8-wkndbtc-01, sections 2, 5, 6);
docs/STAGE_E_DESIGN.md D9 (lines 478-600); reports/stage_e0_topstep_facts.json F9.1, F9.2;
reports/stage_e2a_vehicles.md "Result per exposure" rows 15-17; docs/NULL_CRITERIA_E.md section 3
(lines 78-90). Round 2: the rulings' round-2 section (lines 114-159) and the regime log's K9R-006 and
K9R-007 entries (lines 218-253). The overnight log (K9O-*) was not opened: no member uses it, and its excluded rows are
the lead's rulings verbatim.

**Official pages fetched in this task** (saved raw under reports/stage_e10_research/catalog/, one row
per fetch in catalog/fetchlog.tsv: file | URL | UTC time | sha256 | bytes | tool):
- BLS Employment Situation, CPI and PPI archived-release lists (bls.gov/bls/news-release/empsit.htm,
  cpi.htm, ppi.htm), and three shutdown-period releases whose embargo lines confirm that the archive
  file name carries the release date (empsit_11202025, cpi_10242025, ppi_11252025).
- Federal Reserve FOMC calendar (federalreserve.gov/monetarypolicy/fomccalendars.htm).
- BEA GDP news-release archive and the 2026 release schedule (bea.gov/news/archive?...=451,
  bea.gov/news/schedule/full).
- ISM Report On Business release calendar: the live page (2026 dates) and a Wayback capture of the
  same official page dated 2025-10-09 (2025 dates).
- Tool notes: WebFetch was not used because it does not save the raw page. curl with a browser
  user-agent was denied by bls.gov (three 1,325-byte "Access Denied" pages, deleted, logged); scrapling
  `extract get` worked for BLS, the Fed and BEA. ISM returned a captcha page to `extract get`
  (logged, deleted) and was read with `extract fetch`. Wayback refused curl (logged) and served
  `extract get`. Firecrawl was not needed.

---

## 0. Header

| Item | Value |
|---|---|
| Cluster | K9: low-frequency session holds gated by a rare, sourced condition (design target (b)) |
| Members | **1 active member** (K9-anncday-01) on the equity-index exposures. No ports, no ML member. Withdrawn drafts, kept in full: K9-vixback-01 (round 2 items 6-10; Appendix A) and K9-vixspike-01 (round 3, R-01; Appendix B) |
| Trials in N (confirmation) | **3** = 1 member x 3 exposures (Nasdaq-100, Russell 2000, Dow). Budget 40, so 37 unused. Projected program N = 198 + 3 = **201** |
| Traded exposures and vehicles | Nasdaq-100: MNQ, q_c 1; Russell 2000: M2K, q_c 3; Dow: MYM, q_c 3 (reports/stage_e2a_vehicles.md, rows 15-17). The S&P 500 is not a traded exposure (D1.5); every member's evidence is on the S&P 500 or the US market and is transferred |
| External daily series | None for the active member (calendar only). The VIX close and its 3:45 pm ET fallback (C8) belong to the withdrawn K9-vixspike-01 (Appendix B); the VX futures item to the withdrawn K9-vixback-01 (Appendix A). Nothing is bought in E.10 |
| Calendars | EC-K9 (C9): the K9-anncday-01 date set (and the withdrawn K9-vixspike-01's exclusion set), from the official pages above; holiday sessions from the E.2a equity calendar (C4, R-12) |
| Source overlap | **K9-anncday-01 is labelled "source-overlap"** (its main source runs to 2023-08). The withdrawn K9-vixspike-01 would be "not source-overlap" (Appendix B; R-03, R-11) |
| Starred contracts | MNQ\*, M2K\* and MYM\* are starred micros (D9.8; referent D9.11 and D9.12) |

### Common conventions (apply to every entry unless the entry says otherwise)

- **C1 Clock and bars.** America/Chicago (CT). "The bar at hh:mm" is the ohlcv-1m bar whose ts_event
  (open) is hh:mm:00 CT; it closes at hh:mm + 1 min, and its values are usable from then on (K8 C1).
- **C2 Fills.** A market intent emitted on a bar fills at the next bar's open (D6 engine convention).
  "Market intent on the bar at 14:58" fills at the open of the 14:59 bar.
- **C3 Trade date and hours.**
  - Trade date d = [d-1 17:00 CT, d 16:00 CT). **The trade date of an entry after the 17:00 CT reopen is
    the next calendar day.** The first bar of a Monday trade date is the Sunday 17:00 CT bar.
  - Topstep hours (F4, quoted in K8 C3): "Sunday open | 5:00 PM CT", "Weekday reopen | 5:00 PM CT".
  - C_X = 15:00 CT for the equity group (the C - 2 convention of D6's CP1, as K8-wkndbtc-01 uses it).
    F = 15:08 CT (D9.1).
  - **Reopen entries (round 2 item 5).** Every K9 entry at a reopen is market intent on the 17:59 CT
    bar, filling at the 18:00 CT open, on weekdays and Sundays alike. This amends D-entry for D9.4
    ("reckless trades in gapped markets"), following K8-wkndbtc-01's judgment that the reopen's first
    minutes are the gapped market of D9.4. An 18:00 CT fill on calendar day t belongs to trade date
    t + 1. Holds stay above two hours (about 21 h). **R-06:** this amendment was made after the sources
    were read, so it is a user decision (design draft K9-H; the alternative is the 17:00 CT first bar, as
    D-entry was fixed). The catalog keeps 18:00 pending that decision (lead recommendation: 18:00).
- **C4 Exclusions (all members).**
  - **Roll-blackout dates (D4) are excluded at screening** (`screen_candidate` with `roll_blackout`).
    This catalog does not identify them. The 299-date research window is 316 trade dates less 15
    roll-blackout and 2 UR-1 dates (design target (d)); counts below are given on the 316 dates and, in
    proportion, on the 299.
  - Trade dates on which the entry bar or a bar the rule reads is missing carry no trade. If the exit
    bar is missing, the exit is sent on the first later bar; the engine's flatten at F is the backstop.
  - Trade dates on which the external series has no value for the decision day (withdrawn drafts only; a CBOE holiday that is
    not a CME holiday, or the reverse) carry no trade. No forward fill.
  - **Early-close, early-halt and closure dates (R-12, amending round 2 item 14).** An announcement
    date that the program's equity calendar marks as an early close, early halt or closure is excluded:
    no trade. In the window these are 2025-07-03 and 2026-04-03 (K9-anncday-01, Exclusions). F (15
    minutes before an early close; D9.1, D9.13) still governs any position open at an unscheduled halt.
  - Nothing is read from embargo, holdout-2 or holdout-1 dates.
- **C5 Weekly cap (D-wk).** At most two entries per member per product per Monday-Friday week, by trade
  date. A third and later signal in the week is skipped (first come, first taken).
- **C6 Guarded fills (D9.5a) and the CPI window (D9.12).** Every entry fills at 18:00 CT (C3) and every
  exit at 14:59 CT (early-close dates are excluded, C4). No release that concerns the equity
  index (Employment Situation, CPI, PPI and GDP at 07:30 CT; ISM at 09:00 CT; FOMC statement at
  13:00 CT) falls in [release, release + 2 min) of either fill, and no opening fill falls in
  [CPI - 5 min, CPI + 5 min]. Positions held through a release are governed by D9.5 (size).
- **C7 Size.** q_c of the D2 vehicle: MNQ 1 (0.1 lot-equivalent), M2K 3 (0.3), MYM 3 (0.3). Never
  above 1 lot-equivalent (D9.5). No member sizes by signal.
- **C8 External series and look-ahead (withdrawn drafts only; the active member reads none).**
  - **VIX, in order (round 2 item 4).** (1) CBOE's official VIX close for day t: "post-2003, the VIX
    Close is timed at 4:15pm" (C-K9R-001-12), that is 15:15 CT. Its publication before the entry
    intent (17:59 CT) is **[unverified]** and is verified in E.12. (2) If it is not reliably available
    by then, the sourced fallback is the 3:45 pm ET (14:45 CT) VIX value, whose daily change the source
    tests in Table A1: "Daily changes in VIX are used to measure sudden changes in VIX, using Intraday
    VIX measured at 3:30 pm, 3:45 pm, 4:00 pm, and the CBOE close, respectively." (C-K9R-001-25); at
    the 1.0 cutoff the 3:45 pm column gives 36.6 days a year, 10.62 bps, t 2.12 (row C-K9R-001-26).
    The fallback needs intraday VIX values; a free history for them is **[unverified]** (Q18). Each
    value is used only after its own time stamp.
  - The VX futures item belongs to the withdrawn K9-vixback-01 (Appendix A).
- **C9 Event calendar EC-K9** (official pages, catalog/ folder; section 8 rows CAL-*). Research window
  2025-04-01..2026-06-19. The October-November 2025 lapse in appropriations is visible in the pages:
  the BLS archives list "October 2025 Employment Situation – Not published because of 2025 lapse in
  federal government appropriations" (CAL-BLS-1; CPI and PPI likewise, CAL-BLS-2, -3), and the BEA
  archive lists a "3rd Quarter 2025 (Initial Estimate)" and an "(Updated Estimate)" in place of the
  advance, second and third estimates (CAL-BEA-1, -2). BLS dates come from the archive file names
  (MMDDYYYY), confirmed for the three shutdown-period releases by their embargo lines (CAL-BLS-4 to -6).

  | Release (time CT) | Dates in the research window (actual release dates) | n | Page |
  |---|---|---|---|
  | FOMC statement (13:00) | 2025-05-07, 06-18, 07-30, 09-17, 10-29, 12-10; 2026-01-28, 03-18, 04-29, 06-17 | 10 | Fed calendar (the 2025-08-22 notation vote on the longer-run strategy statement is not a meeting and is not counted, CAL-FED-3) |
  | Employment Situation (07:30) | 2025-04-04, 05-02, 06-06, 07-03, 08-01, 09-05, 11-20, 12-16; 2026-01-09, 02-11, 03-06, 04-03, 05-08, 06-05 | 14 | BLS archive (October 2025 not published) |
  | GDP first and last estimate (07:30) | 2025-04-30 (Q1 advance), 06-26 (Q1 third), 07-30 (Q2 advance), 09-25 (Q2 third), 12-23 (Q3 initial), 2026-01-22 (Q3 updated), 02-20 (Q4 advance), 04-09 (Q4 third), 04-30 (2026Q1 advance) | 9 | BEA archive and 2026 schedule. 2026Q1's third estimate is 2026-06-25, after the window |
  | GDP second estimates (07:30; the withdrawn K9-vixspike-01's exclusion set only) | 2025-05-29, 08-28; 2026-03-13, 05-28 | 4 | BEA |
  | ISM Manufacturing PMI (09:00) | 2025-04-01, 05-01, 06-02, 07-01, 08-01, 09-02, 10-01, 11-03, 12-01; 2026-01-05, 02-02, 03-02, 04-01, 05-01, 06-01 | 15 | ISM calendar: 2026 live page; 2025 from the 2025-10-09 capture. These are **scheduled** dates ("released on the first business day of the month", CAL-ISM-1; January 2026 moved to the 5th, CAL-ISM-2); that each release occurred on its scheduled day is **[unverified]** (ISM is private and was not affected by the lapse; round 2 item 11c) |
  | Inflation: earlier of CPI and PPI, by reference month (07:30) | 2025-04-10, 05-13, 06-11, 07-15, 08-12, 09-10 (PPI), 10-24, 12-18; 2026-01-13, 02-13, 03-11, 04-10, 05-12, 06-10 | 14 | BLS archives. No October 2025 CPI or PPI. Pairing by reference month is the lead's ruling (round 2 item 11a); release-month pairing would add 2025-11-25 and is not used |

  - **R-12 exclusions.** Two dates fall on equity-index holiday sessions and are excluded: 2025-07-03
    (Employment Situation; early halt) and 2026-04-03 (Good Friday, Employment Situation; abbreviated
    session). The E.2a equity calendar (reports/stage_e2a_calendar_sources.md lines 136-151) lists the
    window's other early halts and closures (2025-04-18, 05-26, 06-19, 07-04, 09-01, 11-27, 11-28,
    12-24, 12-25; 2026-01-01, 01-19, 02-16, 05-25, 06-19); none holds an announcement date. After R-12
    the date set has **58** dates.
  - **R-07 flags.** Dates moved by the October-November 2025 lapse in appropriations are
    **[unverified: date announced before the entry intent]**: Employment Situation 2025-11-20,
    2025-12-16, 2026-02-11; CPI 2025-10-24, 2025-12-18 (the rulings' list); and the BEA GDP dates
    2025-12-23, 2026-01-22, 2026-02-20, 2026-04-09 (writer's addition, see K9-anncday-01). Under
    reference-month pairing no rescheduled PPI release sets an inflation date: each came after its
    month's CPI (September PPI 2025-11-25, November 2026-01-14, December 2026-01-30, January 2026-02-27).

- **C10 Frequency arithmetic (no price data).** 316 trade dates in the research window (299 after
  roll-blackout and UR-1 exclusions). A source rate r per year converts as r / 252 per trade date
  (the source's own year: HPWZ's "All Days" row has 5,965 observations over September 1994 to May
  2018, C-K9R-001-22, 252 a year). The weekly-cap effect is computed under independence of signal
  days (binomial, five trade dates a week); clustering of signal days lowers the after-cap count
  below that figure, by an amount the catalog cannot measure without price data.
- **C11 Cost wall, by the ratio route (rulings).** The member's documented mean move per trade,
  divided by the source's own mean absolute daily move (or 0.798 x its daily standard deviation), is
  set against M_X / E|m_1| and G(f) / E|m_1| (ticks per contract; design target (a) and
  cost_wall.json). E|m_1| is the vehicle's mean absolute **day-session** (O_X to C_X) move; the
  members hold about 21 hours, close to close. A close-to-close move is larger than a day-session move,
  so using E|m_1| as the scale understates the member's expected move in ticks: the comparison is
  conservative for the member.

  | Vehicle | q_c | eps_X | RT_X | E\|m_1\| (context) | M_X / E\|m_1\| | G(0.2) / E\|m_1\| | G(0.1) / E\|m_1\| |
  |---|---|---|---|---|---|---|---|
  | MNQ | 1 | 170 | 5.41 | 726.92 | 0.022 | 1.18 | 2.35 |
  | M2K | 3 | 50 | 6.35 | 212.27 | 0.090 | 1.21 | 2.39 |
  | MYM | 3 | 56 | 7.52 | 262.30 | 0.086 | 1.10 | 2.16 |

  M2K's eps_X is the operative 50 (design target (a), D3); the vehicles table prints the translated 56.
  G(f) at each member's own f = eps_X / f + RT_X is computed in the entry.
- **C12 Payout paths (F9.1, F9.2), arithmetic only.** Standard: "Payout eligibility 5 winning days of
  $150+". Consistency: "Consistency = Largest Winning Day ÷ Total Net Profit", target 40%.
  - A $150 day at q_c needs 300 ticks per contract on MNQ (0.41 x E|m_1|), 100 on M2K at 3 contracts
    (0.47 x E|m_1|) and 100 on MYM at 3 contracts (0.38 x E|m_1|).
  - **Standard path:** a member trading about once a week supplies at most one qualifying day a week.
    Five qualifying days take at least five weeks; if a share s of trips clears $150, about 5 / s
    weeks (s = 0.5: 10 weeks; s = 0.25: 20 weeks). s is unknown without price data.
  - **Consistency path:** total net profit must reach 2.5 x the largest winning day. A session hold's
    winning day is of the order of E|m_1| per contract (MNQ about $363 at q_c, M2K $318, MYM $393),
    while the documented edge per trip is about 0.15 x E|m_1| (K9-anncday-01, by its support source's
    ratio, C11). In expectation total profit grows by about 0.15 x E|m_1| a trip, so reaching 2.5 x one
    typical winning day takes of the order of 17 trips, that is about 17 weeks at one trip a week,
    before variance. A single K9 member pays out slowly on either path; its role is as a component
    of a combination (design target (a), reading 2).
- **C13 Source overlap (NULL_CRITERIA_E section 3).** A member is "source-overlap" if any supporting
  source's sample overlaps its confirmation window [S_X, 2024-02-29], S_X no earlier than 2019-05-06.
  Each entry also states overlap with holdout-2 (2024-04-01..2025-03-31) and the research window
  (2025-04-01..2026-06-19).

Passage ids: P-* are the research readers' passages (as logged); C-* are passages this writer
extracted from the same saved files; CAL-* are calendar-page passages. All are in section 8.

---

## 1. Members

### K9-anncday-01 (macro-announcement-day premium: long the announcement trade date)

- **Status:** active; the only active K9 member after round 3 (R-01). R-02 is a user decision (design
  draft K9-G): cut it for consistency with E.0's K1 exclusion, or keep it (the lead recommends keep).
- **Cluster and exposures.** K9. MNQ\* (q_c 1), M2K\* (q_c 3), MYM\* (q_c 3). Evidence on the US stock
  market (index unnamed in the survey), transferred.
- **Mechanism.** A premium for bearing scheduled macroeconomic news risk. "In this period, on average,
  44 trading days per year have significant macroeconomic announcements. At the daily level, the
  average stock market excess return is 10.68 basis points (bps) on announcement days and 0.93 bps on
  days without major macroeconomic announcements. As a result, the cumulative excess stock market
  return on the 44 announcement days averages 4.65% per year, accounting for about 71% of the annual
  equity premium (6.59%)." (P-K9C-003-a). Table 1: "Ann 44 10.68 bps 4.65% 5.36", "FOMC 10 17.61 bps
  1.74% 4.71", "Non-FOMC 34 8.65 bps 2.91% 3.71" (P-K9C-003-b). Recent: "from January 2020 to August
  2023, the average announcement premium was 16.33 basis points per announcement, higher than the
  full sample average of 10.68 basis points." (P-K9C-003-e).
  - **Support:** "The average announcement day excess return from 1958 to 2009 is 11.4 basis points
    versus 1.1 basis points for all the other days, suggesting that over 60% of the cumulative annual
    equity risk premium is earned on announcement days. The Sharpe ratio is ten times higher."
    (P-K9C-001-a); "In the 1961-2014 period, during the thirty days per year with significant
    macroeconomic announcements, the cumulative excess returns of the S&P 500 index averaged 3.36%,
    which accounts for 55% of the total annual equity premium of 6.19%." (P-K9C-002-a, first part).
  - **Evidence status:** full text (NBER w31923, revised December 2023; a survey with an updated
    sample). Savor-Wilson (JFQA 2013) and Ai-Bansal (Econometrica 2018) full text.
- **Rare condition and decision time.**
  - **Date set (extracted).** "The announcements are the FOMC, Non-farm payroll, GDP (first and last),
    ISM manufacturing PMI, and the earlier of the CPI and PPI announcements." (P-K9C-003-c). Inflation
    rule: "We combine the PPI and CPI announcements into one “inflation” announcement by using the
    earlier one each month, as they reveal information of a similar nature. This additional step
    becomes necessary because in recent years the CPI announcement starts to regularly occur before
    the PPI announcement" (P-K9C-003-d).
  - **Return window.** "This table documents the average excess return of the U.S. stock market during
    the 1961-2023 period." (C-K9C-003-1); "At the daily level" (C-K9C-003-2). The survey does not state
    the window beyond "daily"; Savor-Wilson's returns are one trading day, close to close (reader's log
    entry K9C-001). The member reads it as close to close.
  - **Mapping to the 2025-2026 calendar (round 2 item 11):** FOMC = statement day of each
    scheduled meeting; NFP = Employment Situation release day; GDP first = advance estimate, last =
    third estimate, and for 2025Q3 (no advance, second or third estimate) first = "Initial Estimate"
    2025-12-23 and last = "Updated Estimate" 2026-01-22; inflation = the earlier of CPI and PPI per
    reference month (14 dates); ISM dates are scheduled dates, [unverified] as actual.
  - **Member condition:** trade date d is in the EC-K9 date set (C9: 60 dates; 58 after the R-12
    exclusions).
  - **Decision time (R-07):** known in advance from the official schedules, except the dates the
    October-November 2025 lapse in appropriations rescheduled, which are **[unverified: date announced
    before the entry intent]**: Employment Situation 2025-11-20, 2025-12-16 and 2026-02-11; CPI
    2025-10-24 and 2025-12-18 (both set the inflation date; no rescheduled PPI release sets one, C9).
    The writer adds, on the same reading, the BEA GDP dates 2025-12-23 and 2026-01-22 (the 2025Q3
    "Initial" and "Updated" estimates exist only because of the lapse) and 2026-02-20 and 2026-04-09
    (the 2025Q4 advance and third estimates, later than BEA's usual late-January and late-March slots;
    an inference from the usual pattern). E.11 fetches BLS's revised-schedule notice (and BEA's, for
    the GDP dates) and keeps a date only if its announcement precedes the entry intent (17:59 CT the
    evening before); otherwise the date is dropped. **E.12's harness uses the date set as known at the
    entry intent.** No released value is read.
- **Signal:** calendar membership only.
- **Entry rule:** BUY q_c by market intent on the 17:59 CT bar of the evening before the announcement
  trade date d, filling at the 18:00 CT open (Sunday 17:59 / 18:00 CT when d is a Monday): D-entry as
  amended for D9.4 (round 2 item 5; the source measures from the prior close).
- **Exit rule:** intent at 14:58 CT on d, fill 14:59 (D-exit). Early-close, early-halt and closure
  dates are excluded (R-12); F still governs any position open at an unscheduled halt. The hold
  contains the release.
- **Holding horizon:** about 21 h (18:00 to 14:59 CT); inside trade date d; flat by F.
- **Exclusions (in addition to C4; R-12, amending round 2 item 14):** an announcement date that the
  program's equity calendar marks as an early close, early halt or closure: no trade. In the window:
  2025-07-03 (Employment Situation; "| 2025-07-03 | Day before Independence Day | early_halt | 12:15 |
  cme | inferred |", CAL-E2A-1) and 2026-04-03 (Good Friday, Employment Situation; "| 2026-04-03 | Good
  Friday (abbreviated, jobs report) | early_halt | 08:15 | cme | empirical |", CAL-E2A-2). The window's
  other equity holiday sessions hold no announcement date (C9). Trade dates that follow a holiday
  session but are regular themselves (2025-09-02 ISM after Labor Day; 2025-12-01 ISM after
  Thanksgiving) are kept.
- **Exclusion-list check (X1-X15).**
  - X1, X2, X3, X5, X7, X8, X9, X10, X11, X13, X14, X15: no.
  - **X4 (pre-release drift): admissible (ruling).** "No pre-release move is read; the trade is
    unconditional on price."
  - **X6 (post-FOMC continuation): admissible (ruling).** "No post-FOMC move is read, and FOMC is one
    date type among six." Risk: the FOMC days carry the largest per-day premium in the source
    (17.61 bps) and the pre-FOMC drift is a non-survivor (K9C-007).
  - **X12 (month-end flows): admissible with a flag (ruling).** "The date set is keyed to release
    calendars, not the day of the month. K9C-004's day-of-month confound is the main falsification
    risk and is quoted in the entry." ISM falls on the first business day and Employment Situation
    usually on the first Friday, so about half the dates sit at the turn of the month.
  - **D.1's E-H1 and E.0's K1-predrift-01 exclusion (round 3, R-02): ruled; the member stays.** E.0
    excluded K1-predrift-01 because "this is MES's scheduled-macro-drift family (E-H1/E-H2, class C5,
    null on MES under docs/NULL_CRITERIA.md) re-run on the Dow, a sibling index highly correlated with
    the S&P; the K1 brief allows MES families only through the core ports." (K1-E0). D.1's E-H1 went
    long MES into FOMC, CPI and NFP releases, stopping at the release. The lead's four grounds that this
    does not bind K9-anncday-01:
    1. The frozen design leaves announcement members to each cluster's own literature. D6 lists among
       the families not ported "E calendar and events (each cluster writes its own announcement members
       from its own literature, which is more specific than MES's E-H1)" (DS-D6, docs/STAGE_E_DESIGN.md
       line 381). This member comes from its own literature (Ai-Bansal-Guo; Savor-Wilson).
    2. E-H1's D.1c verdict on MES was a non-resolution (underpowered), not a null. The hypothesis was
       not rejected, so re-testing a related one does not repeat a failed family.
    3. The member differs from E-H1 in date set (six release types, including GDP, ISM manufacturing
       and PPI when earlier, against FOMC, CPI and NFP), in hold (the whole announcement day, including
       the release response, against a stop at the release), in exposures (three traded equity
       indices; MES is not traded in Stage E) and in source.
    4. The K1-predrift-01 exclusion rested on the E.0 K1 brief, which allowed MES families in K1 only
       through the core ports. That brief does not govern K9, and the E.10 prompt scopes the exclusion
       list to families Stage E tested.

    **Risk and user decision (design draft K9-G):** cut K9-anncday-01 for consistency with E.0's K1
    exclusion, or keep it (the lead recommends keep). Correction recorded by the lead: X4's "Members
    tested" cell lists K1-predrift-01, which was excluded at E.0 with 0 trials and never screened; only
    K2-predrift-01 was tested. X4's mechanism exclusion is unchanged.
  - "D9.12 (CPI window) does not bite, because the entry fill is at 17:00 CT the evening before."
    (ruling). Under round 2 item 5 the entry fills at 18:00 CT the evening before; the point holds.
- **Data fields read.** EC-K9 date set; vehicle ohlcv-1m at the 18:00 CT bar and 14:59 CT (intents on
  the 17:59 and 14:58 bars).
- **Order type:** market. **Sizing:** q_c.
- **Parameters.**

  | Literal | Value | Source or rule |
  |---|---|---|
  | Date types | FOMC, NFP, GDP first and last, ISM manufacturing, inflation (earlier of CPI and PPI) | P-K9C-003-c, -d |
  | Inflation pairing | earlier release per reference month | P-K9C-003-d; round 2 item 11a |
  | 2025Q3 GDP | initial 2025-12-23 (first), updated 2026-01-22 (last) | CAL-BEA-1, -2; round 2 item 11b |
  | Hold | the announcement trade date, close to close | C-K9C-003-1, -2; K9C-001 |
  | Entry, exit | intent 17:59 CT, fill 18:00 CT (evening before d); intent 14:58, fill 14:59 | D-entry amended (round 2 item 5; a user decision, design draft K9-H, R-06); D-exit |
  | Holiday sessions | announcement dates on an equity early close, early halt or closure excluded | R-12 (amends round 2 item 14) |
  | Rescheduled dates | kept only if announced before the 17:59 CT entry intent (E.11 check) | R-07 |
  | Direction, size | long, q_c | P-K9C-003-a; (b)7 |
  | Weekly cap | 2 per week | D-wk |

- **Expected frequency (official calendars, C9; recounted in round 3).**
  - Union in the 316-date window: 10 + 14 + 9 + 15 + 14 = 62, less 2 same-day overlaps (2025-07-30
    FOMC and GDP; 2025-08-01 NFP and ISM) = 60 dates. Inflation paired by reference month (round 2 item
    11a).
  - **After R-12** (2025-07-03 and 2026-04-03 excluded): **58 dates before the cap; 56 after the D-wk
    cap.** Two weeks hold three dates (2025-04-28: GDP, ISM, NFP; 2026-04-27: FOMC, GDP, ISM); the third
    is skipped (2025-05-02 NFP, 2026-05-01 ISM). Scaled to the 299 screened dates: **54.9 before the
    cap, 53.0 after.**
  - **Worst case (R-07 flagged dates dropped as well):** dropping the five BLS dates the rulings list
    gives 53 before and 51 after the cap (50.1 / 48.3 scaled to 299). Dropping also the four BEA GDP
    dates gives **49 before and 47 after the cap (46.4 / 44.5 scaled)**, still above the 40-trip margin
    of (b)1. The rulings estimated "about 50 dates before the cap, about 47 scaled".
  - These counts replace the round-1 "about 52" (round 2 item 12), which was the source's 1961-2023
    average (44 a year x 299 / 252); the 2025-2026 calendar has more announcement days.
  - Roll-blackout and UR-1 dates are excluded at screening and are not identified here.
- **Target move against M_X and G(f) (ratio route).**
  - **K9C-003 (main):** 10.68 bps per announcement day, 1961-2023 (16.33 bps, 2020-01 to 2023-08), in
    the source's units (daily excess return of the US stock market). The survey reports no mean
    absolute or standard deviation figure: **[no conversion available]**.
  - **K9C-001 (support):** 11.4 bps with "The standard deviation of announcement day returns is 98.6
    bps versus 94.6 bps for other days" (C-K9C-001-1; Table 1 "Std. Dev. 98.6 94.6 81.8 75.4",
    C-K9C-001-2). Ratio = 11.4 / (0.798 x 98.6) = **0.145**, labelled: the support source's own date set
    (CPI/PPI, employment, FOMC, 1958-2009), not K9C-003's (round 2 item 13).
  - Against M_X / E|m_1|: clears on all three (6.5x MNQ, 1.62x M2K, 1.68x MYM). Against G(f) at
    f = 56 / 316 = 0.177 (after R-12 and the cap): 1.33 (MNQ), 1.36 (M2K), 1.23 (MYM): the move is
    about one ninth of the eps bar.
- **Conflicting evidence (quoted).**
  - **Day-of-month confound (main risk):** "Including the day-of-the-month fixed effects lowers the
    average macroeconomic announcement fixed effect. Though the announcement fixed effects’ point
    estimates remain economically meaningful on average, they lose their joint statistical
    significance in the presence of the day-of-the-month fixed effects." (P-K9C-004-b);
    "macroeconomic announcements happen to occur on days with high average market returns, and may not
    in and of themselves be special." and "Controlling for the day-of-the-month fixed effects, the
    macroeconomic announcement fixed effects show that macroeconomic variables as a whole account for
    56% of the equity premium." (P-K9C-004-c).
  - **Pre-FOMC drift gone:** "the pre-FOMC drift essentially disappeared after 2015 in both
    announcements accompanied by press conferences and announcements not accompanied by press
    conferences" (P-K9C-007-a, verified with line-break hyphenation).
  - **FOMC premium low 2016-2019:** "the premium for the FOMC announcement was low between January 2016
    and December 2019 and attribute the decline to reduced uncertainty over this period." (P-K9C-003-e,
    first part).
- **Falsification.** The standard condition and the 30-trip floor; reported: trips by date type (FOMC,
  NFP, GDP, ISM, inflation; FOMC versus non-FOMC); **the day-of-month split:** each trip's
  trading-day-of-month index is reported, with the mean trip P&L for dates in the first five trading
  days of the month against the rest (descriptive; K9C-004's confound); the mean P&L of the same
  exposure on non-announcement trade dates held the same way is reported as the benchmark the
  premium must exceed.
- **Topstep check.**
  1. Flat by F: last fill 14:59. 2. Market orders only. 3. D9.3: at most 2 a week, holds about 21 h.
  4. D9.4: entries fill at 18:00 CT, 60 minutes after the reopen, including the Sunday evenings before
     the Monday dates (2025-06-02, 11-03, 12-01; 2026-01-05, 02-02, 03-02, 06-01) (round 2 item 5; a user decision under R-06, design draft K9-H). 5. **News (D9.5):** every trip holds through a scheduled
     release by design, at q_c <= 0.3 lot-equivalent, never the full maximum: compliant with "Topstep
     doesn't require you to flatten positions during economic releases" [F6.1] and the full-size
     prohibition [F6.3]. 6. D9.5a: fills at 18:00 and 14:59 CT, clear of
     07:30, 09:00 and 13:00 CT releases. 7. D9.12: no opening fill in [CPI - 5, CPI + 5] (the opening fill is the evening
     before). 8. D9.6: 1 or 3 micros. 9. D9.7: recorded. 10. D9.13: early-close, early-halt and closure dates are
     excluded (R-12).
  11. Payout (C12).
- **Member-level coverage:** vehicle bars at 18:00 and 14:59 CT >= 0.95.
- **Data needed:** vehicle bars; EC-K9 for the research window (built here) and for the confirmation
  window [S_X, 2024-02-29] (not built here; same pages' archives).
- **Source window and label.** K9C-003: 1961-2023 (Table 1), with the January 2020 to August 2023
  sub-sample (P-K9C-003-e). K9C-001: 1958-2009 (stocks). K9C-002: 1961-2014. K9C-003 **overlaps the
  confirmation window** (2019-05-06..2024-02-29). It does not overlap holdout-2 (it ends 2023-08) or
  the research window. **Label: source-overlap.** "An edge cannot be claimed without a registered
  holdout read (NULL_CRITERIA_E section 3)." (ruling). The excluded pre-announcement variant's source (HPWZ,
  to May 2018) is not source-overlap (section 2; R-08).
- **Trials in N:** 3.

---

## 2. Excluded members

The lead's rulings, with each "cost wall" reason restated by the ratio route or marked [conversion
unverified] where the source gives no daily volatility figure (the original per-trade-date bp and tick
figures were the readers' round-price conversions). No round-1 exclusion decision changes. Round 2 adds
K9-vixback-01 (items 6-10) and restates the Treasury row (item 15). Round 3 adds K9-vixspike-01 (R-01) and
amends the pre-announcement row (R-02, R-08).

| Candidate | Sources | Reason (check failed) |
|---|---|---|
| **K9-vixback-01** (VIX-futures backwardation state, long the next trade date; full draft in Appendix A) | K9R-004 (P-K9R-004-a, -b, -c, -d; C-K9R-004-1 to -19); conflict K9R-005 (P-K9R-005-a) | **Excluded in round 2 (items 6-10), two reasons.** (a) Shape, consistent with the TSMOM ruling: backwardation states persist for days or weeks, so the weekly cap picks days arbitrarily, and the capped count is anywhere from about 24 to 56. (b) Evidence at the member's horizon: at K = 1 day only D1-D2 (bottom 10%) are significant (C-K9R-004-9 to -12; P-K9R-004-d's "significant in all cases" holds at 1 month and 1 quarter), and a 10% cut gives about 30 trips before the cap, below the 40-trip expectation. Candidate feature for V20's ML route v2. Its data item (seven nearest VX closes plus spot VIX) stays in Appendix A |
| **K9-vixspike-01** (uncertainty premium after an unscheduled VIX spike, long the next trade date; full draft in Appendix B) | K9R-001 (P-K9R-001-b to -h; C-K9R-001-*); context K9R-002, K9R-003; conflicts K9R-007, K9R-008, K9R-012, K9R-014 | **Withdrawn in round 3 (R-01): it fails the design target's pre-declared X10 borderline test.** The test admits a volatility-spike member only if "the condition reads a volatility level, not the sign of the last move" (DT-2); the condition is a one-day change in VIX, and the source states "although the correlation between daily returns and daily changes in VIX is close to −70%, the information contents of these two variables are not the same" (C-K9R-001-28). Its Table 8 shows next-day returns after large price drops alone that are positive, of comparable or larger size, statistically insignificant on 5-16 days a year (C-K9R-001-27, -29, -24). The source's own data therefore do not separate the uncertainty premium from a reversal of the spike-day fall; reading "level" to cover a one-day change would relax a pre-declared test after reading the source. The user may reinstate it at E.11 (Appendix B, Reinstatement conditions) |
| Pre-announcement overnight long (reopen to release - 5 min, NFP/ISM/GDP) | K9R-001 / K9C-006 | Variant of K9-anncday-01: same mechanism, a subset of the same dates, the hold window as a parameter (no-grids rule). **Further reason (R-02): its window is D.1's E-H1 window** (long into the release, stopping at it), so it would re-run E-H1's window on the same research window as MES. The source's sub-period statement (R-08, replacing "weak"): "By contrast, the performance of the non-FOMC macro announcements remains stable and significant across all three subperiods. In particular, during the last subperiod of 2012–2018, the pre-announcement return is on average 6.98 basis point and statistically significant for the non-FOMC macro announcements" (P-K9C-006-e). **For the user's comparison (R-08):** (i) the variant's source (HPWZ, sample to May 2018) is **not source-overlap**, while K9-anncday-01 is; (ii) the segment the member adds after the release is, in the source, "small and insignificant" with "large variances": "Post announcement, the average returns for NFP, ISM, and GDP are small and insignificant, while exhibiting large variances" (P-K9C-006-c). Offered to the user as K9-anncday-01's alternative literal set; the lead recommends the full-day member (design draft K9-G) |
| Long equity after a large prior-day shock (moderate shocks) | K9R-019 | Rule 1: abstract only, threshold and sample unknown. Conflict K9R-014 (ES daily autocorrelation about zero) |
| Continue the prior day in calm volatility states | K9R-012, K9R-013 | Evidence: older cash-index data, contradicted in S&P futures after 1993 (K9R-014). Also X3-adjacent |
| MCL continuation after a 2-SD day | K9R-017 | Frequency: about 15 a year, under the 10% floor. Data from a non-exchange feed, exits fitted |
| Range compression or inside-day direction | R3 | No academic source gives a direction (R3 saturation). A compression-gated breakout is X2 |
| European-open overnight drift (closing-flow or late-VIX conditioned) | K9O-001, K9O-003 | Non-survivor: the authors report it near zero since 2021 in ES, NQ and YM (K9O-002). The flow version needs signed volume, which the bars lack |
| 12-month TSMOM held overnight only, in a trend state | K9O-004, K9O-005, K9O-009 | Shape: the trend state persists for weeks, so the weekly cap would pick days arbitrarily, and the Bear state yields about 20 capped trips. Kept for V20's ML route v2 as a feature |
| 6E time-of-day pattern; MGC Asian-session premium | K9O-010/011; K9O-013/014 | Shape: no sourced condition (every day); X9-adjacent (fix-driven) |
| Bitcoin Monday long | K9C-014, K9C-015 | Evidence: 2013-2017 only, with per-year sign reversals (P-K9C-014-c). No later evidence |
| Futures weekend effect | K9C-016 | Rule 1: abstract only, products unknown. Equity weekend effect gone (K9C-017, K9C-018) |
| Pre-FOMC drift; FOMC-day FX; FOMC-cycle weeks; pre-holiday; options-expiration week; Halloween | K9C-005/007/010/008/009/020/021/022 | Frequency below the floor and/or non-survivor; option expiry is X13-adjacent |
| Treasury announcement-day premium | K9C-001 (bonds), K9C-011 | **Kept; reasons in order (round 2 item 15).** (1) The bond premium's only full-text evidence ends before 2010 (K9C-001's Treasury sample, 1961-2009). (2) "insignificant after 2008" is abstract only (K9C-011). (3) The cost wall is **[conversion unverified]**: the source's figure in its own units is "For 5-year bonds, the return di¤erential is 2.6 bps (t-statistic = 2.57), and it then grows to 3.4 bps (t-statistic = 2.23), 4.1 bps (t-statistic = 2.04), and 4.5 bps (t-statistic = 2.02) for 10-, 20-, and 30-year bonds respectively." (P-K9C-001-d), with "a moderate level of announcement premiums for Treasury bonds, which averages about 3 bps" (P-K9C-002-d); no daily standard deviation of bond returns was located, so it cannot be set against M_X (M_X / E\|m_1\| 0.21-0.28 on ZT-UB) |
| Scarcity-state carry (storage, basis) | K9M-001/002/004/005/007/008 | **Restated.** Source figures in their own units are annual long-short portfolio premia (log numeric claims, not re-verified here: 8.06%/yr low-minus-high inventory, P-K9M-001-c; within-class carry Sharpe 0.7, P-K9M-002-d; 9%/yr, P-K9M-004-b; 18.38%/yr, P-K9M-005-b; 6.93%/yr, P-K9M-008-a). No single-commodity daily volatility is given, so the comparison with M_X is **[conversion unverified]**. The exclusion leans on: faster rebalancing lowers returns (P-K9M-003-c); needs deferred-contract bars; the evidence is monthly |
| FX carry earned in the US session | K9M-010, K9M-011 | **Restated.** Source figure: carry 3.25%/yr intraday versus 1.12%/yr overnight (P-K9M-010-d, log figure): **[conversion unverified]**. The exclusion leans on: no rarity condition; X9-adjacent |
| NG long after an extreme cold forecast | K9M-017 | Evidence is a 5-day NG1/NG2 spread, not an outright session hold. Needs NOAA GEFS forecast history |
| New-crop corn weather-premium short | K9M-019/021/022 | **Restated.** Source figure: a 12% average decline June to December, 2000-2020 (P-K9M-019-a, log figure), a seasonal figure in the source's units: **[conversion unverified]**. The exclusion leans on: passive short not attractive (P-K9M-021-c); X8 risk; the signal sits in the new-crop (deferred) December contract |
| Calendar-month commodity seasonality | K9M-013, K9M-014 | Evidence: no out-of-sample gain (K9M-014) |

---

## 3. Beyond budget

None. 3 of 40 trials are used; nothing was dropped for budget. Not written: the pre-announcement window
(offered to the user as K9-anncday-01's alternative literal set). K9-vixback-01 (Appendix A) and
K9-vixspike-01 (Appendix B) were withdrawn on shape, evidence and the X10 test (section 2), not on
budget.

---

## 4. Routed

| Item | To | Note |
|---|---|---|
| 12-month TSMOM trend state (K9O-004/005/009) | V20 ML route v2 | as a feature (ruling) |
| Pre-announcement overnight long (K9R-001 / K9C-006) | the user | offered as K9-anncday-01's alternative window (ruling) |
| K9-vixback-01 (withdrawn draft, Appendix A) | V20 ML route v2 | candidate feature (round 2 items 6-10) |
| K9-vixspike-01 (withdrawn draft, Appendix B) | the user, at E.11 | reinstatable on the conditions in its entry (R-01) |
| D-entry at 18:00 CT (17:59 intent) | the user, design draft K9-H | R-06; alternative: the 17:00 CT first bar |
| BLS (and BEA) revised-schedule notices | E.11 | R-07: keep a rescheduled date only if announced before the 17:59 CT entry intent |
| VIX official daily close; 3:45 pm ET VIX value (fallback); only if Appendix B is reinstated | E.11/E.12 | new external series; the close's publication before 17:59 CT is verified in E.12 (round 2 item 4); a free intraday history for the fallback is [unverified] (Q18) |
| HPWZ JFE 2022 version | closed (R-11) | the author manuscript states the same sample; matters only if Appendix B is reinstated |
| EC-K9 for the confirmation window | E.11/E.12 | the same official archives (BLS, Fed, BEA, ISM) back to 2019 |

---

## 5. Log accounting

88 sources (regime 25, calendar 22, overnight 19, commodity 22). Dispositions are the lead's rulings;
this writer opened only the entries the rulings name.

| Items | Disposition |
|---|---|
| K9R-001 (= K9C-006, same paper) | Withdrawn draft K9-vixspike-01 (Appendix B; R-01). Its pre-announcement half is an excluded variant (P-K9C-006-c, -e quoted in section 2) |
| K9R-002, K9R-003 | Context for the withdrawn K9-vixspike-01 (Appendix B) |
| K9R-004 | Withdrawn draft K9-vixback-01 (Appendix A); excluded in round 2 (section 2) |
| K9R-005 | Conflict for the withdrawn K9-vixback-01 (quoted in Appendix A) |
| K9R-008, K9R-012, K9R-014 | Conflicts for the withdrawn K9-vixspike-01 (Appendix B) |
| K9R-013, K9R-017, K9R-019 | Excluded rows |
| K9R-006 | Read in round 2 after selection; monthly horizon; not used (R-03) |
| K9R-007 | Conflict for the withdrawn K9-vixspike-01 (Appendix B; round 2 item 17) |
| K9R-009 to -011, -015, -016, -018, -020 to -025 | Not named in the rulings: no member, no exclusion row |
| K9C-001, K9C-002 | Support for K9-anncday-01 (quoted); K9C-001's bond half is an excluded row |
| K9C-003 | **Used:** K9-anncday-01 |
| K9C-004, K9C-007 | Conflicts for K9-anncday-01 (quoted) |
| K9C-005, -008 to -011, -014 to -018, -020 to -022 | Excluded rows |
| K9C-012, -013, -019 | Not named in the rulings |
| K9O-001 to -005, -009 to -011, -013, -014 | Excluded rows |
| K9O-006 to -008, -012, -015 to -019 | Not named in the rulings |
| K9M-001 to -005, -007, -008, -010, -011, -013, -014, -017, -019, -021, -022 | Excluded rows (K9M-003 cited as the rebalancing reason) |
| K9M-006, -009, -012, -015, -016, -018, -020 | Not named in the rulings |

---

## 6. Trial count table

| Member | Exposure | Vehicle (q_c) | Trials | eps | Expected trips before / after cap | Label | Status |
|---|---|---|---|---|---|---|---|
| K9-anncday-01 | Nasdaq-100 / Russell 2000 / Dow | MNQ (1) / M2K (3) / MYM (3) | 3 | each exposure's eps_X | after R-12: 58 / 56 on the window's trade dates (54.9 / 53.0 scaled to 299); worst case with the R-07 dates dropped 49 / 47 (46.4 / 44.5 scaled) | **source-overlap** | active; R-02 user decision (K9-G) |
| ~~K9-vixback-01~~ | same | same | 0 (3 if reinstated) | | withdrawn (Appendix A) | | excluded, round 2 items 6-10 |
| ~~K9-vixspike-01~~ | same | same | 0 (3 if reinstated) | | withdrawn (Appendix B) | | excluded, round 3 R-01 |
| **K9 total** | | | **3** | | | | |

Budget 40; program N 198 + 3 = **201** (projected). The member is stated under K9 only; K9's Holm
family (D5) contains the trials that pass the K9 screen.

---

## 7. Questions for the lead: answered in round 2

Round-1 questions, each with the lead's answer (rulings file, "Round 2: rulings on CatalogWriter's
section 7", items 1-17).

1. **K9-vixspike-01, the non-announcement filter** (the source's counts appear to include announcement
   days; the filtered member falls below 40 trips). *Answer, item 1:* keep the filter; 37.8-39.7 trips
   before the cap and 36.7-38.4 after, below the (b)1 margin and above the floor; the user decides; the
   no-filter reading (47.1 / 45.1) is recorded and not chosen.
2. **Cutoff unit.** *Answer, item 2:* noted, no change.
3. **K9-vixspike-01 below M_X on the longer sample (M2K, MYM).** *Answer, item 3:* stated as a weakness
   in the entry's cost-wall section; no change.
4. **VIX close publication.** *Answer, item 4:* the official 15:15 CT close, verified in E.12; the
   3:45 pm ET value is the sourced fallback; both written in order (C8 and the entry).
5. **Reopen entries and D9.4.** *Answer, item 5:* every reopen entry is intent on the 17:59 CT bar,
   filling at the 18:00 CT open, weekdays and Sundays (C3).
6. **K9-vixback-01 slope definition and data item.** *Answer, items 6-10:* the member is excluded; the
   definition and data item stay in Appendix A.
7. **K9-vixback-01 percentile window.** *Answer, items 6-10:* moot after the exclusion; both versions
   are kept in Appendix A.
8. **K9-vixback-01 1-day evidence for D3-D4.** *Answer, items 6-10:* reason (b) of the exclusion.
9. **K9-vixback-01 persistence under the weekly cap.** *Answer, items 6-10:* reason (a) of the
   exclusion, consistent with the TSMOM ruling.
10. **VX futures timing.** *Answer, items 6-10:* moot; noted in Appendix A.
11. **K9-anncday-01 calendar mapping.** *Answer, item 11:* reference-month pairing (14 inflation dates);
    2025Q3 Initial and Updated as first and last; ISM dates scheduled, [unverified] as actual.
12. **K9-anncday-01 count.** *Answer, item 12:* 60 dates, 58 after the cap (56.8 / 54.9 scaled to
    299); "about 52" replaced.
13. **K9-anncday-01 ratio route.** *Answer, item 13:* Savor-Wilson's 0.145, labelled as the support
    source's own date set; K9C-003's figure is [no conversion available].
14. **Early-close dates.** *Answer, item 14:* the exit is the forced flatten at F; early-close dates are
    not excluded (C4, both entries).
15. **Exclusions weakened by the restatement.** *Answer, item 15:* the Treasury row is kept with its
    reasons in order; the other three rows keep their independent reasons (section 2).
16. **HPWZ published version.** *Answer, item 16:* "not source-overlap" kept on the NBER sample; the
    JFE 2022 version is re-checked in E.11, and the label flips if its sample runs past 2019-05-06.
17. **Unused VIX sources K9R-006 and K9R-007.** *Answer, item 17:* checked; K9R-006 added as
    monthly-horizon context (P-K9R-006-a) and K9R-007 as conflicting transfer evidence (P-K9R-007-a),
    both verified (section 8).

**New questions after round 2**

18. **Fallback data.** The 3:45 pm ET fallback needs a history of intraday VIX values (the source used
    CBOE VIX tick data from 1992). A free history with that time stamp is [unverified]. If none exists,
    the fallback cannot be backtested and only the official close is usable. E.12 could check both
    with the close's publication time.
19. **K9R-006 and the source-overlap label.** K9R-006's sample (1990-2022) overlaps the confirmation
    window. It entered in round 2 as monthly-horizon context, after the member was chosen, and no
    literal comes from it. Does it count as a "supporting source" under NULL_CRITERIA_E section 3? If
    yes, K9-vixspike-01 becomes source-overlap.
    *Lead ruling (2026-10-02 23:30 PDT):* no. Section 3's test is whether the member "was chosen partly on
    evidence from that window". K9-vixspike-01 was chosen (rulings, 22:55-22:58) and specified (round 1) on
    K9R-001 alone. K9R-006 was read afterwards (round 2, item 17), as context at another horizon, and no
    literal comes from it. It is post-selection context, not a supporting source. The label stays "not
    source-overlap". The user and the reviewer may take the stricter reading, which turns the member
    source-overlap and changes nothing else (the edge chain would then need a registered holdout read).
    *Superseded by round 3, R-03:* K9R-006 is removed from the evidence (fix (a)); the label stands, and
    the member is withdrawn anyway (R-01).
20. **Information, no change proposed.** (a) With the 18:00 CT entry, both members (after round 3, the one active member) miss the 15:00-18:00
    CT part of their sources' close-to-close return (the hour after the cash close, the halt and the
    reopen hour). This is the transfer cost of the D9.4 amendment. (b) K9R-007's size and style result
    suggests K9-vixspike-01's effect is weakest on M2K and MNQ; each trial is screened on its own
    exposure.


**Round 3 (Fable review; reports/stage_e10_catalog_rulings.md)**

- **R-01:** K9-vixspike-01 withdrawn to Appendix B; Excluded-table row added; reinstatement conditions
  (widen the X10 test explicitly, one cutoff, the descriptive reversal diagnostic) in its entry.
- **R-02:** ruling written into K9-anncday-01's exclusion-list check (four grounds; user decision K9-G);
  E-H1 added to the pre-announcement row as a further reason.
- **R-03:** K9R-006 removed from Appendix B's evidence and from the JSON sources; section 5 keeps it as
  read in round 2 after selection, monthly horizon, not used. Q19 is moot.
- **R-04:** Table 8 gloss reworded to "positive, of comparable or larger size, statistically
  insignificant on 5-16 days a year" and moved into Appendix B's X10 paragraph with the -70% sentence.
- **R-05:** the cutoff-selection rule stated in Appendix B; the 0.5 row listed as the alternative.
- **R-06:** the 18:00 CT entry is a user decision (design draft K9-H); the catalog keeps it pending
  (C3, K9-anncday-01). Q20(a) is its transfer cost.
- **R-07:** rescheduled dates flagged [unverified: date announced before the entry intent] in C9 and
  K9-anncday-01's decision time; E.11 and E.12 handling stated. The writer also flagged four BEA GDP
  dates (new Q21).
- **R-08:** pre-announcement row: "weak" replaced by P-K9C-006-e; facts (i) and (ii) added.
- **R-09:** the "40 of 202" derivation restated in Appendix B.
- **R-10:** acknowledged by the lead; no catalog change.
- **R-11:** closed; Appendix B's label note cites the manuscript (R11-1, R11-2). Round-1 Q16 closed.
- **R-12:** announcement dates on an equity early close, early halt or closure excluded (2025-07-03,
  2026-04-03), checked against the E.2a equity calendar; the date set recounted (58 / 56; 54.9 / 53.0
  scaled; worst case 49 / 47, 46.4 / 44.5 scaled).
- **R-13, R-14, R-15:** acknowledged; no catalog change (R-14 matters only if Appendix B is reinstated;
  R-15 confirms Appendix A). Q18 is moot unless Appendix B is reinstated.
- **R-16:** Appendix B states the mixed-sample ratio as conservative.
- **Totals:** 1 active member, 3 trials, projected N = 201 (header, section 6, JSON).

**New question after round 3**

21. **BEA dates under R-07.** The rulings list the BLS dates the lapse moved. The writer also flagged
    four BEA GDP dates (2025-12-23, 2026-01-22, 2026-02-20, 2026-04-09): the 2025Q3 estimates exist only
    because of the lapse, and the 2025Q4 advance and third estimates fell later than BEA's usual slots
    (an inference). Should E.11's check cover BEA's revised schedule as well? The worst case above
    already drops them.
    *Lead answer (reports/stage_e10_catalog_rulings.md, addendum):* yes, under the same rule as R-07.

---

## 8. Verification table

Every quoted passage was grepped in the saved file (script in the writer's scratchpad; normalization:
whitespace runs collapsed, line-break hyphens joined, curly and straight quote glyphs equated where
stated). Line numbers are of the first line of the match in the saved file (raw HTML for .html files).
The "Use" column says where the id or its text appears: the body (sections 0-7), Appendix A or
Appendix B. Rows added in round 2 and round 3 are tagged.

| Passage id | Saved file | Line | Status | Use |
|---|---|---|---|---|
| P-K9R-001-b | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 291 | found with whitespace or hyphenation differences (quote/dash glyphs normalized) | quoted or cited in: body, App. B |
| P-K9R-001-c | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 297 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-001-d | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1588 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-001-e#1 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1609 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-001-e#2 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1610 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-001-f#1 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1619 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-001-f#2 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1620 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-001-h | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 859 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-002-a | reports/stage_e10_research/regime/giot_uclouvain.txt | 19 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-002-c#1 | reports/stage_e10_research/regime/giot_uclouvain.txt | 613 | found verbatim | quoted or cited in: App. B |
| P-K9R-002-c#2 | reports/stage_e10_research/regime/giot_uclouvain.txt | 614 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-002-c#3 | reports/stage_e10_research/regime/giot_uclouvain.txt | 615 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-003-b | reports/stage_e10_research/regime/simon_wiggins_2001_ideas.html | 33 | found verbatim | quoted or cited in: App. B |
| P-K9R-004-a | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 494 | found with whitespace or hyphenation differences | quoted or cited in: body, App. A |
| P-K9R-004-b | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 500 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| P-K9R-004-c | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 523 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| P-K9R-004-d | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 547 | found with whitespace or hyphenation differences | quoted or cited in: body, App. A |
| P-K9R-005-a | reports/stage_e10_research/regime/lubnau_todorova_2015_ideas.html | 33 | found verbatim | quoted or cited in: body, App. A |
| P-K9R-008-a | reports/stage_e10_research/regime/moreira_muir_nber_w22208.txt | 56 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| P-K9R-012-a | reports/stage_e10_research/regime/sentana_wadhwani_1992_ideas.html | 33 | found verbatim | quoted or cited in: App. B |
| P-K9R-014-b (as logged, one piece) | reports/stage_e10_research/regime/bianco_corsi_reno_2009_pnas.txt | - | NOT FOUND | **removed as one piece** (two-column text interleaves "k=1" tokens); re-quoted as .1 and .2 below |
| P-K9C-001-a | reports/stage_e10_research/calendar/savor_wilson_2013_draft.txt | 47 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-002-a | reports/stage_e10_research/calendar/ai_bansal_2018_econometrica.txt | 45 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-003-a | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 100 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-003-b#1 | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 122 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-003-b#2 | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 123 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-003-b#3 | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 124 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-003-c | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 131 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-003-d | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 110 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-003-e | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 141 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-004-b | reports/stage_e10_research/calendar/ernst_gilbert_hrdlicka_2021.txt | 163 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-004-c#1 | reports/stage_e10_research/calendar/ernst_gilbert_hrdlicka_2021.txt | 176 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-004-c#2 | reports/stage_e10_research/calendar/ernst_gilbert_hrdlicka_2021.txt | 178 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-007-a | reports/stage_e10_research/calendar/kurov_wolfe_gilbert_2020.txt | 19 | found with whitespace or hyphenation differences | quoted or cited in: body |
| C-K9R-001-1 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1585 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-2 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1569 | found verbatim | quoted or cited in: App. B |
| C-K9R-001-3 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1626 | found verbatim | quoted or cited in: App. B |
| C-K9R-001-4 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1601 | found verbatim | verified; evidence, not quoted |
| C-K9R-001-5 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1602 | found verbatim | quoted or cited in: App. B |
| C-K9R-001-6 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1623 | found verbatim | quoted or cited in: App. B |
| C-K9R-001-7 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1627 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-8 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1628 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-9 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1014 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-10 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 878 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-11 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1688 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-12 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 2014 | found verbatim | quoted or cited in: body, App. B |
| C-K9R-001-13 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 2004 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-14 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1753 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-15 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1771 | found verbatim | quoted or cited in: App. B |
| C-K9R-001-16 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1780 | found with whitespace or hyphenation differences | verified; evidence, not quoted |
| C-K9R-001-17 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1004 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-18 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1572 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-001-19 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1606 | found with whitespace or hyphenation differences | verified; evidence, not quoted |
| C-K9R-001-20 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 291 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-004-1 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 133 | found with whitespace or hyphenation differences | quoted or cited in: body, App. A |
| C-K9R-004-2 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 134 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-3 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 141 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-4 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 147 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-5 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 148 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-6 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 152 | found verbatim | quoted or cited in: App. A |
| C-K9R-004-7 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 473 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-8 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 596 | found verbatim | quoted or cited in: App. A |
| C-K9R-004-9 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 566 | found with whitespace or hyphenation differences | quoted or cited in: body, App. A |
| C-K9R-004-10 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 567 | found with whitespace or hyphenation differences | verified; evidence, not quoted |
| C-K9R-004-11 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 568 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-12 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 569 | found with whitespace or hyphenation differences | verified; evidence, not quoted |
| C-K9R-004-13 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 202 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-14 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 135 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-15 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 466 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-16 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 523 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| C-K9R-004-17 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 187 | found with whitespace or hyphenation differences | verified; evidence, not quoted |
| C-K9R-004-18 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 471 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| P-K9R-014-b.1 | reports/stage_e10_research/regime/bianco_corsi_reno_2009_pnas.txt | 96 | found verbatim | quoted or cited in: App. B |
| P-K9R-014-b.2 | reports/stage_e10_research/regime/bianco_corsi_reno_2009_pnas.txt | 98 | found verbatim | quoted or cited in: App. B |
| C-K9C-001-1 | reports/stage_e10_research/calendar/savor_wilson_2013_draft.txt | 664 | found with whitespace or hyphenation differences | quoted or cited in: body |
| C-K9C-001-2 | reports/stage_e10_research/calendar/savor_wilson_2013_draft.txt | 1713 | found with whitespace or hyphenation differences | quoted or cited in: body |
| C-K9C-003-1 | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 127 | found verbatim | quoted or cited in: body |
| C-K9C-003-2 | reports/stage_e10_research/calendar/ai_bansal_guo_2023_w31923.txt | 101 | found with whitespace or hyphenation differences | quoted or cited in: body |
| C-K9R-001-21 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1600 | found verbatim | quoted or cited in: App. B |
| C-K9R-001-22 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1005 | found with whitespace or hyphenation differences | quoted or cited in: body, App. B |
| C-K9R-001-23 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1610 | found with whitespace or hyphenation differences | verified; evidence, not quoted |
| P-K9C-001-d | reports/stage_e10_research/calendar/savor_wilson_2013_draft.txt | 794 | found with whitespace or hyphenation differences | quoted or cited in: body |
| P-K9C-002-d | reports/stage_e10_research/calendar/ai_bansal_2018_econometrica.txt | 251 | found with whitespace or hyphenation differences | quoted or cited in: body |
| C-K9R-001-24 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1683 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| C-K9R-004-19 | reports/stage_e10_research/regime/fassas_hourvouliades_2019_jrfm.txt | 196 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| RUL-1 | reports/stage_e10_briefs/task4_lead_rulings.md | 28 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| RUL-2 | reports/stage_e10_briefs/task4_lead_rulings.md | 31 | found with whitespace or hyphenation differences | quoted or cited in: App. B |
| RUL-3 | reports/stage_e10_briefs/task4_lead_rulings.md | 68 | found verbatim | quoted or cited in: body |
| RUL-4 | reports/stage_e10_briefs/task4_lead_rulings.md | 69 | found verbatim | quoted or cited in: body |
| RUL-5 | reports/stage_e10_briefs/task4_lead_rulings.md | 70 | found with whitespace or hyphenation differences | quoted or cited in: body |
| RUL-6 | reports/stage_e10_briefs/task4_lead_rulings.md | 71 | found with whitespace or hyphenation differences | quoted or cited in: body |
| RUL-7 | reports/stage_e10_briefs/task4_lead_rulings.md | 74 | found with whitespace or hyphenation differences | quoted or cited in: body |
| RUL-8 | reports/stage_e10_briefs/task4_lead_rulings.md | 49 | found verbatim | quoted or cited in: App. A |
| RUL-9 | reports/stage_e10_briefs/task4_lead_rulings.md | 87 | found verbatim | quoted or cited in: body |
| DT-1 | reports/stage_e10_design_target.md | 121 | found verbatim | verified; evidence, not quoted |
| LOG-1 | reports/stage_e10_research_regime.md | 190 | found with whitespace or hyphenation differences | quoted or cited in: App. A |
| D9-1 | docs/STAGE_E_DESIGN.md | 510 | found verbatim | quoted or cited in: body |
| D9-2 | docs/STAGE_E_DESIGN.md | 506 | found verbatim | quoted or cited in: body |
| F9-1 | reports/stage_e0_topstep_facts.json | 70 | found verbatim | quoted or cited in: body |
| F9-2 | reports/stage_e0_topstep_facts.json | 71 | found verbatim | quoted or cited in: body |
| K8-1 | reports/stage_e0_catalog_K8.md | 97 | found verbatim | quoted or cited in: body |
| P-K9R-006-a | reports/stage_e10_research/regime/bansal_stivers_quantpedia_pointer.md | 44 | found verbatim | verified; **removed from the evidence in round 3 (R-03)**, not quoted (added in round 2) |
| P-K9R-007-a | reports/stage_e10_research/regime/copeland_1999_ideas.html | 33 | found verbatim | quoted or cited in: body, App. B (added in round 2) |
| P-K9R-007-a#2 | reports/stage_e10_research/regime/copeland_1999_ideas.html | 33 | found verbatim | quoted or cited in: body, App. B (added in round 2) |
| C-K9R-001-25 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 2032 | found with whitespace or hyphenation differences | quoted or cited in: body, App. B (added in round 2) |
| C-K9R-001-26 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 2029 | found with whitespace or hyphenation differences | quoted or cited in: body (added in round 2) |
| C-K9R-001-27 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1660 | found with whitespace or hyphenation differences | quoted or cited in: body, App. B (added in round 3) |
| C-K9R-001-28 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1662 | found with whitespace or hyphenation differences | quoted or cited in: body, App. B (added in round 3) |
| C-K9R-001-29 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1674 | found with whitespace or hyphenation differences | quoted or cited in: App. B (added in round 3) |
| C-K9R-001-30 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1611 | found with whitespace or hyphenation differences | quoted or cited in: App. B (added in round 3) |
| C-K9R-001-31 | reports/stage_e10_research/regime/hu_pan_wang_zhu_nber_w25817.txt | 1621 | found with whitespace or hyphenation differences | quoted or cited in: App. B (added in round 3) |
| P-K9C-006-c.1 | reports/stage_e10_research/calendar/hu_pan_wang_zhu_w25817.txt | 99 | found with whitespace or hyphenation differences | quoted or cited in: body (added in round 3) |
| P-K9C-006-c.2 | reports/stage_e10_research/calendar/hu_pan_wang_zhu_w25817.txt | 101 | found with whitespace or hyphenation differences | quoted or cited in: body (added in round 3) |
| P-K9C-006-e | reports/stage_e10_research/calendar/hu_pan_wang_zhu_w25817.txt | 1114 | found with whitespace or hyphenation differences | quoted or cited in: body (added in round 3) |
| DS-D6 | docs/STAGE_E_DESIGN.md | 381 | found with whitespace or hyphenation differences | quoted or cited in: body (added in round 3) |
| K1-E0 | reports/stage_e0_catalog_K1.md | 597 | found verbatim | quoted or cited in: body (added in round 3) |
| DT-2 | reports/stage_e10_design_target.md | 175 | found with whitespace or hyphenation differences | quoted or cited in: body, App. B (added in round 3) |
| CAL-E2A-1 | reports/stage_e2a_calendar_sources.md | 139 | found verbatim | quoted or cited in: body (added in round 3) |
| CAL-E2A-2 | reports/stage_e2a_calendar_sources.md | 149 | found verbatim | quoted or cited in: body (added in round 3) |
| R11-1 | reports/stage_e10_briefs/review_scratch/hpwz_jfe_mit.txt | 958 | found verbatim | quoted or cited in: body, App. B (added in round 3) |
| R11-2 | reports/stage_e10_briefs/review_scratch/hpwz_jfe_mit.txt | 37 | found verbatim | quoted or cited in: body, App. B (added in round 3) |
| CAL-BLS-1 | reports/stage_e10_research/catalog/bls_empsit_archive_sget.html | 420 | found verbatim | quoted or cited in: body |
| CAL-BLS-2 | reports/stage_e10_research/catalog/bls_cpi_archive_sget.html | 417 | found verbatim | quoted or cited in: body |
| CAL-BLS-3 | reports/stage_e10_research/catalog/bls_ppi_archive_sget.html | 421 | found verbatim | verified; evidence, not quoted |
| CAL-BLS-4 | reports/stage_e10_research/catalog/bls_empsit_11202025.html | 422 | found verbatim | quoted or cited in: body |
| CAL-BLS-5 | reports/stage_e10_research/catalog/bls_cpi_10242025.html | 400 | found verbatim | verified; evidence, not quoted |
| CAL-BLS-6 | reports/stage_e10_research/catalog/bls_ppi_11252025.html | 397 | found verbatim | verified; evidence, not quoted |
| CAL-FED-1 | reports/stage_e10_research/catalog/fed_fomccalendars.html | 1492 | found verbatim | verified; evidence, not quoted |
| CAL-FED-2 | reports/stage_e10_research/catalog/fed_fomccalendars.html | 1213 | found verbatim | verified; evidence, not quoted |
| CAL-FED-3 | reports/stage_e10_research/catalog/fed_fomccalendars.html | 1677 | found with whitespace or hyphenation differences (HTML entities decoded) | quoted or cited in: body |
| CAL-BEA-1 | reports/stage_e10_research/catalog/bea_gdp_news_archive.html | 530 | found verbatim | quoted or cited in: body |
| CAL-BEA-2 | reports/stage_e10_research/catalog/bea_gdp_news_archive.html | 528 | found verbatim | verified; evidence, not quoted |
| CAL-BEA-3 | reports/stage_e10_research/catalog/bea_schedule_full.html | 377 | found verbatim | verified; evidence, not quoted |
| CAL-BEA-4 | reports/stage_e10_research/catalog/bea_schedule_full.html | 417 | found verbatim | verified; evidence, not quoted |
| CAL-BEA-5 | reports/stage_e10_research/catalog/bea_schedule_full.html | 492 | found verbatim | verified; evidence, not quoted |
| CAL-ISM-1 | reports/stage_e10_research/catalog/ism_rob_calendar_fetch.html | 673 | found verbatim | quoted or cited in: body |
| CAL-ISM-2 | reports/stage_e10_research/catalog/ism_rob_calendar_fetch.html | 733 | found verbatim | quoted or cited in: body |
| CAL-ISM-3 | reports/stage_e10_research/catalog/ism_rob_calendar_wayback_20251009.html | 935 | found verbatim | verified; evidence, not quoted |

Rows: 138. NOT FOUND: 1 (P-K9R-014-b (as logged, one piece)). Removed from the entries: P-K9R-014-b as one
piece (its two verbatim pieces are quoted instead, joined by "[...]") and, in round 3, P-K9R-006-a (R-03).
Partial quotes in the entries are contiguous substrings of the rows above. Ruling, design-target, D9,
F9, K8, K1 and E.2a-calendar quotes are checked in the rows RUL-*, DT-*, D9-*, DS-*, F9-*, K8-*, K1-*,
CAL-E2A-* and LOG-* against the repo files.

---

## Appendix A. Withdrawn draft: K9-vixback-01

Withdrawn by the lead's round-2 rulings, items 6-10 (section 2 gives the two reasons). Kept in full so
the user can reinstate it; a candidate feature for V20's ML route v2. The text is the round-1 draft
with round 2 items 5 (entry intent 17:59 CT, fill 18:00 CT) and 14 (exit at F on an early-close date)
applied; round 3's R-12 amends item 14 (holiday-session dates excluded) if the draft is reinstated. References to "round-1 Q6-Q10" point to the round-1 questions answered in section 7. Its
passages are in section 8.

### K9-vixback-01 (withdrawn draft; VIX-futures backwardation state: long the next trade date)

- **Cluster and exposures.** K9. MNQ\* (q_c 1), M2K\* (q_c 3), MYM\* (q_c 3). One trial per exposure.
  S&P 500 evidence transferred.
- **Mechanism.** Contrarian timing from the shape of the VIX futures curve (fear priced at the front
  earns a premium). "This means that whenever the estimated VIX term structure took negative values
  (i.e., the VIX futures were in backwardation), the subsequent future return of S&P500 was positive."
  (P-K9R-004-a, with its opening sentence: "The coefficient of negative slope (Slope− t ) had a
  negative sign in all cases, and it was statistically significant in the three out of four time
  horizons under review (except the monthly horizon)."). Contango carries no signal: "when the VIX
  futures term structure was in contango (as it normally is), there was no meaningful market timing
  signal for S&P500 returns" (P-K9R-004-b). Percentiles: "the lower percentiles (D1–D4, which
  correspond to 5–20 percentiles) coefficients were statistically significant in all cases and had
  statistically higher coefficients compared to the respective higher percentile coefficients"
  (P-K9R-004-d).
  - **Evidence status:** full text (JRFM 2019, open access). One regressor, Newey-West errors, adjusted
    R2 0.009 at 1 day; one bull-market sample.
  - **Distinct from K9-vixspike-01 (ruling):** a curve-shape state, not a one-day spike. The two
    conditions overlap on some dates; the overlap is reported, not removed.
- **Rare condition and decision time.**
  - **Source slope definition (extracted; differs from the ruling's front-second reading, round-1 Q6).** The
    estimation was "conducted on each trading day by fitting a linear model of the available futures
    prices and spot VIX level as a function of time to maturity based on the least squares criterion"
    (C-K9R-004-3), FVIX_{i,t} = α + β TtM_{i,t}, where "TtMi,t is the time to maturity in days for the
    respective contract i on day t." (C-K9R-004-4). "Spot VIX was considered as the price for VIX
    futures with maturity equal to zero. Everyday t, we considered seven futures contracts and the spot
    VIX. The estimated VIX futures term structure was the daily estimated coefficient β."
    (C-K9R-004-5). Units: "volatility percentage points per year" (C-K9R-004-6).
  - **Contracts and prices:** "the daily closing prices of spot VIX and the seven nearest VIX futures
    for the period from 4 January 2010–29 December 2017" (C-K9R-004-1), from "the website of the CBOE
    Futures Exchange" (C-K9R-004-2). Closing prices, not settlements (round-1 Q10). Seven nearest monthly
    contracts (the source counts listed series as monthly; weeklies are not mentioned).
  - **Percentile construction (extracted; differs from the ruling's D-pct window, round-1 Q7).** "we used a
    classification based on the rolling 20 equally-spaced percentiles (from 5–95 percentiles) of the
    estimated VIX futures slope at any given day t." (C-K9R-004-18); "at any given time t, we considered
    the information set available at that time, which was the past history of the VIX term structure
    up to time t−1." (C-K9R-004-7); "(percentiles are ranked from 5%–95% in equal classes of 5%)"
    (C-K9R-004-8). D1-D4 is the bottom 20%.
  - **Member condition (written per the source, as the brief directs):** Slope_t at or below the 20th
    percentile of all past slopes from 2010-01-04 (the source's sample start, C-K9R-004-14) through
    t-1. **The ruling's version** (kept for the lead's choice, round-1 Q7): at or below the 20th percentile of
    the trailing 250 completed trade dates (D-pct).
  - **Decision time:** after day t's closes are published (spot VIX 15:15 CT; VX futures close and
    publication time [unverified], C8) and before the 17:59 CT intent. Look-ahead: none if
    publication precedes 17:59 CT.
- **Signal:** Slope_t as above; the ranking is invariant to the per-year scaling of β, so the scale
  literal does not matter. The time-to-maturity day count (calendar or trading days) is not stated by
  the source (round-1 Q6).
- **Entry rule:** BUY q_c by market intent on the 17:59 CT bar of calendar day t, filling at the
  18:00 CT open (Sunday for Monday): D-entry as amended for D9.4 (round 2 item 5).
- **Exit rule:** intent at 14:58 CT, fill 14:59 (D-exit; the source's K = 1 day is close to close:
  "Rt+K represents percentage returns in S&P500 in the subsequent K period (where K = 1 day, 1 week,
  1 month, and 1 quarter)", C-K9R-004-15).
- **Holding horizon:** about 21 h (18:00 to 14:59 CT; F on an early-close date); **session window:** trade date t + 1; flat by F.
- **Exclusions (in addition to C4):** days with fewer than seven listed VX contracts or a missing
  close; spot VIX missing. Announcement days are **not** excluded (the source has no such filter).
- **Exclusion-list check (X1-X15).**
  - X1-X9, X11, X12, X15: no (no vehicle return, range, release, auction, fix, limit, month-end or
    Monday keying).
  - **X13 (roll and expiry): risk, not keyed.** The seven-contract set changes when the front VX
    contract expires, so Slope_t can jump at VX expiries. The rule is not keyed to the expiry; the
    falsification reports trips on VX expiry-adjacent dates.
  - **X10: admissible (ruling, "same X10 and X14 readings as M1").** The condition reads a curve state,
    not the sign of the last move ("the cleaner side of the X10 borderline", reader's note). Risk as for
    K9-vixspike-01: backwardation follows falls.
  - **X14: admissible (ruling).** Risk: the slope is read from another market's prices (VX futures and
    SPX options).
- **Data fields read.** Spot VIX daily close; the seven nearest VX futures daily closing prices and
  their maturities (CFE website; free history, start date and access [unverified]; new series, flagged for E.11/E.12; the ruling's data
  item "CBOE CFE VX futures daily settlements, front and second month" changes per Q6); vehicle ohlcv-1m at 18:00 and 14:59 CT.
- **Order type:** market. **Sizing:** q_c.
- **Parameters.**

  | Literal | Value | Source or rule |
  |---|---|---|
  | Slope | OLS β of price on time to maturity over spot VIX (maturity 0) and the seven nearest VX futures, daily closing prices | C-K9R-004-1, -3, -4, -5 |
  | Time to maturity unit | days (calendar or trading: not stated) | C-K9R-004-4; open (round-1 Q6) |
  | Reference set | all slopes from 2010-01-04 through t-1 (source); ruling: trailing 250 trade dates (D-pct) | C-K9R-004-7, -14; D-pct (round-1 Q7) |
  | Cut | at or below the 20th percentile (D1-D4) | P-K9R-004-d; C-K9R-004-8; D-pct's 80/20 |
  | Horizon | next day, close to close | P-K9R-004-c (K = 1 day row); C-K9R-004-15 |
  | Entry, exit | intent 17:59 CT, fill 18:00 CT; intent 14:58, fill 14:59 | D-entry amended (round 2 item 5); D-exit |
  | Direction, size | long, q_c | P-K9R-004-a; (b)7 |
  | Weekly cap | 2 per week | D-wk |

- **Expected frequency.**
  - **Ruling's D-pct version:** 20% of dates by construction (on average), 0.20 x 299 = **59.8** before
    the cap. After the cap: **55.9** if signal days were independent; **23.9** if signal days came in
    full Monday-Friday weeks (2 of 5 kept). Curve states persist, so the true figure lies between, and
    nearer the lower end the more persistent the state. The excluded 12-month TSMOM row was ruled out
    on the same persistence ground (round-1 Q9).
  - **Per-source (expanding) version:** not 20% by construction in a given window; the share of
    research-window dates in the bottom 20% of the 2010-2025 history depends on how 2025-2026 compares
    with that history. **[no calendar arithmetic available]**.
- **Target move against M_X and G(f) (ratio route).**
  - Source figures (Table 3, K = 1 day, decimal returns): "D1 0.0237 **", "D2 0.0050 **", "D3 0.0005",
    "D4 0.0000" (C-K9R-004-9 to -12). Daily standard deviation of S&P 500 returns 0.0093 (Table 1,
    C-K9R-004-13; the PDF text layer prints each Table 1 cell twice; the column is read from the layout:
    term structure 0.0166, S&P 500 daily 0.0093). 0.798 x 0.0093 = 0.00742.
  - Per-bin ratios: D1 **3.19**, D2 **0.67**, D3 **0.067**, D4 **0.0**. The pooled bottom-20% mean
    needs the bin counts, which the source does not report; with equal counts it would be 0.98
    [assumption]. **[no conversion available for the pooled condition]**.
  - Against M_X / E|m_1| (0.022, 0.090, 0.086): D1 and D2 clear on all three; D3 clears MNQ only; D4
    clears none. Against G(f) at f = 0.187 (D-pct, independence): 1.26 (MNQ), 1.29 (M2K), 1.17 (MYM).
  - The D1 figure (2.37% mean next-day return) is large against the 0.93% daily standard deviation and
    a 4.63% maximum daily return ("Maximum 0.0678 0.0463", C-K9R-004-19), so D1 likely holds few days. Its weight in any pooled figure is
    unknown.
- **Conflicting evidence (quoted).**
  - "Contrary to previous research, very low volatility levels appear to be followed by significantly
    positive average returns over the next 20, 40 or 60 trading days." (P-K9R-005-a; non-US, 20-60
    days, abstract only).
  - **Within the source:** at K = 1 day, Table 3 marks only D1 and D2 as significant; D3 (0.0005) and
    D4 (0.0000) carry no star (C-K9R-004-11, -12). The text's "statistically significant in all cases"
    (P-K9R-004-d) holds at 1 month and 1 quarter, not at the member's 1-day horizon (round-1 Q8).
  - Table 2 at K = 1 day: "−0.0004 0.0245 −0.1687 *** 0.009 10.59 2.07" (C-K9R-004-16, the
    reader's P-K9R-004-c row): the Slope− coefficient is significant, but adjusted R2 is 0.009.
- **Falsification.** The standard condition and the 30-trip floor; reported: trips by bin (D1-D2 versus
  D3-D4), trips skipped by the cap, the overlap with K9-vixspike-01 dates (if reinstated), trips adjacent to VX
  expiries, the reversal check as in K9-vixspike-01, D9.7 exits.
- **Topstep check.** As K9-vixspike-01, items 1-10. Announcement days are not excluded, so some trips
  hold through CPI, NFP or FOMC releases at q_c <= 0.3 lot-equivalent (D9.5 permits holding through
  releases at below the maximum size). Opening fills stay outside every CPI window (C6).
- **Member-level coverage:** vehicle bars at 18:00 and 14:59 CT >= 0.95; VX and spot VIX closes
  present for t.
- **Data needed:** vehicle bars as above; VX futures (seven nearest) and spot VIX daily closes from
  2010-01-04 (per-source version) or from 250 trade dates before each window (D-pct version), free.
- **Source window and label.** K9R-004: 2010-01-04 to 2017-12-29 (C-K9R-004-1). No overlap with the
  confirmation window, holdout-2 or the research window. **Label: not source-overlap.**
- **Trials in N:** 0 (withdrawn; 3 if reinstated).

---

## Appendix B. Withdrawn draft: K9-vixspike-01

Withdrawn by the lead's round-3 ruling R-01 (reports/stage_e10_catalog_rulings.md): it fails the design
target's pre-declared X10 borderline test (section 2). Kept in full so the user can reinstate it at E.11
on the conditions in its entry. R-03, R-04, R-05, R-09, R-11 and R-16 are applied here. References to
round-1 questions (Q1-Q20) point to section 7. Its passages are in section 8.

### K9-vixspike-01 (withdrawn draft; uncertainty premium after an unscheduled VIX spike: long the next trade date)

- **Status:** **withdrawn** (round 3, R-01): it fails the design target's pre-declared X10 borderline
  test (Exclusion-list check, X10, below). Before the withdrawal (round 2 item 1) it was active, below
  the (b)1 40-trip margin (37.8-39.7 trips before the cap, 36.7-38.4 after) and above the 30-trip floor;
  the no-filter reading (47.1 / 45.1) was recorded as the alternative.
- **Reinstatement conditions (R-01).** The user may reinstate this draft at E.11 only by: (1) widening the
  design target's X10 borderline test explicitly, so that a one-day change in the implied-volatility
  index counts as well as a volatility level; (2) choosing one cutoff (R-05, Expected frequency): 0.5
  (meets (b)1 with margin, about 62 capped trips, a weaker per-trip move) or 1.0 (needs the (b)1
  waiver); (3) adding a pre-stated descriptive reversal diagnostic: the mean trip P&L on signal days
  whose vehicle day-session return was non-negative, reported beside the overall mean; descriptive
  only, it changes no tier. If reinstated, R-12 also applies (a trade date t + 1 that the equity
  calendar marks as an early close, early halt or closure, such as Thanksgiving Thursday, is excluded),
  and the 18:00 CT entry follows the user's K9-H decision (R-06).
- **Cluster and exposures.** K9. Traded exposures: Nasdaq-100 (MNQ\*, q_c 1), Russell 2000 (M2K\*,
  q_c 3), Dow (MYM\*, q_c 3). One trial per exposure. Signal variable: the CBOE VIX for all three
  (the source's variable; VXN, RVX and VXD are an untested transfer and are not used, ruling).
- **Mechanism.** A premium for heightened uncertainty that resolves on the next day. The source's model
  predicts it: "Prediction 5 Unanticipated spikes in VIX will be followed by VIX reversals and high
  re- turns." (P-K9R-001-h). Evidence: "Focusing on non-announcement days, we identify days of
  unanticipated heightened uncertainty using sudden and large increases in VIX. Consistent with our
  model's prediction, we find that such heightened VIX days are followed by large next-day market
  returns, with magnitudes comparable to the pre-announcement returns." (P-K9R-001-b); "we find
  predictability only for those non-announcement days with heightened VIX and the adjusted R-squared
  of the predictive regression is 2.34%, comparable to that for the scheduled announcements. For all
  other non-announcement days, changes in VIX cannot predict the next-day returns and the R-squared is
  essentially zero." (P-K9R-001-c).
  - **Magnitudes** (Table 7, η = 0, cutoff in VIX points, heightened days a year, next-day return in
    bps, t): 1994-2018 "1.5 24.6 19.63 2.68" and "1.0 39.7 10.34 2.01" (P-K9R-001-e); 1986-2018
    "1.5 22.2 14.22 2.07" and "1.0 36.5 6.59 1.41" (P-K9R-001-f). Higher cutoffs: "a cutoff value of
    2.5% yields an average of 11.1 heightened VIX days per year ... a higher cutoff value of 3.0%
    results in an average of 7.7 heightened VIX days per year ... the corresponding next-day returns,
    as reported under Rett+1 in Table 7, are 36.59 and 42.70 basis points" (P-K9R-001-d).
  - **Context (supporting sign at longer horizons):** "very high levels of implied volatility can on a
    statistical basis be viewed as signalling an imminent increase in stock indices, at least on a
    short term basis" (P-K9R-002-a; S&P 100 after VIX above its 90th percentile, 1-day "Mean 0.19" %,
    "Std. 2.31", P-K9R-002-c); in S&P futures, "profits and risk‐adjusted profits would have been
    enhanced by buying S&P futures when the fear indicators were high rather than low"
    (P-K9R-003-b, abstract only, 10-30-day horizons). K9R-006, added in round 2, was removed from this
    evidence in round 3 (R-03; section 5).
  - **Evidence status:** full text (NBER w25817, revised March 2021; published JFE 2022, whose text was
    not read). Peer-reviewed, model-led, t-stats about 2 to 3, weaker on the longer sample.
  - **Transfer (not tested by the source).** The source's returns are the S&P 500 cash index, close to
    close ("Reported under Rett+1 are average daily returns on the S&P 500 index realized on
    heightened VIX days.", C-K9R-001-6). The member trades the Nasdaq-100, Russell 2000 and Dow
    futures from 18:00 CT to 14:59 CT (C3), so it misses the source's 15:00-18:00 CT segment of day
    t, including the reopen.
- **Rare condition and decision time.**
  - **Source definition (extracted).** "∆VIXt = VIXt − VIXt−1" (C-K9R-001-2). "At the close of trading
    day t, we define day t + 1 as a heightened VIX day, if ∆VIXt is larger than a pre-determined
    constant cutoff value." (C-K9R-001-1). Table 7's header states the comparison as "VIXt − VIXt−1 ≥
    Cutoff (η = 0)" (C-K9R-001-21); the member uses ≥, the table's form.
  - **Role of η.** η is the decay of an exponentially weighted moving average of past VIX that replaces
    VIX_{t-1}; "When η = 0, there is no smoothing and µηt−1 = VIXt−1" (C-K9R-001-3). The member uses
    η = 0 (ruling), the simple daily change.
  - **Cutoff unit.** Table 7 labels the cutoff "(%)" (C-K9R-001-5). VIX is quoted in annualized
    percentage points and ∆VIX is a level difference (its standard deviation is "1.59% for the first
    sample", C-K9R-001-8), so a cutoff of 1.0 is **1.0 VIX point**, as the ruling assumed.
  - **Non-announcement day.** "“Non-Ann” refers to all trading days that are not FOMC, NFP, ISM, or GDP
    announcements days" (C-K9R-001-9). GDP counts every estimate: "including GDP, which has one
    preliminary announcement and two revisions for each quarter" (C-K9R-001-10). The filter applies to
    **day t + 1**, the heightened-VIX day whose return is measured (Table 9's title, "Predicting
    Non-Announcement Day Return", C-K9R-001-15). See Q1: the source's tabulated counts appear to
    include announcement days.
  - **Member condition:** VIX_close(t) - VIX_close(t-1) >= 1.0 (or the same change in the 3:45 pm ET
    values under the fallback), and trade date t + 1 is not in the HPWZ announcement set (FOMC,
    Employment Situation, ISM Manufacturing, any GDP estimate; C9).
  - **Decision time (round 2 item 4), in order:** (1) CBOE's official VIX close for day t (the 15:15 CT
    value), if it is published before the entry intent at 17:59 CT ([unverified]; verified in E.12);
    (2) otherwise the sourced fallback, the 3:45 pm ET (14:45 CT) VIX value of day t against that of
    day t - 1 (Table A1, C-K9R-001-25, -26): "it is possible to use information as early as 3:45 pm to
    identify the set of days on which heightened uncertainty has been triggered" (C-K9R-001-13).
    Look-ahead: none; both values are known at the 17:59 CT intent.
- **Signal:** the condition above; no price of the traded vehicle is read.
- **Entry rule:** BUY q_c by market intent on the 17:59 CT bar of calendar day t, filling at the
  18:00 CT open (Sunday 17:59 / 18:00 CT when t + 1 is a Monday): D-entry as amended for D9.4 (round 2
  item 5; C3).
- **Exit rule:** market intent on the first bar at or after C_X - 2 min (14:58 CT) of trade date t + 1,
  filling at the 14:59 open (D-exit; the source measures close to close).
- **Holding horizon:** about 20 h 59 min (18:00 to 14:59 CT), at least 2 hours by construction.
  **Session window:** inside trade date t + 1. **Flat by F** (15:08): last fill 14:59.
- **Exclusions (in addition to C4):** trade dates t + 1 in the HPWZ announcement set (50 dates in the
  316, C9); days where VIX_close(t) or VIX_close(t-1) is missing; one position at a time (a signal on
  t + 1 while a position is open cannot occur, since every trip closes at 14:59 of its own trade date).
- **Exclusion-list check (X1-X15).**
  - X1, X2, X3: no. The rule reads no intraday or prior-range return of the vehicle.
  - X4, X6: no. Announcement days are excluded; no pre- or post-release move is read.
  - X5, X7, X8, X9, X11, X12, X15: no (no auction, inventory, WASDE, fix, limit, month-end or
    Monday-trend keying).
  - X13: no. The VIX is an index; no expiry or roll is read.
  - **X10 (overreaction reversal): the reason for the withdrawal (R-01).** The round-1 ruling read it
    admissible: "The condition reads an implied-volatility change, not the sign or size of the price
    move. The mechanism is the source's model prediction (P-K9R-001-h: uncertainty resolves and earns a
    premium), not overreaction." The design target's borderline test, fixed before any source was
    read, admits such a member only if "the condition reads a volatility level, not the sign of the last
    move" (DT-2); this condition is a one-day change in VIX. **Risk, in the source's own words:**
    "although the correlation between daily returns and daily changes in VIX is close to −70%, the
    information contents of these two variables are not the same" (C-K9R-001-28), so the trade is long
    mostly after falls. On Table 8 (1986-2018) the source says: "As shown in the left panel, after
    large price drops, the stock market does on average yield positive returns on the next day, but the
    predicted returns are statistically insignificance." (C-K9R-001-27). Next-day returns after large
    price drops alone are **positive, of comparable or larger size, statistically insignificant on 5-16
    days a year** (R-04): rows from "-2.4 5.3 27.96 1.26" (C-K9R-001-29) to "-1.5 16.3 15.48 1.77"
    (C-K9R-001-24), against the member's 10.34 bps on 39.7 days a year. The source's data therefore do
    not separate the uncertainty premium from a reversal of the spike-day fall (K9R-014, K9R-012).
    Reinstatement needs the user to widen the test explicitly (Reinstatement conditions, above).
  - **X14 (cross-market lead): admissible (lead's ruling).** "VIX measures the uncertainty state of the
    US equity market whose premium the member collects. It is not a price lead from another market.
    Precedent: K1-vxnband-01 conditioned an equity member on VXN inside K1." **Risk:** VIX is computed
    from SPX options, another market's prices (the V16 class). The reviewer may challenge both rulings.
- **Data fields read.**
  - CBOE VIX official daily close, days t-1 and t (free history; publication before 17:59 CT
    [unverified], verified in E.12). Fallback: the 3:45 pm ET VIX values of t-1 and t (intraday history
    [unverified], Q18). New series for the program, flagged for E.11/E.12.
  - EC-K9 exclusion set (C9; free, known in advance).
  - Vehicle ohlcv-1m open and instrument_id at the 18:00 CT bar (entry fill) and 14:59 CT (exit fill);
    the intents are emitted on the 17:59 and 14:58 bars.
- **Order type:** market. **Sizing:** q_c (MNQ 1, M2K 3, MYM 3).
- **Parameters (every literal and its source).**

  | Literal | Value | Source or rule |
  |---|---|---|
  | Signal variable | CBOE VIX daily close | K9R-001 (C-K9R-001-2); ruling |
  | Change measure | VIX_t - VIX_{t-1} (η = 0) | C-K9R-001-2, C-K9R-001-3; ruling |
  | Cutoff | >= 1.0 VIX point | P-K9R-001-e row "1.0 39.7 10.34 2.01"; C-K9R-001-21 (≥); design rule (b)1 frequency (ruling) |
  | Day traded | t + 1, the day after the spike | C-K9R-001-1 |
  | Non-announcement set | FOMC, NFP, ISM, GDP (all estimates) on t + 1 | C-K9R-001-9, -10; ruling |
  | VIX value used | official close (15:15 CT); fallback 3:45 pm ET (14:45 CT) | C-K9R-001-12; C-K9R-001-13, -25, -26; round 2 item 4 |
  | Entry | intent on the 17:59 CT bar of day t, fill at the 18:00 CT open | D-entry amended for D9.4 (round 2 item 5) |
  | Exit | intent at 14:58 CT, fill 14:59; holiday-session dates excluded if reinstated | D-exit (C_X - 2 min); R-12 (amends round 2 item 14) |
  | Direction, size | long, q_c | P-K9R-001-h; design target (b)7 |
  | Weekly cap | 2 per Monday-Friday week | D-wk |

- **Expected frequency (calendar and source arithmetic only).**
  - Source rate at the 1.0 cutoff, 1994-2018: 39.7 days a year (P-K9R-001-e) = 0.1575 per trade date.
  - **Before the filter and cap:** 0.1575 x 299 = **47.1** (the ruling's "about 47").
  - **With the non-announcement filter:** 50 of the 316 window dates are HPWZ announcement dates
    (10 FOMC + 14 NFP + 15 ISM + 13 GDP, less 2 same-day overlaps), so 266 / 316 = 0.842 are eligible:
    47.1 x 0.842 = **39.7 before the cap** (if spikes fall on announcement days at the calendar rate).
    If they fall at the source's own rate, 47.1 x 162 / 202 = **37.8**. **Derivation (R-09):** Table 1
    gives 4,976 non-announcement days ("Non-Ann ... 4976", C-K9R-001-17) and 5,965 days in all
    (C-K9R-001-22); Table 9 gives 4,814 "Normal Days", "all trading days that are not FOMC, NFP, ISM, and
    GDP announcement days and not heightened VIX days" (C-K9R-001-14, -16). So 4,976 - 4,814 = 162 of
    Table 9's 202 heightened-VIX days are non-announcement days, and 40 (19.8%) fall on announcement
    days, against 989 of 5,965 (16.6%) of all days. This is an inference from the tables, not a source
    statement.
  - **After the D-wk cap** (independence, C10): **38.4** (or 36.7). Without the filter: 45.1.
    Clustering of VIX spikes lowers these further.
  - Both filtered figures are **below the 40-trip expectation of (b)1**. Both clear the proposed
    30-trip floor unless clustering is strong.
  - **Cutoff selection (R-05).** The lead's round-1 choice of 1.0 over 1.5 applied (b)1. The source's
    0.5 row ("0.5 68.0 7.87 2.28" on 1994-2018, C-K9R-001-30; "0.5 65.4 4.84 1.62" on 1986-2018,
    C-K9R-001-31) was not in the lead's view, and no rule picked 1.0 over 0.5. The applied rule was in
    effect "the largest cutoff whose count clears 40", a rarity preference that the design target's
    reading 3 (prefer the upper end of the band) argues against.
  - **Alternative: the 0.5 cutoff.** 68.0 / 252 x 299 = 80.7 trips before the filter; 67.9 with it
    (64.7 at the source's split); 62.4 after the cap (59.9), so it meets (b)1 with margin (the rulings
    say about 62). Its per-trip move is weaker: ratio 7.87 / 90.2 = 0.087 on 1994-2018, which is just
    below M_X / E|m_1| on M2K (0.090) and just above it on MYM (0.086); 4.84 / 90.2 = 0.054 on
    1986-2018, below M_X on both. If the draft is reinstated, the user chooses one cutoff: 0.5 or 1.0
    (with the (b)1 waiver). No grids: one literal set.
- **Target move against M_X and G(f) (ratio route, C11).**
  - Source: 10.34 bps per trip (1994-2018 row); the source's daily standard deviation of S&P 500
    returns is 1.13% ("The sample standard deviations are 1.13% and 9.42%, respectively, for daily
    returns and daily changes in volatility.", C-K9R-001-11; that figure is for January 1986 to May
    2018). Ratio = 10.34 / (0.798 x 113) = **0.115**. The denominator is the 1986-2018 standard deviation,
    which includes October 1987; the 1994-2018 figure is not reported, so the denominator is overstated
    and the ratio is **conservative** for the member (R-16). The 1986-2018 row gives 6.59 / 90.2 = **0.073**.
  - Against M_X / E|m_1| (MNQ 0.022, M2K 0.090, MYM 0.086): the 1994-2018 row clears on all three (5.1x,
    1.28x, 1.33x). **The 1986-2018 row clears MNQ only** (3.3x) and falls below M_X on M2K (0.81x) and
    MYM (0.85x). This is a weakness of the member (round 2 item 3).
  - Against G(f) at the member's f = 38.4 / 299 = 0.128: G(f) / E|m_1| = 1.83 (MNQ), 1.86 (M2K), 1.69
    (MYM). The source's move is about one sixteenth of the eps bar, as the design target (a) reading 2
    expects.
- **Conflicting evidence (quoted).**
  - Weaker on the longer sample: "1.0 36.5 6.59 1.41" (P-K9R-001-f; t 1.41 at the member's cutoff).
  - "Volatility timing increases Sharpe ratios because changes in factor volatilities are not offset by
    proportional changes in expected returns." (P-K9R-008-a; monthly, so not a direct contradiction).
  - Reversal reading: "when volatility is low, daily (and hourly) stock returns exhibit positive
    autocorrelation, but when it is high, returns exhibit negative serial correlation. They also find
    an important asymmetry--negative serial correlation is more likely after price declines."
    (P-K9R-012-a, abstract only). In S&P futures the daily effect has nearly gone: "serial correlation
    has almost disappeared, the AR(1) [...] coefficient of Rt being just −0.0276, whereas the mean value
    found" (P-K9R-014-b, re-quoted in two pieces because the PDF's two-column text interleaves; the
    1928-1990 comparison value is 0.0618 per the log).
  - Table 8 (large price drops alone): moved into the X10 paragraph above and reworded (R-04).
  - **Size and style (transfer risk; added in round 2, item 17):** "On days that follow increases in
    the VIX, portfolios of large-capitalization stocks outperform portfolios of small-capitalization
    stocks and value-based portfolios outperform growth-based portfolios. On days following a decrease
    in the VIX, the opposites occur." (P-K9R-007-a; abstract only, sample not stated, published 1999).
    A relative effect after any VIX rise, not a spike: it suggests the next-day premium is smaller on
    the Russell 2000 (small caps) and the Nasdaq-100 (growth) than on large-cap value, so the S&P 500
    evidence transfers least well to M2K and MNQ. Each trial is screened on its own exposure; no rule
    changes.
- **Falsification.**
  - The standard condition on each exposure's eps_X (D5: research-window mean net P&L > 0 and daily
    t >= 1.0, zeros on no-trade dates), with the proposed 30-trip floor (design target (d)).
  - **Reversal diagnostic (pre-stated, R-01; descriptive only, it changes no tier):** the mean trip P&L
    on signal days whose vehicle day-session return on day t (D-ret) was non-negative, reported beside
    the overall mean.
  - Reported: trips skipped by the cap; D9.7 exits; the mean trip P&L per exposure side by side (the
    K9R-007 size and style transfer risk).
- **Topstep check.**
  1. Flat by F: last fill 14:59. Inside one trade date.
  2. Orders: market only; no stops, targets or brackets (D9.4).
  3. D9.3: at most 2 entries a week; hold about 21 h, far above the 2-minute and 10-minute floors.
  4. D9.4 (gapped markets): the entry fills at 18:00 CT, 60 minutes after the weekday or Sunday reopen
     (round 2 item 5, the K8-wkndbtc-01 precedent); it is not a stray-fill trade in a gapped market.
  5. News (D9.5): q_c is at most 0.3 lot-equivalent. Announcement days are excluded, so trips rarely
     hold through a scheduled release (CPI and PPI days are not excluded by the source's set).
  6. D9.5a and D9.12: no fill near a release; no opening fill in a CPI window (C6).
  7. D9.6: MNQ 1, M2K 3, MYM 3 micros, within 20 micros.
  8. **D9.7:** long holds after volatile days meet the 2% zone more often (design target (b)8). The
     harness blocks entry and forces exit beyond the stop level; D9.7 exits are recorded per trip.
  9. D9.8/D9.11: starred micros; D9.11 names no equity product. D9.13: R-12 applies if reinstated (C4).
  10. Payout (C12): at most one or two trips a week; slow on both paths.
- **Member-level coverage (D9):** ohlcv-1m coverage of the vehicle at 18:00 CT and 14:59 CT on the
  research window at least 0.95. D1 measured 08:30-15:00, so the 18:00 CT minute is E.2's check.
  The VIX close must be present for t-1 and t.
- **Data needed:** vehicle ohlcv-1m (research window; confirmation [S_X, 2024-02-29]); CBOE VIX daily
  closes over both windows plus one prior day (free; new series, E.11/E.12); EC-K9 for both windows
  (the confirmation-window announcement dates are not built here).
- **Source window and label.** K9R-001 (NBER w25817 text): "The sample period is from September 1994 to
  May 2018 for the top panel and January 1986 to May 2018 for the bottom panel." (C-K9R-001-7); Table
  A1 runs January 1992 to May 2018. VIX before 1990 is VXO (C-K9R-001-18). Context: K9R-002 January
  1986 to 2002; K9R-003 January 1989 to June 1999. **No overlap** with the confirmation window
  (S_X >= 2019-05-06), holdout-2 or the research window. **Label: not source-overlap**, on the NBER w25817
  sample (to May 2018). The re-check against the published version is closed (R-11): the review's
  saved copy of the JFE author manuscript ("Accepted 1 September 2021", R11-2) states "The sample period
  is from September 1994 to May 2018." (R11-1; reports/stage_e10_briefs/review_scratch/hpwz_jfe_mit.txt,
  grepped by this writer). K9R-007 (published 1999) cannot overlap. K9R-006 (1990-2022) was removed
  from the evidence (R-03), so the label stands.
- **Trials in N:** 0 (withdrawn; 3 if reinstated).
