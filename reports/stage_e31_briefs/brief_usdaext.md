# Brief: UsdaExt-OpusHigh (worker-high, model opus) - extend the USDA release calendar backwards

Objective (one): extend reports/stage_e31_briefs/research/usda_releases.csv (2022-11-01..2024-02-29, written by
DataResearch-OpusHigh) backwards to 2019-06-01, with the same reports, the same columns
(date,time_et,report,source_url,evidence) and the same evidence grading, into a NEW file
reports/stage_e31_briefs/research/usda_releases_ext.csv covering 2019-06-01..2022-10-31.
Work from the latest month backwards (2022-10 first). The lead may tell you to stop at an earlier bound once the
pilot window is fixed; whatever you finish must be whole months, and the file header comment states the covered range.
Reports: WASDE (and Crop Production released with it), NASS Grain Stocks, NASS Crop Progress (Mondays 16:00 ET in
season; note holiday shifts), FAS Weekly Export Sales (Thursdays 08:30 ET; holiday shifts), NASS Fats & Oils. NOPA crush
in a separate block of rows marked report "NOPA" (not USDA). Read reports/stage_e31_briefs/research/data_facts.md
section b and the existing CSV first for the sources and grading DataResearch used, and reuse its saved pages.
Sources: usda.gov/oce WASDE archive, NASS calendar and report archives (Cornell USDA ESMIS mirror is acceptable),
FAS export sales archive. Fetching: WebFetch, then `scrapling extract get <url> <file>`, then `scrapling extract
fetch`; save every page used raw under reports/stage_e31_briefs/research/pages/usda_ext/ and read by grep. Firecrawl
has no credits. If a WebSearch returns an over-budget notice, stop searching, log it with the time and return. Use at
most 40 searches. Missing or uncertain dates are marked in the evidence column, never guessed silently.
Output: the CSV and reports/stage_e31_briefs/research/usda_ext_fetch_log.md (URL, UTC time, sha256, method, ok/failed).
Boundaries: research only; no Databento call, no API key, no market data; do not edit usda_releases.csv or any repo
file outside reports/stage_e31_briefs/research/. No commits.
Return: the paths, the covered range, row counts per report, a summary of at most 200 words, and anything unfinished.
