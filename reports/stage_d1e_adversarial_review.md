# Stage D.1e Task 5d: adversarial review of the two pre-registration documents

Reviewer: worker (Fable 5.1, max effort), 2026-09-22. Brief: lead-scratch/brief_5d_review.md.
Documents reviewed line by line, in their current draft state (every [FILLED BEFORE HASHING]
value present, the two hash placeholders open): `reports/stage_d1f_confirmation_list.md`
(430 lines) and `docs/NULL_CRITERIA.md` (229 lines). epsilon_day = 34, N_C6 = 46 taken as
given. The review attacks rules, definitions and wording; where a rule turns out to be
wrong in a way that also changes a filled number, the number consequence is stated so the
lead can route a recomputation, not verified here.

What was checked mechanically, not only read:
- All 31 sha256 values in confirmation-list section 0 recomputed: every one matches disk.
- epsilon re-derived on the PINNED extension file (sha256 583cca... matches disk): 100 rows,
  66 pass / 30 fail / 4 marginal, smallest passing extension cell $92.018 (consistency, T=8,
  p=0.575, R=1.0); binding cell stays power_gate.json consistency T=2 p=0.60 R=1.00 at
  $87.481 -> 34.99 -> 34. epsilon = 34 holds on the pinned version (the verification report
  worked on a 90-row version and asked for exactly this re-derivation).
- The 21 Tier A statistics cross-checked against progress.md's D.1b "Not selected, ranked by
  the size of the implied edge" table (14) and the D.1d top-of-p-ordering table (7): match.
- Position size read from every trial module; trip P&L in USD read from
  reports/stage_d1e_members_trials.json; C-H4's session gating read from its code; the
  slippage table's buckets and sizes read; the release-date table of E-H1/E-H2 read; the
  runner's code path to `funnel.null_generator._refuse_non_research` traced.
- No network, no Databento call, no holdout byte, no TopstepX. No file other than this one
  written.

Severity: BLOCKER = could flip or fake a verdict while looking compliant; SHOULD-FIX = an
ambiguity a careful reader would exploit or misread; NOTE = cosmetic or a pin worth adding.

---

## 1. Re-tuning room and pinning (R)

### R-1  BLOCKER  The daily-series unit assumes 2 micros; every trial is coded at 1 micro
Quoted (list 3.1): "For a trial: d_t = daily_net_usd[t] / 2.5 (2 micros x $1.25) over the
window's trade dates, $0 on days without trades, from the runner's daily_net_usd."
Quoted (list 2.1 A1): "with the canonical engine configuration (2 micros, market fills at
the calibrated cost model; C-H4 with the existing trade-through passive fill model)."

Fact: the engine configuration does not set size; the strategy does. Every one of the 31
trial modules sets `QUANTITY_MICROS = 1` (a_session_clock/h1..h4, b_reference_breakout/
h1..h4, c_short_horizon_reversal/h1..h4 including C-H4 "Quantity 1 micro", d_volatility_state/
h1, h3, h4, e_calendar_event/h1..h4, g_timeframe/retests.py `QUANTITY_MICROS = 1`); D-H2 and
RT7 size 1..5 by formula (`MIN_QUANTITY_MICROS = 1`, `MAX_QUANTITY_MICROS = 5`). The
factories in `_lead_accounting.TRIALS` pass no quantity. The recorded trip P&L confirms it:
A-H4 rth leg mean trip $19.96, SD $285.98 -> 15.97 and 228.8 net ticks PER MICRO at 1 micro;
the list's unit gives 7.98 and 114.4 (the coverage-map figures). C-H4: -$2.945 per trip ->
-2.36 ticks per micro, not -1.18.

Exploit: as written, d_t is HALF the member's net ticks per micro per day for 29 trials and
for C-H4, so "UCB95 < 34" is really "UCB95 of the per-micro edge < 68". A trial with a true
edge of 60 ticks per micro per day (= $150 per day at 2 micros, well above the $85 gate
boundary the whole epsilon derivation rests on) would be declared null. Every trial's null
is twice as easy as the economics say; the statistics (per-event ticks, per micro by
construction) and the H tests (2 micros, /2.5 correct) are on the right scale, so Tier A is
internally inconsistent. The reverse fudge is also open: a session could "fix" it by
instantiating the trials at 2 micros for the confirmation run, a configuration no
continuity check covers (the train-union accounting is at 1 micro) and one that changes the
slippage bucket (R-8).

Consequence for filled numbers (not verified here, direction certain): every trial's SD_day
in the power table is at half scale, so every trial's n_b and n_a are understated by about
4x (n scales with SD^2): A-H4 rth leg 38 -> ~150, C-H1 47 -> ~190, E-H1 4 -> ~16, C-H4 46 ->
~180. The C7 proxies (per-trade SD "100 ticks per micro, between B-H1 hold-75's 49.8 and
A-H4 rth leg's 114.6") are read off the half-scale table, so the Family H projections are
understated too (H-5). N_C6 = 46 becomes roughly 180 days at the correct unit, which
quadruples D.1g's MBO purchase (C-1). NULL_CRITERIA section 2.3's per-trade epsilon and
"typical trades per day" are unaffected (r is a count). Power remains reachable for every
class at every S in the table after the correction, but the table must be re-issued.

Fix (lead decides between the two consistent options; the third is not allowed):
(a) Per-micro unit, recommended: "For a trial, d_t = daily_net_usd[t] / (1.25 x q_m), where
q_m is the member's coded contract quantity: 1 for the 29 fixed-size trials and for C-H4;
2 for H1 to H6 (whose daily_net_usd is at 2 micros). For D-H2 and RT7, whose size varies in
[1, 5] by rule, q_m = the member's mean filled micros per round trip over the confirmation
window, recorded in the run JSON [or another rule the lead fixes now]. Scaling a 1-micro
P&L to the 2-micro bar assumes linear costs; the size-5 slippage bucket that a 2-micro
order would pay is slightly higher, so the assumption overstates the 2-micro edge and is
conservative for the null claim."
(b) Dollar unit at coded size: compare daily_net_usd against epsilon x 1.25 x q_m dollars.
Same content, different presentation.
Not allowed: running the trials at 2 micros in D.1f (violates "every parameter frozen at
its recorded value" and the continuity check).
Also: correct A1 to "each trial at its coded quantity (1 micro; D-H2 and RT7 by their sizing
rule); H1 to H6 at 2 micros"; re-issue section 4 and NULL_CRITERIA section 5 at the
corrected unit before hashing; re-verify.

### R-2  BLOCKER  The trial parameters and the continuity target live in unhashed files
Quoted (list 0): "Trial modules (the code is the definition; every parameter is the literal
in the file):" and "The 31 trial IDs are the label strings in
strategy.research._d1d_accounting.ALL_TRIALS (24 from _d1b_accounting.ALL_TRIALS plus the 7
RETESTS in g_timeframe/retests.py). D.1f imports that tuple; it does not retype labels or
factories."
Quoted (list 1.4): "every trial re-run on the train union must reproduce
reports/stage_d1d_accounting.json to the cent before any confirmation figure is read."

Fact: the parameters that distinguish 8 of the 31 trials are NOT literals in the hashed
modules. They are lambda arguments in `strategy/research/_lead_accounting.py` (not hashed):
`H2RthCloseWindowSessionPosition(direction="buy")` / `(direction="sell")`,
`H4EthVsRthDecomposition(session="eth")` / `(session="rth")`,
`H1FrictionAwareOpeningRangeBreakout(hold_minutes=5)` / `(hold_minutes=75)`. The 31-tuple
is assembled in `_d1d_accounting.py` (not hashed) from `_lead_accounting.TRIALS` (not
hashed), `f_data_native/trials.py` and `g_timeframe/trials.py` (both empty today, both not
hashed, both importable places to add a 32nd "trial"). The continuity target
`reports/stage_d1d_accounting.json` is not hashed either.

Exploit: change `hold_minutes=75` to 60, or swap buy/sell, regenerate
stage_d1d_accounting.json with `uv run python -m strategy.research._d1d_accounting`, and
every hash in section 0 still matches while the continuity check passes to the cent. The
only defence the list has against a parameter change is a JSON it does not pin.

Fix: add to section 0, with these current values:
- strategy/research/_lead_accounting.py  456be614636748809ab986656654a1fcf7269ee542cc769f77e36da1e9c401ee
- strategy/research/_d1d_accounting.py  df741c259408647fc5e09540e9669dc8c384e657a59991b41ef6243c6ca8c8ff
- strategy/research/f_data_native/trials.py  cf9073b326c5b43bc5d74dc5bcacfd1da05ee2bd85c9b4bcd4df5f41f020b9fd
- strategy/research/g_timeframe/trials.py  0a0bd610ae6e2f6644b0429eda3d27654d09f49b6662bfdc46bc111d1a7b97b1
- reports/stage_d1d_accounting.json  d00ff04ba381b1e077d859393ee374746aa954db190b12ac06e64c7dc259c968
- reports/stage_d1b_accounting.json  fd9120990606f8e533904299102de157883d9aacf6316906a63fa3009f2b0a5f
- reports/stage_d1_accounting.json  7e50a98e983e164e1f27e698bb892be7cfbf6c0b7cdbf2b42ff3a508f9b32201
and add a third column to the A1 table with each member's factory expression verbatim
(e.g. `lambda: H1FrictionAwareOpeningRangeBreakout(hold_minutes=75)`), so the parameter is
in the hashed document, not only in a hashed file.

### R-3  BLOCKER  Section 5.4 orders an edit to two hashed modules, and the runner cannot reach 2019-2024 without changes section 5 does not list
Quoted (list 0): "A member whose referenced file changes before D.1f runs is INVALID until
this list is re-issued under a new hash; D.1f must verify every hash before running."
Quoted (list 5.4): "The F and G statistics modules: a date-set parameter in place of the
EDA-date resolution; identical output on the EDA dates asserted by a test."
Quoted (list 5.1): "screening.runner: a ConfirmationWindow object accepted by
screen_candidate, loading the confirmation parquet through a loader with the same refusal
semantics as data.research_bars (holdout-2 dates refused, mined dates refused for
confirmation runs). The train-union path stays as is for continuity runs."

Fact 1: `f_data_native/_stylized_facts.py` and `g_timeframe/_stylized_facts.py` are in
section 0's hash list. 5.4 requires editing them. As written, D.1f cannot satisfy both:
the edit makes all 64 statistic members INVALID by section 0's own rule. The
`_d1e_event_series.py` pattern already shows the edit is unnecessary: the modules' builders
(`build_f1..build_f6`, `build_days`, `build_statistics`) take the date list as an argument
and were called from a wrapper "on the same 139 EDA dates. Neither module is edited or
monkey-patched." `resolve_eda_dates()` (which hard-codes indices 142:289 of the research
parquet and asserts subset-of-train-union) is only the default caller.

Fact 2: the harness changes D.1f needs are larger than 5.1 to 5.6 list, and each is a place
where the confirmation path can diverge from the train-union path while the continuity
check passes:
- `screening.runner.screen_frame` (line 309) calls `session_benchmark(frame, ...)`, which
  calls `funnel.null_generator.build_segment_table`, which calls `_refuse_non_research` and
  RAISES "non-research (embargo/out-of-range) trade dates refused" for any trade date
  outside 2025-04-01..2026-06-12. Every confirmation run through the runner fails until
  `funnel/null_generator.py` or `screening/drift.py` is changed. Neither is in section 5.
- `screen_candidate` (lines 324-327) refuses any date outside `train_union_window()` and
  (line 334) takes its splice dates from `splice_trade_dates_from_parquet(RESEARCH_SERIES_PATH)`,
  the research parquet, not the confirmation parquet. The confirmation path needs its own
  splice dates, its own drift path and its own session benchmark, all recomputed on the
  confirmation bars.
- `data/pull_mes.py` hard-codes `WINDOW_START = 2025-04-01`, `WINDOW_END = 2026-09-16`,
  pulls newest-first, and its `request_touches_sealed_window` guards only holdout-1.
- `data/build_mes_bars.py` hard-codes the same window and derives the rolls file name from
  it; `data/bars.py`/`data/validate.py` are on the build path.
- `data/cme_calendar.py` (5.3) is imported by `data/session.py`, `data/splits.py` and
  `sim/engine.py` (D-2).
- `strategy/research/e_calendar_event/h1_scheduled_macro_drift.py` holds the release table
  that E-H1 and E-H2 need for 2019-2024 (N-1).

Exploit: any of these files is changed "to make the confirmation run work", the change is
not on the train-union path, continuity passes, and nothing in the document says the change
must be frozen or even listed.

Fix: (i) strike 5.4's "a date-set parameter in place of the EDA-date resolution"; replace
with "the two hashed statistics modules are NOT edited; a new module
strategy/research/_d1f_statistics.py calls their builders with the confirmation date set
exactly as strategy/research/_d1e_event_series.py (sha256 51ec1d88...) calls them with the
EDA dates; a test asserts that the wrapper on the 139 EDA dates reproduces every recorded
estimate, n and implied edge to 1e-9 (the Task 1c check)". (ii) Enumerate every file D.1f
MAY change: screening/runner.py, screening/drift.py, funnel/null_generator.py (the
research-slice refusal only, replaced by a refusal of holdout-1, holdout-2 and, for
confirmation runs, mined dates), data/pull_mes.py, data/build_mes_bars.py, data/bars.py,
data/validate.py, data/holdout.py, data/cme_calendar.py, data/research_bars.py (a
confirmation loader), the new h_daily_bar/ and _d1f_*.py modules, and the E-H1 release table
by whatever mechanism N-1 settles. (iii) State: "Every other file under screening/, sim/,
funnel/, rules/, data/, strategy/ is byte-identical to the harness-freeze manifest (R-4)."

### R-4  BLOCKER  Nothing freezes the harness at run time; the continuity check covers only the train-union path
Quoted (list 5.6): "refuses to run if any hash in section 0 or the hash of this file or of
docs/NULL_CRITERIA.md has changed."
Quoted (list 1.5): "6. Continuity check on the train union. 7. Run the list."

Fact: the numbers for 37 of 58 Tier A members come out of screening/runner.py,
screening/drift.py, screening/trips.py, sim/engine.py, sim/fill_model.py, sim/costs.py,
sim/slippage_calibration.json, funnel/power_gate.py, reports/power_gate.json,
funnel/null_generator.py, funnel/multiple_comparisons.py, rules/xfa_rules.py,
data/cme_calendar.py, data/session.py, data/bars.py, data/build_mes_bars.py,
data/research_bars.py, data/splits.py, strategy/interface.py. None is hashed anywhere in
either document. screening/runner.py is modified and uncommitted today (git: ` M
screening/runner.py`), so "commit 2530d29 plus this stage's additive changes" does not
pin it. The continuity check (1.4) reproduces the 31 trials on the 289 train days; it is
blind to any code path the train-union run does not exercise (the confirmation loader, the
2019-2024 calendar entries, the new roll-blackout computation on the confirmation parquet,
the refusal semantics, anything gated on dates before 2025).

Exploit: after step 7 shows a marginal member, edit an early-close time, a slippage bucket,
or the drift-path exclusion for the confirmation path, re-run; the train-union continuity
still passes; section 5.6's checks still pass.

Fix: add to 1.5 a step between 1 and 2: "1b. Harness freeze: D.1f writes
reports/stage_d1f_harness_freeze.json listing the sha256 of every file under screening/,
sim/ (including sim/slippage_calibration.json), funnel/ (including reports/power_gate.json),
rules/, data/*.py, strategy/interface.py, strategy/research/h_daily_bar/*, strategy/research/
_d1f_*.py and the files in section 0 and R-2, and prints it into the STATE file BEFORE any
quote or purchase. _d1f_confirmation.py refuses to run if any listed hash differs, checks
again when step 8 completes, and records the manifest's own sha256 in every output JSON.
Any change to a listed file after step 1b voids the run; a re-run is a new declaration
under a new name, and the voided run's results are still reported." Baseline today, for
the lead's diff: runner 5e514eed..., drift 41d18d47..., trips 15706210...,
engine 2f5f11b1..., fill_model 709d4892..., costs af3a21c9...,
slippage_calibration.json 2d680dd2..., power_gate.py bf5aac6e..., power_gate.json
e5708824..., null_generator 2d9d2300..., multiple_comparisons 6666cf22...,
xfa_rules c7a4a375..., cme_calendar 5f24edda..., session 4f419645..., bars b8fbc955...,
build_mes_bars 6881a380..., research_bars 52ad49f8..., splits cf2e0ca4..., holdout
ec586af1..., adapter 6b3f13fa..., pull_mes bc5716a1..., interface defdd336... (full
values in the shell log of this review; the lead recomputes them at freeze time).

### R-5  SHOULD-FIX  The event value e for 64 members is defined in an unhashed file, and the F4.4 description is inverted
Quoted (list 2.1 A2): "for F4.1, F4.4 and every G statistic, the signed forward move in
ticks the estimate averages; for F4.4 the control-level subtraction is applied exactly as
the recorded implied edge applies it"
Quoted (list 2.1 A2 table): "| F4_4_round_number_multiples_of_100 | F / C2 | -3.3631
(estimate -4.5774 before the control subtraction) | -1 | 559 |"

Fact: `strategy/research/_d1e_event_series.py` (sha256 51ec1d88..., not hashed) is the only
place the per-event value is operationally defined ("sign(sign_pred) * ticks per pooled
observation" for correlation statistics; "round_ticks" for F4.4; "x" for G). For F4.4 the
recorded JSON says the opposite of the list: `recorded_implied_edge_ticks = -3.3631` is the
plain mean of the round-level leg ("event_mean_ticks": -3.3631, "event_series_definition":
"round_ticks ... mean = implied_edge_ticks"), and `recorded_estimate = -4.5774` is the
control-SUBTRACTED difference (control mean +1.214, n_control 2549). So -4.5774 is AFTER
the control subtraction, not before, and "as the recorded implied edge applies it" means
"not at all". The coverage map carries the same inversion.

Exploit: a D.1f coder can implement F4.4's v with or without a per-event control
adjustment (and there is no per-event form of a difference of means; it would have to be a
window-wide constant subtracted from every event), citing either half of the sentence.

Fix: "F4_4_round_number_multiples_of_100: e = round_ticks (the signed forward 15-minute
move from the round level), v = s x e - c, with NO control-level adjustment; the recorded
implied edge -3.3631 is that plain mean, and the control-subtracted estimate -4.5774 is
reported descriptively beside it." Hash `_d1e_event_series.py` in section 0 and state that
the D.1f wrapper (R-3) reproduces its per-event definitions.

### R-6  SHOULD-FIX  Sample-derived thresholds are called "declared literals"
Quoted (list 2.1 A2): "(the only change is the date set; every threshold, bucket grid,
refractory period, baseline length and timeframe is the declared literal)"

Fact: F2_4's volatility tercile edges ("tercile edges from the pooled EDA sample"), F5_1 and
F5_2's tercile edges, F5_3's pooled regression, and G1/G4's Q80 ("computed once and
FROZEN" on the EDA sample) are sample quantities, not literals. On a new date set the
hashed code recomputes them from that set. Trailing baselines (F5_1, G1, G4: "previous 20
EDA dates") likewise re-anchor to the new window's first 20 dates.

Exploit: implement either "recompute on the confirmation window" (what the code does) or
"freeze at the EDA values" (which requires reading them out of the D.1b/D.1d JSONs) and
call both "the declared literal".

Fix: "Thresholds that the declarations define as sample quantiles or fits (F2_4, F5_1, F5_2
tercile edges; F5_3's log-range on log-volume regression; G1 and G4's Q80; the F5_1/G1/G4
trailing 20-date baselines) are recomputed on the confirmation window's own dates, pooled
over the whole window, exactly as the hashed code computes them on the EDA dates. They are
not frozen at the EDA values." (Or the reverse, with the EDA values listed here.)

### R-7  SHOULD-FIX  Step 1 lets H1 to H6 be run on the mined window before the confirmation
Quoted (list 1.5): "1. Harness work (section 5), built and tested on the existing research
bars, before any purchase."
Quoted (list 5.5): "strategy/research/h_daily_bar/: the six H modules with the look-ahead
tests of 2.1 A3."

Exploit: the D.1f coder "smoke-tests" H1 to H6 through screen_candidate on the train union,
sees six P&Ls, and the spec's remaining ambiguities (H-2, H-3, H-6, H-7) get resolved in
the direction those P&Ls suggest. The specification is hashed, so the resolution is
visible, but the choice is still made after a look.

Fix: "H1 to H6 are exercised before the purchase only on synthetic bars (the look-ahead
tests of A3). No H module is run on the research parquet, the train union or any fold
before step 7; if one is, the run is logged in the STATE file as a look, and it counts as
one screen in N for that member."

### R-8  NOTE  Two-micro orders are costed at the five-micro calibration
Fact: `sim/slippage_calibration.json` has sizes [1, 5, 10, 20, 50]; `sim.costs.calibrated_size`
picks the smallest calibrated size >= qty, so H1 to H6 (2 micros) pay the size-5 bucket
(one side mean 0.539..0.588 ticks against 0.52..0.56 at size 1). Conservative for an edge
claim, marginally anti-conservative for the null. State it in A3 and in NULL_CRITERIA 4.3.

### R-9  NOTE  The bootstrap is named by description, not by function; p-value and quantile conventions unpinned
Quoted (list 3.1): "stationary block bootstrap of the daily series (Politis-Romano,
circular, mean block 5 days, 10,000 resamples, seed 20260921), the same construction as
screening/drift.py and the F/G inference. UCB95 = the 95th percentile of the bootstrap
distribution of the mean (one-sided). ... One-sided p for H0: theta <= 0 is the fraction of
centred replicates (theta* - theta_hat) that are >= theta_hat."
Fact: drift.py uses seed 20260918 and `np.quantile`; F/G use 2,000 resamples and seed
20260918; so "the same construction" is loose. With B = 10,000 the smallest p is 0, which
Holm rejects at any alpha.
Fix: "Implementation: `funnel.null_generator.stationary_bootstrap_indices(rng, n, n, 5.0)`
as `screening.drift.bootstrap_mean_lower_bounds` uses it, with a fresh
`np.random.default_rng(20260921)` per member; UCB95 = `np.quantile(means, 0.95)` (default
linear); p = (1 + #{theta* - theta_hat >= theta_hat}) / (B + 1)."

### R-10  NOTE  The gate call for a statistic is underspecified
Quoted (list 3.2 ii): "for a statistic, the equivalent gate call on its event p/R/T"
Fix: "p = share of events with v > 0 (ties neither), R = mean of positive v over mean of
|negative v|, T = `screening.trips.nearest_segments_per_day(events per window day)` on the
gate grid {1, 2, 4}, standard path, robust=True, as `screening.runner._gate` does for
trips." Affects edge claims only (makes them harder), but two implementations are possible.

---

## 2. Epsilon (E)

### E-1  SHOULD-FIX  The epsilon paragraph describes a file version that is not the pinned one, leaves "robust-80% passing" undefined, and does not forbid recomputation
Quoted (NULL 2.2): "the minimum over 216 cells, the 120 grid cells plus 96 extension rows
at T = 1, 2, 4, 8 and 16 on both paths (reports/stage_d1e_gate_extension.json, sha256
583cca13086731914fa7e63c0f4fb6ffa8e85aa402921ab199f7ee6bbe1facdd at 06:22Z; the four
standard-path T = 32 cells that were still running cannot lower it, since the only one
priced below the binding cell sits near $20 per day, far under every measured boundary)"
and "the smallest net_edge_usd_per_day_at_2_micros among all robust-80% passing cells over
both payout paths and every evaluated T (grid plus extension)".

Facts: the file with sha256 583cca... has 100 rows, not 96: 12/10/11/9/6 per path at T =
1/2/4/8/16 plus the four standard-path T = 32 cells, all finished (p=0.40,R=2.0 fail
$92.15; p=0.425,R=2.0 pass $188.50; p=0.45,R=1.5 fail $20.65; p=0.475,R=1.5 fail $113.36).
The cell count is 220. epsilon = 34 is unchanged (checked above). "Robust-80% passing" is
power_gate.json's `verdict_rule`: "pass if power - 1.96*se >= 0.80; marginal if power >=
0.80; else fail"; the nearest excluded cell (consistency T=4 p=0.58 R=1.0, $84.41, power
0.8043, lower95 0.7956) is marginal, and the verification report notes epsilon is "one MC
verdict away from 33". power_gate.json (e5708824...) holds the binding cell and is not
pinned; reports/stage_d1e_power_gate_cells.json is cited and not pinned.

Exploit: re-run the gate at another seed (8,000 careers per cell) or "include marginal
cells" and derive 33 or 35 while citing the same rule; or re-read "passing" as point
estimate >= 0.80.

Fix: replace the parenthetical with: "epsilon_day = 34 is FINAL for this list. It was
derived once from two pinned files, reports/power_gate.json (sha256 e5708824...) and
reports/stage_d1e_gate_extension.json (sha256 583cca...; 100 rows, 66 pass / 30 fail / 4
marginal, including the four finished standard-path T = 32 cells, one of which passes at
$188.50), 220 cells in all. 'Passing' means `robust_c80_verdict == "pass"`, i.e. Monte
Carlo power minus 1.96 x se >= 0.80; marginal cells are excluded. No recomputation,
re-simulation or extension of the cell set changes epsilon for this list; a different
epsilon needs a new list under a new name." Drop the "still running" sentence and the
power_gate_cells.json citation or pin it.

### E-2  SHOULD-FIX  The daily framing lets a class go null by inactivity, and section 7 does not force the per-trade resolution into the statement
Quoted (NULL 2.4): "It is large for low-frequency members because a strategy that trades
once a day must earn about a session's worth of typical movement in edge to fund a
Combine".
Quoted (NULL 7): "add the descriptive resolution (the largest UCB95 per trade found in the
class)".

Fact: E-H3 traded 4 times in 289 days (daily SD 0.93 half-scale ticks; n_b = 1 day); E-H2,
E-H4, D-H1, RT6, B-H4, D-H4 all have n_b = 1 or 2. Their achieved null power at epsilon is
~1 from the first week: a member that almost never trades cannot have a 34-tick daily edge.
That is correct economics, but it means C5's null (per-trade epsilon 351 ticks; E-H3's
2,457) is established by inactivity, and section 7 then permits "no strategy class ... has
an edge large enough to fund the Topstep funnel" with the resolution as an optional
appendix.

Exploit: a class whose members were never really tested is announced null with the same
sentence as C3, whose members were resolved to 0.02 ticks per trade.

Fix: in section 7, make the resolution mandatory and per class: "Every class statement
carries, in the same sentence, the class's per-trade epsilon at its confirmation-window
frequency, the member with the fewest trades or events and its count, and the largest
UCB95 per trade in the class." And decide now (lead) whether a minimum-activity rule
applies: e.g. "a member with fewer than [n] closed round trips or events on the confirmation
window is inconclusive (insufficient activity), not null" (see N-2 for the zero case, which
already exists). If no such rule is wanted, say so explicitly: "no minimum activity is
required; a null established by inactivity is labelled 'null by inactivity' in the report".

### E-3  NOTE  The cost sentence is framed per trade where the test is per day, and the "overstates" claim points the wrong way
Quoted (list 2.1 A2): "c is fixed at the T=1 figure for every statistic whatever its event
frequency: the modelled cost's dependence on T is 0.05 ticks (2.111 at T=1, 2.084 at T=2,
2.073 at T=4, 2.064 at T=8), which overstates cost on multi-event days by under 2% of the
smallest per-trade epsilon and is in the conservative direction for an edge claim."
Facts: per DAY, 0.05 x 928 events (F1_1_h1_ETH) is 46 ticks, more than epsilon_day; the
per-trade "under 2%" hides it. But the T-dependence is a funnel-segment artefact (where in
the session the funnel's round turns fall), not a discount for frequency: the engine
charges commission 0.976 ticks plus two one-side slippages of 0.52..0.59 per round turn
regardless of how many trades a day, so 2.11 is the right order for every event and is not
an overcharge. Overcharging would in any case be ANTI-conservative for the null (lower v,
lower UCB). Time of day is ignored for statistics (ETH one-side mean 0.556 vs RTH 0.529 at
size 1: about 0.05 per round turn, negligible).
Fix: "c = 2.11 ticks is the modelled market round turn at 2 micros (commission $1.22 plus
two one-side slippages at the mean of the calibrated table). It is charged per event at
every frequency; the funnel's T-dependent figures are not frequency discounts. Statistics
ignore the time-of-day slippage table; the RTH/ETH difference is about 0.05 ticks per round
turn."

### E-4  NOTE  "Typical trades per day" mixes trials and statistics by class
Quoted (NULL 2.3): "Typical frequency is the median trades per day of the class's trial
members on the 289-day train union". C2's 0.945 is the trials' median; C2's statistics run
0.8 to 9.6 events per day. Descriptive, but label the column "trial members only".

### E-5  NOTE  r for the per-trade translation is not defined for trials
Quoted (list 3.1): "r = trades (or events) per window day". Pin: "for a trial, r =
ScreeningReport.trades_per_day on the confirmation window (closed round trips over all
window dates, blackout dates included); for a statistic, r = events over the statistic's
own post-exclusion date count".

---

## 3. Family H (H)

### H-1  SHOULD-FIX  The instrument guard does not cover H3 on the first post-splice day, though the text says it does
Quoted (list 2.1 A3): "Instrument guard: if the most recent complete daily bar's
instrument_id differs from the instrument_id of day d's 08:30 bar, no trade on day d
(levels are not comparable across a splice; the roll blackout already covers the splice
date and the two prior sessions, this guard covers the first post-splice day for H3 and H6
as well)."
Fact: the splice happens inside the splice trade date's ETH (18:00/19:00 CT, drift.py), so
the splice day's RTH bars carry one instrument_id and its daily bar is COMPLETE by the
list's own definition. On d = splice + 1, the most recent complete bar (d-1 = splice day) has
day d's instrument_id, so the guard passes, and H3 compares H[d-1] (new contract) with
H[d-2] (old contract) across a +206..+226-tick basis jump. The guard as written only fires
on the splice day itself, which the blackout already removes. H1, H2, H4, H5 use ranges
(basis-free) and H6 uses same-day values, so only H3 is affected, on about four days a
year.
Exploit: a coder who implements the sentence literally ships a contaminated H3; a coder
who "fixes" it after seeing H3's P&L has re-parametrized a hashed spec.
Fix: "Instrument guard: every daily bar that enters day d's condition (d-1 for H1, H2, H4,
H5, H6; d-1 and d-2 for H3; the 60 trailing bars for H4 and H5 are ranges and are exempt)
must carry the instrument_id of day d's 08:30 bar; otherwise no trade on day d."

### H-2  SHOULD-FIX  H4/H5 need 61 complete bars, the lookback says 60
Quoted: "Lookbacks count complete bars: k = 4 (H1), 7 (H2), 2 (H3), 60 (H4, H5), 1 (H6)." and
"Range[d-1] <= P33.33 of Range over the 60 complete bars before d-1" and "tercile cuts ...
of the trailing 60 complete ranges".
Fix: "H4 and H5 need d-1 plus the 60 complete bars before it (61 complete bars); the
percentiles are over those 60, excluding d-1. No trade until 61 complete bars exist."

### H-3  SHOULD-FIX  The exit bar may not exist
Quoted: "Exit for every H test: a market_intent to flatten emitted on the bar with CT time
14:58 (fills at the 14:59 open)."
Fact: a minute with no trade has no bar. If 14:58 is missing, no exit is emitted and the
engine's forced flatten (decision inside the flatten window, fill at the next open) closes
the position at a different price.
Fix: "emitted on the first bar the strategy sees with CT time >= 14:58 and before the
no-new-positions time; if none exists, the engine's forced flatten applies and the day is
counted and logged as a forced exit."

### H-4  SHOULD-FIX  Say that the production factories take no arguments
Quoted: "(60-day warm-up shortened to 6 in the test through a test-only parameter that the
production factory does not expose)".
Fix: "The six factories registered for D.1f take no arguments. Every constant is a
module-level literal; the test-only warm-up override is a private constructor argument
with the production default, read from no configuration and unused by the factory."

### H-5  SHOULD-FIX  The C7 projections inherit R-1's unit error
Quoted (coverage map, cited by list 4): "Per-trade SD for H1-H5 ...: 100 ticks per micro,
between B-H1 hold-75's 49.8 (75-minute hold) and A-H4 rth leg's 114.6 (full-session
hold)". Those proxies are at half scale (R-1: 99.6 and 228.8 per micro). The H tests trade
2 micros and their /2.5 is right, so their projected SD is about half the truth and their
n_b (H6: 29) about a quarter. Re-project after R-1.

### H-6  NOTE  "strict inequalities as written" contradicts the table
Quoted: "CLV cuts 0.2 and 0.8; strict inequalities as written." vs H6 "CLV >= 0.8 buys, CLV
<= 0.2 sells", H4 "<= P33.33", H5 ">= P66.67".
Fix: "inequalities exactly as the table writes them: strict for H1, H2, H3 and the breakout
triggers; non-strict for H4, H5 and H6's CLV cuts."

### H-7  NOTE  Percentile arguments
"33.33rd and 66.67th percentiles" vs 100/3 and 200/3: pin one ("q = 33.33 and 66.67 exactly,
`np.percentile(ranges, q, method='linear')`").

### H-8  NOTE  Define a bar's CT clock time
"the bar whose CT clock time is 08:30": pin "the America/Chicago wall-clock minute of the
bar's ts_event (its open); 'the 08:30 bar' has ts_event at 08:30:00 CT".

### H-9  NOTE  Name the literal sources of OR = 30 and the 09:00..14:29 entry window
Quoted: "Sources: Crabel ... no parameter is taken from any result seen in this program."
OR = 30 minutes is B-H3's declared OR30 and the RT1..RT4 "first six five-minute bars"; say
so, so a reader does not suspect it was read off B-H1's hold-5/hold-75 results.

---

## 4. Holdout-2 leakage (L)

### L-1  SHOULD-FIX  "Before any read" is not literally true, the pull order exposes holdout-2 first, and the puller's guards cover only holdout-1
Quoted (list 1.2): "sealed on arrival, before any read" and "Sealing happens in the same
D.1f task as the download, immediately after the round-trip verification of each chunk,
and before any parquet is built from any new chunk."
Facts: `data.adapter.fetch_range` (lines 127-151) chmods the file read-only and then calls
`delivered_record_bytes`, which decodes the whole chunk (`DBNStore.from_file(path).to_ndarray(...)`)
to compare record bytes with the quote: every downloaded chunk, including the 13 holdout-2
chunks, is decoded in memory once. `data.pull_mes` pulls `reversed(monthly_chunks(...))`,
newest first, so the 13 holdout-2 chunks arrive FIRST and would sit in plaintext during the
other 58 downloads unless sealing is per chunk. `request_touches_sealed_window` blocks
only holdout-1's UTC window and `is_sealed_raw` reads only DEFAULT_PATHS' manifest, so
nothing stops a later re-buy of a holdout-2 chunk, and nothing forces the D.1f puller to
buy them at all.
Fix: "The adapter's record-byte verification is the only decode of a holdout-2 chunk and
computes nothing but a byte count. Each holdout-2 chunk is sealed by the same function
call that downloads it, before the next chunk is requested; the pull order for D.1f is
oldest-first. The holdout-2 manifest records per chunk only bytes and sha256 (plaintext and
sealed), no row counts, no dates. The puller refuses to re-buy any chunk listed in either
manifest."

### L-2  SHOULD-FIX  seal_holdout and verify_seal cannot seal holdout-2 as written; state the invariants the new code must meet
Quoted (list 5.2): "data/holdout.py: seal_holdout and verify_seal parametrized by
HoldoutPaths and by the holdout's date bounds; the existing manifest untouched; tests on
synthetic data."
Facts: `seal_holdout` raises if `paths.manifest.exists()`, splits by `HOLDOUT_START` (>=),
raises "no holdout rows found; refusing to write an empty seal" when the holdout parquet is
empty (holdout-2 is never built into bars, so it is), and `raw_files_overlapping_holdout`
and `verify_seal["research_has_no_holdout_rows"]` are HOLDOUT_START-based. The D.1f version
is therefore new logic, not a parametrization, and the list gives it no acceptance
criteria.
Fix: "The holdout-2 seal must satisfy, and its tests must assert: (i) after sealing, no
plaintext of any of the 13 chunks exists under the repo, in /tmp, or in the vendor client's
cache; (ii) the manifest lists 13 raw records with sha256_plaintext and sha256_sealed;
(iii) verify_seal(holdout-2 paths) reports all_ok with plaintext_absent for all 13; (iv) the
confirmation loader asserts max(trade_date) <= 2024-02-29 and refuses trade dates in
2024-03-01..2025-03-31 and >= 2025-04-01 on the confirmation path; (v) `python -m
data.holdout status` reports both holdouts at the start and end of every later session."

### L-3  SHOULD-FIX  The shared unlock log and the stage regex; say holdout-2 is unreadable before D.2
Quoted (list 1.2): "the same append-only docs/HOLDOUT_UNLOCK_LOG.md, the same
REGISTRATION.md requirement, the same acknowledgement phrase with "holdout 2" named in the
stage argument".
Facts: `prior_unlocks()` counts every "## ... UNLOCK ..." heading regardless of holdout, so
one holdout's unlock changes the other's `prior_unlocks_acknowledged`; the ceremony's regex
`r"\s*(stage\s+)?d\.2\s*"` rejects "Stage D.2 holdout 2", so the parametrization must
loosen it, and the list does not say how far.
Fix: "Unlock headings name the holdout ('UNLOCK holdout 2 bars'); prior_unlocks counts per
holdout; the stage argument must match `(stage\s+)?d\.2(\s+holdout\s+2)?` exactly. Holdout-2
is unreadable in D.1f and D.1g: any unlock of either holdout before a registered Stage D.2
voids this list."

### L-4  NOTE  No embargo between holdout-2 and the mined window
Quoted (list 1.2 a): "adjacency: it is the year immediately before the mined research
window". Holdout-2 ends 2025-03-31; the mined window starts 2025-04-01 (its first session's
first two hours are in the sealed chunk). The March 2024 embargo separates holdout-2 from
the confirmation window only. State why none is needed on the mined side (intraday-only
members, no trailing state across the boundary, no shared bars) or end holdout-2 at
2025-02-28 with March 2025 embargoed.

### L-5  NOTE  259 vs 239
List 1.2 "about 259 CME trade dates"; list 4 and power.md "about 239 trade dates". Both
called trade dates; the first is before roll-blackout and degraded exclusions, the second
after. Label both.

### L-6  NOTE  Embargo phrasing
"the March 2024 trade dates (2024-03-01 through 2024-03-28)": say "every March 2024 trade
date" so a 2024-03-29 session, if the calendar shows one, is covered.

---

## 5. Multiplicity (M)

### M-1  SHOULD-FIX  DSR, t and PBO are named but not specified for the confirmation window
Quoted (list 3.2 iii): "DSR at N = 58 must exceed 0.95, the daily t-statistic must exceed
3.0 (Harvey-Liu-Zhu), and the CSCV PBO over the 58 must be below 0.5."
Facts: `_d1b_accounting` computes Sharpe variance as `pvariance` of daily Sharpes ACROSS a
label set, moments with `pstdev`, PBO on `N_PBO_BLOCKS = 8` blocks of `len // 8` days. The
list fixes none of: which daily series (confirmation-window d_t of the 58 Tier A members),
the label set for the Sharpe variance, the observation count, the block count for a
~1,150-day window (8 blocks of ~144 days vs the 36-day blocks D.1b used), or whether the
D.1b/D.1d sensitivities (N widened by the Tier B and EDA statistics) are reported.
Exploit: choose the block count or the variance set after seeing which one clears 0.5.
Fix: "DSR: `funnel.multiple_comparisons.deflated_sharpe_ratio(sharpe_m, n_days, 58,
pvariance of the 58 Tier A confirmation-window daily Sharpes, skew_m, kurt_m)` with moments
from `_d1b_accounting._moments` on d_t; t: `harvey_liu_zhu_verdict(mean, pstdev, n_days)`
one-sided; PBO: `probability_of_backtest_overfitting` on 8 contiguous equal blocks of
`n_days // 8` days over the 58 Tier A daily series. Reported alongside, not criteria: the
same three at N = 101 (58 plus the 43 Tier B members) and at N = 186 (plus the 85 EDA
statistics), as the D.1b and D.1d entries did."

### M-2  SHOULD-FIX  The Tier B anomaly clause is two-sided and names the wrong future data
Quoted (list 2.2): "A Tier B statistic that comes out BH-significant at 10% within Tier B
with |net edge| >= 2.11 ticks is reported as an anomaly for a future declared test on data
neither window has used; it is not a D.1f finding."
Exploit: s is fixed from the mined sign, but |net edge| lets a significant NEGATIVE value
(the opposite trade) count as an anomaly, a post-hoc sign flip. "Data neither window has
used" includes both sealed holdouts, which exist for the pre-registered D.2 bar, not for
testing an anomaly selected from 43.
Fix: "an anomaly only if BH-significant (one-sided, in direction s) at 10% within Tier B and
net edge >= +2.11 ticks per event in direction s; a significant negative value is reported
as 'sign reversal versus the mined window', not as an anomaly. Any future test of an anomaly
runs on forward data (Stage E) or a new purchase outside both holdouts, the confirmation
window and the mined window, under a new declaration, and adds to N."

### M-3  SHOULD-FIX  D.1g's N, its in-sample dates and "before 2024-02-29"
Quoted (list 3.5): "the N_C6 trade dates are the LAST N_C6 confirmation-window dates before
2024-02-29" and "D.1g's decision rules: 3.1 to 3.4 verbatim, with C-H4 as the single Tier A
member of C6 and Holm family m = 1."
Facts: those dates are inside the confirmation window D.1f has already run C-H4 on
(trade-through model), so D.1g's edge test is new only in fill model, not in dates. A
queue-model C-H4 is arguably a new trial (new execution hypothesis); the list does not say
whether N becomes 59 for D.1g's DSR. "before 2024-02-29" excludes the window's last date;
the window is "through 2024-02-29 inclusive".
Fix: "on or before 2024-02-29"; "D.1g's DSR uses N = 59 (the queue-model C-H4 is a new
trial) [or: N = 58, C-H4 re-measured; lead decides]"; "D.1g's dates were already read by
D.1f's trade-through run of the same signal; the D.1g result is out-of-sample only in the
fill model, and any C6 edge claim says so."

### M-4  NOTE  Regime slices can seed nothing inside this program's data
Quoted (list 3.6): "No slice is chosen, dropped, weighted or used in any verdict." Add:
"anything learned from a slice can seed only a new declaration under a new name, counted
in N, tested on data outside the confirmation window, the mined window and both holdouts."

---

## 6. Inconclusive and null rules (N)

### N-1  BLOCKER  E-H1 and E-H2 cannot fire on the confirmation window: their release table covers 2025-04-01..2026-06-12 only
Quoted (list 2.1 A1 table): "| E-H1 scheduled macro drift | C5 |", "| E-H2 post-release
momentum | C5 |".
Quoted (list 3.4): "A class with zero members on the confirmation window (for example an H
test whose condition never fires in the window) is inconclusive, not null."
Quoted (code, hashed module h1_scheduled_macro_drift.py docstring): "Calendar table
(hardcoded, sourced; covers the RESEARCH_START..RESEARCH_END window 2025-04-01..2026-06-12";
h2_post_release_momentum.py: "from strategy.research.e_calendar_event.h1_scheduled_macro_drift
import RELEASE_TABLE_ET" and "Same calendar table as H1".
Facts: on trade dates 2019..2024 the table has no entry, so E-H1 and E-H2 place no trade;
by 3.4 both are inconclusive, so C5 can never reach a null verdict in D.1f as the list
stands, and the C5 row of the power table (binding member E-H1, n_b = 4) describes a run
that cannot happen. Extending the table means editing a hashed module (INVALID by section
0) and adding data the list does not provide for; leaving it means C5 is inconclusive by
construction while section 7 still lists C5 among the classes D.1f may pronounce on.
Exploit: D.1f "extends the table as an obvious oversight" from whatever source is handy,
after the other 29 trials' results are in; or picks which releases count (regular FOMC
only? the 2020-03-03 and 2020-03-15 emergency actions? shutdown-delayed BLS releases?)
with the P&L in view.
Fix (lead decides): (a) "Before the purchase, D.1f writes
strategy/research/e_calendar_event/_release_table_2019_2024.py: scheduled FOMC statement
dates and 2:00pm ET times from federalreserve.gov/monetarypolicy/fomccalendars.htm
(historical pages), and CPI and Employment Situation release dates and 8:30am ET times from
bls.gov/schedule archives, for 2019-05-01..2024-02-29, using the actually-published date
where a release moved, excluding unscheduled FOMC actions (the module's own 'regularly
scheduled' convention), each entry citing its source; E-H1 and E-H2 read RELEASE_TABLE_ET
extended by that module through an import shim that leaves the two hashed modules
unedited [or: the two modules are edited and re-hashed in an amendment before purchase].
The new module's sha256 goes into the harness freeze (R-4) before any quote." Or (b) "C5's
null is not attainable in D.1f; E-H1 and E-H2 are inconclusive by construction; section 7's
summary excludes C5." Either way, re-issue the C5 power row.

### N-2  SHOULD-FIX  The zero case divides by zero and the wording says "class"
Quoted (list 3.3): "achieved null power = Phi(epsilon_day / SE_boot - 1.645)"; (list 3.4)
"A class with zero members on the confirmation window ... is inconclusive, not null."
Facts: a member with no trades has d_t = 0 everywhere, SE_boot = 0, UCB95 = 0 < epsilon and
Phi(inf) = 1: the formula says "null with power 1". The sentence that saves it says "class
with zero members", which is not what it means.
Fix: "A member with zero closed round trips or zero events on the confirmation window, or
with SE_boot = 0, is inconclusive (no evidence), not null; its class is out of the null
verdict." Cross-reference E-2 for a minimum-activity threshold above zero.

### N-3  SHOULD-FIX  "masked" versus "excluded" for vendor-degraded days, and the degraded set is not stable
Quoted (list 1.3): "vendor-degraded days masked from strategies and excluded from event
statistics as Families F and G did".
Facts: in the current pipeline the strategies TRADE through degraded days (the flag is a
hindsight field blanked by `mask_hindsight_fields=True`; the day's P&L counts in
daily_net_usd), while the F/G date set drops any trade date with any flagged bar
(including the Monday after a degraded Sunday: 2021-12-05 and 2022-01-02 are Sundays).
Databento's condition entries for the 2020-2024 dates carry "last modified" stamps of
2026-08-23..2026-09-01, so a later `get_dataset_condition` call can return a different set.
Exploit: drop degraded days from a trial's daily series ("masked" read as "excluded"), or
re-query the condition endpoint until a convenient set appears.
Fix: "Trials trade through vendor-degraded days; the flag is hidden from the strategy and
the day's P&L counts. Event statistics exclude every trade date with any flagged bar. The
two differ by design and stay so. The degraded-date list is fetched once at step 2, frozen
in the run JSON, and compared with the eight dates known at declaration (2020-02-27,
2020-02-28, 2020-05-05, 2020-06-30, 2020-07-01, 2021-12-05, 2022-01-02, 2024-09-18); any
difference is logged before step 5."

### N-4  NOTE  The two daily series have different denominators
For trials, d_t runs over every window date including roll-blackout dates ($0); for
statistics, over the post-exclusion date set. State it beside 3.1 so nobody "harmonises"
after the run.

### N-5  NOTE  Normal-approximation power beside a percentile UCB
3.3's power uses SE_boot and the normal quantile; UCB95 is a percentile. For a heavy-tailed
member they disagree; both are pinned, so only note it: "the two constructions are used as
written and are not reconciled after the run".

---

## 7. C6 (C)

### C-1  BLOCKER  C-H4 trades every session; "MBO for N_C6 RTH days" cannot simulate its fills
Quoted (list 3.5): "D.1g's data: MBO for N_C6 RTH days chosen by a rule declared here".
Quoted (NULL 1.1): "on the N_C6 pre-declared confirmation dates".
Facts: `H4PassiveFillReversal.on_bar` has no clock gate; it resets per trade date and
places resting orders whenever its magnitude condition fires, ETH included (92.5 trips per
day is a 23-hour figure). RTH-only MBO leaves every ETH resting order without a fill model.
Exploit: D.1g either (i) restricts C-H4 to RTH, a re-parametrization of a frozen member,
(ii) keeps trade-through fills for ETH and queue fills for RTH, a mixed model the C6
statement does not describe, or (iii) buys full days without the list saying so. Any of
the three is chosen after D.1f's C-H4 result is known.
Fix (lead decides): "D.1g buys full-session MBO (17:00 CT to 16:00 CT) for the N_C6 trade
dates (quotes.md: $1.00 per full day against $0.78 RTH-only), and simulates every resting
order of C-H4 as coded." Or: "D.1g evaluates a declared RTH-only variant, C-H4-RTH, whose
module is written and hashed now, counted as a new trial (N + 1), with the original C-H4's
D.1f trade-through result reported beside it." Also carry R-1 here: C-H4 is a 1-micro
member, so N_C6 must be recomputed at the correct unit (roughly 180 days), and the D.1g
budget line with it.

### C-2  SHOULD-FIX  The D.1g fill model's declaration must precede the MBO download and must not be fitted on the evaluation days
Quoted (NULL 1.1): "filled by the queue-position fill model declared and hashed in Stage
D.1g from MBO data"; (list 3.5) "declared and hashed in D.1g before any P&L is computed".
Exploit: "from MBO data" reads as "calibrated on the MBO data", and "before any P&L" allows
inspecting the 46 days' books first. A queue model tuned on the evaluation days is
in-sample.
Fix: "The queue-position fill model is specified and hashed BEFORE the MBO purchase. Any
parameter it needs from book data is estimated on days outside the N_C6 evaluation dates
(declared in advance), never on them."

---

## 8. Data-quality rules (D)

### D-1  SHOULD-FIX  The start rule needs four pins to be objective
Quoted (NULL 4.1): "the median over that month's RTH one-minute bars (CT clock time 08:30 to
14:59, every research trade date in the month) of the bar's volume"; "For each calendar
month M of the extension from MES's first full month through 2024-02"; "S = the first trade
date of the earliest month M* such that V_M >= 0.25 x V_ref for M* and for every later
month through 2024-02."
Exploits: (a) a clock minute with no trade has no bar; early MES had many; the median over
bars present differs from the median over 390 clock minutes with zeros, and the two can
straddle 0.25 x V_ref for a marginal month; (b) "every research trade date in the month"
does not say whether roll-blackout and vendor-degraded dates are in the V_ref and V_M
samples; (c) "MES's first full month" is ambiguous for May 2019 (trading began 2019-05-06),
which decides whether S can be 2019-05-06 at all (the power table lists it as a candidate);
(d) a later reader can apply 4.1 to a parquet built before the 2024-02-29 drop.
Fix: "V_ref and V_M are medians over the RTH bars PRESENT in the parquet (a clock minute with
no bar contributes nothing), over ALL trade dates of the month with no exclusion of
roll-blackout or vendor-degraded dates, computed on the confirmation parquet after step 4's
drop and on the research parquet as it is. The extension's first month is 2019-05; if M* =
2019-05, S = 2019-05-06, the first trade date with bars."

### D-2  BLOCKER  The 2019-2024 calendar has no completeness check and no freeze point, and the code fails silently without it
Quoted (list 5.3): "data/cme_calendar.py: holidays and early closes for 2019 through 2024
from CME's published schedules, each entry citing its source verbatim; the flatten-time
logic unchanged."
Facts: `data.session.early_halt_ct(day)` returns None for any date absent from HOLIDAYS; no
error. `CALENDAR_COVERAGE = (2025-01-01, 2026-12-31)` is defined and enforced nowhere.
`sim.engine._is_trade_date` treats an unlisted full closure as a session, shifting the
roll blackout's "two prior sessions" by a day. On an unlisted early-close day the bars end
at 12:00 CT with `early_halt_ct` None: strategies hold into the halt (the engine then closes
"at the last bar's close" with a forced-flatten event), the XFA "flatten 15 minutes before
an early close" rule never triggers, and H's completeness test wrongly marks the day
complete. The list schedules the calendar before the purchase (good) but validates nothing
against the bars it will govern, and nothing in either document freezes it.
Exploit: after step 7 shows a marginal member, "correct" an early-close time or add a
missed holiday; results change on those days; continuity (2025-26) still passes; section
5.6 still passes.
Fix: (i) "The bar builder asserts every built date lies inside CALENDAR_COVERAGE, extended
to 2019-01-01." (ii) Add step 4b to 1.5: "run `data.validate.observe_holidays` over the
confirmation bars and require: every weekday with no bars is a listed FULL_CLOSURE; every
day whose last RTH bar opens before 14:59 CT is a listed EARLY_HALT whose halt_ct equals the
observed last minute plus one; every listed 2019-2024 entry is observed. Any discrepancy
stops the run; the calendar is corrected, re-hashed into the harness freeze, and the
correction logged, all before step 5. After step 7 starts the calendar is immutable." (iii)
"The 2025-2026 entries are byte-identical to the file hashed at declaration
(5f24edda9504ca7e091c980969d743c05ba0472d8bd613473611d2335971cd54)."

### D-3  NOTE  Cost-bias section: add the two mechanical facts
NULL 4.3 states the early-era bias both ways (correct). Add R-8 (size-5 bucket for 2 micros)
and E-3 (statistics ignore time of day).

### D-4  NOTE  A symbology oddity in the first instrument
quotes.md: instrument 7849 (2019-04-01..2019-06-17) maps to raw symbols ['DNMH929 C35',
'MESM9']. Fix now the rule for a bar whose raw_symbol is not an MES outright inside the
continuous series (drop and log), so it is not decided when the June 2019 roll is in view.

### D-5  NOTE  "2020 included" is true for trials, not fully for statistics
The vendor flag removes 2020-02-27 and 2020-02-28 (the COVID onset) and three more 2020
dates from every statistic's date set. Say so beside 3.6/4.4 so the "no regime exclusion"
claim is precise.

---

## 9. Provenance (V)

### V-1  SHOULD-FIX  The hashing procedure is circular, and chmod is a weak anchor
Quoted (list 6): "[WRITTEN AT HASHING: sha256 of this file and of docs/NULL_CRITERIA.md, the
UTC time, and the chmod to read-only.]"; (NULL 1) "reports/stage_d1f_confirmation_list.md,
sha256 [FILLED AT HASHING]."
Facts: a file cannot contain its own sha256. NULL_CRITERIA embeds the list's hash and the
list wants NULL_CRITERIA's hash: circular. reports/stage_d1b_family_f_declaration.md, which
progress.md describes as hashed and read-only, is `-rw-rw-r--` today (its hash still
matches; D.1d's is `-r--r--r--`).
Exploit: an ill-defined procedure lets a later session "re-hash" a modified list and call
it compliant.
Fix: "Order: (1) the list's section 6 records only the UTC time and the chmod; the list is
hashed first. (2) NULL_CRITERIA section 1 embeds the list's hash; NULL_CRITERIA is hashed
second. (3) Both hashes are written to reports/stage_d1e_declaration_hashes.json (which
_d1f_confirmation.py checks) and to progress.md. (4) The lead asks the user for a commit
of the three files; the commit hash is the anchor, chmod is a convenience."

### V-2  SHOULD-FIX  Provenance table of load-bearing files not in section 0
Beyond R-2 and R-4: strategy/research/_d1e_event_series.py 51ec1d881cfdd9385f421809c2cdcfa9f8233d18ac5dcddbd92e84c3f8e90645;
reports/stage_d1e_power.json c1f2d8334e708f72639110efd5a127459552215d829c97b78b4ae1d702347c83;
reports/stage_d1e_coverage.md a4b31316486198c8011ef32a4d37becd90555729a6ce2b090be6887d8373d013;
reports/stage_d1e_members_trials.json bc6649da293edb0b63e025d610437ffa89c81a66049139b01ea1cb8507e802a7;
reports/stage_d1e_members_events.json c6db647fe818faec0f70772a9b241c78f0865999ee83c6d4b9d4a19317bc2df8;
reports/power_gate.json e57088247881c184a411344d6b1b696a782987eb92ef3a4328e6b6f39315c40c;
sim/slippage_calibration.json 2d680dd2e2d09895cd28d81f258c525092f503688cc6801f28ca0171abbe30b5.
The power JSON already records the coverage/members/quotes hashes in its meta; the list
should cite the power JSON's own hash so section 4's numbers are traceable.

### V-3  NOTE  "plus this stage's additive changes" is not a state
screening/runner.py is modified and uncommitted. R-4's freeze covers it; until then the
phrase pins nothing.

### V-4  NOTE  reports/stage_d1e_power_gate_cells.json is cited (NULL 2.2) and not pinned
Pin or drop (E-1).

### V-5  NOTE  N_C6 is a rule plus a filled value
"N_C6 = the days C-H4 needs for 80% null power at epsilon per Task 3 (46 days ...)": the
rule survives R-1; the value does not. After the unit fix, re-fill and re-verify.

---

## 10. Wording (W)

### W-1  SHOULD-FIX  The all-classes sentence overreaches in tense and scope
Quoted (NULL 7): ""no strategy class the program has tested on MES with market orders at 2
micros has an edge large enough to fund the Topstep funnel, on the pre-registered window,
at the stated power""
Fix: ""on trade dates S to 2024-02-29, no member of any class the program tested on MES
(market-order trials at their coded size, event statistics at the flat modelled round
turn, Family H at 2 micros) showed a net edge of at least epsilon_day = 34 net ticks per
micro per day, the smallest edge that funds the Topstep XFA funnel under the Stage B model
of the 2026 rules and fee schedule at 2 micros; every member's one-sided 95% upper bound
was below epsilon at >= 80% achieved null power; per class, the per-trade resolution was
[table]"." The present tense "has an edge" and the unscoped "the Topstep funnel" go.

### W-2  NOTE  Section 1 states a fact where the test supports an inference
"no member of the class has a net edge of at least epsilon" -> "for every member of the
class, a net edge of at least epsilon is rejected at one-sided 95% (UCB95 < epsilon), with
achieved null power of at least 80%".

### W-3  NOTE  "executed with market orders" does not describe the statistics
Section 1's template covers classes whose members include event statistics that are not
executed at all. Add: "trials executed through the engine with market orders; event
statistics charged the flat modelled round turn of 2.11 ticks per event".

### W-4  NOTE  "Fifty-four of the 95 measured members" (NULL 5) is a half-scale count for trials
After R-1 the per-trade resolution of every trial doubles; recompute the sentence.

---

## 11. Checked and found sound (no finding)
- All 31 section-0 hashes match disk; the D.1b and D.1d declarations' hashes match.
- The 21 Tier A statistics equal the logged D.1b (14) and D.1d (7) near-miss lists, member
  for member; s equals the sign of each recorded edge.
- Holdout-2 bounds, the whole-chunk embargo month, the 2024-02-29 22:00-24:00 UTC drop and
  the 2025-03-31 22:00-24:00 UTC bars staying sealed are fixed independently of any result.
- The start rule reads only unsealed months (V_M through 2024-02 uses RTH bars; the
  2024-03-01 session's first hour in the February chunk is ETH) and the research parquet.
- epsilon = 34 holds on the pinned files (E-1 is about the description, not the value).
- The roll blackout (splice plus two prior sessions) matches `canonical_engine_config`; the
  drift charge for statistics is the exposure-matched form drift.py uses for trips.
- The H look-ahead tests (scaled-copy invariance, fill-after-decision, hand-built series)
  are well designed; the engine's fill-at-next-open contract and the canaries cover timing.
- REGISTRATION.md is not written by D.1f; the DSR/t/PBO thresholds are the program's
  standing ones; "descriptive only" is attached to every slice and sensitivity.
- No choice of epsilon, holdout bounds or start rule depends on how D.1f might come out
  (the 0.25 fraction is a judgment made now and says so).

## 12. Summary table

| ID | Severity | Where | One line |
|---|---|---|---|
| R-1 | BLOCKER | list 3.1, A1 | d_t = daily_net_usd/2.5 assumes 2 micros; all 31 trials and C-H4 are coded at 1 micro; trial nulls tested at 68 ticks/micro/day, power rows off ~4x, N_C6 off ~4x |
| R-2 | BLOCKER | list 0, 1.4 | Trial parameters (direction, session, hold_minutes) live in unhashed _lead_accounting.py; ALL_TRIALS and the continuity JSON unhashed |
| R-3 | BLOCKER | list 0, 5.1, 5.4 | 5.4 edits two hashed modules (INVALID by 0); runner path raises on 2019-2024 via null_generator; pull/build/calendar/release table not enumerated |
| R-4 | BLOCKER | list 5.6, 1.5 | No harness freeze at run time; continuity covers only the train-union path |
| N-1 | BLOCKER | list A1, 3.4; NULL 7 | E-H1/E-H2 release table covers 2025-04..2026-06 only: zero trades on the window, C5 unresolvable or extended post hoc |
| C-1 | BLOCKER | list 3.5; NULL 1.1 | C-H4 trades all sessions; RTH-only MBO cannot fill its ETH orders |
| D-2 | BLOCKER | list 5.3; NULL 4.2 | 2019-2024 calendar unvalidated and unfrozen; missing entries fail silently and shift blackout, flatten, H completeness |
| R-5 | SHOULD-FIX | list A2 | e defined in unhashed _d1e_event_series.py; F4.4 control-subtraction description inverted |
| R-6 | SHOULD-FIX | list A2 | Sample-derived thresholds (terciles, Q80, regression, baselines) called "literals" |
| R-7 | SHOULD-FIX | list 1.5, 5.5 | H1-H6 may be run on the mined bars before the confirmation |
| E-1 | SHOULD-FIX | NULL 2.2 | Epsilon text describes a 96-row file; pinned file has 100 rows with finished T=32; "passing" undefined; recomputation not forbidden; power_gate.json unpinned |
| E-2 | SHOULD-FIX | NULL 2.4, 7 | Null by inactivity (E-H3: 4 trades); per-trade resolution not mandatory in the statement; minimum activity undecided |
| H-1 | SHOULD-FIX | list A3 | Instrument guard does not cover H3 on splice+1 though the text claims it |
| H-2 | SHOULD-FIX | list A3 | H4/H5 need 61 complete bars; lookback says 60 |
| H-3 | SHOULD-FIX | list A3 | Exit bar 14:58 may not exist |
| H-4 | SHOULD-FIX | list A3 | State the production factories take no arguments |
| H-5 | SHOULD-FIX | list 4 | C7 projections inherit the half-scale proxies |
| L-1 | SHOULD-FIX | list 1.2 | Adapter decodes every chunk; newest-first pull exposes holdout-2 first; puller guards cover holdout-1 only |
| L-2 | SHOULD-FIX | list 5.2 | seal_holdout/verify_seal cannot seal holdout-2 as written; no acceptance invariants |
| L-3 | SHOULD-FIX | list 1.2 | Shared unlock log counts across holdouts; stage regex rejects "holdout 2"; unreadability before D.2 not stated |
| M-1 | SHOULD-FIX | list 3.2 iii | DSR variance set, PBO block count, t construction, sensitivities unspecified |
| M-2 | SHOULD-FIX | list 2.2 | Tier B anomaly clause is two-sided (sign flip) and points at "data neither window has used" (includes the holdouts) |
| M-3 | SHOULD-FIX | list 3.5 | D.1g's N unstated; dates already read by D.1f; "before" vs "on or before" |
| N-2 | SHOULD-FIX | list 3.3, 3.4 | SE_boot = 0 divides by zero; "class with zero members" wording |
| N-3 | SHOULD-FIX | list 1.3 | "masked" vs "excluded" for degraded days; degraded set mutable at the vendor |
| C-2 | SHOULD-FIX | NULL 1.1; list 3.5 | Fill model declared "from MBO data": must precede download, not be fitted on evaluation days |
| D-1 | SHOULD-FIX | NULL 4.1 | Start rule: bars-present vs clock minutes; exclusions; "first full month"; parquet version |
| V-1 | SHOULD-FIX | list 6; NULL 1 | Self-referential/circular hashing; chmod weak; ask for a commit |
| V-2 | SHOULD-FIX | list 0 | Provenance table of unhashed load-bearing files |
| W-1 | SHOULD-FIX | NULL 7 | All-classes sentence: present tense, unscoped funnel model |
| R-8 | NOTE | A3; NULL 4.3 | 2 micros costed at the size-5 bucket |
| R-9 | NOTE | list 3.1 | Bootstrap function, per-member RNG, quantile method, p = (k+1)/(B+1) |
| R-10 | NOTE | list 3.2 ii | Gate call for statistics: define p, R, T |
| E-3 | NOTE | list A2 | Cost sentence framed per trade; "overstates" points the wrong way for a null |
| E-4 | NOTE | NULL 2.3 | "Typical trades per day" is trials only |
| E-5 | NOTE | list 3.1 | Define r for trials and statistics |
| H-6 | NOTE | list A3 | "strict inequalities" contradicts H4-H6 |
| H-7 | NOTE | list A3 | Percentile q literal |
| H-8 | NOTE | list A3 | Define CT clock time of a bar |
| H-9 | NOTE | list A3 | Name the literal source of OR = 30 |
| L-4 | NOTE | list 1.2 | No embargo between holdout-2 and the mined window |
| L-5 | NOTE | list 1.2, 4 | 259 vs 239 trade dates |
| L-6 | NOTE | list 1.2 | Embargo phrasing |
| M-4 | NOTE | list 3.6 | Slices can seed only new declarations outside this program's data |
| N-4 | NOTE | list 3.1 | Trial and statistic daily series have different denominators |
| N-5 | NOTE | list 3.3 | Normal-approximation power beside percentile UCB |
| D-3 | NOTE | NULL 4.3 | Add the two mechanical cost facts |
| D-4 | NOTE | list 1.1 | Instrument 7849 raw-symbol oddity: fix the drop rule now |
| D-5 | NOTE | list 3.6; NULL 4.4 | "2020 included" is partial for statistics |
| V-3 | NOTE | list 0 | "additive changes" pins nothing; runner.py uncommitted |
| V-4 | NOTE | NULL 2.2 | power_gate_cells.json cited, unpinned |
| V-5 | NOTE | list 3.5 | N_C6 value must follow R-1 |
| W-2 | NOTE | NULL 1 | State the null as an inference |
| W-3 | NOTE | NULL 1 | "executed with market orders" vs statistics |
| W-4 | NOTE | NULL 5 | "Fifty-four of 95" is a half-scale count |

Counts: 7 BLOCKER, 23 SHOULD-FIX, 25 NOTE (55 findings).

## 13. Verdict

NOT READY. Seven blockers, in the order the lead should take them:
1. R-1 (unit): a definition error that makes every trial's null twice as easy as the
   economics the whole document rests on, and that propagates into the filled power and
   N_C6 numbers. Fix the definition, re-issue section 4 / NULL_CRITERIA 5 and N_C6, and
   re-verify before hashing.
2. N-1 (E-H1/E-H2 release table) and C-1 (C-H4 sessions vs RTH-only MBO): two members whose
   frozen code cannot run as the list assumes; both need a lead decision written into the
   list now.
3. R-2, R-3, R-4 (pinning): the parameters, the assembly tuple, the continuity target, the
   event-value definition and the entire harness are outside the hash perimeter, and 5.4
   contradicts section 0. Add the hashes, enumerate the changeable files, add the freeze
   step.
4. D-2 (calendar): the one harness component the list deliberately leaves to be written
   later has no completeness check and no freeze point, and the code fails silently
   without it.

The stage prompt's own requirements are otherwise met in form: epsilon, holdout bounds and
the start rule do not depend on D.1f's outcome; the 31 trials and 21 near-misses are the
logged ones; Family H has six fully specified tests with look-ahead checks; C6's criteria
are inherited; the inconclusive rule rounds nothing to null. After the blockers and
should-fixes above are adjudicated in writing, the documents are ready to hash under the
V-1 procedure.

## 14. What this review did not do
- Did not execute any strategy, the runner, or the bootstrap; every code fact is from
  reading the files named above.
- Did not verify the power table's arithmetic (out of scope; R-1 is a definition finding
  whose numerical consequence is stated by direction and rough factor only).
- Did not check the 2019-2024 CME calendar or the 2019-2024 release dates against any
  external source (no network).
- Did not read any holdout byte or any extended-history bar; none exists in the repo.
- Did not test whether `session_benchmark` is reachable on a confirmation window other
  than by reading `screen_frame` (line 309 calls it unconditionally) and
  `build_segment_table` (line 102 calls `_refuse_non_research`).

---

## 15. Re-review after amendments (2026-09-22, same reviewer, after reports/stage_d1e_adjudication.md)

Re-read in full: reports/stage_d1f_confirmation_list.md (606 lines) and docs/NULL_CRITERIA.md
(274 lines), both amended and refilled. Mechanical checks repeated on the amended state:
- Every hash now in section 0 recomputed: all 31 original entries, the 7 R-2 entries, the
  R-5 entry, the 5 epsilon/cost entries (power_gate.json e5708824..., gate_extension.json
  d569e261..., power_gate_cells.json 433a3ea6..., slippage_calibration.json 2d680dd2...,
  cme_calendar.py 5f24edda...) and the 5 V-2 artifacts (members_trials.json f546e3f3...,
  power.json 29b0e03e..., coverage.md 63e18451..., members_events.json c6db647f...,
  quotes.json a796ef73...) match disk. Commit f1bb073 exists (HEAD).
- epsilon re-derived on the NEWLY pinned files (the extension hash changed from 583cca... to
  d569e261... after my first pass): 100 extension rows, 66 pass / 30 fail / 4 marginal,
  smallest passing extension cell $92.018; grid (power_gate_cells.json) 120 cells, 37 pass,
  smallest passing $87.481 -> 34. NULL 2.2's "220 cells", "66 pass, 30 fail, 4 marginal" and
  "one T = 32 cell passes, at $188.50" are exact on the pinned files.
- The new A1 factory column checked against strategy/research/_lead_accounting.py TRIALS and
  g_timeframe/retests.py RETESTS: all 31 expressions verbatim (RT1-RT4 lambdas, RT5
  SpikeFadeRetest, RT6 DailyVolRegimeGateRetest, RT7 DailyVolSizingRetest, C-H4
  H4PassiveFillReversal).
- Refilled numbers read against reports/stage_d1e_power.json (29b0e03e...): C1 149/161/149 and
  n_a 379 (A-H4 rth leg, sd_day 223.99), C5 16/10/16 and 41 (E-H1, sd_day 50.29), C6
  181/174/181 and 461 (C-H4, sd_day 190.54), C7 114 and 290 (H6, sd_day 145.46, proxies
  200/230): the list's section 4 and the criteria's section 5 agree with the JSON. "47 of the
  95 measured members" resolvable below 2.11 ticks per trade at S = 2019-05-06 reproduces (47).
  reports/stage_d1e_power_verification.md carries an appended section 11 re-verifying the
  per-micro series, N_C6 = 181, the class tables and the 47-of-95 count, so section 4's
  "verified in" reference is no longer stale.
- No network, no data read, no holdout byte; nothing written except this section.

### 15.1 Status of the 55 findings

| ID | Status | Where amended, and what remains |
|---|---|---|
| R-1 | PARTLY | list 3.1, A1, criteria 1, 4.3, 5; coverage map section 6; power table re-issued and re-verified (verification section 11). REMAINS: criteria 1.1, the C6 statement template, still says "sized at 2 micros" for C-H4, which is coded at 1 micro (list 3.5: "C-H4 at its coded 1 micro"); it must say "at its coded 1 micro, compared per micro with the 2-micro bar as in section 1". |
| R-2 | RESOLVED | list 0 (seven hashes, all match disk), A1 factory column (verbatim, checked). |
| R-3 | RESOLVED | list 5.4 (wrapper, hashed modules untouched), 5.1 (null_generator refusal, own splices/drift/benchmark), 5.8 (enumerated files). |
| R-4 | RESOLVED | list 1.5 step 1b, 5.6. (Wording: see NEW-4.) |
| R-5 | RESOLVED | list A2 and its F4.4 row; _d1e_event_series.py hashed. |
| R-6 | RESOLVED | list A2. |
| R-7 | RESOLVED | list 1.5 step 1 and closing sentence, 5.5. |
| R-8 | RESOLVED | list A3 parameters, criteria 4.3. |
| R-9 | RESOLVED | list 3.1 (function, per-member rng, quantile, (k+1)/(B+1)). |
| R-10 | RESOLVED | list 3.2 ii. |
| E-1 | RESOLVED | criteria 2.2 rewritten; both files pinned; epsilon confirmed on the new pins. |
| E-2 | RESOLVED | as adjudicated (ACCEPT-MOD): "null by inactivity" under 30 trips or events, mandatory per-class resolution; list 3.3, criteria 1, 6, 7. The modification is sound: the economic statement is right and the label prevents the misreading. |
| E-3 | RESOLVED | list A2 cost sentence rewritten; the wrong-direction sentence removed. |
| E-4 | RESOLVED | criteria 2.3 header. |
| E-5 | RESOLVED | list 3.1. |
| H-1 | RESOLVED | list A3 instrument guard. (Wording: see NEW-9.) |
| H-2 | RESOLVED | list A3 (61 bars; test warm-up 7). |
| H-3 | RESOLVED | list A3 exit rule. |
| H-4 | RESOLVED | list A3 parameters paragraph. |
| H-5 | RESOLVED | coverage map 5 (200/230), power table C7 re-projected (H6 n_b 114). |
| H-6 | RESOLVED | list A3. |
| H-7 | RESOLVED | list A3. |
| H-8 | RESOLVED | list A3. |
| H-9 | RESOLVED | list A3. |
| L-1 | RESOLVED | list 1.2, 1.5 steps 2-3. |
| L-2 | RESOLVED | list 5.2 (five invariants). |
| L-3 | RESOLVED | list 1.2 (headings, per-holdout count, regex, unreadable before D.2). |
| L-4 | RESOLVED | as adjudicated (ACCEPT-MOD): reason written in list 1.2 (a); the reason is correct for intraday-only members with warm-up inside each window. |
| L-5 | RESOLVED | list 1.2. |
| L-6 | RESOLVED | list 1.2. |
| M-1 | RESOLVED | list 3.2 iii (functions, variance set, blocks, sensitivities). |
| M-2 | RESOLVED | list 2.2. |
| M-3 | RESOLVED | as adjudicated (ACCEPT-MOD): list 3.5 (on or before; N = 59; in-sample-in-dates statement). (Criteria: see NEW-3.) |
| M-4 | RESOLVED | list 3.6. |
| N-1 | PARTLY | Mechanism decided and written (list 5.7, 5.8, A1 keeps C5). REMAINS: the amendment contradicts section 0's INVALID rule, 5.6's refusal and A1's factory column; as written D.1f cannot run E-H1/E-H2 without breaking one of them. See NEW-1 (blocker). |
| N-2 | RESOLVED | list 3.3, 3.4; criteria 6. |
| N-3 | PARTLY | list 1.3 and 1.5 step 2 resolved (trade-through vs exclude; condition fetched once and frozen; eight dates). REMAINS: criteria 4.2 still reads "masked from every strategy, excluded from event statistics" with no explanation; since every later stage "is judged against this document, not against a paraphrase", carry the list-1.3 sentence or an explicit cross-reference there. |
| N-4 | RESOLVED | list 3.1. |
| N-5 | RESOLVED | list 3.3. |
| C-1 | RESOLVED | list 3.5 (full trade-date MBO), criteria 1.1 (full trade dates). |
| C-2 | RESOLVED | list 3.5, criteria 1.1. |
| D-1 | RESOLVED | criteria 4.1 (bars present, no exclusions, 2019-05 / 2019-05-06, post-drop parquet). |
| D-2 | RESOLVED | list 5.3, 1.5 step 4b. |
| D-3 | RESOLVED | criteria 4.3. |
| D-4 | RESOLVED | list 1.1 drop-and-log rule. (Its interaction with the per-interval symbol mapping is new: see NEW-6.) |
| D-5 | RESOLVED | list 3.6, criteria 4.4. |
| V-1 | RESOLVED | list 6 (order, hashes file, user's commit as anchor); criteria 1 keeps its [FILLED AT HASHING] by design. |
| V-2 | RESOLVED | list 0 provenance table; all values match disk. (Wording: see NEW-7.) |
| V-3 | RESOLVED | list 0 (commit f1bb073, which exists, plus the freeze manifest). |
| V-4 | RESOLVED | criteria 2.2 and list 0 (433a3ea6... matches). |
| V-5 | RESOLVED | list 3.5 (181), consistent with section 4, criteria 5 and the JSON. |
| W-1 | RESOLVED | criteria 7. |
| W-2 | RESOLVED | criteria 1. |
| W-3 | RESOLVED | criteria 1. (One slip introduced: see NEW-8.) |
| W-4 | RESOLVED | criteria 5 (47 of 95; reproduced). |

Resolved 52, partly 3 (R-1, N-1, N-3), not resolved 0.

### 15.2 New findings introduced by the amendments

#### NEW-1  BLOCKER (to hashing)  The E-H amendment cannot be executed under section 0, 5.6 and A1 as they now stand
Quoted (list 0): "A member whose referenced file changes before D.1f runs is INVALID until this
list is re-issued under a new hash; D.1f must verify every hash before running." with the
PRE-amendment hashes of the two modules still listed (h1_scheduled_macro_drift.py 94e92ff1...,
h2_post_release_momentum.py b2f09ab6...), and "D.1f imports that tuple; it does not retype
labels or factories."
Quoted (list 5.7): "they are amended to accept a table argument whose default is the existing
table, re-hashed in a declared amendment recorded in the STATE file before the purchase ...
the D.1f factories for E-H1 and E-H2 pass the combined table."
Quoted (list 5.6): "refuses to run if any hash in section 0, in the harness-freeze manifest,
or of this file or of docs/NULL_CRITERIA.md has changed."
Quoted (list A1 table): "| E-H1 scheduled macro drift | C5 | `H1ScheduledMacroDrift` |" and
"| E-H2 post-release momentum | C5 | `H2PostReleaseMomentum` |".
Conflict: after the mandated amendment the two files' hashes differ from section 0, so (a)
by section 0 both members are INVALID until the list is re-issued, which after hashing means a
new declaration; (b) by 5.6 _d1f_confirmation.py must refuse to run at all; (c) the D.1f
factories that pass the table are not the verbatim no-argument expressions A1 pins, and
section 0 forbids retyping factories. A "STATE-file amendment" is not the "re-issue under a
new hash" section 0 demands. Whichever way D.1f resolves it, it deviates from a hashed
document, and a later session can read the same text the other way (drop C5 as INVALID, or
run with the table and call 5.6 satisfied).
Fix (three sentences, before hashing): in section 0, annotate the two E-H entries "pre-amendment
hash; the post-amendment hash is recorded in reports/stage_d1f_harness_freeze.json under the
declared amendment of 5.7, and for these two files only, section 0's INVALID rule and 5.6's
refusal read the freeze manifest"; in A1, give E-H1 and E-H2 a second factory line, "D.1f
confirmation factory: `lambda: H1ScheduledMacroDrift(release_table=RELEASE_TABLE_ET |
RELEASE_TABLE_2019_2024)`" (and the E-H2 analogue), verbatim as the amendment will write them,
and state that the continuity run of 1.4 uses the no-argument factories with the default table
and that the amended modules must reproduce the train-union figures to the cent under both
factories; amend the "does not retype labels or factories" sentence with "except the two
confirmation factories of E-H1 and E-H2 listed in A1".

#### NEW-6  SHOULD-FIX  The raw-symbol drop rule can remove May-June 2019 under a per-interval symbol mapping
Quoted (list 1.1): "A bar inside the continuous series whose raw symbol is not an MES outright
(MES, a month letter and a year digit) is dropped and logged; symbology maps instrument 7849's
2019 interval to 'DNMH929 C35' as well as 'MESM9' (D-4)."
Fact: data/bars.py resolves one raw symbol per instrument_id (`instrument_raw_symbols(rolls)`).
Instrument 7849 carries both symbols over 2019-04-01..2019-06-17; the April bars do not exist
(0 billable bytes) and the May-June bars are MESM9. If the builder labels every 7849 bar with the
first mapped symbol, the rule as written drops all bars from 2019-05-06 to the June 2019 roll,
V_M for 2019-05 and 2019-06 becomes empty, and S moves to 2019-07-01 or later by a coding
choice, not by the start rule.
Fix: "The raw symbol of a bar is the symbol symbology maps to its instrument_id ON THE BAR'S
DATE; a bar is dropped only if no MES outright maps to its instrument_id on that date. The
number of dropped bars per month is logged and is expected to be zero from 2019-05-06 on; a
non-zero count stops the run for a lead decision before step 5."

#### NEW-2  NOTE  Holdout-2 size rationale is now false at the corrected scale
Quoted (list 1.2 b): "about 259 days is several times the days Task 3 finds any member needs
for 80% null power at epsilon (section 4)". Section 4 now gives C3 566, C2 193, C6 181, C1 149,
C7 114 against about 239 usable holdout-2 days. Reword: "about 239 usable days exceeds the
binding n_b of every class except C3 (566), whose null power holdout-2 alone cannot reach".
This affects the stated reason for holdout-2's length, not any D.1f rule.

#### NEW-3  NOTE  The criteria's test summary does not carry D.1g's N = 59
Quoted (criteria 3): "then DSR > 0.95 at N = 58, daily t > 3.0 and CSCV PBO < 0.5". List 3.5 sets
N = 59 for D.1g, and D.1g is judged against the criteria document. Add "(N = 59 for D.1g's
queue-model C-H4, list 3.5)".

#### NEW-4  NOTE  The list cannot authorise a commit
Quoted (list 1.5 step 1b): "prints it into the STATE file before any quote or purchase, and
commits it." CLAUDE.md allows a commit only when the stage prompt asks; list 6 already says the
lead asks the user. Reword: "and asks the user to commit it".

#### NEW-5  NOTE  data/config.py must change before the freeze it is frozen by
Quoted (list 1.1): "with the caps in data/config.py as the user sets them for D.1f"; (list 5.8)
"Every other file under screening/, sim/, funnel/, rules/, data/ and strategy/ is byte-identical
to the harness-freeze manifest of step 1b", and 1b freezes "data/*.py". data/config.py is not in
5.8's list of files D.1f may change, yet its caps and session id must be set for the purchase.
Add to 1b: "data/config.py's D.1f session id and spend caps are set by the user before step 1b
and are frozen with it."

#### NEW-7  NOTE  "hashed at hashing time" now describes values that are already filled
Quoted (list 0): "the first three are regenerated by the unit correction of R-1 and hashed at
hashing time" while the three hashes are present and match disk. Reword: "hashed now; any
regeneration of these files before hashing re-fills these three lines". Aside, outside the two
documents: reports/stage_d1e_power_verification.md's header table still lists the superseded
input hashes (power.json c1f2d833..., members_trials.json bc6649da..., coverage.md a4b31316...);
its section 11 lists the current ones. A one-line note at the head of that report would stop a
reader taking the header as the verified state.

#### NEW-8  NOTE  The class-statement template lists C-H4 among the market-order trials
Quoted (criteria 1): "the trials executed through the engine with market orders ... at their
coded contract size (1 micro for the 29 fixed-size trials and C-H4, ...)". C-H4 rests limit
orders (trade-through fills) and belongs to C6, whose statement is 1.1. Move "and C-H4" out of
the market-order clause ("1 micro for the 29 fixed-size trials; C-H4, at 1 micro, is section
1.1's").

#### NEW-9  NOTE  The rewritten instrument guard's preamble and parenthetical disagree for H1 and H2
Quoted (list A3): "every daily bar that enters day d's condition (d-1 for H1, H2, H4, H5 and H6;
d-1 and d-2 for H3) must carry the instrument_id of day d's 08:30 bar ... The trailing 60 ranges
of H4 and H5 are basis-free and exempt." H1's Range[d-2..d-4] and H2's Range[d-2..d-7] also enter
the condition and are basis-free; the exemption sentence names only H4 and H5. Make the
parenthetical the rule: "the earlier ranges of H1 and H2 are basis-free and exempt, as are the
trailing 60 of H4 and H5".

#### NEW-10  NOTE  The epsilon rule names a field the grid file does not carry
Quoted (criteria 2.2): "epsilon_day = floor( min over every cell whose robust_c80_verdict ==
"pass" of net_edge_usd_per_day_at_2_micros / $2.50 )". power_gate.json rows have no such field;
the grid values come from the pinned reports/stage_d1e_power_gate_cells.json, which has it (the
extension file carries it directly). Say "net_edge_usd_per_day_at_2_micros as tabulated in
power_gate_cells.json for the 120 grid cells and as stored in the extension file".

New findings: 10 (1 BLOCKER to hashing, 1 SHOULD-FIX, 8 NOTE).

### 15.3 Verdict after amendments

NOT READY, on one item: NEW-1. Hashing now would freeze a self-contradiction that makes two
Tier A members (E-H1, E-H2) impossible to run without deviating from a hashed rule, and gives a
later session a compliant-looking reason either to drop C5 or to run past 5.6's refusal. The
fix is three sentences in section 0, A1 and 5.7, plus the three PARTLY remainders (criteria 1.1
"sized at 2 micros" for C-H4; criteria 4.2's "masked"; the NEW-1 carve-out itself) and NEW-6's
per-date symbol rule. None of the remaining NOTEs blocks hashing. After those amendments the
two documents are READY TO HASH under the section 6 procedure; epsilon = 34, N_C6 = 181, the
class tables and the 47-of-95 count are consistent with their pinned sources as of this
re-read.
