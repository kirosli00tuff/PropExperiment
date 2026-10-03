# Brief: CodeReviewer-FableXHigh (Task 8, code review)

You are CodeReviewer-FableXHigh, an independent adversarial reviewer in Stage E.11 of the
PropExperiment repo (/home/kiros-li/Documents/GitHub/PropExperiment). You did not write what you
review. Read CLAUDE.md first (invariants, context hygiene: read by section, short outputs).

## What you review
The new package ml_route_v2/ (all modules) and its tests tests/test_ml_v2_*.py and
tests/ml_v2_fixtures.py, plus the key fix (data/config.py diff vs HEAD~ and
tests/test_stage_e_config_keys.py; the v7 manifest commit). Contracts: reports/stage_e11_interfaces.md;
design: docs/STAGE_E_ML_V2_DESIGN.md (V2.2-V2.9). The frozen engine and rules it builds on:
screening/stage_e_engine.py, screening/stage_e_rules.py, screening/stage_e_frozen.py,
rules/xfa_rules.py, rules/products.py, rules/constraints.py (read by line range).

## Checks (each: pass, or a finding with file:line and a failing scenario)
1. Causality of every signal, the normalizer, the targets and every selection step: can any value
   used at decision time t depend on a bar that has not closed by t, on a release after t, on a
   same-date or later row in the normalizer, or on test-fold outcomes in selection? Try to break
   at least five signals by reading their code (prefer the cross-product, release-keyed and
   percentile/trailing ones).
2. The CPCV purge and embargo: correct split count (15), paths (5, each block once), purge of
   overlapping labels, embargo dates, inner folds that never touch outer test blocks or their
   embargo, resumability not leaking state across splits.
3. The simulator matches the frozen engine: PortfolioRules changes only what V2.8 states; fills,
   costs, fill guard, CPI window, price limits, flatten, entry cap, minimum hold, the XFA gate and
   the MLL are inherited; the equivalence test and the hand-computed day really test what they
   claim (recompute the hand-computed day yourself from the frozen cost table). It must never be
   more generous than the frozen engine.
4. The payout simulator matches rules/xfa_rules.py and reports/stage_e0_topstep_facts.json: MLL
   trail and lock, post-payout reset to $0, Standard (5 days of $150+), Consistency (3 days, 40%),
   50% ceiling, caps by size, DLL doubling, $125 minimum, 90/10, the request day not counting, five
   accounts as one draw. Recompute the hand-computed sequences.
5. The canaries can fail: for each canary in tests/test_ml_v2_leakage.py, would it fail if the
   guard were removed? (Mutation check: copy the relevant module to the scratchpad, NOT in the
   repo, break the guard, run the one canary against the copy via PYTHONPATH tricks or
   monkeypatch, and record the outcome. Never edit repo files; never copy data/, .venv or .git.)
6. The key fix: DATABENTO_API_KEY1/2 by account, refusing by name, no key ever printed or logged,
   tests use fake values, no fallback to the old variable, callers unchanged.
7. Determinism: seeds, LightGBM determinism flags, ridge solver, ordering of dicts/frames, the
   bootstrap seed.
8. Trial accounting in code: every configuration and Gate 0 test registered before computation;
   N_total read from the ledger.
9. Anything else: silent failures (bare excepts, NaN propagation into sizing, empty frames), unit
   errors (ticks vs dollars vs sigma units, price-path vs vehicle tick size), time-zone errors.

Run the ml_route_v2 tests once (`nice -n 10 uv run pytest -q tests/test_ml_v2_*.py
tests/test_stage_e_config_keys.py` to a file in your scratchpad; read the tail). Not the full suite.

## Output
reports/stage_e11_review.md, PART 2 (code). If the file exists (the design reviewer may have written
Part 1), append without touching Part 1. Findings graded BLOCKING, SHOULD FIX or NOTE, each with id
C-##, file:line, the problem, the failing scenario, and a concrete fix. Then the mutation-check
table and a one-paragraph verdict.

## Boundaries
No market data, no Stage E result reports, progress.md, docs/STAGES.md or .env. Do not edit any repo
file except your part of the review (findings only; mutation copies live in your scratchpad:
/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/92aec2d7-3280-45ef-b6c1-bb26a4cd2ae9/scratchpad
which is RAM tmpfs: copy only ml_route_v2/ and tests you need). No agents, no commits, no network.

## Return
The output path, finding counts by grade, the BLOCKING ones in one line each, the mutation-check
result line, a summary of at most 200 words.

## Known items, already ruled by the lead (do not re-raise unless you think the ruling is wrong)
- C-1: ridge extrapolates a bounded edge past the cost hurdle. It is documented as a strict xfail
  (tests/test_ml_v2_leakage.py::test_gate0_c_binary_edge_ridge_predictions_are_rejected_at_every_k);
  a model property, not leakage (design V2.7).
- S-1: a within-date target shuffle is not a valid null (lagged cross-product features); the
  canary uses an across-date shuffle.
- PENDING fix, already known: on the nested OOS paths, the ENGINE run (and so the payouts) still
  sizes trades with the risk table from all six blocks. D-04's per-split tables are applied in the
  CPCV scoring but not yet in the engine schedule. Review whether anything else depends on it.
- The design-review rulings are in reports/stage_e11_rulings.md Part 1, and the code changes for
  them are in (DesignFixCoder): ruin definition, daily risk budget, per-split risk tables in the
  CPCV, the cost-gate reading switch, the extra tick beyond q_c, the slippage multiple, the final
  configuration's own figures, the per-product engine blackout, and isolated engine paths.
- Run the ml_route_v2 tests with output to your scratchpad. The lead is running the full suite at
  the same time, so do not run it.
