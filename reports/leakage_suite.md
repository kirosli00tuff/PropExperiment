# Leakage suite: planted-future canaries (Stage C, Task 4)

Generated 2026-09-17T14:50:15.183426+00:00 · `uv run python -m sim.leakage_canaries` · tests: `tests/test_leakage_canaries.py` · machine-readable: `reports/leakage_suite.json`

## Verdict: PASS

On a planted copy of real research bars, the real engine shows **no exploitable performance** from the planted future: -0.19 ticks per canary trade (z = -0.71, direction hit rate 0.515, 1,210 trades) against a planted jump of 16 ticks.

That result means something only because the same canary **catches known leaks**. Both deliberately broken engines capture the jump: same-bar fill 15.63 ticks (z = 53.65), peek-next-bar 15.63 ticks (z = 53.65). The latency control shows the real engine is not passing just by being slow: it captures 15.63 ticks (z = 53.65) when the marker is legitimately available one bar before the jump.

The literal check from the Stage B-C prompt (random baseline on planted data) also passes (0.00 ticks per round trip, z = 0.00). It is not evidence of point-in-time discipline, though. The same random baseline on the LEAKY same-bar-fill engine also shows nothing (0.29 ticks, z = 0.50), because a coin flip never reads the marker. The canary reader and the mutants carry the proof.

The structural checks all pass. The engine pulls exactly N+1 bars before it asks the strategy about bar N (a look-ahead buffer is caught in `tests/test_leakage_canaries.py`). Strategies receive only frozen primitive objects. Backdated intents are refused and never filled. The hindsight flag `vendor_degraded_day` never changes a trade.

### Real research bars, trade dates 2025-10-01..2025-12-31

88,360 bars; 1,273 planted jumps of 16 ticks.

| Check | Result | Trades | Mean captured (ticks) | z | Direction hit rate |
|---|---|---|---|---|---|
| Planted future, real engine: must show NO edge | **PASS** | 1210 | -0.19 | -0.71 | 0.515 |
| Mutant engine (fills at the decision bar's open): canary must DETECT it | **PASS** | 1212 | 15.63 | 53.65 | 0.948 |
| Mutant engine (strategy sees bar N+1 early): canary must DETECT it | **PASS** | 1212 | 15.63 | 53.65 | 0.948 |
| Marker one bar early (legitimately tradeable), real engine: must CAPTURE it | **PASS** | 1212 | 15.63 | 53.65 | 0.948 |
| Random baseline on planted data (literal check) | **PASS** | 1826 | 0.00 | 0.00 | — |
| Random baseline on the unplanted copy | **PASS** | 1825 | 0.03 | 0.06 | — |
| Random baseline on planted data, LEAKY engine (shows the literal check is blind) | **PASS** | 1828 | 0.29 | 0.50 | — |
| Tripwire feed: bars pulled at each strategy call == N+1 | **PASS** | 88360 |  |  |  |
| Strategy receives only frozen primitive objects | **PASS** | 88360 |  |  |  |
| Intents stamped with the bar OPEN are refused, never filled | **PASS** |  |  |  |  |
| Flipping vendor_degraded_day everywhere changes nothing | **PASS** |  |  |  |  |
| Every Bar field has a point-in-time class | **PASS** |  |  |  |  |

Diagnostics (informational): mutants on the latency markers act one bar early, so they should capture ~0.

| Diagnostic | Trades | Mean captured (ticks) | z |
|---|---|---|---|
| same_bar_fill_on_latency_markers | 1212 | 0.02 | 0.08 |
| peek_next_bar_on_latency_markers | 1212 | 0.02 | 0.08 |

### Synthetic random-walk bars, 40 RTH days

16,200 bars; 800 planted jumps of 16 ticks.

| Check | Result | Trades | Mean captured (ticks) | z | Direction hit rate |
|---|---|---|---|---|---|
| Planted future, real engine: must show NO edge | **PASS** | 800 | 0.07 | 0.57 | 0.516 |
| Mutant engine (fills at the decision bar's open): canary must DETECT it | **PASS** | 800 | 16.02 | 129.12 | 1.000 |
| Mutant engine (strategy sees bar N+1 early): canary must DETECT it | **PASS** | 800 | 16.02 | 129.12 | 1.000 |
| Marker one bar early (legitimately tradeable), real engine: must CAPTURE it | **PASS** | 800 | 16.02 | 129.12 | 1.000 |
| Random baseline on planted data (literal check) | **PASS** | 347 | -0.17 | -0.17 | — |
| Random baseline on the unplanted copy | **PASS** | 347 | 0.11 | 0.16 | — |
| Random baseline on planted data, LEAKY engine (shows the literal check is blind) | **PASS** | 347 | -0.03 | -0.03 | — |
| Tripwire feed: bars pulled at each strategy call == N+1 | **PASS** | 16200 |  |  |  |
| Strategy receives only frozen primitive objects | **PASS** | 16200 |  |  |  |
| Intents stamped with the bar OPEN are refused, never filled | **PASS** |  |  |  |  |
| Flipping vendor_degraded_day everywhere changes nothing | **PASS** |  |  |  |  |
| Every Bar field has a point-in-time class | **PASS** |  |  |  |  |

Diagnostics (informational): mutants on the latency markers act one bar early, so they should capture ~0.

| Diagnostic | Trades | Mean captured (ticks) | z |
|---|---|---|---|
| same_bar_fill_on_latency_markers | 793 | -0.04 | -0.29 |
| peek_next_bar_on_latency_markers | 793 | -0.04 | -0.29 |

## Pass/fail criteria (fixed in code before any run)

- `leak_canary_real_engine`: trades >= 100 AND mean captured < JUMP/4 ticks AND |z| < 4 AND |hit rate - 0.5| < 4 binomial SE
- `positive_control_detected`: trades >= 100 AND mean captured >= JUMP/2 ticks AND z >= 5
- `latency_control_real_engine`: trades >= 100 AND mean captured >= JUMP/2 ticks AND z >= 5
- `random_baseline`: trades >= 100 AND |mean gross ticks per round trip| < 4 SE
- `tripwire`: at every strategy call for bar N, exactly N+1 bars pulled from the feed

## Design

- **Planted data.** A copy of real research bars (trade dates above) gets a 16-tick jump inside RTH bars every 20 minutes, in a seeded random direction. Every later bar shifts with it, so prices stay continuous and on-grid, and every row still passes `construct_bar`. The original frame is never mutated.
- **Why the marker sits on the jumped bar.** A marker that becomes visible at bar N's close and predicts bar N+1's move is legitimately tradeable, so a correct engine SHOULD profit from it. That is the latency control, not a leak test. The leak canary instead carries information about a move that has already happened by the time a point-in-time engine may act. Only an engine that fills at a price from before its decision, or shows the strategy a bar early, can monetize it. Seen from the previous bar's decision point, it is exactly the prompt's 'predictor of the next bar's return'.
- **Mutants.** `_SameBarFillMutant` and `_PeekNextBarMutant` live in `sim/leakage_canaries.py`, run nowhere else, and are marked DELIBERATELY BROKEN. They give identical numbers because both are one-bar look-aheads that trade the same price pairs; the mechanisms differ, and the diagnostics table shows both differ from the real engine.
- **Real engine guards exercised.** The fill-after-decision invariant (`EngineInvariantError`), the intent-timestamp refusal (`engine_intent_timestamp_mismatch`), the one-way iterator, and the frozen `Bar` / `AccountView` hand-off.
- **Hindsight fields.** `vendor_degraded_day` is Databento's after-the-fact quality verdict. It stays on the `Bar` (the Stage C interface lists it) but is classified `hindsight`. Stage D.1 must not condition on it, and the engine provably ignores it. Gating trading on it would silently delete the 2025-11-28 CME outage day from backtests.
- **Not covered.** This suite tests the ENGINE's point-in-time discipline. It cannot detect look-ahead a strategy builds into its own features from data it is handed legitimately. That remains Stage D.1's responsibility, and the canary pattern here (a planted marker plus a reader) is the template for testing a real feature pipeline.
