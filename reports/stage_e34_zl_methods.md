# Stage E.34 Part M: ZL methods addendum (M1-M4 and the lead's reconciliations L)

Assembled 2026-10-29 by the lead (Opus 5.5 max, session 3). This file extends E.32's methods brief
(reports/stage_e32_methods_brief.md), which it cites and does not repeat. It holds: this front (purpose, verdicts,
what Part P takes, errata), then five files concatenated unchanged: stage_e34_briefs/M1_F10_ZL.md (MathReaderM1-OpusHigh),
M2_F09_ZL.md (MathReaderM2-OpusHigh), M3_labels_ZL.md (MathReaderM3-OpusHigh), M4_power_ZL.md (MathReaderM4-OpusHigh)
and L_lead_reconciliations.md (the lead, sessions 2-3). The workers' scripts and outputs are under
stage_e34_briefs/work/<worker>/. Where an erratum below corrects a worker file, the erratum governs; the protocol
(reports/stage_e34_zl_protocol.md) already carries every correction that enters it.

Review: MathReviewer-FableXHigh (claude-fable-5-1, confirmed from its transcript), stage_e34_briefs/review/MathReview.md:
GO WITH FIXES, 2 BLOCKING, 4 SHOULD FIX, 14 NOTE. All four worker scripts open no market data and reran byte for
byte; an independent implementation (no frozen imports) reproduced every M4 and L number. Nothing in Part M computed a
ZL feature value, label, return or outcome.

## Verdicts and what Part P takes

| Topic | Verdict | Key figures | Protocol | Review status |
|---|---|---|---|---|
| M1 F10 on ZL | MBP-1 for discovery (owned) and for the test (route A); no MBO | 8 of E.32's 12 F3 features carry over, 2 adapted (seasoned queue imbalance, cancellations), 2 dropped (IOFI5, QI3); USD 23.36 (MBP-1 test) against 40.96 for MBO in both windows, USD 17.60 more | P2 F10, P4 F10 table, P11 | B1 and B2 fixed (errata 1-2) |
| M1 / L.a minimum horizon | 5 minutes | measured day share of T records 76.2% (DF34) instead of M1's assumed 83%; SD criterion read at the 5th-percentile date | P4 windows 5, 15, 30 (60 for lam60) | confirmed |
| M2 F09 into ZL | crush residual with ZL as the adjusting leg: USE; ZS and ZM leading ZL on 1-minute bars: USE; CL: EXCLUDED; HO, RB, RINs: not owned for either window | break-even share 0.52 of a dislocation within one half-life (ZM 0.70 in E.32); cost per sigma 0.085 (ZM 0.092); look-backs 5, 15, 30 minutes; 17 features | P2 F09c, F09p; P4 L1-L2; P6.5 VECM report only | S3, S4 (errata 5-6) |
| M3 labels | FH15, FH30, FH60, TB15, TB30 (FH05 and TB60 out); market execution at 1 s selects; trade-through limits reported | cost-aware executable labels at f 0.880 ticks; FH caps 17 / 8 / 4 trades a date (L.b) | P3, P6.4 | S1, S2 (errata 3-4) |
| M4 power and N | the test can detect only a large edge; Holm never binds; E.32-D2 is decisive | at N 1038: G3 0.1746, b_test 0.166967, G4 0.2028, SR80_test 0.1957; T_disc 796, T_test 870; e80 0.97 / 1.94 / 3.74 ticks at the FH caps; as coded, a lone finalist beside null Tier B companions passes with probability about 0, amended 0.845 at a true daily Sharpe of 0.20 | P7.2, P9.3, P9.4, P10.2 | numbers verified; N1, N2 (errata 7-8) |
| L.a-L.f | lead reconciliations and rulings | caps 17 / 8 / 4 and K2's measured form (L.b); latest 30-minute entry 12:42 CT (L.c); ts_event drop-and-count rule (L.d); test trade dates 2017-05-22..2020-11-30 (L.e); rulings after review (L.f) | P1.2, P3.8, P9.1, P10.2 | L.b corrected by L.f.1 |

E.33's negative on ZM (M2 (e)) informs only the prior; no feature, label or setting is chosen by it (protocol P1.5,
firewall rule 5). M2's statement that the test window's ZM bars are owned is wrong before 2019-05 (erratum 21).

## Errata (they govern over the worker files)
1. (MathReview B1) M1:153, :155-158 and :467, F10.7: qb~ = 0 only if the most recent change of bid_1 with ts_recv in
   (t - 1 s, t] was an increase (ask: a decrease); the proof sketch fails on a rise-then-fall second. Trap 9 (M1:407)
   adds that path (hand value: the min over [t - 0.2 s, t], not 0). Protocol F10.7, LT12.
2. (MathReview B2) M1:169-180, :178 and :469, F10.9: the claim "counts correctly in either case" is false. Take the
   touch decrease over every consecutive record pair of the batch (any action) and subtract the batch's T lots at
   that price once, floored at 0; one-sided or bad pairs contribute 0 and are counted. Protocol F10.9, DC2, LT12.
3. (MathReview S1) L:55-56: the 20-entry cap never binds for FH15, FH30, FH60; it can bind for TB15 and TB30. L.f.1.
4. (MathReview S2) M1:402, :456 against M3:230-231, :445-446: one bad-book reading, E.33's FA-4 (any record of the
   batch), for features and labels; M3's F_LAST-record form is superseded; labels from ZL MBP-1 in both windows, so M3
   c.4's parity options reduce to (a). L.f.2.
5. (MathReview S3) M2:540-541: delete "further capped by Topstep's latest entry (h 30: 10:50 PT = 12:50 CT)"; the grid
   alone governs (latest entries 12:57 / 12:42 / 12:12 CT). Matters for option B only.
6. (MathReview S4) M2:225-227, :230-231 and :514: the implied-oil gap's bar bounce has two bar closes: SD sqrt(2) x
   1.594 = 2.254 ZL ticks, 41% of sigma_1, 19% of sigma_5, 11% of sigma_15, 8% of sigma_30 (not 29 / 13 / 8 / 6%);
   2.14 ticks with ZL's price from its BBO mid. The verdict stands (k = 1 dropped, k >= 5 kept).
7. (MathReview N1) M4:41-43: SR80 = bar + z80 se(bar, T) is E.32's convention; the exact value is 0.1937 (N 838) and
   0.1958 (N 1038) against 0.1936 and 0.1957.
8. (MathReview N2) M4:168-169: heavy tails add 1-3% at kurtosis 6-20, not 2-4%; at skew -2 and kurtosis 30, +11.1% on
   SR80_test and +13.1% on the binding threshold.
9. (MathReview N3) M1:207-208: TI5 = 0.20 with iid SE 0.0603 is 3.3 standard errors, not two.
10. (MathReview N4) M1:73-74: the ratios to ZM's 0.0120 are 3.7 / 7.1 / 13 on the c_f column and 2.0 / 2.3 / 2.0 on
    the c_f + e80_test column, not "3 to 6".
11. (MathReview N5) The ts_recv - ts_event tail differs between E.32's data facts and DF34; the run stage's drop report
    shows the overlap with the flags (protocol P1.2; L.f.5).
12. (MathReview N6) M1:44: "Databento derives CME MBP-1 from MBO" is an inference from the general schema page, as M1
    2.1 (:103) says.
13. (MathReview N7) M1:387-388: at 08:35 on the open-time axis a 30-minute window reaches back to 07:20 and a
    15-minute window to 07:35.
14. (MathReview N8) M3:393-394: 243 covered minutes, so n_eff 16.2 / 8.1 / 4.05.
15. (MathReview N9) Illustrative figures at E.32b's caps 19 / 9 / 4 and the 12:50 CT entry (M1:35-36 and :64-68:
    3.28 / 4.19 / 6.08 become 3.34 / 4.30 / 6.08 at caps 17 / 8 / 4; M2:110-112: 4.19 -> 4.30 ticks, 0.461 -> 0.473
    c/bu; M3:19 and :205) are superseded by L.b; none enters the protocol.
16. (MathReview N10) Citation line drift, quotes verified: M4:71 line 777 -> 795; M4:21 lines 518, 520, 521 -> 517,
    519, 520; M3:104 line 285 -> 283-284; M2:375 -> 880 and 893; M2:390-391 lines 278, 356 -> 283, 362; M2:306
    165-167 -> 171; M3:351 line 395 -> 408.
17. (MathReview N11) M2:179 and :284: read as closed-trial statuses (R1-11, R1-15, R1-08), not statistics.
18. (MathReview N12) Traps added in the protocol: LT13 (DST), 0.3's bar-stamp note (rule B cannot look ahead under
    either convention), G1's timing of trade counts and batches, and the bad-book reading (erratum 4).
19. (MathReview N13) K2 binds only below about 810 test dates at N 1038 (L.f.3).
20. (MathReview N14) M4:252-262 show 9 of the script's 12 D2 cases (the rest are in m4_out.md); M4:268's figure is
    0.0485.
21. (ProtocolReview B1) M2:38-39 and :235: the test window's ZS and ZL bars are owned (2017-04..2020-11); ZM's only for
    2019-05..2020-11. ZM.v.0 ohlcv-1m 2017-05-01..2019-04-30 is bought with the test data (protocol P9.1, P9.2, P11;
    L.f.4).
22. (FixVerify F4) M3:229-230: MBP-1 "has no R record" is wrong; DF34 counts one R record in the ZL files. The bad
    mark is per update either way (E.33's code clears it at each F_LAST record; L.f.2).



---

<!-- concatenated unchanged: reports/stage_e34_briefs/M1_F10_ZL.md (sha256 0b096005338fd134) -->

# E.34 methods addendum, M1: F10 order-book state on ZL at 5 minutes and longer

Worker: MathReaderM1-OpusHigh (opus, high). Started 2026-10-29 12:10 PDT (`TZ=America/Vancouver date`).
Scope (BRIEFS.md lines 145-174): which E.32 F3 order-book features carry over to ZL, which need MBO and which work
from MBP-1; the minimum aggregation horizon at ZL's message rate; MBO or MBP-1 for discovery, the test schema, the
cost difference; leakage traps; a "Protocol inputs" block for protocol P4.

What this file does not do: it reads no market data, computes no feature, return, label or model output, and copies
no statistic an earlier stage computed on ZL data. The only numbers about ZL data used here are record counts from
reports/stage_e32_data_facts.md (counts, not outcomes) and the shared ZL facts of BRIEFS.md lines 49-69. Arithmetic is
in work/MathReaderM1-OpusHigh/scripts/m1_examples.py (sha256 16ddd5c8...b687), output m1_examples.out (sha256
163533b6...7849). Web pages saved under work/MathReaderM1-OpusHigh/pages/ (log.tsv); 1 WebSearch used of 20.

Citation keys: "E.32 brief L<n>" = reports/stage_e32_methods_brief.md line n (the verified quotes there are E.32's);
"P <n>" = reports/stage_e32_discovery_protocol.md line n; "DF <n>" = reports/stage_e32_data_facts.md line n; "DB-x
L<n>" = a Databento page saved in my pages/ folder, line n (x: mbp1 = schemas_mbp-1.md, glbx = datasets_glbx-mdp3.md,
schema = schemas_whats-a-schema.md, mbo = schemas_mbo.md, mbp10 = schemas_mbp-10.md); "E.32b recs <n>" =
reports/stage_e32b_recommendations.md line n; "feat33 <n>" etc. = reports/stage_e33_briefs/work/pipeline/<file> line n.

---------------------------------------------------------------------------------------------------------------------

## 0. Bottom line

1. Of the 12 E.32 F3 features, 8 carry over to ZL MBP-1 with the same definition (F3.1-F3.3 best-level OFI, F3.5-F3.6
   aggressor imbalance, F3.10 sweeps, F3.11 refills, F3.12 trailing lambda; F3.10 with one wording change, the
   depletion test on the touch after the batch). 2 need an adaptation that MBP-1 supports (F3.7 seasoned queue
   imbalance via a causal 1-second running minimum that bounds the exact seasoned depth from above and is exact (zero)
   for a newly improved touch; F3.9 touch cancellations with fill lots attributed by price inside the event batch
   instead of by order id). 2 need depth beyond level 1 and are dropped on MBP-1 (F3.4 multi-level integrated OFI,
   F3.8 three-level queue imbalance). The context block's book items (spread, touch depth, volume, sigma) all carry
   over; C.7 days to expiry needs definitions, which are owned for discovery and not for the test.
2. ZL's rate (E.32 data facts, whole trade-date windows): median 168,917 book events and 19,195 trade records a date,
   quietest date 6,998 trade records (DF 260-262). At an assumed 83% day-session share that is about 8 book events a
   second and 55 trade records a minute (20 on the quietest date). A sign imbalance then has an iid sampling SD of
   0.100 or less from 5 minutes on even on the quietest date (n about 100), against 0.22 at 1 minute; with that and
   the published decay of forward order-flow predictability within about 30 minutes, the window set is 5, 15 and 30
   minutes (60 only for the lambda conditioner). Minimum aggregation horizon: 5 minutes.
3. Recommendation for the lead: discovery on the owned ZL MBP-1 front month; the test on ZL MBP-1 2017-05-22..
   2020-11-30 (same schema in both windows). Cost (E.32b recs 4.5(c), estimates): MBP-1 in both windows USD 23.36,
   MBO in both USD 40.96, difference USD 17.60; buying MBO for discovery alone costs USD 19.48. The cost is not the
   reason. The reasons are: the MBO-only features are the ones M1's evidence rates lowest (multi-level OFI is a
   contemporaneous fit; seasoning and iceberg detail are conditioners), MBO does not reduce the discovery dates'
   exposure (the exposure is of dates, not schemas; V50 item 4), MBP-1 in both windows needs no equivalence proof,
   and Databento derives CME MBP-1 from MBO, so nothing in MBP-1 is lost against MBO at level 1. Cost of the
   decision: a weaker spoofing guard (an upper bound on seasoned depth, not the exact value) and approximate
   cancellation attribution. A mixed route (MBP-1 discovery, MBO test with a derived top of book, USD 21.48) needs
   an equivalence check first (section 4.4).
4. Leakage traps specific to ZL (section 5): ts_recv clock, 1 s latency, ZL.v.0's flips between contracts (ZLN1/ZLK1
   alternation 2021-04-04..04-10, one-day ZLQ1 2021-06-29 and ZLQ2 2022-06-30), the 07:45-08:30 pause and the
   opening uncross, the 13:13 label end, snapshot and F records inside MBP-1, side-N trades (10.0% of ZL trade
   records), and the MDP 2 data before 2017-05-21 (ts_recv equals ts_event there).
5. The F10 list (section 7): 12 features, F10.1-F10.12, plus E.33's context block adapted to ZL.

---------------------------------------------------------------------------------------------------------------------

## 1. The hurdle at ZL horizons (extends E.32 brief M1 section 1, L3649-3674, from ZM to ZL)

Assumptions, stated: (A1) sigma_h is the measured day-session SD of h-minute ZL mid changes (shared facts: h15 20.37,
h30 28.10, h60 38.21 ticks); (A2) a forecast f of the h-minute change is normal with sd(f) = sqrt(R2) sigma_h, R2 its
out-of-sample R-squared; (A3) the round trip is c_f = 2.38 ticks (USD 14.28) at Topstep (shared facts). For a normal
forecast E|f| = 0.7979 sd(f); trading only the top decile of |f| gives a mean traded |f| = 2.0627 sd(f) (phi(1.6449)/0.05).
R2 needed so that the mean traded |f| equals a target edge g: R2 = (g/(sigma_h k))^2, k = 0.7979 or 2.0627.

| h (min) | sigma_h (ticks) | R2 for g = c_f, every bar | R2 for g = c_f, top decile | g = c_f + e80_test (ticks) | R2 for that g, top decile |
|---|---|---|---|---|---|
| 15 | 20.37 | 0.0214 | 0.00321 | 2.38 + 0.90 = 3.28 | 0.00609 |
| 30 | 28.10 | 0.0113 | 0.00169 | 2.38 + 1.81 = 4.19 | 0.00523 |
| 60 | 38.21 | 0.0061 | 0.00091 | 2.38 + 3.70 = 6.08 | 0.00595 |

Check (h 30, top decile): 28.10 x 2.0627 = 57.96; 2.38/57.96 = 0.04106; squared 0.00169. Worked in dollars: sigma_30 =
28.10 ticks = USD 168.60; c_f = USD 14.28 is 8.5% of it (c_f/sigma 0.085, E.32b recs 4.5 line 534).

Reading: at 15-60 minutes ZL's hurdle in R2 terms is 3 to 6 times lower than ZM's at 5 minutes in E.32 (0.0120 top
decile), because ZL moves more per cost unit. That is the case for F10 on ZL. It does not supply the missing link:
E.32's forward-OFI bound R2_pred = rho^2 R2_c (E.32 brief L3711) with R2_c = 0.65 (CKS, E.32 brief L3810) and an
assumed lag-1 autocorrelation of window OFI rho = 0.05, 0.10, 0.20 gives 0.0016, 0.0065, 0.026; the top-decile
target with the test's detectable edge (about 0.005-0.006) sits between rho = 0.05 and rho = 0.10, and CKS report
that OFI autocorrelations at 10 s "are small and quickly vanish" (E.32 brief L3812). Whether 5-30 minute ZL OFI has
rho near 0.1 is exactly what discovery would measure; nothing published gives it for ZL.

---------------------------------------------------------------------------------------------------------------------

## 2. (a) Carry-over: every F3 feature and the context block's book items

### 2.1 What each schema contains (from the Databento pages, fetched 2026-10-29 19:12-19:13 UTC)

- MBO: "provides every order book event across every price level, keyed by its order ID" (DB-mbo L6).
- MBP-10: "every order book event across the top ten price levels, keyed by price ... alongside total size and order
  count at the top ten price levels" (DB-mbp10 L6). Not owned for ZL.
- MBP-1: "provides every order book event that updates the top price level, also known as the best bid and offer
  (BBO). This includes every trade and changes to book depth, alongside total size and order count at the BBO"
  (DB-mbp1 L6). Fields: action A, C, M, R, T (L20); side "the side that initiates the event ... **A**sk for a sell
  order (or sell aggressor in a trade), **B**id for a buy order (or buy aggressor in a trade), or **N**one" (L21);
  depth "The book level where the update event occurred" (L22); price and size "The order price" / "The order
  quantity" (L23-24); bid_px_00, ask_px_00, bid_sz_00, ask_sz_00, bid_ct_00, ask_ct_00 (L28-33); two-sided BBO
  changes get side N (L37). E.33's split keeps all of these (data33 59-63, MBP1_SPLIT).
- How Databento builds MBP-1 for CME: "Databento derives all of the less granular schemas starting from the most
  granular schema available. As you may have noticed from our schemas' descriptions, the majority of them--MBP, BBO,
  TBBO, trades, and OHLCV--are simply derived from MBO data." (DB-schema L77); "you can also derive one schema from
  another losslessly on the client side, and you should expect your self-derived data to be consistent with ours"
  (DB-schema L79). On GLBX: "it is important to use the `F_LAST` flag when calculating the best bid and offer, like
  our MBP-1 schema ... This is accounted for when we construct our other schemas, such as MBP-1 and Trades." (DB-glbx
  L39-42). Inference [not a Databento statement about GLBX specifically]: the owned ZL MBP-1 is a function of ZL's
  MBO stream restricted to the top level, so any quantity defined on the touch and on trades is the same from either
  schema; only order identity, order age and levels below the touch are lost.
- Trades: "Each trade summary in the message is normalized into one **T**rade record" (DB-glbx L57); MBP-n "include
  **T**rade records, but do not include **F**ill detail records" (L54); fills "do not modify the orders" (L62), so a
  resting order's size reduction after a fill arrives as a separate book record. "Implied trades ... may not have an
  aggressing side set. These trades will be normalized with side set to **N**one." (L70-71).
- Implied liquidity: "Databento combines the real and implied books, publishing the merged top-of-book on the
  [CMBP-1] schema" (DB-glbx L113). The owned file is MBP-1, not CMBP-1, so touch sizes are outright only (same
  conclusion as E.32 brief L2238-2242 for ZM and ZS/ZL; R3b's inference, now consistent with the GLBX page).
- Counts in the owned ZL file (DF 1.5 and 3.2): 158,046,466 records, 142,061,153 F_LAST records (1.113 records per
  event); T records 7,250,840 side A, 7,160,339 side B, 1,608,719 side N (10.04% unsigned); 165,388 F records whose
  meaning in MBP-1 is undocumented (DF 288-290); 848 F_SNAPSHOT and 848 F_BAD_TS_RECV records; 476 F_MAYBE_BAD_BOOK
  records; 564,084 A/C/M records with side N (two-sided BBO updates). Match algorithm K for every ZL outright (DF 53).

### 2.2 The table

Notation as E.32 P0.3 (P 46-81), with ZL replacing ZM: bid_1, ask_1, qb_1, qa_1 the ZL touch after a book update (an
F_LAST record), M_ZL the mid, ticks of 0.01 c/lb = USD 6. "Window of k minutes" on the open-time axis (pause and
close skipped). OFI e_n is E.32 F2.8's (P 433), already implemented for ZL MBP-1 in feat33 205-218 and 558-616.

| F3 item | ZL formula (MBP-1 or as stated) | From MBP-1? | Why | Needs MBO? | Verdict |
|---|---|---|---|---|---|
| F3.1-F3.3 OFI_k/Obar_k, k 1, 5, 15 | sum of e_n over ZL book updates in the window; Obar_k = trailing 20-date reference mean of abs(OFI_k) | yes | e_n uses only touch prices and sizes after each update; E.33 already built k 1, 5 from ZL MBP-1 (F2.10-F2.11, P 434; feat33 590-602) | no | carry over, windows changed to k 5, 15, 30 (section 3) |
| F3.4 IOFI5 | needs level-m OFI, m 1..5 | no | MBP-1 has the touch only | yes (or MBP-10) | drop. M1: multi-level gains are "contemporaneous" goodness of fit (E.32 brief L3814-3815, L3803) |
| F3.5-F3.6 TI_k, k 5, 15 | (B_k - S_k)/(B_k + S_k), aggressor contracts from T records, side N excluded | yes | MBP-1 T records carry the aggressor side (DB-mbp1 L21) and the size; one T record per trade summary as in MBO (DB-glbx L57) | no | carry over, k 5, 15, 30 |
| F3.7 QI1 on seasoned depth | exact form needs each order's last add or modify time | partial | MBP-1 has no order age; a causal proxy exists (2.3 b) | yes for the exact form | adapt: QI1s (proxy), plus a 5-minute average QIbar5 |
| F3.8 QI3 | levels 1-3 | no | touch only | yes (or MBP-10) | drop |
| F3.9 CR5 | contracts removed from the touch by cancels and size-reducing or price-changing modifies, fills excluded | partial | removals are visible as touch-size decreases on C and M records; fill lots must be attributed by price inside the batch, not by order id (2.3 c) | yes for order-id attribution | adapt |
| F3.10 SW5 | trade set sharing one ts_event that empties the pre-trade best ask (buy) or bid (sell) | yes | pre-trade touch and the touch after the set's batch are both in MBP-1; the set is defined by ts_event, not side, so side-N prints are included | no | carry over, window 15 (sparser events; 2.3 d) |
| F3.11 RF15 | add at the same price and side within 100 ms (ts_recv) after that touch level reached 0 through trades | yes | the re-add restores the touch, so it is a depth-0 A record; the depletion through trades is visible (T records at that price, then the level gone) | no | carry over |
| F3.12 lam60 | OLS slope of 1-minute dM_ZL on signed volume B - S over the trade-bearing intervals of the last 60 minutes / trailing 20-date median | yes | mids and signed T sizes only | no | carry over |
| C.3 spread | min(s_ZL(t), 5) ticks | yes | touch prices | no | carry over |
| C.4 touch depth | log(1 + qb_1 + qa_1) | yes | bid_sz_00 + ask_sz_00, outright only (no implied) | no | carry over |
| C.5 volume rate | log((V_ZL(15) + 1)/(Vbar + 1)), V from T records (sides A, B, N) | yes | as E.33 F1.5 (feat33 592: "MBP-1 trade (T) records only") | no | carry over |
| C.6 log sigma_ZL(D) | SD of 1-minute mid changes, 20 dates before D | yes | mids | no | carry over |
| C.7 days to expiry | from the front's last definition record before 08:30 CT | needs definitions | owned for discovery (Z4); for the test "not priced" (E.32b recs 4.5(c)) | no | carry over; the test needs ZL definitions 2017-05..2020-11 bought, or the expiry from the CBOT calendar rule (lead's choice) |
| C.11-C.14 flags | validity flags | yes | | no | keep one flag per family present |

### 2.3 Equations for the adapted and changed items

(a) OFI (F10.1-F10.3). e_n = 1{bid_n >= bid_{n-1}} qb_n - 1{bid_n <= bid_{n-1}} qb_{n-1} - 1{ask_n <= ask_{n-1}} qa_n +
1{ask_n >= ask_{n-1}} qa_{n-1} over consecutive good two-sided ZL book updates n-1, n (P 433; XGH eqs. 2-4, E.32
brief L3693-3697). OFI_k(t) = sum of e_n over updates with ts_recv in (t - k, t] on the open-time axis, with E.33's
rulings kept: no term for the first update of an open interval (FD3 a, feat33 597), an update whose own or previous
state is one-sided or bad contributes nothing and is counted (FD3 b, feat33 598-599), crossed or locked states
allowed (FD3 c, feat33 601). F10 feature: OFI_k/Obar_k, clipped to [-5, 5].

(b) Seasoned queue imbalance proxy (F10.7) and its 5-minute average (F10.8). Exact (E.32 P 437-438): S_b(t) = sum of
sizes of resting orders at bid_1(t) whose last add or modify has ts_recv <= t - 1.000 s. Claim: with MBP-1 alone,
  qb~(t) = 0                                   if bid_1 rose in (t - 1 s, t] (a new, higher level appeared),
  qb~(t) = min { qb_1(u) : u in [t_c, t] }     otherwise, t_c = max(t - 1 s, last time bid_1 changed),
where u runs over book-update states with ts_recv in [t_c, t] and the state as of t_c. Proof sketch: (i) a bid level
above every level that existed at some earlier instant contains only orders added or moved there after that
instant, so if bid_1 rose inside the last second, every order at bid_1(t) was added or modified within it and
S_b(t) = 0 exactly. (ii) Otherwise every seasoned order at bid_1(t) sat at that price through [t_c, t] with a size
at least its size at t (a size increase is a modify, which would unseason it), so qb_1(u) >= S_b(t) for every u in
[t_c, t] and qb~(t) >= S_b(t): an upper bound, equal to S_b(t) when no order arrived at the level inside the window.
When bid_1 fell inside the last second (the better level was consumed or cancelled), [t_c, t] is shorter than 1 s
and the bound is looser; that case is counted. Same for the ask with "ask_1 fell" in (i). QI1s(t) = (qb~ - qa~)/
(qb~ + qa~), invalid (0, G3) if the denominator is 0. QIbar5(t) = the mean of QI1s over the 300 one-second marks
ending at t (marks with an invalid value skipped; invalid if fewer than 150 valid).
What the proxy keeps: an order that flickers in and out within one second never enters qb~ (its arrival raises
qb_1 only after the minimum was set by the earlier, smaller size). What it loses against MBO: when new orders
arrive while old ones leave inside the same second, the minimum overstates seasoned depth.

(c) Touch cancellations (F10.9). For consecutive MBP-1 records j-1, j of the front (every record, not only F_LAST),
with action_j in {C, M}: on the bid, if bid_1(j) = bid_1(j-1) and qb_1(j) < qb_1(j-1), removed r_j = qb_1(j-1) -
qb_1(j); if bid_1(j) < bid_1(j-1), r_j = qb_1(j-1) (the level left); ask symmetric. Fill attribution: inside one
event batch (records up to and including the next F_LAST), let F_b = the sum of T sizes at price p = bid_1 before the
batch's first T record with the trade at p on the bid (sell aggressor, or side N at the bid price); the first F_b
contracts of r_j at p in that batch are fills and are not counted; lots do not carry across batches (E.33 ruling FD5,
feat33 455 "fill lots do not carry across event batches"). Cb_5, Ca_5 = the counted removals in the 5-minute window;
CR5 = (Ca_5 - Cb_5)/(Ca_5 + Cb_5), invalid if the denominator is 0. Side-N A/C/M records (two-sided updates) are
handled by the state difference, not by the record's side. Whether CME's post-fill size reductions appear in MBP-1
as C or M records in the same batch, or on the T record itself, is [unverified]; the definition counts correctly in
either case unless the reduction falls in a later batch. A run-stage data check (counts only): per batch with T
records at the touch, the share in which the touch-size decrease on C/M records equals the traded size.

(d) Sweeps (F10.10). A trade set = the T records sharing one ts_event (any side). pre-ask = ask_1 as of the record
before the set's first T; the set is a buy sweep if, at the set's batch end (its F_LAST record), ask_1 > pre-ask or
the ask side is empty; a sell sweep with the bid. SW15 = (sweeps_buy_15 - sweeps_sell_15)/sbar_15, sbar_15 = trailing
20-date reference mean of sweeps_buy_15 + sweeps_sell_15; invalid if sbar_15 = 0. Change from E.32 F3.10 (P 445):
the depletion is read at the batch end, not at record level, because in MBP-1 the resting-size reductions after a
fill may follow the T record (DB-glbx L62); the window is 15 minutes because sweeps are rarer than trades (their ZL
rate is not on disk; a sweep count is a run-stage data check).

(e) Refills (F10.11). As E.32 F3.11 (P 446): after a trade set empties the touch level p on side X (2.3 d), an MBP-1
A record with price p and side X whose ts_recv is within 100 ms of the batch end, that makes p the touch again, is a
refill on side X. RF15 = (refill_bid_15 - refill_ask_15)/rbar_15, rbar_15 = trailing 20-date reference mean of
abs(refill_bid_15 - refill_ask_15); invalid if rbar_15 = 0. Identical to the MBO count except that a refill by a
modify (M) of an existing order to price p is not counted in either version (E.32 says "an add").

(f) Lambda (F10.12). For each one-minute interval i of the 60 ending at t that contains T records: dM_i = M_ZL(end) -
M_ZL(start) in ticks, sv_i = B_i - S_i (contracts, side N excluded). lam60 = OLS slope with intercept of dM on sv
(numpy.linalg.lstsq on centred regressors, P 0.3), divided by the trailing 20-date reference median of the same slope;
invalid with fewer than 30 such intervals (P 450).

### 2.4 Worked ZL examples (illustrative; no data read; depth and sizes are assumptions)

(i) OFI. Assume ZL touch depth D = 30 contracts a side (assumption; no verified ZL touch size exists, F2_grains.md line
30 and 140). By CKS eq. 1 (E.32 brief L3701), a one-tick mid move needs OFI = 2D = 60 contracts; a 5-minute OFI of
+120 contracts goes with about +2.0 ticks (USD 12.00) of contemporaneous move. Forward, only rho x that survives in
expectation under the linear model: with rho = 0.1, about 0.2 tick, against c_f = 2.38 ticks.
(ii) TI. On a median date about 55 trade records a minute (section 3): a 5-minute window holds about 275; 165 buys
and 110 sells give TI5 = (165 - 110)/275 = 0.20, two iid standard errors (0.060 each). Under long-memory signs (C0
0.2, gamma 0.5, assumed) the null SD is 0.18, so TI5 = 0.20 is about one SD: a fitted model, not a threshold rule.
(iii) Seasoned proxy. Bid 52.40 c/lb shows 20 lots at t - 1 s, 8 lots at t - 0.4 s after a cancel, then a 15-lot add
at t - 0.2 s: qb_1(t) = 23, qb~(t) = min(20, 8, 23) = 8. The exact seasoned depth is at most 8 (it is 8 if the 8
remaining lots are old orders). The ask jumped from 52.42 down to 52.41 at t - 0.3 s: qa~(t) = 0. QI1s = (8 - 0)/(8
+ 0) = 1.0, while the unseasoned QI1 = (23 - qa_1)/(23 + qa_1) would be smaller: a just-improved offer counts as
unseasoned, which is the spoofing guard's purpose (P 219: "a CFTC soybean-complex spoofing case, hence seasoned
depth").
(iv) Sweep. Ask 52.41 shows 12 lots; a buy aggressor for 15 lots prints T 12 @ 52.41 and T 3 @ 52.42 at one ts_event;
after the batch ask_1 = 52.42 > 52.41: one buy sweep. If a 10-lot ask is re-added at 52.41 40 ms after the batch end,
that is an ask refill (RF counts it on the ask side).
(v) Lambda. Over 60 trade-bearing minutes, if the fitted slope is 0.05 ticks per net contract, a minute with +20 net
buying goes with +1.0 tick; divided by a trailing median slope of 0.04, lam60 = 1.25 (the book is 25% thinner than
usual). This is a conditioner (E.32 brief M1 4.7, L3966-3971), not a direction.

### 2.5 Data needs

Owned: ZL MBP-1 front month (Z3, 39 files), E.33's per-date split (DERIVED/split/ZL, split33 1-16, every MBP-1
field), ZL definitions inside Z4. Reused code: feat33.stream_mbp1 (558-616) already yields mids, OFI and T volume for
ZL; it does not yet count T sides, removals, sweeps, refills or the 1-second running minimum, so the run stage needs
an MBP-1 version of the ZM loop's F3 branches (feat33 333-553 is MBO-specific: order ids, seasoning per order,
pending fills per order id). Compute: one pass over 158 M records (DF 264), against 699 M for ZM MBO in E.33.

### 2.6 Verdict (a)

Carry over 8, adapt 2, drop 2 (IOFI5, QI3), add 1 (QIbar5, a 5-minute state average of the seasoned proxy, to give
the queue-imbalance block a 5-minute horizon). The F10 set stays at 12 features (section 7).

---------------------------------------------------------------------------------------------------------------------

## 3. (b) ZL's message rate and the minimum aggregation horizon

### 3.1 The rate (counts only)

Per trade date, whole ts_recv window [D-1 16:00, D 16:00) CT, 816 dates (DF 238-262; rule: min, lower median, p90
nearest rank, max):

| ZL MBP-1 count per date | min (date) | median | p90 | max |
|---|---|---|---|---|
| records | 63,170 (2023-06-21) | 188,737 | 249,130 | 486,639 |
| book events (F_LAST) | 54,999 (2023-06-21) | 168,917 | 225,487 | 448,862 |
| T records | 6,998 (2021-04-05) | 19,195 | 25,760 | 40,543 |

The day-session share is not on disk (DataFacts' reports/stage_e34_data_facts.md did not exist when this file was
written, 12:10-12:40 PDT; if it reports per-session counts, they replace the assumption below). Assumption: 83% of
events and trades fall in the 290-minute day session (ZM's day share of volume, P 130-133, "17% of volume"
overnight; ZL may differ). Then (m1_examples.out):

| day share | T records a minute: min / median / p90 / max date | book events a second: min / median / p90 / max date |
|---|---|---|
| 0.70 | 16.9 / 46.3 / 62.2 / 97.9 | 2.2 / 6.8 / 9.1 / 18.1 |
| 0.83 | 20.0 / 54.9 / 73.7 / 116.0 | 2.6 / 8.1 / 10.8 / 21.4 |
| 1.00 | 24.1 / 66.2 / 88.8 / 139.8 | 3.2 / 9.7 / 13.0 / 25.8 |

For scale: ZM's T records (both instruments) have a similar median per date (19,413, DF 251), so ZL trades about as
often as ZM by record count; ZL's book events are top-of-book only and so not comparable with ZM's MBO events.
Within Topstep's 1 s latency the median ZL book changes about 8 times: the entry price is not the price seen at t,
which is why P3.2's fill at the touch as of t + L stays.

### 3.2 Events per bucket for a stable imbalance

Criterion (stated, a design choice for the lead to accept or change): a window is long enough when, on the quietest
date, (i) the iid sampling SD of a trade-sign imbalance is at most 0.10, i.e. n >= 100 trade records, and (ii) the
chance of an empty window (feature invalid) is negligible. Long-memory signs widen the null spread: with sign
autocorrelation C0 l^-gamma (BGPW eq. 7, E.32 brief L3841-3842; Lillo and Farmer alpha about 0.6, L3905), Var(sum of
n signs)/n = 1 + 2 sum_{l<n} (1 - l/n) C0 l^-gamma; at C0 = 0.2, gamma = 0.5 (assumed, between BGPW's 1/5 and 2/3):

| k (min) | n quiet date (20/min) | SD iid | SD long memory | n median date (55/min) | SD iid | SD long memory |
|---|---|---|---|---|---|---|
| 1 | 20 | 0.224 | 0.374 | 55 | 0.135 | 0.282 |
| 5 | 100 | 0.100 | 0.240 | 275 | 0.060 | 0.184 |
| 15 | 300 | 0.058 | 0.179 | 824 | 0.035 | 0.138 |
| 30 | 601 | 0.041 | 0.150 | 1,648 | 0.025 | 0.116 |
| 60 | 1,202 | 0.029 | 0.125 | 3,296 | 0.017 | 0.097 |

Reading: criterion (i) is first met at 5 minutes on the quietest date. The long-memory column says that even
uninformative persistent flow produces |TI| of 0.15-0.25 at 5-30 minutes, so TI must enter a fitted model next to
its own trailing scale (the model learns what is extreme), not as a fixed threshold. Book-event features (OFI, CR)
have about 8 events a second, so a 5-minute window holds about 2,400 updates; the binding count is trades.

### 3.3 Against the decay of forward predictability

- "In no more than thirty minutes, order imbalances lose their predictive ability" (CRS 2005, E.32 brief L3821).
- CCZ's lagged cross-impact "mainly manifests at short-term horizons and decays rapidly in time" (L3819); own-OFI
  one-minute out-of-sample R2 negative (L3818).
- Grain abstracts: lagged order imbalance predicts "for some contracts" (Volkenand et al., L4324); Dalian meal OFI
  and TI predictability "diminishes over longer measure and price change frequency horizons" (Jin et al., L4327);
  both [abstract only] in E.32.
So the useful feature windows lie below about 30 minutes, the noise floor puts their lower end at 5 minutes, and
the labels are 15-60 minutes (band B). Windows: 5, 15, 30 minutes for flow (OFI, TI), 5 for cancellations, 15 for
the sparse event counts (sweeps, refills), 60 for the liquidity-state lambda (a conditioner; E.32 F3.12 needs 30
trade-bearing minutes). A 1-minute window is dropped: below the noise floor on quiet dates and the horizon at which
the published out-of-sample R2 is negative. Minimum aggregation horizon: 5 minutes.

Verdict (b): windows {5, 15, 30} for OFI and TI; 5 for CR; 15 for SW and RF; 60 for lambda; instantaneous state
(QI1s) only next to its 5-minute average.

---------------------------------------------------------------------------------------------------------------------

## 4. (c) Discovery on MBO or MBP-1; the test schema; the cost

### 4.1 What MBO would add on ZL

Exact seasoned depth (order age per order), exact fill attribution by order id (F3.9), levels 2-5 (F3.4, F3.8),
order ids for iceberg and large-order detection (E.32 brief M1 7.4, L4158-4162: "ZS and ZL MBP-1 cannot see icebergs
(no order IDs)"), queue composition. Under M1's verdicts these are: MLOFI "contemporaneous gains only" (SKIP as a
block, L3803), integrated OFI MAYBE as one feature, icebergs and refill rates MAYBE as conditioners (L4106-4111,
L4178-4184). None has forward evidence in futures at the band's horizons.

### 4.2 Why MBP-1 is enough for F10 discovery

1. Level-1 content is the same: CME MBP-1 is derived from MBO (DB-schema L77), and every F3 quantity defined on the
   touch and on trades is computable from it (section 2.2: 8 of 12 carried over, 2 adapted).
2. Exposure is the same either way: the discovery dates were read on ZL MBP-1 by E.31 (passive markouts, 1 s and
   10 s mid-move splits, queue-imbalance splits) and by E.33 (ZL mids and best-level OFI as inputs to ZM labels:
   F2.4-F2.6, F2.7, F2.10-F2.11 and the crush F1, P 412-434; values in E.33's feature store, not opened here).
   V50 item 4, quoted in E.32b recs 4.5(b): "Any test of an order-flow signal on these dates is therefore not a
   clean holdout". A purchased MBO stream covers the same dates and events, so it does not make discovery cleaner.
3. The same schema in both windows without a proof: if discovery uses MBP-1 and the test MBP-1, feature code is
   identical. MBO discovery with an MBP-1 test is ruled out (MBO-only features could not be computed in the test).
4. Compute: one pass over 158 M MBP-1 records with no book rebuild; ZL MBO would need a full order-book rebuild of a
   larger stream (its size is not on disk; ZM MBO was 699 M records against 158 M for ZL MBP-1, DF 264).
5. Fewer frozen parameters for features that the evidence rates lowest (multi-level weights, depth levels).

Costs of the choice: the spoofing guard is a bound, not the exact seasoned depth (2.3 b); CR5 attributes fill lots
by price inside the batch (2.3 c); no levels below the touch; no iceberg flag. These cost little against a program
prior of about 4% that is already conditioned on order flow carrying forward information at 15-60 minutes.

### 4.3 The test schema and dates

- ZL MBP-1, ZL.v.0, request 2017-05-21..2020-11-30, trade dates 2017-05-22..2020-11-30 (870 after a 20-date burn-in,
  shared facts). Before 2017-05-21 the data are MDP 2: "The `ts_recv` field on all MDP 2 data is set to the same
  value as `ts_event`" and "all records on MDP 2 data have the `F_BAD_TS_RECV` flag set" (DB-glbx L299-301), and
  "The highest granularity schema available for MDP 2 data is MBP-10" (L315). An MBP-1 test could technically start
  2017-05-01, but its first 15 dates would have no capture clock, so P1.4's ts_recv rules could not be applied the
  same way; keep E.32 P9's start (shared facts: "The 15 trade dates 2017-05-01..2017-05-19 stay sealed and untested").
- Definitions for C.7 in the test: not owned, not priced (E.32b recs 4.5(c)). Either buy them with the test data or
  drop C.7 (lead's choice; a feature computable in discovery but not in the test cannot stay).

### 4.4 Cost (E.32b recs 4.5(c) lines 625-636, estimates, not quotes)

| route | discovery | test | total |
|---|---|---|---|
| A: MBP-1 both windows (recommended) | owned, USD 0 | MBP-1 USD 23.36 | USD 23.36 |
| B: MBO both windows | MBO USD 19.48 | MBO USD 21.48 | USD 40.96 |
| C: MBP-1 discovery, MBO test with top of book derived from MBO | USD 0 | MBO USD 21.48 | USD 21.48 + an equivalence check |

Difference B - A = USD 17.60; MBO for discovery alone = USD 19.48. Route C is USD 1.88 cheaper than A but rests on
Databento's statement that schemas derive "losslessly" (DB-schema L79); "the same schema unless you show the features
are identical" needs a measured check: buy one discovery month of ZL MBO (about USD 0.50 at the census k of USD
0.4995 a month), derive the top of book with F_LAST batches, and compare record by record with the owned MBP-1 of
that month (counts and field equality only, no outcome). That check is a purchase and so the lead's and the user's
call; without it, route A.

Verdict (c): discovery on the owned ZL MBP-1; test on ZL MBP-1 2017-05-21..2020-11-30 (route A, USD 23.36,
estimate); the F10 list contains only MBP-1-computable features.

---------------------------------------------------------------------------------------------------------------------

## 5. (d) Leakage and look-ahead traps, each with a test

1. Clock (ts_recv versus ts_event). Every feature at t uses records with ts_recv <= t (P G1, P 0.3). ZL MBP-1:
   ts_recv trails ts_event by 0.1-10 ms for about 98% of records, precedes it for 0.146%, and 1 record of 158 M lags
   by >= 1 s (DF 92-104). Test: recompute features at ts_recv + 50 ms and confirm features change only for records
   inside the shift (no feature depends on ts_event); assert no record with ts_recv > t is read (truncate the day at
   t and compare, P4.1's future-scramble test).
2. Latency. Topstep L = 1.000 s: an order decided at t fills at the ZL touch as of t + L (P3.2), and the label starts
   at the fill. No feature may read (t, t + L]. Test: features at t are identical when every record after t is
   replaced by noise; label start >= t + L asserted in code.
3. Rolls. ZL.v.0 is a by-volume continuous series: 26 runs, 20 instruments (DF 153); it alternated ZLN1/ZLK1 on
   2021-04-04..04-10 and sat on ZLQ1 for 2021-06-29 and ZLQ2 for 2022-06-30 (DF 157). The owned file holds only the
   mapped instrument per date, so look-backs across a flip read a different contract's book. Rules: exclude the roll
   date and the next date from rows and trades (P1.4 rule, applied to ZL's front); sums (OFI, TI, CR, SW, RF, signed
   volume) and mids never span two instrument ids (a window that would is invalid, G3); trailing 20-date references
   and sigma chain across rolls (they are scales). Test: assert instrument_id is constant inside every summation
   window; count windows made invalid.
4. The 07:45-08:30 pause and the open. The book can be locked or crossed in the pause ("Before the trading session
   begins, or during the daily pause, it is normal for order books to be locked or crossed", DB-glbx L104). Rules:
   the open-time axis skips the pause (P 0.3); no OFI term bridges it (FD3 a); the decision grid starts at 08:35
   (P3.6 rule 1), so 5-minute windows at 08:35 cover 08:30-08:35 only, while 15- and 30-minute windows reach back
   into the overnight 07:15-07:45 (by the axis rule). The opening uncross prints at 08:30 likely carry side N
   [unverified for ZL]; TI excludes side N anyway, but C.5 volume and SW include them. Test: count T records with
   ts_recv in [08:30:00, 08:30:05) by side on 5 discovery dates (counts only) and report; if the uncross batch is a
   sweep by the 2.3 d rule, exclude the first batch after 08:30:00 from SW and RF (freeze one choice before any
   label).
5. The close. Every label span ends by 13:13:00, one minute before the 13:14-13:15 settlement window (P3.6 rule 2,
   stated for ZM; ZL's settlement window is [unverified] here and is assumed the same CBOT grains window). Latest
   label starts are 13:12:00 - h (P 0.3 grid). Note for the lead: the shared fact "latest 30-minute entry 10:50 PT"
   (12:50 CT) is later than the grid's 12:42 CT for h 30; the stricter one should bind. No feature reads after t,
   so the close affects labels, not features.
6. Trailing references. Obar, sbar, rbar, the lambda median and sigma use the 20 trade dates before D only (P 0.3).
   Test: references for D computed from a store truncated at D-1 16:00 CT equal the production values.
7. Records that are not book events. Exclude from every count: F_SNAPSHOT and F_BAD_TS_RECV records (848 each in
   the ZL file, DF 1.5 table), the 165,388 MBP-1 F records (meaning undocumented, DF 288-290), R records; a batch
   with F_MAYBE_BAD_BOOK (476 records) marks the book bad (feat33 stream_mbp1 docstring, READING FA-4). Test: totals
   by action before and after the filter, reported.
8. Side N. 10.04% of ZL T records have no aggressor side (implied trades, DB-glbx L70-71). TI and lambda exclude
   them; volume includes them; sweeps and refills define direction by the side that was depleted, not by the print
   side. Report the share dropped per date (R3b b.3, E.32 brief L2296-2298).
9. Seasoned proxy. qb~ uses only states with ts_recv in [t - 1 s, t]; the "rose within 1 s" test reads the touch
   price history in the same interval. Test: synthetic stream (P4.2 style) with a 0.5 s flicker order, a 2 s old
   order and an improving add: qb~ equals the hand value.
10. Fill attribution in CR5. Lots do not carry across batches (FD5). Test: synthetic batch with a T at the touch
    followed by an equal C reduction gives removal 0; a C without a T gives removal equal to its size.
11. Releases. Labels avoid [R - 2 min, R + 30 min] around 11:00 CT releases (P3.6 rule 3); features may span a
    release (known at t), with C.8-C.9 as flags. No extra trap.
12. Implied liquidity. Touch sizes are outright only (MBP-1, not CMBP-1; DB-glbx L113): depth and QI understate the
    executable touch; side-N prints with no visible resting quantity are likely implied matches. Stated, not
    corrected (no owned data can rebuild implied depth).

Verdict (d): traps 1-10 are tested in code before any label is read; 11-12 are stated in the protocol.

---------------------------------------------------------------------------------------------------------------------

## 6. Evidence table (sources used here)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| MBP-1 content | Databento MBP-1 schema | "provides every order book event that updates the top price level, also known as the best bid and offer (BBO). This includes every trade and changes to book depth, alongside total size and order count at the BBO." | pages/schemas_mbp-1.md L6 |
| MBP-1 trade side = aggressor | same | "**A**sk for a sell order (or sell aggressor in a trade), **B**id for a buy order (or buy aggressor in a trade), or **N**one where no side is specified" | same L21 |
| MBO content | Databento MBO schema | "provides every order book event across every price level, keyed by its order ID" | pages/schemas_mbo.md L6 |
| MBP derived from MBO | Databento "What's a schema" | "Databento derives all of the less granular schemas starting from the most granular schema available. As you may have noticed from our schemas' descriptions, the majority of them--MBP, BBO, TBBO, trades, and OHLCV--are simply derived from MBO data." | pages/schemas_whats-a-schema.md L77 |
| Client-side derivation lossless | same | "you can also derive one schema from another losslessly on the client side, and you should expect your self-derived data to be consistent with ours" | same L79 |
| F_LAST used to build MBP-1 on GLBX | Databento GLBX.MDP3 | "This is accounted for when we construct our other schemas, such as MBP-1 and Trades." | pages/datasets_glbx-mdp3.md L42 |
| One T record per trade summary | same | "Each trade summary in the message is normalized into one **T**rade record." | same L57 |
| Fills do not modify orders | same | "These records correspond to resting orders in the order book, but **do not** modify the orders." | same L62 |
| Implied trades unsigned | same | "Implied trades ... may not have an aggressing side set. These trades will be normalized with side set to **N**one." | same L70-71 |
| Merged implied top of book only in CMBP-1 | same | "Databento combines the real and implied books, publishing the merged top-of-book on the [CMBP-1] schema." | same L113 |
| Pause books locked or crossed | same | "Before the trading session begins, or during the daily pause, it is normal for order books to be locked or crossed" | same L104 |
| MDP 2 before 2017-05-21: no capture clock | same | "The `ts_recv` field on all MDP 2 data is set to the same value as `ts_event`." | same L299 |
| MDP 2 highest granularity | same | "The highest granularity schema available for MDP 2 data is MBP-10." | same L315 |
| Forward imbalance predictability gone by 30 min | CRS 2005 | "In no more than thirty minutes, order imbalances lose their predictive ability and returns are no longer negatively dependent." | E.32 brief L3821 |
| OFI same-window R2 65% | CKS 2014 | "with an average R2 of 65%" | E.32 brief L3810 |
| OFI autocorrelation vanishes | CKS | "In our data the autocorrelations at a timescale of 10 seconds are small and quickly vanish as well" | E.32 brief L3812 |
| MLOFI contemporaneous | XGH | "a simple, linear relationship between MLOFI and the contemporaneous change in mid-price" | E.32 brief L3814 |
| Cross-impact decays fast; own OFI OOS R2 negative | CCZ | "this lagged cross-impact mainly manifests at short-term horizons and decays rapidly in time"; Table 8 "OS R2 -0.37 -0.10 -0.36 -0.10 -0.36 -0.10" | E.32 brief L3818-3819 |
| Sign long memory | Lillo and Farmer 2004 | "The autocorrelation function decays roughly as τ −α with α ≈ 0.6" | E.32 brief L3905 |
| Extreme imbalance pins price | Patzelt and Bouchaud | "extreme order flow imbalance is not associated with large returns" | E.32 brief L3911 |
| Grain lagged imbalance [abstract only] | Volkenand, Filler, Odening 2018 | "For some contracts, returns can be predicted using lagged order imbalance." | E.32 brief L4350 |
| Dalian meal OFI/TI decays [abstract only] | Jin et al. 2023 | "while both OFI and TI are shown to predict future price changes, this predictability diminishes over longer measure and price change frequency horizons" | E.32 brief L4351 |
| Exposure of the discovery dates | V50 item 4 via E.32b | "Any test of an order-flow signal on these dates is therefore not a clean holdout" | E.32b recs 4.5(b), line 595-596 |

---------------------------------------------------------------------------------------------------------------------

## 7. Protocol inputs (F10, ready to paste into P4; a proposal for the lead, who freezes it)

Data: ZL MBP-1, ZL.v.0 front (discovery: the owned Z3 files via E.33's per-date split; test: ZL MBP-1 2017-05-21..
2020-11-30 after the single sealed read is assigned). Book updates = F_LAST records; excluded from all counts:
F_SNAPSHOT, F_BAD_TS_RECV, F and R records; a batch containing F_MAYBE_BAD_BOOK marks the book bad. Clock: ts_recv
(G1); "as of u" = last book update with ts_recv <= u. Ticks 0.01 c/lb = USD 6 (from the definitions). Windows of k
minutes on ZL's open-time axis (pause 07:45-08:30 and close 13:20-19:00 skipped; overnight minutes count). A window
spanning two instrument ids is invalid. Invalid values -> 0 and the F10 flag = 0 (G3). Trailing 20-date reference =
mean (or median where stated) over minute marks 08:35-13:13 of the 20 trade dates before D, chained across rolls.
Statistics conventions as P 0.3 (population SD; lstsq with intercept).

| ID | Definition | Window / parameters | Normalisation | Clip |
|---|---|---|---|---|
| F10.1-F10.3 | OFI_k = sum over consecutive good two-sided ZL book updates in (t - k, t] of e_n = 1{bid_n >= bid_{n-1}} qb_n - 1{bid_n <= bid_{n-1}} qb_{n-1} - 1{ask_n <= ask_{n-1}} qa_n + 1{ask_n >= ask_{n-1}} qa_{n-1}; no term for the first update of an open interval; a pair with a one-sided or bad state contributes 0 and is counted; crossed or locked states allowed | k = 5, 15, 30 min | / Obar_k = trailing 20-date reference mean of abs(OFI_k); invalid if Obar_k = 0 | [-5, 5] |
| F10.4-F10.6 | TI_k = (B_k - S_k)/(B_k + S_k): B_k (S_k) = contracts of T records with side B (A) and ts_recv in (t - k, t]; side N excluded | k = 5, 15, 30 min; invalid if B_k + S_k = 0 | none (bounded) | no |
| F10.7 | QI1s = (qb~ - qa~)/(qb~ + qa~): qb~ = 0 if bid_1 rose in (t - 1 s, t]; else min of qb_1 over the book states with ts_recv in [t_c, t] and the state as of t_c, t_c = max(t - 1.000 s, last change of bid_1); qa~ symmetric (ask_1 fell -> 0) | seasoning 1.000 s | none | no |
| F10.8 | QIbar5 = mean of QI1s at the 300 one-second marks t - 299 s .. t (on the open-time axis; invalid marks skipped) | 5 min; invalid if fewer than 150 valid marks | none | no |
| F10.9 | CR5 = (Ca_5 - Cb_5)/(Ca_5 + Cb_5): Cb = contracts removed from the bid touch by C or M records (state difference record to record: same price and lower size -> the decrease; touch price fell -> the whole previous size), less, within one event batch, the T contracts printed at that bid price (first lots attributed to fills; no carry across batches); Ca symmetric | 5 min; invalid if Ca_5 + Cb_5 = 0 | none | no |
| F10.10 | SW15 = (sw_buy_15 - sw_sell_15)/sbar_15: a trade set = T records sharing one ts_event (any side); buy sweep if at the set's batch end ask_1 > the ask_1 as of the record before the set's first T, or the ask side is empty; sell sweep symmetric on the bid | 15 min | sbar_15 = trailing 20-date reference mean of sw_buy_15 + sw_sell_15; invalid if 0 | [-5, 5] |
| F10.11 | RF15 = (rf_bid_15 - rf_ask_15)/rbar_15: a refill on side X = an A record at price p, side X, ts_recv within 100 ms after the batch end of a trade set that emptied touch level p on side X (F10.10 rule), that makes p the touch again | 15 min; refill window 100 ms | rbar_15 = trailing 20-date reference mean of abs(rf_bid_15 - rf_ask_15); invalid if 0 | [-5, 5] |
| F10.12 | lam60 = OLS slope (with intercept) of dM_i (ZL mid change over 1-minute interval i, ticks) on sv_i = B_i - S_i (contracts, side N excluded), over the trade-bearing 1-minute intervals among the 60 ending at t | 60 min; invalid with fewer than 30 intervals | / trailing 20-date reference median of the same slope | [-5, 5] |

Context block for a ZL-traded program (E.33's C with ZL replacing ZM; the lead decides the block for the whole
registration): C.1 tod, C.2 tod^2 (08:35-13:13 axis); C.3 min(s_ZL(t), 5) ticks; C.4 log(1 + qb_1 + qa_1) of ZL at t;
C.5 log((V_ZL(15) + 1)/(Vbar + 1)), V from T records of all sides; C.6 log sigma_ZL(D); C.7 days to the ZL front's
expiration / 60, capped (needs test-window definitions, section 4.3); C.8-C.9 release flags; C.10 Monday or first
date after a closure; C.15 June-August; one validity flag per family.

Parameters frozen here: windows {5, 15, 30} (OFI, TI), 5 (CR, QIbar), 15 (SW, RF), 60 (lambda, minimum 30
intervals); seasoning 1.000 s; refill 100 ms; reference length 20 dates; clip 5. Dropped from E.32 F3: F3.4 IOFI5,
F3.8 QI3 (need depth beyond level 1); F3.1-F3.3's 1-minute window. Not added: bid_ct_00/ask_ct_00 order-count
features (available in MBP-1, no forward evidence read), microprice (SKIP as a signal, E.32 brief M1 5.7).

Run-stage data checks before any label (counts only, no outcome): (1) day-session share of ZL events and T records
(replaces section 3.1's 83% assumption); (2) per batch with T at the touch, whether the C/M touch decrease equals the
traded size (validates F10.9's attribution); (3) sweeps and refills per 15 minutes on 5 dates (validates the
normaliser floors); (4) side-N share at 08:30:00-08:30:05 (trap 4); (5) the share of seconds in which the touch price
fell, where QI1s's bound is looser (trap 9).

---------------------------------------------------------------------------------------------------------------------

## 8. Not finished, unverified, and failures

- Day-session message counts for ZL: not on disk; DataFacts' file was absent when I checked (12:17 PDT). Section 3
  uses an assumed 83% day share and gives 70% and 100% bounds. The horizon verdict (5 minutes) holds at 70% (17 T
  records a minute on the quietest date: n = 85 in 5 minutes, iid SD 0.11, slightly above the 0.10 criterion; the
  quietest date, 2021-04-05, is the Monday after Good Friday).
- Unverified: whether CME post-fill size reductions in Databento MBP-1 sit on the T record or on following C/M
  records in the same batch (F10.9 handles both, not a later batch); the meaning of the 165,388 F records in the ZL
  MBP-1 file; the side of ZL opening-uncross prints; ZL's settlement window (assumed 13:14-13:15 CT as for ZM); the
  claim that GLBX MBP-1 is derived from MBO rests on Databento's general schema page, not on a GLBX-specific
  sentence.
- No ZL touch depth or spread is verified anywhere on disk (F2_grains.md lines 30, 140, 160: a 2.06-tick US-hours
  spread for 2022 exists only as a snippet); the worked examples use an assumed depth of 30 lots. If ZL's spread is
  often 2 ticks, the shared assumption S = 1.0 tick in c_f is optimistic; C.3 measures it.
- Rule 3: E.33's ZL-derived feature values (F2.4-F2.7, F2.10-F2.11, F1) and E.31's ZL passive-markout statistics
  exist on the discovery dates; I did not open their outputs and give no file:line for the values (the protocol
  definitions are at P 412-434; E.31's reading is described at E.32b recs 4.5(b) lines 594-596).
- Rule 9 deviation: pages were saved with curl directly, not first read with WebFetch, because a raw copy was
  required and the Databento docs serve plain markdown; all 7 fetches succeeded (pages/log.tsv). 1 WebSearch used
  (no budget notice). No Scrapling or Firecrawl needed.
- The 12:42 CT versus 12:50 CT latest 30-minute entry (trap 5) is flagged for the lead, not resolved.


---

<!-- concatenated unchanged: reports/stage_e34_briefs/M2_F09_ZL.md (sha256 da1e75ff995e7d36) -->

# M2. F09 into ZL: soy-complex (and energy) lead-lag and relative value with ZL as the traded leg

Stage E.34, ZL methods addendum, part M2. Worker MathReaderM2-OpusHigh, 2026-10-29 (started 12:10 PDT).
No market data was opened, no price, return, feature or model output was computed, nothing was trained, N stays 838.
Every number below is either quoted (with its source) or hand arithmetic on the shared ZL facts in BRIEFS.md
`## RULES`; the arithmetic is reproduced by work/MathReaderM2-OpusHigh/scripts/m2_examples.py, which writes
work/MathReaderM2-OpusHigh/m2_examples.json (sha256 prefix a426a5eab43aedde). Values from that JSON are named by key.

Files:
- Pages fetched in this stage, with the log: reports/stage_e34_briefs/work/MathReaderM2-OpusHigh/pages/ (log.tsv).
- Reused verified quotes: the E.32 methods brief (reports/stage_e32_methods_brief.md), cited as "E.32 brief
  <section>:<line>", and two E.32 saved pages read by grep for passages the brief did not quote
  (reports/stage_e32_briefs/pages/R3a_crush/zhou_jcm2023_wur.pdf.txt and rechner_poitras_1993.pdf.txt).

Conventions (as E.32 M2 and the E.32 protocol 0.3):
- Prices: S = ZS in cents/bu, O = ZL in cents/lb, M = ZM in USD/short ton; nS, nL, nM = the same prices in ticks
  (0.25 c/bu, 0.01 c/lb, 0.10 USD/ton). ZL tick = USD 6.00.
- Board crush in cents/bu: C = 11 O + 2.2 M - S = 0.11 nL + 0.22 nM - 0.25 nS (E.32 brief M2 c, 4718-4728; E.32
  protocol F1, line 413). One ZL tick moves C by 0.11 c/bu, so a 1 c/bu crush dislocation closed by ZL alone is
  1/0.11 = 9.09 ZL ticks (1/11 c/lb) = USD 54.55 a ZL contract (m2_examples.json zl_ticks_per_cent_crush).
- Cost: Topstep ZL round trip c_f = 2.38 ticks (E.32b holding scope 15). sigma_h (ticks): h1 5.52, h5 12.05, h15
  20.37, h30 28.10, h60 38.21 (E.32b holding scope 15). Band B = 15, 30, 60 minutes.
- [derived] marks my algebra; [unverified] a claim without fetched full text; [u] an assumption.

## Bottom line (for the lead)

1. (a) Crush residual, ZL adjusting. The mechanism is the same residual E.33 used (F1), read for the ZL leg. The
   expected gross per trade is G = s_L x D x (1 - 2^-m) / 0.11 ZL ticks (s_L = ZL's share of the closure, D the
   dislocation in c/bu, m the hold in half-lives). Break-even share s_L* = 2.38 x 0.11 / (D (1 - 2^-m)): 0.52 at
   D = 1 c, m = 1; 0.35 at m = 2; 0.26 even with full reversion. ZL is cheaper per crush cent than ZM was (ZM needed
   0.70 at D = 1, m = 1), but its noise is larger, so cost per sigma is about the same (ZL 0.085, ZM 0.092). The
   published evidence gives no s_L, no intraday half-life, and the one intraday source says leadership moves with
   relative volume. Verdict: USE, as the crush set of F09, with ZL-specific normalisation (a ZL-dependent regression
   residual) and an origin split (did ZL move, or did the others?).
2. (b) ZS and ZM leading ZL. Minute look-backs (1, 5, 15, 30) are allowed; seconds are not (E.32 M2 b). The useful
   form is one "implied-oil gap" (how far ZL lags what the ZS and ZM moves imply through the crush), plus each
   leader's own scaled return. Bars suffice for the leaders at minute look-backs; the leaders' books would make the
   test-window read a new purchase (ZS and ZM book data for 2017-05..2020-11 are not owned; only their ohlcv-1m bars
   are, inside the sealed files). Verdict: USE, bars only for ZS and ZM.
3. (c) CL, HO, RB. HO and RB are not owned for either window (only 2025-04..2026-06, closed): EXCLUDE. RINs have no
   owned or free intraday series: EXCLUDE. CL bars are owned for both windows, but E.12 and E.20 already used CL's
   60-minute return as a lead on ZL (R1-11, R1-15; no pass), and the test window's 2019-05..2020-11 ZL bars were read
   in those trials. The literature found links energy to vegetable oil weekly or daily, through biodiesel pricing,
   with no intraday evidence. Verdict: EXCLUDE CL from F09's registered sets. Fallback if the lead wants it: one
   disclosed context feature (CL scaled return at k = 15), never a set of its own.
4. (d) Which leg adjusts. Use the VECM loadings alpha on (ZS c, ZL ticks, ZM ticks), the adjustment share s_L, the
   weak-exogeneity restriction alpha_L = 0, the bivariate device (oil value against implied oil value) for IS, CS
   and ILS, and the OU half-life hl = -ln 2 / ln phi with phi = 1 + beta'alpha. They must not select anything. Two
   uses are clean: (i) causal features (prior-date estimates of s_L and hl inside each training fold), and (ii) a
   report-only diagnostic computed for every set after the search, whether or not anything passes. (E.33 made the
   VECM a Tier-A-only P6.5 diagnostic, so the program never measured which leg adjusts.) Literature: intraday (Zhou
   et al., 2015 data) both ZS and ZM Granger-cause ZL more as ZL's relative volume rises; daily evidence has beans
   adjusting (Adrangi; Liu and Sono, abstracts) and, in the renewable-diesel regime, biofuel shocks starting in ZL
   (Avileis and Swanson, daily). So ZL is a plausible follower to bean and meal shocks and the origin of biofuel
   shocks.
5. (e) E.33's ZM negative constrains the ZL prior two ways that pull apart. The shares sum to 1, so evidence that
   ZM does not close the residual moves share toward ZS and ZL. But E.33 also failed in a way consistent with a
   common cause: no tradable minutes-scale reversion or propagation in the complex net of costs, at a cost per sigma
   (0.092) that ZL barely improves on (0.085). Net reading: E.33 rules out "ZM adjusts strongly" but not "ZL
   adjusts"; it is weak, mildly negative evidence for F09 on ZL. E.32b's about 2.5% for F09 is not contradicted.
   The prior number is the lead's decision.
6. (f) Protocol inputs. A 17-feature F09 list (crush 8, propagation 9) and a V28 rule variant (4 rules x 3 holds
   = 12). My judgment: F09 built only from bars is not an order-book strategy, so under a literal V43 it must be
   rules (V28). The ML form is admissible only if the lead rules, as E.33's precedent allows, that sets traded and
   labelled on ZL's own book inside the order-book program count as order-book strategies. That ruling is reserved
   for the lead.

## (a) The crush residual with ZL as the adjusting leg

**1. Core idea.**
- E.33 asked whether ZM closes crush dislocations. Here the same relation is read for ZL: when C = 11 O + 2.2 M - S
  is far from its causal mean, does ZL move to close it within 15-60 minutes, and by enough to pay 2.38 ticks?
- Two things change against E.33's F1. First, the residual's normalisation: an Engle-Granger (OLS) residual depends
  on which leg is the dependent variable, so F1.3 (ZM on ZS and ZL) has to be re-fitted with ZL as the dependent
  variable. Second, the dislocation's origin. In the discovery regime the oil leg carries its own biofuel shocks
  (section (d)). A dislocation that ZL itself opened is a margin change ZL caused, not a ZL lag, and fading it fades
  news. So the crush set needs a feature that says which leg opened the gap.

**2. Equations.**
- Crush level and its z-scores are leg-agnostic, so E.32 protocol F1.1, F1.2 and F1.4 (lines 418-421) carry over
  unchanged: zC_k(t) = (C(t) - mean_k)/sd_k over the minute marks t - j, j = 1..k, inside the segment. The sign is
  the one difference: zC > 0 (crush wide: oil plus meal rich against beans) means sell ZL when ZL is the closer.
- ZL-dependent residual (the F1.3 mirror) [derived from protocol line 420 by swapping the roles of ZM and ZL]:
  before D's open, OLS on the clean 1-minute samples 08:35-13:13 of the 10 trade dates before D in the current
  segment (at least 3, or invalid):
      O = a + b_S S + b_M M + eps   (natural units: c/lb on c/bu and USD/ton; centred fit, a from the means)
      e_L(t) = (O(t) - a - b_S S(t) - b_M M(t)) / 0.01   [ZL ticks],   zRL(t) = e_L(t) / sd_e.
  e_L > 0 means ZL is rich against beans and meal: sell ZL.
- Physical hedge ratios, against which the rolling b_S and b_M are read [derived]: from C = const, O = (S - 2.2 M +
  C)/11, so b_S = 1/11 = 0.0909 c/lb per c/bu and b_M = -2.2/11 = -0.200 c/lb per USD/ton. In ticks, a 1-tick ZS
  move implies 0.25/0.11 = 2.273 ZL ticks; a 1-tick ZM move implies -0.22/0.11 = -2.000 ZL ticks
  (m2_examples.json zl_ticks_per_zs_tick, zl_ticks_per_zm_tick). Per ZL contract (60,000 lb of oil = 60,000/11 =
  5,454.5 bu), the crush-neutral position is 5,454.5/5,000 = 1.091 ZS and 5,454.5 x 0.022 = 120.0 tons = 1.200 ZM:
  the board's 9 ZL : 10 ZS : 11 ZM scaled to one ZL lot (9 x 1.091 = 9.82, about 10; 9 x 1.2 = 10.8, about 11). The
  traded position is ZL alone; the ratios only define the residual.
- Why rolling, never fixed physical weights: Janzen and Wang's weekly cash regression of soybean on meal and oil
  changes moved from 0.511 dSBM + 0.232 dSO (2007-2020) to 0.451 dSBM + 0.070 dSO (Oct 2020-Sep 2025), "a
  previously stable relationship among soybean crush components has broken down" (E.32 brief R3a 2.1, 1497-1501; the quote at 1500).
  The oil coefficient is the one that collapsed, so a ZL-dependent residual with fixed weights would be most wrong
  exactly in the leg traded here. The E.32 protocol's rule stands: levels are "normalised by causal rolling
  statistics, never fixed cents" (protocol F1, line 194).
- Origin split [new, derived]: over the last k = 30 minutes the crush change splits into leg contributions
  dC_30 = 11 dO_30 + 2.2 dM_30 - dS_30. ZL's signed share of the absolute contributions:
      oL30 = 11 dO_30 / (|11 dO_30| + |2.2 dM_30| + |dS_30|),   in [-1, 1]; invalid when the denominator is 0.
  |oL30| near 1: ZL opened the dislocation (biofuel-type shock; do not fade). |oL30| near 0: beans or meal opened it
  (ZL lags; the catch-up case of section (b)).
- Trade arithmetic (E.32 M2 f, 5093-5121, rewritten for ZL) [derived]: with ZL's adjustment share s_L (section d), a
  dislocation D = |C - m| c/bu and a hold of m half-lives (m = h / hl),
      expected gross G = s_L x D x (1 - 2^-m) / 0.11 ZL ticks;   break-even share s_L* = 2.38 x 0.11 / (D (1 - 2^-m)).
  Including the test's minimum detectable edge (K2: stop if the best discovery net edge is below e80_test, 1.81
  ticks at h 30), a configuration needs G >= 2.38 + 1.81 = 4.19 ticks at h 30 (E.32b recs 4.5(a), "c_f +
  e80_test 4.19"), i.e. s_L x D x (1 - 2^-m) >= 4.19 x 0.11 = 0.461 c/bu.

**3. Worked ZL example** (illustrative prices, not data).
- Prices: ZS 1,300.00 c/bu, ZL 60.00 c/lb, ZM 380.0 USD/ton: C = 660 + 836 - 1,300 = 196 c/bu.
- ZS rises 4 ticks (1.00 c/bu) in 10 minutes; ZL and ZM do not move. C falls 1.00 c/bu; oL30 = 0 (beans opened it).
  If ZL alone closes it (s_L = 1), ZL rises 1/0.11 = 9.09 ticks = USD 54.55 a contract.
- Against sigma_30 = 28.10 ticks, the full 9.09-tick closure is 0.32 sigma: a 1 c/bu dislocation is small relative
  to ZL's own 30-minute noise. In crush units ZL's 30-minute sigma is 28.10 x 0.11 = 3.09 c/bu.
- Break-even share s_L* (m2_examples.json breakeven_sL; rows D in c/bu, columns m = 1 / 2 / 3 / full reversion):

| D | m = 1 | m = 2 | m = 3 | full |
|---|---|---|---|---|
| 0.5 | 1.047 (impossible) | 0.698 | 0.598 | 0.524 |
| 1 | 0.524 | 0.349 | 0.299 | 0.262 |
| 2 | 0.262 | 0.175 | 0.150 | 0.131 |
| 3 | 0.175 | 0.116 | 0.100 | 0.087 |

  Check of one cell: 2.38 x 0.11 / (1 x 0.5) = 0.2618 / 0.5 = 0.5236. Gross at s_L = 1, D = 1: 4.545 / 6.818 /
  7.955 ticks at m = 1 / 2 / 3 (gross_sL1_D1).
- Against ZM (E.32 M2 f table, 5134-5135): at D = 1, m = 1 ZM needed 0.70, ZL needs 0.52. One crush cent is 9.09 ZL
  ticks against 4.55 ZM ticks, and the cost in ticks is 2.38 against 1.59: 2.38/9.09 = 0.262 c against 1.59/4.545 =
  0.350 c. ZL is about 25% cheaper per crush cent closed.
- Hold against half-life (halflife_vs_hold; D = 1 c): hl 10 min gives s_L* 0.405 / 0.299 / 0.266 at h 15 / 30 / 60;
  hl 20 min 0.646 / 0.405 / 0.299; hl 30 min 0.894 / 0.524 / 0.349; hl 60 min 1.646 / 0.894 / 0.524. A half-life
  near or above the hold makes every D near 1 c unpayable.
- With the K2 edge included (G >= 4.19 at h 30), the D needed is 0.461 / (s_L (1 - 2^-m)): s_L = 1: 0.92 / 0.61 /
  0.53 c at m = 1 / 2 / 3; s_L = 0.5: 1.84 / 1.23 / 1.05 c; s_L = 0.25: 3.69 / 2.46 / 2.11 c.
- With the hypothetical VECM of section (d) (s_L = 0.142, hl 17.6 min), ZL's full eventual move per cent of
  dislocation is 1.29 ticks, below 2.38 even with full reversion. The family is alive only if s_L is well above
  that illustration.
- Spread sensitivity: c_f assumes a 1.0-tick ZL spread [u]. The only published ZL figure is a search snippet, "US
  hours 2.06 ticks" for Q1-Q3 2022 (F2_grains.md line 54, GRAINS-35, unverified). At S = 2.06, c_f = 2.06 + 0.5 +
  0.88 = 3.44 and s_L* at D = 1, m = 1 rises to 0.757 (cf_spread206). DataFacts or the run stage should measure the
  ZL day-session spread on discovery MBP-1 before freezing c_f; that is a count-type fact, not an outcome.

**4. Data.**
- 1-minute prices of ZS, ZM and ZL in the day session (08:30-13:20 CT), on one clock. For ZL, the BBO mid from its
  own book where the program buys or owns it (MBP-1 owned for discovery; F10's book purchase covers the test). For
  ZS and ZM, ohlcv-1m closes in both windows (section (b) for why bars). Bar volumes for the volume-share features.
- Front-month map and segments as E.32 protocol G2 (lines 372-376): ZS has no October or December contract, so
  autumn segments mix months [DataFacts confirms months from the definitions]. ohlcv-1m v.0 bars roll on
  Databento's continuous rule; segment breaks must come from the definitions or the bars' instrument_id.
- Executable prices: ZL ask/bid at decision + 1 s (E.33 P3.2) if the ZL book is used; with bars only, the next bar's
  open plus the full c_f.

**5. Leakage and look-ahead traps** (E.32 M2 c (i)-(v), 4797-4815, all apply; ZL-specific additions):
- (i) Normalisation leak: an OLS residual fitted on the same day it is used is look-ahead (Zhou's per-day smoother
  is description only, E.32 brief M2 bottom line 4, 4459-4461). Test: future-scramble invariance; the
  coefficients for D equal those from a run truncated at D's open.
- (ii) Bounce and staleness in the leg that is also the label. If C(t) uses ZL's last trade and the label starts
  at ZL's next price, bid-ask bounce in ZL makes a spurious "reversion" that the label confirms. Use ZL's BBO mid in
  C when the book exists (MathReview A-3, E.32 brief 4788); with bars, require each leg's last trade within a frozen
  staleness limit (for example 2 minutes) and test with a +1-bar shift of the feature (the edge must not jump).
- (iii) Stale leaders. A minute without a ZS or ZM trade has no bar (ohlcv bars come from trades); forward-filling a
  stale close makes a dislocation that "closes" when the leg next trades. Test: count entries whose leaders' last
  trade is older than the limit; it must be 0.
- (iv) Origin features use dO_30, which overlaps the label only if the label start is inside the 30-minute window;
  it is not (labels start at t + L). Test: oL30 at t is unchanged when all data after t is scrambled.
- (v) Regime: biofuel-policy days (EPA RVO and SRE announcements, mostly unscheduled) give ZL-origin dislocations
  that persist (section (d)). Not a leak; an exclusion by date list would be one, because the dates are known only
  afterwards. Any filter must be causal (for example a 20-date realised-volatility state), or the days stay in.

**6. Compute.** As E.32 M2 c and f (4817-4822, 5180-5183): about 2.6 million rows over the windows, rolling OLS per
date in milliseconds, RAM under 1 GB.

**7. Verdict: USE** as F09's crush set on ZL, with three frozen choices: the ZL-dependent rolling residual zRL (10
dates, in segment), the origin share oL30 and its interaction with zC30, and ZL's volume share. Drop F1.7/F1.8 (the
overnight crush gap): its once-a-day form is K6-crushgap-01 (R1-08), null on 2019-05..2024-02 in E.22, and the test
window's 2019-05..2020-11 bars were read for it (seal section 4). It adds exposure and little that is new.

## (b) ZS and ZM leading ZL at minute look-backs

**1. Core idea.**
- News about bean demand (exports, crush pace, weather) reaches ZS first, the most liquid leg (median v_0 ADV
  77,862 against ZM's 36,690; E.32 protocol F2, line 200). Meal news reaches ZM. The question is whether ZL prices
  the implied change in oil value with a delay of minutes. A delay could come from slower spread and processor flow,
  as the E.32b dossier frames it ("through crush margins that a slower participant set prices with a delay", E.32b
  recs 4.5, 540).
- Seconds are out of reach: in E.32 M2 (b), a pure-shift lead of 1-2 s leaves 0.20-0.53 ticks of predictable move
  after 0.3 s latency on ZM, and "a naive strategy based on market orders cannot make any profit of this effect"
  (Huth and Abergel, E.32 brief 4693). De Boer et al. put soybean-complex liquidity spillovers "mainly within 30 s"
  (F2_grains.md line 80, GRAINS-24, abstract). F09 therefore tests whether a minutes-scale residue exists, at
  look-backs of 5-30 minutes and holds of 15-60.
- The leaders matter only through what they imply for oil. With meal fixed, a bean move implies an oil move of the
  same sign. With beans fixed, a meal move implies an oil move of the opposite sign (oil plus meal value must match
  beans). That is why one implied-oil gap, not separate ZS and ZM returns, is the primary propagation feature.

**2. Equations.**
- Scaled leader returns (E.32 protocol F2.1-F2.6, lines 430-431, with the roles of the legs swapped):
  rX_k(t) = (P_X(t) - P_X(t - k min)) / (tick_X x sigma_X(D) x sqrt(k)), X in {ZS, ZM}, k in {5, 15, 30}; sigma_X(D)
  as protocol 0.3 (lines 60-62: the SD of 1-minute changes over 08:35-13:13 of the 20 prior dates, chained across
  rolls).
- Implied-oil gap with physical weights (the F2.7 mirror) [derived]:
      g_k = [ (dS_k - 2.2 dM_k)/11 - dO_k ] / 0.01 / (sigma_ZL(D) sqrt(k))   (natural units for dS, dM, dO)
  Identity: (dS - 2.2 dM)/11 - dO = -(11 dO + 2.2 dM - dS)/11 = -dC_k/11 c/lb, so g_k = -dC_k / (0.11 sigma_ZL(D)
  sqrt(k)): the k-minute crush change in ZL ticks, sign reversed. g_k > 0: ZL rose less than beans and meal imply;
  buy ZL.
- Regression-weight gap (preferred; uses the zRL fit of (a)): gR_k = [ b_S dS_k + b_M dM_k - dO_k ] / 0.01 /
  (sigma_ZL(D) sqrt(k)), with b_S, b_M frozen for D. The physical weights treat every bean move as an oil move. The
  weekly evidence says that since late 2020 beans move with oil far less (oil coefficient 0.070; E.32 brief 1499).
  So g_k mostly measures crush-margin changes that need not reverse, and gR_k uses the empirical co-movement instead.

**3. Worked example** (m2_examples.json b_example).
- ZS +4 ticks (1.00 c/bu) over 15 minutes; ZM and ZL unchanged. Physical gap: 1/0.11 = 9.09 ZL ticks; g_15 = 9.09 /
  20.37 = 0.446 (sigma_15 20.37 measured, not sqrt-scaled).
- If ZL closes a fraction f of the gap within a 30-minute hold, the gross is 9.09 f; break-even f = 2.38/9.09 =
  0.262. At f = 0.5: gross 4.545, net 2.165 ticks, per-trade Sharpe 2.165/28.10 = 0.0771, and (3/0.0771)^2 = 1,516
  trades for t = 3 before any deflation. That is about 1.9 trades a date over 796 OOF dates, under the 9-a-day cap.
- How big are bean moves in oil terms? ZS's 15-minute sigma under random-walk scaling is 3.11 x sqrt(15) = 12.05 ZS
  ticks = 3.01 c/bu. With meal fixed it implies 27.4 ZL ticks, 1.34 times ZL's own 15-minute sigma
  (zs_1sigma15_implied_over_zl_sigma15). ZL cannot be following the physical identity tick for tick, or its sigma
  would be larger. Most bean moves are absorbed by the margin and by meal. The physical gap is therefore large and
  mostly not a ZL lag, which is the case for gR_k.
- Bounce in bar closes (half a tick per leg, in ZL ticks: ZS 1.136, ZM 1.000, ZL 0.5; combined SD 1.594 ticks,
  bounce_gap_sd_ticks): 13% of sigma_5, 8% of sigma_15, 6% of sigma_30. Bars are adequate at k >= 5; at k = 1 bounce
  is 29% of sigma_1 (1.594/5.52), so k = 1 is dropped.

**4. Data: bars or books.**
- Bars suffice for the leaders. At look-backs of 5-30 minutes the close of an ohlcv-1m bar is a trade price within
  the minute; staleness and bounce are second-order (above) and can be bounded by a staleness rule. The leaders'
  books would add order-flow features (E.32 protocol F2.8-F2.11, ZS and ZL OFI). The only positive forward
  order-flow finding in E.32's sources is cross-asset and lagged (E.32 protocol F2, line 204), but it decays within
  about 30 minutes, and its fast part is what HFT takes.
- Test-window consequence (the decisive point): ZS, ZM and ZL ohlcv-1m for 2017-05..2020-11 are owned inside the
  sealed soy files (E.32b recs 4.5(c), the "test, F09" row, line 644). No ZS or ZM book data for the window was ever
  bought ("No order-book data (MBO, MBP, trades) for the window was ever bought or read", seal section 4,
  reports/stage_e32_test_seal.md 117-119). A frozen model whose leaders use ZS MBP-1 or ZM MBO features would make
  the one test read require buying ZS and ZM book data for 2017-05..2020-11 as well as ZL's. That purchase is not
  priced (E.32b priced only ZL: MBO USD 21.48, MBP-1 USD 23.36) and would need a logged quote and the user's
  approval. Bars-only leaders keep the F09 test inputs at USD 0.
- ZL's own price: its BBO mid from the book when the program has the ZL book (F10); otherwise ZL bars, with the
  entry at the next bar's open plus the full c_f.
- Bar timing [DataFacts to confirm]: Databento ohlcv-1m records are stamped with the bar's open time (ts_event at the
  start of the interval), so the bar stamped u is complete only at u + 60 s. [unverified here: from vendor-format
  knowledge, not a fetched page]

**5. Leakage and look-ahead traps.**
- (i) Bar-open stamps: using the bar stamped t at decision time t is a 1-minute look-ahead. Rule: at decision t,
  the latest usable bar is the one stamped t - 1 min (closing at t). Test: shift every leader bar by +1 minute;
  features at t must change only if they used the bar stamped t.
- (ii) Mixed clocks: the ZL book on ts_recv, bars on ts_event. At minute look-backs the gap is milliseconds (E.33
  measured the largest ZM/ZS/ZL median ts_recv - ts_event gap at 0.252 ms; E.33_RETURN.md line 150), so the rule in (i)
  dominates.
- (iii) Contemporaneous news: a USDA report moves all three legs within the same minute. A gap measured while the
  legs are still repricing is not a lead. Keep E.33's release exclusion (P3.6 rule 3: marks within [R - 2, R + 30]
  minutes of a release are not used; feat33.py 829-830) and add no new event list after the fact.
- (iv) Roll steps: a front change in one leg makes a k-minute "return" across a roll. Returns are invalid when the
  window crosses any leg's front change (protocol G2).
- (v) Selected look-backs: k is frozen at {5, 15, 30} before any outcome. Choosing k after seeing results counts
  each tried k into N.
- (vi) Exposure on the discovery dates: E.33 computed ZS and ZL scaled returns (k 1, 5, 15) and the ZS/ZL OFI as
  features with ZM labels (feat33.py 1032-1051). The reverse direction (ZS and ZM returns with ZL labels) was never
  computed. Disclose this under P1.5.

**6. Compute.** Bars for three roots over 816 dates: seconds per feature pass, RAM well under 1 GB.

**7. Verdict: USE, bars only for ZS and ZM:** rS_k and rM_k at k = 5, 15, 30, and gR_k at k = 5, 15, 30. Leader
books are excluded because they would make the test read a new, unpriced purchase.

## (c) CL, HO and RB as leaders (biofuel and energy linkage)

**1. Data status.**
- CL ohlcv-1m: owned 2010-07..2026-06 (BRIEFS RULES), so both windows are owned. CL is a NYMEX contract and trades
  through the ZL day session.
- HO and RB ohlcv-1m: owned only 2025-04..2026-06, which is closed (2024-03 onward). Neither discovery nor test is
  owned, so using them needs two Databento purchases, each needing a quote and approval. Not free.
- RINs (D4, D6): no exchange futures feed; prices are OTC assessments (OPIS, Argus) [unverified: no page fetched]. No
  owned or free intraday series.

**2. Exposure.**
- E.12 Gate 0 (R1-11) and E.20's search (R1-15) both had G17, "the 60-minute log return (x 1e4) of each other
  cluster's lead price path". On ZL the live leads were NQ, ZN, 6E, CL and GC, at horizons h60, h120 and hF, over
  2019-05-06..2024-02-29, with no pass (E.32b recs L11, 442-449; R1_closed_lines.md lines 84, 112).
- LR-Q3b rated ZL F09 "same family and product at a neighbouring horizon" because of exactly these leads (recs L11,
  452-453).
- The ZL test window's 2019-05..2020-11 bars were read in those trials (E.12 and E.20 rows, seal section 4,
  reports/stage_e32_test_seal.md 123 and 126). A CL-to-ZL lead in the test is therefore not virgin either.

**3. Mechanism and equations.**
- Biodiesel is priced off its feedstock. Irwin and Good (farmdoc daily, 2013-09-18) model a soybean-oil plant with a
  "Conversion factor of 7.55 pounds of soybean oil per gallon of biodiesel". They find "the market has typically
  priced biodiesel based on the cost of soybean oil, a markup for other variable and fixed costs, and zero profits",
  with all other costs "lumped into the constant term of 0.60" (farmdoc_fdd180913_biodiesel_prices.pdf.txt lines
  51, 89-93).
- Zero-profit pricing [derived from that passage]: P_BD (USD/gal) = 0.60 + 7.55 x P_SBO (USD/lb). Revenue also
  includes the RIN, credits and glycerin, so diesel affects ZL only through the margin P_BD + RIN + credit -
  feedstock. The trade calls the oil-to-diesel gap "BOHO" (bean oil minus heating oil). Trade press says RIN values
  rise with it [unverified: Fastmarkets snippet in a search result, not fetched].
- Worked: one ZL tick (0.0001 USD/lb) is 7.55 x 0.0001 = 0.000755 USD of feedstock cost per gallon. If biodiesel
  value tracked heating oil one for one with no RIN absorption, a 1-cent-per-gallon HO move would map to 0.01 /
  7.55 = 0.001325 USD/lb = 13.2 ZL ticks [derived; illustrative upper bound]. The RIN and the margin absorb part of
  any such move, and the literature gives no intraday share.
- Direction in the discovery regime: in the renewable-diesel boom the feedstock led the fuel. "Biodiesel prices
  initially followed the surge upward in soybean oil prices, but lagged in the second half of 2021"
  (farmdoc_fdd111323_biodiesel_squeeze.pdf.txt lines 165-167, Irwin, 2023-11-13; weekly data). Biofuel-policy news
  moves ZL first (Avileis and Swanson, daily 2019-2025: "a 1% biofuel-induced price increase in soybean oil leads to
  a 0.19% rise in soybean prices and a 0.30% drop in soybean meal prices", E.32 brief 1802-1804).
- Weekly and older evidence on energy to vegetable oil: Kristoufek, Janda and Zilberman (weekly 2003-2011) find
  "biodiesel with German diesel" strongly connected at low frequencies, and in crisis periods "biodiesel ... is lead
  by ... (German diesel) even at high frequencies" (kristoufek_2012_timefreq_biofuels.pdf.txt lines 32-39; "high
  frequencies" there means scales of weeks). They report Busse et al. (2010), secondary: "crude oil strongly
  influenced the prices of biodiesel and biodiesel shocks transmitted into rapeseed oil prices. However, the results
  are regime-dependent." (lines 79-81). Tanaka, Guo and Wang (GCB Bioenergy 2023), wholesale prices: crude oil and
  biodiesel are net transmitters and soybeans a net receiver [unverified: abstract via search result only].
- Intraday: three queries for intraday or high-frequency soybean oil and crude oil lead-lag found no study (search
  log). The nearest intraday commodity work is on realised volatility, not return leads [unverified, search results].

**4. Verdict.**
- HO, RB, RINs: EXCLUDE (not owned in either window; RINs not available at all as an intraday series).
- CL: EXCLUDE from F09's registered sets. Reasons:
  - (i) The only CL-to-ZL test the program ran (60-minute CL return as a lead on ZL, h60-hF) found nothing, and a
    15-60 minute version is the same family at a neighbouring horizon (LR-Q3b). It would add trials to N with a
    prior lowered by that null.
  - (ii) The mechanism runs through biodiesel and RIN margins that the literature measures weekly or daily. In the
    discovery regime it ran mostly from ZL to fuel, not the reverse.
  - (iii) Its test-window bars (CL and ZL, 2019-05..2020-11) are already exposed through G17.
  - (iv) CL is the most-watched energy contract. A 15-60 minute lead from it into a liquid CBOT contract would be an
    unusual minutes-scale inefficiency with no published support found.
- Fallback, if the lead decides to include CL: one context feature rCL_15 = (CL(t) - CL(t - 15 min)) / (0.01 x
  sigma_CL(D) x sqrt(15)) from owned CL ohlcv-1m (bar timing as (b)(5)(i)), in the propagation set only. Count it
  and disclose it as a repeat of G17 at a neighbouring horizon. No CL rule.

## (d) Which leg adjusts: loadings, shares, half-life, and how to estimate them without selecting

**1. Core idea.** ZL is tradable on the crush only if it is a closing leg (alpha_L != 0, with the right sign and a
large enough share) and the closure is fast against the hold (hl < h). None of the three numbers is published for
intraday soy, and the program never measured them: E.33 made the VECM loadings a P6.5 diagnostic, run "after the
test list is hashed; Tier A and Tier B only" (E.32 protocol 663, 671-672), and with Tier A empty "none was
computed" (E.33c_RETURN.md 180-183).

**2. Equations** (E.32 M2 c-e, 4744-4760, 4962-5008, re-signed for ZL) [derived where marked]:
- VECM, r = 1, P = (S [c/bu], nL, nM)': dP_t = alpha z_{t-1} + sum_j Gamma_j dP_{t-j} + u_t, z = beta'P with
  physical beta = (-1, 0.11, 0.22) so that z = C (c/bu), or beta from a causal rolling Johansen fit normalised on
  the ZL entry.
- Adjustment share [derived]: s_i = beta_i alpha_i / (beta'alpha), with sum s_i = 1. With short-run terms, replace
  alpha by alpha~ = (I - sum Gamma_j)^-1 alpha (MathReview A-4, E.32 brief 4974). ZL's eventual move per 1 c/bu of
  z is alpha_L / (-beta'alpha) = -s_L / 0.11 ticks: ZL falls 9.09 s_L ticks when the crush is 1 c too wide.
- Weak exogeneity: H0 alpha_L = 0 (ZL does not adjust: F09's crush set is dead); H0 alpha_S = alpha_M = 0 (ZL does
  all the adjusting). "If they are zero then that particular error correction term does not enter that equation"
  (Boero notes, E.32 brief 5071).
- Half-life: phi = 1 + beta'alpha (Gamma = 0) and hl = -ln 2 / ln phi in sampling units (E.32 brief 4764,
  4863). At dt = 1 minute: phi 0.90 -> 6.58 min, 0.95 -> 13.51, 0.97 -> 22.76, 0.99 -> 68.97 (hl_from_phi). OLS
  biases phi down by about (1 + 3 phi)/T (Kiviet and Phillips eq. 3.12, E.32 brief 4866), so hl comes out too
  short. One day session (T 290) at true 0.95 gives about 10.6 min instead of 13.5 (E.32 brief 4891-4893). Correct
  with b_c = (T b_hat + 1)/(T - 3) and report Hansen grid-bootstrap intervals (E.32 brief 4871-4872, 4874-4879).
- Bivariate price-discovery device for ZL [derived, mirroring E.32 brief 5005-5010]: p1 = 0.11 nL (ZL's oil value,
  c/bu); p2 = S - 0.22 nM (implied oil value from beans less meal, c/bu); z = p1 - p2 = C; beta = (1, -1)', one
  common trend. Then CS_1 = alpha_2 / (alpha_2 - alpha_1), Hasbrouck IS_1 with both Cholesky orderings (report both
  bounds), and Putnins' ILS_1 = IL_1/(IL_1 + IL_2). ILS_1 > 0.5 says ZL leads, against the trade; ILS_1 < 0.5 says
  ZL follows. The trivariate IS/CS do not apply (two common trends; E.32 brief 4447-4450).

**3. Worked example (hypothetical alpha, not an estimate;** m2_examples.json vecm_hyp).
- alpha = (+0.02, -0.05, -0.06) per minute on (ZS cents, ZL ticks, ZM ticks), the same magnitudes as E.32 M2 e with
  signs for z = C.
- beta'alpha = -0.02 - 0.0055 - 0.0132 = -0.0387, so phi = 0.9613 and hl = 0.6931/0.03947 = 17.56 min.
- Shares: ZS 0.517, ZL 0.142, ZM 0.341. ZL's move per cent of z is -0.05/0.0387 = -1.292 ticks. Iterating the error
  correction from z0 = +1 c gives ZS +0.517 c, ZL -1.292 ticks, ZM -1.550 ticks and z -> 0, a match.
- Reading: at this alpha ZL cannot pay at D = 1 (1.29 < 2.38 even at full reversion). The kill line is s_L* from
  (a): 0.26 at full reversion, 0.40 at hl 20 and h 30.

**4. Literature on which leg adjusts** (no intraday s_L, hl or alpha_L is published in any source found).
- Intraday, 2015 day sessions (Zhou, Bagnarosa, Gohin, Pennings and Debie, J. Commodity Markets 2023; full text).
  Speeds depend on volume, the vector does not (E.32 brief 1576-1578). The ZL-specific passages, which the E.32 brief
  quoted only in part (zhou_jcm2023_wur.pdf.txt lines 821-822 and 880-882):
  - "the contribution of soybean to the common factor relative to that of soyoil is positively related to the
    ratio of the traded volumes of soyoil and soybean. This means that the higher the volume of soyoil relative to
    soybean, the more soybean will Granger cause soyoil";
  - "If the traded volumes of soyoil relative to soybean increase, we can expect soymeal to even more significantly
    Granger cause the soyoil dynamics".
  - Reading: ZL is the follower of both other legs on days when ZL's relative volume is high. "Which leg adjusts"
    is a state variable, so ZL's volume share and its ratio to ZS enter as features, not as a fixed belief.
- Daily, CBOT (Adrangi 2006, abstract only; full text failed again this stage, log): "soybean contracts bear the
  burden of convergence when the spread between soybean and soy meal contract prices widens, this is not true of
  soybean and soy oil contracts" (E.32 brief 1795-1797). For the bean-oil pair, beans do not carry the adjustment,
  which leaves oil (or neither) to do it: weak, abstract-level support for ZL adjusting daily.
- Daily, Dalian (Liu and Sono 2016, abstract): "one-way information flow from the soymeal and soyoil markets to the
  soybean market" (E.32 brief 1798). Beans adjust there.
- Pit-era open/close (Rechner and Poitras 1993, full text, saved E.32 page rechner_poitras_1993.pdf.txt lines
  267-278 and 343-356). For the oil leg alone the correlation of the overnight change with the next day-session
  change is "-0.035 (-1.70)" in 1978-87 and "-0.08935 (-2.95)" in 1987-91, against -0.49 and -0.43 for the crush
  (E.32 brief 1643-1644). Most of the crush's opening reversal is not a reversal in oil.
- Renewable-diesel regime, daily events (Avileis and Swanson, NCCC-134 2025, full text): biofuel shocks start in ZL,
  and "meal prices serve as a price anchor when it comes to biofuels" (E.32 brief 1802-1805). On those days ZL is the
  origin, not the closer. Weekly cash evidence agrees that beans decoupled from oil after 2020 (Janzen and Wang, E.32
  brief 1497-1501).
- Net: ZL plausibly follows bean and meal shocks (intraday, state-dependent) and leads on biofuel shocks. That is the
  reason for the origin split oL30 in (a) and for gR_k in (b).

**5. Estimating them without turning a diagnostic into a selection.**
- Allowed, causal features (inside the frozen feature set, so no extra trials):
  - for each date D, a VECM on the prior 20 dates' clean day-session minutes inside the segment, giving s_L(D),
    hl(D) and alpha_L(D);
  - these enter the ML set as features, or not at all.
  - Test: the values for D equal those from a run truncated at D's open (future-scramble invariance; E.32 brief
    5044-5046).
- Required, report-only (selects nothing):
  - after the search, on every F09 set whether or not anything passes (unlike E.33's Tier-A-only P6.5), report:
    alpha (trivariate, with Gamma), s_L with a session-block bootstrap CI, phi_hat, the Kendall-corrected phi_c,
    the grid-bootstrap hl CI by hour, and bivariate ILS with both IS bounds;
  - all on OOF dates, with beta frozen from prior dates.
  - A negative then comes with its mechanism: either ZL does not adjust or it adjusts too slowly.
- Not recommended, and if used it must be hashed in the registration: an early kill on the first fold's training
  dates (s_L's CI upper end below s_L* at the frozen D and h). It is a pre-registered selection step on discovery
  prices. It saves compute but steers the search, and its dates must stay training-only. Its use is the lead's
  decision.
- Gate parameters (sampling dt = 1 min, 20-date window, day session only, release minutes excluded, IS ordering
  rule) are frozen before any outcome. Choosing them after seeing results is a selection step (E.32 brief 5047-5049).

**6. Data.** The same 1-minute bars (leaders) and ZL mids or bars as (a); no extra purchase. Compute is milliseconds
per date for the VECM (E.32 brief 5055-5056). Grid bootstraps run minutes on 8 threads.

**7. Verdict: USE** in two roles: causal prior-date estimates as features (optional), and the report-only
diagnostic (required). No gate on outcome-bearing statistics unless it is pre-registered.

## (e) How E.33's ZM negative constrains the prior for ZL as the traded leg

**1. What E.33 showed** (E.33c_RETURN.md 12-35, 207-225; aggregate outcomes only):
- 300 configurations: S1 crush, S2 propagation from ZS and ZL, S3 ZM order flow, S4 own path, S5 pooled; 6 labels;
  10 models.
- Tier A empty. The best G1 configuration loses 1.098 ticks a trade. The best daily Sharpe, 0.0478, sits inside the
  null's per-seed maxima; it is "not a null statement in the program's sense".
- ZL entered only as an input leg (its mids, scaled returns and OFI). ZL labels were never computed.

**2. Two channels that pull in opposite directions.**
- (i) Leg-share channel (raises the ZL prior). The shares of a closure sum to one. E.33's failure is evidence
  against "ZM closes the residual strongly at 5-60 minutes", and that removes probability from a hypothesis that
  competes with "ZL closes it".
  - Illustration, not an estimate: say the prior weights are ZM strong closer 0.10, ZL strong closer 0.10, and
    everything else (no tradable minutes structure, beans close, the structure is seconds-fast) 0.80. Say E.33 had
    power 0.8 against the ZM case.
  - The ZM weight then falls to 0.1 x 0.2 / (0.02 + 0.90) = 0.022, and the ZL weight rises to 0.10/0.92 = 0.109, a
    9% relative gain.
- (ii) Common-cause channel (lowers it):
  - E.33 failed across every set, including ZM's own order flow and the pooled set, at a cost per sigma (ZM 1.59/
    17.25 = 0.092 at 30 minutes under random-walk scaling) that ZL barely improves on (2.38/28.10 = 0.085;
    m2_examples.json cost_per_sigma). It is base-rate evidence that 1-lot market-order signals at minutes in this
    complex do not clear costs.
  - Its S2 also says ZS and ZL moves at 1-15 minute look-backs carried no tradable information for the less liquid
    byproduct. The same slow-participant mechanism is what F09 needs from ZL.
  - In the renewable-diesel regime, ZL is also where the complex's idiosyncratic shocks start (section d). That
    makes "ZL lags" less likely than "ZM lags" was.
- (iii) What E.33 does not constrain:
  - s_L and hl, which were never estimated;
  - the ZS/ZM-to-ZL direction of propagation;
  - the origin-split reading, in which only leader-opened dislocations are traded.
  - Power is limited too: E.33 could miss edges below its minimum detectable 1.41-3.98 ZM ticks a trade
    (E.33c_RETURN.md 194-200). The ZL discovery e80 is 1.08, 2.16 and 4.41 ticks at h 15, 30, 60 (BRIEFS RULES).

**3. Reading.**
- Channel (i) is small, because the ZM-strong-closer weight was already low before E.33 (the literature prior was
  "ZM is NOT the default adjusting leg", E.32 brief 1825-1827).
- Channel (ii) is broad. On balance E.33 is weak, mildly negative evidence for F09 on ZL. E.32b's figure (F09 about
  2.5%, P(edge) 0.05 after lowering for the G17 null, x 0.7 x 0.7; recs 4.5, 545-548) is consistent with this
  reading; nothing here argues for raising it.
- The prior number is the lead's decision.
- One design consequence follows: F09 on ZL should not be a mirror of E.33's S1 and S2 with the leg swapped. It
  should carry the two changes the regime evidence suggests (the ZL-dependent residual with the origin split, and
  the regression-weight gap). Otherwise it inherits E.33's failure mode unchanged.

## (f) Protocol inputs

Proposals for the lead's pre-registration; the lead decides what enters, the model rule (V43/V28) and every count.
Notation and general rules follow the E.32 protocol 0.3 and G1-G4 (lines 46-70, 368-380):
- point in time on ts_recv for book data;
- bars usable only after their close (rule B below);
- level quantities only inside the current segment (all three fronts unchanged);
- scales chained across rolls;
- invalid -> 0 with the family flag set;
- clip to [-5, 5] after normalisation.

**Prices.** O(u): ZL BBO mid as of u if the program holds ZL book data, else the close of ZL's last complete
ohlcv-1m bar. S(u), M(u): the close of ZS's and ZM's last complete ohlcv-1m bar. Rule B: at decision time t the last
usable bar of any root is the one stamped t - 1 min (the bar covering [t - 1 min, t)) [bar-stamp convention for
DataFacts to confirm]. Staleness: a leg whose last trade bar is older than 2 minutes at t makes every F09 feature
invalid at t.

**Scales.** sigma_X(D) for X in {ZS, ZM, ZL} as protocol 0.3 (20 prior dates, 08:35-13:13, 1-minute changes, in
ticks of X). Crush statistics in c/bu. V_X(k): contracts traded in the k minutes ending at t (bar volumes; ZL from
its book trades if held).

**Crush set S_crushL (8 features; each with E.33's context block C if the lead keeps it).**

| ID | Definition | Look-back | Normalisation |
|---|---|---|---|
| L1.1 | zC30 = (C(t) - mean_30)/sd_30, C = 11 O + 2.2 M - S; mean and sd over C(t - j min), j = 1..30 | 30 min, in segment | own rolling z; clip |
| L1.2 | zC120: as L1.1 with j = 1..120 | 120 min, in segment | as L1.1 |
| L1.3 | zRL = e_L(t)/sd_e; before D's open, OLS O = a + b_S S + b_M M on the clean 1-minute samples 08:35-13:13 (release marks [R - 2, R + 30] min excluded) of the 10 trade dates before D in the segment (at least 3 dates or invalid); centred fit, a from the means; e_L = (O - a - b_S S - b_M M)/0.01 in ZL ticks; sd_e = fit residual SD in ZL ticks; coefficients fixed for D | 10 dates | sd_e; clip |
| L1.4 | dzC5 = zC30(t) - zC30(t - 5 min) | 35 min | difference of z |
| L1.5 | oL30 = 11 dO_30 / (\|11 dO_30\| + \|2.2 dM_30\| + \|dS_30\|), dX_30 = X(t) - X(t - 30 min) | 30 min | bounded [-1, 1]; invalid if denominator 0 |
| L1.6 | zC30 x (1 - \|oL30\|) (reversion weighted to leader-opened dislocations) | 30 min | product |
| L1.7 | vrelL15 = V_ZL(15)/(V_ZL(15) + V_ZS(15) + V_ZM(15)) | 15 min | share in [0, 1] |
| L1.8 | zC30 x vrelL15 | 30 min | product |

**Propagation set S_propL (9 features).**

| ID | Definition | Look-back | Normalisation |
|---|---|---|---|
| L2.1-L2.3 | rS_k = (S(t) - S(t - k))/0.25/(sigma_ZS(D) sqrt(k)), k = 5, 15, 30 | k min | sigma_ZS(D); clip |
| L2.4-L2.6 | rM_k = (M(t) - M(t - k))/0.10/(sigma_ZM(D) sqrt(k)), k = 5, 15, 30 | k min | sigma_ZM(D); clip |
| L2.7-L2.9 | gR_k = [b_S dS_k + b_M dM_k - dO_k]/0.01/(sigma_ZL(D) sqrt(k)), b_S, b_M from L1.3's fit for D (invalid when L1.3 is invalid), k = 5, 15, 30 | k min | sigma_ZL(D); clip |

- Not included, with reasons:
  - k = 1 (bounce is 29% of sigma_1, (b)3);
  - the physical-weight gap g_k (equal to a scaled crush change, already carried by L1.4; mostly margin moves,
    (b)3);
  - F1.7/F1.8 overnight crush gap (K6-crushgap-01 exposure, (a)7);
  - leader OFI and any ZS or ZM book feature (test-window purchase, (b)4);
  - CL (see (c); fallback rCL_15 = (CL(t) - CL(t - 15))/0.01/(sigma_CL(D) sqrt(15)) in S_propL only, if the lead
    overrides);
  - HO, RB, RINs (not owned).
- ZL's own scaled returns enter only through the context block C (as E.33 treated the own price path); the gaps
  already net ZL's own move.
- Optional causal mechanism features (d)5, if the lead wants them in S_crushL: s_L(D), hl(D) from a VECM on the 20
  prior dates (day session, dt 1 min, release marks excluded, beta normalised on the ZL entry, lag order fixed at 5).
  They are constant within D. This adds 2 features, not trials.

**Model rule.**
- My judgment: F09 built only from bars is not an order-book strategy, so under a literal V43 (docs/DECISIONS.md
  788-806: "for order-book and limit-order strategies"; "V28 stands unchanged for every other line") it must run as
  rules.
- The ML form (S_crushL and S_propL as E.33-style sets) is admissible only if the lead rules that sets whose labels,
  execution and ZL mid come from ZL's own book inside the one order-book program qualify, as E.33's precedent did
  ("E.33 ran its crush and propagation sets as ML inside an order-book program", BRIEFS RULES).
- This is the lead's decision (reserved); the counts below are for either reading.

**Rule-based variant (V28), 4 rules x h {15, 30, 60} = 12 configurations.**

Common to every rule:
- Decision grid: minute marks 08:35..(13:12 - h) CT, further capped by Topstep's latest entry (h 30: 10:50 PT =
  12:50 CT).
- One position at a time. Enter at the first qualifying mark, by market order: ZL ask/bid at t + 1 s from the book,
  or the next ZL bar's open plus c_f if bars only.
- Exit by market at t + h. Flat by the session end. E.33's P3.6 exclusions (releases, rolls, limits). No re-entry
  until flat.
- Thresholds are fixed here, from E.32b's draft (recs 4.5(b) P4-P5, 616-619), not tuned. Any other value is a new
  configuration counted into N.

| Rule | Entry condition at mark t | Side |
|---|---|---|
| R1 crush reversion (ZL-dependent residual) | \|zRL\| >= 2.0 | sell if zRL > 0, buy if < 0 |
| R2 leader-opened crush reversion | \|zC30\| >= 1.5 and \|oL30\| <= 1/3 | sell if zC30 > 0, buy if < 0 |
| R3 implied-oil catch-up | \|gR_15\| >= 1.5 | buy if gR_15 > 0, sell if < 0 |
| R4 ZS leads | \|rS_15\| >= 1.5 and \|rL_15\| <= 0.5 (rL_15 = ZL's own scaled 15-minute return) | the sign of rS_15 |

**Parameters to freeze (all F09).**
- Segment rule (protocol G2).
- 10-date OLS window, at least 3 dates.
- 20-date scale window.
- Staleness limit 2 min.
- Rule B bar timing.
- Look-backs {5, 15, 30}; z windows {30, 120}; volume window 15.
- The origin window 30 and cut 1/3.
- Thresholds 2.0, 1.5, 1.5, 1.5, 0.5.
- Holds {15, 30, 60}; release exclusion [R - 2, R + 30] min.
- Clip [-5, 5].
- c_f 2.38 (spread assumed 1.0 tick [u]; sensitivity at the measured spread, (a)3).
- The report-only diagnostic list of (d)5.

**Data per window.**
- Discovery 2020-12-01..2024-02-29: ZS, ZM, ZL ohlcv-1m (owned, 39 files each); ZL book (owned MBP-1 front month,
  or the F10 MBO purchase, USD 19.48 estimate); definitions Z4 (owned).
- Test 2017-05..2020-11: ZS, ZM, ZL ohlcv-1m inside the sealed files (USD 0); ZL book only as F10 buys it; no ZS or
  ZM book.
- Exposure to disclose (P1.5 and seal section 4):
  - E.33's ZS/ZL features with ZM labels on the discovery dates;
  - E.31's ZS/ZL 1 s and 10 s splits;
  - E.12/E.20 G17 leads (CL among them) on ZL, 2019-05..2024-02, which covers the test window's 2019-05..2020-11
    bars;
  - E.22's crush gap traded in ZS.

**Trial-count implications (for the lead).** Rules: 12. ML on the two sets: 2 sets x 5 labels x 10 model settings =
100 (E.32b's option A counted 200 for four sets including S_book and S_pool).

## Evidence table

| Claim | Source (type) | Verbatim quote | File |
|---|---|---|---|
| Biodiesel priced off soybean oil cost; 7.55 lb/gal | Irwin and Good, farmdoc daily 2013-09-18 (extension) | "Conversion factor of 7.55 pounds of soybean oil per gallon of biodiesel"; "the market has typically priced biodiesel based on the cost of soybean oil, a markup for other variable and fixed costs, and zero profits" | pages/farmdoc_fdd180913_biodiesel_prices.pdf(.txt) lines 51, 93-94 |
| In the RD boom, biodiesel lagged soybean oil | Irwin, farmdoc daily 2023-11-13 (extension) | "Biodiesel prices initially followed the surge upward in soybean oil prices, but lagged in the second half of 2021" | pages/farmdoc_fdd111323_biodiesel_squeeze.pdf(.txt) lines 165-167 |
| Conversion 7.50-7.55 lb/gal held throughout | same | "This has been assumed to be between 7.50 and 7.55 pounds per gallon for the entire time we have used the model." | same, lines 78-80 |
| Biodiesel led by diesel at weekly scales in crises | Kristoufek, Janda and Zilberman 2012 (academic; arXiv 1209.0900) | "in the crisis periods, ethanol (biodiesel) is lead by corn (German diesel) even at high frequencies (low scales)" | pages/kristoufek_2012_timefreq_biofuels.pdf(.txt) lines 38-39 |
| Busse et al.: crude oil influences biodiesel, regime-dependent (secondary) | same, citing Busse et al. 2010 | "crude oil strongly influenced the prices of biodiesel and biodiesel shocks transmitted into rapeseed oil prices. However, the results are regime-dependent." | same, lines 80-81 |
| ZL follows ZS more when ZL's relative volume is high | Zhou et al. 2023 JCM (academic, full text, E.32 page) | "the higher the volume of soyoil relative to soybean, the more soybean will Granger cause soyoil" | reports/stage_e32_briefs/pages/R3a_crush/zhou_jcm2023_wur.pdf.txt lines 822, 880 |
| ZL follows ZM more when ZL's relative volume is high | same | "If the traded volumes of soyoil relative to soybean increase, we can expect soymeal to even more significantly Granger cause the soyoil dynamics" | same, lines 881-882 |
| Oil leg alone barely reverses overnight moves | Rechner and Poitras 1993 (academic, full text, E.32 page) | Table IA soybean oil: "(Open, - Close,-]) and (Close, - Open,) -0.035 (-1.70)"; Table IB: "-0.08935 (-2.95)" | reports/stage_e32_briefs/pages/R3a_crush/rechner_poitras_1993.pdf.txt lines 278, 356 |
| Day-session cointegration 180/243; no half-life | Zhou et al. | E.32 brief R3a 3.1 | E.32 brief 1549-1590 |
| Leg relations broke after 2020 (weekly) | Janzen and Wang 2025 | E.32 brief R3a 2.1 | E.32 brief 1497-1501 |
| Biofuel shocks start in ZL; meal anchors | Avileis and Swanson 2025 | E.32 brief R3a 6.1 | E.32 brief 1802-1805 |
| Beans do not carry the bean-oil adjustment (daily) | Adrangi 2006 [abstract only] | E.32 brief R3a 6.1 | E.32 brief 1795-1797 |
| Crude and biodiesel net transmitters (wholesale) | Tanaka, Guo and Wang 2023, GCB Bioenergy | [unverified: abstract via search result] | none |
| BOHO spread and RIN values co-move | Fastmarkets trade press | [unverified: search snippet] | none |
| ZL spread about 2.06 ticks US hours 2022 | GRAINS-35 | [unverified: snippet] | F2_grains.md line 54 |
| VECM shares, weak exogeneity, half-life bias, grid bootstrap, ILS | E.32 M2 (c)-(e) | as cited in (d) | E.32 brief 4699-5080 |

## Search log, stopping rule, failures

- WebSearch: 13 queries (12:11-12:20 PDT). No budget notice. Topics:
  - which leg adjusts in the crush (3 queries);
  - soybean oil and crude, heating oil or diesel transmission (4);
  - intraday soybean oil and energy lead-lag (3);
  - EPA RVO intraday reactions (1; trade press only, events 2025-2026, outside both windows);
  - farmdoc biodiesel and BOHO (2).
- Searched, not found: any intraday estimate of ZL's crush-adjustment share or half-life; any intraday (minutes)
  study of soybean oil against crude oil or heating oil; any academic intraday event study of EPA announcements on
  ZL.
- Fetches (pages/log.tsv). Method: curl with browser headers. WebFetch was not used, because it returns a model
  summary, not the raw bytes rule 9 requires to be saved. Scrapling was used once (`extract get`, then the library
  fetcher).
  - Saved and used: farmdoc fdd180913, farmdoc fdd111323, Kristoufek et al. arXiv 1209.0900.
  - Failed:
    - Adrangi 2006 (three Clute OJS URLs return a viewer page with no PDF);
    - AgEcon Search 15880 and Franken, Irwin and Garcia 2020 (AWS WAF challenge, HTTP 202; Scrapling `extract get`
      returned the PDF once but as decoded text, unreadable; the library fetcher got the 202 page; Firecrawl not
      tried);
    - the IPB journal VECM paper (PDF xref error).
  - These gaps are covered by the E.32 brief's sources or marked [unverified]. None is presented as a finding.
- Stopping rule: each topic (a)-(e) has at least two full-text sources, or an explicit "not found" after at least
  three queries.

## Not finished or not verified

- Not verified here:
  - the ohlcv-1m bar-stamp convention (ts_event at the bar open);
  - the ZS, ZM and ZL contract months;
  - the ZL day-session spread. These are DataFacts or run-stage counts.
- No intraday s_L, hl or ZL-CL lead evidence exists in what was searched. Every such number above is hypothetical
  and labelled so.
- The Franken, Irwin and Garcia (2020) biodiesel hedge paper (soybean oil against heating oil weights) was not
  obtained (WAF). A Firecrawl retry was not attempted.


---

<!-- concatenated unchanged: reports/stage_e34_briefs/M3_labels_ZL.md (sha256 af0ddc05adf550f8) -->

# E.34 methods addendum, M3 for ZL: labels and holding band

Worker MathReaderM3-OpusHigh (Opus 5.5, high), Stage E.34, started 2026-10-29 12:10 PDT. Prompt text: "Labels and
holding band from E.32b's F5 (Topstep ZL band 15-60 minutes): the label set, cost-aware targets, and the trade-through
and market execution variants of E.32 M6."

Scope and sources. This section maps E.32 protocol P3 (reports/stage_e32_discovery_protocol.md lines 254-366) and
P6.4 (641-662), the E.32 methods brief M3 (lines 5232-6146) and M6 (8346-9187), and E.33's code (lab33.py, cost33.py
under reports/stage_e33_briefs/work/pipeline/) from ZM to ZL as the traded leg, inside E.32b's Topstep ZL band
B = {15, 30, 60} minutes (reports/stage_e32b_holding_scope.md lines 913-951). No market data was opened. Every number
below is either a shared standard number from BRIEFS.md (cited "E.32b holding scope 15") or arithmetic on those
numbers in work/MathReaderM3-OpusHigh/M3_calc.py (output M3_calc.out, 54 lines, run 2026-10-29 12:18 PDT, 22 s, nice
10, seed 20261029; the only simulation is a stylised Brownian mid, as in E.32 M6). Web: 5 WebSearch queries
(work/.../pages/searches.tsv), 6 fetches (pages/log.tsv, with UTC time and sha256). Ticks are ZL ticks (0.01 c/lb =
USD 6.00) unless stated. CT = America/Chicago; PT = America/Vancouver.

Standard ZL numbers used (E.32b holding scope 15): sigma_1/15/30/60 = 5.52 / 20.37 / 28.10 / 38.21 ticks; Topstep fee
USD 5.28 RT = 0.880 tick; c_f = 2.38 = S 1.0 (assumed, u) + 0.5 slippage (E.32b ruling OC-5, an assumption) + 0.88;
e80 at the test 0.90 / 1.81 / 3.70 ticks at n = 19 / 9 / 4 a day.

---

## (a) The label set inside B

### a.1 Core idea
A label is the executable net of one trade that holds h minutes (fixed horizon, F) or until a volatility-scaled
barrier on the mid or h minutes, whichever comes first (triple barrier, T). B fixes the horizons; the label set is
the subset of {F, T} x {15, 30, 60} that the program searches. Every label added multiplies the configurations by
the number of sets and model settings, so it costs N.

### a.2 Equations (decision time t, L = 1.000 s, f = 0.880 tick; ZL book "as of u" per E.32 0.3)
    N_long^F(t)  = bid_1(t + h + L) - ask_1(t + L) - f
    N_short^F(t) = bid_1(t + L) - ask_1(t + h + L) - f
    y^F(t) = +1 if N_long^F > 0; -1 if N_short^F > 0; 0 otherwise.
Triple barrier, h in the T set: m0 = M_ZL(t + L); b(t) = kappa sigma_ZL(D) sqrt(h), kappa = 1.0; tau_up / tau_dn =
the first ZL book update u in (t + L, t + L + h min] with M_ZL(u) >= m0 + b / <= m0 - b (updates with M_ZL undefined
ignored); tau = min(tau_up, tau_dn, t + L + h min);
    N_long^T(t)  = bid_1(tau + L) - ask_1(t + L) - f,   N_short^T(t) = bid_1(t + L) - ask_1(tau + L) - f,
    y^T = +1 if tau = tau_up, -1 if tau = tau_dn, 0 if no barrier by t + L + h.
These are E.32 P3.3-P3.4 (lines 279-301) with ZM replaced by ZL and f = 0.528 replaced by 0.880; E.33 implements
them in lab33.py label_row (lines 600-640) and first_barrier (513-545).

First-passage facts used below (driftless Brownian mid; E.32 brief M3 b.2, line 5430 onward):
P(no barrier by h) = (4/pi) sum_n (-1)^n/(2n+1) exp(-(2n+1)^2 pi^2 / (8 k^2)), k = b / (sigma_path sqrt(h)).

### a.3 Worked ZL example (M3_calc.out section 3)
- Barrier half-widths at sigma_1 = 5.52: b = 21.38 / 30.23 / 42.76 ticks at h = 15 / 30 / 60 (USD 128 / 181 / 257 a
  contract).
- ZL's h-minute SD grows slower than sqrt(h): b / sigma_h = 1.050 / 1.076 / 1.119 (sigma_h from E.32b F3). The
  barrier is therefore wider than one h-SD, and wider the longer h. Share of T labels ending at the vertical barrier:
  0.371 if the path diffuses at sigma_1 (k = 1), 0.415 / 0.439 / 0.475 at the h-scale diffusion (series; the 1-s grid
  simulation gives 0.426 / 0.447 / 0.484). The truth for ZL lies between: short-scale mid changes carry spread
  flicker, so the 1-minute SD overstates the path's diffusion. I say this as a reading of the variance ratio, not as
  a measurement.
- Mean hold of a T label, E[min(tau, h)] / h = 0.706 (k = 1) to 0.774 (k = 1.119) (simulation, 40,000 paths). A T60
  trade therefore holds about 42-46 minutes on average, a T30 about 21-23, a T15 about 11.
- Break-even hit rate for barrier exits (barriers on the mid, cost s + f = 1.88 at a 1-tick spread; E.32 brief
  MathReview B-13 reading (i), line 5429): p* = 0.5 + 1.88 / (2b) = 0.544 / 0.531 / 0.522.

### a.4 Decision per label (verdict for the lead)

| label | in or out | reasons |
|---|---|---|
| F05 | out | outside B: E.32b G/minG 1.6135 > 1.10 at h = 5 (holding scope line 921) |
| F15 | in | in B (G/minG 1.081); 263 starts a date; up to 17 trades a date (d below); 1.88 ticks = 0.092 sigma_15 |
| F30 | in | min G of the pair (0.1492); 248 starts; up to 8 trades a date |
| F60 | in | in B (G/minG 1.066); power term "power term >= cost term from h = 60" (holding scope line 921); 218 starts a date, the last at 12:12 CT; up to 4 trades a date; the only horizon whose max trade count equals E.32b's n_cap (4) |
| T15 | in | E.33 symmetry (S_book on ZL mirrors E.33's ZM sets, R1-21 stated differences, E.32b recs line 609); exit realism at the barrier; mean hold about 11 min, so it reaches more trades a date than F15 within the 20-entry cap |
| T30 | in | same; mean hold 21-23 min |
| T60 | out (recommended) | (1) its realised hold (42-46 min) sits between F30 and F60, so it adds little information the other five do not span, while it costs one more label (under E.32b option A 4 sets x 10 settings = 40 more configurations, N 1038 to 1078; under option B 10 more, 900 to 910); (2) b = 42.76 ticks at 47-48% vertical exits makes T60 a near-fixed-horizon label at its long end (the M3 b.2 point that at wide barriers "the triple-barrier label is almost a fixed-horizon label"); (3) no head-to-head evidence favours TB over FH as a target (E.32 brief M3 b.7, lines 5494-5496: "Its advantage is the realism of the exit, not prediction ... none was found here"); (4) the session does not forbid it: 218 starts, last entry 12:12 CT, no pause or flat-by conflict (Topstep flat by 15:10 CT is 117 minutes after the 13:13 cap). If the lead wants a symmetric T set, T60 is admissible on every timing rule; the case against is N and redundancy, not feasibility |
| to-close, mid-to-mid, last-trade labels | out | to-close lies outside B (OC G/minG 1.4735); mid and last-trade labels are excluded by E.32 M3 e.4 and f.5 trap 5 |

Final set (recommended): F15, F30, F60, T15, T30, the five labels E.32b's draft keeps (recs line 614). Session
length (290 minutes, 08:30-13:20 CT), the pause (07:45-08:30 CT, outside every day label) and Topstep's flat-by
(15:10 CT) do not bind on any of them; the binding timing limits are the 08:35 start and the 13:13 end (section e).

### a.5 Data each label needs
ZL top of book (bid_1, ask_1, F_LAST batching, the bad-book flag) for every update in [t, t + 2L + h] on D's front;
sigma_ZL(D) from 1-minute ZL mids of the 20 prior trade dates (E.32 0.3 definition with X = ZL, chained across ZL
rolls). Discovery source: owned ZL MBP-1 front month (Z3_ZL_v_0) or ZL MBO if bought (section c.4 on source parity).

### a.6 Leakage traps for labels (each with a test)
1. sigma_ZL(D) using D itself. Test: compute it from dates strictly before D; recompute with D's data removed and
   assert equality (E.32 brief M3 b.5 trap 1).
2. Barrier test on the last trade or on 1-minute bars. Test: barriers step through book updates; assert no bar or
   trade field enters label_row (lab33 replays updates only).
3. Mid labels. Test: assert every label uses bid at the long exit and ask at the long entry; N_long + N_short =
   -s(t + L) - s(t + h + L) - 2f < 0 on every row (lab33 raises LabelError if both are positive).
4. Choosing T60 or a kappa after seeing results. Test: the declared label set equals the set run; each label counts
   in N (M3 b.5 trap 5).
5. Prior exposure, not a leak but a disclosure: ZL h60-hF bar labels were computed by E.12 and E.20 on
   2019-05-06..2024-02-29, which covers the discovery dates (E.32b recs lines 594-597, R1-11, R1-15). No earlier stage
   computed a ZL book label at 15-60 minutes; E.31's ZL use was conditioning splits on ZM fills, and the V49 ZL
   trade-through follow-up was skipped (docs/DECISIONS.md lines 1031-1037: "This covers ... the ZL follow-up of V49
   (skipped)").

---

## (b) Cost-aware targets and the dead zone

### b.1 Core idea
The target already contains the spread and the fee, so a row is +1 or -1 only if the trade would have made money at
executable prices. The dead zone is not a tuned threshold: it is whatever the book's spreads at entry and exit plus
2f make it (E.32 P3.3, line 285: "The dead zone is the spread plus costs, not a tuned threshold").

### b.2 Equations
With A = M + s/2 and B = M - s/2:
    N_long^F > 0  <=>  M(t + h + L) - M(t + L) > (s(t + L) + s(t + h + L)) / 2 + f.
So the half-width of the dead zone in mid ticks is d(t) = s_bar + f, with s_bar the mean of the entry and exit
spreads; at 1-tick spreads d = 1.880 ticks. The class-conditional magnitudes for the EV rule (E.32 P3.5) are the
weighted means mu_long_k, mu_short_k of the net labels over training rows; the decision is long iff EV_long >
max(EV_short, 0). The regression form is the same target: N_long or N_short, traded iff the forecast net exceeds 0.

What enters the label's cost and what does not:
- in: the measured spreads at t + L and t + h + L (from the book), the 1 s latency drift (prices are read at t + L),
  and f = 0.880 (Topstep USD 5.28 / 6.00);
- not in: E.32b's 0.5-tick slippage (ruling OC-5). It is a planning allowance for a bar-based cost; a one-lot market
  order at the touch has no depth walk (E.32 P3.2, line 263), and the latency drift is already in the prices. Adding
  0.5 would double-count it, the same error MathReview B-13 recorded for the ZM barriers (line 5429). E.32b's
  c_f = 2.38 stays the planning number for G, e80 and K2; the label uses 1.88 at 1-tick spreads.
- the account residual (E.28's 0.062 for ZM; brief M3 e.2) is not in E.33's labels (f = 0.528 = fee only) and is not
  added here; the prop simulator carries account economics (P6.4 Tier A).

### b.3 Worked ZL example (M3_calc.out section 2; normal moves, magnitudes independent of the sign)

| cost basis | h | threshold d (ticks) | d / sigma_h | P(dead zone) = 2 Phi(d/sigma_h) - 1 | break-even sign hit rate q* = 0.5 + d / (1.596 sigma_h) |
|---|---|---|---|---|---|
| s = 1 + f (label, 1-tick book) | 15 | 1.880 | 0.0923 | 0.0735 | 0.5578 |
| | 30 | 1.880 | 0.0669 | 0.0533 | 0.5419 |
| | 60 | 1.880 | 0.0492 | 0.0392 | 0.5308 |
| c_f (E.32b planning) | 15 | 2.380 | 0.1168 | 0.0930 | 0.5732 |
| | 30 | 2.380 | 0.0847 | 0.0675 | 0.5531 |
| | 60 | 2.380 | 0.0623 | 0.0497 | 0.5390 |
| s = 2.06 (u) + f | 15 | 2.940 | 0.1443 | 0.1148 | 0.5904 |
| | 30 | 2.940 | 0.1046 | 0.0833 | 0.5656 |
| | 60 | 2.940 | 0.0769 | 0.0613 | 0.5482 |

Check (h = 30, 1-tick): 1.88 / 28.10 = 0.0669; Phi(0.0669) = 0.52667, x 2 - 1 = 0.0533; q* = 0.5 + 1.88 / 44.85 =
0.5419. The c_f rows reproduce E.32b's "p_be norm" column (0.573 / 0.553 / 0.539, holding scope lines 929-931).
The 2.06-tick row uses the only ZL spread figure found, a search snippet (GRAINS-35, F2_grains.md line 54: "US hours
2.06 ticks ... per search snippet"), so it is [unverified]; ZL's real spread is a DataFacts count, not an assumption
this section may fix. Whatever it is, the label measures it row by row; only the planning number c_f depends on S.

In USD at the 1-tick book: the dead zone is 1.88 x 6 = USD 11.28 a contract a side of the mid; a trade 1 tick past it
nets USD 6.00.

### b.4 Data needs
The ZL touch at t + L and t + h + L; nothing else (the threshold is a protocol constant plus measured spreads).

### b.5 Leakage traps
1. A dead-zone width set from the data (a quantile of |dM|, a class-balance target). Test: the only constants in the
   label are L and f; assert no data-derived threshold (E.32 brief M3 f.5 trap 1).
2. Spread taken at t instead of t + L. Test: rerun with L = 0 and report it only as a bound.
3. Re-weighting classes so that the 0 class shrinks. Test: evaluate at natural class frequencies (M3 f.5 trap 2).
4. Fee per firm in the label. Selection uses Topstep's f only (E.32 P7, Topstep, market, L = 1 s); other fees apply
   only in P6.4 variants after the test list is hashed.

### b.6 Verdict
USE the executable three-class target with dead zone = spreads + 2f (f = 0.880), and the net executable return as the
regression target. No 0.5-tick slippage term in the label. Report P(class 0) per label and h (DataFacts or the run,
not now).

---

## (c) Executable prices from the ZL book, Topstep's 1 s latency, and the M6 execution variants

### c.1 Core idea
The label and the trade simulation read the same prices: a market buy decided at t fills at ask_1 of the ZL book as
of t + L, a market sell at bid_1, one contract, L = 1.000 s (E.32 0.3, line 79; Topstep's latency as E.33 used it).
The M6 variants differ only in execution on one common signal set (E.32 P6.4, MathReview D-11).

### c.2 Equations
- (i) Market entry and exit (E.32 P3.2 for ZL): fill = touch as of t + L; fallback when the needed side is empty or
  the book is bad: the first later update at which it exists and the book is good; an entry with none before the
  planned exit is not made (counted); an exit with none before 13:20:00 is marked at the ZL front's limit on the
  blocking side (low limit for a long), or, if D has no limits, at the last valid touch, and flagged (lab33.py
  exit_fill lines 478-504). Also reported at L = 0.300 s for the test list only.
- (ii) Trade-through limit entry (E.32 P6.4 (ii); cost33.py limit_entry_through lines 335-370): at t + L the order
  rests at the ZL touch (bid_1 for a long, ask_1 for a short); it fills at its own price at the first A or B trade
  strictly through it (below a buy, above a sell) in (t + L, c + L], c = min(t + W, exit decision), W = min(60 s,
  h/5) = 60 s for every h in B; side-N trades (implied or opening) never fill (cost33 READING C2); market exit as in
  (i). (ii-b): an unfilled order converts to a market entry filling as of c + L.
- Per-signal identities (E.32 brief M6 B1-B5, lines 8518-8530), in mid coordinates for a long, X the signed mid path
  from t + L, G = X_H:
      V_M = alpha - s - f;   V_L = E[1_Fill X_H] - p f;   V_LC = V_L + E[1_noFill (X_H - X_W - s - f)];
      V_M - V_L = OC - p s,  OC = (1 - p)(E[G | no fill] - s - f)   (latency drift omitted).
  Under B6-TT a buy limit at the bid fills once the mid has reached -s.
- (iii) Queue-model limits: Rithmic routes only (E.32 P6.4 (iii)). Not applicable: the program is Topstep, whose route
  is trade-through (M6 5.3 table: Topstep "(i); (ii) documented").

### c.3 Worked ZL example (M3_calc.out section 6; stylised Brownian mid, sigma_1 5.52 ticks a minute, constant drift
alpha over h, 400,000 paths, 1 s grid over W = 60 s, ZL fee 0.88)

| s | h | alpha | p_fill | E[G given fill] | E[G given no fill] | V_M | V_L | V_LC | OC | p s |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 15 | 0 | 0.799 | -1.37 | 5.64 | -1.84 | -1.79 | -2.16 | 0.76 | 0.80 |
| 1 | 15 | 2.38 | 0.793 | 0.97 | 7.85 | 0.52 | 0.07 | 0.14 | 1.24 | 0.79 |
| 1 | 15 | 3.28 | 0.790 | 1.79 | 8.78 | 1.38 | 0.72 | 0.97 | 1.45 | 0.79 |
| 1 | 30 | 4.19 | 0.793 | 2.68 | 9.60 | 2.24 | 1.43 | 1.85 | 1.60 | 0.79 |
| 1 | 60 | 6.08 | 0.794 | 4.60 | 11.65 | 4.18 | 2.96 | 3.81 | 2.01 | 0.79 |
| 2 | 15 | 3.28 | 0.652 | 0.78 | 8.00 | 0.41 | -0.07 | 0.03 | 1.78 | 1.30 |
| 2 | 30 | 4.19 | 0.656 | 1.84 | 8.89 | 1.38 | 0.63 | 1.04 | 2.07 | 1.31 |
| 2 | 60 | 6.08 | 0.658 | 3.67 | 10.55 | 3.14 | 1.84 | 2.82 | 2.62 | 1.32 |

(alpha = 3.28 / 4.19 / 6.08 is E.32b's "c_f + e80 test" at h = 15 / 30 / 60, holding scope lines 943-945; all rows
for s = 1, 2 and alpha in {0, 2.38, 3.38, c_f + e80} are in M3_calc.out lines 31-54.)
Check (s = 1, h = 15, alpha 2.38): V_M - V_L = 0.515 - 0.070 = 0.445 = OC - p s = 1.238 - 0.793. V_M = 2.38 - 1 - 0.88
= 0.50 (simulated 0.515, within noise).
Reading: ZL's larger sigma_1 (5.52 against ZM's 3.15) makes trade-through fills likely within 60 s (0.79 at a 1-tick
spread, 0.65 at 2 ticks), but the selection is the M6 one: the filled signals are the ones that moved against the
order (E[G | fill] far below alpha), and the opportunity cost of the unfilled ones exceeds the spread the filled ones
save at every alpha >= c_f. Market entry beats the trade-through limit at every positive-edge row, by 0.45-1.30
ticks; the limit wins only at alpha = 0 (by 0.04 at s = 1, 0.71 at s = 2), where neither pays. This is the stylised
model only, with no E.31-type excess adverse markout (that calibration was measured on ZM fills and is not
transferable to ZL); a front-loaded or mean-reverting path changes the numbers, which is what (ii) on real data
measures.
- Latency drift SD (Brownian): 0.713 ticks at L = 1.0 s, 0.390 at 0.3 s (5.52 x sqrt(L/60)); mean zero for a signal
  that accrues linearly, negative for a front-loaded one (M6 E1).

### c.4 Data needs, and source parity between discovery and test
- (i) needs the ZL touch with F_LAST batching and the bad-book flag; (ii) also needs ZL trade prints with price and
  aggressor side. Both are in MBP-1 (top level after each event, plus action-T trade records with side) and in MBO.
- Implied liquidity: Databento's GLBX documentation says "Databento combines the real and implied books, publishing
  the merged top-of-book on the CMBP-1 schema" and "Implied trades ... may not have an aggressing side set. These
  trades will be normalized with side set to None" (pages/databento_glbx_mdp3.md lines 113 and 70). So MBP-1 is the
  outright book, as is an MBO rebuild, and implied prints fall under cost33's side-N rule. That MBP-1 is derived from
  MBO is a search summary only [unverified].
- Parity trap: the test window has ZL MBO from 2017-05-21 (sealed), while discovery may use MBP-1. The two differ in
  how a bad book is represented: in MBO the book is bad from F_MAYBE_BAD_BOOK until the next R (clear) record (lab33
  docstring lines 10-14); MBP-1 has no R record, so a per-record reading is needed ("an update is bad iff its F_LAST
  record carries F_MAYBE_BAD_BOOK", a reading to declare). Options for the lead (data spend is not mine to decide):
  (a) labels from the same schema in both windows: ZL MBP-1 test (USD 23.36 estimate, E.32b recs 4.5(c)) beside the
  ZL MBO test that F10 needs; (b) ZL MBO for discovery too (USD 19.48 estimate), labels from the mbo_book31 rebuild
  in both windows, as E.33 did for ZM; (c) MBP-1 discovery and MBO test with a declared, hashed parity rule and a
  count of differing touch states on test dates (the weakest: the check runs on the sealed data). (b) also gives F10
  its own MBO features and removes the reading. I recommend (b) or (a), not (c).

### c.5 Leakage traps
1. Fill at t instead of t + L. Test: the engine takes L as an input; L = 0 reported only as a bound (M6 2.5).
2. A trade stamped at the placement time counted as a fill. Test: cost33 READING C1 (start exclusive).
3. Side-N (implied) prints filling a limit. Test: cost33 READING C2; count side-N prints at the order's price.
4. Variants compared on different signal subsets. Test: P6.4's common signal set (the selection variant's decision
   times and sides); the per-variant signal count equals the common set's count.
5. A variant or W chosen after results. Test: P6.4 lists (i), (i) at 0.3 s, (ii), (ii-b) before the test list is
   hashed; they select nothing.

### c.6 Verdict
- USE (i) market entry and exit at L = 1.000 s as the selection execution, with E.32 P3.2's fallback mapped to ZL.
- USE (ii) and (ii-b) as reported variants after the test list is hashed (Topstep documents trade-through; V50:
  "Any later stage prices its fills under the trade-through rule unless a firm documents otherwise", DECISIONS lines
  1038-1041). Expect them to lose to (i) for any signal that pays (c.3).
- SKIP (iii) (no Rithmic route at Topstep; ZL MBO not owned for discovery).
- Other firms' fees: not in this program unless the lead adds firms; if added, each needs its ZL fee in ticks from
  E.28's firm files, not the ZM list of P6.4.

---

## (d) Trade rule and entry limits

### d.1 Core idea
One position at a time; the label type fixes the exit; the EV rule of E.32 P3.5 decides side or no trade; holds never
overlap; the cap is 20 entries a date (E.32 P3.8, line 357). Topstep adds no hold-time floor that binds at minutes
(M6 5.3) and no daily trade count; Topstep's news block does not name grains (F2_firms.md lines 13-17: "Other
products (energies, rates, FX, etc.) are unaffected"; grains are not named).

### d.2 Equations
Decision grid G_h(D) = {08:35:00, 08:36:00, ..., 13:12:00 - h} CT (E.32 0.3, line 68; lab33 LAST_GRID_OFFSET 277).
After an FH exit filled at t + h + L the next decision is the first grid minute at or after the fill, t + h + 1 min,
so one FH cycle takes h + 1 minutes:
    n_max^F(h) = floor((277 - h) / (h + 1)) + 1.
A TB trade frees the account at tau + L, so n_max^T depends on the realised tau (bounded by 20).

### d.3 Worked ZL example (M3_calc.out section 1)

| h | starts a date | latest entry CT / PT | n_max^F under P3.8 | n_max^F if re-entry at the exit minute were allowed | E.32b n_cap | e80 test at n_max^F (E.32b's at n_cap) |
|---|---|---|---|---|---|---|
| 15 | 263 | 12:57 / 10:57 | 17 | 18 | 19 | 0.956 (0.90) |
| 30 | 248 | 12:42 / 10:42 | 8 | 9 | 9 | 1.923 (1.81) |
| 60 | 218 | 12:12 / 10:12 | 4 | 4 | 4 | 3.699 (3.70) |

e80 = SR80_test sigma_h / sqrt(n) with SR80_test 0.1936 (E.32b definitions, holding scope line 16). Check (h = 30):
0.1936 x 28.10 / sqrt(8) = 5.440 / 2.828 = 1.923.
Finding for the lead (arithmetic, not an outcome): E.32b's n_cap = min(20, floor(290 / h)) assumes the full 290-minute
session and back-to-back holds. Under the protocol's grid (08:35 start, 13:13 end) and P3.8's re-entry rule the
maximum is 17 and 8 trades at h = 15 and 30, so the e80 a configuration must beat at the test is 0.96 and 1.92 ticks,
not 0.90 and 1.81. Stop rule K2 ("stop if the best discovery net edge is below the test's 1.8 ticks", BRIEFS shared
facts) quotes the h = 30 value at n = 9; at the protocol's n = 8 it is 1.92. These are upper bounds on trade counts:
a configuration that trades less needs more. Whether to re-base K2 and G1 is the lead's decision.
Latest entries in PT are 8 minutes earlier than E.32b's "latest start PT" column (11:05 / 10:50 / 10:20, holding scope
lines 943-945), because the protocol ends every span at 13:13 CT, not at the 13:20 close.

### d.4 Data needs
None beyond the labels; the entry cap and grid are protocol constants.

### d.5 Leakage traps
1. Decisions that use records after t. Test: P3.8 "The decision uses only records with ts_recv <= t"; truncate the
   inputs at t and recompute the decision (M6 2.5).
2. Overlapping simulated holds (counting the same move twice in X_D). Test: assert entry_ns(k+1) >= exit fill ns(k).
3. The re-entry rule changed after results. Test: the rule (next decision at the first grid minute at or after the
   exit fill) is frozen; the alternative (decide at the exit minute, net the exit and the new entry) counts in N if
   compared.

### d.6 Verdict
USE E.32 P3.5 and P3.8 unchanged, with ZL prices, f = 0.880 and the 20-entry cap. Latest entries 12:57 / 12:42 /
12:12 CT for h = 15 / 30 / 60 (10:57 / 10:42 / 10:12 PT). Report the e80 re-base above to the lead.

---

## (e) Exclusions

### e.1 Core idea
A row is kept and a trade entered only if the whole possible span [t, t + L + h] (FH; [t, t + 2L + h] for TB rows,
lead ruling R-L10, lab33 lines 582-598) sits in a market state the bot could trade and the family is about. Every
window comes from a calendar or the clock, never from prices (E.32 brief M3 g.6 trap 1). Rules known at t govern
rows and entries; rules that look into the span are row rules only (E.32 P3.6 first paragraph, lines 304-310).

### e.2 Rules for ZL (numbered as E.32 P3.6)
1. Open: no span starts before 08:35:00 CT (06:35 PT). Unchanged.
2. Close: every span ends by 13:13:00 CT, one minute before the settlement window. The 13:14-13:15 window is verified
   for ZC, ZS and ZW only (F2_grains.md line 120, GRAINS-28; line 158: "ZL and ZM settlement-window pages not found in
   Wayback") [unverified for ZL]; the cap costs ZL nothing if ZL's window differs, so keep it. Topstep's flat-by
   (15:10 CT) and its early-close rule ("Flat 15 minutes before an early close", F2_firms.md line 29) never bind,
   because rule 4 drops early-close dates.
3. Scheduled releases at 11:00 CT: no span meets [R - 2 min, R + 30 min] for USDA WASDE, NASS Crop Production
   (monthly, annual), Grain Stocks, Prospective Plantings, Acreage and NOPA Monthly Crush, with E.32 P3.6 rule 3's
   calendar files, parse rule, NOPA rule dates and count assertion unchanged (lines 315-329). WASDE carries the US
   soybean-oil balance and NOPA reports oil stocks, so for ZL these are the core releases, not peripheral ones.
   Additional ZL-relevant events (verdicts):
   - FOMC decision (13:00 CT, 8 a year; time from Topstep's verified Tier 1 page, F2_firms.md line 13): recommended
     IN as [12:58, 13:13]. Cost: 15 starts per label on each FOMC date (starts 12:43-12:57, 12:28-12:42, 11:58-12:12
     for h = 15 / 30 / 60), about 0.2% of rows. It is a scheduled cross-asset volatility event inside the day session;
     ZM's protocol did not exclude it, so including it is a stated difference from E.33 (one declared rule, not a
     comparison, so no N). The lead decides; the calendar must be built from the Federal Reserve's published dates
     before the run (both windows).
   - EIA Weekly Petroleum Status Report (Wednesday 10:30 ET = 09:30 CT, inside the session): recommended OUT as an
     exclusion, IN as a reported stratum. Sources: EIA's schedule page: "The standard release time and day of the
     week will be at 10:30 a.m. eastern time on Wednesday with the following exceptions" (pages/eia_wpsr_schedule.txt;
     the page lists only 2024-2026 exceptions). Reasons: no study of ZL's intraday response to the WPSR was found
     (search 4, negative); the window would remove h + 33 starts on about 50 dates a year (63 of 248 F30 starts on a
     Wednesday, about 5% of all F30 rows); the historical exception dates (holiday shifts to Thursday at other times)
     for 2017-2024 are not on disk, and EIA's robots.txt disallows "/archive/" paths, so a sourced calendar for both
     windows is not assured. The stratum report (rows meeting [09:28, 10:00] on WPSR Wednesdays, standard days only)
     selects nothing.
   - EPA RFS / RVO proposals and final rules, CARB LCFS quarterly reports, and Reuters "leaks": OUT as exclusions;
     IN as a reported stratum of dated EPA events. Reasons: (i) EPA and leak times are unscheduled, so a window around
     them is not knowable at t and a live bot without a news feed could not apply it; (ii) the large moves arrive as
     limit states, which rules 5 already handle: on 2022-12-01 "January, March and May 2023 contracts were down the
     4.50¢-a-lb daily limit (the spot month does not have a daily trading limit)" (pages/fbn_22778_epa_dec2022.txt),
     and in June 2023 "CME soybean oil futures hit limit down during the overnight session on the back of the leaked
     reports" (pages/fastmarkets_vegoil_slump_jun2023.txt); (iii) CARB reports come "by 3pm" Pacific on scheduled
     dates (Avileis and Swanson 2025, reports/stage_e32_briefs/pages/R3a_crush/aveleis_swanson_nccc134_2025.pdf.txt
     line 395, quoting CARB), after ZL's day session; (iv) the paper finds the effect at the daily level only (E.32
     brief line 1965: "No intraday timing is reported"). The stratum's dates come from EPA's own pages or the Federal
     Register, saved before the run [not built here].
   - Outside the day session, no window needed: Export Sales 07:30 CT, NASS Fats & Oils 14:00 CT, Crop Progress 15:00
     CT (E.32 P3.6 rule 3, lines 328-329).
4. Rolls and calendar: exclude the ZL roll date (the ZL.v.0 instrument_id on D differs from that of the previous
   trade date) and the trade date after it, and early-close and late-open dates (E.32 P1.4 with ZL as the front).
   ZL's roll dates are the traded leg's own; ZS or ZM rolls affect features only (P4, other workers). The owned ZL
   MBP-1 is ZL.v.0 only, so no second-month fallback exists around a roll; the exclusion is required, not optional.
   Data note: limits are removed on the spot month ("price limits are removed on the business day prior to first
   notice day", E.32 brief lines 2324-2325); if any ZL.v.0 front on a kept date is a spot-month contract, rule 5's skip case
   fires; DataFacts should count such dates.
5. Locked book and price limits (E.33's ZM rule mapped to ZL):
   - Row rule: no span containing a ZL book update without a bid or an ask, or marked bad (a limit-locked ZL book
     shows one side empty, so this removes locked spans).
   - Row and entry rule: no span starting while M_ZL(t) >= HL - 0.02c or M_ZL(t) <= LL + 0.02c, c = (HL + LL)/2,
     HL, LL from the ZL front's last definition record with ts_recv <= 08:30:00 CT on D; skip (and count) when the
     record is missing or a limit field is UNDEF_PRICE or 0. This is Topstep's rule, "Stop trading above: Settlement
     x (1 + Price Limit% - 2%)" (E.32 brief M6 4.1 table, line 8814): with HL = S(1 + l), the line is HL - 0.02S.
     Exact integer form as in lab33 _near_limit (lines 387-393): 100 (bid + ask) >= 198 HL - 2 LL, or <= 202 LL +
     2 HL, prices in fixed point.
   - Worked ZL example (illustrative settlement S = 60.00 c/lb, not a data read; limit 4.50 c, the value quoted for
     2022-12-01 above): HL = 64.50, LL = 55.50, 0.02c = 1.20 c = 120 ticks; entries stop when the mid reaches 63.30 or
     56.70, 330 ticks from S = 8.6 sigma_60 = 11.7 sigma_30 = 16.2 sigma_15. At S = 50 c the line is 450 - 100 = 350
     ticks; at S = 80 c, 450 - 160 = 290. It binds only on limit-scale days, which are the EPA and leak days.
   - Trap carried from E.33 (a data finding, not a reading): Databento's ZM definition limits changed only on Sundays,
     so the band could be stale after a large move and removed whole dates (E.33 protocol readings L21, lines
     950-962; LabelCoder_readings.md lines 29-38); the user kept the rule as written for ZM discovery and deferred the
     test-window source (DECISIONS lines 1083-1086, V52.2). For ZL the same can happen. Options for the lead: (a) E.33
     literal (definitions as of 08:30); (b) settlement based: c = the ZL front's prior settlement and the width from
     the definitions ((HL - LL)/2), which follows Topstep's wording, but needs a settlement source (Databento
     statistics schema, ownership unknown). DataFacts should count, per ZL front, how often the definitions' limit
     fields change and on which weekdays (definitions only, no prices).
6. ZS or ZM invalid: rows kept; features fall back (P4, other workers).
7. Low-liquidity dates: no exclusion beyond rule 4. A volume-based date filter would be either a tuned threshold or
   a data-derived window (trap g.6.1). If the lead wants one, it must be causal (prior 20 dates' day volume) and is
   reported as a stratum, selecting nothing. The 2017-2019 test years have lower volume (E.32b recs line 632); that
   is a P9 regime difference, not an exclusion.

### e.3 Worked ZL example: a WASDE day (M3_calc.out section 4)
Release window [10:58, 11:30] removes starts t in [10:58 - h, 11:30]: 48 / 63 / 93 starts for h = 15 / 30 / 60;
kept 215 / 185 / 125 of 263 / 248 / 218. n_eff falls from 18.47 / 9.23 / 4.62 to 16.27 / 8.13 / 4.07 (blocks
08:35-10:58, 143 minutes, and 11:31-13:12, 101 minutes; M3 d.2 closed form n_eff = covered minutes / h).

### e.4 Leakage traps
1. Windows from the data (volatility spikes). Test: build W from calendar files and clock only, without loading any
   price; assert equality (M3 g.6 trap 1).
2. Unscheduled events excluded with hindsight (EPA, leaks). Test: no exclusion uses an unscheduled time; they appear
   only as a stratum.
3. Release dates rescheduled after the fact. Test: calendar rows carry the scheduled date as published before the day
   (M3 g.6 trap 2).
4. Roll detection from volume inside the label window. Test: roll dates from the instrument_id mapping only.
5. Stale limit bands (above). Test: count dates on which rule 5 removes all minutes, per rule source.

### e.5 Verdict
USE rules 1-6 mapped to ZL; ADD the FOMC window if the lead agrees (recommended); report EIA WPSR and EPA dates as
strata only; decide the limit-band source (a or b) before the freeze and record the count of dates affected.

---

## (f) Sample weights and rows per day

### f.1 Equations
E.32 P3.7 (lines 346-354) for ZL: c_m = the number of rows of the same label type and date whose span meets one-minute
interval m by more than one second; u_i = mean of 1/c_m over the intervals span_i meets; raw u_i are the weights, per
date, no renormalisation. An FH span of h minutes plus L meets h intervals. TB spans are the realised [t, tau + L]
(weights only; never a feature or a scorer input, M3 d.5 trap 2).

### f.2 Worked ZL example (M3_calc.out section 4; ordinary date, before exclusions)

| label | rows a date | n_eff a date | rows over 796 OOF dates | n_eff over 796 |
|---|---|---|---|---|
| F15 / T15 | 263 | 18.47 | 209,348 | 14,699 |
| F30 / T30 | 248 | 9.23 | 197,408 | 7,350 |
| F60 | 218 | 4.62 | 173,528 | 3,675 |

n_eff = 277 / h (covered minutes 08:35-13:12, M3 d.2 closed form); interior u_i = 1/h; the first and last labels of a
date are more unique. TB n_eff is larger than the FH figure (realised spans average 0.71-0.77 h, a.3). Every
reported standard error uses n_eff or day-block inference, never the row count (M3 d.7).

### f.3 Verdict
USE uniqueness weights as the single declared weighting; no time decay; no sequential bootstrap (M3 d.7). Labels never
cross dates, so weights never depend on another fold.

---

## (g) Protocol inputs (ready for P3 of the ZL program)

    P3.1 Labels: F15, F30, F60 (fixed horizon), T15, T30 (triple barrier, vertical h = 15, 30). Not searched: F05,
         T60, to-close, mid or last-trade labels.
    P3.0 Constants: L = 1.000 s (selection; 0.300 s test list only); f = 0.880 ZL ticks (Topstep USD 5.28 / 6.00);
         tick 0.01 c/lb from the definitions (checked_tick with the cents fix); clock ts_recv; book update = state
         after an F_LAST record; "as of u" = last update with ts_recv <= u; M_ZL defined iff both sides, bid < ask,
         not bad. MBP-1 bad-book reading (if MBP-1 is the label source): an update is bad iff its F_LAST record carries
         F_MAYBE_BAD_BOOK.
    P3.2 Executable prices: buy at ask_1(ZL) as of u + L, sell at bid_1(ZL) as of u + L; one contract, no depth walk;
         fallback, entry-not-made, limit mark and last-touch mark exactly as E.32 P3.2 with ZL's front and limits.
    P3.3 FH: N_long = bid_1(t+h+L) - ask_1(t+L) - 0.880; N_short = bid_1(t+L) - ask_1(t+h+L) - 0.880;
         y = +1 if N_long > 0, -1 if N_short > 0, else 0 (assert not both positive).
    P3.4 TB: m0 = M_ZL(t+L); b = 1.0 x sigma_ZL(D) x sqrt(h); first ZL update in (t+L, t+L+h] with M_ZL >= m0 + b
         (up) or <= m0 - b (down), undefined mids ignored, ties by update order; tau = that update's ts_recv or
         t+L+h; N^T at tau + L; y^T = barrier sign or 0; market exits only. sigma_ZL(D) = population SD of 1-minute
         ZL mid changes over 08:35-13:13 of the 20 prior trade dates, chained across ZL rolls.
    P3.5 Trade rule: E.32 P3.5 unchanged (EV from calibrated p_k and weighted class means of N; long iff EV_long >
         max(EV_short, 0); ties no trade).
    P3.6 Exclusions: (1) starts >= 08:35:00; (2) spans end <= 13:13:00; (3) [R-2, R+30] at 11:00 CT for the seven
         USDA/NOPA report types of E.32 P3.6 rule 3 with its files, parse rule, NOPA rule dates and counts; FOMC
         [12:58, 13:13] on decision dates if adopted; (4) ZL.v.0 roll date and the next trade date, early-close and
         late-open dates; (5) row: no ZL update without bid or ask or marked bad in the span; row and entry: not
         M_ZL(t) >= HL - 0.02c or <= LL + 0.02c, limit source per the lead's choice (a) or (b), skip-and-count rule
         as E.32; (6) ZS/ZM invalid -> features fall back. Strata (report only): EIA WPSR Wednesdays [09:28, 10:00];
         EPA RFS/RVO dates.
    P3.7 Rows: every t in G_h(D) = {08:35, ..., 13:12 - h} on OOF dates passing P3.6 with M_ZL(t) defined
         (263 / 248 / 218 a date for h = 15 / 30 / 60); weights = raw average uniqueness at 1-minute resolution.
    P3.8 Simulation: one position, at most 20 entries a date, next decision at the first grid minute at or after the
         exit fill; latest entries 12:57 / 12:42 / 12:12 CT; max FH trades a date 17 / 8 / 4.
    P6.4 Variants (after the test list is hashed; select nothing): (i) market at L = 1.000 s and 0.300 s;
         (ii) trade-through limit at the ZL touch, fill on the first A/B print strictly through within
         (t+L, min(t+60 s, exit decision)+L], side-N never fills; (ii-b) conversion to market at the timeout;
         Topstep fee only. (iii) not run.

Open items for the lead (not decided here): T60 in or out (recommended out); FOMC window (recommended in); limit-band
source for rule 5; label source parity (c.4 options a, b, c); re-basing e80 / K2 to n_max = 17 / 8 / 4.

---

## Searched, not found, and limits

- ZL daily price-limit values for 2021-2024 beyond the 4.50 c quoted for 2022-12-01: not found (search 1 returned the
  semi-annual reset mechanism only; CME notices are on cmegroup.com, which this stage may not fetch; the AgCanada
  page answered 403). The protocol reads limits from the definitions, so no value is needed for the rule itself.
- Intraday ZL response to EIA's WPSR: no study found (search 4).
- EPA announcement times of day for 2021-2023: not found; only trade-press day-level reports (searches 2-3).
- ZL settlement window: not found for ZL (F2_grains.md line 158); 13:14-13:15 CT verified for ZC, ZS, ZW only.
- ZL spread: only a snippet (2.06 ticks, [unverified]); the real distribution is a DataFacts count.
- The Brownian numbers (a.3, c.3, d.3) are stylised: ZL's variance ratio below 1 at 15-60 minutes means the real path
  is not Brownian; they size the problem and decide nothing.


---

<!-- concatenated unchanged: reports/stage_e34_briefs/M4_power_ZL.md (sha256 be17411e03969e92) -->

# E.34 ZL methods addendum, M4: power and N (MathReaderM4-OpusHigh, opus high)

Written 2026-10-29 12:10-12:17 PDT. Pure arithmetic: no market-data file was opened, and no price, return or outcome
was computed. Synthetic normal draws were used only in the D2 simulation (section f). Script:
reports/stage_e34_briefs/work/MathReaderM4-OpusHigh/m4_power.py (sha256 26de065a0666ab4c...). Full output:
work/MathReaderM4-OpusHigh/m4_out.md (sha256 050071a59795f067...; 195 lines). Run:
`nice -n 10 uv run python reports/stage_e34_briefs/work/MathReaderM4-OpusHigh/m4_power.py`, 2 s.

The script imports the frozen E.32 functions that E.32b recs 4.4 (reports/stage_e32b_recommendations.md:501-507)
names: `p7_final.se_sharpe`, `p7_final.g4_threshold` (reports/stage_e32_briefs/protocol/p7_final.py:41-56),
`p7_thresholds.required_sharpe` and `trade_dates` (p7_thresholds.py:55-81), and
`funnel.multiple_comparisons.expected_max_sharpe` / `deflated_sharpe_ratio` (funnel/multiple_comparisons.py:63-81).
Its `row()` repeats E.32b's own scratch script line for line (`hurdles.py`, still present in the E.32b scratchpad
.../3860d0d1-.../scratchpad/d5/hurdles.py, lines 22-33), with T_disc, T_test, skew and kurtosis passed in as
parameters.

**Reproduction check.** At N 838, T_disc 796, T_test 870 the output gives SR0 0.1137, G3 0.1724 (t 4.86), b_test
0.1649 (t 4.86; unrounded 0.164882), G4 0.2007 (t 5.66), binding 0.2007, SR80_test 0.1936. That matches E.32b recs
4.4 (line 512), protocol P7.2 (reports/stage_e32_discovery_protocol.md:704-712; 0.164882 at line 724) and E.33c's
s80 values 0.2309 / 0.2025 (reports/E.33c_RETURN.md:194-195) to every printed digit. The N 938, 1038 and 1138 rows
also match E.32b's 100, 200 and 300 rows (lines 518, 520, 521) to every digit.

---

## Equations (used throughout)

Symbols: SR is the daily Sharpe of the net daily series (zeros on no-trade dates); T is the number of dates; g3 is
skewness; g4 is raw kurtosis (3 = normal); V is the cross-trial variance of the Sharpe estimates; gamma = 0.5772;
Phi is the standard normal CDF; z80 = Phi^-1(0.8) = 0.8416.

1. Expected maximum under the null (BLdP 2014 eq. 1; E.32 brief M5a d.2 item 1, reports/stage_e32_methods_brief.md:7259-7260):
   e(N) = (1 - gamma) Phi^-1(1 - 1/N) + gamma Phi^-1(1 - 1/(N e)),  SR0 = sqrt(V) e(N).
2. DSR (BLdP 2014 eq. 2; M5a d.2 item 2, line 7261-7262; funnel/multiple_comparisons.py:81):
   DSR = Phi[ (SR - SR0) sqrt(T - 1) / sqrt(1 - g3 SR + (g4 - 1)/4 SR^2) ].
3. G3 = the smallest SR with DSR >= 0.95 at N, V = 1/(T_disc - 1), T = T_disc (P8 G3, protocol line 744-748).
   First-order form (M5a d.2 item 3, line 7266-7269): G3 ~ (e(N) + 1.645) / sqrt(T_disc).
4. b_test = max(3.0 / sqrt(T_test), the smallest SR with DSR >= 0.95 at N, V = 1/(T_test - 1), T = T_test)
   (p7_final.py docstring lines 13-15; kept by V52 item 1 per E.32b recs 4.4 line 506).
5. Mertens SE (M5b d.2 item 3, line 8223-8224; p7_final.py:41-42): se(SR, T) = sqrt((1 - g3 SR + (g4 - 1)/4 SR^2)/(T - 1)).
6. G4 = the smallest SR_d with SR_d - se(SR_d, T_disc) >= b_test (P8 G4, protocol lines 749-752). Binding = max(G3, G4).
7. SR80 (the true daily Sharpe that passes with probability 0.80): SR80 = bar + z80 se(bar, T). Here bar = b_test
   on T_test for the test, G3 or the binding threshold on T_disc for discovery. This is p7_final.py's convention
   (line 104) and E.33's (reports/stage_e33c_briefs/work/D_stats.md:249).
8. Per-trade minimum detectable net edge (random walk, independent trades; E.32b holding scope lines 16-18):
   e80(h, n) = SR80 x sigma_h / sqrt(n) ticks a trade, net. Here n is the average number of trades per date,
   inactive dates included, because a series that trades n' a day on a fraction p of dates has daily SR about
   mu sqrt(n' p) / sigma_h. The required gross is c_f + e80, with c_f = 2.38 ticks for Topstep ZL (E.32b holding
   scope 15, line 915).
9. Dependence (M5b c.2 items 3 and 5, lines 8057-8067): with same-day equicorrelation rho_w among k trades a day,
   D_day = 1 + (k - 1) rho_w and e80 scales by sqrt(D_day).

---

## (a) T_disc and T_test for ZL

The counts come from `p7_thresholds.trade_dates`, which counts weekdays minus grain full closures. The closures
come from the program's CME grains holiday calendars (data.calendars.grains from 2019-05-01, the hist2010 grains
calendar before; docstring p7_thresholds.py:5-7). It opens no market data and no sealed file; neither calendar is
listed in reports/stage_e32_briefs/seal/derived_unsealed_files.tsv (checked by grep).

| window | span | weekdays | CBOT trade dates | burn-in | T |
|---|---|---|---|---|---|
| discovery | 2020-12-01..2024-02-29 | 848 | 816 | 20 | **T_disc = 796** |
| test, MBO | 2017-05-22..2020-11-30 | 921 | 890 | 20 | **T_test = 870** |
| test, MBP-1 | 2017-05-01..2020-11-30 | 936 | 905 | 20 | **T_test = 885** |

- Cross-checks against recorded counts (no data opened). E.33 split the owned ZL MBP-1 into records on 816 dates
  (BRIEFS shared facts; E.33's split record). E.33's OOF set was 796 dates, 2020-12-30..2024-02-29, in "6 blocked
  folds with a 21-date embargo" (reports/E.33c_RETURN.md:18, 212). Every post-burn-in date is out of fold, so
  T_disc = 816 - 20. E.32 P9 records 890 program dates and T_test = 870 for the MBO window
  (protocol lines 777-781). The MBP-1 window adds the 15 sealed trade dates 2017-05-01..2017-05-19 that P9 says
  "stay sealed and untested" under MBO (line 777). 890 + 15 = 905, which matches the calendar.
- Assumption: the ZL program keeps E.33's construction (a 20-date feature burn-in; folds that make every
  post-burn-in date OOF). F09 relative-value features with longer lookbacks would need a longer burn-in. At 40
  dates (T_disc 776, T_test 850) the binding threshold rises from 0.2007 to 0.2031 and SR80_test from 0.1936 to
  0.1959 (m4_out.md "Sensitivity" table). That is about +1.2%, so e80 rises by about 1.2%.
- Which test length applies depends on the data the test buys. The F10 order-book state can be built from MBP-1,
  which is the schema owned for discovery (no ZL MBO is owned; BRIEFS shared facts). In that case the MBP-1 span
  (T_test 885) is the like-for-like test. One open item: before 2017-05-21 the data are MDP 2 level-aggregated,
  and "the ts_recv field on all MDP 2 data is set to the same value as ts_event" (P9 quoting Databento, protocol
  lines 772-775). The 15 early dates may therefore differ in timestamp semantics. That is a data question for M3
  or DataFacts, not arithmetic.

## (b) Threshold table at N = 838 + B

### Test on MBO (T_disc 796, T_test 870), normal moments

| B | N | e(N) | SR0 disc | G3 SR_d (t) | b_test (t) | G4 SR_d (t) | binding | SR80_test | SR80 disc G3 | SR80 disc binding | b_test unrounded |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 838 | 3.2045 | 0.1137 | 0.1724 (4.86) | 0.1649 (4.86) | 0.2007 (5.66) | 0.2007 | 0.1936 | 0.2025 | 0.2309 | 0.164882 |
| 40 | 878 | 3.2179 | 0.1141 | 0.1729 (4.88) | 0.1653 (4.88) | 0.2012 (5.68) | 0.2012 | 0.1941 | 0.2030 | 0.2313 | 0.165339 |
| 62 | 900 | 3.2250 | 0.1144 | 0.1732 (4.89) | 0.1656 (4.88) | 0.2014 (5.68) | 0.2014 | 0.1943 | 0.2032 | 0.2316 | 0.165581 |
| 100 | 938 | 3.2369 | 0.1148 | 0.1736 (4.90) | 0.1660 (4.90) | 0.2018 (5.69) | 0.2018 | 0.1947 | 0.2036 | 0.2320 | 0.165984 |
| 150 | 988 | 3.2517 | 0.1153 | 0.1741 (4.91) | 0.1665 (4.91) | 0.2023 (5.71) | 0.2023 | 0.1952 | 0.2042 | 0.2325 | 0.166489 |
| 200 | 1038 | 3.2657 | 0.1158 | 0.1746 (4.93) | 0.1670 (4.92) | 0.2028 (5.72) | 0.2028 | 0.1957 | 0.2047 | 0.2330 | 0.166967 |
| 250 | 1088 | 3.2790 | 0.1163 | 0.1751 (4.94) | 0.1674 (4.94) | 0.2033 (5.73) | 0.2033 | 0.1962 | 0.2052 | 0.2334 | 0.167421 |
| 300 | 1138 | 3.2917 | 0.1167 | 0.1755 (4.95) | 0.1679 (4.95) | 0.2037 (5.75) | 0.2037 | 0.1966 | 0.2056 | 0.2338 | 0.167853 |

### Test on MBP-1 (T_disc 796, T_test 885)

The discovery columns (SR0, G3, SR80 disc G3) do not change. The test-driven columns do:

| B | N | b_test (t) | G4 (t) | binding | SR80_test | SR80 disc binding | b_test unrounded |
|---|---|---|---|---|---|---|---|
| 0 | 838 | 0.1635 (4.86) | 0.1993 (5.62) | 0.1993 | 0.1920 | 0.2294 | 0.163470 |
| 40 | 878 | 0.1639 (4.88) | 0.1997 (5.64) | 0.1997 | 0.1924 | 0.2299 | 0.163924 |
| 62 | 900 | 0.1642 (4.88) | 0.2000 (5.64) | 0.2000 | 0.1927 | 0.2301 | 0.164164 |
| 100 | 938 | 0.1646 (4.90) | 0.2004 (5.65) | 0.2004 | 0.1931 | 0.2305 | 0.164564 |
| 150 | 988 | 0.1651 (4.91) | 0.2009 (5.67) | 0.2009 | 0.1936 | 0.2310 | 0.165064 |
| 200 | 1038 | 0.1655 (4.92) | 0.2014 (5.68) | 0.2014 | 0.1940 | 0.2315 | 0.165538 |
| 250 | 1088 | 0.1660 (4.94) | 0.2018 (5.69) | 0.2018 | 0.1945 | 0.2320 | 0.165988 |
| 300 | 1138 | 0.1664 (4.95) | 0.2022 (5.71) | 0.2022 | 0.1949 | 0.2324 | 0.166416 |

Reading:
- G4 binds over G3 at every budget. In t terms the required discovery t is 5.66 to 5.75, and the test t is
  4.86 to 4.95. The daily t > 3.0 bar (0.1017 at T 870; 0.1008 at T 885) never binds at the test.
- A budget of 0 to 300 moves the binding threshold by +0.0030 (+1.5%) and SR80_test by +0.0030. The test's
  length moves them less: MBP-1 instead of MBO lowers b_test by 0.0014.
- Moment sensitivity at N 838 (m4_out.md, the "Moment sensitivity" table), as binding / SR80_test:
  - normal: 0.2007 / 0.1936
  - skew -0.5, kurtosis 6: 0.2059 / 0.1979
  - kurtosis 10: 0.2033 / 0.1956
  - kurtosis 20: 0.2070 / 0.1985
  - skew -2, kurtosis 30: 0.2270 / 0.2151

  A series that trades on a fraction p of dates has raw daily kurtosis of about 3/p (for example 6 at
  p = 0.5), so the skew -0.5 / kurtosis 6 row is the realistic floor for a once-or-twice-a-day ZL rule.

## (c) e80 in ticks a trade, net (ZL day-session sigma_h from E.32b holding scope 15, lines 922-930)

e80 = SR80 x sigma_h / sqrt(n). sigma_h: 20.37 (h 15), 28.10 (h 30), 38.21 (h 60). Entry caps n_cap: 19, 9, 4
(line 941-946). Test on MBO.

| N (B) | h | n/date | e80 disc G3 | e80 disc binding (G3+G4) | e80 test | edge at the binding threshold (about 50% power) | gross needed at test, c_f + e80 test |
|---|---|---|---|---|---|---|---|
| 838 (0) | 15 | 19 (cap) | 0.95 | 1.08 | 0.90 | 0.94 | 3.28 |
| 838 (0) | 15 | 4 | 2.06 | 2.35 | 1.97 | 2.04 | 4.35 |
| 838 (0) | 15 | 2 | 2.92 | 3.33 | 2.79 | 2.89 | 5.17 |
| 838 (0) | 15 | 1 | 4.12 | 4.70 | 3.94 | 4.09 | 6.32 |
| 838 (0) | 30 | 9 (cap) | 1.90 | 2.16 | 1.81 | 1.88 | 4.19 |
| 838 (0) | 30 | 4 | 2.85 | 3.24 | 2.72 | 2.82 | 5.10 |
| 838 (0) | 30 | 2 | 4.02 | 4.59 | 3.85 | 3.99 | 6.23 |
| 838 (0) | 30 | 1 | 5.69 | 6.49 | 5.44 | 5.64 | 7.82 |
| 838 (0) | 60 | 4 (cap) | 3.87 | 4.41 | 3.70 | 3.83 | 6.08 |
| 838 (0) | 60 | 2 | 5.47 | 6.24 | 5.23 | 5.42 | 7.61 |
| 838 (0) | 60 | 1 | 7.74 | 8.82 | 7.40 | 7.67 | 9.78 |
| 900 (62) | 30 | 9 / 2 / 1 | 1.90 / 4.04 / 5.71 | 2.17 / 4.60 / 6.51 | 1.82 / 3.86 / 5.46 | 1.89 / 4.00 / 5.66 | 4.20 / 6.24 / 7.84 |
| 1138 (300) | 15 | 19 / 2 / 1 | 0.96 / 2.96 / 4.19 | 1.09 / 3.37 / 4.76 | 0.92 / 2.83 / 4.00 | 0.95 / 2.93 / 4.15 | 3.30 / 5.21 / 6.38 |
| 1138 (300) | 30 | 9 / 2 / 1 | 1.93 / 4.09 / 5.78 | 2.19 / 4.65 / 6.57 | 1.84 / 3.91 / 5.52 | 1.91 / 4.05 / 5.72 | 4.22 / 6.29 / 7.90 |
| 1138 (300) | 60 | 4 / 2 / 1 | 3.93 / 5.56 / 7.86 | 4.47 / 6.32 / 8.94 | 3.76 / 5.31 / 7.51 | 3.89 / 5.50 / 7.78 | 6.14 / 7.69 / 9.89 |

- The N 838 cap rows reproduce E.32b holding scope 15 (lines 944-946): 0.95 / 1.08 / 0.90; 1.90 / 2.16 / 1.81;
  3.87 / 4.41 / 3.70.
- The MBP-1 test lowers each test e80 by about 0.8% (h30 cap 1.80, h30 n=1 5.39; m4_out.md second e80 table).
- At realistic rates the detectable edge is 2 to 3 times the cap value. E.33's G1 passers traded about one to two a
  date; at those rates a 30-minute rule needs 3.85 to 5.44 ticks net at the test, and 4.59 to 6.49 ticks net to clear
  discovery with 80% probability. In gross terms that is 6.2 to 7.8 ticks, or 0.22 to 0.28 sigma_30, per trade.

**Heavy-tail and independence caveat (E.33c 3.7 v, reports/E.33c_RETURN.md:194-199).** E.33 called the formula "a
lower-side figure for heavy-tailed series, which the measured figures below cover". On ZM, measured per configuration
as e80 = s80 x SD(X_D) / (trades per date), with no random-walk or independence assumption, the G1 passers' medians
were 1.57 (T15), 1.95 (T30), 4.33 (F60) and 4.37 (F30) ticks. The formula gave 1.41 at 15 minutes and 4 a date, 1.99
at 30 minutes and 4 a date, and 3.98 at 60 minutes and 2 a date (same lines; the ZM table is in
reports/stage_e33c_briefs/work/D_stats.md:253-290). These figures are ZM aggregates from a RETURN summary, not ZL
statistics.

Three effects separate the measured figures from the formula. The ZL facts set their direction, not their size:
1. Tails raise the bar slightly through se(): +2 to 4% at kurtosis 6 to 20, +11% at skew -2 / kurtosis 30
   (section b).
2. Same-day correlation multiplies e80 by sqrt(1 + (k - 1) rho_w), and day-to-day dependence works the same way
   (M5b c.2 items 3 and 5). This effect can be the larger one, and it only raises e80.
3. Pooled per-trade SD differs from sigma_h. E.33's measured pooled sigma ranged from 0.83 x (T30) to 1.26 x (F15)
   of the 3.15 sqrt(h) number, depending on label and exit (D_stats.md:255-279).

The ZL program should therefore treat the formula column as a floor. The protocol's P10 report should report the
measured version (s80 x SD(X_D) / mean trades per date) beside it, as E.33 did.

## (d) The K2 comparison against 1.8 ticks and the budget

K2 (E.32b recs, lines 25 and 551-552): "The best discovery configuration's net edge per trade is below the test's
minimum detectable edge (1.8 ticks for a 30-minute hold): stop."

- 1.8 ticks is the test e80 at h 30 at the 9-entry cap, N 838, T_test 870: 0.1936 x 28.10 / 3 = 1.81.
- How the budget moves it: B 62 gives 1.82, B 150 gives 1.83, B 300 gives 1.84. With the MBP-1 test: 1.80 at B 0
  and 1.83 at B 300. Rounded to one decimal, it stays 1.8 for every B up to 300 on either schema.
- The fixed 1.8 is a horizon and rate figure, not a program constant. The test's own detectable edge is 0.90 (h 15,
  cap 19), 1.81 (h 30, cap 9) and 3.70 (h 60, cap 4). It is 3.85 or 5.44 for a 30-minute rule at 2 or 1 trades a
  date.
- Two consequences under the formula's assumptions follow. These are for the lead; I am not ruling on them.
  1. **K2 is weaker than G4 for slow rules.** Any configuration that clears the binding threshold has observed
     SR_d >= 0.2007, so its observed per-trade net is at least 0.2007 sigma_h / sqrt(n). That is 1.037 x the
     test's e80 at its own rate. For a 30-minute rule at 1 to 2 trades a date, a 1.8-tick K2 passes edges of
     1.8 to 3.8 ticks that G4 would already have rejected. K2 adds nothing there.
  2. **At 15 minutes and high rates, K2 at 1.8 is stricter than the test's power requires.** A G4 passer at h 15
     can have net below 1.8 when n > (0.2007 x 20.37 / 1.8)^2 = 5.2 trades a date. K2 would stop it although the
     test's e80 at that rate (for example 1.39 at n = 8) is below its edge.

  A rate- and horizon-matched K2 would compare the best configuration's net with
  e80_test(h, n_bar) = SR80_test(N) sigma_h / sqrt(n_bar), at the configuration's own n_bar and measured
  SD(X_D). That is the E.33 measured form. Whether to restate K2 this way is a lead decision.
- The budget's effect on the whole program: going from B = 0 to B = 300 raises every e80 by 1.5%. The choice of
  horizon and trade rate moves e80 by a factor of 2 to 8. The budget is not the lever on power. The trade rate is,
  and so is the measured dependence.

## (e) Holm at the test with up to 3 finalists

screening/stage_e_verdict.py runs Holm over the Tier A p_upper at 0.05 / K (lines 21-23, 545). K is the list's
`k_holm` in 1..9 (v13; lines 34-35, 84, 369-373). V14 (b) and E.32 P9 use K = 9 (protocol line 787). The steps are
`holm_alpha_k = 0.05 / K` and `threshold = alpha_K / (m - i)` (screening/stage_e_stats.py:288-293, 317-334).
p_upper is a stationary block bootstrap p (mean block 5, B = 10,000; stage_e_verdict.py:15-18), whose floor is
1/10,001 (z 3.72).

| K | m = 1 | m = 2 | m = 3 (first step) | m = 3, steps 1 / 2 / 3 (z) |
|---|---|---|---|---|
| 1 | 0.0500 (z 1.645) | 0.0250 (1.960) | 0.0167 (2.128) | 2.128 / 1.960 / 1.645 |
| 2 | 0.0250 (1.960) | 0.0125 (2.241) | 0.0083 (2.394) | 2.394 / 2.241 / 1.960 |
| 9 | 0.0056 (2.539) | 0.0028 (2.773) | 0.0019 (2.902) | 2.902 / 2.773 / 2.539 |

- The K = 9 row reproduces P7.2's 2.539 / 2.773 / 2.902 (protocol lines 716-718).
- Effect on the test bar: none, in normal-approximation terms. The strictest Holm z (2.902) is below t 3.0, and
  both are far below b_test's t of 4.86 to 4.95, so the combined bar is b_test whether there are 1, 2 or 3
  finalists and whether K is 1, 2 or 9. A ZL registration with two families (F10, F09) could use K = 2 or keep 9
  without changing power.
- Holm could bind only if the bootstrap SE of the daily mean exceeds the iid SE by a factor f with 2.902 f > 4.86,
  that is f > 1.67 (day-to-day autocorrelation; Lo 2002 eq. 19's factor, M5b c.2 item 3). The t > 3.0 and DSR
  checks use the iid SD and Mertens SE (stage_e_verdict.py:209-213, 197), so they do not inflate with dependence.
  The P10 or test report should state the series' SE_boot / SE_iid.
- Holm's m counts Tier A only (stage_e_verdict.py:541-545); Tier B does not enter Holm.

## (f) The open E.32 D2 item (V14 (c), the test DSR variance)

As coded, the program verdict's DSR takes V = pvariance of the Tier A Sharpes if there are 2 or more, else of Tier A
and Tier B (stage_e_verdict.py:23-25, 216-219, 550-553). So SR0 = e(N) x pop SD(tested Sharpes). E.32 D2
(reports/E.32_RETURN.md:436-440) recommends amending it so that V = 1/(T_test - 1). That would make check (1)'s
DSR identical to check (2)'s. The item "stays open until a test is registered (V56 item 4)" (E.32b recs line 487).

Multipliers (SR0 / s, with a member at observed s and nulls at exactly 0):

| N | e(N) | 1 member + 1 null | 1 member + 2 nulls |
|---|---|---|---|
| 838 | 3.2045 | 1.602 | 1.511 |
| 878 | 3.2179 | 1.609 | 1.517 |
| 900 | 3.2250 | 1.613 | 1.520 |
| 1138 | 3.2917 | 1.646 | 1.552 |

The 838 row reproduces P7.2 (protocol lines 727-729: "1.60 x", "1.51 x"). SR0 > s means DSR < 0.5. Beside null
companions, no true Sharpe can pass check (1), and the budget only raises the multiplier.

I also ran a synthetic simulation, drawing every member's estimate as N(s_i, se(s_i, 870)) with 4,000 reps at
N 838 (2,000 at N 1138; m4_out.md). Pass probabilities by true Sharpes:

| true Sharpes (finalist first) | V14 (c) DSR | amended DSR (= check 2) | t > 3 | as coded: all three | amended: DSR and t |
|---|---|---|---|---|---|
| 0.20 + 2 nulls (Tier A of 1, Tier B null) | 0.000 | 0.845 | 0.997 | 0.000 | 0.845 |
| 0.25 + 2 nulls | 0.000 | 0.995 | 1.000 | 0.000 | 0.995 |
| 0.40 + 2 nulls | 0.000 | 1.000 | 1.000 | 0.000 | 1.000 |
| 0.25 + 0.15 | 0.704 | 0.993 | 1.000 | 0.699 | 0.993 |
| 0.25 + 0.10 | 0.210 | 0.994 | 1.000 | 0.206 | 0.994 |
| 0.20 + 0.15 | 0.848 | 0.857 | 0.998 | 0.725 | 0.857 |
| 0.20 + 0.10 | 0.387 | 0.842 | 0.999 | 0.294 | 0.842 |
| 0.25 + 0.20 + 0.15 | 0.855 | 0.991 | 1.000 | 0.851 | 0.991 |
| 0.25 + 0.15 + 0.00 | 0.002 | 0.994 | 1.000 | 0.002 | 0.994 |

The N 1138 values are 0.00 to 0.04 lower; for example, 0.20 + 2 nulls amended is 0.824.

- P7.2's analytic figures (0.83 for 0.25 beside 0.15; 0.09 for 0.25 beside 0.10; protocol lines 729-731) fix the
  companion at its true Sharpe. This simulation also draws the companion's noise. Its 0.70 and 0.21 differ for
  that reason (the gap's SD, sqrt(2) x 0.034 = 0.048, is half the 0.10 gap). This is a model difference, not an
  error in either.
- What D2 changes for ZL:
  - With a Tier A of 1, the most likely outcome given E.33's empty Tier A, the Tier B companions are selected with
    gates ignored and are likely near-null. As coded, the test then has power of about 0 for any true Sharpe.
  - Amended, the program bar is exactly b_test, and the power table in (b)/(c) holds: 0.80 at SR80_test.
  - With 2 or 3 real finalists, the coded version also depends on the gap between their true Sharpes, which the
    discovery outcomes cannot pin down.
  - Amending cannot loosen the bar below check (2), and Holm, t and PBO are unchanged (P9, protocol lines
    793-799).
  - Every e80 and power figure in this file assumes the amendment, or at least 2 real finalists of similar true
    Sharpe. If V14 (c) stays as coded, the ZL protocol should say that the tabulated powers are upper bounds.

## Verdict (arithmetic only; selection rules and gates are the lead's)

1. **Reproduced.** The frozen code reproduces E.32b's N 838 row and P7.2 to every printed digit. The same functions
   can serve the ZL protocol unchanged, with T_disc 796 and T_test 870 (MBO) or 885 (MBP-1).
2. **N barely matters.** B = 0 to 300 moves the binding threshold from 0.2007 to 0.2037 and test e80 by 1.5%.
   Any budget in {0..300} leaves K2's 1.8 ticks at 1.8.
3. **Trade rate and dependence matter.** At E.33's observed 1 to 2 trades a date, a 30-minute ZL rule needs 3.9 to
   5.4 ticks net at the test, 6.2 to 7.8 ticks gross. A 60-minute rule needs 5.2 to 7.4 net. These are floors:
   tails add 2 to 11%, and same-day correlation multiplies by sqrt(D_day).
4. **K2.** As a fixed 1.8 ticks, K2 is redundant with G4 for slow rules and stricter than needed for fast 15-minute
   rules. A rate- and horizon-matched form is available (section d). The choice is the lead's.
5. **Holm** never binds at the test (z at most 2.90 against b_test's t of 4.86 or more) unless the bootstrap SE
   exceeds the iid SE by more than 1.67 x.
6. **D2 is the one item that changes power materially.** Unamended, a lone finalist beside Tier B nulls cannot pass.

## (g) Protocol inputs (ready for P7)

Formulas: equations 1-8 above, computed with the functions named at the top. b_test is pinned at the unrounded
value at the registered N. Normal moments apply for the published rows; G3 and G4 use each configuration's own
moments at run time (P8).

Fixed inputs: T_disc = 816 - 20 = 796 (2020-12-01..2024-02-29, CBOT grain calendar). T_test = 890 - 20 = 870
(MBO, 2017-05-22..2020-11-30) or 905 - 20 = 885 (MBP-1, 2017-05-01..2020-11-30). V_disc = 1/795. V_test = 1/869
(MBO) or 1/884 (MBP-1). The DSR and G4 targets are 0.95 and SR_d - se >= b_test, and the daily t bar is 3.0.
z80 = 0.8416. sigma_h = 20.37 / 28.10 / 38.21 (h 15 / 30 / 60). n_cap = 19 / 9 / 4. c_f = 2.38.

| B | N | MBO test: G3 / b_test (unrounded) / G4 = binding / SR80_test / SR80 disc binding | MBO e80 test h15 cap, h30 cap, h60 cap | MBO e80 test h30 at n = 1 / 2 / 4 | MBP-1 test: b_test (unrounded) / binding / SR80_test |
|---|---|---|---|---|---|
| 0 | 838 | 0.1724 / 0.164882 / 0.2007 / 0.1936 / 0.2309 | 0.90, 1.81, 3.70 | 5.44 / 3.85 / 2.72 | 0.163470 / 0.1993 / 0.1920 |
| 40 | 878 | 0.1729 / 0.165339 / 0.2012 / 0.1941 / 0.2313 | 0.91, 1.82, 3.71 | 5.45 / 3.86 / 2.73 | 0.163924 / 0.1997 / 0.1924 |
| 62 | 900 | 0.1732 / 0.165581 / 0.2014 / 0.1943 / 0.2316 | 0.91, 1.82, 3.71 | 5.46 / 3.86 / 2.73 | 0.164164 / 0.2000 / 0.1927 |
| 100 | 938 | 0.1736 / 0.165984 / 0.2018 / 0.1947 / 0.2320 | 0.91, 1.82, 3.72 | 5.47 / 3.87 / 2.74 | 0.164564 / 0.2004 / 0.1931 |
| 150 | 988 | 0.1741 / 0.166489 / 0.2023 / 0.1952 / 0.2325 | 0.91, 1.83, 3.73 | 5.49 / 3.88 / 2.74 | 0.165064 / 0.2009 / 0.1936 |
| 200 | 1038 | 0.1746 / 0.166967 / 0.2028 / 0.1957 / 0.2330 | 0.91, 1.83, 3.74 | 5.50 / 3.89 / 2.75 | 0.165538 / 0.2014 / 0.1940 |
| 250 | 1088 | 0.1751 / 0.167421 / 0.2033 / 0.1962 / 0.2334 | 0.92, 1.84, 3.75 | 5.51 / 3.90 / 2.76 | 0.165988 / 0.2018 / 0.1945 |
| 300 | 1138 | 0.1755 / 0.167853 / 0.2037 / 0.1966 / 0.2338 | 0.92, 1.84, 3.76 | 5.52 / 3.91 / 2.76 | 0.166416 / 0.2022 / 0.1949 |

The e80 cells for B 40, 100, 150, 200 and 250 are SR80_test x sigma_h / sqrt(n) from the SR80_test column. They were
computed from the rounded SR80_test column (checked with a one-line python run, all cells agree), not printed by m4_power.py; the B 0, 62 and 300 cells are script output. A
registration recomputes the row at the registry's N immediately after its last registration (P7.1 rule) and on the
actual test schema.

## Inputs and sources used

- E.32 protocol P7-P9: reports/stage_e32_discovery_protocol.md:683-829.
- E.32b recs 4.4 and K2: reports/stage_e32b_recommendations.md:25, 478-531, 551-552.
- E.32b holding scope 1.5 and 15: reports/stage_e32b_holding_scope.md:14-18, 255-298, 913-951.
- E.33c 3.7 (v): reports/E.33c_RETURN.md:194-199. E.33 measured-e80 table: reports/stage_e33c_briefs/work/D_stats.md:249-292.
- Code: p7_final.py, p7_thresholds.py, funnel/multiple_comparisons.py, screening/stage_e_verdict.py,
  screening/stage_e_stats.py, and E.32b's scratch hurdles.py (path above).
- Methods brief: M5a d.2 (lines 7253-7285) and d.8 (7402-7417), M5b c.2 (8043-8079), and the Mertens/Opdyke
  evidence rows (8286-8287).
- Literature claims: none are new. The BLdP 2014, Mertens (via BLdP 2012) and Lo 2002 equations are cited through
  the E.32 brief's verified quotes (M5a d.8, M5b d.8). The brief marks "Var(SR_hat) ~ 1/T under the null" as
  [unverified] (line 7417), and that status carries over here.


---

<!-- concatenated unchanged: reports/stage_e34_briefs/L_lead_reconciliations.md (sha256 23f5ed5b22cac3de) -->

# E.34 Part M, section L: lead reconciliations of M1-M4 against Part F (lead, Opus 5.5 max, session 2)

Written 2026-10-29 13:55-14:10 PDT. Arithmetic on counts already on disk; no market-data file opened. Inputs:
reports/stage_e34_briefs/M1_F10_ZL.md (M1), M3_labels_ZL.md (M3), M4_power_ZL.md (M4),
reports/stage_e34_data_facts.md (DF34), reports/stage_e34_exposure.md (X).

## L.a M1's message rate and the minimum aggregation horizon, redone with DF34

Source check. M1's per-date counts (records median 188,737, F_LAST book events 168,917, T records 19,195, quietest
date 6,998 T on 2021-04-05) are cited from E.32's data facts (M1 lines 32-33, 242-249: "DF 238-262"), recorded counts,
not a decode. M1's only script (work/MathReaderM1-OpusHigh/scripts/m1_examples.py) contains no file-open or data-read
call (grep for open(, read_, dbn, parquet, DBNStore, from_file, glob, Path(: no hit). RULES rule 2 holds.

DF34's counts agree with M1's to within the date-set and median-rule difference: records median 188,782 against
188,737; T median 19,206 against 19,195 (DF34 section 3 table, line 127). F_LAST is set on 142,061,153 of 158,046,466
records (89.9%), so 188,782 x 0.899 = 169,700 book events against M1's 168,917.

The day-session share was M1's only assumption (83%). DF34 measured it (section 3 totals, lines 137-146):
- T records: 12,207,251 of 16,019,898 in 08:30-13:20 CT = 76.2%;
- all records: 111,058,833 of 158,044,028 = 70.3%.
M1's binding count is trades (M1 3.2, last paragraph). At the measured 76.2%, over the 290-minute day session:

| date | T a date | T a minute (x 0.762 / 290) | n in 5 minutes | iid SD of a sign imbalance, 1/sqrt(n) |
|---|---|---|---|---|
| quietest (2021-04-05, E.32 DF) | 6,998 | 18.39 | 91.9 | 0.104 |
| DF34 5th percentile | 12,352 | 32.46 | 162.3 | 0.078 |
| DF34 median | 19,206 | 50.47 | 252.3 | 0.063 |

Book events at the measured 70.3%: 168,917 x 0.703 / 17,400 s = 6.8 a second on the median date (M1's 0.70 row).

Ruling L.a. The minimum aggregation horizon stays 5 minutes and M1's windows stand ({5, 15, 30} for OFI and TI, 5 for
CR, 15 for SW and RF, 60 for lambda). M1's criterion (i) (iid SD at most 0.10) is read at the 5th-percentile date,
where it holds with margin (0.078). The one quietest date (the Monday after Easter 2021) misses it by 0.004. That is
immaterial next to the long-memory SD of 0.24 at 5 minutes (M1 3.2 table), which is why TI enters the models next to
its own trailing scale and never as a fixed threshold. Caveat: the per-date day share is taken at the pooled 816-date
share; DF34 tabulates day-session records per date (median 131,302) but not day-session T per date.

## L.b Entry caps and the form of K2

M3 d.2: under the frozen grid G_h(D) = {08:35, ..., 13:12 - h} CT and E.32 P3.8's re-entry rule (next decision at the
first grid minute at or after the exit fill), n_max(h) = floor((277 - h) / (h + 1)) + 1:
h 15: floor(262 / 16) + 1 = 17; h 30: floor(247 / 31) + 1 = 8; h 60: floor(217 / 61) + 1 = 4.
E.32b's n_cap = min(20, floor(290 / h)) = 19, 9, 4 assumed back-to-back holds over the whole 290-minute session.

Test e80 at the protocol caps, e80 = SR80_test x sigma_h / sqrt(n), sigma_h 20.37 / 28.10 / 38.21 (E.32b holding
scope 15):

| N (B) | SR80_test (T_test 870; M4 (g)) | h 15, n 17 | h 30, n 8 | h 60, n 4 |
|---|---|---|---|---|
| 838 (0) | 0.1936 | 0.96 | 1.92 | 3.70 |
| 1038 (200) | 0.1957 | 0.97 | 1.94 | 3.74 |

Ruling L.b.
1. The caps used in the protocol's power statements, P7 tables and P10 reports are 17 / 8 / 4, the maxima the frozen
   grid allows. E.32b's 19 / 9 / 4 are superseded for ZL. The 20-entry hard cap of E.32 P3.8 stays as written (it
   never binds at h >= 15).
2. K2 is stated in the rate- and horizon-matched, measured form that M4 (d) offers (E.33's measured e80):
   for a configuration c, e80_test(c) = SR80_test(N_reg, T_test) x SD(X_D,c) / nbar_c, with X_D,c its daily net P&L in
   ticks and nbar_c its mean trades a date, both over its out-of-fold discovery dates. K2 stops the run before the
   sealed read if no Tier A finalist has out-of-fold mean net per trade >= e80_test(c). Because mean(X_D) / nbar >=
   SR80 x SD(X_D) / nbar is the same inequality as SR_d >= SR80_test, and G4 already requires SR_d - se >= b_test
   (binding 0.2007 at N 838, above SR80_test 0.1936), K2 cannot bind for a Tier A finalist while T_test stays 870. It
   binds when the test window shrinks (for example dates lost to P1.2's drop rule or to a short purchase), because
   SR80_test rises as T_test falls. K2 is computed at the realised T_test immediately before the sealed read. The fixed
   figures (0.96 / 1.92 / 3.70 at N 838; 1.8 ticks at E.32b's cap 9) are reported beside it for continuity, not used.

## L.c The latest 30-minute entry

12:42 CT (10:42 PT), from the frozen grid: decision minutes 08:35 .. 13:12 - h CT, every label span ends by 13:13 CT,
before the 13:14-13:15 CT settlement window (M3 d.3, d.6; E.32 0.3 line 68; lab33 LAST_GRID_OFFSET 277). E.32b's
12:50 CT (10:50 PT, BRIEFS shared facts) was a planning figure against the 13:20 close and is superseded for the
protocol. Latest entries: 12:57 / 12:42 / 12:12 CT at h 15 / 30 / 60. Topstep's flat-by time (15:10 CT) never binds,
because ZL's day session ends at 13:20 CT.

## L.d A lower bound on ts_event (X section 6 residual)

DF34 (lines 104-112): ts_recv is non-decreasing within every file; ts_event > ts_recv on 230,475 records (0.146%);
ts_recv - ts_event > 1 s on 354; > 1 day on 7; F_SNAPSHOT and F_BAD_TS_RECV each on 848 records (identical counts).

Ruling L.d (goes into P1.2 as a drop-and-count rule; ts_recv stays the only clock, E.33 P0.3):
1. Drop every record flagged F_SNAPSHOT or F_BAD_TS_RECV (E.33's G6 exclusion; all MDP 2 records carry F_BAD_TS_RECV).
2. Drop every record whose ts_event lies before the first instant of its window's first trade date (discovery:
   2020-11-30T22:00:00Z; test: 2017-05-21T21:00:00Z, the start of trade date 2017-05-22, 16:00 CDT) or whose
   ts_recv - ts_event exceeds 86,400 s.
3. Count the drops by rule and window and report them in the run's data report. Dropping uses ts_event only; no
   feature or label reads it.
The rule closes the residual that guard33's check_records leaves open (no lower bound on ts_event): no record time-
stamped by the exchange inside the sealed window can enter a discovery feature.

## L.e The test span (M1 4.3 against M4 (a))

Trade dates 2017-05-22..2020-11-30 on ZL MBP-1, 890 dates, T_test 870 after the 20-date burn-in, the same span as E.32
P9 for ZM. M4's MBP-1 option from 2017-05-01 (905 dates, T_test 885) is not used: before 2017-05-21 the data are MDP 2,
"The `ts_recv` field on all MDP 2 data is set to the same value as `ts_event`" and "all records on MDP 2 data have the
`F_BAD_TS_RECV` flag set" (M1 4.3, from the saved Databento GLBX page), so the ts_recv clock and L.d rule 1 cannot be
applied the same way. The 15 trade dates 2017-05-01..2017-05-19 stay sealed and untested. Every threshold and power
figure uses T_test 870 (M4's MBO rows).

## L.f (session 3, 15:26 PDT): lead rulings after MathReview and ProtocolReview
- L.f.1 (MathReview S1): L.b's "the 20-entry hard cap of E.32 P3.8 stays as written (it never binds at h >= 15)" holds
  for FH15, FH30 and FH60 only (maxima 17, 8, 4). For TB15 and TB30 the trade count per date is realised (a barrier
  exit frees the account early) and the cap can bind; L.b's e80 table is for the FH labels. Protocol 0.5, P3.8, P7.2.
- L.f.2 (MathReview S2, ProtocolReview B2): one bad-book reading for features, labels, exclusions and fills: E.33
  reading FA-4 (feat33.stream_mbp1): an MBP-1 update is bad iff any record of its batch carries F_MAYBE_BAD_BOOK; the
  mark belongs to that update only (the code clears it at each F_LAST record). M3's F_LAST-record form (M3 c.4, (g)
  P3.0) is superseded. Labels come from ZL MBP-1 in both windows (M1 4.4, L.e), so M3 c.4's parity options reduce to
  (a) without an MBO purchase; parity by identical code. Book updates are F_LAST records of any action (F and R
  included), as E.33's code. Protocol 0.3, P3.2, P4 F10 header.
- L.f.3 (MathReview N13): K2 can bind for a configuration that passed G4 only if SR80_test at the realised T_test
  exceeds 0.2028, roughly T_test below 810 at N 1038 (870 x (0.1957/0.2028)^2). Protocol P10.2.
- L.f.4 (ProtocolReview B1): the test window's ZM ohlcv-1m bars are owned only for 2019-05..2020-11
  (reports/stage_e32_test_seal.md section 2). The data plan adds ZM.v.0 ohlcv-1m 2017-05-01..2019-04-30, bought with
  the test MBP-1 (estimate about USD 1.46: 24 x the median USD 0.0608 of 73 settled ZM ohlcv-1m months in the spend
  ledger). The BRIEFS RULES fact "test bars for ZL, ZS, ZM are owned" was wrong for ZM and is corrected there.
  Protocol P9.1, P9.2, P11.
- L.f.5 (MathReview N5): the overlap of the ts_recv - ts_event tail (DF34: 354 records above 1 s, 7 above a day) with
  the F_SNAPSHOT and F_BAD_TS_RECV flags is left to the run stage's drop report (each record counted under every rule
  it meets and once in the total); no protocol number depends on it, and E.34 makes no new count.
