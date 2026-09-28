# Brief: ReleaseChecker-OpusMed (Stage E.5 Task C3, NGS confirmation-window check)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" and "Web research
budgets" paragraphs first. Times in your report: PDT (America/Vancouver). You are a worker: you do not spawn workers.

## Objective (one)
For every EIA Weekly Natural Gas Storage Report (NGS) release K4-ngpre-01 trades in its confirmation window, check the
release date and time against EIA's record of actual publication and the schedule captures, and give C9's verdict per
release. You extract and check; you draw no conclusion about any member or result.

## The window
NG's confirmation window is S_NG..2024-02-29. S_NG is not computed yet (it is at least 2019-05-06, D4's earliest), so
check every NGS row dated 2019-05-06..2024-02-29; the lead filters to S_NG afterwards.

## Inputs
- The rules: reports/stage_e0_catalog_K4.md lines 135-170 (C9: EC-NGS and the availability and drop rules). Read those
  lines only.
- The rows under check: K4-ngpre-01's frozen table, strategy/members/k4/_releases.py, tuple `NGS` (line 242 on:
  (date, T_N "HH:MM" CT) per row), for dates 2019-05-06..2024-02-29. Read it with a short script; print counts, not rows.
  Its source is the frozen release calendar reports/stage_e2b_release_calendar.json, key `releases`, rows with
  `release == "NGS"` (fields id, date, time_local, tz, instant_utc, evidence, source{url, saved_path}, note); many
  2019-2024 rows are [unverified] there (taken from EIA's standing Thursday rule). Never print either file whole.
- How E.4 did the research window (reuse its method and its saved pages first): reports/stage_e4_briefs/1b_release_checker.md,
  reports/stage_e4_release_check.md (grep the "Sources" and "Log" sections), reports/stage_e4_release_check.json key
  `ngs` (row shape), saved pages under data/vendor/release_pages/e4/ and data/vendor/release_pages/eia/.

## What to check, per NGS row in the window
1. The schedule entry: the standard slot ("10:30 a.m. eastern time on Thursdays") or that year's exception table on
   https://ir.eia.gov/ngs/schedule.html, from the LAST Wayback capture before the release (the catalog's yearly
   captures 20190111124957, 20200128214849, 20210104203613, 20220114160745, 20230210074654, 20240607000738, plus any
   others the CDX API lists: http://web.archive.org/cdx/search/cdx?url=ir.eia.gov/ngs/schedule.html&from=2019&to=2024).
   Flag any entry marked "(Updated)"; for each give the EARLIEST capture that shows it and the latest capture before it
   that does not.
2. The actual publication: a Wayback capture of https://ir.eia.gov/ngs/ngs.html taken after the release and before the
   next one ("Released: <date> at 10:30 a.m. ... Next Release: ..."), or another EIA record that states the date (and
   time, where stated): EIA's WNGSR history file, the Natural Gas Weekly Update, archive pages. Use the `id_` Wayback
   form (http://web.archive.org/web/<ts>id_/<url>) and check the served capture's own timestamp (E.4's R-T3-1 lesson: a
   request can be served from a different capture; record the effective timestamp).

## C9's verdict per row
- `keep`: the actual date and time equal the schedule entry, and no "(Updated)" marker.
- `drop_actual_differs`: the actual date or time differs from the schedule entry (give both).
- `updated`: the schedule entry carries "(Updated)"; give the earliest capture showing it (the lead applies the member's
  entry time, T - 90 minutes).
- `unverifiable`: no record of actual publication obtained; say what you tried. Keep the calendar's value.
A record with a date but no clock time is "date verified, time from the schedule" (time_basis "schedule"); do not guess.

## Output
- reports/stage_e5_ngs_check.json: `{"window": ["2019-05-06","2024-02-29"], "ngs": [row], "updated_markers": [...],
  "schedule_captures_used": [...], "sources": [{"url","effective_capture","fetched_pdt","saved_path","sha256"}],
  "log": [...]}` with row = `{"id","date","time_ct_table","time_et","calendar_evidence","schedule_entry",
  "schedule_source","actual_date","actual_time_et","time_basis","actual_source","updated_marker",
  "earliest_capture_showing_update","verdict","reason"}` (E.4's `ngs` row shape plus the table's CT time).
- reports/stage_e5_ngs_check.md: counts per verdict (also per year), every non-keep row in a table, every source URL, and
  a log of every failed fetch with its time.
- Save every fetched page under data/vendor/release_pages/e5/ (git-ignored) with its URL and sha256 in the JSON.

## Allowed tools and sources
curl (browser-like User-Agent), WebFetch, Firecrawl scrape, the Wayback CDX API. Read-only public EIA pages and Wayback
captures only. No data API (not the EIA API), no login, no paid source. Write each page to disk first and grep it for
the passages you need; only quoted lines enter your context. Wayback can be slow or down: pace requests (about one per
second), retry a failed capture once after a pause, record failures, and label what stays unverifiable. If any
WebSearch returns an over-budget or cost notice, stop searching, write the notice and the time into your log, and
return; never continue from memory. Budget about 90 minutes; return what you have with the rest labelled.

## Boundaries
No edit to the release calendar, strategy/, screening/, rules/, data/ (other than data/vendor/release_pages/e5/),
tests/, docs/ or any other report. No commits. You decide no member's event set and no table change; the lead does.

## Return
The two report paths, a summary of at most 200 words (counts per verdict and per year, the unverifiable count and why),
and anything unfinished.
