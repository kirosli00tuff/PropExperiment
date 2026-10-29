# E.34 protocol fix log: DRAFT v0.1 -> v0.2 (lead Opus 5.5 max, session 3, 2026-10-29 15:14-15:26 PDT)

v0.1 snapshot: review/protocol_v0.1.md (sha256 c49b4aef...). Diff: review/protocol_v0.1_to_v0.2.diff (318 lines).
The edits were applied as 42 exact-once replacements plus the header and sources edits. No P7.2 threshold changed;
N stays 838 (nothing registered). Part M worker files M1-M4 are not edited; their corrections are the errata of
reports/stage_e34_zl_methods.md, and lead rulings are L.f in L_lead_reconciliations.md.

## BLOCKING (4; MathReview S2 = ProtocolReview B2)
| Item | Fix and where | Declared choice or number changed |
|---|---|---|
| MR-B1 F10.7 zero rule wrong on a rise-then-fall second | P4 F10.7 row: qb~ = 0 only if the most recent change of bid_1 in (t - 1 s, t] was an increase (ask: a decrease); LT12 hand test of the counterexample | yes: feature definition |
| MR-B2 F10.9 fill attribution wrong if the post-fill reduction sits on the T record | P4 F10.9 row: per batch, decreases at p over every consecutive record pair of any action minus the batch's T lots at p, floored at 0; bad or one-sided pairs contribute 0 and are counted; DC2 reworded (report only); LT12 tests both placements | yes: feature definition |
| PR-B1 ZM test bars not owned before 2019-05 | P9.1 (owned ZL/ZS 2017-04..2020-11, ZM 2019-05..2020-11; buy ZM.v.0 ohlcv-1m 2017-05-01..2019-04-30 with the test data; stop before the read if not bought); P9.2 quote list and estimates from the spend ledger (ZM bars about USD 1.46; definitions at most about USD 1.66; about USD 26.5 in all); P11 rows split; P2 F09p wording; BRIEFS RULES fact corrected; L.f.4 | yes: run-stage data plan |
| PR-B2 (= MR-S2) two bad-book rules | 0.3: one reading for features, labels, exclusions and fills, E.33 FA-4 (any record of the batch), mark for that update only; P4 F10 header; P3.2 (MBP-1 labels in both windows, same code); L.f.2 | yes: declared reading (M3's F_LAST-only form superseded) |

## SHOULD FIX (16)
| Item | Fix and where | Changed |
|---|---|---|
| MR-S1 (with PR-N8) 20-cap binds for TB | 0.5, P3.8, P7.2 row and notes (FH caps; TB realised; K2 measured form governs); L.f.1 | wording |
| MR-S3 M2's 12:50 CT cap in the option-B rule grid | header OC-5 line (option B on L.c's grid, no 12:50 cap); methods errata | option B only |
| MR-S4 bar bounce omits sqrt 2 | P2 F09p: 2.25 ticks, 41% of sigma_1, 19% of sigma_5 (was 29% of sigma_1); methods errata | text number; k = 1 still dropped |
| PR-S1 two run orders | P7.1 run order S_pool, S_crush, S_book, S_prop, then labels, then the P5 grid; P10.3 cut in P7.1's order | declared order (E.32's mirror) |
| PR-S2 mirror substitutions incomplete | 0.4 counts and names list (200, set names, 43 columns, N_reg, z 5.72, blocks, 258 SFI fits, 180/120 folds, run order, labels, 0.90/0.905) | inherited numbers made explicit |
| PR-S3 methods file missing | reports/stage_e34_zl_methods.md assembled before the freeze (T5); sources line | no |
| PR-S4 ts_event reads | P1.2: no feature, label, exclusion or fill reads ts_event; G6 and LT8 read it for reports only | wording |
| PR-S5 non-front records not dropped | P1.2 drop rule (3), counted (DF34: 83 records on 14 dates) | yes: drop rule (E.33's code already filters) |
| PR-S6 F10.7 zero denominator | F10.7 row: invalid if qb~ + qa~ = 0 | yes: invalidity rule (E.32 F3.7's) |
| PR-S7 F10 window changes not listed | P2 F10 and a list after the F10 table with reasons | listing only |
| PR-S8 F and R records | 0.3 and F10 header: book updates are F_LAST records of any action; F and R enter no T, C or M count (E.33 code) | reading |
| PR-S9 sourcing from M2 (e) | P2 F09c citation and sources of the two additions; F09p k = 30 reason | sourcing only |
| PR-S10 OC-5 not a user decision | header decision list; P2; P11 | adds a user decision |
| PR-S11 registration mechanics dropped | P7.1: E.32 P7.1 mechanics with ID pattern, freeze fields, require_registered | yes: mechanics (E.32's) |
| PR-S12 own-price disclosure | P1.5: the linear identity and what E3 removes | wording |

## NOTEs acted on
PR-N1 G5-G7 lines 383-394; PR-N2 flip dates 2021-04-05..04-12; PR-N3 lam60 normalised by abs(median), invalid at 0;
PR-N4 V_X(15) on the open-time axis; PR-N5 bar sigma needs bars at both ends; PR-N6 Tier A prop simulator kept
(P6.4); PR-N7 LT8 "changes no rule"; PR-N9 firewall wording; PR-N10 two independent implementations required (G7);
PR-N11 invalid-by-construction shares reported (LT11, P10.5); PR-N12 bar files hashed once before any read; PR-N13
NOPA release time recorded per month; PR "not finished" (bar instrument_ids on rolls): G2 rule. MR-N1 SR80
convention note; MR-N2 tail adjustment 1-3%; MR-N5 drop overlaps reported (P1.2; L.f.5); MR-N12 a (LT13 DST), b (0.3
bar-stamp note: rule B cannot look ahead under either convention), c (G1 timing of trade counts and batches); MR-N13
K2 trigger about 810 dates (P10.2; L.f.3). Not acted on in the protocol (methods errata only): MR-N3, N4, N6-N11, N14;
PR-N14 needs no change.

## Round 2: FixVerify on v0.2 (PASS WITH FIXES) -> FROZEN v1.0 (lead, session 3, 15:44-15:48 PDT)
FixVerifier-FableXHigh (claude-fable-5-1): 4 BLOCKING fixed; 16 SHOULD FIX: 15 fixed, 1 partly (PR-S4, closed by
F3); 32 of 32 recomputations match; no new leak; new items F1-F4 SHOULD FIX and F5-F11 NOTE. All eleven applied in
the verifier's own replacement wording (18 exact-once replacements, scratchpad apply_v10.py; v0.2 snapshot
review/protocol_v0.2.md; diff review/protocol_v0.2_to_v1.0.diff): F1 V_X(15) = the 15 bars stamped t - 15 .. t - 1 on
the open-time axis, a missing bar adds 0; F2 0.4 keeps P4.2's N-free binomial figures (0.91, 0.26); F3 ts_event is a
trade-set key in F10.10-F10.11, never a clock; F4 the per-update bad mark without the wrong "no R record"; F5 the
definition and ZM-bar estimates are medians (dearest months USD 2.18 and 1.77; total 27.3); F6 "of the same batch"
and DC2's third case; F7 a change from an undefined touch counts as an improvement-side change (bid increase, ask
decrease); F8 T_b(p) side-matched (A or N on the bid, B or N on the ask; M1 2.3 c); F9 NOPA time: discovery keeps
11:00 CT, the test follows the recorded time (P3.6 rule 3, P9.5); F10 F and R records' book states enter OFI and
F10.9 differences; F11 the ZS-book purchase order of size. No third review round (OC-28).
