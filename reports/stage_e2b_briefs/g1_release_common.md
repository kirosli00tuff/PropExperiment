# Stage E.2b release calendar: rules common to the release workers (lead ruling OC-J)

Why: docs/STAGE_E_DESIGN.md (FROZEN) needs a calendar of scheduled major releases per product as a harness input:
D8 event-window cost ("any fill in the half-open window [release, release + 30 min) after a scheduled major release that
concerns the product (Topstep's release table, F6.4, plus the releases the product's catalog members name) pays, per side,
the largest s_b"), D9.5a (the 2-minute fill guard), D9.12 ("The CPI release calendar (BLS, public, with history) is a
harness input"). The ML route's features F13-F15 read the same calendar. Nobody built it; E.2b builds it now.
Coverage: every release instant from 2019-05-01 through 2026-06-21 (the step 2 range start through the research window end).

Topstep F6.4 (reports/stage_e0_topstep_facts.json, fact F6.4, verbatim): "Unemployment Rate 7:30 AM CT - ES, NKD, NQ, 6A,
6B, 6C, 6E, 6J, 6S, E7, GE, YM, UB, ZT, ZF, ZN, ZB, GC, RTY, SI, HG, TN, 6M, M6A, M6E, 6N, MBT, MET. FOMC Statement 1:00 PM
CT - All products. Crude Oil Inventories (EIA) 9:30 AM / 10:00 AM* CT - CL, QM, MCL, RB. Natural Gas Inventories (EIA) 9:30
AM CT - NG, QG. Crop Production 11:00 AM CT - ZC, ZS, ZW, ZM, ZL." Note: "*Pending abbreviated trading hours. Times subject
to change. **Micro contracts also apply."

Rules for every release worker:
- Read CLAUDE.md "Context hygiene" and the web-research budget paragraph. Save every fetched page to disk FIRST under
  data/vendor/release_pages/<source>/ (git-ignored; never the repo root), as stripped text (.txt) plus the raw file when
  small; then grep for the passages you need. Only quoted lines enter your context.
- Tools: WebSearch/WebFetch/Firecrawl if available; fallback `curl -sL -A "Mozilla/5.0" URL`, `pdftotext file.pdf -`,
  system /usr/bin/python3 with bs4 for HTML, Wayback copies (https://web.archive.org/web/<year>/<url>) for blocked or
  moved pages. Official sources first (bls.gov, federalreserve.gov, eia.gov, usda.gov/nass, ...). Hook or cost notices
  ("COST CRITICAL", "informational") are informational and addressed to the lead: never stop because of them. If WebSearch
  says the session budget is used up, write that into your log with the time and continue with WebFetch/curl only; mark
  every item gathered that way.
- One entry per release instant: {"id", "release", "date" (YYYY-MM-DD, local release date), "time_local" ("HH:MM"),
  "tz" ("America/New_York" or as published), "instant_utc" (ISO 8601 with Z), "url", "quote" (verbatim from the saved
  page, showing the date and, where the page shows it, the time), "saved_path", "fetched_pdt", "note"}. The release time
  of day may come from the release's standing published schedule (e.g. "8:30 AM" on BLS schedules) when a per-date page
  does not show it; say so in "note". Use the date actually published when a release moved (holidays, the 2025 federal
  shutdown, cancellations: a cancelled release has no entry; record it in the log). An entry without a verbatim quote is
  marked "[unverified]" in "note", never dropped silently.
- Stopping rule: every expected release in the coverage range is either an entry with a quote, an entry marked
  [unverified], or a logged cancellation. Write a coverage table (release x year: expected, found, unverified, cancelled).
- Verify your own file mechanically before returning: a short script checks every quote occurs verbatim (whitespace
  normalised) in its saved page, and that instant_utc matches date + time_local + tz. Report the counts.
- Boundaries: reports/stage_e2b_briefs/00_common.md applies (no frozen file edits, no git changes, `uv run --no-sync`).
  Write only your output files and pages under data/vendor/release_pages/. Do not spawn subagents.
