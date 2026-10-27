# E.32 lead design notes (working file; the protocol is the authority once written)

## Fixed facts (computed, no data read)
- Discovery 2020-12-01..2024-02-29: 816 trade dates (program grains calendars; equals E.31's 816 measured dates);
  E.31 kept 764 DAY dates for the front month after its exclusions (23 roll days, 20 after a roll, 4 holiday or
  early close, 5 late opens).
- Test 2017-05-01..2020-11-30: 905 trade dates (same calendars).
- Discovery files: one manifest, sha256 09396842c4fd5d742c166e5b6ca1327c5eeebfed9b112952b84d15f254c23261, 156 files
  (Z1 ZM MBO, Z2 ZS MBP-1, Z3 ZL MBP-1, Z4 definitions; 39 months each), 24,234,707,848 bytes, exit 3 (E.31:
  definitions data-quality findings only).
- Program code for thresholds: funnel.multiple_comparisons.expected_max_sharpe / deflated_sharpe_ratio (B&LdP eq. 3,
  cross-trial Sharpe variance, raw kurtosis), screening.stage_e_verdict.pbo (CSCV, 8 blocks), HLZ t > 3.0.
- p7_thresholds.py at budget 500 (N 1038), T 816: E[max SR] daily 0.114 (c=1); SR for DSR>=0.95 0.172 daily
  (2.74 annualised); Bonferroni z 3.72; Holm over 3 test candidates alpha 0.0167 (z 2.128).

## Binding text
- V43: frozen model/features/labels/window/hyperparameters/code hashed before any outcome; every configuration in N;
  purged + embargoed CV on discovery; one test on data that never selected it with the program's bar (Holm, net
  Sharpe, DSR at N, PBO); costs from the measured fill and adverse-selection model, never touched-means-filled.
- V50: trade-through rule for passive fills; E.31 read the discovery dates (markouts incl. queue-imbalance splits),
  so an order-flow test on them is not a clean holdout (the sealed window answers this).
- V51: discovery = owned 2020-12..2024-02; test = sealed 2017-05..2020-11; 2024-03+ closed.

## Power arithmetic (random walk, sigma_1m 3.15 ticks; alpha 0.05/3 one-sided, power 0.8; n = 8.82 (sigma/mu)^2)
- 15-min hold sigma 12.2: mu 1.0 net -> 1,313 trades (1.45/day of 905); mu 0.5 -> 5,250 (5.8/day; cap 19).
- 60-min sigma 24.4: mu 1.0 -> 5,250 (5.8/day > cap 4: infeasible); needs mu >= about 2 ticks net.
- One trade a day (open or close families): n <= 905 -> mu >= 2.97 sigma / 30.1 = 0.0987 sigma: 30-min hold
  sigma 17.3 -> mu >= 1.71 ticks net (3.3 gross). Literature R2 1-2% gives about corr 0.12 -> about 1.6 gross. Weak.
- Event family (about 40-60 events): mu >= 2.97 sigma / sqrt(n_events): hopeless unless huge.
=> Selection must carry a power gate computed from discovery trade counts with a shrunk edge (winner's curse).

## Open design questions for after the readers
- Families (<= 6): crush residual (with ZS/ZL lead features), order flow / worked orders / sweep-refill, session
  handoff (overnight gap at 08:30, close), post-USDA (power-doomed? keep as conditioner/exclusion?), liquidity
  regimes (conditioner, not a family).
- K-fold vs walk-forward: the test is EARLIER than discovery, so "train on later, predict earlier" mirrors the test.
- Grid points are configurations (no nested selection); selection only by the P8 rule over all of them.

## Program bar for the one-shot test (read 2026-10-27 00:18 from code, no data)
- V43 (DECISIONS.md 788-809): frozen model/features/labels/window/hyperparameters/code hashed before any outcome;
  every configuration searched counts into N; purged + embargoed CV on discovery; tested once on data that never
  selected it "with the program's bar (Holm, net Sharpe, DSR at N, PBO)"; costs from the measured fill and
  adverse-selection model, never touched-means-filled; no model trades before it passes.
- The bar in code: screening/stage_e_verdict.py (harness-pinned): per trial a daily series in "net ticks per
  contract per day"; stationary block bootstrap (mean block 5 days, B 10,000, seed 20260923 + ordinal) -> UCB95,
  SE_boot, p_upper; Holm at 0.05/K, K = the list's k_holm (1..9); DSR > 0.95 at the list's program N with the
  population variance of daily Sharpe over the Tier A trials if >= 2, else over every run trial of the cluster
  (V14 c); daily t > 3.0 one-sided; CSCV PBO < 0.5 on 8 contiguous blocks over the Tier A series (>= 2), else all
  run series. Fewer than 2 series -> DSR variance undefined and PBO undefined -> "no edge" (lines 549-594).
  => P8/P9 MUST put at least 2 run series on the test list, or the program's bar cannot pass. Pin how.
  => With 2-3 correlated candidates the V14(c) variance can be tiny (E[max SR] small) - a soft spot; consider a
     protocol-added, stricter check with V from the discovery cross-configuration variance (state it as an
     addition, never a relaxation).
- Runner trade-rate floor D9.3 (screening/stage_e_runner.py 31-39, 124-138; Stage E bar runner): refuses a 21st
  entry a day, exits sooner than 2 full minutes after an opening fill, and labels mean holding < 10 min. E.33 is
  not that runner, but the floor encodes Topstep's "average durations measured in seconds" pattern (E.0 F7.3)
  and bar resolution. Decide in P3 whether 1- and 5-minute horizons survive (firm thresholds: Lucid <= 5 s, Tradeify
  10 s, so minutes are allowed by firms; the 10-minute mean floor is a program rule for the bar runner).
- Null side (NULL_CRITERIA_E 2-3): eps_X = min(eps_tr, eps_funnel), eps_tr = floor($85 / (q x tick value)) net
  ticks/contract/day; for ZM at q = 1: floor(85/10) = 8 ticks/day. A null statement needs UCB95 < eps_X with
  achieved null power >= 0.80. Relevant to P10's "what is reported if nothing passes".

## Test-window bar (p7_thresholds.py test_bars, budget 500, N 1038, T_test 905; normal days)
- daily t > 3.0 -> SR_d 0.0997; DSR > 0.95 at V = c/(T-1): c 0.25 0.1092, c 0.5 0.1317, c 1 0.1637, c 2 0.2089.
- 80% power needs true SR_d = bar + 0.8416/sqrt(905) (+0.028): c = 1 -> 0.1917 (3.04 annualised).
- Net edge per trade for 80% power (c = 1), mu = s sigma_h / sqrt(n): 5 min x 8/day 0.48; 15 min x 4/day 1.17,
  x 8/day 0.83; 30 min x 4/day 1.65; 60 min x 4/day 2.34 ticks net. If the V14(c) variance over the test
  candidates is small (near-duplicate candidates), the t bar binds: 15 min x 4/day 0.78.
- Caveat for the protocol: n trades every day assumed; zero-trade days lower SR_d. Winner's curse: discovery
  estimates must be shrunk before the power check (P8).

## Environment facts for P5 (uv env, 2026-10-27 00:20)
- Installed and pinned in pyproject: numpy 2.5.3, pandas 3.0.5, scipy 1.18.1, scikit-learn 1.9.1, lightgbm 4.7.0,
  torch 2.14.0+cu130, databento 0.82.0. Missing: statsmodels (Johansen/VECM would need own code or a dependency
  change: E.33 decision), polars, numba, xgboost.
- Web searches used by 00:20: 101 of the 1,500 session cap.
