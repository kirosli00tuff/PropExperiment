# Stage D.1e Task 3 (power and sample size): handoff, paused on lead request

Paused before the full run. No compute is running. Nothing was deleted.

## Files on disk

- `strategy/research/_d1e_power.py` — complete, `ruff check` clean, imports and runs.
- `tests/test_d1e_power.py` — complete, `ruff check` clean, 10 tests, **8 pass, 2 fail**
  (both failures are expectation questions for the lead, not code faults; see below).
- `reports/stage_d1e_power.json` / `.md` — **NOT WRITTEN**. The full run never started.

## Done

- Inputs parsed and cross-checked: `parse_class_map` reads the class of all 95 measured
  members verbatim from coverage.md sections 2/3/4 and the module raises if that set does not
  equal the union of the trials and events JSON keys (it does equal it). 101 members total
  (31 trials + 21 Tier A + 43 Tier B + 6 projected Family H).
- Series construction, VIF_boot (Politis-Romano, p = 1/5, K = 20, 0.2·gamma_0 floor),
  analytic n_a/n_b, vectorised bootstrap simulation, log-linear threshold interpolation,
  percentile-bootstrap spot check, CME calendar / supplied-days estimator, Family H
  projection, class roll-up, JSON schema and markdown renderer — all implemented to the brief.
- Probe results (cheap, already measured):
  - No member hits the VIF floor (0 of 101).
  - Largest analytic sizes at eps_day = 34: n_a 1,447 and n_b 566, both `F1_1_h1_RTH`.
    Every n is well under the grid top, so **no grid truncation is needed** and the
    runtime escape hatch in the brief is not required.
  - Timing: 6.1 s per member for the full length grid at 2,000 replications
    (~580 s serial, ~80 s at `--jobs 8`); percentile spot check 26 s at n = 200,
    roughly linear in n, so ~6 class spot checks ≈ 3-4 min. Full run well under 20 min.
  - The 8 vendor-degraded dates parse correctly out of `stage_d1e_quotes.md`.

## Not done

1. The full run (`reports/stage_d1e_power.json` and `.md`).
2. Resolution of the two failing tests (both need a lead ruling).

## Tests run and results

`uv run pytest tests/test_d1e_power.py -q` → **8 passed, 2 failed, 0.81 s**.

Passing: tests 2, 4, 5, 6 (with the correction below), 7, plus the AR(1) VIF assertions
inside test 3, the holiday-observance guard, the VIF-floor guard and the z-constant guard.

### Failure A — test 1, the iid VIF band (seed luck, not a code fault)

`variance_inflation` on 5,000 iid N(0,10) draws with seed 20260922 gives **0.9289**; the
brief asks for 1.0 +/- 0.05. Measured over 20 seeds: mean **0.9957**, sd **0.0467**. The
estimator is unbiased, but 1 sampling sd is 0.047, so the +/-0.05 band is about 1.07 sd wide
and a large share of seeds miss it. Options for the lead: (a) keep 5,000 days and pick a seed
inside the band (offsets +5, +12, +19 give 1.006, 0.999, 0.994), (b) widen the band to
+/-0.10 (about 2 sd), or (c) raise the series to ~50,000 days, which shrinks the sd to ~0.015.
I did not choose; the test is currently written to the brief's number and fails.

### Failure B — test 3, AR(1) simulated power_b (a real property of the specified estimator)

Measured **power_b = 0.848** at the analytic n_b; the brief asks for 0.80 +/- 0.04. This is
not an implementation error. Diagnostic on the AR(1) series (phi = 0.3, 20,000 days):

| quantity | value |
|---|---|
| VIF_boot of the source series | 1.587 |
| actual var(mean of a draw) x n / gamma_0(source) | 1.584 |
| E[V_B(x)] / gamma_0(source), x = the draw's own series | 1.380 |
| mean SE_hat | 0.745 |
| actual sd of the draw mean | 0.803 |

The draw's variance is right (1.584 vs the 1.587 the analytic n assumes), but `SE_hat`,
computed from the DRAW's own autocovariances as the design specifies, is diluted a SECOND
time by the (1-p)^k weighting: a block-resampled series' lag-k autocorrelation is itself
about (1-p)^k times the source's, so E[V_B(x)] carries ((1-p)phi)^k twice over. SE_hat runs
about 7% small, the UCB is correspondingly tight, and power_b lands above 0.80. The effect
is zero for iid members and grows with persistence, so it touches only the few members with
material lag-1 autocorrelation. Lead ruling needed: accept and document (and widen the test
band, e.g. 0.80-0.90, recording why), or change the SE definition. **I changed nothing.**

## Two further deviations already made, both flagged for the lead

1. **scipy is unavailable.** It is not a project dependency (`pyproject.toml`, and
   `strategy/research/f_data_native/_stylized_facts.py:154` says so explicitly). The module
   uses `statistics.NormalDist().inv_cdf` instead of `scipy.stats.norm.ppf`; the values agree
   to ~1e-15 (z_b 0.8416212335729144, z_95 1.6448536269514715, z_a 3.1340460549238425).
   Adding scipy would have been outside my write boundary.
2. **Test 6's arithmetic.** The brief says January 2023 has "21 weekdays minus 2 closures
   = 19". It has **22** weekdays (1 Jan 2023 was a Sunday), so the estimator returns **20**
   after removing Mon 2 Jan (New Year observed) and Mon 16 Jan (MLK) — exactly the two
   closures the brief names. The closure rule is right; only the brief's weekday count is
   off by one. The test asserts 20 and carries the discrepancy in its docstring.
3. **Censored simulated thresholds (an edge case the design does not cover).** For members
   whose analytic n is tiny, the shortest simulated length already exceeds 80% power, so the
   crossing is never bracketed and the interpolated figure is an upper bound, not a
   measurement. Adopting it would claim fewer days than any measured crossing supports, so
   `_chosen` reports it with flag `sim_censored_below_grid_{a,b}` and keeps the analytic
   size. Both figures are always reported, as the brief requires. The lead may prefer the
   literal rule (simulated figure wins whenever |diff| > 15%); one edit to `_chosen` reverts it.

## Exact commands that remain

```bash
cd /home/kiros-li/Documents/GitHub/PropExperiment

# 1. after the lead rules on failures A and B, re-run the tests
uv run pytest tests/test_d1e_power.py -q

# 2. the full run (writes reports/stage_d1e_power.json and .md); ~5-10 min at --jobs 8
uv run python -m strategy.research._d1e_power --eps-day 34 --jobs 8

# lint gate used throughout (ruff format is NOT enforced in this repo)
uv run ruff check strategy/research/_d1e_power.py tests/test_d1e_power.py
```

Serial fallback if the box must stay quiet: add `--jobs 1` (about 10 min single-core).
`--replications` exists for timing probes only; the reported run must keep the default 2,000.

## Invariants

Holdout untouched (no `data.holdout` call, no holdout date read), REGISTRATION.md untouched,
no TopstepX call, no Databento request of any kind, no commit, no existing file modified.
`uv run python -m data.holdout status` was NOT run by this worker — it is the lead's
session-level check.

---

## Resumed (lead rulings A-F applied, full run completed)

Everything below was done by the resuming worker. Nothing outside the brief's write
list was touched; the four `M` entries in `git status` (CLAUDE.md, ledger/,
screening/runner.py, tests/test_screening_runner.py) predate this worker.

### What changed

- **A. Test 1 iid band.** `IID_DAYS` 5,000 -> **50,000**, same seed scheme, band kept at
  +/-0.05. Measured VIF on the 50,000-day series is inside the band; the constant carries a
  comment giving the sampling-sd reason.
- **B. Simulation standard error (the substantive change).** `simulate_powers` now uses

      SE_hat = sqrt( gamma_0_hat(x) * VIF_boot(source) / n )

  with `gamma_0_hat(x)` the replicate's own sample variance (`ddof=1`) and `VIF_boot(source)`
  computed once per call from the source series. The per-replicate `V_B` is gone, which
  removes the double attenuation diagnosed above. Documented in the module docstring, in
  `simulate_powers`' docstring, in `meta.notes`, and in a paragraph at the head of the
  markdown. Test 3 keeps its 0.80 +/- 0.04 band and its AR(1) VIF assertions and now passes;
  its docstring records the 0.848 figure as the regression this pins.
  Side effect: `row["sim_floor_hits"]` (a per-replicate count that no longer exists) is
  replaced by `row["sim_source_vif_floored"]` (bool). Removing the per-draw autocovariance
  work also cut the runtime roughly fourfold.
- **B (spot check).** The percentile spot check is kept and now carries
  `spot_check.interpretation` verbatim: "a check of the closed form against the percentile
  construction inside the bootstrap world, biased upward for autocorrelated members by the
  double attenuation; not a check of the absolute level". The same caveat is in markdown
  section 4, in `percentile_ucb_success`' docstring and in `meta.notes`.
- **C. scipy.** Unchanged: `statistics.NormalDist`. `test_normal_quantiles_...` now also
  compares the module constants against quantiles recomputed in the test from `NormalDist`.
- **D. Test 6.** Kept as written, expectation 20.
- **E. Censored thresholds.** `_chosen` unchanged: analytic kept,
  `sim_censored_below_grid_{a,b}` flagged, both figures reported.
- **F. File split (mechanical, no behaviour change).** `_d1e_power.py` 1,015 -> **796** lines.
  - `strategy/research/_d1e_calendar.py` (117 lines): the supply-window constants and the
    CME calendar / supplied-days estimator, moved verbatim.
  - `strategy/research/_d1e_power_report.py` (210 lines): `render_markdown` and `_fmt`.
    It imports nothing from `_d1e_power` (no import cycle): the four labels it used to read
    as module constants now travel in `payload["meta"]` as `descriptive_note`,
    `eps_ref_per_trade`, `eps_sensitivity`, `cost_bar_market_ticks`, `cost_bar_passive_ticks`.
  - The calendar tests import `strategy.research._d1e_calendar as cal`.

### Commands run and results

```
uv run ruff check strategy/research/_d1e_power.py strategy/research/_d1e_calendar.py \
    strategy/research/_d1e_power_report.py tests/test_d1e_power.py   -> All checks passed
uv run pytest tests/test_d1e_power.py -q                             -> 10 passed in 1.88 s
uv run python -m strategy.research._d1e_power --eps-day 34 --jobs 8  -> 146.1 s (2m27 wall)
```

`--eps-day` is the only argument that differs from the defaults in that run
(`--replications` 2000, `--jobs` 8, `--max-grid-n` 3000 are the defaults), and
`meta.eps_day`, `meta.replications`, `meta.n_grid` and `meta.seed_base` record them, so the
final-epsilon re-run is the same command with one number changed.

### Outputs

- `reports/stage_d1e_power.json` (362 KB; 101 member rows, 7 classes, meta with the four
  source SHA-256s).
- `reports/stage_d1e_power.md` (24.6 KB; sections 1-6 as the brief lists them).

### Still open / not verified by this worker

- The binding n_b for C3 (566 days, `F1_1_h1_RTH`) exceeds the days supplied from the two
  latest starts (516 at S = 2022-01-03, 277 at S = 2023-01-03). That is reported, not judged.
- No independent (fable) verification of any figure here; that is the lead's to route.
- `uv run python -m data.holdout status` was NOT run by this worker either (lead's
  session-level check). No holdout file was read or written.

---

## Second run (lead follow-up: chosen-figure rule + class resolution range)

### What changed

1. **Chosen figure is now `max(analytic, simulated)`** once the two differ by more than 15%
   (`_chosen`). A simulated size BELOW the analytic one is recorded and ignored: for a
   heavy-tailed member at short lengths the replicate's variance estimate is right-skewed, the
   closed-form UCB under-covers there, and adopting the smaller figure would plan on an
   anti-conservative test. Where the simulation asks for MORE days it still wins. Both figures
   and `diff_{a,b}_pct` stay in every row. Flags: `sim_used_larger_{a,b}` (was `sim_used_{a,b}`)
   and the new `sim_smaller_ignored_{a,b}`. Censored cases unchanged. Reason recorded in the
   module docstring, `meta.notes` and the markdown header.
   Flag counts this run: `sim_used_larger_a` 5, `sim_used_larger_b` 3,
   `sim_smaller_ignored_a` 6, `sim_smaller_ignored_b` 11, `sim_censored_below_grid_a` 10,
   `sim_censored_below_grid_b` 32, `zero_variance_draws` 27, `projected` 6.
2. **`classes[c].resolution_range`** added to the JSON: per supplied-days start,
   `{basis, members, min_per_trade, max_per_trade, min_per_day, max_per_day}`, each extreme
   carrying `{member, value}`, over the class's MEASURED members. C7 has no measured member, so
   its range is over the six projected Family H rows and `basis` reads `projected`. Markdown
   section **5a-bis** prints the per-trade range at S = 2019-05-06 and S = 2021-01-04.
3. **A third split** was needed: the two additions put `_d1e_power.py` back over the 800-line
   cap (871), so the inference core moved to `strategy/research/_d1e_power_stats.py` (226
   lines) - the numerics constants, the z-quantiles, the variance/VIF estimators, the analytic
   sample size, the threshold interpolation and the simulation. Pure move, no behaviour change.
   `_d1e_power.py` is now 683 lines. The tests reference the moved names as
   `strategy.research._d1e_power_stats as stats`.

### Members whose chosen figure changed (17 of 101)

| class | member | chosen a | chosen b | why |
|---|---|---|---|---|
| C1 | A-H1 european-open overnight drift | 3 -> 4 | 2 | sim_smaller_ignored_a |
| C1 | A-H3 weekend effect | 52 | 16 -> 21 | sim_smaller_ignored_b |
| C1 | A-H4 rth leg | 95 | 30 -> 38 | sim_smaller_ignored_b |
| C2 | RT2 B-H1 ORB 5-min bars (hold 15 bars) | 44 | 11 -> 17 | sim_smaller_ignored_b |
| C2 | RT3 B-H3 breakout leg 5-min bars | 10 -> 13 | 5 | sim_smaller_ignored_a |
| C2 | RT4 B-H3 fade leg 5-min bars | 10 -> 13 | 5 | sim_smaller_ignored_a |
| C2 | F4_4_round_number_multiples_of_100 | 99 -> 117 | 55 | sim_smaller_ignored_a, sim_used_larger_b |
| C2 | F4_1_rth_open_crossing | 51 | 17 -> 20 | sim_smaller_ignored_b |
| C2 | G2.ETH.15 | 46 | 15 -> 18 | sim_smaller_ignored_b |
| C2 | G2.ETH.60 | 37 | 13 -> 15 | sim_smaller_ignored_b |
| C3 | C-H3 close-location-value reversal | 25 -> 37 | 15 | sim_smaller_ignored_a |
| C3 | G1.RTH.15 | 267 | 63 -> 88 | sim_used_larger_a, sim_smaller_ignored_b |
| C3 | G4.RTH.15 | 122 | 28 -> 39 | sim_used_larger_a, sim_smaller_ignored_b |
| C3 | G1.ETH.30 | 58 | 19 -> 23 | sim_smaller_ignored_b |
| C3 | G4.RTH.30 | 54 | 13 -> 15 | sim_used_larger_a, sim_smaller_ignored_b |
| C3 | G1.ETH.60 | 53 | 16 -> 18 | sim_used_larger_a, sim_smaller_ignored_b |
| C4 | RT7 D-H2 daily-vol sizing | 3 -> 4 | 2 | sim_smaller_ignored_a |

Every change is upward; no chosen figure fell. Largest moves: C3 G1.RTH.15 n_b 63 -> 88 (+40%),
C3 G4.RTH.15 n_b 28 -> 39 (+39%), C2 RT2 n_b 11 -> 17 (+55%), C3 C-H3 n_a 25 -> 37 (+48%).

### Class binding members, before -> after

Only C1's binding n_b moved; every binding member id is unchanged.

| class | binding n_a | binding n_b |
|---|---|---|
| C1 | 95 (A-H4 rth leg), unchanged | **30 -> 38** (A-H4 rth leg) |
| C2 | 492 (G3.RTH.5), unchanged | 193 (G3.RTH.5), unchanged |
| C3 | 1,447 (F1_1_h1_RTH), unchanged | 566 (F1_1_h1_RTH), unchanged |
| C4 | 436 (F2_4_15min_vol_tercile_top), unchanged | 171 (F2_4_15min_vol_tercile_top), unchanged |
| C5 | 11 (E-H1 scheduled macro drift), unchanged | 4 (E-H1 scheduled macro drift), unchanged |
| C6 | 116 (C-H4 passive-fill reversal), unchanged | 46 (C-H4 passive-fill reversal), unchanged |
| C7 | 73 (H6 prior-close, projected), unchanged | 29 (H6 prior-close, projected), unchanged |

Section 2b is unchanged in substance: C3's 566 days still exceed supply at S = 2022-01-03 (516)
and S = 2023-01-03 (277); every other class clears every start.

### Commands and runtime

```
uv run ruff check strategy/research/_d1e_power.py strategy/research/_d1e_power_stats.py \
    strategy/research/_d1e_power_report.py strategy/research/_d1e_calendar.py \
    tests/test_d1e_power.py                                          -> All checks passed
uv run pytest tests/test_d1e_power.py -q                             -> 10 passed in 1.94 s
uv run python -m strategy.research._d1e_power --eps-day 34 --jobs 8  -> 151.2 s (2m33 wall)
```

Test 5 now also pins the new rule (simulated larger wins, simulated smaller ignored, inside the
15% band unflagged); the known-answer tests 1-4, 6 and 7 are untouched. `--eps-day` is still the
only non-default argument, so the final-epsilon re-run is the same command with one number
changed.

---

## Third run (per-micro unit, finding R-1)

### What changed

- `trial_series()` now returns `record["daily_net_ticks_per_micro"]` as is. `USD_PER_TICK_2_MICROS`
  is deleted and there is no position-size assumption anywhere in the module; a test asserts the
  constant is gone. Trade counts still come from `daily_n_trips`; no `per_trade` / `per_day`
  summary field is read by this module (it never was), so nothing else needed switching.
- Family H per-trade SD proxies: 100 -> **200** for H1-H5, 115 -> **230** for H6. Firing
  fractions unchanged. Test 7 updated to the corrected constants.
- Test 4 rewritten: a fake member carries `daily_net_ticks_per_micro` and the test asserts
  pass-through, with the convention spelled out (one trip of $5.00 on 2 micros = 5.00/(1.25x2)
  = 2.0 ticks per micro). The module does not build that series, so the assertion is on
  pass-through, as instructed.
- The unit correction is stated in the module docstring, in `trial_series`' docstring, in
  `meta.notes` and in a new paragraph of the markdown header, each citing
  `reports/stage_d1e_adjudication.md` finding R-1.
- `meta.source_sha256["reports/stage_d1e_members_trials.json"]` is now `f546e3f325b0...`,
  the regenerated artifact.

### Effect

Trial and projected members' SDs doubled, so their sample sizes went up by about 4x
(n scales with SD^2); 62 chosen figures moved by 2x or more, every one upward, and all 62 are
trial or projected rows. Statistic members (F*, G*) are identical to the previous run, as
expected - they are built from tick sums, never from dollars. The largest single move is
C3 C-H3 close-location-value reversal n_a 37 -> 185 (x5.00, the extra factor coming from the
chosen-figure rule); the typical move is x3.8 to x4.0. Two rows moved exactly x2 off a
floor of 1 day (E-H2, RT6).

| class | binding n_a before -> after | binding n_b before -> after |
|---|---|---|
| C1 | 95 -> **379** (A-H4 rth leg) | 38 -> **149** (A-H4 rth leg) |
| C2 | 492 -> 492 (G3.RTH.5) | 193 -> 193 (G3.RTH.5) |
| C3 | 1,447 -> 1,447 (F1_1_h1_RTH) | 566 -> 566 (F1_1_h1_RTH) |
| C4 | 436 -> 436 (F2_4_15min_vol_tercile_top) | 171 -> 171 (F2_4_15min_vol_tercile_top) |
| C5 | 11 -> **41** (E-H1 scheduled macro drift) | 4 -> **16** (E-H1 scheduled macro drift) |
| C6 | 116 -> **461** (C-H4 passive-fill reversal) | 46 -> **181** (C-H4 passive-fill reversal) |
| C7 | 73 -> **290** (H6 prior-close, projected) | 29 -> **114** (H6 prior-close, projected) |

Binding member ids are unchanged in every class. Section 2b is unchanged in substance: C3's
566 days remain the only binding n_b that exceeds supply, at S = 2022-01-03 (516) and
S = 2023-01-03 (277); C6's 181 and C1's 149 clear every start.

Descriptive: measured members whose per-trade eps_min at S = 2019-05-06 falls below the 2.11
market cost bar: **47 of 95** (was 54 of 95 before the correction, since every trial member's
eps_min doubled).

### Commands and runtime

```
uv run ruff check strategy/research/_d1e_power.py strategy/research/_d1e_power_report.py \
    tests/test_d1e_power.py                                          -> All checks passed
uv run pytest tests/test_d1e_power.py -q                             -> 10 passed in 0.29 s
uv run python -m strategy.research._d1e_power --eps-day 34 --jobs 8  -> 43.1 s
```

The run is faster than the previous two because the competing power-gate extension job had
finished, not because of any change here. `--eps-day` remains the only non-default argument.
