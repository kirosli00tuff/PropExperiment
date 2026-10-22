# C2. Machine learning on order-book data, part 1: the deep models

Stage E.28 methods brief, deep-dive section C2. Worker: C2_DeepLOB (Opus 5.5). Written 2026-10-21 (PDT).
Pages: `reports/stage_e28_briefs/pages/C2_DeepLOB/` (log: `log.tsv`). Scripts and probe output:
`reports/stage_e28_briefs/work/C2_DeepLOB/`.

## 0. Scope, sources and how to read this section

**What this covers.** DeepLOB (Zhang, Zohren and Roberts 2019), the FI-2010 benchmark, later CNN, RNN and
transformer models (TransLOB, DeepLOB-Seq2Seq and DeepLOB-Attention, HLOB, TLOB/MLPLOB, BiN-CTABL in passing,
deep models on market-by-order data), the benchmark and reproducibility studies (LOBCAST; Briola, Turiel and
Aste 2020; Briola, Bartolucci and Aste 2024 "microstructural guide"; Lucchese, Pakkanen and Veraart 2024), the
futures results that exist (CME Eurodollar, CME E-mini S&P 500, Eurex Bund), label design against costs,
post-publication decay, the gap between accuracy and net profit, retail latency, and training compute on this
laptop versus a cloud GPU.

**Sources.** 20 papers fetched as full-text PDFs (arXiv), two cloud price pages and three Databento
documentation pages, all saved raw with sha256 in `log.tsv`. Quotes below are copied from the pdftotext output
(`*.raw.txt` next to each PDF); line breaks inside a quote are joined and hyphenation left as printed. One source
could not be fetched (Kolm, Turiel and Westray 2023, a paywall); everything taken from it is marked
[unverified]. Seven WebSearch calls of the 60 budget were used.

**Measured, not guessed, compute numbers.** Section 10 reports a probe I ran on this laptop's RTX 3050 with
synthetic random tensors (no market data): parameter counts, peak GPU memory, training throughput and
single-sample inference latency for DeepLOB (paper version and the common PyTorch version) and a TransLOB-like
model. Script: `work/C2_DeepLOB/C2_gpu_probe.py`; output: `work/C2_DeepLOB/C2_gpu_probe.out` (run 02:29:58 to
02:30:21 PDT, nice 10, 4 CPU threads, 14 MiB GPU memory in use before launch).

**The cost yardstick used throughout (MES, one contract).** One MES tick is 0.25 index points, worth $1.25.
The program's cost model (`sim/costs.py`, repo-internal, flagged there for reconfirmation) uses a $1.22
round-turn commission and fees on TopstepX, which is 1.22 / 1.25 = **0.976 ticks per round trip**. At an index
level of 4,700 one tick is 0.25 / 4,700 = 0.532 basis points (bp); at 5,000 it is 0.500 bp. So any label
threshold, forecast or markout below about 1 tick per round trip cannot pay fees even before the spread and
adverse selection. A round trip that crosses the spread on both legs (when the spread is 1 tick) pays a further
1 tick relative to the mid-price, so about 1.98 ticks in total. One passive and one aggressive leg is,
relative to mid, the fee only (0.976 ticks) plus whatever adverse selection the passive fill suffers; that
adverse selection is exactly what the Part B pilot's markouts measure.

**Notation used in every section.** p_a^(i)(t), v_a^(i)(t): price and size at ask level i at event t;
p_b^(i)(t), v_b^(i)(t): the same on the bid; level 1 is the best quote. Mid-price p_t = (p_a^(1)(t) +
p_b^(1)(t)) / 2. k: horizon, counted in book events unless stated. A "label" is the class the model is trained
to predict: up (+1), stationary (0), down (-1).

## 1. DeepLOB (Zhang, Zohren and Roberts 2019)

Source: Zhang, Z., Zohren, S. and Roberts, S. (2019), "DeepLOB: Deep Convolutional Neural Networks for Limit
Order Books", IEEE Transactions on Signal Processing 67(11); arXiv 1808.03668v6. File `deeplob_zhang2019.pdf`.

### 1.1 Core idea in plain words

Take the last 100 snapshots of the top 10 levels of the book (price and size on each side, 40 numbers per
snapshot), treat that 100 x 40 array like a one-channel image, and let a neural network learn its own
"features" instead of hand-built ones such as order-flow imbalance. Convolution layers first merge price and
size at each level, then merge bid and ask (which gives something like a micro-price at every level), then
merge all 10 levels. An "Inception" block looks at several time-window lengths at once. A small recurrent layer
(LSTM, 64 units) then reads the 100 time steps in order and outputs three probabilities: the mid-price goes up,
stays, or goes down over the next k events.

Verbatim (abstract): "The architecture utilises convolutional filters to capture the spatial structure of the
limit order books as well as LSTM modules to capture longer time dependencies." And on the first layer: "The
first layer essentially summarises information between price and volume {p(i) , v (i) } at each order book
level."

### 1.2 Equations, every term explained

**Input.** One sample is X = [x_1, ..., x_100]^T in R^(100 x 40), with x_t = [p_a^(i)(t), v_a^(i)(t),
p_b^(i)(t), v_b^(i)(t)] for i = 1..10 (paper, Section IV.B). Time runs over book events, not seconds: in the
LSE data "∆k,k+1 is on average 0.192 seconds", so 100 events cover about 19 s on average.

**Normalisation.** Each feature is z-scored with "the mean and standard deviation of the previous 5 days’ data
to normalise the current day’s data (with a separate normalisation [two-column text interleaved here in the PDF extraction] for each instrument)". In symbols, for
feature j on day d: z_j(t) = (x_j(t) - mu_j(d-5..d-1)) / sigma_j(d-5..d-1). Using only past days avoids a
look-ahead in the scaling.

**Mid-price** (paper eq. 1): p_t = (p_a(t) + p_b(t)) / 2, where p_a(t), p_b(t) are the best ask and best bid.

**Smoothed label** (paper eqs. 2 to 4). With k the horizon in events:

- m_-(t) = mean of the past mid-prices p_t, p_(t-1), ..., p_(t-k) (paper eq. 2 prints (1/k) times a sum over
  i = 0..k, which has k + 1 terms; TLOB (Berti and Kasneci 2025, their eq. 6) writes the same quantity with the
  consistent 1/(k + 1). I use 1/(k + 1).)
- m_+(t) = (1/k) times the sum over i = 1..k of p_(t+i), the mean of the next k mid-prices.
- Eq. 3 (used by FI-2010): l_t = (m_+(t) - p_t) / p_t, smoothing the future only.
- Eq. 4 (used by DeepLOB on its LSE data): l_t = (m_+(t) - m_-(t)) / m_-(t), smoothing past and future.
- Class: up (+1) if l_t > alpha, down (-1) if l_t < -alpha, stationary (0) otherwise; alpha is a threshold on
  the percentage change.

Verbatim: "If lt > α or lt < −α, we define it as up (+1) or down (−1). For anything else, we consider it as
stationary (0)." On why eq. 4: the eq. 3 labels "are less consistent ... This is essentially detrimental for
designing trading algorithms as signals are not consistent here leading to many redundant trading actions thus
incurring larger transaction costs."

Assumption hidden in eq. 4: the label at t uses m_-(t), a backward average that includes p_t and the k
previous mids. The label is therefore "is the average of the next k mids above the average of the last k + 1
mids", not "will the price I can trade at rise". A trade entered at t is priced against p_t (or the touch), not
against m_-(t), so the label can be "up" even when the next k mids are all below the current mid (if the past
k were lower still). Section 6 returns to this.

**Micro-price, the intuition for the second conv layer.** The paper motivates the bid/ask merge with the
micro-price p_micro = I p_a^(1) + (1 - I) p_b^(1), with I = v_b^(1) / (v_a^(1) + v_b^(1)) (the extracted PDF
text of this equation is garbled; this is the standard form the paper describes): "The weight I is called the
imbalance. The micro-price is an important indicator as it considers volumes on bid and ask side". A
convolution with learned weights generalises this fixed weighting to all 10 levels.

**Layers.** Conv(1x2, 16 filters, stride 1x2) then two Conv(4x1, 16); Conv(1x2, 16, stride 1x2) then two
Conv(4x1, 16); Conv(1x10, 16) then two Conv(4x1, 16); Inception module with three branches (1x1 then 3x1, 1x1
then 5x1, 3x1 max-pool then 1x1, 32 filters each, concatenated to 96 channels); LSTM with 64 units; dense
softmax over 3 classes. Activation Leaky-ReLU with slope 0.01. Each convolution output is
y = LeakyReLU(W * x + b), W the learned kernel, * the discrete convolution, b a bias.

**Loss and training.** Categorical cross-entropy L = -(1/N) sum_n sum_c y_(n,c) log q_(n,c), where y_(n,c) is
1 if sample n has class c and q_(n,c) is the softmax output. Adam with learning rate 0.01 and epsilon 1, batch
32, early stopping when validation accuracy does not improve for 20 epochs ("about 100 epochs for the FI-2010
dataset and 40 epochs for the LSE dataset"), Keras/TensorFlow on one Tesla P100.

**Parameter count, derived.** For a convolution with kernel h x w, c_in inputs and c_out filters the count is
(h w c_in + 1) c_out; an LSTM with input size d and H units has 4 (H (d + H) + H) parameters in Keras. Block 1:
(2*1+1)*16 + 2*(4*16+1)*16 = 48 + 2080 = 2,128. Block 2: (2*16+1)*16 + 2080 = 2,608. Block 3: (10*16+1)*16 +
2080 = 4,656. Inception: 2*(16+1)*32 + (3*32+1)*32 + (5*32+1)*32 + (16+1)*32 = 9,888. LSTM: 4*(64*(96+64)+64)
= 41,216. Dense: 64*3+3 = 195. Total 60,691, matching the paper's "about 60,000 parameters". My PyTorch build
counts 60,947 because PyTorch's LSTM carries a second bias vector (+256). The LSTM is 68% of the model.

### 1.3 Data it needs; is one CME contract for 4 to 12 months enough?

DeepLOB needs exactly what Databento's mbp-10 schema provides: the top 10 price levels with sizes, updated at
every book event. Databento: "MBP-10 (market by price) provides every order book event across the top ten price
levels, keyed by price. This includes every trade and changes to aggregate market depth, alongside total size
and order count at the top ten price levels." (`databento_schema_mbp-10.html`). tbbo does not suffice:
"BBO on trade (TBBO) provides every trade event alongside the BBO immediately before the effect of each trade"
(top of book only, sampled only at trades). mbo is a superset (mbp-10 can be built from it).

Scale of the original: the LSE set "is made up of 12 months, and has more than 134 million samples. On average,
there are 150,000 events per day per stock" over five stocks, with "the first 6 months as training data, the
next 3 months as validation data and the last 3 months as test data". One MES contract for 4 months is roughly
80 trading days, so about 1/15 of the stock-days DeepLOB used, and from a single instrument. Smaller studies
did train on less: LOBCAST used 6 training days per stock, HLOB 40 training days per stock-year, the Bund-futures
benchmark one month (Section 5). So 4 months is enough to fit the model (it has only 60k parameters and millions
of event samples), but not enough to show the result is stable across regimes: the test window would be one
or two months of one contract. 12 months allows a 6/3/3 split like the paper's. The binding constraint is
independence, not sample count: successive samples share 99 of 100 input rows and overlapping label windows, so
the effective sample size is closer to the number of non-overlapping horizons than to the number of events.

### 1.4 What it estimates or decides

It estimates the three class probabilities P(up), P(stationary), P(down) for the smoothed mid-price change over
the next k events. It does not estimate the size of the move, the fill probability of a passive order, or
any cost. The paper's trading rule turns the argmax class into a position (Section 1.6).

### 1.5 Worked example: the label on toy MES mids

Toy numbers (not data). k = 5. Past mids p_(t-5)..p_t = 4700.000, 4700.125, 4700.125, 4700.250, 4700.250,
4700.375 (mids move in half-tick steps of 0.125). Next mids p_(t+1)..p_(t+5) = 4700.375, 4700.500, 4700.625,
4700.625, 4700.750.

- m_-(t) = 28201.125 / 6 = 4700.1875. m_+(t) = 23502.875 / 5 = 4700.575.
- Eq. 3: l_t = (4700.575 - 4700.375) / 4700.375 = 4.255e-5 = 0.43 bp.
- Eq. 4: l_t = (4700.575 - 4700.1875) / 4700.1875 = 8.244e-5 = 0.82 bp. (This uses the 1/(k+1) definition adopted
  in Section 1.2. The script's second line uses i = 0..k-1 (five mids) and prints 0.745 bp; its "m- printed"
  line, 5640.225, is the paper's literal 1/k over k+1 terms and is not a price. The class labels are the same
  under both.)
- With alpha = 0.25e-4 (0.25 bp, LLOY's k = 20 value in Zhang and Zohren 2021, Table 11) both give "up". With
  alpha = 1e-4 (1 bp) both give "stationary". With FI-2010's 0.002 (20 bp) both give "stationary".
- In ticks: the mean of the next five mids is 0.2 points = 0.8 ticks above the current mid. Even a perfect
  "up" call here is worth at most 0.8 ticks gross mid-to-mid, below the 0.976-tick round-trip fee alone.

Script: `work/C2_DeepLOB/C2_worked_examples.py` (output `C2_worked_examples.out`).

### 1.6 Published results, and what the trading test assumed

FI-2010, "Setup 2" (7 training days, 3 test days): accuracy 84.47% and F1 83.40% at k = 10; F1 72.82% and
80.35% at k = 20 and 50 (`deeplob_zhang2019.txt`, Table II). LSE, five stocks, 3-month test: accuracy
70.17%, 63.93%, 61.52% at k = 20, 50, 100 (F1 70.15, 63.49, 60.65). Transfer to five stocks not used in
training (GLEN, HSBC, CNA, BP, ITV): accuracy 68.62, 63.44, 61.46. These are three-class numbers with roughly
balanced classes, so chance is about 33%.

The trading simulation used no costs and mid-price fills, by design: "we assume trading takes place at
mid-price2 and compare gross profits before fees". Rule: on a +1 signal buy one share at t + 5, hold until -1
appears; flat overnight. The authors argue mid-mid is equivalent to "enter the trade passively, while we exit
it aggressively, crossing the spread", and that "careful timing of the entry points as well as more elaborate
trading rules ... should be able to account for additional profits to cover the transaction costs". That
argument assumes the passive entry is filled at the touch with no adverse selection, which is the very thing a
passive-fill markout measures.

### 1.7 Turning the pilot into a pre-registerable hypothesis

The pilot measures, for a 1-lot passive order on one contract: fill rate, time in queue, and markouts at 1, 10
and 60 s (markout = signed mid-price change after the fill, in ticks, positive when the fill was good).

**H-C2-DeepLOB-1 (adverse-selection filter).** "A DeepLOB-type classifier trained on mbp-10 snapshots before
each simulated passive order's placement time separates filled orders into groups with different mean 10 s
markout." Procedure: train on the first ~60% of days (time-ordered), validate on the next ~20%, test once on
the last ~20%, with a purge of one label horizon plus an embargo between blocks. At test time, for every
pilot-style passive fill, record the model's P(price moves against the resting side) at placement. Test
statistic: difference in mean 10 s markout (ticks) between the lowest and highest terciles of that probability,
with a day-clustered or Newey-West standard error; pass if t > 3.0 (the program's bar) and the low-risk tercile's
mean markout exceeds the 0.976-tick fee. Sample: with markout standard deviation sigma and a target difference
delta, n per group ~ 2 (z_alpha + z_beta)^2 sigma^2 / delta^2 with z_alpha = 3.0, z_beta = 0.84: sigma = 2
ticks, delta = 0.5 tick needs 473 fills per tercile (1,419 total); delta = 0.25 tick needs 1,890 per tercile;
multiply by a design effect of about 3 for clustering within days (assumption, to be replaced by the pilot's
measured intra-day correlation). The pilot's own markout sigma at 10 s is the number that sets this.
Trial count: one architecture, one label (the 10 s markout sign of a hypothetical passive fill), one horizon =
+1 to N if pre-registered as the single primary; the 1 s and 60 s variants add +2 if tested. Any search over
alpha, k, look-back length, learning rate or seeds that picks a winner adds each tried configuration to N.

### 1.8 Compute

60,947 parameters (PyTorch). On the RTX 3050: 4,602 samples/s at batch 32 (94 MiB peak GPU memory) and 5,247
samples/s at batch 256 (577 MiB); 844 samples/s on 4 CPU threads; single-sample inference 0.87 ms median on GPU
and 1.24 ms on CPU (Section 10). It fits the 4 GB card with a wide margin.

### 1.9 Evidence at retail scale and latency

- The original trading test is gross of costs and fills at mid (quoted above); it is not evidence of net
  profit.
- Independent reproduction: LOBCAST measured DeepLOB at F1 71.4 ± 5.3 on FI-2010 against a claimed 78.9 ± 4.4,
  and 59.5 on its 2021 and 2022 NASDAQ sets (Section 4.1).
- In the Bund futures benchmark DeepLOB reached balanced accuracy 0.54 (Section 5.3).
- No study found tests DeepLOB's signal with a tens-of-milliseconds order delay, real fees and passive-fill
  adverse selection on a futures contract (searched; null).

## 2. The FI-2010 benchmark and its problems

Source: Ntakaris, A., Magris, M., Kanniainen, J., Gabbouj, M. and Iosifidis, A. (2018), "Benchmark dataset for
mid-price forecasting of limit order book data with machine learning methods", Journal of Forecasting 37(8);
arXiv 1705.03233. File `fi2010_ntakaris2018.pdf`.

### 2.1 What it is, in plain words

The first public limit-order-book dataset: five Finnish stocks (Kesko, Outokumpu, Sampo, Rautaruukki,
Wärtsilä) on NASDAQ Nordic Helsinki for ten trading days, 1 to 14 June 2010, already normalised and labelled.
Verbatim: "five stocks from the NASDAQ Nordic stock market for a time period of ten consecutive days, leading
to a dataset of ≈4,000,000 time series samples in total". Each row summarises a block of 10 events: "each of
our representations is a vector that contains information for 10 consecutive events ... (i.e. 394,337
representations)", described by a 144-dimensional feature vector (the first 40 are the raw 10-level book).

### 2.2 The label equation

FI-2010 eq. 8 (as printed in the paper): l_i^(j) = ((1/k) sum_(j=i+1..i+k) m_j - m_i) / m_i, where m_i is the
current mid-price and the m_j are the next k mid-prices, k in {1, 2, 3, 5, 10} representation steps (each is 10
events, so 10 to 100 events). Threshold 0.002: "For percentage changes equal to or greater than 0.002, we use
label 1. For percentage change that varies from -0.00199 to 0.00199, we use label 2, and, for percentage change
smaller or equal to -0.002, we use label 3." This is DeepLOB's eq. 3 with alpha = 0.002.

Worked conversion: 0.002 = 20 bp. On MES at 4,700 that is 0.002 x 4,700 = 9.4 points = 37.6 ticks; at 5,000 it
is 40 ticks. A 20 bp move in 10 to 100 events is rare on a liquid index future, so the same threshold on MES
would label almost everything "stationary". The threshold is not a cost-aware choice; LOBCAST: "θ was chosen to
obtain a balanced dataset in the number of classes for the horizon k = 5 ... Thus, θ is not chosen in accordance
with its financial implication but rather serves the purpose of balancing the dataset."

### 2.3 Its problems (each sourced)

1. **Prices cannot be recovered, so no cost-inclusive backtest is possible on it.** "In compliance with NASDAQ
   OMX agreements, the normalized feature dataset is made available ... normalized in order to prevent
   reconstruction of the original NASDAQ data." LOBCAST: "This dataset has the intrinsic limitation of being
   already pre-processed (filtered, normalized, and labelled) so that the original LOB cannot be backtracked,
   thus hampering thorough experimentation." Consequence: a 2026 student-journal paper (Makinde, Bristol BILT
   Student Research Journal, arXiv 2601.02310, file `tkan_alphadecay2026.pdf`) reports "a 132.48% return
   compared to the -82.76% DeepLOB drawdown under 1.0 bps transaction costs" on FI-2010; given (1), returns in
   basis points on normalised FI-2010 prices are not interpretable as money, and I treat that result as not
   evidence either way.
2. **Tiny and old.** Ten days, five illiquid-by-today's-standard stocks, 2010. DeepLOB: "10 days is an
   insufficient amount [two-column text interleaved in the PDF extraction] of data to fully test the robustness and generalisation ability of an algorithm" and "the
   FI-2010 dataset was collected in 2010 and the instruments were less liquid compared to now".
3. **Unstable labels and class balance that changes with the horizon.** LOBCAST: "the labelling method employed
   is found to be prone to instability" and "the class composition for different values of k is k = 1, U: 18%,
   S: 63%, D:19%; k = 5, U: 32%, S: 35%, D:33%; k = 10, U: 37%, S: 25%, D:38%." So accuracy at different
   horizons is measured against different base rates.
4. **Downsampled.** DeepLOB: "the FI2010 dataset is actually downsampled limit order book data because the
   authors followed [50] to create additional features by using every non-overlapping block of 10 events".
5. **Horizon naming (corrected after review, MG5-01).** DeepLOB's Table II (Setup 2) reports k = 10, 20, 50
   (F1 83.40, 72.82, 80.35) and Table I (Setup 1) reports k = 10, 50, 100 (F1 77.66, 74.96, 76.58); TransLOB's
   Tables 3 to 6 cite the Setup 2 rows at k = 10, 20, 50 consistently ("DeepLOB [41] 74.85 74.06 74.85 72.82"
   under "Table 4: Prediction horizon k = 20"). FI-2010 ships five label columns (k = 1, 2, 3, 5, 10
   representation steps, 10 to 100 events), so a paper's "k = 100" means the fifth column.
6. **Results do not transfer.** LOBCAST: models' "performance significantly drops when applied to unseen
   LOBSTER market data" (Section 4.1).

### 2.4 Items 3 to 8 for FI-2010 as a "method"

FI-2010 is a dataset, not a model, so most of the per-method items do not apply. Data: none of it is CME, and it
cannot be replaced by one Databento contract; the useful lesson is the protocol (day-based anchored forward
splits). Hypothesis for the pilot: none; FI-2010 results should carry zero weight in pre-registration, and
nothing in this program should be tuned on it. Compute: trivial (394,337 rows). Evidence at retail scale: none
possible (problem 1). Verdict in Section 12: skip.

## 3. Later CNN, RNN and transformer models

Each subsection gives the eight items in order: (1) idea, (2) equations, (3) data, (4) what it estimates,
(5) worked example, (6) pilot hypothesis and trial count, (7) compute, (8) evidence. Sections 5 to 10 hold the
cross-cutting evidence; here each item points there when it is shared.

### 3.1 TransLOB (Wallbridge 2020)

Source: Wallbridge, J. (2020), "Transformers for limit order books", arXiv 2003.00130. File
`translob_wallbridge2020.pdf`.

1. **Idea.** Replace DeepLOB's convolution-plus-LSTM with causal (past-only) dilated convolutions that build
   features, followed by masked self-attention, which lets each time step look back at every earlier step and
   weight the relevant ones. Verbatim: "This architecture uses a causal convolutional network for feature
   extraction in combination with masked self-attention to update features based on relevant contextual
   information."
2. **Equations.** Dilated causal convolution with kernel size 2 and dilation d (the paper: "five
   one-dimensional convolutional layers ... with 14 features, kernel size 2 and dilation rates 1, 2, 4, 8 and 16
   respectively"): y_t = ReLU(W_0 x_t + W_1 x_(t-d) + b), where x_t is the 40-vector (first layer) or 14-vector
   (later layers) at step t, W_0 and W_1 are 14 x 40 (or 14 x 14) weight matrices and b a bias; stacking
   d = 1, 2, 4, 8, 16 gives each output a view of the last 1 + 1 + 2 + 4 + 8 + 16 = 32 steps. Then layer
   normalisation and a one-dimensional time encoding, giving X in R^(100 x 15). For each head a = 1..C (C = 3):
   Q_a = X W_a^Q, K_a = X W_a^K, V_a = X W_a^V (W in R^(d x d/C), d = 15), and the paper's masked scaled
   dot-product attention head_a = Softmax(Mask(Q_a K_a^T / sqrt(d))) V_a, where Mask "substitutes infinitesimal
   values to entries in the upper right triangle of the applied matrix which forces queries to only pay
   attention to keys in its causal history". MultiHead(X) = [head_1, ..., head_C] W^O with W^O in R^(d x d);
   then a residual connection and layer normalisation; "two transformer blocks with three heads and with the
   weights shared between iterations of the transformer block"; a feed-forward layer of 64 and a softmax over
   three classes. Softmax(z)_j = exp(z_j) / sum_i exp(z_i) turns each row of scores into weights that sum to 1.
3. **Data.** Same 100 x 40 input as DeepLOB; mbp-10 suffices. Tested only on FI-2010 (7 training, 3 test days).
4. **Estimates.** Three-class probabilities for the FI-2010 label at k in {10, 20, 50, 100}.
5. **Worked example (receptive field, why it matters for MES).** With dilations 1..16 the convolution stack
   sees 32 events, and attention extends that to all 100. If MES book events arrive every 0.05 s (an assumed
   rate for illustration; the pilot will measure it), 100 events are 5 s of history; at 0.2 s (DeepLOB's LSE
   average) they are 20 s. The model's history window in seconds therefore changes with market activity unless
   the input is resampled on a clock.
6. **Pilot hypothesis.** Same form as H-C2-DeepLOB-1 with TransLOB as the classifier; if run alongside DeepLOB
   it adds +1 configuration per horizon to N. There is no reason in the evidence to pre-register it ahead of
   DeepLOB (item 8).
7. **Compute.** LOBCAST counts 1.1 x 10^5 parameters and 2.40 ms inference (its Table 1). My TransLOB-like
   approximation (101,940 parameters) trains at 5,598 samples/s at batch 32 (43 MiB) and 7,725 at batch 256
   (214 MiB) on the RTX 3050; single-sample inference 1.27 ms GPU, 0.65 ms CPU (Section 10). Original training:
   "one K80 GPU on google colab", 150 epochs.
8. **Evidence.** Claimed FI-2010 F1 91.61% at k = 100 (Table 6). LOBCAST could not reproduce it: F1 59.4 ± 2.6
   against a claimed 87.3 ± 4.0 (robustness rank 9 of 15) and "Among the models, TRANSLOB and ATNBOF exhibit the
   largest discrepancies, ranking as the second and first worst performers"; on NASDAQ 2021 and 2022 it scored
   57.7 and 50.4. No cost-inclusive or futures result.

### 3.2 DeepLOB-Seq2Seq and DeepLOB-Attention (Zhang and Zohren 2021)

Source: Zhang, Z. and Zohren, S. (2021), "Multi-Horizon Forecasting for Limit Order Books: Novel Deep Learning
Approaches and Hardware Acceleration using Intelligent Processing Units", arXiv 2105.10430. File
`zhang_zohren_multihorizon2021.pdf`.

1. **Idea.** Keep DeepLOB as the encoder, but instead of one prediction emit a path of predictions for several
   horizons in sequence, each step conditioned on the previous one (an encoder-decoder, as in machine
   translation). Verbatim: "we adopt encoder-decoder models with sequence-to-sequence and Attention mechanisms
   to generate a forecasting path."
2. **Equations** (paper eqs. 4 to 7). Encoder h_t = f(h_(t-1), x_t), f a recurrent cell, h_t its hidden state.
   Context vector for decoder step t: c_t = sum_(i=1..T) alpha_(t,i) h_i with attention weights
   alpha_(t,i) = exp(e(h'_(t-1), h_i)) / sum_(j=1..T) exp(e(h'_(t-1), h_j)), where h'_(t-1) is the decoder's
   previous hidden state and e is a score, one of h_i^T h'_(t-1) ("dot"), h_i^T W_a h'_(t-1) ("general") or a
   form with tanh(W_a [h_i ; h'_(t-1)]) ("concatenate"). Decoder h'_t = f(h'_(t-1), y_(t-1), c_t) and
   P(y_t | y_(t-1), ..., y_1, c_t) = g(h'_t, c_t), g a softmax. Seq2Seq is the special case where c_t is only
   the last encoder state. Labels as DeepLOB eq. 4, with alpha chosen per stock and horizon "to have a balanced
   training set"; their Table 11 lists alpha from 0.10 to 3.05 (units 10^-4, that is 0.10 to 3.05 bp).
3. **Data.** FI-2010 and the LSE year (same as DeepLOB). mbp-10 suffices.
4. **Estimates.** Class probabilities at several horizons from one network.
5. **Worked example (their thresholds in MES ticks).** alpha of 0.10 to 3.05 bp is 0.19 to 5.73 MES ticks at
   4,700 (1 tick = 0.532 bp); for the five main stocks at k = 20 (0.10 to 0.40 bp) it is 0.19 to 0.75 ticks.
   The "up" class at short horizons is therefore defined by moves smaller than one MES tick round-trip fee.
6. **Pilot hypothesis.** Multi-horizon output maps naturally onto the pilot's three markout horizons: one
   network predicts the sign of the 1, 10 and 60 s markouts jointly. H-C2-Attn-1: "the attention model's
   predicted adverse-move probability at placement ranks fills by 10 s markout" (as H-C2-DeepLOB-1). If the
   three horizons are tested it is 3 configurations; pre-registering 10 s as primary and the others as
   descriptive keeps it at +1 confirmatory.
7. **Compute.** Their Table 10 (one NVIDIA GeForce RTX 2080): DeepLOB 96 s per epoch, 105,347 parameters (a different implementation from the 60k paper model; see 10.1);
   "DeepLOB-Seq 215" s and DeepLOB-Attention 270 s per epoch, 177,699 parameters; "The model training lasts for
   200 epochs". So about 2.8 times DeepLOB's cost per epoch. On the RTX 3050 the recurrent decoder is the
   slow part; I did not probe it.
8. **Evidence.** On the LSE test set the gain over plain DeepLOB is small or nil: F1 at k = 20 is 68.40
   (DeepLOB) against 67.76 (Seq2Seq) and 68.09 (Attention); at k = 100, 61.10 against 61.95 and 62.46. LOBCAST
   reproduced DEEPLOBATT at 67.3 ± 9.0 on FI-2010 (claimed 78.8 ± 3.1), 60.1 and 58.9 on NASDAQ 2021 and 2022.
   No costs, no futures.

### 3.3 HLOB (Briola, Bartolucci and Aste 2024)

Source: Briola, A., Bartolucci, S. and Aste, T. (2024), "HLOB: Information Persistence and Structure in Limit
Order Books", arXiv 2405.18938v3. File `hlob_briola2024.pdf`.

1. **Idea.** Instead of assuming that neighbouring book levels interact (as DeepLOB's 1 x 2 convolutions do),
   first measure which volume levels share information (pairwise mutual information on the training days),
   keep only the strongest dependencies as a sparse planar graph (the Triangulated Maximally Filtered Graph,
   TMFG), and build convolutions over the graph's tetrahedra, triangles and edges ("Homological Convolutional
   Neural Networks"), followed by an LSTM.
2. **Equations.** Mutual information between two binned volume series X and Y: MI(X, Y) = sum_x sum_y
   p(x, y) log(p(x, y) / (p(x) p(y))), with p the empirical bin frequencies (standard definition; the paper bins
   volumes: "we categorize volumes into equally spaced bins"). It is zero when X and Y are independent. The
   averaged 2L x 2L MI matrix (L = 10 levels, volumes only: "we reduce the dimension of each LOB snapshot from
   L(τ) ∈ R4L to L(τ) ∈ R2L") is the similarity matrix for TMFG, a greedy construction that adds the vertex
   with the largest summed similarity into a triangular face, so that the graph stays planar and contains
   tetrahedra (4-cliques). The paper motivates the graph as minimising the Kullback-Leibler divergence between
   the true density f(L) and the graph-structured approximation f~(L | G); D_KL(f || f~) = E_f[log f - log f~],
   so minimising it over G means maximising E_f[log f~(L | G)], the expected log-likelihood (equivalently the
   cross-entropy -E_f[log f~]). Labels (from the companion "microstructural guide"): mid-price change over
   H in {10, 50, 100} book updates compared with one tick theta (Section 4.2).
3. **Data.** 15 NASDAQ stocks via LOBSTER, 2017 to 2019; per year "40 days for training, 5 days for validation,
   and 10 consecutive days for testing", and "the 5 days of validation are randomly selected from the same
   period characterizing the training set" (validation days interleaved with training days, which makes early
   stopping slightly optimistic). For MES, mbp-10 gives the 20 volume series it needs.
4. **Estimates.** Up/stable/down probabilities of the next-H-update mid change, at a one-tick threshold.
5. **Worked example (mutual information of two binned series).** Two binary bins with joint table p(0,0) = 0.4,
   p(0,1) = 0.1, p(1,0) = 0.1, p(1,1) = 0.4 (marginals 0.5 each): MI = 2 x 0.4 log(0.4/0.25) + 2 x 0.1
   log(0.1/0.25) = 0.8 x 0.470 + 0.2 x (-0.916) = 0.376 - 0.183 = 0.193 nats. An independent pair (all cells
   0.25) gives 0. HLOB keeps the edges with the largest such values.
6. **Pilot hypothesis.** HLOB's own finding is that structure and predictability are strongest for large-tick
   instruments (average spread close to one tick), which is what MES is. H-C2-HLOB-1 would be the same
   adverse-selection test as H-C2-DeepLOB-1 with HLOB as the classifier (+1 to N per horizon). Its extra
   researcher degrees of freedom (number of volume bins, which training days build the MI matrix) must be fixed
   before seeing test data or counted.
7. **Compute.** The layers the paper lists are small (for example "the number of parameters for the
   convolutional operation involving tetrahedra is equal to 12 384"); the TMFG build is a one-off O(n^2) step on
   a 20 x 20 matrix. The companion study's 135 experiments took "a cumulative GPU runtime of 959 hours, 16
   minutes and 27 seconds" on a university cluster (about 7.1 GPU-hours per experiment).
8. **Evidence.** Mixed even in-sample by the authors' own account: at the longest horizon "For small-tick
   stocks, HLOB is the best-performing model in 1/6 scenarios"; "For large-tick stocks, it is the
   best-performing model in 4/6 cases"; average F1 0.32 (small-tick) and 0.52 (large-tick), average MCC 0.05
   and 0.30, average pT 0.05 for small-tick stocks (pT is the probability of a correct complete transaction,
   Section 4.3). The conclusion concedes that "applying a dual-attention mechanism on the input data spatial and
   temporal dimensions guarantees ... enhanced performances ... offering an edge over HLOB". No costs, no
   futures.

### 3.4 TLOB and MLPLOB (Berti and Kasneci 2025), and BiN-CTABL

Source: Berti, L. and Kasneci, G. (2025), "TLOB: A Novel Transformer Model with Dual Attention for Price Trend
Prediction with Limit Order Book Data", arXiv 2502.15757v3. File `tlob_berti2025.pdf`.

1. **Idea.** A transformer that alternates attention across time (which past snapshots matter) and across
   features (which book levels matter), plus a plain MLP baseline (MLPLOB) that, surprisingly, already beats
   the earlier deep models. Verbatim: "by adapting a simple MLP-based architecture to LOB, we show that we
   surpass SoTA performance; thus, challenging the necessity of complex architectures."
2. **Equations.** Label (their eqs. 6 and 7): w_-(t, h, k) = (1/(k + 1)) sum_(i=0..k) p_(t-i) (backward
   average), w_+(t, h, k) the forward average over the horizon h, l(t, h, k) = (w_+ - w_-) / w_-, "upward if
   l(t, h, k) > θ, downward if l(t, h, k) < −θ, and stable if −θ ≤ l(t, h, k) ≤ θ". Their key move: set theta to
   the average spread as a fraction of mid ("setting it equal to the average spread as a percentage of the
   mid-price, reflecting the primary transaction cost"). MLPLOB block (their eq. 9): Z = sigma(LayerNorm(
   sigma(U W_3) W_4 + U)), with U the block input, W_3 and W_4 weight matrices, sigma a nonlinearity, and the
   "+ U" a skip connection.
3. **Data.** FI-2010; TSLA and INTC from LOBSTER for January 2015 ("20 order book files for each stock",
   "the initial 17 days are allocated for training, the 18th day for validation, and the final two days for
   testing"); 12 days of Binance BTCUSDT perpetual in January 2023.
4. **Estimates.** Three-class trend probabilities at h in {10, 20, 50, 100} (FI-2010) or {50, 100, 200}.
5. **Worked example (spread threshold on MES).** If MES's average spread is 1 tick (an assumption the pilot
   will check), theta = 1 tick / mid = 0.532 bp at 4,700. A label "up" then means the forward mean mid exceeds
   the backward mean by more than one tick, the minimum that could cover a crossed spread, but still not the
   0.976-tick fee on top. A cost-aware MES threshold would be about 2 ticks (1.98) for a taker-taker round trip.
6. **Pilot hypothesis.** H-C2-TLOB-1: "with theta set to the measured average spread plus the fee, a
   TLOB/MLPLOB classifier's out-of-sample three-class F1 exceeds a no-skill benchmark (the class-prior
   classifier) by a pre-set margin, and its 'up' calls have positive mean 10 s mid change net of the fee".
   Statistic: mean net mid change after 'up' minus after 'down' calls, HAC t > 3.0. +1 to N per (model,
   horizon); MLPLOB should be the default because it is simpler and was at least as good.
7. **Compute.** Their Table 2 prints "MLPLOB TLOB 6.3 · 107 1 · 107 4.79 2.24" (parameters, then inference
   ms; the column pairing in the extracted text is ambiguous, but both are of order 10^7 parameters, about 150 to
   1,000 times the paper's DeepLOB). "All the experiments were carried out using an RTX 3090." A 10^7-parameter model at batch 32
   would still fit 4 GB (weights plus Adam state are about 16 bytes per parameter, so 0.16 GB at 10^7), but
   training would be correspondingly slower; not probed.
8. **Evidence.** With the cost-aware threshold, performance collapses toward chance: "Table 8: F1-score on
   Tesla with θ set to the average spread" shows TLOB at 41.39, 36.48 and 30.82 for h = 50, 100, 200 (three
   classes; 33% is chance), and for Intel the method could not be applied because it "would result in 99.99% of
   trends classified as stationary". Their decay evidence is one day against one day: "we tested on a day of
   Intel from 2012/06/21[footnote marker 10 removed] and confronted the difference in performance with 2015/01/30" (F1 66.87 against
   60.19). They concede: "the proposed methodologies are not sufficiently mature for practical deployment in
   live trading environments".

**BiN-CTABL** (Tran et al. 2021, bilinear network with temporal attention and bilinear input normalisation):
not fetched separately; known here only through LOBCAST, where it was the best and most robust model:
F1 82.6 ± 7.0 on FI-2010 (claimed 80.1), "the strongest robustness score of 99.7", but on NASDAQ data "BINCTABL
experiences an average decrease of approximately 19.6% in F1-Score across all horizons" (61.2 and 59.2 on 2021
and 2022). It has 1.1 x 10^4 parameters and 0.71 ms inference (LOBCAST Table 1). Lesson: the most robust model
is one of the smallest.

### 3.5 Deep learning on market-by-order data (Zhang, Lim and Zohren 2021)

Source: Zhang, Z., Lim, B. and Zohren, S. (2021), "Deep Learning for Market by Order Data", arXiv 2102.08811
(Applied Mathematical Finance). File `mbo_zhang2021.pdf`.

1. **Idea.** Feed the model the raw order messages (add, modify, cancel, with side, price and size, keyed by
   order ID) instead of the aggregated book. Verbatim: "while MBO-driven and LOB-driven models individually
   provide similar performance, ensembles of the two can lead to improvements in forecasting accuracy".
2. **Equations.** Each message is preprocessed into features including Action in {-1, 0, 1} ("-1 means
   cancelling an order, 0 means updating price or size for the existing order and 1 means adding a new order"),
   Side, Price, Size, and "Change price and Change size ... the difference between entries for the price and
   size of a specific ID"; prices are normalised to their level relative to the book so instruments can be
   pooled. Sequence models (LSTM, attention as in Section 3.2) map the last T messages to the DeepLOB-style
   label.
3. **Data.** "MBO data over a period of one year for five highly liquid instruments from the London Stock
   Exchange". For MES this needs Databento's mbo schema: "Market by order (MBO) provides every order book event
   across every price level, keyed by its order ID. This allows you to determine the queue position of each
   order". mbp-10 is not enough.
4. **Estimates.** Same three-class label.
5. **Worked example (what the numbers say).** At k = 20: LOB-DeepLOB F1 68.40; MBO-LSTM 61.75;
   Ensemble-MBO-LOB 69.02. The MBO-only model is about 6.6 F1 points worse, and the ensemble adds
   69.02 - 68.40 = 0.62 points. At k = 100: 61.10 against 54.79 and 61.82 (+0.72).
6. **Pilot hypothesis.** The useful link is not the classifier but the data: mbo gives each order's queue
   position, which is what a passive-fill simulation needs. If Part B buys mbo, H-C2-MBO-1: "queue position at
   placement (from mbo) predicts the 10 s markout of filled passive orders" is a cheaper, interpretable test
   than any deep model (+1 to N). A deep MBO model would add +1 per horizon.
7. **Compute.** Sequence models of the same size class as DeepLOB-Attention; mbo files are larger than mbp-10
   (every order event at every level). Not probed.
8. **Evidence.** LSE equities only, no costs, no futures. The gain from MBO is under one F1 point.

## 4. Benchmark and reproducibility studies (the evaluation methods)

These are methods for judging the models above. The eight items are adapted: "what it estimates" is what the
evaluation measures, and the pilot item is how to adopt the evaluation in a pre-registration.

### 4.1 LOBCAST (Prata, Masi, Berti and others 2024)

Source: Prata, M. et al. (2024), "LOB-Based Deep Learning Models for Stock Price Trend Prediction: A Benchmark
Study", Artificial Intelligence Review; arXiv 2308.01915v2. File `lobcast_prata2024.pdf`. Code:
github.com/matteoprata/LOBCAST.

1. **Idea.** Re-run 15 published models under one pipeline, five seeds each, on FI-2010 (robustness: do the
   claims reproduce?) and on fresh NASDAQ data (generalisability: do they transfer?). Verbatim: "Our extensive
   experiments reveal that all models exhibit a significant performance drop when exposed to new data, thereby
   raising questions about their real-world market applicability."
2. **Equations.** Robustness and generalisability score: "a value ≤ 100 that is computed as 100 − (|A| + S)",
   where A is the average, over the declared horizons and five seeds, of (claimed F1 minus measured F1), on
   FI-2010 for robustness and on LOB-2021/2022 for generalisability, and S the standard deviation of those
   differences. Labels as
   FI-2010 (Section 2.2). F1 for a class c = 2 precision_c recall_c / (precision_c + recall_c), averaged over
   classes (macro F1), which is insensitive to the large "stationary" class in the way accuracy is not.
3. **Data.** FI-2010; LOB-2021 (2021-07-01 to 2021-07-15) and LOB-2022 (2022-02-01 to 2022-02-15), six NASDAQ
   stocks from LOBSTER, sampled every 10 events, "6-2-2 days split", z-scored.
4. **Measures.** Reproducibility and transfer of F1; a gross-of-costs backtest.
5. **Worked example (DeepLOB's scores).** Claimed 78.9 ± 4.4; measured 71.4 ± 5.3 on FI-2010, robustness 87.6
   (so |A| + S = 12.4); 59.5 ± 3.0 on LOB-2021 (generalisability 73.7: |78.9 - 59.5| = 19.4, plus S of about
   6.9 across seeds and horizons, gives 100 - 26.3 = 73.7; S here is the paper's own spread term, not the
   ± printed beside the mean); 59.5 ± 2.9 on LOB-2022 (74.7).
6. **Pilot adoption.** Adopt LOBCAST's discipline in any pre-registration: several seeds reported as a
   distribution, no hyperparameter search on the test window, and the "claimed versus measured" comparison
   replaced by "validation versus one-shot test". The trial count must include every seed and setting that could
   have been selected; if results are averaged over a fixed pre-declared set of seeds, the seeds are one
   configuration.
7. **Compute.** "the training process for all the models took approximately 155 hours for FI-2010 and 258 hours
   for LOB-2021/2022, utilizing a cluster comprised of 8 GPUs (1 NVIDIA GeForce RTX 2060, 2 NVIDIA GeForce RTX
   3070, and 5 NVIDIA Quadro RTX 6000)".
8. **Evidence.** (a) "All models are very sensitive to hyperparameters, in fact, they diverged (F1-score ⩽ 33%)
   during the hyperparameters search for about half of the runs." (b) On NASDAQ data F1 is "ranging 48-61%".
   (c) Their backtest assumed "no transaction fees", fills "at the next open price", one share; "the two stocks
   with the highest positive daily returns (namely LSTR and NFLX) are the only ones for which the strategy is
   profitable", that is, profit tracked the stock's drift, not the model. They also note inference "in the order
   of milliseconds, potentially unsuitable for HFT applications" for DeepLOB (1.31 ms), TransLOB (2.40 ms) and
   DeepLOB-Attention (1.73 ms).

### 4.2 Briola, Turiel and Aste (2020): an MLP is as good

Source: Briola, A., Turiel, J. and Aste, T. (2020), "Deep Learning modeling of Limit Order Book: a comparative
perspective", arXiv 2007.07319v3. File `briola_turiel_aste2020_comparative.pdf`.

1. **Idea.** Compare random, logistic regression, MLP, LSTM, attention-LSTM and CNN-LSTM on one dataset, one
   label and one feature set. Verbatim: "We observe that the Multilayer Perceptron performs comparably to or
   better than state-of-the-art CNN-LSTM architectures".
2. **Equations.** Targets are quantile classes of the H-step log return (q_-1, q_0, q_+1) at H in {10, 50,
   100} events; metrics include balanced accuracy and the Matthews correlation coefficient (MCC, defined in
   4.3).
3. **Data.** "Intel Corporation’s (INTC) LOB data from 04-02-2019 to 31-05-2019 ... while the test dataset
   consists of Intel Corporation's LOB data from 03-06-2019 to 28-06-2019"; INTC "is representative of a large
   tick stock". About four months of one large-tick instrument: the same shape as the Part B purchase.
4. **Measures.** Whether depth (CNN, LSTM) adds anything over a feed-forward network on the same inputs.
5. **Worked example.** Not needed; the result is an ordering ("the MLP outperforms the CNN-LSTM throughout
   metrics and horizons (or performs analogously)").
6. **Pilot adoption.** Any deep model in a pre-registration should be tested against a pre-declared MLP and
   logistic regression on the same inputs; the deep model counts as useful only if it beats them on the test
   window. Each baseline is +1 to N.
7. **Compute.** Small. Not reported in a form I could extract.
8. **Evidence.** Negative for architecture complexity. The same finding recurs: TLOB's MLPLOB (Section 3.4),
   and a 2025 BTC/USDT study where "simpler models can match and even exceed the performance of more complex
   networks" (Wang 2025, arXiv 2506.05764, file `crypto_inputs2025.pdf`; caveat: one trading day of data,
   "a single trading day, 2025-01-30, sampled at 100ms intervals", and it smooths features with Kalman and
   Savitzky-Golay filters, the latter normally a centred window that would use future values unless applied
   causally, which the paper does not state).

### 4.3 Briola, Bartolucci and Aste (2024): "Deep limit order book forecasting: a microstructural guide"

Source: Briola, A., Bartolucci, S. and Aste, T. (2024), "Deep Limit Order Book Forecasting: A Microstructural
Guide", arXiv 2403.09267v4 (published in Quantitative Finance, 2025, DOI 10.1080/14697688.2025.2522911 per a
search result for the LSE repository record; [unverified] from the search snippet, not fetched). File
`briola_microstructural_guide2024.pdf`. Code: LOBFrame (github.com/FinancialComputingUCL/LOBFrame).

1. **Idea.** Train DeepLOB on 15 NASDAQ stocks over three years and show that (a) predictability depends on
   tick size and liquidity, and (b) accuracy-type metrics overstate usefulness; propose a transaction-level
   metric. Verbatim: "We demonstrate that the stocks’ microstructural characteristics influence the efficacy of
   deep learning methods and that their high forecasting power does not necessarily correspond to actionable
   trading signals."
2. **Equations.**
   - Label (paper eq. 2): Down if (m_(tau+Delta tau) - m_tau) <= -theta; Stable if -theta < (m_(tau+Delta tau)
     - m_tau) < +theta; Up if >= +theta, "where θ is the tick size and mτ is the mid-price at time τ", and
     "horizons are always defined in terms of LOB updates (which are unevenly spaced), while physical time is
     never used". Unlike DeepLOB, no smoothing and no percentage: a raw mid-price difference against one tick.
   - Tick-size classes: "if (i) ⟨σ⟩ ≳ 3θ, we are dealing with a small-tick stock; if (ii) ⟨σ⟩ ≲ 1.5θ, we are
     dealing with a large-tick stock", with ⟨σ⟩ the average bid-ask spread.
   - Transaction metric (paper eq. 3): pT = CT / (PT + TT - CT), where PT is the number of potential
     transactions (open-then-close sequences in the true labels), TT the number executed on the predicted
     labels, and CT those that match in both. It is the size of the intersection over the size of the union
     (a Jaccard index) of true and predicted round trips.
   - MCC for K classes (Gorodkin's form): MCC = (c s - sum_k p_k t_k) / sqrt((s^2 - sum_k p_k^2)(s^2 - sum_k
     t_k^2)), with s the number of samples, c the number correctly classified, t_k the true count and p_k the
     predicted count of class k; 0 for random guessing, 1 for perfect (standard definition; the paper: "a value
     of 0 indicates a random prediction").
3. **Data.** LOBSTER, 15 stocks, 2017 to 2019, 10 levels; DeepLOB with AdamW, "a learning rate equal to 6 ×
   10−5", batch 32, up to 100 epochs with patience 15.
4. **Measures.** MCC and pT by stock class and horizon.
5. **Worked example (pT).** Suppose the true labels contain 100 round trips (PT = 100), the model triggers 100
   (TT = 100) and 10 of them coincide (CT = 10). pT = 10 / (100 + 100 - 10) = 10/190 = 0.053. The paper's
   large-tick average at H10 is "0.10", and "the average pT value for this class of stocks equals 0.10, with a
   smoother decrease for higher threshold values". So about one in ten predicted-or-true round trips is caught
   correctly, even where predictability is best.
6. **Pilot adoption.** Pre-register a transaction-level primary metric, not F1 or accuracy: for example "the
   fraction of model-triggered round trips whose net P&L after the 0.976-tick fee is positive, and the mean net
   P&L per round trip, with a day-clustered t". MES is a large-tick contract by this definition if its average
   spread is under 1.5 ticks (the pilot measures this), which is where the paper finds the most structure. One
   primary metric is +0 configurations by itself; it fixes how the +1 per model is judged.
7. **Compute.** "A total number of 135 experiments have been run ... for a cumulative GPU runtime of 959 hours,
   16 minutes and 27 seconds" on GTX 1080 Ti to V100 GPUs: about 7.1 GPU-hours per DeepLOB experiment (one
   stock, one year, one horizon).
8. **Evidence.** MCC for large-tick stocks at H10 "is 0.29 (18 units higher than the one characterizing
   small-tick" stocks), small-tick 0.11; at H50 small-tick 0.04; pT averages of 0.06 to 0.12 at H10 (large-tick 0.10). The paper refuses to
   backtest: "backtesting a trading strategy based on the outputs of a deep learning model by using historical
   data-only is not possible", because it would require "(ii) being always executed; (iii) having a zero
   market-impact; (iv) having zero transaction costs". And: "achieving high scores on these traditional machine
   learning metrics does not necessarily translate into the generation of actionable trading signals".

### 4.4 Lucchese, Pakkanen and Veraart (2024): predictability exists, is short, and is tested properly

Source: Lucchese, L., Pakkanen, M. S. and Veraart, A. E. D. (2024), "The short-term predictability of returns
in order book markets: a deep learning perspective", International Journal of Forecasting; arXiv 2211.13777v3.
File `lucchese2024_predictability.pdf`.

1. **Idea.** Test whether DeepLOB-type models beat an "unpredictive benchmark" using model confidence sets
   (Hansen, Lunde and Nason 2011) rather than raw accuracy, over many horizons and stocks, and introduce a
   "volume representation" of the book (sizes on a fixed grid of ticks around the mid, with zeros for empty
   ticks) that is more robust than the level-by-level layout. Verbatim: "Our findings show that at high
   frequencies predictability in mid-price returns is not just present, but ubiquitous."
2. **Equations.** Mid-price on the tick grid: R_(t,t+h) = m_(t+h) - m_t in {..., -theta, -theta/2, 0,
   theta/2, theta, ...} (their notation uses the tick size). Smoothed target: m_(t+h)^(k) = (1/(2k + 1))
   sum_(i=-k..k) m_(t+h+i), "we fix k = 5". Classes: down if r < -gamma, flat if in [-gamma, gamma], up if >
   gamma, with gamma_h = (|Q_h(0.33)| + Q_h(0.66)) / 2 from training-set quantiles (balance, not cost).
   Predictability means lower test-set categorical cross-entropy than the benchmark that predicts the training
   class frequencies. The MCS procedure starts with all models, tests equal expected loss, removes the worst
   model while that is rejected, and reports for each model a p-value of belonging to the set of best models; a
   small MCS p-value for the unpredictive benchmark means some model beats it.
3. **Data.** LOBSTER, "one year of open (9:30 EST) to close (16:00 EST) trading data for 115 Nasdaq tickers from
   January 2, 2019, to January 31, 2020", 10 tickers used; validation days chosen "by randomly selecting 5 days"
   inside the training window.
4. **Measures.** At which horizons any model beats the no-skill benchmark, per stock.
5. **Worked example (MCS logic).** With three models whose mean test cross-entropies are 1.050 (benchmark),
   1.040 and 1.038, the MCS first tests whether all three have equal expected loss; if rejected it drops the
   worst (the benchmark); a benchmark MCS p-value of 0.003 says the benchmark is outside the 99% set, so at least
   one model has real predictive content at that horizon. The size of the improvement (here 0.010 nats per
   sample) is a separate question and says nothing about money.
6. **Pilot adoption.** The MCS is a principled way to compare several pre-declared models while controlling the
   family-wise error, and it would sit beside the program's Holm and DSR machinery. Each model in the set is
   still +1 to N.
7. **Compute.** Not extracted.
8. **Evidence.** "we were able to identify predictability up to 50 order book events ahead at the 99% confidence
   level" for most stocks. No trading or cost test. On latency, Appendix A.7 notes that co-located systems reach
   "tick-to-trade latency ... of the order of a couple of microseconds" and that deep models need "a couple of
   hundred microseconds"; the paper assumed "instantaneous access" and lists "how predictability varies as a
   function of" latency as "An interesting analysis", that is, untested (Section 9).

### 4.5 Sirignano and Cont (2019): the universality claim

Source: Sirignano, J. and Cont, R. (2019), "Universal features of price formation in financial markets:
perspectives from deep learning", Quantitative Finance 19(9); arXiv 1803.06917. File `sirignano_cont2019.pdf`.

Core claim: "The universal price formation model exhibits a remarkably stable out-of-sample prediction accuracy
across time, for a wide range of stocks from different sectors." The target is the direction of the next
mid-price move (event time), from LSTM networks trained on "billions of electronic market quotes and
transactions for US equities"; training "is parallelized over approximately 500 compute nodes" on a
supercomputer. This is the strongest published evidence of stability over time, but it concerns the next price
change, with no costs, no latency and no futures, and its compute is far outside this program's reach. For the
pilot it suggests pooling: a model trained across several CME contracts may beat a single-contract model, which
argues against a one-contract purchase if a deep model is ever the goal.

## 5. Results on futures and CME data

Searched for DeepLOB-family studies on CME futures (four WebSearch queries plus arXiv API queries; log in
Section 13). Three futures studies were found and read in full; none is a cost-inclusive, latency-aware test of a
deep order-book model on a micro contract.

### 5.1 CME Eurodollar futures, Level 1, 2018 (Spears, Zohren and Roberts 2020)

Source: arXiv 2007.15982, "Investment sizing with deep learning prediction uncertainties for high-frequency
Eurodollar futures trading". File `eurodollar_sizing2020.pdf`.

1. **Idea.** Predict short-horizon changes of Eurodollar futures micro-prices with an MLP and a "CNN-LSTM with
   inception (CNN-LSTM Inc)" (the DeepLOB family), and scale each position by the model's uncertainty estimate.
2. **Equations.** Micro-price (as printed): P_t^c = (ask volume_t^c · bid price_t^c + ask price_t^c · bid
   volume_t^c) / (ask volume_t^c + bid volume_t^c), the size-weighted mid of the best quotes of contract c
   (weights each side's price by the opposite side's size, so the price leans toward the thinner side, where
   the next move is more likely). Uncertainty from Monte Carlo dropout ("rescaling the final model weights by
   this proportion at test time"); position size alpha_t scaled by aleatoric (Al) and epistemic (Ep)
   uncertainty; trade only if |alpha_t| exceeds a threshold of 0.1 bp.
3. **Data.** "Thomson Reuters data for continuous contract EDc1 to EDc15 for each US trading day of 2018. This
   data reflects Level 1 limit order book best bid-ask-volume quotes"; analysis on EDc7 to EDc15. A one-contract
   Databento tbbo or mbp-1 purchase would give data of this type for one contract; the paper uses nine.
4. **Estimates.** A regression forecast of the micro-price change and its variance.
5. **Worked example (where the edge dies).** Their cost unit is "0.005bps per unit volume"; the Sharpe of every
   strategy turns negative at "12 ... the minimal integral multiple of transaction costs such that the Sharpe
   ratios for each presented strategy is negative", that is 12 x 0.005 = 0.06 bp. The median spread is "0.5
   basis points (bps)". So the strategies survive at most 0.06 / 0.5 = 12% of the spread; any strategy that pays
   even a sixth of the spread per unit loses money.
6. **Pilot hypothesis.** Not a direct fit; the transferable piece is uncertainty-scaled sizing, which does not
   apply to a fixed 1-lot passive order.
7. **Compute.** Small models; not reported in a form I could extract.
8. **Evidence.** The authors: "the transaction costs analysed here are significantly less than the median daily
   bid-ask spread of 0.5bps ... it is important to understand that the approach presented may not necessarily be
   traded outright as a stand alone strategy in practice." Negative for a stand-alone retail strategy.

### 5.2 CME E-mini S&P 500 (ESU6), Level II, August 2016 (Dixon 2017, two papers)

Sources: Dixon, M. (2017), "Sequence Classification of the Limit Order Book using Recurrent Neural Networks",
arXiv 1707.05642 (file `dixon_rnn_seq2017.pdf`); Dixon, M. (2017), "A High Frequency Trade Execution Model for
Supervised Learning", arXiv 1710.03870 (file `dixon_execution2017.pdf`).

1. **Idea.** Predict the next mid-price "flip" of ES from book depths and market orders with an RNN, and use
   the prediction to move a market maker's quotes away before an adverse move. The second paper adds a "trade
   information matrix": the expected P&L of each (predicted, actual) cell of the confusion matrix under a fill
   model with queue position. Verbatim: "The capability to adjust quotes according to this prediction reduces
   the likelihood of adverse price selection."
2. **Equations.** Expected P&L per decision = sum over predicted class i and actual class j of
   P(predicted i, actual j) x E[P&L | i, j], where E[P&L | i, j] comes from a fill model (queue position of a
   reference order, fill when the trade-to-book ratio exceeds what is ahead of it: "the reference order is
   partially filled if the trade-to-book ratio is above 1/11" in their example). This decomposition makes the
   cost of each kind of error explicit (a false "stationary" before a flip costs the spread plus the adverse
   tick; a false "flip" costs only lost fills).
3. **Data.** "from August 1, 2016 to August 31, 2016 ... the front month E-mini S&P 500 (ESU6) between the times
   of 12:00pm and 22:00 UTC". One month of one CME contract at Level II: the Part B shape. Queue position needs
   mbo (or an estimate from mbp-10).
4. **Estimates.** Probability of an up-flip, down-flip or no flip at the next mid change (up to 1 s ahead).
5. **Worked example (the matrix on MES numbers, illustrative).** A resting 1-lot bid fills. If no flip follows
   (prob 0.80 in this toy), the market maker can later sell at the ask: +1 tick (+$1.25) minus fee 0.976 tick
   = +0.024 tick. If a down-flip follows (0.20), it is stuck 1 tick under water: exit at -1 tick minus fee =
   -1.976 ticks. Blind quoting: 0.80 x 0.024 + 0.20 x (-1.976) = -0.376 ticks per fill. A classifier that warns
   of 75% of down-flips (recall 0.75) at the cost of skipping 10% of the good fills changes the mix to
   0.72 x 0.024 + 0.05 x (-1.976) = -0.081 ticks per opportunity, still negative. On MES the 0.976-tick fee
   alone exceeds the 1-tick spread capture minus almost any adverse selection, which is the pilot's question.
6. **Pilot hypothesis.** This is the closest published design to Part B. H-C2-Dixon-1: "Conditional on fill,
   the 10 s markout of a 1-lot passive MES order is higher when a pre-registered classifier (logistic or RNN on
   book imbalance and recent order flow) does not predict an adverse flip at placement", with the trade
   information matrix filled from the pilot's measured fill rates and markouts. Statistic: difference in mean
   markout, HAC or day-clustered t > 3.0. Sample as in Section 1.7. +1 to N per classifier.
7. **Compute.** The RNN search "yields several candidate architectures" in "several hours on a modern graphics
   processing unit (GPU)"; inference estimated at "around 100 micro-seconds on a modern CPU" in C++.
8. **Evidence.** Thin and favourable to the idea only under ideal assumptions. The backtest is 90 minutes of one
   day: "applied to ESU6 data from 11am to 12:30pm (CST) on August the 4th, 2016 ... With perfect information,
   and 0ms latency, strategy M M 2 is shown to outperform strategy M M 1", at "a transaction cost per contract of
   35 cents" (a clearing-member rate, below the TopstepX fee). Horizon decay: "the performance of the RNN decays as
   we increase the prediction horizon from the next book update event to 1s in the future", with colocated
   latency "in the range of 100 micro-seconds to 1ms". The author's own recommendation: "first design a market
   making strategy that is profitable after accounting for additional latency". He also cites earlier work that
   "the information content of the limit order book does not seem to translate to greater economic profits
   through different high frequency trading rules" (Kozhan and Salmon 2012; Kearns and Nevmyvaka 2013; not
   fetched).

### 5.3 Eurex Bund futures, 2022 (DeepLOB as a benchmark)

Source: arXiv 2501.08822, "Deep Learning Meets Queue-Reactive: A Framework for Realistic Limit Order Book
Simulation" (file `dlqr_bund2025.pdf`). Data: "Euro-Bund Futures (FGBL), specifically covering active trading
days over three months from March to June 2022", five levels. DeepLOB was trained on "one month of limit order
book data, with a two-day validation period and three-day test period", with a horizon of "k = 500 events" and
a threshold of "20 basis points to achieve balanced class distributions". Result: "the DeepLOB architecture ...
achieves a baseline performance with balanced accuracy of 0.54" (three classes, chance 0.33), matched by a much
simpler queue-reactive model ("The QR model matches this performance despite its simpler architecture"). No
trading test. The threshold is again chosen for class balance.

### 5.4 Not found

No paper applying DeepLOB, TransLOB, HLOB or TLOB to MES, ES, NQ or any other CME equity-index future with fees,
spread and latency was found. The Kolm, Turiel and Westray (2023) "Deep order flow imbalance" study (Mathematical
Finance 33(4), 1044-1081) covers 115 NASDAQ stocks, not futures; I could not fetch it (paywall). A Quantpedia
summary seen in a search snippet says forecasts have an "accuracy peak" at about two price changes [unverified,
search snippet only].

## 6. Label design at horizons whose moves beat the spread and fees

### 6.1 What the literature did, in MES ticks

| Study | Label threshold | Horizon | Threshold in MES ticks at 4,700 | Chosen for |
|---|---|---|---|---|
| FI-2010 / DeepLOB on FI-2010 | 0.002 on eq. 3 | 10 to 100 events | 37.6 | class balance at k = 5 |
| DeepLOB, DeepLOB-Attention on LSE | 0.10 to 3.05 bp on eq. 4 | 20, 50, 100 events | 0.19 to 5.73 | "a balanced training set" |
| Briola et al. 2024, HLOB | one tick, raw mid difference | 10, 50, 100 updates | 1 (for MES) | tick grid |
| Lucchese et al. 2024 | training-set 33/66% quantiles | 10 to 1000 events | data-dependent | balance |
| TLOB, Section 7.5 | average spread / mid | 50 to 200 | about 1 if the spread is 1 tick | cost, partly |
| Bund benchmark | "20 basis points" | 500 events | not comparable | balance |

Only TLOB's last experiment ties the threshold to a cost, and only to the spread, not the fee.

### 6.2 Rules for a cost-aware label on one CME contract

1. **Measure the move from a price you can trade.** DeepLOB's eq. 4 compares a forward mean with a backward
   mean m_-(t); a trade entered at t is priced at p_t or at the touch. Use r_t = m_+(t) - p_t (eq. 3 form) or,
   for a passive strategy, the markout of the hypothetical fill.
2. **Set the threshold in ticks at or above the round-trip cost.** For MES: 0.976 ticks of fees; about 1.98
   ticks for a taker-taker round trip at a 1-tick spread; 0.976 ticks plus the measured adverse selection for a
   maker entry and taker exit. A 2-tick threshold is the natural floor for an aggressive strategy.
3. **Use clock time or price-change time, not event time, if the strategy acts on a clock.** The pilot measures
   1, 10 and 60 s markouts. Event-time horizons (k = 100 events) shrink in seconds when the market is busy;
   Lucchese et al. found that predictability persists over more events for stocks with more book updates per price change (it is "easier for the deep learning models to predict returns that are the result of fewer price changes"), and
   "One might thus expect to obtain a more consistent maximum predictable horizon across stocks when using a
   price change-driven clock".
4. **Accept heavy class imbalance rather than lowering the threshold.** With a cost-aware threshold most short
   horizons are "stationary" (TLOB on Intel: "99.99% of trends classified as stationary"). Use class weights or
   a regression target (expected move in ticks) instead of shrinking theta to balance classes.
5. **Condition on the action.** For a passive order the right label is "markout of a fill that would have
   happened", which requires a fill model (queue position from mbo, or the pilot's measured fill
   probabilities). Labels computed on all book events overstate what a resting order earns, because fills
   happen disproportionately just before adverse moves (adverse selection).
6. **Purge and embargo by the label horizon.** A label at t uses prices up to t + h, so training samples within
   h of a test sample leak; drop them (purge) and add an embargo gap, as V43 requires.

### 6.3 Worked example: the hit rate a direction call needs

A long or short call wins g ticks when right and loses l ticks when wrong; cost c per round trip. Expected
P&L E = h g - (1 - h) l - c, so break-even h* = (l + c) / (g + l). With c = 0.976 (fee only, passive entry and
aggressive exit at mid-equivalent): g = l = 1 tick needs h* = 0.988; g = l = 2 ticks needs 0.744; g = l = 4
ticks needs 0.622. Adding one more tick of cost (both legs aggressive): 1.488 (impossible), 0.994 and 0.747.
With a stationary outcome allowed: P(right) 0.60, P(stationary) 0.25, P(wrong) 0.15, moves of 1.5 ticks: gross
0.60 x 1.5 - 0.15 x 1.5 = 0.675 ticks, net of fee -0.301; with 3-tick moves gross 1.350, net +0.374, net of fee
and 1 tick of spread -0.626. (Script: `C2_worked_examples.py`.) The precision of the published models'
up/down classes at short horizons is in the 60 to 70% range (DeepLOB LSE Table IV), at thresholds below one MES
tick (Section 3.2 item 5). Those numbers do not clear these break-evens.

## 7. Post-publication results and decay

What was found, strongest first:

- **Out-of-dataset drops (not strictly post-publication).** LOBCAST: claimed FI-2010 F1 of 79 to 87 fall to 48
  to 61 on NASDAQ 2021 and 2022 for every model (Section 4.1). "we conjecture that the overall performance is
  worse in LOB-2022 than in LOB-2021 due to the higher stocks’ volatility."
- **Within-month decay without retraining, on CME ES.** Dixon: "The F1 scores are observed to exhibit a secular
  decay when the model is not re-trained on a daily basis but instead trained only at the beginning of the
  month", though "a model trained at the beginning of the month can still be effective weeks later".
- **Over years.** TLOB: Intel 2012 F1 66.87 against 2015 60.19, but one day each ("we tested on a day of Intel
  from 2012/06/21[footnote marker 10 removed] and confronted the difference in performance with 2015/01/30"), so weak.
- **Counter-evidence: stability.** Sirignano and Cont report "remarkably stable out-of-sample prediction accuracy
  across time"; DeepLOB reports stable accuracy over its 3-month LSE test and on untrained stocks. Both are
  accuracy, gross, pre-2018 data.
- **Not found.** No study re-tests DeepLOB or its successors on data after their publication with costs on a
  futures contract. No study measures decay of order-book deep-model predictability year by year on CME data
  (one search, null). A gap, not a finding.

## 8. The gap between classification accuracy and net trading profit

Every cost-aware test found points the same way:

| Evidence | What it shows | Source file |
|---|---|---|
| DeepLOB's own simulation is "gross profits before fees" at mid | the headline profit result excludes costs by design | `deeplob_zhang2019.pdf` |
| LOBCAST backtest: profit only on the two stocks with the highest daily returns | gross profit tracked drift | `lobcast_prata2024.pdf` |
| Briola et al.: pT averages of 0.06 to 0.12 at H10 (large-tick 0.10); "high forecasting power does not necessarily correspond to actionable trading signals" | about 1 in 10 round trips caught | `briola_microstructural_guide2024.pdf` |
| TLOB with spread threshold: F1 41.4, 36.5, 30.8 on TSLA (chance 33) | most of the accuracy lives in sub-spread moves | `tlob_berti2025.pdf` |
| Eurodollar (CME): Sharpe negative at 0.06 bp cost, spread 0.5 bp | survives 12% of the spread | `eurodollar_sizing2020.pdf` |
| ES (CME): outperformance only "With perfect information, and 0ms latency" on 90 minutes | no realistic test | `dixon_execution2017.pdf` |

Why accuracy misleads, in one line each: (a) accuracy and F1 weight every sample equally, but money is made on
the few moves larger than costs; (b) labels set for class balance put the "up" boundary below the cost (Section
6.1); (c) consecutive samples overlap, so accuracy over millions of samples overstates the number of
independent bets; (d) a correct direction call at event t is worth nothing if the order cannot be placed before
the move (Section 9); (e) Briola et al.'s point: errors that break a position's sequence (a premature close)
matter more than their count, "we are more interested in the chronological location of prediction errors rather
than in the number of their occurrence".

## 9. What survives retail latency

**The latency gap.** The program's orders travel Vancouver to CME Aurora in tens of milliseconds (READER_RULES,
program context), plus the TopstepX platform's own handling time (not measured in any source I read).
Co-located professionals: Lucchese et al. cite "tick-to-trade latency ... of the order of a couple of
microseconds" for FPGA systems and "a couple of hundred microseconds" with deep models; Dixon puts colocated CME
latency "in the range of 100 micro-seconds to 1ms". With 10 to 100 ms against 0.2 to 1 ms, tens of milliseconds is therefore 10 to 500 times slower than
a colocated deep-model trader and about 10,000 times slower than an FPGA trader.

**The predictability horizon.** Predictability is found "up to 50 order book events ahead" (Lucchese), decays from
the next event to 1 s on ES (Dixon), peaks at about two price changes for deep order-flow models (Kolm et al.,
[unverified]), and DeepLOB's accuracy falls from 70% to 62% between k = 20 and k = 100 events (about 4 s and 19 s
on LSE). So most of the documented signal lives in horizons that a tens-of-milliseconds trader reaches late, and
the part that remains at 10 to 60 s is weaker and has not been shown to beat costs.

**Model inference is not the bottleneck.** Measured on this laptop: 0.87 to 1.27 ms median for one sample on the
RTX 3050 and 0.65 to 2.06 ms on CPU (Section 10), small against the network delay.

**What could survive.** (1) Signals used to decide whether to keep a resting order in the queue, or where to
place it, at horizons of 10 to 60 s, where the decision tolerates tens of milliseconds; that is the pilot's
markout question, and Dixon's framing. (2) Not: aggressive entries on sub-second direction calls. **Evidence on
latency-degraded performance of these models: none found** (one targeted search and the papers' own text;
Lucchese et al. list it as future work). A gap, not a finding.

## 10. Training compute: the RTX 3050 4 GB versus a cloud GPU

### 10.1 Measured on this laptop (synthetic data)

`work/C2_DeepLOB/C2_gpu_probe.out`, RTX 3050 4GB Laptop GPU, PyTorch 2.14.0+cu130, 4 CPU threads, nice 10:

| Model | Params | GPU train, batch 32 | GPU train, batch 256 | CPU train, batch 32 | 1-sample inference, GPU / CPU (median, p99) |
|---|---|---|---|---|---|
| DeepLOB, paper (16 ch, no BN) | 60,947 | 4,602 samples/s, 94 MiB | 5,247 samples/s, 577 MiB | 844 samples/s | 0.87/1.15 ms; 1.24/1.66 ms |
| DeepLOB, PyTorch common (32 ch, BN, Inception 64) | 143,907 | 2,036, 181 MiB | 2,092, 1,258 MiB | 330 | 1.23/1.27; 2.06/2.16 |
| TransLOB-like | 101,940 | 5,598, 43 MiB | 7,725, 214 MiB | 1,940 | 1.27/2.06; 0.65/1.14 |

The parameter counts agree with the literature: LOBCAST lists DeepLOB at 1.4 x 10^5 and TransLOB at 1.1 x 10^5,
so LOBCAST evaluated the 32-channel PyTorch variant, not the paper's 60k model. All three use under a third of
the 4 GB card at batch 256. Memory is not a constraint; time is.

### 10.2 Training time for one configuration (scenarios; samples per day is a guess until the pilot counts
events)

Samples per epoch = samples per day x training days. Time per epoch = samples / throughput (batch 256 numbers).
40 epochs, as DeepLOB used on the LSE data:

| Model | 50k samples/day x 80 days (4.0M) | 200k samples/day x 80 days (16M) |
|---|---|---|
| DeepLOB paper | 0.21 h/epoch, 8.5 h | 0.85 h/epoch, 33.9 h |
| DeepLOB PyTorch 32-ch | 0.53 h/epoch, 21.2 h | 2.12 h/epoch, 85.0 h |
| TransLOB-like | 0.14 h/epoch, 5.8 h | 0.58 h/epoch, 23.0 h |

Reference points: DeepLOB-Attention costs about 2.8 times DeepLOB per epoch (Section 3.2); Briola et al. averaged
about 7.1 GPU-hours per DeepLOB experiment on cluster GPUs; LOBCAST used 155 + 258 hours on 8 GPUs. Data in RAM:
a day of 200k rows x 40 float32 features is 32 MB; 80 days is 2.6 GB if materialised as rows (the 100-row windows
should be indexed, not copied: copying would multiply this by 100).

### 10.3 Cloud prices (pages fetched 2026-10-21)

RunPod (`runpod_pricing.html`, fetched 09:29 UTC, 02:29 PDT; the page has "Community Cloud" and "Secure Cloud" tabs and
the static HTML does not say which tab these figures belong to): "RTX 4090|24 GB VRAM|41 GB RAM|6|vCPUs|$|0.89|/hr",
"A100 PCIe|80 GB VRAM|117 GB RAM|8|vCPUs|$|1.79|/hr", "RTX 3090|24 GB VRAM|125 GB RAM|16|vCPUs|$|0.5|/hr",
"RTX A5000|24 GB VRAM|25 GB RAM|9|vCPUs|$|0.27|/hr" (field separators are mine, from the page's text nodes).
Lambda (`lambda_pricing.html`): "NVIDIA A100 SXM|40 GB|...|$1.99", "NVIDIA H100 SXM|80 GB|...|$3.99", "NVIDIA
Tesla V100|16 GB|...|$0.79", per GPU-hour, "* plus applicable sales tax/VAT/GST".

Cost of the same work: 18 GPU-hours costs $16 on a RunPod RTX 4090 and $32 on a RunPod A100; 100 GPU-hours $89
and $179; 500 GPU-hours $445 and $895 (Lambda A100 40 GB: $36, $199, $995). Speed-ups over the RTX 3050 for these
small models were not measured: small CNN-LSTMs are limited by the sequential LSTM and kernel-launch overhead, so
a large GPU may give much less than its nominal advantage. Treat any assumed speed-up as a guess until a one-epoch
probe is run on the rented card.

**Recommendation for this program.** One configuration of DeepLOB or a TransLOB-like model trains overnight on the
laptop. The real cost is the number of configurations times seeds: 10 configurations x 5 seeds x 20 h = 1,000
GPU-hours, about 6 weeks of laptop time or about $900 to $1,800 of rented GPU time. That number, not the
hardware, should drive how many configurations a pre-registration allows.

## 11. From the pilot to pre-registerable hypotheses: summary and trial-count cost

The pilot (one contract, about 4 months, one Databento schema) measures fill rates, queue times and 1/10/60 s
markouts of a 1-lot passive order. Deep models enter only as classifiers that condition those quantities. All
hypotheses below share one design: time-ordered train / validation / test blocks with purge and embargo of the
label horizon; one-shot test; statistic = difference in mean markout (ticks) between model-favoured and
model-disfavoured fills, day-clustered or Newey-West t > 3.0; the favoured group's mean markout must also exceed
the 0.976-tick fee. Sample per group ~ 2 (3.0 + 0.84)^2 sigma^2 / delta^2 (473 fills per group for sigma = 2
ticks and delta = 0.5 tick; 1,890 for delta = 0.25), times a design effect for within-day dependence that the
pilot must estimate.

| ID | Classifier or variable | Data needed | Confirmatory configurations if pre-registered minimally | Notes |
|---|---|---|---|---|
| H-C2-Base-1 | logistic regression and MLP on top-of-book imbalance and recent order flow | mbp-10 (or mbp-1) | +2 | must be run; deep models are judged against these |
| H-C2-Dixon-1 | adverse-flip classifier inside the trade information matrix | mbp-10; mbo for queue position | +1 | closest published design |
| H-C2-DeepLOB-1 | DeepLOB (paper, 60k params) | mbp-10 | +1 (10 s), +2 more if 1 s and 60 s tested | |
| H-C2-Attn-1 | DeepLOB-Attention, joint 1/10/60 s | mbp-10 | +1 primary | only if DeepLOB passes |
| H-C2-TLOB-1 | MLPLOB with spread-plus-fee threshold | mbp-10 | +1 | TLOB itself adds +1 |
| H-C2-HLOB-1 | HLOB | mbp-10 | +1 plus fixed bin count | complexity cost |
| H-C2-MBO-1 | queue position at placement (no deep model) | mbo | +1 | cheapest, interpretable |

Every tuned choice (threshold, horizon, look-back, learning rate, seeds kept, early-stopping rule) that is not
fixed in advance adds its tried values to N. A minimal deep-learning block (two baselines plus DeepLOB at one
horizon) costs +3; a typical published search (3 horizons x 3 thresholds x 2 look-backs x 5 seeds, picking the
best) would cost 90.

Which schema: mbp-10 is enough for every classifier above except H-C2-MBO-1 and an exact queue-position fill
model, which need mbo. tbbo supports none of the deep models (top of book at trades only). Choosing the schema is
the lead's decision; this section only states what each test requires.

## 12. Verdicts (use / maybe / skip for this program)

| Method | Verdict | Reason |
|---|---|---|
| DeepLOB | maybe | Fits the data (mbp-10) and the laptop (60k params, 8 to 34 h per configuration); worth one pre-registered test as an adverse-selection filter after simple baselines. Not as a stand-alone direction strategy: no cost-inclusive evidence anywhere, thresholds below one MES tick. |
| FI-2010 | skip | Normalised, 2010, 10 days, cannot be backtested; zero weight in any decision. |
| TransLOB | skip | Its headline result did not reproduce (LOBCAST: 59.4 against a claimed 87.3). |
| DeepLOB-Seq2Seq / DeepLOB-Attention | skip (maybe later) | No material gain over DeepLOB on LSE (F1 68.09 vs 68.40 at k = 20), 2.8x the training cost; multi-horizon output only matters if DeepLOB passes first. |
| HLOB | skip | Complex, mixed results even in-sample, extra researcher choices; keep its finding that large-tick books are more predictable as a prior for MES. |
| TLOB | skip | 10^7-scale parameters; with a spread threshold its F1 falls toward chance. |
| MLPLOB / MLP baseline | use (as baseline) | Matches or beats deep models in three independent studies; cheap. |
| BiN-CTABL | maybe (as small baseline) | Most robust in LOBCAST, 1.1 x 10^4 params; known here only through LOBCAST [paper not fetched]. |
| Deep models on MBO | skip (model); the mbo data's queue position: use if a fill model is needed | MBO-only models were about 6.6 F1 points worse than DeepLOB; ensemble +0.6. |
| LOBCAST protocol (seeds, reproduce-before-trust) | use | Directly prevents the failure it documents. |
| Briola et al. transaction metric pT and one-tick label | use | A transaction-level primary metric and a tick-based threshold suit a pre-registration. |
| Lucchese et al. model confidence sets | maybe | Sound way to compare several models against no-skill; overlaps the program's Holm/DSR tools. |
| Dixon trade information matrix (CME ES) | use | The only published framework linking a classifier's confusion matrix to P&L under fill probabilities; maps onto the pilot. |
| Eurodollar uncertainty sizing | skip | Edge dies at 12% of the spread; sizing is irrelevant for a fixed 1-lot. |
| Sirignano-Cont universal model | skip | Supercomputer-scale; its pooling lesson argues against judging deep models on one contract. |

Overall: the deep-model literature gives no evidence that any of these models earns money after costs at retail
latency on any market, and gives direct evidence (Eurodollar, TLOB spread threshold, Briola pT, LOBCAST) that
accuracy overstates value. The defensible use in this program is narrow: a small classifier, judged against
simple baselines, as a filter on the passive-order markouts the pilot measures.

## 13. References (all fetched in full unless marked)

Files are under `reports/stage_e28_briefs/pages/C2_DeepLOB/`; sha256 and fetch times in `log.tsv`.

1. Zhang, Z., Zohren, S., Roberts, S. (2019). DeepLOB: Deep convolutional neural networks for limit order books.
   IEEE Transactions on Signal Processing 67(11). arXiv 1808.03668v6. `deeplob_zhang2019.pdf`
2. Ntakaris, A., Magris, M., Kanniainen, J., Gabbouj, M., Iosifidis, A. (2018). Benchmark dataset for mid-price
   forecasting of limit order book data with machine learning methods. Journal of Forecasting 37(8). arXiv
   1705.03233. `fi2010_ntakaris2018.pdf`
3. Wallbridge, J. (2020). Transformers for limit order books. arXiv 2003.00130. `translob_wallbridge2020.pdf`
4. Zhang, Z., Zohren, S. (2021). Multi-horizon forecasting for limit order books: novel deep learning
   approaches and hardware acceleration using intelligent processing units. arXiv 2105.10430.
   `zhang_zohren_multihorizon2021.pdf`
5. Briola, A., Bartolucci, S., Aste, T. (2024). HLOB: information persistence and structure in limit order
   books. arXiv 2405.18938v3. `hlob_briola2024.pdf`
6. Berti, L., Kasneci, G. (2025). TLOB: a novel transformer model with dual attention for price trend
   prediction with limit order book data. arXiv 2502.15757v3. `tlob_berti2025.pdf`
7. Zhang, Z., Lim, B., Zohren, S. (2021). Deep learning for market by order data. arXiv 2102.08811.
   `mbo_zhang2021.pdf`
8. Prata, M., Masi, G., Berti, L., Arrigoni, V., Coletta, A., Cannistraci, I., Vyetrenko, S., Velardi, P.,
   Bartolini, N. (2024). LOB-based deep learning models for stock price trend prediction: a benchmark study.
   arXiv 2308.01915v2. `lobcast_prata2024.pdf`
9. Briola, A., Turiel, J., Aste, T. (2020). Deep learning modeling of limit order book: a comparative
   perspective. arXiv 2007.07319v3. `briola_turiel_aste2020_comparative.pdf`
10. Briola, A., Bartolucci, S., Aste, T. (2024). Deep limit order book forecasting: a microstructural guide.
    arXiv 2403.09267v4; Quantitative Finance 2025, DOI 10.1080/14697688.2025.2522911 [journal details
    unverified, from a search snippet]. `briola_microstructural_guide2024.pdf`
11. Lucchese, L., Pakkanen, M. S., Veraart, A. E. D. (2024). The short-term predictability of returns in order
    book markets: a deep learning perspective. arXiv 2211.13777v3. `lucchese2024_predictability.pdf`
12. Sirignano, J., Cont, R. (2019). Universal features of price formation in financial markets: perspectives
    from deep learning. arXiv 1803.06917. `sirignano_cont2019.pdf`
13. Spears, T., Zohren, S., Roberts, S. (2020). Investment sizing with deep learning prediction uncertainties
    for high-frequency Eurodollar futures trading. arXiv 2007.15982. `eurodollar_sizing2020.pdf`
14. Dixon, M. (2017). Sequence classification of the limit order book using recurrent neural networks. arXiv
    1707.05642. `dixon_rnn_seq2017.pdf`
15. Dixon, M. (2017). A high frequency trade execution model for supervised learning. arXiv 1710.03870.
    `dixon_execution2017.pdf`
16. Anonymous authors as listed in arXiv 2501.08822 (2025). Deep learning meets queue-reactive: a framework for
    realistic limit order book simulation. `dlqr_bund2025.pdf` (author names not extracted)
17. Wang, H. (2025). Exploring microstructural dynamics in cryptocurrency limit order books: better inputs
    matter more than stacking another hidden layer. arXiv 2506.05764v2. `crypto_inputs2025.pdf`
18. Briola, A., Turiel, J., Marcaccioli, R., Aste, T. (2021). Deep reinforcement learning for active high
    frequency trading. arXiv 2101.07107. `briola_drl_hft2021.pdf` (read; used only for background: one-unit
    INTC agent that pays the spread; not cited for a result)
19. Makinde, A. (2026). Temporal Kolmogorov-Arnold networks (T-KAN) for high-frequency limit order book
    forecasting. BILT Student Research Journal (7); arXiv 2601.02310. `tkan_alphadecay2026.pdf`
20. Kolm, P. N., Turiel, J., Westray, N. (2023). Deep order flow imbalance: extracting alpha at multiple
    horizons from the limit order book. Mathematical Finance 33(4), 1044-1081. [unverified: full text not
    fetched, paywall; bibliographic data from a search result]
21. Tsantekidis, A. et al. (2018). Using deep learning for price prediction by exploiting stationary limit order
    book features. arXiv 1810.09965. `tsantekidis_stationary2018.pdf` (fetched; not used)
22. Arnaboldi, L., Sokolovsky, A. (2022). A generic methodology for the statistically uniform and comparable
    evaluation of automated trading platform components. arXiv 2009.09993v4. `spy_lob_negative2020.pdf`
    (fetched by mistake for a different paper; not used; file name is misleading)
23. Databento documentation: MBP-10, TBBO and MBO schema pages. `databento_schema_mbp-10.html`,
    `databento_schema_tbbo.html`, `databento_schema_mbo.html`
24. RunPod GPU pricing page, `runpod_pricing.html`; Lambda GPU pricing page, `lambda_pricing.html`
    (both fetched 2026-10-21 09:29 UTC)
25. Repo-internal (not new evidence): `sim/costs.py`, MES round-turn $1.22 on TopstepX, flagged there as
    needing reconfirmation.

Search log (7 WebSearch calls of 60): (1) DeepLOB on CME E-mini futures; (2) Kolm-Turiel-Westray deep OFI PDF;
(3) deep LOB on Chinese commodity futures with costs; (4) LOB deep learning with transaction costs, negative
results; (5) latency robustness of LOB deep forecasts; (6) E-mini order-book ML cost-inclusive studies;
(7) order-book predictability decline over years. Null results: no DeepLOB-family test on CME equity-index
futures with costs (1, 6), no latency-degradation study (5), no year-by-year decay study on futures (7).
Discovery otherwise by the arXiv API (export.arxiv.org). No throttling or blocks except the Wiley paywall.

## 14. Evidence table

| # | Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|---|
| 1 | DeepLOB combines CNNs and LSTMs on raw book data | Zhang et al. 2019 | "The architecture utilises convolutional filters to capture the spatial structure of the limit order books as well as LSTM modules to capture longer time dependencies." | deeplob_zhang2019.pdf |
| 2 | DeepLOB labels: threshold alpha on smoothed percentage change | Zhang et al. 2019 | "If lt > α or lt < −α, we define it as up (+1) or down (−1). For anything else, we consider it as stationary (0)." | deeplob_zhang2019.pdf |
| 3 | DeepLOB normalises with the previous 5 days | Zhang et al. 2019 | "use the mean and standard deviation of the previous 5 days’ data to normalise the current day’s data (with a separate normalisation [two-column text interleaved here in the PDF extraction] for each instrument)" | deeplob_zhang2019.pdf |
| 4 | DeepLOB has about 60k parameters | Zhang et al. 2019 | "We use 64 LSTM units in our work, resulting in about 60,000 parameters" | deeplob_zhang2019.pdf |
| 5 | DeepLOB LSE data scale and split | Zhang et al. 2019 | "our LSE dataset is made up of 12 months, and has more than 134 million samples. On average, there are 150,000 events per day per stock." | deeplob_zhang2019.pdf |
| 6 | DeepLOB's trading test excludes costs | Zhang et al. 2019 | "we assume trading takes place at mid-price2 and compare gross profits before fees" | deeplob_zhang2019.pdf |
| 7 | FI-2010 scope | Ntakaris et al. 2018 | "five stocks from the NASDAQ Nordic stock market for a time period of ten consecutive days, leading to a dataset of ≈4,000,000 time series samples in total" | fi2010_ntakaris2018.pdf |
| 8 | FI-2010 threshold 0.002 | Ntakaris et al. 2018 | "For percentage changes equal to or greater than 0.002, we use label 1." | fi2010_ntakaris2018.pdf |
| 9 | FI-2010 cannot be backtracked to prices | Prata et al. 2024 | "already pre-processed (filtered, normalized, and labelled) so that the original LOB cannot be backtracked, thus hampering thorough experimentation" | lobcast_prata2024.pdf |
| 10 | FI-2010 theta chosen for balance, not finance | Prata et al. 2024 | "θ is not chosen in accordance with its financial implication but rather serves the purpose of balancing the dataset" | lobcast_prata2024.pdf |
| 11 | All benchmarked models drop on new data | Prata et al. 2024 | "all models exhibit a significant performance drop when exposed to new data, thereby raising questions about their real-world market applicability" | lobcast_prata2024.pdf |
| 12 | Models diverge in half of hyperparameter runs | Prata et al. 2024 | "they diverged (F1-score ⩽ 33%) during the hyperparameters search for about half of the runs" | lobcast_prata2024.pdf |
| 13 | LOBCAST backtest assumed no fees; profit tracked drift | Prata et al. 2024 | "the two stocks with the highest positive daily returns (namely LSTR and NFLX) are the only ones for which the strategy is profitable" | lobcast_prata2024.pdf |
| 14 | TransLOB and ATNBoF reproduced worst | Prata et al. 2024 | "Among the models, TRANSLOB and ATNBOF exhibit the largest discrepancies, ranking as the second and first worst performers" | lobcast_prata2024.pdf |
| 15 | LOBCAST training compute | Prata et al. 2024 | "approximately 155 hours for FI-2010 and 258 hours for LOB-2021/2022, utilizing a cluster comprised of 8 GPUs" | lobcast_prata2024.pdf |
| 16 | TransLOB architecture | Wallbridge 2020 | "This architecture uses a causal convolutional network for feature extraction in combination with masked self-attention" | translob_wallbridge2020.pdf |
| 17 | Attention models trained 200 epochs; per-epoch times | Zhang and Zohren 2021 | "The model training lasts for 200 epochs" (Table 10: DeepLOB 96 s, DeepLOB-Attention 270 s per epoch, RTX 2080) | zhang_zohren_multihorizon2021.pdf |
| 18 | LSE thresholds chosen for balance | Zhang and Zohren 2021 | "The label parameter (α) is chosen for each instrument to have a balanced training set" | zhang_zohren_multihorizon2021.pdf |
| 19 | High forecasting power is not actionable | Briola et al. 2024 | "their high forecasting power does not necessarily correspond to actionable trading signals" | briola_microstructural_guide2024.pdf |
| 20 | Historical backtests need impossible assumptions | Briola et al. 2024 | "backtesting a trading strategy based on the outputs of a deep learning model by using historical data-only is not possible" | briola_microstructural_guide2024.pdf |
| 21 | Large-tick pT about 0.10 | Briola et al. 2024 | "the average pT value for this class of stocks equals 0.10, with a smoother decrease for higher threshold values" | briola_microstructural_guide2024.pdf |
| 22 | Briola et al. compute | Briola et al. 2024 | "A total number of 135 experiments have been run ... for a cumulative GPU runtime of 959 hours, 16 minutes and 27 seconds" | briola_microstructural_guide2024.pdf |
| 23 | MLP matches CNN-LSTM | Briola, Turiel, Aste 2020 | "the Multilayer Perceptron performs comparably to or better than state-of-the-art CNN-LSTM architectures" | briola_turiel_aste2020_comparative.pdf |
| 24 | HLOB best in few small-tick cases | Briola et al. 2024 (HLOB) | "For small-tick stocks, HLOB is the best-performing model in 1/6 scenarios" | hlob_briola2024.pdf |
| 25 | Simple MLP beats SoTA | Berti and Kasneci 2025 | "by adapting a simple MLP-based architecture to LOB, we show that we surpass SoTA performance" | tlob_berti2025.pdf |
| 26 | Spread-based threshold kills Intel labels | Berti and Kasneci 2025 | "would result in 99.99% of trends classified as stationary" | tlob_berti2025.pdf |
| 27 | TLOB decay evidence is one day vs one day | Berti and Kasneci 2025 | "we tested on a day of Intel from 2012/06/21[footnote marker 10 removed] and confronted the difference in performance with 2015/01/30" | tlob_berti2025.pdf |
| 28 | MBO and LOB similar; ensemble helps | Zhang, Lim, Zohren 2021 | "while MBO-driven and LOB-driven models individually provide similar performance, ensembles of the two can lead to improvements in forecasting accuracy" | mbo_zhang2021.pdf |
| 29 | Predictability up to 50 events | Lucchese et al. 2024 | "we were able to identify predictability up to 50 order book events ahead at the 99% confidence level" | lucchese2024_predictability.pdf |
| 30 | Co-located tick-to-trade in microseconds | Lucchese et al. 2024 | "tick-to-trade latency ... to be of the order of a couple of microseconds (µs)" | lucchese2024_predictability.pdf |
| 31 | Universal model stable over time | Sirignano and Cont 2019 | "The universal price formation model exhibits a remarkably stable out-of-sample prediction accuracy across time" | sirignano_cont2019.pdf |
| 32 | Eurodollar costs analysed far below the spread | Spears et al. 2020 | "the transaction costs analysed here are significantly less than the median daily bid-ask spread of 0.5bps" | eurodollar_sizing2020.pdf |
| 33 | Eurodollar data are CME Level 1, 2018 | Spears et al. 2020 | "This data reflects Level 1 limit order book best bid-ask-volume quotes" | eurodollar_sizing2020.pdf |
| 34 | ES backtest assumed perfect information and zero latency | Dixon 2017b | "With perfect information, and 0ms latency, strategy M M 2 is shown to outperform strategy M M 1." | dixon_execution2017.pdf |
| 35 | ES RNN decays within 1 s | Dixon 2017a | "the performance of the RNN decays as we increase the prediction horizon from the next book update event to 1s in the future" | dixon_rnn_seq2017.pdf |
| 36 | ES F1 decays within the month without retraining | Dixon 2017a | "The F1 scores are observed to exhibit a secular decay when the model is not re-trained on a daily basis" | dixon_rnn_seq2017.pdf |
| 37 | Bund DeepLOB balanced accuracy 0.54 | arXiv 2501.08822 | "the DeepLOB architecture ... achieves a baseline performance with balanced accuracy of 0.54" | dlqr_bund2025.pdf |
| 38 | mbp-10 content | Databento docs | "MBP-10 (market by price) provides every order book event across the top ten price levels, keyed by price." | databento_schema_mbp-10.html |
| 39 | tbbo content | Databento docs | "BBO on trade (TBBO) provides every trade event alongside the BBO immediately before the effect of each trade." | databento_schema_tbbo.html |
| 40 | mbo gives queue position | Databento docs | "This allows you to determine the queue position of each order and provides the highest level of granularity available." | databento_schema_mbo.html |
| 41 | Cloud price, RunPod RTX 4090 and A100 | RunPod pricing page | "RTX 4090|24 GB VRAM|41 GB RAM|6|vCPUs|$|0.89|/hr"; "A100 PCIe|80 GB VRAM|117 GB RAM|8|vCPUs|$|1.79|/hr" (separators mine) | runpod_pricing.html |
| 42 | Cloud price, Lambda A100 40 GB | Lambda pricing page | "NVIDIA A100 SXM|40 GB|124|1800 GiB|5.8 TiB SSD|$1.99" (separators mine) | lambda_pricing.html |
| 43 | FI-2010 cost-inclusive return claim | Makinde 2026 | "producing a 132.48% return compared to the -82.76% DeepLOB drawdown under 1.0 bps transaction costs" (not credible as money: FI-2010 prices are normalised) | tkan_alphadecay2026.pdf |
| 44 | Kolm et al. accuracy peak at two price changes | Quantpedia summary via search snippet | [unverified: search snippet only] | none |

Measured (this worker, synthetic data): parameter counts, GPU memory, throughput and latency in Section 10.1,
`work/C2_DeepLOB/C2_gpu_probe.out`. Computed: all worked examples, `work/C2_DeepLOB/C2_worked_examples.out`.

## Corrections after review (Stage E.28, MathReviewer G5)

- MG5-01 (BLOCKING): problem 5 of Section 2.3 rewritten. DeepLOB Table II (Setup 2) uses k = 10, 20, 50 and Table I (Setup 1) uses k = 10, 50, 100; the claimed cross-paper inconsistency is removed. Section 1.6 now says "at k = 20 and 50".
- MG5-02 (SHOULD FIX): worked example 1.5 now states that the script's second line uses five mids (0.745 bp) and that its "m- printed" line is not a price; class labels unchanged. The script itself was not edited.
- MG5-03 (SHOULD FIX): LOBCAST score definition corrected: A is the average of (claimed F1 minus measured F1) over declared horizons and five seeds, S the standard deviation of those differences.
- MG5-04 (NOTE): TLOB parameter ratio changed to "about 150 to 1,000 times the paper's DeepLOB".
- MG5-05 (NOTE): Briola pT range unified at both places as "averages of 0.06 to 0.12 at H10 (large-tick 0.10)".
- MG5-06 (NOTE): latency ratio restated with the assumed figures, "10 to 500 times slower".
- MG5-07 (NOTE): added the clause reconciling the 105,347-parameter figure with the 60k paper model.
- MG5-08 (NOTE): added "[footnote marker 10 removed]" to the TLOB Intel quote in both body places.
