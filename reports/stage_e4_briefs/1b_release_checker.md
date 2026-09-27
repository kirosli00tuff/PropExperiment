# Brief: ReleaseChecker-OpusMed (Stage E.4 Part 1, Task 1b)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" and
"Web research budgets" paragraphs first. Times in your report: PDT (America/Vancouver).

## Objective (one)
For the research window (trade dates 2025-04-01..2026-06-19), check the event dates K4's members time
on against the publishers' own records, and apply the catalog's C9 drop rules. You extract and check;
you draw no conclusion about any member or result.

## Inputs
- The rules: reports/stage_e0_catalog_K4.md lines 135-191 (C9: EC-WPSR, EC-NGS, the availability and
  drop rules, EC-API, EC-CAL, EC-NYSE). Read those lines only.
- The calendar under check: reports/stage_e2b_release_calendar.json, key `releases`, rows with
  `release` in {WPSR, NGS, API_WSB} and `date` in the window (64, 64 and 64 rows). Read it with a
  short script; never print the whole file. Fields: id, date, time_local, tz, instant_utc, evidence,
  source{url, saved_path}, note.
- Pages E.2b already saved (git-ignored, reuse them first): data/vendor/release_pages/eia/ (WPSR issue
  pages, the NGS schedule page, Wayback CDX listings), data/vendor/release_pages/api/. How they were
  sourced: reports/stage_e2b_release_sources_commodity_log.md and ..._named_log.md (grep, do not read
  whole).

## What to check
1. WPSR (EC-WPSR), every in-window row: the calendar's date and ET time against (i) the schedule entry
   (standard "10:30 a.m. eastern time on Wednesdays", or that year's exception table on
   https://www.eia.gov/petroleum/supply/weekly/schedule.php and its Wayback captures) and (ii) EIA's
   record of actual publication (https://www.eia.gov/petroleum/supply/weekly/archive/ and the issue
   pages). Flag any entry marked "(Updated)" in any schedule capture, and for each give the timestamp
   of the EARLIEST capture that shows the updated entry (and the latest capture before it that does
   not), so the lead can apply "no capture dated before the member's entry time shows the update".
2. NGS (EC-NGS), every in-window row (59 are [unverified] in the calendar, taken from EIA's standing
   rule): the same two checks against https://ir.eia.gov/ngs/schedule.html (and captures) and a record
   of actual publication: for example Wayback captures of https://ir.eia.gov/ngs/ngs.html ("Released:
   <date> at 10:30 a.m. ... Next Release: ..."), the WNGSR history file ngshistory.xls, EIA's Natural
   Gas Weekly Update, or other EIA pages. Same "(Updated)" capture test.
3. API (EC-API): for every in-window WPSR that is in its standard Wednesday 10:30 ET slot, the Tuesday
   before it and the Monday before that: is that Monday a US federal holiday (OPM's federal holiday
   list; give the source URL)? Also report whether the calendar's API_WSB row for that week exists
   and its date/time.
4. NYSE (EC-NYSE, used by K4-eiamom-01): every NYSE full closure and early close (with the close
   time) from 2025-04-01 to 2026-06-19, from nyse.com's holidays and trading hours page (or its Wayback
   captures), with the source URL.

## C9's verdict per WPSR or NGS row
- `keep`: the actual publication date and time equal the schedule entry, and no "(Updated)" marker.
- `drop_actual_differs`: the actual date or time differs from the schedule entry (give both).
- `updated`: the schedule entry carries "(Updated)"; give the earliest capture showing it. (The lead
  applies each member's entry time.)
- `unverifiable`: no record of actual publication could be obtained; give the reason and what you
  tried. Keep the calendar's value.
A time that EIA's record does not state (a page with a date but no clock time) is "date verified, time
from the schedule": say so per row in a field, do not guess.

## Output
- reports/stage_e4_release_check.json:
  `{"window": ["2025-04-01","2026-06-19"], "wpsr": [row], "ngs": [row], "api_weeks": [week],
    "nyse": {"full_closures": [{"date","name","source_url"}], "early_closes": [{"date","close_time_et","source_url"}]},
    "sources": [{"url","fetched_pdt","saved_path","sha256"}], "log": [..] }`
  where row = `{"id","date","time_et","calendar_evidence","schedule_entry","schedule_source",
  "actual_date","actual_time_et","time_basis" ("stated"|"schedule"), "actual_source","updated_marker",
  "earliest_capture_showing_update","verdict","reason"}` and week = `{"wpsr_date","tuesday","monday",
  "monday_federal_holiday","holiday_name","api_row_date","api_row_time_et","source_url"}`.
- reports/stage_e4_release_check.md: counts per verdict, every non-keep row in a table, the NYSE list,
  the API weeks with a holiday Monday, every source URL, and a log of every fetch attempt that failed
  (with time).
- Save every fetched page under data/vendor/release_pages/e4/ with its URL and sha256 in the JSON.

## Allowed tools and sources
curl (browser-like User-Agent), WebFetch, Firecrawl scrape, the Wayback CDX API
(http://web.archive.org/cdx/search/cdx?url=...). Read-only public schedule and archive pages only. No
data API (not the EIA API), no login, no paid source. Write each page to disk first and grep it for the
passages you need; only quoted lines enter your context. If any WebSearch returns an over-budget or
cost notice, stop searching, write the notice and the time into your log, and return; never continue
from memory. Wayback can be down for hours: if it fails, record it, try the other sources, and label
what stays unverifiable. Do not spend more than about 45 minutes; return what you have with the rest
labelled.

## Boundaries
Do not edit the release calendar or any frozen file, code, tests, strategy/, screening/, data/ other
than data/vendor/release_pages/e4/. No commits. You decide no member's event set; the lead does.

## Return
The two paths, a summary of at most 200 words (counts per verdict, unverifiable counts and why), and
anything unfinished.
