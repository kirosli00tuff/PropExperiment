# Brief: ReleaseSourcer-Commodity-OpusHigh (worker-high on opus) - sourced data

Objective: a verified list of every release instant, 2019-05-01 through 2026-06-21, of (1) EIA's Weekly Petroleum Status
Report (Topstep's "Crude Oil Inventories (EIA) 9:30 AM / 10:00 AM* CT"), (2) EIA's Weekly Natural Gas Storage Report
("Natural Gas Inventories (EIA) 9:30 AM CT"), (3) USDA NASS Crop Production ("Crop Production 11:00 AM CT"; include the
annual Crop Production summary if NASS titles it Crop Production, noting it).

Read reports/stage_e2b_briefs/00_common.md and reports/stage_e2b_briefs/g1_release_common.md (binding).
Sources: EIA's release schedules and holiday release schedules (eia.gov/petroleum/supply/weekly/, the WPSR archive with
each issue's release date, eia.gov/naturalgas/storage/ and its release schedule and archive), USDA NASS release calendars
per year and the Crop Production report archive (usda.library.cornell.edu / nass.usda.gov). Normal times: WPSR Wednesday
10:30 ET, gas storage Thursday 10:30 ET, Crop Production 12:00 ET; holiday weeks and the 2025 federal shutdown moved or
cancelled releases: use the dates and times actually published (an archive listing the issue's release date and time
beats a rule; a rule-derived date with no per-date source is "[unverified]"). Weekly series are long (about 370 each):
prefer year schedule pages plus archive listings that show many dates per page over one fetch per week.
Output: reports/stage_e2b_release_sources_commodity.json (same shape as the macro file: coverage, entries, cancellations,
coverage_table, verification) and a log reports/stage_e2b_release_sources_commodity_log.md.
Reply with the paths, a summary of at most 200 words, counts per release and year, and anything unverified.
