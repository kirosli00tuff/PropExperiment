# Stage E.9 Task 1b: release and calendar check for the K8 members

Worker: ReleaseChecker-OpusMed (worker-medium, opus). Written 2026-10-02T05:30:05Z (UTC). Window 2025-04-01..2026-06-19. Fetch stamps are UTC; clock times are CT unless marked ET. Machine-readable twin: reports/stage_e9_release_check.json (per-row verdicts, quotes, page sha256 under `evidence_pages`). Evidence pages: reports/stage_e9_briefs/pages/ (48 files). WebSearch was not used (0 calls); no budget or cost notice was met. Nothing was written to data/vendor/. The release calendar was read only (sha256 839f2437bedbeb7b3423d7058a9955a0d4ccd1aebc4b01c62be624ab11d7bcb8).

Verdicts: keep / drop / unverifiable per row. Rulings are left to the lead; points needing one are under "For the lead".

## A1. Calendar rows per traded root (research window)

| Root | Release, local time | Rows |
|---|---|---|
| MGC | CPI 08:30 America/New_York | 14 |
| MGC | FOMC 14:00 America/New_York | 10 |
| MGC | G17 09:15 America/New_York | 14 |
| MGC | NFP 08:30 America/New_York | 14 |
| 6C | FOMC 14:00 America/New_York | 10 |
| 6C | NFP 08:30 America/New_York | 14 |
| 6C | WPSR 10:30 America/New_York | 56 |
| 6C | WPSR 12:00 America/New_York | 7 |
| 6C | WPSR 17:00 America/New_York | 1 |
| MNQ | CPI 08:30 America/New_York | 14 |
| MNQ | FOMC 14:00 America/New_York | 10 |
| MNQ | ISM_SERVICES 10:00 America/New_York | 15 |
| MNQ | NFP 08:30 America/New_York | 14 |

All counts equal the brief's expected counts (differences: {'MGC': {}, '6C': {}, 'MNQ': {}}). Row ids per root are in the JSON (A1.rows).

Note: the catalog C6 table (reports/stage_e0_catalog_K8.md, C6) names NFP, CPI, FOMC for gold and NFP, CPI, FOMC for Nasdaq-100. The calendar's `products` also attach G17 (09:15 ET) to MGC and ISM_SERVICES (10:00 ET) to MNQ, and do not attach CPI to 6C. Reported, not ruled.

## A2. Verdict per row

| Release | Rows | Verdicts | Evidence |
|---|---|---|---|
| CPI | 14 | keep 14 | cited: E.7 Task 1b (reports/stage_e7_release_check.json B_cpi, same 14 rows, same date and time) |
| FOMC | 10 | keep 10 | Federal Reserve FOMC calendar page + each statement press release ("For release at 2:00 p.m. EDT/EST"). Fetched fresh |
| G17 | 14 | keep 14 | Fed G.17 release-dates table + each release PDF ("For release at 9:15 a.m."). Fetched fresh |
| ISM_SERVICES | 15 | keep 15 | ISM release-date calendar (Wayback captures 20251009234426 and 20260415040000; the live page redirects to an ISM login) + ISM's PR Newswire releases (10:00 ET stamp). Fetched fresh |
| NFP | 14 | keep 14 | BLS: Employment Situation archive list (release-date file names) + BLS yearly schedules 2025/2026 (time). Fetched fresh |
| WPSR | 64 | keep 62, drop 2 | cited: E.4 Task 1b (reports/stage_e4_release_check.json wpsr, all 64 rows, same date and time) |

### Non-keep rows

| id | calendar | official record | verdict | source |
|---|---|---|---|---|
| WPSR-2025-12-29 | 2025-12-29 17:00 ET | schedule entry in last capture before release (20251228152631): December 19, 2025 / December 29, 2025 / Monday / 10:30 a.m. / Christmas; EIA WPSR home page capture 20251229205315 UTC shows prior release and notice "We are delaying today's release of the Weekly Petroleum Status Report with data for the week ending Dec. 19."; capt | drop (E.4: drop_actual_differs; K4-L-14 (E.4; drop applied in K4 member code only, calendar row unchanged)) | E.4 record |
| WPSR-2026-05-28 | 2026-05-28 12:00 ET | EIA's WPSR home page showed the previous release after the scheduled time; Wayback capture 20260528163711 UTC of the WPSR home page, 37 min after the scheduled time, still shows the previous release: "Data for week ending May 15, 2026 Release Date: May 20, 2026" (data/vendor/release_pages/e4/wpsr_home_20260528163711.html); next  | drop (E.4: drop_actual_differs; K4-L-15 (E.4; drop applied in K4 member code only, calendar row unchanged)) | E.4 record |

Both drops are E.4 verdicts, applied by the E.4 lead inside the K4 member code (K4-L-14, K4-L-15). The frozen calendar still carries both rows. WPSR-2025-12-29 is 16:00 CT, outside every K8 grid. WPSR-2026-05-28 is 11:00 CT, which is on the oilcad entry grid (A3).

### Sample quotes (every row has its own quote in the JSON)

- ISM_SERVICES-2025-04-03: "### Apr 03, 2025, 10:00 ET Services PMI® at 50.8%; March 2025 Services ISM® Report On Business®"; ISM calendar row: "April 1 3"; rule: "The ISM Services PMI ® Report is released on the third business day of the month at 10:00 a.m. (EST)"
- NFP-2025-04-04: "Friday, April 4, 2025 | 08:30 AM | **Employment Situation** for March 2025"; archive: "[March 2025 Employment Situation](/news.release/archives/empsit_04042025.htm)"
- CPI-2025-04-10: "Thursday, April 10, 2025 | 08:30 AM | Consumer Price Index"
- G17-2025-04-16: "For release at 9:15 a.m. (EDT) April 16, 2025"; G.17 table: "16-April-2025"
- FOMC-2025-05-07: "For release at 2:00 p.m. EDT"; calendar: "May 6-7 Statement: PDF | HTML"
- BLS time zone: "All times on calendar are Eastern Time"

G.17 anomaly (keep, flagged): the 2026-05-15 PDF reads "For release at 9:15 a.m. (PM)" and the 2026-06-15 PDF "For release at 9:15 a.m. (AM)". The time 9:15 a.m. and the date match, but the zone label is garbled on the Fed's own PDF. The other 12 read (EDT) or (EST).

ISM note (keep, flagged): ISM's rule text reads "The ISM Services PMI ® Report is released on the third business day of the month at 10:00 a.m. (EST)". It says EST all year; the PR Newswire stamps read "10:00 ET", which is how the calendar encodes it (10:00 America/New_York).

## A3. Calendar instants on a K8 fill minute (calendar only)

CT times of all rows per root: MGC: NFP 07:30 CT x14, CPI 07:30 CT x14, G17 08:15 CT x14, FOMC 13:00 CT x10; 6C: WPSR 09:30 CT x56, NFP 07:30 CT x14, FOMC 13:00 CT x10, WPSR 11:00 CT x7, WPSR 16:00 CT x1; MNQ: ISM_SERVICES 09:00 CT x15, NFP 07:30 CT x14, CPI 07:30 CT x14, FOMC 13:00 CT x10.

| Member (traded root) | Release | CT | Rows on an entry fill minute | Rows on an exit fill minute |
|---|---|---|---|---|
| K8-oilcad-01 | WPSR | 09:30 | 56 | 56 |
| K8-flight-01 | FOMC | 13:00 | 10 | 10 |
| K8-oilcad-01 | FOMC | 13:00 | 10 | 10 |
| K8-oilcad-01 | WPSR | 11:00 | 7 | 7 |
| K8-wkndbtc-01 (MNQ) | any | Sun 18:00 / Mon 14:59 | 0 | 0 |

Grids: flight entries 08:35..14:55 step 5; flight exits assumed on the 5-minute grid 08:40..15:05 (the brief gives only "up to 15:05"; no MGC release lies anywhere in 08:35..15:05 except FOMC 13:00, so the assumption changes nothing); oilcad entries 08:05..13:25, exits 08:20..13:40. No MGC row (07:30, 08:15, 13:00) other than FOMC is inside 08:35..15:05. WPSR 16:00 CT (2025-12-29) and NFP 07:30 are outside the oilcad grid.

Dates (entry rows; the exit rows are the same rows):

- K8-oilcad-01 WPSR 09:30 (56): 2025-04-02, 2025-04-09, 2025-04-16, 2025-04-23, 2025-04-30, 2025-05-07, 2025-05-14, 2025-05-21, 2025-06-04, 2025-06-11, 2025-06-18, 2025-06-25, 2025-07-02, 2025-07-09, 2025-07-16, 2025-07-23, 2025-07-30, 2025-08-06, 2025-08-13, 2025-08-20, 2025-08-27, 2025-09-10, 2025-09-17, 2025-09-24, 2025-10-01, 2025-10-08, 2025-10-22, 2025-10-29, 2025-11-05, 2025-11-19, 2025-11-26, 2025-12-03, 2025-12-10, 2025-12-17, 2025-12-31, 2026-01-07, 2026-01-14, 2026-01-28, 2026-02-04, 2026-02-11, 2026-02-25, 2026-03-04, 2026-03-11, 2026-03-18, 2026-03-25, 2026-04-01, 2026-04-08, 2026-04-15, 2026-04-22, 2026-04-29, 2026-05-06, 2026-05-13, 2026-05-20, 2026-06-03, 2026-06-10, 2026-06-17
- K8-flight-01 FOMC 13:00 (10): 2025-05-07, 2025-06-18, 2025-07-30, 2025-09-17, 2025-10-29, 2025-12-10, 2026-01-28, 2026-03-18, 2026-04-29, 2026-06-17
- K8-oilcad-01 FOMC 13:00 (10): 2025-05-07, 2025-06-18, 2025-07-30, 2025-09-17, 2025-10-29, 2025-12-10, 2026-01-28, 2026-03-18, 2026-04-29, 2026-06-17
- K8-oilcad-01 WPSR 11:00 (7): 2025-05-29, 2025-09-04, 2025-10-16, 2025-11-13, 2026-01-22, 2026-02-19, 2026-05-28

## A4. Official releases the calendar lacks

- NFP: the BLS archive list has 14 releases in the window, equal to the calendar's 14 (missing: none). BLS: "October 2025 Employment Situation – Not published because of 2025 lapse in federal government appropriations" (also in the calendar's `cancellations`).
- CPI: none missing (E.7: []).
- FOMC: the 10 statement days match. Not in the calendar: 2025-08-22, "August 22 (notation vote) Statement on Longer-Run Goals and Monetary Policy Strategy" (fed_fomccalendars.html). It is not a policy statement, and the page gives no time. For the lead.
- G17: the Fed table lists 14 releases in the window, all in the calendar (missing: none; table: "October 2025 NA November 2025 NA"). Not in the calendar: the annual revision, "The annual revision to industrial production and capacity utilization was published on November 24, 2025." (fed/g17_20251203.html), with no time on the saved pages. This is the calendar's own known_gaps[0].
- ISM_SERVICES: 15 Services PMI releases on PR Newswire in the window, all in the calendar (missing: none). Not a Services report and not in the calendar: 2026-01-29 11:00 ET "ISM® Makes Annual Adjustments to Seasonal Factors ..." (seasonal-factor notice).
- WPSR: E.4 checked all 64 rows. Each week Monday 2025-03-31..2026-06-15 has one row, except the week of 2025-12-22, which has none, and the week of 2025-12-29, which has two (12-29 17:00 ET and 12-31 10:30 ET). That is EIA's Christmas shift of the week-ending-12-19 report (E.4 record). No missing WPSR found.

## B. K8-wkndbtc-01 clock points (Mondays 2025-04-07..2026-06-15)

Test: trade date in the group calendar, no early_halt_ct, flatten_time_ct == 15:08 (MNQ and MES for equity, MBT for crypto); late opens recorded but not part of the B test. Clock test: MBT bar [14:59,15:00) Friday in crypto session_intervals(Friday); MBT bar [Sun 17:59, 18:00) in crypto session_intervals(Monday); MNQ [Sun 17:59, 18:01) and [Mon 14:58, 15:00) in equity session_intervals(Monday). Booking: data.group_session.trade_date_of_instant on open_intervals. One row per Monday is in the JSON (B.rows).

| Mondays | Fridays not full | Mondays not full | Eligible Mondays |
|---|---|---|---|
| 63 | 4 | 5 | 54 |

Excluded Mondays:

| Monday | Why |
|---|---|
| 2025-04-21 | Friday 2025-04-18 not full: equity trade_date=False halt=None F=None; crypto trade_date=False halt=None F=None; MBT Fri 14:59 not in session |
| 2025-05-26 | Monday not full: crypto BOOKED_FORWARD to 2025-05-27 (not a trade date); equity halt 12:00, F=11:30; MBT Sun 17:59 not in a Monday session (booked to 2025-05-27); MNQ Mon 14:58-14:59 not in session |
| 2025-07-07 | Friday 2025-07-04 not full: equity trade_date=True halt=12:00 F=11:30; crypto trade_date=True halt=12:00 F=11:30; MBT Fri 14:59 not in session |
| 2025-09-01 | Monday not full: crypto BOOKED_FORWARD to 2025-09-02 (not a trade date); equity halt 12:00, F=11:30; MBT Sun 17:59 not in a Monday session (booked to 2025-09-02); MNQ Mon 14:58-14:59 not in session |
| 2025-12-01 | Friday 2025-11-28 not full: equity trade_date=True halt=12:15 F=11:45; crypto trade_date=True halt=13:45 F=11:45; MBT Fri 14:59 not in session |
| 2026-01-19 | Monday not full: crypto BOOKED_FORWARD to 2026-01-20 (not a trade date); equity halt 12:00, F=11:45; MBT Sun 17:59 not in a Monday session (booked to 2026-01-20); MNQ Mon 14:58-14:59 not in session |
| 2026-02-16 | Monday not full: crypto BOOKED_FORWARD to 2026-02-17 (not a trade date); equity halt 12:00, F=11:45; MBT Sun 17:59 not in a Monday session (booked to 2026-02-17); MNQ Mon 14:58-14:59 not in session |
| 2026-04-06 | Friday 2026-04-03 not full: equity trade_date=True halt=08:15 F=08:00; crypto trade_date=True halt=10:15 F=08:00; MBT Fri 14:59 not in session |
| 2026-05-25 | Monday not full: crypto BOOKED_FORWARD to 2026-05-26 (not a trade date); equity halt 12:00, F=11:45; MBT Sun 17:59 not in a Monday session (booked to 2026-05-26); MNQ Mon 14:58-14:59 not in session |

B4 booking: on every eligible Monday the MBT Sunday 17:59 bar and the MNQ Sunday 18:00 bar book to the Monday, in both regimes (5-day: Sunday 17:00 CT open; 24/7 from trade date 2026-06-01: weekend trading belongs to the next trade date, data/calendars/crypto.py WEEKEND_TO_NEXT_TRADE_DATE_FROM, lines 314-317; E.6 member specs K7-L-01, lines 96-99, 191). Booked-forward holiday Mondays in the window (data/calendars/crypto.py BOOKED_FORWARD, lines 303-309): 2025-05-26, 2025-09-01, 2026-01-19, 2026-02-16, 2026-05-25. All five are excluded above; their Sunday 17:59 MBT bar books to the Tuesday. The same five as E.6 R-1b-2.

Facts kept out of the B test (for the lead): Monday 2026-06-01 has a crypto `delayed_start` (EXTENDED_MAINTENANCE: opened Friday 2026-05-29 16:30 CT, data/calendars/crypto.py 263-274). Its Sunday 17:59 bar is in session and it passes B; E counts it as not full because of the late open. Friday 2025-11-28 also carries the 07:30 CT Globex-outage late open (equity and crypto); it fails B anyway.

## C. The 24/7 change

CME (press release 19 Feb 2026, via E.6/E.2a, sha256 e3190d96...): "Beginning Friday, May 29 at 4:00 p.m. CT , CME Group Cryptocurrency futures and options will trade continuously on CME Globex with at least a two-hour weekly maintenance period over the weekend."

CME (press release 1 June 2026, sha256 f03c0339...): "CME Group, the world's leading derivatives marketplace, today announced it launched 24/7 trading for Cryptocurrency futures and options. The expanded trading hours, which went live on Friday, May 29, mark a significant milestone"

Repository: data/calendars/crypto.py:91-92 LAST_5DAY_TRADE_DATE = date(2026, 5, 29); FIRST_24_7_TRADE_DATE = date(2026, 6, 1); :263-274 EXTENDED_MAINTENANCE 2026-06-01 opened Friday 2026-05-29 16:30 CT. Cited from reports/stage_e6_release_check.json B_mondays.citations, with no new fetch.

| Count | Before (trade dates <= 2026-05-29) | After (trade dates >= 2026-06-01) | Total |
|---|---|---|---|
| crypto-calendar research-window trade dates | 294 | 14 | 308 |
| equity-calendar research-window trade dates | 301 | 15 | 316 |
| B eligible Mondays | 51 | 3 (2026-06-01, 2026-06-08, 2026-06-15) | 54 |

Crypto after = 14 because 2026-06-19 is BOOKED_FORWARD to 2026-06-22 (holdout-1).

## D. Roll blackouts (research window)

| Leg root | n | Dates | Record |
|---|---|---|---|
| MGC | 18 | 2025-05-28, 2025-05-29, 2025-05-30, 2025-07-29, 2025-07-30, 2025-07-31, 2025-11-25, 2025-11-26, 2025-11-27, 2026-01-28, 2026-01-29, 2026-01-30, 2026-03-26, 2026-03-27, 2026-03-30, 2026-05-27, 2026-05-28, 2026-05-29 | 1 distinct list across 7 runner records (window_dates.excluded.roll_blackout_any_leg), e.g. K5_K5-cp1-01_MGC_research.json |
| MCL | 45 | 2025-04-16, 2025-04-17, 2025-04-21, 2025-05-15, 2025-05-16, 2025-05-19, 2025-06-17, 2025-06-18, 2025-06-19, 2025-07-17, 2025-07-18, 2025-07-21, 2025-08-18, 2025-08-19, 2025-08-20, 2025-09-18, 2025-09-19, 2025-09-22, 2025-10-16, 2025-10-17, 2025-10-20, 2025-11-18, 2025-11-19, 2025-11-20, 2025-12-17, 2025-12-18, 2025-12-19, 2026-01-15, 2026-01-16, 2026-01-19, 2026-02-18, 2026-02-19, 2026-02-20, 2026-03-18, 2026-03-19, 2026-03-20, 2026-04-16, 2026-04-17, 2026-04-20, 2026-05-14, 2026-05-15, 2026-05-18, 2026-06-17, 2026-06-18, 2026-06-19 | 1 distinct list across 7 runner records (window_dates.excluded.roll_blackout_any_leg), e.g. K4_K4-apipre-01_MCL_research.json |
| 6C | 15 | 2025-06-12, 2025-06-13, 2025-06-16, 2025-09-11, 2025-09-12, 2025-09-15, 2025-12-11, 2025-12-12, 2025-12-15, 2026-03-12, 2026-03-13, 2026-03-16, 2026-06-11, 2026-06-12, 2026-06-15 | 1 distinct list across 3 runner records (window_dates.excluded.roll_blackout_any_leg), e.g. K3_K3-cp1-01_6C_research.json |
| MBT | 42 | 2025-04-24, 2025-04-25, 2025-04-28, 2025-05-29, 2025-05-30, 2025-06-02, 2025-06-26, 2025-06-27, 2025-06-30, 2025-07-24, 2025-07-25, 2025-07-28, 2025-08-28, 2025-08-29, 2025-09-02, 2025-09-25, 2025-09-26, 2025-09-29, 2025-10-30, 2025-10-31, 2025-11-03, 2025-11-26, 2025-11-28, 2025-12-01, 2025-12-24, 2025-12-26, 2025-12-29, 2026-01-29, 2026-01-30, 2026-02-02, 2026-02-26, 2026-02-27, 2026-03-02, 2026-03-26, 2026-03-27, 2026-03-30, 2026-04-23, 2026-04-24, 2026-04-27, 2026-05-28, 2026-05-29, 2026-06-01 | 1 distinct list across 6 runner records (window_dates.excluded.roll_blackout_any_leg), e.g. K7_K7-cp1-01_MBT_research.json |
| MNQ | 15 | 2025-06-16, 2025-06-17, 2025-06-18, 2025-09-16, 2025-09-17, 2025-09-18, 2025-12-16, 2025-12-17, 2025-12-18, 2026-03-17, 2026-03-18, 2026-03-19, 2026-06-15, 2026-06-16, 2026-06-17 | 1 distinct list across 5 runner records (window_dates.excluded.roll_blackout_any_leg), e.g. K1_K1-cp1-01_MNQ_research.json |
| MES | unverifiable | - | no research-window MES roll-blackout list in reports/stage_e2a_bars.md/.json, the D.1 records (only confirmation-window counts in reports/stage_d1e_power.json) or data/research_bars.py (no roll/splice metadata); the runner computes it at run time. data/vendor/databento/rolls/MES_v_0_2025-04-01_2026-09-16.jsonl exists but is outside the named sources and spans past 2026-06-19 (holdout-1): not opened |

UR-1: screening/stage_e_align.py:45 UNSEEN_ROLL_DATES = (date(2026, 6, 18), date(2026, 6, 19))  # rule UR-1.

| Member | Legs | Union of known leg dates | Union + UR-1 | Traded leg + UR-1 | Caveat |
|---|---|---|---|---|---|
| K8-flight-01 | MES+MGC | 18 | 20 | 20 | MES dates unverifiable |
| K8-oilcad-01 | MCL+6C | 60 | 60 | 17 |  |
| K8-wkndbtc-01 | MBT+MNQ | 57 | 59 | 17 |  |

For the lead: catalog C5 says "Signal-leg roll-blackout dates are not excluded". The union above follows the brief; the traded-leg column is given for comparison. Eligible B Mondays that fall in K8-wkndbtc-01's union + UR-1: 14 (2025-04-28, 2025-06-02, 2025-06-16, 2025-06-30, 2025-07-28, 2025-09-29, 2025-11-03, 2025-12-29, 2026-02-02, 2026-03-02, 2026-03-30, 2026-04-27, 2026-06-01, 2026-06-15).

## E. EC-CAL non-full weekdays

Definition: weekday, trade date, no early_halt_ct, no late open (scheduled_late_opens, late_opens or delayed_starts), flatten_time_ct == 15:08 (equity: MNQ and MES). F from rules.sessions.flatten_time_ct (MES/MNQ, MBT, MGC, MCL, 6C).

### equity (16 weekdays; 316 trade dates in window)

| Date | Day | Trade date | Halt CT | Late open | F | Record (data/calendars/equity.py) |
|---|---|---|---|---|---|---|
| 2025-04-18 | Fri | no | - | - | None | line 144: `date(2025, 4, 18): _note("Closed 2025-04-17 16:00 CT and no event on 2025-04-18 (Good "` |
| 2025-05-26 | Mon | yes | 12:00 | - | 11:30 | line 146: `date(2025, 5, 26): _note("12:00 CT halt, 17:00 CT reopen.",` |
| 2025-06-19 | Thu | yes | 12:00 | - | 11:30 | line 148: `date(2025, 6, 19): _note("12:00 CT halt, 17:00 CT reopen.",` |
| 2025-07-03 | Thu | yes | 12:15 | - | 11:45 | line 150: `date(2025, 7, 3): _note("'closed' at 12:15 CT, reopen 17:00 CT for trade date 2025-07-04.",` |
| 2025-07-04 | Fri | yes | 12:00 | - | 11:30 | line 152: `date(2025, 7, 4): _note("'closed' at 12:00 CT for trade date 2025-07-04 (a Friday; next "` |
| 2025-09-01 | Mon | yes | 12:00 | - | 11:30 | line 155: `date(2025, 9, 1): _note("12:00 CT halt, 17:00 CT reopen.",` |
| 2025-11-27 | Thu | yes | 12:00 | - | 11:30 | line 157: `date(2025, 11, 27): _note("12:00 CT halt, 17:00 CT reopen.",` |
| 2025-11-28 | Fri | yes | 12:15 | late_opens_entry | 11:45 | line 159: `date(2025, 11, 28): _note("The plan (capture 2024-12-20) has only the 12:15 CT close; the "` |
| 2025-12-24 | Wed | yes | 12:15 | - | 11:45 | line 162: `date(2025, 12, 24): _note("'closed' at 12:15 CT (capture 2026-01-29; the 2024-12-20 "` |
| 2025-12-25 | Thu | no | - | - | None | line 165: `date(2025, 12, 25): _note("Closed 2025-12-24 12:15 CT, reopen 2025-12-25 17:00 CT for trade "` |
| 2026-01-01 | Thu | no | - | - | None | line 167: `date(2026, 1, 1): _note("Closed 2025-12-31 16:00 CT, reopen 2026-01-01 17:00 CT for trade "` |
| 2026-01-19 | Mon | yes | 12:00 | - | 11:45 | line 169: `date(2026, 1, 19): _note("12:00 CT halt, 17:00 CT reopen. CME's record for product 318, the "` |
| 2026-02-16 | Mon | yes | 12:00 | - | 11:45 | line 172: `date(2026, 2, 16): _note("12:00 CT halt, 17:00 CT reopen.",` |
| 2026-04-03 | Fri | yes | 08:15 | - | 08:00 | line 174: `date(2026, 4, 3): _note("'closed' at 08:15 CT (jobs-report Good Friday) after the Thursday "` |
| 2026-05-25 | Mon | yes | 12:00 | - | 11:45 | line 177: `date(2026, 5, 25): _note("12:00 CT halt, 17:00 CT reopen.",` |
| 2026-06-19 | Fri | yes | 12:00 | - | 11:45 | line 179: `date(2026, 6, 19): _note("'closed' at 12:00 CT (a Friday; trade date 2026-06-22 per CME, "` |

### crypto (16 weekdays; 308 trade dates in window)

| Date | Day | Trade date | Halt CT | Late open | F | Record (data/calendars/crypto.py) |
|---|---|---|---|---|---|---|
| 2025-04-18 | Fri | no | - | - | None | line 190: `_closure(date(2025, 4, 18), "Good Friday"),` |
| 2025-05-26 | Mon | no | - | - | 11:30 | line 303: `_fwd(date(2025, 5, 26), "Memorial Day", date(2025, 5, 27)),` (BOOKED_FORWARD to 2025-05-27) |
| 2025-06-19 | Thu | no | - | - | 11:30 | line 304: `_fwd(date(2025, 6, 19), "Juneteenth", date(2025, 6, 20)),` (BOOKED_FORWARD to 2025-06-20) |
| 2025-07-04 | Fri | yes | 12:00 | - | 11:30 | line 191: `_halt(date(2025, 7, 4), "Independence Day", HALT_NOON),` |
| 2025-09-01 | Mon | no | - | - | 11:30 | line 305: `_fwd(date(2025, 9, 1), "Labor Day", date(2025, 9, 2)),` (BOOKED_FORWARD to 2025-09-02) |
| 2025-11-27 | Thu | no | - | - | 11:30 | line 306: `_fwd(date(2025, 11, 27), "Thanksgiving Day", date(2025, 11, 28)),` (BOOKED_FORWARD to 2025-11-28) |
| 2025-11-28 | Fri | yes | 13:45 | late_opens_entry | 11:45 | line 192: `_halt(date(2025, 11, 28), "Day after Thanksgiving", CLOSE_1345),` |
| 2025-12-24 | Wed | yes | 12:45 | - | 11:45 | line 193: `_halt(date(2025, 12, 24), "Christmas Eve", CLOSE_1245),` |
| 2025-12-25 | Thu | no | - | - | None | line 194: `_closure(date(2025, 12, 25), "Christmas Day"),` |
| 2026-01-01 | Thu | no | - | - | None | line 196: `_closure(date(2026, 1, 1), "New Year's Day"),` |
| 2026-01-19 | Mon | no | - | - | 11:45 | line 307: `_fwd(date(2026, 1, 19), "Martin Luther King Jr. Day", date(2026, 1, 20)),` (BOOKED_FORWARD to 2026-01-20) |
| 2026-02-16 | Mon | no | - | - | 11:45 | line 308: `_fwd(date(2026, 2, 16), "Presidents Day", date(2026, 2, 17)),` (BOOKED_FORWARD to 2026-02-17) |
| 2026-04-03 | Fri | yes | 10:15 | - | 08:00 | line 197: `_halt(date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", GOOD_FRIDAY_1015),` |
| 2026-05-25 | Mon | no | - | - | 11:45 | line 309: `_fwd(date(2026, 5, 25), "Memorial Day", date(2026, 5, 26)),` (BOOKED_FORWARD to 2026-05-26) |
| 2026-06-01 | Mon | yes | - | delayed_start | 15:08 | line 92: `FIRST_24_7_TRADE_DATE = date(2026, 6, 1)` |
| 2026-06-19 | Fri | no | - | - | 11:45 | line 310: `_fwd(date(2026, 6, 19), "Juneteenth (24/7 regime)", date(2026, 6, 22)),` (BOOKED_FORWARD to 2026-06-22) |

### metals (15 weekdays; 315 trade dates in window)

| Date | Day | Trade date | Halt CT | Late open | F | Record (data/calendars/metals.py) |
|---|---|---|---|---|---|---|
| 2025-04-18 | Fri | no | - | - | None | line 178: `_closure(date(2025, 4, 18), "Good Friday"),` |
| 2025-05-26 | Mon | yes | 13:30 | - | 11:30 | line 179: `_halt(date(2025, 5, 26), "Memorial Day", HALT_1330),` |
| 2025-06-19 | Thu | yes | 13:30 | - | 11:30 | line 180: `_halt(date(2025, 6, 19), "Juneteenth", HALT_1330),` |
| 2025-07-04 | Fri | yes | 12:00 | - | 11:30 | line 181: `_halt(date(2025, 7, 4), "Independence Day", HALT_NOON),` |
| 2025-09-01 | Mon | yes | 13:30 | - | 11:30 | line 182: `_halt(date(2025, 9, 1), "Labor Day", HALT_1330),` |
| 2025-11-27 | Thu | yes | 13:30 | - | 11:30 | line 183: `_halt(date(2025, 11, 27), "Thanksgiving Day", HALT_1330),` |
| 2025-11-28 | Fri | yes | 13:45 | late_opens_entry | 11:45 | line 184: `_halt(date(2025, 11, 28), "Day after Thanksgiving", CLOSE_1345),` |
| 2025-12-24 | Wed | yes | 12:45 | - | 11:45 | line 185: `_halt(date(2025, 12, 24), "Christmas Eve", CLOSE_1245),` |
| 2025-12-25 | Thu | no | - | - | None | line 186: `_closure(date(2025, 12, 25), "Christmas Day"),` |
| 2026-01-01 | Thu | no | - | - | None | line 188: `_closure(date(2026, 1, 1), "New Year's Day"),` |
| 2026-01-19 | Mon | yes | 13:30 | - | 11:45 | line 189: `_halt(date(2026, 1, 19), "Martin Luther King Jr. Day", HALT_1330),` |
| 2026-02-16 | Mon | yes | 13:30 | - | 11:45 | line 190: `_halt(date(2026, 2, 16), "Presidents Day", HALT_1330),` |
| 2026-04-03 | Fri | no | - | - | None | line 191: `_closure(date(2026, 4, 3), "Good Friday"),` |
| 2026-05-25 | Mon | yes | 13:30 | - | 11:45 | line 192: `_halt(date(2026, 5, 25), "Memorial Day", HALT_1330),` |
| 2026-06-19 | Fri | yes | 12:00 | - | 11:45 | line 193: `_halt(date(2026, 6, 19), "Juneteenth", HALT_NOON),` |

### energy (15 weekdays; 315 trade dates in window)

| Date | Day | Trade date | Halt CT | Late open | F | Record (data/calendars/energy.py) |
|---|---|---|---|---|---|---|
| 2025-04-18 | Fri | no | - | - | None | line 168: `_closure(date(2025, 4, 18), "Good Friday"),` |
| 2025-05-26 | Mon | yes | 13:30 | - | 11:30 | line 169: `_halt(date(2025, 5, 26), "Memorial Day", HALT_1330),` |
| 2025-06-19 | Thu | yes | 13:30 | - | 11:30 | line 170: `_halt(date(2025, 6, 19), "Juneteenth", HALT_1330),` |
| 2025-07-04 | Fri | yes | 12:00 | - | 11:30 | line 171: `_halt(date(2025, 7, 4), "Independence Day", HALT_NOON),` |
| 2025-09-01 | Mon | yes | 13:30 | - | 11:30 | line 172: `_halt(date(2025, 9, 1), "Labor Day", HALT_1330),` |
| 2025-11-27 | Thu | yes | 13:30 | - | 11:30 | line 173: `_halt(date(2025, 11, 27), "Thanksgiving Day", HALT_1330),` |
| 2025-11-28 | Fri | yes | 13:45 | late_opens_entry | 11:45 | line 174: `_halt(date(2025, 11, 28), "Day after Thanksgiving", CLOSE_1345),` |
| 2025-12-24 | Wed | yes | 12:45 | - | 11:45 | line 175: `_halt(date(2025, 12, 24), "Christmas Eve", CLOSE_1245),` |
| 2025-12-25 | Thu | no | - | - | None | line 176: `_closure(date(2025, 12, 25), "Christmas Day"),` |
| 2026-01-01 | Thu | no | - | - | None | line 178: `_closure(date(2026, 1, 1), "New Year's Day"),` |
| 2026-01-19 | Mon | yes | 13:30 | - | 11:45 | line 179: `_halt(date(2026, 1, 19), "Martin Luther King Jr. Day", HALT_1330),` |
| 2026-02-16 | Mon | yes | 13:30 | - | 11:45 | line 180: `_halt(date(2026, 2, 16), "Presidents Day", HALT_1330),` |
| 2026-04-03 | Fri | no | - | - | None | line 181: `_closure(date(2026, 4, 3), "Good Friday"),` |
| 2026-05-25 | Mon | yes | 13:30 | - | 11:45 | line 182: `_halt(date(2026, 5, 25), "Memorial Day", HALT_1330),` |
| 2026-06-19 | Fri | yes | 12:00 | - | 11:45 | line 183: `_halt(date(2026, 6, 19), "Juneteenth", HALT_NOON),` |

### fx (15 weekdays; 316 trade dates in window)

| Date | Day | Trade date | Halt CT | Late open | F | Record (data/calendars/fx.py) |
|---|---|---|---|---|---|---|
| 2025-04-18 | Fri | no | - | - | None | line 147: `_closure(date(2025, 4, 18), "Good Friday"),` |
| 2025-05-26 | Mon | yes | - | - | 11:30 | line 1683: `date(2025, 5, 26): Citation(` |
| 2025-06-19 | Thu | yes | - | - | 11:30 | line 1697: `date(2025, 6, 19): Citation(` |
| 2025-07-04 | Fri | yes | 12:00 | - | 11:30 | line 148: `_halt(date(2025, 7, 4), "Independence Day", time(12, 0)),` |
| 2025-09-01 | Mon | yes | - | - | 11:30 | line 1722: `date(2025, 9, 1): Citation(` |
| 2025-11-27 | Thu | yes | - | - | 11:30 | line 1736: `date(2025, 11, 27): Citation(` |
| 2025-11-28 | Fri | yes | 13:45 | late_opens_entry | 11:45 | line 149: `_halt(date(2025, 11, 28), "Day after Thanksgiving", time(13, 45)),` |
| 2025-12-24 | Wed | yes | 12:45 | - | 11:45 | line 150: `_halt(date(2025, 12, 24), "Christmas Eve", time(12, 45)),` |
| 2025-12-25 | Thu | no | - | - | None | line 151: `_closure(date(2025, 12, 25), "Christmas Day"),` |
| 2026-01-01 | Thu | no | - | - | None | line 153: `_closure(date(2026, 1, 1), "New Year's Day"),` |
| 2026-01-19 | Mon | yes | - | - | 11:45 | line 1759: `date(2026, 1, 19): Citation(` |
| 2026-02-16 | Mon | yes | - | - | 11:45 | line 1773: `date(2026, 2, 16): Citation(` |
| 2026-04-03 | Fri | yes | 10:15 | - | 08:00 | line 154: `_halt(date(2026, 4, 3), "Good Friday (abbreviated, jobs report)", time(10, 15)),` |
| 2026-05-25 | Mon | yes | - | - | 11:45 | line 1801: `date(2026, 5, 25): Citation(` |
| 2026-06-19 | Fri | yes | 12:00 | - | 11:45 | line 155: `_halt(date(2026, 6, 19), "Juneteenth", time(12, 0)),` |

Notes: on the FX US-holiday Mondays/Thursdays (2025-05-26, 06-19, 09-01, 11-27, 2026-01-19, 02-16, 05-25) the fx module has no halt: it has a Citation with the note "US holiday with regular FX Globex hours ... Same session clock as a regular day: no entry". F is still 11:30/11:45 from rules.sessions TOPSTEP_HOLIDAYS (rules/sessions.py:100 on). On the crypto booked-forward days, flatten_time_ct also returns 11:30/11:45 although the day is not a crypto trade date.

| Group | Full sessions in window |
|---|---|
| equity | 303 |
| crypto | 303 |
| metals | 304 |
| energy | 304 |
| fx | 304 |

| Member | Groups | Full-session set size (both groups full) |
|---|---|---|
| K8-flight-01 | equity + metals | 303 |
| K8-oilcad-01 | energy + fx | 304 |
| K8-wkndbtc-01 | crypto + equity | 302 |

(K8-wkndbtc-01 trades Mondays only. Its set here is the weekday set the brief asks for, not the B count.)

## F. External series

Verdict: confirmed: no active K8 member reads a price series from outside the bars, or any released value.

- K8-flight-01 (reports/stage_e0_catalog_K8.md:296-302): "MES ohlcv-1m close and instrument_id ... Gold vehicle ohlcv-1m open and instrument_id ... EC-CAL (equity-and-crypto and metals groups), and EC-FOMC and EC-BLS (for C6 only). Free, known in advance."
- K8-oilcad-01 (reports/stage_e0_catalog_K8.md:421-427): "Crude series ohlcv-1m close and instrument_id ... 6C ohlcv-1m open and instrument_id ... EC-CAL (energy and FX groups), and EC-FOMC, EC-BLS and EC-WPSR (for C6 only). Free, known before d."
- K8-wkndbtc-01 (reports/stage_e0_catalog_K8.md:543-549): "MBT ohlcv-1m close and instrument_id ... Nasdaq-100 vehicle ohlcv-1m open and instrument_id ... EC-CAL (equity-and-crypto group). Free, known in advance."
- all (reports/stage_e0_catalog_K8.md C10 (lines 86-249 block)): "All are external, free, and known before the trade date. No rule reads a released value."

The only external inputs are the free event calendars (EC-CAL, and for C6 EC-FOMC, EC-BLS, EC-WPSR). K8-wkndbtc-01's data line names EC-CAL only; C6 still applies to it through the harness. Nothing was fetched into data/vendor/.

## For the lead (facts, no ruling)

1. C6 vs calendar products: MGC carries G17 08:15 CT and MNQ carries ISM_SERVICES 09:00 CT beyond the catalog C6 table. Neither is on a K8 entry or exit minute (A3), so it is moot for fills, but it matters for the D8 event-window cost.
2. FOMC 13:00 CT is on both the flight and the oilcad entry grids (10 days each). WPSR 09:30 CT (56) and 11:00 CT (7, including the E.4-dropped 2026-05-28) are on the oilcad grid.
3. The calendar still holds WPSR-2025-12-29 and WPSR-2026-05-28, which E.4 dropped (K4-L-14/L-15, applied in K4 code only).
4. MES roll-blackout dates are unverifiable from the named sources. This affects only K8-flight-01's union, and only if signal-leg dates are excluded at all (C5 says they are not).
5. 2026-06-01: crypto delayed start (opened Fri 2026-05-29 16:30 CT). It passes B and fails E's late-open test.
6. 2025-08-22 FOMC notation vote and 2025-11-24 G.17 annual revision are not in the calendar (A4).

## Not finished or not verifiable

- MES research-window roll blackouts: unverifiable (D). The vendor rolls file was not opened: it is outside the named sources and runs to 2026-09-16.
- The ISM live calendar redirects to a login, so Wayback captures were used. ISM's 2025 capture of 2025-04-03 had no table; the 20251009234426 capture was used for the 2025 dates.
- BLS pages were saved from scrapling markdown output (curl got 403), so they are not byte-identical to the HTTP body.
- No release times were found for the 2025-08-22 notation vote or the 2025-11-24 G.17 annual revision.
- CPI and WPSR rows were not re-fetched; each cites the E.7 or E.4 check of the same row (same date and time).

## Evidence pages

| Saved path | URL | Fetched (UTC) | How | sha256 |
|---|---|---|---|---|
| reports/stage_e9_briefs/pages/bls_empsit_archive.md | https://www.bls.gov/bls/news-release/empsit.htm | 2026-10-02T05:21:39Z | scrapling extract get (curl 403) | 42112ed48a30c1fa... |
| reports/stage_e9_briefs/pages/bls_empsit_schedule.md | https://www.bls.gov/schedule/news_release/empsit.htm | 2026-10-02T05:21:38Z | scrapling extract get (curl 403) | 13e601820f8df4f6... |
| reports/stage_e9_briefs/pages/bls_schedule_2025_home.md | https://www.bls.gov/schedule/2025/home.htm | 2026-10-02T05:21:48Z | scrapling extract get | cc7b87f63d89cd0c... |
| reports/stage_e9_briefs/pages/bls_schedule_2026_home.md | https://www.bls.gov/schedule/2026/home.htm | 2026-10-02T05:21:49Z | scrapling extract get | e1d71b1e4e7a7e74... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20250507.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20250507a.htm | 2026-10-02T05:22:10Z | curl | b0728c88b0f1324f... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20250618.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20250618a.htm | 2026-10-02T05:22:10Z | curl | 8fe573428c27aa89... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20250730.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20250730a.htm | 2026-10-02T05:22:10Z | curl | ed33a60b181d5e4b... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20250917.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20250917a.htm | 2026-10-02T05:22:10Z | curl | 8512a88988a2435b... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20251029.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20251029a.htm | 2026-10-02T05:22:10Z | curl | f8b0ef2b37e70fd0... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20251210.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20251210a.htm | 2026-10-02T05:22:10Z | curl | 59e3125b29edc8d9... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20260128.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20260128a.htm | 2026-10-02T05:22:10Z | curl | d6a774aebb06c5fe... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20260318.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20260318a.htm | 2026-10-02T05:22:11Z | curl | dd376f9488130d45... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20260429.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20260429a.htm | 2026-10-02T05:22:11Z | curl | 4019bb27e2884b6d... |
| reports/stage_e9_briefs/pages/fed/fomc_statement_20260617.html | https://www.federalreserve.gov/newsevents/pressreleases/monetary20260617a.htm | 2026-10-02T05:22:11Z | curl | ff7804dd316fe153... |
| reports/stage_e9_briefs/pages/fed/g17_20250416.html | https://www.federalreserve.gov/releases/g17/20250416/default.htm | 2026-10-02T05:22:11Z | curl | e8fa2981a6f23ea4... |
| reports/stage_e9_briefs/pages/fed/g17_20250416.pdf | https://www.federalreserve.gov/releases/g17/20250416/g17.pdf | 2026-10-02T05:22:31Z | curl | 161048f89b1df156... |
| reports/stage_e9_briefs/pages/fed/g17_20250515.html | https://www.federalreserve.gov/releases/g17/20250515/default.htm | 2026-10-02T05:22:11Z | curl | db3971f54b2e684b... |
| reports/stage_e9_briefs/pages/fed/g17_20250515.pdf | https://www.federalreserve.gov/releases/g17/20250515/g17.pdf | 2026-10-02T05:22:32Z | curl | 0c501784d8e1a309... |
| reports/stage_e9_briefs/pages/fed/g17_20250617.html | https://www.federalreserve.gov/releases/g17/20250617/default.htm | 2026-10-02T05:22:12Z | curl | 08698c798cbde813... |
| reports/stage_e9_briefs/pages/fed/g17_20250617.pdf | https://www.federalreserve.gov/releases/g17/20250617/g17.pdf | 2026-10-02T05:22:32Z | curl | 232eb48005b1e28e... |
| reports/stage_e9_briefs/pages/fed/g17_20250716.html | https://www.federalreserve.gov/releases/g17/20250716/default.htm | 2026-10-02T05:22:12Z | curl | 53430cd1989bcf61... |
| reports/stage_e9_briefs/pages/fed/g17_20250716.pdf | https://www.federalreserve.gov/releases/g17/20250716/g17.pdf | 2026-10-02T05:22:32Z | curl | d8ab3ba23ea26b89... |
| reports/stage_e9_briefs/pages/fed/g17_20250815.html | https://www.federalreserve.gov/releases/g17/20250815/default.htm | 2026-10-02T05:22:12Z | curl | 780be45f2cb39fde... |
| reports/stage_e9_briefs/pages/fed/g17_20250815.pdf | https://www.federalreserve.gov/releases/g17/20250815/g17.pdf | 2026-10-02T05:22:32Z | curl | bc1261aaaff0c66f... |
| reports/stage_e9_briefs/pages/fed/g17_20250916.html | https://www.federalreserve.gov/releases/g17/20250916/default.htm | 2026-10-02T05:22:13Z | curl | 525d8e9d8ce6c2e2... |
| reports/stage_e9_briefs/pages/fed/g17_20250916.pdf | https://www.federalreserve.gov/releases/g17/20250916/g17.pdf | 2026-10-02T05:22:33Z | curl | 6cf39b5fb42adfa8... |
| reports/stage_e9_briefs/pages/fed/g17_20251203.html | https://www.federalreserve.gov/releases/g17/20251203/default.htm | 2026-10-02T05:22:13Z | curl | 31b9f134a8356dfe... |
| reports/stage_e9_briefs/pages/fed/g17_20251203.pdf | https://www.federalreserve.gov/releases/g17/20251203/g17.pdf | 2026-10-02T05:22:33Z | curl | 7391281a5ad86a55... |
| reports/stage_e9_briefs/pages/fed/g17_20251223.html | https://www.federalreserve.gov/releases/g17/20251223/default.htm | 2026-10-02T05:22:13Z | curl | e67a6005d56e1c87... |
| reports/stage_e9_briefs/pages/fed/g17_20251223.pdf | https://www.federalreserve.gov/releases/g17/20251223/g17.pdf | 2026-10-02T05:22:33Z | curl | 55c56c925ffde7c0... |
| reports/stage_e9_briefs/pages/fed/g17_20260116.html | https://www.federalreserve.gov/releases/g17/20260116/default.htm | 2026-10-02T05:22:14Z | curl | cb3f9081a7f69dbb... |
| reports/stage_e9_briefs/pages/fed/g17_20260116.pdf | https://www.federalreserve.gov/releases/g17/20260116/g17.pdf | 2026-10-02T05:22:33Z | curl | ff5d65e67d045887... |
| reports/stage_e9_briefs/pages/fed/g17_20260218.html | https://www.federalreserve.gov/releases/g17/20260218/default.htm | 2026-10-02T05:22:14Z | curl | fe59b5b554585635... |
| reports/stage_e9_briefs/pages/fed/g17_20260218.pdf | https://www.federalreserve.gov/releases/g17/20260218/g17.pdf | 2026-10-02T05:22:33Z | curl | babb45243d43455e... |
| reports/stage_e9_briefs/pages/fed/g17_20260316.html | https://www.federalreserve.gov/releases/g17/20260316/default.htm | 2026-10-02T05:22:14Z | curl | 0e54f4b03382c21f... |
| reports/stage_e9_briefs/pages/fed/g17_20260316.pdf | https://www.federalreserve.gov/releases/g17/20260316/g17.pdf | 2026-10-02T05:22:34Z | curl | 0ac04ffa63d2e856... |
| reports/stage_e9_briefs/pages/fed/g17_20260416.html | https://www.federalreserve.gov/releases/g17/20260416/default.htm | 2026-10-02T05:22:14Z | curl | 713e8cfdc42ca23f... |
| reports/stage_e9_briefs/pages/fed/g17_20260416.pdf | https://www.federalreserve.gov/releases/g17/20260416/g17.pdf | 2026-10-02T05:22:34Z | curl | f2487e21b16374a6... |
| reports/stage_e9_briefs/pages/fed/g17_20260515.html | https://www.federalreserve.gov/releases/g17/20260515/default.htm | 2026-10-02T05:22:14Z | curl | e891cde5e452b30c... |
| reports/stage_e9_briefs/pages/fed/g17_20260515.pdf | https://www.federalreserve.gov/releases/g17/20260515/g17.pdf | 2026-10-02T05:22:34Z | curl | 30056f96d8b22be9... |
| reports/stage_e9_briefs/pages/fed/g17_20260615.html | https://www.federalreserve.gov/releases/g17/20260615/default.htm | 2026-10-02T05:22:14Z | curl | 93ca49b48131393a... |
| reports/stage_e9_briefs/pages/fed/g17_20260615.pdf | https://www.federalreserve.gov/releases/g17/20260615/g17.pdf | 2026-10-02T05:22:34Z | curl | eacd698a930ceac6... |
| reports/stage_e9_briefs/pages/fed_fomccalendars.html | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | 2026-10-02T05:21:31Z | curl | f897c8db3241efe3... |
| reports/stage_e9_briefs/pages/fed_g17_release_dates.html | https://www.federalreserve.gov/releases/g17/release_dates.htm | 2026-10-02T05:21:32Z | curl | c1049baff74ae087... |
| reports/stage_e9_briefs/pages/prn_ism_p1.md | https://www.prnewswire.com/news/institute-for-supply-management/?page=1&pagesize=100 | 2026-10-02T05:22:49Z | scrapling extract get | 3e76f75ddde4ebd4... |
| reports/stage_e9_briefs/pages/prn_ism_p2.md | https://www.prnewswire.com/news/institute-for-supply-management/?page=2&pagesize=100 | 2026-10-02T05:22:52Z | scrapling extract get | e2052f441d876caf... |
| reports/stage_e9_briefs/pages/wb_ism_calendar_20251009234426.html | http://web.archive.org/web/20251009234426id_/https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/ | 2026-10-02T05:25:04Z | curl via web.archive.org (live page redirects to an ISM login) | 26d8e944b930c369... |
| reports/stage_e9_briefs/pages/wb_ism_calendar_20260415040000.html | http://web.archive.org/web/20260415040000id_/https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/ | 2026-10-02T05:24:45Z | curl via web.archive.org | a947cbddc4b95533... |
