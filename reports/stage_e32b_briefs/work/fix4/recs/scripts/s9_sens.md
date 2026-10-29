## 9. Sensitivities: the alternatives (current files)

Every run is r3_score.py on one mode of work/R2/patch_v31_q3_lead.py applied to the version 1 combinations (the
ts150 mode starts from work/R2/R2_combinations_topstep150.json); v1 is the unpatched version 1 run. The table is
generated from the files' "R4" and "best_own_broker" keys.

{SENS_TABLE}

**q3only (LR-Q3a and LR-Q3b, V31 narrow, the user's decision D1):** C021 YM F08 topstep 2.85 (Q7 4: YM test
2015-10..2019-04 buyable, about USD 4.26) leads; C049 MYM F08 mffu (30, 60; h_c 30) 2.70 and C039 YM F12 topstep (15,
30) 2.65 (Q 3, 2, 2, 3, 0, 4, 4; L9 applies: exclude R1-14 H6 T3) enter; C138 is fifth (2.65); best own-broker C141
2.60 (rank 23). The Dow candidates (C021, C049, C039) all rest on the narrow reading of V31: no YM purchase and no
variant on YM's 2019-05..2024-02 window is allowed under the literal reading. C049 uses YM's path (L5) and MFFU's costs
(c_f 5.30 MYM ticks, x 0.0838). C147 stays 2.55 with Q7 2 (MNQ and RTY have no clean pre-2024-03 window).

**nozlw (primary plus no ZL window, the user's decision D2):** C140 falls to 2.45 (rank 19) and C138 to 2.35 (rank
33); every R4 member has Q7 2 (no clean pre-2024-03 test window); the MNQ and RTY members need post-2024-03 data with
the user's approval (V51), and the YM member of C021 and C147 is bound by V31 read literally (section 5). RTY F09
(C113, 2.50) is fifth here.

**ts150_v2 (primary with Topstep's Standard Path $150 in Q6):** n_reaching_2 = 5 and fewer_than_3_reach_2 = false;
the run's last printed line "fewer than 3 reach 2.00: False" is r3_score.py's label with its value (RV2 N1), not a
finding that fewer than three reach 2.00. The Standard Path deducts 1 from Q6 where a one-lot sqrt(n/day) sigma_hc v
is below $150: C072 MNQ F08 topstep falls to 2.40 (rank 22) and C147 to 2.40 (rank 25, through its MNQ member), so MNQ
F08 enters at Lucid (C075, 2.55) and C108 RTY F08 topstep takes fifth. C140 and C138 ($505.85) and C021 ($316.17)
keep Q6 4: their one-lot sqrt(n/day) sigma v exceeds $150.

**q3bleg (primary without LR-Q3b: the leg-level F09 reading, Q3 2 as rated; LR-Q3b's sensitivity):** reproduces the
version 2 primary list and own broker (C138 and C140 2.75, C113 2.60, C072 and C021 2.55; C139 2.60).

**v1 (06:20, before LR-Q3a, LR-V31 and LR-Q3b; LR-Q6p primary):** its F01 leaders (C003, C043, C044) are gated now
(Appendix A).
