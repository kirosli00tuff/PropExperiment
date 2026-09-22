# Progress

## 2026-09-16 — Stage A.1: offline data + rules engine build

Offline half of Stage A. No TopstepX credential exists, and none was used, stubbed or referenced. Work lives under `data/`, `rules/`, `sim/`, `tests/`, `reports/`, `ledger/`, plus `docs/ACCESS.md`. Supporting files at the repo root: `pyproject.toml`, `uv.lock`, `.gitignore` (which keeps `.env` and paid raw data out of git). **100 tests pass** (`uv run pytest`); ruff is clean.

### Databento spend (this session)

| | Before | New this session | After | Cap | Headroom left |
|---|---|---|---|---|---|
| Session (`stage-A.1-2026-09-16`) | $0.0000 | **$1.888175** | $1.888175 | $15.00 | $13.11 |
| Shared account (MLCryptoEngine ledger + this repo) | $82.117874 | **$1.888175** | **$84.006048** | $120.00 | $35.99 |

- **Requests:** 18 billable requests (monthly MES `ohlcv-1m` chunks). Each was quoted twice: once in the planning pass, and again immediately before its download. That makes 36 quote entries, 18 commits (written before download) and 18 settles in `ledger/databento_spend.jsonl`, which is append-only.
- **Delivered bytes** equalled quoted billable bytes exactly for all 18 chunks.
- **Actual cost** is recorded as equal to the quote: the historical API returns no per-request invoice. Reconcile against the Databento portal if an exact figure is needed.
- **Refusals:** none. The gate never had to stop a request.

### What ran

1. **Task 1 — adapter port.**
   - **Ported and adapted to MES** from MLCryptoEngine's `data/databento` module, which was read only, never edited:
     - adapter and immutable raw storage (`data/adapter.py`);
     - symbology-derived roll boundaries;
     - CME session calendar (`data/session.py`);
     - `ts_recv` ordering validation (`data/validate.py`);
     - spend gate and ledger (`data/spend_gate.py`). The gate now also enforces the shared-account cap by reading MLCryptoEngine's ledger, and closes if that ledger is missing.
   - **Added the missing CME holiday calendar** (`data/cme_calendar.py`, 2025–2026). Each day's status comes from CME's own documents; exact clock times are graded CME, empirical, secondary or inferred per entry. Every holiday inside the data window was then **checked against the bars**. That check caught one research error: 2025-07-04 was an early 12:00 CT halt, not a full closure. It was fixed, with a regression test.
2. **Task 2 — MES ohlcv-1m pull.**
   - **Data:** `MES.v.0`, 2025-04-01 → 2026-09-16 (17.5 months), 517,197 bars.
   - **Immutable raw:** stored read-only. A re-fetch is refused before any quote, and final placement uses `os.link`, so an existing file can never be replaced.
   - **Continuous series:** written to `data/processed/MES/…parquet`, with flag columns documented in the schema metadata and in `data/bars.py`: `in_flatten_window` (15:10 CT), `in_no_new_positions_window` (15:08 CT), `in_scheduled_closure`, `is_roll_session`, `gap_before_minutes`, `vendor_degraded_day`, `trade_date`, `raw_symbol`.
   - **Daily halt:** confirmed as 16:00–17:00 CT, both in the calendar and in the data (0 bars inside it).
3. **Task 3 — validation.** Full findings in `reports/bar_validation.md`.
   - **Hard checks:** 0 ordering, duplicate, negative-volume, off-tick or OHLC failures.
   - **Gaps:** 663 missing expected minutes in 19 runs, all flagged and none filled: 18 single overnight minutes, plus the 645-minute CME outage of 2025-11-27/28. There are 0 RTH gaps.
   - **Tick cross-check:** MLCryptoEngine's trades files for 2026-07-15 and 2026-07-31, read in place, match the bars exactly: 2,640 minutes at **0 ticks / 0 contracts** tolerance. One condition: trades must be bucketed by `ts_recv`. Databento builds bars on its receive clock, and bucketing by `ts_event` gives 12 boundary minutes that differ.
4. **Task 4 — cost model** (`sim/costs.py`, calibrated by `sim/calibrate_slippage.py` into `sim/slippage_calibration.json`).
   - **Input:** the two mbp-10 days in MLCryptoEngine, read in place, not re-bought; 25.6M book records.
   - **Output:** one-side market-order slippage versus mid, in ticks, by 15-minute CT bucket and size.

     | Window | 1 micro | 10 micros | 50 micros |
     |---|---|---|---|
     | Open (08:30–09:00) | 0.547 | 0.602 | 1.161 |
     | Midday (11:00–13:00) | 0.523 | 0.542 | 0.867 |
     | Close (14:30–15:10) | 0.525 | 0.557 | 0.978 |

   - **Commission:** $1.22 MES round turn, with the source cited in code and a blocking TODO to reconfirm at checkout.
   - **Not covered:** the model excludes latency, adverse selection and queue position, and rests on only two days.
5. **Task 5 — rules engine** (`rules/xfa_rules.py`). Pure functions with integer-cent money. Each rule is its own function:
   - **MLL:** the end-of-day trailing floor (part a) is separate from the real-time equity breach check (part b).
   - **Combine:** the best-day rule raises the profit target; it never fails the account.
   - **XFA payouts:** Standard and Consistency eligibility, and payout checks in a fixed order with named refusals.
   - **Post-payout MLL reset:** its own state transition.
   - **Scaling Plan:** uses `MICROS_PER_MINI = 10`.
   - **15:10 CT flatten:** no override input exists.
   - **Gate:** an HFExperiment-style frozen intent with construction-time refusal, plus an AiTrader-style deny-only gate whose limits are module constants.
6. **Task 6 — known-answer tests** (`tests/test_xfa_rules.py`, 60 tests; every expected value is hand-computed in a comment). All five required scenarios are present and pass:
   - **Intrabar wick:** breaches the MLL although the day's close never does.
   - **Big Combine day:** raises the target and the account is explicitly not failed.
   - **Consistency boundary:** 40.00% passes and 40.01% fails.
   - **Balance ceiling:** a payout above 50% of balance but under the dollar cap is refused, with a reason distinct from the dollar-cap refusal.
   - **Post-payout loss:** the MLL resets to $0, and an immediate loss is caught as a breach. A counterfactual check proves the old floor would have missed it.

### Conflicts flagged, not silently resolved

**Rules: stricter value encoded.** I checked the prompt's rule figures against Topstep's help center on 2026-09-16. Where they differ, the **stricter** value is encoded (listed in the `rules/xfa_rules.py` docstring). All need reconfirmation in Stage A.2:

1. **Combine consistency:** the help center now says **55%**; the prompt says 50%. 50% is kept, as the stricter value. The same help article still shows a "÷ 0.50" example, so it contradicts itself.
2. **Scaling Plan at exactly $2,000:** the help center text says "$1,500–$2,000: 3 lots; *above* $2,000: 5 lots". I encoded 5 lots only above $2,000. The tier table itself is an image I could not read directly.
3. **Payout rules the prompt did not mention**, now encoded from the help center: the **$125 minimum payout**; after the first payout, Standard requires net profit since the last payout; day counts restart after each payout; and the request day does not count toward the next window.
4. **50%-of-balance ceiling:** the help center applies it to **both** paths. The prompt stated it for Standard only.
5. **Earlier cutoffs:** no new positions from **15:08 CT** ("Risk Managers begin flattening at that time"); on CME early-close days the flatten is **15 minutes before the early close**.
6. **MLL locks:** at $50,000 in the Combine and at $0 in the XFA. The post-payout reset sets the floor to a **$0 balance**, so the drawdown buffer equals the remaining balance, confirmed by Topstep's worked example. It is not literally zero buffer unless the balance is $0.

**Other conflicts:**

- **Possible conflict with docs/DECISIONS.md (needs a decision before Stage A.2, not resolved here).** TopstepX's API Access page says "All trading activity must originate from your personal device. The use of VPS, VPNs, and remote servers is prohibited", and that a server "can watch and record, but it cannot trade". That constrains where the live bot may run.
- **Roll choice.** The series uses `MES.v.0`, not the `MES.c.0` MLCryptoEngine used, because `.c.0` holds the expiring contract through expiry. Even `.v.0` splices about two sessions after volume has moved: roughly 4–6× lower volume on those days. This is flagged for Stage C, and no new roll rule was invented.
- **Commission $1.22:** re-read on the help center 2026-09-16 (article dated 2026-07-28). It still needs checkout confirmation, per the TODO in `sim/costs.py`.
- **Process note:** the rules engine was written before its tests (not strict test-first), and the tests were written from the specification rather than read back from the code.

### Independent code review (rules engine + spend gate)

An independent reviewer read both modules. Result: **0 critical, 0 high, 2 medium**, both fixed test-first (each new test was seen failing before the fix):

1. **Friday evening was not treated as flat.** The flatten and no-new-positions checks treated Friday after 17:00 CT as an open session. Fixed: from Friday's flatten time, the account stays flat through the weekend.
2. **Settle could understate spend.** The settle step flagged a download larger than its quote but still recorded only the quoted cost. Fixed: it now charges pro rata, so the ledger stays pessimistic.

The series was rebuilt afterward and the validation results are unchanged. The 18 real downloads were unaffected: delivered bytes matched the quotes exactly.

### Explicitly skipped (per the Stage A.1 "What not to do" list)

- **TopstepX API key, Practice account, `retrieveBars`:** not touched. No credential exists, and no placeholder, stub or config slot was created.
- **Anything under `live/` or `ops/`, including kill-switch and watchdog code:** not touched. Both directories are still empty.
- **Written questions for Topstep support:** not drafted. They wait until the account exists and checkout figures are confirmed.
- **Funnel-level Monte Carlo and Combine-pass-probability modeling:** not started. That is Stage D.1, which needs a strategy.

### Needed from you tomorrow morning, before Stage A.2

1. **Create a TopstepX account.**
2. **Choose the Combine path at checkout.** Figures below are from the help center on 2026-09-16; confirm them on the checkout page:
   - **Standard:** $49/mo plus a $149 activation fee per XFA.
   - **No Activation Fee:** $95/mo, $0 activation.

   Also decide whether to add the optional **Daily Loss Limit**. It changes pricing and qualifies for the current doubled-payout-cap offer.
3. **Subscribe to API Access.** Listed at $29/mo, or $14.50/mo with code `topstep`.
4. **At checkout, note the MES round-turn commission shown** (expected $1.22) and the 50K XFA payout caps. Those replace the TODO figures.
5. **Decide where the live bot will run,** given the personal-device / no-VPS rule above. A Stage A.2 design constraint.

## 2026-09-17 — Stage B–C: funnel simulator + backtest harness

*(In progress. This entry is written in order; the ETA probe below was logged before Task B.1 started.)*

### ETA probe (run before Task B.1)

- **What ran:** `uv run python -m sim.eta_probe`. It is the thinnest event-driven loop, `sim/engine.py` seeded as `iter_probe_bars` and `run_probe_loop`, run over **one month of MES bars (April 2025)**. It does strict chronological replay and collects intents from a stub that emits every 97th bar. No fill model and no rules gate. April 2025 is the earliest month on disk, chosen so the probe never touches data that could later fall inside the sealed holdout. The probe reads no returns.
- **Measured (best of 5):** 28,979 bars in **0.076 s = 381,186 bars/s**; 298 intents collected; parquet month load 0.032 s.
- **Added second probe:** one rules-engine account-day (`apply_realtime_mll` → `record_realized_pnl` → `close_trading_day` → `check_payout_request`), because that step, not bar iteration, is what the Stage B Monte Carlo repeats. Measured **13.24 µs per account-day** (50,400 steps in 0.668 s).
- **Probe authoring time:** 07:16:00Z → 07:17:12Z, 150 lines in 72 s (one hook-gate retry included). Context reading and design before it took about 11 min.

**ETA derived from the probe:**

| Component | Basis | Estimate |
|---|---|---|
| Engine full-history run (C.2/C.4/C.7) | 517,197 bars ÷ 381k bars/s = 1.36 s bare; allow 10× for gate + fills + ledger | ~14 s per full run; the leakage suite (about 10 runs on subsets) takes < 1 min |
| Funnel null baseline (B.3) | stability ladder 1k→32k runs (Σ 63k) × 2 paths × 252 days × ~4 account-days/day × 13.24 µs × 3 (generator, costs, payout logic) | ~5,100 core-s ≈ **5 min** on 18 workers, plus ~1.5 min for the independent-draw counterfactual |
| Power gate (B.4) | ~48–80 grid points × 2 paths × 4k runs × same per-run cost | ≈ **15–25 min** on 18 workers |
| Authoring | ~5,000 lines (code + tests) at the probe's measured ~125 lines/min = 40 min of writing, × 6 for design / test / fix cycles (the probe's design-to-writing ratio was ~9:1, most of it one-time context reading) | ~4.5 h; delegated work runs in parallel, saving ~1 h |
| Reviews, reports, this entry | — | ~45 min |
| **Total** | | **≈ 4.5–5.5 h wall → completion ≈ 11:45–12:45Z** |

- **Verdict:** the full list fits overnight, so no scope cut is planned. Re-estimate checkpoint: after Stage B completes, compare actual against this table and apply the "if time runs out" priority order if the gap is large.
- **The ×6 multiplier is the one unmeasured input.** The probe measures compute throughput and raw writing speed, not design iterations. It is checked against actuals below.

### What ran

Everything in the task list was built. Nothing was cut. Order of work: ETA probe → split boundaries → null generator → funnel simulator + baseline → strategy interface → engine + fill model → leakage suite → walk-forward → sealed holdout → known-answer tests → independent review → fixes → power gate.

**Stage B : Task 1 — multi-day rules sequence tests** (`tests/test_xfa_rules_sequences.py`, 7 tests). Chains 25-40 day sequences through `rules/xfa_rules.py`: the XFA floor ratcheting and locking at $0 with a final touch breach; the Combine floor locking at $50,000; an intraday wick breaching mid-sequence where the close would not; Scaling Plan tiers crossed in both directions at the exact boundaries ($1,499.99 / $1,500 / $2,000 / $2,000.01) with a `position_limit_exceeded` refusal after a downward crossing; three sequential Standard payouts including a "no profit since last payout" refusal that later clears; two Consistency payouts including a 40%-largest-day refusal diluted by later days; and a Combine whose target is raised twice before it passes exactly at the raised target.

**Stage B : Task 2 — null generator** (`funnel/null_generator.py`, `tests/test_null_generator.py`, 23 tests). Sign-randomized stationary block bootstrap (mean block 5 trading days) over the 310 research-slice RTH sessions. The zero-edge property is structural, not asserted: the side comes from `fair_signs(rng, shape)`, which reads only the shape, so `E[pnl] = ½·move − ½·move = 0` exactly. The tests show the side array is identical for two tables with opposite drift and the same seed, and that a table with a +40-tick drift yields a long-run mean within 4 SE of zero over 400,000 segment draws.
- **Calibrated volatility, from the bars, not invented:** RTH session (08:30 CT open → last bar before the flatten) sd = **226.9 ticks = $283.62 per micro**; mean +13.65 ticks (the historical long drift the coin removes). Good Friday 2026-04-03 is the one research day with no RTH window (its 08:15 halt precedes the 08:30 open) and is skipped.

**Stage B : Task 3 — funnel Monte Carlo** (`funnel/simulator.py`, `funnel/run_null_baseline.py`; `reports/funnel_null_baseline.{md,json}`). 64,000 runs per path of a 12-month (252-day) lifecycle: one Combine at a time, a pass activating one XFA, up to 5 XFAs live, every live account trading the **same** generator draw. Costs and every rule decision go through `sim/fill_model.py` and `rules/xfa_rules.py`.

| | Standard | Consistency |
|---|---|---|
| Combine pass rate per attempt (resolved) | 18.1% (19.6%) | 18.1% (19.6%) |
| P(first payout within 12 months) | 66.3% | 41.9% |
| Months to first payout p10/p50/p90 | 1.8 / 5.0 / 10.1 | 2.1 / 5.9 / 10.6 |
| Monthly net income: mean / median | **+$1** / −$76 | **−$28** / −$92 |
| Monthly net income p80 / p90 / p95 | $43 / $199 / $388 | $2 / $128 / $292 |
| P(monthly net > 0) | 26.3% | 20.4% |
| XFAs activated / breached per run | 2.27 / 2.10 | 2.27 / 1.99 |

- **Sample size was checked, not assumed.** Nested ladder 1k→64k with tolerances fixed in code before the run (rates ±1 pp, money ±max($10, 2%), plus 1.96·SE ≤ tolerance). Both paths stabilise at **N = 16,000**; headline numbers use 64,000.
- **Correlation is the story.** Among days with ≥2 XFAs live and a breach, **21.9%** hit two or more accounts at once (Standard); with independent draws the same figure is **2.5%**. Per run: 5.0% vs 0.4%. Consistency: 20.4% vs 1.8%. Modelling the accounts as independent would understate cluster risk by roughly 9×.
- **The funnel pays for variance.** Null monthly net income rises with size: 1 micro −$53, 2 micros +$1, 3 micros +$83, 5 micros +$177 (Standard, 1 round turn/day). Losses are capped at fees while payouts harvest upside, so a zero-edge gambler is better off sizing up. This drove the power-gate redesign below.

**Stage B : Task 4 — power gate** (`funnel/power_gate.py`, `tests/test_power_gate.py`; `reports/power_gate.{md,json,csv}`, `reports/power_gate_samples.npz`). The screening criterion Stage D.1 runs before spending research time on a candidate. 120 grid points — win probability p in {0.40, 0.45, 0.50, 0.55, 0.60} x average win/loss ratio R in {0.75, 1.0, 1.5, 2.0} x round turns/day T in {1, 2, 4}, both payout paths — at 8,000 runs each: **960,000 simulated 12-month careers**.

- **Two nulls, because the obvious one is too easy.** The *matched* null is a zero-edge trader at the same size and activity. The *robust* null is the most favourable zero-edge result at **any** size on the ladder — the coin-flipper who happened to pick the best size to gamble with. That redesign is forced by the sizing finding directly above: since a zero-edge gambler profits from sizing up, comparing a 2-micro candidate only against a 2-micro null would let a candidate "win" purely by being compared to a badly-sized coin flip. Robust critical values land at 6-7 micros (Standard) and 5-6 (Consistency).
- **Confidence level, stated rather than assumed.** 80% is the headline, with 90% and 95% panels computed alongside. The verdict rule is conservative: a cell passes only if `power - 1.96*se >= 0.80`, so the lower bound must clear the bar, not the point estimate. A cell clearing 0.80 on the point estimate alone is marked `marginal` — exactly one does (standard, T=2, p=0.45, R=2.0, at 95%).

| Null / confidence | Cells passing (of 120) |
|---|---|
| Matched, c = 80% | 46 |
| Matched, c = 90% | 41 |
| Matched, c = 95% | 36 (+1 marginal) |
| **Robust, c = 80%** | **37** |

- **The win/loss ratio dominates the win rate.** No cell with R = 0.75 passes anywhere in the grid — 0 of 30, under either null, at any confidence or activity level. At 1 round turn/day only one cell with R <= 1 passes at all. Lifting p from 0.40 to 0.60 cannot rescue a strategy whose losers match its winners; lifting R from 1.0 to 2.0 repeatedly can. Practical bar for Stage D.1 at 1 RT/day: **R >= 1.5 with p >= 0.55, or R = 2.0 with p >= 0.50.**
- **Nine cells pass the matched null and fail the robust one.** Those are the candidates that would look real against a naive benchmark and are not proven. Use the robust verdict for any claim that has to survive scrutiny.
- **Cost, for reference:** the modelled round turn costs $2.64 per micro at 1 RT/day, $2.61 at 2, $2.59 at 4. At p = 0.50, R = 1.0 the gross edge is exactly zero by construction, and cost alone is what makes that configuration lose money.

**Provenance note, recorded because it matters for trust in these numbers.** Task 4 did not run during the Stage B-C session: the machine shut off in the gap after the size-ladder extension wrote its JSON (2026-09-17T22:57:12Z) and before the gate started. Everything else in this entry is from the original session. The gate was re-run unchanged on 2026-09-17 in a recovery session (`uv run python -m funnel.power_gate`, 2,905.5 s, output stamped 2026-09-18T00:21:27Z) against the same `reports/funnel_null_baseline.json` this entry already describes; no code was modified to produce it. That recovery session also found and fixed a related defect: `funnel/power_gate.py:56` defaults `screen()` to `reports/power_gate.json`, so while the file was missing the exact call this entry recommends to Stage D.1 raised `FileNotFoundError`. The test suite missed it because all five `screen()` tests pass an explicit `tmp_path`.

**Stage C : Task 1 — strategy interface** (`strategy/interface.py`, `strategy/null_strategy.py`, `strategy/random_baseline.py`, `tests/test_strategy_interface.py`, 47 tests). Frozen `Bar` + `AccountView` in, `rules.xfa_rules.OrderIntent` out, so the rules gate consumes a strategy's output with no translation. `construct_bar` refuses malformed rows with named reasons, mirroring `construct_intent`. Both reference implementations are explicit non-strategies: the null emits nothing; the random baseline is an unconditional coin flip keyed by `blake2b(seed, bar.ts_event_ns)` that reads no price, volume or flag — the tests prove that by mutating every price and flag field and getting identical output.

**Stage C : Tasks 2-3 — engine and fill model** (`sim/engine.py`, `sim/fill_model.py`, `tests/test_engine_known_answer.py` 7, `tests/test_engine_constraints.py` 15, `tests/test_fill_model.py` 19, `tests/test_engine_regressions.py` 6). Strict chronological replay from a one-way iterator; FIFO integer-tick lots so every P&L figure is exact to the cent; a complete ledger (intents with their refusal, fills, forced flattens, MLL checks, day closes, account starts) that `reconstruct_balances` rebuilds the final balance from.
- **Cost caveats are carried in the code and repeated here:** the slippage table rests on **two days** of book data and excludes **latency, adverse selection and queue position**. Both calibration days (2026-07-15, 2026-07-31) now fall inside the sealed holdout. Any P&L this engine reports is a **lower bound on cost**, i.e. an optimistic result.
- **Roll blackout, decided from the data:** `MES.v.0` splices about two sessions after volume moves (Stage A.1 measured 20-40% of normal volume on those sessions), so new exposure is refused on the splice trade date and the two preceding trade dates. Those dates come from the vendor roll schedule and the exchange calendar, never from the bars.

**Stage C : Task 4 — leakage suite** (`sim/leakage_canaries.py`, `tests/test_leakage_canaries.py` 15; `reports/leakage_suite.{md,json}`). **Verdict: PASS**, on a planted copy of three real research months and on synthetic bars.

| Check | Result |
|---|---|
| Planted future, real engine (must show nothing) | **PASS** −0.19 ticks/trade, z = −0.71, hit rate 51.5%, 1,210 trades |
| Positive control: same-bar-fill mutant (must be caught) | **PASS** +15.63 ticks, z = 53.6, hit rate 94.8% |
| Positive control: peek-next-bar mutant (must be caught) | **PASS** +15.63 ticks, z = 53.6 |
| Latency control: marker one bar early (must be captured) | **PASS** +15.63 ticks, z = 53.6 |
| Random baseline on planted data (the prompt's literal check) | **PASS** 0.00 ticks/round trip, z = 0.00 |
| Random baseline on a LEAKY engine | PASS too — which is the point (see below) |
| Tripwire: bars pulled at each strategy call == N+1 | **PASS** 0 violations |
| Strategy receives only frozen primitive objects | **PASS** |
| Backdated intents refused, never filled | **PASS** |
| Hindsight flag never gates trading / never reaches the strategy | **PASS** |

- **Why the suite is not just the prompt's recipe.** Running the random baseline on planted data cannot detect a leak: a coin flip never reads the marker. The suite proves that by running the same baseline on a deliberately leaky engine, where it also shows nothing. The real evidence is a canary-reader strategy plus **mutation positive controls**: two engines broken on purpose (`same_bar_fill`, `peek_next_bar`) that the canary must catch, and a latency control that the correct engine must capture. Without the positive controls, "no edge" would be indistinguishable from a broken canary — which is exactly what happened on the first run, when a scoring bug made both controls report 0 trades and I had to fix the suite before trusting it.
- **Design note.** A marker visible at bar N's close that predicts bar N+1's move is *legitimately* tradeable, so it is the latency control, not a leak test. The leak canary carries information about a move that has already happened by the time a point-in-time engine may act.

**Stage C : Task 5 — walk-forward splits** (`data/splits.py`, `tests/test_walk_forward.py` 36; `reports/walk_forward_folds.json`). 311 research trade dates → **8 folds**, each train 142 / embargo 1 / test 21 trade dates, anchored at the end so fold 0's train starts exactly on 2025-04-01 and fold 7's test ends exactly on 2026-06-12. `WF_TRAIN_DAYS` is derived (311 − 8·21 − 1 = 142) from a calendar-computed date list, not a literal, so a calendar correction moves it automatically. Test windows are non-overlapping, so concatenated out-of-sample P&L never double-counts a day. The builder refuses any embargo or holdout date with a named error.

**Stage C : Task 6 — sealed holdout** (`data/holdout.py`, `tests/test_holdout.py` 39; `docs/HOLDOUT_MANIFEST.json`, `docs/HOLDOUT_UNLOCK_LOG.md`). The holdout is **not a file anyone can open**:
- Research + embargo rows (431,999) live in a new read-only research parquet; the holdout (**85,198 bars, 63 trade dates, 2026-06-22 → 2026-09-16**) is encrypted into `data/sealed/`, and so are the **four paid raw DBN months** that overlap it, so "rebuild from raw" is not a way around the seal.
- Reading requires a ceremony: the exact acknowledgement phrase (which is also the key material), a Stage D.2 label, a **non-empty pre-registration** in `REGISTRATION.md` (≥200 characters naming a metric, a threshold and a decision rule — currently 0 bytes, so the gate is shut), an intact checksum, and an acknowledgement of prior unlocks. The log entry is written and fsynced **before** anything is decrypted.
- **No paid data was risked:** every plaintext file was removed only after its sealed copy decrypted back to an identical sha256, and the four raw hashes plus the full-series hash were cross-checked against checksums recorded before the migration. `uv run python -m data.holdout status` reports `all_ok: true`.
- **Residual exposure, stated:** MLCryptoEngine (another repo) still holds plaintext MES tick and book files for 2026-07-15 and 2026-07-31 — the Stage A.1 cost-calibration days, which fall inside this holdout. That is cost-structure information, not price direction, but Stage D.2 should know its cost model was fit on holdout-period book data.

**Stage C : Task 7 — engine known-answer tests.** A throwaway "buy on bar 1, sell on bar 10" strategy on a hand-built series, checked to the cent: entry 6000.25, exit 6003.75, gross +14 ticks = 1,750¢, two fills at 61¢ commission and 63¢ slippage each, final balance **1,502¢**, matched by `reconstruct_balances`. Plus size-bucket rounding (3 micros uses the 5-micro row), fill-time-vs-decision-time bucket selection, a short round trip, FIFO across two entry lots, the real calibration table, forced flatten at the 15:08/15:10 boundaries, MLL liquidation at a hand-derived touch tick (23840 = 5960.00) and at the open when the bar gaps through it, account restart, timestamp-mismatch refusals, roll blackout, position limits, session-change cancellation, and the engine invariants.

### Defects found and fixed (each with a regression test)

**Found by me while wiring the engine:**
1. **A breach at a fill left the position open.** When a fill's cost pushed equity onto the MLL floor, the account breached with the just-opened position still live, and `check_mll` then returned early for a non-active account, so the position kept accruing P&L until the 15:10 flatten. Topstep liquidates at once. Fixed; `tests/test_engine_regressions.py` pins it (verified failing against the pre-fix logic before the fix went in).

**Found by the independent review (three Opus reviewers, each finding adversarially verified by a second agent; 2 of 8 engine/funnel findings were refuted and left alone):**
2. **A position could span a session change** (engine, confirmed high→medium). If no decision time fell inside the flatten window — a data gap, or an early halt the calendar does not know — no forced flatten was queued and the position survived into the next session, to be marked at its open. The reviewer's probe closed a Friday long on Sunday for +$998,780. Now any position still open when a session ends is closed at **that session's last close**, with reason `forced_flatten_session_end`.
3. **A terminal account repeated its last day's P&L forever** (engine, medium). `close_trading_day` leaves a non-active account untouched, so `session_start_balance_cents` froze and every later day reported the breach day's loss again — and the daily series is exactly what Stage D.1 feeds into the funnel. The engine now tracks its own last-close balance.
4. **The engine trusted `OrderIntent` fields** (engine, low). A hand-built intent bypassing `construct_intent` with side `"BUY"` was executed as a **sell**, because `signed_quantity` treats anything that is not `"buy"` as a sell. Now refused as `engine_malformed_intent`.
5. **The hindsight flag reached the strategy** (engine, low). `vendor_degraded_day` is published by the vendor months later. It is now blanked in the copy the strategy receives (`EngineConfig.mask_hindsight_fields`, default on); the engine keeps the true value for reporting. **This is a deliberate deviation from the Stage C task text**, which lists `vendor_degraded_day` among the fields handed to the strategy: a strategy that sits out degraded days would be using information nobody had at the time, and the 2025-11-28 CME outage is exactly the kind of day that would be silently skipped. The flag stays on `Bar` and the behaviour is one config flag away if you disagree.
6. **Re-buy protection matched filenames, not dates** (holdout, medium). Any request whose range covered holdout dates under a different chunk name would have been bought again and landed as plaintext. `fetch_range` now refuses any request overlapping the sealed window (2026-06-21 → 2026-09-17) before it is even quoted — while leaving Stage E forward data (from 2026-09-17) buyable.
7. **The manifest stored absolute paths** (holdout, medium). Moving the repo would have made the sealed chunks look unsealed and re-buyable. Repo-relative paths added alongside.
8. **Deleting the unlock log reset the unlock count** (holdout, medium). The manifest now pins the log's byte length and sha256 at seal time, and `verify_seal` fails if the log is missing, truncated or rewritten.
9. **Newlines in `stage`/`reason` could forge log headings** (holdout, low), inflating the unlock count; the stage regex also accepted "D.2.1". Both tightened.
10. **The pre-registration gate accepted "TBD"** (holdout, low). It now requires ≥200 characters naming a metric, a threshold and a decision rule.
11. **Rebuilding after an authorised unseal would have clobbered the read-only research parquet** (holdout, low), breaking its manifest checksum after doing all the work. `data/build_mes_bars.py` now refuses up front.
12. **`stable_n` accepted the first passing ladder rung** (funnel, low) even if a later rung failed. It is now the smallest N from which every later rung is also stable (today's answer is unchanged: 16,000).

**Refuted by the adversarial verifier, deliberately not changed:** a pending order filling after an intraday data gap (the order was submitted at 15:06 CT, before the 15:08 cutoff — the fill model working as intended), and the end-of-data partial session (walk-forward folds are built from trade dates, so they always end on a complete session).

**One test was rewritten rather than kept passing.** `test_roll_blackout_still_allows_a_reducing_order_on_the_blackout_day` relied on carrying a position overnight into the blackout day — which defect 2's fix correctly makes impossible. The reducing-order branch is now covered white-box in the regressions file, and the replay test asserts what is actually true: on a blackout day the account is flat and both sides are refused.

### Delegation: what went to subagents, at what tier, and what I kept

The prompt reserved ultracode for a genuinely divided build, so here is the division, auditable after the fact.

**Delegated to Sonnet writers (effort high), each verified by an independent Opus agent (effort high/medium) that recomputed expectations by hand and was told to refute:**

| Piece | Outcome |
|---|---|
| B.1 multi-day rules sequence tests | 7 tests. Verifier found 2 blocking gaps (the no-trade-day exclusion was not genuinely exercised; the long Combine sequence had no final breach) → fix round → re-verified clean |
| C.5 walk-forward builder + tests | 36 tests. Verifier independently counted 311 research dates and rebuilt all 8 folds field by field; fix round added parameter validation and derived `WF_TRAIN_DAYS` from the calendar instead of a literal |
| C.1 reference strategies + interface tests | 47 tests. Verifier **mutation-tested** them: 5 deliberate breaks (reading a price, reading a flag, ignoring pending orders, half-exits, doubled entry rate), all caught |
| B.2 null generator tests | 23 tests |
| C.3 fill model tests | 19 tests |
| C.7 engine known-answer + constraint tests | 22 tests. Verifier recomputed every cent, including the liquidation touch price, with plain python arithmetic |
| B.3/B.4 funnel, quality-generator and power-gate tests | 26 tests, including an exact random-walk known answer for the Combine |
| Funnel report prose pass | Verifier checked every number against the JSON and the tables against a fresh render; one fix round |
| Independent correctness review (3 Opus reviewers + adversarial verifiers) | 12 findings, 10 confirmed and fixed, 2 refuted |

**Kept in-house (Opus, lead):** the ETA probe; every statistical design decision (null construction and its zero-edge proof, bootstrap, stability rule, power-gate test definition, sizing rule); the leakage-canary design including the mutation controls; the engine and fill model; the sealed-holdout mechanism and the migration itself; all split boundaries; every defect fix above; and this entry.

**A delegation attempt failed and was re-run:** the first C.7 workflow lost both agents to an account session limit. The re-run produced the tests above. Two later pauses (the session limit, then the machine restart) cost wall-clock time but no work: finished agents replay from cache, and the compute jobs write their outputs in a single step at the end.

### ETA (probe-derived) versus actual

| | Probe-derived ETA | Actual |
|---|---|---|
| Engine full-history run | ~14 s | ~17k bars/s under load; 3 research months replay in ~5 s |
| Funnel null baseline | ~6.5 min | **32 min** (5×) |
| Power gate | 15-25 min | **48.4 min** (2×) |
| Leakage suite | < 1 min | 37 s (real + synthetic) |
| Authoring | ~4.5 h | ~2 h of hands-on time |
| **Total** | **4.5-5.5 h** | **≈4 h of active work, spread over ~16 h wall clock** |

- **Where the estimate was wrong, and why.** The Monte Carlo estimate assumed ~26 ms per run; a *null* run really costs ~3 ms, so the per-run estimate was 8× pessimistic — but the sensitivity grid multiplies runs by 24 configurations, and large-size configurations keep accounts alive far longer than the null headline, so the wall-clock came out 5× over. The lesson for the next probe: time the *most expensive* configuration in the grid, not the headline one.
- **The power gate missed the same way the funnel did, for the same reason.** 15-25 min estimated, 2,905.5 s (48.4 min) actual. The estimate was again anchored on a cheap configuration: the grid's cheapest cell (T=1, p=0.40, R=0.75) costs about 2.4 s, the richest (T=4, p=0.60, R=2.0) about 78 s — a 30× spread, because high-edge cells keep five XFAs alive all year instead of breaching them early. Per-configuration costs came in at 267 s / 390 s / 700 s for Standard at T=1/2/4 and 312 s / 461 s / 775 s for Consistency (2,905 s total). Same lesson as the null baseline, now demonstrated twice: **time the most expensive configuration in the grid, not the headline one.**
- **Authoring beat the estimate** because the ×6 design-iteration multiplier was pessimistic for work that was fully designed before writing, and because nine delegated pieces ran in parallel with my own.
- **Wall clock ≫ working time.** An account session limit (~6.6 h) and the user being away (~6.8 h) dominate the calendar. No task was cut for time.

### Databento spend

**$0.00 this session.** Nothing in Stage B or C needed new data: everything runs on the MES bars Stage A.1 already pulled. The ledger is unchanged at 72 entries, last written 2026-09-16.

| | Before | This session | After | Cap |
|---|---|---|---|---|
| Session | — | **$0.00** | $0.00 | $5.00 |
| Shared account | $84.006048 | **$0.00** | $84.006048 | $120.00 (headroom $35.99) |

The spend gate was touched only to make it **refuse** more: a request overlapping the sealed holdout window is now rejected before it is quoted, so a future session cannot accidentally re-buy sealed months.

### What Stage D.1 needs from this session

Stage D.1 is strategy research and is still a separate session. Nothing here designs, implies or hints at an edge: the only two strategies in the repo are a null that never trades and an unconditional coin flip, both explicitly labelled non-strategies. What D.1 inherits:

1. **The contract to build against:** `strategy/interface.py` (`INTERFACE_VERSION = 1`). Implement `on_bar(bar, account) -> Sequence[OrderIntent]`, build intents with `market_intent(bar, side, qty)`, and read `strategy/random_baseline.py` as the shape to copy. The engine enforces the timing contract; you cannot accidentally trade on a price you have not seen.
2. **The benchmark to beat:** `reports/funnel_null_baseline.md`. A zero-edge trader at 2 micros makes about **+$1/month** on the Standard path and **−$28/month** on the Consistency path, with a lottery-like right tail. Beating "positive P&L" is not the bar; beating *this* is.
3. **The screen to run before spending research time:** `funnel.power_gate.screen(path, win_probability, win_loss_ratio, segments_per_day)` against `reports/power_gate.json`. It returns a verdict for your candidate's estimated per-trade quality. Use the **matched** verdict for the honest question and the **robust** one if you want the stricter test.
4. **The harness:** `sim.engine.run_backtest(bars, strategy, EngineConfig(restart_on_terminal=...), table)` with bars from `data.research_bars.load_research_bars(BAR_COLUMNS)`. `sim.engine.daily_net_pnl(result)` gives the per-day series to feed back into the funnel simulator through a bootstrap generator with the same `draw(rng, n_days)` shape as `funnel.null_generator.NullDayGenerator`.
5. **The folds:** `data.splits.walk_forward_folds(...)` — 8 non-overlapping test windows, 168 out-of-sample trade dates in total. Fit on train, report on test, never on the holdout.
6. **The rule you must not break:** the holdout (2026-06-22 → 2026-09-16) is sealed. Before Stage D.2 can read it, someone has to write a real pre-registration into `REGISTRATION.md` (metric, threshold, decision rule) — ideally at the *end* of D.1, while the bar is still honest.
7. **Run the canaries after any harness change:** `uv run pytest tests/test_leakage_canaries.py`. A failure there is a stop-the-line event; every backtest number is provisional until it passes.
8. **Carry the cost caveat into every claim:** commission $1.22/round turn still needs checkout confirmation (Stage A.2), and the slippage model is a two-day lower bound that excludes latency, adverse selection and queue position. A strategy that only works at modelled cost does not work.

### Still open / for Stage A.2

- Every Topstep figure here (the $49/month Combine, $149 activation, $14.50/month API, the $1.22 commission, the payout caps and the rules conflicts Stage A.1 flagged) is still help-center-sourced and needs checkout confirmation. The fee schedule is one frozen dataclass (`funnel.simulator.FeeSchedule`), so re-running the baseline with confirmed numbers is a one-line change.
- Payouts in the funnel are **gross**: no profit split is applied, because the current split was not confirmed. If Topstep keeps a share, every income figure above is optimistic by that share.
- The XFA activation delay, LFA call-up, inactivity rules and the optional Daily Loss Limit plan are not modelled.

## 2026-09-18 — Stage D.1: strategy research and hypothesis screening

### Headline

**No candidate is shortlisted. 23 hypotheses were formalized and screened across 5 non-overlapping families. None clears the robust power-gate verdict: not on fold 0's train dates, and not on the full 289-day train-date union.** The best-looking results are all unconditional long positions. Their P&L is what the research slice's own upward drift predicts, so the gate never had edge to grade in the first place. Removing those long-only trials shows that nothing conditional carries forward: the in-sample winner loses out of sample in 94% of splits. `REGISTRATION.md` stays empty. Nothing here is ready for Stage D.2.

### Guardrails, with evidence

- **Sealed holdout:** `python -m data.holdout status` gives `all_ok: true`, `unlocks_logged: 0`, `research_has_no_holdout_rows: true`. I checked it before dispatch, during the run and at the end. No research file imports or names an unlock path (`grep -rniE "unlock|data/sealed" strategy/research/` finds nothing).
- **`REGISTRATION.md`:** 0 bytes.
- **Protected files:** `git diff HEAD` is empty for `sim/engine.py`, `sim/fill_model.py`, `strategy/interface.py`, `rules/xfa_rules.py`, `funnel/power_gate.py`, `data/splits.py`, `data/holdout.py`, `data/research_bars.py`, `docs/HOLDOUT_UNLOCK_LOG.md` and `docs/HOLDOUT_MANIFEST.json`. No new backtest infrastructure was built.
- **Other guardrails:** `live/` and `ops/` are still empty. No TopstepX reference exists anywhere. No sentiment or social-media signal was built.
- **Train dates only:** every backtest used `fold.train_dates`, and no test-only date was read.
- **Leakage canaries:** `tests/test_leakage_canaries.py` ran after every family's strategies were in final form, and all 15 passed each time. The full suite passes (364 tests) and ruff is clean.
- **Databento spend: $0.00.** Nothing needed new data. The ledger is unchanged at 72 entries, last written 2026-09-17; the $10 cap was never approached.

### Delegation breakdown

**5 Sonnet subagents, effort high, one per family.** Each ran Task 1 → Task 3 end to end as a two-stage pipeline: research, then formalize and screen. That is 10 completed subagent calls in total. The session's default workflow guideline is under 5 agents; I went above it because this prompt sets its own band of 4–6 for a broad sweep of the source directory, and 5 conditioning variables were needed to cover it without overlap.

| Agent | Region: the only variable it may condition on | Tier | Research | Screen |
|---|---|---|---|---|
| `a_session_clock` | Clock only: time of day, session position, day of week | Sonnet / high | done | done, 6 trials |
| `b_reference_breakout` | Price crossing a level computed from a prior completed window | Sonnet / high | done | done, 6 trials |
| `c_short_horizon_reversal` | Sign and size of a recent return, plus bar-derived flow proxies | Sonnet / high | done (run 1) | done, 3 trials (+1 not runnable) |
| `d_volatility_state` | An estimated state: realized vol, range compression, volume regime, gap size | Sonnet / high | done | done, 4 trials |
| `e_calendar_event` | An exogenous calendar known in advance: FOMC/CPI/NFP, expiry, month turn | Sonnet / high | done | done, 4 trials |

**Kept in-house (Opus, lead):**
- the partition itself;
- verifying retrieval capability before dispatch;
- the Task 4 statistics module (`funnel/multiple_comparisons.py`, with 24 known-answer tests);
- an independent re-run of all 23 trials (`strategy/research/_lead_accounting.py`);
- every judgment below about what is real and what is an artifact;
- this entry.

**A delegation run was lost and recovered.** The first run lost 5 of its 6 in-flight agents to the account session limit; only the reversal family's research stage finished. The workflow could not be resumed across sessions, so I extracted that finished result from the old journal and fed it into the second run as input. It was reused, not re-researched. Subagent tokens: 535k in run 1 (mostly lost) and 1.29M in run 2.

**Partitioning failure, recorded as one:**
- **B-H4 and D-H3 test the same mechanism.** B-H4 is a narrow-range-conditioned opening-range breakout. D-H3 is range compression gating a breakout. Both are Crabel's contraction → expansion idea, with different parameters. My boundary told B not to use volatility-state filters "as a standalone idea". That left room for B to use one as a filter on its own breakout, which is what happened. The wording was too loose, and the mistake is mine, not the agents'. Both variants failed.
- **Separately, source convergence rather than a partition breach:** A-H1, A-H4 and D-H4 all rest on the same NY Fed overnight-drift paper (Boyarchenko, Larsen & Whelan, SR 917). They condition on different variables (the clock versus gap size), so the partition held. But their results are not independent evidence, and the Task 4 trial count treats them as separate trials, which makes that count generous to the candidates.

### Task 1: literature and community investigation

**183 items considered: 81 passed the relevance pre-filter, 102 were rejected in one line each, and 41 were carried forward.**

| Family | Items | Passed | Rejected | Carried forward |
|---|---|---|---|---|
| A session clock | 28 | 17 | 11 | 10 |
| B reference breakout | 56 | 8 | 48 | 7 |
| C short-horizon reversal | 24 | 11 | 13 | 6 |
| D volatility state | 28 | 23 | 5 | 10 |
| E calendar events | 47 | 22 | 25 | 8 |

**Retrieval was mapped before dispatch, because this task is worthless if scraping silently falls back to snippets.**
- SSRN, the prompt's primary HIGH source, returns HTTP 403 to WebFetch.
- The Playwright browser fallback is unavailable: no Chrome is installed.
- The path that works is WebSearch → an author, RePEc or university mirror → WebFetch, which saves the PDF → `pdftotext`. I verified it end to end on the anchor paper, SSRN 2693810, via `pages.nes.ru`.
- The check paid off immediately. The search snippet claimed the anchor paper's sample ran to November 2011. The paper itself says January 2008 – September 2011 (draft of March 2018).

**Retrieval shortfalls, stated rather than smoothed over:**
- **Only 34 of the 81 items that passed the pre-filter were read in full.** The rest: 9 blocked (SSRN or ScienceDirect 403 with no mirror), 16 snippet-only, 6 abstract-only, 4 skipped for "time budget", and the remainder not retrieved. The prompt sends every passing item to full-text retrieval, so the 4 time-budget skips are a shortfall, not a documented block.
- **10 carried-forward sources were never read in full.** Their claims stay marked `[unverified]` and did not feed any hypothesis as sourced fact.
- **A weakness in the verification tool itself.** WebFetch passes HTML pages through a summarizing model, so a "direct quote" from an HTML page is not guaranteed to be word-for-word. Only the PDF → `pdftotext` path returns exact source text. Quotes gathered via HTML (for example Carver's blog) are a lower verification tier than quotes from PDFs.

**Social and sentiment data:** no avenue surfaced that argued seriously for sentiment as a signal. Nothing was built.

<details>
<summary>Full Task 1 log: every item considered, including one-line pre-filter rejections (183 items)</summary>

**Family A — Session-clock seasonality** (28 items, 17 passed the pre-filter, 10 carried forward)

| # | Source | Item | Pre-filter | Retrieval | Carried | Mechanism, or rejection reason | Quality flags |
|---|---|---|---|---|---|---|---|
| A1 | SSRN (mirror: pages.nes.ru) | [Intraday Trading Invariance in the E-mini S&P 500 Futures Market (And…](https://pages.nes.ru/aobizhaeva/ABKO-intradayinv.pdf) | pass | full text (PDF, exact) | yes | Establishes that MES-class E-mini futures have a real, measured, deterministic U-shaped intraday activity pattern (open/close busy, midday quiet) — f… |  |
| A2 | NY Fed Staff Reports | [The Overnight Drift (Boyarchenko, Larsen, Whelan) — SR 917, rev. Aug …](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf) | pass | full text (PDF, exact) | yes | Deterministic, clock-timed liquidity-provision/inventory-risk resolution at a fixed session boundary (European open) — pure flow-timing, not a price-… |  |
| A3 | Liberty Street Economics (NY Fed b… | [The Disappearing Overnight Drift (2026 follow-up to SR 917)](https://libertystreeteconomics.newyorkfed.org/2026/07/the-disappearing-overnight-drift/) | pass | full text (HTML via summarizer) | yes | Direct evidence the classic overnight-drift edge has structurally decayed since 2021 — MES's own research window (Apr 2025–Jun 2026) is entirely insi… |  |
| A4 | SSRN (403, no free mirror found) | [Market Return Around the Clock: A Puzzle (Bondarenko & Muravyev), JFQ…](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3596245) | pass | blocked | yes | Same European-open flow-timing story as SR 917, on a different sample window — a strong corroborating citation for H1 but not load-bearing on its own… | numbers repeated identically across many secondary sources … |
| A5 | arXiv q-fin.TR | [Does Overnight News Explain Overnight Returns? (Glasserman, Krstovski…](https://arxiv.org/pdf/2507.04481) | pass | full text (PDF, exact) | yes | Own core mechanism (NLP-scored news topic exposure) is out of my family's scope (reads news/calendar content, belongs to family E). Retained only as … |  |
| A6 | citation only, inside item above (… | Cooper, Cliff & Gulen (2008) — overnight equity risk premium | pass | not_independently_retrieved | no | Individual-stock/index cash-equity study, not futures; supports the broader overnight-return stylized fact but not independently verified. | secondary citation only, not independently read |
| A7 | citation only, inside item above (… | Kelly & Clark (2011) — overnight returns on index ETFs | pass | not_independently_retrieved | no | ETF-based, adjacent instrument; not independently verified. | secondary citation only, not independently read |
| A8 | jonathankinlay.com (practitioner b… | [Overnight Trading in the E-Mini S&P 500 Futures (2019)](https://jonathankinlay.com/2019/03/overnight-trading-in-the-e-mini-sp-500-futures/) | pass | full text (HTML via summarizer) | yes | Corroborates overnight-session anomaly on the exact instrument, but is itself a direct, concrete instance of the program's cost-discipline prior: the… | practitioner blog, single-author, methodology not peer-revi… |
| A9 | JSTOR / Journal of Financial and Q… | [Day-of-the-Week Effects in Financial Futures: GNMA, T-Bond, T-Note, T…](https://business.purdue.edu/faculty/mcconnell/publications/Day-of-the-Week-Effects-in-Financial-Futures.pdf) | pass | full text (PDF, exact) | yes | Not equity-index futures, but directly on-point as a methodological caution: day-of-week seasonals in financial futures are regime-unstable and can f… |  |
| A10 | Journal of Financial Economics (mi… | [Hedging Demand and Market Intraday Momentum (Baltussen, Da, Lammers, …](https://academicweb.nd.edu/~zda/intramom.pdf) | pass | full text (PDF, exact) | yes | Directly on-instrument (S&P E-mini, NQ). NOTE: their actual tradeable signal conditions on the day's realized return-so-far, which is a 'recent retur… |  |
| A11 | arXiv q-fin.ST | [Stylized Facts and Market Microstructure: German Bond Futures (Bodor …](https://arxiv.org/pdf/2401.10722) | pass | full text (PDF, exact) | yes | Rates futures (fallback clause), LOB-based — the U-shape finding itself is not testable on MES this session (no order-book data on disk per the DATA … |  |
| A12 | Quantpedia (medium priority per so… | [Lunch Effect in the U.S. Stock Market Indices](https://quantpedia.com/lunch-effect-in-the-u-s-stock-market-indices/) | pass | full text (HTML via summarizer) | yes | Weak discovery-layer lead only — admitted lack of academic grounding means this should not be independently formalized, but it does corroborate the g… | self-admits: pattern 'not documented in academic papers', s…; no explicit Sharpe/CAGR/win-rate numbers given in the acces… |
| A13 | quanttraderjournal.com (practition… | [Intraday Seasonality Patterns in Futures Markets](https://quanttraderjournal.com/articles/intraday-seasonality-futures) | pass | full text (HTML via summarizer) | no | Rejected as evidence despite being read in full — logged specifically as a cautionary example; its numbers must not influence any hypothesis or the n… | speculative numbers dressed as findings — precise-looking t…; textbook example of exactly the source-quality tell the tas… |
| A14 | SSRN / arXiv | [Structural Limits of OHLCV-Based Intraday Signals in MNQ Futures: A S…](https://arxiv.org/abs/2605.04004) | pass | abstract only | no | Directly on-instrument (MNQ) but every tested signal reads price/range/volume (opening range, gap, volume signature) — out of my family's scope (belo… | single-author SSRN preprint, unclear peer-review status |
| A15 | IEEE / ResearchGate / academia.edu | [Assessing the Profitability of Timely Opening Range Breakout on Index…](https://ieeexplore.ieee.org/document/8641124/) | pass | abstract only | no | Right instrument family (equity index futures) but the signal reads the opening price range directly — out of my family's scope (price/range-conditio… |  |
| A16 | Journal of Financial Economics | [The Cross-Section of Intraday and Overnight Returns (Bogousslavsky, 2…](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2869624) | reject | — | no | cash-equity cross-sectional factor-timing study (size/illiquidity/profitability premia across many stocks), no single-instrument futures angle — gene… |  |
| A17 | databento.com | [Market microstructure guide](https://databento.com/microstructure) | pass | full text (HTML via summarizer) | no |  |  |
| A18 | CFTC Office of the Chief Economist | [Gaussian Process-Based Algorithmic Trading Strategy Identification](https://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_algorithmictradingstrateg.pdf) | reject | — | no | right instrument (E-mini S&P 500 data) but wrong topic — about classifying/identifying algorithmic trading strategy types via ML, not session-clock r… |  |
| A19 | qoppac.blogspot.com (Robert Carver) | [This Blog is Systematic — various posts](https://qoppac.blogspot.com/) | reject | — | no | discovery-layer search found no specific quantified time-of-day or day-of-week seasonality post; only general commentary that momentum rules can be c… |  |
| A20 | CME Group | [Quarterly Equity Insights newsletters (Jan 2025, Apr 2026, Jul 2026 i…](https://www.cmegroup.com/newsletters/quarterly-equity-index-recap/2026-july-equity-index-recap.html) | reject | — | no | reachable content, but no time-of-day/day-of-week seasonality article located across the issues surfaced by search — only ADV/volume growth stats and… |  |
| A21 | Barchart | [S&P 500 E-Mini Sep '26 Futures Seasonal Returns chart](https://www.barchart.com/futures/quotes/ES*0/seasonality-chart) | reject | — | no | vendor charting tool, no disclosed methodology — not research |  |
| A22 | TradingView | [S&P 500 E-Mini Futures Chart — ES1! quotes](https://www.tradingview.com/symbols/CME_MINI-ES1!/) | reject | — | no | vendor quote/chart page, not research |  |
| A23 | NinjaTrader (broker blog) | [Fundamental Analysis of E-mini S&P 500 Index Futures](https://ninjatrader.com/futures/blogs/fundamental-analysis-of-e-mini-s-p-500-index-futures/) | reject | — | no | broker marketing content, generic contract-spec overview, no seasonality methodology |  |
| A24 | Benzinga | [S&P 500 Seasonality: Can The First Six Months Predict Performance Of …](https://www.benzinga.com/Opinion/26/08/61251264/sp-500-seasonality-can-the-first-six-months-predict-performance-of-es-futures) | reject | — | no | news/opinion aggregation, not primary research; also concerns semiannual/monthly calendar seasonality rather than session-clock periodicity |  |
| A25 | EquityClock | [E-Mini S&P 500 Futures (ES) Seasonal Chart](https://equityclock.com/charts/e-mini-sp-500-futures-es-seasonal-chart/) | reject | — | no | vendor seasonality charting tool, no disclosed statistical methodology |  |
| A26 | Palma Futures (Substack) | [S&P 500 E-mini Levels For 8/3/2026](https://palmafutures.substack.com/p/s-and-p-500-e-mini-levels-for-832026) | reject | — | no | daily market-commentary newsletter, not research |  |
| A27 | arXiv q-fin.TR | [Seasonal Trading in Commodity Futures: Evidence from Regression and S…](https://arxiv.org/abs/2609.12227) | reject | — | no | commodity-specific mechanics (harvest cycles, weather, storage) — explicitly excluded by the pre-filter rule |  |
| A28 | SSRN / ScienceDirect (JFE 2018) | [Market Intraday Momentum (Gao, Han, Li, Zhou, 2018) — first-half-hour…](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2440866) | pass | abstract only | no | SPY ETF, not futures directly (passes prefilter via the index-tracking fallback clause). Like Baltussen et al., the actual predictive signal conditio… | not independently fetched in full — redundant with the full… |

**Family B — Reference-level breakout / range expansion** (56 items, 8 passed the pre-filter, 7 carried forward)

| # | Source | Item | Pre-filter | Retrieval | Carried | Mechanism, or rejection reason | Quality flags |
|---|---|---|---|---|---|---|---|
| B1 | NES mirror (SSRN 2693810) | [Intraday Trading Invariance in the E-mini S&P 500 Futures Market (And…](https://pages.nes.ru/aobizhaeva/ABKO-intradayinv.pdf) | pass | full text (PDF, exact) | yes | Not a breakout-signal paper itself; establishes that return variation per transaction is log-linearly related to trade size (slope -2) in E-mini S&P … | Peer-reviewed-track academic paper (Kellogg/UIC/Maryland/NE… |
| B2 | CFTC Office of the Chief Economist… | [Stop Orders in Select Futures Markets (Nicholas Fett, Lihong McPhail,…](https://www.cftc.gov/sites/default/files/Stoploss_final_ada.pdf) | pass | full text (PDF, exact) | yes | Direct evidence for the liquidity-vacuum/stop-cascade mechanism at a reference level: resting stop orders are invisible in the book until triggered b… | Primary regulatory research using CME audit-trail data, not…; Authors explicitly disclaim the paper does not reflect CFTC… |
| B3 | CFTC-authorized public release / S… | [The Flash Crash: The Impact of High Frequency Trading on an Electroni…](https://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_flashcrash0314.pdf) | pass | full text (PDF, exact) | yes | Canonical liquidity-vacuum/stop-cascade event in the E-mini S&P 500: a large sell program combined with HFTs demanding immediacy produced a 'hot pota… | Primary CFTC-authorized empirical study using regulatory tr… |
| B4 | Umeå School of Business and Econom… | [Assessing the profitability of intraday opening range breakout strate…](http://www.econ.umu.se/ueslpnr/ues845.pdf) | pass | full text (PDF, exact) | yes | Formalizes ORB as: long/short positions established at a predetermined price threshold a percentage above/below the opening price, built on Crabel's … | Instrument is WTI crude oil futures, not an equity index or…; Peer-reviewed-track academic working paper, appears methodo… |
| B5 | arXiv (q-fin, preprint) | [Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ Fut…](https://arxiv.org/abs/2605.04004) | pass | full text (PDF, exact) | yes | Directly tests Opening Range Breakout (and 13 other OHLCV signal families) on Micro E-mini Nasdaq-100 (MNQ) futures — the Nasdaq sibling of MES in th… | Single-author, 2026-dated arXiv preprint with no visible pe…; Directly echoes this program's own cost-discipline prior (O… |
| B6 | This Blog is Systematic (qoppac.bl… | [A simple breakout trading rule (pysystemtrade)](https://qoppac.blogspot.com/2016/05/a-simple-breakout-trading-rule.html) | pass | partial_fetch_summarized | yes | Continuous (not binary) breakout forecast: forecast = 40 x (price - rolling_mean)/(rolling_max - rolling_min), scaled -20 to +20, smoothed with an EW… | Practitioner author (ex-AHL, published book author), MEDIUM…; Tested across 37 futures contracts broadly, not MES/ES/NQ s… |
| B7 | jonathankinlay.com | [A Meta-Strategy in S&P 500 E-Mini Futures](https://jonathankinlay.com/2020/10/a-meta-strategy-in-sp-500-e-mini-futures/) | pass | partial_fetch_summarized | no | Underlying 'Target Trader Strategy' is a reference-level breakout: enters 40 ticks below a target level (long) or 80 ticks above (short) with a 1,000… | No cost/slippage disclosure despite tick-level entries — a …; Short, cherry-pickable-looking window (2018-2020) with dram… |
| B8 | IEEE Access 2019 / mirrors (Resear… | [Assessing the Profitability of Timely Opening Range Breakout on Index…](https://ieeexplore.ieee.org/document/8641124/) | pass | blocked | yes | Per title/abstract only: a 'timely' opening-range-breakout (TORB) variant tested on one-minute intraday data across DJIA, S&P 500, NASDAQ, HSI and TA… | Three separate mirror URLs (two ResearchGate paths, one Sci…; Passes the prefilter on title/venue alone (peer-reviewed IE… |
| B9 | Stop-Loss Orders and Price Cascade… | [Stop-Loss Orders and Price Cascades in Currency Markets](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr150.pdf) | reject | — | no | Pure FX (currency spot) market study — explicitly excluded by the prefilter's 'pure FX... do NOT pass' rule, despite being the foundational academic … |  |
| B10 | Medium (XT Exchange) | Bitcoin Futures Market Microstructure: Liquidation Cascades, Funding … | reject | — | no | Pure crypto (Bitcoin perpetual/futures liquidations) — excluded by the prefilter's 'pure crypto... do NOT pass' rule. |  |
| B11 | Delphi Digital | Liquidity Cascades & the Evolution of Financial Markets | reject | — | no | Crypto-market liquidity-cascade research report — pure crypto, excluded. |  |
| B12 | Mudrex Learn | What Is Liquidation Cascade In Crypto Futures Trading? (2026) | reject | — | no | Retail crypto-education vendor content on crypto perpetuals — pure crypto, excluded. |  |
| B13 | ChainUp | Crypto Perpetual Futures: Liquidation Mechanics Every Trader Should K… | reject | — | no | Crypto exchange vendor content on perpetual-futures liquidation mechanics — pure crypto, excluded. |  |
| B14 | arXiv | [Slippage-at-Risk (SaR): A Forward-Looking Liquidity Risk Framework fo…](https://arxiv.org/pdf/2603.09164) | reject | — | no | Crypto perpetual-futures exchange liquidity-risk framework — pure crypto, excluded. |  |
| B15 | arXiv | [Resolution-Aware Perpetual Futures on Binary Prediction Markets: An E…](https://arxiv.org/pdf/2605.10400) | reject | — | no | Prediction-market/crypto perpetuals (Polymarket) — no CME/equity-index-futures angle, excluded. |  |
| B16 | Pintu Academy | Liquidation Cascade in the Futures Market: What Is It and How Does It… | reject | — | no | Retail crypto-exchange education content — pure crypto, excluded. |  |
| B17 | Bookmap blog | Market Profile Trading Strategies / Market Profile Charts & Indicators | reject | — | no | Vendor (order-flow visualization tool) marketing content, no primary research or verifiable backtest methodology. |  |
| B18 | QuantVPS blog | The Ultimate Guide to Value Area Trading Strategy | reject | — | no | VPS-hosting vendor marketing content dressed as a trading guide, no verifiable methodology. |  |
| B19 | Axia Futures blog | Trading Breakout Using Market Profile Structure | reject | — | no | Prop-trading-firm/education vendor marketing content, no primary research. |  |
| B20 | Metrotrade blog | What Is a Breakout in Futures Trading? Strategies Explained | reject | — | no | Broker vendor marketing/education content, generic, no verifiable methodology. |  |
| B21 | HowToTrade.com | The Ultimate Guide to the Value Area Trading Strategy | reject | — | no | Retail education vendor content, no verifiable methodology or futures-specific backtest. |  |
| B22 | QuantifiedStrategies.com | Value Area Trading Strategy Explored – Does It Work? (Backtest) | reject | — | no | Retail backtest blog, not in the prioritized source directory; deprioritized as unreviewed vendor content given time budget. |  |
| B23 | FTMO blog | Master Volume Profile Trading with the VA Breakout Strategy | reject | — | no | Prop-firm vendor marketing content, no verifiable methodology. |  |
| B24 | CrossTrade | Opening Range Breakout / CrossTrade | reject | — | no | Trading-platform vendor education page, no verifiable backtest or primary research. |  |
| B25 | edgeful blog | ES futures trading strategies: data-backed approaches for day trading… | reject | — | no | Data-vendor marketing blog presenting statistics without disclosed methodology or cost accounting; not in the prioritized source directory. |  |
| B26 | edgeful blog | 5 minute opening range breakout on ES: 108% return in 6 months | reject | — | no | Vendor marketing content with a headline-return framing (108% in 6 months) typical of cherry-picked-window promotion; no cost/robustness disclosure. |  |
| B27 | tradingstats.net | Opening Range Breakout (ORB) Strategy: 6,142 Days of ES & NQ | reject | — | no | Vendor statistics-marketing site, large sample-size headline with no visible methodology or peer review. |  |
| B28 | tradingstats.net | Initial Balance Breakout Statistics: ES & NQ Futures 2015-2025 | reject | — | no | Same vendor statistics-marketing site as above, no disclosed methodology. |  |
| B29 | steady-turtle.com | Opening Range Breakout Strategy / ORB Guide for ES & NQ Futures | reject | — | no | Vendor/education guide, no verifiable methodology or cost accounting. |  |
| B30 | volatilitybox.com | ES Futures Volatility: Average Daily Range, ATR, and Trading Strategi… | reject | — | no | Vendor content site, generic volatility statistics without a testable breakout-mechanism claim. |  |
| B31 | Trade That Swing | Opening Range Breakout Strategy up 400% This Year (Strict Rules, Full… | reject | — | no | Clickbait vendor marketing (headline annual-return claim), classic quality-flag for speculative/promotional content. |  |
| B32 | proptradingvibes.com | Opening Range Breakout Strategy for NQ & ES (2026) | reject | — | no | Prop-firm-adjacent vendor marketing content, no verifiable methodology. |  |
| B33 | EminiMind | The Opening Range Breakout Trade | reject | — | no | Retail education vendor content, no verifiable backtest. |  |
| B34 | tosindicators.com | Opening Range Breakout For ThinkOrSwim - Free ORB Tools | reject | — | no | Charting-tool vendor marketing page, not research. |  |
| B35 | See It Market | One Trade to Rule Them All: The 15-min Opening Range Breakout | reject | — | no | Practitioner blog, not in the prioritized source directory, hyperbolic title with no disclosed cost accounting. |  |
| B36 | Warrior Trading | Opening Range Breakout Trading Strategy | reject | — | no | Trading-education vendor/broker marketing content. |  |
| B37 | OnlyPropFirms | The 15-Minute Opening Range Breakout Strategy for Futures Trading | reject | — | no | Prop-firm marketing/discovery site, no verifiable methodology. |  |
| B38 | SSRN 3136824 (Yoshihiro Ohashi) | Momentum Ignition Price Manipulation and Pricing Mechanisms | reject | — | no | Generic theoretical market-design/manipulation paper (uniform vs. discriminatory pricing mechanisms); abstract gives no indication it concerns MES/ES… |  |
| B39 | unattributed web result | Momentum Ignition - The Market's Parasitic 'Stop Hunt' Phenomenon Exp… | reject | — | no | Could not confirm from title/lede whether this concerns futures at all versus cash equities market-abuse generally; treated as out of scope rather th… |  |
| B40 | Trading Technologies (TT) Help Lib… | Momentum Ignition / TT Trade Surveillance Help and Tutorials | reject | — | no | Vendor compliance-tool documentation defining a market-abuse pattern for surveillance purposes, not research on a tradeable mechanism. |  |
| B41 | momentumignition.com | Momentum Ignition | reject | — | no | Generic vendor/marketing site, no research content identified. |  |
| B42 | DayTrading.com | Momentum Ignition | reject | — | no | Retail trading-education vendor content, no primary research. |  |
| B43 | FasterCapital | Momentum Ignition: Sparking the Trend: Momentum Ignition and Front Ru… | reject | — | no | Content-farm/SEO site, no primary research or verifiable sourcing. |  |
| B44 | Bookmap blog | How to Spot Stop Order Clusters & Understand Their Impact on Market M… | reject | — | no | Vendor (order-flow tool) marketing content, duplicate of the same source already rejected above for a different article. |  |
| B45 | Tradeciety | The Order Clustering Effect Around Round Numbers | reject | — | no | Retail trading-education vendor content, no verifiable primary research or futures-specific data. |  |
| B46 | ResearchGate | Above Up, Below Down: The Impact of Limit Order Clustering on Stock P… | reject | — | no | Cash-equities-only limit-order-clustering study with no stated futures angle — excluded by the prefilter's cash-equities rule. |  |
| B47 | SSRN 2823630 (Kyle, Obizhaeva) | Dimensional Analysis and Market Microstructure Invariance | reject | — | no | General market-microstructure-invariance theory paper (trade-size/volatility scaling across asset classes), not about a reference-level breakout or l… |  |
| B48 | CME Group Newsletters | [Equity Insights / July 2026 / April 2026 - CME Group Quarterly Equity…](https://www.cmegroup.com/newsletters/quarterly-equity-index-recap.html) | reject | — | no | Covers equity-index total-return-futures roll financing spreads and AIR futures volume, not breakout/stop-cascade mechanics — off-topic for this fami… |  |
| B49 | Databento Blog | [General Databento blog search (OpenBB app with CME futures data, US E…](https://databento.com/blog) | reject | — | no | No specific article on opening-range-breakout or reference-level-breakout mechanics was located despite a targeted search; the discoverable content i… |  |
| B50 | Robot Wealth blog | [General Robot Wealth blog/strategy-index search](https://robotwealth.com/index-of-strategies/) | reject | — | no | No specific breakout/ORB article for equity-index or E-mini futures was located; the breakout content found concerns crypto cross-sectional strategie… |  |
| B51 | Quantitative Brokers blog | [General QB blog/liquidity commentary](https://www.quantitativebrokers.com/blog) | reject | — | no | Execution-algorithm vendor marketing and liquidity commentary, no citable research on the reference-level breakout mechanism itself. |  |
| B52 | Quantpedia | [Screener - Quantpedia](https://quantpedia.com/screener) | reject | — | no | Could not locate a specific opening-range-breakout or reference-level strategy page behind the screener in search results; LOW-priority source per th… |  |
| B53 | QuantConnect forum/research | [Strategy] Opening Range Breakout by Michael Handschuh; Opening Range… | reject | — | no | Community forum/tutorial content, not primary research; also stocks-in-play framing rather than futures. |  |
| B54 | automated-trading.ch / StrategyQua… | Opening Range Breakout Strategy (Quantower); How to create opening ra… | reject | — | no | Trading-platform vendor documentation and forum discussion, not primary research. |  |
| B55 | damnpropfirms.com | Opening Range Breakout Strategy for Futures Traders / Damn Prop Firms | reject | — | no | Prop-firm-review vendor marketing content, no verifiable methodology. |  |
| B56 | Nasdaq (Phil Mackintosh, 'The Prin… | [General search for a breakout/stop-related article on Nasdaq's 'The P…](https://www.nasdaq.com/economic-institute/the-print) | reject | — | no | No specific article addressing breakout/stop-hunt/liquidity-vacuum mechanics was located in search results despite this being a named HIGH-priority s… |  |

**Family C — Short-horizon reversal / mean reversion** (24 items, 11 passed the pre-filter, 6 carried forward)

| # | Source | Item | Pre-filter | Retrieval | Carried | Mechanism, or rejection reason | Quality flags |
|---|---|---|---|---|---|---|---|
| C1 | SSRN 2693810 (mirror: pages.nes.ru) | [Intraday Trading Invariance in the E-Mini S&P 500 Futures Market — An…](https://pages.nes.ru/aobizhaeva/ABKO-intradayinv.pdf) | pass | full text (PDF, exact) | yes | Volume/volatility/trade-size co-movement (mixture-of-distributions / intraday trading invariance), not a reversal mechanism per se; used only as back… | Mandated anchor, not itself a reversal paper — included for… |
| C2 | Journal of Banking & Finance 24 (2… | [Intraday price reversals for index futures in the US and Hong Kong — …](https://www.sciencedirect.com/science/article/abs/pii/S0378426699000722) | pass | blocked | yes | Opening-price-shock reversal: large price change at futures market open predicts a subsequent partial reversal, on S&P 500 futures and Hang Seng Inde… | WebFetch returned a confirmed HTTP 403 on the ScienceDirect…; All content above comes from WebSearch result snippets only… |
| C3 | Journal of Banking & Finance 29 (2… | [Intraday price reversals in the US stock index futures market: A 15-y…](https://digitalcommons.montclair.edu/acctg-finance-facpubs/70/) | pass | abstract only | yes | 15-year (Nov 1987-Sep 2002) study of intraday reversal in US stock index futures following large opening price changes; reversal strongest after larg… | Only the abstract page was retrievable; the DOI-linked publ… |
| C4 | Journal of Empirical Finance 11 (2… | Overreaction of index futures in Hong Kong — Fung & Lam | pass | not_fetched_redundant | no | Same author cluster/topic as Fung, Mok & Lam (2000) — HK-focused companion overreaction study. | Not fetched — logged from a single search-result title only… |
| C5 | arXiv:2605.04004 (q-fin) | [Structural Limits of OHLCV-Based Intraday Momentum Signals in MNQ Fut…](https://arxiv.org/pdf/2605.04004) | pass | full text (PDF, exact) | yes | Tests 14 OHLCV-derived signal families (volume spikes, gap continuation, opening-range breakout, wide-range/'expansion' bars, a volatility-volume-gap… | Single-author, self-identified 'Independent Researcher' wit…; Cites its own unpublished companion arXiv preprints by the … |
| C6 | arXiv:2501.16772 (q-fin.ST) | [Trends and Reversion in Financial Markets on Time Scales from Minutes…](https://arxiv.org/pdf/2501.16772) | pass | full text (PDF, exact) | yes | Minute-to-decade-scale trend/reversion regression on 24 diversified futures markets (including S&P 500 futures) using 14 years (2010-2023) of TickDat… | Peer-reviewed-track academic paper (Zurich University of Ap… |
| C7 | qoppac.blogspot.com | [Very.... slow... mean reversion .... and some thoughts on trading at …](https://qoppac.blogspot.com/2025/03/very-slow-mean-reversion-and-some.html) | pass | fetched_and_summarized | yes | Documents a real, practitioner-run 'fast mean reversion' futures strategy (2-30 minute horizon, explicitly citing Safari & Schmidhuber 2501.16772 for… | Practitioner blog, not peer-reviewed — but this specific po… |
| C8 | arXiv:2508.06788 | [Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomi…](https://arxiv.org/abs/2508.06788) | pass | abstract only | no | 1-second-frequency structural VAR of price/order-flow-imbalance endogeneity in S&P 500 E-mini futures, focused on how macro news announcements reshap… | Only search-snippet-level content retrieved, not full text … |
| C9 | jonathankinlay.com | [Optimal Mean-Reversion Strategies / Mean Reversion Strategies categor…](https://jonathankinlay.com/category/mean-reversion-strategies/) | pass | abstract only | no | Ornstein-Uhlenbeck-process optimal-control framework for mean-reversion strategies (Hamilton-Jacobi-Bellman / Fredholm integral equation for optimal … | Not fetched beyond title/lede — logged honestly as unread p… |
| C10 | quantitativebrokers.com/blog | [Quantitative Brokers blog / Monthly Microstructure Metrics Report](https://www.quantitativebrokers.com/blog) | pass | abstract only | no | Vendor commentary on microstructure 'regimes' (liquidity, spread, book depth) for execution-algo tuning. | Vendor marketing content — flagged per the task's explicit … |
| C11 | robotwealth.com | [Exploring Mean Reversion and Cointegration (Parts 1-2) — Robot Wealth](https://robotwealth.com/exploring-mean-reversion-and-cointegration-part-2/) | reject | — | no | FX pairs/cointegration trading (commodity-currency pairs), not equity-index futures and not a single-instrument bar-derived reversal signal — pure FX… |  |
| C12 | quantpedia.com | [Short Term Reversal with Futures — Quantpedia strategy #](https://quantpedia.com/strategies/short-term-reversal-with-futures) | reject | — | no | Weekly-rebalanced cross-sectional reversal factor across 24 diverse US futures (currencies, agriculturals, commodities, financials) — not intraday mi… |  |
| C13 | arXiv:2608.21888 | [Short-horizon mean reversion in cryptocurrency markets: a matched cro…](https://arxiv.org/abs/2608.21888) | reject | — | no | Pure crypto (Binance pairs); the small US-equities/ETF comparison group does not include futures and is incidental to the paper's crypto focus — expl… |  |
| C14 | arXiv:2606.08586 | [Cross-sectional topological anomaly scores and intraday return predic…](https://arxiv.org/pdf/2606.08586) | reject | — | no | Cross-sectional cash-equity (S&P 500 constituent stocks) signal, not a futures/single-instrument bar-derived reversal mechanism — cash-equities cross… |  |
| C15 | cicfconf.org | [Market Closure and Short-Term Reversal — Della Corte & Kosowski](https://www.cicfconf.org/sites/default/files/paper_357.pdf) | reject | — | no | Title-level read indicates a cash-equity market-closing-auction reversal study, not futures microstructure — cash-equities-only microstructure with n… |  |
| C16 | efmaefm.org | [End-of-Day Reversal — Baltussen, Da & Soebhag](http://www.efmaefm.org/0EFMAMEETINGS/EFMA%20ANNUAL%20MEETINGS/2024-Lisbon/papers/EndofDayReversal_withnames.pdf) | reject | — | no | Cross-sectional cash-equity end-of-day reversal factor ('ROD3 return predicts last-hour return in the cross-section') — cross-sectional equities fact… |  |
| C17 | quantitativo.com (Substack) | [Volume Shocks and Overnight Returns — Quantitativo](https://www.quantitativo.com/p/volume-shocks-and-overnight-returns) | reject | — | no | Cash-equity, overnight-return-focused ('predicts positive returns overnight — but not during the next trading session'); not futures, not an intraday… |  |
| C18 | tandfonline.com | [Persistence or reversal? The effects of abnormal trading volume on st…](https://www.tandfonline.com/doi/full/10.1080/1351847X.2024.2303092) | reject | — | no | Cash-equity cross-sectional abnormal-trading-volume factor study, not futures, not a single-instrument bar-derived signal. |  |
| C19 | arXiv:2201.09319 | [Option Volume Imbalance as a predictor for equity market returns](https://arxiv.org/pdf/2201.09319) | reject | — | no | Options-market volume imbalance predicting cash equity index returns — different instrument/data class (options order flow), not futures bar-derived … |  |
| C20 | newyorkfed.org | [The Overnight Drift — Boyarchenko, Larsen & Whelan (NY Fed SR917)](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf) | reject | — | no | Overnight (close-to-open) drift is a calendar/clock-keyed effect, explicitly owned by a different family (A, clock effects) per this task's scope car… |  |
| C21 | onlinelibrary.wiley.com (Journal o… | [Intraday price-reversal patterns in the currency futures market: GLOB…](https://onlinelibrary.wiley.com/doi/10.1002/fut.20226) | reject | — | no | Currency (FX) futures, not equity-index futures — pure-FX asset class explicitly excluded by the prefilter even when wrapped in a futures contract. |  |
| C22 | cftc.gov | [The Futures Trading Landscape — Fett & Haynes (CFTC OCE, 2017)](https://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_futureslandscape.pdf) | reject | — | no | Descriptive market-structure/participant-composition paper on the S&P E-mini (who trades, contract types), not a reversal-signal or bar-derived-proxy… |  |
| C23 | cftc.gov | [High Frequency Traders and the Price Process (CFTC OCE working paper)](https://www.cftc.gov/sites/default/files/2020-02/ABHFT20191129_ada.pdf) | reject | — | no | Title/lede-level read (E-mini HFT participant classification and price-process effects) shows no specific reversal-signal or bar-derived-proxy conten… |  |
| C24 | Databento Microstructure Guide (se… | [Order Flow Imbalance in Market Microstructure / VWAP-to-mid deviation…](https://databento.com/microstructure/market-microstructure) | pass | abstract only | no | General claim that VWAP-to-mid deviations show 'short-horizon asymmetries coherent with transient pressure followed by microstructure reversion as de… |  |

**Family D — Volatility and liquidity state** (28 items, 23 passed the pre-filter, 10 carried forward)

| # | Source | Item | Pre-filter | Retrieval | Carried | Mechanism, or rejection reason | Quality flags |
|---|---|---|---|---|---|---|---|
| D1 | SSRN 2693810 / mirror pages.nes.ru | [Intraday Trading Invariance in the E-Mini S&P 500 Futures Market (And…](https://pages.nes.ru/aobizhaeva/ABKO-intradayinv.pdf) | pass | full text (HTML via summarizer) | yes | Trade size shrinks systematically, all else equal, in more volatile environments (Intraday Trading Invariance hypothesis); volatility is not tied to … | Anchor paper, peer-quality academic work with named CME-dat… |
| D2 | SSRN 6847024 | [Intraday Microstructure Dynamics of E-mini S&P 500 Futures: Volatilit…](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6847024) | pass | blocked | yes | Documents (per snippet) L-shaped intraday liquidity decay and long-memory/persistent realized volatility in ES futures using 1-minute OHLCV bars over… | papers.ssrn.com returned 403 as expected; no non-SSRN mirro…; Extremely close topical/data match to this session's task (… |
| D3 | Federal Reserve Bank of New York S… | [The Overnight Drift (Boyarchenko, Larsen, Whelan)](https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr917.pdf) | pass | full text (HTML via summarizer) | yes | Order imbalances at the U.S. equity close create dealer inventory risk; dealers demand compensation, generating a systematic positive S&P 500 (incl. … | Federal Reserve staff report, rigorous methodology (bootstr… |
| D4 | CFTC Office of the Chief Economist | [Liquidity in Select Futures Markets (Fett & Haynes, 2017)](https://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_liquidityfuturesmarkets.pdf) | pass | full text (HTML via summarizer) | yes | Order-book depth and average trade size for the S&P E-mini contract decline specifically during periods of elevated volatility -- a direct liquidity-… | Government economist paper, explicit CFTC-employee-in-offic… |
| D5 | CFTC Office of the Chief Economist | [The Futures Trading Landscape (Fett & Haynes, 2017)](https://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_futureslandscape.pdf) | pass | not retrieved (time budget) | no | Per search summary, overviews participant-type activity specifically in the S&P E-mini contract; not fetched in full this session. |  |
| D6 | Review of Finance 2015 / CREATES W… | [Assessing Measures of Order Flow Toxicity via Perfect Trade Classific…](https://pure.au.dk/ws/files/68359010/rp13_43.pdf) | pass | full text (HTML via summarizer) | yes | Cautionary/negative finding: VPIN (a volume-imbalance 'informed trading' proxy, a natural candidate for a 'volume regime' state variable) is construc… | Directly falsifies a plausible 'volume regime as informedne…; Also moot for this session on data-availability grounds: tr… |
| D7 | CME Group articles | [Reassessing Liquidity: Beyond Order Book Depth (2025)](https://www.cmegroup.com/articles/2025/reassessing-liquidity-beyond-order-book-depth.html) | pass | blocked | yes | Per snippet: documents orderbook depth collapsing sharply on a specific April 2025 E-mini S&P volatility event even as volume spiked, illustrating li… | WebFetch timed out twice (60s each); genuine retrieval fail… |
| D8 | CME Group newsletter | [Equity Insights / April 2026 (Quarterly Equity Index Recap)](https://www.cmegroup.com/newsletters/quarterly-equity-index-recap/2026-april-equity-index-recap.html) | pass | snippet only | no | General volume/product-mix commentary, no vol/liquidity-state mechanism or empirical methodology presented. | Vendor newsletter/marketing content, aggregated stats witho… |
| D9 | quantresearch.org | [VPIN: The Volume Synchronized Probability of Informed Trading (Easley…](https://www.quantresearch.org/VPIN.pdf) | pass | not retrieved (time budget) | no | Original VPIN construction paper; superseded for this session's purposes by the Andersen & Bondarenko critique already read in full. |  |
| D10 | Databento Microstructure Guide | [What is market liquidity? / What is volatility (finance)?](https://databento.com/microstructure/liquidity) | pass | snippet only | no | Generic glossary-level definitions of liquidity/volatility and their qualitative relationship (wider spreads under higher volatility). | Reference/glossary content, not an empirical or futures-spe… |
| D11 | Bookmap blog | [Narrow Range Breakouts: Why Volatility Compression Leads to Expansion](https://bookmap.com/blog/narrow-range-breakouts-why-volatility-compression-leads-to-expansion) | pass | full text (HTML via summarizer) | yes | Narrative claim: during range compression, stop-loss and breakout orders cluster at the range boundaries; when the range finally breaks, trapped posi… | No backtests, no statistical data, no citations to research…; Vendor marketing content (Bookmap sells order-flow visualiz… |
| D12 | jonathankinlay.com | [Volatility Trading Styles (2020)](https://jonathankinlay.com/2020/07/volatility-trading-styles/) | pass | full text (HTML via summarizer) | no | Compares aggressive/conservative/balanced short-volatility and VIX-curve trading styles using options and leveraged ETFs; S&P futures mentioned only … | Marketing-style unverified return claims with no methodolog…; These figures are [unverified] and explicitly not adopted f… |
| D13 | jonathankinlay.com | [Simple momentum strategy in E-Mini Futures (new intraday high entry)](https://jonathankinlay.com/) | pass | snippet only | no | Buy S&P E-mini futures when price makes a new intraday high -- an entry trigger. |  |
| D14 | jonathankinlay.com | [Scalping Archives (tag page)](https://jonathankinlay.com/tag/scalping/) | pass | not retrieved (time budget) | no |  |  |
| D15 | qoppac.blogspot.com (Robert Carver) | [Vol Targeting and Trend Following (2018)](https://qoppac.blogspot.com/2018/07/vol-targeting-and-trend-following.html) | pass | full text (HTML via summarizer) | yes | Scales position size dynamically to trailing realized volatility (vol targeting) to normalize risk exposure per trade, rather than holding fixed posi… | Practitioner blog (medium-priority tier per source director… |
| D16 | robotwealth.com | [Robot Wealth site (general search, no specific vol-regime-filter arti…](https://robotwealth.com/) | pass | snippet only | no |  |  |
| D17 | robotwealth.com | [The VIX Futures Basis](https://robotwealth.com/the-vix-futures-basis/) | reject | — | no | VIX futures product-specific basis/term-structure trading -- wrong instrument (a volatility derivative, not equity-index futures) and wrong mechanism… |  |
| D18 | GitHub | [ginsupig/vol-regime-trend-bot](https://github.com/ginsupig/vol-regime-trend-bot) | reject | — | no | Unvetted code repository with no author credentials, methodology writeup, or empirical validation shown -- not a primary research source. |  |
| D19 | General literature (Corsi 2009 and… | [HAR-RV model / volatility clustering & long-memory literature](https://medium.com/@simomenaldo/realized-volatility-and-har-models-a-new-paradigm-for-volatility-forecasting-4a660f2530f3) | pass | snippet only | yes | Foundational, asset-general result: realized volatility exhibits long memory, well captured by an additive cascade of daily/weekly/monthly realized-v… | Not futures/MES-specific; general asset-class result whose … |
| D20 | Journal of Futures Markets (Wiley) | [Forecasting realized volatility: the role of implied volatility, leve…](https://onlinelibrary.wiley.com/doi/full/10.1002/fut.22241) | pass | blocked | no |  |  |
| D21 | arXiv 2604.13458 | [Interpretable Systematic Risk around the Clock (Songrun He)](https://arxiv.org/pdf/2604.13458) | pass | snippet only | no | Uses around-the-clock S&P 500 E-mini futures data (1997-2020) with LLM-classified news-driven jump categories to build a factor-mimicking risk-premiu… |  |
| D22 | arXiv 2510.18569 | [QuantEvolve: Automating Quantitative Strategy Discovery through Multi…](https://arxiv.org/html/2510.18569v1) | pass | snippet only | no | Per snippet, switches between strategies using rolling ATR quantiles and sigmoid transitions as a regime-detection mechanism -- methodologically adja… |  |
| D23 | arXiv 1605.07945 | [Trading VIX Futures under Mean Reversion with Regime Switching](https://arxiv.org/pdf/1605.07945) | reject | — | no | Instrument is VIX futures (a volatility derivative) traded directly via mean-reversion, not MES/ES/NQ equity-index futures conditioned on a vol/liqui… |  |
| D24 | arXiv 2606.09478 | [Volatility Forecasting and Return Prediction under Market Regimes: Ev…](https://arxiv.org/html/2606.09478v1) | reject | — | no | Shanghai Stock Exchange Composite Index (Chinese equity market) -- explicitly excluded by the pre-filter instructions. |  |
| D25 | arXiv 2108.05801 | [A Hybrid Learning Approach to Detecting Regime Switches in Financial …](https://arxiv.org/pdf/2108.05801) | pass | not retrieved (time budget) | no | Per snippet, evaluates regime-detection trading strategies on 'major indices' and futures, 2014-2020. |  |
| D26 | arXiv 2510.03236 | [Improving S&P 500 Volatility Forecasting through Regime-Switching Met…](https://arxiv.org/abs/2510.03236) | pass | full text (HTML via summarizer) | yes | Regime-switching (soft Markov, spectral clustering, HAR-coefficient/Bayesian-GMM) methods to forecast S&P 500 realized volatility; regime state is us… | Instrument is SPX cash index, not ES/MES/NQ futures -- mech… |
| D27 | Nasdaq (The Print, Phil Mackintosh) | [The Print newsletter/author page (no single on-topic article matched)](https://www.nasdaq.com/economic-institute/the-print) | pass | snippet only | no |  |  |
| D28 | Quantpedia / Alpha Architect / Qua… | General strategy screeners and list repositories | reject | — | no | Deprioritized per the source directory's explicit instruction (LOW tier, pursue only if named from elsewhere); not individually queried this session … |  |

**Family E — Exogenous calendar and scheduled events** (47 items, 22 passed the pre-filter, 8 carried forward)

| # | Source | Item | Pre-filter | Retrieval | Carried | Mechanism, or rejection reason | Quality flags |
|---|---|---|---|---|---|---|---|
| E1 | Federal Reserve Bank of New York S… | [The Pre-FOMC Announcement Drift (Lucca & Moench, 2011, rev. 2012; pub…](https://www.bostonfed.org/-/media/Documents/conference/PDF/Lucca_preFOMCDrift.pdf) | pass | full text (HTML via summarizer) | yes | S&P500 rises on average 49bp in the 24h before scheduled FOMC statement releases; >80% of the 1994-2011 equity premium earned in that window; explana… | none — primary peer-reviewed/central-bank source, numbers d… |
| E2 | Skidmore College faculty mirror (S… | [The Disappearing Pre-FOMC Announcement Drift (Kurov, Wolfe & Gilbert,…](https://www.skidmore.edu/economics/documents/KurovWolfeGilbert-TheDisappearingPre-FOMC-Announce-Drift-200914.pdf) | pass | full text (HTML via summarizer) | yes | Extends Lucca-Moench sample to Dec 2019; the pre-FOMC drift, which BGM (2019) showed was already limited to meetings with a press conference, weakene… | none — peer-reviewed, numbers directly quoted |
| E3 | UC Berkeley Haas faculty mirror (S… | [Stock Returns over the FOMC Cycle (Cieslak, Morse & Vissing-Jorgensen…](https://faculty.haas.berkeley.edu/morse/research/papers/cycle_paper_cieslak_morse_vissingjorgensen.pdf) | pass | full text (HTML via summarizer) | yes | The entire US (and worldwide) equity premium since 1994 is earned in even weeks of FOMC-meeting cycle time (weeks 0,2,4,6 from the last meeting), not… | none in the sections read — this is a Journal of Finance pa… |
| E4 | Wharton faculty mirror (SSRN 13120… | [How Much Do Investors Care About Macroeconomic Risk? Evidence from Sc…](https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/Draft20111128p_edited.pdf) | pass | full text (HTML via summarizer) | yes | Generalizes the FOMC-specific drift to the full scheduled macro calendar: CPI, PPI, employment (NFP), and FOMC decision days all carry an elevated eq… | none — peer-reviewed JFQA paper, numbers directly quoted fr… |
| E5 | CFTC Office of the Chief Economist | [Macro News Announcements and Automated Trading (Haynes & Roberts, 201…](https://www.cftc.gov/sites/default/files/idc/groups/public/@economicanalysis/documents/file/oce_macroannouncement.pdf) | pass | full text (HTML via summarizer) | yes | Directly studies E-mini S&P 500 futures (and 10Y Treasury futures) transaction data around the monthly BLS Employment Situation (NFP) release. Automa… | none — official CFTC Office of the Chief Economist research… |
| E6 | arXiv q-fin.TR 2508.06788 (Takahas… | [Returns and Order Flow Imbalances: Intraday Dynamics and Macroeconomi…](https://arxiv.org/pdf/2508.06788) | pass | full text (HTML via summarizer) | yes | Structural VAR (identified via heteroskedasticity) on S&P 500 E-mini futures BBO data at 1-second frequency within 15-minute windows. Macro news anno… | An earlier WebFetch call on the SAME arXiv abstract URL pro… |
| E7 | SSRN 1958587 (primary) + third-par… | [Calendar Anomalies in Stock Index Futures (Carchano & Pardo)](https://dx.doi.org/10.2139/ssrn.1958587) | pass | blocked | no | Tests turn-of-month, day-of-week, holiday and January effects across multiple stock-index futures markets including the S&P. | retrieval_blocked on both attempted mirrors — logged honest… |
| E8 | paperswithbacktest.com (secondary … | [Closing the Question on the Continuation of Turn-of-the-Month Effects…](https://paperswithbacktest.com/strategies/closing-the-question-on-the-continuation-of-turn-of-the-month-effects-evidence-from-the-s-p-index-futures-contract) | pass | full text (HTML via summarizer) | yes | S&P 500 index futures turn-of-month effect (last session of month + next 3 sessions) tested May 1982-Dec 1999; found to disappear after 1990, attribu… | Secondary/aggregator summary, not primary text — this is ex… |
| E9 | CME Group (cmegroup.com) | [Impact of Economic Indicators on CME Group Markets (whitepaper)](https://www.cmegroup.com/education/files/Economic-Indicators-WhitePaper.pdf) | pass | blocked | no | Exchange-published research on which macro releases (NFP, CPI, PMI, retail sales, FOMC) move which CME product volumes/volatility most. | retrieval_blocked — WebFetch timed out (60s) on all three c… |
| E10 | CME Group OpenMarkets (cmegroup.co… | [Navigating the S&P 500 Rebalance: A Quarterly Market Ritual (2025)](https://www.cmegroup.com/openmarkets/equity-index/2025/Navigating-the-S-P-500-Rebalance-A-Quarterly-Market-Ritual.html) | pass | blocked | no | Exchange commentary on how quarterly S&P 500 reconstitution flow interacts with ES/MES futures trading. | retrieval_blocked, same cmegroup.com timeout issue as above |
| E11 | CME Group (cmegroup.com) | [Managing Month-End Equity Flows and Portfolio Risk (2025)](https://www.cmegroup.com/articles/2025/managing-month-end-equity-flows-and-portfolio-risk.html) | pass | blocked | no | Describes CME's own S&P 500 Month-End futures product, built explicitly around month-end rebalancing flow — evidence the exchange itself treats month… | retrieval_blocked, same cmegroup.com timeout issue |
| E12 | CME Group (cmegroup.com) | Economic Indicators That Most Impact Markets (2025) | pass | not_retrieved | no |  | not attempted after repeated timeouts on the same domain |
| E13 | SSRN / afajof.org | [The Unintended Consequences of Rebalancing (Harvey, Mazzoleni & Melon…](https://afajof.org/management/viewp.php?n=144452) | pass | not_retrieved | no | Predictable equity-bond/index rebalancing flow creates short-term price pressure that can in principle be front-run or faded systematically. | not read in full |
| E14 | arXiv q-fin.TR 2506.21775 | [On the Hidden Costs of Passive Investing](https://arxiv.org/pdf/2506.21775) | pass | snippet only | no | Predictable price pressure around index-reconstitution effective dates from passive funds' mechanical trading; per WebFetch's abstract summary, the a… | Abstract-level summary only, and the underlying instrument … |
| E15 | arXiv q-fin.CP/PR 2606.12872 | Non-Spanning Identification of Scheduled Event Risk in Option Pricing | pass | snippet only | no | Models FOMC/CPI/NFP as deterministic-time jumps in the SPX implied-vol surface. | not fetched in full — relevance judged from abstract snippe… |
| E16 | arXiv | When the Fed Speaks: Dynamics and Forecasts of the Volatility Surface | pass | snippet only | no |  |  |
| E17 | arXiv | Volatility jumps and the classification of monetary policy announceme… | pass | snippet only | no |  |  |
| E18 | arXiv | Co-jumping of Treasury Yield Curve Rates | pass | snippet only | no |  |  |
| E19 | European Central Bank Working Pape… | [Price drift before U.S. macroeconomic news: private information?](https://www.ecb.europa.eu/pub/pdf/scpwps/ecbwp1901.en.pdf) | pass | not_retrieved | no |  |  |
| E20 | arXiv q-fin.ST 2511.06177 | Push-response anomalies in high-frequency S&P 500 price series | reject | — | no | On SPY ETF tick-level momentum/reversal, no calendar-event conditioning at all — belongs to a different (intraday microstructure) family, not exogeno… |  |
| E21 | arXiv q-fin.ST | Forecasting U.S. equity market volatility with attention and sentimen… | reject | — | no | Sentiment/attention-based signal — explicitly forbidden for this session by the task brief, rejected without further reading regardless of relevance. |  |
| E22 | arXiv | Do Prediction Markets Forecast Cryptocurrency Volatility? Evidence fr… | reject | — | no | Crypto instrument — explicitly excluded scope. |  |
| E23 | arXiv | Warp speed price moves: Jumps after earnings announcements | reject | — | no | Single-stock earnings announcements, not an index-level scheduled macro/calendar event and not a futures instrument. |  |
| E24 | arXiv 1802.01393 / 1506.05911 | Seasonal Stochastic Volatility and the Samuelson Effect in Agricultur… | reject | — | no | Commodity-specific mechanics — explicitly excluded scope per the family brief. |  |
| E25 | qoppac.blogspot.com (Robert Carver) | Systems building - futures rolling / seasonality posts | reject | — | no | Search surfaced only commodity-seasonality (Samuelson effect) content, not equity-index scheduled-event content; commodity mechanics are explicitly o… |  |
| E26 | jonathankinlay.com | E-mini tag archive / general HFT scalping posts | reject | — | no | No specific FOMC/CPI/NFP-conditioned post surfaced in search; the archive page itself was not fetched for content, so this is logged as a discovery-l… |  |
| E27 | Quantitative Brokers blog | (no specific post found) | reject | — | no | Search did not surface an accessible QB blog post on scheduled-event execution; logged as an unfound discovery-layer source per the directory's instr… |  |
| E28 | SSRN (via IDEAS/RePEc) | The limits to stock index arbitrage: Examining S&P 500 futures and SP… | reject | — | no | About general index-arbitrage limits/basis dynamics, not conditioned on any exogenous calendar event — belongs to a different mechanism family. |  |
| E29 | ScienceDirect/SSRN | Short-term market reversals and the S&P 500 index option returns (Kaj… | reject | — | no | Options-based short-term reversal, not calendar-event conditioned and not a futures instrument. |  |
| E30 | SSRN/ResearchGate | The S&P 500 index inclusion effect: Evidence from the options market | reject | — | no | Cash-equity index-inclusion effect studied via options, not futures; single-name inclusion/exclusion premia also don't mechanically transfer to an in… |  |
| E31 | CFTC.gov | Limits to Arbitrage and Commodity Index Investment: Front-Running... | reject | — | no | Commodity-index specific — explicitly excluded scope. |  |
| E32 | arXiv 1408.3650 | The Random Walk of High Frequency Trading | reject | — | no | General HFT/random-walk microstructure theory, no calendar-event conditioning. |  |
| E33 | MarketScreener | E-mini S&P 500 futures held flat as traders awaited CPI data | reject | — | no | News wire, not research — single-day market commentary with no methodology. |  |
| E34 | TradingView News | S&P 500 futures add slightly to gains, yields churn after in-line CPI | reject | — | no | News wire, not research. |  |
| E35 | moomoo Community | Small-Cap Futures Lead Rebound Into CPI | reject | — | no | Retail social-forum post, not research. |  |
| E36 | edgeful.com blog | CPI trading strategy: how to trade CPI news releases | reject | — | no | Vendor marketing content with no stated sourcing or methodology. |  |
| E37 | leprivatebanker.com | Emini S&P Futures Retreat as Policy Tightening and AI Caution Collide | reject | — | no | News commentary, not research. |  |
| E38 | Barchart | Tech-led rally E-mini indices climb following CPI and ahead of PPI da… | reject | — | no | News wire, not research. |  |
| E39 | FXEmpire | S&P500 and Nasdaq 100: Payrolls Will Decide if Waller's Rally Gets Fo… | reject | — | no | Opinion/forecast commentary, not research. |  |
| E40 | Blue Line Futures | Nonfarm Payrolls Loom: E-mini S&P and NQ Hold Key Support | reject | — | no | Brokerage marketing blog, discretionary commentary, no methodology. |  |
| E41 | Investing.com | U.S. stock index futures steady with nonfarm payrolls on deck | reject | — | no | News wire, not research. |  |
| E42 | TradeStation / SoFi / StockTitan /… | Quadruple/Triple Witching explainer articles (multiple retail-educati… | reject | — | no | Retail educational content describing the mechanism with no primary data or citable statistics beyond what the Stoll & Whaley literature already esta… |  |
| E43 | Santander Asset Management | Quadruple Witching: When Expiration Becomes a Market Variable (PDF) | reject | — | no | Asset-manager marketing piece, not primary research. |  |
| E44 | Gulf News | 'Quadruple witching' to drive S&P volumes into expiration | reject | — | no | News wire republishing a volume statistic without a citable methodology. |  |
| E45 | SSRN (Stoll & Whaley school; Atlan… | [The Effect of the 'Triple Witching Hour' on Stock Market Volatility (…](https://fraser.stlouisfed.org/files/docs/publications/frbatlreview/pages/67107_1985-1989.pdf) | pass | snippet only | yes | Classic finding: greatly increased last-half-hour volume on expiration Fridays and detectable downward price pressure pre-1987; effect diminished aft… | Not independently pdftotext-verified this session despite b… |
| E46 | Quantpedia (deprioritized per sour… | Turn of the Month in Equity Indexes | pass | snippet only | no |  | vendor screener / paywalled-backtest marketing |
| E47 | CXO Advisory (deprioritized aggreg… | Stock Index Futures Calendar Effects | pass | snippet only | no |  |  |

</details>

### Task 2: formalization

Every trial is a concrete implementation of `strategy/interface.py` under `strategy/research/<family>/`. Its SUPPORT and REFUTE conditions were written into the module docstring before any backtest ran. Each agent used one pre-chosen parameter setting per hypothesis, with no grid search. Directional pairs were pre-registered together, not picked after the fact: A-H2 buy/sell, A-H4 ETH/RTH, B-H1 hold 5/75 and B-H3 breakout/fade.

**Not runnable: C-H4, passive-fill re-specification.** The harness has one fill model, a market order filled at the next bar's open. It has no resting or limit order type, and adding one would mean extending `sim/fill_model.py`, which this session is forbidden to do. It is logged as a hypothesis, not counted as a trial. This matters more than it looks. The reversal family's own sources (Carver 2025) say fast mean reversion survives costs only with passive fills, so family C's three failures are failures of *aggressive* fills specifically.

### Task 3: screening, train dates only

**I verified the numbers rather than trusting them.** I re-ran all 23 trials through the real engine and fill model on fold 0's train dates:
- **17 of 23 reproduce the agents' reported figures to the cent.**
- **All 6 of family B's differ.** B ran without the 2-session roll blackout that families A, C, D and E all applied. Fold 0's train window contains exactly 6 blackout dates, which is exactly the gap (142 vs 136 trades for B-H1). I confirmed this by re-running with and without the blackout. B's code is correct; its run configuration was inconsistent with everyone else's.
- The table uses the blackout-consistent numbers. The correction flips B-H4's fold-0 net from +$47 to −$24; every B verdict is a fail either way.

**No trial passed the robust verdict on its first fold,** so under the prompt's rule none qualified for the 8-fold extension. Instead, I re-ran every trial across the full 289-day train-date union, 2025-04-01 → 2026-05-13, to check that the fold-0 null result was not an artifact of one regime. It was not: **0 of 23 pass robust on the larger sample either.** Measured win probability p and win/loss ratio R were run through `screen("standard", p, R, T, robust=True)`, with T snapped to the nearest grid value in {1, 2, 4}.

| Trial | Pre-registered support condition (abridged) | Fold 0 train: n / p / R / T / net | Robust (fold 0) | 289 train days: n / p / R / net | Robust (289 d) | t-stat | DSR (N=23) |
|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | ROBUST screen() verdict = pass at nearest T grid point (T=1), using measured p/R from the ledger; net long bi… | 136 / 0.493 / 1.12 / 0.96 / $160 | fail | 276 / 0.507 / 1.01 / $141 | fail | 0.20 | 0.000 |
| A-H2 rth close window (buy) | Either direction clears ROBUST screen() pass at nearest T grid (T=1) using measured ledger p/R, replicated ac… | 131 / 0.534 / 1.10 / 0.92 / $800 | fail | 266 / 0.492 / 1.13 / $588 | fail | 0.54 | 0.000 |
| A-H2 rth close window (sell) | Same combined support condition as the buy leg (see above); either direction passing supports the hypothesis. | 131 / 0.435 / 0.84 / 0.92 / $-1,468 | fail | 266 / 0.462 / 0.86 / $-1,956 | fail | -1.78 | 0.000 |
| A-H3 weekend effect | ROBUST screen() pass at nearest T grid, measured p/R from the combined Mon+Fri ledger, stable across all 8 fo… | 53 / 0.434 / 0.70 / 0.37 / $-2,665 | below_grid | 110 / 0.436 / 0.81 / $-4,411 | fail | -1.68 | 0.000 |
| A-H4 eth leg | ETH leg clears ROBUST pass (or shows materially larger measured edge than the RTH leg) at nearest T grid, RTH… | 136 / 0.574 / 0.91 / 0.96 / $1,586 | fail | 277 / 0.552 / 0.94 / $2,550 | fail | 0.88 | 0.000 |
| A-H4 rth leg | Same combined support condition as the ETH leg (see above) — RTH leg passing at a level comparable to or bett… | 136 / 0.522 / 1.13 / 0.96 / $2,642 | fail | 276 / 0.529 / 1.11 / $5,509 | fail | 1.16 | 0.000 |
| B-H1 opening-range breakout (hold 5) | ROBUST screen() verdict = pass at measured p/R/T (never a hand-picked grid point), edge sign matches breakout… | 136 / 0.419 / 0.67 / 0.96 / $-1,096 | below_grid | 276 / 0.438 / 0.85 / $-1,347 | fail | -2.41 | 0.000 |
| B-H1 opening-range breakout (hold 75) | Same as the hold=5 variant. | 136 / 0.507 / 0.89 / 0.96 / $-542 | fail | 276 / 0.533 / 0.86 / $-293 | fail | -0.14 | 0.000 |
| B-H2 prior-day stop cascade | ROBUST verdict = pass at measured p/R/T, edge sign matches break direction, fold-0 pass holds across all 8 tr… | 106 / 0.425 / 1.99 / 0.75 / $680 | fail | 223 / 0.448 / 1.33 / $303 | fail | 0.39 | 0.000 |
| B-H3 breakout leg | Leg-level: same ROBUST-pass + sign-match + fold-stability rule as H1/H2. Horse-race claim: supported only if … | 135 / 0.489 / 0.91 / 0.95 / $-472 | fail | 274 / 0.493 / 0.87 / $-1,186 | fail | -0.96 | 0.000 |
| B-H3 fade leg | Same leg-level and horse-race rules as the breakout leg. | 135 / 0.459 / 1.10 / 0.95 / $-227 | fail | 274 / 0.449 / 1.19 / $-231 | fail | -0.19 | 0.000 |
| B-H4 narrow-range breakout | ROBUST verdict = pass at measured p/R/T; filtered p/R reported alongside H1's for contrast; fold-0 pass holds… | 54 / 0.444 / 1.22 / 0.38 / $-24 | fail | 115 / 0.443 / 1.22 / $-60 | fail | -0.10 | 0.000 |
| C-H1 magnitude-conditioned reversal | Robust screen() verdict == 'pass' with measured p/R (not a grid pick), direction consistent with fading, and … | 19893 / 0.350 / 1.10 / 140.09 / $-55,495 | below_grid | 40743 / 0.361 / 1.09 / $-107,967 | below_grid | -24.46 | 0.000 |
| C-H2 post-spike exhaustion fade | Robust screen() verdict == 'pass' with measured p/R, direction consistent with fading spikes, and survives al… | 4512 / 0.361 / 1.24 / 31.77 / $-8,535 | below_grid | 8829 / 0.365 / 1.12 / $-20,090 | below_grid | -10.15 | 0.000 |
| C-H3 close-location-value reversal | Robust screen() verdict == 'pass' with measured p/R, direction consistent with fading extreme-CLV bars, and s… | 6239 / 0.356 / 1.17 / 43.94 / $-14,054 | below_grid | 12066 / 0.368 / 1.10 / $-29,176 | below_grid | -11.77 | 0.000 |
| D-H1 trailing-vol regime gate | Robust verdict = pass at the nearest T grid point AND p/R are the measured ledger figures AND >=30 closed tri… | 66 / 0.409 / 1.06 / 0.46 / $-117 | fail | 106 / 0.434 / 0.80 / $-304 | fail | -1.73 | 0.000 |
| D-H2 inverse-vol sizing | Robust verdict = pass AND p/R measured from the (now variable-size) trip P&L series AND >=30 trips AND stable… | 135 / 0.415 / 0.97 / 0.95 / $-1,181 | fail | 276 / 0.460 / 0.84 / $-2,320 | fail | -1.96 | 0.000 |
| D-H3 range-compression gate | Robust pass at nearest T grid point AND >=50 closed trips AND a first-fold pass confirmed as robust-pass on a… | 1385 / 0.391 / 1.22 / 9.75 / $-2,683 | below_grid | 2846 / 0.385 / 1.13 / $-8,234 | below_grid | -6.06 | 0.000 |
| D-H4 overnight gap fade | Robust pass at nearest T grid point AND >=30 trips AND stable pass across all 8 folds AND the win/loss patter… | 54 / 0.352 / 0.57 / 0.38 / $-561 | below_grid | 134 / 0.433 / 0.70 / $-843 | below_grid | -2.05 | 0.000 |
| E-H1 scheduled macro drift | ROBUST screen()==pass at the nearest T grid point using MEASURED p/R (not a hand-picked grid point); directio… | 14 / 0.571 / 0.32 / 0.10 / $-915 | below_grid | 31 / 0.484 / 0.69 / $-776 | below_grid | -0.73 | 0.000 |
| E-H2 post-release momentum | ROBUST screen()==pass at the nearest T grid point using MEASURED p/R; first-fold pass surviving all 8 train f… | 11 / 0.455 / 0.86 / 0.08 / $-60 | fail | 25 / 0.480 / 1.04 / $-16 | fail | -0.08 | 0.000 |
| E-H3 quarterly witching short | ROBUST screen()==pass at the nearest T grid point using MEASURED p/R; first-fold pass surviving all 8 folds w… | 2 / 0.000 / — / 0.01 / $-47 | unmeasurable (no wins) | 4 / 0.250 / 1.36 / $-26 | below_grid | -0.65 | 0.000 |
| E-H4 turn-of-month long | ROBUST screen()==pass at the nearest T grid point using MEASURED p/R; first-fold pass surviving all 8 folds w… | 27 / 0.444 / 2.14 / 0.19 / $63 | fail | 55 / 0.436 / 1.26 / $-7 | fail | -0.07 | 0.000 |


- **Reading the table:**
  - **Family C trades 31–141 round turns a day, far above the gate's grid,** which tops out at 4. The T approximation is irrelevant here: all three trials fail on win probability alone (p ≈ 0.36, below the grid's floor of 0.40).
  - **Family E trades 0.01–0.19 a day,** with 4–55 trades over 289 days. These trials are underpowered, not refuted.
  - **`below_grid` means the measured p or R is under the grid's smallest point.** The gate treats that as a fail.

### Task 4: multiple-comparisons accounting

The trial count is **N = 23**: every trial logged, not only the ones that passed, with no parameter search hidden behind it. Without adjustment, testing 23 things against the same train data would make a false pass at a 5% threshold more likely than not: 1 − 0.95²³ ≈ 0.69. The three named corrections below come from `funnel/multiple_comparisons.py`, each checked against hand-computed known answers.

- **Deflated Sharpe Ratio (Bailey & López de Prado 2014), N = 23, applied to daily net P&L over 289 days.**
  - The variance of Sharpe estimates across trials is 0.109, which puts the expected maximum daily Sharpe under the null at 0.649.
  - The best observed daily Sharpe is 0.068 (A-H4 RTH leg, 1.08 annualised).
  - **DSR is 0.000 for every trial.** I recomputed the benchmark from the 20 non-C trials only, which is more generous to the candidates because C's large negative Sharpes widen the variance. The best trial then reaches DSR 0.024, which is still nothing.
  - For contrast, the same trial with no correction for the number of trials tried scores 0.886, short of the 0.95 conventionally used. The deflation is doing real work here; this is not a near miss.
- **Harvey/Liu/Zhu hurdle (t > 3.0, not 2.0).** The best t-stat in the set is 1.16. **No trial clears even the conventional t > 2.0**, let alone 3.0.
- **Probability of backtest overfitting (CSCV, Bailey et al. 2017).** The 8 walk-forward train windows overlap heavily (142 days stepping 21), so they cannot serve as CSCV blocks. **The approximation, stated:** the 289-day train union is cut into 8 contiguous, disjoint 36-day blocks, giving 70 balanced splits (one trailing day dropped).

  | Candidate set | PBO | In-sample winner's mean out-of-sample net | P(in-sample winner is positive out of sample) |
  |---|---|---|---|
  | All 23 trials | 0.143 | +$1,721 | 0.83 |
  | Excluding family C (20) | 0.157 | +$1,721 | 0.83 |
  | Annualised Sharpe > −1 only (13) | 0.157 | +$1,721 | 0.83 |
  | **Also excluding the four unconditional longs (9)** | **0.943** | **−$521** | **0.06** |

  **A low PBO here does not mean edge; it means beta.** In the first three rows the in-sample winner is nearly always the unconditional RTH long, and it stays above the median out of sample for one reason: the research slice rose. `progress.md` (Stage B, Task 2) records a +13.65-tick-per-session long drift in this sample. At $1.25 a tick that alone predicts about $4.0k net across A-H4's 276 RTH sessions after $2.64 round-turn costs. A-H4's RTH leg made $5.5k, which is the same order. Once the unconditional longs A-H1, A-H2 buy and both A-H4 legs are removed, every remaining conditional signal is overfit: the in-sample winner loses out of sample in 94% of splits.

**What this exposes about the gate.** The power gate's null is a zero-edge trader with the drift deliberately removed (Stage B, Task 2). So the gate grades a long-only strategy's market drift as if it were edge. That did not change any verdict here, because nothing passed anyway. But a long-only candidate tested on a trending sample could clear the gate on beta alone. A future session should screen long-only and short-only candidates against a buy-and-hold or drift benchmark, not only the zero-edge null. Building that is harness work, and out of scope here.

### Task 5: ranked shortlist

**The shortlist is empty. No candidate cleared the Task 3 robust verdict, so nothing reached Task 4 as a survivor, and I am not promoting a near miss.** For the record, here is what came closest and why it is not a candidate:
- **A-H4 RTH leg** (long through the RTH session): fails robust; t = 1.16; DSR 0.000; the P&L is the sample's drift.
- **A-H4 ETH leg** (long overnight within the trade date): fails robust; t = 0.88; the same NY Fed drift paper as A-H1 and D-H4; that drift's own authors report it has decayed since 2021 (NY Fed, Liberty Street 2026).
- **B-H2** (prior-day high/low stop-cascade capture): R = 1.99 on fold 0 but p = 0.425, falling to R = 1.33 over 289 days. Fails robust at both sizes; t = 0.39.

There was nothing to converge on too early: no family produced a passer.

### Harness facts this session surfaced (limitations, not fixed)

1. **No position can be held across a trade-date boundary.** `rules/xfa_rules.py` flattens at 15:10 CT and refuses new entries from 15:08 CT, by design. This is the XFA rule, and it is not a defect. A position opened in the evening and held to the morning stays within one trade date and works, as A-H4's ETH leg shows. Multi-day hypotheses cannot be tested as specified, for example the 24-hour pre-FOMC drift and a multi-day turn-of-month hold.
2. **Easy to trip over: holding across a contract splice raises `EngineInvariantError`** instead of returning a graceful refusal, unless `EngineConfig(roll_blackout=roll_blackout_dates(...))` is supplied. Nothing documents that a strategy runner must pass it. That is exactly how family B came to run with a different configuration. A shared screening runner would stop this recurring.
3. **No passive or limit order type** (see C-H4 above).
4. **`power_gate.screen()` covers T in {1, 2, 4} only.** High-frequency families (C) and sparse ones (E) are screened by approximation.
5. **The power-gate null removes drift** (see Task 4).
6. **No order-book data outside the holdout** (both mbp-10 days are sealed) and **no second instrument**. True order-flow and cross-asset lead-lag ideas were untestable; bar-derived proxies stood in for order flow.

### What a future session would need before any candidate could move toward Stage D.2

**Nothing from this session is a Stage D.2 candidate, and I recommend `REGISTRATION.md` stays empty.** That decision is yours. If a further research round is wanted, these are the prerequisites. The harness items need their own properly scoped build session (in the style of Stage C), not a D.1:

1. **A drift or buy-and-hold benchmark alongside the zero-edge null,** so directional candidates cannot pass on beta.
2. **A passive or limit order type in the fill model,** so family C's strongest sourced idea (reversal with passive fills) becomes testable. It will need its own fill-realism caveats: queue position is exactly what the current cost model leaves out.
3. **A shared screening runner that fixes one `EngineConfig`,** including the roll blackout, so families cannot diverge the way B did.
4. **Data, which needs spend and a quote-then-log decision:**
   - order-book days outside the holdout window, for order-flow work;
   - an MNQ or NQ series, for cross-asset lead-lag;
   - a longer history, if the calendar-event family is to escape being underpowered (4–55 trades in 289 days).
5. **Re-screen any new candidate against N = 23 plus however many more trials are tried,** carrying this session's trial count forward, not resetting it. The trials logged here are the starting denominator for the next round.

Artifacts: `strategy/research/` (23 trial implementations plus family helpers), `strategy/research/_lead_accounting.py`, `funnel/multiple_comparisons.py`, `tests/test_multiple_comparisons.py`, `reports/stage_d1_accounting.json`.

## 2026-09-18 — Stage D.1a: harness fixes (drift benchmark, passive fills, shared runner)

### Headline

The three harness gaps Stage D.1 named are closed. Every future screen goes through one call, `screening.screen_candidate(label, factory, window)`; `docs/SCREENING.md` is the whole contract a future prompt needs to point at. Re-running Stage D.1's exact 23 trials through it reproduces every logged figure to the cent and every robust verdict. The four unconditional longs D.1 flagged (A-H1, A-H2 buy, both A-H4 legs) now fail the **drift benchmark itself**, on both sub-checks, on all 9 windows tried: 36 of 36 runs. The regression also surfaced a real defect in my first drift benchmark, fixed below with before/after numbers. No new hypothesis was run, and no verdict changed.

### Guardrails, with evidence

- **Sealed holdout:** `python -m data.holdout status` gave `all_ok: true` and `unlocks_logged: 0` before the session, mid-session (after Task 3) and at the end. Nothing written this session reads `data/sealed`. The runner loads bars only through `data.research_bars`, which refuses holdout rows, and it refuses any window date outside the folds' train dates.
- **`REGISTRATION.md`:** 0 bytes.
- **`live/`, `ops/`:** still empty. No TopstepX or ProjectX reference exists in any file written this session (grep verified).
- **Databento spend: $0.00** of the $10 cap. No data was acquired or quoted; the ledger is unchanged at 72 entries, last written 2026-09-17. Everything ran on the 517,197-bar MES series already on disk.
- **Tests:** 392 pass. That is 364 before, plus 28 new: 13 passive-fill, 9 drift-benchmark, 6 runner. The leakage canaries pass after the harness change. Ruff is clean.

### Task 1 — drift benchmark (`screening/drift.py`, `tests/test_drift_benchmark.py`)

**Reused, not re-derived.** The drift figure comes from Stage B's own calibration: `funnel.null_generator.build_segment_table` + `calibration_summary`. On the 310 research sessions it reproduces **+13.648 ticks/session**, the D.1 figure, and I found no reason to doubt it. Recomputed per fold, as required, it is anything but constant: **+19.5 (fold 0), +8.3, +3.7, +0.8, −5.1 (fold 4), +2.1, +0.0, +9.8 ticks/session**. None is individually significant (|t| ≤ 1.17). What inflates in-sample P&L is realized drift, significant or not.

**Design decision 1: what the benchmark is.** The benchmark is the candidate's own unconditional counterpart, rebuilt from each window's bars:
- It is the window's average price path by minute of the trade date (ETH and RTH).
- Every interval a candidate holds a position is charged what an unconditional position of the same size and sign earned, on average, over the same clock interval.

For a candidate long from the RTH open to the flatten, this is exactly the "hold long through RTH every day" benchmark the prompt names. `session_benchmark` still reports that literal figure and its short mirror.

The literal session-long comparison gets three cases wrong; the exposure-matched form gets them right:
- **ETH exposure.** A-H1 and the A-H4 ETH leg earn *overnight* drift. An RTH-only benchmark cannot attribute it.
- **Shorts.** A short is charged *negative* drift automatically. A short-only rider in a falling window, fold 4 for example, is caught exactly as a long rider is in a rising one. The mirror check is built in; shorts are not exempt.
- **Partial exposure.** A literal "beat buy-and-hold" test fails every market-neutral edge in an up-drifting window and passes any flat strategy in a down-drifting one.

Costs cancel: the counterpart makes the same trips, so the excess is gross.

**Design decision 2: what "clearing" means.** Both conditions are required:
- **(a) Significance.** The mean daily excess over the counterpart is > 0 at **one-sided 95%**. The bound is a percentile stationary block bootstrap, with a mean block of 5 days (the null generator's assumption), 10,000 resamples and a fixed seed, taken over every window date.
- **(b) Sufficiency.** Each trip's drift expectation is subtracted from its net P&L, and the drift-adjusted p/R must still pass the **robust zero-edge power gate**. This is the literal fix for D.1's complaint that "the gate grades drift as edge": the gate now also sees drift-free P&L.

**Why not a simple dominance check.** An unconditional clock strategy's excess over its own counterpart is a mean-zero residual by construction. "Excess > 0" would pass such a strategy about half the time on noise, a coin flip on exactly the case the check exists to catch.

**Why 95% rather than the power gate's 80%.** The power gate's leniency buys power against a stringent funnel null. This check is a plain one-sample test, and at 80% it would pass one drift-plus-noise candidate in five. And nothing below t ≈ 1.645 could survive D.1's Deflated Sharpe accounting at N = 23 anyway, so the stricter level discards nothing viable.

**Stated consequence.** A purely clock-based unconditional hypothesis *cannot* clear this check in-sample, however real its seasonality. Its in-sample P&L *is* the average path. Seasonality claims need out-of-sample persistence, not an in-sample screen. The runner attaches this as a caveat to every report.

**Known-answer tests (all pass), run end to end through the runner with the real engine, cost model and gate:**

| Case | Result |
|---|---|
| Injected drift (+100/+100/−20 ticks/session, mean +60), unconditional long | **The old zero-edge gate alone passes it** (p = 2/3, robust pass): the D.1 failure mode, reproduced. The drift check attributes $4,500 of $4,500 gross to drift (share 1.00), excess $0.00, and fails it. The literal session benchmark reads exactly +60.0 ticks/session. |
| Mirror: falling market, unconditional short | Old gate fooled the same way. Drift charged +$4,500 (negative drift × short), excess $0, fail. Not exempt. |
| Zero drift, genuine conditional signal (a 09:00 signal bar right 8 days in 10; up and down sessions balance minute by minute) | Drift attribution exactly $0. Drift-adjusted p/R identical to raw (p = 0.80). Excess $5,400, significant. Verdict **pass**, with no reasons. Unaffected by the check. |
| Hand-computed attribution | 2 micros, day moves +8 and +4 ticks: charged 1,500¢ per trip; excess +500¢ / −500¢ to the cent. |

**Mutation checks.** Switching attribution off fails 3 tests. Dropping its sign, i.e. charging shorts long drift, fails the short-side test alone, which is the right test to catch that.

**Defect found by the Task 4 regression, fixed, and reported rather than tuned away.** The first version averaged the path over *every* window date. The regression's per-trial table showed a systematic pattern no unconditional strategy should produce: the A-H4 ETH leg was charged *more* drift than its gross on all 9 windows (share 1.37–7.11), and the RTH leg less. I traced it to two measured facts:
1. **All four contract splices in the research slice happen inside a trade date,** at 18:00/19:00 CT, and the continuous series jumps **+206 to +226 ticks** at each one: the roll basis, not a market move. That jump sat inside the ETH path.
2. **The roll-week RTH sessions were sharply negative in this sample.** The Dec-2025 blackout days sum to −516 ticks and Mar-2026's to −339. In fold 6, for example, tradable-day drift is +6.36 ticks/session against +0.03 across all days.

No position can exist on a roll-blackout date, and every splice falls on one. The fix builds the path from **tradable dates only (the canonical roll blackout excluded)**, and adds a guard that raises if a contract change ever appears inside a path day. A regression test pins both.

This is not tuning toward the expected answer. The four flagged trials failed before the fix too, and the fix follows from the two facts above, not from any verdict. The pre-fix output is kept as `reports/stage_d1a_regression_prefix.json`. Across all 74 runs, the fix changed no composite verdict, no drift verdict and no significance result. Five drift-adjusted gate labels moved between `fail` and `below_grid`, both of which are failures: A-H3 and D-H1 on the train union, D-H3 on the train union, A-H1 on fold 2, and the A-H4 ETH leg on fold 5. Afterwards A-H1, A-H2 buy and the A-H4 ETH leg sit at drift share **1.00** on nearly every window, which is the theoretical answer.

**Residuals that remain, explained to the dollar, not fixed.** The A-H4 RTH leg still shows +$4–6/day of excess on folds 2–7. On fold 4, the +$776 total breaks down as:

| Component | Amount | Cause |
|---|---|---|
| 130 normal trips | +$1,023 | On 2025-11-20 the XFA MLL liquidated the position at 10:58, on a day that fell 825 ticks by 15:00. That day's full drop stays in the average the other trips are charged. |
| The liquidated trip | −$634 | |
| Five early-close sessions | +$388 | The path keys on clock minute, so half-days are charged the regular-day morning average. |

The first is path-dependent loss truncation by the account rules; a drift benchmark rightly does not call it drift. The second is a small calendar effect. Neither is near significance (lower bound −$19/day). I stopped here rather than keep adjusting the benchmark.

### Task 2 — passive/limit orders (`sim/fill_model.py`, `sim/engine.py`, `strategy/interface.py`, `tests/test_passive_fills.py`)

**What it models.** `limit_intent(bar, side, qty, limit_price, ttl_bars)` builds a `PassiveIntent`, and `INTERFACE_VERSION` goes to 2. Market strategies are unchanged: all 94 existing engine, fill-model and interface tests pass untouched.

The order is gate-checked at its decision time exactly like a market order, including the roll blackout and position limits.

It rests from the **next** bar, so its own decision bar's range can never fill it. That is a known-answer test.

It fills only when a later bar trades **at least one tick through** the limit, and then at **exactly the limit price**, commission only (61¢ per micro per side, no slippage). A bar that merely touches the limit does not fill it.

Cancellation:
- on `ttl_bars` expiry;
- on a session change or forced flatten;
- if it would add exposure, once the no-new-positions window opens (15:08 CT). Exits still fill there.

A marketable-on-arrival limit (a buy at or above the decision close) is refused by both the constructor and the engine; it is an aggressive order and belongs to `market_intent`.

**Adverse-selection decision: no extra per-fill penalty.** Two reasons:
1. The trade-through rule *is* the adverse-selection model. The fills it keeps are the ones where price went through the level against the order, and the touch-and-bounce fills it drops tend to be the winners. Its net bias is **pessimistic**.
2. The post-fill path comes from the real bars, so a flat penalty on top would count adverse selection twice.

**What it does NOT model**, carried as caveats on every result that used it. The list is `PASSIVE_FILL_CAVEATS`, which the runner attaches automatically whenever a passive fill occurs:
- **Queue position.** Trade-through sidesteps it by assuming a level is exhausted before price trades through it. Implied, hidden or cancelled liquidity can break that assumption.
- **The order's own effect on the market's path.**
- **Volume at the level.** Any trade-through fills the full size.
- **Latency.**

These sit on top of the two-day slippage calibration's existing caveats, which still apply to every market fill.

**Known-answer tests (to the cent):**

| Scenario | Result |
|---|---|
| Buy limit 6000.00, touched at 09:02, traded through at 09:03 | Fill at 6000.00, not the 09:03 open (6000.50), with 61¢ commission and 0 slippage. Market exit at 6002.00 with 61¢ + 63¢. Net **815¢**, matched by `reconstruct_balances`. |
| Price never reaches the limit | No fill; `passive_expired` at exactly decision + ttl. |
| Passive short entry and passive cover, 2 micros | Gross 2,000¢ − 244¢ = **1,756¢**. |
| Passive exit inside the 15:08 window | Fills; net **315¢**. |

Also tested: the decision bar's own trade-through never fills its order; a resting entry is cancelled once the 15:08 window opens; a smuggled marketable `PassiveIntent` is refused by the engine; a roll-blackout passive entry is refused.

**Mutation check:** a touch-fills rule fails 3 tests, including the engine known answer.

**C-H4 was not implemented.** That would be running a new trial, which this session does not do. It is now *testable*: a future session can express it with `limit_intent`.

### Task 3 — shared screening runner (`screening/`, `docs/SCREENING.md`, `tests/test_screening_runner.py`)

`screen_candidate(label, factory, window)` returns a frozen `ScreeningReport`. It carries:
- n / p / R / T and net;
- the exposure class (long_only, short_only, both, none);
- market and passive fill counts;
- the raw zero-edge verdicts, matched and robust;
- the drift-adjusted verdicts and the drift significance block;
- the literal session benchmark;
- `drift_verdict` and a composite `verdict`, which is "pass" only if the robust zero-edge gate AND both drift sub-checks clear;
- one-line reasons, and caveats.

What it hard-codes:
- **One `EngineConfig`** (`canonical_engine_config`): restart on terminal, XFA, mean slippage, hindsight masked, and the roll blackout (splice + 2 sessions, from the vendor schedule). A test pins it equal to the config D.1's lead accounting used, including the 6 blackout dates in fold 0.
- **Train-only windows** (`fold_train_window(i)`, `train_union_window()`). A test-only date is refused.
- **One measurement:** `screening.trips`, promoted from family D's `_metrics.py`, which is now a re-export, so D.1 scripts run unchanged.
- **T snapped to the gate grid, and flagged.**

**Structurally awkward to bypass.** `EngineConfig` now **requires** `roll_blackout` (keyword-only). Omitting it, which was exactly family B's D.1 failure, is now a `TypeError` instead of a silently different result. Synthetic tests pass the explicit, greppable `NO_ROLL_BLACKOUT`; the 17 existing construction sites were updated. `EngineConfig`'s docstring points to the runner. `screen_frame`, the same pipeline on a caller-supplied frame, exists for synthetic tests and is documented as not for research. Python cannot stop someone importing `run_backtest`, but the unsafe omission is gone and the safe path is the documented one.

### Task 4 — regression against Stage D.1's 23 trials (`strategy/research/_d1a_regression.py`, `reports/stage_d1a_regression.json`)

74 runs through `screen_candidate`, 2.4 min on 12 workers:
- 23 trials × {fold 0 train, 289-day train union};
- plus the four flagged trials on folds 1–7.

**0 problems** on every check:
1. **Same numbers:** n / p / R / T / net equal `reports/stage_d1_accounting.json` exactly for all 46 D.1 runs, for example A-H4 RTH fold 0 at 136 / 0.5221 / 1.1286 / $2,641.72. The market-order path is unchanged.
2. **Same verdicts:** each raw robust verdict equals D.1's logged table, including the `below_grid` and `unmeasurable` cells, for all 46. **No trial passes the composite verdict on any window.** All 23 still fail, and none flipped in either direction.
3. **The four flagged trials fail the drift benchmark itself, not merely the zero-edge null**, on all 36 runs (4 trials × 9 windows). Every one fails *both* drift sub-checks: excess not significant, and the drift-adjusted p/R fail the robust gate.

| Trial | Window | Gross | Charged to drift | Drift share | Excess $/day | 95% lower bound $/day | Drift verdict |
|---|---|---|---|---|---|---|---|
| A-H1 european-open drift | fold 0 | $520 | $520 | 1.00 | +0.00 | −6.10 | fail |
| A-H2 close window (buy) | fold 0 | $1,134 | $1,134 | 1.00 | −0.00 | −8.30 | fail |
| A-H4 ETH leg | fold 0 | $1,944 | $1,925 | 0.99 | +0.13 | −19.35 | fail |
| A-H4 RTH leg | fold 0 | $2,992 | $3,107 | 1.04 | −0.81 | −28.93 | fail |
| A-H1 european-open drift | 289-day union | $872 | $872 | 1.00 | +0.00 | −3.86 | fail |
| A-H2 close window (buy) | 289-day union | $1,266 | $1,266 | 1.00 | +0.00 | −6.22 | fail |
| A-H4 ETH leg | 289-day union | $3,279 | $3,439 | 1.05 | −0.56 | −15.98 | fail |
| A-H4 RTH leg | 289-day union | $6,221 | $6,102 | 0.98 | +0.41 | −20.11 | fail |

This is the direct proof D.1 asked for. D.1's closing inference was that "A-H4's RTH leg made $5.5k, which is the drift's order". The benchmark now makes it exact: 98% of that leg's gross over 289 days, and 100% of A-H1's and A-H2's, is what an unconditional position earned over the same clock interval.

**Folds 1–7 (supplementary):**
- A-H1 and A-H2 buy: share 1.00 on every fold.
- A-H4 ETH leg: share 1.00 on folds 1–5, 1.51 and 1.08 on folds 6–7.
- A-H4 RTH leg: share 0.11–3.53, the MLL and early-close residual explained above.
- Every one of the 28 runs fails the drift benchmark.

**The drift check does not blanket-fail everything.** Two conditional trials clear its *significance* sub-check on fold 0:
- **C-H2** (post-spike fade): gross excess significant at a +$1.94/day bound, yet −$8,535 net after costs;
- **E-H4:** +$0.07/day bound.

The zero-edge gate and the drift-adjusted gate still fail both, and over 289 days neither clears significance. That is why (a) alone is not the bar: gross signal beyond drift is necessary, not sufficient.

### Delegation

- **Delegated: one Sonnet `code-reviewer` subagent** for an independent adversarial correctness review of the diff, findings only (results below). Nothing else was delegated, including the known-answer tests.
- **Kept with the lead (Opus):** every design and statistical decision above, all code and tests, the splice/blackout diagnosis and fix, the residual accounting, and this entry.

### Independent review

One Sonnet `code-reviewer` ran adversarially over the diff and traced these by hand:
- passive-fill look-ahead;
- intra-bar fill ordering;
- close-priced fill recovery in the drift attribution;
- trip grouping across account restarts;
- DST collisions in `minute_of_trade_date` (impossible on real data: Globex is closed at every US DST transition).

Result: **0 critical, 0 high, 0 medium, 1 low.**

The low finding: `ENGINE_REFUSAL_ORDER` listed `engine_malformed_passive` before the closure, flatten and blackout refusals. The engine actually checks a passive intent's wrapped order first. The constant has no consumer in the code, but it was misleading, so I reordered it to match the engine's real precedence. The reviewer verdict was APPROVE.

### What a future hypothesis-screening session needs to know

1. **Say "use the shared screening runner (docs/SCREENING.md)"** and nothing else about configuration. Call `screen_candidate(label, factory, fold_train_window(i) | train_union_window())`, pass a zero-argument factory, and read `report.verdict`, `report.reasons` and `report.caveats`.
2. **Do not build `EngineConfig` or call `run_backtest` yourself for screening.** It now refuses to be built without an explicit roll blackout.
3. **A pass now means two things:** robust zero-edge on measured p/R, and the drift benchmark (significant excess over the unconditional counterpart, plus drift-adjusted p/R passing the robust gate).
4. **Pure clock-seasonality hypotheses cannot clear the drift check in-sample.** Do not spend trials on them without an out-of-sample argument.
5. **Passive orders exist** (`limit_intent`). Any result that used them carries `PASSIVE_FILL_CAVEATS`: trade-through fills, no queue position, no market impact. C-H4 (reversal with passive fills) is now expressible. It would be a *new* trial and counts toward N.
6. **Carry N = 23 forward.** Every `screen_candidate` call is a trial.
7. **Still not fixed; out of scope here:**
   - the gate's T grid is {1, 2, 4};
   - positions cannot cross a trade date;
   - no order-book data outside the holdout, and no second instrument.

   Data acquisition remains your decision.

Artifacts:
- **Code:** `screening/` (`runner.py`, `drift.py`, `trips.py`), `sim/fill_model.py` and `sim/engine.py` (passive orders, required `roll_blackout`), `strategy/interface.py` (v2).
- **Tests:** `tests/test_passive_fills.py`, `tests/test_drift_benchmark.py`, `tests/test_screening_runner.py`.
- **Docs:** `docs/SCREENING.md`.
- **Regression:** `strategy/research/_d1a_regression.py`, `reports/stage_d1a_regression.json`, `reports/stage_d1a_regression_prefix.json`.

## 2026-09-18 — Stage D.1b: C-H4 and Family F (next hypothesis round)

### Headline

**The shortlist is still empty. This is the program's second consecutive clean null.**
- **C-H4** (short-horizon reversal with passive fills, trial 24) fails every pre-registered condition. It loses more per trip than its market-fill parent C-H1: −$3.25 against −$2.79.
- **Family F**, the declared-in-advance data-native exploration, computed its 57 declared statistics. The selection rule, fixed before any computation, **admitted zero hypotheses**:
  - every statistically robust directional pattern is worth about 0.1 tick per trade, against a 2.1-tick round-turn cost;
  - every pattern large enough to pay for costs is statistically indistinguishable from noise.
- **The cumulative trial count is therefore N = 24, not 28+.** Across all 24 trials, the best t-stat is still 1.16. DSR is 0.000 for every trial, and at most 0.022 under the most generous variant. The in-sample winner among conditional strategies loses out of sample in 94% of CSCV splits.
- `REGISTRATION.md` stays empty. Nothing here is ready for Stage D.2.

### Guardrails, with evidence

- **Sealed holdout:** `python -m data.holdout status` gave `all_ok: true` and `unlocks_logged: 0` before the session, during it (before the accounting run) and at the end.
  - No file written this session reads `data/sealed` or names an unlock path.
  - The Family F discovery computation loads bars only through `data.research_bars`, and asserts that its dates are a subset of the train union and disjoint from fold 0's train window.
- **`REGISTRATION.md`:** 0 bytes. **`live/`, `ops/`:** empty. No TopstepX or ProjectX reference exists in any file written this session (grep verified).
- **Shared runner only:**
  - Every screening run and every accounting run went through `screen_candidate`. Nothing this session builds an `EngineConfig` or calls `run_backtest`.
  - D.1's `_lead_accounting.py` did both, so it was not reused as a runner. Only its `TRIALS` list is imported.
- **Databento spend: $0.00** of the $10 cap. No data acquired or quoted; the ledger is unchanged, last entry 2026-09-17.
- **Tests:** 403 pass, including the leakage canaries: 392 before this session, plus 1 runner test and 10 C-H4 state-machine tests. Ruff is clean.
- **One harness change, additive:** `ScreeningReport.daily_net_usd` is the net P&L per window date, in window order. The cumulative accounting needs it, and D.1 got the same series by bypassing the runner.
  - A known-answer test pins that it covers every window date, including $0 days, and sums to `net_pnl_usd` to the cent.
  - No verdict logic changed. The D.1 continuity check below reproduces all 23 trials exactly through it.

### Delegation breakdown

| Work | Who | Notes |
|---|---|---|
| C-H4 spec restated from D.1's log (item C7 and `h4_passive_fill_wrapper.py`), choice of H1 as the signal, limit price, exit rule, SUPPORT/REFUTE conditions | **Lead (Opus)** | Written into the subagent prompt before any code existed |
| C-H4 implementation, 10 unit tests, one fold-0 screen | **Sonnet subagent** (general-purpose) | 148k tokens |
| C-H4 code review and independent fold-0 re-run | **Lead** | Reproduced to the cent: 12,770 trips, −$41,538.26 |
| Family F Task 2a: feature list, discovery window, inference plan, selection rule | **Lead** | Written and hashed before any computation |
| Family F Task 2b: raw computation of the 57 declared statistics | **Sonnet subagent** (general-purpose) | 273k tokens |
| Review of that computation; fix of one declared statistic that silently returned n = 0 (F3.3(a), see below) | **Lead** | |
| Family F Task 2c (selection), Task 3 (cumulative accounting: module, run, reading), Task 4, this entry | **Lead** | |

Two subagents in total, both Sonnet, and neither made a statistical or selection judgment.

### Task 1 — C-H4: reversal with passive fills (trial 24)

**Source, reused and not re-derived.**
- Stage D.1 family C, item C7: Carver (2025), "There is no possibility that you would be able to overcome trading costs unless you were passively filled".
- The source Carver cites for his 2–30-minute fast mean reversion: Safari & Schmidhuber (2025, arXiv:2501.16772).
- D.1's logged mechanism: *"any of H1–H3, but specified from the start to require resting/limit-style fills (an order left at or better than the signal bar's close) rather than aggressive market-order fades"*.

**Formalization** (`strategy/research/c_short_horizon_reversal/h4_passive_fill_reversal.py`, interface v2). One pre-chosen setting, no grid:
- **Signal:** identical to C-H1: fade a 5-minute return whose magnitude ranks in the 20th–60th percentile of the trailing 120 one-minute-step values. H1 was chosen as the signal because it is the variant whose source Carver's post directly cites.
- **Entry:** passive. `limit_intent` at the signal close + 1 tick for a sell, − 1 tick for a buy, TTL 5 bars. This is the nearest non-marketable price to "at the close", since a limit *at* the close is refused as marketable.
- **Exit:** passive first. After 5 bars in the position, a limit at close ± 1 tick with TTL 5, and a market flatten if that expires. The whole round turn is passive where possible, which is what Carver's claim requires.
- The magnitude window does not update while an entry order is resting. That is consistent with H1's update-only-when-flat rule; I noted it on review and accepted it.
- **Implementation choices the subagent flagged, all accepted on review:**
  - tick-integer rounding of limit prices;
  - one internal `_exit_attempted` flag, because `AccountView` cannot distinguish "exit due" from "passive exit expired";
  - a refused passive exit is treated like an expired one, so the market fallback follows;
  - unit tests use shortened warm-up parameters, with the TTLs left at production values.

**Pre-registered, before any backtest:**
- **SUPPORT:**
  - the fold-0 composite verdict passes, meaning the robust zero-edge gate AND both drift sub-checks;
  - passive fills > 0, ≥ 30 trips, fade direction intact;
  - then a stable pass across all 8 folds.
- **REFUTE:** any one of:
  - the composite fails;
  - net ≤ $0;
  - net per trip no better than C-H1's market-fill −$2.79 on fold 0, which refutes the specific claim that passive fills rescue this reversal.

**Result, fold 0 train (142 dates): refuted, on all three REFUTE conditions.**

| n trips | trades/day | p | R | net | net/trip | robust | drift | composite |
|---|---|---|---|---|---|---|---|---|
| 12,770 | 89.9 (T snapped to 4) | 0.433 | 0.805 | −$41,538 | −$3.25 | fail | fail (lower bound −$203/day) | **fail** |

- **Fill mix:** 28,434 passive orders placed, 23,403 passive fills, 2,137 market fills (fallback exits).
- **Why it did worse than market fills: gross, not costs.** Roughly $17.1k of the loss is modelled cost: 23.4k passive fills at $0.61, plus 2.1k market fills at about $1.32. That leaves about −$1.9 per trip *gross*, against about −$0.15 per trip for C-H1's market fills.
  - The trade-through rule fills a fade only when price keeps moving through the level against it. That is exactly the adverse selection passive liquidity provision suffers.
  - The rule drops the touch-and-bounce fills, which are the winners, so this result is **pessimistic by construction**.
  - It therefore does not prove that a real resting order with good queue priority would lose. It does show that nothing in 1-minute bars can establish that it would win.
- **8-fold extension: not triggered**, because fold 0 failed. The 289-day union run the accounting needs gives 26,723 trips, −$78,687, composite fail.

**What this result does and does not account for.** These are the `PASSIVE_FILL_CAVEATS`, stated here rather than left to the runner:
1. **Trade-through fill rule on 1-minute OHLC bars.** A limit fills only if a later bar trades at least one tick *through* it, and then at exactly the limit. A touch is not a fill.
2. **Queue position is not modelled.** Trade-through assumes the level is exhausted before price goes through it; implied, hidden or cancelled liquidity can break that.
3. **The order's own market impact is not modelled.**
4. **Volume at the level is not checked.** Any trade-through fills the full size, so partial fills are impossible here.
5. **Latency is not modelled,** neither the decision-to-order delay nor the cancel/replace delay.
6. **No extra adverse-selection penalty is applied.** The trade-through rule and the real post-fill path carry it; the dropped touch fills bias the result pessimistically.
7. **Market fallback exits use the two-day slippage calibration,** which is a lower bound on cost (its days are inside the sealed holdout; it excludes latency and adverse selection). Commission is $0.61 per side per micro, still to be confirmed at checkout.

### Task 2a — Family F declared feature space (logged before computation)

**`reports/stage_d1b_family_f_declaration.md`, sha256 `9c17c508c50ee66e37fc471136368c4b364922bc16437f7d9f0b5d860314448d`, written 2026-09-18T20:17:00Z.** That was before the computation script existed. Only the column schema and the fold construction were consulted to write it. Not committed mid-session (no commit was requested), so the hash plus the file's mtime is the evidence; the file is unchanged since, and its hash is recorded in the output JSON's meta. In summary:

- **Discovery (EDA) window:** the 147 train-union dates *not* in fold 0's train window, 2025-10-17 → 2026-05-13, minus 8 excluded dates (6 roll-blackout, 4 vendor-degraded, 2 of them overlapping), leaving 139 dates.
  - **Why:** Task 2d screens on fold 0 first, and discovery never saw fold 0's dates, so that screen would have been out-of-sample relative to discovery.
- **The declared features, 57 tested statistics:**
  - **F1** return autocorrelation, h ∈ {1, 5, 15, 30, 60} min, and variance ratios, RTH and ETH (18);
  - **F2** volatility clustering, daily RV persistence, leverage asymmetry, vol-tercile-conditioned 15-min autocorrelation (12);
  - **F3** 30-min bucket-to-bucket return correlations across RTH (12), plus intraday momentum in the Gao-Han-Li-Zhou / Baltussen form (2), plus descriptive bucket moments;
  - **F4** crossings of the RTH open and the prior close, gap-fill by gap tercile, and round-number (×50, ×100) continuation versus control levels (7);
  - **F5** relative-volume- and trend-efficiency-conditioned autocorrelation, range-per-volume residual (5);
  - **F6** the 08:30 open's position inside the overnight range (1). Added beyond the prompt's starting list, before computation: the overnight range is a data-native reference no family used.
- **Inference:** a stationary day-block bootstrap (mean block 5, 2,000 resamples), Benjamini–Hochberg at FDR 10% across all 57, sign agreement in ≥ 3 of 4 sub-blocks, and an implied gross edge in ticks for every directional statistic.
- **Selection rule for Task 2c** (fixed in the same file): directional, AND BH-significant, AND sub-block-stable, AND implied edge ≥ 2.11 ticks per trade (≥ 0.98 only if the hypothesis is specified with passive entry and exit), AND not an already-screened A–E mechanism. If nothing qualifies, zero hypotheses.

### Task 2b — stylized facts (`reports/stage_d1b_family_f_facts.json`)

No signals, no P&L, no `strategy/interface.py`. The code is `strategy/research/f_data_native/_stylized_facts.py`, and 21 implementation choices are logged verbatim in the JSON.

**Two deviations found on the lead's review, both logged:**
1. **F3.3(a) silently returned n = 0.** The subagent computed the declared "first bar → 09:00 CT" return with its generic window routine. That routine requires a valid step *into* the first bar, which always crosses the daily halt, and a gap-free overnight. I replaced it with the literal statistic (first bar's close to the 08:59 CT bar's close, same instrument), which gives n = 134, and re-ran. This is a bug fix to a declared statistic, not a new one. Every other statistic is unchanged; the computation is deterministic.
2. **F3.1 (descriptive bucket moments) covers the 13 RTH buckets only.** The declaration said every bucket of the trade date. It is descriptive and ineligible by declaration, so it cannot affect selection; noted, not re-run.

**What the data say (EDA dates, 139 days):**

| Feature | Finding | BH (10%) | Sub-blocks agreeing | Implied gross edge | Novel? |
|---|---|---|---|---|---|
| F1.1 1-min autocorr, RTH | −0.023 [−0.044, −0.002] | no (p .034) | 3/4 | 0.12 ticks for a fade | No: family C's region |
| F1.1 other horizons | all \|ρ\| ≤ 0.05, all CIs span 0 | no | — | ≤ 0.8 ticks | — |
| **F1.2 VR(5), RTH** | **0.930 [0.897, 0.972]**: mild mean reversion at 1–5 min | **yes** | 4/4 | about 0.1 tick (via F1.1) | No: C-H1/C-H3/C-H4's mechanism |
| **F1.2 VR(60), ETH** | **0.851 [0.773, 0.911]**: overnight mean reversion within the hour | **yes** | 4/4 | ≤ 0.08 tick (via ETH F1.1 h ≤ 30) | Partly: no ETH reversal trial existed |
| F2.1 \|r\| autocorr, lags 1–60 min | +0.19 to +0.33, RTH and ETH | yes (8/8) | 4/4 | non-directional | Textbook volatility clustering |
| F2.2 daily RV persistence | +0.50 [0.31, 0.62] | yes | 4/4 | non-directional | Textbook; used by D-H1/D-H2 |
| F2.3 leverage asymmetry | −0.114 [−0.202, −0.025]: down half-hours → higher next vol | yes | 4/4 | predicts vol, not side | Textbook |
| F2.4 vol-tercile 15-min autocorr | ±0.02, CIs span 0 | no | 3/4 | −0.2 to −1.3 ticks | Near D-H1 |
| F3.2 bucket → next bucket (12 pairs) | ρ from −0.19 to +0.16, all CIs span 0 | no (best p .099) | 2–4/4 | −7.6 to +4.2 ticks | New conditioning |
| F3.3 intraday momentum (a) overnight→close, (b) first 30 min→close | −0.056 (p .53); −0.110 (p .22). Sign is *reversal*, the opposite of the literature's momentum | no | 3/4 | −5.0; −6.3 ticks | Literature (A10/A28), never screened |
| F4.1 / F4.2 RTH-open / prior-close crossing | −3.5 / −1.0 ticks per 15 min, CIs span 0 | no | 3/4, 2/4 | −3.5, −1.0 | Near B |
| F4.3 gap fill by \|gap\| tercile | 95% / 58% / 30% of gaps fill | yes (3/3) | 4/4 | ineligible by declaration | **D-H4's mechanism; replication, not discovery.** D-H4 still failed |
| F4.4 round numbers vs control | ×50: −1.7 ticks (p .31); ×100: −4.6 (p .073) | no | 2/4, 3/4 | −0.5, −3.4 | New |
| F5.1–F5.3 volume/range conditioning | \|ρ\| ≤ 0.05, all CIs span 0 | no | 2–3/4 | ≤ 1.1 ticks | New |
| F6.1 open's position in the overnight range | +0.017 (p .84) | no | 2/4 | 6.6 ticks (noise) | New |

**Descriptive:** RTH 30-min bucket returns are fat-tailed (excess kurtosis up to 9.7), with bucket means indistinguishable from zero. That is clock seasonality, ineligible by declaration.

### Task 2c — hypotheses formalized: **zero**

I applied the rule exactly as declared.
- **Survives BH:** 15 of 57. Of these, 12 are ineligible by declaration (F2.1 ×8, F2.2, F4.3 ×3); F2.3 predicts volatility, not direction; and 2 remain eligible through a directional reading: VR(5) RTH and VR(60) ETH.
- **Fails the economics:** both remaining facts are real but tiny.
  - The fades they imply earn about 0.12 ticks (RTH, from F1.1 h1) and at most 0.08 ticks (ETH, F1.1 h ≤ 30) per trade, gross. The bar is 2.11 ticks at market, or 0.98 passive.
  - Being 18× short of the market bar is not a near miss.
  - VR(5) RTH is also C-H1/C-H3/C-H4's mechanism, and C-H4 has just shown that even passive fills do not rescue it.
- **Not selected, ranked by the size of the implied edge.** All are large enough to pay for costs, and none is statistically distinguishable from zero:

  | Statistic | Implied edge | p |
  |---|---|---|
  | F3.2 bucket 07→08 | −7.6 ticks | .27 |
  | F6.1 | +6.6 ticks | .84 |
  | F3.3(b) | −6.3 ticks | .22 |
  | F3.2 bucket 08→09 | −6.2 ticks | .099 |
  | F3.3(a) | −5.0 ticks | .53 |
  | F4.4 ×100 | −4.6 ticks | .073 |
  | F3.2 bucket 01→02 | +4.2 ticks | .37 |
  | F3.2 bucket 10→11 | +3.7 ticks | .18 |
  | F4.1 | −3.5 ticks | .21 |
  | F3.2 buckets 02→03, 05→06, 04→05, 06→07, 12→13 | 2.4–3.1 ticks | .26–.81 |

  - The smallest p among them is .073, and the BH threshold at that rank is about .03.
  - Formalizing any of them would be testing noise that happens to be large. That is precisely what the rule exists to stop, and each would have added one to N.

**Consequence:** Task 2d had nothing to screen, so zero Family F trials were run and N rises by 1 (C-H4), not by up to 7. The cap of 6 was never binding, so no justification for exceeding it arises.

**Ideas for a future round (not computed; from the subagent and the lead):**
- a direction-split gap fill (up-gaps vs down-gaps);
- why short-lag \|r\| clustering is stronger in ETH;
- where ETH's variance ratio crosses from above 1 to below 1;
- whether F3.2's mid-morning bucket pattern aligns with the 09:00/10:00 CT release slots, which would make it an E-family question.

None of these gets formalized without new data: every one of them was generated from the discovery dates.

### Task 3 — cumulative multiple-comparisons accounting (`strategy/research/_d1b_accounting.py`, `reports/stage_d1b_accounting.json`)

**Continuity first.** All 23 D.1 trials were re-run through `screen_candidate` on the 289-day train union and reproduce D.1's net P&L to the cent, and each daily-series Sharpe to 1e-6: **0 problems.** So this is D.1's accounting carried forward, not a new one. The whole run took 83 s on 12 workers.

**N = 24**: D.1's 23 plus C-H4. No Family F hypothesis was formalized, so none enters the count. As a sensitivity, N is also widened by Family F's 57 EDA statistics.

- **Deflated Sharpe Ratio (daily net P&L, 289 days):**

  | Variant | N | Sharpe variance across trials | Expected max daily Sharpe under null | Best observed (A-H4 RTH, 0.068) → DSR |
  |---|---|---|---|---|
  | Cumulative, all 24 | 24 | 0.143 (up from 0.109, driven by C-H4's −1.15) | 0.750 | **0.000** |
  | Variance excluding family C (most generous) | 24 | 0.0085 | 0.182 | **0.022** (D.1: 0.024 at N = 23) |
  | Sensitivity: N + 57 EDA statistics | 81 | 0.143 | 0.930 | **0.000** |

  - **C-H4:** daily Sharpe −1.15, t = −19.5; DSR 0.000 under every N, including uncorrected (N = 1). There is no "significant against this session's small count" artefact to catch, because nothing in this session is positive.
  - **Judged against this session's trials alone:** C-H4 is the only new trial, so a this-session-only DSR/PBO is degenerate (1 strategy) and is reported as undefined, not as 0.
- **Harvey/Liu/Zhu:** the best t-stat across all 24 is **1.16** (A-H4 RTH leg, drift-explained per D.1a). No trial clears t > 2.0, let alone 3.0.
- **PBO (CSCV, 8 contiguous 36-day blocks of the train union, 70 splits; D.1's approximation, unchanged):**

  | Candidate set | PBO | In-sample winner's mean OOS net | P(winner positive OOS) |
  |---|---|---|---|
  | All 24 | 0.129 | +$1,721 | 0.83 |
  | Excluding family C (20) | 0.157 | +$1,721 | 0.83 |
  | **Excluding the four unconditional longs (20)** | **0.400** | **−$521** | **0.06** |

  - As in D.1, a low PBO with the longs included is beta, not edge. The winner is the drift-riding RTH long, which D.1a showed is 98% drift.
  - With the longs removed, the conditional winner loses out of sample in **94% of splits**, the same as D.1.
  - This set has 20 strategies, where D.1's comparable row had 9: D.1 also dropped family C and trials with annualised Sharpe below −1. That makes this PBO 0.400 instead of D.1's 0.943; the winner's out-of-sample record is identical.
- **8-fold stability extension: not applicable.** No candidate cleared the robust verdict and the drift benchmark.

### Task 4 — shortlist (updated, not reset)

**Still empty.** Nothing cleared the Task 3 bar; nothing came close. For the record, the closest remain D.1's A-H4 legs and B-H2. The A-H4 legs are drift, per D.1a. B-H2 fails robust with t = 0.39. Nothing new joins them. No single winner, no D.2 readiness, and `REGISTRATION.md` is untouched. That decision remains the user's.

### Should the program keep searching? A question for the user, stated plainly

Two consecutive clean nulls, 24 trials, and a declared data-native sweep that found no tradable-magnitude structure are, in my judgment, **a signal worth discussing before another round**, not a reason for a third round of the same kind:

- **What has been searched:**
  - 1-minute MES bars only;
  - 289 train days, April 2025 → May 2026;
  - retail micro-contract costs (about 2.1 ticks per round turn at market);
  - intraday-only holding (the XFA flatten);
  - literature across 5 families, plus a declared EDA.
- **What the searches agree on:**
  - the robust structure in these bars is real but small: short-lag mean reversion (VR 0.85–0.93), volatility clustering, gap-fill base rates;
  - it is an order of magnitude below cost;
  - passive execution does not rescue it under a realistic, pessimistic fill rule;
  - everything big enough to trade is noise at this sample size.
- **What another round like this would buy:** more trials against the same 289 days. That raises N, lowers every future candidate's DSR, and consumes train data that cannot be un-seen. The sealed holdout stays safe, but the train set is increasingly mined.
- **The options, and I recommend the user choose rather than defaulting to "search more":**
  - **(a) Pause strategy search on this data.** Accept that 1-minute MES bars at micro-contract costs do not show an intraday edge findable by these methods.
  - **(b) A scoped data decision** (spend, quote-then-log), each item named in D.1/D.1a:
    - order-book days outside the holdout, for order flow and a realistic queue-position fill model, the one thing that could overturn C-H4's pessimistic verdict;
    - MNQ/NQ, for cross-asset structure;
    - a longer history, which gives power for the ranked-but-noisy Family F patterns and the calendar family.

    Any new round on new data would still carry N = 24 forward.
  - **(c) Revisit the constraint set,** since the XFA intraday flatten rules out every multi-day effect in the literature. That is a program-scope question, not a research one.

Artifacts:
- **Code:**
  - `strategy/research/c_short_horizon_reversal/h4_passive_fill_reversal.py`;
  - `strategy/research/_d1b_ch4_fold0.py`;
  - `strategy/research/f_data_native/` (`_stylized_facts.py`, and `trials.py`, which is deliberately empty);
  - `strategy/research/_d1b_accounting.py`;
  - `screening/runner.py` (`daily_net_usd`).
- **Tests:** `tests/test_c_h4_passive_reversal.py`, `tests/test_screening_runner.py`.
- **Reports:** `reports/stage_d1b_family_f_declaration.md`, `reports/stage_d1b_family_f_facts.json`, `reports/stage_d1b_ch4_fold0.json`, `reports/stage_d1b_accounting.json`.
- **Docs:** `docs/STAGES.md`, `docs/SCREENING.md` (N = 24).

## 2026-09-18 — Stage D.1c: constraint audit (XFA flatten and the excluded hypothesis space)

### Headline

**This is a decision brief, not a decision.** Three findings change how Stage D.1b's closing option (c) ("revisit the constraint set") reads:

1. **The flatten rule is encoded correctly, and it applies to every Topstep account type, including the LFA.** Topstep's help center, checked today, still says: no new positions from 15:08 CT; flat by 15:10 CT; 15 minutes before any CME early close. The holiday article names the Combine, the XFA and the LFA explicitly. **Reaching the LFA would therefore not unlock multi-day holding.** It would also remove API automation, which the LFA does not support. The premise that "moving to the LFA gives access to multi-day strategies" is false on current documentation.
2. **None of the three other prop firms checked allows overnight holding either.** Lucid (flat by 16:45 ET), MyFundedFutures (auto-close 16:10 ET) and Tradeify (flat by 16:45 ET, from a secondary source only) all require a daily flat, and none of them exempts its live tier. Among the venues on record, only trading personal capital (IBKR) removes the constraint.
3. **The pre-filter excluded almost nothing on horizon grounds.**
   - Of Stage D.1's 102 pre-filter rejections, **0 were rejected mainly for being multi-day.** Horizon appears as a contributing reason in 3, and each of those 3 also had another reason that would have excluded it on its own.
   - The constraint worked **upstream, through search scope.** All five D.1 families were defined as intraday mechanisms, and Family F declared only returns formed within one trade date. As a result, multi-day literature was searched for only when it surfaced incidentally.
   - Among the 81 items that passed the pre-filter, **12 make a claim whose core is multi-day, and 7 make one that crosses the daily close.** Among the 41 carried forward, those figures are 6 and 5.
   - **No near miss from D.1/D.1b failed because of the flatten.** Every one failed on cost, drift (beta), adverse selection or statistical power.

`rules/xfa_rules.py` is unchanged. `REGISTRATION.md` is 0 bytes. No backtest ran, no data was requested ($0.00), and no code was written.

### Guardrails, with evidence

- **Sealed holdout:** `uv run python -m data.holdout status` gave `all_ok: true`, `unlocks_logged: 0` and `research_has_no_holdout_rows: true` at the start of the session and again at the end.
- **No TopstepX API contact.** This session read only public help-center and marketing pages, fetched anonymously. `live/`, `ops/` and credentials were not touched. `live/` and `ops/` are still empty.
- **No backtest, no engine, no screening runner.** Nothing under `sim/`, `screening/` or `strategy/` was run or edited. Databento spend was **$0.00**, and nothing was quoted.
- **No code change.** The only files written are this entry and one line in `docs/STAGES.md`.

### Delegation

**None.** The prompt named Task 1 and Task 2 as candidates for delegation. I ran both inline:
- **Task 1** needed seven page fetches, plus raw-HTML extraction so the rule text could be quoted verbatim.
- **Task 2's** source was already in context: D.1's untruncated literature log (`all_results.json` in the D.1 session's workflow output). progress.md shows that log only in truncated form, so the table there was not enough for this task.

A subagent would have had to re-derive both. **Task 3 is lead-only, as the prompt requires.**

### Task 1: the flatten rule, reconfirmed against Topstep's help center (2026-09-18)

**Verbatim text,** taken from the pages' raw HTML rather than a summarizer, so these are exact quotes:

- *"When and What Products Can I Trade?"* (help.topstep.com article 8284206, dated 2026-07-13, the same revision `rules/xfa_rules.py` cites):
  - "Topstep is a day trading program. All positions must be closed by 3:10 PM CT every weekday. You can resume trading at 5:00 PM CT. No swing trading."
  - "[All open positions and pending orders] begin to automatically cancel at 3:10 PM CST. Avoid opening new positions after 3:08 PM CT — Risk Managers begin flattening at that time. It's still your responsibility to be flat by 3:10 PM CT."
  - "If you're trading a product with an earlier daily close than 3:10 PM CT, you must exit before that product's close." The earlier-closing products are CBOT grains (1:20 PM CT) and CME livestock (1:05 PM CT). None of them affects MES.
  - "Can I swing trade or hold positions overnight? No. All positions must be closed by 3:10 PM CT each weekday. Topstep does not permit holding positions from one session to the next."
- *"Topstep Holiday Trading Hours"* (article 13350348, marked "Updated today"):
  - "All account types must close positions 15 minutes before any early close."
  - "Applies to: Trading Combine®, Express Funded Account® (XFA), Live Funded Account® (LFA)."
- *"Live Funded Account Parameters"* (article 10657969, marked "Updated yesterday"): "The API Gateway is built for the simulated environment and isn't available on Live, so automated strategies are not possible at this time in the Live Funded Account."
- *topstep.com/live-funded-account-rules:* "All positions MUST be closed prior to 3:10 PM CT or prior to the market close of that product, whichever is sooner."

**What this means for each question the prompt asked:**

| Question | Answer |
|---|---|
| Does the encoded 15:08 no-new / 15:10 flatten / 15-min-early rule still match? | **Yes, exactly.** The Hours article is the same 2026-07-13 revision that was read on 2026-09-16. The 2026 holiday table matches every cutoff that `data/cme_calendar.py` plus `flatten_time_ct()` produce, including Good Friday (08:15 halt → 08:00), the 12:00 halts (→ 11:45) and the 12:15 closes (→ 12:00). |
| Does the flatten differ by stage (Combine / XFA / LFA)? | **No.** The holiday article lists all three account types by name. The LFA rules page states the same 15:10 CT close, and no page describes an LFA exemption. |
| Is there any account type, product or exception that allows an overnight or multi-day position? | **None found.** "No swing trading" and "does not permit holding positions from one session to the next" are unqualified statements. The only product-level variation moves the close *earlier* (grains, livestock), never later. |

**Discrepancies.** None of these is material. All go to Stage A.2 for confirmation on a real account:

1. **The no-new-positions cutoff on early-close days is our extrapolation.** Topstep states only the close-by time (for example, 11:45 CT). The code also blocks new entries 2 minutes before that (11:43 CT), carrying over the normal-day 15:08/15:10 gap. That is stricter, not looser, so it can only cost trades.
2. **Topstep's own text mixes "3:10 PM CST" and "3:10 PM CT".** In September, CST would literally mean 16:10 CDT. The code uses America/Chicago local time, and the "CT" reading is the one used everywhere else on the page. This looks like a typo on Topstep's side and needs confirming.
3. **The live-only Juneteenth 2026 cutoff was 11:10 CT, against 11:45 CT for simulated accounts.** It is in the past, and XFA accounts are simulated, so the encoded 11:45 was right for the XFA. It shows that live and simulated holiday cutoffs *can* differ.
4. **The LFA marketing page describes the auto-flatten as "about ten seconds before the trading session ends (3:10 PM CT)".** The help center says Risk Managers begin at 3:08. This is a wording inconsistency, and it concerns the LFA only.
5. **Only the LFA follows CME's "blended trade date" protocol for the daily loss limit around holidays.** This does not affect the XFA engine.

**Effect on Task 3's framing: large, in one direction.** Every Topstep stage, the LFA included, is intraday-only. So the LFA is not a path to multi-day strategies in any form.

### Task 2: catalog of the excluded hypothesis space

**Source:** D.1's untruncated Task 1 output (`~/.claude/projects/…/432f46d4…/d1/all_results.json`, 183 items across 5 families; the counts match progress.md's table exactly), the 24 trial docstrings under `strategy/research/`, and `reports/stage_d1b_family_f_declaration.md`.

**A note on "overnight".** "Overnight" does not mean "excluded". A CME trade date runs from 17:00 CT on the prior evening to about 15:10 CT under the flatten. Most of the overnight session is therefore holdable. What is excluded is:
- any position held across **15:10 → 17:00 CT**: the last RTH minutes, the post-close hour and the daily halt/reopen gap;
- any position held across more than one trade date.

This is why A-H1 (02:00–03:00 ET) tested its source's claim in full, while A-H4's ETH leg did not.

**(a) Pre-filter rejections (D.1 Task 1): 0 of 102 rejected mainly on horizon.**

| Item | Rejected mainly for | Horizon also cited? |
|---|---|---|
| A24 Benzinga, S&P semiannual seasonality | news/opinion, not research | yes: "semiannual/monthly … rather than session-clock" |
| C12 Quantpedia, short-term reversal with futures | weekly cross-sectional factor across 24 mixed futures (a multi-asset factor, not equity-index) | yes: "not intraday minutes-to-hour" |
| C17 Quantitativo, volume shocks and overnight returns | cash equity, not futures | yes: "overnight/close-to-open framing" |

- The other 99 were rejected for asset class (crypto, FX, commodities, cash-equity cross-section), for being vendor or news content, or as discovery dead ends.
- **C20** (the NY Fed overnight-drift paper, rejected in family C) was a duplicate handed to family A, where it was carried forward as A2. It was not excluded.
- **Fraction excluded at the pre-filter because of horizon: 0/102 (0%)** as the main reason, and **3/102 (2.9%)** as a contributing reason. In none of the 3 did the horizon change the outcome.

**Caveat on that number: it measures the wrong stage.**
- The family briefs in D.1's workflow (`stage_d1.js`) scoped every search as intraday:
  - A: "deterministic intraday periodicity";
  - C: "minutes-to-an-hour";
  - B and D: intraday levels and states;
  - E: calendar events, which are the only family that did not specify a horizon.
- The briefs never mention the flatten. The exclusion happened when the families were designed, before any source was found. Its size **cannot be counted from the log**, because searches that were never run left no entries.
- Multi-day literature (time-series momentum, multi-day trend-following, carry, month-end flow) appears in the log only where it surfaced incidentally.

**(b) Sources that passed the pre-filter but make a multi-day or cross-close claim: 19 of 81 passed, 11 of 41 carried forward.**

*Core claim is multi-day (12 passed, 6 carried).* Of these, none was tested as specified:

| Item | Carried | Claim | What happened to it |
|---|---|---|---|
| B6 Carver, breakout rule | yes | position within a 10–320 business-day range (figures come from a summarizer, [unverified]) | **never formalized.** Family B built only intraday level breaks |
| C6 Safari & Schmidhuber (2025) | yes | S&P and other futures **revert below ~a few hours and trend from there to ~a few years** | only the minute-scale reversion was used (C-H1–H4); the multi-day trend regime was set aside |
| C7 Carver, "very slow mean reversion" | yes | the post is about multi-year slow mean reversion; fast (2–30 min) mean reversion is a side topic | only the fast part was used (C-H4) |
| D15 Vol targeting and trend following | yes | trend following with volatility-scaled size | only the vol-scaling part was used (D-H2) |
| E3 Cieslak, Morse & Vissing-Jorgensen | yes | the equity premium is earned in even weeks of the FOMC cycle | **never formalized** |
| E8 Turn-of-month, S&P futures | yes | a 4-session hold across month-end | tested only as the degraded E-H4 (see below) |
| E7 Carchano & Pardo; E11 CME month-end flows; E13 Harvey et al., rebalancing; E14 passive reconstitution; E46, E47 calendar aggregators | no | multi-day calendar and flow effects | blocked, snippet-only or deprioritized, so never read in full |

*Core claim crosses the daily close; testable only truncated (7 passed, 5 carried):*
- **A4** Bondarenko & Muravyev, close-to-open;
- **A6** Cooper, Cliff & Gulen, and **A7** Kelly & Clark, both close-to-open on cash equities and ETFs;
- **A9** day-of-week effects, close-to-close;
- **E1** Lucca & Moench, the 24-hour pre-FOMC window;
- **E2** Kurov et al., the same window;
- **E4** Savor & Wilson, announcement-day close-to-close returns.

**(c) Trials tested in a truncated form their source does not support: 4 of 24.**

| Trial | Source claim | What the harness tested | Truncation |
|---|---|---|---|
| **E-H1** scheduled macro drift | 24-hour pre-FOMC drift (E1) | from the trade date's 17:00 CT open to the release, about 14.5–20 hours | declared up front as a "harness-compatibility adaptation" in the docstring |
| **E-H4** turn of month | a continuous 4-session hold (E8) | independent single-session longs on each target day | declared up front as "a meaningfully weaker claim"; the literal claim is untestable |
| **A-H4 ETH leg** | overnight return, close to open (A4–A7) | 17:00 CT → 08:30 CT | misses 15:00 → 17:00 CT (the post-close hour plus the halt/reopen gap); **not declared** |
| **A-H3** weekend effect | classic Monday/Friday effect measured close-to-close, so it includes the weekend gap (A9 lineage) | RTH-only Monday short / Friday long | the weekend itself is not held; reframed as RTH-only in the docstring; **the gap is not declared** |

The other 20 trials are intraday by construction and fully faithful to their sources on horizon. That includes A-H1 (its window lies inside one trade date) and D-H4 (the gap is its conditioning variable; the trade itself is intraday).

**(d) Family F's 57 statistics.**
- Every return statistic was formed within one trade date; the declaration says so (line 23).
- The only statistic that crosses days, **F2.2** daily realized-variance persistence, is non-directional and was ineligible by declaration.
- So **Family F's null covers intraday horizons only.** It says nothing about multi-day return predictability, because it never measured any.

**(e) Near misses: would removing the flatten plausibly change the verdict?**

| Finding | Why it failed | Is the flatten relevant? |
|---|---|---|
| F1.1/F1.2 short-lag mean reversion (VR(5) 0.930 RTH, VR(60) 0.851 ETH) | worth 0.08–0.12 ticks per trade against a 2.11-tick cost | **No.** A 1–60-minute effect is not larger when held longer. Per C6, longer horizons flip to *trend*, which would be a different hypothesis, not this one rescued. |
| C-H4 passive-fill reversal | adverse selection under the trade-through fill rule: about −$1.9 per trip gross | **No.** The bottleneck is fill realism and the missing book data. |
| A-H4 RTH / A-H1 / A-H2 buy / A-H4 ETH (unconditional longs) | the P&L is market drift (beta); all four fail the drift benchmark in 36/36 runs | **No, for the edge question.** Holding longer captures more drift, which the drift benchmark subtracts. |
| A-H4 ETH truncation specifically | the same drift failure | **Marginal and unmeasured.** It adds about 2 of roughly 23 session hours, for a drift its own source reports as decayed to near zero in 2021–25 (A3). |
| B-H2 prior-day stop cascade | p = 0.425, t = 0.39 | **No.** It is an intraday mechanism. |
| E-H1 macro drift | 31 trades in 289 days (underpowered); the drift was reported to disappear after 2016 (E2) | **Partly.** The flatten cut the window to 14.5–20 of 24 hours, but power and decay would bind first. |
| E-H4 turn of month | 55 trades; the source reports the effect disappeared after 1990 | **Partly.** The literal test becomes possible, but power and decay remain. |
| F3.2 / F3.3 / F4.4 / F6.1 (large but noisy, p ≥ .073) | sample size | **No.** These are intraday patterns; the bottleneck is data length. |

**Summary of Task 2.**
- **No tested near miss was killed by the flatten.** Its cost lies entirely in *untested* space: multi-day trend (C6, B6, D15), the FOMC cycle (E3), multi-session calendar and flow effects (E8, E11, E13, E14), and literal close-to-close forms of the day-of-week and FOMC claims.
- **The strongest evidence in the log that this space matters** is C6's regime map, which places trend-following at multi-day horizons and reversion at intraday horizons. The latter is exactly the regime D.1b measured and found below cost.
- **But C6 is a pooled regression across 24 futures, not an after-cost S&P result.** No source in the log demonstrates a multi-day MES edge net of costs.

### Task 3: decision brief (lead only)

**1. What the constraint actually excludes, quantified.**

| Measure | Figure |
|---|---|
| Pre-filter rejections due mainly to horizon | **0 of 102** (3 contributing, none decisive) |
| Passed sources with a multi-day or cross-close core claim | **19 of 81** (23%); **11 of 41** carried forward (27%) |
| Carried-forward multi-day sources never formalized in any form | **3** (B6, D15, E3), plus the multi-day halves of C6 and C7 |
| Trials run in truncated form | **4 of 24** (2 declared, 2 not) |
| Near misses whose failure is attributable to the flatten | **0** |
| Search scope excluded before any source was seen | **not countable.** Every D.1 family was scoped intraday, and the searches that were never run left no record |

On the measured evidence, **the flatten did not cause any observed failure.** The premise in D.1b's closing section, that the flatten "rules out every multi-day effect in the literature", is accurate as a description of the constraint. But it is not evidence that those effects would survive costs on MES: no source in the log shows that. What the constraint cost the program is an **unexamined region** of hypothesis space, whose most relevant marker is C6. It is not a lost result.

**2. What relaxing it would require: the options, as tradeoffs.**

**Option A: stay on Topstep and reach the LFA.**
- **Horizon:** no change. The LFA flattens at 15:10 CT like every other Topstep account (Task 1). It does not relax the constraint at all.
- **Automation:** the LFA has none ("automated strategies are not possible at this time"). The program as built could not run there.
- **Access:** the LFA is a call-up at Topstep's discretion (docs/DECISIONS.md models it as a terminal event), not a tier a trader selects.
- **Net:** on current documentation this is **not a route to multi-day strategies.** Its only relevance is as the eventual call-up event that ends automation, which is already the modelled assumption.

**Option B: a second prop firm with different flatten rules.**
- **What is known:**
  - The earlier session's second-firm comparison **is not stored anywhere on disk.** I searched this repo, every sibling repo under `~/Documents/GitHub/` and every saved Claude Code transcript; no file mentions Lucid, MyFundedFutures or Tradeify apart from this session's prompt.
  - What *is* recorded, in docs/DECISIONS.md: Topstep was chosen as "the only futures prop firm with native REST/WebSocket API; Tradovate blocks API on prop accounts; Apex bans automation outright".
- **What was checked today** (flatten only; automation policy was *not* re-researched):

  | Firm | Daily flat requirement | Overnight on any tier? | Source grade |
  |---|---|---|---|
  | Lucid | "All positions must be closed by 4:45 PM EST, Monday through Friday"; "Swing trading is not allowed in the new LucidLive accounts" | no | help center, verbatim |
  | MyFundedFutures | "any open positions will be automatically closed at 4:10 PM EST"; the live FAQ says the same for live accounts | no | help center, verbatim |
  | Tradeify | flat by 4:45 PM ET on all account types, including Live | no | **secondary only**: the help center returned HTTP 403 |

- **Net:** none of the three firms relaxes the horizon constraint. Lucid's and Tradeify's 16:45 ET cutoffs are 35 minutes later than Topstep's, but still before the 17:00 ET halt, so no position can cross a trade date at any of them.
  - Firms outside these three were not examined, so this is not a claim about the whole prop-firm market.
  - Whether any of the three permits API automation was not re-checked. The DECISIONS.md record implies that Tradovate-routed firms block it.

**Option C: trade personal capital through IBKR.**
- **Horizon:** the constraint is removed entirely. There is no flatten, MLL, consistency rule, payout cap or profit split.
- **Capital:** it reopens the sizing problem. The prompt's figures, **a minimum of about $5,000–$6,000 against a stated pool of at most $6,000 and a preferred size under $2,500**, come from the earlier chat analysis. I could not find that analysis on disk and did not re-derive it. This session has not verified these figures.
- **What is on record elsewhere:**
  - HFExperiment established IBKR Canada as the only broker reachable for this operator's residency with an order-placing API, and recorded, on the operator's own statement of 2026-08-28, that a funded live IBKR account exists.
  - Futures permissions on that account were not checked this session.
  - MBTExperiment's `REINTRODUCTION.md` records a program rule relevant here: **a capital ceiling chosen after seeing the margin figure is "reverse-engineered, whatever the intent".** Any sizing decision should be registered on risk grounds first.
- **The economics change in kind:**
  - On a prop account, the downside is capped at fees and the capital is the firm's.
  - On personal capital, the whole stake is at risk, but the upside is uncapped and unsplit.
  - Per-trade cost (about 2.1 ticks round turn) weighs much less against a multi-day move than against an intraday one. That is the mechanism by which a longer horizon *could* help. It is also paid for in larger overnight gap risk, which has no firm-side stop.
- **What building it would take** (not built; out of scope under the scope lock):
  - an IBKR execution adapter;
  - a risk layer replacing the XFA rules;
  - a harness that can hold positions across trade dates (today the engine enforces the XFA flatten);
  - multi-day research that carries **N = 24** forward.
- **Data:** multi-day hypotheses are **far less powered** on the current 17.5-month history, which gives about 290 daily observations and about 60 weekly ones. A useful multi-day search would almost certainly need a longer history, which means a Databento spend decision.

**Option D: stay intraday-only and treat the result as an informative negative.**
- **What it says:** 24 trials, a declared data-native sweep and three independent statistical corrections agree. The structure robustly present in intraday 1-minute MES bars is an order of magnitude below retail micro costs, and everything large enough to trade is noise at this sample size.
- **What it keeps:** the whole built stack stays valid: rules engine, funnel, harness, runner and sealed holdout. It needs no new venue, capital or code.
- **What it leaves open:** it can still be combined with D.1b's option (b), new data for intraday work (order-book days outside the holdout, MNQ/NQ, a longer history), without touching the constraint.
- **What it gives up:** it closes the multi-day region without having looked at it, so the program's negative stays scoped to "intraday, at these costs" and does not generalize beyond that.

**3. This session is not choosing between these.** The questions below are the ones whose answers would decide it. They are listed in no particular order.

1. **Is the goal specifically a *prop-firm* program, or a *systematic MES* program that happens to have started on a prop firm?** Options A and B keep the first; only C changes the second. On today's evidence, A and B do not relax the horizon constraint.
2. **Is manual trading on the LFA something you would want to do at all?** On current documentation it would be manual *and* still intraday-only.
3. **Is the IBKR capital-sizing problem still binding at today's savings?** Is the "$6,000 max / under $2,500 preferred" pool still the right frame? Following the MBTExperiment precedent, would you register a risk-based capital rule *before* seeing any margin figure?
4. **Should the earlier second-firm and IBKR analyses be put on disk,** so the next session can re-read them instead of relying on the prompt's summary? They are not in any repository or transcript on this machine.
5. **Is a multi-day search worth its prerequisites?** Those are: a harness change so positions can cross trade dates, a longer-history data purchase, and N = 24 carried forward. Or is the unexamined region acceptable to leave closed?
6. **Is "intraday MES at micro-contract costs shows no findable edge" a result you would accept as the program's conclusion** if option D is chosen, or would that feel premature before D.1b's option (b), new intraday data?
7. **Should another prop firm be examined beyond the three checked here?** Or is "no researched firm allows overnight holding" enough to set option B aside?

### What this session did not do

It made no code changes. It did not touch `rules/xfa_rules.py`, `live/`, `ops/` or any adapter. It ran no backtest and no hypothesis test, spent no data, did not write to `REGISTRATION.md` and made no TopstepX API contact. The holdout was never unlocked (`unlocks_logged: 0`). It makes no recommendation.

