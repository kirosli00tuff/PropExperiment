# Stage D.1e Task 1: coverage map. What the MES null is about

Written by the lead (Fable 5.1, xhigh) on 2026-09-22 from three extraction artifacts:
`reports/stage_d1e_members_recorded.json` (Task 1a, sonnet medium: recorded figures from the
D.1b/D.1d reports), `reports/stage_d1e_members_trials.json` (Task 1b, opus xhigh: the 31
trials re-run once through `screening.screen_candidate` on the 289-day train union to read
their per-trade and per-day distributions; continuity to `stage_d1d_accounting.json` to the
cent, `continuity_problems: []`; runtime 257 s; not a new trial, N stays 31) and
`reports/stage_d1e_members_events.json` (Task 1c, opus high: event-level and per-day series
for all 64 directional Family F and G statistics, reproducing every recorded estimate, n and
implied edge to 1e-9; no new statistic).

Units. Trials: net ticks per micro per trip, each round trip divided by its own contract
quantity (section 6; the trials trade 1 micro, D-H2 and RT7 1 to 5). Statistics: ticks per event, as the recorded implied edge
averages them (correlation statistics: sign(predictor) x forward move; F4.x and G: the signed
forward move). "Daily SD" is the standard deviation of the per-trade-date series over every
date in the window, $0 or 0 ticks on dates without a trade or event. Lag-1 AC is the lag-1
autocorrelation of that daily series. VIF (trials) is var(daily) / (trades per day x
var(per trade)), the within-day clustering factor.

Windows. Trials: the train union, 289 trade dates, 2025-04-01 to 2026-05-13. Statistics: the 139 EDA dates,
2025-10-17 to 2026-05-13 (Family F and G were computed on the EDA slice of the train union, D.1b and D.1d).

## 1. Classes and the refinements to the prompt's starting classification

| Class | Contents | Refinement (logged) |
|---|---|---|
| C1 session-clock effects | A-H1, A-H2 (buy), A-H2 (sell), A-H3, A-H4 eth leg, A-H4 rth leg | none |
| C2 reference levels and breakouts | B-H1 (5), B-H1 (75), B-H2, B-H3 breakout, B-H3 fade, B-H4, RT1-RT4; statistics F6.1, F4.1, F4.4 x100 (Tier A), F4.2, F4.4 x50 (Tier B), G2, G3, G5 at every timeframe (Tier A where near-misses, else Tier B) | F6.1 (the open's position in the overnight range) added to C2: it is a reference-level statistic and was on the D.1b near-miss list; the prompt did not place it |
| C3 short-horizon reversal and momentum at market fills | C-H1, C-H2, C-H3, RT5; statistics F3.2 (all 12 bucket pairs), F3.3 (a) and (b), F1.1 at h = 1, 5, 15, 30, 60 for ETH and RTH, G1 and G4 at every timeframe | F1 enters through its directional statistic F1.1 (lag autocorrelation at horizon h), not the F1.2 variance ratios: a variance ratio has no side and cannot carry an edge, so F1.2 is reported descriptively and is not a member |
| C4 volatility-state conditioning | D-H1, D-H2, D-H3, D-H4, RT6, RT7; statistics F2.4 (bottom and top vol tercile), F5.1, F5.2 (bottom and top terciles), F5.3 | F2 enters through F2.4 only; F2.1-F2.3 are non-directional facts (vol-of-vol, intraday vol shape, range scaling), reported descriptively |
| C5 calendar and scheduled events | E-H1, E-H2, E-H3, E-H4 | none |
| C6 passive-execution strategies | C-H4 | as the prompt says: criteria and data need defined here; the class verdict belongs to Stage D.1g with order-book fills |
| C7 daily-bar constructions for intraday entries | H1-H6, declared in `reports/stage_d1f_confirmation_list.md` section 2.1 A3 | new, per the prompt; no existing figures, so Task 3 projects their power from proxies (section 4 below) |

Tier A = the 31 trials, the 21 logged near-misses and the 6 H tests (58, the Holm family).
Tier B = the 43 directional F and G statistics that were not near-misses; they enter the class
null and never an edge claim. Both tiers are members of the null. Non-directional facts (F1.2,
F2.1-F2.3, F4.3, G0) are not members.

Out of scope, so the verdict never speaks for them: multi-day holding (excluded by the venue,
D.1c); every instrument other than MES and every cross-asset effect (the user's MES-only
decision); order-flow signals needing book data beyond C6's fill model; sizes other than the
2-micro headline; passive execution for any class other than C6; constructions not on the
frozen list, including the ideas logged for later in the D.1b and D.1d entries.

## 2. The 31 trials (source: Task 1b re-run; t from the D.1d accounting)

| Class | Member (trial ID = label in ALL_TRIALS) | coded micros | mean trip micros | trades/day | per-trade mean (ticks/micro) | per-trade SD | daily SD (ticks/micro/day) | lag-1 AC | VIF | net $ (289 d) | daily t |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | A-H1 european-open overnight drift | 1 | 1.000 | 0.955 | +0.41 | 34.67 | 33.88 | +0.004 | 1.00 | 141 | +0.20 |
| C1 | A-H2 rth close window (buy) | 1 | 1.000 | 0.920 | +1.77 | 53.81 | 51.62 | -0.087 | 1.00 | 588 | +0.54 |
| C1 | A-H2 rth close window (sell) | 1 | 1.000 | 0.920 | -5.88 | 53.87 | 51.70 | -0.087 | 1.00 | -1,956 | -1.78 |
| C1 | A-H3 weekend effect | 1 | 1.000 | 0.381 | -32.08 | 199.08 | 123.46 | +0.122 | 1.01 | -4,411 | -1.68 |
| C1 | A-H4 eth leg | 1 | 1.000 | 0.958 | +7.37 | 139.47 | 136.54 | -0.013 | 1.00 | 2,550 | +0.88 |
| C1 | A-H4 rth leg | 1 | 1.000 | 0.955 | +15.97 | 229.20 | 223.99 | -0.301 | 1.00 | 5,509 | +1.16 |
| C2 | B-H1 opening-range breakout (hold 5) | 1 | 1.000 | 0.955 | -3.90 | 27.01 | 26.40 | +0.109 | 1.00 | -1,347 | -2.41 |
| C2 | B-H1 opening-range breakout (hold 75) | 1 | 1.000 | 0.955 | -0.85 | 99.52 | 97.25 | -0.087 | 1.00 | -293 | -0.14 |
| C2 | B-H2 prior-day stop cascade | 1 | 1.000 | 0.772 | +1.09 | 42.24 | 37.09 | +0.087 | 1.00 | 303 | +0.39 |
| C2 | B-H3 breakout leg | 1 | 1.000 | 0.948 | -3.46 | 59.61 | 58.04 | -0.053 | 1.00 | -1,186 | -0.96 |
| C2 | B-H3 fade leg | 1 | 1.000 | 0.948 | -0.68 | 59.61 | 58.03 | -0.055 | 1.00 | -231 | -0.19 |
| C2 | B-H4 narrow-range breakout | 1 | 1.000 | 0.398 | -0.42 | 43.69 | 27.49 | -0.035 | 0.99 | -60 | -0.10 |
| C2 | RT1 B-H1 ORB 5-min bars (hold 1 bar) | 1 | 1.000 | 0.945 | -1.40 | 25.55 | 24.83 | +0.053 | 1.00 | -478 | -0.91 |
| C2 | RT2 B-H1 ORB 5-min bars (hold 15 bars) | 1 | 1.000 | 0.945 | -5.87 | 98.95 | 96.17 | +0.175 | 1.00 | -2,002 | -0.98 |
| C2 | RT3 B-H3 breakout leg 5-min bars | 1 | 1.000 | 0.945 | -2.86 | 64.98 | 63.15 | -0.052 | 1.00 | -975 | -0.73 |
| C2 | RT4 B-H3 fade leg 5-min bars | 1 | 1.000 | 0.945 | -1.28 | 64.98 | 63.15 | -0.053 | 1.00 | -437 | -0.33 |
| C3 | C-H1 magnitude-conditioned reversal | 1 | 1.000 | 140.979 | -2.12 | 14.97 | 208.06 | -0.091 | 1.37 | -107,967 | -24.46 |
| C3 | C-H2 post-spike exhaustion fade | 1 | 1.000 | 30.550 | -1.82 | 18.08 | 93.30 | +0.177 | 0.87 | -20,090 | -10.15 |
| C3 | C-H3 close-location-value reversal | 1 | 1.000 | 41.751 | -1.93 | 16.63 | 116.87 | +0.089 | 1.18 | -29,176 | -11.77 |
| C3 | RT5 C-H2 spike fade 5-min bars | 1 | 1.000 | 9.772 | -2.97 | 22.90 | 67.71 | +0.070 | 0.89 | -10,475 | -7.29 |
| C4 | D-H1 trailing-vol regime gate | 1 | 1.000 | 0.367 | -2.30 | 13.63 | 8.31 | -0.019 | 1.01 | -304 | -1.73 |
| C4 | D-H2 inverse-vol sizing | 1..5 by rule | 3.424 | 0.955 | -2.13 | 23.52 | 22.99 | +0.036 | 1.00 | -2,320 | -1.96 |
| C4 | D-H3 range-compression gate | 1 | 1.000 | 9.848 | -2.31 | 21.38 | 64.01 | +0.007 | 0.91 | -8,234 | -6.06 |
| C4 | D-H4 overnight gap fade | 1 | 1.000 | 0.464 | -5.03 | 28.27 | 19.37 | +0.023 | 1.01 | -843 | -2.05 |
| C4 | RT6 D-H1 daily-vol regime gate | 1 | 1.000 | 0.464 | -1.30 | 16.46 | 11.21 | +0.077 | 1.00 | -217 | -0.91 |
| C4 | RT7 D-H2 daily-vol sizing | 1..5 by rule | 1.778 | 0.889 | -1.55 | 20.57 | 19.40 | +0.040 | 1.00 | -1,070 | -1.47 |
| C5 | E-H1 scheduled macro drift | 1 | 1.000 | 0.107 | -20.03 | 154.61 | 50.29 | -0.002 | 0.99 | -776 | -0.73 |
| C5 | E-H2 post-release momentum | 1 | 1.000 | 0.087 | -0.51 | 32.65 | 9.43 | -0.000 | 0.96 | -16 | -0.08 |
| C5 | E-H3 quarterly witching short | 1 | 1.000 | 0.014 | -5.12 | 17.30 | 1.86 | -0.001 | 0.84 | -26 | -0.65 |
| C5 | E-H4 turn-of-month long | 1 | 1.000 | 0.190 | -0.11 | 12.39 | 5.36 | +0.075 | 0.99 | -7 | -0.07 |
| C6 | C-H4 passive-fill reversal | 1 | 1.000 | 92.467 | -2.36 | 17.70 | 190.54 | +0.013 | 1.25 | -78,687 | -19.47 |

Notes (per-micro scale, section 6). C-H1, C-H2, C-H3 and C-H4 trade 30 to 141 times a day and
are the members whose daily SD (93 to 208 ticks per micro per day) is highest relative to
their per-trade SD; their VIFs of 0.87 to 1.37 say within-day clustering is mild. The four
unconditional-exposure members (A-H4 rth leg, A-H4 eth leg, A-H3, B-H1 hold 75) have the
largest per-trade SD (100 to 229) and carry the drift; A-H4 rth leg's lag-1 AC of -0.30 is the
only autocorrelation beyond +/-0.25. D-H2 and RT7 are the two sized members (mean trip size
3.42 and 1.78 micros); dividing each trip by its own size is what section 6 defines. E-H3
trades four times in 289 days; its daily series is almost all zeros. The 1b JSON keeps the
superseded flat-$2.50 fields beside the per-micro ones so the correction is auditable.

## 3. The 21 Tier A statistics (source: Task 1c; the D.1b and D.1d near-miss lists)

| Class | Statistic ID | events | events/day | event mean (ticks) | event SD | daily-sum SD | lag-1 AC | recorded edge | s | reproduction |
|---|---|---|---|---|---|---|---|---|---|---|
| C2 | F6_1_overnight_range_position | 138 | 0.993 | +6.580 | 103.48 | 103.10 | +0.091 | +6.580 | +1 | pass |
| C2 | F4_4_round_number_multiples_of_100 | 559 | 4.022 | -3.363 | 55.64 | 89.31 | +0.135 | -3.363 | -1 | pass |
| C2 | F4_1_rth_open_crossing | 261 | 1.878 | -3.452 | 43.17 | 54.70 | +0.078 | -3.452 | -1 | pass |
| C2 | G2.RTH.30 | 319 | 2.295 | +5.191 | 47.80 | 64.09 | -0.054 | +5.191 | +1 | pass |
| C2 | G2.ETH.30 | 598 | 4.302 | -1.622 | 30.22 | 53.32 | +0.043 | -1.622 | -1 | pass |
| C2 | G2.ETH.5 | 1328 | 9.554 | -0.492 | 13.71 | 36.85 | +0.055 | -0.492 | -1 | pass |
| C2 | G5.RTH.15 | 129 | 0.928 | -4.016 | 43.33 | 40.74 | +0.169 | -4.016 | -1 | pass |
| C2 | G5.RTH.30 | 124 | 0.892 | +4.516 | 51.65 | 48.55 | -0.018 | +4.516 | +1 | pass |
| C2 | G3.RTH.15 | 138 | 0.993 | -10.080 | 163.63 | 163.04 | +0.066 | -10.080 | -1 | pass |
| C3 | F3_2_bucket07_bucket08 | 134 | 0.964 | -7.560 | 40.21 | 39.50 | -0.018 | -7.560 | -1 | pass |
| C3 | F3_3_opening_30min_to_close_momentum | 134 | 0.964 | -6.336 | 46.95 | 46.11 | +0.019 | -6.336 | -1 | pass |
| C3 | F3_2_bucket08_bucket09 | 134 | 0.964 | -6.224 | 39.62 | 38.91 | +0.247 | -6.224 | -1 | pass |
| C3 | F3_3_overnight_to_close_momentum | 134 | 0.964 | -4.993 | 47.11 | 46.26 | +0.035 | -4.993 | -1 | pass |
| C3 | F3_2_bucket01_bucket02 | 138 | 0.993 | +4.174 | 59.82 | 59.60 | +0.014 | +4.174 | +1 | pass |
| C3 | F3_2_bucket10_bucket11 | 134 | 0.964 | +3.694 | 42.37 | 41.60 | -0.124 | +3.694 | +1 | pass |
| C3 | F3_2_bucket02_bucket03 | 138 | 0.993 | +3.058 | 61.53 | 61.31 | +0.004 | +3.058 | +1 | pass |
| C3 | F3_2_bucket05_bucket06 | 138 | 0.993 | +2.942 | 42.93 | 42.77 | -0.055 | +2.942 | +1 | pass |
| C3 | F3_2_bucket04_bucket05 | 138 | 0.993 | +2.587 | 54.50 | 54.30 | +0.054 | +2.587 | +1 | pass |
| C3 | F3_2_bucket06_bucket07 | 138 | 0.993 | -2.486 | 44.01 | 43.85 | -0.122 | -2.486 | -1 | pass |
| C3 | F3_2_bucket12_bucket13 | 134 | 0.964 | +2.381 | 47.28 | 46.42 | -0.050 | +2.381 | +1 | pass |
| C3 | G1.RTH.5 | 1789 | 12.871 | +0.879 | 27.12 | 107.40 | -0.253 | +0.879 | +1 | pass |

s is the confirmation direction (the sign of the recorded implied edge); the tested per-event
quantity in D.1f is s x event value - 2.11 ticks (confirmation list, section 2.1 A2). For
F4.4 x100 the event series is the round-level leg with no control adjustment: the recorded
implied edge -3.363 is its plain mean, and the recorded estimate -4.577 is the
control-subtracted difference (control-leg mean +1.214 over 2,549 control events), reported
descriptively (corrected after the Task 5d review, R-5). The D.1b list (progress.md, "Not selected, ranked by the size of the implied
edge") and the D.1d p-ordering (G2.RTH.30 first, then G1.RTH.5, G2.ETH.30, G2.ETH.5, G5.RTH.15,
G5.RTH.30, G3.RTH.15) were re-read for this map and match this table member for member.

## 4. The 43 Tier B statistics (source: Task 1c coverage series)

| Class | Statistic ID | events | events/day | event mean (ticks) | event SD | daily-sum SD | lag-1 AC | s | reproduction |
|---|---|---|---|---|---|---|---|---|---|
| C2 | F4_2_prior_rth_close_crossing | 237 | 1.705 | -1.042 | 39.48 | 50.05 | +0.077 | -1 | pass |
| C2 | F4_4_round_number_multiples_of_50 | 1249 | 8.986 | -0.516 | 50.74 | 117.70 | +0.077 | -1 | pass |
| C2 | G2.RTH.5 | 1013 | 7.288 | +0.210 | 25.17 | 68.34 | +0.040 | +1 | pass |
| C2 | G3.RTH.5 | 138 | 0.993 | +1.297 | 176.14 | 175.50 | +0.089 | +1 | pass |
| C2 | G5.RTH.5 | 141 | 1.014 | -0.255 | 26.96 | 27.59 | +0.105 | -1 | pass |
| C2 | G2.ETH.15 | 833 | 5.993 | -0.508 | 23.46 | 60.59 | -0.019 | -1 | pass |
| C2 | G2.RTH.15 | 529 | 3.806 | -0.514 | 35.53 | 67.43 | +0.085 | -1 | pass |
| C2 | G3.RTH.30 | 134 | 0.964 | +2.022 | 132.23 | 129.81 | -0.123 | +1 | pass |
| C2 | G2.ETH.60 | 401 | 2.885 | -0.591 | 40.67 | 62.56 | +0.018 | -1 | pass |
| C2 | G2.RTH.60 | 168 | 1.209 | +2.887 | 62.65 | 68.96 | -0.177 | +1 | pass |
| C2 | G3.RTH.60 | 112 | 0.806 | +1.607 | 113.94 | 102.19 | -0.079 | +1 | pass |
| C2 | G5.RTH.60 | 112 | 0.806 | -4.571 | 74.52 | 68.38 | +0.178 | -1 | pass |
| C3 | F1_1_h1_ETH | 128968 | 927.827 | -0.081 | 5.06 | 177.26 | +0.133 | -1 | pass |
| C3 | F1_1_h5_ETH | 25568 | 183.942 | -0.023 | 11.90 | 152.97 | +0.015 | -1 | pass |
| C3 | F1_1_h15_ETH | 8335 | 59.964 | -0.052 | 21.23 | 149.19 | -0.119 | -1 | pass |
| C3 | F1_1_h30_ETH | 4026 | 28.964 | +0.035 | 27.91 | 145.38 | +0.117 | +1 | pass |
| C3 | F1_1_h60_ETH | 1803 | 12.971 | +0.687 | 37.79 | 142.76 | +0.063 | +1 | pass |
| C3 | F1_1_h1_RTH | 52977 | 381.129 | -0.118 | 9.44 | 247.55 | +0.121 | -1 | pass |
| C3 | F1_1_h5_RTH | 10485 | 75.432 | -0.049 | 20.42 | 181.77 | -0.173 | -1 | pass |
| C3 | F1_1_h15_RTH | 3403 | 24.482 | -0.094 | 35.45 | 191.75 | +0.112 | -1 | pass |
| C3 | F1_1_h30_RTH | 1632 | 11.741 | +0.031 | 48.65 | 168.20 | +0.074 | +1 | pass |
| C3 | F1_1_h60_RTH | 678 | 4.878 | -0.813 | 67.38 | 141.68 | +0.055 | -1 | pass |
| C3 | F3_2_bucket03_bucket04 | 138 | 0.993 | -1.848 | 53.60 | 53.40 | -0.102 | -1 | pass |
| C3 | F3_2_bucket09_bucket10 | 134 | 0.964 | -1.597 | 42.00 | 41.23 | +0.025 | -1 | pass |
| C3 | F3_2_bucket11_bucket12 | 134 | 0.964 | +1.007 | 48.65 | 47.76 | -0.206 | +1 | pass |
| C3 | G1.ETH.5 | 4405 | 31.691 | +0.009 | 15.27 | 81.09 | +0.050 | +1 | pass |
| C3 | G4.RTH.5 | 1784 | 12.835 | +0.416 | 25.08 | 96.11 | +0.092 | +1 | pass |
| C3 | G1.ETH.15 | 1456 | 10.475 | +0.807 | 34.69 | 97.13 | -0.106 | +1 | pass |
| C3 | G1.RTH.15 | 577 | 4.151 | -1.917 | 46.23 | 104.64 | +0.202 | -1 | pass |
| C3 | G4.RTH.15 | 577 | 4.151 | -1.055 | 40.41 | 95.80 | -0.040 | -1 | pass |
| C3 | G1.ETH.30 | 715 | 5.144 | -0.354 | 35.88 | 75.09 | -0.090 | -1 | pass |
| C3 | G1.RTH.30 | 279 | 2.007 | -0.663 | 59.91 | 75.96 | +0.071 | -1 | pass |
| C3 | G4.RTH.30 | 277 | 1.993 | -1.487 | 55.99 | 81.56 | -0.232 | -1 | pass |
| C3 | G1.ETH.60 | 334 | 2.403 | +0.518 | 43.39 | 66.65 | +0.001 | +1 | pass |
| C3 | G1.RTH.60 | 117 | 0.842 | -4.308 | 84.03 | 72.42 | -0.178 | -1 | pass |
| C3 | G4.RTH.60 | 115 | 0.827 | -4.009 | 78.57 | 75.31 | -0.308 | -1 | pass |
| C4 | F2_4_15min_vol_tercile_bottom | 1135 | 8.165 | -0.219 | 22.23 | 54.60 | -0.055 | -1 | pass |
| C4 | F2_4_15min_vol_tercile_top | 1134 | 8.158 | -1.307 | 46.81 | 151.52 | +0.188 | -1 | pass |
| C4 | F5_1_relvol_tercile_bottom | 464 | 3.338 | +0.241 | 35.99 | 72.56 | -0.170 | +1 | pass |
| C4 | F5_1_relvol_tercile_top | 464 | 3.338 | +1.091 | 63.47 | 117.42 | +0.090 | +1 | pass |
| C4 | F5_2_efficiency_tercile_bottom | 544 | 3.914 | -0.904 | 47.44 | 94.00 | -0.075 | -1 | pass |
| C4 | F5_2_efficiency_tercile_top | 544 | 3.914 | -0.404 | 51.39 | 112.28 | +0.105 | -1 | pass |
| C4 | F5_3_range_volume_residual | 1632 | 11.741 | +0.763 | 48.80 | 162.96 | +0.017 | +1 | pass |

## 5. C7, Family H (no figures yet): the proxy rule Task 3 uses

H1-H6 have never been run, by design (this stage screens nothing). Their power is PROJECTED
from members with the same exposure shape, and the projection is labelled as such everywhere
it appears; the achieved null power that the criteria require is measured in D.1f on the H
series themselves. Proxy rule, fixed here:
- Per-trade SD for H1-H5 (an opening-range breakout or fade entered between 09:00 and 14:29 CT
  and held to 14:58): 200 ticks per micro, between B-H1 hold-75's 99.5 (75-minute hold) and
  A-H4 rth leg's 229 (full-session hold) at the corrected per-micro scale (section 7), nearer
  the latter because the median hold is about three quarters of the session. H6 (entry at
  the open, exit at 14:58): 230, the A-H4 rth leg figure. (The first issue of this map read
  the proxies off the half-scale table, 100 and 115; corrected after the Task 5d review,
  H-5.)
- Firing fraction f (the share of complete trade dates on which the condition holds and an
  entry occurs), from the conditions' definitions under exchangeable daily ranges, not from
  any data: NR4 1/4, NR7 1/7, inside day 1/4, bottom tercile 1/3, top tercile 1/3, CLV in the
  outer fifths 2/5; times 0.9 for the breakout and fade tests, the share of days on which a
  30-minute opening range is breached before 14:30 (the ORB trials B-H1 and RT1-RT2 entered
  on 95% of their tradable days).
- Daily SD = per-trade SD x sqrt(f) (a day without an entry contributes 0; the mean term is
  negligible at these sizes). Lag-1 AC taken as 0.
- Trades per day = f, for the per-trade translation of epsilon.

## 6. Unit correction after the Task 5d review (R-1)
The first issue of this map, and the Task 1b re-run behind it, divided every trial's daily and
per-trade P&L by $2.50 as if every trial traded 2 micros. Every trial module trades
QUANTITY_MICROS = 1 (D-H2 and RT7 size 1 to 5 by rule), so those figures were at half the
per-micro scale for 29 trials and C-H4. The runner now records each round trip's contract
quantity (ScreeningReport.trip_micros) and the series in section 2 are per micro per trip:
d_t = the sum over the trips closing on t of trip_pnl_usd / (1.25 x trip_micros). The
statistics (sections 3 and 4) were always in ticks per event and are unchanged.

## 7. Re-runs and reads logged (none is a new trial; N = 31)
- Task 1b: the 31 trials re-run once on the 289-day train union through `screen_candidate`
  (`strategy/research/_d1e_members.py`), to record per-trade and per-day distributions the D.1d
  accounting never wrote down. Two additive fields on `ScreeningReport` (`trip_pnls_usd`,
  `daily_n_trips`) with three tests; every existing field unchanged; continuity to the cent.
- Task 1c: the 64 directional F and G statistics recomputed on the 139 EDA dates by the hashed
  modules' own builders (`strategy/research/_d1e_event_series.py`), no module edited.
- No holdout date, no extended-history bar, no order-book record was read.
