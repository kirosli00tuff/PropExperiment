# C2. Machine learning on order-book data, part 2: order-flow features and tree models

Stage E.28 methods brief, deep-dive section. Worker C2_OFI (Opus 5.5), written 2026-10-21 from 02:50 PDT.
Pages: `reports/stage_e28_briefs/pages/C2_OFI/` (log: `log.tsv`). Scripts: `reports/stage_e28_briefs/work/C2_OFI/`
(worked-example arithmetic: `C2_OFI_examples.py`, output `C2_OFI_examples.out`).

## 0. Scope, sources and how to read this section

**What this covers.** Order-flow imbalance (OFI) and its extensions (multi-level, integrated, cross-asset, deep),
queue imbalance and trade-flow features, gradient-boosted trees on those features, and the evaluation questions that
decide whether any of it is tradable for this program: contemporaneous versus predictive R-squared, label design,
how fast predictive power decays with horizon and latency, latency races and sniping, post-publication evidence, and
what exists on futures. Part 1 (C2_DeepLOB.md) covers the deep models (DeepLOB, TransLOB, LOBCAST and so on); the
microprice is in C2_LOB.md section 5. This section cross-references them and does not repeat them.

**Sources.** 22 documents fetched and saved (full-text PDFs from arXiv, NBER, Oxford ORA, NeurIPS, a Cornell copy of
Stoikov and Waeber; two cloud price pages; two Databento schema pages; one library documentation page). Every
quoted line below was read from the saved file with grep or line ranges. One key paper could not be fetched in full:
Kolm, Turiel and Westray (2023), "Deep order flow imbalance" (Mathematical Finance 33(4), paywalled; SSRN blocks this
machine; the Wiley page returned a Cloudflare challenge). Its abstract was read on IDEAS/RePEc, and its method is
described from two later papers that reimplemented it (Lucchese, Pakkanen and Veraart 2024; Jaddu and Bilokon
2023). Everything about Kolm et al. that is not in those three texts is marked [unverified].

**Notation used throughout.** Tick = minimum price increment. For MES the tick is 0.25 index points and worth
$1.25; for ES it is 0.25 points and $12.50 (rules/products.py lines 153-154). "Mid" = (best bid + best ask)/2.
"Markout at h" of a fill = the mid at fill time + h minus the fill price, signed so that positive is good for the
filled order, in ticks.

### 0.1 The cost hurdle that every method in this section must clear

All numbers from rules/products.py (MES: tick value $1.25, round-turn commission and fees 122 cents; ES: $12.50,
378 cents). Computed in `C2_OFI_examples.py` section 3.

| Contract | Fees per round turn, in ticks | Taker round turn (cross a 1-tick spread once, plus fees) | Maker round turn (both legs passive, no adverse move), net |
|---|---|---|---|
| MES | 1.22 / 1.25 = 0.976 ticks | 1 + 0.976 = 1.976 ticks = $2.47 | 1 - 0.976 = 0.024 ticks = $0.03 |
| ES | 3.78 / 12.50 = 0.302 ticks | 1.302 ticks = $16.28 | 0.698 ticks = $8.72 |

Two consequences shape every verdict below.

1. A **taker** strategy driven by an order-flow forecast needs the expected favourable mid move over its holding
   period to exceed about 2 ticks on MES (1.3 ticks on ES). The papers below report predictability over horizons of
   a few book events or seconds, where typical mid moves are a fraction of a tick to about a tick. The arithmetic is
   in section 7.4.
2. A **maker** strategy on MES keeps at most 0.024 ticks per round turn before adverse selection. On MES the
   only realistic use of an order-flow signal is to *avoid bad fills* (cancel or not post when the signal says the
   queue is about to be run over), not to earn the spread. ES has a 0.70-tick fee-adjusted spread, so the
   question is less hopeless there. (ES and MES are both marked `admissible=False` in rules/products.py; that
   flag is the program's, and this section does not reopen it.)

---

## 1. Order-flow imbalance (Cont, Kukanov and Stoikov 2014)

Source: Cont, R., Kukanov, A. and Stoikov, S. (2014), "The price impact of order book events", Journal of Financial
Econometrics 12(1). Read from arXiv 1011.6402v3 (`cks2014_price_impact.pdf/.txt`). The arXiv text shows equations
(1) to (5); numbers below follow it.

### 1.1 Core idea in plain words

Over a short interval, count how much was added to the bid side of the best quotes minus how much was removed, and
the same for the ask side with the sign flipped. Market sells, bid cancellations and bid price drops all lower
"demand"; limit bids and bid price rises raise it; the ask side is the mirror. The net number, OFI, is a
supply/demand imbalance measured in contracts. The paper's finding is that the mid-price change over the same
interval is close to linear in OFI, and that the slope is inversely proportional to the depth at the best quotes.
The paper says it plainly: the variable "treats a market sell and a cancel buy of the same size as equivalent, since
they have the same effect on the size of the bid queue. We find that this aggregate variable explains mid-price
changes over short time scales in a linear fashion, for a large sample of stocks, with an average R2 of 65%."

This is a **contemporaneous** (explanatory) relation: OFI over [t_{k-1}, t_k] explains the price change over the same
[t_{k-1}, t_k]. It is not a forecast. Section 7 shows why this distinction is the whole question for trading.

### 1.2 Equations, every term explained

**Event contribution.** Observe the best bid price P^B_n, bid size q^B_n, best ask P^A_n and ask size q^A_n after the
n-th change in the best quotes. The contribution of event n is (CKS, unnumbered equation in section 2.1):

    e_n = 1{P^B_n >= P^B_{n-1}} q^B_n  -  1{P^B_n <= P^B_{n-1}} q^B_{n-1}
          - 1{P^A_n <= P^A_{n-1}} q^A_n  +  1{P^A_n >= P^A_{n-1}} q^A_{n-1}

where 1{.} is 1 if the condition holds and 0 otherwise. Reading the bid half case by case (the paper's own words):
"if q^B increases but P^B remains the same, we assign e_n = q^B_n - q^B_{n-1}, representing the size that was added
at the bid. If q^B decreases, we also assign e_n = q^B_n - q^B_{n-1} ... If P^B increases, we let e_n = q^B_n,
representing the size of a price-improving limit order. If P^B decreases, we let e_n = q^B_{n-1}, representing the
size that was removed" (sub- and superscripts restored from the PDF extraction). The ask half is the same with signs reversed.

**OFI over an interval.** With N(t) the number of events up to time t:

    OFI_k = sum_{n = N(t_{k-1})+1}^{N(t_k)} e_n

**Price change in ticks.** ΔP_k = (P_k - P_{k-1}) / δ, where P_k is the mid at t_k and δ the tick size.

**Stylized model and its derivation (CKS eq. 1).** Assumptions: (i) every price level beyond the best quotes holds
exactly D shares; (ii) limit orders and cancellations arrive only at the best quotes. Then removing D shares from the
bid moves the bid down one tick, so the bid change is ΔP^b = ceil[(L^b - C^b - M^s)/D] ticks, where L^b is limit
buy volume, C^b bid cancellations, M^s market sells; the ask is ΔP^a = -ceil[(L^s - C^s - M^b)/D]. Averaging the
two for the mid and dropping the rounding gives

    ΔP = OFI / (2D) + ε,    OFI = L^b - C^b - M^s - L^s + C^s + M^b          (CKS eq. 1)

with ε the truncation error. So in this toy world the impact coefficient is exactly 1/(2D).

**Empirical model (CKS eqs. 2-4).**

    ΔP_k = β_i OFI_k + ε_k                                              (eq. 2)
    β_i = c / AD_i^λ + ν_i                                             (eq. 3)
    AD_i = [1 / (2(N(T_i) - N(T_{i-1}) - 1))] sum_n (q^B_n + q^A_n)     (average depth in half-hour i)

β_i is the price-impact coefficient in half-hour window i, ε_k noise "due to the influence of deeper levels of the
order book and rounding errors", c and λ constants, ν_i noise. "Note that the stylized model exposed above
corresponds to λ = 1." Estimation: OLS of ΔP_k on OFI_k (with intercept α_i, eq. 4) on 10-second intervals within
each half hour; then log β̂_i = α_L - λ log AD_i + error (eq. 5) across half hours.

### 1.3 Data it needs; is one CME contract for 4 to 12 months enough?

It needs only best bid and ask prices and sizes at every change (level 1). CKS used NYSE TAQ consolidated quotes,
"one calendar month (April, 2010) of trades and quotes (TAQ) data for 50 stocks", and remark that "Level 1 TAQ data
can be successfully used to study limit orders". Databento's tbbo schema (trades with the BBO just before) is not
enough on its own, because OFI needs every quote change, not only quotes at trades. mbp-1 or mbp-10 is enough:
Databento's mbp-10 record carries `bid_px_N`, `ask_px_N`, `bid_sz_N`, `ask_sz_N` for levels 00 to 09 plus `action`,
`side` and two nanosecond timestamps (`databento_mbp10.html.txt`). Four months of one liquid contract gives far more
observations than CKS had per stock (they had 273 half-hour windows per stock). For estimating β and λ, one month
would do. For any predictive claim, sample size is governed by the much weaker predictive signal (section 7).

### 1.4 What it estimates or decides

It estimates the instantaneous price impact per contract of net order flow, and its dependence on depth. It decides
nothing by itself. Uses for this program: (a) a feature (lagged OFI) for a forecast; (b) a depth-scaled measure of
how much flow is needed to move the price one tick, which tells a passive order how fragile its queue is.

### 1.5 Worked example (toy MES numbers; `C2_OFI_examples.py` section 1)

Start: bid 5000.00 x 20, ask 5000.25 x 15. Four quote changes:

| Event | New state | Rule that applies | e_n |
|---|---|---|---|
| 1 | bid 5000.00 x 25 | bid price same, size up: q^B_n - q^B_{n-1} = 25 - 20 | +5 |
| 2 | ask 5000.25 x 10 | ask price same, size down: -(q^A_n - q^A_{n-1}) = -(10 - 15) | +5 |
| 3 | ask 5000.50 x 30 | ask price rose (queue of 10 consumed): +q^A_{n-1} = +10 | +10 |
| 4 | bid 5000.00 x 18 | bid price same, size down: 18 - 25 | -7 |

OFI = 5 + 5 + 10 - 7 = **+13 contracts**. The mid moved from 5000.125 to 5000.25, +0.5 tick. The stylized model
predicts ΔP = OFI/(2D): with D = 20 contracts per level, 13/40 = 0.325 tick; with D = 100, 0.065 tick. To get a full
1-tick move the model needs OFI = 2D contracts. As a real calibration point, Takahashi (2025) reports for ES
(2008-2013) a mean depth of 0.63 thousand contracts (Table 1, "∗∗∗ in the thousands"), so about 2 x 630 = 1,260
contracts of net flow per tick under the stylized model. MES depth is not quoted in any fetched source; the pilot
should measure it.

### 1.6 Published results

- R²: "the average R2 for order flow imbalance is 65% compared to 32% for the trade imbalance."
- Robustness to the obvious tautology (OFI includes price-changing events): excluding them, "the R2 declined, but
  remained in the 35%-60% region."
- Linearity: adding OFI_k|OFI_k| raised R² "from 65% to 68% on average", "barely noticeable".
- Depth scaling: "λ̂ are very close to 1 across stocks and the hypothesis {λ = 1} cannot be rejected for 35 out of
  50 stocks."
- Timescale: they repeat with Δt from 10 quote updates to 10 minutes; "The fit of our model generally increases with
  Δt, but the rest of the results stays the same."
- Trades add nothing once OFI is in: "Trades seem to carry little to no information about price changes after the
  simultaneous order flow imbalance is taken into account."

No prediction, no out-of-sample trading test, no costs: the paper does not claim any.

### 1.7 Turning the pilot into a pre-registerable hypothesis (candidate for the lead)

**H-OFI-1 (adverse selection of a passive fill).** For simulated 1-lot passive fills on the pilot contract, the
markout at 10 s is lower when the OFI over the 1 s before the fill was against the order (negative OFI for a resting
bid that got filled, positive for a resting ask) than when it was with the order.
- Statistic: slope b in markout_10s,j = a + b · s_j · OFI_j / AD_j + u_j, where s_j = +1 for a filled bid and -1 for
  a filled ask, OFI_j the 1-s OFI before fill j, AD_j the average depth of that half hour; t-statistic with
  Newey-West errors in fill-time order (fills cluster). Equivalent nonparametric check: difference in mean markout
  between the top and bottom terciles of s_j·OFI_j/AD_j.
- Sample: with markout standard deviation about 1 tick at 10 s [assumption, to be measured in the pilot] and a
  target difference of 0.2 tick between terciles, 393 fills per tercile (two-sided 5%, power 80%; section 7 of
  `C2_OFI_examples.out`), so about 1,200 fills, before inflating for clustering. A difference of 0.1 tick needs
  1,570 per tercile.
- Trial count: one configuration if the OFI window (1 s) and the markout horizon (10 s) are fixed in advance; three
  if all three markout horizons (1/10/60 s) are tested; nine if three OFI windows are also tried. Every one adds to
  N.
- Why it matters: it is a direct test of whether OFI can tell a passive order when to step out of the queue, which
  is the only use section 0.1 leaves open on MES.

### 1.8 Compute

Trivial. OFI is a running sum over book updates; one pass in Python with numpy (or polars) over tens of millions of
rows takes minutes on the laptop. Memory: about 88 million best-quote events for 84 RTH days at the ES event rate
(45 events per second, Takahashi 2025 Table 1; MES is likely lower [unverified]) is 3.5 GB as 10 float32 columns, so
process day by day. No GPU, no cloud.

### 1.9 Evidence at retail scale and latency

None in CKS: the result is contemporaneous. A trader who sees OFI_k only after interval k has already missed the
price change it explains. What survives as a forecast is the subject of sections 4, 7 and 9: in short, little, and
mostly within a second.

---

## 2. Multi-level OFI (Xu, Gould and Howison 2018)

Source: Xu, K., Gould, M. D. and Howison, S. D. (2018/2019), "Multi-level order-flow imbalance in a limit order book",
arXiv 1907.06230v2 (`xgh2018_mlofi.pdf/.txt`); published version recorded on Oxford ORA (`ora_9b7d0422.html`).

### 2.1 Core idea

CKS look only at the best bid and ask. Orders arrive, cancel and execute deeper in the book too, and that activity
also moves the price. MLOFI computes a separate OFI for each of the first M price levels and regresses the mid change
on all M of them. The finding: with ordinary least squares the extra levels look useless or unstable (the levels are
strongly correlated), but with ridge regression every extra level improves the out-of-sample fit.

### 2.2 Equations

Let b^m(τ_n) and a^m(τ_n) be the level-m bid and ask prices and r^m(τ_n), q^m(τ_n) the level-m bid and ask sizes
just after event n (XGH section 3.1). Then (XGH eqs. 9-12):

    ΔW^m(τ_n) = r^m(τ_n)                  if b^m(τ_n) > b^m(τ_{n-1})
              = r^m(τ_n) - r^m(τ_{n-1})    if b^m(τ_n) = b^m(τ_{n-1})
              = -r^m(τ_{n-1})              if b^m(τ_n) < b^m(τ_{n-1})          (eq. 9)
    ΔV^m(τ_n) = -q^m(τ_{n-1})              if a^m(τ_n) > a^m(τ_{n-1})
              = q^m(τ_n) - q^m(τ_{n-1})    if a^m(τ_n) = a^m(τ_{n-1})
              = q^m(τ_n)                   if a^m(τ_n) < a^m(τ_{n-1})          (eq. 10)
    MLOFI^m(t_{k-1}, t_k) = sum_{n: t_{k-1} < τ_n <= t_k} e^m(τ_n),  e^m = ΔW^m - ΔV^m      (eqs. 11-12)

"When M = 1, MLOFI and OFI are identical". The regression is ΔP_k = α + sum_m β_m MLOFI^m_k + ε_k (their eq. 16),
fit by ridge regression, which minimizes (XGH eq. 18)

    C(β, λ) = ||y - Xβ||²₂ + λ||β||²₂

where y is the vector of mid changes, X the matrix of MLOFI values, and λ >= 0 the penalty, chosen by 5-fold
cross-validation over "50 logaritmically-spaced candidate values of λ between 10^-5 and 10^5". Ridge shrinks
correlated coefficients towards each other instead of letting them blow up with opposite signs, which is why it
fixes the OLS instability.

### 2.3 Data; is one CME contract enough?

Needs M levels of prices and sizes at every book change. XGH used LOBSTER (Nasdaq) for six stocks, "each trading day
from 4 January 2016 to 30 December 2016", 30-minute windows split into 10-second intervals. Databento mbp-10 gives
M up to 10 for one CME contract and is sufficient; mbo would allow MBP depth beyond 10 ("It is possible to construct
MBP-10 yourself from MBO data if you want more price levels", Databento docs). One contract for 4 months gives about
84 days x 13 half-hour windows of RTH; XGH ran 2,772 regressions per stock (252 days x 11 windows; 16,632 over six stocks), so 1,092 windows from 4 months of
one contract is about 40% of one stock's sample and 7% of their total: enough for the contemporaneous fit, not much for cross-sectional claims.

### 2.4 What it estimates

The contemporaneous impact of flow at each level; the shape of β_m across m tells how much deeper-book activity
matters for the contract. Still contemporaneous.

### 2.5 Worked example

Using the same toy as 1.5 but with level 2: suppose during the interval 30 contracts are added at the second bid level
(4999.75) and 10 cancelled from the second ask level. Then MLOFI^1 = +13 (as
before), MLOFI^2 = +30 - (-10) = +40 if level-2 prices did not shift. With illustrative ridge coefficients β_1 =
0.02 and β_2 = 0.005 ticks per contract, the fitted ΔP = 0.02 x 13 + 0.005 x 40 = 0.26 + 0.20 = 0.46 tick: in this
toy the deeper level contributes almost half. (Coefficients invented for the arithmetic; the paper's per-stock values
are in its Tables 5 and 7, which this section did not transcribe.) One subtlety the definitions carry: when the best
ask is consumed (event 3), the old level-2 ask becomes level 1, so the "level m" bookkeeping shifts; MLOFI handles
it by comparing level-m prices before and after, exactly as eq. 10 does.

### 2.6 Published results

- "By analyzing the out-of-sample RMSE of the Ridge regression fits, we find that including net order flow deeper
  into the LOB improves the goodness-of-fit of the MLOFI regressions for all of the stocks in our sample, with an
  improvement of about 65–75% for large-tick stocks and about 15–30% for small-tick stocks."
- OLS was misleading: "we uncover evidence to suggest that the OLS regressions over-fit".
- MES and ES are large-tick contracts (one-tick spread almost always: Takahashi reports a mean ES spread of 0.25
  points with a 99th percentile of 0.30), so the large-tick result is the relevant one, but it is a stock result.

### 2.7 Pilot hypothesis

**H-MLOFI-1.** Same as H-OFI-1 with the 1-s OFI replaced by the ridge-weighted MLOFI combination, with the weights
frozen from a training block that precedes the test block. This adds the ridge λ choice (done inside training by
cross-validation, so not a separate trial if the grid is frozen) and one more configuration to N. It is better
framed as a comparison: "MLOFI explains markouts better than level-1 OFI" (statistic: difference in out-of-sample
R² of the two markout regressions, tested with a Diebold-Mariano test on squared errors). Adds 1 configuration.

### 2.8 Compute

Ten running sums instead of one, plus a ridge fit per window: minutes on the laptop. No GPU.

### 2.9 Evidence at retail scale

None; contemporaneous only. Its value for this program is as a better input to the forecasting methods below.

---

## 3. Integrated OFI and cross-impact (Cont, Cucuringu and Zhang 2023)

Source: Cont, R., Cucuringu, M. and Zhang, C. (2023), "Cross-impact of order flow imbalance in equity markets",
Quantitative Finance; arXiv 2112.13213v4 (`ccz2023_crossimpact.pdf/.txt`).

### 3.1 Core idea

Two steps. First, compress the ten level-by-level OFIs into one number, "integrated OFI", using the first principal
component of their historical covariance: the levels are highly correlated, so one weighted sum carries most of the
information and avoids over-fitting. Second, ask whether the order flow of *other* assets helps. Answer:
contemporaneously, no ("multi-asset models with cross-impact do not provide additional explanatory power for
contemporaneous impact compared to a sparse model without cross-impact terms"); for forecasting the next minute,
yes, a little ("lagged cross-asset OFIs do improve the forecasting of future returns ... this lagged cross-impact
mainly manifests at short-term horizons and decays rapidly in time").

### 3.2 Equations

Level-m OFI of asset i over (t - h, t] (CCZ eq. 2), scaled by average depth across M levels (eq. 3):

    OFI^{m,h}_{i,t} = sum_{n = N(t-h)+1}^{N(t)} (OF^{m,b}_{i,n} - OF^{m,a}_{i,n})
    ofi^{m,h}_{i,t} = OFI^{m,h}_{i,t} / Q^{M,h}_{i,t},
    Q^{M,h}_{i,t} = (1/M) sum_{m=1}^{M} [1/(2ΔN(t))] sum_n (q^{m,b}_{i,n} + q^{m,a}_{i,n})

with ΔN(t) = N(t) - N(t - h) the event count in the window and M = 10. Integrated OFI (eq. 4):

    ofi^{I,h}_{i,t} = w_1ᵀ ofi^{(h)}_{i,t} / ||w_1||_1

where w_1 is "the first principal vector computed from historical data" and dividing by the l1 norm makes the
weights sum to 1. The paper reports the first component "can explain over 89% of the total variance among
multi-level OFIs". Returns are log mid returns r^{(h)}_{i,t} = log(P_{i,t}/P_{i,t-h}) (eq. 5). Models: price-impact
(own OFI only) and cross-impact (all assets' OFIs) regressions, fit with LASSO for sparsity; forward-looking versions
(their eqs. 12-17) regress the next-minute return on lagged OFIs or lagged returns (AR and cross-AR).

**Why PCA here (short derivation).** If the ten level-OFIs are x = (x_1..x_10) with covariance Σ, the unit vector
w that maximizes Var(wᵀx) is the top eigenvector of Σ (maximize wᵀΣw subject to wᵀw = 1; the Lagrangian gives
Σw = μw, and the variance is the eigenvalue μ). If 89% of the variance lies along w_1, then wᵀx is nearly a
sufficient one-number summary, and a regression on one variable cannot over-fit across levels.

### 3.3 Data; one CME contract enough?

Integrated OFI needs mbp-10 for one contract: yes. Cross-impact needs several contracts' books at once (for
example MES with ES, or MES with ZN): a single-contract purchase cannot test it. CCZ used "the top 100 components of
S&P 500 index, existing from 2017-01-01 to 2019-12-31" from LOBSTER.

### 3.4 What it estimates

A depth-normalized, multi-level flow summary (the useful part for this program) and a cross-asset lead-lag at
one-minute horizons.

### 3.5 Worked example

Toy weights w_1 = (0.4, 0.3, 0.2, 0.1) on four levels, normalized ofi vector (1.0, 0.5, -0.2, 0.3): ofi^I = (0.4 +
0.15 - 0.04 + 0.03) / 1.0 = **0.54** (`C2_OFI_examples.out` section 6). The real w_1 puts most weight on the top
levels but not all; CCZ Figure 2 shows the weights by stock.

### 3.6 Published results, including the null ones

- Contemporaneous, in sample: own best-level OFI explains "71.16% of the in-sample variation"; integrated OFI gives
  "an average adjusted R2 value of 87.14%". Adding cross-asset integrated OFI adds "0.71%".
- **Forecasting the next minute: out-of-sample R² is negative for every model.** Table 8, "Out-of-sample performance
  for one-minute-ahead returns": FPI[1] -0.37, FCI[1] -0.10, FPI^I -0.36, FCI^I -0.10, AR -0.36, CAR -0.10 (mean
  across stocks and windows; the paper reports R² in percent elsewhere, for example 87.14%, so these are most likely
  -0.37% and so on). Cross-impact beats own-impact "at the 1% confidence level", but neither beats the historical
  mean. Integrated OFI forecasts no better than lagged returns (AR).
- The authors argue negative R² is not useless: "negative R2 values do not imply that the forecasts are economically
  meaningless", and run a strategy that "only executes an order when the one-minute-ahead return forecast exceeds the
  bid-ask spread". Its annualized PnL is 0.21 to 0.43 (Table 11; units as in the paper), and **"the strategy ignores
  trading costs, as this is not the focus of our paper."** The cost-free PnL of the lagged-return AR model (0.23) is
  the same as that of the own-OFI model (0.21 and 0.23).
- Horizon: "the PnL of cross-asset models declines more quickly over longer horizons."

### 3.7 Pilot hypothesis

Integrated OFI is the natural single feature for H-OFI-1 (it replaces the choice among 10 levels with one frozen
weight vector, estimated on training data), so it can be used *instead of* level-1 OFI at no extra trial cost if the
lead declares it as the one feature. Cross-impact needs a second contract's data (a later purchase): **H-XI-1**,
"lagged ES integrated OFI over the previous 1 s predicts the MES mid change over the next 1 s beyond MES's own
OFI", statistic the out-of-sample R² difference with a Diebold-Mariano test; sample several million 1-s intervals
(available from 4 months); 1 configuration per lag-horizon pair. Expect ES and MES to be nearly the same book (same
index, arbitraged within milliseconds, see section 10), so the lead-lag, if any, will be sub-second and not
reachable from Vancouver.

### 3.8 Compute

PCA of a 10 x 10 covariance and LASSO fits: laptop, minutes.

### 3.9 Retail evidence

CCZ's own result is the most direct evidence in this section: at a one-minute horizon OFI-based forecasts lose to the
historical mean out of sample, and the trading result excludes costs. The equity spreads they compare against are
not CME fees; on MES the fee alone is about one tick (section 0.1).

---

## 4. Deep order-flow imbalance (Kolm, Turiel and Westray 2023)

Source: Kolm, P. N., Turiel, J. and Westray, N. (2023), "Deep order flow imbalance: extracting alpha at multiple
horizons from the limit order book", Mathematical Finance 33(4), 1044-1081. **Full text not obtained** (paywall;
SSRN 403). Read: the abstract on IDEAS/RePEc (`ktw2023_ideas.html`); the reimplementation and description in Lucchese,
Pakkanen and Veraart (2024, `lpv2024_predictability.txt`, section 2.3.2); and a second description in Jaddu and
Bilokon (2023, `dl_rl_lob_2023.txt`, section 2). Claims taken only from the secondary papers are labelled
"(secondary)".

### 4.1 Core idea

Feed a neural network not the raw book (prices and sizes, which drift and are non-stationary) but the per-level order
flows of section 2, which are stationary. The abstract: "While raw order book states can be used as input to the
forecasting models, we achieve state-of-the-art predictive accuracy by training simpler 'off-the-shelf' artificial
neural networks on stationary inputs derived from the order book. Specifically, models trained on order flow
significantly outperform most models trained directly on order books." The forecast is a regression of future
returns at several horizons at once ("alpha at multiple horizons"), and the paper finds "that the effective horizon
of stock specific forecasts is approximately two average price changes."

### 4.2 Equations

Inputs (Lucchese et al. section 2.3.2, restating Kolm et al.): for book event t and level l, bid and ask order flow

    bOF^(l)_t = v^(l)_{b,t}                      if p^(l)_{b,t} > p^(l)_{b,t-1}
              = v^(l)_{b,t} - v^(l)_{b,t-1}       if p^(l)_{b,t} = p^(l)_{b,t-1}
              = -v^(l)_{b,t-1}                    if p^(l)_{b,t} < p^(l)_{b,t-1}
    aOF^(l)_t = -v^(l)_{a,t-1}                    if p^(l)_{a,t} > p^(l)_{a,t-1}
              = v^(l)_{a,t} - v^(l)_{a,t-1}       if p^(l)_{a,t} = p^(l)_{a,t-1}
              = v^(l)_{a,t}                       if p^(l)_{a,t} < p^(l)_{a,t-1}
    OFI^(l)_t = bOF^(l)_t - aOF^(l)_t

(v = volume, p = price, b = bid, a = ask; the same as MLOFI per event, without summing over a clock interval.) The
network input is the last T events of all 2L flows, "a (T × 2L) array", {x_{t-τ}} = (aOF^(l)_{t-τ}, bOF^(l)_{t-τ})
for τ = 0..T-1 and l = 1..L. Lucchese et al.: "The original deepOF specification in Kolm et al. (2021) was
structured as a (multi-horizon) regression task. In their setting, the last layer of the deep neural network maps
each prediction to R". Jaddu and Bilokon (secondary) state that "The first ten OFI levels were used by Kolm et al."
and that performance was measured by out-of-sample R² per horizon h,

    R²_OS,h = 1 - MSE_{m,h} / MSE_{bmk,h}

with MSE_{m,h} the model's mean squared error and MSE_{bmk,h} that of a benchmark, "the average out-of-sample return
of the stock" (secondary, citing Kolm et al. page 17). R²_OS > 0 means the model beats the historical mean.

Architecture: LSTM and CNN-LSTM networks (the deepLOB architecture of Part 1 with the order-flow array entering "at
the second convolutional layer", Lucchese et al.). The weights are fit by Adam on squared error; Jaddu and Bilokon
report (secondary) a learning rate of 0.00001, batch size 256 and four hidden layers for the MLP variant [these
hyperparameters are unverified against the original].

### 4.3 Data; one CME contract enough?

Kolm et al. used LOBSTER data for "115 stocks traded on Nasdaq" (abstract). Jaddu and Bilokon (secondary) describe
"a 3-week rolling-window out-of-sample methodology across 48 weeks using a (1-week validation, 4-weeks training,
1-week out-of-sample testing) structure". So each fitted model saw four weeks of one stock. On that design, 4 months
of one CME contract's mbp-10 (about 17 weeks) is enough for roughly 12 rolling test weeks; 12 months would give
about 47. mbp-10 is the right schema (ten levels of size and price at every change); mbo is not needed.

### 4.4 What it estimates

E[mid return over the next h events | last T events of order flow], for several h at once. It decides nothing; a
trading rule must be wrapped around it (threshold, side, size), and each wrapper is a configuration.

### 4.5 Worked example

The input arithmetic is that of section 1.5 per level. A worked example of the output scale is more useful: if the
model's R²_OS at horizon h is 2% and the standard deviation of the h-event mid return is 1 tick, the forecasts have
standard deviation sqrt(0.02) x 1 = 0.14 tick, and their mean absolute size is about 0.14 x sqrt(2/π) = 0.11 tick
(for a normal forecast). Against the MES taker hurdle of 1.98 ticks (section 0.1) a forecast would have to be about
14 standard deviations from zero before a trade paid. This is why such forecasts are used to time or cancel passive
orders, not to cross the spread.

### 4.6 Published results

- From the abstract: order-flow inputs beat raw-book inputs; forecastability is linked to stock characteristics
  ("'information-rich' stocks can be predicted more accurately"); the effective horizon is about two average price
  changes.
- Secondary: "the results show that models perform better when using OF and OFI as input rather than raw LOB and
  that CNN-LSTM extracts alpha most accurately, followed by LSTM-MLP, LSTM, and a stacked LSTM" (Jaddu and Bilokon),
  and "Kolm et al. [5] observed that price prediction accuracy falls off after six horizons".
- Lucchese et al. (2024), who reran deepOF on Nasdaq stocks with model confidence sets: "models based on the basic
  order book level representation are considerably outperformed by those with order flow or volume inputs", and the
  predictability "was found to persist up to 50-300 order book updates ahead ... Such predictable horizons might
  vary from a few milliseconds to nearly half a second, depending on the stock under consideration."
- Neither the abstract nor the two secondary descriptions report a cost-inclusive trading result for deepOF
  [whether the original paper contains one is unverified].

### 4.7 Pilot hypothesis

**H-DOF-1.** A deepOF-type regression trained on the earlier part of the purchase predicts the sign of the mid change
over the next k book events (k fixed in advance, for example k = 2 average mid changes as Kolm et al. found) with
R²_OS > 0 on a later, untouched block. Statistic: R²_OS with a Diebold-Mariano test of squared errors against the
historical-mean benchmark; then the economic test, H-OFI-1's markout regression with the model forecast in place of
OFI. Sample: a predictive R² of ρ² corresponds to a forecast-outcome correlation ρ, and the t-statistic of a
correlation on n independent observations is about ρ sqrt(n); so t = 3 at R² = 1% (ρ = 0.1) needs n = 9/0.01 = 900
non-overlapping observations, and at R² = 0.1% needs 9,000 [first-order approximation that ignores estimation noise
in the coefficients, so an out-of-sample test needs more]. Four months of event-time data supply far more; the
binding sample is the economic test on fills. Trial count: architecture (1) x input depth L (1 if
fixed at 10) x horizons (1 to 6) x training window (1): 1 to 6 configurations before any trading wrapper, plus the
wrapper configurations. Training-set tuning by validation is inside the frozen pipeline and does not add to N if
the grid is declared.

### 4.8 Compute

The deepLOB-family networks are small (Part 1 gives parameter counts). On the RTX 3050 (4 GB) an LSTM with 10-level
order-flow input of length T = 100 trains with batch 256 well inside memory; the binding limit is RAM for the event
arrays (88 million events x 20 float32 flows = 7.1 GB for 84 RTH days at the ES event rate,
`C2_OFI_examples.out` section 8), so training must stream from disk in day chunks. A rolling scheme of 12 refits
on 4 months is a guess of 1 to 3 GPU-hours per refit on the 3050 [unverified, no probe run]. If that is too slow, a
rented RTX 4090 costs $0.89 per hour and an A100 PCIe 80 GB $1.79 per hour on RunPod, and an H100 PCIe $3.29 per
hour on Lambda (1-GPU plan) (`runpod_pricing.html.txt`, `lambda_pricing.html.txt`, fetched 2026-10-21): 50 GPU-hours
would cost about $44 on a 4090, $90 on an A100 and $164 on an H100 (`C2_OFI_examples.out` section 9).

### 4.9 Evidence at retail scale and latency

- The horizon is the problem. "approximately two average price changes", or "a few milliseconds to nearly half a second"
  in Lucchese et al., is shorter than or comparable to this program's order round trip from Vancouver (tens of
  milliseconds before any model time).
- Lucchese et al. state the practical limits plainly: "we focus on mid-to-mid returns, which are not tradable in
  practice"; "Another critical aspect that would need to be accounted for in practical high-frequency trading is
  total execution speed"; "if many traders exploit the same inefficiencies, this might erode all predictive power
  above the lowest tradable latencies"; "while the predictability identified in this paper might not be directly
  tradable through a standalone strategy, it might still help some market players, such as market makers, to gauge
  the direction of the market and adjust their quotes accordingly."
- The one retail-style attempt found (Jaddu and Bilokon 2023, OFI features in a Kolm-style model feeding RL agents
  on CFDs: FX, DE40, FTSE 100, gold) is a negative result: "backtesting with retail costs produced promising
  results, with profitability achieved using Q Learning on GBPUSD and EURUSD, but failed to bring similar results
  during forward testing. This is due to long processing times of making predictions, sometimes skipping two
  timesteps". They had "Only ten weeks of order flow imbalance data" per instrument.

---

## 5. Queue imbalance and trade-flow features

### 5.1 Queue imbalance (Gould and Bonart 2016)

Source: Gould, M. D. and Bonart, J. (2016), "Queue imbalance as a one-tick-ahead price predictor in a limit order
book", Market Microstructure and Liquidity; arXiv 1512.03492v1 (`gould_bonart2016_qi.pdf/.txt`).

**(1) Idea.** Compare the sizes of the best bid and best ask queues. When the bid queue is much larger than the ask
queue, the next mid move is more likely up (the ask queue is more likely to be depleted first). This is the simplest
order-book predictor and the one with the most direct use for a passive order: a resting bid at the front of a small
bid queue facing a large ask queue is likely to be filled just before the price drops.

**(2) Equations.** Queue imbalance (Gould-Bonart eq. 7):

    I(t) = (n_b(b_t, t) - n_a(a_t, t)) / (n_b(b_t, t) + n_a(a_t, t)),   I ∈ [-1, 1]

with n_b(b_t, t) the volume at the best bid price b_t and n_a(a_t, t) the volume at the best ask a_t. The predictor of
the direction of the next mid move y (1 = up, 0 = down) is a logistic regression

    P(y = 1 | I) = 1 / (1 + exp(-(x_0 + I x_1)))

with x_0 and x_1 fitted by maximum likelihood (the formula appears in the arXiv text as "1 + e^{-(x0 + Ix1)}"). They
also fit local (kernel) logistic regressions. Derivation sketch [standard, not from the paper]: if each queue is
depleted at a rate proportional to the opposite side's pressure, the chance the ask empties first rises with n_b /
(n_a + n_b) = (1 + I)/2, which is why a monotone S-shaped function of I is the natural first model; Stoikov's
microprice (C2_LOB.md section 5) turns the same idea into a price estimate.

**(3) Data.** Best-queue sizes at the moment before each mid change. mbp-1 is enough; mbp-10 contains it. Their data:
"10 liquid stocks on Nasdaq". One CME contract over 4 months gives tens of thousands of mid changes or more: ample.

**(4) Estimates.** P(next mid move is up | I).

**(5) Worked example** (`C2_OFI_examples.out` section 4, with illustrative coefficients x_0 = 0, x_1 = 2): bid queue
40, ask queue 10: I = 30/50 = 0.6, P(up) = 1/(1 + e^{-1.2}) = 0.769. Reversed (10 vs 40): 0.231. Equal queues: 0.5.
The paper's own example: "if n_b(b(t), t) = 200 and n_a(a(t), t) = 100 ... I(t) = (200 − 100)/(200 + 100) = 1/3."

**(6) Results.** "Compared to the null model, we find that our logistic regressions improve out-of-sample performance
of binary classification by about 50–60% for large tick stocks and about 10–30% for small-tick stocks", and
probabilistic predictions improve "by about 20–30% for large-tick stocks and about 2–6% for small-tick stocks."
MES/ES are large-tick, so the stronger number is the relevant one, with the caveat that these are 2014 Nasdaq
stocks. The prediction is of the *next* mid move, whenever it comes; it says nothing about how soon.

**(7) Pilot hypothesis. H-QI-1.** For the pilot's simulated 1-lot passive fills, the 1 s and 10 s markouts are
monotone in the queue imbalance on the order's own side at the time of the fill (fills when the own-side queue was
small relative to the opposite queue have worse markouts). Statistic: slope of markout on signed I_j with
Newey-West t, or the difference between top and bottom terciles. Sample as H-OFI-1 (about 400 to 1,600 fills per
tercile for 0.2 to 0.1 tick differences at 1-tick markout standard deviation). Trial count: 1 per markout horizon
fixed in advance. A cheaper companion that needs no fills at all: **H-QI-0**, logistic regression of the next mid move
on I across all mid changes in the test block; statistic: out-of-sample AUC against 0.5. With 2,000 events per class,
an AUC of 0.55 gives z = 5.5 and 0.52 gives z = 2.2 (Hanley-McNeil approximation, `C2_OFI_examples.out` section 7);
this replicates Gould and Bonart on a CME contract and costs 1 trial.

**(8) Compute.** Logistic regression on one feature: seconds.

**(9) Retail evidence.** Gould and Bonart themselves stress simplicity, not tradability: the methods "are extremely
simple to implement and outperform our simple null model by a considerable margin". Stoikov and Waeber (2016,
section 9.1) give the most useful retail-latency evidence for this exact feature: it still saves execution cost at
100 ms and at 1 s, but less.

### 5.2 Trade-flow features

Trade imbalance (signed traded volume over an interval: buyer-initiated minus seller-initiated) is the older measure.
CKS tested it directly (section 4.1 of CKS): "the average R2 for order flow imbalance is 65% compared to 32% for the
trade imbalance", and when both are included "the dependence on trade imbalance becomes questionable. The average
t-statistic of T I_k decreases by a factor of four". The Aït-Sahalia, Fan, Xue and Zhou (2022) predictor set (section
6) mixes trade variables (TxnImbalance, PastReturn) with book variables (LobImbalance) and reports that
"TxnImbalance, PastReturn, LobImbalance are almost always used" by LASSO. For this program trade-flow features come
free with mbp-10 (`action = T` rows carry side and size) or with tbbo, so they belong in any feature set as a
control, not as a separate method.

---

## 6. Gradient-boosted trees (XGBoost, LightGBM) on OFI features

Sources: Chen, T. and Guestrin, C. (2016), "XGBoost: a scalable tree boosting system", KDD; arXiv 1603.02754v3
(`xgboost_chen_guestrin2016.pdf/.txt`). Ke, G. et al. (2017), "LightGBM: a highly efficient gradient boosting
decision tree", NeurIPS (`lightgbm_ke2017.pdf/.txt`). Evidence: Aït-Sahalia, Fan, Xue and Zhou (2022), NBER w30366
(`afxz2022_hf_predictable.pdf/.txt`); Wang (2025), arXiv 2506.05764 (`crypto_lob_gbdt_2025.txt`); Wang (2025b),
arXiv 2509.22985 (`liq_withdraw_ml_2025.txt`).

### 6.1 Core idea

A boosted tree model is a sum of many small regression trees. Each new tree is fitted to the errors left by the trees
before it. Trees capture thresholds and interactions automatically (for example "OFI matters only when the spread
is one tick and the own queue is small") that a linear model on OFI misses. The program has used LightGBM before on
1-minute bars; here the inputs would be event-time or second-level order-flow features.

### 6.2 Equations (XGBoost paper, eqs. 2, 4, 5, 6)

Prediction for observation i with K trees: ŷ_i = sum_{k=1}^{K} f_k(x_i), each f_k a tree that maps x to a leaf j and
returns that leaf's weight w_j. The regularized objective (eq. 2):

    L(φ) = sum_i l(ŷ_i, y_i) + sum_k Ω(f_k),    Ω(f) = γT + (1/2) λ ||w||²

with l a differentiable convex loss, T the number of leaves in the tree, γ the cost per leaf and λ the L2 penalty
on leaf weights. At boosting step t, with g_i and h_i the first and second derivatives of the loss with respect to
the previous prediction, a second-order Taylor expansion gives (eq. 4)

    L̃^(t) = sum_{j=1}^{T} [ (sum_{i∈I_j} g_i) w_j + (1/2)(sum_{i∈I_j} h_i + λ) w_j² ] + γT

where I_j is the set of observations falling in leaf j. Minimizing each quadratic in w_j gives the optimal leaf
weight and the tree's score (eqs. 5, 6):

    w*_j = - (sum_{i∈I_j} g_i) / (sum_{i∈I_j} h_i + λ)
    L̃^(t)(q) = -(1/2) sum_j (sum_{i∈I_j} g_i)² / (sum_{i∈I_j} h_i + λ) + γT

The score is used to choose splits greedily. For squared loss l = (1/2)(ŷ - y)², g_i = ŷ_i - y_i and h_i = 1.
LightGBM optimizes the same kind of objective but speeds up the split search with two techniques the paper names:
"Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling (EFB)" (keep all large-gradient rows and a
sample of small-gradient rows; bundle features that are rarely non-zero together), plus histogram binning.

### 6.3 Worked example (`C2_OFI_examples.out` section 5)

Squared loss, a leaf with three observations whose residuals ŷ - y are -0.5, -0.2, +0.1 tick (the current model is
too low on the first two): G = -0.6, H = 3, λ = 1. Leaf weight w* = -(-0.6)/(3 + 1) = **+0.15 tick** (the leaf
raises the prediction by 0.15, less than the mean residual of 0.2 because λ shrinks it), and the leaf's objective
contribution is -(1/2)(0.36)/4 = -0.045. With λ = 0 the weight would be 0.2, the plain mean: λ is a shrinkage
towards zero that matters most in small leaves.

### 6.4 Data; one CME contract enough?

Any feature table: OFI and MLOFI over several look-back windows, queue imbalance, spread, depth, trade imbalance,
recent returns, time of day. mbp-10 for one contract supplies all of them. Trees need many observations per leaf; 4
months of 1-second or event-time rows (millions) is ample for fitting, and the limiting factor is again the weak
signal, not the row count.

### 6.5 What it estimates

E[y | x] for a chosen label y (section 8), or P(class | x) for classification.

### 6.6 Published results, including null ones

- **Trees add little over a linear model.** Aït-Sahalia et al. (2022), S&P 100 stocks, January 2019 to December
  2020, a horse race of OLS, ridge, LASSO, FarmPredict, random forests, gradient boosted trees and small neural
  networks: "all methods have very similar performance, except OLS. The improvements from a nonlinear method like
  random forest or gradient boosting trees are limited for most cases when compared with LASSO."
- The same paper finds large out-of-sample predictability over very short horizons: "The median out-of-sample R2
  for predicting 5-second returns is approximately 10% and furthermore R2 > 0 for every single stock". Two caveats.
  First, its return is "the average transaction price in a time window divided by the mid-quote price at the
  timestamp" (their eq. 2.4 and section 7.3), so part of what is predicted is whether the next trades print at the
  bid or the ask, which a taker cannot capture [this interpretation is mine, from the definition]. Second, the
  predictability is very short-lived (section 9).
- Crypto (BTC/USDT, Bybit, horizons 100 ms to 1 s; a single-author working paper): "with data preprocessing and
  hyperparameter tuning, simpler models can match and even exceed the performance of more complex networks",
  comparing logistic regression and XGBoost with DeepLOB. No cost-inclusive trading test was found in it.
- Nasdaq MBO, one hour of seven stocks, forecasting a liquidity-withdrawal index (not returns): "forecasts at 250 ms
  are noise-dominated; XGBoost delivers the best out-of-sample accuracy at 1 s and 5 s; and HAR is competitive, and
  best for most symbols, at 2 s."
- No published study of LightGBM or XGBoost on OFI features for CME futures was found (two WebSearch queries and two
  arXiv API queries; `work/C2_OFI/C2_OFI_arxiv_*.xml`). This is a search gap, not evidence of absence.

### 6.7 Pilot hypothesis

**H-GBT-1.** A LightGBM model on a frozen feature list (integrated OFI over 3 look-backs, queue imbalance, spread,
depth, trade imbalance, last 3 mid changes, time of day) predicts the 10 s markout of a passive fill better than the
linear H-OFI-1 regression. Statistic: Diebold-Mariano test on squared markout errors in the test block, then the
economic test (does excluding the worst predicted decile of fills raise the mean markout by more than fees allow).
Sample: as H-OFI-1, at least about 1,500 test-block fills. Trial count: one per frozen hyperparameter set; if a grid
is searched on validation data inside the pipeline, the lead decides whether the grid counts as one configuration
or as its size (V43 says every configuration counts; a 3 x 3 grid of depth x learning rate is 9). The evidence above
(trees about equal to LASSO) argues for declaring the linear model as primary and the trees as one secondary
configuration.

### 6.8 Compute

LightGBM on a few million rows by 20 to 40 features trains in seconds to minutes on 10 CPU threads; memory is
the feature table (about 84 days x 23 h x 3,600 = 7 million 1-s rows x 40 float32 = 1.1 GB for 4 months of near-24-hour trading). The
GPU is not needed. Event-time tables are larger (section 4.8): stream or subsample.

### 6.9 Retail evidence

None found that is cost-inclusive on futures. The best large study (Aït-Sahalia et al.) finds the edge is in the
first milliseconds and that trees do not beat LASSO by much; both points cut against a slow trader.

---

## 7. Contemporaneous versus predictive R-squared

This is an evaluation method, not a model, but it decides how to read every number above.

### 7.1 Core idea

A contemporaneous regression (ΔP over [t-1, t] on OFI over [t-1, t]) measures how prices are *formed*: it is high
partly by construction, since the events that move the price are counted in OFI. A predictive regression (ΔP over
[t, t+1] on OFI over [t-1, t]) measures what a trader could *know in advance*. Only the second matters for trading,
and it is usually one or two orders of magnitude smaller.

### 7.2 Equations and a short derivation (assumptions stated)

Assume the CKS relation holds exactly with noise independent of past flow:

    ΔP_k = β OFI_k + ε_k,   ε_k independent of OFI_{k-1},   Var(ΔP_k) = β² Var(OFI) + σ²_ε
    contemporaneous R²_c = β² Var(OFI) / Var(ΔP)

and assume OFI is autocorrelated with lag-1 correlation ρ (order flow is persistent because large orders are split).
Then Cov(ΔP_k, OFI_{k-1}) = β Cov(OFI_k, OFI_{k-1}) = β ρ Var(OFI), so the predictive R² of a regression of ΔP_k on
OFI_{k-1} is

    R²_pred = Corr(ΔP_k, OFI_{k-1})² = β² ρ² Var(OFI)² / (Var(OFI) Var(ΔP)) = ρ² R²_c

**Under these assumptions the predictive R² is the contemporaneous R² times the squared autocorrelation of the flow.**
With R²_c = 0.65 (CKS) and ρ = 0.1, R²_pred = 0.0065; with ρ = 0.05, 0.0016; with ρ = 0.2, 0.026
(`C2_OFI_examples.out` section 2). CKS report that at 10 s "the autocorrelations at a timescale of 10 seconds are
small and quickly vanish". Predictability beyond this bound must come from something else (queue imbalance,
nonlinear book state, trade-sign persistence), which is what the deep and tree models try to extract.

### 7.3 What the literature reports on each side

| Quantity | Value | Source |
|---|---|---|
| Contemporaneous R², best-level OFI, 10 s, 50 NYSE stocks 2010 | 65% | CKS |
| Contemporaneous R², integrated OFI, 1 min, 100 Nasdaq stocks 2017-2019 | 87.14% (in sample) | CCZ Table 3 text |
| Predictive out-of-sample R², next 1-min return, own or integrated OFI | -0.37 / -0.36 (negative) | CCZ Table 8 |
| Predictive out-of-sample R², next 5-s return (trade-price based), S&P 100 2019-2020 | median about 10% | Aït-Sahalia et al. |
| Same, after a 10 ms data delay (INTC, 5 s horizon) | 14% falls to 2.5% | Aït-Sahalia et al. section 6.2 |

### 7.4 Worked example: from R² to a trading hurdle

If the forecast explains a fraction R² of the variance of the next-horizon mid move with standard deviation σ, the
forecast's own standard deviation is sqrt(R²)·σ and its mean absolute value is sqrt(R²)·σ·sqrt(2/π) for a normal
forecast. With σ = 1 tick: R² = 1% gives a mean |forecast| of 0.080 tick; 5% gives 0.178; 20% gives 0.357
(`C2_OFI_examples.out` section 3). The MES taker hurdle is 1.976 ticks. Even a 20% R² at a horizon where the mid
moves about 1 tick leaves the typical forecast at a sixth of the hurdle, and only rare extreme forecasts could pay.
A longer horizon raises σ (more ticks of movement to forecast) but, by 7.3, R² falls fast with horizon.

### 7.5 Pilot use and N

Every candidate hypothesis above should report both numbers: the contemporaneous fit (a data sanity check that costs
no trial and should reproduce CKS's linearity on the contract) and the predictive or markout test (the one that
counts in N). Declaring the contemporaneous check as diagnostic, not as a hypothesis, keeps it out of N.

### 7.6 Compute

None beyond the regressions.

### 7.7 Evidence

Covered in 7.3. The negative result is the main one: CCZ's out-of-sample R² for the next minute is below zero for
every OFI model.

---

## 8. Label design at horizons that beat costs

Sources: López de Prado (2018), Advances in Financial Machine Learning, chapter 3 (book not fetched); described in the
mlfinpy library documentation (`mlfinpy_labelling.rst.txt`, a secondary source that cites the book). Lucchese et al.
(2024) section 3 and A.6 for event-time labels and their practical limits.

### 8.1 The three label families, in plain words

1. **Fixed (clock) horizon.** Label = sign (or value) of the return from t to t + h seconds, with a dead band ±τ
   labelled 0. Simple, but the same h means very different things in quiet and busy periods, and it ignores the
   path (a trade stopped out at t + 2 s still gets the t + 10 s label).
2. **Event-time horizon.** Label = return over the next k book events or k mid changes (DeepLOB, Kolm et al.,
   Lucchese et al.). Comparable across activity levels, but the clock duration is random. Lucchese et al.: "we use an
   order book-driven clock. In practice, this means the prediction horizon is intrinsically stochastic, which might
   be a problem in execution."
3. **Triple barrier.** Label = which of three barriers is touched first: an upper return barrier (+1), a lower one
   (-1), or a time limit (0). The mlfinpy documentation: "the vertical barrier represents the amount of time an
   observation has to reach its given return in either direction before it is given a label of 0", and the
   barriers can be set "dynamically ... for each observation based on their given volatilities". The same page says
   of fixed-horizon labels that they "will always fail to capture information about the path of the prices
   [Lopez de Prado, 2018]".

### 8.2 Equations

Fixed horizon (mlfinpy, citing AFML): r_{t0,t1} = p_{t1}/p_{t0} - 1, and L = -1 if r < -τ, 0 if |r| <= τ, +1 if
r > τ.

Tradeable versions (this section's recommendation, not from a paper). For a taker buy at time t: entry at the ask
A_t, exit at the bid B_{t+h}, so the tradeable return in ticks is

    R^taker_{t,h} = (B_{t+h} - A_t)/δ - f,   f = fee per round turn in ticks (0.976 for MES, 0.302 for ES)

and for a passive buy that fills at the bid B_t and is marked at the mid M_{t+h}, the markout is

    R^maker_{t,h} = (M_{t+h} - B_t)/δ - f/2.

Lucchese et al. make the same point: "we focus on mid-to-mid returns, which are not tradable in practice. When
considering specific trading applications, one should thus define the return labels appropriately, for example,
working with ask-to-bid returns."

Triple barrier with costs: upper barrier at B_{t+s} >= A_t + (f + g)δ for a target net gain g, lower barrier at
B_{t+s} <= A_t - Lδ for a loss limit L, vertical barrier at s = H.

### 8.3 Worked example (MES taker)

Buy at the ask 5000.25. With f = 0.976 tick and target g = 1 tick net, the upper barrier needs the bid to reach
5000.25 + ceil(1.976) ticks = 5000.75 (2 ticks above entry: net 2 - 0.976 = 1.024 ticks = $1.28). A 4-tick loss
limit puts the lower barrier at a bid of 4999.25 (net -4.976 ticks = -$6.22). Vertical barrier 60 s. Breakeven
hit rate for the upper barrier, if every trade ends at one of the two price barriers: p x 1.024 = (1 - p) x 4.976,
so p = 4.976 / 6.0 = 82.9%. A model has to be right four times out of five in this design before costs are
covered; with symmetric 2-tick barriers (upper at +2, lower at -2: net +1.024 / -2.976) the breakeven is
2.976/4.0 = 74.4%. These hit rates are far above the accuracy of any published order-book model at
multi-second horizons (Part 1, section 4; Gould-Bonart's next-move classifier is about the next tick, not the next
two). Arithmetic: (2 - 0.976) = 1.024; (4 + 0.976) = 4.976; 4.976/(1.024 + 4.976) = 0.829.

### 8.4 Data and whether one contract is enough

All three labels can be built from mbp-1 or mbp-10 alone. The passive-order label (markout of a fill) needs a fill
model, which mbp-10 supports only with a queue-position assumption; mbo supports it directly (order ids, so the
simulated order's place in the queue can be tracked). This is the main reason the pilot schema choice matters for
this section.

### 8.5 Pilot use and N

The pilot's own outputs are labels already: 1/10/60 s markouts of a simulated passive fill are R^maker at h = 1, 10,
60 s. Each label definition (horizon, barrier pair) used in a test is a configuration. Overlapping labels (a 60-s
label computed every second overlaps 59 neighbours) require purged and embargoed cross-validation, which V43 already
mandates; the embargo should be at least the label horizon (60 s for the 60-s markout).

### 8.6 Compute and evidence

Label construction is a pass over the data: laptop, minutes. Evidence that triple-barrier labels improve
out-of-sample trading results on order-book data was not found in the fetched sources; the mlfinpy page argues for
the method but reports no test. The honest statement is that label choice changes what is being predicted, and the
only label that matches this program's trade is the cost-adjusted markout of a 1-lot passive fill.

---

## 9. Decay of predictive power with horizon and latency: what is left after 50 to 100 ms

### 9.1 The evidence, source by source

1. **Aït-Sahalia, Fan, Xue and Zhou (2022), S&P 100 stocks, 2019-2020.** The most direct measurement found.
   "approximately 80% of the overall predictability is achieved by relying on the most recent 10 milliseconds, 10
   transactions or 10 lots transacted." Delay test (INTC, 5-s horizon, delays 0.1 ms to 5 s): "the average
   out-of-sample R2 drops from 14% to 2.5% after a delay of 10ms (1% of a second) ... The results suggest that the
   majority of the predictability has its source in the most recent few milliseconds of price and quote
   movements." By horizon: "predictability of returns vanishes to 0 (meaning that a binary directional prediction
   becomes no better than a coin toss) in just five minutes". The R² values at 30 ms and 100 ms delay are in their
   Figure 14, which was not read numerically from the PDF; the text says the decrease is monotone, so they are below
   2.5% [exact values unverified].
2. **Stoikov and Waeber (read from the 16 September 2015 SSRN version), 5-year US Treasury notes on eSpeed (cash, not futures), July 2010, Level I.** An
   execution use (sell one lot within a horizon T, using top-of-book imbalance I_t = B_t/(A_t + B_t)), with latency
   L explicitly in the model. Table 1, savings over TWAP "expressed as percentages of the minimum bid ask spread"
   (the values are fractions: 0.32 means about a third of a spread, as the text says):

   | T (trade frequency) | L = 1 ms | L = 100 ms | L = 1000 ms | L = 5000 ms |
   |---|---|---|---|---|
   | 10 s | 0.20 | 0.17 | 0.11 | 0.05 |
   | 1 min | 0.32 | 0.26 | 0.17 | 0.07 |
   | 5 min | 0.33 | 0.35 | 0.18 | 0.07 |

   At 100 ms the imbalance signal still saves 0.26/0.32 = 81% of what it saves at 1 ms for a once-a-minute trader.
   This is the key distinction for this program: **as an execution aid for a trade you were going to make anyway,
   much of the signal survives 100 ms; as a standalone alpha, almost none does** (item 1). Their own words: "the
   advantage of observing the limit order book can dissipate quickly as execution latency increases."
3. **Lehalle and Mounjid (arXiv 2016, v1 2 October 2016), NASDAQ OMX Nordic labelled transactions plus a control model.** "the added value of exploiting a
   knowledge on liquidity imbalance is eroded by latency: being able to predict future liquidity consuming flows is
   of less use if you have not enough time to cancel and reinsert your limit orders", and in the numerical results
   "The latency cost increases exponentially with the latency factor τ". Also: "the identified effects are usually
   not strong enough to be the source of a statistical arbitrage: the expected value of buying and selling back
   using accurate predictions based on sizes at first limits does not beat transaction costs (bid-ask spread and
   fees)."
4. **Lucchese, Pakkanen and Veraart (2024).** Predictable horizons of "a few milliseconds to nearly half a second,
   depending on the stock".
5. **Takahashi (2025), ES 2008-2013, 1-s structural VAR.** "Impulse responses indicate that shocks dissipate almost
   entirely within a second."
6. **Kolm et al. (2023).** Effective horizon "approximately two average price changes" (abstract).

### 9.2 Plain-words answer

After 50 to 100 ms of total delay (a Vancouver-to-Aurora round trip plus processing), the directional forecasting
power of order-flow features at second-scale horizons is mostly gone: on the one dataset that measured it, a 10 ms
delay removes about 80% of the out-of-sample R². What remains usable is the slower, smaller part: the tendency of
the queue that is much smaller to be depleted first, which helps decide *whether to keep a passive order in the
queue* or *when to execute a trade already decided*, and which Stoikov and Waeber find still worth about 80% of its
1-ms value at 100 ms for an execution problem.

### 9.3 Pilot hypothesis

**H-LAT-1.** The predictive value of queue imbalance for the 10 s markout of a passive fill (H-QI-1's slope) is
still positive when the imbalance is measured 100 ms before the fill instead of at the fill. Statistic: the H-QI-1
slope computed with I_{t-100ms}; one-sided t > threshold set by the lead. This directly measures what a 100 ms trader
can still use. Sample as H-QI-1. Trial count: 1 per delay value; testing 0, 50, 100 and 250 ms adds 4, of which only
the 100 ms (or the measured latency of the account) should be the declared test, the rest diagnostics.
Practical note: Databento's `ts_recv` and `ts_event` (nanoseconds, in the mbp-10 schema) let the pilot apply any
delay exactly.

### 9.4 Compute

Recomputing features with a lag is a shift; laptop.

---

## 10. Latency races and sniping (Budish, Cramton and Shim 2015; Aquilina, Budish and O'Neill 2022; Cartea and Sánchez-Betancourt)

### 10.1 Budish, Cramton and Shim (2015), "The high-frequency trading arms race"

Read from the NBER conference version of 17 September 2013 (`bcs2013_nber.pdf/.txt`); the QJE 2015 version (130(4),
1547-1621) could not be fetched (both the Chicago Booth and Cramton links returned HTML pages). Numbers may differ
slightly in the published version.

**Idea.** ES and SPY track the same index. At human time scales they are almost perfectly correlated; at
millisecond scales the correlation collapses, because each trades in its own continuous order book and one updates
first. "Over all trading days in 2011, the median return correlation is just 0.0923 at 10 milliseconds and 0.0073 at
1 millisecond." When ES jumps, resting quotes in SPY become stale for a few milliseconds, and fast traders race to
hit them: "other market participants will try to 'snipe' the old quotes ... continuous limit order books process
message requests one-at-a-time in serial, so only the first message to reach the exchange matters – liquidity
providers usually lose the race."

**Equations (model section, eqs. 6.1 to 6.4 of the 2013 version).** A liquidity provider quotes spread s. Fundamental
traders arrive at rate λ_fund and pay s/2 each. The public signal jumps at rate λ_jump by J. If |J| > s/2 the N - 1
snipers and the provider race; the provider loses with probability (N-1)/N and then loses J - s/2. Zero profit for
the provider, with c_speed the cost of speed per unit time:

    λ_fund · s/2 - λ_jump · Pr(J > s/2) · E(J - s/2 | J > s/2) · (N-1)/N = c_speed        (6.1)
    λ_jump · Pr(J > s/2) · E(J - s/2 | J > s/2) · 1/N = c_speed                           (6.2)
    ⇒ λ_jump · Pr(J > s/2) · E(J - s/2 | J > s/2) = λ_fund · s/2                          (6.4)

Eq. 6.4 says the spread is set so that what liquidity providers earn from fundamental traders exactly pays for what
they lose to snipers. In the paper's words, "all of the expenditure by market makers on speed technology ultimately
is borne by fundamental investors, via the bid-ask spread."

**Worked example: a slow maker (this program) never wins the race.** Replace (N-1)/N by 1. On a 1-tick-spread
contract the passive order earns half the spread, 0.5 tick, against the mid when filled by a fundamental trader, and
loses J - 0.5 tick when sniped after a jump of J ticks; it also pays half the round-turn fee per fill. If a fraction
π of fills are snipes, the net per fill is (1 - π)·0.5 - π·(J - 0.5) - f/2 = 0.5 - πJ - f/2. Break-even π = (0.5 -
f/2)/J (`C2_OFI_examples.out` section 10):

| Contract | f/2 (ticks) | Break-even toxic share, J = 1 tick | J = 2 ticks |
|---|---|---|---|
| MES | 0.488 | 1.2% | 0.6% |
| ES | 0.151 | 34.9% | 17.4% |

On MES a slow passive order breaks even only if fewer than about 1 in 80 of its fills are picked off after a
1-tick jump. The pilot's 1 s markout distribution measures π directly (the share of fills followed within 1 s by a
mid move of a full tick against the order).

**Results.** "the arms race does not actually eliminate the arbitrage opportunities; rather, it just continually raises
the bar for capturing them": ES-SPY arbitrage duration fell "from a median of 97ms in 2005 to a median of 7ms in
2011", while profitability per opportunity stayed "at a median of about 0.08 index points per unit traded", with
"on average about a thousand such arbitrage opportunities per day in ES-SPY". Light alone needs "roughly 4
milliseconds to travel between Chicago (where ES trades) and New York".

### 10.2 Aquilina, Budish and O'Neill (2022), "Quantifying the high-frequency trading 'arms race'"

QJE 137(1); read from NBER w29011 (`abo2022_quantifying_race.pdf/.txt`). London Stock Exchange message data for
FTSE 100 stocks, which include failed attempts, so races can be seen directly. "latency-arbitrage races are very
frequent (about one per minute per symbol for FTSE 100 stocks), extremely fast (the modal race lasts 5-10 millionths
of a second), and account for a remarkably large portion of overall trading volume (about 20%)", "races constitute
roughly one-third of price impact and the effective spread", and "the top 6 firms accounting for over 80% of all race
wins and losses". The average race is worth "a bit more than half a tick". For a Vancouver trader with tens of
milliseconds of latency, races are decided three to four orders of magnitude faster than it can react; every race
involving its resting order is lost.

### 10.3 Cartea and Sánchez-Betancourt on latency

Sources: Cartea, Á. and Sánchez-Betancourt, L. (2021), "The shadow price of latency: improving intraday fill ratios in
foreign exchange markets", SIAM Journal on Financial Mathematics 12(1) 254-294, read as chapter 3 of Sánchez-
Betancourt's Oxford DPhil thesis "Uncertain Execution in Order-Driven Markets" (2021, `ora_ceba987f.pdf/.txt`);
and Cartea, Jaimungal and Sánchez-Betancourt, "Latency and liquidity risk" (arXiv 1908.03281,
`cjs_latency_liquidity_risk.txt`; published version on ORA, `ora_b14aafdb.txt`).

**Idea.** For a liquidity taker, latency creates a "moving target problem": "by the time their order is processed by
the exchange, prices or quantities may have worsened, so the order cannot be filled". They define latency broadly as
the sum of four delays (exchange streams data; trader receives and decides; trader sends; exchange receives and
processes) and, for a fill-or-kill order sent against the quote seen at t_0 and processed at t_4, "our measure of
latency is t_4 − t_0". The optimal strategy adds a price "discretion" to each marketable limit order, trading off
the cost of walking the book against the target fill ratio; the control problem is solved via FBSDEs ("The price
limit of a MLO is characterized as the solution to a new class of forward-backward stochastic differential
equations (FBSDEs) driven by random measures").

**Results (USD/JPY, two proprietary traders, December 2016 to March 2017).** Fill ratios of about 80% to 90%;
unfilled trades cluster in high volatility ("36.5% (resp. 40.0%) of T1's (resp. T2's) unfilled trades occur in the
top quartile of volatility"). Mapping latency to fill ratio with 50 "clones" of trader 1 with latencies of 0 to 50
ms: "when latency is zero, T0 would have obtained a fill ratio of 100%. At the other extreme T50's fill ratio is 89%",
and trader 1's naive strategy implied a latency of 27 ms (90% fill ratio). With the latency-optimal strategy, mean
daily fill rose to "between 98.9% and 99.5%" from 91.0%. The cost of chasing a missed trade with a market order 20
ms or 100 ms later was 2.33 and 2.88 ticks for trader 1 (USD/JPY ticks of 10^-3 JPY). The "shadow price of latency"
conclusion: trader 1 "would be better off employing the latency-optimal strategy developed here, instead of
investing in hardware and co-location services".

**Relevance.** This is the taker side of the same problem the pilot measures on the maker side: at tens of
milliseconds, a non-trivial share of intended trades fails or fills worse, and the effect concentrates in volatile
moments. Data: their method needs the trader's own order timestamps and the book (mbp-10 or mbo) at those times;
the pilot can reproduce the "clone" mapping on MES by replaying hypothetical marketable orders at delays of 0 to 100
ms against the recorded book.

### 10.4 Pilot hypotheses from this section

- **H-SNIPE-1.** Among simulated passive fills, the share followed within 1 s by a full-tick adverse mid move exceeds
  the MES break-even of 1.2% (section 10.1). Statistic: binomial test of the observed share against 1.2%; sample:
  with a true share of 5%, 400 fills give a standard error of 1.1 percentage points, ample. Trial count: 1. A
  rejection in the expected direction is a *negative* result for passive MES strategies and saves later trials.
- **H-LATFILL-1.** A replayed marketable limit order at the observed best quote fills less often as the assumed
  latency rises from 0 to 100 ms (Cartea-Sánchez-Betancourt mapping). This is a diagnostic curve, not an alpha test;
  it should be reported, not counted.

### 10.5 Compute

Replays over the recorded book: laptop.

---

## 11. Post-publication results and decay

What was found:

- **The contemporaneous relation has not decayed.** CKS (NYSE TAQ, April 2010): average R² 65% at 10 s. CCZ (Nasdaq,
  2017-2019): best-level OFI explains "71.16%" in sample at 1 min, integrated OFI 87.14%. This is expected: it is a
  mechanical price-formation relation, not an anomaly.
- **Very-short-horizon predictability persists after publication but lives at milliseconds.** Gould and Bonart (2014
  data) and Aït-Sahalia et al. (2019-2020 data) both find it; the later paper finds 80% of it in the last 10 ms.
- **Arbitrage-type edges persist but the speed bar rises.** BCS: ES-SPY opportunity durations fell from 97 ms to 7 ms
  over 2005-2011 while profit per opportunity stayed roughly constant, "it just continually raises the bar for
  capturing them".
- **One-minute OFI forecasts already fail out of sample** in 2017-2019 equities (CCZ Table 8, negative R²), with a
  trading test that excludes costs.
- **Retail forward test failed** (Jaddu and Bilokon 2023): profitable backtest with retail costs, failed forward test
  because of processing delays.

What was not found: no study that measures the decay of an OFI or queue-imbalance *trading* signal before and after
its publication (in the style of McLean and Pontiff for monthly anomalies). Absent that, the evidence above reads as
"the signal did not disappear; it moved to time scales this program cannot reach".

---

## 12. Evidence on futures specifically

| Market | What was found | Source (saved file) | Bearing on this program |
|---|---|---|---|
| CME E-mini S&P 500 (ES), 2008-2013 | OFI built from CME BBO files exactly as CKS; "On average, 45 events occur per second, each averaging 15 contracts"; spread at the minimum tick (mean 0.25 points); depth mean 0.63 thousand contracts; "both price and flow impacts are significant at the one-second horizon"; "shocks dissipate almost entirely within a second"; news announcements raise price impact | Takahashi 2025, arXiv 2508.06788v2 (`emini_ofi_2025.txt`) | Confirms the CKS mechanics on ES; one-second shock decay means no exploitable lag at 50 to 100 ms |
| ES versus SPY, 2005-2011 | Correlation collapse below 10 ms; ES leads; arbitrage windows 97 ms (2005) to 7 ms (2011) | BCS 2013 (`bcs2013_nber.txt`) | Any MES/ES lead-lag is a millisecond race |
| CME ES Level II, 2016; CME Eurodollar Level 1, 2018; Eurex Bund 2022 | Deep-model results | Part 1, C2_DeepLOB.md sections 5.1 to 5.3 | See Part 1 |
| US Treasuries (cash, eSpeed, 5-year notes, 2010) | Top-of-book imbalance predicts the next price move and saves about a third of the spread in execution at 1 ms latency; 0.26 of a spread at 100 ms; "this trading signal is hardly a secret in the 5 year US treasuries market" | Stoikov and Waeber 2016 (`ssrn2661618_treasury.txt`) | Cash, not futures, but the closest Treasury evidence; supports the execution-aid use, not alpha |
| US Treasury futures (ZN etc.) | Smales (2013) "Bond futures and order imbalance" (JIFMIB 26) and Fleming et al. (2018) on BrokerTec are cited by other papers | Pointers only, not fetched [unverified] | Gap |
| Crude oil (CL) | No OFI or queue-imbalance predictability study found; one 2025 Lakehead master's thesis on order-book curvature and volatility in crude futures (search result, not fetched) [unverified] | none | Gap |
| CSI 300 index futures (China), 500 ms snapshots | OFI impact modelled as an Ornstein-Uhlenbeck shock; "horizon-dependent heterogeneity" and "regime-dependent dynamics in the memory and forecasting power of order flow imbalance" | arXiv 2505.17388 (`csi300_ofi_2025.txt`) | Different market structure (snapshot data); weak transfer |
| NSE Nifty futures, September 2018 | Hawkes models forecast OFI itself (not returns) | arXiv 2408.03594 (`hawkes_ofi_forecast_2024.txt`) | Forecasting the flow is possible; says nothing about tradable returns |

Searches run for futures-specific OFI evidence: 4 WebSearch queries (E-mini, Treasury, crude, latency decay) and 2
arXiv API queries. The CME gap for Treasuries and crude is real in what this worker could reach.

---

## 13. Verdicts (use / maybe / skip for this program)

Verdicts are this worker's recommendation to the lead; the lead decides.

| Method | Verdict | Reason |
|---|---|---|
| OFI, level 1 (CKS 2014) | **Use** as a feature and as a data check | Costs nothing to compute from mbp-10; its contemporaneous linearity is a sanity test of the purchased data; as a 1-s pre-fill feature it is the obvious first test of adverse selection of passive fills (H-OFI-1). Not a standalone signal: contemporaneous only. |
| Multi-level OFI (XGH 2018) | **Maybe** (fold into integrated OFI) | Better contemporaneous fit with ridge, especially for large-tick books; on its own it adds trials without a separate trading use. |
| Integrated OFI (CCZ 2023) | **Use** as the single depth-normalized flow feature | One frozen PCA weight vector replaces a choice among ten levels, which saves trials. |
| Cross-impact (CCZ 2023) | **Skip** for the one-contract pilot; maybe later | Needs a second contract's book; one-minute forecasts were negative out of sample even in the paper; ES/MES lead-lag is a microsecond-to-millisecond race (BCS, ABO). |
| Deep OFI (Kolm et al. 2023) | **Skip** for now; maybe after a positive H-OFI-1/H-QI-1 | Effective horizon about two price changes (milliseconds to half a second); no cost-inclusive result seen; the only retail-style replication failed in forward test because of processing delay; GPU training is feasible but adds architecture and horizon trials. Full text not read. |
| Queue imbalance (Gould-Bonart 2016) | **Use** | Simplest and most robust feature for the passive-order decision on a large-tick contract; the only feature with published evidence (Stoikov-Waeber) of retaining most of its value at 100 ms latency in an execution use. H-QI-0 replicates it on CME data for 1 trial. |
| Trade-flow features | **Use** as controls only | CKS: trades add little once OFI is in; free in mbp-10. |
| Gradient-boosted trees on OFI features | **Maybe** (one secondary configuration) | Program already runs LightGBM; Aït-Sahalia et al. find trees add little over LASSO at high frequency; declare the linear model primary. |
| Predictive vs contemporaneous R² discipline | **Use** (mandatory reporting) | Prevents reading 65-87% contemporaneous R² as forecastability; R²_pred = ρ²R²_c under the linear AR(1) assumptions of 7.2. |
| Labels | **Use** cost-adjusted markouts of a 1-lot passive fill (the pilot's outputs) as the label; triple barrier only for a taker test | Mid-to-mid labels are not tradable; MES taker barriers need 74-83% hit rates (8.3). |
| Latency-decay measurement (H-LAT-1) | **Use** | The single most decision-relevant measurement for a tens-of-milliseconds trader, and cheap given nanosecond timestamps. |
| Sniping share (H-SNIPE-1) | **Use** | Directly tests whether passive MES can break even (1.2% toxic-fill ceiling); a likely negative that would save trials. |
| Any taker strategy on MES driven by order-flow forecasts | **Skip** | Hurdle about 2 ticks; published predictability is a fraction of a tick and gone within tens of milliseconds. |

### 13.1 Candidate hypotheses and their trial cost (for the lead)

| ID | Test | Trials if horizons fixed in advance | If all three markout horizons |
|---|---|---|---|
| H-QI-0 | Queue imbalance predicts next mid move on the CME contract (AUC > 0.5) | 1 | 1 |
| H-OFI-1 | Pre-fill signed integrated OFI predicts 10 s passive-fill markout | 1 | 3 |
| H-QI-1 | Own-side queue imbalance predicts passive-fill markout | 1 | 3 |
| H-LAT-1 | H-QI-1 still holds with the feature lagged 100 ms | 1 | 3 |
| H-SNIPE-1 | Toxic-fill share exceeds the 1.2% MES break-even | 1 | 1 |
| H-GBT-1 | LightGBM beats the linear markout model (one frozen hyperparameter set) | 1 | 3 |
| H-DOF-1 | deepOF R²_OS > 0 at a fixed event horizon | 1 to 6 | n/a |
| H-XI-1 | ES OFI leads MES (needs second contract) | 1 per lag-horizon pair | n/a |

The first five together add 5 to 11 trials to N and need only the pilot's own outputs plus the purchased book.

---

## 14. Fetch status and gaps

- WebSearch calls used: 11 of the 60 budgeted. No budget notice was received.
- Not obtained: Kolm, Turiel and Westray (2023) full text (Wiley Cloudflare challenge; SSRN 403; no free copy found
  in two searches); Budish, Cramton and Shim QJE 2015 published version (used the 2013 NBER version); López de Prado
  (2018) book (described from the mlfinpy documentation); Smales (2013) and Fleming et al. (2018) (pointers only);
  Cartea and Sánchez-Betancourt SIAM 2021 published version (used the thesis chapter).
- Not read numerically: Aït-Sahalia et al. Figure 14 (R² at 30 ms and 100 ms delay); XGH Tables 5 and 7.
- Saved but not used as evidence: `quantpedia_deepofi.html` (secondary blog), `ofi_conditional_impact_2020.pdf`
  (a master's dissertation; not needed).
- Scrapling and Firecrawl were not used (no terms checks were needed). No market data was read; MES depth and event
  rates are not known from any fetched source and the pilot should measure them.

---

## 15. References

1. Aït-Sahalia, Y., Fan, J., Xue, L. and Zhou, Y. (2022). How and when are high-frequency stock returns predictable?
   NBER Working Paper 30366. `afxz2022_hf_predictable.pdf`
2. Anantha, A. N. and Jain, S. (2024). Forecasting high frequency order flow imbalance using Hawkes processes. arXiv
   2408.03594v1. `hawkes_ofi_forecast_2024.pdf`
3. Aquilina, M., Budish, E. and O'Neill, P. (2022). Quantifying the high-frequency trading "arms race". Quarterly
   Journal of Economics 137(1); read as NBER Working Paper 29011. `abo2022_quantifying_race.pdf`
4. Budish, E., Cramton, P. and Shim, J. (2015). The high-frequency trading arms race: frequent batch auctions as a
   market design response. Quarterly Journal of Economics 130(4), 1547-1621; read as the NBER conference version of
   17 September 2013. `bcs2013_nber.pdf`
5. Cartea, Á., Jaimungal, S. and Sánchez-Betancourt, L. (2019). Latency and liquidity risk. arXiv 1908.03281;
   published version on ORA. `cjs_latency_liquidity_risk.pdf`, `ora_b14aafdb.pdf`
6. Cartea, Á. and Sánchez-Betancourt, L. (2021). The shadow price of latency: improving intraday fill ratios in
   foreign exchange markets. SIAM Journal on Financial Mathematics 12(1), 254-294; read as chapter 3 of
   Sánchez-Betancourt, L. (2021), Uncertain Execution in Order-Driven Markets, DPhil thesis, University of Oxford.
   `ora_ceba987f.pdf`
7. Chen, T. and Guestrin, C. (2016). XGBoost: a scalable tree boosting system. KDD 2016; arXiv 1603.02754v3.
   `xgboost_chen_guestrin2016.pdf`
8. Cont, R., Cucuringu, M. and Zhang, C. (2023). Cross-impact of order flow imbalance in equity markets.
   Quantitative Finance; arXiv 2112.13213v4. `ccz2023_crossimpact.pdf`
9. Cont, R., Kukanov, A. and Stoikov, S. (2014). The price impact of order book events. Journal of Financial
   Econometrics 12(1); arXiv 1011.6402v3. `cks2014_price_impact.pdf`
10. Databento (2026). Schemas and data formats: MBP-10; MBO. Documentation pages. `databento_mbp10.html`,
    `databento_mbo.html`
11. Gould, M. D. and Bonart, J. (2016). Queue imbalance as a one-tick-ahead price predictor in a limit order book.
    Market Microstructure and Liquidity; arXiv 1512.03492v1. `gould_bonart2016_qi.pdf`
12. Jaddu, K. S. and Bilokon, P. A. (2023). Combining deep learning on order books with reinforcement learning for
    profitable trading. arXiv 2311.02088v1. `dl_rl_lob_2023.pdf`
13. Ke, G., Meng, Q., Finley, T., Wang, T., Chen, W., Ma, W., Ye, Q. and Liu, T.-Y. (2017). LightGBM: a highly
    efficient gradient boosting decision tree. NeurIPS 30. `lightgbm_ke2017.pdf`
14. Kolm, P. N., Turiel, J. and Westray, N. (2023). Deep order flow imbalance: extracting alpha at multiple horizons
    from the limit order book. Mathematical Finance 33(4), 1044-1081. Abstract only (`ktw2023_ideas.html`); full
    text not read.
15. Lambda (2026). GPU cloud pricing page, fetched 2026-10-21. `lambda_pricing.html`
16. Lehalle, C.-A. and Mounjid, O. (2016). Limit order strategic placement with adverse selection risk and the role
    of latency. arXiv 1610.00261v1. `lm2017_latency_placement.pdf`
17. López de Prado, M. (2018). Advances in Financial Machine Learning, chapter 3. Wiley. Not read; described via the
    mlfinpy documentation, Labelling page. `mlfinpy_labelling.rst.txt`
18. Lucchese, L., Pakkanen, M. S. and Veraart, A. E. D. (2024). The short-term predictability of returns in order
    book markets: a deep learning perspective. International Journal of Forecasting; arXiv 2211.13777v3.
    `lpv2024_predictability.pdf`
19. RunPod (2026). GPU cloud pricing page, fetched 2026-10-21. `runpod_pricing.html`
20. Stoikov, S. and Waeber, R. (2016). Reducing transaction costs with low-latency trading algorithms. Quantitative
    Finance; read as the 16 September 2015 SSRN version (copy at smallake.kr). `ssrn2661618_treasury.pdf`
21. Takahashi, M. (2025). Returns and order flow imbalances: intraday dynamics and macroeconomic news effects. arXiv
    2508.06788v2. `emini_ofi_2025.pdf`
22. Wang, H. (2025). Exploring microstructural dynamics in cryptocurrency limit order books: better inputs matter
    more than stacking another hidden layer. arXiv 2506.05764v2. `crypto_lob_gbdt_2025.pdf`
23. Wang, H. (2025b). Forecasting liquidity withdrawal with machine learning models. arXiv 2509.22985v2.
    `liq_withdraw_ml_2025.pdf`
24. Xu, K., Gould, M. D. and Howison, S. D. (2018). Multi-level order-flow imbalance in a limit order book. Market
    Microstructure and Liquidity; arXiv 1907.06230v2; ORA record. `xgh2018_mlofi.pdf`, `ora_9b7d0422.html`
25. Zhang, X. et al. (2025). Stochastic price dynamics in response to order flow imbalance: evidence from CSI 300
    index futures. arXiv 2505.17388v1. `csi300_ofi_2025.pdf` [author list not checked]
26. Program file: rules/products.py lines 153-154 (MES and ES tick values and round-turn commissions).

Journal names for items 11, 18, 20 and 24 are from memory of the literature, not from the fetched texts [unverified].

---

## 16. Evidence table

All files are under `reports/stage_e28_briefs/pages/C2_OFI/` (text versions `.txt` for PDFs, `.html.txt` for HTML).

| Claim | Source | Verbatim quote | Saved file |
|---|---|---|---|
| OFI explains short-horizon mid changes linearly, R² 65% | CKS 2014 | "explains mid-price changes over short time scales in a linear fashion, for a large sample of stocks, with an average R2 of 65%" | cks2014_price_impact.txt |
| OFI beats trade imbalance | CKS 2014 | "the average R2 for order flow imbalance is 65% compared to 32% for the trade imbalance" | cks2014_price_impact.txt |
| Fit survives removing price-changing events | CKS 2014 | "With this change the R2 declined, but remained in the 35%-60% region." | cks2014_price_impact.txt |
| Impact inversely proportional to depth | CKS 2014 | "the hypothesis {λ = 1} cannot be rejected for 35 out of 50 stocks" | cks2014_price_impact.txt |
| Trades add little after OFI | CKS 2014 | "Trades seem to carry little to no information about price changes after the simultaneous order flow imbalance is taken into account." | cks2014_price_impact.txt |
| Level-1 data suffice | CKS 2014 | "Level 1 TAQ data can be successfully used to study limit orders" | cks2014_price_impact.txt |
| 10-s autocorrelations small | CKS 2014 | "the autocorrelations at a timescale of 10 seconds are small and quickly vanish as well" | cks2014_price_impact.txt |
| Deeper levels improve out-of-sample fit | XGH 2018 | "an improvement of about 65–75% for large-tick stocks and about 15–30% for small-tick stocks" | xgh2018_mlofi.txt |
| OLS over-fits MLOFI | XGH 2018 | "we uncover evidence to suggest that the OLS regressions over-fit" | xgh2018_mlofi.txt |
| First PC carries most multi-level variance | CCZ 2023 | "the first principal component can explain over 89% of the total variance among multi-level OFIs" | ccz2023_crossimpact.txt |
| Cross-impact adds nothing contemporaneously | CCZ 2023 | "multi-asset models with cross-impact do not provide additional explanatory power for contemporaneous impact compared to a sparse model without cross-impact terms" | ccz2023_crossimpact.txt |
| Integrated OFI in-sample R² | CCZ 2023 | "with an average adjusted R2 value of 87.14%" | ccz2023_crossimpact.txt |
| 1-minute forecasts negative out of sample | CCZ 2023 Table 8 | "OS R2 -0.37 -0.10 -0.36 -0.10 -0.36 -0.10" | ccz2023_crossimpact.txt |
| Trading test excludes costs | CCZ 2023 | "the strategy ignores trading costs, as this is not the focus of our paper." | ccz2023_crossimpact.txt |
| Lagged cross-impact decays fast | CCZ 2023 | "this lagged cross-impact mainly manifests at short-term horizons and decays rapidly in time" | ccz2023_crossimpact.txt |
| Deep OFI: order-flow inputs beat raw book | Kolm et al. 2023 (abstract) | "models trained on order flow significantly outperform most models trained directly on order books" | ktw2023_ideas.html |
| Deep OFI effective horizon | Kolm et al. 2023 (abstract) | "the effective horizon of stock specific forecasts is approximately two average price changes" | ktw2023_ideas.html |
| deepOF was a regression | Lucchese et al. 2024 | "The original deepOF specification in Kolm et al. (2021) was structured as a (multi-horizon) regression task." | lpv2024_predictability.txt |
| Predictable horizons ms to half a second | Lucchese et al. 2024 | "Such predictable horizons might vary from a few milliseconds to nearly half a second, depending on the stock under consideration." | lpv2024_predictability.txt |
| Mid-to-mid returns not tradable | Lucchese et al. 2024 | "we focus on mid-to-mid returns, which are not tradable in practice" | lpv2024_predictability.txt |
| Edge may be eroded above lowest latencies | Lucchese et al. 2024 | "this might erode all predictive power above the lowest tradable latencies" | lpv2024_predictability.txt |
| Event clock makes horizon random | Lucchese et al. 2024 | "the prediction horizon is intrinsically stochastic, which might be a problem in execution" | lpv2024_predictability.txt |
| Kolm et al. used 10 OFI levels (secondary) | Jaddu and Bilokon 2023 | "The first ten OFI levels were used by Kolm et al. [5]" | dl_rl_lob_2023.txt |
| Kolm et al. evaluation design (secondary) | Jaddu and Bilokon 2023 | "a 3-week rolling-window out-of-sample methodology across 48 weeks using a (1-week validation, 4-weeks training, 1-week out-of-sample testing) structure" | dl_rl_lob_2023.txt |
| Retail OFI forward test failed | Jaddu and Bilokon 2023 | "backtesting with retail costs produced promising results ... but failed to bring similar results during forward testing. This is due to long processing times of making predictions" | dl_rl_lob_2023.txt |
| Queue imbalance improves next-move classification | Gould and Bonart 2016 | "improve out-of-sample performance of binary classification by about 50–60% for large tick stocks and about 10–30% for small-tick stocks" | gould_bonart2016_qi.txt |
| XGBoost objective | Chen and Guestrin 2016 | "where Ω(f ) = γT + λkwk2" (eq. 2; the PDF text extraction of one half lambda times the squared norm of w) | xgboost_chen_guestrin2016.txt |
| LightGBM techniques | Ke et al. 2017 | "Gradient-based One-Side Sampling (GOSS) and Exclusive Feature Bundling (EFB)" | lightgbm_ke2017.txt |
| Trees add little over LASSO at high frequency | Aït-Sahalia et al. 2022 | "The improvements from a nonlinear method like random forest or gradient boosting trees are limited for most cases when compared with LASSO." | afxz2022_hf_predictable.txt |
| 5-s out-of-sample R² about 10% | Aït-Sahalia et al. 2022 | "The median out-of-sample R2 for predicting 5-second returns is approximately 10%" | afxz2022_hf_predictable.txt |
| 80% of predictability in last 10 ms | Aït-Sahalia et al. 2022 | "approximately 80% of the overall predictability is achieved by relying on the most recent 10 milliseconds" | afxz2022_hf_predictable.txt |
| 10 ms delay cuts R² from 14% to 2.5% | Aït-Sahalia et al. 2022 | "the average out-of-sample R2 drops from 14% to 2.5% after a delay of 10ms (1% of a second)" | afxz2022_hf_predictable.txt |
| Predictability gone in 5 minutes | Aït-Sahalia et al. 2022 | "predictability of returns vanishes to 0 ... in just five minutes" | afxz2022_hf_predictable.txt |
| Their return uses transaction prices | Aït-Sahalia et al. 2022 | "the return at a quote timestamp is defined as the the average transaction price in a time window divided by the mid-quote price at the timestamp" | afxz2022_hf_predictable.txt |
| Imbalance execution value falls with latency | Stoikov and Waeber | "the advantage of observing the limit order book can dissipate quickly as execution latency increases" | ssrn2661618_treasury.txt |
| Savings about 1/3 spread at 1 ms | Stoikov and Waeber | "saving on average approximately 1/3 of the spread per share if trades are executed with low latency (≈ 1 millisecond)" | ssrn2661618_treasury.txt |
| Treasury imbalance signal well known | Stoikov and Waeber | "This trading signal is hardly a secret in the 5 year US treasuries market" | ssrn2661618_treasury.txt |
| Imbalance not a stat-arb after costs | Lehalle and Mounjid | "the expected value of buying and selling back using accurate predictions based on sizes at first limits does not beat transaction costs (bid-ask spread and fees)" | lm2017_latency_placement.txt |
| Latency erodes imbalance value | Lehalle and Mounjid | "the added value of exploiting a knowledge on liquidity imbalance is eroded by latency" | lm2017_latency_placement.txt |
| ES OFI shocks die within a second | Takahashi 2025 | "Impulse responses indicate that shocks dissipate almost entirely within a second." | emini_ofi_2025.txt |
| ES event rate and size | Takahashi 2025 | "On average, 45 events occur per second, each averaging 15 contracts." | emini_ofi_2025.txt |
| ES-SPY correlation collapses at ms | BCS 2013 | "the median return correlation is just 0.0923 at 10 milliseconds and 0.0073 at 1 millisecond" | bcs2013_nber.txt |
| Arbitrage duration fell, profit constant | BCS 2013 | "declines dramatically, from a median of 97ms in 2005 to a median of 7ms in 2011" | bcs2013_nber.txt |
| Arms race raises the bar | BCS 2013 | "the arms race does not actually eliminate the arbitrage opportunities; rather, it just continually raises the bar for capturing them" | bcs2013_nber.txt |
| Liquidity providers lose races | BCS 2013 | "only the first message to reach the exchange" ... "liquidity providers usually lose the race" | bcs2013_nber.txt |
| Speed costs borne via spread | BCS 2013 | "all of the expenditure by market makers on speed technology ultimately is borne by fundamental investors, via the bid-ask spread" | bcs2013_nber.txt |
| Races fast and frequent | Aquilina et al. 2022 | "about one per minute per symbol for FTSE 100 stocks), extremely fast (the modal race lasts 5-10 millionths of a second)" | abo2022_quantifying_race.txt |
| Races one-third of spread | Aquilina et al. 2022 | "races constitute roughly one-third of price impact and the effective spread" | abo2022_quantifying_race.txt |
| Latency reduces fill ratio (FX) | Cartea and Sánchez-Betancourt | "when latency is zero, T0 would have obtained a fill ratio of 100%. At the other extreme T50 's fill ratio is 89%" | ora_ceba987f.txt |
| Missed trades cluster in high volatility | Cartea and Sánchez-Betancourt | "36.5% (resp. 40.0%) of T1's (resp. T2's) unfilled trades occur in the top quartile of volatility" | ora_ceba987f.txt |
| Strategy beats buying speed | Cartea and Sánchez-Betancourt | "T1 would be better off employing the latency-optimal strategy developed here, instead of investing in hardware and co-location services" | ora_ceba987f.txt |
| Fixed-horizon labels ignore the path (secondary for AFML) | mlfinpy docs | "the fixed horizon method will always fail to capture information about the path of the prices [Lopez de Prado, 2018]" | mlfinpy_labelling.rst.txt |
| Triple barrier definition (secondary) | mlfinpy docs | "the vertical barrier represents the amount of time an observation has to reach its given return in either direction before it is given a label of 0" | mlfinpy_labelling.rst.txt |
| Simpler models match deep nets on crypto LOB | Wang 2025 | "simpler models can match and even exceed the performance of more complex networks" | crypto_lob_gbdt_2025.txt |
| XGBoost vs HAR on liquidity withdrawal | Wang 2025b | "forecasts at 250 ms are noise-dominated; XGBoost delivers the best out-of-sample accuracy at 1 s and 5 s" | liq_withdraw_ml_2025.txt |
| mbp-10 fields | Databento docs | "bid_sz_N uint32_t The bid size at level N (top level if N = 00)." | databento_mbp10.html.txt |
| MBO can rebuild deeper MBP | Databento docs | "It is possible to construct MBP-10 yourself from MBO data if you want more price levels" | databento_mbp10.html.txt |
| RunPod prices | RunPod pricing | "RTX 4090 24 GB VRAM 41 GB RAM 6 vCPUs $ 0.89 /hr"; "A100 PCIe 80 GB VRAM 117 GB RAM 8 vCPUs $ 1.79 /hr" | runpod_pricing.html.txt |
| Lambda prices (1-GPU plan) | Lambda pricing | "NVIDIA H100 PCIe 80 GB 26 225 GiB 1 TiB SSD $3.29" | lambda_pricing.html.txt |

## Corrections after review (Stage E.28, MathReviewer G5)

- MG5-10 (SHOULD FIX): XGH's 2,772 regressions restated as per stock (16,632 over six stocks); the pilot's 1,092 windows are about 40% of one stock's sample and 7% of their total.
- MG5-11 (SHOULD FIX): the Kolm et al. phrase at the "horizon is the problem" bullet now uses the verbatim words "approximately two average price changes".
- MG5-12 (NOTE): removed the contradicting parenthesis about the level-2 ask moving to 5000.75 in worked example 2.5.
- MG5-13 (NOTE): 12 months of rolling test weeks changed from about 45 to about 47.
- MG5-14 (NOTE): added "(sub- and superscripts restored from the PDF extraction)" after the CKS case-by-case quote.
- MG5-15 (NOTE): verdict table now reads "R²_pred = ρ²R²_c under the linear AR(1) assumptions of 7.2" instead of "bound".
- MG5-16 (SHOULD FIX): Gould and Bonart data year corrected to 2014 at both places ("2014 Nasdaq stocks").
