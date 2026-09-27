# Brief: RunnerCoder-OpusXHigh (Stage E.2b Task 1, runner core; worker-xhigh on opus)

Objective: build and test the generalized Stage E screening runner and cross-product alignment (design D11.5, D11.6),
with the E.2a carried items, the member template and the per-cluster code-freeze helper, and prove it reproduces D.1's
MES screening output bit for bit.

## Read first (by section)
- reports/stage_e2b_briefs/00_common.md (binding).
- docs/STAGE_E_DESIGN.md (FROZEN): D4 (windows, holdouts, cross-product windows), D6 (the session table: O, C, F per
  product), D8 (costs and the event window), D9 (the constraint set, the member-level coverage check, the trade-rate
  floor), D11 items 4 to 6 and 9. docs/NULL_CRITERIA_E.md (what the outputs must support). docs/SCREENING.md.
- reports/E.2a_RETURN.md sections 2 (the MBT holdout-1 rows paragraph), 3.3 to 3.9, 5 (rulings T12-1..T12-4), 6 (L-1..L-13,
  R-F1, R-F3, R-F4) and 7.
- Code: screening/runner.py (screen_candidate at line 431, screen_frame at 347; D.1f-frozen, do not edit), sim/engine.py,
  sim/fill_model.py, sim/costs.py, strategy/interface.py, the E.2a modules rules/products.py, rules/constraints.py,
  rules/sessions.py, rules/price_limits.py, data/calendars/, data/group_session.py, data/build_bars.py (its parquet schema
  and metadata), sim/product_costs.py, screening/vehicles.py, tests/test_screening_runner.py,
  tests/test_d1f_runner_hardening.py, tests/test_leakage_canaries.py.

## Build (new files; suggested names, keep them in screening/, data/ and strategy/stage_e/)
1. Frozen inputs: a loader that takes a product's rules (rules/products.py), calendar (data/calendars/), cost table
   (reports/stage_e2a_costs.json), vehicle (reports/stage_e2a_vehicles.json), q_c (reports/stage_e2a_vehicle_sizes.json)
   and epsilon (reports/stage_e2a_epsilon.json) from the frozen files only, and refuses unless each E.2a table's sha256
   equals its recorded value (full hashes: costs f4360bb77272d0335485a9e01c0f6fc6ab99c47d52e640d95f9cd0397296df14,
   sizes 280d7e9df1953069448ca1762588477146a5d3c35bc53d3e9e2df50272c47325,
   vehicles 1f1cafee4330961799f33d5493e640897cfa79827be98597dbaba23292e29913,
   epsilon 4e2c773182a23e7d073305ca4eb0134d3b3ac554ccc8215730bc1e194eaff496). The public entry takes the cluster, the member
   label, the member factory, the legs and a named frozen window, and nothing that could vary a rule, cost, epsilon,
   calendar, tick or q_c.
2. Stage E bar loader with trade-date refusals: refuses (by CME trade date from the product's group calendar, not by
   timestamp) any row booked to holdout-1 (trade date >= 2026-06-22), holdout-2 (2024-04-01..2025-03-31) or the March 2024
   embargo; in particular MBT's 1,617 bars booked to trade date 2026-06-22 (ruling L-9). A synthetic test plants MBT rows
   booked to 2026-06-22 and proves the loader refuses them (the lead's Task 9 DECISIONS entry cites this test; name it
   clearly). The confirmation-window path (S_X..2024-02-29) reads the step 2 store that PurchaseCoder2 is building in
   parallel (same parquet schema as data/build_bars.py's research parquets; the lead will relay its path layout); build
   the interface, test it on synthetic files, and refuse cleanly when the store is absent.
3. Cross-product alignment (D11.5): a shared UTC minute grid; no forward fill into a signal; a member whose leg has no
   bar at a decision time does not trade. Cross-product window rules of D4 (intersection of the legs' windows, the union
   of the legs' roll-blackout dates excluded, every leg passes the coverage check).
4. The member-level coverage check (at least 0.95 in the member's own window, D9) and the trade-rate floor (at most 20
   entries a day, a 2-minute minimum hold, a 10-minute mean hold), applied before any member result is written. A failing
   member is labelled, not dropped.
5. The E.2a carried items: roll blackouts from each product's group calendar (L-8); vendor-unit ticks for cent-quoted grains
   and livestock (ZC, ZW, ZS, ZL, HE, LE: vendor tick = 100 x the E.0 tick); the flatten rules of rules/sessions.py (R-F1,
   R-F4); the event-window cost under D8's literal text, using the largest s_b and not max(s_b + depth) (T12-4); the MBT
   refusal (item 2); and a check of 2026-06-18/19 for an unseen roll (a roll after 2026-06-20 is invisible to research-window
   symbology). For the roll check, use calendars and symbology/roll metadata (data/vendor roll caches, the E.2a reports),
   never prices; if it cannot be decided without new data, make the runner exclude or refuse those dates by a named rule
   and record the question.
6. The generalized screen: produce each member's research-window daily net series (per micro or per contract, zeros on
   no-trade days, the units D5 names) and a member result record. The D4 power check and the D5 screen with the Tier A/B
   assignment are written by ScreenStatsCoder-OpusXHigh in screening/stage_e_stats.py in parallel; the lead will relay its
   function signatures. Your runner calls them so that the runner, never a person, computes them. If they are not ready
   when your core is done, report and the lead will route the wiring.
7. The member template strategy/stage_e/_template.py (with strategy/stage_e/__init__.py) and a per-cluster code-freeze
   helper that hashes a cluster's member modules into a cluster freeze file before its screening session runs any of
   them; the runner refuses a member whose module is not in the cluster's freeze or differs from it.
8. Entry-point discipline: the public cluster screening entry calls screening.harness_freeze.preflight() first (see
   00_common.md). Accept the data root and the output directory as explicit arguments (never assume REPO_ROOT/data), so
   the Windows backend (Task 5) can run the same entry on another machine.
9. MES regressions: the generalized runner reproduces D.1's screening output for three MES trials (one from class C1, one
   C2, one C4; classes as in reports/stage_d1f_confirmation_list.md, read-only) bit for bit on MES's own research bars.
   Compare with D.1's recorded output (find it in reports/, e.g. stage_d1*_accounting.json, stage_d1f_tier_*.json) AND with
   the unchanged screening/runner.py screen_candidate. Run these through the heavy.sh gate (at most 6 threads).

## Tests
New test files (e.g. tests/test_stage_e_runner.py, tests/test_stage_e_alignment.py, tests/test_stage_e_loader.py,
tests/test_stage_e_mes_regression.py): known answers on synthetic products of several groups, including cross-product.
Every existing runner and canary test passes unchanged: tests/test_screening_runner.py, tests/test_d1f_runner_hardening.py,
tests/test_leakage_canaries.py (run them).

## Ownership
You own: the new files above (screening/stage_e_*.py or names you choose, excluding screening/stage_e_stats.py),
strategy/stage_e/, your new tests. Others own: screening/stage_e_stats.py and its tests (ScreenStatsCoder), the ML route
package and pyproject.toml/uv.lock (MLPipelineCoder), data/pull_*.py, data/config.py, data/holdout.py and the step 2 store
builder (PurchaseCoder2), compute/ (the lead and the Windows backend worker), screening/harness_freeze.py (lead).
Canaries through your runner are Task 3's (CanaryCoder, later); keep the runner's interface documented in module
docstrings so CanaryCoder can use it.

## Report
reports/stage_e2b_task1_runner_worker.md (see 00_common.md). Include the public interface (signatures) at the top, the MES
regression table (trial, recorded value, new-path value, equal), and every question for the user.
