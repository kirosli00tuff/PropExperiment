## 6. Program 4: EQ3 F08, the session and overnight-to-day handoff pooled over YM, MNQ and RTY (C147, Topstep)

### 6(a) Fact table

Pool facts (R2_combinations.json and r3_out.json C147): one registration over the members YM, MNQ and RTY, asset class
equity for all three. rho = 0.5, the spec 8.3 default within a class: E.29 section 3.2 measured only the CL-ZM, CL-GC,
CL-NQ, ZM-GC, ZM-NQ and GC-NQ pairs, none of YM-MNQ, YM-RTY or MNQ-RTY (R2_combinations.json rho_measured = {};
work/fix4/r1/r1fix_report.md F6). K_total = 3 x 870 = 2,610 test trades; K_eff = K_total / (1 + (m - 1) rho) =
2,610 / 2 = 1,305 (r3_out.json C147 K_used; work/score/r3_score.py k_eff); q = SR80_test x sqrt(870 / K_eff) =
0.1936 x 0.8165 = 0.1581 (C147 q; r3_score.py q5_score). K_eff falls if the true rho exceeds 0.5 (at rho 1 it
is 870, one member's count).

| item | YM | MNQ | RTY | source |
|---|---|---|---|---|
| band B; h_c | 15, 30; 30 | 15, 30; 30 | 15, 30; 30 | F5 pairs 5, 2, 9 |
| c_f (ticks); USD a round trip | 2.256 = 1.0 (u) + 0.5 + fee 0.756 (USD 3.78, stated); 11.28 | 3.94 = 1.0 (u) + 0.5 + fee 2.44 (USD 1.22, stated; tick USD 0.50); 1.97 | 2.256 = 1.0 (u) + 0.5 + fee 0.756 (USD 3.78, stated); 11.28 | combos_detail C147 members |
| sigma_30 (ticks) | 63.23 | 147.10 (NQ's F3, OC-1) | 51.75 | idem; F5_holding.json pairs rows."30".sigma |
| c_f / sigma_30 | 0.0357 | 0.0268 | 0.0436 (worst member: the pool's Q4 x) | idem; r3_out.json C147 x |
| K_year; K_disc; K_test; n/day | 252; 796; 870; 1 | 252; 796; 870; 1 | 252; 796; 870; 1 | combos_detail (daily family) |
| trades a year | 252 (one a trade date; F5's continuous cap at h 30, 13 a day or 3,276 a year, does not apply) | 252 | 252 | idem; F5 rows."30".n_cap, trades_per_year |
| e80 test, pooled (q 0.1581 x sigma_30) | 10.00 ticks (USD 49.98) | 23.26 ticks (USD 11.63) | 8.18 ticks (USD 40.91) | arithmetic |
| e80 test alone (q 0.1936, K 870) | 12.24 | 28.48 | 10.02 | combos_detail e80_ticks.test |
| c_f + e80 test, pooled | 12.25 | 27.20 | 10.44 | arithmetic |
| p_be (emp / norm) | 0.5248 / 0.5224 | 0.5183 / 0.5168 | 0.5304 / 0.5273 | combos_detail |
| Q6 (Consistency Path) | 4 (dll 0, payout 0, news 0) | 4 (dll 0, payout 0, news 0) | 4 (dll 0, payout 0, news 0) | r3_out.json C147 Q6_by_member |
| Standard Path $150 vs sqrt(n/day) sigma_30 v | $316.17: below | $73.55: exceeds (deducts 1) | $258.76: below | combos_detail prop_fit |
| MLL/(sigma_30 v) | 6.33 | 27.19 | 7.73 | idem |
| news (Topstep Tier 1) | "the family's fixed trade times lie outside every Tier 1 window" | "Topstep Tier 1: micro capped, one lot allowed (not stopped)" | as YM | idem |
| clean test window | 0 months under LR-V31 (106.97 before V31: 2010-06-06..2019-05-06, never read, unsealed) | 0.82 months (2010-06-06..2010-07-01) | 0.0 months (none) | R2_combinations.json C147 data.windows |
| data after 2024-03 | 2024-03..2025-03 not owned (a purchase, which V31 forbids); 2025-04..2026-06 owned, read through MYM by E.7 K1; 2026-06-17 onward not owned | 2024-03-01..2025-03-31 not owned, not read (13 months, about 273 dates); 2025-04..2026-06 owned, read by E.7 K1 and E.9 K8 on MNQ; 2026-06-17 onward not owned | 2024-03-01..2025-03-31 not owned, not read; 2025-04..2026-06 owned, read through M2K by E.7 K1; 2026-06-17 onward not owned | F2_data_access; sections 4(b), 5 and Appendix B(b) P1 |
| data schema | ohlcv-1m (YM price path) | ohlcv-1m (NQ price path) | ohlcv-1m (RTY price path) | combos_detail members data |
| data cost (estimates) | discovery 0; test none under LR-V31 (USD 4.26 for 2015-10..2019-04 under the narrow reading) | discovery 0; test about USD 1.29 (2024-03..2025-03, needs V51 approval) | discovery 0; test about USD 1.08 (2024-03..2025-03, needs V51 approval) | combos_detail; 6(c) |

Every data period after 2024-03 is closed by V51 item 2 unless the user approves it.

| pool item | C147 EQ3 topstep | source |
|---|---|---|
| documented horizon vs B | [30, 60]: "documented horizon(s) [60] min lie outside B (15-30 min)" | combos_detail C147 |
| C (r3 rank; R4) | 2.55 (12; R4 5): at 2.55 below C020 by G(h_c) (0.0973, RTY's) and above C108 by product code | r3_out.json; ties |
| Q1; Q2; Q3 (weakest member) | 3: "identified imbalance carry-over at the European open on the ES cousin (F08.E03), 60 min outside the band; cash-open handoff only F01.E05"; 2: "cousin peer-reviewed in sample, negative after spreads (F08.E03) and SPY (F01.E05)"; 1: "R1-03 K1-cp3-01 closed on MYM, MNQ and M2K and R1-13 E16-H4 pooled incl. YM, NQ and RTY; 15-30 min holds of these handoff signals are close variants" | R2_combinations.json C147 Q1-Q3 |
| Q4; Q5; Q6; Q7 | 3 (x 0.0436, the worst member's; r3 for_lead: "Q4 pool: worst member's x used (spec names the worst member only for Q6)"); 2 (q 0.1581); 4 (each member 4); 2 (test-window deduction 2: clean_test_window_months 0) | r3_out.json C147 |
| K_total; K_eff; rho; q | 2,610; 1,305; 0.5 (default); 0.1581 | r3_out.json C147 |
| prop fit (one account) | no DLL (Topstep 50K, MLL $2,000 trailing, used as the DLL, LR-DLL); flat-by-close 13:10 PT; latest start 12:30 PT at h 30; no overnight; gate note "flat-by-close gate: documented exit 07:00 PT vs flat-by-close 13:10 PT"; gates none. The three positions open on the same bar: at rho 0.5 their one-day sigma is USD 544.45 (from USD 316.17, 73.55 and 258.76), MLL / that 3.67; MNQ and RTY alone USD 302.32, 6.62 (arithmetic) | combos_detail prop_fit; arithmetic |
| same pool elsewhere | C161 mffu 2.55 (rank 15); C154 tradeify 2.25 (MNQ member Q6 3); C168 ibkr 2.10 (YM and RTY members Q6 1: margin); EQ3m {MYM, MNQ, RTY}: C175 mffu 2.40, C182 ibkr 1.80 | r3_out.json |
| sensitivities | ts150_v2 2.40 (rank 25; MNQ member Q6 3); q3only 2.55 (rank 32; Q7 stays 2, as MNQ and RTY have no clean pre-2024-03 window); nozlw 2.55 (R4 3rd); q3bleg 2.55 (rank 16, outside the R4); v1 2.55 (rank 46) | section 9 files |

Closed-line overlap (the members'; R1_closed_lines.md): R1-03 K1-cp3-01 (the CLV rule quoted in 4(a), MYM, MNQ and M2K
traded, 08:31 to 14:59); R1-13 E16-H4 (pooled incl. YM, NQ and RTY; V31 for YM's window); R1-10 K8-wkndbtc-01 (MNQ);
R1-01 MES families A and D; NQ-path lines of other families R1-14, R1-15, R1-18; R1-11 (E.12 Gate 0 on MNQ, MYM and
M2K) and R1-15 (E.20's search on NQ and RTY) are other families (bar-feature ML, G17 cross-market leads among the
features); scorer flag 13: "a cash-open F08 test has no direct evidence".

### 6(b) Pre-registration outline (draft)

- **P1 data.** YM ohlcv-1m (YM.v.0), NQ ohlcv-1m as MNQ's price path (NQ.v.0; OC-1) and RTY ohlcv-1m (RTY.v.0).
  Discovery 2020-12-01..2024-02-29, owned for all three. P1.5 exposure: E.16 H1/H4 pooled (YM 2019-05..2024-02, NQ
  2010-07..2024-02, RTY 2017-06..2024-02), E.21 (NQ, RTY), E.20's search (NQ, RTY), R1-14 H6 (NQ, 2020-06..2024-02),
  E.12 Gate 0 (MNQ, MYM and M2K vehicles), K1 (R1-03, MYM, MNQ and M2K traded). Test: none for YM under LR-V31
  (section 5); MNQ and RTY have no clean pre-2024-03 window (L10 (i)), so their test reads 2024-03 onward only with the
  user's approval (V51 item 2).
- **P2 F08 pooled.** One registration, members pooled, one mechanism (the handoff at the US cash open); excluded
  configurations as Programs 2 and 3: K1-cp3-01's rule (closed on MYM, MNQ and M2K), E16-H4's rule and K8-wkndbtc-01's
  rule (MNQ).
- **P3.** F08 at 15-30 minutes (B), h_c 30: entry at the 08:31 CT open on each member, exit at the open of the bar at
  08:31 + h, h {15, 30}; one trade per member a trade date, the members' positions opened on the same bar. The CPI,
  PPI and NFP note of 4(b) P3 applies to every member; full-size YM and RTY trade outside Topstep's Tier 1 windows and
  MNQ is capped at one lot, not stopped.
- **P4 (draft).** Program 2's grid (ON and CLV x side x h {15, 30} = 8, or 4 without the CLV members), each
  configuration run on the pool with the same parameters on every member: 8 (or 4) trials.
- **P5-P6.** Rule-based (V28); nothing to fit.
- **P7 (draft).** 8 (or 4) -> N 846 (842): binding 0.2008 daily, b_test 0.1650 at 870 test dates per member (section
  8); pooled per-trade test edge q 0.1581 at K_eff 1,305.
- **P8.** Section 2; G1 for a once-a-day family on each member, G2 in each member's ticks (YM and RTY USD 5, MNQ USD
  0.50).
- **P9. How the pool is cut under the decisions in force.** LR-V31 keeps YM out (no purchase, no variant on E.16's YM
  window), so the registration would cover MNQ and RTY only, on the post-2024-03 span the user approves. By the
  scorer's formulas the two-member pool has K_total 1,740 and K_eff 1,160 at rho 0.5, so q = 0.1936 x sqrt(870 /
  1,160) = 0.1677 (Q5 still 2; e80 test 24.67 ticks on MNQ, 8.68 on RTY) at the 870-date design; on the 13-month
  unread span (about 273 dates a member) K_eff is about 364 (2 x 273 / 1.5) and the test bars are section 8's
  short-window row (b_test 0.2964, SR80_test 0.3485 at N 846). The lead's K0: if only one of V31's narrowing and the
  2024-03+ approval is granted, the pool shrinks to its admissible members and is re-scored before any registration.
  With both granted, YM's test window (2015-10..2019-04) would not overlap MNQ's and RTY's (2024-03 onward), so the
  pooled test would be read over two disjoint spans.
- **P10.** Section 2.

### 6(c) Data purchase plan

| use | schema | symbols | dates | status | approximate cost (estimate) |
|---|---|---|---|---|---|
| discovery | ohlcv-1m | YM.v.0, NQ.v.0, RTY.v.0 | 2020-12-01..2024-02-29 | owned; read (6(b) P1; YM inside E.16's window, V31) | 0 |
| test, YM | ohlcv-1m | YM.v.0 | none under LR-V31; 2015-10-01..2019-04-30 under the narrow reading | not owned, never read; V31 forbids the purchase | USD 4.26 under the narrow reading only (combos_detail C147 all_data_cost_usd; E.12 quote rate USD 0.0991 a month x 43) |
| test, MNQ (needs the user's approval, V51) | ohlcv-1m | NQ.v.0 | 2024-03-01..2025-03-31 | not owned, not read | about USD 1.29 (USD 0.0995 a month x 13; 2010-2019 quote rate) |
| test, RTY (needs the user's approval, V51) | ohlcv-1m | RTY.v.0 | 2024-03-01..2025-03-31 | not owned, not read | about USD 1.08 (USD 0.0827 a month x 13; 2010-2019 quote rate) |
| owned after 2024-03 | ohlcv-1m | YM, NQ, RTY (MYM, MNQ, M2K) | 2025-04..2026-06 | owned; read by E.7 K1 (MYM, MNQ, M2K) and E.9 K8 (MNQ); closed by V51 | 0 |
| not owned | ohlcv-1m | YM, NQ, RTY | 2026-06-17 onward | closed by V51 | not priced |

Quote requests to obtain later, only after the user approves 2024-03 onward (V51), a funded Databento account exists
and a fresh quote is approved: GLBX.MDP3, ohlcv-1m, NQ.v.0, 2024-03-01..2025-03-31; GLBX.MDP3, ohlcv-1m, RTY.v.0,
2024-03-01..2025-03-31 (the same two requests serve Program 2 and Appendix B; L7). No YM request under LR-V31
(combos_detail lists GLBX.MDP3 ohlcv-1m YM.v.0 2015-10-01..2019-04-30, valid only under the narrow reading); the ON
signal on the first test date needs the 17:00 CT bar of the prior trade date, inside the discovery file for 2024-03-01.

### 6(d) Kill-criteria facts

- Power: q 0.1581 at K_eff 1,305; e80 test 10.00 ticks on YM (USD 49.98), 23.26 on MNQ (USD 11.63), 8.18 on RTY (USD
  40.91), that is 0.158 sigma_30 on each member; c_f + e80 12.25, 27.20, 10.44. Cut to MNQ and RTY (6(b) P9): q 0.1677,
  e80 24.67 and 8.68 ticks at the 870-date design.
- Published effect: as 4(d) (F08.E03, ES, European open: 0.069 daily gross, -0.031 net; no futures evidence at the cash
  open, scorer flag 13).
- Prop limits by horizon (F5 pairs 5, 2, 9; MLL/(sigma_h v)): YM 15: 8.84, 30: 6.33; MNQ 15: 37.87, 30: 27.19; RTY 15:
  10.69, 30: 7.73. The three positions at once: about 3.67 (rho 0.5, arithmetic above). Payout: the Standard Path's
  $150 exceeds MNQ's $73.55 (ts150_v2: C147 2.40).
- Data: none buyable for YM under LR-V31; MNQ and RTY about USD 2.37 (estimate), only with the V51 approval.
