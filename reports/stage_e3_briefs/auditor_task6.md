# Brief: MemberAuditor-FableXHigh, part 2 (Stage E.3, Task 6: recomputation)

You are resumed with this small brief. The objective is one: independently recompute the screen figures
of K2's research-window run and check each tier against the frozen D5. You wrote none of the runner
or member code, and you did not run the screen.

## Inputs

- The runner's outputs: reports/stage_e3_k2_screen/ holds one JSON record per member,
  K2_<label>_research.json (series.dates, series.values in net ticks per contract per day,
  series.n_trips, screen, power, labels, trade_rate, daily_net_usd, engine counters), plus
  K2_research_cluster.json (tiers, not_tiered, refused_members). Read them with short scripts that
  print only the fields you need. Never print a whole series.
- The frozen D5: docs/STAGE_E_DESIGN.md lines 298-345. The screen is research-window mean net P&L > 0
  and daily t >= 1.0, with zeros on no-trade days, t = mean / (population sd / sqrt(n))
  (screening/stage_e_stats.py lines 20-30, 141-170). Read the tier rules in stage_e_stats.assign_tiers
  (lines 241 onward) to learn how labels and exclusions enter, but compute in your own code.
- The frozen cost table and vehicles: reports/stage_e2a_costs.json and
  reports/stage_e2a_vehicles.json, read through screening.stage_e_frozen (costs[root].bucket_at,
  side_slippage_ticks, commission_side_cents, slippage_cents) or directly. The release calendar is
  reports/stage_e2b_release_calendar.json (for the event-window cost, D8).
- The Task 5 crash and the rerun: reports/stage_e3_STATE.md (C-1, R-T5-1).

## What to produce (Part 2 of reports/stage_e3_member_audit.md, under its existing heading)

1. For every one of the 44 records: recompute mean and daily t from series.values in your own code. Check
   that the series has one value per window date with zeros on no-trade days: the dates equal the window's
   trade dates, and the count of non-zero days is at most n_trips. Compare with the record's screen
   (mean_ticks, t_daily, passes) to 1e-9 relative. Verdict per record: VERIFIED, VERIFIED WITH NOTES or
   DISCREPANCY.
2. Check each tier assignment in K2_research_cluster.json against D5 and the labels. Tier A = passes the
   screen, not excluded; Tier B = every other screened member; excluded = coverage below 0.95. Check how
   a floor label (mean_holding_below_10min, entries_above_20_per_day, hold_below_2min) enters under the
   frozen rules. Verdict per member.
3. For two members, K2-cp1-01 ZN (a port) and K2-aucpost-01 ZN (an event member): rebuild the daily series
   from the trip list and the cost table. The runner's records carry NO trip list (lead ruling R-T6-1,
   reports/stage_e3_STATE.md). For these two trials only, replay the frozen engine in memory through the
   runner's own functions: load the cluster freeze (screening.stage_e_freeze.load_cluster_freeze("K2")),
   resolve the member, load bars with the runner's own loader, build the member window, call the
   runner's _run_member and extract_trips, all as screen_member does. Call
   screening.harness_freeze.preflight(<harness sha256>) first. Use a fresh PYTHONPYCACHEPREFIX outside
   the repository and nice -n 10. Never open a bar file yourself, and never write into
   reports/stage_e3_k2_screen/. First show that the replayed daily series equals the recorded
   series.values exactly (a determinism check). If it does not, stop and report DISCREPANCY. Write each
   trip list (entry and exit fill times in CT, sides, prices, quantities, per-trip gross and net) to
   reports/stage_e3_briefs/audit/trips_<member>.json. Then rebuild each day's net ticks per contract
   from the trips and the frozen cost table in YOUR own code (not the runner's cost functions):
   commission per side, slippage per side by the fill's 30-minute CT bucket, the event-window rule for
   fills in [release, release + 30 min) of a release concerning the product, and ceil-to-cent
   rounding. Match every day to 1e-9. Verdict per member. The replay is a replication for verification:
   the recorded run stays the only result.
4. Check the trade counts against the specs' expectations where they are fixed by the calendar. For the
   event members: trades should be at most the research-window event counts (2Y 13, 5Y 15, 10Y 15,
   30Y 15, FOMC 10, ISM 15; month-end 28 before exclusions), less excluded dates. Explain every shortfall
   you can: roll blackout, early halt, missing bar, UR-1, engine refusal. List each unexplained one.
   Also check that every trip's entry and exit fill minutes match the rule's fill minutes (your notes in
   section 8), or a documented deviation (D9.5a guard, missing bar, F).
5. Report the program N the records imply: the runner does not count N. Give the number of screened
   trials in this run (records with status "run" that were screened), the count of any refused, and N =
   58 + screened. Also say whether any record shows a trial the freeze does not declare.

Grade each item VERIFIED, VERIFIED WITH NOTES or DISCREPANCY, and give the time you started and ended (PDT).
Return to the lead: the report path, a summary of at most 200 words (counts by verdict, each DISCREPANCY
named), and anything unfinished.

## Boundaries

Read-only except Part 2 of your report and your own scripts and trip files under reports/stage_e3_briefs/audit/.
Never re-run the runner or any member on real bars, except item 3's replay of the two named trials
through the runner's own functions. Never open a bar file directly (data/processed*). Every other check
uses the runner's recorded outputs and the frozen tables only. No git changes, no web, no workers.
