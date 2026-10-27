# Recheck_W3: FixVerifierDofB-FableXHigh, items DO-12..DO-22 and the P4 hunks of protocol v0.3

Label: FixVerifierDofB-FableXHigh (independent re-checker; did not write the protocol or its fixes).
Date: 2026-10-27 (PDT).

Inputs read (by section, grep and line ranges only; no market data opened):
- reports/stage_e32_discovery_protocol.md, DRAFT v0.3, 738 lines,
  sha256 330c4af7379791e3957f13818e31b9900adac722e465030a77925e99fc587e1f (verified at the start), mtime
  2026-10-27 08:01:53 PDT.
- reports/stage_e32_briefs/work/lead/protocol_v0.2.md (647 lines) through `diff` against v0.3 (32 hunks in all).
- reports/stage_e32_briefs/review/ProtocolReview_dof.md: findings table rows and sections DO-12..DO-22, DO-6,
  DO-11; ProtocolReview_feasibility.md FE-2, FE-7, FE-8, FE-9, FE-10; ProtocolReview_leakage.md LE-2, LE-4, LE-5;
  ProtocolReview_arithmetic.md AR-2, AR-5.
- reports/stage_e32_STATE.md lines 356-367 only.
- docs/prompts/STAGE_E.33.md (grep and lines 40-50, 93-135, 148-190) and its git history
  (`git log -- docs/prompts/STAGE_E.33.md`, `git show 3a75f3b`).
- Code, read-only: screening/stage_e_verdict.py 170-230 (moments, t_stat, dsr_table);
  funnel/multiple_comparisons.py harvey_liu_zhu_verdict (t = mean / (stdev / sqrt(n))).
- Own recomputation: reports/stage_e32_briefs/review/recheck/work_W3/recompute.py (binomials, normal tails, fit
  counts, terciles, fold sizes, feature counts, clip counts, proofs' compute from P5's per-fit figures, the
  DO-15 interval arithmetic). Its output is quoted below where a number is checked.

Severity scale used for new findings: as the brief defines it (BLOCKING / SHOULD FIX / NOTE).

## 1. Per-item verdicts (DO-12..DO-22)

| ID | Verdict | v0.3 lines | Evidence (verbatim, current text) | Proposed fix if not CORRECT |
|---|---|---|---|---|
| DO-12 | CORRECT | 67-71 (convention); 54, 356-357, 393, 397, 429, 432, 556, 666 (uses) | "Statistics conventions (ProtocolReview DO-12, FE-9, FE-10): every SD in a feature, a normaliser or a fit is the population SD (ddof 0); a weighted mean and SD are m = sum w x / sum w and sqrt(sum w (x - m)^2 / sum w); an OLS fit is numpy.linalg.lstsq on centred regressors with an intercept, and its residual SD is sqrt(SSR / n). Statistics of daily series (mean, SD, Sharpe, skewness, raw kurtosis, t) are those of screening/stage_e_verdict.py moments() and t_stat() (population SD; Sharpe = mean / pstdev)." | None required. The one global sentence covers sigma_X(D), sd_30, sd_e, sd_g, sd_gap, RV15, G5's weighted SD, P6.2 and G5(c), as the finding asked. moments() verified: statistics.pstdev, third and fourth moments divided by n, sharpe = mean / sd; t_stat() calls harvey_liu_zhu_verdict, t = mean / (sd / sqrt(n)). See R-W3-8 (G3 says "sample skewness") and R-W3-13 (F1.3's intercept scale), found under cross-check (d). |
| DO-13 | CORRECT | 422; 68-69 | "lam60 = the OLS slope (with an intercept; 0.3) of dM_ZM (ticks) on signed volume (B - S, contracts) over those of the 60 one-minute intervals ending at t that contain trades, divided by the trailing 20-date reference median of the same slope; invalid with fewer than 30 such intervals (ProtocolReview DO-13)" | None. Intercept stated, trade-bearing intervals only, solver pinned by 0.3 (lstsq, centred regressors). |
| DO-14 | CORRECT | 667-668 | "(d) mean daily net > 0 within each tercile of sigma_ZM(D): the 796 OOF dates sorted by sigma_ZM(D) ascending (ties by date), ranks 1-265, 266-530 and 531-796 (ProtocolReview DO-14; sigma_ZM(D) is known before D opens)." | None. Recomputed: 265 + 265 + 266 = 796; the reviewer's exact cut points. Zeros are in the series by P3.8 (X_D = 0 on dates with no trade), so "mean daily net" includes them. |
| DO-15 | PARTIAL | 322-325 | "c_m = the number of rows of the same label type and date whose span intersects m by more than one second (so an FH span of h minutes plus L covers h intervals; ProtocolReview DO-15; for TB the realised span [t, tau + L]); u_i = the mean over the intervals m covered by span_i of 1/c_m." | c_m carries the reviewer's criterion and the FH arithmetic holds (recomputed: a span [t, t + 15 min + 1.000 s] from a minute mark intersects 15 intervals by more than 1 s and the 16th by exactly 1.000 s, which "more than one second" excludes). But u_i says "covered by span_i", a second criterion. For FH rows the two agree; for a TB row whose tau + L falls inside a minute the sets differ (recomputed: a span ending 7 min 30 s after t fully covers 7 intervals and intersects 8 by more than 1 s), so u_i has two readings for every TB row and G7 agreement can fail on it. Replace l.325 "u_i = the mean over the intervals m covered by span_i of 1/c_m" with "u_i = the mean of 1/c_m over the intervals m that span_i intersects by more than one second (the same intervals that count span_i in c_m)". |
| DO-16 | CORRECT | 419 | "CR5 = (Ca_5 - Cb_5)/(Ca_5 + Cb_5): contracts removed from the price level that was the best ask (Ca) or best bid (Cb) just before the record, by cancels, size-reducing modifies (the reduction) and modifies to another price (the full size), in the 5-minute window; fills are not removals (ProtocolReview DO-16); invalid if the denominator is 0" | None. All three removal kinds and the fills exclusion are stated; "just before the record" is the reviewer's "when the record arrived". |
| DO-17 | CORRECT | 507; 450-451 | P5: "LightGBM's feature bins are built from the inner-training rows only (DO-17)." LT3: "that LightGBM's feature bins come from the inner-training rows only (the inner-validation set is built with reference= the training Dataset; ProtocolReview DO-17)" | None required. The evaluation fold needs no reference= (booster.predict on raw arrays uses the model's stored bins), so leaving it out is not a gap. Wording NOTE R-W3-12: "the training Dataset" should read "the inner-training Dataset", since the sentence before it distinguishes the two. |
| DO-18 | PARTIAL | 533-535; 724-725 | P5: "before the first real-outcome fit, E.33 times the feature builder on 3 dates and one fold of the two slowest grid points (E33-S5F15L100E and E33-S5F15G3050), writes the projected total to its STATE file, and that projection is the reference for P10's 3x stop." P10: "measured compute above 3 times the probe-based projection written to the STATE file before the first real-outcome fit (P5), or two out-of-memory failures." | The base is now fixed before outcomes (the finding's point). Missing: the unit. "projected total" and "measured compute" can each be wall time or CPU time, and under 7 worker processes the two differ by a factor of up to 7, so the stop fires at two different points. The reviewer's text also asked that the STATE entry name the probe times and the formula. Replace l.534-535 "writes the projected total to its STATE file, and that projection is the reference for P10's 3x stop" with "writes the projected wall time of the 1,800 fits to its STATE file (the probe times and the extrapolation formula with it), and that projection is the reference for P10's 3x stop"; replace l.724 "measured compute above 3 times" with "measured wall time of the search above 3 times". |
| DO-19 | WRONG | 726-729 | "E.33's deadlines (its prompt: the search is cut at 00:00 PDT on 2026-10-28 and work stops at 01:00): the cut unit is a whole feature set in the P5 order (S5, S1, S3, S2, S4), which is the "family" of the prompt's C3 (ProtocolReview DO-19); unrun configurations stay registered and count in N, and P8 runs on the configurations that ran, with the registered N." | The cut unit (feature set = C3's "family") resolves the finding's second half. The times are now wrong against the source of truth: docs/prompts/STAGE_E.33.md was changed after v0.3 (v0.3 mtime 08:01:53; commits 864574b 08:12 "no fixed end", then 3a75f3b 08:16 "hard deadline 09:00"). The prompt now reads (l.43-46) "Hard deadline (user, 2026-10-27 08:16): work stops at 08:00 PDT on 2026-10-28; the return is written by 08:45; nothing runs after 09:00" and C3 (l.161-164) "If the full budget cannot finish by 07:00 PDT on 2026-10-28, finish whole families." Since "This document" binds (0.1) and E.33 runs it unchanged, an E.33 lead following l.726 cuts the search at 00:00, seven hours before the prompt's cut, and P8 sees a smaller subset. Replace l.726 "(its prompt: the search is cut at 00:00 PDT on 2026-10-28 and work stops at 01:00)" with "(its prompt, user 2026-10-27 08:16: no new configuration starts after 07:00 PDT on 2026-10-28; running ones finish or are recorded as failed by 08:00; the return is written by 08:45; nothing runs after 09:00)". Whether the protocol should instead defer to the prompt's times by reference (so a later user change does not stale it again) is the lead's call; one pair of times must be written. |
| DO-20 | CORRECT | 651-654 | "G1-G5, the ranking and the walks below are the whole selection rule: the per-firm nets, FDR, PBO and session or robustness splits that E.33's prompt (D1-D2) asks for are reports, never gates (ProtocolReview DO-20). A failed configuration (P5) fails G1." | None required. The route is a compressed equivalent of the reviewer's mapping (per-firm nets = P6.4, FDR/Holm = P7.2 references, PBO = P6.3); P7.2 l.635-636 separately says "None is a gate". The trade counts, DSR at N and no-month-dominating items of D1 are G1, G3 and G5(b). Wording only: "session ... splits" are void (P1.3: one session). |
| DO-21 | CORRECT | 465-469, 471-472, 478-479 | "Seeds 1-20 for null searches and 101-120 for planted searches, each run exactly once (no reruns; 4,800 fits in all)." "The proof fails if Tier A is non-empty in 2 or more of the 20 null searches (P(at least 2 of 20) = 0.26 at a true rate of 0.05)." "The proof passes if at least one S5 configuration at FH15 or TB30 enters Tier A in at least 14 of the 20 planted seeds (P(at least 14 of 20) = 0.91 at a per-seed power of 0.8; ...)" | None for the finding as stated: the seed sets are exact, reruns are forbidden, "2 or more of 20" is the reviewer's "more than 1 of 20", and since the searched subset is exactly S5 x {FH15, TB30} the pass criterion is well defined (it reduces to "Tier A non-empty"). Recomputed: P(>= 2 of 20 at 0.05) = 0.2642; P(>= 14 of 20 at 0.80) = 0.9133. Gaps the new text opens are reported as R-W3-2 (no compute estimate), R-W3-3 (date count implicit), R-W3-4 (oracle undefined), R-W3-5 ("no reruns" against a fixable failure), R-W3-9 and R-W3-10 (two small numbers). |
| DO-22 | CORRECT | 511-513; 654; 489-490 | "A configuration with any fold whose fit raises an error, or yields probabilities that are not finite, is failed: it has no OOF series, fails G1, is recorded with the error, and stays in N." P8: "A failed configuration (P5) fails G1." LOGIT: "Non-convergence is logged and the fit is used as is." | None for the finding as stated (failed, no series, fails G1, stays in N; non-convergence is not a failure; 0.2 forbids refitting with changed settings). The remaining two-way reading, a fold killed rather than erroring (out-of-memory kill, reboot, usage-limit pause), is R-W3-7. |

Counts: 11 items; CORRECT 8 (DO-12, 13, 14, 16, 17, 20, 21, 22), PARTIAL 2 (DO-15, DO-18), WRONG 1 (DO-19), MISSING 0.

## 2. Hunk map, P4 (v0.3 lines 340-481)

The diff lists seven hunks inside P4; every one maps to at least one item. No HUNK- entries.

| v0.2 lines -> v0.3 lines | Item ID(s) | Check |
|---|---|---|
| 318-319 -> 353-355 (G4 clip lists) | DO-11 | Counted: clipped 1 + 4 + 3 + 11 + 4 + 3 + 5 + 7 = 38; not clipped 4 + 10 + 1 + 5 + 1 = 21; 38 + 21 = 59. Matches the reviewer's lists. |
| 342 -> 378 (C.7 definition record) | LE-2, FE-8 | "from its last definition record with ts_recv <= 08:30:00 CT on D" agrees with P3.6 rule 5 at l.314 (same as-of rule) and with FE-8's "C.7 uses the expiration of the same record". |
| 383 -> 419 (F3.9 CR5) | DO-16 | See the item table. |
| 386 -> 422 (F3.12 lam60) | DO-13 (+ FE-10's "0.3" pointer) | See the item table. |
| 405-406 -> 441-445 (LT1 all streams; LT7) | LE-5 | LT1 now names ZM MBO, ZS/ZL MBP-1 and the definitions. LT7 is defined (decision from streams truncated at t; fill from streams truncated at t + L), stricter than LE-5's proposal (decision at t + L). Timing gap reported as R-W3-6; ordering as R-W3-14. |
| 410-411 -> 449-452 (LT3) | DO-17 (bins), LE-5 (weights of own date), LE-4 / AR-5 (embargo 21, look-backs) | Bins: see DO-17. Embargo 21 agrees with P6.1 l.546-548 (21 dates; 642/642/642/642/643/664). "each row's weight depends only on rows of its own date" is LE-5's LT3 addition and agrees with P3.7 l.325-326. |
| 418-427 -> 459-480 (P4.2 rewritten) | FE-2, FE-7, DO-21 | Numbers recomputed (cross-check b). FE-2's cost line ("4,800 fits, about 1.6-3.3 h of wall time") and its "796 OOF dates and the real exclusion calendar" were not carried into v0.3 (R-W3-2, R-W3-3); FE-7's oracle definition ("the P3.5 rule applied with the true class probabilities") became "it knows the planted signal exactly" (R-W3-4). |

hunks_mapped = 7, hunks_unmapped = 0.

## 3. Cross-checks

### (a) LT1..LT7
- Every LT reference in the protocol is in P4.1 (l.440-457): LT1 l.440, LT7 l.443, LT2 l.446, LT3 l.448, LT4 l.453,
  LT5 l.455 (which refers to "LT1-LT2"), LT6 l.457. Each number is defined exactly once; no reference elsewhere
  uses a different number or scope (P10 l.723 refers to "P4.1, P4.2" as wholes).
- LT7 (simulator causality) is defined at l.443-445.
- docs/prompts/STAGE_E.33.md contains no "LT" numbering (grep: none); its B4 (i)-(iv) are mapped in the protocol
  as LT1 = B4 i, LT2 = B4 ii, LT3 = B4 iii, LT5 = B4 iv; LT4, LT6 and LT7 are protocol additions. The prompt's "must
  pass before any model is fitted" matches P4.1's heading "before any model is fitted on real outcomes".
- Disagreements: none in numbering. Two findings on content and order: R-W3-6 (LT7 needs a fitted model, which the
  heading forbids before real outcomes) and R-W3-14 (LT7 listed between LT1 and LT2).

### (b) P4.2 synthetic proofs
Every element has exactly one mention and they agree with each other: subset S5 x {FH15, TB30} x 10 grid points
(l.465), seeds 1-20 null and 101-120 planted (l.468), oracle SR 0.35 (l.476-477), pass >= 14 of 20 (l.478-479),
null fails at >= 2 of 20 (l.471). Recomputed (work_W3/recompute.py):
- 1 x 2 x 10 = 20 configurations; x 6 folds = 120 fits a search; 40 searches = 4,800 fits; 40 full searches =
  40 x 1,800 = 72,000 ("about 40 times the search"): all as stated.
- P(>= 2 of 20 | 0.05) = 0.2642 (stated 0.26); P(>= 14 of 20 | 0.80) = 0.9133 (stated 0.91).
- 300 x P(Z > 5.66) = 2.27e-6 (stated "about 2e-6"); 300 x P(Z > 4.86) = 1.76e-4 (stated "about 2e-4");
  t = 0.1724 sqrt(796) = 4.864 and 0.2007 sqrt(796) = 5.662 (P7.2's 4.86 and 5.66).
- 20 x 20 = 400 null Sharpes as stated; 1/sqrt(796) = 0.03544, which rounds to 0.0354, not the stated 0.0355
  (R-W3-9, NOTE).
- "P7.2 gives a selection power of 0.91 at a realised daily Sharpe of 0.25" (l.479-480): P7.2 l.639-641 gives
  0.91 at 0.25 as the joint probability "selected and then passes". Selection alone at s = 0.25 under normal
  days (threshold 0.2007, se = sqrt((1 + s^2/2)/796)) is 0.915, so the figure holds but the citation is loose
  (R-W3-10, NOTE).
- Compute: P4.2 states no compute for the proofs and P5's estimate (l.521-541) covers only the 1,800 real fits. From
  P5's own per-fit figures the proofs are 2,880 LOGIT + 1,920 LGBM fits on production-size tables (the proofs apply
  G1-G5 with the production thresholds, so the tables carry 796 OOF dates): 10.7-64 CPU-h at P5's guesses (1.5-9.1 h
  of wall time at 7 workers), 6.2-9.7 CPU-h at the FeasibilityReviewer's balanced probes (0.9-1.4 h wall), up to
  59 CPU-h in the 99%-class-0 regime. That is 2.67 times the real search's fits, run before the freeze and the
  first real-outcome fit, and it is absent from the deadline arithmetic (R-W3-2, SHOULD FIX). The date count that
  makes the production thresholds applicable is only implicit (R-W3-3).

### (c) Feature counts
Counted from the per-family tables: C.1-C.15 = 15 (C.11-C.14 are four flags); F1.1-F1.8 = 8; F2: 3 + 3 + 1 + 2 + 2
= 11; F3: 3 + 1 + 2 + 1 + 1 + 1 + 1 + 1 + 1 = 12; F4: 5 + 8 = 13. Sums: S1 = 23, S2 = 26, S3 = 27, S4 = 28, S5 = 59.
Every stated count agrees: l.369/385/400/409/424 headings; l.437 "C 15, F1 8, F2 11, F3 12, F4 13; S1 23, S2 26, S3
27, S4 28, S5 59"; l.165-166 set definitions; P5 l.526 "59 features (S5)"; P4.2 l.466 "the 59 S5 feature columns";
P6.5 l.594 "59 x 6 = 354"; G4 l.353-355 38 + 21 = 59. P5 l.526 "263 rows a date x 796 dates = 209,000" is the FH15
grid (263 x 796 = 209,348). No disagreement.

### (d) SD and OLS conventions (DO-12, DO-13, FE-9, FE-10)
- Stated once: 0.3 l.67-71 (population SD ddof 0; weighted mean and SD; lstsq on centred regressors with an
  intercept; residual SD sqrt(SSR / n); daily-series statistics per moments() and t_stat()). Code checked:
  moments() uses statistics.pstdev and divides the third and fourth central moments by n; t_stat() returns
  harvey_liu_zhu_verdict's t = mean / (stdev / sqrt(n)); dsr_table uses statistics.pvariance (P9 l.703 "population
  variance" agrees).
- Formulas with an explicit pointer: F3.12 l.422 "(with an intercept; 0.3)"; P6.2 l.556-557 "population SD ...
  exactly as screening/stage_e_verdict.py moments() and t_stat()".
- Formulas that rely on the global sentence without a pointer (consistent, since 0.3 says "every SD in a feature, a
  normaliser or a fit"): sigma_X(D) l.54, G5 l.356 (weighted mean and SD), F1.3 l.393 (OLS and sd_e), F1.7 l.397,
  F4.7 l.429, F4.10 l.432, G4 l.662 (g3, g4 "from the configuration's moments"), G5(c) l.666.
- Disagreements: G3 l.660-661 "the configuration's own sample skewness and raw kurtosis": "sample skewness" names
  the bias-corrected estimator, which is not what moments() computes and not what P6.2 says feeds G3 (R-W3-8,
  SHOULD FIX, wording that an implementer can read two ways in the fourth decimal of DSR). G5(c) l.666 "(mean/SD x
  sqrt(n))" has no pointer (R-W3-11, NOTE). F1.3's intercept a is used on the natural scale while 0.3 fits on
  centred regressors (R-W3-13, NOTE).

## 4. New findings

| ID | Severity | v0.3 lines | Finding | Proposed fix |
|---|---|---|---|---|
| R-W3-1 | SHOULD FIX | 726-729 | P10's deadlines ("cut at 00:00 PDT on 2026-10-28 and work stops at 01:00") were right against the 22:41 prompt (dcbcd2f) but the prompt was changed at 08:12 (864574b) and 08:16 (3a75f3b), after v0.3 (08:01:53): C3 now cuts at 07:00 PDT, work stops at 08:00, the return is written by 08:45, nothing runs after 09:00. The protocol binds and runs unchanged, so an E.33 lead following l.726 cuts the search seven hours early and P8 runs on a smaller subset; a lead following the prompt breaks l.726. Two readings, different subsets. | Replace l.726's parenthesis with "(its prompt, user 2026-10-27 08:16: no new configuration starts after 07:00 PDT on 2026-10-28; running ones finish or are recorded as failed by 08:00; the return is written by 08:45; nothing runs after 09:00)". Lead's decision whether to cite the prompt's times by reference instead. |
| R-W3-2 | SHOULD FIX | 465-469; 521-541 | No compute estimate exists for the synthetic search proofs. 4,800 production-size fits (2,880 LOGIT, 1,920 LGBM; the proofs apply G1-G5 at production thresholds, so the tables carry the 796 OOF dates) are 2.67 times the real search's fits: 10.7-64 CPU-h at P5's per-fit guesses (1.5-9.1 h wall at 7 workers), 6.2-9.7 CPU-h at the FeasibilityReviewer's balanced probes (0.9-1.4 h wall), up to 59 CPU-h in the 99%-class-0 regime. They run before the freeze and the first real-outcome fit, inside the same day as the search, and neither P5's estimate nor P10's deadline clause counts them. FE-2's cost line was dropped when its scale was adopted. | Add to P5's compute estimate after l.531: "- Synthetic search proofs (P4.2): 4,800 fits (2,880 LOGIT, 1,920 LGBM) on production-size tables, 2.67 times the search's fits: 11-64 CPU-h at the guesses above (1.5-9 h wall at 7 workers), 6-10 CPU-h at the FeasibilityReviewer's balanced probes (0.9-1.4 h wall). They run before the freeze; the P5 probe times are taken from them, and the deadline clause of P10 counts them." |
| R-W3-3 | SHOULD FIX | 465-468 | The search proofs' date count and calendar are not declared; they are implied only by "1/sqrt(796)" at l.475 and by "G1-G5 with the production thresholds". G1 (at least 796 trades, a trade on 50% of OOF dates), G5(a) 13 quarters, G5(b) 25% of a month, G5(c) 39 months and G5(d) ranks 1-265 are only computable on the 796 OOF dates of the real calendar. An implementer who generates 30 synthetic dates (the record-level stream's count at l.462) makes every null search pass vacuously (G1 fails everything) and every planted search fail. FE-2's "the 796 OOF dates and the real exclusion calendar" was dropped. | Replace l.465-467 "run from synthetic minute rows (mids, touch prices, labels and the 59 S5 feature columns generated to match the data facts' rates)" with "run from synthetic minute rows on the real decision grid G_h(D), the 796 OOF dates and the P3.6 exclusion calendar (the 20 burn-in dates as history; mids, touch prices, labels and the 59 S5 feature columns generated to match the data facts' rates)". |
| R-W3-4 | SHOULD FIX | 476-479 | The oracle is "it knows the planted signal exactly" with no trade rule and no label type: the plant's size (SR 0.35) depends on whether the oracle holds 15 minutes (FH15) or to the TB30 barriers, and on how it trades the signal. E.33 can size the plant two ways with different realised power, before outcomes but with the proof gating the whole stage (P10). FE-7's definition (the P3.5 rule with the true class probabilities) was not carried over. | Replace l.476-477 "one F3 feature carries a signal whose oracle strategy (it knows the planted signal exactly) has a daily Sharpe of 0.35 net under the selection variant" with "one F3 feature carries a signal; its size is the one at which the P3.5 rule applied with the true class probabilities (the oracle) gives a daily Sharpe of 0.35 net under the selection variant at FH15 on the synthetic series (about 2.1 ticks net per trade at 4 trades a date); the same plant is used for the TB30 configurations". Lead's choice of the sizing label type; one must be written. |
| R-W3-5 | SHOULD FIX | 468-469 against 723 | "each run exactly once (no reruns; 4,800 fits in all)" forbids every rerun, but P10 l.723 stops only on "a leakage or synthetic-proof failure ... that cannot be fixed without changing a declared choice", so a failure fixed by a logged code fix (0.2) must be shown fixed by running the proofs again. As written an implementer either refuses the rerun (and the stage stops on a fixed bug) or reruns against the text. The finding's intent (no fishing for a pass) needs the rerun pinned to the same seeds and reported. | Replace l.468-469 "each run exactly once (no reruns; 4,800 fits in all)" with "each run exactly once per pipeline hash (4,800 fits); after a logged code fix (0.2) all 40 are rerun with the same seeds, every run before and after the fix is reported, and no seed is added, replaced or rerun on its own". |
| R-W3-6 | SHOULD FIX | 443-445 with the heading at 439 | LT7 compares a recomputed entry decision with "the production decision", which under P3.5 needs a fitted model's class probabilities and the mu_k of a training fold. The heading requires every P4.1 test "before any model is fitted on real outcomes", so at that time no production decision exists. LE-5's proposal named "20 configurations", which implies real fitted ones. Two resolutions (a stub or synthetic model before the fits; real configurations after them) test different things and one of them is after outcomes. | Add to l.445: "LT7 runs before the first real-outcome fit on the fitted models of one P4.2 null search (seed 1), and is repeated on the Tier A and Tier B configurations after the test list is hashed; a mismatch at either time stops E.33 (P10)." Lead's decision which model LT7 uses; one must be written. |
| R-W3-7 | SHOULD FIX | 511-513 | "any fold whose fit raises an error" does not cover a fold killed before it writes a result (an out-of-memory kill, a reboot, a usage-limit pause). E.33 C3 resumes interrupted configurations from DONE markers (a rerun), P10 l.725 tolerates one out-of-memory failure before stopping, and nothing says whether a once-killed configuration is rerun with identical settings or failed. The choice is made when the kill is seen, possibly after other configurations' outcomes: the DO-22 mechanism again. | Add after l.513: "A fold interrupted before it writes its result (a killed process, an out-of-memory kill, a reboot, a usage-limit pause) is not failed: it is rerun once from the DONE markers with identical settings (E.33 C3); a second interruption of the same fold fails the configuration. Every out-of-memory kill counts toward P10's two-failure stop." Lead's decision between rerun-once and fail; one must be written. |
| R-W3-8 | SHOULD FIX | 660-661 | G3: "the configuration's own sample skewness and raw kurtosis". "Sample skewness" names the bias-corrected estimator (scipy.stats.skew bias=False), while 0.3 l.70-71 and P6.2 l.556-557 say the moments are moments()' population form (divisor n, pstdev). The two differ by order 1/n relative, which moves G3's DSR in the fourth decimal and can flip a configuration at the margin; a careful implementer can read it either way. | Replace "the configuration's own sample skewness and raw kurtosis" with "the configuration's own skewness and raw kurtosis (moments(), 0.3)". |
| R-W3-9 | NOTE | 475 | "1/sqrt(796) = 0.0355": 1/sqrt(796) = 0.035444, which rounds to 0.0354. A reported comparison value, not a gate. | Replace "0.0355" with "0.0354". |
| R-W3-10 | NOTE | 479-480 | "P7.2 gives a selection power of 0.91 at a realised daily Sharpe of 0.25": P7.2 l.639-641 states 0.91 at 0.25 as the joint "selected and then passes" probability. Selection alone at 0.25 is 0.915 under normal days, so the number holds; the attribution does not. | Replace with "(P7.2's joint select-and-pass probability is 0.91 at a realised daily Sharpe of 0.25; selection alone is 0.92)". |
| R-W3-11 | NOTE | 666 | G5(c) "(mean/SD x sqrt(n))" carries no convention pointer, though 0.3 l.70-71 settles it. | Replace with "(mean/SD x sqrt(n), the population SD of t_stat(); 0.3)". |
| R-W3-12 | NOTE | 450-451 | LT3 "the inner-validation set is built with reference= the training Dataset": "training" here must be the inner-training Dataset, which the same sentence distinguishes from the fold's training rows. | Replace "reference= the training Dataset" with "reference= the inner-training Dataset". |
| R-W3-13 | NOTE | 393 with 68-69 | F1.3 uses a on the natural scale (e(t) = (M_ZM(t) - a - b_S M_ZS(t) - b_L M_ZL(t))/0.10) while 0.3 fits lstsq "on centred regressors with an intercept", whose fitted intercept is the mean of M_ZM. An implementer who plugs that intercept into F1.3 is wrong by b_S mean(M_ZS) + b_L mean(M_ZL); G7 does not catch it when both implementations do the same. | Add to l.393 after "in natural units": "(a is the natural-scale intercept recovered from the means, a = mean M_ZM - b_S mean M_ZS - b_L mean M_ZL)". |
| R-W3-14 | NOTE | 443 | LT7 is listed between LT1 and LT2; the numbering is consistent everywhere, but the order invites a miscount of "the seven tests". | Move the LT7 bullet after LT6 (l.457), text unchanged. |
| R-W3-15 | NOTE | 467 | "G1-G5 with the production thresholds (N 838)": the proofs run before the C1 registration, so 838 is the expected N (P7.1 l.616-617). P7.2 l.641-642 recomputes the search's thresholds if the registered N differs, but the proofs would then have been run at another N than the search. | Add "(the expected N; if the registered N differs, the proofs are not rerun and the return says at which N they ran)" or, lead's choice, require the proofs after registration. |

## 5. Summary and what was not done

- Items: 8 CORRECT, 2 PARTIAL (DO-15 u_i criterion; DO-18 unit of the compute stop), 1 WRONG (DO-19: the prompt's
  deadlines moved after v0.3). Hunks: 7 of 7 mapped, none unmapped. Cross-checks: (a) LT numbering consistent and LT7
  defined, one timing gap (R-W3-6); (b) all stated proof numbers recompute except 0.0355 (0.0354) and a loose
  citation, with no compute estimate for the 4,800 proof fits (R-W3-2) and the date count implicit (R-W3-3);
  (c) every feature count agrees; (d) one convention at 0.3, one wording conflict at G3 (R-W3-8).
- New findings: 0 BLOCKING, 8 SHOULD FIX (R-W3-1..8), 7 NOTE.
- Not done: no market data was opened (none was needed); no code was run beyond the arithmetic script; I did not
  re-check items owned by other re-checkers except where a cross-check touched them (DO-6, DO-11, LE-5, FE-2,
  FE-7, FE-8, FE-9, FE-10, AR-2, AR-5 were read for the hunk map and conventions only, and no verdict is given on
  them).
