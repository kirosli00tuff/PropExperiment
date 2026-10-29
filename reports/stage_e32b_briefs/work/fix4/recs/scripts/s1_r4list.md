## 1. The R4 list (r3_out.json "R4", version 3 after LR-Q3b, verbatim) and its grouping

| R4 | id | product or pool | family | best venue | band B | h_c | C | weak | r3 rank |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C140 | ZL | F10 order-book state at 5 min and longer | topstep | 15, 30, 60 | 30 | 2.75 | no | 1 |
| 2 | C138 | ZL | F09 cross-market lead-lag | topstep | 15, 30, 60 | 30 | 2.65 | no | 2 |
| 3 | C072 | MNQ | F08 session and overnight-to-day handoff | topstep | 15, 30 | 30 | 2.55 | no | 4 |
| 4 | C021 | YM | F08 session and overnight-to-day handoff | topstep | 15, 30 | 30 | 2.55 | no | 5 |
| 5 | C147 | EQ3 {YM, MNQ, RTY} | F08 session and overnight-to-day handoff | topstep | 15, 30 | 30 | 2.55 | no | 12 |
| own broker | C141 | ZL | F10 order-book state at 5 min and longer | ibkr | 15, 30, 60 | 30 | 2.60 | no | 3 |

- n_reaching_2 = 5; fewer_than_3_reach_2 = false; "R4_prop_only" is the same five. None is weak.
- Ties (r3_out.json "ties"): none at 2.75, 2.65 or 2.60 (C140, C138 and C141 stand alone); at 2.55 C072 above C021 by
  G(h_c) 0.0805 < 0.0894, then C075, C074 (MNQ lucid, mffu), C019, C023, C022, C020 (YM), C147 (EQ3; G 0.0973, its
  worst member's), C108 (RTY, below C147 by product code), C107, C161, C110; at 2.50 C134 (ZL F03 topstep) above C113
  by Q1, then C112, C115 and C139 by G(h_c).
- Q3 under LR-Q3b (L11): C138 has Q3 1 (the rater's 2 is kept as Q3_rater); C140 and C141 keep the rater's 2.
- Q7 under LR-V31 and the census: C072, C021 and C147 carry the 24-month test-window deduction (Q7 2); C140, C138 and
  C141 keep Q7 4 on the sealed ZL window.
- Sensitivities (section 9): q3only puts C021 YM F08 first (2.85); nozlw puts C072 MNQ F08 first (2.55); q3bleg (the
  leg-level F09 reading) reproduces the version 2 list (C138 and C140 2.75, C113 2.60, C072 and C021 2.55).

Grouping:
- **Program 1, ZL (C140 F10 and C138 F09)**: one product, venue, band and sealed test window; one registration with two
  feature families on the one sealed read (L3), F10 first (the higher C). The best own-broker C141 (ZL F10 at IBKR) is
  an execution choice of the same program (section 7); C139 (ZL F09 at IBKR) is 2.50 under LR-Q3b.
- **Program 2, MNQ F08 (C072)** and **Program 3, YM F08 (C021)**: the same family at the cash open on two underlyings.
  Sections 4 and 5 keep them separate because their data constraints differ (post-2024-03 data for MNQ; V31 for YM).
- **Program 4, EQ3 F08 (C147)**: the same handoff pooled over YM, MNQ and RTY at Topstep, one registration (section 6).
  Under the decisions in force its YM member cannot enter (LR-V31), so the pool is cut to MNQ and RTY (6(b) P9).
- RTY F09 (C113, 2.50) left the R4 under LR-Q3b (L11); its tables are kept in Appendix B.
