# Stage E.11 rulings: the lead on every review finding

Lead: Opus 5.5 (xhigh). The findings are in reports/stage_e11_review.md: Part 1 is the design
review (DesignReviewer-FableMax), Part 2 the code review (CodeReviewer-FableXHigh). Each ruling says
accept or reject, the fix, and where the fix lives. "Design" means docs/STAGE_E_ML_V2_DESIGN.md;
"code" means ml_route_v2/ and its tests.

## Part 1: design review (ruled 2026-10-03, about 04:20 PDT)

| Id | Grade | Ruling | Fix and where |
|---|---|---|---|
| D-01 | BLOCKING | Accept. Under D-proportional sizing, a breach is structurally rare, so "ruin = MLL breached" is near-vacuous | Ruin for verdict criterion 7 = the MLL breached, OR D <= 0.25 x MLL (the KS2b level) at any close within 252 dates, read with KS1, KS3 and KS4 off. The plain breach probability is reported beside it. The analytic figures (fixed size 0.235/0.139/0.078; a trailing-phase breach before lock 0.39/0.29/0.20; reaching D < 0.25 MLL under D-sizing 0.70/0.29/0.12 at S 1.0/1.5/2.0) go into V2.0. Code: payout_sim ruin output |
| D-02 | BLOCKING | Accept option (a) | The research-window test is a screen only (no Holm claim). The confirmatory control is the DSR at N_total on the nested OOS record plus the registered holdout-2 read. The route's slot in V21's K = 10 is unused on the research window (a DECISIONS entry for the freeze session). Option (b), t >= 2.58 at 0.05/10 with power 0.17 at S = 1.5, goes in V2.12. Design only |
| D-03 | SHOULD FIX | Accept the daily risk budget | Each accepted trade consumes (n x sigma$)^2 of sigma_target^2. A trade's n is the largest that fits both b (or the band) and the day's remaining budget; no entry once the budget is spent. Daily sigma <= sigma_target by construction (independent trades). Code: sizing, portfolio, simulate member, payout_sim re-sizing |
| D-04 | SHOULD FIX | Accept | The risk table (sigma(p,h), L(p,h)) is recomputed per outer split from its training blocks and per inner fold from its inner training blocks. The frozen table comes from all six blocks. The admissibility filter stays once on the whole window (ruled). Code: cpcv / selection_metric / pipeline |
| D-05 | SHOULD FIX | Accept | Items 1, 7 and 10 are merged into one coupled decision, with both consistent sets written out (literal: hurdles 2.5c/3c/4c, tau 0.10; gross: 1.5c/2c/3c, tau 0.167, Gate 0 at the loosest hurdle). Code keeps the literal reading as the default, with a constant switch (COST_GATE_READING) so the freeze flips it in one line. Lead recommendation: the gross reading, for the reviewer's reasons |
| D-06 | SHOULD FIX | Accept | The price path is fixed once, before Gate 0: the full-size contract for every exposure (the table, v1 ML-A07). The owned NG store is NG itself (full-size), so it is free. The owned MCL, MGC and MHG micro stores are not price paths. Gate 0 runs once, on phase 1. Phase-2 products are c/sigma-filtered, not audited, and N adds the phase-1 Gate 0 tests only. Design only |
| D-07 | SHOULD FIX | Accept | V2.9 states: the selection score is the mean of the per-fold (per-split) daily Sharpes; a configuration is eligible only with >= 30 trades and a finite score on every fold, and on every one of the 15 outer splits for the final model; no eligible configuration = no model = fail. "Every split versus a majority" goes in V2.12. Design only (code already does this) |
| D-08 | SHOULD FIX | Accept both | (a) Contracts beyond D2's q_c pay one extra tick per side: D8's "one extra tick for the part beyond the top level", with the top level taken as q_c, which is conservative. Code: PortfolioRules.fill_cost override (the engine), the fixed-D metric and payout_sim re-sizing. (b) The nested OOS record is re-priced at 1.5 x slippage and reported beside every criterion (D8's early-era re-check); the registration decides whether a pass must survive it. Code: selection_metric slippage multiple, pipeline report |
| D-09 | SHOULD FIX | Accept | A power paragraph goes into V2.9. Criterion 5 (S >= 1.5) is dropped as a gate, being redundant with t >= 3 apart from 1.37 -> 1.50 and turning the lower band edge into a coin flip; it is reported beside the gates instead. V2.0 adds F1's "near 3.5" with the reconciliation (sigma free at 10% ruin vs sigma fixed at 0.10 x D). V2.12 lists keeping it as a gate as the alternative |
| D-10 | NOTE | Accept | The 150K figures are labelled a lower bound on income, with a different trade set for ruin (V2.9, V2.12 item 12) |
| D-11 | NOTE | Accept | The compliance reading and the alternative (no new entry with a fill in [release - 5, release + 30) when open lot-equivalents exceed half the tier) go in V2.12 item 11 |
| D-12 | NOTE | Accept | The stale V2.6 text is fixed: 154 columns; the LightGBM literals are new, not v1's; depth 3 is near-degenerate at phase-1 scale (min_data_in_leaf 2000) |
| D-13 | NOTE | Accept | V2.9's partition is labelled a change (all six blocks, 15 splits); the block-cut rule is kept |
| D-14 | NOTE | Accept | (a) The operative Gate 0 bar is about z 3.57 with family A in the Holm family (3.24 without), stated. (b) The pre-cost alternative (no cost multiple; bars 2-4 only), under which the prompt's canary sentence holds literally, is added to the coupled Gate 0 decision |
| D-15 | NOTE | Accept | The reason for the 4.0 alarm is stated: above F1's 3.5 (the HFT figure) and the band's 2.5 ceiling |
| D-16 | NOTE | Accept | The V2.12 gaps are added (t >= 1.645 alternative, paper-trading 1.25 x D8, the generic list, the warm-up rule as its own item), plus a "lead decisions, not open" list |
| D-17 | NOTE | Accept | The 2010 extension runs per path in separate processes, or in date chunks, for memory (V2.11) |
| D-18 | NOTE | Accept | The D1 ADV census and (if chosen) E|m_1| are added to V2.4's list of research-window-derived constants |
| D-19 | NOTE | Accept | V2.2 states that the clock uses O_X and F_X only and deliberately ignores C_X; some decisions and exits fall after settlement |
| D-20 | NOTE | Accept | (a) N_program is read from the ledger at the freeze. (b) v2 adds 45 + \|A\| + \|B\| to the program's N, plus 1 for the research-window test as a tested rule (v1 M6 logic) |
| D-21 | NOTE | Accept | Beside criterion 2, the final configuration's own CPCV OOS t and Sharpe (its PBO-matrix column) are reported. Code: pipeline report |
| D-22 | NOTE | Accept | One sentence on the two directions of bias in the DSR variance |
| D-23 | NOTE | Accept | $4,019 -> $4,018 |
| D-24 | NOTE | Accept | The power of research-window-only warm-up (0.58 to 0.66 at S = 1.5) is added to the warm-up item |

## Part 2: code review (ruled 2026-10-03, about 05:55 PDT)

Review result: 0 BLOCKING, 2 SHOULD FIX, 10 NOTE. Its test run read 717 passed and 1 xfailed (C-1).
Mutation checks: 9 of 9 guard removals made their canary fail; the unmutated control passed 11 of
11.

| Id | Grade | Ruling | Fix and where |
|---|---|---|---|
| C-01 | SHOULD FIX | Accept | Resumable state carries a constants fingerprint (sha256 of ml_route_v2/constants.py): in the CPCV unit key extra, Gate 0 B state, every stage pkl (refused on mismatch), the engine path and payout fingerprints. Partial keywords are hashed in _callable_name. Test: flip COST_GATE_READING with monkeypatch -> mismatch error. Code (ReviewFixCoder) |
| C-02 | SHOULD FIX | Accept | A candidate whose pair has NaN sigma or loss in the split's risk table is skipped with reason risk_unknown and counted; the raise is kept only for a pair absent from the table. Test with a vehicle planted in two blocks. Code |
| C-03 | NOTE | Accept | An empty-schedule path emits a payouts row with n_trips 0, NaN figures and empty_schedule True. Code |
| C-04 | NOTE (the known pending item) | Accept | Per-split sigma and loss are attached to each split's candidates in _nested_schedule; join_risk prefers row-level values; PortfolioMember and _pack follow. Every engine and payout figure then uses the training-block table of the split that produced the trade (D-04 complete). Code |
| C-05 | NOTE | Accept | Rows whose fill minute has no calibrated cost bucket are counted per (root, horizon) in Panel.counts. Code |
| C-06 | NOTE | Accept | decide._exit_ts treats exit_ts <= 0 as missing. Code |
| C-07 | NOTE | Accept | The ridge fit runs under one BLAS thread (threadpoolctl if available, else documented and recorded in the unit record). Code |
| C-08 | NOTE | Accept | Design rule (V2.9): N accumulates across runs on real data. Every real-data run under a different configuration set or reading adds its configurations and Gate 0 tests again. Synthetic runs add nothing. The freeze session passes N_program explicitly. Design text |
| C-09 | NOTE | Accept | payout_sim reads the scaling tier from the balance at the prior session's close, before that date's payout debit (V2.8). Code |
| C-10 | NOTE | Accept, deferred | (a) docs/ACCESS.md:9 still names DATABENTO_API_KEY. (b) data/config.py returns the raw value rather than key.strip(). Both are outside this stage's two allowed commits, and (b) is a frozen harness file (a v8 manifest). The next purchasing session fixes both when it writes its manifest. Listed in the return's section 7 |
| C-11 | NOTE | Accept | The engine record and the combined-MLL audit are labelled "kill switches off" in the pipeline report and docstrings. Code (labels) |
| C-12 | NOTE | Accept | The normalizer's rolling variance uses a shifted origin per root (the root's first finite value, a past constant). Same z values to rounding; no scale dependence. Code |
