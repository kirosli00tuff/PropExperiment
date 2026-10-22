## Part 5. Verification: MathReviewer's findings, the rulings and the fixes

Six independent MathReviewer-FableXHigh reviews (Fable 5.1, xhigh) checked every equation, derivation summary, worked
example and evidence claim, with re-derivations in sympy or numpy and a scripted check of every quote against the saved
source files. Reviews: reports/stage_e28_briefs/R_math_G1.md to R_math_G6.md; fix logs R_fix_G1.md to R_fix_G6.md;
scripts under reports/stage_e28_briefs/work/REV_G1 to REV_G6.

| Group | Files | BLOCKING | SHOULD FIX | NOTE | Outcome |
|---|---|---|---|---|---|
| G1 | C2_SDE, C2_Filter | 0 | 5 | 14 | all SHOULD FIX and 9 factual notes applied; the lead applied MG1-07 (a one-sided alternative for H-SDE-ETA) and MG1-18 (the HMM gate's verdict reads "maybe", since its cost-inclusive evidence is daily, not intraday) |
| G2 | C2_Hawkes, the lead's C0, C3 and C4 | 0 | 10 | 15 | all applied in C2_Hawkes and C1; the lead fixed its own files (C3's order of the constraints, C0's list of constraints, the 0.3 ms wording, CPCV "15 splits, 5 paths", a paraphrase in quotation marks, the Hawkes configuration count, three factual notes) |
| G3 | C2_LOB, C2_Pooled | 0 | 5 | 14 | all SHOULD FIX and 7 factual notes applied, including a flag that Cont-de Larrard's equation (5) for the duration tail is wrong in the paper itself; the lead lifted an [unverified] mark whose full text is saved by the LOB reader (MG3-18) |
| G4 | C2_Control, C2_StatsRMT | 0 | 6 | 12 | 16 of 18 applied; the lead applied the remaining verdict-row correction (MG4-14) and noted two superseded helper-script outputs (MG4-01, MG4-10) |
| G5 | C2_DeepLOB, C2_OFI | 1 | 5 | 10 | all applied except one note without replacement text; the BLOCKING item (a misread two-column table that invented a cross-paper inconsistency) is removed and changed no verdict |
| G6 | C2_AFML, C2_Firms | 2 | 7 | 14 | both BLOCKING and all SHOULD FIX applied, with 8 notes |
| Total | | 3 | 38 | 79 | |

The lead's ruling for every group: all BLOCKING and SHOULD FIX findings accepted and fixed as the reviewer proposed;
notes applied where they correct a fact, number, citation or missing [unverified] mark. No verdict in the brief changed
except the HMM gate (use to maybe). The reviewers report zero fabricated or misattributed quotes (each review file gives its
quote-check counts), and no equation or worked example wrong in the deep dives other than the items listed in their
files. The lead's synthesis (Parts 0, 3 and 4) was checked against its cited lines: 23 of 24 quotes verbatim at the
cited lines; the one paraphrase in quotation marks is fixed.

Limits of the review, from the reviewers' own reports: papers that neither the readers nor the reviewers could fetch
in full (for example Kolm, Turiel and Westray 2023 on deep OFI) are checked only against abstracts and secondary
sources, and the [unverified] marks stand; one reported result (Cont-Stoikov-Talreja Table 4) remains unreproduced
after nine readings; G4's raw quote-check appendix was cut by a usage limit, its findings and judgments complete.
Every deep dive ends with a "Corrections after review" section listing what changed.
