# E.34 ZL methods addendum, M4: power and N (MathReaderM4-OpusHigh, opus high)

Written 2026-10-29 12:10-12:17 PDT. Pure arithmetic: no market-data file was opened, and no price, return or outcome
was computed. Synthetic normal draws were used only in the D2 simulation (section f). Script:
reports/stage_e34_briefs/work/MathReaderM4-OpusHigh/m4_power.py (sha256 26de065a0666ab4c...). Full output:
work/MathReaderM4-OpusHigh/m4_out.md (sha256 050071a59795f067...; 195 lines). Run:
`nice -n 10 uv run python reports/stage_e34_briefs/work/MathReaderM4-OpusHigh/m4_power.py`, 2 s.

The script imports the frozen E.32 functions that E.32b recs 4.4 (reports/stage_e32b_recommendations.md:501-507)
names: `p7_final.se_sharpe`, `p7_final.g4_threshold` (reports/stage_e32_briefs/protocol/p7_final.py:41-56),
`p7_thresholds.required_sharpe` and `trade_dates` (p7_thresholds.py:55-81), and
`funnel.multiple_comparisons.expected_max_sharpe` / `deflated_sharpe_ratio` (funnel/multiple_comparisons.py:63-81).
Its `row()` repeats E.32b's own scratch script line for line (`hurdles.py`, still present in the E.32b scratchpad
.../3860d0d1-.../scratchpad/d5/hurdles.py, lines 22-33), with T_disc, T_test, skew and kurtosis passed in as
parameters.

**Reproduction check.** At N 838, T_disc 796, T_test 870 the output gives SR0 0.1137, G3 0.1724 (t 4.86), b_test
0.1649 (t 4.86; unrounded 0.164882), G4 0.2007 (t 5.66), binding 0.2007, SR80_test 0.1936. That matches E.32b recs
4.4 (line 512), protocol P7.2 (reports/stage_e32_discovery_protocol.md:704-712; 0.164882 at line 724) and E.33c's
s80 values 0.2309 / 0.2025 (reports/E.33c_RETURN.md:194-195) to every printed digit. The N 938, 1038 and 1138 rows
also match E.32b's 100, 200 and 300 rows (lines 518, 520, 521) to every digit.

---

## Equations (used throughout)

Symbols: SR is the daily Sharpe of the net daily series (zeros on no-trade dates); T is the number of dates; g3 is
skewness; g4 is raw kurtosis (3 = normal); V is the cross-trial variance of the Sharpe estimates; gamma = 0.5772;
Phi is the standard normal CDF; z80 = Phi^-1(0.8) = 0.8416.

1. Expected maximum under the null (BLdP 2014 eq. 1; E.32 brief M5a d.2 item 1, reports/stage_e32_methods_brief.md:7259-7260):
   e(N) = (1 - gamma) Phi^-1(1 - 1/N) + gamma Phi^-1(1 - 1/(N e)),  SR0 = sqrt(V) e(N).
2. DSR (BLdP 2014 eq. 2; M5a d.2 item 2, line 7261-7262; funnel/multiple_comparisons.py:81):
   DSR = Phi[ (SR - SR0) sqrt(T - 1) / sqrt(1 - g3 SR + (g4 - 1)/4 SR^2) ].
3. G3 = the smallest SR with DSR >= 0.95 at N, V = 1/(T_disc - 1), T = T_disc (P8 G3, protocol line 744-748).
   First-order form (M5a d.2 item 3, line 7266-7269): G3 ~ (e(N) + 1.645) / sqrt(T_disc).
4. b_test = max(3.0 / sqrt(T_test), the smallest SR with DSR >= 0.95 at N, V = 1/(T_test - 1), T = T_test)
   (p7_final.py docstring lines 13-15; kept by V52 item 1 per E.32b recs 4.4 line 506).
5. Mertens SE (M5b d.2 item 3, line 8223-8224; p7_final.py:41-42): se(SR, T) = sqrt((1 - g3 SR + (g4 - 1)/4 SR^2)/(T - 1)).
6. G4 = the smallest SR_d with SR_d - se(SR_d, T_disc) >= b_test (P8 G4, protocol lines 749-752). Binding = max(G3, G4).
7. SR80 (the true daily Sharpe that passes with probability 0.80): SR80 = bar + z80 se(bar, T). Here bar = b_test
   on T_test for the test, G3 or the binding threshold on T_disc for discovery. This is p7_final.py's convention
   (line 104) and E.33's (reports/stage_e33c_briefs/work/D_stats.md:249).
8. Per-trade minimum detectable net edge (random walk, independent trades; E.32b holding scope lines 16-18):
   e80(h, n) = SR80 x sigma_h / sqrt(n) ticks a trade, net. Here n is the average number of trades per date,
   inactive dates included, because a series that trades n' a day on a fraction p of dates has daily SR about
   mu sqrt(n' p) / sigma_h. The required gross is c_f + e80, with c_f = 2.38 ticks for Topstep ZL (E.32b holding
   scope 15, line 915).
9. Dependence (M5b c.2 items 3 and 5, lines 8057-8067): with same-day equicorrelation rho_w among k trades a day,
   D_day = 1 + (k - 1) rho_w and e80 scales by sqrt(D_day).

---

## (a) T_disc and T_test for ZL

The counts come from `p7_thresholds.trade_dates`, which counts weekdays minus grain full closures. The closures
come from the program's CME grains holiday calendars (data.calendars.grains from 2019-05-01, the hist2010 grains
calendar before; docstring p7_thresholds.py:5-7). It opens no market data and no sealed file; neither calendar is
listed in reports/stage_e32_briefs/seal/derived_unsealed_files.tsv (checked by grep).

| window | span | weekdays | CBOT trade dates | burn-in | T |
|---|---|---|---|---|---|
| discovery | 2020-12-01..2024-02-29 | 848 | 816 | 20 | **T_disc = 796** |
| test, MBO | 2017-05-22..2020-11-30 | 921 | 890 | 20 | **T_test = 870** |
| test, MBP-1 | 2017-05-01..2020-11-30 | 936 | 905 | 20 | **T_test = 885** |

- Cross-checks against recorded counts (no data opened). E.33 split the owned ZL MBP-1 into records on 816 dates
  (BRIEFS shared facts; E.33's split record). E.33's OOF set was 796 dates, 2020-12-30..2024-02-29, in "6 blocked
  folds with a 21-date embargo" (reports/E.33c_RETURN.md:18, 212). Every post-burn-in date is out of fold, so
  T_disc = 816 - 20. E.32 P9 records 890 program dates and T_test = 870 for the MBO window
  (protocol lines 777-781). The MBP-1 window adds the 15 sealed trade dates 2017-05-01..2017-05-19 that P9 says
  "stay sealed and untested" under MBO (line 777). 890 + 15 = 905, which matches the calendar.
- Assumption: the ZL program keeps E.33's construction (a 20-date feature burn-in; folds that make every
  post-burn-in date OOF). F09 relative-value features with longer lookbacks would need a longer burn-in. At 40
  dates (T_disc 776, T_test 850) the binding threshold rises from 0.2007 to 0.2031 and SR80_test from 0.1936 to
  0.1959 (m4_out.md "Sensitivity" table). That is about +1.2%, so e80 rises by about 1.2%.
- Which test length applies depends on the data the test buys. The F10 order-book state can be built from MBP-1,
  which is the schema owned for discovery (no ZL MBO is owned; BRIEFS shared facts). In that case the MBP-1 span
  (T_test 885) is the like-for-like test. One open item: before 2017-05-21 the data are MDP 2 level-aggregated,
  and "the ts_recv field on all MDP 2 data is set to the same value as ts_event" (P9 quoting Databento, protocol
  lines 772-775). The 15 early dates may therefore differ in timestamp semantics. That is a data question for M3
  or DataFacts, not arithmetic.

## (b) Threshold table at N = 838 + B

### Test on MBO (T_disc 796, T_test 870), normal moments

| B | N | e(N) | SR0 disc | G3 SR_d (t) | b_test (t) | G4 SR_d (t) | binding | SR80_test | SR80 disc G3 | SR80 disc binding | b_test unrounded |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 838 | 3.2045 | 0.1137 | 0.1724 (4.86) | 0.1649 (4.86) | 0.2007 (5.66) | 0.2007 | 0.1936 | 0.2025 | 0.2309 | 0.164882 |
| 40 | 878 | 3.2179 | 0.1141 | 0.1729 (4.88) | 0.1653 (4.88) | 0.2012 (5.68) | 0.2012 | 0.1941 | 0.2030 | 0.2313 | 0.165339 |
| 62 | 900 | 3.2250 | 0.1144 | 0.1732 (4.89) | 0.1656 (4.88) | 0.2014 (5.68) | 0.2014 | 0.1943 | 0.2032 | 0.2316 | 0.165581 |
| 100 | 938 | 3.2369 | 0.1148 | 0.1736 (4.90) | 0.1660 (4.90) | 0.2018 (5.69) | 0.2018 | 0.1947 | 0.2036 | 0.2320 | 0.165984 |
| 150 | 988 | 3.2517 | 0.1153 | 0.1741 (4.91) | 0.1665 (4.91) | 0.2023 (5.71) | 0.2023 | 0.1952 | 0.2042 | 0.2325 | 0.166489 |
| 200 | 1038 | 3.2657 | 0.1158 | 0.1746 (4.93) | 0.1670 (4.92) | 0.2028 (5.72) | 0.2028 | 0.1957 | 0.2047 | 0.2330 | 0.166967 |
| 250 | 1088 | 3.2790 | 0.1163 | 0.1751 (4.94) | 0.1674 (4.94) | 0.2033 (5.73) | 0.2033 | 0.1962 | 0.2052 | 0.2334 | 0.167421 |
| 300 | 1138 | 3.2917 | 0.1167 | 0.1755 (4.95) | 0.1679 (4.95) | 0.2037 (5.75) | 0.2037 | 0.1966 | 0.2056 | 0.2338 | 0.167853 |

### Test on MBP-1 (T_disc 796, T_test 885)

The discovery columns (SR0, G3, SR80 disc G3) do not change. The test-driven columns do:

| B | N | b_test (t) | G4 (t) | binding | SR80_test | SR80 disc binding | b_test unrounded |
|---|---|---|---|---|---|---|---|
| 0 | 838 | 0.1635 (4.86) | 0.1993 (5.62) | 0.1993 | 0.1920 | 0.2294 | 0.163470 |
| 40 | 878 | 0.1639 (4.88) | 0.1997 (5.64) | 0.1997 | 0.1924 | 0.2299 | 0.163924 |
| 62 | 900 | 0.1642 (4.88) | 0.2000 (5.64) | 0.2000 | 0.1927 | 0.2301 | 0.164164 |
| 100 | 938 | 0.1646 (4.90) | 0.2004 (5.65) | 0.2004 | 0.1931 | 0.2305 | 0.164564 |
| 150 | 988 | 0.1651 (4.91) | 0.2009 (5.67) | 0.2009 | 0.1936 | 0.2310 | 0.165064 |
| 200 | 1038 | 0.1655 (4.92) | 0.2014 (5.68) | 0.2014 | 0.1940 | 0.2315 | 0.165538 |
| 250 | 1088 | 0.1660 (4.94) | 0.2018 (5.69) | 0.2018 | 0.1945 | 0.2320 | 0.165988 |
| 300 | 1138 | 0.1664 (4.95) | 0.2022 (5.71) | 0.2022 | 0.1949 | 0.2324 | 0.166416 |

Reading:
- G4 binds over G3 at every budget. In t terms the required discovery t is 5.66 to 5.75, and the test t is
  4.86 to 4.95. The daily t > 3.0 bar (0.1017 at T 870; 0.1008 at T 885) never binds at the test.
- A budget of 0 to 300 moves the binding threshold by +0.0030 (+1.5%) and SR80_test by +0.0030. The test's
  length moves them less: MBP-1 instead of MBO lowers b_test by 0.0014.
- Moment sensitivity at N 838 (m4_out.md, the "Moment sensitivity" table), as binding / SR80_test:
  - normal: 0.2007 / 0.1936
  - skew -0.5, kurtosis 6: 0.2059 / 0.1979
  - kurtosis 10: 0.2033 / 0.1956
  - kurtosis 20: 0.2070 / 0.1985
  - skew -2, kurtosis 30: 0.2270 / 0.2151

  A series that trades on a fraction p of dates has raw daily kurtosis of about 3/p (for example 6 at
  p = 0.5), so the skew -0.5 / kurtosis 6 row is the realistic floor for a once-or-twice-a-day ZL rule.

## (c) e80 in ticks a trade, net (ZL day-session sigma_h from E.32b holding scope 15, lines 922-930)

e80 = SR80 x sigma_h / sqrt(n). sigma_h: 20.37 (h 15), 28.10 (h 30), 38.21 (h 60). Entry caps n_cap: 19, 9, 4
(line 941-946). Test on MBO.

| N (B) | h | n/date | e80 disc G3 | e80 disc binding (G3+G4) | e80 test | edge at the binding threshold (about 50% power) | gross needed at test, c_f + e80 test |
|---|---|---|---|---|---|---|---|
| 838 (0) | 15 | 19 (cap) | 0.95 | 1.08 | 0.90 | 0.94 | 3.28 |
| 838 (0) | 15 | 4 | 2.06 | 2.35 | 1.97 | 2.04 | 4.35 |
| 838 (0) | 15 | 2 | 2.92 | 3.33 | 2.79 | 2.89 | 5.17 |
| 838 (0) | 15 | 1 | 4.12 | 4.70 | 3.94 | 4.09 | 6.32 |
| 838 (0) | 30 | 9 (cap) | 1.90 | 2.16 | 1.81 | 1.88 | 4.19 |
| 838 (0) | 30 | 4 | 2.85 | 3.24 | 2.72 | 2.82 | 5.10 |
| 838 (0) | 30 | 2 | 4.02 | 4.59 | 3.85 | 3.99 | 6.23 |
| 838 (0) | 30 | 1 | 5.69 | 6.49 | 5.44 | 5.64 | 7.82 |
| 838 (0) | 60 | 4 (cap) | 3.87 | 4.41 | 3.70 | 3.83 | 6.08 |
| 838 (0) | 60 | 2 | 5.47 | 6.24 | 5.23 | 5.42 | 7.61 |
| 838 (0) | 60 | 1 | 7.74 | 8.82 | 7.40 | 7.67 | 9.78 |
| 900 (62) | 30 | 9 / 2 / 1 | 1.90 / 4.04 / 5.71 | 2.17 / 4.60 / 6.51 | 1.82 / 3.86 / 5.46 | 1.89 / 4.00 / 5.66 | 4.20 / 6.24 / 7.84 |
| 1138 (300) | 15 | 19 / 2 / 1 | 0.96 / 2.96 / 4.19 | 1.09 / 3.37 / 4.76 | 0.92 / 2.83 / 4.00 | 0.95 / 2.93 / 4.15 | 3.30 / 5.21 / 6.38 |
| 1138 (300) | 30 | 9 / 2 / 1 | 1.93 / 4.09 / 5.78 | 2.19 / 4.65 / 6.57 | 1.84 / 3.91 / 5.52 | 1.91 / 4.05 / 5.72 | 4.22 / 6.29 / 7.90 |
| 1138 (300) | 60 | 4 / 2 / 1 | 3.93 / 5.56 / 7.86 | 4.47 / 6.32 / 8.94 | 3.76 / 5.31 / 7.51 | 3.89 / 5.50 / 7.78 | 6.14 / 7.69 / 9.89 |

- The N 838 cap rows reproduce E.32b holding scope 15 (lines 944-946): 0.95 / 1.08 / 0.90; 1.90 / 2.16 / 1.81;
  3.87 / 4.41 / 3.70.
- The MBP-1 test lowers each test e80 by about 0.8% (h30 cap 1.80, h30 n=1 5.39; m4_out.md second e80 table).
- At realistic rates the detectable edge is 2 to 3 times the cap value. E.33's G1 passers traded about one to two a
  date; at those rates a 30-minute rule needs 3.85 to 5.44 ticks net at the test, and 4.59 to 6.49 ticks net to clear
  discovery with 80% probability. In gross terms that is 6.2 to 7.8 ticks, or 0.22 to 0.28 sigma_30, per trade.

**Heavy-tail and independence caveat (E.33c 3.7 v, reports/E.33c_RETURN.md:194-199).** E.33 called the formula "a
lower-side figure for heavy-tailed series, which the measured figures below cover". On ZM, measured per configuration
as e80 = s80 x SD(X_D) / (trades per date), with no random-walk or independence assumption, the G1 passers' medians
were 1.57 (T15), 1.95 (T30), 4.33 (F60) and 4.37 (F30) ticks. The formula gave 1.41 at 15 minutes and 4 a date, 1.99
at 30 minutes and 4 a date, and 3.98 at 60 minutes and 2 a date (same lines; the ZM table is in
reports/stage_e33c_briefs/work/D_stats.md:253-290). These figures are ZM aggregates from a RETURN summary, not ZL
statistics.

Three effects separate the measured figures from the formula. The ZL facts set their direction, not their size:
1. Tails raise the bar slightly through se(): +2 to 4% at kurtosis 6 to 20, +11% at skew -2 / kurtosis 30
   (section b).
2. Same-day correlation multiplies e80 by sqrt(1 + (k - 1) rho_w), and day-to-day dependence works the same way
   (M5b c.2 items 3 and 5). This effect can be the larger one, and it only raises e80.
3. Pooled per-trade SD differs from sigma_h. E.33's measured pooled sigma ranged from 0.83 x (T30) to 1.26 x (F15)
   of the 3.15 sqrt(h) number, depending on label and exit (D_stats.md:255-279).

The ZL program should therefore treat the formula column as a floor. The protocol's P10 report should report the
measured version (s80 x SD(X_D) / mean trades per date) beside it, as E.33 did.

## (d) The K2 comparison against 1.8 ticks and the budget

K2 (E.32b recs, lines 25 and 551-552): "The best discovery configuration's net edge per trade is below the test's
minimum detectable edge (1.8 ticks for a 30-minute hold): stop."

- 1.8 ticks is the test e80 at h 30 at the 9-entry cap, N 838, T_test 870: 0.1936 x 28.10 / 3 = 1.81.
- How the budget moves it: B 62 gives 1.82, B 150 gives 1.83, B 300 gives 1.84. With the MBP-1 test: 1.80 at B 0
  and 1.83 at B 300. Rounded to one decimal, it stays 1.8 for every B up to 300 on either schema.
- The fixed 1.8 is a horizon and rate figure, not a program constant. The test's own detectable edge is 0.90 (h 15,
  cap 19), 1.81 (h 30, cap 9) and 3.70 (h 60, cap 4). It is 3.85 or 5.44 for a 30-minute rule at 2 or 1 trades a
  date.
- Two consequences under the formula's assumptions follow. These are for the lead; I am not ruling on them.
  1. **K2 is weaker than G4 for slow rules.** Any configuration that clears the binding threshold has observed
     SR_d >= 0.2007, so its observed per-trade net is at least 0.2007 sigma_h / sqrt(n). That is 1.037 x the
     test's e80 at its own rate. For a 30-minute rule at 1 to 2 trades a date, a 1.8-tick K2 passes edges of
     1.8 to 3.8 ticks that G4 would already have rejected. K2 adds nothing there.
  2. **At 15 minutes and high rates, K2 at 1.8 is stricter than the test's power requires.** A G4 passer at h 15
     can have net below 1.8 when n > (0.2007 x 20.37 / 1.8)^2 = 5.2 trades a date. K2 would stop it although the
     test's e80 at that rate (for example 1.39 at n = 8) is below its edge.

  A rate- and horizon-matched K2 would compare the best configuration's net with
  e80_test(h, n_bar) = SR80_test(N) sigma_h / sqrt(n_bar), at the configuration's own n_bar and measured
  SD(X_D). That is the E.33 measured form. Whether to restate K2 this way is a lead decision.
- The budget's effect on the whole program: going from B = 0 to B = 300 raises every e80 by 1.5%. The choice of
  horizon and trade rate moves e80 by a factor of 2 to 8. The budget is not the lever on power. The trade rate is,
  and so is the measured dependence.

## (e) Holm at the test with up to 3 finalists

screening/stage_e_verdict.py runs Holm over the Tier A p_upper at 0.05 / K (lines 21-23, 545). K is the list's
`k_holm` in 1..9 (v13; lines 34-35, 84, 369-373). V14 (b) and E.32 P9 use K = 9 (protocol line 787). The steps are
`holm_alpha_k = 0.05 / K` and `threshold = alpha_K / (m - i)` (screening/stage_e_stats.py:288-293, 317-334).
p_upper is a stationary block bootstrap p (mean block 5, B = 10,000; stage_e_verdict.py:15-18), whose floor is
1/10,001 (z 3.72).

| K | m = 1 | m = 2 | m = 3 (first step) | m = 3, steps 1 / 2 / 3 (z) |
|---|---|---|---|---|
| 1 | 0.0500 (z 1.645) | 0.0250 (1.960) | 0.0167 (2.128) | 2.128 / 1.960 / 1.645 |
| 2 | 0.0250 (1.960) | 0.0125 (2.241) | 0.0083 (2.394) | 2.394 / 2.241 / 1.960 |
| 9 | 0.0056 (2.539) | 0.0028 (2.773) | 0.0019 (2.902) | 2.902 / 2.773 / 2.539 |

- The K = 9 row reproduces P7.2's 2.539 / 2.773 / 2.902 (protocol lines 716-718).
- Effect on the test bar: none, in normal-approximation terms. The strictest Holm z (2.902) is below t 3.0, and
  both are far below b_test's t of 4.86 to 4.95, so the combined bar is b_test whether there are 1, 2 or 3
  finalists and whether K is 1, 2 or 9. A ZL registration with two families (F10, F09) could use K = 2 or keep 9
  without changing power.
- Holm could bind only if the bootstrap SE of the daily mean exceeds the iid SE by a factor f with 2.902 f > 4.86,
  that is f > 1.67 (day-to-day autocorrelation; Lo 2002 eq. 19's factor, M5b c.2 item 3). The t > 3.0 and DSR
  checks use the iid SD and Mertens SE (stage_e_verdict.py:209-213, 197), so they do not inflate with dependence.
  The P10 or test report should state the series' SE_boot / SE_iid.
- Holm's m counts Tier A only (stage_e_verdict.py:541-545); Tier B does not enter Holm.

## (f) The open E.32 D2 item (V14 (c), the test DSR variance)

As coded, the program verdict's DSR takes V = pvariance of the Tier A Sharpes if there are 2 or more, else of Tier A
and Tier B (stage_e_verdict.py:23-25, 216-219, 550-553). So SR0 = e(N) x pop SD(tested Sharpes). E.32 D2
(reports/E.32_RETURN.md:436-440) recommends amending it so that V = 1/(T_test - 1). That would make check (1)'s
DSR identical to check (2)'s. The item "stays open until a test is registered (V56 item 4)" (E.32b recs line 487).

Multipliers (SR0 / s, with a member at observed s and nulls at exactly 0):

| N | e(N) | 1 member + 1 null | 1 member + 2 nulls |
|---|---|---|---|
| 838 | 3.2045 | 1.602 | 1.511 |
| 878 | 3.2179 | 1.609 | 1.517 |
| 900 | 3.2250 | 1.613 | 1.520 |
| 1138 | 3.2917 | 1.646 | 1.552 |

The 838 row reproduces P7.2 (protocol lines 727-729: "1.60 x", "1.51 x"). SR0 > s means DSR < 0.5. Beside null
companions, no true Sharpe can pass check (1), and the budget only raises the multiplier.

I also ran a synthetic simulation, drawing every member's estimate as N(s_i, se(s_i, 870)) with 4,000 reps at
N 838 (2,000 at N 1138; m4_out.md). Pass probabilities by true Sharpes:

| true Sharpes (finalist first) | V14 (c) DSR | amended DSR (= check 2) | t > 3 | as coded: all three | amended: DSR and t |
|---|---|---|---|---|---|
| 0.20 + 2 nulls (Tier A of 1, Tier B null) | 0.000 | 0.845 | 0.997 | 0.000 | 0.845 |
| 0.25 + 2 nulls | 0.000 | 0.995 | 1.000 | 0.000 | 0.995 |
| 0.40 + 2 nulls | 0.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| 0.25 + 0.15 | 0.704 | 0.993 | 1.000 | 0.699 | 0.993 |
| 0.25 + 0.10 | 0.210 | 0.994 | 1.000 | 0.206 | 0.994 |
| 0.20 + 0.15 | 0.848 | 0.857 | 0.998 | 0.725 | 0.857 |
| 0.20 + 0.10 | 0.387 | 0.842 | 0.999 | 0.294 | 0.842 |
| 0.25 + 0.20 + 0.15 | 0.855 | 0.991 | 1.000 | 0.851 | 0.991 |
| 0.25 + 0.15 + 0.00 | 0.002 | 0.994 | 1.000 | 0.002 | 0.994 |

The N 1138 values are 0.00 to 0.04 lower; for example, 0.20 + 2 nulls amended is 0.824.

- P7.2's analytic figures (0.83 for 0.25 beside 0.15; 0.09 for 0.25 beside 0.10; protocol lines 729-731) fix the
  companion at its true Sharpe. This simulation also draws the companion's noise. Its 0.70 and 0.21 differ for
  that reason (the gap's SD, sqrt(2) x 0.034 = 0.048, is half the 0.10 gap). This is a model difference, not an
  error in either.
- What D2 changes for ZL:
  - With a Tier A of 1, the most likely outcome given E.33's empty Tier A, the Tier B companions are selected with
    gates ignored and are likely near-null. As coded, the test then has power of about 0 for any true Sharpe.
  - Amended, the program bar is exactly b_test, and the power table in (b)/(c) holds: 0.80 at SR80_test.
  - With 2 or 3 real finalists, the coded version also depends on the gap between their true Sharpes, which the
    discovery outcomes cannot pin down.
  - Amending cannot loosen the bar below check (2), and Holm, t and PBO are unchanged (P9, protocol lines
    793-799).
  - Every e80 and power figure in this file assumes the amendment, or at least 2 real finalists of similar true
    Sharpe. If V14 (c) stays as coded, the ZL protocol should say that the tabulated powers are upper bounds.

## Verdict (arithmetic only; selection rules and gates are the lead's)

1. **Reproduced.** The frozen code reproduces E.32b's N 838 row and P7.2 to every printed digit. The same functions
   can serve the ZL protocol unchanged, with T_disc 796 and T_test 870 (MBO) or 885 (MBP-1).
2. **N barely matters.** B = 0 to 300 moves the binding threshold from 0.2007 to 0.2037 and test e80 by 1.5%.
   Any budget in {0..300} leaves K2's 1.8 ticks at 1.8.
3. **Trade rate and dependence matter.** At E.33's observed 1 to 2 trades a date, a 30-minute ZL rule needs 3.9 to
   5.4 ticks net at the test, 6.2 to 7.8 ticks gross. A 60-minute rule needs 5.2 to 7.4 net. These are floors:
   tails add 2 to 11%, and same-day correlation multiplies by sqrt(D_day).
4. **K2.** As a fixed 1.8 ticks, K2 is redundant with G4 for slow rules and stricter than needed for fast 15-minute
   rules. A rate- and horizon-matched form is available (section d). The choice is the lead's.
5. **Holm** never binds at the test (z at most 2.90 against b_test's t of 4.86 or more) unless the bootstrap SE
   exceeds the iid SE by more than 1.67 x.
6. **D2 is the one item that changes power materially.** Unamended, a lone finalist beside Tier B nulls cannot pass.

## (g) Protocol inputs (ready for P7)

Formulas: equations 1-8 above, computed with the functions named at the top. b_test is pinned at the unrounded
value at the registered N. Normal moments apply for the published rows; G3 and G4 use each configuration's own
moments at run time (P8).

Fixed inputs: T_disc = 816 - 20 = 796 (2020-12-01..2024-02-29, CBOT grain calendar). T_test = 890 - 20 = 870
(MBO, 2017-05-22..2020-11-30) or 905 - 20 = 885 (MBP-1, 2017-05-01..2020-11-30). V_disc = 1/795. V_test = 1/869
(MBO) or 1/884 (MBP-1). The DSR and G4 targets are 0.95 and SR_d - se >= b_test, and the daily t bar is 3.0.
z80 = 0.8416. sigma_h = 20.37 / 28.10 / 38.21 (h 15 / 30 / 60). n_cap = 19 / 9 / 4. c_f = 2.38.

| B | N | MBO test: G3 / b_test (unrounded) / G4 = binding / SR80_test / SR80 disc binding | MBO e80 test h15 cap, h30 cap, h60 cap | MBO e80 test h30 at n = 1 / 2 / 4 | MBP-1 test: b_test (unrounded) / binding / SR80_test |
|---|---|---|---|---|---|
| 0 | 838 | 0.1724 / 0.164882 / 0.2007 / 0.1936 / 0.2309 | 0.90, 1.81, 3.70 | 5.44 / 3.85 / 2.72 | 0.163470 / 0.1993 / 0.1920 |
| 40 | 878 | 0.1729 / 0.165339 / 0.2012 / 0.1941 / 0.2313 | 0.91, 1.82, 3.71 | 5.45 / 3.86 / 2.73 | 0.163924 / 0.1997 / 0.1924 |
| 62 | 900 | 0.1732 / 0.165581 / 0.2014 / 0.1943 / 0.2316 | 0.91, 1.82, 3.71 | 5.46 / 3.86 / 2.73 | 0.164164 / 0.2000 / 0.1927 |
| 100 | 938 | 0.1736 / 0.165984 / 0.2018 / 0.1947 / 0.2320 | 0.91, 1.82, 3.72 | 5.47 / 3.87 / 2.74 | 0.164564 / 0.2004 / 0.1931 |
| 150 | 988 | 0.1741 / 0.166489 / 0.2023 / 0.1952 / 0.2325 | 0.91, 1.83, 3.73 | 5.49 / 3.88 / 2.74 | 0.165064 / 0.2009 / 0.1936 |
| 200 | 1038 | 0.1746 / 0.166967 / 0.2028 / 0.1957 / 0.2330 | 0.91, 1.83, 3.74 | 5.50 / 3.89 / 2.75 | 0.165538 / 0.2014 / 0.1940 |
| 250 | 1088 | 0.1751 / 0.167421 / 0.2033 / 0.1962 / 0.2334 | 0.92, 1.84, 3.75 | 5.51 / 3.90 / 2.76 | 0.165988 / 0.2018 / 0.1945 |
| 300 | 1138 | 0.1755 / 0.167853 / 0.2037 / 0.1966 / 0.2338 | 0.92, 1.84, 3.76 | 5.52 / 3.91 / 2.76 | 0.166416 / 0.2022 / 0.1949 |

The e80 cells for B 40, 100, 150, 200 and 250 are SR80_test x sigma_h / sqrt(n) from the SR80_test column. They were
computed from the rounded SR80_test column (checked with a one-line python run, all cells agree), not printed by m4_power.py; the B 0, 62 and 300 cells are script output. A
registration recomputes the row at the registry's N immediately after its last registration (P7.1 rule) and on the
actual test schema.

## Inputs and sources used

- E.32 protocol P7-P9: reports/stage_e32_discovery_protocol.md:683-829.
- E.32b recs 4.4 and K2: reports/stage_e32b_recommendations.md:25, 478-531, 551-552.
- E.32b holding scope 1.5 and 15: reports/stage_e32b_holding_scope.md:14-18, 255-298, 913-951.
- E.33c 3.7 (v): reports/E.33c_RETURN.md:194-199. E.33 measured-e80 table: reports/stage_e33c_briefs/work/D_stats.md:249-292.
- Code: p7_final.py, p7_thresholds.py, funnel/multiple_comparisons.py, screening/stage_e_verdict.py,
  screening/stage_e_stats.py, and E.32b's scratch hurdles.py (path above).
- Methods brief: M5a d.2 (lines 7253-7285) and d.8 (7402-7417), M5b c.2 (8043-8079), and the Mertens/Opdyke
  evidence rows (8286-8287).
- Literature claims: none are new. The BLdP 2014, Mertens (via BLdP 2012) and Lo 2002 equations are cited through
  the E.32 brief's verified quotes (M5a d.8, M5b d.8). The brief marks "Var(SR_hat) ~ 1/T under the null" as
  [unverified] (line 7417), and that status carries over here.
