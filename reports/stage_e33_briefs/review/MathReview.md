# MathReview (Stage E.33 B7, MathReviewer-FableXHigh)

Written 2026-10-28 02:19-02:45 PDT (times from `date`). Standard: reports/stage_e32_discovery_protocol.md (sha256
c4ffb9d7...) and reports/stage_e33_briefs/INTERFACE.md. Rule 1 (INTERFACE 2): label VALUES appear only inside the
equality checks below; no statistic of labels was computed or printed anywhere (work files included).
Work files: reports/stage_e33_briefs/review/math_work/ (own scripts hand_replay.py, hand_history.py,
hand_features.py, hand_labels.py, b5_arith.py, oracle_check.py; intermediates features_work.txt, labels_work.txt,
hist_<date>.npz, hand_values.json, hand_label_results.json). No import of feat33, lab33, build_*, or anything
under implB/; raw records only through data33 (guard33); the ZM book through mbo_book31.Book with my own driver.

## 0. Status log
- 02:19 brief, INTERFACE 1-4, protocol 0.3, P1.4, P3, P4, P4.2, P7.2 read; free -m 10.4 GB available.
- 02:25 replay probe (ZM front of 2022-09-29, own loop): 1.5 s per date; 17% of the front's F_LAST events carry
  more than one ts_recv, so the first probe's "live book at u" snapshot was wrong; fixed to the state at the last
  F_LAST record <= u (0.3) before any value was compared.
- 02:30-02:34 history passes (20 dates before 2022-09-29 and before 2021-08-16), one process, nice 10.
- 02:36 features recomputed; 02:38 labels recomputed (A's T15/T30 tables were complete at 02:33: no wait).
- 02:39 B5 arithmetic; 02:40 oracle check on check seed 80001.
- Tables compared: A features DERIVED/features/c22b0a50f4cd (manifest = current feat33.py 1c40775e...,
  build_features33.py 74317731...); A labels DERIVED/labels/17934b7b23b1 (manifest = current lab33.py 75d8aa43...,
  build_labels33.py 947c2b5e...); B features DERIVED/implB/features/345ba20d4f97; B labels DERIVED/implB/labels
  (code_sha12 efdde5c74ee1, built 15:15 PDT 10-27).

## 1. Dates and decision times chosen (why)
The 20 B3 dates (R-L5, recomputed: default_rng(20261028).choice(796, 20) over the sorted OOF list): 2021-01-19,
01-25, 03-11, 03-16, 04-01, 05-04, 07-06 (late open, excluded), 07-09, 07-29, 08-16 (release), 2022-06-03, 09-01,
09-29, 12-13 (after a roll, excluded), 12-22, 2023-01-11, 02-16, 04-10, 08-11 (release), 2024-02-15 (release).
- D1 = 2022-09-29, t1 = 10:30:00 CT (i = 115): no release, not excluded, limits 453.3/393.3 far from the mid
  (408.9), segment 30 contains at least the 19 previous trade dates (2022-09-01 is in it), so F1.3's 10-date OLS and
  the 20-date references lie inside one segment; 10:30 keeps every window clear of the 08:30 pause. Also t0 =
  08:40:00 (i = 5) for the open-time-axis window across 08:30 (F4.4: the mark t - 30 min is 07:25:00).
- D2 = 2021-08-16, 10:27:00 (i = 112): a mid-session burst (|B*| >= 3 at e = 10:25) for F4.11/F4.12 (D1 has none).
- D3 = 2023-08-11 (WASDE/Crop Production, R = 11:00 CT): F05 flags at 10:52, 10:53, 11:29, 11:30, 11:31.
- D4 = 2021-04-01 (LB-15: rule 5 removes 82 F05 minutes): limit test from my own as-of pass over the Z4
  definitions; flags at the first failing minute and the minute before it.
- D5 = 2022-12-13 (after a roll): every flag must be false.

## 2. Hand recomputation: features
Method (features_work.txt holds every intermediate): the state "as of u" is the one after the last F_LAST record
of the front with ts_recv <= u (both implementations commit there: feat33.py 190, replayB.py 41). Seasoned depth
from my own order-time dict (last A or M ts_recv <= t - 1.000 s) on the displayed book's first three levels.
sigma_ZM(D1) = population SD of the 1-minute mid changes between consecutive marks 08:35..13:13 of the 20 trade
dates before D1 (5,560 intervals): 3.463850368378 ticks (A's and B's _day: 3.4638503683783424). Trailing
references pooled over the 279 marks of the 20 dates (5,580 marks). F1.3: 10 dates in the segment, 2,757 samples
(NOPA 2022-09-15 removes 33 marks under the closed window), centred lstsq, a recovered from the means. The
open-time axis: both coders (FA-1 (B), B-OPEN-1 (a)) take 07:45:00 as the junction mark; my mapping gives the
same marks (08:40 - 30 min = 07:25:00) and the value matches, which confirms that reading on both sides.

| # | Date, time (i) | ID | Mine | A | B | Agree (A, B) |
|---|---|---|---|---|---|---|
| 1 | 2022-09-29 10:30 (115) | C.3 | 1.0 (spread 1 tick) | 1.0 | 1.0 | yes, yes |
| 2 | same | C.4 | 2.0794415416798357 (qb1 5, qa1 2) | 2.0794415416798357 | same | yes, yes |
| 3 | same | C.5 | -0.023905520853554366 (V15 1022, Vbar 1046.75 over 20 dates) | -0.023905520853554366 | same | yes, yes |
| 4 | same | C.6 | 1.2423807935715776 | 1.2423807935715776 | same | yes, yes |
| 5 | same | F1.1 | 0.8742031477820698 (C 182.825, mean_30 182.0478, sd_30 0.8890) | 0.8742031477818667 | 0.8742031477818817 | yes (2.3e-13 rel), yes |
| 6 | same | F1.3 | -2.0353261482575378 (a -72.7205, b_S 0.417572, b_L -1.62074, sd_e 26.9534 ticks, n 2757, rank 3) | -2.0353261482575378 | -2.0353261482574956 | yes (exact), yes (2e-14) |
| 7 | same | F2.8 | -0.5863259147922344 (OFI_S_1 -46 over 543 F_LAST updates; Obar_S_1 78.4546594982; identical with all 581 records) | -0.5863259147922344 | same | yes, yes |
| 8 | same | F3.1 | -0.8289926842993809 (OFI_ZM_1 -33 over 910 updates; Obar_ZM_1 39.8073476703) | -0.8289926842993809 | same | yes, yes |
| 9 | same | F3.2 | OFI_ZM_5 -195 over 3,079 updates; reading A: Obar_5 97.51362007168458 -> -1.9997206529370035; reading B: Obar_5 97.50931899641577 -> -1.9998088593682801 | -1.9997206529370035 | -1.9998088593682801 | A = reading A exactly; B = reading B exactly; A vs B 4.4e-5 rel (SF-1) |
| 10 | same | F3.7 | 0.3333333333333333 (seasoned 4 vs 2; displayed 5 vs 2) | 0.3333333333333333 | same | yes, yes |
| 11 | same | F3.8 | -0.09090909090909091 (seasoned 4+8+8 vs 2+10+12) | -0.09090909090909091 | same | yes, yes |
| 12 | same | F4.1 | -0.7217401833585598 (408.85 - 409.10) | -0.7217401833585598 | same | yes, yes |
| 13 | 2022-09-29 08:40 (5) | F4.4 | 0.052708450544453056 (M(08:40) 411.70, M(07:25) 411.60) | 0.052708450544453056 | same | yes, yes |
| 14 | 2021-08-16 10:27 (112) | F4.11 | -3.0968245103533545 (sigma 2.6258278299; B(e) largest at e = 10:25, j* = 2) | -3.0968245103533545 | same | yes, yes |
| 15 | same | F4.12 | -2.0758635483443566 (= DB exp(-2/5)) | -2.0758635483443566 | same | yes, yes |
| 16 | same | C.6 | 0.9653962101036038 | 0.9653962101036038 | same | yes, yes |

Counts (features): 16 values; agreeing with A 16/16 within G7 (15 bit-exact); agreeing with B 16/16 within G7 (14
bit-exact). Row 9: each implementation matches its own declared reading, and the two readings differ.

## 3. Hand recomputation: labels, flags, weights
Method (labels_work.txt): P3.3 from bid_1/ask_1 as of t + L and t + h + L (L = 1 s); P3.4 stepping through every
update in (t + L, t + L + h] in record order, skipping undefined mids, exact test S_u - S_0 >= 2b with S = bid + ask
in ticks; P3.6 rules 1-5 (closed release window; limit test 50(bid + ask) >= 99 HL - LL or <= 101 LL + HL with
HL/LL from the front's last definition record with ts_recv <= 08:30 CT, my own as-of pass; locked-book row rule
over [t, t + L + h] and, for TB, also over [t, max(t + L + h, tau + L)]); P3.7 c_m over clock minutes, strict
> 1 s, fsum/h over row_ok rows.

| # | Date, time (i) | Label | Mine (y, n_long, n_short, w, flags) | A | B | Agree |
|---|---|---|---|---|---|---|
| 1 | 2022-09-29 08:35 (0) | F15 | +1, 5.4719999999999995, -8.528, w 0.22121526621526622 (c_m 1..15), entry_ok, row_ok | same | same | yes, yes |
| 2 | 2022-09-29 08:36 (1) | F15 | +1, 1.472, -4.5280000000000005, w 0.15899304399304398 | same | same | yes, yes |
| 3 | 2022-09-29 10:30 (115) | F15 | +1, 6.4719999999999995, -10.528, w 1/15 | same | same | yes, yes |
| 4 | 2022-09-29 11:05 (150) | F15 | -1, -4.5280000000000005, 1.472, w 1/15 | same | same | yes, yes |
| 5 | 2022-09-29 12:57 (262) | F15 | 0, -2.528, -0.528, w 0.22121526621526622 (c_m 15..1) | same | same | yes, yes |
| 6 | 2022-09-29 09:27 (52) | T15 | -1 (tau_dn at 1664462040015360062), -18.528, 14.472, span_end tau + L | same | same | yes, yes |
| 7 | 2022-09-29 10:30 (115) | T15 | +1 (tau_up at 1664466133624395502), 11.472, -14.528 | same | same | yes, yes |
| 8 | 2022-09-29 10:31 (116) | T15 | +1, 11.472, -15.528 | same | same | yes, yes |
| 9 | 2022-09-29 11:06 (151) | T15 | 0 (vertical), -10.528, 7.4719999999999995 | same | same | yes, yes |
| 10 | 2023-08-11 10:52 (137) | F05 | +1, 3.472, -7.5280000000000005, w 0.45666666666666667, entry_ok, row_ok | same | same | yes, yes |
| 11 | 2023-08-11 11:31 (176) | F05 | -1, -17.528, 13.472, w 0.45666666666666667 | same | same | yes, yes |
| 12 | 2021-04-01 08:43 (8) | F05 | +1, 8.472, -12.528 (mid below HL - 0.02c = 420.92) | same | same | yes, yes |

Exclusion flags: 2023-08-11 F05 at 10:53 (span end 10:58:01 touches R - 2 min), 11:29, 11:30 (span starts at
R + 30 min; closed) -> entry_ok = row_ok = false in mine, A and B; rule 3 removes 38 minutes in all three.
2021-04-01 F05 at 08:44 (i = 9): the limit part fails (HL 429.0, LL 379.0 from the definition record at
2021-04-01 00:00 UTC; cal33.limits agrees) -> all false in mine, A, B; 82 minutes fail in all three (= LB-15).
2022-12-13 (after a roll): A and B both have 0 entry_ok and 0 row_ok rows in F15.
Whole-date equality checks (counts only): F15 2022-09-29 entry_ok 263/263, row_ok 263/263, (y, n_long, n_short)
263/263, w 263/263 against both A and B; T15 2022-09-29 (y, n_long, n_short, span_end) 263/263 against both (the
union and possible TB spans give the same locked-book result on all 263 rows); F05 2021-04-01 entry_ok 273/273
against both. A's mid_move equals (S(t + L + h) - S(t + L))/2 at the checked rows (7.0, 3.0, 8.5, -3.0, -1.0 ticks).

Counts (labels): the 12 rows agree with A 12/12 and with B 12/12 exactly; the 5 flag minutes 5/5 with both; the
weights (rows 1, 2, 3, 5, 10, 11) agree exactly with both.

## 4. B5 threshold arithmetic (b5_arith.py: own formulas, no import of p7_final or funnel)
E[max SR] = sqrt(V) ((1 - g) Z^-1(1 - 1/N) + g Z^-1(1 - 1/(N e))), DSR by bisection on (SR - SR0) sqrt(T - 1) /
sqrt(1 - skew SR + (kurt - 1)/4 SR^2) = 1.6449, se(SR) = sqrt((1 + SR^2/2)/(T - 1)).
| Quantity | Mine | Protocol / p7_final_budget300.md | Agree |
|---|---|---|---|
| SR0 multiplier at N 838 | 3.2045 | 3.2045 (P7.2 V14 c) | yes |
| SR0 discovery (V = 1/795) | 0.113653 | 0.1137 | yes |
| G3 normal | 0.172422 (t 4.865, ann 2.737) | 0.1724 (4.86, 2.74) | yes |
| G3 skew -0.5, kurt 6 | 0.175564 | 0.1756 | yes |
| t > 3.0 on 870 | 0.101710 | 0.1017 | yes |
| test DSR bar (V = 1/869) = b_test | 0.164882 (t 4.863, ann 2.617) | 0.164882 / 0.1649 (4.86, 2.62) | yes |
| G4 | 0.200703 (t 5.663, ann 3.186) | 0.2007 (5.66, 3.19) | yes |
| G4 if the test DSR is dropped | 0.137343 | 0.1373 | yes |
| 80% test power true Sharpe | 0.193698 | 0.1936 | yes |
| P(select) x P(pass) at s = 0.15, 0.17, 0.20, 0.25 | 0.0257, 0.1091, 0.4170, 0.9083 (select 0.0776, 0.1950, 0.4922, 0.9145) | 0.026, 0.109, 0.417, 0.908 (0.078, 0.195, 0.492, 0.914) | yes |
| per-trade ticks: h5 n4/n8, h15 n4/n8, h30 n4, h60 n2 | 0.707/0.500, 1.224/0.866, 1.731, 3.463 | 0.71/0.50, 1.22/0.87, 1.73, 3.46 | yes |
| P(>= 2 of 20 at 0.05) | 0.2642 | 0.26 | yes |
| P(>= 14 of 20 at 0.8) | 0.9133 | 0.91 | yes |
| 300 P(Z > 5.66); 300 P(Z > 4.86) | 2.27e-6 (2.24e-6 at the exact z 5.6625); 1.76e-4 (1.72e-4 at 4.8646) | about 2e-6; about 2e-4 | yes |
| 1/sqrt(796) | 0.035444 | 0.0354 | yes |
| reference z: Bonf/Holm 300, Bonf 838, BY 300 (c 6.283), Holm K9 m1/m2/m3, HLZ | 3.588, 3.847, 4.042, 2.539/2.773/2.902, 3.000 | same | yes |
| V14 (c) multipliers: one null companion, two | 1.602, 1.511 | 1.60, 1.51 | yes |

Plant calibration (ProofCoder_calibration.json vs synth33.py; oracle_check.py on check seed 80001):
- Generator moments re-derived by hand from make_path: Delta = X(B_{i+h}) - X(B_i) | z_i ~ N(beta g z_i,
  sigma_D^2 h + beta^2 vz) with c = (59/60, 1, ..., 1, 1/60), g = 5.226161, vz = 75.803173 (drift_moments agrees);
  the fractional-part/spread case analysis of fh_class_probs re-derived (k_up = a_e + 1 or + 1.5, k_dn = b_e - 1 or
  - 1.5) and recomputed by a midpoint integral (400 points per half): max |difference| 2.5e-10 over 209k rows.
- Empirical calibration (synthetic labels, deciles of p_up and p_dn, 19k rows each): model mean vs empirical share
  within 0.014 everywhere (overlapping 15-minute spans make the effective n about 1/15 of the row count).
- Own class means and own P3.8 simulation (one position, cap 20, next decision at i + h + 1): 8,532 trades,
  Sharpe 0.339510 = synth33.oracle_fh 0.339510 = check_values[0] 0.339510.
- Precision: bisection to 5e-4 in beta, slope dSR/dbeta 1.010, calib_se 0.0048 -> se(beta) about 0.0047; beta
  rounded to 0.367; calibration mean 0.3498 (se 0.0048, 60 draws), fresh-draw check mean 0.3486 (se 0.0045), i.e.
  0.31 se below the 0.35 target. Adequate for a 0.35 anchor.

## 5. Findings by grade
BLOCKING: none.

SHOULD FIX
- SF-1 (reading divergence, B3 cannot pass on four columns until decided): the OFI term e_n whose previous or
  current book state is two-sided but not a valid book (the crossed/locked pre-open state at the first update
  after 08:30). A (FA-6; feat33.py 538, 587-589) computes the term when both states are two-sided and not bad and
  makes a window with a non-computable term invalid (and drops that mark from the reference); B (B-OFI-1; dayB.py
  56) sets such terms to 0. Measured on D1: Obar_ZM_5 97.51362007168458 (A) vs 97.50931899641577 (B), 4.4e-5
  relative, so every F3.2, F3.3, F2.9, F2.11 row of every date differs by about that much (B3 counts: 5,140,
  5,390, 5,415, 5,398 rows of 5,460), far above G7's 1e-9; rows 08:35-08:39 (k = 5) and 08:35-08:49 (k = 15) also
  differ directly. Which side matches the protocol: A. F2.8's e_n is defined from the prices and quantities of
  consecutive book updates; 0.3 restricts only the mid M to valid books; G3 names an "empty book side" (not a
  crossed or locked book) as a cause of invalidity and says a feature that "cannot be computed" takes 0 (the
  feature, not a term). B's zeroing is an imputation the text does not state. Decision for the lead; if A's reading
  is adopted, B changes the term rule in dayB.py and rebuilds the 20 dates.

NOTE
- N-1 (not recomputed here; for the lead's B3 harmonisation): the other A-B feature disagreements over the 20
  dates are F3_11 (5,426 rows, nearly every row: the refill definition or rbar_15), F3_9 (725 rows, about 40 a
  date: which records count as touch removals), F3_10 (1,022 rows on 5 dates: sbar_5), F3_12 (1,694 rows on 7
  dates: the lam60 reference median), and C_5/F2_8/F2_10/F3_1 (298/1,341/2,123/1,077 rows) only on dates whose
  20-date history holds an early-close date (2020-12-24, 2022-11-25): the early-close reading (B-EARLY-1 vs A).
  2021-07-06 (scheduled late open) differs in its own rows of F1_2, F1_1, F1_4, F1_6, F4_5 and others (B-LATE-1).
- N-2: P4.2's "per-seed power of 0.8" is an assumption, not arithmetic: at the selection threshold alone,
  P(SR_d >= 0.2007) = 0.8 needs a realised daily Sharpe of 0.231 (Tier A has further gates), against an oracle of
  0.35 (SD 0.037 across draws). ProofCoder's probe seed 9101 (fitted S5F15 0.336 and 0.417 vs oracle 0.369) supports
  it. The binomial 0.9133 is exact given 0.8.
- N-3: B's label tables (built 15:15) have no `mid_move` column (INTERFACE 4.2 added it at 15:20; reported-only,
  never used by P8). The B3 schema comparison should expect this or LabelCoder2 should add it.
- N-4 (data observation, no action): 17% of the ZM front's F_LAST events contain records with more than one
  ts_recv (76,988 of 446,490 on 2022-09-29). Both implementations commit at F_LAST records, which is the protocol's
  as-of state; any check that reads the live book at u (as my first probe did) is wrong and was corrected.
- N-5: T15's locked-book row rule: A's union span (TB-SPAN (c)) and the possible span give identical results on all
  263 rows of D1; the reading cannot be told apart on this date.
- N-6: the rounded P4.2 rates "about 2e-6" and "about 2e-4" are 2.27e-6 and 1.76e-4 at the quoted z values
  (2.24e-6 and 1.72e-4 at the exact G4/G3 z); consistent.

## 6. Not done / limits
- F3.9, F3.10, F3.11, F3.12, F1.5, F1.7, F2.7, F4.6-F4.10 and the C.7-C.10, C.15 calendar flags were not
  recomputed (outside the 10-feature scope); the A-B differences there are listed in N-1 without adjudication.
- TB weights (P3.7 on realised spans) were not recomputed; A and B agree with each other at the checked T15 rows.
- Labels on dates with a one-sided or bad book inside a span (rule 5 row part) did not occur on D1, D3, D4; that
  branch is untested by hand.
