# Brief: ReleaseChecker-OpusMed (Stage E.4 Part 3, K3, Task 1b)

Repository: /home/kiros-li/Documents/GitHub/PropExperiment. Read CLAUDE.md's "Context hygiene" and "Web research
budgets" paragraphs first. Times in your report: PDT (America/Vancouver).

## Objective (one)
Build and check the clocks, calendars and free index histories K3's members time on, for 2019-04-01..2026-06-19
(research window 2025-04-01..2026-06-19 first). You extract and check; you draw no conclusion about any member or result.

## Inputs
- The rules: reports/stage_e0_catalog_K3.md lines 140-201 (C9: T_L, T_E, T_T, EC-EW, EC-JP, EC-TGT, ME(m), with the
  known-answer tests at lines 177-181) and the K3-mehedge-01 entry's index lines (grep "obtainable proxy", "E.2 rule",
  "Formula" and "Timing" inside the section starting at the line `### K3-mehedge-01`). Read those lines only.
- The FX calendar: data.group_session.load_group_calendar("fx") (EC-CAL: trade dates, early halts).
- Pages saved by earlier stages (reuse first): data/vendor/release_pages/ (for example e4b/ holds gov.uk's
  bank-holidays.json).

## What to build and check
1. T_L(d): 16:00 Europe/London on each weekday d, in America/Chicago (zoneinfo). Run C9's known-answer tests. List the
   11:00 CT weekdays per year and compare with C9's list (lines 148-152).
2. T_E(d): 14:15 Europe/Berlin in America/Chicago (zoneinfo); known-answer tests; the 08:15 CT weekdays.
3. T_T(d): 09:55 Asia/Tokyo on Tokyo date d, in America/Chicago (it falls on the CT evening of d-1); known-answer test.
4. EC-EW: England-and-Wales bank holidays 2019-04..2026-06 (gov.uk bank-holidays.json).
5. EC-TGT: TARGET closing days 2019-2026 from the ECB's working-hours page (live, and Wayback captures for 2019-2025
   dated before each year), with the source per year; log any difference between years.
6. EC-JP: Japanese national holidays 2019-2026 from the Cabinet Office CSV (syukujitsu.csv; saved raw with URL and
   sha256); the Tokyo business days (weekdays that are not national holidays and not 31 December, 1-3 January); the
   gotobi dates (Tokyo business days whose day of month is 5, 10, 15, 20, 25 or 30, no shift) and the last Tokyo business
   day of each month. Check the year-end closure rule (31 Dec - 3 Jan) against any free record of which dates carried a
   Tokyo fix (for example MUFG's published TTM history, or a news or bank notice); if none is found, say so.
7. ME(m): the last EC-CAL FX trade date of each calendar month 2019-04..2026-06, and which of them are EC-EW bank holidays
   (C9 drops those; expect 2020-08-31 and 2021-05-31 and none in the research window).
8. The index histories for K3-mehedge-01 (free only; no purchase, no paid source, no login, no data API with a key):
   the EURO STOXX 50 price index daily official closes from STOXX Ltd.'s free history file (h_3msx5e.txt or its current
   equivalent on stoxx.com, or a Wayback capture of it), and the Nikkei 225 daily closes from Nikkei Inc.
   (indexes.nikkei.co.jp) or FRED's public download of series NIKKEI225 (https://fred.stlouisfed.org/graph/fredgraph.csv?id=NIKKEI225,
   a public file, not the key-based API). Cover 2019-04-01..2026-06-19. Save each raw file under
   data/vendor/index_history/ with its URL, fetch time and sha256, parse to (date, close), and check for gaps against the
   exchange's trading days (list every missing date and every non-trading date with a value). If an index cannot be
   obtained free, say so with every attempt logged: that exposure's mehedge trial is then dropped (the entry's rule).

## Output
- reports/stage_e4c_release_check.json with keys: "t_l" (per-year 11:00 weekdays, known-answer results), "t_e" (same),
  "t_t" (known-answer results), "ec_ew" [{date,name}], "ec_tgt" [{date,name,source_url,capture}], "ec_jp_holidays"
  [{date,name}], "tokyo_business_days_count" per year, "gotobi" [date], "tokyo_month_end" [date], "month_ends"
  [{month, me_date, ew_holiday: bool}], "index": {"SX5E": {obtained: bool, source_url, saved_path, sha256, first, last,
  n, missing_dates:[..], extra_dates:[..]}, "N225": {...}}, "sources": [...], "log": [...], "unverified": [...].
- reports/stage_e4c_release_check.md: counts, every known-answer result, the TARGET days, the Tokyo year-end finding,
  the month-end drops, the index findings, every source URL, and a log of failed fetches (with time).
- Save every fetched page under data/vendor/release_pages/e4c/ with a manifest.jsonl recording the URL requested, the URL
  actually served (for Wayback, the capture's own timestamp) and the sha256.

## Allowed tools and sources
curl (browser-like User-Agent), WebFetch, Firecrawl scrape, the Wayback CDX API, Python with zoneinfo. Read-only public
pages and public download files only. Write each file to disk first and grep it. If any WebSearch returns an over-budget or
cost notice, stop searching, log it with the time, and return; never continue from memory. Time box about 45 minutes; the
research-window items and the index histories first; return what you have with the rest labelled.

## Boundaries
Do not edit the release calendar, any frozen file, code, tests, strategy/, screening/, or data/ other than
data/vendor/release_pages/e4c/ and data/vendor/index_history/. No commits. You decide no member's event set; the lead does.

## Return
The two paths, a summary of at most 200 words (counts, known-answer results, the index outcome for each index, anything
unverifiable), and anything unfinished.
