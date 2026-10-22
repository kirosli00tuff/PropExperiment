# R_fix_G6: fixes applied after R_math_G6.md (Stage E.28, BriefFixer G6)

Files edited: C2_AFML.md, C2_Firms.md (each with a "Corrections after review" section appended).

| Finding | Severity | Status | One line |
|---|---|---|---|
| MG6-01 | BLOCKING | applied | AFML 1.5: one-lag ADF stated [unverified book]; mechanism sentence replaced per review; assessment and verdict reason say "one-lag ADF". |
| MG6-02 | SHOULD FIX | applied | AFML 4.5: u_bar about 0.53 / 0.69 from 1.45 mean other labels; n_eff 0.5 to 0.7. |
| MG6-03 | SHOULD FIX | applied | AFML H-ML1 and table: about 1,000 per arm unpaired, about 500 paired. |
| MG6-04 | SHOULD FIX | applied | AFML H-FD1 sample in log-loss units (placeholder delta 0.005, sigma 0.3, about 28,000); tick example moved to H-TB1/H-ML1. |
| MG6-05 | SHOULD FIX | applied | 7.2 million to about 7.0 million (6,955,200) in 1.3 and the 1-s data sentence; timing mentions left (runs used 7.2M). |
| MG6-06 | SHOULD FIX | applied | "2011 to 2019" marked [unverified]. |
| MG6-07 | NOTE | applied | "about 100 trades" labelled as my estimate with basis (exact text given). |
| MG6-08 | NOTE | applied | Li quote line 17 to line 23. |
| MG6-09 | NOTE | skipped (NOTE, style) | Immaterial table-header wording; no number changes. |
| MG6-10 | NOTE | applied | 39 of 39 to 40 of 40. |
| MG6-11 | NOTE | skipped (NOTE, no exact text) | Review gives only a direction (cite abstract form or mention gamma_1); not a corrected-text fix. |
| MG6-12 | NOTE | skipped (NOTE) | Script-versus-text mismatch concerns the script/JSON, outside the two files; text is correct. |
| MG6-13 | NOTE | skipped (NOTE, style) | Quote marks around paraphrase at lines 647 and 675. |
| MG6-14 | NOTE | applied | Cites line 259 and drops the full stop inside the quote. |
| MG6-15 | BLOCKING | applied | E4 speaker now Campbell Harvey; Man AHL E4 attribution reworded in sections 1, 2, 3, 4. |
| MG6-16 | SHOULD FIX | applied | FPGA cites new E95 (HRT) and E96 (Optiver); co-location cites E93, [unverified] for ML firms. Quotes grep-checked, not in verify script. |
| MG6-17 | SHOULD FIX | applied | "not fetched" sentence rewritten per the review's option B; pointer stays [unverified]. |
| MG6-18 | NOTE | applied | AHL's co-CEO (its CIO at the time of E1). |
| MG6-19 | NOTE | applied | E32 quote extended with the customer/investor sentence. |
| MG6-20 | NOTE | applied | E78 quote extended with the reliance sentence. |
| MG6-21 | NOTE | applied | E9 speaker named (Ledford, Chief Scientist). |
| MG6-22 | NOTE | skipped (NOTE, no exact text) | Verification-method note for section 5 (PDF quotes checked against pdftotext, not saved .txt); no replacement text given; lead may add it or save a default-mode .txt. |
| MG6-23 | NOTE | skipped (NOTE, style) | AQR title quote marks. |

Counts: applied 17 (BLOCKING 2 of 2, SHOULD FIX 7 of 7, NOTE 8), skipped 6 (all NOTE), needs lead 0.

Residual points for the lead: (1) MG6-16 evidence rows E95/E96 and the extended E32/E78 quotes are not covered by C2_Firms_verify.py, so "94 of 94 pass" in section 5 covers E1-E94 only; (2) MG6-01 depends on `REV_G6_math_checks.json`, which the AFML text now cites; (3) the AFML script/JSON were not touched (MG6-12).
