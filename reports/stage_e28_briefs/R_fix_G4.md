# R_fix_G4: fix log for R_math_G4.md (BriefFixer, Stage E.28 group G4)

Files edited: C2_Control.md, C2_StatsRMT.md (each with a closing "Corrections after review" section). No other file touched. Scripts under work/ and JSON were not edited (outside the brief).

| ID | Severity | Status | One line |
|---|---|---|---|
| MG4-01 | SHOULD FIX | applied (text); script fix needs lead | C2_Control gamma thresholds replaced with exact bounded values; C2_threshold.py (sigma applied twice) not edited |
| MG4-02 | SHOULD FIX | applied | q = 5 drift attributed to the Q = 10 bound; Gueant quote attached to bounded case |
| MG4-03 | SHOULD FIX | applied | ORCL range split into Table 4 (11.65 to 34.25) and Table 5 (11.75 to 33.29) |
| MG4-04 | SHOULD FIX | applied | H-GW1 ordering argument limited to touch H-GLFT1; H-CJ2 can still pass |
| MG4-05 | NOTE | applied | H-AS0 sample about 1,450 fills (text and table) |
| MG4-06 | NOTE | applied | H-GW1 sample ~800 (ES) or ~900 (MES) |
| MG4-07 | NOTE | applied (partial) | "Greek transliterated" added to 2 quotes, "layout joined" to 1; the other listed quotes already carry caveats |
| MG4-08 | NOTE | skipped (style) | Ho-Stoll notation clarification not added |
| MG4-09 | NOTE | applied | "Proposition 3" dropped from the GLFT citation |
| MG4-10 | SHOULD FIX | applied (text); script mismatch needs lead | Prior-mean-0 option used: 0.0211, 0.930, 0.186/-0.012/-0.156; C2_StatsRMT_examples.py part_d and its JSON still hold the grand-mean values |
| MG4-11 | SHOULD FIX | applied | k = 4 rate bias restated: 0.020 bits measured, 0.058 first-order scale |
| MG4-12 | NOTE | applied | Timings set to JSON values (1.16, 3.01, 1.18, 1.41 ms) in all 8 places |
| MG4-13 | NOTE | skipped (style) | Rotation caveat on the race table not added |
| MG4-14 | NOTE | applied (partial) | Section 10 sentence corrected; the same "0.02 to 0.10" in the line-960 verdict row left (needs lead) |
| MG4-15 | NOTE | applied | BLdP citation now eq. 1 (restated under eq. 2) and Appendix 1 |
| MG4-16 | NOTE | applied | "grep -a" and one reference title, in both places |
| MG4-17 | NOTE | applied | LZ verdict row cites CTW only, plus the worked-example bias |
| MG4-18 | NOTE | applied | +7.6% described as about 7%, 0.7 points from the formula (text at the conclusion line; the measured table row +7.6% kept as the measured value) |

## Needs lead

- MG4-01: fix work/C2_Control/C2_threshold.py (c2 already contains sigma) and rerun to regenerate C2_threshold_out.txt; line 6 of C2_Control.md still lists these as provenance, while the text now cites REV_G4_control_check_out.txt.
- MG4-10: work/C2_StatsRMT/C2_StatsRMT_examples.py part_d (two-level block) and its JSON still use the grand-mean estimator; the brief now follows the review's second option (prior mean 0), the script needs the matching change or a note.
- MG4-14: the section 19 verdict row (C2_StatsRMT.md ~line 960) still says "within 0.02 to 0.10 bits of maximal entropy"; the review lists only line 673.
- Unverified by me: the 0.0227 (mean of squared family means) is derived from review values (0.0211 + 0.0016); not run.
