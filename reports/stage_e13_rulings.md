# Stage E.13 rulings on the Fable review (reports/stage_e13_review.md)

Lead: Opus 5.5. Ruled 2026-10-04, from about 01:40 PDT. Review verdict: BLOCK (1 BLOCKING, 7 SHOULD FIX, 8 NOTE).
Every BLOCKING and SHOULD FIX finding is fixed below. The fixed files are reports/stage_e13_ranking.md (v3),
reports/stage_e13_prereg_ngrepl.md, reports/stage_e13_prereg_gexmom.md, reports/stage_e13_venues.md (and
reports/stage_e13_venues_part2.md), reports/stage_e13_info_sources.md (lead note), reports/stage_e13_phidias_question.md
and reports/stage_e13_STATE.md. Superseded ranking versions: reports/stage_e13_briefs/ranking_v1.md and
ranking_v2.md.

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| R-01 Top-two order rests on a tie criterion section 1 does not contain; C2's odds asserted | BLOCKING | ACCEPTED. Branch (i): section 1 is applied as written, with no tie criterion and no amendment. The review's derivation request (branch (ii)'s second half) is also met, so the primary key is a computed number for both candidates. Section 1's wording makes the primary key the deployment odds (row (b)). | C2's odds derived with the same structure as C1's (reports/stage_e13_briefs/c2_odds.py, .out): (a) 3.9% / 18.0% / 38% and (b) 0.8% / 5.0% / 15.4% (skeptical / central / optimistic). C1 (b): 1.8% / 6.6% / 14%. C1 leads on row (b) in the central and skeptical cases, so **C1 is first and C2 second**. Ranking section 5 rewritten; the ease check rewritten (the more expensive candidate ranks first); the recommendation is C1 (calendar probe first) with C2 as an optional companion. The process note lists all three versions with full hashes. |
| R-02 Negative-gamma share marked UNSOURCED, but the saved paper gives 48% | SHOULD FIX | ACCEPTED. | The quote ("2930 days with a negative NGE and 3158 with a positive one", 1996-2020) is cited in the ranking's power row and section 4, prereg C2 section 7, and INF's lead note, with the caveat that SqueezeMetrics' GEX is a different construction. Power at share 0.48 added (0.33 / 0.86 / 0.995). The 200-date stop is kept, stated as far from binding at 48%. |
| R-03 C2 income: per-MES label wrong | SHOULD FIX | ACCEPTED. | "$6.5-$15.6 net per MES per trade ($13-$31 for the two MES of a 50K)". |
| R-04 NG prereg names only half of the V24 question | SHOULD FIX | ACCEPTED. | Prereg C1 section 10 item 1 now names both computations on the 2019-2024 panel: the reload of the persisted OOF predictions (q), and the single full-panel M1 fit. The ranking's risks row says the same. |
| R-05 C2 evidence cell describes the unconditional result | SHOULD FIX | ACCEPTED. | The cell is split: conditional (S&P only, 1996-2020, in-sample) and unconditional (60+ futures, 1974-2020). Post-publication record: none for the conditional form; I-39 concerns the unconditional form. Section 5 item 2 reads the evidence at that strength. |
| R-06 C5 cost cell mislabels the Phidias fee | SHOULD FIX | ACCEPTED in substance, with a correction: the saved pages DO use "Lifetime" (the TOU's "LIFETIME PAYMENT" table; the rules page's "CASH Account Activation Fees ... Lifetime"). They show the $149-$169 is the one-time CASH-account activation fee, not an evaluation price. | The ranking's C5 cell and the VEN Phidias row (merged and part 2) now read "CASH-account activation fee $149 / $149 / $169, a one-time ('lifetime') payment ...; evaluation price UNSOURCED". |
| R-07 C2 prereg: no rule for unsourced calendar dates; a second statement of c | SHOULD FIX | ACCEPTED. | Prereg C2 section 3 adopts C1's ruling C12: exclude and count unsourced dates; stop before the purchase above 2%. Section 4 is the only statement of c (2.038 MES ticks). The ranking's sentence now points to it. |
| R-08 First-version hash cannot be checked | SHOULD FIX | ACCEPTED. | v1 was reconstructed byte-for-byte and verified against its recorded prefix: full sha256 e4106799b27819720155833b6a3e128b3215ee440f5a0e963eda011f036297fe, reports/stage_e13_briefs/ranking_v1.md. v2 is kept: dcba2f0a7c84b27bdaeb4201fcacc5e84dbb718f5ee0b98dacfed7cc996cc594, ranking_v2.md. Full hashes are in STATE and the process note. |
| R-09 "A third of today's level" does not give 0.11 sigma | NOTE | ACCEPTED. | The level is stated as 27-33% of today's (about 2,100-2,600, unsourced); the cost is 0.08-0.11 sigma and the bar 0.13-0.17 sigma, in the ranking and prereg C2. |
| R-10 AiTrader day-count convention | NOTE | ACCEPTED. | "Counting 2026-07-28 as day 1" added; day 0 gives 2027-01-19. |
| R-11 Scrapling deviations: two workers, not three; InfoSource's Firecrawl order | NOTE | ACCEPTED. Ruling: a fact from a deviation fetch stands only on a compliant corroborating copy. Otherwise it is marked "deviation fetch". | Marked: P1-19, P1-21, P1-37 and Lucid's TOU (VEN section 5, the lead summary's ETF bullet, the question file's section 4). No classification rests on them alone. The count is corrected in the open choices. INF's lead note records the Firecrawl order deviation. |
| R-12 The C10 stop reads test bars; what does a stop end? | NOTE | ACCEPTED, strict branch. | Prereg C1: a C10 stop closes the registered attempt. Any calendar fix and rerun is a new registration with N counted again. |
| R-13 Power uses the 8.90-year span | NOTE | ACCEPTED. | The ranking's power cell adds about 3.29 and 0.91 for the ruled window (the prereg already gave the 0.97 scale). |
| R-14 The 12% headline is a midpoint | NOTE | No change needed. | The ranking's row (a) now shows the annex's cases (16.5% / 7.1% / about 35%) beside the headline. |
| R-15 Minor citation slips | NOTE | ACCEPTED. | 4.82 years cited to NGR section 9; "47.9 a year, rounded" for 50 trades. The ES estimate label was already right. |
| R-16 Things not found wrong | NOTE | Recorded. | none |

## What changed in the verdict

The order of the top two returns to C1 first, C2 second. That is the order of v1, but it now rests on section 1
applied literally and on computed odds for both candidates, not on v1's undeclared tie-break. Every other rank is
unchanged. The recommendation:
1. pause until the AiTrader readout; or, if the user keeps searching,
2. C1, with its one-session calendar probe first, and C2 as an optional companion that shares the equity calendar
   and the harness change.

## Follow-up check

The C2 odds are new numbers that enter the ranking. RankingReviewer-FableXHigh was asked, through a short
follow-up to the same review (no new spawn), to check c2_odds.py, its output, the C1 row (b) figures and the R-01
ruling. Its answer is recorded below.

**Follow-up verdict (reports/stage_e13_review.md, "Follow-up check (2026-10-04)"): R-01 CLOSED.** Section 1 is
unchanged and applied with no tie criterion; both candidates' odds are derived; the v1 hash matches. The reviewer's
scipy recomputation reproduces every C2 and C1 odds cell. R-02, R-03, R-04, R-06, R-07, R-08, R-10, R-12 and R-13 are
CLOSED, checked in the files. The reviewer agrees that the lead's "Lifetime" correction on R-06 is right and its
own original statement was wrong. Overall: APPROVE WITH FIXES, once R-17 is applied. Three new findings:

| Finding | Grade | Ruling | Fix |
|---|---|---|---|
| R-17 Section 5 must disclose that the C1/C2 order depends on the row-(b) reading and the chain asymmetries | SHOULD FIX | ACCEPTED (disclosure; no input changed). | Section 5 now gives why row (b) is the reading, the row-(a) order (C2 first in two of three cases), the reversal thresholds (C2 persistence 0.46 against 0.35 used; C1 factor below about 0.76 of its value), C2's missing forward-test factor, and that the recommendation is the same either way. |
| R-18 The central P(pass given present) is share-independent by construction | NOTE | ACCEPTED. | Section 4 says (a) depends on where the bar sits in the assumed mean range, and that the identical share lines are by construction. |
| R-19 The absent term includes the cost bar for C2 but not for C1 | NOTE | ACCEPTED (disclosed; immaterial). | Section 4 states both conventions; the t-bar-only term gives C2 central (a) 0.188 instead of 0.180, with no order change. |

With R-17 applied, every BLOCKING and SHOULD FIX finding of the review and its follow-up is fixed.
