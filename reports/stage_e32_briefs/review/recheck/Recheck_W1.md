# Recheck W1: leakage (LE-1..LE-7) and arithmetic (AR-1..AR-5) fixes in protocol DRAFT v0.3

Label: FixVerifierLeakArith-FableXHigh (independent re-checker; did not write the protocol or its fixes).
Date: 2026-10-27, work 08:42-08:56 PDT (times from `date`).

Inputs read (by section):
- reports/stage_e32_discovery_protocol.md, DRAFT v0.3, 738 lines, sha256
  330c4af7379791e3957f13818e31b9900adac722e465030a77925e99fc587e1f (verified by sha256sum at 08:42).
- reports/stage_e32_briefs/work/lead/protocol_v0.2.md (647 lines); diff saved at
  reports/stage_e32_briefs/review/recheck/work_W1/diff_v02_v03.txt (344 lines, 32 hunks).
- reports/stage_e32_briefs/review/ProtocolReview_leakage.md (findings table + LE-1..LE-7) and
  ProtocolReview_arithmetic.md (findings table + AR-1..AR-5); reports/stage_e32_STATE.md lines 356-367.
- reports/stage_e32_briefs/protocol/p7_final.py (147 lines, source read in full: imports p7_thresholds and
  funnel.multiple_comparisons; reads calendars only, no market data) and p7_final_budget300.md; rerun output at
  reports/stage_e32_briefs/review/recheck/work_W1/p7_final_rerun.md (byte-identical to p7_final_budget300.md).
- Code: screening/stage_e_verdict.py (moments, t_stat, dsr_table), screening/trial_registry.py (current_n,
  register, ID regex), screening/stage_e_stats.py (holm_tier_a), reports/stage_e31_briefs/research/
  usda_releases*.csv (counts only; no dates printed), reports/stage_e31_briefs/work/pilot/ (file names).
- No market data opened; no registration or ledger function called (current_n() reads the registry's last line).

## 1. Per-item verdicts

| ID | Verdict | v0.3 lines | Evidence (verbatim, current text) | Proposed fix if not CORRECT |
|---|---|---|---|---|
| LE-1 | PARTIAL | 249-254, 271-273, 288-293, 311, 333-335; 282 | "The locked-book part of rule 5 looks into the span, so it is a row rule only ...; the trade simulation never conditions an entry on it and uses the P3.2 fallback instead" (290-291); "The decision uses only records with ts_recv <= t." (334); "a trade may be entered at t only if the possible span [t, t + L + h min] meets them and the ZM book at t has both sides and is not marked bad" (289-290) | The entry is now causal and LT7 tests it: the finding's core is resolved. The lead's fallback variant (delayed entry fill instead of a void decision) leaves one case undefined: a TB trade whose entry is filled late has no barrier reference, because P3.4 sets m0 = M_ZM(t + L) and that mid is undefined exactly when the fallback fires. Add after line 254: "For a TB trade, m0 of P3.4 is M_ZM as of the entry fill update (= M_ZM(t + L) when no fallback fired); if M_ZM is undefined at that update the entry is not made and counted with the entries not made." Also line 282: replace "the span of the label starting at t meets P3.6" with "the entry rules of P3.6 hold at t (P3.6, first paragraph)". See R-W1-2, R-W1-6, R-W1-7. |
| LE-2 | CORRECT | 311-316; 441-442 | "HL and LL are the high and low limit prices of the front's last definition record with ts_recv <= 08:30:00 CT on D (a per-date as-of pass over the Z4 files; ProtocolReview LE-2, FE-8)"; LT1: "from ALL input streams (ZM MBO, ZS and ZL MBP-1, and the definitions) truncated at ts_recv <= t" | Equivalent route: the 08:30:00 CT snapshot precedes every decision (rule 1: no span starts before 08:35:00), so no future record is read, and the definitions stream is in LT1. One gap of no consequence for outcomes (R-W1-11): no text for a date with no definition record at or before 08:30 CT. |
| LE-3 | PARTIAL | 300-309; 701-702 | "skip rows whose date is not a valid YYYY-MM-DD ...; keep rows with time_et "12:00" and report exactly one of ... A calendar month with no valid NOPA row (2022-11 and 2022-12 among them) gets its rule date ... E.33 asserts the counts per report type and prints them before any label." | Parse rule, file coverage and placeholder handling are right (my count under the v0.3 rule: WASDE 39, NASS Crop Production 39, Annual 4, Grain Stocks 13, Prospective Plantings 3, Acreage 3, NOPA 37 valid rows; 1 comment line; 7 invalid-date rows, 5 FAS and the 2 NOPA placeholders; exactly 2 months lack a valid NOPA row). Missing: the assertion has no expected values, so it cannot fail. Replace the last two sentences of the parse rule with: "A calendar month with no valid NOPA row (exactly 2022-11 and 2022-12 in these files) gets its rule date ... at 11:00 CT. E.33 asserts, before any label, 39 WASDE, 39 NASS Crop Production, 4 NASS Crop Production Annual, 13 NASS Grain Stocks, 3 NASS Prospective Plantings, 3 NASS Acreage and 37 NOPA counting rows plus 2 NOPA rule dates (39 release dates per monthly report over the 39 months), and stops on any other count." P9 line 702: after "by the P3.6 rule" add "(parse rule included; E.33 asserts one WASDE, one Crop Production and one NOPA date per calendar month of the window, 43 each)". |
| LE-4 | CORRECT | 546-550; 452 | "the 21 trade dates immediately after block k's last date. 21 covers the longest feature look-back: F1.7's and F4.7's 20-date SDs reach the 13:15 mid of the 21st date back ... Training dates per fold: 642, 642, 642, 642, 643, 664."; LT3: "the embargo (21 dates) exceeds every label's span and every feature look-back" | Recomputed: blocks 133,133,133,133,132,132 (sum 796); 796 - 133 - 21 = 642 (folds 1-4), 796 - 132 - 21 = 643 (fold 5), 796 - 132 = 664 (fold 6, no embargo). Every look-back in P4 and 0.3 is at most 20 dates (sigma_X, trailing references, C.5 Vbar: 20; F1.3: 10; F1.7/F4.7: 20 overnight changes reaching the 21st date's 13:15 mid), so the first training date E + 22 reads nothing from block k. Route (a) of the finding. |
| LE-5 | PARTIAL | 441-445; 449-452 | LT1: "from ALL input streams (ZM MBO, ZS and ZL MBP-1, and the definitions)"; LT7: "for the same 200 times, the entry decision recomputed from streams truncated at t equals the production decision, and the entry fill recomputed from streams truncated at t + L equals the production fill."; LT3: "each row's weight depends only on rows of its own date" | LT1 and LT3 parts done. LT7 as written contradicts the P3.2 fallback: a fallback entry fills at the first book update after t + L, so a stream truncated at t + L cannot reproduce it and the test fails on a correct simulator; and no configuration is named although the decision needs a model. Replace lines 443-445 with: "LT7 Simulator causality (ProtocolReview LE-5): for the same 200 times restricted to each configuration's grid G_h(D), and for the 20 configurations of P4.2's subset (S5 x {F15, T30} x the 10 grid points), the entry decision (side or no trade) recomputed from all streams truncated at t equals the production decision, and the entry fill recomputed from streams truncated at the production fill time (t + L, or the fallback fill update of P3.2) equals the production fill. Any mismatch stops E.33 until fixed." |
| LE-6 | CORRECT | 311-312; 271-273; 249-254 | "(row rule) no span with a book update at which the ZM book lacks a bid or an ask or is marked bad (ProtocolReview LE-6)"; "The barrier test steps through book updates (0.3) and ignores updates at which M_ZM is undefined (an empty side or a bad book never triggers a barrier" | Both sentences of the finding's fix are present; the trade-side case (FH exit into a bad book) is covered by the P3.2 fallback ("or the book is marked bad, at u + L"). |
| LE-7 | CORRECT | 95-110; 159; 456 | Refused (guard): "E.31's measured outputs (reports/stage_e31_briefs/work/pilot/runs/, stats31.md, stats31.json, the measure31 output tables)"; "Not opened by E.33's workers (coders and reviewers), because they reproduce E.31's discovery-date statistics: reports/E.31_RETURN.md section 3.5, reports/stage_e32_briefs/X1_exposure.md Table C, ... The E.33 lead may read them"; P1.5 item 5: "E.33's workers do not open E.31's outputs (P1.2)" | Equivalent route: the former prose "never" list is now in the guard-enforced refusal list (stats31.md/json are under pilot/runs/, verified by find), and the markdown reproductions are closed to the workers who could be steered, with P1.5 item 5 now consistent with P1.2. A data guard cannot enforce what an agent opens with a file reader, so the reviewer's "LT6 then covers them" was never achievable for the .md files; the lead's split is the enforceable version. Three wording notes in R-W1-8. |
| AR-1 | WRONG (one clause); structure sound | 643-647; 710-713 | "with any companion whose test Sharpe is null or weaker, its SR0 is 1.51-1.60 times the strong candidate's Sharpe, so a true daily Sharpe of 0.25 or 0.30 then fails with probability near 1"; P9: "which makes a real edge fail whenever a companion's test Sharpe is null or weaker (P7.2)" | The disclosure and the reserved user decision are the right pre-registration structure (section 3c). The quantitative clause is wrong for a weaker but non-null companion: SR0_program = 3.2045 x pstdev(tested Sharpes) (E[max] multiplier at N 838, recomputed), which is 1.602 s with one null companion (k = 2) and 1.511 s with two (k = 3), but 3.2045 x |s1 - s2| / 2 at k = 2 otherwise: at (0.25, 0.15) SR0 = 0.160, the better member needs 0.216 and passes with about 0.84; at (0.25, 0.10) SR0 = 0.240, needs 0.296, passes with about 0.09 (the reviewer's own numbers, reproduced). Replacement for lines 643-647 and 712-713 in R-W1-1. |
| AR-2 | PARTIAL | 64-71; 555-557; 659-663; 665; 639 | 0.3: "Statistics of daily series (mean, SD, Sharpe, skewness, raw kurtosis, t) are those of screening/stage_e_verdict.py moments() and t_stat() (population SD; Sharpe = mean / pstdev)"; P6.2: "population SD, daily Sharpe SR_d = mean / population SD, skewness, raw kurtosis and t, exactly as ... moments() and t_stat() compute them"; P7.2: "b_test is pinned at 0.1649 (N 838, T_test 870)" | Conventions fixed and verified against the code (moments(): statistics.pstdev, third and fourth moments over n; t_stat(): harvey_liu_zhu_verdict(mean, pstdev, n)). G5(c)'s "mean/SD" is now covered by 0.3. Missing: the finding's third sentence (G4 uses p7_final.py's unrounded b_test, not the 4-decimal display). Unrounded b_test at N 838 = 0.164882 (DSR exactly 0.95000); at 0.1649 the DSR is 0.95006. G4 threshold: 0.200703 at the unrounded value, 0.200722 at 0.1649; a configuration with SR_d in [0.200703, 0.200722) passes under one reading and fails under the other. Line 639: replace "b_test is pinned at 0.1649 (N 838, T_test 870)" with "b_test is pinned at p7_final.py's unrounded value at the registered N (0.164882 at N 838, T_test 870; displayed 0.1649), and G4 compares against that value". |
| AR-3 | CORRECT | 615-618; 659-660 | "The N of every DSR, threshold and test in P7.2, P8 and P9 is trial_registry.current_n() immediately after that registration: 838 if no other stage registers first" | Verified: current_n() = 538 now (registry's last n_after); register() appends one entry with N + len(test_ids), so one call with 300 ids gives 838; the ID regex [A-Z][A-Za-z0-9]{0,15}-[A-Za-z0-9]{1,16} and the "E33-" prefix rule accept E33-S5F15L010A, E33-S5F15G3200 etc., and "E33" passes the test-label regex. P8 G3 agrees. One wording note on P9's "the list's program N" (R-W1-9). |
| AR-4 | CORRECT | 636-638 | "the test's Holm (holm_tier_a at K = 9 over m tested candidates, alpha 0.05/(9m)) z 2.539, 2.773, 2.902 for m = 1, 2, 3 (ProtocolReview AR-4)" | Recomputed one-sided z at 0.05/(9m): 2.539, 2.773, 2.902. holm_tier_a (stage_e_stats.py 317-334) uses threshold alpha_k / (m - i) at step i = 0, i.e. alpha_K / m at step 1. The added clause "t > 3.0 is stricter at the test than Holm" holds (2.902 < 3.0). |
| AR-5 | CORRECT | 546-550; 452 | as LE-4 | Route (a) with the training-date counts the finding asked for; counts recomputed above. |

## 2. Hunk map (my sections: 0 = lines 1-80, P1 = 81-161, P7 = 607-648, P9 = 689-717)

| v0.2 lines -> v0.3 lines | Item ID(s) | Check |
|---|---|---|
| 3 -> 3 | HUNK-3 | Status line only (v0.2 -> v0.3, "ProtocolReviewer findings applied"); no content; fine |
| 35-36 -> 35-38 | DO-1 | Readings file hashed before C1, none after the first real-outcome fit; P8 unit-tested on synthetic series; consistent with P4.2 and P10 |
| 61a -> 64-71 | DO-9; DO-12, FE-9, FE-10; DO-6, AR-2 | "Book update" = state after an F_LAST record (matches measure31_core's F_LAST boundaries, data facts 471); statistics conventions verified against moments()/t_stat() |
| 85-94 -> 95-110 | FE-5, LE-7 | See LE-7 and R-W1-8 |
| 542-548 -> 610-619 | FE-1, DO-3; DO-4, AR-3 | ID pattern and example verified against the registry regex; "min_data_in_leaf 50h or 200h" matches P5 line 501 ("{50 h, 200 h} rows"); N rule verified |
| 565-569 -> 636-647 | AR-4; DO-2; AR-1 | Holm z verified; b_test pinning (see AR-2 remainder, R-W1-4); AR-1 clause wrong (R-W1-1) |
| 626a -> 710-713 | AR-1 | Reserved decision; wording wrong in the same way (R-W1-1); deadline note (R-W1-10) |

Hunks in my sections: 7; mapped to items: 6; unmapped (HUNK-): 1 (checked, no finding). Hunks outside my sections
(P3, P4, P5, P6, P8, P10) were read for the item checks only and are not mapped here.

## 3. Cross-checks

### (a) N: 538 and 838
- 838 at lines 467 (P4.2 proofs use N 838), 617, 621 (P7.2 heading), 625, 636, 639, 641 (P7.2), and "the registered N
  after E.33's registration" at 659-660 (P8 G3), "the registered N" at 663 (G4): all denote N after E.33's one
  register() call of 300 ids. 538 appears once, line 204 ("the 538 are bar-level"), as the count of trials registered
  before E.33, which equals current_n() today (538, read at 08:50). P7.1 says 838 is conditional on no other stage
  registering first, and P7.2 says p7_final.py recomputes at the registered N otherwise. All uses agree.
- P9 line 705, "the list's program N": in stage_e_verdict.py program_n is a field of the test's candidate-list payload
  (lines 300, 384) recorded beside the registry's N (registry_n, 758). P7.1 says the N of every test in P9 is 838; if
  a stage registers trials between E.33 and the test, the two can differ. Wording only (R-W1-9).

### (b) P7.2 and P9 numbers against p7_final.py
- Rerun: `uv run python reports/stage_e32_briefs/protocol/p7_final.py --budget 300 --out work_W1/p7_final_rerun.md`,
  rc 0, output byte-identical to p7_final_budget300.md (diff empty). The script reads program calendars only.
- Every P7.2 number matches the output: SR0 0.1137; G3 0.1724 (t 4.86; 2.74 annualised), 0.1756 at skew -0.5,
  kurtosis 6; t > 3.0 at T_test 870 = 0.1017; test DSR 0.1649 (t 4.86); b_test 0.1649 (2.62); G4 0.2007 (t 5.66;
  3.19); dropped-DSR branch b_test 0.1017 and selection threshold 0.1724; select-and-pass products 0.026, 0.109,
  0.417, 0.908 -> 0.03, 0.11, 0.42, 0.91 at s = 0.15, 0.17, 0.20, 0.25; per-trade 0.71 (h 5, n 4), 0.50 (n 8), 1.22
  (h 15, n 4), 0.87 (n 8), 1.73 (h 30, n 4), 3.46 (h 60, n 2); 80%-power Sharpe 0.1936; reference z 3.588, 3.847,
  4.042 (c(300) 6.283), 2.539, HLZ 3.0. T_disc 796 (816 - 20), T_test 870 (890 - 20).
- P9: T_test 870 and 890 program trade dates (line 696-697) match. P4.2 (not my section, touched by the numbers):
  N 838, 300 x P(Z > 5.66) = 2.3e-6 ("about 2e-6"), 300 x P(Z > 4.86) = 1.8e-4 ("about 2e-4"), 1/sqrt(796) =
  0.03544 ("0.0355"), selection power 0.914 at s = 0.25 ("0.91"), P(at least 14 of 20 | 0.8) = 0.913, P(at least 2
  of 20 | 0.05) = 0.264: all agree. P8 terciles 265 + 265 + 266 = 796. P6.1 training dates 642/642/642/642/643/664
  agree with the block sizes and the 21-date embargo.
- Unrounded values the protocol does not print: b_test 0.164882, G3 0.172422 (DSR at the display value 0.1724 is
  0.94994, at 0.1725 is 0.95023; P8 G3 gates on the function, so this is fine). The only consequence is the G4
  rounding band of AR-2 (R-W1-4).
- Sign: P9 (1) says "DSR > 0.95" (the program's DSR_MIN is strict, stage_e_verdict.py 89, 587); P8 G3, P7.2 and P9
  (2) say ">= 0.95". Measure zero, as the arithmetic lens said (AR-15, a NOTE the lead did not apply); R-W1-12.

### (c) AR-1 as a pre-registration matter
Question: does disclosing the power gap in P7.2 and reserving the V14 (c) amendment to the user in P9 resolve the
BLOCKING finding, given that the bar must be fully stated before outcomes and the power statements must describe
the bar in force under each branch?

Judgment: yes in structure, with one wrong clause and one missing sentence.
1. Both branches are fully stated before any test outcome. Under (a) (amend V14 c for this test) the program DSR
   uses V = 1/(T_test - 1), so check (1) coincides with check (2) and the P7.2 table is the exact power of the
   combined bar. Under (b) (as coded) V = the population variance of the tested Sharpes: a stated rule whose value
   depends on the test outcomes, which pre-registration permits as long as the rule is fixed first; it is.
2. Monotonicity makes the choice safe against outcome steering. The combined bar is "both pass". Under (a), (1) =
   (2); under (b), (1) is an extra condition. So amending can only loosen the combined bar, and only down to check
   (2), whose power the table states. No discovery outcome can steer the user to a bar looser than the tabulated
   one; the table is therefore the exact power of the loosest admissible bar and an upper bound otherwise, which
   is what lines 646-647 say ("upper bounds that depend on the list's composition").
3. The power statement under (b) is partly wrong: lines 644-646 claim SR0 = 1.51-1.60 x the strong member's Sharpe
   and near-certain failure "with any companion whose test Sharpe is null or weaker"; that holds for null companions
   only (section 1, AR-1). A frozen protocol that E.33 copies into its reports should not carry it. R-W1-1 gives
   the replacement.
4. The decision deadline, "before the test is registered" (line 710), falls after the discovery outcomes are
   known. By point 2 this cannot loosen the bar beyond check (2), but the protocol does not say so; a reader sees
   an outcome-informed choice of bar. Either add the monotonicity sentence (R-W1-10) or move the deadline before
   E.33's C1 registration, as DO-2 does for b_test. The lead's route ("E.32 does not amend a user decision; it
   states the consequence") is correct: the amendment is the user's.

## 4. New findings

| ID | Severity | Lines | Finding | Proposed fix |
|---|---|---|---|---|
| R-W1-1 | SHOULD FIX | 643-647, 712-713 | The AR-1 clause overstates: SR0_program = 3.2045 x pstdev(tested Sharpes) is 1.60 s (k 2) or 1.51 s (k 3) only when the companions are null; a weaker non-null companion gives 3.2045 x |s1 - s2| / 2 at k 2, so at (0.25, 0.15) the strong member passes with about 0.84 and at (0.25, 0.10) with about 0.09. "Fails with probability near 1" and "fail whenever a companion's test Sharpe is null or weaker" are wrong for the weaker case. | Replace lines 643-647 with: "The test-power figures above (and P4.2's) assume the test's DSR checks use V = 1/(T_test - 1). The program verdict as coded (V14 c) takes V = the population variance of the 2-3 tested Sharpes, so its SR0 = 3.2045 x the population SD of those Sharpes (the E[max] multiplier at N 838): with one null companion SR0 = 1.60 x the strong member's Sharpe (two nulls: 1.51 x), and no true Sharpe passes; with a weaker but real companion SR0 = 3.2045 x half the gap between them (two members), so a true 0.25 beside a true 0.15 needs 0.216 and passes with about 0.84, beside 0.10 it needs 0.296 and passes with about 0.09 (ProtocolReview AR-1, a3_out.txt). Under V14 (c) as coded these powers are upper bounds that depend on the list's composition; amending V14 (c) as P9 reserves makes check (1) identical to check (2), so it can only loosen the combined bar, and only to the bar whose power is tabulated. P9 reserves the remedy to the user." Replace lines 712-713 "which makes a real edge fail whenever a companion's test Sharpe is null or weaker (P7.2)" with "which makes a real edge fail with near certainty beside a null companion and with a probability that rises with the gap between the members' true Sharpes (P7.2)". |
| R-W1-2 | SHOULD FIX | 249-254 with 264-270 | A TB trade whose entry fill is delayed by the P3.2 fallback has no defined barrier reference: P3.4 sets m0 = M_ZM(t + L), undefined when the book as of t + L lacks a side or is bad, which is exactly the fallback case. Two implementations (m0 at the fill update; no barriers, vertical exit only) give different trades. | Add after line 254: "For a TB trade, m0 of P3.4 is M_ZM as of the entry fill update (equal to M_ZM(t + L) when no fallback fired); if M_ZM is undefined at that update, the entry is not made and is counted with the entries not made." |
| R-W1-3 | SHOULD FIX | 443-445 | LT7 recomputes the entry fill "from streams truncated at t + L", but a P3.2 fallback fill occurs at a later book update, so a sampled fallback case fails LT7 on a correct simulator ("Any mismatch stops E.33"); and LT7 names no configuration although the decision needs a fitted model. | Text in the LE-5 row of section 1. |
| R-W1-4 | SHOULD FIX | 639, 661-663 | G4's b_test is the 4-decimal display 0.1649 while G3 and the P7.2 thresholds are the function's values; unrounded b_test 0.164882 gives G4 0.200703 against 0.200722 at 0.1649, a band in which the two readings disagree. | Text in the AR-2 row of section 1. |
| R-W1-5 | SHOULD FIX | 307-308, 702 | "E.33 asserts the counts per report type" names no expected counts, so the assertion cannot fail; "2022-11 and 2022-12 among them" suggests other months may lack a NOPA row (none does). P9's test calendar inherits no count expectation. | Text in the LE-3 row of section 1 (counts verified: 39, 39, 4, 13, 3, 3, 37 + 2 rule dates). |
| R-W1-6 | NOTE | 282 | P3.5 still says "the span of the label starting at t meets P3.6", which read alone includes the row-only locked-book rule that P3.6 now excludes from entries. | "the entry rules of P3.6 hold at t (P3.6, first paragraph)". |
| R-W1-7 | NOTE | 252-254 | The limit-marked exit uses "the front's limit price ... per P3.6 rule 5's definitions", undefined on a date whose definition record carries UNDEF_PRICE or 0 (rule 5's skip case). | Add: "if D has no limit prices (rule 5's skip case), the exit is marked at the last valid touch on that side before it emptied, and flagged." |
| R-W1-8 | NOTE | 105-106, 108-109, 456 | (i) "the measure31 output tables" is not a path; a guard test "for each" needs one (measure31 writes `<out>/<date>/{placements,loop,implied,days}.parquet`, README_measure31.md 58; the run folder should be named, under pilot/runs/ if that is where E.31 wrote it). (ii) "X1_exposure.md Table C": say whether the file or the section is closed to workers (a worker reading by grep can skip a section). (iii) LT6 "every path and date class of P1.2" should say "of P1.2's Refused list": the "Not opened by E.33's workers" list is a worker rule a data guard cannot test. | As stated. |
| R-W1-9 | NOTE | 705 | "the list's program N" is the test candidate list's program_n field (stage_e_verdict.py 300, 384), set at the test registration; P7.1 says the N of every test in P9 is 838 (current_n() after E.33's registration). They differ if a stage registers trials in between. | "at the list's program N (= the N of P7.1, 838, unless trials were registered after E.33, in which case the registry's N at the test registration, recorded beside it)". |
| R-W1-10 | NOTE | 710-713 | The reserved decision's deadline ("before the test is registered") is after the discovery outcomes are known. Harmless by monotonicity (amending can only loosen the combined bar to check (2), the tabulated bar), but the text does not say so, so a reader sees an outcome-informed choice of bar. | Either add to line 713: "Amending can only loosen the combined bar, and only to check (2), whose power P7.2 tabulates; the discovery outcomes cannot steer it further." or set the deadline "recorded before E.33's C1 registration" as DO-2 does for b_test. |
| R-W1-11 | NOTE | 314-316 | Rule 5 covers a record with UNDEF_PRICE or 0 but not a date with no ZM-front definition record at or before 08:30:00 CT on D (possible on the first file date, a burn-in date). | Add: "if no such record exists on or before D, the latest earlier record in the Z4 files is used; if none, the limit-proximity part is skipped for D and the date is counted". |
| R-W1-12 | NOTE | 705 vs 623, 625, 659, 706 | P9 (1) "DSR > 0.95" is the program's strict sign (DSR_MIN, stage_e_verdict.py 89, 587); P8 G3, P7.2 and P9 (2) use ">= 0.95". p7_final.py solves the thresholds at equality, so at the display values both signs pass (DSR 0.95006 at 0.1649); measure zero, but E.33's two implementations should copy one sign (the arithmetic lens's AR-15). | In P8 G3 and P9 (2) write "DSR > 0.95 (the program's sign)" or state that (2) uses ">=" by design. |

## 5. Not finished or not verifiable here
- The reviewer's Monte Carlo (a3_out.txt) was not rerun; the closed-form SR0 cases and the two pass probabilities
  were recomputed analytically and agree with the figures quoted in the AR-1 finding.
- T_test = 870 and 890 program trade dates were taken from p7_thresholds.trade_dates (program calendars); the
  leakage lens's LE-17 note (which calendar mix reproduces 890) was not re-examined.
- The location of measure31's `<out>` folder was not resolved (R-W1-8 i); E.31's return tables were not opened.
