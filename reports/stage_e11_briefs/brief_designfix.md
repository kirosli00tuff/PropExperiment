# Brief: DesignFixCoder-OpusXHigh, the code side of the design-review rulings (Part 1)

You are DesignFixCoder-OpusXHigh in Stage E.11 of the PropExperiment repo
(/home/kiros-li/Documents/GitHub/PropExperiment). Read CLAUDE.md first (invariants, context hygiene,
compute limits). Synthetic data only. ml_route_v2/ is built. You apply the code side of the lead's
rulings on the design review.

Read: reports/stage_e11_rulings.md, Part 1 (the rulings table); the matching design text in
docs/STAGE_E_ML_V2_DESIGN.md (grep for "design review D-0"); reports/stage_e11_interfaces.md
sections 0 and 9; the code you change, by grep and line ranges.

## Changes (each with tests)
1. **D-01, ruin definition.** payout_sim: a path is ruined if the MLL is breached OR D at a close is
   <= KS2B_HALT_BELOW x MLL, within the horizon. It is evaluated with KS1, KS3 and KS4 off. KS2's
   half-size multiplier stays on: it is sizing, not a stop. Report both ruin (this definition) and
   breach_only in PayoutSummary. pipeline.py's verdict criterion 7 reads the new ruin. Tests:
   - a path that drifts to D < 0.25 MLL without breaching counts as ruined, not as breached;
   - a breach counts as both.
2. **D-03, daily risk budget.** The day starts with sigma_target^2. Each accepted trade consumes
   (n x sigma_ticks x tick_value)^2. A trade's n is the largest that fits the per-trade b (or the
   2b rounding band) and the remaining budget; no entry once the budget is spent. Apply it
   wherever sizing happens:
   - accept_trades (the fixed-D metric);
   - the engine PortfolioMember (per trade date, from the account view);
   - payout_sim re-sizing.
   Put the arithmetic in sizing.py once and reuse it. Tests: hand-computed budget consumption over
   a day of 4+ candidates; a day whose budget is spent refuses further entries.
3. **D-04, risk table per split.** sigma(p,h) and L(p,h) used to size trades inside the nested CPCV
   come from the split's training rows. Per outer split: its training blocks. Per inner fold: the
   inner training blocks. The final model and the research-window schedule use the table from all
   six blocks. The admissibility filter stays once on the whole window. Implement with a
   risk-table callback, so cpcv passes the split's training rows and score_split gets the matching
   table; keep the ScoreFn contract backward compatible. Test: a planted volatility spike inside an
   outer test block does not change the risk table used to score that block.
4. **D-05, cost-gate reading switch.**
   - constants.COST_GATE_READING = "net", with the comment "# V2.7: 'net' = literal F7
     (|r_hat| - c > k c); 'gross' = |r_hat| > k c; the user decides (V2.12 item 1)".
   - decide.cost_gate honours it.
   - Tests for both readings at the boundaries.
   - Default stays "net". Do not change tau or the Gate 0 constants.
5. **D-08a, cost beyond q_c.** Each contract beyond the vehicle's D2 q_c pays one extra tick per side.
   - Engine: PortfolioRules overrides fill_cost (and close_cost if the engine uses it for exits) to
     add (qty - q_c)^+ ticks x tick value per fill, on top of the parent's cost. This only adds
     cost. Take q_c from screening.stage_e_frozen's vehicle tables.
   - Fixed-D metric: per trade, cost per contract += 2 x (n - q_c)^+ / n ticks.
   - payout_sim re-sizing: the same per-contract adjustment. Add q_c to TradeRecord with a default,
     if needed.
   - Tests: a hand-computed fill above q_c costs exactly the extra ticks; at or below q_c it is
     unchanged. The engine-equivalence test (single product at size <= q_c) must still pass.
6. **D-08b, cost sensitivity.** selection_metric gets a slippage_multiple parameter (default 1.0)
   that scales the slippage part of the cost (cost minus commission/tick_value). The pipeline
   reports the nested OOS record's median-path t, Sharpe and daily mean at 1.5 x slippage beside
   1.0 x. Test: at multiple 1.0 it equals the current figure; higher multiples lower the P&L
   monotonically.
7. **D-21, the final configuration's own figures.** The pipeline report adds the final
   configuration's own CPCV OOS t and Sharpe, from its column of the path-averaged OOS matrix, beside
   the nested median-path t.

## Then
Run all ml_route_v2 tests: `nice -n 10 uv run pytest -q tests/test_ml_v2_*.py`, output to
reports/stage_e11_briefs/designfix_pytest.out, tail only. All pass. The only allowed xfail is
tests/test_ml_v2_leakage.py::test_gate0_c_binary_edge_ridge_predictions_are_rejected_at_every_k
(C-1, documented).

## Boundaries
- Edit only ml_route_v2/ files, tests/test_ml_v2_*.py and tests/ml_v2_fixtures.py.
- constants.py: additions only, with a V2.x comment; do not change existing values.
- Do not edit the design draft, the interfaces file or the review/rulings files.
- Never touch the harness directories (rules/, sim/, screening/, funnel/, data/, ml_route/,
  compute/, strategy/), data files, .env or result reports.
- No full suite, no agents, no commits, no network.

## Return
The files changed; the test result line; for each change, where it lives and its test names; any
ruling you could not implement as written, with why; a summary of at most 200 words.

## Added by the lead after FixCoder's return (04:50)
8. **Per-product engine blackout (V2.2).** The frozen StageERules carries one shared blackout set,
   so on any traded product's roll date the engine refuses entries in every product. v2's rule
   (V2.2) excludes only each product's own roll dates. PortfolioRules therefore checks the
   blackout per product: an entry in product P is refused only on P's own roll-blackout dates.
   This keeps the guard against a position spanning P's contract change. Implement it as the
   least-invasive override, documented in the module docstring like the existing one.
   Tests:
   - P's entry on P's roll date is refused;
   - P's entry on another product's roll date is accepted;
   - the single-product equivalence test with the frozen StageERules still passes (one product:
     identical sets).
9. **Engine path isolation default.** Make one process per engine path (isolate_paths) the
   default in the pipeline. Measured at size A: 56% combined vs 49% for one inline path, and five
   inline paths were never measured. Keep the inline option for tests.
