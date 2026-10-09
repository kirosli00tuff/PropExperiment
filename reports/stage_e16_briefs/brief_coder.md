# Task 3 brief: BaseRulesCoder-OpusXHigh (worker-xhigh, opus, in a git worktree). Read brief_common.md first.

You work in a git worktree of the repo at HEAD be01890. Files the lead wrote after HEAD are NOT in your worktree:
read them from the main tree by absolute path: /home/kiros-li/Documents/GitHub/PropExperiment/reports/stage_e16_briefs/
lead_spec.md (THE SPEC: implement exactly it), brief_common.md, and docs/prompts/STAGE_E.16.md (in your worktree
too). Do not commit; leave your changes in the worktree; the lead merges. Synthetic data only: your worktree has no
store (data/processed* are git-ignored) and you must not read any store in the main tree.

Objective: a new package base_rules/ (outside the harness directories) and its tests (tests/test_base_rules_*.py),
implementing the five test runners H1..H5 of lead_spec.md, the multi-day simulator, the statistics and the power
calculation, a run-once marker per test, and a runtime probe at full 2010-2024 scale. It must import and call frozen
modules unchanged (screening/stage_e_engine.py, screening/stage_e_frozen.py for D8 costs, data/stage_e_bars.py for
the E.12 step-2 confirmation stores, data/hist_store.py / data/hist_calendar.py / data/group_session.py for the
ext2010 stores and calendars, rules/products.py, screening/trial_registry.py, funnel/multiple_comparisons.py or
screening/stage_e_verdict.py for the DSR the program already uses). Never edit a frozen module; where frozen code reads
a 2019-on calendar, follow c1_replication/context.py's pattern (read c1_replication/README.md first: it is the
precedent for a test package outside the harness).

Modules (names are suggestions; keep files under 400 lines):
- constants.py: every parameter of lead_spec.md (windows per product including U2's starts: 24 products 2010-07-01,
  RTY 2017-06-01, TN 2016-01-04, HE 2017-07-03; the fallback 2019-05-06..2024-02-29; warm-ups 20 and 60; NW lags;
  year-stability thresholds 10 and H2's 6; Holm 0.05; the cost cases base / stress (+1 tick per side) / 1.5 x
  slippage; tenor map; vehicles per E.12/D2), and the input paths and pinned sha256s as parameters the freeze fills.
- inputs.py: loaders for reports/stage_e16_settlement.json (schema in brief_settlement.md; periods tile the window;
  refuse gaps, overlaps, grades below "secondary" for H1/H4 use) and for the EC-AUC rows (frozen
  reports/stage_e2b_release_calendar.json TREASURY_AUCTION rows from 2019-05 plus a 2010-2019 file of the same row
  format at a path parameter), with E.0's filter. The real files are being produced in parallel; build to the schema
  with synthetic fixtures.
- calendars.py: trade dates, early-halt/halt dates, unsourced dates and day-session open per product and date, from
  the frozen 2019-on group calendars and the hist2010 JSON calendars, plus a livestock 2010-2019 JSON at a path
  parameter (same format as data/calendars/hist2010/*.json); roll blackouts from the stores' roll metadata as
  data.stage_e_bars does (L-8).
- store.py: the 2010-2024 splice loader. Inputs: a run manifest (root -> ext2010 store path + sha256, E.12 step-2 store
  path + sha256), written by E.17. Reads only the columns and minutes the runners need, one product at a time.
  Guarantees: sha256 verified before any row is returned; holdout-2, embargo, research-window, MES and data/sealed
  paths refused; no trade date after 2024-02-29; a trade date present in both stores refused; store-boundary handling
  per lead_spec section 2; the raw symbol (contract) per bar and the splice instants exposed. Build it to the same
  layout as the real stores (read data/hist_store.py's and data/step2_store.py's writers and data/stage_e_bars.py's
  loader to learn the layout and metadata keys, by section) and test it on synthetic stores written in that layout
  (to a temporary directory on disk; pytest's tmp_path is fine for small ones).
- costs.py: per-fill cost in exact cents from screening.stage_e_frozen's ProductCosts (commission per side,
  side_slippage_ticks of the fill minute's bucket, slippage_cents ceil to the cent), the event-window rule and the
  D9.5a fill guard from release calendars, the three cost cases, and lead_spec section 1's conservative 2010-2019
  fallback for release types without 2010-2019 rows (write a small report function that lists, from the
  2019-05..2024-02 frozen release calendar alone, which release types ever touch an H fill minute).
- sim.py: the multi-day position simulator: fills at bar opens per the engine's clock, rolls at splices (lead_spec
  section 2), daily marks MK at the settlement-minute bar open, P&L in exact cents, per-fill costs.
- h1.py .. h5.py (or one runners.py if smaller): each produces the per-unit net series (base, stress, 1.5 x), the H5
  component daily series, exclusion counters by reason, per-product and per-year tables, and a CALENDAR-ONLY count
  mode (no bars: the candidate units per product and year that the calendars, windows and blackout estimate allow;
  used for the power table).
- stats.py: t, Newey-West p, the larger-p rule, Holm across the registered tests, year stability (thresholds per
  test; fewer than 3 qualifying years fails), DSR at N via the program's existing function, the cost-case tables.
- power.py: the power table of lead_spec section 5 by simulation (normal per-unit returns at the prior's net Sharpe,
  unit counts per year from the calendar-only counts, Holm thresholds 0.01 and 0.05, n >= 30, year stability) with the
  analytic one-sided t power beside it; priors: net Sharpe H1 0.3-0.8, H2 0.4-0.9, H3 0.3-0.7, H4 0.2-0.6,
  H5 0.8-1.5 (annual); full window and fallback window. Fixed seed. Expected exclusion rates where bars are needed:
  state your assumption (roll blackouts 3 dates per roll from each product's listed contract cycle in rules/products.py
  or the D-docs; early closes and halts from the calendars; missing bars 0 for liquid hours, stated).
- run.py + README.md: CLI for E.17 (one command per test), the run-once marker (written before any bar is read;
  refuses a second run), the registration check (screening.trial_registry: the test id must be registered), the
  freeze-manifest check (every input sha256 against reports/stage_e16_freeze.json, path a parameter), outputs to
  reports/stage_e17_runs/ (path a parameter). E.17 runs it; you never run it on real data.

Tests (tests/test_base_rules_*.py; pytest -q -p no:cacheprovider; synthetic only):
1. a hand-computed multi-day trade to the cent, including a roll across a splice and an overnight mark;
2. a single-day trade that matches the frozen engine fill for fill (run screening.stage_e_engine with StageERules and a
   trivial member on the same synthetic frame; prices, fill minutes and base-case costs identical);
3. causality for every signal (H1, H2, H4; H3 has none beyond the calendar) and for the risk scaling and H5's scaling:
   perturb every bar at or after a decision instant and assert the decision and sigma are unchanged;
4. a planted-edge synthetic world per runner that the runner detects (passes Holm at 0.05/5 with n >= 30) and a
   pure-noise world it rejects;
5. the splice loader on synthetic ext2010 + E.12 layout stores: boundary, double-date refusal, refusals of holdout,
   embargo, research, sealed paths and dates after 2024-02-29, sha256 mismatch refusal;
6. exclusion counters (blackout, early close, unsourced, missing bar, no reference, window end, store boundary,
   same-tenor overlap) on small hand-built calendars;
7. run-once and registration refusals.
Run your new tests and the existing engine/cost tests they touch; do not run the whole suite (30 minutes; the lead
runs it).

Runtime probe (after the tests pass): synthetic stores at full 2010-2024 scale (27 products, about 3,500 trade dates,
one-minute bars over each product's real session hours) written to /home/kiros-li/.cache/propexp_e16_probe/ (on disk;
NOT /tmp, a RAM tmpfs; NOT inside the repo), built and processed one product at a time if memory requires; check
`free -g` first and keep the peak under 70% of the available memory; nice -n 10; at most 7 threads. Run all five
runners end to end on them; report wall time per test and the peak RSS (/usr/bin/time -v). Delete the probe stores
afterwards. Write the probe result to reports/stage_e16_briefs/runtime_probe.md in the MAIN tree (absolute path).

Also produce, in the main tree: reports/stage_e16_briefs/power_table.json and .md (power.py's output at the priors,
full and fallback windows, with the calendar-only unit counts used), and reports/stage_e16_briefs/release_touch.md
(the release types that touch H fill minutes, from the frozen 2019-05..2024-02 calendar alone). The calendar-only
counts need the real settlement table and calendars; if reports/stage_e16_settlement.json or
reports/stage_e16_calendars/*.json are not in the main tree yet when you get there, use the lead's prior settlement
minutes and the frozen calendars, label the table "provisional", and say so in your return (the lead reruns it).

Boundaries: write only base_rules/, tests/test_base_rules_*.py (and fixtures under tests/), and the three main-tree
report files named above. No harness edit, no ledger write, no store read, no Databento. Other workers own the
settlement table, the overlap audit and the calendars. If the spec is ambiguous or a frozen module cannot be called
as the spec needs, choose the conservative option, write it into base_rules/README.md under "Coder choices", and
report it; do not change the spec.
