| Finding | Where in docs/STAGE_E_ML_V2_DESIGN.md | As a rule or open |
|---|---|---|
| F1 MLL binds; realistic band | V2.0: the dollar table at S 1.0, 1.5 and 2.0 for 50K, 150K and 5 x 150K; eps as context; ruin for scale. V2.9 verdict 5: Sharpe >= 1.5, alarm above 4.0; verdict 7: ruin <= 10% | rule; the thresholds are open (V2.12 item 14) |
| F2 Gate 0 first | V2.2b: families A and B, a fixed pass bar, fail = stop; V2.1: phase 2 only after a pass | rule; the bar is open (item 1) |
| F3 ridge primary, shallow LightGBM | V2.6: ridge lambda {0.01, 0.1, 1.0}, LightGBM depth {2, 3}, no LSTM or transformer, lstm.py not reused | rule; the grids are open (item 9) |
| F4 nested CPCV, PBO, DSR at full N, t >= 3 | V2.9: 6 blocks, 15 outer and 4 inner splits, purge plus 1-date embargo; PBO by CSCV on 16 blocks; N_total = N_program + 45 + Gate 0 tests; median-path t >= 3 | rule |
| F5 power | V2.0: minimum detectable Sharpe per data length; V2.9: the research-window bar t >= 1.0 with its power | rule; the research bar is open (item 14) |
| F6 horizon, turnover, c/sigma | V2.2: 3 decision times by rule, h in {60, 120, F}, one position per product, at most 3 entries a day, tau = 0.10 | rule; tau and the clock are open (items 6, 7) |
| F7 cost gate | V2.7: net edge > k c, k in {1.5, 2, 3} by nested CPCV | rule; the reading is open (item 10) |
| F8 drawdown-distance sizing | V2.8: 0.10 x D, 0.25 x D loss cap, b = sigma_target / sqrt(3), the 2b rounding band, size down after a payout through D | rule; the constants are open (item 11) |
| F9 payout mechanics | V2.9 payout simulation: Standard and Consistency, caps by size, the DLL doubling, the MLL path and its post-payout reset, resets, ruin, keep-D policy | rule; the policy is open (item 15) |
| F10 kill switches | V2.8: KS1 to KS5 with thresholds | rule; the thresholds are open (item 13) |
| F11 five accounts one bet | V2.0 note; V2.8 at most 1 position per cluster; V2.9 payout sim: 5 accounts as one draw | rule |
| F12 Live Funded bans the API | V2.12 item 18, D9.10 / facts F12.2g | open (deployment risk) |
| F13 no tick or order-book data | V2.1: one-minute OHLCV only, in every phase | rule |
