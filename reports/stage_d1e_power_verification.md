# Stage D.1e Task 3b: independent verification of the power and sample-size figures

NOTE (added by the lead, 2026-09-22 09:05Z): the input hashes in the header tables of sections 1 to 10 are those of the pre-correction run (2 micros assumed); section 11 re-verifies the corrected per-micro run and lists the current hashes, which are the verified state.

Worker: fable, xhigh (Stage D.1e, 2026-09-22). Second, independent computation of every number in
`reports/stage_d1e_power.json` / `.md` that enters the verdict criteria or the decision packet, plus
the epsilon derivation. The code under verification (`strategy/research/_d1e_power.py`,
`_d1e_power_stats.py`, `_d1e_power_report.py`, `_d1e_calendar.py`) was NOT imported for any
recomputation; three short passages of it were read at the very end, only to explain two
JSON-internal differences already found (sections 8.1 and 8.2) and the supplied-days method
(section 6). The only project import is `funnel.null_generator.stationary_bootstrap_indices`, which
the program's own inference uses.

> Appended 2026-09-22: section 11 re-verifies the run after the unit correction (per-micro trial series,
> H proxies 200/230, eps_day = 34 on the finished extension file). Sections 2 to 5 and 8 to 9 describe the
> superseded run for the 31 trials and 6 H rows; the 64 statistic rows are unchanged between the two.

Recomputation script (scratch, re-runnable, prints markdown to stdout, writes nothing):
`reports/_d1e_power_verify_scratch.py` (`uv run python reports/_d1e_power_verify_scratch.py --sim`).

Holdout: `uv run python -m data.holdout status` at start and end: `unlocks_logged: 0`, `all_ok: true`.
No holdout date, no Databento call, no network, no TopstepX. Files written: this report and the scratch script.

## Inputs (read only) and their sha256 at the time of reading

| file | sha256 | note |
|---|---|---|
| reports/stage_d1e_power.json | c1f2d8334e708f72639110efd5a127459552215d829c97b78b4ae1d702347c83 | generated 2026-09-22T06:00:52Z, eps_day = 34 (provisional) |
| reports/stage_d1e_members_trials.json | bc6649da293edb0b63e025d610437ffa89c81a66049139b01ea1cb8507e802a7 | matches the JSON's `source_sha256` |
| reports/stage_d1e_members_events.json | c6db647fe818faec0f70772a9b241c78f0865999ee83c6d4b9d4a19317bc2df8 | matches |
| reports/stage_d1e_coverage.md | a4b31316486198c8011ef32a4d37becd90555729a6ce2b090be6887d8373d013 | matches |
| reports/stage_d1e_quotes.md | 18d1fe2b8f8a56e2545ed917c77f4c5e8deed661deee777a485d9805e1bffcfd | matches |
| reports/power_gate.json | e57088247881c184a411344d6b1b696a782987eb92ef3a4328e6b6f39315c40c | 120 grid cells, T = 1, 2, 4 |
| reports/stage_d1e_gate_extension.json (version A) | 9fe0dbc20915067d0093ba24dd1437e582c3bcd6d827773b9556c8b00f5be5b9 | mtime 2026-09-21 22:54:52 local (-0700), 84 rows, T = 1, 2, 4, 8, robust_c80 pass 58 / marginal 4 / fail 22. This is the version on disk when `stage_d1e_power.json` was generated. |
| reports/stage_d1e_gate_extension.json (version B) | e1659fb3021f8b855b96d2ebaa5d2f4cc37dec62e484aea1625f9431bccc6be6 | rewritten by the background gate-extension job at 23:07:28 local (generated_utc 2026-09-22T06:07:28Z), 90 rows (six standard-path T = 16 rows appended), pass 61 / marginal 4 / fail 25. This is the version my script read. The job was still running at the end of this task (21 processes), so the file may change again. |

## Verdict summary

| section | verdict | size of any discrepancy |
|---|---|---|
| 1. eps_day and its cell | VERIFIED WITH NOTES | none in value (34 on both file versions); version caveat and a one-marginal-cell sensitivity, see 1.2 |
| 2. every member: SD_day, r, VIF_boot, n_a, n_b | VERIFIED | 101/101 members: max relative difference < 1e-4 % on r, SD_day, VIF_boot; all 202 analytic n identical |
| 3. re-simulation and the chosen-figure rule | VERIFIED WITH NOTES | 26/26 arm-checks consistent (worst 5.2 %); rule correctly applied to all 190 arm-cases; one seed-sensitive flag (F4_4 x100, arm b) |
| 4. Family H projections | VERIFIED | exact |
| 5. class tables incl. `resolution_range`, `typical_r`, `eps_trade`, `gross_equivalent_trade`, binding members, achievable flags | VERIFIED | exact, 42/42 resolution rows |
| 6. supplied days and holdout-2 | VERIFIED WITH NOTES | arithmetic reproduces exactly under the stated method; the method undercounts trade dates by 3 to 4 days (exact rule) and by about 3 to 4 % (pipeline's own calendar convention); no achievability flag changes |
| 7. tests/test_d1e_power.py audit | VERIFIED WITH NOTES | 10 passed in 1.97 s; expectations independent of the code; both known-answer cases present; gaps listed |
| 8. JSON internal consistency | VERIFIED WITH NOTES | `spot_check.closed_form_power_b` is a separate MC draw (max 2.3 sigma from the curve); one 3.3-sigma non-monotone step at short n; md matches JSON row for row |

## 1. eps_day and the cell it comes from

Rule (docs/NULL_CRITERIA.md 2.2): smallest `net_edge_usd_per_day_at_2_micros` among cells with
`robust_c80_verdict == "pass"` over both payout paths and every T in `power_gate.json` and
`stage_d1e_gate_extension.json`, divided by 2.5, rounded down to a whole tick. `power_gate.json` rows
carry no net-per-day field, so I derived it as (gross ticks per trade - cost_usd(T)/1.25) x T x 2 x 1.25
with the cost table `mean_round_turn_cost_usd_per_micro_by_segments`; on the extension rows the same
formula reproduces the stored field for all 90 rows to 1e-6. Round-turn costs recomputed: 2.1107 (T=1),
2.0841 (T=2), 2.0725 (T=4) ticks, 2.0639 (T=8) from the extension: the figures NULL_CRITERIA quotes.
The verdict rule (`pass` iff lower95 >= 0.80, `marginal` iff power >= 0.80 and lower95 < 0.80) holds
on all 210 cells.

| quantity | reported | recomputed | rel diff | verdict |
|---|---|---|---|---|
| min passing net $/day | (34 ticks/day implied) | 87.4809 (power_gate.json, consistency, T=2, p=0.60, R=1.00; 17.496 net ticks/trade; robust power 0.8121, lower95 0.8036) | - | VERIFIED |
| eps_day exact | - | 34.9923 ticks per micro per day | - | - |
| eps_day (floor) | 34 | 34 | 0 | VERIFIED |
| eps_day in $ at 2 micros | - | 85.00 | - | - |
| passing cells (version B) | - | 98 of 210 (37 grid + 61 extension); 4 marginal | - | - |

Five smallest passing cells:

| file | path | T | p | R | net ticks/trade | net $/day | robust power | lower95 |
|---|---|---|---|---|---|---|---|---|
| power_gate.json | consistency | 2 | 0.6 | 1.0 | 17.496 | 87.481 | 0.8121 | 0.8036 |
| stage_d1e_gate_extension.json | consistency | 8 | 0.575 | 1.0 | 4.601 | 92.018 | 0.8636 | 0.8561 |
| stage_d1e_gate_extension.json | consistency | 8 | 0.475 | 1.5 | 4.738 | 94.767 | 0.8565 | 0.8488 |
| stage_d1e_gate_extension.json | consistency | 4 | 0.66 | 0.75 | 9.688 | 96.878 | 0.9074 | 0.9010 |
| stage_d1e_gate_extension.json | consistency | 4 | 0.59 | 1.0 | 9.755 | 97.550 | 0.8896 | 0.8828 |

Smallest marginal cells (excluded by the rule) and largest failing cells:

| file | path | T | p | R | net $/day | verdict | robust power | lower95 |
|---|---|---|---|---|---|---|---|---|
| stage_d1e_gate_extension.json | consistency | 4 | 0.58 | 1.0 | 84.408 | marginal | 0.8043 | 0.7956 |
| stage_d1e_gate_extension.json | consistency | 1 | 0.47 | 2.0 | 99.286 | marginal | 0.8009 | 0.7921 |
| stage_d1e_gate_extension.json | standard | 2 | 0.62 | 1.0 | 107.061 | marginal | 0.8064 | 0.7977 |
| stage_d1e_gate_extension.json | standard | 1 | 0.49 | 2.0 | 114.588 | fail | 0.7790 | 0.7699 |
| stage_d1e_gate_extension.json | standard | 1 | 0.56 | 1.5 | 112.517 | fail | 0.7956 | 0.7868 |
| stage_d1e_gate_extension.json | standard | 1 | 0.52 | 1.75 | 111.959 | fail | 0.7776 | 0.7685 |

### 1.1 Version caveat
Version A (84 rows) was on disk when the power JSON was produced; version B (90 rows) appended six
standard-path T = 16 rows (3 pass, smallest passing $113.20; 3 fail) and left the earlier 84 rows'
verdict counts unchanged (58/4/22 -> 61/4/25), so eps_day = 34 on both versions. The smallest passing
extension cell on version B is $92.02 (consistency, T=8, p=0.575, R=1.0), above the grid cell that binds.
The background job was still writing at the end of this task; a consistency-path T = 16 pass below
$87.48 is the only way the figure moves. The lead should pin the extension file's sha256 that the final
eps is derived from and re-run the derivation on that pinned version (the scratch script prints it).

### 1.2 Sensitivity, descriptive
The nearest excluded cell is `marginal`: consistency, T=4, p=0.58, R=1.0 at $84.41 per day (robust power
0.8043, lower95 0.7956). Had it read `pass`, eps_day would be floor(84.41/2.5) = 33. The rule excludes
marginal cells and the exclusion is applied as written; this is recorded so the lead knows the figure is
one MC verdict away from 33. The binding cell's $87.48 is deterministic (E|m_2| = 97.9016 ticks x
(0.6 - 0.4) - 2.0841 = 17.496 ticks x 5), so only its verdict, not its value, is subject to MC noise.

Verdict: **VERIFIED WITH NOTES** (value exact; version to be pinned by the lead).

## 2. Every member: SD_day, r, VIF_boot, n_a_analytic, n_b_analytic

Recomputed from the raw series only. Trials: d_t = daily_net_usd / 2.5 over 289 dates, r = sum(daily_n_trips)/289.
Statistics: d_t = s x daily_sum_ticks - 2.11 x daily_count over 139 EDA dates, r = sum(daily_count)/139, s = recorded_direction.
SD_day = std(d, ddof=1). VIF_boot = [g0 + 2 sum_(k=1..20) 0.8^k g_k]/g0 with g_k = (1/n) sum (d_t - m)(d_(t+k) - m), floor 0.2.
Quantiles by Newton on math.erfc: z_a = 3.1340460549238505 (reported 3.1340460549238425, diff 8e-15),
z_b = 0.8416212335729145 (diff 1e-16), z_95 = 1.6448536269514722 (diff 7e-16); alpha_holm = 0.05/58 exact.
n_a = ceil(((z_a+z_b) SD sqrt(VIF)/34)^2), n_b likewise with z_95.

Result: 101 members reported, 101 recomputed, none missing or extra. Worst |relative difference| over
all members: r 0.0000 %, SD_day 0.0000 %, VIF_boot 0.0000 % (all below 1e-4 %). All 101 n_a and all 101
n_b identical (no ceiling-boundary case arose). eps_trade = 34/r identical. No member's VIF is floored
(smallest VIF_boot 0.4001, G4.RTH.30), consistent with `floor_hits = 0`. Secondary fields:
`eps_min_at_supplied` (per day and per trade at every S) max |rel diff| 1e-13 %; `eps_ref_days` (n_a, n_b
at 1 net tick per trade, eps_day_ref = r) identical for every member; `n_b_sensitivity` at eps 30..40
identical for every member; `cluster_vif` (trials) within 0.5 % for all 31.

Full table (d% = (recomputed - reported)/reported x 100):

| member | kind | r rep | r mine | d% | SD rep | SD mine | d% | VIF rep | VIF mine | d% | lag1 rep | lag1 mine | n_a rep | n_a mine | n_b rep | n_b mine | eps/trade rep | mine | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | trial | 0.9550 | 0.9550 | +0.000 | 16.940 | 16.940 | +0.000 | 0.8903 | 0.8903 | +0.000 | +0.0043 | +0.0043 | 4 | 4 | 2 | 2 | 35.601 | 35.601 | ok |
| A-H2 rth close window (buy) | trial | 0.9204 | 0.9204 | +0.000 | 25.811 | 25.811 | +0.000 | 0.9725 | 0.9725 | +0.000 | -0.0863 | -0.0863 | 9 | 9 | 4 | 4 | 36.940 | 36.940 | ok |
| A-H2 rth close window (sell) | trial | 0.9204 | 0.9204 | +0.000 | 25.848 | 25.848 | +0.000 | 0.9748 | 0.9748 | +0.000 | -0.0863 | -0.0863 | 9 | 9 | 4 | 4 | 36.940 | 36.940 | ok |
| A-H3 weekend effect | trial | 0.3806 | 0.3806 | +0.000 | 61.732 | 61.732 | +0.000 | 0.9871 | 0.9871 | +0.000 | +0.1222 | +0.1222 | 52 | 52 | 21 | 21 | 89.327 | 89.327 | ok |
| A-H4 eth leg | trial | 0.9585 | 0.9585 | +0.000 | 68.269 | 68.269 | +0.000 | 0.8777 | 0.8777 | -0.000 | -0.0128 | -0.0128 | 56 | 56 | 22 | 22 | 35.473 | 35.473 | ok |
| A-H4 rth leg | trial | 0.9550 | 0.9550 | +0.000 | 111.995 | 111.995 | +0.000 | 0.5520 | 0.5520 | +0.000 | -0.3006 | -0.3006 | 95 | 95 | 38 | 38 | 35.601 | 35.601 | ok |
| B-H1 opening-range breakout (hold 5) | trial | 0.9550 | 0.9550 | +0.000 | 13.202 | 13.202 | +0.000 | 0.9704 | 0.9704 | +0.000 | +0.1087 | +0.1087 | 3 | 3 | 1 | 1 | 35.601 | 35.601 | ok |
| B-H1 opening-range breakout (hold 75) | trial | 0.9550 | 0.9550 | +0.000 | 48.626 | 48.626 | +0.000 | 0.9217 | 0.9217 | +0.000 | -0.0865 | -0.0865 | 30 | 30 | 12 | 12 | 35.601 | 35.601 | ok |
| B-H2 prior-day stop cascade | trial | 0.7716 | 0.7716 | +0.000 | 18.545 | 18.545 | +0.000 | 1.2119 | 1.2119 | +0.000 | +0.0874 | +0.0874 | 6 | 6 | 3 | 3 | 44.063 | 44.063 | ok |
| B-H3 breakout leg | trial | 0.9481 | 0.9481 | +0.000 | 29.019 | 29.019 | +0.000 | 0.8169 | 0.8169 | -0.000 | -0.0531 | -0.0531 | 10 | 10 | 4 | 4 | 35.861 | 35.861 | ok |
| B-H3 fade leg | trial | 0.9481 | 0.9481 | +0.000 | 29.017 | 29.017 | +0.000 | 0.8184 | 0.8184 | +0.000 | -0.0550 | -0.0550 | 10 | 10 | 4 | 4 | 35.861 | 35.861 | ok |
| B-H4 narrow-range breakout | trial | 0.3979 | 0.3979 | +0.000 | 13.746 | 13.746 | +0.000 | 0.7346 | 0.7346 | -0.000 | -0.0351 | -0.0351 | 2 | 2 | 1 | 1 | 85.443 | 85.443 | ok |
| C-H1 magnitude-conditioned reversal | trial | 140.9792 | 140.9792 | +0.000 | 104.030 | 104.030 | +0.000 | 0.7988 | 0.7988 | +0.000 | -0.0910 | -0.0910 | 119 | 119 | 47 | 47 | 0.241 | 0.241 | ok |
| C-H2 post-spike exhaustion fade | trial | 30.5502 | 30.5502 | +0.000 | 46.650 | 46.650 | +0.000 | 1.1675 | 1.1675 | -0.000 | +0.1772 | +0.1772 | 35 | 35 | 14 | 14 | 1.113 | 1.113 | ok |
| C-H3 close-location-value reversal | trial | 41.7509 | 41.7509 | +0.000 | 58.436 | 58.436 | +0.000 | 0.7883 | 0.7883 | +0.000 | +0.0885 | +0.0885 | 37 | 37 | 15 | 15 | 0.814 | 0.814 | ok |
| D-H1 trailing-vol regime gate | trial | 0.3668 | 0.3668 | +0.000 | 4.153 | 4.153 | +0.000 | 0.9129 | 0.9129 | +0.000 | -0.0192 | -0.0192 | 1 | 1 | 1 | 1 | 92.698 | 92.698 | ok |
| D-H2 inverse-vol sizing | trial | 0.9550 | 0.9550 | +0.000 | 27.860 | 27.860 | +0.000 | 0.7696 | 0.7696 | -0.000 | -0.0159 | -0.0159 | 9 | 9 | 4 | 4 | 35.601 | 35.601 | ok |
| D-H3 range-compression gate | trial | 9.8478 | 9.8478 | +0.000 | 32.004 | 32.004 | +0.000 | 0.9447 | 0.9447 | +0.000 | +0.0074 | +0.0074 | 14 | 14 | 6 | 6 | 3.453 | 3.453 | ok |
| D-H4 overnight gap fade | trial | 0.4637 | 0.4637 | +0.000 | 9.686 | 9.686 | +0.000 | 1.1393 | 1.1393 | +0.000 | +0.0228 | +0.0228 | 2 | 2 | 1 | 1 | 73.328 | 73.328 | ok |
| E-H1 scheduled macro drift | trial | 0.1073 | 0.1073 | +0.000 | 25.143 | 25.143 | +0.000 | 1.1762 | 1.1762 | -0.000 | -0.0018 | -0.0018 | 11 | 11 | 4 | 4 | 316.968 | 316.968 | ok |
| E-H2 post-release momentum | trial | 0.0865 | 0.0865 | +0.000 | 4.714 | 4.714 | +0.000 | 0.9479 | 0.9479 | +0.000 | -0.0000 | -0.0000 | 1 | 1 | 1 | 1 | 393.040 | 393.040 | ok |
| E-H3 quarterly witching short | trial | 0.0138 | 0.0138 | +0.000 | 0.932 | 0.932 | +0.000 | 0.9884 | 0.9884 | +0.000 | -0.0015 | -0.0015 | 1 | 1 | 1 | 1 | 2456.500 | 2456.500 | ok |
| E-H4 turn-of-month long | trial | 0.1903 | 0.1903 | +0.000 | 2.682 | 2.682 | +0.000 | 0.8995 | 0.8995 | -0.000 | +0.0743 | +0.0743 | 1 | 1 | 1 | 1 | 178.655 | 178.655 | ok |
| C-H4 passive-fill reversal | trial | 92.4671 | 92.4671 | +0.000 | 95.272 | 95.272 | +0.000 | 0.9272 | 0.9272 | +0.000 | +0.0128 | +0.0128 | 116 | 116 | 46 | 46 | 0.368 | 0.368 | ok |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | trial | 0.9446 | 0.9446 | +0.000 | 12.415 | 12.415 | +0.000 | 0.9644 | 0.9644 | +0.000 | +0.0520 | +0.0520 | 3 | 3 | 1 | 1 | 35.993 | 35.993 | ok |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | trial | 0.9446 | 0.9446 | +0.000 | 48.084 | 48.084 | +0.000 | 1.3629 | 1.3629 | +0.000 | +0.1728 | +0.1728 | 44 | 44 | 17 | 17 | 35.993 | 35.993 | ok |
| RT3 B-H3 breakout leg 5-min bars | trial | 0.9446 | 0.9446 | +0.000 | 31.577 | 31.577 | +0.000 | 0.9070 | 0.9070 | +0.000 | -0.0518 | -0.0518 | 13 | 13 | 5 | 5 | 35.993 | 35.993 | ok |
| RT4 B-H3 fade leg 5-min bars | trial | 0.9446 | 0.9446 | +0.000 | 31.576 | 31.576 | +0.000 | 0.9060 | 0.9060 | +0.000 | -0.0529 | -0.0529 | 13 | 13 | 5 | 5 | 35.993 | 35.993 | ok |
| RT5 C-H2 spike fade 5-min bars | trial | 9.7716 | 9.7716 | +0.000 | 33.856 | 33.856 | +0.000 | 0.9717 | 0.9717 | +0.000 | +0.0703 | +0.0703 | 16 | 16 | 6 | 6 | 3.479 | 3.479 | ok |
| RT6 D-H1 daily-vol regime gate | trial | 0.4637 | 0.4637 | +0.000 | 5.603 | 5.603 | +0.000 | 0.9439 | 0.9439 | -0.000 | +0.0765 | +0.0765 | 1 | 1 | 1 | 1 | 73.328 | 73.328 | ok |
| RT7 D-H2 daily-vol sizing | trial | 0.8893 | 0.8893 | +0.000 | 17.157 | 17.157 | +0.000 | 0.8517 | 0.8517 | +0.000 | +0.0225 | +0.0225 | 4 | 4 | 2 | 2 | 38.233 | 38.233 | ok |
| F3_2_bucket07_bucket08 | statistic | 0.9640 | 0.9640 | +0.000 | 39.483 | 39.483 | +0.000 | 1.1742 | 1.1742 | -0.000 | -0.0183 | -0.0183 | 26 | 26 | 10 | 10 | 35.269 | 35.269 | ok |
| F6_1_overnight_range_position | statistic | 0.9928 | 0.9928 | +0.000 | 103.103 | 103.103 | +0.000 | 0.9586 | 0.9586 | +0.000 | +0.0906 | +0.0906 | 140 | 140 | 55 | 55 | 34.246 | 34.246 | ok |
| F3_3_opening_30min_to_close_momentum | statistic | 0.9640 | 0.9640 | +0.000 | 46.097 | 46.097 | +0.000 | 0.9319 | 0.9319 | +0.000 | +0.0169 | +0.0169 | 28 | 28 | 11 | 11 | 35.269 | 35.269 | ok |
| F3_2_bucket08_bucket09 | statistic | 0.9640 | 0.9640 | +0.000 | 38.901 | 38.901 | +0.000 | 1.0301 | 1.0301 | +0.000 | +0.2433 | +0.2433 | 22 | 22 | 9 | 9 | 35.269 | 35.269 | ok |
| F3_3_overnight_to_close_momentum | statistic | 0.9640 | 0.9640 | +0.000 | 46.253 | 46.253 | +0.000 | 0.9244 | 0.9244 | +0.000 | +0.0354 | +0.0354 | 28 | 28 | 11 | 11 | 35.269 | 35.269 | ok |
| F4_4_round_number_multiples_of_100 | statistic | 4.0216 | 4.0216 | +0.000 | 87.882 | 87.882 | +0.000 | 1.0996 | 1.0996 | +0.000 | +0.1136 | +0.1136 | 117 | 117 | 46 | 46 | 8.454 | 8.454 | ok |
| F3_2_bucket01_bucket02 | statistic | 0.9928 | 0.9928 | +0.000 | 59.604 | 59.604 | +0.000 | 1.2124 | 1.2124 | +0.000 | +0.0139 | +0.0139 | 59 | 59 | 24 | 24 | 34.246 | 34.246 | ok |
| F3_2_bucket10_bucket11 | statistic | 0.9640 | 0.9640 | +0.000 | 41.597 | 41.597 | +0.000 | 0.7732 | 0.7732 | +0.000 | -0.1231 | -0.1231 | 19 | 19 | 8 | 8 | 35.269 | 35.269 | ok |
| F4_1_rth_open_crossing | statistic | 1.8777 | 1.8777 | +0.000 | 53.946 | 53.946 | +0.000 | 1.2585 | 1.2585 | +0.000 | +0.0791 | +0.0791 | 51 | 51 | 20 | 20 | 18.107 | 18.107 | ok |
| F3_2_bucket02_bucket03 | statistic | 0.9928 | 0.9928 | +0.000 | 61.309 | 61.309 | +0.000 | 1.1460 | 1.1460 | +0.000 | +0.0046 | +0.0046 | 59 | 59 | 24 | 24 | 34.246 | 34.246 | ok |
| F3_2_bucket05_bucket06 | statistic | 0.9928 | 0.9928 | +0.000 | 42.771 | 42.771 | +0.000 | 0.8831 | 0.8831 | +0.000 | -0.0535 | -0.0535 | 23 | 23 | 9 | 9 | 34.246 | 34.246 | ok |
| F3_2_bucket04_bucket05 | statistic | 0.9928 | 0.9928 | +0.000 | 54.304 | 54.304 | +0.000 | 1.0297 | 1.0297 | +0.000 | +0.0538 | +0.0538 | 42 | 42 | 17 | 17 | 34.246 | 34.246 | ok |
| F3_2_bucket06_bucket07 | statistic | 0.9928 | 0.9928 | +0.000 | 43.853 | 43.853 | +0.000 | 0.7769 | 0.7769 | +0.000 | -0.1216 | -0.1216 | 21 | 21 | 8 | 8 | 34.246 | 34.246 | ok |
| F3_2_bucket12_bucket13 | statistic | 0.9640 | 0.9640 | +0.000 | 46.420 | 46.420 | +0.000 | 0.8680 | 0.8680 | +0.000 | -0.0512 | -0.0512 | 26 | 26 | 11 | 11 | 35.269 | 35.269 | ok |
| G2.RTH.30 | statistic | 2.2950 | 2.2950 | +0.000 | 62.917 | 62.917 | +0.000 | 0.9836 | 0.9836 | -0.000 | -0.0567 | -0.0567 | 54 | 54 | 21 | 21 | 14.815 | 14.815 | ok |
| G1.RTH.5 | statistic | 12.8705 | 12.8705 | +0.000 | 106.326 | 106.326 | +0.000 | 0.4395 | 0.4395 | +0.000 | -0.2793 | -0.2793 | 68 | 68 | 27 | 27 | 2.642 | 2.642 | ok |
| G2.ETH.30 | statistic | 4.3022 | 4.3022 | +0.000 | 54.118 | 54.118 | +0.000 | 1.0781 | 1.0781 | -0.000 | +0.0493 | +0.0493 | 44 | 44 | 17 | 17 | 7.903 | 7.903 | ok |
| G2.ETH.5 | statistic | 9.5540 | 9.5540 | +0.000 | 39.594 | 39.594 | +0.000 | 0.9744 | 0.9744 | +0.000 | +0.0334 | +0.0334 | 21 | 21 | 9 | 9 | 3.559 | 3.559 | ok |
| G5.RTH.15 | statistic | 0.9281 | 0.9281 | +0.000 | 40.624 | 40.624 | +0.000 | 0.9310 | 0.9310 | -0.000 | +0.1728 | +0.1728 | 22 | 22 | 9 | 9 | 36.636 | 36.636 | ok |
| G5.RTH.30 | statistic | 0.8921 | 0.8921 | +0.000 | 48.541 | 48.541 | +0.000 | 0.8853 | 0.8853 | -0.000 | -0.0162 | -0.0162 | 29 | 29 | 12 | 12 | 38.113 | 38.113 | ok |
| G3.RTH.15 | statistic | 0.9928 | 0.9928 | +0.000 | 163.037 | 163.037 | +0.000 | 0.9470 | 0.9470 | +0.000 | +0.0652 | +0.0652 | 345 | 345 | 135 | 135 | 34.246 | 34.246 | ok |
| F1_1_h1_RTH | statistic | 381.1295 | 381.1295 | +0.000 | 263.274 | 263.274 | +0.000 | 1.5268 | 1.5268 | +0.000 | +0.0974 | +0.0974 | 1447 | 1447 | 566 | 566 | 0.089 | 0.089 | ok |
| F1_1_h5_RTH | statistic | 75.4317 | 75.4317 | +0.000 | 182.518 | 182.518 | +0.000 | 0.6674 | 0.6674 | +0.000 | -0.1619 | -0.1619 | 304 | 304 | 119 | 119 | 0.451 | 0.451 | ok |
| F1_1_h15_RTH | statistic | 24.4820 | 24.4820 | +0.000 | 191.778 | 191.778 | +0.000 | 1.1518 | 1.1518 | +0.000 | +0.1128 | +0.1128 | 580 | 580 | 227 | 227 | 1.389 | 1.389 | ok |
| F1_1_h30_RTH | statistic | 11.7410 | 11.7410 | +0.000 | 168.272 | 168.272 | +0.000 | 1.0528 | 1.0528 | +0.000 | +0.0743 | +0.0743 | 408 | 408 | 160 | 160 | 2.896 | 2.896 | ok |
| F1_1_h60_RTH | statistic | 4.8777 | 4.8777 | +0.000 | 141.644 | 141.644 | +0.000 | 1.0307 | 1.0307 | -0.000 | +0.0519 | +0.0519 | 283 | 283 | 111 | 111 | 6.971 | 6.971 | ok |
| F1_1_h1_ETH | statistic | 927.8273 | 927.8273 | +0.000 | 177.319 | 177.319 | +0.000 | 1.3338 | 1.3338 | +0.000 | +0.1344 | +0.1344 | 574 | 574 | 225 | 225 | 0.037 | 0.037 | ok |
| F1_1_h5_ETH | statistic | 183.9424 | 183.9424 | +0.000 | 153.002 | 153.002 | +0.000 | 1.0306 | 1.0306 | +0.000 | +0.0152 | +0.0152 | 330 | 330 | 130 | 130 | 0.185 | 0.185 | ok |
| F1_1_h15_ETH | statistic | 59.9640 | 59.9640 | +0.000 | 149.198 | 149.198 | +0.000 | 0.7922 | 0.7922 | +0.000 | -0.1168 | -0.1168 | 242 | 242 | 95 | 95 | 0.567 | 0.567 | ok |
| F1_1_h30_ETH | statistic | 28.9640 | 28.9640 | +0.000 | 145.375 | 145.375 | +0.000 | 0.9494 | 0.9494 | +0.000 | +0.1120 | +0.1120 | 275 | 275 | 108 | 108 | 1.174 | 1.174 | ok |
| F1_1_h60_ETH | statistic | 12.9712 | 12.9712 | +0.000 | 142.746 | 142.746 | +0.000 | 1.2065 | 1.2065 | +0.000 | +0.0605 | +0.0605 | 337 | 337 | 132 | 132 | 2.621 | 2.621 | ok |
| F2_4_15min_vol_tercile_bottom | statistic | 8.1655 | 8.1655 | +0.000 | 55.255 | 55.255 | +0.000 | 1.0425 | 1.0425 | +0.000 | -0.0244 | -0.0244 | 44 | 44 | 18 | 18 | 4.164 | 4.164 | ok |
| F2_4_15min_vol_tercile_top | statistic | 8.1583 | 8.1583 | +0.000 | 150.538 | 150.538 | +0.000 | 1.4053 | 1.4053 | +0.000 | +0.1840 | +0.1840 | 436 | 436 | 171 | 171 | 4.168 | 4.168 | ok |
| F3_2_bucket03_bucket04 | statistic | 0.9928 | 0.9928 | +0.000 | 53.405 | 53.405 | +0.000 | 0.5936 | 0.5936 | +0.000 | -0.1019 | -0.1019 | 24 | 24 | 10 | 10 | 34.246 | 34.246 | ok |
| F3_2_bucket09_bucket10 | statistic | 0.9640 | 0.9640 | +0.000 | 41.228 | 41.228 | +0.000 | 0.7739 | 0.7739 | -0.000 | +0.0261 | +0.0261 | 18 | 18 | 8 | 8 | 35.269 | 35.269 | ok |
| F3_2_bucket11_bucket12 | statistic | 0.9640 | 0.9640 | +0.000 | 47.759 | 47.759 | +0.000 | 0.6847 | 0.6847 | +0.000 | -0.2052 | -0.2052 | 22 | 22 | 9 | 9 | 35.269 | 35.269 | ok |
| F4_2_prior_rth_close_crossing | statistic | 1.7050 | 1.7050 | +0.000 | 49.445 | 49.445 | +0.000 | 0.9557 | 0.9557 | +0.000 | +0.0770 | +0.0770 | 32 | 32 | 13 | 13 | 19.941 | 19.941 | ok |
| F4_4_round_number_multiples_of_50 | statistic | 8.9856 | 8.9856 | +0.000 | 118.136 | 118.136 | +0.000 | 0.7236 | 0.7236 | +0.000 | +0.0639 | +0.0639 | 139 | 139 | 55 | 55 | 3.784 | 3.784 | ok |
| F5_1_relvol_tercile_bottom | statistic | 3.3381 | 3.3381 | +0.000 | 73.226 | 73.226 | +0.000 | 0.8223 | 0.8223 | +0.000 | -0.1703 | -0.1703 | 61 | 61 | 24 | 24 | 10.185 | 10.185 | ok |
| F5_1_relvol_tercile_top | statistic | 3.3381 | 3.3381 | +0.000 | 117.067 | 117.067 | +0.000 | 0.7172 | 0.7172 | +0.000 | +0.0939 | +0.0939 | 135 | 135 | 53 | 53 | 10.185 | 10.185 | ok |
| F5_2_efficiency_tercile_bottom | statistic | 3.9137 | 3.9137 | +0.000 | 93.314 | 93.314 | +0.000 | 0.9660 | 0.9660 | +0.000 | -0.0760 | -0.0760 | 116 | 116 | 45 | 45 | 8.688 | 8.688 | ok |
| F5_2_efficiency_tercile_top | statistic | 3.9137 | 3.9137 | +0.000 | 112.123 | 112.123 | +0.000 | 0.7250 | 0.7250 | +0.000 | +0.1048 | +0.1048 | 125 | 125 | 49 | 49 | 8.688 | 8.688 | ok |
| F5_3_range_volume_residual | statistic | 11.7410 | 11.7410 | +0.000 | 162.951 | 162.951 | +0.000 | 0.7007 | 0.7007 | +0.000 | +0.0164 | +0.0164 | 255 | 255 | 100 | 100 | 2.896 | 2.896 | ok |
| G1.ETH.5 | statistic | 31.6906 | 31.6906 | +0.000 | 97.109 | 97.109 | +0.000 | 2.3633 | 2.3633 | -0.000 | +0.3226 | +0.3226 | 305 | 305 | 120 | 120 | 1.073 | 1.073 | ok |
| G2.RTH.5 | statistic | 7.2878 | 7.2878 | +0.000 | 66.230 | 66.230 | +0.000 | 0.7750 | 0.7750 | +0.000 | +0.0313 | +0.0313 | 47 | 47 | 19 | 19 | 4.665 | 4.665 | ok |
| G3.RTH.5 | statistic | 0.9928 | 0.9928 | +0.000 | 175.500 | 175.500 | +0.000 | 1.1669 | 1.1669 | +0.000 | +0.0876 | +0.0876 | 492 | 492 | 193 | 193 | 34.246 | 34.246 | ok |
| G4.RTH.5 | statistic | 12.8345 | 12.8345 | +0.000 | 89.376 | 89.376 | +0.000 | 1.0616 | 1.0616 | +0.000 | +0.0657 | +0.0657 | 116 | 116 | 46 | 46 | 2.649 | 2.649 | ok |
| G5.RTH.5 | statistic | 1.0144 | 1.0144 | +0.000 | 27.369 | 27.369 | +0.000 | 0.9276 | 0.9276 | -0.000 | +0.1071 | +0.1071 | 10 | 10 | 4 | 4 | 33.518 | 33.518 | ok |
| G1.ETH.15 | statistic | 10.4748 | 10.4748 | +0.000 | 96.683 | 96.683 | +0.000 | 0.9949 | 0.9949 | +0.000 | -0.1035 | -0.1035 | 128 | 128 | 50 | 50 | 3.246 | 3.246 | ok |
| G2.ETH.15 | statistic | 5.9928 | 5.9928 | +0.000 | 62.899 | 62.899 | +0.000 | 0.8386 | 0.8386 | +0.000 | -0.0267 | -0.0267 | 46 | 46 | 18 | 18 | 5.673 | 5.673 | ok |
| G1.RTH.15 | statistic | 4.1511 | 4.1511 | +0.000 | 106.077 | 106.077 | +0.000 | 1.4531 | 1.4531 | +0.000 | +0.2223 | +0.2223 | 224 | 224 | 88 | 88 | 8.191 | 8.191 | ok |
| G2.RTH.15 | statistic | 3.8058 | 3.8058 | +0.000 | 68.926 | 68.926 | +0.000 | 1.1299 | 1.1299 | +0.000 | +0.0771 | +0.0771 | 74 | 74 | 29 | 29 | 8.934 | 8.934 | ok |
| G4.RTH.15 | statistic | 4.1511 | 4.1511 | +0.000 | 100.089 | 100.089 | +0.000 | 0.7275 | 0.7275 | +0.000 | -0.0365 | -0.0365 | 100 | 100 | 39 | 39 | 8.191 | 8.191 | ok |
| G1.ETH.30 | statistic | 5.1439 | 5.1439 | +0.000 | 76.158 | 76.158 | +0.000 | 0.7272 | 0.7272 | +0.000 | -0.0675 | -0.0675 | 58 | 58 | 23 | 23 | 6.610 | 6.610 | ok |
| G1.RTH.30 | statistic | 2.0072 | 2.0072 | +0.000 | 76.182 | 76.182 | +0.000 | 0.8125 | 0.8125 | -0.000 | +0.0856 | +0.0856 | 65 | 65 | 26 | 26 | 16.939 | 16.939 | ok |
| G3.RTH.30 | statistic | 0.9640 | 0.9640 | +0.000 | 129.811 | 129.811 | +0.000 | 0.6681 | 0.6681 | +0.000 | -0.1223 | -0.1223 | 154 | 154 | 61 | 61 | 35.269 | 35.269 | ok |
| G4.RTH.30 | statistic | 1.9928 | 1.9928 | +0.000 | 83.214 | 83.214 | +0.000 | 0.4001 | 0.4001 | -0.000 | -0.2253 | -0.2253 | 38 | 38 | 15 | 15 | 17.061 | 17.061 | ok |
| G1.ETH.60 | statistic | 2.4029 | 2.4029 | +0.000 | 66.751 | 66.751 | +0.000 | 0.7340 | 0.7340 | +0.000 | +0.0096 | +0.0096 | 45 | 45 | 18 | 18 | 14.150 | 14.150 | ok |
| G2.ETH.60 | statistic | 2.8849 | 2.8849 | +0.000 | 63.381 | 63.381 | +0.000 | 0.6617 | 0.6617 | +0.000 | +0.0097 | +0.0097 | 37 | 37 | 15 | 15 | 11.786 | 11.786 | ok |
| G1.RTH.60 | statistic | 0.8417 | 0.8417 | +0.000 | 72.294 | 72.294 | +0.000 | 0.6003 | 0.6003 | -0.000 | -0.1768 | -0.1768 | 43 | 43 | 17 | 17 | 40.393 | 40.393 | ok |
| G2.RTH.60 | statistic | 1.2086 | 1.2086 | +0.000 | 68.420 | 68.420 | +0.000 | 0.6039 | 0.6039 | -0.000 | -0.1737 | -0.1737 | 39 | 39 | 16 | 16 | 28.131 | 28.131 | ok |
| G3.RTH.60 | statistic | 0.8058 | 0.8058 | +0.000 | 102.185 | 102.185 | +0.000 | 0.8180 | 0.8180 | -0.000 | -0.0799 | -0.0799 | 117 | 117 | 46 | 46 | 42.196 | 42.196 | ok |
| G4.RTH.60 | statistic | 0.8273 | 0.8273 | +0.000 | 75.725 | 75.725 | +0.000 | 0.6045 | 0.6045 | -0.000 | -0.3026 | -0.3026 | 48 | 48 | 19 | 19 | 41.096 | 41.096 | ok |
| G5.RTH.60 | statistic | 0.8058 | 0.8058 | +0.000 | 68.264 | 68.264 | +0.000 | 1.0546 | 1.0546 | -0.000 | +0.1765 | +0.1765 | 68 | 68 | 27 | 27 | 42.196 | 42.196 | ok |
| H1 NR4 opening-range breakout | projected | 0.2250 | 0.2250 | +0.000 | 47.434 | 47.434 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 31 | 31 | 13 | 13 | 151.111 | 151.111 | ok |
| H2 NR7 opening-range breakout | projected | 0.1286 | 0.1286 | -0.000 | 35.857 | 35.857 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 18 | 18 | 7 | 7 | 264.444 | 264.444 | ok |
| H3 inside-day opening-range breakout | projected | 0.2250 | 0.2250 | +0.000 | 47.434 | 47.434 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 31 | 31 | 13 | 13 | 151.111 | 151.111 | ok |
| H4 bottom-tercile prior range, breakout | projected | 0.3000 | 0.3000 | +0.000 | 54.772 | 54.772 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 42 | 42 | 17 | 17 | 113.333 | 113.333 | ok |
| H5 top-tercile prior range, opening-range fade | projected | 0.3000 | 0.3000 | +0.000 | 54.772 | 54.772 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 42 | 42 | 17 | 17 | 113.333 | 113.333 | ok |
| H6 prior-close location follow-through | projected | 0.4000 | 0.4000 | +0.000 | 72.732 | 72.732 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 73 | 73 | 29 | 29 | 85.000 | 85.000 | ok |

Verdict: **VERIFIED**.

## 3. Re-simulation and the chosen-figure rule

### 3.1 Members re-simulated
Binding n_b members of C1..C6 (A-H4 rth leg, G3.RTH.5, F1_1_h1_RTH, F2_4_15min_vol_tercile_top,
E-H1 scheduled macro drift, C-H4 passive-fill reversal; C7 is projected, nothing to simulate) plus
E-H3 quarterly witching short, C-H1 magnitude-conditioned reversal, F3_2_bucket04_bucket05 (the F3.2
bucket with the largest reported |diff_b|), G1.RTH.5, and three Tier B members chosen because the
chosen-figure rule changed their figure: G4.RTH.30 (largest diff_a, +41.5 %), G1.RTH.15 (+19.0 % a),
F4_4_round_number_multiples_of_100 (Tier A, +18.5 % b). Both arms were re-simulated for all 13 (the
brief asked n_a for two; the a-arm costs nothing extra since it is the same draw shifted by eps).

Construction (lead's correction 2, applied identically): centred series, stationary bootstrap indices
from `funnel.null_generator.stationary_bootstrap_indices(rng, n_source, n, 5.0)`, one draw set per
length, SE_hat = sqrt(var(x, ddof=1) x VIF_boot(source)/n) with VIF_boot(source) my own recomputed
value; arm a: reject if (mean + eps)/SE > z_a; arm b: success if mean + z_95 SE < eps; a zero-variance
draw counts as a rejection in arm a (shifted mean > 0) and a success in arm b. 2,000 replications per
length, my own seed base 7771, 4 processes, 28 s wall. Grid = the code's own grid for that member
(meta n_grid plus its analytic n_a and n_b; "grid-matched") and, separately, that grid plus five local
points at 0.75/0.87/1.0/1.15/1.3 x the reported simulated figure ("refined"). The crossing of 0.80 is
log-linearly interpolated between the first bracketing pair, as the code does (its own interpolation
reproduces from its curve: A-H4 rth leg n_b_sim 29.17 = 20 x 1.5^((0.80-0.733)/(0.805-0.733))).
MC se of the crossing by the delta method from the local slope. Tolerance = max(10 %, 2 MC se).

| member | arm | analytic | reported sim | censored rep | mine grid-matched | mine refined | MC se (n) | rel diff grid-matched % | rel diff refined % | tolerance % | verdict | rule outcome mine (refined) vs rep chosen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-H4 rth leg | a | 95 | 98.08 | False | 98.20 | 98.51 | 1.15 | 0.1 | 0.4 | 10.0 | consistent | within_band -> 95 vs rep 95 |
| A-H4 rth leg | b | 38 | 29.17 | False | 29.22 | 29.71 | 1.88 | 0.2 | 1.9 | 12.9 | consistent | smaller_ignored -> 38 vs rep 38 |
| G3.RTH.5 | a | 492 | 517.94 | False | 498.97 | 498.97 | 3.80 | -3.7 | -3.7 | 10.0 | consistent | within_band -> 492 vs rep 492 |
| G3.RTH.5 | b | 193 | 181.66 | False | 180.39 | 184.99 | 4.66 | -0.7 | 1.8 | 10.0 | consistent | within_band -> 193 vs rep 193 |
| F1_1_h1_RTH | a | 1447 | 1,469.69 | False | 1,416.34 | 1,417.71 | 23.97 | -3.6 | -3.5 | 10.0 | consistent | within_band -> 1447 vs rep 1447 |
| F1_1_h1_RTH | b | 566 | 570.57 | False | 553.54 | 553.54 | 16.61 | -3.0 | -3.0 | 10.0 | consistent | within_band -> 566 vs rep 566 |
| F2_4_15min_vol_tercile_top | a | 436 | 458.46 | False | 463.10 | 460.04 | 8.90 | 1.0 | 0.3 | 10.0 | consistent | within_band -> 436 vs rep 436 |
| F2_4_15min_vol_tercile_top | b | 171 | 152.29 | False | 155.96 | 157.93 | 5.04 | 2.4 | 3.7 | 10.0 | consistent | within_band -> 171 vs rep 171 |
| E-H1 scheduled macro drift | a | 11 | 4.00 | True | 4.00 (cens) | 4.00 (cens) | - | 0.0 | 0.0 | - | consistent (both censored at grid floor) | censored -> 11 vs rep 11 |
| E-H1 scheduled macro drift | b | 4 | 4.00 | True | 4.00 (cens) | 4.00 (cens) | - | 0.0 | 0.0 | - | consistent (both censored at grid floor) | censored -> 4 vs rep 4 |
| C-H4 passive-fill reversal | a | 116 | 122.15 | False | 123.55 | 123.95 | 2.75 | 1.2 | 1.5 | 10.0 | consistent | within_band -> 116 vs rep 116 |
| C-H4 passive-fill reversal | b | 46 | 41.97 | False | 42.41 | 42.84 | 1.19 | 1.1 | 2.1 | 10.0 | consistent | within_band -> 46 vs rep 46 |
| E-H3 quarterly witching short | a | 1 | 2.00 | True | 2.00 (cens) | 2.00 (cens) | - | 0.0 | 0.0 | - | consistent (both censored at grid floor) | censored -> 1 vs rep 1 |
| E-H3 quarterly witching short | b | 1 | 2.00 | True | 2.00 (cens) | 2.00 (cens) | - | 0.0 | 0.0 | - | consistent (both censored at grid floor) | censored -> 1 vs rep 1 |
| C-H1 magnitude-conditioned reversal | a | 119 | 119.12 | False | 118.79 | 118.78 | 2.15 | -0.3 | -0.3 | 10.0 | consistent | within_band -> 119 vs rep 119 |
| C-H1 magnitude-conditioned reversal | b | 47 | 48.06 | False | 47.12 | 47.11 | 2.09 | -2.0 | -2.0 | 10.0 | consistent | within_band -> 47 vs rep 47 |
| F3_2_bucket04_bucket05 | a | 42 | 36.80 | False | 36.24 | 37.52 | 0.60 | -1.5 | 2.0 | 10.0 | consistent | within_band -> 42 vs rep 42 |
| F3_2_bucket04_bucket05 | b | 17 | 14.68 | False | 14.15 | 13.96 | 0.50 | -3.6 | -4.9 | 10.0 | consistent | smaller_ignored -> 17 vs rep 17 |
| G1.RTH.5 | a | 68 | 73.77 | False | 73.51 | 74.00 | 1.47 | -0.3 | 0.3 | 10.0 | consistent | within_band -> 68 vs rep 68 |
| G1.RTH.5 | b | 27 | 25.50 | False | 24.18 | 24.01 | 0.80 | -5.2 | -5.8 | 10.0 | consistent | within_band -> 27 vs rep 27 |
| G4.RTH.30 | a | 38 | 53.75 | False | 54.06 | 52.27 | 1.41 | 0.6 | -2.8 | 10.0 | consistent | used_larger -> 53 vs rep 54 |
| G4.RTH.30 | b | 15 | 12.14 | False | 12.51 | 11.47 | 0.50 | 3.1 | -5.5 | 10.0 | consistent | smaller_ignored -> 15 vs rep 15 |
| F4_4_round_number_multiples_of_100 | a | 117 | 98.52 | False | 100.86 | 98.94 | 1.42 | 2.4 | 0.4 | 10.0 | consistent | smaller_ignored -> 117 vs rep 117 |
| F4_4_round_number_multiples_of_100 | b | 46 | 54.50 | False | 51.98 | 52.70 | 2.29 | -4.6 | -3.3 | 10.0 | consistent | within_band -> 46 vs rep 55 |
| G1.RTH.15 | a | 224 | 266.60 | False | 256.72 | 266.25 | 6.91 | -3.7 | -0.1 | 10.0 | consistent | used_larger -> 267 vs rep 267 |
| G1.RTH.15 | b | 88 | 62.28 | False | 63.50 | 62.10 | 1.64 | 2.0 | -0.3 | 10.0 | consistent | smaller_ignored -> 88 vs rep 88 |

All 26 arm-checks are "consistent": the grid-matched estimates sit within 5.2 % of the reported
figures (median |diff| 1.6 %), all censored cases are censored in my run too (E-H1 both arms at the
grid floor 4; E-H3 both arms at 2), and the re-derived rule outcome matches the reported chosen figure
in 25 of 26 cases. The 26th is F4_4 x100 arm b: the reported simulated n_b (54.50, +18.5 % over the
analytic 46) triggered `sim_used_larger_b` -> 55; my estimates are 51.98 grid-matched (+13.0 %) and
52.70 refined (+14.6 %), which fall inside the 15 % band and would keep 46. The two estimates are the
same quantity within MC noise (0.8 to 1.1 se), so the flag is seed-sensitive at this member: the
threshold is hard and the true excess sits near 15 %. The reported outcome is the conservative one
(more days) and F4_4 x100 is not binding for C2 (G3.RTH.5 at 193 is), so nothing downstream changes.
G4.RTH.30 arm a re-derives to 53 versus the reported 54 (ceil of 52.27 versus 53.75), a one-day
difference inside the tolerance.

Power at the reported chosen n, mine versus the reported curve (binomial se about 0.009):

| member | n (chosen_b) | rep power_b | mine power_b | n (chosen_a) | rep power_a | mine power_a | zero-var draws mine (all lengths) | rep sim_zero_variance_draws |
|---|---|---|---|---|---|---|---|---|
| A-H4 rth leg | 38 | 0.8150 | 0.8390 | 95 | 0.7810 | 0.7735 | 0 | 0 |
| G3.RTH.5 | 193 | 0.8245 | 0.8260 | 492 | 0.7725 | 0.7830 | 0 | 0 |
| F1_1_h1_RTH | 566 | 0.7975 | 0.8070 | 1447 | 0.7920 | 0.8140 | 0 | 0 |
| F2_4_15min_vol_tercile_top | 171 | 0.8460 | 0.8260 | 436 | 0.7780 | 0.7705 | 0 | 0 |
| E-H1 scheduled macro drift | 4 | 0.9260 | 0.9070 | 11 | 0.8640 | 0.8825 | 1231 | 1249 |
| C-H4 passive-fill reversal | 46 | 0.8295 | 0.8305 | 116 | 0.7755 | 0.7735 | 0 | 0 |
| E-H3 quarterly witching short | 2 | 1.0000 | 1.0000 | 2 | 1.0000 | 1.0000 | 3781 | 3763 |
| C-H1 magnitude-conditioned reversal | 47 | 0.7910 | 0.7995 | 119 | 0.7995 | 0.8010 | 0 | 0 |
| F3_2_bucket04_bucket05 | 17 | 0.8235 | 0.8330 | 42 | 0.8855 | 0.8920 | 0 | 0 |
| G1.RTH.5 | 27 | 0.8205 | 0.8325 | 68 | 0.7705 | 0.7630 | 0 | 0 |
| G4.RTH.30 | 15 | 0.8410 | 0.8445 | 54 | - | 0.8205 | 85 | 0 |
| F4_4_round_number_multiples_of_100 | 55 | - | 0.8065 | 117 | 0.8795 | 0.8955 | 0 | 0 |
| G1.RTH.15 | 88 | 0.9120 | 0.9200 | 267 | - | 0.8010 | 33 | 29 |

Zero-variance draws: on the code's own grid my counts are 0 for G4.RTH.30 (reported 0), 33 for
G1.RTH.15 (reported 29), 1,231 for E-H1 (reported 1,249), 3,781 for E-H3 (reported 3,763): MC agreement.
(My 85 for G4.RTH.30 in the main table arose only at my extra length n = 9, below the code's grid.)

### 3.2 The chosen-figure rule on every member (lead's correction 1)
Rule verified on all 95 measured members x 2 arms = 190 cases: chosen = analytic unless
|sim - analytic|/analytic > 15 %, then chosen = max(analytic, ceil(sim)); `sim_used_larger_x` when the
simulation won, `sim_smaller_ignored_x` when it lost, `sim_censored_below_grid_x` keeps the analytic
figure; diff_pct = (sim - analytic)/analytic x 100 reproduced to 1e-6 on every row. Outcome counts:
within band 123 (chosen = analytic, no flag), censored 42 (10 a, 32 b; analytic kept), smaller_ignored
17 (6 a, 11 b), used_larger 8 (5 a: G1.RTH.15 224->267, G4.RTH.15 100->122, G4.RTH.30 38->54,
G1.ETH.60 45->53, G4.RTH.60 48->57; 3 b: F4_4 x100 46->55, G4.RTH.5 46->55, G1.ETH.15 50->59).
The ceil is applied to the exact simulated value (G4.RTH.5 b 54.024 -> 55; G4.RTH.60 a 56.023 -> 57),
which the md's one-decimal column hides. No violation.

| member | arm | analytic | sim | diff rep | diff mine | censored flag | chosen rep | chosen by rule | flags rep | rule outcome | ok |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | a | 4 | 2.3764 | -40.589 | -40.589 | False | 4 | 4 | sim_smaller_ignored_a | smaller_ignored | ok |
| A-H1 european-open overnight drift | b | 2 | 2.0000 | 0.000 | 0.000 | True | 2 | 2 | sim_censored_below_grid_b | censored | ok |
| A-H2 rth close window (buy) | a | 9 | 9.7428 | 8.253 | 8.253 | False | 9 | 9 | - | within_band | ok |
| A-H2 rth close window (buy) | b | 4 | 4.0000 | 0.000 | 0.000 | True | 4 | 4 | sim_censored_below_grid_b | censored | ok |
| A-H2 rth close window (sell) | a | 9 | 9.0237 | 0.264 | 0.264 | False | 9 | 9 | - | within_band | ok |
| A-H2 rth close window (sell) | b | 4 | 4.0000 | 0.000 | 0.000 | True | 4 | 4 | sim_censored_below_grid_b | censored | ok |
| A-H3 weekend effect | a | 52 | 58.1316 | 11.792 | 11.792 | False | 52 | 52 | - | within_band | ok |
| A-H3 weekend effect | b | 21 | 15.7428 | -25.034 | -25.034 | False | 21 | 21 | sim_smaller_ignored_b | smaller_ignored | ok |
| A-H4 eth leg | a | 56 | 60.8748 | 8.705 | 8.705 | False | 56 | 56 | - | within_band | ok |
| A-H4 eth leg | b | 22 | 20.8994 | -5.003 | -5.003 | False | 22 | 22 | - | within_band | ok |
| A-H4 rth leg | a | 95 | 98.0846 | 3.247 | 3.247 | False | 95 | 95 | - | within_band | ok |
| A-H4 rth leg | b | 38 | 29.1671 | -23.245 | -23.245 | False | 38 | 38 | sim_smaller_ignored_b | smaller_ignored | ok |
| B-H1 opening-range breakout (hold 5) | a | 3 | 2.0000 | -33.333 | -33.333 | True | 3 | 3 | sim_censored_below_grid_a | censored | ok |
| B-H1 opening-range breakout (hold 5) | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| B-H1 opening-range breakout (hold 75) | a | 30 | 30.6412 | 2.137 | 2.137 | False | 30 | 30 | - | within_band | ok |
| B-H1 opening-range breakout (hold 75) | b | 12 | 11.3735 | -5.221 | -5.221 | False | 12 | 12 | - | within_band | ok |
| B-H2 prior-day stop cascade | a | 6 | 5.4512 | -9.147 | -9.147 | False | 6 | 6 | - | within_band | ok |
| B-H2 prior-day stop cascade | b | 3 | 3.0000 | 0.000 | 0.000 | True | 3 | 3 | sim_censored_below_grid_b | censored | ok |
| B-H3 breakout leg | a | 10 | 10.1149 | 1.149 | 1.149 | False | 10 | 10 | - | within_band | ok |
| B-H3 breakout leg | b | 4 | 4.0000 | 0.000 | 0.000 | True | 4 | 4 | sim_censored_below_grid_b | censored | ok |
| B-H3 fade leg | a | 10 | 9.5511 | -4.489 | -4.489 | False | 10 | 10 | - | within_band | ok |
| B-H3 fade leg | b | 4 | 4.0000 | 0.000 | 0.000 | True | 4 | 4 | sim_censored_below_grid_b | censored | ok |
| B-H4 narrow-range breakout | a | 2 | 2.0000 | 0.000 | 0.000 | True | 2 | 2 | sim_censored_below_grid_a | censored | ok |
| B-H4 narrow-range breakout | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| C-H1 magnitude-conditioned reversal | a | 119 | 119.1242 | 0.104 | 0.104 | False | 119 | 119 | - | within_band | ok |
| C-H1 magnitude-conditioned reversal | b | 47 | 48.0587 | 2.253 | 2.253 | False | 47 | 47 | - | within_band | ok |
| C-H2 post-spike exhaustion fade | a | 35 | 31.3641 | -10.388 | -10.388 | False | 35 | 35 | - | within_band | ok |
| C-H2 post-spike exhaustion fade | b | 14 | 10.0000 | -28.571 | -28.571 | True | 14 | 14 | sim_censored_below_grid_b | censored | ok |
| C-H3 close-location-value reversal | a | 37 | 24.6266 | -33.442 | -33.442 | False | 37 | 37 | sim_smaller_ignored_a | smaller_ignored | ok |
| C-H3 close-location-value reversal | b | 15 | 10.0000 | -33.333 | -33.333 | True | 15 | 15 | sim_censored_below_grid_b | censored | ok |
| D-H1 trailing-vol regime gate | a | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_a | censored | ok |
| D-H1 trailing-vol regime gate | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| D-H2 inverse-vol sizing | a | 9 | 9.7946 | 8.829 | 8.829 | False | 9 | 9 | - | within_band | ok |
| D-H2 inverse-vol sizing | b | 4 | 4.0000 | 0.000 | 0.000 | True | 4 | 4 | sim_censored_below_grid_b | censored | ok |
| D-H3 range-compression gate | a | 14 | 13.8689 | -0.937 | -0.937 | False | 14 | 14 | - | within_band | ok |
| D-H3 range-compression gate | b | 6 | 6.0000 | 0.000 | 0.000 | True | 6 | 6 | sim_censored_below_grid_b | censored | ok |
| D-H4 overnight gap fade | a | 2 | 2.0000 | 0.000 | 0.000 | True | 2 | 2 | sim_censored_below_grid_a | censored | ok |
| D-H4 overnight gap fade | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| E-H1 scheduled macro drift | a | 11 | 4.0000 | -63.636 | -63.636 | True | 11 | 11 | sim_censored_below_grid_a | censored | ok |
| E-H1 scheduled macro drift | b | 4 | 4.0000 | 0.000 | 0.000 | True | 4 | 4 | sim_censored_below_grid_b | censored | ok |
| E-H2 post-release momentum | a | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_a | censored | ok |
| E-H2 post-release momentum | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| E-H3 quarterly witching short | a | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_a | censored | ok |
| E-H3 quarterly witching short | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| E-H4 turn-of-month long | a | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_a | censored | ok |
| E-H4 turn-of-month long | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| C-H4 passive-fill reversal | a | 116 | 122.1451 | 5.298 | 5.298 | False | 116 | 116 | - | within_band | ok |
| C-H4 passive-fill reversal | b | 46 | 41.9692 | -8.763 | -8.763 | False | 46 | 46 | - | within_band | ok |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | a | 3 | 2.0000 | -33.333 | -33.333 | True | 3 | 3 | sim_censored_below_grid_a | censored | ok |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | a | 44 | 49.1201 | 11.637 | 11.637 | False | 44 | 44 | - | within_band | ok |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | b | 17 | 10.4086 | -38.773 | -38.773 | False | 17 | 17 | sim_smaller_ignored_b | smaller_ignored | ok |
| RT3 B-H3 breakout leg 5-min bars | a | 13 | 9.6659 | -25.647 | -25.647 | False | 13 | 13 | sim_smaller_ignored_a | smaller_ignored | ok |
| RT3 B-H3 breakout leg 5-min bars | b | 5 | 5.0000 | 0.000 | 0.000 | True | 5 | 5 | sim_censored_below_grid_b | censored | ok |
| RT4 B-H3 fade leg 5-min bars | a | 13 | 9.9068 | -23.794 | -23.794 | False | 13 | 13 | sim_smaller_ignored_a | smaller_ignored | ok |
| RT4 B-H3 fade leg 5-min bars | b | 5 | 5.0000 | 0.000 | 0.000 | True | 5 | 5 | sim_censored_below_grid_b | censored | ok |
| RT5 C-H2 spike fade 5-min bars | a | 16 | 14.0637 | -12.102 | -12.102 | False | 16 | 16 | - | within_band | ok |
| RT5 C-H2 spike fade 5-min bars | b | 6 | 6.0000 | 0.000 | 0.000 | True | 6 | 6 | sim_censored_below_grid_b | censored | ok |
| RT6 D-H1 daily-vol regime gate | a | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_a | censored | ok |
| RT6 D-H1 daily-vol regime gate | b | 1 | 2.0000 | 100.000 | 100.000 | True | 1 | 1 | sim_censored_below_grid_b | censored | ok |
| RT7 D-H2 daily-vol sizing | a | 4 | 2.6664 | -33.340 | -33.340 | False | 4 | 4 | sim_smaller_ignored_a | smaller_ignored | ok |
| RT7 D-H2 daily-vol sizing | b | 2 | 2.0000 | 0.000 | 0.000 | True | 2 | 2 | sim_censored_below_grid_b | censored | ok |
| F3_2_bucket07_bucket08 | a | 26 | 23.3400 | -10.231 | -10.231 | False | 26 | 26 | - | within_band | ok |
| F3_2_bucket07_bucket08 | b | 10 | 10.0000 | 0.000 | 0.000 | True | 10 | 10 | sim_censored_below_grid_b | censored | ok |
| F6_1_overnight_range_position | a | 140 | 147.6966 | 5.498 | 5.498 | False | 140 | 140 | - | within_band | ok |
| F6_1_overnight_range_position | b | 55 | 51.4880 | -6.385 | -6.385 | False | 55 | 55 | - | within_band | ok |
| F3_3_opening_30min_to_close_momentum | a | 28 | 28.4289 | 1.532 | 1.532 | False | 28 | 28 | - | within_band | ok |
| F3_3_opening_30min_to_close_momentum | b | 11 | 10.6772 | -2.935 | -2.935 | False | 11 | 11 | - | within_band | ok |
| F3_2_bucket08_bucket09 | a | 22 | 19.6848 | -10.524 | -10.524 | False | 22 | 22 | - | within_band | ok |
| F3_2_bucket08_bucket09 | b | 9 | 9.0000 | 0.000 | 0.000 | True | 9 | 9 | sim_censored_below_grid_b | censored | ok |
| F3_3_overnight_to_close_momentum | a | 28 | 29.9220 | 6.864 | 6.864 | False | 28 | 28 | - | within_band | ok |
| F3_3_overnight_to_close_momentum | b | 11 | 10.2444 | -6.869 | -6.869 | False | 11 | 11 | - | within_band | ok |
| F4_4_round_number_multiples_of_100 | a | 117 | 98.5219 | -15.793 | -15.793 | False | 117 | 117 | sim_smaller_ignored_a | smaller_ignored | ok |
| F4_4_round_number_multiples_of_100 | b | 46 | 54.5004 | 18.479 | 18.479 | False | 55 | 55 | sim_used_larger_b | used_larger | ok |
| F3_2_bucket01_bucket02 | a | 59 | 62.2404 | 5.492 | 5.492 | False | 59 | 59 | - | within_band | ok |
| F3_2_bucket01_bucket02 | b | 24 | 22.5720 | -5.950 | -5.950 | False | 24 | 24 | - | within_band | ok |
| F3_2_bucket10_bucket11 | a | 19 | 18.6819 | -1.674 | -1.674 | False | 19 | 19 | - | within_band | ok |
| F3_2_bucket10_bucket11 | b | 8 | 8.9978 | 12.472 | 12.472 | False | 8 | 8 | - | within_band | ok |
| F4_1_rth_open_crossing | a | 51 | 55.2331 | 8.300 | 8.300 | False | 51 | 51 | - | within_band | ok |
| F4_1_rth_open_crossing | b | 20 | 16.6598 | -16.701 | -16.701 | False | 20 | 20 | sim_smaller_ignored_b | smaller_ignored | ok |
| F3_2_bucket02_bucket03 | a | 59 | 56.7649 | -3.788 | -3.788 | False | 59 | 59 | - | within_band | ok |
| F3_2_bucket02_bucket03 | b | 24 | 22.4645 | -6.398 | -6.398 | False | 24 | 24 | - | within_band | ok |
| F3_2_bucket05_bucket06 | a | 23 | 22.8776 | -0.532 | -0.532 | False | 23 | 23 | - | within_band | ok |
| F3_2_bucket05_bucket06 | b | 9 | 9.0000 | 0.000 | 0.000 | True | 9 | 9 | sim_censored_below_grid_b | censored | ok |
| F3_2_bucket04_bucket05 | a | 42 | 36.7964 | -12.389 | -12.389 | False | 42 | 42 | - | within_band | ok |
| F3_2_bucket04_bucket05 | b | 17 | 14.6766 | -13.667 | -13.667 | False | 17 | 17 | - | within_band | ok |
| F3_2_bucket06_bucket07 | a | 21 | 22.4958 | 7.123 | 7.123 | False | 21 | 21 | - | within_band | ok |
| F3_2_bucket06_bucket07 | b | 8 | 8.4696 | 5.870 | 5.870 | False | 8 | 8 | - | within_band | ok |
| F3_2_bucket12_bucket13 | a | 26 | 25.2060 | -3.054 | -3.054 | False | 26 | 26 | - | within_band | ok |
| F3_2_bucket12_bucket13 | b | 11 | 11.4137 | 3.761 | 3.761 | False | 11 | 11 | - | within_band | ok |
| G2.RTH.30 | a | 54 | 47.8964 | -11.303 | -11.303 | False | 54 | 54 | - | within_band | ok |
| G2.RTH.30 | b | 21 | 22.7418 | 8.294 | 8.294 | False | 21 | 21 | - | within_band | ok |
| G1.RTH.5 | a | 68 | 73.7682 | 8.483 | 8.483 | False | 68 | 68 | - | within_band | ok |
| G1.RTH.5 | b | 27 | 25.4982 | -5.562 | -5.562 | False | 27 | 27 | - | within_band | ok |
| G2.ETH.30 | a | 44 | 40.3100 | -8.386 | -8.386 | False | 44 | 44 | - | within_band | ok |
| G2.ETH.30 | b | 17 | 17.2172 | 1.278 | 1.278 | False | 17 | 17 | - | within_band | ok |
| G2.ETH.5 | a | 21 | 22.3915 | 6.626 | 6.626 | False | 21 | 21 | - | within_band | ok |
| G2.ETH.5 | b | 9 | 9.0000 | 0.000 | 0.000 | True | 9 | 9 | sim_censored_below_grid_b | censored | ok |
| G5.RTH.15 | a | 22 | 20.5602 | -6.544 | -6.544 | False | 22 | 22 | - | within_band | ok |
| G5.RTH.15 | b | 9 | 9.0000 | 0.000 | 0.000 | True | 9 | 9 | sim_censored_below_grid_b | censored | ok |
| G5.RTH.30 | a | 29 | 29.1879 | 0.648 | 0.648 | False | 29 | 29 | - | within_band | ok |
| G5.RTH.30 | b | 12 | 12.6808 | 5.674 | 5.674 | False | 12 | 12 | - | within_band | ok |
| G3.RTH.15 | a | 345 | 323.2507 | -6.304 | -6.304 | False | 345 | 345 | - | within_band | ok |
| G3.RTH.15 | b | 135 | 141.6226 | 4.906 | 4.906 | False | 135 | 135 | - | within_band | ok |
| F1_1_h1_RTH | a | 1447 | 1,469.6851 | 1.568 | 1.568 | False | 1447 | 1447 | - | within_band | ok |
| F1_1_h1_RTH | b | 566 | 570.5703 | 0.807 | 0.807 | False | 566 | 566 | - | within_band | ok |
| F1_1_h5_RTH | a | 304 | 316.2933 | 4.044 | 4.044 | False | 304 | 304 | - | within_band | ok |
| F1_1_h5_RTH | b | 119 | 118.1546 | -0.710 | -0.710 | False | 119 | 119 | - | within_band | ok |
| F1_1_h15_RTH | a | 580 | 603.4929 | 4.050 | 4.050 | False | 580 | 580 | - | within_band | ok |
| F1_1_h15_RTH | b | 227 | 219.3216 | -3.383 | -3.383 | False | 227 | 227 | - | within_band | ok |
| F1_1_h30_RTH | a | 408 | 400.0284 | -1.954 | -1.954 | False | 408 | 408 | - | within_band | ok |
| F1_1_h30_RTH | b | 160 | 158.4363 | -0.977 | -0.977 | False | 160 | 160 | - | within_band | ok |
| F1_1_h60_RTH | a | 283 | 273.8700 | -3.226 | -3.226 | False | 283 | 283 | - | within_band | ok |
| F1_1_h60_RTH | b | 111 | 106.7552 | -3.824 | -3.824 | False | 111 | 111 | - | within_band | ok |
| F1_1_h1_ETH | a | 574 | 589.2230 | 2.652 | 2.652 | False | 574 | 574 | - | within_band | ok |
| F1_1_h1_ETH | b | 225 | 213.4283 | -5.143 | -5.143 | False | 225 | 225 | - | within_band | ok |
| F1_1_h5_ETH | a | 330 | 329.0671 | -0.283 | -0.283 | False | 330 | 330 | - | within_band | ok |
| F1_1_h5_ETH | b | 130 | 128.6876 | -1.010 | -1.010 | False | 130 | 130 | - | within_band | ok |
| F1_1_h15_ETH | a | 242 | 264.2457 | 9.192 | 9.192 | False | 242 | 242 | - | within_band | ok |
| F1_1_h15_ETH | b | 95 | 84.3507 | -11.210 | -11.210 | False | 95 | 95 | - | within_band | ok |
| F1_1_h30_ETH | a | 275 | 268.3114 | -2.432 | -2.432 | False | 275 | 275 | - | within_band | ok |
| F1_1_h30_ETH | b | 108 | 112.7573 | 4.405 | 4.405 | False | 108 | 108 | - | within_band | ok |
| F1_1_h60_ETH | a | 337 | 329.2518 | -2.299 | -2.299 | False | 337 | 337 | - | within_band | ok |
| F1_1_h60_ETH | b | 132 | 134.3481 | 1.779 | 1.779 | False | 132 | 132 | - | within_band | ok |
| F2_4_15min_vol_tercile_bottom | a | 44 | 46.3084 | 5.246 | 5.246 | False | 44 | 44 | - | within_band | ok |
| F2_4_15min_vol_tercile_bottom | b | 18 | 15.7915 | -12.269 | -12.269 | False | 18 | 18 | - | within_band | ok |
| F2_4_15min_vol_tercile_top | a | 436 | 458.4554 | 5.150 | 5.150 | False | 436 | 436 | - | within_band | ok |
| F2_4_15min_vol_tercile_top | b | 171 | 152.2850 | -10.944 | -10.944 | False | 171 | 171 | - | within_band | ok |
| F3_2_bucket03_bucket04 | a | 24 | 26.9988 | 12.495 | 12.495 | False | 24 | 24 | - | within_band | ok |
| F3_2_bucket03_bucket04 | b | 10 | 10.0000 | 0.000 | 0.000 | True | 10 | 10 | sim_censored_below_grid_b | censored | ok |
| F3_2_bucket09_bucket10 | a | 18 | 18.4729 | 2.627 | 2.627 | False | 18 | 18 | - | within_band | ok |
| F3_2_bucket09_bucket10 | b | 8 | 8.2292 | 2.865 | 2.865 | False | 8 | 8 | - | within_band | ok |
| F3_2_bucket11_bucket12 | a | 22 | 20.5136 | -6.756 | -6.756 | False | 22 | 22 | - | within_band | ok |
| F3_2_bucket11_bucket12 | b | 9 | 9.0000 | 0.000 | 0.000 | True | 9 | 9 | sim_censored_below_grid_b | censored | ok |
| F4_2_prior_rth_close_crossing | a | 32 | 33.3915 | 4.348 | 4.348 | False | 32 | 32 | - | within_band | ok |
| F4_2_prior_rth_close_crossing | b | 13 | 12.6408 | -2.763 | -2.763 | False | 13 | 13 | - | within_band | ok |
| F4_4_round_number_multiples_of_50 | a | 139 | 140.7392 | 1.251 | 1.251 | False | 139 | 139 | - | within_band | ok |
| F4_4_round_number_multiples_of_50 | b | 55 | 53.2801 | -3.127 | -3.127 | False | 55 | 55 | - | within_band | ok |
| F5_1_relvol_tercile_bottom | a | 61 | 60.5303 | -0.770 | -0.770 | False | 61 | 61 | - | within_band | ok |
| F5_1_relvol_tercile_bottom | b | 24 | 24.5989 | 2.496 | 2.496 | False | 24 | 24 | - | within_band | ok |
| F5_1_relvol_tercile_top | a | 135 | 141.1148 | 4.530 | 4.530 | False | 135 | 135 | - | within_band | ok |
| F5_1_relvol_tercile_top | b | 53 | 48.2715 | -8.922 | -8.922 | False | 53 | 53 | - | within_band | ok |
| F5_2_efficiency_tercile_bottom | a | 116 | 110.9012 | -4.395 | -4.395 | False | 116 | 116 | - | within_band | ok |
| F5_2_efficiency_tercile_bottom | b | 45 | 47.0094 | 4.465 | 4.465 | False | 45 | 45 | - | within_band | ok |
| F5_2_efficiency_tercile_top | a | 125 | 138.0431 | 10.434 | 10.434 | False | 125 | 125 | - | within_band | ok |
| F5_2_efficiency_tercile_top | b | 49 | 44.2611 | -9.671 | -9.671 | False | 49 | 49 | - | within_band | ok |
| F5_3_range_volume_residual | a | 255 | 258.0972 | 1.215 | 1.215 | False | 255 | 255 | - | within_band | ok |
| F5_3_range_volume_residual | b | 100 | 99.2575 | -0.743 | -0.743 | False | 100 | 100 | - | within_band | ok |
| G1.ETH.5 | a | 305 | 328.8645 | 7.824 | 7.824 | False | 305 | 305 | - | within_band | ok |
| G1.ETH.5 | b | 120 | 105.1631 | -12.364 | -12.364 | False | 120 | 120 | - | within_band | ok |
| G2.RTH.5 | a | 47 | 43.5818 | -7.273 | -7.273 | False | 47 | 47 | - | within_band | ok |
| G2.RTH.5 | b | 19 | 20.8276 | 9.619 | 9.619 | False | 19 | 19 | - | within_band | ok |
| G3.RTH.5 | a | 492 | 517.9434 | 5.273 | 5.273 | False | 492 | 492 | - | within_band | ok |
| G3.RTH.5 | b | 193 | 181.6620 | -5.875 | -5.875 | False | 193 | 193 | - | within_band | ok |
| G4.RTH.5 | a | 116 | 104.1605 | -10.206 | -10.206 | False | 116 | 116 | - | within_band | ok |
| G4.RTH.5 | b | 46 | 54.0241 | 17.444 | 17.444 | False | 55 | 55 | sim_used_larger_b | used_larger | ok |
| G5.RTH.5 | a | 10 | 9.9675 | -0.325 | -0.325 | False | 10 | 10 | - | within_band | ok |
| G5.RTH.5 | b | 4 | 4.0000 | 0.000 | 0.000 | True | 4 | 4 | sim_censored_below_grid_b | censored | ok |
| G1.ETH.15 | a | 128 | 115.6101 | -9.680 | -9.680 | False | 128 | 128 | - | within_band | ok |
| G1.ETH.15 | b | 50 | 58.5127 | 17.025 | 17.025 | False | 59 | 59 | sim_used_larger_b | used_larger | ok |
| G2.ETH.15 | a | 46 | 43.7000 | -5.000 | -5.000 | False | 46 | 46 | - | within_band | ok |
| G2.ETH.15 | b | 18 | 14.1518 | -21.379 | -21.379 | False | 18 | 18 | sim_smaller_ignored_b | smaller_ignored | ok |
| G1.RTH.15 | a | 224 | 266.6027 | 19.019 | 19.019 | False | 267 | 267 | sim_used_larger_a | used_larger | ok |
| G1.RTH.15 | b | 88 | 62.2774 | -29.230 | -29.230 | False | 88 | 88 | sim_smaller_ignored_b | smaller_ignored | ok |
| G2.RTH.15 | a | 74 | 80.6415 | 8.975 | 8.975 | False | 74 | 74 | - | within_band | ok |
| G2.RTH.15 | b | 29 | 26.8692 | -7.348 | -7.348 | False | 29 | 29 | - | within_band | ok |
| G4.RTH.15 | a | 100 | 121.0858 | 21.086 | 21.086 | False | 122 | 122 | sim_used_larger_a | used_larger | ok |
| G4.RTH.15 | b | 39 | 27.8638 | -28.554 | -28.554 | False | 39 | 39 | sim_smaller_ignored_b | smaller_ignored | ok |
| G1.ETH.30 | a | 58 | 66.4292 | 14.533 | 14.533 | False | 58 | 58 | - | within_band | ok |
| G1.ETH.30 | b | 23 | 18.7329 | -18.553 | -18.553 | False | 23 | 23 | sim_smaller_ignored_b | smaller_ignored | ok |
| G1.RTH.30 | a | 65 | 66.6525 | 2.542 | 2.542 | False | 65 | 65 | - | within_band | ok |
| G1.RTH.30 | b | 26 | 23.3947 | -10.020 | -10.020 | False | 26 | 26 | - | within_band | ok |
| G3.RTH.30 | a | 154 | 151.0523 | -1.914 | -1.914 | False | 154 | 154 | - | within_band | ok |
| G3.RTH.30 | b | 61 | 61.2383 | 0.391 | 0.391 | False | 61 | 61 | - | within_band | ok |
| G4.RTH.30 | a | 38 | 53.7519 | 41.452 | 41.452 | False | 54 | 54 | sim_used_larger_a | used_larger | ok |
| G4.RTH.30 | b | 15 | 12.1372 | -19.085 | -19.085 | False | 15 | 15 | sim_smaller_ignored_b | smaller_ignored | ok |
| G1.ETH.60 | a | 45 | 52.5995 | 16.888 | 16.888 | False | 53 | 53 | sim_used_larger_a | used_larger | ok |
| G1.ETH.60 | b | 18 | 15.1819 | -15.656 | -15.656 | False | 18 | 18 | sim_smaller_ignored_b | smaller_ignored | ok |
| G2.ETH.60 | a | 37 | 40.0041 | 8.119 | 8.119 | False | 37 | 37 | - | within_band | ok |
| G2.ETH.60 | b | 15 | 12.0830 | -19.446 | -19.446 | False | 15 | 15 | sim_smaller_ignored_b | smaller_ignored | ok |
| G1.RTH.60 | a | 43 | 48.8157 | 13.525 | 13.525 | False | 43 | 43 | - | within_band | ok |
| G1.RTH.60 | b | 17 | 16.6793 | -1.887 | -1.887 | False | 17 | 17 | - | within_band | ok |
| G2.RTH.60 | a | 39 | 38.6374 | -0.930 | -0.930 | False | 39 | 39 | - | within_band | ok |
| G2.RTH.60 | b | 16 | 17.6489 | 10.306 | 10.306 | False | 16 | 16 | - | within_band | ok |
| G3.RTH.60 | a | 117 | 109.4191 | -6.479 | -6.479 | False | 117 | 117 | - | within_band | ok |
| G3.RTH.60 | b | 46 | 52.5794 | 14.303 | 14.303 | False | 46 | 46 | - | within_band | ok |
| G4.RTH.60 | a | 48 | 56.0233 | 16.715 | 16.715 | False | 57 | 57 | sim_used_larger_a | used_larger | ok |
| G4.RTH.60 | b | 19 | 19.4936 | 2.598 | 2.598 | False | 19 | 19 | - | within_band | ok |
| G5.RTH.60 | a | 68 | 64.4389 | -5.237 | -5.237 | False | 68 | 68 | - | within_band | ok |
| G5.RTH.60 | b | 27 | 28.6092 | 5.960 | 5.960 | False | 27 | 27 | - | within_band | ok |

Verdict: **VERIFIED WITH NOTES** (one seed-sensitive flag, conservative direction).

## 4. Family H projections

Proxy rule (coverage.md section 5): per-trade SD 100 (H1-H5) or 115 (H6); f = 1/4 x 0.9, 0.9/7,
1/4 x 0.9, 1/3 x 0.9, 1/3 x 0.9, 2/5 (no 0.9 factor for H6); SD_day = SD x sqrt(f); r = f; VIF 1; lag1 0.
All six rows reproduce exactly (n_a 31/18/31/42/42/73, n_b 13/7/13/17/17/29).

| member | SD_trade | f | SD_day rep | SD_day mine | r rep | r mine | n_a rep | mine | n_b rep | mine | eps/trade rep | mine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 NR4 opening-range breakout | 100.0 | 0.225000 | 47.4342 | 47.4342 | 0.225000 | 0.225000 | 31 | 31 | 13 | 13 | 151.111 | 151.111 |
| H2 NR7 opening-range breakout | 100.0 | 0.128571 | 35.8569 | 35.8569 | 0.128571 | 0.128571 | 18 | 18 | 7 | 7 | 264.444 | 264.444 |
| H3 inside-day opening-range breakout | 100.0 | 0.225000 | 47.4342 | 47.4342 | 0.225000 | 0.225000 | 31 | 31 | 13 | 13 | 151.111 | 151.111 |
| H4 bottom-tercile prior range, breakout | 100.0 | 0.300000 | 54.7723 | 54.7723 | 0.300000 | 0.300000 | 42 | 42 | 17 | 17 | 113.333 | 113.333 |
| H5 top-tercile prior range, opening-range fade | 100.0 | 0.300000 | 54.7723 | 54.7723 | 0.300000 | 0.300000 | 42 | 42 | 17 | 17 | 113.333 | 113.333 |
| H6 prior-close location follow-through | 115.0 | 0.400000 | 72.7324 | 72.7324 | 0.400000 | 0.400000 | 73 | 73 | 29 | 29 | 85.000 | 85.000 |

Verdict: **VERIFIED**.

## 5. Class tables

`typical_r` = median of r over the class's TRIAL members (C7: median firing fraction over the six H
rows); `eps_trade` = 34/typical_r; `gross_equivalent_trade` = eps_trade + 2.11; binding_a/b = the member
with the largest chosen_a / chosen_b in the class; `null_power_achievable_at[S]` = supplied_days[S] >=
binding_b days; class member lists match coverage.md (C1 6, C2 31, C3 40, C4 13, C5 4, C6 1, C7 6; tiers
A 52 = 31 trials + 21 near-misses, B 43, H 6). All exact.

| class | n members | typical_r rep | mine | eps_trade rep | mine | gross rep | mine | binding_a rep | mine | binding_b rep | mine | achievable flags ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 6 | 0.937716 | 0.937716 | 36.2583 | 36.2583 | 38.3683 | 38.3683 | A-H4 rth leg (95) | A-H4 rth leg (95) | A-H4 rth leg (38) | A-H4 rth leg (38) | True |
| C2 | 31 | 0.944637 | 0.944637 | 35.9927 | 35.9927 | 38.1027 | 38.1027 | G3.RTH.5 (492) | G3.RTH.5 (492) | G3.RTH.5 (193) | G3.RTH.5 (193) | True |
| C3 | 40 | 36.150519 | 36.150519 | 0.9405 | 0.9405 | 3.0505 | 3.0505 | F1_1_h1_RTH (1447) | F1_1_h1_RTH (1447) | F1_1_h1_RTH (566) | F1_1_h1_RTH (566) | True |
| C4 | 13 | 0.676471 | 0.676471 | 50.2609 | 50.2609 | 52.3709 | 52.3709 | F2_4_15min_vol_tercile_top (436) | F2_4_15min_vol_tercile_top (436) | F2_4_15min_vol_tercile_top (171) | F2_4_15min_vol_tercile_top (171) | True |
| C5 | 4 | 0.096886 | 0.096886 | 350.9286 | 350.9286 | 353.0386 | 353.0386 | E-H1 scheduled macro drift (11) | E-H1 scheduled macro drift (11) | E-H1 scheduled macro drift (4) | E-H1 scheduled macro drift (4) | True |
| C6 | 1 | 92.467128 | 92.467128 | 0.3677 | 0.3677 | 2.4777 | 2.4777 | C-H4 passive-fill reversal (116) | C-H4 passive-fill reversal (116) | C-H4 passive-fill reversal (46) | C-H4 passive-fill reversal (46) | True |
| C7 | 6 | 0.262500 | 0.262500 | 129.5238 | 129.5238 | 131.6338 | 131.6338 | H6 prior-close location follow-through (73) | H6 prior-close location follow-through (73) | H6 prior-close location follow-through (29) | H6 prior-close location follow-through (29) | True |

Achievability, recomputed: every class achievable at every S except C3 (binding n_b 566) at 2022-01-03
(516 supplied) and 2023-01-03 (277), which the JSON flags `false` and the md marks "short". Under my
larger supplied-day recounts of section 6 (534 and 288 at most), C3 stays short at both starts.

### 5.1 `resolution_range` (lead's correction 3) and md section 5a-bis
Recomputed two ways for each class and each S: (i) min and max of the members' own
`eps_min_at_supplied` fields, over measured members (C7: over its projected rows), per trade and per
day; (ii) the same from my own eps_min = (z_95+z_b) SD sqrt(VIF)/sqrt(N). Member identities and values
match in all 42 class x S cells (values to 1e-6 %); `basis` and `members` fields correct. Section
5a-bis of the md (2019-05-06 and 2021-01-04 columns) matches the JSON.

| class | S | basis | min/trade rep | from rep fields | from mine | max/trade rep | from rep fields | from mine | min/day rep | mine | max/day rep | mine | ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 2019-05-06 | measured/6 vs measured/6 | 1.2266 (A-H1 european-open overnight drift) | 1.2266 (A-H1 european-open overnight drift) | 1.2266 (A-H1 european-open overnight drift) | 11.8097 (A-H3 weekend effect) | 11.8097 (A-H3 weekend effect) | 11.8097 (A-H3 weekend effect) | 1.1714 (A-H1 european-open overnight drift) | 1.1714 | 6.0984 (A-H4 rth leg) | 6.0984 | ok |
| C1 | 2019-07-01 | measured/6 vs measured/6 | 1.2468 (A-H1 european-open overnight drift) | 1.2468 (A-H1 european-open overnight drift) | 1.2468 (A-H1 european-open overnight drift) | 12.0042 (A-H3 weekend effect) | 12.0042 (A-H3 weekend effect) | 12.0042 (A-H3 weekend effect) | 1.1907 (A-H1 european-open overnight drift) | 1.1907 | 6.1989 (A-H4 rth leg) | 6.1989 | ok |
| C1 | 2020-01-02 | measured/6 vs measured/6 | 1.3213 (A-H1 european-open overnight drift) | 1.3213 (A-H1 european-open overnight drift) | 1.3213 (A-H1 european-open overnight drift) | 12.7210 (A-H3 weekend effect) | 12.7210 (A-H3 weekend effect) | 12.7210 (A-H3 weekend effect) | 1.2618 (A-H1 european-open overnight drift) | 1.2618 | 6.5690 (A-H4 rth leg) | 6.5690 | ok |
| C1 | 2021-01-04 | measured/6 vs measured/6 | 1.5145 (A-H1 european-open overnight drift) | 1.5145 (A-H1 european-open overnight drift) | 1.5145 (A-H1 european-open overnight drift) | 14.5815 (A-H3 weekend effect) | 14.5815 (A-H3 weekend effect) | 14.5815 (A-H3 weekend effect) | 1.4464 (A-H1 european-open overnight drift) | 1.4464 | 7.5298 (A-H4 rth leg) | 7.5298 | ok |
| C1 | 2022-01-03 | measured/6 vs measured/6 | 1.8320 (A-H1 european-open overnight drift) | 1.8320 (A-H1 european-open overnight drift) | 1.8320 (A-H1 european-open overnight drift) | 17.6381 (A-H3 weekend effect) | 17.6381 (A-H3 weekend effect) | 17.6381 (A-H3 weekend effect) | 1.7496 (A-H1 european-open overnight drift) | 1.7496 | 9.1082 (A-H4 rth leg) | 9.1082 | ok |
| C1 | 2023-01-03 | measured/6 vs measured/6 | 2.5004 (A-H1 european-open overnight drift) | 2.5004 (A-H1 european-open overnight drift) | 2.5004 (A-H1 european-open overnight drift) | 24.0734 (A-H3 weekend effect) | 24.0734 (A-H3 weekend effect) | 24.0734 (A-H3 weekend effect) | 2.3879 (A-H1 european-open overnight drift) | 2.3879 | 12.4313 (A-H4 rth leg) | 12.4313 | ok |
| C2 | 2019-05-06 | measured/31 vs measured/31 | 0.2998 (G2.ETH.5) | 0.2998 (G2.ETH.5) | 0.2998 (G2.ETH.5) | 13.9953 (G3.RTH.5) | 13.9953 (G3.RTH.5) | 13.9953 (G3.RTH.5) | 0.8634 (B-H4 narrow-range breakout) | 0.8634 | 13.8946 (G3.RTH.5) | 13.8946 | ok |
| C2 | 2019-07-01 | measured/31 vs measured/31 | 0.3048 (G2.ETH.5) | 0.3048 (G2.ETH.5) | 0.3048 (G2.ETH.5) | 14.2258 (G3.RTH.5) | 14.2258 (G3.RTH.5) | 14.2258 (G3.RTH.5) | 0.8776 (B-H4 narrow-range breakout) | 0.8776 | 14.1235 (G3.RTH.5) | 14.1235 | ok |
| C2 | 2020-01-02 | measured/31 vs measured/31 | 0.3229 (G2.ETH.5) | 0.3229 (G2.ETH.5) | 0.3229 (G2.ETH.5) | 15.0753 (G3.RTH.5) | 15.0753 (G3.RTH.5) | 15.0753 (G3.RTH.5) | 0.9301 (B-H4 narrow-range breakout) | 0.9301 | 14.9668 (G3.RTH.5) | 14.9668 | ok |
| C2 | 2021-01-04 | measured/31 vs measured/31 | 0.3702 (G2.ETH.5) | 0.3702 (G2.ETH.5) | 0.3702 (G2.ETH.5) | 17.2801 (G3.RTH.5) | 17.2801 (G3.RTH.5) | 17.2801 (G3.RTH.5) | 1.0661 (B-H4 narrow-range breakout) | 1.0661 | 17.1558 (G3.RTH.5) | 17.1558 | ok |
| C2 | 2022-01-03 | measured/31 vs measured/31 | 0.4478 (G2.ETH.5) | 0.4478 (G2.ETH.5) | 0.4478 (G2.ETH.5) | 20.9024 (G3.RTH.5) | 20.9024 (G3.RTH.5) | 20.9024 (G3.RTH.5) | 1.2896 (B-H4 narrow-range breakout) | 1.2896 | 20.7520 (G3.RTH.5) | 20.7520 | ok |
| C2 | 2023-01-03 | measured/31 vs measured/31 | 0.6111 (G2.ETH.5) | 0.6111 (G2.ETH.5) | 0.6111 (G2.ETH.5) | 28.5286 (G3.RTH.5) | 28.5286 (G3.RTH.5) | 28.5286 (G3.RTH.5) | 1.7600 (B-H4 narrow-range breakout) | 1.7600 | 28.3234 (G3.RTH.5) | 28.3234 | ok |
| C3 | 2019-05-06 | measured/40 vs measured/40 | 0.0162 (F1_1_h1_ETH) | 0.0162 (F1_1_h1_ETH) | 0.0162 (F1_1_h1_ETH) | 5.2157 (G4.RTH.60) | 5.2157 (G4.RTH.60) | 5.2157 (G4.RTH.60) | 2.4460 (RT5 C-H2 spike fade 5-min bars) | 2.4460 | 23.8423 (F1_1_h1_RTH) | 23.8423 | ok |
| C3 | 2019-07-01 | measured/40 vs measured/40 | 0.0164 (F1_1_h1_ETH) | 0.0164 (F1_1_h1_ETH) | 0.0164 (F1_1_h1_ETH) | 5.3016 (G4.RTH.60) | 5.3016 (G4.RTH.60) | 5.3016 (G4.RTH.60) | 2.4863 (RT5 C-H2 spike fade 5-min bars) | 2.4863 | 24.2350 (F1_1_h1_RTH) | 24.2350 | ok |
| C3 | 2020-01-02 | measured/40 vs measured/40 | 0.0174 (F1_1_h1_ETH) | 0.0174 (F1_1_h1_ETH) | 0.0174 (F1_1_h1_ETH) | 5.6182 (G4.RTH.60) | 5.6182 (G4.RTH.60) | 5.6182 (G4.RTH.60) | 2.6347 (RT5 C-H2 spike fade 5-min bars) | 2.6347 | 25.6821 (F1_1_h1_RTH) | 25.6821 | ok |
| C3 | 2021-01-04 | measured/40 vs measured/40 | 0.0200 (F1_1_h1_ETH) | 0.0200 (F1_1_h1_ETH) | 0.0200 (F1_1_h1_ETH) | 6.4399 (G4.RTH.60) | 6.4399 (G4.RTH.60) | 6.4399 (G4.RTH.60) | 3.0201 (RT5 C-H2 spike fade 5-min bars) | 3.0201 | 29.4383 (F1_1_h1_RTH) | 29.4383 | ok |
| C3 | 2022-01-03 | measured/40 vs measured/40 | 0.0242 (F1_1_h1_ETH) | 0.0242 (F1_1_h1_ETH) | 0.0242 (F1_1_h1_ETH) | 7.7898 (G4.RTH.60) | 7.7898 (G4.RTH.60) | 7.7898 (G4.RTH.60) | 3.6531 (RT5 C-H2 spike fade 5-min bars) | 3.6531 | 35.6091 (F1_1_h1_RTH) | 35.6091 | ok |
| C3 | 2023-01-03 | measured/40 vs measured/40 | 0.0330 (F1_1_h1_ETH) | 0.0330 (F1_1_h1_ETH) | 0.0330 (F1_1_h1_ETH) | 10.6319 (G4.RTH.60) | 10.6319 (G4.RTH.60) | 10.6319 (G4.RTH.60) | 4.9860 (RT5 C-H2 spike fade 5-min bars) | 4.9860 | 48.6011 (F1_1_h1_RTH) | 48.6011 | ok |
| C4 | 2019-05-06 | measured/13 vs measured/13 | 0.2315 (D-H3 range-compression gate) | 0.2315 (D-H3 range-compression gate) | 0.2315 (D-H3 range-compression gate) | 2.1767 (F5_1_relvol_tercile_top) | 2.1767 (F5_1_relvol_tercile_top) | 2.1767 (F5_1_relvol_tercile_top) | 0.2908 (D-H1 trailing-vol regime gate) | 0.2908 | 13.0789 (F2_4_15min_vol_tercile_top) | 13.0789 | ok |
| C4 | 2019-07-01 | measured/13 vs measured/13 | 0.2353 (D-H3 range-compression gate) | 0.2353 (D-H3 range-compression gate) | 0.2353 (D-H3 range-compression gate) | 2.2126 (F5_1_relvol_tercile_top) | 2.2126 (F5_1_relvol_tercile_top) | 2.2126 (F5_1_relvol_tercile_top) | 0.2956 (D-H1 trailing-vol regime gate) | 0.2956 | 13.2943 (F2_4_15min_vol_tercile_top) | 13.2943 | ok |
| C4 | 2020-01-02 | measured/13 vs measured/13 | 0.2494 (D-H3 range-compression gate) | 0.2494 (D-H3 range-compression gate) | 0.2494 (D-H3 range-compression gate) | 2.3447 (F5_1_relvol_tercile_top) | 2.3447 (F5_1_relvol_tercile_top) | 2.3447 (F5_1_relvol_tercile_top) | 0.3132 (D-H1 trailing-vol regime gate) | 0.3132 | 14.0881 (F2_4_15min_vol_tercile_top) | 14.0881 | ok |
| C4 | 2021-01-04 | measured/13 vs measured/13 | 0.2858 (D-H3 range-compression gate) | 0.2858 (D-H3 range-compression gate) | 0.2858 (D-H3 range-compression gate) | 2.6876 (F5_1_relvol_tercile_top) | 2.6876 (F5_1_relvol_tercile_top) | 2.6876 (F5_1_relvol_tercile_top) | 0.3591 (D-H1 trailing-vol regime gate) | 0.3591 | 16.1486 (F2_4_15min_vol_tercile_top) | 16.1486 | ok |
| C4 | 2022-01-03 | measured/13 vs measured/13 | 0.3458 (D-H3 range-compression gate) | 0.3458 (D-H3 range-compression gate) | 0.3458 (D-H3 range-compression gate) | 3.2510 (F5_1_relvol_tercile_top) | 3.2510 (F5_1_relvol_tercile_top) | 3.2510 (F5_1_relvol_tercile_top) | 0.4343 (D-H1 trailing-vol regime gate) | 0.4343 | 19.5336 (F2_4_15min_vol_tercile_top) | 19.5336 | ok |
| C4 | 2023-01-03 | measured/13 vs measured/13 | 0.4719 (D-H3 range-compression gate) | 0.4719 (D-H3 range-compression gate) | 0.4719 (D-H3 range-compression gate) | 4.4372 (F5_1_relvol_tercile_top) | 4.4372 (F5_1_relvol_tercile_top) | 4.4372 (F5_1_relvol_tercile_top) | 0.5928 (D-H1 trailing-vol regime gate) | 0.5928 | 26.6604 (F2_4_15min_vol_tercile_top) | 26.6604 | ok |
| C5 | 2019-05-06 | measured/4 vs measured/4 | 0.9795 (E-H4 turn-of-month long) | 0.9795 (E-H4 turn-of-month long) | 0.9795 (E-H4 turn-of-month long) | 18.6309 (E-H1 scheduled macro drift) | 18.6309 (E-H1 scheduled macro drift) | 18.6309 (E-H1 scheduled macro drift) | 0.0679 (E-H3 quarterly witching short) | 0.0679 | 1.9985 (E-H1 scheduled macro drift) | 1.9985 | ok |
| C5 | 2019-07-01 | measured/4 vs measured/4 | 0.9957 (E-H4 turn-of-month long) | 0.9957 (E-H4 turn-of-month long) | 0.9957 (E-H4 turn-of-month long) | 18.9378 (E-H1 scheduled macro drift) | 18.9378 (E-H1 scheduled macro drift) | 18.9378 (E-H1 scheduled macro drift) | 0.0691 (E-H3 quarterly witching short) | 0.0691 | 2.0314 (E-H1 scheduled macro drift) | 2.0314 | ok |
| C5 | 2020-01-02 | measured/4 vs measured/4 | 1.0551 (E-H4 turn-of-month long) | 1.0551 (E-H4 turn-of-month long) | 1.0551 (E-H4 turn-of-month long) | 20.0686 (E-H1 scheduled macro drift) | 20.0686 (E-H1 scheduled macro drift) | 20.0686 (E-H1 scheduled macro drift) | 0.0732 (E-H3 quarterly witching short) | 0.0732 | 2.1527 (E-H1 scheduled macro drift) | 2.1527 | ok |
| C5 | 2021-01-04 | measured/4 vs measured/4 | 1.2094 (E-H4 turn-of-month long) | 1.2094 (E-H4 turn-of-month long) | 1.2094 (E-H4 turn-of-month long) | 23.0038 (E-H1 scheduled macro drift) | 23.0038 (E-H1 scheduled macro drift) | 23.0038 (E-H1 scheduled macro drift) | 0.0839 (E-H3 quarterly witching short) | 0.0839 | 2.4675 (E-H1 scheduled macro drift) | 2.4675 | ok |
| C5 | 2022-01-03 | measured/4 vs measured/4 | 1.4629 (E-H4 turn-of-month long) | 1.4629 (E-H4 turn-of-month long) | 1.4629 (E-H4 turn-of-month long) | 27.8258 (E-H1 scheduled macro drift) | 27.8258 (E-H1 scheduled macro drift) | 27.8258 (E-H1 scheduled macro drift) | 0.1015 (E-H3 quarterly witching short) | 0.1015 | 2.9848 (E-H1 scheduled macro drift) | 2.9848 | ok |
| C5 | 2023-01-03 | measured/4 vs measured/4 | 1.9967 (E-H4 turn-of-month long) | 1.9967 (E-H4 turn-of-month long) | 1.9967 (E-H4 turn-of-month long) | 37.9780 (E-H1 scheduled macro drift) | 37.9780 (E-H1 scheduled macro drift) | 37.9780 (E-H1 scheduled macro drift) | 0.1385 (E-H3 quarterly witching short) | 0.1385 | 4.0738 (E-H1 scheduled macro drift) | 4.0738 | ok |
| C6 | 2019-05-06 | measured/1 vs measured/1 | 0.0727 (C-H4 passive-fill reversal) | 0.0727 (C-H4 passive-fill reversal) | 0.0727 (C-H4 passive-fill reversal) | 0.0727 (C-H4 passive-fill reversal) | 0.0727 (C-H4 passive-fill reversal) | 0.0727 (C-H4 passive-fill reversal) | 6.7235 (C-H4 passive-fill reversal) | 6.7235 | 6.7235 (C-H4 passive-fill reversal) | 6.7235 | ok |
| C6 | 2019-07-01 | measured/1 vs measured/1 | 0.0739 (C-H4 passive-fill reversal) | 0.0739 (C-H4 passive-fill reversal) | 0.0739 (C-H4 passive-fill reversal) | 0.0739 (C-H4 passive-fill reversal) | 0.0739 (C-H4 passive-fill reversal) | 0.0739 (C-H4 passive-fill reversal) | 6.8343 (C-H4 passive-fill reversal) | 6.8343 | 6.8343 (C-H4 passive-fill reversal) | 6.8343 | ok |
| C6 | 2020-01-02 | measured/1 vs measured/1 | 0.0783 (C-H4 passive-fill reversal) | 0.0783 (C-H4 passive-fill reversal) | 0.0783 (C-H4 passive-fill reversal) | 0.0783 (C-H4 passive-fill reversal) | 0.0783 (C-H4 passive-fill reversal) | 0.0783 (C-H4 passive-fill reversal) | 7.2423 (C-H4 passive-fill reversal) | 7.2423 | 7.2423 (C-H4 passive-fill reversal) | 7.2423 | ok |
| C6 | 2021-01-04 | measured/1 vs measured/1 | 0.0898 (C-H4 passive-fill reversal) | 0.0898 (C-H4 passive-fill reversal) | 0.0898 (C-H4 passive-fill reversal) | 0.0898 (C-H4 passive-fill reversal) | 0.0898 (C-H4 passive-fill reversal) | 0.0898 (C-H4 passive-fill reversal) | 8.3016 (C-H4 passive-fill reversal) | 8.3016 | 8.3016 (C-H4 passive-fill reversal) | 8.3016 | ok |
| C6 | 2022-01-03 | measured/1 vs measured/1 | 0.1086 (C-H4 passive-fill reversal) | 0.1086 (C-H4 passive-fill reversal) | 0.1086 (C-H4 passive-fill reversal) | 0.1086 (C-H4 passive-fill reversal) | 0.1086 (C-H4 passive-fill reversal) | 0.1086 (C-H4 passive-fill reversal) | 10.0417 (C-H4 passive-fill reversal) | 10.0417 | 10.0417 (C-H4 passive-fill reversal) | 10.0417 | ok |
| C6 | 2023-01-03 | measured/1 vs measured/1 | 0.1482 (C-H4 passive-fill reversal) | 0.1482 (C-H4 passive-fill reversal) | 0.1482 (C-H4 passive-fill reversal) | 0.1482 (C-H4 passive-fill reversal) | 0.1482 (C-H4 passive-fill reversal) | 0.1482 (C-H4 passive-fill reversal) | 13.7055 (C-H4 passive-fill reversal) | 13.7055 | 13.7055 (C-H4 passive-fill reversal) | 13.7055 | ok |
| C7 | 2019-05-06 | projected/6 vs projected/6 | 13.3264 (H6 prior-close location follow-through) | 13.3264 (H6 prior-close location follow-through) | 13.3264 (H6 prior-close location follow-through) | 20.4397 (H2 NR7 opening-range breakout) | 20.4397 (H2 NR7 opening-range breakout) | 20.4397 (H2 NR7 opening-range breakout) | 2.6280 (H2 NR7 opening-range breakout) | 2.6280 | 5.3306 (H6 prior-close location follow-through) | 5.3306 | ok |
| C7 | 2019-07-01 | projected/6 vs projected/6 | 13.5459 (H6 prior-close location follow-through) | 13.5459 (H6 prior-close location follow-through) | 13.5459 (H6 prior-close location follow-through) | 20.7763 (H2 NR7 opening-range breakout) | 20.7763 (H2 NR7 opening-range breakout) | 20.7763 (H2 NR7 opening-range breakout) | 2.6712 (H2 NR7 opening-range breakout) | 2.6712 | 5.4184 (H6 prior-close location follow-through) | 5.4184 | ok |
| C7 | 2020-01-02 | projected/6 vs projected/6 | 14.3548 (H6 prior-close location follow-through) | 14.3548 (H6 prior-close location follow-through) | 14.3548 (H6 prior-close location follow-through) | 22.0169 (H2 NR7 opening-range breakout) | 22.0169 (H2 NR7 opening-range breakout) | 22.0169 (H2 NR7 opening-range breakout) | 2.8307 (H2 NR7 opening-range breakout) | 2.8307 | 5.7419 (H6 prior-close location follow-through) | 5.7419 | ok |
| C7 | 2021-01-04 | projected/6 vs projected/6 | 16.4543 (H6 prior-close location follow-through) | 16.4543 (H6 prior-close location follow-through) | 16.4543 (H6 prior-close location follow-through) | 25.2370 (H2 NR7 opening-range breakout) | 25.2370 (H2 NR7 opening-range breakout) | 25.2370 (H2 NR7 opening-range breakout) | 3.2448 (H2 NR7 opening-range breakout) | 3.2448 | 6.5817 (H6 prior-close location follow-through) | 6.5817 | ok |
| C7 | 2022-01-03 | projected/6 vs projected/6 | 19.9034 (H6 prior-close location follow-through) | 19.9034 (H6 prior-close location follow-through) | 19.9034 (H6 prior-close location follow-through) | 30.5272 (H2 NR7 opening-range breakout) | 30.5272 (H2 NR7 opening-range breakout) | 30.5272 (H2 NR7 opening-range breakout) | 3.9249 (H2 NR7 opening-range breakout) | 3.9249 | 7.9614 (H6 prior-close location follow-through) | 7.9614 | ok |
| C7 | 2023-01-03 | projected/6 vs projected/6 | 27.1651 (H6 prior-close location follow-through) | 27.1651 (H6 prior-close location follow-through) | 27.1651 (H6 prior-close location follow-through) | 41.6651 (H2 NR7 opening-range breakout) | 41.6651 (H2 NR7 opening-range breakout) | 41.6651 (H2 NR7 opening-range breakout) | 5.3569 (H2 NR7 opening-range breakout) | 5.3569 | 10.8661 (H6 prior-close location follow-through) | 10.8661 | ok |

Verdict: **VERIFIED**.

## 6. Supplied days at each S, and holdout-2

Stated method (JSON `method` strings, confirmed in `_d1e_calendar.py` at the end): weekdays S..2024-02-29
minus the ten full-closure holidays (New Year's, MLK, Presidents', Good Friday, Memorial, Juneteenth
from 2022, Independence, Labor, Thanksgiving, Christmas; Sunday -> Monday, Saturday -> no weekday
closure), minus 3 blackout dates per quarterly roll pro rata by months (= number of months in range),
minus the degraded dates in range. My recount used my own holiday and Easter code (Easter checked
against dateutil for 2019-2025, no mismatch).

| S | rep weekday open | mine (stated rule) | mine (pipeline closures) | rep blackout | rolls exact x3 | pro-rata months | rep degraded | degraded in range | of which weekday-open | rep days | mine: stated method | mine: exact rolls, weekday degraded | mine: pipeline closures, exact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019-05-06 | 1216 | 1216 | 1247 | 58 | 57 (19 rolls) | 58 | 7 | 7 | 5 | **1151** | 1151 | 1154 | 1185 |
| 2019-07-01 | 1177 | 1177 | 1207 | 56 | 54 (18 rolls) | 56 | 7 | 7 | 5 | **1114** | 1114 | 1118 | 1148 |
| 2020-01-02 | 1049 | 1049 | 1076 | 50 | 48 (16 rolls) | 50 | 7 | 7 | 5 | **992** | 992 | 996 | 1023 |
| 2021-01-04 | 795 | 795 | 817 | 38 | 36 (12 rolls) | 38 | 2 | 2 | 0 | **755** | 755 | 759 | 781 |
| 2022-01-03 | 542 | 542 | 558 | 26 | 24 (8 rolls) | 26 | 0 | 0 | 0 | **516** | 516 | 518 | 534 |
| 2023-01-03 | 291 | 291 | 300 | 14 | 12 (4 rolls) | 14 | 0 | 0 | 0 | **277** | 277 | 279 | 288 |
| holdout-2 2024-04-01..2025-03-31 | 252 | 252 | 259 | 12 | 12 (4 rolls) | 12 | 1 | 1 | 1 | **239** | 239 | 239 | 246 |

Columns: "mine (stated rule)" reproduces the reported weekday-open count exactly at every S and for
holdout-2; "mine: stated method" reproduces every reported total exactly (1,151 / 1,114 / 992 / 755 /
516 / 277; holdout-2 239). The two "exact" columns are alternative counts, not corrections of arithmetic:

1. Roll blackout: the range holds 19 / 18 / 16 / 12 / 8 / 4 quarterly rolls (Mar/Jun/Sep/Dec, roll about
   a week before the third Friday), i.e. 57 / 54 / 48 / 36 / 24 / 12 blackout dates, versus the pro-rata
   58 / 56 / 50 / 38 / 26 / 14 (holdout-2: 12 both ways). Effect: +1 to +2 days.
2. Degraded dates: two of the seven in-range dates are Sundays (2021-12-05, 2022-01-02) and are
   subtracted from a weekday count. A degraded Sunday UTC date covers the Sunday 17:00 CT open that
   belongs to Monday's trade date, so whether it removes a trade date depends on how D.1f masks
   degraded bars; at most 2 days either way. Effect: 0 to +2 days.
3. Holiday convention: the repo's own `data/cme_calendar.py` treats MLK, Presidents', Memorial,
   Juneteenth, Independence, Labor and Thanksgiving as EARLY-HALT trade dates (12:00 CT halt), not
   closures; only Good Friday, Christmas and New Year's are full closures there. Under that convention
   the weekday-open counts are 1,247 / 1,207 / 1,076 / 817 / 558 / 300 (holdout-2 259) and the totals
   1,185 / 1,148 / 1,023 / 781 / 534 / 288 (holdout-2 246): +3.0 %, +3.1 %, +3.1 %, +3.4 %, +3.5 %, +4.0 %
   (holdout-2 +2.9 %) above the reported figures, i.e. at or just beyond the stated +/-3 % band for the
   later starts, and in one direction. Whether those dates count as usable confirmation days depends on
   the member's session window (an RTH strategy flattened at 12:00 CT still trades; an afternoon-only
   one does not), which is a D.1f matter. Good Friday 2021-04-02 and 2023-04-07 also had abbreviated
   CME equity sessions (jobs report), counted as closures here.

None of the three moves any `null_power_achievable_at` flag (the only short cells, C3 at 2022 and 2023,
stay short: 566 > 534 and 566 > 288). The estimate's direction is conservative for the report's purpose
(fewer days claimed than the calendar supplies).

Full closures counted per year under the stated rule:
- 2019: 9: 2019-01-01, 2019-01-21, 2019-02-18, 2019-04-19, 2019-05-27, 2019-07-04, 2019-09-02, 2019-11-28, 2019-12-25
- 2020: 8: 2020-01-01, 2020-01-20, 2020-02-17, 2020-04-10, 2020-05-25, 2020-09-07, 2020-11-26, 2020-12-25
- 2021: 8: 2021-01-01, 2021-01-18, 2021-02-15, 2021-04-02, 2021-05-31, 2021-07-05, 2021-09-06, 2021-11-25
- 2022: 9: 2022-01-17, 2022-02-21, 2022-04-15, 2022-05-30, 2022-06-20, 2022-07-04, 2022-09-05, 2022-11-24, 2022-12-26
- 2023: 10: 2023-01-02, 2023-01-16, 2023-02-20, 2023-04-07, 2023-05-29, 2023-06-19, 2023-07-04, 2023-09-04, 2023-11-23, 2023-12-25
- 2024: 10: 2024-01-01, 2024-01-15, 2024-02-19, 2024-03-29, 2024-05-27, 2024-06-19, 2024-07-04, 2024-09-02, 2024-11-28, 2024-12-25

Verdict: **VERIFIED WITH NOTES** (arithmetic exact; method systematically conservative by 3 to 4 %).

## 7. Audit of tests/test_d1e_power.py

`uv run pytest tests/test_d1e_power.py -q`: **10 passed in 1.97 s** (run once).

| test | expected value comes from | independent of the code under test? | note |
|---|---|---|---|
| 1 `test_iid_series_has_unit_vif_and_textbook_null_sample_size` | `_expected_n` in the test: ceil(((z+z_b) sd sqrt(vif)/eps)^2) with NormalDist quantiles and numpy sd; band 140..175; simulated power_b = 0.80 +/- 0.03 | yes (formula re-stated in the test); VIF = 1 +/- 0.05 on 50,000 iid days | the iid known-answer case: analytic n equals the textbook value and the simulation reproduces 80 % power at it |
| 2 `test_iid_series_detection_sample_size_matches_the_textbook_value` | same, at z_Holm; band 360..440; power_a = 0.80 +/- 0.03 | yes | second half of the iid known-answer case (detection arm) |
| 3 `test_ar1_series_vif_matches_the_bootstrap_implied_factor_not_the_true_one` | 1 + 2 sum ((1-p) phi)^k = 1.6316 (asserted to 1e-3 as a literal), true long-run (1+phi)/(1-phi) = 1.8571; VIF within 10 % of 1.6316; power_b = 0.80 +/- 0.04 at the analytic n | yes for the literals; the sum uses `stats.BOOTSTRAP_RENEWAL_P` and `stats.MAX_LAG_K`, but the 1e-3 literal pins them | the AR(1) known-answer case: the inflation shown is the block-5 bootstrap-implied factor (1.63), deliberately below the true 1.86; the test documents that the program under-corrects by design. It is also the regression test for the SE construction (correction 2): the replicate-own-V_B version gave 0.848 |
| 4 `test_unit_conversions_for_trials_and_statistics` | hand arithmetic ($2.5 -> 1 tick; -1 x 10 - 2 x 2.11) | yes | |
| 5 `test_threshold_interpolation_is_log_linear_and_reports_a_curve_that_never_crosses` | 20 sqrt 2 by hand; `_chosen` cases: censored -> analytic; +50 % -> simulated; -50 % -> analytic + flag; +5 %/-10 % -> analytic, no flag | yes | covers the rule of correction 1; does not probe the exact 15 % boundary (> versus >=) |
| 6 `test_supplied_days_calendar_for_january_2023` | hand count 22 weekdays, 2 closures -> 20 | yes | encodes MLK Day as a full closure (see section 6 note 3); the docstring records the brief's 19 as a weekday-count slip |
| `test_holiday_observance_rules` | CME facts as literals | yes | Saturday rule, Juneteenth from 2022, Good Friday 2022 |
| 7 `test_family_h_projection_uses_the_coverage_map_proxy_rule` | 100 sqrt 0.225 by hand; literals (100, 0.225), (115, 0.4) | yes | |
| `test_bootstrap_variance_floors_a_strongly_alternating_series` | +/-1 series: V_B/g0 = 1 + 2 sum (-0.8)^k = 0.12 < 0.2 | yes (implicit) | asserts against `stats.VIF_FLOOR_FRACTION`, a constant |
| `test_normal_quantiles_match_the_published_values` | published quantiles as 1e-12 literals | yes | my erfc-Newton values agree to 1e-14 |

Both required known-answer cases are present (tests 1-2 iid normal; test 3 AR(1) phi = 0.3). Gaps, for
the record: no test of the autocovariance divisor (1/n) or of the VIF on a series with negative lag-1
autocorrelation (the only such members here have VIF 0.40-0.60 and are where the bootstrap over-corrects
in the other direction); no direct test of `simulate_powers` SE against a hand value; no test of class
aggregation (`typical_r` over trials only, binding selection, `resolution_range`); no test of the
degraded-date or blackout subtraction; no test at exactly 15 %; no test that the eps derivation
implements NULL_CRITERIA 2.2 (eps_day is passed in, not derived, in this run).

Verdict: **VERIFIED WITH NOTES**.

## 8. JSON internal consistency

Checked: power curves non-decreasing in n beyond 3 MC se; analytic n's present in each curve; se fields
binomial; eps_trade = 34/r; `spot_check.n` = chosen_b; flags consistent with `sim_zero_variance_draws`;
class member lists versus coverage.md; tier counts; floor fields; md section 3 (101 rows) versus JSON
(class, tier, SD, VIF, n_a, n_b, chosen_a, chosen_b): **no md-vs-JSON mismatch**.

### 8.1 `spot_check.closed_form_power_b` is not the curve's value at the same n
For all five measured binding members the field differs from `curve[n].power_b`: A-H4 rth leg 0.808 vs
0.815, C-H4 0.8185 vs 0.8295, F1_1_h1_RTH 0.800 vs 0.7975, F2_4 0.8165 vs 0.846, G3.RTH.5 0.8325 vs
0.8245 (E-H1 0.926 both). Read at the end: `attach_spot_checks` calls `simulate_powers(centred, eps,
[n], SEED_BASE + index, 2000)`, the same seed base as the main curve but with a single-length list, so
the RNG stream differs and it is an independent 2,000-replicate estimate of the same quantity; the
percentile column is 200 replicates x inner B = 1,000. The differences are MC noise (largest F2_4, 0.0295
= 2.3 se of a difference of two 2,000-rep proportions; my own value at n = 171 is 0.826, between the
two). Not an error, but the md's "closed-form power_b" column in section 4 should be read as a
re-draw, not as the curve value.

### 8.2 Other observations
- F5_1_relvol_tercile_top arm a: power_a falls from 0.331 (n = 10) to 0.283 (n = 15) and 0.2625 (n = 20)
  before rising: a 3.3-se step, and G1.RTH.15 arm a dips from 0.51 (n = 62-75) to 0.47 (n = 100) in both
  the reported and my curves. Heavy-tailed members with a right-skewed replicate variance at short
  lengths; the dips sit far below the 0.80 crossing and do not affect any figure.
- E-H3 (4 trades in 289 days): both arms at power 1.0 at every length from n = 2; censored, analytic
  n_a = n_b = 1 kept. E-H1 (31 trades in 289 days): n_b = 4 is a 4-day sample in which 63 % of draws are
  all-zero; the "power" there is dominated by the zero-variance convention. Both are correctly flagged.
- The 15 % rule flips figures for 8 members and would flip F4_4 x100 back under my seed (section 3.1).
- `sim_source_vif_floored` is absent from projected rows (field omitted rather than null); harmless.
- Reported runtime 151 s versus my 28 s for 13 members: consistent with 95 members x 2 arms.

Verdict: **VERIFIED WITH NOTES**.

## 9. For the lead's re-run at the final epsilon

Scaling check to apply to the re-run JSON against this verified run (eps = 34):
- n_a_analytic and n_b_analytic: n(eps_final) = ceil(n_exact(34) x (34/eps_final)^2), so the reported
  integers scale as (34/eps_final)^2 to within the ceiling (at most 1 day off when using the rounded
  n(34)). Example rows, my recomputation:

| member | eps | n_a | n_b | eps/trade | (34/eps)^2 x n_a(34) | (34/eps)^2 x n_b(34) |
|---|---|---|---|---|---|---|
| F1_1_h1_RTH | 33 | 1537 | 601 | 0.087 | 1536.0 | 600.8 |
| F1_1_h1_RTH | 35 | 1366 | 535 | 0.092 | 1365.5 | 534.1 |
| G3.RTH.5 | 33 | 522 | 205 | 33.239 | 522.3 | 204.9 |
| G3.RTH.5 | 35 | 464 | 182 | 35.254 | 464.3 | 182.1 |
| A-H4 rth leg | 33 | 101 | 40 | 34.554 | 100.8 | 40.3 |
| A-H4 rth leg | 35 | 90 | 35 | 36.649 | 89.6 | 35.9 |

- eps_trade (member and class) and gross_equivalent_trade - 2.11 scale as eps_final/34 exactly.
- Unchanged by eps: r, SD_day, lag1, VIF_boot, eps_min_at_supplied and `resolution_range`, eps_ref_days,
  n_b_sensitivity, supplied_days, holdout2. If any of these changes, the input series changed.
- Simulated n's scale approximately as (34/eps_final)^2 but not exactly (new analytic grid points, MC
  noise); the chosen-figure flags can flip for the members within about 4 points of the 15 % threshold
  (F4_4 x100 b +18.5, G4.RTH.5 b +17.4, G1.ETH.15 b +17.0, G1.ETH.60 a +16.9, G4.RTH.60 a +16.7,
  F4_1 b -16.7, G1.ETH.30 b -18.6, G1.RTH.15 a +19.0, G4.RTH.30 b -19.1). A flip there is expected
  behaviour, not a bug.
- Binding members and achievability flags: C3's F1_1_h1_RTH is the only member that is short anywhere.
  Its n_b runs 727 / 639 / 566 / 505 / 454 / 409 at eps 30 / 32 / 34 / 36 / 38 / 40 (verified
  `n_b_sensitivity`). Against the supplied 277 (2023-01-03) it stays short for every eps_final in
  30..40; against 516 (2022-01-03) it is short for eps_final <= 35 and achievable for eps_final >= 36
  (the crossing is at eps = 34 x sqrt(566.0/516) = 35.6), so the C3 flag at the 2022 start is the one
  achievability cell that the final epsilon can flip; against 755 (2021-01-04) it is achievable for
  every eps_final >= 30. All other classes are achievable at every S for any eps_final in 30..40.

Three member rows to spot-check after the re-run: (1) **F1_1_h1_RTH**: the C3 binding member, the
largest n in the file and the row that sets the only "short" flags; (2) **G3.RTH.5**: the C2 binding
member, the largest Tier B n_b in an achievable class, r = 0.993 so its eps/trade tracks eps_day almost
one for one; (3) **A-H4 rth leg**: the C1 binding member and the member with the strongest negative
lag-1 autocorrelation (-0.30, VIF 0.55), i.e. the one most exposed to the VIF construction, with the
largest reported sim-versus-analytic gap among binding members (arm b -23 %). If a fourth is wanted,
F4_4_round_number_multiples_of_100 arm b, as the canary for the 15 % flag flipping.

## 10. What was not done or could not be verified
- Version A of `stage_d1e_gate_extension.json` (84 rows) was overwritten before my script ran; its
  eps = 34 is inferred from the unchanged verdict counts of the first 84 rows and the T = 16 rows'
  values, not from a row-level recomputation on that version.
- 13 of 95 measured members were re-simulated, as briefed; the chosen-figure rule and diff_pct were
  checked on all 95 x 2 arms against the reported simulated values, not against fresh simulations.
- The supplied-days recount follows the stated rule and two alternative conventions; no exchange
  calendar file for 2019-2024 exists in the repo, so the true CME trade-date count was not read from a
  source.
- The percentile spot-check column (200 replicates) was not re-simulated; it changes no figure.
- The md's section 1 count "roll blackout" and "vendor degraded" figures are reproduced exactly, but the
  question of whether a degraded Sunday removes a Monday trade date is a D.1f pipeline question left open.

## Appendix A. Re-simulated power curves (mine), power_a / power_b by n, reported values in brackets

- A-H4 rth leg: 10: 0.243/0.595 (rep 0.284/0.584), 15: 0.344/0.677 (rep 0.334/0.690), 20: 0.379/0.743 (rep 0.388/0.733), 22: 0.383/0.747, 25: 0.406/0.795, 29: 0.428/0.790, 30: 0.415/0.804 (rep 0.428/0.805), 34: 0.443/0.812, 38: 0.474/0.839 (rep 0.453/0.815), 50: 0.561/0.859 (rep 0.548/0.862), 74: 0.694/0.912, 75: 0.700/0.914 (rep 0.680/0.923), 85: 0.739/0.953, 95: 0.773/0.967 (rep 0.781/0.960), 98: 0.795/0.973, 100: 0.815/0.970 (rep 0.811/0.970), 113: 0.850/0.986, 128: 0.896/0.991, 150: 0.944/0.997 (rep 0.939/0.996), 200: 0.992/0.999 (rep 0.992/0.999), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- G3.RTH.5: 10: 0.033/0.147 (rep 0.033/0.128), 15: 0.029/0.166 (rep 0.030/0.158), 20: 0.034/0.195 (rep 0.031/0.196), 30: 0.033/0.265 (rep 0.037/0.260), 50: 0.066/0.356 (rep 0.086/0.373), 75: 0.104/0.470 (rep 0.103/0.479), 100: 0.135/0.580 (rep 0.149/0.564), 136: 0.215/0.695, 150: 0.245/0.729 (rep 0.243/0.723), 158: 0.237/0.757, 182: 0.284/0.790, 193: 0.315/0.826 (rep 0.315/0.825), 200: 0.324/0.823 (rep 0.316/0.830), 209: 0.330/0.861, 236: 0.402/0.878, 300: 0.514/0.939 (rep 0.520/0.933), 388: 0.651/0.980, 451: 0.747/0.988, 492: 0.783/0.996 (rep 0.772/0.994), 500: 0.802/0.993 (rep 0.786/0.997), 518: 0.801/0.995, 596: 0.880/0.999, 673: 0.909/0.999, 750: 0.956/1.000 (rep 0.947/1.000), 1000: 0.990/1.000 (rep 0.986/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- F1_1_h1_RTH: 10: 0.013/0.122 (rep 0.018/0.118), 15: 0.008/0.122 (rep 0.009/0.118), 20: 0.011/0.139 (rep 0.015/0.130), 30: 0.008/0.161 (rep 0.011/0.154), 50: 0.016/0.209 (rep 0.015/0.200), 75: 0.019/0.241 (rep 0.022/0.251), 100: 0.030/0.291 (rep 0.028/0.288), 150: 0.040/0.383 (rep 0.035/0.377), 200: 0.061/0.420 (rep 0.067/0.446), 300: 0.101/0.556 (rep 0.097/0.571), 428: 0.183/0.703, 496: 0.235/0.754, 500: 0.221/0.768 (rep 0.226/0.762), 566: 0.269/0.807 (rep 0.282/0.797), 571: 0.273/0.819, 656: 0.324/0.862, 742: 0.398/0.883, 750: 0.405/0.890 (rep 0.391/0.885), 1000: 0.573/0.958 (rep 0.580/0.956), 1102: 0.645/0.974, 1279: 0.730/0.979, 1447: 0.814/0.994 (rep 0.792/0.990), 1470: 0.810/0.992, 1500: 0.822/0.994 (rep 0.810/0.995), 1690: 0.880/0.995, 1911: 0.928/0.998, 2000: 0.949/0.999 (rep 0.943/0.997), 3000: 0.996/1.000 (rep 0.996/1.000)
- F2_4_15min_vol_tercile_top: 10: 0.041/0.275 (rep 0.041/0.294), 15: 0.035/0.251 (rep 0.035/0.272), 20: 0.033/0.238 (rep 0.027/0.250), 30: 0.035/0.303 (rep 0.045/0.281), 50: 0.076/0.383 (rep 0.088/0.385), 75: 0.150/0.518 (rep 0.157/0.525), 100: 0.221/0.625 (rep 0.234/0.610), 114: 0.265/0.652, 132: 0.296/0.720, 150: 0.320/0.789 (rep 0.314/0.794), 152: 0.315/0.787, 171: 0.362/0.826 (rep 0.338/0.846), 175: 0.358/0.843, 198: 0.390/0.883, 200: 0.394/0.891 (rep 0.394/0.889), 300: 0.579/0.969 (rep 0.592/0.969), 344: 0.643/0.983, 399: 0.700/0.994, 436: 0.770/0.997 (rep 0.778/0.996), 458: 0.798/0.997, 500: 0.838/0.999 (rep 0.838/1.000), 527: 0.872/1.000, 596: 0.897/1.000, 750: 0.960/1.000 (rep 0.968/1.000), 1000: 0.998/1.000 (rep 0.996/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- E-H1 scheduled macro drift: 4: 0.865/0.907 (rep 0.880/0.926), 10: 0.882/0.994 (rep 0.881/0.993), 11: 0.882/0.997 (rep 0.864/0.996), 15: 0.912/1.000 (rep 0.900/1.000), 20: 0.893/1.000 (rep 0.878/1.000), 30: 0.893/1.000 (rep 0.891/1.000), 50: 0.968/1.000 (rep 0.963/1.000), 75: 0.997/1.000 (rep 0.994/1.000), 100: 1.000/1.000 (rep 1.000/1.000), 150: 1.000/1.000 (rep 1.000/1.000), 200: 1.000/1.000 (rep 1.000/1.000), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- C-H4 passive-fill reversal: 10: 0.145/0.383 (rep 0.144/0.374), 15: 0.194/0.438 (rep 0.173/0.458), 20: 0.193/0.540 (rep 0.201/0.547), 30: 0.245/0.670 (rep 0.244/0.692), 31: 0.270/0.699, 37: 0.292/0.772, 42: 0.330/0.791, 46: 0.359/0.831 (rep 0.359/0.830), 48: 0.382/0.837, 50: 0.396/0.859 (rep 0.396/0.845), 55: 0.433/0.873, 75: 0.567/0.947 (rep 0.550/0.956), 92: 0.649/0.976, 100: 0.700/0.984 (rep 0.696/0.987), 106: 0.741/0.990, 116: 0.773/0.992 (rep 0.775/0.995), 122: 0.792/0.996, 140: 0.862/0.999, 150: 0.881/0.999 (rep 0.897/0.999), 159: 0.905/1.000, 200: 0.961/1.000 (rep 0.970/1.000), 300: 0.998/1.000 (rep 0.997/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- E-H3 quarterly witching short: 2: 1.000/1.000 (rep 1.000/1.000), 10: 1.000/1.000 (rep 1.000/1.000), 15: 1.000/1.000 (rep 1.000/1.000), 20: 1.000/1.000 (rep 1.000/1.000), 30: 1.000/1.000 (rep 1.000/1.000), 50: 1.000/1.000 (rep 1.000/1.000), 75: 1.000/1.000 (rep 1.000/1.000), 100: 1.000/1.000 (rep 1.000/1.000), 150: 1.000/1.000 (rep 1.000/1.000), 200: 1.000/1.000 (rep 1.000/1.000), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- C-H1 magnitude-conditioned reversal: 10: 0.092/0.429 (rep 0.098/0.417), 15: 0.115/0.485 (rep 0.112/0.490), 20: 0.138/0.571 (rep 0.134/0.528), 30: 0.213/0.658 (rep 0.198/0.654), 36: 0.253/0.689, 42: 0.286/0.762, 47: 0.325/0.799 (rep 0.330/0.791), 48: 0.329/0.804, 50: 0.341/0.812 (rep 0.335/0.816), 55: 0.386/0.847, 62: 0.445/0.883, 75: 0.541/0.911 (rep 0.535/0.916), 89: 0.627/0.957, 100: 0.703/0.970 (rep 0.696/0.966), 104: 0.728/0.974, 119: 0.801/0.989 (rep 0.799/0.984), 137: 0.865/0.992, 150: 0.898/0.997 (rep 0.910/0.997), 155: 0.921/0.997, 200: 0.980/1.000 (rep 0.976/0.999), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- F3_2_bucket04_bucket05: 10: 0.253/0.699 (rep 0.264/0.712), 11: 0.276/0.717, 13: 0.305/0.783, 15: 0.357/0.817 (rep 0.348/0.805), 17: 0.402/0.833 (rep 0.368/0.824), 19: 0.439/0.819, 20: 0.445/0.821 (rep 0.453/0.832), 28: 0.645/0.877, 30: 0.682/0.894 (rep 0.668/0.879), 32: 0.726/0.912, 37: 0.788/0.935, 42: 0.892/0.950 (rep 0.885/0.956), 48: 0.928/0.976, 50: 0.936/0.976 (rep 0.936/0.981), 75: 0.997/0.999 (rep 0.996/0.995), 100: 1.000/1.000 (rep 1.000/1.000), 150: 1.000/1.000 (rep 1.000/1.000), 200: 1.000/1.000 (rep 1.000/1.000), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- G1.RTH.5: 10: 0.263/0.551 (rep 0.274/0.526), 15: 0.278/0.645 (rep 0.298/0.631), 19: 0.291/0.707, 20: 0.303/0.744 (rep 0.297/0.713), 22: 0.343/0.758, 25: 0.352/0.820, 27: 0.365/0.833 (rep 0.379/0.821), 29: 0.388/0.861, 30: 0.406/0.862 (rep 0.418/0.870), 33: 0.433/0.880, 50: 0.606/0.970 (rep 0.603/0.970), 55: 0.649/0.983, 64: 0.728/0.992, 68: 0.763/0.994 (rep 0.770/0.994), 74: 0.800/0.997, 75: 0.809/0.997 (rep 0.806/0.998), 85: 0.859/0.998, 96: 0.913/0.999, 100: 0.917/1.000 (rep 0.923/1.000), 150: 0.991/1.000 (rep 0.993/1.000), 200: 0.999/1.000 (rep 1.000/1.000), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- G4.RTH.30: 9: 0.539/0.713, 10: 0.539/0.745 (rep 0.530/0.762), 11: 0.523/0.789, 12: 0.593/0.812, 14: 0.630/0.820, 15: 0.647/0.845 (rep 0.610/0.841), 16: 0.636/0.854, 20: 0.678/0.910 (rep 0.682/0.901), 30: 0.730/0.978 (rep 0.738/0.971), 38: 0.736/0.992 (rep 0.742/0.989), 40: 0.756/0.995, 47: 0.768/0.997, 50: 0.772/0.998 (rep 0.773/0.998), 54: 0.821/0.999, 62: 0.864/1.000, 70: 0.895/1.000, 75: 0.917/1.000 (rep 0.922/1.000), 100: 0.973/1.000 (rep 0.980/1.000), 150: 1.000/1.000 (rep 0.998/1.000), 200: 1.000/1.000 (rep 1.000/1.000), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- F4_4_round_number_multiples_of_100: 10: 0.094/0.574 (rep 0.087/0.587), 15: 0.124/0.679 (rep 0.119/0.672), 20: 0.130/0.723 (rep 0.144/0.713), 30: 0.182/0.711 (rep 0.171/0.702), 41: 0.249/0.745, 46: 0.305/0.758 (rep 0.291/0.763), 47: 0.309/0.781, 50: 0.354/0.792 (rep 0.344/0.778), 55: 0.388/0.806, 63: 0.442/0.850, 71: 0.560/0.875, 74: 0.580/0.877, 75: 0.585/0.875 (rep 0.599/0.881), 86: 0.685/0.912, 99: 0.800/0.939, 100: 0.794/0.945 (rep 0.811/0.938), 113: 0.881/0.953, 117: 0.895/0.964 (rep 0.879/0.967), 128: 0.923/0.964, 150: 0.976/0.986 (rep 0.970/0.985), 200: 0.998/0.997 (rep 0.998/0.996), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- G1.RTH.15: 10: 0.143/0.309 (rep 0.124/0.311), 15: 0.172/0.354 (rep 0.187/0.363), 20: 0.215/0.398 (rep 0.198/0.406), 30: 0.275/0.509 (rep 0.276/0.499), 47: 0.429/0.694, 50: 0.435/0.706 (rep 0.434/0.712), 54: 0.468/0.734, 62: 0.510/0.799, 72: 0.499/0.847, 75: 0.511/0.866 (rep 0.498/0.875), 81: 0.510/0.897, 88: 0.487/0.920 (rep 0.497/0.912), 100: 0.471/0.948 (rep 0.477/0.949), 150: 0.588/0.991 (rep 0.595/0.993), 200: 0.679/1.000 (rep 0.693/1.000), 224: 0.751/1.000 (rep 0.726/1.000), 232: 0.751/1.000, 267: 0.801/1.000, 300: 0.856/1.000 (rep 0.851/1.000), 307: 0.869/1.000, 347: 0.912/1.000, 500: 0.979/1.000 (rep 0.984/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)

## 11. Re-verification after the unit correction (appended 2026-09-22)

Lead follow-up after the Task 5d adversarial review (finding R-1): every trial module trades
QUANTITY_MICROS = 1 (D-H2 and RT7 size 1 to 5 by rule), so the trial series verified in sections 2 to 5
above (`daily_net_usd / 2.5`) was at half the per-micro scale. `reports/stage_d1e_members_trials.json`
was regenerated with `daily_net_ticks_per_micro` (each round trip divided by its own quantity) and the
power run repeated at eps_day = 34, now confirmed on the finished 100-row extension file. Sections 2 to 5
and 8 to 9 above describe the superseded run (kept as the record of what was verified then); this section
supersedes them for every trial and Family H figure. Statistics were not touched (item 5 confirms it).

Inputs for this pass (sha256): stage_d1e_power.json 29b0e03e16edfd7d1b0fe09ed0e03963d03127e978dd88c79c5160d77ad793ca
(generated 2026-09-22T07:04:19Z, eps_day 34, runtime 43 s); stage_d1e_members_trials.json
f546e3f325b07267988fccaf30550e04e59e12f4765805073f0e1d505d648e74 (07:00:14Z, unit_note present);
stage_d1e_members_events.json c6db647f… (unchanged); stage_d1e_coverage.md
63e18451e4e5947863be23dd031d87bc23a34b2c932493491d93bb5fac98dc61 (proxies 200/230);
stage_d1e_gate_extension.json d569e261f0eb9297aa7af2c78fb09b65e113adb6c3f9009b2d6fa94867d06858 (100 rows,
finished); snapshot of the earlier run
`/tmp/claude-1000/-home-kiros-li-Documents-GitHub-PropExperiment/fbadc349-fea7-48e6-b228-64f8d81e2cc2/lead-scratch/power_eps34_micros2_SNAPSHOT.json`
sha256 c1f2d833… (= the file verified in sections 1 to 9). Scratch script re-run as
`uv run python reports/_d1e_power_verify_scratch.py --v2 --snapshot <snapshot> [--sim --members ...]`
(the `--v2` switch reads the per-micro series, rebuilds it from the trip lists, and uses the 200/230 proxies).
Holdout status re-checked: `unlocks_logged: 0`, `all_ok: true`.

| item | verdict | size of any discrepancy |
|---|---|---|
| (1) per-micro trial series rebuilt from trips | VERIFIED | max abs diff 2.3e-13 on all 31; equals usd/1.25 for exactly the 29 fixed-size trials; differs for D-H2 and RT7 |
| (2) SD_day, VIF_boot, n_a, n_b for 31 trials and 6 H rows | VERIFIED | all < 1e-4 %; all 74 analytic n identical |
| (3) re-simulation of the six binding members | VERIFIED WITH NOTES | 12/12 arm-checks consistent (worst 3.7 %); E-H1 arm a crosses 0.80 non-monotonically, see 11.3 |
| (4) chosen-figure rule, N_C6 = 181, class tables, resolution ranges, 47 of 95 | VERIFIED | rule holds on all 190 arm-cases; 181 exact; 42/42 resolution cells; 47 of 95 with the same member set |
| (5) 64 statistic rows unchanged | VERIFIED | byte-identical to the snapshot; member order, meta, supplied_days, holdout2 identical |
| eps_day on the finished extension file | VERIFIED | 34 (min passing cell still the grid's $87.48; smallest extension pass $92.02; T = 32 rows all above $188) |

### 11.1 Item (1): the per-micro trial series
Rebuilt independently: trips assigned to dates in order by `daily_n_trips`, each trip contributing
`trip_pnl_usd / (1.25 x trip_micros)`. Compared with the file's `daily_net_ticks_per_micro`, with
`daily_net_usd / 1.25` (the 1-micro reading) and with the superseded `daily_net_usd / 2.5`.

| trial | trips | coded_micros | distinct trip_micros | mean_trip_micros file / mine | max abs diff file vs rebuilt from trips | max abs diff file vs usd/1.25 | max abs diff file vs usd/2.5 | SD_day usd/2.5 (old) | SD_day per-micro (new) | ratio |
|---|---|---|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | 276 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 1.3e+02 | 16.9395 | 33.8790 | 2.0000 |
| A-H2 rth close window (buy) | 266 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 1.0e+02 | 25.8109 | 51.6218 | 2.0000 |
| A-H2 rth close window (sell) | 266 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 1.0e+02 | 25.8483 | 51.6965 | 2.0000 |
| A-H3 weekend effect | 110 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 4.3e+02 | 61.7322 | 123.4644 | 2.0000 |
| A-H4 eth leg | 277 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 2.9e+02 | 68.2688 | 136.5376 | 2.0000 |
| A-H4 rth leg | 276 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 1.0e+03 | 111.9947 | 223.9894 | 2.0000 |
| B-H1 opening-range breakout (hold 5) | 276 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 7.4e+01 | 13.2023 | 26.4046 | 2.0000 |
| B-H1 opening-range breakout (hold 75) | 276 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 2.6e+02 | 48.6262 | 97.2524 | 2.0000 |
| B-H2 prior-day stop cascade | 223 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 9.6e+01 | 18.5453 | 37.0905 | 2.0000 |
| B-H3 breakout leg | 274 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 1.5e+02 | 29.0189 | 58.0378 | 2.0000 |
| B-H3 fade leg | 274 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 1.5e+02 | 29.0166 | 58.0333 | 2.0000 |
| B-H4 narrow-range breakout | 115 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 9.5e+01 | 13.7457 | 27.4914 | 2.0000 |
| C-H1 magnitude-conditioned reversal | 40743 | 1 | [1] | 1.0 / 1.000000 | 2.3e-13 | 1.1e-13 | 5.1e+02 | 104.0299 | 208.0599 | 2.0000 |
| C-H2 post-spike exhaustion fade | 8829 | 1 | [1] | 1.0 / 1.000000 | 2.3e-13 | 5.7e-14 | 3.3e+02 | 46.6500 | 93.3001 | 2.0000 |
| C-H3 close-location-value reversal | 12066 | 1 | [1] | 1.0 / 1.000000 | 1.1e-13 | 5.7e-14 | 6.9e+02 | 58.4357 | 116.8715 | 2.0000 |
| D-H1 trailing-vol regime gate | 106 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 2.9e+01 | 4.1528 | 8.3056 | 2.0000 |
| D-H2 inverse-vol sizing | 276 | 1..5 by rule | [1, 2, 3, 4, 5] | 3.4239130434782608 / 3.423913 | 0.0e+00 | 1.7e+02 | 7.7e+01 | 27.8598 | 22.9897 | 0.8252 |
| D-H3 range-compression gate | 2846 | 1 | [1] | 1.0 / 1.000000 | 5.7e-14 | 2.8e-14 | 1.5e+02 | 32.0044 | 64.0088 | 2.0000 |
| D-H4 overnight gap fade | 134 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 1.0e+02 | 9.6860 | 19.3721 | 2.0000 |
| E-H1 scheduled macro drift | 31 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 2.8e+02 | 25.1426 | 50.2852 | 2.0000 |
| E-H2 post-release momentum | 25 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 3.9e+01 | 4.7136 | 9.4271 | 2.0000 |
| E-H3 quarterly witching short | 4 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 1.1e+01 | 0.9323 | 1.8647 | 2.0000 |
| E-H4 turn-of-month long | 55 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 2.8e+01 | 2.6818 | 5.3636 | 2.0000 |
| C-H4 passive-fill reversal | 26723 | 1 | [1] | 1.0 / 1.000000 | 1.1e-13 | 1.1e-13 | 4.8e+02 | 95.2717 | 190.5433 | 2.0000 |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | 273 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 6.3e+01 | 12.4155 | 24.8309 | 2.0000 |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | 273 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 4.1e+02 | 48.0838 | 96.1675 | 2.0000 |
| RT3 B-H3 breakout leg 5-min bars | 273 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 2.8e+02 | 31.5774 | 63.1549 | 2.0000 |
| RT4 B-H3 fade leg 5-min bars | 273 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 2.8e+02 | 31.5758 | 63.1516 | 2.0000 |
| RT5 C-H2 spike fade 5-min bars | 2824 | 1 | [1] | 1.0 / 1.000000 | 4.3e-14 | 5.7e-14 | 2.3e+02 | 33.8556 | 67.7112 | 2.0000 |
| RT6 D-H1 daily-vol regime gate | 134 | 1 | [1] | 1.0 / 1.000000 | 0.0e+00 | 0.0e+00 | 5.1e+01 | 5.6034 | 11.2069 | 2.0000 |
| RT7 D-H2 daily-vol sizing | 257 | 1..5 by rule | [1, 2, 3] | 1.7782101167315174 / 1.778210 | 0.0e+00 | 6.9e+01 | 5.1e+01 | 17.1565 | 19.3955 | 1.1305 |

Rebuild-from-trips mismatches above 1e-9: none. Series equal to usd/1.25: 29 (all trials whose
`trip_micros` are all 1, `coded_micros` = 1); differing: D-H2 inverse-vol sizing (`trip_micros` in 1..5,
mean 3.4239, matching the file's `mean_trip_micros`) and RT7 D-H2 daily-vol sizing (1..3, mean 1.7782).
Consequence for the scale: SD_day doubles exactly (ratio 2.000000) for the 29, and becomes 0.8252 x and
1.1305 x the old figure for D-H2 and RT7, which are the only two trials whose lag-1 autocorrelation and
VIF_boot changed (D-H2 lag1 -0.016 -> +0.036, VIF 0.770 -> 0.985; RT7 lag1 +0.023 -> +0.068, VIF 0.852 ->
0.957; a per-trip quantity that varies with the vol regime changes the shape of the daily series, not
only its scale). Verdict: **VERIFIED**.

### 11.2 Item (2): SD_day, VIF_boot, n_a, n_b for the 31 trials and 6 H rows
Recomputed from the per-micro series exactly as in section 2 (same formulas, quantiles and eps = 34);
Family H from per-trade SD 200 (H1-H5) and 230 (H6) with the unchanged firing fractions. Worst |relative
difference| over all 101 members: r, SD_day, VIF_boot all 0.0000 % (< 1e-4 %); all 101 n_a and 101 n_b
identical; eps_min, eps_ref_days, n_b_sensitivity, cluster_vif identical as before. The 37 rows that
changed:

| member | kind | r rep | r mine | d% | SD rep | SD mine | d% | VIF rep | VIF mine | d% | lag1 rep | lag1 mine | n_a rep | n_a mine | n_b rep | n_b mine | eps/trade rep | mine | status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | trial | 0.9550 | 0.9550 | +0.000 | 33.879 | 33.879 | +0.000 | 0.8903 | 0.8903 | +0.000 | +0.0043 | +0.0043 | 14 | 14 | 6 | 6 | 35.601 | 35.601 | ok |
| A-H2 rth close window (buy) | trial | 0.9204 | 0.9204 | +0.000 | 51.622 | 51.622 | +0.000 | 0.9725 | 0.9725 | +0.000 | -0.0863 | -0.0863 | 36 | 36 | 14 | 14 | 36.940 | 36.940 | ok |
| A-H2 rth close window (sell) | trial | 0.9204 | 0.9204 | +0.000 | 51.697 | 51.697 | +0.000 | 0.9748 | 0.9748 | +0.000 | -0.0863 | -0.0863 | 36 | 36 | 14 | 14 | 36.940 | 36.940 | ok |
| A-H3 weekend effect | trial | 0.3806 | 0.3806 | +0.000 | 123.464 | 123.464 | +0.000 | 0.9871 | 0.9871 | +0.000 | +0.1222 | +0.1222 | 206 | 206 | 81 | 81 | 89.327 | 89.327 | ok |
| A-H4 eth leg | trial | 0.9585 | 0.9585 | +0.000 | 136.538 | 136.538 | +0.000 | 0.8777 | 0.8777 | -0.000 | -0.0128 | -0.0128 | 224 | 224 | 88 | 88 | 35.473 | 35.473 | ok |
| A-H4 rth leg | trial | 0.9550 | 0.9550 | +0.000 | 223.989 | 223.989 | +0.000 | 0.5520 | 0.5520 | +0.000 | -0.3006 | -0.3006 | 379 | 379 | 149 | 149 | 35.601 | 35.601 | ok |
| B-H1 opening-range breakout (hold 5) | trial | 0.9550 | 0.9550 | +0.000 | 26.405 | 26.405 | +0.000 | 0.9704 | 0.9704 | +0.000 | +0.1087 | +0.1087 | 10 | 10 | 4 | 4 | 35.601 | 35.601 | ok |
| B-H1 opening-range breakout (hold 75) | trial | 0.9550 | 0.9550 | +0.000 | 97.252 | 97.252 | +0.000 | 0.9217 | 0.9217 | +0.000 | -0.0865 | -0.0865 | 120 | 120 | 47 | 47 | 35.601 | 35.601 | ok |
| B-H2 prior-day stop cascade | trial | 0.7716 | 0.7716 | +0.000 | 37.091 | 37.091 | +0.000 | 1.2119 | 1.2119 | +0.000 | +0.0874 | +0.0874 | 23 | 23 | 9 | 9 | 44.063 | 44.063 | ok |
| B-H3 breakout leg | trial | 0.9481 | 0.9481 | +0.000 | 58.038 | 58.038 | +0.000 | 0.8169 | 0.8169 | -0.000 | -0.0531 | -0.0531 | 38 | 38 | 15 | 15 | 35.861 | 35.861 | ok |
| B-H3 fade leg | trial | 0.9481 | 0.9481 | +0.000 | 58.033 | 58.033 | +0.000 | 0.8184 | 0.8184 | +0.000 | -0.0550 | -0.0550 | 38 | 38 | 15 | 15 | 35.861 | 35.861 | ok |
| B-H4 narrow-range breakout | trial | 0.3979 | 0.3979 | +0.000 | 27.491 | 27.491 | +0.000 | 0.7346 | 0.7346 | -0.000 | -0.0351 | -0.0351 | 8 | 8 | 3 | 3 | 85.443 | 85.443 | ok |
| C-H1 magnitude-conditioned reversal | trial | 140.9792 | 140.9792 | +0.000 | 208.060 | 208.060 | +0.000 | 0.7988 | 0.7988 | +0.000 | -0.0910 | -0.0910 | 473 | 473 | 185 | 185 | 0.241 | 0.241 | ok |
| C-H2 post-spike exhaustion fade | trial | 30.5502 | 30.5502 | +0.000 | 93.300 | 93.300 | +0.000 | 1.1675 | 1.1675 | -0.000 | +0.1772 | +0.1772 | 139 | 139 | 55 | 55 | 1.113 | 1.113 | ok |
| C-H3 close-location-value reversal | trial | 41.7509 | 41.7509 | +0.000 | 116.871 | 116.871 | +0.000 | 0.7883 | 0.7883 | +0.000 | +0.0885 | +0.0885 | 148 | 148 | 58 | 58 | 0.814 | 0.814 | ok |
| D-H1 trailing-vol regime gate | trial | 0.3668 | 0.3668 | +0.000 | 8.306 | 8.306 | +0.000 | 0.9129 | 0.9129 | +0.000 | -0.0192 | -0.0192 | 1 | 1 | 1 | 1 | 92.698 | 92.698 | ok |
| D-H2 inverse-vol sizing | trial | 0.9550 | 0.9550 | +0.000 | 22.990 | 22.990 | +0.000 | 0.8587 | 0.8587 | +0.000 | +0.0356 | +0.0356 | 7 | 7 | 3 | 3 | 35.601 | 35.601 | ok |
| D-H3 range-compression gate | trial | 9.8478 | 9.8478 | +0.000 | 64.009 | 64.009 | +0.000 | 0.9447 | 0.9447 | +0.000 | +0.0074 | +0.0074 | 53 | 53 | 21 | 21 | 3.453 | 3.453 | ok |
| D-H4 overnight gap fade | trial | 0.4637 | 0.4637 | +0.000 | 19.372 | 19.372 | +0.000 | 1.1393 | 1.1393 | +0.000 | +0.0228 | +0.0228 | 6 | 6 | 3 | 3 | 73.328 | 73.328 | ok |
| E-H1 scheduled macro drift | trial | 0.1073 | 0.1073 | +0.000 | 50.285 | 50.285 | +0.000 | 1.1762 | 1.1762 | -0.000 | -0.0018 | -0.0018 | 41 | 41 | 16 | 16 | 316.968 | 316.968 | ok |
| E-H2 post-release momentum | trial | 0.0865 | 0.0865 | +0.000 | 9.427 | 9.427 | +0.000 | 0.9479 | 0.9479 | +0.000 | -0.0000 | -0.0000 | 2 | 2 | 1 | 1 | 393.040 | 393.040 | ok |
| E-H3 quarterly witching short | trial | 0.0138 | 0.0138 | +0.000 | 1.865 | 1.865 | +0.000 | 0.9884 | 0.9884 | +0.000 | -0.0015 | -0.0015 | 1 | 1 | 1 | 1 | 2456.500 | 2456.500 | ok |
| E-H4 turn-of-month long | trial | 0.1903 | 0.1903 | +0.000 | 5.364 | 5.364 | +0.000 | 0.8995 | 0.8995 | -0.000 | +0.0743 | +0.0743 | 1 | 1 | 1 | 1 | 178.655 | 178.655 | ok |
| C-H4 passive-fill reversal | trial | 92.4671 | 92.4671 | +0.000 | 190.543 | 190.543 | +0.000 | 0.9272 | 0.9272 | +0.000 | +0.0128 | +0.0128 | 461 | 461 | 181 | 181 | 0.368 | 0.368 | ok |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | trial | 0.9446 | 0.9446 | +0.000 | 24.831 | 24.831 | +0.000 | 0.9644 | 0.9644 | +0.000 | +0.0520 | +0.0520 | 9 | 9 | 4 | 4 | 35.993 | 35.993 | ok |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | trial | 0.9446 | 0.9446 | +0.000 | 96.168 | 96.168 | +0.000 | 1.3629 | 1.3629 | +0.000 | +0.1728 | +0.1728 | 173 | 173 | 68 | 68 | 35.993 | 35.993 | ok |
| RT3 B-H3 breakout leg 5-min bars | trial | 0.9446 | 0.9446 | +0.000 | 63.155 | 63.155 | +0.000 | 0.9070 | 0.9070 | +0.000 | -0.0518 | -0.0518 | 50 | 50 | 20 | 20 | 35.993 | 35.993 | ok |
| RT4 B-H3 fade leg 5-min bars | trial | 0.9446 | 0.9446 | +0.000 | 63.152 | 63.152 | +0.000 | 0.9060 | 0.9060 | +0.000 | -0.0529 | -0.0529 | 50 | 50 | 20 | 20 | 35.993 | 35.993 | ok |
| RT5 C-H2 spike fade 5-min bars | trial | 9.7716 | 9.7716 | +0.000 | 67.711 | 67.711 | +0.000 | 0.9717 | 0.9717 | -0.000 | +0.0703 | +0.0703 | 61 | 61 | 24 | 24 | 3.479 | 3.479 | ok |
| RT6 D-H1 daily-vol regime gate | trial | 0.4637 | 0.4637 | +0.000 | 11.207 | 11.207 | +0.000 | 0.9439 | 0.9439 | -0.000 | +0.0765 | +0.0765 | 2 | 2 | 1 | 1 | 73.328 | 73.328 | ok |
| RT7 D-H2 daily-vol sizing | trial | 0.8893 | 0.8893 | +0.000 | 19.396 | 19.396 | +0.000 | 0.8595 | 0.8595 | +0.000 | +0.0400 | +0.0400 | 5 | 5 | 2 | 2 | 38.233 | 38.233 | ok |
| H1 NR4 opening-range breakout | projected | 0.2250 | 0.2250 | +0.000 | 94.868 | 94.868 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 124 | 124 | 49 | 49 | 151.111 | 151.111 | ok |
| H2 NR7 opening-range breakout | projected | 0.1286 | 0.1286 | -0.000 | 71.714 | 71.714 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 71 | 71 | 28 | 28 | 264.444 | 264.444 | ok |
| H3 inside-day opening-range breakout | projected | 0.2250 | 0.2250 | +0.000 | 94.868 | 94.868 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 124 | 124 | 49 | 49 | 151.111 | 151.111 | ok |
| H4 bottom-tercile prior range, breakout | projected | 0.3000 | 0.3000 | +0.000 | 109.545 | 109.545 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 165 | 165 | 65 | 65 | 113.333 | 113.333 | ok |
| H5 top-tercile prior range, opening-range fade | projected | 0.3000 | 0.3000 | +0.000 | 109.545 | 109.545 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 165 | 165 | 65 | 65 | 113.333 | 113.333 | ok |
| H6 prior-close location follow-through | projected | 0.4000 | 0.4000 | +0.000 | 145.465 | 145.465 | +0.000 | 1.0000 | 1.0000 | +0.000 | +0.0000 | +0.0000 | 290 | 290 | 114 | 114 | 85.000 | 85.000 | ok |

Family H:

| member | SD_trade | f | SD_day rep | SD_day mine | r rep | r mine | n_a rep | mine | n_b rep | mine | eps/trade rep | mine |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 NR4 opening-range breakout | 200.0 | 0.225000 | 94.8683 | 94.8683 | 0.225000 | 0.225000 | 124 | 124 | 49 | 49 | 151.111 | 151.111 |
| H2 NR7 opening-range breakout | 200.0 | 0.128571 | 71.7137 | 71.7137 | 0.128571 | 0.128571 | 71 | 71 | 28 | 28 | 264.444 | 264.444 |
| H3 inside-day opening-range breakout | 200.0 | 0.225000 | 94.8683 | 94.8683 | 0.225000 | 0.225000 | 124 | 124 | 49 | 49 | 151.111 | 151.111 |
| H4 bottom-tercile prior range, breakout | 200.0 | 0.300000 | 109.5445 | 109.5445 | 0.300000 | 0.300000 | 165 | 165 | 65 | 65 | 113.333 | 113.333 |
| H5 top-tercile prior range, opening-range fade | 200.0 | 0.300000 | 109.5445 | 109.5445 | 0.300000 | 0.300000 | 165 | 165 | 65 | 65 | 113.333 | 113.333 |
| H6 prior-close location follow-through | 230.0 | 0.400000 | 145.4648 | 145.4648 | 0.400000 | 0.400000 | 290 | 290 | 114 | 114 | 85.000 | 85.000 |

Scale check against the snapshot (statistics omitted, identical): SD_day ratio exactly 2 for the 29
fixed-size trials, VIF and lag1 unchanged for them; n_b roughly x4 (A-H4 rth leg 38 -> 149, C-H4 46 -> 181,
E-H1 4 -> 16, C-H1 47 -> 185), n_a likewise (95 -> 379, 116 -> 461, 11 -> 41, 119 -> 473).

| trial | SD_day snapshot | SD_day now | ratio | n_b snapshot | n_b now | n_a snapshot | n_a now | VIF same | lag1 same |
|---|---|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | 16.9395 | 33.8790 | 2.000000 | 2 | 6 | 4 | 14 | True | True |
| A-H2 rth close window (buy) | 25.8109 | 51.6218 | 2.000000 | 4 | 14 | 9 | 36 | True | True |
| A-H2 rth close window (sell) | 25.8483 | 51.6965 | 2.000000 | 4 | 14 | 9 | 36 | True | True |
| A-H3 weekend effect | 61.7322 | 123.4644 | 2.000000 | 21 | 81 | 52 | 206 | True | True |
| A-H4 eth leg | 68.2688 | 136.5376 | 2.000000 | 22 | 88 | 56 | 224 | True | True |
| A-H4 rth leg | 111.9947 | 223.9894 | 2.000000 | 38 | 149 | 95 | 379 | True | True |
| B-H1 opening-range breakout (hold 5) | 13.2023 | 26.4046 | 2.000000 | 1 | 4 | 3 | 10 | True | True |
| B-H1 opening-range breakout (hold 75) | 48.6262 | 97.2524 | 2.000000 | 12 | 47 | 30 | 120 | True | True |
| B-H2 prior-day stop cascade | 18.5453 | 37.0905 | 2.000000 | 3 | 9 | 6 | 23 | True | True |
| B-H3 breakout leg | 29.0189 | 58.0378 | 2.000000 | 4 | 15 | 10 | 38 | True | True |
| B-H3 fade leg | 29.0166 | 58.0333 | 2.000000 | 4 | 15 | 10 | 38 | True | True |
| B-H4 narrow-range breakout | 13.7457 | 27.4914 | 2.000000 | 1 | 3 | 2 | 8 | True | True |
| C-H1 magnitude-conditioned reversal | 104.0299 | 208.0599 | 2.000000 | 47 | 185 | 119 | 473 | True | True |
| C-H2 post-spike exhaustion fade | 46.6500 | 93.3001 | 2.000000 | 14 | 55 | 35 | 139 | True | True |
| C-H3 close-location-value reversal | 58.4357 | 116.8715 | 2.000000 | 15 | 58 | 37 | 148 | True | True |
| D-H1 trailing-vol regime gate | 4.1528 | 8.3056 | 2.000000 | 1 | 1 | 1 | 1 | True | True |
| D-H2 inverse-vol sizing | 27.8598 | 22.9897 | 0.825193 | 4 | 3 | 9 | 7 | False | False |
| D-H3 range-compression gate | 32.0044 | 64.0088 | 2.000000 | 6 | 21 | 14 | 53 | True | True |
| D-H4 overnight gap fade | 9.6860 | 19.3721 | 2.000000 | 1 | 3 | 2 | 6 | True | True |
| E-H1 scheduled macro drift | 25.1426 | 50.2852 | 2.000000 | 4 | 16 | 11 | 41 | True | True |
| E-H2 post-release momentum | 4.7136 | 9.4271 | 2.000000 | 1 | 1 | 1 | 2 | True | True |
| E-H3 quarterly witching short | 0.9323 | 1.8647 | 2.000000 | 1 | 1 | 1 | 1 | True | True |
| E-H4 turn-of-month long | 2.6818 | 5.3636 | 2.000000 | 1 | 1 | 1 | 1 | True | True |
| C-H4 passive-fill reversal | 95.2717 | 190.5433 | 2.000000 | 46 | 181 | 116 | 461 | True | True |
| RT1 B-H1 ORB 5-min bars (hold 1 bar) | 12.4155 | 24.8309 | 2.000000 | 1 | 4 | 3 | 9 | True | True |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | 48.0838 | 96.1675 | 2.000000 | 17 | 68 | 44 | 173 | True | True |
| RT3 B-H3 breakout leg 5-min bars | 31.5774 | 63.1549 | 2.000000 | 5 | 20 | 13 | 50 | True | True |
| RT4 B-H3 fade leg 5-min bars | 31.5758 | 63.1516 | 2.000000 | 5 | 20 | 13 | 50 | True | True |
| RT5 C-H2 spike fade 5-min bars | 33.8556 | 67.7112 | 2.000000 | 6 | 24 | 16 | 61 | True | True |
| RT6 D-H1 daily-vol regime gate | 5.6034 | 11.2069 | 2.000000 | 1 | 1 | 1 | 2 | True | True |
| RT7 D-H2 daily-vol sizing | 17.1565 | 19.3955 | 1.130504 | 2 | 2 | 4 | 5 | False | False |

Verdict: **VERIFIED**.

### 11.3 Item (3): re-simulation of the six binding members
Same construction as section 3 (correction 2), own seed 7771, 2,000 replications, both arms, 4 processes,
2.4 s wall (the CPU is no longer shared with the gate-extension job). Members: A-H4 rth leg (C1, 149),
G3.RTH.5 (C2, 193), F1_1_h1_RTH (C3, 566), F2_4_15min_vol_tercile_top (C4, 171), E-H1 scheduled macro
drift (C5, 16), C-H4 passive-fill reversal (C6, 181). C7's H6 (114) is projected and not simulated.

| member | arm | analytic | reported sim | censored rep | mine grid-matched | mine refined | MC se (n) | rel diff grid-matched % | rel diff refined % | tolerance % | verdict | rule outcome mine (refined) vs rep chosen |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A-H4 rth leg | a | 379 | 374.47 | False | 380.27 | 373.46 | 7.59 | 1.5 | -0.3 | 10.0 | consistent | within_band -> 379 vs rep 379 |
| A-H4 rth leg | b | 149 | 161.03 | False | 162.13 | 156.01 | 5.84 | 0.7 | -3.1 | 10.0 | consistent | within_band -> 149 vs rep 149 |
| G3.RTH.5 | a | 492 | 517.94 | False | 498.97 | 498.97 | 3.80 | -3.7 | -3.7 | 10.0 | consistent | within_band -> 492 vs rep 492 |
| G3.RTH.5 | b | 193 | 181.66 | False | 180.39 | 184.99 | 4.66 | -0.7 | 1.8 | 10.0 | consistent | within_band -> 193 vs rep 193 |
| F1_1_h1_RTH | a | 1447 | 1,469.69 | False | 1,416.34 | 1,417.71 | 23.97 | -3.6 | -3.5 | 10.0 | consistent | within_band -> 1447 vs rep 1447 |
| F1_1_h1_RTH | b | 566 | 570.57 | False | 553.54 | 553.54 | 16.61 | -3.0 | -3.0 | 10.0 | consistent | within_band -> 566 vs rep 566 |
| F2_4_15min_vol_tercile_top | a | 436 | 458.46 | False | 463.10 | 460.04 | 8.90 | 1.0 | 0.3 | 10.0 | consistent | within_band -> 436 vs rep 436 |
| F2_4_15min_vol_tercile_top | b | 171 | 152.29 | False | 155.96 | 157.93 | 5.04 | 2.4 | 3.7 | 10.0 | consistent | within_band -> 171 vs rep 171 |
| E-H1 scheduled macro drift | a | 41 | 13.73 | False | 13.48 | 13.23 | 0.76 | -1.9 | -3.6 | 11.0 | consistent | smaller_ignored -> 41 vs rep 41 |
| E-H1 scheduled macro drift | b | 16 | 10.00 | True | 10.00 (cens) | 10.00 (cens) | - | 0.0 | 0.0 | - | consistent (both censored at grid floor) | censored -> 16 vs rep 16 |
| C-H4 passive-fill reversal | a | 461 | 474.82 | False | 466.99 | 464.73 | 15.52 | -1.6 | -2.1 | 10.0 | consistent | within_band -> 461 vs rep 461 |
| C-H4 passive-fill reversal | b | 181 | 173.60 | False | 173.32 | 174.00 | 5.35 | -0.2 | 0.2 | 10.0 | consistent | within_band -> 181 vs rep 181 |

| member | n (chosen_b) | rep power_b | mine power_b | n (chosen_a) | rep power_a | mine power_a | zero-var draws mine (all lengths) | rep sim_zero_variance_draws |
|---|---|---|---|---|---|---|---|---|
| A-H4 rth leg | 149 | 0.7970 | 0.7885 | 379 | 0.8070 | 0.7985 | 0 | 0 |
| G3.RTH.5 | 193 | 0.8245 | 0.8260 | 492 | 0.7725 | 0.7830 | 0 | 0 |
| F1_1_h1_RTH | 566 | 0.7975 | 0.8070 | 1447 | 0.7920 | 0.8140 | 0 | 0 |
| F2_4_15min_vol_tercile_top | 171 | 0.8460 | 0.8260 | 436 | 0.7780 | 0.7705 | 0 | 0 |
| E-H1 scheduled macro drift | 16 | 0.9210 | 0.9225 | 41 | 0.7920 | 0.7835 | 276 | 258 |
| C-H4 passive-fill reversal | 181 | 0.8150 | 0.8135 | 461 | 0.7860 | 0.7965 | 0 | 0 |

All 12 arm-checks consistent; the three statistic members reproduce the section-3 figures exactly
(same series, same seed). The re-derived rule outcome matches every reported chosen figure, including
N_C6 = 181 (C-H4: analytic 181, simulated 173.6 reported / 173.3 mine, -4.1 %, inside the band, no flag).
A-H4 rth leg's n_b_sim is now 161.0 (+8.1 %; mine 162.1 / 156.0), inside the band, so 149 stands; at
n = 149 the simulated null power is 0.797 reported / 0.789 mine, i.e. 0.80 within MC noise.

Note on E-H1 arm a (31 trades in 289 days). The reported n_a_sim = 13.73 is the FIRST crossing of 0.80,
but the detection-power curve is not monotone for this sparse series: it reaches 0.81-0.84 at n = 14-30,
falls back to 0.792 at the chosen n_a = 41 (mine 0.783) and 0.774 at 50 (mine 0.762), and only stays
above 0.80 from about n = 70 (0.832 at 75). The 3.3-se drop 30 -> 41 is flagged by my monotonicity check
and reproduced in my run, so it is a property of the series (a 41-day window holds about 4.4 trades and
the replicate SD is right-skewed), not MC noise. The chosen-figure rule handled it as designed
(`sim_smaller_ignored_a`, analytic 41 kept), so no figure is wrong under the rule; but the simulated
detection power at the chosen 41 days is about 0.79, and a monotone reading of the curve would put the
80 % detection length near 70 days. n_a enters only the "days to detect" table (not the null criterion),
and C5's null-power figure n_b = 16 is unaffected (its arm b is at 0.92 there). Reported for the lead's
judgment. Verdict: **VERIFIED WITH NOTES**.

### 11.4 Item (4): chosen-figure rule, N_C6, class tables, resolution ranges, 47 of 95
Rule (correction 1) re-checked on all 95 measured members x 2 arms = 190 cases against the new JSON: no
violation; diff_pct reproduced to 1e-6; outcome counts now within band 133, censored 28 (10 a, 18 b),
smaller_ignored 19 (8 a, 11 b), used_larger 10 (the 8 of section 3.2 plus two trials whose arm-a
simulation now exceeds the analytic figure by more than 15 %). Rows where the rule changed a figure or
recorded an ignored one:

| member | arm | analytic | sim | diff rep | diff mine | censored flag | chosen rep | chosen by rule | flags rep | rule outcome | ok |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A-H1 european-open overnight drift | a | 14 | 11.8568 | -15.309 | -15.309 | False | 14 | 14 | sim_smaller_ignored_a | smaller_ignored | ok |
| A-H3 weekend effect | b | 81 | 66.5822 | -17.800 | -17.800 | False | 81 | 81 | sim_smaller_ignored_b | smaller_ignored | ok |
| C-H2 post-spike exhaustion fade | b | 55 | 45.2047 | -17.810 | -17.810 | False | 55 | 55 | sim_smaller_ignored_b | smaller_ignored | ok |
| C-H3 close-location-value reversal | a | 148 | 184.1210 | 24.406 | 24.406 | False | 185 | 185 | sim_used_larger_a | used_larger | ok |
| C-H3 close-location-value reversal | b | 58 | 41.7640 | -27.993 | -27.993 | False | 58 | 58 | sim_smaller_ignored_b | smaller_ignored | ok |
| D-H3 range-compression gate | b | 21 | 14.1558 | -32.591 | -32.591 | False | 21 | 21 | sim_smaller_ignored_b | smaller_ignored | ok |
| E-H1 scheduled macro drift | a | 41 | 13.7320 | -66.507 | -66.507 | False | 41 | 41 | sim_smaller_ignored_a | smaller_ignored | ok |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | a | 173 | 199.5676 | 15.357 | 15.357 | False | 200 | 200 | sim_used_larger_a | used_larger | ok |
| RT2 B-H1 ORB 5-min bars (hold 15 bars) | b | 68 | 47.2589 | -30.502 | -30.502 | False | 68 | 68 | sim_smaller_ignored_b | smaller_ignored | ok |
| RT3 B-H3 breakout leg 5-min bars | b | 20 | 13.6515 | -31.742 | -31.742 | False | 20 | 20 | sim_smaller_ignored_b | smaller_ignored | ok |
| RT4 B-H3 fade leg 5-min bars | b | 20 | 14.8712 | -25.644 | -25.644 | False | 20 | 20 | sim_smaller_ignored_b | smaller_ignored | ok |
| RT7 D-H2 daily-vol sizing | a | 5 | 3.9648 | -20.703 | -20.703 | False | 5 | 5 | sim_smaller_ignored_a | smaller_ignored | ok |
| F4_4_round_number_multiples_of_100 | a | 117 | 98.5219 | -15.793 | -15.793 | False | 117 | 117 | sim_smaller_ignored_a | smaller_ignored | ok |
| F4_4_round_number_multiples_of_100 | b | 46 | 54.5004 | 18.479 | 18.479 | False | 55 | 55 | sim_used_larger_b | used_larger | ok |
| F4_1_rth_open_crossing | b | 20 | 16.6598 | -16.701 | -16.701 | False | 20 | 20 | sim_smaller_ignored_b | smaller_ignored | ok |
| G4.RTH.5 | b | 46 | 54.0241 | 17.444 | 17.444 | False | 55 | 55 | sim_used_larger_b | used_larger | ok |
| G1.ETH.15 | b | 50 | 58.5127 | 17.025 | 17.025 | False | 59 | 59 | sim_used_larger_b | used_larger | ok |
| G2.ETH.15 | b | 18 | 14.1518 | -21.379 | -21.379 | False | 18 | 18 | sim_smaller_ignored_b | smaller_ignored | ok |
| G1.RTH.15 | a | 224 | 266.6027 | 19.019 | 19.019 | False | 267 | 267 | sim_used_larger_a | used_larger | ok |
| G1.RTH.15 | b | 88 | 62.2774 | -29.230 | -29.230 | False | 88 | 88 | sim_smaller_ignored_b | smaller_ignored | ok |
| G4.RTH.15 | a | 100 | 121.0858 | 21.086 | 21.086 | False | 122 | 122 | sim_used_larger_a | used_larger | ok |
| G4.RTH.15 | b | 39 | 27.8638 | -28.554 | -28.554 | False | 39 | 39 | sim_smaller_ignored_b | smaller_ignored | ok |
| G1.ETH.30 | b | 23 | 18.7329 | -18.553 | -18.553 | False | 23 | 23 | sim_smaller_ignored_b | smaller_ignored | ok |
| G4.RTH.30 | a | 38 | 53.7519 | 41.452 | 41.452 | False | 54 | 54 | sim_used_larger_a | used_larger | ok |
| G4.RTH.30 | b | 15 | 12.1372 | -19.085 | -19.085 | False | 15 | 15 | sim_smaller_ignored_b | smaller_ignored | ok |
| G1.ETH.60 | a | 45 | 52.5995 | 16.888 | 16.888 | False | 53 | 53 | sim_used_larger_a | used_larger | ok |
| G1.ETH.60 | b | 18 | 15.1819 | -15.656 | -15.656 | False | 18 | 18 | sim_smaller_ignored_b | smaller_ignored | ok |
| G2.ETH.60 | b | 15 | 12.0830 | -19.446 | -19.446 | False | 15 | 15 | sim_smaller_ignored_b | smaller_ignored | ok |
| G4.RTH.60 | a | 48 | 56.0233 | 16.715 | 16.715 | False | 57 | 57 | sim_used_larger_a | used_larger | ok |

Class blocks (typical_r, eps_trade, gross_equivalent_trade, binding members, supplied days, achievable
flags): all exact; the only non-achievable cells remain C3 at the 2022 and 2023 starts. N_C6 = 181 is
C-H4's chosen_b = analytic n_b (ceil of 180.1 at SD 190.54, VIF 0.927).

| class | n members | typical_r rep | mine | eps_trade rep | mine | gross rep | mine | binding_a rep | mine | binding_b rep | mine | achievable flags ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 6 | 0.937716 | 0.937716 | 36.2583 | 36.2583 | 38.3683 | 38.3683 | A-H4 rth leg (379) | A-H4 rth leg (379) | A-H4 rth leg (149) | A-H4 rth leg (149) | True |
| C2 | 31 | 0.944637 | 0.944637 | 35.9927 | 35.9927 | 38.1027 | 38.1027 | G3.RTH.5 (492) | G3.RTH.5 (492) | G3.RTH.5 (193) | G3.RTH.5 (193) | True |
| C3 | 40 | 36.150519 | 36.150519 | 0.9405 | 0.9405 | 3.0505 | 3.0505 | F1_1_h1_RTH (1447) | F1_1_h1_RTH (1447) | F1_1_h1_RTH (566) | F1_1_h1_RTH (566) | True |
| C4 | 13 | 0.676471 | 0.676471 | 50.2609 | 50.2609 | 52.3709 | 52.3709 | F2_4_15min_vol_tercile_top (436) | F2_4_15min_vol_tercile_top (436) | F2_4_15min_vol_tercile_top (171) | F2_4_15min_vol_tercile_top (171) | True |
| C5 | 4 | 0.096886 | 0.096886 | 350.9286 | 350.9286 | 353.0386 | 353.0386 | E-H1 scheduled macro drift (41) | E-H1 scheduled macro drift (41) | E-H1 scheduled macro drift (16) | E-H1 scheduled macro drift (16) | True |
| C6 | 1 | 92.467128 | 92.467128 | 0.3677 | 0.3677 | 2.4777 | 2.4777 | C-H4 passive-fill reversal (461) | C-H4 passive-fill reversal (461) | C-H4 passive-fill reversal (181) | C-H4 passive-fill reversal (181) | True |
| C7 | 6 | 0.262500 | 0.262500 | 129.5238 | 129.5238 | 131.6338 | 131.6338 | H6 prior-close location follow-through (290) | H6 prior-close location follow-through (290) | H6 prior-close location follow-through (114) | H6 prior-close location follow-through (114) | True |

`resolution_range`: 42 of 42 class x S cells match from the members' reported fields and from my own
eps_min (values to 1e-6 %); md section 5a-bis matches the JSON.

| class | S | basis | min/trade rep | from rep fields | from mine | max/trade rep | from rep fields | from mine | min/day rep | mine | max/day rep | mine | ok |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 2019-05-06 | measured/6 vs measured/6 | 2.4532 (A-H1 european-open overnight drift) | 2.4532 (A-H1 european-open overnight drift) | 2.4532 (A-H1 european-open overnight drift) | 23.6194 (A-H3 weekend effect) | 23.6194 (A-H3 weekend effect) | 23.6194 (A-H3 weekend effect) | 2.3429 (A-H1 european-open overnight drift) | 2.3429 | 12.1969 (A-H4 rth leg) | 12.1969 | ok |
| C1 | 2019-07-01 | measured/6 vs measured/6 | 2.4936 (A-H1 european-open overnight drift) | 2.4936 (A-H1 european-open overnight drift) | 2.4936 (A-H1 european-open overnight drift) | 24.0085 (A-H3 weekend effect) | 24.0085 (A-H3 weekend effect) | 24.0085 (A-H3 weekend effect) | 2.3814 (A-H1 european-open overnight drift) | 2.3814 | 12.3978 (A-H4 rth leg) | 12.3978 | ok |
| C1 | 2020-01-02 | measured/6 vs measured/6 | 2.6425 (A-H1 european-open overnight drift) | 2.6425 (A-H1 european-open overnight drift) | 2.6425 (A-H1 european-open overnight drift) | 25.4420 (A-H3 weekend effect) | 25.4420 (A-H3 weekend effect) | 25.4420 (A-H3 weekend effect) | 2.5236 (A-H1 european-open overnight drift) | 2.5236 | 13.1380 (A-H4 rth leg) | 13.1380 | ok |
| C1 | 2021-01-04 | measured/6 vs measured/6 | 3.0290 (A-H1 european-open overnight drift) | 3.0290 (A-H1 european-open overnight drift) | 3.0290 (A-H1 european-open overnight drift) | 29.1631 (A-H3 weekend effect) | 29.1631 (A-H3 weekend effect) | 29.1631 (A-H3 weekend effect) | 2.8927 (A-H1 european-open overnight drift) | 2.8927 | 15.0596 (A-H4 rth leg) | 15.0596 | ok |
| C1 | 2022-01-03 | measured/6 vs measured/6 | 3.6639 (A-H1 european-open overnight drift) | 3.6639 (A-H1 european-open overnight drift) | 3.6639 (A-H1 european-open overnight drift) | 35.2762 (A-H3 weekend effect) | 35.2762 (A-H3 weekend effect) | 35.2762 (A-H3 weekend effect) | 3.4991 (A-H1 european-open overnight drift) | 3.4991 | 18.2164 (A-H4 rth leg) | 18.2164 | ok |
| C1 | 2023-01-03 | measured/6 vs measured/6 | 5.0007 (A-H1 european-open overnight drift) | 5.0007 (A-H1 european-open overnight drift) | 5.0007 (A-H1 european-open overnight drift) | 48.1467 (A-H3 weekend effect) | 48.1467 (A-H3 weekend effect) | 48.1467 (A-H3 weekend effect) | 4.7758 (A-H1 european-open overnight drift) | 4.7758 | 24.8626 (A-H4 rth leg) | 24.8626 | ok |
| C2 | 2019-05-06 | measured/31 vs measured/31 | 0.2998 (G2.ETH.5) | 0.2998 (G2.ETH.5) | 0.2998 (G2.ETH.5) | 13.9953 (G3.RTH.5) | 13.9953 (G3.RTH.5) | 13.9953 (G3.RTH.5) | 1.7269 (B-H4 narrow-range breakout) | 1.7269 | 13.8946 (G3.RTH.5) | 13.8946 | ok |
| C2 | 2019-07-01 | measured/31 vs measured/31 | 0.3048 (G2.ETH.5) | 0.3048 (G2.ETH.5) | 0.3048 (G2.ETH.5) | 14.2258 (G3.RTH.5) | 14.2258 (G3.RTH.5) | 14.2258 (G3.RTH.5) | 1.7553 (B-H4 narrow-range breakout) | 1.7553 | 14.1235 (G3.RTH.5) | 14.1235 | ok |
| C2 | 2020-01-02 | measured/31 vs measured/31 | 0.3229 (G2.ETH.5) | 0.3229 (G2.ETH.5) | 0.3229 (G2.ETH.5) | 15.0753 (G3.RTH.5) | 15.0753 (G3.RTH.5) | 15.0753 (G3.RTH.5) | 1.8601 (B-H4 narrow-range breakout) | 1.8601 | 14.9668 (G3.RTH.5) | 14.9668 | ok |
| C2 | 2021-01-04 | measured/31 vs measured/31 | 0.3702 (G2.ETH.5) | 0.3702 (G2.ETH.5) | 0.3702 (G2.ETH.5) | 17.2801 (G3.RTH.5) | 17.2801 (G3.RTH.5) | 17.2801 (G3.RTH.5) | 2.1322 (B-H4 narrow-range breakout) | 2.1322 | 17.1558 (G3.RTH.5) | 17.1558 | ok |
| C2 | 2022-01-03 | measured/31 vs measured/31 | 0.4478 (G2.ETH.5) | 0.4478 (G2.ETH.5) | 0.4478 (G2.ETH.5) | 20.9024 (G3.RTH.5) | 20.9024 (G3.RTH.5) | 20.9024 (G3.RTH.5) | 2.5791 (B-H4 narrow-range breakout) | 2.5791 | 20.7520 (G3.RTH.5) | 20.7520 | ok |
| C2 | 2023-01-03 | measured/31 vs measured/31 | 0.6111 (G2.ETH.5) | 0.6111 (G2.ETH.5) | 0.6111 (G2.ETH.5) | 28.5286 (G3.RTH.5) | 28.5286 (G3.RTH.5) | 28.5286 (G3.RTH.5) | 3.5201 (B-H4 narrow-range breakout) | 3.5201 | 28.3234 (G3.RTH.5) | 28.3234 | ok |
| C3 | 2019-05-06 | measured/40 vs measured/40 | 0.0162 (F1_1_h1_ETH) | 0.0162 (F1_1_h1_ETH) | 0.0162 (F1_1_h1_ETH) | 5.2157 (G4.RTH.60) | 5.2157 (G4.RTH.60) | 5.2157 (G4.RTH.60) | 2.6583 (F3_2_bucket09_bucket10) | 2.6583 | 23.8423 (F1_1_h1_RTH) | 23.8423 | ok |
| C3 | 2019-07-01 | measured/40 vs measured/40 | 0.0164 (F1_1_h1_ETH) | 0.0164 (F1_1_h1_ETH) | 0.0164 (F1_1_h1_ETH) | 5.3016 (G4.RTH.60) | 5.3016 (G4.RTH.60) | 5.3016 (G4.RTH.60) | 2.7020 (F3_2_bucket09_bucket10) | 2.7020 | 24.2350 (F1_1_h1_RTH) | 24.2350 | ok |
| C3 | 2020-01-02 | measured/40 vs measured/40 | 0.0174 (F1_1_h1_ETH) | 0.0174 (F1_1_h1_ETH) | 0.0174 (F1_1_h1_ETH) | 5.6182 (G4.RTH.60) | 5.6182 (G4.RTH.60) | 5.6182 (G4.RTH.60) | 2.8634 (F3_2_bucket09_bucket10) | 2.8634 | 25.6821 (F1_1_h1_RTH) | 25.6821 | ok |
| C3 | 2021-01-04 | measured/40 vs measured/40 | 0.0200 (F1_1_h1_ETH) | 0.0200 (F1_1_h1_ETH) | 0.0200 (F1_1_h1_ETH) | 6.4399 (G4.RTH.60) | 6.4399 (G4.RTH.60) | 6.4399 (G4.RTH.60) | 3.2822 (F3_2_bucket09_bucket10) | 3.2822 | 29.4383 (F1_1_h1_RTH) | 29.4383 | ok |
| C3 | 2022-01-03 | measured/40 vs measured/40 | 0.0242 (F1_1_h1_ETH) | 0.0242 (F1_1_h1_ETH) | 0.0242 (F1_1_h1_ETH) | 7.7898 (G4.RTH.60) | 7.7898 (G4.RTH.60) | 7.7898 (G4.RTH.60) | 3.9702 (F3_2_bucket09_bucket10) | 3.9702 | 35.6091 (F1_1_h1_RTH) | 35.6091 | ok |
| C3 | 2023-01-03 | measured/40 vs measured/40 | 0.0330 (F1_1_h1_ETH) | 0.0330 (F1_1_h1_ETH) | 0.0330 (F1_1_h1_ETH) | 10.6319 (G4.RTH.60) | 10.6319 (G4.RTH.60) | 10.6319 (G4.RTH.60) | 5.4187 (F3_2_bucket09_bucket10) | 5.4187 | 48.6011 (F1_1_h1_RTH) | 48.6011 | ok |
| C4 | 2019-05-06 | measured/13 vs measured/13 | 0.4630 (D-H3 range-compression gate) | 0.4630 (D-H3 range-compression gate) | 0.4630 (D-H3 range-compression gate) | 3.2684 (D-H4 overnight gap fade) | 3.2684 (D-H4 overnight gap fade) | 3.2684 (D-H4 overnight gap fade) | 0.5816 (D-H1 trailing-vol regime gate) | 0.5816 | 13.0789 (F2_4_15min_vol_tercile_top) | 13.0789 | ok |
| C4 | 2019-07-01 | measured/13 vs measured/13 | 0.4706 (D-H3 range-compression gate) | 0.4706 (D-H3 range-compression gate) | 0.4706 (D-H3 range-compression gate) | 3.3222 (D-H4 overnight gap fade) | 3.3222 (D-H4 overnight gap fade) | 3.3222 (D-H4 overnight gap fade) | 0.5912 (D-H1 trailing-vol regime gate) | 0.5912 | 13.2943 (F2_4_15min_vol_tercile_top) | 13.2943 | ok |
| C4 | 2020-01-02 | measured/13 vs measured/13 | 0.4987 (D-H3 range-compression gate) | 0.4987 (D-H3 range-compression gate) | 0.4987 (D-H3 range-compression gate) | 3.5206 (D-H4 overnight gap fade) | 3.5206 (D-H4 overnight gap fade) | 3.5206 (D-H4 overnight gap fade) | 0.6265 (D-H1 trailing-vol regime gate) | 0.6265 | 14.0881 (F2_4_15min_vol_tercile_top) | 14.0881 | ok |
| C4 | 2021-01-04 | measured/13 vs measured/13 | 0.5717 (D-H3 range-compression gate) | 0.5717 (D-H3 range-compression gate) | 0.5717 (D-H3 range-compression gate) | 4.0355 (D-H4 overnight gap fade) | 4.0355 (D-H4 overnight gap fade) | 4.0355 (D-H4 overnight gap fade) | 0.7181 (D-H1 trailing-vol regime gate) | 0.7181 | 16.1486 (F2_4_15min_vol_tercile_top) | 16.1486 | ok |
| C4 | 2022-01-03 | measured/13 vs measured/13 | 0.6915 (D-H3 range-compression gate) | 0.6915 (D-H3 range-compression gate) | 0.6915 (D-H3 range-compression gate) | 4.8814 (D-H4 overnight gap fade) | 4.8814 (D-H4 overnight gap fade) | 4.8814 (D-H4 overnight gap fade) | 0.8687 (D-H1 trailing-vol regime gate) | 0.8687 | 19.5336 (F2_4_15min_vol_tercile_top) | 19.5336 | ok |
| C4 | 2023-01-03 | measured/13 vs measured/13 | 0.9438 (D-H3 range-compression gate) | 0.9438 (D-H3 range-compression gate) | 0.9438 (D-H3 range-compression gate) | 6.6624 (D-H4 overnight gap fade) | 6.6624 (D-H4 overnight gap fade) | 6.6624 (D-H4 overnight gap fade) | 1.1856 (D-H1 trailing-vol regime gate) | 1.1856 | 26.6604 (F2_4_15min_vol_tercile_top) | 26.6604 | ok |
| C5 | 2019-05-06 | measured/4 vs measured/4 | 1.9590 (E-H4 turn-of-month long) | 1.9590 (E-H4 turn-of-month long) | 1.9590 (E-H4 turn-of-month long) | 37.2619 (E-H1 scheduled macro drift) | 37.2619 (E-H1 scheduled macro drift) | 37.2619 (E-H1 scheduled macro drift) | 0.1359 (E-H3 quarterly witching short) | 0.1359 | 3.9969 (E-H1 scheduled macro drift) | 3.9969 | ok |
| C5 | 2019-07-01 | measured/4 vs measured/4 | 1.9913 (E-H4 turn-of-month long) | 1.9913 (E-H4 turn-of-month long) | 1.9913 (E-H4 turn-of-month long) | 37.8756 (E-H1 scheduled macro drift) | 37.8756 (E-H1 scheduled macro drift) | 37.8756 (E-H1 scheduled macro drift) | 0.1381 (E-H3 quarterly witching short) | 0.1381 | 4.0628 (E-H1 scheduled macro drift) | 4.0628 | ok |
| C5 | 2020-01-02 | measured/4 vs measured/4 | 2.1102 (E-H4 turn-of-month long) | 2.1102 (E-H4 turn-of-month long) | 2.1102 (E-H4 turn-of-month long) | 40.1372 (E-H1 scheduled macro drift) | 40.1372 (E-H1 scheduled macro drift) | 40.1372 (E-H1 scheduled macro drift) | 0.1463 (E-H3 quarterly witching short) | 0.1463 | 4.3054 (E-H1 scheduled macro drift) | 4.3054 | ok |
| C5 | 2021-01-04 | measured/4 vs measured/4 | 2.4188 (E-H4 turn-of-month long) | 2.4188 (E-H4 turn-of-month long) | 2.4188 (E-H4 turn-of-month long) | 46.0075 (E-H1 scheduled macro drift) | 46.0075 (E-H1 scheduled macro drift) | 46.0075 (E-H1 scheduled macro drift) | 0.1678 (E-H3 quarterly witching short) | 0.1678 | 4.9351 (E-H1 scheduled macro drift) | 4.9351 | ok |
| C5 | 2022-01-03 | measured/4 vs measured/4 | 2.9259 (E-H4 turn-of-month long) | 2.9259 (E-H4 turn-of-month long) | 2.9259 (E-H4 turn-of-month long) | 55.6516 (E-H1 scheduled macro drift) | 55.6516 (E-H1 scheduled macro drift) | 55.6516 (E-H1 scheduled macro drift) | 0.2029 (E-H3 quarterly witching short) | 0.2029 | 5.9695 (E-H1 scheduled macro drift) | 5.9695 | ok |
| C5 | 2023-01-03 | measured/4 vs measured/4 | 3.9934 (E-H4 turn-of-month long) | 3.9934 (E-H4 turn-of-month long) | 3.9934 (E-H4 turn-of-month long) | 75.9561 (E-H1 scheduled macro drift) | 75.9561 (E-H1 scheduled macro drift) | 75.9561 (E-H1 scheduled macro drift) | 0.2770 (E-H3 quarterly witching short) | 0.2770 | 8.1475 (E-H1 scheduled macro drift) | 8.1475 | ok |
| C6 | 2019-05-06 | measured/1 vs measured/1 | 0.1454 (C-H4 passive-fill reversal) | 0.1454 (C-H4 passive-fill reversal) | 0.1454 (C-H4 passive-fill reversal) | 0.1454 (C-H4 passive-fill reversal) | 0.1454 (C-H4 passive-fill reversal) | 0.1454 (C-H4 passive-fill reversal) | 13.4470 (C-H4 passive-fill reversal) | 13.4470 | 13.4470 (C-H4 passive-fill reversal) | 13.4470 | ok |
| C6 | 2019-07-01 | measured/1 vs measured/1 | 0.1478 (C-H4 passive-fill reversal) | 0.1478 (C-H4 passive-fill reversal) | 0.1478 (C-H4 passive-fill reversal) | 0.1478 (C-H4 passive-fill reversal) | 0.1478 (C-H4 passive-fill reversal) | 0.1478 (C-H4 passive-fill reversal) | 13.6685 (C-H4 passive-fill reversal) | 13.6685 | 13.6685 (C-H4 passive-fill reversal) | 13.6685 | ok |
| C6 | 2020-01-02 | measured/1 vs measured/1 | 0.1566 (C-H4 passive-fill reversal) | 0.1566 (C-H4 passive-fill reversal) | 0.1566 (C-H4 passive-fill reversal) | 0.1566 (C-H4 passive-fill reversal) | 0.1566 (C-H4 passive-fill reversal) | 0.1566 (C-H4 passive-fill reversal) | 14.4847 (C-H4 passive-fill reversal) | 14.4847 | 14.4847 (C-H4 passive-fill reversal) | 14.4847 | ok |
| C6 | 2021-01-04 | measured/1 vs measured/1 | 0.1796 (C-H4 passive-fill reversal) | 0.1796 (C-H4 passive-fill reversal) | 0.1796 (C-H4 passive-fill reversal) | 0.1796 (C-H4 passive-fill reversal) | 0.1796 (C-H4 passive-fill reversal) | 0.1796 (C-H4 passive-fill reversal) | 16.6032 (C-H4 passive-fill reversal) | 16.6032 | 16.6032 (C-H4 passive-fill reversal) | 16.6032 | ok |
| C6 | 2022-01-03 | measured/1 vs measured/1 | 0.2172 (C-H4 passive-fill reversal) | 0.2172 (C-H4 passive-fill reversal) | 0.2172 (C-H4 passive-fill reversal) | 0.2172 (C-H4 passive-fill reversal) | 0.2172 (C-H4 passive-fill reversal) | 0.2172 (C-H4 passive-fill reversal) | 20.0835 (C-H4 passive-fill reversal) | 20.0835 | 20.0835 (C-H4 passive-fill reversal) | 20.0835 | ok |
| C6 | 2023-01-03 | measured/1 vs measured/1 | 0.2964 (C-H4 passive-fill reversal) | 0.2964 (C-H4 passive-fill reversal) | 0.2964 (C-H4 passive-fill reversal) | 0.2964 (C-H4 passive-fill reversal) | 0.2964 (C-H4 passive-fill reversal) | 0.2964 (C-H4 passive-fill reversal) | 27.4110 (C-H4 passive-fill reversal) | 27.4110 | 27.4110 (C-H4 passive-fill reversal) | 27.4110 | ok |
| C7 | 2019-05-06 | projected/6 vs projected/6 | 26.6529 (H6 prior-close location follow-through) | 26.6529 (H6 prior-close location follow-through) | 26.6529 (H6 prior-close location follow-through) | 40.8794 (H2 NR7 opening-range breakout) | 40.8794 (H2 NR7 opening-range breakout) | 40.8794 (H2 NR7 opening-range breakout) | 5.2559 (H2 NR7 opening-range breakout) | 5.2559 | 10.6612 (H6 prior-close location follow-through) | 10.6612 | ok |
| C7 | 2019-07-01 | projected/6 vs projected/6 | 27.0919 (H6 prior-close location follow-through) | 27.0919 (H6 prior-close location follow-through) | 27.0919 (H6 prior-close location follow-through) | 41.5527 (H2 NR7 opening-range breakout) | 41.5527 (H2 NR7 opening-range breakout) | 41.5527 (H2 NR7 opening-range breakout) | 5.3425 (H2 NR7 opening-range breakout) | 5.3425 | 10.8368 (H6 prior-close location follow-through) | 10.8368 | ok |
| C7 | 2020-01-02 | projected/6 vs projected/6 | 28.7095 (H6 prior-close location follow-through) | 28.7095 (H6 prior-close location follow-through) | 28.7095 (H6 prior-close location follow-through) | 44.0338 (H2 NR7 opening-range breakout) | 44.0338 (H2 NR7 opening-range breakout) | 44.0338 (H2 NR7 opening-range breakout) | 5.6615 (H2 NR7 opening-range breakout) | 5.6615 | 11.4838 (H6 prior-close location follow-through) | 11.4838 | ok |
| C7 | 2021-01-04 | projected/6 vs projected/6 | 32.9085 (H6 prior-close location follow-through) | 32.9085 (H6 prior-close location follow-through) | 32.9085 (H6 prior-close location follow-through) | 50.4741 (H2 NR7 opening-range breakout) | 50.4741 (H2 NR7 opening-range breakout) | 50.4741 (H2 NR7 opening-range breakout) | 6.4895 (H2 NR7 opening-range breakout) | 6.4895 | 13.1634 (H6 prior-close location follow-through) | 13.1634 | ok |
| C7 | 2022-01-03 | projected/6 vs projected/6 | 39.8068 (H6 prior-close location follow-through) | 39.8068 (H6 prior-close location follow-through) | 39.8068 (H6 prior-close location follow-through) | 61.0544 (H2 NR7 opening-range breakout) | 61.0544 (H2 NR7 opening-range breakout) | 61.0544 (H2 NR7 opening-range breakout) | 7.8499 (H2 NR7 opening-range breakout) | 7.8499 | 15.9227 (H6 prior-close location follow-through) | 15.9227 | ok |
| C7 | 2023-01-03 | projected/6 vs projected/6 | 54.3303 (H6 prior-close location follow-through) | 54.3303 (H6 prior-close location follow-through) | 54.3303 (H6 prior-close location follow-through) | 83.3301 (H2 NR7 opening-range breakout) | 83.3301 (H2 NR7 opening-range breakout) | 83.3301 (H2 NR7 opening-range breakout) | 10.7139 (H2 NR7 opening-range breakout) | 10.7139 | 21.7321 (H6 prior-close location follow-through) | 21.7321 | ok |

Measured members with per-trade eps_min below the 2.11 cost bar at S = 2019-05-06 (1,151 days):

- from the reported eps_min fields: 47 of 95
- from my recomputed eps_min: 47 of 95; same set: True
- C2 (13): B-H1 opening-range breakout (hold 5), F4_2_prior_rth_close_crossing, F4_4_round_number_multiples_of_100, F4_4_round_number_multiples_of_50, G2.ETH.15, G2.ETH.30, G2.ETH.5, G2.ETH.60, G2.RTH.15, G2.RTH.30, G2.RTH.5, G5.RTH.5, RT1 B-H1 ORB 5-min bars (hold 1 bar)
- C3 (21): C-H1 magnitude-conditioned reversal, C-H2 post-spike exhaustion fade, C-H3 close-location-value reversal, F1_1_h15_ETH, F1_1_h15_RTH, F1_1_h1_ETH, F1_1_h1_RTH, F1_1_h30_ETH, F1_1_h30_RTH, F1_1_h5_ETH, F1_1_h5_RTH, F1_1_h60_ETH, G1.ETH.15, G1.ETH.30, G1.ETH.5, G1.ETH.60, G1.RTH.5, G4.RTH.15, G4.RTH.30, G4.RTH.5, RT5 C-H2 spike fade 5-min bars
- C4 (11): D-H1 trailing-vol regime gate, D-H2 inverse-vol sizing, D-H3 range-compression gate, F2_4_15min_vol_tercile_bottom, F2_4_15min_vol_tercile_top, F5_1_relvol_tercile_bottom, F5_2_efficiency_tercile_bottom, F5_2_efficiency_tercile_top, F5_3_range_volume_residual, RT6 D-H1 daily-vol regime gate, RT7 D-H2 daily-vol sizing
- C5 (1): E-H4 turn-of-month long
- C6 (1): C-H4 passive-fill reversal
- nearest to the bar: F4_2_prior_rth_close_crossing 2.078; F1_1_h60_RTH 2.161; F5_1_relvol_tercile_top 2.177; B-H1 opening-range breakout (hold 5) 1.996

Verdict: **VERIFIED** (47 of 95, same set from the reported fields and from my recomputation).

### 11.5 Item (5): the 64 statistic rows
Compared with the snapshot as JSON with sorted keys: 64 of 64 statistic member dicts byte-identical
(every field, including curves, simulated figures, flags, eps_min, spot checks); member order identical
(so the per-member seeds are the same); meta identical apart from timestamps, runtime, notes and source
hashes; `supplied_days` and `holdout2_detail` identical; no trial or projected row is identical (all 37
changed, as they must). Verdict: **VERIFIED**.

### 11.6 Epsilon on the finished extension file
extension file version read: {"generated_utc": "2026-09-22T06:36:29.644792+00:00", "rows": 100, "T_values": [1, 2, 4, 8, 16, 32], "verdicts": {"pass": 66, "marginal": 4, "fail": 30}, "smallest_pass_by_T": {"1": 102.92393548387098, "2": 107.06119354838708, "4": 96.87836308258082, "8": 92.0179677419354, "16": 98.28123996628806, "32": 188.4951689271085}}
Minimum passing net $/day is still the grid cell (consistency, T=2, p=0.60, R=1.00) at $87.48 ->
34.99 -> eps_day = 34; the smallest passing extension cell is $92.02 (T=8), the new T = 32 rows pass
only from $188.50, and the nearest excluded cell remains the marginal consistency T=4 p=0.58 R=1.0 at
$84.41 (section 1.2). The version caveat of section 1.1 is closed by this sha. Verdict: **VERIFIED**.

### 11.7 JSON-internal observations on the new run
As in section 8: `spot_check.closed_form_power_b` is a separate 2,000-replicate draw (A-H4 rth leg 0.780
vs curve 0.797 at n = 149; C-H4 0.814 vs 0.815 at 181; E-H1 0.9195 vs 0.921 at 16; statistics unchanged);
md section 3 matches the JSON row for row; the E-H1 arm-a dip of 11.3 is the only new non-monotone step.

### Appendix B. Re-simulated curves after the correction (mine), power_a / power_b by n, reported in brackets

- A-H4 rth leg: 10: 0.092/0.304 (rep 0.102/0.296), 15: 0.107/0.335 (rep 0.105/0.354), 20: 0.121/0.405 (rep 0.121/0.382), 30: 0.145/0.451 (rep 0.130/0.470), 50: 0.166/0.558 (rep 0.157/0.564), 75: 0.209/0.630 (rep 0.209/0.611), 100: 0.247/0.690 (rep 0.247/0.668), 121: 0.297/0.729, 140: 0.324/0.776, 149: 0.342/0.788 (rep 0.327/0.797), 150: 0.345/0.780 (rep 0.350/0.782), 161: 0.365/0.816, 185: 0.415/0.852, 200: 0.466/0.854 (rep 0.459/0.855), 209: 0.459/0.892, 281: 0.642/0.942, 300: 0.679/0.958 (rep 0.671/0.958), 326: 0.706/0.969, 374: 0.801/0.980, 379: 0.798/0.979 (rep 0.807/0.986), 431: 0.867/0.995, 487: 0.925/0.991, 500: 0.923/0.999 (rep 0.921/0.997), 750: 0.994/1.000 (rep 0.991/1.000), 1000: 0.999/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- G3.RTH.5: 10: 0.033/0.147 (rep 0.033/0.128), 15: 0.029/0.166 (rep 0.030/0.158), 20: 0.034/0.195 (rep 0.031/0.196), 30: 0.033/0.265 (rep 0.037/0.260), 50: 0.066/0.356 (rep 0.086/0.373), 75: 0.104/0.470 (rep 0.103/0.479), 100: 0.135/0.580 (rep 0.149/0.564), 136: 0.215/0.695, 150: 0.245/0.729 (rep 0.243/0.723), 158: 0.237/0.757, 182: 0.284/0.790, 193: 0.315/0.826 (rep 0.315/0.825), 200: 0.324/0.823 (rep 0.316/0.830), 209: 0.330/0.861, 236: 0.402/0.878, 300: 0.514/0.939 (rep 0.520/0.933), 388: 0.651/0.980, 451: 0.747/0.988, 492: 0.783/0.996 (rep 0.772/0.994), 500: 0.802/0.993 (rep 0.786/0.997), 518: 0.801/0.995, 596: 0.880/0.999, 673: 0.909/0.999, 750: 0.956/1.000 (rep 0.947/1.000), 1000: 0.990/1.000 (rep 0.986/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- F1_1_h1_RTH: 10: 0.013/0.122 (rep 0.018/0.118), 15: 0.008/0.122 (rep 0.009/0.118), 20: 0.011/0.139 (rep 0.015/0.130), 30: 0.008/0.161 (rep 0.011/0.154), 50: 0.016/0.209 (rep 0.015/0.200), 75: 0.019/0.241 (rep 0.022/0.251), 100: 0.030/0.291 (rep 0.028/0.288), 150: 0.040/0.383 (rep 0.035/0.377), 200: 0.061/0.420 (rep 0.067/0.446), 300: 0.101/0.556 (rep 0.097/0.571), 428: 0.183/0.703, 496: 0.235/0.754, 500: 0.221/0.768 (rep 0.226/0.762), 566: 0.269/0.807 (rep 0.282/0.797), 571: 0.273/0.819, 656: 0.324/0.862, 742: 0.398/0.883, 750: 0.405/0.890 (rep 0.391/0.885), 1000: 0.573/0.958 (rep 0.580/0.956), 1102: 0.645/0.974, 1279: 0.730/0.979, 1447: 0.814/0.994 (rep 0.792/0.990), 1470: 0.810/0.992, 1500: 0.822/0.994 (rep 0.810/0.995), 1690: 0.880/0.995, 1911: 0.928/0.998, 2000: 0.949/0.999 (rep 0.943/0.997), 3000: 0.996/1.000 (rep 0.996/1.000)
- F2_4_15min_vol_tercile_top: 10: 0.041/0.275 (rep 0.041/0.294), 15: 0.035/0.251 (rep 0.035/0.272), 20: 0.033/0.238 (rep 0.027/0.250), 30: 0.035/0.303 (rep 0.045/0.281), 50: 0.076/0.383 (rep 0.088/0.385), 75: 0.150/0.518 (rep 0.157/0.525), 100: 0.221/0.625 (rep 0.234/0.610), 114: 0.265/0.652, 132: 0.296/0.720, 150: 0.320/0.789 (rep 0.314/0.794), 152: 0.315/0.787, 171: 0.362/0.826 (rep 0.338/0.846), 175: 0.358/0.843, 198: 0.390/0.883, 200: 0.394/0.891 (rep 0.394/0.889), 300: 0.579/0.969 (rep 0.592/0.969), 344: 0.643/0.983, 399: 0.700/0.994, 436: 0.770/0.997 (rep 0.778/0.996), 458: 0.798/0.997, 500: 0.838/0.999 (rep 0.838/1.000), 527: 0.872/1.000, 596: 0.897/1.000, 750: 0.960/1.000 (rep 0.968/1.000), 1000: 0.998/1.000 (rep 0.996/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- E-H1 scheduled macro drift: 10: 0.749/0.817 (rep 0.760/0.835), 12: 0.776/0.826, 14: 0.814/0.915, 15: 0.819/0.913 (rep 0.811/0.918), 16: 0.815/0.922 (rep 0.810/0.921), 18: 0.787/0.943, 20: 0.787/0.969 (rep 0.789/0.963), 30: 0.839/0.996 (rep 0.836/0.997), 41: 0.783/1.000 (rep 0.792/1.000), 50: 0.762/1.000 (rep 0.774/1.000), 75: 0.841/1.000 (rep 0.832/1.000), 100: 0.910/1.000 (rep 0.908/1.000), 150: 0.979/1.000 (rep 0.973/1.000), 200: 0.994/1.000 (rep 0.996/1.000), 300: 1.000/1.000 (rep 1.000/1.000), 500: 1.000/1.000 (rep 1.000/1.000), 750: 1.000/1.000 (rep 1.000/1.000), 1000: 1.000/1.000 (rep 1.000/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
- C-H4 passive-fill reversal: 10: 0.046/0.179 (rep 0.060/0.186), 15: 0.056/0.195 (rep 0.052/0.220), 20: 0.055/0.226 (rep 0.060/0.233), 30: 0.070/0.276 (rep 0.064/0.288), 50: 0.075/0.362 (rep 0.083/0.369), 75: 0.124/0.497 (rep 0.119/0.490), 100: 0.158/0.579 (rep 0.151/0.597), 130: 0.201/0.685, 150: 0.223/0.755 (rep 0.235/0.748), 151: 0.261/0.736, 174: 0.286/0.800, 181: 0.306/0.814 (rep 0.302/0.815), 200: 0.335/0.850 (rep 0.351/0.840), 226: 0.378/0.890, 300: 0.542/0.948 (rep 0.526/0.952), 356: 0.644/0.974, 413: 0.730/0.986, 461: 0.796/0.992 (rep 0.786/0.994), 475: 0.809/0.996, 500: 0.819/0.996 (rep 0.825/0.995), 546: 0.875/0.998, 617: 0.923/0.998, 750: 0.962/1.000 (rep 0.967/1.000), 1000: 0.994/1.000 (rep 0.997/1.000), 1500: 1.000/1.000 (rep 1.000/1.000), 2000: 1.000/1.000 (rep 1.000/1.000), 3000: 1.000/1.000 (rep 1.000/1.000)
