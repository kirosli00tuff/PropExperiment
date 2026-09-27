# Brief: ReleaseSourcer-Macro-OpusHigh (worker-high on opus) - sourced data

Objective: a verified list of every Employment Situation (Unemployment Rate / nonfarm payrolls), CPI and scheduled FOMC
statement release instant from 2019-05-01 through 2026-06-21.

Read reports/stage_e2b_briefs/00_common.md and reports/stage_e2b_briefs/g1_release_common.md (binding).
Reuse: reports/stage_d1f_release_sources.json and strategy/research/e_calendar_event/_release_table_2019_2024.py (read-only,
frozen by D.1f) already hold verified FOMC, CPI and NFP entries for 2019-05-01..2024-02-29 with URLs and verbatim quotes.
Copy those entries (mark "reused_from": "stage_d1f_release_sources.json") after re-checking each quote against a freshly
saved copy of its page, or its Wayback copy (re-fetch each distinct URL once, not each entry). Keep D.1f's conventions:
regularly scheduled FOMC statements only (2:00 pm ET; unscheduled meetings, notation votes and cancelled meetings have no
entry; list the exclusions in the log); BLS releases at 8:30 am ET. Then source 2024-03-01..2026-06-21 new (BLS schedule
pages per year and month views, BLS release archives; the Federal Reserve's FOMC calendars page). Watch for the 2025
federal government shutdown (BLS releases delayed or cancelled in October-November 2025): use the dates actually published.
Output: reports/stage_e2b_release_sources_macro.json ({"coverage": {"first": "2019-05-01", "last": "2026-06-21"},
"entries": [...], "cancellations": [...], "exclusions": [...], "coverage_table": {...}, "verification": {...}}), and a log
reports/stage_e2b_release_sources_macro_log.md (queries, pages saved, decisions, stopping-rule table).
Reply with the paths, a summary of at most 200 words, counts per release and year, and anything unverified.
