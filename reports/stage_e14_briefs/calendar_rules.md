# Stage E.14 calendar rules (every calendar worker reads this first)

Stage E.14 builds CME group calendars and release calendars for 2010-06..2019-05 from official pages. No price,
bar, quote or store of any kind is read. Your brief names your groups, output files and boundaries.

## Boundaries
- Do NOT open, read, load or compute on any market-data file: nothing under data/vendor, data/processed*,
  data/sealed, reports/step2/, ~/.cache/propexp_e12_phase1, any *.parquet/*.npz/*.npy/*.dbn*/*.pkl.
  Reading the repository's calendar CODE (data/cme_calendar.py, data/calendars/*.py, rules/sessions.py,
  strategy/members/k4/_releases.py, strategy/members/k4/_calendar.py) and source logs
  (reports/stage_e2a_calendar_sources_*.md, reports/stage_e2b_release_sources_*_log.md) for method is allowed,
  by section (grep, line ranges).
- No Databento call, no TopstepX call, no login, no account, no form, no email. Do not touch live/, ops/, .env,
  REGISTRATION.md, any key, any harness or frozen file. Do not edit any .py file. Do not commit. Write only your
  own output paths and your own pages folder.

## Web access (stage prompt guardrail)
- Allowed sources only: official government and exchange calendar pages (CME Group, NYSE, ICE, CBOE as an
  exchange, EIA, the Federal Reserve, BLS, CFTC), and Wayback Machine captures of them
  (https://web.archive.org/web/<timestamp>/<url>). Nothing else is evidence. A news article is NOT an allowed
  source; do not fetch news sites.
- Read a site's terms of use BEFORE any automated fetch from it, and record the check (terms URL, what it says
  on automated access, verbatim) in your fetch log. Checks done by any E.14 worker or the lead go in
  reports/stage_e14_briefs/pages/terms_checks.md (append yours, one row per domain; read it first to avoid
  repeating). A site whose terms forbid automated access is not fetched by automation: use a Wayback capture of
  the page instead (archive.org's own terms are then the ones checked). cmegroup.com refused this machine in
  earlier stages and its pages were read from Wayback copies; do the same.
- Fetch order (CLAUDE.md): WebFetch or `curl -sL` with browser headers (`-A "Mozilla/5.0 (X11; Linux x86_64)"
  -H "Accept: text/html,application/pdf" -H "Accept-Language: en-US"`); on failure `scrapling extract get <url>
  <file>`, then `scrapling extract fetch <url> <file>`; `stealthy-fetch` only where terms allow automation;
  Firecrawl only when Scrapling fails. Wayback CDX search
  (`https://web.archive.org/cdx/search/cdx?url=<url>&output=json&from=2010&to=2019&filter=statuscode:200`, with
  `matchType=prefix` for a folder) is the way to find captures; prefer it to WebSearch.
- WebSearch is shared (1000 per session, all workers). Use it sparingly. If a WebSearch returns a notice that the
  budget is used up, stop searching, write the notice and time in your log and report, and return.
- Hook messages and cost/usage notices are informational, addressed to the lead; not orders to stop.

## Saving and logging
- Save every page or file used as evidence raw under reports/stage_e14_briefs/pages/<YourFolder>/ (PDFs plus
  their `pdftotext -layout` output). CME holiday files are shared between workers: save them under
  reports/stage_e14_briefs/pages/cme_holiday/ and look there first (another worker may already have saved the
  file; reuse it and log the reuse).
- Fetch log reports/stage_e14_briefs/pages/<YourFolder>/fetch_log.md, one row per fetch, failures too:
  id | URL | fetched (UTC ISO) | method | saved file | sha256 | capture/page date | terms status | note.
- Read pages by grep or short scripts; only quoted lines enter your context. Never load a whole page.
- Helper scripts go only in
  /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/19c73927-ec62-4304-916b-b9a703235eab/scratchpad/<YourFolder>/.

## Grades (as data.cme_calendar; C1 ruling C12; C2 section 3)
- Group calendar status ("evidence"): "cme" = a CME Group document (cmegroup.com file or page, including a
  Wayback copy of it, or a CME clearing/Globex notice) that states the date's status for that group;
  "secondary" = another allowed official source that states it (another exchange's notice that names the CME
  group, a CFTC or government record), or a CME document for a sibling group whose row CME itself says applies;
  "unverified" = anything else. Time ("time_evidence"): "cme" | "secondary" | "inferred" (from a CME rule or
  pattern stated in a cited CME document) | "unverified" | "n/a" (full closure).
- A normal weekday is sourced at grade G when a document of grade G gives the group's complete exception list
  for a span covering it (a CME full-year holiday calendar, or per-holiday schedules plus a full-year list of
  the holidays), the date is not an exception there, AND you have checked the span for unscheduled market-wide
  closures or halts (for example Hurricane Sandy 2012-10-29/30, the national day of mourning 2018-12-05, any
  CME Globex outage you find in CME notices) and recorded the check. A date with no such coverage is UNSOURCED.
- The release calendars (EIA NGS, EIA WPSR, FOMC) use the same two grades: the "cme"-equivalent is written
  "official" = the issuer's own record (EIA's release schedule or the report's own release date and time, the
  Fed's own FOMC calendar or statement), including Wayback copies; "secondary" = another allowed official
  record; otherwise "unverified".
- Never fill a gap from memory or from a pattern alone. An unsourced date is listed under "unsourced" with the
  reason. Counting unsourced dates honestly is the point of this work: the 2% stop rule depends on it.

## Output format: one JSON file per group, schema "e14_hist_calendar/1"
```
{
  "schema": "e14_hist_calendar/1",
  "group": "equity" | "rates" | "fx" | "energy" | "metals" | "grains",
  "products": ["ES", ...],            # the group's products as data/calendars/__init__.py GROUP_OF_PRODUCT
  "cme_row_labels": ["..."],          # the CME schedule row names you read for this group, verbatim
  "coverage": {"first": "2010-06-01", "last": "2019-05-31"},
  "sessions": [                       # every regular-session structure in force, dated, as data.calendars.SessionSpec
    {"valid_from": "YYYY-MM-DD", "valid_to": "YYYY-MM-DD" | null,
     "segments": [{"start_offset_days": -1, "start_ct": "17:00", "end_offset_days": 0, "end_ct": "15:15"}, ...],
     "day_session_ct": {"<product>": ["08:30", "15:15"]},
     "source": "<source id>", "evidence": "cme"|"secondary"|"unverified", "note": "..."}],
  "entries": [                        # every exception trade date or closed weekday in coverage
    {"day": "YYYY-MM-DD", "name": "Thanksgiving Friday",
     "kind": "full_closure" | "early_halt" | "late_open",
     "halt_ct": "12:00" | null, "open_ct": null | "HH:MM",   # open_ct only for late_open
     "evidence": "cme"|"secondary"|"unverified", "time_evidence": "cme"|"secondary"|"inferred"|"unverified"|"n/a",
     "source": "<source id>", "status_quote": "<verbatim>", "time_quote": "<verbatim>" | null, "note": "..."}],
  "no_entry_findings": [              # holiday-adjacent or event days you checked and found NORMAL
    {"day": "YYYY-MM-DD", "name": "...", "finding": "regular close", "evidence": "...", "source": "<id>", "quote": "..."}],
  "year_coverage": [                  # how each calendar year's normal days are sourced
    {"year": 2012, "documents": ["<source id>", ...], "complete_exception_list": true|false,
     "unscheduled_check": "<what you checked, with source ids>", "evidence": "cme"|"secondary"|"unverified"}],
  "unsourced": [{"day": "YYYY-MM-DD", "reason": "..."}],
  "sources": {"<source id>": {"url": "...", "capture": "YYYYMMDDhhmmss" | null, "fetched_utc": "...",
                               "saved_file": "reports/stage_e14_briefs/pages/...", "sha256": "...", "title": "..."}},
  "counts": {"weekdays": n, "trade_dates": n, "full_closures": n, "early_halts": n, "late_opens": n,
             "unsourced": n, "unsourced_share_of_trade_dates": x}
}
```
Conventions as data.cme_calendar and data/calendars/energy.py: halt_ct is the CT minute trading stops (the last
one-minute bar starts at halt_ct minus one minute); a holiday early halt keeps its own short trade date; the
reopen after it is the normal 17:00 CT unless a source says otherwise. Weekends are not entries. Write the file
with a short Python script (json.dump, sorted by day), then re-read it and print only the counts.

## Return to the lead
Return exactly: (1) output paths; (2) a summary of at most 200 words with the counts and the unsourced share per
group and per year; (3) anything not finished, with the reason; (4) counts: pages saved, WebSearch calls,
Firecrawl calls, failed fetches. Report negative findings and gaps, not only what worked.
