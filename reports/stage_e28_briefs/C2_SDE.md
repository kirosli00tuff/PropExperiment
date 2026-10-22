# C2_SDE: stochastic calculus and continuous-time models of prices and order flow

Stage E.28, Part C2 deep dive. Worker C2_SDE (opus, xhigh), written 2026-10-21 (PDT).
Pages: reports/stage_e28_briefs/pages/C2_SDE/ (log.tsv lists every fetch, including failures).
Worked examples: reports/stage_e28_briefs/work/C2_SDE/C2_SDE_examples.py, output in
C2_SDE_examples_out.txt (sha256 27ffc12b...e680b9). The examples use synthetic numbers only. No market
data was read. Nothing here is registered, and nothing here changes N (538). Where a section proposes a
hypothesis and a number of configurations, that is a proposal for the lead. The lead decides what
counts toward N.

How to read this file. Every claim from a source has a verbatim quote in the evidence table (section 12)
and a saved file. Equations carry the paper's own equation number when the fetched text shows it.
Anything I could not check against fetched full text is marked [unverified], with the reason.
Derivations I wrote myself are marked [derived], with their assumptions.

## 0. Setting and the numbers used throughout

- Instrument used for examples: MES. The tick is alpha = 0.25 index points, the tick value is $1.25,
  and the round-turn commission is $1.22. All three come from the repo: rules/products.py, line
  `_p("MES", "sp500", MICRO, "0.25", "1.25", "5", 122, ...)`, with the commission sourced in that file
  to the Topstep facts F3.7/F3.6. The CME spec page could not be read: the Wayback capture renders
  the table in JavaScript, so it is logged as not used.
- Illustrative volatility: an index level of P0 = 5000 and 15% annualised volatility. That gives a
  daily volatility of 0.15/sqrt(252) = 0.945%, or 47.25 points. If all of that variance falls in the
  23,400-second regular session, the per-second standard deviation is 47.25/sqrt(23400) = 0.309
  points = 1.24 ticks. Over 10 s it is 0.977 points (3.91 ticks), and over 60 s it is 2.39 points
  (9.57 ticks). These are round numbers for teaching, not estimates (C2_SDE_examples_out.txt, E1).
- The pilot (READER_RULES): one Databento schema (mbp-10, mbo or tbbo) for one CME contract over
  about 4 months. It measures fill rates, queue times and 1/10/60 s markouts of a 1-lot passive order.
  Latency from Vancouver to Aurora is tens of milliseconds, with no co-location.
- Markout convention used here: for a passive buy filled at price p_f at time t, the markout at
  horizon h is m(t+h) - p_f, where m is the mid-price. A sell takes the opposite sign. Units are ticks
  unless stated.

---

## 1. Ito processes and Ito's lemma

**(1) Core idea.** An Ito process models a price as a drift plus a "noise integral" against Brownian
motion. Ordinary calculus breaks for such paths, because the squared increments of Brownian motion do
not vanish: they add up to elapsed time. Ito's lemma is the chain rule with that extra second-order
term. Almost everything later in this section builds on it: the GBM and OU solutions, the
quadratic-variation target that realised variance estimates, and the HJB equations behind
Avellaneda-Stoikov (which belong to C2_Control).

**(2) Key equations.**

- Ito process: dX_t = mu_t dt + sigma_t dB_t. Here B_t is a standard Brownian motion, mu_t is the
  drift (expected change per unit time), and sigma_t is the instantaneous volatility. Both are adapted:
  they may depend on the past, but not on the future.
- Quadratic variation (MIT 18.S096, Lecture 17, Theorem 2.5): over a partition of [0,T] whose mesh goes
  to 0, sum_i (B_{t_{i+1}} - B_{t_i})^2 -> T with probability 1. In shorthand, (dB_t)^2 = dt. For X,
  the quadratic variation is [X]_T = integral_0^T sigma_t^2 dt. This "integrated variance" is the target
  that realised variance estimates (section 6).
- Ito's lemma (MIT 18.S096, Lecture 18, Theorem 1.1): for a smooth f(t,x),
  df(t,X_t) = ( df/dt + mu_t df/dx + (1/2) sigma_t^2 d2f/dx2 ) dt + sigma_t (df/dx) dB_t.
  Note: the theorem line in the fetched notes prints the dB_t coefficient as df/dx alone. The proof
  line directly below it carries the sigma_t factor, which is the correct form.
- Derivation summary (from the same notes): expand f to second order,
  df = f_t dt + f_x dX + (1/2) f_xx (dX)^2. Then (dX)^2 = sigma^2 (dB)^2 + 2 mu sigma dt dB + mu^2 dt^2.
  Keep (dB)^2 = dt, and drop dt dB and dt^2, which are of higher order. Assumptions: f is once
  differentiable in t and twice in x, with continuous derivatives, and mu and sigma are adapted and
  integrable.

**(3) Data.** None by itself. It is a tool.

**(4) What it decides.** Nothing directly. It turns a model of dX into a model of any function of X:
log-prices, P&L, inventory value.

**(5) Worked example.** Take f = log S for a geometric Brownian motion dS = mu S dt + sigma S dB. Ito
gives d log S = (mu - sigma^2/2) dt + sigma dB. The term -sigma^2/2 is the "Ito correction". At MES tick
scale it is negligible. With zero log-drift, the gap between the GBM mean E[S_h] and S_0 is
S_0 (exp(sigma^2 h/2) - 1). That is 0.00057 points (0.0023 ticks) over 60 s, and 0.034 points (0.14
ticks) over one hour (E1). Over the horizons the pilot measures, the correction cannot be told apart
from zero.

**(6) Pilot hypothesis.** None of its own. The testable consequences appear in sections 2 to 7: the
martingale property behind markouts, and quadratic variation behind volatility estimates. It adds 0 to N.

**(7) Compute.** None.

**(8) Evidence.** It is mathematics, with no empirical claim to test.

---

## 2. Arithmetic and geometric Brownian motion at tick scale, and the discreteness that replaces them

**(1) Core idea.** ABM (dS = mu dt + sigma dB) and GBM (dS = mu S dt + sigma S dB) are the two baseline
continuous price models. At 1 to 60 s on MES they are indistinguishable. The real issue at this scale is
that neither model is right. The price lives on a 0.25-point grid, the spread is at least one tick, and
the last trade price bounces between bid and ask. The useful models at this scale treat the observed
price as a latent continuous "efficient" price X_t plus a discretisation or noise. Two of them are
covered here: the Roll bid-ask bounce model, and the uncertainty-zones model of Robert and Rosenbaum for
large-tick assets.

**(2) Key equations.**

- ABM: S_t = S_0 + mu t + sigma B_t (MIT 18.S096 L18, Example 1.3(i): "Brownian motion with drift").
  GBM: S_t = S_0 exp((mu - sigma^2/2) t + sigma B_t) [derived from the L18 Example 1.3(iii)
  computation for exp(mu t + sigma B_t), by setting the drift of log S to mu - sigma^2/2].
- Roll model [unverified: Roll (1984) was not fetched; the derivation below is complete]. The trade
  price is p_t = m_t + (s/2) q_t, where m_t is a martingale efficient price, s is the spread, and
  q_t = +1 for a buyer-initiated trade, -1 for a seller-initiated one. The q_t are i.i.d. with mean 0,
  independent of m. Then dp_t = dm_t + (s/2)(q_t - q_{t-1}) and
  Cov(dp_t, dp_{t-1}) = (s^2/4) Cov(q_t - q_{t-1}, q_{t-1} - q_{t-2}) = -(s^2/4) Var(q) = -s^2/4.
  With s = 1 tick = 0.25 points, this is -0.0156 points^2. Trade-price returns are negatively
  autocorrelated even when the efficient price is a martingale. That is why markouts and volatility use
  the mid or microprice, not the last trade.
- Uncertainty zones (model: Robert and Rosenbaum 2011; estimator consistency: Robert and Rosenbaum 2012, per Dayri and Rosenbaum's ref. [35]; as summarised with equations in Dayri and Rosenbaum,
  arXiv 1207.6325, section 2):
  - An "alternation" is a one-tick move in the opposite direction to the previous move. A
    "continuation" is a one-tick move in the same direction. Let N^(a) and N^(c) be their counts over
    [0,t].
  - Estimator: eta_hat = N^(c) / (2 N^(a)), with eta in [0, 1/2].
  - Efficient price at the i-th price change: X_{t_i} = P_{t_i} - sign(P_{t_i} - P_{t_{i-1}}) (1/2 - eta) alpha,
    where alpha is the tick.
  - Realised variance on the recovered X (their eq. (3)): sigma_hat^2_[0,t] = sum_{t_i<=t} (X_hat_{t_i} - X_hat_{t_{i-1}})^2.
  - Interpretation, quoted: if eta is small, "there is a lot of mean reversion in the price" and "the
    tick size is very large". If eta is near 1/2, the price behaves like a sampled Brownian motion.
    2 eta alpha acts as an "implicit spread".

**(3) Data.** The eta estimator needs only the sequence of price changes of a single price series: last
trade, or mid. Any of mbp-10, mbo or tbbo carries it, since tbbo has trades with the BBO. Four months of
one contract gives thousands of price changes per session. The count is not known until the pilot, so
this is a guess. That is far more than needed to estimate a ratio of counts.

**(4) What it estimates.** eta measures tick-scale mean reversion, and with it how "large" the tick is
relative to how precisely traders locate the efficient price. It also gives a noise-corrected efficient
price and its realised variance.

**(5) Worked example (illustrative counts).** Suppose a session has 4,000 one-tick changes in the last
traded price: 2,800 alternations and 1,200 continuations. Then eta_hat = 1200/(2 x 2800) = 0.214. The
implicit spread is 2 eta alpha = 2 x 0.214 x 0.25 = 0.107 points (0.43 tick). Now let the trade price
tick up from 5000.00 to 5000.25. The efficient-price estimate is
5000.25 - (0.5 - 0.214) x 0.25 = 5000.25 - 0.0715 = 5000.18. That is 0.29 tick below the new trade price,
on the side the price came from. This is what "more alternations than continuations" means: the next
trade-price change is more likely to be back down. Whether a passive order can earn that bounce after
costs is worked out in section 7.

**(6) Pilot hypotheses.**

- H-SDE-ETA (descriptive). H0: eta = 1/2 on the 1-lot contract's mid-price series, against the one-sided
  alternative eta < 1/2 (eta = 1/2 is the boundary of the model's admissible range; MathReviewer MG1-07). Statistic: the daily
  eta_hat, with a day-block bootstrap confidence interval whose upper end is compared with 1/2. Sample: the pilot's full window. This is a
  description of the market, not a trading rule. I propose 0 configurations, with the lead's decision
  reserved.
- H-SDE-BOUNCE (a rule). This is the rule Safari and Schmidhuber describe and doubt: post a buy at the
  lower price just after an up-tick, and a sell at the higher price just after a down-tick. Statistic:
  the mean cost-inclusive markout per fill at the pre-declared horizon, one-sided, with day-clustered
  standard errors. Configurations: 1 (one horizon fixed in advance), or 3 if all of 1/10/60 s are tested.

**(7) Compute.** Counting and one pass per day. The laptop handles it.

**(8) Evidence.**
- Safari and Schmidhuber (arXiv 2501.16772, 2025) describe exactly this tick oscillation of S&P 500 futures with a 0.25 tick (the E-mini grid). They
  write that it "can be used to reduce trading costs, but it can hardly be used for a profitable trading
  strategy", and that any "market maker fee" is compensation for the risk that "the price does not revert
  but runs away". This is negative evidence, and it comes from the closest source to our setting.
- Dayri and Rosenbaum give the theory, not trading results.

---

## 3. Jump-diffusions: Merton (normal jumps) and Kou (double-exponential jumps)

**(1) Core idea.** A jump-diffusion adds a compound Poisson process to a diffusion. At random times
(rate lambda per unit time) the log-price jumps by a random amount Y. In Merton (1976), Y is normal. In
Kou (2002), Y is asymmetric double-exponential. The double-exponential version has fatter tails and a
memoryless property that makes path-dependent quantities, such as barrier hitting, tractable.

**(2) Key equations.**

- Kou (2002), eq. (1): dS_t / S_{t-} = mu dt + sigma dW_t + d( sum_{i=1}^{N_t} (V_i - 1) ).
  - N_t is a Poisson process with rate lambda.
  - V_i are i.i.d. positive jump multipliers, and Y = log V.
  - W, N and the Y's are independent.
  - The Greek letters are lost in the PDF text extraction. I restored them from the paper's prose:
    "N t is a Poisson process with rate", "Y = logV has an asymmetric double exponential
    distribution".
- Density of Y (Kou, unnumbered display after eq. (1); eq. (2) is the mixture form): f_Y(y) = p eta1 e^{-eta1 y} 1{y >= 0} + q eta2 e^{eta2 y} 1{y < 0},
  with p, q >= 0, p + q = 1, eta1 > 1 and eta2 > 0. Upward jumps are exponential with mean 1/eta1 and
  occur with probability p. Downward jumps have mean 1/eta2 and probability q. The condition eta1 > 1
  keeps E[V] finite.
- Merton (1976): the same structure with Y ~ N(m, delta^2). Kou: "In Merton's paper Y s are normally
  distributed." The Merton 1976 PDF itself could not be fetched (section 13).
- Moments [derived]. For an exponential variable with rate eta, E = 1/eta and E[.^2] = 2/eta^2. So
  E[Y] = p/eta1 - q/eta2 and E[Y^2] = 2p/eta1^2 + 2q/eta2^2.
- Solution [Kou eq. (3); re-derived, by Ito's formula for jump processes, assuming constant mu and sigma]:
  S_t = S_0 exp((mu - sigma^2/2) t + sigma W_t) prod_{i=1}^{N_t} V_i.
- Quadratic variation of log S over [0,T] [derived]: sigma^2 T + sum_{i<=N_T} Y_i^2. Its expectation is
  (sigma^2 + lambda E[Y^2]) T, so the jump share of variance is lambda E[Y^2] / (sigma^2 + lambda E[Y^2]).

**(3) Data.** Fitting lambda, eta1, eta2 and p by maximum likelihood needs many jumps. Jumps are rare at
tick resolution (section 4: about 1% of quadratic variation in tick data). Four months of one contract
might hold tens of genuine jumps, mostly at scheduled releases. That is enough to count them, but not to
pin down a tail shape. The schema does not matter for counting, since trades or BBO suffice. The full
book matters only for studying what a jump does to the queues.

**(4) What it estimates.** It estimates the jump intensity and size distribution, and with them the jump
share of variance. For option pricing, its original use, it explains volatility smiles. For a 1-lot
passive order, it describes the left tail of markouts: the order rests at a price the market jumps
through.

**(5) Worked example (E7).** Take 2232 points^2 as the continuous (diffusive) variance; a jump share s of total QV then adds s/(1-s) x 2232.
Suppose jumps are 1% of quadratic variation, which is the tick-data figure. Then jump variance is 22.5 points^2/day. If that
comes from one jump per day (lambda = 1), the RMS jump is 4.75 points (19 ticks). If it comes from five
per day, the RMS jump is 2.12 points (8.5 ticks). At 20% share, typical of older 5-minute estimates, the
RMS jump is 23.6 points (94 ticks) at lambda = 1.

Why this matters for a 1-lot quoting strategy: one adverse 19-tick jump through a resting order costs
19 x $1.25 = $23.75. Section 7 shows the margin per round turn at zero adverse selection is $0.03. So a
single such event erases the margin of about 790 round turns.

A Kou parameter set for illustration: p = 0.4, mean up-jump 0.2%, mean down-jump 0.3%. Then E[Y] = -0.10%,
E[Y^2] = 1.4e-5, and the RMS jump is 0.37%, which is 18.7 points at 5000.

**(6) Pilot hypothesis.**
- H-SDE-NEWS (a rule). Pulling quotes in a fixed window around scheduled macro releases (for example
  [-1, +5] min around 08:30 ET) raises mean cost-inclusive markout per fill. Statistic: the difference in
  mean markout, flagged fills against unflagged, with a day-clustered t. Configurations: 1 (one window
  fixed in advance).
- Needs: a release calendar, which I have not checked the repo for (section 13). Sample: about 4
  releases a week gives roughly 70 windows in 4 months. Fills inside those windows will be few, so the
  test has low power, and I would keep it descriptive. The jump-diffusion likelihood itself proposes no
  trading rule.

**(7) Compute.** A maximum-likelihood fit of a 4- or 5-parameter mixture on about 2 million 1-s returns
takes seconds to minutes on the laptop.

**(8) Evidence.**
- Christensen, Oomen and Podolskij (JFE 2014; arXiv 2602.10925) used EBS FX and CME futures tick data.
  They find that "jumps account for about 1% of total price variability (i.e., quadratic variation)",
  where lower-frequency estimates are "an order of magnitude larger". They also find that traditional
  measures "spuriously assign a burst of volatility to the jump component". Their review table lists
  jump shares of 4.4% to 15% for S&P 500 futures at 5-minute sampling in earlier work.
- I found no evidence that fitting Merton or Kou helps a passive futures strategy. Their documented use
  is option pricing (Kou: "the model is simple enough to produce analytical solutions for a variety of option-pricing problems, including call and put options").

---

## 4. Jump tests: bipower variation (Barndorff-Nielsen and Shephard), Lee-Mykland, Ait-Sahalia-Jacod

**(1) Core idea.** These tests decide from data whether a price path, or a given return, contains a jump.
- Bipower variation sums products of adjacent absolute returns. A single jump inflates only one factor
  of each product, so bipower variation still estimates the continuous part of the variance, while
  realised variance includes the jumps. The gap between the two estimates the jump part.
- Lee-Mykland standardises each return by a local bipower volatility and flags returns too large to be
  diffusive.
- Ait-Sahalia-Jacod compare fourth-power variation at two sampling scales. The ratio goes to 1 if there
  are jumps and to 2 if there are not.

**(2) Key equations.**

- Bipower variation (BNS 2006, eq. (4)-(5)): {Y}^[1,1]_t = plim sum_j |y_{j-1}||y_j| = mu1^2 integral_0^t
  sigma_s^2 ds. Here mu1 = E|u| = sqrt(2)/sqrt(pi) ~ 0.79788 for u ~ N(0,1), and y_j are the returns on a
  grid of step delta. Then RV - mu1^{-2} BV estimates sum_j c_j^2, the squared jumps.
- Ratio test (BNS eq. (11)): H_hat = delta^{-1/2} ( mu1^{-2} {Y_delta}^[1,1] / [Y_delta] - 1 ) /
  sqrt( {Y_delta}^[1,1,1,1] / ({Y_delta}^[1,1])^2 ) -> N(0, vartheta).
  - Here vartheta = pi^2/4 + pi - 5 ~ 0.6090 (eq. (6)).
  - The quadpower variation is {Y_delta}^[1,1,1,1] = delta^{-1} sum |y_{j-3}||y_{j-2}||y_{j-1}||y_j|.
  - Reject continuity if the statistic is significantly negative. Without jumps, BV/RV -> mu1^2 ~ 0.6366.
  - The adjusted version J_hat puts max(t^{-1}, .) in the denominator.
- Lee-Mykland (2008, eq. (7)-(8)): L(i) = log(S(t_i)/S(t_{i-1})) / sigma_hat(t_i), with
  sigma_hat(t_i)^2 = (1/(K-2)) sum_{j=i-K+2}^{i-1} |log S(t_j)/S(t_{j-1})| |log S(t_{j-1})/S(t_{j-2})|.
  - The window K must satisfy K = O_p(dt^alpha), -1 < alpha < -0.5. The paper says: "We suggest the
    smallest integer K that satisfies the necessary condition", which is about sqrt(252 x n_obs per day).
  - Threshold (Lemma 1, eq. (12)-(13)): (max |L(i)| - C_n)/S_n -> xi, where P(xi <= x) = exp(-e^{-x}).
    Here C_n = (2 log n)^{1/2}/c - (log pi + log log n)/(2c (2 log n)^{1/2}), S_n = 1/(c (2 log n)^{1/2}),
    and c = sqrt(2/pi) ~ 0.7979. At 1%, beta* = -log(-log 0.99) = 4.6001.
- Ait-Sahalia-Jacod (Annals of Statistics 2009, eq. (12)-(13)): S_hat(p,k,Delta_n)_t =
  B_hat(p, k Delta_n)_t / B_hat(p, Delta_n)_t, where B_hat(p, Delta) = sum |Delta-increments|^p.
  - For p > 2 and k >= 2, it converges to 1 on paths with jumps and to k^{p/2-1} on continuous paths.
    With p = 4 and k = 2, that is 2.
  - Under i.i.d. additive noise the limit is 1/2 (their section 5.4 and empirical section).

**(3) Data.** Equally spaced returns of one price series: last trade, mid or microprice. Any schema
works. Practical problems at MES tick scale:
- (a) Microstructure noise. Lee-Mykland used 15-minute data in their application so that "results are
  not greatly affected by the presence of market microstructure noise".
- (b) Zero returns [derived, my analysis]. On a 0.25 grid, many 1-s mid returns are exactly zero. In the
  synthetic rounded-price example (E5), 16% of 1-s returns were zero, and real data will likely have more
  because the mid does not change every second. A zero in either factor zeroes the bipower product. That
  biases BV down, and with it sigma_hat, which inflates L(i) and produces false jump flags.
- Noise-robust variants exist. The comparison study recommends them at 5 s when noise is the issue:
  "LM12 and ASJL - based on very high-frequency (five second) data, are the best choice". This is
  Lee-Mykland 2012 with pre-averaging, which I did not fetch.

**(4) What it decides.** Which days, or which individual returns, contain jumps. This gives the jump
share of variance and jump times and sizes for event studies.

**(5) Worked example (E6).**
- For 1-s data over one 23,400-second session: n = 23,400, C_n = 5.139, S_n = 0.2794. The 1% critical
  value is |L| > 5.139 + 4.6001 x 0.2794 = 6.42.
- For one-minute data (n = 390), the critical value is |L| > 5.47.
- For 80 sessions pooled at 1 s (n = 1.872 million), it is 7.36.
- The window K for 23,400 observations a day is about sqrt(252 x 23400) = 2428 seconds (40 minutes).
- Multiple testing: a naive 5% test applied to each of 23,400 returns would flag about 1,170 returns a
  day with no jumps at all. The Gumbel threshold exists to prevent this.
- Ait-Sahalia-Jacod with p = 4, k = 2: a value near 2 points to no jumps, near 1 to jumps, and near 1/2
  to noise.

**(6) Pilot hypothesis.**
- H-SDE-JUMPFILTER (a rule). Cancel resting quotes for X seconds after a Lee-Mykland flag (1% Gumbel
  threshold, or the Bajgrowicz-Scaillet-Treccani threshold). The claim is that mean markout of the
  remaining fills improves. Statistic: the difference in mean cost-inclusive markout, day-clustered.
  Configurations: 1 (threshold and X fixed in advance). Each extra threshold or cooldown adds 1.
- Caveat [derived]. L(i) uses the return ending at t_i, so it flags a jump only after the jump has
  traded through the book. It cannot protect the order that was hit. It helps only if jumps cluster, and
  Bajgrowicz et al. find that for their stocks jumps "do not cluster in time". I expect a null. The test
  is cheap, but the expected gain is small.
- H-SDE-JUMPSHARE (descriptive, 0 configurations proposed): the share of the pilot's adverse markout
  mass that falls within flagged windows.

**(7) Compute.** O(n) per day, which takes seconds on the laptop.

**(8) Evidence.**
- Bajgrowicz, Scaillet and Treccani (Management Science 2016) show the danger. Testing at 5% over 252
  days with no jump still flags "more than 12 days" on average. In Dow Jones stocks 2006-2008, "spurious
  detections can represent up to 90% of the jumps detected initially". Bursts of volatility are "often
  incorrectly identified as jumps when the sampling is too sparse".
- Christensen et al. reach the same conclusion from tick data (section 3).
- Ait-Sahalia and Jacod's own DJIA 2005 application found most statistics near 1, which suggests jumps,
  with "evidence of market microstructure noise in the form of density mass below 1".
- The simulation comparison by Maneesoonthorn, Martin and Forbes ranks the Ait-Sahalia-Jacod test
  "the least powerful test overall".
- Net: jump tests are good at descriptive accounting, but their detections are fragile, and none of
  these papers reports a trading gain.

---

## 5. The Ornstein-Uhlenbeck process and its estimation

**(1) Core idea.** An Ornstein-Uhlenbeck (OU) process is pulled back toward a mean mu at speed kappa,
with Gaussian shocks. Sampled at a fixed step h, it is exactly an AR(1). So estimating it means one
OLS regression and one transform. The catch is that the regression's slope is biased toward faster
mean reversion in finite samples. The bias is set by the time span of the data, not by how finely it is
sampled. A short window can make a random walk look mean-reverting.

**(2) Key equations** (Bao, Ullah and Wang 2014, eq. (2.1)-(2.5)).
- SDE (2.1): dx(t) = kappa (mu - x(t)) dt + sigma dB(t).
- Solution (2.2): x(t) = mu + (x(0) - mu) e^{-kappa t} + sigma integral_0^t e^{kappa (s-t)} dB(s).
  Derivation summary [derived]: apply Ito's lemma to e^{kappa t} x(t). The cross terms cancel, giving
  d(e^{kappa t} x) = kappa mu e^{kappa t} dt + sigma e^{kappa t} dB. Integrate from 0 to t.
- Exact discretisation (2.4): x_{ih} = alpha + phi x_{(i-1)h} + eps_{ih}, with
  - phi = exp(-kappa h)
  - alpha = mu (1 - exp(-kappa h))
  - eps i.i.d. N(0, sigma_eps^2), sigma_eps^2 = sigma^2 (1 - exp(-2 kappa h)) / (2 kappa).
  This is exact, not an Euler approximation, because the stochastic integral in (2.2) over one step is
  Gaussian with that variance.
- Estimator (2.5): kappa_hat = -ln(phi_hat)/h, where phi_hat is the OLS slope, with the sample means
  removed when mu is unknown. Gaussian errors make OLS conditional on x_0 the conditional MLE. Then
  mu_hat = alpha_hat/(1 - phi_hat) and sigma_hat^2 = sigma_eps_hat^2 x 2 kappa_hat / (1 - phi_hat^2).
  Avellaneda and Lee (2010, eq. (21)) use the same mapping on daily data: "kappa = -log(b) * 252",
  m = a/(1-b), and an equilibrium s.d. sigma_eq = sqrt(Var(zeta)/(1 - b^2)).
- Half-life [derived]: the expected deviation decays as e^{-kappa t}, so the half-life is ln 2 / kappa.
- Stationary s.d.: sigma/sqrt(2 kappa). Avellaneda and Lee's "s-score" is s = (X(t) - m)/sigma_eq, a
  deviation measured in stationary s.d.'s (their eq. (15)).
- Finite-sample bias.
  - The Kendall (1954) / Marriott-Pope (1954) approximation for an AR(1) with unknown mean is
    E[phi_hat - phi] ~ -(1 + 3 phi)/n. [unverified: I could not fetch Yu (2012) or Tang and Chen (2009)
    in full. The formula is from my training memory. Yu's abstract, seen only in a search summary, says
    his first approximation "follows the bias formula of Marriott and Pope (1954)" and "performs poorly
    when mean reversion is slow". My Monte Carlo below checks the formula numerically.]
  - Verified from fetched text: Bao et al. write "there exists serious bias in estimating the mean
    reversion parameter (kappa) by almost all the methods, especially when ... the speed of mean
    reversion is slow". They report that Tang and Chen (2009) showed "the bias of kappa_hat is up to
    O(T^-1) ... where T is the time span", and that Phillips and Yu (2005) found substantial MLE bias
    "regardless of data frequency".
  - Bias in kappa [derived from the AR(1) formula]: Delta kappa ~ (1 + 3 phi)/(n h phi), which is about
    4/T when phi ~ 1, with T = n h. The relative bias is therefore about 4/(kappa T) = 5.8 x
    (half-life / T). Keeping the bias in kappa under 10% needs a span of about 58 half-lives.

**(3) Data.** Any equally spaced series of the variable modelled. On the pilot, the natural candidates
for x(t) are:
- (a) the mid or microprice minus a slow reference: price mean reversion
- (b) top-of-book imbalance I = (q_bid - q_ask)/(q_bid + q_ask): order-flow persistence. Measuring it
  continuously needs the BBO sizes all the time, which means mbp-1 or mbp-10. tbbo records the BBO only
  at trades.
- (c) the spread in ticks
- (d) the microprice minus the mid.

Four months at 1 s is about 85 sessions x 23,400 = 2.0 million observations. Precision is not the
constraint, as the next sentence shows: the asymptotic s.d. of kappa_hat is about sqrt(2 kappa / T)
[unverified: a standard expanding-domain result, not checked against a fetched source]. For
kappa = 0.05/s and T = 2.0 million s, that is 0.00022/s. The constraint is non-stationarity: the mean
and the speed change across the session and across days.

**(4) What it estimates.** The mean-reversion speed and half-life, the long-run mean and the stationary
s.d. For a quoting strategy, the half-life of a signal such as imbalance is the shelf life of an edge.
It can be compared with order latency (tens of ms) and queue times.

**(5) Worked example (E4: exact formulas, then a Monte Carlo of 4,000 replications with the mean
estimated).**
- phi = 0.95 at h = 1 s: kappa = -ln 0.95 = 0.0513/s, half-life 13.5 s.
  - With a 10-minute window (n = 600), the approximate bias is -(1 + 2.85)/600 = -0.0064.
  - So E[phi_hat] ~ 0.9436, giving kappa ~ 0.0581/s (13% too fast) and a half-life of about 11.9 s.
  - Monte Carlo: mean phi_hat = 0.94381 (bias -0.00619, against the formula's -0.00642). The median
    kappa_hat is 0.0562.
- phi = 0.999 (true half-life 693 s, about 11.5 min) with the same 10-minute window:
  - The formula gives E[phi_hat] ~ 0.99234, so kappa_hat ~ 0.0077/s, 7.7 times the true value. The
    apparent half-life is 90 s.
  - Monte Carlo: bias -0.00875, larger than the formula's -0.00666, as Yu reports for slow mean reversion.
    The median kappa_hat is 0.0081, 8.1 times the true value.
  - With a full session (n = 23,400) the bias in kappa falls to 17%.
- The lesson for the pilot: an OU fit on short windows turns a slowly drifting mid into a "13-second
  mean reverter". Any OU-based signal must have its span declared in advance with T >= about 60
  half-lives. It should also be checked against a random-walk null simulated with the same n.

**(6) Pilot hypotheses.**
- H-SDE-OU-IMB (descriptive, 0 configurations proposed). The OU half-life of 1-s top-of-book imbalance
  on the pilot contract exceeds 10 times the measured order round-trip latency. Statistic: kappa_hat
  from the exact AR(1), with a day-block bootstrap confidence interval and the bias check above. It
  decides whether any imbalance signal can be acted on at retail latency. The trading rule that would
  use it belongs to C2_LOB and C2_DeepLOB, and counts there.
- H-SDE-MART (descriptive). The 1-s mid-price return is a martingale difference: the variance ratio
  VR(q) = Var(r_q)/(q Var(r_1)) = 1 for q in {10, 60}. Statistic: the variance-ratio z with a
  heteroskedasticity-robust s.e. [unverified: Lo-MacKinlay (1988) was not fetched]. 0 configurations
  as a description. If a rule fades mid moves on the basis of VR < 1, it is 1 configuration per
  horizon tested.
- If the lead registers any OU-based quoting rule, every (variable, window, entry band) triple is one
  configuration. Example: Avellaneda-Lee-style s-score bands of 1.25/0.5 on imbalance with a 30-minute
  window would be 1 configuration. A grid of 3 windows x 3 bands is 9.

**(7) Compute.** One OLS per window, trivial on the laptop. The Monte Carlo bias checks (4,000 paths x
600 steps) take seconds.

**(8) Evidence.**
- Avellaneda and Lee (2010), OU s-score statistical arbitrage on US equities residuals at daily
  horizon, with 10 bp round-trip costs: "PCA-based strategies have an average annual Sharpe ratio of
  1.44 over the period 1997 to 2007, with much stronger performances prior to 2003. During 2003-2007 ...
  only 0.9". ETF-based signals showed "a similar degradation after 2002". This is post-publication-era
  decay, and the setting is a different market and horizon from ours.
- At the MES tick scale, the only direct evidence I found is Safari and Schmidhuber's negative verdict
  on the tick oscillation (section 2).
- I found no out-of-sample, cost-inclusive result for OU-based quoting on a single futures contract at
  retail latency.

---

## 6. Realised variance under microstructure noise: TSRV and related estimators

**(1) Core idea.** Summing squared high-frequency returns (realised variance, RV) estimates the
integrated variance integral sigma^2 dt only if prices are observed without error. With additive
noise, each return carries two noise terms. Their squares do not average out: they add up, so RV grows
with the number of observations. Two-scales realised variance (TSRV) does three things:
- it averages RV over K sparse subgrids, which keeps all the data but cuts the noise bias by a factor
  of about K
- it estimates the remaining bias from the full-grid RV, which is mostly noise
- it subtracts that bias.

**(2) Key equations** (Zhang, Mykland and Ait-Sahalia 2005; equation numbers from the NBER WP 10111
version I fetched).
- Observation model (4): Y_{t_i} = X_{t_i} + eps_{t_i}. X is the efficient Ito process. eps is noise,
  i.i.d., mean 0, independent of X.
- Bias of full-grid RV (10): E([Y,Y]_T | X) = [X,X]_T + 2n E(eps^2). Variance (11): 4n E(eps^4) + O_p(1).
  The paper: "[Y;Y]_T has a positive bias whose magnitude increases linearly with the sample size n".
- Noise variance estimator (12): E(eps^2)_hat = [Y,Y]^(all)_T / (2n).
- Subsample average (13): [Y,Y]^(avg)_T = (1/K) sum_{k=1}^K [Y,Y]^(k)_T, where grid k uses every K-th
  observation starting at offset k. Average subsample size (15): n_bar = (n - K + 1)/K.
- TSRV (32)-(33): <X,X>_hat_T = [Y,Y]^(avg)_T - 2 n_bar E(eps^2)_hat = [Y,Y]^(avg)_T -
  (n_bar/n) [Y,Y]^(all)_T.
- Rate (35)-(36): the error is O_p(n_bar^{1/2}/K^{1/2}) + O_p(n_bar^{-1/2}). The bars over n are lost in
  the text extraction, and I read them from the structure. With n_bar ~ n/K the two terms are n^{1/2}/K,
  from noise, and (K/n)^{1/2}, from discretisation. The paper: "The error is minimized by equating the
  two terms", which gives K = O(n^{2/3}) and an O_p(n^{-1/6}) error. In practice K = c n^{2/3} (36).
- Small-sample adjustment (41)-(42): multiply by (1 - n_bar/n)^{-1}. The paper: "one should take
  a(1 - n_bar/n) = 1".
- Related estimators.
  - Uncertainty-zones RV for large-tick assets (section 2, Dayri-Rosenbaum eq. (3)).
  - Realised kernels (Barndorff-Nielsen, Hansen, Lunde and Shephard 2008) [unverified: not fetched].
  - Pre-averaging (Jacod, Li, Mykland, Podolskij and Vetter 2009) [unverified: not fetched].
  - Christensen et al. use pre-averaging on tick data: their keywords include "pre-averaging".

**(3) Data.** The sequence of one price series. At a 1-s grid, any schema works. The noise term that
matters is the one in the observed price. For trade prices it is the bid-ask bounce. For the mid on a
1-tick book it is mainly rounding to the 0.125-point grid. Hansen and Lunde warn that the i.i.d.
assumption fails: "market microstructure noise is time-dependent and correlated with increments in the
efficient price" (DJIA, 2000-2002; September 2004 version). Four months of one contract is plenty for daily or 5-minute estimates.

**(4) What it estimates.** It estimates integrated variance over a window (a day, or a trailing 5 to
30 minutes), and the variance of the noise. For the pilot, it supplies:
- the volatility state variable for conditioning fill rates and markouts
- the sigma for the touch-probability model (section 7)
- the sigma input to Avellaneda-Stoikov-type quoting (C2_Control).

**(5) Worked example.** E5b: 200 synthetic sessions on a 1-s grid. The efficient price is an ABM with
the illustrative 47.25-point daily s.d., so the true IV is 2232 points^2. Each estimator is shown as
its ratio to the true IV, as mean (s.d.).

| observed price | RV 1 s | RV 60 s | RV 300 s | TSRV K=60 | TSRV K=300 | TSRV K=818 (=n^{2/3}) |
|---|---|---|---|---|---|---|
| X + i.i.d. N(0, 0.10^2) noise | 1.210 (0.011) | 0.993 (0.071) | 0.993 (0.148) | 0.978 (0.055) | 0.982 (0.126) | 0.964 (0.220) |
| X rounded to the 0.125 grid | 1.027 (0.009) | 0.990 (0.071) | 0.993 (0.149) | 0.978 (0.055) | 0.982 (0.126) | 0.964 (0.220) |

Checks and readings:
- The RV 1 s bias under i.i.d. noise matches eq. (10): 2n E(eps^2) = 2 x 23400 x 0.01 = 468, which is
  21% of 2232.
- With (41) applied, TSRV at K = 60 becomes about 0.978/(1 - 1/60) = 0.995.
- The remaining shortfall is an edge effect: each of the K subgrids misses, on average, (K-1)/n of the
  session, so E[TSRV]/IV is about 1 - (K-1)/n - n_bar/n: 0.981, 0.984 and 0.964 for K = 60, 300, 818,
  which the table reproduces. Neither (41) nor more data at the same K removes it; in the pilot, scale
  by n/(n-K+1) or anchor every subgrid to both ends of the session.
- The textbook K = n^{2/3} is far too large at n = 23,400 with this little noise. The constant c must
  be tuned, and it is a choice that should be declared in advance.
- At 1 s on MES-like volatility (1.24 ticks per second), rounding noise biases RV by only 2.7%. The
  noise problem grows when sampling in tick time, where n per session is much larger. That count is
  unknown until the pilot.
- The noise estimator (12) needs n large relative to IV/(2 E eps^2). At 1 s it overstates the noise:
  0.058 points^2 estimated against 0.010 true in the one-day E5 run.

**(6) Pilot hypothesis.**
- H-SDE-VOL (a rule or a conditioning test). Passive fills in the top tercile of the trailing 5-minute
  TSRV have worse mean cost-inclusive markout than fills in the bottom tercile. Statistic: the
  difference in means, with day-clustered s.e. and a one-sided test.
  - Configurations: 1 if the window, the split and K are fixed in advance.
  - Used as a filter ("quote only outside the top tercile"), it is the same single configuration. Each
    extra window or split adds 1.
  - Sample: needs a few thousand fills (section 7, E3).
- Volatility measurement itself is descriptive: 0 configurations proposed.

**(7) Compute.** O(n K) per window if done naively, and O(n) with cumulative sums. A session of 1-s data
takes milliseconds. Tick-time data at about 10^6 updates per session is still seconds. This is a guess
at the count. The laptop handles it.

**(8) Evidence.** As statistics these estimators are sound, with consistency and rates proven by ZMA.
- Hansen and Lunde's bias correction "can greatly reduce the mean squared error". But they reject i.i.d.
  noise in both trade and quote data.
- As trading inputs: I found no cost-inclusive evidence that a TSRV-conditioned quoting rule beats an
  unconditioned one for a slow participant. Its value for this program is as a measurement tool.

---

## 7. What these models say about a 1-lot passive strategy on a tick-sized futures book

This section puts sections 1 to 6 together for the pilot's object: one resting 1-lot limit order at the
touch on one large-tick contract, with tens of milliseconds of latency.

**7.1 The martingale markout budget (E3).**
- Suppose the mid is a martingale and fills carry no information about future mid moves. A passive
  buy at the bid on a 1-tick book then has expected markout (mid minus fill price) of +0.5 tick at
  every horizon. A round turn of two passive fills earns 1 tick, $1.25.
- The MES round-turn commission is $1.22, or 0.488 tick per fill. The margin before any adverse
  selection is $0.03 per round turn: 0.012 tick per fill.
- Adverse selection of 0.05 tick per fill turns the round turn to -$0.095. At 0.10 tick it is -$0.22,
  and at 0.25 tick it is -$0.595.
- So the cost structure leaves almost nothing. Even a perfectly uninformed counterparty flow gives a
  margin that a 0.012-tick adverse move erases.
- The program's earlier finding fits this: E.25 found that limit orders rescue no earlier rule (as
  summarised in READER_RULES; the C3 section cites the return itself).

**7.2 What a diffusion says about a resting order [derived].**
- In a continuous martingale price model, a limit buy at level a below the price fills when the price
  first hits a, at the stopping time tau_a. By the strong Markov property (MIT L17, used in the
  reflection-principle proof), the price after tau_a is again a martingale started at a. So
  E[S_{tau_a + h} - a | filled] = 0.
- A resting order in a diffusion earns nothing against its own fill price. All of its gross edge comes
  from the discreteness of the quote grid: the half-spread between the efficient price and the bid.
- Any edge therefore has to come from one of four places:
  - (i) the tick being large relative to the efficient-price uncertainty (eta < 1/2, section 2)
  - (ii) queue position, since fills at the front of the queue are less adversely selected than fills
    at the back. That is queue mathematics, covered by C2_LOB.
  - (iii) conditioning on state: volatility (section 6), imbalance (section 5), or news and jumps
    (sections 3 and 4)
  - (iv) fee rebates, which a retail prop account does not get.

**7.3 Touch probability is not fill probability (E2).**
- By the reflection principle (MIT 18.S096 L17, Proposition 2.3), P(max_{s<=t} B(s) >= a) =
  2 - 2 Phi(a/sqrt(t)). For a price with s.d. sigma per sqrt-second, the argument is a/(sigma sqrt(t)).
  With sigma = 1.24 ticks/sqrt(s), the probability that the price touches a level within t is:

| level away | t = 1 s | t = 10 s | t = 60 s |
|---|---|---|---|
| 1 tick | 0.418 | 0.798 | 0.917 |
| 2 ticks | 0.105 | 0.609 | 0.834 |
| 4 ticks | 0.001 | 0.306 | 0.676 |

- On a real book, a touch fills an order only after the whole queue ahead of it trades. An order joining
  at the touch has touch probability 1, but its fill probability depends on queue depletion.
- The pilot can measure the gap between the diffusion touch rate (from the TSRV sigma) and the observed
  fill rate. That gap is a direct, model-light measure of how much the queue matters.
- Cont and de Larrard (2013) make the dependence of price moves on queues explicit. In their Markov
  queue model, the probability that the next price move is up, given n orders on the bid and p on the
  ask, is phi(n,p) (eq. (7)), a closed-form integral. In the balanced case (limit-order rate lambda =
  market-order rate mu + cancellation rate theta), the rescaled price s_{n log(n) t}/sqrt(n) converges to "delta sqrt(pi lambda / D(f))
  W_t" (Theorem 1; the per-unit-time sigma is their eq. (13)). Here delta is the tick, and D(f) = sum_ij i j f(i,j) (eq. (9)) is a depth measure of
  the queue sizes after a price change.
- So the diffusion's sigma is not a primitive at this scale. It is set by the tick size, order arrival
  rates and depth. Diffusion-level models are good for estimating sigma, and queue-level models (C2_LOB,
  C2_Hawkes) are needed for fills.

**7.4 Latency.**
- Baron, Brogaard, Hagstromer and Kirilenko (JFQA 2019; the WP version was fetched): "differences in
  relative latency account for large differences in HFTs' trading performance". Speed works "through
  both the short-lived information channel and the risk management channel", and it helps "market
  making".
- A Vancouver order with tens of ms of latency is at the bottom of that ranking. Given the 0.012-tick
  margin in 7.1, an order that cannot be cancelled before faster traders act on new information is the
  textbook adversely selected order.
- Cartea, Jaimungal and Sanchez-Betancourt (2019) model latency for liquidity takers ("there is no
  guarantee that MLOs are filled"). That is a different problem, and it does not change this point.

**7.5 Sample size (E3).** Assume independent fills, which is optimistic because fills cluster. The
fills needed to detect a per-fill edge delta over cost, one-sided at 5% with 80% power, using per-fill
markout s.d. sigma sqrt(h):

| horizon | markout s.d. (ticks) | delta = 0.05 tick | delta = 0.10 tick | delta = 0.25 tick |
|---|---|---|---|---|
| 1 s | 1.24 | 3,774 | 944 | 151 |
| 10 s | 3.91 | 37,745 | 9,436 | 1,510 |
| 60 s | 9.57 | 226,467 | 56,617 | 9,059 |

- A 1-lot pilot on one contract might see something like 50 to 200 fills a session. This is a guess:
  the pilot will measure it. That is about 4,000 to 17,000 fills in 85 sessions.
- That supports a 60-s test only for edges of about 0.25 tick, which is 20 times the cost margin. The
  1-s horizon is well powered but shows mostly the half-spread before adverse selection has played out.
- Recommendation for the lead: declare one primary horizon and one effect size in advance, and report
  the others as descriptive.

**7.6 What the textbook says the strategy problem is.** Cartea, Jaimungal and Penalva (2015) treat this
problem in chapter 10, "Market Making", with sections "10.2.2 Market Making At-The-Touch", "10.4 Market
Making with Adverse Selection" and "10.4.2 Short-Term-Alpha and Adverse Selection" (front matter fetched).
Chapter 11 covers "Pairs Trading and Statistical Arbitrage Strategies" with "Co-integrated Log Prices
with Short-Term-Alpha", the OU tools of section 5. Their stochastic-calculus appendix A covers diffusion
processes, jump processes, doubly stochastic Poisson processes and Feynman-Kac. I could not fetch the
chapters themselves, so their content beyond the table of contents is [unverified]. The control
problems are C2_Control's.

---

## 8. Compute needs (all methods in this section)

- Every method here is closed-form, an OLS, or a small likelihood. None needs a GPU.
- The binding cost is reading the raw data:
  - The Databento MBP-10 record (fields listed in the fetched docs) is ts_recv 8 + ts_event 8 + rtype 1
    + publisher_id 2 + instrument_id 4 + action 1 + side 1 + depth 1 + price 8 + size 4 + flags 1 +
    ts_in_delta 4 + sequence 4 = 47 bytes, plus 10 levels x (bid_px 8 + ask_px 8 + bid_sz 4 + ask_sz 4 +
    bid_ct 4 + ask_ct 4 = 32) = 320 bytes. That is 367 bytes of fields, about 368 bytes per record, the
    extra byte being the DBN record header's length field [unverified; the rest derived from the docs' field types].
  - At an assumed 2 to 10 million records per session (a guess; the pilot will measure it), one session
    is 0.7 to 3.7 GB raw.
  - Processed day by day, keeping only BBO, trades and derived 1-s series, the peak memory is well under
    the laptop's limits (CLAUDE.md: half of available memory per job, chunked).
  - Four months fit on disk at 60 to 300 GB raw (a guess). Store only the reduced series.
- Laptop (20 threads, 14 GB, RTX 3050 4 GB): sufficient for every method in this section, including the
  Monte Carlo bias checks.
- Bigger machine, if day-by-day streaming proves slow. A Lambda on-demand "NVIDIA A10 24 GB" instance
  with "30" vCPUs and "226 GiB" RAM is "$1.29" per GPU-hour, and a "Quadro RTX 6000" (14 vCPU, 46 GiB) is
  "$0.69" (lambda.ai/pricing, fetched 2026-10-21). Ten hours on the A10 box costs $12.90, plus tax.
  Hetzner's dedicated-vCPU "General Purpose" cloud starts at "EUR 43.49 per month, excl. VAT"
  (hetzner.com/cloud, fetched). Neither is needed for this section's methods.

---

## 9. Verdicts (use / maybe / skip for this program)

| method | verdict | reason |
|---|---|---|
| Ito processes and Ito's lemma | use (as language) | Needed to read every other model and the C2_Control HJB work. No testable claim of its own. |
| ABM vs GBM at tick scale | use ABM, skip GBM distinctions | At 1 to 60 s the two differ by about 0.002 tick in mean (E1). ABM in ticks is the simpler working model. Neither describes the 0.25 grid. |
| Roll bounce / uncertainty zones (eta, implicit spread, efficient-price recovery) | use (descriptive) | Cheap. Directly measures tick-scale mean reversion and how large the tick is on the pilot contract. A bounce-capture rule built on it is "maybe" at best: Safari-Schmidhuber's direct E-mini verdict is negative. |
| Merton / Kou jump-diffusion fits | skip (as models); maybe (as risk accounting) | Built for option pricing, and nothing here suggests a quoting gain. The useful part is the arithmetic of the jump tail against a $0.03 round-turn margin (section 3), which needs no fitted model. |
| Jump tests (BV, Lee-Mykland, ASJ) | maybe (descriptive, data cleaning) | Useful for labelling events and splitting markouts. Fragile: spurious detections are up to 90%, and they are an ex-post flag. As a real-time quote filter I expect a null. Use the noise-robust variants at 5 s if used. |
| OU process, exact AR(1) estimation, half-life, bias checks | use (as an estimation tool) | Gives the shelf life of signals such as imbalance against latency. The bias analysis is a guard against spurious "fast mean reversion" from short windows. Skip OU price mean reversion as a stand-alone strategy: no cost-inclusive evidence at this scale, and Avellaneda-Lee decayed post-2002. |
| RV / TSRV / uncertainty-zones RV | use (as a measurement tool) | Cheap and well founded. Gives the volatility state for conditioning fills and markouts and for touch-rate baselines. Not a strategy. Declare K, or c, and the windows in advance. |
| Diffusion touch probability vs measured fills | use (pilot diagnostic) | The gap between Brownian touch rates and observed fill rates measures the queue effect directly, with no model fitting. |

## 10. Pre-registerable hypotheses from this section, with proposed trial counts

These are proposals. The lead decides selection rules and counts. "Descriptive" means the item selects
no rule and reports an estimate. I propose that such items add 0 to N, but that is the lead's call.

| id | type | statistic | sample | proposed configurations |
|---|---|---|---|---|
| H-SDE-ETA | descriptive | daily eta_hat = N^(c)/(2 N^(a)), with day-block bootstrap CI; H0 eta = 1/2 | all pilot sessions | 0 |
| H-SDE-BOUNCE | rule | mean cost-inclusive markout per fill at one pre-declared horizon; one-sided, day-clustered t | as many fills as the pilot gives; see 7.5 for power | 1 (or 3 if all horizons are tested) |
| H-SDE-NEWS | rule | difference in mean markout, fills inside vs outside a fixed window around scheduled releases | about 70 release windows in 4 months; low power | 1 |
| H-SDE-JUMPFILTER | rule | difference in mean markout with vs without a post-flag cooldown (LM 1% Gumbel threshold, fixed cooldown X) | all fills; few flags | 1 per (threshold, cooldown) pair |
| H-SDE-JUMPSHARE | descriptive | share of adverse markout mass within flagged windows | all fills | 0 |
| H-SDE-OU-IMB | descriptive | exact-AR(1) kappa_hat of 1-s imbalance, half-life against measured latency, with bias check and random-walk null | all sessions | 0 |
| H-SDE-MART | descriptive (or rule) | variance ratio VR(q), q in {10, 60}, of 1-s mid returns | all sessions | 0 descriptive; 1 per horizon if used as a rule |
| H-SDE-VOL | rule (conditioning/filter) | difference in mean markout, top vs bottom tercile of trailing 5-min TSRV (K fixed) | a few thousand fills | 1 |
| touch vs fill gap | descriptive | observed fill rate minus Brownian touch probability at the same sigma and distance | all resting orders | 0 |

If every rule above were registered with a single configuration, the section would add 4 to N:
BOUNCE, NEWS, JUMPFILTER and VOL. With all three horizons for BOUNCE and both VR horizons used as
rules, it would add 8. All of these need the pilot's fills, so they cannot be tested on the
public-research side alone.

## 11. References

Fetched in full (file under pages/C2_SDE/):
- Ait-Sahalia, Y. and Jacod, J. (2009). Testing for jumps in a discretely observed process. Annals of
  Statistics 37(1), 184-222. arXiv:0903.0226. [aitsahalia_jacod_2009_jumps.pdf]
- Avellaneda, M. and Lee, J.-H. (2010). Statistical arbitrage in the US equities market. Quantitative
  Finance 10(7). Author copy dated 2009-06-16. [avellaneda_lee_2010_statarb.pdf]
- Bajgrowicz, P., Scaillet, O. and Treccani, A. (2016). Jumps in high-frequency data: spurious
  detections, dynamics, and news. Management Science 62(8), 2198-2217. UNIGE submitted version.
  [bajgrowicz_scaillet_treccani.pdf]
- Bao, Y., Ullah, A. and Wang, Y. (2014). Exact distribution of the mean reversion estimator in the
  Ornstein-Uhlenbeck process. UCR working paper 201413. [bao_ullah_wang_2014_ou_estimator.pdf]
- Barndorff-Nielsen, O. E. and Shephard, N. (2006). Econometrics of testing for jumps in financial
  economics using bipower variation. Journal of Financial Econometrics 4(1), 1-30. Nuffield WP version.
  [bns_2006_bipower_jumps.pdf]
- Baron, M., Brogaard, J., Hagstromer, B. and Kirilenko, A. (2019). Risk and return in high-frequency
  trading. JFQA 54(3), 993-1024. CityU GRU WP 2017-018 version. [baron_etal_hft_risk_return_wp.pdf]
- Cartea, A., Jaimungal, S. and Sanchez-Betancourt, L. (2019). Latency and liquidity risk.
  arXiv:1908.03281. [cartea_jaimungal_sb_latency.pdf]
- Christensen, K., Oomen, R. C. A. and Podolskij, M. (2014). Fact or friction: jumps at ultra high
  frequency. Journal of Financial Economics 114(3). arXiv:2602.10925 (2014 manuscript).
  [christensen_oomen_podolskij_fact_friction.pdf]
- Cont, R. and de Larrard, A. (2013). Price dynamics in a Markovian limit order market. SIAM Journal on
  Financial Mathematics 4(1). arXiv:1104.4596. [cont_delarrard_2013_markov_lob.pdf]
- Dayri, K. and Rosenbaum, M. (2015). Large tick assets: implicit spread and optimal tick size. Market
  Microstructure and Liquidity 1(1). arXiv:1207.6325. [dayri_rosenbaum_large_tick.pdf]
- Hansen, P. R. and Lunde, A. (2006). Realized variance and market microstructure noise. JBES 24(2).
  September 2004 version. [hansen_lunde_2006.pdf]
- Kou, S. G. (2002). A jump-diffusion model for option pricing. Management Science 48(8), 1086-1101.
  [kou_2002.pdf]
- Lee, S. S. and Mykland, P. A. (2008). Jumps in financial markets: a new nonparametric test and jump
  dynamics. Review of Financial Studies 21(6), 2535-2563. [lee_mykland_2008.pdf]
- Maneesoonthorn, W., Martin, G. M. and Forbes, C. S. (2020). High-frequency jump tests: which test
  should we use? Journal of Econometrics. arXiv:1708.09520v3. [maneesoonthorn_jump_tests_which.pdf]
- MIT OpenCourseWare 18.S096 (Fall 2013), Topics in Mathematics with Applications in Finance, lecture
  notes 5, 17 and 18 (C. Lee). CC BY-NC-SA. [mit_18s096_lec5.pdf, mit_18s096_lec17.pdf,
  mit_18s096_lec18_ito.pdf]
- Safari, S. A. and Schmidhuber, C. (2025). Trends and reversion in financial markets on time scales
  from minutes to decades. arXiv:2501.16772v2. [safari_schmidhuber_2025_trends_reversion.pdf]
- Zhang, L., Mykland, P. A. and Ait-Sahalia, Y. (2005). A tale of two time scales: determining
  integrated volatility with noisy high-frequency data. JASA 100, 1394-1411. NBER WP 10111 (2003)
  version. [zma_2005_tsrv_nber.pdf]

Fetched, publisher or reference pages only:
- Ait-Sahalia, Y. and Jacod, J. (2014). High-Frequency Financial Econometrics. Princeton University
  Press. Book description via Wayback. [asj_2014_princeton_wayback.html]
- Cartea, A., Jaimungal, S. and Penalva, J. (2015). Algorithmic and High-Frequency Trading. Cambridge
  University Press, ISBN 978-1-107-09114-6. Front matter and table of contents.
  [cjp_2015_frontmatter.pdf]
- Databento docs, MBP-10 schema. [databento_mbp10_docs.html]
- Lambda GPU cloud pricing [lambda_pricing.html]. Hetzner cloud pricing [hetzner_cloud.html].

Cited but not fetched [unverified beyond the stated use]:
- Shreve, S. E. (2004). Stochastic Calculus for Finance II: Continuous-Time Models. Springer. The brief's
  core text. Not fetched: the Springer page served a bot challenge and the Wayback capture was an empty
  shell. Its standard results (Ito's lemma, the reflection principle, OU) are cited here from the MIT
  notes instead.
- Merton, R. C. (1976). Option pricing when underlying stock returns are discontinuous. JFE 3, 125-144.
  Described via Kou (2002).
- Robert, C. Y. and Rosenbaum, M. (2011). A new approach for the dynamics of ultra-high-frequency data:
  the model with uncertainty zones. JFEc 9(2), 344-366. Used via Dayri-Rosenbaum. HAL served a bot check.
- Yu, J. (2012). Bias in the estimation of the mean reversion parameter in continuous time models. J.
  Econometrics 169, 114-122. Abstract seen only in a search summary.
- Tang, C. Y. and Chen, S. X. (2009). Parameter estimation and bias correction for diffusion processes.
  J. Econometrics 149, 65-81. Cited via Bao et al.
- Phillips, P. C. B. and Yu, J. (2005). Cited via Bao et al.
- Kendall, M. G. (1954) and Marriott, F. H. C. and Pope, J. A. (1954): the AR(1) bias formula, from
  memory.
- Roll, R. (1984). A simple implicit measure of the effective bid-ask spread. Journal of Finance 39.
  Derivation given in full.
- Lo, A. W. and MacKinlay, A. C. (1988). Variance-ratio test.
- Barndorff-Nielsen, O. E., Hansen, P. R., Lunde, A. and Shephard, N. (2008). Realised kernels,
  Econometrica 76.
- Jacod, J., Li, Y., Mykland, P. A., Podolskij, M. and Vetter, M. (2009). Pre-averaging, Stochastic
  Processes and their Applications 119.
- Lee, S. S. and Mykland, P. A. (2012). Jumps in equilibrium prices and market microstructure noise
  (LM12). Named in Maneesoonthorn et al.

Repo source: rules/products.py (MES tick 0.25, tick value 1.25, round-turn commission 122 cents).

Note on bibliographic details: titles, authors and years match the fetched files. Journal volume,
issue and page numbers are from memory unless the fetched file prints them (Ait-Sahalia-Jacod 2009,
Kou 2002, the Lee-Mykland page 2535, and ZMA via the search record) [unverified otherwise]. The
journal of Maneesoonthorn et al. is not printed in the arXiv copy.

## 12. Evidence table

Quotes are verbatim from the saved text, except that math typography is approximated where
pdftotext dropped Greek letters, bars or superscripts. Such cases are noted in brackets.

| claim | source | verbatim quote | saved file |
|---|---|---|---|
| Ito's lemma statement | MIT 18.S096 L18 | "Theorem 1.1. (Ito’s lemma) Let f (t, x) be a smooth function of two variables, and let Xt be a stochastic process satisfying dXt = µt dt + σt dBt for a Brownian motion Bt." | mit_18s096_lec18_ito.pdf |
| Ito proof drops dt dB, dt^2 | MIT 18.S096 L18 | "We can ignore the terms dtdBt and (dt)2 ." | mit_18s096_lec18_ito.pdf |
| ABM definition | MIT 18.S096 L18 | "The stochastic process Xt = µt + σBt is known as the Brownian motion with drift µ" | mit_18s096_lec18_ito.pdf |
| Quadratic variation of BM | MIT 18.S096 L17 | "A Brownian motion Bt satisfies the following equation with probability 1: lim (Bti+1 − Bti )2 = T." [sum and limit subscript dropped] | mit_18s096_lec17.pdf |
| Reflection principle | MIT 18.S096 L17 | "P(M (t) ≥ a) = 2P(B(t) > a) = 2 − 2Φ( a/√t )." [fraction typeset] ... "is also known as the ‘reflection principle’." | mit_18s096_lec17.pdf |
| OU SDE | Bao, Ullah, Wang 2014 | "dx(t) = κ(µ − x(t))dt + σdB(t), (2.1)" | bao_ullah_wang_2014_ou_estimator.pdf |
| Exact AR(1) discretisation | Bao, Ullah, Wang 2014 | "The exact discrete model corresponding to (2.1) is an AR(1) model" ... "where φ = exp(−κh), α = µ[1−exp(−κh)]" | bao_ullah_wang_2014_ou_estimator.pdf |
| LS/ML estimator of kappa | Bao, Ullah, Wang 2014 | "It is well known that the LS/ML estimator of κ based on the discrete data is κ̂ = − ln(φ̂)/h, (2.5)" [fraction typeset] | bao_ullah_wang_2014_ou_estimator.pdf |
| kappa bias serious when slow | Bao, Ullah, Wang 2014 | "there exists serious bias in estimating the mean reversion parameter (κ) by almost all the methods, especially when the diffusion process has a linear drift function and the speed of mean reversion is slow (i.e., small values of κ)." | bao_ullah_wang_2014_ou_estimator.pdf |
| Bias O(1/T) in span | Bao et al. citing Tang-Chen | "Tang and Chen (2009) showed that the bias of κ̂ is up to O(T −1 ) in the stationary Vasicek model (Vasicek, 1977), where T is the time span." | bao_ullah_wang_2014_ou_estimator.pdf |
| Frequency does not fix bias | Bao et al. citing Phillips-Yu | "the bias of the maximum likelihood estimator (MLE) for κ in the CIR model ... can be substantial for data sets with very long time spans, regardless of data frequency." | bao_ullah_wang_2014_ou_estimator.pdf |
| OU fit mapping on daily data | Avellaneda-Lee 2010 | "κ = −log(b) ∗ 252" | avellaneda_lee_2010_statarb.pdf |
| OU stat-arb decay | Avellaneda-Lee 2010 | "after accounting for transaction costs, PCA-based strategies have an average annual Sharpe ratio of 1.44 over the period 1997 to 2007, with much stronger performances prior to 2003. During 2003-2007, the average Sharpe ratio of PCA-based strategies was only 0.9." | avellaneda_lee_2010_statarb.pdf |
| Their cost assumption | Avellaneda-Lee 2010 | "we assume a slippage/transaction cost of 0.05% or 5 basis points per trade (a round-trip transaction cost of 10 basis points)." | avellaneda_lee_2010_statarb.pdf |
| RV bias grows with n | ZMA 2005 (NBER WP) | "[Y; Y ]T has a positive bias whose magnitude increases linearly with the sample size n." | zma_2005_tsrv_nber.pdf |
| Additive noise model | ZMA 2005 | "Yti = Xti + ti : (4)" [epsilon dropped by extraction] | zma_2005_tsrv_nber.pdf |
| TSRV construction | ZMA 2005 | "Hence the bias of [Y; Y ](avg) can be consistently estimated by 2n^. A bias-adjusted estimator for < X; X > can thus be obtained by" [n-bar and epsilon-hat dropped] | zma_2005_tsrv_nber.pdf |
| Optimal K | ZMA 2005 | "The error is minimized by equating the two terms on the right hand side of (35), yielding that the optimal sampling step for [Y; Y ](avg) is K = O(n2=3 )." [= is the extraction of /] | zma_2005_tsrv_nber.pdf |
| Small-sample adjustment | ZMA 2005 | "Hence one can argue that one should take a(1 n=n) = 1, yielding (41)." [minus and bar dropped] | zma_2005_tsrv_nber.pdf |
| Noise not i.i.d. | Hansen-Lunde | "market microstructure noise is time-dependent and correlated with increments in the efficient price. These properties are found in both transaction and quotation data." | hansen_lunde_2006.pdf |
| Bias correction helps MSE | Hansen-Lunde | "The bias correction can greatly reduce the mean squared error of the RV" | hansen_lunde_2006.pdf |
| mu1 constant | BNS 2006 | "µ1 = E |u| = √2/√π ≃ 0.79788 (5)" | bns_2006_bipower_jumps.pdf |
| BV/RV limit without jumps | BNS 2006 | "It converges to µ21 ≃ 0.6366 under BSM. Estimates below µ 21 provide evidence for jumps." | bns_2006_bipower_jumps.pdf |
| vartheta constant | BNS 2006 | "ϑ = π 2 /4 + π − 5 ≃ 0.6090. (6)" | bns_2006_bipower_jumps.pdf |
| LM window choice | Lee-Mykland 2008 | "We suggest the smallest integer K that satisfies the necessary condition as an optimal choice for K." | lee_mykland_2008.pdf |
| LM 1% threshold | Lee-Mykland 2008 | "Equivalently, β∗ = − log(− log(0.99)) = 4.6001." | lee_mykland_2008.pdf |
| LM constant c | Lee-Mykland 2008 | "c = E|Ui | = 2/ π ≈ 0.7979." [square root dropped] | lee_mykland_2008.pdf |
| LM sampled sparsely to avoid noise | Lee-Mykland 2008 | "With this choice of frequency, results are not greatly affected by the presence of market microstructure noise." | lee_mykland_2008.pdf |
| ASJ statistic limits | Ait-Sahalia-Jacod 2009 | "As the sampling interval tends to 0, our test statistic converges to 1 if there are jumps, and to another deterministic and known value (such as 2) if there are no jumps." | aitsahalia_jacod_2009_jumps.pdf |
| ASJ data show noise | Ait-Sahalia-Jacod 2009 | "we see evidence of market microstructure noise in the form of density mass below 1 (the limit is 1/2, see Section 5.4, if the noise is i.i.d." | aitsahalia_jacod_2009_jumps.pdf |
| ASJ test weakest | Maneesoonthorn et al. | "The ASJ is the least powerful test overall" | maneesoonthorn_jump_tests_which.pdf |
| Noise-robust tests at 5 s | Maneesoonthorn et al. | "If microstructure noise alone is thought to be present, the two tests designed to cater for that feature - LM12 and ASJL - based on very high-frequency (five second) data, are the best choice." | maneesoonthorn_jump_tests_which.pdf |
| Multiple-testing false jumps | Bajgrowicz et al. | "if the jump tests are carried out at the 5% significance level over a one-year period (i.e., 252 trading days) with no single jump, on average more than 12 days are still going to be erroneously selected as containing a jump." | bajgrowicz_scaillet_treccani.pdf |
| Up to 90% spurious | Bajgrowicz et al. | "In Dow Jones stocks between 2006 and 2008, spurious detections can represent up to 90% of the jumps detected initially." | bajgrowicz_scaillet_treccani.pdf |
| Jumps rare, no clustering | Bajgrowicz et al. | "jumps are rare events, they do not cluster in time" | bajgrowicz_scaillet_treccani.pdf |
| Jumps about 1% of QV in tick data | Christensen-Oomen-Podolskij | "we show that jumps account for about 1% of total price variability (i.e., quadratic variation) in contrast to accepted estimates from lower-frequency data, which are an order of magnitude larger." | christensen_oomen_podolskij_fact_friction.pdf |
| Low-frequency jump measures spurious | Christensen-Oomen-Podolskij | "traditional measures of jump variation based on lower-frequency data tend to spuriously assign a burst of volatility to the jump component." | christensen_oomen_podolskij_fact_friction.pdf |
| CME futures tick data used | Christensen-Oomen-Podolskij | "We are grateful to ICAP and the CME for giving permission to use the EBS foreign exchange and CME futures market data in this study." | christensen_oomen_podolskij_fact_friction.pdf |
| Kou model components | Kou 2002 | "N t is a Poisson process with rate , and Vi is a sequence of independent identically distributed (i.i.d.) nonneg-ative random variables such that Y = logV has an asymmetric double exponential distribution" [lambda dropped] | kou_2002.pdf |
| Merton jumps normal | Kou 2002 | "In Merton’s paper Y s are normally distributed." | kou_2002.pdf |
| Kou: option-pricing purpose | Kou 2002 | "the model is simple enough to produce analytical solutions for a variety of option-pricing problems, including call and put options" | kou_2002.pdf |
| Queue-conditional up-move probability | Cont-de Larrard | "the probability φ(n, p) that the next price move is an increase, conditioned on having the n orders on the bid side and p orders on the ask side is:" | cont_delarrard_2013_markov_lob.pdf |
| Volatility from order flow | Cont-de Larrard | "express the volatility of price changes in terms of parameters describing the arrival rates of buy and sell orders and cancelations." | cont_delarrard_2013_markov_lob.pdf |
| Diffusion limit terms | Cont-de Larrard | "where δ is the tick size, D(f ) is given by (9) and W is a standard Brownian motion." | cont_delarrard_2013_markov_lob.pdf |
| eta estimator | Dayri-Rosenbaum | "It is proved in [35] that as the tick value goes to zero, a consistent estimator of η over [0, t] is given by" | dayri_rosenbaum_large_tick.pdf |
| eta small = mean reversion, large tick | Dayri-Rosenbaum | "if η is small, there is a lot of mean reversion in the price and the buy/sell zones are very small: the tick size is very large." | dayri_rosenbaum_large_tick.pdf |
| Implicit spread | Dayri-Rosenbaum | "the quantity 2ηα can be seen as an implicit spread" | dayri_rosenbaum_large_tick.pdf |
| Large-tick definition | Dayri-Rosenbaum | "large tick assets, for which the effective spread is almost always equal to one tick" | dayri_rosenbaum_large_tick.pdf |
| E-mini tick oscillation | Safari-Schmidhuber 2025 | "When the (compounded) underlying market price is in the middle between two ticks, the futures price tends to oscillate between them, leading to a negative auto-correlation of market returns from one minute to the next." | safari_schmidhuber_2025_trends_reversion.pdf |
| Not a profitable strategy | Safari-Schmidhuber 2025 | "This effect can be used to reduce trading costs, but it can hardly be used for a profitable trading strategy." | safari_schmidhuber_2025_trends_reversion.pdf |
| Bounce rule and its risk | Safari-Schmidhuber 2025 | "placing buy orders at the lower price just after an up-tick, and placing sell orders at the higher price just after a down-tick. However, there are trading costs. Moreover, there is the risk that the price does not revert but runs away" | safari_schmidhuber_2025_trends_reversion.pdf |
| Relative latency drives HFT performance | Baron et al. | "differences in relative latency account for large differences in HFTs’ trading performance." | baron_etal_hft_risk_return_wp.pdf |
| Speed helps market making | Baron et al. | "speed is useful for a variety of strategies including market making and cross-market arbitrage." | baron_etal_hft_risk_return_wp.pdf |
| Latency vs fills for takers | Cartea-Jaimungal-Sanchez-Betancourt | "there is no guarantee that MLOs are filled." | cartea_jaimungal_sb_latency.pdf |
| CJP book covers at-the-touch MM and adverse selection | CJP 2015 front matter | "10.2.2 Market Making At-The-Touch" ... "10.4 Market Making with Adverse Selection" | cjp_2015_frontmatter.pdf |
| ASJ book scope | Princeton UP page (Wayback) | "including methods that are robust to market microstructure noise, and address estimation and testing questions involving the jump part of the model." | asj_2014_princeton_wayback.html |
| MBP-10 contents | Databento docs | "MBP-10 (market by price) provides every order book event across the top ten price levels, keyed by price." | databento_mbp10_docs.html |
| Cloud price, A10 box | Lambda pricing | "NVIDIA A10 24 GB 30 226 GiB 1.3 TiB SSD $1.29" | lambda_pricing.html |
| Cloud price, CPU box | Hetzner cloud | "General Purpose Dedicated vCPUs Constantly high CPU usage High-traffic applications starting from max/mo. € 43.49 per month, excl. VAT" | hetzner_cloud.html |
| MES tick, value, commission | repo | `_p("MES", "sp500", MICRO, "0.25", "1.25", "5", 122, admissible=False)` | rules/products.py |

## 13. Failures, gaps and limits (for the lead)

- Core texts not read in full.
  - Shreve II: the Springer page returned a bot challenge, and the Wayback capture was an empty
    JavaScript shell. Both are deleted and logged as failed.
  - Ait-Sahalia-Jacod (2014): book description only.
  - Cartea-Jaimungal-Penalva (2015): front matter and table of contents only.
  - The equations here come from open papers and MIT OCW notes on the same material, not from the
    three books.
- Merton (1976): the NYU copy returned 404, and MIT DSpace returned 429 and then failed. It is described
  via Kou (2002).
- Yu (2012) and Tang-Chen (2009): the SMU repository returned an empty bot page, and the CUHK archive
  and CORE returned challenge pages. The AR(1) bias formula is from memory [unverified] and was checked
  only by my Monte Carlo (E4). It matches well at phi = 0.95 and understates the bias at phi = 0.999.
- Robert-Rosenbaum (2011): HAL served an "are you a bot" page. I did not try Scrapling because the
  needed content was available via Dayri-Rosenbaum.
- The CME MES spec page (Wayback) renders its table in JavaScript, so it was not used. The tick and
  commission come from rules/products.py.
- mit_18s096_lec5.pdf was fetched but not used.
- Not fetched: Roll (1984), Lo-MacKinlay (1988), realised kernels (2008), pre-averaging (2009), LM12. Each
  is marked [unverified] where named.
- Not checked: whether the repo has a macro-release calendar for H-SDE-NEWS.
- All worked examples are synthetic: an illustrative level of 5000, 15% volatility, and an assumed
  fills-per-session range. Real MES 1-s zero-return fractions, update counts per session, fill counts
  and adverse-selection sizes are unknown until the pilot. No market data was read.
- Budget: 15 of 60 WebSearch calls used. No Firecrawl, no Scrapling. No key was read.
- I found no out-of-sample, cost-inclusive evidence that any method in this section makes money for a
  slow 1-lot passive trader. The two directly relevant sources point the other way: Safari-Schmidhuber
  on the E-mini tick bounce, and Baron et al. on latency. The positive value of these methods for the
  program is measurement: eta, TSRV, OU half-lives, jump accounting, and the touch-vs-fill gap.
- Quote check: work/C2_SDE/C2_SDE_checkquotes.py tests every evidence-table quote against the saved
  text (layout and plain pdftotext). 9 of the roughly 60 quotes fail exact string matching, all because
  of PDF typography: fractions, hats, dropped Greek letters, two-column interleaving and line-break
  hyphenation. I read each one by eye in work/C2_SDE/raw/ and confirmed it.
- Written 2026-10-21 02:21 to 02:45 PDT.

## Corrections after review (Stage E.28, MathReviewer G1)

- MG1-01: both Kou quotes (body, evidence table) replaced with the verbatim abstract sentence.
- MG1-02: "(DJIA 2004)" changed to "(DJIA, 2000-2002; September 2004 version)".
- MG1-03: added a bullet after the (41) bullet in E5b naming the (K-1)/n subgrid edge effect, with the 0.981 / 0.984 / 0.964 predictions and the pilot remedy.
- MG1-04: E7 now says 2232 points^2 is the continuous (diffusive) variance and that a jump share s adds s/(1-s) x 2232.
- MG1-05: Theorem 1 now stated for the rescaled price s_{n log(n) t}/sqrt(n), with eq. (13) cited for the per-unit-time sigma.
- MG1-06: uncertainty-zone attribution split into model (Robert-Rosenbaum 2011) and estimator consistency (Robert-Rosenbaum 2012, per Dayri-Rosenbaum ref. [35]); the verbatim quote row in the evidence table is unchanged.
- MG1-08: the 368th byte now described as the DBN record header's length field, marked [unverified].
- MG1-09: "E-mini tick oscillation" reworded to S&P 500 futures with a 0.25 tick (the E-mini grid).
- MG1-10: Kou density citation changed to the unnumbered display after eq. (1); the solution is cited as Kou eq. (3), re-derived.
- Not applied: MG1-07 (needs lead), MG1-11, MG1-12 (style), MG1-13 (review says no change). See reports/stage_e28_briefs/R_fix_G1.md.
