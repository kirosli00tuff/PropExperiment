# Brief: MemberAuditor-K4-FableXHigh, part 2 (Stage E.4 Part 1, Task 6: recomputation)

You are resumed with this small brief. The objective is one: independently recompute the screen figures
of K4's research-window run and check each tier against the frozen D5. You wrote none of the runner or
member code, and you did not run the screen.

## Inputs

- The runner's outputs in reports/stage_e4_k4_screen/: one record per trial, K4_<label>_research.json
  (series.dates, series.values in net ticks per contract per day, series.n_trips, screen, power, labels,
  trade_rate, daily_net_usd, engine counters), its trip list K4_<label>_research_trips.json (harness v4:
  every trip with root, open/close timestamps, trade_date, contracts, gross_cents, net_cents,
  close_reason, locked, and the record's sha256), and K4_research_cluster.json (tiers, not_tiered,
  refused_members). Read them with short scripts that print only the fields you need.
- The frozen D5: docs/STAGE_E_DESIGN.md lines 298-345. The screen is research-window mean net P&L > 0
  and daily t >= 1.0, with zeros on no-trade days, t = mean / (population sd / sqrt(n))
  (screening/stage_e_stats.py). Learn the tier rules from stage_e_stats.assign_tiers, but compute in your
  own code.
- The frozen cost table and vehicles: reports/stage_e2a_costs.json and reports/stage_e2a_vehicles.json
  (through screening.stage_e_frozen or directly); the release calendar reports/stage_e2b_release_calendar.json
  (for D8's event-window cost and D9.5a).
- The event tables the members traded on: strategy/members/k4/_releases.py and _calendar.py, and specs
  section 11 (reports/stage_e4_member_specs.md).
- The run log: reports/stage_e4_STATE.md (Task 5 lines).

## What to produce (Part 2 of reports/stage_e4_member_audit.md, under its existing heading)

1. For every record: recompute mean and daily t from series.values in your own code; check one value per
   window date with zeros on no-trade days (the dates equal the window's trade dates; non-zero days at most
   n_trips). Compare with the record's screen (mean_ticks, t_daily, passes) to 1e-9 relative.
2. Check each tier in K4_research_cluster.json against D5 and the labels (Tier A = passes the screen, not
   excluded; Tier B = every other screened trial; excluded = coverage below 0.95), including how any floor
   label enters.
3. For two trials, K4-cp1-01 MCL (a port) and K4-ngpre-01 NG (an event member): rebuild the daily series from
   the runner's trip list and the frozen cost table in YOUR own code, with no replay (harness v4 writes the
   trips): check each trip's net = gross - commission - slippage per side (slippage by the fill's 30-minute
   CT bucket, the D8 event-window rule for fills in [release, release + 30 min) of a release concerning the
   product, ceil to the cent as the frozen table rules), sum per trade date, convert to net ticks per
   contract, and match series.values and daily_net_usd day by day. Check that the trip list's record_sha256
   equals the record file's sha256. If a trip's gross cannot be checked without prices, say so and check
   everything else.
4. Trade counts: reconcile each event member's trips with the checked event table (ngpre with NGS in the
   window; apipre with the 55 standard weeks; eiafade with WPSR rows passing T_W + 15 <= 13:13; eiamom
   with standard Wednesdays not in NYSE_NOT_FULL), explaining every untraded event (roll blackout, early
   halt, missing bar, UR-1, zero signal, threshold not met, engine refusal) from the records and trips; list
   any unexplained. Check that every trip's entry and exit fill minutes match the rule's fill minutes or a
   documented deviation (D9.5a guard, missing bar, F, MLL liquidation). For ovr, check at most 5 entries a
   day and no overlap.
5. Program N: the runner does not count N. Give the number of screened trials (records with status "run"
   and a screen), any refused or excluded, whether any record shows a trial the freeze does not declare, and
   N = 102 + screened.
6. The MLL liquidations: count them per trial (the engine's accounts_started - 1, or the counters) and say
   whether any trial's tier could depend on them.

Grade each item VERIFIED, VERIFIED WITH NOTES or DISCREPANCY, and give the time you started and ended (PDT).
Return to the lead: the report path, a summary of at most 200 words (counts by verdict, each DISCREPANCY
named), and anything unfinished.

## Boundaries

Read-only except Part 2 of your report and your own scripts under reports/stage_e4_briefs/audit/. Never
re-run the runner or any member on real bars; never open a bar file (data/processed*). Every check uses the
runner's recorded outputs and the frozen tables only. No git changes, no web, no workers.
