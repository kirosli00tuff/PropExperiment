# E.32 Part M1: order-flow measures for FORWARD directional prediction in ZM (1 s to 30 min)

Worker: OrderFlowMath-OpusHigh (re-spawned run; the first run fetched the evidence pages at 23:05-23:13 PDT on
2026-10-26 but wrote no output). Written 2026-10-27 from 00:23 PDT. ROOT = M1_order_flow.
Evidence pages and log: reports/stage_e32_briefs/pages/M1_order_flow/ (log.tsv). Arithmetic:
reports/stage_e32_briefs/work/M1_order_flow/M1_examples2.py, output M1_examples2.out (every number in a worked
example below is printed there). M1_examples.py / .out from the first run are SUPERSEDED: its Chordia-Roll-
Subrahmanyam R-squared inputs did not match the paper's Table 5 and are corrected here (section 2.3).

Scope rules followed: no market data read, no statistic derived from data, nothing registered, N stays 538.
Every equation or claim from a source carries a quote and the saved file; [unverified] marks abstract-only or
snippet-only knowledge. E.28 sections cited as "E.28 2.x" (reports/stage_e28_methods_brief.md); I read only the
line ranges my brief names (2.9 sections 7 and 9, 4.6; 2.3 section 5 headings and 5.1/5.7/5.8) and do not repeat
them.

## 0. What is new here relative to E.28, in one paragraph

E.28 2.9 treated order flow as a sub-second, passive-execution problem and concluded that "as an execution aid ...
much of the signal survives 100 ms; as a standalone alpha, almost none does". This part asks the different
question E.32 needs: what order-flow measures can say about the ZM mid-price 1 to 30 MINUTES ahead, where a
taker's round trip costs about 1.59 ticks at Topstep (E.28 ranking row 130, column mu*_mkt = 1.59). The answer
from the sources read: (1) every measure in this part is far stronger contemporaneously than forward; (2) the
forward part decays to statistical insignificance by 5 to 30 minutes in the best-documented case (Chordia, Roll and
Subrahmanyam 2005, NYSE) and to "approximately two average price changes" for deep-learned order-flow forecasts
(Kolm, Turiel and Westray 2023, abstract), which is about 12 seconds in ZM under a stated assumption; (3) trade-sign
persistence is by construction offset by asymmetric liquidity, so it predicts flow, not price; (4) the one
minutes-scale order-flow-adjacent effect with a large published forward R-squared in a CBOT grain is the
post-drift-burst reversal (Christensen, Oomen and Renò: ZC corn, 97 events, b = -0.20, R2 = 41.5%), and its event
time is defined at a local extremum of the test statistic, a look-ahead that a frozen protocol must remove before
trusting the number. Order-flow measures therefore enter a ZM directional search as conditioners and as event
detectors (planner families 5 and 7), not as standalone forecasts.

## 1. The common hurdle at minutes horizons (extends E.28 2.9 section 7.4 from MES to ZM)

Assumptions, stated: (A1) ZM mid changes follow a random walk across minutes, so sigma_h = sigma_1m x sqrt(h)
with sigma_1m = 3.15 ticks (A0 Table 1); (A2) a forecast f of the h-minute mid change is normal with
sd(f) = sqrt(R2) x sigma_h, R2 being its out-of-sample R-squared; (A3) the taker hurdle is BE = 1.59 ticks per
round trip (E.28 ranking row 130, mu*_mkt). For a normal forecast, E|f| = sd(f) x sqrt(2/pi), sqrt(2/pi) =
0.7979. If only the top decile of |f| is traded, the mean |f| traded is sd(f) x E[|Z| : |Z| > 1.6449] =
sd(f) x phi(1.6449)/0.05 = sd(f) x 0.10314/0.05 = sd(f) x 2.0627. Setting the mean traded |f| equal to BE and
solving gives the out-of-sample R2 a forecast needs merely to break even on average (gross of slippage beyond
the E.28 cost model):

| h (min) | sigma_h = 3.15 x sqrt(h) (ticks) | R2 needed, trade every bar = (1.59/(sigma_h x 0.7979))^2 | R2 needed, top decile only = (1.59/(sigma_h x 2.0627))^2 |
|---|---|---|---|
| 1 | 3.150 | 0.400 | 0.0599 |
| 5 | 7.044 | 0.0800 | 0.0120 |
| 15 | 12.200 | 0.0267 | 0.0040 |
| 30 | 17.253 | 0.0133 | 0.0020 |

Check (h = 5): 3.15 x 2.2361 = 7.044; 7.044 x 2.0627 = 14.53; (1.59/14.53)^2 = 0.01197. Matches.
Reading: a forecast at 1 minute needs an out-of-sample R2 near 6% even when it trades only its top decile; at 30
minutes 0.2% suffices. The "R2 needed" falls as 1/h. In the one source read that reports forward order-imbalance
R2 at 5 to 60 minutes (CRS 2005 Table 5, section 2.3), R2 also falls roughly as 1/h (1996: 3.32% at 5 minutes,
0.53% at 30, a factor 6.3 against 6.0 for 1/h), but the imbalance coefficient itself loses significance by 30
minutes, so the 30-minute R2 is mostly the lagged return and noise. Longer horizons therefore do not rescue an
unconditional order-flow forecast; the only route left is conditioned subsets (events, extremes), which is what
planner families 5 and 7 propose.

## 2. (a) Order-flow imbalance: best-level, multi-level, integrated, deep; contemporaneous versus forward

E.28 2.9 sections 1-4 give the definitions, the MES worked examples and the sub-second evidence; section 7 gives
the identity R2_pred = rho^2 x R2_c under a linear model; section 9 gives the latency decay. Below: only what a
1 s to 30 min forward search adds.

### 2.1 Core idea

OFI adds up, over a window, the net change in the best bid queue minus the net change in the best ask queue
(arrivals add, cancels and market orders subtract, a price-level shift books the whole new or lost queue). It
explains about 65% of the variance of mid changes in the SAME window (Cont, Kukanov and Stoikov), because the events
that move the mid are the events counted. Its forward value comes only from the persistence of order flow, which
is small and decays fast; at minutes horizons the published forward R2 is near zero or negative out of sample,
and what survives is cross-asset and short-lived (Cont, Cucuringu and Zhang 2023).

### 2.2 Equations (source equation numbers where the full text shows them)

- Event contribution (Xu, Gould and Howison, eqs. 2-4; same as CKS): for the n-th book event,
  e_n = DeltaW(tau_n) - DeltaV(tau_n), where DeltaW = r1(tau_n) if the best bid price b1 rose, r1(tau_n) -
  r1(tau_{n-1}) if unchanged, -r1(tau_{n-1}) if it fell; DeltaV is the mirror image for the ask queue q1 at price
  a1 (q1(tau_n) if a1 FELL, q1(tau_n) - q1(tau_{n-1}) if unchanged, -q1(tau_{n-1}) if it rose). r1, q1 are best bid
  and ask sizes in contracts; tau_n event times.
- Window OFI (XGH eq. 5): OFI(t_{k-1}, t_k) = sum of e_n over events in (t_{k-1}, t_k].
- Order-level identity (CKS, text above eq. 1): OFI = L^b - C^b - M^s - L^s + C^s + M^b, with L limit-order
  arrivals, C cancels, M market orders at the best quotes (b bid side, s/a ask side), in contracts.
- Stylized impact (CKS eq. 1): DeltaP = OFI/(2D) + epsilon, D the (equal) depth per level in contracts, DeltaP in
  ticks; regression form (CKS eq. 2): DeltaP_k = beta OFI_k + epsilon_k; depth link (CKS eq. 3):
  beta_i = c / AD_i^lambda + nu_i, AD_i the average best-queue size over the half-hour window i.
- Multi-level OFI (XGH eqs. 9-12): the same e^m computed at the m-th occupied level, m = 1..M, giving the vector
  MLOFI(t_{k-1}, t_k) = (MLOFI^1, ..., MLOFI^M); XGH fit DeltaP on it with OLS and Ridge.
- Integrated OFI (Cont, Cucuringu and Zhang, eq. 4): ofi^I_{i,t} = w1' ofi^(h)_{i,t} / ||w1||_1, w1 the first
  principal vector of the multi-level OFI vector, "computed from historical data".
- Forward model with cross-asset lags (CCZ eq. 15, "FCI^I"): r_{i,t+f} = alpha_i + sum_j sum_{k in L}
  beta_{i,j}^{I,k} ofi^{I,(kh)}_{j,t} + eta, L = {1,2,3,5,10,20,30} minutes of lagged OFI, f the forecast
  horizon in minutes, re-estimated on the previous 30 minutes and rolled forward each minute.
- Linear forward bound (E.28 2.9 section 7.2): R2_pred = rho^2 R2_c, rho the lag-1 autocorrelation of window OFI.

### 2.3 Worked example on ZM

(i) Stylized impact. Assume (illustrative, no data read) a ZM depth of D = 50 contracts at each best quote.
By CKS eq. 1 one tick of mid move needs OFI = 2D = 100 contracts; an OFI of +30 contracts gives
DeltaP = 30/(2 x 50) = 0.30 tick, contemporaneously. Check: 0.30 x 100 = 30.

(ii) What is left forward. With R2_c = 0.65 (CKS average) and a lag-1 OFI autocorrelation rho of 0.05, 0.1 or
0.2 (assumptions bracketing CKS's "small" 10-second autocorrelations), R2_pred = 0.0016, 0.0065, 0.026
(M1_examples2.out A3). Against section 1, at 1 minute even rho = 0.2 (R2 = 0.026) is below the 0.060 needed for
top-decile trading; at 5 minutes it exceeds the 0.012 top-decile need, but CKS's own statement is that OFI
autocorrelations at 10 s "are small and quickly vanish", so rho at 5-minute aggregation is not expected to be 0.2.

(iii) The one published forward-R2 table at 5-60 minutes (CRS 2005 Table 5, NYSE 150 largest stocks, regression
of the next interval's midpoint return on the lagged midpoint return and lagged trade-count imbalance OIB#;
R2 is the cross-sectional average adjusted R2 in percent). Mapped onto ZM under A1 and A2 (an assumption: that
ZM would show the same R2), sd(f) = sqrt(R2) x sigma_h:

| CRS cell | R2 | sigma_h ZM (ticks) | sd(f) | mean abs f | top-decile mean abs f | vs BE 1.59 |
|---|---|---|---|---|---|---|
| 1996, 5 min | 0.0332 | 7.044 | 1.283 | 1.024 | 2.647 | top decile clears |
| 1996, 30 min | 0.0053 | 17.253 | 1.256 | 1.002 | 2.591 | top decile clears, but OIB# coefficient weak (avg t 2.24, cross-sectional t 2.00) |
| 2002, 5 min | 0.0054 | 7.044 | 0.518 | 0.413 | 1.068 | does not clear |
| 2002, 30 min | 0.0018 | 17.253 | 0.732 | 0.584 | 1.510 | does not clear; OIB# not significant (avg t 0.50) |

Check (2002, 5 min): sqrt(0.0054) = 0.0735; x 7.044 = 0.518; x 2.0627 = 1.068. The decisive fact is the time trend:
between 1996 and 2002 the 5-minute R2 fell from 3.32% to 0.54% (a factor of 6) as markets automated, and CRS add
that the rule was feasible "only for the specialist and perhaps sophisticated floor traders" who could see the
imbalance. In ZM every participant sees the aggressor side in real time, so the starting point is the 2002 row or
below, which does not clear the hurdle.

(iv) Forward horizon of deep order-flow forecasts. Kolm, Turiel and Westray (abstract): "the effective horizon of
stock specific forecasts is approximately two average price changes". Assume ZM mid changes are +-1 tick steps of
a random walk (an assumption; half-tick moves through a 2-tick spread and bid-ask bounce break it). Then the
number of mid changes per minute is about sigma_1m^2 / (1 tick)^2 = 3.15^2 = 9.92, one change every 60/9.92 =
6.05 s, and two average price changes take about 12 s. Check: 9.92 changes x 6.05 s = 60.0 s. So the
deep-learned order-flow edge, if it transfers, lives at about 12 seconds in ZM: inside E.31's measured passive
10-second window (gross -0.970 ticks per fill) and below the 1-minute floor of this search.

(v) Cross-asset lags. CCZ's only positive forward finding is that LAGGED CROSS-ASSET OFI helps: Table 8
out-of-sample R2 for one-minute-ahead returns is -0.37 (own best-level OFI), -0.36 (own integrated OFI) and
-0.10 (with cross-asset OFI), all negative, and "this lagged cross-impact mainly manifests at short-term
horizons and decays rapidly in time". The ZM analogue is lagged ZS and ZL best-level OFI (computable from the
owned MBP-1) as features for the ZM 1-5 minute label; planner family 6 already caps this at "a feature only".
[MathReview B-6 (lead: accepted): CCZ Table 8 (saved lines 1464-1467) has six columns, FPI[1] −0.37, FCI[1] −0.10, FPI^I −0.36, FCI^I −0.10, AR −0.36, CAR −0.10, and the cross-asset lagged RETURNS model (CAR, no OFI) reaches the same −0.10; read "cross-asset lags (OFI or returns alike) are less negative out of sample; Table 8 does not separate OFI from returns". The MAYBE-as-feature verdict is unaffected; the verdict-table reason column (original line 739) should not credit OFI specifically.]

### 2.4 Data it needs (owned schemas) and horizon

- Best-level OFI: ZM MBO (book rebuilt to level 1) or the level-1 quote and size changes; ZS and ZL MBP-1 give
  exactly the inputs of XGH eqs. 2-5 (best price and size after each event). Aggregate on a 1-second grid, then
  sum to 1, 5, 15, 30 minutes.
- MLOFI and integrated OFI: ZM only (needs levels 2..M, available only by rebuilding the book from MBO; ZS and ZL
  have no depth beyond level 1). The order-level identity (L, C, M separately) is also ZM-only; MBP-1 gives only
  the net queue changes.
- Use ts_recv (receive time) as the knowledge time for every feature; definitions file for tick size and the
  v.0/v.1 roll map.

### 2.5 Leakage and look-ahead traps, each with a test

1. Contemporaneous overlap: a label window that starts before the feature window ends inherits R2_c (65%). Test:
   assert label_start >= feature_end + delay (delay frozen, e.g. 1 s) in code; and a canary: shift the label back
   by one bar; if the out-of-sample R2 jumps by an order of magnitude, the production alignment is right and the
   canary shows what leakage would look like (log both).
2. Normalizers from the future: OFI divided by depth AD_i (CKS eq. 3 uses the window's own average) or by a
   daily volatility. Test: future-scramble invariance, i.e. replace all data after time t with noise and assert
   every feature at t is bit-identical.
3. Integrated-OFI weights w1 fitted on the full sample (CCZ eq. 4 requires "historical data"). Test: fit w1 inside
   each training fold only; the future-scramble test above also catches it.
4. ts_event versus ts_recv: exchange timestamps precede the time the data could be acted on. Test: recompute
   features with ts_recv + 50 ms; a forward R2 that collapses means the edge was latency (E.28 2.9 section 9).
5. Roll and session joins: OFI summed across the v.0 roll or across the 13:20 close to 19:00 reopen gap. Test:
   assert no feature or label window spans a roll date in the roll blackout or a session gap longer than the
   label horizon.
6. Overlapping labels (5-30 minute labels on a 1-minute grid): purged and embargoed CV per V43. Test: assert
   train/test index sets are separated by at least the label horizon plus the feature lookback.

### 2.6 Compute (ThinkPad, 39 months)

One streaming pass over ZM MBO per day rebuilds the book and writes per-second OFI vectors (levels 1..M). The
message count is a DataFacts item; at an ASSUMED 2 million ZM messages per day and about 819 trading days
(39 months at 252 days a year) the pass touches about 1.6 billion messages; a compiled (numba or Rust) book
builder at an assumed 5-10 million messages per second needs 3-6 minutes of CPU plus I/O, in day-sized chunks,
single-threaded per day, at most 8 days in parallel under the default limits; memory is per-day (well under 1 GB).
ZS/ZL MBP-1 OFI is cheaper (no book rebuild). The per-second output is about 819 x 23 h x 3600 s x M floats, about
68 million rows x M; at M = 5 float32 that is about 1.4 GB on disk, so store per-day parquet.

### 2.7 Verdict for a minutes-scale directional ZM search under V43

MAYBE, as features only: best-level OFI of ZM, ZS and ZL lagged 1-30 minutes and ZM integrated OFI enter the
frozen feature set as conditioners; no OFI-only model is a separate configuration (each would add to N with
published forward R2 below the section-1 hurdle). SKIP deep order-flow models (horizon about 12 s in ZM by 2.3 iv)
and SKIP MLOFI as a separate block (contemporaneous gains only; XGH's improvement is "goodness-of-fit" of the
contemporaneous relation).

### 2.8 Evidence table (a)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| OFI explains same-window mid changes with R2 about 65% | Cont, Kukanov and Stoikov (2014), arXiv 1011.6402v3 | "with an average R2 of 65%" | cks_2014_price_impact_order_book_events.txt |
| Stylized impact equation | CKS eq. 1 | "OF I = Lb − C b − M s − Ls + C s + M b and  is the truncation error" (around "∆P = OFI/2D + ε, (1)") | same |
| OFI autocorrelations vanish fast | CKS | "In our data the autocorrelations at a timescale of 10 seconds are small and quickly vanish as well" | same |
| Depth link | CKS eq. 3 | "βi = c / ADi^λ + νi , (3)" (as rendered) | same |
| MLOFI is a contemporaneous fit | Xu, Gould and Howison (arXiv 1907.06230) | "a simple, linear relationship between MLOFI and the contemporaneous change in mid-price" | xu_gould_howison_2018_mlofi.txt |
| MLOFI gain is out-of-sample goodness of fit, large-tick 65-75% | XGH | "improves the goodness-of-fit of the MLOFI regressions for all of the stocks in our sample, with an improvement of about 65–75% for large-tick stocks" | same |
| Integrated OFI: first PC, l1-normalized, from historical data | Cont, Cucuringu and Zhang (arXiv 2112.13213) eq. 4 | "where w 1 is the first principal vector computed from historical data" | ccz_2023_cross_impact_ofi.txt |
| First PC explains most multi-level OFI variance | CCZ | "the first principal component can explain over 89% of the total variance among multi-level OFIs" | same |
| Forward: own OFI out-of-sample R2 negative at 1 min; cross-asset less negative | CCZ Table 8 | "OS R2 -0.37 -0.10 -0.36 -0.10 -0.36 -0.10" | same |
| Forward cross-impact decays fast | CCZ abstract | "this lagged cross-impact mainly manifests at short-term horizons and decays rapidly in time" | same |
| CCZ horizons and lags | CCZ section 4.2 | "including f ∈ {2, 3, 5, 10, 20, 30} minutes" and "L = {1, 2, 3, 5, 10, 20, 30} represents the set of lags" | same |
| Forward imbalance predictability lost by 30 minutes | Chordia, Roll and Subrahmanyam (2005 JFE; 2004 working paper) | "In no more than thirty minutes, order imbalances lose their predictive ability and returns are no longer negatively dependent." | crs_2005_speed_of_convergence_wp.txt |
| Forward R2 values, OIB# regressions | CRS Table 5 | 1996 row: "R2 3.32 1.59 1.42 0.94 1.02 0.78 0.53 0.43 0.52 0.43"; 2002 row: "R2 0.54 0.32 0.35 0.30 0.28 0.93 0.18 0.16 0.17 0.15" (pairs = OIB# then OIB$ at 5, 10, 15, 30, 60 min) | same |
| Only insiders could trade it | CRS | "A trading rule based on the short-period results in Table 5 is therefore feasible only for the specialist and perhaps sophisticated floor traders." | same |
| Deep order-flow forecast horizon | Kolm, Turiel and Westray (2023), Mathematical Finance 33(4) | "the effective horizon of stock specific forecasts is approximately two average price changes" [abstract only, IDEAS page; full text not read: Wiley terms forbid automated access, see section 11] | ideas_ktw_2023.html(.txt) |
| Order flow beats raw book as model input | KTW abstract | "models trained on order flow significantly outperform most models trained directly on order books" [abstract only] | same |

## 3. (b) Trade-sign imbalance and its long memory: why sign persistence does not predict price

### 3.1 Core idea

The signs of market orders (buy +1, sell -1) are strongly autocorrelated with a slowly decaying power law,
because large orders are split (Lillo and Farmer 2004; Bouchaud, Gefen, Potters and Wyart 2004). The NEXT trade's
sign is therefore predictable, yet returns are close to uncorrelated: liquidity providers who see the same
persistence make the expected move of the predicted (likely) trade small and of the surprising trade large, so
the expected mid change is zero ("asymmetric liquidity", Bouchaud, Farmer and Lillo 2009). Predicting flow is not
predicting price; at minutes scale extreme sign imbalance even coincides with a PINNED price (Patzelt and
Bouchaud).

### 3.2 Equations

- Sign autocorrelation (BGPW eq. 7): C0(l) = <eps_{n+l} eps_n> ~= C0 / l^gamma (l >= 1), eps_n the sign of trade
  n, l the lag in trades, 0 < gamma < 1 ("for FT, one finds γ ≈ 1/5, whereas for Total γ ≈ 2/3").
- Effective number of correlated trades out of 1000 (BGPW eq. 8): N_e ~= 1 + sum_{l=1}^{1000} C0(l) ~= 1 +
  C0/(1-gamma) x 1000^(1-gamma).
- Lillo and Farmer (abstract): on the LSE the sign autocorrelation "decays roughly as τ^−α with α ≈ 0.6,
  corresponding to a Hurst exponent H ≈ 0.7" (alpha plays the role of BGPW's gamma; alpha = 2 - 2H).
- Asymmetric liquidity (BFL 2009 eqs. 6.21-6.24): r_n = m_{n+1} - m_n = eta_n + theta (eps_n - eps_hat_n),
  eps_hat_n = E_n[eps_{n+1} | I] the liquidity providers' sign predictor, theta the impact per unit surprise.
  Efficiency E_{n-1}[r_n | I] = 0 implies phi+_n r+_n - phi-_n r-_n = 0 (eq. 6.22) with r+ = theta (1 - eps_hat),
  r- = theta (1 + eps_hat) (eqs. 6.23-6.24); phi+ (phi-) the probability that the trade matches (opposes) the
  predictor.
- Aggregate sign impact (Patzelt and Bouchaud eqs. 2-5, 9): R_N(Q) = <log m_{t+N} - log m_t | Q>, Q the signed
  volume over N trades; R_N(Q) ~= R_N F(Q/Q_N), Q_N ~ N^xi, R_N ~ N^psi; same for the sign imbalance E.

### 3.3 Worked example

(i) BGPW eq. 8 on their FT numbers (C0 = 0.2, gamma = 0.2, l up to 1000): closed form 1 + 0.2/0.8 x 1000^0.8 =
1 + 0.25 x 251.19 = 63.8; the exact sum 1 + sum 0.2 l^-0.2 = 63.68 (M1_examples2.out B1). The paper's text says
"a factor Ne ≈ 50": the order of magnitude agrees, the paper's rounding is loose (63.7, not 50). Its point
stands: if each trade had a permanent fixed impact, sign memory would amplify impact about 50-60 times between
lag 1 and lag 1000, which is not observed; the impact must therefore be transient or history dependent.

(ii) Asymmetric liquidity, ZM-sized. Assume a ZM sign predictor eps_hat = 0.2 (the next market order is a buy with
probability (1 + 0.2)/2 = 0.6) and theta = 0.5 tick (illustrative). Then r+ = 0.5 x (1 - 0.2) = 0.40 tick when the
trade matches, r- = 0.5 x (1 + 0.2) = 0.60 tick when it does not; phi+ = 0.6, phi- = 0.4. Expected mid change =
0.6 x 0.40 - 0.4 x 0.60 = 0.24 - 0.24 = 0 ticks. Check: a correct 60/40 call on flow earns nothing on price. Any
directional edge from sign imbalance must come from a liquidity provider who UNDER-predicts the persistence
(slow information set), which in an electronic CBOT book with visible aggressor flags is not the base case.

(iii) Minutes scale. Patzelt and Bouchaud: "extreme order flow imbalance is not associated with large returns. To
the contrary, it is observed when the price is 'pinned' to a particular level." A 30-minute ZM window in which 85%
of trades are buys is, on this evidence, more likely a passive seller (an iceberg or a worked offer, section 7)
absorbing flow at one price than the start of a move.

### 3.4 Data (owned)

ZM MBO trade events (action T or F with aggressor side) give eps_n exactly; ZS and ZL MBP-1 carry trade events
with side. No Lee-Ready inference is needed. Horizons: sign imbalance over the last 100-1000 trades or 1-30 min.

### 3.5 Leakage traps and tests

1. Counting the trade that defines the label's first mid change in the feature (fill and mid change share a
   timestamp). Test: assert every trade in the feature has ts_recv strictly before the label's start mid.
2. Implied (spread-leg) trades and the trade-summary versus per-fill records double counting volume. Test: count
   per-match volume twice (summary and fills) on a known day and assert one equals the other (DataFacts owns the
   schema detail).
3. Using the full-day sign autocorrelation fit (C0, gamma) as a feature normalizer. Test: future-scramble invariance
   (section 2.5 test 2).

### 3.6 Compute

Trivial next to the book rebuild: one counter per trade.

### 3.7 Verdict

SKIP as a standalone directional predictor: the mechanism (3.3 ii) and the evidence (3.3 iii) both say sign
persistence is priced. MAYBE as a conditioner inside families 5 and 7: a large one-sided sign imbalance with NO
price move flags absorption (a refilling passive order, section 7), which conditions a breakout or reversal
label; a sign imbalance WITH a burst-sized move is the drift-burst state of section 9.

### 3.8 Evidence table (b)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Order signs are long-memory; future signs predictable | Lillo and Farmer (2004), arXiv cond-mat/0311053 | "The autocorrelation function decays roughly as τ −α with α ≈ 0.6, corresponding to a Hurst exponent H ≈ 0.7. This implies that the signs of future orders are quite predictable from the signs of past orders" | lillo_farmer_2004_long_memory.txt |
| Market stays efficient via liquidity and size fluctuations | Lillo and Farmer | "fluctuations in order signs are compensated for by anti-correlated fluctuations in transaction size and liquidity, which are also long-memory processes. This tends to make the returns whiter." | same |
| Power-law sign correlation, stock-dependent gamma | BGPW (2004), arXiv cond-mat/0307332, eq. 7 | "For example, for FT, one finds γ ≈ 1/5, whereas for Total γ ≈ 2/3." | bouchaud_gefen_potters_wyart_2004.txt |
| Amplification puzzle | BGPW eq. 8 | "For FT, γ ≈ 1/5 and C0 ≈ 0.2, which means that the effect of one trade should be amplified, through the correlations, by a factor Ne ≈ 50 !" | same |
| Asymmetric liquidity | Bouchaud, Farmer and Lillo (2009), arXiv 0809.0822, section 6.5.1 | "This result shows that the most likely outcome has the smallest impact. We call this mechanism asymmetric liquidity" | bouchaud_farmer_lillo_2009_digest.txt |
| Small deviations at high frequency only | BFL 6.5.1 | "This is a plausible first approximation, although one can expect (and indeed observes) deviations from strict unpredictability at high frequencies." | same |
| Extreme imbalance means pinned price | Patzelt and Bouchaud (arXiv 1706.04163) | "extreme order flow imbalance is not associated with large returns. To the contrary, it is observed when the price is “pinned” to a particular level." | patzelt_bouchaud_2018_aggregate_impact.txt |

## 4. (c) Kyle's lambda at minute horizons (Hasbrouck-style regressions)

### 4.1 Core idea

Kyle's lambda is the slope of the price change on signed order flow over the same interval: a liquidity (price
impact) STATE, contemporaneous by construction. For forward direction it can only scale or condition another
signal (a high-lambda state makes a given flow move the price more; a low-lambda state is where absorption,
section 3.3 iii, happens). Its estimated slope also shrinks with the aggregation window (Patzelt and Bouchaud),
so lambda at 1 minute and at 30 minutes are different numbers, and a frozen protocol must fix one.

### 4.2 Equations

- Hasbrouck (2009 JF) eq. 4: Delta p_it = lambda_i x S_it + epsilon_it, where S_it is the SIGNED SQUARE ROOT of
  dollar volume over 5-minute interval t ("price changes and signed volume aggregated over 5-minute intervals. A
  separate estimate is computed for each month"); Delta p the log price change.
- Easley, Lopez de Prado, O'Hara and Zhang (2019 NBER version) bar form: lambda_tau = (p_tau - p_{tau-W}) /
  sum_{i=tau-W}^{tau} b_i V_i, b_i = sign(p_i - p_{i-1}) on bars, V_i bar volume, W the lookback.
- Aggregation scaling (Patzelt and Bouchaud, text after eqs. 3-6): the slope of the linear part of aggregate
  impact, dR_N/dQ at Q = 0 = R_N/Q_N, "scales as N^-κ with κ = ξ − ψ ≈ 0.25", N the number of trades in the window.

### 4.3 Worked example

Assume (illustrative, no data read) a ZM 1-minute lambda of 0.02 tick per contract of signed volume and a 1-minute
signed-volume standard deviation of 60 contracts (for scale: day-session volume 36,690 x 0.83 = 30,453 contracts
over the 290-minute session = 105 contracts per minute on average, M1_examples2.out C1).
- Contemporaneous R2 = (lambda x sd(Q))^2 / sigma_1m^2 = (0.02 x 60)^2 / 3.15^2 = 1.44 / 9.9225 = 0.145.
- Forward, with a lag-1 signed-volume autocorrelation of 0.1 (assumption): 0.01 x 0.145 = 0.0015, far below the
  0.060 needed at 1 minute for top-decile trading (section 1).
- Window scaling: if trades per window are proportional to minutes (assumption), the slope at h minutes is
  0.02 x h^-0.25: 0.0134 at 5, 0.0102 at 15, 0.0086 at 30 ticks per contract. Check: 30^-0.25 = 1/2.340 = 0.4273;
  0.02 x 0.4273 = 0.00855.
- Hasbrouck's unit check: median lambda about 7 x 10^-6 per sqrt(dollar); a 10,000-dollar order moves log price
  by sqrt(10,000) x 7 x 10^-6 = 100 x 7 x 10^-6 = 0.0007 = 7 bp, matching the paper's text.

### 4.4 Data (owned)

ZM MBO trades with aggressor side (signed volume) and mid; ZS/ZL MBP-1 the same at level 1. Rolling estimate over
a trailing window (for example the last 60 one-minute bars), fixed in the protocol.

### 4.5 Leakage traps and tests

1. Estimating lambda over a window that overlaps the label (the slope then "knows" the label's move). Test: assert
   the estimation window ends at or before feature time t.
2. Using a full-month lambda (Hasbrouck's monthly estimate) as a feature for days within that month. Test:
   future-scramble invariance.
3. The ELOPZ bar form takes b_i from the bar's price change, so on the bar that contains a burst the "signed
   volume" is the price change's sign: it is a volatility proxy. Test: report its correlation with |return| over
   the same window; above about 0.5 (a frozen threshold) it is treated as a volatility feature, not a flow one.

### 4.6 Compute

A rolling OLS per bar; seconds over 39 months.

### 4.7 Verdict

MAYBE as a conditioner (liquidity state, in the feature set at one frozen window); SKIP as a direction source.
ELOPZ, the one 87-futures study that uses Kyle's lambda in out-of-sample prediction, predicts the sign of changes
in spread, realized volatility and higher moments a week ahead, not the sign of returns, and finds "some of
these microstructure features with apparent high explanatory power can exhibit low predictive power".

### 4.8 Evidence table (c)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Hasbrouck price-impact regression, 5-min, monthly | Hasbrouck (2009 JF), author copy | "The specification is estimated using price changes and signed volume aggregated over 5-minute intervals. A separate estimate is computed for each month." | hasbrouck_2009_jf_gibbs.txt |
| Unit check | Hasbrouck | "a $10,000 buy order would move the log price by 10,000 × 7 × 10−6 = 0.0007, that is, seven basis points" (the square-root sign is lost in the PDF text; the arithmetic requires sqrt(10,000)) | same |
| Bar-level Kyle lambda | Easley, Lopez de Prado, O'Hara, Zhang (NBER conference version 2019) | "where 𝑏𝑖 = sign[𝑝𝑖 − 𝑝𝑖−1 ], which is computed on bar level, and 𝑊 is the lookback window size." | elopz_2019_microstructure_machine_age_nber.txt |
| Their labels are not return direction | ELOPZ | "We focus on predicting six important outcomes of market price dynamics using a one-week forecast horizon: the sign of change of the bid-ask spread; sign of change in realized volatility; ..." | same |
| Explanatory is not predictive | ELOPZ abstract | "some of these microstructure features with apparent high explanatory power can exhibit low predictive power, and vice versa" | same |
| Impact slope falls with window size | Patzelt and Bouchaud | "It scales as N −κ with κ = ξ − ψ ≈ 0.25, i.e. it decreases with N as a power-law" | patzelt_bouchaud_2018_aggregate_impact.txt |

## 5. (d) The microprice for a large-tick, 1-tick-spread book

E.28 2.3 section 5 covers the definition, the Markov computation and the evidence (from the same Gatheral60
slides, saved again here as stoikov_gatheral60_microprice_slides.pdf). Added here: what the microprice can and
cannot do 1-30 minutes ahead in ZM.

### 5.1 Core idea

The microprice is the expected mid-price "in the distant future" given today's imbalance and spread, and it is a
martingale, so it is horizon independent: the expected mid change from now to any later time is the same bounded
adjustment, which in a 1-tick-spread book lies between the bid and the ask. It is therefore a better fair-value
estimate (for labels and entry prices), not a source of minutes-scale drift.

### 5.2 Equations (slides)

- Imbalance I_t = Q^b/(Q^b + Q^a), spread S_t, mid M_t; P^micro_t = lim_i P^i_t, P^i_t = E[M_{tau_i} | F_t], tau_i
  the successive times the mid changes.
- Main result: P^i_t = M_t + sum_{k=1}^{i} g^k(I_t, S_t), g^1(I, S) = E[M_{tau_1} - M_t | I, S], g^{i+1} =
  E[g^i(I_{tau_1}, S_{tau_1}) | I, S]; discrete version g^1 = (1 - Q)^{-1} R^1 k, B = (1 - Q)^{-1} R^2,
  G* = P^micro - M = sum_{i>=2} (eigen-terms of B) g^1.
- Toy model 2 (Brownian imbalance, spread 1): P^micro_t = M_t + I_t - 1/2.

### 5.3 Worked example (ZM, 1-tick spread)

Take a ZM book with Q^b = 40 and Q^a = 10 contracts at a 1-tick spread (illustrative). I = 40/50 = 0.80. Toy model 2
gives an adjustment of 0.80 - 0.50 = +0.30 tick. The largest possible adjustment in this toy is +-0.5 tick (I -> 1
or 0), which is 0.5/1.59 = 0.31 of the taker hurdle. Because P^micro is a martingale, the 5-minute and the
30-minute expected mid changes given this state are the same +0.30 tick. Check: the slides list "Micro-price is
horizon independent" and "Micro-price seems to live between the bid and the ask".

### 5.4 Data (owned)

ZM, ZS, ZL best bid and ask sizes from MBP-1 (ZS, ZL) or the rebuilt level 1 (ZM); the transition matrices Q, R1,
R2 are estimated per training fold on a fixed (imbalance bucket, spread) grid.

### 5.5 Leakage traps and tests

1. The slides' validation fitted G* "obtained from the first day of March" and compared it with averages over the
   whole month including that day. Test: fit the transition matrices only on training folds; future-scramble
   invariance on the fitted G*.
2. Using the microprice as a label's END price while it is also a feature: the label then contains the feature.
   Test: the label uses the mid (or microprice) at t+h only, the feature only at t, assert disjoint timestamps.

### 5.6 Compute

A 10-30 state matrix inversion per fold; trivial.

### 5.7 Verdict

SKIP as a directional signal at 1-30 minutes (bounded at 0.5 tick, below 1.59). USE as the price inside labels and
entry marks (replace the mid at t and t+h by the microprice to remove the bid-ask bounce noise from a 1-5 minute
label), which is a design choice, not a trial; whether it counts toward N is the lead's call.

### 5.8 Evidence table (d)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Definition as the limit of expected future mids | Stoikov, Gatheral60 slides | "Ptmicro = lim Pti ... where the approximating sequence of martingale prices is given by Pti = E [Mτi |Ft ]" (as rendered) | stoikov_gatheral60_microprice_slides.txt |
| Toy model with 1-tick spread | slides | "The spread St = 1 then ... Ptmicro = Mt + It − 1/2" (as rendered across lines) | same |
| Horizon independence, bounded | slides, Summary | "6 Micro-price is horizon independent" and "7 Micro-price seems to live between the bid and the ask" | same |
| Validation horizons and calibration day | slides | "Compute averages of Mt+60 − Mt , Mt+300 − Mt and Mt+600 − Mt grouped by It and St for the entire month of March. Compare to G ∗ obtained from the first day or March." | same |
| Published claim | Stoikov (2018) QF abstract | "The micro-price estimated using high-frequency data is empirically a better predictor of short-term prices than the mid-price or the weighted mid-price" [abstract only, IDEAS] | ideas_stoikov_2018.html(.txt) |

## 6. (e) Cancellation and replenishment rates; resiliency after a liquidity shock

E.28 2.2 (Hawkes) gives the arrival-intensity machinery (kernels, branching ratio, MLE); E.28 2.3 gives the queue
models. Added here: resiliency as a forward CONDITIONER after a sweep, at seconds-to-minutes scale.

### 6.1 Core idea

After a market order empties the best queue (a "sweep"), the book refills. How fast and on which side it refills
says whether the shock was absorbed (fast same-side refill: reversion) or is part of one-sided pressure (slow
refill on the side being hit: continuation). Xu et al. (2016, Chinese stocks) find price resiliency after the most
aggressive (book-walking) market orders and price continuation after less aggressive ones; Bechler and Ludkovski
(2017, Nasdaq large-tick, minutes-scale volume buckets) find the side under pressure is replenished LESS than usual.
Both measure the shock and the response in the same window; no source read measures the 1-30 minute forward
return conditional on the refill rate in futures (a gap, not a finding).

### 6.2 Equations (definitions for the protocol; the papers use these concepts, not these exact formulas)

- Sweep event at time t0 on the ask: a buy market order with penetrability p >= 1 (Xu et al.: Type-1 walks the
  book, p > 1; Type-2 empties the best level, p = 1).
- Refill ratio after Delta seconds: R(Delta) = [Q^a_1(t0 + Delta) - Q^a_1(t0+)] / [Q^a_1(t0-) - Q^a_1(t0+)], Q^a_1
  the depth at the pre-sweep best ask price (0 when that level was emptied), t0- just before, t0+ just after.
- Side-specific net limit flow over a window (Bechler and Ludkovski's V^{L,A}, V^{L,B}): additions minus
  cancellations at the touch on each side, in contracts.
- Cancellation ratio: cancels / adds at the touch over the window (order level, MBO only).
- Exponential-refill toy (an ASSUMPTION used only for the worked example): R(Delta) = 1 - exp(-Delta/tau), tau the
  refill time constant.

### 6.3 Worked example

ZM ask queue of 50 contracts (illustrative) is swept at t0. In the toy, a "resilient" regime with tau = 2 s has
recovered 1 - exp(-6/2) = 1 - 0.0498 = 95.0% of the queue by Delta = 6 s; a "thin" regime with tau = 20 s has
recovered 1 - exp(-6/20) = 1 - 0.7408 = 25.9% (M1_examples2.out E1). A frozen feature is R(6 s) in [0, 1] (or the
fitted tau); the hypothesis family it conditions is "after a buy sweep, low R(6 s) on the ask predicts a positive
5-15 minute ZM return; high R(6 s) predicts reversion". Check: 0.950 and 0.259 differ by a factor 3.7, so the
feature separates the two regimes well inside 6 seconds, which leaves the minutes-scale label untouched.

### 6.4 Data (owned)

ZM MBO (order-level adds and cancels by price level: full refill and cancellation ratios). ZS and ZL MBP-1: only the
net best-level size change; cancels at the best can be inferred as size decreases not matched by a trade event,
and only at level 1. Context from the grain literature (abstract level): Ma and Serra report that "Between 75% and
79% of the large number of limit orders submitted are then deleted" in CBOT corn, soybeans and wheat, so
cancellation flow is the bulk of the MBO message stream.

### 6.5 Leakage traps and tests

1. Defining the sweep by what follows (for example "a sweep that the price did not reverse"). Test: the event
   flag at t0 is a function only of messages with ts_recv <= t0; future-scramble invariance.
2. Measuring refill over a window that overlaps the label. Test: label start >= t0 + Delta + delay.
3. Choosing Delta or tau thresholds after looking at forward returns. Test: Delta and thresholds frozen in the
   protocol; any alternative counts into N.
4. MBO book-rebuild errors at the session open (snapshot versus incremental) creating fake sweeps. Test: count
   sweeps in the first 60 s after each session open and after each data gap; assert the rate is not an outlier
   versus the session average (threshold frozen; DataFacts owns the snapshot mechanics).

### 6.6 Compute

Event-driven pass inside the same book rebuild as section 2.6; negligible extra cost.

### 6.7 Verdict

MAYBE, as a conditioner for family 5 (sweep and refill aftermath): it is cheap, ZM-MBO-native, and the
contemporaneous evidence (one-sided replenishment drives impact) gives a mechanism, but there is no forward
evidence in futures, so it enters as ONE frozen feature, not a grid.

### 6.8 Evidence table (e)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Spread and depth recover within 20 best-limit updates | Xu, Chen, Xiong, Zhang et al. (arXiv 1602.00731v2) | "the spread and depth can return to the sample average within 20 best limit updates" | xu_lob_resiliency_after_mo_2016.txt |
| Resiliency after aggressive, continuation after less aggressive | Xu et al. abstract | "The price resiliency behavior is dominant after aggressive market orders, while the price continuation behavior is dominant after less-aggressive market orders." | same |
| Type-1 walks the book | Xu et al. | "a Type-1 order is an effective buy market order whose penetrability p is greater than 1. This means that these orders walk up the limit order book and result in multiple trades." | same |
| One-sided replenishment drives impact | Bechler and Ludkovski (arXiv 1708.02715) | "the Ask side is replenished less than usual under upside price pressure" and "LOB resilience (and hence price impact) is essentially driven by one-sided flows rather than aggregate two-sided metrics" | meso_scale_resiliency_2017.txt |
| Their "predictive" fits are same-bucket | Bechler and Ludkovski | "Pk+1 − Pk and the concurrent trade imbalance T Ik" and "from about R2 ≃ 0.4 when using only T I as a predictor for ∆P , to R2 ≃ 0.7 when using both T I and V Lj" | same |
| CBOT grain limit orders mostly deleted | Ma and Serra (AJAE 2025) abstract | "Between 75% and 79% of the large number of limit orders submitted are then deleted" [abstract only, IDEAS; full text not read] | ideas_ma_serra_2025.html(.txt) |

## 7. (f) Detecting large orders being worked, and icebergs, from MBO

### 7.1 Core idea

CME native icebergs keep their order ID across tranches and can trade more than their displayed size, so they are
detectable exactly from order-level data; synthetic icebergs (vendor-managed) look like a chain of new orders
arriving just after a fill and are detectable only heuristically (Zotikov and Antonov). Detecting that someone is
working a large order says where liquidity is, but Frey and Sandas find iceberg price impact is consistent with
liquidity, not information, and Bacry et al. find metaorder impact is transient and "the market does not anticipate
the size of the meta-orders". The forward directional value is therefore small and the iceberg is better used as
an absorption flag (a price level likely to hold while the iceberg lives).

### 7.2 Equations

- Native detection (Zotikov and Antonov): an order is iceberg if a trade against it exceeds its resting displayed
  size, or if it is refreshed by a modify after a fill with the same order ID; peak size and tranche count follow
  from the message grammar (their Figure 1 finite-state machine; worked example: total 43, peaks 9, 9, 9, 7).
- Total-size prediction: Kaplan-Meier on accumulated volume with censoring by cancellation; the native mean
  prediction is v_hat_mean = [sum_{u in V_p} f_p(u)]^-1 sum_{u in V_p} u f_p(u), V_p = {u : u > v_r}, v_r the volume
  executed before tranche r, f_p the estimated density of total size given peak p (their section 5.1).
- Square-root impact of a metaorder (Bacry et al.): I(Q) = Y sigma_day sqrt(Q/V_day), with a duration factor
  1/T^gamma, gamma ~= 0.25, and a transient decay with exponent 0.5-0.8 after execution (their abstract).

### 7.3 Worked example

Assumptions: a native ZM iceberg bid is detected after 40 contracts executed (illustrative); the fitted
Kaplan-Meier mean predicts a total of 120 (illustrative); Y = 1; sigma_day from the random walk over the 290-minute
day session = 3.15 x sqrt(290) = 3.15 x 17.03 = 53.64 ticks; V_day = 36,690 (ADV). If ALL of the iceberg were
informed and its impact permanent, the extra impact still to come is 53.64 x (sqrt(120/36,690) - sqrt(40/36,690)) =
53.64 x (0.05719 - 0.03302) = 1.30 ticks (M1_examples2.out F1). That is below the 1.59-tick hurdle in the most
favourable case, before the Frey-Sandas finding (liquidity, not information) and Bacry's transient decay cut it
further. Check: the impact of a 1,000-lot metaorder by the same formula is 53.64 x 0.1651 = 8.86 ticks, i.e. a
quarter of a typical day's 96-tick range (A0), a plausible order of magnitude.
[MathReview B-1 (lead: accepted): 8.86/96 = 0.092, so 8.86 ticks is under a tenth (9.2%) of the 96-tick median range, not a quarter; the "plausible order of magnitude" conclusion survives.]

### 7.4 Data (owned)

ZM MBO only: order IDs, modify actions after fills, and trade sizes per order are needed. Whether Databento's CME
MBO preserves the native-iceberg modify sequence and trade-summary sizes exactly as Zotikov and Antonov describe
for the CME feed is [unverified] here and belongs to DataFacts. ZS and ZL MBP-1 cannot see icebergs (no order IDs).

### 7.5 Leakage traps and tests

1. Labeling an order "iceberg" or "large" using its total executed size or its final fraction executed (known
   only when it dies). Frey and Sandas' impact result is conditional on "the fraction of the iceberg order that is
   eventually executed", an ex-post quantity. Test: the iceberg flag and predicted total at time t use only
   messages up to t (future-scramble invariance); log the detection timestamp and assert label start > it.
2. Fitting the Kaplan-Meier total-size model on the whole sample. Test: fit per training fold.
3. Survivorship: only icebergs that lived long enough to be detected enter the sample; the label must be measured
   from detection time, not from the iceberg's first tranche. Test: assert label_start >= detection time.

### 7.6 Compute

One extra hash map (order ID to state) in the book rebuild; the Kaplan-Meier fit is seconds.

### 7.7 Verdict

MAYBE as a conditioner (an "absorption at level L" flag and its predicted remaining size, used to condition
families 5 and 7: a sweep INTO a live iceberg is more likely to reverse); SKIP as a direction source (3.3 iii,
7.3). The synthetic-iceberg heuristic adds frozen parameters (time window after a fill, size match rule) and
false positives; leave it out unless the lead wants it as one counted variant.

### 7.8 Evidence table (f)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Native CME icebergs keep order ID; trades can exceed display | Zotikov and Antonov (arXiv 1909.09495) | "All new tranches are submitted as modifications of the initial order; this means that the original order ID is preserved throughout the whole lifetime of the iceberg. Additionally, trades against these orders may sometimes be larger in volume than the current resting size, as indicated by trade summary messages." | zotikov_antonov_cme_iceberg.txt |
| Synthetic icebergs only heuristically detectable | Zotikov and Antonov | "Synthetic icebergs, on the other hand, being identical to non-iceberg orders in how they are processed by the exchange, can only be detected heuristically" | same |
| Their data: one week of ES | Zotikov and Antonov | "an almost week-long full order depth (FOD) LOB log of a September E-Mini S&P 500 futures contract" (as rendered across lines) | same |
| Iceberg impact consistent with liquidity, conditional on eventual execution | Frey and Sandas (CFR WP 09-06) | "the observed price impact of an iceberg order of a given size depends critically on the fraction of the iceberg order that is eventually executed. Together this evidence supports the liquidity-based explanation." | frey_sandas_2009_iceberg_cfr.txt |
| Detected icebergs attract market orders | Frey and Sandas | "We find that detected iceberg orders are more likely to attract market orders that undetected iceberg orders" (sic) | same |
| Metaorder impact transient; size not anticipated | Bacry, Iuga, Lasnier, Lehalle (arXiv 1412.0217) | "We observe a power-law for the transient impact with an exponent between 0.5 (for long metaorders) and 0.8 (for shorter ones). Moreover we show that the market does not anticipate the size of the meta-orders." | bacry_etal_2015_metaorder_lifecycle.txt |
| Square-root and duration factor | Bacry et al. | "we confirm a square root temporary impact in the daily participation, and we shed light on a duration factor in 1/T γ with γ ≃ 0.25" | same |

## 8. (g) VPIN and its critiques

### 8.1 Core idea

VPIN measures the average absolute buy-sell imbalance over volume buckets, as a real-time proxy for "toxic" flow.
It is UNSIGNED by construction (absolute imbalance), so it carries no direction; its claimed use is to forecast
volatility and turmoil. Andersen and Bondarenko show its forecasting content is mostly a mechanical function of
trading intensity, with no incremental power for future volatility once volume and volatility are controlled, and
that its behaviour reverses with the trade-classification method.

### 8.2 Equations (Easley, Lopez de Prado and O'Hara 2012, RFS version)

- Bulk volume classification (ELO eq. 7): V^B_tau = sum_{i in bucket tau} V_i Z((P_i - P_{i-1})/sigma_DeltaP),
  V^S_tau = V - V^B_tau; V_i volume of time bar i, Z the standard normal CDF, sigma_DeltaP the standard deviation of
  bar price changes.
- VPIN (ELO eq. 9): VPIN = alpha mu / (alpha mu + 2 epsilon) ~= sum_{tau=1}^{n} |V^S_tau - V^B_tau| / (n V), V the
  fixed bucket volume, n the number of buckets ("V equal to one-fiftieth of the average daily volume ... n=50").

### 8.3 Worked example

V = ADV/50 = 36,690/50 = 733.8, rounded to 734 contracts per bucket. With five illustrative bucket imbalances
|V^S - V^B| = 200, 150, 400, 100, 300 (n = 5 for brevity), VPIN = (200 + 150 + 400 + 100 + 300)/(5 x 734) =
1,150/3,670 = 0.3134. Bulk classification of one 1-minute ZM bar that rose 3 ticks with sigma_DeltaP = 3.15 ticks:
buy share = Z(3/3.15) = Z(0.952) = 0.8295, so 82.95% of the bar's volume is booked as buys although the MBO data
give the true aggressor of every trade. Check: 1,150/3,670 = 0.31335. In ZM the bulk rule is unnecessary and adds
error; with MBO aggressor flags, an exact VPIN is computable.

### 8.4 Data (owned)

ZM MBO trades with aggressor side (exact V^B, V^S); ZS, ZL MBP-1 the same. Volume buckets of a frozen size.

### 8.5 Leakage traps and tests

1. Bucket size from the full-sample average daily volume (ELO: "1/50th of the average daily volume in our sample
   period"). Test: bucket size from a trailing window (for example the previous 20 sessions) only;
   future-scramble invariance.
2. Percentile thresholds from the full-sample CDF (ELO: "We use the entire sample period to determine the
   cumulative distribution function of the estimated parameters"). Test: CDF from training folds only.
3. Volume-clock features joined to a time-clock label: the bucket that is "complete" at time t may close after t.
   Test: a bucket's value is usable only from the ts_recv of its closing trade.
4. Benchmark omission (Andersen and Bondarenko): any VPIN feature must be compared with the same model using
   trailing volume and trailing |return| instead. Test: the protocol includes that benchmark as the
   comparison, not as an extra trial.

### 8.6 Compute

Trivial.

### 8.7 Verdict

SKIP for direction (unsigned). At most MAYBE as a regime conditioner, and then only if it beats the
volume-and-volatility benchmark (8.5 test 4); since AB find no incremental volatility power, the expected value of
adding it is low, and it costs a frozen choice of (V, n).

### 8.8 Evidence table (g)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Bulk classification formula | ELO (2012 RFS, NYU-hosted copy) eq. 7 | "Z is the CDF of the standard normal distribution and 𝜎∆𝑃 is the estimate of the standard derivation of price changes between time bars" | elo_2012_vpin_rfs_nyu.txt |
| Bucket and window choice | ELO | "we focus on V equal to one-fiftieth of the average daily volume. If we then choose n=50, we will calculate the VPIN metric over 50 buckets" | same |
| Full-sample bucket size and CDF | ELO | "We use a bucket size equal to 1/50th of the average daily volume in our sample period (V)" and "We use the entire sample period to determine the cumulative distribution function of the estimated parameters." | same |
| VPIN poor volatility predictor; mechanical with intensity | Andersen and Bondarenko (CREATES RP 2011-50, JFM 2014) abstract | "it is a poor predictor of short run volatility, that it did not reach an all-time high prior, but rather after, the flash crash, and that its predictive content is due primarily to a mechanical relation with the underlying trading intensity" | andersen_bondarenko_2014_vpin_flash_crash.txt |
| No incremental power after controls; classification dependence | Andersen and Bondarenko reply (CREATES RP 2013-42) | "Doing so, we find no evidence of incremental predictive power of VPIN for future volatility." and "the properties of VPIN are strongly dependent on the underlying trade classification" | andersen_bondarenko_2013_reply.txt |
| Counterpoint: VPIN top out-of-sample feature for sign of spread or volatility change, 87 futures, one week | ELOPZ (2019) | "out-of-sample prediction results show that VPIN is the most important predictor for five variables" | elopz_2019_microstructure_machine_age_nber.txt |

## 9. Planner families 5 and 7 (method side), and the grain forward-OFI evidence

### 9.1 Family 5: aftermath of non-news jumps and liquidity shocks (sweep and refill) at 1-30 minutes

Core idea. Most price jumps are not news (Joulin et al.: "neither idiosyncratic news nor market wide news can
explain the frequency and amplitude of price jumps") and look like liquidity events: "jumps are followed by
increased volatility, whereas news tend on average to be followed by lower volatility levels", and "most price
jumps are induced by order flow fluctuations close to the point of vanishing liquidity". Marcaccioli, Bouchaud and
Benzaquen show endogenous jumps are preceded by "progressively accelerating growth of volatility", and that the
volatility profile alone classifies events as endogenous or exogenous "without relying on the news feed" (a
volatility result, not a sign result). The one directional, minutes-scale, grain-inclusive measurement is the drift
burst study of Christensen, Oomen and Renò: short-lived explosive trends occur across futures, "the majority of them
are accompanied by subsequent price reversion", and in CBOT corn (ZC), day session 08:30-13:20 CT, 2012-2017, 97
bursts at |T| > 4.0 give a 5-minute reversal slope b = -0.20 (t = -8.25), R2 = 41.5%, 76.3% reversals (Table 4).

Equations (CORe eqs. 35-36): R-_j = X_{t_j} - X_{t_j - 5m}, R+_j = X_{t_j + 5m} - X_{t_j}, X the log mid, t_j the
burst time; R+_j = a + b R-_j + e_j. The test statistic uses a left-sided exponential kernel K(x) = exp(-|x|),
x <= 0, a 5-minute drift bandwidth and a 25-minute volatility bandwidth, on a 5-second grid (their section 5.2).

Worked example. Assume ZM has ZC's burst rate (an assumption; ZM is a different market). Over the discovery window
(39 months, about 3.25 x 252 = 819 trade dates) that is 97/1528 x 819 = 52.0 events at |T| > 4.0, or 29/1528 x 819
= 15.5 at |T| > 4.5. A pre-burst move of 15 ticks over 5 minutes (15/7.044 = 2.13 sigma_5m) and b = -0.20 imply an
expected 5-minute post move of -0.20 x 15 = -3.0 ticks, or 3.0 - 1.59 = 1.41 ticks net of the taker hurdle; the
break-even pre-burst move is 1.59/0.20 = 7.95 ticks (15.9 ticks if the true b is -0.10). Power: with 52 events, a
t-statistic of 3.0 on the mean net post-move needs mean/sd >= 3/sqrt(52) = 0.416. Check: 0.416 x 7.21 = 3.0.
[MathReview B-3 (lead: accepted): 0.416 is the realised-t condition, not a power statement; 80% power at t = 3 needs mean/sd >= (3 + 0.8416)/sqrt(52) = 0.533, and at 15.5 events (|T| > 4.5) 3/sqrt(15.5) = 0.762 realised and 0.976 at 80% power. Relabel as "realised t" or give the power number; the verdict's sentence "statistical power ... is the binding constraint" is strengthened, not weakened.]

The trap that decides the family. CORe count "at most one drift burst ... over any five-minute window at which the
test statistic attains a local extremum and exceeds a set critical value". A local extremum is known only after the
statistic has turned, i.e. after the drift has stopped; conditioning R+ on the extremum time selects the moment the
trend ended, which biases b toward reversal. Their test statistic is real-time (left-sided kernel, chosen "to allow
for real-time updating"), but their event time is not. A tradable protocol must time the entry at a realizable
point: the first 5-second grid time at which |T| crosses the threshold, or the first time |T| has fallen a frozen
margin below its running maximum (plus the latency delay); the published b and R2 must be expected to shrink.
Test: compute the entry time from the stream truncated at that time (future-scramble invariance) and log the
distance between realizable entry and CORe's extremum time.

Data. ZM MBO (mid on a 5-second grid, plus sweep/refill and iceberg conditioners from sections 6-7); ZS and ZL
MBP-1 for "is the burst complex-wide or ZM-only" (an endogenous ZM-only burst is the liquidity case).
Compute: the drift-burst statistic is two kernel-weighted sums per 5-second step: about 819 days x 23 h x 720
steps = 13.6 million evaluations, minutes on one core.
Verdict: USE as a candidate event family (one frozen detector, one frozen entry rule, one label horizon set), with
the realizable-time correction mandatory and the expected sample of about 15-52 events stated up front: the
statistical power, not the mechanism, is the binding constraint. Conditioners from sections 3, 6 and 7 (sign
imbalance with no price move, refill ratio, live iceberg at the level) are where order flow earns its place.

### 9.2 Family 7: MBO order-flow imbalance, aggressive cancellations and queue features as conditioners only

The evidence in sections 2-8 supports the planner's "conditioners only": forward order-flow predictability is
negative out of sample at 1 minute in the best equity study (CCZ Table 8), gone by 30 minutes in CRS, about 12 s
in ZM by the KTW rule (2.3 iv), priced away for sign persistence (3.3 ii), bounded at 0.5 tick for the microprice
(5.3), and unsigned for VPIN (8.1). Recommended frozen conditioner set (lead's decision; listed for convenience,
each computed at one frozen window): ZM best-level OFI and integrated OFI over the last 1 and 5 minutes; ZS and ZL
best-level OFI over the last 1 and 5 minutes; trade-sign imbalance over the last 5 minutes; refill ratio R(6 s)
after the last sweep; a live-native-iceberg flag at the best levels; a trailing Kyle lambda. None is a separate
configuration; all enter one frozen model, so N grows by the model, not by the feature count.

### 9.3 Forward OFI evidence in grains (planner pointer: "no forward-looking OFI evidence exists for grains")

Two abstracts state forward predictability from order imbalance in soy-complex or CBOT grain futures, against the
planner's wording:
- Volkenand, Filler and Odening (2018, Agricultural Finance Review), CME best bid and offer data for corn, wheat,
  soy, live cattle and lean hogs, March 2008 and March 2016: "For some contracts, returns can be predicted using
  lagged order imbalance. This offers the opportunity to derive profitable trading strategies." [abstract only]
- Jin, Kearney, Li and Yang (2023, International Journal of Finance & Economics), Chinese soybean meal futures
  (Dalian): "while both OFI and TI are shown to predict future price changes, this predictability diminishes over
  longer measure and price change frequency horizons." [abstract only]
Neither full text was read (Hull repository: Cloudflare challenge, and robots.txt disallows ClaudeBot; Emerald
full-text page: one curl returned a Cloudflare "Just a moment..." challenge, no further routes tried; section 11), so the horizons, the out-of-sample
design and any cost treatment are unknown. Ma and Serra's abstract frames its result as contribution to "price
discovery" by order types (a contemporaneous decomposition), which supports the first half of the planner's
sentence. Net: forward OFI evidence for grains EXISTS at abstract level, is short-lived where described, and has
no verified after-cost result.

### 9.4 Evidence table (families 5 and 7, grain OFI)

| Claim | Source | Verbatim quote | File |
|---|---|---|---|
| Jumps not explained by news; volatility after jumps rises | Joulin, Lefevre, Grunberg, Bouchaud (arXiv 0803.1769) | "neither idiosyncratic news nor market wide news can explain the frequency and amplitude of price jumps" and "jumps are followed by increased volatility, whereas news tend on average to be followed by lower volatility levels" | joulin_etal_2008_jumps.txt |
| Jumps from vanishing liquidity | Joulin et al. | "We conjecture that most price jumps are induced by order flow fluctuations close to the point of vanishing liquidity." | same |
| Endogenous vs exogenous volatility profiles | Marcaccioli, Bouchaud, Benzaquen (arXiv 2106.07040) | "endogenous price jumps are characterized by progressively accelerating growth of volatility" and "classify large events into endogenous and exogenous dynamical classes, without relying on the news feed" | marcaccioli_bouchaud_benzaquen_2022_jumps.txt |
| Drift bursts common, mostly reversed | Christensen, Oomen, Renò, "The drift burst hypothesis" (arXiv 2601.08974v2, paper dated November 2020) | "Drift bursts occur once a week on average, and the majority of them are accompanied by subsequent price reversion and can thus be regarded as “ﬂash crashes.”" | christensen_oomen_reno_drift_burst.txt |
| ZC sample and session | CORe Table 2 note | "the sample period is January 2012 – December 2017 for all contracts, except ES" and "except for ZC where the interval is restricted to 08:30 – 13:20 Chicago time" | same |
| ZC counts | CORe Table 3 | "ZC Corn 1.15 1.13 2.9 97 29 15 5 2" (counts at |T| > 4.0, 4.5, 5.0, 5.5, 6.0) | same |
| ZC reversal regression | CORe Table 4, Panel A | "ZC 97 −0.20 41.5% 76.3% 87 −0.21 43.0% 77.0%" with t "(−8.25) (−8.05)" | same |
| Reversion regression definition | CORe eqs. 35-36 | "R t+ = a + b R t− + εt j . (36)" and "b < 0 means a drift burst tends to be followed by a retracement of the price" | same |
| Event time at local extremum (look-ahead) | CORe footnote 24 | "we allow for at most one drift burst to be established over any ﬁve-minute window at which the test statistic attains a local extremum and exceeds a set critical value" | same |
| Real-time kernel | CORe footnote 23 | "In practice, a backward-looking kernel is preferred to allow for real-time updating." | same |
| Lagged OI predicts some CME ag returns | Volkenand, Filler, Odening (2018 AFR) | "For some contracts, returns can be predicted using lagged order imbalance." [abstract only, IDEAS] | ideas_volkenand_2018.html(.txt) |
| Soybean meal OFI predicts, decays with horizon | Jin, Kearney, Li, Yang (2023 IJFE) | "while both OFI and TI are shown to predict future price changes, this predictability diminishes over longer measure and price change frequency horizons" [abstract only, IDEAS] | ideas_jin_etal_2023.html(.txt) |
| Ma-Serra is a price-discovery study | Ma and Serra (2025 AJAE) | "We examine limit order dynamics and their role in price discovery in the Chicago Mercantile Exchange (CME) corn, soybean, and wheat futures markets from January 2019 to June 2020, using order‐level data." [abstract only, IDEAS] | ideas_ma_serra_2025.html(.txt) |

## 10. Verdicts in one table (minutes-scale DIRECTIONAL ZM search under V43)

| Measure | Verdict | Role | Main reason |
|---|---|---|---|
| Best-level OFI (ZM, ZS, ZL), lagged 1-5 min | MAYBE | feature in one frozen model | forward R2 = rho^2 x R2_c is small; CCZ 1-min out-of-sample R2 negative; cross-asset lags the only positive forward finding |
| Multi-level / integrated OFI (ZM) | MAYBE (integrated only) | feature | gains are contemporaneous; integrated OFI is one number, MLOFI vector adds parameters |
| Deep order-flow models (KTW) | SKIP | none | effective horizon about two price changes, about 12 s in ZM (2.3 iv) |
| Trade-sign imbalance | SKIP as signal; MAYBE as conditioner | absorption flag | asymmetric liquidity prices sign persistence; extreme imbalance means a pinned price |
| Kyle lambda (trailing) | MAYBE | liquidity-state conditioner | contemporaneous by construction; slope scales as N^-0.25 so the window must be frozen |
| Microprice | SKIP as signal; USE in labels | de-noised mid for labels and entries | martingale, bounded at 0.5 tick in a 1-tick book |
| Cancellation / refill rates, resiliency | MAYBE | family-5 conditioner | mechanism documented contemporaneously; no forward futures evidence |
| Iceberg / large-order detection | MAYBE | absorption-level flag | impact is liquidity, transient; 1.30-tick best case below 1.59 |
| VPIN | SKIP (direction) | at most regime flag vs benchmark | unsigned; no incremental volatility power after controls |
| Drift-burst aftermath (family 5) | USE | candidate event family | ZC b = -0.20, R2 41.5% published, but event time has look-ahead; 15-52 ZM events expected |

## 11. Planner pointers (method side; R3b_microstructure owns the grain papers' numbers)

| Planner claim | Status | Evidence |
|---|---|---|
| Ma and Serra (AJAE 2025): "This is contemporaneous" | PARTLY VERIFIED | Abstract (IDEAS) frames the study as the "role in price discovery" of order types, a contemporaneous decomposition; full text not read (Wiley terms; Cloudflare), so the method detail and the 27-30% / 56% shares are not checked here (R3b's item). |
| "no forward-looking OFI evidence exists for grains" | REFUTED as worded (abstract level) | Volkenand, Filler and Odening 2018 (CME corn, wheat, soy): "For some contracts, returns can be predicted using lagged order imbalance."; Jin, Kearney, Li and Yang 2023 (Chinese soybean meal): "both OFI and TI are shown to predict future price changes, this predictability diminishes over longer measure and price change frequency horizons". Both abstract only; no after-cost or minutes-horizon result verified. The planner's practical point (no usable forward OFI edge documented) stands. |
| Family 5: aftermath of non-news jumps and liquidity shocks, sweep and refill, 1-30 minutes | PARTLY VERIFIED (mechanism and one grain measurement) | Drift-burst reversal in ZC at 5 minutes, b = -0.20, R2 41.5%, 97 events (CORe Table 4, full text); non-news jumps are liquidity events (Joulin et al.); but the event time is a local extremum (look-ahead), and no source measures sweep-and-refill conditioned forward returns in futures. |
| Family 7: MBO OFI, aggressive cancellations, queue features as conditioners only | VERIFIED (consistent with every forward source read) | CCZ Table 8 negative 1-min out-of-sample R2; CRS "In no more than thirty minutes, order imbalances lose their predictive ability"; KTW horizon "approximately two average price changes" (abstract); asymmetric liquidity (BFL). |

## 12. Gaps, failures, stopping rule and route log

- Not read in full (abstract or slides only): Kolm, Turiel and Westray 2023 (Wiley; terms forbid automated access;
  SSRN blocked); Stoikov 2018 journal version (closed; slides used, as in E.28); Ma and Serra 2025 (Wiley:
  WebFetch 403, curl Cloudflare); Jin et al. 2023 (Hull repository Cloudflare, robots disallow ClaudeBot);
  Volkenand et al. 2018 (Emerald Cloudflare challenge, one attempt); Wang, Ye and Zhao 2016 (Chinese ag futures,
  daily; known from a search snippet only; the AUT PDF link returned HTML, not the paper).
- Topic stopping rule: (a) 4 full texts (CKS, XGH, CCZ, CRS); (b) 4 (Lillo-Farmer, BGPW, BFL, Patzelt-Bouchaud);
  (c) 3 (Hasbrouck, ELOPZ, Patzelt-Bouchaud); (d) slides only, all that is accessible (same as E.28); (e) 2 full
  texts (Xu et al., Bechler-Ludkovski) plus E.28 2.2, below the 3-source rule: a third forward-resiliency source
  in futures was not found and no extra discovery query was spent on it in this run; (f) 3 (Zotikov-Antonov,
  Frey-Sandas, Bacry et al.); (g) 4 (ELO, AB 2014, AB reply, ELOPZ); family 5: 3 (CORe, Joulin, Marcaccioli). The
  "last 3 discovery queries surfaced nothing new" condition is documented only for the grain forward-OFI question
  (2 queries in this run returned the same three papers); the first run's discovery queries were not logged, so
  for the other topics this condition is unverified.
- Correction to my own first run: M1_examples.py used Chordia-Roll-Subrahmanyam R2 inputs (0.0261, 0.0028, 0.0007)
  that are not in CRS Table 5; M1_examples2.py uses the Table 5 values (3.32%, 0.53%, 0.54%, 0.18%).
- Numerical caveats a reviewer should recheck: the random-walk scaling (A1) for every sigma_h; the KTW 12-second
  translation assumes unit-tick mid steps (half-tick moves and bounce would change it); the drift-burst event
  count assumes ZM's burst rate equals ZC's 2012-2017 day-session rate; BGPW's "Ne ≈ 50" recomputes to 63.7.
- Databento-specific encoding of native-iceberg modifies and trade-summary sizes in CME MBO is unverified here
  (DataFacts).
- WebSearch: 4 calls in this run; no budget notice seen. No Scrapling or Firecrawl used in this run; all fetches
  by curl (arXiv, IDEAS, Imperial) and logged in log.tsv with sha256.
