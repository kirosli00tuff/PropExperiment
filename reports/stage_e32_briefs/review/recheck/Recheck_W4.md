# Recheck W4: FixVerifierFeas-FableXHigh (feasibility lens items FE-1..FE-11)

Written 2026-10-27 08:33-08:55 PDT. Model: claude-fable-5-1 (this transcript). I did not write the protocol or
its fixes; each fix was assumed wrong until shown correct.

Inputs read (by section, grep and line ranges only):
- reports/stage_e32_discovery_protocol.md DRAFT v0.3, 738 lines, sha256
  330c4af7379791e3957f13818e31b9900adac722e465030a77925e99fc587e1f (checked; the copy
  reports/stage_e32_briefs/work/lead/protocol_v0.3.md has the same hash).
- reports/stage_e32_briefs/work/lead/protocol_v0.2.md (647 lines) through
  `diff` saved at reports/stage_e32_briefs/review/recheck/work_W4/diff_v02_v03.txt (344 lines, 33 hunks).
- reports/stage_e32_briefs/review/ProtocolReview_feasibility.md: the findings table and sections FE-1..FE-11.
- reports/stage_e32_STATE.md lines 356-367 only.
- docs/prompts/STAGE_E.33.md by grep and short ranges (lines 16-60, 140-166); its git history for the deadline.
- Code: screening/trial_registry.py (lines 48-49, 81, 199-224); reports/stage_e32_data_facts.md 6.2 header;
  reports/E.31_RETURN.md headings and a table count over lines 243-343.
- No market data opened (nothing under data/, /mnt/large-storage, ~/.cache, no .dbn, .zst, .parquet). No web.
  No registry, ledger or seal function called; the ID regex was tested on strings in my own script
  (reports/stage_e32_briefs/review/recheck/work_W4/checks.py, output quoted below).

Recomputed numbers (checks.py): the 300 IDs of P7.1 are distinct, all match `_ID`, 10 characters after the
hyphen, and the old form `E33-S5-FH15-L-C0.01-r0` is refused; P(>= 2 of 20 | 0.05) = 0.264; P(>= 14 of 20 | 0.8)
= 0.913; P(>= 14 of 20 | 0.914) = 0.999; P(>= 14 of 20 | 0.492) = 0.050; 300 P(Z > 5.66) = 2.3e-6; 300 P(Z > 4.86)
= 1.8e-4; 0.2007 sqrt(796) = 5.66; 0.1724 sqrt(796) = 4.86; 1/sqrt(796) = 0.0354; training dates per fold under
the P6.1 rule as written (blocks 133, 133, 133, 133, 132, 132; embargo = the 21 dates after block k's last date)
= 642, 642, 642, 642, 643, 664; 59 x 6 = 354 SFI fits per configuration, 1,770 for five; 40 x 1,800 = 72,000;
20 x 6 = 120 fits a search, x 40 = 4,800; (0.35 - 0.25)/0.35 = 0.286.

## 1. Per-item table

| ID | Verdict | v0.3 lines | Evidence (verbatim, current text) | Proposed fix if not CORRECT |
|---|---|---|---|---|
| FE-1 | CORRECT | 611-616 | "E33-<set><label><grid>, set S1..S5; label F05, F15, F30, F60, T15, T30; grid, in the P7.1 order: L001A ... G3200 ... Example: E33-S5F15L010A. E.33 registers all 300 in one screening.trial_registry.register call (test "E33", freeze = the hashed configuration file) before any real-outcome fit." All 300 IDs pass `_ID.fullmatch` and start with "E33-" (checks.py); `register` takes (test, test_ids, freeze, freeze_sha256, harness_sha256) as the text implies; P5's probe IDs E33-S5F15L100E and E33-S5F15G3050 use the same codes. | None required. Two clarity notes in R-W4-5 (a repeat `register` under "E33" raises, trial_registry.py l.218-221, so a restart re-uses the registration; the prompt's C1 per-trial fields can only live in the freeze file, the ledger line's FIELDS are fixed, l.81). |
| FE-2 | PARTIAL | 459-481 | "the subset S5 x {FH15, TB30} x the 10 grid points (20 configurations, 120 fits a search) ... Seeds 1-20 for null searches and 101-120 for planted searches, each run exactly once (no reruns; 4,800 fits in all)." Scale, seeds, pass rules and the analytic null rate (2e-6, 2e-4) all recompute. | Missing from the reviewer's route: (i) the number of synthetic dates for the search proofs is not declared (only implied by "1/sqrt(796)" at l.475); G1 "at least 796 trades", G3 at T = 796 and the P6.1 blocks need 796 OOF dates, and a 30-date implementer reading l.462 would get a different proof. Add at l.465 after "the data facts' rates)": "over 796 synthetic OOF dates (plus 20 burn-in dates) with the P6.1 blocks and embargo and the P1.4 exclusion calendar applied as on the real dates". (ii) The cost is absent from P5's compute estimate and from the probe projection: 4,800 fits is 2.7 x the real search's 1,800 (the reviewer's 1.6-3.3 h of wall time). Add to P5 l.531 after "8-13 s an LGBM fit.": "The P4.2 proofs add 4,800 fits (about 1.6-3.3 h of wall time under the thread cap) before the first real-outcome fit; they may run beside the feature build and the B7 reviews, and they are included in the probe projection of the next bullet." |
| FE-3 | CORRECT | 497-500 | "Threads (ProtocolReview FE-3; CLAUDE.md: at most half the cores, never more than 8): processes x threads <= 8 at any time (LOGIT fits one thread each, up to 8 processes; LGBM 2 processes x 4 threads or 1 x 8); with deterministic true the result does not depend on the thread count." | None required. R-W4-3 (NOTE): l.530 "With 7 worker processes at nice 10" is consistent only read as single-thread LOGIT processes, and "one thread each" is achieved only with OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = 1 in each process (numpy's BLAS is the other thread source, as the reviewer said). |
| FE-4 | PARTIAL | 533-535; P10 724-725 | "E.33 times the feature builder on 3 dates and one fold of the two slowest grid points (E33-S5F15L100E and E33-S5F15G3050), writes the projected total to its STATE file, and that projection is the reference for P10's 3x stop." P10: "measured compute above 3 times the probe-based projection written to the STATE file before the first real-outcome fit (P5)". The reference is now one number (cross-check d passes). | The reviewer's worst-case point is only half taken: the 3 dates are not named (the reviewer: the median, p90 and maximum message-count dates of F 5), the fold is not named, and the projection formula is not stated, so E.33 can probe three light dates and write a low total that the 3x stop then exceeds early (a feasibility stop, not an outcome steer). Replace l.533-535 with: "Probe and compute stop (ProtocolReview FE-4, DO-18): before the first real-outcome fit, E.33 times the feature builder on 3 dates (the median, p90 and maximum ZM message-count dates of F 5) and fold 6 (the largest training set, 664 dates) of the two slowest grid points (E33-S5F15L100E and E33-S5F15G3050); the projected total is 796 x the mean per-date builder seconds plus 1,080 x the L100E seconds plus 720 x the G3050 seconds under the thread cap of this section, plus the P4.2 proofs' 4,800 fits on the same per-fit seconds; E.33 writes it to its STATE file, and that written total is the reference for P10's 3x stop." |
| FE-5 | CORRECT | 95-111; P10 723 | "The list governs market data and measured outcomes; the program's code, docs, prompts and the E.32 briefs are readable." ... "Not opened by E.33's workers (coders and reviewers) ...: reports/E.31_RETURN.md section 3.5, reports/stage_e32_briefs/X1_exposure.md Table C, ... The E.33 lead may read them". P10: "a guard refusal or any read of refused market data or outcomes (P1.2)". The prompt's "Read first: reports/E.31_RETURN.md" no longer conflicts (the lead may read it; sections 5-7 hold no result tables: 0 table rows in l.243-343). | None required for the finding. R-W4-6 (NOTE): the reviewer's closing clause "Where the prompt and this rule differ, this rule applies" was not taken, and this protocol and E.32's own reports (reports/stage_e32_*.md, reports/E.32_RETURN.md) are admitted only by the first sentence's scope, not by name. |
| FE-6 | PARTIAL | 592-594; 536-537; P10 729-731; 580-582; 100-101 | (i) "5 repeats (seeds 1-5), with one noise canary block (M5b a). SFI (one refit per feature and fold: up to 59 x 6 = 354 fits per configuration) only if time remains (P10 cut order)." (ii) "No package is added after the pipeline freeze (uv.lock is hashed): statsmodels is not installed, so anything that would need it is written in numpy with tests before the freeze or reported as not done". (iii) unchanged: "fills simulated with E.31's model (a) K-algorithm and (b) FIFO back of queue (kalgo31 and E.31's fill code, reused for this report only)" and P1.2 (d) "kalgo31 with E.31's fill code for the P6.4 (iii) passive-fill simulation only: F 6.1-6.2". | (i) and (ii) are resolved (R stated, cost stated, cut order in P10). (iii) is MISSING: F 6.2 (data_facts l.479-483) classes measure31_core.VOrder, Loop, Placement, InstrumentRun.fill and _k_allocation as "Not reusable for this purpose", so "E.31's fill code, reused" is a declared choice that cannot be implemented as written, and P10 l.723-724 says "Stop at once" on exactly that (see R-W4-2). Replace l.581-582 "(kalgo31 and E.31's fill code, reused for this report only)" with "(kalgo31 as is, and a port of E.31's queue state machine, measure31_core's VOrder, Placement and fill logic, to the signal times, written and tested by E.33; reported as not done if it is not ready by the P10 cut)", and l.100-101 "and kalgo31 with E.31's fill code for the P6.4 (iii) passive-fill simulation only: F 6.1-6.2" with "and kalgo31, with measure31_core's fill logic as the reference for E.33's P6.4 (iii) port only: F 6.1-6.2". |
| FE-7 | PARTIAL | 476-480 | "Planted: one F3 feature carries a signal whose oracle strategy (it knows the planted signal exactly) has a daily Sharpe of 0.35 net under the selection variant; E.33 reports the realised OOF Sharpe of the best planted configuration per seed beside the oracle. The proof passes if at least one S5 configuration at FH15 or TB30 enters Tier A in at least 14 of the 20 planted seeds (P(at least 14 of 20) = 0.91 at a per-seed power of 0.8 ...)". 0.35, the realised-beside-oracle report and 0.913 all match the reviewer's route; the margin is 28.6% of estimation loss. | The oracle is not defined. "Knows the planted signal exactly" admits two readings with different planted sizes and so different pass probabilities (the proof is a P10 stop condition): the P3.5 rule applied with the generator's true class probabilities (the reviewer's oracle; costs and the dead zone included), or trading the signal's direction whenever it is present. Replace "whose oracle strategy (it knows the planted signal exactly)" with "whose oracle strategy (the P3.5 rule applied with the generator's true class probabilities, with the P3.8 costs and the dead zone)". |
| FE-8 | CORRECT | 312-316; 378 | "HL and LL are the high and low limit prices of the front's last definition record with ts_recv <= 08:30:00 CT on D (a per-date as-of pass over the Z4 files; ProtocolReview LE-2, FE-8) ... If that record's limit prices are UNDEF_PRICE or 0, the limit-proximity part is skipped for D and the date is counted." C.7: "from its last definition record with ts_recv <= 08:30:00 CT on D". | None required. R-W4-8 (NOTE): say "either field" and the no-record case: "If either field of that record is UNDEF_PRICE (mbo_book31.UNDEF_PRICE, 2^63 - 1) or 0, or no such record exists, the limit-proximity part is skipped for D and the date is counted." |
| FE-9 | CORRECT | 67-69; 506-508; 356-358 | 0.3: "a weighted mean and SD are m = sum w x / sum w and sqrt(sum w (x - m)^2 / sum w)". P5: "Calibration: a multinomial logistic regression (C = 1e4, lbfgs, max_iter 1000, tol 1e-6; ProtocolReview FE-9) of y on the booster's three raw scores". G5 unchanged but now governed by 0.3's convention. | None required. R-W4-7 (NOTE): the calibrator's non-convergence handling is not stated (LOGIT's is, l.490-491): add "non-convergence is logged and the fit is used as is" after "tol 1e-6". |
| FE-10 | CORRECT | 68-69; 393; 422 | 0.3: "an OLS fit is numpy.linalg.lstsq on centred regressors with an intercept, and its residual SD is sqrt(SSR / n)". F3.12 cites "(with an intercept; 0.3)"; F1.3's "OLS on the 1-minute samples" is an OLS fit and so falls under 0.3. Equivalent to the reviewer's route (centring plus lstsq; a is recovered from the means). | None required. |
| FE-11 | PARTIAL | 726-731 | "E.33's deadlines (its prompt: the search is cut at 00:00 PDT on 2026-10-28 and work stops at 01:00): the cut unit is a whole feature set in the P5 order ... A features-only store may be built before the pipeline freeze. When time is short, reports are cut in this order (first cut first): the VECM diagnostic, SFI, clustered MDA, the P6.4 (iii) queue variants, the prop simulator, Tier B's variants, the rest of P6.5 (ProtocolReview FE-11). G1-G5 and the test list are never cut." The cut order, the never-cut set and the features-only store are the reviewer's. | Missing: (i) the fingerprint and rebuild rule, and the "after B3 passes" condition, so a store built by pre-freeze feature code can feed the search while the frozen pipeline (and P9's one read on the test window) runs different code. Replace "A features-only store may be built before the pipeline freeze." with "A features-only store (P4 features at every minute mark; no label, no return) may be built as soon as B3 passes and before the pipeline freeze, keyed by the sha256 of the feature code that built it, and is rebuilt if the frozen feature code differs; labels, fits and simulations wait for the freeze and the C1 registration." (ii) The quoted deadlines no longer match the prompt: R-W4-1. |

Verdict counts: CORRECT 6 (FE-1, FE-3, FE-5, FE-8, FE-9, FE-10), PARTIAL 5 (FE-2, FE-4, FE-6, FE-7, FE-11), WRONG 0,
MISSING 0.

## 2. Hunk map (my sections: P5 482-541, P6 542-606, P8 649-688, P10 718-738)

| Hunk (v0.2 -> v0.3 lines) | Item ID(s) | Check |
|---|---|---|
| 444,445c497,500 | FE-3 | Thread rule; verified above. |
| 451,452c506,508 | FE-9, DO-17 | Calibrator max_iter 1000, tol 1e-6; bins from inner-training rows; consistent with LT3 l.448-452. |
| 454a511,514 | DO-22 | "Failed fits": consistent with P8 l.654 "A failed configuration (P5) fails G1" and with "stays in N". |
| 471,472c531,537 | FE-4, DO-18 (probe bullet); FE-6 (no-package bullet); FE-3 (quoted probe times) | The quoted probe times 2.4-3.5 s, 1.9-65.6 s and 8-13 s match the review (FE-3 section: 2.4-3.5 and 1.9-65.6 s LOGIT; 8.1-10.0 and 10.5-13.2 s LGBM). FE-4 PARTIAL as above. |
| 481,484c546,550 | LE-4, AR-5 | Embargo 20 -> 21; training sizes recomputed 642, 642, 642, 642, 643, 664 (cross-check a). |
| 489,491c555,557 | DO-6, AR-2 | Population SD, moments() and t_stat(); consistent with 0.3 l.70-71. |
| 526c592,594 | FE-6 | MDA repeats and SFI cost; verified above. |
| 574c652,654 | DO-20 (and DO-22 cross-reference) | Reports never gates; failed fails G1. |
| 587,591c667,671 | DO-14, DO-7 | Terciles ranks 1-265, 266-530, 531-796 partition 796 (265 + 265 + 266); total-order ranking key. |
| 595,596c675,679 | DO-5 | Tier B by the correlation walk; consistent with P9's use of Tier B. |
| 635,640c722,731 | FE-5 (read clause), FE-4/DO-18 (3x reference), FE-11, DO-19 | Verified above; R-W4-1 and R-W4-2 on this hunk. |

Hunks in my sections: 11; mapped to an item: 11; unmapped (HUNK-): 0. Hunks outside my sections were not checked
(542,548c610,619 is FE-1's P7.1 text and was read for FE-1; 626a710,713 is P9).

## 3. Cross-checks

(a) Embargo and fold sizes. "21" appears at l.452 (LT3: "the embargo (21 dates)"), l.546-548 (P6.1) and l.588
(P6.5, "embargo as P6.1"); no "20 trade dates immediately" or other embargo length remains (grep "embargo|21
dates|642|643|664"). Training sizes from T_disc 796, blocks 133 x 4 and 132 x 2, and the rule "all other blocks'
dates minus the 21 trade dates immediately after block k's last date": 642, 642, 642, 642, 643, 664 (checks.py),
equal to l.548. Agree.

(b) Threads and compute rules. P5 l.497-500 states processes x threads <= 8 and cites CLAUDE.md. P4.2 (l.459-481)
and P6.5 (l.587-606) state fit counts (4,800; 354 per configuration) and no thread counts, so nothing there
contradicts the cap. P5 l.530 "With 7 worker processes at nice 10" is within the cap only as single-thread LOGIT
processes (R-W4-3). nice 10: stated once (l.530); not stated for the feature build, the proofs or the diagnostics
(R-W4-4). One heavy job: the protocol never counts heavy jobs; the prompt allows two (l.38); the LGBM 2 x 4
arrangement is one search job, so no disagreement, but the proofs beside the feature build would be the second.
Resumable: the protocol does not say the search, the feature build or the proofs are resumable; the prompt does
(C3 "resume it from the per-configuration DONE markers", l.49-51 "restartable per trade date, with a DONE marker
per date"). Reported as R-W4-4 (NOTE).

(c) Deadlines and cut order. Protocol: P10 l.726 "its prompt: the search is cut at 00:00 PDT on 2026-10-28 and work
stops at 01:00"; P5 l.539 cites "E.33 prompt C3" with no time; the cut list (l.729-731) appears only in P10. Prompt
(docs/prompts/STAGE_E.33.md as committed at 08:16:42 PDT, 3a75f3b "Stage E.33 hard deadline 09:00 PDT Wed
2026-10-28", after v0.3 was written at 07:58-08:02): l.43-46 "Hard deadline (user, 2026-10-27 08:16): work stops at
08:00 PDT on 2026-10-28; the return is written by 08:45; nothing runs after 09:00"; C3 l.161 "If the full budget
cannot finish by 07:00 PDT on 2026-10-28, finish whole families". The strings "00:00" and "01:00" no longer occur
in the prompt. DISAGREEMENT: R-W4-1. The protocol does not say it supersedes the prompt where they differ: no
"supersede", "prevail", "where they differ" or "this rule applies" occurs; 0.1 lists "This document" last among
binding sources without ordering it against the prompt. The ordering lives only in the prompt (l.18-20: "Binding,
in this order: the frozen protocol ..., this prompt, V43, V50, V37"). Reported as R-W4-2b inside R-W4-6 (NOTE),
since the prompt's own ordering already makes the protocol prevail.

(d) The 3x stop reference. P5 l.535 "that projection is the reference for P10's 3x stop" and P10 l.724-725
"3 times the probe-based projection written to the STATE file before the first real-outcome fit (P5)" name the
same single number; no other "3 times" or "P5 estimate" wording remains (grep). Unambiguous. What goes into the
projection (feature build, 1,800 fits, the 4,800 proof fits) and how it is extrapolated from the probe are not
stated: covered by FE-4 PARTIAL.

(e) P1.2's allowlist for E.33's first steps. Admits by name: the program's code, docs, prompts and the E.32 briefs
(l.96); the program calendars (l.98-99); the release calendar; E.31's code as a library (l.100-101). Admitted by
scope only (the list "governs market data and measured outcomes"): this protocol, reports/E.32_RETURN.md,
reports/stage_e32_test_seal.md, reports/stage_e32_data_facts.md, reports/stage_e32_methods_brief.md (the prompt's
"Read first"), docs/soy_test/SOY_TEST_MANIFEST.json (a doc), and the 156-file manifest.json inside the data
directories (read by verify_discovery_hashes.py, P1.1). Refuses: E.31's measured outputs for everyone (l.103-105:
runs/, stats31.md, stats31.json, the measure31 output tables); for workers, reports/E.31_RETURN.md section 3.5 and
X1 Table C in three files (l.106-110). reports/E.31_RETURN.md sections 5-7 (l.243-343) hold no result tables (0
table rows), so the 3.5 scope is enough. Passes, with R-W4-6 (NOTE) to name the protocol and E.32's reports.

## 4. New findings

| ID | Severity | v0.3 lines | Finding | Proposed fix |
|---|---|---|---|---|
| R-W4-1 | SHOULD FIX | 726 (P10) | The deadlines attributed to the prompt ("the search is cut at 00:00 PDT on 2026-10-28 and work stops at 01:00") are stale: the prompt committed at 08:16 PDT (3a75f3b) cuts the search at 07:00 (C3 l.161) and stops work at 08:00, return by 08:45, nothing after 09:00 (l.43-46); "00:00" and "01:00" no longer occur in it. The prompt binds the protocol first (l.18-20), so a literal E.33 cuts the search seven hours early and fewer configurations reach P8. | Replace the parenthesis with: "(its prompt as last amended before E.33 starts; at this writing, user 2026-10-27 08:16: the search is cut at 07:00 PDT on 2026-10-28, work stops at 08:00, the return is written by 08:45 and nothing runs after 09:00; these times are feasibility limits, not declared choices, so the prompt's current times govern and an amendment of them does not amend this protocol)". |
| R-W4-2 | SHOULD FIX | 723-724 (P10) against 31-33 (0.2) and the prompt l.56-57 | P10 lists "a declared choice that cannot be implemented as written (0.2)" under "Stop at once", while 0.2 says "E.33 stops that part and reports" and the prompt says "If it cannot be run as written, stop that part and report." With FE-6 (iii) unfixed (E.31's fill code is "Not reusable", F 6.2), a literal reader stops the whole stage over a P6.4 diagnostic. Two readings, different outcomes. | Replace "a declared choice that cannot be implemented as written (0.2)" with "a declared choice of P1-P5, P6.1-P6.2, P7 or P8 that cannot be implemented as written (0.2; a P6.3-P6.5 or P6.4 item that cannot be implemented is reported as not done and is not a stop)". |
| R-W4-3 | NOTE | 530 (P5) | "With 7 worker processes at nice 10, about 1-4 hours of wall time" predates the thread rule of l.497-500 and is consistent with it only for single-thread LOGIT processes; "one thread each" needs the BLAS thread variables set. | "With up to 8 single-thread LOGIT processes (OMP_NUM_THREADS = OPENBLAS_NUM_THREADS = MKL_NUM_THREADS = 1) or 2 x 4-thread LGBM processes at nice 10, about 1-4 hours of wall time". |
| R-W4-4 | NOTE | 521-540 (P5 compute) | The protocol never says the feature build, the proofs, the search and the diagnostics are resumable (CLAUDE.md "Long computations are resumable"; the prompt's per-date and per-configuration DONE markers), nor that every long job runs at nice 10. | Add a bullet: "Every long job (the split, the feature build, the P4.2 proofs, the 1,800 fits, P6.4 and P6.5) runs at nice 10, writes a DONE marker per trade date or per configuration and fold, and skips finished pieces on restart (E.33 prompt C3)." |
| R-W4-5 | NOTE | 614-616 (P7.1) | Not stated: a second `register` under test "E33" raises ("a registration is never repeated or amended", trial_registry.py l.218-221), so a stop and restart re-uses the one registration; and the prompt's C1 per-trial fields (family, set, label, horizon, model, hyperparameters, sha256s) can only live in the freeze file, because the ledger line's FIELDS are fixed (l.81). | After "before any real-outcome fit." add: "The freeze file holds, per ID, the set, label, h, model, hyperparameters, pipeline sha256 and protocol sha256 (the prompt's C1 fields; the registry line carries none). The registry refuses a second registration under "E33", so after any stop or restart E.33 re-uses the one registration and re-checks it with trial_registry's check function." |
| R-W4-6 | NOTE | 96 (P1.2) | This protocol and E.32's own reports (reports/stage_e32_*.md, reports/E.32_RETURN.md), which the prompt says to read first, are admitted only by the first sentence's scope, not by name; and the reviewer's clause "Where the prompt and this rule differ, this rule applies" (FE-5) was not taken, so the protocol nowhere says it prevails over the prompt (the prompt says so itself, l.18-20). | "The list governs market data and measured outcomes; the program's code, docs, prompts, this protocol, E.32's reports (reports/E.32_RETURN.md, reports/stage_e32_*.md) and the E.32 briefs are readable. Where the prompt's reading list and this section differ, this section applies." |
| R-W4-7 | NOTE | 506-508 (P5) | The calibrator's non-convergence handling is not stated (LOGIT's is at l.490-491); at C = 1e4 on a near-constant booster lbfgs may hit max_iter, and the fit's use is then undeclared. | After "tol 1e-6; ProtocolReview FE-9)" add ", non-convergence logged and the fit used as is,". |
| R-W4-8 | NOTE | 315-316 (P3.6 rule 5) | "If that record's limit prices are UNDEF_PRICE or 0" does not say whether one or both fields trigger the skip, and the no-record case (no Z4 record with ts_recv <= 08:30 CT on D) is not covered. | "If either field of that record is UNDEF_PRICE (mbo_book31.UNDEF_PRICE, 2^63 - 1) or 0, or no such record exists, the limit-proximity part is skipped for D and the date is counted." |

Severity counts: BLOCKING 0, SHOULD FIX 2, NOTE 6.

## 5. Not finished or not verified

- I did not time anything; the reviewer's probe seconds (2.4-3.5 s, 1.9-65.6 s, 8-13 s) are quoted from the review,
  not re-measured, and the "1.6-3.3 h" for the 4,800 proof fits is the reviewer's figure.
- E.31_RETURN.md sections 5-7 were checked for result tables by a table-row count and a grep only, not read.
- Hunks outside P5, P6, P8 and P10 were not checked (other re-checkers).
