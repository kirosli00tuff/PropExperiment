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
