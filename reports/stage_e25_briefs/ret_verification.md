## 5. Verification

S4: ShortlistReviewer-FableXHigh (fable, xhigh), 11:30-11:45 PDT, reports/stage_e25_briefs/review_S4.md (221 lines).
Verdict on synthesis v2: **BLOCK** until findings 1-2 are corrected; READY WITH FIXES once 1-12 are applied; no
shortlisted candidate duplicates a prior trial (rows 1-5 checked against r0_mechanism_index.md sections 1-16 and
its keyword index); no membership or rank change. Counts: BLOCKING 2, SHOULD FIX 10, NOTE 10. The reviewer also
confirmed the brief's D8 hurdle table against reports/stage_e2a_costs.md and the MES Stage D cost (2.03 ticks).
Every fix below is in synthesis.md v3 (v2 kept as synthesis_v2_prereview.md), s2_power.py/.out v2 and
ret_decisions.md; the lead's recomputed figures match the reviewer's to two decimals.

| # | Severity | Finding (short) | Ruling | Fix |
|---|---|---|---|---|
| 1 | BLOCKING | C1 power used 299 days; the published t 5.34 is over 2,620 TRADED days (about 61% of the sample) | accepted | s2_power.py uses SR per traded day over about 183 expected traded days: MNQ E[t] 1.26, power 0.35 (Holm-5 0.14); MES 1.11, 0.30 (0.11); forward 250 days 0.31 / 0.27; S1 row 1 says "traded days" |
| 2 | BLOCKING | C2 row mixed the 14.8 bp sensitivity into the published-size range; n stated three ways | accepted | one event rule (15 monthly expiries, 10 if the quarterly dates are blacked out); C2 at 12.89 bp: E[t] 0.47-0.58, power 0.12-0.14 |
| 3 | SHOULD FIX | C4 row did not describe the FOMC-conditional design | accepted | C4 row as designed (n 3): 0.11 at 12.62 bp, 0.21 at the conditional cell's 23.65 bp (full-sample sd) |
| 4 | SHOULD FIX | C3's 16.91 is an unlabelled upper bound | accepted | C3 at the tradable 17:00 CT leg 12.75 bp (digitized): ratio 15.07, power 0.15-0.19; 16.91 labelled as the published upper bound |
| 5 | SHOULD FIX | Holm step k = 4 but five trials designed | accepted | k = 5 (alpha 0.01, z 2.326) throughout |
| 6 | SHOULD FIX | overlap cells omitted the nearest prior trials; K2-monthend-01 removes blindness on 2 of C4's 3 events | accepted | rows 1-4 name K1-vwap-01, A-H4 rth/eth legs, D-H4, K2-monthend-01; C4 design states the non-blind dates and the month-end fixed effect |
| 7 | SHOULD FIX | grades missing on Delgado, Chuk, Brusco/VigorTas ES | accepted | [secondary-only] and P labels added |
| 8 | SHOULD FIX | "every independent S&P test at or below zero" contradicts Paz +0.39 | accepted | "no independent S&P test after publication is distinguishable from zero; the latest are negative" (S1, S2, S3, decisions) |
| 9 | SHOULD FIX | re-dig row "E20H6 as a replica" mis-stated H6's exit | accepted | "exits 1-2 minutes before the close (14:58 bar, fill about 14:59 CT)" |
| 10 | SHOULD FIX | V38 row overstated DF3 ("post-2015-inclusive") | accepted | "samples run past 2015 ... neither publishes a post-2015 estimate"; same in decision 4 |
| 11 | SHOULD FIX | per-trade basis caveat missing (fills vs round trips) | accepted | S1 row 1: per round trip about 8 bp if the paper counts fills |
| 12 | SHOULD FIX | S3 power range mislabelled | accepted | 0.11-0.22 at published sizes, 0.06-0.17 at post-2015 sizes |
| 13 | NOTE | C5 sd is DF3's inference | accepted | marked in the S2 row and design |
| 14 | NOTE | RD3-C1 bound depends on the gold price | accepted | 10.5-14.0 MGC ticks |
| 15 | NOTE | MNQ ratio depends on the NQ level | accepted | 8.16-9.71 at NQ 21,000-25,000 |
| 16 | NOTE | V34 row: DF1 grades it "weakens the basis" | accepted | "weakens the 'unsized' basis" |
| 17 | NOTE | header time stamps | accepted | header now v3 |
| 18 | NOTE | C4 condition rests on DF3's reading of Table 11 cell labels | accepted | stated in the C4 design |
| 19 | NOTE | row 6 size is net of spread | accepted | "used as gross: conservative" |
| 20 | NOTE | row 2 source version | accepted | January 2024 AFA copy; August 2026 version drops the futures table |
| 21 | NOTE | B1's cancel time is the lead's parameter | accepted | stated as a design parameter to be fixed in a pre-registration before any data is read |
| 22 | NOTE | Apex/Lucid/Tradeify/Bulenox facts rest on search summaries | accepted | marked [secondary-only] in the prop landscape |

Earlier verification inside the stage: the lead spot-checked the mechanism index's N reconciliation (538); NM2
re-classified NM1's 119 fee-covering rows from the verbatim rule text and confirmed Group A empty; DF1-DF3 re-read
every shortlisted number from full text (DF1 and DF3 confirmed the figures; DF2 verified Table II and digitized the
2026 figures).

**Re-check (ShortlistReviewer-FableXHigh, resumed 11:48, returned by 11:51 PDT per `date`; review_S4.md "Re-check"): READY.** Findings
1-12 applied correctly; NOTEs 13-18 and 20-22 applied; every s2_power.out v2 row re-derived to two decimals; no new
error introduced. Its four remaining NOTEs (an index-gap caveat on row 6, the V34 wording in decision 5, the NQ
level in the S2 C1 ratio, and this line) were applied by the lead at 11:51.
