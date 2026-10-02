# Brief: ReleaseChecker-OpusMed (Stage E.9 Task 1b), worker-medium on opus

Objective: check every dated input the three K8 members (4 trials) meet on the research window
(trade dates 2025-04-01..2026-06-19), and record a verdict per item (keep / drop / unverifiable),
each with a source URL or repository citation. K8 members read no free external price series, so
nothing is fetched into data/vendor/ (item F confirms). No judgment on results; the lead rules on
anything unclear.

The members (legs: signal leg read only, traded leg at q_c = 1):
- K8-flight-01 (H30 and HEOD): signal MES (group equity), traded MGC (group metals). Entry fills at
  t_k in {08:35, 08:40, ..., 14:55} CT; at most one entry a day; exits fill up to 15:05 CT.
- K8-oilcad-01: signal MCL (energy), traded 6C (fx). Entry fills at t in {08:05, 08:10, ..., 13:25}
  CT; exits 15 minutes later (last 13:40).
- K8-wkndbtc-01: signal MBT (crypto), traded MNQ (equity). Monday trade dates only: reads MBT's
  close of the bar at Friday 14:59 CT (the Friday before) and of the bar at Sunday 17:59 CT; entry
  fills on MNQ at Sunday 18:00 CT, exit fills Monday 14:59 CT.
C6 rule (all members): an entry whose fill would land in [release, release + 2 min) of a release
that concerns the TRADED product is skipped, not deferred.

Read first (by section, grep, never whole files): CLAUDE.md sections "Web research budgets",
"Page-fetch fallback", "Context hygiene"; reports/stage_e0_catalog_K8.md lines 86-249 (C1-C15:
C3 hours and the MBT regimes, C5 exclusions, C6 releases table, C10 calendars), 490-609
(K8-wkndbtc-01). Earlier release checks you may cite instead of re-fetching (grep them):
reports/stage_e4_release_check.md/.json (K4: WPSR, FOMC on MCL), stage_e4b (K5: MGC releases),
stage_e4c (K3: 6C releases), stage_e6 (K7: MBT, the 24/7 change), stage_e7 (K1: MNQ releases).

Items:
A. Release instants for C6 on each traded root (MGC, 6C, MNQ). The frozen release calendar
   reports/stage_e2b_release_calendar.json (key "releases"; each row has date, time_local, tz,
   instant_utc, products, evidence, source) is the engine's D9.5a and D8 input. Do not edit it.
   A1. For each traded root, list the research-window rows whose "products" include it, per
       release name and local time (expected counts: MGC NFP 14, CPI 14, G17 14, FOMC 10; 6C WPSR 64
       (56 at 10:30 ET, 7 at 12:00 ET, 1 at 17:00 ET), NFP 14, FOMC 10; MNQ ISM_SERVICES 15, NFP 14,
       CPI 14, FOMC 10). Report any difference.
   A2. Verdict per row: keep when the row's date and time equal the official record (BLS release
       schedule pages for Employment Situation and CPI, including the 2025 lapse-in-appropriations
       reschedules and cancellations; the Federal Reserve's FOMC calendar; EIA's WPSR schedule and
       its holiday exceptions; the Fed G.17 schedule; ISM's Services PMI calendar). An earlier
       stage's check of the same row (same date, time, release) may be cited as the evidence;
       re-check only rows no earlier check covers. Drop = the official date or time differs (give
       both). Unverifiable = no official record found.
   A3. From the calendar alone, list every row whose CT instant equals a K8 entry fill minute:
       flight-01 (MGC) instants in {08:35, ..., 14:55} on the 5-minute grid; oilcad (6C) instants in
       {08:05, ..., 13:25}; wkndbtc (MNQ) at Sunday 18:00 or Monday 14:59. Give date, release, CT time.
       Also list rows that equal an exit fill minute (flight up to 15:05; oilcad up to 13:40) for
       the record (exits are deferred by the engine, not skipped).
   A4. Any official release in the window that concerns these roots under the calendar's own
       release_products table but that the calendar lacks: list it (the members read the frozen
       calendar only; the lead rules).
B. K8-wkndbtc-01's clock points. For every Monday CT date in 2025-04-07..2026-06-15:
   B1. the Friday before (Monday - 3 days): is it a trade date with no early halt and the regular
       flatten in BOTH the equity and the crypto group calendars? (data.group_session
       .load_group_calendar("equity") and ("crypto"); rules.sessions.flatten_time_ct for MNQ and
       MBT; regular F is 15:08 CT);
   B2. the Monday: the same test in both calendars;
   B3. whether the group calendars have MBT open at Friday 14:59 CT and Sunday 17:59 CT and MNQ
       open at Sunday 17:59-18:00 CT and Monday 14:58-14:59 CT (session intervals of the trade
       date, data.group_session.session_intervals or the module's equivalent);
   B4. the trade date CME books the Sunday 17:59 MBT bar to in each regime (E.6's readings,
       reports/stage_e6_member_specs.md K7-L-01, data/group_session.py lines 30-40), and whether
       any Monday in the window is a booked-forward holiday.
   Write one row per Monday (JSON) and a count table: Mondays, Fridays not full, Mondays not full,
   eligible Mondays (both full, both clock points in session). Name each excluded Monday and why.
C. The 24/7 change (catalog section 6 item 11): the date and CT time CME moved bitcoin futures
   to continuous trading, quoted from CME's own release (the K7 catalog preamble and E.6's check
   name CME's releases of 19 Feb and 1 June 2026; cite E.6's saved quote if it has one), and the
   count of research-window trade dates and of B's eligible Monday trade dates on each side.
D. Roll blackouts. For each leg root (MES, MGC, MCL, 6C, MBT, MNQ), the research-window
   roll-blackout dates as earlier frozen runs recorded them: the single-leg members' runner records
   (reports/stage_e4b_k5_screen/ for MGC, stage_e4_k4_screen/ MCL, stage_e4c_k3_screen/ 6C,
   stage_e6_k7_screen/ MBT, stage_e7_k1_screen/ MNQ; key window_dates.excluded.roll_blackout_any_leg;
   read with a short python that prints only the date lists). MES has no Stage E single-leg record:
   find its research-window roll-blackout dates in reports/stage_e2a_bars.md/.json, the D.1
   records, or data/research_bars.py metadata (never open a parquet); if none, mark unverifiable
   (the runner computes it at run time). Then per member: the union of its legs' dates, and the
   UR-1 dates 2026-06-18 and 2026-06-19 (screening/stage_e_align.py). Give counts per member.
E. EC-CAL dates (read only): for the groups equity, crypto, metals, energy, fx, every weekday
   2025-04-01..2026-06-19 that is not a trade date, has early_halt_ct set, has a late open, or
   whose flatten time (rules.sessions.flatten_time_ct for MES/MNQ, MBT, MGC, MCL, 6C) is not 15:08.
   Quote the data/calendars/<group>.py record for each (grep). Then each member's full-session set
   size in the window (trade dates that are full sessions in both of its legs' groups).
F. External series: confirm by grep of reports/stage_e0_catalog_K8.md lines 252-609 that no active
   K8 member reads a price series from outside the bars, or any released value.

Outputs: reports/stage_e9_release_check.md (tables per item, verdicts, quotes) and
reports/stage_e9_release_check.json (per item rows with verdict, source URL or file citation,
quote, fetch time UTC, saved path and sha256; B's per-Monday rows; D's per-leg date lists). Save
every web page used as evidence raw under reports/stage_e9_briefs/pages/ (URL, UTC fetch time and
sha256 in the .json) and read it with grep; only quoted lines enter your context. Scripts print
counts and summaries, never whole tables.

Tools: Read, Grep, Bash (python with PYTHONPYCACHEPREFIX set to a fresh directory under
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/20d17daf-bbde-4768-93fa-814f35cbb398/scratchpad/1b/;
`uv run python` for repo imports), WebFetch, WebSearch (sparingly). Page fallback when WebFetch
fails: `scrapling extract get <url> <file>`, then `scrapling extract fetch <url> <file>`; Firecrawl
only if Scrapling fails. If a WebSearch returns a budget or cost notice, stop searching, write it
with the time into the .md, and return. It is informational: never continue from memory.
/tmp is a RAM-backed tmpfs: never copy the repository (or data/, .venv, .git) into it.

Boundaries: write only the two outputs and files under reports/stage_e9_briefs/pages/. Do not
touch strategy/, screening/, rules/, tests/, data/ or any other report (the release calendar and
group calendars are frozen: report, never edit). No bar reads (never open a parquet). No paid
source, no key, no login. No TopstepX reference. Do not spawn workers. Other workers may write
code under strategy/members/k8/ at the same time: never read or touch it.

Return: the two paths, a summary of at most 200 words, and anything you could not finish.
