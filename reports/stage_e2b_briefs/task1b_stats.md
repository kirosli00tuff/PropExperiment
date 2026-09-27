# Brief: ScreenStatsCoder-OpusXHigh (Stage E.2b Task 1, statistics; worker-xhigh on opus)

Objective: build and test the D4 power check, the D5 screen with the Tier A/B assignment, and the D4 start rule, as pure
functions the Stage E runner calls, so these are always computed by code and never by hand.

## Read first (by section)
- reports/stage_e2b_briefs/00_common.md (binding).
- docs/STAGE_E_DESIGN.md (FROZEN): D3 (epsilon and its units), D4 (the power check per member; the start rule;
  "inconclusive by design"), D5 (the tiers, the screen, Holm alpha_k = 0.05 / K). docs/NULL_CRITERIA_E.md.
- The D.1e Task 3 power method this generalizes: strategy/research/_d1e_power.py, _d1e_power_stats.py,
  _d1e_power_report.py, reports/stage_d1e_power.json (read by section). The D.1f start rule:
  strategy/research/_d1f_start_rule.py and reports/stage_d1f_step5_start_rule.json. docs/NULL_CRITERIA.md 4.1 (read-only).
- reports/stage_e2a_epsilon.json and reports/stage_e2a_epsilon_declaration.md + addendum (units of eps_X: net ticks per
  contract per day; translated and operative values). Read only; never edit.

## Build: screening/stage_e_stats.py (you may split into a few modules under screening/)
1. The power check at eps_X: n_b from the member's research-window daily series, analytic, and the block-bootstrap
   simulation where the two differ by more than 15% (the larger governs); a member whose n_b exceeds the days its window
   supplies is labelled "inconclusive by design". Fixed seeds as module constants. Units consistent with epsilon's
   (convert explicitly; test the conversion).
2. The D5 screen: research-window mean net P&L > 0 and daily t >= 1.0 (per micro or per contract, zeros on no-trade
   days); Tier A = passes, Tier B = every other member; members labelled by the coverage or trade-rate checks stay in the
   record with their labels (ask the lead if D5 or D9 says how a labelled member is tiered; do not guess).
3. The Holm machinery for a cluster's Tier A at alpha_k = 0.05 / K (K = the number of clusters with a non-empty Tier A),
   as a function for the confirmation sessions (K passed as the count, validated 1..8).
4. The D4 start rule generalized: V_ref,X = the median of the 14 monthly medians (2025-04..2026-05) of the day-session
   one-minute volume of the vehicle's bars present; S_X = the first trade date of the earliest month M* from which every
   month through 2024-02 has median day-session one-minute volume >= 0.25 V_ref,X; 0.15 and 0.40 descriptive; earliest
   possible S_X is the first trade date with bars on or after 2019-05-06. Input: monthly medians (computed elsewhere);
   the function reads no bars.
Within your first 30 minutes, write the public signatures (dataclasses and functions, with units) into the module
docstring and into the top of your report file (create it early); the lead reads that file and relays the signatures to
RunnerCoder, who calls them.

## Tests
tests/test_stage_e_stats.py (and more if needed): known answers (hand-computable series; the D.1e figures in
reports/stage_d1e_power.json reproduced by the generalized code for MES at MES's epsilon; the D.1f start rule result in
reports/stage_d1f_step5_start_rule.json reproduced from its recorded monthly medians, if recorded there; the 15% switch;
the inconclusive label; the t >= 1.0 boundary; zeros on no-trade days; Holm on a textbook example).

## Ownership
You own screening/stage_e_stats.py (and any screening/stage_e_stats_*.py) and their tests. Do not edit anything else.

## Report
reports/stage_e2b_task1_stats_worker.md.
