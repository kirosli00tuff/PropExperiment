# Stage E.7 Task 1b: external and dated inputs of the K1 members (release check)

Worker: ReleaseChecker-OpusMed (worker-medium, opus). Written 2026-09-28, times PDT unless marked
UTC. Machine-readable twin: reports/stage_e7_release_check.json. Evidence pages:
reports/stage_e7_briefs/pages/ (sha256 per page in the JSON, key `evidence_pages`). WebSearch was not
used (0 calls). No budget or cost notice was met.

Verdicts: keep / drop / unverifiable per row. Where the brief's keep rule is not met, the specific
problem is listed and the ruling is left to the lead.

## A. VXN daily history (Cboe, catalog C9)

### A1. Fetch

| Field | Value |
|---|---|
| URL requested | https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv |
| URL served | https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv (HTTP 307 then 200, text/csv) |
| Saved | data/vendor/index_history/vxn/VXN_History.csv (unmodified) |
| Fetched | 2026-09-28 00:55:48 PDT (07:55:48Z) |
| sha256 | f1b00135c4922ea756cd22cfeaa1d483700a6aed580f8da562f61574b5e1cdcc |
| Bytes | 218,655 |
| Last-Modified | Fri, 25 Sep 2026 22:01:14 GMT |
| Manifest | data/vendor/index_history/vxn/manifest.jsonl (7 lines: the 307 attempt, the 200 fetch, 3 Wayback copies, the failed FRED curl, the FRED scrapling fetch). data/vendor/index_history/manifest.jsonl not touched. |

Free, no key, curl with a browser User-Agent. The first attempt without `-L` got only the 307.

### A2. Parse (counts only)

| Check | Result |
|---|---|
| Header | DATE,OPEN,HIGH,LOW,CLOSE |
| Date format | MM/DD/YYYY |
| First / last date | 2009-09-14 / 2026-09-25 |
| Rows | 4,287 |
| CLOSE parses as decimal | all 4,287; 6 decimals each; none has a nonzero 3rd-6th decimal |
| Duplicate / non-increasing dates | 0 / 0 |
| Weekend rows | 0 |
| Blank / non-positive values (O,H,L,C) | 0 / 0 |
| Rows with O = H = L = C | 12. Three fall in the span: 2020-10-16 (35.02 on all four; prior close 34.54; NYSE open), 2021-04-02 and 2021-12-24 (both carry the prior day's close) |

### A3. Coverage 2019-04-30..2026-06-19

Weekdays 1,864; rows 1,797; weekdays with no row 67.

NYSE full closures in the span come from the NYSE holidays page: Wayback captures 2019-01-07
(2019 column), 2020-01-22 (2020), 2021-01-11 (2021), 2022-01-05 (2022, 2023), 2024-01-11 (2024,
2025), the live page (2026), plus the ICE notice for 2025-01-09 ("will close all NYSE Group equity
and options markets on Thursday, January 9, 2025, in observance of the National Day of Mourning").
That's 69 closures. No Cboe holiday calendar was fetched. Cboe's closure days are taken as the NYSE
list (inference).

| Class | Count | Dates |
|---|---|---|
| Missing on an NYSE closure | 67 | all 67 missing weekdays (full list with the equity-calendar fields in the JSON, `A_vxn.missing_weekday_list`) |
| True gap (missing on an NYSE-open day) | 0 | none |
| Row on an NYSE-closed day | 2 | 2021-04-02 (Good Friday; row 23.21 x4 = 04-01 close), 2021-12-24 (Christmas observed; row 21.32 x4 = 12-23 close) |

The 67 missing days against the equity calendar (`load_group_calendar("equity")`):
- 48 are trade dates with a 12:00 CT early halt.
- 2 are trade dates with an 08:15 halt (2023-04-07, 2026-04-03, Good Friday NFP).
- 1 is a trade date with an 08:30 halt (2025-01-09).
- 16 are **not** trade dates (CME full closures: Christmas, New Year, Good Friday without NFP).

So the brief's expectation ("those holidays are equity-calendar trade dates with an early halt")
holds for 51 of the 67, not all. Of the two rows on closed days, 2021-04-02 is an equity trade date
(halt 08:15) and 2021-12-24 is not a trade date.

Research window (trade dates 2025-04-01..2026-06-19):
- 10 equity trade dates have no VXN row: 2025-05-26, 06-19, 07-04, 09-01, 11-27, 2026-01-19,
  02-16, 04-03, 05-25, 06-19.
- 9 of the 316 window trade dates read a d-1 with no VXN row, so the member has "no trade on d":
  2025-05-27, 06-20, 07-07, 09-02, 11-28, 2026-01-20, 02-17, 04-06, 05-26.

### A4. Point-in-time / revisions

- Wayback CDX for cdn.cboe.com lists 3 captures: 2022-07-14, 2022-12-30 and 2024-04-19. There is
  **none in 2025 or 2026**. The CDX for cdn-api.cboe.com returned 0 captures. An earlier CDX query
  at about 07:58Z got an Internet Archive "Temporarily Offline" page. The retries worked.
- The copies are saved under data/vendor/index_history/vxn/wayback/.

| Copy | Rows | Last row | Common dates | CLOSE diffs | O/H/L diffs |
|---|---|---|---|---|---|
| wb 20220714220323 | 3,223 | 2022-07-13 | 3,223 | 0 | 0 |
| wb 20221230140502 | 3,341 | 2022-12-29 | 3,341 | 0 | 0 |
| wb 20240419091234 | 3,667 | 2024-04-18 | 3,667 | **1**: 2024-02-01 CLOSE 11.200000 (capture) vs 17.330000 (now); LOW is 11.200000 in both | 0 |
| FRED VXNCLS (current, not PIT) | 6,447 values + 242 blanks | 2026-09-22 | 4,284 | 0 at 2 dp; 1,797 span dates, 0 diffs; FRED's in-span blanks = the same 67 dates | n/a |

FRED fetch: curl failed with an HTTP/2 stream error, and a retry over HTTP/1.1 hung and was killed.
`scrapling extract get` then returned 200. That copy is text output saved as fred_VXNCLS.csv, so it
may not be byte-identical to the HTTP body. FRED carries the same values on 2021-04-02, 2021-12-24
and 2024-02-01 as the current Cboe file.

No revision check is possible for window dates: no 2025-2026 capture exists, and FRED is a current
copy.

### A5. Publication time of day D's close

| Evidence | Observation | Before 08:30 CT on D+1? |
|---|---|---|
| Last-Modified of the file | 2026-09-25 22:01:14Z = 17:01 CDT on D, last row 2026-09-25 | yes |
| Wayback 2022-12-30 14:05:02Z (08:05 CST) | last row 2022-12-29 | yes |
| Wayback 2024-04-19 09:12:34Z (04:12 CDT) | last row 2024-04-18 | yes |
| Wayback 2022-07-14 22:03:23Z (17:03 CDT) | last row 2022-07-13 (D's row not yet present same evening) | not informative for D+1 |
| Cboe statement | none found. The vix_historical_data page says "VIX Index data for 1990 to present (Updated Daily)" (VIX only; VXN not in its list). The VXN dashboard page is JavaScript; grep found no timing text | n/a |
| FRED (secondary, not the member's source) | "2026-09-22: 20.18 ... Updated: Sep 23, 2026 8:37 AM CDT" | no (FRED lags) |

Every Cboe-file observation puts publication before 08:30 CT on the next trade date: 3 of 3
informative observations, one of them only 25 minutes before. No Cboe statement exists, so the
timing is observational only (unverifiable as a stated guarantee).

### Verdict A

The brief's keep rule is not met in full. These are the specific problems, for the lead to rule on:
1. **Revision found:** 2024-02-01 CLOSE was 11.20 in the 2024-04-19 capture and is 17.33 now. This
   is before the window.
2. **Two carry-forward rows on NYSE-closed days:** 2021-04-02 and 2021-12-24. Both are before the
   window. 2021-04-02 is an equity trade date, so a d = 2021-04-05 read gets the carried 23.21.
3. **No point-in-time copy for 2025-2026:** window values are checked only against FRED's current
   copy (0 diffs).
4. **No Cboe statement on publication time:** 3 observations are consistent with before 08:30 CT on
   D+1.

What passes: obtained free, and there is no gap on any NYSE-open day in 2019-04-30..2026-06-19.

## B. CPI instants in the window (D9.12)

The source is reports/stage_e2b_release_calendar.json, key `releases`, rows with `"cpi": true`
between 2025-04-01 and 2026-06-19. There are 14 rows, all release "CPI", 08:30 America/New_York.
The engine (screening/stage_e_rules.py 159-167) takes every cpi row whatever its `products`. The 14
rows list MNQ (not M2K or MYM) in `products`.

Schedule quotes come from the saved BLS pages
data/vendor/release_pages/bls/schedule_2025_home.txt and schedule_2026_home.txt (line given). Each
page carries "NOTE: All times on calendar are Eastern Time."

| id | instant_utc | Schedule line | Quote | Verdict |
|---|---|---|---|---|
| CPI-2025-04-10 | 2025-04-10T12:30Z | 2025:453 | Thursday, April 10, 2025 / 08:30 AM / Consumer Price Index | keep |
| CPI-2025-05-13 | 2025-05-13T12:30Z | 2025:526 | Tuesday, May 13, 2025 / 08:30 AM / Consumer Price Index | keep |
| CPI-2025-06-11 | 2025-06-11T12:30Z | 2025:593 | Wednesday, June 11, 2025 / 08:30 AM / Consumer Price Index | keep |
| CPI-2025-07-15 | 2025-07-15T12:30Z | 2025:654 | Tuesday, July 15, 2025 / 08:30 AM / Consumer Price Index | keep |
| CPI-2025-08-12 | 2025-08-12T12:30Z | 2025:715 | Tuesday, August 12, 2025 / 08:30 AM / Consumer Price Index | keep |
| CPI-2025-09-11 | 2025-09-11T12:30Z | 2025:798 | Thursday, September 11, 2025 / 08:30 AM / Consumer Price Index | keep |
| CPI-2025-10-24 | 2025-10-24T12:30Z | 2025:853 | Friday, October 24, 2025 / 08:30 AM / Consumer Price Index; BLS release: "embargoed until 8:30 a.m. (ET) Friday, October 24, 2025" | keep |
| CPI-2025-12-18 | 2025-12-18T13:30Z | 2025:927 | Thursday, December 18, 2025 / 08:30 AM / Consumer Price Index; BLS release: "embargoed until 8:30 a.m. (ET) Thursday, December 18, 2025" | keep |
| CPI-2026-01-13 | 2026-01-13T13:30Z | 2026:256 | Tuesday, January 13, 2026 / 08:30 AM / Consumer Price Index | keep |
| CPI-2026-02-13 | 2026-02-13T13:30Z | 2026:339 | Friday, February 13, 2026 / 08:30 AM / Consumer Price Index | keep |
| CPI-2026-03-11 | 2026-03-11T12:30Z | 2026:406 | Wednesday, March 11, 2026 / 08:30 AM / Consumer Price Index | keep |
| CPI-2026-04-10 | 2026-04-10T12:30Z | 2026:459 | Friday, April 10, 2026 / 08:30 AM / Consumer Price Index | keep |
| CPI-2026-05-12 | 2026-05-12T12:30Z | 2026:536 | Tuesday, May 12, 2026 / 08:30 AM / Consumer Price Index | keep |
| CPI-2026-06-10 | 2026-06-10T12:30Z | 2026:607 | Wednesday, June 10, 2026 / 08:30 AM / Consumer Price Index | keep |

The UTC offsets match ET: EDT 12:30Z and EST 13:30Z. The 2025-12-18, 2026-01-13 and 2026-02-13 rows
are in EST.

The BLS notices were fetched fresh with `scrapling extract get`, because curl got 403 on every
bls.gov URL:
- pages/bls_archives_cpi_10242025.md (08:04:16Z)
- pages/bls_archives_cpi_12182025.md (08:04:17Z)
- pages/bls_news-release_cpi.md (08:04:18Z)

The BLS CPI archive list gives 14 release dates in the window, identical to the 14 calendar rows. So
no CPI published in the window is missing from the calendar.

The cancelled October 2025 CPI is in the calendar's `cancellations` (originally 2025-11-13 08:30 ET,
"2025 lapse in federal appropriations; not published"). BLS quotes:
- bls_news-release_cpi.md: "October 2025 Consumer Price Index – Not published because of 2025 lapse
  in federal government appropriations"
- bls_archives_cpi_12182025.md: "BLS did not collect survey data for October 2025 due to a lapse in
  appropriations. BLS was unable to retroactively collect these data."

Verdict B: all 14 keep; no missing CPI.

## C. Equity calendar dates the members meet (2025-04-01..2026-06-19, read only)

- 319 weekdays checked. 16 are flagged (not a trade date, early halt, late open, or F != 15:08).
- `rules.sessions.flatten_time_ct` gives the same F for MNQ, M2K and MYM on every weekday (0
  disagreements).
- Citations are quoted from data/calendars/equity.py `SOURCES` (the CME trading-hours-by-product
  service record for ES, via Wayback captures 2024-12-20 and 2026-01-29). The full URL, status quote
  and time quote per date are in the JSON.

| Date | Day | Trade date | Halt CT | Late open | F (all 3) | Name | Citation quote (truncated) | Verdict |
|---|---|---|---|---|---|---|---|---|
| 2025-04-18 | Fri | no | - | - | - | Good Friday | `{"groupCode":"ES","eventDate":"2025-04-18","events":[]}` | keep |
| 2025-05-26 | Mon | yes | 12:00 | - | 11:30 | Memorial Day | `...,"eventDate":"2025-05-26",... "eventTime":"12:00","marketEventType":"preopen"...` | keep |
| 2025-06-19 | Thu | yes | 12:00 | - | 11:30 | Juneteenth | `...,"eventDate":"2025-06-19",... "eventTime":"12:00","marketEventType":"preopen"...` | keep |
| 2025-07-03 | Thu | yes | 12:15 | - | 11:45 | Day before Independence Day | `...,"eventDate":"2025-07-03",... "eventTime":"12:15","marketEventType":"closed"...` | keep |
| 2025-07-04 | Fri | yes | 12:00 | - | 11:30 | Independence Day | `...,"eventDate":"2025-07-04",... "eventTime":"12:00","marketEventType":"closed"...` | keep |
| 2025-09-01 | Mon | yes | 12:00 | - | 11:30 | Labor Day | `...,"eventDate":"2025-09-01",... "eventTime":"12:00","marketEventType":"preopen"...` | keep |
| 2025-11-27 | Thu | yes | 12:00 | - | 11:30 | Thanksgiving | `...,"eventDate":"2025-11-27",... "eventTime":"12:00","marketEventType":"preopen"...` | keep |
| 2025-11-28 | Fri | yes | 12:15 | 07:30 (unscheduled outage) | 11:45 | Day after Thanksgiving | `...,"eventDate":"2025-11-28",... "eventTime":"12:15","marketEventType":"closed"...`; LATE_OPEN_SOURCES: `{"tradingDate":"2025-11-28","eventTime":"07:30","marketEventType":"open"}` | keep |
| 2025-12-24 | Wed | yes | 12:15 | - | 11:45 | Christmas Eve | `...,"eventDate":"2025-12-24",... "eventTime":"12:15","marketEventType":"closed"...` | keep |
| 2025-12-25 | Thu | no | - | - | - | Christmas Day | `...,"eventDate":"2025-12-25","events":[{"tradingDate":"2025-12-26","eventTime":"16:00","marketEventType":"preopen"...` | keep |
| 2026-01-01 | Thu | no | - | - | - | New Year's Day | `...,"eventDate":"2026-01-01","events":[{"tradingDate":"2026-01-02","eventTime":"16:00","marketEventType":"preopen"...` | keep |
| 2026-01-19 | Mon | yes | 12:00 | - | 11:45 | Martin Luther King Jr. Day | `...,"eventDate":"2026-01-19",... "eventTime":"12:00","marketEventType":"preopen"...` | keep |
| 2026-02-16 | Mon | yes | 12:00 | - | 11:45 | Presidents Day | `...,"eventDate":"2026-02-16",... "eventTime":"12:00","marketEventType":"preopen"...` | keep |
| 2026-04-03 | Fri | yes | 08:15 | - | 08:00 | Good Friday (abbreviated, jobs report) | `...,"eventDate":"2026-04-03",... "eventTime":"08:15","marketEventType":"closed"...` | keep |
| 2026-05-25 | Mon | yes | 12:00 | - | 11:45 | Memorial Day | `...,"eventDate":"2026-05-25",... "eventTime":"12:00","marketEventType":"preopen"...` | keep |
| 2026-06-19 | Fri | yes | 12:00 | - | 11:45 | Juneteenth | `...,"eventDate":"2026-06-19",... "eventTime":"12:00","marketEventType":"closed"...` | keep |

Note for the lead (fact, no ruling): on the 2025 12:00 halt days F is 11:30 (halt - 30 min), and on
the 2026 ones 11:45 (halt - 15 min). The 12:15 days in 2025 give 11:45. The lead comes from
rules/sessions.py `TOPSTEP_EARLY_CLOSE_LEAD` (2025: 30 min, 2026: 15 min; lines 208-214), not from
the calendar module. Its citation was not checked here, because it is outside item C.

Verdict C: all 16 dates keep (each cited); no unverifiable date.

## D. Other dated inputs

Every member's "Data fields read" line in reports/stage_e0_catalog_K1.md 216-594 was checked:
- cp1: 252
- cp2: 330
- cp3: 383
- vxnband: 454
- vwap: 556

They read vehicle ohlcv-1m fields and instrument_id; vxnband also reads the VXN close. No active
member (cp1, cp2, cp3, vxnband, vwap) reads a release instant or value. Release words appear only in
each member's harness check items 4-7 (star rules, news, event-minute guard, CPI window) at lines
265-269, 342-347, 393-397, 488-493 and 583-588.

Harness release rows in the window, from reports/stage_e2b_release_calendar.json (count only):

| Release | MNQ | M2K | MYM |
|---|---|---|---|
| FOMC | 10 | 10 | 10 |
| NFP | 14 | 14 | 14 |
| ISM_SERVICES | 15 | 15 | 15 |
| CPI (products field; engine applies all 14 to all three) | 14 | 0 | 0 |

Verdict D: keep (no member reads a release; counts recorded).

## Not finished or not verifiable

- No Wayback capture of the VXN file from 2025 or 2026 exists, so window values have no
  point-in-time check. FRED is a current copy.
- No Cboe statement on VXN publication time was found. A Cboe holiday calendar was not fetched;
  Cboe's closures are taken as the NYSE list.
- The FRED copy was saved from scrapling text output, so it is not guaranteed byte-identical to the
  HTTP body.
- The NYSE Wayback captures of 2023-01-02, 2025-01-09 and 2026-01-01 are JavaScript shells and were
  not used. Their years are covered by the other captures.
