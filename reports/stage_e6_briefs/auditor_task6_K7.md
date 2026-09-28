# Brief: MemberAuditor-K7-FableXHigh, part 2 (Stage E.6, K7, Task 6: recomputation)

You are resumed with this small brief. The objective is one: independently recompute the screen figures of K7's
research-window run and check each tier against the frozen D5. You wrote none of the runner or member code, and you did
not run the screen.

## Inputs

- The runner's outputs in reports/stage_e6_k7_screen/: one record per trial, K7_<label>_research.json (series.dates,
  series.values in net ticks per contract per day, series.n_trips, screen, power, labels, trade_rate, daily_net_usd,
  engine counters, window_dates with its exclusions, coverage), its trip list K7_<label>_research_trips.json (every trip
  with root, open/close timestamps, trade_date, contracts, gross_cents, net_cents, close_reason, locked, and the
  record's sha256), and K7_research_cluster.json (tiers, not_tiered, refused_members). Read them with short scripts that
  print only the fields you need.
- The frozen D5: docs/STAGE_E_DESIGN.md lines 298-345: research-window mean net P&L > 0 and daily t >= 1.0, zeros on
  no-trade days, t = mean / (population sd / sqrt(n)) (screening/stage_e_stats.py). Learn the tier rules from
  stage_e_stats.assign_tiers and OC-H, but compute in your own code.
- The frozen cost table and vehicles: reports/stage_e2a_costs.json and reports/stage_e2a_vehicles.json (through
  screening.stage_e_frozen or directly); the release calendar reports/stage_e2b_release_calendar.json (D8's event-window
  cost and D9.5a; MBT's rows are NFP, CPI, PPI at 07:30 CT and FOMC at 13:00 CT).
- The event tables the members traded on: strategy/members/k7/_calendar.py (CRYPTO_FULL_SESSIONS, VENDOR_DEGRADED, MBTX)
  and specs section 9 (reports/stage_e6_member_specs.md).
- The run log: reports/stage_e6_STATE.md (Task 5 lines) and reports/stage_e6_briefs/t5_run.log.

## What to produce (Part 2 of reports/stage_e6_member_audit.md, under its existing heading)

1. For every record: recompute mean and daily t from series.values in your own code; check one value per window date
   with zeros on no-trade days (the dates equal the window's trade dates; non-zero days at most n_trips). Compare with
   the record's screen (mean_ticks, t_daily, passes) to 1e-9 relative.
2. Check each tier in K7_research_cluster.json against D5, OC-H and the labels (Tier A = passes the screen, not excluded;
   Tier B = every other screened trial; excluded = coverage below 0.95), including how any floor label enters.
3. For two trials, K7-cp2-01 MBT (a port, the one whose fills can meet the FOMC event window) and K7-montrend-01 MBT (its
   Sunday-evening fills use D8's overnight buckets; if it has no trips, take K7-rev2h-01 MBT instead and say so): rebuild
   the daily series from the runner's trip list and the frozen cost table in YOUR own code, with no replay: each trip's
   net = gross - commission - slippage per side (slippage by the fill's 30-minute CT bucket, D8's event-window rule for
   fills in [release, release + 30 min) of a release concerning MBT, rounding as the frozen table rules), summed per
   trade date, converted to net ticks per contract (tick value $0.50), matched against series.values and daily_net_usd
   day by day. Check that each trip list's record_sha256 equals its record file's sha256. If gross cannot be checked
   without prices, say so and check everything else.
4. Trade counts: reconcile K7-expiry-01's trips with MBTX (research rows) and the window's roll-blackout exclusions
   (every untraded date explained: roll blackout, early halt, not a full session, vendor-degraded, missing bar, UR-1,
   engine refusal); K7-montrend-01's with the Monday trade dates in CRYPTO_FULL_SESSIONS less VENDOR_DEGRADED and the
   window's exclusions; K7-rev2h-01's with the full sessions (at most 2 entries a day). Check each trip's entry and exit
   fill minutes against the rule (expiry: both T_exp slots; montrend: hh:00 / hh:01 and 14:00) or a documented deviation
   (D9.5a, missing bar, F, MLL). List anything unexplained.
5. Program N: the runner does not count N. Give the number of screened trials (records with status "run" and a screen),
   any refused or excluded, whether any record shows a trial the freeze does not declare, and N = 150 + screened (the
   lead's pre-declared rule, specs K7-L-05).
6. The MLL liquidations: count them per trial (accounts_started - 1, or the counters) and say whether any trial's tier
   could depend on them.

Grade each item VERIFIED, VERIFIED WITH NOTES or DISCREPANCY, and give the time you started and ended (PDT). Return to the
lead: the report path, a summary of at most 200 words (counts by verdict, each DISCREPANCY named), and anything unfinished.

## Boundaries

Read-only except Part 2 of your report and your own scripts under reports/stage_e6_briefs/audit_k7/. Never re-run the
runner or any member on real bars; never open a bar file (data/processed*). Every check uses the runner's recorded outputs
and the frozen tables only. No git changes, no web, no workers.
