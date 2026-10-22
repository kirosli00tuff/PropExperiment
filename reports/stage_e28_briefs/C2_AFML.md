# E.28 methods brief, Part C2: fractional differencing, labels and validation (AFML), wavelets and spectral methods

Worker: C2_AFML (MethodReader, opus). Written 2026-10-21 PDT, starting 02:44. Pages:
`reports/stage_e28_briefs/pages/C2_AFML/` (log: `log.tsv`). Scripts and outputs:
`reports/stage_e28_briefs/work/C2_AFML/` (`C2_AFML_examples.py` with `C2_AFML_examples.json`;
`C2_AFML_lgb_probe.py` with `C2_AFML_lgb_probe.json`). Every number marked "measured" or "computed" comes from those
files, which use synthetic data only. No market data was read, nothing is registered, and N stays 538.

How to read this section. Section 0 says what the pilot will measure and why these methods matter for it. Sections 1
to 10 take each method in turn and answer the brief's eight items: (1) idea, (2) equations, (3) data, (4) what it
estimates or decides, (5) worked example, (6) pilot hypothesis, (7) compute, (8) evidence. Section 11 sums up compute,
section 12 lists the candidate hypotheses in one table, and section 13 gives verdicts. The references, the evidence
table and the gaps log come after that.

Source caveat, stated once. *Advances in Financial Machine Learning* (AFML, Lopez de Prado 2018, Wiley) is a paid
book, and I did not fetch it. Its methods are quoted here from the author's own summary paper, which states them with
the same equations and points to the book chapters: Lopez de Prado (2018), "The 10 Reasons Most Machine Learning
Funds Fail", *Journal of Portfolio Management* 44(6) (file `lopezdeprado_2018_10reasons_jpm.txt`). The
fixed-width-window details come from the open-source mlfinpy documentation, which quotes chapter 5
(`mlfinpy_fracdiff.txt`). Hosking (1981), Andersen and Bollerslev (1997), Gencay, Selcuk and Whitcher (2002, book;
2001, paper) and Arian et al. (2024) are paywalled. For those I cite open full-text secondary sources, and claims
taken from abstracts or citing papers are marked [unverified]. pdftotext garbles some math symbols. Where a quote is
garbled I say so and restate the equation in clean notation.

---

## 0. What the pilot gives these methods to work with

Part B buys one schema for one CME contract for about 4 months. For a simulated 1-lot passive order it measures:

- a fill indicator F_i in {0, 1} for each order i;
- a queue time Q_i, the seconds from posting to fill (censored when the order is cancelled or never fills);
- markouts M_i(h) = s_i (m_{t_i + h} - p_i) / tick, for h in {1, 10, 60} seconds. Here s_i = +1 for a filled buy
  and -1 for a filled sell, p_i is the fill price and m is the mid price.

Three features of this data shape the rest of this section:

1. **The labels look forward and overlap.** M_i(60) depends on the 60 seconds after the fill. If orders are posted
   every few seconds, neighbouring labels share most of their future path. This is exactly the situation that
   AFML's uniqueness weights (section 4), purging and embargo (section 5) and CPCV (section 6) were built for.
2. **The features are not stationary.** Price levels, cumulative order-flow imbalance and queue depth drift and
   trend. Fractional differencing (section 1) claims to make such series stationary while keeping their memory.
3. **The data has strong time-of-day structure.** Fill rates, spreads, depth and volatility all depend on the time
   of day, including the Globex open, the 08:30 ET data releases, the cash open and close, and the 16:00 to 17:00 CT
   maintenance halt. Spectral and periodicity methods (sections 9 and 10) measure and remove that structure.
   Wavelets (sections 7 and 8) split a series by time scale.

None of these methods is a strategy by itself. They are preprocessing, labelling and validation tools. Their value
here depends on two things: whether they make the single honest test of a frozen pipeline (V43) more powerful, and
how many configurations they add to N.

---

## 1. Fractional differencing (Hosking 1981; AFML ch. 5, fixed-width window, minimum d passing ADF)

### 1.1 Idea

Taking returns (the first difference of log prices) makes a price series stationary, but it throws away the level.
Every value of a return series "forgets" where the price was. The opposite choice keeps the full level but is
non-stationary, and most estimators assume stationarity. Fractional differencing takes a non-integer amount d
between 0 and 1 of differencing. The output is a weighted sum of the current and past values, with weights that
decay slowly. Lopez de Prado proposes the smallest d whose output passes a unit-root test, on the argument that this
keeps "as much memory as possible" (`lopezdeprado_2018_10reasons_jpm.txt`, line 259). In his words: "Fractional differentiation (FracDiff) allows us to generalize the
notion of returns to non-integer (positive real) differences 𝑑" (`lopezdeprado_2018_10reasons_jpm.txt`, lines
282-283).

Hosking (1981) introduced the operator in time-series modelling as ARIMA(0, d, 0), "fractionally differenced"
noise. A history paper puts it this way: Hosking "proposed to reverse this order of operations, i.e discretising
first, then fractionally differencing", and the result "for 0 < d < 1/2 is stationary and possesses long memory"
(`graves_etal_2014_long_memory_history.txt`, lines 1065-1071). I did not obtain Hosking (1981) itself. Its theorems
are cited through Graves et al. (2014) and Hurvich's NYU handout.

### 1.2 Equations

**The operator.** Let B be the backshift operator, B x_t = x_{t-1}. For real d, the binomial series gives

    (1 - B)^d = sum_{k=0}^{inf} w_k B^k,   w_0 = 1,   w_k = -w_{k-1} (d - k + 1) / k.

The output is x~_t = sum_k w_k x_{t-k}. The AFML summary gives exactly this recursion, 𝜔𝑘 = −𝜔𝑘−1 (𝑑−𝑘+1)/𝑘, with "𝜔0 = 1"
(`lopezdeprado_2018_10reasons_jpm.txt`, lines 283-288; the recursion is restated because pdftotext splits the
fraction over three lines). The closed form is w_k = (-1)^k C(d, k), where C(d, k) = d(d-1)...(d-k+1)/k! is the generalised binomial
coefficient. Equivalently, w_k = Gamma(k - d) / (Gamma(k + 1) Gamma(-d)). Hurvich writes the same coefficients
(his π_j) as Gamma(j - d) / (Gamma(j + 1) Gamma(-d)), a fraction split over lines 81-83 in the extraction, and notes that "π j ∼ j −d −1/Γ(−d ) as j → ∞"
(`hurvich_farima_handout.txt`, line 119; the exponent is -d-1).

*Derivation summary.* Expand (1 - z)^d = sum_k C(d, k)(-z)^k, which is valid for |z| < 1. Then
w_k / w_{k-1} = -(d - k + 1)/k, which is the recursion above. Stirling's formula gives
|w_k| ~ k^{-d-1} / |Gamma(-d)|, so the weights decay as a power law, not exponentially. That slow decay is the "long
memory."

**Special cases.** For d = 0 the weights are (1, 0, 0, ...), so the output equals the input. For d = 1 they are
(1, -1, 0, ...), which is ordinary returns. For 0 < d < 1, "all weights after 𝜔0 = 1 are negative and greater than
-1" (`lopezdeprado_2018_10reasons_jpm.txt`, lines 293-299).

**Stationarity (Hosking's model).** If x_t = (1 - B)^{-d} e_t with e_t white noise, then x_t is weakly stationary for
d in (-0.5, 0.5). Its spectral density is

    f(lambda) = (sigma^2 / 2 pi) |2 sin(lambda / 2)|^{-2d},   so   f(lambda) ~ (sigma^2 / 2 pi) lambda^{-2d} as lambda -> 0.

Hurvich: "If d ∈ (−.5 , .5), then {xt } is weakly stationary" and "the ARIMA (0,d ,0) process will not be stationary
if d ≥ .5" (`hurvich_farima_handout.txt`, lines 121 and 151). The spectral density appears at lines 158-169, with
garbled symbols. Its autocorrelation decays as k^{2d-1}, a standard result I did not verify against Hosking's own
text, so it is marked [unverified]. The application to prices follows from this. If the log price is I(1)
(integrated of order 1), then (1 - B)^d applied to it is I(1 - d). That output is stationary only when 1 - d < 0.5,
that is d > 0.5, in the infinite-window theory.

**Expanding versus fixed-width window (FFD).** A sample of length T only supplies the first t weights at time t.
Early outputs therefore use fewer weights than late ones (an "expanding window"), and AFML shows this gives the output
a drift. The fixed-width fix keeps only the weights larger than a threshold tau and applies that same window at every
t:

    l* = largest k with |w_k| >= tau;   x~_t = sum_{k=0}^{l*} w_k x_{t-k}   for t > l*.

The mlfinpy documentation quotes chapter 5: "Without the control of weight-loss the \(\widetilde{X}\) series will
pose a severe negative drift. This problem is corrected by using a fixed-width window and not an expanding one"
(`mlfinpy_fracdiff.txt`, lines 66-67). Its function signature describes `thresh` as the "Threshold for minimum weight"
(line 92). The weight-loss ratio lambda_l that the docs define (lines 58-63) belongs to the expanding-window variant.

**Choosing d.** Compute FFD for d on a grid (for example 0, 0.05, ..., 1). Run an augmented Dickey-Fuller (ADF) test
on each output and pick the smallest d whose ADF statistic is below the 5% critical value. The ADF regression is

    Delta y_t = a + b y_{t-1} + sum_{i=1}^{p} c_i Delta y_{t-i} + e_t,   H0: b = 0 (unit root),   statistic = b_hat / se(b_hat).

The statistic is compared with Dickey-Fuller critical values, not normal ones (about -2.86 at 5% with a constant).
mlfinpy: "Based on where the ADF statistic crosses this threshold, the minimum \(d\) value can be defined"
(`mlfinpy_fracdiff.txt`, lines 123-124).

**A property the sources do not state (my derivation, checked numerically).** The FFD weights do not sum to zero.
Partial sums of binomial coefficients satisfy

    S(l) = sum_{k=0}^{l} w_k = prod_{k=1}^{l} (1 - d/k) = Gamma(l + 1 - d) / (Gamma(1 - d) Gamma(l + 1)) ~ l^{-d} / Gamma(1 - d).

Write x_{t-k} = x_t - (r_t + ... + r_{t-k+1}), with r the returns. Then

    x~_t = S(l*) x_t  -  sum_{k=1}^{l*} w_k (r_t + ... + r_{t-k+1}).

So the FFD output is a small multiple S(l*) of the price level plus a finite moving average of returns. If the price
has a unit root, the FFD output still has one, scaled by S(l*): about 0.070 for d = 0.4 and tau = 1e-4, a window of
282 weights (computed; `C2_AFML_examples.json`, key `ffd_weights`; the asymptotic formula gives 0.0703). With p = 1 the ADF
regression cannot absorb the long negative moving average in Delta x~_t (the weights after w_0 sum to S(l*) - 1, about
-0.87 at d = 0.3), so the test over-rejects (Schwert 1989). With Schwert's lag rule the rejection at d = 0.3 to 0.4 is
borderline or absent (`REV_G6_math_checks.json`). The output still carries a unit root scaled by S(l*). This does not
mean the series is stationary. It also means that a high correlation between the FFD output and the price level comes
mostly from that scaled level component. It is not evidence of predictive memory.

### 1.3 Data needed, and whether one contract for 4 to 12 months is enough

FFD needs one time series sampled on a regular clock, an event clock or volume bars. The candidates are a mid-price
series, cumulative signed volume, cumulative OFI (order-flow imbalance) or queue depth. Any of the three schemas
(mbp-10, mbo, tbbo) supply mid prices and trades. Cumulative OFI and depth features need mbp-10 (depth) or mbo.
Length is not a constraint. Four months of 1-second bars is about 7.0 million points (84 x 23 x 3600 = 6,955,200; the
timing runs used 7.2 million). An FFD window of 282 to 1,458 points uses up less than 0.03% of that. What 4 months cannot do is tell a
real long-memory effect from a finite-sample artefact. The selected d* changes with the sample (section 1.5).

### 1.4 What it estimates or decides

FFD decides a feature transform. The "minimum d" rule picks a single number d* from a unit-root test. It estimates
no relation to returns and makes no forecast. In the time-series literature, d is a parameter of a long-memory model
and is estimated by MLE or log-periodogram regression. AFML's d* is a different object: a preprocessing setting
chosen by a test threshold.

### 1.5 Worked example (computed; `C2_AFML_examples.py`)

**Weights for d = 0.4.** The recursion gives w_0 = 1. Then w_1 = -1 (0.4 - 0)/1 = -0.4,
w_2 = -(-0.4)(0.4 - 1)/2 = 0.4 * (-0.6)/2 = -0.12, w_3 = -(-0.12)(0.4 - 2)/3 = 0.12 * (-1.6)/3 = -0.064,
w_4 = -0.0416 and w_5 = -0.029952. These match the script's output exactly. The window length and the weight sum
depend on tau:

| d | tau | window l*+1 | S = sum of weights | l^{-d}/Gamma(1-d) |
|---|---|---|---|---|
| 0.2 | 1e-4 | 497 | 0.248 | 0.248 |
| 0.4 | 1e-3 | 55 | 0.136 | 0.135 |
| 0.4 | 1e-4 | 282 | 0.070 | 0.070 |
| 0.4 | 1e-5 | 1,458 | 0.036 | 0.036 |
| 0.6 | 1e-4 | 140 | 0.023 | 0.023 |

**A pure random walk passes the "minimum d" test.** I simulated T = 200,000 i.i.d. normal log returns (sd 1e-4), so
nothing is predictable by construction, and applied FFD with tau = 1e-4. ADF was run on every 10th point, with one lagged difference (p = 1), the
setting AFML's own fixed-width-window snippet uses [unverified: book not fetched]:

| d | ADF t | corr(FFD, level) | corr(FFD_t, r_{t+1}) |
|---|---|---|---|
| 0.0 | -0.92 | 1.000 | -0.002 |
| 0.2 | -2.12 | 0.999 | -0.002 |
| 0.3 | -3.29 | 0.998 | -0.002 |
| 0.4 | -4.98 | 0.996 | -0.002 |
| 0.6 | -11.81 | 0.979 | -0.003 |
| 1.0 | -98.99 | 0.002 | -0.005 |

This reproduces the pattern Lopez de Prado reports for E-mini log prices: "ADF statistic computed on the FracDiff
series with 𝑑 = .4 is -3.2733 ... the correlation between the original series and the FracDiff series with 𝑑 = .4
is very high, around 0.995, indicating that most of the memory is still preserved"
(`lopezdeprado_2018_10reasons_jpm.txt`, lines 302-308). On a series with no memory to preserve, d = 0.3 already
passes ADF with a 0.998 correlation to the level, and FFD has zero correlation with the next return at every d. The
selected d* also moves with the sample: 0.35 on the first half, 0.15 on the second half and 0.30 on the full sample
(key `ffd_dstar_by_segment`). On this evidence, "passes ADF while correlated with the level" cannot by itself tell a
useful feature from a useless one.

### 1.6 Pilot use: a testable hypothesis

- **H-FD1 (feature value).** In a frozen classifier for "adverse fill" (M_i(10) < 0, or M_i(60) below minus the
  per-side fee), replace the integer-differenced version of one drifting input (cumulative OFI or the mid price)
  with its FFD version. Fix tau = 1e-4 and choose d* inside each training fold by the ADF rule. H0: out-of-sample log
  loss is unchanged.
- **Statistic.** The mean per-fill difference in log loss between the two models over purged and embargoed test
  folds, with a Newey-West (HAC) t, or a block bootstrap over days.
- **Sample.** At least several thousand fills. The section 12 power formula is unit-free, so delta and sigma must be in the
  statistic's units (log loss per fill). With placeholders delta = 0.005 and sigma = 0.3 per fill it gives about 28,000
  independent fills; H-FD1's sample is set by the log-loss sd measured in the pilot. The tick-denominated example
  belongs to H-TB1 and H-ML1, not here. Overlapping 60-second labels reduce the effective sample
  (section 4).
- **Trial count.** 1 configuration if d* is set by the rule inside folds and tau is frozen. A grid of fixed d values
  adds one configuration per value (for example 5 for d in {0.2, 0.4, 0.6, 0.8, 1.0}).

### 1.7 Compute

FFD is one convolution. On the laptop it took 0.55 s for 7.2 million points (d = 0.4, tau = 1e-5, window 1,458; FFT
convolution; measured, key `timing_ffd_7.2M_d0.4_tau1e-5_s`). The ADF grid over 20 values of d, run on a 1-in-10
subsample, takes seconds. No GPU or cloud machine is needed.

### 1.8 Evidence that it works out of sample, at retail scale and latency

- **Original claim (in sample, no predictive test).** The E-mini example above reports ADF statistics and
  correlations only. It does not show a forecast improving. The paper's broader claim is: "Without memory, series
  will not be predictive" (`lopezdeprado_2018_10reasons_jpm.txt`, line 321). The simulation in section 1.5 shows
  that a high correlation with the level appears even when there is nothing to predict.
- **Gajda and Walasek (2020), Warsaw WP 32/2020.** Four stock indices, an ANN, judged by RMSE and MAE: "The conclusion
  of the study is that fractionally differentiated time series performed better in trained ANN" (`wne_wp338.txt`,
  abstract). This is a forecast-error comparison with no trading costs. It does not settle whether the target was
  made comparable across the two transforms. An RMSE on fractionally differenced targets is not a return forecast.
- **Slepaczuk and Bieganowski (2024, ICAIF; arXiv 2411.12753).** Crypto, supervised autoencoders. The method picks d*
  inside a walk-forward ("Fractional differencing will be applied to features using a walk-", line 83), charges a
  0.05% cost per trade ("Transaction cost for all assets amounts to 0.05%", line 327), and admits "research does not
  take into account slippage" (line 453). I found no ablation that removes FFD while keeping everything else, so the
  paper cannot isolate what FFD contributes.
- **Andersen and Bollerslev (1996, NBER w5752).** The established use of fractional differencing on high-frequency
  data is to model long memory in volatility, through absolute returns. It is not used to forecast price direction.
  This paper fractionally differences 5-minute absolute DM-dollar returns to study volatility persistence (see the
  "the fractionally difference five-minute" absolute returns at line 882, and the filter gain at line 848).
- **Independent critiques.** I found no peer-reviewed paper that tests AFML's FFD rule out of sample against plain
  returns at intraday frequency. My search on 2026-10-21 found applications and tutorials only. The critique here is
  my own derivation and simulation in sections 1.2 and 1.5, not a published result. *Retail latency:* FFD costs
  nothing to compute in real time (one dot product of about 300 weights per update), so latency is not the issue.
  Whether it adds information is.

**Assessment.** FFD is a cheap and harmless transform. Its signature claim, keeping memory while passing ADF, can be
reproduced on pure noise with a one-lag ADF, and the cited evidence for it is in sample or lacks an ablation. Treat it as one optional
feature variant, counted in N, never as a source of edge.

---

## 2. The triple-barrier labelling method (AFML ch. 3)

### 2.1 Idea

A fixed-horizon label ("did the price go up over the next h seconds?") ignores what happened along the way. A
position stopped out at minus 4 ticks and a position that ends at plus 1 tick count as opposite outcomes, even if the
first would have been closed long before the horizon. The triple-barrier method labels each event by which of three
exits it reaches first: a profit-taking level (upper), a stop-loss level (lower), or a time limit (vertical). In the
source's words: "If the upper horizontal barrier is touched first, we label the observation as a 1. If the lower
horizontal barrier is touched first, we label the observation as a -1. If the vertical barrier is touched first, we
have two choices: The sign of the return, or a 0" (`lopezdeprado_2018_10reasons_jpm.txt`, lines 360-363).

### 2.2 Equations

For event i, starting at time t_{i,0} with price p_{i,0}, a volatility estimate sigma_i (for example an EWMA of
recent returns), multipliers (u, l) and a vertical horizon h:

    upper_i = p_{i,0} (1 + u sigma_i),   lower_i = p_{i,0} (1 - l sigma_i),
    tau_up  = inf{ t in (t_{i,0}, t_{i,0} + h] : p_t >= upper_i },   tau_dn = inf{ t : p_t <= lower_i },
    t_{i,1} = min(tau_up, tau_dn, t_{i,0} + h),
    y_i = +1 if t_{i,1} = tau_up;  -1 if t_{i,1} = tau_dn;  sign(p_{t_{i,0}+h} - p_{i,0}) (or 0) otherwise.

The source states the timing conditions: "We will denote 𝑡𝑖,1 the time of the first barrier touch, and the return
associated with the observed feature is 𝑟𝑡𝑖,0 ,𝑡𝑖,1 . For the sake of clarity, 𝑡𝑖,1 ≤ 𝑡𝑖,0 + ℎ and the horizontal
barriers are not necessarily symmetric" (lines 367-371). It also says the barriers scale with volatility: "a dynamic
function of estimated volatility (whether realized or implied)" (line 357). The interval [t_{i,0}, t_{i,1}] is the
label's span. Sections 4 to 6 use it.

**A fact the method leans on.** If the price is a driftless random walk and the barriers are symmetric, the
probability of hitting the upper barrier first is 1/2 (by the optional stopping theorem applied to the martingale
p_t). With asymmetric barriers at distances a above and b below, and no drift, P(up first) = b / (a + b). (Standard
gambler's-ruin result, ignoring the vertical barrier. My statement, not from the fetched sources.) So a model that
predicts "+1" more often than b/(a + b) of the time is claiming drift or path structure.

### 2.3 Data, and whether one contract for 4 to 12 months is enough

The method needs a price path after each event at the resolution of the barriers. For a passive-order pilot, the
natural version is defined *after a fill*: a profit target k_u ticks better than the fill price, a stop k_l ticks
worse, and a vertical barrier at 10 s or 60 s. Trades and the best bid and offer are enough to compute it, so tbbo
suffices and mbp-10 is more than enough. With barriers of 1 to 4 MES ticks and a horizon of 60 s, four months yields
as many labels as there are simulated fills, typically thousands. Barrier hits within one second need event-time
(not 1-second bar) resolution, which all three schemas provide.

### 2.4 What it estimates or decides

It defines the label (the target). It estimates nothing. Its parameters, (u, l, h) or (k_u, k_l, h), are design
choices, and each choice is a configuration counted in N.

### 2.5 Worked example (computed by hand)

MES ticks are 0.25 index points. Event at p_0 = 100.00 (a toy price), barriers ±0.50 (2 ticks), vertical barrier
after 6 updates. Path: 100.25, 100.00, 99.75, 100.25, 100.50, 100.75.
- Update 1: 100.25 < 100.50 and > 99.50, no touch. Update 2: 100.00, no touch. Update 3: 99.75 > 99.50, no touch.
  Update 4: 100.25, no touch. Update 5: 100.50 >= 100.50, upper touched. So t_1 = update 5, y = +1, and the
  realised return is +0.50 = +2 ticks.
- With ±0.75 barriers instead, no barrier is touched before update 6. At update 6 the price is 100.75, which equals
  the upper barrier, so y = +1 at t_1 = 6, the same time as the vertical barrier. A barrier exactly on the last
  update shows that ties need a declared rule.
- A fixed-horizon label at update 3 would have been -1 (99.75 < 100). That is the path dependence the method exists
  to handle.

### 2.6 Pilot use: a testable hypothesis

- **H-TB1 (conditional fill quality).** For filled 1-lot passive orders, define the triple-barrier outcome with
  k_u = k_l = 2 ticks and h = 60 s. Score the outcome in ticks: +k_u, -k_l, or the 60-s markout if the vertical
  barrier comes first. Subtract the per-side fee in ticks. H0: the mean is <= 0. H1: it is > 0 in a pre-declared
  subset, for example when the queue ahead at posting is below its median.
- **Statistic.** A one-sided HAC t on the per-fill net outcome, clustered by day. The fills are not independent
  because their spans overlap (section 4).
- **Sample.** 2,000 or more fills is a minimum guide. The power numbers are in section 12.
- **Trial count.** 1 per barrier and horizon pair. A small declared grid such as (k_u = k_l) in {1, 2, 4} times
  h in {10, 60} s adds 6. The Korean-stocks study below *optimised* its barriers. That practice inflates N and must
  be counted.

### 2.7 Compute

Labelling is a single forward scan per event. With a vectorised first-passage search it is O(events x horizon
updates). For 10^5 fills and about 10^3 book updates per 60 s, that is about 10^8 comparisons, seconds on the
laptop. No GPU is needed.

### 2.8 Evidence

- **Primary source.** The method is a definition. Its only stated advantage is realism of the target. The summary
  paper offers no out-of-sample test of triple-barrier labels against fixed-horizon labels.
- **Korean stocks (arXiv 2504.02249, 2025).** "we optimize the triple barrier labeling" (line 26) and arrive at a
  "29-day window and 9% barriers" chosen to "ensure balanced label" (lines 29 and 40-41). The results are
  classification metrics. The barrier search is itself a multiple-testing step.
- **Crypto (arXiv 2411.12753).** Uses triple-barrier labels with walk-forward and a 0.05% cost, but ignores slippage
  (quoted in section 1.8). There is no fixed-horizon control.
- **Hudson and Thames on E-mini (Singh and Joubert, about 2019).** Uses triple-barrier labels inside meta-labeling.
  See section 3.8.
- **No independent head-to-head found.** I found no peer-reviewed comparison of triple-barrier against
  fixed-horizon labels with cost-inclusive out-of-sample P&L. Classification accuracy on a triple-barrier label is
  not P&L. The label is only as good as its barrier choice, and those choices add trials.

**Assessment.** For the passive-order pilot, the triple-barrier outcome after a fill is a natural, pre-registerable
target. It is the realistic P&L of a "post, then exit at ±k ticks or at 60 s" rule. Its value is in defining the
measured quantity honestly, not in any predictive gain.

---

## 3. Meta-labeling (AFML ch. 3; Joubert 2022 and later papers)

### 3.1 Idea

Split the decision in two. A *primary* model (a rule, a fundamental view, or the simple rule "always join the best
bid") chooses the side. A *secondary* model learns when the primary model is right, and so decides whether to act
and how large to bet. The AFML summary puts it this way: "The goal of the primary model is to predict the sign of the
position’s return. The goal of the secondary model is to predict the accuracy of the primary model’s prediction"
(`lopezdeprado_2018_10reasons_jpm.txt`, lines 389-391). Also: "Its purpose is to determine whether we should act or
pass on the opportunity that has been presented" (lines 411-412). The intended trade-off is a primary model with
high recall and low precision, whose false positives the secondary model filters out (lines 403-409).

### 3.2 Equations

- Primary side s_i in {-1, +1} for event i. The label comes from section 2 (or a fixed horizon): y_i in {-1, 0, +1}.
- **Meta-label:** z_i = 1 if s_i y_i > 0 (the primary model was right), else 0. Many implementations instead use
  z_i = 1[s_i r_i > 0], where r_i is the return over the label span.
- **Secondary model:** p_i = P(z_i = 1 | X_i), from any probabilistic classifier. The features X_i can include the
  primary model's own state. Act if p_i > c, a declared threshold, and optionally size the bet m_i = g(p_i).
- **Classification metrics.** The fetched text defines precision as "the number of true positives relative to the
  total number of predicted positives" and recall as "the number of true positives relative to the total number of
  positives" (lines 397-399). The F1 score is "the harmonic average between precision and recall" (lines 403-404):
  F1 = 2 P R / (P + R).
- **Link from precision to P&L (my derivation).** Suppose an accepted trade wins +a (net of costs) when z = 1 and
  loses -b when z = 0. Then the expected P&L per accepted trade is pi(c) a - (1 - pi(c)) b, where pi(c) is the
  precision at threshold c. It is positive exactly when pi(c) > b / (a + b). Joubert (2022) says the "relationships
  between binary classification metrics and strategy performance are explained" (abstract only, see 3.8), so this is
  presumably covered there. I could not verify that.
- **Bet sizing.** AFML ch. 10 maps p to a size through a test statistic, z = (p - 1/2) / sqrt(p (1 - p)), with
  m = 2 Phi(z) - 1. [unverified: chapter 10 not fetched. Meyer, Barziy and Joubert (2023) study calibration before
  sizing (`ht_metalabeling_repo_readme.md`).]

### 3.3 Data, and whether one contract for 4 to 12 months is enough

Meta-labeling needs a primary rule's event list, a label per event, and features known at decision time. It needs
enough *primary events* to train a classifier and still test it once. For a passive-order pilot, the primary rule is
"post at the best bid or offer whenever condition A holds." Every posted order is an event, and the meta-label is
"this fill was non-toxic" (net 60-s markout > 0). Four months of one contract gives thousands to tens of thousands
of such events. Features such as queue position, depth imbalance and recent trade signs need mbp-10 (depth). Exact
queue position needs mbo. tbbo lacks depth beyond level 1.

**Pitfall specific to passive orders.** The meta-label exists only for orders that fill, and the fill itself depends
on the decision to keep the order resting. A secondary model trained on fills of an "always post" policy learns
P(non-toxic | filled, X). At deployment it decides *before* the fill, which changes which orders fill. If a model
cancels orders whose queue position was good, the remaining fills are a different population. The test has to
simulate the whole policy (post or cancel, then the fill model, then the markout). It cannot simply re-score the old
fills. This is a selection effect, and the sources do not discuss it for passive execution.

### 3.4 What it estimates or decides

It estimates P(primary is right | X) and decides to act or pass, and possibly the size. It does not choose the side.

### 3.5 Worked example (computed by hand)

A primary "always join" rule produces 1,000 fills. 45% of them are non-toxic, each worth a = +1.0 tick net. The
other 55% are toxic, each costing b = 1.2 ticks net (after fees).
- Primary alone: 0.45 x 1.0 - 0.55 x 1.2 = 0.45 - 0.66 = -0.21 ticks per fill, or -210 ticks in total.
- Break-even precision: b / (a + b) = 1.2 / 2.2 = 0.545.
- A secondary model at threshold c accepts 400 fills with precision 0.55: 0.55 x 1.0 - 0.45 x 1.2 = 0.55 - 0.54 =
  +0.01 ticks per fill, or +4 ticks in total. That is a 0.5-percentage-point precision margin over break-even (0.55 vs 0.545). With 400 fills
  and a per-fill sd near 1.1 ticks, the standard error is 1.1 / sqrt(400) = 0.055 ticks, so +0.01 is 0.18 standard
  errors. That is indistinguishable from zero. A meta-labeling gain that looks large in precision terms (0.45 to
  0.55) can still be untestable in P&L terms.
- Recall here is 220 / 450 = 0.49 (true positives accepted over all non-toxic fills), and F1 = 2(0.55)(0.49) /
  (0.55 + 0.49) = 0.52.

### 3.6 Pilot use: a testable hypothesis

- **H-ML1 (fill-toxicity filter).** Primary rule: join the best bid or offer whenever the spread is 1 tick. The
  secondary model is a frozen gradient-boosted classifier on decision-time features: queue ahead, level-1 and
  level-5 depth imbalance, last-5 trade signs, and seconds since the last price change. A declared threshold c sets
  a ceiling on the cancel rate. H0: the mean net 60-s markout per filled order under the filtered policy is less
  than or equal to that under the unfiltered policy.
- **Statistic.** The difference in mean net markout per posted order (not per fill, so cancelled orders count as
  zero), estimated by a policy simulation on held-out days. Use a HAC t or a day-block bootstrap. Report precision
  and recall as diagnostics only.
- **Sample.** The test set must hold enough accepted fills. For a 0.25-tick difference at sd 2 ticks, about 1,000 accepted
  fills per arm for an unpaired comparison, or about 500 paired differences (same days, same posted orders) (section 12). One test on data that never selected the model (V43).
- **Trial count.** 1 model x the number of thresholds c declared (for example 2) x feature-set variants (keep to 1).
  So 2 configurations, plus any primary-rule variants.

### 3.7 Compute

One LightGBM fit on 10^6 rows x 30 features with 200 trees took 5.6 s on 8 threads (measured,
`C2_AFML_lgb_probe.json`). A 45-split CPCV of one configuration takes about 4 minutes, and 100 configurations about
7 hours. Laptop-feasible. No GPU is needed.

### 3.8 Evidence

- **Lopez de Prado (2018).** "In my experience, meta-labeling ML models can deliver more robust and reliable outcomes
  than standard labeling models" (lines 430-431). This is an experience claim, not a test.
- **Joubert (2022), JFDS 4(3): 31-44, "Meta-Labeling: Theory and Framework".** From the abstract only (journal page,
  `joubert_2022_jfds_landing.html`): "The author also deconstructs meta-labeling into three components, using a
  controlled experiment to show how each component helps to improve strategy metrics." [unverified beyond the
  abstract; the full text is paywalled. A search snippet suggests the experiments use synthetic data, also
  unverified.]
- **Meyer, Joubert and Alfeus (2022), "Meta-Labeling Architecture"; Thumm, Barucca and Joubert (2023), "Ensemble
  Meta-Labeling"; Meyer, Barziy and Joubert (2023), "Calibration and Position Sizing".** Abstracts only. For example,
  "ensembles are especially beneficial when the underlying data consist of multiple regimes and are nonlinear in
  nature" (`thumm_barucca_joubert_2023_ensemble_landing.html`). All are from the same group, which sells the
  mlfinlab library. That is not independent evidence.
- **Singh and Joubert, "Does Meta-Labeling Add to Signal Efficacy?" (Hudson and Thames PDF, about 2019).** E-mini
  tick data from 2011 to 2019 [unverified: the saved text gives only the out-of-sample table captions, 2018-2019]. Out of sample, for mean reversion, "The precision jumps from 0.17 to 0.20 and the
  accuracy from 17% to 63%". For trend following, "The precision increases from 0.48 to 0.54"
  (`singh_joubert_metalabeling_efficacy.txt`, lines 601-602 and 687-688). The authors also state: "we manually
  tuned a few parameters to ensure that we have sufficient data points" and "We used up-sampling to balance these
  classes" (lines 505-511). The out-of-sample window is about one year per strategy (Tables 1 and 2, 2018-2019). The
  text gives no trading costs, no significance test and no count of trials. A precision of 0.20 on a mean-reversion
  strategy whose payoff structure is not shown says nothing about net P&L.
- **Man and Chan (2020, arXiv 2005.12483).** 464 trades of one strategy from 2013 to 2019, with a test set from
  Jan 2018 to Oct 2019. Table 4 gives "Sharpe Ratio 0.360 0.743 0.829" for the original strategy, meta-labeling without feature selection, and with feature selection (`man_chan_2020_feature_selection_metalabeling.txt`, line 436; the running text at lines 372-374 is split across two columns). The spread over 100 random seeds measures
  model randomness, not sampling error. The test set holds on the order of 100 trades (my estimate: 464 trades over seven years with a 22-month test window), and no costs are stated.
- **Not found.** I found no independent, peer-reviewed, cost-inclusive out-of-sample evaluation of meta-labeling on
  futures, and none on passive execution. A search on 2026-10-21 for 2023-2024 independent evaluations returned
  theses, vendor pages and abstracts.

**Assessment.** Meta-labeling is a sound idea as an *architecture*: a fixed, simple primary rule plus a learned filter
keeps the side decision out of the search. Its published support is thin, comes mostly from the method's
promoters, and is measured in precision rather than net P&L. For passive orders, the selection effect in 3.3 must be
handled by simulating the whole policy.

---

## 4. Sample uniqueness weights and the sequential bootstrap (AFML ch. 4)

### 4.1 Idea

When labels overlap in time, two consecutive samples are largely the same observation. A model then sees the same
information many times and overweights it. Uniqueness measures how much of each label's span is shared with other
labels, and the weights give less influence to shared information. "Two labels 𝑦𝑖 and 𝑦𝑗 are concurrent at observation 𝑡 when both are a function of at least one ... common return" (a stray symbol between "one" and "common" is dropped) (`lopezdeprado_2018_10reasons_jpm.txt`, lines
452-453).

### 4.2 Equations (lines 455-473 of the summary paper; garbled by pdftotext and restated here)

- Indicator 1_{t,i} = 1 if label i's span [t_{i,0}, t_{i,1}] includes return bar t.
- Concurrency c_t = sum_i 1_{t,i}, the number of labels using bar t.
- Uniqueness of label i at t: u_{t,i} = 1_{t,i} / c_t. The source: "The uniqueness of a label 𝑖 at time 𝑡 is
  𝑢𝑡,𝑖 = 1𝑡,𝑖 𝑐𝑡−1" (line 460).
- Average uniqueness: u_bar_i = (sum_t u_{t,i}) / (sum_t 1_{t,i}).
- Return-attribution weight: w~_i = | sum_{t = t_{i,0}}^{t_{i,1}} r_{t-1,t} / c_t |, normalised as
  w_i = w~_i I / sum_j w~_j, so the weights sum to the number of labels I.
- **Sequential bootstrap.** Draw samples one at a time. At each step, each candidate's probability is proportional
  to its average uniqueness given the samples already drawn. The source says this "can significantly increase the
  average uniqueness of samples" (lines 486-491).
- **A useful by-product (my addition).** n_eff = sum_i u_bar_i is a rough effective number of non-overlapping labels.
  It is the right order of magnitude for the "sample" in a power calculation.

### 4.3 Data, and whether 4 months is enough

The method needs only label spans and bar returns, which come from section 2. It works with any schema.

### 4.4 What it decides

Training weights, and the effective sample size.

### 4.5 Worked example (computed; key `uniqueness_toy`)

Six bars with returns r = (+0.002, -0.001, +0.003, +0.001, -0.002, +0.004). Label A spans bars 1-3, B spans 2-4 and
C spans 5-6.
- Concurrency: c = (1, 2, 2, 1, 1, 1).
- u_bar_A = (1/1 + 1/2 + 1/2) / 3 = 0.667, u_bar_B = (1/2 + 1/2 + 1/1) / 3 = 0.667, u_bar_C = 1.
- w~_A = |0.002/1 - 0.001/2 + 0.003/2| = |0.002 - 0.0005 + 0.0015| = 0.003. w~_B = |-0.0005 + 0.0015 + 0.001| = 0.002.
  w~_C = |-0.002 + 0.004| = 0.002.
- Normalised to I = 3: w_A = 3(0.003)/0.007 = 1.286, w_B = w_C = 0.857. n_eff = 0.667 + 0.667 + 1 = 2.33 of 3 labels.

**Pilot scale (assumed rates, stated).** Suppose 2,000 posted orders a day over a 23-hour session, which is one every
41.4 s on average, with a 60-s markout label. The mean number of other labels covering a bar is H / spacing = 1.45,
so u_bar = E[1 / c_t] is about 0.53 for Poisson-like arrivals and 0.69 for evenly spaced orders; n_eff is then 0.5 to
0.7 of the label count before bursts, which push it lower. With bursts, where orders cluster at busy times, overlap is far higher. n_eff, not the raw
count, should feed the power calculation in section 12.

### 4.6 Pilot use

This is a weighting choice, not a hypothesis. Pre-register one scheme (for example average-uniqueness weights times
|attributed return|). If two schemes are compared, that comparison adds 1 configuration to N. Report n_eff alongside
every test statistic.

### 4.7 Compute

O(labels x span length). Seconds for 10^5 labels.

### 4.8 Evidence

The only evidence I found is the method's own Monte Carlo claim (above). I found no independent study that shows
uniqueness weighting improves out-of-sample results. The statistical point behind it, that overlapping observations
overstate the sample size, is standard (the Newey-West and Hansen-Hodrick logic), and HAC standard errors address it
in inference.

**Assessment.** Use n_eff and HAC inference in any case. The weights themselves are optional, low cost, and count as
1 configuration if compared.

---

## 5. Purged k-fold cross-validation with an embargo (AFML ch. 7)

### 5.1 Idea

Ordinary k-fold cross-validation assumes independent rows. With overlapping labels and serially correlated features,
a training row next to a test row carries almost the same information, so the test score is inflated. The source
explains the leak: "(1) Because of the serial correlation, 𝑋𝑡 ≈ 𝑋𝑡+1 ; (2) because labels are derived from
overlapping data points, 𝑌𝑡 ≈ 𝑌𝑡+1 . Then, placing t and t+1 in different sets leaks information"
(`lopezdeprado_2018_10reasons_jpm.txt`, lines 496-499). The fix has two parts. *Purging* removes training rows
whose label spans overlap any test label span. The *embargo* also removes training rows that start shortly after a
test block.

### 5.2 Equations

Test label j has span [t_{j,0}, t_{j,1}]. A training label i "overlaps" if any of the three conditions holds (lines
510-512):

    (1) t_{j,0} <= t_{i,0} <= t_{j,1};   (2) t_{j,0} <= t_{i,1} <= t_{j,1};   (3) t_{i,0} <= t_{j,0} <= t_{j,1} <= t_{i,1}.

Purging drops every such i. For the embargo of length h, the source says: "We can implement this embargo period h
by setting 𝑌𝑗 = 𝑓 [[𝑡𝑗,0 , 𝑡𝑗,1 + ℎ]] before purging. A small value ℎ ≈ .01𝑇, where 𝑇 is the number of bars, often
suffices to prevent all leakage" (lines 521-523). The embargo is needed only *after* a test block. Training rows
that end before the test begins "contain information that was available at the testing time" (lines 518-520).

**Bias bound (Li 2026, arXiv 2609.29530; a single-author preprint, not peer reviewed).** Define delta as the distance
from a test point to the nearest training point in its future, and beta_mix(delta) as the beta-mixing coefficient
(how fast dependence dies out with lag). Li proves that "under β-mixing the leakage bias at a test point is at most
2M βmix (δ)" (`arxiv_2609_29530_trinity_validation.txt`, line 23; M bounds the loss). Purging and embargo work by
increasing delta. In words: "purged k-fold with an embargo pays in distance instead, which is cheap when the process
forgets quickly but cannot repair the part of causality demanded by non-stationarity" (lines 27-29). The practical
rule given is: "All gaps/purges/embargoes should be denominated in H + cτ with c ≈ 2–3", where H is the label
horizon and tau the dependence scale (line 742).

### 5.3 Data, and whether 4 months is enough

The method needs label spans and timestamps. With 4 months of one contract and k = 5 to 10 folds, each fold holds
1.7 to 3.4 weeks. That is enough for a 60-s label horizon. It is short against volatility clustering, which has long
memory, and it covers few regimes.

### 5.4 What it decides

How the sample is split into training and test sets (the protocol). It estimates nothing.

### 5.5 Worked example (assumed rates; key `purge_toy`)

2,000 events a day over 84 sessions gives T = 168,000 labels with a mean spacing of 41.4 s and H = 60 s.
- **Purge.** Each test-block boundary removes the training labels within 60 s of it, about 1.45 labels per boundary
  at the mean rate (60 / 41.4). That is negligible.
- **AFML embargo.** h = 0.01 T = 1,680 events, about 0.84 sessions. That is far more than the 60-s horizon needs, but
  roughly the scale of intraday volatility clustering.
- **Li's rule.** H + c tau with c = 2-3. If the autocorrelation of the losses (not of the raw returns) has a
  half-life tau of 30 minutes, the gap is about 60 s + 60-90 min.
- **Practical simplification for CME.** Make every fold a set of whole Globex sessions. Each session ends at the
  16:00 CT maintenance halt (an assumption about the session calendar to confirm in Part B). A 60-s label then never
  crosses a session boundary, so purging is automatic, and a 1-session embargo after each test block covers the
  slower dependence.

### 5.6 Pilot use

This is a protocol, not a hypothesis. It adds 0 configurations if k, H and h are declared before any computation.
One pre-registerable *diagnostic* is worth running:
- **H-CV0 (leak test).** Train the frozen pipeline on a placebo target: the meta-label shifted by a random number of
  days, or the true features paired with labels from another session. Under the chosen purged scheme the
  out-of-sample IC or AUC must be within 2 standard errors of 0 (AUC 0.5). If it is not, the protocol leaks. Li's
  pure-noise experiment shows the size of the effect: Table rows "Shuffled 5-fold +0.318 ± 0.012", "Contiguous 5-fold +0.004 ± 0.012" and "Purged 5-fold (gap = H) +0.000 ± 0.012" (lines 719-722). This check adds 0 to N.

### 5.7 Compute

Splitting is negligible. The cost is k model fits per configuration (section 3.7).

### 5.8 Evidence

- **Theory and simulation support the mechanism.** Li (2026) shows on pure noise that shuffled k-fold produces a
  spurious IC of +0.32, while contiguous and purged folds do not. The same paper argues that under
  non-stationarity, "expanding walk-forward" is the honest choice when "expected live performance" is to be quoted
  (lines 750-751). That is the situation of a single final test.
- **AFML's own claim.** h ≈ 0.01T "often suffices to prevent all leakage". This is an experience claim (line 523).
- **Independent evidence.** The leak itself is well established (overlapping-observation inference). I found no
  study showing that purging *changes a trading decision* out of sample. It is a hygiene step, and its benefit is
  avoiding false positives.

**Assessment.** Use it for model selection inside the training period. Use a single forward hold-out (walk-forward
or a reserved block) for the one final test (V43).

---

## 6. Combinatorial purged cross-validation, CPCV (AFML ch. 12)

### 6.1 Idea

Walk-forward produces one backtest path, "which can be easily overfit" (line 539). CPCV splits the sample into N
contiguous groups. It tests on every combination of k groups and trains on the rest (purged and embargoed), then
stitches the test predictions into phi backtest paths. Each path covers the whole sample once. The result is a
*distribution* of Sharpe ratios rather than a single number: "A key advantage of CPCV is that it allows us to derive
a distribution of Sharpe ratios, as opposed to a single (likely overfit) Sharpe ratio estimate" (lines 605-606).

### 6.2 Equations (lines 566-597, restated)

- N groups. Groups 1 to N-1 have size floor(T/N), and the last group takes the remainder.
- Number of train/test splits: C(N, k) = N! / (k! (N - k)!). The source writes it as C(N, N-k), which is the same
  number.
- Each split tests k groups, so k C(N, k) group-tests in all, spread evenly over the N groups. Each group is
  therefore tested phi times:

      phi[N, k] = (k / N) C(N, k) = C(N - 1, k - 1).

  The source gives the same formula, garbled by pdftotext over lines 583-590. The identity
  (k/N) C(N, k) = C(N-1, k-1) is the step that makes "each group tested phi times" exact.
- Path p (p = 1..phi) takes, for each group g, the prediction from the p-th split that tested g. Each path is a full
  out-of-sample sequence. The per-path Sharpe ratios SR_1..SR_phi give an empirical distribution.
- Training fraction per split: (N - k)/N. Larger k gives more paths but less training data.

### 6.3 Data, and whether 4 months is enough

The same as section 5. With 84 sessions, N = 6 gives 14-session groups, and N = 12 gives 7-session groups. Paths
share their training data heavily, so the phi Sharpe ratios are strongly correlated and are *not* phi independent
samples.

### 6.4 What it decides or estimates

It estimates the dispersion of a fixed configuration's out-of-sample performance across paths. It also supplies the
in-sample and out-of-sample matrix that PBO and CSCV and the deflated Sharpe ratio work need, which the program
already uses.

### 6.5 Worked example (computed; key `cpcv`)

| N | k | splits C(N,k) | paths phi | train fraction |
|---|---|---|---|---|
| 6 | 2 | 15 | 5 | 0.667 |
| 10 | 2 | 45 | 9 | 0.800 |
| 10 | 3 | 120 | 36 | 0.700 |
| 12 | 2 | 66 | 11 | 0.833 |
| 16 | 4 | 1,820 | 455 | 0.750 |

Check for N = 6, k = 2: C(6,2) = 6 x 5 / 2 = 15 splits. Each group is in C(5,1) = 5 of them, so phi = 5. That matches
the source: "There are ( ) = 15" splits, and each group "forms part of 𝜑[6,2] = 5 testing sets" (lines 592-596; the binomial symbol is lost in pdftotext). The
script confirms that every group is tested exactly 5 times. Cost: 15 fits per configuration for N = 6, k = 2, and
1,820 for N = 16, k = 4.

### 6.6 Pilot use

CPCV is a protocol for the *selection* stage. It adds 0 configurations, but its choice of (N, k) must be declared.
Two pre-registerable uses:
- **H-CV1 (stability).** For the single frozen configuration, report the fraction of CPCV paths with a net mean
  markout above 0. Report it as a descriptive diagnostic, not as the test.
- **Feed PBO.** If S configurations are compared (for example 2 meta-label thresholds x 3 barrier settings = 6),
  CPCV supplies the S x paths performance matrix for PBO, and the deflated Sharpe ratio uses N_total = 538 + S.

### 6.7 Compute

Fits = configurations x C(N, k). For S = 6, N = 10 and k = 2 that is 270 LightGBM fits. At about 6 s each (10^6 rows,
measured), that is 27 minutes on the laptop. With N = 16 and k = 4 it is 10,920 fits, about 18 hours, which is
still feasible overnight. A cloud CPU box would cut this only linearly. GPU training of gradient-boosted trees on a
4 GB RTX 3050 is possible but not needed at this size.

### 6.8 Evidence

- **Arian, Norouzi Mobarekeh and Seco (2024), *Knowledge-Based Systems*, DOI 10.1016/j.knosys.2024.112477.** A
  synthetic controlled comparison of out-of-sample methods. I could not retrieve the full text (Elsevier and SSRN are
  blocked from this machine, and OpenAlex lists no open-access copy). Its finding, as reported by a citing paper:
  "finding that Combinatorial Purged Cross-Validation shows superiority in mitigating over-fitting risks, though
  walk-forward remains the industry standard for realistic trading simulation" (`arxiv_2512_12924.txt`, lines
  182-184). [unverified: from a citing paper, not the full text]
- **Li (2026).** Places CPCV with purged k-fold: good for model comparison when stationarity is credible, but it
  cannot fix non-stationarity (line 745: "Stationarity credible, goal is model comparison/tuning → purged k-fold +
  embargo (or CPCV)").
- **Deep, Deep and Lamptey (2025, arXiv 2512.12924).** An honest walk-forward protocol with costs
  on 100 US equities over 34 test periods: "We report statistically insignificant aggregate results (p-value 0.34)"
  (lines 30-31). This shows that strict protocols tend to turn apparent edges into nulls. It does not compare against
  CPCV.
- **Not found.** I found no evidence that CPCV-selected strategies earn more *live* than walk-forward-selected ones.

**Assessment.** Use CPCV (or CSCV, which the program already runs) to *diagnose* overfitting across the configuration
set. Keep a single untouched forward block for the decisive test. The paths are correlated, so a "distribution of
Sharpe ratios" must not be read as independent replications.

---

## 7. Wavelets: Haar and Daubechies filters, the MODWT, and multiresolution analysis (Gencay, Selcuk and Whitcher 2002; Percival and Walden 2000)

### 7.1 Idea

A Fourier transform splits a series by frequency but loses *when* things happen. A wavelet transform splits it by
*scale* (roughly, period ranges such as 2-4 s, 4-8 s, 8-16 s, and so on) while keeping time location. The discrete
wavelet transform (DWT) does this with a pair of filters: a high-pass "wavelet" filter h, which takes differences of
local averages, and a low-pass "scaling" filter g, which takes local averages. Applying them repeatedly to the
smoothed output gives one set of coefficients per scale. The DWT downsamples by 2 at every level. The maximal overlap
DWT (MODWT) does not, so it keeps one coefficient per time point at every level. Percival's slides sum up the
difference: "unlike the DWT, MODWT is defined naturally for all samples sizes", and "MODWT-based MRA has details and
smooths that shift along with X" (`percival_2018_modwt_slides.txt`, lines 20-25). A *multiresolution analysis*
(MRA) writes the series as a sum of detail series D_j, one per scale, plus a smooth S_J.

### 7.2 Equations

**Filters.** A wavelet filter {h_l}, l = 0..L-1, has even length L, sums to 0, has unit energy (sum h_l^2 = 1) and
is orthogonal to its even shifts. The scaling filter is its quadrature mirror, g_l = (-1)^{l+1} h_{L-1-l}.
- Haar (L = 2): h = (1/sqrt2, -1/sqrt2), g = (1/sqrt2, 1/sqrt2).
- Daubechies D(4) (L = 4): g = (1 + sqrt3, 3 + sqrt3, 3 - sqrt3, 1 - sqrt3) / (4 sqrt2), the extremal-phase filter.
  The "least asymmetric" LA(8) is the usual choice when coefficients must line up in time with events. (Standard
  values from Percival and Walden 2000; the book was not fetched, so [unverified against the book].)

**MODWT filters.** These are rescaled DWT filters: "h̃j,l = hj,l /2j/2 and g̃j,l = gj,l /2j/2" (Percival slides,
line 45), where h_{j,l} is the level-j equivalent filter of width "Lj = (2j − 1)(L − 1) + 1" (line 42). The
exponents read 2^{j/2} and 2^j, lost in pdftotext.

**Pyramid algorithm.** With V~_0 = X, for j = 1..J:

    W~_{j,t} = sum_{l=0}^{L-1} h~_l V~_{j-1, t - 2^{j-1} l mod N},   V~_{j,t} = sum_{l=0}^{L-1} g~_l V~_{j-1, t - 2^{j-1} l mod N},

with h~_l = h_l / sqrt2 and g~_l = g_l / sqrt2. This is from the slides (lines 484-485, garbled). The "mod N" makes
the filter circular, so the first L_j - 1 coefficients at level j wrap around to the end of the series. These are the
*boundary coefficients*. The slides note that the "algorithm requires N log2(N ) multiplications, which is the same
as needed by fast Fourier transform algorithm" (line 487).

**MRA and energy.** X = sum_{j=1}^{J0} D~_j + S~_{J0} (slides, line 163, garbled in the extraction). Energy is preserved:
||X||^2 = sum_j ||W~_j||^2 + ||V~_{J0}||^2 (slides, lines 372-376, garbled in the extraction), which gives a scale-by-scale analysis of the sample variance
(lines 377-384). D~_j is obtained by running the *inverse* pyramid on W~_j alone (all other levels set to 0). That
inverse step uses V~_{j-1,t} = sum_l h~_l W~_{j, t + 2^{j-1} l} + sum_l g~_l V~_{j, t + 2^{j-1} l} (lines 491-494).
Note the **plus** sign in the time index: the inverse looks *forward*.

**Scale and period.** Level j coefficients respond mainly to periods between 2^j and 2^{j+1} sampling intervals. On
1-second data, j = 1 covers 2-4 s, j = 3 covers 8-16 s, and j = 6 covers 64-128 s, matching the 1, 10 and 60 s
markout horizons.

**Causality (the key practical point; my derivation, confirmed numerically).** The forward coefficients W~_{j,t}
depend only on X_t, X_{t-1}, ..., X_{t-L_j+1}. Apart from the circular boundary they are *causal* and can be used as
real-time features. The MRA details D~_j and the smooth S~_J apply the forward filter and then the forward-looking
inverse. They are two-sided (zero-phase) filters of X, so D~_{j,t} depends on future values. Any feature built from an
MRA, or from denoising and reconstruction over the whole sample, leaks future data.

### 7.3 Data, and whether 4 months is enough

Wavelets need a regularly sampled series. The choice is a clock (1-s mid, 1-s signed volume) or an event clock
(per-trade signs, per-book-update OFI). tbbo gives trades and BBO. mbp-10 adds depth-based series such as
imbalance. Four months of 1-s data (about 7.0 million points) supports J = 12 levels (2^12 s, about 68 min) with millions
of coefficients per level. That is ample for estimating wavelet variance and for features.

### 7.4 What it estimates or decides

- The *wavelet variance* nu^2_j (energy per scale). It estimates how variance is spread across time scales, a
  scale-based spectrum.
- *Features*: causal W~_{j,t} at chosen levels.
- An MRA as a description of the series, for plots and explanation only.

### 7.5 Worked example (computed; Haar MODWT, J = 2, circular; key `haar_modwt_x8`)

Take X = (4, 6, 10, 12, 8, 6, 5, 5). For Haar, h~ = (1/2, -1/2) and g~ = (1/2, 1/2).
- Level 1: W~_{1,t} = (X_t - X_{t-1})/2 and V~_{1,t} = (X_t + X_{t-1})/2, with X_{-1} = X_7 = 5 (circular).
  W~_1 = (-0.5, 1, 2, 1, -2, -1, -0.5, 0) and V~_1 = (4.5, 5, 8, 11, 10, 7, 5.5, 5).
  For example, W~_{1,0} = (4 - 5)/2 = -0.5 and W~_{1,2} = (10 - 6)/2 = 2.
- Level 2 (lag 2^{1} = 2): W~_{2,t} = (V~_{1,t} - V~_{1,t-2})/2, which gives
  W~_2 = (-0.5, 0, 1.75, 3, 1, -2, -2.25, -1). For example, W~_{2,2} = (8 - 4.5)/2 = 1.75. And
  V~_{2,t} = (V~_{1,t} + V~_{1,t-2})/2 = (5, 5, 6.25, 8, 9, 9, 7.75, 6).
- Energy: sum X^2 = 16 + 36 + 100 + 144 + 64 + 36 + 25 + 25 = 446, and ||W~_1||^2 + ||W~_2||^2 + ||V~_2||^2 = 446,
  as the identity requires.
- MRA: D~_1 = (-0.75, -0.5, 0.5, 1.5, -0.5, -0.25, -0.25, 0.25), D~_2 = (-1.3125, -0.5625, 1.4375, 2.0625, 0.5625,
  -0.6875, -0.6875, -0.8125) and S~_2 = (6.0625, 7.0625, 8.0625, 8.4375, 7.9375, 6.9375, 5.9375, 5.5625).
  D~_1 + D~_2 + S~_2 = X exactly (maximum error 0).
- **Leak test.** Change only the last value, X_7, from 5 to 9, and record which outputs change (key
  `haar_causality`). W~_1 changes at t = 7 and at t = 0 (circular wrap). W~_2 changes at 7 and at 0, 1, 2 (all wrap).
  So no coefficient *before* t = 7 changes except through the boundary. But D~_1 changes at t = 6 (and 0, 7), and
  S~_2 changes at t = 4, 5, 6 (and 0, 1, 2, 7). The MRA components at earlier times move when a *later* value
  changes. That is look-ahead.

### 7.6 Pilot use: a testable hypothesis

- **H-W1 (scale of adverse selection).** Compute causal LA(8) MODWT coefficients of 1-s signed trade volume for
  j = 1..6. Discard the first L_j - 1 values of each day so that no wrap-around reaches across sessions. Their
  rolling energies over the last 5 minutes are added to the frozen fill-toxicity classifier (H-ML1). H0: no change in
  held-out log loss (statistic as in H-FD1).
- **Descriptive companion (not a test).** The wavelet variance of 1-s mid returns by scale tells whether the 1-s and
  10-s markouts are dominated by bid-ask bounce (energy concentrated at j = 1) or by information (energy at coarser
  scales).
- **Sample.** As for H-FD1.
- **Trial count.** 1 configuration per (filter, J, window) combination. Declare one: LA(8), J = 6, 5-minute window.
  Adding Haar makes 2.

### 7.7 Compute

A Haar MODWT with J = 8 on 7.2 million points took 0.69 s (measured, numpy). It held 9 arrays of 7.2 million doubles,
0.52 GB (key `modwt_7.2M_J8_memory_GB`). LA(8) needs about 4 times the multiplications, a few seconds. With 4 months
in memory at J = 12 the arrays reach about 0.75 GB, which fits in 14 GB. Process day by day if needed. No GPU is
needed.

### 7.8 Evidence

- **Hasumi and Kajita (2018), JCER Discussion Paper 148.** On the S&P 500: "We show that inappropriate procedures for
  applying the wavelet decomposition to time series data easily lead to data leakage" and "wavelet-based forecasting
  in which the time series data are processed appropriately cannot outperform even a naive prediction"
  (`hasumi_kajita_2018_wavelet_leakage.txt`, lines 35-40; the same sentences are on the landing page). Their Table 1
  (leaky, whole test set decomposed) shows a direction accuracy of 0.7302. Their Table 2 (sequential, causal
  decomposition) shows 0.4841 to 0.5238 (lines 214-216 and 348-353).
- **Gencay, Selcuk and Whitcher (2001), *Physica A* 289: 543-556.** A MODWT-based intraday seasonality filter for FX
  volatility (abstract only, Bilkent record): "Our methodology is based on a wavelet multi-scaling approach which
  decomposes the data into its low- and high-frequency components through the application of a non-decimated
  discrete wavelet transform" (`bilkent_gsw2001_record.txt`). This is a descriptive volatility-modelling use, not a
  trading test. [Full text not retrieved.]
- **The book (Gencay, Selcuk and Whitcher 2002, Academic Press).** Not retrieved. [unverified]
- **Not found.** I found no cost-inclusive, out-of-sample evidence that wavelet features improve intraday futures
  trading at retail latency. The stock-prediction literature that reports large gains is the setting Hasumi and
  Kajita warn about. Search snippets also mention a 2024 multilevel wavelet-LSTM paper claiming to avoid leakage
  [unverified: snippet only].

**Assessment.** Wavelets are a useful *descriptive* tool for which time scales carry the markout variance, and they
give cheap causal multiscale features. Published forecasting gains are largely leakage. Only causal coefficients,
never MRA components, may enter a feature set.

---

## 8. Wavelet denoising (Donoho and Johnstone shrinkage)

### 8.1 Idea

Transform the noisy series. Shrink the small wavelet coefficients, which are mostly noise, toward 0. Keep the large
ones, which carry signal. Then invert the transform. Donoho's abstract describes shrinking all the empirical wavelet coefficients "of d towards 0 by an amount" sqrt(2 log n) sigma / sqrt(n). The square roots and sigma are lost in the extracted text, so the amount is restated (`donoho_1995_denoising_soft_threshold.txt`, lines 12-14).

### 8.2 Equations

- Model: d_i = f(t_i) + sigma z_i, z_i i.i.d. N(0, 1) (abstract, lines 8-11).
- Soft threshold: eta_t(y) = sgn(y) (|y| - t)_+. Hard threshold: y 1(|y| > t). The source gives "t(y) =
  sgn(y)(jyj t)+" (line 83, garbled).
- Universal threshold: t_n = sigma sqrt(2 log n), on coefficients scaled to unit noise. The source states it at line 86, where the extraction garbles it, with a 1/sqrt(n) factor from its normalisation. sigma is usually
  estimated as the median absolute finest-level coefficient divided by 0.6745. That estimator is standard but I did
  not quote it from the fetched text, so it is [unverified].
- *Why sqrt(2 log n)*: for n i.i.d. N(0, 1) variables, P(max |z_i| <= sqrt(2 log n)) -> 1. A threshold at that level
  therefore kills pure noise with high probability. The source states this at line 383 (garbled in the extraction).

### 8.3 Data, and whether 4 months is enough

The same as section 7. The causality problem is worse here: denoising a whole window and reading its last point is a
two-sided filter at every interior point.

### 8.4 What it estimates

A smooth estimate f^ of the signal.

### 8.5 Worked example (computed; key `soft_threshold_toy`)

Coefficients c = (0.1, -0.3, 2.5, 0.2, -0.05, -1.8, 0.4, 0.0), n = 8. The sorted absolute values are 0, 0.05, 0.1,
0.2, 0.3, 0.4, 1.8 and 2.5, so the median is (0.2 + 0.3)/2 = 0.25. sigma^ = 0.25 / 0.6745 = 0.3706, and
t = 0.3706 x sqrt(2 ln 8) = 0.3706 x 2.0393 = 0.756. Soft thresholding gives 2.5 -> 1.744 and -1.8 -> -1.044, and
sets every other coefficient to 0.

### 8.6 Pilot use

I see no pre-registerable hypothesis that denoising adds to an order-book classifier, which can learn its own
filtering. If included, it is 1 configuration (one wavelet, one threshold rule, applied causally on a trailing
window, keeping only the last reconstructed point).

### 8.7 Compute

Negligible: the same cost as one MODWT.

### 8.8 Evidence

- The statistical optimality results (near-minimax risk, lines 163 and 413-414) are for estimating a smooth f from
  i.i.d. Gaussian noise. They are not about forecasting returns.
- A 2018 study of wavelet denoising before forecasting the M3 yearly series reportedly found no gain [unverified:
  search snippet only, not retrieved].
- Hasumi and Kajita (section 7.8) apply directly. Causal, sequential processing removed the apparent gain.

**Assessment.** Skip for the order-book program.

---

## 9. Spectral methods: the periodogram

### 9.1 Idea

Any stationary series can be written as a sum of sinusoids. The *spectrum* S(f) says how much variance sits at each
frequency f. The periodogram is the raw sample estimate of it. Its use here is to find and measure periodic
structure, such as a daily cycle in volatility or activity, and to see long memory (power rising toward f = 0).

### 9.2 Equations

For x_0..x_{n-1} (demeaned), the Fourier frequencies are f_k = k/n cycles per sample, k = 0..floor(n/2), and

    X_k = sum_{t=0}^{n-1} x_t e^{-i 2 pi f_k t},   I(f_k) = |X_k|^2 / n.

- Parseval: sum_t x_t^2 = (1/n) sum_{k=0}^{n-1} |X_k|^2, so the periodogram ordinates partition the sample
  variance.
- For a stationary series, E I(f) -> S(f), but Var I(f) is approximately S(f)^2 and does not shrink with n. The raw
  periodogram is inconsistent, so it is smoothed or averaged. SciPy's Welch estimator "computes an estimate of the
  power spectral density by dividing the data into overlapping segments, computing a modified periodogram for each
  segment and averaging the periodograms" (`scipy_welch_docs.txt`). (The inconsistency and the chi-squared
  distribution with 2 degrees of freedom are standard results, cited from memory [unverified here].)
- For long memory (section 1), S(f) ~ C f^{-2d} near 0 (Hurvich handout, line 169). A regression of log I(f_k) on
  log f_k at low frequencies (the GPH method) estimates d. That is the time-series estimate of d, distinct from
  AFML's d*.

### 9.3 Data, and whether 4 months is enough

The method needs a regularly sampled series, for example 1-minute absolute returns, 1-minute trade counts, or the
fill rate per minute of a simulated order. With 84 sessions of 1,380 one-minute bars (n = 115,920), the daily
frequency is resolved 84 times over. That is ample.

### 9.4 What it estimates

S(f). In particular, the peaks at 1/day and its harmonics, and the slope near 0.

### 9.5 Worked example

*By hand:* x = (1, 0, -1, 0, 1, 0, -1, 0), a cosine of period 4, with n = 8. At k = 2 (f = 2/8 = 1/4),
e^{-i 2 pi t/4} = (-i)^t, so X_2 = 1(1) + (-1)(-1) + 1(1) + (-1)(-1) = 4, and I(1/4) = 16/8 = 2. By symmetry
|X_6| = 4, and every other X_k = 0. Parseval check: (16 + 16)/8 = 4 = sum x_t^2. All the variance sits at period 4.

*Computed (key `periodogram_top3`):* the synthetic series has 60 days of 1,380 one-minute bars, an imposed daily
U-shape in volatility, random daily volatility levels and t(5) shocks. The three largest periodogram ordinates of the
demeaned absolute returns are at periods of 1,380 minutes (1 day), 27,600 minutes (20 days, from the random daily
volatility levels) and 690 minutes (half a day, the second harmonic). That is the pattern Andersen and Bollerslev
describe for real data (section 10).

### 9.6 Pilot use

The periodogram is diagnostic. Before any test, compute the periodogram of the per-minute fill rate and the
per-minute mean 60-s markout to decide how many harmonics P the periodicity model in section 10 needs. It adds 0 to
N if P is fixed by a declared rule (for example, the smallest P whose residual periodogram shows no peak at 1/day and
its first 4 harmonics above the 99% chi-squared band).

### 9.7 Compute

One FFT of 115,920 points takes milliseconds, and one of 7.2 million points under a second. No GPU is needed.

### 9.8 Evidence

The periodogram is a standard estimator, and the question is what it is applied to. Its role in this field is
established by Andersen and Bollerslev's work (section 10). On their data, the daily periodicity dominates the
autocorrelation function of absolute returns: "the implementation of this idea is obscured by the strong intradaily
periodicity" (`andersen_bollerslev_1996_nber_w5752.txt`, lines 894-895).

---

## 10. Intraday periodicity and seasonality (Andersen and Bollerslev 1997; the flexible Fourier form; the wavelet filter of Gencay et al. 2001)

### 10.1 Idea

Intraday volatility, volume, spreads and fill rates follow a strong and repeatable daily shape. On CME equity
futures this includes the US cash open and close, the 08:30 ET releases, the Asian and European opens, and the
pre-halt lull. If this shape is not removed, it shows up as spurious "predictability": any feature correlated with
the time of day will appear to forecast fills and markouts. Andersen and Bollerslev model returns as a daily
volatility level times a deterministic intraday shape times noise, and estimate the shape with a smooth Fourier
series in the time of day.

### 10.2 Equations

**Model.** Yan (2021) restates Andersen and Bollerslev (1997) as

    r_{t,n} = sigma_t s_n z_{t,n} / sqrt(N),

"where 𝜎𝑡 is the conditional daily volatility at day 𝑡, 𝑠𝑛 is the intraday volatility periodicity during the period
of 𝑟𝑡,𝑛 and 𝑧𝑡,𝑛 is an iid series of zero mean and unit variance" (`arxiv_2111_02376_mcgarch.txt`, lines 572-574). The
shape is periodic, s_{n+jN} = s_n, and normalised so that sum_n s_n^2 / N = 1 (lines 574 and 593-594, garbled).

**Estimation (the flexible Fourier form).** Take logs of the squared standardised return:

    x_{t,n} = log( r_{t,n}^2 N / sigma_t^2 ) = log s_n^2 + log z_{t,n}^2,

and regress x on a smooth function of the time of day n/N:

    log s_n^2 ~= mu_0 + mu_1 (n/N) + mu_2 (n/N)^2 + sum_{p=1}^{P} [ gamma_p cos(2 pi p n / N) + delta_p sin(2 pi p n / N) ] + sum_k lambda_k I_k(t, n).

The I_k are dummies for announcement windows. Then s^_n = exp(f^_n / 2), renormalised so that the mean of
s^2 equals 1. This is the standard A&B (1997) appendix form as described in later literature. I did not fetch A&B
(1997) itself, so the exact normalising constants in their equation are [unverified]. What is verified: A&B used "a
flexible Fourier transform to estimate the intraday volatility periodicity component 𝑠𝑛" (Yan, lines 584-585). The R
package `highfrequency` implements it with cosine and sine counts P1 = P2 = 5 by default: "the number of cosinus
terms used in the flexible Fourier specification of the periodicity function, see Andersen et al. (1997) for details.
Default = 5" (`rdoc_highfrequency_spotvol.txt`).

**Robust variants.** Boudt, Croux and Laurent (2011) make the estimate robust to jumps (via the `highfrequency`
docs; not fetched).

**Wavelet alternative (Gencay, Selcuk and Whitcher 2001).** This uses the MODWT smooth or details to separate the
intraday cycle from lower frequencies. It is "simple to calculate, does not depend on a particular model selection
criterion" (abstract, `bilkent_gsw2001_record.txt`). Note: an MRA-based seasonal filter is two-sided (section 7.2).
It is fine for describing data, but not for real-time standardisation. Andersen and Bollerslev make the same point
about their own low-pass filter: "the low-pass filtering technique developed below is based on a two-sided weighted
average of both past and future absolute returns" (NBER w5752, lines 900-901), whereas the flexible Fourier form
"procedures are directly applicable in a forecasting context" (line 899).

### 10.3 Data, and whether 4 months is enough

The method needs a returns, activity or fill series per intraday bin, plus a daily volatility estimate sigma_t (for
example a GARCH or realised-volatility proxy from trailing days only). Four months gives about 84 observations per
bin, enough for a 2P + 3 parameter smooth curve (P = 4 gives 11 parameters against about 100,000 observations).
Announcement dummies need the release calendar and at least about 15 to 20 occurrences per announcement type in
the sample. For monthly releases, 4 months gives only 4, too few to estimate separately. That is a reason to extend
the sample to 12 months, or to group announcements.

### 10.4 What it estimates

The deterministic intraday shape s_n, and from it standardised returns or activity.

### 10.5 Worked example (computed; key `fff_fit`)

Synthetic: 60 days x 1,380 one-minute bars with true shape s_n^2 proportional to 1 + 0.8 cos(2 pi n/N) +
0.3 cos(4 pi n/N), random daily levels and t(5) shocks. A flexible Fourier regression with P = 2 (7 parameters) on
82,800 log squared standardised returns recovers s^ with a correlation of 0.996 to the true s and a largest absolute
error of 0.097, on a shape that ranges from about 0.3 to 1.5. *Arithmetic of the fit:* the regression has 1
intercept, 2 polynomial terms and 2 x 2 Fourier terms, so 7 columns. Exponentiating half the fitted value gives s^.
The log z^2 term has a non-zero mean (about -1.27 for Gaussian z), which the renormalisation absorbs.

### 10.6 Pilot use: testable hypotheses

- **H-P1 (time-of-day structure in passive execution).** H0: the fill probability within 60 s of a 1-lot passive
  order at the best bid or offer does not depend on the time of day. Model: logit(P(fill)) = flexible Fourier form
  in time of day with P = 4, plus dummies for the 08:30 ET release minute and the cash open and close. Statistic:
  likelihood-ratio chi-squared with 2P + 2 + (number of dummies) degrees of freedom, using day-clustered or
  day-block bootstrap inference.
- **H-P2 (the same for net 60-s markouts of fills).** OLS with HAC standard errors and the same regressors, with an
  F (Wald) test on the time-of-day terms.
- **Sample.** 84 sessions give about 84 observations per minute-of-day bin. Detecting a fill-rate swing of 10
  percentage points between bins is easy with thousands of orders a day.
- **Trial count.** These are descriptive tests that *define the baseline*. They add 1 each to N if they are reported
  as findings. The rule that follows is more important: **any order-book ML model must beat a time-of-day-only
  baseline**, so that the model's apparent skill is not just the clock.

### 10.7 Compute

One least-squares fit with 11 columns on about 10^5 to 10^7 rows takes seconds. No GPU is needed.

### 10.8 Evidence

- **Andersen and Bollerslev (1997), *J. Empirical Finance* 4: 115-158.** "The pervasive intraday periodicity in the
  return volatility in foreign exchange and equity markets is shown to have a strong impact on the dynamic properties
  of high frequency returns" (abstract, Kellogg page, `kellogg_ab1997_landing.txt`, line 191). [Full text paywalled;
  abstract only.]
- **Andersen and Bollerslev (1996, NBER w5752).** On DM-dollar data, long-run dependence in volatility is visible only
  after the periodicity is handled (lines 600-616 and 892-902).
- **Yan (2021, arXiv 2111.02376).** The multiplicative component model (intraday shape times daily GARCH times
  intraday GARCH) builds on A&B. This is a volatility-forecasting use.
- **For trading.** Time-of-day effects in volatility and liquidity are among the most robust facts in market
  microstructure. As a source of *alpha* they are not an edge: everyone knows the clock. Their value to this program
  is as a control and as a stratifier, for example of the fill-probability model used in the Part B simulation.

**Assessment.** Use this as a required baseline and control. It is cheap and robust, and it is not a strategy.

---

## 11. Compute summary: laptop versus a bigger machine

| Method | Work for 4 months of one contract | Laptop (20 CPUs, 14 GB, RTX 3050 4 GB) | Needs more? |
|---|---|---|---|
| FFD + ADF grid | 1 convolution per d, about 7.2M points | 0.55 s per d (measured) | No |
| Triple-barrier labels | 10^5 fills x about 10^3 updates | seconds (estimate) | No |
| Uniqueness weights | O(labels x span) | seconds (estimate) | No |
| Purged k-fold / CPCV | configurations x C(N,k) fits | 6 s per 10^6-row LightGBM fit (measured); 270 fits about 27 min; 10,920 fits about 18 h | Optional, overnight is fine |
| MODWT J = 8 to 12 | about N J multiplies | 0.69 s Haar J = 8 (measured); 0.5-0.75 GB RAM | No |
| Periodogram / FFF | 1 FFT; 1 least-squares fit | under 1 s / seconds | No |

**Cloud prices, fetched 2026-10-21 (per GPU-hour, on demand, before tax).** RunPod lists an RTX 4090 (24 GB) at
"$ 0.89 /hr", an A100 PCIe (80 GB) at "$ 1.79 /hr" and an H100 PCIe at "$ 2.89 /hr" (`runpod_pricing.txt`). Lambda
lists, for a 1x instance, an A100 SXM (40 GB) at "$1.99" and an H100 PCIe (80 GB) at "$3.29" per GPU per hour, plus
applicable sales tax (`lambda_pricing.txt`). (I read the RunPod figures from a flattened page by matching each price
to the GPU name that follows it. Check them on the live page before any spend.) None of the methods in this section
needs a GPU. An 18-hour overnight CPCV run on the laptop would cost about 18 x $0.89 = $16 on a rented 4090 pod. It
would only be faster if the trees were trained on the GPU, so renting is not worth it at this scale. GPU needs come
from the deep order-book models covered in other C2 sections, not from these methods.

---

## 12. Candidate hypotheses and their cost in N

**Power rule used throughout (stated assumption).** For a one-sample mean test of the per-fill net outcome, at
two-sided alpha = 0.05 and 80% power, n = ((1.96 + 0.8416) sigma / delta)^2 *effective* observations (computed, key
`power_examples`):
- delta = 0.25 tick, sigma = 2 ticks: n = (2.8016 x 8)^2 = 503.
- delta = 0.25 tick, sigma = 4 ticks: n = 2,010.
- delta = 0.10 tick, sigma = 2 ticks: n = 3,140.
- With a Bonferroni-style z of 3.023 (alpha = 0.05/20, two-sided): n = ((3.023 + 0.8416) x 8)^2 = 956 for
  delta = 0.25 tick and sigma = 2 ticks.

The sigma values are placeholders. The pilot measures the real sd of 1/10/60-s markouts in ticks. "Effective" means
n_eff = sum of average uniqueness (section 4), or HAC-adjusted, not the raw count of overlapping fills.

| ID | Hypothesis (H1) | Statistic | Sample (effective) | Configurations added to N |
|---|---|---|---|---|
| H-FD1 | An FFD-transformed drifting input lowers held-out log loss of the frozen fill-toxicity model versus the integer-differenced input | mean per-fill log-loss difference, HAC t / day-block bootstrap | thousands of fills | 1 (d* by rule in-fold, tau fixed), or 1 per fixed d |
| H-TB1 | The mean net triple-barrier outcome of filled passive orders is > 0 in a declared subset (for example queue-ahead below median) | one-sided HAC t, day-clustered | >= 500 to 2,000 | 1 per (k_u, k_l, h); declared grid of 6 at most |
| H-ML1 | The meta-label filter raises mean net 60-s markout per *posted* order versus always-post, by policy simulation | difference in means, day-block bootstrap | >= 1,000 accepted fills per arm unpaired (about 500 paired) | 1 model x thresholds (2) = 2 |
| H-W1 | Causal MODWT scale energies of signed volume lower held-out log loss of the toxicity model | as H-FD1 | thousands of fills | 1 (LA(8), J = 6), 2 with Haar |
| H-P1 | Fill probability within 60 s depends on time of day (FFF P = 4 + event dummies) | LR chi-squared, day-clustered | all posted orders | 1 (descriptive) |
| H-P2 | Net 60-s markout of fills depends on time of day | Wald F with HAC | all fills | 1 (descriptive) |
| H-CV0 | The purged protocol shows no skill on a placebo target | IC/AUC within 2 se of null | as the main test | 0 (diagnostic) |
| H-CV1 | Share of CPCV paths with positive net mean markout | descriptive | as the main test | 0 (diagnostic) |
| (weights) | Uniqueness-weighted versus unweighted training | as H-FD1 | as H-FD1 | 0 if one scheme is declared, 1 if compared |
| (denoise) | Not proposed | n/a | n/a | 0 |

The minimal declared set (H-FD1 with the in-fold rule, H-TB1 with one setting, H-ML1 with 2 thresholds, H-W1 with
one filter, H-P1 and H-P2) adds 7 to N. The maximal grids listed add 18 (5 + 6 + 2 + 2 + 1 + 1, plus 1 for the weights
comparison). The lead decides which, if any, are pre-registered. This section only prices them.

---

## 13. Verdicts for this program

| Method | Verdict | Reason |
|---|---|---|
| Fractional differencing (FFD, minimum d by ADF) | **maybe** | Cheap and causal, but its signature evidence (passes ADF, 0.995 correlation with the level) is reproduced on pure noise with the one-lag ADF the rule uses (section 1.5), and d* moves with the sample. At most one optional feature variant, counted in N. |
| Triple-barrier labels | **use** | The natural, honest target for a post-then-exit passive order. Its value is in definition, not prediction. Declare the barriers ex ante. |
| Meta-labeling | **use (as architecture), with caution** | A fixed simple primary rule plus a learned filter keeps the side decision out of the search. Published support is thin, comes from the method's promoters and is measured in precision. For passive orders, simulate the whole post/cancel policy (selection effect, section 3.3). |
| Sample uniqueness weights / sequential bootstrap | **maybe** | Always report n_eff and HAC inference. The weights themselves are optional, and I found no independent evidence. |
| Purged k-fold + embargo | **use** | Necessary hygiene for model selection with overlapping labels. Use session-aligned folds, with gaps of H + c tau. |
| CPCV | **use (diagnostic only)** | Supplies the path matrix for PBO/CSCV and DSR. Its paths are correlated, and it is not the final test. One forward hold-out decides (V43). |
| Wavelets (Haar/Daubechies, MODWT, MRA) | **maybe** | Good for describing which scales carry markout variance, and cheap causal features. MRA and full-sample decompositions leak (section 7.5), and published forecasting gains are largely leakage. |
| Wavelet denoising | **skip** | No forecasting benefit shown, two-sided by construction, and adds a configuration for nothing. |
| Periodogram | **use (diagnostic)** | Fixes the number of harmonics for the periodicity model, and shows long memory and the daily cycle. |
| Intraday periodicity (A&B flexible Fourier form) | **use (mandatory baseline)** | Every order-book model must beat a time-of-day-only baseline. It is also the stratifier for the fill model. Not an edge by itself. |

---

## References

Full text fetched (file under `pages/C2_AFML/`):
1. Lopez de Prado, M. (2018). The 10 Reasons Most Machine Learning Funds Fail. *Journal of Portfolio Management*
   44(6). GARP copy: https://www.garp.org/hubfs/Whitepapers/a1Z1W0000054x6lUAA.pdf, `lopezdeprado_2018_10reasons_jpm.pdf`.
   It summarises AFML chapters 3, 4, 5, 7 and 12.
2. Lopez de Prado, M. (2017). The 7 Reasons Most Machine Learning Funds Fail (slides, SSRN 3031282, mirror).
   `lopezdeprado_2017_7reasons_slides.pdf` (background, not quoted).
3. mlfinpy documentation, "Fractionally Differentiated" (quotes AFML ch. 5).
   https://mlfinpy.readthedocs.io/en/latest/FractionalDifferentiated.html, `mlfinpy_fracdiff.html`.
4. Graves, T., Gramacy, R., Watkins, N., Franzke, C. (2014/2017). A brief history of long memory: Hurst, Mandelbrot
   and the road to ARFIMA. arXiv 1406.6018. `graves_etal_2014_long_memory_history.pdf`.
5. Hurvich, C. FARIMA handout, NYU Stern. `hurvich_farima_handout.pdf`.
6. Gajda, J., Walasek, R. (2020). Fractional differentiation and its use in machine learning. University of Warsaw
   WNE Working Paper 32/2020 (338). `wne_wp338.pdf`.
7. Slepaczuk, R., Bieganowski, B. (2024). Supervised Autoencoders with Fractionally Differentiated Features and Triple
   Barrier Labelling Enhance Predictions on Noisy Data. ICAIF-24; arXiv 2411.12753. `arxiv_2411_12753_sae_fracdiff_tbl.pdf`.
8. Stock Price Prediction Using Triple Barrier Labeling and Raw OHLCV Data: Evidence from Korean Markets (2025).
   arXiv 2504.02249. `arxiv_2504_02249_tbl_korea.pdf`.
9. Singh, A., Joubert, J. Does Meta-Labeling Add to Signal Efficacy? Hudson and Thames (about 2019).
   https://hudsonthames.org/wp-content/uploads/2022/04/Does-Meta-Labeling-Add-to-Signal-Efficacy.pdf,
   `singh_joubert_metalabeling_efficacy.pdf`.
10. Man, X., Chan, E. (2020). The best way to select features? arXiv 2005.12483. `man_chan_2020_feature_selection_metalabeling.pdf`.
11. Li, J. (2026). The Impossible Trinity of Time-Series Validation. arXiv 2609.29530 (preprint). `arxiv_2609_29530_trinity_validation.pdf`.
12. Deep, G., Deep, A., Lamptey, W. (2025). Interpretable Hypothesis-Driven Trading: A Rigorous Walk-Forward
    Validation Framework for Market Microstructure Signals. arXiv 2512.12924. `arxiv_2512_12924.pdf`.
13. Percival, D. B. (2018). MODWT lecture slides, UW STAT 530 (from Percival and Walden 2000, WMTSA).
    https://faculty.washington.edu/dbp/s530/PDFs/05-MODWT-for-printing-2018.pdf, `percival_2018_modwt_slides.pdf`.
14. Hasumi, R., Kajita, Y. (2018). Boundary problem and data leakage: A caveat for wavelet-based forecasting. JCER
    Discussion Paper 148. `hasumi_kajita_2018_wavelet_leakage.pdf`.
15. Donoho, D. L. (1995). De-noising by soft-thresholding. *IEEE Trans. Information Theory* 41(3), 613-627 (Stanford
    copy). `donoho_1995_denoising_soft_threshold.pdf`.
16. Andersen, T. G., Bollerslev, T. (1996). Heterogeneous Information Arrivals and Return Volatility Dynamics:
    Uncovering the Long-Run in High Frequency Returns. NBER WP 5752 (published *J. Finance* 1997).
    `andersen_bollerslev_1996_nber_w5752.pdf`.
17. Yan, X. (2021). Multiplicative Component GARCH Model of Intraday Volatility. arXiv 2111.02376. `arxiv_2111_02376_mcgarch.pdf`.
18. SciPy docs: `scipy.signal.periodogram`, `scipy.signal.welch`. `scipy_periodogram_docs.html`, `scipy_welch_docs.html`.
19. R package highfrequency, `spotvol` documentation (rdocumentation.org, v0.6.3). `rdoc_highfrequency_spotvol.html`.
20. RunPod GPU pricing page (fetched 2026-10-21). `runpod_pricing.html`. Lambda GPU cloud pricing page (fetched
    2026-10-21). `lambda_pricing.html`.

Abstract or record only (claims marked [unverified] beyond the abstract):
21. Joubert, J. F. (2022). Meta-Labeling: Theory and Framework. *J. Financial Data Science* 4(3): 31-44, DOI
    10.3905/jfds.2022.1.098. `joubert_2022_jfds_landing.html`.
22. Meyer, M., Joubert, J. F., Alfeus, M. (2022). Meta-Labeling Architecture. *JFDS* 4(4). `meyer_joubert_alfeus_2022_arch_landing.html`.
23. Thumm, D., Barucca, P., Joubert, J. F. (2023). Ensemble Meta-Labeling. *JFDS* 5(1). `thumm_barucca_joubert_2023_ensemble_landing.html`.
24. Meyer, M., Barziy, I., Joubert, J. F. (2023). Meta-Labeling: Calibration and Position Sizing. *JFDS* (via the repo
    README). `ht_metalabeling_repo_readme.md`.
25. Andersen, T. G., Bollerslev, T. (1997). Intraday periodicity and volatility persistence in financial markets.
    *J. Empirical Finance* 4(2-3): 115-158, DOI 10.1016/S0927-5398(97)00004-2. `kellogg_ab1997_landing.html`.
26. Gencay, R., Selcuk, F., Whitcher, B. (2001). Differentiating intraday seasonalities through wavelet multi-scaling.
    *Physica A* 289: 543-556. `bilkent_gsw2001_record.html`.
27. Arian, H. R., Norouzi Mobarekeh, D., Seco, L. A. (2024). Backtest overfitting in the machine learning era: A
    comparison of out-of-sample testing methods in a synthetic controlled environment. *Knowledge-Based Systems*,
    DOI 10.1016/j.knosys.2024.112477. Not retrieved. Its finding is cited via ref. 12.

Cited, not retrieved:
28. Hosking, J. R. M. (1981). Fractional differencing. *Biometrika* 68(1): 165-176, DOI 10.1093/biomet/68.1.165 (via
    refs. 4 and 5).
29. Lopez de Prado, M. (2018). *Advances in Financial Machine Learning*. Wiley (via refs. 1 and 3).
30. Gencay, R., Selcuk, F., Whitcher, B. (2002). *An Introduction to Wavelets and Other Filtering Methods in Finance
    and Economics*. Academic Press.
31. Percival, D. B., Walden, A. T. (2000). *Wavelet Methods for Time Series Analysis*. Cambridge University Press
    (via ref. 13).
32. Donoho, D. L., Johnstone, I. M. (1994). Ideal spatial adaptation by wavelet shrinkage. *Biometrika* 81(3): 425-455.
33. Boudt, K., Croux, C., Laurent, S. (2011). Robust estimation of intraweek periodicity in volatility and jump
    detection. *J. Empirical Finance* 18: 353-367 (via ref. 19).

---

## Evidence table

| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| FracDiff generalises returns to non-integer d | Lopez de Prado 2018 | "Fractional differentiation (FracDiff) allows us to generalize the notion of returns to non-integer (positive real) differences 𝑑" | lopezdeprado_2018_10reasons_jpm.txt (l. 282-283) |
| Weights for 0<d<1 are negative after w0 | Lopez de Prado 2018 | "Anywhere in between these two cases, all weights after 𝜔0 = 1 are negative and greater than -1" | lopezdeprado_2018_10reasons_jpm.txt (l. 298-299) |
| E-mini example: d = 0.4 passes ADF, corr 0.995 | Lopez de Prado 2018 | "the value of an ADF statistic computed on the FracDiff series with 𝑑 = .4 is -3.2733, and we can reject the null hypothesis with a confidence level in excess of 95%" | lopezdeprado_2018_10reasons_jpm.txt (l. 304-306) |
| Expanding window drifts; fixed width fixes it | mlfinpy docs (AFML ch. 5) | "Without the control of weight-loss the \(\widetilde{X}\) series will pose a severe negative drift. This problem is corrected by using a fixed-width window and not an expanding one." | mlfinpy_fracdiff.txt (l. 66-67) |
| Minimum d chosen at the ADF crossing | mlfinpy docs | "Based on where the ADF statistic crosses this threshold, the minimum \(d\) value can be defined." | mlfinpy_fracdiff.txt (l. 123-124) |
| ARFIMA(0,d,0) is stationary with long memory for 0<d<1/2 | Graves et al. 2014 | "to obtain the ARFIMA(0, d, 0) process, which for 0 < d < 1/2 is stationary and possesses long memory" | graves_etal_2014_long_memory_history.txt (l. 1070-1071) |
| Not stationary for d >= 0.5 | Hurvich handout | "the ARIMA (0,d ,0) process will not be stationary if d ≥ .5." | hurvich_farima_handout.txt (l. 151) |
| ANN accuracy better with FFD inputs (indices) | Gajda and Walasek 2020 | "The conclusion of the study is that fractionally differentiated time series performed better in trained ANN." | wne_wp338.txt (abstract) |
| FFD study ignores slippage | Slepaczuk and Bieganowski 2024 | "research does not take into account slippage, which could potentially dimin-" | arxiv_2411_12753_sae_fracdiff_tbl.txt (l. 453) |
| Triple-barrier label definition | Lopez de Prado 2018 | "If the upper horizontal barrier is touched first, we label the observation as a 1. If the lower horizontal barrier is touched first, we label the observation as a -1." | lopezdeprado_2018_10reasons_jpm.txt (l. 360-362) |
| Barriers optimised in a TBL study | Korean-stocks paper 2025 | "stocks from 2006 to 2024, we optimize the triple barrier labeling" | arxiv_2504_02249_tbl_korea.txt (l. 26) |
| Secondary model predicts primary accuracy | Lopez de Prado 2018 | "The goal of the secondary model is to predict the accuracy of the primary model's prediction." | lopezdeprado_2018_10reasons_jpm.txt (l. 390-391) |
| Meta-labeling is an experience claim | Lopez de Prado 2018 | "In my experience, meta-labeling ML models can deliver more robust and reliable outcomes than standard labeling models." | lopezdeprado_2018_10reasons_jpm.txt (l. 430-431) |
| Joubert's framework uses a controlled experiment | Joubert 2022 (abstract) | "The author also deconstructs meta-labeling into three components, using a controlled experiment to show how each component helps to improve strategy metrics" | joubert_2022_jfds_landing.html (citation_abstract) |
| Ensembles help with regimes (abstract) | Thumm, Barucca, Joubert 2023 | "The authors demonstrate that ensembles are especially beneficial when the underlying data consist of multiple regimes and are nonlinear in nature." | thumm_barucca_joubert_2023_ensemble_landing.html |
| E-mini meta-labeling, out-of-sample precision | Singh and Joubert | "The precision jumps from 0.17 to 0.20 and the accuracy from 17% to 63%." | singh_joubert_metalabeling_efficacy.txt (l. 601-602) |
| Parameters hand-tuned, classes up-sampled | Singh and Joubert | "we manually tuned a few pa- rameters to ensure that we have sufficient data points" (line-break hyphen as extracted) | singh_joubert_metalabeling_efficacy.txt (l. 506-507) |
| Meta-labeling Sharpe 0.36 to 0.74 (464 trades) | Man and Chan 2020 | "Sharpe Ratio 0.360 0.743 0.829" (Table 4: original, without and with feature selection) | man_chan_2020_feature_selection_metalabeling.txt (l. 436) |
| Uniqueness definition | Lopez de Prado 2018 | "The uniqueness of a label 𝑖 at time 𝑡 is 𝑢𝑡,𝑖 = 1𝑡,𝑖 𝑐𝑡−1 ." | lopezdeprado_2018_10reasons_jpm.txt (l. 460) |
| Sequential bootstrap raises uniqueness (Monte Carlo) | Lopez de Prado 2018 | "Monte Carlo experiments demonstrate that sequential bootstrapping can significantly increase the average uniqueness of samples" | lopezdeprado_2018_10reasons_jpm.txt (l. 489-491) |
| Embargo size rule | Lopez de Prado 2018 | "A small value ℎ ≈ .01𝑇, where 𝑇 is the number of bars, often suffices to prevent all leakage." | lopezdeprado_2018_10reasons_jpm.txt (l. 522-523) |
| Walk-forward single path overfits | Lopez de Prado 2018 | "First, a single scenario is tested (the historical path), which can be easily overfit" | lopezdeprado_2018_10reasons_jpm.txt (l. 538-539) |
| CPCV gives a distribution of Sharpe ratios | Lopez de Prado 2018 | "A key advantage of CPCV is that it allows us to derive a distribution of Sharpe ratios, as opposed to a single (likely overfit) Sharpe ratio estimate." | lopezdeprado_2018_10reasons_jpm.txt (l. 605-606) |
| Leakage bias bound; purging pays in distance | Li 2026 | "purged k-fold with an embargo pays in distance instead, which is cheap when the process forgets quickly but cannot repair the part of causality demanded by non-stationarity" | arxiv_2609_29530_trinity_validation.txt (l. 27-29) |
| Shuffled k-fold shows skill on noise | Li 2026 | "On pure noise, shuffled 5-fold reports an information coefficient of +0.32, while contiguous 5-fold, using the same amount of future data, reports +0.004." | arxiv_2609_29530_trinity_validation.txt (l. 29-31) |
| CPCV best in a synthetic comparison [unverified, citing paper] | Deep et al. 2025 citing Arian et al. 2024 | "finding that Combinatorial Purged Cross-Validation shows superiority in mitigating over-fitting risks" | arxiv_2512_12924.txt (l. 182-184) |
| A strict protocol yields a null | Deep et al. 2025 | "We report statistically insignificant aggregate results (p-value 0.34)" | arxiv_2512_12924.txt (l. 30) |
| MODWT works for any N and shifts with X | Percival 2018 | "unlike the DWT, MODWT is defined naturally for all samples sizes" | percival_2018_modwt_slides.txt (l. 20-21) |
| MODWT pyramid cost | Percival 2018 | "algorithm requires N log2(N ) multiplications, which is the same as needed by fast Fourier transform algorithm" | percival_2018_modwt_slides.txt (l. 487-488) |
| Wavelet forecasting leaks; proper processing fails | Hasumi and Kajita 2018 | "We find that wavelet-based forecasting in which the time series data are processed appropriately cannot outperform even a naive prediction." | hasumi_kajita_2018_wavelet_leakage.txt (l. 38-39); jcer_boundary_leakage_landing.txt (l. 279) |
| MODWT seasonality filter (abstract) | Gencay, Selcuk, Whitcher 2001 | "Our methodology is based on a wavelet multi-scaling approach which decomposes the data into its low- and high-frequency components through the application of a non-decimated discrete wavelet transform." | bilkent_gsw2001_record.txt |
| Soft-threshold shrinkage | Donoho 1995 | "(2) Apply the soft thresholding nonlinearity" (followed by the garbled formula for eta_t(y) = sgn(y)(|y| - t)_+) | donoho_1995_denoising_soft_threshold.txt (l. 83-85) |
| Welch averages periodograms | SciPy docs | "Welch's method [1] computes an estimate of the power spectral density by dividing the data into overlapping segments, computing a modified periodogram for each segment and averaging the periodograms." | scipy_welch_docs.txt |
| Periodicity obscures the volatility ACF | Andersen and Bollerslev 1996 | "the implementation of this idea is obscured by the strong intradaily periodicity" | andersen_bollerslev_1996_nber_w5752.txt (l. 894-895) |
| Two-sided filters are not forecast-usable | Andersen and Bollerslev 1996 | "the low-pass filtering technique developed below is based on a two-sided weighted average of both past and future absolute returns" | andersen_bollerslev_1996_nber_w5752.txt (l. 900-901) |
| Periodicity matters for high-frequency dynamics (abstract) | Andersen and Bollerslev 1997 | "The pervasive intraday periodicity in the return volatility in foreign exchange and equity markets is shown to have a strong impact on the dynamic properties of high frequency returns." | kellogg_ab1997_landing.txt (l. 191) |
| A&B multiplicative model | Yan 2021 | "where 𝜎𝑡 is the conditional daily volatility at day 𝑡, 𝑠𝑛 is the intraday volatility periodicity during the period of 𝑟𝑡,𝑛" | arxiv_2111_02376_mcgarch.txt (l. 572-573) |
| FFF implementation default P = 5 | highfrequency docs | "the number of cosinus terms used in the flexible Fourier specification of the periodicity function, see Andersen et al. (1997) for details. Default = 5." | rdoc_highfrequency_spotvol.txt |
| Cloud GPU price, RunPod | RunPod pricing | "RTX 4090 24 GB VRAM 41 GB RAM 6 vCPUs $ 0.89 /hr" (flattened page text) | runpod_pricing.txt |
| Cloud GPU price, Lambda | Lambda pricing | "NVIDIA A100 SXM 40 GB 30 220 GiB 512 GiB SSD $1.99" | lambda_pricing.txt |

---

## Gaps, failures and route log

- **Not retrieved (paywalled; no open copy found by OpenAlex or Crossref):** Hosking (1981), the AFML book,
  Andersen and Bollerslev (1997) full text, the Gencay-Selcuk-Whitcher 2002 book and 2001 paper, the Joubert (2022)
  and other JFDS full texts, and the Arian et al. (2024) full text. Claims about them rest on abstracts, citing papers
  or secondary full text, and are marked as such.
- **Blocked:** Springer and SpringerOpen PDFs of a 2025 *Financial Innovation* paper (crypto information-driven bars,
  triple-barrier labels and deep learning) returned a 3 KB stub on both routes. The paper is not used, and the file
  was deleted (noted in `log.tsv`). pm-research.com needed a cookie jar (curl with cookies), noted in the log.
  Wikipedia pages returned a stub (pointer only, not used). The Theseus thesis and the MDPI JRFM PDF returned HTML
  stubs. Not used.
- **Scrapling and Firecrawl:** not used. curl was enough for every page used, so no terms-of-use decision was needed.
- **WebSearch budget:** 19 of 60 calls used. No budget-exhausted notice was seen. Cost notices from a hook were
  informational and ignored, as the rules say.
- **Negative search results (not findings about the world, only about my search):** I found no independent,
  peer-reviewed, cost-inclusive out-of-sample evaluation of (a) AFML's FFD rule against plain returns at intraday
  frequency, (b) meta-labeling on futures or on passive execution, (c) uniqueness weighting, or (d) CPCV-selected
  versus walk-forward-selected strategies in live trading.
- **My own contributions, not from the literature, flagged where used:** the FFD weight-sum and unit-root
  decomposition (section 1.2), the random-walk FFD simulation and the instability of d* (section 1.5), the
  precision-P&L break-even (section 3.2), the passive-order selection effect (section 3.3), the MODWT causality
  demonstration (section 7.5), and the power numbers, whose sigma values are placeholders (section 12).
- **Resume check (2026-10-21 05:12 PDT, re-spawned after a usage cut):** the file was already complete through this log. On
  resume I checked every evidence-table quote against its saved file (40 of 40 found; one carries a pdftotext line
  hyphen, "pa- rameters", as in the file) and reran `C2_AFML_examples.py` under `uv run`: every computed value
  matched; only the two wall-clock timings moved (FFD 0.549 s to 0.507 s, Haar MODWT 0.689 s to 0.921 s), so the
  original JSON was kept. No new searches or fetches.

## Corrections after review (Stage E.28, MathReviewer G6)

- MG6-01: section 1.5 now states the ADF uses one lagged difference (p = 1) [unverified: AFML book not fetched]; the mechanism sentence is replaced (the long negative moving average and Schwert 1989 over-rejection; borderline or absent with Schwert's lag rule); the assessment and the verdict-table reason now say "with a one-lag ADF". Verdict "maybe" unchanged.
- MG6-02: section 4.5 pilot scale now gives mean other labels covering a bar 1.45, u_bar about 0.53 (Poisson) to 0.69 (even spacing), n_eff 0.5 to 0.7 of the label count.
- MG6-03: H-ML1 sample changed to about 1,000 fills per arm unpaired or about 500 paired differences; the verdict-table cell matches.
- MG6-04: H-FD1 sample restated in log-loss units (placeholders delta 0.005, sigma 0.3 give about 28,000 fills); tick example assigned to H-TB1 and H-ML1. H-W1 "As for H-FD1" inherits this.
- MG6-05: 7.2 million corrected to about 7.0 million (6,955,200) in section 1.3 and section 8 (line 774 text); the timing mentions of 7.2 million (lines 212, 819, 961, 1083) are left because the timing runs did use 7.2 million points.
- MG6-06: "E-mini tick data from 2011 to 2019" marked [unverified].
- MG6-07: test-set size of about 100 trades labelled as my estimate with its basis.
- MG6-08: Li quote line citation changed from line 17 to line 23.
- MG6-10: evidence-table check count changed from 39 of 39 to 40 of 40.
- MG6-14: "as much memory as possible" now cites line 259 and drops the full stop inside the quote.
