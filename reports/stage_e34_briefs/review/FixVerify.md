# FixVerify: verification of DRAFT v0.2 of reports/stage_e34_zl_protocol.md (FixVerifier-FableXHigh, Fable 5.1, xhigh)

Written 2026-10-29, 15:28-15:45 PDT (session 3). Object under review: reports/stage_e34_briefs/review/protocol_v0.1_to_v0.2.diff
(318 lines, read whole), review/FixLog.md, and L.f of reports/stage_e34_briefs/L_lead_reconciliations.md, against the
BLOCKING and SHOULD FIX items of review/MathReview.md and review/ProtocolReview.md and the sources each fix cites.
Scratch files, scripts and their outputs: reports/stage_e34_briefs/work/FixVerifier-FableXHigh/ (my_diff.txt,
ledger_agg.out, recompute_p7_rerun.py and its recompute_p7.out, extra_checks.py/.out, f10_hand_tests.py/.out).
No market-data file, no outcome file of P1.2's list, no E.33/E.33b/E.33c result file, no web, no .env, no key, no
Databento call, no git change; the protocol and every other stage file untouched.

## Verdict: PASS WITH FIXES

- The diff is the true object: `diff review/protocol_v0.1.md reports/stage_e34_zl_protocol.md` reproduces
  review/protocol_v0.1_to_v0.2.diff byte for byte (v0.1 sha256 c49b4aef..., live protocol 3069fbee..., both files
  stamped 15:26:00 PDT). Every hunk maps to a FixLog item (the one unlisted hunk, P10.4's "the review files" gloss,
  is benign).
- All 4 BLOCKING items: FIXED. All 16 SHOULD FIX items: 15 FIXED, 1 PARTLY (PR-S4: the new sentence "no feature,
  label, exclusion or fill reads ts_event" is contradicted by F10.10's trade-set key; not a look-ahead).
- Every new number recomputes (table below): z 5.72, the K2 trigger 810 (exact with the frozen functions: K2 binds
  for a G4 passer iff T_test <= 810), 2.25 ticks / 41% / 19%, 43 / 258 / 180 / 120, 0.898 / 0.905 at N 1038, the
  exact SR80 0.1958, the tail percentages, and the ledger figures (73 settled ZM.v.0 ohlcv-1m rows, median 0.0608,
  max 0.0738; 39 three-parent definition rows, median 0.0385; 1.46, 1.77, 1.66, 26.5).
- The new F10.7 and F10.9 definitions are point in time and give the right hand values on the MathReviewer's two
  counterexamples (F10.7: 50 where v0.1 gave 0; F10.9: 3 removals whichever record carries the post-fill reduction,
  where v0.1 gave 0 on the T-record placement) and on nine further cases (f10_hand_tests.out).
- No new leak or look-ahead. No P7.2 threshold changed; N stays 838.
- New findings: 0 BLOCKING, 4 SHOULD FIX (all wording or a definition's ambiguity; none moves a threshold, a trial
  count or a declared choice's substance), 7 NOTE. Replacement text is given for each.

Counts: items checked 20 (4 BLOCKING, 16 SHOULD FIX): FIXED 19, PARTLY 1, NOT FIXED 0, WRONG 0. NOTEs acted on,
spot-checked: 27 (all as described; one, PR-N4, introduced an ambiguity: new finding F1). Recomputations: 32 rows,
32 match. New findings: 4 SHOULD FIX (F1-F4), 7 NOTE (F5-F11).

## Per-item table (BLOCKING and SHOULD FIX)

| Item | Status | Evidence (v0.2 line; source checked) |
|---|---|---|
| MR-B1 F10.7 zero rule wrong on a rise-then-fall second | FIXED | P4 F10.7 row (line 418): "qb~ = 0 if the most recent change of bid_1 with ts_recv in (t - 1 s, t] was an increase ... qa~ symmetric (0 if the most recent change of ask_1 ... was a decrease)" = the reviewer's exact fix; LT12 (lines 446-450) adds the path with the hand value "min over [t - 0.2 s, t], not 0". Hand test 1 (f10_hand_tests.out): v0.2 gives 50 (= exact seasoned depth), v0.1 gave 0. Methods errata 1. Rule uses only states with ts_recv <= t: point in time |
| MR-B2 F10.9 fill attribution wrong when the reduction sits on the T record | FIXED | F10.9 row (line 420): D_b(p) over "every consecutive pair of front records from the state before b to b's F_LAST record, of any action", minus T_b(p) once, floored at 0; one-sided or bad pairs 0 and counted; DC2 reworded as a report (454-455); LT12 tests both placements. Hand tests A (reduction on T: v0.2 3, v0.1 0), B (on a later M: 3, 3), B2 (on an F record: 3, 0), D, E, F, G, H all as expected. Errata 2. Batches counted by their F_LAST ts_recv <= t (G1): point in time. See NOTE F6 (a later-batch reduction is counted as a cancel under both forms, as M1 section 8 discloses) |
| PR-B1 ZM test bars not owned before 2019-05 | FIXED | P9.1 (542-549), P9.2 (557-565), P11 rows (666-668, 673-674) agree: ZL and ZS 44 chunks 2017-04..2020-11, ZM 19 chunks 2019-05..2020-11 (reports/stage_e32_test_seal.md lines 57-59 verified: "ZM \| 19 \| 2019-05 to 2020-11 (no earlier ZM file is owned)"); ZM.v.0 ohlcv-1m 2017-05-01..2019-04-30 bought with the test MBP-1, stop before the read if not bought; P2 F09p reworded; BRIEFS RULES corrected (lines 414-417); L.f.4. Ledger figures reproduce (table below). See NOTE F5 ("at most" USD 1.66) |
| PR-B2 = MR-S2 two bad-book rules | FIXED | 0.3 (71-77): one reading for features, labels, exclusions and fills, "an update is bad iff any record of its batch carries F_MAYBE_BAD_BOOK", mark for that update only; feat33.py 558-562 docstring and code 589-606 verified (`batch_bad` set on any flagged record, consumed at F_LAST, then cleared); F10 header (411-413) points to 0.3/FA-4; P3.2 (297-298) labels and fills same code in both windows; L.f.2; errata 4. No F_LAST-only sentence survives (grep). One wrong fact inside the new text: "(MBP-1 has no R record ...)", DF34 line 144/151 counts one R record: new finding F4 (wording; the rule itself is right) |
| MR-S1 20-cap binds for TB | FIXED | 0.5 (115), P3.8 (337-339), P7.2 row label (511) and note (516-517): FH maxima 17/8/4 (recomputed: floor((277 - h)/(h + 1)) + 1), TB realised and capped at 20, the measured K2 form governs; L.f.1 |
| MR-S3 M2's 12:50 CT cap in option B | FIXED | Header OC-5 (10-14): option B "on the grid of L.c, without M2's 12:50 CT cap"; methods errata 5. Option B only; nothing in option A's text changes |
| MR-S4 bar bounce omits sqrt 2 | FIXED | P2 F09p (251-255): "about 2.25 ZL ticks: 41% of sigma_1 and 19% of sigma_5"; recomputed sqrt(2) x 1.594 = 2.254, 40.8%, 18.7%; k = 1 still dropped; errata 6 |
| PR-S1 two run orders | FIXED | P7.1 (491-493) "sets S_pool, S_crush, S_book, S_prop (P10.3's cut order); inside a set FH15, FH30, FH60, TB15, TB30; inside a label the P5 grid order"; P10.3 (639-640) "a whole set in P7.1's run order"; 0.4 (106-107) maps E.32's S5, S1, S3, S2, S4 to the same order. P8's set index (S_crush 1 .. S_pool 4) is a tie-break index, as in E.32, not a run order |
| PR-S2 mirror substitutions incomplete | FIXED (one ambiguity: F2) | 0.4 (101-109) lists 200, the set names, 43 columns, N_reg, z 5.72, the four blocks, 258, 180/120, the run order, the labels, 0.90/0.905. All recompute. The 0.91 -> 0.90 substitution would also catch E.32 P4.2's binomial 0.91 (P(at least 14 of 20) at 0.8 = 0.913, independent of N): finding F2 |
| PR-S3 methods file missing | FIXED | reports/stage_e34_zl_methods.md exists (15:29 PDT, 2,199 lines): a lead front (verdicts; errata 1-19) then the five worker files, each contained verbatim (substring check, work/FixVerifier-FableXHigh notes); sources line (21-24) and P10.4 (643) name it. The errata cover MR-S3 and MR-S4 |
| PR-S4 ts_event reads | PARTLY | P1.2 (150-152) now says "no feature, label, exclusion or fill reads it; the G6 clock report and the LT8 count read it for reports only". F10.10 (line 421) reads ts_event as the key of a trade set ("T records sharing one ts_event"), and F10.11 depends on that set; inherited from E.32 F3.10, and not a look-ahead (G1 counts the set by its batch end's ts_recv). The sentence is false as written: finding F3 |
| PR-S5 non-front records not dropped | FIXED | P1.2 rule (3) (149-150); DF34 lines 191-192 "83 of the 158,044,028 records ... on 14 dates" verified; feat33.py line 563 filters the front already |
| PR-S6 F10.7 zero denominator | FIXED | F10.7 row: "invalid if qb~ + qa~ = 0"; E.32 F3.7 (line 444) and M1 2.3(b) (162-163) say the same |
| PR-S7 F10 window changes not listed | FIXED | P2 F10 (260) and the list after the F10 table (426-430): OFI 1,5,15 -> 5,15,30; TI 5,15 -> 5,15,30; SW5 -> SW15; QI3 -> QIbar5, each with its reason; M1 2.2 (126-134) verified |
| PR-S8 F and R records | FIXED | 0.3 (71-72) and the F10 header (411-413): book updates are F_LAST records of any action, F and R included, as feat33.stream_mbp1 (any flagged F_LAST record is an update: code line 566). See NOTE F10 on the phrase "enter no T, C or M count" now that F10.9 counts state differences of any action |
| PR-S9 sourcing from M2 (e) | FIXED | P2 F09c (232, 239-243): "(e) for the prior only"; the residual from M2 (a).2 (M2 line 96: "Why rolling, never fixed physical weights: Janzen and Wang's weekly cash regression"), the origin split from M2 (a).1-2 (lines 70-78 and 102-105) and (d).4 (393-395: Avileis and Swanson; Janzen and Wang). F09p k = 30 from M2 (b).1 (line 194 "holds of 15-60"). Each cited passage exists and says what is claimed; none is an E.31 or E.33 result |
| PR-S10 OC-5 not a user decision | FIXED | Header (10-14), P2 (282-283), P11 (673): consistent (option A is this text; option B registered instead as an amendment under 0.2; N_before + 62 = 12 rules + 50 S_book configurations, E.32b recs line 625 "option B 62") |
| PR-S11 registration mechanics dropped | FIXED | P7.1 (494-499): one register call before any real-outcome fit, IDs <test>-<set><label><grid> (set+label+grid is 9 characters, inside the registry pattern's 16), freeze-file fields, require_registered after a restart; E.32 lines 685-701 verified; "the readings file" is defined in 0.2 (56-58) |
| PR-S12 own-price disclosure | FIXED | P1.5 (214-220): the identity -dO_k/(0.01 sigma_ZL sqrt k) = gR_k - b_S (0.25 sigma_ZS/(0.01 sigma_ZL)) rS_k - b_M (0.10 sigma_ZM/(0.01 sigma_ZL)) rM_k follows from L2.1-L2.9 as written (rS_k = dS_k/0.25/(sigma_ZS sqrt k), rM_k = dM_k/0.10/(sigma_ZM sqrt k), gR_k = [b_S dS_k + b_M dM_k - dO_k]/0.01/(sigma_ZL sqrt k)); verified algebraically |

NOTEs acted on, spot-checked against their sources: PR-N1 (E.32 G5 starts at line 383, G7 ends at 394: verified),
PR-N2 (DF34 lines 205-209: changes on 04-05, 04-07, 04-08, 04-09, 04-12), PR-N3 (abs of the median; invalid at 0),
PR-N4 (see F1), PR-N5 (both end marks need a usable bar), PR-N6 (E.32 lines 659-661 verified), PR-N7, PR-N8, PR-N10,
PR-N11, PR-N12, PR-N13 (see F9), MR-N1 (exact SR80 0.1958 recomputed), MR-N2 (recomputed), MR-N5, MR-N12 a (278 - h:
273/263/248/218), MR-N12 b (the reasoning holds: under a close-stamp convention the rule-B bar is one minute older,
never later), MR-N12 c (G1's timing rule is point in time under both conventions), MR-N13 (recomputed, exact). PR-N9's
claim that X's rules 2, 6 and 7 are tightened was not re-read against X section 3 (listed under not verified).

## New findings

### SHOULD FIX

**F1. P4 "Leader and crush inputs", V_X(15) (lines 380-383): the new wording shifts the bar window by a minute under
the protocol's own mark convention, and at the open picks a bar that does not exist.** 0.3 (as E.32 0.3, line 64-65)
defines the sample points of "the window of k minutes ending at t" as the marks t - j, j = 1..k. "The bars stamped
m - 1 min for the 15 minute marks m of the window" therefore reads as the bars stamped t - 16 .. t - 2: one minute
earlier than C.5's T-record window (t - 15, t] (line 371-372), and without the rule-B bar stamped t - 1. At t =
08:35 the marks are 08:30-08:34 and 07:35-07:44, so the literal bars include one stamped 08:29, inside the pause.
v0.1's "the 15 bars stamped t - 15 min .. t - 1 min" was unambiguous. Not a look-ahead (every bar is stamped at or
before t - 1 min under either reading), but a hidden choice inside L1.7. Replacement, lines 380-383: "V_X(15) in
L1.7 is, for each of ZL, ZS and ZM, the sum of its bar volumes over the 15 bars stamped at the minute marks t - 15,
..., t - 1 of the open-time axis (0.3): the bars covering the window (t - 15, t], the last of them the rule-B bar.
A window at 08:35 reaches back across the 07:45-08:30 pause to the bars stamped 07:35-07:44 and 08:30-08:34, as
C.5's T-record window does (ProtocolReview N4); one source type for all three legs (a change from M2 (f), which took
ZL's volume from its book). A missing bar contributes 0 to the sum."

**F2. 0.4 (lines 107-109): "P4.2's planted-proof figures 0.91 and 0.914 -> 0.90 and 0.905" also catches a figure that
does not depend on N.** E.32 P4.2 line 532 has two 0.91s: "P(at least 14 of 20) = 0.91 at a per-seed power of 0.8"
(a binomial: recomputed 0.913, unchanged at any N) and "P7.2's joint select-and-pass probability is 0.91 at a
realised daily Sharpe of 0.25" (N-dependent: 0.908 at N 838, 0.898 at N 1038). A literal mirror would misstate the
binomial. The pass criterion itself (14 of 20) is unaffected. Replacement: "P4.2's P7.2-derived figures, 'P7.2's
joint select-and-pass probability is 0.91 at a realised daily Sharpe of 0.25, and selection alone 0.914' -> 0.90 and
0.905 (0.898 and 0.905 at N 1038; ProtocolReview recompute_p7.out); P4.2's binomial figures 0.91 (P(at least 14 of
20) at a per-seed power of 0.8) and 0.26 (P(at least 2 of 20) at 0.05) do not depend on N and stay."

**F3. P1.2 (lines 150-152): "no feature, label, exclusion or fill reads [ts_event]" is contradicted by F10.10 (line
421).** F10.10 defines a trade set as "T records sharing one ts_event", and F10.11's refill is keyed to that set.
E.32 F3.10 did the same (M1 2.2 line 132), so nothing moved; the set is counted by its batch end's ts_recv (G1), so
this is not a look-ahead. The sentence is false and would fail its own audit. Replacement, line 150-152: "Dropping
reads ts_event. No feature, label, exclusion or fill reads it as a clock; F10.10 and F10.11 use it only as the key
that groups the T records of one trade set (E.32 F3.10), and the set enters a window by its batch end's ts_recv (G1).
The G6 clock report and the LT8 count read it for reports only (counts, no outcome; ProtocolReview S4)."

**F4. 0.3 (line 75): "(MBP-1 has no R record; E.33's code clears it at each F_LAST record)" states a wrong fact.**
DF34 line 144 ("R clear | 1") and line 151 ("Action codes seen: A, C, M, T, F, R (R once)") count one R record in the
ZL MBP-1 files, and the F10 header (line 411) says "F and R included". The rule is right (E.33's code, feat33.py
606, resets `batch_bad` at every F_LAST record and gives R no role); the parenthesis is wrong, inherited from M3
line 229-230. Replacement: "(the mark is per update: E.33's code clears it at each F_LAST record, and no record
type resets it otherwise; MBP-1 carries no clear-and-rebuild semantics, and DF34 counts one R record in the ZL files)".

### NOTE

**F5. P9.2 (560-562), P11 (667, 674): "at most about USD 1.66 for the definitions" is a median, not a bound.** 43 x
the median settled month 0.0385 = 1.66; the dearest settled three-parent month was 0.0506 (43 x 0.0506 = 2.18). "A
ZL-only request is a subset" bounds each month by its three-parent price, not by the median. Likewise "the 73 settled
ZM.v.0 ohlcv-1m monthly buys": 72 are whole months and one is a 20-day span (median over all 73, 0.0608; over the
72 commits, 0.0609). No decision depends on either ("the quote decides"). Replacement: "about USD 1.66 for the
definitions (43 months x USD 0.0385, the median settled month of the 39 three-parent ZM/ZS/ZL definition buys, of
which a ZL-only request is a subset; USD 2.18 at the dearest month, 0.0506)" and, in P11 and the closing line, "about
USD 1.66" for "at most about USD 1.66".

**F6. F10.9 row (420) and DC2 (454-455): "on a later C or M record" should say "of the same batch", and DC2 should
count the third case.** LT12 (449-450) already says "of the batch". If a post-fill reduction ever falls in a later
batch, both the v0.1 and the v0.2 form count the fill as a cancel (hand test C: 12 counted, true removals 0); M1
section 8 lists this as unverified. The definition is declared, so there is no hidden choice; the report should make
the limitation visible. Replacement for DC2: "DC2 per batch with a T at the touch, which record carries the post-fill
size reduction (the T record, a later C or M record of the same batch, or a record of a later batch; F10.9 is correct
in the first two cases and counts the fill as a removal in the third)".

**F7. F10.7 row: a change from an undefined touch is not classified.** When the bid side was empty (one-sided state)
and an order then rests, "the most recent change of bid_1" is neither an increase nor a decrease as written. Reading
it as an increase is exact (no order rested at a price above an empty side, so S_b = 0). Rare. Replacement, inside
the cell: "(a change from an undefined bid_1 counts as an increase)".

**F8. F10.9 row: T_b(p) is price-matched only.** In a locked state (bid_1 = ask_1 = p) a T at p is subtracted from
both sides' decreases; M1 2.3(c) kept the aggressor side ("sell aggressor, or side N at the bid price"), dropped in
v0.1 already. Rare (locked states are transient). Optional: "T_b(p) = the contracts of b's T records printed at p with
side A or N (bid), side B or N (ask)".

**F9. P9.2 (569-570): the recorded NOPA time governs the test calendar only.** E.32 rule 3 (lines 318-328) fixes R =
11:00 CT for every discovery release, and P3.6 rule 3 adopts it "word for word" for the discovery dates. If NOPA's
2017-2020 release time differs from 11:00 CT on some months, the two windows' rule-3 masks differ by construction.
Declared before any outcome, so not a leak; say it in P9.5 (regime differences) or in P3.6 rule 3: "the discovery
calendar keeps E.32's R = 11:00 CT for NOPA; the test calendar follows the recorded time (P9.2)".

**F10. F10 header (411-413): "F and R records are neither trades nor removals and enter no T, C or M count" can be
misread now that F10.9 no longer counts C or M records.** F10.9 counts the touch decrease over consecutive records
of any action, so an F record carrying a post-fill reduction enters D_b(p) (hand test B2: 3 removals, correct) and an
F_LAST F record is an OFI book update. Replacement: "F and R records are neither trades nor removals by themselves:
they enter no T count (C.5, TI_k, lam60's sv_i, T_b) and start no sweep or refill; their book states enter the
state differences of OFI and F10.9 like any other record's."

**F11. P2 F09p (251-252): "a larger test-window purchase than the ZM bars of P11"** is right in direction (a ZS MBP-1
test-window buy would be of the order of the ZL MBP-1's USD 23, against USD 1.46) but no figure is given; optional
"(of the order of the ZL MBP-1's USD 23.36 against USD 1.46)".

## Recomputation table (quoted | recomputed | match)

| Quantity (where) | Quoted | Recomputed (method) | Match |
|---|---|---|---|
| binding-threshold z (0.4) | 5.72 | 0.2028 x sqrt(796) = 5.7217; frozen functions at N 1038: G4 0.2028, z 5.722 | yes |
| K2 trigger (P10.2, L.f.3) | roughly T_test below 810 | 870 x (0.1957/0.2028)^2 = 810.15; exact with p7_final/p7_thresholds (G4 pinned at T_test 870, SR80_test recomputed at each T): SR80_test > G4 for T_test <= 810 (0.2029 at 810), not at 811 (0.2028) | yes, exact |
| dates lost (P10.2) | about 60 | 870 - 810 = 60 | yes |
| bar bounce (P2 F09p) | 2.25 ticks | sqrt(2) x 1.594 = 2.254 | yes |
| share of sigma_1 | 41% | 2.254/5.52 = 40.8% | yes |
| share of sigma_5 | 19% | 2.254/12.05 = 18.7% | yes |
| S_pool columns (0.4) | 43 | 14 + 8 + 9 + 12 (P4 headers: C 14, F09c 8, F09p 9, F10 12) | yes |
| SFI fits (0.4) | 258 | 43 x 6 | yes |
| fold counts a set (0.4, P10.3) | 180 / 120 | 5 x 6 x 6; 5 x 4 x 6 (E.32's 216 / 144 = 6 x 6 x 6; 6 x 4 x 6) | yes |
| select-and-pass, selection at s 0.25, N 1038 (0.4) | 0.898 / 0.905 (0.90 / 0.905) | extra_checks.py with the frozen functions: 0.8978 / 0.9050; rerun of the reviewer's script byte-identical to its recompute_p7.out | yes |
| E.32's figures at N 838 (for the substitution) | 0.91 / 0.914 | 0.9083 / 0.9145 | yes |
| exact SR80 (P7.2 note) | 0.1958 vs 0.1957 | bisection on s - z80 se(s, 870) = b_test: 0.1958; bar-se form 0.1957 (N 838: 0.1937 / 0.1936) | yes |
| tails at kurtosis 6-20 (P7.2 note) | about 1-3% | binding +1.3 / +2.6 / +3.2%, SR80_test +1.0 / +2.2 / +2.6% (skew 0 k 10; skew -0.5 k 6; k 20), N 1038 | yes |
| tails at skew -2, kurtosis 30 | about 11% (13% binding) | SR80_test +11.1%, binding +13.2% | yes |
| settled ZM.v.0 ohlcv-1m rows (P9.2) | 73, median 0.0608, max 0.0738 | ledger script, aggregates only: 73 settle rows (schema ohlcv-1m, symbol ZM.v.0, acct-2), actual_usd median 0.0608, max 0.0738, min 0.0432; spans 31 d x 42, 30 d x 24, 28 d x 4, 29 d x 2, 20 d x 1 | yes |
| ZM bars estimate | about USD 1.46; 1.77 at the dearest | 24 x 0.0608 = 1.459 (unrounded median: 1.4597); 24 x 0.0738 = 1.771 | yes |
| definition months (P9.2) | median 0.0385 | 39 settle rows, symbol "ZM.FUT,ZS.FUT,ZL.FUT", actual_usd median 0.0385 (max 0.0506, min 0.0288) | yes |
| definitions estimate | at most about 1.66 | 43 x 0.0385 = 1.656; dearest month 43 x 0.0506 = 2.18 (see F5) | arithmetic yes; "at most" no |
| total test purchase (P9.2, P11) | about 26.5 | 23.36 + 1.46 + 1.66 = 26.48; 0.5432 x 43 = 23.36 | yes |
| month counts | 24; 43 | 2017-05..2019-04 = 24; 2017-05..2020-11 = 43 | yes |
| option B count (header) | N_before + 62 | 12 rules + 5 labels x 10 settings = 62; E.32b recs line 625 "option B 62" | yes |
| LT13 decision minutes | 278 - h | 273 / 263 / 248 / 218 at h 5 / 15 / 30 / 60 = P3.7's counts | yes |
| non-front records (P1.2) | 83 on 14 dates | DF34 lines 191-192 | yes |
| flip dates (P1.4) | 2021-04-05..04-12 | DF34 lines 205-209 | yes |
| E.32 ranges cited by the edits | 383-394; 659-661; 685-701 | read: G5 at 383, G7 ends 394; P6.4 prop simulator 659-661; P7.1 685-701 | yes |
| FH maxima (P3.8) | 17 / 8 / 4 | floor((277 - h)/(h + 1)) + 1 | yes |
| e80 rows (P7.2, unchanged) | 0.97 / 1.94 / 3.74; 5.50 / 3.89 / 2.75 | 0.967 / 1.944 / 3.739; 5.500 / 3.889 / 2.750 | yes |
| P9.4 multipliers (unchanged) | 1.633 / 1.539 | 1.6329 / 1.5395 | yes |
| share of test dates without ZM (P9.1) | more than half | 495/870 = 57% (ProtocolReview's count) | yes |
| binomial in E.32 P4.2 (for F2) | 0.91 | P(X >= 14 \| 20, 0.8) = 0.913; P(>= 2 of 20 at 0.05) = 0.264 | yes |
| methods file (PR-S3) | five files concatenated unchanged | each of M1-M4 and L is a verbatim substring of reports/stage_e34_zl_methods.md; front has "Errata" 1-19 | yes |
| diff is the object | 318 lines | diff of v0.1 against the live protocol: 318 lines, identical | yes |

## Consistency checks (brief item 4)

- One bad-book reading everywhere: 0.3 (features, labels, exclusions, fills), F10 header, P3.2, P3.4 ("undefined mids
  ignored"), L.f.2, errata 4: all the batch form. No F_LAST-only sentence remains (grep "F_LAST record carries", "iff
  its F_LAST": none). Finding F4 is a fact inside the parenthesis, not a second rule.
- Run order equals cut order: P7.1, P10.3 and 0.4 agree (S_pool, S_crush, S_book, S_prop).
- FH versus TB caps: 0.5, P3.8, P7.2 (row label and note), P10.2 (K2 uses the measured nbar_c), L.f.1: consistent.
- ZM bars: P9.1, P9.2 (24 months, 2017-05-01..2019-04-30, requested to abut the owned 2019-05 chunk), P11 (two
  rows), the closing line: consistent; stop before the read if not bought appears in P9.1, P9.2 and P11.
- OC-5: header, P2 and P11 consistent (option A is this text; option B an amendment under 0.2; N_before + 62).
- The mirror list in 0.4 and the places it is applied (P4.2 proofs at P7.2's thresholds, P6.5 blocks, P10 cut rule,
  P8 at N_reg) agree; P7.2's values are unchanged against v0.1 (only the row label moved).
- G1's new timing rule (T records by their own ts_recv; batches by their F_LAST ts_recv) matches F10.4-F10.6,
  F10.9-F10.11 and feat33's trade count (lines 591-592).
- The bar-stamp note (0.3): correct under both conventions; DF34 line 58 reads the stamp as the open minute, so the
  run stage's hashed schema page is a confirmation, not a precondition.
- Brief item 6: no v0.2 sentence takes a P1.2 outcome file as its source. The edits cite DF34, the seal document,
  feat33.py (code, allowed by firewall rule 2), the spend ledger, E.32 and E.32b text, DECISIONS, M1-M4 passages that
  cite literature, the two reviews and recompute_p7.out (threshold arithmetic, no outcome). E.33's negative is cited
  only as an aggregate RETURN statement, unchanged from v0.1 and allowed by RULES 3.

## F10.7 and F10.9 hand tests (brief item 5; f10_hand_tests.py, no market data)

F10.7 (t = 10.0 s; "exact" = seasoned depth by order age): 1 rise-then-fall (B1 counterexample): v0.2 50, v0.1 0,
exact 50. 2 pure rise: 0 / exact 0. 3 flicker at the same price: 50 / 50. 4 rise-fall-rise: 0 / 0. 5 rise-rise-fall
(100 -> 101 -> 103 -> 101): v0.2 5, exact 0 (an upper bound, as the protocol claims; a tighter exact rule exists,
"bid_1(u) < bid_1(t) for some u in [t - 1 s, t] gives 0", but the declared rule is a valid bound and is not mine to
change). 6 ask improved: 0 / 0. 7 fall then new rise: 0 / 0. Point in time: every state used has ts_recv <= t.
F10.9 (bid side): A reduction on the T record: v0.2 3, v0.1 0, expected 3. B on a later M record: 3 / 3 / 3. B2 on
an F record: 3 / 0 / 3. C in the next batch: 12 / 12, true 0 (NOTE F6). D level consumed by a trade: 0. E cancel
empties the level: 20. F bad batch: 0. G fill, add, cancel in one batch: 4. H rise then cancel of the new level: 5.

## Not finished or not verified

- PR-N9 (rules 2, 6 and 7 "tightened against X's text"): X section 3 was not re-read; taken from the reviewer.
- The ZM.v.0 2019-05 raw chunk's first date (whether 2019-05-01 or later) is not on disk in any file I read; P9.1's
  "requested ... to the start of the owned 2019-05 chunk" covers either case.
- NOPA's 2017-2020 release time and the F-record semantics in MBP-1 stay [unverified] (no web; both reviews say the
  same); F10.9's hand test B2 shows the v0.2 form is correct if an F record carries the fill reduction.
- The seal's `status` behaviour on a new in-window ZM plaintext file (it "reports any in-window ZM, ZS or ZL
  plaintext that reappears ... and turns all_ok false", seal section 2) applies to the ZM bars exactly as it already
  applied to the ZL MBP-1 purchase in v0.1; the run stage's seal extension is not described in the protocol for
  either. Not new in v0.2; recorded for the lead.
- M4's moment table was reproduced from the frozen functions at N 838 and N 1038 (within 0.1 point of MathReview N2's
  percentages); M4's own simulation (P9.4 table) was not rerun.
- No market data, no outcome file and no E.33-family result file was opened; nothing here confirms a spread, depth,
  fill-reduction placement or bar convention on real records.
