# E.28 methods brief, deep dive C2: limit-order-book models and the mathematics of fill probability

Worker: C2_LOB (Opus 5.5, Stage E.28 reader). Started 2026-10-21 02:21 PDT. Written section by section.
Pages: reports/stage_e28_briefs/pages/C2_LOB/ (log.tsv lists URL, UTC and PDT fetch time, method, sha256).
Scripts: reports/stage_e28_briefs/work/C2_LOB/ (C2_LOB_cst_cdl.py and the other C2_LOB_*.py files compute
every worked example below; run them with the project venv python, `-I`).

No market data was read. No rule is tested here. Trial-count figures are what each hypothesis WOULD add to N if the
lead chose to register it; whether a descriptive calibration test counts toward N is the lead's decision, not this
brief's.

## 0. Notation and the pilot quantities used throughout

- Tick size delta. For MES the tick is 0.25 index points and one point is $5, so one tick is $1.25 per contract
  (contract specification; not re-fetched for this brief, other workers hold the CME pages).
- Best bid price B, best ask price A, spread S = (A - B)/delta in ticks, mid M = (A + B)/2.
- q_b, q_a: displayed size (contracts) at the best bid and ask. With mbo data, the queue is a list of individual
  orders in time priority; with mbp-10 it is only the aggregate size at each of 10 levels.
- A "1-lot passive order" in the pilot is a virtual buy at B (or sell at A), joined at the back of the queue at
  time t0. Its outcomes: filled or not within horizon H; time to fill tau; markout after fill at h = 1, 10, 60 s,
  defined for a buy as m_h = M(t_fill + h) - B (in ticks; a sell is the mirror image). A negative mean markout is
  adverse selection.
- Back-of-queue position: Q_ahead(t) = number of contracts ahead of the virtual order. FIFO fill condition
  (CME FIFO products, section 9): the order fills when Q_ahead reaches 0 and a further aggressive sell trades at B.
- Poisson rate notation follows each paper. "Event" means a limit-order arrival, a cancellation or a market order.

The single most important data fact for every method below: models that need the queue AHEAD of a specific order
(fill probability, queue value, survival models) need either mbo data (order-by-order, so cancellations ahead of us
are observed) or an assumption about where cancellations happen inside an aggregated mbp-10 level. Section 11
lists the formulas and which schema identifies each.

---

## 1. Cont, Stoikov and Talreja (2010): birth-death queue model and Laplace-transform probabilities

Source: Cont, R., Stoikov, S., Talreja, R. (2010), "A stochastic model for order book dynamics", Operations
Research 58(3), 549-563. Full text: author preprint saved as `cst_2010_try1.pdf` / `.txt` (21 pages).

### 1.1 Core idea
Treat each price level of the book as a queue. Limit orders arrive as Poisson processes (births), market orders and
cancellations remove orders (deaths). Because all events are independent Poisson streams, the best-bid and best-ask
queues evolve, until the mid-price first moves, as two independent birth-death processes. Questions such as "will
the next mid move be up?" and "will my order at the bid fill before the mid moves?" become first-passage problems
for birth-death processes, which have closed-form Laplace transforms (continued fractions). Numerical inversion of
those transforms gives the probabilities without simulation.

### 1.2 Equations (with every term)
Assumptions (paper section 2, quoted in the evidence table): unit order size (the size unit is the average limit
order size S_l); for i >= 1 ticks from the opposite best quote,
- limit buy (sell) orders arrive at rate lambda(i);
- market buy (sell) orders arrive at rate mu;
- each resting order at distance i is cancelled at rate theta(i), so a level holding x orders loses orders to
  cancellation at total rate theta(i) * x;
- all these streams are mutually independent.
The paper suggests lambda(i) = k / i^alpha (power law). The book state X(t) is then a continuous-time Markov chain
(Proposition 1: ergodic, has a stationary distribution).

Estimators (paper section 3.2), sample length T in minutes:
- lambda_hat(i) = N_l(i) / T, where N_l(i) is the count of size increases at distance i (i <= 5), then fit
  k, alpha by least squares: min over (k, alpha) of sum_{i=1..5} (lambda_hat(i) - k / i^alpha)^2.
- mu_hat = N_m * S_m / (T * S_l), N_m = number of market orders, S_m their average size.
- theta_hat(i) = N_c(i) * S_c / (T * Q_i * S_l) for i <= 5 (theta_hat(i) = theta_hat(5) beyond), where N_c(i) is
  the count of size decreases at distance i not caused by trades, S_c the average cancel size, and Q_i the average
  queue size at distance i in units of S_l.
For Sky Perfect Communications (Tokyo SE) Table 2 gives lambda_hat(1..5) = 1.85, 1.51, 1.09, 0.88, 0.77;
theta_hat(1..5) = 0.71, 0.81, 0.68, 0.56, 0.47; mu_hat = 0.94; k = 1.92; alpha = 0.52 (per minute, sizes in units
of S_l).

First-passage machinery (paper section 4.1):
- Two-sided Laplace transform of a random variable X: f_hat(s) = E[exp(-s X)]. For independent X, Y,
  f_hat_{X+Y}(s) = f_hat_X(s) * f_hat_Y(s) (paper eq. 3).
- For a birth-death process with birth rate lambda and death rate mu_i in state i, let sigma_b be the first-passage
  time from state b to 0. It is a sum of independent one-step-down passage times,
  sigma_b = sigma_{b,b-1} + ... + sigma_{1,0}, so f_hat_b(s) = prod_{i=1..b} f_hat_{i,i-1}(s) (eq. 5), with
  f_hat_{i,i-1}(s) = -(1/lambda) * Phi_{k=i..inf} [ -lambda*mu_k / (lambda + mu_k + s) ] (eq. 6, from Abate and
  Whitt 1999 eq. 4.9). Phi denotes a continued fraction: Phi_{n} a_n/b_n = a_1/(b_1 + a_2/(b_2 + ...)).
- In the book model at spread S, the queues have birth rate lambda(S) and death rate mu + i*theta(S) in state i
  (Lemma 2), giving f_hat_{j,S}(s) in eq. (9).

Result A, probability that the next mid move is UP (Proposition 3). With a orders at the ask, b at the bid, spread
S, and Lambda_S = sum_{i=1..S-1} lambda(i) (the rate at which some order arrives inside the spread),
P[mid up first] is the inverse Laplace transform evaluated at 0 of eq. (10); for S = 1 it reduces to
  F_hat_{a,b,1}(s) = (1/s) * f_hat_{a,1}(s) * f_hat_{b,1}(-s)            (eq. 11)
Derivation summary: for S = 1, the mid moves when either queue first hits 0, so the probability is
P[sigma_A < sigma_B] = P[sigma_A - sigma_B < 0]; the transform of sigma_A - sigma_B is f_hat_a(s) f_hat_b(-s) by
independence, and dividing by s turns a density transform into a CDF transform, evaluated at 0.

Result B, probability that an order placed at the bid fills before the mid moves (Proposition 5, "given the order is
not cancelled"). The order's own waiting time zeta_B is the time for the b orders counted at the bid (the last of
which is ours, and never cancels) to be removed; it is a sum of independent exponentials with rates
mu + theta(S)(i-1), i = 1..b, so
  g_hat_{b,S}(s) = prod_{i=1..b} (mu + theta(S)(i-1)) / (mu + theta(S)(i-1) + s)      (eq. 14)
and, for S = 1,
  F_hat_{a,b,1}(s) = (1/s) * g_hat_{b,1}(s) * f_hat_{a,1}(-s)            (eq. 16)
inverted at 0 gives P[zeta_B < sigma_A].

Result C, "making the spread" (Proposition 6): probability that a bid and an ask order both fill before the mid
moves, h_{a,b} + h_{b,a}, eq. (18)-(21), involving Poisson probabilities and a matrix exponential. Table 5 shows it
is not monotone in b for fixed a.

### 1.3 Data needed; is one CME contract's Databento data for 4-12 months enough?
- Estimation needs, per level, counts of size increases, decreases not caused by trades, and trades: mbp-10 is
  enough (the paper itself used 5-level Tokyo data, and it says it could NOT validate Result B empirically because
  "our data set does not allow us to track specific orders").
- Validating Result B (fill before move) needs order tracking: mbo, or a virtual order on mbp-10 under an assumed
  cancellation-position rule. tbbo (top of book at each trade) is not enough for cancellations.
- Volume: the parameters are a handful of rates; even one week of a liquid future gives many thousands of events per
  level. 4 months is ample for estimation; 4-12 months matters only for regime splits.

### 1.4 What it estimates or decides
Conditional probabilities of the next mid move, of fill before move, and of round-trip capture, as functions of
(q_a, q_b, S). It can decide: join the queue or not; choose bid versus ask; it does NOT model adverse selection
after the fill (the model has no information content in order flow; every move is mechanical depletion).

### 1.5 Worked example (computed; script C2_LOB_cst_cdl.py, C2_LOB_cst_big.py)
I solved the S = 1 problems exactly as absorbing Markov chains (queues truncated at 80-120 units) instead of
inverting Laplace transforms, using the paper's Table 2 rates lambda(1) = 1.85, mu = 0.94, theta(1) = 0.71.
- Mid-up probability, (bid b, ask a): (b=2, a=1) 0.665 vs the paper's Laplace value 0.664; (3,1) 0.741 vs 0.741;
  (5,1) 0.812 vs 0.812; (1,2) 0.335 vs 0.336; (1,5) 0.188 vs 0.188. Result A reproduces to three decimals.
- Fill-before-move (Result B): my exact solve under the stated assumptions gives (b=1, a=1) 0.503 vs the paper's
  0.497; (1,5) 0.882 vs 0.776; (3,1) 0.291 vs 0.206; (5,5) 0.607 vs 0.393. I could NOT reproduce Table 4. I tried
  three readings (our order behind b others; no cancellations ahead; our own cancellation counted as failure); none
  matches (script C2_LOB_cst_variants*.py). Either Table 4 used other parameters or the model differs from the text
  in a way I could not find. Consequence for a pilot: re-derive Result B from the model and validate it on the
  pilot's own fills; do not copy Table 4.
- Illustration of queue length (my exact solve, same rates; rows b = units at the bid including ours, columns
  a = 1, 5, 10, 20 at the ask): b = 1: 0.50, 0.88, 0.95, 0.98; b = 5: 0.22, 0.61, 0.77, 0.89; b = 20: 0.11, 0.34,
  0.49, 0.65. Joining the back of a long queue opposite a short one gives a low chance of filling before the price
  moves.
- Arithmetic of the bad case. Suppose the order fills only because the bid queue is exhausted by sell market
  orders. Before: bid B, ask B + 1 tick, mid B + 0.5. After depletion the bid is B - 1 tick and (one-tick spread) the
  ask is B, mid B - 0.5. A buy filled at B shows an immediate markout of (B - 0.5) - B = -0.5 tick = -$0.625 on one
  MES contract, before fees. In the CST model this is the "fill then move" path; Result B counts only fills that
  happen before the move.

### 1.6 Testable, pre-registerable hypothesis from the pilot
- H1 (calibration): "CST Result B, with rates estimated on the first 2 months, predicts the fill-before-mid-move
  outcome of back-of-queue 1-lot virtual orders in the following 2 months better than the unconditional fill rate."
- Statistic: Brier score difference D = mean((y - p_CST)^2) - mean((y - p_bar)^2), y = 1 if filled before the mid
  moves; one-sided test of D < 0 with a block bootstrap by day; plus a calibration slope (logistic regression of y on
  logit p_CST; slope 1, intercept 0 is perfect).
- Sample: to estimate a probability near 0.3 within +/-0.02 at 95%, n = 1.96^2 * 0.3 * 0.7 / 0.02^2 = 2,017
  roughly independent placements; placing one virtual order every 5 minutes for 23 hours on 80 trading days gives
  80 * 276 = 22,080 placements, enough even after heavy dependence (effective n / 10).
- Configurations added to N: 1 (one fixed model, one fixed rate-estimation window). Adding the S > 1 variants or
  re-estimation frequencies multiplies it.

### 1.7 Compute
Rate estimation is counting; Laplace inversion or the absorbing-chain solve takes well under a second per state on
the laptop (one 6,400-state sparse solve took 0.68 s wall time including Python start-up, in Python/SciPy). No GPU, no cloud.

### 1.8 Evidence on retail scale and latency
- The paper is in-sample on one Tokyo stock and validates only Result A against empirical frequencies (Table 3); it
  states that fill-before-move probabilities "are not obtainable" from its data. No cost-inclusive or
  out-of-sample trading result.
- Its own discussion of making the spread is a probability, not a P&L; the model has no adverse-selection channel,
  so it cannot say whether a fill is profitable. Lehalle and Mounjid (section 12) show why that omission matters.
- No evidence found on futures or at retail latency.

---

## 2. Cont and de Larrard (2013): Markovian limit order market (level-1 queue model)

Source: Cont, R., de Larrard, A. (2013), "Price dynamics in a Markovian limit order market", SIAM Journal on
Financial Mathematics 4(1), 1-25. Full text: arXiv 1104.4596, saved as `cont_delarrard_2013_markovian.pdf/.txt`.

### 2.1 Core idea
Keep only the best bid and best ask queues (level 1), assume a one-tick spread, and let each queue be a
birth-death process (limit orders at rate lambda, market orders plus cancellations at rate mu + theta). When one
queue empties, the price moves one tick and both queues restart from a random draw (from distribution f after an
up-move, f~ after a down-move), which stands for the depth that was sitting behind. The price becomes a
semi-Markov process whose jump direction and timing depend on queue sizes. Volatility at coarse scales follows from
order-flow rates and depth.

### 2.2 Equations
- Duration until the next price change, starting from ask a and bid b (Proposition 1, eq. 3-4):
  P[tau > t | q_a = a, q_b = b] = ((mu + theta)/lambda)^((a+b)/2) * psi_{a}(t) * psi_{b}(t),
  psi_n(t) = integral from t to infinity of (n/u) * I_n(2 u sqrt(lambda (theta + mu))) * exp(-u (lambda + theta + mu)) du,
  where I_n is the modified Bessel function of the first kind. Derivation: each queue is a birth-death walk; the
  Laplace transform of its hitting time of 0 from x is L(s, x) = [((lambda+mu+theta+s) - sqrt((lambda+mu+theta+s)^2
  - 4 lambda (mu+theta))) / (2 lambda)]^x (root below 1 of the quadratic from the one-step recursion); the two queues
  are independent until tau, so the survival functions multiply.
- Tail: if lambda < mu + theta, P[tau > t] ~ x y (lambda + mu + theta)^2 / (lambda^2 (mu + theta - lambda)^2 4 t^2)
  (eq. 5) (as printed; eq. (5) is not consistent with (3)-(4): for lambda < mu + theta the tail is exponential with
  rate (sqrt(mu+theta) - sqrt(lambda))^2, only 0.02 per unit time for the paper's 12 vs 13 example, which is why
  Figure 3 looks like a power law over its plotted range; the mean duration is finite. Not used by any pilot
  quantity); if balanced, lambda = mu + theta, P[tau > t] ~ x y / (pi lambda t) (eq. 6), infinite mean duration.
- Probability the next move is UP, balanced case (Proposition 2, eq. 7), bid n, ask p:
  phi(n, p) = (1/pi) integral_0^pi (2 - cos t - sqrt((2 - cos t)^2 - 1))^p * sin(n t) cos(t/2) / sin(t/2) dt.
  Derivation: in the balanced case the pair (q_b, q_a) is a symmetric simple random walk on the quadrant observed at
  Poisson times; phi is the discrete harmonic function with phi(0, p) = 0 and phi(n, 0) = 1 (discrete Dirichlet
  problem, eq. 8, solved via Lawler and Limic). It does not depend on the rates at all.
- Continuum approximation (my derivation, not in the paper): for large queues the walk is close to a planar
  Brownian motion with independent equal-variance coordinates; the harmonic function on the quadrant that is 1 on
  the q_a = 0 axis and 0 on the q_b = 0 axis is linear in the polar angle, giving
  phi(n, p) ~ (2/pi) * arctan(n / p).
- Volatility (Theorem 1, eq. 13): at time scales much longer than tau_0 = 1/lambda, the price diffuses with
  sigma = delta * sqrt(n * pi * lambda / D(f)), where n solves n ln n * tau_0 = tau_2 (the number of events over
  the horizon tau_2) and D(f) is a depth measure of the queues after a price change (paper eq. 9).

### 2.3 Data; enough?
Level-1 queue sizes and event counts: tbbo is not enough for cancellations, mbp-1 or mbp-10 is enough (mbp-10
also gives the depth behind the best quote, which the paper's f distribution needs). 4 months of one contract is
ample for lambda, mu + theta and f. Order tracking (mbo) is not needed for the price-move results.

### 2.4 What it estimates or decides
Next-move direction and the waiting time to the next move from (q_b, q_a); a volatility estimate from order-flow
rates. For a passive order it gives the hazard of the queue being depleted, which is the adverse-selection event of
section 1.5.

### 2.5 Worked example (computed; C2_LOB_cst_cdl.py)
- eq. 7 versus the arctan approximation: phi(2, 1) = 0.6977 vs 0.7048; phi(5, 2) = 0.7560 vs 0.7578;
  phi(3, 10) = 0.1860 vs 0.1855; phi(300, 100) = 0.7952 vs 0.7952; phi(50, 450) = 0.0704 vs 0.0704.
  The arctan form is exact to 4 decimals at the queue sizes an index future shows, so a pilot can use it directly.
- Hypothetical MES-like case (illustrative numbers, NOT measured; the pilot will measure them): bid 300 lots,
  ask 100 lots, in units of one lot. phi(300, 100) = (2/pi) arctan(3) = 0.6366 * 1.2490 = 0.795. The chance that
  the bid side is depleted first is 0.205. A buy joined at the back of that 300-lot bid fills for sure on that path
  and then, by the arithmetic of 1.5, marks out at about -0.5 tick = -$0.625 immediately after.
- Paper's own numerical example: lambda = 12, mu + theta = 13 (the source gives no time unit), q_a = 4, q_b = 5,
  Pareto tail of the duration decaying as t^-2 as printed in eq. (5) (Figure 3; see the flag after eq. 5 in 2.2).

### 2.6 Testable hypothesis
- H2 (direction): "On the pilot's held-out months, (2/pi) arctan(q_b/q_a) predicts the sign of the next mid change
  with Brier score below 0.25 (coin flip) and with calibration slope within [0.8, 1.2]."
- Statistic: Brier score and its block-bootstrap CI by day; calibration regression. Sample: every mid change is an
  observation; a liquid index future gives far more than 10,000 per month, so power is not a problem; dependence is
  handled by the day blocks.
- N: 1 (no free parameter). This is a descriptive check of a necessary condition (queue imbalance is informative),
  not a trading rule; the lead decides whether it counts.

### 2.7 Compute
Quadrature of eq. 7 or arctan per event; trivial on the laptop.

### 2.8 Evidence at retail scale
- Empirical support in the paper is a visual comparison for Citigroup on one day (26 June 2008); the paper reports
  lambda slightly below mu + theta for Citigroup, GE and GM ("the difference is small"). In-sample, equities, no
  costs, no trading test.
- The model's prediction is about price moves, not about profit: knowing that the price moves up with probability
  0.8 is worth nothing to a passive trader who cannot get filled ahead of the queue (section 6) and nothing to an
  aggressive trader who pays the spread (section 4.8).

---

## 3. Huang, Lehalle and Rosenbaum (2015): the queue-reactive (QR) model, and later extensions

Source: Huang, W., Lehalle, C.-A., Rosenbaum, M. (2015), "Simulating and analyzing order book data: the
queue-reactive model", Journal of the American Statistical Association 110(509), 107-122. Full text: arXiv
1312.0563v2, saved as `huang_lehalle_rosenbaum_2015_qr.pdf/.txt`.

### 3.1 Core idea
Same queueing view as CST, but the arrival intensities are no longer constants or simple power laws: each event
type's intensity at queue i is an arbitrary function of that queue's current size ("queue-reactive"). The functions
are estimated non-parametrically from data, one value per queue size. The model runs inside periods where a
reference price p_ref is constant; when p_ref moves, queues shift and, with probability theta_reinit, the whole
book is redrawn from its stationary distribution (exogenous information). The result is a realistic market
simulator for large-tick assets, used for execution-probability and transaction-cost analysis.

### 3.2 Equations
- State: q = (q_{-K}, ..., q_{-1}, q_1, ..., q_K), queue sizes at K levels each side of p_ref (K = 3 in the paper),
  measured in units of AES_i, the average event size at level i (paper section 2).
- Model I (independent queues, paper section 2.3.1): at queue i with size n, limit orders arrive at intensity
  lambda^L_i(n), cancellations at lambda^C_i(n), market orders at lambda^M_i(n); births f_i(q) = lambda^L_i(q_i),
  deaths g_i(q) = lambda^C_i(q_i) + lambda^M_i(q_i). Each queue is a birth-death process with state-dependent rates.
- Estimator (paper section 2.3.2, maximum likelihood for a piecewise-constant intensity): for every event omega at
  queue i, record the waiting time Delta t_i(omega) since the previous event at that queue, its type T_i(omega) in
  {E+ insertion, E- cancellation, E^t trade} and the queue size q_i(omega) before it. Then
  Lambda_hat_i(n) = [ mean(Delta t_i(omega) | q_i(omega) = n) ]^(-1)        (total event rate at size n)
  lambda_hat^L_i(n) = Lambda_hat_i(n) * #{T_i = E+, q_i = n} / #{q_i = n}
  lambda_hat^C_i(n) = Lambda_hat_i(n) * #{T_i = E-, q_i = n} / #{q_i = n}
  lambda_hat^M_i(n) = Lambda_hat_i(n) * #{T_i = E^t, q_i = n} / #{q_i = n}.
  Derivation summary: with exponential waiting times at a constant total rate Lambda in state n, the MLE of Lambda
  is 1 / mean waiting time, and the MLE of each type's share is its empirical frequency.
- Models IIa/IIb: intensities at level 2 also depend on whether level 1 is empty; bid-ask dependence.
- Model III (QR proper, section 3.1): p_ref moves by one tick with probability theta when the mid moves and the
  best queue is empty; with probability theta_reinit the book is redrawn from its invariant distribution.
  theta and theta_reinit are calibrated to the 10-minute volatility and the mean-reversion ratio
  eta = N_c / (2 N_a) (continuations over twice alternations). France Telecom values used later: theta = 0.7,
  theta_reinit = 0.85.
- Fill probability (section 2.5): a buy order of size n0 joined at Q_{-1} fills only after all orders placed before
  it are executed or cancelled. Because the aggregate data do not identify which order cancels, the paper adds
  Assumption 3 (every resting order other than ours is equally likely to be the one cancelled) and Assumption 4
  (the cancellation intensity hitting the others is lambda^C_1(q_{-1}) * (q_{-1} - n0)/q_{-1}), then computes the
  fill-before-move probability by Monte Carlo.

### 3.3 Data; enough?
- Intensity estimation needs every change of each queue with its type: mbp-10 identifies size increases, decreases
  and trades per level (trades flagged by the trade messages), so mbp-10 is enough for Model I/II/III. mbo is better
  because it also tells which order cancelled, removing the need for Assumptions 3-4 (the paper says this directly:
  "we would need more detailed market data keeping records of the identifiers of the submitted and canceled
  orders").
- Volume: one value per (level, queue size in AES, event type); with queues in the hundreds of AES units on an index
  future, many queue-size bins will be sparse at the tails; 4 months of one contract gives plenty of events near the
  modal queue sizes. Extensions calibrate on comparable samples: Bodor and Carlier (2025) used Bund futures over
  three months (March to June 2022).

### 3.4 What it estimates or decides
A simulator, not a forecast. It estimates the fill probability and time-to-fill of a hypothetical order at any queue
position, the distribution of the mechanical price path, and pre-trade cost of a placement policy. It decides
placement (join, wait, cancel) only through simulation.

### 3.5 Worked example (estimator arithmetic; hypothetical counts, C2_LOB_examples2.py)
Suppose at the best bid, among events that occurred when the queue held n = 5 AES, there were 2,000 events with
mean waiting time 0.25 s, of which 900 insertions, 700 cancellations and 400 trades. Then
Lambda_hat(5) = 1/0.25 = 4.00 per s; lambda^L = 4 * 900/2000 = 1.80; lambda^C = 4 * 700/2000 = 1.40;
lambda^M = 4 * 400/2000 = 0.80 per s. If our 1-unit order sits in a queue of 10 units, Assumption 4 applies the
cancellation intensity 1.40 * (10 - 1)/10 = 1.26 per s to the 9 others. The paper notes that orders with lower
priority are in fact more likely to be cancelled (Gareche et al. 2013), so this uniform assumption overstates the
cancellations ahead of us and "execution probabilities might be slightly overestimated".

### 3.6 Testable hypothesis
- H3 (simulator fidelity for fills): "A Model I QR simulator fitted on the pilot's training months predicts the
  held-out empirical fill-within-H rate of back-of-queue 1-lot virtual orders (H = 10 s and 60 s) within the 95%
  interval, and does so better than a constant-rate (CST-style Poisson) model."
- Statistic: for each queue-size bucket, the difference between simulated and observed fill rates; a chi-square
  goodness-of-fit over buckets, plus the Brier score of the simulated probability per placement versus the Poisson
  model. HLR's own Figure 9 says the Poisson model "clearly overestimates" execution probabilities; the pilot can
  test whether that holds on a CME future.
- Sample: same placements as H1 (about 22,000 over 80 days); simulation draws per placement (for example 1,000) are
  cheap.
- N: 1 per frozen model variant (Model I only). Each extension (Hawkes term, order sizes, deep QR) adds 1.

### 3.7 Compute
Model I estimation is counting (seconds on the laptop for months of data once the events are extracted). Monte
Carlo of fill probabilities: about 10^3 paths per placement times 2 x 10^4 placements is 2 x 10^7 short paths;
vectorized NumPy on the laptop, minutes to an hour. The deep extension (MDQR, Bodor and Carlier 2025) trains a
neural network with early stopping ("Training termination after 10 consecutive epochs without improvement"); a
network of that kind on 3 months of one futures contract fits on the RTX 3050 (4 GB) in my judgment, but the paper
does not report hardware or training time, so this is [unverified].

### 3.8 Extensions (each read in full text, abstracts quoted in the evidence table)
- Wu, Rambaldi, Muzy and Bacry (2019), queue-reactive Hawkes models (arXiv 1901.08938): add self-exciting Hawkes
  terms to QR intensities; on Eurex Bund and DAX level-1 data "the Hawkes term dramatically improves the pure
  Queue-Reactive model" for inter-event times and queue distributions. Relevant because CME futures order flow is
  bursty; a QR fitted on MES without Hawkes terms will likely misstate short-horizon fill probabilities.
- Bodor and Carlier (2024), order sizes (arXiv 2405.18594): intensities and order SIZES both depend on book state;
  on German bond futures the extended model "significantly improves the description of order flow properties".
- Bodor and Carlier (2025), Multidimensional Deep QR (arXiv 2501.08822): neural intensities with cross-queue
  dependence; Bund futures, 3 months.
- Sfendourakis (2025), multi-dimensional QR with a hidden efficient price (arXiv 2506.11843): MLE procedure and a
  liquidation backtest.

### 3.9 Evidence on retail scale
- All QR papers are simulators judged on stylized facts (queue distributions, volatility, inter-event times), not on
  trading P&L. HLR report a "maximal mechanical volatility" of 5 bps against 14 bps empirical for France Telecom:
  the pure order-book model cannot generate the observed volatility without exogenous resets.
- No paper found that shows a QR-derived passive strategy profitable after costs out of sample, at any latency.
- The models are aimed at execution cost analysis for a broker (Kepler Cheuvreux, CFM and BNP Paribas
  affiliations), which is a different use from a retail prop account seeking positive expected value.

---

## 4. Queue imbalance as a one-tick-ahead predictor (Gould and Bonart 2016)

Source: Gould, M. D., Bonart, J. (2016), "Queue imbalance as a one-tick-ahead price predictor in a limit order
book", Market Microstructure and Liquidity 2(2), 1650006. Full text: arXiv 1512.03492, saved as
`gould_bonart_2016_qi.pdf/.txt`.

### 4.1 Core idea
The relative size of the best bid and best ask queues predicts the direction of the next mid-price move. Fit a
logistic regression of "next move is up" on the imbalance. It works far better for large-tick stocks (thick queues,
one-tick spread), which is the regime of MES and most CME index futures.

### 4.2 Equations
- Queue imbalance (eq. 7): I(t) = (n_b(t) - n_a(t)) / (n_b(t) + n_a(t)), in [-1, 1]; n_b, n_a are the volumes at
  the best bid and ask.
- Target: y_i = 1 if the i-th mid change is up, 0 if down (eq. 9); I_i is I sampled at a uniformly random time
  between the (i-1)-th and i-th mid change (eq. 10).
- Model: y_hat(I) = P(y = 1 | I) = 1 / (1 + exp(-(x0 + x1 I))), fit by maximum likelihood (section 5.3).
- Evaluation: area under the ROC curve (AUC) for binary prediction, and mean squared residual for probabilistic
  prediction, against a null model y_hat = 0.5 whose mean squared residual "is exactly 1/4".
- Link to sections 1-2: in the Cont-de Larrard balanced model P(up) = phi(n_b, n_a) ~ (2/pi) arctan(n_b/n_a), which
  is a deterministic function of I because n_b/n_a = (1 + I)/(1 - I). The logistic fit is a flexible empirical
  version of the same curve.

### 4.3 Data; enough?
Best-level sizes at every mid change: tbbo gives the BBO at trades only (not between trades), so it misses
quote-driven mid changes; mbp-1 or mbp-10 is enough; mbo is more than needed. The paper used 252 days x 100 random
mid changes per day = 25,200 points per stock (80/20 split). One CME index future has far more mid changes per day,
so 4 months is plenty.

### 4.4 What it estimates or decides
The probability that the next mid move is up. For a passive 1-lot it decides WHEN to quote: post a bid only when the
imbalance favours the bid (the price is likely to move away up, which also means the bid is less likely to fill),
or avoid posting a bid when the imbalance is strongly negative (the bid queue is about to be depleted, i.e. the
adverse-selection path of section 1.5).

### 4.5 Worked example (C2_LOB_examples2.py), using the paper's Table 2 estimates
- MSFT (large tick): x0 = 0.01, x1 = 2.49. At I = 0.5: p = 1/(1 + e^-(0.01 + 1.245)) = 1/(1 + e^-1.255) = 0.778;
  at I = 0.9: 0.905; at I = 0: 0.502.
- GOOG (small tick): x0 = 0.03, x1 = 0.54. At I = 0.5: 0.574; at I = 0.9: 0.626.
- Out-of-sample AUC (Table 4): 0.75 to 0.81 for the five large-tick stocks, 0.58 to 0.64 for small-tick stocks.
- Power: under the null (AUC = 0.5) with n1 = n2 = 5,000 up and down moves, the standard error of AUC is about
  sqrt((n1 + n2 + 1)/(12 n1 n2)) = 0.0058, so an AUC of 0.52 is already 3.4 standard errors from 0.5.

### 4.6 Testable hypothesis
- H4 (necessary condition, not a strategy): "On the pilot's held-out months, the logistic imbalance model fitted on
  training months has AUC > 0.5 for the next mid move", AND the trading-relevant version:
  H4b: "Back-of-queue 1-lot bids placed when I > c (c fixed in advance, e.g. 0.5) have a higher mean 10 s markout,
  net of a fixed per-contract fee, than bids placed when I < -c." Statistic: difference of mean markouts (ticks),
  Newey-West t across days (the program's usual t > 3.0 bar). Sample: markouts exist only for filled orders; at
  a guessed 30% fill rate, 22,000 placements give about 6,600 fills split across the two arms.
- N: H4 adds 1 (no free parameter after the logistic fit); H4b adds 1 per threshold c (pre-register one value).

### 4.7 Compute
Logistic regression on 10^5 to 10^6 points: seconds on the laptop.

### 4.8 Evidence on retail scale
- Out-of-sample in the paper means a random 80/20 split of pooled points from the same 252 days, not a
  chronological hold-out, so it does not test stability through time.
- The paper predicts direction, not profit, and has no costs. Its own caveat: performance is an unconditional
  average and "would improve considerably" if one considered only |I| near 1.
- The economic problem for a retail trader: a strong imbalance is public and seen by every faster participant;
  a passive order placed at the favoured side joins a queue that others reached earlier (section 6), and an
  aggressive order pays the spread (one tick on MES, or 2 x 0.5 tick round trip) against a predicted move of one
  tick that happens with probability about 0.8. Expected gross gain of buying at the ask when p_up = 0.8 and the
  next move is +/-1 tick: (0.8 - 0.2) * 1 tick = 0.6 tick per move, measured against the mid; relative to the ask
  paid, the gain is 0.6 - 0.5 = 0.1 tick before fees and before latency (the queue state is stale by the
  time a tens-of-milliseconds order arrives). Lehalle and Mounjid (section 12) quantify the latency loss.

---

## 5. The microprice (Stoikov 2018)

Source: Stoikov, S. (2018), "The micro-price: a high-frequency estimator of future prices", Quantitative Finance
18(12), 1959-1966. The journal full text is closed access (OpenAlex: "closed"), the SSRN copy is blocked to this
machine. Evidence used: the author's talk slides ("Gatheral60" conference, Imperial College host,
`stoikov_gatheral60_slides.pdf/.txt`) and the author's public code repository (README and notebook,
`stoikov_microprice_github_readme.md`, `stoikov_microprice_notebook.ipynb`). Claims not on the slides are marked
[unverified].

### 5.1 Core idea
The mid-price ignores queue sizes, and the size-weighted mid is noisy and can move the wrong way after a
cancellation (slides' example). The microprice is defined as the limit of expected future mid-prices at the times
the mid changes, given the current imbalance and spread; under a Markov assumption it is the mid plus an adjustment
that depends only on (imbalance, spread), computable from a transition matrix estimated on data. It is a martingale
by construction, so it is a fair-value estimate a passive order can be priced against.

### 5.2 Equations (from the slides)
- Information: F_t = (M_t, I_t, S_t), M = (P^b + P^a)/2, S the spread, I_t = Q^b/(Q^b + Q^a) (note: in [0, 1],
  not Gould-Bonart's [-1, 1]).
- Definition: P^micro_t = lim_{i -> inf} P^i_t, with P^i_t = E[M_{tau_i} | F_t] and tau_1, tau_2, ... the
  successive times the mid changes.
- Assumption 2: the dynamics do not depend on the level M_t, so E[M_{tau_1} - M_t | M_t, I_t, S_t] = g^1(I_t, S_t).
- Main result: P^i_t = M_t + sum_{k=1..i} g^k(I_t, S_t), with g^1(I, S) = E[M_{tau_1} - M_t | I, S] and
  g^{i+1}(I, S) = E[g^i(I_{tau_1}, S_{tau_1}) | I, S].
- Discrete Markov implementation: discretize X_t = (I_t, S_t) into n imbalance buckets x m spread values; estimate
  Q_{ij} = P(M_{t+1} - M_t = 0 and X_{t+1} = j | X_t = i) (no mid change), R^1_{ik} = P(M_{t+1} - M_t = k | X_t = i)
  and R^2_{ik} = P(M_{t+1} - M_t != 0 and X_{t+1} = k | X_t = i). Then
  g^1 = (1 - Q)^(-1) R^1 K (K the vector of mid-change sizes) and g^{i+1} = B g^i with B = (1 - Q)^(-1) R^2.
  Convergence holds if B has strictly positive entries, B^k -> W (stationary) and W g^1 = 0; the data are
  symmetrized to guarantee W g^1 = 0. Closed form: P^micro = M + sum_{i>=2} (eigen-terms of B) g^1, written on the
  slides as a spectral decomposition.
- Toy results: (i) if mid moves are independent of I, P^micro = M; (ii) if I is a Brownian motion on [0, 1] and the
  mid jumps or bounces with probability 1/2 at the boundaries, P^micro = M + (I - 1/2) (one-tick spread), which is
  the weighted mid.
- The author's notebook uses n_imb = 10 (and 4) imbalance buckets, n_spread = 2 (and 4), dt = 1.

### 5.3 Data; enough?
BBO prices and sizes sampled on a clock or at events: mbp-1/mbp-10 is enough; tbbo is enough only if one samples at
trades. The slides fit the transition matrices on the first trading day of March 2011 (BAC and CVX) and compare G* with 1, 5
and 10 minute mid changes averaged over the whole month (and on three consecutive days); the calibration day is
inside the validation month.
For one CME index future, 4 months is ample; the state space is 10 x 2 = 20 states.

### 5.4 What it estimates or decides
A fair price inside the spread. For passive orders: where the fair value sits relative to the bid you would join.
A bid at B with microprice P has an expected edge of P - B per fill BEFORE adverse selection from the fill itself;
the slides' summary claims "Micro-price is a good predictor of future mid prices" and "seems to live between the bid
and the ask".

### 5.5 Worked example (C2_LOB_examples2.py)
Under the Cont-de Larrard balanced model with a symmetric reset after each move (so g^2 = g^3 = ... = 0), the
microprice adjustment is g^1 = delta (2 phi - 1), phi = (2/pi) arctan(Q^b/Q^a):
- Q^b = 300, Q^a = 100: phi = 0.795, adjustment +0.590 tick. The weighted mid gives (I - 1/2) = 0.75 - 0.5 = +0.25
  tick. The CdL toy puts the microprice ABOVE the ask (0.59 > 0.5 tick), which the real estimator should not do
  (Stoikov reports it lives between bid and ask). The gap shows that the toy omits the order flow that refills the
  thin side; an estimate on real data is needed.
- Q^b = 60, Q^a = 240: phi = 0.156, adjustment -0.688 tick under CdL versus -0.30 tick for the weighted mid.
- Edge arithmetic for a passive buy: with the microprice 0.2 tick above the mid, a bid at B = mid - 0.5 tick has an
  expected edge of 0.7 tick = $0.875 per MES contract before the fill's own adverse selection and fees; the pilot's
  markouts conditional on fill measure the adverse selection that eats this.

### 5.6 Testable hypothesis
- H5: "Bucketed by microprice-minus-bid (fixed buckets, frozen microprice estimated on the first 2 months), the
  mean 10 s markout of filled back-of-queue 1-lot bids is increasing in the bucket, and the top bucket's mean
  markout net of a fixed fee is positive."
- Statistic: Jonckheere-type trend test across buckets, or a regression of markout on (P_micro - B) with day-clustered
  standard errors; the decision-relevant statistic is the top-bucket mean net markout with a Newey-West t.
- Sample: about 6,600 fills (section 4.6 assumption) across, say, 5 buckets, about 1,300 per bucket.
- N: 1 per frozen (n_imb, n_spread) choice; the author's notebook already shows two choices (10 and 4 buckets),
  so pre-register one.

### 5.7 Compute
A 20-state matrix inverse; trivial on the laptop.

### 5.8 Evidence on retail scale
- The slides' validation is a visual comparison of G*, fitted on the first trading day of March 2011, against 1, 5
  and 10 minute mid changes averaged over the whole month (and on three consecutive days; the calibration day is
  inside the validation month) for two stocks; no costs, no trading test.
- [unverified, from the search snippet only] the published abstract says the microprice is "empirically a better
  predictor of short-term prices than the mid-price or the weighted mid-price".
- No source found showing a microprice-based passive strategy that is profitable after costs at retail latency.

---

## 6. Value of queue position (Moallemi and Yuan 2017; Dahlstrom, Hagstromer and Norden 2023)

Sources: Moallemi, C. C., Yuan, K. (2017 revision), "A model for queue position valuation in a limit order book",
Columbia Business School working paper (author server copy, `moallemi_yuan_2017_queuevalue.pdf/.txt`).
Dahlstrom, P., Hagstromer, B., Norden, L. L. (2023), "The determinants of limit order cancellations", Financial
Review 59(1), 181-201 (online August 2023; DOI 10.1111/fire.12363), open access, saved as `dhn_2023_full_scrapling_fetch.md`. Note: I found no
Dahlstrom-Hagstromer-Norden paper titled on queue VALUE; their paper on cancellations is the one that measures how
queue position matters, so it is used here.

### 6.1 Core idea
Under FIFO, an order's position in the queue is worth money. Value = fill probability x (spread earned - adverse
selection). Both terms worsen as the order moves back: it fills less often, and when it does fill, it is more often
because a large aggressive order or a price jump swept the whole queue, which is exactly when the price is about to
move against it. An order at the back of a long queue on a large-tick asset can have negative value even though
it "earns" the half-spread.

### 6.2 Equations (Moallemi-Yuan)
- Accounting identity (eq. 1): V_t = alpha_t (delta_t - AS_t), with alpha_t = P(FILL | F_t) the fill probability,
  delta_t = P_A - P_t the liquidity premium (order price minus the latent efficient price P_t; a half-spread if P_t
  is the mid), AS_t = E[P_{tau*} - P_t | F_t, FILL] the adverse selection (shown for a sell order at the ask).
  Derivation: V_t = E[(P_A - P) 1{FILL} | F_t]; P_t = E[P | F_t] is a martingale; optional stopping at the fill or
  cancel time tau* splits the expectation into the two terms.
- Price dynamics (eq. 2): P_t = P_0 + lambda sum_{trades} u_i + sum_{jumps} J_k: linear permanent impact lambda per
  signed trade size u_i, trades Poisson at rate mu, jumps Poisson at rate gamma with mean-zero sizes J_k.
- Queue dynamics: a trade of size u >= q (queue ahead) fills the order; 0 <= u < q advances it; a positive jump
  fills it (all orders at the ask are lifted), a negative jump cancels it; a cancellation event shrinks the queue
  ahead proportionally, q -> l q (uniform proportional cancellations).
- Theorem 1: V(q, delta) = alpha(q) delta - beta(q), with alpha and beta solving Volterra integral equations
  (eq. 6-7); Theorem 2: alpha(q) = fill probability, AS = beta(q)/alpha(q) > 0, alpha non-increasing in q, and with
  no cancellations alpha(inf) = p_J^+ (probability of an up jump), beta(inf) = J_bar^+ = E[J 1{J > 0}].
- Theorem 3 (two-sided exponential trade sizes, no cancellations): alpha(q) = p_J^+ + mu (1 - p_J^+)/(mu + 2 gamma)
  e^{-b q} (eq. 9), with beta(q) in eq. (10). (The definition of b in the saved text contains a symbol, zeta, that
  is not defined on the page I read; I do not use b numerically.)
- Inputs (paper's list): gamma/mu, eta^+/mu (cancellation rate over trade rate), trade-size distribution f, lambda,
  p_J^+, E[J | J > 0].

### 6.3 Dahlstrom-Hagstromer-Norden findings (order-level hazard model)
Cox-type hazard model of cancellation for 138,486 limit orders in OMXS 30 stocks, Nasdaq Stockholm, May 2014.
They split same-side depth into depth AHEAD of the order (Front-of-Queue) and BEHIND it (Back-of-Queue). Result:
cancellation hazard falls strongly when depth behind the order grows (hazard-rate change -56.4% for changes,
-58.7% for levels) and is almost unaffected by depth ahead (-2.2% for the level; -11.5% is the non-HFT firms' coefficient for changes
in Front-of-Queue Depth, HFTs -42.0%). Their reading: traders manage the
expected profit at execution, and a larger queue ahead means a fill requires a larger, more informed market order:
"To the extent that market order size reflects private information, this difference represents an adverse
selection cost." HFTs react more strongly than other firms.

### 6.4 Data; enough?
Queue position needs order-level data: mbo identifies each order's priority and which orders ahead cancel.
mbp-10 can only approximate position by an assumption (proportional cancellations as Moallemi-Yuan assume, or
uniform as HLR assume). Moallemi-Yuan used Nasdaq ITCH (market-by-order) and say why: "Market-by-order data makes it
possible to reconstruct the limit order book". For the MES pilot, an mbo purchase is the schema that makes queue
position, and therefore every number in this section, measurable rather than assumed.

### 6.5 Worked example (C2_LOB_examples2.py)
- Moallemi-Yuan Table 3 decomposition check, BAC: fill probability 0.62, adverse selection 0.57 tick, premium
  delta_0 = 0.8 tick (half-spread 0.5 + Nasdaq rebate 0.3): 0.62 x (0.8 - 0.57) = +0.143 tick, matching the reported
  0.14. Remove the rebate (CME charges a fee to passive orders, there is no maker rebate for a retail MES account):
  0.62 x (0.5 - 0.57) = -0.043 tick, i.e. -$0.054 per MES contract-equivalent before fees. CSCO: +0.076 with rebate,
  -0.113 without. PBR: -0.028 even with the rebate.
- Back of a very long queue (Theorem 2 limits, no cancellations), BAC 8/9/2013 inputs mu = 1.65/min,
  gamma = 0.71/min, mean jump 0.91 tick, p_J^+ = 0.5 assumed: alpha(0) = (mu/2 + gamma p_J^+)/(mu/2 + gamma) =
  (0.825 + 0.355)/(0.825 + 0.71) = 0.769; alpha(inf) = 0.5; beta(inf) = 0.5 x 0.91 = 0.455 tick;
  V(inf) = 0.5 x 0.8 - 0.455 = -0.055 tick with the rebate, 0.5 x 0.5 - 0.455 = -0.205 tick without.
- The paper's own front-versus-average gap: "about 0.26 ticks on 8/9/2013 and 0.21 ticks on 8/20/2013".
- Reading for MES: a retail order arriving tens of milliseconds after a price level forms joins behind the fast
  participants, so it is a back-of-queue order by construction; the model says such an order is worth roughly
  zero to negative ticks gross on a large-tick product without a rebate. This is the central risk for the program's
  limit-order direction and the pilot's markouts are the direct test.

### 6.6 Testable hypothesis
- H6 (queue-position value at retail position): "The mean value per placement of a back-of-queue 1-lot virtual
  order, V = 1{fill} x (fill price vs mid 60 s after fill) - fee, is below zero" (one-sided, the program's working
  null is that it is not positive). Statistic: mean V per placement with a day-block bootstrap CI; decomposition
  into fill rate x (half-spread - adverse selection) reported alongside. Moallemi-Yuan used exactly this
  non-parametric backtest: 1,000 random artificial orders per day over 30 days, mid one minute after execution as
  the fundamental value; they stress that the estimates are noisy and need many observations.
- H6b: "Value is decreasing in queue position" (model-implied alpha(q) and beta(q) calibrated on training months
  predict the held-out sign and slope of V across queue-position terciles).
- Sample: Moallemi-Yuan's design is 30 days x 1,000 = 30,000 placements; the pilot's 80+ days at one placement per
  5 minutes (22,000) is comparable; mbo needed to place orders at defined positions other than the back.
- N: H6 is a single descriptive go/no-go number (1 if registered); H6b adds 1.

### 6.7 Compute
Volterra equations (6)-(7) on a grid of queue positions: a few seconds per day of parameters on the laptop. The
backtest is a replay of mbo events with a virtual order: CPU and memory bound by the data size (the pilot's
problem, not the model's).

### 6.8 Evidence on retail scale
- Moallemi-Yuan's sample is large-tick Nasdaq stocks in August 2013 with a 0.3-tick maker rebate that dominates the
  sign of the back-of-queue value (worked example). No futures, no fees, no latency treatment beyond queue position.
- Dahlstrom et al. is descriptive (cancellation behaviour), not a trading test.
- Both point the same way: queue position is valuable to whoever gets the front; a slow participant gets the back
  and the adverse selection that comes with it.

---

## 7. Execution-time survival models (Lo, MacKinlay and Zhang 2002)

Source: Lo, A. W., MacKinlay, A. C., Zhang, J. (2002), "Econometric models of limit-order executions", Journal of
Financial Economics 65, 31-71 (closed access per OpenAlex). Full text used: NBER Working Paper 6257 (November
1997), saved as `lo_mackinlay_zhang_nber_w6257.pdf`. The PDF is a scan with no text layer; Firecrawl OCR failed
(credits exhausted, logged); I read the pages as images and transcribed the quotes in the evidence table (page
numbers given). The abstract on the authors' MIT page (`lmz_mit_page.html/.txt`) is the published version's.

### 7.1 Core idea
Treat time-to-fill of a limit order as a lifetime and use survival analysis: orders cancelled or unfilled at the
horizon are censored, not discarded. Covariates (distance of the limit price from the quotes, size, spread,
volatility, depth) shift the distribution. The authors also show that "hypothetical" fills built from price paths
are very poor proxies for real fills, which matters for any virtual-order pilot.

### 7.2 Equations (NBER WP section 4, equation numbers as printed)
- Censoring indicator (4.2) and likelihood (4.3): L = prod_{uncensored} f(t_i) * prod_{censored} S(t_i), where f is
  the density and S(t) = P(T > t) the survival function. (The printed exponent form f(t_i)^delta_i S(t_i)^(1 -
  delta_i) has delta_i = 1 for censored, which contradicts the product form; the product form is the correct
  likelihood.)
- Generalized gamma density (4.4): f(t) = lambda |p| kappa^kappa (lambda t)^(p kappa - 1) exp(-(lambda t)^p kappa)
  / Gamma(kappa), with shape parameters kappa, p and scale lambda; survival (4.5): S(t) = 1 - Gamma(kappa,
  (lambda t)^p kappa)/Gamma(kappa) for p > 0 (Gamma(a, b) the incomplete gamma function as the paper defines it).
  kappa = 1 gives the Weibull (4.6), kappa = 1 and p = 1 the exponential, kappa -> infinity the lognormal (the WP prints kappa = 0, a misprint; the
  published JFE version may differ).
- Kaplan-Meier estimator (section 4.3): S_hat(t) = prod_{t_(i) <= t} ((n - i)/(n - i + 1))^(1 - censoring flag),
  i.e. multiply by (at-risk - 1)/at-risk at each fill time.
- Covariates (section 4.4): accelerated failure time (AFT) T = exp(X' beta) T_0, or proportional hazards
  h(t; X) = h_0(t) exp(-X' beta) (4.7). The paper prefers the generalized gamma AFT model; it "fits remarkably
  well" and beats Cox in the right tail.

### 7.3 Data; enough?
Each placement needs a start time, an end time, and whether it ended in a fill or a censoring (cancel, price moved
away, horizon). For the pilot's VIRTUAL orders the fill time comes from the queue simulation (section 11), so the
survival model inherits whatever bias the virtual-fill rule has. Covariates at placement (queue ahead, imbalance,
spread, recent volatility) come from mbp-10; queue ahead requires mbo. 4 months gives tens of thousands of
placements, ample for a 3-parameter baseline plus a handful of covariates.

### 7.4 What it estimates or decides
The whole distribution of time-to-fill, so P(fill within 1, 10, 60 s | covariates) = 1 - S(h | X), and how much
one tick of price improvement shortens the wait. The paper's example: for ABT, "the probability of an ABT
limit-buy order surviving 20 minutes drops from about 95% to just over 20% when the limit price changes from one
tick below to one tick above the original limit price".

### 7.5 Worked example (C2_LOB_examples2.py)
- Kaplan-Meier on 10 toy placements (seconds; F = fill, C = censored): 3F, 5F, 5C, 8F, 12F, 15C, 20F, 30C, 45F,
  60C. S_hat: after 3 s 9/10 = 0.900; after the 5 s fill 0.900 x 8/9 = 0.800 (fills before censorings at ties);
  after 8 s 0.800 x 6/7 = 0.686; 12 s 0.686 x 5/6 = 0.571; 20 s 0.571 x 3/4 = 0.429; 45 s 0.429 x 1/2 = 0.214.
  So P(fill within 60 s) = 1 - 0.214 = 0.786 in this toy.
- Generalized gamma with scale 1/lambda = 30 s: exponential (kappa = 1, p = 1) gives S(10 s) = e^(-1/3) = 0.717 and
  S(60 s) = e^(-2) = 0.135; a Weibull with p = 0.7 gives 0.629 and 0.197 (more early fills and a fatter tail).
- AFT reading: if one tick more aggressive pricing has x'beta = -1, all fill times shrink by e^-1 = 0.368.

### 7.6 Testable hypothesis
- H7: "A generalized-gamma AFT model with covariates (queue ahead, imbalance, spread) fitted on the training months
  predicts held-out P(fill within 10 s) better (lower Brier score, or higher concordance index) than the
  Kaplan-Meier marginal with no covariates."
- Statistic: Brier score at 1, 10, 60 s with inverse-probability-of-censoring weights, and Harrell's concordance;
  block bootstrap by day for the difference.
- Sample: about 22,000 placements; with 5 covariates, events per variable far exceed the usual 10-20 minimum.
- N: 1 per frozen covariate set and distribution.

### 7.7 Compute
Maximum likelihood with 3 + k parameters on 10^4-10^5 rows: seconds on the laptop.

### 7.8 Evidence on retail scale; the hypothetical-execution warning
- The data are actual ITG institutional limit orders, 100 large S&P 500 stocks, 1994-1995: a different market era.
- The key result for the pilot: hypothetical fills are poor proxies. For ABT the lower-bound (first trade at the
  limit price) mean execution time was 15.58 minutes, the upper bound 60.12 minutes, the actual 25.39 minutes;
  differences significant for all 16 stocks (z from 5.93 to 18.18); even "n-th passage" rules (a crude queue
  position) "cannot match the empirical distribution of actual limit-order execution times". With mbo data the
  pilot can do far better than TAQ first-passage rules (it sees the queue ahead), but its fills remain
  hypothetical: no own-order impact, no latency, no information about whether a real order at the back would be
  selected against more than the replay shows. The pilot's virtual fill rule should therefore be stated as a
  lower bound on adverse selection.

---

## 8. Deep fill-probability estimators (Maglaras, Moallemi and Wang 2022; Arroyo, Cartea, Moreno-Pino and Zohren 2023)

Sources: Maglaras, C., Moallemi, C. C., Wang, M. (2022), "A deep learning approach to estimating fill
probabilities in a limit order book", Quantitative Finance 22(11), 1989-2003; full text: working paper revision of
11 March 2021 (Wayback copy of the author page, `maglaras_moallemi_wang_2021_deeplob.pdf/.txt`; the live page is
behind a Cloudflare challenge). Arroyo, A., Cartea, A., Moreno-Pino, F., Zohren, S. (2024), "Deep attentive survival
analysis in limit order books: estimating fill probabilities with convolutional-transformers", Quantitative
Finance 24(1), 35-57 (Crossref, `crossref_reference_check.txt`); full text: arXiv
2306.05479v1 (`arroyo_etal_2023_survival.pdf/.txt`). Related analytic work: Lokin, F., Yu, F., "Fill probabilities
in a limit order book with state-dependent stochastic order flows", arXiv 2403.02572v2 (February 2026)
(`fill_prob_state_dependent_2024.pdf/.txt`).

### 8.1 Core idea
Replace the hand-built queue model with a neural network that maps the recent history of the book (a time series
of features) to the distribution of time-to-fill of a passive order, trained by the censored-data likelihood of
section 7. MMW use an LSTM that outputs piecewise-constant hazard rates; Arroyo et al. use a convolutional
Transformer encoder and a monotonic decoder that outputs a survival function S(t | x) at any t.

### 8.2 Equations
MMW (section 3.3 and 4.3):
- Partition time into M + 1 intervals [0, tau_1), ..., [tau_M, inf) (they use the deciles of observed fill times,
  10 intervals) and let the network output hazards lambda_1..lambda_{M+1} >= 0.
- Cumulative hazard: Lambda(t) = sum_{i=1..i*(t)} lambda_i (tau_i - tau_{i-1}) + lambda_{i*(t)+1} (t - tau_{i*(t)}),
  i*(t) = max{i : tau_i < t}. Then F_T(t) = 1 - exp(-Lambda(t)), f_T(t) = lambda_{i*(t)+1} exp(-Lambda(t)).
- Log-likelihood per order: filled at t: -Lambda(t) + log lambda_{i*(t)+1}; unfilled through t: the survival term,
  which is log S(t) = -Lambda(t). (The saved text prints "log(1 - e^{Lambda(t)})" for the unfilled case, which
  cannot be right for a survival term; I use -Lambda(t), the standard right-censored contribution.)
- Decision rule (section 6.4): use a limit order iff P_hat(T <= h) > Theta; implementation shortfall
  IS = 1{p_hat <= Theta} IS_mkt + 1{p_hat > Theta} IS_limit, IS_mkt = p_A(0) - p_M(0),
  IS_limit = 1{T <= h} [p_B(0) - p_M(0)] + 1{T > h} C_cleanup, C_cleanup = p_A(h) - p_M(0).
Arroyo et al. (eq. 1): L(theta) = sum_k [ delta_k log f_hat(z_k | x_k, theta) + (1 - delta_k) log S_hat(z_k | x_k,
theta) ], delta_k = 1 if filled; right-censored log-likelihood (RCLL) is a proper scoring rule (they cite Rindt et
al. 2022). The decoder's weights are constrained positive so S_hat is monotone in t.

### 8.3 Data; enough?
- Both build training sets from VIRTUAL orders replayed through order-level data: MMW from Nasdaq ITCH, 1,000
  synthetic orders per day, fill rules that track the queue ahead ("executed if the size of the market order is
  larger than the share of limit orders in front of the synthetic limit order"; cancellations in front advance the
  position). That rule needs mbo. Arroyo et al. use LOBSTER (Nasdaq message data), 100 orders per day per ticker,
  either tracked real orders or hypothetical one-share orders "placed last in the queue" and pegged to the best
  level.
- Sample sizes: MMW use 502 trading days (Oct 2012 to Sep 2014), rolling 12 months train, 1 month validation, 1
  month test, repeated 10 times. Arroyo et al. train on 1 September to 26 December 2022 (about 4 months). One CME
  contract for 4 months at, say, 1,000 virtual orders per day (Moallemi-style) gives about 80,000 labelled orders;
  enough for an LSTM of modest size, short of MMW's scale. 12 months would match MMW's training window.

### 8.4 What it estimates or decides
The conditional fill-time distribution, so P(fill within 1, 10, 60 s | book history), and through the threshold
rule, whether to post passively or cross.

### 8.5 Worked example (numbers from MMW tables)
- Fill-probability AUC, horizons 1/5/10 min: logistic 0.62/0.60/0.60; bucket (time of day x imbalance quintile)
  0.63/0.60/0.60; RNN 0.72/0.67/0.66 (Table 6).
- Implementation shortfall to buy one share, ticks (Table 8), 1-minute horizon: always market order 0.508; always
  limit then clean-up 0.443; logistic threshold 0.321; bucket 0.317; RNN 0.279 (s.e. 0.02).
- Arithmetic of what IS measures: a filled limit buy scores p_B(0) - p_M(0) = -0.5 tick (a gain of half a spread
  against the arrival mid) no matter where the price goes after the fill; an unfilled one pays the clean-up cost
  (1.09 to 1.22 ticks at 1 minute, Table 9). IS is the right yardstick for a broker who MUST buy; it is NOT the
  P&L of a trader who chooses whether to trade, because it ignores the post-fill markout (adverse selection) on
  filled orders.
- Hazard arithmetic: with two intervals [0, 10 s) hazard 0.03/s and [10 s, inf) hazard 0.01/s, Lambda(60 s) =
  0.03 x 10 + 0.01 x 50 = 0.8, P(fill within 60 s) = 1 - e^-0.8 = 0.551.

### 8.6 Testable hypothesis
- H8: "An LSTM hazard model (architecture, features, intervals frozen in advance) trained on the pilot's first
  months predicts held-out P(fill within 10 s) with a higher time-dependent concordance / lower integrated Brier
  score than (a) Kaplan-Meier and (b) the generalized-gamma AFT of section 7."
- H8b (the one that matters for money): "Posting only when P_hat(fill within 10 s) > Theta (Theta frozen) raises
  the mean per-placement value V (section 6.6) relative to posting always." Statistic: difference in mean V with a
  day-block bootstrap; Newey-West t.
- Sample: 4 months x 1,000 virtual orders per day = about 80,000; split chronologically (train / validation /
  test by month), never randomly.
- N: H8 adds 1 per architecture frozen; H8b adds 1 per Theta. MMW chose Theta "empirically over the test data set",
  i.e. on the test month; a pre-registered pilot must freeze Theta on validation data.

### 8.7 Compute (hardware and cost)
- An LSTM over the last 50-500 book events with a few dozen features and ~10^5 training sequences is a small model;
  it fits in the RTX 3050's 4 GB and trains in minutes to hours. The papers do not report hardware or wall time, so
  this is my estimate [unverified].
- Arroyo et al.'s convolutional Transformer with lookback T = 1,000 events: attention cost grows with T^2, so 4 GB
  VRAM limits batch size; feasible with small batches and mixed precision in my estimate [unverified].
- Cloud fallback, from the Lambda price page fetched 2026-10-21 (`lambda_pricing.html`), per GPU-hour plus sales
  tax: NVIDIA A10 24 GB $1.29; A100 PCIe 40 GB $1.99; H100 PCIe 80 GB $3.29; A6000 48 GB $1.09. A 20-run
  hyper-parameter sweep at 2 GPU-hours each on an A10 costs 20 x 2 x $1.29 = $51.60; each run is a configuration
  that enters N.
- The binding cost is not GPU time but building the training labels: replaying mbo events with virtual orders is
  CPU and memory work on the laptop (14 GB RAM limit; chunk by day).

### 8.8 Evidence on retail scale
- MMW test on large-tick Nasdaq stocks 2012-2014 with a rolling monthly test; Arroyo et al. compare models only by
  likelihood-based scores (Tables 5-8; the convolutional Transformer improves the RCLL over an MLP encoder by
  62-86% on average), with no trading or cost evaluation. In arXiv v1 Table 7 several T = 1000 entries repeat
  across tickers (13.77, 7.02, 79.29 each three times), which looks like a copy error.
- Arroyo et al.'s Table 3 shows how rarely REAL orders at the best level fill (fill probability 0.039 to 0.095 for
  the nine tickers shown, October-December 2022), because most are cancelled first.
- Arroyo et al. describe the adverse-selection signature directly: an order inside the spread that fills within a
  few seconds did so because "the price moved in the favorable direction", while one that does not "is likely that
  the price moved adversely".
- No paper found that shows a deep fill-probability model turning a retail-latency passive strategy profitable
  after fees.

---

## 9. FIFO versus pro-rata matching on CME, and what each means for a back-of-queue order

Sources: CME Group Client Systems Wiki pages "CME Globex Matching Algorithms" and "Supported Matching Algorithms"
(`cme_globex_matching_algorithms.*`, `cme_supported_matching_algorithms.*`); CME Micro E-mini FAQ via Wayback,
snapshot 2025-11-16 (`cme_micro_emini_faq_wayback.*`; cmegroup.com refuses this machine); Databento blog "CME
matching algorithms explained" (`databento_cme_matching_blog.*`, a vendor explainer, used only for the product
examples and volume shares).

### 9.1 The rules
- FIFO: "The FIFO algorithm uses price and time as the only criteria for filling an order. In this algorithm, all
  orders at the same price level are filled according to time priority; the first order at a price level is the
  first order matched."
- MES: "Micro E-mini futures will use FIFO (First in, first out) algorithm, identical to their E-mini
  counterparts." Databento lists ES, NQ, ZN, ZF, ZB and CL outrights as FIFO examples, with FIFO at 70.3% of CME
  volume (vendor figure).
- Pro rata (CME steps): "Quantity to be matched is multiplied by each resting order's pro-rated percentage to
  calculate allocated trade quantity. All fills are rounded down to the nearest integer (which may be zero)." Pro
  rata is never the last step; remainders go FIFO (or "Leveling", at most one lot per order).
- Allocation (SOFR futures): TOP order priority to the first order that betters the market, then pro rata with a
  2-lot minimum ("The Pro Rata algorithm will only allocate to resting orders that will receive 2 or more
  contracts"), then FIFO for the residual. "This match algorithm known as Pro Rata or Allocation Algorithm is
  applied only to the SOFR futures at CME Group (SOFR packs and Bundles match via FIFO)."
- Configurable (Databento examples: ZT, ZQ, ZC, ZS, ZW outrights): TOP, Split between FIFO and pro rata by product
  parameters, Leveling.

### 9.2 What each means for a 1-lot at the back
- FIFO: fill time = time for the queue ahead to be consumed by trades plus cancellations ahead. Everything in
  sections 1, 3, 6, 7 and 8 applies; queue position is the state variable; latency decides position.
- Pro rata: position matters little; SIZE matters. Worked example: a 1,000-lot bid level hit by a 50-lot sell.
  A 1-lot's pro-rata share is 50 x 1/1,000 = 0.05 lot, floored to 0, and the 2-lot minimum would remove it anyway;
  it can only be filled through the FIFO residual or a TOP allocation. A 40-lot resting order gets
  floor(50 x 40/1,000) = 2 lots. A 1-lot trader in a pro-rata product is therefore filled mostly when the
  level is swept, which is the adverse path. The TOP rule is the exception: a 1-lot that improves the market when
  the spread is wider than one tick gets priority.
- For this program: MES (and the other equity-index micros) is FIFO, so queue-position models are the right
  family; a pro-rata contract would need a different fill model (allocation share, minimums, over-sizing
  incentives) and is a poor fit for 1-lot passive orders.

### 9.3 Data, hypothesis, compute
- mbo shows each order's priority and its fills, so the pilot can check the FIFO assumption directly: H9: "For the
  pilot contract, every observed fill at a price level is allocated in strict time-priority order" (descriptive
  check of the matching rule on mbo data; a failure would invalidate every FIFO fill model). Statistic: share of
  trades whose fills violate time priority among visible orders. N: 0 (data validation, not a hypothesis), the lead
  decides. Compute: trivial.
- Evidence: CME's own documentation (primary). No academic test found of FIFO behaviour on MES.

---

## 10. Bouchaud, Bonart, Donier and Gould, Trades, Quotes and Prices (2018), and its market-making break-even

Source: Bouchaud, J.-P., Bonart, J., Donier, J., Gould, M. (2018), Trades, Quotes and Prices: Financial Markets
Under the Microscope, Cambridge University Press, DOI 10.1017/9781316659335. The book's full text is not open; I
verified only its chapter titles and page ranges from Crossref (`bouchaud_tqp_crossref_chapters.txt`). The
break-even relation below is taken from the open arXiv paper by the same group: Wyart, M., Bouchaud, J.-P.,
Kockelkoren, J., Potters, M., Vettorazzo, M. (2008), "Relation between bid-ask spread, impact and volatility in
order-driven markets", Quantitative Finance 8(1), 41-57 (Crossref); arXiv physics/0603084v3
(`wyart_etal_2008_spread_impact_vol.*`).

### 10.1 What the book covers (verified chapter list)
Single-queue dynamics: simple models (pp. 78-100); single-queue dynamics for large-tick stocks (101-116);
joint-queue dynamics for large-tick stocks (117-133); the Santa Fe model; Hawkes processes; long-range persistence
of order flow; the impact of market orders and metaorders; propagator models; the Kyle model; the determinants of
the bid-ask spread (298-318); the profitability of market-making (319-332); optimal execution (384-405). It is the
reference text that ties the queue models of sections 1-3 to impact and adverse selection. Content claims about
the book beyond titles are [unverified] here.

### 10.2 Core idea and equation (from Wyart et al., same research group)
- Lagged impact (response) function, eq. (6): R_l = < eps_i (m_{i+l} - m_i) >, where eps_i = +1 for a buyer-
  initiated trade and -1 for a seller-initiated one, m_i the mid just before trade i, l the lag in trades.
- A liquidity provider filled on trade i earns the half-spread S/2 against the mid and loses R_l as the price
  moves against it; the market-making P&L of a strategy participating in a fraction phi_i of trades is
  G_L = sum_i phi_i eps_i v_i (m_i + eps_i S_i/2) (eq. 20), and the zero-profit (competitive) condition gives a
  linear spread-impact relation, with R_1 = S/(2 lambda_inf), lambda_inf = 1/(1 - C_1) >= 1 (eq. 7, 10 with phi = 0); R_1 = S/2 only when order
  signs are uncorrelated (C_1 = 0).
- Empirical statement: "fast market making strategies are on average weakly profitable" on the Paris Bourse; and
  "fast market making strategies can be profitable even though the long-term average cost of limit orders is
  positive", because of long-range order-flow correlations.

### 10.3 Pilot translation
The pilot's markout of a filled passive buy at horizon h is exactly m_h = (M(t_fill) - B) + (M(t_fill + h) -
M(t_fill)) = S/2 - (adverse move), i.e. the empirical S/2 - R_h for our fills. With S = 1 tick on MES:
m_h = 0.5 tick - adverse move. If the adverse move over 60 s averages 0.57 tick (the BAC adverse-selection figure
from Moallemi-Yuan, used only for scale), m_60 = -0.07 tick before fees. A per-side fee f in ticks is subtracted
on top; for example a $0.50 all-in fee per side would be 0.50/1.25 = 0.40 tick (illustrative number, not a quote of
any broker's or Topstep's fee).

### 10.4 Testable hypothesis, data, compute
- H10: "Over the held-out months, the mean markout of filled back-of-queue 1-lot passive orders, m_h at
  h = 1, 10, 60 s, net of the per-side fee, is greater than zero." One-sided; Newey-West t > 3.0 to pass. This is
  the pilot's headline hypothesis and the one every other section feeds.
- Data: any schema that gives the mid at fill time and h seconds later (mbp-1 or better); the fill itself needs the
  queue model (mbo for the position). Sample: about 6,600 fills (section 4.6 guess); with a markout standard
  deviation of about 1 tick at 60 s (guess, to be measured), the standard error of the mean is 1/sqrt(6,600) =
  0.012 tick, ignoring clustering; day-block resampling will widen it.
- N: 3 if the three horizons are separate hypotheses; 1 if one horizon (say 10 s) is pre-registered as primary.
- Compute: trivial.

### 10.5 Evidence on retail scale
Wyart et al. study the profitability of an "infinitesimal" market maker that participates in a vanishing fraction
of all trades at the touch, i.e. one with average queue luck, not one at the back of the queue with tens of
milliseconds of latency. Their "weakly profitable" is a ceiling for a retail participant, not a floor.

---

## 11. The fill-probability formulas a pilot can estimate and test (synthesis)

Each line: formula, inputs, schema that identifies it, how to test it on the pilot. Notation as in section 0.

F1. Empirical fill curve (non-parametric). p_hat(h) = 1 - S_KM(h), Kaplan-Meier over virtual placements with
censoring at cancel (price moved away) or horizon. Inputs: placement time, end time, filled flag. Schema: needs the
virtual fill rule (F2). Test: it is the baseline every model must beat (Brier score at h = 1, 10, 60 s).

F2. FIFO virtual fill rule (the label generator). A buy at B placed at t0 behind Q_ahead(t0) contracts fills at the
first t with V_sell(t0, t) >= Q_ahead(t0) - C_ahead(t0, t) + 1, where V_sell is sell-aggressor volume traded at B
and C_ahead the cancelled volume ahead of us. mbo observes C_ahead exactly; mbp-10 must assume it (HLR Assumption 3:
uniform over the queue; Moallemi-Yuan: proportional shrinkage). Rule if the price moves through B: filled (a trade
below B implies our bid was taken; MMW's rule). Test: compare fill rates under the mbo-exact rule and the mbp-10
approximations on the same days; the gap measures the error of buying only mbp-10.

F3. Queue-depletion time with Poisson unit flow (CST eq. 14): zeta = sum_{i=1..b} Exp(mu + theta (i - 1)),
E[zeta] = sum_{i=1..b} 1/(mu + theta (i - 1)). Worked (hypothetical rates, C2_LOB_examples3.py): mu = 2 lots/s of
sell market orders at B, theta = 0.02 per lot per second cancellations: 10 lots ahead, mean 5.2 s, P(fill <= 10 s)
= 0.994; 50 ahead, mean 20.7 s, P(<= 10 s) = 0.000, P(<= 60 s) = 1.000; 200 ahead, mean 55.3 s, P(<= 60 s) =
0.875. These near-deterministic times show the model's weakness: with unit-size Poisson flow the waiting time
concentrates around its mean, whereas real fills come from bursty, lumpy sweeps (Hawkes terms, order-size models,
section 3.8). It ignores the price moving away. Test against F1: calibration by queue-ahead bucket.

F4. Fill before the mid moves (CST Proposition 5, S = 1): P[zeta_B < sigma_A], ask queue a birth-death process
(birth lambda, death mu + i theta). Exact solve as an absorbing chain (my script) rather than Laplace inversion.
Test: H1.

F5. Direction of the next move (CdL eq. 7; continuum form): P(up | q_b, q_a) ~ (2/pi) arctan(q_b/q_a); empirical
version: logistic in I = (q_b - q_a)/(q_b + q_a) (Gould-Bonart). The probability that a back-of-queue bid's queue is
depleted before the ask is 1 - P(up), i.e. the probability of the adverse path. Test: H2, H4.

F6. Order value (Moallemi-Yuan eq. 1): V = alpha (delta - AS) - fee x alpha (fee only on fills), estimated
non-parametrically as V_hat = mean over placements of 1{fill} x (m_60 - f). Test: H6 (V < 0 is the null to
reject).

F7. Covariate fill-time models: AFT T = exp(X'beta) T_0 with generalized-gamma T_0 (LMZ), or piecewise-constant
hazards P(T <= h | x) = 1 - exp(-Lambda(h | x)) (MMW), or a neural S(t | x) (Arroyo). Test: H7, H8 against F1.

F8. Markout identity (Wyart et al., applied to our fills): m_h = S/2 - (adverse move over h) - f. Test: H10.

Recommended order for a pilot: F2 (labels) -> F1 (baseline) -> F8/F6 (is there any money at the back of the
queue?) -> only if F6/F8 are not clearly negative, F5/F7 as conditioning filters (each filter adds to N).

---

## 12. Latency: why the models above favour the fastest participant (evidence)

- Lehalle and Mounjid (2018 version of arXiv 1610.00261, `lehalle_mounjid_latency.*`): on NASDAQ-OMX labelled
  data (AstraZeneca, January to September 2013), imbalance predicts the next mid move, and different participant
  classes accept passive fills at different imbalances; high-frequency proprietary traders "achieve to buy via
  limit orders when the imbalance is very small" (they are the least adversely selected). In their control model,
  "the added value of exploiting liquidity imbalance is eroded by latency: being able to predict future liquidity
  consuming flows is of less use if you do not have enough time to cancel and reinsert your limit orders", and
  "the faster will have more profits than the slower". Their latency is a modelling factor (reacting every tau
  book changes), not milliseconds, so the size of the retail penalty is not quantified.
- Baron, Brogaard, Hagstromer and Kirilenko (2019, JFQA 54(3), 993-1024; accepted version
  `baron_etal_2019_hft_risk_return.*`): on Swedish equities 2010-2014, "differences in relative latency account for
  large differences in HFTs' trading performance"; "The fastest firms earn a higher realized spread when trading
  passively"; and a previous version on the E-mini S&P 500 futures (2010-2012) found "high industry concentration,
  difficulty of new entry, and the importance of latency".
- Implication for the pilot: a Vancouver-to-Aurora order arrives tens of milliseconds after the book state that
  triggered it. The pilot's virtual orders should be placed with a delay (for example 50 ms after the trigger event,
  using exchange timestamps) and cancellations should take effect with the same delay; results without the delay
  overstate fills at good queue positions and understate adverse selection.

---

## 13. Verdict per method (for this program: one CME FIFO contract, 1-lot, retail latency, Part B pilot)

These are a reader's recommendations to the lead, not selection decisions.

| Method | Verdict | Reason |
|---|---|---|
| CST (2010) birth-death queues, Laplace probabilities | maybe | Cheap, interpretable baseline for fill-before-move (F4) and mid direction; Result A reproduces exactly, but I could not reproduce its fill-before-move Table 4, and the model has no adverse-selection channel, so it cannot say whether a fill is worth having. Use only as a benchmark inside H1. |
| Cont-de Larrard (2013) level-1 Markov model | use | Zero-parameter direction probability, phi ~ (2/pi) arctan(q_b/q_a), exact at index-future queue sizes (my check: 4 decimals at 300/100); gives the probability of the adverse (queue-depletion) path for a back-of-queue order. One configuration. |
| Queue-reactive model (HLR 2015) and extensions | maybe (later) | A good simulator for counterfactual placement policies, but it is a tool for after the pilot shows that some passive fills are worth having; each variant (Hawkes, sizes, deep) is another configuration. mbp-10 suffices for intensities; mbo removes its cancellation assumptions. |
| Queue imbalance (Gould-Bonart 2016) | use | One logistic curve; strong for large-tick books (AUC 0.75-0.81 on large-tick stocks); serves as the conditioning variable for H4b. Direction is not profit; latency erodes it (section 12). |
| Microprice (Stoikov 2018) | maybe | Better fair-value reference than the mid for markouts and a natural filter (H5), but it overlaps with imbalance, the full paper was not available to me, and every bucket choice is a configuration. |
| Queue-position value (Moallemi-Yuan; Dahlstrom et al.) | use | The decision framework for the whole direction: value = fill probability x (half-spread - adverse selection). Their own numbers turn negative at the back of the queue once the Nasdaq rebate is removed (-0.043 tick for BAC). H6 is the pilot's go/no-go. Needs mbo for positions other than the back. |
| Survival models (LMZ 2002) | use | Kaplan-Meier with censoring is the correct way to report the pilot's fill rates; a generalized-gamma AFT is a cheap covariate model. LMZ's warning on hypothetical fills shapes the pilot's fill rule. |
| Deep fill-probability (MMW 2022; Arroyo et al. 2024) | skip for now | Better AUC (0.62 to 0.72 at 1 minute in MMW) and better likelihood scores, but evaluated on implementation shortfall or likelihood, not on post-fill markouts; MMW tuned the threshold on the test month; many configurations; needs 12 months of labels to match MMW. Revisit only if H6/H10 find value somewhere. |
| FIFO vs pro-rata (CME) | use | MES is FIFO per CME; queue-position models apply. Pro-rata products (SOFR Allocation, 2-lot minimum) are a poor fit for 1-lot passive orders. |
| Bouchaud et al. (2018) / Wyart et al. markout identity | use | Gives the headline test H10: mean net markout = S/2 - adverse move - fee > 0? Wyart et al.'s "weakly profitable" result is for a participant with average queue luck, a ceiling for a slow one. |

Overall reading of the evidence: every model here agrees that a slow 1-lot at the back of a FIFO queue on a
one-tick large-tick contract is filled disproportionately on the paths where the price then moves against it.
No source I found shows a retail-latency passive strategy on such a contract that is profitable after fees out of
sample. The pilot's markouts (H6, H10) are the direct test of whether that negative prior holds for the chosen
contract.

## 14. What I could not finish or verify

- Stoikov (2018) full paper: closed access, SSRN blocked; used the author's slides and code. Its published-abstract
  claim is [unverified] (search snippet only).
- Bouchaud et al. (2018): only chapter titles and pages verified (Crossref); contents [unverified]. The break-even
  relation is cited from the open Wyart et al. paper instead.
- Lo, MacKinlay and Zhang: the only open full text (NBER WP 6257) is an image-only scan. Firecrawl OCR failed with
  "Insufficient credits" (logged 2026-10-21 PDT); quotes were transcribed by reading page images (pages given in the
  evidence table) and cannot be grep-checked. The published JFE version may differ in numbers.
- CST Table 4 (fill before move) not reproduced by my exact-chain solve under three readings of the model (section
  1.5); cause unknown.
- MMW: the live author PDF sits behind a Cloudflare challenge; I used the Wayback copy (April 2024 snapshot).
- Wayback answered 429 once (other workers likely on the same service); retried later successfully.
- Compute and training-time figures for the deep models are my estimates; none of the papers reports hardware.
- All MES-scale queue sizes, flow rates and fees in worked examples are hypothetical illustrations, labelled where
  used; the pilot will measure them. No market data was read.
- I found no Dahlstrom-Hagstromer-Norden paper on queue VALUE as such; their 2023 cancellations paper is used.
- WebSearch calls used: 11 of 60.

## 15. References

1. Arroyo, A., Cartea, A., Moreno-Pino, F., Zohren, S. (2024). Deep attentive survival analysis in limit order
   books: estimating fill probabilities with convolutional-transformers. Quantitative Finance 24(1), 35-57.
   DOI 10.1080/14697688.2023.2286351. arXiv 2306.05479.
2. Baron, M., Brogaard, J., Hagstromer, B., Kirilenko, A. (2019). Risk and return in high-frequency trading. Journal
   of Financial and Quantitative Analysis 54(3), 993-1024. DOI 10.1017/S0022109018001096.
3. Bodor, H., Carlier, L. (2024). A novel approach to queue-reactive models: the importance of order sizes. arXiv
   2405.18594 (SSRN 4722082).
4. Bodor, H., Carlier, L. (2025). Deep learning meets queue-reactive: a framework for realistic limit order book
   simulation. arXiv 2501.08822.
5. Bouchaud, J.-P., Bonart, J., Donier, J., Gould, M. (2018). Trades, Quotes and Prices: Financial Markets Under the
   Microscope. Cambridge University Press. DOI 10.1017/9781316659335.
6. CME Group Client Systems Wiki. CME Globex Matching Algorithms; Supported Matching Algorithms.
   cmegroupclientsite.atlassian.net/wiki/spaces/EPICSANDBOX/pages/457316046 and /457218479 (fetched 2026-10-21).
7. CME Group. Frequently Asked Questions: Micro E-mini Equity Index Futures. Wayback snapshot 2025-11-16 of
   cmegroup.com/articles/faqs/frequently-asked-questions-micro-e-mini-equity-index-futures.html.
8. Cont, R., de Larrard, A. (2013). Price dynamics in a Markovian limit order market. SIAM Journal on Financial
   Mathematics 4(1), 1-25. DOI 10.1137/110856605. arXiv 1104.4596.
9. Cont, R., Stoikov, S., Talreja, R. (2010). A stochastic model for order book dynamics. Operations Research 58(3),
   549-563. DOI 10.1287/opre.1090.0780.
10. Dahlstrom, P., Hagstromer, B., Norden, L. L. (2024). The determinants of limit order cancellations. Financial
    Review 59(1), 181-201 (online 2023). DOI 10.1111/fire.12363.
11. Databento (n.d.). CME matching algorithms explained. databento.com/blog/cme-matching-algorithms-explained
    (vendor blog; product examples only).
12. Gould, M. D., Bonart, J. (2016). Queue imbalance as a one-tick-ahead price predictor in a limit order book.
    Market Microstructure and Liquidity 2(2), 1650006. DOI 10.1142/S2382626616500064. arXiv 1512.03492.
13. Huang, W., Lehalle, C.-A., Rosenbaum, M. (2015). Simulating and analyzing order book data: the queue-reactive
    model. Journal of the American Statistical Association 110(509), 107-122. DOI 10.1080/01621459.2014.982278.
    arXiv 1312.0563.
14. Lambda (2026). GPU cloud pricing. lambda.ai/pricing (fetched 2026-10-21).
15. Lehalle, C.-A., Mounjid, O. (2017). Limit order strategic placement with adverse selection risk and the role of
    latency. Market Microstructure and Liquidity 3(1), 1750009. DOI 10.1142/S2382626617500095. arXiv 1610.00261.
16. Lo, A. W., MacKinlay, A. C., Zhang, J. (2002). Econometric models of limit-order executions. Journal of
    Financial Economics 65(1), 31-71. DOI 10.1016/S0304-405X(02)00134-4. NBER Working Paper 6257 (1997).
17. Lokin, F., Yu, F. (2026 revision). Fill probabilities in a limit order book with state-dependent stochastic
    order flows. arXiv 2403.02572v2.
18. Maglaras, C., Moallemi, C. C., Wang, M. (2022). A deep learning approach to estimating fill probabilities in a
    limit order book. Quantitative Finance 22(11), 1989-2003. DOI 10.1080/14697688.2022.2124189.
19. Moallemi, C. C., Yuan, K. (2017 revision). A model for queue position valuation in a limit order book. Working
    paper, Columbia Business School; SSRN 2996221.
20. Sfendourakis, E. (2025). Multi-dimensional queue-reactive model and signal-driven models: a unified framework.
    arXiv 2506.11843.
21. Stoikov, S. (2018). The micro-price: a high-frequency estimator of future prices. Quantitative Finance 18(12),
    1959-1966. DOI 10.1080/14697688.2018.1489139. Slides: "The Micro-Price", Gatheral 60 conference; code:
    github.com/sstoikov/microprice.
22. Wu, P., Rambaldi, M., Muzy, J.-F., Bacry, E. (2019). Queue-reactive Hawkes models for the order flow. arXiv
    1901.08938 (a related version appears as "A single queue reactive Hawkes model for the order flow", Market
    Microstructure and Liquidity 6, 2020, DOI 10.1142/S2382626620500136).
23. Wyart, M., Bouchaud, J.-P., Kockelkoren, J., Potters, M., Vettorazzo, M. (2008). Relation between bid-ask
    spread, impact and volatility in order-driven markets. Quantitative Finance 8(1), 41-57.
    DOI 10.1080/14697680701344515. arXiv physics/0603084.

## 16. Evidence table

All files are under reports/stage_e28_briefs/pages/C2_LOB/. Every quote below except the LMZ rows was checked
with `grep -F` against the saved text (script work/C2_LOB/C2_LOB_quotes.tsv, 64 of 64 found). Ligatures (fi) are
as in the PDF text layer. LMZ rows are transcribed from page images of an image-only scan.

| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| CST: market orders are Poisson at rate mu | Cont, Stoikov, Talreja 2010, sec. 2 | "Market buy (resp. sell) orders arrive at independent, exponential times with rate μ," | cst_2010_try1.pdf/.txt |
| CST: cancellation rate proportional to queue size | same | "parameter θ(i), then the overall cancellation rate for the batch is θ(i)x." | cst_2010_try1.txt |
| CST could not validate fill-before-move empirically | same, sec. 5.2.3 | "us to track speciﬁc orders, empirical values for these quantities, as well as the quantities in §5.2.4," / "are not obtainable." | cst_2010_try1.txt |
| CST Table 3 checked by 30,000 simulations | same, sec. 5.2.2 | "30,000 replications) and the Laplace transform methods described in §4. The simulation results," | cst_2010_try1.txt |
| CdL: balanced-case direction probability free of rates | Cont, de Larrard 2013, sec. 3.2 | "Note that the conditional probabilities (7) are, in the case of a balanced order book, independent" / "of the parameters describing the order flow." | cont_delarrard_2013_markovian.txt |
| CdL: lambda just below mu + theta in data | same, sec. 2.2 | "the difference is small" | cont_delarrard_2013_markovian.txt |
| QR: order identifiers needed to model cancellations ahead | Huang, Lehalle, Rosenbaum 2015, sec. 2.5 | "need more detailed market data keeping records of the identifiers of the submitted and canceled" | huang_lehalle_rosenbaum_2015_qr.txt |
| QR: fill probabilities may be overestimated | same | "As a result, execution probabilities might be slightly overestimated using Assumptions" | huang_lehalle_rosenbaum_2015_qr.txt |
| QR: Poisson model overestimates execution probability | same | "our three models give fairly similar execution probabilities, while the Poisson model clearly" | huang_lehalle_rosenbaum_2015_qr.txt |
| QR: mechanical volatility far below empirical | same, sec. 3.1.2 | "lower than the empirical volatility (5 bps compared with 14 bps for the stock France Telecom)." | huang_lehalle_rosenbaum_2015_qr.txt |
| Hawkes term improves QR on Eurex futures | Wu et al. 2019, abstract | "using Level-I order book data from Eurex future assets (Bund and DAX) show that the Hawkes term" / "dramatically improves the pure" | qr_hawkes_2019.txt |
| Order-size QR improves order-flow description | Bodor, Carlier 2024, abstract | "reveals that the extended queue-reactive model significantly improves the description of" | qr_order_sizes_2024.txt |
| MDQR trained with early stopping on 3 months of Bund futures | Bodor, Carlier 2025 | "Training termination after 10 consecutive epochs without improvement" ; "trading days over three months from March to June 2022 for futures maturing in June 2022" | dl_meets_qr_2025.txt |
| Imbalance gain smaller for small-tick stocks | Gould, Bonart 2016, intro | "10–30% for small-tick stocks." | gould_bonart_2016_qi.txt |
| Null model mean squared residual | same, sec. 5.3 | "and the mean squared residual is exactly 1/4." | gould_bonart_2016_qi.txt |
| Out-of-sample split is random, not chronological | same, sec. 5.2 | "performing this analysis, we randomly partition each stock’s aggregated data" | gould_bonart_2016_qi.txt |
| Strong imbalance gives higher predictability | same, sec. 6 / 7 | "regression curves predict that when I is close to 1, the probability of an upward" ; "the out-of-sample performance of our estimators would improve considerably." | gould_bonart_2016_qi.txt |
| Microprice claims (author slides) | Stoikov, Gatheral60 slides | "Micro-price is a good predictor of future mid prices" ; "Micro-price seems to live between the bid and the ask" | stoikov_gatheral60_slides.txt |
| Microprice calibration data | same | "Bid and ask quotes for Bank of America (BAC) and Chevron" | stoikov_gatheral60_slides.txt |
| Microprice code uses 10 imbalance buckets | author notebook | "n_imb=10" | stoikov_microprice_notebook.ipynb |
| Order value decomposition | Moallemi, Yuan 2017, sec. 2.1 | "order value = fill probability × (liquidity spread premium − adverse selection cost) ." | moallemi_yuan_2017_queuevalue.txt |
| Premium includes a 0.3-tick rebate | same, sec. 4.2 | "δ0 = (half-spread) + (rebate) = 0.8 (ticks)." | moallemi_yuan_2017_queuevalue.txt |
| Front-vs-average queue value gap | same, sec. 4.3 | "was about 0.26 ticks on 8/9/2013 and 0.21 ticks on 8/20/2013, which is comparable to the bid-ask" | moallemi_yuan_2017_queuevalue.txt |
| Order-level data needed | same, sec. 4 | "Market-by-order data makes it possible to reconstruct the limit order book at any" | moallemi_yuan_2017_queuevalue.txt |
| Backtest design: artificial orders, 1-minute mid | same, sec. 5.1 | "and insert an artificial order on a random side of the market at each of these times." ; "assume that the mid-price one minute after the order’s execution is an unbiased point estimate of" | moallemi_yuan_2017_queuevalue.txt |
| Queue ahead implies adverse selection | Dahlstrom, Hagstromer, Norden 2023, intro | "To the extent that market order size reflects private information, this difference represents an adverse selection cost." | dhn_2023_full_scrapling_fetch.md |
| DHN sample | same, Table 1 note | "The data include 138,486 limit orders sampled from the OMXS 30 stocks in May 2014 on Nasdaq Stockholm." | dhn_2023_full_scrapling_fetch.md |
| Execution time sensitive to price, not size | Lo, MacKinlay, Zhang, abstract (MIT page) | "We find that execution times are very sensitive to limit" | lmz_mit_page.txt |
| Hypothetical fills are poor proxies (transcribed, WP p. 14, PDF page 18) | LMZ NBER WP 6257 | "In summary, hypothetical limit-order executions are very poor substitutes for actual limit-order data." | lo_mackinlay_zhang_nber_w6257.pdf |
| ABT lower/upper/actual execution times (transcribed, WP p. 13, PDF page 17) | same | "For example, ABT's lower-bound mean is 15.58 minutes, its upper-bound mean is 60.12 minutes, yet its actual mean is 25.39 minutes." | lo_mackinlay_zhang_nber_w6257.pdf |
| One-tick price change moves survival a lot (transcribed, WP p. 32, PDF page 36) | same | "the probability of an ABT limit-buy order surviving 20 minutes drops from about 95% to just over 20% when the limit price changes from one tick below to one tick above the original limit price." | lo_mackinlay_zhang_nber_w6257.pdf |
| Generalized gamma AFT fits well (transcribed, WP p. 33, PDF page 37) | same | "we find that the generalized gamma model with an accelerated failure time specification fits the data remarkably well" | lo_mackinlay_zhang_nber_w6257.pdf |
| MMW virtual fill rule tracks queue ahead | Maglaras, Moallemi, Wang 2021 WP, sec. 4.2 | "limit order is executed if the size of the market order is larger than the share of limit" | maglaras_moallemi_wang_2021_deeplob.txt |
| MMW sample design | same, sec. 5.1 | "For each trading day, 1000 synthetic limit orders are simulated at times chosen uniformly" | maglaras_moallemi_wang_2021_deeplob.txt |
| MMW threshold chosen on the test set | same, sec. 6.4 | "implementation shortfall empirically over the test data set." | maglaras_moallemi_wang_2021_deeplob.txt |
| MMW RNN AUC at 1/5/10 min | same, Table 6 | "RNN              0.72      0.67      0.66" | maglaras_moallemi_wang_2021_deeplob.txt |
| Fast fills inside spread mean favourable move | Arroyo et al. 2023, sec. 5 | "an order is executed within a few seconds of being placed into the book, the price moved in the" | arroyo_etal_2023_survival.txt |
| Arroyo training window | same, sec. 7 | "We train our model with data from 1 September 2022 to 26 December 2022. We use the tick-" | arroyo_etal_2023_survival.txt |
| Arroyo hypothetical orders placed last in queue | same, sec. 5.1 | "ume placed last in the queue (i.e. following regular price-time priority) of a level in the order book." | arroyo_etal_2023_survival.txt |
| State-dependent extension of CST fill probabilities | Lokin, Yu 2026, abstract | "including the probability of a mid-price change, the fill probabilities of orders placed at the" | fill_prob_state_dependent_2024.txt |
| FIFO definition | CME Client Systems Wiki | "The FIFO algorithm uses price and time as the only criteria for filling an order." | cme_supported_matching_algorithms.txt |
| Pro-rata rounding | same | "All fills are rounded down to the nearest integer (which may be zero)." | cme_supported_matching_algorithms.txt |
| 2-lot minimum in Allocation | same | "The Pro Rata algorithm will only allocate to resting orders that will receive 2 or more contracts." | cme_supported_matching_algorithms.txt |
| Allocation applies to SOFR futures | same | "is applied only to the SOFR futures at CME Group (SOFR packs and Bundles match via FIFO)." | cme_supported_matching_algorithms.txt |
| MES is FIFO | CME Micro E-mini FAQ (Wayback 2025-11-16) | "Micro E-mini futures will use FIFO (First in, first out) algorithm, identical to their E-mini counterparts." | cme_micro_emini_faq_wayback.html/.txt |
| FIFO product examples and volume share (vendor) | Databento blog | "Popular products: ES, NQ, ZN, ZF, ZB, CL outrights" ; "Volume: 70.3%" | databento_cme_matching_blog.txt |
| Cloud GPU price | Lambda pricing page | "NVIDIA A10 24 GB 30 226 GiB 1.3 TiB SSD $1.29" ; "plus applicable sales tax/VAT/GST" | lambda_pricing.html/.txt |
| Fast market making weakly profitable | Wyart et al. 2008 | "2.64. Hence, fast market making strategies are on average weakly profitable on" | wyart_etal_2008_spread_impact_vol.txt |
| Fast MM profitable despite long-run cost | same, intro | "We show in particular that fast market making strategies can be profitable even" | wyart_etal_2008_spread_impact_vol.txt |
| Latency erodes imbalance value | Lehalle, Mounjid 2018 | "by latency: being able to predict future liquidity consuming flows is of less use if" | lehalle_mounjid_latency.txt |
| Faster agent profits more | same, sec. 4.2 | "two agents act optimally according the same criterion, the faster will have more profits than" | lehalle_mounjid_latency.txt |
| HF prop traders fill at small imbalance | same, sec. 5 | "frequency proprietary traders (HFPT), we see that HFPT achieve to buy via limit orders when" | lehalle_mounjid_latency.txt |
| Lehalle-Mounjid sample | same, sec. 5 | "on this exchange from the north of Europe (we focus on AstraZeneca from January 2013 to" | lehalle_mounjid_latency.txt |
| Relative latency explains HFT performance | Baron et al. 2019, abstract | "measures of latency and find that differences in relative latency account for large differences in" | baron_etal_2019_hft_risk_return.txt |
| Fastest earn higher passive realized spread | same, intro | "dimensions. The fastest firms earn a higher realized spread when trading passively, consistent with" | baron_etal_2019_hft_risk_return.txt |
| Same findings in E-mini S&P 500 futures | same, footnote 4 | "A previous version of this paper analyzes HFT performance in the E-mini S&P 500 futures contract over a two-year" ; "sizes and lower trading volumes. Nevertheless, we generate similar findings (e.g., high industry concentration," | baron_etal_2019_hft_risk_return.txt |
| TQP book has a market-making profitability chapter | Crossref metadata | "The Profitability of Market-Making \| 319-332" | bouchaud_tqp_crossref_chapters.txt |

End of C2_LOB. Finished 2026-10-21 PDT (time of last write in log.tsv).

## Corrections after review (Stage E.28, MathReviewer G3)

- MG3-01: sec. 2.2 CdL eq. (5) now carries the reviewer's flag (eq. 5 inconsistent with eqs. 3-4; exponential tail, finite mean; not used by any pilot quantity). The rate is written "0.02 per unit time" instead of "0.02/s" because of MG3-07.
- MG3-02: secs. 5.3 and 5.8 now state that the slides fit on the first trading day of March 2011 and compare with month-average (and 3-day) mid changes; the calibration day is inside the validation month.
- MG3-03: sec. 7.2 lognormal limit changed from kappa -> 0 to kappa -> infinity, with the WP misprint noted.
- MG3-04: sec. 10.2 now R_1 = S/(2 lambda_inf), lambda_inf = 1/(1 - C_1); R_1 = S/2 only when C_1 = 0.
- MG3-07: sec. 2.5 "per second" removed from the CdL example (source gives no unit); also marks the t^-2 tail as the eq. (5) claim.
- MG3-11: sec. 6.3 -11.5% relabelled as the non-HFT coefficient for changes in Front-of-Queue Depth (HFTs -42.0%); -2.2% is the level.
- MG3-12: sec. 8.8 "six tickers" changed to "nine tickers".
