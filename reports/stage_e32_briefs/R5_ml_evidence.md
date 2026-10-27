# R5_ml_evidence: how much out-of-sample directional predictability at 1-240 minutes, and did it survive costs

Stage E.32 follow-up reader (MLEvidence-OpusHigh, re-spawned 2026-10-27 02:34 PDT after a usage-limit stop at
00:51 PDT). Evidence pages and log: reports/stage_e32_briefs/pages/R5_ml_evidence/ (log.tsv). Scratch and scripts:
reports/stage_e32_briefs/work/R5_ml_evidence/. Labels: [A] academic, [P] practitioner pointer, [R] regulator,
[X] exchange, [F] firm. [unverified] marks any claim not read in fetched full text.

Cited, not repeated: M1_order_flow.md (order-flow forward decay; Chordia-Roll-Subrahmanyam 2005 Table 5;
Cont-Cucuringu-Zhang Table 8; Kolm-Turiel-Westray abstract; R2-needed table), M4_models.md (model families, data
size, Chinco-Clark-Joseph-Ye, Briola et al.), M5a_validation.md, M5b_power.md, R4_events.md (Gao-Han-Li-Zhou,
Jin et al., Baltussen et al.), E.28 2.8 (deep LOB models: reports/stage_e28_methods_brief.md lines 8260-9387),
E.28 2.9 section 6.6 (Ait-Sahalia, Fan, Xue and Zhou).

(Sections are written in order as the reading proceeds; a section marked PENDING was not finished.)

## B. From an out-of-sample correlation to ticks per trade (topic b; placed first because every row of table A is read through it)

Script and full output: work/R5_ml_evidence/R5_rho_arith.py and R5_rho_arith.out (no data read; inputs are the
stage's standard numbers). M1 section 1 already tabulates the OOS R2 a forecast needs at 1-30 minutes for
"trade every bar" and "top decile"; this section derives the same machinery in terms of the correlation rho,
adds the hit-rate and OOS-R2 conversions that published papers need, and answers the brief's 15-minute question.

### B.1 Assumptions (stated, not measured)

- (B-A1) r = the h-minute ZM mid change (ticks) and f = the forecast are jointly normal with mean 0, sd(r) =
  sigma_h, sd(f) = sigma_f, corr(r, f) = rho. Zero-mean is a simplification (a drift term would add to one side).
- (B-A2) Random-walk scaling: sigma_h = sigma_1m x sqrt(h), sigma_1m = 3.15 ticks (A0 Table 1). So
  sigma_5 = 3.15 x 2.2361 = 7.044, sigma_15 = 3.15 x 3.8730 = 12.200, sigma_60 = 3.15 x 7.7460 = 24.400 ticks.
- (B-A3) Constant sigma across the session (false in practice: overnight 1-minute volatility is lower than the
  day session's; A0 does not split it). Non-overlapping holds, independent across bars.
- (B-A4) Hurdle: E.28 ranking row 130 (reports/stage_e28_ranking.md), verbatim
  "| 6 | topstep | ZM | 2.69 | 2 | 4 | 2 | 1 | 2 | 3 | 2.475 | 2.150 | 2.312 | 0.59 | 1.59 | 0.86 | 49.23 | 2.08 | ok |  |",
  header "| Rank | Firm | Code | ... | mu*_lim | mu*_mkt | mu10K | ...": market-order break-even mu*_mkt = 1.59 ticks
  (the brief's "about 1.6"). Gross needed for 1.2 ticks net = 1.59 + 1.2 = 2.79, rounded to 2.8 as in the brief.
[MathReview D-1 (lead: accepted): 1.59 is E.28's cycle-EV threshold mu*_mkt at T = 20/day (= 1.528 + 0.062), not the cost of a round trip; the per-round-trip cost is c = 1.528 ticks, so "2.79 gross for 1.2 net" becomes 2.728 on the per-trade basis.]

### B.2 Sign-of-forecast strategy: E[r sign(f)] = rho sigma_h sqrt(2/pi)

Derivation. Under B-A1 the regression of r on f is linear: E[r | f] = rho (sigma_h / sigma_f) f. The position is
s = sign(f) in {-1, +1}, so the gross P&L per trade is r s and, by the tower property,
E[r sign(f)] = E[ E[r | f] sign(f) ] = rho (sigma_h / sigma_f) E[f sign(f)] = rho (sigma_h / sigma_f) E|f|.
For f ~ N(0, sigma_f^2), E|f| = sigma_f sqrt(2/pi) (half-normal mean: 2 int_0^inf x phi(x/sigma_f)/sigma_f dx =
sigma_f sqrt(2/pi)). Hence

  E[r sign(f)] = rho sigma_h sqrt(2/pi),  sqrt(2/pi) = 0.79788.                                        (B1)

The scale of f cancels: only its correlation with r matters for a sign rule. Companion results under B-A1:
- Hit rate (Sheppard's orthant formula for a bivariate normal): P(sign r = sign f) = 1/2 + arcsin(rho)/pi, so
  rho = sin(pi (hit - 1/2)).                                                                            (B2)
  hit 51% -> rho 0.0314; 52% -> 0.0628; 53% -> 0.0941; 55% -> 0.1564. (Discrete ZM prices give zero-change bars at
  short horizons; B2 then applies to the non-zero bars only, an approximation.)
- OOS R2 against a zero forecast: R2_oos = 1 - E(r - f)^2 / E r^2 = 2 rho k - k^2, k = sigma_f / sigma_h.   (B3)
  It peaks at rho^2 when k = rho (a calibrated forecast). So R2_oos <= rho^2, i.e. rho >= sqrt(R2_oos) whenever
  R2_oos > 0, and a NEGATIVE published OOS R2 does not mean rho <= 0: an over-dispersed forecast (k > 2 rho)
  has R2_oos < 0 with rho > 0 (example: rho 0.10, k 0.30 gives R2_oos = 0.06 - 0.09 = -0.03). Papers that
  report only OOS R2 (Baltussen et al.'s -0.04% for SM in R4; Cont-Cucuringu-Zhang's -0.10 to -0.37 in M1)
  therefore bound rho only when R2 > 0; a negative value is uninformative about the sign rule unless the paper
  also reports hit rates or the forecast's dispersion.

Worked example, 15 minutes, trade EVERY non-overlapping bar: rho = G / (sigma_15 sqrt(2/pi)) = G / 9.734.
- G = 1.59 (break-even): rho = 1.59 / 9.734 = 0.1633 (R2 at most 0.0267, hit 55.2%).
- G = 1.6: rho = 0.1644. G = 2.8 (1.2 net): rho = 2.8 / 9.734 = 0.2876 (R2 at most 0.0827, hit 59.3%).
Check: 0.2876 x 12.200 x 0.79788 = 2.799 ticks. But a 15-minute bar every bar is 19.3 trades a day in the day
session (290 / 15), not 4, so this is not the brief's design; it shows only that unconditional trading needs
rho near 0.16-0.29, well above anything in table A at minutes horizons.

### B.3 Thresholded strategy: trade only when |f| is large

Let the standardised forecast z = f / sigma_f ~ N(0,1). Trade (sign z) only when |z| > c. Then
- trade fraction per bar q = P(|z| > c) = 2 (1 - Phi(c)), so c = Phi^{-1}(1 - q/2);                         (B4)
- E[r sign(f) | |z| > c] = rho sigma_h E[|z| : |z| > c] = rho sigma_h phi(c) / (1 - Phi(c)) = rho sigma_h 2 phi(c) / q.   (B5)
  (Derivation: E[|z| 1{|z|>c}] = 2 int_c^inf x phi(x) dx = 2 phi(c), divided by q.)
- Per day: n_trades = q x N_bars, N_bars = session minutes / h (non-overlapping decision points).

Worked example, h = 15, 4 trades a day (results from R5_rho_arith.out, every step reproducible by hand):

| Session assumed | N_bars = minutes/15 | q = 4/N_bars | c (B4) | E|z| given trade = 2 phi(c)/q | rho for G = 1.6 | rho for G = 2.4 (0.8 net) | rho for G = 2.8 (1.2 net) |
|---|---|---|---|---|---|---|---|
| Day 08:30-13:20 CT (290 min) | 19.333 | 0.2069 | 1.2621 | 1.7389 | 0.0754 | 0.1131 | 0.1320 |
| Full Globex day 19:00-13:20 less the 07:45-08:30 halt (1,055 min) | 70.333 | 0.0569 | 1.9043 | 2.2887 | 0.0573 | 0.0860 | 0.1003 |

Hand check, day session: phi(1.2621) = exp(-0.79645)/2.50663 = 0.45093/2.50663 = 0.17990; 2 x 0.17990 / 0.2069
= 1.7390; rho = 1.6 / (12.200 x 1.7390) = 1.6 / 21.216 = 0.0754. Check G = 2.8: 2.8 / 21.216 = 0.1320.
At 8 trades a day in the day session (q = 0.4138, c = 0.8172, factor 1.3808) the rho needed rises to 0.095,
0.143 and 0.166 for G = 1.6, 2.4, 2.8.

Reading. In this normal model a forecast with rho about 0.13 over all day-session 15-minute bars, traded in its
top 21% (|z| > 1.26), earns 2.8 ticks gross; trading the full Globex day at the same 4 trades lowers the need to
about 0.10, but only if overnight bars are as volatile and as forecastable as day bars (B-A3, unlikely). In R2
terms (calibrated forecast) these are 1.0-1.7% OOS R2 at 15 minutes, every bar. Daily Sharpe check (brief's
target about 0.19): net per trade / sigma_15 x sqrt(n) = 1.0 / 12.200 x sqrt(5.5) = 0.192; 0.8 net at 4 trades
gives 0.131, 1.2 net at 8 trades gives 0.278 (R5_rho_arith.out).

Where the normal model flatters the threshold rule (each needs a test, not a belief):
1. Linearity of E[r | f] into the tails (B5 assumes the top 21% are as informative per unit of f as the body).
   ML forecasts often lose calibration in the tails; check with a binned reliability plot of realised r against
   predicted f deciles on validation folds.
2. Large |f| clusters in time (volatility, news). Then the 4 trades a day are not independent, the effective n
   is smaller, and sigma_h at trade time is larger than 12.2 (which raises the edge in ticks but also slippage;
   E.28's 1.59 is an average-condition hurdle).
3. Overlapping decision points: choosing the top 4 of 290 one-minute decision points (q = 0.0138, factor 2.7)
   looks cheaper still, but consecutive 15-minute forecasts sampled each minute are highly autocorrelated, so the
   iid selection factor overstates the gain.

### B.4 What published R2 values imply in ZM ticks (illustration only; the papers are not ZM)

Using rho >= sqrt(R2_oos) (B3) and B1 at the paper's own horizon, ZM volatility:

| Published OOS number (source, see table A) | horizon | rho implied (lower bound) | ZM gross per trade, sign every bar | note |
|---|---|---|---|---|
| Gao et al. SPY OOS R2 1.2% (R4) | 30 min, once a day | 0.110 | 0.110 x 17.253 x 0.798 = 1.51 | one trade a day, no threshold possible beyond skipping days |
| CRS 1996, 5-min R2 3.32% (M1) | 5 min | 0.182 | 1.02 | top-4-of-58 bars: 2.84 |
| CRS 2002, 5-min R2 0.54% (M1) | 5 min | 0.073 | 0.41 | top-4-of-58 bars: 1.15 (below 1.59) |

The 1996-to-2002 drop is the decay story of section D; the 2002 level, mapped to ZM, does not clear the hurdle
even with aggressive thresholding (M1 section 2.3 iii reaches the same conclusion by the R2 route).

## C. Public forecasting competitions on market data (topic c)

Access decision (log.tsv, 2026-10-27 00:49 PDT): kaggle.com answered robots.txt with a Google reCAPTCHA page and
its terms page is JavaScript-rendered and unreadable, so Kaggle was treated as NOT open to automated fetch and no
Kaggle page (overview, evaluation, leaderboard, discussion) was read. Consequence: the public-to-private
shake-up of each Kaggle market competition could NOT be measured; facts are taken only from the host firm's own
page [F] or an academic paper [A], and anything else is marked [unverified] with its origin. Competition
write-ups and forums are practitioner pointers only and were not used as evidence.

### C.1 The competitions, facts by source

| Competition | Task and metric | Validation / final scoring | Winning approach | Source and status |
|---|---|---|---|---|
| Two Sigma Financial Modeling Challenge (launched 2016-12-01) | "submitting code to forecast returns, with scores appearing on the competition leaderboard virtually in real time"; anonymised time-series features; metric (a signed square root of R2, "R") [unverified: memory, not read] | code competition; private score on later, unseen time periods [unverified] | not read | [F] Two Sigma, "Two Sigma Partners with Kaggle" (twosigma_partners_kaggle.html): "On December 1st, we launched our first public coding competition with Kaggle. Their community of over 700k data scientists has been invited to compete in a financial modeling competition, submitting code to forecast returns, with scores appearing on the competition leaderboard virtually in real time." Run dates December 2016 to March 2017 [unverified: WebSearch snippet of a winners' interview] |
| Jane Street Market Prediction (announced 2020-11-24) | trade/no-trade decision on anonymised opportunities; "utility" score [unverified: not read] | forecasting phase scored on live data after the close, with leaderboard updates to 25 Aug 2021 [unverified: WebSearch snippet of a university news post] | not read | [F] Jane Street blog, Craig Falls, Nov 24 2020 (janestreet_blog_kaggle_index.html): "Jane Street is running a Kaggle contest based on a real problem with real financial data ... with a total $100K being paid out." |
| Optiver Realized Volatility Prediction (2021) | forecast 10-minute realised volatility of stocks from order-book snapshots; RMSPE [unverified: memory] | not read | not read | No host page read (the Optiver page fetched for the later contest returned a JavaScript shell with no text). VOLATILITY, not direction: not evidence on directional predictability in any case. |
| Optiver Trading at the Close (2023) | forecast the 60-second-ahead move of a Nasdaq stock's weighted price relative to an index during the closing auction, in basis points; MAE; about 4,000 teams [unverified: WebSearch snippet] | not read | not read | Host page optiver_kaggle_closing_cross.html saved but its body is script-rendered; no fact extracted. |
| G-Research Crypto Forecasting (Nov 2021 - May 2022) | "forecast the short-term returns of 14 different crypto coins ... evaluated on a weighted Pearson correlation coefficient" | "each team selected their two best models for submission and we ran them for three months against real live market data to get our final leaderboard" | "all of our top three used a LightGBM model, though some experimented with other approaches, including neural networks. However, all of our top competitors believed it was their feature engineering that contributed most to their wins." | [F] G-Research, "Wrapping up the G-Research Crypto Forecasting competition", 30 May 2022 (gresearch_crypto_wrapup.html). Also: "With such a noisy dataset, it was unsurprising that the leaderboard saw many big jumps and precipitous drops, particularly early in the competition." Winning correlation value: not stated on the host page; not read elsewhere. |
| M6 Financial Forecasting Competition (Feb 2022 - Feb 2023; monthly horizon, 100 assets; included as the one market competition with a peer-reviewed results paper) | quintile-probability forecasts (RPS) and portfolio weights (information ratio, IR) | live evaluation, 12 monthly submission points | see C.2 | [A] Makridakis, Spiliotis, Hollyman, Petropoulos, Swanson and Gaba, arXiv 2310.13357 (IJF), arxiv_2310_13357_m6_competition.pdf; [A] Stanek, arXiv 2412.04490, arxiv_2412_04490_m6_luck.pdf |

### C.2 What the measured competition evidence says about selection and overfitting

1. [A] M6 (monthly, not intraday, but live and fully out of sample): "from the 163 teams included in the global
   leaderboard, 38 (23.3%) managed to provide more accurate forecasts than the benchmark, 47 (28.8%) to construct
   better portfolios, and 11 (6.7%) to achieve both higher IR and RPS scores ... only 3 teams outperformed the
   benchmark's forecasts in all 12 months of the competition, while none the benchmark's investment decisions".
   On the forecast-to-money link: "this link is weak, being maximized (r = 0.7) for the top 20% of the teams and
   vanishing when more than 40% of the teams are considered. Moreover, there seems to be no association (r = 0.12)
   between the two measures for the top 5% of the teams". Summary line: "an R-Squared of 0.099 between the
   forecasting and the investment decision ranks".
2. [A] Stanek on M6: "there is insufficient evidence to suggest that the extreme Sharpe ratios observed are beyond
   what one would expect by chance, given the number of teams, and thus not necessarily indicative of the
   possibility of consistently attaining abnormal returns." This is the competition analogue of the deflated
   Sharpe ratio logic in M5a: the winner of 163 noisy entrants is expected to look good.
3. [A] Roelofs, Fridovich-Keil, Miller, Shankar, Hardt, Recht and Schmidt (NeurIPS 2019; 120 Kaggle competitions;
   neurips2019_roelofs_kaggle_overfitting.pdf): with i.i.d. public/private splits there is "little to no signs of
   overfitting ... the overall effect sizes of (potential) overfitting are typically small (e.g., less than 1%
   classification accuracy)", but the outliers "usually have pathologies such as non-i.i.d. data splits or
   (effectively) small test sets", and "We have seen multiple competitions where a non-i.i.d. split lead to
   substantial gaps between public and private scores, suggesting that distribution shifts ... may be a more
   pressing problem than test set re-use". On shake-up (rank changes): "large rank changes can be a natural
   consequence of random noise in the evaluation ... even though all score deviations are small".
   Market competitions are the non-i.i.d. case by construction (the private set is a LATER period), so the
   public-to-private gap there mixes test-set reuse with regime change; Roelofs et al. did not single out the
   finance competitions, and I could not read their per-competition appendix rows for them (not in the 11-page
   main text).

What this means (my judgement, labelled): the measured sources say (i) on i.i.d. holdouts, adaptive reuse of a
holdout costs little; (ii) on forward-in-time holdouts with low signal-to-noise, ranks reshuffle largely by luck
and a forecast-quality lead does not translate reliably into money (M6 r = 0.12 among the top 5%); (iii) the
host firms' own words for the market contests are "noisy" and "big jumps and precipitous drops"; and (iv) the
winning recipe reported by the one host page read (G-Research) is LightGBM plus feature engineering. For E.33 the
transferable lessons are the one-shot sealed test (already V43) and a planning prior that the selected model's
validation score overstates its test score; the size of that overstatement on Kaggle market contests stays
UNMEASURED here.

## A. Evidence table: out-of-sample directional forecasts at 1-240 minutes (topic a)

Order: commodity futures first, then index/rates/FX futures, then equities, then reviews. "Read here" means the
full text was read by this worker (file under pages/R5_ml_evidence/ unless another folder is named); "cited" rows
come from another reader's output and are not re-read. Horizons outside 1-240 minutes are kept when they bound
the question (seconds-scale results show where predictability lives; one ~5.5 h row shows a null at the top end).

| # | Study [label] | Market | Horizon | Sample | Features | Model | Validation | OOS result (verbatim where read) | Costs and net | Later replication or decay | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 | Dixon, Klabjan and Bang (2016), "Classification-based financial markets prediction using deep neural networks", arXiv 1603.08604 [A] | 43 CME commodity and FX futures (one pooled model) | next 5-minute mid change, 3 classes (threshold 1e-3 "chosen to balance the class labels") | "5 minute mid-prices ... from March 31st 1991 to September 30th, 2014"; tests from 2005 | price differences lagged 1-100, moving averages 5-100, pairwise return correlations with all other symbols: "9895 features" | feed-forward DNN | walk-forward: "training set consists of 25,000 consecutive observations and the test set consists of the next 12,500", rolled "ten times ... in 1000 observation period increments" (so the ten test windows overlap heavily) | "predict the direction of instrument movement to, on average, 42% accuracy with a standard deviation across instruments of 11%"; Figure 3: "a heavier density around an accuracy of 0.35 which is slightly better than a random selection" (chance is about 1/3); best "HG Copper 0.68"; "the worst five performing instruments performed no better or even worse than white noise" | none: "transaction costs are ignored"; fills "at the mid-price"; Sharpe "as high as 3.29" (Platinum) gross | none found | read here: arxiv_1603_08604_dixon_klabjan_bang.pdf |
| A2 | Peng, Zhang and Wang (2025), arXiv 2508.06914 [A, working paper] | 15 Chinese futures incl. Dalian soybean meal (M), corn (C), corn starch (CS) | 5 seconds ("the data of the first 25 seconds is used to compute the independent variables, and that of the subsequent 5 second are used to calculate the dependent variable") | "October 1st 2024 to October 31st 2024, covering a total of 18 trading days", 0.5 s snapshots | trade and level-1 book: volume, returns and imbalances, "speed and cost" groups | logistic regression and SVM variants for imbalanced classes | rolling: "the data of the first 2 trading days is used for the training, and that of the 3rd trading day" for testing | Table 4, soybean meal, "Average returns per trade on the test set" for long signals: 3.34e-5 (LR), 9.17e-5 (SMOTE-LR), 8.57e-5 (mean-uncertainty LR) | no fees or spread applied in the text read; the label is the "Average P_txn" of forward trades over the current price, which embeds bid-ask bounce (same construction as A4). Under an assumed M price of about 3,000 CNY/t (not read) and a 1 CNY tick, 8.6e-5 is about 0.26 tick gross | 18 days only; no replication | read here: arxiv_2508_06914_china_hf_futures_direction.pdf |
| A3 | Baltussen, Da, Lammers and Martens (JFE 2021) [A] | 60+ futures incl. CBOT soybean meal | first half-hour (with overnight) to last half-hour | SM 1982-2020 | intraday returns | OLS | recursive OOS | SM OOS R2 -0.04% (first half-hour); -0.27% with r_M | not needed (null) | the only CBOT grain test found; null over 38 years | cited: R4_events.md lines 351-354, 437 |
| A4 | Gao, Han, Li and Zhou (2018; 2015 draft read by R4) [A] | SPY and ETFs; crude oil and gold futures; FX | first half-hour to last half-hour | SPY 1993-2013 | half-hour returns | OLS | recursive OOS | SPY OOS R2 1.2% (1.8% with the twelfth half-hour); "does not show up in major currency pairs or commodity futures" | R4 records none for the commodity null | replicated internationally (A11) for equity indices; commodity null | cited: R4_events.md lines 435, 439-444 |
| A5 | Jin, Kearney, Li and Yang (MPRA 2019) [A] | Dalian soybean, soybean meal; Shanghai copper, rebar | first half-hour to last half-hour | soybean meal 2008-06 to 2013-06 | half-hour returns | OLS | in-sample R2 reported by R4 (OOS not recorded there) | soybean meal R2 0.90% (in sample), t = 2.60 | not recorded | not replicated on CBOT (A3 null) | cited: R4_events.md lines 436, 446-449 |
| A6 | Mesfin (2026), "Sequential Structure in Intraday Futures Data: LSTM vs Gradient Boosting on MNQ", arXiv 2605.17724 [A, single-author working paper, not peer reviewed] | Micro E-mini Nasdaq-100 (MNQ) | 10:30 bar open to session close (about 5.5 h; above the 240-minute range, kept as a boundary null) | "944 trading days spanning 2021 through 2025" | engineered daily/intraday features (GBDT); raw 5-minute bar sequences (LSTM) | gradient boosting, LSTM | "strict walk-forward validation with expanding training windows across three out-of-sample test periods (2023, 2024, 2025)" | "No configuration produces out-of-sample accuracy materially above base rate. Combined out-of-sample accuracies range from 50.00% to 50.89% across all gradient boosting variants. The LSTM produces combined OOS accuracy of 50.59%" against "a 51.8% base rate"; "Permutation test p-values are 0.135 ... and 0.515" | not reached (null) | n/a | read here: arxiv_2605_17724_mnq_lstm_gbdt.pdf |
| A7 | Spears, Zohren and Roberts (2020), CME Eurodollar [A] | CME Eurodollar futures, level 1 | seconds-scale micro-price changes | 2018 | best quotes | MLP, CNN-LSTM | (E.28) | (E.28) | Sharpe negative at 12 x 0.005 = 0.06 bp cost against a 0.5 bp median spread | none | cited: E.28 2.8 section 5.1 |
| A8 | Dixon (2017), CME ES RNN [A] | ESU6, level II | next mid flip up to 1 s | August 2016 | book depths, market orders | RNN | (E.28) | "the performance of the RNN decays as we increase the prediction horizon from the next book update event to 1s in the future" | 90-minute backtest "With perfect information, and 0ms latency" | "secular decay when the model is not re-trained on a daily basis" | cited: E.28 2.8 sections 5.2, 7 |
| A9 | Li, Sakkas and Urquhart (2022), J. Financial Markets 57 [A] | 16 developed-market stock indices (cash indices, not futures) | first half-hour to last half-hour | US "January 3, 2000 to December 29, 2017" (others shorter) | half-hour returns | OLS | "expanding window ... first five years ... as the initial estimation period ... adding one day at a time" | Table 5 R2_OOS (%): U.S. 2.86, Japan 2.20, Australia 1.82, France 1.48 ... New Zealand -0.43, Austria -0.24; "11 out of 16 countries have a positive OOS R2" | the text read applies no transaction cost (grep for "cost" finds only liquidity measures); cash indices are not directly tradable | international replication of A4 for equities only | read here: nott_li_sakkas_urquhart_2022_itsm_firecrawl.md (route 4, Firecrawl) |
| A10 | Ait-Sahalia, Fan, Xue and Zhou (2022), NBER w30366 [A] | S&P 100 stocks | 1 s to 1,800 s (calendar), also trade and volume clocks | "January 2019 - December 2020" | 13 predictors x 9 windows (117) from trades and quotes | OLS, ridge, LASSO, RF, GBT, NN | "A new model is fitted for every testing day using data from the past 5 days ... Hyper-parameters ... tuned every month" | "The median out-of-sample R2 for predicting 5-second returns is approximately 10%"; "returns are only predictable over the next 3 minutes"; "predictability of returns vanishes to 0 (meaning that a binary directional prediction becomes no better than a coin toss) in just five minutes"; "approximately 80% of the overall predictability is achieved by relying on the most recent 10 milliseconds" | none; the return is average transaction price over the mid (E.28's caveat: partly bid/ask print prediction) | trees about equal to LASSO (E.28 2.9 section 6.6) | read here from E.28's saved copy: reports/stage_e28_briefs/pages/C2_OFI/afxz2022_hf_predictable.txt |
| A11 | Chinco, Clark-Joseph and Ye (JF 2019) [A] | NYSE stocks | 1 minute | 2005-2012 | 3 lags of 1-minute returns of the whole cross-section | LASSO per stock | rolling 30-minute windows | "increases out-of-sample fit by at least ∆R̄n2 = 1.2%pt" | "an annualized Sharpe ratio of 1.8 net of trading costs" (the only net-positive minutes-scale ML result in this table) | predictors "unexpected, short-lived, and sparse" | cited: M4_models.md lines 181-185 |
| A12 | Chordia, Roll and Subrahmanyam (JFE 2005) [A] | NYSE 150 largest stocks | 5 to 60 minutes | 1996-2002 | lagged return, order imbalance | OLS | regression R2 by year | 5-minute R2 3.32% (1996) to 0.54% (2002); imbalance loses predictive power within 30 minutes | feasible "only for the specialist and perhaps sophisticated floor traders" | decayed sixfold in six years | cited: M1_order_flow.md section 2.3 (iii) |
| A13 | Cont, Cucuringu and Zhang (2023) [A] | US stocks | 1 minute ahead | (M1) | own and cross-asset multi-level OFI lags | OLS rolled each minute | 30-minute rolling | Table 8 OOS R2 -0.37 (own best-level OFI), -0.10 (with cross-asset OFI) | n/a | "decays rapidly in time" | cited: M1_order_flow.md section 2.3 (v) |
| A14 | Kolm, Turiel and Westray (Math. Finance 2023) [A] | 115 Nasdaq stocks | multiple, event-scaled | (abstract only) | deep order-flow imbalance | deep nets | (not read) | "the effective horizon of stock specific forecasts is approximately two average price changes" [abstract; full text not fetched: Wiley Cloudflare in E.28, SSRN blocked, no other host found by one WebSearch] | not read | not read | cited: M1_order_flow.md section 2.3 (iv) |
| A15 | DeepLOB family, LOBCAST, Briola et al., Lucchese et al., Sirignano and Cont [A] | LSE, Nasdaq stocks; FI-2010 | 10-100 book events, up to "50 order book events" | various | full book | CNN-LSTM, transformers, MLP | mostly single splits; MCS in Lucchese | DeepLOB LSE accuracy 70.17/63.93/61.52% at k = 20/50/100 (3 classes); LOBCAST F1 79-87 on FI-2010 falls to 48-61 on Nasdaq 2021-22 | DeepLOB simulation "gross profits before fees"; Briola: "high forecasting power does not necessarily correspond to actionable trading signals" | out-of-dataset drops (LOBCAST) | cited: E.28 2.8 sections 1.6, 4.1-4.5, 7, 8 |
| A16 | Ghosh, Neufeld and Sahoo (2020), arXiv 2004.10178 [A] | S&P 500 constituents | open to close (about 390 min; above range, boundary) | "January 1993 till December 2018" | returns relative to close, open and intraday | RF, LSTM | Krauss-style study periods: "4-year window and 1-year stride ... 26 study periods with non-overlapping trading part" | long top-10 / short bottom-10: "a daily return, prior to transaction costs, of 0.64% using LSTM networks, and 0.54% using random forests" | costs "0.05% slippage cost on each half-turn ... a total of 0.2%" per day; after-cost tables reported | last sub-period called "the time-period of deterioration; probably since by that time on, machine learning algorithms are broadly available" | read here: arxiv_2004_10178_ghosh_lstm_rf_intraday.pdf |
| A17 | Easley, Lopez de Prado, O'Hara and Zhang (NBER conf. 2019; RFS 2021) [A] | 87 liquid futures, all asset classes | one week, in dollar-volume bars ("roughly 50 bars per day") | (2019 version) | microstructure measures (Kyle lambda, Amihud, VPIN, Roll, Corwin-Schultz) | random forest | "10-fold purged Cross-Validation" | targets are signs of changes in spread, volatility, Jarque-Bera, kurtosis/skewness, serial correlation: NOT the sign of the return. Kept as a scope marker: the largest ML-on-futures-microstructure study found does not forecast direction | n/a | n/a | read here: nber_conf_easley_lopezdeprado_ohara_zhang_2019.pdf |
| A18 | Kelly and Xiu (2023), "Financial Machine Learning", NBER w31502 (review) [A] | review | intraday case | n/a | n/a | n/a | n/a | the high-frequency return-prediction studies it reviews are Chinco et al. ("they forecast one-minute-ahead stock returns trained in rolling 30-minute regressions") and Ait-Sahalia et al. ("all methods have very similar performance, except for OLS. The improvements from a nonlinear method like random forest or boosted trees are limited for most cases when compared with lasso"); Easley et al. is reviewed for "risk and liquidity outcomes", not returns | n/a | n/a | read here: nber_w31502_kelly_xiu_financial_ml.pdf |

Reading of table A (evidence, with the arithmetic of section B):
1. No study read reports a positive OUT-OF-SAMPLE, cost-inclusive directional result for any CBOT grain at
   1-240 minutes. The one CBOT soybean-meal test (A3) is null over 1982-2020; the Dalian soybean-meal results are
   in-sample (A5) or 5-second gross (A2, about 0.26 tick under a stated price assumption).
2. Where minutes-scale OOS R2 is positive, it is in equities or equity indices and at one specific daily slot
   (A4: 1.2%, A9: up to 2.86%, both last half-hour, both gross), or at 1 minute with thousands of cross-sectional
   predictors (A11: +1.2 points of R2, net Sharpe 1.8, the only net-positive row).
3. Unconditional high-frequency predictability is real but lives in seconds and milliseconds (A10: 5-second R2
   about 10%, gone by 3-5 minutes, 80% from the last 10 ms; A8 decays by 1 s; A14 about two price changes).
4. Every futures ML study at minutes horizons that reports accuracy either ignores costs (A1) or finds nothing
   out of sample (A6); the cost-inclusive futures result (A7) dies at 12% of the spread.
5. Model class: where compared, trees and neural nets do not beat regularised linear models by much (A10, A18).

## D. Decay and crowding of intraday predictability (topic d)

| Market and dates | What changed | Magnitude (verbatim where read) | Source [label] |
|---|---|---|---|
| NYSE stocks, 1996 to 2002 (decimalisation, automation) | 5-minute forward R2 from order imbalance and lagged return | 3.32% (1996) to 0.54% (2002), about a factor of 6 | CRS 2005 Table 5, cited from M1 section 2.3 (iii) [A] |
| NYSE stocks, tick-size regimes (1/8, 1/16, decimal) | short-horizon predictability of returns from order flow | abstract: predictability "has declined over time with the minimum tick size" and prices were closer to random-walk benchmarks in the decimal regime [unverified: abstract seen only in WebSearch summaries; full text not fetched (Deakin repository behind an AWS WAF challenge, ScienceDirect not tried under the program's rules)] | Chordia, Roll and Subrahmanyam, JFE 87 (2008) [A] |
| EBS interdealer FX (EUR/USD, USD/JPY, EUR/JPY), 2003 to 2007 | rise of algorithmic trading vs serial autocorrelation of 5-second returns | "the introduction and growth of algorithmic trading coincides with a reduction in the absolute value of serial autocorrelation in each of the three currency-pairs we analyze, especially in the euro-yen currency pair, the currency with the lowest trading volume"; structural VAR: "algorithmic trading participation reduces the degree of serial autocorrelation in currency returns" | Chaboud, Chiquoine, Hjalmarsson and Vega (Oct 2012 version; JF 2014), boc_chaboud_et_al_rise_of_machines.pdf [A] |
| CME E-mini S&P 500 vs SPY, 2005 to 2011 | lead-lag arbitrage window | "the duration of ES-SPY arbitrage opportunities declines dramatically, from a median of 97ms in 2005 to a median of 7ms in 2011" while "the profitability of ES-SPY arbitrage opportunities is remarkably constant throughout this period, at a median of about 0.08 index points per unit traded"; "in 2011 the ES-SPY correlation reaches 0.50 at a 142 ms interval, whereas in 2005 the ES-SPY correlation only reaches 0.50 at a 2,627 ms interval" | Budish, Cramton and Shim (NBER 2013 version), read from E.28's saved copy reports/stage_e28_briefs/pages/C2_OFI/bcs2013_nber.txt [A] |
| S&P 100 stocks, 2019-2020 | where the remaining predictability sits | "approximately 80% of the overall predictability is achieved by relying on the most recent 10 milliseconds, 10 transactions or 10 lots transacted"; return predictability gone within 3-5 minutes | Ait-Sahalia et al. 2022 (A10) [A] |
| S&P 500 stocks, 1993-2018 (daily-rebalanced ML statistical arbitrage, open-to-close) | performance by sub-period | the last sub-period is "the time-period of deterioration; probably since by that time on, machine learning algorithms are broadly available" (the authors' conjecture, not a test) | Ghosh, Neufeld and Sahoo 2020 (A16) [A] |
| CME ES, August 2016 | model decay without retraining, within one month | "The F1 scores are observed to exhibit a secular decay when the model is not re-trained on a daily basis" | Dixon 2017, cited from E.28 2.8 section 7 [A] |
| Nasdaq stocks, FI-2010 (2010) to 2021-2022 | deep LOB model accuracy out of dataset | F1 79-87 (FI-2010) to 48-61 (Nasdaq 2021, 2022) | LOBCAST, cited from E.28 2.8 sections 4.1, 7 [A] |
| CBOT soybean meal, 1982-2020 | intraday momentum | null over the whole span (no period with a positive OOS R2 is reported by R4) | Baltussen et al., cited from R4 [A] |
| Live market competitions, 2021-2023 | out-of-sample skill of hundreds of teams | M6: 23.3% of 163 teams beat the forecast benchmark, none beat the investment benchmark in all 12 months; extreme Sharpe ratios consistent with chance (section C) | Makridakis et al.; Stanek [A] |

Reading (evidence): every dated comparison found points the same way. As markets automated, (1) minutes-scale
predictability from public order flow and lagged returns fell (CRS: factor 6 at 5 minutes in six years; FX
autocorrelation fell with algorithmic participation), and (2) the cross-market lead-lag that remains was compressed
from seconds to single-digit milliseconds, with constant profit per opportunity, i.e. it became a speed race, not a
forecasting problem. No study was found that measures year-by-year decay of intraday directional predictability in
a CME grain contract; that is a search gap (two discovery queries, section F), not evidence either way.

Judgement (mine): a ZM trader in Vancouver with tens of milliseconds of latency competes only for what is left
after (2), so the relevant prior is the post-automation level (CRS 2002 row or below), not the pre-2000 level, and
lead-lag from ZS/ZL to ZM at sub-second scale should be presumed taken (consistent with M1 and M2).

## E. What this implies for E.33 (topic e). Evidence and judgement are marked separately.

Supporting arithmetic (work/R5_ml_evidence/R5_rho_horizons.py and .out; assumptions B-A1 to B-A4; 4 trades a day
inside the 290-minute day session, thresholded per B4-B5):

| h (min) | sigma_h (ticks) | bars/day | q | c | E|z| given trade | rho for 1.59 gross | rho for 2.4 (0.8 net) | rho for 2.8 (1.2 net) | gross at rho 0.03 / 0.05 / 0.08 / 0.10 |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 7.044 | 58.0 | 0.0690 | 1.8186 | 2.2136 | 0.102 | 0.154 | 0.180 | 0.47 / 0.78 / 1.25 / 1.56 |
| 15 | 12.200 | 19.3 | 0.2069 | 1.2621 | 1.7389 | 0.075 | 0.113 | 0.132 | 0.64 / 1.06 / 1.70 / 2.12 |
| 30 | 17.253 | 9.7 | 0.4138 | 0.8172 | 1.3808 | 0.067 | 0.101 | 0.118 | 0.71 / 1.19 / 1.91 / 2.38 |
| 60 | 24.400 | 4.8 | 0.8276 | 0.2178 | 0.9415 | 0.069 | 0.105 | 0.122 | 0.69 / 1.15 / 1.84 / 2.30 |

Check (h = 30): 3.15 x sqrt(30) = 17.253; 2.8 / (17.253 x 1.3808) = 2.8 / 23.823 = 0.1175.

Numbered statements (each tied to rows of table A, section D or section B):

1. EVIDENCE (A3, A4, A5, A2): for agricultural futures, no published OOS directional R2 above zero at 1-240
   minutes was found. The CBOT soybean-meal test is null (OOS R2 -0.04%, 1982-2020); the Dalian evidence is
   in-sample (R2 0.90%) or a 5-second gross 0.26-tick figure. By B3 a negative OOS R2 does not rule out a small
   positive rho, so the grain evidence is "no demonstrated rho", not "rho = 0".
2. EVIDENCE (A4, A9, A11, A12): the largest minutes-scale OOS values in any liquid market are R2 of 1-3% at a
   single daily slot in equity indices (rho >= 0.11-0.17 by B3, for one trade a day), +1.2 R2 points at 1 minute
   from thousands of cross-sectional equity predictors, and 0.54% at 5 minutes from order imbalance on the NYSE
   in 2002 (rho >= 0.073), down from 3.32% in 1996.
3. EVIDENCE (A10, A13, A14, A8, D rows 3-5): unconditional predictability from price and order flow is strong
   only at seconds and below, and is gone within about 3-5 minutes in liquid electronic markets; cross-asset
   lead-lag was compressed to single-digit milliseconds by 2011 on CME ES.
4. JUDGEMENT (from 1-3): a plausible OOS rho for an every-bar ZM forecast built from price, ZS/ZL cross-asset and
   ZM order-flow features is 0.00-0.05 at 5-15 minutes and similar or lower at 30-60 minutes; 0.05-0.08 is an
   optimistic case; rho >= 0.10 at any of these horizons would exceed every OOS value published for commodity
   futures and match only the best single-slot equity-index results.
5. ARITHMETIC (section B and the table above) on statement 4: at 4 trades a day in the day session, rho 0.05 gives
   0.78-1.19 ticks gross (below the 1.59 break-even at every horizon) and rho 0.08 gives 1.25-1.91 gross, i.e.
   at most about 0.3 tick net. The brief's target of 0.8-1.2 ticks net needs rho 0.10-0.13 at 15-60 minutes
   (0.15-0.18 at 5 minutes). JUDGEMENT: the evidence places that requirement at or beyond the top of what any
   liquid market has shown out of sample at these horizons, and above everything shown for grains; the honest
   prior for E.33's search producing a model that clears 0.8 ticks net is low (I would not put it above roughly
   one in ten, and this number is my judgement, not a measured rate). A thresholded rule's apparent edge is
   additionally exposed to the three normal-model failure modes in B.3.
6. DESIGN, horizon (EVIDENCE: table above, A10, D): at a fixed 4 trades a day the rho needed is lowest at 30-60
   minutes (0.067-0.069 for break-even, 0.118-0.122 for 1.2 net) and highest at 5 minutes (0.102 / 0.180),
   because sigma_h grows with sqrt(h) while the selection factor falls more slowly than the trade fraction rises.
   Against that, the published predictability is concentrated at short horizons and decays by 3-5 minutes (A10).
   JUDGEMENT: if E.33 searches several horizons, 15-60 minutes is where the cost arithmetic is kindest, and any
   signal there must come from slow state (session structure, overnight information, cross-asset level
   dislocations, events: R4, M2), not from the fast order-flow persistence that A10/A13/A14 show dies within
   minutes.
7. DESIGN, trade rate (B.3): thresholding to a few trades a day lowers the rho needed by a factor of 2.2 relative to
   trading every 15-minute bar (0.075 vs 0.163 for break-even) but only if E[r | f] stays linear into the tails
   and large forecasts are not clustered; E.33 should test calibration of the top bucket on validation folds
   (binned realised r against predicted f) before believing B5.
8. DESIGN, model class (EVIDENCE: A10, A18, G-Research in C.1, A6, M4): regularised linear models match trees and
   neural nets at high frequency; the one host-reported market competition win used LightGBM with heavy feature
   engineering; a sequence model on four years of one instrument found nothing (A6). JUDGEMENT: consistent with
   M4's verdict (linear primary, one GBDT secondary, no deep sequence models).
9. DESIGN, validation and reporting (EVIDENCE: A10 and A11 refit on 5-day and 30-minute windows because predictors
   are short-lived; C.2 Roelofs: forward-in-time splits are where public/private gaps arise; M6: forecast skill
   and money weakly linked; Stanek: winners consistent with luck). JUDGEMENT: (a) report rho, hit rate and the
   top-bucket conditional mean in ticks for every configuration, not only OOS R2 (B3: R2 can be negative with
   positive rho, and accuracy alone misleads, E.28 2.8 section 8); (b) treat the best validation configuration's
   score as biased upward and rely on the sealed one-shot test (V43) and M5a's deflation; (c) if a rolling refit is
   part of the frozen pipeline, it is one configuration, declared in advance.

## F. Discovery log, stopping rule, and what was not done

Discovery used (this spawn): WebSearch 15 calls (budget 60); arXiv API 4 queries (R5_arxiv_q1-q4.xml in the work
folder; q1 from the first spawn); Firecrawl 1 page (Li-Sakkas-Urquhart, route 4 after curl and Scrapling get and
fetch hit Cloudflare). No WebSearch budget notice was received.

Stopping rule (READER_BRIEF rule 6):
- (a) evidence table: more than 3 full texts read (A1, A2, A6, A9, A10, A16, A17, A18 here, plus cited rows). The
  last three discovery queries aimed at intraday ML on commodity/agricultural futures (WebSearch "machine learning
  intraday returns agricultural commodity futures ..."; WebSearch "Chinese commodity futures minute-level ...";
  arXiv q3) surfaced only A2 as new; the rest were daily-horizon studies. Stopped.
- (c) competitions: host pages read for G-Research, Jane Street, Two Sigma; Optiver pages unreadable; Kaggle not
  fetched by terms decision. Academic sources: Roelofs et al., Makridakis et al., Stanek. Stopped; shake-up sizes
  unmeasured.
- (d) decay: CRS 2005 (M1), Chaboud et al., Budish et al., Ait-Sahalia et al., Ghosh et al. read; one targeted
  query for futures-market decay found nothing new. Stopped.

Not finished or not verified, and why:
- Kaggle leaderboard shake-ups (Jane Street, Optiver x2, G-Research, Two Sigma): not measured; Kaggle treated as
  closed to automated fetch (reCAPTCHA on robots.txt, unreadable terms). Metrics and dates for those contests other
  than the host-page quotes are [unverified].
- Chordia, Roll and Subrahmanyam (2008) full text: not fetched (Deakin AWS WAF; no other open host found);
  cited as [unverified] abstract.
- Kolm, Turiel and Westray (2023) OOS numbers: no full text on a host whose terms allow fetching (one WebSearch);
  M1's abstract citation stands.
- Gu-Kelly-Xiu style reviews: Kelly and Xiu (2023) read for the intraday case only; no separate intraday ML
  review was found.
- Agricultural intraday ML (gradient boosting or neural nets on CBOT grains at minutes): none found; recorded as a
  search gap, not as evidence.
- Planner pointers: this brief owns none (M4 owns the grain-LOB and Briola claims, R4 owns Baltussen), so there is
  no planner-pointer table.
