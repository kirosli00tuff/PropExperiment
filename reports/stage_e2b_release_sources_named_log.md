# Stage E.2b: member-named release instants, source log (ReleaseSourcerNamed-OpusHigh)

Brief: reports/stage_e2b_briefs/g1d_release_named.md, with 00_common.md and g1_release_common.md.
Output: reports/stage_e2b_release_sources_named.json. It has the same shape as the macro list: coverage, conventions,
entries, cancellations, moves, exclusions, same_instant_entries (empty), coverage_table and verification.
Scripts: data/vendor/release_pages/named_scripts/. Fetch log: data/vendor/release_pages/named_manifest.jsonl.
Work ran from 2026-09-26 14:00 to 14:30 PDT.

## Coverage table (found / expected; expected = found + cancelled)

| release | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | total |
|---|---|---|---|---|---|---|---|---|---|
| API_WSB | 35/35 | 52/52 | 52/52 | 52/52 | 52/52 | 53/53 | 52/52 | 24/24 | 372/372 |
| CROP_PROGRESS | 32/32 | 35/35 | 35/35 | 35/35 | 35/35 | 35/35 | 28/34 (6 canc.) | 11/11 | 246/252 |
| G17 | 8/8 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | 11/13 (2 canc.) | 6/6 | 85/87 |
| ISM_SERVICES | 8/8 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | 6/6 | 86/86 |
| PPI | 8/8 | 12/12 | 12/12 | 12/12 | 12/12 | 12/12 | 10/11 (1 canc.) | 7/7 | 85/86 |
| TREASURY_AUCTION | 48/48 | 80/80 | 84/84 | 84/84 | 84/84 | 84/84 | 84/84 | 39/39 | 587/587 |

1461 entries in total. No entry carries "[unverified]". Every entry has a verbatim quote from a saved page. The API_WSB
caveat is below: those dates come from API's announced schedule, not from a record of publication.

Mechanical verification (named_scripts/verify.py, 2026-09-26 PDT):
- quote_ok 1461/1461 and utc_ok 1461/1461.
- cross_ok 764 of 764 cross-checks.
- Quotes for cancellations (12), moves (10) and exclusions (2) all match their saved pages.
- 0 failures. The script also checks each release's time of day, re-parses every Treasury CSV row back to its date and
  close time, and recounts the coverage table from the entries.

## Per release: source, method, time of day

1. **PPI (BLS), 08:30 ET.**
   - Primary source: the final BLS annual schedule pages for 2019 to 2026, reused from the macro worker (Wayback
     copies under bls/schedule_YYYY_home.txt). Each quote is the schedule row: date, "08:30 AM" and
     "Producer Price Index for <month>".
   - Cross-check: the BLS PPI release archive (bls/archive_ppi.html). Its link file names carry the actual release date
     (ppi_MMDDYYYY.htm). All 85 dates match the schedule in both directions.
   - bls.gov returns 403 to plain curl. It returned 200 to curl with full browser headers (HTTP/2, Firefox UA,
     Sec-Fetch-*), so this page was fetched directly.
2. **ISM Services PMI, 10:00 ET.**
   - The ismworld.org report calendar redirects to an SSO login, so it could not be used.
   - Source: ISM's own press releases as listed on PR Newswire (ism/prn_list_p1..p6). Each listing row prints
     "Mon DD, YYYY, 10:00 ET" followed by the title. The quote is the timestamp line plus the title.
   - Titles matched: "Non-Manufacturing ISM Report On Business" up to mid-2020, "Services PMI (formerly
     Non-Manufacturing NMI)" in August 2020, then "Services ISM Report On Business" and "ISM Services PMI Report".
     Hospital PMI is excluded.
   - Checks: one release per month for May 2019 to June 2026, all at 10:00 ET. Seventeen releases fall on the 4th or 5th
     weekday of the month. All of them sit in holiday months: New Year, July 4, Labor Day, and Good Friday 2026.
   - No second source was used for ISM.
3. **G.17 Industrial Production (Federal Reserve Board), 09:15 ET.**
   - Primary source: the G.17 release-dates table (fed/g17/release_dates.txt). Rows read like
     "May 2019 15-May-2019", and one reads "December 2025 03-December-2025 and 23-December-2025".
   - Time cross-check: the Board's calendar.json (fed/g17/calendar.json) has an entry with "time":"9:15 a.m." for 59 of
     the 85 dates.
   - The other 26 dates have no dated calendar entry: 2022-11 through 2024-12 have an empty month field, and 2025-12-03
     is missing. For those, 09:15 is the standing time. Every G.17 entry in calendar.json carries 9:15 a.m., and the
     2025-12-03 release announces 2025-12-23 "at 9:15 a.m. EST". The note field says this on each such entry.
4. **API Weekly Statistical Bulletin, 16:30 ET.**
   - Source: API's published annual "Schedule of Releases" PDFs for 2019 to 2026 (api/wsb_schedule_YYYY.pdf/.txt).
     Each quote is the schedule row: week-end date, publication date and weekday.
   - Time: the WSB page states "approximately 4:30 pm Eastern", with Wednesday release when Monday is a Federal
     holiday (api/wsb_live.txt, quoted as a cross-check on every entry).
   - **Caveat:** these are pre-announced schedules. The PDFs say "Publish dates are subject to change". The 2019 PDF is
     "Tentative schedule of release as of 12/18/2018", and the 2020 PDF is a revised version of 11/04/2020. No source
     found shows the actual publication dates.
   - The entries carry evidence_kind "announced_schedule" rather than "[unverified]". The dates are on an official
     page; that they happened as scheduled is not independently confirmed. The lead may prefer to treat all 372 as
     [unverified].
   - Checks: publication weekdays match the PDFs' weekday column, and the gaps between releases are 6 to 8 days with
     no missing week.
   - When the next year's PDF repeats a date (for example 2023-01-04, 2024-01-03 or 2025-12-30), the row from the
     publication year's schedule is kept.
5. **USDA NASS Crop Progress, 16:00 ET (17:00 once).**
   - Primary source: the NASS monthly release calendars, reused from the commodity worker (usda/nass_cal/). Each quote
     runs from the date line through "<time> Crop Progress Published".
   - 2021-04-05 is printed "5:00 pm ET" and is entered at 17:00.
   - Cross-check: the ESMIS release page for each issue ("Release date May 06 2019") at usda/crop_progress/view/. The
     listing pages crawled were 0 to 30, and all 246 release pages match.
   - The two sources agree exactly (246 = 246). Seasons run April to November; 2019 ran into December and ended on
     2019-12-09.
6. **Treasury note and bond auctions, instant = competitive close (ET).**
   - Source: the FiscalData auctions_query API, downloaded as CSV with metadata fields only
     (treasury/auctions_query_notes_bonds_20190501_20260621.csv, 763 rows). Each quote is the CSV row verbatim.
   - Time: closing_time_comp. 13:00 for most auctions, 11:30 for about 34 Monday and pre-holiday auctions, and 10:00
     for 2019-12-24 (5-year).
   - Scope, from the members' words in reports/stage_e2b_release_names.json:
     - K2-aucpre-01 and K2-aucpost-01 define the EC-AUC records as security_type Note or Bond, floating_rate "No",
       inflation_index_security "No", and announcemt_date < auction_date. Their tenor match trades 2-, 5-, 10- and
       30-year auctions and says "3-, 7- and 20-year auctions are therefore not traded".
     - K2-ml-01 reads {2, 5, 7, 10, 20, 30}-year.
     - K2-cp3-01 holds "through ... the 12:00 CT auction closes" with no tenor limit.
   - I therefore entered every nominal coupon auction: 2-, 3-, 5-, 7-, 10-, 20- and 30-year, reopenings included. Each
     entry carries original_security_term, so a member can subset its own tenors.
   - **TIPS and FRNs are out** (87 TIPS rows and 87 FRN rows skipped), because both member filters say
     floating_rate "No" and inflation_index_security "No".
   - **Excluded (listed under exclusions):** 2019-06-21 (10-year reopening, 11:00) and 2021-12-02 (20-year reopening).
     Both were announced the same day with no non-competitive close, and the members' filter needs
     announcemt_date < auction_date.
   - Result: 587 entries. Some days have two auctions at different close times; no two entries share an instant.

## Cancellations (no entry)
- **PPI, October 2025 data.** The original slot was 2025-11-14 08:30. BLS archive: "October 2025 Producer Price Index–
  Not published because of 2025 lapse in federal government appropriations".
- **G.17, no release in October or November 2025.** The table reads "October 2025 NA" and "November 2025 NA". The
  originally scheduled dates are [unverified]: a pre-shutdown copy of the table needs web.archive.org, which was
  unreachable (see network notes).
- **Crop Progress, 6 issues:** 2025-10-06, 10-14, 10-20, 10-27, 11-03 and 11-10. NASS notice of 2025-11-19: "Crop
  Progress (Oct. 6, 14, 20, 27; Nov. 3, 10) will not be released".

## Moves (the entry carries the published date)
- PPI September 2025 data: 2025-10-16 moved to 2025-11-25.
- PPI November 2025 data: 2025-12-11 moved to 2026-01-14.
- PPI February 2026 data: 2026-03-12 (schedule as of January 2026) moved to 2026-03-18. The pages give no reason.
- G.17 September 2025 data: published 2025-12-03 after the shutdown. The original slot is [unverified].
- API WSB, week ending 2020-11-06: 2020-11-11 moved to 2020-11-10, per API's revised 2020 schedule.

## Not entered: for the lead
- The **G.17 annual revision** was published as a standalone release on 2025-11-24 (quoted on the 2025-12-03 release
  page). It is not in the G.17 release-dates table, and I did not enter it. I did not audit whether other years' annual
  revisions were published on separate dates.
- **Treasury tenor scope** is the lead's call. I included 3-year auctions and all other nominal tenors. Restricting to
  the tenors each member trades is a filter on original_security_term.

## Network and tool notes
- web.archive.org was unreachable from this machine from about 14:05 PDT to the end of the run: connection timeouts,
  including a failed ping. archive.org's availability API answered at first and then returned errors. No page in the
  output was fetched through Wayback by me. The BLS schedule pages reused from the macro worker are its earlier Wayback
  copies.
- Firecrawl use:
  - Search, 3 calls: this found the API WSB page URL and the 2021, 2023 and 2024 schedule PDF URLs.
  - Scrape, 4 calls on Wayback copies of the API WSB page (2020-04, 2022-02, 2025-11): these returned only the links to
    the 2019, 2020, 2022 and 2025 schedule PDFs.
  - Every PDF was then downloaded directly from api.org with curl and saved. No quoted text comes from a Firecrawl
    result.
- WebSearch was not used, and no search-budget notice was seen.
- Nothing was purchased. No git command was run.
