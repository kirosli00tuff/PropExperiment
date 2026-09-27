# Stage E.2b release sources, macro (NFP, CPI, FOMC): worker log

Worker: ReleaseSourcerMacro-OpusHigh (worker-high, opus). Brief: reports/stage_e2b_briefs/g1b_release_macro.md.
Run 2026-09-26, 13:30 to 13:50 PDT. Output: reports/stage_e2b_release_sources_macro.json.

## Result

227 release instants from 2019-05-01 through 2026-06-21, each with a verbatim quote from a saved official page.
0 entries are marked [unverified]. 3 cancellations and 6 moved releases are logged, plus 8 FOMC exclusions.

| Release | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 | Total |
|---|---|---|---|---|---|---|---|---|---|
| NFP (Employment Situation) | 8 | 12 | 12 | 12 | 12 | 12 | 11 | 6 | 85 |
| CPI | 8 | 12 | 12 | 12 | 12 | 12 | 11 | 6 | 85 |
| FOMC statement (scheduled) | 6 | 7 | 8 | 8 | 8 | 8 | 8 | 4 | 57 |

## Stopping-rule table (release x year: expected, found, unverified, cancelled, moved)

Expected means the releases the originally published schedule put in the coverage range. Moved releases count once, at the
date actually published.

| Release | Year | Expected | Found | Unverified | Cancelled | Moved |
|---|---|---|---|---|---|---|
| NFP | 2019 (May-Dec) | 8 | 8 | 0 | 0 | 0 |
| NFP | 2020 | 12 | 12 | 0 | 0 | 0 |
| NFP | 2021 | 12 | 12 | 0 | 0 | 0 |
| NFP | 2022 | 12 | 12 | 0 | 0 | 0 |
| NFP | 2023 | 12 | 12 | 0 | 0 | 0 |
| NFP | 2024 | 12 | 12 | 0 | 0 | 0 |
| NFP | 2025 | 12 | 11 | 0 | 1 | 2 |
| NFP | 2026 (Jan-Jun 21) | 6 | 6 | 0 | 0 | 1 |
| CPI | 2019 (May-Dec) | 8 | 8 | 0 | 0 | 0 |
| CPI | 2020 | 12 | 12 | 0 | 0 | 0 |
| CPI | 2021 | 12 | 12 | 0 | 0 | 0 |
| CPI | 2022 | 12 | 12 | 0 | 0 | 0 |
| CPI | 2023 | 12 | 12 | 0 | 0 | 0 |
| CPI | 2024 | 12 | 12 | 0 | 0 | 0 |
| CPI | 2025 | 12 | 11 | 0 | 1 | 2 |
| CPI | 2026 (Jan-Jun 21) | 6 | 6 | 0 | 0 | 1 |
| FOMC | 2019 (May-Dec) | 6 | 6 | 0 | 0 | 0 |
| FOMC | 2020 | 8 | 7 | 0 | 1 | 0 |
| FOMC | 2021 | 8 | 8 | 0 | 0 | 0 |
| FOMC | 2022 | 8 | 8 | 0 | 0 | 0 |
| FOMC | 2023 | 8 | 8 | 0 | 0 | 0 |
| FOMC | 2024 | 8 | 8 | 0 | 0 | 0 |
| FOMC | 2025 | 8 | 8 | 0 | 0 | 0 |
| FOMC | 2026 (Jan-Jun 21) | 4 | 4 | 0 | 0 | 0 |

Every expected release is an entry with a quote or a logged cancellation. The stopping rule is met.

## Finding for the lead: D.1f omitted one FOMC statement

The regularly scheduled January 28-29, 2020 FOMC meeting (statement released 2020-01-29, "For release at 2:00 p.m. EST")
is not in reports/stage_d1f_release_sources.json, so it is also absent from the frozen
strategy/research/e_calendar_event/_release_table_2019_2024.py. The Fed's historical page lists it as an ordinary meeting
("January 28-29 Meeting - 2020") with a Statement link (monetary20200129a.htm). This matches the discrepancy the D.1f table
docstring already records (its .md heading said 38 FOMC statements, the JSON held 37). The entry FOMC-2020-01-29 is new here
(no "reused_from") and its note names the omission. I did not touch any D.1f file. Whether this affects D.1f results is the
lead's call.

## Sources and fetches

No WebSearch or Firecrawl was used; every page came from a known official URL. Pages are saved under
data/vendor/release_pages/bls/ and data/vendor/release_pages/fed/ (raw .html/.pdf plus stripped .txt). Every fetch is
recorded in data/vendor/release_pages/macro_manifest.jsonl (url, fetched_url, direct or Wayback, fetched time PDT, paths;
83 records, 60 direct and 23 Wayback; the first 2026 BLS fetch was saved gzip-compressed and was re-fetched, and the later
record is the one used).

- federalreserve.gov answers scripted clients, so Fed pages were fetched directly: fomccalendars.htm (2021-2027 panels),
  fomchistorical2019.htm, fomchistorical2020.htm, and the statement press release of every in-range regularly scheduled
  meeting (57 pages, monetaryYYYYMMDDa.htm). fomchistorical2021.htm does not exist yet (404 direct and in Wayback), so
  2021 onward comes from fomccalendars.htm, as in D.1f.
- bls.gov returns 403 to curl, so every BLS page is a Wayback copy (https://web.archive.org/web/<ts>id_/<url>), which the
  release rules allow. Each entry's "fetched_url" gives the snapshot. Pages: the annual schedules
  schedule/2019..2026/home.htm (snapshots of 2026-08-19, and 2026-09-19 for 2026); the 2024 January and February month
  views D.1f cited; the release archives bls/news-release/empsit.htm and cpi.htm (snapshots of 2026-09-05 and 2026-08-30);
  earlier snapshots of schedule/2025/home.htm (2025-09-24) and schedule/2026/home.htm (2026-01-22) to show the originally
  scheduled dates of moved and cancelled releases; and six release documents (empsit_11202025, empsit_12162025,
  empsit_02112026, cpi_10242025, cpi_12182025, cpi_02132026) for the embargo line of each moved release.
  schedule/news_release/empsit.htm came back empty from Wayback and was not used.

## How each entry is built and checked

- NFP and CPI: the row of the BLS annual schedule for the release year (date, time, release name and reference period),
  quoted from the saved .txt, e.g. "Friday, May 03, 2019 08:30 AM Employment Situation for April 2019". Only the exact
  names "Employment Situation" and "Consumer Price Index" are taken (not "Employment Situation of Veterans" and the like).
  Every schedule row agreed with the BLS release archive: the archive link file name carries the actual release date
  (for example news.release/archives/empsit_11202025.htm), and all 170 links were found. The six moved releases also quote
  their own embargo line ("8:30 a.m. (ET) Thursday, November 20, 2025").
- FOMC: the statement press release header, e.g. "May 01, 2019 Federal Reserve issues FOMC statement For release at 2:00
  p.m. EDT". All 57 say 2:00 p.m.; EDT/EST agrees with the UTC offset on every entry. Cross-check: the statement link sits
  under a regularly scheduled meeting row of fomccalendars.htm or the historical page.
- D.1f reuse: all 153 D.1f entries are copied with "reused_from": "stage_d1f_release_sources.json", the D.1f url and
  quote kept as d1f_source_url and d1f_quote. Each D.1f quote was rechecked against a fresh copy of its page (10 distinct
  URLs, each fetched once). D.1f quotes are markdown renderings with "..." gaps, so the recheck strips link, bold and
  heading markup, splits on "...", and requires every segment in the fresh page text (statement file names are matched
  against the raw HTML). Result: 153 of 153 pass; the D.1f notes (exclusions) also pass. The entry's own "quote" is
  quoted fresh from the saved page as above.
- The D.1f dates and my fresh parse agree for every D.1f entry; the only difference in the D.1f window is the added
  FOMC-2020-01-29.

## Decisions

- FOMC convention kept from D.1f: regularly scheduled statements only, 14:00 ET. Excluded, with quotes in "exclusions":
  2019-10-04 unscheduled call; 2020-03-02 and 2020-03-15 unscheduled meetings; notation votes 2020-03-19, 2020-03-23,
  2020-03-31, 2020-08-27; and, new, the 2025-08-22 notation vote (Statement on Longer-Run Goals and Monetary Policy
  Strategy). The cancelled March 17-18, 2020 meeting is in "cancellations". The 2024-11-07 statement fell on a Thursday
  (a 6-7 November meeting) and is included as scheduled.
- 2025 federal shutdown (quoted from the BLS archives and releases): the October 2025 Employment Situation and October 2025
  CPI were "Not published because of 2025 lapse in federal government appropriations". They were scheduled for 2025-11-07
  and 2025-11-13 (2025-09-24 schedule snapshot) and are cancellations with no entry. Moved, and entered at the published
  date: September NFP 2025-10-03 to 2025-11-20; September CPI 2025-10-15 to 2025-10-24; November NFP 2025-12-05 to
  2025-12-16; November CPI 2025-12-10 to 2025-12-18.
- January 2026 data also moved: NFP 2026-02-06 to 2026-02-11 and CPI 2026-02-11 to 2026-02-13 (2026-01-22 schedule snapshot
  compared with the 2026-09-19 one and the releases' own embargo lines). The saved pages do not state the cause; the entries
  use the published dates.
- Same-date releases are kept as separate entries (no collision dropping, unlike the D.1f table): 2019-12-11 CPI and FOMC,
  2020-06-10 CPI and FOMC, and new 2024-06-12 CPI and FOMC. Listed under "same_date_releases".
- Holiday shifts inside the published schedules (for example NFP 2020-07-02, 2025-07-03) are the scheduled dates and are
  not counted as moves.

## Mechanical verification

data/vendor/release_pages/macro_scripts/verify.py re-reads the output JSON and checks each quote as a whitespace-normalised
substring of its saved_path, recomputes instant_utc from date + time_local + tz with zoneinfo, checks every cross-check,
cancellation, move and exclusion quote, and checks that BLS times are 08:30 and FOMC times 14:00. Result (in the JSON under
"verification"): 227/227 quotes, 227/227 instants, 234/234 cross-checks, 153/153 D.1f rechecks, 7/7 cancellation, 12/12
move and 8/8 exclusion quotes; 0 failures. The scripts that fetched, parsed and built the file are in the same folder
(fetch.py, parse_bls.py, parse_fed.py, recheck_d1f.py, build.py, finalize.py).

## Not done or open

- Nothing unverified. Wayback copies stand in for bls.gov, which blocks scripted access; the snapshot times are in each
  entry.
- For the lead: the D.1f omission of FOMC 2020-01-29 (above), and the cause of the February 2026 moves, which is not stated
  on any saved page.
