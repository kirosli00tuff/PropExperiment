# RecsAssembler-OpusXHigh report (Stage E.32b wave F, section F3 and its 08:58 addendum)

Worker: RecsAssembler-OpusXHigh (Opus 5.5, xhigh), session 4, 2026-10-29 08:57-09:21 PDT (times from `date`). Holdout
status at start and end: unlocks_logged 0 in every block. No data file, no Databento call, no TopstepX, no commit. Read
by section only. Brief: briefs/brief_wave_f.md header, F3 and "F3 addendum (lead, 08:58)".

## Files written (and only these)

| file | sha256 (first 16) | what |
|---|---|---|
| reports/stage_e32b_briefs/work/R4/draft_sections_v2.md | 23e311cbc2360a2c | copy of draft version 2, made first |
| reports/stage_e32b_briefs/work/R4/recommendations_s3.md | efd73f15039d8b27 | copy of the session-3 recommendations file, made first |
| reports/stage_e32b_briefs/work/R4/draft_sections.md | c90c0d4c6e31be91 | version 3 (834 lines) |
| reports/stage_e32b_recommendations.md | fcb8feb66e2108f8 | rebuilt (1,242 lines) |
| reports/stage_e32b_briefs/work/fix4/recs/scripts/ | - | build_draft_v3.py, assemble_s4.py, their text inputs (header_v3.md, s0_L11.md, s1_r4list.md, s6_eq3.md, s7_c141.md, s9_sens.md, rty_overlap.md, sec0_body.txt, sec_lc.txt) and renum_log.txt (the 42 cross-reference renumberings, each with context) |

Both files are generated: build_draft_v3.py rebuilds draft v3 from draft_sections_v2.md (every replacement exact and
count-checked; a rerun reproduces the same sha256), and assemble_s4.py builds the recommendations file from
lead_sections.md (verbatim), draft v3 and the JSON outputs (tables generated, not typed).

## 1. Draft v3 (work/R4/draft_sections.md), changes by section

- Header: version 3 note, inputs with current hashes (r3_out.json d3812c40..., R2_combinations.json bdbce3ae...,
  q3only, nozlw, ts150_v2, q3bleg 21ccabbb..., v1, F5_holding.json, SR80.json, the updated R1 files, RULINGS, the R1 fix
  report, REVIEW_recs).
- Section 0: L1-L10 kept as the record. L7: "(sections 4-5)" -> "(Appendix B and section 4)", "only unread ... stretch"
  -> "longest unread ... span" with 2026-06-17 onward, and a version-3 note (C113 left the R4; C147 reads the same NQ and
  RTY span). L10 (ii): the ts150 parenthesis now cites r3_out_ts150_v2.json (C072 2.40, rank 22; C147 2.40). New L11:
  RV2 B1, R1Fixer's verified G17 facts (live leads ZN, 6E, CL, GC, ZC on M2K/RTY and NQ, ZN, 6E, CL, GC on ZL; E.12
  also g17_mbt from 2024-01-02; g17_mes excluded by P-1a; Family B one pooled ridge per horizon; E.20 decision times
  09:00, 11:00, 13:00 and t4 14:08 CT on equity), the lead's resolution LR-Q3b with its effects (C138 2.75 -> 2.65,
  C139 2.60 -> 2.50, C113, C112, C115 2.60 -> 2.50, C114 2.45 -> 2.35, C116 2.15 -> 2.05; C147 enters; C141 best own
  broker) and LR-OF.
- Section 1: the R4 list verbatim from r3_out.json (C140, C138, C072, C021, C147; own broker C141), ties, Q3 and Q7
  notes, grouping: Program 1 = C140 ZL F10 + C138 ZL F09 (one sealed read, F10 first), Program 2 MNQ F08, Program 3 YM
  F08, Program 4 EQ3 F08; RTY F09 to Appendix B.
- Section 2 (skeleton): the closing V51 sentence renumbered for Programs 2-4.
- Section 3 (Program 1): heading reordered; fact table with C140 first and C138 second (C 2.65 (2), Q3 1 with the
  LR-Q3b reason quoted from R2_combinations.json and the rater's Q3_rater quoted in full: fixes draft :187); C140's Q3
  quote kept with a bracket: R1-11 and R1-15 held G17 on ZL, other families for F10 (LR-OF); Q4-Q7 row and "same pair
  elsewhere" (C141 2.60, C139 2.50) rewritten. The "ZL in other families' closed lines" bullet (draft :207) replaced by
  the lead's LR-OF wording, verbatim from the addendum. Outline P1 lists the book first and adds the G17 exposure of
  the discovery dates; P2 lists F10 first and adds F09's stated difference from R1-11/R1-15 (leaders ZS and ZM, never
  G17 leads; 15-60 minute band against h60-hF). Data plan rows reordered (F10 first). 3(d) unchanged.
- Sections 4 and 5: version 2's MNQ (5) and YM (6) renumbered as Programs 2 and 3; r3 ranks updated (C072 4, C021 5);
  cross-references fixed (4(b) P1, 4(a), 4(d), Appendix B(b) P1); YM's "same pair elsewhere" adds C147.
- Section 6 (new, Program 4, C147 EQ3 F08): (a) member table (c_f, sigma_30, c_f/sigma, K, trades a year, pooled e80
  = q x sigma_30: YM 10.00, MNQ 23.26, RTY 8.18 ticks; single-member e80 12.24, 28.48, 10.02; Q6 per member 4;
  Standard-Path payout facts; MLL ratios; news; clean test window YM 0 under LR-V31 (106.97 before), MNQ 0.82, RTY 0.0;
  the unread 2024-03..2025-03 and 2026-06-17 onward stretches; schema and cost) and pool table (Q1-Q7 with reasons,
  K_total 2,610, K_eff 1,305 at rho 0.5 with no measured pair, q 0.1581, prop fit incl. the members' combined one-day
  sigma at rho 0.5: USD 544.45, MLL ratio 3.67, arithmetic; other EQ3/EQ3m pools; sensitivities); closed-line overlap;
  (b) outline (one registration, members pooled, F08 at 15-30 minutes, h_c 30; P9 says how the pool is cut to MNQ and
  RTY under LR-V31: K_eff 1,160, q 0.1677, Q5 still 2 at the 870-date design; about 364 on 273 dates; the lead's K0
  re-score; disjoint windows if both conditions were granted); (c) data plan with the quote requests (no YM request
  under V31; NQ and RTY 2024-03..2025-03 only with the V51 approval); (d) kill-criteria facts.
- Section 7: C141 ZL F10 at IBKR (C 2.60, rank 3): Q1-Q7 with quotes, Q6 3 = margin deduction 0 (USD 4,661.63
  against USD 6,000 u) + sigma_day deduction 1 (USD 701.05 > USD 120), c_f 2.503, power, fit, data, other own-broker
  rows, capital (V32); one line: C139 ZL F09 at IBKR is 2.50 (rank 21) under LR-Q3b. Outline/data and kill-criteria
  facts adapted to F10 (S_book's 50 configurations if selected separately).
- Section 8: the short-window sentence renamed for the new programs.
- Section 9: rewritten from the current files: a generated table (file hash, rulings, R4 1-5, best own broker with
  rank, reach 2.00) for primary, q3only, nozlw, ts150_v2, q3bleg, v1, and one note per run. ts150_v2: n_reaching_2 = 5,
  fewer_than_3_reach_2 = false, the printed line is the label with its value (RV2 N1); its R4 is C140, C138, C021,
  C075, C108 (C072 and C147 fall to 2.40 through MNQ's Q6 3).
- Appendix A unchanged. Appendix B (new): version 2's RTY section with an intro (Q3 2 -> 1, C 2.60 -> 2.50, rank 3 ->
  18), C (r3 rank) row updated, Q3 row (LR-Q3b value and the rater's value described with its statement marked as
  corrected; draft :304), "same pair elsewhere" updated, the closed-line overlap paragraph rewritten (draft :316,
  :318-319: R1-11 G17 leads ZN, 6E, CL, GC, ZC on M2K, MBT from 2024-01-02, NQ never applied; R1-15 the same five among
  its 36 frozen features, decision times 09:00, 11:00, 13:00 and t4 14:08 CT), P1.5 and P2 additions.
- Section 10: references renumbered; one version-3 limit added.

## 2. Recommendations file (reports/stage_e32b_recommendations.md), changes by section

| section | change | words |
|---|---|---|
| header | session-4 assembly note | 102 |
| 0. Summary | rewritten from the lead's session-4 text and r3_out.json (RV2 S4): R4 in order with C, priors, K0-K4 one line each, stop rule, D1-D4 | 298 (limit 300) |
| 1. R1 | table regenerated from R1_closed_lines.json; R1-11 and R1-15 rows carry the cross-market content (step-5 :46, :50; RV2 S6), and the two session-4 bullets are quoted verbatim below the table; the patch docstring block regenerated (now has the q3bleg line); new block quoting RULINGS.md LR-Q3b, its detail and LR-OF | 2,115 |
| 2. R2 | counts and product line regenerated (identical to session 3); errata list adds LR-Q3b and R1Fixer's session-4 edits | 879 |
| 3. R3 | regenerated: primary-run line (07:19:31; 185, 159 eligible, 26 gated, 133 at C >= 2.00), top 20, 3.1 gated list (identical to session 3) with a line that LR-Q3b set no gate, 3.2 = draft v3 section 9 (all five sensitivity runs) | 2,202 |
| 4. R4 | 4.0 R4 list and grouping (draft v3 section 1); 4.1 lead base rates (verbatim); 4.2 L1-L11 (L11 = RV2 B1 with LR-Q3b and LR-OF); 4.3 skeleton; 4.4 thresholds; 4.5 ZL program (lead text + draft 3(a)-(c), step-5 :465 and :485 fixed); 4.6 MNQ and YM F08 (lead text + draft 4-5); 4.7 EQ3 F08 pool (lead text + draft 6(a)-(d)); 4.8 the lead's dropped-RTY note (tables in the Appendix); 4.9 the lead's F01 note + draft Appendix A | 11,047 |
| 5. Non-prop | lead paragraph (verbatim) + C141 fact table, outline and data, kill-criteria facts | 827 |
| 6. Stop rule | lead text (verbatim) | 200 |
| 7. Decisions | lead text (verbatim) | 185 |
| 8. Sources | hash table regenerated (adds q3bleg files, patch script, F5_holding.json, SR80.json, both score outputs, RULINGS, REVIEW_recs, both fix reports, recommendations_s3.md); score paragraph: both hashes (05:40:30 run 70809d501bf316c1 kept as work/score/score32b_out_run2.json; 08:51:03 run ee74c6a0aa508ae9), R2 took only the top-15 list, identical in both runs (checked); scripts incl. patch_v31_q3_lead.py's q3bleg mode, R2_combinations_q3bleg.json, r3_out_q3bleg.json and LR-Q3b; limits | 584 |
| Appendix | dropped RTY F09 tables (draft v3 Appendix B: step-5 :568, :580, :582-583 fixed) | 1,617 |
| Lead check | new, against the session-4 lead text | 515 |

Total 20,574 words, 1,242 lines. Lead text check (script): all 104 non-heading lines of lead_sections.md from "## Base
rates" on appear verbatim, and each of its 10 section bodies appears as one contiguous block. Section numbers were
prefixed to the lead's candidate headings (### 4.5 1-2. ..., as in session 3); no lead word was changed.

## 3. Lead check (as written into the file)

Numbers and facts in work/R4/lead_sections.md checked against the files; nothing in it was changed; none of the
differences changes a score, rank or prior.

1. Candidates 1-2 ("60-minute leads from five other asset classes (NQ, ZN, 6E, CL, GC) on ZL") and the dropped-RTY
   note ("ZN, 6E, CL, GC and ZC on M2K and RTY"): E.12 also had g17_mbt (bitcoin, a sixth class), live on M2K and ZL
   rows only 2024-01-02..2024-02-29 (R1_closed_lines.md R1-11 cross-market bullet; RULINGS.md LR-Q3b detail;
   r1fix_report F3). E.20 had no MBT lead. "RTY in E.20" is right as to the root; E.20's vehicle was M2K (F4).
2. Candidates 3-4: "MNQ: read by E.20 and E.21". F2_data_access.json codes.MNQ.read_windows also lists r002-E16 (NQ
   2010-07-01..2024-02-29), r003-C1b (NQ feature leg 2010-07-01..2019-04-30) and r008-E23 (NQ 2011-07-27..2019-04-30).
   Carried from the session-3 check (item 6).
3. D4 ("13 unread months"), the dropped-RTY note and the EQ3 prior ("273 unread dates"): 2024-03..2025-03 is the
   longest unread span; 2026-06-17 onward (about 4 months) is also neither owned nor read. Wording only.
4. Stop rule item 1 "(far below 80% even pooled)": no pooled power is in the files. Arithmetic: the MNQ+RTY pool at rho
   0.5 has a per-date Sharpe 1.155 times a member's (0.194 -> 0.224); p7_final.py's power at about 273 dates (N 846;
   recommendations_s3.md Lead check item 9) is 0.05 at 0.194 and 0.23 at 0.25, so about 0.1-0.2: consistent, not
   computed.

Checked and consistent: the 23/838/17 base counts, 4% and 1/19; D2 b 42 of 47 own ratings (F4_blind_unmasked.json;
MZC, MZS, MZW, MZL, MZM 0.5) and 46 of 47 as scored (score32b_out.json layer1; NQ unscored); every ZL, YM, MNQ, EQ3,
RTY, F01 and C141 number in the lead text (listed with file and field in the file's Lead check).

## 4. Step-3 grep counts (reports/stage_e32b_recommendations.md)

| pattern | count |
|---|---|
| "12.3 ticks" | 0 |
| "not a small-cap lag" | 0 |
| "priors of 1.5-4%" | 0 |
| "about 1.5% each" | 0 |
| "final build only if" | 0 |
| "no cross-market configuration" | 0 |
| "measured no correlation" | 0 |

The same seven give 0 in draft v3; "late-session" gives 0 in both. No quote of a corrected statement was needed: the
rater's RTY Q3 sentence is described ("its statement that no closed line held a cross-market feature on RTY or M2K is
corrected by LR-Q3b"), not quoted.

## 5. RV2 items covered

S1 (YM 12.2): in the lead text; no "12.3" left; the draft prints 12.24. S2 (F09.E06 both lags): in the lead text; the
old phrase is gone. S3 (priors "under 1% to about 4%"): in the lead text; the old phrase is gone. S4 (Summary):
rewritten. S6 (R1-11/R1-15 cross-market content): in the R1 table rows and quoted under it; the step-5 passages of both
files corrected. N1 (ts150_v2 label): stated in section 3.2 / draft 9.

## 6. For the lead (not decided here)

- patch_v31_q3_lead.py's docstring still says "q3only (LR-Q3a only: the narrow V31 reading)", but the code applies
  LR-Q3b in every mode except q3bleg (line 31: `mode != "q3bleg"`), so q3only carries LR-Q3a and LR-Q3b. The files
  here state the rulings each run actually carries. The script is read-only for me.
- EQ3 pool: R2_combinations.json C147 data.all_data_cost_usd 4.26 is YM's 2015-10..2019-04 purchase, which LR-V31
  forbids; the file keeps the value (no score effect: Q7 uses the clean window, 0). The two-member numbers (K_eff
  1,160, q 0.1677; about 364 on 273 dates) and the members' combined one-day sigma are arithmetic by the scorer's
  formulas, not a re-score; how a pooled test would be read if YM (test before 2019-05) and MNQ/RTY (after 2024-03)
  were all admitted is a design question left open.
- LR-OF's wording is used verbatim; it lists the ZL G17 leads without E.12's two-month MBT lead (Lead check 1).
- The draft-v3 P4 grid for the pool (Program 2's 8 or 4 configurations with shared parameters) is a draft proposal,
  as every grid in the file.

## 7. Not finished or not verified

- Nothing in the brief is left undone. Not checked by a second model: the EQ3 arithmetic (6(a), 6(b) P9, 6(d)), the
  combined one-day sigma, and the Lead check's pooled-power interpolation.
- The brief named B/SR80.json; the file is B/work/F5/SR80.json (read there; SR80_test 0.19362508 matches r3_out.json).
- F5_holding.json's h-30 fields for YM, MNQ and RTY are continuous-family values (n_cap 13, 3,276 trades a year); the
  F08 tables use the daily-family values from combos_detail (K_year 252) and say so.
