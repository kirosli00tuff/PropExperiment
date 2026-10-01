# Stage E.8 Task 1b: release and dated-input check for the K6 members

Worker: ReleaseChecker-OpusMed (worker-medium, opus). Written 2026-10-01 00:20 PDT (07:20 UTC).
Window: trade dates 2025-04-01..2026-06-19. Machine-readable copy with every row, URL, quote,
sha256 and fetch time: `reports/stage_e8_release_check.json`. Evidence pages are saved raw under
`reports/stage_e8_briefs/pages/`. The pages were fetched 2026-10-01 07:07-07:15 UTC (00:07-00:15
PDT). Exact times are in the JSON `sources` block.

Verdict counts:

| Item | Keep | Drop | Unverifiable |
|---|---|---|---|
| A (WASDE calendar rows) | 14 | 0 | 0 |
| B2 (HE/LE limit periods) | 5 | 1 | 0 |
| C (EC-CAL exception dates) | 32 | 0 | 0 |

Search log: 2 WebSearch calls (07:11 and 07:12 UTC). Neither returned a budget or cost notice.
No Firecrawl was used. cmegroup.com returned 403 to curl, and Wayback had no captures of the 2025
and 2026 SER PDFs. The PDFs were fetched as raw bytes through the Scrapling library
(`Fetcher.get`) after `scrapling extract get` wrote the PDF as corrupted text.

## A. WASDE releases (EC-WASDE)

**A1. Published schedules**
- **2025.** Wayback capture 2025-03-11 12:10:21 UTC of the USDA OCE WASDE page (captured before
  2025-04-01), `wb_oce_wasde_20250311121021.html`: "2025 WASDE Release Dates (12:00pm ET) Jan. 10,
  Feb. 11, Mar. 11, Apr. 10, May 12, Jun. 12, Jul. 11, Aug. 12, Sep. 12, Oct. 9, Nov. 10, and
  Dec. 9".
- **2026.** Capture 2025-12-19 23:58:18 UTC (before 2026-01-01), `wb_oce_wasde_20251219235818.html`:
  "2026 WASDE Release Dates (12:00pm ET) In 2026 the WASDE report will be released on Jan. 12,
  Feb. 10, Mar. 10, Apr. 9, May 12, Jun. 11, Jul. 10, Aug. 12, Sep. 11, Oct. 9, Nov. 10, and
  Dec. 10." The live page (`usda_oce_wasde_live.md`) has the same 2026 line.

**A2. Publication record.** Source: the ESMIS listing (`esmis_wasde_pub_p0.md`,
`esmis_wasde_pub_p1.md`) and the saved view pages
`data/vendor/release_pages/usda/esmis_view/wasde_<date>.txt` (the "Release date" line). No ESMIS
page gives a release time.

| Calendar row | Schedule line | ESMIS date | Time (calendar) | Drop rule | Verdict |
|---|---|---|---|---|---|
| 2025-04-10 | Apr. 10 | Apr 10 2025 | 12:00 ET (16:00Z) | matches | keep |
| 2025-05-12 | May 12 | May 12 2025 | 12:00 ET (16:00Z) | matches | keep |
| 2025-06-12 | Jun. 12 | Jun 12 2025 | 12:00 ET | matches | keep |
| 2025-07-11 | Jul. 11 | Jul 11 2025 | 12:00 ET | matches | keep |
| 2025-08-12 | Aug. 12 | Aug 12 2025 | 12:00 ET | matches | keep |
| 2025-09-12 | Sep. 12 | Sep 12 2025 | 12:00 ET | matches | keep |
| 2025-11-14 | Nov. 10 (scheduled) | Nov 14 2025 | 12:00 ET (17:00Z) | differs; notice dated 2025-10-31 found | keep |
| 2025-12-09 | Dec. 9 | Dec 09 2025 | 12:00 ET | matches | keep |
| 2026-01-12 | Jan. 12 | Jan 12 2026 | 12:00 ET | matches | keep |
| 2026-02-10 | Feb. 10 | Feb 10 2026 | 12:00 ET | matches | keep |
| 2026-03-10 | Mar. 10 | Mar 10 2026 | 12:00 ET | matches | keep |
| 2026-04-09 | Apr. 9 | Apr 09 2026 | 12:00 ET | matches | keep |
| 2026-05-12 | May 12 | May 12 2026 | 12:00 ET | matches | keep |
| 2026-06-11 | Jun. 11 | Jun 11 2026 | 12:00 ET | matches | keep |

The instant_utc of all 14 rows equals 12:00 America/New_York on its date (script check, 0
mismatches).

**A3. Known cases**
- **November 2025 (row 2025-11-14).** The schedule date was Nov. 10 (2025 list above). The NASS
  ASB notice https://www.nass.usda.gov/Newsroom/Notices/2025/10-31-2025.php reads: "Crop Production
  – November 14, 2025 (previously scheduled for November 10, 2025)" and "The World Agricultural
  Outlook Board will release the World Agricultural Supply and Demand Estimates (WASDE) in
  conjunction with the Crop Production release on November 14th." and "Adjusted release dates are
  due to the lapse in appropriations."
  - The notice date is 2025-10-31. The NASS notices index line reads "10/31/25 [USDA's National
    Agricultural Statistics Service (NASS) will release key data in November]"
    (`nass_notice_2025-10-31_live.md`), and a Wayback capture taken 2025-11-07 14:35:38 UTC already
    holds the WASDE sentence (`wb_nass_notice_2025-10-31_20251107143538.html`).
  - The notice is dated before 2025-11-14, so the row is kept.
  - The FAS notice (`fas_reschedule_notice.txt`) and `nass_notice_2025-11-19.txt` say nothing about
    the WASDE date (grep).
- **October 2025.** Scheduled Oct. 9 (2025 list). It was not published:
  - ESMIS's month filter reads "December 2025November 2025September 2025", with no October 2025.
  - The ESMIS listing goes from Nov 14 2025 straight to Sep 12 2025.
  - The post-lapse OCE 2025 list (capture 2025-12-19) reads "... Aug. 12, Sep. 12, Nov. 14, and
    Dec. 9".
  - The calendar has no October 2025 row. Its `cancellations` entry says "no October 2025 WASDE
    was published". There is nothing to drop.

**A4. Time.** All 14 rows are at 12:00 ET (11:00 CT), per the schedule headers "(12:00pm ET)". For
Nov 14, the post-change 2025 list carries the same header. No row is at another time.

**A5. WASDEs missing from the calendar.** None. ESMIS lists exactly the 14 calendar dates in the
window. One item is recorded for the lead: the ESMIS files for 2026-05-12 and 2026-06-11 are named
`wasde0526v2` and `wasde0626v2`, and the 2026-05-12 view URL ends in `-0`. The release dates are
unchanged.

## B. HE and LE price limits (K6-limitcont-01, initial limit only)

**B1. Table periods that intersect 2025-03-25..2026-06-19** (rules/price_limits.py LIMITS):

| Root | Period | Amount (USD/lb) | Status | Table sources |
|---|---|---|---|---|
| HE | 2024-09-13..2025-08-29 | 0.0400 | sourced | pl_20240913105737, pl_20250829060023 |
| HE | 2025-08-30..2025-09-01 | 0.0400 | bracketed | pl_20250829060023, pl_20250830034814 |
| HE | 2025-09-02..2026-06-19 | 0.0475 | sourced | pl_20250830034814, pl_20260820062901 |
| LE | 2024-11-06..2025-06-01 | 0.0650 | sourced | pl_20241106132409, pl_20250527172431 |
| LE | 2025-06-02..2026-05-18 | 0.0725 | sourced | cme_livestock_notices, pl_20250604005334, pl_20260516231307 |
| LE | 2026-05-19..2026-06-19 | 0.0725 | bracketed | cme_livestock_notices, pl_20260820062901 |

Per-date rows: 306 livestock trade dates x 2 roots = 612 rows (JSON `B.B1_rows`).
- HE: 0.0400 on 105 dates, 0.0475 on 201.
- LE: 0.0650 on 42 dates, 0.0725 sourced on 242, 0.0725 bracketed on 22.
- Rows where the table differs from CME's text: 14, all LE, trade dates 2026-06-01..2026-06-18.

**B2. Checks against CME's own text.** The E.2a capture files no longer exist (the E.2a scratchpad
cache under /tmp is gone). For that reason the E.2a capture values were read from
`reports/stage_e2a_price_limits.json` `captures_parsed`, and CME's Special Executive Reports were
fetched fresh.

| Period | Table | CME text | Verdict |
|---|---|---|---|
| HE 2024-09-13..2025-08-29 | 0.0400 | SER-9609 (Aug 28, 2025) "Current Initial Price Limit" $0.04/lb.; SER-9424 (Aug 29, 2024) new initial $0.04/lb. "effective on trade date September 3, 2024 ... until the first trading day in September 2025" | keep |
| HE 2025-08-30..2025-09-01 (bracketed) | 0.0400 | SER-9609: "Effective Sunday, August 31, 2025 for trade date Tuesday, September 2, 2025*" and "*Monday, September 1, 2025 is a U.S. holiday". $0.04 stays in force until 2025-09-02, and the period holds no trade date (Sat, Sun, Labor Day). | keep |
| HE 2025-09-02..2026-06-19 | 0.0475 | SER-9609: "The new futures price limits effective on trade date September 2, 2025 ... will remain in effect until the first trading day in September 2026", Lean Hog new initial $0.0475/lb.; SER-9791 (Aug 18, 2026) "Current Initial Price Limit" $0.0475/lb. | keep |
| LE 2024-11-06..2025-06-01 | 0.0650 | SER-9568 (May 22, 2025) current initial $0.0650/lb.; SER-9426 (Sep 9, 2024) decreased initial $0.065/lb. "effective on trade date Friday, October 25, 2024" | keep |
| LE 2025-06-02..2026-05-18 | 0.0725 | SER-9568: "Effective, Sunday June 1, 2025 for trade date Monday, June 2, 2025", new initial $0.0725/lb.; SER-9736 (May 14, 2026) current initial $0.0725/lb. | keep |
| **LE 2026-05-19..2026-06-19 (bracketed)** | **0.0725** | SER-9736: "Effective, Sunday May 31, 2026 for trade date Monday, June 1, 2026, Chicago Mercantile Exchange Inc. ("CME") will reset price limits for Live Cattle", with Live Cattle current $0.0725/lb. and **new initial (effective 6/1/2026) $0.0850/lb.**, new expanded $0.1275/lb. | **drop** |

What CME's text gives on each trade date of the two bracketed periods:
- **HE 2025-08-30..09-01:** $0.04, and no trade dates.
- **LE 2026-05-19..2026-05-29** (8 trade dates): $0.0725, the same as the table.
- **LE 2026-06-01..2026-06-18** (14 trade dates): $0.0850. The table has $0.0725.

Notes for the lead. Both are outside the window and get no verdict:
- **HE 2024-09-04..09-12.** CME's $0.04 took effect on trade date 2024-09-03 (SER-9424). The table
  has these dates as bracketed at $0.0375.
- **LE 2024-10-09..10-24.** CME's $0.065 took effect on 2024-10-25 (SER-9426). The table has
  $0.0650 bracketed from 2024-10-09.

**B3. Expanded limits, for the record only (the member does not read them)**
- **HE, Rule 15202.D** (`cme_rulebook_152.pdf`, the current rulebook copy fetched 2026-10-01):
  "Should any Lean Hog futures contract month within the first eight listed contracts subject to
  price limits settle at limit, the daily price limits for all contract months shall increase by 50
  percent the next business day, rounded down to the nearest $0.0025 per pound. ... There shall be
  no price limits on the current month contract during the last two trading days."
  - Trigger: any of the first eight listed months settling at the limit.
  - Expanded amounts: $0.06/lb. through 2025-08-29 (SER-9424); $0.07/lb. from 2025-09-02
    (SER-9609).
- **LE, Rule 10102.D** (`cme_rulebook_101.pdf`): "Should any Live Cattle futures contract month
  within the first four listed contract months subject to price limits settle at limit, or should
  any Feeder Cattle futures contract month within the first four listed contract months subject to
  price limits settle at its limit, the daily price limits for all contract months shall increase on
  the next Business Day by 50 percent ... During the last two trading days in the expiring contract
  month, the daily price limit shall be equal to the expanded price limit".
  - Trigger: any of the first four Live Cattle or Feeder Cattle months settling at the limit.
  - Expanded amounts: $0.0975/lb. through 2025-06-01 (SER-9426); $0.1075/lb. from 2025-06-02
    (SER-9568); $0.1275/lb. from 2026-06-01 (SER-9736).
- **Captures in the window showing an expanded (bold) limit** (E.2a `captures_parsed`): all LE at
  $0.1075.
  - Trade date 2025-08-11: captures 20250811015042, 20250811021552 and 20250811171214.
  - Trade date 2025-10-20: capture 20251018123959.
  - None for HE.
- **CME text the table does not encode** (recorded only): HE has no limit in the expiring month's
  last two trading days; LE uses the expanded limit in the expiring month's last two trading days.

## C. EC-CAL dates (grains and livestock)

Weekdays in the window: 319. Trade dates: 306 for grains and 306 for livestock.
`flatten_time_ct` agrees across ZC, ZW, ZS, ZM and ZL on all 319 weekdays, and across HE and LE on
all 319. Every listed date has a record in the module's `SOURCES` (and in `LATE_OPEN_SOURCES` for
late opens). The source is CME's trading-hours-by-product service, and each record's quote is in
the JSON.

| Date | Grains | Livestock | Verdict |
|---|---|---|---|
| 2025-04-18 Good Friday | closed | closed | keep |
| 2025-05-26 Memorial Day | closed | closed | keep |
| 2025-06-19 Juneteenth | closed | closed | keep |
| 2025-07-04 Independence Day | closed | closed | keep |
| 2025-09-01 Labor Day | closed | closed | keep |
| 2025-11-27 Thanksgiving | closed | closed | keep |
| 2025-11-28 | halt 12:05, late open 08:30 (no evening session), F 11:45 | halt 12:05 (LE service: "eventTime":"12:05","marketEventType":"closed"), F 11:45 | keep |
| 2025-12-24 | halt 12:05, F 11:45 | halt 12:15 (LE service: "eventTime":"12:15","marketEventType":"closed"), F 11:45 | keep |
| 2025-12-25 Christmas | closed | closed | keep |
| 2025-12-26 | late open 08:30 | (none) | keep |
| 2026-01-01 New Year | closed | closed | keep |
| 2026-01-02 | late open 08:30 | (none) | keep |
| 2026-01-19 MLK Day | closed | closed | keep |
| 2026-02-16 Presidents Day | closed | closed | keep |
| 2026-04-03 Good Friday | closed | closed | keep |
| 2026-05-25 Memorial Day | closed | closed | keep |
| 2026-06-19 Juneteenth | closed | closed | keep |

There are 17 grain rows and 15 livestock rows. On the four halt days, F = 11:45 comes from
`day_rule` reason "Topstep close-by 11:45 (topstep_8284222_2025)". Every other trade date has
F = 13:18 (grains) or 13:03 (livestock).

## D. Other dated inputs

- **Catalog grep** (`reports/stage_e0_catalog_K6.md` lines 233-744). No active member's rule reads
  a release other than WASDE, or any release value.
  - wasdepre (line 630) and wasdepost (line 706) read EC-WASDE dates only.
  - limitcont reads EC-LIM and EC-CAL (line 499).
  - cp1 (238), cp2 (289) and cp3 (337) read their own vehicle.
  - crushgap reads ZS, ZM and ZL bars and EC-CAL (383).
  - **Flag for the lead:** cp2's "Data needed" (lines 332-333) lists "EC-CAL, EC-USDA, EC-FOMC
    (harness), EC-LIM". Its "Data fields read" (line 313) names no release.
- **Frozen calendar rows in the research window whose products include a K6 root** (harness
  inputs, counted only):

  | Release | Rows | Local time |
  |---|---|---|
  | WASDE | 14 | 12:00 ET |
  | CROP | 14 | 12:00 ET |
  | CROP_PROGRESS | 39 | 16:00 ET |
  | FOMC | 10 | 14:00 ET |
  | CROP_ANNUAL | 1 | 12:00 ET |
  | Total | 78 | |

- **Dates that are both a WASDE date and an FOMC date:** none. The FOMC dates are 2025-05-07,
  06-18, 07-30, 09-17, 10-29, 12-10, 2026-01-28, 03-18, 04-29 and 06-17.

## Not done or not verifiable

- I could not re-open the E.2a capture HTML files (the cache is gone). Their values come from the
  E.2a JSON. Each B2 verdict rests on the SERs fetched in this task.
- The rulebook chapters are the current (2026-10-01) copies, not copies dated within the window.
  SER-9568 says Rule 101X02.D was last amended effective 2024-10-25, which is before the window.
