## 5. Verification

Every number entering a verdict was checked by a Fable worker that did not produce it (each model confirmed from its
transcript: claude-fable-5-1).
- FactAuditor-FableXHigh (F4, 01:35-03:26): every value that feeds a score PASS (0 wrong values across 47 codes, 5
  firms, 235 pairs, S_mean, IBKR and cross-family checks); blinding FAILED twice (B1: Lucid plan names in four items;
  B2: the MFFU name in one quote), both patched before rater 2 rated the FINAL3 sheets; S1-S4 handled (the HG
  erratum, the IIP lines, sizes and ticks removed from items, SIL left as ruled).
- RankingReviewer-FableXHigh (RV1, Step 4, 06:58-07:25): PASS; 0 BLOCKING, 3 SHOULD FIX, 13 NOTE. It recomputed every
  Layer 1 and Layer 2 score, gate, S, tie and rank (46 scored codes, 103 ranked pairs) and all 28 variants' top 5 and
  MNQ ranks with exact fractions; reran F3 on MCL, 6E and ZC byte for byte inside the window discipline (guards OK
  before and after, unlocks 0); confirmed the blinding (rater 2 rated FINAL3; no code, firm or platform name in its 819
  reasons) and the unknown rules; matched econ inputs to F3 and F4 for 112 pairs x 3 blocks.
- RecsReviewer-FableXHigh (RV2, R5 and F5, 06:58-07:20): PASS WITH ONE RULING NEEDED; 1 BLOCKING, 6 SHOULD FIX, 7
  NOTE. It recomputed R3 for 185 combinations in five runs (Q4-Q7, C, order, R4, own broker) and F5 for 8 rows,
  checked the closed-line overlaps against the frozen code, and found no outcome read. B1 (the F09 candidates' Q3
  rested on an incomplete closed-line fact) was ruled as LR-Q3b (family level), which drops RTY F09 from the R4 and
  adds the EQ3 F08 pool.
- Session-4 fixes: RV1 S1-S3 and N1-N2 by ScoreFixer (score rerun 08:51:03 with no score, gate or rank change; 178
  tests pass); RV2 B1 (text) and S6 by R1Fixer, which also corrected three of RV2's own statements against the code (no
  MES lead in E.12, MBT live for two months, Family B a pooled ridge); RV2 S1-S3 and S5 by the lead; S4 by the
  RecsAssembler; RV2 N1, N2, N5 and N6 addressed in the text.
- FixVerifier-FableXHigh (09:23-09:41): PASS; 0 BLOCKING, 0 SHOULD FIX, 7 NOTE. With its own scripts it reproduced
  the run-2/run-3 identity, all six r3 runs from the spec 8.3 text, the LR-Q3b patch's scope (exactly C112-C116 and
  C138-C139), the EQ3 arithmetic, every number in the lead's session-4 text, all 75 cells of the E_dir table and the
  six claims of its reading, the G17 facts against the frozen code, and 105 lead lines verbatim. The lead then applied
  six of its NOTE fixes (wording, timestamps, attribution: the reviewer's proposed text; not re-reviewed).
- Inter-rater agreement: 302/329 exact (91.8%); D6 23/47 (rater 2 reads samples spanning 2010 as not "on data after
  2010").
- Not verified: the full texts behind the evidence rows were not re-fetched by RV2 (no web access); the drafter's
  published-effect translations (F10.E01 R2 to 0.058 sigma; F01.E02 to 15.5%) are arithmetic under stated
  assumptions; the econ32b.json read by the 05:40:30 run (0567890e) is not on disk, so its blocks are inferred
  unchanged from the identical scores; p7_final.py's power was not rerun for the pooled 273-date case (the "far below
  80%" statement rests on an interpolation from recorded values).
