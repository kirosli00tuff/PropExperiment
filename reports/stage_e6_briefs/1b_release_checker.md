# Brief: ReleaseChecker-OpusMed (Stage E.6 Task 1b), worker-medium on opus

Objective: check every dated input the K7 (bitcoin, MBT) members read on the research window
(trade dates 2025-04-01..2026-06-19), and record a verdict per item (keep / drop / unverifiable),
each with a source URL. No judgment on results; the lead rules on anything unclear.

Read first (by section, grep, never whole files): CLAUDE.md sections "Web research budgets",
"Page-fetch fallback", "Context hygiene"; reports/stage_e0_catalog_K7.md lines 171-190 (C9 EC-MBTX)
and 420-517 (K7-expiry-01), 595-694 (K7-montrend-01); data/calendars/crypto.py header (lines 1-80).

Items:
A. EC-MBTX. For each contract month 2025-04..2026-06, MBT's last trading day as CME publishes it
   (CME's MBT or BTC product calendar / contract specifications; cmegroup.com refuses automated
   fetches, so use Wayback captures on web.archive.org), against the rule-derived list in the catalog
   (lines 185-187: 2025-04-25, 05-30, 06-27, 07-25, 08-29, 09-26, 10-31, 11-28, 12-24, 2026-01-30,
   02-27, 03-27, 04-24, 05-29; June 2026 is 06-26, after the window, record it only). Look hard at
   2025-12: the rule gives Wed 12-24 (26 Dec is a UK bank holiday) but E.2a's bar check saw the
   expiring contract stop at 09:59 CT on Fri 12-26 (reports/stage_e2a_calendar_bar_checks.md line
   672; lines 663-675 for the other months). For each date: T_exp = 16:00 Europe/London converted to
   America/Chicago with zoneinfo (UK and US clock changes; expect 10:00 CT, 11:00 CT on 2025-10-31
   and 2026-03-27), and a quote that final settlement is the CME CF Bitcoin Reference Rate (BRR) at
   4:00 p.m. London. Verdict per date: keep (CME confirms), drop (CME shows a different date; give
   the CME date and quote), unverifiable (no CME source found; kept as the rule gives it).
B. Sunday-evening opens read by K7-montrend-01. For every Monday 2025-04-07..2026-06-15: is it an
   EC-CAL crypto trade date (data.group_session.load_group_calendar("crypto").is_trade_date; the
   BOOKED_FORWARD holidays are not) and is the engine's flatten time regular
   (rules.sessions.flatten_time_ct("MBT", d) == 15:08)? List the Mondays that fail either. Then cite,
   from the sources already recorded in data/calendars/crypto.py and
   reports/stage_e2a_calendar_sources_crypto.md (grep; no new web fetch needed unless a quote is
   missing), CME's Sunday 17:00 CT open before 2026-05-29 and continuous trading from Friday
   2026-05-29 16:00 CT (the 2026-02-19 and 2026-06-01 press releases).
C. The E.2a L-9 guard. From code and tests only, confirm that no MBT bar booked to a trade date on or
   after 2026-06-18 reaches a member on the research window: the runner's loader (grep
   screening/stage_e_runner.py for the bar loader, data/stage_e_bars.py), data/trade_date_guard.py,
   screening/stage_e_align.py (rule UR-1), and reports/stage_e2a_bars.json (the MBT file's last trade
   date and dropped rows). Run `uv run pytest -q tests/test_e2b_trade_date_guard.py` and any
   stage_e_bars test that covers holdout-1 refusal. Do NOT open any parquet or bar file, and do not
   call a bar loader.
D. Holiday inputs of the EC-MBTX rule, 2021-05..2026-06: the England-and-Wales bank holidays
   (strategy/members/k3/_calendar.py EW_BANK_HOLIDAYS, source reports/stage_e4c_release_check.json;
   confirm it covers 2021-2026 and check it against gov.uk's bank-holidays JSON
   https://www.gov.uk/bank-holidays.json, saved raw) and the US federal holidays (observed dates)
   plus Good Friday 2021-2026 with a source (OPM federal holidays pages; Good Friday from the CME
   equity calendar data/cme_calendar.py HOLIDAYS). Output both lists in the JSON.
E. For the record only, no verdict: from reports/stage_e0_symbology.json (MBT.v.0 roll intervals;
   metadata, not bars) list for each rule-derived EC-MBTX date 2021-05..2026-06 the trade date on
   which the MBT.v.0 instrument changes next (the splice), and whether the expiry date lies inside the
   roll blackout (the splice trade date and the 2 crypto trade dates before it, from the crypto
   calendar). Count how many survive, research window and 2021-05-03..2024-02-29 separately.

Outputs: reports/stage_e6_release_check.md (tables per item, verdicts, quotes) and
reports/stage_e6_release_check.json (machine-readable: per item rows with verdict, source URL, quote,
fetch time UTC, saved page path and sha256). Save every page used as evidence raw under
reports/stage_e6_briefs/pages/ and read it with grep; only quoted lines enter your context.

Tools: Read, Grep, Bash (python with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/0f52aad4-207e-43da-84df-b6a0ead28371/scratchpad/),
WebFetch, WebSearch (sparingly). Page fallback when WebFetch fails: `scrapling extract get <url>
<file>`, then `scrapling extract fetch <url> <file>`; Firecrawl only if Scrapling fails. If a
WebSearch returns a budget or cost notice, stop searching, write it with the time into the .md, and
return. It is informational: never continue from memory.

Boundaries: write only the two outputs and files under reports/stage_e6_briefs/pages/. Do not
touch strategy/, screening/, data/, rules/, tests/ or any other report. No bar reads. No paid source,
no key, no login. No TopstepX reference. Do not spawn workers.

Return: the two paths, a summary of at most 200 words, and anything you could not finish.
