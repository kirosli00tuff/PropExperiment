# Brief: ReleaseChecker-OpusMed (Stage E.7 Task 1b), worker-medium on opus

Objective: obtain and check the one free external series a K1 member reads (Cboe's VXN daily
history) and every dated input the K1 members (MNQ, M2K, MYM) meet on the research window (trade
dates 2025-04-01..2026-06-19); record a verdict per item (keep / drop / unverifiable), each with a
source URL. No judgment on results; the lead rules on anything unclear.

Read first (by section, grep, never whole files): CLAUDE.md sections "Web research budgets",
"Page-fetch fallback", "Context hygiene"; reports/stage_e0_catalog_K1.md lines 144-157 (C9 VXN),
403-501 (K1-vxnband-01; the data lines 443-451 and 468-472); data/group_session.py lines 1-60.

Items:
A. VXN daily history (the catalog's C9 source; free, no key).
   A1. Fetch https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv raw (curl with a
       browser User-Agent; fallback per CLAUDE.md). Save it unmodified as
       data/vendor/index_history/vxn/VXN_History.csv. Write a NEW manifest
       data/vendor/index_history/vxn/manifest.jsonl (one JSON line per fetch attempt: file,
       url_requested, url_served, http status, fetched_pdt, fetched_utc, sha256, bytes, the
       Last-Modified header, note). Do NOT touch data/vendor/index_history/manifest.jsonl (an earlier
       stage's record).
   A2. Parse it (script output: counts only): header, date format, first and last date, row count,
       whether every CLOSE parses as a decimal and how many decimals it carries, any duplicate or
       non-increasing dates, any non-positive or blank value.
   A3. Coverage 2019-04-30..2026-06-19: list every weekday in that span with no VXN row, and classify
       each against (i) the NYSE / Cboe full-closure holidays (a source for the list: the NYSE
       holidays page or its Wayback captures; Cboe's holiday calendar if reachable), and (ii) the
       equity trade-date calendar data.group_session.load_group_calendar("equity") (is_trade_date,
       early_halt_ct). Expected: rows missing only on exchange holidays (Cboe closed) - and those
       holidays are equity-calendar trade dates with an early halt at CME. Report any missing row on a
       date the stock market was open (a true gap) separately, and any row on a date it was closed.
   A4. Point-in-time check: find 1-3 Wayback captures of the same CSV URL (CDX:
       http://web.archive.org/cdx/search/cdx?url=cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv),
       preferably one from 2025 and one from 2026 before 2026-06-19; save them under
       data/vendor/index_history/vxn/wayback/ (manifest lines as A1) and count, for the dates both
       files hold, how many CLOSE values differ (list any that do). If Wayback is down or has none,
       record that; try FRED VXNCLS (https://fred.stlouisfed.org/graph/fredgraph.csv?id=VXNCLS) as a
       second copy and compare the same way.
   A5. Publication time of the daily close: a Cboe statement (VXN index page, Cboe index
       dissemination / "daily index values" pages, the file's own Last-Modified, Wayback capture
       times of the CSV relative to the last row's date) giving when day D's close appears. The
       member uses the close of trade date d-1 from 08:30 CT on d; state whether every piece of
       evidence puts publication before 08:30 CT on the next trade date, with quotes.
   Verdict for A: keep (obtained free, gaps only on closure days, no revisions found),
   or the specific problem.
B. CPI instants in the research window that D9.12 applies to MNQ, M2K and MYM (rules/constraints.py
   lines 20-30; the engine takes every row with "cpi": true from the frozen release calendar
   reports/stage_e2b_release_calendar.json, key with the row list, release "CPI"). 14 rows, dates
   2025-04-10..2026-06-10, 08:30 ET each. For each: check the date and time against the saved BLS
   schedule page named in the row (data/vendor/release_pages/bls/schedule_2025_home.txt and
   schedule_2026_home.txt; grep) and, for 2025-10-24 and 2025-12-18 (the shutdown-delayed
   releases), against a BLS notice (bls.gov needs browser headers; fallback per CLAUDE.md). Also
   record whether BLS published a CPI in the window that the calendar lacks (the cancelled October
   2025 CPI: quote the BLS notice). Verdict per row.
C. The equity calendar dates the members meet in the window (read only; no new web fetch unless a
   citation is missing): from data.group_session.load_group_calendar("equity") and
   rules.sessions.flatten_time_ct(root, d) for MNQ, M2K and MYM, list every weekday
   2025-04-01..2026-06-19 that is not a trade date, has early_halt_ct set, has a late open, or whose
   flatten time is not 15:08; confirm the three roots agree; and quote the citation the calendar
   module data/calendars/equity.py records for each (SOURCES / SOURCES_2025_2026, grep). Verdict per
   date (keep = cited; unverifiable = no citation).
D. Any other dated input: confirm by grep of reports/stage_e0_catalog_K1.md lines 216-594 that no
   active K1 member (cp1, cp2, cp3, vxnband, vwap) reads a release instant or value; FOMC, NFP and
   ISM_SERVICES rows for the three roots are harness inputs (D8, D9.5a), verified in E.2b: count them
   in the research window from the release calendar and record the count only.

Outputs: reports/stage_e7_release_check.md (tables per item, verdicts, quotes) and
reports/stage_e7_release_check.json (machine-readable: per item rows with verdict, source URL,
quote, fetch time UTC, saved path and sha256; for A the file path, sha256, first/last date, row count,
the missing-weekday list with classification, the revision counts, and the publication-time
evidence). Save every page used as evidence raw under reports/stage_e7_briefs/pages/ and read it with
grep; only quoted lines enter your context. Never print the CSV; scripts print counts.

Tools: Read, Grep, Bash (python with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/99bb7678-38d8-413c-82c8-d103cf2d3163/scratchpad/;
`uv run python` for repo imports), WebFetch, WebSearch (sparingly). Page fallback when WebFetch
fails: `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`; Firecrawl
only if Scrapling fails. If a WebSearch returns a budget or cost notice, stop searching, write it with
the time into the .md, and return. It is informational: never continue from memory.

Boundaries: write only the two outputs, files under data/vendor/index_history/vxn/ and files under
reports/stage_e7_briefs/pages/. Do not touch strategy/, screening/, rules/, tests/, other data/
files or any other report. No bar reads (never open a parquet). No paid source, no key, no login. No
TopstepX reference. Do not spawn workers.

Return: the two paths, a summary of at most 200 words, and anything you could not finish.
