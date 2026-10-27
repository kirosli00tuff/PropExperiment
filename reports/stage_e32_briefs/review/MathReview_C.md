# MathReview C: M5a_validation.md, M5b_power.md and the p7 threshold cross-check

Reviewer: MathReviewer-FableXHigh (group C), re-spawned 2026-10-27 02:33 PDT after the 00:51 usage stop; no
scratch from the first spawn existed. Brief: reports/stage_e32_briefs/work/lead/brief_MathReviewer_C.md.
Work files: reports/stage_e32_briefs/review/work_C/ (`c_dates.py` own trade-date count, `c_calc.py` every
closed-form number, `c_sim.py` the Monte Carlo tables, `c_quotes.py` tolerant quote search, `c_addendum.py`,
`p7_rerun_budget500.md`, `log.tsv`; each with its `_out.txt`). No market data, no data/ file, no web fetch
(log.tsv records zero fetches). Every number below was computed from my own formulas before any reader
calculator or the lead's script was run; the reader calculators were not run at all; p7_thresholds.py was run
once, after my computation, and its output is byte-identical to the saved p7_thresholds_budget500.md.

Severity scale (brief): BLOCKING changes a verdict or would mislead the frozen protocol; SHOULD FIX is a wrong
number or derivation that changes no verdict, an unstated assumption, a quote not found, or an [unverified] item
carrying weight; NOTE is clarity.

## Counts

| File | BLOCKING | SHOULD FIX | NOTE | Verdict |
|---|---|---|---|---|
| M5a_validation.md | 0 | 3 (C-1, C-2, C-3) | 3 (C-4, C-5, C-6) | sound with fixes |
| M5b_power.md | 0 | 3 (C-7, C-8, C-9) | 3 (C-14, C-15, C-16) | sound with fixes |
| protocol/p7_thresholds.py + budget500 output | 1 (C-10) | 1 (C-11) | 2 (C-12, C-13) | arithmetic sound; two sections use different bars, fix before the freeze |
| Total | 1 | 7 | 8 | |

## Findings table

| ID | File:line | Claim as written | What is wrong | Correct value or derivation | Severity |
|---|---|---|---|---|---|
| C-1 | M5a 0.1 l.25; f.3 l.660-668 (table) and l.670-672 (power); summary l.758 | Test-window trade dates 2017-05-01..2020-11-30 "about 899 (936 weekdays minus an assumed 37 closures)", "error about +-3 dates" | 37 closures is 6 too many; no list was given. CBOT grain full closures in the window are 31 | 936 weekdays - 31 = 905. My typed list (c_dates_out.txt: 2017 x5, 2018 x9, 2019 x9, 2020 x8) is identical date for date to the program's grains/hist2010 calendars, which p7 reads (31 dates printed in work_C). Effect on f.3: SR = z/sqrt(905) gives 0.0547/0.0707/0.0997 for z 1.645/2.128/3.0 (table has 0.0549/0.0710/0.1001); gross ticks unchanged to 2 d.p.; power 0.998/0.981, 0.661/0.323, 0.373/0.116 (vs 0.998/0.98, 0.66/0.32, 0.37/0.12). No verdict moves | SHOULD FIX |
| C-2 | M5a d.2 item 4 l.343-346 | "if SR_hat and sqrt(V) are both multiplied by sqrt(q) (annualising) then T must become years, and z is unchanged" | Not true beyond first order. z = (SR - sqrt(V) e(N)) sqrt(T - 1) / sqrt(D): the factor sqrt(T/q - 1) is not sqrt(T - 1)/sqrt(q) at Y = 3.25 years (1.50 vs 1.80), and D's SR^2 term scales by q (annual D = 1 + SR_ann^2/2 = 4.6 at SR_ann 2.68) | c_addendum_out.txt: per-trade SR 0.1689, T 816, N 738, V 1/T gives z 1.644, DSR 0.950; the same inputs annualised (SR 2.676, V x 251, T 3.25) give z 0.644, DSR 0.74; monthly basis DSR 0.924. Replace the sentence with the rule the section already applies: compute DSR on the native basis (per trade or daily with zeros) and never rescale inside the formula; SR*_ann ~ t*/sqrt(Y) stays valid as a display conversion of the t-bar only. The program's docstring warning is the correct statement | SHOULD FIX |
| C-3 | M5a a.5 l.121-130 (and a.4 l.116) | Purge test "on timestamps only: ... max(t_i,1 over training rows before the block) < a_j ..." | The test is only as good as the clock. The trap the brief names (ts_event vs ts_recv) is missing: a label end computed on ts_event with a decision time on ts_recv (or a feature computed at ts_event and acted on later) leaks by the feed latency, and the unit test as written cannot see it because both timestamps come from the same row table | Add one row: "Decision time and label end taken from different clocks" with the test "declare the clock (ts_recv, or ts_event + a fixed latency) in the protocol; assert both t_i,0 and t_i,1 are built from it; assert t_i,0 >= the ts_recv of the last feature input". F_data_facts may own the clock choice, but the purged-CV assertion needs it | SHOULD FIX |
| C-4 | M5a d.8 l.489; 0.1 | "Var(SR_hat) ~ 1/T under the null: Lo 2002 / Mertens 2002 not fetched; standard result used as an assumption [unverified]" | It is verified in group C's other file: M5b d.8 row 1 quotes Lo 2002 line 223 ("VIID = 1 + 1/2SR") from the saved full text, which gives Var ~ 1/T at SR 0 | Cross-cite M5b d.8 / pages/M5b_power/lo_2002_faj_statistics_sharpe.txt l.223 and drop [unverified] | NOTE |
| C-5 | M5a e.3 l.541 | PBO noise row "200 configs, S = 16, 12 repetitions: sd 0.114, 5%-95% 0.341-0.671" | 12 draws give an sd with about +-20% relative error and a 5-95% band that is really the min-max of 12 values. My 6-draw check gives sd 0.161, band 0.222-0.635 | Mark the row as indicative or run 200 repetitions (12,870 splits x 200 configs x 200 reps is still under a minute in NumPy). The text's conclusions rest on the 200-rep rows, which reproduce: mean 0.487/0.519, sd 0.222/0.173, bands 0.14-0.86 / 0.24-0.82; one true SR 0.10: mean 0.322, band 0.07-0.67 (c_sim_out.txt) | NOTE |
| C-6 | M5a f.4 item 2 l.683-686; f.8 l.711; summary 3 l.756-758 | "No N-deflation is needed [at the one-shot test] for validity" | Correct as statistics (the test data played no part in selection), but it is one side of a three-way disagreement about the test bar: screening/stage_e_verdict.py l.22-26 applies "DSR > 0.95 at the list's program N" on the test series, and p7's test_bars section computes that bar as binding (t-equivalent 4.92). See C-9 and C-10. M5a should say that its Holm-over-3 bar presumes the lead drops the DSR-at-N component at the test, or state the consequence if it stays | NOTE (the decision is the lead's) |
| C-7 | M5b 0 l.19; c.3 l.361-390; c.8 l.466-469; d.3 item 3 l.529; "What this means" l.583-587; Failures l.610-611 | Test-window trade dates "904 (range 903-905) ... 936 weekdays minus 32 typed closures ... plus 2018-12-05, the national day of mourning, [unverified] whether grains closed" | 2018-12-05 is not a grain full closure in the program's calendars (31 closures, printed in work_C); my recollection, [unverified, no CME page may be fetched], is that CME closed only its US equity-index and interest-rate markets that day and agricultural markets kept regular hours. The program calendar is the source of record for E.33 | 905. Every "/test day" figure moves by 0.1% (e.g. 8,786/905 = 9.71, not 9.72; 1,313/905 = 1.45 unchanged); the gate formula "k_test x 904" should read 905. No verdict moves. The brief's 816 discovery dates are confirmed by all three counts and by my list | SHOULD FIX |
| C-8 | M5b d.2 item 6 l.509-511 | "The 80%-power sample is ((c + 0.8416)/SR)^2, larger by ((c + 0.8416)/c)^2: 1.639 at c = 3.0, 1.776 at c = 2.128" | The second number is wrong | ((2.1280 + 0.8416)/2.1280)^2 = (1.3955)^2 = 1.947; M5b's own worked example gives 1,313/677 = 1.94 (d.3 item 2). 1.639 at c = 3.0 is right (my 1.640), and the verdict line "1.64 times MinTRL at t > 3" is unaffected | SHOULD FIX |
| C-9 | M5b c.2 item 2 l.332-335; c.2 item 8 l.354-356; c.8 l.466-469; "What this means" item 1 l.583-587 | "The program bar t > 3.0 ... is stricter, so when both apply c = 3.0 binds"; the P8 gate uses c = 3.0 | The program's test verdict chain (stage_e_verdict.py l.22-26) also requires DSR > 0.95 at the program N on the test series. p7 shows that under V = 1/(T - 1) that bar is daily SR 0.1637 at T 905, N 1,038, a t-equivalent of 4.92, which binds over t > 3.0 (0.0997) and over Holm-over-3 (0.0707). Under the program's actual V (population variance of the <= 3 tested Sharpes, or of the cluster's run trials) the bar is undetermined before the read | If the DSR-at-N component applies at the test, trades needed scale by ((4.92 + 0.8416)/(3.0 + 0.8416))^2 = 2.25: 15-minute holds at mu = 1 need 5.5 trades a date (not 2.4), at mu = 0.5 21.9 (not 9.7, and above the 19-per-day day-session cap). The gate formula must name the bar it uses (c = 3.0 only if the lead drops DSR at the test; otherwise c = the DSR t-equivalent at the frozen V), and c.8's "rules out ..." list changes accordingly | SHOULD FIX (BLOCKING if the gate is frozen at c = 3.0 while the test keeps DSR at N; see C-10) |
| C-10 | p7_thresholds.py report() l.122-136 (output l.25-60) versus test_bars() l.141-175 (output l.62-93) | "Power of the one-shot test (905 trade dates, alpha 0.0167 one-sided = Holm step 1 over 3, power 0.8)" with a "feasible" column; then "Net edge per trade for 80% power at the binding bar (c = 1): true daily SR 0.1917" | The script's own binding bar is daily SR 0.1637 (t 4.92), yet the power table and its feasibility verdicts are computed at z 2.128. Trades needed differ by ((4.92 + 0.8416)/(2.128 + 0.8416))^2 = 3.76. Example: h = 15, mu = 0.5: power table says 5,250 trades, 5.80 a day, "feasible: yes"; at the binding bar n = (0.1917 x 12.20 / 0.5)^2 = 21.9 a day, over the cap of 19, "no". h = 15, mu = 1.0: 1.45 a day becomes 5.47. h = 60, mu = 1.5 "yes" (2.58) becomes (0.1917 x 24.40 / 1.5)^2 = 9.7 a day, "no" | Both sections must use the one bar the protocol freezes. Either (i) recompute the power table with c = the DSR t-equivalent at the frozen V (replace `a_test` by `1 - Z.cdf(bar * sqrt(t_test))` or compute n = (s_req sigma_h / mu)^2 directly), or (ii) if the lead drops DSR at the test, delete the "binding bar (c = 1)" section and use c = 3.0 or 2.128 consistently. The trades_needed arithmetic itself is right (every cell reproduced to the unit, c_calc_out.txt) | BLOCKING |
| C-11 | p7 test_bars() l.144-147, l.158-160 | "The DSR's Sharpe variance V is unknown before the read, so V = c / (T - 1) is tabulated" | The program's verdict does not use a null c/(T - 1): `dsr_table` (stage_e_verdict.py l.216-229) takes `statistics.pvariance` of the Sharpes over `variance_over` (the Tier A trials when two or more, else the cluster's run trials, docstring l.23-24). With <= 3 selected candidates that variance is small and the SR0 benchmark collapses toward 0 (M5a d.5's "V over survivors" trap, anti-conservative); with the cluster's run trials it is a quantity nobody has defined for E.33 | The output should say which V the verdict will use and the protocol should freeze it (M5a d.3(v)'s rule: empirical V with the literal N, or V = 1/T with an effective N, never empirical V with an effective N). Until then the c-grid is a sensitivity table, not the bar | SHOULD FIX |
| C-12 | p7 test_bars() docstring l.147 | "the observed Sharpe is about N(s, 1 / sqrt(T)) (normal days)" | SE is sqrt((1 + s^2/2) / T) (Lo 2002 eq. 8-9, quoted in M5b d.8) | At s 0.19 the understatement is 0.9%; the 80%-power column is 0.1917 vs 0.1920. Negligible; state the approximation | NOTE |
| C-13 | p7 docstring l.8; funnel/multiple_comparisons.py:66 (quoted in M5a 0.2) | "Bailey and Lopez de Prado 2014, eq. 3 for the expected maximum" | Eq. (3) is the Appendix A.1 number; the main-text equation is (1) (M5a 0.2 already says so) | Cite "eq. (1); Appendix eq. (3)" | NOTE |
| C-14 | M5b b.3 item 3 l.240-246; b.2 item 3 l.200 | "42 noise months and one month at +6 SD gives t > 3 in 1.7% of draws" | The Monte Carlo t is sum/sqrt(M) with the variance known to be 1; a real t uses the sample SD, which one +6 month inflates to about sqrt(1 + 36/43) = 1.36, so the one-spike false-pass rate under a real t-statistic is lower than 1.7% | Say the 1.7% is an upper bound (known-variance t); the dominance rules' catch rates (78.5% / 66.3% / 82.4%) reproduce: 0.789 / 0.663 / 0.828 (c_sim_out.txt) | NOTE |
| C-15 | M5b a.2 MDA l.56-58; a.5 item 3 l.111-112 | Permute column j "by a random permutation pi inside T_k only" | An i.i.d. row shuffle of a persistent feature (rolling volatility, crush beta, lagged OFI) destroys its own autocorrelation as well as its link to y, which is exactly the extrapolation Hooker et al. describe (quoted in a.9). Block permutation (whole trade dates) or Strobl 2008's conditional permutation inside T_k keeps the feature's dynamics. M5b uses a block-permuted copy only for the noise canary | Add: "permute in whole-trade-date blocks inside T_k; report the i.i.d. version beside it" | NOTE |
| C-16 | M5b c.2 item 6 l.350-351; c.9 last row | "A common automatic lag is floor(4 (T/100)^{2/9}) = 6 ... [rule attributed to Newey and West 1994; not read here]" | The arithmetic reproduces (6.38 -> 6 at T 816, 6.52 -> 6 at T 905); the attribution is [unverified]. If P8 freezes "lag 6", freeze the formula, not the citation | Keep the formula; cite it as a rule of thumb or fetch the source | NOTE |

## Item 7: cross-check of p7_thresholds.py against M5a and M5b

1. Trade-date counts. Independent count (c_dates.py, holiday list typed by me before reading any calendar):
   2017-05-01..2020-11-30 has 936 weekdays and 31 CBOT grain full closures, so 905 trade dates; 2020-12-01..
   2024-02-29 has 848 weekdays and 32 closures, so 816. The program's calendars (hist2010 grains before
   2019-05-01, data.calendars.grains after; coverage to 2026-06-19) hold exactly the same 31 and 32 dates (printed
   in the work_C run log). So the script's 905 is right. M5b's 904 adds 2018-12-05 (not in the program calendar;
   my memory [unverified] is that CME kept agricultural markets open that day). M5a's 899 assumed 37 closures with
   no list; it overcounts by 6 (plausibly the early-close days, which are not closures). The script's
   `full_closures` join of the two calendars is correct for both windows (no boundary gap at 2019-05-01).
2. Required daily Sharpe for DSR >= 0.95 at N = 1,038 (own formula, c_calc_out.txt; the program's
   `deflated_sharpe_ratio` through p7 gives the same to 4 decimals):
   T = 816: 0.1150 / 0.1388 / 0.1724 / 0.2201 at c = 0.25 / 0.5 / 1 / 2 (normal), 0.1755 at c = 1 with skew -0.5,
   kurtosis 6; annualised x sqrt(252): 2.20 / 2.74 / 3.49 at c = 0.5 / 1 / 2.
   T = 905: 0.1092 / 0.1317 / 0.1637 / 0.2089; skew case 0.1665 at c = 1.
   t-equivalents at c = 1: 0.1724 sqrt(816) = 4.93 and 0.1637 sqrt(905) = 4.92, against e(1,038) + 1.645 =
   3.2657 + 1.6449 = 4.91 (M5a's rule), and against M5a's 4.81 at N 738 and 5.02 at N 1,538: consistent.
   E[max SR] = sqrt(V) e(N): 0.0809 / 0.1144 / 0.1618 at T 816 (output rows match).
3. Power arithmetic. `trades_needed` = ((z_alpha + z_0.8) sigma / mu)^2 is the standard one-sided normal
   formula; every one of the 30 cells reproduces to the unit (e.g. h 15, mu 0.5: (2.9696 x 12.20 / 0.5)^2 =
   5,250; /905 = 5.80). `cap = 290 // h` gives 58/19/9/4/2/1. The "feasible" column is correct for the bar the
   table uses (z 2.128) but that is not the script's own binding bar: C-10.
4. `test_bars` derivation. t_bar = 3/sqrt(905) = 0.0997; s = bar + 0.8416/sqrt(905) = bar + 0.0280 (0.1277 for
   t > 3; 0.1917 at the c = 1 DSR bar), correct to first order (C-12). mu = s sigma_h / sqrt(n): with n independent
   trades on every trade date, each mean mu and SD sigma_h, the daily P&L has mean n mu and SD sigma_h sqrt(n), so
   its Sharpe is mu sqrt(n)/sigma_h and mu = s sigma_h/sqrt(n). Correct. All 17 cells reproduce (h 15, n 1:
   0.1917 x 12.20 = 2.34; n 4: 1.17). Two conditions the docstring should state: (i) trades on every date (if a rule
   trades on a fraction p of dates the daily-with-zeros Sharpe is sqrt(p) times the per-trade one, M5a d.3(iv), so
   s must be the daily series' Sharpe); (ii) independence across the n trades (M5b's D factor; with D > 1 replace n by
   n/D).
5. Cross-file DSR t-bars: M5a 4.81 (N 738) and 5.02 (1,538) both reproduce (e(N) 3.1677 and 3.3756, exact
   E[max] by integration 3.1534 and 3.3633, so the Bailey-LdP approximation is 0.4-0.5% high, as M5a says). p7's
   N 1,038 sits between them at 4.91-4.93. M5b's power numbers at c = 3.0 and z 2.128 reproduce; the gap between
   M5b's gate (c = 3.0) and p7's binding bar (t 4.92) is C-9/C-10.

## M5a_validation.md, topic by topic

### 0. Shared inputs
Checked and correct: sigma_h = 3.15 sqrt(h) = 7.044 / 12.200 / 17.253 / 24.400 / 34.507 / 48.800 (stated as an
assumption); break-even 1.59 ticks is the mu*_mkt column of reports/stage_e28_ranking.md line 130 (header line 123
confirmed: "mu*_lim | mu*_mkt | mu10K | cost/attempt", row "0.59 | 1.59 | 0.86 | 49.23"); 848 weekdays, 32
closures, 816 dates; 765 + 290 = 1,055 minutes; 860,880 slots; 3.25 years. Section 0.2: every file:line cited for
the program functions is correct (funnel/multiple_comparisons.py 63/81/116/143, HLZ_HURDLE = 3.0 at line 28;
screening/stage_e_verdict.py 197/216/231, DSR_MIN 0.95 l.89, T_MIN l.90, N_PBO_BLOCKS 8 l.92;
screening/stage_e_stats.py 288/317, FAMILY_ALPHA l.103, MAX_FAMILIES l.108; ml_route_v2/constants.py 128-132;
ml_route_v2/cpcv.py 735/761/769). Wrong: test-window dates 899 (C-1).

### (a) Purged and embargoed K-fold
Equations: purge interval [a_j - h, b_j + h_max] follows from t_i,1 >= a_j and t_i,0 <= b_j + h_max with
t_i,1 = t_i,0 + h; embargo (b_j + h_max, b_j + h_max + e]; the session-alignment argument (whole trade dates as
folds, labels clipped at the 13:20 close, so purge set empty) is valid, with the stated caveat for overnight-hold
labels; phi and AFML 0.01T correctly restated. Worked example: 81.6, 734.4, 24.40, 2 x 60 = 120 slots, 10 x 120 /
860,880 = 0.139%, 1/734.4 = 0.136%, 10/816 = 1.23%, Li overhead 10 x (120 + 1,055)/860,880 = 1.365% (= 0.139% +
1.23%), 8,609 slots = 8.16 dates, 8.16/734.4 = 1.11%, 20/734.4 = 2.72%, 10 x 480/860,880 = 0.558%, 714/734 =
97.3%: all correct. Quotes: LdP 2018 purging (l.506-507), embargo-only-after (l.528 in the file; M5a says
l.515-518, the file's line numbering differs by the figure block, text found), 0.01T (l.522-523, found; italic
math glyphs defeat a plain grep), Li "sanitization overhead" and "H + c tau" (found), Cerqueira stationary (l.35,
found). Leakage traps: real and testable; missing the clock trap (C-3). Verdict USE follows.

### (b) CPCV
phi[N,k] = (k/N) C(N,k) = C(N-1,k-1) (algebra checked); the b.3 table (15/5/136, 28/7/102, 45/9/81.6,
120/36/81.6/0.70, 66/11/68, 120/15/51), 650.8 training dates, 1/sqrt(816) = 0.0350, x sqrt(252) = 0.556, +-1.1;
the compute table (3,000 fits = 5.0 h at 6 s, 0.42 h at 0.5 s ... 225,000 fits = 375 h / 31.3 h); 15,776 rows;
344 MB: all correct. The argument that the path spread measures training-set instability and not sampling error
is right (all paths share the test dates). Quotes: LdP path-count sentence (l.596 in file), "as opposed to a
single (likely overfit)" (found), Li l.745 and l.524-525 (found). Verdict MAYBE follows. Arian 2024 is marked
[unverified] and carries nothing.

### (c) Walk-forward
F = floor((L - W_1)/Delta), beta = F Delta/L; the table (9/27/0.69, 7/21/0.54, 5/15/0.38, 4/24/0.62); 62.8 dates a
quarter; 251 to 754 training dates; P(>= 6 of 9) = 130/512 = 0.254; 1,800 fits = 3.0 h; 45,000 = 75 h: correct.
Li Proposition 7 restated correctly (file l.495-503: Var L-hat of order sigma_inf^2/(beta T); A.4 l.907-912:
theta_1 - theta_0 = (1 - beta) Delta, so worst-case error >= (1 - beta) Delta/2). Quotes: Li l.750-752
(found, hyphenated across lines), l.533 "conjures information" (found), Cerqueira l.36-39 and "Rep-Holdout"
(found), LdP walk-backward and "History is a filtration" (found, multi-line). The reversed walk-forward is labelled
a suggestion. Verdict USE follows from the two sources' conditions (expected non-stationarity).

### (d) Deflated Sharpe ratio
Equations 1-2 match the program's body and the paper's three printed outcomes; the null calibration t* ~ e(N) +
1.645 sqrt(D) is correct and D's 2% bound at per-trade SR <= 0.3 holds (D = 1.045 at SR 0.3, gamma4 3). Item 4's
invariance claim is wrong beyond first order (C-2). Items 5-6 (eq. (9) N_hat, ONC, participation ratio, MinBTL)
restated correctly. Worked examples, all reproduced (c_calc_out.txt): e(N) table (3.1677 / 3.3756 / 3.7137 and
the Z^-1 columns), sqrt(2 ln N); the whole d.3(ii) table (every SR0, the three SR* columns, t*, gross ticks, SR_ann,
e.g. T 816 N 738: 0.1109, 0.1689/0.1699/0.1724, 4.83, 3.65, 2.68; T 3,264 N 5,538: 0.0650, 0.0939/0.0940/0.0947,
5.36, 2.74, 2.97); d.3(iii) DSR 0.589/0.553/0.471/0.342 and 0.914/0.899/0.858/0.771 at t 3.30 and 4.47; d.3(iv)
sqrt(p) scaling and kurtosis gamma4/p = 18 (my own 1,000-draw check: mean z 1.665 per trade vs 1.659 daily,
correlation 1.0000); d.3(v) (1 - rho)/T = 0.000613, N_hat 500.5, K_eff 3.99 / 1.56 / 55.1 / 235.8 and the
effective-N table's e values (3.143 ... 3.266); d.3(vi) e(45)^2 = 5.00, 10.0 / 11.4 / 13.8 years, 1.76 / 1.87 /
2.06 annualised. Quotes: BLdP 2014 "only a 90% chance", "0.9505", "after N=88", "five additional variables",
"only N trials are independent" (all found); LdP-Lewis three quotes (found, multi-line); Nikolopoulos l.264
(found); BBLZ 2014 "45 independent model configurations" (l.470, found). Traps: complete for the topic (the
survivors-only V trap is the one p7 trips, C-11). Verdict USE follows; the range t 4.8-5.4 is conditional on V =
1/T, which the section states.

### (e) PBO / CSCV
Equations match the paper (omega = r/(N+1), logit orientation fixed by the "High logit values" sentence, which is
in the file at l.488 hyphenated "consis-tency"); the program's (worse + 0.5)/N convention gives the same sign of
lambda (algebra checked for all N). C(8,4) = 70, C(16,8) = 12,870, "12, 780" typo confirmed in the file (l.453,
2 hits). Hand split: training 18/-1/-10/4, test -10/6/18/-4, omega 0.2, lambda -1.386; over all 70 splits my code
gives PBO 56/70 = 0.800 and 32/70 = 0.457 OOS losses, and the tie on {b1..b4} at 4/4/4/0 is real. Noise table
reproduced for the 200-rep rows (C-5 for the 12-rep row); P(PBO < 0.4 | null) 0.25-0.38 in my runs, consistent
with "roughly one null search in three". Quotes: "even number S of disjoint submatrices" (l.452), "underperform
the median", "greater than 0.05", "even if phi ~ 0" (found). Verdict USE-as-diagnostic follows.

### (f) FWER versus FDR
Equations (Bonferroni, Holm step-down, BH, BY with L_m, Storey pi0, White RC, Hansen SPA recentring, Romano-Wolf
stepdown, HLZ p 0.0027) correctly stated. Thresholds table: every Bonferroni z, L_m (7.182 at 738), BY z and BH
3rd-rejection z reproduced to 3 decimals; HLZ = Bonferroni over 37.0 one-sided tests; Bonferroni over 12 and 15:
2.638, 2.713; Holm over 3: 2.128/1.960/1.645. Equicorrelated-max quantiles by numerical integration: 3.471 / 2.906
(738), 3.612 / 2.997 (1,538), 3.843 / 3.146 (5,538) against the table's simulated 3.472 / 2.903, 3.607 / 2.995,
3.844 / 3.152: agree to the simulation's precision. DSR-as-test size 5.50e-4 / 3.96e-4 / 2.32e-4 (91 / 126 / 215
times stricter than 5%; "about 100" is fair). ZM-unit table and power: reproduce at 899; the 905 values are in C-1.
Quotes: HLZ "greater than 3.0" (found, multi-line), "0.27%" (found), "3.9 and 3.0" (found), "Both Bonferroni and
Holm" (l.2362), Fithian-Lei three (found), Storey "as or more extreme" (l.226-229, two-column layout), White
(found, multi-line), BH 1995 Theorem 1 (l.20), Hansen (found), Romano-Wolf (found). Holm 1979 and BY 2001 are
[unverified] originals quoted through HLZ and Fithian-Lei; they carry procedure statements that are textbook and
correctly given, so no finding. Verdicts follow; the test-bar position is C-6.

### Planner pointers and summary
The "Bonferroni across K with Bonferroni within = global Bonferroni" point is correct (0.05/4/50 = 0.05/200).
Summary item 3's 899 is C-1; item 1's numbers reproduce.

## M5b_power.md, topic by topic

### 0. Shared quantities
sigma values (7.044 / 12.200 / 24.400 / 27.280) correct and the random-walk assumption is stated with its
conditions; 1.59 cited to the same E.28 row; months 43 / 39 and blocks 14 + 1 / 13 correct; critical values
2.1280 / 0.8416 / 1.6449 / 0.00135 correct. Hit-rate conversion gross = (2p - 1) E|r|, E|r| = sigma sqrt(2/pi) =
9.734, p = 0.6074 / 0.6859 / 0.5537: correct under the stated sign-size independence. Test-window dates 904: C-7.

### (a) Feature importance
Equations are the standard MDI / MDA / clustered MDA / SFI / LOCO definitions; the SE(MDA) <= sqrt(f/n) bound is a
valid binomial-type bound under the stated independence caveat. Worked example: 0.195 / 0.389 / 0.112 ticks a
point, 57,392 and 15,776 rows, SE 0.00187, 2 SE = 0.37 points = 0.073 ticks, ln 2 - H(0.6074) = 0.02323
(M5b 0.02325, rounding of p), 10.7 points: all correct; 220 MB correct. Quotes: Breiman OOB permutation (found,
multi-line) and "percent increase in misclassification rate" (found); Falces Marin two (found); LdP "research
tool" (l.187); Strobl 2007 two and 2008 one (found); Hooker two (l.22 and multi-line); Fisher-Rudin "Rashomon"
(l.72); Man-Chan two (found); Ambroise-McLachlan two (found); mlfinlab "snippet 6.5.2.1 page-85" (l.1); MLAM
ToC "Feature Importance Analysis" (l.25). MLAM 6.5 and AFML ch. 8 are [unverified] but the verdict rests on the
verified substitution-effect sources, so no finding. Traps: real; the permutation-dynamics point is C-15. Verdict
follows.

### (b) Stability
Equations: binomial null, Phi(delta/sqrt(M)) alternative, stationary bootstrap (checked against the Politis-Romano
p. 468 page image: "let X*_{i+1} be equal to X_{J+1} with probability 1 - p ... is indeed stationary", and p. 470
"with n fixed, let X_j for j > n be defined to be X_{j-n}", both exactly as typed), the one-sided centred p-value
(same form as the program's p_upper in stage_e_verdict.py l.18), the Politis-White block length with the 2009
correction (D_SB = 2 g(0)^2, so b = (G/sigma_LR^2)^{2/3} T^{1/3}; the arch docs file contains the lambda and c_i
= 2 statements), and the AR(1) closed form b = T^{1/3} (2 phi/(1 - phi^2))^{2/3} (derived independently: G = 2
gamma_0 phi/(1 - phi)^2, sigma_LR^2 = gamma_0 (1 + phi)/(1 - phi)). Worked examples: P(Bin(43) >= 29) = 0.0158,
>= 26: 0.1110, >= 33: 0.0003, Bin(39) >= 26: 0.0266, Bin(13) >= 9: 0.1334, Bin(14) >= 10: 0.0898, normal approx
2.135 / 0.0164, Phi(1.065) = 0.857, tercile 0.961 / 0.368 / 0.701, spike 0.0174, block lengths 3.33 / 2.09 / 5.39 /
7.33 / 3.22 (3.33 at 905 too): all correct. Monte Carlo (c_sim_out.txt, 200,000 draws): quarters rule P(pass)
0.971 / 0.951, P(t > 3 and rule) 0.797 / 0.791 vs 0.800; months rule 0.728 and 0.431; dominance median 0.103, 99%
0.169, P(share <= 0.25) = 1.000, LOMO 1% 2.63, P(all > 2.5) 0.9993; spike catch rates 0.789 / 0.663 / 0.828: all
match M5b within noise. Quotes: PPW 2009 (found), E.28 line 11968 (confirmed), R3a l.60 OS formula (confirmed).
Verdict follows; C-14 is a caveat.

### (c) Power
Equations 1-8 correct (the overlap D = m derivation checked algebraically and by my own simulation, D = 3.07 for
m = 3; the NW eq. (5) and Bartlett weights confirmed on the NBER document page 3 image exactly as typed; the
"2 pi times ... modified Bartlett weights" sentence is there too; Lo eq. 19 and the "reduces to Equation 17"
sentence found at l.305-320 of the two-column text). Worked examples: 8,786 / 9.72 / 10.77 by hand; the 9-row
table (all 27 trade-count cells and the caps 211 / 58 / 70.3 / 19.3 / 17.6 / 4.8); the MDE table (30 cells);
NW shortfall 1.3958 and 1.037; D 1.45 / 1.90; the event table (18 MDE cells and 18 power cells, e.g. 10.72 and
0.119 by hand; 1.685 for 39 df): all correct. E.28 line 8054 and 11626 and R4 line 235 quotes confirmed. Traps
real. Verdict: arithmetic right at c = 3.0; the bar question is C-9. Trade dates C-7.

### (d) Sharpe SE and MinTRL
Equations: Lo V_IID (quote l.223 found), Mertens form and its (gamma4 - 1)/4 rewrite (algebra checked), PSR and
MinTRL exactly as the BLdP 2012 code lines (both found verbatim), the link MinTRL ~ (c/SR)^2 = 50% power. Worked
examples: 0.014142 / 0.014166 / 0.014510 / 0.014926, V 1.052742, sqrt(1.45) = 1.204; MinTRL 1,345 (1,411) vs
2,197, 677 (711) vs 1,313, 1,792 (1,866) vs 2,929, 5,364 (5,485) vs 8,786; 1.633; annualised 1.30, 5.4 years,
3.6 years, delta 2.465, power 0.30: all correct. The 1.776 ratio is C-8. Quotes: BLdP 2012 six (found), Benhamou
(found), BLdP 2014 PSR sentence (found), Opdyke abstract (found, abstract only and so marked). Verdict follows.

## Everything checked and found correct (coverage)

- Closed-form numbers recomputed from my own formulas and matching the file to the printed precision: M5a 0.1
  (8), a.3 (12), b.3 (24 table cells + 6), c.3 (14), d.3 (e(N) table 18, DSR table 77 cells, d.3(iii) 10, d.3(v)
  12 + 4 + 16, d.3(vi) 5), f.3 (thresholds 42 cells, max-quantiles 9, sizes 3, Holm/Bonferroni 5, ZM units 16,
  power 6); M5b 0 (10), a.3 (12), b.3 (binomials 6 + 12 others), c.3 (27 + 6 + 30 + 4), c.4 (36 + 3), d.3 (16):
  about 450 numbers, all correct except those in C-1, C-2 (a claim, not a number), C-7, C-8.
- Simulated tables reproduced by my own code within Monte Carlo error: M5a e.3 (hand split and 70-split PBO,
  3 null rows, 1 signal row), d.3(iv); M5b b.3 items 2-3 (7 statistics), c.3 overlap D.
- Program references: 20 file:line citations in M5a 0.2 and the verdict constants, all correct.
- p7_thresholds.py: calendar join, 2 trade-date counts, 6 E[max] values, 6 required-Sharpe values and their
  annualisation, 6 multiple-testing rows, 30 power cells, 5 test-bar rows, 17 net-edge cells: all reproduced;
  rerun byte-identical to the saved output.
- Verbatim quotes: M5a 38 checked (of about 55), M5b 30 checked (of about 40), all found in the saved pages
  (five needed whitespace / ligature / two-column tolerant matching; two scanned sources checked on the page
  images). No quote missing, no number absent from its source. [unverified] items carrying weight: none that a
  verdict depends on (C-4 is a cross-cite, C-16 a rule of thumb).
- Equations re-derived: purge/embargo intervals, phi[N,k], Li Proposition 7 restatement, DSR z and its null
  calibration, N_hat and K_eff, MinBTL, PBO logit orientation and the program's rank convention, Holm/BH/BY/
  Storey/RC/SPA/Romano-Wolf statements, hit-rate conversion, SE(MDA) bound, binomial and Phi(delta/sqrt(M))
  alternatives, stationary-bootstrap p-value, Politis-White block length and its AR(1) closed form, n_iid, Lo's
  D factor, overlap D = m, same-day D, NW eq. (5), Lo/Mertens variance and its rewrite, PSR, MinTRL, the
  50%-power link, and p7's mu = s sigma_h/sqrt(n).

## Could not check
- Whether CME's agricultural markets traded on 2018-12-05 (no CME page may be fetched; the program's calendar
  says they did; my memory agrees but is [unverified]).
- The Politis-Romano JASA 1994 and Newey-West 1994 originals (not on disk; the Statistica Sinica and NBER copies
  were checked on their page images instead).
- M5a's Monte Carlo columns that depend on its own seeds (the "Monte Carlo mean max" column, the d.3(v)
  simulated means); I checked them against exact integration and analytic values instead, and they agree.
