# Brief: ReleaseChecker-OpusMed (Stage E.4 Part 2, K5, Task 1b)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" and
"Web research budgets" paragraphs first. Times in your report: PDT (America/Vancouver).

## Objective (one)
Build and check the event dates K5's members time on: the LBMA gold AM (10:30 London) and PM (15:00
London) auction days and their start instants in America/Chicago, and the FOMC statement instants. You
extract and check; you draw no conclusion about any member or result.

## Inputs
- The rules: reports/stage_e0_catalog_K5.md lines 161-230 (C9: EC-LBMA, EC-UKBH, EC-FOMC; C10: the London
  to Chicago conversion with zoneinfo and the 5-hour weeks). Read those lines only.
- E.3's verified FOMC table: strategy/members/k2/_releases.py, FOMC_STATEMENT_DATES (line 141 on), built from
  reports/stage_e2b_release_calendar.json FOMC rows (instant 13:00 CT).
- Saved pages from earlier stages, reuse first: data/vendor/release_pages/ (grep; do not read whole).

## What to check
1. EC-UKBH: England-and-Wales bank holidays 2019-05-01..2026-06-19 from https://www.gov.uk/bank-holidays.json
   (save the file; it lists years ahead) and, for years the live file no longer lists, a Wayback capture of it.
2. EC-LBMA, the scheduled auction days: every weekday 2019-05-01..2026-06-19 that is not an England-and-Wales
   bank holiday is a scheduled gold AM and PM auction day, EXCEPT any day on which IBA (ICE Benchmark
   Administration) or LBMA announced IN ADVANCE that an auction would not be held (for example UK half days such
   as 24 and 31 December, when the PM auction is usually not held, or special closures such as a state funeral).
   Find IBA's or LBMA's notices or schedule pages (and Wayback captures) for each year, and record for each
   such day which auction(s) were not held, the source URL, and the date of the notice (it must predate the
   day). Research window 2025-04-01..2026-06-19 first; then 2019-05..2025-03. Label any year you cannot source.
3. The start instants: for every scheduled day, T_AM = 10:30 and T_PM = 15:00 London converted to America/Chicago
   with Python zoneinfo (C10). List the weekdays in 5-hour weeks for each year and confirm C10's table
   (lines 206-219). Report any published change to the 10:30 or 15:00 start times in 2019-2026 (with source).
4. EC-FOMC: confirm that the FOMC statement dates and 13:00 CT instants in reports/stage_e2b_release_calendar.json
   (rows with release FOMC) equal E.3's FOMC_STATEMENT_DATES exactly, and list the research-window ones (10
   expected: C lines 256-257). No web needed for this item.

## Output
- reports/stage_e4b_release_check.json:
  `{"window": ["2025-04-01","2026-06-19"], "uk_bank_holidays": [{"date","name","source"}],
    "no_auction_days": [{"date","am_held": bool,"pm_held": bool,"reason","notice_date","source_url"}],
    "auction_days": [{"date","am_ct":"HH:MM","pm_ct":"HH:MM","five_hour_week": bool}]  (2019-05-01..2026-06-19),
    "five_hour_weeks": {"<year>": {"spring": [..], "autumn": [..]}},
    "fomc": {"equal_to_k2_table": bool, "rows": [{"date","instant_ct"}], "differences": [..]},
    "sources": [{"url","fetched_pdt","saved_path","sha256"}], "log": [..], "unverified": [..]}`
- reports/stage_e4b_release_check.md: counts, the no-auction days with sources, the 5-hour weeks, the FOMC
  comparison, every source URL, and a log of failed fetches (with time).
- Save every fetched page under data/vendor/release_pages/e4b/ with its URL and sha256 in the JSON (and a
  manifest.jsonl recording the URL requested AND the URL actually served, which for Wayback is the capture's
  own timestamp: the K4 check mis-dated a capture that Wayback served from another day).

## Allowed tools and sources
curl (browser-like User-Agent), WebFetch, Firecrawl scrape, the Wayback CDX API. Read-only public pages only.
No data API, no login, no paid source. Write each page to disk first and grep it for the passages you need.
If any WebSearch returns an over-budget or cost notice, stop searching, log it with the time, and return;
never continue from memory. Do not spend more than about 40 minutes; return what you have, the rest labelled.

## Boundaries
Do not edit the release calendar, any frozen file, code, tests, strategy/, screening/, or data/ other than
data/vendor/release_pages/e4b/. No commits. You decide no member's event set; the lead does.

## Return
The two paths, a summary of at most 200 words (counts, no-auction days found, unverifiable items), and anything
unfinished.
