# SpotCheck_B: FixSpotCheckB-FableXHigh, v0.3 -> v0.4 diff hunks in P4..P10

- Object: reports/stage_e32_discovery_protocol.md DRAFT v0.4, sha256
  87d8203a3a3279368e8218ccaab27a701e632d1b6d8a4ba333831fd828716cd3 (matches the brief; `wc -l` gives 822 lines,
  the brief and the STATE entry say 817).
- Diff: reports/stage_e32_briefs/work/lead/protocol_v0.3.md vs v0.4, 37 hunks; 25 fall at v0.4 line >= 359 (P4 to
  the end) and are checked here. Diff saved at work_spot_B/diff_v03_v04.txt; recomputations at
  work_spot_B/recompute.py (reads p7_thresholds, p7_final and funnel.multiple_comparisons only; no market data).
- Sources read by grep/sed: Recheck_W1..W4.md, stage_e32_STATE.md 483-499 (the lead's rulings),
  docs/prompts/STAGE_E.33.md (l.15-22, 40-58, 63-66, 87-90, 126-140, 142-150, 159-166), screening/trial_registry.py,
  screening/stage_e_verdict.py, screening/stage_e_stats.py, funnel/multiple_comparisons.py,
  reports/stage_e31_briefs/work/pilot/measure31_core.py, reports/stage_e32_data_facts.md (l.268-272, 407-418,
  479-482), reports/stage_e32_briefs/review/ProtocolReview_dof.md l.167-168.
- Model: Fable 5.1 (claude-fable-5-1) per this session's system prompt; the lead verifies from the transcript.

## 1. Per-hunk table (25 hunks)

| # | v0.4 lines | Finding IDs | Verdict | Evidence (recomputed or quoted) | Proposed fix |
|---|---|---|---|---|---|
| 1 | 412 (F1.3) | R-W3-13 | CORRECT | A centred lstsq fit returns intercept = mean M_ZM and the same slopes; the natural-scale intercept is a = mean M_ZM - b_S mean M_ZS - b_L mean M_ZL, residuals and sd_e unchanged. Text states exactly that. | none |
| 2 | 458 (P4.1 heading) | R-W3-6 | CORRECT | "LT7 is repeated after the test list is hashed" matches l.482. | none |
| 3 | 461 (LT7 bullet removed from between LT1 and LT2) | R-W3-14 | CORRECT | LT7 now follows LT6 (l.476); numbering LT1..LT7 unchanged, each defined once. | none |
| 4 | 467-468 (LT3) | R-W3-12, DO-17 | CORRECT | "reference= the inner-training Dataset". | none |
| 5 | 474-483 (LT6, LT7) | R-W1-8 iii; LE-5, R-W1-3, R-W3-6, R-W3-14 | PARTIAL | LT6 "P1.2's Refused list" as R-W1-8 asked. LT7: lead's choice (seed-1 null-search fold models, synthetic-trained, applied to the real streams at LT1's 200 times, grid-restricted; fill recomputed at the production fill time incl. the P3.2 fallback; repeated on Tier A/B models after the hash). LT1 draws 200 decision times (l.459) so "the 200 times of LT1" exists; P4.2's subset is S5 x {FH15, TB30} x 10 (l.491). Missing: the second run happens after real outcomes exist and after the freeze; "stops E.33 until fixed (P10)" names no procedure for that case, while the prompt's B7 (l.134-136) says "A bug found later is fixed only by a logged amendment, with every affected configuration re-run and counted" and P7.1 says the one E33 registration is never repeated (N fixed). A rerun under the same N and a rerun that adds to N are both readable. | S-B-1 |
| 6 | 491-499 (P4.2 search proofs) | FE-2, R-W3-3, R-W3-15, R-W3-5 | CORRECT | 20 x 6 x 40 = 4,800 fits; "P3.6 exclusion calendar" covers P3.6 rule 3 (releases) and rule 4 (P1.4 dates), so it is the broader and right reference; 20 burn-in dates per P1/P9; thresholds at expected N 838 not rerun (lead's R-W3-15 choice); rerun rule per R-W3-5 verbatim. | none |
| 7 | 503-512 (null SD; planted) | R-W3-9; FE-7, R-W3-4, R-W3-10 | WRONG (one number) | 1/sqrt(796) = 0.035444 -> 0.0354 ok. Plant: lead's choice (P3.5 oracle, true class probabilities, P3.8 costs, dead zone l.275, FH15, same plant for TB30, no tick figure). P(>= 14 of 20 at 0.8) = 0.9133 ok; joint at 0.25 = 0.908 -> 0.91 ok. "selection alone about 0.92": recomputed 0.9145, and p7_final.py's own table prints 0.914; that is "about 0.91". | S-B-4 |
| 8 | 538-540 (calibrator) | R-W4-7 | CORRECT | "non-convergence logged and the fit used as is". | none |
| 9 | 546-549 (interrupted fold) | R-W3-7 | CORRECT | Lead's choice (rerun once, second interruption fails). Consistent with P10 "two out-of-memory failures" (l.803) and the prompt's C3 DONE markers. | none |
| 10 | 566-584 (threads, proofs cost, probe formula, long jobs) | R-W4-3; R-W3-2, FE-2; FE-4, DO-18; R-W4-4 | CORRECT (two notes) | 2,880 LOGIT + 1,920 LGBM = 4,800 = 2.67 x 1,800; at 10-60 s / 5-30 s: 10.7-64.0 CPU-h, /7 = 1.5-9.1 h; balanced probes 6.2-9.7 CPU-h, 0.9-1.4 h: all as stated. Fold 6 = 664 (blocks 133x4, 132x2, embargo 21). F 5 names the median/p90/max message-count dates (2022-02-15, 2022-07-27, 2021-05-07). The lead's formula projects the search (build + 1,800 fits) and leaves the 4,800 proof fits to a separate measured figure; consistent with P10 l.801-803 "of the search". Notes: "at 7 processes" (l.571) beside "up to 8 single-thread LOGIT processes" (l.566-567); and the measured quantity P10 compares is "the search", undefined as to whether it includes the build when the store is built before the freeze (l.810-813). | S-B-3, S-B-5 |
| 11 | 630-633 (P6.4 iii port) | FE-6 | CORRECT | measure31_core.VOrder (l.161), Placement (l.236), InstrumentRun.fill (l.307) exist; F 6.2 (data_facts l.479-482) lists them as not reusable; P1.2 l.107-108 now reads "measure31_core's fill logic as the reference for E.33's P6.4 (iii) port only" (consistent). | none |
| 12 | 667-671 (P7.1 freeze file, re-check) | R-W4-5 | CORRECT | trial_registry.require_registered(test_ids, *, test=None, freeze_sha256=None, path=...) exists (l.136-138); register() raises on a repeated test or id (l.218-221). | none |
| 13 | 678 (G3 sign) | R-W1-12 | CORRECT | DSR_MIN = 0.95 and "d_value > DSR_MIN" (stage_e_verdict.py 89, 587). | none |
| 14 | 680 (test DSR sign) | R-W1-12 | CORRECT | as above. | none |
| 15 | 694-699 (b_test unrounded; drop branch) | AR-2, R-W1-4; DO-2, R-W2-2 | CORRECT | b_test = 0.164882 (p7_final at N 838, T_test 870); G4 = 0.200703 (0.200722 at 0.1649); drop branch 0.1017 / 0.1373 / 0.1724: all recompute. 0.2 (l.33) defines an amendment as "a new protocol version decided by the user and hashed before it runs". | none |
| 16 | 701-708 (AR-1 clause) | AR-1, R-W1-1 | CORRECT (one note) | expected_max_sharpe(838, 1) = 3.2045; one null: 1.602 s; two nulls: 1.511 s. (0.25, 0.15): SR0 0.1602, needs 0.2167, passes 0.833; (0.25, 0.10): SR0 0.2403, needs 0.2974, passes 0.085. Stated 0.216/0.84 and 0.296/0.09 agree within rounding (not gates). Monotonicity holds: combined bar = both checks; the amended DSR equals check (2); the as-coded DSR can be stricter or looser than (2), so amending changes the combined bar only when as-coded is stricter, loosening it to (2). | S-B-6 |
| 17 | 720-723 (G3 sign, moments, undefined DSR) | R-W1-12, R-W3-8, R-W2-3, DO-26 (lead) | CORRECT | funnel.multiple_comparisons.deflated_sharpe_ratio exists (l.81); moments() uses pstdev and n-divided moments (stage_e_verdict.py 178-183). | none |
| 18 | 725-726 (G4 b_test source) | DO-2 | CORRECT | A1 verifies the protocol sha256 (prompt l.63-64). | none |
| 19 | 729-730 (G5 c convention) | R-W3-11 | CORRECT | t_stat() (stage_e_verdict.py 209) per 0.3. | none |
| 20 | 733-735 (ranking round) | R-W2-4 | CORRECT | "Python's round() (half to even)". | none |
| 21 | 742-747 (Tier B skip, fallback, rho) | DO-5, R-W2-1, R-W2-5 | CORRECT | ProtocolReview_dof.md l.167-168: 0.429 at rho 0.70, 0.927 at rho 0.98 -> 43%, 93%. | none |
| 22 | 770-772 (P9 calendar assertion) | LE-3, R-W1-5 | CORRECT (one note) | May 2017..Nov 2020 = 43 calendar months (recomputed from TEST_MBO); WASDE, Crop Production and NOPA are monthly; "(row or rule date)" matches P3.6's NOPA rule. P3.6 rule 3 also excludes Crop Production Annual, Grain Stocks, Prospective Plantings and Acreage (l.311-312), for which the test assertion states no count. | S-B-7 |
| 23 | 775-779 (program N; DSR sign) | R-W1-9, R-W1-12 | CORRECT | program_n field (stage_e_verdict.py 300, 384); ">" sign as l.587. | none |
| 24 | 784-789 (P9 reserved decision) | R-W1-1, R-W1-10 | CORRECT | Monotonicity sentence (lead's choice over moving the deadline); "(Holm, t and PBO unchanged)" is a correct tightening of R-W1-1's text. | none |
| 25 | 800-813 (P10 stops; deadlines; features-only store) | R-W4-2; DO-18; DO-19, R-W3-1, R-W4-1; FE-11 | PARTIAL | R-W4-2 text applied; consistent with 0.2 (a P1-P5 choice cannot be dropped without changing a declared choice, so a whole-stage stop is the only reading). DO-18 "measured wall time of the search" applied. Times match the prompt (07:00 C3 l.161-163; 08:00, 08:45, 09:00 l.44-46); R-W4-1's governing clause applied verbatim; FE-11 text verbatim; B3 is the prompt's agreement step (l.87). Missing: the paraphrase "no new configuration starts after 07:00 ..., running ones finish or are recorded as failed by 08:00" is not the prompt's rule. C3 says "If the full budget cannot finish by 07:00 PDT on 2026-10-28, finish whole families", and the protocol's own cut unit is a whole feature set (l.808-809). With up to 8 processes a set is mid-way at 07:00: the prompt (and the cut unit) finish it; the paraphrase forbids starting its remaining configurations. Two readings give P8 different input sets. "recorded as failed" also collides with P5's "failed" (an error; fails G1) where C3 says "unrun" (same P8 effect, different report). | S-B-2 |

Counts: CORRECT 21, PARTIAL 2 (hunks 5, 25), WRONG 1 (hunk 7, one reported number), UNTAGGED 0 (every hunk in
P4..P10 carries a FixVerifier or ProtocolReview tag).

## 2. Coverage of re-check findings whose v0.3 lines fall in P4..P10 (v0.3 340-738)

| Finding | Kind | v0.3 lines | Addressed in v0.4 | Status |
|---|---|---|---|---|
| LE-3 (P9 part) | PARTIAL | 701-702 | 770-772 | yes (S-B-7 note) |
| LE-5 | PARTIAL | 441-445 | 476-483 | yes (S-B-1) |
| AR-1 | WRONG | 643-647, 710-713 | 701-708, 784-789 | yes |
| AR-2 | PARTIAL | 639, 659-663 | 694-695, 725-726 | yes |
| LE-4, AR-5 | CORRECT | 546-550, 452 | no edit needed | n/a |
| R-W1-1 | SHOULD FIX | 643-647, 712-713 | 701-708, 784-786 | yes |
| R-W1-3 | SHOULD FIX | 443-445 | 476-483 | yes |
| R-W1-4 | SHOULD FIX | 639, 661-663 | 694-695, 725-726 | yes |
| R-W1-5 (P9 part) | SHOULD FIX | 702 | 770-772 | yes |
| R-W1-8 (iii) | NOTE | 456 | 474-475 ((i) at 114, other section) | yes |
| R-W1-9 | NOTE | 705 | 775-776 | yes |
| R-W1-10 | NOTE | 710-713 | 786-788 | yes |
| R-W1-12 | NOTE | 623, 625, 659, 705-706 | 678, 680, 720, 775, 778; no ">= 0.95" remains | yes |
| DO-2 | PARTIAL | 639-642, 661-662 | 694-699, 725-726 | yes |
| DO-5 | PARTIAL | 674-679 | 742-747 | yes |
| R-W2-1 | SHOULD FIX | 675-677 | 743-746 | yes |
| R-W2-2 (P7.2 part) | SHOULD FIX | 639-641 | 696-698 | yes |
| R-W2-3 | NOTE | 659 | 722 | yes |
| R-W2-4 | NOTE | 669 | 733-734 | yes |
| R-W2-5 | NOTE | 678-679 | 746-747 | yes |
| DO-15 | PARTIAL | 322-325 | P3 (other checker) | out of scope |
| DO-17 / R-W3-12 | CORRECT / NOTE | 450-451, 507 | 467-468 | yes |
| DO-18 | PARTIAL | 533-535, 724-725 | 574-581, 801-803 | yes (S-B-3) |
| DO-19 | WRONG | 726-729 | 804-810 | yes (S-B-2) |
| DO-13, 14, 16, 20, 21, 22 | CORRECT | 422, 667, 419, 651, 465, 511 | no edit needed | n/a |
| R-W3-1 | SHOULD FIX | 726-729 | 804-808 | yes (S-B-2) |
| R-W3-2 | SHOULD FIX | 465-469, 521-541 | 570-573 | yes |
| R-W3-3 | SHOULD FIX | 465-468 | 491-495 | yes |
| R-W3-4 | SHOULD FIX | 476-479 | 505-508 | yes |
| R-W3-5 | SHOULD FIX | 468-469 | 497-499 | yes |
| R-W3-6 | SHOULD FIX | 443-445 | 476-483 | yes (S-B-1) |
| R-W3-7 | SHOULD FIX | 511-513 | 546-549 | yes |
| R-W3-8 | SHOULD FIX | 660-661 | 722 | yes |
| R-W3-9 | NOTE | 475 | 503 | yes |
| R-W3-10 | NOTE | 479-480 | 511-512 | yes (S-B-4) |
| R-W3-11 | NOTE | 666 | 729-730 | yes |
| R-W3-13 | NOTE | 393 | 412 | yes |
| R-W3-14 | NOTE | 443 | 476 | yes |
| R-W3-15 | NOTE | 467 | 495-496 | yes |
| FE-2 | PARTIAL | 459-481 | 491-495, 570-573 | yes |
| FE-4 | PARTIAL | 533-535 | 574-581 | yes (lead's choice: proofs outside the projection) |
| FE-6 | PARTIAL | 580-582 (+100-101) | 630-633 (+107-108) | yes |
| FE-7 | PARTIAL | 476-480 | 505-508 | yes |
| FE-11 | PARTIAL | 726-731 | 810-813 | yes |
| FE-1, FE-3, FE-9, FE-10 | CORRECT | 611-616, 497-500, 506-508, 393/422 | no edit needed | n/a |
| R-W4-1 | SHOULD FIX | 726 | 804-808 | yes (S-B-2) |
| R-W4-2 | SHOULD FIX | 723-724 | 800-801 | yes |
| R-W4-3 | NOTE | 530 | 566-568 | yes (S-B-5) |
| R-W4-4 | NOTE | 521-540 | 582-584 | yes |
| R-W4-5 | NOTE | 614-616 | 667-671 | yes |
| R-W4-7 | NOTE | 506-508 | 538-539 | yes |

Every finding in my sections is addressed somewhere in v0.4; none is missing. (FE-5, FE-8, R-W4-6, R-W4-8,
R-W2-6, R-W2-7, R-W1-2, R-W1-6, R-W1-7, R-W1-11, DO-1, DO-15 lie in P0-P3: the other checker.)

## 3. Protocol-wide consistency (grep of v0.4 for every term or number my hunks changed)

- ">= 0.95" / "sample skewness" / "0.0355" / "00:00" / "01:00" (stale deadline): no occurrence remains.
- "DSR > 0.95": l.678, 680, 720, 775, 778, all with the program's sign; DSR_MIN strict (stage_e_verdict.py 587).
- b_test and thresholds: 0.1649 displayed (l.681, 694-695), 0.164882 unrounded (l.694), 0.2007 (l.683-684), 0.1373
  and 0.1724 drop branch (l.697); G4 (l.725-726) points to the same pin. Consistent.
- kalgo31 / measure31_core: P1.2 l.107-108 ("reference for E.33's P6.4 (iii) port only") and P6.4 l.630-633 agree;
  runs/measure31/ named in the refused folder (l.114).
- LT7: heading l.458, bullet l.476-483 only; LT1-LT6 unchanged in number.
- "exclusion calendar": only l.492 ("P3.6 exclusion calendar"); P3.6 rule 4 (l.327) cites P1.4, so the reference is
  the inclusive one. "burn-in": l.58, 64, 493, 728, 764, all 20 dates.
- "dead zone": defined l.275 (P3.5), used l.507. "P3.8": section l.348, used l.507, 600, 618.
- "the split" (l.582): the ZS/ZL re-split of l.560.
- "wall time": l.568, 571, 573, 577, 579 (P5) and 801-802 (P10): the projection and the stop both say "of the search";
  the proofs have their own measured figure (l.573). See S-B-3 for the scope of the measured quantity.
- Process counts: l.566-567 "up to 8 single-thread LOGIT processes ... or 2 x 4-thread LGBM" and l.530 "processes x
  threads <= 8"; l.571 "at 7 processes" (S-B-5).
- 0.91 / 0.92: l.511-512 (P4.2) and l.689 (P7.2 table, 0.91 at 0.25); P4.2's "selection alone about 0.92" vs
  p7_final's 0.914 (S-B-4).
- "43 each" (l.772): 43 calendar months May 2017..Nov 2020; T_test 870 = 890 - 20 (l.764, p7_final).
- Deadlines: l.804-808 only; the prompt's C3 wording differs (S-B-2).
- "A1", "B3", "C1", "C3": l.726, 811, 490/385, 548/583/589/810-813; each is a step of the prompt (l.63, 87, 142, 159).

## 4. Problems

| ID | Severity | v0.4 lines | Problem | Proposed fix |
|---|---|---|---|---|
| S-B-1 | SHOULD FIX | 482-483 | LT7's second run (Tier A/B fold models, after the test list is hashed) happens after real outcomes exist and after the freeze. "A mismatch at either time stops E.33 until fixed (P10)" gives no procedure for a fix at that point: 0.2 covers code fixes only "before the first real outcome"; the prompt's B7 (l.134-136) says a bug found after the freeze "is fixed only by a logged amendment, with every affected configuration re-run and counted"; P7.1 says the one E33 registration is never repeated (N fixed at 838). A rerun of the affected configurations under the same N, a rerun that adds trials to N, and a plain stop are all readable, and they give different test lists. Also unstated: which fold model LT7 applies at a time t (implied: the fold whose OOF block holds t's date, as production does). | Replace l.482-483 "LT7 is repeated on the Tier A and Tier B fold models after the test list is hashed. A mismatch at either time stops E.33 until fixed (P10)." with: "At each time t the fold model is the one whose OOF block holds t's date, as in production. LT7 is repeated on the Tier A and Tier B fold models after the test list is hashed. A mismatch at the first run stops E.33 until the code is fixed under 0.2 (the pipeline hash re-taken before the first real-outcome fit). A mismatch at the second run is a bug found after the freeze: E.33 stops the test list, reports the mismatch, and the fix and the re-run of every configuration whose OOF series the fix changes follow the prompt's B7 rule under the one E33 registration (no configuration is added to N; P8 is re-run on the re-run series and the test list re-hashed)." The lead decides whether the rerun stays under N 838 or is a new registration; one must be written. |
| S-B-2 | SHOULD FIX | 804-808 | The deadline paraphrase attributed to the prompt ("no new configuration starts after 07:00 PDT on 2026-10-28, running ones finish or are recorded as failed by 08:00") is not the prompt's rule. C3 (l.161-163) reads "If the full budget cannot finish by 07:00 PDT on 2026-10-28, finish whole families", and l.808-809 makes the cut unit a whole feature set. With up to 8 processes a set is mid-way at 07:00: C3 and the cut unit finish it; the paraphrase forbids starting its remaining configurations. The two readings give P8 different input sets (a partial set versus a whole one). "recorded as failed" also uses P5's word for an error (fails G1) where C3 says "unrun" (same P8 effect, different report). | Replace "no new configuration starts after 07:00 PDT on 2026-10-28, running ones finish or are recorded as failed by 08:00, the return is written by 08:45 and nothing runs after 09:00" with "if the full budget cannot finish by 07:00 PDT on 2026-10-28 the search is cut to whole families (C3): a feature set is started only if the P5 projection says it can finish by 08:00, a started set runs to completion, any configuration still running at 08:00 is stopped and recorded as unrun, the return is written by 08:45 and nothing runs after 09:00". Lead's choice whether a set started before the cut may run past 07:00; one rule must be written. |
| S-B-3 | SHOULD FIX (feasibility only) | 577-581 with 801-803 | The projection formula sums the feature build (796 x builder seconds / P_b) and the 1,800 fits, but P10 compares it with "a measured wall time of the search". When the features-only store is built before the freeze (l.810-813) an implementer can measure the search from the first real-outcome fit (fits only) or from the build's first DONE marker (build plus fits); the 3x stop then fires at different points. No outcome can steer it, but the stop is a different stage outcome. | After "the written value is the reference for P10's 3x stop." (l.580-581) add: "The measured wall time compared with it is the sum of the feature build's wall time (from its first to its last DONE marker, whenever it was built) and the 1,800 fits' wall time (from the first real-outcome fit to the last DONE marker), the same two parts as the projection." |
| S-B-4 | NOTE | 512 | "selection alone about 0.92": recomputed 0.9145 at the unrounded threshold 0.200703; p7_final.py's table prints 0.914. A reported comparison figure, not a gate. | Replace "and selection alone about 0.92" with "and selection alone 0.914 (the P7.2 table)". |
| S-B-5 | NOTE | 571 | "(1.5-9 hours of wall time at 7 processes)" sits beside the thread rule's "up to 8 single-thread LOGIT processes ... or 2 x 4-thread LGBM processes" (l.566-567). An estimate only. | "(1.5-9 hours of wall time at 7 single-thread processes, a rough figure under the thread rule above)". |
| S-B-6 | NOTE | 705-706 | "needs 0.216 and passes with about 0.84 ... needs 0.296 and passes with about 0.09": recomputed at the exact SR0 (3.2045 x 0.05 = 0.1602; x 0.075 = 0.2403), DSR > 0.95 at T_test 870: needs 0.2167, passes 0.833; needs 0.2974, passes 0.085. Within the reviewer's Monte Carlo precision; not a gate. | "needs 0.217 and passes with about 0.83, and beside 0.10 it needs 0.297 and passes with about 0.09". |
| S-B-7 | NOTE | 771-772 | The test-stage assertion covers USDA WASDE, NASS Crop Production and NOPA (43 each) but P3.6 rule 3 (l.311-312) also excludes windows around NASS Crop Production Annual, Grain Stocks, Prospective Plantings and Acreage; the discovery assertion (l.323-325) states counts for all seven types, the test assertion for three. The four others are unchecked for the test calendar. | Add after "43 each": "and, for the four other P3.6 rule-3 report types, the counts the test stage derives from the saved sources before its registration (expected from the USDA schedule pattern, [unverified] here: Crop Production Annual 3, Grain Stocks 14, Prospective Plantings 3, Acreage 4)". The lead verifies the four counts from the saved source pages; no web access was used here. |

No BLOCKING item. Nothing in P4..P10 would leak, lets an outcome steer a choice, or makes a verdict number wrong.

## 5. Not finished or not verified

- The reviewer's DO-5 Monte Carlo (rho table) and AR-1 a3_out.txt were not rerun; the rho cells were read from
  ProtocolReview_dof.md l.167-168 and the AR-1 cases recomputed analytically (section 1, hunk 16).
- The FeasibilityReviewer's per-fit seconds were not re-measured; the CPU-hour and wall-time ranges were recomputed
  from the stated per-fit figures only.
- The S-B-7 expected counts for the four other report types come from the known USDA release pattern, not from the
  saved source pages (no web access, pages not opened): marked [unverified].
- Hunks at v0.4 lines < 359 (P0-P3) were not checked (the other checker).
