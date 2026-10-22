# E.28 methods brief, Part C2: filtering and latent-state models (Kalman, EKF/UKF, particle filters, HMMs)

Worker: C2_Filter (MethodReader, Opus 5.5). Written 2026-10-21 PDT, starting 02:43. Pages:
`reports/stage_e28_briefs/pages/C2_Filter/` (log: `log.tsv`). Scripts and probe outputs:
`reports/stage_e28_briefs/work/C2_Filter/` (`C2F_bench.py` with `C2F_bench_results.json` and `C2F_bench.log`;
`C2F_examples.py` with `C2F_examples.json`; `C2F_fetch.sh`, `C2F_ctx.py` are fetch and grep helpers). Every number
marked "measured" comes from those files. They use synthetic data only: no market data was read, nothing was
registered, and N stays 538.

How to read this section. Section 0 sets up the one object every method here shares: a hidden state observed
through noise, and the difference between filtering, smoothing and prediction. That difference decides whether a
regime model leaks the future into a backtest. Sections 1 to 4 take each method in turn with the eight items the
brief asks for: (1) idea, (2) equations, (3) data, (4) what it estimates or decides, (5) worked example,
(6) pilot hypothesis, (7) compute, (8) evidence. Section 5 collects the evidence on intraday futures. Section 6 says
how a regime model could gate a passive strategy without adding hidden trials. Section 7 is the compute summary
with cloud prices, section 8 the candidate hypotheses in one table, section 9 the verdicts, then the references,
the evidence table and the gaps log.

Quotes are verbatim from the saved text files (pdftotext output of the saved PDFs, or the de-tagged HTML). Two
sources are scanned images with no text layer (Hamilton 1989, Rabiner 1989); their quotes were read from the page
image of the saved PDF, and the evidence table says so. pdftotext mangles some mathematical symbols (subscripts,
hats, Greek letters). Where a quote contains mangled symbols I say so and restate the equation in clean notation.

Units used in the examples: MES (Micro E-mini S&P 500) has a tick of 0.25 index points worth $1.25. "Markout at h
seconds" for a passive buy filled at price p is (mid at fill time + h) minus p, signed so that a negative number is
a loss to the passive side; for a sell, the sign flips.

---

## 0. Common frame: hidden states, filtering, smoothing, and the look-ahead rule

All four methods in this section share one structure, the state-space (or hidden-state) model:

    hidden state:   x_t ~ p(x_t | x_{t-1}; theta)        (how the unobserved thing evolves)
    observation:    y_t ~ p(y_t | x_t; theta)            (how what we see depends on it)

- x_t is the thing we cannot see: the efficient price, a hedge ratio, log volatility, or a discrete regime label.
- y_t is what the data show: a mid-price, a trade price, a return, a spread.
- theta is the vector of fixed parameters (noise variances, transition probabilities).

Three different questions can be asked of this model, and they use different data:

| Question | Object | Uses data | Legal at decision time t? |
|---|---|---|---|
| Filtering | p(x_t \| y_1..y_t) | up to and including t | yes |
| Prediction | p(x_{t+h} \| y_1..y_t) | up to t | yes |
| Smoothing | p(x_t \| y_1..y_T), T > t | past AND future | no: look-ahead |
| Viterbi path | most likely x_1..x_T jointly given y_1..y_T | past AND future | no: look-ahead |

Hamilton (2005, Palgrave entry) states the distinction directly: filtered probabilities are "ξ jt = Pr(st = j|Ωt ;
θ)" with "Ωt = {yt , yt−1 , ..., y1 , y0 } denotes the set of observations obtained as of date t", while "One is also
often interested in forming an inference about what regime the economy was in at date t based on observations
obtained through a later date T , denoted ξ̂t|T . These are referred to as “smoothed” probabilities"
(hamilton_palgrave_regime.txt, eqs. 5 and the paragraph after eq. 12).

**The look-ahead rule for this program.** Any trading decision, gate or feature at time t may use only filtered or
predicted quantities, computed with parameters theta estimated on data that ended before the evaluation window.
Smoothed probabilities and Viterbi paths are fine for describing history and for the E-step of estimation inside a
training window, never as an input to a decision in the evaluation window. Section 4 measures how large the bias is
on synthetic data (filtered regime classification accuracy 97.3% versus smoothed 99.0%), and shows a three-line
example in which the Viterbi label of a past observation flips when two later observations arrive.

A second shared point: theta is estimated by maximum likelihood. For every model here the likelihood comes out of
the filter itself, through the "prediction error decomposition":

    log L(theta) = sum_{t=1}^{T} log p(y_t | y_1..y_{t-1}; theta)

Each term is the density of the new observation given only the past, which the filter computes as a by-product.
Hamilton writes it for the regime model as "log f (y1 , y2 , ..., yT |y0 ; θ) = Σ log f(yt |Ωt−1 ; θ)" (eq. 10,
summation sign restated) and says "An estimate of the value of θ can then be obtained by maximizing (10) by
numerical optimization" (hamilton_palgrave_regime.txt). The same holds for the Kalman filter (Gaussian terms,
section 1) and the particle filter (a Monte Carlo estimate of each term, section 3).

---

## 1. The Kalman filter (linear Gaussian state-space model)

### 1.1 Idea

The Kalman filter tracks a hidden quantity that moves smoothly (a random walk or an autoregression) and is
observed with noise. Each step does two things. **Predict**: move the previous estimate forward with the state
equation, and widen its uncertainty by the state noise. **Update**: compare the new observation with what the
prediction expected (the "innovation"), and move the estimate toward the observation by a fraction K, the Kalman
gain. K is large when the prediction is uncertain relative to the observation noise, and small when the
observations are noisy. Kalman's 1960 paper introduced the recursive form; its abstract says "A nonlinear
difference (or differential) equation is derived for the covarianc[e] matrix of the optimal estimation error. From
the solution of this equation the co[]efficients of the difference (or differential) equation of the optimal linear
filter ar[e ob]tained without further calculations" (kalman_1960.txt; letters clipped at the column edge by
pdftotext are restored in brackets).

### 1.2 Equations

Model (Welch and Bishop, TR 95-041, eqs. 1.1 to 1.4, restated without the control input B u):

    state:        x_t = A x_{t-1} + w_t,        w_t ~ N(0, Q)
    observation:  z_t = H x_t + v_t,            v_t ~ N(0, R)

- x_t: n-vector hidden state at step t. z_t: m-vector observation.
- A: n x n state transition matrix. H: m x n observation matrix.
- Q: n x n covariance of the state noise w_t. R: m x m covariance of the observation noise v_t.
- Welch and Bishop: "The random variables w k and v k represent the process and measurement noise (respectively).
  They are assumed to be independent (of each other), white, and with normal probability distributions"
  (welch_bishop_kf_intro.txt).

Recursion (Welch and Bishop Tables 1-1 and 1-2, eqs. 1.9 to 1.13; the superscript minus there means "prior",
written here as t|t-1):

    time update (predict):
      x_{t|t-1} = A x_{t-1|t-1}                                   (1.9)
      P_{t|t-1} = A P_{t-1|t-1} A' + Q                             (1.10)
    measurement update (correct):
      F_t       = H P_{t|t-1} H' + R                    (innovation covariance; inside 1.11)
      K_t       = P_{t|t-1} H' F_t^{-1}                            (1.11)
      x_{t|t}   = x_{t|t-1} + K_t (z_t - H x_{t|t-1})              (1.12)
      P_{t|t}   = (I - K_t H) P_{t|t-1}                            (1.13)

- x_{t|t-1}, P_{t|t-1}: mean and covariance of the state given data to t-1 (prior).
- x_{t|t}, P_{t|t}: mean and covariance given data to t (posterior, the filtered estimate).
- v_t = z_t - H x_{t|t-1}: the innovation. Welch and Bishop: "The difference ( z k – H x̂ k ) in (1.7) is called
  the measurement innovation, or the residual".
- K_t: the Kalman gain. Welch and Bishop: K "is chosen to be the gain or blending factor that minimizes the a
  posteriori error covariance", and "as the measurement error covariance R approaches zero, the gain K weights the
  residual more heavily ... as the a priori estimate error covariance P k approaches zero, the gain K weights the
  residual less heavily".

**Derivation summary (Gaussian conditioning).** Assume x_{t-1} given data to t-1 is N(x_{t-1|t-1}, P_{t-1|t-1}),
and the model above holds with known A, H, Q, R. Then (x_t, z_t) given data to t-1 is jointly Gaussian with means
(x_{t|t-1}, H x_{t|t-1}), variances P_{t|t-1} and F_t, and cross-covariance P_{t|t-1} H'. The conditional mean of
a Gaussian x given z is mean_x + Cov(x,z) Var(z)^{-1} (z - mean_z), and the conditional covariance is Var(x) -
Cov(x,z) Var(z)^{-1} Cov(z,x). Substituting gives exactly 1.11 to 1.13. Welch and Bishop reach the same gain by
minimising the trace of the posterior covariance: "substituting that into (1.6), performing the indicated
expectations, taking the derivative of the trace of the result with respect to K, setting that result equal to
zero, and then solving for K". If the noises are not Gaussian but have the stated covariances, the same recursion is
still the best linear estimator; it is no longer the full conditional distribution.

**Likelihood for parameter estimation.** With Gaussian noises, z_t given the past is N(H x_{t|t-1}, F_t), so

    log L(theta) = -1/2 * sum_t [ m log(2 pi) + log det F_t + v_t' F_t^{-1} v_t ]

where theta collects the unknowns in A, H, Q, R. This is the prediction error decomposition of section 0 with
Gaussian terms (my derivation from the conditional density above; the textbook treatment is Harvey 1990, which
Cartea and Karyampas cite but which I did not fetch). It is maximised numerically. An alternative is EM: the E-step
runs the filter and the Rauch-Tung-Striebel smoother inside the training window (smoothing is legal there), the
M-step updates Q and R in closed form. Ho and Xin (2016) describe this for noisy high-frequency prices: "One
technique for addressing both asynchronous returns and market microstructure is the Kalman-EM (KEM) algorithm"
(ho_xin_2016_sparse_kf.txt).

**Steady state.** Welch and Bishop: "under conditions where Q and R are in fact constant, both the estimation error
covariance P k and the Kalman gain K k will stabilize quickly and then remain constant". For the local-level model
below this gives a closed form.

### 1.3 The local-level model: an efficient price observed with microstructure noise

This is the case the brief names. Cartea and Karyampas (2009, eq. 4) write it as "Yt = Xt + εt", where "Yt is the
observed log-price, equal to the true efficient log-price Xt plus an error term εt that captures all types of the
microstructure error", and by microstructure error they mean "the bid-ask bounces; differences in trade sizes; and
other sources" (cartea_karyampas_2009.txt). Adding a random-walk efficient price gives the local-level model:

    x_t = x_{t-1} + eta_t,     eta_t ~ N(0, q)     (efficient price, a random walk)
    y_t = x_t + eps_t,         eps_t ~ N(0, r)     (observed mid or trade price)

so A = H = 1, Q = q, R = r. The filter is the scalar version of 1.9 to 1.13:

    P_{t|t-1} = P_{t-1|t-1} + q,   K_t = P_{t|t-1} / (P_{t|t-1} + r),
    x_{t|t} = x_{t|t-1} + K_t (y_t - x_{t|t-1}),   P_{t|t} = (1 - K_t) P_{t|t-1}.

**Steady state, derived.** Write P for the steady prior variance P_{t|t-1}. The posterior is P r / (P + r), and the
next prior adds q, so P = P r / (P + r) + q. Multiply by (P + r): P^2 - q P - q r = 0, whose positive root is

    P = ( q + sqrt(q^2 + 4 q r) ) / 2,        K = P / (P + r).

The steady filter is x_{t|t} = (1 - K) x_{t-1|t-1} + K y_t: **an exponentially weighted moving average with weight K
set by the signal-to-noise ratio q/r.** This matters for the program: on a regularly sampled mid-price, a
local-level Kalman filter adds nothing that an EWMA with the right span does not already give. What the model adds is
(a) a principled choice of the span, (b) the decomposition of observed variance into q and r, and (c) a way to handle
irregular spacing (let q scale with elapsed time) and missing observations (skip the update).

**What the model implies for returns.** Differencing y_t gives dy_t = eta_t + eps_t - eps_{t-1}, an MA(1) process with

    Var(dy) = q + 2r,    Cov(dy_t, dy_{t-1}) = -r,    rho_1 = -r / (q + 2r),

so the first-order autocorrelation of price changes lies between -0.5 and 0, and is more negative the larger the
noise. A method-of-moments estimate is r_hat = -gamma_1_hat and q_hat = gamma_0_hat + 2 gamma_1_hat, where gamma_k
are sample autocovariances of dy (my derivation; it is the Roll-type bid-ask bounce argument).

**Assumptions that fail on CME order-book data, and what they do.** (i) The noise is not Gaussian or independent: the
MES mid moves on a half-tick grid (0.125 points) and stays constant for many events, so the "noise" is partly
rounding. Dahlhaus and Neddermeyer propose a particle filter for exactly this reason (section 3). (ii) q is not
constant: it has a strong time-of-day pattern (Stroud and Johannes model "seasonal components capturing time of the
day patterns" for 5-minute S&P futures returns; stroud_johannes_2014.txt). (iii) The efficient price may be better
observed by a depth-weighted price (microprice) than by the mid; that is a choice of observation, and each choice
is a configuration (section 1.6).

### 1.4 Dynamic hedge ratios

Here the hidden state is the regression coefficient between two prices. Palomar (Portfolio Optimization book,
section 15.6.3, eq. 15.3) writes it, restated from its LaTeX, as y1t = [1, y2t] (µt, γt)' + εt and (µt+1, γt+1)'
= I (µt, γt)' + (η1t, η2t)', and then, verbatim apart from removed LaTeX delimiters: "where all the noise components are independent and distributed as εt ∼ N(0,σε²), η1t ∼ N(0,σµ²), and η2t
∼ N(0,σγ²), the state transition matrix is the identity T=I, the observation matrix is Zt=[1 y2t]"
(palomar_book_kalman_pairs.html.txt; LaTeX markup removed). So A = I, H_t = [1, y2t] changes every step (allowed: the
recursion uses H_t at step t), Q = diag(sigma_mu^2, sigma_gamma^2), R = sigma_eps^2. The spread traded is the
innovation y1t - mu_{t|t-1} - gamma_{t|t-1} y2t, scaled by its standard deviation sqrt(F_t). Palomar motivates the
filter as the replacement for rolling least squares: "the hedge ratio and the mean will slowly change over time and
then the least squares solution should be recomputed on a rolling-window basis. However, it is better to employ a
more sophisticated time-varying modeling and estimation technique based on state-space modeling and the Kalman
filter". Montana, Triantafyllopoulos and Tsagaris (2009) connect it to flexible least squares (arXiv 0709.3884).

**Data limit for this program.** A hedge ratio needs two contracts. Part B buys ONE contract, so this application
cannot be tested on the pilot. It needs a second purchase (for example MES with MNQ, or two adjacent maturities of
one root for a calendar spread), and a two-legged trade pays two round trips. Section 9 rates it skip for now.

### 1.5 Worked examples (computed in C2F_examples.py; numbers from C2F_examples.json)

**(a) Local level on MES mids, one-second steps.** Take q = 0.01 points^2 (efficient-price standard deviation 0.1
points, 0.4 tick, per second) and r = 0.015625 points^2 (noise standard deviation 0.125 points, half a tick).

- Steady state: P = (0.01 + sqrt(0.0001 + 4 x 0.01 x 0.015625)) / 2 = (0.01 + sqrt(0.000725)) / 2 = (0.01 +
  0.026926) / 2 = 0.018463. K = 0.018463 / (0.018463 + 0.015625) = 0.5416. So the filter puts 54% weight on the
  newest mid: an EWMA with a half-life under one second.
- Implied return autocorrelation: rho_1 = -0.015625 / (0.01 + 2 x 0.015625) = -0.015625 / 0.04125 = -0.379.
- Four steps from prior mean 5000.00 and variance 0.02, observing mids 5000.25, 5000.25, 5000.00, 5000.50:

| t | y_t | x_{t\|t-1} | P_{t\|t-1} = P + q | K_t | innovation | x_{t\|t} | P_{t\|t} |
|---|---|---|---|---|---|---|---|
| 1 | 5000.25 | 5000.00000 | 0.030000 | 0.03 / 0.045625 = 0.65753 | 0.25000 | 5000.00 + 0.65753 x 0.25 = 5000.16438 | 0.34247 x 0.03 = 0.010274 |
| 2 | 5000.25 | 5000.16438 | 0.020274 | 0.56475 | 0.08562 | 5000.21274 | 0.008824 |
| 3 | 5000.00 | 5000.21274 | 0.018824 | 0.54643 | -0.21274 | 5000.09649 | 0.008538 |
| 4 | 5000.50 | 5000.09649 | 0.018538 | 0.54263 | 0.40351 | 5000.31545 | 0.008479 |

  The gain falls from 0.66 toward the steady 0.54 within three steps, as Welch and Bishop say it should.

- Measured on synthetic data (C2F_bench_results.json): 1,000,000 simulated one-second steps with these q and r;
  maximum likelihood (Nelder-Mead on the steady-state innovations likelihood of dy; steady-state K and F; exact only asymptotically) returned q_hat = 0.009981 and
  r_hat = 0.015577 in 0.68 s (66 likelihood evaluations); the sample rho_1 was -0.3794 against the theoretical
  -0.3788.

**(b) Dynamic hedge ratio, three steps.** Model y1 = gamma_t y2 + eps (intercept fixed at 0 for clarity),
gamma a random walk with sigma_gamma^2 = 0.0001, sigma_eps^2 = 1, prior gamma = 2.0 with variance 0.01.

| t | y2 | y1 | gamma prior | P prior = P + 0.0001 | F = y2^2 P + 1 | K = P y2 / F | innovation y1 - gamma y2 | gamma post | P post = (1 - K y2) P |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10.0 | 21.0 | 2.00000 | 0.010100 | 100 x 0.0101 + 1 = 2.01 | 0.101 / 2.01 = 0.050249 | 21 - 20 = 1.0 | 2.05025 | 0.005025 |
| 2 | 10.5 | 21.5 | 2.05025 | 0.005125 | 1.56502 | 0.034384 | -0.02761 | 2.04930 | 0.003275 |
| 3 | 9.8 | 19.0 | 2.04930 | 0.003375 | 1.32410 | 0.024977 | -1.08313 | 2.02225 | 0.002549 |

  The innovation divided by sqrt(F) is the z-score a pairs rule trades on: at t = 3 it is -1.083 / sqrt(1.324) =
  -0.94.

### 1.6 A testable, pre-registerable hypothesis from the pilot

The pilot measures, for a 1-lot passive order on one contract: whether it fills (under TopstepX's rule, a resting
limit fills only on a trade-through; C3_lead_draft.md quotes docs/DECISIONS.md:30-46 to that effect), the queue time,
and the 1, 10 and 60 s markouts. A Kalman filter can only turn this into a hypothesis by supplying a feature.

**H-KF1 (filtered-price deviation predicts adverse selection).** At the moment a passive bid (ask) is placed, compute
d_t = x_{t|t} - mid_t from a local-level filter on one-second mids, with q and r estimated by maximum likelihood on
the training window only. Hypothesis: the mean 10 s markout of passive fills placed when d_t < 0 for a bid (d_t > 0
for an ask; the filter puts the efficient price on the order's own side of the mid, nearer the resting bid or ask, so the fill is more likely adverse) is lower than for the other fills.

- Test statistic: difference of mean 10 s markouts between the two groups, in ticks, with a t-statistic clustered
  by trading day (fills on the same day are not independent). One-sided, against the program's bar t > 3.0.
- Sample needed: n per group = 2 (z_alpha + z_beta)^2 sigma^2 / d^2 with z_alpha = 3.0 and power 0.8 (z_beta =
  0.8416), so (3.8416)^2 = 14.758. With a markout standard deviation sigma = 1.5 ticks (an ASSUMPTION; the pilot
  will measure it) and a difference d = 0.25 tick: 2 x 14.758 x (1.5 / 0.25)^2 = 2 x 14.758 x 36 = 1,063 fills per
  group. For d = 0.10 tick it is 6,642 per group; for d = 0.5 tick, 266. Full grid in C2F_examples.json (power).
  Day clustering raises these numbers by the design effect, which the pilot must estimate.
- Trial count: if the observation (mid), the sampling (1 s), the estimation window and the sign split are fixed in
  advance, this is one configuration: N rises by 1. Each extra choice multiplies: mid or microprice (x2), 1 s or
  event time (x2), and three markout horizons tested separately (x3) would make 12.
- What a pass would mean: only that the feature sorts fills. It would still need a strategy that uses it (pull the
  order when d_t is adverse), which is a second, separately counted test on data that did not select it.

A descriptive use, not a hypothesis: estimating q and r by time of day measures how much of the observed price
variance is noise. Whether a purely descriptive measurement adds to N is the lead's decision; I flag it and do not
count it.

### 1.7 Compute

Measured on the ThinkPad (synthetic data, nice 10; C2F_bench_results.json): a plain Python loop of the scalar filter
runs 1,000,000 steps in 0.85 s; the steady-state filter as a linear filter (scipy lfilter) runs 10,000,000 steps in
0.074 s; the MLE on 1,000,000 steps took 0.68 s. Four months of regular-hours one-second mids are about 80 days x
23,400 s = 1.87 million steps, so a full fit takes seconds. A two-state hedge-ratio filter is the same order. No GPU or
cloud machine is needed. (Cloud prices are in section 7 for the methods that might need them.)

Software: pykalman 0.11.2 (PyPI, uploaded 2026-01-31; "An implementation of the Kalman Filter, Kalman Smoother, and EM
algorithm in Python"), filterpy 1.4.5 (last upload 2018-10-10), statsmodels 0.15.0 (2026-08-27) (pypi_*.json). None
is installed in the project environment; the scalar filter is twenty lines of numpy.

### 1.8 Evidence: does it work at retail scale and latency?

- **As a volatility and covariance estimator under microstructure noise: yes, on equities, as a measurement tool.**
  Cartea and Karyampas: "We propose a Kalman-filter-based methodology that allows us to deconstruct price series into
  the true efficient price and the microstructure noise. This approach allows us to employ volatility estimators that
  achieve very low Root Mean Squared Errors (RMSEs) compared to other estimators" (cartea_karyampas_2009.txt). Owens
  and Steigerwald: "We use the Kalman filter to derive more efficient weights, for any given sampling frequency. We
  demonstrate the efficacy of the procedure through an extensive simulation exercise" (owens_steigerwald.txt). Both
  are estimation results (RMSE of volatility), not trading results; neither is on futures; neither has costs because
  neither trades.
- **Kalman price-impact on order-book data:** Mertens, Ciacci, Lillo and Livieri (2022, Quantitative Finance) fit a
  state-space price-impact model with a Kalman filter on 2016 NASDAQ order-book data and report better out-of-sample
  price-impact forecasts than historical estimates. [unverified: known only from the LSE repository page via WebFetch,
  which says "Full text not available from this repository"; not saved as evidence.]
- **Kalman pairs trading, with costs:** He, Wang, Liu and Huang (2023, Journal of Innovation & Knowledge) on minute
  data of 47 Chinese commodity futures: "after considering transaction costs, the cumulative return in-sample reached
  81%, the cumulative return out-of-sample was 21%, and the average monthly Sharpe ratio was 10 in-sample and 18
  out-of-sample" (he_etal_2023_jik.html.txt). Treat with strong caution: a monthly Sharpe ratio of 18 out of sample
  is far outside any plausible range for a published, replicable futures strategy; I could not find the cost rate
  in the saved text by grep (searches for "commission", "slippage", "basis point", "bps" found nothing); and the
  reference list attaches Gatev et al. (1999) to a physiology paper ("Feedforward ankle strategy of balance during
  quiet stance in adults"), a sign of weak editing. It is not evidence I would rely on.
- **Kalman pairs trading, gross only:** Montana, Triantafyllopoulos and Tsagaris (FLS, closely related to the Kalman
  filter): "Our simulation results have shown gross monetary results, and we have assumed that transaction costs are
  negligible" (montana_etal_0709_3884_fls.txt). The Palomar book chapter shows the method with no after-cost
  evidence.
- **Retail latency.** The filter itself costs microseconds per update. Latency matters only through what the feature
  predicts: any edge that lives in sub-second deviations of the filtered price from the mid is exactly what
  co-located firms trade first. From Vancouver (tens of milliseconds to Aurora) a d_t signal would arrive after the
  quote has already moved in most of the cases where it matters. I found no paper testing a Kalman-filtered price
  signal for passive execution at retail latency, with or without costs. That is a gap, not a finding.

---

## 2. Extended and unscented Kalman filters (brief)

### 2.1 Idea

When the state or observation equation is nonlinear, x_t = f(x_{t-1}) + w_t and z_t = h(x_t) + v_t, the Gaussian
algebra of section 1 no longer holds exactly. The **extended Kalman filter (EKF)** linearises f and h around the
current estimate with a first-order Taylor expansion and then runs the ordinary filter. Welch and Bishop: "In
something akin to a Taylor series, we can linearize the estimation around the current estimate using the partial
derivatives of the process and measurement functions", and its weakness: "a fundamental flaw of the EKF is that the
distributions ... of the various random variables are no longer normal after undergoing their respective nonlinear
transformations. The EKF is simply an ad hoc state estimator that only approximates the optimality of Bayes’ rule by
linearization" (welch_bishop_kf_intro.txt). The **unscented Kalman filter (UKF)** instead pushes a small, fixed set of
"sigma points" through the nonlinear functions and recomputes mean and covariance from them. Wan and van der Merwe
(2000): "The unscented transformation (UT) is a method for calculating the statistics of a random variable which
undergoes a nonlinear transformation", with "approximations that are accurate to the third order for Gaussian inputs
for all nonlinearities" (wan_vandermerwe_ukf.txt).

### 2.2 Equations

EKF (standard form; Welch and Bishop Tables 2-1 and 2-2 give it with symbols that pdftotext mangles):

    x_{t|t-1} = f(x_{t-1|t-1}),          P_{t|t-1} = F_t P_{t-1|t-1} F_t' + Q,     F_t = df/dx at x_{t-1|t-1}
    K_t = P_{t|t-1} H_t' (H_t P_{t|t-1} H_t' + R)^{-1},                             H_t = dh/dx at x_{t|t-1}
    x_{t|t} = x_{t|t-1} + K_t (z_t - h(x_{t|t-1})),   P_{t|t} = (I - K_t H_t) P_{t|t-1}

- F_t and H_t are Jacobian matrices (matrices of first partial derivatives) evaluated at the current estimate.

UKF sigma points for an L-dimensional state with mean m and covariance P (Wan and van der Merwe eqs. 15 to 18; the
symbols are lost in the extracted text, so this is a restatement of the standard form they describe):

    lambda = alpha^2 (L + kappa) - L
    chi_0 = m,   chi_i = m + (sqrt((L + lambda) P))_i,   chi_{i+L} = m - (sqrt((L + lambda) P))_i,   i = 1..L
    weights:  W_0^m = lambda / (L + lambda),  W_0^c = lambda / (L + lambda) + (1 - alpha^2 + beta),
              W_i^m = W_i^c = 1 / (2 (L + lambda))
    mean of g(x):  sum_i W_i^m g(chi_i);   covariance: sum_i W_i^c (g(chi_i) - mean)(g(chi_i) - mean)'

- (sqrt(M))_i is the i-th row (or column) of a matrix square root such as the Cholesky factor.
- alpha sets the spread of the points (Wan and van der Merwe: "usually set to a small positive value (e.g., 1e-3)"),
  kappa is "a secondary scaling parameter which is usually set to 0", and beta encodes prior knowledge of the
  distribution ("for Gaussian distributions, [beta = 2] is optimal"; the symbol is lost in extraction).

### 2.3 Data, estimates, worked example

- Data and estimates: the same as the model they filter. They matter only when the program needs a nonlinear
  state-space model, for example log volatility observed through returns (section 3), or a price observed through a
  rounding (tick-grid) function.
- **Worked example (C2F_examples.json, ukf).** Let x ~ N(0, 1) be log variance and ask for E[exp(x/2)], the mean
  volatility multiplier. Exact: exp(1/8) = 1.13315. EKF (linearise at the mean 0): exp(0) = 1.00000, a 12% error,
  because a first-order expansion ignores curvature. UT with L = 1, alpha = 1, kappa = 2, so lambda = 1 x (1 + 2) - 1
  = 2: sigma points 0 and +-sqrt(1 + 2) = +-1.7321, weights 2/3, 1/6, 1/6. Mean = (2/3) x exp(0) + (1/6) x
  (exp(0.8660) + exp(-0.8660)) = 0.66667 + (1/6) x (2.37744 + 0.42062) = 0.66667 + 0.46634 = 1.13301, within 0.012% of
  the exact value.
- A further caution for the canonical stochastic-volatility model (section 3): there y_t = beta exp(x_t / 2) W_t, so
  E[y_t | x_t] = 0 whatever x_t is, and an EKF on y_t gets no information about x_t from the mean. The usual fix is to
  observe log(y_t^2) instead, which is linear in x_t with non-Gaussian (log chi-square) noise; that is the basis of
  the Kim, Shephard and Chib (1998) mixture approach and of quasi-likelihood Kalman fitting.

### 2.4 Hypothesis, compute, evidence

- Hypothesis: none of its own. An EKF or UKF is an implementation choice inside a model; choosing between them after
  seeing results would be a hidden trial. If a nonlinear filter is used, fix the variant in the pre-registration.
- Compute: a UKF costs 2L + 1 function evaluations per step; for L up to 5 on 1.87 million steps that is seconds to
  a minute in numpy on the laptop.
- Evidence: I found no trading evidence specific to EKF or UKF on intraday futures. Their value is in engineering
  (Wan and van der Merwe's examples are time-series estimation and neural-network training).

---

## 3. Particle filters (sequential importance resampling) and stochastic volatility

### 3.1 Idea

When the model is nonlinear or non-Gaussian, the filtering distribution p(x_t | y_1..y_t) has no closed form. A
particle filter represents it by N random samples ("particles") with weights. Each step: move every particle forward
with the state equation, weight it by how well it explains the new observation, and, when the weights become too
uneven, resample (copy heavy particles, drop light ones). Doucet and Johansen (2009/2011 tutorial): "Since their
introduction in 1993 [22], particle filters have become a very popular class of numerical methods for the solution
of optimal estimation problems in non-linear non-Gaussian scenarios. In comparison with standard approximation
methods, such as the popular Extended Kalman Filter, the principal advantage of particle methods is that they do not
rely on any local linearisation technique" (doucet_johansen_pf_tutorial.txt; [22] is Gordon, Salmond and Smith 1993).

### 3.2 Equations

General model (Doucet and Johansen section 2): X_1 ~ mu(x), X_n | X_{n-1} ~ f(x_n | x_{n-1}), Y_n | X_n ~ g(y_n |
x_n). Sequential importance resampling (SIR) with proposal q (their "SMC for filtering" algorithm, symbols restated):

    n = 1:   sample X_1^i ~ q(x_1 | y_1);  weight w_1^i = mu(X_1^i) g(y_1 | X_1^i) / q(X_1^i | y_1);  W_1^i ∝ w_1^i
    n >= 2:  resample if needed; sample X_n^i ~ q(x_n | y_n, X_{n-1}^i);
             incremental weight alpha_n^i = g(y_n | X_n^i) f(X_n^i | X_{n-1}^i) / q(X_n^i | y_n, X_{n-1}^i);
             W_n^i ∝ W_{n-1}^i alpha_n^i (W_{n-1}^i = 1/N right after a resampling step)

Doucet and Johansen write the weight step as "Compute the weights αn Xn−1:n = g( yn |Xni )f ( Xni |Xn−1 i ) / q (
Xn |yn ,Xn−1 )" (mangled by pdftotext; restated above). The **bootstrap filter** of Gordon, Salmond and Smith uses the
state equation itself as the proposal, q = f, so the weight is just the observation density g(y_n | X_n^i).

- **Filtering estimate:** E[phi(x_n) | y_1..y_n] ≈ sum_i W_n^i phi(X_n^i).
- **Likelihood estimate:** p(y_n | y_1..y_{n-1}) ≈ (1/N) sum_i alpha_n^i over the particles that entered step n with
  equal weight. The product over n estimates the likelihood L(theta) (section 0). It is noisy, so maximising it over
  theta needs care (smoothing the estimate across theta, or particle MCMC).
- **When to resample: the effective sample size.** "ESS = ( Σ (Wn^i)^2 )^{-1}" (restated); "The ESS takes values
  between 1 and N and we resample only when it is below a threshold NT ; typically NT = N/2" (Doucet and Johansen).
- **Why resampling at all:** without it, "IS — and thus SIS — provides estimates whose variance increases,
  typically exponentially" with n (Doucet and Johansen). Resampling has its own cost: "some degree of degeneracy is
  inevitable in all but trivial cases: if SMC algorithms are used for sufficiently many time steps every resampling
  step reduces the number of unique values representing X1". For filtering (only the current x_n matters) this is
  harmless; for smoothing and parameter estimation it is the central difficulty.
- **Parameter estimation is the weak point.** Doucet and Johansen: "Although progress has been made, this is a
  difficult problem and it cannot be considered to have been solved in full generality".

**Derivation summary.** Bayes' rule gives the exact recursion p(x_n | y_1..y_n) ∝ g(y_n | x_n) ∫ f(x_n | x_{n-1})
p(x_{n-1} | y_1..y_{n-1}) dx_{n-1}. Replacing p(x_{n-1} | ...) by its weighted particle approximation makes the
integral a finite mixture; drawing from the mixture with proposal q and correcting by importance weights gives the
algorithm. As N grows the estimates converge (for a fixed time n) at the Monte Carlo rate; Doucet and Johansen note
for importance sampling that "the approximation error decreases at a rate of O(1/N ) regardless of the dimension of
the space" (for the variance of the estimate).

### 3.3 The standard example: stochastic volatility

Doucet and Johansen, Example 4: "Xn = αXn−1 + σVn , Yn = β exp (Xn /2) Wn", with "Vn ∼ N (0, 1) and Wn ∼ N (0, 1)",
initial X_1 ~ N(0, sigma^2 / (1 - alpha^2)) (doucet_johansen_pf_tutorial.txt). Kim, Shephard and Chib (1998) call the
same model "The canonical model in this class for regularly spaced data" (ksc_1998_sv_wp.txt; equation symbols lost
in extraction).

- X_n: log variance (deviation from its mean), an AR(1) with persistence alpha (close to 1) and shock size sigma.
- Y_n: the return (mean-corrected), whose standard deviation is beta exp(X_n / 2).
- beta: the typical volatility level.
- The bootstrap weight for a particle with log variance x is the normal density N(y_n; 0, beta^2 exp(x)).

### 3.4 Data, estimates

- Data: a return series. At intraday horizons that is the one-second or ten-second mid change, or trade-by-trade
  prices. Dahlhaus and Neddermeyer build a particle filter that "works directly on the transaction data and updates
  the volatility estimate immediately after the occurrence of a new transaction", with "a nonlinear market
  microstructure noise model" and a decomposition of "spot volatility per transaction times the trading intensity"
  (arxiv_1006_1860_spotvol_pf.txt). For one CME contract, tbbo (every trade with the BBO before it) or mbp-10 (every
  book event in the top ten levels; databento_mbp10.html.txt: "MBP-10 (market by price) provides every order book
  event across the top ten price levels") over 4 to 12 months gives millions of observations: ample for a model
  with 3 to 6 parameters. mbo is not needed.
- Estimates: the filtered spot volatility at each event, its uncertainty, and the likelihood for model comparison.
  It decides nothing by itself; it is a state estimate that a gate or a sizing rule might use.

### 3.5 Worked example: one bootstrap step with five particles (C2F_examples.json, particle)

Parameters alpha = 0.98, sigma = 0.15, beta = 1 (return in ticks). Previous particles x = (-0.4, -0.1, 0.0, 0.2,
0.6), equally weighted. Shocks drawn: (0.5, -1.0, 0.2, 1.2, -0.3).

1. Propagate: x' = 0.98 x + 0.15 shock. First particle: 0.98 x (-0.4) + 0.15 x 0.5 = -0.392 + 0.075 = -0.317. All
   five: (-0.317, -0.248, 0.030, 0.376, 0.543).
2. Observe y = 2.2 ticks. Weight = N(2.2; 0, exp(x')). First particle: variance exp(-0.317) = 0.7284, so w =
   exp(-0.5 x 4.84 / 0.7284) / sqrt(2 pi x 0.7284) = exp(-3.3224) / 2.1393 = 0.03606 / 2.1393 = 0.01686. All five:
   (0.01686, 0.02032, 0.03754, 0.06276, 0.07454). The large move favours high-volatility particles.
3. Normalise: sum = 0.21202; W = (0.0795, 0.0959, 0.1771, 0.2960, 0.3516).
4. Likelihood increment p(y | past) ≈ mean of w = 0.21202 / 5 = 0.0424.
5. ESS = 1 / (0.0795^2 + 0.0959^2 + 0.1771^2 + 0.2960^2 + 0.3516^2) = 1 / 0.2581 = 3.875. The threshold is N/2 =
   2.5 and 3.875 is above it, so the ESS rule would NOT resample at this step. For illustration only, systematic resampling with u = 0.37 uses
   points (0.37 + k) / 5 = 0.074, 0.274, 0.474, 0.674, 0.874 against the cumulative weights (0.0795, 0.1754, 0.3524,
   0.6484, 1.0): it keeps particles 1, 3, 4, 5, 5. Particle 2 is dropped and particle 5 is copied.
6. Filtered mean log variance: sum W x' = 0.0795 x (-0.317) + 0.0959 x (-0.248) + 0.1771 x 0.030 + 0.2960 x 0.376 +
   0.3516 x 0.543 = -0.0252 - 0.0238 + 0.0053 + 0.1113 + 0.1909 = 0.2585, up from the unweighted propagated mean
   0.384 / 5 = 0.077: one big return raises the volatility estimate.

### 3.6 A testable hypothesis from the pilot

**H-PF1 (filtered spot volatility predicts fill quality).** At order placement, compute the filtered spot volatility
sigma_t from a bootstrap SV filter on one-second mid changes (parameters estimated on the training window and then
frozen). Hypothesis: passive fills placed when sigma_t is above its training-window median have a lower mean 10 s
markout than those placed below it.

- Test statistic: difference of mean 10 s markouts (ticks), day-clustered t, one-sided, bar t > 3.0.
- Sample: the same power table as H-KF1 (1,063 fills per group for d = 0.25 tick at sigma = 1.5 ticks; the pilot's
  measured markout dispersion replaces the assumption).
- Trial count: +1 if the model (SV with AR(1) log variance), sampling (1 s), particle count, parameters and median
  split are fixed in advance. A competing simpler feature (an EWMA of squared mid changes) is the honest baseline; if
  the lead wants the SV filter to beat it, that is a second test and +1 more.
- My expectation, stated before any data: an EWMA of squared changes will carry almost all the information the SV
  filter carries at one-second sampling over months, because the filtered SV estimate is itself close to an
  exponentially weighted average of log squared returns. The particle filter earns its cost only if the
  microstructure-noise model (Dahlhaus and Neddermeyer) or the per-transaction time change matters.

### 3.7 Compute

Measured (C2F_bench_results.json): a numpy bootstrap filter with 1,000 particles ran 100,000 steps in 5.39 s on the
CPU (resampling at 1.2% of steps under the ESS < N/2 rule); a torch version on the RTX 3050 ran 10,000 steps with
100,000 particles in 2.26 s with 4 MB of GPU memory. Scaling: 1.87 million one-second steps x 1,000 particles is
about 100 s on the CPU. Filtering is cheap.

Parameter estimation is not. Particle MCMC with 10,000 iterations, each a full pass of about 100 s, would take about
11.6 days of CPU. Two cheaper routes exist: (a) fit the parameters by the Kim-Shephard-Chib MCMC on the regular grid
(Stroud and Johannes report that their C implementation "makes 12,500 draws in 12–25 minutes using a 2.8 GHz Xeon
processor for each year of 5-minute returns (around 70,500 observations)", stroud_johannes_2014.txt; four months of
ten-second regular-hours returns is about 80 x 2,340 = 187,200 observations, so roughly 30 to 70 minutes at that
rate if the code were as efficient), then run the particle filter only for filtering; (b) quasi-likelihood on
log(y^2) with a Kalman filter. A cloud GPU would help only route (c), many particle-likelihood evaluations in
parallel: at RunPod's listed $0.89/hr for an RTX 4090 (runpod_pricing.html.txt), 100 GPU-hours would be $89. I see
no need for it in this program.

Software: particles 0.4 (PyPI, "Sequential Monte Carlo in Python", uploaded 2023-11-06; pypi_particles.json).

### 3.8 Evidence

- **Intraday S&P futures volatility, out of sample: positive for forecasting.** Stroud and Johannes estimate "models
  of high frequency index futures returns using ‘around the clock’ 5-minute returns" with "multiple persistent
  stochastic volatility factors, jumps ... seasonal components ... and announcement effects", use "particle filters
  to construct likelihood functions for model comparison and out-of-sample forecasting from 2009 to 2012", and report
  that the "approach improves realized volatility forecasts by up to 50% over existing benchmarks"
  (stroud_johannes_2014.txt). Their Table 8 ("Out-of-sample VXX trading results, March 2009–March 2012") gives Sharpe
  ratios of 1.78 to 2.32 for the SV models' single-model rules; I found no mention of transaction costs in the saved
  text (grep for "transaction cost", "bid-ask", "commission" returns nothing), and the SV rules were short the VIX index (long the VXX, which the paper describes as inversely linked to the VIX) on
  396 to 551 of the days, a period in which being short volatility paid. This is a volatility forecasting
  result on 5-minute data, not evidence for a passive-order strategy.
- **Online spot volatility at transaction level:** Dahlhaus and Neddermeyer report that "an efficient implementation
  of the method requires a few milliseconds for a single update of the estimator (including one iteration of the
  particle filter with 500 particles)" (arxiv_1006_1860_spotvol_pf.txt). Feasible at retail latency; no trading test.
- **Null or negative evidence:** I found no out-of-sample, cost-inclusive trading result for a particle-filter
  signal at intraday horizons in futures. The method's known failure mode is parameter estimation (Doucet and
  Johansen's quote above), not filtering.

---

## 4. Hidden Markov models and Hamilton (1989) regime switching

### 4.1 Idea

The market is assumed to switch between a small number K of unobserved states ("regimes"), for example calm and
turbulent, or thick and thin book. The state follows a Markov chain: the chance of moving to state j depends only on
the current state. In each state the observations (returns, spreads, depth, trade counts) come from a different
distribution. The filter computes, after each observation, the probability of being in each state now. Hamilton
(1989): "The parameters of an autoregression are viewed as the outcome of a discrete-state Markov process. ... The
econometrician is presumed not to observe these shifts directly, but instead must draw probabilistic inference about
whether and when they may have occurred based on the observed behavior of the series. The paper presents an
algorithm for drawing such probabilistic inference in the form of a nonlinear iterative filter. The filter also
permits estimation of population parameters by the method of maximum likelihood" (hamilton_1989.pdf, page 357,
read from the page image). In the engineering literature the same model is the hidden Markov model (HMM); Rabiner's
tutorial (1989) set out its "three fundamental problems" (rabiner_1989.pdf, page 257, page image): evaluating the
likelihood (forward algorithm), finding the most likely state sequence (Viterbi), and estimating the parameters
(Baum-Welch).

### 4.2 Equations

**Model.** s_t in {1..K} is the regime. Transition probabilities, Hamilton (Palgrave) eq. 4: "Pr(st = j|st−1 = i,
st−2 = k, ..., yt−1 , yt−2 , ...) = Pr(st = j|st−1 = i) = pij". Each row of the K x K matrix P = [p_ij] sums to 1. The
emission density in regime j is eta_jt = f(y_t | s_t = j, past; theta); for Hamilton's AR(1) example (eq. 7) it is
the normal density with mean c_j + phi y_{t-1} and variance sigma^2. For a volatility regime with zero mean it is
N(y_t; 0, sigma_j^2).

- theta: all parameters (p_ij, the emission means and variances).
- Expected time spent in regime j once entered: 1 / (1 - p_jj) steps (geometric duration; standard result).

**Forward filter (Hamilton filter), eqs. 5 to 12 of the Palgrave entry.** Input: the filtered probabilities from
t-1, "ξ i,t−1 = Pr(st−1 = i|Ωt−1 ; θ)". Then:

    predicted:   Pr(s_t = j | Omega_{t-1}) = sum_i p_ij xi_{i,t-1}
    density:     f(y_t | Omega_{t-1}) = sum_i sum_j p_ij xi_{i,t-1} eta_jt              (eq. 8)
    filtered:    xi_jt = sum_i p_ij xi_{i,t-1} eta_jt / f(y_t | Omega_{t-1})            (eq. 9)
    likelihood:  log f(y_1..y_T | y_0) = sum_t log f(y_t | Omega_{t-1})                 (eq. 10)

Start: "If the Markov chain is presumed to be ergodic, one can use the unconditional probabilities ξ i0 = Pr(s0 =
i) = (1 − pjj) / (2 − pii − pjj)" (two-state case; fraction restated). In matrix form for K regimes (eqs. 11 and 12):
the predicted vector is P' xi_{t-1|t-1}, multiplied element by element by the density vector eta_t, then
normalised by its sum. This is the forward algorithm of the HMM literature in its normalised form; Jurafsky and
Martin: "we use an efficient O(N 2 T ) algorithm called the forward algorithm. The forward algorithm is a kind of
dynamic programming algorithm" (jurafsky_martin_hmm_appendix.txt; N^2 T means states squared times length).

**Derivation summary.** By Bayes' rule, Pr(s_t = j | Omega_t) ∝ f(y_t | s_t = j, Omega_{t-1}) Pr(s_t = j | Omega_{t-1}),
and by the Markov property Pr(s_t = j | Omega_{t-1}) = sum_i p_ij Pr(s_{t-1} = i | Omega_{t-1}). The normalising
constant is the one-step predictive density, which is the likelihood contribution. Assumptions: the regime is
Markov of order one with constant transition probabilities (Hamilton notes they can depend on observable variables:
"The calculations in (11) and (12) remain valid when the probabilities in P depend on ... functions of observable
variables"); given the regime and the past, y_t has a known density.

**Backward pass and smoothing (training window only).** The backward recursion beta_t(i) = sum_j p_ij eta_{j,t+1}
beta_{t+1}(j), beta_T = 1, gives the smoothed probabilities gamma_t(i) = Pr(s_t = i | all data) ∝ alpha_t(i)
beta_t(i), with alpha_t the unnormalised forward quantity, and the expected transitions xi_t(i,j) = Pr(s_t = i,
s_{t+1} = j | all data) ∝ alpha_t(i) p_ij eta_{j,t+1} beta_{t+1}(j). These use future data.

**Baum-Welch (EM) estimation.** Jurafsky and Martin: "The standard algorithm for HMM training is the forward-backward,
or Baum-Welch algorithm (Baum, 1972), a special case of the Expectation-Maximization or EM algorithm", and "In the
E-step, we compute the expected state occupancy count γ and the expected state transition count ξ from the earlier
A and B probabilities. In the M-step, we use γ and ξ to recompute new A and B probabilities". For Gaussian
emissions the M-step is (standard closed forms):

    p_ij      = sum_{t<T} xi_t(i,j) / sum_{t<T} gamma_t(i)
    mu_j      = sum_t gamma_t(j) y_t / sum_t gamma_t(j)
    sigma_j^2 = sum_t gamma_t(j) (y_t - mu_j)^2 / sum_t gamma_t(j)

Each iteration cannot lower the likelihood; it converges to a local maximum, so the starting values matter and must
be fixed in advance (or several fixed starts, keeping the highest training likelihood, by a stated rule).

**Viterbi.** The most likely whole path: Jurafsky and Martin eq. A.14, "vt ( j) = max vt−1 (i) ai j b j (ot )"
(a_ij = p_ij, b_j(o_t) = eta_jt), with back-pointers and a final backtrace. Bulla et al. use Viterbi paths for their
allocation rule (section 5). Viterbi uses all data up to the end of the sequence it is run on: run on data through t
only and keep only its last state, it is a causal (legal) rule; run on the whole sample, it looks ahead.

**Choosing K is not a standard test.** Hamilton: "the likelihood ratio test of this hypothesis fails to satisfy the
usual regularity conditions, because under the null hypothesis, some of the parameters of the model would be
unidentified", so "the likelihood ratio test does not have the usual χ2 limiting distribution". For this program the
practical consequence is to fix K = 2 before seeing data rather than select it.

### 4.3 Data

- For a volatility regime: a regular series of mid changes (1 s or 10 s). For a liquidity regime: the top-of-book
  spread, L1 depth, total depth in the top 10 levels, trade count per interval. For an order-flow regime: signed trade
  volume or order-flow imbalance per interval. mbp-10 supplies all of these; tbbo supplies trades and the BBO only
  ("BBO on trade (TBBO) provides every trade event alongside the BBO immediately before the effect of each trade",
  databento_tbbo.html.txt), which is enough for volatility and trade-flow regimes but not depth regimes. mbo
  ("provides every order book event across every price level, keyed by its order ID. This allows you to determine
  the queue position of each order", databento_mbo.html.txt) is needed for queue position, not for an HMM.
- Is 4 to 12 months enough? For estimation, yes: four months of regular hours at 10 s is about 187,000 steps; with
  regimes lasting 20 to 100 steps there are thousands of regime episodes, more than enough for 2 to 10 parameters.
  For TESTING a gate, the binding sample is the number of fills, not the number of steps, and the effective sample
  is closer to the number of days (about 80 in four months) when regimes cluster by day (section 6).

### 4.4 What it estimates or decides

The filtered probability of each regime at each step, the regime-specific parameters (volatility, spread, depth
levels), and the transition probabilities (how sticky each regime is). A gate turns the filtered probability into
an on/off decision for the passive strategy (section 6).

### 4.5 Worked examples (C2F_examples.json)

**(a) Hamilton filter, two volatility regimes, 10-second mid changes in ticks.** Calm regime sigma_1 = 0.5 tick,
turbulent sigma_2 = 2 ticks, p_11 = 0.99 (expected duration 1 / 0.01 = 100 steps, about 17 minutes), p_22 = 0.95
(20 steps, about 3 minutes). Start at the ergodic probabilities: xi_10 = (1 - 0.95) / (2 - 0.99 - 0.95) = 0.05 / 0.06
= 0.83333, xi_20 = 0.16667. Densities: N(0; 0, 0.5^2) = 1 / (0.5 sqrt(2 pi)) = 0.79788; N(0; 0, 2^2) = 0.19947.

| t | y_t | predicted (calm, turb.) | eta (calm, turb.) | f(y_t \| past) | filtered (calm, turb.) |
|---|---|---|---|---|---|
| 1 | 0.0 | 0.83333, 0.16667 | 0.79788, 0.19947 | 0.83333 x 0.79788 + 0.16667 x 0.19947 = 0.69815 | 0.95238, 0.04762 |
| 2 | 2.0 | 0.95238 x 0.99 + 0.04762 x 0.05 = 0.94524, 0.05476 | 0.00027, 0.12099 | 0.00688 | 0.03678, 0.96322 |
| 3 | 1.0 | 0.08458, 0.91542 | 0.10798, 0.17603 | 0.17028 | 0.05363, 0.94637 |
| 4 | 0.0 | 0.10042, 0.89958 | 0.79788, 0.19947 | 0.25956 | 0.30868, 0.69132 |

One 2-tick move (a 4-sigma event under calm, 1 sigma under turbulent) flips the filter to 96% turbulent; one quiet
step afterwards only brings it back to 69% turbulent, because the regime is sticky.

**(b) Why smoothing and Viterbi look ahead.** Same model, observations (0, 0.25, 1.5, 0.25). Filtered turbulent
probabilities: 0.048, 0.016, 0.304, 0.106; Viterbi path: calm, calm, calm, calm. Now two more observations arrive,
2.5 and 3.0. The filtered probabilities for t = 1..4 do not change (they cannot: they use data to t only), and are
0.9997 and 1.0000 for t = 5, 6. But the Viterbi path for the six observations is turbulent at all six steps,
including t = 1..4. A backtest that used the Viterbi (or smoothed) label at t = 3 would have "known" at t = 3 that the
market was turbulent, which nobody trading at t = 3 could know.

**(c) Measured size of the bias.** On 200,000 synthetic steps from a two-state model (p_11 = 0.995, p_22 = 0.98,
sigma = 1 and 3), the share of steps whose regime was classified correctly (probability above 0.5) was 97.25% with
filtered probabilities and 98.98% with smoothed ones (C2F_bench_results.json). The 1.7 points are mostly the
regime changes the filter recognises late; those are the moments a volatility gate exists for, so the bias falls
where it matters most.

**(d) Baum-Welch recovers the parameters.** Ten EM iterations on those 200,000 steps from deliberately wrong starts
(p = 0.95/0.90, sigma = 0.5 sd and 2 sd of the data) returned p_11 = 0.99536, p_22 = 0.98036, sigma = 1.0029 and
3.0104 (true 0.995, 0.98, 1, 3); the log-likelihood rose from -343,389.1 to -332,005.96 and stopped changing after
iteration 8 (C2F_bench_results.json).

### 4.6 A testable hypothesis from the pilot

**H-HMM1 (a volatility-regime gate improves the passive order's per-order outcome).** Fit a two-state Gaussian HMM
(zero means, regime variances) to 10-second mid changes on the training window. In the evaluation window, compute
the filtered turbulent probability xi_2t with the frozen parameters. Gate rule: post the passive 1-lot only when
xi_2t < 0.5 at the decision time; otherwise do not post (or cancel). Hypothesis: the mean per-order outcome of the
gated strategy exceeds that of the ungated strategy, where the per-order outcome is the 10 s markout plus the
half-spread captured if filled, and zero if not filled.

- Why per order and not per fill: a gate changes which orders fill. Comparing markouts conditional on fill would
  hide the lost spread capture of the orders not posted, and would reward any rule that simply fills less.
- Test statistic: difference of daily means of per-order outcomes (gated minus ungated, on the same days), a paired
  t-statistic over days, one-sided, bar t > 3.0. Pairing by day removes the day effect.
- Sample: with paired days, n days = (z_a + z_b)^2 s_D^2 / d^2, where s_D is the standard deviation of the daily
  difference. The pilot must measure s_D; with 80 days and t > 3.0 at power 0.8 the detectable daily difference is
  d = 3.84 s_D / sqrt(80) = 0.43 s_D. A per-fill comparison instead (gate-on fills versus gate-off fills) needs the
  per-group numbers of the H-KF1 table, about 1,000 fills per group for a quarter-tick effect at 1.5 ticks dispersion.
- Trial count: K = 2, the feature (10 s mid change), the emission family (Gaussian, zero mean), the threshold (0.5),
  the training window, the refit schedule (none inside the evaluation window, or a stated weekly refit), the EM
  starts and the stopping rule all fixed in advance: N + 1. A grid of K in {2, 3} x three feature sets (volatility,
  spread, trade count) x three thresholds (0.3, 0.5, 0.7) would be N + 18.

**H-HMM2 (liquidity regime and queue time).** Same structure with the observation vector (log spread, log L1 depth)
and the hypothesis that queue times are longer and 10 s markouts worse when the thin-book state is filtered above
0.5. Separately counted, N + 1.

### 4.7 Compute

Measured (numpy, Python loop over time, C2F_bench_results.json): forward filter 200,000 steps in 0.72 s; backward
pass 2.0 s; ten Baum-Welch iterations 27.3 s. Scaling to 1.87 million one-second steps: about 4.5 minutes for ten
iterations. Everything fits on the laptop with a few hundred MB of memory. hmmlearn 0.3.3 (PyPI, uploaded
2024-10-31; "Hidden Markov Models in Python with scikit-learn like API") and statsmodels 0.15.0 (Markov-switching
regression) exist; neither is in the project environment, and a numpy version is short.

### 4.8 Evidence

- **Intraday E-mini S&P futures, HMM momentum, 1-minute bars: pre-cost positive, one year, weak cost model.**
  Christensen, Godsill and Turner (arXiv 2006.08307): "The model is simulated on one year’s worth of e-mini S&P500
  futures data at one minute sampling frequency, and it is shown that pre-cost the models have a Sharpe ratio in
  excess of 2.0", and "Post-cost results reduce the Sharpe ratio of the HMM strategies by approximately 15%"
  (christensen_godsill_turner_2020_hmm_momentum.txt). I could not find the cost assumption in the saved text (grep
  for "commission", "slippage", "spread", "tick" finds only definitions). A 15% haircut for a one-minute strategy is
  far smaller than the program's measured round trip would imply (D.1b: robust patterns worth "about 0.1 tick per
  trade, against a 2.1-tick round-turn cost", quoted in C3_lead_draft.md). One year of data, no deflation for the
  model variants tried.
- **Daily equity indices, regime-based allocation: positive out of sample with stated costs.** Bulla et al. (2011):
  "transaction costs are fixed at 10 basis points (0.10%) for a one-way trade", and "Portfolio risk is lowered by an
  average of 41% for all markets under consideration. Besides, annualized excess return between 18.5 (S&P 500) and
  201.6 (Nikkei) basis points can be realized by avoiding highly volatile periods"
  (bulla_etal_2011_ms_allocation.txt). This is the clearest positive case: a regime model used as a GATE (stay out in
  the high-volatility state), not as a return forecaster. It is daily and slow, so it says nothing direct about
  10-second regimes.
- **Forecasting failure of regime models: negative.** Engel (1994), 18 exchange rates: "By the mean-squared-error
  criterion, the Markov model does not generate superior forecasts to a random walk or the forward rate"
  (engel_1994_ms_fx.txt). Bessec and Bouabdallah: "We find that the main source of error is due to the
  misclassification of future regimes" (bessec_bouabdallah_2005.txt). Dacco and Satchell (1999), "Why do
  regime-switching models forecast so badly?", argue that a small regime-classification error can erase the gain
  from knowing the true model [unverified: known from a search-result abstract only; full text paywalled].
- **Order-book regimes, statistical not trading:** Li, Xing and Chen (arXiv 1912.00764) find on NASDAQ that
  "inter-trade durations in ultra-high frequency have two modes", that "the regime switchings are driven by the
  changes of high-frequency traders (HFTs) between providing and taking liquidity", and that their two-state model
  with transition probabilities driven by lagged order-book factors "has good in-sample fitness and the superior
  out-of-sample performance" (arxiv_1912_00764.txt). One mode is "to the order of approximately 10−4 seconds": a
  regime that switches on the 100-microsecond scale is invisible to a trader with tens of milliseconds of latency.
- **Theory for market making under hidden regimes:** Campi and Zabaljauregui (arXiv 1902.01157): order "intensities
  ... depend not only on the spreads she quotes, but also on unobservable factors modelled by a hidden Markov chain"
  (arxiv_1902_01157_mm_hmm.txt). Theory only; no empirical test.
- **Liquidity-regime delay of orders:** Brigida (2020, Applied Finance Letters) reportedly finds a four-state Markov
  switching model with a state of rapidly varying liquidity and proposes delaying orders in it [unverified: search
  snippet only; the download URL returned 22 bytes].

---

## 5. Evidence on intraday futures, collected

What the fetched literature shows, sorted by how close it is to this program's question (a 1-lot passive order on
one CME contract, tens of milliseconds from the exchange, net of retail costs):

| Study | Market, horizon | Method | Out of sample? | Costs? | Result | Relevance |
|---|---|---|---|---|---|---|
| Christensen, Godsill, Turner (2020) | E-mini S&P, 1-min bars, 2011 | HMM / IOHMM momentum, forward algorithm | yes, within 2011 ("each one of the data points used to evaluate a trade had not been used in any of the previous stages") | yes, assumption not found | pre-cost Sharpe > 2, post-cost about 15% lower | closest futures match; one year, no deflation, aggressive not passive |
| Stroud, Johannes (2014) | S&P futures, 5-min, 2007-2012 | SV with jumps and seasonality, MCMC + particle filter | yes, 2009-2012 | no costs in the VXX test | RV forecasts up to 50% better; VXX rule Sharpe about 2 | volatility forecasting only |
| He et al. (2023) | 47 Chinese commodity futures, minute | Kalman hedge ratio pairs | yes | claimed, rate not found | OOS monthly Sharpe 18 | implausible; weak editing; not relied on |
| Li, Xing, Chen (2019) | NASDAQ stocks, trade durations | 2-state regime switching with LOB-driven transitions | yes (statistical fit) | n/a | two regimes, one at about 1e-4 s | regimes partly at speeds retail cannot see |
| Dahlhaus, Neddermeyer (2013) | transaction data | particle filter spot vol with microstructure noise | n/a | n/a | few ms per update with 500 particles | feasibility only |
| Cartea, Karyampas (2009/2011) | equities, high frequency | Kalman efficient price | simulation and data | n/a | lower RMSE volatility | measurement only |
| Bulla et al. (2011) | equity indices, daily | 2-state HMM gate | yes | 10 bp one way | risk -41%, excess return 18.5 to 201.6 bp a year | positive gate evidence, but daily |
| Engel (1994); Bessec, Bouabdallah (2005) | FX quarterly; Monte Carlo | Markov switching forecasts | yes | n/a | no MSE gain; misclassification dominates | negative for regime forecasting |

What is missing, stated as a gap rather than a finding: I found no study that uses a Kalman filter, particle filter
or HMM to gate or time passive limit orders on a CME futures contract, out of sample, net of costs, at retail
latency. The closest evidence is either (a) the right market at the wrong horizon or side of the book (1-minute
aggressive momentum), (b) the right idea at the wrong frequency (daily HMM gates), or (c) estimation results with no
trading. The section 6 protocol is designed so that the pilot can produce such a test without the usual biases.

---

## 6. How a regime model could gate a passive strategy without adding hidden trials

A gate is a rule "post the passive order only when the filtered state is X". It adds hidden trials in five ways. Each
has a countermeasure that can be written into a pre-registration. These are proposals for the lead; the selection
rules themselves are the lead's decision.

1. **Model choices made after seeing results.** K, the observation vector, the sampling interval, the emission
   family, the threshold, the training window, the refit schedule, the EM starting values and stopping rule are all
   researcher choices. Countermeasure: fix every one in the declaration, with its hash, before the evaluation data are
   touched. Every alternative actually run counts into N, including ones abandoned for bugs. A deterministic rule for
   multiple EM starts (for example 5 fixed seeds, keep the highest training likelihood) is one configuration, not
   five, because it selects on training likelihood only.
2. **Look-ahead through smoothing or Viterbi.** Section 4.5 shows the mechanism and its size. Countermeasure: the
   gate input is the filtered probability xi_{t|t} computed with parameters frozen from the training window; the
   code computes it with a forward pass only, and a unit test asserts that the gate value at t is unchanged when data
   after t are deleted (the test that example (b) passes for filtered probabilities and fails for Viterbi).
3. **Parameter leakage.** Parameters fitted on the whole sample carry information from the evaluation window even if
   the filter itself is causal. Countermeasure: fit on the training window only; leave an embargo between training
   and evaluation of at least one trading day (longer than the 60 s markout and than the slow regime's expected
   duration); if refits are allowed, use expanding or rolling windows that end before each evaluation day, by a
   schedule fixed in advance.
4. **Label switching.** An HMM's states have no names; "state 2" can be the calm one in one fit and the turbulent
   one in the next. Countermeasure: define the gated state by a property (the state with the larger emission
   variance), not by its index.
5. **Survivor accounting.** A gate that posts fewer orders can look better per fill while earning less per order.
   Countermeasure: the test statistic is per decision opportunity (per order the ungated strategy would have posted),
   with unposted and unfilled orders scored as zero, compared with the ungated baseline on the same days (paired by
   day). The fill rule must be TopstepX's trade-through rule, not touch fills.

Two further points that are about honesty rather than leakage:

- **The simple competitor.** A filtered HMM probability is, in practice, close to a smooth function of a recent
  realised-volatility estimate. If the HMM gate passes, the natural question is whether a fixed threshold on an
  EWMA of squared mid changes would have done as well. Testing both adds one trial. Declaring in advance that only
  the simple gate is tested is also a valid choice, and cheaper in N.
- **Regime models already tried.** C3_lead_draft.md item 4 notes that "Hidden Markov regimes stand where the
  deterministic volatility-regime gates stood (D-H1, the VXN bands, G9; C1 section 2)". Those earlier gates were on 1-minute bars
  for directional rules. A gate for passive orders on order-book data is a different hypothesis, but the lead should
  decide whether the earlier gate tests bear on its prior.

---

## 7. Compute summary and cloud prices

| Method | Typical job on 4 months of one contract | Measured on the laptop (synthetic) | Needs a bigger machine? |
|---|---|---|---|
| Kalman local level | filter + MLE on 1.87 M one-second steps | 0.85 s per 1 M steps (loop); 0.074 s per 10 M (steady state); MLE 0.68 s on 1 M | no |
| Kalman hedge ratio | 2-state filter on two contracts | same order as above | no |
| EKF / UKF | 2L+1 evaluations per step | not measured; seconds to a minute by scaling | no |
| Particle filter (SV) | filtering, 1,000 particles | 5.39 s per 100 k steps CPU; GPU 2.26 s for 10 k steps x 100 k particles (4 MB) | no for filtering; particle MCMC estimation about 11.6 CPU-days at 10 k iterations, avoidable |
| HMM (2 states) | Baum-Welch, 10 iterations | 27.3 s on 200 k steps; about 4.5 min on 1.87 M | no |

Current cloud prices, for reference only (fetched 2026-10-21; pages saved): Lambda lists "NVIDIA A10 24 GB 30 226 GiB
1.3 TiB SSD $1.29" per GPU-hour and "NVIDIA A100 PCIe 40 GB ... $1.99" (lambda_pricing.html.txt); RunPod lists "RTX
4090 24 GB VRAM 41 GB RAM 6 vCPUs $ 0.89 /hr" and "RTX 3090 24 GB VRAM 125 GB RAM 16 vCPUs $ 0.5 /hr"
(runpod_pricing.html.txt); Hetzner lists dedicated-vCPU cloud servers "starting from max/mo. € 43.49 per month, excl.
VAT" (hetzner_cloud.html.txt). None of the methods in this section needs them. The one job that might, particle-MCMC
parameter estimation, is avoidable (section 3.7); if done anyway, 100 GPU-hours on the RunPod RTX 4090 would cost
about $89.

---

## 8. Candidate hypotheses in one table (proposals; declarations and counts are the lead's)

| ID | Feature or gate | Outcome | Statistic | Sample (assumption: markout sd 1.5 ticks) | N added if fully fixed in advance |
|---|---|---|---|---|---|
| H-KF1 | sign of filtered efficient price minus mid at placement | 10 s markout of fills | difference of means, day-clustered t > 3.0 | about 1,063 fills per group for 0.25 tick | +1 (up to +12 with observation, sampling and horizon variants) |
| H-PF1 | filtered SV spot volatility above training median | 10 s markout of fills | difference of means, day-clustered t > 3.0 | as H-KF1 | +1 (+1 more for an EWMA competitor) |
| H-HMM1 | filtered turbulent probability < 0.5 gates posting | per-order outcome (markout + half-spread if filled, 0 if not) | paired-by-day t > 3.0, gated minus ungated | detects 0.43 s_D with 80 days | +1 (+18 for a K x feature x threshold grid) |
| H-HMM2 | filtered thin-book probability | queue time and 10 s markout | difference of means, day-clustered | as H-KF1 per group | +1 |
| (none) | dynamic hedge ratio | spread trade | n/a | needs a second contract | not testable on the one-contract pilot |

The power numbers use z = 3.0 (the program's t bar) and power 0.8: n per group = 2 x 3.8416^2 x (sigma/d)^2 =
29.52 (sigma/d)^2. The pilot's measured markout dispersion and the intraclass correlation of fills within a day must
replace the 1.5-tick assumption before any declaration.

---

## 9. Verdicts (for this program)

| Method | Verdict | Reason |
|---|---|---|
| Kalman filter, local level (efficient price + noise) | maybe | Cheap and exact for its assumptions, and the q/r decomposition is a useful pilot measurement. As a signal it is an EWMA with a principled span; the sub-second deviations it could detect are what co-located firms trade first. Worth one pre-registered test (H-KF1) at most. |
| Kalman filter, dynamic hedge ratio | skip | Needs a second contract the pilot does not buy, pays two round trips, and the cost-inclusive evidence found is either gross-only (Montana et al.) or implausible (He et al.). |
| Extended / unscented Kalman | skip as a separate method | An implementation detail of a nonlinear model. If a nonlinear model is used, fix the variant in advance; never choose it on results. |
| Particle filter (SV) | skip for now | Filtering is cheap, but at one-second sampling it should add little over an EWMA of squared changes; parameter estimation is the hard, expensive part, and no cost-inclusive intraday trading evidence was found. Revisit only if the pilot shows that discreteness (tick-grid noise) dominates. |
| HMM / Hamilton regime switching as a gate | maybe (one pre-registered gate; worth one test, not evidence of an intraday effect) | The only method here with a clear role for a passive strategy: deciding when not to post. Positive out-of-sample, cost-inclusive evidence exists for HMM gates at daily frequency (Bulla et al.), and the computation is minutes on the laptop. The risks (look-ahead via smoothing or Viterbi, label switching, configuration grids) are controllable by the section 6 protocol. Expect a modest effect; the regime-forecasting literature (Engel; Bessec and Bouabdallah) warns that misclassification erodes gains. |
| HMM as a return forecaster (directional) | skip | The program's directional tests failed on cost; the one intraday futures HMM study found is pre-cost dominated, one year long, and aggressive. |

---

## References

Saved files are under `reports/stage_e28_briefs/pages/C2_Filter/` (sha256 in `log.tsv`).

1. Kalman, R. E. (1960). A new approach to linear filtering and prediction problems. Transactions of the ASME,
   Journal of Basic Engineering 82 (Series D), 35-45. Copy: cs.yale.edu/homes/yry/readings/general/Kalman1960.pdf.
   File: kalman_1960.pdf/.txt.
2. Welch, G., Bishop, G. (2004 revision). An Introduction to the Kalman Filter. UNC-Chapel Hill TR 95-041.
   techreports.cs.unc.edu/papers/95-041.pdf. File: welch_bishop_kf_intro.pdf/.txt.
3. Hamilton, J. D. (1989). A new approach to the economic analysis of nonstationary time series and the business
   cycle. Econometrica 57(2), 357-384. Copy: users.ssc.wisc.edu/~bhansen/718/Hamilton1989.pdf (scanned). File:
   hamilton_1989.pdf.
4. Hamilton, J. D. (2005). Regime-Switching Models. Prepared for the Palgrave Dictionary of Economics.
   econweb.ucsd.edu/~jhamilto/palgrav1.pdf. File: hamilton_palgrave_regime.pdf/.txt.
5. Rabiner, L. R. (1989). A tutorial on hidden Markov models and selected applications in speech recognition.
   Proceedings of the IEEE 77(2), 257-286. Copy: cs.ubc.ca/~murphyk/Bayes/rabiner.pdf (scanned). File:
   rabiner_1989.pdf.
6. Jurafsky, D., Martin, J. H. (draft of August 2026). Speech and Language Processing, Appendix A: Hidden Markov
   Models. web.stanford.edu/~jurafsky/slp3/A.pdf. File: jurafsky_martin_hmm_appendix.pdf/.txt.
7. Doucet, A., Johansen, A. M. (2011). A tutorial on particle filtering and smoothing: fifteen years later. In
   Handbook of Nonlinear Filtering, Oxford University Press. stats.ox.ac.uk/~doucet/doucet_johansen_tutorialPF2011.pdf.
   File: doucet_johansen_pf_tutorial.pdf/.txt.
8. Gordon, N. J., Salmond, D. J., Smith, A. F. M. (1993). Novel approach to nonlinear/non-Gaussian Bayesian state
   estimation. IEE Proceedings F 140(2). [not fetched; cited through Doucet and Johansen ref. 22]
9. Wan, E. A., van der Merwe, R. (2000). The unscented Kalman filter for nonlinear estimation. IEEE AS-SPCC.
   groups.seas.harvard.edu/courses/cs281/papers/unscented.pdf. File: wan_vandermerwe_ukf.pdf/.txt.
10. Kim, S., Shephard, N., Chib, S. (1998). Stochastic volatility: likelihood inference and comparison with ARCH
    models. Review of Economic Studies 65, 361-393. Working-paper copy: econwpa.ub.uni-muenchen.de/econ-wp/em/papers/
    9610/9610002.pdf. File: ksc_1998_sv_wp.pdf/.txt.
11. Cartea, A., Karyampas, D. (2009). Volatility and covariation of financial assets: a high-frequency analysis.
    UC3M Working Paper 09-76 (forthcoming Journal of Banking and Finance). e-archivo.uc3m.es/bitstream/10016/5904/1/
    wb097609.pdf. File: cartea_karyampas_2009.pdf/.txt.
12. Owens, J. P., Steigerwald, D. G. (2006). Noise reduced realized volatility: a Kalman filter approach. Advances in
    Econometrics 20. Copy: webarchive.ucr.edu/.../DougSteigerwald.pdf. File: owens_steigerwald.pdf/.txt.
13. Ho, M., Xin, J. (2016). Sparse Kalman filtering approaches to covariance estimation from high frequency data in
    the presence of jumps. arXiv 1602.02185. File: ho_xin_2016_sparse_kf.pdf/.txt.
14. Mertens, L. P., Ciacci, A., Lillo, F., Livieri, G. (2022). Liquidity fluctuations and the latent dynamics of
    price impact. Quantitative Finance 22(1), 149-169. [unverified: repository landing page only, via WebFetch]
15. Palomar, D. P. Portfolio Optimization (online book), section 15.6 Kalman pairs trading.
    bookdown.org/palomar/portfoliooptimizationbook/15.6-kalman-pairs-trading.html. File: palomar_book_kalman_pairs.html.
16. Montana, G., Triantafyllopoulos, K., Tsagaris, T. (2009). Flexible least squares for temporal data mining and
    statistical arbitrage. arXiv 0709.3884. File: montana_etal_0709_3884_fls.pdf/.txt.
17. Triantafyllopoulos, K., Montana, G. (2011). Dynamic modeling of mean-reverting spreads for statistical
    arbitrage. arXiv 0808.1710. File: triantafyllopoulos_montana_0808_1710.pdf/.txt (fetched; not quoted).
18. He, C., Wang, T., Liu, X., Huang, K. (2023). An innovative high-frequency statistical arbitrage in Chinese
    futures market. Journal of Innovation & Knowledge 8(4), 100429. File: he_etal_2023_jik.html/.txt.
19. Stroud, J. R., Johannes, M. S. (2014). Bayesian modeling and forecasting of 24-hour high-frequency volatility.
    JASA 109, 1368-1384. arXiv 1211.2961. File: stroud_johannes_2014.pdf/.txt.
20. Dahlhaus, R., Neddermeyer, J. C. (2013). On-line spot volatility-estimation and decomposition with nonlinear
    market microstructure noise models. arXiv 1006.1860. File: arxiv_1006_1860_spotvol_pf.pdf/.txt.
21. Christensen, H. L., Godsill, S. J., Turner, R. E. (2020). Hidden Markov models applied to intraday momentum
    trading with side information. arXiv 2006.08307. File: christensen_godsill_turner_2020_hmm_momentum.pdf/.txt.
22. Bulla, J., Mergner, S., Bulla, I., Sesboüé, A., Chesneau, C. (2011). Markov-switching asset allocation: do
    profitable strategies exist? Journal of Asset Management 12(5). MPRA 21154. File: bulla_etal_2011_ms_allocation.pdf/.txt.
23. Engel, C. (1994). Can the Markov switching model forecast exchange rates? Journal of International Economics 36,
    151-165. File: engel_1994_ms_fx.pdf/.txt.
24. Bessec, M., Bouabdallah, O. (2005). What causes the forecasting failure of Markov-switching models? A Monte Carlo
    study. EconWPA 0503018 (later Studies in Nonlinear Dynamics & Econometrics). File: bessec_bouabdallah_2005.pdf/.txt.
25. Dacco, R., Satchell, S. (1999). Why do regime-switching models forecast so badly? Journal of Forecasting 18(1),
    1-16. [unverified: abstract via search result only]
26. Li, Z., Xing, H., Chen, X. (2019). A multifactor regime-switching model for inter-trade durations in the limit
    order market. arXiv 1912.00764. File: arxiv_1912_00764.pdf/.txt.
27. Campi, L., Zabaljauregui, D. (2020). Optimal market making under partial information with general intensities.
    Applied Mathematical Finance. arXiv 1902.01157. File: arxiv_1902_01157_mm_hmm.pdf/.txt.
28. Brigida, M. (2020). Applied Finance Letters, article 268. [unverified: search snippet only; download failed]
29. Chen, R., Feng, Y., Palomar, D. (2016). Forecasting intraday trading volume: a Kalman filter approach. SSRN
    3101695. [not fetched (SSRN blocks); the CRAN intradayModel manual that implements it is saved as
    cran_intradaymodel.pdf but not quoted]
30. Databento schema pages: mbp-10, tbbo, mbo (databento.com/docs/schemas-and-data-formats/...). Files:
    databento_mbp10.html, databento_tbbo.html, databento_mbo.html (+ .txt).
31. Price pages: lambda.ai/pricing, runpod.io/pricing, hetzner.com/cloud. Files: lambda_pricing.html,
    runpod_pricing.html, hetzner_cloud.html (+ .txt).
32. PyPI metadata: filterpy, pykalman, hmmlearn, statsmodels, particles. Files: pypi_<name>.json.

---

## Evidence table (claim | source | verbatim quote | saved file)

| # | Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|---|
| E1 | Kalman's paper derives a recursion for the error covariance that yields the optimal filter | Kalman 1960 | "A nonlinear difference (or differential) equation is derived for the covarianc[e] matrix of the optimal estimation error" (bracket: letter clipped by pdftotext) | kalman_1960.txt |
| E2 | KF model and noise assumptions | Welch, Bishop | "They are assumed to be independent (of each other), white, and with normal probability distributions" | welch_bishop_kf_intro.txt |
| E3 | Gain minimises posterior error covariance | Welch, Bishop | "the gain or blending factor that minimizes the a posteriori error covariance" | welch_bishop_kf_intro.txt |
| E4 | Gain and covariance converge when Q, R constant | Welch, Bishop | "both the estimation error covariance P k and the Kalman gain K k will stabilize quickly and then remain constant" | welch_bishop_kf_intro.txt |
| E5 | EKF is an approximation that breaks normality | Welch, Bishop | "The EKF is simply an ad hoc state estimator that only approximates the optimality of Bayes’ rule by linearization" | welch_bishop_kf_intro.txt |
| E6 | UT accuracy | Wan, van der Merwe | "approximations that are accurate to the third order for Gaussian inputs for all nonlinearities" | wan_vandermerwe_ukf.txt |
| E7 | Efficient price plus noise decomposition by Kalman filter | Cartea, Karyampas | "We propose a Kalman-filter-based methodology that allows us to deconstruct price series into the true efficient price and the microstructure noise" | cartea_karyampas_2009.txt |
| E8 | Observation equation of the noise model | Cartea, Karyampas | "Yt is the observed log-price, equal to the true efficient log-price Xt plus an error term εt that captures all types of the microstructure error" | cartea_karyampas_2009.txt |
| E9 | Kalman weights for realized volatility, shown in simulation | Owens, Steigerwald | "We use the Kalman filter to derive more efficient weights, for any given sampling frequency. We demonstrate the efficacy of the procedure through an extensive simulation exercise" | owens_steigerwald.txt |
| E10 | Kalman-EM handles asynchrony and noise | Ho, Xin | "One technique for addressing both asynchronous returns and market microstructure is the Kalman-EM (KEM) algorithm" | ho_xin_2016_sparse_kf.txt |
| E11 | Kalman replaces rolling least squares for hedge ratios | Palomar book 15.6 | "the least squares solution should be recomputed on a rolling-window basis. However, it is better to employ a more sophisticated time-varying modeling and estimation technique based on state-space modeling and the Kalman filter" | palomar_book_kalman_pairs.html.txt |
| E12 | Kalman pairs strategy claims OOS profit after costs (implausible) | He et al. 2023 | "the cumulative return out-of-sample was 21%, and the average monthly Sharpe ratio was 10 in-sample and 18 out-of-sample" | he_etal_2023_jik.html.txt |
| E13 | Reference-list error in He et al. | He et al. 2023 | "[Gatev et al., 1999] P. Gatev, S. Thomas, T. Kepple, M. Hallett. Feedforward ankle strategy of balance during quiet stance in adults" | he_etal_2023_jik.html.txt |
| E14 | FLS/Kalman stat-arb results are gross of costs | Montana et al. | "Our simulation results have shown gross monetary results, and we have assumed that transaction costs are negligible" | montana_etal_0709_3884_fls.txt |
| E15 | Particle filters avoid local linearisation | Doucet, Johansen | "the principal advantage of particle methods is that they do not rely on any local linearisation technique" | doucet_johansen_pf_tutorial.txt |
| E16 | SV model used as the standard example | Doucet, Johansen | "Example 4 - Stochastic Volatility model ... Xn = αXn−1 + σVn , Yn = β exp (Xn /2) Wn" (layout joined) | doucet_johansen_pf_tutorial.txt |
| E17 | Resampling rule by ESS | Doucet, Johansen | "The ESS takes values between 1 and N and we resample only when it is belowa threshold NT ; typically NT = N/2" | doucet_johansen_pf_tutorial.txt |
| E18 | Degeneracy is inevitable over many steps | Doucet, Johansen | "some degree of degeneracy is inevitable in all but trivial cases" | doucet_johansen_pf_tutorial.txt |
| E19 | Parameter estimation unsolved in general | Doucet, Johansen | "this is a difficult problem and it cannot be considered to have been solved in full generality" | doucet_johansen_pf_tutorial.txt |
| E20 | SV canonical model | Kim, Shephard, Chib | "The canonical model in this class for regularly spaced data is" | ksc_1998_sv_wp.txt |
| E21 | Particle filter for transaction-level spot vol, ms per update | Dahlhaus, Neddermeyer | "requires a few milliseconds for a single update of the estimator (including one iteration of the particle filter with 500 particles)" | arxiv_1006_1860_spotvol_pf.txt |
| E22 | SV with particle filters improves OOS RV forecasts on S&P futures | Stroud, Johannes | "We show that our approach improves realized volatility forecasts by up to 50% over existing benchmarks" | stroud_johannes_2014.txt |
| E23 | SV MCMC run time | Stroud, Johannes | "makes 12,500 draws in 12–25 minutes using a 2.8 GHz Xeon processor for each year of 5-minute returns (around 70,500 observations)" | stroud_johannes_2014.txt |
| E24 | Time-of-day seasonality in intraday futures volatility | Stroud, Johannes | "seasonal components capturing time of the day patterns" | stroud_johannes_2014.txt |
| E25 | Hamilton's filter and ML estimation | Hamilton 1989 | "The paper presents an algorithm for drawing such probabilistic inference in the form of a nonlinear iterative filter. The filter also permits estimation of population parameters by the method of maximum likelihood" | hamilton_1989.pdf (page 357, read from page image) |
| E26 | Markov transition probabilities | Hamilton 2005 | "Pr(st = j|st−1 = i, st−2 = k, ..., yt−1 , yt−2 , ...) = Pr(st = j|st−1 = i) = pij" | hamilton_palgrave_regime.txt |
| E27 | Filtered probability definition and data set | Hamilton 2005 | "Ωt = {yt , yt−1 , ..., y1 , y0 } denotes the set of observations obtained as of date t" | hamilton_palgrave_regime.txt |
| E28 | Smoothed probabilities use later data | Hamilton 2005 | "forming an inference about what regime the economy was in at date t based on observations obtained through a later date T , denoted ξ̂t|T . These are referred to as “smoothed” probabilities" | hamilton_palgrave_regime.txt |
| E29 | ML by maximising the filter's likelihood | Hamilton 2005 | "An estimate of the value of θ can then be obtained by maximizing (10) by numerical optimization" | hamilton_palgrave_regime.txt |
| E30 | Number of regimes cannot be chosen by a standard LR test | Hamilton 2005 | "the likelihood ratio test does not have the usual χ2 limiting distribution" | hamilton_palgrave_regime.txt |
| E31 | HMM three problems | Rabiner 1989 | "three fundamental problems" (for HMM design) | rabiner_1989.pdf (page 257, read from page image) |
| E32 | Forward algorithm cost | Jurafsky, Martin | "we use an efficient O(N 2 T ) algorithm called the forward algorithm" | jurafsky_martin_hmm_appendix.txt |
| E33 | Baum-Welch is EM | Jurafsky, Martin | "The standard algorithm for HMM training is the forward-backward, or Baum-Welch algorithm (Baum, 1972), a special case of the Expectation-Maximization or EM algorithm" (line breaks joined) | jurafsky_martin_hmm_appendix.txt |
| E34 | Viterbi recursion | Jurafsky, Martin | "vt ( j) = max vt−1 (i) ai j b j (ot )" | jurafsky_martin_hmm_appendix.txt |
| E35 | HMM on E-mini 1-min: pre-cost Sharpe > 2 | Christensen et al. | "it is shown that pre-cost the models have a Sharpe ratio in excess of 2.0" | christensen_godsill_turner_2020_hmm_momentum.txt |
| E36 | Costs cut that Sharpe by about 15% | Christensen et al. | "Post-cost results reduce the Sharpe ratio of the HMM strategies by approximately 15%" (hyphenation joined) | christensen_godsill_turner_2020_hmm_momentum.txt |
| E37 | HMM gate OOS with stated costs | Bulla et al. | "transaction costs are fixed at 10 basis points (0.10%) for a one-way trade" | bulla_etal_2011_ms_allocation.txt |
| E38 | HMM gate lowers risk and adds excess return (daily) | Bulla et al. | "Portfolio risk is lowered by an average of 41% for all markets under consideration" | bulla_etal_2011_ms_allocation.txt |
| E39 | Regime model no better than random walk (FX) | Engel 1994 | "By the mean-squared-error criterion, the Markov model does not generate superior forecasts to a random walk or the forward rate" | engel_1994_ms_fx.txt |
| E40 | Misclassification drives MS forecast failure | Bessec, Bouabdallah | "We find that the main source of error is due to the misclassification of future regimes" (ligature restored) | bessec_bouabdallah_2005.txt |
| E41 | Two duration regimes in NASDAQ LOB driven by HFT behaviour | Li, Xing, Chen | "the regime switchings are driven by the changes of high-frequency traders (HFTs) between providing and taking liquidity" | arxiv_1912_00764.txt |
| E42 | One regime is sub-millisecond | Li, Xing, Chen | "One mode is to the order of approximately 10−4 seconds, and the other is to the order of 100 seconds" | arxiv_1912_00764.txt |
| E43 | Market making with hidden-Markov intensities (theory) | Campi, Zabaljauregui | "unobservable factors modelled by a hidden Markov chain" | arxiv_1902_01157_mm_hmm.txt |
| E44 | mbp-10 content | Databento | "MBP-10 (market by price) provides every order book event across the top ten price levels, keyed by price" | databento_mbp10.html.txt |
| E45 | tbbo content | Databento | "BBO on trade (TBBO) provides every trade event alongside the BBO immediately before the effect of each trade" | databento_tbbo.html.txt |
| E46 | mbo content | Databento | "Market by order (MBO) provides every order book event across every price level, keyed by its order ID. This allows you to determine the queue position of each order" | databento_mbo.html.txt |
| E47 | GPU rental price | RunPod | "RTX 4090 24 GB VRAM 41 GB RAM 6 vCPUs $ 0.89 /hr" | runpod_pricing.html.txt |
| E48 | GPU rental price | Lambda | "NVIDIA A10 24 GB 30 226 GiB 1.3 TiB SSD $1.29" | lambda_pricing.html.txt |
| E49 | CPU server price | Hetzner | "starting from max/mo. € 43.49 per month, excl. VAT" | hetzner_cloud.html.txt |
| E50 | Software versions | PyPI | pykalman "0.11.2", "An implementation of the Kalman Filter, Kalman Smoother, and EM algorithm in Python"; hmmlearn "0.3.3", "Hidden Markov Models in Python with scikit-learn like API"; particles "0.4", "Sequential Monte Carlo in Python" | pypi_pykalman.json, pypi_hmmlearn.json, pypi_particles.json |

Measured numbers (not quotes): C2F_bench_results.json and C2F_examples.json in work/C2_Filter/.

---

## Gaps, failures and limits (log)

- No study found that tests a Kalman, particle-filter or HMM signal for timing or gating PASSIVE orders on CME
  futures, out of sample, net of costs, at retail latency. Reported as a gap, not as evidence against.
- Fetch failures: Aït-Sahalia, Mykland and Zhang (2005) Princeton copy (404); Ang and Timmermann regime survey
  (Columbia returned an HTML page); Brigida (2020) download (22 bytes); Mertens et al. (2022) full text not in the
  LSE repository (abstract only via WebFetch, not saved); Chen, Feng and Palomar (2016) is on SSRN, which blocks this
  machine; Dacco and Satchell (1999) paywalled. Each is marked [unverified] or not used.
- Scanned PDFs: Hamilton (1989) and Rabiner (1989) have no text layer and no OCR tool is installed; one page of each
  was read from its image for the quotes in E25 and E31. Their equations are cited through Hamilton (2005, text) and
  Jurafsky and Martin (text) instead.
- pdftotext dropped most symbols from Wan and van der Merwe's UKF equations (15) to (18) and mangled Doucet and
  Johansen's formulas; the equations in sections 2.2 and 3.2 are restatements in standard notation, labelled as such.
- The 1.5-tick markout standard deviation in the power calculations is an assumption, not a measurement; the pilot
  replaces it. The design effect of day clustering was not estimated.
- He et al. (2023): I could not locate the transaction-cost rate in the saved HTML by grep; the paper is flagged, not
  relied on.
- WebSearch calls used: 17 of the 60 budgeted. No budget notice was received. Firecrawl and Scrapling were not
  needed (no terms checks were required).
- No market data was read; all measured numbers are on synthetic data. No Databento, broker, TopstepX or ProjectX
  call; no keys read.

## Corrections after review (Stage E.28, MathReviewer G1)

- MG1-14: Stroud-Johannes summary corrected: the SV rules were short the VIX index (long the VXX) on 396 to 551 of the days; the Sharpe range and conclusion are unchanged.
- MG1-15: H-KF1 parenthetical replaced so the sign condition is unambiguous (efficient price on the order's own side of the mid, fill more likely adverse).
- MG1-16: "within 0.01%" changed to "within 0.012%".
- MG1-17: "exactly the regime changes" changed to "mostly the regime changes".
- MG1-19: likelihood description now notes steady-state K and F, exact only asymptotically.
- Not applied: MG1-18 (needs lead, verdict wording). See reports/stage_e28_briefs/R_fix_G1.md.
