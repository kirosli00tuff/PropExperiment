# Brief: ReleaseChecker-OpusMed (Stage E.8 Task 1b), worker-medium on opus

Objective: check every dated input the seven K6 members (cluster K6: ZC, ZW, ZS, ZM, ZL, HE, LE)
meet on the research window (trade dates 2025-04-01..2026-06-19), and record a verdict per item
(keep / drop / unverifiable), each with a source URL. No K6 member reads a free external price
series (settlements come from the bars through the harness's proxy), so nothing is fetched into
data/vendor/. No judgment on results; the lead rules on anything unclear.

Read first (by section, grep, never whole files): CLAUDE.md sections "Web research budgets",
"Page-fetch fallback", "Context hygiene"; reports/stage_e0_catalog_K6.md lines 136-162 (C9a
EC-USDA, the drop rule), 163-200 (C10 EC-LIM), 496-595 (K6-limitcont-01), 596-744 (the two WASDE
members); rules/price_limits.py lines 1-63 and the 'HE' and 'LE' rows of LIMITS (grep "'HE': (").

Items:
A. WASDE releases (EC-WASDE; K6-wasdepre-01 and K6-wasdepost-01 read the date only, with T = 11:00
   CT = 12:00 ET). The frozen release calendar reports/stage_e2b_release_calendar.json (key
   "releases", rows with "release" == "WASDE") has 14 rows dated 2025-04-10..2026-06-11. Do not edit
   it. For each row, and for every WASDE USDA published or scheduled in 2025-04..2026-06:
   A1. The year's published schedule: USDA OCE's WASDE page ("2025 WASDE Release Dates (12:00pm ET)"
       and the 2026 list; https://www.usda.gov/oce/commodity/wasde and its Wayback captures, the
       2025 list captured before 2025-04-01 and the 2026 list before 2026-01-01). Quote the line
       for each date.
   A2. The record of publication: ESMIS
       (https://esmis.nal.usda.gov/publication/world-agricultural-supply-and-demand-estimates and
       the saved pages data/vendor/release_pages/usda/esmis_view/wasde_<date>.txt; grep). Record the
       ESMIS date and, where the page gives one, the release time.
   A3. The drop rule (catalog C9a, lines 154-156): an event whose actual ESMIS date differs from the
       year's published schedule is kept only if a USDA notice of the new date, dated BEFORE the new
       date, is found; otherwise it is dropped. Apply it to every row. Known cases to settle with
       quotes: the October 2025 WASDE (cancelled in the 2025 lapse in appropriations; confirm it was
       not published, and that the calendar has no October 2025 row), and the November 2025 WASDE
       (calendar row 2025-11-14; find the originally scheduled date and the USDA notice of the new
       date with its own date; saved candidates: data/vendor/release_pages/usda/fas_reschedule_notice.txt,
       nass_notice_2025-10-31.txt, nass_notice_2025-11-19.txt).
   A4. Time: every kept row at 12:00 ET (11:00 CT). A row at any other time: verdict drop (the lead
       does not re-time events).
   A5. Any WASDE published in the window that the calendar lacks: list it (the members read the
       frozen calendar only; the lead rules).
B. The price limits K6-limitcont-01 reads (HE and LE only). The member reads the INITIAL daily
   limit of the frozen table rules/price_limits.py LIMITS (the harness's EC-LIM; it encodes no
   expanded limit, flag R-L2) on every livestock trade date of the window.
   B1. List the HE and LE periods that intersect 2025-03-25..2026-06-19 (amount in USD per pound,
       status sourced / bracketed / carried, the sources named). Write one row per livestock trade
       date of the window with the amount in force (a script; print counts only, the rows go in
       the .json).
   B2. Check each period's amount and its start date against CME's own publications: the saved
       captures and notices the E.2a JSON names (reports/stage_e2a_price_limits.json, keys
       "captures_parsed" and "sources"; grep for the capture ids in the periods), and CME's
       livestock price-limit reset notices for the September 2025 Lean Hog reset and the June 2025
       and June 2026 Live Cattle resets (CME Group "price limits" page, cmegroup.com notices or
       Special Executive Reports; cmegroup.com blocks automated fetches, so try Wayback captures
       and the page-fetch fallback). Settle the two bracketed periods in the window
       (HE 2025-08-30..2025-09-01 at 0.0400; LE 2026-05-19..2026-06-19 at 0.0725): what was the limit
       on each trade date, by CME's own text. Verdict per period: keep (the table equals CME's
       text), drop (it differs: give both values), unverifiable.
   B3. For the record only (the member does not read it): CME's rule text for the livestock
       EXPANDED limit in the window (the amounts for HE and LE and what triggers an expansion: one
       contract month settling at the limit, or any month, or the first two), quoted from the CME
       rulebook chapters (Live Cattle chapter 101, Lean Hogs chapter 152) or a CME notice; and the
       dates in the window on which a capture shows an expanded limit (the E.2a JSON
       captures_parsed rows with expanded_bold true for HE or LE; list them).
C. EC-CAL dates the members meet (read only; no web fetch unless a citation is missing): from
   data.group_session.load_group_calendar("grains") and ("livestock"), rules.sessions
   (flatten_time_ct or the module's equivalent for each root), list every weekday
   2025-04-01..2026-06-19 that is not a trade date, has early_halt_ct set, has a late open
   (scheduled_late_opens; grains: no evening session), or whose flatten time is not 13:18 (grains)
   or 13:03 (livestock). Confirm the five grain roots agree with each other and HE and LE agree.
   Quote the citation data/calendars/grains.py and livestock.py record for each date (grep).
   Verdict per date (keep = cited; unverifiable = no citation).
D. Any other dated input. Confirm by grep of reports/stage_e0_catalog_K6.md lines 233-744 that no
   active K6 member (cp1, cp2, cp3, crushgap, limitcont, wasdepre, wasdepost) reads a release other
   than WASDE, or any release value. Count, from the frozen release calendar, the research-window
   rows whose products include a K6 root, per release name (WASDE, CROP, CROP_ANNUAL,
   CROP_PROGRESS, FOMC, any other) - these are harness inputs (D8 event cost, D9.5a guard), counted
   only. List the dates that are both a WASDE date and an FOMC date.

Outputs: reports/stage_e8_release_check.md (tables per item, verdicts, quotes) and
reports/stage_e8_release_check.json (machine-readable: per item rows with verdict, source URL,
quote, fetch time UTC, saved path and sha256; B1's per-date limit rows). Save every page used as
evidence raw under reports/stage_e8_briefs/pages/ (URL, UTC fetch time and sha256 in the .json)
and read it with grep; only quoted lines enter your context. Scripts print counts and summaries,
never whole tables.

Tools: Read, Grep, Bash (python with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/94d6572b-fdf2-4814-9116-60c2521d80a0/scratchpad/1b/;
`uv run python` for repo imports), WebFetch, WebSearch (sparingly). Page fallback when WebFetch
fails: `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`; Firecrawl
only if Scrapling fails. If a WebSearch returns a budget or cost notice, stop searching, write it
with the time into the .md, and return. It is informational: never continue from memory.

Boundaries: write only the two outputs and files under reports/stage_e8_briefs/pages/. Do not
touch strategy/, screening/, rules/, tests/, data/ or any other report (the release calendar and
the limit table are frozen: report, never edit). No bar reads (never open a parquet). No paid
source, no key, no login. No TopstepX reference. Do not spawn workers. Another worker may be
writing code under strategy/members/k6/ at the same time: never read or touch it.

Return: the two paths, a summary of at most 200 words, and anything you could not finish.
