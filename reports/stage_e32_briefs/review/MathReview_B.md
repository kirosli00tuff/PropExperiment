# E.32 MathReview B: M1_order_flow.md and M3_labels.md

Reviewer: MathReviewer-FableXHigh (group B), independent adversarial review, 2026-10-27 (PDT). Brief:
reports/stage_e32_briefs/work/lead/brief_MathReviewer_B.md. I wrote nothing I review. No market data read, no
data/ path opened, no web fetch made (log.tsv in work_B/ is therefore absent), no reviewed file edited.

Method. Every worked-example number was recomputed from the standard ZM numbers with my own scripts before I
opened the readers' calculators: work_B/m1_recompute.py (.out) and work_B/m3_recompute.py (.out). Only after
that did I diff against work/M1_order_flow/M1_examples2.out and work/M3_labels/M3_calc.out (both agree with my
numbers to the printed precision; the single discrepancy is a rounding in M3's f.3 table, B-14). Every quoted
string in both files' evidence tables was checked against the saved pages by work_B/quote_check.py (.out:
exact normalised match for 94 of 127 segments; the 33 others (28 not matched exactly, 5 whose file column my
parser could not resolve) were re-grepped by hand with short substrings via work_B/g.py and all were found in
the named source, see the coverage list; the one quote that is a reconstruction of lost PDF layout is B-7). Equations were re-derived
or checked against the saved full text (equation numbers included). Program records were checked at
reports/stage_e28_ranking.md line 130, reports/stage_e28_briefs/A3_econ.md lines 54, 85-92 and 331,
reports/stage_e28_ranking_spec.md lines 114-124, reports/E.31_RETURN.md lines 177-191, and
reports/stage_e28_briefs/A0_contract_stats.md line 115.

Standard numbers used (READER_BRIEF.md lines 50-60): tick 10 USD; sigma_1m 3.15 ticks; fee 5.28 USD = 0.528
ticks; BE = mu*_mkt = 1.59 ticks (ranking line 130: `| 6 | topstep | ZM | 2.69 | 2 | 4 | 2 | 1 | 2 | 3 | 2.475
| 2.150 | 2.312 | 0.59 | 1.59 | 0.86 | 49.23 | 2.08 | ok |  |`); E.31 gross 10 s edges -0.970 (c), -0.287 (a),
-0.252 (b) (E.31_RETURN.md line 191); ADV 36,690; day share 0.83; day session 290 min; 816 trade dates.

Severity key (brief): BLOCKING changes a verdict or would mislead the frozen protocol; SHOULD FIX is a wrong
number or derivation that does not change a verdict, an unstated assumption, a quote not in the saved source, or
an [unverified] item carrying weight; NOTE is clarity or minor.

---

## Part 1: reports/stage_e32_briefs/M1_order_flow.md

### 1.0 Section 1 (common hurdle) and section 0

Recomputed (m1_recompute.out, "Section 1"): z_0.95 = 1.6449, phi = 0.10314, E[|Z| : |Z| > 1.6449] =
0.10314/0.05 = 2.0627, sqrt(2/pi) = 0.7979; sigma_h = 3.150, 7.044, 12.200, 17.253; R2 (trade every bar) =
0.4002, 0.0800, 0.0267, 0.0133; R2 (top decile) = 0.0599, 0.0120, 0.0040, 0.0020. All four rows of the table at
lines 44-49 match. Derivation check: for a calibrated normal forecast f with sd sqrt(R2) sigma_h, trading
sign(f) earns E|f| per trade, so E|f| = BE is the break-even; conditioning on the top decile multiplies by
2.0627/0.7979. Correct, with one unstated premise (B-9). The "falls as 1/h" statement is right (R2 needed is
proportional to 1/sigma_h^2). The CRS 1996 ratio 3.32/0.53 = 6.26 against 6.0 is right.

### 1.1 Topic (a) OFI (section 2)

Equations (2.2): XGH eqs. 2-5 and 9-12 (saved text lines 276, 377, 397), CKS eq. 1 (line 258-260: "∆P = OFI/2D
+ ε" with OFI = Lb − Cb − Ms − Ls + Cs + Mb), CKS eq. 3 (line 288), CCZ eq. 4 (line 351) and eq. 15 (line 1386)
are all present and numbered as cited. The sign table for DeltaV (ask side counts q1(tau_n) when a1 fell,
−q1(tau_{n−1}) when it rose) is the CKS e_n indicator form; correct. "DeltaP in ticks, D the depth per level"
is consistent with CKS's ⌈(L−C−M)/D⌉/2 construction (line 252): one depleted level on one side moves the mid
half a tick.

Worked examples (2.3): (i) 2D = 100, 30/100 = 0.30 tick: correct. (ii) rho^2 x 0.65 = 0.0016, 0.0065, 0.026:
correct. (iii) CRS Table 5 values 3.32/0.53 (1996) and 0.54/0.18 (2002) are in the saved text (lines 1501,
1527), the OIB# t-statistics quoted (2.24 and 2.00 at 30 min 1996; 0.50 at 30 min 2002) are in the table
(lines 1495-1497, 1521-1523), and "cross-sectional average adjusted R-square in percent" is the table note
(line 1554). Mapped numbers sd(f) 1.283/1.256/0.518/0.732, mean |f| 1.024/1.002/0.413/0.584, top decile
2.647/2.591/1.068/1.510: all match. (iv) 3.15^2 = 9.92 changes/min, 6.05 s each, 12.1 s for two: correct under
the stated unit-tick assumption. (v) CCZ Table 8 numbers match the saved table (line 1467) but see B-6 for what
the table's columns show.

Compute (2.6): 819 days, 1.64e9 messages, 2.7-5.5 min CPU, 67.8M rows, 1.36 GB at M = 5: correct.

Leakage traps (2.5): the six traps are real and each test would detect its trap. ts_event vs ts_recv, roll and
session joins, overlapping labels and future normalisers are all present. No omission found.

Verdict (2.7): MAYBE as features only. Follows from the arithmetic (R2_pred far below the hurdle) and the
sources. B-6 weakens one supporting sentence but not the verdict.

### 1.2 Topic (b) trade-sign long memory (section 3)

Equations: BGPW eq. 7 (line 626) and eq. 8 (line 638: "Ne ≃ 1 + Σ_{l=1}^{1000} C0(l) ≈ 1 + C0/(1−γ) 1000^{1−γ}")
as stated; alpha = 2 − 2H gives 0.6 for H = 0.7, matching Lillo-Farmer (line 16); the BFL asymmetric-liquidity
identities are the standard ones and the arithmetic below confirms them.

Worked examples: (i) closed form 1 + 0.25 x 251.19 = 63.80, exact sum 63.68 (m1_recompute.out B1); the paper's
"Ne ≈ 50" (line 641) is indeed loose; the reader says so. (ii) r+ = 0.40, r− = 0.60, 0.6 x 0.40 − 0.4 x 0.60 = 0:
correct. (iii) Patzelt-Bouchaud "pinned" quote present (found by quote_check).

Traps: real and testable (fill and mid change sharing a timestamp is the right one here). Verdict: SKIP as
signal, MAYBE as conditioner. Follows.

### 1.3 Topic (c) Kyle's lambda (section 4)

Equations: Hasbrouck eq. 4 (line 579) does carry the square-root sign over "(Signed Dollar Volume)", so "signed
square root of dollar volume" is right and the unit check sqrt(10,000) x 7e-6 = 7 bp is right (line 612).
ELOPZ bar form and "lookback window W" present (line 817). Patzelt-Bouchaud "κ = ξ − ψ ≈ 0.25" present (line 315).

Worked example: 36,690 x 0.83 = 30,453 over 290 min = 105.0/min; R2_c = 1.44/9.9225 = 0.1451; forward 0.00145;
slopes 0.01337/0.01016/0.00855 at 5/15/30 min; 30^-0.25 = 0.4273. All correct. (R2 = beta^2 Var(x)/Var(y) for a
univariate regression, as used.)

Traps: real; trap 3 (ELOPZ b_i from the bar's own price change makes it a volatility proxy) is a good catch.
Verdict MAYBE as conditioner: follows.

### 1.4 Topic (d) microprice (section 5)

Equations: slides lines 236-242 give toy model 2 "P_micro = M_t + I_t − 1/2" with S_t = 1; lines 399-412 give
g^1 = (1 − Q)^{-1} R^1 k and B = (1 − Q)^{-1} R^2 with a spectral decomposition for G*. The file's summary of G*
("sum of eigen-terms of B applied to g^1") is loose but matches the slides' procedure.

Worked example: I = 0.80, adjustment +0.30 tick, maximum 0.5 tick = 0.31 of BE. Correct in the toy. On the
brief's specific question (is the adjustment at most ±0.5 tick in a 1-tick-spread book): exact in toy model 2
(I in [0, 1]); in general it is the slides' empirical statement "Micro-price seems to live between the bid and
the ask" (line 493), not a theorem (B-5). The verdict is robust to this: even a 1-tick adjustment is below the
0.59 limit-order and 1.59 market-order break-evens.

Traps: both real (in-sample G* from one day; microprice as both feature and label end). Verdict: SKIP as
signal, USE in labels. Follows.

### 1.5 Topic (e) cancellation and replenishment (section 6)

Equations are the file's own definitions (declared as such). Worked example: 1 − e^{-3} = 0.9502,
1 − e^{-0.3} = 0.2592, ratio 3.67: correct. Xu et al. Type-1 (p > 1) and Type-2 (size greater than the best ask
but not walking the book, lines 200-201) are as described. Traps: four, real; trap 4 (book-rebuild artefacts at
the open) is an important one. Verdict MAYBE as one frozen conditioner: follows, and the file is candid that no
forward futures evidence exists.

### 1.6 Topic (f) icebergs and worked orders (section 7)

Equations: Zotikov-Antonov worked example "total volume of 43, 4 tranches with peak sizes 9, 9, 9 and 7" is in
the saved text (line 196); Bacry "duration factor in 1/T^γ with γ ≃ 0.25" (line 17); Frey-Sandas "fraction of
the iceberg order that is eventually executed" (line 113).

Worked example: sigma_day = 3.15 x 17.029 = 53.64; sqrt(120/36,690) = 0.05719, sqrt(40/36,690) = 0.03302,
difference x 53.64 = 1.30 ticks; 1,000-lot 8.86 ticks. Arithmetic correct; the sanity sentence is wrong (B-1)
and the inputs mix sessions (B-2).

Traps: three, real; trap 1 (ex-post "fraction executed") and trap 3 (survivorship from detection time) are the
decisive ones. Verdict MAYBE as absorption flag, SKIP as direction: follows.

### 1.7 Topic (g) VPIN (section 8)

Equations: ELO eq. 7 (line 712) is the bulk classification and eq. 9 (line 858) is VPIN, as cited. Worked
example: 36,690/50 = 733.8; 1,150/3,670 = 0.31335; Z(3/3.15) = Z(0.952) = 0.8295: correct. Traps: four, real;
trap 3 (volume-clock bucket closing after t) and trap 4 (volume-and-volatility benchmark) are the ones that
matter. Verdict SKIP for direction: follows (unsigned by construction).

### 1.8 Section 9 (families 5 and 7, grain OFI)

CORe numbers: Table 2 gives ZC "# days" 1,528 (line 1092), so 97/1528 x 819 = 52.0 and 29/1528 x 819 = 15.5 are
right; Table 3 "97 29 15 5 2" (line 1138) and Table 4 "97 −0.20 41.5% 76.3%" (line 1588), the 08:30-13:20
restriction (line 1097) and footnotes 23-24 (quotes found) are all present. Arithmetic: 15/7.044 = 2.13,
−0.20 x 15 = −3.0, 3.0 − 1.59 = 1.41, 1.59/0.20 = 7.95, 1.59/0.10 = 15.9, 3/sqrt(52) = 0.416, 13.6M kernel
evaluations: all correct. The look-ahead in CORe's event time (local extremum of the statistic) is real and the
proposed realizable-entry rule with future-scramble invariance would catch it; this is the most important trap
in the file and it is handled. Two issues with the sizing sentences: B-3 (power) and B-4 (illustration size).
Section 9.3's grain forward-OFI pointers are abstract-only and the file labels them so; they carry no verdict.

### 1.9 Findings table, M1_order_flow.md

| ID | file:line | Claim as written | What is wrong | Correct value or derivation | Severity |
|---|---|---|---|---|---|
| B-1 | M1_order_flow.md:537-538 | "the impact of a 1,000-lot metaorder by the same formula is 53.64 x 0.1651 = 8.86 ticks, i.e. a quarter of a typical day's 96-tick range" | 8.86/96 = 0.092; the stated fraction is wrong by a factor of about 2.7 | 8.86 ticks is under a tenth (9.2%) of the 96-tick median range; the "plausible order of magnitude" conclusion survives | SHOULD FIX |
| B-2 | M1_order_flow.md:532-535 | sigma_day = 3.15 x sqrt(290) (day session only) with V_day = 36,690 (all sessions) | The square-root law pairs a volatility and a volume over the same window; the day-session sigma is combined with the full-day ADV, which understates Q/V | With the day-session volume 36,690 x 0.83 = 30,453: sqrt(120/30,453) − sqrt(40/30,453) = 0.06277 − 0.03624 = 0.02653, x 53.64 = 1.42 ticks (still below 1.59); 1,000-lot 9.72 ticks. State the pairing or use it | NOTE |
| B-3 | M1_order_flow.md:667-668 | "Power: with 52 events, a t-statistic of 3.0 on the mean net post-move needs mean/sd >= 3/sqrt(52) = 0.416" | That is the realised-t condition, not a power statement; a test with 80% power at t = 3 needs a larger true effect, and the |T| > 4.5 subsample (15.5 events) needs far more | 80% power at t = 3: (3 + 0.8416)/sqrt(52) = 0.533; at 15.5 events: 3/sqrt(15.5) = 0.762 realised, 0.976 at 80% power. Relabel as "realised t" or give the power number; the verdict's sentence "statistical power ... is the binding constraint" is strengthened, not weakened | SHOULD FIX |
| B-4 | M1_order_flow.md:665 | "A pre-burst move of 15 ticks over 5 minutes (15/7.044 = 2.13 sigma_5m)" used as the burst example | A drift burst at |T| > 4.0 is, by construction, a drift of about 4 spot-volatility units over the bandwidth, i.e. of order 4 sigma_5m = 28 ticks under A1, not 2.1 sigma; the illustration is smaller than any event the detector would flag | The break-even pre-burst move 7.95 ticks (b = −0.20) is the useful number; a 28-tick burst implies −5.6 ticks expected post-move, net 4.0. Say that the 15-tick case is below the detection threshold | NOTE |
| B-5 | M1_order_flow.md:392-393, 416, 693, 744 | "The largest possible adjustment in this toy is +-0.5 tick"; verdict and summary table: "bounded at 0.5 tick in a 1-tick book" | Exact only in toy model 2 (I in [0,1]); in the general Markov model the bound is the slides' empirical observation (line 493: "seems to live between the bid and the ask"); only g^1, the first-change term, is bounded by half a tick in a 1-tick-spread book | Phrase as "bounded in the toy; empirically inside the spread in the slides' data"; verdict unchanged (even 1 tick is below 0.59 and 1.59) | NOTE |
| B-6 | M1_order_flow.md:135-139, 739 | "CCZ's only positive forward finding is that LAGGED CROSS-ASSET OFI helps: Table 8 ... -0.10 (with cross-asset OFI)"; verdict table: "cross-asset lags the only positive forward finding" | CCZ Table 8 (saved lines 1464-1467) has six columns: FPI[1] −0.37, FCI[1] −0.10, FPI^I −0.36, FCI^I −0.10, AR −0.36, CAR −0.10. The cross-asset lagged RETURNS model (CAR, no OFI) reaches the same −0.10, so Table 8 shows a cross-asset effect, not an OFI effect | Say "cross-asset lags (OFI or returns alike) are less negative out of sample; Table 8 does not separate OFI from returns". The MAYBE-as-feature verdict is unaffected; the reason column should not credit OFI specifically | SHOULD FIX |
| B-7 | M1_order_flow.md:196 | Quote "βi = c / ADi^λ + νi , (3)" marked "(as rendered)" | The saved text renders line 288 as "βi = + νi , (3)" (the fraction is lost in extraction); the quoted form is a reconstruction from the PDF, not the rendered text | Mark as "reconstructed from the PDF; the .txt loses the fraction" | NOTE |
| B-8 | M1_order_flow.md:393-394 | "Because P^micro is a martingale, the 5-minute and the 30-minute expected mid changes given this state are the same +0.30 tick" | The martingale property gives E[P^micro_{t+h}] = P^micro_t, not E[M_{t+h} − M_t] = adjustment for finite h; horizon independence of the MID change is the slides' empirical result at 60-600 s | "the slides find the mid-change averages at 60, 300 and 600 s all close to G*" | NOTE |
| B-9 | M1_order_flow.md:35-42 | Break-even from "mean traded abs f = BE" | Requires a calibrated forecast, E[r given f] = f (true for the linear-normal model in A2 but not stated); an uncalibrated forecast with the same R2 needs a scale fit first | Add "f calibrated" to A2 | NOTE |

M1 counts: BLOCKING 0, SHOULD FIX 3 (B-1, B-3, B-6), NOTE 6 (B-2, B-4, B-5, B-7, B-8, B-9).

### 1.10 Per-file verdict, M1_order_flow.md: SOUND WITH FIXES

Every equation checked is correct and numbered as in the saved sources; every worked-example number recomputes
(m1_recompute.out matches M1_examples2.out line for line); the verdicts follow from the arithmetic. The three
SHOULD FIX items are a wrong sanity fraction (B-1), a "power" sentence that is a realised-t sentence (B-3), and
one supporting claim stronger than CCZ Table 8 (B-6). None changes a verdict.

---

## Part 2: reports/stage_e32_briefs/M3_labels.md

### 2.0 Standing assumptions (lines 19-30)

A1 check: sqrt(8/pi) = 1.5958, x 3.15 x 17.029 = 85.6 ticks for the 290-minute session (m3_recompute.out "A1
check"); A0 line 115 gives the median daily range 96.0 and the zero-change share 0.18, as cited. Roll's model:
Var(trade-price change) = Var(mid change) + s^2/2, so a 1-tick spread adds 0.5 tick^2 = 5.0% of 9.92: correct.
BE and the session times are the standard numbers. One consequence of A1 not drawn (B-23): under A1 the
23-hour range would be 187 ticks against the observed 96, so sqrt(h) scaling across sessions is clearly broken,
which is why the to-close rows are the least reliable in the file (the file says "usable for sizing, not for
inference", which is the right qualifier).

### 2.1 Topic (a) bars and event-time sampling

Equations: tick, volume and dollar bar definitions are as in the saved mlfinpy text; the symmetric CUSUM is
exactly the saved code (mlfinpy_src_filters.py lines 76-86: s_pos = max(0, ...), s_neg = min(0, ...), "if s_neg <
-thresh ... elif s_pos > thresh", strict inequalities, one side reset); the first-passage bound (reflected walk
from 0 reaches H in mean H^2/sigma^2; from a start x in (H^2 − x^2)/sigma^2 <= H^2/sigma^2, so two racing sides
give a mean spacing at or below H^2/sigma^2) is correct.

Worked example: V = 733.8; 41.50 day bars at 6.99 min (6.72 at A0's mean 109.2/min; A0 line 115 gives 71 median,
109.2 mean); 8.50 overnight bars at 86 min (8.5/min) or 367 min (2/min); 290 + 765 one-minute rows; CUSUM toy
reproduced step by step (one event, at t8, S+ touches 6 at t5 without firing); spacing bounds 3.63/10.08/22.68
min. All correct (m3_recompute.out "a.3").

Traps: five, real and testable; trap 3 (sums carried across 13:20/07:45/roll) and trap 5 (E.31's unflagged
prints, quote present at E.31_RETURN.md section 3.5) are the ones most likely to bite. Verdicts follow.

### 2.2 Topic (b) fixed horizon vs triple barrier

Equations: R^exec for both sides is right (short sells at B_{t+L}, covers at A_{t+L+h}). First-passage facts:
P(up first) = 1/2; E[tau] = a^2/sigma^2; the alternating series for P(no exit by h) is the standard one and
evaluates to 0.3708 (kappa = 1) and 0.9090 (kappa = 2) in my script, matching the file. E[sqrt(290 − u)] =
(2/3) sqrt(290), 35.76 ticks, equivalent 128.9 min: correct (but see B-23 on what "equivalent" means).

Worked example: E[tau] = 1.61/2.52/3.63 min, 95% exit by 4.23/6.61/9.52 min (bisection on the series, mine
agrees to 0.01 min), p* = (k + 1.59)/(2k) = 0.699/0.659/0.6325 and the k = 5 check 0.659 x 3.41 − 0.341 x 6.59
= 0.000; kappa = 1 at h = 60: a = 24.40, p* = 0.5326; sigma_15 = 12.20 and 1/12.20 = 0.082; to-close 53.64 vs
14.09, ratio 3.807 = sqrt(14.5). All correct. The definition of the barrier price is however inconsistent with
the cost applied (B-13).

Traps: five, real; trap 2 (OHLC ties) and trap 4 (settlement price not tradeable) are well chosen. One trap
missing (B-29). Verdicts follow once B-13 is resolved; the "SKIP fixed +-4-6 ticks" reason (a 2-7-minute label)
holds under either reading of B-13.

### 2.3 Topic (c) meta-labeling

Equations: z_i on the executable return; precision threshold (k + BE)/(2k) is the same p* as b.3; correct. mlfinpy
lines 333 and 340 are as quoted (my grep: `out_df["ret"] = out_df["ret"] * events_["side"]  # meta-labeling`,
`out_df.loc[out_df["ret"] <= 0, "bin"] = 0`).

Worked example: k = 12.20, p* = 13.79/24.40 = 0.5652; spacing 144/9.9225 = 14.51 min, 20.0 events/day, 16,320
total, 3,264 accepted; net 0.58 x 10.61 − 0.42 x 13.79 = +0.362; se 0.00864, t = 1.71-1.72; total edge 1,182
ticks, 1.45/day; sd 12.04, SR 0.030. All correct except a rounding in the n-for-t=3 figure (B-15) and the
all-exits-on-barrier simplification (B-17). Verdict MAYBE: follows; the sample-size conclusion is the right one.

### 2.4 Topic (d) uniqueness weights (the 19.33)

Equations: the closed form sum_i u_i = (1/h) #{t : c_t > 0} is a correct derivation (swap the sums; each bar with
c_t > 0 contributes exactly 1 to sum_i 1_{t,i}/c_t). Time-decay formulas match mlfinpy_src_attribution.py as
quoted (slope and const rules).

Worked example (brief item 7): my direct computation on 276 labels over 290 bars gives c_max = 15, u = 0.2212
(first), 0.1590, 0.1301, 0.0667 (interior), H_15 = 3.3182, sum u = 19.3333 = 290/15, mean u = 0.0700, 816 x
19.333 = 15,776 and 276 x 816 = 225,216; time decay (0.5833, 0.6667, 0.8333, 1.0) and (0, 0.1111, 0.5556, 1.0).
All match. The 19.33 is confirmed. Compute figures 3.4e6, 7.6e11, 1.14e6, 9.3e8: correct.

Traps: four, real. Verdicts (n_eff mandatory, uniqueness weights, SKIP decay and sequential bootstrap) follow.

### 2.5 Topic (e) the cost floor and executable labels (brief item 7)

Decomposition of 1.59 (lines 482-493) checked against E.28: A3_econ.md line 331 gives for topstep x ZM F_rt 5.28
USD = 0.528 ticks, sigma_T 3.15, mu*_lim 0.59, mu*_mkt 1.59, cost/attempt 49.2, "ex-API mu*_lim 0.58"; section
2.1 (line 54) defines c_lim = F_rt/v and c_mkt = F_rt/v + S_rt; section 2.4 (line 92) states "with S_rt = 1 tick
for every pair, mu*_mkt = mu*_lim + 1.00 by construction". So 1.59 = 0.528 (fee) + 1.000 (default spread) +
0.062 (mu*_lim − c_lim = 0.59 − 0.528, the account-economics residual, of which 0.01 is the API subscription per
the ex-API figure and up to 0.01 the grid), slippage 0, sigma_T = sigma_1m (a one-minute holding scale, ranking
spec line 115), T = 20 trades a day. The file's decomposition and all three caveats are correct. ranking.md line
130 is quoted exactly.

E.31 numbers (e.3): the three columns satisfy E_10 = half-spread captured + 10 s markout (0.341 − 0.629 =
−0.288, 0.359 − 0.611 = −0.252, −0.425 − 0.545 = −0.970), which fixes the sign convention the file assumes (a
negative "captured" means the fill is worse than the mid at the fill). The 0.5 − 0.425 = 0.075 comparison is
therefore a correct reading; the point that a signal-conditioned passive fill is worse than the unconditional
number is right and matters.

Equations (e.4): R^exec − R^mid expansion is correct; latency sd 3.15 x sqrt(0.3/60) = 0.223 and sqrt(1/60) =
0.407; fractions 1/60 = 1.7%, 1/900 = 0.11%; Roll covariance −s^2/4 = −0.25 tick^2: correct.

Worked example (e.5): 2.0/12.20 = 0.164; 2.0 − 1.0 − 0.528 = 0.472, − 0.062 = 0.41 = 2.0 − 1.59; front-loaded
2.0 − 1.0 − 1.59 = −0.59; Phi(0.1252) − 0.5 = 0.0498 (my NormalDist 0.04985): correct; dead-zone constant
differs from f.2 (B-18). The brief's "mid labels about 1 tick optimistic per round trip" is confirmed: the
spread term (s_entry + s_exit)/2 = 1 tick at 1-tick spreads, 1.528 with the fee, 1.59 with the residual.

Traps: four, real; trap 2's unit test (−(1 + 0.528) for a round trip with no mid move) is exactly right.
Verdict USE executable labels: follows.

### 2.6 Topic (f) cost-aware target and the per-horizon table (brief item 7)

Equations: N_long + N_short = −(s_{t+L} + s_{t+L+h}) − 2c_x < 0 (so the classes are exclusive): correct. q* =
1/2 + BE/(2 E|DeltaM_h|) from E[net] = (2q − 1)E|DeltaM| − BE under magnitude-sign independence: correct.
E|DeltaM| = 0.7979 sigma_h: correct. Barrier q* = (k + BE)/(2k) and SR_trade = ((2p − 1)k − BE)/(2k sqrt(p(1 −
p))): correct.

Per-horizon table recomputed (m3_recompute.out "f.3 table"): sigma_h 3.150/7.044/12.200/17.253/24.400/34.507/
48.800/53.643, E|DeltaM| 2.513/5.620/9.734/13.766/19.468/27.532/38.936/42.801, q* 0.8163/0.6415/0.5817/0.5578/
0.5408/0.5289/0.5204/0.5186, q*(1.528) 0.804/0.636/0.579/0.556/0.539/0.528/0.520/0.518, barriers +-sigma
0.752/0.613/0.565/0.546/0.533/0.523/0.516/0.515, +-2 sigma 0.626/0.556/0.533/0.523/0.516/0.512/0.508/0.507,
n 236,640/47,328/15,504/7,344/3,264/1,632/816/816, t at q* 307.7/61.5/20.3/9.9/4.7/2.3/1.2/1.1, q for t = 3
0.819/0.648/0.594/0.575/0.567/0.566/0.573/0.571; uniform-entry row 35.762/28.534/0.044/0.528/0.527/0.522/0.511.
Every cell matches the file except q* at h = 5 (B-14). The brief's hit rates 0.816/0.642/0.582/0.541/0.520/0.519
are therefore confirmed as 0.8163/0.6415/0.5817/0.5408/0.5204/0.5186 (the 5-minute value rounds to 0.641).
Items 1-5 after the table: dead zone 0.179/0.104/0.052 with Phi(0.2257) = 0.5893; +-5 barrier at p = 0.68 mean
0.21, sd 4.665, SR 0.045; the h = 60 hand check 0.5408, se 0.00875, t 4.66, 0.5671. All correct. The "t = 3"
column is a realised-t threshold, not a power figure (B-27); the trade counts ignore the g.3 cuts (B-16).

Traps: five, real; trap 5 (DeepLOB's smoothed label contains the past: saved lines 251-253 confirm m− is "the
mean of the previous k mid-prices") is a genuine leak and the test given would detect it. Verdict USE (dead-zone
label, EV rule) with 60-120 min as the provable band: follows from the table; the 240-min and to-close
statements ("profitable but not provable") follow.

### 2.7 Topic (g) sampling exclusions

Sources: CBOT 2015 filing line 90 ("1:14-1:15 p.m. CT settlement window") and line 78 (8:30 a.m. - 1:20 p.m.),
Submission 25-045 line 141 ("CME Globex Pre-Open:"), R4_events.md line 27 (settlement VWAP) and line 42 (WASDE
11:00 CT), E.31 exclusion precedent and post-USDA bucket (quotes found), log.tsv line 15 (cftc robots): all
present. The futures pre-open inference is labelled [unverified] and carries no verdict: acceptable.

Worked example: 290 − 5 − 7 = 278 allowed minutes; 278 − 15 + 1 = 264 starts; 48 excluded (10:43-11:30
inclusive); 216 kept; blocks 143 and 103 minutes; n_eff 16.40 vs 18.53; ratios 0.818 and 0.885; 15 x 2.13 = 32
of 4,633 (0.69%). All correct (the file's 4,625 uses 18.5 rounded). Boundary convention (B-22).

Traps: four, real (calendar-only W, rescheduled releases, roll from volume crossover, asymmetric exclusions).
Verdict USE all eight rules: follows.

### 2.8 Cross-file consistency (group B)

BE = 1.59 in both files (M1 line 21, M3 line 28), both quoting ranking line 130 column mu*_mkt; sigma_h
identical (3.150/7.044/12.200/17.253/24.400); M1 states the hurdle as an R2 (forecast model), M3 as a hit rate
(sign model), and M3 lines 685-688 say so explicitly and correctly (R2 needed falls as 1/h, excess hit rate as
1/sqrt(h)); M1's 2.3(iv) and M3's A1 both rest on the same unit-step/random-walk assumption and both state it.
No contradiction found. Both files use 816 dates; M3 notes E.31's 764 usable day dates, M1 uses 819 (39 months
at 252/yr) for the compute and burst counts; the two are different quantities (calendar vs owned) and do not
conflict, but a frozen protocol should pick one (NOTE, folded into B-16).

### 2.9 Findings table, M3_labels.md

| ID | file:line | Claim as written | What is wrong | Correct value or derivation | Severity |
|---|---|---|---|---|---|
| B-13 | M3_labels.md:187-193 (b.2) against 214-216 (b.3), 295-297 (c.2), 642 (f.2) | b.2: "for event i with entry price P_i (the executable entry) ... Upper barrier P_i + a_i, lower P_i − a_i ... Barrier tests are on the executable exit price (the bid for a long, the ask for a short)"; b.3/c.2/f.2: "win k − 1.59, loss −(k + 1.59), so p* = (k + 1.59)/(2k)" | Under b.2's definition an upper-barrier hit for a long means bid_exit >= ask_entry + k, so the k ticks are already net of the spread; charging BE = 1.59 (which contains the 1-tick spread) on top double-counts the spread by 1.0 tick. The b.3/c.3/f.2/f.3 numbers are right for barriers measured on the MID around the mid at entry | Either (i) barriers on the mid, cost BE = 1.59: p* = 0.699/0.659/0.6325 (as written), or (ii) barriers on executable prices, cost c_x = 0.59 (fee + residual): p* = (k + 0.59)/(2k) = 0.574/0.559/0.549 at k = 4/5/6 and 0.5121 at k = 24.40. The protocol must state which; every mixed reading errs conservative, so no verdict changes, but the label definition the freeze inherits is ambiguous | SHOULD FIX |
| B-14 | M3_labels.md:659 | q* fixed horizon at h = 5: "0.642" | 1.59/(2 x 5.6199) = 0.14146, q* = 0.64146, which rounds to 0.641; M3_calc.out prints 0.6415 | 0.641 | NOTE |
| B-15 | M3_labels.md:314 | "needs n = 0.2436 x (3 / 0.0148)^2 = 0.2436 x 41,088 = 10,009 accepted trades" | Rounding the margin to 0.0148 before squaring; with 0.58 − 0.56516 = 0.014836 the count is 9,961 | about 10,000 (9,961 unrounded); conclusion unchanged | NOTE |
| B-16 | M3_labels.md:645, 653, 656-665, 690-692 | "n = 816 x floor(290 / h)" and the table's trade counts; "to close, entry 08:30 (h = 290)" | The g.3 rules the same file adopts allow only 278 day minutes (08:35-13:13) and E.31 kept 764 dates, so the counts are 764 x floor(278/h): h = 15: 13,752 (not 15,504), h = 60: 3,056, h = 5: 42,020; and an 08:30 entry is inside the 5-minute open exclusion, so the to-close row is h = 278 (sigma 52.5, q* 0.5190). The file notes the 6% date effect but not the minute cut | t at q* becomes 19.1 (h = 15), 4.5 (h = 60); q for t = 3 0.5945 and 0.5679. Direction: slightly more conservative; the 60-120 min conclusion stands | NOTE |
| B-17 | M3_labels.md:303-317 | c.3 nets every accepted trade at +-k (k = 12.20) | b.2 says 37% of kappa = 1 labels end on the vertical barrier under A1, with outcomes inside (−k, k); the net, sd and SR are upper-bound illustrations | State "treating every exit as a barrier exit"; the sample-size conclusion is unchanged (it gets slightly worse with the vertical-barrier outcomes) | NOTE |
| B-18 | M3_labels.md:563-564 against 631-632 | e.5: dead zone 0 < R^mid <= 1.528 ("Phi(1.528/12.20) − 0.5 = 0.0498"); f.2: "the dead zone ... about |M_{t+L+h} − M_{t+L}| <= 1.59 ticks" | Two different constants for the same quantity (with and without the 0.062 residual) | Pick one: with 1.59 the share is Phi(0.1303) − 0.5 = 0.0518 (10.4% both signs, as f.3 item 4 already uses) | NOTE |
| B-22 | M3_labels.md:803-804, 765-767 | "a start t is excluded if [t, t + 15] meets [10:58, 11:30]: t from 10:43 to 11:30, 48 minutes (10:43 + 15 = 10:58 touches the window)" | Whether a label ending at 10:58:00 "intersects" a window starting at 10:58 is a closed/half-open interval convention; the count is 47 or 48 depending on it, and the same strictness point the file makes for CUSUM (line 92-93) applies | Declare half-open minute intervals [t, t + h) and W = [release − 2, release + D_rel) in the protocol; then 47 excluded starts, 217 kept | NOTE |
| B-23 | M3_labels.md:201-204, 666 | "the typical to-close label has sd (2/3) x 3.15 x 17.029 = 35.76 ticks, the same as a fixed 128.9-minute label" | 35.76 is the entry-time average of the sd; the pooled variance over uniform entries is sigma_1m^2 x E[290 − u] = 9.9225 x 145, rms sd 37.9 ticks, equivalent h = 145 min. Also A1's own check (85.6 vs 96 for the session; 187 vs 96 for 23 h) shows sqrt(h) is weakest exactly at these horizons | Say "mean sd 35.8 (equivalent 129 min); rms sd 37.9 (equivalent 145 min)"; the q* difference is 0.528 vs 0.526, immaterial | NOTE |
| B-27 | M3_labels.md:644-647, 656 (last column), 671-675 | "needs q* + 3 x 0.5/sqrt(n) to show net skill above break-even at t = 3"; column "q needed for net skill at t = 3"; "can be shown at t = 3" | This is the observed hit rate at which the realised t equals 3, not the true hit rate at which a t = 3 test has a stated power; a pre-registered power claim needs the latter (M5b's domain) | At 80% power: q* + (3 + 0.8416) x 0.5/sqrt(n): h = 60: 0.5745 (not 0.5671); h = 120: 0.5764; h = 15: 0.5971. Relabel the column "observed hit rate giving t = 3" or add the power column; the 60-120 min band is the same either way | SHOULD FIX |
| B-29 | M3_labels.md:190-192, 233-245 | sigma_hat_i "an EWMA of 1-minute mid changes over the previous 60 day-session minutes" | A trap not listed: for the first hour after 08:30 the previous 60 day-session minutes are yesterday's 12:20-13:20 (or, if the window is clock-based, the overnight/pre-open), so barriers in the opening hour are scaled by the wrong regime; the file's g.3 rule 1 removes only 5 minutes | Add a trap: "sigma_hat at session start; test: tabulate sigma_hat by minute-of-day and assert the opening-hour value is from the declared source"; or declare a day-of-week/minute-of-day volatility profile | NOTE |

M3 counts: BLOCKING 0, SHOULD FIX 2 (B-13, B-27), NOTE 8 (B-14, B-15, B-16, B-17, B-18, B-22, B-23, B-29).
(IDs B-10 to B-12, B-19 to B-21, B-24 to B-26 and B-28 were used in my working notes for items that checked out
and are listed in section 3 as verified; they are not findings.)

### 2.10 Per-file verdict, M3_labels.md: SOUND WITH FIXES

The break-even decomposition, the per-horizon hit-rate table, the 19.33 effective labels, the 1-tick mid-label
bias and every other worked number recompute exactly (m3_recompute.out agrees with M3_calc.out; the only
numeric slip is a third-decimal rounding, B-14). The equations are right and the leakage traps are real and
testable. The two SHOULD FIX items are a label-definition ambiguity between b.2 and the break-even arithmetic
(B-13: executable-price barriers plus a spread-inclusive BE double-count the spread; all readings err
conservative) and a "t = 3" column that is a realised-t threshold presented as a detectability requirement
(B-27). Neither changes a verdict.

---

## Part 3: coverage, everything checked and found correct

### 3.1 M1_order_flow.md (verified items)

Equations (12): CKS eq. 1 and the e_n indicator form; CKS eq. 3 numbering; XGH eqs. 2-5, 9-12 numbering and
content; CCZ eq. 4 (first principal vector, l1-normalised) and eq. 15 (lag set L, horizons f); E.28 2.9 s7.2
identity R2_pred = rho^2 R2_c; BGPW eq. 7 and eq. 8 (closed form confirmed against the saved rendering);
alpha = 2 − 2H; BFL asymmetric-liquidity identities (checked by the worked arithmetic); Hasbrouck eq. 4 (signed
square root confirmed in the saved text); ELOPZ bar-level lambda with b_i on bars and lookback W; ELO eqs. 7
(bulk classification) and 9 (VPIN); Stoikov toy model 2 and the discrete g^1, B formulas; CORe eqs. 35-36
reversal regression and the left-sided exponential kernel.

Worked-example numbers (all recomputed, all match; m1_recompute.out): section 1 table (8 cells plus the
constants 1.6449, 0.10314, 2.0627, 0.7979); 2.3 (i) 100 and 0.30; (ii) 0.0016/0.0065/0.026; (iii) 12 mapped
cells and the ratios 6.26 and 6.15; (iv) 9.92, 6.05 s, 12.1 s; 2.6 819 days, 1.64e9, 2.7-5.5 min, 67.8M, 1.36
GB; 3.3 (i) 63.80 and 63.68; (ii) 0.40, 0.60, 0.6, 0.4, 0; 4.3 30,453, 105.0, 0.145, 0.0015, 0.0134/0.0102/0.0086,
0.4273, 7 bp; 5.3 0.80, +0.30, 0.31; 6.3 0.950, 0.259, factor 3.7; 7.3 53.64, 0.05719, 0.03302, 1.30, 8.86
(the fraction of the range is B-1); 8.3 733.8, 0.31335, 0.8295; 9.1 52.0, 15.5, 2.13, −3.0, 1.41, 7.95, 15.9,
0.416, 7.21, 13.6M.

Quotes checked against saved pages (all found; file names as in the evidence tables): CKS "average R2 of 65%",
"autocorrelations at a timescale of 10 seconds are small and quickly vanish", eq. 1 line (line 260); XGH
"contemporaneous change in mid-price", "65–75% for large-tick stocks"; CCZ "first principal vector computed
from historical data", "over 89% of the total variance", Table 8 row (line 1467), "decays rapidly in time",
horizons and lags; CRS "In no more than thirty minutes", Table 5 R2 rows (lines 1501, 1527), "feasible only for
the specialist", t-statistics 2.24/2.00/0.50, adjusted-R2 note (line 1554), 150 stocks (line 359); KTW abstract
"approximately two average price changes", "significantly outperform" (IDEAS page); Lillo-Farmer alpha 0.6, H
0.7, "returns whiter"; BGPW gamma 1/5 and 2/3, "Ne ≈ 50 !" (line 641); BFL "asymmetric liquidity", "deviations
from strict unpredictability at high frequencies"; Patzelt-Bouchaud "pinned", "κ = ξ − ψ ≈ 0.25" (line 315);
Hasbrouck "5-minute intervals ... each month" (line 582), "seven basis points" (line 612); ELOPZ b_i and W,
"six important outcomes" (line 132), "low predictive power, and vice versa", "VPIN is the most important
predictor for five variables"; Stoikov slides "lim Pti", "Mt + It − 1/2" (lines 240-242), "horizon independent"
(line 492), "between the bid and the ask" (line 493), "first day or March" (line 439); Stoikov 2018 abstract
(IDEAS); Xu et al. "within 20 best limit updates", "resiliency ... aggressive", "Type-1 ... p greater than 1",
Type-2 definition (lines 200-201); Bechler-Ludkovski "replenished less than usual", "one-sided flows",
"concurrent trade imbalance", R2 0.4 to 0.7; Ma-Serra "75% and 79%" and "price discovery" (IDEAS);
Zotikov-Antonov order-ID preservation, synthetic icebergs, one week of ES, "43 ... 9, 9, 9 and 7" (line 196);
Frey-Sandas "eventually executed" (line 113), "more likely to attract market orders"; Bacry exponents 0.5-0.8,
"does not anticipate the size", "duration factor ... γ ≃ 0.25" (line 17); ELO eq. 7 sentence, "one-fiftieth",
"entire sample period"; Andersen-Bondarenko 2014 abstract and 2013 reply quotes; Joulin two quotes;
Marcaccioli two quotes; CORe "once a week on average", sample period (line 1096), ZC 08:30-13:20 (line 1097),
Table 2 "# days 1,528" (line 1092), Table 3 row (line 1138), Table 4 row (line 1588), eqs. 35-36, footnotes 23
and 24; Volkenand and Jin abstracts (IDEAS). The one quote that is a reconstruction rather than the rendered
text is CKS eq. 3 (B-7). Count (quote_check.out): 78 quote segments in M1's evidence tables, 63 matched exactly
by script, 15 verified by hand, of which 1 is a reconstruction (B-7).

Program-record citations: ranking line 130 mu*_mkt 1.59 (verified); A0 Table 1 numbers (verified); E.31
−0.970 (verified).

Leakage traps: 2.5 (6), 3.5 (3), 4.5 (3), 5.5 (2), 6.5 (4), 7.5 (3), 8.5 (4), 9.1 (1): 26 traps, all real,
each with a test that detects it; no omission found beyond those the file already covers.

Verdicts: 10 rows of section 10; each follows from the evidence shown, with the reason wording of the OFI row
qualified by B-6 and the microprice row by B-5.

### 3.2 M3_labels.md (verified items)

Equations (14): tick/volume/dollar bar closes; imbalance-bar rule as in mlfinpy (AFML form marked
[unverified] by the file, which is correct practice); symmetric CUSUM (exactly the saved code lines 76-86);
reflected-walk spacing bound; R^exec both sides; volatility-scaled barrier a_i = kappa sigma_hat sqrt(h);
first-passage P(up) = 1/2, E[tau] = a^2/sigma^2, the alternating exit series (0.3708, 0.9090 reproduced);
to-close E[sqrt(290 − u)] = (2/3) sqrt(290); meta-label z_i and precision threshold; uniqueness closed form
n_eff = covered bars/h; time-decay slope/const rules (as in mlfinpy_src_attribution.py lines 164-167); R^exec −
R^mid expansion; latency sd sigma_1m sqrt(L/60); Roll covariance −s^2/4 and variance +s^2/2; three-class label
exclusivity; q* = 1/2 + BE/(2 E|DeltaM|); barrier q* and SR_trade; detectability se = 0.5/sqrt(n).

Worked-example numbers (all recomputed, all match except B-14; m3_recompute.out): A1 check 1.5958, 85.6, 5%;
a.3 733.8, 41.5, 7.0, 6.7, 8.5, 86, 367, 50.0, 290/765; CUSUM toy (12 steps, one event at t8); spacings
3.63/10.08/22.7; b.2 0.3708/0.9090, 35.76, 128.9; b.3 1.61/2.52/3.63, 4.23/6.61/9.52, 0.699/0.659/0.6325, the
k = 5 zero check, 24.40, 0.5326, 37%, 12.20, 0.082, 53.64, 14.09, 3.807, 3.808; b.6 236,640; c.3 12.20,
0.5652, 14.5, 20, 16,320, 3,264, 0.362, 0.00864, 1.71, (10,009 vs 9,961: B-15), 1,182, 1.45, 12.04, 0.030; d.3
276, 15, 0.0667, 0.2212, 0.1590, 0.1301, 3.3182, 19.33, 0.0700, 225,216, 15,776, both decay rows; d.6 3.4e6,
7.6e11, 1.14e6, 9.3e8; e.2 0.528, 1.000, 0.062, 1.528, 0.59 − 0.528; e.3 0.075, 48.5%; e.4 0.223, 0.407, 1.7%,
0.11%, −0.25; e.5 0.164, 0.472, 0.41, −0.59, −0.39, 0.0498, 5%/10%; f.3 all 9 rows x 10 columns (89 cells
match, 1 rounding), items 1-5 (0.179/0.104/0.052, 0.5893, 0.21, 4.665, 0.045), the h = 60 hand check; g.4 278,
264, 48, 216, 143, 103, 16.4, 18.5, 0.818, 0.886, 32, 0.69%.

Quotes checked against saved pages and program records (all found): LdP 2018 "oversample information",
"subordinated process", "corporate actions", "regardless of the observed volatility", "dynamic function of
estimated volatility", "number of bars elapsed", "pre-defined constant threshold", "predict the accuracy of the
primary model's prediction", "significantly increase the average uniqueness"; Easley et al. 2012 "partial
recovery of Normality", "1/50 of the average daily volume"; Murphy-Izzeldin "not normally distributed"; Fayyaz
et al. "No systematic relationship" (line 2304), "All AUC values lie in" (line 2282) with "0.48–0.60
(near-chance)" (line 2283), "near-chance (0.50–0.60)" (line 2755); mlfinpy filters code (lines 81-86),
Filtering.rst "hovering" (line 29), FinancialDataStructure "closer to normal", labeling.py line 72 and lines
333/340, Sampling.rst concurrency and sequential-bootstrap sentences, attribution.py docstring and formula
lines; Lucchese et al. "not tradable in practice"; DeepLOB "no order can transact exactly at the mid-price",
"stationary (0)" (line 283), "redundant trading actions thus incurring larger transaction costs" (lines
294-295), "previous k mid-prices" (line 253); E.28 ranking line 130 (exact), ranking spec lines 118-119,
A3_econ.json "default 1 (u): no sourced median" (line 739) and "per side = RT/2" (line 13990); E.31 E_10 row,
"5.5% of aggressor prints", "fills 0-5 minutes after a USDA release -8.98 (68 fills)", "52 of 816 dates",
"384 s, 4 workers" (line 177), "764 DAY dates" (line 27); DECISIONS.md V50 item 2 (line 1038); CBOT 2015 filing
lines 78 and 90; Submission 25-045 line 141; R4_events.md lines 27 and 42; M3 log.tsv line 15. Count
(quote_check.out): 49 quote segments in M3's evidence tables, 31 matched exactly by script, 18 verified by hand,
all found. The latency 300-1,000 ms row is marked [unverified] and the file treats it as a
stress range, not a fact: acceptable.

Leakage traps: a.5 (5), b.5 (5), c.5 (4), d.5 (4), e.7 (4), f.5 (5), g.6 (4): 31 traps, all real with
detecting tests; one addition proposed (B-29).

Verdicts: 14 rows of the summary table; each follows from the arithmetic shown, subject to B-13's clarification
for the two barrier rows.

### 3.3 Brief item 7 (the seven named checks)

1. Break-even decomposition 1.59 = 0.528 + 1.0 + 0.062, slippage 0, 1-minute hold, T = 20: CONFIRMED against
   A3_econ.md lines 54, 85-92, 331 and ranking spec lines 114-124.
2. Hit rates per horizon under sigma_h = 3.15 sqrt(h) and symmetric magnitudes: CONFIRMED as
   0.8163/0.6415/0.5817/0.5408/0.5204/0.5186; the file's 0.642 at 5 min should read 0.641 (B-14).
3. 19.33 effective labels per session (15-minute labels every minute): CONFIRMED (direct sum 19.3333 = 290/15).
4. Mid labels about 1 tick optimistic per round trip: CONFIRMED (half-spread at entry plus half at exit = 1.0
   tick at 1-tick spreads; 1.528 with the fee; 1.59 with the residual).
5. Microprice adjustment at most +-0.5 tick in a 1-tick-spread book: CONFIRMED for toy model 2; in general an
   empirical statement in the slides (B-5); the SKIP verdict does not depend on the bound being exact.
6. Cross-file consistency (break-even, sigma_h, hit rate vs R2 framing): CONSISTENT (section 2.8).
7. Calculators: both readers' scripts reproduce my independent numbers (no hidden input differences found).

### 3.4 Totals

| File | BLOCKING | SHOULD FIX | NOTE | Verdict |
|---|---|---|---|---|
| M1_order_flow.md | 0 | 3 (B-1, B-3, B-6) | 6 (B-2, B-4, B-5, B-7, B-8, B-9) | sound with fixes |
| M3_labels.md | 0 | 2 (B-13, B-27) | 8 (B-14, B-15, B-16, B-17, B-18, B-22, B-23, B-29) | sound with fixes |
| Total | 0 | 5 | 14 | |

### 3.5 Not checked, and why

- AFML (the book) and Ane-Geman 2000: not on disk; the files mark them [unverified] and nothing rests on them.
- KTW 2023, Stoikov 2018 (journal), Ma-Serra 2025, Jin et al. 2023, Volkenand et al. 2018: abstract-only in the
  evidence pages; the files label them so and no verdict rests on them (checked that this is true).
- E.28's break-even simulator was not rerun at other (T, sigma_T); M3 e.2 caveat 3 is a correct statement that
  the 0.062 residual is not transferable across horizons, but its size at h = 60 is unknown to me as to the file.
- CORe's T-statistic normalisation (used in B-4 only as an order-of-magnitude argument) was not re-derived from
  their eqs.; B-4 is a NOTE for that reason.
- No web fetch was made, so no site terms were read and work_B/log.tsv was not created.
- Timing claims (E.31's 384 s, M3's "minutes") were checked for citation only, not re-measured.

Scripts and outputs: work_B/m1_recompute.py (.out), work_B/m3_recompute.py (.out), work_B/quote_check.py (.out),
work_B/g.py. None reads market data.

