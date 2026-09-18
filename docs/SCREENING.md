# Screening a hypothesis: use the shared runner

Stage D.1a (2026-09-18). This page is the whole contract for any hypothesis-screening session, whether a D.1-style literature round or data-native exploration. A prompt can say **"use the shared screening runner (docs/SCREENING.md)"** and nothing more about engine configuration, roll blackout, drift, or fill model.

## The call

```python
from screening import screen_candidate, fold_train_window, train_union_window

report = screen_candidate("F-H1 short label", lambda: MyStrategy(param=...), fold_train_window(0))
report.verdict   # "pass" only if BOTH benchmarks clear
report.reasons   # why not, one line per failed check
report.caveats   # carry these into any write-up of the result
report.to_dict() # JSON-able, for the session's report file
```

- **Strategy:** implement `strategy.interface.Strategy` (`on_bar(bar, account)`). Pass a zero-argument *factory*, not an instance, so every screen starts from fresh state.
- **Window:** `fold_train_window(i)` (i = 0..7, 142 train dates each) or `train_union_window()` (289 dates, the Stage D.1 accounting window). Any date outside the folds' train windows is refused. Test dates are for out-of-sample evaluation, not screening. The sealed holdout is unreachable from here.

## What the runner fixes for you

| Concern | What the runner does | Where |
|---|---|---|
| Engine configuration | One `EngineConfig`: restart on terminal, XFA phase, mean slippage, hindsight fields masked | `screening.runner.canonical_engine_config` |
| Roll blackout | The splice trade date plus the 2 sessions before it, from the vendor roll schedule. `EngineConfig` now *requires* `roll_blackout`, so omitting it is a `TypeError`, not a silently different result | same |
| Bars | Research slice only, restricted to the window's train dates | `screen_candidate` |
| Fill model | Market orders (`market_intent`) and resting limit orders (`limit_intent`) both go through the same engine. The passive-fill caveats are attached whenever a passive fill happened | `sim/fill_model.py` |
| Measurement | p / R / T from the ledger (`screening.trips.measure`); T snapped to the gate's grid {1, 2, 4}, with the snap flagged | `screening/trips.py` |
| Benchmark 1: zero-edge null | `funnel.power_gate.screen(..., robust=True)` on measured p/R/T, standard path. Unchanged from Stage B | `funnel/power_gate.py` |
| Benchmark 2: drift | Recomputed on the window's own bars. (a) The daily excess over the candidate's unconditional counterpart must be positive at one-sided 95%. (b) Drift-adjusted p/R must still pass the robust gate | `screening/drift.py` |

## Passive (limit) orders

`limit_intent(bar, side, qty, limit_price, ttl_bars)` builds a resting limit order.

**How it rests:**
- It rests from the next bar.
- It must be non-marketable against the decision bar's close. A buy must sit below the close, a sell above it.

**How it fills:**
- It fills only when a later bar trades **at least one tick through** its price, and then at exactly that price.
- A fill pays commission only; there is no slippage.
- No adverse-selection penalty is added. The trade-through rule is the adverse-selection model, and it biases results *pessimistically*, because the touch-and-bounce fills it drops are the ones that tend to win.

**When it is cancelled:**
- It expires `ttl_bars` minutes after the decision.
- A session change or forced flatten cancels it.
- Once the no-new-positions window opens, it is cancelled if it would add exposure.

**What it does NOT model**, and every result that used it must say so:
- queue position;
- the order's own effect on the market's path;
- volume available at the level;
- latency.

The full list is `sim.fill_model.PASSIVE_FILL_CAVEATS`, which the runner attaches to the report automatically.

## Reading the drift benchmark

- `drift.drift_share_of_gross` is the fraction of the candidate's gross P&L that its unconditional counterpart (same clock exposure, same size and sign, no conditioning) would have earned on average over the window. About 1.0 means the P&L *is* the window's drift.
- `session_benchmark` is the literal "1 micro long through RTH every day" figure, with its short mirror, for context. The verdict uses the exposure-matched form: it charges ETH exposure ETH drift, and it charges shorts negative drift, so a short-only candidate is not exempt in a falling window.
- **By construction, a purely clock-based unconditional hypothesis cannot clear this check in-sample.** A seasonality claim needs out-of-sample evidence, not an in-sample screen.

## Rules that still apply

1. **Every call is a trial.** Log every screen you run, including failures, and carry the trial count forward. Stage D.1 logged N = 23. The next round's multiple-comparisons accounting (`funnel/multiple_comparisons.py`) starts from 23 plus that round's own trials.
2. **Do not build `EngineConfig` or call `sim.engine.run_backtest` directly for screening.** `screening.runner.screen_frame` exists only for synthetic known-answer tests; it skips the train-date check.
3. **Run the canaries after any harness change:** `uv run pytest tests/test_leakage_canaries.py`.
4. **Costs are a lower bound.** The slippage table rests on two days of book data, both inside the sealed holdout, and excludes latency, adverse selection and queue position. Commission ($1.22/round turn) still needs checkout confirmation. A strategy that only works at modelled cost does not work.
5. **Known gaps, not fixed by this runner:**
   - the gate's T grid is {1, 2, 4} only;
   - no position can cross a trade date (the XFA flatten);
   - there is no order-book data outside the holdout and no second instrument.
