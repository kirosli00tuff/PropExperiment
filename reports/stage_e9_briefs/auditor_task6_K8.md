# Brief: MemberAuditor-K8-FableXHigh, part 2 (Stage E.9, K8, Task 6: recomputation)

You are resumed with this small brief. The objective is one: independently recompute the screen figures of K8's
research-window run and check each tier against the frozen D5. You wrote none of the runner or member code, and you did
not run the screen. Written by the Stage E.9 lead, 2026-10-01 23:55 PDT.

## Inputs

- The runner's outputs in reports/stage_e9_k8_screen/ (run 23:53:04-23:53:59 PDT, "K8 research: 4 members, 0 refused";
  log reports/stage_e9_briefs/t5_run.log; the lead's field summary reports/stage_e9_briefs/t5_summary.out): one record per
  trial, K8_<label>_research.json (series, screen, power, labels, trade_rate, daily_net_usd, engine with
  accounts_started and counters, window_dates with its exclusions, coverage), its trip list
  K8_<label>_research_trips.json, and K8_research_cluster.json (tiers). Read them with short scripts that print only the
  fields you need.
- The frozen D5: docs/STAGE_E_DESIGN.md lines 298-345 (research-window mean net P&L > 0 and daily t >= 1.0, zeros on
  no-trade days; t = mean / (population sd / sqrt(n)), screening/stage_e_stats.py). Learn the tier rules from
  stage_e_stats.assign_tiers and OC-H (reports/E.4_RETURN.md line 375), but compute in your own code.
- The frozen cost table and vehicles (reports/stage_e2a_costs.json, reports/stage_e2a_vehicles.json, or
  screening.stage_e_frozen); the release calendar reports/stage_e2b_release_calendar.json (D8's event-window cost, D9.5a).
- The tables the members traded on (strategy/members/k8/_calendar.py, _releases.py), specs sections 1-3 and 7
  (reports/stage_e9_member_specs.md), the Task 1b check reports/stage_e9_release_check.json (B: the 54 Mondays; D: roll
  blackouts per leg). The frozen member code is commit 558a5dc (cluster freeze reports/stage_e_k8_member_freeze.json,
  sha256 99f5a6ce...).

## What to produce (Part 2 of reports/stage_e9_member_audit.md, under its existing heading)

0. The frozen files: every file under strategy/members/k8/ equals the cluster freeze (sha256 per file) and the files you
   audited in Part 1 (no change was made after Part 1; reports/stage_e9_member_rulings.md).
1. For every record: recompute mean and daily t from the series in your own code; check one value per window date with
   zeros on no-trade days (the dates equal the window's trade dates; non-zero days at most the trading days). Compare with
   the record's screen (mean_ticks, t_daily, passes) to 1e-9 relative.
2. Check each tier in K8_research_cluster.json against D5, OC-H and the labels. The runner put K8-flight-01 HEOD MGC
   (mean +10.676 ticks/day, t 1.395, 55 trips) and K8-wkndbtc-01 MNQ (+28.975, t 1.072, 39 trips) in Tier A, and H30
   (t 0.976) and oilcad (t -5.907) in Tier B. Say for each Tier A trial how far its t is from 1.0 in the sense of the
   largest single day's contribution (the t with that day removed, reported as a sensitivity, not a ruling).
3. Rebuild the daily series of K8-flight-01 HEOD MGC, K8-wkndbtc-01 MNQ and K8-oilcad-01 6C from the runner's trip lists
   and the frozen cost table in YOUR own code, with no replay: each trip's net = gross - commission - slippage per side
   (slippage by the fill's 30-minute CT bucket, D8's event-window rule for fills in [release, release + 30 min) of a
   release concerning the root, the D9.7 exit's event-window cost as D9.7 states, rounding as the frozen table rules),
   summed per trade date, converted to net ticks per contract (MGC $1.00, MNQ $0.50, 6C $5.00 per tick; q_c 1), matched
   against the series and daily_net_usd day by day. Check each trip list's record_sha256 against its record file. (The
   prompt names "one port, one other member"; K8 has no port, so the lead names these three: both Tier A trials and the
   trial with event-window fills and MLL liquidations.) If gross cannot be checked without prices, say so.
4. Trade counts against the checked event tables and the rules:
   - wkndbtc: the 54 eligible research Mondays (Task 1b B), less the trial's window exclusions (roll blackout, UR-1,
     not every leg trades): every remaining Monday has one trip or an explanation from the record (G = 0 and missing
     bars cannot be checked without prices: list the unexplained Mondays); no trip on any other date; entry fill Sunday
     18:00 CT and exit fill Monday 14:59 CT or a documented deviation (the one price_limit_exit, the 2-minute trip);
     trips before and after the 24/7 change (2026-05-29 16:00 CT) counted separately.
   - flight: trips only on FLIGHT_DATES in the window, at most one per date; entry fills on the 5-minute grid 08:35..14:55
     CT, none at 13:00 CT on an FOMC date; H30 and HEOD have identical entry dates, minutes and sides (the same trigger
     rule); exits at T_e + 30 or 15:05 (H30) and 15:05 (HEOD), or a documented deviation.
   - oilcad: entry fills on the 5-minute grid 08:05..13:25 CT, none at a guarded minute of 6C (09:30 on a 10:30-ET WPSR
     date, 11:00 on a 12:00-ET WPSR date including 2026-05-28, 13:00 on an FOMC date); exits at T_e + 15 or a documented
     deviation; at most 17 entries a day and entries at least 20 minutes apart; classify the 8 fill_guard_deferral counts
     (exit fills deferred past a release, which the specs leave to the engine, versus entry fills deferred because the 6C
     bar at t was missing, the K8-L-08 edge, R-T3-8); explain the 3-minute trip.
5. Program N: the runner does not count N. Give the number of screened trials (records with status "run" and a screen),
   any refused or excluded, whether any record shows a trial the freeze does not declare, and N = 194 + screened (the
   lead's pre-declared rule, specs K8-L-16).
6. The MLL liquidations per trial (accounts_started - 1 and the mll_liquidation counter) and whether any tier could depend
   on them (oilcad's 2; a bound, not an estimate). Also report each record's fill_guard_deferral and price_limit_exit
   counters.

Grade each item VERIFIED, VERIFIED WITH NOTES or DISCREPANCY, and give the time you started and ended (PDT). Return to the
lead: the report path, a summary of at most 200 words (counts by verdict, each DISCREPANCY named), and anything unfinished.
If the harness refuses the write, return the full Part 2 text in your final message.

## Boundaries

Read-only except Part 2 of your report and your own scripts under reports/stage_e9_briefs/audit_k8/. Never re-run the
runner or any member on real bars; never open a bar file (data/processed*). Every check uses the runner's recorded outputs
and the frozen tables only. No repository copy; no git changes, no web, no workers.
