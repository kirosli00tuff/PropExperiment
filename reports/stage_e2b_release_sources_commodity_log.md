# Stage E.2b release calendar: commodity sources log (ReleaseSourcerCommodity-OpusHigh)

Worker: ReleaseSourcerCommodity-OpusHigh (worker-high, opus). Brief: reports/stage_e2b_briefs/g1c_release_commodity.md,
with 00_common.md and g1_release_common.md. Lead additions: WASDE (release "WASDE"; 13:5x PDT), and the resume ruling
of 16:4x PDT for finishing WNGSR without Wayback. Times are PDT (America/Vancouver), 2026-09-26.

Output: reports/stage_e2b_release_sources_commodity.json (coverage, conventions, entries, cancellations, moves,
exclusions, anomalies, ngs_weeks_without_a_saved_page, coverage_table, verification).
Scripts: data/vendor/release_pages/commodity_scripts/ (fetch.py, crawl_*.py, parse_*.py, extra.py, build.py,
finalize.py, verify.py). Pages: data/vendor/release_pages/eia/ and usda/; fetch manifest
data/vendor/release_pages/commodity_manifest.jsonl (url, fetched_url, direct or wayback, fetched_pdt, paths).
Rebuild: `python3 build.py && python3 finalize.py && python3 verify.py` in commodity_scripts/ (system python3, bs4).

## Sources and method per release

WPSR (EIA Weekly Petroleum Status Report). Direct from eia.gov (13:55-14:35).
- Date: the issue page of every archive folder on https://www.eia.gov/petroleum/supply/weekly/archive/ (371 issue
  pages, 2019-05-01..2026-06-17), header quote "Data for week ending <X> | Release Date: <D>".
- Time: EIA's WPSR holiday release schedule (schedule.php). 65 Wayback captures 2019-01..2025-01 plus the current page
  (covers Dec 2024..Nov 2026) were saved before Wayback blocked. For each release date listed as an exception, the row
  from the latest saved capture on or before the release date is used (the schedule changed 11:00 a.m. to 12:00 p.m.
  for 2025 holiday weeks between captures of 2024-12-25 and 2025-01-10; entries note when versions disagree).
  Other weeks: Wednesday 10:30 ET, the standing sentence quoted as a cross-check from the nearest earlier capture.
- Every WPSR release date is either a Wednesday or a holiday-schedule date; no unmatched weekday.
- Two delayed weeks were published together with the following week (one instant each, listed under moves):
  week ending 2022-06-17 (scheduled 2022-06-23 11:00, released 2022-06-29 with week ending 06-24) and week ending
  2023-11-03 (scheduled 2023-11-08, released 2023-11-15 with week ending 11-10). Quotes from the archive notices.

NGS (EIA Weekly Natural Gas Storage Report). The per-week page (ir.eia.gov/ngs/ngs.html, header "for week ending X |
Released: D at T") has no EIA archive; Wayback was the only per-week copy. EIA's history xls files (ngshistory,
cvhistory, revisions) carry week-ending dates only, no report dates (checked). Wayback refused connections
(HTTP 000 / connection refused on 443 and 80, archive.org API 429) from about 14:00; retries at 14:0x-14:46 (poll every
45-60 s), 16:43, 16:45 and a last one at 16:55, all HTTP 000. No Wayback data was used for NGS. Per lead ruling the entries use EIA's
own pages, each with an evidence_class:
- holiday_schedule_row (7, verified): EIA's current WNGSR holiday schedule (ir.eia.gov/ngs/schedule.html) rows for
  2025-2026 (e.g. "November 26, 2025 Wednesday 12:00 p.m. Thanksgiving Day"); each row mapped to the storage week whose
  normal Thursday it replaces.
- eia_notice (1, verified): NGWU of 2023-07-06: "We will release our Weekly Natural Gas Storage Report on Friday,
  July 7, at 10:30 a.m. eastern time."
- standing_rule_ngwu_corroborated (315, [unverified]): Thursday 10:30 ET from the quoted rule "The standard release
  time and day of the week will be at 10:30 a.m. eastern time on Thursdays"; the EIA Natural Gas Weekly Update dated
  that Thursday already reports the week's storage figure (header and storage sentence quoted as cross-checks).
  324 NGWU pages were saved (2019-05-02..2026-01-22; NGWU ends there).
- standing_rule_only (40, [unverified]): same rule, no NGWU for that week (NGWU skipped holiday weeks, 2020-04-16 lacks
  a header, the 2023-11-09/16 NGWUs carry no storage figure, and NGWU stops after 2026-01-22: 21 of these are
  2026-01-29..2026-06-18). Holiday-week risk: late-December/early-January weeks, 2020-06-25, 2020-07-02, 2023-09-14,
  2023-11-09, 2023-11-16, 2024-03-07, 2024-06-20 (Juneteenth Wednesday) are rule placeholders.
- inferred_thursday_holiday_shift (10, [unverified]): the normal Thursday was a federal holiday (2019-07-04,
  Thanksgiving 2019-2024, 2020-12-24 closure, 2021-11-11 Veterans Day, 2024-07-04). Entered as Wednesday 12:00 ET,
  EIA's published practice for a Thursday holiday in the 2025-2026 rows (analog row quoted). A Thursday instant
  would fall on a closed day, so a rule placeholder there would certainly be wrong; the lead may prefer to drop these
  or treat the whole Wednesday-Thursday window as event time.
- Known inconsistency: NGWU dated 2025-11-13 already reports week ending 2025-11-07, while EIA's schedule gives that
  WNGSR as Friday 2025-11-14 10:30 (the schedule row is used). NGWU dates are therefore corroboration, not proof.

CROP and CROP_ANNUAL (USDA NASS). Direct from nass.usda.gov and esmis.nal.usda.gov.
- NASS Agricultural Statistics Board calendar, monthly list view, 86 months 2019-05..2026-06
  (reports_by_date.php?view=l&month=MM&year=YYYY): quote from the date header to the report name, e.g.
  "Fri, 05/10/19 12:00 pm ET Cotton Ginnings - Ann. Published 12:00 pm ET Crop Production"; every row has status
  "Published" and time 12:00 pm ET. Cross-check: the ESMIS Crop Production release listing (dates match 85/85).
- Annual summary: NASS labels "Crop Production - Ann." / "Crop Production Annual Summary" (ESMIS publication
  "Crop Production Annual Summary"); 7 entries (January 2020-2026), each the same instant as that January's monthly
  Crop Production. Kept as release CROP_ANNUAL; collapse by instant_utc if one row per instant is wanted.
- October 2025 Crop Production cancelled; November 2025 moved from 11-10 to 11-14 (NASS notices of 2025-11-19 and
  2025-10-31, quoted).

WASDE (USDA WAOB; lead addition). Date: the ESMIS WASDE release page per release ("Release date May 12 2026"; 85
pages). Time: USDA WASDE FAQ "Lockup is lifted when the report is released at 12:00 noon Eastern time." (per-year
USDA WASDE release-date pages from earlier years exist only in Wayback and were not retrieved). Every WASDE date equals
a Crop Production date (same instant, separate entries). October 2025 WASDE: logged as cancelled; no saved USDA page
states it directly (the WASDE page's shutdown notice is only in Wayback); evidence is the ESMIS listing (Sep 12 2025
is followed by Nov 14 2025, the date filter has no October 2025) plus the NASS notices. November 2025 moved to 11-14
("... will release the World Agricultural Supply and Demand Estimates (WASDE) in conjunction with the Crop Production
release on November 14th.").

## Coverage table (release x year)

| release | year | expected | found | unverified | cancelled | moved | merged delayed weeks |
|---|---|---|---|---|---|---|---|
| WPSR | 2019 | 35 | 35 | 0 | 0 | 0 | 0 |
| WPSR | 2020 | 53 | 53 | 0 | 0 | 0 | 0 |
| WPSR | 2021 | 52 | 52 | 0 | 0 | 0 | 0 |
| WPSR | 2022 | 51 | 51 | 0 | 0 | 0 | 1 |
| WPSR | 2023 | 51 | 51 | 0 | 0 | 0 | 1 |
| WPSR | 2024 | 52 | 52 | 0 | 0 | 0 | 0 |
| WPSR | 2025 | 53 | 53 | 0 | 0 | 0 | 0 |
| WPSR | 2026 | 24 | 24 | 0 | 0 | 0 | 0 |
| NGS | 2019 | 35 | 0 | 35 | 0 | 0 | 0 |
| NGS | 2020 | 53 | 0 | 53 | 0 | 0 | 0 |
| NGS | 2021 | 52 | 0 | 52 | 0 | 0 | 0 |
| NGS | 2022 | 52 | 0 | 52 | 0 | 0 | 0 |
| NGS | 2023 | 52 | 1 | 51 | 0 | 0 | 0 |
| NGS | 2024 | 52 | 0 | 52 | 0 | 0 | 0 |
| NGS | 2025 | 53 | 7 | 46 | 0 | 0 | 0 |
| NGS | 2026 | 24 | 0 | 24 | 0 | 0 | 0 |
| CROP | 2019 | 8 | 8 | 0 | 0 | 0 | 0 |
| CROP | 2020-2024 | 12 each | 12 each | 0 | 0 | 0 | 0 |
| CROP | 2025 | 12 | 11 | 0 | 1 | 1 | 0 |
| CROP | 2026 | 6 | 6 | 0 | 0 | 0 | 0 |
| CROP_ANNUAL | 2020-2026 | 1 each | 1 each | 0 | 0 | 0 | 0 |
| WASDE | 2019 | 8 | 8 | 0 | 0 | 0 | 0 |
| WASDE | 2020-2024 | 12 each | 12 each | 0 | 0 | 0 | 0 |
| WASDE | 2025 | 12 | 11 | 0 | 1 | 1 | 0 |
| WASDE | 2026 | 6 | 6 | 0 | 0 | 0 | 0 |

"expected" counts entries plus logged cancellations; "merged delayed weeks" are weekly data published inside a later
release instant (no separate entry). NGS by evidence class per year is in the JSON coverage_table (by_evidence_class).
Total entries 921: WPSR 371, NGS 373, CROP 85, CROP_ANNUAL 7, WASDE 85. Unverified: 365 (all NGS).

## Verification (verify.py)

Whitespace-normalised substring match of every quote in its saved page; the quote must show the entry date (except the
365 NGS rule entries, whose quote is the standing rule); instant_utc recomputed from date + time_local + tz with
zoneinfo; cross-check, cancellation and move quotes matched the same way; WPSR and NGS week-ending sequences checked for
7-day contiguity (entries plus merged delayed weeks). Result: quote_ok 921/921, utc_ok 921/921, cross_ok 1193/1193,
cancellations 4/4, moves 8/8, WPSR weeks 373 and NGS weeks 373 contiguous, failures none.

## Timeline and incidents

- 13:50 start; EIA and USDA sites reachable directly (no blocking, unlike bls.gov).
- 13:55-14:35 WPSR issue pages (about 8 s per eia.gov response; 3 parallel shards, 1 s sleep each).
- 13:58 Wayback captures of the WPSR schedule (65 of 137) and WNGSR schedule (0 of 33) fetched, then Wayback began
  refusing connections (the WPSR crawl, the schedule crawl and possibly other workers shared the IP). It stayed down
  through 16:45 PDT.
- 14:0x one Firecrawl web search (2 credits) to locate WASDE October 2025 notices; the govdelivery bulletin it found
  (usda/usdaoc_bulletin_900c29.txt) turned out to be about 2013 and is not used.
- About 15:07 the session hit the usage limit; resumed 16:4x under the lead's ruling for NGS.
- Not used: data/vendor/release_pages/usda/fas_reschedule_notice.txt (no WASDE content).

## Open questions for the lead

1. NGS: 365 of 373 entries are rule-derived and [unverified]. If Wayback comes back, commodity_scripts/crawl_ngs.py
   (throttled binary search over saved CDX lists in eia/ngs_cdx/) fills ngs_found.json and build.py then uses the
   WNGSR page header for those weeks automatically. Throttle to at most about 10 requests per minute.
2. NGS inferred holiday shifts (10) and holiday-week rule placeholders: keep, drop, or widen to a window.
3. CROP_ANNUAL duplicates the January CROP instant; keep or collapse.
4. WPSR 2025 holiday times: the 12:00 p.m. rows come from the 2025-01-10 capture and the current page; any mid-2025
   change is unseen (later 2025 Wayback captures were not retrieved).
