# Brief: CalendarBuilder-OpusHigh (worker-high, opus). Stage E.12 Task 2c

You are a worker in Stage E.12 (prompt docs/prompts/STAGE_E.12.md, Task 2c). Read CLAUDE.md's
"Web research budgets", "Page-fetch fallback" and "Context hygiene" paragraphs and follow them.

## Objective
Build the EC-K9 announcement date set (calendar C9 of reports/stage_e10_catalog_K9.md) for the
v2 training window 2019-05-01..2024-02-29, from the official pages EC-K9 names, with one source
row per date, so K9-anncday-01 can enter ML route v2 as a feature (V23 item 8).

## Inputs (read by section, never whole)
- reports/stage_e10_catalog_K9.md: C9 definition (around lines 117-143), K9-anncday-01 (lines
  195-300: its condition and decision_time), section 8 "Verification table" (line 591 on: the CAL-*
  source rows the research-window dates came from; reuse the same publishers and page families).
- reports/stage_e10_catalog_K9.json members[0].event_dates: the frozen research-window rows
  (2025-04..2026-06), the format to copy.
- reports/stage_e2b_release_calendar.json: the frozen release calendar (FOMC, NFP, CPI, PPI rows
  from 2019-05). A cross-check source only: every date you take must come from an official page
  you fetched; agreement with this file is evidence, disagreement is a finding to report.

## The rule
Exactly C9's text: the union of FOMC statement days, NFP (Employment Situation) release days, GDP
first and last estimates (BEA advance and third), ISM manufacturing (scheduled release days), and
per reference month the earlier of the CPI and PPI release days. Dates known in advance only
(K9-anncday-01's decision_time: known before the 17:59 CT entry intent on the evening before d).
Where C9's text leaves a case open (for example an unscheduled FOMC action such as March 2020's,
or a rescheduled release), do not decide it: list the case with its evidence under "questions"
and keep it out of date_set until the lead rules.

## Method
Official publishers only (Federal Reserve Board, BLS, BEA, ISM) and Wayback captures of their
pages. Fetch order per CLAUDE.md (WebFetch, scrapling get, scrapling fetch; bls.gov needs browser
headers: scrapling usually works there). Save every page used raw under
reports/stage_e12_briefs/calendar_pages/, grep it, log URL, UTC fetch time and sha256. A year or a
component that no official source covers is logged as an uncovered span (dates), never guessed.
A WebSearch over-budget notice: stop searching, log it with the time, return what you have.

## Cross-check (required)
Apply your method to the research window 2025-04-01..2026-06-19 for at least one component per
publisher (all five if cheap) and compare with the frozen event_dates: report every difference.
Compare FOMC, NFP, CPI and PPI over 2019-05..2024-02 with reports/stage_e2b_release_calendar.json.

## Output
1. reports/stage_e12_ec_k9_2019_2024.json (this schema exactly; the V23Coder's code reads it):
   {"schema": "ec_k9/1", "window": ["2019-05-01", "2024-02-29"], "rule": "<C9's text, quoted>",
    "event_dates": {"FOMC": [...], "NFP": [...], "GDP_first_last": [...],
    "ISM_manufacturing_scheduled": [...], "inflation_earlier_of_CPI_PPI_by_reference_month": [...]},
    "date_set": [sorted union of the five lists, "YYYY-MM-DD"],
    "uncovered_spans": [["YYYY-MM-DD", "YYYY-MM-DD", "component", "reason"], ...],
    "questions": [...], "sources": [{"id": "CAL-E12-001", "publisher": ..., "url": ..., "fetched_utc":
    ..., "sha256": ..., "page_file": ..., "dates": [...], "quote": "verbatim line(s)"}],
    "cross_check": {...}}
   Every date in every list cites at least one CAL-E12 row whose quote shows it.
2. reports/stage_e12_ec_k9_2019_2024.md: the CAL-E12 rows as a table, per-year counts per
   component, the cross-check results, uncovered spans and questions.
3. reports/stage_e12_briefs/calendarbuilder_log.md: every fetch (time, URL, route, result, sha256).

## Boundaries
Read-only web fetches of the four publishers' pages and their Wayback captures. No market data, no
Databento, no TopstepX/ProjectX, no key, no code edits, no commits. Released values (the CPI print
etc.) are never recorded, only dates.

## Return (at most 200 words)
The output paths, the date counts per component and in total, uncovered spans, cross-check
differences, the open questions, and anything you could not finish.
