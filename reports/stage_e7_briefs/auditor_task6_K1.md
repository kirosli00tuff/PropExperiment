# Brief: MemberAuditor-K1-FableXHigh, part 2 (Stage E.7, K1, Task 6: recomputation)

You are resumed with this small brief. The objective is one: independently recompute the screen figures of K1's
research-window run and check each tier against the frozen D5. You wrote none of the runner or member code, and you did
not run the screen.

## Inputs

- The runner's outputs in reports/stage_e7_k1_screen/: one record per trial, K1_<label>_research.json (series.dates,
  series.values in net ticks per contract per day, series.n_trips, screen, power, labels, trade_rate, daily_net_usd,
  engine counters, window_dates with its exclusions, coverage), its trip list K1_<label>_research_trips.json (every trip
  with root, open/close timestamps, trade_date, contracts, gross_cents, net_cents, close_reason, locked, and the
  record's sha256), and K1_research_cluster.json (tiers, not_tiered, refused_members). Read them with short scripts that
  print only the fields you need. (File names as the runner wrote them; list the directory first.)
- The frozen D5: docs/STAGE_E_DESIGN.md lines 298-345: research-window mean net P&L > 0 and daily t >= 1.0, zeros on
  no-trade days, t = mean / (population sd / sqrt(n)) (screening/stage_e_stats.py). Learn the tier rules from
  stage_e_stats.assign_tiers and OC-H, but compute in your own code.
- The frozen cost table and vehicles: reports/stage_e2a_costs.json and reports/stage_e2a_vehicles.json (through
  screening.stage_e_frozen or directly); the release calendar reports/stage_e2b_release_calendar.json (D8's event-window
  cost and D9.5a; the three roots' rows are FOMC 13:00 CT, ISM_SERVICES 09:00 CT, NFP 07:30 CT, and CPI 07:30 CT with the
  D9.12 window).
- The tables the members traded on: strategy/members/k1/_calendar.py (EQUITY_TRADE_DATES, EQUITY_FULL_SESSIONS) and
  strategy/members/k1/_vxn.py (VXN_CLOSE), and specs section 9 (reports/stage_e7_member_specs.md).
- The run log: reports/stage_e7_STATE.md (Task 5 lines) and reports/stage_e7_briefs/t5_run.log.

## What to produce (Part 2 of reports/stage_e7_member_audit.md, under its existing heading)

0. The frozen files: every file under strategy/members/k1/ equals the cluster freeze reports/stage_e_k1_member_freeze.json
   (sha256 per file) and, apart from the Task 4 fixes named in reports/stage_e7_member_rulings.md, the files you audited.
1. For every record: recompute mean and daily t from series.values in your own code; check one value per window date
   with zeros on no-trade days (the dates equal the window's trade dates; non-zero days at most the trading days). Compare
   with the record's screen (mean_ticks, t_daily, passes) to 1e-9 relative.
2. Check each tier in K1_research_cluster.json against D5, OC-H and the labels (Tier A = passes the screen, not excluded;
   Tier B = every other screened trial; excluded = coverage below 0.95), including how any floor label enters.
3. For two trials, K1-cp2-01 MNQ (a port whose fills can meet the 09:00 ISM and 13:00 FOMC event windows) and K1-vwap-01
   MNQ (many trips a day, reversals): rebuild the daily series from the runner's trip list and the frozen cost table in
   YOUR own code, with no replay: each trip's net = gross - commission - slippage per side (slippage by the fill's
   30-minute CT bucket, D8's event-window rule for fills in [release, release + 30 min) of a release concerning the root,
   rounding as the frozen table rules), summed per trade date, converted to net ticks per contract (tick value $0.50;
   q_c contracts), matched against series.values and daily_net_usd day by day. Check that each trip list's record_sha256
   equals its record file's sha256. If gross cannot be checked without prices, say so and check everything else.
4. Trade counts: reconcile K1-vxnband-01's trips with its event table: the window dates in EQUITY_FULL_SESSIONS whose V
   (VXN_CLOSE of the EC-CAL trade date before d) exists and satisfies V < 20 or V >= 30, less the window's exclusions
   (roll blackout, UR-1); every such date either has one trip or an explanation (no breach, missing bar, instrument, C_prev
   guard, engine refusal); no trip on any other date. Check its entry and exit fill minutes (exit fill 30 minutes after the
   entry fill, or a documented deviation: D9.5a, missing bar, F, MLL). K1-vwap-01: at most 20 entries a trade date, every
   hold >= 2 minutes, last fill <= 14:59, trips only on EQUITY_FULL_SESSIONS dates. The ports: at most one entry a trade
   date, fill minutes per the rule (CP1 14:30 / 14:59, CP3 08:31 / 14:59, CP2 75 minutes or F) or a documented deviation.
   List anything unexplained.
5. Program N: the runner does not count N. Give the number of screened trials (records with status "run" and a screen),
   any refused or excluded, whether any record shows a trial the freeze does not declare, and N = 156 + screened (the
   lead's pre-declared rule, specs K1-L-16).
6. The MLL liquidations: count them per trial (accounts_started - 1, or the counters) and say whether any trial's tier
   could depend on them.

Grade each item VERIFIED, VERIFIED WITH NOTES or DISCREPANCY, and give the time you started and ended (PDT). Return to the
lead: the report path, a summary of at most 200 words (counts by verdict, each DISCREPANCY named), and anything unfinished.

## Boundaries

Read-only except Part 2 of your report and your own scripts under reports/stage_e7_briefs/audit_k1/. Never re-run the
runner or any member on real bars; never open a bar file (data/processed*). Every check uses the runner's recorded outputs
and the frozen tables only. No git changes, no web, no workers.
