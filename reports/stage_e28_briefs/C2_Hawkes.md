# E.28 methods brief, Part C2: point processes for order arrivals (Poisson, Hawkes, MLE, nonparametric kernels)

Worker: C2_Hawkes (MethodReader, opus high). Written 2026-10-21 PDT, starting 02:21. Pages:
`reports/stage_e28_briefs/pages/C2_Hawkes/` (log: `log.tsv`). Scripts and probe outputs:
`reports/stage_e28_briefs/work/C2_Hawkes/` (`C2_bench.py` with `C2_bench_results.json`, `C2_multi.py` with
`C2_multi_results.json`, `C2_examples.py` with `C2_examples.json`). Every number marked "measured" comes from those
files: synthetic data only, no market data read, nothing registered. N stays 538.

How to read this section. Section 0 sets up the one object everything else uses: the conditional intensity of a
point process and its likelihood. Sections 1 to 9 take each method in turn with the eight items the brief asks for:
(1) idea, (2) equations, (3) data, (4) what it estimates, (5) worked example, (6) pilot hypothesis, (7) compute,
(8) evidence. Section 10 covers software and measured speed, section 11 collects the candidate hypotheses in one
table, section 12 gives verdicts, then references, the evidence table and the gaps log.

Quotes are verbatim from the saved text files (pdftotext output of the saved PDFs, or the de-tagged HTML). pdftotext
mangles some mathematical symbols; where a quote contains mangled symbols I say so and restate the equation in clean
notation next to it.

---

## 0. Foundations: counting processes, intensity, likelihood

**Objects.** A point process on [0, T] is a random set of event times 0 < t_1 < t_2 < ... < t_M <= T. Its counting
process is N(t) = number of events in (0, t]. In the multivariate case each event also has a type
k_m in {1, ..., D} (for example D = 4: buy market order, sell market order, bid-side limit order, ask-side limit
order), and N_i(t) counts type-i events.

**Conditional intensity.** With H_t the history (all event times and types before t),

    lambda_i(t) = lim_{dt -> 0} P( one type-i event in [t, t+dt) | H_t ) / dt.

In words: the instantaneous event rate of type i, given everything that has happened. Every model below is a choice
of how lambda depends on time and on the history. Bacry et al. (2013, eq. 3) write the same definition
(file `bacry_delattre_hoffmann_muzy_2013.txt`, line 240: "λi (t) = lim ∆−1 E [Ni (t + ∆) − Ni (t) | Ft ]").

**Compensator.** Lambda_i(t) = integral_0^t lambda_i(s) ds, the expected number of type-i events up to t given the
path of the intensity. N_i(t) - Lambda_i(t) is a martingale (zero-mean noise).

**Log-likelihood of any point process with an intensity.** For parameters theta,

    log L(theta) = sum_{m=1}^{M} log lambda_{k_m}(t_m | theta)  -  sum_{i=1}^{D} integral_0^T lambda_i(t | theta) dt.

Derivation sketch (assumption: at most one event at a time, intensity left-continuous and positive at events). Cut
[0, T] into small bins of width dt. In a bin with no event the probability is about 1 - lambda dt, whose log is about
-lambda dt; in a bin with a type-k event the probability is about lambda_k dt. Summing logs over bins and dropping the
constant M log dt gives the formula: the first sum rewards the model for putting high intensity where events occurred,
the integral penalises intensity where nothing occurred. Bacry, Mastromatteo and Muzy (2015) state it as their
eq. (70) (file `bacry_mastromatteo_muzy_2015.txt`, line 2106: "The log-likelihood of a non-homogeneous,
multi-dimensional Poisson defined as in Eq. (2) reads", followed by log L(µ, Φ) = − Σ_i ∫_0^T dt λ^i_t + Σ_m log
λ^{k_m}_{t_m}) and credit the MLE for Hawkes processes to Ogata.

**Ties matter for this program.** The formula assumes no two events share a timestamp. CME data have many events in
one matching-engine message (one aggressive order filling many resting orders) (background, reader's knowledge; the pilot will measure the profile). Databento timestamps are in
nanoseconds; `ts_event` is "The matching-engine-received timestamp expressed as the number of nanoseconds since the
UNIX epoch" (`databento_mbo_schema.html.txt`). Any Hawkes fit must first decide how to treat same-timestamp events
(merge one aggressive order's fills into one market-order event; drop or jitter exact ties). Filimonov and Sornette
(2015) list timestamp quality among the main sources of bias (quote in section 8).

---

## 1. Homogeneous Poisson process

**(1) Idea.** Events arrive at a constant rate lambda, independently of the past. It is the "no memory" null model
for order arrivals and the baseline inside every queue model of fill probability (the Cont-Stoikov-Talreja style
models belong to another C2 reader; here only the point-process side).

**(2) Equations.** lambda(t) = lambda (constant). Counts in a window of length tau are Poisson:
P(N(tau) = j) = exp(-lambda tau) (lambda tau)^j / j!, with mean = variance = lambda tau. Gaps between events are
i.i.d. exponential with mean 1/lambda. Log-likelihood: log L = M log lambda - lambda T, maximised at
lambda_hat = M / T, with standard error sqrt(M) / T (from the second derivative -M / lambda^2).

**(3) Data.** Event times of one type. tbbo is enough for trade arrivals (it "provides every trade event alongside
the BBO immediately before the effect of each trade", `databento_tbbo_schema.html.txt`); mbp-10 or mbo for limit-order
and cancel arrivals. One contract for 4 to 12 months is far more than enough for a rate; the issue is that the rate
is not constant (section 2).

**(4) Estimates.** A single rate per event type; under the model, the probability that a queue of Q lots ahead of a
passive order is consumed within tau seconds.

**(5) Worked example (fill probability, measured).** Assume market sells of size 1 hit the bid at lambda = 2 per
second, 20 lots are ahead of our 1-lot bid, and nothing else changes the queue (no cancellations ahead, no level
clearing). We are filled when 21 market-sell lots have arrived: P(fill within tau) = P(N(tau) >= 21).
At tau = 10 s, lambda tau = 20 and P(Poisson(20) >= 21) = 0.441; at tau = 1 s it is 6e-15; at 60 s it is 1.000
(`C2_bench_results.json`, key `fill_prob`). Section 3 repeats this with clustered (Hawkes) arrivals of the same mean.

**(6) Pilot hypothesis.** Not a trading hypothesis on its own. Its job is to be the null in two tests: the
over-dispersion test (H-C2-0 in section 11: variance of counts equals the mean) and the fill-model comparison
(H-C2-3). It adds no configuration to N when used only as a benchmark that is fixed in advance.

**(7) Compute.** Trivial (counting).

**(8) Evidence.** Order flow is not Poisson: it clusters. Bacry, Mastromatteo and Muzy (2015) summarise the
Hardiman-Bouchaud variance estimator with "for a Poisson process, both quantities are equal so that one directly gets
||Φ|| = 0" and report estimated branching ratios far from zero on E-mini data (section 8). The LOB-simulation review
of Jain et al. (2024) names "volatility clustering" as the first improvement of Hawkes over Poisson models
(`arxiv_2402_17359.txt`, line 307: "The major two areas of significant improvement we see in Hawkes Process methods
compared to Poisson methods is first, volatility clustering effect is observed in Hawkes Models and second, the Epps
Effect"). A counterpoint: Lokin and Yu (2026) get usable fill probabilities from queues driven by state-dependent
Poisson flows on FX spot data, while noting the model is "slightly overestimated when the best-bid queue is large"
(`lokin_yu_2026_fillprob.txt`, lines 1766-1768; quoted in section 9).

---

## 2. Inhomogeneous (time-varying) Poisson process

**(1) Idea.** Same independence, but the rate follows a known or estimated clock: lambda(t) = mu(t). On CME index
futures the rate is high at the 06:30 PT cash open and near 13:00 PT, low over lunch and overnight, and jumps at
scheduled news (08:30 ET releases, FOMC) (background, reader's knowledge; the pilot will measure the profile). An inhomogeneous Poisson model with a fixed intraday profile is the honest
baseline that any Hawkes model must beat, because a Hawkes model fitted to data with an unmodelled profile reads the
profile as self-excitation (section 8).

**(2) Equations.** Counts in (a, b] are Poisson with mean integral_a^b mu(t) dt. Log-likelihood
log L = sum_m log mu(t_m) - integral_0^T mu(t) dt. Common estimators: (i) piecewise-constant mu on 5- or 15-minute
bins of the trading day, averaged over days (mu_hat_bin = events in that bin over all days / (days x bin length));
(ii) kernel smoothing of the pooled event times; (iii) a parametric shape (for example a sum of a constant and decaying
bumps after the open and after each scheduled release). Time change: s = Lambda(t) = integral_0^t mu turns the process
into a unit-rate Poisson process in "business time"; that is the time-rescaling idea of section 6. In the Hawkes
literature the same object is the exogenous intensity mu(t): Bacry, Mastromatteo and Muzy (2015), section 2.2.2
"Exogenous non-stationarity", lines 305-308: "The exogenous intensity µ can be generalized to a deterministic
function of time µ(t). This choice allows to model a non-stationary system in which the interaction kernel is indeed
independent of time. In finance, this is the case when one wants to model intra-day seasonalities".

**(3) Data.** Event times (any schema) across many days; the profile needs many days because each bin is averaged
across days. Four months (about 84 trading days) give about 84 observations per bin, enough for a stable profile at
5-minute resolution for frequent events (thousands per bin per day); news-window profiles need more, since there are
only about 4 to 8 high-impact releases a month.

**(4) Estimates.** The intraday activity profile and the news response of each event type; the expected number of
opposite-side market orders in the next tau seconds given only the clock.

**(5) Worked example.** If the market-sell rate is 5 per second in the first second after an 08:30 ET release and
1 per second in the next, the expected count over those 2 s is 5 + 1 = 6 and the chance of no market sell at all is
exp(-6) = 0.0025; with a flat 1-per-second rate it would be exp(-2) = 0.135 (`C2_examples.json`, key `inhom`). For a
queue of 3 lots ahead, P(fill within 2 s) = P(Poisson(6) >= 4) = 1 - (1 + 6 + 18 + 36) e^-6 = 1 - 61 x 0.00248 = 0.849
under the news profile versus P(Poisson(2) >= 4) = 1 - (1 + 2 + 2 + 1.333) e^-2 = 1 - 6.333 x 0.1353 = 0.143 under
the flat rate.

**(6) Pilot hypothesis.** H-C2-0 (section 11) uses it as the null: "after removing a pre-registered intraday profile
(fixed from the pilot's first month), counts of market orders in 10 s windows remain over-dispersed". It also enters
as the baseline in H-C2-1 and H-C2-3. The profile itself must be frozen before any test; if its bin width or smoothing
is chosen by looking at results, each candidate counts in N.

**(7) Compute.** Seconds on the laptop.

**(8) Evidence.** Rambaldi, Pennesi and Lillo (2015) needed an explicit news-driven exogenous term for FX
(`rambaldi_pennesi_lillo_2015.txt`, abstract: "we find that the model is able to capture the increase of trading
activity after the news, both when the news has a sizeable effect on volatility and when this effect is negligible").
Lallouache and Challet (2016) could fit a whole day with two or three exponentials but not two consecutive days; they and
BMM (2015) attribute the limit to intraday non-stationarity of the exogenous intensity (BMM summary,
`bacry_mastromatteo_muzy_2015.txt`, lines 1148-1152: "the intraday seasonality of (mainly) the
exogenous intensity µ does not allow to fit well a whole day"; LC lines 922-923).

---
## 3. Univariate Hawkes process: kernels, branching ratio, stationarity

**(1) Idea.** Each event raises the rate of future events for a while; the rise decays with a kernel phi. Market
orders beget market orders (order splitting, herding, algorithms reacting to each other). The Hawkes process is the
simplest model of this clustering, and it is linear: the intensity is a baseline plus a sum of decaying bumps, one per
past event.

**(2) Equations.**

    lambda(t) = mu + sum_{t_m < t} phi(t - t_m),        phi(s) >= 0 for s > 0, phi(s) = 0 for s <= 0.

- mu > 0: the exogenous (baseline) rate, events per second that arrive "from outside".
- phi: the excitation kernel; phi(s) is the extra rate at lag s after one event.
- n = ||phi|| = integral_0^inf phi(s) ds: the branching ratio, the expected number of direct "children" of one event.

Bacry, Mastromatteo and Muzy (2015) give the general D-dimensional definition as their eq. (2) (file
`bacry_mastromatteo_muzy_2015.txt`, lines 121-131: "A Hawkes process is a counting-process Nt such that the intensity
vector can be written as λit = µi + Σ ∫ dNtj0 φij (t − t0 ), where the quantity µ = {µi } is a vector of exogenous
intensities, and Φ(t) = {φij (t)} is a matrix-valued kernel such that: It is component-wise positive ... causal ...
L1 -integrable"; layout flattened).

*Exponential kernel.* phi(s) = n beta exp(-beta s). beta (per second) sets the decay speed: an event's influence
halves every ln 2 / beta seconds; n is the integral. BMM eq. (6) uses the same parametrisation, alpha beta e^{-beta t}
(lines 214-217), and state the bivariate stability condition alpha^(s) + alpha^(c) < 1 as eq. (7). The exponential
kernel makes (N, lambda) Markov: between events lambda decays as d lambda = -beta (lambda - mu) dt and jumps by
n beta at each event (BMM Proposition 2, eq. (8), which omits the µ term: "dλt = −βλt dt + αβ dNt"). This is what
makes the O(N) likelihood (section 5) and exact simulation possible.

*Power-law kernel.* phi(s) = alpha beta / (1 + beta s)^{1 + gamma} (BMM eq. (9), "regularized power-law"). Its integral
is alpha beta x 1 / (beta gamma) = alpha / gamma, so stationarity needs alpha < gamma (BMM eq. (10), lines 270-274:
"The stationarity condition in is met for α<γ, indicating that the tail exponent γ of a power law-kernel should be
positive for the increments of the process to be stationary"). Long memory: the influence of an event decays like
s^{-(1+gamma)}, so events minutes ago still matter. Hardiman, Bercot and Bouchaud (2013) approximate a power law by a
sum of exponentials with power-law weights plus a short-lag cut-off so that the O(N) recursion still applies (their
eqs. (12)-(13); quoted in section 5).

*Stationarity and the mean rate.* If n < 1 the process has stationary increments and the mean rate is

    Lambda = mu / (1 - n).

Derivation: take expectations of the intensity equation in the stationary state:
Lambda = mu + integral phi(s) Lambda ds = mu + n Lambda. In D dimensions the condition is that the matrix of kernel
integrals ||Phi|| has spectral radius below 1 (BMM Proposition 1, lines 183-187: "The process Nt has asymptotically
stationary increments and λt is asymptotically stationary if the kernel satisfies the assumption, also referred to as
the stability condition: (H) The matrix ||Φ|| = {||φij ||} [D, i,j=1] has spectral radius smaller than 1"), and the mean rate
vector is Lambda = (I - ||Phi||)^{-1} mu, which equals BMM eq. (21), Λ = (I + Ψ̂(0))µ, since I + Ψ̂(0) =
(I - Φ̂(0))^{-1} by their eq. (20).

*Cluster (branching) representation.* Exogenous "immigrants" arrive as Poisson(mu); each event independently has
Poisson(n) children whose delays are drawn from phi / n; children have children, and so on. This maps onto a
Galton-Watson tree: BMM lines 992-1000: "it is possible to map the branching structure of the Hawkes process described
above onto the one of a Galton-Watson tree with average offspring ||Φ||. ... The three phases of the Hawkes process
(stationary ||Φ|| < 1, non-stationary ||Φ|| > 1 and quasi-stationary ||Φ|| = 1) correspond then to the three phases
of a Galton-Watson branching process". Consequences: mean cluster size 1 / (1 - n); the fraction of events that are
endogenous (have a parent) is n. BMM (lines 1190-1200) use this to read n as "a direct measure of the fraction of
endogenous events within the whole population of mid-price changes".

*Counts are over-dispersed.* For a window W much longer than the kernel's memory, Var[N(W)] / E[N(W)] -> 1 / (1 - n)^2
(Hardiman and Bouchaud 2014, their eq. (4) gives the integral of the autocovariance as Lambda / (1 - n)^2, so Var[N(W)] / E[N(W)] -> 1 / (1 - n)^2; file
`hardiman_bouchaud_2014_branching.txt`, line 114, symbols mangled). That gives the moment estimator of section 7.

**(3) Data.** Event times of one type: trades (tbbo suffices: the `side` field marks "A sk for a sell aggressor in a
trade, B id for a buy aggressor", `databento_tbbo_schema.html.txt`), mid-price changes (mbp-1 or mbp-10), or any one
book-event type (mbp-10 or mbo). A month of one liquid contract already has hundreds of thousands to millions of
events (the exact count for MES is not known to me and must be measured on the pilot; [unverified]). For a kernel
with memory of seconds, one trading day is already a large sample; the binding problem is non-stationarity across the
day, not sample size (section 6 evidence).

**(4) Estimates.** mu, n and the kernel shape (decay time 1/beta, or the power-law exponent); the predicted rate
lambda(t | history), which is a forecast of the next-seconds event rate.

**(5) Worked example (measured).** (a) Mean rate and endogeneity: mu = 0.5 per s, n = 0.8 gives Lambda =
0.5 / 0.2 = 2.5 events per s; 80 % of events are endogenous; clusters average 1 / 0.2 = 5 events. A simulation of
200,000 s with beta = 1 per s produced 502,398 events, an empirical rate of 2.512 per s against 2.5 in theory
(`C2_bench_results.json`, `hb_estimator`).

(b) Same mean, different fill risk. Re-run the section 1 fill example with Hawkes market sells of the same mean rate
2 per s (n = 0.7, beta = 1 per s, so mu = 2 x 0.3 = 0.6 per s), 20 lots ahead, starting at random times in a long
stationary simulation (797,653 events, 20,000 start times):

| window | P(fill), Poisson | P(fill), Hawkes | mean count, Hawkes | variance of count, Hawkes (Poisson: = mean) |
|---|---|---|---|---|
| 1 s | 6e-15 | 0.000 | 2.00 | 4.67 |
| 10 s | 0.441 | 0.392 | 19.97 | 156.7 |
| 60 s | 1.000 | 1.000 | 119.5 | 1265 |

With the same mean, clustering spreads the count: in 10 s the variance is 7.8 times the Poisson value. The fill
probability at 10 s drops from 0.44 to 0.39 and, more important for a passive trader, fills come in bursts: when the
queue does get eaten it is usually inside a burst of one-sided market orders, which is the adverse-selection setting
(Cartea, Jaimungal and Ricci, section 9). The theory check: for W >> 1/beta, Var/mean -> 1/(1 - 0.7)^2 = 11.1; at
60 s the measured ratio is 1265 / 119.5 = 10.6, close to the limit; at 10 s it is 7.8 because the window is only 10
kernel time constants.

**(6) Pilot hypothesis.** H-C2-0 and H-C2-1 in section 11 (over-dispersion after deseasonalising; out-of-sample
intensity forecast beats the seasonal Poisson baseline). The univariate model is the building block; trading use comes
through the bivariate buy/sell version (section 4) and markout conditioning (H-C2-2).

**(7) Compute.** One exponential-kernel likelihood evaluation over 1,000,000 events took 0.71 s in plain Python on the
laptop; a full three-parameter MLE on 100,220 events took 9.5 s (`C2_bench_results.json`, `speed_python`). A day of
MES market orders is a laptop job. No GPU.

**(8) Evidence.** Clustering is not in doubt; its size and shape are. On E-mini S&P mid-price changes, Hardiman,
Bercot and Bouchaud (2013) find a power-law kernel (`hardiman_bercot_bouchaud_2013.txt`, lines 7-10: "We model the
arrival of mid-price changes in the E-Mini S&P futures contract as a self-exciting Hawkes process. Using several
estimation methods, we find that the Hawkes kernel is power-law with a decay exponent close to −1.15 at short times,
less than ≈ 103 seconds [10^3 s], and crosses over to a second power-law regime with a larger decay exponent ≈ −1.45
for longer times scales"). BMM's Figure 6 caption (lines 1123-1126) says the E-mini kernel and the EuroStoxx trade
kernel "is almost identical" in shape across markets and years, and they conclude (lines 1137-1139) that "the
power-law nature of Hawkes kernels remains a solid empirical fact which, at least, calls to question all the approaches
based on exponential Hawkes models". Lallouache and Challet (2016) on FX: significance is reachable only for short
windows (section 6). None of this is a trading result.

---
## 4. Multivariate Hawkes for order-book events (buy and sell market orders, limit orders, cancels, price moves)

**(1) Idea.** Give each event type its own intensity and let every type excite every other type through its own
kernel. The matrix of kernel integrals is a map of "who triggers whom, how strongly, how fast": a market buy that
eats the ask triggers new ask limit orders (refill, i.e. resiliency), more market buys (splitting), and an up-tick of
the mid; an up-tick triggers sell-side activity (mean reversion). This is the natural model for the events that
decide whether and when a passive 1-lot order fills and what happens to the price afterwards.

**(2) Equations.**

    lambda_i(t) = mu_i + sum_{j=1}^{D} sum_{t_m < t, k_m = j} phi_ij(t - t_m),    i = 1..D.

- phi_ij: effect of a type-j event on the type-i rate (i = target, j = source).
- ||Phi|| = matrix of n_ij = integral phi_ij; stationarity needs spectral radius(||Phi||) < 1; mean rates
  Lambda = (I - ||Phi||)^{-1} mu (section 3).
- Exponential case: phi_ij(s) = n_ij beta_ij exp(-beta_ij s). With one shared beta there are D + D^2 + 1 parameters
  (D = 4 gives 21).

*Bivariate buy/sell market orders* (D = 2, symmetric): n_ii = a_s (self), n_ij = a_c (cross). The eigenvalues of
[[a_s, a_c], [a_c, a_s]] are a_s + a_c and a_s - a_c, so stationarity is a_s + a_c < 1, BMM eq. (7) ("α(s) + α(c) < 1").

*Resiliency response (Large 2007).* BMM eq. (66) restate Large's response function: G_ij(t) dt = E[dN_i(t) | F_0,
dN_j(0) = 1] - E[dN_i(t) | F_0], the extra type-i activity at lag t caused, directly or through cascades, by one
type-j event at 0. For a Hawkes process G = Psi = Phi + Phi*Phi + Phi*Phi*Phi + ... (BMM eqs. (17)-(18), lines 410-415;
"*" is convolution). The integral of Psi_ij is the total number of type-i events, children plus all later generations,
that one type-j event causes: ||Psi|| = (I - ||Phi||)^{-1} - I.

*Price model with mutually exciting up and down moves (Bacry, Delattre, Hoffmann and Muzy 2013).* Let N_1 count
up-ticks and N_2 down-ticks of the mid, X(t) = N_1(t) - N_2(t) the price in ticks. Mean reversion is modelled by
cross-excitation only (file `bacry_delattre_hoffmann_muzy_2013.txt`, eqs. (6)-(7), lines 262-270:
"λ1 (t) = µ + ∫ ϕ(t − s)dN2 (s)", "λ2 (t) = µ + ∫ ϕ(t − s)dN1 (s)"; symbols restored: ∫), with phi(t) = a e^{-b t} and ||phi|| = a / b < 1
(their eqs. (8)-(9); note their phi has no factor b, unlike section 3). Their Proposition 2.1 gives the signature plot
(variance per unit time of price changes over horizon tau) in closed form (lines 302-312, symbols partly mangled):

    C(tau) = Lambda ( kappa^2 + (1 - kappa^2) (1 - e^{-gamma tau}) / (gamma tau) ),
    Lambda = 2 mu / (1 - ||phi||),   kappa = 1 / (1 + ||phi||),   gamma = a + b.

C(0) = Lambda (tick-level variance, all moves count) falls to C(inf) = Lambda kappa^2 (diffusive variance: part of
each move is undone). This is a direct model of the "bounce" a passive fill sees in its 1 and 10 s markouts.

*State-dependent extensions.* The pure Hawkes intensity ignores the book. Bacry, Jaisson and Muzy (2016) say so in
their conclusion (`arxiv_1412_7096.txt`, lines 1098-1101: "One thing that probably lacks in our purely Hawkes order
book model is that the arrival of events does not directly depend on the state of the order book but only on the past
events. For example, it is not clear that in our model, when the spread is important, liquidity will arrive.").
Morariu-Patrichi and Pakkanen (2022) let the kernels depend on a state (spread, queue imbalance) that switches at
events; Muni Toke and Yoshida (2020) and Sfendourakis and Muni Toke (2021) multiply a Hawkes-type intensity by
exp(theta' X(t)) with book covariates X (imbalance, spread). The Toke-Yoshida "ratio" form, quoted with mangled layout
(`toke_yoshida_2020.txt`, lines 943-951): λ^{i,k_i}_R(t) = λ_{0,R}(t) exp(Σ_j ϑ^{i,k_i}_j X_j(t)), "with some unobserved
baseline intensity λ_{0,R}(t)"; the baseline cancels when one predicts which type comes next, so only ratios are
estimated.

**(3) Data.**
- Buy/sell market orders only: tbbo is enough (aggressor side on every trade). One aggressive order that fills
  several resting orders should be merged into one event (same ts_event and side).
- Mid-price up/down moves (Bacry et al. 2013 model): mbp-1 or mbp-10 (or tbbo if only trade-driven moves are wanted).
- Limit orders and cancels at the best levels (Large's 10-D, Bacry-Jaisson-Muzy's 8-D models): mbp-10 records each
  event with an action ("A dd, C ancel, M odify, clea R book, or T rade") and the book level `depth`
  (`databento_mbp10_schema.html.txt`), which supports a level-I event classification. Separating a cancel from a
  modify that loses queue priority, and tracking one order's queue position, needs mbo ("keyed by its order ID. This
  allows you to determine the queue position of each order", `databento_mbo_schema.html.txt`).
- Sample: 4 months of one contract is ample for D = 4 to 8 with exponential kernels if fitted day by day (each day
  is already 10^5 to 10^6 events for a liquid contract; [unverified] for MES until the pilot counts it). Kernels
  depending on a state variable need enough events in each state; rare states (wide spread on MES) may have too few.

**(4) Estimates.** The excitation matrix (who triggers whom), decay times, exogenous rates, the endogeneity of each
event type, resiliency (how fast a depleted best level refills after a market order), and at every instant the
intensities of the next market buy and sell, i.e. a short-horizon forecast of one-sided pressure.

**(5) Worked example.** (a) Stationarity: a_s = 0.5, a_c = 0.2 gives eigenvalues 0.7 and 0.3 (< 1, stationary); with
mu = (0.3, 0.3) per s, Lambda = (I - A)^{-1} mu = (1.0, 1.0) per s (`C2_examples.json`, `bivariate`): each side's
observed rate is 3.3 times its exogenous rate.

(b) Signature plot (Bacry et al. 2013 formula, illustrative parameters mu = 0.2 per s, ||phi|| = 0.6, b = 2 per s,
so a = 1.2, gamma = 3.2): Lambda = 2 x 0.2 / 0.4 = 1.0 tick^2 per s, kappa = 1 / 1.6 = 0.625,
C(inf) = 1.0 x 0.625^2 = 0.391. At tau = 1 s: (1 - e^{-3.2}) / 3.2 = 0.9592 / 3.2 = 0.2998, so
C(1 s) = 0.391 + (1 - 0.391) x 0.2998 = 0.573; C(0.1 s) = 0.912, C(10 s) = 0.410, C(60 s) = 0.394
(`C2_examples.json`, `signature`). Reading: over 10 s the realised variance is only 41 % of what counting every tick
would suggest, because up-moves trigger down-moves within about 1 / gamma = 0.3 s. For a passive order filled on an
up-move against it, part of the adverse move is expected to reverse within a second.

(c) Response totals: with ||Phi|| = [[0.5, 0.2], [0.2, 0.5]], ||Psi|| = (I - ||Phi||)^{-1} - I: (I - A)^{-1} =
(1 / 0.21) [[0.5, 0.2], [0.2, 0.5]] = [[2.381, 0.952], [0.952, 2.381]], so one exogenous market buy causes on average
1.381 further buys and 0.952 sells.

**(6) Pilot hypotheses.** H-C2-2 (markouts conditioned on the bivariate buy/sell intensity at fill time) and H-C2-3
(Hawkes-driven fill model) in section 11 are the two that touch the pilot's fill and markout measurements directly.
A third, H-C2-5, uses the Bacry et al. (2013) model: "the up/down mutually exciting model, fitted on day d-1, predicts
the sign and size of the mean 1 s and 10 s mid reversion after a passive fill on day d better than a zero-reversion
benchmark", statistic: mean squared markout forecast error difference, day-level DM-type t; 2 horizons x 1 model =
2 configurations. Each needs only mbp-1-level information; queue position (H-C2-3) is better with mbo.

**(7) Compute (measured on the laptop, synthetic 4-D data).** One evaluation of a 4-D, 21-parameter exponential
log-likelihood took 0.27 s on 100,386 events and 2.95 s on 999,087 events in plain Python (`C2_multi_results.json`).
A full MLE with numerical gradients needs about 22 evaluations per gradient step; at about 100 steps that is about
2,200 evaluations, i.e. 1.8 hours per million-event fit in plain Python (extrapolation, not measured). Analytic
gradients computed in the same pass, or a compiled loop (numba, C++), cut this to minutes [unverified speed-up
factor; numba is not installed in the project]. Per-day fits (which non-stationarity requires anyway) keep each fit
at 10^5 to 10^6 events. Memory is not a constraint (16 bytes per event: 100 million events = 1.6 GB, process by day).
No GPU needed. A cloud machine is unnecessary; if wanted, Lambda's 1x A10 instance (30 vCPUs, 226 GiB RAM) lists at
$1.29 per GPU-hour (`lambda_pricing.html.txt`), so a 10-hour batch of parallel daily fits would cost about $13.

**(8) Evidence.**
- Large (2007), as summarised by BMM (lines 1588-1607; primary paper paywalled, not read): LSE Barclays data at 1 s
  resolution for January 2002, a 10-D Hawkes model, "He mainly found that aggressive limit orders are principally
  caused by aggressive market orders ... Large estimated that the studied stock value is resilient less than 40 % of
  cases and, when it is the case, the book replenishment occurs within a time frame of around 20s."
- Muni Toke (2011): "after a market order, a limit order is likely to be submitted more quickly than it would have
  been without the market order ... We also show that the reciprocal effect is not observed on the studied markets"
  (`toke_2011_marketmaking.txt`, lines 163-169), verified on "equity, bond futures, index futures" (lines 20-21).
- Bacry, Jaisson and Muzy (2016), DAX and Bund futures June 2013 to June 2014, 8-D level-I model
  (`arxiv_1412_7096.txt`, lines 1081-1086): "Fast and localized influences, for which the volume of the kernel is
  localized around the reaction time of the market (on our data 0.3 milliseconds) and influences which are spread over
  a wide range of time scales"; and (lines 1093-1095) "market orders are more exogenous than limit and cancel orders".
  The 0.3 ms figure matters here: BJM find one of the two kinds of influence (the fast, localized kind, which is how market
  orders act) concentrated at about 0.3 ms, faster than this program can react (tens of ms from Vancouver); the other kind is
  spread over a wide range of time scales.
- Lallouache and Challet (2016), FX: "Using multivariate Hawkes process to fit the arrival and the reciprocal
  influence of buy and sell trades systematically yields null cross-terms" (`lallouache_challet_2016.txt`, lines
  171-172).
- Rambaldi, Bacry and Lillo (2017), Eurex Bund and DAX futures: models that ignore order size fail ("simple models
  assuming the independence between volume and time are not suitable to describe the data",
  `rambaldi_bacry_lillo_2017.txt`, abstract).
- Morariu-Patrichi and Pakkanen (2022): "excitation effects in the order flow are strongly state-dependent"
  (`morariu_pakkanen_2022.txt`, abstract).
- Martins and Hendricks (2016), JSE LOB data: fit quality "improves as the number of exponentials is increased, with a
  sum-of-three-exponentials yielding the best fit" (`arxiv_1604_01824_multivar_signif.txt`, abstract).
- Lu and Abergel (2018) report inhibition effects (negative influences) that linear Hawkes cannot represent:
  [unverified, search snippet only; the HAL copy returned a bot check].
- Bacry et al. (2013) fit the price model to Euro-Bund and Euro-Bobl futures ("consistent with empirical fits on
  futures Euro-Bund and Euro-Bobl in several situations", abstract). This is a fit of the signature plot, not a
  forecast test.

---
## 5. Maximum-likelihood estimation and the O(N) recursion for exponential kernels

**(1) Idea.** Write the probability of the observed event sequence as a function of the parameters (section 0) and
maximise it. For general kernels each intensity value needs a sum over all past events, so one likelihood evaluation
costs O(N^2). For exponential kernels the sum can be carried forward event by event, so it costs O(N), which is why
exponential and sum-of-exponential kernels dominate practice.

**(2) Equations (univariate, phi(s) = n beta e^{-beta s}, observation window [0, T]).**

Intensity at the i-th event: lambda(t_i) = mu + n beta A_i, where A_i = sum_{j < i} exp(-beta (t_i - t_j)).

Recursion: A_1 = 0, and A_i = exp(-beta (t_i - t_{i-1})) (1 + A_{i-1}). Proof: every term of A_{i-1} and the new
event at t_{i-1} (the "1") are all discounted by the same factor exp(-beta (t_i - t_{i-1})).

Compensator: integral_0^T lambda(t) dt = mu T + sum_i n (1 - exp(-beta (T - t_i))), because each event adds
integral_0^{T - t_i} n beta e^{-beta s} ds = n (1 - e^{-beta (T - t_i)}).

Log-likelihood:

    log L(mu, n, beta) = sum_{i=1}^{N} log( mu + n beta A_i )  -  mu T  -  n sum_{i=1}^{N} (1 - e^{-beta (T - t_i)}).

Martins and Hendricks (2016) write the same structure for a sum of exponentials with the recursion credited to
Ozaki (1979) (`arxiv_1604_01824_multivar_signif.txt`, lines 574-580, layout mangled: "Using the following recursive
relationships Ozaki (1979) ... R1,i (j) = e^{−(tj −tj−1)/τ1,i} (1 + R1,i (j − 1))"). Lallouache and Challet (2016)
state the complexity gain (`lallouache_challet_2016.txt`, lines 163-164: "When a kernel is a sum of exponentials, one
can exploit a recursive relation for the log-likelihood calculation that reduces the computational complexity from
O(N 2 ) to O(N ) (see Ozaki [37])"). BMM (lines 2122-2126): "In the case of a general Hawkes process, the computation
of the likelihood (or its gradient) is of the order of O(M 2 D) where M is the total number of jumps. The fact that it
reduces to O(M D) when the kernels are exponential functions is one of the major reasons why exponential kernels (or
sum of exponential kernels) are so commonly used".

Note a disagreement: Martins and Hendricks (lines 623-626) say the O(N) advantage "does not translate to the
multivariate case". BMM's O(M D) statement and the implementation in `C2_multi.py` (one D-vector of decayed counts
carried forward, D x D work per event) show that it does; with distinct decays per pair the recursion keeps D^2 accumulators and stays linear in N. I follow BMM.

*Multivariate form used in `C2_multi.py`.* With one beta: R_j(t) = sum over past type-j events of e^{-beta (t - t_m)};
lambda_k(t_m) = mu_k + beta sum_j n_kj R_j(t_m^-); log L = sum_m log lambda_{k_m}(t_m) - T sum_k mu_k -
sum_m (sum_k n_{k, k_m}) (1 - e^{-beta (T - t_m)}).

*Power laws inside the recursion.* Hardiman, Bercot and Bouchaud (2013) build a power law from exponentials
(`hardiman_bercot_bouchaud_2013.txt`, lines 177-190, layout mangled): phi(tau) = (n / Z) [ sum_{i=0}^{M-1}
xi_i^{-(1+eps)} e^{-tau / xi_i} - S e^{-tau / xi_{-1}} ], scales xi_i = tau_0 m^i, "The parameter Z is chosen such that
∫0∞ φ(τ )dτ = n and S such that φ(0) = 0 ... we have chosen m = 5 and M = 15". Footnote 1 of the same paper: "By
approximating with a sum of exponentials we can take advantage of a recurrence relation which reduces the time
complexity of the log-likelihood calculation in Eq. (14) from O(N 2 ) to O(N )".

*Optimiser practice.* Parameters are constrained (mu > 0, beta > 0, 0 <= n < 1); a log transform for mu and beta and
a logit for n make the problem unconstrained (as in `C2_bench.py`). The surface can be multi-modal in beta, so use
several starts: Lallouache and Challet: "we use the L-BFGS-B algorithm [10] ... For each fit we try different starting
points to avoid local maxima" (lines 169-170). Standard errors come from the inverse of the observed information
(negative Hessian of log L at the maximum); the asymptotic normality result for Hawkes MLE is due to Ogata (1978)
[unverified: not fetched; cited from memory of the literature and by BMM only as "first introduced by Ogata"].

*Alternatives.* EM using the branching structure (BMM lines 2130-2146: E-step "the probability pmm0 that ... tm is an
ancestor of tm0", M-step parameters from these probabilities; fast when few events fall within one kernel width,
slow for long-memory kernels); method of moments (BMM line 2146); penalised convex MLE with fixed decays for large D
(BMM lines 2155-2170: "in order to get a convex log-likelihood (70), the parameters β ij are a priori fixed ... an L1
penalization that ensures sparsity and a trace-norm penalization that ensures low-rank").

**(3) Data.** Any event-time data; the recursion needs events sorted in time with ties resolved.

**(4) Estimates.** Point estimates and standard errors of mu, n (or the matrix n_ij), decay rates; the maximised
log-likelihood for model comparison (likelihood ratio between nested kernels; AIC or BIC across kernel families;
out-of-sample log-likelihood for forecast comparison, H-C2-1).

**(5) Worked example (hand, checked by code).** Four events at t = (0.5, 1.0, 1.2, 3.0) s, window T = 4 s,
mu = 0.5 per s, n = 0.6, beta = 2 per s (so n beta = 1.2).

| i | t_i | A_i (recursion) | lambda(t_i) = 0.5 + 1.2 A_i | log lambda |
|---|---|---|---|---|
| 1 | 0.5 | 0 | 0.5000 | -0.6931 |
| 2 | 1.0 | e^{-1.0} (1 + 0) = 0.3679 | 0.9415 | -0.0603 |
| 3 | 1.2 | e^{-0.4} (1 + 0.3679) = 0.6703 x 1.3679 = 0.9169 | 1.6003 | 0.4702 |
| 4 | 3.0 | e^{-3.6} (1 + 0.9169) = 0.02732 x 1.9169 = 0.0524 | 0.5629 | -0.5747 |

Sum of log lambda = -0.8579. Compensator: mu T = 2.0; kernel terms 0.6 (1 - e^{-2 x 3.5}) = 0.5995,
0.6 (1 - e^{-6}) = 0.5985, 0.6 (1 - e^{-5.6}) = 0.5978, 0.6 (1 - e^{-2}) = 0.5188; total 2.0 + 2.3146 = 4.3145.
log L = -0.8579 - 4.3145 = -5.1724. The code gives -5.172567 with both the recursion and the O(N^2) double sum
(`C2_bench_results.json`, `hand`).

**Measured recursion versus naive sum (plain Python/numpy, laptop).**

| events N | naive O(N^2) | recursion O(N) | agreement |
|---|---|---|---|
| 2,000 | 0.065 s | 0.0015 s | 4.5e-13 |
| 5,000 | 0.755 s | 0.0036 s | 0 |
| 10,000 | 2.45 s (and about 2.4 GB RAM for the N x N matrix) | 0.0072 s | 1.8e-12 |
| 100,000 | not run | 0.071 s | |
| 1,000,000 | not run | 0.71 s | |

Parameter recovery: a simulated path with (mu, n, beta) = (0.5, 0.6, 2.0) and 100,220 events was fitted to
(0.498, 0.602, 1.980) in 9.5 s with three starts (`speed_python.full_mle_python`).

**(6) Pilot hypothesis.** MLE is the estimator inside H-C2-1, H-C2-2, H-C2-3 and H-C2-5. Every free modelling choice
(kernel family, number of exponentials, fixed or fitted decays, which event types, fit window: one day, one week)
changes the fitted intensities and so is a configuration. To keep N small, pre-register one specification: for
example a bivariate buy/sell market-order model, sum of three exponentials with fixed decays 1/beta = 0.1, 1 and 10 s,
seasonal baseline from the frozen profile, refitted each day on the previous day only.

**(7) Compute.** As measured above: univariate and low-dimensional fits on a day of data take seconds to minutes on
the laptop; no GPU. The only expensive case is full numerical-gradient MLE of D >= 4 models on many millions of
events in plain Python (hours); fix it with analytic gradients or a compiled loop, not with hardware.

**(8) Evidence.** MLE is standard and consistent for a correctly specified stationary model (the control fit above
recovers the truth). The failures in the literature come from misspecification, not from the estimator:
Filimonov and Sornette (2015) report "(iv) the need for an exhaustive search of the absolute maximum of the
log-likelihood function due to its complicated shape" and upward bias in n from regime shifts and outliers
(`filimonov_sornette_2015_apparent.txt`, abstract; section 8 here).

---
## 6. Goodness of fit: the time-rescaling theorem and residual tests

**(1) Idea.** If the model's intensity is right, then measuring time in units of "expected number of events"
turns any point process into a plain unit-rate Poisson process. So transform the observed gaps with the fitted
compensator and test whether the transformed gaps look like i.i.d. Exponential(1). This is the standard residual
check for every model in this section.

**(2) Equations.** Theorem (Brown, Barbieri, Ventura, Kass and Frank 2002, statement in `brown_etal_2002_rescaling.txt`,
lines 219-226; the PDF's Greek letters are mangled, l = lambda and L = Lambda; symbols restored: ∈, =, ∫ and the "fi" ligature in "Define"): "Let 0 < u1 < u2 < , . . . , < un < T
be a realization from a point process with a conditional intensity function l(t | Ht ) satisfying 0 < l(t | Ht ) for
all t ∈ (0, T]. Define the transformation L ( uk ) = ∫0^uk l(u | Hu ) du ... Then the L ( u k ) ’s are a Poisson
process with unit rate." In clean notation:

    tau_k = Lambda(t_k) - Lambda(t_{k-1}) = integral_{t_{k-1}}^{t_k} lambda(s | H_s) ds  ~  i.i.d. Exp(1),
    z_k = 1 - exp(-tau_k)  ~  i.i.d. Uniform(0, 1).

(Brown et al. eqs. (2.16)-(2.17), lines 314-326.) Derivation sketch: the probability of no event in (t_{k-1}, t_k)
given the history is exp(-tau_k), so P(tau_k > x) = e^{-x}; the conditioning on the past at each step makes the
tau_k independent. Assumptions: the intensity is the true conditional intensity, strictly positive, and events do not
coincide.

For the exponential Hawkes kernel the increments have a closed form: with D_k = t_k - t_{k-1} and
B_{k-1} = sum_{j <= k-1} e^{-beta (t_{k-1} - t_j)} = 1 + A_{k-1},

    tau_k = mu D_k + n B_{k-1} (1 - e^{-beta D_k}).

Tests on the tau_k (Lallouache and Challet 2016, `lallouache_challet_2016.txt`, lines 176-213):
- Kolmogorov-Smirnov against Exp(1) (or the z_k against Uniform). Brown et al. give the KS-plot bands
  (lines 337-340): "For moderate to large sample sizes the 95% (99%) confidence bounds are well approximated as
  bk ± 1.36 / n1/2 (bk ± 1.63 / n1/2)" (ligature restored: "confidence"). Lallouache and Challet call it "a very (even excessively) demanding test".
- Ljung-Box on the tau_k for independence: Q = N (N + 2) sum_k rho_k^2 / (N - k), chi-square under the null; they
  start at lag 2 because their data cleaning induces a lag-1 artefact.
- Engle-Russell excess dispersion: S = sqrt(N) (sigma_hat^2 - 1) / sqrt(8), asymptotically N(0, 1), where
  sigma_hat^2 is the sample variance of the tau_k.
Their key remark (lines 180-184): "The maximum-likelihood estimation, by construction, tends to maximize the
exponential nature of the θs, but not their independence. This explains why QQ-plots of the resulting θs are visually
very satisfying as long as the kernel contains than more one exponential."

**(3) Data.** Same as the fitted model; ties must be resolved first (a zero gap gives tau_k close to 0 and breaks the
test). Coarse timestamps distort the KS test (Lallouache and Challet, lines 920-922: "only the KS test is affected by
introduction of limited time resolution"). Databento's nanosecond ts_event is fine in resolution; the remaining issue
is genuinely simultaneous events within one matching-engine message.

**(4) Estimates/decides.** Whether a fitted intensity is adequate on held-out data; which kernel family survives.

**(5) Worked example.** For the four-event example of section 5: tau_1 = mu t_1 = 0.25; tau_2 = 0.5 x 0.5 +
0.6 x 1 x (1 - e^{-1}) = 0.25 + 0.3793 = 0.6293; tau_3 = 0.5 x 0.2 + 0.6 x 1.3679 x (1 - e^{-0.4}) = 0.1 + 0.2706 =
0.3706; tau_4 = 0.5 x 1.8 + 0.6 x 1.9169 x (1 - e^{-3.6}) = 0.9 + 1.1187 = 2.0187. z = (0.221, 0.467, 0.310, 0.867)
(`C2_bench_results.json`, `hand`). With n = 4 the KS band is plus or minus 1.36 / 2 = 0.68: four points can never
reject anything, which is the practical lesson: GOF needs thousands of events per test window.

**Measured cautionary result.** A pure Poisson process whose rate is drawn afresh from {0.3, 3.0} per s for each 300 s segment
(true branching ratio 0; 30,335 events over 20,000 s) was fitted with an exponential Hawkes model by MLE. The fit
returned n_hat = 0.956, beta_hat = 0.102 per s, mu_hat = 0.067 per s, and it **passed** the time-rescaling KS test
(KS statistic 0.0049, p = 0.45; mean of tau 1.000, variance 1.032, lag-1 autocorrelation 0.017). A correctly
specified control (true n = 0.6, beta = 2) was fitted to n_hat = 0.593, beta_hat = 1.988, KS p = 0.68
(`C2_bench_results.json`, `spurious`). So a passing residual test does not certify that the excitation is real: slow
regime changes and true self-excitation can be indistinguishable by these tests. This reproduces in miniature the
Filimonov and Sornette (2015) point (section 8).

**(6) Pilot hypothesis.** Use GOF as a pre-registered adequacy gate rather than as a hypothesis: "the day-(d-1) model
is considered adequate on day d if KS and Ljung-Box (lags 2 to 21) on its tau_k do not reject at 1 %; a model family
proceeds to H-C2-1 to H-C2-3 only if it is adequate on at least 50 % of evaluation days" (the 50 % threshold is an
example; the lead sets it). A gate fixed in advance adds no configuration; trying several gates and keeping the one
that passes would.

**(7) Compute.** One O(N) pass after the fit; negligible.

**(8) Evidence.** Lallouache and Challet (2016), EBS FX, abstract: "Many fits of Hawkes processes to financial data
look rather good but most of them are not statistically significant ... One can achieve statistical significance
according to three simultaneous tests provided that one uses kernels with two exponentials for fitting an hour at a
time, and two or three exponentials for full days, while longer periods could not be fitted within statistical
satisfaction because of the non-stationarity of the endogenous process. Fitted timescales are relatively short and
endogeneity factor is high but sub-critical at about 0.8." Their conclusion (lines 902-904): "they describe very
precisely a large number of events (around on average 15000)" per day, while two consecutive days fail the LB test
(lines 922-923). For a 1-lot strategy this means: refit daily, and do not expect a single kernel to hold for months.

---
## 7. Nonparametric kernel estimation

**(1) Idea.** Do not assume the kernel's shape (exponential, power law); estimate phi_ij(t) on a grid, or only its
integral n_ij, directly from the data. Use it to decide which parametric family is defensible, and to see on what
time scales the excitation lives (which matters for a strategy with tens of ms of latency).

**(2) Methods and equations.**

*(a) Nonparametric EM.* BMM (lines 2181-2196): the E-step estimates the probability that event m is the parent of
event m'; the M-step re-estimates phi on a grid and mu from those probabilities. Two drawbacks quoted there: "The
convergence speed of the EM algorithm drastically decreases when the decay speed of the kernel φ(t) is low (e.g.,
power-law decaying kernel)" and "The probabilistic interpretation of the kernel values involved in the EM method
prevents the kernels to have negative values".

*(b) Least-squares contrast.* Minimise C(mu, Phi) = sum_i [ integral_0^T lambda_i(t)^2 dt - 2 integral_0^T
lambda_i(t) dN_i(t) ] over piecewise-constant kernels (BMM eqs. (72)-(74), lines 2201-2212); its expectation equals
the L2 distance between the model intensity and the true one (their eqs. (75)-(76)), and with a Lasso penalty it suits
small samples.

*(c) Wiener-Hopf (Bacry and Muzy 2016).* Define the conditional intensity g_ij(t) = E[dN_i(t) | dN_j(0) = 1] / dt -
Lambda_i for t > 0 (BMM eq. (36)). Then the kernel matrix is the unique causal L1 solution of

    g(t) = Phi(t) + (Phi * g)(t),   t > 0       (BMM Theorem 2, eq. (38), lines 631-635)

where * is convolution. Algorithm (BMM lines 2265-2280): estimate Lambda_i = N_i(T) / T; estimate g(t) by kernel
density methods from the empirical cross-event lag distribution; discretise the integral equation on quadrature
points over a chosen support; solve the linear system for Phi on those points; recover mu from Lambda = (I + Psi_hat(0))
mu (eq. (21)). BMM (lines 2290-2296) prefer it to EM when kernels are "not localized (e.g., power-law)" or may be
negative. Bacry, Jaisson and Muzy (2016) adapt it to slowly decaying kernels and recover "a power-law decreasing kernel
over at least 6 decades" in simulation (`arxiv_1412_7096.txt`, lines 22-24).

*(d) Integrated cumulants (NPHC, Achab et al. 2017).* Estimate only the matrix of integrals ||Phi|| by matching the
second- and third-order integrated cumulants of the counts, no kernel shape at all (`achab_etal_2017_nphc.txt`,
abstract: "the first that leads to an estimation of this matrix without any parametric modeling and estimation of the
kernels themselves ... we introduce a moment matching method that fits the second-order and the third-order integrated
cumulants of the process"). Cumulant estimation costs O(nd), O(nd^2), O(nd^3) for orders 1, 2, 3 (lines 339-340).

*(e) Binning and INAR (Kirchner 2017).* Count events in bins of width Delta; the bin counts approximately follow an
integer-valued autoregression INAR(p), estimated as an ordinary VAR(p) by conditional least squares; rescaled
coefficients estimate the kernel on the grid (`kirchner_2017.txt`, abstract: "The timeline is cut into bins and—for
each component process—the number of points in each bin is counted ... the distribution of the resulting ‘bin-count
sequences’ can be approximated by an integer-valued autoregressive model known as the (multivariate) INAR(p) model ...
The estimator depends on a bin-size ∆ and a support s"). This is the closest bridge to the program's existing
regression toolkit: it is a VAR on event counts, with Newey-West-style inference available.

*(f) Moment estimator of the branching ratio (Hardiman and Bouchaud 2014).* For a window W much longer than the
kernel memory, n ≈ 1 - sqrt( E[N_W] / Var[N_W] ) (BMM eq. (64), lines 1229-1233, from Hardiman and Bouchaud 2014,
whose abstract says it "requires knowing only the mean and variance of the event count in a sufficiently large time
window"). BMM (lines 1240-1242) add: "this formula only holds for 1-dimensional Hawkes processes and has no simple
extension in the multivariate situation."

**(3) Data.** As for MLE. The nonparametric methods want more events than parametric ones, because each grid point
of g(t) is a density estimate; months of one contract are enough for D up to about 8 on a log-spaced grid from about
1 ms to 100 s, if fitted on stationary-enough subsamples (or with a seasonal baseline).

**(4) Estimates.** Kernel shapes, their integrals (endogeneity per pair), the time scales of excitation.

**(5) Worked example (measured, method (f)).** On the simulated path of section 3 (n = 0.8, 1/beta = 1 s, 502,398
events) the moment estimator gives:

| window W | mean count | variance | n_hat = 1 - sqrt(mean/var) |
|---|---|---|---|
| 10 s | 25.12 | 380.9 | 0.743 |
| 100 s | 251.2 | 6481 | 1 - sqrt(0.03876) = 1 - 0.1969 = 0.803 |
| 1000 s | 2512 | 59,795 | 0.795 |

With W = 10 kernel time constants the estimate is biased down (0.743); with W >= 100 it is within 0.01 of the truth (exact finite-window values 0.795 and 0.800). On real data
W must exceed the longest memory in the kernel, which for power-law kernels may be hours, so seasonality then
contaminates the variance: the estimator can only be as good as the deseasonalisation.

**(6) Pilot hypothesis.** Use one nonparametric fit (Wiener-Hopf or INAR on log-spaced lags) on the pilot's first
month only, to fix the parametric kernel family and the three fixed decays for H-C2-1 to H-C2-3, before any test
data are touched. That selection step is part of the frozen pipeline; if more than one family is carried forward to
a test, each counts in N. A useful descriptive output for the program: the fraction of buy-to-buy and
trade-to-refill excitation mass at lags below 50 ms (unreachable at retail latency) versus above.

**(7) Compute.** g(t) estimation is O(N x number of lags within the support) with sorted arrays; the Wiener-Hopf
solve is a dense linear system of size (D x grid points), e.g. 8 x 100 = 800 unknowns: trivial. Measured: tick's
nonparametric EM learner (HawkesEM) failed at construction on this machine with tick 0.8.0.2 ("'History' object has no
settable attribute '_minimum_col_width'", `C2_bench_results.json`, `speed_tick`), so an own numpy implementation of
(c) or (e) would be needed; both are a few hundred lines. Laptop is enough.

**(8) Evidence.** The Wiener-Hopf and NPHC methods are validated in their papers on simulations and applied
descriptively to Bund and DAX futures (BJM 2016) and to "financial order book data" (NPHC abstract). Rambaldi, Bacry
and Lillo (2017) apply Wiener-Hopf to Eurex futures with order sizes (section 4). All of this is descriptive
structure; none of these papers reports a forecast or trading test.

---

## 8. The branching ratio as an endogeneity measure, and the criticality debate

**(1) Idea.** n is the fraction of events caused by earlier events. Filimonov and Sornette (2012) proposed it as a
measure of "reflexivity" and a warning signal for flash crashes; Hardiman, Bercot and Bouchaud (2013) argued that
markets sit at n close to 1 at all times; Filimonov and Sornette (2015) replied that the near-1 values are artefacts.
For this program the debate matters less for what n is than for the warnings it produced about fitting Hawkes models
to futures data.

**(2) Equations.** Endogenous fraction = n (one dimension), from Lambda = mu / (1 - n), so mu / Lambda = 1 - n (BMM,
lines 1194-1197). The FS 2012 estimator: exponential-kernel MLE on short windows; HBB 2013: power-law kernel MLE
(section 5); HB 2014: moment estimator (section 7 (f)).

**(3) Data.** E-mini S&P 500 mid-price changes in all three; this is the parent of MES, so the setting is directly
comparable. One contract of tbbo or mbp-1 is enough to reproduce the estimates.

**(4) Estimates.** A time series of n (for example per 30-minute window).

**(5) Worked example.** With mu = 0.5 and n = 0.8 the observed rate is 2.5 per s and only 0.5 of it (20 %) is
exogenous; at n = 0.95 the same mu gives 10 per s and 5 % exogenous. Near 1, small errors in n mean large changes in
implied exogeneity, which is why the bias sources below matter. The measured spurious fit in section 6 (true n = 0,
fitted 0.956) is the cautionary example.

**(6) Pilot hypothesis.** None recommended as a trading test (no published trading result; see (8)). If the lead
wants a diagnostic: "rolling 30-minute n_hat (frozen estimator) is higher in the 30 minutes before the pilot's worst
decile of 60 s markouts than otherwise"; 1 configuration; low prior.

**(7) Compute.** Small (hundreds of 30-minute univariate fits: minutes).

**(8) Evidence.**
- Filimonov and Sornette (2012), E-mini 1998-2010 (`filimonov_sornette_2012.txt`, abstract): "We find that the level of
  endogeneity has increased significantly from 1998 to 2010, with only 70% in 1998 to less than 30% since 2007 of the
  price changes resulting from some revealed exogenous information."
- Hardiman, Bercot and Bouchaud (2013) (abstract, lines 10-16): "we find that the Hawkes kernel integrates to unity
  independently of the analysed period, from 1998 to 2011. This suggests that markets are and have always been close
  to criticality, challenging a recent study which indicates that reflexivity (endogeneity) has increased in recent
  years as a result of increased automation of trading."
- Filimonov and Sornette (2015) (`filimonov_sornette_2015_apparent.txt`, abstract): "We report the following model
  biases: (i) evidence of strong upward biases on the estimation of n when using power law memory kernels in the
  presence of outliers, (ii) strong effects on n resulting from the form of the regularization part of the power law
  kernel, (iii) strong edge effects on the estimated n when using power law kernels, and (iv) the need for an
  exhaustive search of the absolute maximum of the log-likelihood function due to its complicated shape. Moreover, we
  demonstrate that the calibration of the Hawkes process on mixtures of pure Poisson process with changes of regime
  leads to completely spurious apparent critical values for the branching ratio (n ≃ 1) while the true value is
  actually n = 0." The same abstract stresses "(a) the impact of overnight trading ... (b) intraday seasonality and
  detrending of the data and (c) vulnerability of the analysis to day-to-day non-stationarity and regime shifts" and
  "the decrease of quality of the timestamps of tick data due to latency and grouping of messages to packets by the
  stock exchange".
- Hardiman and Bouchaud (2014) (abstract): their moment estimator supports the view that "the best fitting Hawkes
  model to describe S&P futures price changes is in fact critical (now and in the recent past)".
- Lallouache and Challet (2016), FX: n "high but sub-critical at about 0.8", and "the use of power law-like kernels
  mechanically increases the apparent endogeneity factor ... the best kernels are never those with the largest
  endogeneity factors" (lines 917-921).
- BMM (lines 1244-1249) credit FS 2012 with showing the approach "can be used to study particular events such as the
  flash crashes of April and May 2010" and say the results "may be helpful to devise warning tools". I found no
  out-of-sample test of such a warning tool in the sources read [gap, not a finding of absence].

---
## 9. Uses: order-arrival intensity forecasts, fill probability, short-horizon prediction, market making

This section treats the three uses the brief names as methods in their own right, with the evidence on whether each
works.

### 9a. Forecasting order-arrival intensity

**(1) Idea.** At any instant, the fitted lambda_i(t) is a forecast of the rate of type-i events over the next
fraction of a second to a few seconds. For a passive bid, the relevant forecasts are the market-sell rate (fills) and
the market-buy and up-tick rates (the price moving away).

**(2) Equations.** Forecast over horizon h: E[N_i(t, t + h] | H_t] = integral_t^{t+h} E[lambda_i(s) | H_t] ds. For the
exponential kernel with shared beta the conditional mean intensity relaxes to its stationary mean:
E[lambda(t + s) | H_t] = Lambda + (lambda(t) - Lambda) e^{-(1 - n) beta s} in one dimension (derivation: take
expectations of d lambda = -beta (lambda - mu) dt + n beta dN, with E[dN] = lambda ds, giving a linear ODE with rate
beta (1 - n)). In D dimensions the decay matrix is beta (I - ||Phi||). Note the close link to features the program
already knows: with beta fixed, lambda(t) - mu = n beta x (exponentially weighted count of past events with decay
beta). The Hawkes fit mainly chooses the weights and decay; the feature itself is an EWMA of event counts.

**(3) Data.** tbbo for trade intensities; mbp-10 for book events.

**(4) Decides.** Expected next-h-second fills and one-sided pressure; inputs to quoting (skip, widen, cancel).

**(5) Worked example.** n = 0.6, beta = 2 per s, mu = 0.5 per s, so Lambda = 1.25 per s. Right after a burst,
lambda(t) = 4 per s. The excess 2.75 per s decays at rate (1 - 0.6) x 2 = 0.8 per s: after 1 s the expected rate is
1.25 + 2.75 e^{-0.8} = 1.25 + 1.236 = 2.49 per s; after 5 s, 1.25 + 2.75 e^{-4} = 1.30. Expected events in the next
1 s: 1.25 + 2.75 (1 - e^{-0.8}) / 0.8 = 1.25 + 2.75 x 0.6883 = 3.14, versus 1.25 under Poisson.

**(6) Pilot hypothesis.** H-C2-1 (section 11).

**(7) Compute.** Online update is O(D^2) per event (microseconds); fits as in sections 4-5.

**(8) Evidence.** On synthetic data where the model is true, the 4-D model beats a Poisson model with the right rates
by 0.118 nats of log-likelihood per event (`C2_multi_results.json`; this only illustrates the metric). On real data,
I found no published out-of-sample likelihood comparison on CME futures in the sources read; Lallouache and Challet's
failure of multi-day stationarity (section 6) predicts that day-ahead parameters will lose some of the in-sample gain.
[Gap, not a finding.]

### 9b. Fill probability and queue depletion

**(1) Idea.** A resting 1-lot order fills when the volume ahead of it is consumed (by market orders and by
cancellations ahead) before the price moves away. Model each of those flows as point processes; the fill time is a
first-passage time. With Poisson flows there are closed forms (another C2 reader covers the Cont-Stoikov-Talreja
mathematics); with Hawkes flows one simulates from the fitted model conditional on the current history.

**(2) Equations.** Fill by time h if sum over market orders hitting the level in (t, t + h] of their sizes, plus
cancellations ahead, reaches Q_ahead + 1 before the level is cleared or the opposite quote moves. Monte Carlo:
simulate the fitted Hawkes model forward from the current intensities (Ogata thinning, as in `C2_bench.py`) R times;
P_hat(fill by h) = share of paths that reach the threshold. Sizes need a mark distribution (Rambaldi, Bacry and Lillo
2017: size and timing are not independent).

**(3) Data.** Queue position needs mbo (order IDs and fills); mbp-10 gives queue size by level but not one order's
place in it (the pilot can approximate it: back of the queue at placement, moved up by cancels in proportion).

**(4) Decides.** Expected fill probability and time for a passive order at each level; the fill model used in any
later backtest of a passive strategy.

**(5) Worked example (measured).** Section 3 (5b): with the same mean of 2 market sells per s and 20 lots ahead,
P(fill within 10 s) is 0.441 under Poisson and 0.392 under Hawkes (n = 0.7); the Hawkes count variance is 7.8 times
the Poisson one. A Poisson fill model therefore overstates fills in quiet periods and understates how concentrated
fills are in bursts.

**(6) Pilot hypothesis.** H-C2-3 (section 11): the Hawkes-driven fill model beats the seasonal-Poisson fill model on
out-of-sample Brier score of the pilot's 10 s fill indicator.

**(7) Compute.** R = 1,000 forward paths of 10 s at a few events per second is about 10^4 to 10^5 simulated events per
evaluated order; for 10^5 pilot orders that is 10^9 to 10^10 simulated events: hours to days in plain Python, minutes
to hours compiled, or use a variance-reduced analytic approximation. This is the one place a bigger CPU machine would
help; Lambda's 1x A10 instance (30 vCPUs) is listed at $1.29 per hour, and 30 vCPUs for 24 h would cost about $31
(`lambda_pricing.html.txt`). Sub-sampling the orders (for example 10,000) keeps it on the laptop.

**(8) Evidence.** Lokin and Yu (2026), FX spot, state-dependent (Cox/Poisson-type, not Hawkes) queue model
(`lokin_yu_2026_fillprob.txt`, lines 1766-1768): "fill probabilities are slightly overestimated when the best-bid queue
is large ... [execution probability] typically below 0.5%, making accurate estimation challenging" (line wrap; the
bracket is mine). Arroyo, Cartea, Moreno-Pino and Zohren (2023) estimate fill times directly with a deep survival
model and report that "Our method significantly outperforms those typically used in survival analysis literature"
(`arroyo_etal_2023_fillsurv.txt`, abstract); they do not compare against a Hawkes model (0 mentions of "Hawkes" in the
text). A Hawkes-based dark-pool fill-time analysis exists (arXiv 1710.01452) [unverified, search snippet only]. I found
no paper that validates a Hawkes-driven fill model against realised fills of a small resting order on CME data.

### 9c. Short-horizon prediction (next event type, sign, aggressiveness)

**(1) Idea.** Predict the type of the next event as the type with the largest intensity at t-.

**(2) Equations.** Predicted type at t- = argmax_i lambda_i(t-) (Sfendourakis and Muni Toke 2021, section 3.6). For
the ratio models, P(next is type i | an event occurs at t) = lambda_i / sum_j lambda_j, in which the unknown baseline
cancels.

**(3) Data.** tbbo for trade signs; mbp-10 for book-state covariates.

**(4) Decides.** Sign of the next trade or mid move; a direction signal.

**(5) Example of the benchmark trap.** Sfendourakis and Muni Toke (2021, lines 925-928) note that even full knowledge
of a two-type Poisson model with rates 1 and 2 only gives 2/3 accuracy, by always predicting the more frequent type;
accuracy must be judged against simple benchmarks such as "same as last".

**(6) Pilot hypothesis.** H-C2-4 (section 11), with a stated low prior; only worth running as part of a feature set
for the ML readers' models, not as a stand-alone rule.

**(7) Compute.** Small.

**(8) Evidence (negative for plain Hawkes).**
- Sfendourakis and Muni Toke (2021), 36 Paris stocks, 2015, parameters from the previous day (out-of-sample)
  (`sfendourakis_toke_2021.txt`, lines 940-945): "the ’Last’ benchmark correctly signs in average 81% of the trades
  ... This is the best of the benchmarks: ’Imbalance’ is outperformed on 75% of the stock-trading days, the standard
  Hawkes model and the ksdHawkes models are outperformed on more than 90% of the sample." Only the state-dependent
  model with imbalance helps: "Excess performance is positive 97.5% of the time, and increases the signature accuracy
  by more than 5% in average on the sample" (lines 950-951).
- Muni Toke and Yoshida (2020), next-day out-of-sample (`toke_yoshida_2020.txt`, lines 967-969): "The benchmark Hawkes
  model correctly predicts the sign and aggressiveness of an incoming with an accuracy in the range [40%, 60%] for all
  stocks, with a 50% average." Their Table 2: global accuracy 0.503 (Hawkes) versus 0.667 for the best marked ratio
  model with book covariates. They call the exercise "theoretical in the sense that we assume that these computations
  are instantaneous" (lines 895-896): no latency, no costs.
- Neural point processes: EasyTPP (Xue et al., ICLR 2024; `arxiv_2307_08097.txt`, lines 603-606): "the performance of
  new models on the standard datasets seem to be saturating. Notably, all the best to-date models make poor
  predictions on time of future events." Shi and Cartlidge (KDD 2022) report a neural Hawkes model beating
  stochastic and deep baselines on LOB event prediction [unverified, search snippet only].
- None of these is a cost-inclusive trading result.

### 9d. Market making with Hawkes order flow (control models)

**(1) Idea.** Let market-order arrivals be mutually exciting and let them shift the short-term drift of the mid; solve
for optimal quotes (the HJB machinery belongs to the stochastic-control reader).

**(8) Evidence (simulation, not historical).** Cartea, Jaimungal and Ricci (2014/2018), abstract
(`cartea_jaimungal_ricci_2018_ora.txt`): "We show that HF traders who do not include predictors of short-term-alpha in
their strategies are driven out of the market because they are adversely selected by better informed traders and
because they are not able to profit from directional strategies." Their P&L comes from model simulation (lines
930-944): "we apply a simulation study of the HF strategy where MOs are generated over a period of five minutes ...
in each simulation the process is repeated 5, 000 times to obtain the PnLs". Lalor and Swishchuk (2025) use a neural
Hawkes LOB simulator as the environment for a market-making agent (`lalor_swishchuk_2025.txt`, abstract): again a
simulation study. The relevant lesson for a 1-lot passive order at retail latency is the adverse-selection one, which
H-C2-2 tests directly on pilot data.

---
## 10. Open-source software and measured speed

| library | what it does | status (PyPI JSON fetched 2026-10-21) | measured here |
|---|---|---|---|
| tick (X-DataInitiative) | Hawkes simulation; parametric MLE / least squares for exponential and sum-of-exponential kernels; nonparametric EM, Wiener-Hopf, NPHC, ADM4, sum of Gaussians (`bacry_etal_2017_tick.txt`, Table 2) | 0.8.0.2, uploaded 2026-05-04, wheels cp311 to cp314 incl. manylinux x86_64; requires numpy >= 2.0. Release gap: 0.7.0.1 (2020-05-24, cp36-cp38 only) to 0.8.0.0 (2026-04-18) (`pypi_tick.json`) | Simulation works: 1,001,878 events of a 4-D exponential Hawkes in 0.46 s. Every learner failed at construction: `HawkesExpKern`, `HawkesSumExpKern` ("object has no settable attribute 'events'") and `HawkesEM` ("'History' object has no settable attribute '_minimum_col_width'") under Python 3.11 and 3.12 with 0.8.0.2 (logged); also seen under 3.13 and with 0.8.0.1 [unverified: not logged]; 0.8.0.0 has no Linux wheel (`C2_bench_results.json`, `work/C2_Hawkes/C2_tick_tb.py`). I did not debug further. |
| hawkeslib | univariate exponential Hawkes MLE/EM, Bayesian | 0.2.2, 2019-06-18, cp36 wheel only (`pypi_hawkeslib.json`) | not tried (stale) |
| hawkes (omitakahiro) | parametric Hawkes estimation | 1.0.0, 2021-04-01, source only (`pypi_hawkes.json`) | not tried |
| EasyTPP (Ant Group) | neural temporal point processes (PyTorch/TensorFlow), benchmark harness | 0.3.0, 2026-07-13 (`pypi_easy-tpp.json`) | not tried (GPU; see 9c evidence) |
| pyhawkes, hawkes R, PtPack | Bayesian (pyhawkes), R, C++ MLE | named by the tick paper (lines 74-82: "very few open source packages are available. There are mainly three of them ... hawkes R ... is hardly optimized ... PtPack exhibits poor performance compared to tick") | not tried |
| own numpy code (`C2_bench.py`, `C2_multi.py`) | exact O(N) exponential-kernel log-likelihood (1-D and D-D), Ogata thinning simulation, time-rescaling residuals, multi-start MLE | written for this brief | 1-D: 0.71 s per likelihood evaluation on 10^6 events; full 3-parameter MLE on 100,220 events in 9.5 s. 4-D: 2.95 s per evaluation on 999,087 events. |

tick's published benchmark (lines 139-145): fits "on simulated 16-dimensional Hawkes processes, with an increasing
number of events: small=5 × 104 , medium=2 × 105 , large=106 , xlarge= 5 × 107 . We observe on this experiment that
tick outperforms by several orders of magnitudes both hawkes R and PtPack, in particular for large datasets." I could
not reproduce any tick fit on this machine, so its speed claims stay [unverified here].

Practical conclusion: for this program's sizes (one contract, D <= 8, fits per day), an own compiled or vectorised
exponential-kernel likelihood with analytic gradients is the safest route; tick's simulator is usable for synthetic
checks. Reproducibility note: any library used must be pinned and its environment fingerprinted, since the tick
learner failure shows these packages can break silently between releases.

### Compute summary (all methods)

| task | laptop (20 CPUs, 14 GB, RTX 3050 4 GB) | bigger machine or cloud | cost estimate |
|---|---|---|---|
| Poisson, seasonal profiles, moment estimators | seconds | not needed | 0 |
| 1-D / 2-D exponential Hawkes MLE, per day, 4-12 months | minutes in total (measured 9.5 s per 10^5-event fit) | not needed | 0 |
| 4-D to 8-D MLE per day | plain Python with numerical gradients: about 1.8 h per 10^6-event fit (extrapolated); with analytic gradients or compiled loop: minutes [unverified factor] | optional, parallel days | Lambda 1x A10 instance (30 vCPUs, 226 GiB) $1.29/h: 10 h = $12.90 |
| Nonparametric Wiener-Hopf / INAR | minutes | not needed | 0 |
| Monte Carlo Hawkes fill model on 10^5 orders | hours to days in Python; subsample to 10^4 orders | 30 vCPUs for 24 h | about $31 at $1.29/h |
| Neural TPP (EasyTPP, neural Hawkes) | the 3050's 4 GB VRAM limits batch size; feasible for small models [unverified] | single GPU | A10 24 GB at $1.29/h or Quadro RTX 6000 24 GB at $0.69/h; 20 GPU-hours = $14 to $26 |

Prices: `lambda_pricing.html.txt` (Lambda instances table, 1x plans: "NVIDIA A10 24 GB 30 226 GiB 1.3 TiB SSD $1.29",
"NVIDIA Quadro RTX 6000 24 GB 14 46 GiB 512 GiB SSD $0.69", "plus applicable sales tax/VAT/GST"), fetched 2026-10-21
09:31:40 UTC (02:31 PDT). The Hetzner page fetched alongside renders CPU prices with JavaScript, so no CPU-only price was extracted.

---

## 11. Candidate pre-registerable hypotheses from the pilot (for the lead to choose from)

These are proposals, not declarations. Common design for all: the pilot's simulated 1-lot passive orders on one
contract (fill indicator within 1/10/60 s, queue time, markouts at 1/10/60 s in ticks); models fitted on day d-1 and
applied to day d (walk-forward, no information from day d); the seasonal profile and any kernel choice frozen on the
first pilot month, which is then excluded from testing; inference across days (day-clustered standard errors or
Newey-West on daily statistics); success threshold t > 3.0 as in the program. Sample-size arithmetic: for a two-group
difference in mean markout with sd = 1 tick, detectable difference 0.1 tick, power 0.8, the per-group n is
2 (z + 0.8416)^2 / 0.1^2: 1,570 at z = 1.96 and 2,952 at z = 3.0 (`C2_examples.json`); a markout sd of 2 ticks
quadruples it; within-day correlation inflates it further. The MES markout sd and the number of pilot fills per day
are not known yet [to be measured in Part B].

| ID | hypothesis (H1) | test statistic | sample needed | data | configs added to N |
|---|---|---|---|---|---|
| H-C2-0 | After removing the frozen intraday profile, market-order counts in 10 s windows are over-dispersed (Var/mean > 1), i.e. arrivals are not seasonal Poisson | daily Hardiman-Bouchaud n_hat (W = 100 s) and Var/mean of 10 s counts; one-sided t across days | 20+ days | tbbo | 0 if declared a diagnostic that selects nothing (lead decides) |
| H-C2-1 | A bivariate buy/sell exponential-sum Hawkes model (decays 0.1, 1, 10 s fixed; seasonal baseline) fitted on day d-1 gives higher log-likelihood per event on day d than the seasonal inhomogeneous Poisson | mean daily out-of-sample log-likelihood ratio per event; t across days (Newey-West, 5 lags) | 60+ evaluation days | tbbo | 1 |
| H-C2-2 | Passive fills are more adverse when the model's same-direction aggressive intensity at fill time is high: mean markout of fills in the top tercile of lambda_hat(t_fill-) is worse than in the bottom tercile, beyond a fixed EWMA-count benchmark | difference in mean markout (ticks) top minus bottom tercile, day-clustered SE; or regression of markout on standardised log lambda_hat plus the benchmark count, clustered by day | about 3,000 fills per tercile at sd = 1 tick (about 9,000 fills); more if sd is larger | tbbo or mbp-1 for trades and mid; pilot fills | 3 (horizons 1, 10, 60 s), 6 if two kernel families are kept |
| H-C2-3 | A Hawkes-driven queue-depletion fill model predicts the pilot's 10 s fill indicator better than the seasonal-Poisson queue model | out-of-sample Brier score difference, daily means, DM-type t across days | 10,000+ evaluated orders over 60+ days | mbo preferred (queue position); mbp-10 with approximation | 1 (3 if 1/10/60 s fill horizons are all tested) |
| H-C2-4 | The sign of the next trade is predicted by argmax lambda_hat better than "same as last trade" | accuracy difference per day, t across days | 20+ days | tbbo | 1 per target; low prior (section 9c evidence) |
| H-C2-5 | The mutually exciting up/down mid model (Bacry et al. 2013) fitted on day d-1 forecasts the mean 1 s and 10 s reversion of the mid after a passive fill better than zero reversion | mean squared forecast error difference, DM-type t across days | 60+ days, thousands of fills | mbp-1 / mbp-10 | 2 |

What each would decide: H-C2-1 and H-C2-0 only show that the model class carries information (a gate). H-C2-2 is
the one that could change trading: a quoting filter ("do not rest, or cancel, when the toxic-flow intensity is high")
would be a later, separately registered rule. H-C2-3 decides which fill model the program's passive-order backtests
should use; that is a simulator choice, so its configurations should be counted and frozen before any strategy is
tested on that simulator. If all six are run: 8 to 13 configurations added to N; without H-C2-4 (skip, section 12): 7 to 12; plus 1 for the kernel-family
choice made on the first month.

---
## 12. Verdicts per method (use / maybe / skip for this program)

| method | verdict | reason |
|---|---|---|
| Homogeneous Poisson | use, as a null only | It is the benchmark every clustering claim and every fill model must beat; it is wrong as a description (over-dispersion). |
| Inhomogeneous (seasonal) Poisson | use | Mandatory baseline and deseasonaliser; without it Hawkes fits read seasonality and regime shifts as self-excitation (measured: true n = 0 fitted as 0.956). |
| Univariate Hawkes, exponential or sum-of-exponential kernel | use | Cheap (seconds per day on the laptop), exact O(N) likelihood, and its intensity is an EWMA event count with a principled decay; the building block for H-C2-1 to H-C2-3. |
| Univariate Hawkes, power-law kernel | maybe (descriptive only) | Fits E-mini data better (HBB 2013) but is the main source of biased branching ratios (FS 2015); not needed for second-scale fill and markout questions. |
| Multivariate Hawkes, low dimension (buy/sell market orders, up/down mid moves) | use | Directly models one-sided pressure and mid reversion around a passive fill; laptop-sized; tbbo or mbp-1 suffice. |
| Multivariate Hawkes, high dimension (limit orders, cancels by level; Large-style resiliency) | maybe | Descriptive value (refill speed after a trade on MES), but part of the excitation is sub-millisecond (0.3 ms for the fast, localized influences, BJM 2016), below this program's reaction time; needs mbo for clean cancel and queue data. |
| State-dependent Hawkes and ratio models (book imbalance, spread) | maybe | The only Hawkes-family variants with documented out-of-sample predictive gains (Toke-Yoshida, Sfendourakis-Toke), but on stock trade signs, without latency or costs; better treated as features inside the ML readers' pipeline. |
| MLE with the O(N) recursion | use | Standard, consistent, recovers parameters on synthetic data; multi-start required. |
| Time-rescaling goodness of fit (KS, Ljung-Box, excess dispersion) | use, as a gate | Cheap and standard, but measured here to pass a misspecified model, so it cannot be the only check. |
| Nonparametric kernels (Wiener-Hopf, INAR binning) | maybe | One-off on the first pilot month to choose the kernel family and see the time scales; INAR is a VAR on counts that fits the program's tools. tick's EM learner failed here; own code needed. |
| Nonparametric NPHC (integrated cumulants) | skip | Built for and tested at d = 10 to 100 (MemeTracker top 100 sites); this program has D <= 8. |
| Branching ratio as endogeneity or crash-warning signal | skip as a signal | Contested estimates (FS 2012 vs HBB 2013 vs FS 2015), no out-of-sample warning test found, no trading result. |
| Hawkes intensity forecasts (H-C2-1) | use, as a gate | Shows whether the model class carries day-ahead information on this contract before any trading test. |
| Hawkes-driven fill-probability model (H-C2-3) | maybe, promote to use if the pilot shows the Poisson fill model is miscalibrated | Fill models decide every passive-strategy backtest; no published validation against small resting orders on CME found. |
| Short-horizon direction from plain Hawkes intensities (H-C2-4) | skip | Out-of-sample evidence negative: plain Hawkes loses to "same as last" on more than 90 % of stock-days (Sfendourakis-Toke 2021); 50 % global accuracy (Toke-Yoshida 2020). |
| Adverse-selection conditioning of passive fills (H-C2-2) | use | The one trading-relevant test; it uses the pilot's own markouts; theory (Cartea-Jaimungal-Ricci) says ignoring short-term alpha gets a passive trader adversely selected. |
| Hawkes-driven market-making control models | skip for now | Evidence is in-model simulation only; belongs to the control reader; revisit only if H-C2-2 finds a toxic-flow effect. |
| Neural temporal point processes (EasyTPP, neural Hawkes) | skip | Needs GPU work, many configurations (all count in N), benchmark saturation ("all the best to-date models make poor predictions on time of future events"), and no cost-inclusive trading evidence. |

Overall: point processes are worth using here as measurement and simulation tools (fill model, toxic-flow
conditioning, honest baselines), not as a stand-alone source of alpha. I found no out-of-sample, cost-inclusive,
post-publication trading result for any Hawkes-based strategy in the sources read; the one direct predictive test
family (next-trade sign) is negative for plain Hawkes. That absence is a gap in what I found (10 of 60 searches used),
not proof that none exists.

---

## References

- Arroyo, A., Cartea, A., Moreno-Pino, F., Zohren, S. (2023). Deep attentive survival analysis in limit order books:
  estimating fill probabilities with convolutional-transformers. arXiv:2306.05479. File `arroyo_etal_2023_fillsurv.pdf`.
- Achab, M., Bacry, E., Gaïffas, S., Mastromatteo, I., Muzy, J.-F. (2017). Uncovering causality from multivariate
  Hawkes integrated cumulants. ICML; arXiv:1607.06333. File `achab_etal_2017_nphc.pdf`.
- Abergel, F., Jedidi, A. (2013). A mathematical approach to order book modeling. arXiv:1010.5136. File
  `abergel_jedidi_2013.pdf` (fetched by mistake for a Toke paper; not used as evidence).
- Bacry, E., Bompaire, M., Gaïffas, S., Poulsen, S. (2017). Tick: a Python library for statistical learning, with a
  particular emphasis on time-dependent modelling. arXiv:1707.03003. File `bacry_etal_2017_tick.pdf`.
- Bacry, E., Delattre, S., Hoffmann, M., Muzy, J.-F. (2013). Modelling microstructure noise with mutually exciting
  point processes. Quantitative Finance 13(1); arXiv:1101.3422. File `bacry_delattre_hoffmann_muzy_2013.pdf`.
- Bacry, E., Jaisson, T., Muzy, J.-F. (2016). Estimation of slowly decreasing Hawkes kernels: application to high
  frequency order book modelling. Quantitative Finance; arXiv:1412.7096. File `arxiv_1412_7096.pdf`.
- Bacry, E., Mastromatteo, I., Muzy, J.-F. (2015). Hawkes processes in finance. Market Microstructure and Liquidity
  1(1); arXiv:1502.04592. File `bacry_mastromatteo_muzy_2015.pdf`.
- Bacry, E., Muzy, J.-F. (2016). First- and second-order statistics characterization of Hawkes processes and
  non-parametric estimation. IEEE Trans. Information Theory; arXiv:1401.0903. File `bacry_muzy_2016_nonparam.pdf`.
- Brown, E. N., Barbieri, R., Ventura, V., Kass, R. E., Frank, L. M. (2002). The time-rescaling theorem and its
  application to neural spike train data analysis. Neural Computation 14(2). File `brown_etal_2002_rescaling.pdf`
  (CMU copy).
- Cartea, A., Jaimungal, S., Ricci, J. (2014/2018). Buy low, sell high: a high frequency trading perspective (SIAM J.
  Financial Math. 2014); SIGEST reprint "Algorithmic trading, stochastic control, and mutually exciting processes",
  SIAM Review 60(3), 2018. File `cartea_jaimungal_ricci_2018_ora.pdf` (Oxford ORA copy; DOI printed in it
  10.1137/130911196).
- Databento documentation: MBO, MBP-10 and TBBO schema pages (fetched 2026-10-21). Files `databento_*_schema.html`.
- Filimonov, V., Sornette, D. (2012). Quantifying reflexivity in financial markets: toward a prediction of flash
  crashes. Physical Review E 85; arXiv:1201.3572. File `filimonov_sornette_2012.pdf`.
- Filimonov, V., Sornette, D. (2015). Apparent criticality and calibration issues in the Hawkes self-excited point
  process model: application to high-frequency financial data. Quantitative Finance 15(8); arXiv:1308.6756. File
  `filimonov_sornette_2015_apparent.pdf`.
- Hardiman, S. J., Bercot, N., Bouchaud, J.-P. (2013). Critical reflexivity in financial markets: a Hawkes process
  analysis. European Physical Journal B 86; arXiv:1302.1405. File `hardiman_bercot_bouchaud_2013.pdf`.
- Hardiman, S. J., Bouchaud, J.-P. (2014). Branching-ratio approximation for the self-exciting Hawkes process.
  Physical Review E 90; arXiv:1403.5227. File `hardiman_bouchaud_2014_branching.pdf`.
- Jain, K., Firoozye, N., Kochems, J., Treleaven, P. (2024). Limit order book simulations: a review. arXiv:2402.17359.
  File `arxiv_2402_17359.pdf`.
- Kirchner, M. (2017). An estimation procedure for the Hawkes process. Quantitative Finance; arXiv:1509.02017. File
  `kirchner_2017.pdf`.
- Lalor, L., Swishchuk, A. (2025). Event-based limit order book simulation under a neural Hawkes process: application
  in market-making. arXiv:2502.17417. File `lalor_swishchuk_2025.pdf`.
- Lallouache, M., Challet, D. (2016). The limits of statistical significance of Hawkes processes fitted to financial
  data. Quantitative Finance 16(1); arXiv:1406.3967. File `lallouache_challet_2016.pdf`.
- Large, J. (2007). Measuring the resiliency of an electronic limit order book. Journal of Financial Markets 10(1),
  1-25. Not read (paywalled); cited through BMM (2015).
- Lokin, F., Yu, F. (2026, v2). Fill probabilities in a limit order book with state-dependent stochastic order flows.
  arXiv:2403.02572v2. File `lokin_yu_2026_fillprob.pdf` (authors Felix Lokin and Fenghui Yu per the PDF title page).
- Lu, X., Abergel, F. (2018). High-dimensional Hawkes processes for limit order books. Quantitative Finance 18(2),
  249-264. Not read (HAL bot check); [unverified].
- Martins, R., Hendricks, D. (2016). The statistical significance of multivariate Hawkes processes fitted to limit
  order book data. arXiv:1604.01824. File `arxiv_1604_01824_multivar_signif.pdf`.
- Morariu-Patrichi, M., Pakkanen, M. S. (2022). State-dependent Hawkes processes and their application to limit order
  book modelling. Quantitative Finance; arXiv:1809.08060. File `morariu_pakkanen_2022.pdf`.
- Muni Toke, I. (2011). "Market making" in an order book model and its impact on the spread. In Econophysics of
  Order-driven Markets (Springer); arXiv:1003.3796. File `toke_2011_marketmaking.pdf`.
- Muni Toke, I., Yoshida, N. (2020). Marked point processes and intensity ratios for limit order book modeling.
  arXiv:2001.08442. File `toke_yoshida_2020.pdf`.
- Ogata, Y. (1978). The asymptotic behaviour of maximum likelihood estimators for stationary point processes. Annals
  of the Institute of Statistical Mathematics 30. Not fetched [unverified].
- Ozaki, T. (1979). Maximum likelihood estimation of Hawkes' self-exciting point processes. Annals of the Institute
  of Statistical Mathematics 31. Not fetched; recursion quoted via Martins-Hendricks and Lallouache-Challet.
- Rambaldi, M., Bacry, E., Lillo, F. (2017). The role of volume in order book dynamics: a multivariate Hawkes process
  analysis. Quantitative Finance 17(7); arXiv:1602.07663. File `rambaldi_bacry_lillo_2017.pdf`.
- Rambaldi, M., Pennesi, P., Lillo, F. (2015). Modeling foreign exchange market activity around macroeconomic news: a
  Hawkes process approach. Physical Review E 91; arXiv:1405.6047. File `rambaldi_pennesi_lillo_2015.pdf`.
- Sfendourakis, E., Muni Toke, I. (2021). LOB modeling using Hawkes processes with a state-dependent factor.
  arXiv:2107.12872. File `sfendourakis_toke_2021.pdf`.
- Swishchuk, A. (2017). General compound Hawkes processes in limit order books. arXiv:1706.07459. File
  `arxiv_1706_07459.pdf` (fetched from a search hit; not used as evidence).
- Xue, S., et al. (2024). EasyTPP: towards open benchmarking temporal point processes. ICLR 2024; arXiv:2307.08097.
  File `arxiv_2307_08097.pdf`.
- Lambda, GPU cloud pricing page, https://lambda.ai/pricing, fetched 2026-10-21 09:31 UTC. File `lambda_pricing.html`.
- PyPI JSON metadata for tick, hawkeslib, hawkes, easy-tpp, fetched 2026-10-21. Files `pypi_*.json`.

---

## Evidence table

All files under `reports/stage_e28_briefs/pages/C2_Hawkes/` (".txt" is the pdftotext or de-tagged text of the saved
PDF or HTML; quotes are from it, with pdftotext line breaks joined).

| claim | source | verbatim quote | saved file |
|---|---|---|---|
| Hawkes definition | BMM 2015, Def. 1 | "A Hawkes process is a counting-process Nt such that the intensity vector can be written as" | bacry_mastromatteo_muzy_2015.pdf |
| Stationarity condition | BMM 2015, Prop. 1 | "(H) The matrix ||Φ|| = {||φij ||} [D, i,j=1] has spectral radius smaller than 1." | bacry_mastromatteo_muzy_2015.pdf |
| Power-law kernel stationarity | BMM 2015, eq. (10) | "indicating that the tail exponent γ of a power law-kernel should be positive for the increments of the process to be stationary" | bacry_mastromatteo_muzy_2015.pdf |
| Exponential kernel gives Markov property | BMM 2015, Prop. 2 | "Then the couple (Nt , λt ) is a Markov process." | bacry_mastromatteo_muzy_2015.pdf |
| Galton-Watson mapping | BMM 2015, sec. 2.3.7 | "it is possible to map the branching structure of the Hawkes process described above onto the one of a Galton-Watson tree with average offspring ||Φ||" | bacry_mastromatteo_muzy_2015.pdf |
| n = endogenous fraction | BMM 2015, sec. 3.2 | "||Φ|| provides a direct measure of the fraction of endogenous events within the whole population of mid-price changes" | bacry_mastromatteo_muzy_2015.pdf |
| Point-process log-likelihood | BMM 2015, App. C.1 | "The log-likelihood of a non-homogeneous, multi-dimensional Poisson defined as in Eq. (2) reads" | bacry_mastromatteo_muzy_2015.pdf |
| O(N) for exponential kernels | BMM 2015, App. C.1 | "The fact that it reduces to O(M D) when the kernels are exponential functions is one of the major reasons why exponential kernels (or sum of exponential kernels) are so commonly used" | bacry_mastromatteo_muzy_2015.pdf |
| Ozaki recursion | Lallouache-Challet 2016 | "one can exploit a recursive relation for the log-likelihood calculation that reduces the computational complexity from O(N 2 ) to O(N ) (see Ozaki [37])" | lallouache_challet_2016.pdf |
| Multivariate O(N) disputed | Martins-Hendricks 2016 | "this advantage does not translate to the multivariate case" | arxiv_1604_01824_multivar_signif.pdf |
| EM weakness for slow kernels | BMM 2015, App. C.2 | "The convergence speed of the EM algorithm drastically decreases when the decay speed of the kernel φ(t) is low (e.g., power-law decaying kernel)" | bacry_mastromatteo_muzy_2015.pdf |
| Wiener-Hopf characterisation | BMM 2015, Thm. 2 | "Then the matrix function χ(t) = Φ(t) is the unique solution of the Wiener-Hopf system" | bacry_mastromatteo_muzy_2015.pdf |
| Moment estimator only 1-D | BMM 2015, sec. 3.2 | "this formula only holds for 1-dimensional Hawkes processes and has no simple extension in the multivariate situation" | bacry_mastromatteo_muzy_2015.pdf |
| Large (2007) resiliency result | BMM 2015 summary of Large | "Large estimated that the studied stock value is resilient less than 40 % of cases and, when it is the case, the book replenishment occurs within a time frame of around 20s" | bacry_mastromatteo_muzy_2015.pdf |
| Seasonality limits one kernel to about a day (BMM's reading: 'a whole day'; LC's own abstract: full days fit, longer periods do not) | BMM 2015 summary of Lallouache-Challet | "the intraday seasonality of (mainly) the exogenous intensity µ does not allow to fit well a whole day" | bacry_mastromatteo_muzy_2015.pdf |
| Power-law kernel is a solid fact | BMM 2015, sec. 3.1 | "the power-law nature of Hawkes kernels remains a solid empirical fact which, at least, calls to question all the approaches based on exponential Hawkes models" | bacry_mastromatteo_muzy_2015.pdf |
| E-mini kernel power law | Hardiman-Bercot-Bouchaud 2013 | "we find that the Hawkes kernel is power-law with a decay exponent close to −1.15 at short times" | hardiman_bercot_bouchaud_2013.pdf |
| E-mini critical | Hardiman-Bercot-Bouchaud 2013 | "we find that the Hawkes kernel integrates to unity independently of the analysed period, from 1998 to 2011" | hardiman_bercot_bouchaud_2013.pdf |
| Power law via sums of exponentials | Hardiman-Bercot-Bouchaud 2013, fn. 1 | "By approximating with a sum of exponentials we can take advantage of a recurrence relation which reduces the time complexity of the log-likelihood calculation in Eq. (14) from O(N 2 ) to O(N )" (footnote; two-column layout interleaves it in the -layout .txt; verified with plain pdftotext, which reads "advan- tage") | hardiman_bercot_bouchaud_2013.pdf |
| Endogeneity rose 1998-2010 | Filimonov-Sornette 2012 | "with only 70% in 1998 to less than 30% since 2007 of the price changes resulting from some revealed exogenous information" | filimonov_sornette_2012.pdf |
| Spurious criticality from regime shifts | Filimonov-Sornette 2015 | "the calibration of the Hawkes process on mixtures of pure Poisson process with changes of regime leads to completely spurious apparent critical values for the branching ratio (n ≃ 1) while the true value is actually n = 0" | filimonov_sornette_2015_apparent.pdf |
| Timestamp quality matters | Filimonov-Sornette 2015 | "the decrease of quality of the timestamps of tick data due to latency and grouping of messages to packets by the stock exchange" | filimonov_sornette_2015_apparent.pdf |
| Moment estimator of n | Hardiman-Bouchaud 2014 | "Our estimator requires knowing only the mean and variance of the event count in a sufficiently large time window" | hardiman_bouchaud_2014_branching.pdf |
| Most fits not significant | Lallouache-Challet 2016 | "Many fits of Hawkes processes to financial data look rather good but most of them are not statistically significant." | lallouache_challet_2016.pdf |
| FX endogeneity about 0.8 | Lallouache-Challet 2016 | "endogeneity factor is high but sub-critical at about 0.8" | lallouache_challet_2016.pdf |
| Buy/sell cross terms null (FX) | Lallouache-Challet 2016 | "Using multivariate Hawkes process to fit the arrival and the reciprocal influence of buy and sell trades systematically yields null cross-terms." | lallouache_challet_2016.pdf |
| MLE fixes marginals not independence | Lallouache-Challet 2016 | "The maximum-likelihood estimation, by construction, tends to maximize the exponential nature of the θs, but not their independence." | lallouache_challet_2016.pdf |
| Time-rescaling theorem | Brown et al. 2002 | "Then the L ( u k ) ’s are a Poisson process with unit rate." (L = Lambda, mangled glyph; symbols restored: ’s, ∈, =, ∫, "fi" ligature) | brown_etal_2002_rescaling.pdf |
| KS bands | Brown et al. 2002 | "the 95% (99%) confidence bounds are well approximated as bk ± 1.36 / n1/2 (bk ± 1.63 / n1/2 )" (the text file renders ± as §) | brown_etal_2002_rescaling.pdf |
| Signature-plot price model | Bacry et al. 2013 | "we can reproduce microstructure noise (i.e. strong microscopic mean reversion at the level of seconds to a few minutes) and the Epps effect" | bacry_delattre_hoffmann_muzy_2013.pdf |
| Excitation at 0.3 ms | Bacry-Jaisson-Muzy 2016 | "the volume of the kernel is localized around the reaction time of the market (on our data 0.3 milliseconds)" | arxiv_1412_7096.pdf |
| Market orders more exogenous | Bacry-Jaisson-Muzy 2016 | "market orders are more exogenous than limit and cancel orders" | arxiv_1412_7096.pdf |
| Pure Hawkes ignores book state | Bacry-Jaisson-Muzy 2016 | "the arrival of events does not directly depend on the state of the order book but only on the past events" | arxiv_1412_7096.pdf |
| Refill after market orders | Muni Toke 2011 | "after a market order, a limit order is likely to be submitted more quickly than it would have been without the market order" | toke_2011_marketmaking.pdf |
| Volume and timing not independent | Rambaldi-Bacry-Lillo 2017 | "simple models assuming the independence between volume and time are not suitable to describe the data" | rambaldi_bacry_lillo_2017.pdf |
| News-driven exogenous term | Rambaldi-Pennesi-Lillo 2015 | "the model is able to capture the increase of trading activity after the news" | rambaldi_pennesi_lillo_2015.pdf |
| State-dependent excitation | Morariu-Patrichi-Pakkanen 2022 | "excitation effects in the order flow are strongly state-dependent" | morariu_pakkanen_2022.pdf |
| More exponentials fit better | Martins-Hendricks 2016 | "a sum-of-three-exponentials yielding the best fit to the given set of coupled point processes" | arxiv_1604_01824_multivar_signif.pdf |
| Plain Hawkes loses to 'Last' | Sfendourakis-Muni Toke 2021 | "the standard Hawkes model and the ksdHawkes models are outperformed on more than 90% of the sample" | sfendourakis_toke_2021.pdf |
| Hawkes sign+aggressiveness accuracy 50 % | Muni Toke-Yoshida 2020 | "an accuracy in the range [40%, 60%] for all stocks, with a 50% average" | toke_yoshida_2020.pdf |
| Prediction exercise ignores latency | Muni Toke-Yoshida 2020 | "The exercise is theoretical in the sense that we assume that these computations are instantaneous" | toke_yoshida_2020.pdf |
| Neural TPP benchmark saturating | EasyTPP 2024 | "all the best to-date models make poor predictions on time of future events" | arxiv_2307_08097.pdf |
| Adverse selection without short-term alpha | Cartea-Jaimungal-Ricci 2018 | "HF traders who do not include predictors of short-term-alpha in their strategies are driven out of the market because they are adversely selected by better informed traders" | cartea_jaimungal_ricci_2018_ora.pdf |
| Their P&L is simulated | Cartea-Jaimungal-Ricci 2018 | "we apply a simulation study of the HF strategy where MOs are generated over a period of five minutes" | cartea_jaimungal_ricci_2018_ora.pdf |
| Fill-model bias for large queues | Lokin-Yu 2026 | "fill probabilities are slightly overestimated when the best-bid queue is large" (line break after "best-" in the text file) | lokin_yu_2026_fillprob.pdf |
| Deep survival fill model | Arroyo et al. 2023 | "Our method significantly outperforms those typically used in survival analysis literature." | arroyo_etal_2023_fillsurv.pdf |
| Hawkes beats Poisson on clustering | Jain et al. 2024 | "volatility clustering effect is observed in Hawkes Models" | arxiv_2402_17359.pdf |
| tick speed claim | Bacry et al. 2017 (tick) | "tick outperforms by several orders of magnitudes both hawkes R and PtPack, in particular for large datasets" | bacry_etal_2017_tick.pdf |
| tick current release | PyPI | version 0.8.0.2, upload_time 2026-05-04T15:02:27, requires_python ">=3.11" (JSON fields) | pypi_tick.json |
| MBO keyed by order ID, queue position | Databento docs | "provides every order book event across every price level, keyed by its order ID. This allows you to determine the queue position of each order" | databento_mbo_schema.html |
| MBP-10 event actions and depth | Databento docs | "The event action. Can be A dd, C ancel, M odify, clea R book, or T rade." | databento_mbp10_schema.html |
| TBBO trade aggressor side | Databento docs | "provides every trade event alongside the BBO immediately before the effect of each trade" | databento_tbbo_schema.html |
| Nanosecond event timestamp | Databento docs | "The matching-engine-received timestamp expressed as the number of nanoseconds since the UNIX epoch." | databento_mbo_schema.html |
| Cloud price, 1x A10 | Lambda pricing | "NVIDIA A10 24 GB 30 226 GiB 1.3 TiB SSD $1.29" | lambda_pricing.html |

Measured results (synthetic, this brief): `work/C2_Hawkes/C2_bench_results.json` (keys `hand`, `hb_estimator`,
`fill_prob`, `spurious`, `speed_python`, `speed_tick`, `speed_tick_py312_errors`), `C2_multi_results.json`,
`C2_examples.json`; logs `C2_bench.log`, `C2_bench_py311.log`.

---

## Gaps, failures and route log

- arXiv API (export.arxiv.org/api) returned HTTP 429 after 7 queries at about 02:23 PDT (shared with other readers);
  switched to WebSearch for discovery. arxiv.org/pdf downloads kept working.
- HAL (hal.science) returned a bot-check page for Lu and Abergel (2018); file deleted, paper not read; claims from it
  are marked [unverified].
- epubs.siam.org returned 403 for Cartea-Jaimungal-Ricci; Scrapling not used on SIAM (publisher site, terms not
  checked); the Oxford ORA copy was used instead.
- Large (2007) is paywalled; no author copy found in two searches; its content is cited only through BMM (2015).
- Ogata (1978) and Ozaki (1979) not fetched; the recursion is quoted from secondary sources.
- tick 0.8.x learners fail on this machine (details in section 10). Not debugged; any use of tick needs a fix or an
  older Python with an old tick build, which is not available as Linux wheels.
- numba is not installed in the project environment; compiled-loop speed-ups are [unverified].
- MES event counts per day, markout standard deviations and pilot fills per day are unknown until Part B; all sample
  sizes above are conditional on assumed values.
- No out-of-sample, cost-inclusive trading result with a Hawkes model was found in 10 searches; this is a gap in the
  search, not evidence of absence.
- WebSearch calls used: 10 of 60. No budget notice was received.
- One fetch mislabelled at first (arXiv 1010.5136 is Abergel-Jedidi, not Muni Toke); renamed and logged.

## Corrections after review (Stage E.28, MathReviewer G2)

- MG2-01: Lallouache-Challet attribution rewritten (a whole day fits with two or three exponentials, not two consecutive days; limit attributed to intraday non-stationarity); evidence-table label changed to match.
- MG2-02: Hardiman-Bouchaud eq. (4) now stated as Lambda / (1 - n)^2 with the Fano limit following after dividing by Lambda.
- MG2-03: BJM 0.3 ms restated as the fast, localized kind of influence, no share claimed (section 3 text and the verdict-table row).
- MG2-04: configuration count corrected to 8 to 13 if all six run, 7 to 12 without H-C2-4.
- MG2-05: Python 3.13 and tick 0.8.0.1 failures marked [unverified: not logged]; only 3.11 and 3.12 with 0.8.0.2 stated as logged.
- MG2-06: index range [D, i,j=1] bracketed in both Proposition 1 quotes.
- MG2-07: declared symbol and ligature restorations added at the BDHM eqs. (6)-(7), Brown theorem, KS-band and time-rescaling table quotes.
- MG2-08: BMM eq. (8) described as omitting the mu term instead of "written with mu = 0".
- MG2-09: multivariate-recursion qualifier replaced (distinct decays keep D^2 accumulators, still linear in N).
- MG2-10: simulation description corrected (rate drawn afresh from {0.3, 3.0} per 300 s segment).
- MG2-11: intraday-profile and many-events-per-message claims marked as background, reader's knowledge.
- MG2-12: "right (0.80)" replaced by "within 0.01 of the truth (exact finite-window values 0.795 and 0.800)".
- MG2-13: NPHC reason corrected to tested at d = 10 to 100; verdict "skip" unchanged.
- MG2-14: Toke-Yoshida line reference changed to 943-951.
