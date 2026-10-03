# V23Coder-OpusXHigh report (Stage E.12 Task 1, code)

Worker: V23Coder-OpusXHigh (worker-xhigh, opus). Brief: reports/stage_e12_briefs/brief_v23coder.md.
No market data read, no key, no network, no commits. Compute: nice 10, at most 6 BLAS/OMP threads.
Times are America/Vancouver (PDT).

## Test runs

| Run | Command | Summary line |
|---|---|---|
| Baseline, 08:07:54-08:12:08 | `PYTHONPYCACHEPREFIX=<scratch>/pyc_base nice -n 10 uv run pytest -q -p no:cacheprovider tests/test_ml_v2_*.py` | `704 passed, 1 xfailed in 252.91s (0:04:12)` |
| Final, 08:38:43-08:43:15 | same, fresh `<scratch>/pyc_final`, plus `-rxXs` | `791 passed, 2 xfailed in 270.62s (0:04:30)` |

The final run includes Phase1Coder's tests (test_ml_v2_phase1_freeze / _gate0 / _world: 38 tests
at the final run) and the lead's ACCOUNT_150K change in ml_route_v2/account.py. Both xfails are
strict (listed below). `<scratch>` = /tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/8200a1ff-b6ff-45e5-adaa-37850b4a7889/scratchpad.
ruff passes on every file I touched.

## Changes by brief item

### 1. constants.py
- 1-6: module docstring no longer "DRAFT": "frozen by the Stage E.12 freeze manifest
  (reports/stage_e12_ml_v2_freeze.json)", V23 applied.
- 60-62: `C_SIGMA_TAU = 0.167` (V23 item 1: 1.5 c = 0.25 sigma gives 1/6).
- 70-77: Gate 0 constants unchanged in value; each comment cites V23 item 1.
- 91-96: `COST_GATE_KS` comment states the gross hurdles; `COST_GATE_READING = "gross"`; "net"
  stays selectable through the constant.
- 120-125: `RELEASE_WINDOW_BEFORE_MIN = 5`, `RELEASE_WINDOW_AFTER_MIN = 30`,
  `RELEASE_WINDOW_TIER_FRACTION = 0.5` (V23 item 11, P-5).
- 132-138: `N_PROGRAM_AT_FREEZE = 198` (STAGES.md line 114, E.9_RETURN.md line 21, V21, C-08).
  `N_PROGRAM_AT_DRAFT = N_PROGRAM_AT_FREEZE` is kept as a transitional alias, because
  pipeline.py (Phase1Coder's file) still imports it (see Open items).
- I did not touch the 150K figures, PAYOUT_RESET_DELAY_DATES or anything else Topstep-related.
- configs.py:42, 201-203: `ConfigLedger.n_total` now defaults to `N_PROGRAM_AT_FREEZE`.

### 2. decide.py, cost_filter.py
- decide.py:1-23: the docstring now says gross is the default (V23 item 1) and net is selectable.
  The reading is still looked up at call time (`gate_reading`).
- cost_filter.py:8-9, 27, 43, 58: tau is now read at call time as `v2c.C_SIGMA_TAU` instead of a
  name imported at module load. The docstring cites V23 item 1.
- Grep result: the package has no literal 0.10 used as tau and no literal "net" used as a
  default. The remaining "net" strings are the option names (decide.py:34, 76). The remaining
  0.10 values are DAILY_SIGMA_FRACTION, VERDICT_RUIN_MAX and docstrings of the D-03 budget.
  Stale comments say "tau 0.10" at ml_route_v2/synthetic.py:15 and :69. I did not edit them
  because the file is not mine (see Open items).

### 3. Release-window rule (V23 item 11, P-5)
How the flag is computed:
- targets.py:23-31, 48, 196-198, 229-231, 256: new column `release_window`. It is True iff the
  entry fill (`entry_ts_ns`, after the D9.5a deferral) lies in [r - 5 min, r + 30 min) of a
  release r in the vehicle's own `release_times` list. That is the same list used for the
  deferral and the event-window cost. The column is False where there is no entry, and it is not
  a model feature.
- portfolio.py:91-113: `release_window_mask` (half-open interval, per vehicle list) and
  `release_window_binds` (open tenths including the entry > 0.5 x tier tenths). Both accept
  scalars or arrays.

How the flag reaches each path:
- decide.py:36-38, 115-120, 137: `CANDIDATE_COLUMNS` gains `release_window`. `candidates`
  requires a bool column in the rows and carries each row's own flag through.
- portfolio.py:77-79: `CANDIDATE_COLUMNS` gains `release_window`, so `join_risk` requires it.
  portfolio.py:236-238 refuses a non-bool flag.
- pipeline._nested_schedule builds its empty schedule from `decide.CANDIDATE_COLUMNS`, so it
  picks up the column without any edit to pipeline.py.

Where the rule is applied:
- `admit` (portfolio.py:162-196) takes a new required keyword `release_window`. After sizing, a
  flagged entry is refused with reason "release_window" if
  book tenths + n x lot tenths > 0.5 x `tier_tenths`. The entry is refused, not re-sized.
- The fixed-D selection path uses `admission_record` (portfolio.py:264-301): every ranked
  candidate with its contracts and reason, at the base tier. `refusal_counts` is at :304 and
  `accept_trades` (:310) is now a filter of the record. selection_metric.py:7-10 has only a
  docstring change.
- Engine-run portfolio, simulate.py: 63-70 (docstring) and `_Plan.release_window` (210, 241).
  `admit(..., release_window=...)` (366) uses the tier at the prior close, and refusals land in
  `PortfolioRun.decisions` with reason "release_window". `TradeRecord(release_window=...)` is
  set at 599.
- payout_sim.py: `TradeRecord.release_window` (130-132). `run_path` refuses a flagged trade
  above half the path's own tier (361-364). The vectorized `simulate_paths` does the same
  (430, 455, 624-627). The counts are `PathResult.n_release_window_refusals` (191) and
  `PathArrays.n_release_window_refusals` (505).

### 4. K9-anncday-01 (V23 item 8)
The signal module, ml_route_v2/signals/k9.py (new):
- One spec, `k9_anncday`: kind "flag", normalize False, family K9-anncday-01, cluster "K9",
  roots_read (). It is 1.0 iff the trade date is in the EC-K9 set.
- It applies on MNQ, M2K and MYM rows whose date is covered. It does not apply on other
  vehicles, on dates outside both windows (the embargo and holdout-2 dates), or inside uncovered
  spans.
- avail is 17:59 CT on the calendar day before d, so `assert_causal` holds.
- The research-window set is the union of the five lists in the catalog's members[0], which is
  60 dates. The vehicles are checked against the catalog.
- The training-window set comes from reports/stage_e12_ec_k9_2019_2024.json. The loader checks
  schema "ec_k9/1", the exact window, that date_set is sorted and unique and equals the union of
  the five lists, that every date lies in the window, and the span shapes. Any failure raises
  `K9CalendarError`.
- Path constants are read at call time. The loader is cached by (path, mtime, size).

Registration, signals/__init__.py:
- 34 and 44: the spec is imported into REGISTRY.
- 62-63: K9-anncday-01 is removed from EXCLUDED.
- 74: `FAMILY_SIGNALS` adds K9 by name. This is the K9 special case: only "member" specs are
  collected automatically, and the brief asked for kind "flag".
- The identifier one-hots come from the rows and constants.CLUSTERS, so a spec cluster "K9"
  does not affect them. synthetic.py's root selection is member-only and K9 reads no bars, so the
  spec cluster changes nothing there either.

The real training file now exists (written 08:28). It has 240 dates and no uncovered spans, and
it passes every check.

### 5. Gate 0 canaries under the new defaults
| Canary | Result |
|---|---|
| Pure noise fails (gate0 and leakage (a)) | pass |
| Planted gross edge passes (gate0; leakage (b), which also checks the k = 1.5 gate trades it) | pass |
| Edge between 1.0 c and 1.5 c fails Gate 0; bar 1 binds (`test_edge_above_cost_but_below_one_and_a_half_costs_fails`) | pass |
| NEW: edge in [1.5 c, 2.5 c) passes Gate 0 (`test_edge_between_one_and_a_half_and_two_and_a_half_costs_passes`, cost 4.6 ticks, ratios 1.73..2.21; leakage (c) `..._between_bars_passes_gate0`) | pass |
| (c) under net, by monkeypatch: the [1.5 c, 2.5 c) edge is rejected at every k (the old semantics) | pass |
| (c) NEW, gross default: the same edge is NOT rejected by k = 1.5. Each k trades exactly the rows with predicted gross > k c, which is more than 95% of rows at k = 1.5 | pass |
| (c) ridge predictions rejected at every k under net (pinned) | strict xfail, the E.11 C-1 finding, unchanged |
| (d) sub-cost 0.5 c edge: Gate 0 fails and the true mean is rejected at every k (gross) | pass |
| (d) ridge predictions under net (pinned) | pass |
| (d) ridge predictions under gross | strict xfail, NEW finding: 4 of 2,538 rows pass k = 1.5 (see Open items) |

### 6. Tests changed, and why
Reading and tau:
- test_ml_v2_decide.py: the three hand-computed gate tests encoded the net arithmetic. They now
  pin `reading="net"`, and gross counterparts were added. "the default is net" became "the
  default is gross (V23 item 1)". The one-line flip test now flips gross to net.
- test_ml_v2_state_fingerprint.py: `_flip` now asserts the default is "gross" and flips to
  "net". Five test names were renamed to match.

The release-window column:
- test_ml_v2_decide.py and test_ml_v2_portfolio.py: the `_rows`, `cand`, `score_rows` and
  `stub_candidates` fixtures carry the column. The admit kwargs pass `release_window=False`.
- test_ml_v2_simulate.py: `row()` carries the column.
- test_ml_v2_cpcv.py `make_panel`: the fake panel carries `release_window` False, mirroring the
  targets layout. This is why the C-02 test failed in my first full run.
- test_ml_v2_targets.py: the pinned layout gains the column.

Program N:
- test_ml_v2_gate0.py, test_ml_v2_configs.py and test_ml_v2_e2e.py now use
  N_PROGRAM_AT_FREEZE.

K9:
- test_ml_v2_signals.py: the EXCLUDED set, and the non-member family set (G1..G17 plus
  K9-anncday-01, with the spec fields pinned).

Lead's 150K change (no test was weakened):
- test_ml_v2_portfolio.py: the assertion "150K tiers == 50K tiers" is replaced by
  `test_150k_tiers_are_topsteps_published_schedule`. It pins the 9 balances the lead listed:
  0 -> 30, 1499.99 -> 30, 1500 -> 40, 2000 -> 40, 2000.01 -> 50, 3000 -> 50, 3000.01 -> 100,
  4500 -> 100, 4500.01 -> 150.
- test_ml_v2_payout.py:75: `scaling_tiers == 50K and base_lots == 2.0` is now pinned to
  base 3.0 and the published tuple.
- No other test pinned 150K tiers. test_ml_v2_payout.py:477 asserts only `ruin_prob == 0`
  (it still passes), and the simulate 150K test checks the refusal message only.

New tests:
- tests/test_ml_v2_k9.py (15 tests). The real-file test runs now that the file exists.
- Release-window tests in portfolio (mask boundaries, binds at 2/3/5 tiers, admit
  above/at/below half, the accept_trades scenario, exactly half, a bad flag, score_split),
  targets (r - 5 min binds; r + 30 min does not; r + 29 min does; a deferred fill; another
  vehicle's release never binds), simulate (member refusal recorded; exactly half trades, and
  its record carries the flag), and payout (a hand case plus run_path/vectorized parity with
  flags; the count is checked to be greater than 0).

## Open items (lead ruling or routing needed)
1. **Edited files outside my list.** To cover every path, as item 3 requires, I edited three
   files that are not on my list:
   - ml_route_v2/targets.py (the flag);
   - ml_route_v2/simulate.py (the engine-run member and its trade records);
   - tests/test_ml_v2_cpcv.py (its fake panel).

   Neither coder owns these. pipeline.py needed no edit for the rule.
2. **pipeline.py:105, 539 still import `N_PROGRAM_AT_DRAFT`.** I kept the alias at
   constants.py:138 (the same object as N_PROGRAM_AT_FREEZE, 198) so pipeline.py still imports.
   Phase1Coder or the lead should switch those two lines to N_PROGRAM_AT_FREEZE and then delete
   the alias before the freeze hash.
3. **New canary-(d) finding under the gross reading.** Ridge's linear extrapolation of a bounded
   0.5 c edge passes the 1.5 c hurdle on 4 of 2,538 rows. This is C-1 again: under net those
   predictions stayed below 2.5 c. Gate 0 still fails that edge, and the true conditional mean
   is rejected. I recorded it as a strict xfail and did not change any rule.
4. **Two readings for your check:**
   - (a) P-5 implemented as "refused, not re-sized". The brief says "refused".
   - (b) The research-window K9 set is the plain union of the five lists (60 dates), as the
     brief says. The catalog also lists skipped_by_weekly_cap, excluded_R12 (58 dates after
     R-12) and R-07 flagged dates. All of these are inside the union and are not removed.
5. **K9 file absent.** While reports/stage_e12_ec_k9_2019_2024.json is absent, K9 is not
   applicable on the training window and a `K9CalendarMissing` warning is issued; it does not
   raise. The file exists now. The freeze manifest should hash it, and the phase-1 run could
   assert `k9.training_calendar_present()`.
6. **Interfaces contract.** `release_window` is a new column of the interfaces contract
   (targets section 4, candidates section 6). reports/stage_e11_interfaces.md was not updated
   (not my file).
7. **Stale comments in synthetic.py.** ml_route_v2/synthetic.py:15 and :69 still say "tau 0.10"
   (comments only; c/sigma 0.05 is still under 0.167).
8. **Refusal counts in the selection metric.** These are available through `admission_record` /
   `refusal_counts`, but they are not added to SplitScore or the CPCV unit records. That would
   need configs.py and cpcv.py edits.
