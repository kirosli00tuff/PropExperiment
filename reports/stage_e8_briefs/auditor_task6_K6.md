# Brief: MemberAuditor-K6-FableXHigh, part 2 (Stage E.8, K6, Task 6: recomputation)

You are resumed with this small brief. The objective is one: independently recompute the screen figures of K6's
research-window run and check each tier against the frozen D5. You wrote none of the runner or member code, and you did
not run the screen. Written by the Stage E.8 lead, 2026-10-01 02:17 PDT.

## Inputs

- The runner's outputs in reports/stage_e8_k6_screen/ (run 02:10:25-02:12:46 PDT, "K6 research: 27 members, 0 refused";
  log reports/stage_e8_briefs/t5_run.log): one record per trial, K6_<label>_research.json (series.dates, series.values in
  net ticks per contract per day, screen, power, labels, trade_rate, daily_net_usd, engine with accounts_started and
  counters, window_dates with its exclusions, coverage), its trip list K6_<label>_research_trips.json (every trip with
  root, open_utc/close_utc, trade_date, contracts, gross_cents, net_cents, close_reason, locked, and the record's sha256),
  and K6_research_cluster.json (tiers, not_tiered, refused_members). Read them with short scripts that print only the
  fields you need.
- The frozen D5: docs/STAGE_E_DESIGN.md lines 298-345: research-window mean net P&L > 0 and daily t >= 1.0, zeros on
  no-trade days, t = mean / (population sd / sqrt(n)) (screening/stage_e_stats.py). Learn the tier rules from
  stage_e_stats.assign_tiers and OC-H (reports/E.4_RETURN.md line 375), but compute in your own code.
- The frozen cost table and vehicles: reports/stage_e2a_costs.json and reports/stage_e2a_vehicles.json (through
  screening.stage_e_frozen or directly); the release calendar reports/stage_e2b_release_calendar.json (D8's event-window
  cost and D9.5a; K6 roots' research-window rows: WASDE and CROP 11:00 CT, CROP_ANNUAL 11:00 CT, CROP_PROGRESS 15:00 CT,
  FOMC 13:00 CT).
- The tables the members traded on: strategy/members/k6/_calendar.py, _wasde.py, _limits.py, and specs sections 5-7 and 10
  (reports/stage_e8_member_specs.md). The frozen member code is commit 0a14a9a (cluster freeze
  reports/stage_e_k6_member_freeze.json, sha256 a6f8b497...).

## What to produce (Part 2 of reports/stage_e8_member_audit.md, under its existing heading)

0. The frozen files: every file under strategy/members/k6/ equals the cluster freeze (sha256 per file) and the files you
   audited in Part 1 (no change was made after Part 1; reports/stage_e8_member_rulings.md).
1. For every record: recompute mean and daily t from series.values in your own code; check one value per window date with
   zeros on no-trade days (the dates equal the window's trade dates; non-zero days at most the trading days). Compare with
   the record's screen (mean_ticks, t_daily, passes) to 1e-9 relative. K6-limitcont-01 LE has 0 trips (t undefined): say
   how the screen and the tier treat it.
2. Check each tier in K6_research_cluster.json against D5, OC-H and the labels (Tier A = passes the screen, not excluded;
   Tier B = every other screened trial; excluded = coverage below 0.95 or a D9 floor label). The runner put one trial in
   Tier A: K6-limitcont-01 HE, on a single trip (mean +0.1869 ticks/day, t 1.002). Check the arithmetic that a single
   positive day among n zero days gives t = sqrt(n / (n - 1)) >= 1 whatever its size, and say whether anything in the
   frozen D5 or OC-H text excludes it (the lead found nothing; confirm or refute).
3. For two trials, K6-cp2-01 ZC (a port whose fills can meet the 11:00 USDA and 13:00 FOMC event windows, with fill-guard
   deferrals and forced flattens) and K6-limitcont-01 HE (the Tier A trial; one trip closed by D9.7's forced exit):
   rebuild the daily series from the runner's trip list and the frozen cost table in YOUR own code, with no replay: each
   trip's net = gross - commission - slippage per side (slippage by the fill's 30-minute CT bucket, D8's event-window rule
   for fills in [release, release + 30 min) of a release concerning the root, the D9.7 exit's event-window cost as D9.7
   states, rounding as the frozen table rules), summed per trade date, converted to net ticks per contract (tick value
   $12.50 for ZC, $10.00 for HE; q_c 1), matched against series.values and daily_net_usd day by day. Check that each trip
   list's record_sha256 equals its record file's sha256. If gross cannot be checked without prices, say so and check
   everything else.
4. Trade counts against the checked event tables:
   - K6-wasdepre-01 ZC and ZS, K6-wasdepost-01 ZC: the research-window WASDE dates (WASDE_DATES; 14, none dropped by
     R-1b-1) in GRAIN_FULL_SESSIONS, less the trial's window exclusions (roll blackout, UR-1); every such date has one trip
     or an explanation from the record (zero signal cannot be checked without prices: say which dates remain unexplained
     and whether the counters account for them); no trip on any other date; entry and exit fill minutes per the rule
     (wasdepre 10:30 / 11:15, wasdepost 11:15 / 13:14) or a documented deviation (D9.5a, missing bar, D9.7, MLL).
   - K6-limitcont-01 HE and LE: the event condition needs settlement-proxy prices, which you cannot read (no bar file may
     be opened). Check what you can: every trip on a LIVESTOCK_FULL_SESSIONS date at least three livestock trade dates
     after the window's first date (N-9), with d-1 and d-2 not in DROPPED_LIMIT_DATES, entry fill 08:45, exit 12:59 or a
     documented engine exit; and list the dates whose d-1 or d-2 is a dropped LE date (R-1b-2) inside the LE window.
   - K6-crushgap-01 ZS: trips only on GRAIN_FULL_SESSIONS dates, entry fill 08:31, exit 13:14 or a documented engine exit,
     never a ZM or ZL position (legs in the record).
   - The ports: at most one entry per trade date; fill minutes per the rule (CP1 grains 12:45 / 13:14, livestock 12:30 /
     12:59; CP3 08:31 / 13:14 or 12:59; CP2 75 minutes or F) or a documented deviation. List anything unexplained.
5. Program N: the runner does not count N. Give the number of screened trials (records with status "run" and a screen),
   any refused or excluded, whether any record shows a trial the freeze does not declare, and N = 167 + screened (the
   lead's pre-declared rule, specs K6-L-17).
6. The MLL liquidations: count them per trial (accounts_started - 1, or the counters) and say whether any trial's tier
   could depend on them (in particular the Tier A trial and any Tier B trial whose mean would turn positive with MLL-closed
   trips removed, reported as a bound, not an estimate).

Grade each item VERIFIED, VERIFIED WITH NOTES or DISCREPANCY, and give the time you started and ended (PDT). Return to the
lead: the report path, a summary of at most 200 words (counts by verdict, each DISCREPANCY named), and anything unfinished.
If the harness refuses the write, return the full Part 2 text in your final message.

## Boundaries

Read-only except Part 2 of your report and your own scripts under reports/stage_e8_briefs/audit_k6/. Never re-run the
runner or any member on real bars; never open a bar file (data/processed*). Every check uses the runner's recorded outputs
and the frozen tables only. No repository copy is needed for this part; if you make any scratch copy, exclude data/,
.venv and .git and keep it under 1 GB in the scratchpad. No git changes, no web, no workers.
