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
