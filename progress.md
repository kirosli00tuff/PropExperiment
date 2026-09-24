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

Artifacts: this entry; `docs/STAGES.md` (one line). Working files in the session scratchpad: raw HTML of the help-center pages and `items.tsv`, the 183-item extract (not committed).

## 2026-09-21 — Stage D.1d: multi-timeframe audit and bounded coarser-bar sweep

### Headline

**The shortlist is still empty. This is the program's third consecutive clean null, and it closes the resolution-mismatch question.**
- **Task 1:** 7 of the 24 trials were tested at a finer resolution than their cited source specifies. All 7 flags trace to two sources: Mesfin (2026), whose MNQ study runs entirely on 5-minute bars, and the daily-regime claims behind D-H1/D-H2, which the originals measured with an 11-minute half-life on 1-minute returns. Five adversarial verifiers upheld every flag and every non-flag.
- **Task 3, re-tests:** all 7 re-tests at the source's own grid fail the composite verdict on fold 0 and on the 289-day train union. Nothing passed, so no fold extension ran.
- **Task 3, sweep:** the declared Family G sweep computed its 28 statistics at 5, 15, 30 and 60-minute bars. **Zero survive Benjamini–Hochberg** (smallest p = .020 against a rank-1 threshold of .0036), so zero hypotheses were formalized, exactly as the declaration allowed for. Every fact large enough to pay for costs (8 of 28, at 2.9–10.1 ticks) has p ≥ .02 on 112–319 events.
- **Task 4:** cumulative **N = 31** (24 + 7). The prior 24 trials reproduce D.1b's accounting to the cent and to 1e-6 in daily Sharpe. DSR is 0.000 for every trial (0.003 at best under the most generous variant); the best t-stat is still 1.16; with the unconditional longs removed, the in-sample winner loses out of sample in 96% of CSCV splits.
- `REGISTRATION.md` stays empty. Nothing here is ready for Stage D.2.

### Guardrails, with evidence

- **Sealed holdout:** `uv run python -m data.holdout status` gave `all_ok: true`, `unlocks_logged: 0`, `research_has_no_holdout_rows: true` at the start, after the sweep, and at the end. Every D.1d module loads bars only through `data.research_bars` (statistics) or the shared runner (screens); `grep -rniE "unlock|data/sealed|topstepx|projectx"` over the new code finds nothing.
- **Databento spend: $0.00.** No request, no quote. The ledger is unchanged: 72 entries, last written 2026-09-16.
- **`REGISTRATION.md`:** 0 bytes. **`live/`, `ops/`:** empty. **`rules/xfa_rules.py`, `sim/`, `screening/`, `data/`, `funnel/`:** unchanged against HEAD.
- **No bar or position spans a boundary:** every coarse bar lies inside one ETH or RTH segment of one trade date, ends at or before the no-new-positions time, and is dropped rather than truncated at 08:30, 15:00, an early close or the halt (declaration rules R2–R7). Every D.1d strategy closes its own position by 15:00 CT; the Fable review found no forced flatten in any traced run.
- **Shared runner only:** every screen and every accounting run went through `screen_candidate`. Nothing this session builds an `EngineConfig`.
- **Tests:** 509 pass, 1 xfail, up from 403: 27 resampler, 35 re-test and 44 Family G known-answer tests, all written against the declaration rather than the implementation's output. Ruff is clean. The xfail is documented below.
- **Declared before computed:** `reports/stage_d1d_timeframe_declaration.md`, sha256 `07a906328a2aae2097ae30ea02e5b547cf37247245e1cd91b63808809619c745`, written 2026-09-21T23:01:09Z and made read-only before any computation module existed (`strategy/research/g_timeframe/` was created afterwards). The sweep script refuses to run if the file's hash changes, and the hash is embedded in every output JSON's meta. Nothing was added to either list after hashing.

### Delegation breakdown, and what did not go to plan

The prompt was written for ultracode with four per-timeframe workstreams. The session ran differently, and the record should say so:

| Work | Who | Tokens | Outcome |
|---|---|---|---|
| Task 1 audit, families A–E (5 Opus auditors + 5 verifiers) | subagents | 744k, mostly lost | **The account's weekly limit killed 5 of 6 agents mid-run.** Only family A's audit finished; its verifier never ran. |
| Task 1 audit, families B–E; two primary sources re-read (Mesfin PDF → `pdftotext`; Carver raw HTML) | **lead** | — | done inline, in `reports/stage_d1d_horizon_audit.md` |
| Task 1 adversarial verification, one Opus refuter per family (A–E) | subagents | 784k (with the next row) | all 24 verdicts' flags upheld; three descriptive corrections applied (below) |
| Resampler known-answer tests | 1 Opus subagent | | 27 tests; one latent divergence found (below) |
| Task 2 declaration; the resampler, the 7 re-tests, the Family G sweep, the runners, the accounting; every run; selection; this entry | **lead** | — | The four timeframes ran as four forked processes of one shared module, each writing its own result file, not as four subagents: after the first workflow died on the limit, and once the user said the plan was now Pro, one resampler shared by all four was safer than four agents re-deriving it. |
| Declaration-conformance review: does the code implement exactly the hashed rules? | 1 **Fable** subagent, effort xhigh | 687k (with the next row) | **"results trustworthy as computed"**; six LOW findings (below); it re-implemented G1–G5 from the declaration and reproduced all 28 statistics to 1e-9 |
| Re-test and Family G known-answer tests | 2 Opus subagents | | 35 + 44 tests; one latent re-test defect found and fixed (below) |

Model tiers followed the user's mid-session instruction: Fable for the hard logic (the review), Opus for regular work (audits, tests), the lead on Fable. No haiku or sonnet was used.

### Task 1 — horizon-resolution audit of the 24 trials (`reports/stage_d1d_horizon_audit.md`)

Evidence: D.1's untruncated `all_results.json`, each module's code, and two primary re-reads. Verdicts: **FAITHFUL** (matches, or a clock window that a 1-minute grid represents exactly); **RESOLUTION_MISMATCH** (source ≥ 5 min, trial finer); **SOURCE_SILENT**; **NON-RESOLUTION** (differs for a non-bar-size reason: flatten or window definition, D.1c's scope). A flag needs a mismatch plus a plausible understatement mechanism.

| Trial | Source horizon | Tested | Verdict | Flag |
|---|---|---|---|---|
| A-H1 | 02:00–03:00 ET clock hour | fills at the 02:00/03:00 ET opens | FAITHFUL | |
| A-H2 buy / sell | last 30 min, 15:30–16:00 ET | fills at 15:30/16:00 ET | FAITHFUL | |
| A-H3 | JKM's Monday seasonal is in the **open-to-close** return | one session open-to-close | FAITHFUL (amended; see below) | |
| A-H4 eth | close-to-open, 16:00 → 09:30 ET | 17:01 CT fill → 08:30 CT | NON-RESOLUTION | |
| A-H4 rth | 09:30–16:00 ET | same | FAITHFUL | |
| **B-H1 hold 5 / hold 75** | Mesfin: 5-min bars, OR = "the first six five-minute bars", bar+1 / bar+15 | OR15 on 1-min bars, 1-min close-through trigger | **RESOLUTION_MISMATCH** | **yes → 5 min** |
| B-H2 | transaction-level stop execution (finer than 1 min) | 1-min close-through | FAITHFUL | |
| **B-H3 breakout / fade** | Mesfin §4.1 (5-min bars) | OR30 on 1-min bars, 1-min trigger | **RESOLUTION_MISMATCH** | **yes → 5 min** |
| B-H4 | no intraday resolution stated for the contraction measure | 1-min | SOURCE_SILENT | |
| C-H1 | Safari & Schmidhuber: minute data | 5-min return on a 1-min grid | FAITHFUL | |
| **C-H2** | Mesfin §4.2: 5-min bars, 20-bar baseline, bar+1 | 1-min bars, 60-bar baseline, hold 2 | **RESOLUTION_MISMATCH** | **yes → 5 min** |
| C-H3 | no sourced horizon for the CLV construction | 1-min | SOURCE_SILENT | |
| **D-H1** | a daily vol regime ("today predicts tomorrow") | EWMA λ 0.94 on 1-min returns: ≈ 11-min half-life | **RESOLUTION_MISMATCH** (signal window) | **yes → daily V from 5-min returns** |
| **D-H2** | Carver: "vol targets using the last month or so of returns" (exact) | same 11-min half-life | **RESOLUTION_MISMATCH** (signal window) | **yes → daily V** |
| D-H3 | Bookmap narrative, no timeframe | 1-min | SOURCE_SILENT | |
| D-H4 | SR 917's overnight window | the 1-hour halt gap (≈49 h on Mondays); flat by 17:31 CT, never inside the source's 02:00–03:00 ET | NON-RESOLUTION (a different variable; **new relative to D.1c**) | |
| E-H1 | 24 h pre-FOMC | truncated at 17:00 CT | NON-RESOLUTION (D.1c) | |
| E-H2 | discovery within ~1 min, normalising over 5–15 min | 5-min window, 10-min hold | FAITHFUL | |
| E-H3 | last half hour of witching Friday | 14:30–15:00 CT | FAITHFUL | |
| E-H4 | a 4-session hold | single sessions | NON-RESOLUTION (D.1c) | |
| C-H4 | as C-H1 | C-H1's signal, passive fills | FAITHFUL | |

**Counts:** FAITHFUL 10, RESOLUTION_MISMATCH 7 (all flagged), SOURCE_SILENT 3, NON-RESOLUTION 4. **Every flag maps to the 5-minute grid**; no cited source specifies a 15-, 30- or 60-minute bar, so the coarser workstreams carried no re-tests.

**Verification (after the declaration was hashed, so it could not widen the list).** Five Opus verifiers, one per family, re-derived every row and tried to refute it both ways. Every flag and every re-test grid was upheld, and every Mesfin and Carver string in quotation marks was found verbatim. Three descriptive corrections were applied and are recorded in the audit file's amendments section: **A-H3** relabelled NON-RESOLUTION → FAITHFUL, because JKM (fetched, p. 31) locate their significant Monday seasonal in the open-to-close return the trial holds, and the "weekend gap" rationale carried from D.1c is Rogalski (1984)'s cash-equity finding, which JKM cite but do not reproduce (medium confidence: the module's docstring names French 1980, under which close-to-close would be right); **A-H4 ETH** fills at 17:01 CT, not 17:00; **D-H4** also spans the weekend closure, and its "16:00 → 09:30 ET" horizon was the lead's reconstruction, not a log quote. The verifier's sharpest challenge, that D-H4's 17.5-hour source window forced to 1 hour is the same species of error as D-H1/D-H2, was rejected: the trial's variable is disjoint from the source's effect window and sometimes coarser than it, so no bar-size change repairs it, whereas lengthening D-H1/D-H2's estimator on the same bars does.

### Task 2 — declaration (`reports/stage_d1d_timeframe_declaration.md`, sha256 `07a90632…19c745`, 2026-09-21T23:01:09Z)

Fixed before any computation code existed, in the Family F format:
- **Resampling rule R1–R7.** Session minute 0 = 17:00 CT. ETH = [17:00, 08:30), RTH = [08:30, 15:00), both capped at the no-new-positions time (15:08 CT; 17 minutes before a CME early close, read from the bar's own `early_halt_ct` only on the trade date's own calendar day). A slot exists only if it ends at or before its segment's end: dropped, never truncated or extended, so the 60-minute stubs 08:00–08:30 and 14:30–15:00 do not exist, and nothing crosses the halt, the flatten or a trade date. Missing minutes keep a bar; two instrument ids drop it. A bar completes at the decision time of its last minute, or late on the next bar if that minute is missing. One shared module (`strategy/research/g_timeframe/resample.py`) serves the statistics (vectorised) and the strategies (bar by bar), and the two are pinned identical.
- **The 7 re-tests RT1–RT7**, one per flagged trial, changing only horizon-bearing parameters, each taking the source's value where the source states one: RT1/RT2 = B-H1 with OR = six 5-minute bars and bar+1 / bar+15 holds; RT3/RT4 = B-H3's legs on the same grid with the original 30-minute hold; RT5 = C-H2 on 5-minute bars with Mesfin's 20-bar baseline and bar+1 hold; RT6/RT7 = D-H1/D-H2 with V measured per trade date (an EWMA at the original λ over daily means of squared 5-minute returns). Thresholds, buffers, sides, base entries and one-entry-per-session unchanged. SUPPORT/REFUTE in the C-H4 form.
- **Family G, M = 28 tested statistics:** G1 large-body follow-through (RTH, ETH), G2 session-extreme breakout (RTH, ETH), G3 opening-range breakout held to the RTH end, G4 VWAP-deviation continuation/reversion, G5 overnight-range break; each at 5, 15, 30 and 60 minutes; each an event statistic whose value is the mean signed next-bar move in ticks, so the statistic **is** the implied gross edge. G0 (coarse-bar lag-1 autocorrelation) is descriptive only: Family F's F1.1 already measured it at these horizons and found nothing. G1.RTH.5, G1.ETH.5 and G3.RTH.5 are counted but ineligible: they are the re-tests' own mechanism on the re-tests' own grid.
- **Selection rule:** eligible, BH-significant at FDR 10% across this session's 28 only, ≥ 3 of 4 sub-blocks agree, **|edge| ≥ 2.11 ticks** (the $2.64 modelled market round turn; the 0.98-tick passive bar is unavailable because every G template is a market-order template), ≥ 30 events. **The cost bar does not change with the timeframe:** fewer trades per day at 60 minutes cost statistical power, not cost per trade. Cap: 8 across all four timeframes.
- **Inference:** Family F's `compute_result`, imported unchanged (day-block bootstrap, seed 20260918, 2,000 resamples, mean block 5; percentile CI; two-sided p; sub-blocks 35/35/35/34 of the same 139 EDA dates). Stated plainly in the file: those dates are not fresh, and the discipline preserved is F's, that anything formalized is screened first on fold 0, which discovery never saw.

### Task 3 — re-tests: all 7 fail on both windows (`reports/stage_d1d_retests.json`)

Fold 0 train (142 dates) and the 289-day train union, through `screen_candidate`. Every composite verdict is **fail**: the robust zero-edge gate fails or is below grid in every case, and the drift benchmark's 95% lower bound is negative in every case. The original's figures on the same window are from `reports/stage_d1_accounting.json`.

| Re-test | Window | n / T / p / R | Net (per trip) | Robust | Original: n / p / R / net (per trip) |
|---|---|---|---|---|---|
| RT1 B-H1, 5-min ORB, bar+1 | fold 0 | 134 / 0.94 / 0.485 / 0.82 | −$349 (−$2.60) | fail | 136 / 0.419 / 0.67 / −$1,096 (−$8.06) |
| | union | 273 / 0.94 / 0.480 / 0.93 | −$478 (−$1.75) | fail | 276 / 0.438 / 0.85 / −$1,347 (−$4.88) |
| RT2 B-H1, 5-min ORB, bar+15 | fold 0 | 134 / 0.94 / 0.515 / 0.67 | −$1,711 (−$12.77) | below_grid | 136 / 0.507 / 0.89 / −$542 (−$3.99) |
| | union | 273 / 0.94 / 0.538 / 0.71 | −$2,002 (−$7.33) | below_grid | 276 / 0.533 / 0.86 / −$293 (−$1.06) |
| RT3 B-H3 breakout, 5-min | fold 0 | 134 / 0.94 / 0.575 / 0.68 | −$338 (−$2.52) | below_grid | 135 / 0.489 / 0.91 / −$472 (−$3.50) |
| | union | 273 / 0.94 / 0.535 / 0.76 | −$975 (−$3.57) | fail | 274 / 0.493 / 0.87 / −$1,186 (−$4.33) |
| RT4 B-H3 fade, 5-min | fold 0 | 134 / 0.94 / 0.410 / 1.31 | −$355 (−$2.65) | fail | 135 / 0.459 / 1.10 / −$227 (−$1.68) |
| | union | 273 / 0.94 / 0.432 / 1.23 | −$437 (−$1.60) | fail | 274 / 0.449 / 1.19 / −$231 (−$0.84) |
| RT5 C-H2 spike fade, 5-min | fold 0 | 1,444 / 10.2 / 0.401 / 0.91 | −$5,717 (−$3.96) | fail | 4,512 / 0.361 / 1.24 / −$8,535 (−$1.89) |
| | union | 2,824 / 9.8 / 0.411 / 0.91 | −$10,475 (−$3.71) | fail | 8,829 / 0.365 / 1.12 / −$20,090 (−$2.28) |
| RT6 D-H1, daily-V gate | fold 0 | 102 / 0.72 / 0.373 / 1.30 | −$160 (−$1.57) | below_grid | 66 / 0.409 / 1.06 / −$117 (−$1.78) |
| | union | 134 / 0.46 / 0.396 / 1.19 | −$217 (−$1.62) | below_grid | 106 / 0.434 / 0.80 / −$304 (−$2.87) |
| RT7 D-H2, daily-V sizing | fold 0 | 116 / 0.82 / 0.397 / 1.14 | −$385 (−$3.32) | below_grid | 135 / 0.415 / 0.97 / −$1,181 (−$8.75) |
| | union | 257 / 0.89 / 0.455 / 0.91 | −$1,070 (−$4.16) | fail | 276 / 0.460 / 0.84 / −$2,320 (−$8.41) |

**Reading the table, as the declaration's resolution-effect rule requires:** "resolution understated the effect" is supported only where a re-test passes. None does, so it is supported for **none** of the 7. Direction of change, reported as such and nothing more: the per-trip loss shrank for RT1, RT3, RT6 and RT7 and grew for RT2, RT4 and RT5. The 5-minute close-through trigger did what the audit said it plausibly might, raising B-H1's win probability from 0.42 to 0.49, but the win/loss ratio fell with it; Mesfin's 75-minute hold, marginally positive on MNQ at his costs, is the worst row here (p 0.52, R 0.67, −$12.77 per trip). RT5's 5-minute spike population is a third the size of the 1-minute one and loses more per trip, which is Mesfin's own §4.2 finding on MNQ, reproduced on MES: the post-expansion reversal is real, but not capturable at a next-bar-open entry net of cost. RT1–RT4 share one trigger by construction (the source's six-bar range), so their four rows differ only in hold and side.

### Task 3 — Family G sweep: 28 statistics, zero survive (`reports/stage_d1d_family_g_facts.json`, per-timeframe files `…_5m/15m/30m/60m.json`)

- **Resampling, descriptive:** on the 139 EDA dates, 25,847 / 8,615 / 4,307 / 2,084 ETH bars and 10,607 / 3,533 / 1,766 / 816 RTH bars at 5/15/30/60 minutes; bars with a missing minute are 0.01%–0.10% of ETH and 0% of RTH. Zero late completions at any timeframe.
- **G0 continuity:** the coarse-bar lag-1 autocorrelation equals Family F's F1.1 **to four decimals at every ETH timeframe** (e.g. +0.0093 at 5 min, −0.0515 at 15, −0.0381 at 30, +0.0493 at 60). RTH differs slightly (0.0151 vs 0.0144 at 5 min; −0.013 vs −0.039 at 60), and the review traced that to a definition, not to the resampler: F1.1's first RTH window spans the 08:29 → 08:30 step and G0's does not, so F has one more return per day.
- **The 28 tested statistics, top of the p-ordering:**

  | Statistic | n events | Edge (ticks) [95% CI] | p | Sub-blocks | Selection |
  |---|---|---|---|---|---|
  | G2.RTH.30 session-extreme breakout | 319 | **+5.19** [+0.73, +9.65] | .020 | 3/4 | not BH-significant (threshold .0036) |
  | G1.RTH.5 large-body follow-through | 1,789 | +0.88 [+0.07, +1.76] | .034 | 4/4 | ineligible (RT5's grid); and below cost |
  | G2.ETH.30 | 598 | −1.62 [−3.90, +0.32] | .124 | 3/4 | not significant |
  | G2.ETH.5 | 1,328 | −0.49 | .137 | 3/4 | not significant |
  | G5.RTH.15 overnight-range break | 129 | −4.02 [−11.2, +2.9] | .239 | 4/4 | not significant |
  | G5.RTH.30 | 124 | +4.52 | .283 | 2/4 | not significant |
  | G3.RTH.15 ORB held to the close | 138 | −10.08 | .452 | 3/4 | not significant |
  | remaining 21 | 112–4,405 | −4.6 to +2.9 | .44–.98 | | not significant |

- **The same split as Family F, one level coarser.** Eight statistics clear the 2.11-tick cost bar (2.9–10.1 ticks); their p-values are .020–.888 on 112–319 events. Everything with a small p (G1.RTH.5 at 0.88 ticks) is below cost. **Zero BH-significant, zero qualify, zero formalized**, and `G_TRIALS` is empty. No hypothesis was screened, so the sweep adds nothing to N.
- **What the near-miss is worth noting for:** G2.RTH.30, a 30-minute close beyond the session's earlier extreme, is worth +5.2 ticks on the next 30-minute bar with a CI that excludes zero, but it is one of 28 tests, its sub-blocks read +4.2 / −0.6 / +6.3 / +10.0, and the rule this session fixed in advance says it is not distinguishable from noise at this multiplicity. It is logged, not promoted, and it would need new data to be looked at again.

### Task 4 — cumulative accounting (`strategy/research/_d1d_accounting.py`, `reports/stage_d1d_accounting.json`)

**Continuity first: 0 problems.** All 24 prior trials re-run through the runner on the train union reproduce `reports/stage_d1b_accounting.json` to the cent and each daily Sharpe to 1e-6. **N = 31**: 24 + 7 re-tests + 0 Family G.

| Variant | N | Sharpe variance | E[max daily Sharpe under null] | Best DSR |
|---|---|---|---|---|
| Cumulative, all 31 | 31 | 0.117 | 0.713 | **0.000** |
| Variance excluding family C (most generous) | 31 | 0.011 | 0.223 | **0.003** (A-H4 RTH, drift-explained per D.1a) |
| This session only | 7 | 0.018 | 0.185 | **0.0004** (RT4) |
| This session, uncorrected (N = 1) | 1 | — | — | 0.38 (RT4), 0.22, 0.20, 0.18, 0.15, 0.07, 0.00 |
| Sensitivity: N + 57 F + 28 G EDA statistics | 116 | 0.117 | 0.882 | **0.000** |

- **Harvey/Liu/Zhu:** the best t-stat across all 31 is still **1.16** (A-H4 RTH). All seven new trials have negative t-stats (RT5: −7.3). Nothing clears t > 2.0, let alone 3.0.
- **PBO (CSCV, 8 contiguous 36-day blocks, 70 splits):**

  | Candidate set | PBO | In-sample winner's mean OOS net | P(winner positive OOS) |
  |---|---|---|---|
  | All 31 | 0.129 | +$1,721 | 0.83 |
  | Excluding family C (27) | 0.143 | +$1,721 | 0.83 |
  | **Excluding the four unconditional longs (27)** | **0.671** | **−$960** | **0.04** |
  | This session's 7 alone | 0.757 | −$975 | 0.01 |

  As in D.1 and D.1b, the low PBO with the longs included is beta: the winner is the drift-riding RTH long. Among conditional strategies the in-sample winner now loses out of sample in 96% of splits (94% in D.1b); the seven new trials made the conditional pool worse, not better.

### Task 5 — synthesis (lead only)

**Does anything clear the bar? No.** Not one of the 7 re-tests, not one of the 28 declared statistics. The shortlist is empty, as it was after D.1 and D.1b, and `REGISTRATION.md` is untouched.

**Was the resolution-mismatch hypothesis worth checking?** Yes, and it is now closed rather than open:
- It was a real defect in the program's evidence, not a hypothetical one. The strongest quantitative source D.1 found (Mesfin's 947-day MNQ falsification study) was tested at the wrong grid in five trials, and the two volatility-state trials measured a "daily" regime with a quarter-hour estimator. A future reader of D.1 would have been entitled to say the sources were never tested as written.
- Tested as written, the sources fail the same way. The 5-minute trigger does filter noise (B-H1's win probability rose from 0.42 to 0.49), but what it filters out is not where the loss was. Mesfin's one marginal positive (ORB bar+15) is MES's worst re-test row. The daily-vol versions of D-H1/D-H2 change how many days trade and not the sign of anything.
- The sweep adds the coarser-resolution counterpart of Family F's null: the structure that is statistically robust in 5–60-minute bars is sub-cost, and the structure that would clear cost is not distinguishable from noise at this sample size. That is the same sentence D.1b wrote about 1-minute bars.

**What this adds to "should the program keep searching":** the searched region now covers 1-, 5-, 15-, 30- and 60-minute bars, 31 trials, 85 declared statistics (57 + 28), three independent multiple-comparison corrections, and a source-faithfulness audit. Every result agrees. Raising N to 31 has lowered every future candidate's DSR, and the same 139 EDA dates have now been mined twice.

**What remains unexamined after this session,** besides the order-book fill model already scoped for D.1e:
1. **Power at coarse resolution, not method.** A 60-minute-bar effect worth 4–10 ticks has 112–170 events in 139 days here. Resolving it to the cost bar at conventional confidence needs several times that; that is a data-length question (the D.1b option (b) purchase), not a technique question.
2. **Daily-bar signal construction proper.** RT6/RT7 moved a volatility estimator to daily; nobody has built a daily-range or daily-close conditioning variable (Crabel's narrow-range days, prior-day range terciles) for an intraday entry. B-H4 and D-H3 were SOURCE_SILENT, not re-tested, and a daily construction would be a new hypothesis rather than a resolution re-test, so it was correctly outside this session's declaration.
3. **The multi-day region** catalogued by D.1c, unchanged: it needs a harness that can hold across trade dates and a venue that permits it.
4. **A second instrument.** Cross-asset lead-lag has never been touched, for want of data.

None of these is a reason to run another round on the existing 289 days. Each needs something the program does not have: more history, a new construction declared in advance, a different constraint set, or a second series.

### Review findings and defects, all recorded

- **Fable conformance review (xhigh): "results trustworthy as computed."** Six LOW findings, none touching a computed number: (1) `_run_retests.py`'s "supported" label does not read the original's verdict (inert: every original failed in D.1); (2) gross per trip, a declared descriptive column, is not produced because `ScreeningReport` carries no gross figure, so the comparison uses net per trip only; (3) RT6's first-day V = 0.0 enters its 60-day regime history, which tightens the low-vol gate marginally for the first 60 days of each window, an artefact inherited from D-H1 and left in place to keep the re-test faithful to the original; (4) the RTH G0-vs-F1.1 difference is definitional (above); (5) the "all six OR slots present" rule is an undeclared implementation choice that never bound (every RTH day has six); (6) if an entire last RTH slot were missing, a position would fall to the engine's flatten (never occurs in the data).
- **Latent defect found by the re-test tests, fixed, re-run.** When rule R6's late completion delivers two coarse bars in one `push`, `OrbRetest` returned from inside the loop and `SpikeFadeRetest` consumed its hold flag before the fill existed, so the hold was never closed. The test writer verified that **no such push occurs on any research date at 5 minutes** (0 late completions). The fix (no early return; the hold ends at the first completion after the entry's decision bar at which the fill is visible) was applied, both scripts were re-run, and every re-test row and every accounting figure is identical to the pre-fix output. The strict xfail that found it now passes.
- **Latent divergence found by the resampler tests, documented, kept as a strict xfail.** A 1-minute feed that stops inside a slot leaves the builder's last accumulator unreturned while `coarse_bars` emits a short bar; every research trade date runs past its segment ends, so it cannot occur here. The precondition is now stated in `resample.py`'s docstring.
- **Cosmetic:** `_reject_reason`'s message hard-codes M = 28; `main()` asserts M = 28 before calling it, so it cannot misreport today.

### Files that appeared during the session from outside its tasks

`CLAUDE.md`, `docs/ORCHESTRATION.md`, `.claude/agents/worker-*.md`, `.claude/settings.json` and a five-line bullet in `docs/DECISIONS.md` were written at 16:25–16:29 PDT while this session's workflows were running. No subagent of this session issued a write to those paths (checked in every agent transcript), and no other Claude session transcript on this machine was active at that time; their content is the orchestration policy the user described in chat. They are left untouched, are not this session's artifacts, and await the user's confirmation.

Artifacts:
- **Reports:** `reports/stage_d1d_horizon_audit.md`; `reports/stage_d1d_timeframe_declaration.md` (read-only, hashed); `reports/stage_d1d_retests.json`; `reports/stage_d1d_family_g_facts.json` and the four per-timeframe files; `reports/stage_d1d_accounting.json`.
- **Code:** `strategy/research/g_timeframe/` (`resample.py`, `retests.py`, `_run_retests.py`, `_stylized_facts.py`, `trials.py`, deliberately empty); `strategy/research/_d1d_accounting.py`.
- **Tests:** `tests/test_d1d_resample.py`, `tests/test_d1d_retests.py`, `tests/test_d1d_family_g.py`.
- **Docs:** `docs/STAGES.md` (one entry), `docs/SCREENING.md` (N = 31).
- Scratchpad, not committed: `mesfin.txt`, `carver_vt.html`, `jkm.txt`, the pre-fix JSON copies.

## 2026-09-22 — Stage D.1e: defining the MES null (criteria, power and data quotes)

**Bought nothing, screened nothing, N stays 31.** This stage wrote down what "MES is null" will mean before any data is purchased: a bounded statement per strategy class with an economic threshold ε derived from the program's own power gate, the test and power that establish it, the days each class needs, Databento quotes for the history and order-book days that would supply them, a second sealed holdout carved from that history, and the frozen list of tests Stage D.1f runs. Headline: ε = 34 net ticks per micro per day ($85 a day at 2 micros) is the smallest edge that funds the Topstep funnel under the robust null; every class reaches 80% null power at ε within 566 days, and the extended history supplies 992 to 1,151 days under a 2019 or 2020 start; the extension quotes at $7.59 and the 181 full-day order-book dates C6 needs at about $181 to $199; 47 of the 95 measured members can be resolved below the 2.11-tick cost bar with the full history and 48, the once-a-day constructions, cannot. Nothing was bought; the spend decision is the user's.

Lead: Fable 5.1 at xhigh, across two sessions. The first session (00:33–01:36Z) died with the machine (system processes restarted 01:46Z); the second resumed at 04:32Z from `reports/stage_d1e_STATE.md` and the artifacts on disk. Ultracode was off, as the prompt said; the session reminder said it was on, and the prompt won (logged in the STATE file). Two user instructions were applied to CLAUDE.md during the first session (print the full ETA table in chat; agent names carry task, model and effort).

### Guardrails

| Check | Start (session 1, 00:33Z) | Resume (04:32Z) | End |
|---|---|---|---|
| `uv run python -m data.holdout status` | all_ok true, unlocks_logged 0 | all_ok true, unlocks_logged 0, research_has_no_holdout_rows true | all_ok true, unlocks_logged 0, research_has_no_holdout_rows True |
| REGISTRATION.md | 0 bytes | 0 bytes | 0 bytes |
| Databento spend this stage | $0.00 | $0.00: 95 `quote` events appended to `ledger/databento_spend.jsonl` (lines 72–166), every `usd` 0.0, no commit/settle/refused event, `shared_cumulative_usd` 84.006048 unchanged, no new file under data/vendor | same |
| Trial count N | 31 | 31 (the 31 trials were re-run once for their per-trade distributions; no new hypothesis) | 31 |
| git tree | clean at 2530d29 | dirty only with this stage's files (listed under Artifacts) | no commit |
| rules/, live/, ops/, TopstepX | untouched | untouched | untouched |

The quote script (`strategy/research/_d1e_quotes.py`) replaces both billable Databento namespaces with a raising guard before any call and never imports `data.adapter.fetch_range`; `tests/test_d1e_quotes.py` asserts the guard. Endpoints called, all free: `metadata.get_dataset_range`, `list_schemas`, `list_datasets`, `get_dataset_condition`, `get_cost`, `get_billable_size`, `symbology.resolve`.

### Delegation record

| Task | Owner | Model / effort | Outcome | Deviation from the plan |
|---|---|---|---|---|
| 0 Startup, context | lead | fable xhigh | done, 12 min | — |
| 1a Recorded figures from the D.1b/D.1d JSONs | worker-medium | sonnet medium | `reports/stage_d1e_members_recorded.{json,md}`; 31 trials + 21 statistics matched uniquely, 4 min | — |
| 1b Two additive runner fields + 31-trial re-run | worker-xhigh | opus xhigh | `screening/runner.py` (+`trip_pnls_usd`, `daily_n_trips`), 3 tests, `strategy/research/_d1e_members.py`, `reports/stage_d1e_members_trials.json`; continuity to the cent; 257 s run | promoted from the plan's sonnet high because it touches screening/ (CLAUDE.md routing) |
| 1c Event and daily series for all 64 F/G statistics | worker-high | opus high | `strategy/research/_d1e_event_series.py`, `reports/stage_d1e_members_events.json`; every recorded estimate reproduced to 1e-9; 5 min | added subtask: the recorded reports hold no per-day series for statistics |
| 1d Coverage map | lead | — | `reports/stage_d1e_coverage.md` | — |
| 2a Power-gate cell table | worker-medium | haiku medium | `reports/stage_d1e_power_gate_cells.{json,md}`, 120 cells, 70 s | — |
| 2b Finer and deeper gate points | worker-high | opus high | `strategy/research/_d1e_gate_extension.py`, `reports/stage_d1e_gate_extension.json`: 100 rows at T = 1, 2, 4, 8, 16, 32 | the run died with the machine at T=8; the lead restarted the self-resuming script inline in the background (a spawn would have cost more than the work) |
| 2c ε | lead | — | section below | — |
| 3a Power code, tests, run | worker-high | opus high | `strategy/research/_d1e_power.py`, `tests/test_d1e_power.py`, `reports/stage_d1e_power.{json,md}` | two passes plus one follow-up (rulings in `reports/_d1e_power_HANDOFF.md`); paused 05:04–05:46Z at the user's request; the file was split into four modules to respect the 800-line cap |
| 3a' Re-run at the final ε | lead (inline) | — | one command | plan said sonnet medium; a one-line re-run needs no isolation |
| 3b Verification of the power numbers | worker-xhigh | fable xhigh | `reports/stage_d1e_power_verification.md` | ran on the ε = 34 output, which turned out to be final, so no re-check after a re-run was needed |
| 4a/4b Availability and quotes | worker-xhigh | opus xhigh | `strategy/research/_d1e_quotes.py`, `tests/test_d1e_quotes.py`, `reports/stage_d1e_quotes.{json,md}`, 95 ledger quote events; 16 min | — |
| 4c Data-quality rules | lead | — | `docs/NULL_CRITERIA.md` section 4 | — |
| 5 Second holdout, frozen list, Family H | lead | — | `reports/stage_d1f_confirmation_list.md` | — |
| 5d Adversarial review | worker-max | fable max | `reports/stage_d1e_adversarial_review.md`, `reports/stage_d1e_adjudication.md` | ran once on the drafts (55 findings), then re-read the amended documents; the re-read was cut off by the session rate limit at about 07:35Z and resumed at 08:41Z from its transcript |
| 6 NULL_CRITERIA.md | lead | — | `docs/NULL_CRITERIA.md` | — |
| 7 Decision packet, entry, STAGES.md | lead | — | this entry | — |

The first session's four initial Agent calls failed ("agent type not found") because the four worker files had not yet been picked up; they loaded a few minutes later and every spawn after that used them. Concurrency never exceeded four.

### Task 1 — coverage map (`reports/stage_d1e_coverage.md`)

Lead, from three extraction artifacts (Task 1a sonnet medium: recorded figures; Task 1b opus xhigh: the 31 trials re-run once through `screen_candidate` for their per-trade and per-day distributions, continuity to `stage_d1d_accounting.json` to the cent, `continuity_problems: []`; Task 1c opus high: event-level and per-day series for all 64 directional F and G statistics, every recorded estimate reproduced to 1e-9). No new trial, no new statistic; N = 31.

**Seven classes, 101 members: 95 measured and 6 projected.**

| Class | Members | Tier A (Holm family) | Tier B (null only) | Refinement to the prompt's list |
|---|---|---|---|---|
| C1 session clock | 6 trials (A-H1, A-H2 buy, A-H2 sell, A-H3, A-H4 eth, A-H4 rth) | 6 | 0 | none |
| C2 reference levels and breakouts | 10 trials (B-H1 x2, B-H2, B-H3 x2, B-H4, RT1–RT4) + 21 statistics | 10 + 9 (F6.1, F4.1, F4.4x100, G2.RTH.30, G2.ETH.30, G2.ETH.5, G5.RTH.15, G5.RTH.30, G3.RTH.15) | 12 (F4.2, F4.4x50, G2/G3/G5 at the other timeframes) | F6.1 (the open's position in the overnight range) added: a reference-level statistic on the D.1b near-miss list the prompt did not place |
| C3 short-horizon reversal and momentum | 4 trials (C-H1, C-H2, C-H3, RT5) + 36 statistics | 4 + 12 (nine F3.2 bucket pairs, F3.3 a and b, G1.RTH.5) | 24 (F1.1 at h = 1/5/15/30/60 for ETH and RTH, three F3.2 pairs, G1 and G4 at the other timeframes) | F1 enters through its directional statistic F1.1, not the F1.2 variance ratios, which have no side and are reported descriptively |
| C4 volatility-state conditioning | 6 trials (D-H1..D-H4, RT6, RT7) + 7 statistics | 6 | 7 (F2.4 x2, F5.1 x2, F5.2 x2, F5.3) | F2 enters through F2.4 only; F2.1–F2.3 are non-directional facts |
| C5 calendar and scheduled events | 4 trials (E-H1..E-H4) | 4 | 0 | none |
| C6 passive execution | C-H4 | 1 (lower bound only) | 0 | class verdict belongs to D.1g |
| C7 daily-bar constructions | H1–H6, declared in the confirmation list | 6 | 0 | new; power projected from proxies until D.1f measures it |

Per member the map records trades (or events) per day, per-trade net mean and SD in ticks per micro, daily SD over every window date with zeros on no-trade days, lag-1 autocorrelation of the daily series, the within-day clustering VIF, and the window (trials: 289 train-union dates 2025-04-01..2026-05-13; statistics: 139 EDA dates 2025-10-17..2026-05-13). Three things the figures show that the power calculation then depends on: (1) the four high-frequency C3/C6 trials (30 to 141 trades a day) have the largest daily SDs, 47 to 104 ticks per micro, with mild within-day clustering (VIF 0.87 to 1.37); (2) daily autocorrelation is small for almost every member (|lag-1| < 0.25 except A-H4 rth leg at −0.30, G1.RTH.5 at −0.25 and F3.2 08→09 at +0.25), so the block bootstrap's inflation factors sit near 1; (3) E-H3 trades four times in 289 days and its daily series is almost all zeros, which is what makes its economic null trivially cheap and its structural question unanswerable at any feasible length.

Out of scope, named so the verdict never overreaches: multi-day holding (venue, D.1c); other instruments and cross-asset effects (user decision); order-flow signals needing book data beyond C6's fill model; sizes other than 2 micros; passive execution outside C6; constructions not on the frozen list.

Family H proxy rule (for Task 3 only; the criteria use measured series in D.1f): per-trade SD 100 ticks per micro for the five breakout/fade tests (between B-H1 hold-75's 49.8 and A-H4 rth's 114.6, nearer the latter for the three-quarter-session hold) and 115 for the open-to-close H6; firing fractions from the conditions' definitions under exchangeable ranges (NR4 1/4, NR7 1/7, inside day 1/4, terciles 1/3, outer CLV fifths 2/5, times 0.9 for a breach of the opening range before 14:30); daily SD = per-trade SD x sqrt(f). Nothing was read from any data for this.


### Task 2 — the economic threshold ε

Lead judgment on two worker artifacts: the haiku-medium tabulation of the Stage B grid (`reports/stage_d1e_power_gate_cells.{json,md}`, 120 cells, every cell's gross and net ticks per trade and net $/day at 2 micros beside its robust and matched verdicts) and the opus-high extension (`strategy/research/_d1e_gate_extension.py`, `reports/stage_d1e_gate_extension.json`: 100 further cells chosen by the lead to bracket the boundary in net ticks, at T = 1, 2, 4, 8 and 16 on both paths and, on the standard path only, 32 (all four T = 32 cells finished: one passes at $188.50 a day, none can bind), with the same `funnel.power_gate.evaluate_point`, the same 8,000 careers per cell, the same seeds, nothing under funnel/ modified; at T outside the baseline grid only the robust verdict is defined and the matched columns are null). A cell passes when its robust 80% power's lower 95% bound clears 0.80 (the Stage B rule); "marginal" means the point estimate clears and the bound does not, and marginal is not pass.

**The boundary, read in net ticks per trade and in net ticks per micro per day (both paths):**

| Path | T | cells | highest-$/day FAIL (ticks/micro/day, power) | lowest-$/day PASS (ticks/micro/day, power) | marginal cells |
|---|---|---|---|---|---|
| consistency | 1 | 32 | $83.98/day = 33.59 t/μ/d (33.59 t/trade, p=0.45, R=2.0, power 0.68) | $102.92/day = 41.17 t/μ/d (41.17 t/trade, p=0.65, R=1.0, power 0.90) | 39.7 |
| consistency | 2 | 30 | $89.50/day = 35.80 t/μ/d (17.90 t/trade, p=0.5, R=1.5, power 0.78) | $87.48/day = 34.99 t/μ/d (17.50 t/trade, p=0.6, R=1.0, power 0.81) | — |
| consistency | 4 | 31 | $86.58/day = 34.63 t/μ/d (8.66 t/trade, p=0.48, R=1.5, power 0.80) | $96.88/day = 38.75 t/μ/d (9.69 t/trade, p=0.66, R=0.75, power 0.91) | 33.8 |
| consistency | 8 | 9 | $84.39/day = 33.76 t/μ/d (4.22 t/trade, p=0.4, R=2.0, power 0.76) | $92.02/day = 36.81 t/μ/d (4.60 t/trade, p=0.575, R=1.0, power 0.86) | — |
| consistency | 16 | 6 | $47.97/day = 19.19 t/μ/d (1.20 t/trade, p=0.45, R=1.5, power 0.41) | $98.28/day = 39.31 t/μ/d (2.46 t/trade, p=0.4, R=2.0, power 0.84) | — |
| standard | 1 | 32 | $114.59/day = 45.84 t/μ/d (45.84 t/trade, p=0.49, R=2.0, power 0.78) | $119.88/day = 47.95 t/μ/d (47.95 t/trade, p=0.57, R=1.5, power 0.84) | — |
| standard | 2 | 30 | $110.73/day = 44.29 t/μ/d (22.15 t/trade, p=0.45, R=2.0, power 0.76) | $119.48/day = 47.79 t/μ/d (23.90 t/trade, p=0.53, R=1.5, power 0.84) | 42.8 |
| standard | 4 | 31 | $100.08/day = 40.03 t/μ/d (10.01 t/trade, p=0.42, R=2.0, power 0.71) | $110.69/day = 44.28 t/μ/d (11.07 t/trade, p=0.6, R=1.0, power 0.84) | 44.4 |
| standard | 8 | 9 | $94.77/day = 37.91 t/μ/d (4.74 t/trade, p=0.475, R=1.5, power 0.69) | $131.52/day = 52.61 t/μ/d (6.58 t/trade, p=0.425, R=2.0, power 0.92) | — |
| standard | 16 | 6 | $98.28/day = 39.31 t/μ/d (2.46 t/trade, p=0.4, R=2.0, power 0.68) | $113.20/day = 45.28 t/μ/d (2.83 t/trade, p=0.475, R=1.5, power 0.81) | — |

**Why ε is a daily figure.** Read per trade, the boundary falls with T (about 45 net ticks at one round turn a day, 22 at two, 11 at four, 5 to 7 at eight). Read per day it is roughly flat, the consistency path passing first between 34 and 39 ticks per micro per day at every T from 1 to 16 and the standard path between 44 and 53 (its lowest pass at T = 8 sits at 52.6 with the highest fail at 37.9), because the funnel's pass or fail depends on the daily P&L distribution, whose scale barely changes with how the session is cut. The members trade anywhere from 0.014 (E-H3) to 141 (C-H1) times a day, far outside the gate's 1-to-4 grid, so a per-trade ε at the class's "typical frequency" would have to be extrapolated off the grid for every class; the daily figure is the invariant the gate actually measured and needs no extrapolation. This is the one refinement to the prompt's Task 2 wording, and it is conservative: the daily P&L is what the Combine and XFA rules act on.

**The rule (docs/NULL_CRITERIA.md 2.2), mechanical:** ε_day = floor( min over every evaluated cell with robust verdict "pass", both paths, all T, of net $/day at 2 micros ÷ $2.50 ). Taking the minimum over paths and T and rounding down are both in the direction that makes a null harder to claim. Because the verdict requires the power's lower bound to clear 0.80, a cell whose true power is below 0.80 essentially never passes at 8,000 careers, so the minimum approaches the true 80% contour from above and is not a Monte Carlo fluke. **ε_day = 34 net ticks per micro per day, $85.00 a day at 2 micros**, from the cell consistency path, T = 2, p = 0.60, R = 1.00 (grid): 17.496 net ticks per trade × 2 × $2.50 = $87.48 a day, robust power 0.812 with lower bound 0.804; nearest excluded cell marginal at $84.41 (consistency T = 4, p = 0.58, R = 1.00, power 0.804, lower bound 0.796). The next four passing cells sit at 36.8, 37.9, 38.8 and 39.0 ticks per micro per day, all on the consistency path at T = 4, and the standard path's boundary is higher (about 44 to 48 at T = 1 to 4), so the consistency path binds.

**ε per class, per trade, beside the cost bars** (typical frequency = median trades per day of the class's trial members on the train union; C7 = median firing fraction):

| Class | Typical trades/day | ε per trade (net ticks/micro) | Market bar | Passive bar | Gross-equivalent per trade |
|---|---|---|---|---|---|
| C1 | 0.938 | 36.26 | 2.11 | 0.98 | 38.37 |
| C2 | 0.945 | 35.99 | 2.11 | 0.98 | 38.10 |
| C3 | 36.151 | 0.94 | 2.11 | 0.98 | 3.05 |
| C4 | 0.676 | 50.26 | 2.11 | 0.98 | 52.37 |
| C5 | 0.097 | 350.93 | 2.11 | 0.98 | 353.04 |
| C6 | 92.467 | 0.37 | 2.11 | 0.98 | 2.48 |
| C7 | 0.263 | 129.52 | 2.11 | 0.98 | 131.63 |

**What this means, said plainly.** ε is large. A strategy that trades once a day must earn about 34 net ticks on that trade, roughly a quarter of a session's typical range, before it funds a Combine at 2 micros; one that trades 36 times a day needs about one tick a trade. The economic null is therefore cheap to establish for every class (Task 3: the binding member needs 566 (F1_1_h1_RTH) days for 80% null power, and the extended history supplies 1,151 under a May 2019 start, 992 under a January 2020 start). What the data cannot settle for the low-frequency classes is the structural question at the cost-bar scale, whether any member has a positive net edge of a tick or two per trade: that needs about 190,000 to 1,600,000 days for the once-a-day members, which no purchasable MES history supplies. The program therefore claims the bounded economic null and reports the descriptive resolution (the smallest edge each class could have ruled out with the days it had) beside it; it does not claim "no edge". The prompt asked that if ε came out too small to resolve, the stage should say what the program CAN claim instead; the case here is the mirror image, and the same honesty applies.


### Task 3 — power and sample size (`reports/stage_d1e_power.json`)

Worker: opus high in two passes (`strategy/research/_d1e_power.py`, `_d1e_calendar.py`, `_d1e_power_report.py`; `tests/test_d1e_power.py`, 10 known-answer tests, all passing; run at ε = 34: 101 members, 2,000 replications per length, 151 s at 8 jobs). Verified independently by fable xhigh (`reports/stage_d1e_power_verification.md`; section below). Lead rulings during the build, all recorded in `reports/_d1e_power_HANDOFF.md`: the iid known-answer series lengthened to 50,000 days so the ±0.05 VIF band is three sampling deviations wide; the simulation's standard error changed to the replicate's own variance times the source series' bootstrap inflation factor, because a block-bootstrap replicate's autocovariances are already attenuated once and the original design attenuated them twice (measured: simulated null power 0.848 instead of 0.80 on an AR(1) with φ = 0.3; 0.80 ± 0.04 after the change); scipy absent, stdlib normal quantiles used (agreement 1e-15); and the chosen-figure rule below.

**Method.** Unit: net ticks per micro per day (trials: `daily_net_usd / 2.5`; statistics: s × daily event sum − 2.11 × daily event count). Per member: SD of the daily series over every window date, r = trades or events per day, and VIF_boot, the inflation the program's own block-5 stationary bootstrap sees (Politis–Romano, p = 1/5, lags to 20). Analytic: (a) detection days n_a = ((z_a + z_0.8) SD √VIF / ε)² with z_a = Φ⁻¹(1 − 0.05/58) = 3.134, Holm's most stringent step applied to every member so each n_a is an upper bound on what Holm needs; (b) null-power days n_b = ((1.645 + 0.842) SD √VIF / ε)², the length at which a member with true edge 0 shows its one-sided 95% upper bound below ε with 80% probability. Simulation: stationary block-bootstrap resamples of each member's centred daily series (mean block 5, the program's helper, 2,000 replications) at 16 lengths from 10 to 3,000 days plus n_a and n_b themselves, shifted to ε and to 0; power curves with Monte Carlo standard errors; crossings by log-linear interpolation. Chosen figure: analytic unless the two differ by more than 15%, in which case the LARGER; the prompt said "use the simulated figure", and the deviation is logged because the simulation came out smaller for about a dozen heavy-tailed members (A-H3, A-H4 rth, RT2, several G statistics, by 16 to 39%), which reveals under-coverage of the closed-form upper bound at short lengths, not extra power, so planning on it would be anti-conservative; where the simulation asked for more days (F4.4 ×100, G4.RTH.5, G1.ETH.15) it was used. Twenty-nine low-frequency members have analytic n_b below the shortest simulated length (10 days) and keep the analytic figure, flagged. Family H is projected from the coverage map's proxy rule, analytic only.

**Per class (ε = 34 ticks per micro per day):**

| Class | Binding member (null power) | n_b analytic / simulated / chosen | Binding member (detection) | n_a chosen | Days supplied at S = 2019-05-06, 2019-07-01, 2020-01-02, 2021-01-04, 2022-01-03, 2023-01-03 | Null power at ε reachable |
|---|---|---|---|---|---|---|
| C1 | A-H4 rth leg | 149 / 161 / 149 | A-H4 rth leg | 379 | 1151, 1114, 992, 755, 516, 277 | all S |
| C2 | G3.RTH.5 | 193 / 182 / 193 | G3.RTH.5 | 492 | 1151, 1114, 992, 755, 516, 277 | all S |
| C3 | F1_1_h1_RTH | 566 / 571 / 566 | F1_1_h1_RTH | 1447 | 1151, 1114, 992, 755, 516, 277 | S ≤ 2021-01-04 |
| C4 | F2_4_15min_vol_tercile_top | 171 / 152 / 171 | F2_4_15min_vol_tercile_top | 436 | 1151, 1114, 992, 755, 516, 277 | all S |
| C5 | E-H1 scheduled macro drift | 16 / 10 / 16 | E-H1 scheduled macro drift | 41 | 1151, 1114, 992, 755, 516, 277 | all S |
| C6 | C-H4 passive-fill reversal | 181 / 174 / 181 | C-H4 passive-fill reversal | 461 | 1151, 1114, 992, 755, 516, 277 | all S |
| C7 | H6 prior-close location follow-through (projected) | 114 / censored / 114 | H6 prior-close location follow-through | 290 | 1151, 1114, 992, 755, 516, 277 | all S |

Days supplied by the extension, confirmation window S..2024-02-29 after the roll blackout and the vendor-degraded dates (calendar estimate, ±3%): S = 2019-05-06: 1151, S = 2019-07-01: 1114, S = 2020-01-02: 992, S = 2021-01-04: 755, S = 2022-01-03: 516, S = 2023-01-03: 277. Holdout-2 (2024-04-01..2025-03-31) holds about 239 trade dates.

**Reading.** (1) The economic null is cheap. The binding member of the whole list, F1_1_h1_RTH (the one-minute RTH lag autocorrelation, 381 events a day, C3), needs 566 days for 80% null power at ε; every other member needs 193 or fewer (C2's G3.RTH.5 193, C6's C-H4 181, C1's A-H4 rth leg 149, C7's projected H6 114). The extension supplies 992 to 1,151 days if the start rule lands in 2019 or 2020, 755 from 2021, 516 from 2022. Only C3 would fall short, and only if S lands in 2022 or later. (2) Detection power at ε is also within reach for every class but C3 (n_a 1,447 for F1_1_h1_RTH; 492 or fewer elsewhere, C6's C-H4 461). (3) What the history cannot do is resolve the structural question at the cost-bar scale for the low-frequency members. At 1,151 days the smallest edge the data can rule out, per trade, is C1 2.45 to 23.62 (A-H3 weekend effect); C2 0.30 to 14.00 (G3.RTH.5); C3 0.02 to 5.22 (G4.RTH.60); C4 0.46 to 3.27 (D-H4 overnight gap fade); C5 1.96 to 37.26 (E-H1 scheduled macro drift); C6 0.15 to 0.15 (C-H4 passive-fill reversal); C7 26.65 to 40.88 (H2 NR7 opening-range breakout) ticks per trade at S = 2019-05-06. Forty-seven of the 95 measured members can be resolved below the 2.11-tick market cost bar with the full history; 48 cannot, and they are exactly the once-a-day and rarer constructions (E-H1 37.3 ticks per trade, A-H3 23.6, G3.RTH.5 14.0, A-H4 rth 12.8, G3.RTH.15 11.7, F6.1 7.5, ...). A one-tick-per-trade edge for a once-a-day member would need on the order of 190,000 to 1,600,000 trade days to establish or exclude at 80% null power. No purchasable MES history does that, and the criteria therefore claim only the bounded economic null and report the descriptive resolution beside it.


**Independent verification (fable xhigh, `reports/stage_d1e_power_verification.md`, scratch `reports/_d1e_power_verify_scratch.py`).** Recomputed from the raw series without importing the four power modules: ε_day = 34 and its cell reproduce (on both versions of the extension file the background job wrote during the check); all 101 members' r, SD and VIF match to under 1e-4 %, all 202 analytic sample sizes are identical; 13 members re-simulated with an independent seed (26 arm checks) agree within 5.2 %; the chosen-figure rule was applied correctly in all 190 arm cases, with one flag (F4.4 ×100, null-power arm) sitting on the 15 % boundary and flipping under the verifier's seed in the conservative direction; Family H projections, class tables, binding members, achievability flags and all 42 resolution-range cells exact; supplied days exact under the stated method, which undercounts trade dates by 3 to 4 % against the pipeline's early-halt convention (conservative, no flag changes); the tests' expectations are independent of the code and both required known-answer cases are present. Gaps the verifier listed for the record, none affecting a reported number: no test of the autocovariance divisor, of a negative-autocorrelation VIF, of the simulation SE against a hand value, of the class aggregation, of the degraded-date and blackout subtraction, or of the exact 15 % boundary. Verdict: VERIFIED on every section, WITH NOTES on four. After the unit correction the same verifier re-checked the corrected run (section 11 of the report): the per-micro series rebuilt from each trip's P&L and quantity matches the file to 2e-13 on all 31 trials, equals the USD series over 1.25 for exactly the 29 fixed-size trials and differs for D-H2 and RT7; SD, VIF and all 74 analytic sample sizes for the trials and the H rows are identical; the six new binding members re-simulated agree within 3.7% (E-H1's detection curve crosses 0.80 non-monotonically, 0.79 at the chosen 41 days and above 0.80 only from about 70, which the rule handled as designed); the chosen-figure rule on all 190 arm cases, N_C6 = 181, the class tables, all 42 resolution cells and the 47-of-95 count are exact; the 64 statistic rows are byte-identical to the earlier run. VERIFIED.

### Task 4 — availability, quality rules and quotes (`reports/stage_d1e_quotes.md`, $0.00 spent)

Worker: opus xhigh (`strategy/research/_d1e_quotes.py`, `tests/test_d1e_quotes.py`, 95 ledger `quote` events, `$0.00`). Verified by the lead against the ledger diff.

**Availability (4a).** GLBX.MDP3 runs from 2010-06-06; `ohlcv-1m` from the start, `mbo` from 2017-05-21. MES.v.0's symbology interval opens 2019-04-01 (instrument 7849, MESM9), but the 2019-04 chunk quotes at 0 billable bytes: the first month with bars is **2019-05**. Dataset condition 2019-04-01..2025-04-01: 1,872 available days, **8 degraded** (2020-02-27, 02-28, 05-05, 06-30, 07-01; 2021-12-05; 2022-01-02; 2024-09-18), which the existing `vendor_degraded_day` path masks. The current raw data begins at UTC 2025-04-01T00:00 (chunk `range=2025-04-01_2025-05-01`), so the extension's last chunk is `range=2025-03-01_2025-04-01`: no overlap, no gap. Caveat found by the worker and settled by the lead in the confirmation list: the 2025-03-31 22:00–24:00 UTC bars belong to CME trade date 2025-04-01, the mined first date; they sit in the sealed 2025-03 chunk and stay sealed, and the research parquet is not rebuilt.

**Quotes (4b), `metadata.get_cost` only, each a ledger `quote` event:**

| Dataset | Range | Quote | Billable | On disk (zstd 0.327 measured) | Drive |
|---|---|---|---|---|---|
| MES.v.0 ohlcv-1m, continuous, monthly chunks exactly as `data.pull_mes` pulls them | 2019-04-01..2025-04-01, 72 chunks | **$7.59** (72 chunk quotes sum $7.5862; one whole-range quote $7.5862, difference $0.00) | 111.0 MiB | 36 MiB | main, beside the existing chunks |
| Auxiliary schemas | — | none: the pipeline's only paid schema is ohlcv-1m; symbology and dataset condition are free and must be re-run over the range | — | — | — |
| MES MBO, RTH 08:30–15:10 CT, 5 sampled days (2025-05-14, 08-13, 11-12, 2026-02-11, 2026-04-15) | per day | mean **$0.78/day** (range $0.47–1.24), 446 MiB billable/day | | ~145 MiB/day est. | LARGE STORAGE |
| MES MBO, RTH x 20 / 40 / 60 / 120 days | linear scaling of the 5-day mean, not a quote | **$15.67 / $31.34 / $47.01 / $94.03** | 8.7 / 17.4 / 26.1 / 52.2 GiB | 2.8 / 5.7 / 8.5 / 17.1 GiB est. | LARGE STORAGE |
| MES MBO full trade date x 20 / 40 / 60 / 120 | scaling | $20.00 / $40.00 / $60.00 / $120.00 | 11.1–66.7 GiB | 3.6–21.8 GiB est. | LARGE STORAGE |
| MES mbp-10 RTH x 20 / 40 / 60 / 120 (for comparison) | scaling | $24.18 / $48.35 / $72.53 / $145.06 | 48–290 GiB | 16–95 GiB est. | LARGE STORAGE |
| Linearity check: one contiguous 20-day block quoted whole (2025-10-01..10-29) | quote | mbo $22.03 vs 20 x full-day mean $20.00 (ratio 1.10); mbp-10 $33.49 vs $30.57 (1.10) | | | |

Free space: main drive about 368 GB, `/mnt/large-storage` about 770 GB. Every MBO option fits on LARGE STORAGE with two orders of magnitude to spare; nothing secret is ever written there, and the sealed holdouts stay on the main drive. The MBO figures for the C6-needed day count are in the decision packet.

**Ledger accounting:** `ledger/databento_spend.jsonl` 72 lines before, 167 after; new lines 72..166 are all `quote` with `usd` 0.0; `shared_cumulative_usd` 84.006048 before and after; `session_cumulative_usd` 0.0; no new file under `data/vendor`. Seven checks in the quotes report all PASS. The worker also noted that the configured external ledger path was absent and read the relocated copy read-only without modifying `data/config.py`.


### Task 5 — the second holdout and the D.1f confirmation list (`reports/stage_d1f_confirmation_list.md`)

Lead only. Written as a DRAFT in the first session (01:08Z), filled in and amended after the Task 5d review in the second, then hashed and made read-only (section below).

**Second holdout (5a).** Trade dates **2024-04-01 through 2025-03-31** inclusive (239 CME trade dates by the calendar estimate; the exact count is recorded at sealing). Sealed as the 13 whole monthly raw chunks `range=2024-03-01_2024-04-01` through `range=2025-03-01_2025-04-01`, immediately after each chunk's round-trip verification and before any parquet is built from any new chunk, through `data/holdout.py`'s cipher and ceremony with a second `HoldoutPaths` (store `data/sealed/MES_holdout_v2/`, manifest `docs/HOLDOUT2_MANIFEST.json`, the same append-only unlock log, the same REGISTRATION.md requirement). The March 2024 trade dates are embargoed (inside a sealed chunk, never built into bars), which is what makes whole-chunk sealing byte-exact. The 2025-03-31 22:00–24:00 UTC bars (the missing first two hours of the mined trade date 2025-04-01) stay sealed. Why these bounds: it is the year immediately before the mined window, so the closest available regime to live conditions for a final D.2 read; with the current holdout (2026-06-22..2026-09-16) it gives D.2 two separated seasons; and it is several times the days any member needs for 80% null power at ε (Task 3).

**Confirmation window.** Trade dates S (the start rule's date, computed in D.1f) through **2024-02-29**, built from the unsealed chunks only, with the current pipeline's exclusions (roll blackout of the splice date plus two prior sessions from symbology, vendor-degraded days, CME calendar extended to 2019–2024 before any run). The 289 train dates and the 139 EDA dates are never pooled into a confirmation figure; they are used only for the continuity check (every trial reproduces `stage_d1d_accounting.json` to the cent before any confirmation figure is read).

**The frozen list (5b).** Tier A, the Holm family, m = 58: the 31 trials with every parameter frozen at its recorded value (each module's sha256 is in the list; the 31 IDs are the label strings of `strategy.research._d1d_accounting.ALL_TRIALS`, which D.1f imports rather than retypes); the 21 logged near-misses as event statistics with their declared definitions, direction fixed from the mined window, tested net of the 2.11-tick market cost; and Family H, six daily-bar constructions for intraday entries, class C7, fully specified (daily bar built inside the strategy from bars already seen; complete-day rule; instrument guard on every daily bar that enters the condition; 30-minute opening range needing 25 of 30 bars; breakout or fade on the first close beyond the range between 09:00 and 14:29 CT, one entry per day, fill at the next open; exit emitted on the first bar at or after 14:58 CT with the engine's forced flatten as the logged fallback; lookbacks 4, 7, 2, 61, 61, 1 complete bars; tercile cuts at q = 33.33 and 66.67 exactly, linear, over the 60 complete ranges before d-1; CLV cuts 0.2 and 0.8, inequalities exactly as tabulated; 2 micros at the size-5 slippage bucket; factories without arguments): H1 NR4 breakout, H2 NR7 breakout, H3 inside-day breakout, H4 bottom-tercile-range breakout, H5 top-tercile-range fade, H6 prior-close-location follow-through from the open. Look-ahead check per H test: a unit test that perturbs day d's bars and asserts the condition is unchanged, and perturbs day d-1's and asserts it changes as computed by hand; the fill-timing canaries; and hand-built known-answer days. Tier B: the 43 directional F and G statistics that were not near-misses, which enter the class null and never an edge claim. C6's criteria and data rule are in the list's section 3.5 for D.1g to inherit unchanged: a queue-position fill model specified and hashed in D.1g before the MBO purchase, with any book-derived parameter estimated on declared days outside the evaluation dates; full trade-date books, because C-H4 rests orders in every session; N_C6 = 181 days at the corrected per-micro unit, the LAST N_C6 confirmation-window dates on or before 2024-02-29 that are neither blackout nor degraded, never a holdout date; D.1g's queue-model C-H4 counts as a new trial (N = 59) and its dates were already read by D.1f's trade-through run, so a C6 edge claim is out of sample only in the fill model.

**Decision rules (5c), fixed now.** Edge exists: Holm over the 58 one-sided Tier A p-values at family-wise 5%, then the composite screening verdict on the confirmation window (robust zero-edge gate plus both drift sub-checks; for a statistic the gate runs on its event p, R and T as for trips and the drift charge is the window-mean price change over the event's own forward interval), then the cumulative accounting at N = 58 pinned to the program's functions: DSR > 0.95 with the Sharpe variance over the 58 Tier A members' confirmation-window daily Sharpes, daily t > 3.0 one-sided, CSCV PBO < 0.5 on 8 equal contiguous blocks; the same three at N = 101 and 186 reported, not criteria. A passing member goes to the user as a D.2 discussion item and is not registered by D.1f. Null for a class: every Tier A and Tier B member has UCB95 (percentile stationary bootstrap of the per-micro daily net series through the program's own helper, mean block 5, 10,000 resamples, a fresh generator seeded 20260921 per member, np.quantile at 0.95) below ε_day and achieved null power Φ(ε_day/SE_boot − 1.645) ≥ 0.80. Anything else is inconclusive, and one inconclusive member keeps its whole class out of the null verdict; a member with zero trips or events, or a zero bootstrap standard error, is inconclusive, not null; a member meeting the null with fewer than 30 trips or events is marked "null by inactivity" and the class statement carries that label. Regime slices per calendar year are descriptive only; 2020 is included and nothing is excluded in advance or after.


### Task 5d — adversarial review, findings and rulings

Worker: fable max (`reports/stage_d1e_adversarial_review.md`, 06:23–06:50Z, 965 lines). Brief: find every way the two documents let a later stage fudge the result. It returned **55 findings: 7 BLOCKER, 23 SHOULD-FIX, 25 NOTE, verdict NOT READY**, after recomputing all 31 section-0 hashes (all match), re-deriving ε on the pinned extension file (34 holds), cross-checking the near-miss lists (match) and reading position sizes, the C-H4 session gating, the release table and the runner's code path.

The lead's adjudication is in `reports/stage_d1e_adjudication.md`: **all 55 accepted, four with modifications, none rejected.** The seven blockers and what changed:

| ID | Finding | Ruling and amendment |
|---|---|---|
| R-1 | The daily-series unit divided every trial by $2.50 as if it traded 2 micros; every trial module trades 1 micro (D-H2 and RT7 1 to 5 by rule). Every trial's null would have been tested at 68, not 34, ticks per micro per day and every trial's power row was ~4× understated. | Accepted. The unit is now per micro per trip: each round trip divided by its own contract quantity, recorded by a new additive runner field `trip_micros` (TripMicrosFixer-OpusXHigh: runner field, 4 tests, `_d1e_members.py` re-run, `daily_net_usd` byte-identical, continuity to the cent). The power run, the coverage map, N_C6 and the resolution counts were re-issued at the corrected unit and re-verified. Running the trials at 2 micros is forbidden. |
| R-2 | Trial parameters (direction, session, hold_minutes) live in unhashed assembly files; the continuity JSON was unhashed. | Accepted: seven hashes added to section 0 and a verbatim factory column to the trial table. |
| R-3 | Section 5.4 ordered an edit to two hashed statistics modules, and the runner cannot reach 2019–2024 without changes the list did not enumerate. | Accepted: a wrapper module calls the hashed builders with the confirmation dates (the `_d1e_event_series.py` pattern, with the 1e-9 reproduction test); the files D.1f may change are enumerated and everything else must be byte-identical to a freeze manifest. |
| R-4 | Nothing froze the harness at run time; the continuity check covers only the train-union path. | Accepted: step 1b, a harness-freeze manifest written and committed before any quote; the list runner refuses to run on any differing hash and re-checks at completion. |
| N-1 | E-H1 and E-H2 read a release table covering 2025-04..2026-06 only, so they cannot fire on the confirmation window; C5 was unresolvable or would be extended post hoc. | Accepted: a hashed 2019–2024 release-table module from the Federal Reserve and BLS schedule archives, built and cited before the purchase; the two strategy modules amended to accept a table argument with the default unchanged, re-hashed in a declared amendment with a train-union reproduction test. |
| C-1 | C-H4 rests orders in every session; RTH-only MBO could not fill its ETH orders. | Accepted: D.1g buys full trade-date books ($1.00 a day mean against $0.78 RTH-only) for the N_C6 dates. |
| D-2 | The 2019–2024 calendar had no completeness check and no freeze point; a missing entry fails silently and shifts the blackout, the flatten and the H completeness rule. | Accepted: coverage assertion in the bar builder, an observed-holiday validation over the confirmation bars before the start rule runs, immutability once the list runs. |

Should-fix and note rulings of substance: the F4.4 event definition was inverted in the draft and is now the plain round-level move with the control-subtracted estimate descriptive (R-5); sample-derived thresholds are recomputed on the confirmation window as the hashed code does (R-6); the H tests may be exercised only on synthetic bars before the confirmation (R-7); the ε paragraph now pins both source files, defines "pass" and forbids recomputation (E-1); every class statement must carry its per-trade resolution, least-active member and count, and a "null by inactivity" label for members with fewer than 30 trips or events (E-2, the lead's modification: no minimum-activity threshold on the null itself, because a member that almost never trades truly cannot fund a Combine); the H specification gained an instrument guard covering every bar in the condition, a 61-bar warm-up, a fallback exit rule, exact inequalities and percentile arguments (H-1 to H-8); holdout-2 sealing is per chunk in the download call with oldest-first order and per-holdout unlock accounting (L-1 to L-3); DSR, t and PBO are pinned to the program's functions and block count (M-1); the Tier B anomaly clause is one-sided in the mined direction (M-2); D.1g's queue-model C-H4 counts as a new trial, N = 59 (M-3); zero activity is inconclusive (N-2); degraded days are traded through by trials and excluded by statistics, with the vendor's list frozen at fetch (N-3); the start rule reads bars present, all trade dates, on the parquet after the drop, with 2019-05-06 the earliest possible S (D-1); and the hashing order is list first, criteria second, both hashes to a JSON the runner checks and to this entry, with the user's commit as the anchor (V-1).

After the amendments and the corrected numbers, the reviewer re-read both documents: section 15 of the review, after the amendments and the corrected numbers: 52 findings RESOLVED, 3 PARTLY (a residual "2 micros" for C-H4 in the C6 statement, the E-H amendment's conflict with section 0's invalidation rule, an unexplained "masked" in the criteria's degraded-day sentence), 0 NOT RESOLVED, and 10 NEW findings the amendments introduced (one blocker: the E-H release-table amendment could not be executed without breaking section 0, the runner's refusal or the factory column; one should-fix: the raw-symbol drop rule could remove May–June 2019 under a per-interval symbol mapping; eight notes). All thirteen were accepted and written in (adjudication addendum): section 0 carves the two E-H files out to the freeze manifest and the trial table carries both their factories verbatim; the raw symbol is the one mapped on the bar's date and any drop from 2019-05-06 on stops the run; the holdout-2 size rationale is restated at the corrected scale; D.1g's N = 59 is in the criteria; the list asks the user to commit the freeze rather than committing; data/config.py is frozen with it; C-H4 sits in the C6 statement only; H1 and H2's earlier ranges are named exempt from the instrument guard; and the ε rule names the field as tabulated. The reviewer's condition for hashing was exactly those items; they were applied before the hash.

### Task 6 — `docs/NULL_CRITERIA.md`

Lead only; drafted in the first session, filled and amended in the second after the Task 5d review, hashed with the confirmation list. It is the standing document every later MES stage is judged against. Contents:

1. **The null statement**, per class, with every number explicit: market orders at the Stage A.1 modelled retail cost ($1.22 commission plus the time-of-day slippage table, about 2.11 ticks per round turn at one round turn a day), 2 micros, flat by the XFA cutoff, on the pre-registered confirmation window S..2024-02-29; no member has a net edge of at least ε = 34 net ticks per micro per day ($85.00 a day at 2 micros); every member's one-sided 95% upper bound on mean net daily P&L is below ε with achieved null power at least 80%. The statement is made per class, never for "MES", and a class with any inconclusive member gets none.
2. **The C6 variant** for D.1g: resting limit orders, the queue-position fill model declared and hashed in D.1g from MBO data, commission only (the 0.98-tick passive bar), the same daily ε (the funnel's economics do not depend on how a fill happened), the N_C6 pre-declared dates; C-H4's trade-through result in D.1f is a lower bound and does not establish the C6 null.
3. **ε with its derivation** (section below), the rule that fixes it mechanically, the per-class per-trade translation beside the 2.11 and 0.98 cost bars, and what ε does and does not mean: it is the smallest edge that would fund the Topstep funnel at 2 micros under the robust null, not the cost bar; a member can have a real edge below it; the claim is scoped to 2 micros.
4. **The data-quality rules** (Task 4c): the start rule (V_ref = median of the 14 monthly medians of RTH one-minute volume over 2025-04..2026-05 on the research parquet; S = first trade date of the earliest extension month from which every month through 2024-02 has median RTH one-minute volume ≥ 0.25 x V_ref; 0.15 and 0.40 reported descriptively; if no month qualifies D.1f stops with that finding); roll, degraded-day and calendar handling identical to the current pipeline with the CME calendar extended to 2019–2024 from CME's published schedules before any run; the cost model unchanged, with the early-era bias stated both ways (understated costs favour finding an edge, so conservative for a null claim and NOT for a positive finding, which needs a period-appropriate cost re-check before D.2 discussion); regime slices per calendar year descriptive only, 2020 included, nothing excluded before or after.
5. **Power and sample size** from Task 3, per class.
6. **The inconclusive rule and the out-of-scope list** (Task 1's).
7. **What the program may say if the null holds, and what it may not**: the bounded statement with both hashes and the descriptive resolution; never "MES has no edge", "intraday MES has no edge" or "MES is efficient", nothing about other sizes, instruments, fill types, horizons or constructions; if every class C1–C5 and C7 is null, the one aggregate sentence the document allows, with C6 pending and the structural question below ε left open where the power table says the data cannot resolve it.

Path and hash: `docs/NULL_CRITERIA.md`, sha256 `6f69e318c96edf0a58956856c881ec3e1b8c68d89e1c836b3d54cfbf0e3497e2`, read-only from 2026-09-22T08:50:46Z.


### Task 7 — decision packet

Numbers first; the user chooses.

**Option table**

| Option | Buys | Quote | Disk | Enables | Achieved null power at ε (binding member per class) | Still inconclusive after it |
|---|---|---|---|---|---|---|
| 0 Nothing | — | $0 | — | — | none: the 289 mined days cannot be used for confirmation | C1–C7 |
| A Minimal | MES ohlcv-1m 2019-05..2025-03 (71 chunks with data; the 2019-04 chunk is empty) | **$7.59** | 36 MiB, main drive | D.1f: sealing holdout-2, the start rule, the 58-test Tier A list, 43 Tier B statistics, per-class verdicts for C1–C5 and C7 | C1–C5 and C7 all reach 80% null power at ε at every start date; C3 only if S ≤ 2021-01-04 (needs 566 days) | C6 (needs order-book fills) |
| B Complete | A + MES MBO, full trade dates (17:00–16:00 CT, because C-H4 rests orders in every session), for N_C6 = 181 days | $7.59 + $181.00 scaled from the 5-day full-day mean ($199 with the +10% the 20-day block quote showed) = **$188.59 to $206.59** | + about 33 GiB est. on disk (101 GiB billable), LARGE STORAGE | A + D.1g: the C6 variant for C-H4 | as A, plus C6: C-H4 needs 181 full trade dates for 80% null power at ε | none at ε; the structural question below ε stays open for the low-frequency classes (table below) |
| MBO menu | full trade dates, 20 / 40 / 60 / 120 / 181 days (scaled from the 5-day full-day mean of $1.00; a 20-day block quoted whole came in 10% above the scaling) | $20.00 / $40.00 / $60.00 / $120.00 / $181.00 | 3.6 / 7.3 / 10.9 / 21.8 / 33 GiB est. | C-H4 null power at ε: 20 days 0.21; 40 days 0.32; 60 days 0.42; 120 days 0.65; 181 days 0.80 (Φ(ε√n / (SD √VIF) − 1.645) with C-H4's per-micro daily SD 190.54 ticks and VIF 0.927 from `reports/stage_d1e_power.json`); RTH-only books ($0.78 a day) cannot fill C-H4's ETH orders and are not an option | | |

**Power the extension buys, per class** (days supplied under the start rule's possible outcomes vs the binding member's need; the start date S is computed in D.1f by the fixed rule and cannot be chosen):

| Class | Binding member (null power) | Days needed (chosen n_b) | Days supplied 2019-05 / 2020-01 / 2021-01 / 2022-01 start | Null at ε reachable | Smallest per-trade edge excludable with the full extension (class range) |
|---|---|---|---|---|---|
| C1 | A-H4 rth leg | 149 | 1151 / 992 / 755 / 516 | yes at every start | 2.45 (A-H1 european-open overnight drift) to 23.62 (A-H3 weekend effect) ticks |
| C2 | G3.RTH.5 | 193 | 1151 / 992 / 755 / 516 | yes at every start | 0.30 (G2.ETH.5) to 14.00 (G3.RTH.5) ticks |
| C3 | F1_1_h1_RTH | 566 | 1151 / 992 / 755 / 516 | only if S ≤ 2021-01-04 | 0.02 (F1_1_h1_ETH) to 5.22 (G4.RTH.60) ticks |
| C4 | F2_4_15min_vol_tercile_top | 171 | 1151 / 992 / 755 / 516 | yes at every start | 0.46 (D-H3 range-compression gate) to 3.27 (D-H4 overnight gap fade) ticks |
| C5 | E-H1 scheduled macro drift | 16 | 1151 / 992 / 755 / 516 | yes at every start | 1.96 (E-H4 turn-of-month long) to 37.26 (E-H1 scheduled macro drift) ticks |
| C6 | C-H4 passive-fill reversal | 181 | 1151 / 992 / 755 / 516 | yes at every start | 0.15 (C-H4 passive-fill reversal) to 0.15 (C-H4 passive-fill reversal) ticks |
| C7 | H6 prior-close location follow-through | 114 | 1151 / 992 / 755 / 516 | yes at every start | 26.65 (H6 prior-close location follow-through) to 40.88 (H2 NR7 opening-range breakout) ticks |

**What remains underpowered even with all available history:** none at ε. At the cost-bar scale: the 41 members trading about once a day or less (all of C5, most of C1, the daily ORB and breakout trials and statistics in C2, the H tests) cannot be resolved below 2.11 ticks per trade with any purchasable MES history; E-H1 resolves to 18.6 ticks per trade, G3.RTH.5 to 14.0, A-H3 to 11.8, F6.1 to 7.5, A-H4 rth to 6.4.

**Questions the user must answer to proceed**
1. Spend: approve Option A ($7.59), Option B ($43.63), or A now and the MBO purchase later after D.1f's result. Each needs a quote-then-approve in the D.1f/D.1g prompt with the caps in data/config.py.
2. ε: accept ε_day = 34 net ticks per micro per day as derived (the rule is mechanical; changing it means changing the rule in docs/NULL_CRITERIA.md before D.1f, not after).
3. Family H: accept the six declared constructions as the C7 list (any change is a new declaration under a new hash).
4. Holdout-2 bounds 2024-04-01..2025-03-31 and the March 2024 embargo: accept, or choose a different contiguous block before D.1f downloads anything.
5. The start rule's fraction (0.25 x V_ref): accept; the date it yields is computed in D.1f and reported with the 0.15 and 0.40 sensitivities.
6. Whether D.1f's harness work (confirmation loader, parametrized holdout, calendar 2019–2024, F/G date-set parameter, the six H modules, the list runner) is built in a separate stage before the purchase, as the confirmation list's order of operations requires.


### Artifacts

- **Pre-registration (hashed, read-only):** `docs/NULL_CRITERIA.md` (sha256 6f69e318c96edf0a58956856c881ec3e1b8c68d89e1c836b3d54cfbf0e3497e2), `reports/stage_d1f_confirmation_list.md` (sha256 c19cbac191c497a10b5cc756e96510999f13f27c4ac1aa72593aeabf1125147c), `reports/stage_d1e_declaration_hashes.json`.
- **Reports:** `reports/stage_d1e_coverage.md`; `reports/stage_d1e_power.json` and `.md`; `reports/stage_d1e_power_verification.md` (with `reports/_d1e_power_verify_scratch.py`); `reports/stage_d1e_quotes.json` and `.md`; `reports/stage_d1e_power_gate_cells.json` and `.md`; `reports/stage_d1e_gate_extension.json`, `.log` and `_samples.npz`; `reports/stage_d1e_members_recorded.json` and `.md`; `reports/stage_d1e_members_trials.json`; `reports/stage_d1e_members_events.json`; `reports/stage_d1e_adversarial_review.md`; `reports/stage_d1e_adjudication.md`; `reports/_d1e_power_HANDOFF.md`; `reports/stage_d1e_STATE.md`.
- **Code:** `screening/runner.py` (three additive `ScreeningReport` fields: `trip_pnls_usd`, `daily_n_trips`, `trip_micros`; nothing else changed), `strategy/research/_d1e_members.py`, `_d1e_event_series.py`, `_d1e_gate_extension.py`, `_d1e_quotes.py`, `_d1e_power.py`, `_d1e_power_stats.py`, `_d1e_power_report.py`, `_d1e_calendar.py`.
- **Tests:** `tests/test_screening_runner.py` (+7), `tests/test_d1e_quotes.py`, `tests/test_d1e_power.py` (10 known-answer tests).
- **Ledger:** `ledger/databento_spend.jsonl` (+95 quote events, $0.00).
- **Docs:** `docs/STAGES.md` (D.1e entry; D.1f and D.1g as planned stages); `CLAUDE.md` (committed separately at the user's request: two-table ETA rule, role-based agent names, cumulative row).
- Not committed by this stage (the user commits after review): everything above except the two CLAUDE.md commits (50148c2, f1bb073).

### Session cost

Computed at the very end, after everything else in this entry was written. Token figures are raw counts from the transcripts (input + output + cache read + cache creation), summed per assistant message by model; they are not plan-credit percentages, which the session cannot read. Transcripts read: the first session's forked main file `0c13b8c3….jsonl` (its first 57 messages duplicate the `2df44c65….jsonl` stub, counted once) and its six worker files under `0c13b8c3…/subagents/`; this session's main file `fbadc349….jsonl` and its worker files under `fbadc349…/subagents/`.

**Wall clock.** Session 1: 00:33–01:40Z, 67 min of work, ended by the machine going down. Machine down 01:40–04:31Z (2 h 51 min, not work). Session 2: 04:32–08:55Z, of which the user's CPU pause 04:57–05:46Z (49 min) and the session rate limit 07:06–08:41Z (95 min) are not work: 2 h 4 min of work. Total work: 3 h 11 min.

**Final table (every task and every agent spawn; the estimate table printed at the start of session 2 put the stage end at 08:30Z from a 05:48Z resume, about 2 h 40 min of work; the actual is in the cumulative row).**

| # | Task | Agent name | Model | Effort | Start–end (UTC) | Time | Tokens total / output | Status, deviations |
|---|---|---|---|---|---|---|---|---|
| 1 | Session 1 lead: startup, context, planning, Task 5 and 6 drafts, coverage map begun | lead | fable | xhigh | 00:33–01:40 | 67 min | 32,530,701 / 476,385 | died with the machine; work on disk survived |
| 2 | 2a Tabulate power-gate cells | worker-medium (haiku) | haiku | medium | 00:50–00:51 | 1.2 min | 884,660 / 9,577 | done, 120 cells |
| 3 | 2b Gate extension script + T=1,2,4 | worker-high (opus) | opus | high | 00:51–01:13 agent; compute to 01:36 | 22.4 min agent, 47 min compute | 3,227,478 / 16,794 | compute killed by the crash two cells into T=8 |
| 4 | 4a/4b Availability and quotes | worker-xhigh (opus) | opus | xhigh | 00:57–01:13 | 15.7 min | 7,352,811 / 53,403 | done; 95 ledger quotes, $0.00 |
| 5 | 1b Runner fields + 31-trial re-run | worker-xhigh (opus) | opus | xhigh | 00:57–01:13 | 15.5 min | 6,937,064 / 24,647 | done; promoted from sonnet (touches screening/); its 2-micro unit assumption was the R-1 error |
| 6 | 1a Recorded-figure extraction | worker-medium (sonnet) | sonnet | medium | 00:58–01:02 | 4.0 min | 4,754,442 / 16,802 | done |
| 7 | 1c Event-series dump | worker-high (opus) | opus | high | 01:04–01:09 | 5.1 min | 2,940,504 / 20,595 | done; added subtask |
| 8 | Machine down | — | — | — | 01:40–04:31 | 2 h 51 min | — | not work |
| 9 | Session 2 lead: resume, coverage map, ε, briefs, fill-ins, adjudication, amendments, entry | lead | fable | xhigh | 04:32–08:55 | 2 h 4 min work | 91,725,033 / 1,018,950 | two pauses shown below |
| 10 | 2b' Gate extension T=8,16,32 (background compute) | lead inline | — | — | 04:38–04:56, 05:46–06:36 | 68 min compute | — | resumed from its JSON; suspended during the CPU pause; ε unchanged |
| 11 | 3a Power code, first pass | worker-high (opus) | opus | high | 04:47–04:59 | 12.1 min | 7,149,689 / 59,063 | paused before the run at the user's request |
| 12 | User CPU pause | — | — | — | 04:57–05:46 | 49 min | — | not work |
| 13 | 3a Power code resume, rulings, ε=34 run, max rule, resolution ranges | PowerCoder-OpusHigh | opus | high | 05:46–06:01 | 15.4 min | 6,354,712 / 47,286 | done; 10 tests |
| 14 | 3b Verification of every power number | NumberVerifier-FableXHigh | fable | xhigh | 06:02–06:21 | 19.6 min | 13,413,127 / 91,171 | VERIFIED on all sections |
| 15 | 5d Adversarial review | AdvAuditor-FableMax | fable | max | 06:23–06:50 | 27 min | 14,356,521 / 121,383 | 55 findings, NOT READY; all adjudicated |
| 16 | R-1 fix: runner trip_micros + per-micro re-run | TripMicrosFixer-OpusXHigh | opus | xhigh | 06:57–07:06 | 9.1 min | 8,799,164 / 38,586 | done; continuity to the cent |
| 17 | 3a Power re-run at the per-micro unit | PowerCoder-OpusHigh | opus | high | 07:07–07:10 | 2.7 min | 2,760,826 / 11,044 | done; 62 figures moved upward |
| 18 | Session rate limit (Fable) | — | — | — | 07:06–08:41 | 95 min | — | not work; two workers cut off and resumed |
| 19 | 3b Re-verification after the unit correction | NumberVerifier-FableXHigh | fable | xhigh | 08:41–08:46 (a 07:05–07:06 attempt was cut off by the limit, 1,294,377 tokens) | 5.5 min | 7,633,424 / 21,050 | VERIFIED on all five items |
| 20 | 5d Re-review of the amended documents | AdvAuditor-FableMax | fable | max | 08:41–08:49 | 8.3 min | 8,543,899 / 38,622 | 52 resolved, 3 partly, 10 new; READY TO HASH after the carve-outs, which were applied |
| 21 | Hash, entry, STAGES.md, end guardrails, cost | lead | fable | xhigh | 08:46–08:55 | 9 min | (in row 9) | done |
| **Σ** | **Whole stage** | 7 distinct workers, 12 spawns or resumes | | | 00:33–08:55 | **3 h 11 min of work** (+ 5 h 11 min of outages and pauses) against the 05:48Z estimate of about 2 h 40 min from the resume | **220,658,432 / 2,068,745** | lead 124,255,734 (56.3%), workers 96,402,698 (43.7%) |

**Tokens per model (both sessions, lead plus workers):**

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-fable-5-1 (lead both sessions + 2 fable workers) | 14,826 | 1,770,948 | 152,636,399 | 15,074,909 | 169,497,082 |
| claude-opus-5 (8 spawns or resumes) | 796 | 271,418 | 42,054,129 | 3,195,905 | 45,522,248 |
| claude-sonnet-5 (1) | 102 | 16,802 | 4,508,252 | 229,286 | 4,754,442 |
| claude-haiku-4-5 (1) | 142 | 9,577 | 700,681 | 174,260 | 884,660 |
| **All** | 15,866 | 2,068,745 | 199,899,461 | 18,674,360 | **220,658,432** |

**Per worker spawn:** rows 2 to 7 and 11 to 20 above.

**Delegation share:** lead 124.3M tokens (56.3%), workers 96.4M (43.7%); by tier, fable 169.5M (76.8%: lead 124.3M, verifier 22.3M, reviewer 22.9M), opus 45.5M (20.6%), sonnet 4.8M (2.2%), haiku 0.9M (0.4%). Cache reads are 90.6% of every figure; output tokens, the part a model actually wrote, are 2.07M in all, of which the lead wrote 1.50M (72%). The two Fable workers (verification and adversarial review) cost more than all eight opus spawns together, which is the price of routing the verdict-bearing checks to the strongest model; the review's 65 findings, one of them a factor-of-four unit error the lead and two opus workers had all missed, are what that bought.

## 2026-09-23 — Stage D.1f (build): harness build and freeze, no purchase

**Built, tested and hash-froze every piece of the confirmation harness; bought nothing, quoted nothing, ran nothing on new data, N stays 31.** This session did steps 1 and 1b of the frozen confirmation list's order of operations (reports/stage_d1f_confirmation_list.md 1.5) and stopped. It built the confirmation-window loader and screening path, holdout-2 sealing with a seal-on-arrival puller, the 2019–2024 CME calendar with a coverage assertion and the step-4b validator, the confirmation bar build, the statistics wrapper, the six Family H modules, the 2019–2024 macro release table with the declared E-H amendment, and the list runner with its preflight. It then wrote the harness-freeze manifest: **reports/stage_d1f_harness_freeze.json, 129 files, sha256 `ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a`**. The test suite went from 543 to 898 passing (355 new tests, 1 xfail unchanged). A Fable verification and a Fable max adversarial review found 0 blockers. All 8 should-fix findings were accepted and fixed before the freeze.

Lead: Opus 5.5 at xhigh. Ultracode off. All times are Vancouver local (PDT), at the user's instruction during the session. The session ran 2026-09-22 23:39 to 2026-09-23 05:07 PDT. It includes a Fable session-limit pause of 3 h 12 min (01:19–04:31 PDT), which is not work.

### THE RUN SESSION CANNOT START UNTIL THE USER COMMITS THE FREEZE

- **Commit the freeze first.** The run session cannot start until the user commits reports/stage_d1f_harness_freeze.json together with every file it lists; that is 29 harness files not yet committed (12 modified, 17 new). The runner's git anchor refuses otherwise (review finding F4). Suggested scope: `git add -A data screening funnel strategy tests reports docs/STAGES.md progress.md`, after review. Any change to a listed file after the commit voids the run; a re-run is a new declaration under a new name.
- **Freeze manifest sha256:** `ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a`. The run prompt must quote it. The runner requires it: `OPENBLAS_NUM_THREADS=1 uv run python -m strategy.research._d1f_confirmation --step all --manifest-sha256 ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a` (`--step preflight` checks without running).
- **data/config.py D.1f spend settings:** `STAGE_D1F_SESSION_ID = "stage-D.1f-2026-09"`, `D1F_SESSION_CAP_USD = 10.00`, `D1F_REQUEST_CAP_USD = 10.00`. These cover the $7.59 history and nothing more; the order-book purchase cannot fit under them. `EXTERNAL_LEDGER_PATHS` was repointed to the archived MLCryptoEngine ledger at `/mnt/large-storage/Archive/GitHub/MLCryptoEngine/data/vendor/spend_ledger.jsonl`. The old sibling path is gone, and the gate would have failed closed on the purchase. The gate now reads $84.006048 shared, $0 this session. **data/config.py is inside the freeze: changing any of these values means re-running `uv run python -m strategy.research._d1f_freeze` before the commit, and quoting the new sha256.**

### Guardrails

| Check | Start (23:39 PDT) | End (05:04 PDT) |
|---|---|---|
| `uv run python -m data.holdout status` | holdout-1 all_ok true, unlocks_logged 0 | holdout-1 all_ok true, unlocks_logged 0; holdout-2 section present: state not_yet_sealed, 0 chunks, unlocks_logged 0 (all_ok false by design until sealed) |
| docs/HOLDOUT2_MANIFEST.json, data/sealed/MES_holdout_v2 | absent | absent (no real sealing) |
| REGISTRATION.md | 0 bytes | 0 bytes |
| Declaration hashes (list c19cbac1…147c, criteria 6f69e318…97e2) | match | match; both files untouched |
| Databento | — | **zero calls of any kind, $0.00**; ledger unchanged; every vendor path stubbed in tests |
| H modules on real bars (R-7) | — | never; no look to log |
| N | 31 | 31 |
| git | clean at 9cbd815 | no commit; dirty with this stage's files only |
| rules/, live/, ops/, sim/, TopstepX | untouched | untouched |

Every modified file is on the list's allowed set (§5.8), plus data/config.py (list 1.5 NEW-5 and the stage prompt). The runner's own logic went into five `_d1f_*` modules, not the one file §5.8 names, to respect the 800-line cap. Every `_d1f_*` file is inside the manifest, and the preflight refuses any unlisted `.py` (deviation of form, logged).

### Delegation record

| Task | Agent | Model / effort | Outcome | Deviation |
|---|---|---|---|---|
| 0 Startup, plan, constants, config | lead | opus xhigh | STATE file, D.1f date constants in data/research_bars.py, spend constants | estimate table printed just after the first spawn, not before |
| 2 Holdout-2 + puller | HoldoutSealer-OpusXHigh | worker-xhigh / opus | done | — |
| 1 ConfirmationWindow | WindowLoader-OpusXHigh | worker-xhigh / opus | done | — |
| 3a Calendar citations | CalendarExtractor-SonnetMed | worker-medium / sonnet | 71 rows | — |
| 6a Release citations | ReleaseExtractor-SonnetMed | worker-medium / sonnet | 154 rows | — |
| 5 Six H modules | HModuleCoder-OpusXHigh | worker-xhigh / opus | done | one worker for all six, not one per pair (shared mechanics, one look-ahead surface); xhigh, not high |
| 3b Calendar code, bar build, step-4b validator | BarBuilder-OpusXHigh | worker-xhigh / opus | done | the build and validator were not separate prompt tasks but must be frozen before the purchase |
| 4 + 6b Wrapper, release table, E-H amendment | StatsWrapper-OpusHigh | worker-high / opus | done | amendment given to the wrapper worker |
| 7 List runner + freeze script | ListRunner-OpusXHigh | worker-xhigh / opus | done | split into five `_d1f_*` modules |
| 8a Verification | SealVerifier-FableXHigh | worker-xhigh / fable | 0 blocker, 2 should-fix, 7 notes | — |
| fixes 8a | FixApplier-OpusXHigh | worker-xhigh / opus | done | fixes applied BEFORE 8b so the review saw final code |
| 8b Adversarial review | AdvAuditor-FableMax | worker-max / fable | 0 blocker, 6 should-fix, 9 notes; READY TO FREEZE on conditions | cut off by the Fable session limit 01:19 PDT, resumed with context at 04:31 |
| fixes 8b | FreezeHardener-OpusXHigh | worker-xhigh / opus | done | — |
| 9 Freeze, suite, entry | lead | opus xhigh | manifest, this entry | — |

Concurrency never exceeded four. Fable was used exactly twice, for 8a and 8b, as the prompt specified.

### What was built, and what the tests prove

**Task 1, the confirmation window (list 5.1).** data/research_bars.py gained a `trade_date_class` map covering every date since MES began, with no gaps and no overlaps: confirmation, embargo-2, holdout-2, research, research embargo and holdout-1. On top of it sits `load_confirmation_bars`. It filters to 2019-05-01..2024-02-29, then re-checks every returned row, refusing holdout-1, holdout-2, embargo-2 and mined dates, and asserts max ≤ 2024-02-29 (list 5.2 iv). The research loader now also refuses holdout-2, embargo-2 and confirmation dates. `screen_candidate` accepts a `ConfirmationWindow`, built with `confirmation_window(S)`. On that path, bars come only through the confirmation loader, splices come from the confirmation parquet's metadata, and the drift path and session benchmark are recomputed on those bars in their own cache. The train-union path is byte-for-byte the old code path. funnel/null_generator.py's refusal now accepts all-research or all-confirmation frames only, never a mix. screening/drift.py needed no change. The tests cover:
- every refusal, in both directions;
- a synthetic 2021 parquet with a roll, screened end to end, with the benchmark and drift checked by hand;
- E-H3 on the train union reproducing stage_d1d_accounting.json to the cent;
- three planted bugs, all caught.

**Task 2, holdout-2 sealing (list 5.2).** data/holdout.py has a second `HoldoutPaths` (data/sealed/MES_holdout_v2/, docs/HOLDOUT2_MANIFEST.json, the same unlock log and REGISTRATION.md). Sealing is per chunk, oldest first, and happens inside the download call before the next request. Before anything is removed, the round trip is proved, and the sealed blob and the plaintext are hashed. The manifest records bytes and sha256 only, with no dates or row counts. The code refuses to seal out of order, twice, or a chunk outside the 13. Holdout-2 unlocks must name "holdout 2", and unlocks are counted per holdout. `status` reports both holdouts, and holdout-1's keys are unchanged.

data/pull_mes.py `--d1f-pull` buys the 71 chunks oldest first and refuses to re-buy anything in either manifest or on disk. A per-request cap is enforced in a gate subclass, because spend_gate.py is not on §5.8. The resume path decodes a found chunk once before sealing it. Interrupted seals complete through the same proof, and any sealing error stops the pull with a clear message.

Byte paths: `fetch_range` writes `<target>.partial` and hard-links it to the target. databento 0.82.0 has no cache and uses no tempfiles, and a test pins that to the installed version.

The tests assert all five mandatory points: no plaintext of any sealed chunk under the repo, /tmp or the client's cache, searched by content, with a positive control finding the 58 kept chunks; 13 manifest records with both hashes; verify_seal all_ok; the loader refusals; and status reporting both holdouts. The deliberately broken versions of the sealing code (14 by the worker, 6 more by the verifier) were all caught.

**Task 3, the CME calendar 2019–2024 (list 5.3).** data/cme_calendar.py has 68 entries, each citing its source verbatim in `SOURCES_2019_2024`. Of those, 64 carry a CME-direct status source, 3 a secondary one and 1 is unverified; three days CME shows as normal are recorded as no-entry findings. The 2025–2026 entry lines are byte-identical to 9cbd815, checked by `ENTRIES_2025_2026_SHA256` and by the runner against the file at that commit. The whole file's hash moved from 5f24edda to d2aca685 only because the file grew. `CALENDAR_COVERAGE` now runs 2019-01-01..2026-12-31 and is asserted in `add_flags` for every built date. `data.validate.validate_calendar_step4b` implements step 4b's three checks, as a callable the run session invokes. data/build_mes_bars.py `--confirmation` does the following:
- reads only the 58 unsealed chunks;
- stamps the raw symbol mapped on the bar's UTC date;
- drops only bars with no MES outright on that date, logging the drops per month and setting `stop_for_lead_decision` for any drop from 2019-05-06 on;
- drops trade dates after 2024-02-29;
- validates;
- runs step 4b;
- writes the parquet read-only with the manifest sha256 stamped in;
- freezes the dataset-condition and symbology fetches once, and compares the degraded list with the eight declared dates.

Tests: 29.

**Task 4, the statistics wrapper (list 5.4).** strategy/research/_d1f_statistics.py calls the two hashed builders with any date set, exactly as `_d1e_event_series.py` does. The hashed modules were not edited. For each of the 64 directional statistics the wrapper returns per-event values, trade dates and forward intervals, plus the descriptive facts. On the 139 EDA dates it reproduces all 57 F and 28 G records, Q80, G0, F3.1, reports/stage_d1e_members_events.json and every per-event value to 1e-9.

**Task 5, the six Family H modules (list 2.1 A3, 5.5).** strategy/research/h_daily_bar/ has one shared `_mechanics.DailyBarStrategy` and six thin modules; each module holds its constants, a pure `condition()` and a no-argument factory. `H_TRIALS` carries the labels exactly as the table writes them. Day d's daily bar enters the history only when a later trade date's first bar arrives. The condition and the instrument guard are evaluated on day d's 08:30 bar. Tests (50):
- the look-ahead pair per module (day d scaled: condition unchanged; d-1 replaced: the hand-computed change);
- a second, stronger day-d replacement that changes the tick range and CLV (verifier N1);
- timing (OR window, fill at the next open, exit at or after 14:58, forced-exit logging);
- the no-trade cases (early halt, incomplete day, 24 of 30 OR bars, a roll across d-1/d);
- one known answer per module to the cent at 2 micros in the size-5 bucket.

Planted bugs: 38 by the worker (every behaviour-changing one caught) and 8 by the verifier (all caught). The verifier re-derived H1 and H6 by hand to the cent: 263 and 255 cents in side costs, net 982 and 1,964 cents. **No H module ran on real bars at any time.**

**Task 6, the release table and the E-H amendment (list 5.7).** strategy/research/e_calendar_event/_release_table_2019_2024.py covers 2019-05-01..2024-02-29 with 151 entries: 35 FOMC statements at 14:00 ET, 58 CPI and 58 Employment Situation releases at 08:30 ET. All are primary-grade, and each has its verbatim quote and URL. The unscheduled 2019–2020 actions are excluded and listed. Two dates carried both FOMC and CPI (2019-12-11 and 2020-06-10); the lead ruled to keep the earliest release, CPI at 08:30 (choice 6.1). Tests: 30. The declared amendment is in the next section.

**Task 7, the list runner (list 5.6).** The runner is `strategy/research/_d1f_confirmation.py` plus `_d1f_preflight.py`, `_d1f_start_rule.py`, `_d1f_members.py`, `_d1f_decisions.py` and the manifest writer `_d1f_freeze.py`. It runs steps 5 to 8 (start rule, continuity, list, decisions). Each step writes once and nothing re-runs after step 8.

The preflight runs before every step and again after step 8. It checks:
- the required `--manifest-sha256` value;
- the declaration hashes, and that the criteria embed the list's hash;
- every manifest file, with any unlisted `.py` under the harness directories refused;
- the git anchor over every listed path;
- the section-0 hashes, with the E-H literals and the calendar block;
- the build summary (stop flag, step 4b, degraded comparison, manifest stamp);
- both holdouts clean;
- the run-session inputs pinned at step 5 (the parquet, build summary, vendor JSON files and HOLDOUT2_MANIFEST).

Every output header records the manifest sha256 and the Python and library versions. The decision rules implement 3.1–3.6 as written, plus the lead's rulings listed under open choices. Tests: 37 + 35 + 11. They cover a planted edge that passes, a zero edge that comes out null, few and zero events (inactive or inconclusive), SE = 0, one inconclusive member blocking its class, C6 staying inconclusive, every tampered hash refusing, a hand-checked bootstrap, the start rule including its stop case, the exact per-micro trip partition, forced exits counted from the ledger, and the freeze file set.

Continuity for all 31 trials (step 6) is a run-session step. In this session the train-union reproduction was exercised for E-H1, E-H2 and E-H3 only, which the prompt sanctioned.

**Suite:** 543 passed at the start; 898 passed and 1 xfailed at the end (224 s). The 15 leakage canaries pass. New tests per file: confirmation_window 66, holdout2 81, calendar_build 29, statistics 16, release_table 30, h_daily_bar 50, confirmation 37, preflight 35, runner_hardening 11.

### The declared E-H amendment (list 5.7, NEW-1)

| Module | Pre-amendment sha256 (section 0) | Post-amendment sha256 |
|---|---|---|
| strategy/research/e_calendar_event/h1_scheduled_macro_drift.py | 94e92ff15efe2160c5e967da6d1a415385681a43cf500505004b87b363ab25b2 | f28529f058e9a6cc63d1030f6e08ce1b78e7c11c7f89ad64aa583468e1eb7a35 |
| strategy/research/e_calendar_event/h2_post_release_momentum.py | b2f09ab6e71dafe554c8db35c04a02f3476cb25e0f3783ca740ebffc19b5f005 | 7183d9bda56b36b9089b05b9ee02cbd9609392f29d88f14ca005fb6bb341aeca |

The diff is identical in both files. One field was added: `release_table: dict[date, datetime] = field(default_factory=lambda: RELEASE_TABLE_ET, repr=False, compare=False)`. One lookup changed from `RELEASE_TABLE_ET.get(...)` to `self.release_table.get(...)`. Nothing else changed.

Reason: the modules read a module-level table with no hook, so they could not fire on 2019–2024 dates (N-1). Both reproduce stage_d1d_accounting.json on the train union to the cent, under the no-argument factory and under the combined-table factory. Reverting the edit as text restores the old hash. The confirmation factories are the list's verbatim lambdas, and the post-amendment hashes are literals in the preflight and recorded in the manifest's `declared_amendments`.

### Task 8: findings and rulings

**8a verification (Fable xhigh, reports/stage_d1f_verification.md).** All five sealing assertions were verified against the real code paths, not the docstrings. The H1 and H6 known answers were re-derived by hand to the cent. Result: 0 blockers.

| Finding | Ruling |
|---|---|
| D1 resume path sealed without the record-byte decode | accepted, fixed |
| D2 interrupted seal had no automated completion | accepted, fixed (`complete_interrupted_seal`, same proof plus two stricter checks) |
| N1 the ×1.01 scaled copy leaves tick ranges unchanged | accepted: added a stronger replacement test |
| N2 "holdout 2" was optional in the stage argument | accepted, stricter: now required for holdout-2 |
| N7 unclear message on a sealing error | accepted, fixed |
| N3–N6 | noted |

**8b adversarial review (Fable max, reports/stage_d1f_adversarial_review.md).** Result: 0 blockers, 6 should-fix, 9 notes. Verdict: READY TO FREEZE, provided F1–F3 are applied and F4–F6 are decided.

| Finding | Ruling |
|---|---|
| F1 an edit plus a re-freeze passed every check | accepted: required `--manifest-sha256`; E-H hashes as literals |
| F2 the pull and build ran unverified code | accepted: file-hash preflight before any vendor call; manifest stamp in the build |
| F3 `strategy/research` had no `__init__.py` | accepted, broadened: an empty one added; every `*.py` under the harness directories pinned; unlisted ones refused |
| F4 the git anchor covered the manifest only | accepted: covers every listed path |
| F5 run-session inputs unpinned across steps | accepted: pinned at step 5, re-checked at every later step |
| F6 H forced exits undercounted in two rare patterns (P&L unaffected) | accepted: counted from the ledger, differences flagged |
| N5 versions not recorded | accepted |
| N6 docs/HOLDOUT_MANIFEST.json outside the manifest | accepted |
| N7 the frozen config pointed to a missing ledger | accepted; the lead repointed it (reverses choice 0.4) |
| N1–N3, N8, N9 | noted |
| N4 two fail-closed residues | carried into the checklist below |

### Freeze manifest

- **Path:** reports/stage_d1f_harness_freeze.json. Generated 2026-09-23 05:03:25 PDT by `uv run python -m strategy.research._d1f_freeze`.
- **Size:** 129 files.
- **Own sha256:** `ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a`.
- **Contents:** every `*.py` under screening/, sim/, funnel/, rules/, data/ and strategy/; sim/slippage_calibration.json; every section-0 file, including reports/power_gate.json and the E-H modules at their declared hashes; the list, the criteria and the declaration-hashes JSON; the two recorded-facts files; docs/HOLDOUT_MANIFEST.json; pyproject.toml and uv.lock.
- **Preflight at freeze time:** it refuses only because the files are not yet committed, the build summary is missing and holdout-2 is not yet sealed. There is no hash mismatch.

### What the run session must do first (checklist)

1. The user reviews and commits the freeze, with the harness (above). The run prompt quotes the manifest sha256.
2. Start and end with `uv run python -m data.holdout status` for both holdouts. Run everything with `OPENBLAS_NUM_THREADS=1` (review N5).
3. Pull: `uv run python -m data.pull_mes --d1f-pull`. It buys oldest first, seals the 13 holdout-2 chunks on arrival, and refuses any request over $10.00 or a session over $10.00 (history quoted at $7.59). Record the holdout-2 calendar trade-date count at sealing (choice 2.1), not a count taken from the bars. The D.1f rolls and symbology fetches are free.
4. Manual residues (review N4). If a holdout-2 chunk's decode fails, the plaintext stays at its target: inspect it, delete it deliberately and re-pull, and never seal a chunk whose decode failed without a lead decision. A truncated `.partial` left by a crash is removed by the next fetch. Both show up in `status` as `unsealed_plaintext_present`.
5. Build: `uv run python -m data.build_mes_bars --confirmation` (exit code 7 means stop for a lead decision). Step 4b discrepancies caused by thin 2019 trading, or by the pre-2021-06-28 session (a 15:15–15:30 CT pause and a 16:15 CT close; the frozen session.py halts at 16:00) are expected risks. The list's procedure applies: correct the calendar, re-hash it into a new freeze manifest, log the change, all before step 5.
6. The runner, with `--manifest-sha256`, runs steps 5 to 8.

### Open choices the lead made on its own (the user can overturn any before committing)

- **0.1** The spend constants as instructed. The per-request cap lives in data/pull_mes.py because spend_gate.py is outside §5.8.
- **0.2** The D.1f date constants live in data/research_bars.py, not data/splits.py (not on §5.8).
- **0.3** The research path also refuses holdout-2, embargo-2 and confirmation dates.
- **N7 (reverses 0.4)** data/config.EXTERNAL_LEDGER_PATHS was repointed to the archived MLCryptoEngine ledger.
- **1.1** screening/__init__.py was not changed (it is not on §5.8); the runner imports from screening.runner.
- **2.1** The holdout-2 trade-date count at sealing comes from the calendar, never from the sealed bytes.
- **2.2–2.4** Cosmetic adapter messages, stale line numbers in a D.1e report, and chunk-by-chunk D.2 unseals all left as they are.
- **5.1** H readings: early_halt_ct is read from bars dated d; the CT windows count only bars dated d; d-1 is the latest complete bar before d; the exit window is [14:58, the no-new-positions time).
- **6.1** Release collisions keep the earliest release, CPI at 08:30, on 2019-12-11 and 2020-06-10; two FOMC events are dropped.
- **6.2** Calendar calls:
  - 12:00 CT settlement lines are read as 12:15 CT halts, graded inferred;
  - the Good Friday 2021 08:15 time and New Year's Day 2021 are marked unverified;
  - there is no entry for 2020-07-02, 2021-07-02 or 2022-01-03.
- **6.3** The raw-symbol rule reads the bar's UTC date; symbology is fetched once and frozen.
- **6.5** Section 0's calendar line is checked through the 2025–2026 block, compared with the file at 9cbd815.
- **7.3** F4.4 drift across the halt sums the per-minute window means over every covered clock minute, with halt minutes counted as 0; the interval starts at the crossing bar's open.
- **8.1** The runner's interpretations, each the literal or stricter reading:
  - statistics use their own post-exclusion dates;
  - the anomaly test requires mean v ≥ 2.11;
  - the class per-trade epsilon uses the median trades per day of the class's trial members;
  - continuity also checks trip counts and daily Sharpe to 1e-6;
  - S must be 2019-05-06 if M* is 2019-05.
- **8.2 (c')** A Tier B sign reversal is tested on the gross series s·e, with Benjamini–Hochberg at 10%.
- **Runner rulings (a)–(e):**
  - PBO aligns members on the full window with 0 outside each member's own dates;
  - at N = 101, DSR uses the 101-member Sharpe variance and PBO the 101 series; at N = 186, DSR only (the D.1d method);
  - SE_boot uses ddof 0;
  - each year slice is bootstrapped with a fresh generator;
  - drift across the halt as in 7.3.
- **8b F3 broadened**, as recorded above.

Full detail is in reports/stage_d1f_build_STATE.md.

### Artifacts

- **Freeze:** reports/stage_d1f_harness_freeze.json, strategy/research/_d1f_freeze.py.
- **Code:** data/research_bars.py, data/holdout.py, data/pull_mes.py, data/cme_calendar.py, data/bars.py, data/validate.py, data/build_mes_bars.py, data/config.py, screening/runner.py, funnel/null_generator.py, the two E-H modules; new: strategy/research/__init__.py (empty), strategy/research/h_daily_bar/ (8 files), strategy/research/_d1f_{confirmation,preflight,start_rule,members,decisions,statistics,freeze}.py, strategy/research/e_calendar_event/_release_table_2019_2024.py.
- **Tests:** the nine tests/test_d1f_*.py files (355 tests).
- **Reports:** reports/stage_d1f_build_STATE.md, reports/stage_d1f_calendar_sources.{json,md}, reports/stage_d1f_release_sources.{json,md}, reports/stage_d1f_verification.md, reports/stage_d1f_adversarial_review.md.
- **Docs:** docs/STAGES.md (one line).
- **Not committed:** the user commits after review.

### Session cost

Computed at the end from this session's transcript, `6c08762d-eea5-4ab5-95fb-7aa3c5b91a62.jsonl`, and its 12 worker files under `6c08762d…/subagents/`. For each assistant message id, the last streamed record is summed (input + output + cache read + cache creation) and grouped by model. These are raw token counts, not plan-credit percentages. The lead's figure is cut at 05:04 PDT; the entry-writing turns after that are not in it.

**Wall clock.** 23:39–05:07 PDT is 5 h 28 min. Of that, the Fable session-limit pause (01:19–04:31 PDT, 3 h 12 min) is not work. **Work: 2 h 16 min**, against the initial estimate of 3 h 45 min.

**Final table** (initial estimate at 23:45 PDT: end 03:25 PDT, 3 h 45 min of work)

| # | Task | Agent | Model | Effort | Start–end (PDT) | Time | Tokens total / output | Status, deviations |
|---|---|---|---|---|---|---|---|---|
| 0 | Startup, plan, constants, config | lead | opus | xhigh | 23:39–23:47 | 8 min | (lead row) | done |
| 1 | Holdout-2 + puller | HoldoutSealer-OpusXHigh | opus | xhigh | 23:45–00:07 | 22 min | 7,982,844 / 141,803 | done; 61 tests |
| 2 | ConfirmationWindow | WindowLoader-OpusXHigh | opus | xhigh | 23:45–23:58 | 13 min | 6,406,788 / 68,053 | done; 66 tests |
| 3 | Calendar citations | CalendarExtractor-SonnetMed | sonnet | medium | 23:45–00:00 | 15 min | 13,719,461 / 68,054 | done; 71 rows |
| 4 | Release citations | ReleaseExtractor-SonnetMed | sonnet | medium | 23:46–23:52 | 6 min | 3,086,019 / 50,801 | done; 154 rows |
| 5 | Six H modules | HModuleCoder-OpusXHigh | opus | xhigh | 23:52–00:20 | 28 min | 9,536,716 / 144,233 | done; one worker, not three |
| 6 | Calendar code, bar build, 4b | BarBuilder-OpusXHigh | opus | xhigh | 00:01–00:27 | 26 min | 10,497,119 / 132,205 | done |
| 7 | Wrapper, release table, amendment | StatsWrapper-OpusHigh | opus | high | 23:59–00:26 | 27 min | 13,078,503 / 139,622 | done |
| 8 | List runner + freeze script | ListRunner-OpusXHigh | opus | xhigh | 00:27–00:51 | 24 min | 12,701,649 / 141,651 | done; five modules |
| 9 | 8a Verification | SealVerifier-FableXHigh | fable | xhigh | 00:21–00:38 | 17 min | 3,206,735 / 70,195 | 0 blockers |
| 10 | 8a fixes + ruling c' | FixApplier-OpusXHigh | opus | xhigh | 00:51–01:07 | 16 min | 10,379,341 / 77,883 | done |
| 11 | 8b Adversarial review | AdvAuditor-FableMax | fable | max | 01:08–01:19, 04:31–04:39 | 19 min | 5,895,754 / 85,253 | 0 blockers; cut off by the limit, resumed |
| 12 | Fable session-limit pause | — | — | — | 01:19–04:31 | 3 h 12 min | — | not work |
| 13 | 8b fixes | FreezeHardener-OpusXHigh | opus | xhigh | 04:40–04:59 | 19 min | 11,115,975 / 98,305 | done |
| 14 | Suite, freeze, guardrails, entry, cost | lead | opus | xhigh | 04:59–05:07 | 8 min | (lead row) | done |
| L | Lead, whole session | lead | opus | xhigh | 23:39–05:04+ | — | 26,090,118 / 115,093 | orchestration, rulings, checks |
| **Σ** | **Whole stage** | 12 worker spawns (one resumed) | | | 23:39–05:07 | **2 h 16 min of work** (+ 3 h 12 min pause) vs 3 h 45 min estimated | **133,697,022 / 1,333,151** | lead 26.1M (19.5%), workers 107.6M (80.5%) |

**Tokens per model:**

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 (lead + 8 workers) | 992 | 1,058,848 | 103,253,596 | 3,475,617 | 107,789,053 |
| claude-sonnet-5 (2 workers) | 218 | 118,855 | 16,213,856 | 472,551 | 16,805,480 |
| claude-fable-5-1 (2 workers) | 872 | 155,448 | 7,452,140 | 1,494,029 | 9,102,489 |
| **All** | 2,082 | 1,333,151 | 126,919,592 | 5,442,197 | **133,697,022** |

**Delegation share:** lead 26.1M (19.5%), workers 107.6M (80.5%). By tier: opus 107.8M (80.6%), sonnet 16.8M (12.6%), Fable 9.1M (6.8%). Fable spent **9.1M tokens, 5.4% of Stage D.1e's 169.5M**, as the prompt intended. One process note: the sonnet calendar extractor cost more than most opus coders (13.7M), because web extraction re-reads long pages. The Fable limit hit at 01:19 PDT came from the plan's shared Fable slice; this stage had drawn only about 5M Fable tokens by then.

## 2026-09-23 — Stage D.1f (run): the frozen confirmation list on MES, 2020-02-03 to 2024-02-29

**Bought the MES history for $7.586199 (as quoted), sealed holdout-2 on arrival (13 chunks, all_ok, 0 unlocks), corrected one calendar error through the sanctioned step-4b path, and ran the frozen list once. No member passes confirmation. Every one of the 100 members outside C6 has its one-sided 95% upper bound below ε = 34 net ticks per micro per day with achieved null power of at least 0.997, so classes C1 to C5 and C7 are null under docs/NULL_CRITERIA.md; C5 carries the "null by inactivity" label (E-H3, 16 trips); C6 stays inconclusive until Stage D.1g by design.** The start rule gave S = 2020-02-03, so the confirmation window is 2020-02-03 to 2024-02-29: 1,055 trade dates for trials and 998 post-exclusion dates for the statistics, several times what every class needed. Holm over the 58 Tier A p-values rejects nothing; the smallest one-sided p is 0.137 (E-H1), no composite verdict passes, the largest daily t is 1.13 and every DSR at N = 58 is 0.0. Step-4b calendar validation failed on the first build with 12 discrepancies, all from one cause: the 2019-2023 Independence Day sessions were listed as full closures, while CME's own Globex holiday schedules and the bars both show a 12:00 CT halt. The five entries were corrected with CME citations, the harness re-frozen (manifest ba5b34d5… → d3bd21e5…) and committed as 14c1007, and the rebuild passed step 4b. N is now 58. The independent Fable check re-computed every verdict-bearing number and found no discrepancy.

Lead: Opus 5.5 at max effort. Ultracode off. All times are Vancouver local (PDT). The session ran 2026-09-23 16:34 to 18:07 PDT with no pause.

### Guardrails

| Check | Start (16:34 PDT) | After sealing (16:56 PDT) | End (18:04 PDT) |
|---|---|---|---|
| holdout-1 (`uv run python -m data.holdout status`) | all_ok true, unlocks_logged 0, research_has_no_holdout_rows true, 4 chunks sealed with plaintext absent | same | same |
| holdout-2 | state not_yet_sealed, 0 of 13, unlocks_logged 0 (all_ok false by design) | **sealed, 13 of 13 in order, all_ok true, plaintext absent for all 13, unlocks_logged 0** | same, plus confirmation_has_no_holdout2_rows true |
| docs/HOLDOUT_UNLOCK_LOG.md | — | +13 "SEALED holdout 2" records, no UNLOCK | same |
| REGISTRATION.md | 0 bytes | — | 0 bytes |
| Freeze manifest and preflight | ba5b34d5… matches; preflight refused only "build summary missing" and "holdout-2 not sealed" | — | d3bd21e5… after Task 3; the full preflight passes |
| Databento | shared $84.006048; ledger readable at the archived MLCryptoEngine path | session $7.586199 (only the ohlcv-1m history), shared $91.592247 | unchanged |
| git | clean at 11fe0ea (d384bfe plus the run prompt) | — | 14c1007 (Task 3: exactly 2 files); run artifacts uncommitted |
| rules/, live/, ops/, sim/, screening/, funnel/, strategy/, TopstepX | untouched | — | untouched (git status shows nothing there) |
| AiTrader collector window (15:15–16:15 PT) | the session began at 16:34 | — | no job in the window |
| N | 31 | — | 58 |

### Delegation record

| Task | Agent | Model / effort | Outcome | Deviation from the plan |
|---|---|---|---|---|
| 0 Startup, preflight, plan | lead | opus max | all checks passed | — |
| 1 Quote, pull, seal, rolls | lead ran the frozen commands | — | $7.586199; 13 chunks sealed | a free quote pass added before the pull |
| 2 Build | lead ran the frozen command | — | step 4b failed, then passed after Task 3 | — |
| 3 Calendar sources | CalendarChecker-OpusXHigh | worker-xhigh / opus | CME primary sources for 9 dates | — |
| 3 Ruling, edit, re-freeze, commit | lead | opus max | 5 entries corrected; commit 14c1007 | — |
| 4 Steps 5–8 and the probe | lead ran the frozen command | — | S 2020-02-03; continuity 33/33; list; decisions, not void | four single-step calls instead of `--step all` |
| 5 Tabulation | ResultTabulator-SonnetMed | worker-medium / sonnet | reports/stage_d1f_run_tables.{md,json} | — |
| 5, 6 Reading, class statements | lead | opus max | this entry | — |
| 7 Independent verification | NumberVerifier-FableXHigh | worker-xhigh / fable | all VERIFIED, one row with notes, no discrepancy | brief also covered members near the power boundary |
| 8 Entry, STAGES.md, Session cost | lead | opus max | this entry | — |

At most two workers ran at once. Fable ran once, for Task 7, as the prompt specified, and was available when it started.

### Task 1 — purchase and seal (list steps 2 and 3)

- **Quote first.** A free `--d1f-quote-only` pass (16:37–16:41) priced the 71 chunks at **$7.586199** for 116,365,984 billable bytes, every chunk identical to the D.1e quote in price and bytes (ledger/databento_spend.jsonl lines 168–238, all `quote`, $0.00). The largest chunk was $0.116; no quote came near the $10.00 per-request cap.
- **Pull.** `data.pull_mes --d1f-pull`, 16:41–16:56, exit 0: 71 chunks bought oldest first. The ledger gained lines 239–451: 71 `quote`, 71 `commit` and 71 `settle` under session stage-D.1f-2026-09, no refusal. Committed $7.586198747; settled actual $7.586198747, because delivered record bytes equalled the quoted billable bytes for every chunk. The session total is **$7.586199**; the shared total moved from $84.006048 to $91.592247.
- **Seal.** Each of the 13 holdout-2 chunks (range=2024-03-01_2024-04-01 through range=2025-03-01_2025-04-01) was sealed by the same call that downloaded it, after the record-byte check and before the next request, in order. docs/HOLDOUT_UNLOCK_LOG.md gained 13 `SEALED holdout 2` records (plaintext and sealed sha256, the manifest sha256, the decrypt-back proof) and no UNLOCK record. docs/HOLDOUT2_MANIFEST.json holds bytes and sha256 only. After the pull, holdout-2 is sealed, 13 of 13 in order, all_ok, plaintext absent for all 13, 0 unlocks; the 58 confirmation chunks (31 MB) are the only new plaintext on disk.
- **Holdout-2 trade dates, from the calendar at sealing (build choice 2.1):** 258 = 261 weekdays 2024-04-01..2025-03-31 minus the listed full closures 2024-07-04, 2024-12-25 and 2025-01-01. Ten early halts count as trade dates. The embargo month (March 2024) holds 20. See the D.2 items below: the 2024-07-04 entry is very likely wrong in the same way as 2019-2023, which would make the count 259.
- **Vendor metadata.** The degraded-day warnings named exactly the eight declared dates. The roll fetch (`--d1f-rolls`, free) returned 19 quarterly MES rolls from 2019-06-17 to 2023-12-13; its one "cycle violation" is the known 'DNMH929 C35' label on instrument 7849 (list 1.1), and the build's raw-symbol drop count confirms it cost no bars.

### Task 2 — the build, and Task 3 — the step-4b calendar correction

**First build (16:57, exit 0).** 1,695,822 bars written read-only; trade dates 2019-05-06..2024-02-29; raw-symbol drops 0 in every month (so no stop); window drops only the 60 bars of trade date 2024-03-01; degraded list identical to the eight declared; validation 0 hard failures. **Step 4b failed with 12 discrepancies.** The build exits 0 on a step-4b failure and records it; the runner's preflight refuses on it. The failed summary is kept as reports/stage_d1f_confirmation_build_step4b_failed.json and its parquet was moved to data/processed/MES/superseded/.

**Diagnosis.** All 12 come from Independence Day 2019-2023. Each of 2019-07-04, 2020-07-03 (observed), 2021-07-05 (observed), 2022-07-04 and 2023-07-04 was listed as a full closure, and each shows the same bars: a session from 17:00 CT the prior evening to an 11:59 CT last bar, nothing from 12:00, the next bar at 17:00 CT (1,007 to 1,140 bars). That is a 12:00 CT halt, which is how the verified 2025 block already records 2025-07-04 ("research first read as a full closure"). The two "July 3, 12:15" discrepancies (2019, 2023) were a knock-on: with July 4 closed, the closed window ran from 12:15 on July 3 to 17:00 on July 4 and swallowed the July 4 session. The frozen calendar had also pushed each July 4 session into the next trade date, flagged as closure bars (5,536 of the 5,539 closure-flagged bars). Neither of the two causes the prompt expected (thin 2019 trading, the pre-2021-06-28 session) produced any discrepancy. A dry run of the frozen validator with only the five entries changed in memory passed with 0 discrepancies.

**Sources.** The old entries cited CME settlement-time PDFs: "CME Group will not derive or disseminate settlement prices". The file cites the same sentence as the status source for its early-halt holidays (Memorial Day 2019, for example); it says nothing about Globex hours. CalendarChecker-OpusXHigh found CME's own Globex holiday schedules for every date (reports/stage_d1f_calendar_check.md and .json; cmegroup.com refuses automated fetches, so each was read in full from a Wayback copy, and every quote was checked by script as a verbatim substring). For 2019, 2021 and 2022 the compact schedules read "Product|CLOSE|OPEN|HALT|OPEN" / "Equity |…|1200 CT / 1700 UTC|Regular @ 1700 CT / 2200 UTC" under the July 4 (or observed) date; the 2020 schedule gives Equity Products a 12:00 "Close" on Friday July 3 and a Sunday 17:00 open; the 2023 summary PDF gives EQUITIES "12:00 (PREOPEN) HALT" and "17:00 (OPEN)" on Tuesday 4 July. The July 3 12:15 CT closes in 2019 and 2023 are confirmed as listed. CME's clearing advisories add that the holiday's Globex trades carry the next trade date; the calendar keeps its existing convention for every holiday halt (the holiday as its own short trade date).

**Correction (lead ruling).** The five entries became early halts at 12:00 CT, graded cme / cme; each citation keeps its settlement status quote and adds the CME time quote, the archive URL and a note. The 2019-07-03 and 2023-07-03 entries are unchanged. 2024-07-04 was not changed: it is not a step-4b discrepancy, and holdout-2 has no bars to check it against (D.2 item below). The 2025-2026 block is byte-identical (block sha256 8752f837…9538). The edited file passed the frozen validator (0 discrepancies, 54 entries observed) and `ruff check`. `strategy.research._d1f_freeze` re-wrote the manifest at 17:21: 129 files, and only data/cme_calendar.py's hash changed. **Commit 14c1007** holds exactly data/cme_calendar.py and reports/stage_d1f_harness_freeze.json, with the old and new manifest sha256 and the five dates in its message. **Old manifest ba5b34d5239737cc493c360b38753573aa133963e73abf8639ba3532a4cf847a; new manifest d3bd21e50b14c014cf854c3a239fae6d204834e4d360c1cf2b20df7a18b7a3c2**, used for every later runner call.

Tests, not changed (they are outside the commit the prompt allows): tests/test_d1f_calendar_build.py::test_2019_2024_quotes_are_verbatim_from_the_extraction now fails, because it pins every citation to the build's extraction file and the five new time quotes come from the Task 3 check; test_confirmation_build_end_to_end fails in any run session, with the old calendar too, because it asserts that the real confirmation parquet does not exist. Both need a follow-up edit by the user.

**Rebuild (17:22, exit 0, 21 s).** The freeze check passed under d3bd21e5…; 1,695,822 bars; **step 4b passed** (1,259 weekdays, 54 entries, 0 discrepancies); raw-symbol drops 0; only 3 closure-flagged bars remain (single bars on 2020-03-30, 03-31 and 06-30); each July 4 session is now its own trade date with a 12:00 halt; 1,248 trade dates. The runner's full preflight then passed.

### Task 4 — the list run (steps 5 to 8, each run once)

The steps ran as four single-step calls, not `--step all` (same code; see open choices).

**Step 5, the start rule (17:23).** V_ref = 1,763.0 contracts per RTH minute, the median of the 14 monthly medians 2025-04..2026-05 (3204.5, 1890.5, 1382.5, 1248.0, 1363.5, 1373.5, 1817.0, 2659.0, 1439.0, 1702.0, 2152.0, 2653.0, 1820.0, 1709.0). Threshold 0.25 × V_ref = 440.75. Monthly medians of the extension: 2019-05 351, 06 309, 07 310, 08 611, 09 299, 10 361.5, 11 212, 12 201, 2020-01 383, 2020-02 569, and every month from 2020-02 through 2024-02 at 0.32 to 1.61 × V_ref. M* = 2020-02, **S = 2020-02-03**. Sensitivity, descriptive: 0.15 gives 2020-01-02, 0.40 gives 2020-03-02. Step 5 pinned the run inputs (parquet 82e256b4…, build summary b72e685f…, rolls, condition, symbology, HOLDOUT2_MANIFEST).

**Days against the D.1e power table's needs.** Trials see 1,055 window dates (2020-02-03..2024-02-29); statistics see 998 (57 excluded: 48 roll-blackout dates and 9 trade dates with vendor-degraded bars). Needs by class (chosen n_b): C1 149, C2 193, C3 566, C4 171, C5 16, C6 181, C7 114. Every class is covered; the tightest, C3, has 1.76 times its need. The achieved null power of each binding member: A-H4 rth leg 1.0000 (SE 4.12), G3.RTH.5 1.0000 (SE 4.29), F1_1_h1_RTH 0.9998 (SE 6.50), F2_4_15min_vol_tercile_top 1.0000 (SE 4.07), E-H1 1.0000 (SE 1.05), C-H4 1.0000 (SE 5.94), H6 1.0000 (SE 2.86).

**Step 6, continuity (17:23–17:25).** All 33 runs (the 31 trials, plus E-H1 and E-H2 under their confirmation factories) reproduce reports/stage_d1d_accounting.json on the 289-date train union: net P&L to the cent, trip counts exactly, daily Sharpe to 1e-6. 0 problems.

**Probe (17:25–17:27).** C-H1, the most active trial, through `screen_candidate` on the confirmation window; the report was discarded unread. 70.5 s, 1.76 GB peak. It set step 7 at 3 processes.

**Step 7, the list (17:27–17:46, 19 min).** 37 trials and 64 statistics on confirmation_2020-02-03_2024-02-29. Available memory never fell below 6.2 GB. The runner flagged, as designed (review F6), that the engine's ledger holds non-strategy fills the H modules' own records do not: H1 5, H2 2, H3 1, H4 2, H5 4, H6 11 (dates in reports/stage_d1f_run_STATE.md; several are the March 2020 and 2022-02-10 volatility days). P&L comes from the ledger either way; the count reported is the ledger's.

**Step 8, the decisions (17:47–17:49).** The hash re-check found nothing changed: **void = false**. Outputs: reports/stage_d1f_tier_a.json, _tier_b.json, _descriptive_facts.json and _decisions.json, each stamped with the manifest sha256.

### Task 5 — the result

**Tier A, all 58 members** (net ticks per micro per day; trials on 1,055 dates, statistics on 998; ε = 34; bootstrap as list 3.1):

| ID | Class | Kind | n (trips / events) | θ̂ (net ticks per micro per day) | UCB95 | SE_boot | Achieved null power | One-sided p | Holm (rank; reject) | Composite | Status, label |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | C1 | trial | 1,007 | -1.39 | 0.05 | 0.86 | 1.0000 | 0.951 | 28; no | fail | null |
| A-H2 rth close window (buy) | C1 | trial | 972 | -3.06 | -0.57 | 1.50 | 1.0000 | 0.981 | 36; no | fail | null |
| A-H2 rth close window (sell) | C1 | trial | 972 | -0.72 | 1.70 | 1.49 | 1.0000 | 0.680 | 12; no | fail | null |
| A-H3 weekend effect | C1 | trial | 388 | -2.52 | 1.79 | 2.63 | 1.0000 | 0.832 | 14; no | fail | null |
| A-H4 eth leg | C1 | trial | 1,007 | 1.08 | 6.05 | 3.04 | 1.0000 | 0.357 | 5; no | fail | null |
| A-H4 rth leg | C1 | trial | 1,005 | 2.77 | 9.58 | 4.12 | 1.0000 | 0.248 | 2; no | fail | null |
| B-H1 opening-range breakout (hold 5) | C2 | trial | 1,000 | -2.14 | -1.25 | 0.56 | 1.0000 | 1.000 | 43; no | fail | null |
| B-H1 opening-range breakout (hold 75) | C2 | trial | 1,000 | -2.33 | 1.12 | 2.15 | 1.0000 | 0.856 | 17; no | fail | null |
| B-H2 prior-day stop cascade | C2 | trial | 810 | -1.22 | 0.10 | 0.80 | 1.0000 | 0.936 | 23; no | fail | null |
| B-H3 breakout leg | C2 | trial | 991 | -2.41 | -0.34 | 1.27 | 1.0000 | 0.969 | 31; no | fail | null |
| B-H3 fade leg | C2 | trial | 991 | -1.41 | 0.71 | 1.28 | 1.0000 | 0.862 | 19; no | fail | null |
| B-H4 narrow-range breakout | C2 | trial | 441 | -0.85 | 0.28 | 0.69 | 1.0000 | 0.888 | 22; no | fail | null |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | C2 | trial | 984 | -2.47 | -1.58 | 0.55 | 1.0000 | 1.000 | 55; no | fail | null |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | C2 | trial | 984 | -1.94 | 1.02 | 1.82 | 1.0000 | 0.859 | 18; no | fail | null |
| RT3 B-H3 breakout leg 5-min bars | C2 | trial | 984 | -1.87 | 0.11 | 1.20 | 1.0000 | 0.939 | 24; no | fail | null |
| RT4 B-H3 fade leg 5-min bars | C2 | trial | 984 | -1.98 | 0.00 | 1.20 | 1.0000 | 0.950 | 27; no | fail | null |
| F6_1_overnight_range_position | C2 | statistic | 992 | 0.20 | 3.38 | 1.90 | 1.0000 | 0.461 | 7; no | fail | null |
| F4_4_round_number_multiples_of_100 | C2 | statistic | 3,091 | -14.94 | -8.30 | 4.46 | 1.0000 | 0.998 | 39; no | fail | null |
| F4_1_rth_open_crossing | C2 | statistic | 2,068 | -4.38 | -2.43 | 1.20 | 1.0000 | 1.000 | 51; no | fail | null |
| G2.RTH.30 | C2 | statistic | 2,501 | -3.52 | -0.72 | 1.75 | 1.0000 | 0.975 | 33; no | fail | null |
| G2.ETH.30 | C2 | statistic | 4,412 | -6.65 | -4.35 | 1.39 | 1.0000 | 1.000 | 53; no | fail | null |
| G2.ETH.5 | C2 | statistic | 9,584 | -17.84 | -16.15 | 1.05 | 1.0000 | 1.000 | 54; no | fail | null |
| G5.RTH.15 | C2 | statistic | 936 | -2.25 | -0.59 | 0.99 | 1.0000 | 0.990 | 37; no | fail | null |
| G5.RTH.30 | C2 | statistic | 882 | -1.69 | 0.79 | 1.52 | 1.0000 | 0.869 | 21; no | fail | null |
| G3.RTH.15 | C2 | statistic | 987 | -6.80 | -0.05 | 4.01 | 1.0000 | 0.960 | 30; no | fail | null |
| C-H1 magnitude-conditioned reversal | C3 | trial | 149,035 | -275.97 | -267.92 | 4.90 | 1.0000 | 1.000 | 44; no | fail | null |
| C-H2 post-spike exhaustion fade | C3 | trial | 33,126 | -64.74 | -61.37 | 2.04 | 1.0000 | 1.000 | 45; no | fail | null |
| C-H3 close-location-value reversal | C3 | trial | 47,582 | -89.32 | -85.11 | 2.54 | 1.0000 | 1.000 | 46; no | fail | null |
| RT5 C-H2 spike fade 5-min bars | C3 | trial | 10,614 | -21.22 | -18.82 | 1.45 | 1.0000 | 1.000 | 56; no | fail | null |
| F3_2_bucket07_bucket08 | C3 | statistic | 962 | -1.82 | -0.28 | 0.93 | 1.0000 | 0.975 | 34; no | fail | null |
| F3_3_opening_30min_to_close_momentum | C3 | statistic | 960 | -0.87 | 1.83 | 1.66 | 1.0000 | 0.693 | 13; no | fail | null |
| F3_2_bucket08_bucket09 | C3 | statistic | 962 | -3.59 | -2.00 | 0.99 | 1.0000 | 1.000 | 41; no | fail | null |
| F3_3_overnight_to_close_momentum | C3 | statistic | 963 | 1.01 | 3.70 | 1.67 | 1.0000 | 0.262 | 3; no | fail | null |
| F3_2_bucket01_bucket02 | C3 | statistic | 992 | -3.12 | -0.48 | 1.59 | 1.0000 | 0.976 | 35; no | fail | null |
| F3_2_bucket10_bucket11 | C3 | statistic | 963 | -1.87 | 0.03 | 1.19 | 1.0000 | 0.939 | 25; no | fail | null |
| F3_2_bucket02_bucket03 | C3 | statistic | 995 | -2.02 | 0.05 | 1.26 | 1.0000 | 0.949 | 26; no | fail | null |
| F3_2_bucket05_bucket06 | C3 | statistic | 993 | -1.90 | -0.23 | 1.00 | 1.0000 | 0.973 | 32; no | fail | null |
| F3_2_bucket04_bucket05 | C3 | statistic | 994 | -2.79 | -1.14 | 1.02 | 1.0000 | 0.996 | 38; no | fail | null |
| F3_2_bucket06_bucket07 | C3 | statistic | 992 | -1.57 | -0.09 | 0.91 | 1.0000 | 0.958 | 29; no | fail | null |
| F3_2_bucket12_bucket13 | C3 | statistic | 963 | -0.62 | 2.11 | 1.63 | 1.0000 | 0.651 | 10; no | fail | null |
| G1.RTH.5 | C3 | statistic | 14,779 | -35.25 | -30.51 | 2.89 | 1.0000 | 1.000 | 52; no | fail | null |
| D-H1 trailing-vol regime gate | C4 | trial | 397 | -0.92 | -0.54 | 0.24 | 1.0000 | 1.000 | 48; no | fail | null |
| D-H2 inverse-vol sizing | C4 | trial | 1,006 | -2.58 | -1.80 | 0.48 | 1.0000 | 1.000 | 49; no | fail | null |
| D-H3 range-compression gate | C4 | trial | 9,817 | -24.24 | -21.63 | 1.62 | 1.0000 | 1.000 | 50; no | fail | null |
| D-H4 overnight gap fade | C4 | trial | 568 | -1.21 | -0.58 | 0.40 | 1.0000 | 0.999 | 40; no | fail | null |
| RT6 D-H1 daily-vol regime gate | C4 | trial | 520 | -1.36 | -0.89 | 0.29 | 1.0000 | 1.000 | 57; no | fail | null |
| RT7 D-H2 daily-vol sizing | C4 | trial | 987 | -2.57 | -1.76 | 0.50 | 1.0000 | 1.000 | 58; no | fail | null |
| E-H1 scheduled macro drift | C5 | trial | 112 | 1.15 | 2.83 | 1.05 | 1.0000 | 0.137 | 1; no | fail | null |
| E-H2 post-release momentum | C5 | trial | 91 | -0.34 | 0.20 | 0.33 | 1.0000 | 0.853 | 16; no | fail | null |
| E-H3 quarterly witching short | C5 | trial | 16 | -0.06 | 0.03 | 0.06 | 1.0000 | 0.847 | 15; no | fail | null; null by inactivity |
| E-H4 turn-of-month long | C5 | trial | 196 | -0.61 | -0.38 | 0.15 | 1.0000 | 1.000 | 42; no | fail | null |
| C-H4 passive-fill reversal | C6 | trial | 90,418 | -186.63 | -177.18 | 5.94 | 1.0000 | 1.000 | 47; no | fail | null; null under the pessimistic fill model |
| H1 NR4 opening-range breakout | C7 | trial | 266 | 0.12 | 3.18 | 1.88 | 1.0000 | 0.479 | 8; no | fail | null |
| H2 NR7 opening-range breakout | C7 | trial | 155 | -0.36 | 2.10 | 1.50 | 1.0000 | 0.595 | 9; no | fail | null |
| H3 inside-day opening-range breakout | C7 | trial | 80 | 0.40 | 2.30 | 1.17 | 1.0000 | 0.357 | 6; no | fail | null |
| H4 bottom-tercile prior range, breakout | C7 | trial | 336 | 1.04 | 4.14 | 1.91 | 1.0000 | 0.292 | 4; no | fail | null |
| H5 top-tercile prior range, opening-range fade | C7 | trial | 287 | -0.94 | 2.80 | 2.24 | 1.0000 | 0.658 | 11; no | fail | null |
| H6 prior-close location follow-through | C7 | trial | 504 | -3.17 | 1.49 | 2.86 | 1.0000 | 0.864 | 20; no | fail | null |

**Holm.** m = 58, family-wise 5%: the first threshold is 0.05/58 = 0.00086 and the smallest p is 0.137 (E-H1), so Holm rejects nothing. Not one Tier A p-value is below 0.05 even before adjustment.

**Edge exists: no member.** Of the five conditions of list 3.2, no member meets Holm, the composite (0 of 58 pass) or t > 3.0 (largest 1.13, E-H1), and every DSR at N = 58 is 0.0. The family PBO at N = 58 is 0.443 (70 splits, 8 blocks of 131 days), below 0.5, which is the only condition any member meets. The DSR benchmark (the expected maximum daily Sharpe under the null) is 0.791, because the frozen rule takes the population variance of the 58 daily Sharpes (0.115), which the strongly negative high-frequency members widen (C-H1 −1.77, C-H4 −1.24); the best member's daily Sharpe is 0.035. Reported alongside, not criteria: at N = 101 the Sharpe variance is 2.64, the benchmark 4.12, every DSR 0.0 and PBO 0.60; at N = 186 the benchmark is 4.46 and every DSR 0.0. **There is no D.2 discussion item, so the period-appropriate cost re-check does not arise.**

**Tier B, 43 members.** All null: the largest UCB95 is 7.73 (G3.RTH.5) and the smallest achieved power 0.9977 (F4_4_round_number_multiples_of_50). **No anomaly** (BH at 10% within Tier B in direction s, with net edge ≥ 2.11 ticks per event): none is BH-significant. **One sign reversal:** F1_1_h30_ETH, whose gross move per event in the mined direction is −0.35 ticks (p = 0.0018, BH-significant at 10%); by list 2.2 it is reported as a reversal versus the mined window, not as an anomaly, and anything drawn from it needs new data and a new declaration.

**Per class** (runner verdicts, pending the check below): C1 null, C2 null, C3 null, C4 null, C5 null ("null by inactivity": E-H3 quarterly witching short, 16 trips), C6 inconclusive until Stage D.1g (C-H4 labelled "null under the pessimistic fill model"), C7 null. No class has an inconclusive or blocking member.

**Year slices (descriptive, list 3.6; no slice enters any verdict).** 505 member-years (2020–2024, the 2024 slice 43 days). One member-year has UCB95 ≥ 34: A-H4 rth leg in the 2024 stub (43 days, θ̂ 22.98, UCB95 38.87). The largest slice UCB95 per class: C1 38.87 (A-H4 rth leg, 2024), C2 27.87 (G3.RTH.5, 2024), C3 12.15 (F3_3_overnight_to_close_momentum, 2022), C4 16.04 (F5_1_relvol_tercile_top, 2024), C5 8.53 (E-H1, 2022), C7 22.53 (H6, 2024). Full table: reports/stage_d1f_run_tables.md, T5.

**Descriptive resolution** (the smallest per-trade edge this window could rule out at 80% null power, 2.4865 × SE_boot / trades or events per own date, net ticks per trade): C1 2.25 (A-H1) to 17.80 (A-H3); C2 0.27 (G2.ETH.5) to 10.69 (G3.RTH.5); C3 0.013 (F1_1_h1_ETH) to 4.30 (F3_3_overnight_to_close_momentum); C4 0.43 (D-H3) to 2.02 (F5_1_relvol_tercile_top); C5 1.98 (E-H4) to 24.67 (E-H1); C6 0.17 (C-H4); C7 14.90 (H6) to 38.42 (H3). **52 of the 100 members outside C6 cannot be resolved below the 2.11-tick market cost bar on this window** (all of C1 and C7, 19 of 31 in C2, 18 of 40 in C3, 3 of 4 in C5; all 13 in C4 can). D.1e projected 48 of 95 at a 2019-05 start.

Full tables (both tiers, classes, accounting, year slices, counts): reports/stage_d1f_run_tables.md and .json (ResultTabulator-SonnetMed; the lead checked the class block and several rows against the JSONs).

### Task 6 — class statements

**Status: independently verified.** NumberVerifier-FableXHigh (Fable 5.1, xhigh) re-computed every verdict-bearing number without importing the runner's decision or member modules: all VERIFIED, one row VERIFIED WITH NOTES (the DSR underflow), no DISCREPANCY (Task 7). The statements below therefore stand as the program's record.

**The aggregate statement (docs/NULL_CRITERIA.md section 7, W-1; every class C1 to C5 and C7 is null):**

> On trade dates 2020-02-03 to 2024-02-29, no member of any class the program tested on MES (market-order trials at their coded size, event statistics at the flat modelled round turn, Family H at 2 micros) showed a net edge of at least epsilon_day = 34 net ticks per micro per day, the smallest edge that funds the Topstep XFA funnel under the Stage B model of the 2026 rules and fee schedule at 2 micros; every member's one-sided 95% upper bound was below epsilon at >= 80% achieved null power; per class, the per-trade resolution was:

| Class | Epsilon per trade at the class's confirmation-window frequency (net ticks per micro per trade) | Class frequency (median trades per window day of the class's trial members) | Least active member (count) | Largest per-trade upper bound in the class (net ticks per micro per trade) | Label | Descriptive: smallest per-trade edge the window could rule out at 80% null power (net ticks per trade, min to max) |
|---|---|---|---|---|---|---|
| C1 session clock (6) | 36.29 | 0.937 | A-H3 weekend effect (388 round trips) | 10.06 (A-H4 rth leg) | — | 2.25 (A-H1 european-open overnight drift) to 17.80 (A-H3 weekend effect) |
| C2 reference levels and breakouts (31) | 36.45 | 0.933 | B-H4 narrow-range breakout (441 round trips) | 7.75 (G3.RTH.5) | — | 0.27 (G2.ETH.5) to 10.69 (G3.RTH.5) |
| C3 short-horizon reversal and momentum at market fills (40) | 0.89 | 38.25 | G4.RTH.60 (957 events) | 3.84 (F3_3_overnight_to_close_momentum) | — | 0.013 (F1_1_h1_ETH) to 4.30 (F3_3_overnight_to_close_momentum) |
| C4 volatility-state conditioning (13) | 46.14 | 0.737 | D-H1 trailing-vol regime gate (397 round trips) | −0.31 (F5_1_relvol_tercile_top) | — | 0.43 (D-H3 range-compression gate) to 2.02 (F5_1_relvol_tercile_top) |
| C5 calendar and scheduled events (4) | 353.40 | 0.096 | E-H3 quarterly witching short (16 round trips) | 26.68 (E-H1 scheduled macro drift) | null by inactivity (E-H3 quarterly witching short, 16 < 30) | 1.98 (E-H4 turn-of-month long) to 24.67 (E-H1 scheduled macro drift) |
| C7 daily-bar constructions (6) | 129.73 | 0.262 | H3 inside-day opening-range breakout (80 round trips) | 30.31 (H3 inside-day opening-range breakout) | — | 14.90 (H6 prior-close location follow-through) to 38.42 (H3 inside-day opening-range breakout) |

C6 awaits Stage D.1g: C-H4 under the trade-through fill model has UCB95 −177.18 net ticks per micro per day (90,418 trips) and carries the label "null under the pessimistic fill model", which is a lower bound and does not establish the C6 null (list 3.5). The structural question below epsilon remains open where the data cannot resolve it: on this window 52 of the 100 members outside C6 cannot be resolved below the 2.11-tick market cost bar (the last column), among them every member of C1 and C7, 19 of 31 in C2, 18 of 40 in C3 and 3 of 4 in C5. Criteria: docs/NULL_CRITERIA.md, sha256 6f69e318c96edf0a58956856c881ec3e1b8c68d89e1c836b3d54cfbf0e3497e2; members and their definitions: reports/stage_d1f_confirmation_list.md, sha256 c19cbac191c497a10b5cc756e96510999f13f27c4ac1aa72593aeabf1125147c.

**The per-class statements (docs/NULL_CRITERIA.md section 1, with the section 7 fields in the same sentence):**

The common text, identical for every class, is quoted from section 1 with S filled in; each class's own sentence follows it in full.

- **C1 (session clock: A-H1, A-H2 buy, A-H2 sell, A-H3, A-H4 eth, A-H4 rth).** For MES intraday strategies in class C1, tested on the pre-registered confirmation window (trade dates 2020-02-03 to 2024-02-29, S fixed by the start rule in docs/NULL_CRITERIA.md section 4): the trials executed through the engine with market orders at the modelled retail cost (the Stage A.1 cost model: $1.22 commission per round turn plus the time-of-day slippage table, about 2.11 ticks per round turn) at their coded contract size (1 micro for the 29 fixed-size trials, 1 to 5 by rule for D-H2 and RT7, 2 micros for Family H; C-H4, at 1 micro, is section 1.1's), the event statistics charged the flat modelled round turn of 2.11 ticks per event, all flat by the XFA cutoff: for every member of the class, a net edge of at least epsilon = 34 net ticks per micro per day ($85.00 per day at 2 micros, the smallest edge that funds the Topstep XFA funnel under the Stage B model of the 2026 rules and fee schedule at 2 micros) is rejected at one-sided 95% (the upper confidence bound on mean net daily P&L per micro is below epsilon), with achieved null power of at least 80%; per-trade resolution of the class on this window: epsilon per trade at the class's confirmation-window frequency 36.29 net ticks per micro per trade (0.937 trades per window day), least active member A-H3 weekend effect (388 closed round trips), largest per-trade upper bound in the class 10.06 net ticks per micro per trade (A-H4 rth leg). Descriptive, not a criterion: the smallest per-trade edge the window could rule out at 80% null power runs from 2.25 (A-H1) to 17.80 (A-H3) net ticks per trade.
- **C2 (reference levels and breakouts: B-H1 hold 5, B-H1 hold 75, B-H2, B-H3 breakout, B-H3 fade, B-H4, RT1 to RT4; Tier A statistics F6_1, F4_4 x100, F4_1, G2.RTH.30, G2.ETH.30, G2.ETH.5, G5.RTH.15, G5.RTH.30, G3.RTH.15; Tier B F4_2, F4_4 x50, G2.RTH.5, G3.RTH.5, G5.RTH.5, G2.ETH.15, G2.RTH.15, G3.RTH.30, G2.ETH.60, G2.RTH.60, G3.RTH.60, G5.RTH.60).** For MES intraday strategies in class C2, tested on the pre-registered confirmation window (trade dates 2020-02-03 to 2024-02-29, S fixed by the start rule in docs/NULL_CRITERIA.md section 4): the trials executed through the engine with market orders at the modelled retail cost (the Stage A.1 cost model: $1.22 commission per round turn plus the time-of-day slippage table, about 2.11 ticks per round turn) at their coded contract size (1 micro for the 29 fixed-size trials, 1 to 5 by rule for D-H2 and RT7, 2 micros for Family H; C-H4, at 1 micro, is section 1.1's), the event statistics charged the flat modelled round turn of 2.11 ticks per event, all flat by the XFA cutoff: for every member of the class, a net edge of at least epsilon = 34 net ticks per micro per day ($85.00 per day at 2 micros, the smallest edge that funds the Topstep XFA funnel under the Stage B model of the 2026 rules and fee schedule at 2 micros) is rejected at one-sided 95% (the upper confidence bound on mean net daily P&L per micro is below epsilon), with achieved null power of at least 80%; per-trade resolution of the class on this window: epsilon per trade at the class's confirmation-window frequency 36.45 net ticks per micro per trade (0.933 trades per window day), least active member B-H4 narrow-range breakout (441 closed round trips), largest per-trade upper bound in the class 7.75 net ticks per micro per trade (G3.RTH.5). Descriptive, not a criterion: the smallest per-trade edge the window could rule out at 80% null power runs from 0.27 (G2.ETH.5) to 10.69 (G3.RTH.5) net ticks per trade.
- **C3 (short-horizon reversal and momentum at market fills: C-H1, C-H2, C-H3, RT5; Tier A statistics F3_2 07-08, 08-09, 01-02, 10-11, 02-03, 05-06, 04-05, 06-07, 12-13, F3_3 (a) and (b), G1.RTH.5; Tier B F1_1 at five horizons for RTH and ETH, F3_2 03-04, 09-10, 11-12, G1.ETH.5, G4.RTH.5, G1.ETH.15, G1.RTH.15, G4.RTH.15, G1.ETH.30, G1.RTH.30, G4.RTH.30, G1.ETH.60, G1.RTH.60, G4.RTH.60).** For MES intraday strategies in class C3, tested on the pre-registered confirmation window (trade dates 2020-02-03 to 2024-02-29, S fixed by the start rule in docs/NULL_CRITERIA.md section 4): the trials executed through the engine with market orders at the modelled retail cost (the Stage A.1 cost model: $1.22 commission per round turn plus the time-of-day slippage table, about 2.11 ticks per round turn) at their coded contract size (1 micro for the 29 fixed-size trials, 1 to 5 by rule for D-H2 and RT7, 2 micros for Family H; C-H4, at 1 micro, is section 1.1's), the event statistics charged the flat modelled round turn of 2.11 ticks per event, all flat by the XFA cutoff: for every member of the class, a net edge of at least epsilon = 34 net ticks per micro per day ($85.00 per day at 2 micros, the smallest edge that funds the Topstep XFA funnel under the Stage B model of the 2026 rules and fee schedule at 2 micros) is rejected at one-sided 95% (the upper confidence bound on mean net daily P&L per micro is below epsilon), with achieved null power of at least 80%; per-trade resolution of the class on this window: epsilon per trade at the class's confirmation-window frequency 0.89 net ticks per micro per trade (38.25 trades per window day), least active member G4.RTH.60 (957 events), largest per-trade upper bound in the class 3.84 net ticks per micro per trade (F3_3_overnight_to_close_momentum). Descriptive, not a criterion: the smallest per-trade edge the window could rule out at 80% null power runs from 0.013 (F1_1_h1_ETH) to 4.30 (F3_3_overnight_to_close_momentum) net ticks per trade.
- **C4 (volatility-state conditioning: D-H1, D-H2, D-H3, D-H4, RT6, RT7; Tier B F2_4 bottom and top, F5_1 bottom and top, F5_2 bottom and top, F5_3).** For MES intraday strategies in class C4, tested on the pre-registered confirmation window (trade dates 2020-02-03 to 2024-02-29, S fixed by the start rule in docs/NULL_CRITERIA.md section 4): the trials executed through the engine with market orders at the modelled retail cost (the Stage A.1 cost model: $1.22 commission per round turn plus the time-of-day slippage table, about 2.11 ticks per round turn) at their coded contract size (1 micro for the 29 fixed-size trials, 1 to 5 by rule for D-H2 and RT7, 2 micros for Family H; C-H4, at 1 micro, is section 1.1's), the event statistics charged the flat modelled round turn of 2.11 ticks per event, all flat by the XFA cutoff: for every member of the class, a net edge of at least epsilon = 34 net ticks per micro per day ($85.00 per day at 2 micros, the smallest edge that funds the Topstep XFA funnel under the Stage B model of the 2026 rules and fee schedule at 2 micros) is rejected at one-sided 95% (the upper confidence bound on mean net daily P&L per micro is below epsilon), with achieved null power of at least 80%; per-trade resolution of the class on this window: epsilon per trade at the class's confirmation-window frequency 46.14 net ticks per micro per trade (0.737 trades per window day), least active member D-H1 trailing-vol regime gate (397 closed round trips), largest per-trade upper bound in the class −0.31 net ticks per micro per trade (F5_1_relvol_tercile_top). Descriptive, not a criterion: the smallest per-trade edge the window could rule out at 80% null power runs from 0.43 (D-H3) to 2.02 (F5_1_relvol_tercile_top) net ticks per trade.
- **C5 (calendar and scheduled events: E-H1, E-H2, E-H3, E-H4).** For MES intraday strategies in class C5, tested on the pre-registered confirmation window (trade dates 2020-02-03 to 2024-02-29, S fixed by the start rule in docs/NULL_CRITERIA.md section 4): the trials executed through the engine with market orders at the modelled retail cost (the Stage A.1 cost model: $1.22 commission per round turn plus the time-of-day slippage table, about 2.11 ticks per round turn) at their coded contract size (1 micro for the 29 fixed-size trials, 1 to 5 by rule for D-H2 and RT7, 2 micros for Family H; C-H4, at 1 micro, is section 1.1's), the event statistics charged the flat modelled round turn of 2.11 ticks per event, all flat by the XFA cutoff: for every member of the class, a net edge of at least epsilon = 34 net ticks per micro per day ($85.00 per day at 2 micros, the smallest edge that funds the Topstep XFA funnel under the Stage B model of the 2026 rules and fee schedule at 2 micros) is rejected at one-sided 95% (the upper confidence bound on mean net daily P&L per micro is below epsilon), with achieved null power of at least 80%; per-trade resolution of the class on this window: epsilon per trade at the class's confirmation-window frequency 353.40 net ticks per micro per trade (0.096 trades per window day), least active member E-H3 quarterly witching short (16 closed round trips), largest per-trade upper bound in the class 26.68 net ticks per micro per trade (E-H1 scheduled macro drift); null by inactivity (E-H3 quarterly witching short, 16 closed round trips, fewer than 30). Descriptive, not a criterion: the smallest per-trade edge the window could rule out at 80% null power runs from 1.98 (E-H4) to 24.67 (E-H1) net ticks per trade.
- **C7 (daily-bar constructions: H1 to H6).** For MES intraday strategies in class C7, tested on the pre-registered confirmation window (trade dates 2020-02-03 to 2024-02-29, S fixed by the start rule in docs/NULL_CRITERIA.md section 4): the trials executed through the engine with market orders at the modelled retail cost (the Stage A.1 cost model: $1.22 commission per round turn plus the time-of-day slippage table, about 2.11 ticks per round turn) at their coded contract size (1 micro for the 29 fixed-size trials, 1 to 5 by rule for D-H2 and RT7, 2 micros for Family H; C-H4, at 1 micro, is section 1.1's), the event statistics charged the flat modelled round turn of 2.11 ticks per event, all flat by the XFA cutoff: for every member of the class, a net edge of at least epsilon = 34 net ticks per micro per day ($85.00 per day at 2 micros, the smallest edge that funds the Topstep XFA funnel under the Stage B model of the 2026 rules and fee schedule at 2 micros) is rejected at one-sided 95% (the upper confidence bound on mean net daily P&L per micro is below epsilon), with achieved null power of at least 80%; per-trade resolution of the class on this window: epsilon per trade at the class's confirmation-window frequency 129.73 net ticks per micro per trade (0.262 trades per window day), least active member H3 inside-day opening-range breakout (80 closed round trips), largest per-trade upper bound in the class 30.31 net ticks per micro per trade (H3 inside-day opening-range breakout). Descriptive, not a criterion: the smallest per-trade edge the window could rule out at 80% null power runs from 14.90 (H6) to 38.42 (H3) net ticks per trade.
- **C6 (passive execution: C-H4): no statement.** Inconclusive by design until Stage D.1g (list 3.5). C-H4's trade-through result (θ̂ −186.63, UCB95 −177.18 net ticks per micro per day, 90,418 trips, label "null under the pessimistic fill model") is a lower bound and does not establish the C6 null.

Each statement speaks only for the listed members, at the stated sizes, cost model and fills, on the stated window. Section 7's list of claims the program may not make applies to it in full.

### Task 7 — independent verification (Fable xhigh)

NumberVerifier-FableXHigh (worker-xhigh on Fable 5.1, 17:49–18:04) re-computed the verdict-bearing numbers from the output JSONs and the per-member daily series, without importing any strategy.research._d1f_* module (reports/stage_d1f_run_verification.md; scratch script reports/_d1f_run_verify_scratch.py).

| Item | What was re-computed | Verdict |
|---|---|---|
| 1 Binding member of every class (C1 A-H4 rth leg, C2 G3.RTH.5, C3 F1_1_h1_RTH, C4 F2_4_15min_vol_tercile_top, C5 E-H1, C6 C-H4, C7 H6) | θ̂, UCB95, SE_boot, p and power by the list 3.1 method: bit-identical (max difference 0.0). An independent stationary bootstrap in the verifier's own code (seed 20260923) agrees within a 4-sd Monte Carlo tolerance (largest z 1.43). | VERIFIED |
| 1.8 Members within 10% of either boundary | None of the 101 (largest UCB95 9.58, largest SE_boot 7.58). | VERIFIED |
| 2 Holm | All 58 p-values, ranks and thresholds; smallest p 0.1372 against 0.05/58; rejected set empty. | VERIFIED |
| 3 Edge record | No member has status "edge". Every Tier A member fails Holm, the composite, DSR and t, and passes only PBO (0.4429); Sharpe variance, the DSR benchmark 0.7912 and the N = 101 figures match. | VERIFIED; the DSR row VERIFIED WITH NOTES: every DSR is Φ(z) with z ≤ −24.4, exactly 0.0 in double precision |
| 4 Start rule | V_ref 1,763, M* 2020-02, S 2020-02-03, sensitivities 2020-01-02 and 2020-03-02; all 14 reference and 58 extension monthly medians and first trade dates re-computed from the parquets, exactly; the 1,055-date window list identical. | VERIFIED |
| 5 Class labels | The null condition for all 101 members; C1–C5 and C7 null, C6 inconclusive by list 3.5; no blocking member; E-H3 the only "null by inactivity"; every statement field (class frequency, ε per trade, least active member, largest per-trade UCB95) identical. | VERIFIED |
| Extras | All 101 members bit-identical on every field; the 37 trial daily series rebuilt from the raw trips (max deviation 2.3e-13; sizes as list 3.1 states); Tier B anomaly BH identical. | VERIFIED |

**No DISCREPANCY.** What the verifier could not or did not re-derive (its notes N4 and N5): the 64 statistics' daily series, because step 7 stores per-date sums and counts but not per-event values (taken as given; the build session's tests reproduce every recorded EDA estimate and per-event value to 1e-9 through the same wrapper), the step-6 continuity check, the composition of the 57 excluded statistic dates, the year slices, the Tier B sign-reversal test and the composite verdicts themselves. None of these can turn a null into a non-null except the statistics' series; the composites and the sign reversal bear only on edge claims and anomalies, which no member reached.

### D.2 discussion items, and items carried forward

- **D.2 discussion items: none.** No member passed confirmation, so there is nothing to discuss for registration and REGISTRATION.md stays 0 bytes.
- **Holdout-2 calendar, before any D.2 read.** data/cme_calendar.py still lists 2024-07-04 as a full closure. CME's trading-hours service (ES, captured 2024-07-08, reports/stage_d1f_calendar_check.md) gives a 12:00 CT halt, the same pattern corrected here for 2019-2023. It was left alone because it is not a step-4b discrepancy and holdout-2 has no bars that may be read to check it. D.2 should correct it under its own declaration before reading holdout-2. With it corrected, holdout-2 has 259 calendar trade dates, not 258. No 2024 entry after 2024-02-29 has ever been checked against bars.
- **D.1g.** By list 3.5, the N_C6 = 181 dates are the last 181 confirmation-window dates that are neither roll-blackout nor vendor-degraded: 2023-06-07 to 2024-02-29, the last 181 entries of the step-7 statistic dates. D.1g buys and uses them under its own declaration.
- **Tests.** The two calendar-build tests named in Task 3 need a follow-up edit (point the verbatim test at both extraction files; skip the end-to-end guard when the real parquet exists).
- **Calendar grades.** CME schedules now confirm the 12:15 CT closes of 2019-07-03 and 2023-07-03, still graded "inferred"; a later calendar review can upgrade them (a test pins the grade).

### Open choices the lead made on its own

- **R.1 A free quote pass before the pull.** `--d1f-quote-only` ran first and was compared chunk by chunk with the D.1e quotes. Reason: CLAUDE.md requires a quote logged first, and the prompt's stop rule (a quote above $7.59, an unexpected billable size) needs the total before anything is bought; the pull itself gates only per chunk.
- **R.2 Steps 5 to 8 as four single-step calls.** This is the same code as `--step all`, which loops over the same four `run_step` calls with a fresh preflight each. Reason: each step's output is write-once, so a restarted `--step all` would refuse at step 5; single steps resume cleanly and give per-step times.
- **R.3 Process counts.** `--processes 6` for step 6 and 3 for step 7, against the runner's default of 12. CLAUDE.md caps jobs at 8 and at half the available memory; the probe (1.76 GB peak for the heaviest member) and step 6's measured ~0.35 GB per worker put 4 workers above half of the ~10 GB available and 3 below it.
- **R.4 The probe.** C-H1, which is not an H module (R-7), went through step 7's per-member path after step 6 had passed, and its report was discarded unread, so no confirmation figure was seen before continuity and no look was taken.
- **R.5 The scope of Task 3.** Five entries were changed, and only those. The July 3 entries stayed as they were (confirmed by CME). 2024-07-04 was left as a full closure: it is not a step-4b discrepancy and no bars may be read to check it, so it is carried to D.2. The citations keep the build's settlement status quote and add the CME time quote with the archive URL, graded cme / cme; "empirical" is not an allowed 2019-2024 grade.
- **R.6 The commit.** On main, exactly the two files, with this repository's attribution lines, and no push: the git anchor d384bfe and every stage commit are on main, and a branch would have left main's harness out of step with the manifest the run outputs record.
- **R.7 Failed-build artifacts kept.** The summary was copied to reports/stage_d1f_confirmation_build_step4b_failed.json and the parquet moved to data/processed/MES/superseded/; the build refuses to overwrite an existing output, and nothing was deleted.
- **R.8 Tests not edited.** The two failing calendar-build tests are reported, not fixed, because tests/ lies outside the commit the prompt allows.
- **R.9 The holdout-2 count** is recorded as 258 from the calendar as it stands (build choice 2.1), with the 2024-07-04 caveat.
- **R.10 Both statement forms.** The W-1 aggregate sentence, because all six classes are null, and each class's section-1 statement with the section-7 fields joined into the same sentence; both hashes are cited, and none of the phrasings section 7 forbids is used.
- **R.11 The verifier's brief** covered members near the power boundary (SE_boot within 10% of ε/2.4865) as well as UCB95 near ε, since either boundary decides a member's null.

### Artifacts

- **Purchase and seal:** ledger/databento_spend.jsonl (+284 lines: 71 quotes, then 71 quote, commit and settle triples); docs/HOLDOUT2_MANIFEST.json (new); docs/HOLDOUT_UNLOCK_LOG.md (+13 SEALED records); data/sealed/MES_holdout_v2/ (13 sealed chunks); data/vendor/databento/GLBX.MDP3/ohlcv-1m/MES_v_0/ (the 58 confirmation chunks); data/vendor/databento/rolls/MES_{v,c}_0_2019-04-01_2024-03-01.jsonl; the dataset-condition and symbology files, frozen at fetch.
- **Build:** data/processed/MES/ohlcv-1m_MES_v_0_2019-05-01_2024-02-29_confirmation.parquet (read-only); reports/stage_d1f_confirmation_build.json; reports/stage_d1f_confirmation_build_step4b_failed.json; data/processed/MES/superseded/ (the failed build's parquet).
- **Task 3:** data/cme_calendar.py and reports/stage_d1f_harness_freeze.json (commit 14c1007); reports/stage_d1f_calendar_check.{md,json}.
- **The run:** reports/stage_d1f_step5_start_rule.json, _step6_continuity.json, _step7_list_run.json, _tier_a.json, _tier_b.json, _descriptive_facts.json, _decisions.json.
- **Tables and verification:** reports/stage_d1f_run_tables.{md,json} with reports/_d1f_run_tables.py; reports/stage_d1f_run_verification.md with reports/_d1f_run_verify_scratch.py.
- **State:** reports/stage_d1f_run_STATE.md.
- **Docs:** docs/STAGES.md (one line); this entry.
- **Commits:** 14c1007 only. Everything else is uncommitted and waits for the user's review.

### Session cost

Computed at the end from this session's transcript (c39a9cf3-de81-44e4-96f7-c074621e99f7.jsonl) and its 3 worker files under c39a9cf3…/subagents/. For each assistant message id, the last streamed record is summed (input + output + cache read + cache creation) and grouped by model. These are raw token counts, not plan-credit percentages. The lead's figure is cut at 18:06 PDT; the entry-writing turns after that are not in it.

**Wall clock.** 16:34–18:07 PDT, with no pause or outage, so all of it is work. The initial estimate (printed at 16:40 PDT) put the end at 19:40 PDT after 3 h 06 min of work, or about an hour later if Task 3 was needed. Task 3 was needed, and the stage still finished well inside the estimate: the probe-sized run took 19 min against the 48 min guessed, and steps 5, 6 and 8 took minutes.

**Final table** (initial estimate at 16:40 PDT: end 19:40 PDT, 3 h 06 min of work; +1 h if Task 3 was needed)

| # | Task | Agent | Model | Effort | Start–end (PDT) | Time | Tokens total / output | Status, deviations |
|---|---|---|---|---|---|---|---|---|
| 0 | Startup, preflight, plan | lead | opus | max | 16:34–16:37 | 3 min | (lead row) | done |
| 1a | Free quote pass | lead (frozen command) | — | — | 16:37–16:41 | 4 min | — | done; added before the pull |
| 1b | Pull and seal | lead (frozen command) | — | — | 16:41–16:56 | 14.5 min | — | done; $7.586199; 13 chunks sealed |
| 1c | Rolls, holdout status | lead | — | — | 16:56–16:57 | 1 min | — | done |
| 2 | Build | lead (frozen command) | — | — | 16:57–16:57 | 0.5 min | — | step 4b failed (12 discrepancies) |
| 3 | Diagnosis, dry run, ruling, edit, re-freeze, commit | lead | opus | max | 16:58–17:22 | 24 min | (lead row) | done; commit 14c1007 |
| 3w | Calendar sources | CalendarChecker-OpusXHigh | opus | xhigh | 17:00–17:17 | 17 min | 12,289,326 / 61,450 | done; 9 dates CME-sourced |
| 2' | Rebuild, preflight | lead (frozen command) | — | — | 17:22–17:22 | 0.5 min | — | step 4b passed |
| 4a | Step 5, the start rule | lead | — | — | 17:23–17:23 | < 1 min | — | S = 2020-02-03 |
| 4b | Step 6, continuity | lead | — | — | 17:23–17:25 | 2 min | — | 33 of 33, 0 problems |
| 4c | Probe | lead | — | — | 17:25–17:27 | 1 min | — | 70.5 s, 1.76 GB; set 3 processes |
| 4d | Step 7, the list | lead (background) | — | — | 17:27–17:46 | 19 min | — | done; H forced-exit flags as designed |
| 4e | Step 8, the decisions | lead | — | — | 17:47–17:49 | 2 min | — | not void |
| 5w | Tabulation | ResultTabulator-SonnetMed | sonnet | medium | 17:49–17:51 | 2.3 min | 1,122,583 / 14,464 | done |
| 7 | Independent verification | NumberVerifier-FableXHigh | fable | xhigh | 17:49–18:04 | 14.4 min | 3,336,097 / 69,985 | all VERIFIED, one row with notes, no discrepancy |
| 5, 6 | Reading the result, class statements | lead | opus | max | 17:49–18:04 | 15 min | (lead row) | done |
| 8 | End guardrails, entry, STAGES.md, Session cost | lead | opus | max | 18:04–18:07 | — | (lead row) | done |
| L | Lead, whole session | lead | opus | max | 16:33–18:06+ | — | 57,875,683 / 256,838 | orchestration, commands, rulings, checks, writing |
| **Σ** | **Whole stage** | 3 worker spawns | | | 16:34–18:07 | **all work, no pause** (estimate 3 h 06 min, +1 h with Task 3) | **74,623,689 / 402,737** | lead 57.9M (77.6%), workers 16.7M (22.4%) |

**Tokens per model:**

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 (lead + CalendarChecker) | 462 | 318,288 | 68,971,990 | 874,269 | 70,165,009 |
| claude-fable-5-1 (NumberVerifier) | 866 | 69,985 | 3,037,043 | 228,203 | 3,336,097 |
| claude-sonnet-5 (ResultTabulator) | 26 | 14,464 | 1,004,794 | 103,299 | 1,122,583 |
| **All** | 1,354 | 402,737 | 73,013,827 | 1,205,771 | **74,623,689** |

**Per worker spawn:** CalendarChecker-OpusXHigh (worker-xhigh, opus, xhigh) 12,289,326; ResultTabulator-SonnetMed (worker-medium, sonnet, medium) 1,122,583; NumberVerifier-FableXHigh (worker-xhigh, fable, xhigh) 3,336,097.

**Delegation share:** lead 57.9M (77.6%), workers 16.7M (22.4%). By tier: opus 70.2M (94.0%: the lead 57.9M, CalendarChecker 12.3M), Fable 3.3M (4.5%), sonnet 1.1M (1.5%). Fable was used once, for the verification the prompt allowed: 3.3M tokens, about a third of the build session's 9.1M. The lead's share is far above the build session's 19.5%, because the work of this stage was running frozen commands and ruling on what they produced, which the prompt reserved for the lead; the lead wrote 256,838 output tokens.

## 2026-09-23/24 — Stage E.0: CME universe research, hypothesis catalog and program design (no purchase, no data, no freeze)

**The eight clusters of Topstep's CME universe were researched, a 61-member hypothesis catalog was written (170 confirmation trials, projected cumulative N = 228) and a draft Stage E design (D1 to D15) was proposed, all before any price data for a new product existed on this machine, for $0.00 (5,050 free quotes).** D1's liquidity floor was fixed before any census or quote output. It keeps 31 traded exposures and drops NKD, 6M and MET (MET by 0.003 of coverage). The design's staged purchase quotes at $275 to $300, against $28 of headroom under the shared cap, so the user must raise SHARED_ACCOUNT_CAP_USD and fund Databento before E.1. The independent Fable review found 0 blocking and 10 should-fix issues; all ten were fixed and one member was excluded. It re-read 46 logged passages (42 match, 0 misread, 4 unverifiable) and judged the work READY WITH FIXES. C6 is closed by the user's decision, and D.1g will not run. Three limits the plan did not foresee shaped the session:
- every sonnet-medium research reader failed verification, so research moved to opus;
- the session's 200 WebSearch calls ran out at about 21:05, so four clusters were researched without them;
- two usage-limit pauses stopped the session for 6 h 47 min.

Nothing is frozen, bought, registered or committed. The catalog and design are drafts for the user's review.

Lead: Opus 5.5 at max effort. Ultracode off. All times are Vancouver local (PDT). The session ran from 2026-09-23 20:02 (first tool call; the prompt arrived at 19:55) to 2026-09-24 06:25. Two pauses were caused by the usage limit ("You've hit your session limit"): 21:58 to 01:10 and 02:35 to 06:10. Neither counts as work.

### Guardrails

| Check | Start (20:02) | After pause 1 (01:11) | After pause 2 (06:11) | End (06:22) |
|---|---|---|---|---|
| holdout-1 (`uv run python -m data.holdout status`) | all_ok true, unlocks_logged 0, research_has_no_holdout_rows true | all_ok, 0 | all_ok, 0 | all_ok true, unlocks_logged 0, research_has_no_holdout_rows true |
| holdout-2 | sealed 13/13, all_ok true, unlocks_logged 0 | all_ok, 0 | all_ok, 0 | all_ok true, unlocks_logged 0, confirmation_has_no_holdout2_rows true |
| REGISTRATION.md | 0 bytes | — | — | 0 bytes |
| Databento ledger | 451 lines, shared $91.592247 | — | — | 5,501 lines. Lines 452-5,501 are 5,050 `quote` events under stage-E.0-2026-09-23, every `usd` 0.0, session committed $0.00, shared total unchanged at $91.592247 |
| E.0 caps (data/config.py, appended) | `STAGE_E0_SESSION_ID = "stage-E.0-2026-09-23"`, `E0_SESSION_CAP_USD = 0.00`, `E0_REQUEST_CAP_USD = 0.00`; `SHARED_ACCOUNT_CAP_USD` unchanged at 120.00 | — | — | unchanged |
| Data for new products | none | — | — | none: data/vendor/databento/GLBX.MDP3/ohlcv-1m/ holds only MES_v_0 |
| MES bars, rules/, live/, ops/, sim/, screening/, funnel/, strategy/, TopstepX | untouched | — | — | untouched (`git diff --stat` shows nothing there); no TopstepX call, no credential |
| docs/NULL_CRITERIA.md, reports/stage_d1f_confirmation_list.md | untouched | — | — | untouched |
| git | clean at 2124910 | — | — | no commit; changes listed under Artifacts |

The quote module cannot download. data/quote_universe.py installs raising guards on the client's `timeseries` and `batch` namespaces before any vendor call, and it calls only `SpendGate.quote`, never `authorize`, `commit` or `settle`. tests/test_quote_universe.py has 44 tests, all passing. They prove on a temporary ledger that the gate refuses a billable request under the $0.00 caps, and that the module source has no data call. The full suite after the change: 940 passed, 1 xfailed, and exactly the 2 known failures carried from D.1f. One side effect: data/config.py is inside the D.1f harness-freeze manifest, so `d1f_freeze_check()` now reports it as changed. D.1f is finished and D.1g will not run, so nothing depends on that manifest.

### Task 1 — Topstep facts and public liquidity

Topstep facts are in reports/stage_e0_topstep_facts.{md,json}: 15 pages first, then a curl-based follow-up for the star, verbatim payout and API text, holidays and lot counts. Against the constraints the stage prompt listed:
- **Confirmed verbatim:**
  - the 15:10 CT close and the 15:08 CT start of Risk Manager flattening;
  - the 50K limit of 5 minis or 50 micros, with XFA scaling starting at 2 lots;
  - limit orders fill only on trade-through: "the market has to trade through your price - not just touch it";
  - the prohibited SIM patterns, including "Making hundreds of rapid trades to take advantage of preferential queue position in SIM" and "hundreds or thousands of trades per day, with average durations measured in seconds, not minutes";
  - positions closed 15 minutes before any early close;
  - payout caps of $2,000 (standard) and $3,000 (consistency) at 50K, doubled by the Daily Loss Limit option ($1,000 at 50K);
  - a personal device only (no VPS, VPN or remote server), no sandbox, and the HFT prohibition.
- **Differs from the prompt: news.** There is no blackout window. "Topstep doesn't require you to flatten positions during economic releases - in SIM or Funded Accounts". What is prohibited is "Purposefully trading your full Maximum Position Size directly into a scheduled major news event". One rule covers the Combine and the XFA.
- **Differs: the stars.** MES, MNQ, M2K, MYM, M6E, M6A, 6M, MBT, MET, MCL, MGC and SIL are now starred, and MBT and MET are listed under equity futures. The star points to Topstep's "Risk Adjustments: High Risk/High Volatility" article, which sets two rules:
  - a CPI window: "No new opening transactions permitted during the 10-minute window surrounding the release" for NQ, RTY, YM, GC, SI, HG and PL, and micros limited to 3 contracts on the 50K;
  - discretionary volatility caps on the 50K: MCL and MGC 30; SIL and MHG 2; CL, QM, RB, HO and GC 3; SI, HG and PL 0.

  **M6E and M6A are starred but named on no page, so their restriction is unresolved.**
- **New and material:**
  - "Live funded accounts are not allowed to trade through the ProjectX API", so the bot can run on the Combine and the XFA only.
  - Grains trade 19:00-07:45 and 08:30-13:20 CT, with a 07:45-08:30 pause in which "No orders accepted". Livestock trade 08:30-13:05 CT.
  - Prohibited Conduct forbids "Holding a position within 2% of a product's price lock limit". Topstep's own article (fetched by the lead) defines it as "Stop trading when % Net Change approaches the limit minus 2%", with limits calculated from the prior settlement.
- **Not published:**
  - a per-product restriction list keyed to the star;
  - separate Combine and XFA news rules;
  - the XFA scaling tiers as text (they are an image);
  - how QM, QG and the E-micro FX contracts count against the lot limit.
- **Commissions:** Topstep's all-in round-turn figures per product, for example MNQ $1.22, MCL $1.52 ($1.72 from 2026-10-01), ZN $2.62, 6E $4.22, GC $4.32, MGC $1.92, ZC $5.28 and MBT $2.82.

The liquidity census is in reports/stage_e0_liquidity.{md,json}. The first census (sonnet) failed verification: cmegroup.com blocked this machine, and it got 9 of 50 ADV figures, all from search summaries. The opus rerun got:
- tick specifications for 50 of 50;
- open interest for 50 of 50, as of 22 September 2026;
- ADV for 50 of 50 from CME's own August 2026 monthly ADV report (2026 January-August year to date), plus a 2025 full-year figure for 11.

### Task 2 — free quotes (reports/stage_e0_quotes.{md,json}; data/quote_universe.py)

5,050 quotes, all at $0.00, in three sets:
- **Set A**, the history: ohlcv-1m monthly chunks from 2019-05-01 to an exclusive end of 2026-06-21, for 50 products, 4,295 quotes. The 158 failures are all months before a micro existed: MCL before 2021-06, MNG before 2023-10, MHG before 2022-04, MBT before 2021-04 and MET before 2021-11.
- **Set B**, the spread-calibration sample: mbp-1 and tbbo for five full trade dates, 500 quotes. The dates were fixed at 20:10 PDT, before any quote, as the five D.1e sampled for MES: 2025-05-14, 2025-08-13, 2025-11-12, 2026-02-11 and 2026-04-15. They lie inside the research window and clear of both holdouts and the embargo.
- **Set C**, the coverage proxy: ohlcv-1m over each product's declared day-session window on those dates, 250 quotes.

| Cluster | ohlcv-1m 2019-05..2026-06 | mbp-1 sample | tbbo sample |
|---|---|---|---|
| K1 equity index (8) | $69.13 | $32.19 | $19.46 |
| K2 rates (6) | $48.56 | $5.26 | $2.84 |
| K3 FX (12) | $90.41 | $4.38 | $1.74 |
| K4 energy (8) | $50.15 | $2.86 | $2.18 |
| K5 metals (7) | $53.71 | $5.49 | $4.62 |
| K6 ags and livestock (7) | $31.85 | $0.77 | $0.95 |
| K7 crypto (2) | $7.28 | $1.61 | $0.40 |
| **Universe (50)** | **$351.10** | **$52.56** | **$32.19** |

The staged purchase for the 31 exposures D1 keeps (MES bars, already owned, serve as the S&P leg):

| Step | Cost |
|---|---|
| Research window of every admissible contract | $58.42 |
| mbp-1 calibration sample | $46.35 |
| Confirmation plus holdout-2 history, one vehicle per exposure | $170.39 to $195.55 |
| **Total** | **$275.16 to $300.32** |

### Task 3 — research per cluster (reports/stage_e0_research_K1..K8.md; reports/stage_e0_partition.md; reports/stage_e0_source_registry.jsonl)

The partition was written before dispatch at 20:15. It sets product ownership, a region per cluster, a shared append-only source registry, rules for panel sources and announcements, and routes every cross-cluster item to K8. It is recorded as having worked with minor slips: the K6 reader read one K4-region item (K6-046, crude only), and two registry lines were edited in place (K3 run 1 and K7-026). Readers used the D.1 pre-filter and citation rules, plus a retrieval standard the lead tightened at 20:32: a search summary is never retrieved text, full text is required for every passed item, and there is no effort-based stopping.

| Cluster | Reader that produced the accepted log | Screened | Passed | Full text | Abstract only | Blocked / title only | [unverified] | K8 flags |
|---|---|---|---|---|---|---|---|---|
| K1 equity index | opus high, without WebSearch | 27 passed + 95 rejection rows | 27 | 15 | 12 | the same 12 blocked | 24 | 2 |
| K2 rates | sonnet medium, resumed once | 21 in depth | 19 unique (22 ids) | 15 | 6 | — | 13 | 1 |
| K3 FX | sonnet, then an opus continuation | about 90 | 45 ids | 24 | 15 | 6 title only | not counted | 4 |
| K4 energy | opus rerun (the sonnet log is kept as _sonnet_shallow) | about 305 | 43 | 22 | 18 | 3 | 49 | 13 |
| K5 metals | sonnet, then an opus continuation | about 200 | 31 unique | 17 | 8 | 6 | not counted | 7 |
| K6 ags and livestock | opus high, WebSearch gone from 21:05 | about 2,300 records | 49 | 34 | 14 | 1 | 23 | 9 |
| K7 crypto | opus high, without WebSearch | about 115 | 42 | 24 | 17 | 1 | 44 | 12 |
| K8 cross-cluster | opus high, without WebSearch | 47 routed flags + about 650 listing lines | 7 | 5 | 3 | — | 20 | all 47 routed flags dispositioned |

Every accepted log stopped on its container rule (at least 4 logged queries per container, with the last 2 empty); none reached the 60-read cap. The strongest mechanisms, in the lead's reading of the logs by evidence quality:
- **K2:** the Treasury auction cycle's intraday V-shaped pressure around the auction (NY Fed SR 1188, verified to the page); the FOMC post-announcement response; month-end index-extension flows.
- **K3:** the fix trades on CME futures. Krohn, Mueller and Whelan (JF 2024) find 6E around the ECB fix positive after the full spread, and 6B and 6J negative. There is also the Tokyo fix and gotobi-day evidence (Ito and Yamada). Against the London fix: the FCA's study finds the post-fix reversal gone after 2015.
- **K4:** EIA crude and natural-gas storage announcements (Halova, Kurov and Kucher; Prokopczuk and co-authors; Gu and Kurov), an API-to-EIA predictor, and pre-release natural-gas drift. For the drift, the authors' own post-2011 null is stated.
- **K5:** LBMA auction effects (Caminschi and Heaney, with Crain and co-authors on both sides after 2015), FOMC on gold, and hourly overreaction reversal.
- **K6:** USDA report timing. Volatility spikes 5 to 60 minutes after in-session releases, mostly with no systematic direction. Also the soybean crush opening reversal and limit-close continuation.
- **K7:** expiry-day settlement pressure (reversed after 2021 in a later study), 2-hour reversal and Monday trend. CME's 24/7 crypto trading since 2026-05-29 was verified from CME's own release.
- **K1:** little beyond the MES record: a VXN band fade (abstract only) and VWAP trend-following on the Nasdaq-100 (cost-fragile). The log also records the non-survivors: a VIX-futures lead, ICT's pattern and two MNQ ML studies, all null in their own sources.
- **K8:** thin. Flight to gold after equity crashes (abstract only) and crude to CAD, which its source calls weak evidence.

### Task 4 — the hypothesis catalog (reports/stage_e0_catalog.{md,json}; reports/stage_e0_catalog_K1..K8.md)

| Cluster | New | Core ports | ML | Active members | Confirmation trials | Excluded by the writer | Lead actions |
|---|---|---|---|---|---|---|---|
| K1 equity index | 2 | 3 | 1 | 6 | 12 | 21 | K1-predrift-01 excluded (MES's E family re-run on the Dow) |
| K2 rates | 5 | 3 | 1 | 9 | 45 | 9 | CP2 entry window amended |
| K3 FX | 6 | 3 | 1 | 10 | 32 | 16 | K3-ldnmom-01 narrowed from 6 exposures to EUR and JPY; K3-ldnrev-01 window fixed (review R-05) |
| K4 energy | 5 | 3 | 1 | 9 | 20 | 19 | K4-ngrev-01 excluded (review R-06); CP2 buffer fixed |
| K5 metals | 4 | 3 | 1 | 8 | 21 | 17 | K5-preauc-01 narrowed to gold and silver; ML fallback set |
| K6 ags and livestock | 4 | 3 | 1 | 8 | 28 | 18 | crushgap on ZS only; limitcont on HE and LE only; K6-ovr-01 excluded |
| K7 crypto | 3 | 3 | 1 | 7 | 7 | 18 | — |
| K8 cross-cluster | 3 | 0 | 1 | 4 | 5 | 14 | — |
| **Total** | **32** | **21** | **8** | **61** | **170** | **132** | 4 members excluded or removed by the lead |

The confirmation trials split into 96 port trials (3 per traded exposure), 66 new-member trials and 8 ML trials. **Projected cumulative N = 58 + 170 = 228.** The 384 ML grid configurations (48 per cluster) are reported beside the ML members and counted only in the research-window accounting (D15.8).

The writers' most common exclusion reasons were:
- proprietary consensus data (analyst surveys, the API bulletin);
- holding past 15:08 CT;
- the trade-rate floor (lead-lag that resolves in seconds);
- multi-leg spreads that break the 1-lot cap;
- dependence on CME's weekend closure, which ended 2026-05-29;
- no directional result in the evidence;
- insufficient evidence;
- sentiment, which is shelved.

Fifteen members carry the "source-overlap" label (review R-04). Members on starred products carry the star rules. Every lead change is a bracketed note in its entry, and the original text stays visible.

### Task 5 — the design draft (docs/STAGE_E_DESIGN.md and docs/NULL_CRITERIA_E.md, both DRAFT)

- **D1 universe:** the rule was fixed at 20:10, before any output. An exposure is IN if its most active contract has public ADV of at least 10,000 and day-session one-minute coverage of at least 0.95. Its input period was changed at 21:02, before any ADV value was read, to CME's 2026 January-August ADV for every product; the review judged the change legitimate and verdict-neutral. Result: 31 exposures in, and NKD, 6M and MET out. The S&P exposure is a leg only.
- **D2 vehicle and size:** risk-matched to MES at 2 micros ($360.68 of mean absolute day-session move), capped at 1 lot-equivalent under the news rule, with a risk ratio of at most 2.0. The vehicle is the candidate with the lowest cost per unit of risk, chosen in E.2 on research-window data.
- **D3 epsilon:** min(floor($85 / (q x tick value)), the product's own funnel-derived figure, computed in E.2). If no funnel cell passes, the translated figure is used and flagged.
- **D4 windows:** MES's calendar for every product (research 2025-04-01..2026-06-19, confirmation S..2024-02-29, embargo March 2024, holdout-2 sealed on arrival). Holdout-1 is not bought for new products. Per-product start rule; a power check, with an "inconclusive by design" label declared before the run; legs start at their own S; the union of the legs' roll blackouts is excluded.
- **D5 multiple testing:** Tier A is set by a research-window screen (mean > 0, t >= 1.0), and the ML member takes the same screen. Holm runs within each cluster at 0.05/K; the edge conditions are unchanged from D.1f.
- **D6 core port set:** CP1 intraday momentum (F3.3(a)), CP2 opening-range breakout (B-H1 hold 75, entries in [O+15, C), buffer of 4 ticks of the most active contract) and CP3 prior-close location (H6). The ports are literal, only the clock and the tick change, and the MES record is stated correctly in D6 (review R-02).
- **D7 criteria:** a per-cluster statement with a per-exposure resolution table, plus the "inconclusive by design" and "source-overlap" rules. The forbidden claims now cover every asset class and account.
- **D8 costs:** Topstep's round-turn commission plus a slippage table per 30-minute bucket from the mbp-1 sample, with a depth term. An event window, [release, release + 30 min), pays the product's largest bucket.
- **D9 Topstep constraints:**
  - flatten times per group (15:08; grains 13:18 and before the pause; livestock 13:03; early closes 15 minutes before);
  - trade-through for limit orders;
  - the floor: at most 20 entries a day, a 2-minute minimum hold, 10 minutes mean;
  - the 1-lot cap;
  - the event-minute fill guard;
  - the volatility caps and the CPI window;
  - the 2% price-limit rule, with Topstep's formula, precedence over the fill guard, and locked-market exits not filled until the market trades through (review R-08);
  - the deployment notes: personal device, no sandbox, no API on the LFA.
- **D10 calendars:** one per product group, with CME citations, plus the 2024-07-04 fix and the crypto regime split at 2026-05-29.
- **D11:** the E.2 build list.
- **D12 sessions:** E.1 (3-4 h), E.2a and E.2b (8-12 h each), then a screening and a confirmation session per cluster, in the order K4, K5, K2, K3, K6, K7, K1, K8. K1 and K7 are optional.
- **D13 spend:** as quoted in Task 2. Proposed caps: each session's quote plus 10%, and $3.00 per request.
- **D14 carried items:** the two failing calendar-build tests and the 2024-07-04 entry, both to be fixed in E.2.
- **D15 ML protocol:** LightGBM regression; one vehicle with declared fallbacks; up to 12 features (5 common, 7 per cluster), each traced to a logged mechanism with its availability time; horizon from {15, 30, 60, 120}; a nested walk-forward in the research window only, over a 48-configuration grid listed in full, with purge and embargo; one refit, then frozen; trade when |y_hat| >= m x cost; one trial at confirmation.

### Task 7 — C6 closed, D.1g not run (docs/DECISIONS.md, docs/STAGES.md)

This is recorded as the user's decision of 2026-09-23: C6, passive execution, is closed as non-deployable on the XFA, and Stage D.1g will not run. Each reason carries its Topstep source verbatim:
- limit orders fill only on trade-through, the model D.1f already applied to C-H4 (UCB95 −177.18 net ticks per micro per day over 90,418 trips);
- the prohibition on exploiting queue position in SIM.

The entry says plainly that this is a scope decision, not a null. docs/STAGES.md marks D.1g NOT RUN with a pointer to the decision, and adds the Stage E outline (E.0; E.1 freeze and purchase; E.2 build; then the cluster sessions, all planned). The old "Stage E — Practice-account forward test" is renumbered Stage F.

### Task 6 — independent review, and Task 8 — rulings (reports/stage_e0_review.md, reports/stage_e0_review_rulings.md)

CatalogAuditor-FableXHigh (Fable 5.1, xhigh; 02:27 to 06:19, with the pause excluded) returned 0 BLOCKING, 10 SHOULD FIX and 18 NOTE, verdict READY WITH FIXES. It re-read 46 passages, re-fetching 15 sources itself: 42 match, 0 misread, 4 unverifiable. It found no look-ahead, no Topstep conflict, nothing that needed price data, and no result-driven narrowing. All ten SHOULD FIX findings were ruled on:
- R-01: the ML member's Tier A membership now has one definition.
- R-02: the CP1 wording on MES is corrected (MES confirmed the reversal-signed F3.3 as null; the ported momentum form is untested on MES's confirmation).
- R-03: CP1 on livestock is the first-30-minute form by the same rule text.
- R-04: the source-overlap label is applied to 15 members, and unrecorded windows count as overlap.
- R-05: K3-ldnrev-01 now uses the source's 10-minute pre-fix window.
- R-06: K4-ngrev-01 is excluded; its own source contradicts its central step.
- R-07: the K4-cp2-01 buffer is fixed.
- R-08: locked-market exits are no longer simulated as fills.
- R-09: every ML member declares its fallback vehicles now.
- R-10: the stale K6 text is marked superseded.

One NOTE was also acted on: D3 now has a rule for when no funnel cell passes. The review was not re-run.

### Decisions the user must make before Stage E.1

1. Raise SHARED_ACCOUNT_CAP_USD (to about $400 for the whole plan), fund Databento (about $33 of credit left against $275 to $300), and approve per-session caps.
2. D1: the thresholds, and whether to re-admit MET (coverage 0.947) or NKD (whose most active hours are Tokyo's).
3. D2: the risk target and band, the 1-lot cap, and the long bonds (ZB, UB) if they exceed the band.
4. D3: min(translated, funnel-derived) versus the funnel figure alone.
5. D4: leave holdout-1 unbought for new products; allow full-size bars (BTC for MBT) as a price path only if a power check fails.
6. D5: the alpha split across clusters and the t >= 1.0 screen.
7. D6: the three ports.
8. D7: the "inconclusive by design" exception and the "source-overlap" rule.
9. D8: mbp-1 only, and five dates.
10. D9: clear or reject the unresolved star on M6E and M6A (until then they are not D2 candidates); the platinum suspension risk; whether Topstep's "Unfair technology - using software, AI ..." clause could be read against a frozen ML model.
11. D12: whether K1 and K7 get sessions.
12. D15: the model type, the grid, and counting each ML member as one trial.
13. Every member's judgment parameters (thresholds, windows, holds), and the NOTEs carried to E.1 (R-15, R-24, R-28).
14. The commit of this session's files (the planning chat commits after the review).

### Delegation record

| Task | Agent | Model / effort | Outcome | Deviation |
|---|---|---|---|---|
| 0, 3p, 5, 7, 8, entry | lead | opus max | done | — |
| 1 | TopstepFacts-SonnetMed (+ follow-up, resumed) | sonnet medium | done; F12 follow-up found the star's referent | follow-up added |
| 1b | LiquidityCensus-SonnetMed | sonnet medium | failed verification | promoted |
| 1b | LiquidityCensus2-OpusHigh | opus high | accepted | promotion |
| 2 | QuoteCoder-OpusHigh | opus high | 44 tests pass; no vendor call | — |
| 2 run | lead (background) | — | 5,050 quotes, $0.00 | — |
| 3 K4 | ClusterReader-K4-SonnetMed | sonnet medium | failed (shallow, search summaries) | promoted |
| 3 K4 | ClusterReader-K4b-OpusHigh | opus high | accepted | promotion |
| 3 K5 | ClusterReader-K5-SonnetMed | sonnet medium | partial (stopped on a cost notice) | continued on opus |
| 3 K5 | ClusterReader-K5b-OpusHigh | opus high | accepted | promotion |
| 3 K2 | ClusterReader-K2-SonnetMed (resumed once) | sonnet medium | accepted after resume | resumed |
| 3 K3 | ClusterReader-K3-SonnetMed | sonnet medium | failed (under-queried) | continued on opus |
| 3 K3 | ClusterReader-K3b-OpusHigh | opus high | accepted | promotion |
| 3 K6, K1, K7, K8 | ClusterReader-K#-OpusHigh | opus high | all accepted; K6, K1, K7 resumed after pause 1 | routed to opus (was sonnet medium in the plan) |
| 4 x8 | CatalogWriter-K#-OpusXHigh | opus xhigh | 8 catalogs | — |
| 4 | CatalogAssembler-SonnetMed | sonnet medium | assembled, counts checked by script | — |
| 6 | CatalogAuditor-FableXHigh (resumed after pause 2) | fable xhigh | READY WITH FIXES | — |

At most four workers ran at once. Fable was used once, for Task 6.

### Deviations from the plan, with reasons

1. **Research moved from sonnet medium to opus high.** All four sonnet readers failed verification on the first pass. K4 logged search summaries as retrieved text and stopped after 12 minutes "for the time allotted at this worker's effort level". K5 and K2 stopped on the harness's informational cost notices. K3 misstated its stopping rule. Per CLAUDE.md, a sonnet worker failing "more than occasionally on a class of task" moves that class to opus. The routing table's "complex extraction: sonnet medium" line does not hold for literature research with retrieval, and CLAUDE.md should be updated for research readers (user's call).
2. **The liquidity census was promoted to opus** after its sonnet run failed.
3. **Tool budgets ran out.** Firecrawl credits ran out at 20:52. The session's 200 WebSearch calls ran out at about 21:05; raising it needs `CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, which was not done because the run was unattended. OpenAlex and Crossref limits were hit at about 21:17. K6, K7, K1 and K8 were researched with free scholarly APIs and curl only, so their coverage is thinner and more items are abstract-only behind SSRN and publisher blocks. **Recommendation: raise the WebSearch cap for research-heavy stages.**
4. **Two usage-limit pauses.** Three readers and the auditor were resumed from their transcripts, and no finished work was lost.
5. **ETA.** The estimate table was printed before the first spawn, with the research rows marked as guesses. The planned probe (K4's first container) was invalidated by the shallow run, and the research rows were re-sized from the opus reruns.
6. **The lead fetched Topstep's 2% article itself** (one curl call) to answer a catalog question the facts file did not cover.
7. **The lead edited catalog entries** to apply its rulings, as bracketed notes in the cluster files and in the assembled copy.
8. **Hygiene.** Two registry lines were edited in place, against the append-only rule. Several registry DOIs and author names are wrong, with corrections in the logs. The K7 reader saved an arXiv response (ax4.xml) in the repository root; the lead moved it to the scratchpad. The lead first wrote ruling times of 06:40 to 06:50 into the notes from memory instead of the clock; they were corrected to 06:20.

### Open choices the lead made on its own

- O-1: the old "Stage E" forward test was renumbered Stage F.
- O-2: the D1 thresholds, the declared day-session windows and the calibration dates (the D.1e MES dates), all fixed before any output.
- O-3: D1's input period (2026 January-August ADV for all products).
- O-4: the S&P exposure is closed and appears only as a leg; owned MES bars serve as that leg.
- O-5: the core port set and its forms, and CP2's entry window and buffer.
- O-6: the 1-lot cap drawn from the news rule, with D2 amended for it.
- O-7: the event-minute fill guard and the event-window cost.
- O-8: the 2% price-limit rule as Topstep defines it, its precedence over the fill guard, and locked-market exits.
- O-9: member narrowings and exclusions on the writers' questions (K3-ldnmom-01, K5-preauc-01, three in K6, K1-predrift-01), which the review judged not result-driven.
- O-10: a staged purchase, with holdout-1 not bought for new products.
- O-11: D5's tiers, screen and alpha split.
- O-12: the "source-overlap" and "inconclusive by design" rules.
- O-13: ownership rulings (K3-001 stays in K3; K6-032 stays in K6).
- O-14: the routing change to opus for research.
- O-15: quote sets B and C in their stated form (both mbp-1 and tbbo; day-session windows).

### Artifacts

- **Design:** docs/STAGE_E_DESIGN.md and docs/NULL_CRITERIA_E.md (both new, DRAFT). docs/DECISIONS.md and docs/STAGES.md are edited (C6, Stage E outline, this session's line).
- **Code:** data/quote_universe.py and tests/test_quote_universe.py (new); data/config.py (E.0 block appended).
- **Ledger:** ledger/databento_spend.jsonl (+5,050 `quote` lines, $0.00).
- **Reports:**
  - reports/stage_e0_STATE.md
  - reports/stage_e0_partition.md
  - reports/stage_e0_source_registry.jsonl
  - reports/stage_e0_topstep_facts.{md,json}
  - reports/stage_e0_liquidity.{md,json}, and _liquidity_sonnet_failed.{md,json}
  - reports/stage_e0_quotes.{md,json}, reports/stage_e0_quote_run.log, reports/stage_e0_symbology.json
  - reports/stage_e0_research_K1..K8.md, and the superseded _K3_sonnet_partial, _K4_sonnet_shallow and _K5_sonnet_partial
  - reports/stage_e0_catalog_K1..K8.md, reports/stage_e0_catalog.{md,json}
  - reports/stage_e0_review.md, reports/stage_e0_review_rulings.md
- **No commit.**

### Session cost

These figures were computed from this session's transcript (ddaec527-9d48-4509-b368-c2e3eb443675.jsonl) and its 25 worker transcripts under ddaec527…/subagents/. For each assistant message id, the last streamed record is summed (input, output, cache read and cache creation) and grouped by model. They are token counts, not plan-credit percentages, and they are cut at 06:22 PDT, so the entry-writing turns after that are not included. For comparison only, the harness's own dollar notice at 06:22 read "session total ~$511.12".

**Wall clock.** The session ran 20:02 to 06:25 (10 h 23 min). The two usage-limit pauses (21:58-01:10 and 02:35-06:10, 6 h 47 min) are not work, which leaves **about 3 h 36 min of work**. The initial estimate, printed before the first spawn, was about 12 h of work ending at 08:05. Research went faster than guessed once it was on opus, and catalogs took about 20 minutes each.

**Tokens per model:**

| Model | Input | Output | Cache read | Cache creation | Total |
|---|---|---|---|---|---|
| claude-opus-5-5 (lead and opus workers) | 4,182 | 2,833,481 | 613,045,141 | 10,741,708 | 626,624,512 |
| claude-sonnet-5 | 716 | 358,648 | 63,418,527 | 1,788,382 | 65,566,273 |
| claude-fable-5-1 (auditor) | 740 | 116,141 | 9,088,467 | 1,925,724 | 11,131,072 |
| **All** | 5,638 | 3,308,270 | 685,552,135 | 14,455,814 | **703,321,857** |

**Delegation share:** lead 89.0M (12.7%), workers 614.3M (87.3%). By tier: opus 626.6M (89.1%), sonnet 65.6M (9.3%), Fable 11.1M (1.6%). The opus research readers alone used 458.7M (65% of the session): K4b 95.0M, K6 81.2M, K3b 58.1M, K7 57.7M, K5b 57.4M, K8 41.1M, K1 37.6M and Census2 30.5M. This is roughly nine times D.1f's whole session (74.6M), and its main cost is the research-on-opus routing plus heavy tool use (every fetch re-reads a growing context). Fable was used once, 11.1M.

**Final table.** Worker times are the first and last records of each transcript; resumed agents show their working spans.

| # | Task | Agent | Model | Effort | Start–end (PDT) | Time | Tokens total / output | Status |
|---|---|---|---|---|---|---|---|---|
| 0 | Startup, context, partition, D1 rule, STATE, ETA | lead | opus | max | 20:02–20:16 | 14 min | (lead row) | done |
| 1 | Topstep facts (+ follow-up 21:52–21:56) | TopstepFacts-SonnetMed | sonnet | medium | 20:14–20:23 | 9 + 4 min | 7,110,441 / 68,628 | done |
| 1b | Liquidity census | LiquidityCensus-SonnetMed | sonnet | medium | 20:14–20:24 | 10 min | 1,392,080 / 40,487 | failed verification |
| 1b' | Liquidity census rerun | LiquidityCensus2-OpusHigh | opus | high | 20:31–21:00 | 29 min | 30,511,112 / 92,205 | accepted |
| 2 | Quote module and tests | QuoteCoder-OpusHigh | opus | high | 20:15–20:27 | 12 min | 2,472,142 / 52,262 | done |
| 2r | Probe, quote run, report | lead (background) | — | — | 20:30–21:24 | 54 min | — | done, $0.00 |
| 3 | K4 research | ClusterReader-K4-SonnetMed | sonnet | medium | 20:15–20:28 | 13 min | 7,939,760 / 46,137 | failed |
| 3 | K4 rerun | ClusterReader-K4b-OpusHigh | opus | high | 20:31–21:24 | 53 min | 95,021,821 / 193,252 | accepted |
| 3 | K5 research | ClusterReader-K5-SonnetMed | sonnet | medium | 20:25–20:38 | 13 min | 10,060,924 / 37,609 | partial |
| 3 | K5 continuation | ClusterReader-K5b-OpusHigh | opus | high | 20:50–21:27 | 37 min | 57,436,023 / 155,657 | accepted |
| 3 | K2 research (resumed once) | ClusterReader-K2-SonnetMed | sonnet | medium | 20:25–20:50 | 25 min | 25,415,725 / 86,167 | accepted |
| 3 | K3 research | ClusterReader-K3-SonnetMed | sonnet | medium | 20:39–20:49 | 10 min | 8,645,300 / 41,621 | failed |
| 3 | K3 continuation | ClusterReader-K3b-OpusHigh | opus | high | 20:51–21:24 | 33 min | 58,122,615 / 150,720 | accepted |
| 3 | K6 research | ClusterReader-K6-OpusHigh | opus | high | 21:20–21:58, 01:10–01:22 | 50 min | 81,193,424 / 176,199 | accepted |
| 3 | K1 research | ClusterReader-K1-OpusHigh | opus | high | 21:25–21:58, 01:10–01:22 | 45 min | 37,609,843 / 126,600 | accepted |
| 3 | K7 research | ClusterReader-K7-OpusHigh | opus | high | 21:26–21:58, 01:10–01:20 | 42 min | 57,690,230 / 163,423 | accepted |
| 3 | K8 research | ClusterReader-K8-OpusHigh | opus | high | 01:23–01:56 | 33 min | 41,125,560 / 122,413 | accepted |
| 4 | Catalog K2 | CatalogWriter-K2-OpusXHigh | opus | xhigh | 21:01–21:18 | 17 min | 8,270,313 / 110,178 | done |
| 4 | Catalog K4 | CatalogWriter-K4-OpusXHigh | opus | xhigh | 21:27–21:51 | 24 min | 10,169,257 / 151,493 | done |
| 4 | Catalog K3 | CatalogWriter-K3-OpusXHigh | opus | xhigh | 01:12–01:35 | 23 min | 8,939,246 / 141,415 | done |
| 4 | Catalog K5 | CatalogWriter-K5-OpusXHigh | opus | xhigh | 01:20–01:42 | 22 min | 9,973,379 / 149,698 | done |
| 4 | Catalog K6 | CatalogWriter-K6-OpusXHigh | opus | xhigh | 01:24–01:46 | 22 min | 6,098,391 / 148,021 | done |
| 4 | Catalog K7 | CatalogWriter-K7-OpusXHigh | opus | xhigh | 01:36–01:58 | 22 min | 12,138,242 / 145,789 | done |
| 4 | Catalog K1 | CatalogWriter-K1-OpusXHigh | opus | xhigh | 01:43–02:04 | 21 min | 12,442,425 / 131,780 | done |
| 4 | Catalog K8 | CatalogWriter-K8-OpusXHigh | opus | xhigh | 01:57–02:20 | 23 min | 8,426,909 / 158,604 | done |
| 4a | Assembly | CatalogAssembler-SonnetMed | sonnet | medium | 02:21–02:27 | 6 min | 5,002,043 / 37,999 | done |
| 6 | Independent review | CatalogAuditor-FableXHigh | fable | xhigh | 02:27–02:35, 06:10–06:19 | 17 min | 11,131,072 / 116,141 | READY WITH FIXES |
| 5, 7, 8 | Design, C6, rulings, entry | lead | opus | max | throughout; rulings 06:19–06:22; entry 06:22–06:25 | — | (lead row) | done |
| P1 | Pause (usage limit) | — | — | — | 21:58–01:10 | 3 h 12 min | — | not work |
| P2 | Pause (usage limit) | — | — | — | 02:35–06:10 | 3 h 35 min | — | not work |
| L | Lead, whole session | lead | opus | max | 20:02–06:25 | — | 88,983,580 / 463,772 (to 06:22) | orchestration, design, rulings, entry |
| **Σ** | **Whole stage** | 25 worker transcripts | | | 20:02–06:25 | **about 3 h 36 min of work** (estimate: 12 h) | **703,321,857 / 3,308,270** | lead 12.7%, workers 87.3% |
