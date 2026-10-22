# E.28 methods brief, deep dive C2_Pooled: single-contract versus pooled multi-contract order-book models

Worker C2_Pooled (Opus 5.5), Stage E.28, started 2026-10-21 02:41 PDT. Written section by section.
Pages: reports/stage_e28_briefs/pages/C2_Pooled/ (log.tsv lists URL, UTC and PDT fetch time, method, sha256).
Scripts: reports/stage_e28_briefs/work/C2_Pooled/. No market data was read; the only repo numbers used are
contract specifications (rules/products.py) and the A0 worker's summary statistics
(reports/stage_e28_briefs/A0_contract_stats.json, window 2022-11-01..2023-10-31, main session), cited where used.
Nothing here is registered; every "hypothesis" below is a candidate for the lead to accept, change or drop.

Notation used throughout. A contract (or stock) is indexed by i = 1..K. Time inside a contract is indexed by t
(clock time) or by k (the k-th event, for example the k-th mid-price change at time tau_k). p_a and p_b are the best
ask and bid prices, m = (p_a + p_b)/2 the mid-price, s = p_a - p_b the spread, delta_i the tick size of contract i,
q_a^(l), q_b^(l) the resting size at ask and bid level l (l = 1 is the best level). "Pooled" or "universal" means
one parameter vector theta is fit on data from several contracts; "asset-specific" means one theta_i per contract.

## 0. Bottom line first (details and sources below)

- The universality evidence (Sirignano and Cont 2019) is real but comes from about 1000 NASDAQ stocks, billions of
  events, 25 GPU nodes for the pooled model and about 500 for the per-stock models, and a target (the sign of the next
  mid-price change) that is not a trading P&L. The paper reports no costs, no trading rule and no futures. Its useful
  lessons are structural: (a) pooling helped most where the single-instrument sample was small; (b) a test on
  instruments never seen in training, in a later period, is a clean extra out-of-sample check; (c) a longer training
  history helped rather than hurt.
- Later evidence is mixed. Lucchese, Pakkanen and Veraart (2024), with a formal model-confidence-set test on 10
  NASDAQ stocks, found that universal (pooled) models gave results "partially inconsistent" with stock-specific ones
  and found no predictability for some training stocks (CHTR, AAPL), while still finding it for some unseen stocks.
  DeepLOB's unseen-stock test cost 0.06 to 1.55 accuracy points. LOBCAST (Prata et al. 2024) found that "all models
  exhibit a significant performance drop when exposed to new data". A crypto transformer (LiT, 2025) lost about 5% two
  to three months after training. Every equity LOB study that reported trading used mid prices or ignored fees; the one crypto taker backtest (5.4) nets
  taker fees but models no latency.
- No paper was found that pools order-book models across CME futures and tests on a held-out futures contract; this is
  a literature gap found by this search, not a finding either way.
- For a 1-lot passive order the quantities that matter (fill probability, queue time, markout) are contract-specific
  in ticks and lots. Pooling needs causal normalization: prices in ticks or in each contract's own trailing sigma,
  depth divided by trailing average depth, queue position in seconds of volume, labels with per-contract thresholds
  (Section 6). On A0's numbers, main-session 1-minute sigma is 6.61 ticks on MES and 27.83 on NQ (so MNQ), a 4.2x gap.
- Pooled samples are not independent: with cross-contract correlation 0.6, three contracts carry about 1.36
  contracts' worth of independent outcome information (Section 6.4). Inference must cluster by trade date.
- Phased design (Section 7): phase 1 one contract, every configuration counted into N; phase 2 one pre-named pool of
  2 to 3 contracts matched on tick regime and sigma-in-ticks (MES with M2K and/or MYM qualify on sigma; MNQ does not),
  one frozen configuration, scored once on a later block for the pool and for a pre-named unseen contract. A
  disciplined phase 2 adds about 2 to N; an open grid could add over 100.
- Compute: all of this fits the laptop (minutes for tree models, hours per configuration for a small LSTM); cloud GPUs
  cost $0.27 to $0.89 per hour for 24 GB cards (RunPod page fetched 2026-10-21) and are optional.

## 1. Sirignano and Cont (2019): the universal price-formation model

Source: Sirignano, J. and Cont, R. (2019), "Universal features of price formation in financial markets:
perspectives from deep learning", Quantitative Finance 19(9), 1449-1459, doi 10.1080/14697688.2019.1622295
(Crossref, file `crossref_sc_doi.json`); full text read from arXiv 1803.06917, file
`sirignano_cont2019_universal.pdf` / `.txt`.

### 1.1 Core idea in plain words

Treat "how the next price change depends on the recent history of the order book" as one unknown function F. Ask
whether F is the same for every stock. Fit a single recurrent neural network on the pooled data of about 500 stocks,
then (a) compare it with one network per stock, (b) test it on about 500 other stocks it never saw, and (c) test it
months after the training period. The paper finds the pooled ("universal") network wins on (a), works on (b) and
does not decay on (c). The authors read this as evidence that price formation has common, stationary structure,
so data from many assets can be pooled to get the sample sizes deep learning needs.

### 1.2 Data and design (as stated in the paper)

- About 1000 NASDAQ stocks, 2014-01-01 to 2017-03-31, reconstructed from NASDAQ Level III (message) data with
  LOBSTER: "a high-frequency record of all orders, transactions and order cancellations for approximately 1000 stocks
  traded on the NASDAQ between January 1, 2014 and March 31, 2017".
- Split by stock: "We split the universe of stocks into two groups of roughly 500 stocks; training is done on
  transactions and quotes for stocks from the first group."
- Split by time: training January 2014 to May 2015; main test June-August 2015; a later test January-March 2017.
  "All results are out-of-sample in time." "Typically, the out-of-sample dataset is a 3-month time period."
- Event clock: the target is the sign of the next mid-price change, at the random times tau_1, tau_2, ... at which
  the mid-price changes; "step Δk = τk+1 − τk is on average 1.7 seconds in the dataset".
- Pooling without normalization: "Data from various stocks were pooled together for this purposes without any
  specific normalization." Normalizations the authors tried "based on average volume, volatility or average spread,
  or partitioning the training data into sectors or categories such as large/small tick stocks do not improve
  training results."
- Compute: about 500 GPU nodes for the stock-specific models; the universal model trained "across 25 GPU nodes using
  asynchronous stochastic gradient descent" (Blue Waters supercomputer grant acknowledged).

### 1.3 Model and equations

Target. Let tau_k be the k-th time the mid-price m changes, and X_{tau_0:k} the order-book states observed up to
tau_k. The model estimates the two conditional probabilities (paper, Section 3, text)

    P[ m(tau_{k+1}) - m(tau_k) > 0 | X_{tau_0:k} ]   and   P[ m(tau_{k+1}) - m(tau_k) < 0 | X_{tau_0:k} ].

Because tau_{k+1} is by construction a time when m changes, the two probabilities sum to 1: this is a binary
up/down classification on an event clock. It says nothing about WHEN the next change happens or how big it is.

Recurrent form (paper, eq. 2.1):

    (Y_t, h_t) = f(X_t, h_{t-1}; theta)

- t: index of price changes (event time, not clock time).
- X_t: the order-book state at event t (the arXiv text does not list the exact feature vector; the companion paper,
  Section 2 below, uses sizes at the first 50 nonzero levels on each side).
- h_t: the network's hidden ("memory") state, a nonlinear summary of X_s for s <= t.
- Y_t: the predicted probability distribution of the next move (softmax output).
- theta: the network weights, shared across time AND, for the universal model, across all training stocks.
- f: 3 stacked LSTM layers then a ReLU feed-forward layer and a softmax ("Both are deep neural networks with 3 LSTM
  layers followed by a ReLU layer. All layers have 50 units", Figure 6 caption; a 150-unit version is also fit).

The LSTM cell inside f is the standard one (Hochreiter and Schmidhuber 1997; textbook form, not printed in this
paper). For input x_t, previous hidden state h_{t-1} and cell state c_{t-1}:

    i_t = sigma(W_i x_t + U_i h_{t-1} + b_i)        input gate, values in (0,1)
    f_t = sigma(W_f x_t + U_f h_{t-1} + b_f)        forget gate
    o_t = sigma(W_o x_t + U_o h_{t-1} + b_o)        output gate
    g_t = tanh(W_g x_t + U_g h_{t-1} + b_g)         candidate update
    c_t = f_t * c_{t-1} + i_t * g_t                 cell state (* is elementwise product)
    h_t = o_t * tanh(c_t)                           hidden state passed on

sigma is the logistic function 1/(1+e^-z). The forget gate f_t lets the cell keep information for many steps, which
is how the model can use "history ... over many past observations". A layer with input width d_x and H units has
4 (H (H + d_x) + H) parameters.

Training objective: "minimizing a regularized negative log-likelihood objective function using a stochastic gradient
descent algorithm", with backpropagation through time truncated at a lag T. For a binary target y_k in {0,1}
(1 = up) and predicted up-probability phat_k = Y_k, the negative log-likelihood over n events is

    L(theta) = - sum_k [ y_k log phat_k + (1 - y_k) log(1 - phat_k) ] + lambda ||theta||^2,

where lambda >= 0 is the regularization weight (the paper says "regularized"; the penalty form is not stated in the
text, so the l2 form here is an assumption).

Pooling. Stock-specific models solve min over theta_i of L_i(theta_i) for each stock i separately. The universal
model solves min over theta of sum_i L_i(theta), with mini-batches "selected at random from all stocks". Nothing in
the loss tells the network which stock a sample came from; the only way it can adapt to a stock is through the
inputs X_t themselves.

Score (paper, Section 3):

    A_i = (number of price changes where the model correctly predicts the direction for stock i)
          / (total number of price changes)  x 100%.

Baseline (paper, eq. 3.-1, a linear state-space model with probit/logit link):

    h_t = A h_{t-1} + B X_t,    Y_t = P(dP_t > 0 | X_t, h_t) = G(C X_t + D h_t),

with A, B, C, D matrices of coefficients and G a link function (logistic gives a softmax of a linear function).

### 1.4 What it estimates or decides

It estimates a direction probability for the next mid-price change. It decides nothing about orders, size or timing;
it is a forecasting model. The test of "universality" is a comparison of out-of-sample accuracy A_i across models
(asset-specific vs universal) and across stocks (seen vs unseen).

### 1.5 Results reported (verbatim; figures carry most numbers and were not machine-readable)

- Nonlinear vs linear: stock-specific deep model vs stock-specific linear model: "a substantial increase in accuracy,
  between 5% to 10% for most stocks"; universal nonlinear vs stock-specific linear "improves the forecasting accuracy
  by around 10%".
- Universal vs stock-specific: "the universal model consistently outperforms the stock-specific models"; it "most
  strongly outperforms the stock-specific models on stocks with less data".
- Unseen stocks, Table 1: the universal model trained only on stocks 1-464 beat the stock-specific models on 25 of 25
  held-out stocks (465-489), by an average 1.45 percentage points, and was roughly equal (-0.15 points, better on
  4/25) to a universal model that had also seen those stocks.
- Stationarity, Table 2: a model trained on 19 months beat models trained on the 1, 3 or 6 months just before the
  test, on 100% of 50 stocks, by an average 7.2, 3.7 and 1.6 points. "The message is simple: use all available data,
  rather than an arbitrarily chosen time window." Accuracy on unseen stocks in January-March 2017, "18 months after
  the training period", is described as "stable, without any adjustments" (Figure 10).
- History: 5000 lags (about 2 hours of events) beat 100 lags (Figure 12).
- Significance claim: "Given the large size of the data set, even a small deviation (i.e. 1%) from this 50%
  benchmark is statistically significant."

What is NOT reported: no trading rule, no P&L, no transaction costs, no latency, no futures or FX, no confidence
intervals or multiple-comparison control for the many models compared, and no absolute accuracy levels in the text
(they are only in histograms). The validation-set design for the universal model is not described in the text.

### 1.6 Worked examples

(a) Why "1% is significant" at their scale but needs care at ours. If predictions were independent coin flips, the
standard error of an accuracy estimate from n events is sqrt(0.25/n). For n = 1,000,000 test events,
SE = sqrt(0.25/10^6) = 0.0005 = 0.05 percentage points, so a 1-point gain is 0.01/0.0005 = 20 SE. To reach a
z of 3 on a gain d one needs n = (3 x 0.5 / d)^2: d = 0.02 needs 5,625; d = 0.01 needs 22,500; d = 0.005 needs
90,000 INDEPENDENT events. Event-clock forecasts on one contract are serially dependent (overlapping histories,
clustered activity), so the effective n is smaller than the event count; a block bootstrap by day, or a
Newey-West variance on the daily mean of correct-minus-0.5, is the honest version.

(b) Accuracy is not money. Suppose a model predicts the next MES mid-price change with 55% accuracy and the typical
mid-price change is half a tick (one side of a one-tick spread moves). The expected signed mid move per prediction
is (2 x 0.55 - 1) x 0.5 tick x $1.25 = 0.10 x $0.625 = $0.0625 per contract. A taker round trip on MES costs about
one tick of spread ($1.25) plus $1.22 round-turn commission (rules/products.py:154, MES tick 0.25 = $1.25, 122
cents), $2.47 in all: about 40 times the edge. Direction forecasts at this horizon can only matter to this program
as a FILTER for passive orders (cancel or skip a quote when an adverse move is likely), which is what Section 1.7
turns into a hypothesis.

### 1.7 Pilot hypothesis it suggests (candidate, not registered)

H-SC1 (adverse-selection filter, one contract). On the pilot contract, a direction model fit on the training block
predicts the sign of the next mid change; among simulated 1-lot passive bid fills (and symmetric ask fills), the
10-second markout of fills where the model's predicted adverse-move probability is in its top tercile is worse than
in its bottom tercile.
- Test statistic: difference in mean 10 s markout in ticks (bottom-tercile minus top-tercile fills), with a day-block
  bootstrap or a Newey-West t on daily differences; one-sided; the pass rule (for example t > 3.0) set by the lead.
- Sample: fills, not events, are the unit. If the markout SD per fill is about 1 tick (to be measured by the pilot)
  and the true tercile gap is 0.1 tick, each tercile needs about 2 x (3 x 1 / 0.1)^2 = 1,800 fills for z = 3
  (two-sample, equal variances); about 5,400 fills in all, before allowing for dependence.
- Trial count: one model family; if the lead allows 2 history lengths (100, 1000 events) x 2 widths (50, 150 units),
  that is 4 configurations, plus 1 per markout horizon used (1, 10, 60 s) if all three are tested: up to 12 added to N.
  Fixing the horizon at 10 s in advance keeps it at 4.

### 1.8 Data and compute for this program

Data: Databento mbp-10 gives the top 10 levels per side and every book update; that is enough for the event-clock
direction target and level-1..10 sizes. mbo adds queue position (needed for the filter's fill simulation, not for the
direction model itself). tbbo alone is not enough (top of book at trades only, no depth history). Four to twelve
months of one contract is far below the paper's scale (their one year of pooled data is "roughly equivalent to using
500 years (!) of data for training a single-stock model"), so the program should expect a smaller, LSTM-or-simpler
model and should treat a gradient-boosting or logistic baseline as the bar to beat.
Compute: a 3x50 LSTM with about 40 inputs has roughly 4(50x90+50) + 2 x 4(50x100+50) = 18,200 + 40,400 = 58,600
recurrent parameters, small enough for the RTX 3050 (Section 8 has the time and cloud-cost estimate).

### 1.9 Honest evidence

- In-sample-free design: time-out-of-sample and asset-out-of-sample, which is stronger than most of the literature.
- But: direction of the next mid change is a "statistical" target; there is no cost-inclusive result. The program's
  own experience (E.25: limit orders rescue no earlier rule) and the taker arithmetic in 1.6(b) say this target alone
  does not pay at retail latency (tens of milliseconds from Vancouver to Aurora).
- Equities differ from CME futures in ways that matter for pooling: many NASDAQ stocks are "large tick" or "small
  tick" with very different queue sizes; the paper says partitioning by tick size did not help, but it did not pool
  across different asset classes or exchanges.
- Later independent tests (Sections 3 to 5) give a more cautious picture.

## 2. Sirignano (2019): deep learning for limit order books (the "spatial neural network")

Source: Sirignano, J. A. (2019), "Deep learning for limit order books", Quantitative Finance 19(4), 549-570,
doi 10.1080/14697688.2018.1546053 (Crossref, file `crossref_sirignano2019.json`); full text arXiv 1601.01987v7,
file `sirignano2019_dl_lob.pdf` / `.txt`.

### 2.1 Core idea in plain words

Predict the whole probability distribution of how many ticks the best ask and best bid will move (over 1 second, or
at the next price change), not just the direction. Instead of one big softmax over every possible move, model the
distribution as a chain of "does it stop here, given it got this far?" probabilities, each computed by a small
network that looks mostly at the book near that price level ("local spatial structure"). This uses deep-book
information well and is cheap. Important for this brief: the paper is NOT a pooled model. "Models are trained and
tested separately on each stock; i.e., a new randomly initialized model is trained for each stock." It is the
single-asset counterpart that Sirignano and Cont later pooled.

### 2.2 Data

489 stocks (mostly S&P 500 and NASDAQ-100), 2014-01-01 to 2015-08-31, "roughly 50 terabytes of raw data". "Each sample
contains a vector of length 200, recording the state of the limit order book across the first 50 bid and ask nonzero
levels." About 10 million samples per stock at the 1-second horizon (Case 1); on average 5 million per stock at the
next-price-change horizon (Case 2). Split: "The test set is all data from June 1, 2015 to August 31, 2015. The
training data is composed of 95% of the data from January 1, 2014 to May 31, 2015 (drawn at random). The validation
set is the remaining 5%". Inputs exclude prices: they "only include the sizes ... at each level of the limit order
book and not the actual prices".

### 2.3 Equations

One-sided move Y in {r_1, r_2, ...} (number of levels the best ask moves up, say). With a neural network
f_theta(x, y) that takes the book state x and a candidate level y (paper, eq. 10):

    P[ Y = y | Y >= y, X = x ] = exp(f_theta(x, y)) / (1 + exp(f_theta(x, y)))

This is a discrete hazard ("stop here") probability, "analogous to a 'geometric random variable' with a non-constant
probability of increasing at each step". The unconditional probabilities follow by the chain rule:

    P[Y = y_j | x] = H(x, y_j) * prod_{l < j} (1 - H(x, y_l)),   H(x, y) = P[Y = y | Y >= y, X = x].

Log-likelihood of one sample (x, y) (paper, eq. 11):

    L = log( e^{f(x,y)} / (1 + e^{f(x,y)}) ) + sum_{y' < y} log( 1 / (1 + e^{f(x,y')}) ),

so only the levels up to the observed y need evaluating. Well-posedness (Theorem 4.1): the probabilities sum to 1 if
the hidden units are bounded (tanh, sigmoid, clipped ReLU); with plain ReLU the model may have "probability mass escaping to +∞".
Several dimensions (best ask move Y_1, best bid move Y_2) are handled by "dimension splitting" (paper, eq. 12):

    P[Y = (y_1..y_d) | X = x] = P[Y_1 = y_1 | x] * prod_{i=2..d} P[Y_i = y_i | Y_{1:i-1} = y_{1:i-1}, x],

so the cost grows linearly in d (eq. 13 is the matching log-likelihood). A separate 3-way classifier for
{up, no change, down} "stitches" the positive and negative halves together.

### 2.4 What it estimates or decides

The conditional distribution (including tails) of best-bid and best-ask moves. For a passive order, that is directly
the distribution of how far the market runs through or away from the order's price after a fill, i.e. the
distribution of the markout in ticks. It decides nothing by itself.

### 2.5 Results (verbatim)

"The spatial neural network outperforms the standard neural network on 94% of stocks in Case [1] and 97% of stocks in
Case [2]. The average decrease in error for modeling the joint distribution is 0.6% and 3.5% in Case [1] and Case [2]"
(error is cross-entropy). Neural networks have "on average 10% lower error" (Case 1) and "20% lower error" (Case 2)
than logistic regression. "For typical stocks, the best ask price changes only 5-15% of the time in Case [1]."
Compute: "a cluster with 50 GPUs"; "model training takes over 3,000 'GPU node hours'". The spatial network has "20,000
parameters" against "over 170,000" for the standard network. No trading or cost results.

### 2.6 Worked example (hazard chain)

Suppose that, after a passive bid fill on MES, the model gives hazards for the best bid dropping by 1, 2, 3 ticks:
H(1) = 0.7, H(2) = 0.6, H(3) = 0.5. Then P(drop = 1) = 0.7; P(drop = 2) = (1 - 0.7) x 0.6 = 0.18;
P(drop = 3) = 0.3 x 0.4 x 0.5 = 0.06; P(drop >= 4) = 0.3 x 0.4 x 0.5 = 0.06. The four add to 1.00. The expected
drop is at least 0.7x1 + 0.18x2 + 0.06x3 + 0.06x4 = 1.48 ticks ($1.85 on MES), a lower bound because the >= 4 bin
is counted at 4. A model is useful if these numbers change with the book state enough to change a quoting decision.

### 2.7 Pilot hypothesis it suggests

H-S1 (tail of adverse markout). Deep-book depth (levels 2-10 on the side of the fill) predicts the probability that
the 1-second markout of a filled passive 1-lot is <= -2 ticks. Test statistic: out-of-sample log-loss of the hazard
model minus log-loss of the unconditional empirical distribution of markouts (the paper's "naive empirical model"),
per day, averaged, with a Newey-West t over days. Sample: tail events are rare; if P(markout <= -2) is about 5% and
one wants about 400 tail events in the test block, that needs about 8,000 test fills. Trial count: 1 model family; 2
widths x 2 feature sets (levels 1-3, levels 1-10) = 4 configurations; mbp-10 is sufficient (no queue identity
needed because the outcome is a price move, not a fill). Compute: tiny (20,000 parameters).

### 2.8 Evidence and caveats

Out-of-sample in time on 489 stocks, but: the 95/5 random train/validation split inside the training period lets
neighbouring (highly dependent) samples sit on both sides, so early stopping is mildly optimistic (the test block is
clean). No costs. Equities only.

## 3. Lucchese, Pakkanen and Veraart (2024): universal models under a formal model-comparison test

Source: Lucchese, L., Pakkanen, M. S. and Veraart, A. E. D. (2024), "The short-term predictability of returns in
order book markets: A deep learning perspective", International Journal of Forecasting 40(4), 1587-1621,
doi 10.1016/j.ijforecast.2024.02.001 (Crossref, file `crossref_lucchese.json`); full text arXiv 2211.13777v3,
file `lucchese2024_predictability.pdf` / `.txt`.

### 3.1 Core idea in plain words

Ask, with a proper statistical test, whether deep models beat a no-information benchmark at horizons of 10 to 1000
order-book events, which input representation works best, and whether one model can serve several stocks. Their
answer to the last question: sometimes, inconsistently.

### 3.2 Data and design

LOBSTER NASDAQ data, "115 Nasdaq tickers from January 2, 2019, to January 31, 2020", of which "a subset of 10 stocks"
were used (Table 1: from LILAK with 3.77 thousand price changes a day to AAPL with 127.86 thousand). The 55 weeks are
split into W = 11 five-week windows; in each, the first four weeks train and validate (5 random days for
validation) and the fifth week tests. The universal experiment: train on the "in-sample" stocks {QRTEA, CHTR, EXC,
WBA, AAPL} and test on those plus the "out-of-sample" stocks {LILAK, XRAY, PCAR, AAL, ATVI}.

### 3.3 Equations

Information set and target. F_t = sigma(x_t, ..., x_{t-T+1}), the information in the last T order-book feature
vectors. The h-event-ahead return uses a smoothed future mid m^(k)_{t+h} = (1/(2k+1)) sum_{i=-k..k} m_{t+h+i},
with k = 5 (the paper fixes "k = 5" for all horizons), and r_{t,t+h} is its percentage change from m_t. Labels:

    c_{t,t+h} = down if r < -gamma;  same if -gamma <= r <= gamma;  up if r > gamma,
    gamma_hat_h = ( |Q_hat_h(0.33)| + Q_hat_h(0.66) ) / 2,

where Q_hat_h is the empirical quantile function of training-set returns, so the threshold is chosen per stock, per
window and per horizon ("the choice of gamma is specific to the choice of window, horizon, and ticker").

Volume representation (Section 2.4): instead of "level 1, level 2, ..." (which jumps when a new order fills an empty
tick), use the volume at the j-th TICK from the mid, j = 1..W, on each side, giving an array in R^{T x W x 2};
it is normalized by its maximum, s -> s / max_{tau,j,x} s, "instead of the rolling window standardization" (deepLOB
and deepOF inputs use a 5-day rolling z-score). The authors give five desiderata the representation meets, among them
"all entries are in the same units" and "robust to small perturbations".

Loss and test. For model i and test window w, the out-of-sample categorical cross-entropy

    L_{i,w} = -(1/|I_w,test|) sum_{t in I_w,test} sum_{* in {down,same,up}} 1{c_t = *} log phat^i_{*,t}.

The 11 losses per model feed the model confidence set (MCS) of Hansen, Lunde and Nason (2011), which returns p-values
p_i^MCS; a model with a low p-value is statistically inferior to the best. "Definition 4.1. ... there is order
book-driven predictability at confidence level 1 - alpha if p^MCS_benchmark < alpha."

### 3.4 Results on pooling (verbatim)

- Table 8 (universal models only; low p = predictability found): for in-sample CHTR the benchmark p-value is 1.00 at
  every horizon from h = 10 to h = 1000 except 0.94 at h = 300 (no predictability found), and in-sample AAPL is 0.07
  at h = 10 and 1.00 at h = 20; but out-of-sample AAL and ATVI have p = 0.00 at h = 10 to 50.
- "using universal models leads to results that are partially inconsistent with those in Table 4 [stock-specific]";
  "universal models may be picking up different order book dynamics from those identified by stock-specific models";
  "When, instead, the ticker is mainly subject to stock-specific trading patterns, universal models have a hard time
  detecting predictability – we believe this might be the case for CHTR and AAPL."
- "It is rather remarkable that universal models can identify predictability for 'out-of-sample' stocks."
- Table 9: among universal models, the volume representation with L3 data is in the 5% MCS 92% of the time, against
  8% for deepLOB on L2 and 0% for L1 inputs: "some predictive universal patterns can be extracted only from the most
  granular data".
- On trading: "we focus on mid-to-mid returns, which are not tradable in practice"; "while the predictability
  identified in this paper might not be directly tradable through a standalone strategy, it might still help some
  market players, such as market makers, to gauge the direction of the market and adjust their quotes accordingly."
  Their conclusion: "only Nasdaq-traded stocks were considered in this paper ... It would be interesting to explore
  whether similar results are obtained for securities traded on exchanges with different market structures."

### 3.5 Worked example: why per-instrument thresholds break pooled labels

Suppose a pooled MES+MNQ model uses one common return threshold gamma = 0.7 basis points (bps) to define "up". At
assumed round price levels for illustration (MES 4500, MNQ 15500; not measured), one tick is 0.25/4500 = 0.556 bps
on MES and 0.25/15500 = 0.161 bps on MNQ. So "up" means a move of more than 0.7/0.556 = 1.26 MES ticks but
0.7/0.161 = 4.34 MNQ ticks. The same label then encodes a one-tick event on one contract and a four-tick event on
the other, and the class balance differs by contract. Lucchese et al. avoid this by choosing gamma per ticker (with
quantiles: if Q(0.33) = -0.6 bps and Q(0.66) = +0.8 bps on the training set, gamma_hat = (0.6 + 0.8)/2 = 0.7 bps),
and LOBCAST (Section 4.2) names the fixed-threshold problem explicitly. For this program the natural fix is to define
labels in TICKS of each contract, or in units of each contract's own volatility (Section 6).

### 3.6 Pilot hypothesis it suggests

H-L1 (horizon of predictability, one contract): there is order-book-driven predictability of the MES smoothed mid
return at h in {10, 50, 100} book events, in the sense of Definition 4.1 at alpha = 0.05, with the model set
{benchmark, logistic on OFI, LightGBM on the program's book features, one small deep model}. Test statistic: MCS
p-value of the benchmark over W test windows. Sample: their design uses 11 weekly test windows; 4 months of pilot
data give about 17 weeks, so about 13 test windows with a 4-week rolling train. Trial count: 3 horizons x 3 models =
9 configurations (the MCS itself handles comparison within the set, but every model-horizon pair still enters N
under V43). The lead would also need to decide whether the MCS result counts as a pass, given that it measures
mid-to-mid statistical predictability, not fill-conditional markouts.

### 3.7 Evidence and caveats

The MCS on 11 weekly losses is a small-sample test (few windows). Only NASDAQ stocks. Pooling over 5 stocks gave
inconsistent, stock-dependent results, which is the most relevant analogue for a 2-3 contract pool.

## 4. Independent checks on transfer and generalization (DeepLOB, LOBCAST, Briola et al.)

### 4.1 DeepLOB's transfer test (Zhang, Zohren and Roberts 2019)

Source: Zhang, Z., Zohren, S. and Roberts, S. (2019), "DeepLOB: Deep convolutional neural networks for limit order
books", IEEE Transactions on Signal Processing 67(11); arXiv 1808.03668, file `zhang2019_deeplob.pdf` / `.txt`.
(The architecture itself is the subject of the C2_DeepLOB brief; only the transfer evidence is used here.)

Design: trained on five LSE stocks (LLOY, BARC, TSCO, BT, VOD), one year, three-month test; "we directly apply our
model to five more stocks that were not part of the training data set (transfer learning)" (HSBC, GLEN, CNA, BP,
ITV). Normalization: z-score using "the mean and standard deviation of the previous 5 days' data".

Result (Table IV): accuracy at horizon k = 20 events 70.17% on the training stocks' test period versus 68.62% on the
five unseen stocks; at k = 50, 63.93% vs 63.44%; at k = 100, 61.52% vs 61.46%. So the unseen-stock penalty was 1.55,
0.49 and 0.06 points. Their trading illustration uses "mid-prices without transaction costs", and the authors say the
cost assumption "is not a reasonable assumption for a standalone strategy".

Reading: a small (5 + 5 stock) test, all large liquid LSE names in one market, so "unseen" is close to "similar".
That is roughly the situation of MES vs MNQ vs M2K vs MYM: same exchange, same session, similar participants.

### 4.2 LOBCAST (Prata et al. 2024): published LOB models do not generalize well

Source: Prata, M., Masi, G., Berti, L., Arrigoni, V., Coletta, A., Cannistraci, I., Vyetrenko, S., Velardi, P. and
Bartolini, N. (2024), "LOB-based deep learning models for stock price trend prediction: a benchmark study",
arXiv 2308.01915v2, file `prata2024_lobcast.pdf` / `.txt`. Journal version: Artificial Intelligence Review 57(5), 2024,
doi 10.1007/s10462-024-10715-4 (Crossref, file `crossref_lobcast.json`).

Design: 15 models re-run with 5 seeds on FI-2010 and on two new LOBSTER datasets (6 NASDAQ stocks, 10 trading days
each, July 2021 and February 2022), "a 6-2-2 days split", z-score normalization per stock. Note that this is
retraining on new stocks and periods, not zero-shot transfer.

Results (verbatim): "all models exhibit a significant performance drop when exposed to new data". Table 2: DeepLOB's
claimed F1 78.9 became 71.4 on FI-2010 and 59.5 on LOB-2021 and LOB-2022; the best model on LOB-2021 (BINCTABL) had
F1 61.2 against 55.5 for the trivial MAJORITY classifier. "All models are very sensitive to hyperparameters, in fact,
they diverged (F1-score <= 33%) during the hyperparameters search for about half of the runs." Their profit check:
"the models' profitability is far from guaranteed"; in the supplement the simulation makes "the assumption of no
transaction fees".

Relevant to pooling: "We recall that the dataset is made of different stocks. With such a labelling system, fixed
theta, stocks with low returns become associated with stable trends, as their behaviour is overshadowed by stocks
exhibiting higher returns." (This is the label-threshold problem of Section 3.5.) And: "Another weakness in dataset
generation is the potential for training, validation, and test splits to have dissimilar distributions."

Compute note: "the training process for all the models took approximately 155 hours for FI-2010 and 258 hours for
LOB-2021/2022, utilizing a cluster comprised of 8 GPUs (1 NVIDIA GeForce RTX 2060, 2 NVIDIA GeForce RTX 3070, and 5
NVIDIA Quadro RTX 6000)": consumer GPUs are adequate for this model class.

### 4.3 Briola, Bartolucci and Aste (2024 arXiv; QF 2025): microstructure decides predictability

Source: Briola, A., Bartolucci, S. and Aste, T. (2024), "Deep limit order book forecasting: a microstructural
guide", Quantitative Finance 25(7), 1101-1131, 2025, doi 10.1080/14697688.2025.2522911 (Crossref,
file `crossref_briola.json`); arXiv 2403.09267v4, file `briola2024_microstructural_guide.pdf` / `.txt`.

Design: DeepLOB trained per stock on 15 NASDAQ stocks over three years, grouped by tick regime with a practical rule
based on the mean spread <sigma> relative to the tick theta: "if (i) <sigma> >~ 3 theta, we are dealing with a
small-tick stock; if (ii) <sigma> <~ 1.5 theta, we are dealing with a large-tick stock; if (iii) 1.5 theta <~ <sigma>
<~ 3 theta, ... medium-tick".

Results: "the stocks' microstructural characteristics influence the efficacy of deep learning methods and that their
high forecasting power does not necessarily correspond to actionable trading signals"; "for large-tick stocks, the
model's predictive performance is markedly distinct with a stronger ability to correctly classify the two extreme
classes"; for small-tick stocks, "the 29% of true class 1 is misclassified as class -1". They propose scoring a model
by the probability of correctly forecasting a complete round-trip transaction, and find it is often near zero at
higher confidence thresholds (e.g. "the probability of correctly executing a trade at a threshold larger than 0.5 is
zero" for one group and horizon).

Implication for pooling: the tick regime is the first thing to match. MES trades with a one-tick spread almost all
the time during the main session (a large-tick contract by this rule; the pilot will measure it); whether MNQ, M2K
and MYM are large- or medium-tick on this rule is not known from owned data (no mbp data was read) and is a
measurement the pilot or a later purchase must make before pooling.

## 5. Other pooling, transfer and cross-asset work

### 5.1 Cont, Cucuringu and Zhang (2023): pooled OFI regressions with depth-scaled inputs

Source: Cont, R., Cucuringu, M. and Zhang, C. (2023), "Cross-impact of order flow imbalance in equity markets",
Quantitative Finance 23(10), 1373-1393, doi 10.1080/14697688.2023.2236159 (Crossref, file
`crossref_cont_crossimpact.json`); arXiv 2112.13213v4, file
`cont_cucuringu_zhang_crossimpact.pdf` / `.txt`. (OFI itself is covered by the C2_OFI brief.)

Data: "the top 100 components of S&P 500 index, existing from 2017-01-01 to 2019-12-31", Nasdaq ITCH via LOBSTER.

Equations (paper eqs. 1-4). Order flow at level m on the bid for event n of asset i:
OF^{m,b}_{i,n} = q^{m,b}_{i,n} if the level-m bid price rose, q^{m,b}_{i,n} - q^{m,b}_{i,n-1} if it is unchanged,
-q^{m,b}_{i,n-1} if it fell (ask side mirrored). Level-m OFI over (t-h, t]:

    OFI^{m,h}_{i,t} = sum_{n=N(t-h)+1}^{N(t)} ( OF^{m,b}_{i,n} - OF^{m,a}_{i,n} )                 (eq. 2)

Depth scaling, the key normalization for pooling (eq. 3): "Due to the intraday pattern in limit order depth, we use
the average size to scale OFIs":

    ofi^{m,h}_{i,t} = OFI^{m,h}_{i,t} / Q^{M,h}_{i,t},
    Q^{M,h}_{i,t} = (1/M) sum_{m=1}^{M} (1/(2 dN(t))) sum_{n=N(t-h)+1}^{N(t)} ( q^{m,b}_{i,n} + q^{m,a}_{i,n} ),

the average depth over the first M = 10 levels in the same window, dN(t) the number of events in the window. The
"integrated OFI" is the first principal component of the 10 scaled level-OFIs, weights normalized to sum to 1 (eq. 4;
the first component "can explain over 89% of the total variance among multi-level OFIs").
Findings: "once the information from multiple levels is integrated into OFI, multi-asset models with cross-impact do
not provide additional explanatory power for contemporaneous impact compared to a sparse model without cross-impact
terms. On the other hand, we show that lagged cross-asset OFIs do improve the forecasting of future returns" and
"this lagged cross-impact mainly manifests at short-term horizons and decays rapidly in time." Their economic test:
"the strategy ignores trading costs, as this is not the focus of our paper."

Lesson: dividing order flow by the instrument's own recent average depth makes OFI unit-free and comparable across
instruments with very different queue sizes (the MES-vs-ES case is the extreme one). Cross-asset information is a
separate question from pooling: for MES, lagged ES/NQ order flow could be a FEATURE even in a single-contract model.

### 5.2 Wu et al. (2021): representations that survive pooling

Source: Wu, Y., Mahfouz, M., Magazzeni, D. and Veloso, M. (2021), "Towards robust representation of limit orders
books for deep learning models", arXiv 2110.05479, file `wu2021_robust_representation.pdf` / `.txt`. Point used:
level-indexed inputs violate the assumption that each input channel "stands for signals from the same source", and
"a small perturbation would leads to shift of price levels and thus the representation would be affected". Their fix
(a mid-centred moving window of volume per tick) is the one Lucchese et al. adopted (Section 3.3), and it is
naturally expressed in ticks, which is what pooling across contracts needs.

### 5.3 Partial pooling: QuantNet (Koshiyama et al. 2020)

Source: Koshiyama, A., Blumberg, S. B., Firoozye, N., Treleaven, P. and Flennerhag, S. (2020), "QuantNet:
transferring learning across trading strategies", arXiv 2004.03445v2, file `koshiyama2020_quantnet.pdf` / `.txt`.
Daily data on "3103 assets in 58 global equity markets", not order books; included for its architecture. Each market
i has its own encoder and decoder around one shared layer omega (paper eqs. 3-4):

    z^i_t = omega(e^i_t),  e^i_t = enc_i(r^i_{t-1}, e^i_{t-1});   s^i_t = tanh(W^i d^i_t + b^i),  d^i_t = dec_i(z^i_t, d^i_{t-1})

so "market-specific parameters are free to specialize on the problem at hand, whilst market-agnostic parameters are
driven to capture signals from all markets". Reported: "51% higher Sharpe and 69% Calmar ratios" than the best
baseline and "improvements of 15% and 41% in Sharpe and Calmar ratios" over the no-transfer variant. Lesson: between
"one model per contract" and "one model for all" sits partial pooling (shared core, contract-specific input and output
layers, or simply a contract indicator feature). The statistical analogue is a hierarchical (random-effects) model:
theta_i = theta + u_i, u_i ~ N(0, tau^2), which shrinks each contract's estimate toward the pooled one by an amount
the data choose (Section 6.5).

### 5.4 Crypto: cross-asset stability with scale-free features, and decay over time

- Bieganowski and Slepaczuk (2026), "Explainable patterns in cryptocurrency microstructure", arXiv 2602.00776,
  file `crypto_explainable_patterns2026.pdf` / `.txt`. Binance perpetual futures, 1-second data, 2022-01-01 to
  2025-10-12, five coins. Models are fit per asset ("For each asset analyzed, we persist both the model ..."), with
  walk-forward cross-validation with a purge gap. Finding: "the same engineered order book and trade features exhibit
  remarkably similar predictive importance and SHAP dependence shapes across assets spanning an order of magnitude in
  market capitalization". Their normalization advice: "Relative measures such as spreads-to-mid or VWAP-to-mid
  deviations are preferred ... These ratios are inherently scale-invariant". Caveat: their taker backtest reports
  annualized returns on capital of 4.06 to 7.00 (that is 406% to 700%) on three small coins (gross or net of taker fee not stated in the table) while "Latency is not
  explicitly modeled; results should be interpreted as an upper bound in the fastest regime"; such numbers are not
  credible evidence of retail tradability.
- Xiao et al. (2025), "LiT: limit order book transformer", Frontiers in Artificial Intelligence, doi
  10.3389/frai.2025.1616485, files `frontiers_frai2025_1616485.pdf`, `lit_lob_transformer_pmc.txt`. Binance L2 data,
  one model pre-trained on September 2024 and tested on later months: "we observe a significant decline of around 5%
  in most metrics in November and December, falling even below the from-scratch baselines. This confirms the presence
  of a distribution shift". Fine-tuning on recent data recovered performance. This is direct counter-evidence to the
  Sirignano-Cont stationarity finding, in a different market.

### 5.5 Futures and FX: what was found, and what was not

- No paper was found (arXiv API queries for "limit order book" with futures and deep learning, with transfer
  learning, with cross-asset; 3 web searches) that trains a pooled LOB model on several CME futures and tests it on a
  held-out futures contract. This is a gap in the literature found by this search, not evidence that pooling fails
  or works on futures.
- Futures LOB studies found are single-instrument: CAC 40 index futures fill-time model (KANFormer, arXiv 2512.05734,
  abstract only [unverified]: "We evaluate the model using CAC 40 index futures data with labeled orders"), Bund
  futures queue-reactive simulator (arXiv 2501.08822, full text saved by the C2_LOB reader, pages/C2_LOB/dl_meets_qr_2025.txt:
  "trading days over three months from March to June 2022"), Eurodollar futures sizing (arXiv 2007.15982, title only [unverified]); a Chinese rebar futures CNN-LSTM
  (SPIE 2022, search snippet only [unverified]).
- Kolm, Turiel and Westray (2023), "Deep order flow imbalance: Extracting alpha at multiple horizons from the limit
  order book", Mathematical Finance 33(4), 1044-1081 (115 NASDAQ stocks): the full text could not be fetched (SSRN
  403, Wiley returned a Cloudflare challenge; logged). From search snippets only [unverified]: stock-specific models,
  stationary order-flow inputs beat raw book states, and the effective forecast horizon is about two average price
  changes.

## 6. How to normalize features so contracts can be pooled

The literature splits into two camps. Sirignano and Cont pooled raw inputs and found normalization did not help
(their stocks all trade in cents on one exchange). Everyone working with labels in returns or with queue sizes that
differ by orders of magnitude normalizes (Lucchese et al. per-ticker gamma and max-scaling; DeepLOB 5-day rolling
z-score; Cont et al. depth scaling; LOBCAST's warning on fixed thresholds; crypto "scale-invariant" ratios). For CME
equity-index futures the candidates for a pool share an exchange, a session and participants, but their tick values,
queue sizes and volatility in ticks differ a lot. Each normalization below must be CAUSAL: computed only from data
before the moment it is used (a trailing window), never from the full sample, or it is look-ahead leakage.

### 6.1 The quantities and their natural units

| Quantity | Raw unit | Pool-ready form | Why |
|---|---|---|---|
| Price change, markout | index points | dm / delta_i (ticks), or dm / (delta_i sigma_i) | ticks are the exchange's own grid; sigma-units make a "big move" mean the same thing |
| Spread | points | s / delta_i (ticks) and an indicator s = 1 tick | tick regime (Briola rule: mean spread <~ 1.5 ticks is large-tick) |
| Depth, queue size | lots | q / Qbar_i (Cont et al. eq. 3), or log(1 + q / Qbar_i) | ES is 10 times MES in size (multiplier 50 vs 5, rules/products.py:153-154), so lots are not comparable; MNQ vs MES differ again |
| Queue position | lots ahead | lots ahead / queue size (fraction), and lots ahead / lambda_i (seconds of volume) | fill probability depends on how long the queue takes to clear |
| Order flow (OFI) | lots | OFI / Qbar_i (Cont et al.) | unit-free imbalance |
| Time | seconds | event time, or seconds x lambda_i (events per second) | activity rates differ by contract and time of day |
| Labels | P&L | ticks per 1-lot, per contract; class thresholds per contract (Lucchese) | a pooled common threshold mixes 1-tick and 4-tick events (Section 3.5) |

Here delta_i is contract i's tick, sigma_i a trailing volatility in ticks (for example over the previous 5 sessions
at a fixed clock or event interval), Qbar_i trailing average depth over the top M levels, lambda_i trailing traded
volume per second at one side.

### 6.2 Worked example: volatility in ticks for the candidate contracts

The A0 worker measured main-session 1-minute mid-price volatility in ticks over 2022-11-01..2023-10-31
(reports/stage_e28_briefs/A0_contract_stats.json, field `sigma_1m_ticks`): MES 6.61, NQ 27.83, RTY 10.01, YM 12.14.
Micro and mini contracts on the same index share the price and the tick in points (rules/products.py: MNQ and NQ
0.25; M2K 0.10; MYM 1.00), so MNQ ~ NQ, M2K ~ RTY, MYM ~ YM in ticks (an inference, not a measurement of the micros).
A one-tick move is therefore 1/6.61 = 0.151 sigma on MES but 1/27.83 = 0.036 sigma on MNQ. A pooled model whose
label is "markout <= -1 tick" asks a 4.2 times (27.83/6.61) smaller question of MNQ. In dollars the per-minute sigma
is 6.61 x $1.25 = $8.26 (MES), 27.83 x $0.50 = $13.92 (MNQ), 10.01 x $0.50 = $5.01 (M2K), 12.14 x $0.50 = $6.07
(MYM) per contract. Two pool-ready choices: (a) labels in sigma units (markout / (delta_i sigma_i)); or (b) pool only
contracts whose sigma in ticks is within a factor of about 2 (MES 6.61, M2K about 10, MYM about 12 are; MNQ about 28
is not). Choice (b) is simpler and is what Section 7 recommends; it must be fixed before any pooled fit.

### 6.3 Worked example: queue depletion time as the pool-ready queue measure

A passive 1-lot fills when the queue ahead of it is consumed by trades or cancellations. A unit-free measure is the
time the queue would take to clear at the contract's trade rate: T_clear = (lots ahead) / lambda_i. A0's median
main-session volume per minute (front month, field `vol_per_min_main_median`): MES 1637, NQ 984, RTY 255, YM 226
contracts. If about half the volume trades at one side, lambda = 1637/60/2 = 13.6 lots/s on MES. With an assumed
300 lots ahead (illustrative, not measured), T_clear = 300/13.6 = 22 s. For the minis with assumed 15 (NQ), 10 (RTY)
and 8 (YM) lots ahead, T_clear = 1.8, 4.7 and 4.2 s. Raw lots-ahead (300 vs 15) would mislead a pooled fill model;
seconds-of-volume puts the contracts on one axis. The pilot will measure the actual queue sizes for one contract;
the others need a purchase.

### 6.4 Worked example: pooled samples are not independent

If three contracts are pooled and the per-observation outcomes (for example the 10 s markout sign) have pairwise
correlation rho across contracts at the same time, the variance of their average is sigma^2 (1 + 2 rho)/3, so the
effective number of contracts is K_eff = K / (1 + (K - 1) rho) (derivation: Var(mean of K equicorrelated variables)
= sigma^2 [1 + (K - 1) rho] / K; set equal to sigma^2 / K_eff). For K = 3: rho = 0.3 gives K_eff = 3/1.6 = 1.88;
rho = 0.6 gives 3/2.2 = 1.36; rho = 0.8 gives 3/2.6 = 1.15; rho = 0.9 gives 1.07. Equity-index futures co-move
strongly at seconds-to-minutes horizons (the correlation for the program's contracts was not measured here; it is an
assumption to be measured), so a pooled MES+M2K+MYM sample is likely worth between 1 and 2 contracts' worth of
independent outcome information. This is why the inference unit must be the trade DATE across all contracts (a
cluster), not the individual event or fill. Queue and fill dynamics may be less correlated than price moves, which
is the case where pooling can add real information.

### 6.5 Worked example: partial pooling by shrinkage

Suppose phase 1 and a later purchase give mean 10 s markouts per passive fill of -0.30 ticks on MES (standard error
0.05), -0.45 on MNQ (0.08) and -0.20 on M2K (0.10) (illustrative numbers). The standard random-effects model
y_i = mu + u_i + e_i, u_i ~ N(0, tau^2), e_i ~ N(0, s_i^2) (DerSimonian-Laird method of moments; standard formula,
derivation not reproduced here) gives: fixed-effect mean sum(w_i y_i)/sum(w_i) with w_i = 1/s_i^2 equal to -0.320;
heterogeneity Q = sum w_i (y_i - ybar)^2 = 4.24 on K - 1 = 2 degrees of freedom; tau^2 = (Q - 2) /
(sum w - sum w^2 / sum w) = 0.0062 (tau = 0.079 ticks); random-effects mean mu = -0.322 (SE 0.063). Each contract's
shrunk estimate is B_i mu + (1 - B_i) y_i with B_i = s_i^2 / (s_i^2 + tau^2): MES B = 0.287, estimate -0.306; MNQ
B = 0.507, -0.385; M2K B = 0.616, -0.275. The noisiest contract borrows most from the pool, which is the
Sirignano-Cont observation ("most strongly outperforms ... on stocks with less data") in its simplest statistical
form. With K = 3, tau^2 is itself very poorly estimated; this is a reason to keep the phase-2 pool small and
pre-specified, and to report the per-contract results next to the pooled one.

## 7. What this implies for a phased design (one contract, then a pooled model tested on an unseen contract)

Everything in this section is a proposal for the lead. Pass rules, caps and the contract list are lead decisions.

### 7.1 Phase 1: one contract

- Data: the pilot schema (mbp-10 or mbo) for one contract, 2023-11..2024-02 plus any earlier extension. No pooling.
- Models: the simplest credible ones first (logistic / LightGBM on depth-scaled OFI, spread in ticks, queue position
  in seconds-of-volume), and at most one small sequence model. The Sirignano-Cont and DeepLOB results were obtained
  with hundreds of millions to billions of events; one contract for 4 months is far smaller, so a deep model is not
  expected to beat a tuned tree model and should be included only as a counted configuration.
- Targets that matter to a 1-lot passive order: fill within the order's life (yes/no), time to fill (survival),
  markout at 1, 10 and 60 s conditional on a fill, in ticks of the contract.
- Purpose for phase 2: phase 1 fixes the feature definitions, the normalizations (Section 6), the label definitions
  and the validation code, all frozen before any second contract's data is opened.

### 7.2 Phase 2: pooled model on 2 to 3 similar contracts, tested on an unseen one

Choosing "similar" by a rule fixed in advance (candidate rule): same exchange and session (CME Globex equity index),
same tick regime by the Briola spread rule (measured on the training block only), and main-session sigma in ticks
within a factor of 2 of the phase-1 contract. On A0's numbers (Section 6.2) MES (6.61), RTY/M2K (10.01) and YM/MYM
(12.14) pass the sigma part; NQ/MNQ (27.83) does not. A second, different kind of pool is micro plus mini of one index
(MES + ES): identical price process, different queues; it adds information about fill and queue dynamics but almost
none about price direction (correlation near 1, Section 6.4).

Split (contracts A, B in the pool; C unseen; dates illustrative):

    time ->        | train + purged CV (blocks 1..k) | embargo | test block T |
    contract A     |  used                            |   gap   |  scored      |
    contract B     |  used                            |   gap   |  scored      |
    contract C     |  never opened                    |         |  scored once |

C is scored only in the test block T, which is out of time for everything. Testing C on a period used to train A and
B would leak the common index move (the same FOMC minute moves all three), so "unseen contract" must also mean
"unseen time". Sirignano and Cont did the same (unseen stocks tested in June-August 2015, after a January 2014-May
2015 training period). The sealed holdout (2024-03..2025-03) stays sealed; T must sit inside the purchased pre-holdout
window.

### 7.3 Pre-registerable hypotheses for pooling

H-P1 (pooling helps the target contract). On contract A's test block, the pooled model's out-of-sample loss (log-loss
of the fill or markout model, or the realized markout gain of its quote filter) is lower than the phase-1
single-contract model's. Statistic: mean of daily paired differences d_t = loss_single,t - loss_pooled,t, with a
Newey-West or day-block bootstrap t (a Diebold-Mariano-type test). Sample: the detectable standardized daily effect
(mean d / SD d) at t = 3 is 3/sqrt(D): 0.67 for D = 20 test days, 0.47 for 40, 0.39 for 60, 0.34 for 80. A one-month
test block can only detect a large improvement; two months or rolling walk-forward folds are better.

H-P2 (zero-shot transfer). On unseen contract C's test block, the pooled model's quote filter improves the mean 10 s
markout of passive fills over the unfiltered baseline (or over C's unconditional fill and markout rates), with the
same statistic. A weaker, cheaper version: the pooled model's out-of-sample log-loss on C beats C's naive empirical
distribution (the Sirignano 2019 "naive empirical model" benchmark). Sample: as H-S1/H-SC1 per contract (several
thousand fills on C in T), which needs C's own fill simulation and therefore C's mbo or mbp-10 data for T only.

H-P3 (heterogeneity, descriptive, not a pass/fail test): per-contract estimates and the random-effects tau^2 of
Section 6.5, reported so a pooled pass cannot hide a contract where the model fails (Lucchese et al. found exactly
this: in-sample CHTR and AAPL showed no predictability under the universal model).

### 7.4 Trial-count accounting (V43: every configuration counts into N)

| Item | Configurations | Note |
|---|---|---|
| Phase 1 models | per the lead's grid, e.g. 3 model families x 2 feature sets = 6 | counted when screened |
| Phase 2 pooling scheme | full pooling, contract-indicator feature, partial (shared core) = up to 3 | fix one in advance to add 1 |
| Phase 2 normalization | ticks only vs ticks + sigma scaling = 2 | can be fixed from phase 1 at no cost |
| Contract set | each candidate pool (e.g. {MES, MYM} vs {MES, M2K, MYM}) | choosing the pool after seeing results counts every pool tried |
| Unseen contract | each contract tried as C | rotating C (leave-one-contract-out) and reporting the best is a selection; pre-name C |
| Horizons | 1, 10, 60 s markouts | 3 if all tested; 1 if one is pre-named primary |

A disciplined phase 2 (one pool, one scheme, one normalization, one pre-named C, one primary horizon) adds 1 to N for
H-P1 and 1 for H-P2. An undisciplined one (3 schemes x 2 normalizations x 2 pools x 3 choices of C x 3 horizons)
adds 108, which with N already at 538 raises the deflated-Sharpe and Holm bars considerably.

### 7.5 Leakage risks specific to pooling, and the guard for each

1. Common-time leakage across contracts: training on B in a period used to test A (or C). Guard: one calendar split
   for all contracts; folds are sets of trade dates applied to every contract at once (group = trade date).
2. Overlapping labels: 60 s markouts and look-back windows overlap fold boundaries. Guard: purge samples whose label
   window crosses a boundary and embargo at least max(label horizon, feature look-back) after each test fold.
3. Normalization statistics from the future or from the test contract: full-sample sigma, Qbar or z-score means.
   Guard: trailing windows only (DeepLOB uses "the previous 5 days' data"); for C, its normalizers are computed from
   C's own data before each test timestamp, never from the pooled training set's statistics alone.
4. Label thresholds tuned on test data or shared across contracts. Guard: per-contract thresholds from the training
   block only (Lucchese et al.: gamma from D_train); or fixed tick thresholds declared in advance.
5. Hyperparameter or early-stopping choices made on C. Guard: C is never in any validation fold; early stopping uses
   A and B validation folds only.
6. Contract and window selection: picking the pool, C or the test block after looking. Guard: pre-name them; count
   any change into N.
7. Roll handling: quarterly rolls change the front contract; queue and volume features jump at the roll. Guard: the
   program's screening contract already requires one (CLAUDE.md: every candidate goes through
   `screening.screen_candidate` with `roll_blackout` set);
   apply the same blackout to every pooled contract on its own roll calendar.
8. Random within-period validation splits (Sirignano 2019 drew validation "at random" from the training period).
   Guard: never shuffle across time for validation; use day-grouped, purged splits.

### 7.6 Validation the pooled model needs (summary)

- Day-grouped, purged and embargoed walk-forward CV within the training block (scikit-learn's grouped splitters
  exist for this situation: we "would like to know if a model trained on a particular set of groups generalizes well
  to the unseen groups. To measure this, we need to ensure that all the samples in the validation fold come from groups
  that are not represented at all in the paired training fold"; here the groups are trade dates, and the time order
  must also be respected, which LeaveOneGroupOut alone does not do).
- One frozen configuration scored once on the test block T for A and B (out of time) and C (out of time and out of
  contract).
- Paired per-day comparison against the phase-1 single-contract model (H-P1) and the naive benchmark (H-P2), with
  inference clustered by trade date across contracts (Section 6.4).
- The program's existing multiple-testing tools on the counted N (Holm, DSR, PBO/CSCV); with only 2 to 3 contracts,
  leave-one-contract-out gives 2 to 3 numbers, too few for any distributional claim about "universality".

## 8. Compute: the laptop versus a bigger machine or a cloud GPU

Hardware facts. The ThinkPad's GPU is an RTX 3050 Laptop GPU with 4 GB. NVIDIA's comparison page (file
`nvidia_laptop_compare_30.txt`) lists for the "GeForce RTX 3050 Laptop GPU": "NVIDIA CUDA Cores ... 2048 - 2560",
"Boost Clock (MHz) ... 990 - 1740 MHz", "GPU Subsystem Power (W) ... 35 - 80 W", and among the last memory entries "6 GB GDDR6"
and "4 GB GDDR6" (the text extraction does not show which column each belongs to; this machine has 4 GB, per
READER_RULES.md). Peak FP32 throughput is cores x 2
operations per clock x clock: 2048 x 2 x 1.74 GHz = 7.1 TFLOP/s at the top boost, 4.1 at 990 MHz.

Cloud prices fetched 2026-10-21 (on-demand, per GPU-hour, before tax): RunPod (file `runpod_pricing.txt`): "RTX
3090 24 GB VRAM ... $ 0.5 /hr", "RTX 4090 24 GB VRAM ... $ 0.89 /hr", "L4 24 GB VRAM ... $ 0.59 /hr", "RTX A5000 24
GB VRAM ... $ 0.27 /hr", "H100 PCIe 80 GB VRAM ... $ 2.89 /hr" (whether these are the Community or Secure cloud
column could not be told from the text extraction). Lambda (file `lambda_pricing.txt`): "NVIDIA A100 PCIe 40 GB ...
$1.99", "NVIDIA Tesla V100 16 GB ... $0.79", "NVIDIA H100 SXM 80 GB ... $3.99" ("* plus applicable sales tax/VAT/GST").

Estimates (assumptions stated; the timings are guesses until a probe is run):

| Job | Size assumption | Laptop estimate | Cloud estimate |
|---|---|---|---|
| Logistic / LightGBM fill or markout model, one contract | 10^5 to 10^6 fills or events, 50 features | minutes on CPU | not needed |
| 3x50 LSTM (Section 1.8, 58,600 recurrent parameters), one contract | 5 million training sequences of 100 events, 40 inputs | 3 x 2 x 58,600 x 100 = 35 MFLOP per sequence (forward plus backward about 3x forward), 1.76 x 10^14 FLOP per epoch; at an effective 0.5 to 1.4 TFLOP/s (7 to 20% of peak, typical for small recurrent nets) that is 125 to 350 s per epoch, 0.7 to 2 h for 20 epochs | an RTX 4090 at $0.89/h is several times faster [speed ratio not verified]; cost of a few dollars per configuration |
| Same, pooled over 3 contracts | 15 million sequences | 2 to 6 h per configuration; overnight-profile job | about $2 to $5 per configuration at $0.89/h if the 4090 runs it in 2 to 5 h |
| Memory | events stored once, windows built on the fly: 5 million x 40 floats x 4 bytes = 0.8 GB per contract | 2.4 GB for 3 contracts, within the 14 GB rule; VRAM for batch 512 x 100 steps x 50 units x 3 layers is tens of MB | not a constraint |
| Sirignano (2019) scale (489 per-stock models) | the paper's "over 3,000 'GPU node hours'" | not feasible and not needed | 3,000 h x $0.89 = $2,670 as a crude upper bound on modern single GPUs (a modern GPU is much faster than a 2016 node, so the real figure would be lower) |

Verdict on compute: phases 1 and 2 at the scale this program can buy (1 to 3 contracts, months not years) fit on the
laptop under the overnight profile, one GPU job at a time. A cloud GPU is a convenience for a hyperparameter grid,
not a requirement, and every grid point it makes cheaper still counts into N. The Sirignano-Cont universal model
(about 1000 stocks, 25 GPU nodes for one model, about 500 nodes for the per-stock models) is out of scope at any
price that makes sense here, and also out of scope in data.

## 9. Verdicts per method (for this program)

| Method | Verdict | Reason |
|---|---|---|
| Sirignano and Cont universal LSTM (full scale) | skip | Needs hundreds of instruments and years of message data; target is next-mid direction, not a fill or markout; no cost-inclusive evidence; the one transferable lesson (pool where data are thin, test on unseen instrument and unseen time) is kept in Section 7. |
| Sirignano-Cont-style small LSTM as a direction filter on one contract (H-SC1) | maybe | Cheap on the laptop; only useful as an adverse-selection filter; must beat a tree baseline; up to 4 configurations. |
| Sirignano (2019) hazard ("spatial") output layer for markout distributions (H-S1) | maybe | A good way to model the full markout distribution in ticks with few parameters; but it is a per-contract model and the tail needs many fills. |
| Lucchese et al. volume representation and per-contract thresholds | use (as feature and label conventions) | Tick-indexed volumes and per-contract label thresholds are what pooling requires; no extra trials if fixed in advance. |
| Lucchese et al. model confidence set | maybe | Sound for comparing a small model set against no-skill; overlaps the program's Holm/DSR tools; few windows in 4 months. |
| Depth-scaled OFI (Cont, Cucuringu and Zhang) | use | Unit-free across contracts by construction; also gives lagged cross-contract features (ES/NQ flow for MES) without pooling. |
| DeepLOB-style zero-shot transfer test | use (as a validation design) | A leave-one-contract-out, out-of-time test is cheap once a pooled model exists; pre-name the contract. |
| Full pooling of 2 to 3 contracts (phase 2) | maybe | Only after phase 1 passes; only contracts that match on tick regime and sigma-in-ticks; effective sample gain is limited by co-movement (Section 6.4); adds to N. |
| Partial pooling (contract indicator, shared core as in QuantNet, or random-effects shrinkage) | maybe (preferred over full pooling if phase 2 runs) | Lets each contract keep its own level while borrowing strength; shrinkage is transparent and cheap. |
| Pooling across very different contracts (e.g. MES with MNQ, or with non-equity roots) | skip | Sigma in ticks differs by 4.2x (MES vs NQ); Lucchese et al. found universal models inconsistent even within one exchange; LOBCAST warns about fixed thresholds across instruments. |
| Cloud GPU | skip for phases 1-2 | Not needed at this scale; revisit only for a grid the lead has already counted. |

## 10. References (all full texts saved under reports/stage_e28_briefs/pages/C2_Pooled/ unless marked)

1. Sirignano, J. and Cont, R. (2019). Universal features of price formation in financial markets: perspectives from
   deep learning. Quantitative Finance 19(9), 1449-1459. doi 10.1080/14697688.2019.1622295. arXiv 1803.06917.
   `sirignano_cont2019_universal.pdf`.
2. Sirignano, J. A. (2019). Deep learning for limit order books. Quantitative Finance 19(4), 549-570.
   doi 10.1080/14697688.2018.1546053. arXiv 1601.01987. `sirignano2019_dl_lob.pdf`.
3. Lucchese, L., Pakkanen, M. S. and Veraart, A. E. D. (2024). The short-term predictability of returns in order book
   markets: A deep learning perspective. International Journal of Forecasting 40(4), 1587-1621.
   doi 10.1016/j.ijforecast.2024.02.001. arXiv 2211.13777. `lucchese2024_predictability.pdf`.
4. Zhang, Z., Zohren, S. and Roberts, S. (2019). DeepLOB: Deep convolutional neural networks for limit order books.
   IEEE Transactions on Signal Processing 67(11) [volume from general knowledge, not from a fetched page].
   arXiv 1808.03668. `zhang2019_deeplob.pdf`.
5. Prata, M. et al. (2024). LOB-based deep learning models for stock price trend prediction: a benchmark study.
   Artificial Intelligence Review 57(5). doi 10.1007/s10462-024-10715-4. arXiv 2308.01915. `prata2024_lobcast.pdf`.
6. Briola, A., Bartolucci, S. and Aste, T. (2025). Deep limit order book forecasting: a microstructural guide.
   Quantitative Finance 25(7), 1101-1131. doi 10.1080/14697688.2025.2522911. arXiv 2403.09267.
   `briola2024_microstructural_guide.pdf`.
7. Cont, R., Cucuringu, M. and Zhang, C. (2023). Cross-impact of order flow imbalance in equity markets. Quantitative
   Finance 23(10), 1373-1393. doi 10.1080/14697688.2023.2236159. arXiv 2112.13213.
   `cont_cucuringu_zhang_crossimpact.pdf`.
8. Wu, Y., Mahfouz, M., Magazzeni, D. and Veloso, M. (2021). Towards robust representation of limit orders books for
   deep learning models. arXiv 2110.05479. `wu2021_robust_representation.pdf`.
9. Koshiyama, A., Blumberg, S. B., Firoozye, N., Treleaven, P. and Flennerhag, S. (2020). QuantNet: transferring
   learning across trading strategies. arXiv 2004.03445. `koshiyama2020_quantnet.pdf`.
10. Bieganowski, B. and Slepaczuk, R. (2026). Explainable patterns in cryptocurrency microstructure. arXiv
    2602.00776. `crypto_explainable_patterns2026.pdf`.
11. Xiao, Y., Ventre, C., Wang, Y., Li, H., Huan, Y. and Liu, B. (2025). LiT: limit order book transformer. Frontiers
    in Artificial Intelligence. doi 10.3389/frai.2025.1616485. `frontiers_frai2025_1616485.pdf`,
    `lit_lob_transformer_pmc.html`.
12. Kolm, P. N., Turiel, J. and Westray, N. (2023). Deep order flow imbalance: Extracting alpha at multiple horizons
    from the limit order book. Mathematical Finance 33(4), 1044-1081. doi 10.1111/mafi.12413. [full text NOT
    fetched: SSRN 403, Wiley Cloudflare challenge; details from search snippets only, unverified].
13. KANFormer for predicting fill probabilities via survival analysis in limit order books (2025). arXiv 2512.05734.
    [full text saved by the C2_LOB reader: pages/C2_LOB/dl_meets_qr_2025.txt]. Multidimensional Deep Queue-Reactive model (2025), arXiv 2501.08822
    [abstract only, unverified].
14. Hochreiter, S. and Schmidhuber, J. (1997). Long short-term memory. Neural Computation 9(8) [textbook equations;
    not fetched].
15. Hansen, P. R., Lunde, A. and Nason, J. M. (2011). The model confidence set. Econometrica 79(2) [cited via
    Lucchese et al.; not fetched].
16. DerSimonian, R. and Laird, N. (1986). Meta-analysis in clinical trials. Controlled Clinical Trials 7(3) [standard
    random-effects estimator used in Section 6.5; not fetched].
17. scikit-learn developers. Cross-validation user guide (fetched 2026-10-21). `sklearn_cross_validation.html`.
18. NVIDIA. Compare gaming laptops: GeForce RTX 30 Series (fetched 2026-10-21). `nvidia_laptop_compare_30.html`.
19. RunPod. Pricing (fetched 2026-10-21). `runpod_pricing.html`. Lambda. Pricing (fetched 2026-10-21).
    `lambda_pricing.html`.
20. Repo sources: rules/products.py lines 147-154 (tick sizes, tick values, multipliers, round-turn commission in
    cents); reports/stage_e28_briefs/A0_contract_stats.json (sigma_1m_ticks, vol_per_min_main_median; window
    2022-11-01..2023-10-31).

## 11. Evidence table

| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| Universal model data scope | Sirignano and Cont 2019 | "all orders, transactions and order cancellations for approximately 1000 stocks traded on the NASDAQ between January 1, 2014 and March 31, 2017" | sirignano_cont2019_universal.txt |
| Pooled without normalization | Sirignano and Cont 2019 | "Data from various stocks were pooled together for this purposes without any specific normalization." | sirignano_cont2019_universal.txt |
| Normalizations did not help | Sirignano and Cont 2019 | "standard data transformations such as normalizations based on average volume, volatility or average spread, or partitioning the training data into sectors or categories such as large/small tick stocks do not improve training results" | sirignano_cont2019_universal.txt |
| Universal beats stock-specific most where data are thin | Sirignano and Cont 2019 | "The universal model most strongly outperforms the stock-specific models on stocks with less data." | sirignano_cont2019_universal.txt |
| Pooled data equivalent to many years | Sirignano and Cont 2019 | "Using 1 year of the pooled data set is roughly equivalent to using 500 years (!) of data for training a single-stock model" | sirignano_cont2019_universal.txt |
| Unseen-stock result | Sirignano and Cont 2019 | "This universal model outperforms stock-specific models for stocks 465 − 489, even though the universal model has never seen data from these stocks in the training set." | sirignano_cont2019_universal.txt |
| Longer training window better | Sirignano and Cont 2019 | "Model accuracy consistently increases as the length of the training set is increased." | sirignano_cont2019_universal.txt |
| Compute scale | Sirignano and Cont 2019 | "we distributed the training of the universal model across 25 GPU nodes using asynchronous stochastic gradient descent" | sirignano_cont2019_universal.txt |
| 1% is significant at their scale | Sirignano and Cont 2019 | "Given the large size of the data set, even a small deviation (i.e. 1%) from this 50% benchmark is statistically significant." | sirignano_cont2019_universal.txt |
| Sirignano 2019 is per-stock | Sirignano 2019 | "Models are trained and tested separately on each stock; i.e., a new randomly initialized model is trained for each stock." | sirignano2019_dl_lob.txt |
| Random validation split | Sirignano 2019 | "The training data is composed of 95% of the data from January 1, 2014 to May 31, 2015 (drawn at random)." | sirignano2019_dl_lob.txt |
| Spatial vs standard network | Sirignano 2019 | "The spatial neural network outperforms the standard neural network on 94% of stocks in Case [1] and 97% of stocks in Case [2]." | sirignano2019_dl_lob.txt |
| Compute | Sirignano 2019 | "In total, model training takes over 3,000 “GPU node hours”" | sirignano2019_dl_lob.txt |
| Universal models inconsistent | Lucchese et al. 2024 | "using universal models leads to results that are partially inconsistent with those in Table 4" | lucchese2024_predictability.txt |
| Universal models fail on idiosyncratic stocks | Lucchese et al. 2024 | "When, instead, the ticker is mainly subject to stock-specific trading patterns, universal models have a hard time detecting predictability" | lucchese2024_predictability.txt |
| Transfer to unseen stocks | Lucchese et al. 2024 | "It is rather remarkable that universal models can identify predictability for “out-of-sample” stocks." | lucchese2024_predictability.txt |
| Per-ticker thresholds | Lucchese et al. 2024 | "the choice of γ is specific to the choice of window, horizon, and ticker" | lucchese2024_predictability.txt |
| Horizon | Lucchese et al. 2024 | "we were able to identify predictability up to 50 order book events ahead at the 99% confidence level" | lucchese2024_predictability.txt |
| Not tradable as is | Lucchese et al. 2024 | "we focus on mid-to-mid returns, which are not tradable in practice" | lucchese2024_predictability.txt |
| Other market structures untested | Lucchese et al. 2024 | "only Nasdaq-traded stocks were considered in this paper" | lucchese2024_predictability.txt |
| DeepLOB transfer design | Zhang et al. 2019 | "we directly apply our model to five more stocks that were not part of the training data set (transfer learning)" | zhang2019_deeplob.txt |
| DeepLOB rolling normalization | Zhang et al. 2019 | "use the mean and standard deviation of the previous 5 days’ data" | zhang2019_deeplob.txt |
| DeepLOB no costs | Zhang et al. 2019 | "we use mid-prices without transaction costs" | zhang2019_deeplob.txt |
| Generalization drop | Prata et al. 2024 | "all models exhibit a significant performance drop when exposed to new data" | prata2024_lobcast.txt |
| Hyperparameter fragility | Prata et al. 2024 | "they diverged (F1-score ⩽ 33%) during the hyperparameters search for about half of the runs" | prata2024_lobcast.txt |
| Fixed threshold across stocks distorts labels | Prata et al. 2024 | "With such a labelling system, fixed θ, stocks with low returns become associated with stable trends, as their behaviour is overshadowed by stocks exhibiting higher returns." | prata2024_lobcast.txt |
| Consumer GPUs used | Prata et al. 2024 | "a cluster comprised of 8 GPUs (1 NVIDIA GeForce RTX 2060, 2 NVIDIA GeForce RTX 3070, and 5 NVIDIA Quadro RTX 6000)" | prata2024_lobcast.txt |
| Tick-regime rule | Briola et al. | "if (i) ⟨σ⟩ ≳ 3θ, we are dealing with a small-tick stock; if (ii) ⟨σ⟩ ≲ 1.5θ, we are dealing with a large-tick stock" | briola2024_microstructural_guide.txt |
| Forecasts not actionable | Briola et al. | "their high forecasting power does not necessarily correspond to actionable trading signals" | briola2024_microstructural_guide.txt |
| Depth scaling of OFI | Cont, Cucuringu and Zhang 2023 | "Due to the intraday pattern in limit order depth, we use the average size to scale OFIs" | cont_cucuringu_zhang_crossimpact.txt |
| Lagged cross-asset OFI helps forecasting | Cont, Cucuringu and Zhang 2023 | "we show that lagged cross-asset OFIs do improve the forecasting of future returns" | cont_cucuringu_zhang_crossimpact.txt |
| Their PnL ignores costs | Cont, Cucuringu and Zhang 2023 | "the strategy ignores trading costs, as this is not the focus of our paper" | cont_cucuringu_zhang_crossimpact.txt |
| Level representation fragile | Wu et al. 2021 | "a small perturbation would leads to shift of price levels and thus the representation would be affected" | wu2021_robust_representation.txt |
| Partial pooling architecture | Koshiyama et al. 2020 | "market-specific parameters are free to specialize on the problem at hand, whilst market-agnostic parameters are driven to capture signals from all markets" | koshiyama2020_quantnet.txt |
| Crypto cross-asset feature stability | Bieganowski and Slepaczuk 2026 | "the same engineered order book and trade features exhibit remarkably similar predictive importance and SHAP dependence shapes across assets" | crypto_explainable_patterns2026.txt |
| Crypto latency caveat | Bieganowski and Slepaczuk 2026 | "Latency is not explicitly modeled; results should be interpreted as an upper bound in the fastest regime." | crypto_explainable_patterns2026.txt |
| Temporal decay (crypto) | Xiao et al. 2025 | "we observe a significant decline of around 5% in most metrics in November and December, falling even below the from-scratch baselines" | lit_lob_transformer_pmc.txt |
| Group CV purpose | scikit-learn docs | "we need to ensure that all the samples in the validation fold come from groups that are not represented at all in the paired training fold" | sklearn_cross_validation.txt |
| Laptop GPU spec | NVIDIA | "G eForce RTX 3050 Laptop GPU ... NVIDIA CUDA ® Cores ... 2048 - 2560 ... Boost Clock (MHz) ... 990 - 1740 MHz" (columns flattened by extraction) | nvidia_laptop_compare_30.txt |
| Cloud GPU price | RunPod | "RTX 4090 24 GB VRAM 41 GB RAM 6 vCPUs $ 0.89 /hr" | runpod_pricing.txt |
| Cloud GPU price | Lambda | "NVIDIA A100 PCIe 40 GB 120 900 GiB 1 TiB SSD $1.99" | lambda_pricing.txt |

## 12. Run notes

- WebSearch calls used: 5 of 60 (no budget notice seen). Discovery otherwise via the arXiv API and Crossref.
- Failures: Kolm et al. 2023 full text (SSRN 403; Wiley Cloudflare challenge); TechPowerUp spec page (bot check).
  Both logged in log.tsv; the claims that depended on them are marked [unverified] or sourced elsewhere.
- Not done: no measurement of spreads, queue sizes or cross-contract correlations (would need mbp/mbo data, outside
  this brief); the illustrative numbers in Sections 2.6, 3.5, 6.3 and 6.5 are labelled as assumptions. No timing probe
  of an LSTM on the RTX 3050 was run; the Section 8 timings are estimates from FLOP counts.
- Quote check: work/C2_Pooled/C2_Pooled_checkquotes.py matched every evidence-table quote in its saved file except 4
  split by PDF layout (hyphenation, two columns, a page number); those 4 were confirmed by hand at
  sirignano_cont2019_universal.txt:185-190, zhang2019_deeplob.txt:540-541 and 602-603, prata2024_lobcast.txt:28-29.
- Finished 2026-10-21 (PDT; see file mtime).

## Corrections after review (Stage E.28, MathReviewer G3)

- MG3-13: sec. 0 bottom line narrowed to equity LOB studies; the crypto taker backtest nets taker fees but models no latency.
- MG3-14: sec. 5.4 notes that the table does not say whether the 4.06 to 7.00 returns are gross or net of taker fee.
- MG3-15: sec. 2.3 quote corrected to "probability mass escaping to +∞".
- MG3-16: sec. 4.3 heading now "2024 arXiv; QF 2025".
- MG3-19: sec. 1.2 quote corrected to the verbatim "step Δk = τk+1 − τk is on average 1.7 seconds in the dataset".
