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
