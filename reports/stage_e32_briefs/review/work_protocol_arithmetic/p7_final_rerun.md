# P7/P8 frozen thresholds (budget 300; N after E.33 = 538 + 300 = 838)

- T_disc = 796 OOF dates (816 program trade dates 2020-12-01..2024-02-29 minus a 20-date burn-in)
- T_test = 870 (890 program trade dates 2017-05-22..2020-11-30 minus the 20-date burn-in; ZM MBO starts 2017-05-21)

## Discovery gate G3 (DSR >= 0.95, V = 1/(T_disc - 1), literal N)

- E[max SR] under the null, SR0 = 0.1137 daily
- SR_d needed, normal moments: 0.1724 daily (t = 4.86; annualised x sqrt 252 = 2.74)
- SR_d needed, skew -0.5, kurtosis 6: 0.1756 daily

## The one-shot test's bar b_test (daily Sharpe on T_test dates)

- daily t > 3.0: 0.1017
- DSR >= 0.95 at N = 838, V = 1/(T_test - 1), normal moments: 0.1649 (t = 4.86)
- b_test = max = 0.1649 (annualised 2.62)

## Power gate G4 (SR_d - se(SR_d) >= b_test) and the selection threshold

- G4 threshold on discovery SR_d: 0.2007 (t = 5.66); binding selection threshold max(G3, G4) = 0.2007 (annualised 3.19)
- (if the user drops the protocol-added test DSR: b_test = 0.1017, G4 = 0.1373, selection threshold = 0.1724)

## Test power at true daily Sharpe s (normal days)

| true s | annualised | P(pass t > 3.0) | P(pass b_test) |
|---|---|---|---|
| 0.10 | 1.59 | 0.480 | 0.028 |
| 0.12 | 1.90 | 0.704 | 0.094 |
| 0.15 | 2.38 | 0.922 | 0.331 |
| 0.17 | 2.70 | 0.977 | 0.560 |
| 0.20 | 3.17 | 0.998 | 0.847 |
| 0.25 | 3.97 | 1.000 | 0.993 |
| 0.30 | 4.76 | 1.000 | 1.000 |

## P(a configuration with true daily Sharpe s, same in both windows, is selected) x P(it passes the test)

| true s | P(select: SR_d >= max(G3, G4)) | P(pass b_test) | product |
|---|---|---|---|
| 0.10 | 0.002 | 0.028 | 0.000 |
| 0.12 | 0.012 | 0.094 | 0.001 |
| 0.15 | 0.078 | 0.331 | 0.026 |
| 0.17 | 0.195 | 0.560 | 0.109 |
| 0.20 | 0.492 | 0.847 | 0.417 |
| 0.25 | 0.914 | 0.993 | 0.908 |
| 0.30 | 0.997 | 1.000 | 0.997 |

## Net edge per trade implied (random walk sigma_h = 3.15 sqrt(h) ticks, stated assumption; n independent trades every date; daily SR = mu sqrt(n) / sigma_h)

| hold h (min) | sigma_h | trades/date n | mu at selection threshold | mu for 80% test power at b_test |
|---|---|---|---|---|
| 5 | 7.04 | 1 | 1.41 | 1.36 |
| 5 | 7.04 | 2 | 1.00 | 0.96 |
| 5 | 7.04 | 4 | 0.71 | 0.68 |
| 5 | 7.04 | 8 | 0.50 | 0.48 |
| 5 | 7.04 | 12 | 0.41 | 0.39 |
| 15 | 12.20 | 1 | 2.45 | 2.36 |
| 15 | 12.20 | 2 | 1.73 | 1.67 |
| 15 | 12.20 | 4 | 1.22 | 1.18 |
| 15 | 12.20 | 8 | 0.87 | 0.84 |
| 15 | 12.20 | 12 | 0.71 | 0.68 |
| 30 | 17.25 | 1 | 3.46 | 3.34 |
| 30 | 17.25 | 2 | 2.45 | 2.36 |
| 30 | 17.25 | 4 | 1.73 | 1.67 |
| 30 | 17.25 | 8 | 1.22 | 1.18 |
| 60 | 24.40 | 1 | 4.90 | 4.72 |
| 60 | 24.40 | 2 | 3.46 | 3.34 |

(80%-power true daily Sharpe at b_test: 0.1936.)

## Multiple-testing reference thresholds (one-sided, alpha 0.05)

| Rule | alpha per test (first step) | z |
|---|---|---|
| Bonferroni / Holm step 1 at m = 300 | 0.000167 | 3.588 |
| Bonferroni at m = N = 838 | 5.97e-05 | 3.847 |
| BH q = 0.05, rank 1 (= Bonferroni at m = 300) | 0.000167 | 3.588 |
| BY q = 0.05, rank 1 (c(m) = 6.283) | 2.65e-05 | 4.042 |
| Holm step 1 at K = 9 (V14 b, the test) | 0.00556 | 2.539 |
| Harvey-Liu-Zhu t > 3.0 | 0.00135 | 3.000 |
